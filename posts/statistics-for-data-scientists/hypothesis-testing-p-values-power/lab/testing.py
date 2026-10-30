#!/usr/bin/env python3
"""Lab for "p-Values and Power: How Wrong Can a Significant Result Be?" (Statistics for Data Scientists, part 5).

Every number the article calls measured comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python testing.py all --out mine.json            # every stage, the article's budget (about 30 seconds)
    python testing.py all --quick --out quick.json   # the reader's budget (about 6 seconds), noisier
    python testing.py retrodesign --out mine.json    # one stage

Stages:
    pvalues      the p-value as a random variable: its distribution under the null and under alternatives,
                 for a z statistic and for two-sample t-tests on simulated data; 25 repeats of one
                 experiment; Cumming's interval for the p-value of a replication
    power        the power of the two-sample t-test four ways (an integral by hand, SciPy's noncentral t,
                 statsmodels, simulation), its normal approximation, sample sizes, and "observed power"
    retrodesign  Gelman and Carlin's design analysis: power, the type S error rate and the exaggeration
                 ratio, in closed form and by their own simulation, for the two published studies they used
    replication  the Reproducibility Project: Psychology's 100 replications (CC0 data): effect sizes in the
                 original and the replication, by the original p-value, and which non-significant
                 replications are statistically equivalent to no effect
    fpr          the false positive risk: Ioannidis's table, Colquhoun's "p-less-than" and "p-equals"
                 calculations, and a simulation of a million experiments
    tost         two one-sided tests by hand against statsmodels; their size, power and sample sizes
    stopping     optional stopping: the error rate of a 5% test repeated as data accumulate, computed
                 exactly for a z-test and simulated for t-tests

Every simulated quantity is printed as estimate +- MCSE (its Monte Carlo standard error) with the number
of replications R. Every stage draws from its own stream, SeedSequence([stage, sub-stream, seed]), so
stages can run alone and repeat to the bit with the same NumPy version.
"""

import argparse
import csv
import datetime
import hashlib
import json
import math
import pathlib
import platform
import time

import numpy as np
import scipy
from scipy import integrate, optimize, signal, stats

HERE = pathlib.Path(__file__).resolve().parent
OSC_CSV = HERE / "data" / "osc2015_rpp_pairs.csv"
STAGES = ("pvalues", "power", "retrodesign", "replication", "fpr", "tost", "stopping")

# Replications. The article quotes FULL; --quick is the reader's first run.
FULL = dict(pz=200_000, pt=100_000, cumming=4_000_000, power_sim=20_000, retro_reps=2_000, retro_big=10_000_000,
            fpr=500_000, tost=100_000, stop_z=100_000, stop_t=20_000, simmons=200_000)
QUICK = {k: v // 10 for k, v in FULL.items()}
BLOCK = 20_000                                  # simulated experiments per block; fixed, so results do not depend on the machine
Z975 = float(stats.norm.isf(0.025))             # 1.959964, the two-sided 5% point of the standard normal

# Published inputs, as Gelman and Carlin (2014) report them. Durante et al.: an estimate of 17 percentage points
# with p = .035, so z = 2.1 and SE = 17 / 2.1 = 8.1; Kanazawa: 8 points with p = .015, so SE = 3.28.
DURANTE = dict(estimate=17.0, p=0.035, se=8.1, plausible=2.0)
GC_CASES = [  # label, true effect A, standard error s, the values Gelman and Carlin print
    ("kanazawa_0.1", 0.1, 3.28, dict(power=0.05, typeS=0.46, exaggeration=77.0)),
    ("kanazawa_0.3", 0.3, 3.28, dict(typeS=0.40, exaggeration=25.0)),
    ("kanazawa_1.0", 1.0, 3.28, dict(p_hi=0.049, p_lo=0.011, typeS=0.19, exaggeration=8.0)),
    ("durante_2", 2.0, 8.1, dict(power=0.06, typeS=0.24, exaggeration=9.7)),
    ("power80_2.8", 2.8, 1.0, dict(power=0.80, typeS=1.2e-6, exaggeration=1.12)),
]
DESIGN_N, DESIGN_D = 16, 1.0                    # Colquhoun's two-sample design: 16 per group, a true difference of 1 SD
GL_X, GL_W = np.polynomial.legendre.leggauss(200)


# ------------------------------------------------------------------------------- small helpers
def stream(seed, stage, sub=0):
    """An independent generator for (stage, sub-stream): varying ids first, the root seed last."""
    return np.random.default_rng(np.random.SeedSequence([STAGES.index(stage), sub, seed]))


def mcse_share(p, reps):
    return math.sqrt(max(p * (1 - p), 0.0) / reps)


def r6(x):
    """Round for the capture file: floats to six significant digits, recursively."""
    if isinstance(x, dict):
        return {k: r6(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, np.ndarray)):
        return [r6(v) for v in x]
    if isinstance(x, (float, np.floating)):
        x = float(x)
        return x if not math.isfinite(x) or x == 0 else float(f"{x:.6g}")
    if isinstance(x, (np.integer, np.bool_)):
        return int(x)
    return x


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()[:12]


def pm(est, mcse, pct=True, nd=2):
    """'12.34% +- 0.05' for a share, or '9.537 +- 0.006' for a plain value."""
    return f"{100 * est:.{nd}f}% +- {100 * mcse:.{nd}f}" if pct else f"{est:.{nd}f} +- {mcse:.{nd}f}"


def two_sample_t(x, y):
    """Pooled two-sample t statistics and two-sided p-values, row by row, from first principles."""
    n1, n2 = x.shape[1], y.shape[1]
    df = n1 + n2 - 2
    diff = x.mean(axis=1) - y.mean(axis=1)
    sp2 = ((n1 - 1) * x.var(axis=1, ddof=1) + (n2 - 1) * y.var(axis=1, ddof=1)) / df
    se = np.sqrt(sp2 * (1 / n1 + 1 / n2))
    t = diff / se
    return diff, se, t, 2 * stats.t.sf(np.abs(t), df)


def simulate_ttests(rng, reps, n, d):
    """p-values of `reps` pooled two-sample t-tests, n per group, true difference d (in SD units)."""
    p = np.empty(reps)
    for a in range(0, reps, BLOCK):
        m = min(BLOCK, reps - a)
        x = rng.standard_normal((m, n)) + d
        y = rng.standard_normal((m, n))
        p[a:a + m] = two_sample_t(x, y)[3]
    return p


def nct_power(d, n, alpha=0.05):
    """Exact power of the two-sided pooled two-sample t-test with n per group, from SciPy's noncentral t.

    The lower tail is taken as P(T >= c) under -lam, by symmetry: SciPy 1.18.1's nct.cdf(-c, df, lam)
    returns NaN once lam passes about 8, where the tail is far below 1e-30.
    """
    df, lam = 2 * n - 2, d * math.sqrt(n / 2)
    c = stats.t.isf(alpha / 2, df)
    return float(stats.nct.sf(c, df, lam) + stats.nct.sf(c, df, -lam))


# ------------------------------------------------------------------------------- p-values
def p_cdf_z(p, lam):
    """P(P <= p) for a two-sided z-test whose statistic is N(lam, 1): the power at level p."""
    z = stats.norm.isf(np.asarray(p, dtype=float) / 2)
    return stats.norm.sf(z - lam) + stats.norm.cdf(-z - lam)


def p_density_z(p, lam):
    z = stats.norm.isf(np.asarray(p, dtype=float) / 2)
    return (stats.norm.pdf(z - lam) + stats.norm.pdf(z + lam)) / (2 * stats.norm.pdf(z))


def p_median_z(lam):
    """The median p-value: two tails beyond the median of |Z|."""
    q = optimize.brentq(lambda q: stats.norm.cdf(q - lam) - stats.norm.cdf(-q - lam) - 0.5, 0.0, abs(lam) + 10)
    return 2 * stats.norm.sf(q)


def cumming_interval(p_two=0.05, level=0.80):
    """Cumming's p interval: where a replication's one-tailed p falls, given an original two-tailed p.

    With the true effect unknown, the replication's z differs from the original's by two independent unit
    errors, so z_rep ~ N(z_orig, 2).
    """
    z0, w = stats.norm.isf(p_two / 2), stats.norm.isf((1 - level) / 2) * math.sqrt(2)
    return float(stats.norm.sf(z0 + w)), float(stats.norm.sf(z0 - w))


def stage_pvalues(cfg, args):
    out = {}
    edges = np.linspace(0.0, 1.0, 21)
    R = cfg["pz"]
    lams = {"null": 0.0, "durante": DURANTE["plausible"] / DURANTE["se"], "lam1": 1.0, "lam2": 2.0, "lam28": 2.8}
    print(f"[pvalues] two-sided z-test, statistic N(lambda, 1), R = {R:,} per lambda")
    zs = {}
    for i, (key, lam) in enumerate(lams.items()):
        rng = stream(args.seed, "pvalues", i)
        p = 2 * stats.norm.sf(np.abs(lam + rng.standard_normal(R)))
        counts = np.histogram(p, edges)[0]
        exact = np.diff(p_cdf_z(edges, lam)) if lam else np.full(20, 0.05)
        below = float((p <= 0.05).mean())
        rec = dict(lam=lam, R=R, hist=counts / R, exact_bins=exact, share_05=below, share_05_mcse=mcse_share(below, R),
                   power_exact=float(p_cdf_z(0.05, lam)), median_exact=p_median_z(lam), median_sim=float(np.median(p)),
                   share_001=float((p <= 0.001).mean()), share_01=float((p <= 0.01).mean()), share_001_exact=float(p_cdf_z(0.001, lam)))
        if lam == 0:
            rec["chisq_p"] = float(stats.chisquare(counts).pvalue)
            rec["ks_p"] = float(stats.kstest(p, "uniform").pvalue)
        zs[key] = rec
        print(f"  {key:8s} lambda {lam:.4f}: P(p <= .05) {pm(below, rec['share_05_mcse'])} (exact {100 * rec['power_exact']:.2f}%), "
              f"median p {rec['median_sim']:.4f} (exact {rec['median_exact']:.4f})")
    grid = np.geomspace(1e-4, 1.0, 120)
    out["z"] = zs
    out["z_density"] = dict(p=grid, **{k: p_density_z(grid, lam) for k, lam in lams.items()})
    print(f"  null: 20 bins of width .05, chi-squared p {zs['null']['chisq_p']:.3f}, Kolmogorov-Smirnov p {zs['null']['ks_p']:.3f}")

    # Real t-tests on simulated data: Colquhoun's design, 16 per group.
    Rt = cfg["pt"]
    print(f"[pvalues] pooled two-sample t-tests, n = {DESIGN_N} per group, R = {Rt:,} per true difference")
    ts = {}
    for i, d in enumerate((0.0, 0.5, 1.0)):
        rng = stream(args.seed, "pvalues", 10 + i)
        p = simulate_ttests(rng, Rt, DESIGN_N, d)
        below = float((p <= 0.05).mean())
        ts[f"d{d:g}"] = dict(d=d, R=Rt, share_05=below, share_05_mcse=mcse_share(below, Rt), power_exact=nct_power(d, DESIGN_N),
                             hist=np.histogram(p, edges)[0] / Rt, median_sim=float(np.median(p)))
        print(f"  d = {d:.1f}: P(p <= .05) {pm(below, mcse_share(below, Rt))}, exact {100 * nct_power(d, DESIGN_N):.2f}%, "
              f"median p {np.median(p):.4f}")
    rng = stream(args.seed, "pvalues", 20)
    x, y = rng.standard_normal((200, DESIGN_N)) + 0.5, rng.standard_normal((200, DESIGN_N))
    mine, theirs = two_sample_t(x, y)[3], stats.ttest_ind(x, y, axis=1).pvalue
    ts["check_scipy_max_abs_diff"] = float(np.max(np.abs(mine - theirs)))
    out["t"] = ts
    print(f"  by-hand pooled t against scipy.stats.ttest_ind over 200 data sets: max |p difference| {ts['check_scipy_max_abs_diff']:.1e}")

    # The same experiment, 25 times: n = 16 per group, true difference 1 SD.
    rng = stream(args.seed, "pvalues", 30)
    x, y = rng.standard_normal((25, DESIGN_N)) + DESIGN_D, rng.standard_normal((25, DESIGN_N))
    diff, se, t, p = two_sample_t(x, y)
    half = stats.t.isf(0.025, 2 * DESIGN_N - 2) * se
    out["dance"] = dict(diff=diff, lo=diff - half, hi=diff + half, p=p, n_sig=int((p <= 0.05).sum()),
                        p_min=float(p.min()), p_max=float(p.max()))
    print(f"[pvalues] 25 repeats of one experiment (power {100 * nct_power(DESIGN_D, DESIGN_N):.1f}%): {int((p <= 0.05).sum())} "
          f"significant; p from {p.min():.2g} to {p.max():.2g}")

    # Cumming's p interval, in closed form and by simulation with a flat prior on the true effect.
    lo, hi = cumming_interval()
    Rc = cfg["cumming"]
    rng = stream(args.seed, "pvalues", 40)
    delta = rng.uniform(-4.0, 8.0, Rc)
    z0 = delta + rng.standard_normal(Rc)
    keep = (z0 > 0) & (np.abs(2 * stats.norm.sf(z0) - 0.05) <= 0.005)          # originals with two-tailed p in .045 to .055
    p_rep = stats.norm.sf(delta[keep] + rng.standard_normal(int(keep.sum())))   # the replication's one-tailed p
    kept = int(keep.sum())
    inside = float(((p_rep > lo) & (p_rep < hi)).mean())
    out["cumming"] = dict(lo=lo, hi=hi, R=Rc, kept=kept, inside=inside, inside_mcse=mcse_share(inside, kept),
                          below=float((p_rep <= lo).mean()), above=float((p_rep >= hi).mean()))
    print(f"[pvalues] Cumming's 80% p interval for a replication of p = .05: {lo:.6f} to {hi:.4f}; simulated "
          f"({kept:,} originals kept of {Rc:,}): inside {pm(inside, mcse_share(inside, kept))}")
    return out


# ------------------------------------------------------------------------------- power
def power_by_hand(d, n, alpha=0.05):
    """Two-sided pooled two-sample t-test, n per group.

    T = (Z + lam) / sqrt(V / df) with Z standard normal and V chi-squared on df degrees of freedom, so the
    power is the average over V of two normal tails: one integral, taken over V's quantiles u in (0, 1) so
    that the integrand stays smooth however large df is.
    """
    df, lam = 2 * n - 2, d * math.sqrt(n / 2)
    c = stats.t.isf(alpha / 2, df)

    def f(u):
        k = c * math.sqrt(stats.chi2.ppf(u, df) / df)
        return stats.norm.cdf(lam - k) + stats.norm.cdf(-lam - k)

    return integrate.quad(f, 0, 1, limit=200, epsabs=1e-13, epsrel=1e-11)[0]


def normal_power(d, n, alpha=0.05):
    lam, z = d * math.sqrt(n / 2), stats.norm.isf(alpha / 2)
    return float(stats.norm.sf(z - lam) + stats.norm.cdf(-z - lam))


def observed_power_z(p):
    """'Observed power': the power at the effect the data estimated, for a two-sided z-test. A function of p alone."""
    z = stats.norm.isf(np.asarray(p, dtype=float) / 2)
    return stats.norm.sf(Z975 - z) + stats.norm.cdf(-Z975 - z)


def stage_power(cfg, args):
    from statsmodels.stats.power import TTestIndPower
    sm = TTestIndPower()
    out = {}
    print("[power] two-sided pooled two-sample t-test at 5%: by hand (one integral), SciPy nct, statsmodels, normal approximation")
    checks = []
    for d, n in ((1.0, 16), (0.5, 64), (0.5, 16), (0.2, 100), (0.8, 26)):
        hand, nct, smv, nor = power_by_hand(d, n), nct_power(d, n), float(sm.power(d, n, 0.05)), normal_power(d, n)
        checks.append(dict(d=d, n=n, by_hand=hand, nct=nct, statsmodels=smv, normal=nor))
        print(f"  d {d:.1f}, n {n:3d}: by hand {hand:.6f}, nct {nct:.6f}, statsmodels {smv:.6f}, normal approx {nor:.6f}")
    out["checks"] = checks
    out["max_abs_diff_hand_nct"] = max(abs(c["by_hand"] - c["nct"]) for c in checks)
    out["max_abs_diff_sm_nct"] = max(abs(c["statsmodels"] - c["nct"]) for c in checks)
    nan = {}
    for d in (1.0, 0.8):                         # where the libraries' lower tail breaks
        for n in range(2, 401):
            df, lam = 2 * n - 2, d * math.sqrt(n / 2)
            c = stats.t.isf(0.025, df)
            if math.isnan(float(stats.nct.cdf(-c, df, lam))):
                nan[f"d{d:g}"] = dict(first_n=n, lam=lam, scipy_cdf_lower="nan", statsmodels=str(float(sm.power(d, n, 0.05))),
                                      by_hand=power_by_hand(d, n), stable_nct=nct_power(d, n))   # strings keep the JSON valid
                break
    out["nan_check"] = nan
    print("[power] SciPy's nct.cdf(-c, df, lam) for the lower tail: " + "; ".join(
        f"d {k[1:]} first NaN at n = {v['first_n']} (lam {v['lam']:.2f}), where statsmodels returns {v['statsmodels']} and the "
        f"integral gives {v['by_hand']:.12f}" for k, v in nan.items()))

    ns = np.unique(np.round(np.geomspace(2, 400, 80)).astype(int))
    out["curves"] = dict(n=ns, **{f"d{d:g}": [nct_power(d, int(n)) for n in ns] for d in (0.2, 0.5, 0.8, 1.0)},
                         **{f"normal_d{d:g}": [normal_power(d, int(n)) for n in ns] for d in (0.2, 0.5, 0.8, 1.0)})
    Rs = cfg["power_sim"]
    sims = []
    print(f"[power] simulated power, R = {Rs:,} per point")
    for j, (d, n) in enumerate([(0.2, 50), (0.2, 100), (0.2, 200), (0.2, 400), (0.5, 8), (0.5, 16), (0.5, 32), (0.5, 64), (0.5, 128),
                                (1.0, 4), (1.0, 8), (1.0, 16), (1.0, 32)]):
        p = simulate_ttests(stream(args.seed, "power", j), Rs, n, d)
        est = float((p <= 0.05).mean())
        sims.append(dict(d=d, n=n, sim=est, mcse=mcse_share(est, Rs), exact=nct_power(d, n)))
    out["sims"] = sims
    worst = max(abs(s["sim"] - s["exact"]) / s["mcse"] for s in sims if s["mcse"] > 0)
    out["sims_max_z"] = worst
    print("  " + "; ".join(f"d {s['d']:g} n {s['n']}: {100 * s['sim']:.1f}% (exact {100 * s['exact']:.1f})" for s in sims))
    print(f"  largest |simulated - exact| / MCSE: {worst:.2f}")

    sizes = {}
    for d in (0.2, 0.5, 0.8, 1.0):
        for target in (0.8, 0.9):
            n = 2
            while nct_power(d, n) < target:
                n += 1
            sizes[f"d{d:g}_p{int(100 * target)}"] = dict(n=n, power_at_n=nct_power(d, n),
                                                       statsmodels=float(sm.solve_power(effect_size=d, power=target, alpha=0.05)))
    out["sample_sizes"] = sizes
    print("[power] smallest n per group for 80% and 90% power: " +
          "; ".join(f"d {k.split('_')[0][1:]} {k.split('_')[1][1:]}%: {v['n']} (statsmodels {v['statsmodels']:.2f})" for k, v in sizes.items()))

    df, ncp = 2 * DESIGN_N - 2, DESIGN_D * math.sqrt(DESIGN_N / 2)
    c = stats.t.isf(0.025, df)
    tg = np.linspace(-4.5, 8.0, 251)
    t03 = float(stats.t.isf(0.015, df))
    out["design"] = dict(n=DESIGN_N, d=DESIGN_D, df=df, ncp=ncp, crit=c, power=nct_power(DESIGN_D, DESIGN_N), t_grid=tg,
                         h0=stats.t.pdf(tg, df), h1=stats.nct.pdf(tg, df, ncp), t_at_p03=t03, d_at_p03=t03 * math.sqrt(2 / DESIGN_N),
                         beta=float(stats.nct.cdf(c, df, ncp) - stats.nct.cdf(-c, df, ncp)))
    print(f"[power] the design: n {DESIGN_N} per group, d {DESIGN_D:g}: df {df}, noncentrality {ncp:.4f}, critical t {c:.4f}, "
          f"power {100 * out['design']['power']:.2f}%; p = .03 is t = {t03:.4f}, an observed difference of {out['design']['d_at_p03']:.3f} SD")
    pgrid = np.geomspace(1e-4, 1.0, 120)
    t_obs = stats.t.isf(pgrid / 2, df)
    op_t = stats.nct.sf(c, df, t_obs) + stats.nct.sf(c, df, -t_obs)
    out["observed_power"] = dict(p=pgrid, z=observed_power_z(pgrid), t30=op_t,
                                 table={f"{p:g}": float(observed_power_z(p)) for p in (0.001, 0.01, 0.05, 0.1, 0.2, 0.5)})
    print("[power] observed power of a z-test, a function of p alone: " +
          ", ".join(f"p {k} -> {v:.3f}" for k, v in out["observed_power"]["table"].items()))
    return out


# ------------------------------------------------------------------------------- retrodesign
def retrodesign_exact(A, s, alpha=0.05):
    """Power, type S rate and exaggeration ratio for an unbiased normal estimate (Lu, Qiu and Deng, Theorem 1)."""
    z, lam = stats.norm.isf(alpha / 2), A / s
    p_hi, p_lo = stats.norm.sf(z - lam), stats.norm.cdf(-z - lam)
    power = p_hi + p_lo
    exag = (stats.norm.pdf(lam + z) + stats.norm.pdf(lam - z)
            + lam * (stats.norm.cdf(lam + z) + stats.norm.cdf(lam - z) - 1)) / (lam * power)
    return dict(power=float(power), p_hi=float(p_hi), p_lo=float(p_lo), typeS=float(p_lo / power), exaggeration=float(exag))


def exaggeration_of(estimate, significant, A):
    """The exaggeration ratio from simulated estimates: the mean magnitude of the significant ones, over A."""
    return np.abs(estimate[significant]).mean() / A


def exaggeration_draft(estimate, significant, A):
    """An earlier draft of exaggeration_of (the E4 fault)."""
    return estimate[significant].mean() / A


def retrodesign_sim(A, s, rng, alpha=0.05, df=math.inf, n_sims=10_000, fault=False):
    """Gelman and Carlin's retrodesign(), ported line for line: the exaggeration ratio is simulated."""
    z = stats.t.isf(alpha / 2, df) if math.isfinite(df) else stats.norm.isf(alpha / 2)
    p_hi = stats.t.sf(z - A / s, df) if math.isfinite(df) else stats.norm.sf(z - A / s)
    p_lo = stats.t.cdf(-z - A / s, df) if math.isfinite(df) else stats.norm.cdf(-z - A / s)
    power = p_hi + p_lo
    estimate = A + s * (rng.standard_t(df, n_sims) if math.isfinite(df) else rng.standard_normal(n_sims))
    significant = np.abs(estimate) > s * z
    exag = (exaggeration_draft if fault else exaggeration_of)(estimate, significant, A)
    return dict(power=float(power), typeS=float(p_lo / power), exaggeration=float(exag), estimate=estimate, significant=significant)


def stage_retrodesign(cfg, args):
    out = {"cases": {}}
    print("[retrodesign] power, type S and exaggeration: closed form, one 10,000-draw simulation as Gelman and Carlin ran it, "
          f"and {cfg['retro_reps']:,} repeats of that simulation")
    cases = list(GC_CASES)
    if args.effect is not None or args.se is not None:
        cases = [("custom", args.effect if args.effect is not None else DURANTE["plausible"],
                  args.se if args.se is not None else DURANTE["se"], {})]
    for j, (key, A, s, published) in enumerate(cases):
        ex = retrodesign_exact(A, s)
        one = retrodesign_sim(A, s, stream(args.seed, "retrodesign", j), fault=args.fault)
        rng = stream(args.seed, "retrodesign", 100 + j)
        reps = np.array([retrodesign_sim(A, s, rng, fault=args.fault)["exaggeration"] for _ in range(cfg["retro_reps"])])
        big = retrodesign_sim(A, s, stream(args.seed, "retrodesign", 200 + j), n_sims=cfg["retro_big"], fault=args.fault)
        mags = np.abs(big["estimate"][big["significant"]])
        rec = dict(A=A, s=s, lam=A / s, exact=ex, published=published, sim_one=one["exaggeration"],
                   reps=dict(R=len(reps), mean=float(reps.mean()), sd=float(reps.std(ddof=1)),
                             q025=float(np.quantile(reps, 0.025)), q975=float(np.quantile(reps, 0.975))),
                   big=dict(n_sims=cfg["retro_big"], exaggeration=big["exaggeration"], mcse=float(mags.std(ddof=1) / math.sqrt(mags.size) / A),
                            typeS=float((big["estimate"][big["significant"]] < 0).mean()), power=float(big["significant"].mean())),
                   signed_mean_sig=float(big["estimate"][big["significant"]].mean()), mean_abs_sig=float(mags.mean()),
                   share_sig_negative=float((big["estimate"][big["significant"]] < 0).mean()), min_abs_sig=float(mags.min()))
        if "exaggeration" in published:
            rec["reps"]["share_at_or_above_published"] = float((reps >= published["exaggeration"] - 0.05).mean())
        out["cases"][key] = rec
        print(f"  {key:13s} A {A:g}, s {s:g}: power {ex['power']:.4f} (+ {ex['p_hi']:.4f}, - {ex['p_lo']:.4f}), type S {ex['typeS']:.4g}, "
              f"exaggeration {ex['exaggeration']:.4f}; their simulation {one['exaggeration']:.3f}; repeats "
              f"{rec['reps']['mean']:.3f} (SD {rec['reps']['sd']:.3f}); {cfg['retro_big']:,} draws {big['exaggeration']:.4f} +- {rec['big']['mcse']:.4f}"
              + (f"; published {published}" if published else ""))
        print(f"      significant estimates: signed mean {rec['signed_mean_sig']:.3f}, mean magnitude {rec['mean_abs_sig']:.3f}, "
              f"smallest magnitude {rec['min_abs_sig']:.3f}, share below zero {rec['share_sig_negative']:.4f}")

    A, s = DURANTE["plausible"], DURANTE["se"]
    z_obs = DURANTE["estimate"] / s
    crit = Z975 * s
    a, b = (crit - A) / s, (-crit - A) / s
    lam80 = optimize.brentq(lambda l: retrodesign_exact(l, 1.0)["power"] - 0.8, 0.5, 5.0)
    out["durante"] = dict(z_obs=z_obs, p_obs=float(2 * stats.norm.sf(z_obs)), critical=crit, min_exaggeration=crit / A,
                          mean_sig_pos=float(A + s * stats.norm.pdf(a) / stats.norm.sf(a)),
                          mean_sig_neg=float(A - s * stats.norm.pdf(b) / stats.norm.cdf(b)),
                          lam80=lam80, se80=A / lam80, n_multiplier80=(s / (A / lam80)) ** 2)
    du = out["durante"]
    print(f"[retrodesign] Durante et al.: z {z_obs:.4f}, p {du['p_obs']:.4f}; significance needs |estimate| > {crit:.3f}, "
          f"{du['min_exaggeration']:.2f} times the plausible 2; mean significant estimate +{du['mean_sig_pos']:.2f} or "
          f"{du['mean_sig_neg']:.2f}; 80% power at 2 needs SE {du['se80']:.4f}, {du['n_multiplier80']:.1f} times the data")
    lam = np.geomspace(0.01, 6.0, 140)
    curves = [retrodesign_exact(float(l), 1.0) for l in lam]
    out["curves"] = dict(lam=lam, power=[c["power"] for c in curves], typeS=[c["typeS"] for c in curves],
                         exaggeration=[c["exaggeration"] for c in curves])
    for target in (0.5, 0.2, 0.1, 0.06):
        l = optimize.brentq(lambda l: retrodesign_exact(l, 1.0)["power"] - target, 1e-6, 6.0)
        out.setdefault("at_power", {})[f"{target:g}"] = dict(lam=l, **retrodesign_exact(l, 1.0))
    print("[retrodesign] at power " + "; ".join(f"{k}: type S {v['typeS']:.3g}, exaggeration {v['exaggeration']:.2f}"
                                                for k, v in out["at_power"].items()))
    return out


# ------------------------------------------------------------------------------- replication
def read_osc():
    lines = [ln for ln in OSC_CSV.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    rows = []
    for r in csv.DictReader(lines):
        rows.append({k: (int(v) if k == "study" else (float(v) if v != "" else math.nan)) for k, v in r.items()})
    return rows


def fisher_ci(r, n, level):
    z, half = math.atanh(r), stats.norm.isf((1 - level) / 2) / math.sqrt(n - 3)
    return math.tanh(z - half), math.tanh(z + half)


def stage_replication(cfg, args):
    rows = read_osc()
    coded = [r for r in rows if not math.isnan(r["sig_orig"]) and not math.isnan(r["sig_rep"])]
    pairs = [r for r in coded if not math.isnan(r["r_orig"]) and not math.isnan(r["r_rep"])]
    ro, rr = np.array([r["r_orig"] for r in pairs]), np.array([r["r_rep"] for r in pairs])
    out = dict(coded=len(coded), sig_orig=int(sum(r["sig_orig"] for r in coded)), sig_rep=int(sum(r["sig_rep"] for r in coded)),
               sig_rep_given_sig_orig=int(sum(r["sig_rep"] for r in coded if r["sig_orig"] == 1)),
               pairs=len(pairs), mean_r_orig=float(ro.mean()), sd_r_orig=float(ro.std(ddof=1)),
               mean_r_rep=float(rr.mean()), sd_r_rep=float(rr.std(ddof=1)), mean_ratio=float(rr.mean() / ro.mean()),
               median_ratio=float(np.median(rr / ro)), share_rep_below_orig=float((rr < ro).mean()), rep_negative=int((rr < 0).sum()),
               median_n_orig=float(np.median([r["n_orig"] for r in pairs])), median_n_rep=float(np.median([r["n_rep"] for r in pairs])),
               sig_rep_pairs=int(sum(r["sig_rep"] for r in pairs)))
    print(f"[replication] {out['coded']} coded replications: {out['sig_orig']} originals and {out['sig_rep']} replications significant "
          f"({out['sig_rep_given_sig_orig']} of the {out['sig_orig']} significant originals replicated)")
    print(f"  {out['pairs']} pairs with both effect sizes: mean r {out['mean_r_orig']:.4f} (SD {out['sd_r_orig']:.4f}) originally, "
          f"{out['mean_r_rep']:.4f} (SD {out['sd_r_rep']:.4f}) on replication, ratio {out['mean_ratio']:.3f}; replication smaller in "
          f"{100 * out['share_rep_below_orig']:.1f}%, negative in {out['rep_negative']}; median n {out['median_n_orig']:.0f} and {out['median_n_rep']:.0f}")
    bands = {}
    for key, keep in (("p_below_001", lambda p: p < 0.001), ("p_001_to_05", lambda p: 0.001 <= p <= 0.05), ("p_above_05", lambda p: p > 0.05)):
        grp = [r for r in pairs if keep(r["p_orig"])]
        g_ro, g_rr = np.array([r["r_orig"] for r in grp]), np.array([r["r_rep"] for r in grp])
        bands[key] = dict(n=len(grp), replicated=int(sum(r["sig_rep"] for r in grp)),
                          mean_r_orig=float(g_ro.mean()), mean_r_rep=float(g_rr.mean()), ratio=float(g_rr.mean() / g_ro.mean()))
        print(f"  original {key}: {len(grp)} pairs, {bands[key]['replicated']} replicated, mean r {g_ro.mean():.3f} -> {g_rr.mean():.3f} "
              f"(ratio {bands[key]['ratio']:.2f})")
    out["by_original_p"] = bands
    crit = np.array([math.tanh(Z975 / math.sqrt(r["n_orig"] - 3)) for r in pairs])
    out["critical"] = dict(median_r_over_critical=float(np.median(ro / crit)), share_within_1_5=float((ro < 1.5 * crit).mean()))
    print(f"  originals' r over the smallest significant r for their n: median {out['critical']['median_r_over_critical']:.2f}; "
          f"{100 * out['critical']['share_within_1_5']:.1f}% within 1.5 times the bar")

    ns_rows = [r for r in pairs if r["sig_rep"] == 0]
    cis = sorted(((r["r_rep"],) + fisher_ci(r["r_rep"], r["n_rep"], 0.90) + (r["n_rep"], r["study"]) for r in ns_rows))
    out["nonsig"] = dict(n=len(ns_rows), r=[c[0] for c in cis], lo=[c[1] for c in cis], hi=[c[2] for c in cis],
                         n_rep=[c[3] for c in cis], study=[c[4] for c in cis])
    for bound in (0.1, 0.2):
        eq = sum(1 for c in cis if c[1] > -bound and c[2] < bound)
        n80 = math.ceil(((stats.norm.isf(0.05) + stats.norm.isf(0.10)) / math.atanh(bound)) ** 2 + 3)
        out["nonsig"][f"equivalent_{bound:g}"] = eq
        out["nonsig"][f"n_for_80_{bound:g}"] = n80
        print(f"  of the {len(ns_rows)} non-significant replications, {eq} are equivalent to zero within |r| below {bound:g} "
              f"(90% Fisher-z interval; showing that with 80% power needs n = {n80} when the truth is 0)")
    out["scatter"] = dict(r_orig=ro, r_rep=rr, sig_rep=[int(r["sig_rep"]) for r in pairs], p_orig=[r["p_orig"] for r in pairs],
                          n_orig=[r["n_orig"] for r in pairs], n_rep=[r["n_rep"] for r in pairs])
    out["data_sha1"] = sha1(OSC_CSV)
    return out


# ------------------------------------------------------------------------------- false positive risk
def ppv_ioannidis(power, R, u=0.0, alpha=0.05):
    """Ioannidis's positive predictive value with bias u; R is the pre-study odds of a true relationship."""
    b = 1 - power
    return ((1 - b) * R + u * b * R) / (R + alpha - b * R + u - u * alpha + u * b * R)


def fpr_less_than(prior, power, alpha=0.05):
    """Share of p <= alpha results that are false, when a share `prior` of tested effects is real."""
    return alpha * (1 - prior) / (alpha * (1 - prior) + power * prior)


def lr_p_equals(p, n=DESIGN_N, d=DESIGN_D):
    """Colquhoun's likelihood ratio for an observed two-sided p: the density of |t| under the alternative over the null."""
    df, lam = 2 * n - 2, d * math.sqrt(n / 2)
    t = stats.t.isf(np.asarray(p, dtype=float) / 2, df)
    return (stats.nct.pdf(t, df, lam) + stats.nct.pdf(-t, df, lam)) / (2 * stats.t.pdf(t, df))


def fpr_equals(p, prior):
    return 1 / (1 + lr_p_equals(p) * prior / (1 - prior))


def stage_fpr(cfg, args):
    out = {}
    table4 = [(0.80, 1, 0.10, 0.85), (0.95, 2, 0.30, 0.85), (0.80, 1 / 3, 0.40, 0.41), (0.20, 1 / 5, 0.20, 0.23),
              (0.20, 1 / 5, 0.80, 0.17), (0.80, 1 / 10, 0.30, 0.20), (0.20, 1 / 10, 0.30, 0.12), (0.20, 1 / 1000, 0.80, 0.0010),
              (0.20, 1 / 1000, 0.20, 0.0015)]
    out["ioannidis_table4"] = [dict(power=pw, R=R, u=u, published=pub, ppv=ppv_ioannidis(pw, R, u)) for pw, R, u, pub in table4]
    print("[fpr] Ioannidis 2005, Table 4, recomputed: " + ", ".join(f"{t['ppv']:.4f} ({t['published']:g})" for t in out["ioannidis_table4"]))
    tp, fp = 1000 * 0.1 * 0.8, 1000 * 0.9 * 0.05
    out["tree"] = dict(tests=1000, prior=0.1, power=0.8, true_pos=tp, false_pos=fp, fpr=fp / (fp + tp))
    print(f"[fpr] 1,000 tests, 10% real, power 80%: {tp:.0f} true and {fp:.0f} false positives, false positive risk {fp / (fp + tp):.4f}")
    priors = np.linspace(0.01, 0.99, 99)
    pw_design = nct_power(DESIGN_D, DESIGN_N)
    out["less_than"] = dict(prior=priors, **{f"power{int(round(100 * pw))}": fpr_less_than(priors, pw) for pw in (0.2, 0.5, 0.8)},
                            design_power=pw_design, design=fpr_less_than(priors, pw_design))
    odds10 = 1 / 11
    out["benjamin"] = dict(prior=odds10, at_power1_05=fpr_less_than(odds10, 1.0), at_power1_005=fpr_less_than(odds10, 1.0, 0.005),
                           at_power08_05=fpr_less_than(odds10, 0.8))
    print(f"[fpr] prior odds 1:10, alpha .05: false positive risk {out['benjamin']['at_power1_05']:.4f} at power 1, "
          f"{out['benjamin']['at_power08_05']:.4f} at 0.8; alpha .005: {out['benjamin']['at_power1_005']:.4f} at power 1")
    pts = {}
    for p in (0.05, 0.03, 0.01, 0.005, 0.001):
        pw_p = nct_power_level(p)                   # p-less-than: every result at or below p, with the power at that threshold
        pts[f"{p:g}"] = dict(lr=float(lr_p_equals(p)), fpr_prior05=float(fpr_equals(p, 0.5)), fpr_prior01=float(fpr_equals(p, 0.1)),
                             power_at_p=pw_p, less_than_prior05=fpr_less_than(0.5, pw_p, p), less_than_prior01=fpr_less_than(0.1, pw_p, p))
    out["equals"] = pts
    grid = np.geomspace(1e-4, 0.2, 100)
    pw_grid = np.array([nct_power_level(float(a)) for a in grid])
    out["equals_curve"] = dict(p=grid, prior05=fpr_equals(grid, 0.5), prior01=fpr_equals(grid, 0.1), power_at_p=pw_grid,
                               less_prior05=fpr_less_than(0.5, pw_grid, grid), less_prior01=fpr_less_than(0.1, pw_grid, grid))
    print(f"[fpr] p-equals, n = {DESIGN_N} per group, power {100 * pw_design:.2f}%: " + "; ".join(
        f"p {k}: LR {v['lr']:.3f}, FPR {v['fpr_prior05']:.4f} (prior .5) and {v['fpr_prior01']:.4f} (prior .1)" for k, v in pts.items()))
    print("[fpr] p-less-than at the same thresholds, with the power at each: " + "; ".join(
        f"p {k}: power {v['power_at_p']:.4f}, FPR {v['less_than_prior05']:.4f} and {v['less_than_prior01']:.4f}" for k, v in pts.items()))

    R = cfg["fpr"]
    p_null = simulate_ttests(stream(args.seed, "fpr", 0), R, DESIGN_N, 0.0)
    p_alt = simulate_ttests(stream(args.seed, "fpr", 1), R, DESIGN_N, DESIGN_D)
    sims = {}
    for key, lo, hi in (("near_05", 0.045, 0.05), ("near_03", 0.025, 0.035), ("at_most_05", 0.0, 0.05)):
        f0, f1 = float(((p_null > lo) & (p_null <= hi)).mean()), float(((p_alt > lo) & (p_alt <= hi)).mean())
        rec = dict(window=[lo, hi], null_share=f0, alt_share=f1, R=R)
        for prior in (0.5, 0.1):
            fpr = (1 - prior) * f0 / ((1 - prior) * f0 + prior * f1)
            # delta method: Var(f) = f(1 - f)/R for each arm, independent arms
            g0, g1 = prior * f1 * (1 - prior) / ((1 - prior) * f0 + prior * f1) ** 2, -(1 - prior) * f0 * prior / ((1 - prior) * f0 + prior * f1) ** 2
            rec[f"fpr_prior{str(prior).replace('.', '')}"] = fpr
            rec[f"mcse_prior{str(prior).replace('.', '')}"] = math.sqrt(g0 ** 2 * f0 * (1 - f0) / R + g1 ** 2 * f1 * (1 - f1) / R)
        sims[key] = rec
        print(f"  simulated {R:,} null and {R:,} real experiments, p in ({lo:g}, {hi:g}]: null {100 * f0:.3f}%, real {100 * f1:.3f}%; "
              f"false positive risk {pm(rec['fpr_prior05'], rec['mcse_prior05'])} (prior .5), {pm(rec['fpr_prior01'], rec['mcse_prior01'])} (prior .1)")
    out["simulated"] = sims
    out["colquhoun_window_exact_alt"] = nct_power_level(0.05) - nct_power_level(0.045)
    return out


def nct_power_level(alpha):
    return nct_power(DESIGN_D, DESIGN_N, alpha)


# ------------------------------------------------------------------------------- equivalence (TOST)
def tost_ind(x, y, low, upp):
    """Two one-sided pooled t-tests of low < mean(x) - mean(y) < upp, from first principles."""
    n1, n2 = len(x), len(y)
    df = n1 + n2 - 2
    diff = float(np.mean(x) - np.mean(y))
    sp2 = ((n1 - 1) * np.var(x, ddof=1) + (n2 - 1) * np.var(y, ddof=1)) / df
    se = math.sqrt(sp2 * (1 / n1 + 1 / n2))
    t1, t2 = (diff - low) / se, (diff - upp) / se
    p1, p2 = float(stats.t.sf(t1, df)), float(stats.t.cdf(t2, df))
    half = stats.t.isf(0.05, df) * se
    return dict(diff=diff, se=se, df=df, t1=t1, p1=p1, t2=t2, p2=p2, p=max(p1, p2), ci90=[diff - half, diff + half],
                p_nhst=float(2 * stats.t.sf(abs(diff) / se, df)))


def tost_power_exact(n, bound, alpha=0.05):
    """Power of the pooled TOST with n per group when the true difference is 0, in SD units.

    Given the estimated SD s, both one-sided tests reject when |difference| is below bound - t s sqrt(2/n);
    the difference is normal with SD sqrt(2/n), so the power is an average over s: one integral, as for power,
    taken only over the quantiles of s for which that interval exists.
    """
    df, k = 2 * n - 2, math.sqrt(2 / n)
    t = stats.t.isf(alpha, df)
    u_max = stats.chi2.cdf(df * (bound / (t * k)) ** 2, df)
    if u_max <= 0:
        return 0.0
    u = 0.5 * u_max * (GL_X + 1)                    # 200-point Gauss-Legendre on (0, u_max); agrees with quad to 1e-6
    h = bound - t * np.sqrt(stats.chi2.ppf(u, df) / df) * k
    return float(0.5 * u_max * np.sum(GL_W * (2 * stats.norm.cdf(h / k) - 1)))


def tost_reject_share(rng, reps, n, true_diff, bound):
    hits = 0
    for a in range(0, reps, BLOCK):
        m = min(BLOCK, reps - a)
        x, y = rng.standard_normal((m, n)) + true_diff, rng.standard_normal((m, n))
        diff, se, _, _ = two_sample_t(x, y)
        df = 2 * n - 2
        p = np.maximum(stats.t.sf((diff + bound) / se, df), stats.t.cdf((diff - bound) / se, df))
        hits += int((p <= 0.05).sum())
    return hits / reps


def stage_tost(cfg, args):
    from statsmodels.stats.weightstats import ttost_ind
    out = {}
    print("[tost] two one-sided tests by hand against statsmodels.stats.weightstats.ttost_ind (pooled)")
    for j, (key, n, true_diff, bound) in enumerate((("n100_bound03", 100, 0.0, 0.3), ("n16_bound05", DESIGN_N, 0.0, 0.5))):
        rng = stream(args.seed, "tost", j)
        x, y = rng.standard_normal(n) + true_diff, rng.standard_normal(n)
        mine = tost_ind(x, y, -bound, bound)
        p_sm, lower, upper = ttost_ind(x, y, -bound, bound, usevar="pooled")
        mine["statsmodels"] = dict(p=float(p_sm), t1=float(lower[0]), p1=float(lower[1]), t2=float(upper[0]), p2=float(upper[1]))
        mine["max_abs_diff"] = max(abs(mine[k] - mine["statsmodels"][k]) for k in ("p", "t1", "p1", "t2", "p2"))
        out[key] = mine
        print(f"  {key}: difference {mine['diff']:+.4f}, 90% CI {mine['ci90'][0]:+.4f} to {mine['ci90'][1]:+.4f}; t {mine['t1']:.4f} and "
              f"{mine['t2']:.4f}; TOST p {mine['p']:.6f} (statsmodels {p_sm:.6f}, max difference {mine['max_abs_diff']:.1e}); "
              f"ordinary t-test p {mine['p_nhst']:.4f}")
    R = cfg["tost"]
    size = tost_reject_share(stream(args.seed, "tost", 10), R, 69, 0.5, 0.5)
    out["size_at_bound"] = dict(n=69, bound=0.5, true_diff=0.5, R=R, rate=size, mcse=mcse_share(size, R))
    print(f"[tost] true difference on the bound (0.5 SD), n 69: rejects {pm(size, mcse_share(size, R))} (R = {R:,}); nominal 5%")
    zq, zp = stats.norm.isf(0.05), stats.norm.isf(0.10)
    pw = []
    for k, n in enumerate((16, 32, 50, 69, 100, 150)):
        est = tost_reject_share(stream(args.seed, "tost", 20 + k), R, n, 0.0, 0.5)
        approx = max(0.0, 2 * stats.norm.cdf(0.5 / math.sqrt(2 / n) - zq) - 1)
        pw.append(dict(n=n, power=est, mcse=mcse_share(est, R), normal=approx, exact=tost_power_exact(n, 0.5)))
    out["power_bound05"] = pw
    print("[tost] power to show equivalence within 0.5 SD when the truth is 0: " +
          ", ".join(f"n {r['n']} {100 * r['power']:.1f}% (exact {100 * r['exact']:.2f}, normal approx {100 * r['normal']:.1f})" for r in pw))
    ngrid = list(range(8, 161, 2))
    out["power_curve_bound05"] = dict(n=ngrid, exact=[tost_power_exact(n, 0.5) for n in ngrid])
    from statsmodels.stats.power import TTestIndPower as _TP
    bounds80 = {}
    for n in (8, 16, 32, 69, 100, 200, 400, 1000, 1713):
        b = optimize.brentq(lambda b: tost_power_exact(n, b) - 0.8, 0.01, 5.0, xtol=1e-7)
        bounds80[str(n)] = dict(tost_exact=b, tost_normal=(zq + zp) * math.sqrt(2 / n),
                                detectable=float(_TP().solve_power(nobs1=n, power=0.8, alpha=0.05)))
    out["bound80"] = bounds80
    print("[tost] narrowest bound TOST establishes with 80% power: " +
          ", ".join(f"n {k}: ±{v['tost_exact']:.3f} SD (an ordinary test detects {v['detectable']:.3f})" for k, v in bounds80.items()))
    from statsmodels.stats.power import TTestIndPower
    sizes = {}
    for bound in (0.1, 0.2, 0.3, 0.5):
        sizes[f"{bound:g}"] = dict(tost=math.ceil(2 * (zq + zp) ** 2 / bound ** 2),
                                   nhst=math.ceil(TTestIndPower().solve_power(effect_size=bound, power=0.8, alpha=0.05)))
    out["sample_sizes"] = sizes
    bounds = np.round(np.linspace(0.1, 0.8, 36), 4)
    out["sample_size_curve"] = dict(bound=bounds, tost=[2 * (zq + zp) ** 2 / b ** 2 for b in bounds],
                                    nhst=[float(TTestIndPower().solve_power(effect_size=float(b), power=0.8, alpha=0.05)) for b in bounds])
    print("[tost] n per group for 80% power: " + "; ".join(f"bound {k}: equivalence {v['tost']}, detecting it {v['nhst']}" for k, v in sizes.items()))
    return out


# ------------------------------------------------------------------------------- optional stopping
def stopping_exact(K, c=Z975, h=0.005):
    """P(|S_k| >= c sqrt(k) at some k <= K), S_k a sum of k independent N(0, 1): density propagation on a grid.

    The surviving density is convolved with the N(0, 1) kernel at each step (FFT), and the mass beyond the
    moving boundary is absorbed. Returns the cumulative rejection probability after each look.
    """
    L = c * math.sqrt(K) + 10.0
    s = np.arange(-L, L + h / 2, h)
    ks = np.arange(-int(8 / h), int(8 / h) + 1) * h
    kern = stats.norm.pdf(ks) * h
    g = stats.norm.cdf(s + h / 2) - stats.norm.cdf(s - h / 2)        # cell masses of S_1
    cum, absorbed = np.empty(K), 0.0
    for k in range(1, K + 1):
        if k > 1:
            g = signal.fftconvolve(g, kern, mode="same")
        out = np.abs(s) >= c * math.sqrt(k)
        absorbed += float(g[out].sum())
        g[out] = 0.0
        cum[k - 1] = absorbed
    return cum


def stage_stopping(cfg, args):
    out = {}
    K = 1000
    looks = (1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000)
    t0 = time.perf_counter()
    cum = stopping_exact(K)
    r = 1 / math.sqrt(2)
    two = 1 - stats.multivariate_normal(mean=[0, 0], cov=[[1, r], [r, 1]]).cdf([Z975, Z975], lower_limit=[-Z975, -Z975])
    out["exact"] = dict(looks=list(range(1, K + 1)), alpha=cum, at={str(k): float(cum[k - 1]) for k in looks}, check_two_looks=float(two),
                        seconds=round(time.perf_counter() - t0, 1))
    print("[stopping] a 5% z-test repeated after every observation (known variance), exact: " +
          ", ".join(f"{k} looks {100 * cum[k - 1]:.2f}%" for k in looks))
    print(f"  check: two looks from the bivariate normal {100 * two:.4f}%, grid {100 * cum[1]:.4f}%")
    R = cfg["stop_z"]
    rng = stream(args.seed, "stopping", 0)
    first = np.full(R, K + 1)
    bound = Z975 * np.sqrt(np.arange(1, K + 1))
    for a in range(0, R, 5_000):
        m = min(5_000, R - a)
        S = np.cumsum(rng.standard_normal((m, K)), axis=1)
        hit = np.abs(S) >= bound
        any_hit = hit.any(axis=1)
        first[a:a + m][any_hit] = hit[any_hit].argmax(axis=1) + 1
    sim = {str(k): float((first <= k).mean()) for k in looks}
    out["simulated"] = dict(R=R, at=sim, mcse={k: mcse_share(v, R) for k, v in sim.items()})
    worst = max(abs(sim[str(k)] - cum[k - 1]) / max(mcse_share(sim[str(k)], R), 1e-12) for k in looks)
    out["simulated"]["max_z"] = worst
    print(f"  simulated, R = {R:,} paths: " + ", ".join(f"{k} {100 * sim[str(k)]:.2f}%" for k in looks) + f"; largest |sim - exact|/MCSE {worst:.2f}")

    Rt = cfg["stop_t"]
    rng = stream(args.seed, "stopping", 1)
    n0, n1 = 10, 100
    rej_any = rej_last = 0
    for a in range(0, Rt, 5_000):
        m = min(5_000, Rt - a)
        x, y = rng.standard_normal((m, n1)), rng.standard_normal((m, n1))
        ns = np.arange(1, n1 + 1)
        mx, my = np.cumsum(x, axis=1) / ns, np.cumsum(y, axis=1) / ns
        sx = (np.cumsum(x * x, axis=1) - ns * mx ** 2) / np.maximum(ns - 1, 1)
        sy = (np.cumsum(y * y, axis=1) - ns * my ** 2) / np.maximum(ns - 1, 1)
        sl = slice(n0 - 1, n1)
        nn = ns[sl]
        t = (mx[:, sl] - my[:, sl]) / np.sqrt((sx[:, sl] + sy[:, sl]) / 2 * (2 / nn))
        p = 2 * stats.t.sf(np.abs(t), 2 * nn - 2)
        rej_any += int((p <= 0.05).any(axis=1).sum())
        rej_last += int((p[:, -1] <= 0.05).sum())
    a_any, a_last = rej_any / Rt, rej_last / Rt
    out["t_peeking"] = dict(n_from=n0, n_to=n1, looks=n1 - n0 + 1, R=Rt, alpha=a_any, mcse=mcse_share(a_any, Rt),
                            alpha_fixed=a_last, mcse_fixed=mcse_share(a_last, Rt))
    print(f"[stopping] t-test after every added pair from {n0} to {n1} per group ({n1 - n0 + 1} looks): rejects {pm(a_any, mcse_share(a_any, Rt))}; "
          f"the single test at {n1}: {pm(a_last, mcse_share(a_last, Rt))} (R = {Rt:,})")

    Rs = cfg["simmons"]
    rng = stream(args.seed, "stopping", 2)
    rej1 = rej2 = 0
    for a in range(0, Rs, BLOCK):
        m = min(BLOCK, Rs - a)
        x, y = rng.standard_normal((m, 30)), rng.standard_normal((m, 30))
        p20, p30 = two_sample_t(x[:, :20], y[:, :20])[3], two_sample_t(x, y)[3]
        rej1 += int((p20 <= 0.05).sum())
        rej2 += int(((p20 > 0.05) & (p30 <= 0.05)).sum())
    a_s = (rej1 + rej2) / Rs
    out["simmons"] = dict(n_first=20, n_added=10, R=Rs, alpha=a_s, mcse=mcse_share(a_s, Rs), first_look=rej1 / Rs)
    print(f"[stopping] test at 20 per group, add 10 per group if p > .05 and test again: rejects {pm(a_s, mcse_share(a_s, Rs))} (R = {Rs:,})")
    return out


# --------------------------------------------------------------------------------- driver
def provenance(args, budget):
    cpu = platform.processor() or platform.machine()
    try:
        for line in pathlib.Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    import statsmodels
    return {"captured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "os": f"{platform.system()} {platform.release()} {platform.machine()}", "cpu": cpu,
            "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "statsmodels": statsmodels.__version__, "testing_py_sha1": sha1(pathlib.Path(__file__)),
            "data_sha1": {OSC_CSV.name: sha1(OSC_CSV)}, "budget": budget, "seed": args.seed,
            "replications": QUICK if args.quick else FULL,
            "flags": {"effect": args.effect, "se": args.se, "fault": args.fault}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261029)
    parser.add_argument("--effect", type=float, default=None, help="retrodesign stage: the true effect to analyse (default: the published cases)")
    parser.add_argument("--se", type=float, default=None, help="retrodesign stage: the standard error to analyse")
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the retrodesign simulation")
    args = parser.parse_args()
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, NumPy {prov['numpy']}, "
          f"SciPy {prov['scipy']}, statsmodels {prov['statsmodels']}; testing.py {prov['testing_py_sha1']}; budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"pvalues": stage_pvalues, "power": stage_power, "retrodesign": stage_retrodesign, "replication": stage_replication,
             "fpr": stage_fpr, "tost": stage_tost, "stopping": stage_stopping}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
