#!/usr/bin/env python3
"""Lab for "Diffusion Samplers and Solvers" (Diffusion Models series, part 6).

One denoiser, many samplers. The denoiser here is never trained: it is the exact posterior mean
E[x0 | x] of part 5's "crescent world" (four bright crescents, a shared brightness offset, fine
per-pixel detail), so every error this lab measures belongs to the sampler alone.

  worked   the brightness direction as one Gaussian number: DDIM, DPM-Solver++(2M) and Heun step
           by step, computed exactly (closed form, no sampling)
  ode      global error of six deterministic samplers against the exact ODE solution, at matched
           NFE, on five step schedules (32x32 crescents, 256 shared starting points)
  local    the error one step makes, per noise level (EDM's Appendix D.1, repeated on the toy)
  sde      deterministic vs stochastic samplers at matched NFE, judged by sample statistics; and
           with part 5's flawed schedule, a start mismatch that only fresh noise can shrink
  samples  images and trajectories for the figures

Everything runs in the variance-exploding coordinates of DDIM and EDM: x = x0 + sigma * eps, with
sigma = sqrt((1 - abar) / abar). Every solver ends with the same last step from sigma_min to 0, which
returns the denoiser's answer.

Run:   python samplers.py all            # about 15 min on a laptop with 8 free cores
       python samplers.py all --quick    # about 70 s, fewer samples and NFE points
Writes captures.json beside this file and prints the same numbers.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")     # one BLAS thread per worker; the pool supplies the parallelism

import numpy as np

HERE = Path(__file__).resolve().parent
K = 4                                   # crescent orientations (mixture components)
A_C, S_B, TAU = 0.9, 0.3, 0.1           # crescent RMS amplitude, brightness spread, detail noise
SIGMA_MAX, SIGMA_MIN = 80.0, 0.002      # EDM's sampling range
GREY = 2.0 / 256                        # one 8-bit grey level of an image scaled to [-1, 1]


# --------------------------------------------------------------------------- crescent world
def crescent_shapes(r, supersample=8):
    """K zero-mean crescents on an r x r grid: a disc minus an offset disc, in four rotations."""
    g = (np.arange(r * supersample) + 0.5) / (r * supersample)
    yy, xx = np.meshgrid(g, g, indexing="ij")
    outer = (xx - 0.5) ** 2 + (yy - 0.5) ** 2 < 0.36 ** 2
    inner = (xx - 0.64) ** 2 + (yy - 0.42) ** 2 < 0.30 ** 2
    m = (outer & ~inner).astype(float)
    m = m.reshape(r, supersample, r, supersample).mean(axis=(1, 3))
    shapes = []
    for k in range(K):
        s = np.rot90(m, k).reshape(-1)
        s = s - s.mean()
        shapes.append(s * A_C / np.sqrt((s ** 2).mean()))
    return np.stack(shapes)                      # (K, n): zero mean, equal norms


class World:
    """x0 = mu_k + b*1 + tau*z: k uniform, b ~ N(0, s_b^2), z ~ N(0, I). A Gaussian mixture."""

    def __init__(self, r):
        self.r, self.n = r, r * r
        self.mu = crescent_shapes(r)
        self.v_e = S_B ** 2 * self.n + TAU ** 2  # data variance along the brightness axis 1/sqrt(n)

    def sample(self, rng, N):
        k = rng.integers(0, K, N)
        b = rng.normal(0.0, S_B, N)
        return self.mu[k] + b[:, None] + TAU * rng.normal(size=(N, self.n))

    def denoise(self, x, sigma):
        """Exact D(x; sigma) = E[x0 | x0 + sigma*eps = x], for x of shape (N, n)."""
        s2 = sigma * sigma
        p = x.mean(1, keepdims=True)                     # brightness part (1/n)(1.x) on every pixel
        logits = x @ self.mu.T / (TAU ** 2 + s2)         # norms are equal, so only x.mu_k matters
        logits -= logits.max(1, keepdims=True)
        w = np.exp(logits)
        w /= w.sum(1, keepdims=True)
        a_o = TAU ** 2 / (TAU ** 2 + s2)                 # shrink of detail, off the brightness axis
        a_e = self.v_e / (self.v_e + s2)                 # shrink of the brightness coordinate
        return (1.0 - a_o) * (w @ self.mu) + a_o * (x - p) + a_e * p


# --------------------------------------------------------------------------- step schedules
def vp_sigma(t, b_min=0.1, b_d=19.9):
    """sigma(t) of the continuous VP schedule (Song et al.; EDM Table 1)."""
    return np.sqrt(np.expm1(0.5 * b_d * t ** 2 + b_min * t))


def vp_t(sigma, b_min=0.1, b_d=19.9):
    """Inverse of vp_sigma."""
    c = np.log1p(sigma ** 2)
    return (-b_min + np.sqrt(b_min ** 2 + 2.0 * b_d * c)) / b_d


def schedule(name, N, smax=SIGMA_MAX, smin=SIGMA_MIN):
    """N positive noise levels from smax down to smin, then 0: N steps in all."""
    if N == 1:
        return np.array([smax, 0.0])
    i = np.arange(N) / (N - 1)
    if name.startswith("edm"):                           # Karras et al., eq. 5; edm7 = rho 7
        rho = float(name[3:])
        s = (smax ** (1 / rho) + i * (smin ** (1 / rho) - smax ** (1 / rho))) ** rho
    elif name == "uniform":                              # rho = 1: equal steps in sigma
        s = smax + i * (smin - smax)
    elif name == "logsnr":                               # equal steps in log-SNR (DPM-Solver)
        s = np.exp(np.log(smax) + i * (np.log(smin) - np.log(smax)))
    elif name == "vp_time":                              # equal steps in the VP SDE's time t
        s = vp_sigma(vp_t(smax) + i * (vp_t(smin) - vp_t(smax)))
    else:
        raise ValueError(name)
    return np.append(s, 0.0)


# ----------------------------------------------------------------------------- samplers
# Each sampler takes the denoiser D(x, sigma), the start x at sig[0], and the grid sig (ending in 0).
# It returns (x at sigma = 0, NFE). The last step, to sigma = 0, always returns D: every solver below
# reduces to Euler there, as EDM's Algorithm 1 and DPM-Solver++(2M) do.

def ddim(D, x, sig, rng=None):
    """DDIM (eta = 0) = Euler in sigma = DPM-Solver-1 = DPM-Solver++(1): exact if D is constant."""
    nfe = 0
    for s, s2 in zip(sig[:-1], sig[1:]):
        d = D(x, s)
        nfe += 1
        x = d + (s2 / s) * (x - d)
    return x, nfe


def euler_vp(D, x, sig, rng=None):
    """Euler steps in the VP time t on the VP probability-flow ODE (score SDE's ODE, naive variable)."""
    ts = vp_t(np.asarray(sig[:-1]))
    b_min, b_d = 0.1, 19.9
    ab = 1.0 / (1.0 + sig[0] ** 2)
    xv = math.sqrt(ab) * x                               # VP state
    nfe = 0
    for i in range(len(ts) - 1):
        t, t2 = ts[i], ts[i + 1]
        s = sig[i]
        ab = 1.0 / (1.0 + s * s)
        x0 = D(xv / math.sqrt(ab), s)
        nfe += 1
        score = (math.sqrt(ab) * x0 - xv) / (1.0 - ab)
        xv = xv + (t2 - t) * (-0.5 * (b_min + b_d * t) * (xv + score))
    s = sig[-2]
    x0 = D(xv * math.sqrt(1.0 + s * s), s)               # last step to sigma = 0
    return x0, nfe + 1


def heun(D, x, sig, rng=None):
    """EDM Algorithm 1: Euler predictor, trapezoidal corrector; Euler on the last step to 0."""
    nfe = 0
    for s, s2 in zip(sig[:-1], sig[1:]):
        d1 = (x - D(x, s)) / s
        nfe += 1
        xe = x + (s2 - s) * d1
        if s2 == 0:
            x = xe
            continue
        d2 = (xe - D(xe, s2)) / s2
        nfe += 1
        x = x + (s2 - s) * 0.5 * (d1 + d2)
    return x, nfe


def dpm2(D, x, sig, rng=None):
    """DPM-Solver-2 (Lu et al., Algorithm 1), noise form: a midpoint step in log-SNR."""
    nfe = 0
    for s, s2 in zip(sig[:-1], sig[1:]):
        e0 = (x - D(x, s)) / s                           # the noise estimate, eps-hat
        nfe += 1
        if s2 == 0:
            x = x - s * e0
            continue
        sm = math.sqrt(s * s2)                           # half-way in log-SNR
        u = x + (sm - s) * e0
        em = (u - D(u, sm)) / sm
        nfe += 1
        x = x + (s2 - s) * em
    return x, nfe


def dpm3(D, x, sig, rng=None):
    """DPM-Solver-3 (Lu et al., Algorithm 2) with r1 = 1/3, r2 = 2/3, noise form."""
    r1, r2 = 1.0 / 3.0, 2.0 / 3.0
    nfe = 0
    for s, s2 in zip(sig[:-1], sig[1:]):
        e0 = (x - D(x, s)) / s
        nfe += 1
        if s2 == 0:
            x = x - s * e0
            continue
        h = math.log(s / s2)                             # step in half-log-SNR, lambda = -log sigma
        sa, sb = s * math.exp(-r1 * h), s * math.exp(-r2 * h)
        u1 = x - sa * math.expm1(r1 * h) * e0
        d1 = (u1 - D(u1, sa)) / sa - e0
        u2 = (x - sb * math.expm1(r2 * h) * e0
              - (sb * r2 / r1) * (math.expm1(r2 * h) / (r2 * h) - 1.0) * d1)
        d2 = (u2 - D(u2, sb)) / sb - e0
        nfe += 2
        x = x - s2 * math.expm1(h) * e0 - (s2 / r2) * (math.expm1(h) / h - 1.0) * d2
    return x, nfe


def dpmpp2m(D, x, sig, rng=None):
    """DPM-Solver++(2M) (Lu et al. 2025, Algorithm 2), in k-diffusion's form: data prediction,
    second order by reusing the previous step's denoiser output, so one NFE per step."""
    nfe, old, h_last = 0, None, None
    for s, s2 in zip(sig[:-1], sig[1:]):
        d = D(x, s)
        nfe += 1
        if s2 == 0:
            x = d
            continue
        h = math.log(s / s2)
        if old is None:
            dd = d
        else:
            r = h_last / h
            dd = (1.0 + 1.0 / (2.0 * r)) * d - (1.0 / (2.0 * r)) * old
        x = (s2 / s) * x + (1.0 - s2 / s) * dd
        old, h_last = d, h
    return x, nfe


def ancestral(D, x, sig, rng):
    """DDPM ancestral sampling on the subsequence (DDIM eta = 1, k-diffusion's 'Euler a'): a step
    down to sigma_down, then fresh noise sigma_up, so the sample lands at sigma' again."""
    nfe = 0
    for s, s2 in zip(sig[:-1], sig[1:]):
        d = D(x, s)
        nfe += 1
        if s2 == 0:
            x = d
            continue
        s_up = math.sqrt(s2 * s2 * (s * s - s2 * s2) / (s * s))
        s_down = math.sqrt(s2 * s2 - s_up * s_up)
        x = d + (s_down / s) * (x - d) + s_up * rng.normal(size=x.shape)
    return x, nfe


def edm_sde(D, x, sig, rng, s_churn=40.0, s_tmin=0.05, s_tmax=50.0, s_noise=1.0):
    """EDM Algorithm 2: raise the noise by gamma, then one Heun step down (ImageNet-64 'our model'
    settings from EDM Table 5, with S_noise = 1 because this denoiser is exact)."""
    N = len(sig) - 1
    nfe = 0
    for s, s2 in zip(sig[:-1], sig[1:]):
        g = min(s_churn / N, math.sqrt(2.0) - 1.0) if s_tmin <= s <= s_tmax else 0.0
        sh = s * (1.0 + g)
        if g > 0:
            x = x + math.sqrt(sh * sh - s * s) * s_noise * rng.normal(size=x.shape)
        d1 = (x - D(x, sh)) / sh
        nfe += 1
        xe = x + (s2 - sh) * d1
        if s2 == 0:
            x = xe
            continue
        d2 = (xe - D(xe, s2)) / s2
        nfe += 1
        x = x + (s2 - sh) * 0.5 * (d1 + d2)
    return x, nfe


SAMPLERS = {"ddim": ddim, "euler_vp": euler_vp, "heun": heun, "dpm2": dpm2, "dpm3": dpm3,
            "dpmpp2m": dpmpp2m, "ancestral": ancestral, "edm_sde": edm_sde}
NFE_PER_STEP = {"ddim": 1, "euler_vp": 1, "dpmpp2m": 1, "ancestral": 1, "heun": 2, "dpm2": 2,
                "edm_sde": 2, "dpm3": 3}


def steps_for(sampler, nfe_targets):
    """Step counts N whose NFE (N, 2N - 1 or 3N - 2) lands nearest each target, deduplicated."""
    k = NFE_PER_STEP[sampler]
    out = []
    for t in nfe_targets:
        N = max(1, round((t - 1) / k) + 1) if k > 1 else t
        if N not in out:
            out.append(N)
    return out


# --------------------------------------------------------------------------- reference ODE
def rk4_log_sigma(D, x, s_from, s_to, steps):
    """RK4 on dx/du = x - D(x, e^u), u = log sigma: the exact ODE to about 1e-10 at these step counts."""
    u0, u1 = math.log(s_from), math.log(s_to)
    h = (u1 - u0) / steps
    f = lambda xx, u: xx - D(xx, math.exp(u))
    u = u0
    for _ in range(steps):
        k1 = f(x, u)
        k2 = f(x + 0.5 * h * k1, u + 0.5 * h)
        k3 = f(x + 0.5 * h * k2, u + 0.5 * h)
        k4 = f(x + h * k3, u + h)
        x = x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        u += h
    return x


def reference_path(D, x, sig, per_unit=400):
    """Exact ODE states at every positive sigma of the grid, from x at sig[0]: RK4 with about
    per_unit steps per unit of log sigma between consecutive points."""
    states = [x]
    for s, s2 in zip(sig[:-2], sig[1:-1]):
        n = max(4, int(math.ceil(math.log(s / s2) * per_unit)))
        x = rk4_log_sigma(D, x, s, s2, n)
        states.append(x)
    return states


def rms(a):
    return float(np.sqrt(np.mean(a * a)))


def nfe_staying_below(rows, key, tol):
    """The smallest NFE from which every larger NFE in the sweep keeps rows[key] below tol (None if
    the sweep never settles). A first crossing would mislead when a curve is not monotone."""
    best = None
    for r in sorted(rows, key=lambda x: x["nfe"], reverse=True):
        if r[key] is None or not r[key] < tol:
            break
        best = r["nfe"]
    return best


def nfe_at_error(rows, tol):
    """NFE at which |1 - kept| falls to tol for good, interpolated on log-log axes between sweep points."""
    pts = sorted((r["nfe"], abs(1.0 - r["kept"])) for r in rows)
    last = None
    for i in range(len(pts) - 1, 0, -1):          # walk back from the largest NFE while still below tol
        if pts[i - 1][1] >= tol > pts[i][1]:
            last = i
            break
        if pts[i - 1][1] >= tol:
            break
    if last is None:
        return None
    (n0, e0), (n1, e1) = pts[last - 1], pts[last]
    slope = (math.log(e1) - math.log(e0)) / (math.log(n1) - math.log(n0))
    return math.exp(math.log(n0) + (math.log(tol) - math.log(e0)) / slope)


# ------------------------------------------------------------------------------- worked
def sd_schedules(T=1000):
    """Stable Diffusion's scaled-linear abar and Lin et al.'s zero-terminal-SNR rescale (part 5)."""
    sl = np.cumprod(1.0 - np.linspace(0.00085 ** 0.5, 0.012 ** 0.5, T) ** 2)
    r = np.sqrt(sl)
    zs = ((r - r[-1]) * r[0] / (r[0] - r[-1])) ** 2
    return sl, zs


def trailing(S, T=1000):
    return np.round(np.arange(T, 0, -T / S)).astype(int) - 1


def sigma_of(ab):
    return math.sqrt((1.0 - ab) / ab) if ab > 0 else math.inf


def gaussian_1d(sampler, sig, v0, start_var, trace=False):
    """A sampler on one Gaussian direction (data variance v0) is a linear map plus added noise, so
    its output variance follows a two-number recursion. Returns (output std / data std, NFE), and
    with trace=True also [(sigma, kept)] after every step of a deterministic sampler, where kept is
    the state over the exact ODE solution from the same start, at that sigma.

    sig[0] may be inf (zero terminal SNR): at sigma = inf the denoiser returns the data mean, 0, and
    the first step lands at sig[1] * eps, as every x0-form solver does; start_var is then ignored.
    """
    D = lambda s: v0 / (v0 + s * s)                      # D(x; s) = D(s) * x on this direction
    a, var, nfe, i0 = 1.0, 0.0, 0, 0                     # x = a * x_start + noise of variance var
    if math.isinf(sig[0]):                               # first step from pure noise, eps of variance 1
        a, nfe, i0, start_var = sig[1], 1, 1, 1.0
        exact = lambda s: math.sqrt(v0 + s * s)          # the exact path for eps = 1
    else:
        exact = lambda s: math.sqrt((v0 + s * s) / (v0 + sig[0] ** 2))
    path = [(sig[1], a / exact(sig[1]))] if i0 == 1 else []
    old = h_last = a_prev = None
    for s, s2 in zip(sig[i0:-1], sig[i0 + 1:]):
        d = D(s)
        nfe += 1
        if sampler == "ddim":
            a *= d + (s2 / s) * (1 - d)                  # s2 = 0 leaves a * d
        elif sampler == "ancestral":
            if s2 == 0:
                a, var = a * d, var * d * d
            else:
                s_up2 = s2 * s2 * (s * s - s2 * s2) / (s * s)
                f = d + (math.sqrt(s2 * s2 - s_up2) / s) * (1 - d)
                a, var = a * f, var * f * f + s_up2
        elif sampler == "dpmpp2m":
            if s2 == 0:
                a *= d
            else:
                h = math.log(s / s2)
                dd = d * a                               # D(x_i) as a multiple of x_start
                if old is not None:
                    r = h_last / h
                    dd = (1 + 1 / (2 * r)) * d * a - (1 / (2 * r)) * old * a_prev
                old, h_last, a_prev = d, h, a
                a = (s2 / s) * a + (1 - s2 / s) * dd
        elif sampler == "heun":
            d1 = (1 - d) / s
            fe = 1 + (s2 - s) * d1                       # Euler predictor, as a factor
            if s2 == 0:
                a *= fe
            else:
                nfe += 1
                d2 = fe * (1 - D(s2)) / s2
                a *= 1 + (s2 - s) * 0.5 * (d1 + d2)
        else:
            raise ValueError(sampler)
        if trace and sampler != "ancestral":
            path.append((s2, a / exact(s2)))
    kept = math.sqrt((a * a * start_var + var) / v0)
    return (kept, nfe, path) if trace else (kept, nfe)


def run_worked():
    n = 128 * 128
    v0 = n * S_B ** 2 + TAU ** 2
    sl, zs = sd_schedules()
    res = {"n": n, "v0": v0, "sqrt_v0": math.sqrt(v0)}
    # The fixed (zero-terminal-SNR) schedule, trailing spacing: part 5's 0.851 at 50 DDIM steps.
    idx = trailing(50)
    sig = [sigma_of(zs[t]) for t in idx] + [0.0]
    res["trailing50_sigmas"] = [None if math.isinf(s) else s for s in sig]
    first = []
    for i in range(1, 7):
        s, s2 = sig[i], sig[i + 1]
        f_ddim = (v0 + s * s2) / (v0 + s * s)
        f_exact = math.sqrt((v0 + s2 * s2) / (v0 + s * s))
        first.append({"step": i + 1, "sigma": s, "sigma_next": s2, "ddim": f_ddim, "exact": f_exact})
    res["first_steps"] = first
    res["first_step_kept"] = sig[1] / math.sqrt(v0 + sig[1] ** 2)
    # Where the spread is lost, step by step: part 5's grid, and log-SNR spacing for DDIM and 2M.
    sigma_lo = sigma_of(zs[0])                           # the schedule's least noisy level
    log50 = list(schedule("logsnr", 50, smax=4096.0, smin=sigma_lo))
    res["paths"] = {"ddim/trailing": gaussian_1d("ddim", sig, v0, 1.0, trace=True)[2],
                    "ddim/logsnr": gaussian_1d("ddim", log50, v0, 1.0 + 4096.0 ** 2, trace=True)[2],
                    "dpmpp2m/logsnr": gaussian_1d("dpmpp2m", log50, v0, 1.0 + 4096.0 ** 2, trace=True)[2]}
    # Convergence on the same problem: solver x spacing, NFE sweep.
    sweeps = {}
    for St in (10, 13, 17, 20, 25, 34, 50, 67, 100, 134, 200, 400, 1000):
        idx = trailing(St)
        sg = [sigma_of(zs[t]) for t in idx] + [0.0]
        for smp in ("ddim", "dpmpp2m"):
            v, nf = gaussian_1d(smp, sg, v0, 1.0)
            sweeps.setdefault(f"{smp}/trailing", []).append({"steps": St, "nfe": nf, "kept": v})
        sgh = [4096.0 if math.isinf(s) else s for s in sg]          # diffusers' 2^-24 patch
        if St % 2 == 0 or St == 25:
            v, nf = gaussian_1d("heun", sgh, v0, 1.0 + 4096.0 ** 2)
            sweeps.setdefault("heun/trailing4096", []).append({"steps": St, "nfe": nf, "kept": v})
        for name in ("logsnr", "edm7"):
            sg2 = list(schedule(name, St, smax=4096.0, smin=sigma_lo))
            for smp in ("ddim", "dpmpp2m", "heun"):
                if smp == "heun":
                    N = max(2, (St + 1) // 2)
                    sg3 = list(schedule(name, N, smax=4096.0, smin=sigma_lo))
                    v, nf = gaussian_1d("heun", sg3, v0, 1.0 + 4096.0 ** 2)
                else:
                    v, nf = gaussian_1d(smp, sg2, v0, 1.0 + 4096.0 ** 2)
                sweeps.setdefault(f"{smp}/{name}", []).append({"steps": St, "nfe": nf, "kept": v})
    res["sweeps"] = sweeps
    res["nfe_to_1pct"] = {k: nfe_at_error(rows, 0.01) for k, rows in sweeps.items()}
    # Part 5's flawed schedule: the start mismatch that no number of ODE steps removes.
    abar_T = float(sl[-1])
    sT = sigma_of(abar_T)
    res["flawed"] = {"abar_T": abar_T, "sigma_T": sT,
                     "ode_limit": 1.0 / math.sqrt(abar_T * v0 + 1.0 - abar_T),
                     "sde_limit": math.sqrt((v0 / (v0 + sT * sT)) ** 2 / abar_T + v0 * sT * sT / (v0 + sT * sT)) / math.sqrt(v0),
                     "rows": []}
    for St in (25, 50, 100, 200, 500, 1000):
        idx = trailing(St)
        sg = [sigma_of(sl[t]) for t in idx] + [0.0]
        row = {"steps": St}
        for smp in ("ddim", "ancestral", "dpmpp2m"):
            row[smp] = gaussian_1d(smp, sg, v0, 1.0 / abar_T)[0]
        sgz = [sigma_of(zs[t]) for t in idx] + [0.0]
        row["ancestral_zero_snr"] = gaussian_1d("ancestral", sgz, v0, 1.0)[0]
        row["ddim_zero_snr"] = gaussian_1d("ddim", sgz, v0, 1.0)[0]
        res["flawed"]["rows"].append(row)
    print(f"  worked: sqrt(V0)={math.sqrt(v0):.2f}; first DDIM step keeps {res['first_step_kept']:.4f}; "
          f"50 trailing DDIM steps keep {sweeps['ddim/trailing'][6]['kept']:.4f}")
    for k, rows in sweeps.items():
        n1 = res["nfe_to_1pct"][k]
        print(f"  worked {k:18s} 1% at NFE {'-' if n1 is None else f'{n1:.0f}':>4s} | "
              + " ".join(f"{r['nfe']}:{r['kept']:.4f}" for r in rows))
    for k, pth in res["paths"].items():
        print(f"  worked path {k:15s} " + " ".join(f"{sg:.3g}:{v:.4f}" for sg, v in pth[:8]) + f" ... end {pth[-1][1]:.4f}")
    fl = res["flawed"]
    print(f"  flawed schedule: ODE limit {fl['ode_limit']:.4f}, reverse-SDE limit {fl['sde_limit']:.4f}")
    for r in fl["rows"]:
        print(f"  flawed steps={r['steps']:4d} ddim={r['ddim']:.4f} ancestral={r['ancestral']:.4f} "
              f"dpmpp2m={r['dpmpp2m']:.4f} | zero-SNR ddim={r['ddim_zero_snr']:.4f} ancestral={r['ancestral_zero_snr']:.4f}")
    return res


def _measured_job(args):
    name, St, smp, N, chunk = args
    w = World(128)
    sl, zs = sd_schedules()
    ab = zs if name == "zero_snr" else sl
    idx = trailing(St)
    sig = [sigma_of(ab[t]) for t in idx] + [0.0]
    means, nfe = [], 0
    for c0 in range(0, N, chunk):                         # chunks keep memory near 0.5 GB per worker
        eps = np.random.default_rng(7 + 128 + c0).normal(size=(min(chunk, N - c0), w.n))
        if math.isinf(sig[0]):                            # zero SNR: the first x0-form step lands at sig[1]*eps
            x, sig_run, extra = sig[1] * eps, sig[1:], 1
        else:
            x, sig_run, extra = eps / math.sqrt(ab[idx[0]]), sig, 0
        g, nfe = SAMPLERS[smp](w.denoise, x, np.array(sig_run), np.random.default_rng(11 + c0))
        nfe += extra
        means.append(g.mean(1))
    m = np.concatenate(means)
    return {"schedule": name, "steps": St, "sampler": smp, "nfe": nfe, "N": N,
            "kept": float(m.std() / math.sqrt(S_B ** 2 + TAU ** 2 / w.n)),
            "kept_se": float(m.std() / math.sqrt(S_B ** 2 + TAU ** 2 / w.n) / math.sqrt(2 * N))}


def run_worked_measured(quick, workers):
    """Measure three of the worked numbers with the full 16,384-pixel exact denoiser (part 5's setup)."""
    N = 400 if quick else 2000
    jobs = [("zero_snr", 50, "ddim", N, 500), ("zero_snr", 50, "dpmpp2m", N, 500), ("flawed", 200, "ancestral", N, 500)]
    rows = []
    with ProcessPoolExecutor(max_workers=min(workers, 3)) as ex:
        for row in ex.map(_measured_job, jobs):
            rows.append(row)
            print(f"  worked measured: {row['schedule']:9s} {row['sampler']:9s} steps={row['steps']:3d} "
                  f"kept={row['kept']:.4f} +- {row['kept_se']:.4f} (N={N})", flush=True)
    return {"N": N, "rows": rows}


# ------------------------------------------------------------------------------------ ode
ODE_SAMPLERS = ("ddim", "heun", "dpm2", "dpm3", "dpmpp2m")
SCHEDULES = ("edm7", "edm3", "logsnr", "vp_time", "uniform")


def _ode_job(args):
    sampler, sched, Ns, r, n_samples, seed = args
    w = World(r)
    rng = np.random.default_rng(seed)
    x_start = SIGMA_MAX * rng.normal(size=(n_samples, w.n))
    ref = np.load(_ref_path(r, n_samples, seed))
    rows = []
    for N in Ns:
        sig = schedule(sched, N)
        out, nfe = SAMPLERS[sampler](w.denoise, x_start.copy(), sig)
        rows.append({"steps": N, "nfe": nfe, "rms": rms(out - ref)})
    return sampler, sched, rows


def _ref_path(r, n_samples, seed):
    return HERE / ".cache" / f"ref-r{r}-n{n_samples}-s{seed}-{_SRC}.npy"


def make_reference(r, n_samples, seed, steps):
    """The exact ODE endpoint for the shared starting points, checked against twice the steps."""
    path = _ref_path(r, n_samples, seed)
    w = World(r)
    rng = np.random.default_rng(seed)
    x_start = SIGMA_MAX * rng.normal(size=(n_samples, w.n))
    if path.exists():
        return float(json.loads(path.with_suffix(".json").read_text())["self_check_rms"])
    a = rk4_log_sigma(w.denoise, x_start.copy(), SIGMA_MAX, SIGMA_MIN, steps)
    b = rk4_log_sigma(w.denoise, x_start.copy(), SIGMA_MAX, SIGMA_MIN, 2 * steps)
    a, b = w.denoise(a, SIGMA_MIN), w.denoise(b, SIGMA_MIN)
    check = rms(a - b)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.save(path, b)
    path.with_suffix(".json").write_text(json.dumps({"self_check_rms": check}))
    return check


def run_ode(quick, workers):
    r, n_samples, seed = 32, (64 if quick else 256), 2026
    check = make_reference(r, n_samples, seed, 600 if quick else 2000)
    print(f"  ode: reference RK4 self-check rms {check:.2e}", flush=True)
    targets = ((1, 2, 3, 5, 8, 12, 20, 32, 50, 100, 200) if quick else
               (1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50, 64, 80, 100, 128, 160, 200, 256, 320, 400,
                512, 640, 800, 1000))
    jobs = []
    for sched in SCHEDULES:
        for smp in ODE_SAMPLERS:
            jobs.append((smp, sched, steps_for(smp, targets), r, n_samples, seed))
    jobs.append(("euler_vp", "vp_time", steps_for("euler_vp", targets), r, n_samples, seed))
    res = {"r": r, "samples": n_samples, "seed": seed, "reference_self_check_rms": check, "grey": GREY,
           "curves": {}, "nfe_to_grey": {}}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for smp, sched, rows in ex.map(_ode_job, jobs):
            key = f"{smp}/{sched}"
            res["curves"][key] = rows
            res["nfe_to_grey"][key] = nfe_staying_below(rows, "rms", GREY)
            print(f"  ode {smp:8s} {sched:8s} below one grey level from NFE {res['nfe_to_grey'][key]}; "
                  + " ".join(f"{x['nfe']}:{x['rms']:.1e}" for x in rows[::4]), flush=True)
    return res


# ---------------------------------------------------------------------------------- local
def run_local(quick):
    """Error of one step started on the exact path, per noise level, N = 32 (EDM Appendix D.1)."""
    r, n_samples, N = 32, (32 if quick else 128), 32
    w = World(r)
    x_start = SIGMA_MAX * np.random.default_rng(99).normal(size=(n_samples, w.n))
    res = {"N": N, "samples": n_samples, "grids": {}}
    for sched in ("uniform", "edm3", "edm7", "logsnr"):
        sig = schedule(sched, N)
        path = reference_path(w.denoise, x_start.copy(), sig, per_unit=150 if quick else 400)
        rows = []
        for i in range(len(path) - 1):
            s, s2, xs = sig[i], sig[i + 1], path[i]
            row = {"sigma_from": float(s), "sigma_to": float(s2)}
            for smp in ("ddim", "heun"):
                y, _ = SAMPLERS[smp](w.denoise, xs.copy(), np.array([s, s2]))   # one step, s to s2
                row[smp] = rms(y - path[i + 1])
            rows.append(row)
        res["grids"][sched] = rows
        print(f"  local {sched:8s} max ddim {max(x['ddim'] for x in rows):.2e} at sigma "
              f"{max(rows, key=lambda x: x['ddim'])['sigma_to']:.3g}; heun range "
              f"{min(x['heun'] for x in rows):.1e}..{max(x['heun'] for x in rows):.1e}", flush=True)
    return res


# ------------------------------------------------------------------------------------ sde
def sample_stats(w, g):
    """Brightness spread, blur between crescents and detail level, each against the data's own."""
    bright = g.mean(1)
    resid = g - bright[:, None]
    k = np.argmax(resid @ w.mu.T, 1)
    rr = resid - w.mu[k]
    q, _ = np.linalg.qr(w.mu.T)                          # orthonormal basis of the crescent span
    in_span = rr @ q
    shape = float((in_span ** 2).sum(1).mean() / w.n)    # blur: error inside the crescent span
    detail = float(((rr ** 2).sum(1) - (in_span ** 2).sum(1)).mean() / (w.n - K - 1) / TAU ** 2)
    return {"spread": float(bright.std() / math.sqrt(S_B ** 2 + TAU ** 2 / w.n)), "shape": shape,
            "detail": detail}


def _sde_job(args):
    sampler, Ns, r, n_samples, seed = args
    w = World(r)
    rng = np.random.default_rng(seed)
    x_start = SIGMA_MAX * rng.normal(size=(n_samples, w.n))
    rows = []
    for N in Ns:
        out, nfe = SAMPLERS[sampler](w.denoise, x_start.copy(), schedule("edm7", N), np.random.default_rng(seed + N))
        rows.append({"steps": N, "nfe": nfe, **sample_stats(w, out)})
    return sampler, rows


def run_sde(quick, workers):
    r, n_samples, seed = 32, (512 if quick else 2048), 4242
    w = World(r)
    targets = (3, 5, 8, 12, 20, 32, 50, 100) if quick else (3, 4, 5, 6, 8, 10, 12, 16, 20, 25, 32, 40, 50, 64, 100,
                                                             128, 200, 256, 400, 512)
    jobs = [(smp, steps_for(smp, targets), r, n_samples, seed) for smp in ("ddim", "heun", "dpmpp2m", "ancestral", "edm_sde")]
    res = {"r": r, "samples": n_samples, "schedule": "edm7", "curves": {}}
    # floor: what an exact sampler scores, i.e. fresh data measured the same way
    res["floor"] = sample_stats(w, w.sample(np.random.default_rng(32), n_samples))
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for smp, rows in ex.map(_sde_job, jobs):
            res["curves"][smp] = rows
            print(f"  sde {smp:9s} detail " + " ".join(f"{x['nfe']}:{x['detail']:.3f}" for x in rows[::3]), flush=True)
    f = res["floor"]
    print(f"  sde floor (fresh data): shape={f['shape']:.1e} detail={f['detail']:.3f} spread={f['spread']:.3f}")
    return res


# -------------------------------------------------------------------------------- samples
def run_samples():
    """Six starting points through four samplers at three budgets, the exact ODE, and paths."""
    w = World(32)
    rng = np.random.default_rng(606)
    x_start = SIGMA_MAX * rng.normal(size=(6, w.n))
    ref = rk4_log_sigma(w.denoise, x_start.copy(), SIGMA_MAX, SIGMA_MIN, 2000)
    out = {"exact": np.round(w.denoise(ref, SIGMA_MIN), 3).tolist(), "grid": {}}
    for smp in ("ddim", "heun", "dpmpp2m", "ancestral"):
        for nfe in (5, 10, 20):
            N = steps_for(smp, (nfe,))[0]
            g, real = SAMPLERS[smp](w.denoise, x_start.copy(), schedule("edm7", N), np.random.default_rng(1))
            out["grid"][f"{smp}/{nfe}"] = {"nfe": real, "images": np.round(g, 3).tolist()}
    # trajectories: brightness and a crescent coordinate, exact (dense) and DDIM at 6 steps
    e_q = (w.mu[0] - w.mu[2]) / np.linalg.norm(w.mu[0] - w.mu[2])
    coords = lambda x: (x.mean(1) * math.sqrt(w.n), x @ e_q)
    dense = np.exp(np.linspace(math.log(SIGMA_MAX), math.log(SIGMA_MIN), 241))
    x = x_start.copy()
    path = [coords(x)]
    for s, s2 in zip(dense[:-1], dense[1:]):
        x = rk4_log_sigma(w.denoise, x, s, s2, 10)
        path.append(coords(x))
    sig6 = schedule("edm7", 6)
    x = x_start.copy()
    poly = [coords(x)]
    for s, s2 in zip(sig6[:-1], sig6[1:]):
        x, _ = ddim(w.denoise, x, np.array([s, s2]))
        poly.append(coords(x))
    out["paths"] = {"sigma": dense.tolist(), "brightness": [p[0].tolist() for p in path],
                    "crescent": [p[1].tolist() for p in path], "ddim6_sigma": sig6.tolist(),
                    "ddim6_brightness": [p[0].tolist() for p in poly], "ddim6_crescent": [p[1].tolist() for p in poly]}
    # where the crescent decision happens: posterior entropy of the component along the exact paths
    ent = []
    for s in (100, 60, 40, 30, 20, 10, 5, 2, 1):
        xs = w.sample(np.random.default_rng(3), 2000) + s * np.random.default_rng(4).normal(size=(2000, w.n))
        lg = xs @ w.mu.T / (TAU ** 2 + s * s)
        lg -= lg.max(1, keepdims=True)
        p = np.exp(lg)
        p /= p.sum(1, keepdims=True)
        ent.append({"sigma": s, "entropy_bits": float(-(p * np.log2(np.clip(p, 1e-300, 1))).sum(1).mean())})
    out["decision_entropy"] = ent
    print("  samples: decision entropy " + " ".join(f"{e['sigma']}:{e['entropy_bits']:.2f}" for e in ent))
    return out


# ------------------------------------------------------------------------------------ main
_SRC = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]   # caches are keyed to this file


def provenance():
    cpu = platform.processor() or platform.machine()
    try:
        with open("/proc/cpuinfo") as fh:
            for line in fh:
                if line.startswith("model name"):
                    cpu = line.split(":", 1)[1].strip()
                    break
    except OSError:
        pass
    return {"captured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "os": platform.platform(),
            "cpu": cpu, "cores": os.cpu_count(), "python": sys.version.split()[0], "numpy": np.__version__}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["worked", "ode", "local", "sde", "samples", "all"])
    ap.add_argument("--quick", action="store_true", help="fewer samples and NFE points, about 2 minutes")
    ap.add_argument("--workers", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--out", default=str(HERE / "captures.json"))
    args = ap.parse_args()
    prov = provenance()
    print(f"Captured {prov['captured_utc']} on {prov['cpu']} ({prov['cores']} cores), {prov['os']}, "
          f"Python {prov['python']}, numpy {prov['numpy']}" + (" [quick]" if args.quick else ""))
    out_path = Path(args.out)
    cap = json.loads(out_path.read_text()) if out_path.exists() and args.what != "all" else {}
    cap["provenance"] = {**prov, "quick": args.quick, "source_sha1": _SRC}
    t0 = time.time()

    def timed(name, fn):
        t = time.time()
        out = fn()
        print(f"  [{name} took {time.time() - t:.0f} s]", flush=True)
        return out
    if args.what in ("worked", "all"):
        cap["worked"] = timed("worked", run_worked)
        cap["worked_measured"] = timed("worked, 16,384-pixel check", lambda: run_worked_measured(args.quick, args.workers))
    if args.what in ("ode", "all"):
        cap["ode"] = timed("ode", lambda: run_ode(args.quick, args.workers))
    if args.what in ("local", "all"):
        cap["local"] = timed("local", lambda: run_local(args.quick))
    if args.what in ("sde", "all"):
        cap["sde"] = timed("sde", lambda: run_sde(args.quick, args.workers))
    if args.what in ("samples", "all"):
        cap["samples"] = timed("samples", run_samples)
    out_path.write_text(json.dumps(cap, indent=1))
    print(f"wrote {os.path.relpath(out_path)} in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
