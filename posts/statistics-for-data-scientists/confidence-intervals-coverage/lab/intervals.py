#!/usr/bin/env python3
"""Lab for "Confidence Intervals: What 95% Means, Measured" (Statistics for Data Scientists, part 6).

Every number the article calls measured or computed comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python intervals.py all --out mine.json            # every stage, the article's budget (about 30 seconds)
    python intervals.py all --quick --out quick.json   # the reader's budget (about 6 seconds), noisier
    python intervals.py pfizer --out mine.json         # one stage

Stages:
    enumerate  the worked example: the exact coverage of five 95% intervals for a proportion at n = 20 and
               p = 0.1, outcome by outcome, and a simulation that measures the same coverage with its MCSE
    invert     an interval as the set of null values a test does not reject: the p-value functions of the Wald,
               score and exact tests for 2 successes in 20, solved for their 0.05 crossings and matched to the
               closed forms, to statsmodels and to SciPy
    coverage   exact coverage curves of the five intervals at n = 50; the Wald interval's coverage as n grows at
               fixed p; mean coverage, its root mean square error and mean width over a uniform p (Agresti and
               Coull's Table 1, recomputed); the minimum coverage of each interval
    pfizer     the BNT162b2 trial: vaccine efficacy intervals by the Clopper-Pearson method adjusted for
               surveillance time, recomputed for every published row; the five intervals on the primary case
               split and their coverage at its size; the severe-case split, its arm-by-arm Poisson intervals and
               its exact conditional p-value
    overlap    what two overlapping 95% intervals say about a difference: Schenker and Gentleman's error rate of
               the overlap rule, the interval level that makes it a 5% test, its power, and a simulation
    tcoverage  the one-sample t-interval for a mean on a real, heavily skewed population (customer spend):
               coverage across n, which side the misses fall on, and coverage by interval width, beside a normal
               population

Coverage of a binomial interval is computed exactly, by summing the binomial probabilities of the outcomes whose
interval contains p; nothing there is simulated. Every simulated quantity is printed as estimate +- MCSE (its Monte
Carlo standard error) with the number of replications R. Every stage draws from its own stream,
SeedSequence([stage, sub-stream, seed]), so stages can run alone and repeat to the bit with the same NumPy version.
"""

import argparse
import csv
import datetime
import hashlib
import inspect
import json
import math
import pathlib
import platform
import time

import numpy as np
import scipy
from scipy import integrate, optimize, special, stats

HERE = pathlib.Path(__file__).resolve().parent
SPEND_CSV = HERE / "data" / "online_retail_customer_spend.csv"
TRIAL_CSV = HERE / "data" / "bnt162b2_case_splits.csv"
STAGES = ("enumerate", "invert", "coverage", "pfizer", "overlap", "tcoverage")

# Replications. The article quotes FULL; --quick is the reader's first run. Exact computations ignore the budget.
FULL = dict(enum_mc=1_000_000, cov_mc=200_000, overlap_mc=200_000, t_normal=200_000,
            t_reps={10: 200_000, 30: 200_000, 100: 200_000, 300: 100_000, 1000: 60_000, 3000: 40_000, 10000: 20_000})
QUICK = {k: ({n: r // 10 for n, r in v.items()} if isinstance(v, dict) else v // 10) for k, v in FULL.items()}
DRAWS_PER_BLOCK = 2_000_000                    # fixed, so results do not depend on the machine
Z975 = float(stats.norm.isf(0.025))            # 1.959964, the two-sided 95% point of the standard normal
NOMINAL = 0.95

EXAMPLE_N, EXAMPLE_P = 20, 0.1                 # the worked example: 20 audited predictions, a true error rate of 10%
INVERT_X = 2                                   # the outcome whose p-value functions the invert stage draws
CURVE_N = 50                                   # the n of the coverage curves


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


def pm(est, mcse, nd=2):
    """'87.60% +- 0.03' for a share."""
    return f"{100 * est:.{nd}f}% +- {100 * mcse:.{nd}f}"


# ------------------------------------------------------------------------------- five intervals for a proportion
# Each takes the number of successes x (scalar or array) and the number of trials n and returns (lower, upper).
def wald(x, n, z=Z975):
    """p-hat +- z * sqrt(p-hat (1 - p-hat) / n): the inverted Wald test, with the standard error at the estimate."""
    p = np.asarray(x, dtype=float) / n
    h = z * np.sqrt(p * (1 - p) / n)
    return p - h, p + h


def wilson(x, n, z=Z975):
    """The inverted score test: the p0 with |p-hat - p0| <= z sqrt(p0 (1 - p0) / n), solved in closed form."""
    p = np.asarray(x, dtype=float) / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / d
    return c - h, c + h


def agresti_coull(x, n, z=Z975):
    """The Wald form around (x + z^2/2) / (n + z^2): about two successes and two failures added at 95%."""
    nt = n + z**2
    pt = (np.asarray(x, dtype=float) + z**2 / 2) / nt
    h = z * np.sqrt(pt * (1 - pt) / nt)
    return pt - h, pt + h


def clopper_pearson(x, n, alpha=0.05):
    """The inverted pair of one-sided exact binomial tests, from beta quantiles; 0 at x = 0 and 1 at x = n."""
    x = np.asarray(x, dtype=float)
    lo = np.where(x == 0, 0.0, stats.beta.ppf(alpha / 2, np.where(x == 0, 1, x), n - x + 1))
    hi = np.where(x == n, 1.0, stats.beta.ppf(1 - alpha / 2, x + 1, np.where(x == n, 1, n - x)))
    return lo, hi


def clopper_pearson_draft(x, n, alpha=0.05):
    """An earlier draft of clopper_pearson(), kept for exercise E4."""
    x = np.asarray(x, dtype=float)
    return stats.beta.ppf(alpha / 2, x, n - x + 1), stats.beta.ppf(1 - alpha / 2, x + 1, n - x)


def jeffreys(x, n, alpha=0.05):
    """The equal-tailed interval of the Beta(x + 1/2, n - x + 1/2) posterior; 0 at x = 0 and 1 at x = n."""
    x = np.asarray(x, dtype=float)
    lo = np.where(x == 0, 0.0, stats.beta.ppf(alpha / 2, x + 0.5, n - x + 0.5))
    hi = np.where(x == n, 1.0, stats.beta.ppf(1 - alpha / 2, x + 0.5, n - x + 0.5))
    return lo, hi


METHODS = {"wald": wald, "wilson": wilson, "agresti_coull": agresti_coull, "clopper_pearson": clopper_pearson,
           "jeffreys": jeffreys}
NAMES = {"wald": "Wald", "wilson": "Wilson", "agresti_coull": "Agresti-Coull", "clopper_pearson": "Clopper-Pearson",
         "jeffreys": "Jeffreys"}


def binom_pmf_grid(n, p):
    """P(X = x) for x = 0..n (columns) at each p (rows), from log-gamma; the same numbers as stats.binom.pmf, faster."""
    x = np.arange(n + 1)
    p = np.atleast_1d(np.asarray(p, dtype=float))[:, None]
    log_c = special.gammaln(n + 1) - special.gammaln(x + 1) - special.gammaln(n - x + 1)
    return np.exp(log_c + special.xlogy(x, p) + special.xlog1py(n - x, -p))


def coverage(method, n, p):
    """Exact coverage at each p: the sum of P(X = x) over the outcomes x whose interval contains p."""
    x = np.arange(n + 1)
    lo, hi = method(x, n)
    p = np.atleast_1d(np.asarray(p, dtype=float))
    contains = (lo[None, :] <= p[:, None]) & (p[:, None] <= hi[None, :])
    return (binom_pmf_grid(n, p) * contains).sum(axis=1)


def mean_coverage_uniform(method, n):
    """Exact mean coverage over p ~ Uniform(0, 1): P(X = x) integrated over [L(x), U(x)] is an incomplete beta / (n + 1)."""
    x = np.arange(n + 1)
    lo, hi = (np.clip(v, 0, 1) for v in method(x, n))
    return float(np.sum(special.betainc(x + 1, n - x + 1, hi) - special.betainc(x + 1, n - x + 1, lo)) / (n + 1))


def rmse_about_nominal(method, n, level=NOMINAL):
    """Exact sqrt of the integral of (coverage(p) - level)^2 over p in (0, 1): coverage squared is a double sum of
    products of binomial probabilities, each integrating to a beta function over the overlap of two intervals."""
    x = np.arange(n + 1)
    lo, hi = (np.clip(v, 0, 1) for v in method(x, n))
    X, Y = np.meshgrid(x, x, indexing="ij")
    a, b = np.maximum(lo[:, None], lo[None, :]), np.minimum(hi[:, None], hi[None, :])
    ok = b > a
    s, t = X + Y + 1, 2 * n - X - Y + 1
    log_c = (2 * special.gammaln(n + 1) - special.gammaln(X + 1) - special.gammaln(n - X + 1)
             - special.gammaln(Y + 1) - special.gammaln(n - Y + 1) + special.betaln(s, t))
    inc = special.betainc(s, t, np.where(ok, b, 0.0)) - special.betainc(s, t, np.where(ok, a, 0.0))
    c2 = float(np.sum(np.where(ok, np.exp(log_c) * inc, 0.0)))
    c1 = mean_coverage_uniform(method, n)
    return math.sqrt(max(c2 - 2 * level * c1 + level**2, 0.0))


def mean_width_uniform(method, n):
    """Mean expected width over p ~ Uniform(0, 1): every outcome has probability 1 / (n + 1) on average."""
    x = np.arange(n + 1)
    lo, hi = (np.clip(v, 0, 1) for v in method(x, n))
    return float(np.mean(hi - lo))


# ------------------------------------------------------------------------------- enumerate
def stage_enumerate(cfg, args):
    n, p = args.n, args.p
    x = np.arange(n + 1)
    pmf = stats.binom.pmf(x, n, p)
    out = dict(n=n, p=p, pmf=pmf, methods={})
    print(f"[enumerate] {n} trials, true p = {p}: P(X = x) for x = 0..9: " + ", ".join(f"{v:.4f}" for v in pmf[:10])
          + f"; P(X >= 10) = {pmf[10:].sum():.2e}")
    for key, f in METHODS.items():
        lo, hi = f(x, n)
        contains = (lo <= p) & (p <= hi)
        cov = float(pmf[contains].sum())
        covered = [int(v) for v in x[contains]]
        out["methods"][key] = dict(lower=lo, upper=hi, contains=contains, coverage=cov, covered_x=covered)
        rng_txt = f"x = {covered[0]}..{covered[-1]}" if covered == list(range(covered[0], covered[-1] + 1)) else str(covered)
        print(f"[enumerate] {NAMES[key]:16s} contains {p} for {rng_txt}: coverage {cov:.4f} (nominal 0.95)")
    w = out["methods"]["wald"]
    for xi in range(0, min(n, 7) + 1):
        print(f"[enumerate]   x = {xi}: P = {pmf[xi]:.4f}  Wald ({w['lower'][xi]:+.4f}, {w['upper'][xi]:.4f})  "
              f"Wilson ({out['methods']['wilson']['lower'][xi]:.4f}, {out['methods']['wilson']['upper'][xi]:.4f})  "
              f"Clopper-Pearson ({out['methods']['clopper_pearson']['lower'][xi]:.4f}, {out['methods']['clopper_pearson']['upper'][xi]:.4f})")
    # The same coverage measured by simulation: draw X, look up its interval, count how often it contains p.
    R = cfg["enum_mc"]
    draws = stream(args.seed, "enumerate").binomial(n, p, size=R)
    sim = {}
    for key, m in out["methods"].items():
        est = float(np.mean(m["contains"][draws]))
        sim[key] = dict(estimate=est, mcse=mcse_share(est, R), z=(est - m["coverage"]) / mcse_share(m["coverage"], R))
    out["simulated"] = dict(R=R, **sim)
    print("[enumerate] simulated, R = {:,}: ".format(R) + "; ".join(
        f"{NAMES[k]} {pm(v['estimate'], v['mcse'])}" for k, v in sim.items()))
    return out


# ------------------------------------------------------------------------------- invert
def pvalue_wald(x, n, p0):
    ph = x / n
    return 2 * stats.norm.sf(np.abs(ph - p0) / np.sqrt(ph * (1 - ph) / n))


def pvalue_score(x, n, p0):
    return 2 * stats.norm.sf(np.abs(x / n - p0) / np.sqrt(p0 * (1 - p0) / n))


def pvalue_exact(x, n, p0):
    """Two-sided p-value of the exact binomial test as twice the smaller tail; Clopper-Pearson inverts this one."""
    return np.minimum(1.0, 2 * np.minimum(stats.binom.cdf(x, n, p0), stats.binom.sf(x - 1, n, p0)))


def stage_invert(cfg, args):
    x, n = INVERT_X, EXAMPLE_N
    ph = x / n
    grid = np.linspace(0.0005, 0.5, 1000)
    curves = {"wald": pvalue_wald(x, n, grid), "score": pvalue_score(x, n, grid), "exact": pvalue_exact(x, n, grid)}
    # Solve each p-value function for its 0.05 crossings on either side of p-hat.
    roots = {}
    for key, fn in (("score", pvalue_score), ("exact", pvalue_exact)):
        g = lambda p0, fn=fn: float(fn(x, n, p0)) - 0.05
        roots[key] = (optimize.brentq(g, 1e-9, ph - 1e-9, xtol=1e-14), optimize.brentq(g, ph + 1e-9, 1 - 1e-9, xtol=1e-14))
    wl = wald(x, n)
    roots["wald"] = (float(wl[0]), float(wl[1]))               # its p-value function is symmetric and crosses here
    closed = {"score": tuple(float(v) for v in wilson(x, n)), "exact": tuple(float(v) for v in clopper_pearson(x, n))}
    gaps = {k: max(abs(roots[k][0] - closed[k][0]), abs(roots[k][1] - closed[k][1])) for k in closed}
    print(f"[invert] {x} successes in {n}: the 0.05 crossings of each test's p-value function")
    for key, label in (("wald", "Wald test"), ("score", "score test"), ("exact", "exact test")):
        print(f"[invert]   {label:10s} ({roots[key][0]:+.6f}, {roots[key][1]:.6f})"
              + (f"  closed form ({closed[key][0]:.6f}, {closed[key][1]:.6f}), gap {gaps[key]:.1e}" if key in closed else ""))
    # Match the five implementations to the libraries for every x and n from 1 to 100.
    from statsmodels.stats.proportion import proportion_confint
    sm_names = {"wald": "normal", "wilson": "wilson", "agresti_coull": "agresti_coull", "clopper_pearson": "beta",
                "jeffreys": "jeffreys"}
    lib = {}
    for key, f in METHODS.items():
        worst = 0.0
        for nn in range(1, 101):
            xs = np.arange(nn + 1)
            lo, hi = f(xs, nn)
            slo, shi = proportion_confint(xs, nn, 0.05, method=sm_names[key])
            if key in ("wald", "agresti_coull", "wilson"):
                lo, hi = np.clip(lo, 0, 1), np.clip(hi, 0, 1)            # statsmodels clips these three to [0, 1]
            inner = slice(1, nn) if key == "jeffreys" else slice(0, nn + 1)
            if lo[inner].size:
                worst = max(worst, float(np.max(np.abs(lo[inner] - slo[inner]))), float(np.max(np.abs(hi[inner] - shi[inner]))))
        lib[key] = worst
    jl = proportion_confint(0, n, 0.05, method="jeffreys")
    sp = {}
    for key, meth in (("clopper_pearson", "exact"), ("wilson", "wilson")):
        worst = 0.0
        for nn in (1, 2, 5, 10, 20, 50, 170):                  # SciPy's interval is scalar and slow, so a sample of n
            for xx in range(nn + 1):
                ci = stats.binomtest(xx, nn).proportion_ci(0.95, method=meth)
                lo, hi = METHODS[key](xx, nn)
                worst = max(worst, abs(float(ci.low) - float(lo)), abs(float(ci.high) - float(hi)))
        sp[key] = worst
    defaults = dict(statsmodels=inspect.signature(proportion_confint).parameters["method"].default,
                    scipy=inspect.signature(type(stats.binomtest(1, 2)).proportion_ci).parameters["method"].default)
    print("[invert] largest gap to statsmodels proportion_confint over n = 1..100: " + ", ".join(
        f"{NAMES[k]} {v:.1e}" for k, v in lib.items()) + " (Jeffreys at 0 < x < n)")
    print(f"[invert] statsmodels' Jeffreys at x = 0 of {n}: lower limit {jl[0]:.2e}, not 0; ours sets 0, the convention of the exact interval")
    print("[invert] largest gap to scipy.stats.binomtest(...).proportion_ci, n = 1, 2, 5, 10, 20, 50, 170 and every x: " + ", ".join(f"{NAMES[k]} {v:.1e}" for k, v in sp.items()))
    print(f"[invert] defaults: statsmodels proportion_confint method = {defaults['statsmodels']!r}, "
          f"SciPy proportion_ci method = {defaults['scipy']!r}")
    return dict(x=x, n=n, grid=grid, curves=curves, roots=roots, closed=closed, gaps=gaps, statsmodels_gap=lib,
                scipy_gap=sp, statsmodels_jeffreys_x0=jl, defaults=defaults)


# ------------------------------------------------------------------------------- coverage
AC_TABLE1 = {  # Agresti and Coull (1998), Table 1: mean coverage over a uniform p, and root mean square error about .95
    "clopper_pearson": {5: (0.990, 0.041), 15: (0.980, 0.031), 30: (0.973, 0.026), 50: (0.969, 0.022), 100: (0.965, 0.017)},
    "wilson": {5: (0.955, 0.029), 15: (0.953, 0.019), 30: (0.952, 0.014), 50: (0.952, 0.012), 100: (0.951, 0.008)},
    "wald": {5: (0.641, 0.400), 15: (0.819, 0.238), 30: (0.875, 0.170), 50: (0.901, 0.133), 100: (0.922, 0.094)},
}


def add_two(x, n, z=Z975):
    """Agresti and Coull's 'add two successes and two failures' interval: the Wald form around (x + 2) / (n + 4)."""
    nt = n + 4
    pt = (np.asarray(x, dtype=float) + 2) / nt
    h = z * np.sqrt(pt * (1 - pt) / nt)
    return pt - h, pt + h


def stage_coverage(cfg, args):
    out = {}
    n = CURVE_N
    fig_p = np.round(np.arange(1, 1000) / 1000, 3)
    fine = np.linspace(0.0005, 0.9995, 19991)
    out["curves"] = dict(n=n, p=fig_p, **{k: coverage(f, n, fig_p) for k, f in METHODS.items()})
    summary = {}
    for key, f in METHODS.items():
        c = coverage(f, n, fine)
        j = int(np.argmin(c))
        summary[key] = dict(min=float(c[j]), at_p=float(fine[j]), mean=mean_coverage_uniform(f, n),
                            rmse=rmse_about_nominal(f, n), width=mean_width_uniform(f, n),
                            share_below_093=float(np.mean(c < 0.93)), share_at_least_095=float(np.mean(c >= 0.95)))
    wil = summary["wilson"]["width"]
    for key in summary:
        summary[key]["width_vs_wilson"] = summary[key]["width"] / wil
    out["n50"] = summary
    print(f"[coverage] n = {n}, exact over p in (0.0005, 0.9995): min, where, mean over a uniform p, share of p below 0.93, mean width")
    for key, s in summary.items():
        print(f"[coverage]   {NAMES[key]:16s} min {s['min']:.4f} at p = {s['at_p']:.4f}; mean {s['mean']:.4f}; "
              f"below 0.93 on {100 * s['share_below_093']:.1f}% of p; width {s['width']:.4f} ({s['width_vs_wilson']:.3f} x Wilson)")
    cp_ok = summary["clopper_pearson"]["min"] >= NOMINAL - 1e-12
    print(f"[coverage] guarantee check: Clopper-Pearson covers at least 0.95 at every p on the grid: {'yes' if cp_ok else 'NO'}")
    if not cp_ok:
        lo0, hi0 = METHODS["clopper_pearson"](0, n)
        print(f"[coverage]   Clopper-Pearson interval printed for x = 0 of {n}: ({float(lo0)}, {float(hi0):.4f})")
    out["guarantee_ok"] = cp_ok

    # The Wald interval at fixed p as n grows, beside Wilson.
    ns = np.arange(10, 1001)
    walk = {}
    for p in (0.1, 0.05, 0.2, 0.5):
        wc = np.array([coverage(wald, int(m), p)[0] for m in ns])
        drops = np.diff(wc)
        j = int(np.argmin(drops))
        walk[str(p)] = dict(n=ns, wald=wc, min=float(wc.min()), n_at_min=int(ns[np.argmin(wc)]), max=float(wc.max()),
                            biggest_drop=dict(n_from=int(ns[j]), n_to=int(ns[j + 1]), cov_from=float(wc[j]), cov_to=float(wc[j + 1])),
                            share_below_094=float(np.mean(wc < 0.94)),
                            at={str(m): float(wc[m - 10]) for m in (29, 30, 40, 50, 100, 200, 500, 1000)})
        if p == 0.1:
            walk[str(p)]["wilson"] = np.array([coverage(wilson, int(m), p)[0] for m in ns])
        b = walk[str(p)]["biggest_drop"]
        print(f"[coverage] Wald at p = {p}, n = 10..1000: from {wc.min():.4f} (n = {ns[np.argmin(wc)]}) to {wc.max():.4f}; "
              f"below 0.94 for {100 * np.mean(wc < 0.94):.1f}% of n; biggest one-step drop n = {b['n_from']} -> {b['n_to']}: "
              f"{b['cov_from']:.4f} -> {b['cov_to']:.4f}")
    w01 = walk["0.1"]
    print(f"[coverage]   p = 0.1: n = 50 (np = 5, the textbook threshold) {w01['at']['50']:.4f}; n = 100 {w01['at']['100']:.4f}; "
          f"n = 1000 {w01['at']['1000']:.4f}; Wilson across n = 10..1000 from {w01['wilson'].min():.4f} to {w01['wilson'].max():.4f}")
    out["wald_vs_n"] = walk

    # The textbook rule (np >= 5 and n(1 - p) >= 5): the worst Wald coverage it allows, n = 10..300.
    worst = (2.0, 0, 0.0)
    for m in range(10, 301):
        ps = np.linspace(5 / m, 1 - 5 / m, 241)
        c = coverage(wald, m, ps)
        j = int(np.argmin(c))
        if c[j] < worst[0]:
            worst = (float(c[j]), m, float(ps[j]))
    out["textbook_rule_worst"] = dict(coverage=worst[0], n=worst[1], p=worst[2])
    print(f"[coverage] Wald under np >= 5 and n(1 - p) >= 5, n = 10..300: worst coverage {worst[0]:.4f} at n = {worst[1]}, p = {worst[2]:.3f}")

    # Agresti and Coull's Table 1, recomputed exactly, and the other two intervals beside it.
    t1 = {}
    for key, f in METHODS.items():
        t1[key] = {str(m): dict(mean=mean_coverage_uniform(f, m), rmse=rmse_about_nominal(f, m)) for m in (5, 15, 30, 50, 100)}
    pairs = [(k, m, v) for k, rows in AC_TABLE1.items() for m, v in rows.items()]
    mean_ok = sum(round(t1[k][str(m)]["mean"], 3) == v[0] for k, m, v in pairs)
    rmse_ok = sum(round(t1[k][str(m)]["rmse"], 3) == v[1] for k, m, v in pairs)
    rmse_gap = max(abs(t1[k][str(m)]["rmse"] - v[1]) for k, m, v in pairs)
    out["ac_table1"] = dict(computed=t1, printed={k: {str(m): v for m, v in r.items()} for k, r in AC_TABLE1.items()},
                            means_matching=int(mean_ok), rmse_matching=int(rmse_ok), cells_each=len(pairs), rmse_largest_gap=rmse_gap)
    print(f"[coverage] Agresti and Coull's Table 1 over a uniform p: {mean_ok} of {len(pairs)} mean coverages reproduce to the printed "
          f"digit; {rmse_ok} of {len(pairs)} root mean square errors do, the largest gap {rmse_gap:.4f} (computed here by exact integration)")
    for key in METHODS:
        print(f"[coverage]   {NAMES[key]:16s} mean coverage at n = 5, 15, 30, 50, 100: "
              + ", ".join(f"{t1[key][str(m)]['mean']:.3f}" for m in (5, 15, 30, 50, 100)))

    # Mean coverage and mean width as n grows, for the figure.
    nn = np.array([5, 7, 10, 15, 20, 30, 40, 50, 70, 100, 150, 200])
    out["by_n"] = dict(n=nn, **{k: dict(mean=[mean_coverage_uniform(f, int(m)) for m in nn],
                                        width=[mean_width_uniform(f, int(m)) for m in nn]) for k, f in METHODS.items()})

    # Agresti and Coull's other printed claims: the add-two interval's minimum, and Wilson's dip that never closes.
    mins = {m: float(coverage(add_two, m, fine).min()) for m in range(10, 101)}
    out["add_two"] = dict(min_n10=mins[10], min_n11_100=min(v for k, v in mins.items() if k > 10))
    big = 10_000
    pp = np.linspace(0.01 / big, 5.0 / big, 4000)
    xx = np.arange(0, 60)
    lo, hi = wilson(xx, big)
    cw = (stats.binom.pmf(xx[None, :], big, pp[:, None]) * ((lo[None, :] <= pp[:, None]) & (pp[:, None] <= hi[None, :]))).sum(1)
    out["wilson_dip"] = dict(n=big, min=float(cw.min()), at_np=float(pp[np.argmin(cw)] * big))
    print(f"[coverage] add-two interval: minimum coverage {mins[10]:.4f} at n = 10 and {out['add_two']['min_n11_100']:.4f} over n = 11..100; "
          f"Wilson at n = {big:,}: minimum {cw.min():.4f} at np = {pp[np.argmin(cw)] * big:.3f}")

    # Simulation measures the same thing, with an error bar: Wald at n = 50, p = 0.1.
    R = cfg["cov_mc"]
    xs = stream(args.seed, "coverage").binomial(n, 0.1, size=R)
    lo, hi = wald(xs, n)
    est = float(np.mean((lo <= 0.1) & (0.1 <= hi)))
    exact = float(coverage(wald, n, 0.1)[0])
    out["simulated_check"] = dict(n=n, p=0.1, R=R, estimate=est, mcse=mcse_share(est, R), exact=exact)
    print(f"[coverage] simulated Wald coverage at n = {n}, p = 0.1: {pm(est, mcse_share(est, R))} (R = {R:,}); exact {exact:.4f}")
    return out


# ------------------------------------------------------------------------------- pfizer
def read_trial():
    with TRIAL_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    for r in rows:
        for k in ("cases_vaccine", "cases_placebo", "at_risk_vaccine", "at_risk_placebo"):
            r[k] = int(r[k])
        for k in ("surveillance_vaccine", "surveillance_placebo", "published_ve", "published_lower", "published_upper"):
            r[k] = float(r[k])
    return rows


def ve_from_share(pi, r):
    """Vaccine efficacy 1 - IRR from the vaccine group's share of cases pi, with r = vaccine / placebo surveillance time:
    conditional on the total, the vaccine count is Binomial(cases, pi), pi = IRR r / (IRR r + 1), so IRR = pi / ((1 - pi) r)."""
    with np.errstate(divide="ignore"):
        return 1 - np.asarray(pi) / ((1 - np.asarray(pi)) * r)


def ve_interval(xv, xp, r, method=clopper_pearson):
    lo, hi = method(xv, xv + xp)
    return float(ve_from_share(hi, r)), float(ve_from_share(np.clip(lo, 0, 1), r))     # a high share is a low efficacy


def garwood(k, alpha=0.05):
    """Exact (Garwood) interval for a Poisson mean from k events, by chi-square quantiles."""
    lo = 0.0 if k == 0 else stats.chi2.ppf(alpha / 2, 2 * k) / 2
    return lo, stats.chi2.ppf(1 - alpha / 2, 2 * k + 2) / 2


def stage_pfizer(cfg, args):
    rows = read_trial()
    out = dict(rows=[])
    exact_matches = within_rounding = n_ci = 0
    for r in rows:
        xv, xp, tv, tp = r["cases_vaccine"], r["cases_placebo"], r["surveillance_vaccine"], r["surveillance_placebo"]
        ve = 1 - (xv / tv) / (xp / tp)
        rec = dict(table=r["table"], source=r["source"], endpoint=r["endpoint"], subgroup=r["subgroup"], cases=(xv, xp),
                   times=(tv, tp), interval=r["interval"], ve=ve,
                   published=(r["published_ve"], r["published_lower"], r["published_upper"]))
        if r["interval"] == "clopper_pearson":
            n_ci += 1
            lo, hi = ve_interval(xv, xp, tv / tp)
            # Times are printed to three decimals; efficacy limits move monotonically with r, so the extremes of r bound them.
            r_lo, r_hi = (tv - 5e-4) / (tp + 5e-4), (tv + 5e-4) / (tp - 5e-4)
            band = [ve_interval(xv, xp, rr) + (1 - xv / (xp * rr),) for rr in (r_lo, r_hi)]     # (lower, upper, estimate)
            mine = (round(100 * ve, 1), round(100 * lo, 1), round(100 * hi, 1))
            match = mine == rec["published"]
            inside = all(min(100 * b[i] for b in band) - 0.05 - 1e-9 <= pub <= max(100 * b[i] for b in band) + 0.05 + 1e-9
                         for i, pub in zip((2, 0, 1), rec["published"]))
            exact_matches += match
            within_rounding += inside
            rec.update(ci=(lo, hi), matches_printed=match, within_rounding=inside)
            print(f"[pfizer] table {r['table']} {r['subgroup']:26s} {xv:2d} vs {xp:3d}: VE {100 * ve:5.1f} ({100 * lo:6.1f}, {100 * hi:5.1f}); "
                  f"printed {rec['published'][0]:5.1f} ({rec['published'][1]:6.1f}, {rec['published'][2]:5.1f})"
                  f"{'' if match else '  <- differs; inside the rounding range' if inside else '  <- DIFFERS beyond rounding'}")
        else:
            print(f"[pfizer] table {r['table']} {r['endpoint'][:40]:40s} {xv} vs {xp}: VE {100 * ve:.1f}; printed credible interval "
                  f"({rec['published'][1]}, {rec['published'][2]}) -- a posterior statement, not recomputed here")
        out["rows"].append(rec)
    out["summary"] = dict(confidence_rows=n_ci, match_printed=exact_matches, within_rounding=within_rounding)
    print(f"[pfizer] {exact_matches} of {n_ci} Clopper-Pearson rows match every printed digit; {within_rounding} of {n_ci} lie within "
          "what three-decimal surveillance times allow")

    # The primary split under the five intervals.
    xv, xp = 8, 162
    r = 2.214 / 2.222
    n = xv + xp
    prim = {}
    for key, f in METHODS.items():
        lo, hi = f(xv, n)
        prim[key] = dict(share=(float(lo), float(hi)), ve=ve_interval(xv, xp, r, f))
        prim[key]["width_ve"] = prim[key]["ve"][1] - prim[key]["ve"][0]
    out["primary"] = dict(cases=(xv, xp), r=r, ve=1 - (xv / 2.214) / (xp / 2.222), methods=prim)
    print(f"[pfizer] primary split {xv} of {n}, share {xv / n:.4f}: " + "; ".join(
        f"{NAMES[k]} VE ({100 * v['ve'][0]:.2f}, {100 * v['ve'][1]:.2f})" for k, v in prim.items()))
    # How each interval's coverage behaves at this n for shares near the observed one.
    shares = np.round(np.arange(0.01, 0.1201, 0.0005), 4)
    cov170 = {k: coverage(f, n, shares) for k, f in METHODS.items()}
    out["coverage_at_170"] = dict(share=shares, **cov170,
                                  summary={k: dict(min=float(v.min()), mean=float(v.mean())) for k, v in cov170.items()})
    print(f"[pfizer] exact coverage at n = {n} for a true share from 0.01 to 0.12: " + "; ".join(
        f"{NAMES[k]} min {v.min():.4f}, mean {v.mean():.4f}" for k, v in cov170.items()))

    # The severe-case split after dose 1 (FDA Table 12): 1 vaccine case in 4.021, 9 placebo cases in 4.006 thousand person-years.
    sv, sp_, tv, tp = 1, 9, 4.021, 4.006
    arms = {}
    for name, k, t in (("vaccine", sv, tv), ("placebo", sp_, tp)):
        lo, hi = garwood(k)
        arms[name] = dict(cases=k, time=t, rate=k / t, lower=lo / t, upper=hi / t)
    overlap = (arms["placebo"]["lower"], arms["vaccine"]["upper"])
    rr = tv / tp
    pi0 = rr / (1 + rr)                                         # the vaccine share under no efficacy
    lower_tail = float(stats.binom.cdf(sv, sv + sp_, pi0))
    p_two = min(1.0, 2 * min(lower_tail, float(stats.binom.sf(sv - 1, sv + sp_, pi0))))
    mid_p = 2 * float(stats.binom.cdf(sv - 1, sv + sp_, pi0) + 0.5 * stats.binom.pmf(sv, sv + sp_, pi0))
    p_minlike = float(stats.binomtest(sv, sv + sp_, pi0).pvalue)   # SciPy's (and R's) two-sided rule: outcomes no likelier than x
    lo, hi = ve_interval(sv, sp_, rr)
    out["severe"] = dict(arms=arms, overlap=overlap, overlap_width=overlap[1] - overlap[0], pi0=pi0, p_lower_tail=lower_tail,
                         p_two_sided=p_two, mid_p=mid_p, p_scipy_binomtest=p_minlike, ve=1 - (sv / tv) / (sp_ / tp), ve_ci=(lo, hi))
    print(f"[pfizer] severe after dose 1: vaccine {arms['vaccine']['rate']:.3f} ({arms['vaccine']['lower']:.3f}, {arms['vaccine']['upper']:.3f}) "
          f"and placebo {arms['placebo']['rate']:.3f} ({arms['placebo']['lower']:.3f}, {arms['placebo']['upper']:.3f}) per 1000 person-years; "
          f"the arms' 95% intervals overlap from {overlap[0]:.3f} to {overlap[1]:.3f}")
    print(f"[pfizer]   exact conditional test of no efficacy: P(X <= 1) = {lower_tail:.5f}, two-sided p = {p_two:.4f} (mid-p {mid_p:.4f}); "
          f"VE {100 * out['severe']['ve']:.1f} ({100 * lo:.1f}, {100 * hi:.1f})")
    print(f"[pfizer]   scipy.stats.binomtest reports p = {p_minlike:.4f}: it sums the outcomes no more likely than the observed one, "
          "while the Clopper-Pearson interval inverts twice the smaller tail")

    if args.split:
        a, b = args.split
        lo, hi = ve_interval(a, b, r)
        out["split"] = dict(cases=(a, b), r=r, ve=1 - (a / b) / r, ci=(lo, hi))
        print(f"[pfizer] --split {a} {b}, with the primary endpoint's surveillance ratio {r:.5f}: VE {100 * (1 - (a / b) / r):.1f} "
              f"({100 * lo:.1f}, {100 * hi:.1f})")
    return out


# ------------------------------------------------------------------------------- overlap
def alpha_overlap(k, z=Z975):
    """Schenker and Gentleman's large-sample type I error of 'reject when the two intervals do not overlap', k = SE ratio."""
    return 2 * stats.norm.sf(z * (1 + k) / np.sqrt(1 + k**2))


def stage_overlap(cfg, args):
    out = {}
    ks = np.round(np.exp(np.linspace(0, math.log(20), 121)), 4)
    out["alpha_curve"] = dict(k=ks, alpha=alpha_overlap(ks))
    out["alpha_at"] = {str(k): float(alpha_overlap(k)) for k in (1, 2, 4, 10)}
    out["se_bars_alpha"] = float(alpha_overlap(1, z=1.0))
    z_star = Z975 / math.sqrt(2)                                # level whose intervals touch exactly when p = 0.05, at k = 1
    out["level_for_5pct"] = 1 - 2 * stats.norm.sf(z_star)
    out["level_for_5pct_k2"] = 1 - 2 * stats.norm.sf(Z975 * math.sqrt(5) / 3)
    out["arm_overlap_at_5pct"] = 2 - math.sqrt(2)               # overlap as a share of one arm when p = 0.05, k = 1
    out["p_touching"] = {"1": float(alpha_overlap(1)), "2": float(alpha_overlap(2))}
    out["p_half_arm"] = {"1": float(2 * stats.norm.sf(1.5 * Z975 / math.sqrt(2))),
                         "2": float(2 * stats.norm.sf((Z975 + 2 * Z975 - 0.75 * Z975) / math.sqrt(5)))}
    # Power, in units of the difference's standard error, for the standard test and the overlap rule (k = 1).
    d = np.round(np.linspace(0, 5, 201), 3)
    c_ov = 2 * Z975 / math.sqrt(2)
    c_83 = 2 * z_star / math.sqrt(2)
    out["power_curve"] = dict(delta=d, standard=stats.norm.sf(Z975 - d) + stats.norm.cdf(-Z975 - d),
                              overlap95=stats.norm.sf(c_ov - d) + stats.norm.cdf(-c_ov - d),
                              overlap83=stats.norm.sf(c_83 - d) + stats.norm.cdf(-c_83 - d))
    d80 = Z975 + stats.norm.isf(0.2)
    out["power_at_design80"] = dict(delta=d80, standard=float(stats.norm.sf(Z975 - d80) + stats.norm.cdf(-Z975 - d80)),
                                    overlap95=float(stats.norm.sf(c_ov - d80) + stats.norm.cdf(-c_ov - d80)))
    # Greenland et al.'s example: (1.04, 4.96) and (4.16, 19.84), normal with known variances.
    se1, se2 = (4.96 - 1.04) / (2 * Z975), (19.84 - 4.16) / (2 * Z975)
    zg = (12.0 - 3.0) / math.hypot(se1, se2)
    out["greenland"] = dict(se=(se1, se2), z=zg, p=float(2 * stats.norm.sf(zg)))
    print(f"[overlap] the overlap rule's type I error, equal standard errors: {out['alpha_at']['1']:.5f}; SE ratio 2: {out['alpha_at']['2']:.5f}; "
          f"4: {out['alpha_at']['4']:.4f}; 10: {out['alpha_at']['10']:.4f}; limit 0.05")
    print(f"[overlap] standard-error bars: {out['se_bars_alpha']:.4f}; intervals that make the rule a 5% test at k = 1: "
          f"{100 * out['level_for_5pct']:.1f}% (k = 2: {100 * out['level_for_5pct_k2']:.1f}%)")
    print(f"[overlap] at p = 0.05 and k = 1 two 95% intervals overlap by {out['arm_overlap_at_5pct']:.3f} of an arm; touching means "
          f"p = {out['p_touching']['1']:.4f} (k = 2: {out['p_touching']['2']:.4f}); overlap of half an average arm, p = "
          f"{out['p_half_arm']['1']:.4f} (k = 2: {out['p_half_arm']['2']:.4f})")
    print(f"[overlap] a design with 80% power for the standard test has {100 * out['power_at_design80']['overlap95']:.1f}% power under the overlap rule")
    print(f"[overlap] Greenland et al.'s (1.04, 4.96) and (4.16, 19.84): SEs {se1:.3f} and {se2:.3f}, z = {zg:.3f}, p = {out['greenland']['p']:.4f}")

    # Simulation: two independent normal samples of 10, t-intervals, the null true and an 80%-power alternative.
    R, m = cfg["overlap_mc"], 10
    rng = stream(args.seed, "overlap")
    t95, t83 = stats.t.ppf(0.975, m - 1), stats.t.ppf(1 - (1 - out["level_for_5pct"]) / 2, m - 1)
    d_alt = float(optimize.brentq(lambda dd: stats.nct.sf(stats.t.isf(0.025, 2 * m - 2), 2 * m - 2, dd * math.sqrt(m / 2))
                                  + stats.nct.sf(stats.t.isf(0.025, 2 * m - 2), 2 * m - 2, -dd * math.sqrt(m / 2)) - 0.8, 0.5, 3))
    sims = {}
    for label, shift in (("null", 0.0), ("alt80", d_alt)):
        x = rng.standard_normal((R, m)) + shift
        y = rng.standard_normal((R, m))
        mx, my = x.mean(1), y.mean(1)
        sx, sy = x.std(1, ddof=1) / math.sqrt(m), y.std(1, ddof=1) / math.sqrt(m)
        sp = np.sqrt((sx**2 + sy**2))                             # equal n: the pooled SE of the difference
        tstat = (mx - my) / sp
        rej_t = np.abs(tstat) > stats.t.ppf(0.975, 2 * m - 2)
        apart95 = np.abs(mx - my) > t95 * (sx + sy)
        apart83 = np.abs(mx - my) > t83 * (sx + sy)
        sims[label] = {k: dict(rate=float(v.mean()), mcse=mcse_share(float(v.mean()), R))
                       for k, v in (("t_test", rej_t), ("no_overlap_95", apart95), ("no_overlap_83", apart83))}
    out["simulation"] = dict(n_per_group=m, R=R, d_alt=d_alt, **sims)
    print(f"[overlap] simulated, 10 per group, R = {R:,}: with no difference, the t-test rejects {pm(**_r(sims['null']['t_test']))}; "
          f"95% intervals fail to overlap {pm(**_r(sims['null']['no_overlap_95']))}; "
          f"{100 * out['level_for_5pct']:.1f}% intervals {pm(**_r(sims['null']['no_overlap_83']))}")
    print(f"[overlap]   with a true difference of {d_alt:.3f} SD (80% power): t-test {pm(**_r(sims['alt80']['t_test']))}; "
          f"95% intervals apart {pm(**_r(sims['alt80']['no_overlap_95']))}; {100 * out['level_for_5pct']:.1f}% intervals apart "
          f"{pm(**_r(sims['alt80']['no_overlap_83']))}")
    return out


def _r(d):
    return dict(est=d["rate"], mcse=d["mcse"])


# ------------------------------------------------------------------------------- tcoverage
def read_spend():
    with SPEND_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    return np.array([float(r["net_spend_gbp"]) for r in rows])


def normal_decile_coverage(n, level=NOMINAL):
    """Exact coverage of the t-interval for a normal mean within each tenth of interval width. Width is proportional to s,
    V = (n - 1) s^2 / sigma^2 is chi-square(n - 1) and independent of the mean, and given V the interval covers with
    probability 2 Phi(t sqrt(V / (n - 1))) - 1."""
    tq = stats.t.ppf(1 - (1 - level) / 2, n - 1)
    edges = stats.chi2.ppf(np.linspace(0, 1, 11), n - 1)
    f = lambda v: (2 * stats.norm.cdf(tq * math.sqrt(v / (n - 1))) - 1) * stats.chi2.pdf(v, n - 1)
    return [integrate.quad(f, edges[i], edges[i + 1], limit=200)[0] / 0.1 for i in range(10)]


def stage_tcoverage(cfg, args):
    y = read_spend()
    N, mu = len(y), float(y.mean())
    sigma = float(y.std())
    gamma = float(np.mean((y - mu) ** 3) / sigma**3)
    print(f"[tcoverage] customer spend: N = {N:,} customers, mean {mu:,.2f}, SD {sigma:,.2f} (divisor N), skewness {gamma:.2f}")
    out = dict(population=dict(N=N, mean=mu, sd=sigma, skewness=gamma), by_n={})
    rng = stream(args.seed, "tcoverage")
    keep = {}
    for n, R in cfg["t_reps"].items():
        tq = stats.t.ppf(0.975, n - 1)
        below = above = 0
        widths, hits = [], []
        B = max(1, DRAWS_PER_BLOCK // n)
        for a in range(0, R, B):
            m = min(B, R - a)
            s = y[rng.integers(0, N, size=(m, n))]                 # with replacement: independent draws
            xb, h = s.mean(1), tq * s.std(1, ddof=1) / math.sqrt(n)
            below += int(np.sum(xb + h < mu))                       # the whole interval sits below the mean
            above += int(np.sum(xb - h > mu))
            if n in (30, 100):
                widths.append(2 * h)
                hits.append(np.abs(xb - mu) <= h)
        cov = 1 - (below + above) / R
        out["by_n"][str(n)] = dict(R=R, coverage=cov, mcse=mcse_share(cov, R), miss_below=below / R, miss_above=above / R,
                                   mcse_below=mcse_share(below / R, R))
        print(f"[tcoverage] n = {n:6,d}, R = {R:7,d}: coverage {pm(cov, mcse_share(cov, R))}; the interval lies below the mean "
              f"{100 * below / R:.2f}% and above it {100 * above / R:.3f}%")
        if n in (30, 100):
            keep[n] = (np.concatenate(widths), np.concatenate(hits))
    deciles = {}
    for n, (w, c) in keep.items():
        q = np.quantile(w, np.linspace(0, 1, 11))
        d = np.clip(np.searchsorted(q, w, side="right") - 1, 0, 9)
        rates = [float(c[d == i].mean()) for i in range(10)]
        counts = [int((d == i).sum()) for i in range(10)]
        deciles[str(n)] = dict(coverage=rates, mcse=[mcse_share(r_, k) for r_, k in zip(rates, counts)],
                               width_edges=q, sigma_over_sqrt_n=sigma / math.sqrt(n))
        print(f"[tcoverage] spend, n = {n}: coverage by tenth of interval width, narrowest first: "
              + ", ".join(f"{100 * v:.1f}%" for v in rates))
    out["deciles"] = deciles
    # A normal population: the same t-interval, exact overall, and by tenth of width (exact, then simulated).
    exact = {str(n): normal_decile_coverage(n) for n in (30, 100)}
    R = cfg["t_normal"]
    z = stream(args.seed, "tcoverage", 1).standard_normal((R, 30))
    xb, h = z.mean(1), stats.t.ppf(0.975, 29) * z.std(1, ddof=1) / math.sqrt(30)
    hit = np.abs(xb) <= h
    q = np.quantile(2 * h, np.linspace(0, 1, 11))
    d = np.clip(np.searchsorted(q, 2 * h, side="right") - 1, 0, 9)
    sim = [float(hit[d == i].mean()) for i in range(10)]
    out["normal"] = dict(exact_deciles=exact, simulated_n30=dict(R=R, overall=float(hit.mean()), mcse=mcse_share(float(hit.mean()), R),
                                                                 deciles=sim))
    print(f"[tcoverage] normal population, n = 30: exact by tenth of width " + ", ".join(f"{100 * v:.1f}%" for v in exact["30"])
          + f"; simulated overall {pm(float(hit.mean()), mcse_share(float(hit.mean()), R))} (R = {R:,})")
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
            "statsmodels": statsmodels.__version__, "intervals_py_sha1": sha1(pathlib.Path(__file__)),
            "data_sha1": {SPEND_CSV.name: sha1(SPEND_CSV), TRIAL_CSV.name: sha1(TRIAL_CSV)}, "budget": budget,
            "seed": args.seed, "replications": QUICK if args.quick else FULL,
            "flags": {"n": args.n, "p": args.p, "fault": args.fault, "split": args.split}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261031)
    parser.add_argument("--n", type=int, default=EXAMPLE_N, help="enumerate stage: the number of trials (default 20)")
    parser.add_argument("--p", type=float, default=EXAMPLE_P, help="enumerate stage: the true proportion (default 0.1)")
    parser.add_argument("--split", type=int, nargs=2, metavar=("VACCINE", "PLACEBO"), default=None,
                        help="pfizer stage: also analyse this case split, with the primary endpoint's surveillance times")
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of one interval")
    args = parser.parse_args()
    if args.fault:
        METHODS["clopper_pearson"] = clopper_pearson_draft
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, NumPy {prov['numpy']}, "
          f"SciPy {prov['scipy']}, statsmodels {prov['statsmodels']}; intervals.py {prov['intervals_py_sha1']}; budget {budget}, "
          f"seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"enumerate": stage_enumerate, "invert": stage_invert, "coverage": stage_coverage, "pfizer": stage_pfizer,
             "overlap": stage_overlap, "tcoverage": stage_tcoverage}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
