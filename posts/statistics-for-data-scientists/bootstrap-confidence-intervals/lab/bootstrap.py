#!/usr/bin/env python3
"""Lab for "The Bootstrap: From Percentile to BCa, and Where It Breaks" (Statistics for Data Scientists, part 7).

Every number the article calls measured or computed comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python bootstrap.py all --out mine.json            # every stage, the article's budget (about 3 minutes)
    python bootstrap.py all --quick --out quick.json   # the reader's budget (about 25 seconds), noisier
    python bootstrap.py example --out mine.json        # one stage

Stages:
    example    the worked example: the correlation of LSAT and GPA in 15 law schools, bootstrapped by hand; seven
               95% intervals with every intermediate (z0 from the share of replicates below r, the acceleration a
               from the jackknife); the true sampling distribution of r from the 82-school population it was drawn
               from; how much each endpoint moves with the number of replicates B
    reconcile  the from-scratch intervals matched to scipy.stats.bootstrap on the same resamples, and to R's
               boot.ci on R's own replicates (read from crosscheck-r.csv, written by crosscheck.R); the three BCa
               conventions in circulation, compared on one set of replicates
    coverage   each interval's actual coverage of the 82-school correlation, from fresh samples of 15
    spend      the same intervals for mean customer spend at n = 30 and 100, beside the t-interval of part 6
    maximum    the sample maximum: the bootstrap's point mass at the observed maximum, for five German tank serial
               numbers (part 3) and for uniform samples, and what it does to percentile, basic and BCa intervals
    heavy      the mean of infinite-variance (Pareto, tail index 1.5) data: lumpy bootstrap distributions, and
               coverage that stays short of 95% as n grows
    dependent  an autocorrelated series: resampling single observations destroys the dependence and the standard
               error with it

Every simulated quantity is printed as estimate +- MCSE (its Monte Carlo standard error) with its number of
replications R; B is the number of bootstrap replicates per interval. Every stage draws from its own stream,
SeedSequence([stage, sub-stream, seed]), so stages can run alone and repeat to the bit with the same NumPy version.
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
from math import comb

import numpy as np
import scipy
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
LAW_CSV = HERE / "data" / "law_school_82.csv"
SPEND_CSV = HERE / "data" / "online_retail_customer_spend.csv"
R_CSV = HERE / "crosscheck-r.csv"
STAGES = ("example", "reconcile", "coverage", "spend", "maximum", "heavy", "dependent")

# Replications. The article quotes FULL; --quick is the reader's first run. The worked example's own bootstrap
# (B_example replicates) is the same on both budgets, so its numbers match the article on either.
FULL = dict(B_example=10_000, true_reps=1_000_000, endpoint_repeats=200, cov_reps=20_000, cov_B=2_000,
            spend_reps={30: 20_000, 100: 8_000}, spend_B=2_000, max_reps=200_000,
            heavy_reps={30: 10_000, 100: 4_000, 300: 2_000, 1000: 2_000}, heavy_B=1_000, dep_reps=4_000, dep_B=1_000)
QUICK = {k: ({n: r // 10 for n, r in v.items()} if isinstance(v, dict) else
             (v if k == "B_example" or k.endswith("_B") else v // 10)) for k, v in FULL.items()}
DRAWS_PER_BLOCK = 4_000_000                    # fixed, so results do not depend on the machine
Z975 = float(stats.norm.isf(0.025))            # 1.959964
ALPHA = 0.025                                  # each tail of a 95% interval

TANK_SERIALS = np.array([58, 171, 272, 273, 303])   # part 3's seeded capture of k = 5 tanks
TANK_N = 342                                         # the true number of tanks
PARETO_ALPHA = 1.5                                   # tail index: finite mean 3, infinite variance
AR_PHI, AR_N = 0.5, 200                              # the dependent series

METHODS = ("normal", "percentile", "basic", "studentized", "studentized_z", "bca", "fisher_z")
NAMES = {"normal": "normal, bootstrap SE", "percentile": "percentile", "basic": "basic", "studentized": "studentized",
         "studentized_z": "studentized, z scale", "bca": "BCa", "fisher_z": "Fisher z (normal theory)",
         "t": "t-interval"}


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
    """A share as a percentage, rounded half up from its decimal value. Shares are counts over R, so exact ties such
    as 80.25% occur, and float formatting would round some of them down and others up."""
    return str((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def pm(est, mcse, nd=1):
    """'91.2% +- 0.2' for a share."""
    return f"{pc(est, nd)}% +- {pc(mcse, nd)}"


def fmt(iv, nd=4):
    return f"({iv[0]:.{nd}f}, {iv[1]:.{nd}f})"


# ------------------------------------------------------------------------------- quantiles, three conventions
def q_linear(sorted_rows, p):
    """Type 7 ('linear', NumPy's and SciPy's default) quantile. For one sorted vector, p may be a vector of
    probabilities; for sorted rows, p is a scalar or one probability per row."""
    sr = np.asarray(sorted_rows)
    B = sr.shape[-1]
    h = (B - 1) * np.asarray(p, dtype=float)
    lo = np.clip(np.floor(h).astype(int), 0, B - 1)
    hi = np.minimum(lo + 1, B - 1)
    f = h - lo
    if sr.ndim == 1:
        return sr[lo] * (1 - f) + sr[hi] * f
    lo_v = np.take_along_axis(sr, np.broadcast_to(lo, sr.shape[:-1])[..., None], -1)[..., 0]
    hi_v = np.take_along_axis(sr, np.broadcast_to(hi, sr.shape[:-1])[..., None], -1)[..., 0]
    return lo_v * (1 - f) + hi_v * f


def q_inverse_cdf(sorted_values, p):
    """Type 1: the smallest value with empirical cdf >= p (R's quantile(type = 1), as in bootstrap::bcanon)."""
    B = len(sorted_values)
    k = np.clip(np.ceil(B * np.asarray(p, dtype=float)).astype(int), 1, B)
    return sorted_values[k - 1]


def q_norm_inter(sorted_values, p):
    """R boot's norm.inter: the (B + 1)p-th order statistic, interpolated on the normal quantile scale."""
    B = len(sorted_values)
    out = []
    for a in np.atleast_1d(p):
        rk = (B + 1) * a
        k = int(math.trunc(rk))
        if k == rk and 1 <= k <= B:
            out.append(sorted_values[k - 1])
        elif k <= 0:
            out.append(sorted_values[0])
        elif k >= B:
            out.append(sorted_values[-1])
        else:
            t1, t2, t3 = stats.norm.ppf(a), stats.norm.ppf(k / (B + 1)), stats.norm.ppf((k + 1) / (B + 1))
            out.append(sorted_values[k - 1] + (t1 - t2) / (t3 - t2) * (sorted_values[k] - sorted_values[k - 1]))
    return np.array(out)


# ------------------------------------------------------------------------------- the correlation and its pieces
def corr_and_var(x, y):
    """The correlation along the last axis, and its nonparametric delta-method variance sum(L^2)/n^2, where
    L = xs*ys - r (xs^2 + ys^2)/2 are the empirical influence values (xs, ys standardized with divisor n)."""
    n = x.shape[-1]
    xm = x - x.mean(-1, keepdims=True)
    ym = y - y.mean(-1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        xs = xm / np.sqrt((xm * xm).mean(-1, keepdims=True))
        ys = ym / np.sqrt((ym * ym).mean(-1, keepdims=True))
        r = (xs * ys).mean(-1)
        L = xs * ys - r[..., None] * (xs * xs + ys * ys) / 2
    return r, (L * L).sum(-1) / n**2


def jackknife_corr(x, y):
    """Leave-one-out correlations along the last axis, from sums (x and y are centred first for accuracy)."""
    x = x - x.mean(-1, keepdims=True)
    y = y - y.mean(-1, keepdims=True)
    m = x.shape[-1] - 1
    sx, sy = x.sum(-1, keepdims=True) - x, y.sum(-1, keepdims=True) - y
    sxx, syy, sxy = ((x * x).sum(-1, keepdims=True) - x * x, (y * y).sum(-1, keepdims=True) - y * y,
                     (x * y).sum(-1, keepdims=True) - x * y)
    return (sxy - sx * sy / m) / np.sqrt((sxx - sx**2 / m) * (syy - sy**2 / m))


def acceleration(jack, centre=True):
    """BCa's acceleration from leave-one-out estimates: sum(d^3) / (6 (sum d^2)^1.5) with d = mean(jack) - jack,
    Efron's centred form, as in bootstrap::bcanon and SciPy. Passing a number as centre uses it in place of the
    jackknife mean: centre=theta_hat gives the form that R's empinf(type = "jack") hands to boot.ci."""
    d = (jack.mean(-1, keepdims=True) if centre is True else centre) - jack
    return (d**3).sum(-1) / (6 * ((d**2).sum(-1)) ** 1.5)


def accel_from_influence(L):
    """The acceleration from empirical influence values L (already oriented as theta_hat minus leave-one-out)."""
    return float((L**3).sum() / (6 * (L**2).sum() ** 1.5))


def influence_corr(x, y):
    """The correlation's empirical influence values in closed form: xs*ys - r (xs^2 + ys^2)/2."""
    xs = (x - x.mean()) / x.std()
    ys = (y - y.mean()) / y.std()
    r = (xs * ys).mean()
    return xs * ys - r * (xs**2 + ys**2) / 2


def bca_levels(z0, a, alpha=ALPHA):
    """The BCa method's adjusted percentile levels for nominal alpha and 1 - alpha."""
    out = []
    for zz in (stats.norm.ppf(alpha), stats.norm.ppf(1 - alpha)):
        out.append(stats.norm.cdf(z0 + (z0 + zz) / (1 - a * (z0 + zz))))
    return np.array(out)


def intervals_from_replicates(r, v0, rb_sorted, vb, rb, n, a, z0=None):
    """The seven 95% intervals for one sample (scalars) from its sorted replicates; returns dict of (lo, hi)."""
    se = rb.std(ddof=1)
    p = q_linear(rb_sorted, np.array([ALPHA, 1 - ALPHA]))
    if z0 is None:
        z0 = stats.norm.ppf((rb < r).mean())
    lv = bca_levels(z0, a)
    t = np.sort((rb - r) / np.sqrt(vb))
    tq = q_linear(t, np.array([ALPHA, 1 - ALPHA]))
    z, zb = np.arctanh(r), np.arctanh(rb)
    tz = np.sort((zb - z) / np.sqrt(vb / (1 - rb**2) ** 2))
    tzq = q_linear(tz, np.array([ALPHA, 1 - ALPHA]))
    sz0 = math.sqrt(v0) / (1 - r**2)
    return {"normal": (r - Z975 * se, r + Z975 * se),
            "percentile": (p[0], p[1]),
            "basic": (2 * r - p[1], 2 * r - p[0]),
            "studentized": (r - math.sqrt(v0) * tq[1], r - math.sqrt(v0) * tq[0]),
            "studentized_z": (math.tanh(z - sz0 * tzq[1]), math.tanh(z - sz0 * tzq[0])),
            "bca": tuple(q_linear(rb_sorted, lv)),
            "fisher_z": (math.tanh(z - Z975 / math.sqrt(n - 3)), math.tanh(z + Z975 / math.sqrt(n - 3)))}


def read_law():
    with LAW_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    pop = np.array([[float(r["lsat"]), float(r["gpa"])] for r in rows])
    school = np.array([int(r["school"]) for r in rows])
    order = sorted((int(r["sample_order"]), i) for i, r in enumerate(rows) if r["in_sample"] == "1")
    idx = np.array([i for _, i in order])
    return pop, school, idx


# ------------------------------------------------------------------------------- example
def stage_example(cfg, args):
    pop, school, sidx = read_law()
    if args.drop is not None:
        if args.drop not in school[sidx]:
            raise SystemExit(f"--drop {args.drop}: not one of the 15 sampled schools {sorted(school[sidx])}")
        sidx = sidx[school[sidx] != args.drop]
        print(f"[example] --drop {args.drop}: school {args.drop} removed; {len(sidx)} schools remain")
    x, y = pop[sidx, 0], pop[sidx, 1]
    n = len(x)
    r, v0 = corr_and_var(x, y)
    rho = float(corr_and_var(pop[:, 0], pop[:, 1])[0])
    se_normal = (1 - r**2) / math.sqrt(n - 3)
    print(f"[example] {n} law schools: r = {r:.6f}; the 82-school population's rho = {rho:.6f}")
    print(f"[example] standard errors before resampling: normal theory (1 - r^2)/sqrt(n - 3) = {se_normal:.4f}; "
          f"delta method sqrt(sum L^2)/n = {math.sqrt(v0):.4f}")
    rng = stream(args.seed, "example")
    B = cfg["B_example"]
    idx = rng.integers(0, n, size=(B, n))
    if args.fault:                                  # E4: an earlier draft of the resampler
        idx_y = rng.integers(0, n, size=(B, n))
    else:
        idx_y = idx
    print(f"[example] first resample, rows drawn for LSAT: {(idx[0] + 1).tolist()}")
    print(f"[example] first resample, rows drawn for GPA:  {(idx_y[0] + 1).tolist()}")
    rb, vb = corr_and_var(x[idx], y[idx_y])
    r1 = float(rb[0])
    print(f"[example] first resample: {len(set(idx[0].tolist()))} distinct schools, r* = {r1:.4f}")
    ok = np.isfinite(rb) & np.isfinite(vb) & (vb > 0)
    if not ok.all():
        print(f"[example] {int((~ok).sum())} replicates undefined (constant resample), dropped")
    rb, vb = rb[ok], vb[ok]
    rs = np.sort(rb)
    se_boot = float(rb.std(ddof=1))
    bias = float(rb.mean() - r)
    below = int((rb < r).sum())
    p0 = below / len(rb)
    z0 = float(stats.norm.ppf(p0))
    jack = jackknife_corr(x, y)
    a = float(acceleration(jack))
    lv = bca_levels(z0, a)
    print(f"[example] B = {len(rb):,} replicates: mean {rb.mean():.4f}, bootstrap SE {se_boot:.4f}, "
          f"bias estimate {bias:+.4f}")
    print(f"[example] {below:,} of {len(rb):,} replicates lie below r: p0 = {p0:.4f}, z0 = qnorm(p0) = {z0:+.4f}")
    print("[example] leave-one-out correlations, school by school: "
          + ", ".join(f"{s}: {j:.4f}" for s, j in zip(school[sidx], jack)))
    print(f"[example] jackknife mean {jack.mean():.4f}; acceleration a = {a:+.5f}")
    print(f"[example] BCa levels: {100 * lv[0]:.3f}% and {100 * lv[1]:.3f}% in place of 2.5% and 97.5%")
    iv = intervals_from_replicates(r, v0, rs, vb, rb, n, a, z0=z0)
    t = np.sort((rb - r) / np.sqrt(vb))
    tq = q_linear(t, np.array([ALPHA, 1 - ALPHA]))
    for m in METHODS:
        print(f"[example]   {NAMES[m]:26s} {fmt(iv[m])}  width {iv[m][1] - iv[m][0]:.4f}")
    print(f"[example] studentized t* quantiles {tq[0]:.3f} and {tq[1]:.3f}; percentile quantiles "
          f"{q_linear(rs, ALPHA):.4f} and {q_linear(rs, 1 - ALPHA):.4f}")
    out = dict(n=n, schools=school[sidx], r=r, rho=rho, se_normal_theory=se_normal, se_delta=math.sqrt(v0),
               first_resample=dict(rows_lsat=idx[0] + 1, rows_gpa=idx_y[0] + 1, distinct=len(set(idx[0].tolist())),
                                   r=r1),
               B=len(rb), se_boot=se_boot, mean_boot=float(rb.mean()), bias_boot=bias, below=below, p0=p0, z0=z0,
               jackknife=jack, jack_mean=float(jack.mean()), a=a, bca_levels=lv, t_quantiles=tq,
               intervals={m: iv[m] for m in METHODS},
               hist=np.histogram(rb, bins=np.linspace(-0.2, 1.0, 61))[0], hist_edges=np.linspace(-0.2, 1.0, 61))
    if args.drop is not None or args.fault:
        out["flags"] = dict(drop=args.drop, fault=args.fault)
        return out
    # The true sampling distribution of r: fresh samples of n schools from the 82, with replacement.
    rng_t = stream(args.seed, "example", 1)
    R = cfg["true_reps"]
    rt = np.empty(R)
    step = max(1, DRAWS_PER_BLOCK // n)
    for s0 in range(0, R, step):
        m = min(step, R - s0)
        ii = rng_t.integers(0, len(pop), size=(m, n))
        rt[s0:s0 + m] = corr_and_var(pop[ii, 0], pop[ii, 1])[0]
    rt = rt[np.isfinite(rt)]
    true = dict(R=len(rt), se=float(rt.std(ddof=1)), mean=float(rt.mean()), bias=float(rt.mean() - rho),
                p_below_rho=float((rt < rho).mean()), quantiles=np.quantile(rt, [ALPHA, 0.5, 1 - ALPHA]),
                hist=np.histogram(rt, bins=np.linspace(-0.2, 1.0, 61))[0])
    print(f"[example] the true sampling distribution of r at n = {n} from the 82 schools (R = {len(rt):,}): SE "
          f"{true['se']:.4f}, mean {true['mean']:.4f}, bias {true['bias']:+.4f}, P(r < rho) {true['p_below_rho']:.4f}, "
          f"2.5/50/97.5% points {', '.join(f'{v:.4f}' for v in true['quantiles'])}")
    out["true"] = true
    # How much the endpoints move with B: the same 15 schools, bootstrapped again and again.
    rng_b = stream(args.seed, "example", 2)
    reps = cfg["endpoint_repeats"]
    moves = {}
    for Bk in (1_000, 2_000, 10_000):
        ends = []
        for _ in range(reps):
            ii = rng_b.integers(0, n, size=(Bk, n))
            rr, vv = corr_and_var(x[ii], y[ii])
            srt = np.sort(rr)
            z0k = stats.norm.ppf((rr < r).mean())
            pp = q_linear(srt, np.array([ALPHA, 1 - ALPHA]))
            bb = q_linear(srt, bca_levels(z0k, a))
            ends.append([pp[0], pp[1], bb[0], bb[1], rr.std(ddof=1)])
        sd = np.array(ends).std(0, ddof=1)
        moves[str(Bk)] = dict(percentile=sd[:2], bca=sd[2:4], se=sd[4])
        print(f"[example] B = {Bk:6,d}: endpoint SD over {reps} reruns: percentile {sd[0]:.4f}, {sd[1]:.4f}; "
              f"BCa {sd[2]:.4f}, {sd[3]:.4f}; bootstrap SE itself {sd[4]:.4f}")
    out["endpoint_sd"] = dict(repeats=reps, by_B=moves)
    return out


# ------------------------------------------------------------------------------- reconcile
def read_r_capture():
    if not R_CSV.exists():
        return None
    rows = list(csv.DictReader(R_CSV.open(encoding="utf-8")))
    cap = {"interval": {}, "constant": {}, "influence": [], "replicate": []}
    for row in rows:
        if row["kind"] == "interval":
            cap["interval"][row["key"]] = (float(row["v1"]), float(row["v2"]))
        elif row["kind"] == "constant":
            cap["constant"][row["key"]] = (row["v1"], row["v2"])
        elif row["kind"] in ("influence", "replicate"):
            cap[row["kind"]].append((float(row["v1"]), float(row["v2"])))
    cap["influence"] = np.array(cap["influence"])
    cap["replicate"] = np.array(cap["replicate"])
    return cap


def regression_influence(freq, t):
    """R boot's empinf(type = "reg"): regress the replicates on the resampling frequencies f/n (first column
    dropped for identifiability), then centre the coefficients."""
    B, n = freq.shape
    X = np.column_stack([np.ones(B), freq[:, 1:] / n])
    beta = np.linalg.lstsq(X, t, rcond=None)[0][1:]
    l = np.concatenate([[0.0], beta])
    return l - l.mean()


def stage_reconcile(cfg, args):
    pop, school, sidx = read_law()
    x, y = pop[sidx, 0], pop[sidx, 1]
    n = len(x)
    r, v0 = corr_and_var(x, y)
    out = {}
    # 1. scipy.stats.bootstrap: same generator, same resamples, so the limits should agree to rounding error.
    B = cfg["B_example"]
    seed = int(stream(args.seed, "reconcile").integers(2**31))
    lib = {}
    for method in ("percentile", "basic", "BCa"):
        res = stats.bootstrap((x, y), lambda a_, b_, axis: corr_and_var(a_, b_)[0], paired=True, vectorized=True,
                              n_resamples=B, method=method, rng=np.random.default_rng(seed))
        lib[method] = (float(res.confidence_interval.low), float(res.confidence_interval.high))
    idx = np.random.default_rng(seed).integers(0, n, size=(B, n))   # what SciPy draws: one call, B rows of n
    rb, vb = corr_and_var(x[idx], y[idx])
    srt = np.sort(rb)
    jack = jackknife_corr(x, y)
    a_c = float(acceleration(jack))
    z0_mid = float(stats.norm.ppf(((rb < r).sum() + (rb <= r).sum()) / (2 * B)))
    p = q_linear(srt, np.array([ALPHA, 1 - ALPHA]))
    mine = {"percentile": (p[0], p[1]), "basic": (2 * r - p[1], 2 * r - p[0]),
            "BCa": tuple(q_linear(srt, bca_levels(z0_mid, a_c)))}
    diff = max(abs(lib[k][j] - mine[k][j]) for k in lib for j in (0, 1))
    for k in lib:
        print(f"[reconcile] SciPy {scipy.__version__} {k:10s} {fmt(lib[k], 6)}; from scratch {fmt(mine[k], 6)}")
    print(f"[reconcile] largest difference from SciPy: {diff:.1e}")
    out["scipy"] = dict(version=scipy.__version__, B=B, seed=seed, scipy=lib, mine=mine, max_abs_diff=diff,
                        z0_midrank=z0_mid, a=a_c)
    # 2. Three BCa conventions on one set of replicates (the SciPy resamples above).
    freq = np.zeros((B, n))
    np.add.at(freq, (np.repeat(np.arange(B), n), idx.ravel()), 1)
    a_reg = accel_from_influence(regression_influence(freq, rb))
    a_unc = float(acceleration(jack, centre=r))
    a_ij = accel_from_influence(influence_corr(x, y))
    z0_strict = float(stats.norm.ppf((rb < r).mean()))
    print(f"[reconcile] acceleration four ways: jackknife, centred {a_c:+.5f}; jackknife, about r {a_unc:+.5f}; "
          f"regression on these {B:,} resamples {a_reg:+.5f}; exact influence values (infinitesimal jackknife) {a_ij:+.5f}")
    out["acceleration"] = dict(jack_centred=a_c, jack_about_r=a_unc, regression=a_reg, infinitesimal=a_ij)
    conv = {
        "bcanon (bootstrap 2019.6)": dict(z0=z0_strict, a=a_c, rule="type 1",
                                         iv=q_inverse_cdf(srt, bca_levels(z0_strict, a_c))),
        "boot.ci default (boot 1.3.32)": dict(z0=z0_strict, a=a_reg, rule="normal-scale interpolation",
                                              iv=q_norm_inter(srt, bca_levels(z0_strict, a_reg))),
        "boot.ci with jackknife L": dict(z0=z0_strict, a=a_unc, rule="normal-scale interpolation",
                                         iv=q_norm_inter(srt, bca_levels(z0_strict, a_unc))),
        "scipy.stats.bootstrap": dict(z0=z0_mid, a=a_c, rule="type 7", iv=np.array(mine["BCa"])),
    }
    for k, c in conv.items():
        print(f"[reconcile] BCa as {k:30s}: z0 {c['z0']:+.4f}, a {c['a']:+.5f} ({c['rule']}): {fmt(c['iv'])}")
    out["conventions"] = conv
    # 3. R's boot.ci, recomputed from R's own replicates with R's conventions.
    cap = read_r_capture()
    if cap is None:
        print("[reconcile] crosscheck-r.csv not found: run Rscript crosscheck.R to add the R comparison")
        return out
    t, vt = cap["replicate"][:, 0], cap["replicate"][:, 1]
    st = np.sort(t)
    t0, v00 = float(cap["constant"]["t0"][0]), float(cap["constant"]["t0"][1])
    L_reg, L_jack = cap["influence"][:, 0], cap["influence"][:, 1]
    z0r = float(stats.norm.ppf((t < t0).mean()))
    accL = accel_from_influence
    q = lambda p_: q_norm_inter(st, p_)
    zt = np.sort((t - t0) / np.sqrt(vt))
    zz = np.sort((np.arctanh(t) - math.atanh(t0)) / np.sqrt(vt / (1 - t**2) ** 2))
    sz = math.sqrt(v00) / (1 - t0**2)
    mineR = {"normal": (t0 - (t.mean() - t0) - Z975 * t.std(ddof=1), t0 - (t.mean() - t0) + Z975 * t.std(ddof=1)),
             "basic": tuple(2 * t0 - q(np.array([1 - ALPHA, ALPHA]))),
             "studentized": tuple(t0 - math.sqrt(v00) * q_norm_inter(zt, np.array([1 - ALPHA, ALPHA]))),
             "studentized_z": tuple(np.tanh(math.atanh(t0) - sz * q_norm_inter(zz, np.array([1 - ALPHA, ALPHA])))),
             "percentile": tuple(q(np.array([ALPHA, 1 - ALPHA]))),
             "bca": tuple(q(bca_levels(z0r, accL(L_reg)))),
             "bca_jack": tuple(q(bca_levels(z0r, accL(L_jack))))}
    # R's own L_jack is (n - 1)(t0 - t_(i)); check it against the lab's leave-one-out correlations.
    jack_check = float(np.abs(L_jack - (n - 1) * (t0 - jack)).max())
    rdiff = max(abs(cap["interval"][k][j] - mineR[k][j]) for k in mineR for j in (0, 1))
    ver = cap["constant"]["versions"]
    for k in mineR:
        print(f"[reconcile] R boot.ci {k:13s} {fmt(cap['interval'][k])}; recomputed {fmt(mineR[k])}")
    print(f"[reconcile] R {ver[0]}, boot {ver[1]}, B = {len(t):,}: largest difference {rdiff:.1e}; z0 {z0r:+.4f}; "
          f"a from regression {accL(L_reg):+.5f}, from the jackknife {accL(L_jack):+.5f}; R's jackknife values match "
          f"the lab's to {jack_check:.1e}")
    out["r"] = dict(R_version=ver[0], boot_version=ver[1], B=len(t), r=cap["interval"], mine=mineR,
                    max_abs_diff=rdiff, z0=z0r, a_reg=accL(L_reg), a_jack=accL(L_jack), jack_check=jack_check)
    return out


# ------------------------------------------------------------------------------- coverage
def stage_coverage(cfg, args):
    pop, _, sidx = read_law()
    n = args.n if args.n else len(sidx)
    rho = float(corr_and_var(pop[:, 0], pop[:, 1])[0])
    R, B = cfg["cov_reps"], cfg["cov_B"]
    rng = stream(args.seed, "coverage")
    hit = {m: 0 for m in METHODS}
    lo_miss = {m: 0 for m in METHODS}        # rho below the interval
    widths = {m: [] for m in METHODS}
    over1 = {m: 0 for m in METHODS}          # an upper limit above 1, which no correlation can reach
    z0s, accs, undefined = [], [], 0
    M = max(1, DRAWS_PER_BLOCK // (B * n))
    done = 0
    while done < R:
        m = min(M, R - done)
        si = rng.integers(0, len(pop), size=(m, n))
        sx, sy = pop[si, 0], pop[si, 1]
        r, v0 = corr_and_var(sx, sy)
        ii = rng.integers(0, n, size=(m, B, n))
        bx = np.take_along_axis(sx[:, None, :], ii, -1)
        by = np.take_along_axis(sy[:, None, :], ii, -1)
        rb, vb = corr_and_var(bx, by)
        jack = jackknife_corr(sx, sy)
        a = acceleration(jack)
        for k in range(m):
            ok = np.isfinite(rb[k]) & np.isfinite(vb[k]) & (vb[k] > 0) & (np.abs(rb[k]) < 1)
            if ok.sum() < B - 5 or not np.isfinite(a[k]):
                undefined += 1
            rbk, vbk = rb[k][ok], vb[k][ok]
            iv = intervals_from_replicates(float(r[k]), float(v0[k]), np.sort(rbk), vbk, rbk, n, float(a[k]))
            z0s.append(stats.norm.ppf((rbk < r[k]).mean()))
            accs.append(float(a[k]))
            for meth, (lo, hi) in iv.items():
                if lo <= rho <= hi:
                    hit[meth] += 1
                elif rho < lo:
                    lo_miss[meth] += 1
                widths[meth].append(hi - lo)
                over1[meth] += hi > 1
        done += m
    out = dict(n=n, R=R, B=B, rho=rho, undefined=undefined, methods={})
    print(f"[coverage] {R:,} samples of {n} from the 82 schools (rho = {rho:.4f}), B = {B:,} replicates each:")
    for meth in METHODS:
        c = hit[meth] / R
        below = lo_miss[meth] / R
        above = (R - hit[meth] - lo_miss[meth]) / R
        w = np.array(widths[meth])
        out["methods"][meth] = dict(coverage=c, mcse=mcse_share(c, R), rho_below=below, rho_above=above,
                                    mcse_below=mcse_share(below, R), mcse_above=mcse_share(above, R),
                                    median_width=float(np.median(w)), upper_above_1=over1[meth] / R)
        print(f"[coverage]   {NAMES[meth]:26s} {pm(c, mcse_share(c, R))}; rho below the interval {pc(below)}%, "
              f"above it {pc(above)}%; median width {np.median(w):.3f}; upper limit above 1 in "
              f"{pc(over1[meth] / R)}%")
    z0s, accs = np.array(z0s), np.array(accs)
    out["z0_quartiles"] = np.quantile(z0s[np.isfinite(z0s)], [0.25, 0.5, 0.75])
    out["a_quartiles"] = np.quantile(accs[np.isfinite(accs)], [0.25, 0.5, 0.75])
    print(f"[coverage] across samples, z0 quartiles {', '.join(f'{v:+.3f}' for v in out['z0_quartiles'])}; "
          f"a quartiles {', '.join(f'{v:+.4f}' for v in out['a_quartiles'])}; {undefined} samples had undefined replicates")
    return out


# ------------------------------------------------------------------------------- spend
def read_spend():
    with SPEND_CSV.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line for line in f if not line.startswith("#")))
    return np.array([float(r["net_spend_gbp"]) for r in rows])


SPEND_METHODS = ("t", "normal", "percentile", "basic", "studentized", "bca")


def mean_intervals(s, sb_mean, sb_sd, a):
    """The six intervals for the mean of each row of s (m, n), from its replicate means and SDs (m, B)."""
    m, n = s.shape
    xb, sd = s.mean(1), s.std(1, ddof=1)
    tq = stats.t.ppf(1 - ALPHA, n - 1)
    srt = np.sort(sb_mean, axis=1)
    p_lo, p_hi = q_linear(srt, ALPHA), q_linear(srt, 1 - ALPHA)
    z0 = stats.norm.ppf((sb_mean < xb[:, None]).mean(1))
    lv = np.array([bca_levels(z0[k], a[k]) for k in range(m)])
    with np.errstate(divide="ignore", invalid="ignore"):
        ts = np.sort((sb_mean - xb[:, None]) / (sb_sd / math.sqrt(n)), axis=1)
    ts = np.where(np.isfinite(ts), ts, np.nan)
    t_lo, t_hi = np.nanquantile(ts, ALPHA, axis=1), np.nanquantile(ts, 1 - ALPHA, axis=1)
    se = sb_mean.std(1, ddof=1)
    return {"t": (xb - tq * sd / math.sqrt(n), xb + tq * sd / math.sqrt(n)),
            "normal": (xb - Z975 * se, xb + Z975 * se),
            "percentile": (p_lo, p_hi),
            "basic": (2 * xb - p_hi, 2 * xb - p_lo),
            "studentized": (xb - sd / math.sqrt(n) * t_hi, xb - sd / math.sqrt(n) * t_lo),
            "bca": (q_linear(srt, lv[:, 0]), q_linear(srt, lv[:, 1]))}


def mean_coverage(draw, mu, n, R, B, rng, flag=None):
    """Coverage of the six intervals for a mean; draw(rng, m, n) returns m samples. flag(s) marks samples for a split."""
    hit = {k: 0 for k in SPEND_METHODS}
    below = {k: 0 for k in SPEND_METHODS}
    split = {0: {k: 0 for k in SPEND_METHODS}, 1: {k: 0 for k in SPEND_METHODS}}
    count = {0: 0, 1: 0}
    M = max(1, DRAWS_PER_BLOCK // (B * n))
    done = 0
    while done < R:
        m = min(M, R - done)
        s = draw(rng, m, n)
        ii = rng.integers(0, n, size=(m, B, n))
        bs = np.take_along_axis(s[:, None, :], ii, -1)
        sb_mean, sb_sd = bs.mean(-1), bs.std(-1, ddof=1)
        d = s - s.mean(1, keepdims=True)
        a = (d**3).sum(1) / (6 * ((d**2).sum(1)) ** 1.5)      # the jackknife acceleration of a mean, in closed form
        iv = mean_intervals(s, sb_mean, sb_sd, a)
        f = flag(s) if flag else np.zeros(m, dtype=int)
        for k in SPEND_METHODS:
            lo, hi = iv[k]
            h = (lo <= mu) & (mu <= hi)
            hit[k] += int(h.sum())
            below[k] += int((hi < mu).sum())
            for g in (0, 1):
                split[g][k] += int(h[f == g].sum())
        for g in (0, 1):
            count[g] += int((f == g).sum())
        done += m
    res = {}
    for k in SPEND_METHODS:
        c = hit[k] / R
        res[k] = dict(coverage=c, mcse=mcse_share(c, R), interval_below=below[k] / R,
                      interval_above=(R - hit[k] - below[k]) / R, mcse_below=mcse_share(below[k] / R, R),
                      by_flag={str(g): (split[g][k] / count[g] if count[g] else None) for g in (0, 1)})
    return res, count


def stage_spend(cfg, args):
    y = read_spend()
    N, mu = len(y), float(y.mean())
    top = float(np.quantile(y, 0.99))
    k_top = int((y >= top).sum())
    print(f"[spend] customer spend: N = {N:,}, mean {mu:,.2f}; the top 1% are the {k_top} customers spending "
          f"{top:,.0f} or more")
    out = dict(N=N, mean=mu, top1_threshold=top, top1_count=k_top, by_n={})
    rng = stream(args.seed, "spend")
    draw = lambda g, m, n: y[g.integers(0, N, size=(m, n))]
    flag = lambda s: (s >= top).any(1).astype(int)
    for n, R in cfg["spend_reps"].items():
        B = cfg["spend_B"]
        res, count = mean_coverage(draw, mu, n, R, B, rng, flag)
        p_top = 1 - (1 - k_top / N) ** n
        out["by_n"][str(n)] = dict(R=R, B=B, methods=res, with_top=count[1], without_top=count[0],
                                   p_top_exact=p_top)
        print(f"[spend] n = {n}, R = {R:,}, B = {B:,}: {count[1]:,} samples ({pc(count[1] / R)}%; exact "
              f"{pc(p_top)}%) contain a top-1% customer")
        for k in SPEND_METHODS:
            v = res[k]
            print(f"[spend]   {NAMES.get(k, k):22s} {pm(v['coverage'], v['mcse'])}; interval below the mean "
                  f"{pc(v['interval_below'])}%; coverage without a top-1% customer "
                  f"{pc(v['by_flag']['0'])}%, with one {pc(v['by_flag']['1'])}%")
    return out


# ------------------------------------------------------------------------------- maximum
def stage_maximum(cfg, args):
    out = {}
    s = np.sort(TANK_SERIALS)
    k, N = len(s), TANK_N
    m = int(s[-1])
    # The bootstrap distribution of the maximum, exactly: P*(M* <= s_(j)) = (j/k)^k over the k^k resamples.
    cdf = np.array([(j / k) ** k for j in range(1, k + 1)])
    pmf = np.diff(np.concatenate([[0.0], cdf]))
    print(f"[maximum] tanks: serials {s.tolist()}, N = {N}; the bootstrap distribution of the maximum over all "
          f"{k**k:,} resamples: " + ", ".join(f"{v}: {p:.5f}" for v, p in zip(s, pmf)))
    point_mass = 1 - (1 - 1 / k) ** k
    # The sampling distribution of M for N = 342: P(M = m) = C(m - 1, k - 1) / C(N, k).
    ms = np.arange(k, N + 1)
    pM = np.array([comb(int(v) - 1, k - 1) for v in ms], dtype=float) / comb(N, k)
    print(f"[maximum] the bootstrap puts {point_mass:.5f} on the observed maximum {m}; the true distribution of M puts "
          f"{pM[ms == m][0]:.5f} on {m}, {pM[-1]:.5f} on {N}, and has P(M <= {m}) = {pM[ms <= m].sum():.4f}")
    q = lambda p_: s[np.searchsorted(cdf, p_ - 1e-12)]           # inverse cdf of the exact bootstrap distribution
    perc = (int(q(ALPHA)), int(q(1 - ALPHA)))
    basic = (2 * m - perc[1], 2 * m - perc[0])
    jack = np.array([np.max(np.delete(s, i)) for i in range(k)], dtype=float)
    a = float(acceleration(jack))
    z0_strict = float(stats.norm.ppf(cdf[-2]))                    # share of resamples strictly below m
    z0_mid = float(stats.norm.ppf((cdf[-2] + 1) / 2))             # SciPy's mid-rank share
    bca = {"strict": tuple(int(q(v)) for v in bca_levels(z0_strict, a)),
           "midrank": tuple(int(q(v)) for v in bca_levels(z0_mid, a))}
    # The exact interval from the sampling distribution: every N with P(M <= m | N) >= 2.5%, from m upward.
    n_up = m
    while comb(m, k) / comb(n_up + 1, k) >= ALPHA:
        n_up += 1
    n_up95 = m                                                    # one-sided: all 5% above, since M <= N always
    while comb(m, k) / comb(n_up95 + 1, k) >= 2 * ALPHA:
        n_up95 += 1
    print(f"[maximum] exact bounds from P(M <= {m} | N): the largest N not rejected at 2.5% is {n_up}, at 5% {n_up95}; "
          f"the lower tail is empty because M <= N, so ({m}, {n_up}) covers at least 97.5% and ({m}, {n_up95}) at least 95%")
    print(f"[maximum] 95% intervals for N from these five serials: percentile {perc}, basic {basic}, BCa {bca['strict']} "
          f"(z0 {z0_strict:+.4f} from the strict share) or {bca['midrank']} (z0 {z0_mid:+.4f}, mid-rank), with jackknife "
          f"a = {a:+.4f}; the exact interval from the distribution of M is ({m}, {n_up})")
    # SciPy on the same five serials.
    sf = s.astype(float)          # SciPy computes z0 in the data's dtype: integer serials would give z0 = -inf
    res = stats.bootstrap((sf,), np.max, n_resamples=9_999, method="BCa", rng=stream(args.seed, "maximum", 9))
    sp_bca = (float(res.confidence_interval.low), float(res.confidence_interval.high))
    res_p = stats.bootstrap((sf,), np.max, n_resamples=9_999, method="percentile", rng=stream(args.seed, "maximum", 9))
    sp_perc = (float(res_p.confidence_interval.low), float(res_p.confidence_interval.high))
    print(f"[maximum] scipy.stats.bootstrap on the five serials: BCa {fmt(sp_bca, 1)}, percentile {fmt(sp_perc, 1)}")
    # Coverage of N over captures, exactly. Percentile and BCa reach no higher than m, so they cover only when
    # M = N. The basic interval [m, 2m - s_(3)] covers when 2 M - X_(3) >= N, summed over the joint
    # distribution of (X_(3), X_(5)): P(X_(3) = u, X_(5) = w) = C(u - 1, 2) (w - u - 1) / C(N, 5).
    j_lo = int(np.searchsorted(cdf, ALPHA - 1e-12))                # the order statistic the basic interval uses
    cov_basic = 0.0
    for w in range(k, N + 1):
        for u in range(j_lo + 1, w):
            if 2 * w - u >= N:
                cov_basic += comb(u - 1, j_lo) * comb(w - u - 1, k - j_lo - 2) if k - j_lo - 2 >= 0 else 0
    cov_basic /= comb(N, k)
    cov_perc = k / N
    print(f"[maximum] exact coverage of N = {N} over all captures of five: percentile and BCa {pc(cov_perc, 2)}% "
          f"(only when tank {N} is caught), basic {pc(cov_basic, 2)}%, the exact interval at least 95%")
    out["tanks"] = dict(serials=s, N=N, boot_pmf=pmf, point_mass=point_mass, true_pmf_at_m=float(pM[ms == m][0]),
                        true_p_le_m=float(pM[ms <= m].sum()), true_pmf=pM, true_support=ms, percentile=perc,
                        basic=basic, bca=bca, a=a, z0_strict=z0_strict, z0_midrank=z0_mid, exact=(m, n_up),
                        exact_one_sided=(m, n_up95),
                        scipy_bca=sp_bca, scipy_percentile=sp_perc, coverage=dict(percentile=cov_perc, bca=cov_perc,
                                                                                  basic=cov_basic))
    # Uniform samples: the point mass 1 - (1 - 1/n)^n and the coverage of the basic interval, by simulation.
    rng = stream(args.seed, "maximum")
    R = cfg["max_reps"]
    uni = {}
    for n in (10, 100, 1000):
        pmass = 1 - (1 - 1 / n) ** n
        jq = int(math.ceil(n * ALPHA ** (1 / n)))                 # P*(M* <= x_(j)) = (j/n)^n >= 2.5%
        hits = 0
        step = max(1, DRAWS_PER_BLOCK // n)
        for s0 in range(0, R, step):
            mm = min(step, R - s0)
            u = np.sort(rng.random((mm, n)), axis=1)
            hits += int((2 * u[:, -1] - u[:, jq - 1] >= 1.0).sum())
        c = hits / R
        uni[str(n)] = dict(point_mass=pmass, order_stat=jq, basic_coverage=c, mcse=mcse_share(c, R), R=R)
        print(f"[maximum] uniform, n = {n:5,d}: P*(M* = M) = {pmass:.4f}; the basic interval reflects at x_({jq}) and "
              f"covers {pm(c, mcse_share(c, R))} (R = {R:,}); percentile and BCa intervals cover 0%")
    out["uniform"] = dict(by_n=uni, limit_point_mass=1 - math.exp(-1), limit_basic=1 - 0.5**3)
    print(f"[maximum] limits as n grows: point mass 1 - 1/e = {1 - math.exp(-1):.4f}; basic coverage 1 - (1/2)^3 = 0.875")
    return out


# ------------------------------------------------------------------------------- heavy
def stage_heavy(cfg, args):
    al = PARETO_ALPHA
    mu = al / (al - 1)
    draw = lambda g, m, n: g.random((m, n)) ** (-1 / al)     # Pareto with minimum 1: P(X > x) = x^-alpha
    rng = stream(args.seed, "heavy")
    out = dict(alpha=al, mean=mu, by_n={})
    print(f"[heavy] Pareto data with tail index {al}: mean {mu}, infinite variance")
    for n, R in cfg["heavy_reps"].items():
        res, _ = mean_coverage(draw, mu, n, R, cfg["heavy_B"], rng)
        out["by_n"][str(n)] = dict(R=R, B=cfg["heavy_B"], methods=res)
        print(f"[heavy] n = {n:5,d}, R = {R:,}: " + "; ".join(
            f"{NAMES.get(k, k)} {pm(res[k]['coverage'], res[k]['mcse'])}" for k in ("t", "percentile", "studentized", "bca")))
    # One sample's bootstrap distribution: a mixture, one lump per number of copies of the largest value.
    rng1 = stream(args.seed, "heavy", 1)
    n, B = 100, 20_000
    shapes = []
    for j in range(3):
        s = draw(rng1, 1, n)[0]
        imax = int(np.argmax(s))
        ii = rng1.integers(0, n, size=(B, n))
        means = s[ii].mean(1)
        copies = (ii == imax).sum(1)
        share = float(s.max() / s.sum())
        lumps = {str(c): dict(share=float((copies == c).mean()), mean=float(means[copies == c].mean()))
                 for c in range(4) if (copies == c).any()}
        edges = np.linspace(np.quantile(means, 0.001), np.quantile(means, 0.999), 81)
        hist = [np.histogram(means[copies == c], bins=edges)[0] for c in range(4)]
        rest = np.delete(s, imax)
        sd_rest = float(np.sqrt(((rest - rest.mean()) ** 2).sum()) / n)     # the spread the other n - 1 values give
        shapes.append(dict(sample_mean=float(s.mean()), max=float(s.max()), max_share=share, lumps=lumps,
                           edges=edges, hist_by_copies=hist, boot_sd=float(means.std(ddof=1)),
                           spacing=float(s.max() / n), sd_rest=sd_rest))
        print(f"[heavy] sample {j + 1} of n = {n:,}: mean {s.mean():.3f}, largest value {s.max():.1f} "
              f"({pc(share)}% of the sum; lumps {s.max() / n:.3f} apart against a spread of {sd_rest:.3f} from the "
              f"rest); bootstrap means by copies of it: "
              + ", ".join(f"{c} copies {pc(v['share'])}% at {v['mean']:.3f}" for c, v in lumps.items()))
    out["shapes"] = shapes
    return out


# ------------------------------------------------------------------------------- dependent
def stage_dependent(cfg, args):
    phi, n = AR_PHI, AR_N
    R, B = cfg["dep_reps"], cfg["dep_B"]
    rng = stream(args.seed, "dependent")
    # Exact variance of the mean of a stationary AR(1) with unit innovations: gamma_k = phi^k / (1 - phi^2).
    g0 = 1 / (1 - phi**2)
    var_mean = g0 / n * (1 + 2 * sum((1 - k / n) * phi**k for k in range(1, n)))
    burn = 200
    hits = 0
    se_ratio, lag1_orig, lag1_res = [], [], []
    M = max(1, DRAWS_PER_BLOCK // (B * n))
    done = 0
    lag1 = lambda z: float(np.corrcoef(z[:-1], z[1:])[0, 1])
    example = None
    while done < R:
        m = min(M, R - done)
        e = rng.standard_normal((m, n + burn))
        xs = np.empty_like(e)
        xs[:, 0] = e[:, 0] * math.sqrt(g0)
        for t in range(1, n + burn):
            xs[:, t] = phi * xs[:, t - 1] + e[:, t]
        xs = xs[:, burn:]
        ii = rng.integers(0, n, size=(m, B, n))
        mb = np.take_along_axis(xs[:, None, :], ii, -1).mean(-1)
        srt = np.sort(mb, axis=1)
        lo, hi = q_linear(srt, ALPHA), q_linear(srt, 1 - ALPHA)
        hits += int(((lo <= 0) & (0 <= hi)).sum())
        se_ratio.extend((mb.std(1, ddof=1) / math.sqrt(var_mean)).tolist())
        for k in range(m):
            lag1_orig.append(lag1(xs[k]))
            lag1_res.append(lag1(xs[k][ii[k, 0]]))
        if example is None:
            example = dict(series=xs[0][:100], resample=xs[0][ii[0, 0]][:100], lag1=lag1(xs[0]),
                           lag1_resample=lag1(xs[0][ii[0, 0]]))
        done += m
    c = hits / R
    theory = math.sqrt((1 - phi) / (1 + phi))
    out = dict(phi=phi, n=n, R=R, B=B, sd_mean_exact=math.sqrt(var_mean), sd_iid=math.sqrt(g0 / n),
               se_ratio_mean=float(np.mean(se_ratio)), se_ratio_theory=theory, coverage=c, mcse=mcse_share(c, R),
               coverage_theory=float(2 * stats.norm.cdf(Z975 * math.sqrt(g0 / n / var_mean)) - 1),
               lag1_orig=float(np.mean(lag1_orig)), lag1_resample=float(np.mean(lag1_res)), example=example)
    print(f"[dependent] AR(1), phi = {phi}, n = {n}: the SD of the mean is {math.sqrt(var_mean):.4f} (exact); "
          f"independent resampling estimates {np.mean(se_ratio):.3f} of it (large-n theory {theory:.3f})")
    print(f"[dependent] lag-1 autocorrelation: series {np.mean(lag1_orig):+.3f}, resamples {np.mean(lag1_res):+.4f}; "
          f"the percentile interval for the mean covers {pm(c, mcse_share(c, R))} (R = {R:,}, B = {B:,}); "
          f"normal-theory value at that SE ratio {pc(out['coverage_theory'])}%")
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
    data = {LAW_CSV.name: sha1(LAW_CSV), SPEND_CSV.name: sha1(SPEND_CSV)}
    if R_CSV.exists():
        data[R_CSV.name] = sha1(R_CSV)
    return {"captured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "os": f"{platform.system()} {platform.release()} {platform.machine()}", "cpu": cpu,
            "python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
            "bootstrap_py_sha1": sha1(pathlib.Path(__file__)), "data_sha1": data, "budget": budget,
            "seed": args.seed, "replications": QUICK if args.quick else FULL,
            "flags": {"drop": args.drop, "fault": args.fault, "n": args.n}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261101)
    parser.add_argument("--drop", type=int, default=None, metavar="SCHOOL",
                        help="example stage: leave this school (its number in the 82) out of the sample")
    parser.add_argument("--n", type=int, default=None, help="coverage stage: sample size drawn from the 82 (default 15)")
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the example stage's resampler")
    args = parser.parse_args()
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, NumPy {prov['numpy']}, "
          f"SciPy {prov['scipy']}; bootstrap.py {prov['bootstrap_py_sha1']}; budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"example": stage_example, "reconcile": stage_reconcile, "coverage": stage_coverage, "spend": stage_spend,
             "maximum": stage_maximum, "heavy": stage_heavy, "dependent": stage_dependent}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
