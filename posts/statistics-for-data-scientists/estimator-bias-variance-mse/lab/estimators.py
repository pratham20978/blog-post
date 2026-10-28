#!/usr/bin/env python3
"""Lab for "Estimators and Their Errors: Bias, Variance, and Why the Best One Can Be Biased".

Every number the article calls measured comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python estimators.py all --out mine.json            # every stage, the article's budget (about 2 minutes)
    python estimators.py all --quick --out quick.json   # the reader's budget (about 15 seconds), noisier
    python estimators.py tanks --out mine.json          # one stage

Stages:
    tanks        the German tank problem with N = 342 tanks and k = 5 captured: one capture worked by hand,
                 then six estimators' sampling distributions, bias, variance and MSE, simulated and exact;
                 the Rao-Blackwell step from 2 x mean - 1 to the minimum-variance unbiased estimator; and
                 Ruggles and Brodie's 1947 comparison with the German records
    consistency  the same estimators as k grows from 1 to 100: which errors shrink, how fast, and which never do
    divisors     the variance estimator sum of squares / d for d = n - 1, n, n + 1 and the best d, on normal,
                 uniform and exponential data; the bias of s
    baseball     Efron and Morris's 18 batters of 1970: James-Stein on the raw and arcsine scales, both
                 published comparisons recomputed, then the season replayed by simulation
    stein        the total risk of James-Stein against the separate means for 18 normal means, simulated and
                 exact, as the true means spread out

Every simulated quantity is printed as estimate +- MCSE (its Monte Carlo standard error) with the number
of replications R, and set against its exact value wherever one exists. Every stage draws from its own
stream, SeedSequence([stage, sub-stream, seed]), so stages can run alone and repeat to the bit with the
same NumPy version.
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
BATTING_CSV = DATA / "efron_morris_1975_batting.csv"
TANKS_CSV = DATA / "ruggles_brodie_1947_tanks.csv"
STAGES = ("tanks", "consistency", "divisors", "baseball", "stein")

# Replications. The article quotes FULL; --quick is the reader's first run. Each is a multiple of BATCHES.
FULL = dict(tanks=1_000_000, consistency=200_000, divisors=1_000_000, sd_bias=200_000, baseball=200_000,
            stein=100_000)
QUICK = dict(tanks=100_000, consistency=20_000, divisors=100_000, sd_bias=20_000, baseball=20_000,
             stein=10_000)
BATCHES = 20                            # batch means: MCSE of a ratio is the SD over 20 equal batches / sqrt(20)
ROWS = 50_000                           # rows per block; fixed, so results do not depend on the machine
ESTIMATORS = ("mle", "mvue", "minmse", "mom", "first", "spread")
LABELS = {"mle": "MLE  m", "mvue": "MVUE m(1 + 1/k) - 1", "minmse": "m(k + 2)/(k + 1) - 1",
          "mom": "2 x mean - 1", "first": "2 x first - 1", "spread": "(max - min)(1 + 2/(k - 1)) - 1"}


# ------------------------------------------------------------------------------- small helpers
def stream(seed, stage, sub=0):
    """An independent generator for (stage, sub-stream): varying ids first, the root seed last."""
    return np.random.default_rng(np.random.SeedSequence([STAGES.index(stage), sub, seed]))


class Moments:
    """Running sums of an error e over replications, kept per batch: bias, variance and MSE with MCSEs."""

    def __init__(self):
        self.s = np.zeros((BATCHES, 5))            # per batch: count, sum e, sum e^2, sum e^3, sum e^4

    def add(self, batch, e):
        e = np.asarray(e, float)
        self.s[batch] += (e.size, e.sum(), (e ** 2).sum(), (e ** 3).sum(), (e ** 4).sum())

    def summary(self):
        r, s1, s2, s3, s4 = self.s.sum(0)
        mean, m2 = s1 / r, s2 / r
        var = m2 - mean ** 2
        c4 = s4 / r - 4 * mean * s3 / r + 6 * mean ** 2 * m2 - 3 * mean ** 4   # E(e - mean)^4
        return {"R": int(r), "bias": mean, "bias_mcse": math.sqrt(var / r), "var": var,
                "var_mcse": math.sqrt(max(c4 - var ** 2, 0) / r), "sd": math.sqrt(var),
                "mse": m2, "mse_mcse": math.sqrt(max(s4 / r - m2 ** 2, 0) / r), "rmse": math.sqrt(m2)}

    def batch_mse(self):
        return self.s[:, 2] / self.s[:, 0]


def ratio_mcse(num, den):
    """A ratio of two per-batch quantities: the ratio of totals, and the SD of the batch ratios / sqrt(B)."""
    num, den = np.asarray(num, float), np.asarray(den, float)
    return {"ratio": float(num.mean() / den.mean()), "mcse": float((num / den).std(ddof=1) / math.sqrt(len(num)))}


def fmt(x, mcse, digits=2):
    return f"{x:,.{digits}f} +- {mcse:,.{digits}f}"


# ------------------------------------------------------------------------------- the German tank problem
def capture(rng, n_tanks, k, rows, fault=False):
    """rows captures of k distinct serial numbers from 1..N, every k-subset equally likely (Floyd's
    algorithm: for j = N - k + 1..N draw t from 1..j, and take j instead if t is already in the set).
    fault=True is the E4 exercise: an earlier draft that drew t with rng.integers(j), which gives 0..j - 1."""
    s = np.empty((rows, k), dtype=np.int64)
    for i, j in enumerate(range(n_tanks - k + 1, n_tanks + 1)):
        t = rng.integers(0, j, size=rows) if fault else rng.integers(1, j + 1, size=rows)
        top = j - 1 if fault else j
        if i:
            t = np.where((s[:, :i] == t[:, None]).any(1), top, t)
        s[:, i] = t
    return s


def tank_estimates(s, k, rng):
    """All six estimates of N from each row of serial numbers."""
    m = s.max(1).astype(float)
    pick = s[np.arange(len(s)), rng.integers(0, k, size=len(s))]      # one captured tank, chosen at random
    out = {"mle": m, "mvue": m * (1 + 1 / k) - 1, "minmse": m * (k + 2) / (k + 1) - 1,
           "mom": 2 * s.mean(1) - 1, "first": 2.0 * pick - 1}
    if k > 1:
        out["spread"] = (m - s.min(1)) * (1 + 2 / (k - 1)) - 1
    return out


def exact_tanks(n_tanks, k):
    """Exact mean, bias, variance and MSE of each estimator, from the distributions of the maximum and of the
    spread under sampling without replacement: P(M = m) = C(m - 1, k - 1) / C(N, k)."""
    total = math.comb(n_tanks, k)
    ms = np.arange(k, n_tanks + 1, dtype=float)
    pm = np.array([math.comb(int(m) - 1, k - 1) / total for m in ms])
    out = {}

    def from_pmf(values, p):
        mean = float((values * p).sum())
        var = float(((values - mean) ** 2 * p).sum())
        return mean, var

    for name, g in (("mle", ms), ("mvue", ms * (1 + 1 / k) - 1), ("minmse", ms * (k + 2) / (k + 1) - 1)):
        out[name] = from_pmf(g, pm)
    pop_var = (n_tanks ** 2 - 1) / 12                     # variance of one serial number, uniform on 1..N
    fpc = (n_tanks - k) / (n_tanks - 1) if n_tanks > 1 else 0.0
    out["mom"] = (float(n_tanks), 4 * pop_var / k * fpc)
    out["first"] = (float(n_tanks), 4 * pop_var)
    if k > 1:
        ss = np.arange(k - 1, n_tanks, dtype=float)      # spread = max - min
        ps = np.array([(n_tanks - s) * math.comb(int(s) - 1, k - 2) / total for s in ss])
        out["spread"] = from_pmf(ss * (1 + 2 / (k - 1)) - 1, ps)
    res = {}
    for name, (mean, var) in out.items():
        bias = mean - n_tanks
        res[name] = {"mean": mean, "bias": bias, "var": var, "sd": math.sqrt(var), "mse": var + bias ** 2,
                     "rmse": math.sqrt(var + bias ** 2)}
    return res, pm.tolist()


def read_ruggles_brodie():
    rows = [ln.split(",") for ln in TANKS_CSV.read_text(encoding="utf-8").splitlines()
            if ln and not ln.startswith("#")][1:]
    out = []
    for month, intel, serial, records in rows:
        intel, serial, records = int(intel), int(serial), int(records)
        out.append({"month": month, "intelligence": intel, "serial_number": serial, "records": records,
                    "serial_error": serial - records, "serial_error_pct": 100 * (serial - records) / records,
                    "intelligence_ratio": intel / records})
    return out


def stage_tanks(cfg, args):
    n_tanks, k, reps = args.N, args.k, cfg["tanks"]
    exact, pmf = exact_tanks(n_tanks, k)
    rng = stream(args.seed, "tanks", 0)
    names = [e for e in ESTIMATORS if k > 1 or e != "spread"]
    mom = {e: Moments() for e in names}
    edges = np.arange(0, 2 * n_tanks + 6, 5.0)
    hist = {e: np.zeros(len(edges) - 1, dtype=np.int64) for e in names}
    lo, hi = n_tanks, 0
    cond_sum = np.zeros(n_tanks + 2)                      # Rao-Blackwell: 2 x mean - 1 summed by its maximum m
    cond_sq = np.zeros(n_tanks + 2)
    cond_n = np.zeros(n_tanks + 2)
    keep_m, keep_mom = [], []
    closer = {"mvue_vs_mle": 0, "minmse_vs_mvue": 0, "mle_hits_N": 0}
    per_batch = reps // BATCHES
    for b in range(BATCHES):
        done = 0
        while done < per_batch:
            rows = min(ROWS, per_batch - done)
            s = capture(rng, n_tanks, k, rows, fault=args.fault)
            lo, hi = min(lo, int(s.min())), max(hi, int(s.max()))
            est = tank_estimates(s, k, rng)
            for e in names:
                mom[e].add(b, est[e] - n_tanks)
                hist[e] += np.histogram(est[e], bins=edges)[0]
            err = {e: np.abs(est[e] - n_tanks) for e in ("mle", "mvue", "minmse")}
            closer["mvue_vs_mle"] += int((err["mvue"] < err["mle"]).sum())
            closer["minmse_vs_mvue"] += int((err["minmse"] < err["mvue"]).sum())
            closer["mle_hits_N"] += int((est["mle"] == n_tanks).sum())
            m = s.max(1)
            cond_sum += np.bincount(m, weights=est["mom"], minlength=n_tanks + 2)[:n_tanks + 2]
            cond_sq += np.bincount(m, weights=est["mom"] ** 2, minlength=n_tanks + 2)[:n_tanks + 2]
            cond_n += np.bincount(m, minlength=n_tanks + 2)[:n_tanks + 2]
            if len(keep_m) * ROWS < 3000:
                keep_m.append(m[:3000].tolist())
                keep_mom.append(est["mom"][:3000].tolist())
            done += rows
    sim = {e: mom[e].summary() for e in names}
    out = {"N": n_tanks, "k": k, "R": reps, "fault": args.fault, "exact": exact, "sim": sim,
           "serials_drawn": [lo, hi], "pmf_max": pmf, "hist_edges": edges.tolist(),
           "hist": {e: hist[e].tolist() for e in names}}
    out["z_vs_exact"] = {e: {"bias": (sim[e]["bias"] - exact[e]["bias"]) / sim[e]["bias_mcse"],
                             "mse": (sim[e]["mse"] - exact[e]["mse"]) / sim[e]["mse_mcse"]} for e in names}
    out["shares"] = {key: {"p": v / reps, "mcse": math.sqrt(v / reps * (1 - v / reps) / reps)} for key, v in closer.items()}
    out["shares"]["mle_hits_N"]["exact"] = k / n_tanks           # P(M = N): the last tank is among the k
    out["mse_ratio_mle_mvue"] = ratio_mcse(mom["mle"].batch_mse(), mom["mvue"].batch_mse())
    out["mse_ratio_mle_mvue"]["exact"] = exact["mle"]["mse"] / exact["mvue"]["mse"]
    out["mse_ratio_minmse_mvue"] = ratio_mcse(mom["minmse"].batch_mse(), mom["mvue"].batch_mse())
    out["mse_ratio_minmse_mvue"]["exact"] = exact["minmse"]["mse"] / exact["mvue"]["mse"]
    out["var_ratio_mom_mvue"] = {"exact": exact["mom"]["var"] / exact["mvue"]["var"], "theory": (k + 2) / 3}
    out["var_ratio_mom_mvue"].update(ratio_mcse(
        mom["mom"].s[:, 2] / mom["mom"].s[:, 0] - (mom["mom"].s[:, 1] / mom["mom"].s[:, 0]) ** 2,
        mom["mvue"].s[:, 2] / mom["mvue"].s[:, 0] - (mom["mvue"].s[:, 1] / mom["mvue"].s[:, 0]) ** 2))
    # the best multiplier a in a m - 1 for this N (an oracle: it needs N), against the usable (k + 2)/(k + 1)
    ms = np.arange(k, n_tanks + 1, dtype=float)
    pm = np.array(pmf)
    out["oracle_multiplier"] = float((n_tanks + 1) * (ms * pm).sum() / (ms ** 2 * pm).sum())
    # Rao-Blackwell: the mean of 2 x mean - 1 among captures with the same maximum m, against m(1 + 1/k) - 1
    ok = cond_n >= 1000
    mm = np.nonzero(ok)[0]
    cmean = cond_sum[ok] / cond_n[ok]
    csd = np.sqrt(np.maximum(cond_sq[ok] / cond_n[ok] - cmean ** 2, 0))
    z = (cmean - (mm * (1 + 1 / k) - 1)) / (csd / np.sqrt(cond_n[ok]))
    fit = {"slope": None, "slope_se": None, "intercept": None, "intercept_se": None}
    if len(mm) >= 3:                                      # weighted least squares, weights = count / within-m variance
        xw = np.column_stack([mm, np.ones(len(mm))]).astype(float)
        wt = cond_n[ok] / csd ** 2
        cov = np.linalg.inv(xw.T @ (xw * wt[:, None]))
        coef = cov @ (xw.T @ (wt * cmean))
        fit = {"slope": float(coef[0]), "slope_se": float(math.sqrt(cov[0, 0])),
               "intercept": float(coef[1]), "intercept_se": float(math.sqrt(cov[1, 1]))}
    out["rao_blackwell"] = {"m": mm.tolist(), "cond_mean": cmean.tolist(), "cond_sd": csd.tolist(),
                            "count": cond_n[ok].astype(int).tolist(), "z": z.tolist(), "sum_z2": float((z ** 2).sum()),
                            "fit": fit, "scatter_m": sum(keep_m, [])[:3000], "scatter_mom": sum(keep_mom, [])[:3000]}
    out["count_by_max"] = cond_n.astype(int).tolist()      # captures per value of the maximum m: the MLE's distribution
    # one capture, worked by hand in the article
    s1 = np.sort(capture(stream(args.seed, "tanks", 1), n_tanks, k, 1, fault=args.fault)[0])
    one = tank_estimates(s1[None, :], k, stream(args.seed, "tanks", 2))
    out["worked"] = {"serials": s1.tolist(), "max": int(s1.max()), "mean": float(s1.mean()),
                     "gaps": np.diff(np.concatenate([[0], s1])).tolist(),
                     "estimates": {e: float(v[0]) for e, v in one.items()}}
    out["ruggles_brodie"] = read_ruggles_brodie()

    print(f"tanks: N = {n_tanks} tanks with serial numbers 1..{n_tanks}, k = {k} captured without replacement, "
          f"R = {reps:,}{'  [--fault]' if args.fault else ''}")
    w = out["worked"]
    print(f"  one capture: serials {w['serials']}, max {w['max']}, mean {w['mean']:.1f}; gaps {w['gaps']}")
    print("    estimates: " + ", ".join(f"{e} {v:.1f}" for e, v in w["estimates"].items()))
    print(f"  serial numbers drawn ran from {lo} to {hi}")
    print(f"  {'estimator':32s} {'bias sim':>18s} {'exact':>8s}  {'SD sim':>8s} {'exact':>7s}  {'MSE sim':>20s} {'exact':>9s}  RMSE")
    for e in names:
        si, ex = sim[e], exact[e]
        print(f"  {LABELS[e]:32s} {fmt(si['bias'], si['bias_mcse']):>18s} {ex['bias']:8.2f}  {si['sd']:8.2f} "
              f"{ex['sd']:7.2f}  {fmt(si['mse'], si['mse_mcse'], 0):>20s} {ex['mse']:9.1f}  {ex['rmse']:.1f}")
    r1, r2, r3 = out["mse_ratio_mle_mvue"], out["mse_ratio_minmse_mvue"], out["var_ratio_mom_mvue"]
    print(f"  MSE ratio MLE / MVUE: {r1['ratio']:.4f} +- {r1['mcse']:.4f} (exact {r1['exact']:.4f}); "
          f"m(k+2)/(k+1) - 1 / MVUE: {r2['ratio']:.4f} +- {r2['mcse']:.4f} (exact {r2['exact']:.4f})")
    print(f"  best multiplier a in a m - 1 for this N: {out['oracle_multiplier']:.4f}; (k + 2)/(k + 1) = {(k + 2) / (k + 1):.4f}")
    sh = out["shares"]
    print(f"  the MVUE is closer to N than the MLE in {100 * sh['mvue_vs_mle']['p']:.2f}% +- {100 * sh['mvue_vs_mle']['mcse']:.2f} "
          f"of captures; m(k+2)/(k+1) - 1 is closer than the MVUE in {100 * sh['minmse_vs_mvue']['p']:.2f}% +- "
          f"{100 * sh['minmse_vs_mvue']['mcse']:.2f}; the MLE equals N in {100 * sh['mle_hits_N']['p']:.2f}% +- "
          f"{100 * sh['mle_hits_N']['mcse']:.2f} (exact k/N = {100 * k / n_tanks:.2f}%)")
    rb, ft = out["rao_blackwell"], out["rao_blackwell"]["fit"]
    print(f"  Rao-Blackwell: Var(2 x mean - 1) / Var(MVUE) = {r3['ratio']:.4f} +- {r3['mcse']:.4f} "
          f"(exact {r3['exact']:.4f}, (k + 2)/3 = {r3['theory']:.4f})")
    if ft["slope"] is not None:
        print(f"    the mean of 2 x mean - 1 among captures with the same maximum m, over the {len(rb['m'])} values of m "
              f"with 1,000+ captures, lies on a line with slope {ft['slope']:.4f} +- {ft['slope_se']:.4f} and intercept "
              f"{ft['intercept']:.2f} +- {ft['intercept_se']:.2f}; m(1 + 1/k) - 1 has slope {1 + 1 / k:.4f} and intercept -1")
    for row in out["ruggles_brodie"]:
        print(f"  {row['month']:12s} intelligence {row['intelligence']:5,d} ({row['intelligence_ratio']:.2f} x records), "
              f"serial numbers {row['serial_number']:4d} ({row['serial_error']:+d}, {row['serial_error_pct']:+.1f}%), "
              f"German records {row['records']}")
    return out


def stage_consistency(cfg, args):
    n_tanks, reps = args.N, cfg["consistency"]
    ks = [k for k in range(1, 101) if k <= n_tanks]
    exact = {}
    for k in ks:
        ex, _ = exact_tanks(n_tanks, k)
        exact[str(k)] = {e: {"bias": v["bias"], "rmse": v["rmse"], "mse": v["mse"]} for e, v in ex.items()}
    sim = {}
    for i, k in enumerate(kk for kk in (2, 5, 10, 20, 50, 100) if kk <= n_tanks):
        rng = stream(args.seed, "consistency", i)
        mom = {e: Moments() for e in ESTIMATORS}
        per_batch = reps // BATCHES
        for b in range(BATCHES):
            done = 0
            while done < per_batch:
                rows = min(ROWS // 5, per_batch - done)
                est = tank_estimates(capture(rng, n_tanks, k, rows), k, rng)
                for e in ESTIMATORS:
                    mom[e].add(b, est[e] - n_tanks)
                done += rows
        sim[str(k)] = {e: mom[e].summary() for e in ESTIMATORS}
    out = {"N": n_tanks, "ks": ks, "exact": exact, "sim": sim, "R": reps}
    print(f"consistency: N = {n_tanks}; exact RMSE in tanks (simulated, R = {reps:,}, where shown)")
    print(f"  {'k':>4s} " + " ".join(f"{e:>17s}" for e in ESTIMATORS))
    for k in (1, 2, 5, 10, 20, 50, 100):
        if k > n_tanks:
            continue
        cells = []
        for e in ESTIMATORS:
            ex = exact[str(k)].get(e)
            if ex is None:
                cells.append(f"{'-':>17s}")
                continue
            si = sim.get(str(k), {}).get(e)
            cells.append(f"{ex['rmse']:8.1f}" + (f" ({si['rmse']:6.1f})" if si else " " * 9))
        print(f"  {k:4d} " + " ".join(cells))
    a, b = exact["10"], exact["100"]
    print(f"  k 10 -> 100: MVUE RMSE / {a['mvue']['rmse'] / b['mvue']['rmse']:.1f}, 2 x mean - 1 / "
          f"{a['mom']['rmse'] / b['mom']['rmse']:.1f}, 2 x first - 1 / {a['first']['rmse'] / b['first']['rmse']:.1f}; "
          f"MLE bias at k = 100: {b['mle']['bias']:.2f}")
    return out


# ------------------------------------------------------------------------------- the variance estimator
POPULATIONS = {   # unit variance; excess kurtosis kappa
    "normal": (lambda rng, shape: rng.standard_normal(shape), 0.0),
    "uniform": (lambda rng, shape: rng.uniform(-math.sqrt(3), math.sqrt(3), shape), -1.2),
    "exponential": (lambda rng, shape: rng.exponential(1.0, shape), 6.0),
}


def c4(n):
    """E[s] / sigma for normal data with divisor n - 1: sqrt(2/(n - 1)) Gamma(n/2) / Gamma((n - 1)/2)."""
    return math.sqrt(2 / (n - 1)) * math.exp(math.lgamma(n / 2) - math.lgamma((n - 1) / 2))


def mse_divisor(n, d, kappa):
    """Exact MSE of (sum of squares)/d for sigma^2 = 1: [(n - 1)^2 Var(s^2) + (n - 1 - d)^2] / d^2,
    with Var(s^2) = 2/(n - 1) + kappa/n."""
    return ((n - 1) ** 2 * (2 / (n - 1) + kappa / n) + (n - 1 - d) ** 2) / d ** 2


def stage_divisors(cfg, args):
    n, reps = args.n, cfg["divisors"]
    grid = np.round(np.arange(max(1.0, n - 4.0), 2.0 * n + 12.01, 0.1), 2)
    out = {"n": n, "R": reps, "grid": grid.tolist(), "populations": {}}
    print(f"divisors: sum of squares / d as an estimate of sigma^2 = 1, samples of n = {n}, R = {reps:,} per population")
    for i, (name, (draw, kappa)) in enumerate(POPULATIONS.items()):
        rng = stream(args.seed, "divisors", i)
        best = n + 1 + (n - 1) * kappa / n
        ds = {"n-1": n - 1, "n": n, "n+1": n + 1, "best": best}
        mom = {key: Moments() for key in ds}
        sums = np.zeros((BATCHES, 3))                     # count, sum SS, sum SS^2
        per_batch = reps // BATCHES
        for b in range(BATCHES):
            done = 0
            while done < per_batch:
                rows = min(ROWS * 4, per_batch - done)
                x = draw(rng, (rows, n))
                ss = ((x - x.mean(1, keepdims=True)) ** 2).sum(1)
                sums[b] += (rows, ss.sum(), (ss ** 2).sum())
                for key, d in ds.items():
                    mom[key].add(b, ss / d - 1.0)
                done += rows
        e_ss, e_ss2 = sums[:, 1].sum() / reps, sums[:, 2].sum() / reps
        d_hat = ratio_mcse(sums[:, 2] / sums[:, 0], sums[:, 1] / sums[:, 0])
        res = {"kappa": kappa, "best_d_theory": best, "best_d_sim": d_hat,
               "mean_s2_unbiased": e_ss / (n - 1), "at": {}}
        for key, d in ds.items():
            sm = mom[key].summary()
            res["at"][key] = {"d": d, "bias": sm["bias"], "bias_mcse": sm["bias_mcse"], "mse": sm["mse"],
                              "mse_mcse": sm["mse_mcse"], "mse_exact": mse_divisor(n, d, kappa)}
        res["curve_sim"] = (e_ss2 / grid ** 2 - 2 * e_ss / grid + 1).tolist()
        res["curve_exact"] = [mse_divisor(n, d, kappa) for d in grid]
        r = ratio_mcse(mom["n-1"].batch_mse(), mom["n+1"].batch_mse())
        res["mse_ratio_nm1_np1"] = {**r, "exact": mse_divisor(n, n - 1, kappa) / mse_divisor(n, n + 1, kappa)}
        r = ratio_mcse(mom["best"].batch_mse(), mom["n-1"].batch_mse())
        res["mse_ratio_best_nm1"] = {**r, "exact": mse_divisor(n, best, kappa) / mse_divisor(n, n - 1, kappa)}
        out["populations"][name] = res
        at = res["at"]
        print(f"  {name:11s} excess kurtosis {kappa:+.1f}: mean of s^2 (divisor n - 1) = {res['mean_s2_unbiased']:.4f}")
        for key in ds:
            a = at[key]
            print(f"    d = {a['d']:5.2f} ({key:4s}): bias {fmt(a['bias'], a['bias_mcse'], 4)}, "
                  f"MSE {fmt(a['mse'], a['mse_mcse'], 4)} (exact {a['mse_exact']:.4f})")
        print(f"    best divisor: n + 1 + (n - 1) kappa / n = {best:.2f}; simulated {d_hat['ratio']:.2f} +- {d_hat['mcse']:.2f}; "
              f"MSE(n - 1) / MSE(n + 1) = {res['mse_ratio_nm1_np1']['ratio']:.4f} (exact {res['mse_ratio_nm1_np1']['exact']:.4f}); "
              f"MSE(best) / MSE(n - 1) = {res['mse_ratio_best_nm1']['exact']:.4f}")
    # the bias of s for normal data, and how the n - 1 versus n + 1 gap closes with n
    out["sd_bias"] = {}
    for j, m in enumerate((2, 3, 5, 10, 30, 100)):
        rng = stream(args.seed, "divisors", 10 + j)
        reps_m = cfg["sd_bias"]
        acc = np.zeros((BATCHES, 2))
        per_batch = reps_m // BATCHES
        for b in range(BATCHES):
            done = 0
            while done < per_batch:
                rows = min(max(1, 2_000_000 // m), per_batch - done)
                s = rng.standard_normal((rows, m)).std(1, ddof=1)
                acc[b] += (s.sum(), rows)
                done += rows
        means = acc[:, 0] / acc[:, 1]
        out["sd_bias"][str(m)] = {"sim": float(means.mean()), "mcse": float(means.std(ddof=1) / math.sqrt(BATCHES)),
                                  "exact": c4(m), "R": reps_m, "mse_ratio_nm1_np1": (m + 1) / (m - 1)}
    out["c4_curve"] = {str(m): c4(m) for m in range(2, 101)}
    print("  normal data, E[s] / sigma with divisor n - 1 (exact c4) and the exact MSE ratio of divisors n - 1 and n + 1:")
    print("    " + "; ".join(f"n = {m}: {v['sim']:.4f} +- {v['mcse']:.4f} ({v['exact']:.4f}), ratio {v['mse_ratio_nm1_np1']:.3f}"
                           for m, v in out["sd_bias"].items()))
    return out


# ------------------------------------------------------------------------------- Stein's paradox
def read_batting():
    rows = [ln.split(",") for ln in BATTING_CSV.read_text(encoding="utf-8").splitlines()
            if ln and not ln.startswith("#")][1:]
    names = [r[0] for r in rows]
    hits = np.array([int(r[3]) for r in rows])
    at_bats_rest = np.array([int(r[4]) for r in rows])
    rest = np.array([float(r[5]) for r in rows])
    return names, hits, at_bats_rest, rest


def arcsine(y, n=45):
    """Efron and Morris's variance-stabilising transform: sqrt(n) arcsin(2y - 1), variance near 1."""
    return math.sqrt(n) * np.arcsin(2 * np.asarray(y, float) - 1)


def js_raw(y, n=45):
    """The 1977 rule on raw averages: z = ybar + c (y - ybar), c = 1 - (k - 3) sigma^2 / sum (y - ybar)^2,
    with sigma^2 = ybar (1 - ybar) / n, the binomial variance of one average. Works row-wise."""
    y = np.atleast_2d(y)
    k = y.shape[1]
    ybar = y.mean(1, keepdims=True)
    c = 1 - (k - 3) * (ybar * (1 - ybar) / n) / ((y - ybar) ** 2).sum(1, keepdims=True)
    return ybar + c * (y - ybar), c[:, 0]


def js_grand_mean(x):
    """The 1975 rule for unit-variance normal x: xbar + (1 - (k - 3)/V)(x - xbar), V = sum (x - xbar)^2."""
    x = np.atleast_2d(x)
    k = x.shape[1]
    xbar = x.mean(1, keepdims=True)
    b = (k - 3) / ((x - xbar) ** 2).sum(1, keepdims=True)
    return xbar + (1 - b) * (x - xbar), b[:, 0]


def stage_baseball(cfg, args):
    names, hits, ab_rest, p = read_batting()
    k, n = len(names), 45
    y = hits / n
    z, c = js_raw(y)
    z, c = z[0], float(c[0])
    tse_y, tse_z = float(((y - p) ** 2).sum()), float(((z - p) ** 2).sum())
    x, theta = arcsine(y), arcsine(p)
    d, bshr = js_grand_mean(x)
    d, bshr = d[0], float(bshr[0])
    tse_x, tse_d = float(((x - theta) ** 2).sum()), float(((d - theta) ** 2).sum())
    back = (np.sin(d / math.sqrt(n)) + 1) / 2
    slope, intercept = np.polyfit(y, p, 1)
    c_oracle = float(((y - y.mean()) * (p - y.mean())).sum() / ((y - y.mean()) ** 2).sum())
    z_oracle = y.mean() + c_oracle * (y - y.mean())
    out = {"k": k, "n": n, "players": names, "y": y.tolist(), "p": p.tolist(), "rest_at_bats": ab_rest.tolist(),
           "raw": {"ybar": float(y.mean()), "sigma2": float(y.mean() * (1 - y.mean()) / n),
                   "V": float(((y - y.mean()) ** 2).sum()), "c": c, "z": z.tolist(),
                   "tse_y": tse_y, "tse_z": tse_z, "ratio": tse_y / tse_z,
                   "closer": int((np.abs(z - p) < np.abs(y - p)).sum()),
                   "worse": [names[i] for i in range(k) if abs(z[i] - p[i]) >= abs(y[i] - p[i])],
                   "printed": {"ybar": 0.265, "c": 0.212, "tse_y": 0.077, "tse_z": 0.022, "ratio": 3.5, "closer": 16},
                   "tse_full_season": None},
           "arcsine": {"x": x.tolist(), "theta": theta.tolist(), "xbar": float(x.mean()), "B": bshr,
                       "intercept": float(bshr * x.mean()), "d": d.tolist(), "back": back.tolist(),
                       "tse_x": tse_x, "tse_d": tse_d, "efficiency": tse_x / tse_d,
                       "closer": int((np.abs(d - theta) < np.abs(x - theta)).sum()),
                       "worse": [names[i] for i in range(k) if abs(d[i] - theta[i]) >= abs(x[i] - theta[i])],
                       "spread_theta": float(((theta - theta.mean()) ** 2).sum()),
                       "printed": {"xbar": -3.275, "B": 0.791, "intercept": -2.59, "tse_x": 17.56, "tse_d": 5.01,
                                   "efficiency": 3.50, "closer": 15}},
           "regression": {"slope": float(slope), "intercept": float(intercept), "c_oracle": c_oracle,
                          "tse_oracle": float(((z_oracle - p) ** 2).sum())}}
    full = (hits + p * ab_rest) / (n + ab_rest)
    out["raw"]["tse_full_season"] = [float(((y - full) ** 2).sum()), float(((z - full) ** 2).sum())]
    # 1970 replayed: each player's true average is his rest-of-season average; 45 at-bats drawn again and again
    reps = cfg["baseball"]
    rng = stream(args.seed, "baseball", 0)
    sq_y = np.zeros((BATCHES, k))
    sq_z = np.zeros((BATCHES, k))
    tse = {"y": np.zeros(BATCHES), "z": np.zeros(BATCHES), "zplus": np.zeros(BATCHES), "x": np.zeros(BATCHES),
           "d": np.zeros(BATCHES)}
    wins = negative_c = 0
    ratios = []
    per_batch = reps // BATCHES
    for b in range(BATCHES):
        h = rng.binomial(n, p, size=(per_batch, k))
        ys = h / n
        zs, cs = js_raw(ys)
        ybar = ys.mean(1, keepdims=True)
        zplus = ybar + np.maximum(cs, 0)[:, None] * (ys - ybar)    # positive part: never shrink past the mean
        xs = arcsine(ys)
        ds, _ = js_grand_mean(xs)
        ey, ez = (ys - p) ** 2, (zs - p) ** 2
        sq_y[b], sq_z[b] = ey.sum(0), ez.sum(0)
        ty, tz = ey.sum(1), ez.sum(1)
        tse["y"][b], tse["z"][b] = ty.sum(), tz.sum()
        tse["zplus"][b] = ((zplus - p) ** 2).sum()
        tse["x"][b], tse["d"][b] = ((xs - theta) ** 2).sum(), ((ds - theta) ** 2).sum()
        wins += int((tz < ty).sum())
        negative_c += int((cs < 0).sum())
        ratios.append(ty / tz)
    ratios = np.concatenate(ratios)
    mse_y, mse_z = sq_y.sum(0) / reps, sq_z.sum(0) / reps
    out["replay"] = {"R": reps, "mean_tse_y": float(tse["y"].sum() / reps), "mean_tse_z": float(tse["z"].sum() / reps),
                     "efficiency_raw": ratio_mcse(tse["y"], tse["z"]),
                     "efficiency_positive_part": ratio_mcse(tse["y"], tse["zplus"]),
                     "efficiency_arcsine": ratio_mcse(tse["x"], tse["d"]),
                     "share_js_wins": wins / reps, "share_js_wins_mcse": math.sqrt(wins / reps * (1 - wins / reps) / reps),
                     "share_negative_c": negative_c / reps,
                     "ratio_quantiles": {str(q): float(np.quantile(ratios, q)) for q in (0.05, 0.25, 0.5, 0.75, 0.95)},
                     "share_ratio_ge_observed": float((ratios >= tse_y / tse_z).mean()),
                     "mse_y": mse_y.tolist(), "mse_z": mse_z.tolist(),
                     "players_hurt": [names[i] for i in range(k) if mse_z[i] > mse_y[i]]}
    hist_edges = np.linspace(0, 12, 121)
    out["replay"]["ratio_hist_edges"] = hist_edges.tolist()
    out["replay"]["ratio_hist"] = np.histogram(np.minimum(ratios, 11.999), bins=hist_edges)[0].tolist()

    raw, arc, reg, rep = out["raw"], out["arcsine"], out["regression"], out["replay"]
    print(f"baseball: Efron and Morris's {k} batters, 1970; the first {n} at-bats predict the rest of the season")
    print(f"  raw scale (1977): grand average {raw['ybar']:.4f}, sigma^2 {raw['sigma2']:.6f}, shrinking factor c = "
          f"{raw['c']:.4f} (printed {raw['printed']['ybar']} and {raw['printed']['c']})")
    print(f"    Clemente {y[0]:.3f} -> {z[0]:.4f}; Munson {y[16]:.3f} -> {z[16]:.4f}")
    print(f"    total squared error: averages {tse_y:.4f}, James-Stein {tse_z:.4f}, ratio {tse_y / tse_z:.3f} "
          f"(printed 0.077, 0.022 and 3.5); James-Stein closer for {raw['closer']} of {k}, not for {', '.join(raw['worse'])}")
    print(f"    against full-season averages instead: {raw['tse_full_season'][0]:.4f} and {raw['tse_full_season'][1]:.4f}")
    print(f"  arcsine scale (1975): mean of the transformed averages {arc['xbar']:.4f} (printed {arc['printed']['xbar']}), "
          f"(k - 3)/V = {arc['B']:.4f} (printed {arc['printed']['B']}), intercept {arc['intercept']:.3f} (printed {arc['printed']['intercept']})")
    print(f"    total squared error: averages {tse_x:.3f}, Stein {tse_d:.3f}, efficiency {tse_x / tse_d:.3f} "
          f"(printed 17.56, 5.01 and 3.50); closer for {arc['closer']} of {k}, not for {', '.join(arc['worse'])}")
    print("    back-transformed: " + ", ".join(f"{b:.3f}" for b in back))
    print(f"  regression of rest-of-season on first-45 averages across the 18: slope {reg['slope']:.4f}, "
          f"intercept {reg['intercept']:.4f}; the best constant c with hindsight {reg['c_oracle']:.4f} gives "
          f"total squared error {reg['tse_oracle']:.4f}")
    e = rep["efficiency_raw"]
    print(f"  1970 replayed, R = {reps:,} seasons of {n} at-bats per player from the rest-of-season averages:")
    print(f"    mean total squared error: averages {rep['mean_tse_y']:.4f}, James-Stein {rep['mean_tse_z']:.4f}; "
          f"efficiency {e['ratio']:.3f} +- {e['mcse']:.3f} (positive part {rep['efficiency_positive_part']['ratio']:.3f} +- "
          f"{rep['efficiency_positive_part']['mcse']:.3f}; arcsine scale {rep['efficiency_arcsine']['ratio']:.3f} +- "
          f"{rep['efficiency_arcsine']['mcse']:.3f})")
    print(f"    James-Stein has the smaller total in {100 * rep['share_js_wins']:.2f}% +- {100 * rep['share_js_wins_mcse']:.2f} "
          f"of seasons; c < 0 in {100 * rep['share_negative_c']:.2f}%; the ratio of totals has median "
          f"{rep['ratio_quantiles']['0.5']:.2f} (5% to 95%: {rep['ratio_quantiles']['0.05']:.2f} to "
          f"{rep['ratio_quantiles']['0.95']:.2f}); {100 * rep['share_ratio_ge_observed']:.1f}% of seasons reach the observed "
          f"{tse_y / tse_z:.2f}")
    print("    players whose own MSE James-Stein raises: " + (", ".join(
        f"{nm} ({mse_z[names.index(nm)] / mse_y[names.index(nm)]:.2f} x)" for nm in rep["players_hurt"]) or "none"))
    return out


def stein_risk_exact(k, spread):
    """Exact total risk of the grand-mean James-Stein rule for k unit-variance normal means (James and Stein
    1961, applied in the k - 1 dimensions orthogonal to the grand mean): 1 + (k - 1) - (k - 3)^2 E[1/(k - 3 + 2K)],
    K ~ Poisson(spread / 2), spread = sum (theta - theta bar)^2."""
    lam = spread / 2
    top = int(lam + 40 * math.sqrt(lam + 1) + 60)
    kk = np.arange(top + 1)
    return float(k - (k - 3) ** 2 * (stats.poisson.pmf(kk, lam) / (k - 3 + 2 * kk)).sum())


def stage_stein(cfg, args):
    k, reps = 18, cfg["stein"]
    _, _, _, p = read_batting()
    theta_bb = arcsine(p)
    spread_bb = float(((theta_bb - theta_bb.mean()) ** 2).sum())
    pattern = np.linspace(-1, 1, k)
    pattern /= math.sqrt((pattern ** 2).sum())           # unit spread; any pattern with the same spread has the same risk
    spreads = [0.0, 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256, round(spread_bb, 4)]
    out = {"k": k, "R": reps, "spread_baseball": spread_bb, "points": []}
    print(f"stein: k = {k} normal means with unit variance; total squared error of the separate observations (risk {k}) "
          f"against James-Stein toward the grand mean; R = {reps:,} per point")
    for i, sp in enumerate(spreads):
        rng = stream(args.seed, "stein", i)
        theta = math.sqrt(sp) * pattern
        acc = np.zeros((BATCHES, 3))
        per_batch = reps // BATCHES
        for b in range(BATCHES):
            x = theta + rng.standard_normal((per_batch, k))
            d, bb = js_grand_mean(x)
            dplus = x.mean(1, keepdims=True) + np.maximum(0, 1 - bb)[:, None] * (x - x.mean(1, keepdims=True))
            acc[b] = (((x - theta) ** 2).sum(), ((d - theta) ** 2).sum(), ((dplus - theta) ** 2).sum())
        per = acc / per_batch
        row = {"spread": sp, "exact": stein_risk_exact(k, sp),
               "x": float(per[:, 0].mean()), "x_mcse": float(per[:, 0].std(ddof=1) / math.sqrt(BATCHES)),
               "js": float(per[:, 1].mean()), "js_mcse": float(per[:, 1].std(ddof=1) / math.sqrt(BATCHES)),
               "js_plus": float(per[:, 2].mean()), "js_plus_mcse": float(per[:, 2].std(ddof=1) / math.sqrt(BATCHES))}
        row["efficiency_exact"] = k / row["exact"]
        out["points"].append(row)
        tag = "  <- the 18 batters' true spread (arcsine scale)" if i == len(spreads) - 1 else ""
        print(f"  spread {sp:8.3f}: separate {fmt(row['x'], row['x_mcse'], 3)}, James-Stein {fmt(row['js'], row['js_mcse'], 3)} "
              f"(exact {row['exact']:.3f}), positive part {fmt(row['js_plus'], row['js_plus_mcse'], 3)}; "
              f"efficiency {row['efficiency_exact']:.2f}{tag}")
    curve = np.unique(np.concatenate([[0.0], np.geomspace(0.05, 1000, 160), [spread_bb]]))
    out["curve_spread"] = curve.tolist()
    out["curve_exact"] = [stein_risk_exact(k, s) for s in curve]
    return out


# ------------------------------------------------------------------------------- run
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
            "estimators_py_sha1": hashlib.sha1(source).hexdigest()[:12],
            "batting_csv_sha1": hashlib.sha1(BATTING_CSV.read_bytes()).hexdigest()[:12],
            "tanks_csv_sha1": hashlib.sha1(TANKS_CSV.read_bytes()).hexdigest()[:12],
            "budget": budget, "seed": args.seed, "replications": QUICK if args.quick else FULL,
            "flags": {"N": args.N, "k": args.k, "n": args.n, "fault": args.fault}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261028)
    parser.add_argument("--N", type=int, default=342, help="tanks: how many tanks exist (default 342)")
    parser.add_argument("--k", type=int, default=5, help="tanks: how many are captured (default 5)")
    parser.add_argument("--n", type=int, default=10, help="divisors: sample size (default 10)")
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the capture helper")
    args = parser.parse_args()
    if not 1 <= args.k <= args.N or args.n < 2:
        parser.error("need 1 <= k <= N and n >= 2")
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, "
          f"NumPy {prov['numpy']}, SciPy {prov['scipy']}; estimators.py {prov['estimators_py_sha1']}; "
          f"budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    funcs = {"tanks": stage_tanks, "consistency": stage_consistency, "divisors": stage_divisors,
             "baseball": stage_baseball, "stein": stage_stein}
    for name in STAGES if args.stage == "all" else (args.stage,):
        t0 = time.perf_counter()
        print()
        captures[name] = funcs[name](cfg, args)
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items()))


if __name__ == "__main__":
    main()
