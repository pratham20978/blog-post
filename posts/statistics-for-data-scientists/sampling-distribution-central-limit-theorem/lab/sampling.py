#!/usr/bin/env python3
"""Lab for "The Sampling Distribution: The CLT and Where n = 30 Fails".

Every number the article calls measured comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python sampling.py all --out mine.json            # every stage, the article's budget (about 2 minutes)
    python sampling.py all --quick --out quick.json   # the reader's budget (under a minute), noisier
    python sampling.py sampling --out mine.json       # one stage

Stages:
    population    4,317 customers' net spend, treated as the population: mean, SD, skewness, shape
    sampling      the mean of n customers drawn with replacement, n = 10 to 10,000: its sampling
                  distribution, the standard error against the standard deviation, and the two
                  one-sided error rates of a nominal 5% t-test
    skewness      the same t-test on seven populations of known skewness, against the Edgeworth rate
    student       Student's 1908 sleep data; a z reference with an estimated SD against Student's t
    berry         the Berry-Esseen bound against the exact distance to the normal, computed by
                  inverting the characteristic function
    heavy         infinite variance: Cauchy and Pareto (tail index 1.5) running means and t-test tails
    replications  how many replications a simulated rate needs, and one published simulation rerun

Every simulated rate is printed as estimate +- MCSE with its number of replications R. Every stage
draws from its own stream, SeedSequence([stage, sub-stream, seed]), so stages can run alone and repeat
to the bit with the same NumPy version.
"""

import argparse
import datetime
import hashlib
import json
import math
import pathlib
import platform
import time

import numpy as np
import scipy
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
SPEND_CSV = DATA / "online_retail_customer_spend.csv"
STAGES = ("population", "sampling", "skewness", "student", "berry", "heavy", "replications")

# Replications. The article quotes FULL; --quick is the reader's first run.
FULL = dict(sampling=100_000, skewness=100_000, student=1_000_000, heavy=20_000, heavy_big=2_000,
            truth=2_000_000, small_runs=500, mid_runs=125)
QUICK = dict(sampling=10_000, skewness=10_000, student=100_000, heavy=4_000, heavy_big=400,
             truth=200_000, small_runs=100, mid_runs=25)
CHUNK = 4_000_000                       # values drawn per block; fixed, so results do not depend on the machine
Z95 = stats.norm.ppf(0.95)              # 1.645, the one-sided 5% point
EDGE = (2 * Z95 ** 2 + 1) * stats.norm.pdf(Z95) / 6   # first-order Edgeworth coefficient for one tail


# ------------------------------------------------------------------------------- small helpers
def stream(seed, stage, sub=0):
    """An independent generator for (stage, sub-stream): varying ids first, the root seed last."""
    return np.random.default_rng(np.random.SeedSequence([STAGES.index(stage), sub, seed]))


def share(count, reps):
    """A simulated proportion and its Monte Carlo standard error, sqrt(p(1 - p)/R)."""
    p = count / reps
    return {"p": p, "mcse": math.sqrt(p * (1 - p) / reps), "R": reps}


def fmt_share(d, digits=2):
    return f"{100 * d['p']:.{digits}f}% +- {100 * d['mcse']:.{digits}f}"


def moments(x):
    """Mean, SD (divisor N), skewness, absolute third moment and excess kurtosis of a whole population."""
    x = np.asarray(x, float)
    mu = x.mean()
    d = x - mu
    sd = math.sqrt((d ** 2).mean())
    return {"mean": mu, "sd": sd, "skewness": (d ** 3).mean() / sd ** 3,
            "beta3": (np.abs(d) ** 3).mean() / sd ** 3, "excess_kurtosis": (d ** 4).mean() / sd ** 4 - 3}


def batch_mcse(values, statistic, batches=20):
    """MCSE of any statistic of R replicates, by batch means: the SD of the statistic over 20 equal batches,
    divided by sqrt(20)."""
    parts = np.array_split(np.asarray(values), batches)
    vals = np.array([statistic(p) for p in parts])
    return float(vals.std(ddof=1) / math.sqrt(batches))


def skew_of(x):
    d = x - x.mean()
    return float((d ** 3).mean() / (d ** 2).mean() ** 1.5)


def ks_to_normal(z):
    """Kolmogorov distance between the empirical CDF of z and the standard normal CDF."""
    z = np.sort(z)
    r = len(z)
    f = stats.norm.cdf(z)
    i = np.arange(1, r + 1)
    return float(max((i / r - f).max(), (f - (i - 1) / r).max()))


def t_tails(t, n):
    """Counts of the one-sided 5% rejections (t <= -t95, t >= t95) and two-sided 5% rejections."""
    c95, c975 = stats.t.ppf(0.95, n - 1), stats.t.ppf(0.975, n - 1)
    return int((t <= -c95).sum()), int((t >= c95).sum()), int((np.abs(t) >= c975).sum())


def simulate(draw, mean, n, reps, rng, keep=False):
    """R samples of size n from draw(rng, shape): t-test tail counts, and each sample's mean, SD and
    largest value if asked."""
    lo = hi = two = done = 0
    xbars, sds, tops = [], [], []
    rows = max(1, CHUNK // n)
    while done < reps:
        m = min(rows, reps - done)
        x = draw(rng, (m, n))
        xb, s = x.mean(1), x.std(1, ddof=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            t = (xb - mean) / (s / math.sqrt(n))          # s = 0 gives t = -inf or +inf, as SciPy reports
        a, b, c = t_tails(t, n)
        lo, hi, two = lo + a, hi + b, two + c
        if keep:
            xbars.append(xb)
            sds.append(s)
            tops.append(x.max(1))
        done += m
    out = {"lower": share(lo, reps), "upper": share(hi, reps), "two_sided": share(two, reps)}
    if keep:
        return out, np.concatenate(xbars), np.concatenate(sds), np.concatenate(tops)
    return out


def read_spend(cap=None):
    lines = [ln for ln in SPEND_CSV.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    x = np.array([float(ln.split(",")[1]) for ln in lines[1:]])
    if cap is not None:
        x = np.minimum(x, np.quantile(x, cap))         # winsorise the top: every value above the cap is set to it
    return x


# ------------------------------------------------------------------------------- the population
def stage_population(cfg, args):
    x = read_spend(args.cap)
    n = len(x)
    m = moments(x)
    q = np.quantile(x, [0.1, 0.25, 0.5, 0.75, 0.9, 0.99])
    desc = np.sort(x)[::-1]
    top1, top10 = n // 100, n // 10
    edges = np.round(np.arange(0.0, 5.6001, 0.1), 1)
    counts, _ = np.histogram(np.log10(x), bins=edges)
    out = {"N": n, "total": float(x.sum()), **m, "median": float(q[2]),
           "quantiles": dict(zip(["p10", "p25", "p50", "p75", "p90", "p99"], q.tolist())),
           "min": float(x.min()), "max": float(x.max()), "largest_3": desc[:3].tolist(),
           "top1": {"customers": top1, "share_of_spend": float(desc[:top1].sum() / x.sum())},
           "top10": {"customers": top10, "share_of_spend": float(desc[:top10].sum() / x.sum())},
           "share_below_mean": float((x < m["mean"]).mean()),
           "max_in_sds": float((x.max() - m["mean"]) / m["sd"]),
           "hist_log10_edges": edges.tolist(), "hist_counts": counts.tolist(), "cap": args.cap}
    if args.cap:
        out["cap_value"] = float(x.max())
    print(f"population: {n:,} customers, total GBP {out['total']:,.2f}"
          + (f" (capped at quantile {args.cap}: GBP {x.max():,.2f})" if args.cap else ""))
    print(f"  mean {m['mean']:,.2f}, median {q[2]:,.2f}, SD {m['sd']:,.2f} (divisor N: the whole population)")
    print(f"  skewness {m['skewness']:.3f}, E|X - mu|^3 / sd^3 = {m['beta3']:.3f}, excess kurtosis {m['excess_kurtosis']:.1f}")
    print(f"  {out['share_below_mean']:.1%} of customers spend less than the mean; the top 1% ({top1} customers) "
          f"hold {out['top1']['share_of_spend']:.1%} of all spend, the top 10% {out['top10']['share_of_spend']:.1%}")
    print(f"  largest {desc[0]:,.2f}, {out['max_in_sds']:.1f} SDs above the mean; quantiles 10/50/90/99%: "
          + ", ".join(f"{v:,.2f}" for v in q[[0, 2, 4, 5]]))
    return out


# ------------------------------------------------------------------------------- sampling the mean
SAMPLING_N = (10, 30, 100, 300, 1000, 3000, 10000)
MAIN_N = (10, 30, 100, 1000)


def draw_customers(pop, fault):
    if not fault:
        return lambda rng, shape: pop[rng.integers(0, len(pop), size=shape)]

    def shuffled(rng, shape):                      # an earlier draft: shuffle the customers, take the first n
        return np.stack([rng.permutation(pop)[:shape[1]] for _ in range(shape[0])])
    return shuffled


def stage_sampling(cfg, args):
    pop = read_spend(args.cap)
    m = moments(pop)
    mu, sd, gamma = m["mean"], m["sd"], m["skewness"]
    draw = draw_customers(pop, args.fault)
    reps = cfg["sampling"]
    out = {"population": {"N": len(pop), "mean": mu, "sd": sd, "skewness": gamma, "n_needed": n_needed(gamma)},
           "by_n": {}}
    print(f"sampling: R = {reps:,} samples of each size, drawn with replacement from the {len(pop):,} customers")
    print(f"     n   SE sim / SE theory              skew of mean (exact)  P(mean < mu)   lower tail      upper tail      two-sided")
    top1_floor = np.sort(pop)[::-1][len(pop) // 100 - 1]      # the 43rd-largest spend: the top 1% start here
    for i, n in enumerate(SAMPLING_N):
        tails, xb, s, top = simulate(draw, mu, n, reps, stream(args.seed, "sampling", i), keep=True)
        se = sd / math.sqrt(n)
        se_sim = float(xb.std(ddof=1))
        d2 = (xb - xb.mean()) ** 2
        se_sim_mcse = float(math.sqrt(max(((d2 ** 2).mean() - d2.mean() ** 2) / reps, 0)) / (2 * se_sim))
        z = (xb - mu) / se
        below = share(int((xb < mu).sum()), reps)
        rec = {"R": reps, "se_theory": se, "se_sim": se_sim, "se_sim_mcse": se_sim_mcse,
               "se_ratio": se_sim / se, "mean_of_means": float(xb.mean()),
               "mean_of_means_mcse": se_sim / math.sqrt(reps),
               "skew_exact": gamma / math.sqrt(n), "skew_sim": skew_of(xb), "skew_sim_mcse": batch_mcse(xb, skew_of),
               "median_of_means": float(np.median(xb)), "p_mean_below_mu": below,
               "s_over_sigma_quantiles": dict(zip(["q10", "q25", "q50", "q75", "q90"],
                                                  np.quantile(s / sd, [0.1, 0.25, 0.5, 0.75, 0.9]).tolist())),
               "p_s_below_sigma": share(int((s < sd).sum()), reps),
               "mean_s2_over_sigma2": float((s ** 2).mean() / sd ** 2),
               "mean_s2_over_sigma2_mcse": float((s ** 2 / sd ** 2).std(ddof=1) / math.sqrt(reps)),
               "corr_mean_sd": float(np.corrcoef(xb, s)[0, 1]),
               "ks_sim": ks_to_normal(z), **tails}
        if n in MAIN_N:
            edges = np.round(np.arange(-4.0, 8.0001, 0.1), 1)
            counts, _ = np.histogram(z, bins=edges)
            rec["hist_z_edges"] = edges.tolist()
            rec["hist_z_counts"] = counts.tolist()
            rec["hist_z_below"] = int((z < -4).sum())
            rec["hist_z_above"] = int((z >= 8).sum())
        if n == 30:
            rec["scatter_mean"] = xb[:3000].round(2).tolist()
            rec["scatter_sd"] = s[:3000].round(2).tolist()
            rec["t95"] = float(stats.t.ppf(0.95, n - 1))
            # The mechanism: does the sample hold one of the 43 biggest customers?
            has = top >= top1_floor
            t = (xb - mu) / (s / math.sqrt(n))
            c95 = rec["t95"]
            rec["top1"] = {"floor": float(top1_floor), "p_sample_has_one": share(int(has.sum()), reps),
                           "p_has_one_exact": 1 - (1 - (len(pop) // 100) / len(pop)) ** n,
                           "lower_given_none": share(int((t[~has] <= -c95).sum()), int((~has).sum())),
                           "lower_given_one": share(int((t[has] <= -c95).sum()), int(has.sum())),
                           "p_below_mu_given_none": share(int((xb[~has] < mu).sum()), int((~has).sum()))}
        out["by_n"][str(n)] = rec
        print(f"{n:6d}   {se_sim:8.2f} / {se:7.2f} = {se_sim / se:.3f} +- {se_sim_mcse / se:.3f}"
              f"   {rec['skew_sim']:6.2f} ({rec['skew_exact']:5.2f})   {fmt_share(below, 1):>12}   "
              f"{fmt_share(tails['lower']):>13}   {fmt_share(tails['upper']):>13}   {fmt_share(tails['two_sided']):>13}")
    nn = out["population"]["n_needed"]
    print(f"  skewness {gamma:.2f}: n needed by Cochran's rule {nn['cochran_25g2']:,.0f}; for each one-sided 5% test "
          f"within 10% {nn['one_sided_within_10pct']:,.0f}; for each tail of a two-sided test within 10% "
          f"{nn['two_sided_tails_within_10pct']:,.0f} (first-order Edgeworth)")
    r30 = out["by_n"]["30"]
    tp = r30["top1"]
    print(f"  n = 30: median s / sigma = {r30['s_over_sigma_quantiles']['q50']:.3f}; s < sigma in "
          f"{fmt_share(r30['p_s_below_sigma'], 1)} of samples; mean s^2 / sigma^2 = {r30['mean_s2_over_sigma2']:.3f} "
          f"+- {r30['mean_s2_over_sigma2_mcse']:.3f}; corr(mean, s) = {r30['corr_mean_sd']:.3f}")
    print(f"  n = 30: {fmt_share(tp['p_sample_has_one'], 1)} of samples hold one of the 43 biggest customers (spend >= "
          f"{tp['floor']:,.2f}; exact {100 * tp['p_has_one_exact']:.1f}%); the lower tail rejects "
          f"{fmt_share(tp['lower_given_none'], 1)} of the others and {fmt_share(tp['lower_given_one'], 1)} of those; "
          f"the mean is below mu in {fmt_share(tp['p_below_mu_given_none'], 1)} of the others")
    return out


# ------------------------------------------------------------------------------- populations of known skewness
GY_COUNTS = [447, 132, 42, 21, 3, 2]          # Greenwood and Yule's 647 women, as in Part 1
SKEW_N = (10, 30, 100, 300, 1000)


def lognormal_product_skewness():
    """Exact skewness of a product of 12 independent Uniform(0.5, 1.5) effects, from raw moments."""
    raw = [((1.5 ** (j + 1) - 0.5 ** (j + 1)) / (j + 1)) ** 12 for j in (1, 2, 3)]   # E[X], E[X^2], E[X^3]
    m1, m2, m3 = raw
    var = m2 - m1 ** 2
    return (m3 - 3 * m1 * m2 + 2 * m1 ** 3) / var ** 1.5


def product_of_12(rng, shape):
    x = rng.uniform(0.5, 1.5, shape)               # factor by factor, so memory stays at two arrays
    for _ in range(11):
        x *= rng.uniform(0.5, 1.5, shape)
    return x


def populations():
    """(key, label, mean, exact skewness, draw). Part 1's stories, plus Wilcox and Rousselet's lognormal."""
    lam = 537 / 576
    x = np.arange(6)
    f = np.array(GY_COUNTS, float)
    mu = (x * f).sum() / f.sum()
    s2 = (f * (x - mu) ** 2).sum() / (f.sum() - 1)
    k = mu * mu / (s2 - mu)
    nb_skew = (1 + 2 * mu / k) / math.sqrt(mu * (1 + mu / k))
    e = math.e
    return [
        ("normal", "normal", 0.0, 0.0, lambda r, s: r.standard_normal(s)),
        ("t5_unit_variance", "unit-variance t5", 0.0, 0.0, lambda r, s: r.standard_t(5, s) / math.sqrt(5 / 3)),
        ("poisson_clarke", "Poisson, Clarke's rate 0.932", lam, 1 / math.sqrt(lam), lambda r, s: r.poisson(lam, s)),
        ("exponential", "exponential", 1.0, 2.0, lambda r, s: r.exponential(1.0, s)),
        ("negbin_greenwood_yule", "negative binomial, Greenwood and Yule", mu, nb_skew,
         lambda r, s: r.negative_binomial(k, k / (k + mu), s)),
        ("lognormal_product", "product of 12 effects (Part 1)", 1.0, lognormal_product_skewness(), product_of_12),
        ("lognormal_sigma1", "standard lognormal", math.exp(0.5), (e + 2) * math.sqrt(e - 1),
         lambda r, s: r.lognormal(0.0, 1.0, s)),
    ]


def n_needed(gamma):
    """Sample sizes from three skewness rules (gamma = 0 needs none)."""
    z975 = stats.norm.ppf(0.975)
    two = (2 * z975 ** 2 + 1) * stats.norm.pdf(z975) / 6
    return {"cochran_25g2": 25 * gamma ** 2,                          # two-sided 95% interval covers at least 94%
            "one_sided_within_10pct": (EDGE * gamma / 0.005) ** 2,    # each one-sided 5% test between 4.5% and 5.5%
            "two_sided_tails_within_10pct": (two * gamma / 0.0025) ** 2}  # each tail of a two-sided 5% test 2.25-2.75%


def stage_skewness(cfg, args):
    reps = cfg["skewness"]
    out = {"R": reps, "edgeworth_coefficient": EDGE, "z95": Z95, "populations": {}}
    print(f"skewness: R = {reps:,} t-tests per population and n; first-order Edgeworth: lower tail = 5% + "
          f"{EDGE:.4f} x skewness / sqrt(n)")
    for i, (key, label, mean, gamma, draw) in enumerate(populations()):
        rec = {"label": label, "mean": mean, "skewness": gamma, "n_needed": n_needed(gamma), "by_n": {}}
        line = []
        for j, n in enumerate(SKEW_N):
            tails = simulate(draw, mean, n, reps, stream(args.seed, "skewness", 10 * i + j))
            tails["edgeworth_lower"] = 0.05 + EDGE * gamma / math.sqrt(n)
            tails["edgeworth_upper"] = 0.05 - EDGE * gamma / math.sqrt(n)
            rec["by_n"][str(n)] = tails
            line.append(f"n={n}: {100 * tails['lower']['p']:.2f}/{100 * tails['upper']['p']:.2f}")
        out["populations"][key] = rec
        nn = rec["n_needed"]
        print(f"  {label:38s} skew {gamma:5.2f} | lower/upper % " + "  ".join(line))
        print(f"  {'':38s}   n needed: Cochran {nn['cochran_25g2']:,.0f}; one-sided within 10% "
              f"{nn['one_sided_within_10pct']:,.0f}; two-sided tails within 10% {nn['two_sided_tails_within_10pct']:,.0f}")
    ln = out["populations"]["lognormal_sigma1"]["by_n"]
    print(f"  standard lognormal, two-sided 5% test: n = 30 {fmt_share(ln['30']['two_sided'])}, "
          f"n = 100 {fmt_share(ln['100']['two_sided'])} (Wilcox and Rousselet print 0.111 and 0.116; 0.082 and 0.087)")
    return out


# ------------------------------------------------------------------------------- Student's t
def stage_student(cfg, args):
    lines = [ln for ln in (DATA / "student1908_sleep.csv").read_text(encoding="utf-8").splitlines()
             if ln and not ln.startswith("#")]
    rows = [ln.split(",") for ln in lines[1:]]
    d = np.array([float(b) - float(a) for _, a, b in rows])
    n = len(d)
    mean = d.mean()
    s1, s0 = d.std(ddof=1), d.std(ddof=0)            # divisor n - 1 (today), and n (Student's s.d.)
    z_student = mean / s0
    t = mean / (s1 / math.sqrt(n))
    p_one = stats.t.sf(t, n - 1)
    out = {"differences": d.tolist(), "n": n, "mean": mean, "sd_n_minus_1": s1, "sd_n": s0,
           "student_z": z_student, "t": t, "t_from_z": z_student * math.sqrt(n - 1),
           "p_one_sided": p_one, "p_two_sided": 2 * p_one, "odds": (1 - p_one) / p_one,
           "p_two_sided_normal_reference": 2 * stats.norm.sf(t),
           "t975": stats.t.ppf(0.975, n - 1), "z975": stats.norm.ppf(0.975),
           "p_abs_t9_beyond_z975": 2 * stats.t.sf(stats.norm.ppf(0.975), n - 1)}
    reps = cfg["student"]
    rng = stream(args.seed, "student", 0)
    z_rej = t_rej = done = 0
    rows_ = CHUNK // n
    while done < reps:
        m = min(rows_, reps - done)
        x = rng.standard_normal((m, n))
        tt = x.mean(1) / (x.std(1, ddof=1) / math.sqrt(n))
        z_rej += int((np.abs(tt) >= out["z975"]).sum())
        t_rej += int((np.abs(tt) >= out["t975"]).sum())
        done += m
    out["sim_normal_n10"] = {"z_with_s": share(z_rej, reps), "t": share(t_rej, reps)}
    xs = np.linspace(-5, 5, 401)
    out["density_x"] = xs.tolist()
    out["density_t9"] = stats.t.pdf(xs, n - 1).tolist()
    out["density_normal"] = stats.norm.pdf(xs).tolist()
    print(f"student: sleep gained, drug 2 minus drug 1, {n} patients: {np.array2string(d, separator=', ')}")
    print(f"  mean {mean:.4f}; s.d. {s0:.4f} with divisor n (Student's), {s1:.4f} with n - 1")
    print(f"  Student's z = mean / s.d. = {z_student:.4f}; t = mean / (s / sqrt(n)) = {t:.4f} = z x sqrt(n - 1)")
    print(f"  P(T9 > t) = {p_one:.6f} (two-sided {2 * p_one:.6f}); odds {out['odds']:.1f} to 1 that the mean is positive")
    print(f"  normal reference with the estimated s: two-sided p = {out['p_two_sided_normal_reference']:.3g}, "
          f"{2 * p_one / out['p_two_sided_normal_reference']:.0f} times smaller")
    print(f"  normal data, n = 10, R = {reps:,}: |t| >= 1.960 rejects {fmt_share(out['sim_normal_n10']['z_with_s'])} "
          f"(exact {100 * out['p_abs_t9_beyond_z975']:.2f}%); |t| >= {out['t975']:.3f} rejects {fmt_share(out['sim_normal_n10']['t'])}")
    return out


# ------------------------------------------------------------------------------- Berry-Esseen
C0_UPPER = 0.469                                  # best proven constant (Shevtsova 2013)
C0_LOWER = (math.sqrt(10) + 3) / (6 * math.sqrt(2 * math.pi))   # Esseen 1956: no constant below this works
BERRY_N = (10, 30, 100, 300, 1000, 3000, 10000, 30000, 100000, 300000, 1000000)


def exact_ks(cdf_at, xs=None):
    """sup |F(x) - Phi(x)| on a grid, refined around the largest gap."""
    xs = np.linspace(-4, 4, 1601) if xs is None else xs
    gap = np.abs(cdf_at(xs) - stats.norm.cdf(xs))
    k = int(gap.argmax())
    fine = np.linspace(xs[max(k - 1, 0)], xs[min(k + 1, len(xs) - 1)], 401)
    gf = np.abs(cdf_at(fine) - stats.norm.cdf(fine))
    j = int(gf.argmax())
    return float(gf[j]), float(fine[j])


def cf_cdf(log_psi, n, dt=0.004):
    """CDF of the standardised mean of n draws by Gil-Pelaez inversion:
    F(x) = 1/2 - (1/pi) * integral over t > 0 of Im[exp(-itx) phi_n(t)] / t, with phi_n(t) = psi(t / sqrt(n))^n.
    The range doubles until |phi_n| < 1e-7, so the truncation error is negligible."""
    T = 10.0
    while True:
        t = (np.arange(int(T / dt)) + 0.5) * dt              # midpoint rule, never t = 0
        lphi = n * log_psi(t / math.sqrt(n))
        if np.exp(lphi[-1].real) < 1e-7 or T > 400:
            break
        T *= 2
    phi = np.exp(lphi)

    def F(xs):
        xs = np.atleast_1d(xs)
        res = np.empty(len(xs))
        for i in range(0, len(xs), 50):
            xx = xs[i:i + 50, None]
            res[i:i + 50] = 0.5 - (np.imag(np.exp(-1j * t * xx) * phi) / t).sum(1) * dt / math.pi
        return res
    return F, T


def spend_log_psi(pop):
    m = moments(pop)
    dz = (pop - m["mean"]) / m["sd"]

    def log_psi(u):
        out = np.empty(len(u), complex)
        for i in range(0, len(u), 1000):
            out[i:i + 1000] = np.log(np.exp(1j * np.outer(u[i:i + 1000], dz)).mean(1))
        return out
    return log_psi


def exp_log_psi(u):                               # Exp(1), centred: E exp(iu(X - 1)) = exp(-iu) / (1 - iu)
    return -1j * u - np.log(1 - 1j * u)


def stage_berry(cfg, args):
    pop = read_spend(args.cap)
    m = moments(pop)
    out = {"C0_upper": C0_UPPER, "C0_lower_esseen": C0_LOWER, "target": 0.01}
    # Check the inversion where the answer is known: the mean of n exponentials is a gamma.
    check = {}
    for n in (10, 100, 1000):
        exact, _ = exact_ks(lambda x, n=n: stats.gamma.cdf(n + x * math.sqrt(n), n))
        inv, _ = exact_ks(cf_cdf(exp_log_psi, n)[0])
        check[str(n)] = {"gamma_exact": exact, "inversion": inv}
    out["inversion_check_exponential"] = check
    worst = max(abs(v["gamma_exact"] - v["inversion"]) for v in check.values())
    print(f"berry: inversion checked on the exponential (exact gamma CDF): KS distances agree to {worst:.1e}")
    for key, beta3, gamma, cdf_for in (
            ("exponential", 12 / math.e - 2, 2.0,
             lambda n: (lambda x: stats.gamma.cdf(n + x * math.sqrt(n), n))),
            ("spend", m["beta3"], m["skewness"], lambda n, lp=spend_log_psi(pop): cf_cdf(lp, n)[0])):
        rec = {"beta3": beta3, "skewness": gamma, "by_n": {}}
        for n in BERRY_N:
            ks, at = exact_ks(cdf_for(n))
            rec["by_n"][str(n)] = {"exact": ks, "at_x": at, "bound": C0_UPPER * beta3 / math.sqrt(n),
                                   "edgeworth": gamma * stats.norm.pdf(0) / (6 * math.sqrt(n))}
        lo, hi = 10, 1_000_000                     # smallest n with exact distance <= 0.01, by bisection
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if exact_ks(cdf_for(mid))[0] <= 0.01:
                hi = mid
            else:
                lo = mid
        rec["n_good"] = hi
        rec["n_guaranteed"] = math.ceil((C0_UPPER * beta3 / 0.01) ** 2)
        rec["n_guaranteed_esseen_floor"] = math.ceil((C0_LOWER * beta3 / 0.01) ** 2)
        out[key] = rec
        print(f"  {key}: beta3 = {beta3:.4f}; distance <= 0.01 from n = {hi:,} (exact); Berry-Esseen with C0 = "
              f"{C0_UPPER} guarantees it from n = {rec['n_guaranteed']:,} ({rec['n_guaranteed'] / hi:.0f} times later); "
              f"no C0 >= {C0_LOWER:.4f} could guarantee it before n = {rec['n_guaranteed_esseen_floor']:,}")
        print("    n: exact / bound  " + "  ".join(f"{n:,}: {v['exact']:.4f}/{v['bound']:.4f}" for n, v in
                                                 ((int(k), v) for k, v in rec["by_n"].items()) if n in (30, 1000, 10000, 100000)))
    return out


# ------------------------------------------------------------------------------- infinite variance
HEAVY_N = (10, 100, 1000, 10000, 100000)
CHECKPOINTS = np.unique(np.logspace(0, 6, 241).astype(int))


def pareto15(rng, shape):
    return rng.pareto(1.5, shape) + 1.0            # NumPy's pareto is Lomax; adding 1 gives P(X > x) = x^-1.5, x >= 1


def stage_heavy(cfg, args):
    out = {"checkpoints": CHECKPOINTS.tolist(), "running_means": {}}
    for i, (key, draw) in enumerate((("cauchy", lambda r, k: r.standard_cauchy(k)), ("pareto15", pareto15),
                                     ("exponential", lambda r, k: r.exponential(1.0, k)))):
        runs = []
        for j in range(3):
            x = draw(stream(args.seed, "heavy", 10 * i + j), 1_000_000)
            runs.append((np.cumsum(x)[CHECKPOINTS - 1] / CHECKPOINTS).tolist())
        out["running_means"][key] = runs
    reps = cfg["heavy"]
    iqr = {}
    for j, n in enumerate((1, 10, 100, 1000)):
        rng = stream(args.seed, "heavy", 100 + j)
        means = np.concatenate([rng.standard_cauchy((min(CHUNK // n, reps - k), n)).mean(1)
                                for k in range(0, reps, CHUNK // n)])
        q1, q3 = np.quantile(means, [0.25, 0.75])
        iqr[str(n)] = {"iqr": float(q3 - q1), "mcse": batch_mcse(means, lambda v: np.subtract(*np.quantile(v, [0.75, 0.25])))}
    out["cauchy_mean_iqr"] = iqr
    pareto = {}
    for j, n in enumerate(HEAVY_N):
        r = cfg["heavy_big"] if n >= 100000 else reps
        tails, xb, _, _ = simulate(pareto15, 3.0, n, r, stream(args.seed, "heavy", 200 + j), keep=True)
        q1, q3 = np.quantile(xb, [0.25, 0.75])
        tails["iqr_of_mean"] = float(q3 - q1)
        tails["p_mean_below_3"] = share(int((xb < 3.0).sum()), r)
        pareto[str(n)] = tails
    out["pareto15_ttest"] = pareto
    print(f"heavy: running means of 1,000,000 draws, three seeds each, at n = 10, 1,000, 1,000,000:")
    for key, runs in out["running_means"].items():
        idx = [int(np.searchsorted(CHECKPOINTS, v)) for v in (10, 1000, 1_000_000)]
        print(f"  {key:12s} " + " | ".join(", ".join(f"{run[k]:9.3f}" for k in idx) for run in runs))
    print("  Cauchy: interquartile range of the mean of n draws (one draw: 2) "
          + ", ".join(f"n = {n}: {v['iqr']:.3f} +- {v['mcse']:.3f}" for n, v in iqr.items()))
    print("  Pareto, tail index 1.5 (mean 3), one-sided 5% t-test lower/upper tail:")
    for n, v in pareto.items():
        print(f"    n = {int(n):7,d}: lower {fmt_share(v['lower'])}, upper {fmt_share(v['upper'])}; "
              f"IQR of the mean {v['iqr_of_mean']:.4f}; mean below 3 in {fmt_share(v['p_mean_below_3'], 1)} (R = {v['lower']['R']:,})")
    return out


# ------------------------------------------------------------------------------- replications
def stage_replications(cfg, args):
    out = {"R_for_target": {}}
    for p in (0.05, 0.5):
        out["R_for_target"][str(p)] = {str(t): math.ceil(p * (1 - p) / t ** 2) for t in (0.01, 0.005, 0.001, 0.0005)}
    draw = lambda r, s: r.lognormal(0.0, 1.0, s)
    mu = math.exp(0.5)
    published = {"30": {"2017": (0.111, 5000), "2023": (0.116, 20000)},
                 "100": {"2017": (0.082, 5000), "2023": (0.087, 20000)}}
    for j, n in enumerate((30, 100)):
        truth = simulate(draw, mu, n, cfg["truth"], stream(args.seed, "replications", j))["two_sided"]
        rec = {"truth": truth, "published": {}, "small_runs": {}}
        for k, (year, (value, r)) in enumerate(published[str(n)].items()):
            runs = cfg["small_runs"] if r == 5000 else cfg["mid_runs"]
            rng = stream(args.seed, "replications", 10 + 10 * j + k)
            est = [simulate(draw, mu, n, r, rng)["two_sided"]["p"] for _ in range(runs)]
            est = np.array(est)
            sd_formula = math.sqrt(truth["p"] * (1 - truth["p"]) / r)
            rec["published"][year] = {"value": value, "R": r, "mcse_at_R": sd_formula,
                                      "z_from_truth": (value - truth["p"]) / sd_formula}
            rec["small_runs"][str(r)] = {"runs": runs, "sd": float(est.std(ddof=1)), "sd_formula": sd_formula,
                                         "min": float(est.min()), "max": float(est.max()),
                                         "q05": float(np.quantile(est, 0.05)), "q95": float(np.quantile(est, 0.95)),
                                         "estimates": est.round(5).tolist()}
        out[f"lognormal_n{n}"] = rec
    print("replications: R needed for a target MCSE, R = p(1 - p) / MCSE^2:")
    for p, row in out["R_for_target"].items():
        print(f"  p = {p}: " + ", ".join(f"MCSE {t}: {v:,}" for t, v in row.items()))
    for n in (30, 100):
        rec = out[f"lognormal_n{n}"]
        print(f"  standard lognormal, n = {n}, two-sided 5% t-test: {fmt_share(rec['truth'])} (R = {rec['truth']['R']:,})")
        for year, v in rec["published"].items():
            sr = rec["small_runs"][str(v["R"])]
            print(f"    published {year}: {v['value']} at R = {v['R']:,}, whose MCSE is {v['mcse_at_R']:.4f}: "
                  f"{v['z_from_truth']:+.1f} MCSE from ours; {sr['runs']} reruns at that R spread over "
                  f"{sr['min']:.4f}-{sr['max']:.4f} (SD {sr['sd']:.4f})")
    return out


# --------------------------------------------------------------------------------------- driver
def provenance(args, budget):
    source = pathlib.Path(__file__).read_bytes()
    cpu = platform.processor() or platform.machine()
    try:
        for line in pathlib.Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return {"captured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "os": f"{platform.system()} {platform.release()} {platform.machine()}", "cpu": cpu,
            "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "sampling_py_sha1": hashlib.sha1(source).hexdigest()[:12],
            "spend_csv_sha1": hashlib.sha1(SPEND_CSV.read_bytes()).hexdigest()[:12],
            "budget": budget, "seed": args.seed, "replications": QUICK if args.quick else FULL,
            "flags": {"cap": args.cap, "fault": args.fault}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261026)
    parser.add_argument("--cap", type=float, default=None, help="E3: cap spend at this quantile, e.g. 0.99")
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the sampling helper")
    args = parser.parse_args()
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, "
          f"NumPy {prov['numpy']}, SciPy {prov['scipy']}; sampling.py {prov['sampling_py_sha1']}; "
          f"budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    funcs = {"population": stage_population, "sampling": stage_sampling, "skewness": stage_skewness,
             "student": stage_student, "berry": stage_berry, "heavy": stage_heavy,
             "replications": stage_replications}
    for name in STAGES if args.stage == "all" else (args.stage,):
        t0 = time.perf_counter()
        print()
        captures[name] = funcs[name](cfg, args)
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items()))


if __name__ == "__main__":
    main()
