#!/usr/bin/env python3
"""Lab for "Likelihood: The MLE, Fisher Information, and the Wald, Score and Likelihood-Ratio Tests".

Every number the article calls measured comes from a run of this file. Each stage prints its numbers
and writes them under its own key in the capture file.

    python likelihood.py all --out mine.json            # every stage, the article's budget (about 2 minutes)
    python likelihood.py all --quick --out quick.json   # the reader's budget (about 15 seconds), noisier
    python likelihood.py nb --out mine.json             # one stage

Stages:
    poisson   Clarke's 576 squares of V-1 hits by hand: log-likelihood, score, MLE, observed and expected
              information and the standard error, checked against SciPy and statsmodels; the Wald, score
              and likelihood-ratio statistics for one null value; the same three for one Prussian corps'
              20 years of horse-kick deaths; their exact sizes as the expected count grows; and the Wald
              statistic computed on other scales of the same parameter
    nb        the negative binomial fitted to Greenwood and Yule's 647 women by maximum likelihood:
              Newton's iterations, checks against SciPy and statsmodels, observed and expected information,
              likelihood regions, profile-likelihood and Wald intervals for k, the delta method for the
              dispersion index, and the sampling distribution of the estimate of k
    boundary  Poisson against negative binomial: the observed tests on both data sets, then the
              likelihood-ratio statistic simulated with the null on the boundary (Poisson data) and inside
              the parameter space (negative binomial data, testing the true k)
    tank      the German tank likelihood, which breaks the regularity conditions: its shape at the MLE and
              the exact distribution of the MLE's error
    powerlaw  the lognormal sample from part 1 of this series, regenerated bit for bit: a power law and a
              lognormal fitted to its tail by maximum likelihood and compared with Vuong's normalised
              likelihood ratio at several thresholds, then the comparison's power measured by simulation

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
import warnings

import numpy as np
import scipy
from scipy import optimize, special, stats

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
CLARKE_CSV = DATA / "clarke1946_flying_bombs.csv"
GY_CSV = DATA / "greenwood_yule1920_accidents.csv"
KICKS_CSV = DATA / "bortkiewicz1898_horse_kicks.csv"
STAGES = ("poisson", "nb", "boundary", "tank", "powerlaw")

# Replications. The article quotes FULL; --quick is the reader's first run.
FULL = dict(k_sampling=20_000, boundary=200_000, interior=200_000, powerlaw=1_000)
QUICK = dict(k_sampling=2_000, boundary=20_000, interior=20_000, powerlaw=100)
ROWS = 50_000                           # simulated data sets per block; fixed, so results do not depend on the machine
CHI2_95 = float(stats.chi2.ppf(0.95, 1))   # 3.8415: the 5% point of chi-squared on 1 df
MIX_95 = float(stats.chi2.ppf(0.90, 1))    # 2.7055: the 5% point of the 50:50 mixture of chi2_0 and chi2_1
Z975 = float(stats.norm.ppf(0.975))
REGULAR_EXCLUDED = ("G", "I", "VI", "XI")  # the corps Bortkiewicz left out of his 200 corps-years

# Part 1's lognormal sample: its root seed, its stage index, and the threshold its capture recorded.
PART1_SEED, PART1_STAGE, PART1_THRESHOLD = 20261024, 5, 26.140414260414232


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
    if isinstance(x, np.integer):
        return int(x)
    return x


def read_table(path):
    """A two-column count table (value, frequency) with '#' provenance lines."""
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    rows = list(csv.reader(lines))[1:]
    return np.array([int(r[0]) for r in rows]), np.array([int(r[1]) for r in rows])


def read_kicks():
    lines = [ln for ln in KICKS_CSV.read_text(encoding="utf-8").splitlines() if ln and not ln.startswith("#")]
    by = {}
    for corps, _year, deaths, _in200 in list(csv.reader(lines))[1:]:
        by.setdefault(corps, []).append(int(deaths))
    return by


def sha1(path):
    return hashlib.sha1(path.read_bytes()).hexdigest()[:12]


def class_probs(dist, classes):
    """Probabilities of 0 .. classes - 2 and of (classes - 1 or more), for drawing count tables by multinomial."""
    p = np.append(dist.pmf(np.arange(classes - 1)), dist.sf(classes - 2))
    p = np.maximum(p, 0.0) / p.sum()
    return p


# ------------------------------------------------------------------------- Poisson by hand
def pois_loglik(total, n, lam, log_fact=0.0):
    """Poisson log-likelihood of n counts summing to `total`; log_fact is the sum of log(x!)."""
    return total * np.log(lam) - n * lam - log_fact


def three_statistics(total, n, lam0):
    """Wald (lambda and log-lambda scales), score and likelihood ratio for H0: lambda = lam0.

    All four depend on the data only through the total count, and on n and lam0 only through m = n * lam0.
    """
    m = n * lam0
    if total == 0:
        return dict(wald=math.inf, wald_log=math.inf, score=m, lr=2 * m)
    return dict(wald=(total - m) ** 2 / total,                    # (lam_hat - lam0)^2 x I(lam_hat)
                wald_log=total * math.log(total / m) ** 2,        # same on the log scale, I = n lam_hat
                score=(total - m) ** 2 / m,                       # U(lam0)^2 / I(lam0)
                lr=2 * (total * math.log(total / m) - (total - m)))


def wald_power(total, n, lam0, c):
    """Wald statistic for H0 computed on the scale psi = lambda^c (c = 0 is the log scale)."""
    lam = total / n
    if abs(c) < 1e-12:
        return total * math.log(lam / lam0) ** 2
    info_psi = n * lam ** (1 - 2 * c) / c ** 2                     # I_lambda x (d lambda / d psi)^2 at lam_hat
    return (lam ** c - lam0 ** c) ** 2 * info_psi


def poisson_intervals(total, n):
    """95% intervals for a Poisson rate from inverting each statistic."""
    lam, c = total / n, Z975 ** 2
    se = math.sqrt(lam / n)
    disc = math.sqrt(4 * total * c + c * c)
    f = lambda l: 2 * (total * math.log(total / (n * l)) - (total - n * l)) - c
    return dict(wald=(lam - Z975 * se, lam + Z975 * se),
                wald_log=(lam * math.exp(-Z975 / math.sqrt(total)), lam * math.exp(Z975 / math.sqrt(total))),
                score=((2 * total + c - disc) / (2 * n), (2 * total + c + disc) / (2 * n)),
                lr=(optimize.brentq(f, lam * 1e-6, lam), optimize.brentq(f, lam, lam * 50 + 10 / n)))


def exact_sizes(m):
    """Exact probability that each nominal 5% test rejects a true H0 when the total is Poisson(m)."""
    s = np.arange(0, int(m + 14 * math.sqrt(m) + 40))
    p = stats.poisson.pmf(s, m)
    pos = s > 0
    safe = np.where(pos, s, 1)
    logratio = np.where(pos, np.log(safe / m), 0.0)
    tests = dict(wald=np.where(pos, (s - m) ** 2 / safe, np.inf),
                 wald_log=np.where(pos, s * logratio ** 2, np.inf),
                 score=(s - m) ** 2 / m,
                 lr=2 * (s * logratio - (s - m)))
    rej = {k: v > CHI2_95 for k, v in tests.items()}
    out = {k: float(p[v].sum()) for k, v in rej.items()}
    split = (rej["wald"] != rej["score"]) | (rej["wald"] != rej["lr"]) | (rej["score"] != rej["lr"])
    out["verdicts_differ"] = float(p[split].sum())
    out["mass_covered"] = float(p.sum())
    return out


def stage_poisson(cfg, args):
    import statsmodels.api as sm
    out = {}
    hits, squares = read_table(CLARKE_CSV)
    n, total = int(squares.sum()), int((hits * squares).sum())
    log_fact = float((squares * special.gammaln(hits + 1)).sum())
    lam = total / n
    obs_info, exp_info = total / lam ** 2, n / lam                # -l''(lam_hat), and n / lam at lam_hat
    se = 1 / math.sqrt(exp_info)
    ll_max = float(pois_loglik(total, n, lam, log_fact))
    print(f"V-1 hits (Clarke): n = {n} squares, total = {total} hits")
    print(f"  log-likelihood l(lam) = {total} log(lam) - {n} lam - {log_fact:.4f};  score U(lam) = {total}/lam - {n}")
    print(f"  MLE lam_hat = {total}/{n} = {lam:.6f}; l(lam_hat) = {ll_max:.4f}")
    print(f"  observed information -l''(lam_hat) = {total}/lam_hat^2 = {obs_info:.4f}; "
          f"expected n/lam_hat = {exp_info:.4f}; SE = {se:.6f}")

    # Reference implementations: the same estimate and standard error two other ways.
    sp = optimize.minimize_scalar(lambda l: -pois_loglik(total, n, l, log_fact), bounds=(0.01, 5),
                                  method="bounded", options=dict(xatol=1e-12))
    y = np.repeat(hits, squares).astype(float)
    glm = sm.GLM(y, np.ones((n, 1)), family=sm.families.Poisson()).fit()
    lam_sm, se_sm = math.exp(glm.params[0]), math.exp(glm.params[0]) * glm.bse[0]
    print(f"  scipy.optimize.minimize_scalar: lam_hat = {sp.x:.9f} (|diff| {abs(sp.x - lam):.1e})")
    print(f"  statsmodels GLM Poisson, log link: intercept {glm.params[0]:.6f} (SE {glm.bse[0]:.6f} = 1/sqrt({total})); "
          f"exp gives lam {lam_sm:.6f}, delta-method SE {se_sm:.6f}; llf {glm.llf:.4f}")
    out["v1"] = dict(n=n, total=total, lam_hat=lam, log_fact=log_fact, ll_max=ll_max, obs_info=obs_info,
                     exp_info=exp_info, se=se, scipy_lam=sp.x, sm_intercept=glm.params[0], sm_intercept_se=glm.bse[0],
                     sm_lam=lam_sm, sm_se=se_sm, sm_llf=glm.llf)

    nulls = {}
    for lam0 in (0.85, 1.0):
        st = three_statistics(total, n, lam0)
        st["p"] = {k: float(stats.chi2.sf(v, 1)) for k, v in st.items()}
        st["se_from_null"] = (lam - lam0) / se
        nulls[str(lam0)] = st
        print(f"  H0: lam = {lam0} ({(lam - lam0) / se:+.2f} SE): Wald {st['wald']:.4f} (log scale {st['wald_log']:.4f}), "
              f"score {st['score']:.4f}, LR {st['lr']:.4f}; chi2_1 p {st['p']['wald']:.4f} / {st['p']['score']:.4f} / {st['p']['lr']:.4f}")
    out["v1"]["nulls"] = nulls
    out["v1"]["intervals"] = poisson_intervals(total, n)
    print("  95% intervals: " + "; ".join(f"{k} {a:.4f} to {b:.4f}" for k, (a, b) in out["v1"]["intervals"].items()))

    # Curves for the figures: the log-likelihood around its peak, its quadratic, the score and its tangent.
    grid = np.linspace(lam - 3.6 * se, lam + 3.6 * se, 145)
    out["v1"]["curve"] = dict(lam=grid, ll=pois_loglik(total, n, grid, log_fact) - ll_max,
                              quad=-0.5 * obs_info * (grid - lam) ** 2, score=total / grid - n)

    # One Prussian corps over 20 years, against the rate of the ten corps Bortkiewicz kept.
    kicks = read_kicks()
    regular = [c for c in kicks if c not in REGULAR_EXCLUDED]
    reg_total, reg_n = sum(sum(kicks[c]) for c in regular), 20 * len(regular)
    lam0 = reg_total / reg_n
    corps = {}
    for c, deaths in kicks.items():
        st = three_statistics(sum(deaths), len(deaths), lam0)
        st.update(total=sum(deaths), n=len(deaths), lam_hat=sum(deaths) / len(deaths), excluded=c in REGULAR_EXCLUDED)
        corps[c] = st
    pick = args.corps
    ck = corps[pick]
    ck_total, ck_n = ck["total"], ck["n"]
    ck_lam, ck_se = ck_total / ck_n, math.sqrt(ck_total / ck_n / ck_n)
    print(f"\nCorps {pick}: {ck_total} deaths in {ck_n} years, lam_hat = {ck_lam:.4f} (SE {ck_se:.4f}); "
          f"H0: the {len(regular)} regular corps' rate {reg_total}/{reg_n} = {lam0:.4f} "
          f"(its own SE {math.sqrt(lam0 / reg_n):.4f}, taken as known)")
    print(f"  Wald {ck['wald']:.4f} (log scale {ck['wald_log']:.4f}), score {ck['score']:.4f}, LR {ck['lr']:.4f}; "
          f"chi2_1 p {stats.chi2.sf(ck['wald'], 1):.5f} / {stats.chi2.sf(ck['score'], 1):.5f} / {stats.chi2.sf(ck['lr'], 1):.5f}")
    ck_ll_max = float(pois_loglik(ck_total, ck_n, ck_lam))
    cgrid = np.linspace(0.35, 2.3, 157)
    out["corps"] = dict(pick=pick, null_rate=lam0, null_total=reg_total, null_n=reg_n, null_se=math.sqrt(lam0 / reg_n),
                        all=corps, total=ck_total, n=ck_n, lam_hat=ck_lam, se=ck_se,
                        intervals=poisson_intervals(ck_total, ck_n),
                        curve=dict(lam=cgrid, ll=pois_loglik(ck_total, ck_n, cgrid) - ck_ll_max,
                                   quad=-0.5 * (ck_total / ck_lam ** 2) * (cgrid - ck_lam) ** 2))
    print("  95% intervals: " + "; ".join(f"{k} {a:.4f} to {b:.4f}" for k, (a, b) in out["corps"]["intervals"].items()))
    disagree = [c for c, s in corps.items() if len({s[t] > CHI2_95 for t in ("wald", "score", "lr")}) > 1]
    print(f"  corps whose three verdicts at 5% differ: {', '.join(disagree) if disagree else 'none'}")

    # The Wald statistic on the scale lambda^c, for the corps and for V-1 at lam0 = 0.85.
    powers = np.round(np.linspace(-1, 2, 61), 4)
    out["wald_scale"] = dict(power=powers,
                             corps=[wald_power(ck_total, ck_n, lam0, c) for c in powers],
                             v1=[wald_power(total, n, 0.85, c) for c in powers])
    wc = np.array(out["wald_scale"]["corps"])
    print(f"  corps {pick}, Wald on the scale lam^c for c from -1 to 2: {wc.min():.3f} to {wc.max():.3f} "
          f"(c = 1: {wald_power(ck_total, ck_n, lam0, 1):.3f}; c = 0, log: {wald_power(ck_total, ck_n, lam0, 0):.3f}; "
          f"c = 1/3: {wald_power(ck_total, ck_n, lam0, 1 / 3):.3f}); score and LR do not change with the scale")

    # Exact sizes of the nominal 5% tests, as a function of the expected total count m = n lam0.
    ms = np.unique(np.concatenate([np.geomspace(0.5, 2000, 400), [n * lam, n * 0.85, ck_n * lam0]]))
    sizes = [exact_sizes(m) for m in ms]
    out["sizes"] = dict(m=ms, **{k: [s[k] for s in sizes] for k in ("wald", "wald_log", "score", "lr", "verdicts_differ")},
                        min_mass_covered=min(s["mass_covered"] for s in sizes))
    for m_show in (ck_n * lam0, n * lam):
        s = exact_sizes(m_show)
        print(f"  exact size at expected count {m_show:.1f}: Wald {s['wald']:.4f}, log-Wald {s['wald_log']:.4f}, "
              f"score {s['score']:.4f}, LR {s['lr']:.4f}; verdicts differ with probability {s['verdicts_differ']:.4f}")
    band = lambda key, lo, hi: max(abs(v - 0.05) for v, m in zip(out["sizes"][key], ms) if lo <= m <= hi)
    for lo, hi in ((0.5, 2), (2, 20), (20, 200), (200, 2000)):
        print(f"    m in [{lo}, {hi}]: largest |size - 5%| Wald {band('wald', lo, hi):.4f}, score {band('score', lo, hi):.4f}, "
              f"LR {band('lr', lo, hi):.4f}")
    return out


# ----------------------------------------------------------------------- negative binomial
def nb_ll(ys, ws, mu, k):
    """Negative binomial log-likelihood of a frequency table, parameterised by mean mu and shape k.

    log Gamma(y + k) - log Gamma(k) - y log(k + mu) is written as sum_{j<y} log1p((j - mu)/(k + mu)), which
    is exact for integer y and tends smoothly to the Poisson as k grows.
    """
    total = 0.0
    for y, w in zip(ys, ws):
        j = np.arange(y)
        total += w * (np.log1p((j - mu) / (k + mu)).sum() - k * np.log1p(mu / k) + y * math.log(mu)
                      - special.gammaln(y + 1))
    return float(total)


def nb_score_k(ys, ws, ybar, k):
    """d l / d k at mu = ybar (the profile score in k), and its derivative in k."""
    s, ds = 0.0, 0.0
    for y, w in zip(ys, ws):
        j = np.arange(y)
        s += w * (1 / (k + j)).sum()
        ds -= w * (1 / (k + j) ** 2).sum()
    n = ws.sum()
    return s - n * math.log1p(ybar / k), ds + n * ybar / (k * (k + ybar))


def nb_information(ys, ws, mu, k):
    """Observed information matrix (analytic) at (mu, k), and the expected information (series)."""
    n = ws.sum()
    jmm = float((ws * (ys / mu ** 2 - (k + ys) / (k + mu) ** 2)).sum())
    jmk = float(-(ws * (ys - mu) / (k + mu) ** 2).sum())
    jkk = float(sum(w * (1 / (k + np.arange(y)) ** 2).sum() for y, w in zip(ys, ws))
                - (ws * (1 / k - 1 / (k + mu) + (ys - mu) / (k + mu) ** 2)).sum())
    yy = np.arange(0, 4000)
    p = stats.nbinom.pmf(yy, k, k / (k + mu))                      # SciPy: n = k, p = k / (k + mu)
    inner = np.concatenate([[0.0], np.cumsum(1 / (k + yy[:-1]) ** 2)])   # sum_{j<y} 1/(k + j)^2
    ikk = n * float((p * inner).sum() - mu / (k * (k + mu)))
    imm = n * k / (mu * (k + mu))
    return np.array([[jmm, jmk], [jmk, jkk]]), np.array([[imm, 0.0], [0.0, ikk]]), float(p.sum())


def nb_freq_expected(n, mu, k, top):
    """Expected counts for 0..top-1 and the pooled class top or more."""
    p = stats.nbinom.pmf(np.arange(top), k, k / (k + mu))
    return np.append(n * p, n * (1 - p.sum()))


def profile_bounds(f, x_hat, lo, hi, drop):
    """Both roots of f(x) = f(x_hat) - drop, bracketing outward from x_hat inside (lo, hi)."""
    target = f(x_hat) - drop
    g = lambda x: f(x) - target
    return optimize.brentq(g, lo, x_hat, xtol=1e-12), optimize.brentq(g, x_hat, hi, xtol=1e-12)


def nb_table_matrix(F, cls):
    """Per data set (rows of a frequency matrix): n, mean, divisor-n variance, and whether variance > mean.

    The last is decided in exact integer arithmetic, n sum y^2 - (sum y)^2 - n sum y > 0, because a table
    whose variance equals its mean exactly can come out a hair above it in floating point.
    """
    n = F.sum(1)
    s1, s2 = F @ cls, F @ cls ** 2                                  # integers, exact in float64 at these sizes
    ybar = s1 / n
    var_n = s2 / n - ybar ** 2
    return n, ybar, var_n, n * s2 - s1 * s1 - n * s1 > 0


def nb_gain(F, cls, ybar, k):
    """(l_NB(ybar, k) - l_Poisson(ybar)) per data set, stable as k grows; k = inf gives 0."""
    out = np.zeros(len(F))
    fin = np.isfinite(k)
    if fin.any():
        kk, mu, Ff = k[fin][:, None], ybar[fin][:, None], F[fin]
        j = cls[:-1][None, :]
        g = np.zeros((fin.sum(), len(cls)))
        g[:, 1:] = np.cumsum(np.log1p((j - mu) / (kk + mu)), 1)    # sum_{j<y} log1p((j - mu)/(k + mu))
        n = Ff.sum(1)
        out[fin] = (Ff * g).sum(1) + n * (mu[:, 0] - k[fin] * np.log1p(mu[:, 0] / k[fin]))
    return out


def fit_k_matrix(F, cls, t_lo=-8.0, t_hi=18.0, iters=56):
    """MLE of k for many frequency tables at once: bisection on log k of the profile score.

    A table with divisor-n variance at most its mean has no finite maximum: its MLE is k = inf (the
    Poisson, alpha = 1/k = 0), on the boundary. Otherwise the score is positive below k_hat and negative
    above it.
    """
    n, ybar, var_n, over = nb_table_matrix(F, cls)
    lo, hi = np.full(len(F), t_lo), np.full(len(F), t_hi)
    j = cls[:-1][None, :]
    for _ in range(iters):
        t = 0.5 * (lo + hi)
        k = np.exp(t)[:, None]
        h = np.zeros((len(F), len(cls)))
        h[:, 1:] = np.cumsum(1 / (k + j), 1)
        s = (F * h).sum(1) - n * np.log1p(ybar / k[:, 0])
        up = s > 0
        lo, hi = np.where(up, t, lo), np.where(up, hi, t)
    k = np.exp(0.5 * (lo + hi))
    return np.where(over, k, np.inf), n, ybar, var_n


def fit_k_box(F, cls, t_lo=-5.0, t_hi=5.0):
    """An earlier draft (used with --fault): the same fit with log k confined to (-5, 5), as a generic
    bounded optimiser call would do."""
    k, n, ybar, var_n = fit_k_matrix(F, cls, t_lo, t_hi)
    k_box = np.minimum(np.where(np.isfinite(k), k, math.exp(t_hi)), math.exp(t_hi))
    return k_box, n, ybar, var_n


def stage_nb(cfg, args):
    import statsmodels.api as sm
    out = {}
    ys, ws = read_table(GY_CSV)
    n = int(ws.sum())
    ybar = float((ys * ws).sum() / n)
    var1 = float((ws * (ys - ybar) ** 2).sum() / (n - 1))
    k_mom = ybar ** 2 / (var1 - ybar)
    print(f"Greenwood and Yule: n = {n} women, mean {ybar:.6f}, variance {var1:.6f} (divisor n - 1); "
          f"moment estimate k = {k_mom:.6f}")

    # Newton's method on the profile score in k (mu_hat = ybar for every k), from the moment estimate.
    t, iters = math.log(k_mom), []
    for it in range(30):
        k = math.exp(t)
        s, ds = nb_score_k(ys, ws, ybar, k)
        step = s / (k * ds)
        iters.append(dict(iteration=it, k=k, score=s, step_log_k=step))
        print(f"  Newton {it}: k = {k:.10f}  score {s:+.3e}  step in log k {-step:+.3e}")
        t -= step
        if abs(step) < 1e-13:
            break
    k_hat = math.exp(t)
    ll_nb = nb_ll(ys, ws, ybar, k_hat)
    ll_pois = float((ws * (ys * math.log(ybar) - ybar - special.gammaln(ys + 1))).sum())
    ll_mom = nb_ll(ys, ws, ybar, k_mom)
    print(f"  MLE: mu_hat = {ybar:.6f} (the sample mean), k_hat = {k_hat:.6f}, alpha_hat = 1/k_hat = {1 / k_hat:.6f}")
    print(f"  log-likelihood: NB {ll_nb:.4f} at the MLE, {ll_mom:.4f} at the moment fit; Poisson {ll_pois:.4f}")

    # Reference implementations.
    neg = lambda p: -nb_ll(ys, ws, math.exp(p[0]), math.exp(p[1]))
    sp = optimize.minimize(neg, [math.log(ybar) + 0.2, math.log(k_mom) + 0.3], method="Nelder-Mead",
                           options=dict(xatol=1e-11, fatol=1e-13, maxiter=20000))
    y = np.repeat(ys, ws).astype(float)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        smfit = sm.NegativeBinomial(y, np.ones((n, 1)), loglike_method="nb2").fit(disp=0, method="newton",
                                                                               maxiter=100, tol=1e-12)
    sm_mu, sm_alpha = math.exp(smfit.params[0]), smfit.params[1]
    print(f"  scipy.optimize.minimize (Nelder-Mead on log mu, log k): mu {math.exp(sp.x[0]):.6f}, k {math.exp(sp.x[1]):.6f}, "
          f"log-lik {-sp.fun:.4f}")
    print(f"  statsmodels NegativeBinomial (nb2): mu {sm_mu:.6f}, alpha {sm_alpha:.6f} (1/alpha = {1 / sm_alpha:.6f}), "
          f"SE(alpha) {smfit.bse[1]:.6f}, llf {smfit.llf:.4f}")

    obs, expd, mass = nb_information(ys, ws, ybar, k_hat)
    h = 1e-5                                                       # numerical Hessian, a check on the algebra
    num = np.zeros((2, 2))
    pt = np.array([ybar, k_hat])
    for a in range(2):
        for b in range(2):
            e_a, e_b = np.eye(2)[a] * h, np.eye(2)[b] * h
            f = lambda d: nb_ll(ys, ws, *(pt + d))
            num[a, b] = -(f(e_a + e_b) - f(e_a - e_b) - f(-e_a + e_b) + f(-e_a - e_b)) / (4 * h * h)
    se_obs, se_exp = np.sqrt(np.diag(np.linalg.inv(obs))), np.sqrt(np.diag(np.linalg.inv(expd)))
    print(f"  observed information J: mu-mu {obs[0, 0]:.4f}, mu-k {obs[0, 1]:.2e}, k-k {obs[1, 1]:.6f} "
          f"(numerical Hessian {num[0, 0]:.4f}, {num[0, 1]:.1e}, {num[1, 1]:.6f})")
    print(f"  expected information I: mu-mu {expd[0, 0]:.4f}, k-k {expd[1, 1]:.6f} (series mass {mass:.15f})")
    print(f"  SE(mu_hat) {se_obs[0]:.6f}; SE(k_hat) {se_obs[1]:.6f} observed, {se_exp[1]:.6f} expected; "
          f"SE(alpha_hat) by the observed information {se_obs[1] / k_hat ** 2:.6f}")

    # Intervals for k: profile likelihood (mu profiled out: mu_hat(k) = ybar for every k), and Wald.
    prof = lambda kk: nb_ll(ys, ws, ybar, kk)
    inner = [optimize.minimize_scalar(lambda m: -nb_ll(ys, ws, m, kk), bounds=(0.2, 0.9), method="bounded",
                                      options=dict(xatol=1e-12)).x for kk in (0.5, k_hat, 2.0)]
    pk = profile_bounds(prof, k_hat, 0.05, 50.0, CHI2_95 / 2)
    ints = dict(profile=pk, wald_obs=(k_hat - Z975 * se_obs[1], k_hat + Z975 * se_obs[1]),
                wald_exp=(k_hat - Z975 * se_exp[1], k_hat + Z975 * se_exp[1]),
                wald_log=(k_hat * math.exp(-Z975 * se_obs[1] / k_hat), k_hat * math.exp(Z975 * se_obs[1] / k_hat)))
    print(f"  inner maximum over mu at k = 0.5, k_hat, 2.0: {inner[0]:.6f}, {inner[1]:.6f}, {inner[2]:.6f}")
    for name, (a, b) in ints.items():
        print(f"  95% interval for k, {name:9s}: {a:.4f} to {b:.4f}  (below k_hat {k_hat - a:.4f}, above {b - k_hat:.4f})")
    a_se = se_obs[1] / k_hat ** 2
    ints_alpha = dict(profile=(1 / pk[1], 1 / pk[0]), wald=(1 / k_hat - Z975 * a_se, 1 / k_hat + Z975 * a_se))
    print(f"  for alpha = 1/k: profile {ints_alpha['profile'][0]:.4f} to {ints_alpha['profile'][1]:.4f}; "
          f"Wald {ints_alpha['wald'][0]:.4f} to {ints_alpha['wald'][1]:.4f}")

    # The delta method for the dispersion index D = Var / mean = 1 + mu / k, against its profile likelihood.
    d_hat = 1 + ybar / k_hat
    grad = np.array([1 / k_hat, -ybar / k_hat ** 2])
    cov = np.linalg.inv(obs)
    se_d = float(math.sqrt(grad @ cov @ grad))
    share_k = float(grad[1] ** 2 * cov[1, 1] / (grad @ cov @ grad))

    def prof_d(dd):
        r = optimize.minimize_scalar(lambda m: -nb_ll(ys, ws, m, m / (dd - 1)), bounds=(0.25, 0.8),
                                     method="bounded", options=dict(xatol=1e-12))
        return -r.fun
    pd = profile_bounds(prof_d, d_hat, 1.05, 4.0, CHI2_95 / 2)
    print(f"  dispersion index 1 + mu/k: {d_hat:.4f}; delta-method SE {se_d:.4f} ({share_k:.1%} of its variance from k); "
          f"delta 95% {d_hat - Z975 * se_d:.4f} to {d_hat + Z975 * se_d:.4f}; profile {pd[0]:.4f} to {pd[1]:.4f}")

    # Fit against the counts, beside the moment fit.
    top = 5
    observed = np.append(ws[:top], ws[top:].sum())
    pois_exp = np.append(n * stats.poisson.pmf(np.arange(top), ybar), n * stats.poisson.sf(top - 1, ybar))
    fits = {}
    for name, kk in (("ml", k_hat), ("moments", k_mom)):
        e = nb_freq_expected(n, ybar, kk, top)
        fits[name] = dict(k=kk, expected=e, chisq=float(((observed - e) ** 2 / e).sum()))
    fits["poisson"] = dict(expected=pois_exp, chisq=float(((observed - pois_exp) ** 2 / pois_exp).sum()))
    print("  expected women with 0..4 and 5+ accidents: " + "; ".join(
        f"{k} " + ", ".join(f"{v:.1f}" for v in f['expected']) + f" (chi2 {f['chisq']:.2f})" for k, f in fits.items()))

    # Likelihood regions in (mu, k): the boundary where l drops by chi2_2 / 2, traced along rays from the MLE.
    se_mu, se_lk = se_obs[0], se_obs[1] / k_hat
    regions = {}
    for level in (0.50, 0.95, 0.99):
        drop = stats.chi2.ppf(level, 2) / 2
        pts = []
        for phi in np.linspace(0, 2 * math.pi, 181):
            g = lambda r: nb_ll(ys, ws, ybar + r * math.cos(phi) * se_mu,
                                k_hat * math.exp(r * math.sin(phi) * se_lk)) - (ll_nb - drop)
            r = optimize.brentq(g, 0.0, 12.0, xtol=1e-10)
            pts.append((ybar + r * math.cos(phi) * se_mu, k_hat * math.exp(r * math.sin(phi) * se_lk)))
        regions[str(level)] = pts
    ks95 = [p[1] for p in regions["0.95"]]
    print(f"  joint 95% likelihood region: k from {min(ks95):.4f} to {max(ks95):.4f}; "
          f"Wald ellipse: k from {k_hat - math.sqrt(stats.chi2.ppf(0.95, 2)) * se_obs[1]:.4f} "
          f"to {k_hat + math.sqrt(stats.chi2.ppf(0.95, 2)) * se_obs[1]:.4f}")
    kgrid = np.geomspace(0.3, 3.0, 181)
    out.update(n=n, ybar=ybar, var1=var1, k_mom=k_mom, newton=iters, k_hat=k_hat, alpha_hat=1 / k_hat,
               ll_nb=ll_nb, ll_pois=ll_pois, ll_mom=ll_mom,
               scipy=dict(mu=math.exp(sp.x[0]), k=math.exp(sp.x[1]), ll=-sp.fun),
               statsmodels=dict(mu=sm_mu, alpha=sm_alpha, se_alpha=smfit.bse[1], se_const=smfit.bse[0], llf=smfit.llf),
               obs_info=obs, exp_info=expd, num_hessian=num, se_obs=se_obs, se_exp=se_exp, inner_mu=inner,
               intervals_k=ints, intervals_alpha=ints_alpha,
               dispersion=dict(d_hat=d_hat, se_delta=se_d, share_from_k=share_k,
                               delta=(d_hat - Z975 * se_d, d_hat + Z975 * se_d), profile=pd),
               fits=fits, regions=regions,
               profile_curve=dict(k=kgrid, ll=[prof(kk) - ll_nb for kk in kgrid],
                                  wald=-0.5 * obs[1, 1] * (kgrid - k_hat) ** 2,
                                  wald_log=-0.5 * (obs[1, 1] * k_hat ** 2) * (np.log(kgrid) - math.log(k_hat)) ** 2))
    dgrid = np.linspace(1.15, 2.3, 116)
    out["dispersion"]["curve"] = dict(d=dgrid, ll=[prof_d(dd) - ll_nb for dd in dgrid],
                                      delta=-0.5 * (dgrid - d_hat) ** 2 / se_d ** 2)

    # The sampling distribution of k_hat: data sets of 647 women drawn from the fitted model, refitted.
    reps, cls = cfg["k_sampling"], np.arange(46)
    pmf = class_probs(stats.nbinom(k_hat, k_hat / (k_hat + ybar)), len(cls))
    rng = stream(args.seed, "nb", 1)
    k_star, d_star = [], []
    for start in range(0, reps, ROWS):
        F = rng.multinomial(n, pmf, size=min(ROWS, reps - start)).astype(float)
        kk, _, yb, _ = fit_k_matrix(F, cls)
        k_star.append(kk)
        d_star.append(1 + yb / kk)
    k_star, d_star = np.concatenate(k_star), np.concatenate(d_star)
    fin = np.isfinite(k_star)
    kf = k_star[fin]
    lo_w, hi_w = ints["wald_obs"]
    sk = float(stats.skew(kf))
    above, below = float((k_star > hi_w).mean()), float((k_star < lo_w).mean())
    print(f"  k_hat over R = {reps} data sets from the fitted model: mean {kf.mean():.4f}, median {np.median(kf):.4f}, "
          f"SD {kf.std(ddof=1):.4f} (Wald SE {se_obs[1]:.4f}), skewness {sk:.3f}; infinite in {1 - fin.mean():.4%}")
    print(f"    beyond the Wald limits: above {hi_w:.4f} in {above:.4f} ± {mcse_share(above, reps):.4f}, "
          f"below {lo_w:.4f} in {below:.4f} ± {mcse_share(below, reps):.4f}")
    print(f"    dispersion index: SD {d_star.std(ddof=1):.4f} against the delta-method SE {se_d:.4f}; "
          f"skewness {float(stats.skew(d_star)):.3f}")
    edges = np.linspace(0.3, 2.1, 91)
    hist = np.histogram(np.clip(kf, edges[0], edges[-1] - 1e-9), bins=edges)[0]
    out["k_sampling"] = dict(R=reps, mean=kf.mean(), median=np.median(kf), sd=kf.std(ddof=1), skew=sk,
                             share_infinite=float(1 - fin.mean()), above_wald=above, below_wald=below,
                             above_mcse=mcse_share(above, reps), below_mcse=mcse_share(below, reps),
                             q025=np.quantile(kf, 0.025), q975=np.quantile(kf, 0.975),
                             d_sd=d_star.std(ddof=1), d_skew=float(stats.skew(d_star)),
                             hist_edges=edges, hist=hist.tolist())
    return out


# ------------------------------------------------------------------------------- boundary
def lr_poisson_vs_nb(ys, ws):
    """LR for Poisson (alpha = 0, on the boundary) against the negative binomial, for one count table."""
    cls = np.arange(ys.max() + 1)
    F = np.zeros((1, len(cls)))
    F[0, ys] = ws
    k, n, ybar, var_n = fit_k_matrix(F, cls)
    lr = float(2 * nb_gain(F, cls, ybar, k)[0])
    return dict(k_hat=float(k[0]), alpha_hat=float(1 / k[0]), lr=max(lr, 0.0), mean=float(ybar[0]),
                var_n=float(var_n[0]), p_naive=float(stats.chi2.sf(lr, 1)), p_mixture=float(0.5 * stats.chi2.sf(lr, 1)))


def simulate_null(rng, reps, n, pmf, fault=False, k_test=None):
    """R data sets of n counts; LR for Poisson vs NB (k_test None) or for H0: k = k_test (interior)."""
    cls = np.arange(len(pmf))
    lrs, zero_score = [], []
    for start in range(0, reps, ROWS):
        F = rng.multinomial(n, pmf, size=min(ROWS, reps - start)).astype(float)
        if fault:
            k, nn, ybar, var_n = fit_k_box(F, cls)
            lr = 2 * nb_gain(F, cls, ybar, k)                       # no boundary point: can go negative
        else:
            k, nn, ybar, var_n = fit_k_matrix(F, cls)
            lr = 2 * nb_gain(F, cls, ybar, k)
            if k_test is not None:
                lr = lr - 2 * nb_gain(F, cls, ybar, np.full(len(F), k_test))
            lr = np.maximum(lr, 0.0)
        lrs.append(lr)
        zero_score.append(~nb_table_matrix(F, cls)[3])
    return np.concatenate(lrs), np.concatenate(zero_score)


def summarise_lr(lrs, at_boundary, label, reps):
    p0 = float((lrs == 0).mean())
    p384, p271 = float((lrs > CHI2_95).mean()), float((lrs > MIX_95).mean())
    neg = lrs < 0
    print(f"  {label}: LR = 0 exactly in {p0:.4f} ± {mcse_share(p0, reps):.4f}; score at the boundary <= 0 in "
          f"{at_boundary.mean():.4f}; smallest LR {lrs.min():.4g}")
    if neg.any():
        print(f"    LR < 0 in {neg.mean():.4f} of data sets; of those, {at_boundary[neg].mean():.4f} have variance "
              f"<= mean, and {neg[at_boundary].mean():.4f} of the data sets with variance <= mean have LR < 0")
    print(f"    P(LR > 3.841) = {p384:.4f} ± {mcse_share(p384, reps):.4f}   P(LR > 2.706) = {p271:.4f} ± {mcse_share(p271, reps):.4f}")
    grid = np.round(np.linspace(0, 10, 101), 2)
    pos = np.sort(lrs[lrs > 0])
    qs = [0.5, 0.9, 0.95, 0.99]
    return dict(R=reps, p_zero=p0, p_zero_mcse=mcse_share(p0, reps), p_boundary_score=float(at_boundary.mean()),
                p_gt_3841=p384, p_gt_3841_mcse=mcse_share(p384, reps), p_gt_2706=p271,
                p_gt_2706_mcse=mcse_share(p271, reps), min_lr=float(lrs.min()),
                quantiles_positive={str(q): float(np.quantile(pos, q)) if len(pos) else None for q in qs},
                sf_grid=grid, sf=[float((lrs > x).mean()) for x in grid])


def stage_boundary(cfg, args):
    out = {}
    hits, squares = read_table(CLARKE_CSV)
    ys, ws = read_table(GY_CSV)
    print("Observed tests of Poisson (alpha = 0) against the negative binomial:")
    for name, (a, b) in (("v1", (hits, squares)), ("gy", (ys, ws))):
        r = lr_poisson_vs_nb(a, b)
        n = int(b.sum())
        disp = float((b * (a - r["mean"]) ** 2).sum() / r["mean"])  # Fisher's index of dispersion, the score test
        r.update(dispersion_stat=disp, dispersion_df=n - 1, p_dispersion=float(stats.chi2.sf(disp, n - 1)),
                 z_dispersion=(disp - (n - 1)) / math.sqrt(2 * (n - 1)))
        out[name] = r
        print(f"  {name}: mean {r['mean']:.4f}, variance (divisor n) {r['var_n']:.4f}; alpha_hat {r['alpha_hat']:.5f} "
              f"(k_hat {r['k_hat']:.3f}); LR {r['lr']:.4f}: chi2_1 p {r['p_naive']:.4g}, 50:50 mixture p {r['p_mixture']:.4g}; "
              f"dispersion statistic {disp:.2f} on {n - 1} df, one-sided p {r['p_dispersion']:.4g}")

    # Profile log-likelihood in alpha for V-1, and for one simulated Poisson data set whose maximum is at alpha = 0.
    cls_v = np.arange(hits.max() + 1)
    Fv = np.zeros((1, len(cls_v)))
    Fv[0, hits] = squares
    alphas = np.linspace(0, 0.25, 126)
    gain = lambda F, cls, a: [float(nb_gain(F, cls, (F @ cls) / F.sum(1), np.array([1 / x if x > 0 else np.inf]))[0])
                              for x in a]
    rng = stream(args.seed, "boundary", 9)
    lam_v1 = squares @ hits / squares.sum()
    pm = class_probs(stats.poisson(lam_v1), 21)
    while True:
        Fs = rng.multinomial(int(squares.sum()), pm, size=1).astype(float)
        _, yb, vn, _ = nb_table_matrix(Fs, np.arange(21))
        if vn[0] < yb[0] - 0.01:
            break
    out["profiles"] = dict(alpha=alphas, v1=gain(Fv, cls_v, alphas), simulated=gain(Fs, np.arange(21), alphas),
                           simulated_mean=float(yb[0]), simulated_var_n=float(vn[0]))
    print(f"  a simulated Poisson data set (n = {int(squares.sum())}): mean {yb[0]:.4f}, variance {vn[0]:.4f}, "
          f"so the profile log-likelihood falls from alpha = 0 and alpha_hat = 0")

    reps = cfg["boundary"]
    sims = {}
    for i, (name, n, lam) in enumerate((("v1", int(squares.sum()), float(lam_v1)),
                                        ("gy", int(ws.sum()), float(ws @ ys / ws.sum())))):
        if args.boundary_n:
            n = args.boundary_n
        pmf = class_probs(stats.poisson(lam), 21)
        t0 = time.perf_counter()
        lrs, zs = simulate_null(stream(args.seed, "boundary", 1 + i), reps, n, pmf, fault=args.fault)
        print(f" Poisson null, n = {n}, lam = {lam:.4f}, R = {reps} ({time.perf_counter() - t0:.1f} s):")
        sims[name] = dict(n=n, lam=lam, **summarise_lr(lrs, zs, "boundary", reps))
    out["null_boundary"] = sims

    if not args.fault:
        # Inside the parameter space: data from the fitted negative binomial, testing its true k.
        n_gy, ybar = int(ws.sum()), float(ws @ ys / ws.sum())
        k_true = nb_fit_single(ys, ws, ybar)
        pmf = class_probs(stats.nbinom(k_true, k_true / (k_true + ybar)), 46)
        t0 = time.perf_counter()
        lrs, zs = simulate_null(stream(args.seed, "boundary", 5), cfg["interior"], n_gy, pmf, k_test=k_true)
        print(f" negative binomial null, k = {k_true:.4f} inside the parameter space, n = {n_gy}, "
              f"R = {cfg['interior']} ({time.perf_counter() - t0:.1f} s):")
        out["null_interior"] = dict(n=n_gy, k=k_true, **summarise_lr(lrs, zs, "interior", cfg["interior"]))
    return out


def nb_fit_single(ys, ws, ybar):
    cls = np.arange(ys.max() + 1)
    F = np.zeros((1, len(cls)))
    F[0, ys] = ws
    return float(fit_k_matrix(F, cls)[0][0])


# ----------------------------------------------------------------------------------- tank
def stage_tank(cfg, args):
    out = {}
    N, k, m = 342, 5, 303            # part 3's capture: serials 58, 171, 272, 273 and 303
    logc = lambda NN: special.gammaln(NN + 1) - special.gammaln(k + 1) - special.gammaln(NN - k + 1)
    grid = np.arange(m, 561)
    ll = -logc(grid) + logc(m)
    first = float(ll[1] - ll[0])
    second = float(ll[2] - 2 * ll[1] + ll[0])
    curv = sum(1 / (m - j) ** 2 for j in range(k))                 # d2/dN2 of log L at N = m: positive
    print(f"German tank likelihood, k = {k} serials, largest m = {m}: L(N) = 1/C(N, {k}) for N >= {m}, 0 below")
    print(f"  at the MLE N = {m}: first difference of log L {first:.5f} (no zero score), second difference "
          f"{second:+.3e}; d2 log L / dN2 = +{curv:.3e} > 0, so -l'' is negative: no observed information")
    dist = {}
    for kk in (5, 20):
        mm = np.arange(kk, N + 1)
        p = np.exp(special.gammaln(mm) - special.gammaln(kk) - special.gammaln(mm - kk + 1) - logc_k(N, kk))
        err = N - mm                                               # N minus the MLE, never negative
        mean, sd = float((p * err).sum()), float(math.sqrt((p * err ** 2).sum() - (p * err).sum() ** 2))
        skew = float((p * (err - mean) ** 3).sum() / sd ** 3)
        dist[str(kk)] = dict(err=err[::-1][:260], p=p[::-1][:260], mean=mean, sd=sd, skew=skew,
                             p_zero=float(p[-1]), exp_scale=N / kk)
        print(f"  k = {kk}: N - MLE has mean {mean:.3f}, SD {sd:.3f}, skewness {skew:.3f} (exponential: 2), "
              f"P(MLE = N) = {p[-1]:.5f}")
    # The limit: k (N - M) / N against Exp(1) as N grows with k fixed, and the normal it never becomes.
    lim = {}
    for kk in (5, 20):
        NN = 100_000
        mm = np.arange(kk, NN + 1)
        p = np.exp(special.gammaln(mm) - special.gammaln(kk) - special.gammaln(mm - kk + 1) - logc_k(NN, kk))
        x = kk * (NN - mm[::-1]) / NN
        cdf = np.cumsum(p[::-1])
        ks_exp = float(np.abs(cdf - stats.expon.cdf(x)).max())
        mu_x, sd_x = float((p[::-1] * x).sum()), float(math.sqrt((p[::-1] * x ** 2).sum() - (p[::-1] * x).sum() ** 2))
        ks_norm = float(np.abs(cdf - stats.norm.cdf(x, mu_x, sd_x)).max())
        lim[str(kk)] = dict(N=NN, ks_exponential=ks_exp, ks_normal=ks_norm, mean=mu_x, sd=sd_x)
        print(f"  N = {NN}, k = {kk}: k(N - MLE)/N is within {ks_exp:.4f} of Exp(1) in distribution, "
              f"{ks_norm:.4f} from the normal with its mean and SD")
    out.update(N=N, k=k, m=m, curve=dict(N=grid, ll=ll), first_difference=first, second_difference=second,
               curvature=curv, distribution=dist, limit=lim)
    return out


def logc_k(NN, kk):
    return special.gammaln(NN + 1) - special.gammaln(kk + 1) - special.gammaln(NN - kk + 1)


# ------------------------------------------------------------------------------- power law
def pl_fit(tail, xmin):
    """Continuous power law above xmin: the MLE of alpha (Hill), its SE, and pointwise log densities."""
    logs = np.log(tail / xmin)
    alpha = 1 + len(tail) / logs.sum()
    return alpha, (alpha - 1) / math.sqrt(len(tail)), math.log(alpha - 1) - math.log(xmin) - alpha * logs


def ln_fit(tail, xmin):
    """Lognormal truncated below at xmin: the MLE of (mu, sigma), and pointwise log densities."""
    z, z0, n = np.log(tail), math.log(xmin), len(tail)

    def nll(p):
        mu, s = p[0], math.exp(p[1])
        a = (z0 - mu) / s
        logq = stats.norm.logsf(a)
        h = math.exp(stats.norm.logpdf(a) - logq)                  # inverse Mills ratio
        r = z - mu
        ll = -z.sum() - n * math.log(s) - 0.5 * n * math.log(2 * math.pi) - (r ** 2).sum() / (2 * s * s) - n * logq
        dmu = r.sum() / s ** 2 - n * h / s
        ds = -n / s + (r ** 2).sum() / s ** 3 - n * h * a / s
        return -ll, -np.array([dmu, ds * s])

    best = None
    for start in ((z.mean(), math.log(z.std())), (z0 - 3.0, math.log(3.0)), (z0, math.log(1.0))):
        r = optimize.minimize(nll, start, jac=True, method="L-BFGS-B", bounds=[(-60, 25), (math.log(0.05), math.log(40))])
        if best is None or r.fun < best.fun:
            best = r
    mu, s = best.x[0], math.exp(best.x[1])
    point = stats.norm.logpdf(z, mu, s) - z - stats.norm.logsf((z0 - mu) / s)
    return mu, s, point


def vuong(lp_ln, lp_pl):
    d = lp_ln - lp_pl
    big_r, sd = float(d.sum()), float(d.std())                     # CSN's eq. (C.4): divisor n
    z = big_r / (sd * math.sqrt(len(d)))
    return big_r, sd, z, float(special.erfc(abs(z) / math.sqrt(2)))


def compare_tail(x_sorted_desc, m):
    tail, xmin = x_sorted_desc[:m], x_sorted_desc[m - 1]
    alpha, se, lp = pl_fit(tail, xmin)
    mu, s, ln = ln_fit(tail, xmin)
    big_r, sd, z, p = vuong(ln, lp)
    return dict(n_tail=m, xmin=float(xmin), alpha=alpha, alpha_se=se, ln_mu=mu, ln_sigma=s,
                ll_pl=float(lp.sum()), ll_ln=float(ln.sum()), R=big_r, sd=sd, z=z, p=p)


def ks_xmin(x_sorted_desc, m_min=50):
    """CSN's choice of xmin: the threshold whose power-law fit has the smallest Kolmogorov-Smirnov distance."""
    best, curve = None, []
    for m in range(m_min, len(x_sorted_desc) + 1):
        tail = x_sorted_desc[:m][::-1]                              # ascending, tail[0] = xmin
        xmin = tail[0]
        alpha = 1 + m / np.log(tail / xmin).sum()
        fit = 1 - (tail / xmin) ** (1 - alpha)
        i = np.arange(1, m + 1)
        d = float(max(np.abs(i / m - fit).max(), np.abs((i - 1) / m - fit).max()))
        curve.append(d)
        if best is None or d < best[1]:
            best = (m, d)
    return best[0], best[1], curve


def stage_powerlaw(cfg, args):
    out = {}
    rng = np.random.default_rng(np.random.SeedSequence([PART1_SEED, PART1_STAGE]))
    x = rng.lognormal(0.0, 2.5, 10_000)
    xs = np.sort(x)[::-1]
    m10 = 1000
    surv = np.arange(1, len(xs) + 1) / len(xs)
    slope = float(np.polyfit(np.log10(xs[:m10]), np.log10(surv[:m10]), 1)[0])
    print(f"Part 1's sample regenerated: Lognormal(0, 2.5), n = 10000; top 10% threshold {xs[m10 - 1]:.12f} "
          f"(part 1 recorded {PART1_THRESHOLD:.12f}); least-squares log-log slope {slope:.4f}")
    if abs(xs[m10 - 1] - PART1_THRESHOLD) > 1e-9:
        raise SystemExit("this NumPy does not regenerate part 1's sample; the comparison below is for a different sample")
    rows = []
    for frac in (0.5, 0.25, 0.10, 0.05, 0.02, 0.01):
        c = compare_tail(xs, int(len(xs) * frac))
        c["top_share"] = frac
        rows.append(c)
        print(f"  top {frac:5.0%} ({c['n_tail']:5d} points above {c['xmin']:8.3f}): power-law alpha {c['alpha']:.4f} "
              f"± {c['alpha_se']:.4f}; lognormal mu {c['ln_mu']:7.3f} sigma {c['ln_sigma']:.3f}; "
              f"R = {c['R']:8.3f}, normalised {c['z']:6.3f}, p {c['p']:.3g}")
    m_ks, d_ks, ks_curve = ks_xmin(xs)
    c = compare_tail(xs, m_ks)
    c["ks_distance"] = d_ks
    print(f"  CSN's KS choice: xmin = {c['xmin']:.3f} ({m_ks} points, D = {d_ks:.4f}): alpha {c['alpha']:.4f}; "
          f"R = {c['R']:.3f}, normalised {c['z']:.3f}, p {c['p']:.3g}")
    out.update(n=len(x), threshold=float(xs[m10 - 1]), ls_slope=slope, by_threshold=rows, ks=c,
               ks_curve=dict(m=list(range(50, 50 + len(ks_curve)))[::25], d=ks_curve[::25]))
    tail = xs[:m10]
    a10, ln10 = rows[2], rows[2]
    sel = np.unique(np.geomspace(1, m10, 260).astype(int)) - 1
    sxmin = tail[-1]
    out["ccdf"] = dict(x=tail[sel], s=(sel + 1) / m10,
                       pl=(tail[sel] / sxmin) ** (1 - a10["alpha"]),
                       ln=stats.norm.sf((np.log(tail[sel]) - ln10["ln_mu"]) / ln10["ln_sigma"])
                       / stats.norm.sf((math.log(sxmin) - ln10["ln_mu"]) / ln10["ln_sigma"]))

    # Power of the comparison: fresh samples from the same lognormal, and from a true power law.
    reps = cfg["powerlaw"]
    sim = {}
    rng = stream(args.seed, "powerlaw", 1)
    zs = {"lognormal_top10": [], "lognormal_top5": []}
    for _ in range(reps):
        xx = np.sort(rng.lognormal(0.0, 2.5, 10_000))[::-1]
        zs["lognormal_top10"].append(compare_tail(xx, 1000)["z"])
        zs["lognormal_top5"].append(compare_tail(xx, 500)["z"])
    rng = stream(args.seed, "powerlaw", 2)
    zs["powerlaw_1000"] = []
    for _ in range(reps):
        xx = np.sort(a10["xmin"] * (1 - rng.random(1000)) ** (-1 / (a10["alpha"] - 1)))[::-1]
        zs["powerlaw_1000"].append(compare_tail(xx, 1000)["z"])
    zc = stats.norm.ppf(0.95)                                      # |z| > 1.645 is CSN's p < 0.1
    for name, v in zs.items():
        v = np.array(v)
        ln_wins, pl_wins = float((v > zc).mean()), float((v < -zc).mean())
        sim[name] = dict(R=reps, favours_lognormal=ln_wins, favours_power_law=pl_wins,
                         undecided=1 - ln_wins - pl_wins, mcse=mcse_share(0.5, reps), median_z=float(np.median(v)),
                         z_quantiles=[float(np.quantile(v, q)) for q in (0.05, 0.25, 0.5, 0.75, 0.95)])
        print(f"  {name:16s} R = {reps}: favours lognormal {ln_wins:.3f}, power law {pl_wins:.3f}, undecided "
              f"{1 - ln_wins - pl_wins:.3f} (each ± at most {mcse_share(0.5, reps):.3f}); median normalised ratio {np.median(v):.3f}")
    out["power"] = sim
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
            "statsmodels": statsmodels.__version__,
            "likelihood_py_sha1": sha1(pathlib.Path(__file__)),
            "data_sha1": {p.name: sha1(p) for p in (CLARKE_CSV, GY_CSV, KICKS_CSV)},
            "budget": budget, "seed": args.seed, "replications": QUICK if args.quick else FULL,
            "flags": {"corps": args.corps, "boundary_n": args.boundary_n, "fault": args.fault}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="fewer Monte Carlo replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261028)
    parser.add_argument("--corps", default="XI", help="poisson stage: the corps tested against the regular rate")
    parser.add_argument("--boundary-n", type=int, default=0, help="boundary stage: counts per simulated data set")
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the boundary simulation")
    args = parser.parse_args()
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, "
          f"NumPy {prov['numpy']}, SciPy {prov['scipy']}, statsmodels {prov['statsmodels']}; "
          f"likelihood.py {prov['likelihood_py_sha1']}; budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = {}
    if out_path.exists():
        captures = json.loads(out_path.read_text(encoding="utf-8"))
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"poisson": stage_poisson, "nb": stage_nb, "boundary": stage_boundary, "tank": stage_tank,
             "powerlaw": stage_powerlaw}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
