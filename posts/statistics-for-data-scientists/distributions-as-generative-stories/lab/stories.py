#!/usr/bin/env python3
"""Lab for "Distributions as Generative Stories: Let the Process Pick".

Every number the article calls measured comes from a run of this file. Each stage prints its
numbers and writes them under its own key in the capture file.

    python stories.py all --out mine.json     # every stage, the article's budget (about a minute)
    python stories.py all --quick             # fewer Monte Carlo replications, noisier
    python stories.py accidents               # one stage

Stages:
    worked     Clarke's flying bombs and Bortkiewicz's horse kicks against the binomial and Poisson
    waiting    gaps and waits in a Poisson process, and the coal-mining record
    sums       the same twelve small effects, added and multiplied
    accidents  Greenwood and Yule's accidents: Poisson, the gamma mixture, the negative binomial,
               and a contagion process that produces the same counts
    tails      a unit-variance Student t with 5 degrees of freedom against the normal
    loglog     a lognormal on log-log axes, and Champernowne's floor

Every pmf the article uses is computed twice, once by recurrence below and once by SciPy, and the
largest disagreement is recorded. Every simulated share or mean is reported with its Monte Carlo
standard error (MCSE) and the number of replications R behind it.
"""

import argparse
import datetime
import hashlib
import json
import math
import pathlib
import platform
import sys
import time

import numpy as np
import scipy
from scipy import stats

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
STAGES = ("worked", "waiting", "sums", "accidents", "tails", "loglog")

# R for each simulation. The article quotes FULL; --quick is for a fast first run.
FULL = dict(proc=100_000, coal=10_000, sums=200_000, factories=20_000, contagion=10_000,
            tails=20_000, loglog=1_000, champ=200_000)
QUICK = dict(proc=20_000, coal=2_000, sums=50_000, factories=2_000, contagion=1_000,
             tails=2_000, loglog=200, champ=5_000)


# ------------------------------------------------------------------------------- small helpers
def read_csv(name):
    """Rows of a data file as dicts; lines starting with # are its provenance header."""
    lines = [ln for ln in (DATA / name).read_text(encoding="utf-8").splitlines()
             if ln and not ln.startswith("#")]
    head = lines[0].split(",")
    return [dict(zip(head, ln.split(","))) for ln in lines[1:]]


def moments(values, counts):
    """Mean and variance (divisor n - 1) of a frequency table."""
    v = np.asarray(values, float)
    c = np.asarray(counts, float)
    n = c.sum()
    mean = (v * c).sum() / n
    return mean, (c * (v - mean) ** 2).sum() / (n - 1)


def mcse_share(share, reps):
    return math.sqrt(share * (1 - share) / reps)


def mcse_mean(x):
    x = np.asarray(x, float)
    return float(x.std(ddof=1) / math.sqrt(len(x)))


def chisq(obs, exp):
    obs = np.asarray(obs, float)
    exp = np.asarray(exp, float)
    return float(((obs - exp) ** 2 / exp).sum())


def hanging(obs, exp):
    """Hanging rootogram: each bar of sqrt(observed) hangs from sqrt(expected)."""
    top = np.sqrt(np.asarray(exp, float))
    return {"sqrt_expected": top.tolist(),
            "sqrt_observed": np.sqrt(np.asarray(obs, float)).tolist(),
            "bar_bottom": (top - np.sqrt(np.asarray(obs, float))).tolist()}


def r6(x):
    """Six significant digits, for long arrays that only feed figures."""
    return [float(f"{v:.6g}") for v in np.asarray(x, float)]


def classes(pmf, last):
    """Probabilities of 0, 1, ..., last - 1 and of last-or-more."""
    head = np.asarray(pmf[:last], float)
    return np.append(head, max(0.0, 1.0 - head.sum()))


def skew(x):
    x = np.asarray(x, float)
    d = x - x.mean()
    return float((d ** 3).mean() / (d ** 2).mean() ** 1.5)


def excess_kurtosis(x):
    x = np.asarray(x, float)
    d = x - x.mean()
    return float((d ** 4).mean() / (d ** 2).mean() ** 2 - 3.0)


# ------------------------------------------------------------- pmfs by recurrence, no library
def poisson_pmf(lam, kmax):
    p = np.empty(kmax + 1)
    p[0] = math.exp(-lam)
    for k in range(kmax):
        p[k + 1] = p[k] * lam / (k + 1)
    return p


def binom_pmf(n, prob, kmax):
    p = np.zeros(kmax + 1)
    p[0] = (1 - prob) ** n
    ratio = prob / (1 - prob)
    for k in range(min(kmax, n)):
        p[k + 1] = p[k] * (n - k) / (k + 1) * ratio
    return p


def nbinom_pmf(mu, k, jmax):
    """Negative binomial with mean mu and dispersion k, so that Var = mu + mu^2/k."""
    p = np.empty(jmax + 1)
    q = mu / (k + mu)
    p[0] = (k / (k + mu)) ** k
    for j in range(jmax):
        p[j + 1] = p[j] * (j + k) / (j + 1) * q
    return p


def scipy_nbinom_args(mu, k, fault=False):
    """SciPy's nbinom(n, p) counts failures before n successes: n = k and p = k/(k + mu).

    The --fault draft below is the E4 exercise; it is an easy slip to make.
    """
    if fault:
        return k, mu / (k + mu)
    return k, k / (k + mu)


def t5_sf(t):
    """P(T > t) for Student's t with 5 degrees of freedom, closed form (odd df), no library."""
    theta = math.atan(t / math.sqrt(5.0))
    c = math.cos(theta)
    return 0.5 - (theta + math.sin(theta) * c * (1 + 2.0 / 3.0 * c * c)) / math.pi


def normal_two_sided(x):
    return math.erfc(x / math.sqrt(2.0))


# ---------------------------------------------------------------------------------- stage: worked
def stage_worked(cfg, rng, args):
    out = {}
    rows = read_csv("clarke1946_flying_bombs.csv")
    hits = np.array([int(r["hits"]) for r in rows])
    squares = np.array([int(r["squares"]) for r in rows])
    n_sq, bombs = int(squares.sum()), int((hits * squares).sum())
    lam = bombs / n_sq
    mean, var = moments(hits, squares)
    obs = [int(squares[hits == k].sum()) for k in range(5)] + [int(squares[hits >= 5].sum())]

    pois = classes(poisson_pmf(lam, 60), 5)
    pois_sp = np.append(stats.poisson.pmf(np.arange(5), lam), stats.poisson.sf(4, lam))
    binom_full = binom_pmf(bombs, 1 / n_sq, bombs)
    binom = classes(binom_full, 5)
    binom_sp = np.append(stats.binom.pmf(np.arange(5), bombs, 1 / n_sq),
                         stats.binom.sf(4, bombs, 1 / n_sq))
    exp_pois, exp_binom = n_sq * pois, n_sq * binom
    chi = chisq(obs, exp_pois)
    pois_full = poisson_pmf(lam, bombs)
    tv = 0.5 * (np.abs(binom_full - pois_full).sum() + max(0.0, 1 - pois_full.sum()))
    lecam = bombs * (1 / n_sq) ** 2

    # How rare is rare? Distance from Bin(n, lam/n) to Poisson(lam) as n grows, against Le Cam.
    curve = []
    for n in sorted(set(int(round(v)) for v in np.logspace(0, 4, 41))):
        b = binom_pmf(n, lam / n, n)
        p = poisson_pmf(lam, n)
        curve.append({"n": n, "tv": float(0.5 * (np.abs(b - p).sum() + max(0.0, 1 - p.sum()))),
                      "lecam_bound": lam * lam / n})
    out["clarke"] = {
        "squares": n_sq, "bombs": bombs, "lambda": lam, "mean": mean, "variance": var,
        "dispersion_index": var / mean, "observed": obs,
        "expected_poisson": exp_pois.tolist(), "expected_binomial": exp_binom.tolist(),
        "max_diff_pmf_vs_scipy": float(max(np.abs(pois - pois_sp).max(), np.abs(binom - binom_sp).max())),
        "chi2": chi, "chi2_df": 4, "chi2_p": float(stats.chi2.sf(chi, 4)),
        "binomial_minus_poisson_squares_max": float(np.abs(exp_binom - exp_pois).max()),
        "binomial_minus_poisson_squares_total": float(n_sq * 2 * tv),
        "total_variation": float(tv), "lecam_sum_p2": lecam,
        "rootogram": hanging(obs, exp_pois), "rare_limit_curve": curve,
    }
    c = out["clarke"]
    print(f"Clarke: {n_sq} squares, {bombs} bombs, lambda = {lam:.6f}; mean {mean:.4f}, "
          f"variance {var:.4f} (n - 1), ratio {var / mean:.4f}")
    print("  hits      " + "  ".join(f"{k:>7}" for k in ("0", "1", "2", "3", "4", "5+")))
    print("  observed  " + "  ".join(f"{v:>7d}" for v in obs))
    print("  binomial  " + "  ".join(f"{v:7.3f}" for v in exp_binom))
    print("  Poisson   " + "  ".join(f"{v:7.3f}" for v in exp_pois))
    print(f"  chi-square {chi:.4f} on 4 df, P = {c['chi2_p']:.4f}; recurrence vs SciPy max diff "
          f"{c['max_diff_pmf_vs_scipy']:.1e}")
    print(f"  binomial vs Poisson: total variation {tv:.3e} (Le Cam bound {lecam:.3e}); "
          f"{c['binomial_minus_poisson_squares_total']:.3f} squares in all, at most "
          f"{c['binomial_minus_poisson_squares_max']:.3f} in one class")

    rows = read_csv("bortkiewicz1898_horse_kicks.csv")
    for label, keep in (("bortkiewicz_200", lambda r: r["in_200"] == "yes"),
                        ("bortkiewicz_280", lambda r: True)):
        deaths = np.array([int(r["deaths"]) for r in rows if keep(r)])
        freq = [int((deaths == k).sum()) for k in range(5)] + [int((deaths >= 5).sum())]
        m, v = deaths.mean(), deaths.var(ddof=1)
        exp = len(deaths) * classes(poisson_pmf(m, 40), 5)
        out[label] = {"corps_years": int(len(deaths)), "deaths": int(deaths.sum()), "observed": freq,
                      "mean": float(m), "variance": float(v), "dispersion_index": float(v / m),
                      "expected_poisson": exp.tolist(), "rootogram": hanging(freq, exp)}
        print(f"Bortkiewicz {len(deaths)} corps-years: deaths {deaths.sum()}, observed {freq}, "
              f"mean {m:.4f}, variance {v:.4f}, ratio {v / m:.4f}; Poisson "
              + " ".join(f"{e:.2f}" for e in exp))
    totals = {}
    for r in rows:
        totals[r["corps"]] = totals.get(r["corps"], 0) + int(r["deaths"])
    out["bortkiewicz_corps_totals"] = totals
    return out


# --------------------------------------------------------------------------------- stage: waiting
def stage_waiting(cfg, rng, args):
    out = {}
    # A Poisson process at rate 3 per unit time, built only from exponential gaps.
    rate, reps = 3.0, cfg["proc"]
    gaps = rng.exponential(1 / rate, size=(reps, 40))
    arrivals = gaps.cumsum(axis=1)
    counts = (arrivals <= 1.0).sum(axis=1)
    freq = np.bincount(counts, minlength=15)[:15] / reps
    pois = poisson_pmf(rate, 14)
    third = arrivals[:, 2]
    out["process"] = {
        "rate": rate, "R": reps,
        "count_share": freq.tolist(), "poisson_pmf": pois.tolist(),
        "count_tv_vs_poisson": float(0.5 * np.abs(freq - pois).sum()),
        "count_mean": float(counts.mean()), "count_mean_mcse": mcse_mean(counts),
        "count_variance": float(counts.var(ddof=1)),
        "gap_cv": float(gaps[:, 0].std(ddof=1) / gaps[:, 0].mean()),
        "third_arrival_mean": float(third.mean()), "third_arrival_mean_mcse": mcse_mean(third),
        "third_arrival_variance": float(third.var(ddof=1)),
        "gamma_mean": 3 / rate, "gamma_variance": 3 / rate ** 2,
    }
    p = out["process"]
    print(f"Poisson process at rate 3, R = {reps}: count in [0, 1] mean {p['count_mean']:.4f} "
          f"± {p['count_mean_mcse']:.4f}, variance {p['count_variance']:.4f}; total variation from "
          f"Poisson(3) {p['count_tv_vs_poisson']:.4f}; gap CV {p['gap_cv']:.4f}; third arrival mean "
          f"{p['third_arrival_mean']:.4f} ± {p['third_arrival_mean_mcse']:.4f} (gamma: 1), variance "
          f"{p['third_arrival_variance']:.4f} (gamma: {1 / 3:.4f})")

    dates = np.array([float(r["date"]) for r in read_csv("coal_disasters_1851_1962.csv")])
    days = np.diff(dates) * 365.25
    early = dates[1:] < 1890.0          # both explosions before 1 January 1890
    groups = {"pooled": days, "1851_1889": days[early], "1890_1962": days[~early]}
    sim_reps = cfg["coal"]
    out["coal"] = {"explosions": int(len(dates)), "first": float(dates[0]), "last": float(dates[-1]),
                   "explosions_before_1890": int((dates < 1890.0).sum()),
                   "explosions_from_1890": int((dates >= 1890.0).sum()), "R": sim_reps}
    grid = np.linspace(0, 2000, 101)
    for name, g in groups.items():
        cv = float(g.std(ddof=1) / g.mean())
        sims = rng.exponential(1.0, size=(sim_reps, len(g)))
        sim_cv = sims.std(axis=1, ddof=1) / sims.mean(axis=1)
        share = float((sim_cv >= cv).mean())
        out["coal"][name] = {
            "gaps": int(len(g)), "mean_days": float(g.mean()), "sd_days": float(g.std(ddof=1)),
            "cv": cv, "sim_cv_share_at_least": share, "sim_cv_share_mcse": mcse_share(share, sim_reps),
            "sim_cv_max": float(sim_cv.max()), "sim_cv_q999": float(np.quantile(sim_cv, 0.999)),
            "share_longer_than_3_means": float((g > 3 * g.mean()).mean()),
            "survival_days": grid.tolist(),
            "survival_observed": [float((g > t).mean()) for t in grid],
            "survival_exponential": r6(np.exp(-grid / g.mean())),
        }
        c = out["coal"][name]
        print(f"Coal gaps {name}: {len(g)} gaps, mean {g.mean():.1f} days, CV {cv:.3f}; exponential "
              f"records of the same length reach CV >= {cv:.3f} in {share:.4f} ± "
              f"{c['sim_cv_share_mcse']:.4f} of R = {sim_reps} (largest {c['sim_cv_max']:.3f})")
    out["coal"]["dates"] = dates.tolist()
    return out


# ------------------------------------------------------------------------------------ stage: sums
def stage_sums(cfg, rng, args):
    n = cfg["sums"]
    f = rng.uniform(0.5, 1.5, size=(n, 12))      # twelve small effects, each 0.5 to 1.5
    if args.dominant:
        f[:, 0] = rng.uniform(0.5, 12.5, size=n)  # E3 variant: one effect twelve times wider
    s, prod = f.sum(axis=1), f.prod(axis=1)
    logp = np.log(prod)
    out = {"R": n, "factors": 12, "dominant": bool(args.dominant)}
    for name, x in (("sum", s), ("product", prod), ("log_product", logp)):
        out[name] = {"mean": float(x.mean()), "sd": float(x.std(ddof=1)), "skewness": skew(x),
                     "skewness_scipy": float(stats.skew(x)), "excess_kurtosis": excess_kurtosis(x),
                     "excess_kurtosis_scipy": float(stats.kurtosis(x)), "median": float(np.median(x)),
                     "share_below_mean": float((x < x.mean()).mean())}
    edges = {"sum": np.linspace(8, 16, 61), "product": np.linspace(0, 4, 61),
             "log_product": np.linspace(-4, 3, 61)}
    for name, x in (("sum", s), ("product", prod), ("log_product", logp)):
        h, e = np.histogram(x, bins=edges[name], density=True)
        out[name]["hist_edges"] = r6(e)
        out[name]["hist_density"] = r6(h)
        out[name]["share_outside_hist"] = float(((x < e[0]) | (x > e[-1])).mean())
    print(f"Sums and products of 12 effects from U(0.5, 1.5), R = {n}"
          + (" (one effect twelve times wider)" if args.dominant else "") + ":")
    for name in ("sum", "product", "log_product"):
        o = out[name]
        print(f"  {name:<11} mean {o['mean']:.4f}, sd {o['sd']:.4f}, median {o['median']:.4f}, "
              f"skewness {o['skewness']:.4f}, excess kurtosis {o['excess_kurtosis']:.4f}, "
              f"share below mean {o['share_below_mean']:.4f}")
    return out


# ------------------------------------------------------------------------------- stage: accidents
def stage_accidents(cfg, rng, args):
    out = {}
    rows = read_csv("greenwood_yule1920_accidents.csv")
    x = np.array([int(r["accidents"]) for r in rows])
    f = np.array([int(r["women"]) for r in rows])
    n = int(f.sum())
    mu, s2 = moments(x, f)
    obs = [int(f[x == j].sum()) for j in range(5)] + [int(f[x >= 5].sum())]

    pois = classes(poisson_pmf(mu, 40), 5)
    exp_pois = n * pois
    k = mu * mu / (s2 - mu)                     # method of moments: s2 = mu + mu^2/k
    nb = classes(nbinom_pmf(mu, k, 60), 5)
    n_sp, p_sp = scipy_nbinom_args(mu, k, fault=args.fault)
    nb_sp = np.append(stats.nbinom.pmf(np.arange(5), n_sp, p_sp), stats.nbinom.sf(4, n_sp, p_sp))
    fitted = stats.nbinom(n_sp, p_sp)
    exp_nb = n * nb_sp                          # the expected counts the article draws use SciPy
    out["data"] = {"women": n, "accidents": int((x * f).sum()), "observed": obs, "mean": mu,
                   "variance": s2, "dispersion_index": s2 / mu}
    out["poisson"] = {"expected": exp_pois.tolist(), "chi2": chisq(obs, exp_pois), "chi2_df": 4,
                      "rootogram": hanging(obs, exp_pois)}
    out["negative_binomial"] = {
        "k": k, "alpha_statsmodels": 1 / k, "size_R": k, "theta_MASS": k,
        "scipy_n": n_sp, "scipy_p": p_sp, "R_prob": k / (k + mu), "fault": bool(args.fault),
        "fitted_mean": float(fitted.mean()), "fitted_variance": float(fitted.var()),
        "expected": exp_nb.tolist(), "chi2": chisq(obs, exp_nb), "chi2_df": 3,
        "recurrence_vs_scipy_max_diff": float(np.abs(nb - nb_sp).max()),
        "rootogram": hanging(obs, exp_nb),
    }
    print(f"Greenwood and Yule: {n} women, {out['data']['accidents']} accidents; mean {mu:.4f}, "
          f"variance {s2:.4f} (n - 1), ratio {s2 / mu:.4f}")
    print("  accidents   " + "  ".join(f"{j:>7}" for j in ("0", "1", "2", "3", "4", "5+")))
    print("  observed    " + "  ".join(f"{v:>7d}" for v in obs))
    print("  Poisson     " + "  ".join(f"{v:7.2f}" for v in exp_pois)
          + f"   chi-square {out['poisson']['chi2']:.2f}")
    print("  neg. binom. " + "  ".join(f"{v:7.2f}" for v in exp_nb)
          + f"   chi-square {out['negative_binomial']['chi2']:.2f}")
    print(f"  moment fit k = {k:.4f} (statsmodels alpha = {1 / k:.4f}, R size = MASS theta = {k:.4f}); "
          f"SciPy nbinom(n = {n_sp:.4f}, p = {p_sp:.4f}) has mean {fitted.mean():.4f} and variance "
          f"{fitted.var():.4f}; recurrence vs SciPy max diff "
          f"{out['negative_binomial']['recurrence_vs_scipy_max_diff']:.1e}")
    if args.fault:
        print("  (--fault is on: one helper in this stage is an earlier draft)")

    # What the fitted gamma says about the women's rates.
    g = stats.gamma(a=k, scale=mu / k)
    shares, cuts = {}, {}
    for top in (0.1, 0.2, 0.5):
        cut = g.ppf(1 - top)
        cuts[f"top_{int(top * 100)}"] = float(cut)
        shares[f"top_{int(top * 100)}"] = float(stats.gamma(a=k + 1, scale=mu / k).sf(cut))
    rate_grid = np.linspace(0.002, 2.5, 250)
    out["gamma"] = {"shape": k, "scale": mu / k, "median": float(g.median()),
                    "share_below_mean": float(g.cdf(mu)), "accident_share": shares, "rate_cut": cuts,
                    "poisson_part": mu, "heterogeneity_part": mu * mu / k,
                    "density_x": r6(rate_grid), "density": r6(g.pdf(rate_grid))}
    print(f"  fitted gamma of rates: median {g.median():.4f}, {g.cdf(mu):.1%} of women below the mean; "
          f"top 10% carry {shares['top_10']:.1%}, top 20% {shares['top_20']:.1%}, top half "
          f"{shares['top_50']:.1%} of expected accidents; variance = {mu:.4f} + {mu * mu / k:.4f}")

    # The proneness story, simulated: each woman's rate from the gamma, her count from a Poisson.
    reps, chunk = cfg["factories"], 1000
    var_s, zero_s, within_s, between_s, p2_s, r12_s = [], [], [], [], [], []
    for start in range(0, reps, chunk):
        m = min(chunk, reps - start)
        lam = rng.gamma(k, mu / k, size=(m, n))
        y1 = rng.poisson(lam)
        y2 = rng.poisson(lam)                  # a second five weeks, same women, same rates
        var_s.append(y1.var(axis=1, ddof=1))
        zero_s.append((y1 == 0).mean(axis=1))
        within_s.append(lam.mean(axis=1))
        between_s.append(lam.var(axis=1, ddof=1))
        p2_s.append(y2.mean(axis=1))
        r12_s.append(_rowcorr(y1, y2))
    var_s, zero_s = np.concatenate(var_s), np.concatenate(zero_s)
    within_s, between_s = np.concatenate(within_s), np.concatenate(between_s)
    p2_s, r12_s = np.concatenate(p2_s), np.concatenate(r12_s)
    nb_p0 = float(nbinom_pmf(mu, k, 0)[0])
    out["proneness_simulation"] = {
        "R": reps, "women": n,
        "sample_variance": float(var_s.mean()), "sample_variance_mcse": mcse_mean(var_s),
        "theory_variance": mu + mu * mu / k,
        "zero_share": float(zero_s.mean()), "zero_share_mcse": mcse_mean(zero_s), "nb_p0": nb_p0,
        "within_part": float(within_s.mean()), "within_part_mcse": mcse_mean(within_s),
        "between_part": float(between_s.mean()), "between_part_mcse": mcse_mean(between_s),
        "period2_mean": float(p2_s.mean()), "period2_mean_mcse": mcse_mean(p2_s),
        "period_correlation": float(np.nanmean(r12_s)), "period_correlation_mcse": mcse_mean(r12_s[~np.isnan(r12_s)]),
    }
    s = out["proneness_simulation"]
    print(f"  proneness simulated, R = {reps} factories of {n}: sample variance {s['sample_variance']:.4f} "
          f"± {s['sample_variance_mcse']:.4f} (theory {s['theory_variance']:.4f}); zero share "
          f"{s['zero_share']:.4f} ± {s['zero_share_mcse']:.4f} (NB {nb_p0:.4f}); within part "
          f"{s['within_part']:.4f} ± {s['within_part_mcse']:.4f}, between part {s['between_part']:.4f} "
          f"± {s['between_part_mcse']:.4f}; second five weeks mean {s['period2_mean']:.4f} "
          f"± {s['period2_mean_mcse']:.4f}")

    # The contagion story: everyone starts alike and each accident raises the rate (Polya process).
    b = math.log(1 + mu / k)                   # chosen so period-1 counts are NB(mu, k) exactly
    a = k * b
    reps_c, chunk = cfg["contagion"], 500
    freq_c, var_c, p2_c, r12_c, capped = np.zeros(6), [], [], [], 0
    for start in range(0, reps_c, chunk):
        m = min(chunk, reps_c - start)
        t = np.zeros((m, n))
        count = np.zeros((m, n), dtype=np.int64)
        c1 = np.zeros((m, n), dtype=np.int64)
        alive = np.ones((m, n), dtype=bool)
        for _ in range(60):
            if not alive.any():
                break
            t = t + rng.exponential(1.0, size=(m, n)) / (a + b * count)
            alive &= t <= 2.0
            c1 += (alive & (t <= 1.0))
            count += alive
        capped += int(alive.sum())
        c2 = count - c1
        for j in range(5):
            freq_c[j] += (c1 == j).sum()
        freq_c[5] += (c1 >= 5).sum()
        var_c.append(c1.var(axis=1, ddof=1))
        p2_c.append(c2.mean(axis=1))
        r12_c.append(_rowcorr(c1, c2))
    var_c, p2_c, r12_c = np.concatenate(var_c), np.concatenate(p2_c), np.concatenate(r12_c)
    out["contagion_simulation"] = {
        "R": reps_c, "women": n, "start_rate": a, "rate_step": b, "runs_hitting_event_cap": capped,
        "expected_counts": (n * freq_c / (reps_c * n)).tolist(),
        "sample_variance": float(var_c.mean()), "sample_variance_mcse": mcse_mean(var_c),
        "period2_mean": float(p2_c.mean()), "period2_mean_mcse": mcse_mean(p2_c),
        "period2_theory": k * math.exp(b) * (math.exp(b) - 1),
        "period_correlation": float(np.nanmean(r12_c)), "period_correlation_mcse": mcse_mean(r12_c[~np.isnan(r12_c)]),
    }
    s = out["contagion_simulation"]
    print(f"  contagion simulated, R = {reps_c}: start rate {a:.4f}, each accident adds {b:.4f}; period-1 "
          "counts " + " ".join(f"{v:.2f}" for v in s["expected_counts"])
          + f"; variance {s['sample_variance']:.4f} ± {s['sample_variance_mcse']:.4f}; second five weeks "
          f"mean {s['period2_mean']:.4f} ± {s['period2_mean_mcse']:.4f} (theory {s['period2_theory']:.4f})")
    return out


def _rowcorr(u, v):
    u = u - u.mean(axis=1, keepdims=True)
    v = v - v.mean(axis=1, keepdims=True)
    den = np.sqrt((u * u).sum(axis=1) * (v * v).sum(axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (u * v).sum(axis=1) / den


# ----------------------------------------------------------------------------------- stage: tails
def stage_tails(cfg, rng, args):
    nu = args.df
    scale = math.sqrt((nu - 2) / nu)           # Var t_nu = nu/(nu - 2), so this makes variance 1
    xs = [1, 2, 3, 4, 5, 6]
    sf_scipy = {x: float(2 * stats.t.sf(x / scale, nu)) for x in xs}
    diff = None                                 # the closed form below is written for 5 df only
    if nu == 5:
        diff = max(abs(2 * t5_sf(x / scale) - sf_scipy[x]) for x in xs)
    rows = {str(x): {"t": sf_scipy[x], "normal": normal_two_sided(x),
                     "ratio": sf_scipy[x] / normal_two_sided(x)} for x in xs}
    grid = np.linspace(0, 6.5, 131)
    dens_x = np.linspace(-5, 5, 201)
    out = {"df": nu, "scale": scale, "two_sided_tail": rows, "closed_form_vs_scipy_max_diff": diff,
           "peak_t": float(stats.t.pdf(0, nu) / scale), "peak_normal": float(stats.norm.pdf(0)),
           "curve_x": r6(grid), "curve_t": r6(2 * stats.t.sf(grid / scale, nu)),
           "curve_normal": r6(2 * stats.norm.sf(grid)),
           "density_x": r6(dens_x), "density_t": r6(stats.t.pdf(dens_x / scale, nu) / scale),
           "density_normal": r6(stats.norm.pdf(dens_x))}
    print(f"Student t with {nu} df scaled to variance 1 (scale {scale:.6f}) against the normal; "
          + (f"closed form vs SciPy max diff {diff:.1e}" if diff is not None else "no closed form check"))
    for x in xs:
        r = rows[str(x)]
        print(f"  P(|X| > {x}): t {r['t']:.4e}, normal {r['normal']:.4e}, ratio {r['ratio']:.3f}")
    print(f"  density at 0: t {out['peak_t']:.4f}, normal {out['peak_normal']:.4f}")

    # Draw the t as its story: a normal whose variance is itself random (nu / chi-square_nu).
    reps, chunk = cfg["tails"], 1000
    p4 = sf_scipy[4]
    beyond_t, beyond_z, none100_t, none100_z = [], [], [], []
    for start in range(0, reps, chunk):
        m = min(chunk, reps - start)
        z = rng.standard_normal((m, 1000))
        w = rng.chisquare(nu, size=(m, 1000))
        t = z * np.sqrt(nu / w) * scale
        n0 = rng.standard_normal((m, 1000))
        beyond_t.append((np.abs(t) > 4).sum(axis=1))
        beyond_z.append((np.abs(n0) > 4).sum(axis=1))
        none100_t.append((np.abs(t[:, :100]) > 4).sum(axis=1) == 0)
        none100_z.append((np.abs(n0[:, :100]) > 4).sum(axis=1) == 0)
    bt, bz = np.concatenate(beyond_t), np.concatenate(beyond_z)
    nt, nz = np.concatenate(none100_t), np.concatenate(none100_z)
    sim = {"R": reps, "n": 1000}
    for name, arr, p in (("t", bt, p4), ("normal", bz, normal_two_sided(4))):
        any1 = float((arr > 0).mean())
        sim[name] = {"mean_beyond_4": float(arr.mean()), "mean_beyond_4_mcse": mcse_mean(arr),
                     "expected_beyond_4": 1000 * p, "share_with_any": any1,
                     "share_with_any_mcse": mcse_share(any1, reps),
                     "exact_share_with_any": 1 - (1 - p) ** 1000}
    for name, arr, p in (("t", nt, p4), ("normal", nz, normal_two_sided(4))):
        none = float(arr.mean())
        sim[name]["n100_share_none"] = none
        sim[name]["n100_share_none_mcse"] = mcse_share(none, reps)
        sim[name]["n100_exact_none"] = (1 - p) ** 100
    out["simulation"] = sim
    for name in ("t", "normal"):
        s = sim[name]
        print(f"  {name}, R = {reps} samples of 1,000: {s['mean_beyond_4']:.3f} ± {s['mean_beyond_4_mcse']:.3f} "
              f"points beyond 4 (exact {s['expected_beyond_4']:.3f}); {s['share_with_any']:.4f} ± "
              f"{s['share_with_any_mcse']:.4f} of samples have one (exact {s['exact_share_with_any']:.4f}); "
              f"of 100 points, none beyond 4 in {s['n100_share_none']:.4f} ± {s['n100_share_none_mcse']:.4f} "
              f"(exact {s['n100_exact_none']:.4f})")

    # One sample of 1,000 from each, for the Q-Q figure.
    q = np.sort(rng.standard_normal(1000) * np.sqrt(nu / rng.chisquare(nu, 1000)) * scale)
    zq = np.sort(rng.standard_normal(1000))
    theo = stats.norm.ppf((np.arange(1, 1001) - 0.5) / 1000)
    out["qq"] = {"theoretical": r6(theo), "t_sample": r6(q), "normal_sample": r6(zq),
                 "t_beyond_4": int((np.abs(q) > 4).sum()), "normal_beyond_4": int((np.abs(zq) > 4).sum())}
    print(f"  Q-Q sample: t has {out['qq']['t_beyond_4']} points beyond 4, normal "
          f"{out['qq']['normal_beyond_4']}; t extremes {q[0]:.3f}, {q[-1]:.3f}")
    return out


# ---------------------------------------------------------------------------------- stage: loglog
def stage_loglog(cfg, rng, args):
    out = {}
    sigma, n, top = 2.5, 10_000, 0.10

    def ccdf_fit(x):
        y = np.sort(x)[::-1]
        surv = np.arange(1, len(y) + 1) / len(y)
        m = int(len(y) * top)
        lx, ly = np.log10(y[:m]), np.log10(surv[:m])
        slope, intercept = np.polyfit(lx, ly, 1)
        r2 = float(np.corrcoef(lx, ly)[0, 1] ** 2)
        return y, surv, m, float(slope), float(intercept), r2, float(lx.max() - lx.min())

    x = rng.lognormal(0.0, sigma, n)
    y, surv, m, slope, intercept, r2, decades = ccdf_fit(x)
    keep = np.unique(np.concatenate([np.arange(0, 200), np.geomspace(1, n, 400).astype(int) - 1]))
    out["lognormal"] = {"sigma": sigma, "n": n, "top_share": top, "fit_points": m, "slope": slope,
                        "intercept": intercept, "r2": r2, "decades": decades,
                        "threshold": float(y[m - 1]), "mean": float(x.mean()),
                        "ccdf_x": r6(y[keep]), "ccdf_y": r6(surv[keep])}
    print(f"Lognormal(0, {sigma}), n = {n}: top {top:.0%} ({m} points, {decades:.2f} decades) on log-log "
          f"axes: slope {slope:.4f}, R^2 {r2:.4f}")

    reps, r2s = cfg["loglog"], []
    for _ in range(reps):
        r2s.append(ccdf_fit(rng.lognormal(0.0, sigma, n))[5])
    r2s = np.array(r2s)
    share = float((r2s >= 0.98).mean())
    out["lognormal"].update({"R": reps, "r2_median": float(np.median(r2s)), "r2_min": float(r2s.min()),
                             "share_r2_at_least_098": share,
                             "share_r2_at_least_098_mcse": mcse_share(share, reps)})
    print(f"  over R = {reps} samples: median R^2 {np.median(r2s):.4f}, smallest {r2s.min():.4f}; "
          f"R^2 >= 0.98 in {share:.4f} ± {out['lognormal']['share_r2_at_least_098_mcse']:.4f}")

    # A true power law with the same tail size and slope, for comparison.
    alpha = -slope
    xmin = out["lognormal"]["threshold"]
    pareto = xmin * (1 - rng.random(m)) ** (-1 / alpha)
    py = np.sort(pareto)[::-1]
    psurv = np.arange(1, m + 1) / m
    pl, pv = np.polyfit(np.log10(py), np.log10(psurv), 1)
    out["pareto"] = {"alpha_ccdf": alpha, "xmin": xmin, "n": m, "slope": float(pl),
                     "r2": float(np.corrcoef(np.log10(py), np.log10(psurv))[0, 1] ** 2)}
    print(f"  a Pareto sample of {m} with the same slope: fitted slope {pl:.4f}, R^2 {out['pareto']['r2']:.4f}")

    # Champernowne: halve with probability 2/3, double with 1/3. Without a floor, after T steps,
    # log2 X = 2U - T with U ~ Bin(T, 1/3). With a floor at 1, the equilibrium is P(X = 2^(j-1)) = 2^-j.
    steps = 20
    u = np.arange(steps + 1)
    pmf_u = stats.binom.pmf(u, steps, 1 / 3)
    s_vals = 2 * u - steps
    nofloor = [{"log2x": int(s), "ccdf": float(pmf_u[s_vals >= s].sum())} for s in range(0, steps + 1, 2)]
    floor = [{"log2x": j, "ccdf": 2.0 ** -j} for j in range(0, steps + 1)]
    walkers, horizon = cfg["champ"], 400
    cls = np.ones(walkers, dtype=np.int64)       # class 1 is the floor, incomes 1 to 2
    for _ in range(horizon):
        up = rng.random(walkers) < 1 / 3
        cls = np.where(up, cls + 1, np.maximum(cls - 1, 1))
    emp = [float((cls - 1 >= j).mean()) for j in range(0, 11)]
    dev = max(abs(e - 2.0 ** -j) for j, e in enumerate(emp))
    out["champernowne"] = {"steps_without_floor": steps, "no_floor_ccdf": nofloor, "floor_ccdf": floor,
                           "no_floor_mean": 1.0, "no_floor_median_log2": float(s_vals[np.searchsorted(np.cumsum(pmf_u), 0.5)]),
                           "simulated_walkers": walkers, "simulated_steps": horizon,
                           "simulated_floor_ccdf": emp, "simulated_max_abs_dev": float(dev)}
    print(f"  Champernowne: with a floor P(X >= 2^j) = 2^-j; {walkers} walkers after {horizon} steps "
          f"match it to {dev:.4f}. Without a floor, after {steps} steps P(X >= 1) = "
          f"{nofloor[0]['ccdf']:.4f}, P(X >= 2^10) = {nofloor[5]['ccdf']:.2e}, P(X >= 2^20) = "
          f"{nofloor[-1]['ccdf']:.2e} (2^-20 = {2.0 ** -20:.2e})")
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
            "stories_py_sha1": hashlib.sha1(source).hexdigest()[:12], "budget": budget,
            "seed": args.seed, "replications": QUICK if args.quick else FULL}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261024)
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the NB mapping")
    parser.add_argument("--dominant", action="store_true", help="E3 variant of sums: one wide effect")
    parser.add_argument("--df", type=int, default=5, help="degrees of freedom for the tails stage")
    args = parser.parse_args()
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, "
          f"NumPy {prov['numpy']}, SciPy {prov['scipy']}; stories.py {prov['stories_py_sha1']}; "
          f"budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"worked": stage_worked, "waiting": stage_waiting, "sums": stage_sums,
             "accidents": stage_accidents, "tails": stage_tails, "loglog": stage_loglog}
    for i, name in enumerate(stages):
        rng = np.random.default_rng(np.random.SeedSequence([args.seed, STAGES.index(name)]))
        t0 = time.perf_counter()
        print()
        captures[name] = funcs[name](cfg, rng, args)
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
