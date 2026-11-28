#!/usr/bin/env python3
"""Lab for "Bayesian Inference by Hand: Conjugacy and Credible Intervals" (Statistics for Data Scientists, part 11).

Every number the article calls computed or measured comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python bayes.py all --out mine.json            # every stage, the article's budget (about half a minute)
    python bayes.py all --quick --out quick.json   # the reader's budget: fewer Monte Carlo draws, same exact values
    python bayes.py pfizer --out mine.json         # one stage

Stages:
    laplace    Laplace's question: Paris baptisms 1745-1770 under a uniform prior. P(boy probability <= 1/2) three ways
               (exact integers, the beta CDF, the binomial identity) and by Laplace's own series; the 1783 table
               reconciled with the 1812 totals; the law of succession
    pfizer     the BNT162b2 primary analysis rebuilt from its protocol: the prior's constants, the posterior, the three
               published credible intervals, P(VE > 30%), the success and futility boundaries of the protocol's Table 6,
               and the operating characteristics of its Tables 7 and 8
    conjugate  the three conjugate pairs checked against brute-force normalisation: beta-binomial (the trial's split),
               gamma-Poisson with exposure (the trial's two arms), normal-normal (a year of Paris baptisms after 26 years)
    intervals  equal-tailed against highest-density intervals on two scales, and the frequentist coverage of the trial's
               credible interval at fixed efficacies and averaged over its prior
    priors     prior sensitivity: posterior intervals under named priors and under priors of growing strength; the
               induced priors of "flat" choices; Jeffreys' invariance
    lindley    the Bayes factor against the p-value for each year of Paris baptisms 1771-1784 (Lindley's paradox), and the
               Bayes factor's dependence on the prior under the alternative and on n

Exact quantities (beta and binomial sums, quadrature, root finding) carry no MCSE. The two simulated checks print
estimate +- MCSE with their number of draws S, each from its own stream, SeedSequence([stage, sub-stream, seed]).
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
from scipy import integrate, optimize, special, stats

HERE = pathlib.Path(__file__).resolve().parent
PARIS_CSV = HERE / "data" / "paris_baptisms_1745_1784.csv"
TRIAL_CSV = HERE / "data" / "bnt162b2_bayesian_rows.csv"
STAGES = ("laplace", "pfizer", "conjugate", "intervals", "priors", "lindley")

# Monte Carlo draws. The article quotes FULL; --quick is the reader's first run. Exact computations ignore the budget.
FULL = dict(ratio_draws=400_000, coverage_draws=400_000)
QUICK = {k: v // 10 for k, v in FULL.items()}

A0, B0 = 0.700102, 1.0          # the protocol's prior, beta(0.700102, 1), on theta = (1 - VE)/(2 - VE)
VE_BAR = 0.30                   # the protocol's efficacy bar: success needs P(VE > 30% | data) above a threshold
LEVEL = 0.95
ANALYSES = ((32, 0.995), (62, 0.995), (92, 0.995), (120, 0.995), (164, 0.986))   # protocol section 9.5, Table 6
FINAL_N = 164
POS_FUTILITY = 0.05
PROTOCOL_TABLE6 = {"success": {"32": 6, "62": 15, "92": 25, "120": 35, "164": 53},
                   "futility": {"32": 15, "62": 26, "92": 35}}
# Protocol Tables 7 and 8, as printed: per analysis P(success), P(failure); then the final analysis and overall success.
PROTOCOL_OC = {"30": ["0.006", "0.315", "0.003", "0.231", "0.002", "0.239", "0.002", "0.007", "0.021"],
               "50": ["0.054", "0.078", "0.051", "0.056", "0.063", "0.103", "0.075", "0.196", "0.439"],
               "60": ["0.150", "0.021", "0.160", "0.010", "0.175", "0.019", "0.160", "0.220", "0.866"],
               "70": ["0.368", "0.003", "0.310", "<0.001", "0.195", "0.001", "0.085", "0.036", ">0.999"],
               "80": ["0.722", "<0.001", "0.238", "<0.001", "0.037", "<0.001", "0.003", "<0.001", ">0.999"]}
LAPLACE_1781 = {"first_term_numerator": 1.1521, "log10_root_factor": -2 + 0.4660039,
                "log10_power_p": 73616.6879714, "log10_power_q": 74893.3836139, "log10_power_2": 148550.4760803}
LAPLACE_TAP = {"log10_mu": 72.2511780, "series_second_term": 0.0030761}   # Theorie analytique, 3rd ed., II section 28
PRINTED_TOTAL_1771_1784 = (151859, 145159)                                  # the 1783 table's printed Total row
INFORMED_PERIOD = "1745-1770"
LINDLEY_YEAR = 1782


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


def hu(x, nd=4):
    """A number rounded half up from its decimal value."""
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def pc(share, nd=1):
    """A share as a percentage, rounded half up from its decimal value."""
    return str((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def sci(x, nd=4):
    """'1.1461e-42': a positive number in scientific notation, mantissa rounded half up."""
    if x == 0:
        return "0"
    e = math.floor(math.log10(abs(x)))
    m = Decimal(repr(float(x))) / (Decimal(10) ** e)
    m = m.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    if abs(m) >= 10:
        m, e = m / 10, e + 1
    return f"{m}e{e}"


def ve_of(theta, r):
    """Vaccine efficacy from the vaccine group's expected share of cases, r = vaccine/placebo surveillance time."""
    return 1.0 - theta / ((1.0 - theta) * r)


def theta_of(ve, r):
    """The vaccine group's expected share of cases at efficacy ve: the inverse of ve_of."""
    return r * (1.0 - ve) / (1.0 + r * (1.0 - ve))


def big_ratio(num, den):
    """num/den for huge non-negative integers, as a float, without overflow."""
    if num == 0:
        return 0.0
    shift = max(num.bit_length(), den.bit_length()) - 1000
    if shift > 0:
        num, den = num >> shift, den >> shift
    return num / den if den else math.inf


def read_paris():
    with PARIS_CSV.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
    return {r["period"]: (int(r["boys"]), int(r["girls"])) for r in rows}


def read_trial():
    with TRIAL_CSV.open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(line for line in handle if not line.startswith("#")))
    for r in rows:
        for k in ("cases_vaccine", "cases_placebo"):
            r[k] = int(r[k])
        for k in ("surveillance_vaccine", "surveillance_placebo", "published_ve", "published_lower", "published_upper"):
            r[k] = float(r[k])
    return rows


def credible(yv, yp, r, a=A0, b=B0, level=LEVEL):
    """The equal-tailed credible interval for VE, the posterior median of VE and P(VE > 30%), from beta(a, b)."""
    post = stats.beta(a + yv, b + yp)
    lo_t, hi_t = post.ppf([(1 - level) / 2, (1 + level) / 2])
    return {"lower": ve_of(hi_t, r), "upper": ve_of(lo_t, r), "median": ve_of(post.median(), r),
            "p_ve_gt_30": post.cdf(theta_of(VE_BAR, r)), "p_ve_le_30": post.sf(theta_of(VE_BAR, r))}


# ------------------------------------------------------------------------------- stage: laplace
def exact_half_tail(n, k0, terms=6000):
    """P(Bin(n, 1/2) >= k0) in integer arithmetic: the first `terms` terms exactly, the rest bounded geometrically."""
    c, s, k = math.comb(n, k0), 0, k0
    for _ in range(terms):
        s += c
        if k == n:
            c = 0
            break
        c = c * (n - k) // (k + 1)
        k += 1
    shift = s.bit_length() - 64
    value = math.ldexp(float(s >> shift), shift - n)
    ratio = (n - k) / (k + 1) if c else 0.0
    remainder_rel = big_ratio(c, s) / (1 - ratio) if c else 0.0
    return value, remainder_rel


def laplace_1781_series(p, q):
    """Laplace's 1781 series (art. XIX) for P(x <= 1/2): log10 of its first term and its second-term correction."""
    mu, alpha = q / p, 1 / p
    root = 0.5 * math.log10(2 * alpha * mu / ((1 + mu) * math.pi)) - math.log10(1 - mu)
    power_p = (p + 1) * math.log10((p + q) / p)
    power_q = (q + 1) * math.log10((p + q) / q)
    power_2 = (p + q + 2) * math.log10(2)
    second = alpha * (48 * mu ** 2 + 3 * mu * (1 - mu) ** 2 + (1 - mu) ** 4) / (12 * mu * (1 + mu) * (1 - mu) ** 2)
    return {"log10_root_factor": root, "log10_power_p": power_p, "log10_power_q": power_q, "log10_power_2": power_2,
            "log10_first_term": root + power_p + power_q - power_2, "second_term": second}


def stage_laplace(cfg, args):
    print("[laplace] Paris baptisms, a uniform prior on the probability x that a birth is a boy")
    paris = read_paris()
    p, q = paris[INFORMED_PERIOD]
    a, b = p + 1, q + 1
    post = stats.beta(a, b)
    exact, remainder = exact_half_tail(a + b - 1, a)
    tail_beta = float(post.cdf(0.5))
    tail_binom = float(stats.binom.sf(a - 1, a + b - 1, 0.5))
    ser = laplace_1781_series(p, q)
    first = 10 ** ser["log10_first_term"]
    two_terms = first * (1 - ser["second_term"])
    mean, sd = post.mean(), post.std()
    lo, hi = post.ppf([0.025, 0.975])
    print(f"  1745-1770: {p:,} boys, {q:,} girls; posterior beta({a:,}, {b:,}): mean {hu(mean, 6)}, SD {hu(sd, 6)}, "
          f"95% interval {hu(lo, 5)} to {hu(hi, 5)}; 1/2 lies {hu((mean - 0.5) / sd, 2)} SDs below the mean")
    print(f"  P(x <= 1/2): exact integers {exact!r} (remainder < {remainder:.1e} relative); "
          f"beta CDF {tail_beta!r}; binomial identity {tail_binom!r}")
    print(f"  Laplace 1781, first term of his series: {sci(first, 4)} (he printed 1.1521e-42; logs {hu(ser['log10_root_factor'], 7)} "
          f"against his -1.5339961, {hu(ser['log10_power_p'], 7)}, "
          f"{hu(ser['log10_power_q'], 7)}, {hu(ser['log10_power_2'], 7)}); second term {hu(ser['second_term'], 6)} = 1/{hu(1 / ser['second_term'], 0)}; "
          f"two terms {sci(two_terms, 4)}; first term / exact - 1 = {pc(first / exact - 1, 2)}%")
    print(f"  log10 posterior density at 1/2: {hu(post.logpdf(0.5) / math.log(10), 2)}; law of succession P(next is a boy) "
          f"= {a:,}/{a + b:,} = {hu(a / (a + b), 6)}")
    years = [str(y) for y in range(1771, 1785)]
    sb, sg = sum(paris[y][0] for y in years), sum(paris[y][1] for y in years)
    tp, tq = paris["1745-1784"]
    ok = (p + sb, q + sg) == (tp, tq)
    print(f"  1783 table: the year rows sum to {sb:,} boys and {sg:,} girls (printed Total row {PRINTED_TOTAL_1771_1784[0]:,} "
          f"and {PRINTED_TOTAL_1771_1784[1]:,}); with 1745-1770 they give {p + sb:,} and {q + sg:,}, the 1812 totals "
          f"{tp:,} and {tq:,}: {'match' if ok else 'MISMATCH'}")
    tap = stats.beta(tp + 1, tq + 1)
    tap_exact = float(tap.cdf(0.5))
    tap_laplace = 10 ** (-LAPLACE_TAP["log10_mu"]) * (1 - LAPLACE_TAP["series_second_term"])
    print(f"  1745-1784 (Theorie analytique): P(x <= 1/2) = {sci(tap_exact, 4)}; Laplace's printed 10^-72.2511780 x "
          f"(1 - 0.0030761) = {sci(tap_laplace, 4)}")
    by_year = {y: {"boys": paris[y][0], "girls": paris[y][1], "share": paris[y][0] / sum(paris[y])} for y in years}
    return {"period": INFORMED_PERIOD, "boys": p, "girls": q, "posterior": [a, b], "mean": mean, "sd": sd,
            "interval95": [lo, hi], "sds_below_mean": (mean - 0.5) / sd, "tail_exact": exact,
            "tail_exact_remainder_rel": remainder, "tail_beta_cdf": tail_beta, "tail_binom_identity": tail_binom,
            "laplace_series": ser, "laplace_first_term": first, "laplace_two_terms": two_terms,
            "laplace_printed": LAPLACE_1781, "first_over_exact": first / exact,
            "log10_density_at_half": post.logpdf(0.5) / math.log(10), "succession": a / (a + b),
            "table1783": {"sum_boys": sb, "sum_girls": sg, "printed_total": list(PRINTED_TOTAL_1771_1784),
                          "reconciles_with_1812": ok, "by_year": by_year},
            "tap": {"boys": tp, "girls": tq, "tail_exact": tap_exact, "laplace_printed_value": tap_laplace}}


# ------------------------------------------------------------------------------- stage: pfizer
def success_probability(x, n):
    """P(VE > 30% | x vaccine cases of n) under the protocol's prior, at the design's 1:1 split of follow-up."""
    return float(stats.beta.cdf(theta_of(VE_BAR, 1.0), A0 + x, B0 + n - x))


def pos_final(x, n):
    """Posterior predictive probability that the final analysis succeeds: at most PROTOCOL_TABLE6 final cases."""
    need = PROTOCOL_TABLE6["success"][str(FINAL_N)] - x
    if need < 0:
        return 0.0
    return float(stats.betabinom.cdf(need, FINAL_N - n, A0 + x, B0 + n - x))


def operating_characteristics(ve, success, futility, binding=True):
    """Exact sequential probabilities of success and failure at each analysis for a true VE (1:1 randomisation).
    With binding=False a futility crossing is recorded but the trial continues, as the protocol's nonbinding rule allows."""
    theta = theta_of(ve, 1.0)
    dist, k, out = np.array([1.0]), 0, []
    for n, _ in ANALYSES:
        inc = stats.binom.pmf(np.arange(n - k + 1), n - k, theta)
        dist, k = np.convolve(dist, inc), n
        xs = np.arange(dist.size)
        s_mask = xs <= success[str(n)]
        p_s = float(dist[s_mask].sum())
        dist[s_mask] = 0.0
        p_f = None
        if str(n) in futility:
            f_mask = xs >= futility[str(n)]
            p_f = float(dist[f_mask].sum())
            if binding:
                dist[f_mask] = 0.0
        out.append((p_s, p_f))
    return out


def oc_string(v):
    if v is None:
        return "-"
    if v < 0.0005:
        return "<0.001"
    if v > 0.9995:
        return ">0.999"
    return hu(v, 3)


def stage_pfizer(cfg, args):
    print("[pfizer] the BNT162b2 primary analysis, from the protocol's prior beta(0.700102, 1)")
    prior = stats.beta(A0, B0)
    th30 = theta_of(VE_BAR, 1.0)
    pmean, pmed = A0 / (A0 + B0), float(prior.median())
    q_lo, q_hi = prior.ppf([0.025, 0.975])
    const = {"a_from_rounded_mean": 0.4118 / 0.5882, "theta_at_ve30": th30, "prior_mean": pmean,
             "ve_at_prior_mean": ve_of(pmean, 1.0), "prior_median": pmed, "ve_at_prior_median": ve_of(pmed, 1.0),
             "prior95_theta": [q_lo, q_hi], "prior95_ve": [ve_of(q_hi, 1.0), ve_of(q_lo, 1.0)],
             "prior_p_ve_gt_30": float(prior.cdf(th30)), "prior_p_ve_lt_0": float(prior.sf(0.5)),
             "senn_alternative_b": 0.5882 / 0.4118}
    print(f"  0.4118/0.5882 = {const['a_from_rounded_mean']!r}; theta at VE 30% = 0.7/1.7 = {hu(th30, 6)}; prior mean "
          f"{hu(pmean, 6)} (VE {pc(const['ve_at_prior_mean'], 2)}%), prior median {hu(pmed, 5)} "
          f"(VE {pc(const['ve_at_prior_median'], 2)}%)")
    print(f"  prior 95% interval: theta {hu(q_lo, 5)} to {hu(q_hi, 5)}, VE {hu(const['prior95_ve'][0], 2)} to "
          f"{hu(const['prior95_ve'][1], 4)} (protocol: 0.005 to 0.964; -26.2 to 0.995); prior P(VE > 30%) "
          f"{hu(const['prior_p_ve_gt_30'], 4)}, P(VE < 0) {hu(const['prior_p_ve_lt_0'], 4)}")
    rows_out = []
    for row in read_trial():
        if row["interval"] != "credible":
            continue
        yv, yp, tv, tp = row["cases_vaccine"], row["cases_placebo"], row["surveillance_vaccine"], row["surveillance_placebo"]
        r_true = tv / tp
        r = 1.0 if args.fault else r_true          # the efficacy map's surveillance ratio
        c = credible(yv, yp, r)
        a_post, b_post = A0 + yv, B0 + yp
        mle = 1 - (yv / tv) / (yp / tp)
        mean_ve = 1 - a_post / ((b_post - 1) * r) if b_post > 1 else None
        got = (hu(100 * c["lower"], 1), hu(100 * c["upper"], 1))
        want = (f"{row['published_lower']:.1f}", f"{row['published_upper']:.1f}")
        print(f"  {row['endpoint']}: {yv}:{yp} cases, surveillance ratio r = {tv}/{tp} = {hu(r_true, 6)}; theta at VE 30% "
              f"under the efficacy map {hu(theta_of(VE_BAR, r), 6)}; posterior beta({hu(a_post, 6)}, {b_post:g})")
        print(f"    VE 95% credible interval {hu(100 * c['lower'], 3)} to {hu(100 * c['upper'], 3)}% -> {got[0]} to {got[1]} "
              f"(published {want[0]} to {want[1]}: {'match' if got == want else 'MISMATCH'}); posterior median "
              f"{hu(100 * c['median'], 2)}%, MLE {hu(100 * mle, 2)}%; P(VE <= 30%) = {sci(c['p_ve_le_30'], 3)}")
        prior_weight = (A0 + B0) / (A0 + B0 + yv + yp)
        print(f"    posterior mean of theta {hu(a_post / (a_post + b_post), 6)} = {hu(prior_weight, 6)} x prior mean {hu(pmean, 4)} "
              f"+ {hu(1 - prior_weight, 6)} x observed share {hu(yv / (yv + yp), 6)}")
        rows_out.append({"endpoint": row["endpoint"], "split": [yv, yp], "times": [tv, tp], "r": r_true, "r_map": r,
                         "prior_weight": prior_weight, "posterior_mean_theta": a_post / (a_post + b_post),
                         "posterior": [a_post, b_post], "lower": c["lower"], "upper": c["upper"], "median": c["median"],
                         "mean": mean_ve, "mle": mle, "p_ve_gt_30": c["p_ve_gt_30"], "p_ve_le_30": c["p_ve_le_30"],
                         "published": [row["published_ve"], row["published_lower"], row["published_upper"]],
                         "matches_published": got == want})
    # The protocol's Table 6: success and futility boundaries, recomputed from the prior and the thresholds.
    success, futility, curves = {}, {}, {}
    for n, thr in ANALYSES:
        probs = [success_probability(x, n) for x in range(n + 1)]
        success[str(n)] = max(x for x in range(n + 1) if probs[x] > thr)
        curves[str(n)] = probs
    pos_curves = {}
    for n in (32, 62, 92):
        pos = [pos_final(x, n) for x in range(n + 1)]
        futility[str(n)] = min(x for x in range(n + 1) if pos[x] < POS_FUTILITY)
        pos_curves[str(n)] = pos
    for n, thr in ANALYSES:
        x = success[str(n)]
        fut = f", futility at >= {futility[str(n)]} (POS {hu(pos_curves[str(n)][futility[str(n)] - 1], 4)} at "\
              f"{futility[str(n)] - 1}, {hu(pos_curves[str(n)][futility[str(n)]], 4)} at {futility[str(n)]})" if str(n) in futility else ""
        print(f"  {n} cases: success if at most {x} vaccine cases (VE {pc(1 - x / (n - x), 1)}%; P(VE > 30%) "
              f"{hu(curves[str(n)][x], 4)} at {x}, {hu(curves[str(n)][x + 1], 4)} at {x + 1}; threshold {thr}){fut}")
    match6 = success == PROTOCOL_TABLE6["success"] and futility == PROTOCOL_TABLE6["futility"]
    print(f"  protocol Table 6: {'every boundary matches' if match6 else 'MISMATCH'}")
    # The predictive distribution behind the futility rule, at the first interim analysis.
    predictive = {}
    for x in (14, 15):
        m = FINAL_N - 32
        pmf = stats.betabinom.pmf(np.arange(m + 1), m, A0 + x, B0 + 32 - x)
        predictive[str(x)] = {"pmf": pmf, "need_at_most": PROTOCOL_TABLE6["success"][str(FINAL_N)] - x,
                              "pos": pos_final(x, 32), "mean": float(np.arange(m + 1) @ pmf)}
    print(f"  at 32 cases: POS {hu(predictive['14']['pos'], 4)} with 14 vaccine cases, {hu(predictive['15']['pos'], 4)} "
          f"with 15 (success later needs at most 39 and 38 of the remaining 132)")
    # Tables 7 and 8: the frequentist operating characteristics of the Bayesian rule.
    oc, oc_match = {}, True
    for ve_pct in (30, 50, 60, 70, 80):
        res = operating_characteristics(ve_pct / 100, success, futility)
        flat = []
        for p_s, p_f in res[:3]:
            flat += [p_s, p_f]
        flat += [res[3][0], res[4][0], sum(p_s for p_s, _ in res)]
        strings = [oc_string(v) for v in flat]
        same = strings == PROTOCOL_OC[str(ve_pct)]
        oc_match &= same
        overall_nonbinding = sum(p_s for p_s, _ in operating_characteristics(ve_pct / 100, success, futility, False))
        printed = PROTOCOL_OC[str(ve_pct)]
        column_sum = sum(float(printed[i]) if printed[i][0].isdigit() else 0.0 for i in (0, 2, 4, 6, 7))
        oc[str(ve_pct)] = {"values": flat, "strings": strings, "protocol": printed, "match": same,
                           "overall_nonbinding": overall_nonbinding, "protocol_success_column_sum": column_sum,
                           "n_match": sum(a == b for a, b in zip(strings, printed))}
        print(f"  VE {ve_pct}%: " + " ".join(strings) + f"  (protocol {' '.join(printed)}: "
              f"{'match' if same else 'differs'}; the protocol's own success columns sum to {hu(column_sum, 3)}; "
              f"overall with futility not binding {hu(overall_nonbinding, 4)})")
    print(f"  overall P(success) at VE 30%: {hu(oc['30']['values'][-1], 4)} (the type I error the thresholds were set to hold "
          f"under 0.025)")
    return {"constants": const, "rows": rows_out, "fault": args.fault, "table6": {"success": success, "futility": futility},
            "table6_matches_protocol": match6, "success_curves": curves, "pos_curves": pos_curves,
            "predictive_32": predictive, "operating": oc, "operating_matches_protocol": oc_match}


# ------------------------------------------------------------------------------- stage: conjugate
def stage_conjugate(cfg, args):
    print("[conjugate] each closed-form posterior against the same posterior normalised by quadrature")
    out = {}
    # Beta-binomial: the trial's split.
    yv, n = 8, 170
    f = lambda t: stats.beta.pdf(t, A0, B0) * stats.binom.pmf(yv, n, t)
    z, _ = integrate.quad(f, 0, 1, points=[0.02, 0.047, 0.1], limit=400, epsabs=0, epsrel=1e-13)
    z_closed = math.comb(n, yv) * math.exp(special.betaln(A0 + yv, B0 + n - yv) - special.betaln(A0, B0))
    grid = np.linspace(0.005, 0.15, 59)
    rel = np.max(np.abs(np.array([f(t) for t in grid]) / z / stats.beta.pdf(grid, A0 + yv, B0 + n - yv) - 1))
    cdf = lambda u: integrate.quad(f, 0, u, points=[min(u, 0.047)], limit=400, epsabs=0, epsrel=1e-13)[0] / z
    qs = [optimize.brentq(lambda u, s=s: cdf(u) - s, 1e-6, 0.5, xtol=1e-14) for s in (0.025, 0.975)]
    q_closed = stats.beta.ppf([0.025, 0.975], A0 + yv, B0 + n - yv)
    out["beta_binomial"] = {"marginal_quadrature": z, "marginal_closed": z_closed, "max_rel_density_error": rel,
                            "quantiles_quadrature": qs, "quantiles_closed": q_closed}
    print(f"  beta-binomial, 8 of 170: marginal likelihood {sci(z, 6)} by quadrature, {sci(z_closed, 6)} closed form; "
          f"density error {rel:.1e}; 2.5% and 97.5% points {hu(qs[0], 7)}, {hu(qs[1], 7)} against {hu(q_closed[0], 7)}, {hu(q_closed[1], 7)}")
    # Gamma-Poisson with exposure: each arm's rate per 1,000 person-years, Jeffreys' prior p(lambda) ~ lambda^(-1/2).
    arms = {}
    for arm, y, t in (("vaccine", 8, 2.214), ("placebo", 162, 2.222)):
        post = stats.gamma(y + 0.5, scale=1 / t)                    # SciPy's gamma takes scale = 1/rate
        mode, sd = (y - 0.5) / t, math.sqrt(y + 0.5) / t
        log_peak = (y - 0.5) * math.log(mode) - mode * t             # the kernel's log at its mode, to avoid overflow
        g = lambda lam, y=y, t=t, c=log_peak: math.exp((y - 0.5) * math.log(lam) - lam * t - c) if lam > 0 else 0.0
        top = mode + 60 * sd
        zz, _ = integrate.quad(g, 0, top, points=[mode], limit=400, epsabs=0, epsrel=1e-12)
        mean_q = integrate.quad(lambda lam: lam * g(lam), 0, top, points=[mode], limit=400, epsabs=0, epsrel=1e-12)[0] / zz
        lo, hi = post.ppf([0.025, 0.975])
        arms[arm] = {"cases": y, "thousand_person_years": t, "posterior": [y + 0.5, t], "mean": post.mean(),
                     "mean_quadrature": mean_q, "interval95": [lo, hi], "mle": y / t}
        print(f"  gamma-Poisson, {arm}: {y} cases in {t} thousand person-years -> gamma(shape {y + 0.5}, rate {t}): mean "
              f"{hu(post.mean(), 3)} per 1,000 person-years (quadrature {hu(mean_q, 3)}), 95% interval {hu(lo, 2)} to {hu(hi, 2)}")
    r = 2.214 / 2.222
    rng = stream(args.seed, "conjugate", 0)
    S = cfg["ratio_draws"]
    lv = rng.gamma(8.5, 1 / 2.214, S)
    lp = rng.gamma(162.5, 1 / 2.222, S)
    share = lv * 2.214 / (lv * 2.214 + lp * 2.222)
    probs = np.array([0.025, 0.5, 0.975])
    q_mc = np.quantile(share, probs)
    q_beta = stats.beta.ppf(probs, 8.5, 162.5)
    se = np.sqrt(probs * (1 - probs) / S) / stats.beta.pdf(q_beta, 8.5, 162.5)
    ve_mc = np.quantile(1 - lv / lp, [0.025, 0.975])
    ve_beta = [ve_of(q_beta[2], r), ve_of(q_beta[0], r)]
    print(f"  the two arms' posteriors make the case share beta(8.5, 162.5): Monte Carlo (S {S:,}) quantiles "
          + ", ".join(f"{hu(m, 5)} +- {hu(s, 5)} against {hu(e, 5)}" for m, s, e in zip(q_mc, se, q_beta))
          + f"; VE 95% interval {pc(ve_beta[0], 2)}% to {pc(ve_beta[1], 2)}% (Monte Carlo {pc(ve_mc[0], 2)} to {pc(ve_mc[1], 2)})")
    # The trial's beta prior as gamma priors with a common rate on the two arms' expected counts.
    rng2 = stream(args.seed, "conjugate", 1)
    mv = rng2.gamma(A0 + 8, 1 / 2.0, S)            # prior gamma(0.700102, rate 1) on the expected count, + 8 cases
    mp = rng2.gamma(B0 + 162, 1 / 2.0, S)
    q_mc2 = np.quantile(mv / (mv + mp), probs)
    q_trial = stats.beta.ppf(probs, A0 + 8, B0 + 162)
    se2 = np.sqrt(probs * (1 - probs) / S) / stats.beta.pdf(q_trial, A0 + 8, B0 + 162)
    print("  gamma(0.700102, c) and gamma(1, c) priors on the expected counts give beta(8.700102, 163) for any c: quantiles "
          + ", ".join(f"{hu(m, 5)} +- {hu(s, 5)} against {hu(e, 5)}" for m, s, e in zip(q_mc2, se2, q_trial)))
    out["gamma_poisson"] = {"arms": arms, "share_posterior": [8.5, 162.5], "draws": S, "share_quantiles_mc": q_mc,
                            "share_quantiles_mcse": se, "share_quantiles_beta": q_beta, "ve_interval_jeffreys_rates": ve_beta,
                            "ve_interval_mc": ve_mc, "trial_prior_as_gammas": {"quantiles_mc": q_mc2, "mcse": se2,
                                                                                "quantiles_beta": q_trial}}
    # Normal-normal: Paris 1782 after the 26 years 1745-1770 (normal approximations), against the exact beta update.
    paris = read_paris()
    p0, q0 = paris[INFORMED_PERIOD]
    y, g_ = paris[str(LINDLEY_YEAR)]
    n1 = y + g_
    prior = stats.beta(p0 + 1, q0 + 1)
    m0, s0 = prior.mean(), prior.std()
    phat = y / n1
    se1 = math.sqrt(phat * (1 - phat) / n1)
    w0, w1 = 1 / s0 ** 2, 1 / se1 ** 2
    m_post, s_post = (w0 * m0 + w1 * phat) / (w0 + w1), (w0 + w1) ** -0.5
    exact = stats.beta(p0 + 1 + y, q0 + 1 + g_)
    h = lambda t: stats.norm.pdf(t, m0, s0) * stats.norm.pdf(phat, t, se1)
    zz = integrate.quad(h, m0 - 12 * s0, m0 + 12 * s0, points=[m0], limit=400, epsabs=0, epsrel=1e-13)[0]
    mq = integrate.quad(lambda t: t * h(t), m0 - 12 * s0, m0 + 12 * s0, points=[m0], limit=400, epsabs=0, epsrel=1e-13)[0] / zz
    out["normal_normal"] = {"prior": [m0, s0], "data": [phat, se1, n1], "weight_prior": w0 / (w0 + w1),
                            "posterior": [m_post, s_post], "posterior_quadrature_mean": mq,
                            "exact_beta": [exact.mean(), exact.std()], "exact_beta_params": [p0 + 1 + y, q0 + 1 + g_]}
    print(f"  normal-normal, {LINDLEY_YEAR} ({y:,} of {n1:,}, share {hu(phat, 5)} +- {hu(se1, 5)}) after {INFORMED_PERIOD} "
          f"(N({hu(m0, 6)}, {hu(s0, 6)}^2)): prior weight {hu(w0 / (w0 + w1), 4)}; posterior N({hu(m_post, 6)}, {hu(s_post, 6)}^2), "
          f"quadrature mean {hu(mq, 6)}; exact beta update: mean {hu(exact.mean(), 6)}, SD {hu(exact.std(), 6)}")
    return out


# ------------------------------------------------------------------------------- stage: intervals
def hdi_from_quantile(qf, level=LEVEL):
    """Shortest interval of probability `level` for a unimodal distribution, given its quantile function."""
    res = optimize.minimize_scalar(lambda t: qf(t + level) - qf(t), bounds=(1e-12, 1 - level - 1e-12),
                                   method="bounded", options={"xatol": 1e-12})
    return qf(res.x), qf(res.x + level), res.x


def ve_density(v, post, r):
    theta = theta_of(v, r)
    return post.pdf(theta) * r / (1 + r * (1 - v)) ** 2


def hdr_grid(post, r, lo, hi, m=400_001, level=LEVEL):
    """Hyndman's highest-density region on a VE grid: the density level whose upper set holds `level`."""
    v = np.linspace(lo, hi, m)
    d = ve_density(v, post, r)
    dv = v[1] - v[0]
    order = np.argsort(d)[::-1]
    cum = np.cumsum(d[order]) * dv
    keep = order[: int(np.searchsorted(cum, level)) + 1]
    return float(v[keep].min()), float(v[keep].max())


def coverage_curve(n, r, theta_grid, kind):
    ys = np.arange(n + 1)
    if kind == "credible":
        t_lo = stats.beta.ppf(0.025, A0 + ys, B0 + n - ys)
        t_hi = stats.beta.ppf(0.975, A0 + ys, B0 + n - ys)
    else:  # Clopper-Pearson
        t_lo = np.where(ys > 0, stats.beta.ppf(0.025, np.maximum(ys, 1), n - ys + 1), 0.0)
        t_hi = np.where(ys < n, stats.beta.ppf(0.975, ys + 1, np.maximum(n - ys, 1)), 1.0)
    pmf = stats.binom.pmf(ys[None, :], n, theta_grid[:, None])
    inside = (t_lo[None, :] <= theta_grid[:, None]) & (theta_grid[:, None] <= t_hi[None, :])
    return (pmf * inside).sum(axis=1)


def stage_intervals(cfg, args):
    print("[intervals] equal-tailed and highest-density intervals; the coverage of the trial's credible interval")
    out = {}
    for name, yv, yp, tv, tp in (("primary", 8, 162, 2.214, 2.222), ("severe", 1, 3, 2.215, 2.232)):
        r = tv / tp
        post = stats.beta(A0 + yv, B0 + yp)
        et = [ve_of(post.ppf(0.975), r), ve_of(post.ppf(0.025), r)]
        t_l, t_u, t_mass = hdi_from_quantile(post.ppf)
        hdi_theta_mapped = [ve_of(t_u, r), ve_of(t_l, r)]
        ve_q = lambda s: ve_of(post.ppf(1 - s), r)
        v_l, v_u, v_mass = hdi_from_quantile(ve_q)
        dens_theta = [post.pdf(t_l), post.pdf(t_u)]
        dens_ve = [ve_density(v_l, post, r), ve_density(v_u, post, r)]
        lo_grid = v_l - 0.5 * (v_u - v_l)
        g_l, g_u = hdr_grid(post, r, lo_grid, min(1 - 1e-9, v_u + 0.2 * (v_u - v_l)))
        one_sided = {"equal_tailed": float(post.cdf(theta_of(et[0], r))),
                     "hdi_ve": float(post.cdf(theta_of(v_l, r))), "hdi_theta": float(post.cdf(theta_of(hdi_theta_mapped[0], r)))}
        out[name] = {"split": [yv, yp], "r": r, "equal_tailed": et, "hdi_theta_mapped": hdi_theta_mapped,
                     "hdi_theta": [t_l, t_u], "hdi_theta_lower_mass": t_mass, "hdi_ve": [v_l, v_u],
                     "hdi_ve_upper_tail_mass": v_mass, "hdi_ve_grid": [g_l, g_u], "density_at_hdi_theta": dens_theta,
                     "density_at_hdi_ve": dens_ve, "p_ve_at_least_lower": one_sided,
                     "widths": {"equal_tailed": et[1] - et[0], "hdi_theta_mapped": hdi_theta_mapped[1] - hdi_theta_mapped[0],
                                "hdi_ve": v_u - v_l}}
        print(f"  {name} {yv}:{yp}: equal-tailed VE {pc(et[0], 2)} to {pc(et[1], 2)}%; HDI on theta, mapped "
              f"{pc(hdi_theta_mapped[0], 2)} to {pc(hdi_theta_mapped[1], 2)}%; HDI on VE {pc(v_l, 2)} to {pc(v_u, 2)}% "
              f"(grid {pc(g_l, 2)} to {pc(g_u, 2)}); densities at the VE-HDI ends {sci(dens_ve[0], 4)}, {sci(dens_ve[1], 4)}; "
              f"P(VE >= lower): {pc(one_sided['equal_tailed'], 2)}%, {pc(one_sided['hdi_theta'], 2)}%, {pc(one_sided['hdi_ve'], 2)}%")
    # Coverage at fixed efficacy, and averaged over the prior.
    for name, n, tv, tp, ve_lo in (("primary", 170, 2.214, 2.222, -1.0), ("severe", 4, 2.215, 2.232, -5.0)):
        r = tv / tp
        ve_grid = np.concatenate([np.linspace(ve_lo, 0.9, 1400, endpoint=False), np.linspace(0.9, 0.999, 600)])
        th = theta_of(ve_grid, r)
        cov_cr = coverage_curve(n, r, th, "credible")
        cov_cp = coverage_curve(n, r, th, "clopper_pearson")
        band = (ve_grid >= 0) & (ve_grid <= 0.99)
        # Averaged over the prior: sum over y of the integral of P(y | theta) p(theta) across y's interval, by quadrature.
        ys = np.arange(n + 1)
        t_lo = stats.beta.ppf(0.025, A0 + ys, B0 + n - ys)
        t_hi = stats.beta.ppf(0.975, A0 + ys, B0 + n - ys)
        avg = float(sum(integrate.quad(lambda t, y=y: stats.binom.pmf(y, n, t) * stats.beta.pdf(t, A0, B0),
                                       t_lo[y], t_hi[y], limit=200, epsabs=0, epsrel=1e-11)[0] for y in ys))
        rng = stream(args.seed, "intervals", 0 if name == "primary" else 1)
        S = cfg["coverage_draws"]
        th_draw = rng.beta(A0, B0, S)
        y_draw = rng.binomial(n, th_draw)
        lo_y = stats.beta.ppf(0.025, A0 + y_draw, B0 + n - y_draw)
        hi_y = stats.beta.ppf(0.975, A0 + y_draw, B0 + n - y_draw)
        hit = float(np.mean((lo_y <= th_draw) & (th_draw <= hi_y)))
        mid = (ve_grid >= 0) & (ve_grid <= 0.95)
        out[name]["coverage"] = {"n": n, "ve_grid": ve_grid[::2], "credible": cov_cr[::2], "clopper_pearson": cov_cp[::2],
                                 "credible_min_ve_0_99": float(cov_cr[band].min()), "credible_max_ve_0_99": float(cov_cr[band].max()),
                                 "credible_range_ve_0_95": [float(cov_cr[mid].min()), float(cov_cr[mid].max())],
                                 "cp_range_ve_0_95": [float(cov_cp[mid].min()), float(cov_cp[mid].max())],
                                 "credible_min_at_ve": float(ve_grid[band][np.argmin(cov_cr[band])]),
                                 "credible_max_at_ve": float(ve_grid[band][np.argmax(cov_cr[band])]),
                                 "cp_min_ve_0_99": float(cov_cp[band].min()), "prior_average_quadrature": avg,
                                 "prior_average_mc": hit, "prior_average_mcse": mcse_share(hit, S), "draws": S,
                                 "at_ve": {k: float(coverage_curve(n, r, np.array([theta_of(k / 100, r)]), "credible")[0])
                                           for k in (0, 30, 50, 70, 90, 95)}}
        print(f"  coverage, {name} (n = {n} cases): credible interval {pc(cov_cr[band].min(), 1)}% (at VE "
              f"{pc(out[name]['coverage']['credible_min_at_ve'], 1)}%) to {pc(cov_cr[band].max(), 1)}% (at VE "
              f"{pc(out[name]['coverage']['credible_max_at_ve'], 1)}%) over VE 0 to 99% (Clopper-Pearson at least "
              f"{pc(cov_cp[band].min(), 1)}%); at VE 30, 50, 70, 95%: "
              + ", ".join(f"{pc(v, 1)}%" for k, v in out[name]["coverage"]["at_ve"].items() if k in (30, 50, 70, 95))
              + f"; averaged over the prior {pc(avg, 6)}% by quadrature, {pc(hit, 2)}% +- {pc(mcse_share(hit, S), 2)} "
              f"by simulation (S {S:,}); over VE 0 to 95%: credible {pc(cov_cr[mid].min(), 1)}% to {pc(cov_cr[mid].max(), 1)}%, "
              f"Clopper-Pearson {pc(cov_cp[mid].min(), 1)}% to {pc(cov_cp[mid].max(), 1)}%")
    return out


# ------------------------------------------------------------------------------- stage: priors
NAMED_PRIORS = (("trial", A0, B0), ("senn_alternative", 1.0, 0.5882 / 0.4118), ("uniform", 1.0, 1.0),
                ("jeffreys", 0.5, 0.5), ("haldane", 0.0, 0.0))


def stage_priors(cfg, args):
    print("[priors] how much the prior moves the answer, and what 'flat' means on other scales")
    rows = [("primary", 8, 162, 2.214, 2.222), ("severe", 1, 3, 2.215, 2.232)]
    if args.split:
        rows.append(("yours", args.split[0], args.split[1], args.times[0], args.times[1]))
    named = {}
    for name, yv, yp, tv, tp in rows:
        r = tv / tp
        named[name] = {"split": [yv, yp], "times": [tv, tp]}
        line = []
        for pname, a, b in NAMED_PRIORS:
            if a + yv <= 0 or b + yp <= 0:
                named[name][pname] = None
                line.append(f"{pname} improper")
                continue
            c = credible(yv, yp, r, a, b)
            named[name][pname] = c
            line.append(f"{pname} {pc(c['lower'], 1)} to {pc(c['upper'], 1)}")
        print(f"  {name} {yv}:{yp}: " + "; ".join(line))
    kappas = np.geomspace(0.1, 1000, 81)
    sweep = {}
    for centre_name, m in (("ve30", theta_of(VE_BAR, 1.0)), ("ve0", 0.5)):
        for name, yv, yp, tv, tp in rows[:2]:
            r = tv / tp
            res = [credible(yv, yp, r, k * m, k * (1 - m)) for k in kappas]
            sweep[f"{centre_name}_{name}"] = {"kappa": kappas, "lower": [c["lower"] for c in res],
                                              "upper": [c["upper"] for c in res], "median": [c["median"] for c in res]}
    for key_, k in (("ve30_primary", 1.700102), ("ve30_severe", 1.700102), ("ve0_primary", 170), ("ve0_severe", 4)):
        name = key_.split("_")[1]
        yv, yp, tv, tp = {"primary": (8, 162, 2.214, 2.222), "severe": (1, 3, 2.215, 2.232)}[name]
        m = theta_of(VE_BAR, 1.0) if key_.startswith("ve30") else 0.5
        c = credible(yv, yp, tv / tp, k * m, k * (1 - m))
        sweep[key_]["marker"] = {"kappa": k, "lower": c["lower"], "upper": c["upper"], "median": c["median"]}
        print(f"  prior worth {k:g} cases centred at VE {'30' if m < 0.5 else '0'}%, {name}: VE {pc(c['lower'], 1)} to "
              f"{pc(c['upper'], 1)}%, median {pc(c['median'], 1)}%")
    # "Flat" is a statement about one scale. The uniform prior on theta, seen on the log-odds and VE scales.
    phi = np.linspace(-8, 8, 321)
    theta = special.expit(phi)
    induced = {"phi": phi, "uniform": theta * (1 - theta), "jeffreys": np.sqrt(theta * (1 - theta)) / math.pi,
               "trial": stats.beta.pdf(theta, A0, B0) * theta * (1 - theta)}
    jeffreys_direct = np.sqrt(theta * (1 - theta))                     # sqrt of the Fisher information in phi, n = 1
    ratio = induced["jeffreys"] / jeffreys_direct
    invariance = float(ratio.max() / ratio.min() - 1)
    probs = {}
    for pname, a, b in NAMED_PRIORS[:4]:
        probs[pname] = {"p_ve_gt_30": float(stats.beta.cdf(theta_of(VE_BAR, 1.0), a, b)),
                        "p_ve_lt_0": float(stats.beta.sf(0.5, a, b)),
                        "p_ve_gt_90": float(stats.beta.cdf(theta_of(0.9, 1.0), a, b)),
                        "median_ve": ve_of(float(stats.beta.median(a, b)), 1.0)}
    uni = probs["uniform"]
    print(f"  uniform prior on theta: on the log-odds it is the logistic density, peak {hu(induced['uniform'].max(), 3)} at 0; "
          f"P(VE > 30%) {hu(uni['p_ve_gt_30'], 4)}, P(VE < 0) {hu(uni['p_ve_lt_0'], 4)}, P(VE > 90%) {hu(uni['p_ve_gt_90'], 4)}")
    for pname in ("trial", "senn_alternative", "jeffreys"):
        pr = probs[pname]
        print(f"  {pname}: P(VE > 30%) {hu(pr['p_ve_gt_30'], 4)}, P(VE < 0) {hu(pr['p_ve_lt_0'], 4)}, P(VE > 90%) "
              f"{hu(pr['p_ve_gt_90'], 4)}, prior median VE {pc(pr['median_ve'], 1)}%")
    print(f"  Jeffreys' prior transformed to the log-odds against Jeffreys' rule applied there: ratio constant to {invariance:.1e}")
    return {"named": named, "sweep": sweep, "induced": induced, "prior_probabilities": probs,
            "jeffreys_invariance_rel": invariance}


# ------------------------------------------------------------------------------- stage: lindley
def log_bf01_uniform(n, y):
    """log of the Bayes factor for theta = 1/2 against theta ~ uniform: (n + 1) C(n, y) / 2^n; y may be real."""
    return (math.log(n + 1) + special.gammaln(n + 1) - special.gammaln(y + 1) - special.gammaln(n - y + 1)
            - n * math.log(2))


def log_bf01_beta(n, y, a, b):
    """log Bayes factor for theta = 1/2 against theta ~ beta(a, b)."""
    return -n * math.log(2) + special.betaln(a, b) - special.betaln(a + y, b + n - y)


def stage_lindley(cfg, args):
    print("[lindley] H0: a birth is a boy with probability 1/2, one year of Paris baptisms at a time")
    paris = read_paris()
    years = {}
    for yr in range(1771, 1785):
        y, g = paris[str(yr)]
        n = y + g
        z = (y - g) / math.sqrt(n)
        p_exact = min(1.0, 2 * float(stats.binom.sf(y - 1, n, 0.5)))
        lbf = log_bf01_uniform(n, y)
        bf = math.exp(lbf)
        z_even = optimize.brentq(lambda zz: log_bf01_uniform(n, n / 2 + zz * math.sqrt(n) / 2), 0.5, 6)
        years[str(yr)] = {"boys": y, "girls": g, "n": n, "z": z, "p_exact": p_exact, "p_normal": 2 * float(stats.norm.sf(abs(z))),
                          "bf01": bf, "post_h0": bf / (1 + bf), "post_theta_le_half": float(stats.beta.cdf(0.5, y + 1, g + 1)),
                          "z_break_even": z_even}
    lindley_years = [k for k, v in years.items() if v["p_exact"] < 0.05 and v["bf01"] > 1]
    for k, v in years.items():
        print(f"  {k}: {v['boys']:,} boys of {v['n']:,} (share {hu(v['boys'] / v['n'], 4)}): z {hu(v['z'], 3)}, exact p "
              f"{hu(v['p_exact'], 4)}; BF01 (uniform alternative) {hu(v['bf01'], 3)}, P(H0 | data) {hu(v['post_h0'], 3)}; "
              f"BF01 = 1 at z {hu(v['z_break_even'], 3)}")
    print(f"  years with p < 0.05 and BF01 > 1: {', '.join(lindley_years)}")
    # The focus year in detail.
    y, g = paris[str(LINDLEY_YEAR)]
    n = y + g
    exact_bf = big_ratio((n + 1) * math.comb(n, y), 2 ** n)
    a0, b0 = (v + 1 for v in paris[INFORMED_PERIOD])
    lbf_informed = log_bf01_beta(n, y, a0, b0)
    phat = y / n
    lbf_min = -n * math.log(2) - (y * math.log(phat) + g * math.log(1 - phat))
    kappas = np.geomspace(1e-3, 1e8, 111)
    sweep = [math.exp(log_bf01_beta(n, y, k / 2, k / 2)) for k in kappas]
    post = stats.beta(y + 1, g + 1)
    focus = {"year": LINDLEY_YEAR, "boys": y, "girls": g, "n": n, "bf01_uniform": years[str(LINDLEY_YEAR)]["bf01"],
             "bf01_uniform_exact_integers": exact_bf, "bf01_informed": math.exp(lbf_informed),
             "bf10_informed": math.exp(-lbf_informed), "bf01_minimum": math.exp(lbf_min),
             "bf10_maximum": math.exp(-lbf_min), "kappa": kappas, "bf01_beta_kappa": sweep,
             "estimation": {"interval95": post.ppf([0.025, 0.975]), "p_theta_le_half": float(post.cdf(0.5)),
                            "mean": post.mean()},
             "informed_prior": [a0, b0]}
    print(f"  {LINDLEY_YEAR}: BF01 uniform {hu(focus['bf01_uniform'], 4)} (exact integers {hu(exact_bf, 4)}); against the "
          f"{INFORMED_PERIOD} posterior as H1's prior BF10 {hu(focus['bf10_informed'], 3)}; most H1 can achieve, a spike at "
          f"the observed share: BF10 {hu(focus['bf10_maximum'], 3)}")
    print(f"  {LINDLEY_YEAR} as estimation (uniform prior): 95% interval {hu(focus['estimation']['interval95'][0], 4)} to "
          f"{hu(focus['estimation']['interval95'][1], 4)}, P(theta <= 1/2) {hu(focus['estimation']['p_theta_le_half'], 4)}")
    kk = {k: math.exp(log_bf01_beta(n, y, k / 2, k / 2)) for k in (2, 20, 200, 2_000, 20_000, 200_000)}
    print("  BF01 under beta(k/2, k/2) priors centred at 1/2: " + ", ".join(f"k {k:,}: {hu(v, 3)}" for k, v in kk.items()))
    # Jeffreys' sqrt(n): the Bayes factor at a fixed z as the sample grows.
    ns = np.geomspace(50, 1e8, 121)
    z_obs = years[str(LINDLEY_YEAR)]["z"]
    growth = {}
    for label, zz in (("z_1782", z_obs), ("z_1.96", 1.959963984540054)):
        growth[label] = [math.exp(log_bf01_uniform(m, m / 2 + zz * math.sqrt(m) / 2)) for m in ns]
    cross = {}
    for label, zz in (("z_1782", z_obs), ("z_1.96", 1.959963984540054)):
        f1 = lambda lm, zz=zz: log_bf01_uniform(math.exp(lm), math.exp(lm) / 2 + zz * math.exp(lm / 2) / 2)
        cross[label] = {"bf_1": math.exp(optimize.brentq(f1, math.log(10), math.log(1e9))),
                        "bf_19": math.exp(optimize.brentq(lambda lm: f1(lm) - math.log(19), math.log(10), math.log(1e12)))}
    jeff = math.sqrt(math.log(2 * n / math.pi))
    print(f"  at z = {hu(z_obs, 3)}, BF01 reaches 1 at n = {cross['z_1782']['bf_1']:,.0f} and 19 (P(H0) 0.95) at "
          f"n = {cross['z_1782']['bf_19']:,.0f}; at z = 1.96, at n = {cross['z_1.96']['bf_1']:,.0f} and {cross['z_1.96']['bf_19']:,.0f}. "
          f"Jeffreys' even-odds z for n = {n:,}: sqrt(ln(2n/pi)) = {hu(jeff, 3)}")
    yb, gb = sum(paris[str(k)][0] for k in range(1771, 1785)), sum(paris[str(k)][1] for k in range(1771, 1785))
    pooled = {"boys": yb, "girls": gb, "z": (yb - gb) / math.sqrt(yb + gb),
              "log10_bf01_uniform": log_bf01_uniform(yb + gb, yb) / math.log(10)}
    print(f"  1771-1784 pooled: z {hu(pooled['z'], 2)}, log10 BF01 {hu(pooled['log10_bf01_uniform'], 1)}: both schools reject")
    return {"years": years, "lindley_years": lindley_years, "focus": focus, "kappa_examples": kk, "growth_n": ns,
            "growth": growth, "crossings": cross, "jeffreys_even_z": jeff, "pooled": pooled}


# ------------------------------------------------------------------------------- driver
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
            "bayes_py_sha1": sha1(pathlib.Path(__file__)),
            "data_sha1": {PARIS_CSV.name: sha1(PARIS_CSV), TRIAL_CSV.name: sha1(TRIAL_CSV)}, "budget": budget,
            "seed": args.seed, "draws": QUICK if args.quick else FULL,
            "flags": {"fault": args.fault, "split": args.split, "times": args.times}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo draws (exact values are unchanged)")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261125)
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the pfizer stage's efficacy map")
    parser.add_argument("--split", type=int, nargs=2, metavar=("VACCINE", "PLACEBO"),
                        help="priors: your own case split (with --times)")
    parser.add_argument("--times", type=float, nargs=2, metavar=("VACCINE", "PLACEBO"),
                        help="priors: its surveillance times in 1000 person-years")
    args = parser.parse_args()
    if (args.split is None) != (args.times is None):
        parser.error("--split and --times go together")
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, NumPy {prov['numpy']}, "
          f"SciPy {prov['scipy']}; bayes.py {prov['bayes_py_sha1']}; budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"laplace": stage_laplace, "pfizer": stage_pfizer, "conjugate": stage_conjugate,
             "intervals": stage_intervals, "priors": stage_priors, "lindley": stage_lindley}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
