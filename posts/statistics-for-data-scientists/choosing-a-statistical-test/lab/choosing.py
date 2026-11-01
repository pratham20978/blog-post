#!/usr/bin/env python3
"""Lab for "Which Statistical Test? The Design Decides, Not the Data" (Statistics for Data Scientists, part 8).

Every number the article calls measured or computed comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python choosing.py all --out mine.json            # every stage, the article's budget (about 2 minutes)
    python choosing.py all --quick --out quick.json   # the reader's budget (about 20 seconds), noisier
    python choosing.py example --out mine.json        # one stage

Stages:
    example    the worked example: Student's ten patients (R's sleep data), each given both drugs; the paired t-test
               the design calls for beside the two unpaired tests the two-column layout invites, every intermediate
               printed and matched to SciPy and statsmodels
    twosample  Student's pooled t-test against Welch's: exact type I error and power for normal data, by quadrature
               over the two sample variances, across standard-deviation ratios and group sizes; checked by
               simulation and against scipy.stats.ttest_ind
    pretest    the two-stage habit simulated as one procedure: a Levene (Brown-Forsythe) test of equal variances,
               and a Shapiro-Wilk test of normality, deciding which test to run; its overall and conditional
               error rates against always using Welch
    tables     2x2 tables: Fisher's tea-tasting design, where both margins are fixed; Hellman's malocclusion
               table, analysed by eight tests; the exact size and power of each test when the table comes from
               two independent binomial samples, summed over every possible table; matched to SciPy
    anova      one-way ANOVA on R's PlantGrowth data by hand, the F ratio and Welch's ANOVA beside it, matched to
               SciPy and statsmodels; the F test's type I error with unequal variances, by simulation

Every simulated quantity is printed as estimate +- MCSE (its Monte Carlo standard error) with its number of
replications R. Exact quantities (sums over a finite outcome space, or quadrature to 1e-12) carry no MCSE. Every
stage draws from its own stream, SeedSequence([stage, sub-stream, seed]), so stages can run alone and repeat to
the bit with the same NumPy version.
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
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import scipy
from scipy import optimize, special, stats

HERE = pathlib.Path(__file__).resolve().parent
SLEEP_CSV = HERE / "data" / "student1908_sleep.csv"
PLANT_CSV = HERE / "data" / "plant_growth.csv"
STAGES = ("example", "twosample", "pretest", "tables", "anova")

# Replications. The article quotes FULL; --quick is the reader's first run. Exact computations ignore the budget.
FULL = dict(sim_check=200_000, pretest=100_000, table_check=200_000, anova=100_000)
QUICK = {k: v // 10 for k, v in FULL.items()}
CHUNK = 20_000                                  # replications per block, fixed so results do not depend on the machine
ALPHA = 0.05

# The two-sample designs: (n1, n2) and the ratio grid of sigma1 / sigma2, group 1 being the first size.
DESIGNS = ((10, 40), (25, 25))
PRETEST_DESIGN = (10, 40)
PRETEST_RATIOS = (0.25, 1 / 3, 0.5, 2 / 3, 1.0, 1.5, 2.0, 3.0, 4.0)
RATIOS = tuple(sorted({round(2 ** (k / 4), 12) for k in range(-8, 9)} | {round(r, 12) for r in PRETEST_RATIOS}))  # 1/4 to 4
CHECK_RATIOS = {(10, 40): (0.25, 0.5, 1.0, 2.0, 4.0), (25, 25): (1.0, 4.0)}
QUAD_NODES = 160

# 2x2 tables. Hellman's counts of normal teeth and malocclusion, as Yates (1934) printed them: rows breast-fed and
# bottle-fed infants, columns normal teeth and malocclusion. M. Hellman, Dental Cosmos 56: 1017-1032, 1914.
MALOCCLUSION = ((4, 16), (1, 21))
TEA_CUPS, TEA_MILK_FIRST = 8, 4                 # Fisher's design: eight cups, four of each, and the lady is told so
POWER_ALT = (0.20, 0.05)                        # an alternative for the power comparison: 20% against 5% normal teeth
PI_GRID = np.round(np.arange(0.0025, 1.0, 0.0025), 4)

# ANOVA simulation designs: k = 3 normal groups with equal means.
ANOVA_DESIGNS = {"negative pairing": ((10, 20, 30), (3.0, 2.0, 1.0)),
                 "positive pairing": ((10, 20, 30), (1.0, 2.0, 3.0)),
                 "equal sizes": ((20, 20, 20), (1.0, 2.0, 3.0)),
                 "equal variances": ((10, 20, 30), (1.0, 1.0, 1.0))}

TESTS_2X2 = ("pearson", "yates", "n_minus_1", "fisher", "fisher_doubled", "mid_p", "boschloo", "barnard")
NAMES = {"pearson": "Pearson chi-squared", "yates": "Yates-corrected chi-squared", "n_minus_1": "'N - 1' chi-squared",
         "fisher": "Fisher's exact (Irwin's rule)", "fisher_doubled": "Fisher's exact, doubled one-sided",
         "mid_p": "Fisher's mid-p", "boschloo": "Boschloo's unconditional", "barnard": "Barnard's unconditional"}


# ------------------------------------------------------------------------------- small helpers
def stream(seed, stage, sub=0):
    """An independent generator for (stage, sub-stream): varying ids first, the root seed last."""
    return np.random.default_rng(np.random.SeedSequence([STAGES.index(stage), sub, seed]))


def mcse_share(p, reps):
    return math.sqrt(max(p * (1 - p), 0.0) / reps)


def r6(x):
    """Round for the capture file: floats to six significant digits, recursively."""
    if isinstance(x, dict):
        return {str(k): r6(v) for k, v in x.items()}
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


def scalar(v):
    """The one value of a size-1 array or a number, as a float (NumPy 2.5 refuses float() on a 1-element array)."""
    return float(np.asarray(v).reshape(-1)[0])


def pc(share, nd=1):
    """A share as a percentage, rounded half up from its decimal value. Shares are counts over R, so exact ties occur,
    and float formatting would round some of them down and others up."""
    return str((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def pm(est, mcse, nd=1):
    """'5.1% +- 0.1' for a share."""
    return f"{pc(est, nd)}% +- {pc(mcse, nd)}"


def key(r):
    """A ratio as a capture key: '0.25', '0.5946', '1', '4'."""
    return f"{r:.4g}"


def read_sleep():
    with SLEEP_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    patient = np.array([int(r["patient"]) for r in rows])
    return patient, np.array([float(r["drug_1"]) for r in rows]), np.array([float(r["drug_2"]) for r in rows])


def read_plants():
    with PLANT_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    groups = {}
    for r in rows:
        groups.setdefault(r["group"], []).append(float(r["weight"]))
    return {g: np.array(v) for g, v in groups.items()}


# ------------------------------------------------------------------------------- two-sample t statistics
def t_tests(x, y):
    """Student's pooled and Welch's t-tests along the last axis: (t_student, df_student, p_student, t_welch, df_welch,
    p_welch). x and y may hold many samples, one per row."""
    n1, n2 = x.shape[-1], y.shape[-1]
    m1, m2 = x.mean(-1), y.mean(-1)
    v1, v2 = x.var(-1, ddof=1), y.var(-1, ddof=1)
    sp2 = ((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2)
    ts = (m1 - m2) / np.sqrt(sp2 * (1 / n1 + 1 / n2))
    dfs = n1 + n2 - 2
    ps = 2 * stats.t.sf(np.abs(ts), dfs)
    a, b = v1 / n1, v2 / n2
    tw = (m1 - m2) / np.sqrt(a + b)
    dfw = (a + b) ** 2 / (a**2 / (n1 - 1) + b**2 / (n2 - 1))
    pw = 2 * stats.t.sf(np.abs(tw), dfw)
    return ts, dfs, ps, tw, dfw, pw


def levene_median(x, y):
    """Levene's test centred at the group medians (Brown and Forsythe 1974), SciPy's default: a one-way ANOVA F on
    |x - median| for two groups, along the last axis. Returns the p-value."""
    zx = np.abs(x - np.median(x, -1, keepdims=True))
    zy = np.abs(y - np.median(y, -1, keepdims=True))
    n1, n2 = x.shape[-1], y.shape[-1]
    mx, my = zx.mean(-1), zy.mean(-1)
    m = (n1 * mx + n2 * my) / (n1 + n2)
    between = n1 * (mx - m) ** 2 + n2 * (my - m) ** 2
    within = ((zx - mx[..., None]) ** 2).sum(-1) + ((zy - my[..., None]) ** 2).sum(-1)
    f = between / (within / (n1 + n2 - 2))
    return stats.f.sf(f, 1, n1 + n2 - 2)


# ------------------------------------------------------------------------------- example
def stage_example(cfg, args):
    patient, x, y = read_sleep()
    n = len(x)
    if args.fault:
        # An earlier draft: it reshaped the table to long form and sorted it by hours to print it neatly, then paired
        # the i-th row of drug 1 with the i-th row of drug 2.
        long = sorted([(v, 1, p) for p, v in zip(patient, x)] + [(v, 2, p) for p, v in zip(patient, y)])
        d1 = [(v, p) for v, g, p in long if g == 1]
        d2 = [(v, p) for v, g, p in long if g == 2]
        x = np.array([v for v, _ in d1])
        y = np.array([v for v, _ in d2])
        pid1, pid2 = [p for _, p in d1], [p for _, p in d2]
    else:
        pid1 = pid2 = [int(p) for p in patient]
    d = y - x
    print(f"example: Student's ten patients (R's sleep), extra hours of sleep on drug 1 and drug 2"
          + ("  [--fault: the draft that pairs rows by position]" if args.fault else ""))
    print("  pairs (patient on drug 1, patient on drug 2): " + ", ".join(f"({a}, {b})" for a, b in zip(pid1, pid2)))
    m1, m2, md = x.mean(), y.mean(), d.mean()
    s1, s2, sd = x.std(ddof=1), y.std(ddof=1), d.std(ddof=1)
    r = float(np.corrcoef(x, y)[0, 1])
    cov = float(np.cov(x, y, ddof=1)[0, 1])
    print(f"  means {m1:.2f} and {m2:.2f}; mean difference {md:.2f}; SDs (divisor n - 1) {s1:.4f}, {s2:.4f}, "
          f"differences {sd:.4f}; correlation between the drugs {r:.4f}")
    print(f"  Var(d) = Var(1) + Var(2) - 2 Cov = {s1**2:.4f} + {s2**2:.4f} - 2 x {cov:.4f} = {sd**2:.4f}")
    se_p = sd / math.sqrt(n)
    t_p = md / se_p
    p_p = 2 * stats.t.sf(abs(t_p), n - 1)
    q = stats.t.isf(0.025, n - 1)
    ci_p = (md - q * se_p, md + q * se_p)
    ts, dfs, ps, tw, dfw, pw = (scalar(v) for v in t_tests(y[None, :], x[None, :]))
    sp2 = (s1**2 + s2**2) / 2
    se_u = math.sqrt(sp2 * 2 / n)
    qs, qw = stats.t.isf(0.025, dfs), stats.t.isf(0.025, dfw)
    ci_s, ci_w = (md - qs * se_u, md + qs * se_u), (md - qw * se_u, md + qw * se_u)
    print(f"  paired: SE {se_p:.4f}, t = {t_p:.4f} on {n - 1} df, p = {p_p:.6f}, 95% CI {ci_p[0]:.4f} to {ci_p[1]:.4f}")
    print(f"  Student unpaired: pooled variance {sp2:.4f}, SE {se_u:.4f}, t = {ts:.4f} on {dfs:g} df, p = {ps:.6f}, "
          f"95% CI {ci_s[0]:.4f} to {ci_s[1]:.4f}")
    print(f"  Welch unpaired: SE {se_u:.4f}, t = {tw:.4f} on {dfw:.3f} df, p = {pw:.6f}, 95% CI {ci_w[0]:.4f} to {ci_w[1]:.4f}")
    ratio = se_u / se_p
    n_equiv = n * (s1**2 + s2**2) / sd**2
    print(f"  the unpaired SE is {ratio:.3f} times the paired one; a parallel-group trial would need {n_equiv:.1f} "
          f"patients per arm for the paired SE (from these sample variances)")
    sd_n = d.std(ddof=0)
    z_student = md / sd_n
    print(f"  Student's 1908 scale (divisor n): SDs {x.std(ddof=0):.2f}, {y.std(ddof=0):.2f}, {sd_n:.2f}; z = {z_student:.3f}; "
          f"t = z sqrt(n - 1) = {z_student * math.sqrt(n - 1):.4f}; one-sided P = {stats.t.sf(t_p, n - 1):.6f}")
    # reconcile with the libraries, both orders of arguments and both defaults
    import statsmodels.stats.weightstats as smws
    lib = {"scipy_ttest_rel": float(stats.ttest_rel(y, x).pvalue),
           "scipy_ttest_ind_default": float(stats.ttest_ind(y, x).pvalue),
           "scipy_ttest_ind_welch": float(stats.ttest_ind(y, x, equal_var=False).pvalue),
           "statsmodels_ttest_ind_default": float(smws.ttest_ind(y, x)[1]),
           "statsmodels_ttest_ind_unequal": float(smws.ttest_ind(y, x, usevar="unequal")[1])}
    diffs = [abs(lib["scipy_ttest_rel"] - p_p), abs(lib["scipy_ttest_ind_default"] - ps), abs(lib["scipy_ttest_ind_welch"] - pw),
             abs(lib["statsmodels_ttest_ind_default"] - ps), abs(lib["statsmodels_ttest_ind_unequal"] - pw)]
    print(f"  SciPy ttest_rel p = {lib['scipy_ttest_rel']:.6f}; ttest_ind default (equal_var=True, Student) p = "
          f"{lib['scipy_ttest_ind_default']:.6f}; equal_var=False p = {lib['scipy_ttest_ind_welch']:.6f}")
    print(f"  statsmodels ttest_ind default (usevar='pooled') p = {lib['statsmodels_ttest_ind_default']:.6f}; "
          f"usevar='unequal' p = {lib['statsmodels_ttest_ind_unequal']:.6f}; largest difference from the hand values "
          f"{max(diffs):.1e}")
    return dict(n=n, patient=[int(p) for p in patient], pairs=[[a, b] for a, b in zip(pid1, pid2)], x=x, y=y, d=d,
                means=[m1, m2, md], sd=[s1, s2, sd], sd_divisor_n=[x.std(ddof=0), y.std(ddof=0), sd_n], r=r, cov=cov,
                var_identity=[s1**2, s2**2, 2 * cov, sd**2],
                paired=dict(se=se_p, t=t_p, df=n - 1, p=p_p, ci=ci_p, p_one_sided=float(stats.t.sf(t_p, n - 1))),
                student=dict(pooled_var=sp2, se=se_u, t=ts, df=dfs, p=ps, ci=ci_s),
                welch=dict(se=se_u, t=tw, df=dfw, p=pw, ci=ci_w),
                se_ratio=ratio, n_equivalent_per_arm=n_equiv, student_z=z_student, library=lib,
                max_abs_diff=max(diffs), fault=bool(args.fault))


# ------------------------------------------------------------------------------- twosample
def chi2_nodes(df, m=QUAD_NODES):
    """Generalised Gauss-Laguerre nodes and probability weights for a chi-squared variable with df degrees of freedom."""
    a = df / 2 - 1
    x, w = special.roots_genlaguerre(m, a)
    return 2 * x, w / math.exp(special.gammaln(a + 1))


def exact_reject(n1, n2, s1, s2, delta=0.0, alpha=ALPHA, m=QUAD_NODES):
    """P(reject) of Student's and Welch's two-sided tests for normal samples with SDs s1 and s2 and true mean
    difference delta. Given the two sample variances, the mean difference is normal and independent of them, so the
    rejection probability is a normal tail; the expectation over the two chi-squared variances is a quadrature."""
    u1, w1 = chi2_nodes(n1 - 1, m)
    u2, w2 = chi2_nodes(n2 - 1, m)
    U1, U2 = np.meshgrid(u1, u2, indexing="ij")
    W = np.outer(w1, w2)
    tau = math.sqrt(s1**2 / n1 + s2**2 / n2)                       # SD of the observed mean difference
    se_s = np.sqrt((s1**2 * U1 + s2**2 * U2) / (n1 + n2 - 2) * (1 / n1 + 1 / n2))
    c_s = stats.t.isf(alpha / 2, n1 + n2 - 2)
    a, b = s1**2 * U1 / (n1 - 1) / n1, s2**2 * U2 / (n2 - 1) / n2
    se_w = np.sqrt(a + b)
    c_w = stats.t.isf(alpha / 2, (a + b) ** 2 / (a**2 / (n1 - 1) + b**2 / (n2 - 1)))
    out = []
    for se, c in ((se_s, c_s), (se_w, c_w)):
        p = stats.norm.cdf((delta - c * se) / tau) + stats.norm.cdf((-delta - c * se) / tau)
        out.append(float((W * p).sum()))
    return out


def simulate_rates(n1, n2, s1, s2, reps, rng, delta=0.0):
    """Simulated rejection rates of Student's and Welch's tests at ALPHA, drawn in fixed blocks."""
    hits = np.zeros(2)
    done = 0
    while done < reps:
        k = min(CHUNK, reps - done)
        x = rng.normal(delta, s1, (k, n1))
        y = rng.normal(0.0, s2, (k, n2))
        _, _, ps, _, _, pw = t_tests(x, y)
        hits += [(ps <= ALPHA).sum(), (pw <= ALPHA).sum()]
        done += k
    return hits / reps


def stage_twosample(cfg, args):
    print("twosample: Student's pooled t-test against Welch's, normal data, alpha = 0.05 two-sided")
    out = {"alpha": ALPHA, "ratios": list(RATIOS), "designs": {}}
    designs = DESIGNS if args.n1 is None else ((args.n1, args.n2),)
    for n1, n2 in designs:
        dkey = f"{n1},{n2}"
        rows = {}
        for r in (RATIOS if args.ratio is None else (args.ratio,)):
            es, ew = exact_reject(n1, n2, r, 1.0)
            rows[key(r)] = dict(student=es, welch=ew)
        conv = max(abs(a - b) for a, b in zip(exact_reject(n1, n2, 4.0, 1.0), exact_reject(n1, n2, 4.0, 1.0, m=2 * QUAD_NODES)))
        print(f"  n1 = {n1}, n2 = {n2} (sigma1/sigma2: exact Student, exact Welch; quadrature converged to {conv:.0e})")
        shown = (RATIOS if args.ratio is None else (args.ratio,))
        for i in range(0, len(shown), 4):
            print("    " + "; ".join(f"{r:.3f}: Student {pc(rows[key(r)]['student'], 2)}%, Welch {pc(rows[key(r)]['welch'], 2)}%"
                                   for r in shown[i:i + 4]))
        checks = {}
        for j, r in enumerate(CHECK_RATIOS.get((n1, n2), ()) if args.ratio is None else (args.ratio,)):
            rng = stream(args.seed, "twosample", 10 * DESIGNS.index((n1, n2)) + j if (n1, n2) in DESIGNS else 90 + j)
            sim = simulate_rates(n1, n2, r, 1.0, cfg["sim_check"], rng)
            ex = rows[key(r)]
            z = [(sim[i] - ex[t]) / mcse_share(ex[t], cfg["sim_check"]) for i, t in enumerate(("student", "welch"))]
            checks[key(r)] = dict(student=sim[0], welch=sim[1], R=cfg["sim_check"],
                                  mcse=[mcse_share(sim[0], cfg["sim_check"]), mcse_share(sim[1], cfg["sim_check"])], z=z)
            print(f"    simulated at {r:g} (R = {cfg['sim_check']:,}): Student {pm(sim[0], checks[key(r)]['mcse'][0], 2)}, "
                  f"Welch {pm(sim[1], checks[key(r)]['mcse'][1], 2)} (z against exact {z[0]:+.1f}, {z[1]:+.1f})")
        out["designs"][dkey] = dict(n1=n1, n2=n2, exact=rows, simulated=checks, quad_convergence=conv)
    if args.n1 is not None:                               # a reader's own design: no power, no reconciliation
        return out
    # reconcile the vectorised t-tests with SciPy on 2,000 simulated pairs of samples at the most extreme ratio
    rng = stream(args.seed, "twosample", 50)
    x, y = rng.normal(0, 4.0, (2000, 10)), rng.normal(0, 1.0, (2000, 40))
    _, _, ps, _, _, pw = t_tests(x, y)
    diff = max(float(np.max(np.abs(ps - stats.ttest_ind(x, y, axis=1).pvalue))),
               float(np.max(np.abs(pw - stats.ttest_ind(x, y, axis=1, equal_var=False).pvalue))))
    print(f"  the lab's t-tests against scipy.stats.ttest_ind on 2,000 pairs of samples: largest p difference {diff:.1e}")
    out["scipy_max_abs_diff"] = diff
    # the price of Welch: exact power with equal variances, and with unequal ones
    power = {}
    deltas = [round(0.05 * k, 2) for k in range(0, 41)]
    for n1, n2 in DESIGNS:
        for r in (1.0, 2.0, 0.5):
            cur = [exact_reject(n1, n2, r, 1.0, delta=dl) for dl in deltas]
            power[f"{n1},{n2},{key(r)}"] = dict(delta=deltas, student=[c[0] for c in cur], welch=[c[1] for c in cur])
    # the mean difference at which Student's test has 80% power with equal SDs, and Welch's power there
    at80 = {}
    for n1, n2 in DESIGNS:
        d80 = optimize.brentq(lambda dl: exact_reject(n1, n2, 1.0, 1.0, delta=dl)[0] - 0.8, 0.2, 3.0, xtol=1e-10)
        ps80, pw80 = exact_reject(n1, n2, 1.0, 1.0, delta=d80)
        gap = max(p["student"][i] - p["welch"][i] for p in (power[f"{n1},{n2},1"],) for i in range(len(deltas)))
        at80[f"{n1},{n2}"] = dict(delta=d80, student=ps80, welch=pw80, max_gap=gap)
        print(f"  equal SDs, n1 = {n1}, n2 = {n2}: at a difference of {d80:.3f} SD Student's power is {pc(ps80, 1)}% and "
              f"Welch's {pc(pw80, 1)}%; the largest gap over 0 to 2 SD is {100 * gap:.2f} points")
    for n1, n2 in DESIGNS[:1]:
        for r in (2.0, 0.5):
            p = power[f"{n1},{n2},{key(r)}"]
            i = deltas.index(1.0)
            print(f"  SD ratio {r:g}, n1 = {n1}, n2 = {n2}, difference 1 SD of group 2: Student {pc(p['student'][i], 1)}%, "
                  f"Welch {pc(p['welch'][i], 1)}%")
    out["power"] = power
    out["power_at_80"] = at80
    return out


# ------------------------------------------------------------------------------- pretest
def stage_pretest(cfg, args):
    n1, n2 = PRETEST_DESIGN
    reps = cfg["pretest"]
    print(f"pretest: n1 = {n1}, n2 = {n2}, normal data, equal means; R = {reps:,} per ratio; pre-tests at alpha 0.05")
    out = {"n1": n1, "n2": n2, "R": reps, "alpha_pre": 0.05, "by_ratio": {}}
    for j, r in enumerate(PRETEST_RATIOS):
        rng = stream(args.seed, "pretest", j)
        acc = dict(student=0, welch=0, levene_rule=0, habit=0, lev_reject=0, sw_reject=0, student_given_accept=0,
                   welch_given_reject=0, mw_given_sw=0, n_accept=0, n_reject=0, n_sw=0)
        done = 0
        while done < reps:
            k = min(CHUNK, reps - done)
            x = rng.normal(0.0, r, (k, n1))
            y = rng.normal(0.0, 1.0, (k, n2))
            _, _, ps, _, _, pw = t_tests(x, y)
            rs, rw = ps <= ALPHA, pw <= ALPHA
            lev = levene_median(x, y) <= 0.05
            sw = (stats.shapiro(x, axis=1).pvalue <= 0.05) | (stats.shapiro(y, axis=1).pvalue <= 0.05)
            mw = stats.mannwhitneyu(x, y, axis=1, method="asymptotic").pvalue <= ALPHA
            rule = np.where(lev, rw, rs)                       # Levene decides: Welch if it rejects, else Student
            habit = np.where(sw, mw, rule)                     # Shapiro-Wilk first: Mann-Whitney if either group fails
            acc["student"] += rs.sum(); acc["welch"] += rw.sum(); acc["levene_rule"] += rule.sum()
            acc["habit"] += habit.sum(); acc["lev_reject"] += lev.sum(); acc["sw_reject"] += sw.sum()
            acc["student_given_accept"] += (rs & ~lev).sum(); acc["n_accept"] += (~lev).sum()
            acc["welch_given_reject"] += (rw & lev).sum(); acc["n_reject"] += lev.sum()
            acc["mw_given_sw"] += (mw & sw).sum(); acc["n_sw"] += sw.sum()
            done += k
        row = {}
        for name in ("student", "welch", "levene_rule", "habit", "lev_reject", "sw_reject"):
            p = acc[name] / reps
            row[name] = dict(rate=p, mcse=mcse_share(p, reps))
        for name, den in (("student_given_accept", "n_accept"), ("welch_given_reject", "n_reject"), ("mw_given_sw", "n_sw")):
            p = acc[name] / max(acc[den], 1)
            row[name] = dict(rate=p, mcse=mcse_share(p, max(acc[den], 1)), n=int(acc[den]))
        es, ew = exact_reject(n1, n2, r, 1.0)
        row["exact"] = dict(student=es, welch=ew)
        out["by_ratio"][key(r)] = row
        print(f"  SD ratio {r:5.3f}: Student {pm(row['student']['rate'], row['student']['mcse'], 2)}, Welch "
              f"{pm(row['welch']['rate'], row['welch']['mcse'], 2)}, Levene decides {pm(row['levene_rule']['rate'], row['levene_rule']['mcse'], 2)}, "
              f"the full habit {pm(row['habit']['rate'], row['habit']['mcse'], 2)}; Levene rejects "
              f"{pc(row['lev_reject']['rate'], 1)}%; Student when Levene accepts {pc(row['student_given_accept']['rate'], 2)}%, "
              f"Welch when it rejects {pc(row['welch_given_reject']['rate'], 2)}%")
    # SciPy's levene against the lab's, on 2,000 pairs of samples
    rng = stream(args.seed, "pretest", 50)
    x, y = rng.normal(0, 2.0, (2000, n1)), rng.normal(0, 1.0, (2000, n2))
    diff = float(np.max(np.abs(levene_median(x, y) - stats.levene(x, y, axis=1).pvalue)))
    print(f"  the lab's Levene test against scipy.stats.levene (center='median') on 2,000 pairs: largest p difference {diff:.1e}")
    out["scipy_levene_max_abs_diff"] = diff
    return out


# ------------------------------------------------------------------------------- tables
def table_space(m, n):
    """Every 2x2 table with row totals m and n: a 'successes' in row 1, b in row 2."""
    a, b = np.meshgrid(np.arange(m + 1), np.arange(n + 1), indexing="ij")
    return a.ravel(), b.ravel()


def chi2_family(a, b, m, n):
    """Pearson, Yates-corrected and 'N - 1' chi-squared p-values; a table with an empty column gets p = 1."""
    N = m + n
    s = a + b
    f = N - s
    num = (a * (n - b) - b * (m - a)).astype(float)
    den = (m * n * s * f).astype(float)
    ok = den > 0
    with np.errstate(divide="ignore", invalid="ignore"):
        x2 = np.where(ok, N * num**2 / den, 0.0)
        x2y = np.where(ok, N * np.maximum(np.abs(num) - N / 2, 0.0) ** 2 / den, 0.0)
    out = {"pearson": stats.chi2.sf(x2, 1), "yates": stats.chi2.sf(x2y, 1), "n_minus_1": stats.chi2.sf(x2 * (N - 1) / N, 1)}
    for k in out:
        out[k] = np.where(ok, out[k], 1.0)
    return out, x2, x2y


def fisher_family(a, b, m, n, rel=1e-7):
    """Fisher's exact test conditional on both margins: two-sided by Irwin's rule (every table no likelier than the
    observed one, as SciPy and R do), doubled one-sided, the mid-p version of Irwin's rule (half the probability of
    the tables exactly as likely as the observed one), and the two one-sided p-values Boschloo's test uses."""
    N = m + n
    out = {k: np.ones(len(a)) for k in ("fisher", "fisher_doubled", "mid_p", "less", "greater")}
    for i, (ai, bi) in enumerate(zip(a, b)):
        s = ai + bi
        lo, hi = max(0, s - n), min(m, s)
        xs = np.arange(lo, hi + 1)
        pmf = stats.hypergeom.pmf(xs, N, m, s)
        p0 = pmf[ai - lo]
        tied = np.abs(pmf - p0) <= p0 * rel
        less_likely = pmf < p0 * (1 - rel)
        out["fisher"][i] = min(1.0, pmf[less_likely | tied].sum())
        out["mid_p"][i] = min(1.0, pmf[less_likely].sum() + 0.5 * pmf[tied].sum())
        pl, pg = pmf[xs <= ai].sum(), pmf[xs >= ai].sum()
        out["less"][i], out["greater"][i] = min(1.0, pl), min(1.0, pg)
        out["fisher_doubled"][i] = min(1.0, 2 * min(pl, pg))
    return out


def binom_weights(a, b, m, n, pis):
    """P(table) under two independent binomials with a common success probability, one column per value of pi."""
    pis = np.asarray(pis, dtype=float)
    return stats.binom.pmf(a[:, None], m, pis[None, :]) * stats.binom.pmf(b[:, None], n, pis[None, :])


def unconditional(stat_extreme, a, b, m, n, grid, refine=True):
    """Unconditional p-values: for each table, the largest probability over the common pi of the set of tables at
    least as extreme (stat_extreme[i, j] is True when table j is at least as extreme as table i)."""
    W = binom_weights(a, b, m, n, grid)
    probs = stat_extreme.astype(float) @ W                    # tables x grid
    j = probs.argmax(1)
    p = probs[np.arange(len(a)), j]
    if refine:
        for i in range(len(a)):
            lo, hi = grid[max(j[i] - 1, 0)], grid[min(j[i] + 1, len(grid) - 1)]
            mask = stat_extreme[i]
            fn = lambda q: -float(binom_weights(a[mask], b[mask], m, n, [q]).sum())   # noqa: E731
            res = optimize.minimize_scalar(fn, bounds=(lo, hi), method="bounded", options={"xatol": 1e-10})
            p[i] = max(p[i], -res.fun)
    return np.minimum(p, 1.0)


def all_2x2_pvalues(m, n, grid):
    a, b = table_space(m, n)
    chi, x2, _ = chi2_family(a, b, m, n)
    fis = fisher_family(a, b, m, n)
    pv = dict(chi)
    pv.update({k: fis[k] for k in ("fisher", "fisher_doubled", "mid_p")})
    # Boschloo: Fisher's one-sided p-value is the statistic; two-sided = twice the smaller one-sided p (SciPy's rule)
    ext_less = fis["less"][None, :] <= fis["less"][:, None] * (1 + 1e-12)
    ext_greater = fis["greater"][None, :] <= fis["greater"][:, None] * (1 + 1e-12)
    pv["boschloo"] = np.minimum(1.0, 2 * np.minimum(unconditional(ext_less, a, b, m, n, grid),
                                                    unconditional(ext_greater, a, b, m, n, grid)))
    # Barnard: the pooled Wald (score) statistic; two-sided, tables with |Z| at least the observed one
    N = m + n
    ph = (a + b) / N
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where((ph > 0) & (ph < 1), (a / m - b / n) / np.sqrt(ph * (1 - ph) * (1 / m + 1 / n)), 0.0)
    ext_z = np.abs(z)[None, :] >= np.abs(z)[:, None] * (1 - 1e-12)
    pv["barnard"] = unconditional(ext_z, a, b, m, n, grid)
    pv["barnard"] = np.where(np.abs(z) > 0, pv["barnard"], 1.0)
    return a, b, pv, x2


def size_study(a, b, m, n, pv, grid):
    """The exact size of each 5% test when the table comes from two independent binomials (row totals m and n) with
    a common success probability pi, as a function of pi, and its largest value; and power at POWER_ALT both ways."""
    W = binom_weights(a, b, m, n, grid)
    out, region = {}, {}
    for t in TESTS_2X2:
        rej = pv[t] <= ALPHA + 1e-12
        region[t] = rej
        curve = rej.astype(float) @ W
        j = int(curve.argmax())
        lo, hi = grid[max(j - 1, 0)], grid[min(j + 1, len(grid) - 1)]
        res = optimize.minimize_scalar(lambda q: -float(binom_weights(a[rej], b[rej], m, n, [q]).sum()),
                                       bounds=(lo, hi), method="bounded", options={"xatol": 1e-10})
        mx, arg = (-res.fun, float(res.x)) if -res.fun > curve[j] else (float(curve[j]), float(grid[j]))
        pw = float((rej * stats.binom.pmf(a, m, POWER_ALT[0]) * stats.binom.pmf(b, n, POWER_ALT[1])).sum())
        pw_rev = float((rej * stats.binom.pmf(a, m, POWER_ALT[1]) * stats.binom.pmf(b, n, POWER_ALT[0])).sum())
        at = {f"{q:g}": float(curve[np.argmin(np.abs(grid - q))]) for q in (0.05, 0.1, 0.12, 0.2, 0.3, 0.5)}
        out[t] = dict(max=mx, argmax=min(arg, 1 - arg), n_rejected=int(rej.sum()), at=at, power=pw, power_reversed=pw_rev,
                      curve=[float(curve[np.argmin(np.abs(grid - q))]) for q in PI_GRID])
    return out, region


def exact_z2(a, b, m, n):
    """Barnard's pooled statistic squared, as an exact fraction (0 for a table with an empty column)."""
    from fractions import Fraction as Fr
    if a + b in (0, m + n):
        return Fr(0)
    p = Fr(a + b, m + n)
    return (Fr(a, m) - Fr(b, n)) ** 2 / (p * (1 - p) * (Fr(1, m) + Fr(1, n)))


def stage_tables(cfg, args):
    print("tables: 2x2 tables")
    # Fisher's tea-tasting design: the hypergeometric distribution of the number of milk-first cups picked correctly
    k = range(TEA_MILK_FIRST + 1)
    ways = [math.comb(TEA_MILK_FIRST, i) * math.comb(TEA_CUPS - TEA_MILK_FIRST, TEA_MILK_FIRST - i) for i in k]
    total = math.comb(TEA_CUPS, TEA_MILK_FIRST)
    tail = [sum(ways[i:]) for i in k]
    print(f"  tea: {TEA_CUPS} cups, {TEA_MILK_FIRST} milk first; ways to pick 0..4 of them correctly {ways} of {total}")
    print(f"  P(4 correct) = 1/{total} = {1 / total:.6f}; P(3 or more) = {tail[3]}/{total} = {tail[3] / total:.6f}; "
          f"the 5% test rejects only at 4 correct, so its size is {1 / total:.6f}")
    told_not = [[3, 1], [0, 4]]
    p_not_told = float(stats.fisher_exact(told_not, alternative="greater").pvalue)
    print(f"  not told the split, one cup doubtful: the table {told_not} has one-sided P = {p_not_told:.6f} "
          f"(= 4/56), and no table with one doubt reaches 1/70")
    tea = dict(cups=TEA_CUPS, milk_first=TEA_MILK_FIRST, ways=ways, total=total, tail_counts=tail,
               p_all=1 / total, p_three=tail[3] / total, mid_p_all=0.5 / total, mid_p_three=(tail[4] + 0.5 * ways[3]) / total,
               scipy_p_all=float(stats.fisher_exact([[4, 0], [0, 4]], alternative="greater").pvalue),
               p_not_told_one_doubt=p_not_told)
    # Hellman's malocclusion table, eight ways
    (a0, c0), (b0, d0) = MALOCCLUSION
    m, n = a0 + c0, b0 + d0
    N = m + n
    tab = np.array(MALOCCLUSION)
    expected = np.outer(tab.sum(1), tab.sum(0)) / N
    grid = np.unique(np.concatenate([PI_GRID, np.linspace(0.0005, 0.9995, 2000)]))
    t0 = time.perf_counter()
    a, b, pv, x2 = all_2x2_pvalues(m, n, grid)
    obs = int(np.flatnonzero((a == a0) & (b == b0))[0])
    print(f"  malocclusion (Hellman, via Yates 1934): breast-fed {a0} normal of {m}, bottle-fed {b0} of {n}; expected "
          f"counts {', '.join(f'{v:.3f}' for v in expected.ravel())}; smallest {expected.min():.3f}")
    print(f"  chi-squared {x2[obs]:.4f}; p-values: " + "; ".join(f"{NAMES[t]} {pv[t][obs]:.4f}" for t in TESTS_2X2))
    # SciPy on the observed table, and on every table for the tests SciPy has (every 12th on --quick)
    lib = {"chi2_contingency_default": float(stats.chi2_contingency(tab).pvalue),
           "chi2_contingency_no_correction": float(stats.chi2_contingency(tab, correction=False).pvalue),
           "fisher_exact": float(stats.fisher_exact(tab).pvalue),
           "boschloo_exact": float(stats.boschloo_exact(tab.T).pvalue),
           "barnard_exact": float(stats.barnard_exact(tab.T).pvalue)}
    print("  SciPy on the observed table: " + "; ".join(f"{k_} {v:.4f}" for k_, v in lib.items()))
    fis_diff = max(abs(float(stats.fisher_exact([[ai, m - ai], [bi, n - bi]]).pvalue) - pv["fisher"][i])
                   for i, (ai, bi) in enumerate(zip(a, b)))
    ok = (a + b > 0) & (a + b < N)
    chi_diff = max(abs(float(stats.chi2_contingency([[ai, m - ai], [bi, n - bi]], correction=cor).pvalue) - pv[t][i])
                   for t, cor in (("pearson", False), ("yates", True)) for i, (ai, bi) in enumerate(zip(a, b)) if ok[i])
    sub = [i for i in (range(len(a)) if not args.quick else range(0, len(a), 12)) if ok[i]]
    sp_bos = {i: float(stats.boschloo_exact(np.array([[a[i], m - a[i]], [b[i], n - b[i]]]).T).pvalue) for i in sub}
    sp_bar = {i: float(stats.barnard_exact(np.array([[a[i], m - a[i]], [b[i], n - b[i]]]).T).pvalue) for i in sub}
    bos_diff = max(abs(sp_bos[i] - pv["boschloo"][i]) for i in sub)
    bar_diff = max(abs(sp_bar[i] - pv["barnard"][i]) for i in sub)
    # SciPy's barnard_exact keeps the tables with |Z| >= |Z observed| with no tolerance: a table tied with the observed
    # one in exact arithmetic drops out when rounding leaves its |Z| a few units in the last place below
    z_float = {i: abs((a[i] / m - b[i] / n) / math.sqrt((a[i] + b[i]) / N * (1 - (a[i] + b[i]) / N) * (1 / m + 1 / n))) for i in sub}
    z2 = {(int(x), int(y)): exact_z2(int(x), int(y), m, n) for x, y in zip(a, b)}
    differ = [i for i in sub if abs(sp_bar[i] - pv["barnard"][i]) > 1e-9]
    explained = 0
    for i in differ:
        tied = [j for j in range(len(a)) if j != i and z2[(int(a[j]), int(b[j]))] == z2[(int(a[i]), int(b[i]))]]
        if any(ok[j] and abs((a[j] / m - b[j] / n) / math.sqrt((a[j] + b[j]) / N * (1 - (a[j] + b[j]) / N) * (1 / m + 1 / n)))
               < z_float[i] for j in tied):
            explained += 1
    worst = max(sub, key=lambda i: abs(sp_bar[i] - pv["barnard"][i]))
    mirror = (m - int(a[worst]), n - int(b[worst]))
    sp_mirror = float(stats.barnard_exact(np.array([[mirror[0], m - mirror[0]], [mirror[1], n - mirror[1]]]).T).pvalue)
    ties_worst = sorted((int(a[j]), int(b[j])) for j in range(len(a)) if z2[(int(a[j]), int(b[j]))] == z2[(int(a[worst]), int(b[worst]))])
    print(f"  over the {len(a)} tables with these row totals ({len(sub)} checked for the unconditional tests): largest "
          f"differences from SciPy: fisher_exact {fis_diff:.1e}, chi2_contingency {chi_diff:.1e}, boschloo_exact "
          f"{bos_diff:.1e}, barnard_exact {bar_diff:.1e}")
    print(f"  barnard_exact differs on {len(differ)} tables, {explained} of them tables whose |Z| ties another table's exactly; "
          f"worst ({int(a[worst])} of {m}, {int(b[worst])} of {n}): lab {pv['barnard'][worst]:.6f}, SciPy {sp_bar[worst]:.6f}, "
          f"SciPy on its mirror image {mirror} {sp_mirror:.6f}; exact ties {ties_worst}")
    flips = sum((sp_bar[i] <= ALPHA) != (pv["barnard"][i] <= ALPHA) for i in sub)
    # exact size of each 5% test in this design and in an unbalanced one
    size, region = size_study(a, b, m, n, pv, grid)
    designs = {"malocclusion": dict(m=m, n=n, size=size)}
    for t in TESTS_2X2:
        v = size[t]
        print(f"  ({m}, {n}) {NAMES[t]:34s} rejects {v['n_rejected']:3d} of {len(a)} tables; largest size {pc(v['max'], 2)}% at "
              f"pi = {v['argmax']:.4f}; size at pi 0.12 {pc(v['at']['0.12'], 2)}%; power 20% vs 5% {pc(v['power'], 1)}%, "
              f"reversed {pc(v['power_reversed'], 1)}%")
    mu, nu = 10, 40
    au, bu, pvu, _ = all_2x2_pvalues(mu, nu, grid)
    sizeu, regionu = size_study(au, bu, mu, nu, pvu, grid)
    designs["unbalanced"] = dict(m=mu, n=nu, size=sizeu)
    for t in TESTS_2X2:
        v = sizeu[t]
        print(f"  ({mu}, {nu}) {NAMES[t]:34s} rejects {v['n_rejected']:3d} of {len(au)} tables; largest size {pc(v['max'], 2)}% at "
              f"pi = {v['argmax']:.4f}")
    arg = sizeu["pearson"]["argmax"]
    print(f"  at that pi the expected count of successes in the group of {mu} is {mu * arg:.2f}")
    pairs = (("fisher", "boschloo"), ("fisher_doubled", "boschloo"), ("fisher", "mid_p"), ("fisher_doubled", "fisher"),
             ("yates", "fisher"), ("fisher", "pearson"))
    subset = {f"{s_}_in_{t}": bool(np.all(region[t][region[s_]])) for s_, t in pairs}
    same = {f"{s_}_equals_{t}": bool(np.array_equal(region[s_], region[t]))
            for s_, t in (("n_minus_1", "pearson"), ("barnard", "pearson"), ("yates", "fisher_doubled"))}
    print(f"  ({m}, {n}) rejection regions nested: " + ", ".join(f"{k_} {v}" for k_, v in subset.items()) + "; identical: " +
          ", ".join(f"{k_} {v}" for k_, v in same.items()))
    # Boschloo's two-sided p doubles the smaller one-sided p, so its region is guaranteed to contain the doubled-tail
    # Fisher test's, not the Irwin's-rule version's: check both designs
    subset_u = {f"{s_}_in_{t}": bool(np.all(regionu[t][regionu[s_]])) for s_, t in pairs}
    fisher_not_bos = [[int(au[i]), int(bu[i]), float(pvu["fisher"][i]), float(pvu["boschloo"][i])]
                      for i in np.flatnonzero(regionu["fisher"] & ~regionu["boschloo"])]
    bos_not_fisher_u = int((regionu["boschloo"] & ~regionu["fisher"]).sum())
    print(f"  ({mu}, {nu}) rejection regions nested: " + ", ".join(f"{k_} {v}" for k_, v in subset_u.items()))
    print(f"  ({mu}, {nu}) Fisher (Irwin's rule) rejects {len(fisher_not_bos)} tables Boschloo does not, for example " +
          ", ".join(f"({e[0]} of {mu}, {e[1]} of {nu}: Fisher {e[2]:.4f}, Boschloo {e[3]:.4f})" for e in fisher_not_bos[:2]) +
          f"; Boschloo rejects {bos_not_fisher_u} tables Fisher does not; size at pi 0.1: Fisher "
          f"{pc(sizeu['fisher']['at']['0.1'], 2)}%, Boschloo {pc(sizeu['boschloo']['at']['0.1'], 2)}%")
    extra = [[int(a[i]), int(b[i]), float(pv["fisher"][i]), float(pv["boschloo"][i])]
             for i in np.flatnonzero(region["boschloo"] & ~region["fisher"])]
    print(f"  tables Boschloo rejects and Fisher does not: {len(extra)}, for example " +
          ", ".join(f"({e[0]} of {m}, {e[1]} of {n}: Fisher {e[2]:.4f}, Boschloo {e[3]:.4f})" for e in extra[:3]))
    # simulated check of one exact size: Fisher's test at pi = 0.12
    rng = stream(args.seed, "tables", 1)
    reps = cfg["table_check"]
    sa, sb = rng.binomial(m, 0.12, reps), rng.binomial(n, 0.12, reps)
    hit = np.zeros((m + 1) * (n + 1), dtype=bool)
    hit[a * (n + 1) + b] = region["fisher"]
    sim = float(hit[sa * (n + 1) + sb].mean())
    ex = size["fisher"]["at"]["0.12"]
    print(f"  simulated check at pi = 0.12 (R = {reps:,}): Fisher rejects {pm(sim, mcse_share(sim, reps), 2)}, exact {pc(ex, 2)}%")
    print(f"  ({time.perf_counter() - t0:.1f} s for the 2x2 computations)")
    return dict(tea=tea, malocclusion=dict(table=tab, row_totals=[m, n], expected=expected, min_expected=float(expected.min()),
                                           chi2=float(x2[obs]), pvalues={t: float(pv[t][obs]) for t in TESTS_2X2},
                                           scipy=lib, n_checked=len(sub),
                                           scipy_max_abs_diff=dict(fisher=fis_diff, chi2=chi_diff, boschloo=bos_diff, barnard=bar_diff),
                                           barnard_ties=dict(n_differ=len(differ), n_explained_by_ties=explained,
                                                             decision_flips_at_5pc=int(flips), worst=[int(a[worst]), int(b[worst])],
                                                             lab=float(pv["barnard"][worst]), scipy=sp_bar[worst],
                                                             mirror=list(mirror), scipy_mirror=sp_mirror, tied_tables=ties_worst)),
                n_tables=len(a), pi_grid=PI_GRID, designs=designs, nested=subset, identical=same, boschloo_not_fisher=extra,
                unbalanced_nested=subset_u, unbalanced_fisher_not_boschloo=fisher_not_bos,
                unbalanced_boschloo_not_fisher=bos_not_fisher_u,
                power_alternative=POWER_ALT, pearson_unbalanced_expected=mu * arg,
                sim_check=dict(pi=0.12, R=reps, rate=sim, mcse=mcse_share(sim, reps), exact=ex))


# ------------------------------------------------------------------------------- anova
def anova_f(groups):
    """Classical one-way F, Welch's (1951) W and Brown-Forsythe's F*, with their degrees of freedom and p-values,
    along the last axis of each group's array."""
    k = len(groups)
    n = np.array([g.shape[-1] for g in groups], dtype=float)
    N = n.sum()
    means = np.stack([g.mean(-1) for g in groups], -1)
    vars_ = np.stack([g.var(-1, ddof=1) for g in groups], -1)
    grand = (means * n).sum(-1) / N
    ssb = (n * (means - grand[..., None]) ** 2).sum(-1)
    ssw = ((n - 1) * vars_).sum(-1)
    F = (ssb / (k - 1)) / (ssw / (N - k))
    pF = stats.f.sf(F, k - 1, N - k)
    w = n / vars_
    wsum = w.sum(-1)
    mw = (w * means).sum(-1) / wsum
    A = (w * (means - mw[..., None]) ** 2).sum(-1) / (k - 1)
    lam = ((1 - w / wsum[..., None]) ** 2 / (n - 1)).sum(-1)
    Wst = A / (1 + 2 * (k - 2) * lam / (k**2 - 1))
    df2w = (k**2 - 1) / (3 * lam)
    pW = stats.f.sf(Wst, k - 1, df2w)
    c = (1 - n / N) * vars_
    Fs = ssb / c.sum(-1)
    df2s = 1 / ((c / c.sum(-1)[..., None]) ** 2 / (n - 1)).sum(-1)
    pFs = stats.f.sf(Fs, k - 1, df2s)
    return dict(F=F, pF=pF, df=(k - 1, N - k), W=Wst, pW=pW, df2W=df2w, Fstar=Fs, pFstar=pFs, df2Fstar=df2s,
                ssb=ssb, ssw=ssw, grand=grand, means=means, vars=vars_)


def stage_anova(cfg, args):
    plants = read_plants()
    names = list(plants)
    g = [plants[k] for k in names]
    res = anova_f(g)
    k, N = len(g), sum(len(v) for v in g)
    print("anova: one-way ANOVA on PlantGrowth (dried weight, 10 plants per group)")
    for name, v in zip(names, g):
        print(f"  {name}: mean {v.mean():.3f}, SD {v.std(ddof=1):.4f}, n {len(v)}")
    msb, msw = float(res["ssb"]) / (k - 1), float(res["ssw"]) / (N - k)
    print(f"  grand mean {float(res['grand']):.4f}; between SS {float(res['ssb']):.4f} on {k - 1} df, mean square {msb:.4f}; "
          f"within SS {float(res['ssw']):.4f} on {N - k} df, mean square {msw:.4f}")
    print(f"  F = {msb:.4f}/{msw:.4f} = {float(res['F']):.4f}, p = {float(res['pF']):.6f}; Welch's W = {float(res['W']):.4f} on "
          f"2 and {float(res['df2W']):.3f} df, p = {float(res['pW']):.6f}; Brown-Forsythe F* = {float(res['Fstar']):.4f} on 2 and "
          f"{float(res['df2Fstar']):.3f} df, p = {float(res['pFstar']):.6f}")
    from statsmodels.stats.oneway import anova_oneway
    lib = {"scipy_f_oneway_default": float(stats.f_oneway(*g).pvalue),
           "scipy_f_oneway_welch": float(stats.f_oneway(*g, equal_var=False).pvalue),
           "statsmodels_anova_oneway_default": float(anova_oneway(g).pvalue),
           "statsmodels_anova_oneway_equal": float(anova_oneway(g, use_var="equal").pvalue)}
    diffs = [abs(lib["scipy_f_oneway_default"] - float(res["pF"])), abs(lib["scipy_f_oneway_welch"] - float(res["pW"])),
             abs(lib["statsmodels_anova_oneway_default"] - float(res["pW"])),
             abs(lib["statsmodels_anova_oneway_equal"] - float(res["pF"]))]
    print(f"  SciPy f_oneway default (equal_var=True) p = {lib['scipy_f_oneway_default']:.6f}, equal_var=False p = "
          f"{lib['scipy_f_oneway_welch']:.6f}; statsmodels anova_oneway default (use_var='unequal') p = "
          f"{lib['statsmodels_anova_oneway_default']:.6f}; largest difference {max(diffs):.1e}")
    # two groups: F is Student's t squared and W is Welch's t squared
    _, x, y = read_sleep()
    two = anova_f([y, x])
    ts, _, _, tw, dfw, _ = (scalar(v) for v in t_tests(y[None, :], x[None, :]))
    print(f"  two groups (sleep, as if unpaired): F = {float(two['F']):.4f} = {ts:.4f} squared; W = {float(two['W']):.4f} = "
          f"{tw:.4f} squared, on 1 and {float(two['df2W']):.3f} df (Welch's df {dfw:.3f})")
    # type I error with unequal variances, by simulation
    sims = {}
    for j, (label, (ns, sds)) in enumerate(ANOVA_DESIGNS.items()):
        rng = stream(args.seed, "anova", j)
        hits = np.zeros(3)
        done, reps = 0, cfg["anova"]
        while done < reps:
            kk = min(CHUNK, reps - done)
            gs = [rng.normal(0.0, s, (kk, nn)) for nn, s in zip(ns, sds)]
            r_ = anova_f(gs)
            hits += [(r_["pF"] <= ALPHA).sum(), (r_["pW"] <= ALPHA).sum(), (r_["pFstar"] <= ALPHA).sum()]
            done += kk
        rates = hits / reps
        sims[label] = dict(n=ns, sd=sds, R=reps, F=rates[0], W=rates[1], Fstar=rates[2],
                           mcse=[mcse_share(v, reps) for v in rates])
        print(f"  {label} (n {ns}, SD {sds}), R = {reps:,}: F {pm(rates[0], sims[label]['mcse'][0], 2)}, Welch W "
              f"{pm(rates[1], sims[label]['mcse'][1], 2)}, Brown-Forsythe F* {pm(rates[2], sims[label]['mcse'][2], 2)}")
    return dict(groups={nm: dict(values=v, mean=float(v.mean()), sd=float(v.std(ddof=1)), n=len(v)) for nm, v in zip(names, g)},
                grand=float(res["grand"]), ssb=float(res["ssb"]), ssw=float(res["ssw"]), msb=msb, msw=msw,
                F=float(res["F"]), pF=float(res["pF"]), df=[k - 1, N - k], W=float(res["W"]), pW=float(res["pW"]),
                df2W=float(res["df2W"]), Fstar=float(res["Fstar"]), pFstar=float(res["pFstar"]), df2Fstar=float(res["df2Fstar"]),
                library=lib, max_abs_diff=max(diffs),
                two_groups=dict(F=float(two["F"]), t_student=ts, W=float(two["W"]), t_welch=tw, df2W=float(two["df2W"]), df_welch=dfw),
                simulation=sims)


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
            "statsmodels": statsmodels.__version__, "choosing_py_sha1": sha1(pathlib.Path(__file__)),
            "data_sha1": {SLEEP_CSV.name: sha1(SLEEP_CSV), PLANT_CSV.name: sha1(PLANT_CSV)}, "budget": budget,
            "seed": args.seed, "replications": QUICK if args.quick else FULL,
            "flags": {"fault": args.fault, "n1": args.n1, "n2": args.n2, "ratio": args.ratio}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261101)
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the example stage's pairing")
    parser.add_argument("--n1", type=int, default=None, help="twosample: your own first group size (with --n2)")
    parser.add_argument("--n2", type=int, default=None, help="twosample: your own second group size")
    parser.add_argument("--ratio", type=float, default=None, help="twosample: your own SD ratio sigma1/sigma2")
    args = parser.parse_args()
    if (args.n1 is None) != (args.n2 is None):
        parser.error("--n1 and --n2 go together")
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, NumPy {prov['numpy']}, "
          f"SciPy {prov['scipy']}, statsmodels {prov['statsmodels']}; choosing.py {prov['choosing_py_sha1']}; budget {budget}, "
          f"seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"example": stage_example, "twosample": stage_twosample, "pretest": stage_pretest, "tables": stage_tables,
             "anova": stage_anova}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
