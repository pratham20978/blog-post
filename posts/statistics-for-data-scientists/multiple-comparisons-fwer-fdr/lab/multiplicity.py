#!/usr/bin/env python3
"""Lab for "Multiple Comparisons: FWER, FDR, and Tests You Didn't Count"
(Canery, Statistics for Data Scientists, Part 9).

Usage
    python multiplicity.py [stage ...] [--quick] [--seed N] [--out FILE.json] [--fault stepdown]

Stages (default: all five, in this order)
    procedures   Bonferroni, Holm, Benjamini-Hochberg, Benjamini-Yekutieli and Storey's q-values
                 on the 3,170 Hedenfalk p-values, by hand, matched to statsmodels and SciPy and
                 to the counts Storey & Tibshirani (2003) published.
    dependence   FWER, FDR and the spread of the false discovery proportion for each rule, on
                 simulated studies shaped like Hedenfalk's, as the tests' correlation rises.
    adversarial  the joint law that pushes Benjamini-Hochberg's FDR to alpha * H_m: exact values
                 and one simulated check.
    forking      Simmons, Nelson & Simonsohn's (2011) researcher degrees of freedom, all nulls true.
    freedman     Freedman's (1983) screening: pure-noise regressors, screen at 0.25, refit.
    recompute    optional: rebuild every p-value from the 317,000 permutation statistics in
                 qvalue's hedenfalk.RData (needs network and `pip install rdata==1.1.0`).

--quick runs the small budget; the article quotes the full budget. Every simulated rate prints
as estimate ± MCSE with its R. Exit status 1 means a reconciliation check failed.
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import platform
import sys
import time
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import scipy
import statsmodels
from scipy import special, stats
from scipy.interpolate import make_smoothing_spline
from scipy.optimize import brentq
from statsmodels.stats.multitest import multipletests

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data" / "hedenfalk.csv"
RDATA_URL = "https://raw.githubusercontent.com/StoreyLab/qvalue/master/data/hedenfalk.RData"
RDATA_SHA256 = "013b681c72b63da1fbc56134a26eabbe8ada3f5760fef7fcd7359aeb1ac8e383"
ALPHA = 0.05
STAGES = ("procedures", "dependence", "adversarial", "forking", "freedman")
STAGE_ID = {name: i for i, name in enumerate(STAGES + ("recompute",), start=1)}
BUDGET = {"full": {"dependence": 20_000, "adversarial": 20_000, "forking": 100_000, "freedman": 20_000},
          "quick": {"dependence": 2_000, "adversarial": 2_000, "forking": 10_000, "freedman": 2_000}}
CHUNK = 500  # simulated studies per batch: 500 x 3,170 doubles is about 13 MB
FAILURES = []


def pc(x, d=1):
    """A share as a percentage, rounded once, half up, from its exact decimal."""
    return f"{(Decimal(repr(float(x))) * 100).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)}%"


def hu(x, d=4):
    """A decimal rounded once, half up, from its exact value. A rate of k/20,000 often ends in 5
    at the fifth place, and f"{x:.4f}" rounds the binary float instead, which can go either way."""
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))


def streams(stage, sub, seed):
    """One independent generator per (stage, sub-experiment, seed)."""
    return np.random.default_rng(np.random.SeedSequence([STAGE_ID[stage], sub, seed]))


def check(name, ok, detail=""):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}{(' - ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)


# ---------------------------------------------------------------------------------------------
# The five rules, by hand, for one vector of p-values. Each returns adjusted p-values: reject
# test i at level a exactly when adjusted[i] <= a.
# ---------------------------------------------------------------------------------------------

def adjust_bonferroni(p):
    return np.minimum(1.0, p.size * p)


def adjust_holm(p):
    """Step-down: compare p_(i) with alpha/(m - i + 1), smallest first; stop at the first failure."""
    m = p.size
    o = np.argsort(p, kind="stable")
    a = np.maximum.accumulate((m - np.arange(m)) * p[o])  # running max keeps the order of rejection
    out = np.empty(m)
    out[o] = np.minimum(1.0, a)
    return out


def adjust_bh(p, c=1.0, fault=None):
    """Step-up: the largest k with p_(k) <= k*alpha/(c*m); reject p_(1)..p_(k). c = H_m gives BY."""
    m = p.size
    o = np.argsort(p, kind="stable")
    r = c * m * p[o] / np.arange(1, m + 1)
    if fault == "stepdown":  # E4's injected slip: Holm's running max where BH needs a running min
        a = np.maximum.accumulate(r)
    else:  # running min from the largest p-value down: a later crossing rescues earlier ranks
        a = np.minimum.accumulate(r[::-1])[::-1]
    out = np.empty(m)
    out[o] = np.minimum(1.0, a)
    return out


def harmonic(m):
    return float(np.sum(1.0 / np.arange(1, m + 1)))


# lambda grids for pi0: the paper (Storey & Tibshirani 2003, Remark B) and qvalue's defaults
LAMBDA = {"paper 2003": np.round(np.arange(0.00, 0.951, 0.01), 2),
          "qvalue 2.x": np.round(np.arange(0.05, 0.951, 0.05), 2),
          "qvalue 1.x": np.round(np.arange(0.00, 0.901, 0.05), 2)}
EVAL_AT = {"paper 2003": 1.0, "qvalue 2.x": 0.95, "qvalue 1.x": 0.90}


def pi0_raw(p, lam):
    """Share of p-values at or above each lambda, over 1 - lambda (qvalue counts p >= lambda)."""
    return np.array([np.mean(p >= l) / (1.0 - l) for l in lam])


_PENALTY = {}


def penalty(recipe, df=3.0):
    """The smoothing penalty that makes the smoother matrix's trace equal df, as R's
    smooth.spline(df = 3) does. Found once per lambda grid."""
    if recipe not in _PENALTY:
        lam = LAMBDA[recipe]
        basis = np.eye(lam.size)

        def trace(log_pen):
            return sum(make_smoothing_spline(lam, e, lam=np.exp(log_pen))(x) for e, x in zip(basis, lam)) - df

        _PENALTY[recipe] = float(np.exp(brentq(trace, -30.0, 10.0)))
    return _PENALTY[recipe]


def smooth(recipe, y, xs):
    """The df-3 natural cubic smoothing spline of (lambda, y), evaluated at xs. Beyond the last
    knot a natural spline is a straight line, so points past max(lambda) extrapolate linearly."""
    lam = LAMBDA[recipe]
    f = make_smoothing_spline(lam, y, lam=penalty(recipe))
    xs = np.atleast_1d(np.asarray(xs, float))
    end = lam[-1]
    return np.where(xs <= end, f(np.minimum(xs, end)), f(end) + (xs - end) * f.derivative()(end))


def smoother_weights(recipe):
    """Row w with w @ y = smooth(recipe, y, EVAL_AT[recipe]): the spline is linear in y."""
    return np.array([float(smooth(recipe, e, EVAL_AT[recipe])[0]) for e in np.eye(LAMBDA[recipe].size)])


WEIGHTS = {}


def pi0_storey(p, recipe="qvalue 2.x"):
    if recipe not in WEIGHTS:
        WEIGHTS[recipe] = smoother_weights(recipe)
    return float(min(WEIGHTS[recipe] @ pi0_raw(p, LAMBDA[recipe]), 1.0))


def qvalues(p, pi0):
    """Storey's q-values: pi0 times the BH-adjusted p-values (qvalue with pfdr = FALSE)."""
    return pi0 * adjust_bh(p)


# ---------------------------------------------------------------------------------------------
# The same rules for a batch of studies at once: rows are studies, columns are tests. Returns
# boolean rejections at level alpha, which is all the simulations need.
# ---------------------------------------------------------------------------------------------

def _threshold_stepup(ps, crit):
    """ps sorted ascending by row, crit (rows or 1) x m. Largest k with ps[k] <= crit[k]."""
    below = ps <= crit
    m = ps.shape[1]
    k = np.where(below.any(1), m - np.argmax(below[:, ::-1], axis=1), 0)
    return np.where(k > 0, np.take_along_axis(ps, np.maximum(k - 1, 0)[:, None], 1)[:, 0], -1.0)


def reject_batch(P, alpha=ALPHA, storey=True):
    R, m = P.shape
    ps = np.sort(P, axis=1)
    k = np.arange(1, m + 1)
    out = {"Bonferroni": P <= alpha / m}
    passes = ps <= alpha / (m - k + 1)
    first_fail = np.where(passes.all(1), m, np.argmin(passes, axis=1))
    thr = np.where(first_fail > 0, np.take_along_axis(ps, np.maximum(first_fail - 1, 0)[:, None], 1)[:, 0], -1.0)
    out["Holm"] = P <= thr[:, None]
    out["BH"] = P <= _threshold_stepup(ps, k * alpha / m)[:, None]
    out["BY"] = P <= _threshold_stepup(ps, k * alpha / (m * harmonic(m)))[:, None]
    if storey:
        recipe = "qvalue 2.x"
        if recipe not in WEIGHTS:
            WEIGHTS[recipe] = smoother_weights(recipe)
        raw = np.stack([(P >= l).mean(1) / (1 - l) for l in LAMBDA[recipe]], 1)
        pi0 = np.clip(raw @ WEIGHTS[recipe], 1.0 / m, 1.0)  # qvalue stops on pi0 <= 0; floor at 1/m
        out["Storey q"] = P <= _threshold_stepup(ps, k[None, :] * alpha / (m * pi0[:, None]))[:, None]
        out["_pi0"] = pi0
    return out


# ---------------------------------------------------------------------------------------------
# Stage 1: the worked example
# ---------------------------------------------------------------------------------------------

def load_hedenfalk():
    rows = [line.split(",") for line in DATA.read_text(encoding="utf-8").splitlines()
            if line and line[0].isdigit()]
    stat = np.array([float(r[1]) for r in rows])
    null_ge = np.array([int(r[2]) for r in rows])
    p = np.array([float(r[3]) for r in rows])
    return stat, null_ge, p


def stage_procedures(args, res):
    stat, null_ge, p = load_hedenfalk()
    m = p.size
    ps = np.sort(p)
    print(f"Hedenfalk: m = {m} tests, p = null_ge / 317000 for every row: {bool(np.all(p == null_ge / 317000))}")
    n05 = int((p <= ALPHA).sum())
    pi_half = float(pi0_raw(p, [0.5])[0])
    print(f"p <= 0.05: {n05} genes; if a share pi0 = {pi_half:.4f} (lambda = 0.5) is null, "
          f"about {pi_half * m * ALPHA:.1f} of the {n05} are expected noise")

    adj = {"Bonferroni": adjust_bonferroni(p), "Holm": adjust_holm(p),
           "BH": adjust_bh(p, fault=args.fault), "BY": adjust_bh(p, c=harmonic(m), fault=args.fault)}
    H = harmonic(m)
    print(f"\nBonferroni threshold alpha/m = {ALPHA / m:.6e}")
    print(f"  p_(2) = {float(ps[1])!r} = {int(round(ps[1] * 317000))}/317000; m * p_(2) == alpha exactly: {m * ps[1] == ALPHA}"
          f" -> '<=' rejects {int((p <= ALPHA / m).sum())}, '<' rejects {int((p < ALPHA / m).sum())}")
    print("  rank  p_(i)        Holm a/(m-i+1)  BH i*a/m       BY i*a/(m*H)")
    for i in range(1, 9):
        print(f"  {i:4d}  {ps[i-1]:.4e}   {ALPHA / (m - i + 1):.4e}      {i * ALPHA / m:.4e}     {i * ALPHA / (m * H):.4e}")
    passes = ps <= np.arange(1, m + 1) * ALPHA / m
    kstar = int(np.nonzero(passes)[0].max()) + 1
    print(f"BH: largest k with p_(k) <= k*alpha/m is k = {kstar}: p_({kstar}) = {ps[kstar-1]:.4e} <= {kstar * ALPHA / m:.4e}")
    fails_below = [int(i) + 1 for i in np.nonzero(~passes[:kstar])[0]]
    print(f"    ranks below k that fail their own line but are rejected anyway (step-up): {len(fails_below)}"
          f"{' e.g. ' + str(fails_below[:6]) if fails_below else ''}")
    print(f"BY: H_m = {H:.6f}; BH at alpha/H_m = {ALPHA / H:.6f}; p_(1) = {ps[0]:.4e} vs {ALPHA / (m * H):.4e}")

    pi0 = {name: pi0_storey(p, name) for name in LAMBDA}
    print("\npi0 estimates (3-df smoothing spline of pi0(lambda)):")
    for name, v in pi0.items():
        g = LAMBDA[name]
        print(f"  {name:10s} lambda {g[0]:.2f}..{g[-1]:.2f} step {g[1] - g[0]:.2f}, value at {EVAL_AT[name]:.2f}: pi0 = {v:.7f}")
    fine = np.round(np.arange(0.0, 1.0001, 0.01), 2)
    res["pi0_lambda_grid"] = {name: {"lambda": LAMBDA[name].tolist(), "raw": pi0_raw(p, LAMBDA[name]).tolist(),
                                     "curve_x": fine.tolist(),
                                     "curve_y": smooth(name, pi0_raw(p, LAMBDA[name]), fine).tolist()}
                              for name in LAMBDA}
    q = {name: qvalues(p, v) for name, v in pi0.items()}
    adj["Storey q"] = q["qvalue 2.x"]

    counts = {name: int((a <= ALPHA).sum()) for name, a in adj.items()}
    print("\nDiscoveries at 5%: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    cuts = (0.03, 0.05, 0.07)
    bh_cuts = [int((adj["BH"] <= c).sum()) for c in cuts]
    q_cuts = {name: [int((qq <= c).sum()) for c in cuts] for name, qq in q.items()}
    print("Against Storey & Tibshirani (2003), cutoffs 0.03 / 0.05 / 0.07:")
    print(f"  q-values, paper recipe : {q_cuts['paper 2003']}   published [80, 160, 231]")
    print(f"  q-values, qvalue 2.x   : {q_cuts['qvalue 2.x']}   q-values, qvalue 1.x: {q_cuts['qvalue 1.x']}")
    print(f"  BH                     : {bh_cuts}   published [21, 88, 153]  (open discrepancy, see README)")
    order = np.argsort(p, kind="stable")
    named = []
    for rank, gene, p_pub, q_pub in ((8, "MSH2", 5.05e-5, 0.013), (47, "PDCD5", 4.79e-4, 0.022), (159, "CTGF", 0.0036, 0.049)):
        i = order[rank - 1]
        named.append({"rank": rank, "gene": gene, "p": float(p[i]), "q_paper_recipe": float(q["paper 2003"][i]),
                      "q_qvalue2": float(q["qvalue 2.x"][i]), "p_published": p_pub, "q_published": q_pub})
        print(f"  rank {rank:3d} ({gene:5s}): p = {p[i]:.3g} (paper {p_pub}), q = {q['paper 2003'][i]:.3f} with the paper's pi0"
              f" (paper {q_pub}); {q['qvalue 2.x'][i]:.3f} with qvalue 2.x")

    print("\nReconciliation (absolute tolerance 1e-12 on adjusted p-values):")
    for ours, sm in (("Bonferroni", "bonferroni"), ("Holm", "holm"), ("BH", "fdr_bh"), ("BY", "fdr_by")):
        rej, padj, *_ = multipletests(p, alpha=ALPHA, method=sm)
        d = float(np.max(np.abs(padj - adj[ours])))
        check(f"{ours} vs statsmodels {statsmodels.__version__} '{sm}'", d <= 1e-12 and bool(np.all(rej == (adj[ours] <= ALPHA))),
              f"max |diff| {d:.1e}, rejections {int(rej.sum())}")
    for ours, sp in (("BH", "bh"), ("BY", "by")):
        d = float(np.max(np.abs(stats.false_discovery_control(p, method=sp) - adj[ours])))
        check(f"{ours} vs SciPy {scipy.__version__} false_discovery_control('{sp}')", d <= 1e-12, f"max |diff| {d:.1e}")
    batch = reject_batch(p[None, :])
    same = all(int(batch[k].sum()) == counts[k] for k in ("Bonferroni", "Holm", "BH", "BY", "Storey q"))
    check("batched rules used by the simulations agree with the rules above", same)
    check("q-values equal pi0 x BH-adjusted p-values", bool(np.allclose(q["qvalue 2.x"], pi0["qvalue 2.x"] * adjust_bh(p), rtol=0, atol=1e-15)))
    print("  R 4.5 p.adjust() and qvalue::qvalue() are the author's private check (not run here).")
    res["procedures"] = {"m": m, "n_p_le_05": n05, "pi0_lambda_half": pi_half, "counts_5pct": counts,
                         "kstar_bh": kstar, "harmonic_m": H, "pi0": pi0, "bh_cuts": bh_cuts, "q_cuts": q_cuts,
                         "named_genes": named, "sorted_p_first_300": ps[:300].tolist()}


# ---------------------------------------------------------------------------------------------
# Stage 2: dependence. Studies shaped like Hedenfalk's: 3,170 one-sided z-tests, two thirds null,
# every non-null shifted by MU, all tests equicorrelated at rho.
# ---------------------------------------------------------------------------------------------

M, PI0, MU = 3170, 0.67, 1.6  # MU puts BH at 5% near the 94 discoveries it made on the real data
RHOS = (0.0, 0.1, 0.2, 0.3, 0.5)
RULES = ("Bonferroni", "Holm", "BH", "BY", "Storey q")
FDP_BINS = np.linspace(0, 1, 51)


def stage_dependence(args, res):
    R = BUDGET[args.budget]["dependence"]
    m1 = M - round(PI0 * M)
    null = np.arange(M) >= m1
    print(f"m = {M}, m0 = {M - m1}, m1 = {m1}, non-null shift {MU}, one-sided z-tests; R = {R} studies per rho")
    out, pi0_summary = {}, {}
    for j, rho in enumerate(RHOS):
        g = streams("dependence", j, args.seed)
        acc = {r: {"V": [], "D": [], "S": []} for r in RULES}
        pi0s = []
        for _ in range(R // CHUNK):
            Z = g.standard_normal((CHUNK, M))
            if rho > 0:
                Z = np.sqrt(rho) * g.standard_normal((CHUNK, 1)) + np.sqrt(1 - rho) * Z
            Z[:, :m1] += MU
            rej = reject_batch(special.ndtr(-Z))
            pi0s.append(rej.pop("_pi0"))
            for r in RULES:
                acc[r]["V"].append((rej[r] & null).sum(1))
                acc[r]["D"].append(rej[r].sum(1))
                acc[r]["S"].append((rej[r] & ~null).sum(1))
        row = {}
        allpi0 = np.concatenate(pi0s)
        q05, q95 = np.quantile(allpi0, [0.05, 0.95])
        pi0_summary[str(rho)] = {"mean": float(allpi0.mean()), "q05": float(q05), "q95": float(q95)}
        print(f"\nrho = {rho}: mean Storey pi0 estimate {hu(allpi0.mean())} "
              f"(true {hu(1 - m1 / M)}), 5th-95th percentile [{hu(q05, 3)}, {hu(q95, 3)}]")
        print("  rule        FWER              FDR               P(FDP > 10%)      FDP p95  mean D   power")
        for r in RULES:
            V, D, S = (np.concatenate(acc[r][k]) for k in ("V", "D", "S"))
            fdp = V / np.maximum(D, 1)
            fw, big = (V > 0).mean(), (fdp > 0.10).mean()
            e = {"FWER": fw, "FWER_se": np.sqrt(fw * (1 - fw) / R), "FDR": fdp.mean(), "FDR_se": fdp.std(ddof=1) / np.sqrt(R),
                 "P_FDP_gt_10": big, "P_FDP_gt_10_se": np.sqrt(big * (1 - big) / R),
                 "FDP_quantiles": dict(zip(("50", "90", "95", "99"), np.quantile(fdp, [0.5, 0.9, 0.95, 0.99]).tolist())),
                 "mean_D": D.mean(), "power": (S / m1).mean(), "P_D_zero": (D == 0).mean()}
            hit = D > 0
            e["P_FDP_gt_10_given_D"] = float((fdp[hit] > 0.10).mean()) if hit.any() else 0.0
            if r == "BH":
                e["FDP_hist"] = np.histogram(fdp[hit], bins=FDP_BINS)[0].tolist()
                e["n_with_discoveries"] = int(hit.sum())
            row[r] = {k: (float(v) if not isinstance(v, (dict, list)) else v) for k, v in e.items()}
            print(f"  {r:10s}  {hu(e['FWER'])} ± {hu(e['FWER_se'])}  {hu(e['FDR'])} ± {hu(e['FDR_se'])}  "
                  f"{hu(e['P_FDP_gt_10'])} ± {hu(e['P_FDP_gt_10_se'])}  {hu(e['FDP_quantiles']['95'], 3)}    "
                  f"{hu(e['mean_D'], 1):>6s}  {hu(e['power'], 3)}")
        for r in ("BH", "Storey q"):
            print(f"  {r}: no discoveries in {hu(row[r]['P_D_zero'])} of studies; among studies with discoveries, "
                  f"P(FDP > 10%) = {hu(row[r]['P_FDP_gt_10_given_D'])}")
        out[str(rho)] = row
    bh0 = out["0.0"]["BH"]
    print(f"\nBH under independence: FDR {hu(bh0['FDR'])} against q * m0/m = {hu(ALPHA * (M - m1) / M)}")
    res["dependence"] = {"R": R, "m": M, "m1": m1, "mu": MU, "rhos": list(RHOS), "fdp_bins": FDP_BINS.tolist(), "by_rho": out,
                         "storey_pi0": pi0_summary}


# ---------------------------------------------------------------------------------------------
# Stage 3: the worst case for BH (Lehmann & Romano 2005, Lemma 3.1; Guo & Rao 2008, Thm 5.1).
# All m hypotheses are null. With probability alpha/k, exactly k p-values fall in the k-th slot
# ((k-1)*alpha/m, k*alpha/m] and the rest in (alpha, 1]; otherwise all fall in (alpha, 1].
# Every p-value is still exactly uniform on (0, 1).
# ---------------------------------------------------------------------------------------------

def stage_adversarial(args, res):
    print("Exact, alpha = 0.05 (all nulls true, so FDR = FWER = P(any rejection)):")
    print("        m    H_m        BH          BY         Bonferroni/Holm")
    exact = {}
    for m in (10, 100, 1000, 3170, 10_000, 100_000):
        H = harmonic(m)
        exact[m] = {"H": H, "BH": ALPHA * H, "BY": ALPHA / H, "Bonferroni": ALPHA, "Holm": ALPHA}
        print(f"  {m:7d}  {H:9.6f}  {ALPHA * H:.6f}    {ALPHA / H:.6f}   {ALPHA:.2f}")
    m, R = 3170, BUDGET[args.budget]["adversarial"]
    H = harmonic(m)
    g = streams("adversarial", 1, args.seed)
    probs = np.concatenate([[1 - ALPHA * H], ALPHA / np.arange(1, m + 1)])
    any_rej = {r: [] for r in ("Bonferroni", "Holm", "BH", "BY")}
    first_col = []
    for _ in range(R // CHUNK):
        k = g.choice(m + 1, size=CHUNK, p=probs)
        P = ALPHA + (1 - ALPHA) * g.random((CHUNK, m))  # everything starts in (alpha, 1]
        cols = np.arange(m)[None, :]
        slot = cols < k[:, None]
        P = np.where(slot, (k[:, None] - 1 + g.random((CHUNK, m))) * ALPHA / m, P)
        P = g.permuted(P, axis=1)  # which tests land in the slot is chosen at random
        first_col.append(P[:, 0].copy())
        rej = reject_batch(P, storey=False)
        for r in any_rej:
            any_rej[r].append(rej[r].any(1))
    ks = stats.kstest(np.concatenate(first_col), "uniform")
    print(f"\nSimulated check, m = {m}, R = {R}: one test's p-value is uniform, KS p = {ks.pvalue:.3f}")
    sim = {}
    for r, v in any_rej.items():
        x = np.concatenate(v).mean()
        sim[r] = {"rate": float(x), "se": float(np.sqrt(x * (1 - x) / R)), "exact": exact[m][r]}
        print(f"  {r:10s} {hu(x)} ± {hu(np.sqrt(x * (1 - x) / R))}   exact {hu(exact[m][r], 6)}")
    res["adversarial"] = {"exact": {str(k): v for k, v in exact.items()}, "sim_m": m, "R": R, "sim": sim,
                          "ks_p": float(ks.pvalue)}


# ---------------------------------------------------------------------------------------------
# Stage 4: researcher degrees of freedom (Simmons, Nelson & Simonsohn 2011, Table 1).
# Normal data, no effect anywhere. Two DVs correlated r = .5 (A: test DV1, DV2 and their mean);
# B: test at 20 per cell, then again after 10 more; C: plain test, + gender, x gender (condition
# or interaction); D: three conditions, all three pairs plus a linear trend coded -1, 0, 1.
# A sample is a false positive if any analysis in the scenario has p < .05.
# ---------------------------------------------------------------------------------------------

SINGULAR = {"fits": 0}


def _ols_p(X, y, cols):
    """Two-sided t-test p-values for the coefficients in cols, one regression per row of X.

    If every subject in a cell has the same gender the interaction model is singular (R's lm
    would drop the term). Such rows, about one sample in 10^5, count as not significant."""
    XtX = X.transpose(0, 2, 1) @ X
    bad = ~(np.abs(np.linalg.det(XtX)) > 1e-8)
    if bad.any():
        SINGULAR["fits"] += int(bad.sum())
        XtX = XtX.copy()
        XtX[bad] = np.eye(X.shape[2])
    inv = np.linalg.inv(XtX)
    b = (inv @ (X.transpose(0, 2, 1) @ y[..., None]))[..., 0]
    resid = y - (X @ b[..., None])[..., 0]
    dfree = X.shape[1] - X.shape[2]
    s2 = (resid ** 2).sum(1) / dfree
    out = [2 * stats.t.sf(np.abs(b[:, c] / np.sqrt(s2 * inv[:, c, c])), dfree) for c in cols]
    for pv in out:
        pv[bad] = 1.0
    return out


SNS_PAPER = {"A two DVs": 0.095, "B ten more per cell": 0.077, "C gender": 0.117, "D three conditions": 0.126,
             "A+B": 0.144, "A+B+C": 0.309, "A+B+C+D": 0.607}


def _sns_hits(g, R, coding):
    n0, n1 = 20, 30
    L = np.linalg.cholesky(np.array([[1.0, 0.5], [0.5, 1.0]]))
    dv = g.standard_normal((R, 3, n1, 2)) @ L.T
    gender = (g.random((R, 3, n1)) < 0.5).astype(float)
    outcomes = (dv[..., 0], dv[..., 1], dv.mean(-1))
    comparisons = ((0, 1), (0, 2), (1, 2), "trend")
    hits = {}
    for d, Y in enumerate(outcomes):
        for s, n in enumerate((n0, n1)):
            for c, comp in enumerate(comparisons):
                cells, codes = (((0, 1, 2), (-1.0, 0.0, 1.0)) if comp == "trend"
                                else (comp, (0.0, 1.0) if coding == "dummy" else (-0.5, 0.5)))
                y = np.concatenate([Y[:, cell, :n] for cell in cells], 1)
                x = np.concatenate([np.full((R, n), code) for code in codes], 1)
                gs = np.concatenate([gender[:, cell, :n] for cell in cells], 1)
                gc = gs if coding == "dummy" else gs - 0.5
                one = np.ones_like(y)
                p_plain = _ols_p(np.stack([one, x], -1), y, [1])[0]
                p_cov = _ols_p(np.stack([one, x, gs], -1), y, [1])[0]
                p_cond, p_int = _ols_p(np.stack([one, x, gc, x * gc], -1), y, [1, 3])
                for t, pv in enumerate((p_plain, p_cov, p_cond, p_int)):
                    hits[(d, s, c, t)] = pv < 0.05
    return hits


def _sns_scenarios(keys):
    """Keys are (outcome, stage, comparison, test); each scenario opens some of the four forks."""
    return {"one t test": [k for k in keys if k == (0, 0, 0, 0)],
            "A two DVs": [k for k in keys if k[1:] == (0, 0, 0)],
            "B ten more per cell": [k for k in keys if k[0] == 0 and k[2:] == (0, 0)],
            "C gender": [k for k in keys if k[:3] == (0, 0, 0)],
            "D three conditions": [k for k in keys if k[0] == 0 and k[1] == 0 and k[3] == 0],
            "A+B": [k for k in keys if k[2:] == (0, 0)],
            "A+B+C": [k for k in keys if k[2] == 0],
            "A+B+C+D": list(keys)}


def stage_forking(args, res):
    R = BUDGET[args.budget]["forking"]
    chunk = min(R, 20_000)
    out = {}
    for j, coding in enumerate(("dummy", "effect")):
        g = streams("forking", j + 1, args.seed)
        tallies = None
        for _ in range(R // chunk):
            hits = _sns_hits(g, chunk, coding)
            sc = _sns_scenarios(list(hits))
            part = {name: np.logical_or.reduce([hits[k] for k in ks]).sum() for name, ks in sc.items()}
            tallies = part if tallies is None else {k: tallies[k] + v for k, v in part.items()}
            n_tests = len(hits)
        out[coding] = {name: {"rate": float(v / R), "se": float(np.sqrt(v / R * (1 - v / R) / R))} for name, v in tallies.items()}
    print(f"R = {R} null samples per coding; {n_tests} p-values per sample in A+B+C+D; "
          f"singular fits counted as not significant: {SINGULAR['fits']}")
    print("  scenario              dummy coding       effect coding      paper (15,000 samples)")
    for name in out["dummy"]:
        a, b = out["dummy"][name], out["effect"][name]
        paper = SNS_PAPER.get(name)
        print(f"  {name:20s}  {hu(a['rate'])} ± {hu(a['se'])}   {hu(b['rate'])} ± {hu(b['se'])}   "
              f"{paper if paper is not None else '-'}")
    res["forking"] = {"R": R, "tests_per_sample": n_tests, "paper": SNS_PAPER, "rates": out,
                      "singular_fits": SINGULAR["fits"]}


# ---------------------------------------------------------------------------------------------
# Stage 5: Freedman's screen. n = 100, 50 regressors and y all independent N(0, 1).
# Pass 1: regress y on all 50 (with intercept). Keep regressors with p < 0.25. Pass 2: refit.
# ---------------------------------------------------------------------------------------------

def _fit(X, y):
    n, k = X.shape
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    rss = float(((y - X @ b) ** 2).sum())
    tss = float(((y - y.mean()) ** 2).sum())
    se = np.sqrt(rss / (n - k) * np.diag(np.linalg.inv(X.T @ X)))
    p = 2 * stats.t.sf(np.abs(b / se), n - k)
    r2 = 1 - rss / tss
    q = k - 1
    F = (r2 / q) / ((1 - r2) / (n - k))
    return p, r2, F, float(stats.f.sf(F, q, n - k))


def stage_freedman(args, res):
    R = BUDGET[args.budget]["freedman"]
    n, k, screen = 100, 50, 0.25
    g = streams("freedman", 1, args.seed)
    rows = []
    for _ in range(R):
        X = g.standard_normal((n, k))
        y = g.standard_normal(n)
        p1, r21, F1, pF1 = _fit(np.column_stack([np.ones(n), X]), y)
        keep = np.nonzero(p1[1:] < screen)[0]
        if keep.size:
            p2, r22, F2, pF2 = _fit(np.column_stack([np.ones(n), X[:, keep]]), y)
            sig2 = int((p2[1:] < 0.05).sum())
        else:
            r22, F2, pF2, sig2 = 0.0, float("nan"), 1.0, 0
        rows.append((r21, pF1, int((p1[1:] < 0.05).sum()), keep.size, r22, F2, pF2, sig2))
    a = np.array(rows, float)
    s1, s2 = (a[:, 1] < 0.05).mean(), (a[:, 6] < 0.05).mean()
    summary = {"R": R, "n": n, "k": k, "screen": screen,
               "R2_pass1": float(a[:, 0].mean()), "R2_pass1_theory": k / (n - 1),
               "P_F_sig_pass1": float(s1), "P_F_sig_pass1_se": float(np.sqrt(s1 * (1 - s1) / R)),
               "sig_slopes_pass1": float(a[:, 2].mean()), "kept": float(a[:, 3].mean()),
               "R2_pass2": float(a[:, 4].mean()), "F_pass2_median": float(np.nanmedian(a[:, 5])),
               "P_F_sig_pass2": float(s2), "P_F_sig_pass2_se": float(np.sqrt(s2 * (1 - s2) / R)),
               "P_F_p001_pass2": float((a[:, 6] < 0.001).mean()), "pF_pass2_median": float(np.median(a[:, 6])),
               "sig_slopes_pass2": float(a[:, 7].mean()),
               "log10_pF_bins": np.arange(-10, 0.01, 0.5).tolist(),
               "hist_pass1": np.histogram(np.log10(np.maximum(a[:, 1], 1e-10)), bins=np.arange(-10, 0.01, 0.5))[0].tolist(),
               "hist_pass2": np.histogram(np.log10(np.maximum(a[:, 6], 1e-10)), bins=np.arange(-10, 0.01, 0.5))[0].tolist()}
    print(f"R = {R} pure-noise datasets, n = {n}, {k} regressors, screen at p < {screen}")
    print(f"  pass 1: mean R^2 {hu(summary['R2_pass1'])} (theory k/(n-1) = {hu(k / (n - 1))}); F significant at 5%: "
          f"{hu(s1)} ± {hu(summary['P_F_sig_pass1_se'])}; slopes significant: {hu(summary['sig_slopes_pass1'], 2)}")
    print(f"  kept after screening: {hu(summary['kept'], 2)} regressors on average")
    print(f"  pass 2: mean R^2 {hu(summary['R2_pass2'])}; median F {hu(summary['F_pass2_median'], 2)}; F significant at 5%: "
          f"{hu(s2)} ± {hu(summary['P_F_sig_pass2_se'])}; at 0.1%: {hu(summary['P_F_p001_pass2'])}; "
          f"median p(F) {summary['pF_pass2_median']:.2e}; slopes significant: {hu(summary['sig_slopes_pass2'], 2)}")
    res["freedman"] = summary


def stage_recompute(args, res):
    try:
        import urllib.request
        import rdata
    except ImportError:
        print("  skipped: optional stage needs `pip install rdata==1.1.0`")
        return
    blob = urllib.request.urlopen(RDATA_URL, timeout=60).read()
    sha = hashlib.sha256(blob).hexdigest()
    check("hedenfalk.RData SHA-256", sha == RDATA_SHA256, sha)
    tmp = HERE / "hedenfalk.RData"
    tmp.write_bytes(blob)
    try:
        h = rdata.conversion.convert(rdata.parser.parse_file(tmp))["hedenfalk"]
    finally:
        tmp.unlink(missing_ok=True)
    stat, stat0 = np.asarray(h["stat"], float), np.asarray(h["stat0"], float)
    null = np.sort(stat0.ravel())
    p_rec = (null.size - np.searchsorted(null, stat, side="left")) / null.size
    _, _, p = load_hedenfalk()
    check(f"p rebuilt from {null.size:,} pooled null statistics equals the shipped p", bool(np.array_equal(p_rec, p)))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stages", nargs="*", metavar="stage",
                    help="procedures, dependence, adversarial, forking, freedman, recompute or all (default)")
    ap.add_argument("--quick", action="store_true", help="small budget (minutes become seconds)")
    ap.add_argument("--seed", type=int, default=9)
    ap.add_argument("--out", type=pathlib.Path, help="write the results as JSON here")
    ap.add_argument("--fault", choices=["stepdown"], help="E4: run BH as a step-down rule")
    args = ap.parse_args()
    args.budget = "quick" if args.quick else "full"
    unknown = [s for s in args.stages if s not in STAGES + ("recompute", "all")]
    if unknown:
        ap.error(f"unknown stage(s): {', '.join(unknown)}")
    stages = list(STAGES) if (not args.stages or "all" in args.stages) else args.stages
    stamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    print(f"Captured {stamp} on {platform.platform()} ({platform.machine()}), Python {platform.python_version()}, "
          f"NumPy {np.__version__}, SciPy {scipy.__version__}, statsmodels {statsmodels.__version__}; "
          f"budget {args.budget}, seed {args.seed}" + (f", fault {args.fault}" if args.fault else ""))
    res = {"captured": stamp, "budget": args.budget, "seed": args.seed, "fault": args.fault,
           "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__,
                        "statsmodels": statsmodels.__version__}}
    for name in stages:
        t0 = time.time()
        print(f"\n== {name} " + "=" * (60 - len(name)))
        globals()[f"stage_{name}"](args, res)
        print(f"({name}: {time.time() - t0:.1f} s)")
    if args.out:
        args.out.write_text(json.dumps(res, indent=1, default=float), encoding="utf-8")
        print(f"\nwrote {args.out}")
    if FAILURES:
        print(f"\n{len(FAILURES)} reconciliation check(s) FAILED: {', '.join(FAILURES)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
