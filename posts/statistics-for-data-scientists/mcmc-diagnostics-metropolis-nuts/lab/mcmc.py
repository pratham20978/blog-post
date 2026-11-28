#!/usr/bin/env python3
"""Lab for "MCMC You Can Trust: Metropolis by Hand and the Convergence Diagnostics" (Statistics for Data Scientists, part 12).

Every number the article calls computed or measured comes from a run of this file. Each stage prints its numbers and
writes them under its own key in the capture file.

    python mcmc.py all --out mine.json             # every stage, the article's budget (a few minutes)
    python mcmc.py all --quick --out quick.json    # the reader's budget: shorter chains, fewer replications
    python mcmc.py pfizer --out mine.json          # one stage
    python mcmc.py pfizer --quick --step 0.01 --out e3.json   # E3: your own proposal step
    python mcmc.py pfizer --quick --fault --out e4.json       # E4: an earlier draft of the sampler

Stages:
    pfizer       random-walk Metropolis written from scratch and run on Part 11's posterior beta(8.700102, 163); its
                 first iterations step by step; mean, quantiles and the efficacy interval against the closed form
    tuning       the proposal scale: traces at three scales, and acceptance rate against efficiency (ESS per draw) over
                 a sweep, in one dimension (the trial) and in two (the accidents model)
    nb           Greenwood and Yule's accidents under a negative binomial with weak priors on log mu and log k: a
                 two-phase sampler checked against a brute-force grid of the two-dimensional posterior
    diagnostics  autocorrelation, effective sample size (Geyer's initial monotone sequence), MCSE of the mean and of
                 quantiles, split and rank-normalised R-hat, bulk and tail ESS: each by hand and matched to ArviZ
    mcse         the guarantee measured: how often mean +- 1.96 MCSE contains the exact posterior mean (and quantile),
                 with the naive and the ESS-based standard error
    rhat         what each R-hat sees (chains sharing a trend; one narrow chain), and R-hat against the actual error
                 over many short runs, read at the thresholds 1.1 and 1.01
    bimodal      a posterior with two separated modes: chains started in one mode, dispersed starts, a long proposal
    nuts         the accidents model in PyMC with NUTS: its diagnostics read and its answer checked against the grid

Exact quantities (beta quantiles, quadrature, the grid) carry no MCSE. Each run draws from its own stream,
SeedSequence([stage, sub-stream, seed]). Diagnostics follow Vehtari et al. (2021) and the ArviZ 1.3 source line by line.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import pathlib
import platform
import time
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
import scipy
from scipy import fft as sfft
from scipy import integrate, optimize, special, stats

HERE = pathlib.Path(__file__).resolve().parent
GY_CSV = HERE / "data" / "greenwood_yule1920_accidents.csv"
# PyTensor (under PyMC) compiles code on the first nuts run; keep its cache inside this folder, where cleanup finds it.
os.environ.setdefault("PYTENSOR_FLAGS", f"base_compiledir={HERE / '.pytensor'}")
STAGES = ("pfizer", "tuning", "nb", "diagnostics", "mcse", "rhat", "bimodal", "nuts")

# Budgets. The article quotes FULL; --quick is the reader's first run. Exact quantities ignore the budget.
FULL = dict(warmup=1000, draws=5000, sweep_draws=20000, nb_warmup=2000, nb_draws=5000, mcse_reps=2000,
            mcse_draws=1000, rhat_reps=400, nuts_draws=1000, nuts_tune=1000, cross_chains=1000)
QUICK = dict(warmup=500, draws=1000, sweep_draws=4000, nb_warmup=1000, nb_draws=2000, mcse_reps=200,
             mcse_draws=1000, rhat_reps=40, nuts_draws=500, nuts_tune=500, cross_chains=200)
CHAINS = 4

# Part 11's posterior for the vaccine group's share of cases: prior beta(0.700102, 1) plus 8 of 170 cases.
A_POST, B_POST = 0.700102 + 8, 1.0 + 162
T_VACCINE, T_PLACEBO = 2.214, 2.222             # surveillance time, thousand person-years (Polack et al. 2020)
R_SURV = T_VACCINE / T_PLACEBO
PFIZER_STEP = 0.04                              # about 2.4 posterior SDs, the one-dimensional rule (tuning stage)
PFIZER_STARTS = (0.005, 0.03, 0.15, 0.40)       # overdispersed: the posterior holds 95% between 0.024 and 0.087
LEVEL = 0.95

PRIOR_SD = 2.0                                  # log mu ~ N(0, 2^2) and log k ~ N(0, 2^2): weak, and symmetric in k <-> 1/k
NB_STARTS = ((-2.0, -2.0), (-2.0, 2.0), (1.0, -2.0), (1.0, 2.0))   # (log mu, log k), the corners of a wide box

MIX_W, MIX_D = 0.7, 16.0                        # bimodal target: 0.7 N(0, 1) + 0.3 N(16, 1), constructed
TAIL = (0.05, 0.95)


# ------------------------------------------------------------------------------- small helpers
def stream(seed, stage, sub=0):
    """An independent generator for (stage, sub-stream): varying ids first, the root seed last."""
    return np.random.default_rng(np.random.SeedSequence([STAGES.index(stage), sub, seed]))


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


def mcse_share(p, reps):
    return math.sqrt(max(p * (1 - p), 0.0) / reps)


def ve_of(theta):
    """Vaccine efficacy from the vaccine group's share of cases, adjusted for surveillance time."""
    return 1.0 - theta / ((1.0 - theta) * R_SURV)


def hist(values, lo, hi, bins):
    counts, _ = np.histogram(values, bins=bins, range=(lo, hi))
    return counts.tolist()


# ------------------------------------------------------------------------------- the sampler
def metropolis(logp, x0, step, n_iter, rng):
    """Random-walk Metropolis for many chains at once.

    logp maps an (m, d) array of states to m log densities (unnormalised; -inf outside the support). x0 is (m, d);
    step is a scalar, a (d,) or an (m, d) array of proposal standard deviations. Returns the (m, n_iter, d) draws and
    each chain's acceptance rate. A rejected proposal repeats the current state: that repeat is a draw.
    """
    x = np.array(x0, dtype=float)
    lp = logp(x)
    m, d = x.shape
    out = np.empty((m, n_iter, d))
    accepted = np.zeros(m)
    for t in range(n_iter):
        proposal = x + step * rng.standard_normal((m, d))
        lp_prop = logp(proposal)
        accept = np.log(rng.random(m)) < lp_prop - lp          # accept with probability min(1, r)
        x[accept] = proposal[accept]
        lp[accept] = lp_prop[accept]
        out[:, t] = x
        accepted += accept
    return out, accepted / n_iter


def logp_beta(x):
    """Unnormalised log density of beta(A_POST, B_POST) for an (m, 1) array; -inf outside (0, 1)."""
    t = x[:, 0]
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (A_POST - 1) * np.log(t) + (B_POST - 1) * np.log1p(-t)
    return np.where((t > 0) & (t < 1), out, -np.inf)


def logp_beta_logit(x, jacobian=True):
    """The same posterior on eta = logit(theta). The Jacobian log theta + log(1 - theta) keeps it the same posterior."""
    eta = x[:, 0]
    log_t, log_1mt = -np.logaddexp(0, -eta), -np.logaddexp(0, eta)
    out = (A_POST - 1) * log_t + (B_POST - 1) * log_1mt
    return out + (log_t + log_1mt if jacobian else 0.0)


# ------------------------------------------------------------------------------- diagnostics, by hand
def autocov(x):
    """Each chain's autocovariance at every lag, divisor n, by FFT (x is chains x draws)."""
    n = x.shape[1]
    m = sfft.next_fast_len(2 * n)
    xc = x - x.mean(axis=1, keepdims=True)
    f = np.fft.rfft(xc, n=m, axis=1)
    return np.fft.irfft(f * np.conjugate(f), n=m, axis=1)[:, :n] / n


def ess_core(x, details=False):
    """Effective sample size of chains x draws: the multi-chain autocorrelation of Vehtari et al. (2021, eq. 10),
    Geyer's initial positive then initial monotone sequence, and the cap S log10(S), as ArviZ 1.3 computes it."""
    x = np.asarray(x, dtype=float)
    m, n = x.shape
    if x.max() - x.min() < np.finfo(float).resolution:
        return (x.size, {}) if details else x.size
    acov = autocov(x)
    w = acov[:, 0].mean() * n / (n - 1.0)                       # W: mean within-chain variance, divisor n - 1
    var_plus = w * (n - 1.0) / n + (x.mean(axis=1).var(ddof=1) if m > 1 else 0.0)
    rho = np.zeros(n)
    rho[0] = rho_even = 1.0
    rho[1] = rho_odd = 1.0 - (w - acov[:, 1].mean()) / var_plus
    t = 1
    while t < n - 3 and rho_even + rho_odd > 0.0:               # initial positive sequence: pairs summed from lag 0
        rho_even = 1.0 - (w - acov[:, t + 1].mean()) / var_plus
        rho_odd = 1.0 - (w - acov[:, t + 2].mean()) / var_plus
        if rho_even + rho_odd >= 0:
            rho[t + 1], rho[t + 2] = rho_even, rho_odd
        t += 2
    max_t = t - 2
    if rho_even > 0:
        rho[max_t + 1] = rho_even
    t = 1
    while t <= max_t - 2:                                       # initial monotone sequence
        if rho[t + 1] + rho[t + 2] > rho[t - 1] + rho[t]:
            rho[t + 1] = rho[t + 2] = (rho[t - 1] + rho[t]) / 2.0
        t += 2
    s = m * n
    tau = -1.0 + 2.0 * rho[:max_t + 1].sum() + rho[max_t + 1:max_t + 2].sum()
    tau = max(tau, 1.0 / math.log10(s))
    ess = s / tau
    if np.isnan(rho).any():
        ess = float("nan")
    if details:
        return ess, {"tau": tau, "max_t": max_t, "rho": rho[:max_t + 2].copy(), "W": w, "var_plus": var_plus}
    return ess


def split(x):
    """Each chain cut into a first and a second half: chains x draws becomes 2 chains x draws // 2."""
    half = x.shape[1] // 2
    return np.vstack((x[:, :half], x[:, -half:]))


def z_scale(x):
    """Rank-normalise: pooled ranks (ties averaged), Blom's offset 3/8, then the standard normal quantile."""
    r = stats.rankdata(x, method="average").reshape(x.shape)
    return stats.norm.ppf((r - 0.375) / (x.size + 0.25))


def rhat_basic(x):
    """sqrt(var_plus / W) for chains x draws, with var_plus = (n - 1)/n W + B/n."""
    n = x.shape[1]
    b = n * x.mean(axis=1).var(ddof=1)
    w = x.var(axis=1, ddof=1).mean()
    return math.sqrt((b / w + n - 1) / n)


def rhat_variants(x):
    """The four R-hats of the article: unsplit (Gelman and Rubin's whole chains, without their small-sample
    correction), split (BDA3), and the rank-normalised split R-hat of the bulk and of the folded draws (Vehtari et al.
    2021), whose maximum is the R-hat ArviZ reports."""
    s = split(x)
    bulk = rhat_basic(z_scale(s))
    folded = rhat_basic(z_scale(np.abs(s - np.median(s))))
    return {"unsplit": rhat_basic(x), "split": rhat_basic(s), "bulk": bulk, "folded": folded,
            "rank": max(bulk, folded)}


def ess_bulk(x):
    return ess_core(z_scale(split(x)))


def ess_mean(x):
    return ess_core(split(x))


def ess_quantile(x, p):
    q = np.quantile(x, p)
    return ess_core(split((x <= q).astype(float)))


def ess_tail(x):
    return min(ess_quantile(x, TAIL[0]), ess_quantile(x, TAIL[1]))


def mcse_mean(x):
    return float(np.std(x, ddof=1) / math.sqrt(ess_mean(x)))


def mcse_quantile(x, p):
    """Vehtari et al. (2021, section 4.4): propagate the 16% and 84% quantiles of beta(ESS p + 1, ESS (1 - p) + 1)
    through the empirical quantile function, and halve the distance."""
    ess = ess_quantile(x, p)
    a, b = stats.beta.ppf([0.1586553, 0.8413447], ess * p + 1, ess * (1 - p) + 1)
    s = np.sort(x.ravel())
    size = s.size
    lo = s[int(math.floor(max(a * size - 1, 0)))]
    hi = s[int(math.ceil(min(b * size - 1, size - 1)))]
    return float((hi - lo) / 2)


def summarize(x):
    """Every diagnostic for one scalar quantity's chains x draws."""
    out = rhat_variants(x)
    out.update(ess_bulk=ess_bulk(x), ess_tail=ess_tail(x), ess_mean=ess_mean(x), mcse_mean=mcse_mean(x))
    return out


def acf(x, lags):
    """Mean over chains of each chain's autocorrelation (divisor n), lags 0..lags."""
    ac = autocov(x)
    return (ac[:, :lags + 1] / ac[:, :1]).mean(axis=0)


# ------------------------------------------------------------------------------- the trial's posterior
def pfizer_exact():
    post = stats.beta(A_POST, B_POST)
    q_theta = post.ppf([0.975, 0.5, 0.025])                   # VE decreases in theta: theta's upper quantile is VE's lower
    mean_ve = integrate.quad(lambda t: ve_of(t) * post.pdf(t), 0, 1, epsabs=1e-13, limit=200)[0]
    sd_ve = math.sqrt(integrate.quad(lambda t: (ve_of(t) - mean_ve) ** 2 * post.pdf(t), 0, 1, epsabs=1e-14,
                                     limit=200)[0])
    return {"theta_mean": post.mean(), "theta_sd": post.std(), "theta_q025": post.ppf(0.025),
            "theta_q975": post.ppf(0.975), "ve_mean": mean_ve, "ve_sd": sd_ve, "ve_q025": ve_of(q_theta[0]),
            "ve_median": ve_of(q_theta[1]), "ve_q975": ve_of(q_theta[2]), "p_ve_le_30": post.sf(0.7 * R_SURV / (1 + 0.7 * R_SURV))}


def pfizer_chains(cfg, seed, step=PFIZER_STEP, sub=0):
    rng = stream(seed, "pfizer", sub)
    x0 = np.array(PFIZER_STARTS)[:, None]
    draws, acc = metropolis(logp_beta, x0, step, cfg["warmup"] + cfg["draws"], rng)
    return draws[:, :, 0], acc


def ve_estimates(theta_draws):
    """Mean, median and 2.5%/97.5% quantiles of VE from theta draws (chains x draws), each with its MCSE."""
    ve = ve_of(theta_draws)
    out = {"mean": (float(ve.mean()), mcse_mean(ve))}
    for name, p in (("q025", 0.025), ("median", 0.5), ("q975", 0.975)):
        out[name] = (float(np.quantile(ve, p)), mcse_quantile(ve, p))
    return out


def stage_pfizer(cfg, args):
    ex = pfizer_exact()
    print(f"[pfizer] random-walk Metropolis on Part 11's posterior beta({A_POST:.6f}, {B_POST:g}) for the vaccine group's "
          f"share theta; VE = 1 - theta/((1 - theta) r), r = {T_VACCINE}/{T_PLACEBO}")
    print(f"  exact: E(theta) {ex['theta_mean']:.6f}, SD {ex['theta_sd']:.6f}; VE mean {pc(ex['ve_mean'], 3)}%, "
          f"median {pc(ex['ve_median'], 3)}%, 95% interval {pc(ex['ve_q025'], 3)}% to {pc(ex['ve_q975'], 3)}%, "
          f"SD {pc(ex['ve_sd'], 3)} points")

    # The first iterations of one chain, step by step.
    rng = stream(args.seed, "pfizer", 9)
    theta, rows = 0.10, []
    for t in range(1, 9):
        prop = theta + PFIZER_STEP * rng.standard_normal()
        lp = logp_beta(np.array([[theta]]))[0]
        lp_prop = logp_beta(np.array([[prop]]))[0]
        log_r = lp_prop - lp
        u = rng.random()
        accept = bool(math.log(u) < log_r)
        rows.append({"t": t, "theta": theta, "proposal": prop, "r": math.exp(min(log_r, 700)) if math.isfinite(log_r) else 0.0,
                     "u": u, "accept": accept})
        theta = prop if accept else theta
        rows[-1]["next"] = theta
    print("  first iterations from theta = 0.10, step 0.04:  t  theta  proposal  r = p(prop)/p(theta)  u  decision")
    for r in rows:
        print(f"    {r['t']}  {r['theta']:.4f}  {r['proposal']:.4f}  {r['r']:.4g}  {r['u']:.4f}  "
              f"{'accept' if r['accept'] else 'reject: repeat ' + format(r['theta'], '.4f')}")

    step = args.step if args.step else PFIZER_STEP
    if args.fault:
        # E4: a "faster" draft that samples eta = logit(theta) so that no proposal falls outside (0, 1).
        rng = stream(args.seed, "pfizer", 3)
        x0 = special.logit(np.array(PFIZER_STARTS))[:, None]
        eta, acc = metropolis(lambda x: logp_beta_logit(x, jacobian=False), x0, 0.8,
                              cfg["warmup"] + cfg["draws"], rng)
        draws = special.expit(eta[:, cfg["warmup"]:, 0])
        print("  (--fault: an earlier draft of this stage, sampling logit(theta) with step 0.8)")
    else:
        all_draws, acc = pfizer_chains(cfg, args.seed, step)
        draws = all_draws[:, cfg["warmup"]:]
    est = ve_estimates(draws)
    diag = summarize(draws)
    print(f"  {CHAINS} chains from theta = {', '.join(map(str, PFIZER_STARTS))}; warmup {cfg['warmup']} discarded, "
          f"{cfg['draws']} kept each; step {step if not args.fault else 0.8}; acceptance "
          f"{', '.join(pc(a, 1) + '%' for a in acc)}")
    print(f"  R-hat {diag['rank']:.4f}; bulk ESS {diag['ess_bulk']:.0f}; tail ESS {diag['ess_tail']:.0f} "
          f"(of S = {draws.size})")
    exact_map = {"mean": ex["ve_mean"], "q025": ex["ve_q025"], "median": ex["ve_median"], "q975": ex["ve_q975"]}
    zs = {}
    for k in ("mean", "q025", "median", "q975"):
        v, se = est[k]
        zs[k] = (v - exact_map[k]) / se
        print(f"  VE {k:>6}: chain {pc(v, 3)}% +- {pc(se, 3)} (MCSE); exact {pc(exact_map[k], 3)}%; z = {zs[k]:+.2f}")
    verdict = "PASS: every estimate within 3 MCSE of the closed form" if max(abs(z) for z in zs.values()) < 3 else \
        "FAIL: an estimate is more than 3 MCSE from the closed form"
    print(f"  check: {verdict}")
    draws_ve = ve_of(draws)
    p_le_30 = float((draws_ve <= 0.30).mean())
    print(f"  P(VE <= 30%): exact {ex['p_ve_le_30']:.3g}; the chain's share {p_le_30:g} of {draws.size} draws")

    out = {"exact": ex, "first_iterations": rows, "step": step, "starts": PFIZER_STARTS, "acceptance": acc.tolist(),
           "estimates": {k: {"value": v, "mcse": se, "z": zs[k]} for k, (v, se) in est.items()},
           "diagnostics": diag, "check": verdict, "chain_p_ve_le_30": p_le_30, "fault": args.fault}
    if not args.fault and not args.step:
        # Figure data: the first 400 iterations of each chain (warmup included), and a histogram of the kept draws.
        out["trace_head"] = [c[:400].tolist() for c in all_draws]
        lo, hi, nb = 0.86, 0.995, 54
        out["ve_hist"] = {"lo": lo, "hi": hi, "counts": hist(draws_ve, lo, hi, nb), "n": int(draws_ve.size)}
        v = np.linspace(lo, hi, 271)
        th = R_SURV * (1 - v) / (1 + R_SURV * (1 - v))
        dens = stats.beta(A_POST, B_POST).pdf(th) * R_SURV / (1 + R_SURV * (1 - v)) ** 2
        out["ve_density"] = {"v": v.tolist(), "density": dens.tolist()}
        # A Metropolis step drawn on the density: theta's density on a grid, for Figure 1.
        g = np.linspace(0.0, 0.16, 321)
        out["theta_density"] = {"theta": g.tolist(), "density": stats.beta(A_POST, B_POST).pdf(g).tolist()}
        # Running means: one chain's kept draws against as many independent exact draws, with 95% bands from the
        # chain's own tau (dependent draws) and from tau = 1 (independent draws).
        iid = ve_of(stream(args.seed, "pfizer", 5).beta(A_POST, B_POST, size=cfg["draws"]))
        c1 = draws_ve[0]
        tau1 = ess_core(split(c1[None, :]), details=True)[1]["tau"]
        idx = np.unique(np.geomspace(10, cfg["draws"], 140).round().astype(int))
        out["running"] = {"n": idx.tolist(), "chain": (np.cumsum(c1)[idx - 1] / idx).tolist(),
                          "iid": (np.cumsum(iid)[idx - 1] / idx).tolist(), "tau_chain1": tau1,
                          "sd": float(ex["ve_sd"]), "exact": float(ex["ve_mean"])}
    return out


# ------------------------------------------------------------------------------- the accidents model
def read_gy():
    rows = [line.strip().split(",") for line in GY_CSV.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")][1:]
    y = np.array([int(r[0]) for r in rows])
    w = np.array([int(r[1]) for r in rows])
    return y, w


Y_GY, W_GY = read_gy()


def nb_loglik(mu, k):
    """Greenwood and Yule's log-likelihood under NB(mean mu, shape k), Var = mu + mu^2/k; mu, k broadcast."""
    mu, k = np.asarray(mu, float)[..., None], np.asarray(k, float)[..., None]
    y = Y_GY
    term = (special.gammaln(y + k) - special.gammaln(k) - special.gammaln(y + 1) + k * np.log(k)
            - (k + y) * np.log(k + mu) + y * np.log(mu))
    return (W_GY * term).sum(axis=-1)


def logp_nb(x):
    """Unnormalised log posterior of (log mu, log k): the likelihood times N(0, 2^2) priors on both. The priors are
    stated on the sampler's own coordinates, so no Jacobian term is needed."""
    a, b = x[:, 0], x[:, 1]
    return nb_loglik(np.exp(a), np.exp(b)) - 0.5 * (a ** 2 + b ** 2) / PRIOR_SD ** 2


def nb_grid(n=801):
    """Brute force: the posterior on an n x n grid in (log mu, log k) around the mode, 9 Laplace SDs either side in
    log mu, and 9 below and 14.4 above in log k, whose right tail is longer."""
    res = optimize.minimize(lambda v: -logp_nb(np.array([v]))[0], x0=[-0.75, -0.1], method="Nelder-Mead",
                            options={"xatol": 1e-10, "fatol": 1e-12, "maxiter": 4000})
    mode = res.x
    h = 1e-4
    hess = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            def f(di, dj):
                v = mode.copy()
                v[i] += di
                v[j] += dj
                return logp_nb(np.array([v]))[0]
            hess[i, j] = (f(h, h) - f(h, -h) - f(-h, h) + f(-h, -h)) / (4 * h * h)
    cov = np.linalg.inv(-hess)
    sd = np.sqrt(np.diag(cov))
    a = np.linspace(mode[0] - 9 * sd[0], mode[0] + 9 * sd[0], n)
    b = np.linspace(mode[1] - 9 * sd[1] * 1.0, mode[1] + 9 * sd[1] * 1.6, n)    # log k's right tail is longer
    aa, bb = np.meshgrid(a, b, indexing="ij")
    lp = logp_nb(np.column_stack([aa.ravel(), bb.ravel()])).reshape(n, n)
    p = np.exp(lp - lp.max())
    da, db = a[1] - a[0], b[1] - b[0]
    p /= p.sum() * da * db
    edge = (p[0].sum() + p[-1].sum()) * db * da + (p[:, 0].sum() + p[:, -1].sum()) * da * db
    return {"a": a, "b": b, "p": p, "da": da, "db": db, "mode": mode, "laplace_sd": sd,
            "laplace_corr": cov[0, 1] / (sd[0] * sd[1]), "edge_mass": edge}


def grid_marginal(g, axis):
    """Marginal summaries of exp(coordinate) on one axis: mean, SD, quantiles, and the marginal density."""
    coord = g["a"] if axis == 0 else g["b"]
    d = g["db"] if axis == 0 else g["da"]
    step = g["da"] if axis == 0 else g["db"]
    marg = g["p"].sum(axis=1 - axis) * d                     # density of the log coordinate
    val = np.exp(coord)
    mean = (val * marg).sum() * step
    sd = math.sqrt(((val - mean) ** 2 * marg).sum() * step)
    cdf = np.concatenate([[0.0], np.cumsum((marg[1:] + marg[:-1]) / 2 * step)])
    cdf /= cdf[-1]
    q = {f"q{int(round(p * 1000)):03d}": float(np.exp(np.interp(p, cdf, coord))) for p in (0.025, 0.05, 0.5, 0.95, 0.975)}
    return {"mean": mean, "sd": sd, **q, "log_mean": (coord * marg).sum() * step}, marg


def nb_chains(cfg, seed, sub=0):
    """Two-phase sampling (BDA3, section 12.2): adapt the proposal during warmup, freeze it, keep only what follows.
    Warmup: 0.1 per coordinate for its first fifth, then twice 2.4/sqrt(2) x the SDs from the second half of the
    window before."""
    rng = stream(seed, "nb", sub)
    x0 = np.array(NB_STARTS)
    wu = cfg["nb_warmup"]
    w1 = wu // 5
    w2 = (wu - w1) // 2
    w3 = wu - w1 - w2
    d1, _ = metropolis(logp_nb, x0, np.array([0.1, 0.1]), w1, rng)
    step = 2.4 / math.sqrt(2) * d1[:, w1 // 2:].reshape(-1, 2).std(axis=0, ddof=1)
    d2, _ = metropolis(logp_nb, d1[:, -1], step, w2, rng)
    step = 2.4 / math.sqrt(2) * d2[:, w2 // 2:].reshape(-1, 2).std(axis=0, ddof=1)
    d3, _ = metropolis(logp_nb, d2[:, -1], step, w3, rng)
    draws, acc = metropolis(logp_nb, d3[:, -1], step, cfg["nb_draws"], rng)
    warm = np.concatenate([d1, d2, d3], axis=1)
    return draws, acc, step, warm


def stage_nb(cfg, args):
    print(f"[nb] Greenwood and Yule's 647 women: NB(mu, k), Var = mu + mu^2/k, priors log mu, log k ~ N(0, {PRIOR_SD:g}^2)")
    lo, hi = math.exp(-1.96 * PRIOR_SD), math.exp(1.96 * PRIOR_SD)
    print(f"  prior 95% range for mu and for k: {lo:.4f} to {hi:.1f}")
    g = nb_grid()
    mu_s, mu_m = grid_marginal(g, 0)
    k_s, k_m = grid_marginal(g, 1)
    print(f"  grid 801 x 801 over (log mu, log k); mass on the edge rows and columns {g['edge_mass']:.1e}")
    print(f"  posterior mode (mu, k) = ({math.exp(g['mode'][0]):.6f}, {math.exp(g['mode'][1]):.6f}); "
          f"Laplace SDs of (log mu, log k) {g['laplace_sd'][0]:.5f}, {g['laplace_sd'][1]:.5f}, corr {g['laplace_corr']:+.4f}")
    print(f"  grid: mu mean {mu_s['mean']:.6f} (SD {mu_s['sd']:.6f}), 95% {mu_s['q025']:.5f} to {mu_s['q975']:.5f}; "
          f"k mean {k_s['mean']:.6f} (SD {k_s['sd']:.6f}), median {k_s['q500']:.5f}, 95% {k_s['q025']:.5f} to {k_s['q975']:.5f}")

    draws, acc, step, warm = nb_chains(cfg, args.seed)
    mu, k = np.exp(draws[:, :, 0]), np.exp(draws[:, :, 1])
    print(f"  sampler: {CHAINS} chains from (log mu, log k) = {NB_STARTS}; warmup {cfg['nb_warmup']} (adaptive), then "
          f"step ({step[0]:.4f}, {step[1]:.4f}) frozen; {cfg['nb_draws']} kept each; acceptance "
          f"{', '.join(pc(a, 1) + '%' for a in acc)}")
    rows = {}
    for name, x, gs in (("mu", mu, mu_s), ("k", k, k_s)):
        dg = summarize(x)
        est = {"mean": (float(x.mean()), mcse_mean(x))}
        for qn, p in (("q025", 0.025), ("q500", 0.5), ("q975", 0.975)):
            est[qn] = (float(np.quantile(x, p)), mcse_quantile(x, p))
        z = {qn: (v - gs[qn]) / se for qn, (v, se) in est.items()}
        rows[name] = {"diagnostics": dg, "estimates": {qn: {"value": v, "mcse": se, "z": z[qn]} for qn, (v, se) in est.items()},
                      "grid": gs}
        print(f"  {name}: R-hat {dg['rank']:.4f}, bulk ESS {dg['ess_bulk']:.0f}, tail ESS {dg['ess_tail']:.0f}; " +
              "; ".join(f"{qn} {v:.5f} +- {se:.5f} vs grid {gs[qn]:.5f} (z {z[qn]:+.2f})" for qn, (v, se) in est.items()))
    corr = float(np.corrcoef(draws[:, :, 0].ravel(), draws[:, :, 1].ravel())[0, 1])
    zmax = max(abs(e["z"]) for r in rows.values() for e in r["estimates"].values())
    verdict = "PASS: every estimate within 3 MCSE of the grid" if zmax < 3 else "FAIL: an estimate is more than 3 MCSE off"
    print(f"  posterior correlation of log mu and log k in the draws {corr:+.4f}; check: {verdict}")

    # Figure data: a coarse view of the grid, a thinned sample of draws, the marginals.
    sel = np.linspace(0, 800, 121).round().astype(int)
    pdens = g["p"][np.ix_(sel, sel)]
    flat = np.sort(g["p"].ravel())[::-1]
    cum = np.cumsum(flat) * g["da"] * g["db"]
    levels = {str(c): float(flat[np.searchsorted(cum, c)]) for c in (0.5, 0.9, 0.99)}
    rng = stream(args.seed, "nb", 7)
    pick = rng.choice(draws.shape[1], 300, replace=False)
    thin = draws[:, pick].reshape(-1, 2)
    out = {"prior_range": [lo, hi], "grid": {"mu": mu_s, "k": k_s, "mode_mu": math.exp(g["mode"][0]),
                                               "mode_k": math.exp(g["mode"][1]), "edge_mass": g["edge_mass"],
                                               "laplace_sd": g["laplace_sd"].tolist(), "laplace_corr": g["laplace_corr"]},
           "step": step.tolist(), "acceptance": acc.tolist(), "params": rows, "draws_corr": corr, "check": verdict,
           "fig": {"a": g["a"][sel].tolist(), "b": g["b"][sel].tolist(), "p": pdens.tolist(), "levels": levels,
                   "draws_log": thin.tolist(), "warm_head": [c[:150].tolist() for c in warm],
                   "mu_marg": {"x": np.exp(g["a"][sel]).tolist(), "dens_log": mu_m[sel].tolist()},
                   "k_marg": {"x": np.exp(g["b"][sel]).tolist(), "dens_log": k_m[sel].tolist()},
                   "mu_hist": {"lo": 0.33, "hi": 0.62, "counts": hist(mu, 0.33, 0.62, 40)},
                   "k_hist": {"lo": 0.3, "hi": 2.2, "counts": hist(k, 0.3, 2.2, 40)}}}
    return out


# ------------------------------------------------------------------------------- tuning
def stage_tuning(cfg, args):
    ex = pfizer_exact()
    sd = ex["theta_sd"]
    print(f"[tuning] proposal scale, in multiples c of the posterior SD (theta: {sd:.5f})")
    # Traces at three scales from one start.
    trace_steps = (0.002, PFIZER_STEP, 1.0)
    rng = stream(args.seed, "tuning", 0)
    x0 = np.full((3, 1), 0.10)
    tr, acc3 = metropolis(logp_beta, x0, np.array(trace_steps)[:, None], 1000, rng)
    traces = {}
    for i, s in enumerate(trace_steps):
        rng = stream(args.seed, "tuning", 10 + i)
        d, a = metropolis(logp_beta, np.array(PFIZER_STARTS)[:, None], s, cfg["warmup"] + cfg["draws"], rng)
        kept = d[:, cfg["warmup"]:, 0]
        ess_d = ess_core(split(kept), details=True)[1]
        traces[str(s)] = {"c": s / sd, "acceptance_trace": float(acc3[i]), "trace": tr[i, :, 0].tolist(),
                          "acceptance": float(a.mean()), "ess_mean": ess_mean(kept), "ess_bulk": ess_bulk(kept),
                          "rhat": rhat_variants(kept)["rank"], "tau": ess_d.get("tau"), "max_t": ess_d.get("max_t"),
                          "acf": acf(kept, 80).tolist()}
        print(f"  step {s}: c = {s / sd:.2f}; acceptance {pc(a.mean(), 1)}%; ESS(mean) {traces[str(s)]['ess_mean']:.0f} "
              f"of {kept.size} draws; tau {ess_d.get('tau'):.2f}; truncation lag {ess_d.get('max_t')}; "
              f"R-hat {traces[str(s)]['rhat']:.4f}")

    # Sweep: one dimension (the trial) and two (the accidents model); chains started at the posterior mean.
    cs = np.geomspace(0.05, 40, 25)
    out_sweep = {}
    g = nb_grid()
    a_mean = (g["a"][:, None] * g["p"]).sum() * g["da"] * g["db"]
    b_mean = (g["b"][None, :] * g["p"]).sum() * g["da"] * g["db"]
    a_sd = math.sqrt((((g["a"][:, None] - a_mean) ** 2) * g["p"]).sum() * g["da"] * g["db"])
    b_sd = math.sqrt((((g["b"][None, :] - b_mean) ** 2) * g["p"]).sum() * g["da"] * g["db"])
    for dim, logp, center, scale in (("1d", logp_beta, [ex["theta_mean"]], np.array([sd])),
                                     ("2d", logp_nb, [a_mean, b_mean], np.array([a_sd, b_sd]))):
        rng = stream(args.seed, "tuning", 1 if dim == "1d" else 2)
        m = len(cs) * CHAINS
        x0 = np.tile(center, (m, 1))
        steps = np.repeat(cs, CHAINS)[:, None] * scale[None, :]
        n = 1000 + cfg["sweep_draws"]
        d, a = metropolis(logp, x0, steps, n, rng)
        acc_c, eff_c = [], []
        for i, c in enumerate(cs):
            kept = d[i * CHAINS:(i + 1) * CHAINS, 1000:, 0]
            acc_c.append(float(a[i * CHAINS:(i + 1) * CHAINS].mean()))
            eff_c.append(ess_mean(kept) / kept.size)
        best = int(np.argmax(eff_c))
        out_sweep[dim] = {"c": cs.tolist(), "acceptance": acc_c, "efficiency": eff_c, "best_c": float(cs[best]),
                          "best_acceptance": acc_c[best], "best_efficiency": eff_c[best],
                          "scale": scale.tolist()}
        print(f"  sweep {dim}: best c {cs[best]:.2f} (the rule 2.4/sqrt(d) gives {2.4 / math.sqrt(len(center)):.2f}): "
              f"acceptance {pc(acc_c[best], 1)}%, ESS per draw {eff_c[best]:.3f}")
        for c, ac, ef in zip(cs, acc_c, eff_c):
            print(f"    c {c:7.3f}  acceptance {pc(ac, 1):>5}%  ESS per draw {ef:.4f}")
    return {"traces": traces, "sweep": out_sweep, "posterior_sd_theta": sd}


# ------------------------------------------------------------------------------- diagnostics, matched to ArviZ
def arviz_values(x):
    import arviz_stats as azs
    ess = lambda method, **kw: float(azs.ess(x, method=method, **kw))   # noqa: E731
    return {"rank": float(azs.rhat(x, method="rank")), "unsplit": float(azs.rhat(x, method="identity")),
            "split": float(azs.rhat(x, method="split")), "folded": float(azs.rhat(x, method="folded")),
            # arviz-stats 1.3.3's array interface raises TypeError for method="tail" unless prob is given
            "bulk": float(azs.rhat(x, method="z_scale")), "ess_bulk": ess("bulk"), "ess_tail": ess("tail", prob=TAIL),
            "ess_mean": ess("mean"), "mcse_mean": float(azs.mcse(x, method="mean")),
            "mcse_q025": float(azs.mcse(x, method="quantile", prob=0.025)),
            "mcse_q975": float(azs.mcse(x, method="quantile", prob=0.975))}


def arviz_default_tail(x):
    """ArviZ's tail ESS on xarray input with prob left out: it takes rcParams["stats.ci_prob"] = 0.89, so the
    quantiles 0.11 and 0.89, where Vehtari et al. (2021) and R's posterior use 0.05 and 0.95."""
    import arviz_stats as azs
    import xarray as xr
    return float(azs.ess(xr.DataArray(x, dims=("chain", "draw")), method="tail"))


def stage_diagnostics(cfg, args):
    import arviz_stats as azs
    print(f"[diagnostics] by hand against arviz_stats {azs.__version__}")
    all_draws, _ = pfizer_chains(cfg, args.seed)
    theta = all_draws[:, cfg["warmup"]:]
    nb_draws, _, _, _ = nb_chains(cfg, args.seed)
    quantities = {"pfizer_theta": theta, "pfizer_ve": ve_of(theta), "nb_mu": np.exp(nb_draws[:, :, 0]),
                  "nb_k": np.exp(nb_draws[:, :, 1])}
    out, worst = {}, 0.0
    for name, x in quantities.items():
        mine = summarize(x)
        mine["mcse_q025"] = mcse_quantile(x, 0.025)
        mine["mcse_q975"] = mcse_quantile(x, 0.975)
        theirs = arviz_values(x)
        diff = {k: abs(mine[k] - theirs[k]) / max(abs(theirs[k]), 1e-300) for k in theirs}
        mine["ess_tail_11_89"] = min(ess_quantile(x, 0.11), ess_quantile(x, 0.89))
        theirs["ess_tail_default_xarray"] = arviz_default_tail(x)
        worst = max(worst, max(diff.values()))
        out[name] = {"mine": mine, "arviz": theirs, "max_rel_diff": max(diff.values())}
        print(f"  {name}: R-hat unsplit {mine['unsplit']:.5f}, split {mine['split']:.5f}, bulk {mine['bulk']:.5f}, "
              f"folded {mine['folded']:.5f} -> {mine['rank']:.5f}; ESS bulk {mine['ess_bulk']:.1f}, tail "
              f"{mine['ess_tail']:.1f}, mean {mine['ess_mean']:.1f}; MCSE mean {mine['mcse_mean']:.3g}; largest "
              f"relative difference from ArviZ {max(diff.values()):.1e}")

    # The pieces for the article's hand computation on theta: W, B, var_plus, autocorrelations, truncation.
    s = split(theta)
    n = s.shape[1]
    w = s.var(axis=1, ddof=1).mean()
    b = n * s.mean(axis=1).var(ddof=1)
    var_plus = (n - 1) / n * w + b / n
    ess_val, det = ess_core(s, details=True)
    pieces = {"split_chains": s.shape[0], "n": n, "W": w, "B": b, "var_plus": var_plus,
              "rhat_split": math.sqrt(var_plus / w), "rho_head": det["rho"][:8].tolist(), "max_t": det["max_t"],
              "tau": det["tau"], "ess_mean": ess_val, "S": s.size}
    print(f"  theta, split into {s.shape[0]} half-chains of {n}: W {w:.4e}, B {b:.4e}, var+ {var_plus:.4e}, "
          f"split R-hat {math.sqrt(var_plus / w):.5f}")
    print("  autocorrelations rho_1..rho_7 " + ", ".join(f"{r:.4f}" for r in det["rho"][1:8]) +
          f"; first pair summing below zero at lags {det['max_t'] + 1} and {det['max_t'] + 2}, so the sum keeps lags 1 to "
          f"{det['max_t']} twice and lag {det['max_t'] + 1} once; tau {det['tau']:.3f}; ESS = {s.size}/{det['tau']:.3f} = "
          f"{ess_val:.1f}")
    # MCSE of the 2.5% quantile of VE, step by step.
    ve = ve_of(theta)
    eq = ess_quantile(ve, 0.025)
    a_, b_ = stats.beta.ppf([0.1586553, 0.8413447], eq * 0.025 + 1, eq * 0.975 + 1)
    pieces["mcse_q025_ve"] = {"ess": eq, "beta_a": a_, "beta_b": b_, "mcse": mcse_quantile(ve, 0.025),
                              "estimate": float(np.quantile(ve, 0.025))}
    print(f"  VE 2.5% quantile: ESS of the indicator {eq:.1f}; beta quantiles {a_:.5f}, {b_:.5f}; MCSE "
          f"{pieces['mcse_q025_ve']['mcse']:.5f}")
    print(f"  largest relative difference across every quantity: {worst:.1e}")
    out["pieces"] = pieces
    out["worst_rel_diff"] = worst
    out["arviz_stats_version"] = azs.__version__
    return out


# ------------------------------------------------------------------------------- the MCSE's own guarantee
def stage_mcse(cfg, args):
    ex = pfizer_exact()
    reps, n_draws = cfg["mcse_reps"], cfg["mcse_draws"]
    steps = (0.008, PFIZER_STEP, 0.25)
    print(f"[mcse] {reps} independent runs per step size, each {CHAINS} chains started from exact posterior draws, "
          f"{n_draws} kept draws after 500 warmup; "
          f"exact E(theta) {ex['theta_mean']:.6f}, exact VE 2.5% quantile {pc(ex['ve_q025'], 3)}%")
    out = {"reps": reps, "draws": n_draws, "steps": {}}
    for i, s in enumerate(steps):
        rng = stream(args.seed, "mcse", i)
        x0 = rng.beta(A_POST, B_POST, size=(reps * CHAINS, 1))     # stationary from the first draw: no warmup bias
        d, a = metropolis(logp_beta, x0, s, 500 + n_draws, rng)
        d = d[:, 500:, 0].reshape(reps, CHAINS, n_draws)
        hit_naive = hit_ess = hit_q = 0
        ess_list, ratio, rh, ests, se_n, se_e = [], [], [], [], [], []
        for r in range(reps):
            x = d[r]
            est = x.mean()
            se_naive = x.std(ddof=1) / math.sqrt(x.size)
            e = ess_mean(x)
            se_ess = x.std(ddof=1) / math.sqrt(e)
            hit_naive += abs(est - ex["theta_mean"]) <= 1.96 * se_naive
            hit_ess += abs(est - ex["theta_mean"]) <= 1.96 * se_ess
            ve = ve_of(x)
            q = np.quantile(ve, 0.025)
            hit_q += abs(q - ex["ve_q025"]) <= 1.96 * mcse_quantile(ve, 0.025)
            ess_list.append(e)
            ests.append(est)
            se_n.append(se_naive)
            se_e.append(se_ess)
            ratio.append(se_ess / se_naive)
            rh.append(rhat_variants(x)["rank"])
        res = {"step": s, "acceptance": float(a.mean()), "naive": hit_naive / reps, "ess_based": hit_ess / reps,
               "quantile": hit_q / reps, "ess_median": float(np.median(ess_list)), "se_ratio_median": float(np.median(ratio)),
               "rhat_median": float(np.median(rh)), "share_rhat_lt_101": float(np.mean(np.array(rh) < 1.01)),
               "sd_of_estimates": float(np.std(ests, ddof=1)), "naive_se_median": float(np.median(se_n)),
               "ess_se_median": float(np.median(se_e))}
        out["steps"][str(s)] = res
        print(f"  step {s}: acceptance {pc(res['acceptance'], 1)}%; median ESS {res['ess_median']:.0f} of {CHAINS * n_draws}; "
              f"MCSE/naive SE {res['se_ratio_median']:.2f}; coverage of mean +- 1.96 SE: naive {pc(res['naive'])}% "
              f"(+-{pc(mcse_share(res['naive'], reps))}), ESS-based {pc(res['ess_based'])}% "
              f"(+-{pc(mcse_share(res['ess_based'], reps))}); VE 2.5% quantile +- 1.96 MCSE {pc(res['quantile'])}% "
              f"(+-{pc(mcse_share(res['quantile'], reps))}); median R-hat {res['rhat_median']:.4f}")
        print(f"    run-to-run SD of the estimate {res['sd_of_estimates']:.3e}; median naive SE {res['naive_se_median']:.3e}; "
              f"median ESS-based SE {res['ess_se_median']:.3e}")
    return out


# ------------------------------------------------------------------------------- what R-hat sees
def stage_rhat(cfg, args):
    ex = pfizer_exact()
    print("[rhat] what each R-hat sees, on the trial's posterior")
    out = {}
    # (a) A shared trend: four chains from the same far start, a small step, no warmup discarded.
    rng = stream(args.seed, "rhat", 0)
    d, a = metropolis(logp_beta, np.full((CHAINS, 1), 0.30), 0.004, 400, rng)
    x = d[:, :, 0]
    rv = rhat_variants(x)
    out["trend"] = {"rhat": rv, "ess_bulk": ess_bulk(x), "acceptance": float(a.mean()), "mean_theta": float(x.mean()),
                    "trace": x.tolist()}
    print(f"  shared trend (4 chains from theta = 0.30, step 0.004, 400 draws, no warmup): R-hat unsplit "
          f"{rv['unsplit']:.4f}, split {rv['split']:.4f}, bulk {rv['bulk']:.4f}, folded {rv['folded']:.4f}; "
          f"mean theta {x.mean():.4f} (exact {ex['theta_mean']:.4f})")
    # (b) Constructed chains, as in Vehtari et al. (2021, appendix A): four chains of independent N(0, 1) draws, one of
    # them shifted by delta or scaled to SD s. Median of each R-hat over many replications, and where it crosses.
    reps = cfg["rhat_reps"]
    deltas = np.round(np.arange(0.0, 1.61, 0.1), 2)
    scales = np.round(np.arange(1.0, 0.04, -0.05), 2)
    curves = {}
    for n in (250, 1000):
        rng = stream(args.seed, "rhat", 1 if n == 250 else 2)
        shift = {"split": [], "bulk": [], "folded": [], "unsplit": []}
        for dlt in deltas:
            vals = {k: [] for k in shift}
            for _ in range(reps):
                x = rng.standard_normal((CHAINS, n))
                x[0] += dlt
                rv = rhat_variants(x)
                for k in vals:
                    vals[k].append(rv[k])
            for k in shift:
                shift[k].append(float(np.median(vals[k])))
        scale = {"split": [], "bulk": [], "folded": [], "unsplit": []}
        for s in scales:
            vals = {k: [] for k in scale}
            for _ in range(reps):
                x = rng.standard_normal((CHAINS, n))
                x[0] *= s
                rv = rhat_variants(x)
                for k in vals:
                    vals[k].append(rv[k])
            for k in scale:
                scale[k].append(float(np.median(vals[k])))

        def crossing(xs, ys, level):
            """First x at which the median R-hat reaches level, by linear interpolation."""
            for i in range(1, len(xs)):
                if ys[i - 1] < level <= ys[i]:
                    return float(xs[i - 1] + (level - ys[i - 1]) * (xs[i] - xs[i - 1]) / (ys[i] - ys[i - 1]))
            return None
        cross = {f"shift_split_{t}": crossing(deltas, shift["split"], t) for t in (1.01, 1.1)}
        cross.update({f"scale_folded_{t}": crossing(scales, scale["folded"], t) for t in (1.01, 1.1)})
        cross.update({f"scale_split_{t}": crossing(scales, scale["split"], t) for t in (1.01, 1.1)})
        curves[str(n)] = {"deltas": deltas.tolist(), "shift": shift, "scales": scales.tolist(), "scale": scale,
                          "crossings": cross}
        i05 = int(np.where(deltas == 0.5)[0][0])
        i75 = int(np.where(scales == 0.75)[0][0])
        print(f"  constructed chains, {CHAINS} x {n} N(0, 1) draws, median of {reps} runs: one chain shifted by 0.5 -> split "
              f"R-hat {shift['split'][i05]:.4f}; one chain with SD 0.75 -> split {scale['split'][i75]:.4f}, folded "
              f"{scale['folded'][i75]:.4f}")
        print(f"    split R-hat reaches 1.01 at a shift of {cross['shift_split_1.01']:.3f} SD and 1.1 at "
              f"{cross['shift_split_1.1']:.3f} SD; folded R-hat reaches 1.01 when one chain's SD falls to "
              f"{cross['scale_folded_1.01']:.3f} and 1.1 at {cross['scale_folded_1.1']:.3f}; split R-hat never reaches 1.01 on "
              f"scale alone: {cross['scale_split_1.01'] is None}")
    out["constructed"] = curves

    # (c) The consequence on the trial's posterior: many short runs of a slow sampler (step 0.008), first half discarded.
    lengths = (25, 50, 100, 200, 400, 800, 1600, 3200)
    rows = []
    for j, n in enumerate(lengths):
        rng = stream(args.seed, "rhat", 10 + j)
        x0 = np.tile(np.array(PFIZER_STARTS)[:, None], (reps, 1))
        d, _ = metropolis(logp_beta, x0, 0.008, 2 * n, rng)
        d = d[:, n:, 0].reshape(reps, CHAINS, n)
        for r in range(reps):
            x = d[r]
            rv = rhat_variants(x)
            ve = ve_of(x)
            q = float(np.quantile(ve, 0.025))
            rows.append({"n": n, "rank": rv["rank"], "split": rv["split"], "ess_bulk": ess_bulk(x), "ess_tail": ess_tail(x),
                         "err": q - ex["ve_q025"], "mcse": mcse_quantile(ve, 0.025)})
    rk = np.array([r["rank"] for r in rows])
    spl = np.array([r["split"] for r in rows])
    err = np.array([r["err"] for r in rows])
    se = np.array([r["mcse"] for r in rows])
    eb = np.array([r["ess_bulk"] for r in rows])
    et = np.array([r["ess_tail"] for r in rows])
    rules = {"split<1.1": spl < 1.1, "rank<1.1": rk < 1.1, "rank<1.01": rk < 1.01,
             "rank<1.01 & ESS>400": (rk < 1.01) & (eb > 400) & (et > 400)}
    thr = {}
    for name, ok in rules.items():
        if not ok.any():
            thr[name] = {"passed": 0}
            continue
        cover = float((np.abs(err[ok]) <= 1.96 * se[ok]).mean())
        thr[name] = {"passed": int(ok.sum()), "coverage": cover, "coverage_mcse": mcse_share(cover, int(ok.sum())),
                     "mean_err": float(err[ok].mean()), "rmse": float(np.sqrt((err[ok] ** 2).mean())),
                     "worst": float(np.abs(err[ok]).max()), "share_off_1pt": float((np.abs(err[ok]) > 0.01).mean())}
        t = thr[name]
        print(f"  {name}: {t['passed']} of {len(rows)} runs pass; the lower VE limit +- 1.96 MCSE contains the exact value in "
              f"{pc(cover)}% (+-{pc(t['coverage_mcse'])}); mean error {pc(t['mean_err'], 2)} points, RMSE "
              f"{pc(t['rmse'], 2)}, worst {pc(t['worst'], 2)}; off by more than 1 point {pc(t['share_off_1pt'])}%")
    out["threshold"] = {"reps": reps, "lengths": lengths, "step": 0.008, "rules": thr,
                        "points": [[r["n"], r["rank"], r["err"], r["mcse"], r["ess_bulk"], r["ess_tail"]] for r in rows]}
    return out


# ------------------------------------------------------------------------------- a bimodal posterior
def logp_mix(x):
    t = x[:, 0]
    return np.logaddexp(math.log(MIX_W) - 0.5 * t ** 2, math.log(1 - MIX_W) - 0.5 * (t - MIX_D) ** 2)


def stage_bimodal(cfg, args):
    exact_mean = (1 - MIX_W) * MIX_D
    exact_sd = math.sqrt(1 + MIX_W * (1 - MIX_W) * MIX_D ** 2)
    print(f"[bimodal] target {MIX_W:g} N(0, 1) + {1 - MIX_W:g} N({MIX_D:g}, 1), constructed: exact mean {exact_mean:g}, "
          f"SD {exact_sd:.4f}, P(theta > {MIX_D / 2:g}) = {1 - MIX_W:g}")
    n = cfg["warmup"] + cfg["draws"]
    runs = {"one_mode": (np.array([[-1.5], [-0.5], [0.5], [1.5]]), 2.4),
            "dispersed": (np.array([[-1.0], [1.0], [MIX_D - 1], [MIX_D + 1]]), 2.4),
            "long_jumps": (np.array([[-1.5], [-0.5], [0.5], [1.5]]), MIX_D)}
    out = {"exact": {"mean": exact_mean, "sd": exact_sd, "p_right": 1 - MIX_W}}
    for i, (name, (x0, step)) in enumerate(runs.items()):
        rng = stream(args.seed, "bimodal", i)
        d, a = metropolis(logp_mix, x0, step, n, rng)
        x = d[:, cfg["warmup"]:, 0]
        dg = summarize(x)
        p_right = float((x > MIX_D / 2).mean())
        chain_right = (x > MIX_D / 2).mean(axis=1)
        crossings = int((np.diff((d[:, :, 0] > MIX_D / 2).astype(int), axis=1) != 0).sum())
        se_p = math.sqrt(p_right * (1 - p_right) / max(ess_core(split((x > MIX_D / 2).astype(float))), 1)) if 0 < p_right < 1 else 0.0
        out[name] = {"start": x0[:, 0].tolist(), "step": step, "acceptance": a.tolist(), "diagnostics": dg,
                     "mean": float(x.mean()), "p_right": p_right, "p_right_mcse": se_p, "chain_share_right": chain_right.tolist(),
                     "crossings": crossings, "hist": hist(x, -4, 20, 96),
                     "rank_hist": [np.histogram(c, bins=20, range=(0, x.size))[0].tolist()
                                   for c in stats.rankdata(x).reshape(x.shape)]}
        print(f"  {name}: starts {x0[:, 0].tolist()}, step {step:g}; acceptance {', '.join(pc(v, 1) for v in a)}%; "
              f"R-hat {dg['rank']:.4f} (bulk {dg['bulk']:.4f}, folded {dg['folded']:.4f}); bulk ESS {dg['ess_bulk']:.1f}, "
              f"tail ESS {dg['ess_tail']:.1f}; mean {x.mean():.4f} (exact {exact_mean:g}); P(theta > {MIX_D / 2:g}) "
              f"{p_right:.4f} (exact {1 - MIX_W:g}); crossings {crossings}")
    # How deep must the valley be? Chains started in the larger mode with step 2.4, for several separations of the
    # same mixture: the share that ever reach the other mode within warmup + draws iterations.
    cross = {}
    for j, sep in enumerate((10.0, 12.0, 14.0, 16.0)):
        rng = stream(args.seed, "bimodal", 10 + j)
        lp = lambda x, sep=sep: np.logaddexp(math.log(MIX_W) - 0.5 * x[:, 0] ** 2,         # noqa: E731
                                             math.log(1 - MIX_W) - 0.5 * (x[:, 0] - sep) ** 2)
        d, _ = metropolis(lp, np.zeros((cfg["cross_chains"], 1)), 2.4, n, rng)
        share = float((d[:, :, 0] > sep / 2).any(axis=1).mean())
        cross[str(sep)] = {"share": share, "mcse": mcse_share(share, cfg["cross_chains"])}
    out["crossing"] = {"chains": cfg["cross_chains"], "iterations": n, "step": 2.4, "by_separation": cross}
    print(f"  chains started in the larger mode that ever reach the other ({cfg['cross_chains']} chains, {n} iterations, "
          f"step 2.4): " + ", ".join(f"separation {float(k):g}: {pc(v['share'])}%" for k, v in cross.items()))
    g = np.linspace(-4, 20, 481)
    out["density"] = {"x": g.tolist(), "p": (np.exp(logp_mix(g[:, None])) / math.sqrt(2 * math.pi)).tolist()}
    return out


# ------------------------------------------------------------------------------- NUTS in PyMC
def stage_nuts(cfg, args):
    import arviz_stats as azs
    import pymc as pm
    print(f"[nuts] the accidents model in PyMC {pm.__version__} with NUTS")
    y = np.repeat(Y_GY, W_GY)
    with pm.Model():
        mu = pm.LogNormal("mu", mu=0.0, sigma=PRIOR_SD)        # log mu ~ N(0, 2^2), as in the nb stage
        k = pm.LogNormal("k", mu=0.0, sigma=PRIOR_SD)
        pm.NegativeBinomial("y", mu=mu, alpha=k, observed=y)   # PyMC's alpha is the shape k: Var = mu + mu^2/alpha
        t0 = time.perf_counter()
        idata = pm.sample(draws=cfg["nuts_draws"], tune=cfg["nuts_tune"], chains=CHAINS, cores=1,
                          random_seed=args.seed, progressbar=False, compute_convergence_checks=True)
        wall = time.perf_counter() - t0
    post = idata["posterior"]
    ss = idata["sample_stats"]
    g = nb_grid()
    grid = {"mu": grid_marginal(g, 0)[0], "k": grid_marginal(g, 1)[0]}
    res = {"pymc": pm.__version__, "draws": cfg["nuts_draws"], "tune": cfg["nuts_tune"], "params": {}}
    for name in ("mu", "k"):
        x = np.asarray(post[name].values)
        mine = summarize(x)
        theirs = arviz_values(x)
        mine["ess_tail_11_89"] = min(ess_quantile(x, 0.11), ess_quantile(x, 0.89))
        theirs["ess_tail_default_xarray"] = arviz_default_tail(x)
        est = {"mean": (float(x.mean()), mcse_mean(x))}
        for qn, p in (("q025", 0.025), ("q500", 0.5), ("q975", 0.975)):
            est[qn] = (float(np.quantile(x, p)), mcse_quantile(x, p))
        z = {qn: (v - grid[name][qn]) / se for qn, (v, se) in est.items()}
        res["params"][name] = {"mine": mine, "arviz": theirs, "estimates": {qn: {"value": v, "mcse": se, "z": z[qn]}
                                                                          for qn, (v, se) in est.items()},
                               "ess_per_draw": mine["ess_bulk"] / x.size,
                               "rank_hist": [np.histogram(c, bins=20, range=(0, x.size))[0].tolist()
                                             for c in stats.rankdata(x).reshape(x.shape)]}
        print(f"  {name}: R-hat {mine['rank']:.4f}; bulk ESS {mine['ess_bulk']:.0f}, tail ESS {mine['ess_tail']:.0f}, "
              f"ESS(mean) {mine['ess_mean']:.0f} of {x.size}; " +
              "; ".join(f"{qn} {v:.5f} +- {se:.5f} vs grid {grid[name][qn]:.5f} (z {z[qn]:+.2f})" for qn, (v, se) in est.items()))
    div = int(np.asarray(ss["diverging"].values).sum()) if "diverging" in ss else int(np.asarray(ss["divergences"].values).sum())
    steps = np.asarray(ss["n_steps"].values) if "n_steps" in ss else 2 ** np.asarray(ss["tree_depth"].values) - 1
    depth = np.asarray(ss["tree_depth"].values)
    for name in ("mu", "k"):
        res["params"][name]["ess_per_leapfrog"] = res["params"][name]["mine"]["ess_bulk"] / steps.sum()
    res.update(divergences=div, mean_n_steps=float(steps.mean()), tree_depth_counts={str(int(v)): int((depth == v).sum())
                                                                                     for v in np.unique(depth)},
               step_size=float(np.asarray(ss["step_size"].values).mean()),
               sampling_seconds=float(post.attrs.get("sampling_time", float("nan"))), wall_seconds=wall,
               arviz_summary=str(azs.summary(idata, var_names=["mu", "k"])))
    zmax = max(abs(e["z"]) for p in res["params"].values() for e in p["estimates"].values())
    res["check"] = "PASS: every estimate within 3 MCSE of the grid" if zmax < 3 else "FAIL: an estimate is more than 3 MCSE off"
    print(f"  divergences {div}; mean leapfrog steps per draw {steps.mean():.2f}; tree depths {res['tree_depth_counts']}; "
          f"step size {res['step_size']:.3f}; sampling {res['sampling_seconds']:.1f} s; check: {res['check']}")
    print("  ArviZ summary:\n    " + res["arviz_summary"].replace("\n", "\n    "))
    return res


# ------------------------------------------------------------------------------- main
def provenance(args, budget):
    cpu = platform.processor() or platform.machine()
    try:
        for line in pathlib.Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    versions = {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}
    for mod in ("arviz_stats", "arviz_base", "pymc", "pytensor", "xarray"):
        try:
            versions[mod] = __import__(mod).__version__ if mod not in ("pymc", "pytensor") or args.stage in ("nuts", "all") \
                else "not loaded"
        except ImportError:
            versions[mod] = "not installed"
    return {"captured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "os": f"{platform.system()} {platform.release()} {platform.machine()}", "cpu": cpu, **versions,
            "mcmc_py_sha1": sha1(pathlib.Path(__file__)), "data_sha1": {GY_CSV.name: sha1(GY_CSV)}, "budget": budget,
            "seed": args.seed, "budget_values": QUICK if args.quick else FULL,
            "flags": {"fault": args.fault, "step": args.step}}


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("stage", choices=STAGES + ("all",))
    parser.add_argument("--quick", action="store_true", help="shorter chains and fewer replications")
    parser.add_argument("--out", default="captures.json", help="capture file to write (default captures.json)")
    parser.add_argument("--seed", type=int, default=20261127)
    parser.add_argument("--step", type=float, help="pfizer: your own proposal step (E3)")
    parser.add_argument("--fault", action="store_true", help="E4: an earlier draft of the pfizer stage's sampler")
    args = parser.parse_args()
    cfg = QUICK if args.quick else FULL
    budget = "quick" if args.quick else "full"
    prov = provenance(args, budget)
    print(f"Captured {prov['captured_utc']} on {prov['os']}, {prov['cpu']}; Python {prov['python']}, NumPy {prov['numpy']}, "
          f"SciPy {prov['scipy']}, arviz-stats {prov['arviz_stats']}, PyMC {prov['pymc']}, PyTensor {prov['pytensor']}; "
          f"mcmc.py {prov['mcmc_py_sha1']}; budget {budget}, seed {args.seed}.")
    out_path = pathlib.Path(args.out)
    captures = json.loads(out_path.read_text(encoding="utf-8")) if out_path.exists() else {}
    captures["provenance"] = prov
    timings = captures.setdefault("seconds", {})
    stages = STAGES if args.stage == "all" else (args.stage,)
    funcs = {"pfizer": stage_pfizer, "tuning": stage_tuning, "nb": stage_nb, "diagnostics": stage_diagnostics,
             "mcse": stage_mcse, "rhat": stage_rhat, "bimodal": stage_bimodal, "nuts": stage_nuts}
    for name in stages:
        t0 = time.perf_counter()
        print()
        captures[name] = r6(funcs[name](cfg, args))
        timings[name] = round(time.perf_counter() - t0, 1)
    out_path.write_text(json.dumps(captures, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {out_path.name}: " + ", ".join(f"{k} {v} s" for k, v in timings.items() if k in stages))


if __name__ == "__main__":
    main()
