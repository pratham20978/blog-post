#!/usr/bin/env python3
"""Lab for "Permutation and Rank Tests: What They Actually Test" (Statistics for Data Scientists, part 10).

Every number the article calls measured or computed comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python permutation.py all --out mine.json            # every stage, the article's budget (about 3 minutes)
    python permutation.py all --quick --out quick.json   # the reader's budget (about 30 seconds), noisier
    python permutation.py example --out mine.json        # one stage

Stages:
    example      the worked example: Darwin's 15 pairs of crossed and self-fertilised Zea mays. All 2^15 = 32,768
                 sign assignments enumerated (Fisher's randomisation test), beside the paired t-test, the Wilcoxon
                 signed-rank test and the sign test on the same pairs; Galton's re-paired columns; the Hodges-Lehmann
                 estimate and its exact interval; what SciPy's default Monte Carlo version returns on these data; and
                 why a Monte Carlo p-value adds one, under many tests
    twosample    a permutation engine for two independent samples: the raw difference in means against the
                 studentised (Welch) statistic, as tests of equal means when the variances differ; size by simulation
    mannwhitney  what the Mann-Whitney test tests: equal medians with different shapes, different medians with
                 P(X > Y) = 1/2, and equal centres with unequal spreads; beside Brunner-Munzel's and Welch's tests
    efficiency   the price of ranks: the asymptotic relative efficiency of the rank-sum test to the t-test by
                 quadrature, and power at n = 20 per group by simulation, for eight shapes of distribution
    correlation  rank correlation on the law-school sample: Pearson, Spearman and Kendall, with permutation p-values

Every simulated quantity is printed as estimate +- MCSE (its Monte Carlo standard error) with its number of
replications R. Exact quantities (enumerations, binomial sums, quadrature) carry no MCSE. Every stage draws from its
own stream, SeedSequence([stage, sub-stream, seed]), so stages can run alone and repeat to the bit with the same NumPy.
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
from scipy import integrate, optimize, stats

HERE = pathlib.Path(__file__).resolve().parent
DARWIN_CSV = HERE / "data" / "darwin1876_zea_mays.csv"
LAW_CSV = HERE / "data" / "law_school_82.csv"
STAGES = ("example", "twosample", "mannwhitney", "efficiency", "correlation")

# Replications. The article quotes FULL; --quick is the reader's first run. Exact computations ignore the budget.
FULL = dict(scipy_runs=1_000, twosample=50_000, mannwhitney=20_000, hl_check=200, efficiency=100_000,
            correlation=99_999)
QUICK = {k: (v // 10 if k != "correlation" else 9_999) for k, v in FULL.items()}
ALPHA = 0.05
M_PERM = 999                      # random permutations per simulated data set (twosample)
CHUNK = 500                       # data sets that share one draw of M_PERM permutations
SCIPY_DEFAULT_RESAMPLES = 9_999   # scipy.stats.permutation_test's default n_resamples

TS_DESIGNS = ((10, 40), (25, 25))
TS_RATIOS = (0.25, 1 / 3, 0.5, 2 / 3, 1.0, 1.5, 2.0, 3.0, 4.0)       # sigma1 / sigma2, group 1 being the first size
MW_SIZES = (10, 25, 50, 100, 200, 400)                               # per group, scenarios S1 and S2
MW_S3_DESIGN = (10, 40)
MW_S3_RATIOS = TS_RATIOS
EFF_N = 20                                                           # per group
EFF_POWER = 0.80                                                     # t-test power under normality sets the shift
FWER_TESTS = tuple(int(round(10 ** (k / 4))) for k in range(0, 21))  # 1 to 100,000 tests, for the +1 calculation


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


def pc(share, nd=1):
    """A share as a percentage, rounded half up from its decimal value (shares are counts over R, so exact ties
    occur, and float formatting would round some of them down and others up)."""
    return str((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def hu(x, nd=4):
    """A number rounded half up from its decimal value."""
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def pm(est, mcse, nd=1):
    """'5.1% +- 0.1' for a share."""
    return f"{pc(est, nd)}% +- {pc(mcse, nd)}"


def key(r):
    """A ratio or size as a capture key: '0.25', '0.3333', '1', '4'."""
    return f"{r:.4g}"


def eighths(v):
    """An integer number of eighths of an inch as Darwin wrote it: 188 -> '23 4/8'."""
    sign = "-" if v < 0 else ""
    whole, rest = divmod(abs(int(v)), 8)
    return f"{sign}{whole}" + (f" {rest}/8" if rest else "")


def read_darwin():
    with DARWIN_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    pot = np.array([int(r["pot"]) for r in rows])
    crossed = np.array([int(r["crossed_eighths"]) for r in rows])
    selfed = np.array([int(r["self_eighths"]) for r in rows])
    return pot, crossed, selfed


def read_law():
    with LAW_CSV.open(encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(line for line in f if not line.startswith("#")) if r["in_sample"] == "1"]
    rows.sort(key=lambda r: int(r["sample_order"]))
    return np.array([float(r["lsat"]) for r in rows]), np.array([float(r["gpa"]) for r in rows])


def sign_matrix(n):
    """All 2^n sign assignments: row k puts a minus sign on observation i when bit i of k is set (row 0: all plus)."""
    minus = (np.arange(2 ** n)[:, None] >> np.arange(n)) & 1
    return minus, 1 - 2 * minus


# ------------------------------------------------------------------------------- stage: example
def stage_example(cfg, args):
    pot, crossed, selfed = read_darwin()
    d8 = crossed - selfed                                   # differences in eighths of an inch, exact integers
    n = d8.size
    d = d8 / 8.0
    print("example: Darwin's 15 pairs of Zea mays (1876), height in inches; crossed minus self-fertilised")
    print("  pairs (crossed, self, difference): " + ", ".join(
        f"({eighths(c)}, {eighths(s)}, {eighths(c - s)})" for c, s in zip(crossed, selfed)))
    print(f"  differences in eighths: {', '.join(str(v) for v in d8)}; sum {d8.sum()}; "
          f"{int((d8 > 0).sum())} positive, {int((d8 < 0).sum())} negative")

    # ---- the paired t-test, by hand
    mean, sd = d.mean(), d.std(ddof=1)
    se = sd / math.sqrt(n)
    t = mean / se
    p_t = 2 * stats.t.sf(abs(t), n - 1)
    crit = stats.t.ppf(1 - ALPHA / 2, n - 1)
    ci_t = (mean - crit * se, mean + crit * se)
    print(f"  paired t: mean {mean:.4f} in, SD {sd:.4f}, SE {se:.4f}, t = {t:.4f} on {n - 1} df, p = {p_t:.6f}, "
          f"95% CI {ci_t[0]:.4f} to {ci_t[1]:.4f}; 5% two-sided critical t {crit:.4f}")
    print(f"  one-sided: P(t >= {t:.3f}) = {pc(stats.t.sf(t, n - 1), 3)}%")

    # ---- the randomisation test: every one of the 2^15 sign assignments
    minus, signs = sign_matrix(n)
    absd = np.abs(d8)
    if args.fault:
        # E4: an earlier draft. It worked in centimetres, for readers outside the UK and US.
        dcm = d8 * 2.54 / 8
        sums_cm = signs @ np.abs(dcm)
        obs_cm = dcm.sum()
        ge_count = int((sums_cm >= obs_cm).sum())
        p_perm = min(1.0, 2 * ge_count / 2 ** n)
        print(f"  [draft] working in centimetres: observed total {float(obs_cm)!r} cm")
        sums = signs @ absd
        obs = int(d8.sum())
    else:
        sums = signs @ absd                                     # every possible total, exact in eighths
        obs = int(d8.sum())                                     # 314
        ge_count = int((sums >= obs).sum())
        p_perm = int((np.abs(sums) >= obs).sum()) / 2 ** n
    gt_count, eq_count = int((sums > obs).sum()), int((sums == obs).sum())
    n_minus = minus.sum(axis=1)
    table4 = []
    for k in range(n + 1):
        sel = n_minus == k
        table4.append([k, int((sums[sel] > obs).sum()), int((sums[sel] == obs).sum()), int((sums[sel] < obs).sum()),
                       int(sel.sum())])
    print(f"  randomisation test: {2 ** n:,} sign assignments; totals > {obs}: {gt_count}, = {obs}: {eq_count}, "
          f"at least {obs}: {ge_count} (one-sided {ge_count}/{2 ** n} = {pc(ge_count / 2 ** n, 3)}%); two-sided "
          f"p = {p_perm:.6f}")
    print("  by number of negative signs (>, =, <, total): " + "; ".join(
        f"{k}: {a}, {b}, {c:,}, {tot:,}" for k, a, b, c, tot in table4 if 2 <= k <= 6))
    vals, counts = np.unique(sums, return_counts=True)

    # ---- the Wilcoxon signed-rank test, from the same enumeration
    ranks = stats.rankdata(absd)
    v_obs = float(ranks[d8 > 0].sum())
    v_all = (1 - minus) @ ranks
    total_rank = n * (n + 1) / 2
    p_sr = (int((v_all >= v_obs).sum()) + int((v_all <= total_rank - v_obs).sum())) / 2 ** n
    v_vals, v_counts = np.unique(v_all, return_counts=True)
    print(f"  signed-rank: ranks of |d| for the two negatives {int(ranks[d8 < 0][0])} and {int(ranks[d8 < 0][1])}; "
          f"V+ = {v_obs:.0f}, V- = {total_rank - v_obs:.0f}; exact two-sided p = {p_sr:.6f} "
          f"({int((v_all >= v_obs).sum())} of {2 ** n:,} assignments have V+ >= {v_obs:.0f})")

    # ---- the sign test
    k_pos = int((d8 > 0).sum())
    p_sign = min(1.0, 2 * stats.binom.sf(k_pos - 1, n, 0.5))
    print(f"  sign test: {k_pos} of {n} positive; two-sided p = 2 x {int(round(stats.binom.sf(k_pos - 1, n, 0.5) * 2 ** n))}"
          f"/{2 ** n} = {p_sign:.6f}")

    # ---- the libraries
    lib = {"ttest_1samp": float(stats.ttest_1samp(d, 0.0).pvalue),
           "ttest_rel": float(stats.ttest_rel(crossed / 8, selfed / 8).pvalue),
           "wilcoxon": float(stats.wilcoxon(d).pvalue), "wilcoxon_statistic": float(stats.wilcoxon(d).statistic),
           "binomtest": float(stats.binomtest(k_pos, n).pvalue)}
    exact_res = stats.permutation_test((d8,), lambda x, axis: np.sum(x, axis=axis), permutation_type="samples",
                                       vectorized=True, n_resamples=np.inf)
    lib["permutation_test_exact"] = float(exact_res.pvalue)
    print(f"  SciPy: ttest_1samp p = {lib['ttest_1samp']:.6f}, ttest_rel p = {lib['ttest_rel']:.6f}; wilcoxon p = "
          f"{lib['wilcoxon']:.6f} (statistic {lib['wilcoxon_statistic']:.0f}, the smaller rank sum); binomtest p = "
          f"{lib['binomtest']:.6f}; permutation_test(n_resamples=np.inf) p = {lib['permutation_test_exact']:.6f}")

    # ---- Galton's re-pairing: both columns sorted, tallest against tallest (Fisher 1935, section 19)
    g8 = np.sort(crossed)[::-1] - np.sort(selfed)[::-1]
    g = g8 / 8.0
    t_galton = g.mean() / (g.std(ddof=1) / math.sqrt(n))
    p_galton = 2 * stats.t.sf(abs(t_galton), n - 1)
    print(f"  Galton's re-paired columns: differences {', '.join(eighths(v) for v in g8)}; mean {g.mean():.4f} (unchanged), "
          f"SD {g.std(ddof=1):.4f}, t = {t_galton:.4f}, p = {p_galton:.2e}")

    # ---- the Hodges-Lehmann estimate and its exact interval
    i, j = np.triu_indices(n)
    walsh16 = np.sort(d8[i] + d8[j])                         # twice each Walsh average, in eighths: sixteenths of an inch
    hl = float(np.median(walsh16)) / 16
    v_cdf = np.cumsum(v_counts) / 2 ** n                     # P(V <= v) for v = v_vals
    qu = int(v_vals[np.searchsorted(v_cdf, ALPHA / 2 - 1e-12)])   # R: qsignrank(alpha/2, n)
    lower, upper = walsh16[qu - 1] / 16, walsh16[int(total_rank) - qu] / 16
    achieved = 1 - 2 * float(v_cdf[np.searchsorted(v_vals, qu - 1)])
    print(f"  Hodges-Lehmann: {walsh16.size} Walsh averages; median {hl:.4f} in; exact interval from the {qu}th smallest "
          f"to the {qu}th largest: {lower:.4f} to {upper:.4f} in, confidence {pc(achieved, 2)}%")

    # ---- SciPy's default: 9,999 random sign assignments, so a Monte Carlo test. Its p-value over reruns is exact:
    # the count B of resampled totals at least the observed one is Binomial(9,999, 863/32,768), and the two-sided
    # p-value is 2(B + 1)/10,000.
    q1 = ge_count / 2 ** n
    m = SCIPY_DEFAULT_RESAMPLES
    b = np.arange(m + 1)
    pmf = stats.binom.pmf(b, m, q1)
    pvals = np.minimum(1.0, 2 * (b + 1) / (m + 1))
    p_below = float(pmf[pvals <= ALPHA].sum())
    mean_p = float((pmf * pvals).sum())
    sd_p = math.sqrt(float((pmf * (pvals - mean_p) ** 2).sum()))
    cdf = np.cumsum(pmf)
    q_lo, q_hi = pvals[np.searchsorted(cdf, 0.025)], pvals[np.searchsorted(cdf, 0.975)]
    keep = pmf > 1e-6
    print(f"  SciPy's default (n_resamples={m:,}): over reruns its two-sided p has mean {mean_p:.5f}, SD {sd_p:.5f}, "
          f"95% of runs between {q_lo:.4f} and {q_hi:.4f}; P(p <= 0.05) = {pc(p_below, 1)}% (exact, binomial)")
    runs = []
    for k in range(cfg["scipy_runs"]):
        res = stats.permutation_test((d8,), lambda x, axis: np.sum(x, axis=axis), permutation_type="samples",
                                     vectorized=True, rng=stream(args.seed, "example", 1000 + k))
        runs.append(float(res.pvalue))
    runs = np.array(runs)
    share = float((runs <= ALPHA).mean())
    print(f"  {len(runs):,} actual SciPy runs with different seeds: p from {runs.min():.4f} to {runs.max():.4f}; "
          f"p <= 0.05 in {pm(share, mcse_share(share, len(runs)), 1)} (z against exact "
          f"{(share - p_below) / max(mcse_share(p_below, len(runs)), 1e-12):+.1f})")

    # ---- why a Monte Carlo p-value adds one: Bonferroni over k independent true nulls, m random permutations each,
    # continuous statistic. B is uniform on 0..m under H0 (Phipson and Smyth 2010), so P(B/m <= x) = (floor(m x) + 1)/(m + 1)
    # and P((B + 1)/(m + 1) <= x) = floor((m + 1) x)/(m + 1).
    fwer = {}
    for mm in (999, 9_999):
        naive, plus1 = [], []
        for kk in FWER_TESTS:
            x = ALPHA / kk
            p_n = (math.floor(mm * x + 1e-12) + 1) / (mm + 1)
            p_p = math.floor((mm + 1) * x + 1e-12) / (mm + 1)
            naive.append(1 - (1 - p_n) ** kk)
            plus1.append(1 - (1 - p_p) ** kk)
        fwer[str(mm)] = dict(tests=list(FWER_TESTS), naive=naive, plus_one=plus1)
    f999 = fwer["999"]
    idx = FWER_TESTS.index(1000)
    zeros_ps = 30_000 / 1_001
    print(f"  the +1: with m = 999 permutations per test and Bonferroni over 1,000 true nulls, b/m gives a family-wise "
          f"error of {pc(f999['naive'][idx], 1)}% and (b + 1)/(m + 1) gives {pc(f999['plus_one'][idx], 1)}%; "
          f"30,000 null tests at m = 1,000 give {zeros_ps:.2f} zero p-values on average")
    out = dict(d8=d8, crossed8=crossed, self8=selfed, pot=pot, n=n, sum8=obs, mean=mean, sd=sd, se=se, t=t, p_t=p_t,
               ci_t=ci_t, crit=crit, one_sided_t=stats.t.sf(t, n - 1),
               perm=dict(n_assign=2 ** n, gt=gt_count, eq=eq_count, ge=ge_count, one_sided=ge_count / 2 ** n,
                         p=p_perm, null_values=vals, null_counts=counts),
               table4=table4,
               signed_rank=dict(ranks=ranks, v=v_obs, v_minus=total_rank - v_obs, p=p_sr, v_values=v_vals,
                                v_counts=v_counts, ge=int((v_all >= v_obs).sum())),
               sign=dict(k=k_pos, p=p_sign),
               library=lib,
               galton=dict(d8=g8, mean=g.mean(), sd=g.std(ddof=1), t=t_galton, p=p_galton),
               hodges_lehmann=dict(estimate=hl, lower=lower, upper=upper, qu=qu, confidence=achieved,
                                   n_walsh=int(walsh16.size)),
               monte_carlo=dict(m=m, q1=q1, p_below=p_below, mean_p=mean_p, sd_p=sd_p, q_lo=q_lo, q_hi=q_hi,
                                pvalues=pvals[keep], pmf=pmf[keep], runs=len(runs), runs_share=share,
                                runs_mcse=mcse_share(share, len(runs)), runs_min=runs.min(), runs_max=runs.max()),
               fwer=fwer, zeros_phipson_smyth=zeros_ps, fault=bool(args.fault))
    return out


# ------------------------------------------------------------------------------- stage: twosample
def perm_pvalues(x, n1, m, rng):
    """Two-sided permutation p-values for each row of x (rows are data sets, the first n1 columns group 1), for the
    raw difference in means and for the studentised (Welch) statistic. One draw of m random relabellings, with
    replacement, is shared by the rows; the +1 counts the observed labelling (Phipson and Smyth 2010)."""
    r, big_n = x.shape
    n2 = big_n - n1
    labels = np.argsort(rng.random((m, big_n)), axis=1)[:, :n1]
    mask = np.zeros((m + 1, big_n))
    mask[0, :n1] = 1.0                                       # row 0: the observed labelling
    mask[np.repeat(np.arange(1, m + 1), n1), labels.ravel()] = 1.0
    s1, q1 = x @ mask.T, (x * x) @ mask.T
    s, q = x.sum(axis=1, keepdims=True), (x * x).sum(axis=1, keepdims=True)
    m1, m2 = s1 / n1, (s - s1) / n2
    v1 = (q1 - n1 * m1 ** 2) / (n1 - 1)
    v2 = (q - q1 - n2 * m2 ** 2) / (n2 - 1)
    diff = m1 - m2
    welch = diff / np.sqrt(v1 / n1 + v2 / n2)
    out = []
    for stat in (np.abs(diff), np.abs(welch)):
        obs = stat[:, :1]
        count = (stat[:, 1:] >= obs * (1 - 1e-12)).sum(axis=1)
        out.append((count + 1) / (m + 1))
    sp2 = ((n1 - 1) * v1[:, 0] + (n2 - 1) * v2[:, 0]) / (big_n - 2)
    p_student = 2 * stats.t.sf(np.abs(diff[:, 0]) / np.sqrt(sp2 * (1 / n1 + 1 / n2)), big_n - 2)
    a, b = v1[:, 0] / n1, v2[:, 0] / n2
    df_w = (a + b) ** 2 / (a ** 2 / (n1 - 1) + b ** 2 / (n2 - 1))
    p_welch = 2 * stats.t.sf(np.abs(welch[:, 0]), df_w)
    return out[0], out[1], p_student, p_welch


def twosample_point(n1, n2, ratio, reps, rng):
    hits = np.zeros(4)
    done = 0
    while done < reps:
        k = min(CHUNK, reps - done)
        x = np.concatenate([rng.normal(0.0, ratio, (k, n1)), rng.normal(0.0, 1.0, (k, n2))], axis=1)
        for j, p in enumerate(perm_pvalues(x, n1, M_PERM, rng)):
            hits[j] += (p <= ALPHA).sum()
        done += k
    rates = hits / reps
    return dict(R=reps, perm_diff=rates[0], perm_studentised=rates[1], student=rates[2], welch=rates[3],
                mcse=[mcse_share(v, reps) for v in rates])


def engine_check(rng):
    """The engine against scipy.stats.permutation_test on a design small enough to enumerate: 4 and 6 values,
    C(10, 4) = 210 relabellings. Fed every relabelling, the engine must return SciPy's exact p-values."""
    x = np.round(np.concatenate([rng.normal(0.0, 2.0, 4), rng.normal(0.0, 1.0, 6)]), 3)
    n1, big_n = 4, 10
    from itertools import combinations
    combos = [c for c in combinations(range(big_n), n1)]
    mask = np.zeros((len(combos), big_n))
    for k, c in enumerate(combos):
        mask[k, list(c)] = 1.0
    s1, q1 = x @ mask.T, (x * x) @ mask.T
    m1, m2 = s1 / n1, (x.sum() - s1) / (big_n - n1)
    v1 = (q1 - n1 * m1 ** 2) / (n1 - 1)
    v2 = ((x * x).sum() - q1 - (big_n - n1) * m2 ** 2) / (big_n - n1 - 1)
    diff, welch = m1 - m2, (m1 - m2) / np.sqrt(v1 / n1 + v2 / (big_n - n1))
    ours = [float((np.abs(s) >= abs(s[0]) * (1 - 1e-12)).mean()) for s in (diff, welch)]   # combos[0] is the observed

    def welch_stat(a, b, axis):
        return (a.mean(axis=axis) - b.mean(axis=axis)) / np.sqrt(a.var(axis=axis, ddof=1) / a.shape[axis]
                                                                 + b.var(axis=axis, ddof=1) / b.shape[axis])

    def diff_stat(a, b, axis):
        return a.mean(axis=axis) - b.mean(axis=axis)
    # the engine counts |T*| >= |t|; SciPy's 'two-sided' doubles the smaller one-sided p instead, so the like-for-like
    # comparison hands SciPy |T| with alternative='greater', and its default is recorded beside it
    sp = [float(stats.permutation_test((x[:n1], x[n1:]), lambda a, b, axis, f=f: np.abs(f(a, b, axis)),
                                       n_resamples=np.inf, vectorized=True, alternative="greater").pvalue)
          for f in (diff_stat, welch_stat)]
    sp_doubled = [float(stats.permutation_test((x[:n1], x[n1:]), f, n_resamples=np.inf, vectorized=True).pvalue)
                  for f in (diff_stat, welch_stat)]
    return dict(x=x, ours=ours, scipy=sp, scipy_two_sided_default=sp_doubled,
                max_abs_diff=max(abs(a - b) for a, b in zip(ours, sp)))


def stage_twosample(cfg, args):
    print(f"twosample: permutation tests of equal means for two normal samples, {M_PERM} random relabellings per data "
          f"set, alpha = {ALPHA} two-sided")
    chk = engine_check(stream(args.seed, "twosample", 999))
    print(f"  engine check, 4 and 6 values, all 210 relabellings: difference p {chk['ours'][0]:.6f} (SciPy on |T| "
          f"{chk['scipy'][0]:.6f}), studentised p {chk['ours'][1]:.6f} (SciPy on |T| {chk['scipy'][1]:.6f}); SciPy's "
          f"default two-sided p, which doubles the smaller tail: {chk['scipy_two_sided_default'][0]:.6f} and "
          f"{chk['scipy_two_sided_default'][1]:.6f}")
    reps = cfg["twosample"]
    if args.n1 is not None:
        designs, ratios = ((args.n1, args.n2),), ((args.ratio if args.ratio is not None else 1.0),)
    else:
        designs, ratios = TS_DESIGNS, TS_RATIOS
    res = {}
    for di, (n1, n2) in enumerate(designs):
        rows = {}
        print(f"  n1 = {n1}, n2 = {n2} (sigma1/sigma2: permutation of the difference, permutation of Welch's t; "
              f"Student's t, Welch's t), R = {reps:,}")
        for ri, ratio in enumerate(ratios):
            rng = stream(args.seed, "twosample", 100 * di + ri + (50 if args.n1 is not None else 0))
            pt = twosample_point(n1, n2, ratio, reps, rng)
            rows[key(ratio)] = pt
            mc = pt["mcse"]
            print(f"    {ratio:.3f}: difference {pm(pt['perm_diff'], mc[0], 2)}, studentised {pm(pt['perm_studentised'], mc[1], 2)}; "
                  f"Student {pm(pt['student'], mc[2], 2)}, Welch {pm(pt['welch'], mc[3], 2)}")
        res[f"{n1},{n2}"] = rows
    return dict(m=M_PERM, designs=res, custom=args.n1 is not None, engine_check=chk)


# ------------------------------------------------------------------------------- stage: mannwhitney
LN2 = math.log(2.0)


def p_x_gt_y_normal_vs_exp(c):
    """P(X > Y) for X ~ N(0, 1) and Y = E - c, E ~ Exp(1): the integral of P(Y < x) phi(x) over x > -c."""
    tail = math.exp(-c + 0.5) * stats.norm.sf(1 - c)          # the integral of exp(-(x + c)) phi(x) over x > -c
    return float(stats.norm.sf(-c) - tail)


def median_x_minus_y(c):
    """The median of X - Y for X ~ N(0, 1), Y = E - c: what the two-sample Hodges-Lehmann estimate converges to."""
    def cdf(t):
        return integrate.quad(lambda e: stats.norm.cdf(t - c + e) * math.exp(-e), 0, np.inf, epsabs=1e-13)[0]
    return optimize.brentq(lambda t: cdf(t) - 0.5, -5, 5, xtol=1e-12)


def rates_three_tests(x, y):
    p_mw = stats.mannwhitneyu(x, y, axis=1).pvalue
    p_bm = stats.brunnermunzel(x, y, axis=1).pvalue
    p_w = stats.ttest_ind(x, y, equal_var=False, axis=1).pvalue
    return np.array([(p_mw <= ALPHA).sum(), (p_bm <= ALPHA).sum(), (p_w <= ALPHA).sum()])


def simulate_mw(draw_x, draw_y, n1, n2, reps, rng):
    hits = np.zeros(3)
    done = 0
    step = max(250, min(5_000, 2_000_000 // (n1 + n2)))
    while done < reps:
        k = min(step, reps - done)
        hits += rates_three_tests(draw_x(rng, (k, n1)), draw_y(rng, (k, n2)))
        done += k
    rates = hits / reps
    return dict(R=reps, mw=rates[0], bm=rates[1], welch=rates[2], mcse=[mcse_share(v, reps) for v in rates])


def stage_mannwhitney(cfg, args):
    reps = cfg["mannwhitney"]
    c1 = LN2                                                   # S1: Y = E - ln 2 has median 0, like X
    theta1 = p_x_gt_y_normal_vs_exp(c1)
    c2 = optimize.brentq(lambda c: p_x_gt_y_normal_vs_exp(c) - 0.5, 0.0, 2.0, xtol=1e-14)   # S2: P(X > Y) = 1/2
    hl1 = median_x_minus_y(c1)
    print("mannwhitney: what the rank-sum test responds to; X ~ N(0, 1) against Y = E - c with E ~ Exp(1) (SD 1 both)")
    print(f"  S1, equal medians: c = ln 2 = {c1:.6f}; medians 0 and 0; means 0 and {1 - c1:.4f}; P(X > Y) = {theta1:.6f}; "
          f"the median of X - Y (the two-sample Hodges-Lehmann target) = {hl1:.4f}")
    print(f"  S2, P(X > Y) = 1/2: c = {c2:.6f}; medians 0 and {LN2 - c2:.4f}; means 0 and {1 - c2:.4f}")
    # a check of the quadrature by simulation, on one long draw
    rng = stream(args.seed, "mannwhitney", 900)
    xx, ee = rng.normal(size=2_000_000), rng.exponential(size=2_000_000)
    sim_theta1 = float((xx > ee - c1).mean())
    print(f"  simulated check of P(X > Y) in S1 on 2,000,000 pairs: {sim_theta1:.5f} (exact {theta1:.5f})")

    def draw_norm(r, shape):
        return r.normal(size=shape)

    def draw_exp(c):
        return lambda r, shape: r.exponential(size=shape) - c

    out = dict(theta1=theta1, c1=c1, c2=c2, median_y2=LN2 - c2, mean_y1=1 - c1, mean_y2=1 - c2, hl_target1=hl1,
               sim_theta1=sim_theta1, S1={}, S2={}, S3={})
    for label, c, sub in (("S1", c1, 10), ("S2", c2, 20)):
        print(f"  {label}, n per group (Mann-Whitney, Brunner-Munzel, Welch's t), R = {reps:,}:")
        for k, nn in enumerate(MW_SIZES):
            pt = simulate_mw(draw_norm, draw_exp(c), nn, nn, reps, stream(args.seed, "mannwhitney", sub + k))
            out[label][str(nn)] = pt
            mc = pt["mcse"]
            print(f"    {nn:>3}: Mann-Whitney {pm(pt['mw'], mc[0])}, Brunner-Munzel {pm(pt['bm'], mc[1])}, "
                  f"Welch {pm(pt['welch'], mc[2])}")
    n1, n2 = MW_S3_DESIGN
    print(f"  S3, normal data with equal centres, n1 = {n1}, n2 = {n2}, by sigma1/sigma2; P(X > Y) = 1/2 exactly:")
    for k, ratio in enumerate(MW_S3_RATIOS):
        pt = simulate_mw(lambda r, shape, s=ratio: r.normal(0.0, s, size=shape), draw_norm, n1, n2, reps,
                         stream(args.seed, "mannwhitney", 30 + k))
        out["S3"][key(ratio)] = pt
        mc = pt["mcse"]
        print(f"    {ratio:.2f}: Mann-Whitney {pm(pt['mw'], mc[0], 2)}, Brunner-Munzel {pm(pt['bm'], mc[1], 2)}, "
              f"Welch {pm(pt['welch'], mc[2], 2)}")
    # the two-sample Hodges-Lehmann estimate in S1: the median of the n1 n2 pairwise differences
    rng = stream(args.seed, "mannwhitney", 800)
    est = []
    for _ in range(cfg["hl_check"]):
        x, y = rng.normal(size=400), rng.exponential(size=400) - c1
        est.append(float(np.median((x[:, None] - y[None, :]).ravel())))
    est = np.array(est)
    out["hl_sim"] = dict(R=len(est), mean=float(est.mean()), mcse=float(est.std(ddof=1) / math.sqrt(len(est))))
    print(f"  two-sample Hodges-Lehmann in S1 at 400 per group, R = {len(est)}: mean {est.mean():.4f} +- "
          f"{out['hl_sim']['mcse']:.4f} (target {hl1:.4f}); the difference in medians is 0")
    # a small fixed example to match R's wilcox.test(x, y, conf.int = TRUE), done privately: the first 12 and 15 draws
    rng = stream(args.seed, "mannwhitney", 801)
    x, y = np.round(rng.normal(size=12), 3), np.round(rng.exponential(size=15) - c1, 3)
    diffs = np.sort((x[:, None] - y[None, :]).ravel())
    out["hl_example"] = dict(x=x, y=y, estimate=float(np.median(diffs)),
                             mw=float(stats.mannwhitneyu(x, y).pvalue),
                             mw_statistic=float(stats.mannwhitneyu(x, y).statistic))
    print(f"  fixed example for the R cross-check (12 and 15 values): HL {np.median(diffs):.4f}, Mann-Whitney U "
          f"{out['hl_example']['mw_statistic']:.0f}, p = {out['hl_example']['mw']:.6f}")
    return out


# ------------------------------------------------------------------------------- stage: efficiency
def shapes():
    """Eight shapes scaled to variance 1: (name, density on its support, sampler)."""
    s5, s3 = math.sqrt(3 / 5), math.sqrt(1 / 3)
    sl, sb = math.sqrt(3) / math.pi, 1 / math.sqrt(2)
    ck = 1 / math.sqrt(0.9 + 0.1 * 9)
    r5 = math.sqrt(5)

    def contaminated(r, shape):
        z = r.normal(size=shape)
        return ck * np.where(r.random(shape) < 0.1, 3 * z, z)

    return [
        ("parabolic", lambda v: 3 / (20 * r5) * (5 - v * v) if abs(v) < r5 else 0.0, (-r5, r5),
         lambda r, shape: r5 * (2 * r.beta(2, 2, size=shape) - 1)),
        ("normal", lambda v: stats.norm.pdf(v), (-np.inf, np.inf), lambda r, shape: r.normal(size=shape)),
        ("uniform", lambda v: 1 / (2 * math.sqrt(3)) if abs(v) < math.sqrt(3) else 0.0, (-math.sqrt(3), math.sqrt(3)),
         lambda r, shape: r.uniform(-math.sqrt(3), math.sqrt(3), size=shape)),
        ("logistic", lambda v: stats.logistic.pdf(v, scale=sl), (-np.inf, np.inf),
         lambda r, shape: r.logistic(scale=sl, size=shape)),
        ("t, 5 df", lambda v: stats.t.pdf(v / s5, 5) / s5, (-np.inf, np.inf),
         lambda r, shape: s5 * r.standard_t(5, size=shape)),
        ("Laplace", lambda v: stats.laplace.pdf(v, scale=sb), (-np.inf, np.inf),
         lambda r, shape: r.laplace(scale=sb, size=shape)),
        ("contaminated normal", lambda v: ck ** -1 * (0.9 * stats.norm.pdf(v / ck) + 0.1 * stats.norm.pdf(v / ck, scale=3)),
         (-np.inf, np.inf), contaminated),
        ("t, 3 df", lambda v: stats.t.pdf(v / s3, 3) / s3, (-np.inf, np.inf),
         lambda r, shape: s3 * r.standard_t(3, size=shape)),
    ]


def stage_efficiency(cfg, args):
    reps = cfg["efficiency"]
    df = 2 * EFF_N - 2
    crit = stats.t.ppf(1 - ALPHA / 2, df)

    def power_t(delta):
        nc = delta * math.sqrt(EFF_N / 2)
        return stats.nct.sf(crit, df, nc) + stats.nct.sf(crit, df, -nc)

    delta = optimize.brentq(lambda dd: power_t(dd) - EFF_POWER, 0.1, 3.0, xtol=1e-12)
    print(f"efficiency: rank-sum (Mann-Whitney) against the t-test; ARE = 12 sigma^2 (int f^2)^2; power at n = {EFF_N} "
          f"per group for a shift of {delta:.4f} SD, which gives Student's t {pc(EFF_POWER, 0)}% power for normal data")
    out = dict(n=EFF_N, delta=delta, R=reps, shapes={})
    for k, (name, f, (lo, hi), draw) in enumerate(shapes()):
        var = integrate.quad(lambda v: v * v * f(v), lo, hi, limit=200, epsabs=1e-13)[0]
        mass = integrate.quad(f, lo, hi, limit=200, epsabs=1e-13)[0]
        f2 = integrate.quad(lambda v: f(v) ** 2, lo, hi, limit=200, epsabs=1e-13)[0]
        are = 12 * var * f2 ** 2
        rng = stream(args.seed, "efficiency", k)
        hits = np.zeros(2)
        done = 0
        while done < reps:
            kk = min(10_000, reps - done)
            x, y = draw(rng, (kk, EFF_N)), draw(rng, (kk, EFF_N)) + delta
            hits += [(stats.ttest_ind(x, y, equal_var=False, axis=1).pvalue <= ALPHA).sum(),
                     (stats.mannwhitneyu(x, y, axis=1).pvalue <= ALPHA).sum()]
            done += kk
        rates = hits / reps
        out["shapes"][name] = dict(are=are, mass=mass, variance=var, welch=rates[0], mw=rates[1],
                                   mcse=[mcse_share(v, reps) for v in rates])
        print(f"  {name:>19}: ARE {are:.4f} (mass {mass:.6f}, variance {var:.6f}); power Welch {pm(rates[0], out['shapes'][name]['mcse'][0])}, "
              f"Mann-Whitney {pm(rates[1], out['shapes'][name]['mcse'][1])}, R = {reps:,}")
    print(f"  3/pi = {3 / math.pi:.6f}; 108/125 = {108 / 125:.6f}; pi^2/9 = {math.pi ** 2 / 9:.6f}")
    return out


# ------------------------------------------------------------------------------- stage: correlation
def spearman_null_counts(n):
    """The exact permutation distribution of T = sum_i i * pi(i) over all n! orderings pi of 0..n-1, by dynamic
    programming over the set of values already placed (2^n subsets; position i is the subset's size). Spearman's
    rho is 1 - 6 sum (i - pi(i))^2 / (n (n^2 - 1)), and sum (i - pi(i))^2 = 2 sum i^2 - 2 T."""
    tmax = sum(i * i for i in range(n))
    layer = {0: np.zeros(tmax + 1, dtype=np.int64)}
    layer[0][0] = 1
    for pos in range(n):
        nxt = {}
        for mask, counts in layer.items():
            nz = np.flatnonzero(counts)
            top = nz[-1] + 1 if nz.size else 0
            for v in range(n):
                if mask >> v & 1:
                    continue
                shift = pos * v
                tgt = nxt.setdefault(mask | (1 << v), np.zeros(tmax + 1, dtype=np.int64))
                tgt[shift:shift + top] += counts[:top]
        layer = nxt
    (full,) = layer.values()
    assert int(full.sum()) == math.factorial(n)
    return full


def kendall_counts(x, y):
    dx, dy = np.sign(x[:, None] - x[None, :]), np.sign(y[:, None] - y[None, :])
    prod = np.triu(dx * dy, 1)
    return int((prod > 0).sum()), int((prod < 0).sum())


def stage_correlation(cfg, args):
    lsat, gpa = read_law()
    n = lsat.size
    r = float(np.corrcoef(lsat, gpa)[0, 1])
    rl, rg = stats.rankdata(lsat), stats.rankdata(gpa)
    rho = float(np.corrcoef(rl, rg)[0, 1])
    rho_formula = 1 - 6 * float(((rl - rg) ** 2).sum()) / (n * (n * n - 1))
    conc, disc = kendall_counts(lsat, gpa)
    tau = (conc - disc) / (n * (n - 1) / 2)
    lib = {"pearsonr_p": float(stats.pearsonr(lsat, gpa).pvalue), "spearmanr_p": float(stats.spearmanr(lsat, gpa).pvalue),
           "spearmanr_rho": float(stats.spearmanr(lsat, gpa).statistic),
           "kendalltau_tau": float(stats.kendalltau(lsat, gpa).statistic),
           "kendalltau_p": float(stats.kendalltau(lsat, gpa).pvalue)}
    print(f"correlation: the law-school sample of 15 (average LSAT and GPA of each school's class); ties: "
          f"{n - np.unique(lsat).size} in LSAT, {n - np.unique(gpa).size} in GPA")
    print(f"  Pearson r = {r:.4f}; Spearman rho = {rho:.4f} (Pearson on ranks; 1 - 6 sum d^2/(n(n^2 - 1)) = {rho_formula:.4f}; "
          f"sum d^2 = {int(((rl - rg) ** 2).sum())}); Kendall tau = ({conc} - {disc})/{n * (n - 1) // 2} = {tau:.4f}")
    print(f"  SciPy: pearsonr p = {lib['pearsonr_p']:.6f} (t), spearmanr p = {lib['spearmanr_p']:.6f} (t "
          f"approximation), kendalltau p = {lib['kendalltau_p']:.6f} (exact)")
    # Spearman's exact permutation p-value: every one of the 15! orderings, counted by dynamic programming
    t0 = time.perf_counter()
    counts_t = spearman_null_counts(n)
    tvals = np.arange(counts_t.size)
    rho_t = 1 - 6 * (2 * sum(i * i for i in range(n)) - 2 * tvals) / (n * (n * n - 1))
    hit = np.abs(rho_t) >= abs(rho) * (1 - 1e-12)
    n_hit = int(counts_t[hit].sum())
    p_spear = n_hit / math.factorial(n)
    print(f"  Spearman, exact: {n_hit:,} of the {math.factorial(n):,} orderings have |rho| >= {rho:.4f}; p = "
          f"{p_spear:.6f} ({time.perf_counter() - t0:.1f} s)")
    m = cfg["correlation"]
    rng = stream(args.seed, "correlation", 0)
    obs = np.array([r, rho, tau])
    counts = np.zeros(3)
    done = 0
    gl = gpa - gpa.mean()
    while done < m:
        k = min(20_000, m - done)
        perm = np.argsort(rng.random((k, n)), axis=1)
        gp = gpa[perm]
        rp = rg[perm]
        x0, r0 = lsat - lsat.mean(), rl - rl.mean()
        pr = (gp - gp.mean(axis=1, keepdims=True)) @ x0 / (np.sqrt((x0 ** 2).sum()) * np.sqrt((gl ** 2).sum()))
        prho = (rp - rp.mean(axis=1, keepdims=True)) @ r0 / ((r0 ** 2).sum())
        sx = np.sign(lsat[:, None] - lsat[None, :])[np.triu_indices(n, 1)]
        iu, ju = np.triu_indices(n, 1)
        ptau = (np.sign(gp[:, iu] - gp[:, ju]) * sx).sum(axis=1) / (n * (n - 1) / 2)
        for j, v in enumerate((pr, prho, ptau)):
            counts[j] += (np.abs(v) >= abs(obs[j]) * (1 - 1e-12)).sum()
        done += k
    pvals = (counts + 1) / (m + 1)
    print(f"  permutation p-values, {m:,} random reorderings of GPA plus the observed one: Pearson {pvals[0]:.6f}, "
          f"Spearman {pvals[1]:.6f}, Kendall {pvals[2]:.6f}")
    return dict(n=n, lsat=lsat, gpa=gpa, r=r, rho=rho, rho_formula=rho_formula, tau=tau, concordant=conc,
                discordant=disc, sum_d2=float(((rl - rg) ** 2).sum()), ranks_lsat=rl, ranks_gpa=rg, library=lib,
                spearman_exact=dict(p=p_spear, count=n_hit, orderings=math.factorial(n)),
                m=m, perm_p=dict(pearson=pvals[0], spearman=pvals[1], kendall=pvals[2]))


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
    return {"captured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "os": f"{platform.system()} {platform.release()} {platform.machine()}", "cpu": cpu,
            "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "permutation_py_sha1": sha1(pathlib.Path(__file__)),
            "data_sha1": {DARWIN_CSV.name: sha1(DARWIN_CSV), LAW_CSV.name: sha1(LAW_CSV)}, "budget": budget,
            "seed": args.seed, "replications": QUICK if args.quick else FULL,
            "flags": {"fault": args.fault, "n1": args.n1, "n2": args.n2, "ratio": args.ratio}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261123)
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the example stage's enumeration")
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
          f"SciPy {prov['scipy']}; permutation.py {prov['permutation_py_sha1']}; budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"example": stage_example, "twosample": stage_twosample, "mannwhitney": stage_mannwhitney,
             "efficiency": stage_efficiency, "correlation": stage_correlation}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
