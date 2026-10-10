#!/usr/bin/env python3
"""Lab for "Training a Diffusion Model" (Diffusion Models series, part 5).

Every decision fixed before the first gradient step, measured on a toy whose ideal denoiser
is known exactly, so each error can be compared with the best any network could do.

The toy is "crescent world": r x r images, each one of four bright crescents (the series'
motif) on a dark field, plus a brightness offset b ~ N(0, 0.3^2) shared by every pixel, plus
small per-pixel detail N(0, 0.1^2). It is a Gaussian mixture, so E[x0 | x_t] has a closed form.

  schedules  closed-form schedule numbers: terminal SNR, the first sampling step, the rescale
  leak       the terminal-SNR leak with the exact denoiser, at 16 to 16,384 pixels (numpy)
  train      small MLP denoisers on 8x8 crescents: weighting, target, EMA, width (CPU torch)

Run:   python training_decisions.py all            # about 45 min on 12 cores
       python training_decisions.py all --quick    # about 6 min on 12 cores, smaller and noisier
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
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
T = 1000              # discrete training timesteps, as in DDPM, iDDPM and Stable Diffusion
S = 50                # sampling steps for every sampler in this lab
K = 4                 # crescent orientations (mixture components)
A_C, S_B, TAU = 0.9, 0.3, 0.1   # crescent RMS amplitude, brightness spread, detail noise


# ----------------------------------------------------------------------------- schedules
def abar_linear():
    """DDPM: beta rises linearly from 1e-4 to 0.02."""
    return np.cumprod(1.0 - np.linspace(1e-4, 0.02, T))


def abar_scaled_linear():
    """Stable Diffusion: sqrt(beta) rises linearly from sqrt(0.00085) to sqrt(0.012)."""
    return np.cumprod(1.0 - np.linspace(0.00085 ** 0.5, 0.012 ** 0.5, T) ** 2)


def abar_cosine(s=0.008, clip=0.999):
    """iDDPM cosine schedule; beta is clipped at 0.999, which keeps the last SNR above zero."""
    t = np.arange(T + 1) / T
    f = np.cos((t + s) / (1 + s) * np.pi / 2) ** 2
    beta = np.minimum(1.0 - f[1:] / f[:-1], clip)
    return np.cumprod(1.0 - beta)


def rescale_zero_terminal_snr(abar):
    """Lin et al. Algorithm 1: in sqrt(abar) space keep the first value, move the last to 0."""
    r = np.sqrt(abar)
    r0, rT = r[0], r[-1]
    return ((r - rT) * r0 / (r0 - rT)) ** 2


def log_snr(abar):
    with np.errstate(divide="ignore"):
        return np.log(abar) - np.log1p(-abar)


def steps_leading():
    """DDIM/PNDM 'leading' spacing with steps_offset=1: first step at index 981 of 0..999."""
    return (np.arange(S) * (T // S) + 1)[::-1]


def steps_trailing():
    """'trailing' spacing: the first sampling step is the last training step, index 999."""
    return np.round(np.arange(T, 0, -T / S)).astype(int) - 1


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
    return np.stack(shapes)                      # (K, n), every row has mean exactly 0


class World:
    """Mixture of K Gaussians N(mu_k, tau^2 I + s_b^2 11^T), equal weights."""

    def __init__(self, r):
        self.r, self.n = r, r * r
        self.mu = crescent_shapes(r)
        self.mu_sq = (self.mu ** 2).sum(1)

    def sample(self, rng, N):
        k = rng.integers(0, K, N)
        b = rng.normal(0.0, S_B, N)
        return self.mu[k] + b[:, None] + TAU * rng.normal(size=(N, self.n))

    def denoise(self, x, abar):
        """Exact E[x0 | x_t] for x_t = sqrt(abar) x0 + sqrt(1 - abar) eps, x of shape (N, n)."""
        n, a, s2 = self.n, math.sqrt(abar), 1.0 - abar
        c_e = a * a * (TAU ** 2 + n * S_B ** 2) + s2      # variance along the mean direction e
        c_o = a * a * TAU ** 2 + s2                       # variance orthogonal to it
        p = x.sum(1) / math.sqrt(n)                       # projection on e = 1/sqrt(n)
        xx = (x * x).sum(1)
        xm = x @ self.mu.T                                # (N, K); mu_k . e = 0
        quad = (p * p / c_e)[:, None] + (xx[:, None] - 2 * a * xm + a * a * self.mu_sq[None]
                                        - (p * p)[:, None]) / c_o
        logw = -0.5 * quad
        w = np.exp(logw - logw.max(1, keepdims=True))
        w /= w.sum(1, keepdims=True)
        shrink = a * TAU ** 2 / c_o
        along = a * ((TAU ** 2 + n * S_B ** 2) / c_e - TAU ** 2 / c_o)
        return (1 - a * shrink) * (w @ self.mu) + shrink * x + (along * p / math.sqrt(n))[:, None]


def ddim(x, idx, abar, denoise):
    """Deterministic DDIM (eta = 0) written through x0, so abar = 0 is legal (Lin et al. section 6)."""
    for i, t in enumerate(idx):
        a, s = math.sqrt(abar[t]), math.sqrt(1.0 - abar[t])
        x0 = denoise(x, t)
        eps = (x - a * x0) / s
        a2, s2 = (math.sqrt(abar[idx[i + 1]]), math.sqrt(1.0 - abar[idx[i + 1]])) if i + 1 < len(idx) else (1.0, 0.0)
        x = a2 * x0 + s2 * eps
    return x


# ------------------------------------------------------------------------------- schedules
def run_schedules():
    sched = {"linear": abar_linear(), "cosine": abar_cosine(), "scaled_linear": abar_scaled_linear()}
    sched["scaled_linear_zero_snr"] = rescale_zero_terminal_snr(sched["scaled_linear"])
    out = {"T": T, "S": S, "schedules": {}}
    for name, ab in sched.items():
        lam = log_snr(ab)
        cross = int(np.argmax(lam < 0))                   # first index with SNR < 1
        out["schedules"][name] = {
            "sqrt_abar_T": float(np.sqrt(ab[-1])), "snr_T": float(ab[-1] / (1 - ab[-1])),
            "sqrt_abar_leading_first": float(np.sqrt(ab[steps_leading()[0]])),
            "snr_leading_first": float(ab[steps_leading()[0]] / (1 - ab[steps_leading()[0]])),
            "logsnr_first": float(lam[0]), "logsnr_T": float(lam[-1]) if np.isfinite(lam[-1]) else None,
            "snr1_crossing_index": cross, "snr1_crossing_frac": cross / T,
            # every 10th index, for figures (log-SNR is -inf at a zero-SNR end; stored as None)
            "logsnr_every10": [float(v) if np.isfinite(v) else None for v in lam[::10]] + (
                [float(lam[-1]) if np.isfinite(lam[-1]) else None]),
        }
    sl, z = sched["scaled_linear"], sched["scaled_linear_zero_snr"]
    i64 = int(np.argmin(np.abs(sl - 0.64)))             # the series' worked-example level
    out["rescale_at_abar_064"] = {"index": i64, "abar_before": float(sl[i64]), "abar_after": float(z[i64])}
    out["steps_leading_first3"] = steps_leading()[:3].tolist()
    out["steps_trailing_first3"] = steps_trailing()[:3].tolist()
    return out


# ------------------------------------------------------------------------------------ leak
def leak_prediction(abar_start, n):
    """Exact-ODE prediction of (generated brightness std) / (data brightness std) from N(0, I).

    Along e = 1/sqrt(n) the data coordinate is N(0, V0) with V0 = n s_b^2 + tau^2, independent of the
    crescent. The forward process at abar makes it N(0, abar V0 + 1 - abar); a deterministic flow maps
    that Gaussian onto the data linearly, so starting from N(0, 1) instead shrinks the spread by sqrt(VT).
    """
    v0 = n * S_B ** 2 + TAU ** 2
    return 1.0 / math.sqrt(abar_start * v0 + 1.0 - abar_start)


def run_leak(quick):
    sl = abar_scaled_linear()
    z = rescale_zero_terminal_snr(sl)
    variants = {
        "sd_leading_noise": (sl, steps_leading(), "noise"),
        "sd_trailing_noise": (sl, steps_trailing(), "noise"),
        "sd_trailing_oracle": (sl, steps_trailing(), "oracle"),
        "zero_snr_trailing_noise": (z, steps_trailing(), "noise"),
    }
    N = 1000 if quick else 4000
    chunk = 500
    res = {"N": N, "s_b": S_B, "tau": TAU, "a_c": A_C, "by_resolution": {}}
    for r in (4, 16, 64, 128):
        w = World(r)
        rng_d = np.random.default_rng(1000 + r)
        data = w.sample(rng_d, 20000 if not quick else 5000)
        bd = data.mean(1)
        sd_data = float(bd.std())
        thr = 1.6448536 * math.sqrt(S_B ** 2 + TAU ** 2 / w.n)   # 10% of data lies beyond +-thr
        row = {"n": w.n, "data_brightness_std": sd_data, "data_brightness_mean": float(bd.mean()),
               "data_frac_beyond_thr": float((np.abs(bd) > thr).mean()), "variants": {}}
        for name, (ab, idx, start) in variants.items():
            rng = np.random.default_rng(7 + r)       # same starting noise for every variant
            outs = []
            for c0 in range(0, N, chunk):
                m = min(chunk, N - c0)
                eps = rng.normal(size=(m, w.n))
                if start == "oracle":
                    x0 = w.sample(np.random.default_rng(99 + r + c0), m)
                    x = math.sqrt(ab[idx[0]]) * x0 + math.sqrt(1 - ab[idx[0]]) * eps
                else:
                    x = eps
                outs.append(ddim(x, idx, ab, lambda xx, t: w.denoise(xx, ab[t])))
            g = np.concatenate(outs)
            bg = g.mean(1)
            v = {"brightness_mean": float(bg.mean()), "brightness_std": float(bg.std()),
                 "std_ratio": float(bg.std() / sd_data),
                 "predicted_ratio": leak_prediction(ab[idx[0]], w.n) if start == "noise" else 1.0,
                 "frac_beyond_thr": float((np.abs(bg) > thr).mean())}
            if r == 128:
                edges = np.linspace(-1.2, 1.2, 49)
                v["hist"] = np.histogram(bg, edges)[0].tolist()
                v["hist_edges"] = edges.tolist()
                # six previews, 32x32 (4x4 block mean), for the figures
                pv = g[:6].reshape(6, 32, 4, 32, 4).mean(axis=(2, 4))
                v["previews_32"] = np.round(pv, 3).tolist()
            row["variants"][name] = v
        if r == 128:
            edges = np.linspace(-1.2, 1.2, 49)
            row["data_hist"] = np.histogram(bd, edges)[0].tolist()
            row["data_previews_32"] = np.round(data[:6].reshape(6, 32, 4, 32, 4).mean(axis=(2, 4)), 3).tolist()
        res["by_resolution"][str(r)] = row
        print(f"  leak r={r:3d} n={w.n:5d} data_std={sd_data:.4f} " + " ".join(
            f"{k}={v['std_ratio']:.4f}(pred {v['predicted_ratio']:.4f})" for k, v in row["variants"].items()), flush=True)
    # More sampling steps: the flawed schedule converges to its predicted ratio, the fixed one to 1.
    w = World(128)
    sd_data = math.sqrt(S_B ** 2 + TAU ** 2 / w.n)
    res["steps_sweep"] = {"r": 128, "N": 500 if quick else 1000, "rows": []}
    for steps in ((25, 50, 100) if quick else (25, 50, 100, 200)):
        idx = np.round(np.arange(T, 0, -T / steps)).astype(int) - 1
        row = {"steps": steps}
        for name, ab in (("sd_trailing_noise", sl), ("zero_snr_trailing_noise", z)):
            rng = np.random.default_rng(7 + 128)
            g = np.concatenate([ddim(rng.normal(size=(500, w.n)), idx, ab, lambda xx, t: w.denoise(xx, ab[t]))
                                for _ in range(res["steps_sweep"]["N"] // 500)])
            row[name] = float(g.mean(1).std() / sd_data)
        res["steps_sweep"]["rows"].append(row)
        print(f"  leak steps={steps:3d} n=16384 " + " ".join(f"{k}={v:.4f}" for k, v in row.items() if k != "steps"),
              flush=True)
    return res


# ----------------------------------------------------------------------------------- train
WEIGHTS = {  # loss weight on ||x0 - x0_hat||^2 as a function of SNR (Hang et al. convention)
    "const": lambda snr: 1.0 + 0.0 * snr,
    "snr": lambda snr: snr,                      # the DDPM epsilon loss, written in x0 units
    "maxsnr1": lambda snr: snr.clamp(min=1.0),   # Salimans & Ho's truncated SNR
    "minsnr5": lambda snr: snr.clamp(max=5.0),   # Min-SNR-gamma, gamma = 5
}
TARGET_K = {"eps": lambda snr: snr, "x0": lambda snr: 1.0 + 0.0 * snr, "v": lambda snr: 1.0 + snr}
LAM_GRID = np.round(np.arange(-9.0, 9.01, 0.75), 3)       # 25 log-SNR values for per-level errors
SAMPLER_LAMBDAS = np.linspace(-9.0, 9.0, S)                 # evaluation sampler: uniform in log-SNR


def power_ema_gamma(sigma_rel):
    """Solve EDM2's sigma_rel = sqrt(g+1) / ((g+2) sqrt(g+3)) for the power-EMA exponent g."""
    lo, hi = 0.0, 1e4
    for _ in range(200):
        g = 0.5 * (lo + hi)
        if math.sqrt(g + 1) / ((g + 2) * math.sqrt(g + 3)) > sigma_rel:
            lo = g
        else:
            hi = g
    return 0.5 * (lo + hi)


def train_run(cfg):
    import torch
    import torch.nn as nn
    torch.set_num_threads(1)
    torch.manual_seed(cfg["seed"])
    gen = torch.Generator().manual_seed(cfg["seed"])
    world = World(8)
    n = world.n
    mu = torch.tensor(world.mu, dtype=torch.float32)
    ab_c = torch.tensor(abar_cosine(), dtype=torch.float32)

    class Net(nn.Module):
        """MLP denoiser: [x_t, 17 log-SNR features] -> width -> width -> width -> n (no skip)."""

        def __init__(self, width):
            super().__init__()
            self.f = nn.Sequential(nn.Linear(n + 17, width), nn.SiLU(), nn.Linear(width, width), nn.SiLU(),
                                   nn.Linear(width, width), nn.SiLU(), nn.Linear(width, n))

        def forward(self, x, lam):
            c = (lam / 10.0)[:, None]
            fr = (2.0 ** torch.arange(8, dtype=torch.float32))[None] * math.pi * c
            return self.f(torch.cat([x, c, torch.sin(fr), torch.cos(fr)], 1))

    def to_x0(out, x, a, s):
        if cfg["target"] == "eps":
            return (x - s * out) / a
        if cfg["target"] == "v":
            return a * x - s * out
        return out

    net = Net(cfg["width"])
    opt = torch.optim.Adam(net.parameters(), lr=cfg["lr"])
    params = [p for p in net.parameters()]
    ema_b = {b: [p.detach().clone() for p in params] for b in (0.99, 0.999, 0.9999)}
    ema_p = {sr: ([p.detach().clone() for p in params], power_ema_gamma(sr)) for sr in (0.05, 0.10, 0.20)}

    def sample_x0(N):
        k = torch.randint(0, K, (N,), generator=gen)
        b = torch.randn(N, generator=gen) * S_B
        return mu[k] + b[:, None] + TAU * torch.randn(N, n, generator=gen)

    # fixed evaluation sets, identical across runs (paired comparisons)
    ev = np.random.default_rng(2026)
    ev_x0 = world.sample(ev, 512)
    ev_eps = ev.normal(size=(512, n))
    ev_start = ev.normal(size=(4096, n))
    ref = world.sample(np.random.default_rng(31), 4096)
    proj = np.random.default_rng(5).normal(size=(n, 128))
    proj /= np.linalg.norm(proj, axis=0, keepdims=True)
    ref_sorted = np.sort(ref @ proj, axis=0)
    lam_t = torch.tensor(LAM_GRID, dtype=torch.float32)
    exact_cache = {}
    for lam in LAM_GRID:
        abar = 1.0 / (1.0 + math.exp(-lam))
        xt = math.sqrt(abar) * ev_x0 + math.sqrt(1 - abar) * ev_eps
        exact_cache[lam] = (xt, world.denoise(xt, abar), ((world.denoise(xt, abar) - ev_x0) ** 2).mean())

    def set_params(src):
        saved = [p.detach().clone() for p in params]
        with torch.no_grad():
            for p, q in zip(params, src):
                p.copy_(q)
        return saved

    @torch.no_grad()
    def per_level_excess():
        ex = []
        for lam in LAM_GRID:
            xt, x0_star, _ = exact_cache[lam]
            abar = 1.0 / (1.0 + math.exp(-lam))
            a, s = math.sqrt(abar), math.sqrt(1 - abar)
            x = torch.tensor(xt, dtype=torch.float32)
            out = net(x, torch.full((x.shape[0],), float(lam)))
            x0_hat = to_x0(out, x, a, s).double().numpy()
            ex.append(float(((x0_hat - x0_star) ** 2).mean()))
        return ex

    @torch.no_grad()
    def sample_quality():
        x = torch.tensor(ev_start, dtype=torch.float32)
        lams = SAMPLER_LAMBDAS
        for i, lam in enumerate(lams):
            abar = 1.0 / (1.0 + math.exp(-lam))
            a, s = math.sqrt(abar), math.sqrt(1 - abar)
            out = net(x, torch.full((x.shape[0],), float(lam)))
            x0 = to_x0(out, x, a, s)
            eps = (x - a * x0) / s
            if i + 1 < len(lams):
                ab2 = 1.0 / (1.0 + math.exp(-lams[i + 1]))
                x = math.sqrt(ab2) * x0 + math.sqrt(1 - ab2) * eps
            else:
                x = x0
        g = x.double().numpy()
        if not np.all(np.isfinite(g)):
            return {"swd": None, "offmanifold": None, "brightness_std": None}
        swd = float(np.sqrt(((np.sort(g @ proj, axis=0) - ref_sorted) ** 2).mean()))
        bright = g.mean(1)
        resid = g - bright[:, None]
        d = (resid ** 2).sum(1)[:, None] - 2 * resid @ world.mu.T + world.mu_sq[None]
        return {"swd": swd, "offmanifold": float(d.min(1).mean() / n), "brightness_std": float(bright.std())}

    def evaluate(tag):
        out = {"raw": {"excess": per_level_excess(), **sample_quality()}}
        for b, src in ema_b.items():
            saved = set_params(src)
            out[f"ema_{b}"] = {"excess": per_level_excess(), **sample_quality()}
            set_params(saved)
        for sr, (src, _) in ema_p.items():
            saved = set_params(src)
            out[f"power_{sr}"] = {"excess": per_level_excess(), **sample_quality()}
            set_params(saved)
        return out

    checkpoints = sorted(set(cfg["checkpoints"]))
    log = {"config": cfg, "params": sum(p.numel() for p in params), "checkpoints": {}, "loss": []}
    w_fn, k_fn = WEIGHTS[cfg["weighting"]], TARGET_K[cfg["target"]]
    t0 = time.time()
    run_loss = 0.0
    for step in range(1, cfg["steps"] + 1):
        x0 = sample_x0(cfg["batch"])
        t = torch.randint(0, T, (cfg["batch"],), generator=gen)
        abar = ab_c[t]
        a, s = abar.sqrt()[:, None], (1 - abar).sqrt()[:, None]
        eps = torch.randn(x0.shape, generator=gen)
        x = a * x0 + s * eps
        snr = abar / (1 - abar)
        lam = torch.log(snr)
        target = {"eps": eps, "x0": x0, "v": a * eps - s * x0}[cfg["target"]]
        out = net(x, lam)
        weight = w_fn(snr) / k_fn(snr)
        loss = (weight * ((out - target) ** 2).mean(1)).mean()
        opt.zero_grad(set_to_none=True)
        loss.backward()
        opt.step()
        run_loss += loss.item()
        with torch.no_grad():
            for b, src in ema_b.items():
                for q, p in zip(src, params):
                    q.mul_(b).add_(p, alpha=1 - b)
            for sr, (src, g) in ema_p.items():
                beta = (1 - 1 / step) ** (g + 1)
                for q, p in zip(src, params):
                    q.mul_(beta).add_(p, alpha=1 - beta)
        if step % 500 == 0:
            log["loss"].append(round(run_loss / 500, 6))
            run_loss = 0.0
        if step in checkpoints:
            log["checkpoints"][str(step)] = evaluate(step)
    log["seconds"] = round(time.time() - t0, 1)
    log["mmse_x0"] = [float(exact_cache[l][2]) for l in LAM_GRID]
    return log


def train_configs(quick):
    steps_long = 8000 if quick else 40000
    steps = 4000 if quick else 20000
    seeds = (0,) if quick else (0, 1, 2)
    base = {"lr": 1e-3, "batch": 256}
    cks_long = [steps_long // 8, steps_long // 4, steps_long // 2, steps_long]
    cks = [steps // 4, steps // 2, steps]
    cfgs = []
    for wgt in ("const", "snr", "maxsnr1", "minsnr5"):         # weighting, x0-prediction, as in Min-SNR
        for sd in seeds:
            cfgs.append({**base, "exp": "weighting", "target": "x0", "weighting": wgt, "width": 128,
                         "steps": steps_long, "seed": sd, "checkpoints": cks_long})
    for width in (32, 256):                                    # target at matched Min-SNR objective
        for tgt in ("eps", "x0", "v"):
            for sd in seeds:
                cfgs.append({**base, "exp": "target", "target": tgt, "weighting": "minsnr5", "width": width,
                             "steps": steps, "seed": sd, "checkpoints": cks})
    for width in ((32, 128, 512) if quick else (32, 64, 128, 256, 512)):  # capacity vs weighting
        for wgt in ("snr", "minsnr5"):
            for sd in seeds[:2]:
                cfgs.append({**base, "exp": "width", "target": "x0", "weighting": wgt, "width": width,
                             "steps": steps, "seed": sd, "checkpoints": [steps]})
    return cfgs


def sample_floors():
    """What a perfect model would score: two independent data draws compared the same way."""
    world = World(8)
    ref = world.sample(np.random.default_rng(31), 4096)
    other = world.sample(np.random.default_rng(32), 4096)
    proj = np.random.default_rng(5).normal(size=(world.n, 128))
    proj /= np.linalg.norm(proj, axis=0, keepdims=True)
    swd = float(np.sqrt(((np.sort(other @ proj, axis=0) - np.sort(ref @ proj, axis=0)) ** 2).mean()))
    resid = other - other.mean(1, keepdims=True)
    d = (resid ** 2).sum(1)[:, None] - 2 * resid @ world.mu.T + world.mu_sq[None]
    return {"swd": swd, "offmanifold": float(d.min(1).mean() / world.n), "brightness_std": float(other.mean(1).std())}


def run_train(quick, workers, cache):
    cfgs = train_configs(quick)
    results = [None] * len(cfgs)
    paths = [cache / ("train-" + hashlib.sha1(json.dumps(c, sort_keys=True).encode()).hexdigest()[:12] + ".json")
             for c in cfgs]
    todo = [i for i in range(len(cfgs)) if not paths[i].exists()]
    for i in set(range(len(cfgs))) - set(todo):
        results[i] = json.loads(paths[i].read_text())
    print(f"  train: {len(cfgs)} runs, {len(cfgs) - len(todo)} from cache, {len(todo)} to run", flush=True)
    todo.sort(key=lambda i: -cfgs[i]["steps"] * cfgs[i]["width"])     # longest first keeps the pool busy
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(train_run, cfgs[i]): i for i in todo}
        for done, f in enumerate(as_completed(futs), 1):
            i = futs[f]
            results[i] = f.result()
            paths[i].write_text(json.dumps(results[i]))
            c = cfgs[i]
            last = results[i]["checkpoints"][str(c["steps"])]["raw"]
            print(f"  train {done:2d}/{len(todo)} {c['exp']:9s} {c['target']:3s} {c['weighting']:7s} "
                  f"w={c['width']:3d} seed={c['seed']} swd={last['swd']} ({results[i]['seconds']}s)", flush=True)
    return {"lam_grid": LAM_GRID.tolist(), "sampler_lambdas": [float(SAMPLER_LAMBDAS[0]), float(SAMPLER_LAMBDAS[-1])],
            "floors": sample_floors(), "runs": results}


# ------------------------------------------------------------------------------------ main
def provenance():
    import torch
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
            "cpu": cpu, "cores": os.cpu_count(), "python": sys.version.split()[0], "numpy": np.__version__,
            "torch": torch.__version__}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["schedules", "leak", "train", "all"])
    ap.add_argument("--quick", action="store_true", help="smaller runs, about 6 minutes on 12 cores")
    ap.add_argument("--workers", type=int, default=max(1, min(12, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--out", default=str(HERE / "captures.json"))
    ap.add_argument("--cache", default=str(HERE / ".cache"),
                    help="finished runs are kept here, so an interrupted run resumes; delete it to start over")
    args = ap.parse_args()
    prov = provenance()
    print(f"Captured {prov['captured_utc']} on {prov['cpu']} ({prov['cores']} cores), {prov['os']}, "
          f"Python {prov['python']}, numpy {prov['numpy']}, torch {prov['torch']}" + (" [quick]" if args.quick else ""))
    out_path = Path(args.out)
    cap = json.loads(out_path.read_text()) if out_path.exists() and args.what != "all" else {}
    cap["provenance"] = {**prov, "quick": args.quick}
    if args.what in ("schedules", "all"):
        cap["schedules"] = run_schedules()
        for k, v in cap["schedules"]["schedules"].items():
            print(f"  schedule {k:24s} sqrt(abar_T)={v['sqrt_abar_T']:.6f} SNR_T={v['snr_T']:.6e} "
                  f"leading first step sqrt(abar)={v['sqrt_abar_leading_first']:.6f}")
    cache = Path(args.cache)
    cache.mkdir(parents=True, exist_ok=True)
    if args.what in ("leak", "all"):
        src = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]   # any edit to this file re-runs it
        leak_path = cache / f"leak{'-quick' if args.quick else ''}-{src}.json"
        if leak_path.exists():                       # a resumed run prints the same lines
            cap["leak"] = json.loads(leak_path.read_text())
            for r, row in cap["leak"]["by_resolution"].items():
                print(f"  leak r={int(r):3d} n={row['n']:5d} data_std={row['data_brightness_std']:.4f} " + " ".join(
                    f"{k}={v['std_ratio']:.4f}(pred {v['predicted_ratio']:.4f})" for k, v in row["variants"].items()))
            for row in cap["leak"]["steps_sweep"]["rows"]:
                print(f"  leak steps={row['steps']:3d} n=16384 " + " ".join(
                    f"{k}={v:.4f}" for k, v in row.items() if k != "steps"))
        else:
            cap["leak"] = run_leak(args.quick)
            leak_path.write_text(json.dumps(cap["leak"]))
    if args.what in ("train", "all"):
        cap["train"] = run_train(args.quick, args.workers, cache)
    out_path.write_text(json.dumps(cap, indent=1))
    print(f"wrote {os.path.relpath(out_path)}")


if __name__ == "__main__":
    main()
