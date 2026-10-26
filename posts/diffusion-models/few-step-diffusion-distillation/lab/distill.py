#!/usr/bin/env python3
"""Lab for "Few-Step Diffusion and Distillation: 20 Steps Into 1" (Diffusion Models series, part 7).

The teacher is never trained: it is the exact denoiser E[x0 | x] of part 5's "crescent world" at
8x8 pixels, and the exact probability-flow ODE it defines, solved by RK4. Every student is a small
MLP trained on a CPU, so every error measured here belongs to the student, not to the teacher.

  worked     the decision between two opposite crescents as one number: the exact denoiser, the
             exact endpoint, DDIM at 1 to 8 steps, one progressive-distillation halving, and a small
             network fitted to the cliff by least squares (closed forms plus a 1-D fit, about 1 min)
  reference  4,096 starting noises and their exact ODE endpoints; DDIM and DPM-Solver++(2M) with the
             exact denoiser at 1 to 128 calls; the sample distance between two sets of real data
  teacher    a network copy of the exact denoiser, which warm-starts every student the way a
             pretrained diffusion model warm-starts a real distillation
  students   direct regression, progressive distillation (64 steps down to 1), consistency
             distillation, distribution matching in three variants, and a shortcut model; two seeds
  samples    six starting noises through every method, for the figures
  all        everything, in that order

Every sample lives in the coordinates of parts 5 and 6: x = x0 + sigma * eps, sigma from 80 to 0.

Run:   python distill.py all             # about 30 min with 8 worker processes
       python distill.py all --quick     # about 6 min, shorter training, noisier numbers
       python distill.py worked --x 1.6  # the halving at another starting point
       python distill.py dmd --ratio 1 --warm 0 --steps 3000   # one distribution-matching run (E4)
Writes captures.json beside this file (or --out) and prints the same numbers. Trained networks are
cached in .cache/ under a hash of this file, so a rerun resumes and an edit retrains.
"""
import argparse
import copy
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
    os.environ.setdefault(_v, "1")     # one thread per worker process; the pool supplies parallelism

import numpy as np
import torch
import torch.nn as nn

torch.set_num_threads(1)
HERE = Path(__file__).resolve().parent
K = 4                                   # crescent orientations (mixture components)
A_C, S_B, TAU = 0.9, 0.3, 0.1           # crescent RMS amplitude, brightness spread, detail noise
R = 8                                   # image side; 64 pixels
N_PIX = R * R
SMAX, SMIN, RHO = 80.0, 0.002, 7.0      # EDM's noise range and step spacing
SIGMA_DATA = math.sqrt(A_C ** 2 + S_B ** 2 + TAU ** 2)   # per-pixel data std, for preconditioning
GREY = 2.0 / 256                        # one 8-bit grey level of an image scaled to [-1, 1]
N_EVAL = 4096                           # shared starting noises for every method
WIDTH = 256                             # hidden width of every network


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


MU = crescent_shapes(R)
MU_T = torch.tensor(MU, dtype=torch.float32)
V_E = S_B ** 2 * N_PIX + TAU ** 2               # data variance along the brightness axis 1/sqrt(n)
Q_SPAN, _ = np.linalg.qr(MU.T)                   # orthonormal basis of the crescent span
GAP = min(np.linalg.norm(MU[i] - MU[j]) for i in range(K) for j in range(K) if i != j)


def sample_data(rng, N):
    """x0 = mu_k + b*1 + tau*z: k uniform, b ~ N(0, s_b^2), z ~ N(0, I). A Gaussian mixture."""
    k = rng.integers(0, K, N)
    b = rng.normal(0.0, S_B, N)
    return MU[k] + b[:, None] + TAU * rng.normal(size=(N, N_PIX))


def denoise_np(x, s):
    """Exact D(x; s) = E[x0 | x0 + s*eps = x] in float64; s a scalar."""
    s2 = s * s
    p = x.mean(1, keepdims=True)                 # brightness part (1/n)(1.x) on every pixel
    lg = x @ MU.T / (TAU ** 2 + s2)              # norms are equal, so only x.mu_k matters
    lg -= lg.max(1, keepdims=True)
    w = np.exp(lg)
    w /= w.sum(1, keepdims=True)
    a_o = TAU ** 2 / (TAU ** 2 + s2)             # shrink of detail, off the brightness axis
    a_e = V_E / (V_E + s2)                       # shrink of the brightness coordinate
    return (1.0 - a_o) * (w @ MU) + a_o * (x - p) + a_e * p


def denoise_t(x, s):
    """The same exact denoiser in torch float32, with s of shape (B, 1); the teacher of training."""
    s2 = s * s
    p = x.mean(1, keepdim=True)
    w = torch.softmax(x @ MU_T.T / (TAU ** 2 + s2), dim=1)
    a_o = TAU ** 2 / (TAU ** 2 + s2)
    a_e = V_E / (V_E + s2)
    return (1.0 - a_o) * (w @ MU_T) + a_o * (x - p) + a_e * p


# ----------------------------------------------------------------- steps and exact solutions
def sig_u(u):
    """EDM's rho = 7 spacing as a function of u in [0, 1]: sigma(0) = 80, sigma(1) = 0.002."""
    return (SMAX ** (1 / RHO) + u * (SMIN ** (1 / RHO) - SMAX ** (1 / RHO))) ** RHO


def grid(N):
    """N steps: the levels sigma(i/N) for i < N, then 0. grid(N) contains grid(N/2), which
    progressive distillation needs, and the last step returns the denoiser's answer."""
    return [float(sig_u(i / N)) for i in range(N)] + [0.0]


def rk4_endpoints(x, steps=2000, s_from=SMAX):
    """The exact ODE dx/du = x - D(x, e^u), u = log sigma, from s_from down to SMIN by RK4, then
    D at SMIN: the endpoint every student is measured against (float64)."""
    u0, u1 = math.log(s_from), math.log(SMIN)
    h = (u1 - u0) / steps
    u = u0
    f = lambda xx, uu: xx - denoise_np(xx, math.exp(uu))
    for _ in range(steps):
        k1 = f(x, u)
        k2 = f(x + 0.5 * h * k1, u + 0.5 * h)
        k3 = f(x + 0.5 * h * k2, u + 0.5 * h)
        k4 = f(x + h * k3, u + h)
        x = x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        u += h
    return denoise_np(x, SMIN)


@torch.no_grad()
def ddim(Dfn, xT, N):
    """DDIM (eta = 0) on grid(N): x' = D + (s'/s)(x - D), one denoiser call per step."""
    g = grid(N)
    x = xT
    for s, s2 in zip(g[:-1], g[1:]):
        d = Dfn(x, torch.full((x.shape[0], 1), s))
        x = d + (s2 / s) * (x - d)
    return x


@torch.no_grad()
def dpmpp2m(Dfn, xT, N):
    """DPM-Solver++(2M) on grid(N): second order at one call per step (part 6)."""
    g = grid(N)
    x, old, h_last = xT, None, None
    for s, s2 in zip(g[:-1], g[1:]):
        d = Dfn(x, torch.full((x.shape[0], 1), s))
        if s2 == 0:
            x = d
            continue
        h = math.log(s / s2)
        dd = d if old is None else (1 + 1 / (2 * h_last / h)) * d - (1 / (2 * h_last / h)) * old
        x = (s2 / s) * x + (1 - s2 / s) * dd
        old, h_last = d, h
    return x


# ------------------------------------------------------------------------------- networks
def precond(s, kind="edm"):
    """EDM's preconditioning (Karras et al., Table 1). kind='cm' is the consistency models' version,
    whose c_skip(SMIN) = 1 and c_out(SMIN) = 0 build the boundary condition f(x, SMIN) = x in."""
    sd2 = SIGMA_DATA ** 2
    c_in = 1.0 / torch.sqrt(s * s + sd2)
    if kind == "edm":
        c_skip = sd2 / (s * s + sd2)
        c_out = s * SIGMA_DATA / torch.sqrt(s * s + sd2)
    else:
        c_skip = sd2 / ((s - SMIN) ** 2 + sd2)
        c_out = (s - SMIN) * SIGMA_DATA / torch.sqrt(s * s + sd2)
    return c_in, c_skip, c_out


class Fourier(nn.Module):
    def __init__(self, n=16):
        super().__init__()
        self.register_buffer("f", 2.0 ** torch.linspace(-1, 5, n))

    def forward(self, c):
        a = c * self.f
        return torch.cat([torch.sin(a), torch.cos(a)], 1)


class Net(nn.Module):
    """F(c_in x, embed(ln sigma / 4) [, embed(ln sigma' / 4)]): three hidden layers of WIDTH. With
    two=True it also sees the target noise level sigma' of a jump (the flow-map student)."""

    def __init__(self, width=WIDTH, two=False):
        super().__init__()
        self.two = two
        self.emb = Fourier(16)
        d_in = N_PIX + 32 * (2 if two else 1)
        self.f = nn.Sequential(nn.Linear(d_in, width), nn.SiLU(), nn.Linear(width, width), nn.SiLU(),
                               nn.Linear(width, width), nn.SiLU(), nn.Linear(width, N_PIX))

    def forward(self, xin, s, s2=None):
        e = [self.emb(torch.log(s) / 4)]
        if self.two:
            e.append(self.emb(torch.log(torch.clamp(s2, min=1e-4)) / 4))   # s' = 0 for the last jump
        return self.f(torch.cat([xin] + e, 1))


def D_net(net, x, s, kind="edm", s2=None):
    c_in, c_skip, c_out = precond(s, kind)
    return c_skip * x + c_out * net(c_in * x, s, s2)


def lr_schedule(steps, warm=100):
    """Linear warm-up, then linear decay to zero, as progressive distillation anneals each round."""
    return lambda i: min(1.0, (i + 1) / warm) * max(0.0, 1 - i / steps)


def sample_sigma(B, gen, lo=SMIN, hi=SMAX):
    return torch.exp(math.log(lo) + torch.rand(B, 1, generator=gen) * (math.log(hi) - math.log(lo)))


def one_step(net, z, kind="edm"):
    with torch.no_grad():
        return D_net(net, SMAX * z, torch.full((z.shape[0], 1), SMAX), kind)


# -------------------------------------------------------------------------------- metrics
def crescent_of(x):
    """Which crescent a sample shows: the largest projection of its brightness-free part."""
    return np.argmax((x - x.mean(1, keepdims=True)) @ MU.T, 1)


def swd(a, b, n_dir=256, seed=5):
    """Sliced Wasserstein distance between two sample sets (part 5's instrument)."""
    d = np.random.default_rng(seed).normal(size=(a.shape[1], n_dir))
    d /= np.linalg.norm(d, axis=0, keepdims=True)
    pa, pb = np.sort(a @ d, 0), np.sort(b @ d, 0)
    return float(np.sqrt(((pa - pb) ** 2).mean()))


def evaluate(out, ref, data):
    """Pairing metrics against the exact endpoint from the same noise, and set metrics against data."""
    out = out.numpy().astype(np.float64) if torch.is_tensor(out) else out
    e = np.sqrt(((out - ref) ** 2).mean(1))
    k_out = crescent_of(out)
    same = k_out == crescent_of(ref)
    resid = out - out.mean(1, keepdims=True)
    rr = resid - MU[k_out]
    in_span = rr @ Q_SPAN
    dist = np.sqrt((in_span ** 2).sum(1))
    detail = ((rr ** 2).sum(1) - (in_span ** 2).sum(1)).mean() / (N_PIX - K - 1) / TAU ** 2
    return {"flip": round(float((~same).mean()), 5),
            "err": round(float(np.sqrt((e ** 2).mean())), 5),
            "err_kept": round(float(np.sqrt((e[same] ** 2).mean())), 5) if same.any() else None,
            "swd": round(swd(out, data), 5),
            "blend": round(float((dist > 0.1 * GAP).mean()), 5),
            "spread": round(float(out.mean(1).std() / math.sqrt(S_B ** 2 + TAU ** 2 / N_PIX)), 4),
            "detail": round(float(detail), 4),
            "cover": (np.bincount(k_out, minlength=K) / len(k_out)).round(4).tolist(),
            "_flip_mask": (~same), "_blend_mask": dist > 0.1 * GAP}


def margins(z):
    """Distance of a starting noise from the nearest decision boundary: the gap between its two
    largest projections on the unit crescent directions."""
    srt = np.sort(z @ (MU / np.linalg.norm(MU, axis=1, keepdims=True)).T, 1)
    return srt[:, -1] - srt[:, -2]


MARGIN_BINS = [0.0, 0.025, 0.05, 0.1, 0.2, 0.4, 0.8, 10.0]


def by_margin(mask, m):
    return [round(float(mask[(m >= lo) & (m < hi)].mean()), 4) for lo, hi in zip(MARGIN_BINS[:-1], MARGIN_BINS[1:])]


def public(ev):
    return {k: v for k, v in ev.items() if not k.startswith("_")}


# ----------------------------------------------------------------------------------- worked
def run_worked(x_half=40.0):
    """The decision between crescents 0 and 2 (they point in opposite directions) as one number.
    In a world of just these two, the position along the line between them is +-a plus detail noise
    of 0.1, and its exact denoiser is a closed form."""
    a = float(np.linalg.norm(MU[0] - MU[2]) / 2)

    def D(x, s):
        v = TAU ** 2 + s * s
        return (TAU ** 2 * x + s * s * a * np.tanh(a * x / v)) / v

    def exact(x, n=4000):
        u0, u1 = math.log(SMAX), math.log(SMIN)
        h = (u1 - u0) / n
        u = u0
        f = lambda xx, uu: xx - D(xx, math.exp(uu))
        for _ in range(n):
            k1 = f(x, u); k2 = f(x + .5 * h * k1, u + .5 * h); k3 = f(x + .5 * h * k2, u + .5 * h)
            k4 = f(x + h * k3, u + h)
            x = x + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
            u += h
        return D(x, SMIN)

    def ddim1(x, N):
        g = grid(N)
        for s, s2 in zip(g[:-1], g[1:]):
            d = D(x, s)
            x = d + (s2 / s) * (x - d)
        return x

    eps = np.array([1.0, 0.5, 0.1, 0.02, 0.005, 0.001])
    res = {"a": a, "tau": TAU, "grids": {str(N): grid(N) for N in (1, 2, 4, 8)}, "rows": []}
    ex = exact(SMAX * eps)
    for e_, x_ex in zip(eps, ex):
        x = SMAX * e_
        res["rows"].append({"eps": float(e_), "x": float(x), "D80": float(D(x, SMAX)),
                            **{f"ddim{N}": float(ddim1(x, N)) for N in (1, 2, 4, 8, 64)}, "exact": float(x_ex)})
    res["exact_pm"] = [float(v) for v in exact(SMAX * np.array([0.001, -0.001]))]
    # One progressive-distillation halving, 4 teacher steps -> 2 student steps, at x = 40 (eps 0.5).
    g4, g2 = grid(4), grid(2)
    x = float(x_half)
    d1 = D(x, g4[0]); xm = d1 + (g4[1] / g4[0]) * (x - d1)
    d2 = D(xm, g4[1]); x2 = d2 + (g4[2] / g4[1]) * (xm - d2)
    r = g2[1] / g2[0]
    res["halving"] = {"x": x, "sigma": g4[0], "sigma_mid": g4[1], "sigma_next": g4[2], "D_first": float(d1),
                      "x_mid": float(xm), "D_second": float(d2), "x_two": float(x2), "ratio": r,
                      "target": float((x2 - r * x) / (1 - r)), "student_end": float(ddim1(x, 4)),
                      "ddim2_end": float(ddim1(x, 2))}
    # The flow map in DDIM form: the effective denoiser of one exact jump from 80 to s' equals the
    # 1/s^2-weighted average of D along the exact path (checked numerically at x = 40).
    s_to = g4[2]
    n = 20000
    us = np.linspace(math.log(SMAX), math.log(s_to), n + 1)
    xs = [x]
    xx = x
    h = us[1] - us[0]
    f = lambda xv, uu: xv - D(xv, math.exp(uu))
    for i in range(n):
        u = us[i]
        k1 = f(xx, u); k2 = f(xx + .5 * h * k1, u + .5 * h); k3 = f(xx + .5 * h * k2, u + .5 * h)
        k4 = f(xx + h * k3, u + h)
        xx = xx + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        xs.append(xx)
    xs = np.array(xs)
    ss = np.exp(us)
    dbar_jump = (xx - (s_to / SMAX) * x) / (1 - s_to / SMAX)
    wts = s_to * SMAX / (SMAX - s_to) / ss ** 2 * ss            # weight per unit log-sigma: (s's/(s-s'))/s
    dbar_avg = float(np.trapezoid(wts * D(xs, ss), -us) / np.trapezoid(wts, -us))
    res["flow_map_check"] = {"to": s_to, "dbar_jump": float(dbar_jump), "dbar_path_average": dbar_avg}
    # A small network fitted to the cliff by least squares: how wide its ramp is.
    rng = np.random.default_rng(0)
    e_tr = rng.normal(size=200000)
    y_tr = exact(SMAX * e_tr, n=1500)
    torch.manual_seed(0)
    net = nn.Sequential(nn.Linear(1, 64), nn.SiLU(), nn.Linear(64, 64), nn.SiLU(), nn.Linear(64, 1))
    opt = torch.optim.Adam(net.parameters(), lr=3e-3)
    et = torch.tensor(e_tr, dtype=torch.float32)[:, None]
    yt = torch.tensor(y_tr, dtype=torch.float32)[:, None]
    gen = torch.Generator().manual_seed(0)
    for _ in range(4000):
        idx = torch.randint(0, len(et), (1024,), generator=gen)
        loss = ((net(et[idx]) - yt[idx]) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    with torch.no_grad():
        e_line = torch.linspace(-0.1, 0.1, 2001)[:, None]
        g_line = net(e_line).numpy().ravel()
        e_ev = np.random.default_rng(1).normal(size=200000)
        g_ev = net(torch.tensor(e_ev, dtype=torch.float32)[:, None]).numpy().ravel()
    ramp = e_line.numpy().ravel()[np.abs(g_line) < 0.5 * a]
    res["student_1d"] = {"width": 64, "ramp": [float(ramp.min()), float(ramp.max())],
                         "share_between": float((np.abs(g_ev) < 0.5 * a).mean()),
                         "curve": [[float(e_), float(v)] for e_, v in zip(e_line.numpy().ravel()[::20], g_line[::20])]}
    curve_e = np.concatenate([-np.geomspace(3, 1e-4, 60), np.geomspace(1e-4, 3, 60)])
    res["map"] = {"eps": curve_e.tolist(), "exact": exact(SMAX * curve_e).tolist(),
                  **{f"ddim{N}": ddim1(SMAX * curve_e, N).tolist() for N in (1, 2, 4)}}
    hv = res["halving"]
    print(f"  worked: a={a:.4f}; at x=40 (eps 0.5) D(x;80)={res['rows'][1]['D80']:.4f}, DDIM 1/2/4 steps "
          f"{res['rows'][1]['ddim1']:.4f}/{res['rows'][1]['ddim2']:.4f}/{res['rows'][1]['ddim4']:.4f}, exact {res['rows'][1]['exact']:.4f}")
    print(f"  worked: halving 4->2 at x={hv['x']:g}: teacher {hv['x_mid']:.4f} -> {hv['x_two']:.4f}; student target "
          f"{hv['target']:.4f} against D {hv['D_first']:.4f}; cliff {res['exact_pm'][0]:+.4f} / {res['exact_pm'][1]:+.4f}")
    print(f"  worked: flow-map check D-bar by jump {dbar_jump:.5f}, by path average {dbar_avg:.5f}; 1-D student ramp "
          f"{res['student_1d']['ramp'][0]:+.4f}..{res['student_1d']['ramp'][1]:+.4f}, between crescents "
          f"{res['student_1d']['share_between']:.4f}", flush=True)
    return res


# -------------------------------------------------------------------------------- reference
def _ref_chunk(args):
    z, steps = args
    return rk4_endpoints(SMAX * z, steps)


def cache_dir():
    d = HERE / ".cache"
    d.mkdir(exist_ok=True)
    return d


def run_reference(workers):
    z = np.random.default_rng(2026).normal(size=(N_EVAL, N_PIX))
    path = cache_dir() / f"reference-{_SRC}.npz"
    if path.exists():
        f = np.load(path)
        ref, check = f["ref"], float(f["check"])
    else:
        chunks = np.array_split(z, workers)
        with ProcessPoolExecutor(max_workers=workers) as ex:
            ref = np.concatenate(list(ex.map(_ref_chunk, [(c, 2000) for c in chunks])))
            half = np.concatenate(list(ex.map(_ref_chunk, [(c, 1000) for c in chunks])))
        check = float(np.sqrt(((ref - half) ** 2).mean()))
        np.savez(path, ref=ref, check=check)
    data = sample_data(np.random.default_rng(32), N_EVAL)
    data2 = sample_data(np.random.default_rng(33), N_EVAL)
    res = {"n_eval": N_EVAL, "rk4_self_check": check, "swd_floor": swd(data, data2),
           "exact_endpoints": public(evaluate(ref, ref, data)), "solvers": {}}
    zt = torch.tensor(SMAX * z, dtype=torch.float32)
    for name, fn in (("ddim", ddim), ("dpmpp2m", dpmpp2m)):
        res["solvers"][name] = {str(N): public(evaluate(fn(denoise_t, zt, N), ref, data))
                                for N in (1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 64, 128)}
    print(f"  reference: RK4 self-check rms {check:.2e}; data-to-data sample distance {res['swd_floor']:.4f}; "
          f"exact endpoints {res['exact_endpoints']['swd']:.4f}", flush=True)
    for name in ("ddim", "dpmpp2m"):
        print(f"  reference {name:8s} " + " ".join(
            f"{N}:{v['err']:.3f}/{v['swd']:.3f}/{v['blend']:.2f}" for N, v in res["solvers"][name].items()
            if N in ("1", "2", "4", "8", "16", "32", "128")) + "   (calls: error / sample distance / blends)")
    return z, ref, data, res


# ---------------------------------------------------------------------------------- teacher
def train_teacher(steps, seed=0):
    """Regress a network onto the exact denoiser at log-uniform noise levels, with EDM's loss weight."""
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    net = Net()
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_schedule(steps, 200))
    for _ in range(steps):
        x0 = torch.tensor(sample_data(rng, 512), dtype=torch.float32)
        s = sample_sigma(512, gen)
        x = x0 + s * torch.randn(512, N_PIX, generator=gen)
        with torch.no_grad():
            tgt = denoise_t(x, s)
        c_in, c_skip, c_out = precond(s)
        loss = ((((c_skip * x + c_out * net(c_in * x, s)) - tgt) / c_out) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
    return net


# --------------------------------------------------------------------------------- students
def student_regression(init, pairs, steps, seed):
    """Luhman & Luhman: regress one call at sigma_max onto the teacher's endpoint for that noise."""
    gen = torch.Generator().manual_seed(seed)
    net = copy.deepcopy(init)
    opt = torch.optim.Adam(net.parameters(), lr=5e-4)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_schedule(steps))
    zp = torch.tensor(pairs[0], dtype=torch.float32)
    yp = torch.tensor(pairs[1], dtype=torch.float32)
    s80 = torch.full((512, 1), SMAX)
    for _ in range(steps):
        idx = torch.randint(0, len(zp), (512,), generator=gen)
        loss = ((D_net(net, SMAX * zp[idx], s80) - yp[idx]) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
    return net


def student_pd(init, steps, steps_last, seed, on_round):
    """Salimans & Ho, Algorithm 2: the student's target makes one student DDIM step land where two
    teacher DDIM steps land. Round 1's teacher is the exact denoiser on 64 steps; each student then
    becomes the next round's teacher."""
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed)
    teacher, student, N = None, copy.deepcopy(init), 32
    while N >= 1:
        sig_s = torch.tensor(grid(N), dtype=torch.float32)
        sig_t = torch.tensor(grid(2 * N), dtype=torch.float32)
        n_it = steps_last if N <= 2 else steps
        opt = torch.optim.Adam(student.parameters(), lr=2e-4)
        sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_schedule(n_it))
        if teacher is None:
            Dt = denoise_t
        else:
            Dt = lambda x, s, T=teacher: D_net(T, x, s)
        for _ in range(n_it):
            i = torch.randint(0, N, (512,), generator=gen)
            s, s2, sm = sig_s[i][:, None], sig_s[i + 1][:, None], sig_t[2 * i + 1][:, None]
            x0 = torch.tensor(sample_data(rng, 512), dtype=torch.float32)
            z = x0 + s * torch.randn(512, N_PIX, generator=gen)          # noised data, not teacher paths
            with torch.no_grad():
                d1 = Dt(z, s)
                zm = d1 + (sm / s) * (z - d1)
                d2 = Dt(zm, sm)
                z2 = d2 + (s2 / sm) * (zm - d2)
                r = s2 / s
                tgt = (z2 - r * z) / (1 - r)                              # invert one student DDIM step
            c_in, c_skip, c_out = precond(s)
            loss = ((((c_skip * z + c_out * student(c_in * z, s)) - tgt) / c_out) ** 2).mean()
            opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        on_round(N, student)
        teacher = copy.deepcopy(student).requires_grad_(False)
        N //= 2
    return student


def cm_levels(N=18):
    i = np.arange(N) / (N - 1)
    return (SMIN ** (1 / RHO) + i * (SMAX ** (1 / RHO) - SMIN ** (1 / RHO))) ** RHO


def student_cd(init, steps, seed, mu=0.95, boundary=True):
    """Song et al., Algorithm 2: one Heun step of the exact teacher from t_{n+1} to t_n, and the
    online network at t_{n+1} is trained to match the EMA target network at t_n. boundary=False
    swaps in the ordinary denoiser's preconditioning, which lacks c_out(SMIN) = 0 (exercise E4)."""
    kind = "cm" if boundary else "edm"
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed)
    net = copy.deepcopy(init)
    target = copy.deepcopy(net).requires_grad_(False)
    opt = torch.optim.Adam(net.parameters(), lr=2e-4)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_schedule(steps))
    t = torch.tensor(cm_levels(18), dtype=torch.float32)
    for _ in range(steps):
        n = torch.randint(0, 17, (512,), generator=gen)
        tn, tn1 = t[n][:, None], t[n + 1][:, None]
        x0 = torch.tensor(sample_data(rng, 512), dtype=torch.float32)
        x1 = x0 + tn1 * torch.randn(512, N_PIX, generator=gen)
        with torch.no_grad():
            d = (x1 - denoise_t(x1, tn1)) / tn1
            xe = x1 + (tn - tn1) * d
            d2 = (xe - denoise_t(xe, tn)) / tn
            xh = x1 + (tn - tn1) * 0.5 * (d + d2)                          # Heun, as Song et al. chose
            goal = D_net(target, xh, tn, kind)
        loss = ((D_net(net, x1, tn1, kind) - goal) ** 2).mean()
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        with torch.no_grad():
            for p, q in zip(target.parameters(), net.parameters()):
                p.mul_(mu).add_(q, alpha=1 - mu)
    return net


CM_SCHEDULES = {str(k): grid(k)[1:-1] for k in (1, 2, 3, 4, 8)}   # re-noise to the rho = 7 levels, not tuned


def cm_sample(net, z, taus, seed, kind="cm"):
    """Song et al., Algorithm 1: denoise to the end, add fresh noise at tau, denoise again."""
    gen = torch.Generator().manual_seed(seed)
    with torch.no_grad():
        x = D_net(net, SMAX * z, torch.full((z.shape[0], 1), SMAX), kind)
        for tau in taus:
            xn = x + math.sqrt(tau ** 2 - SMIN ** 2) * torch.randn(x.shape, generator=gen)
            x = D_net(net, xn, torch.full((z.shape[0], 1), tau), kind)
    return x


def student_dmd(init, steps, seed, n_fake=1, reg_w=0.0, pairs=None, warm=2000, trace_every=100):
    """Yin et al.: a one-step generator G(z) moved by the difference of two denoisers on noised
    outputs, the frozen teacher (here exact) and a 'fake' denoiser trained online on G's own samples.
    n_fake = 5 is DMD2's two time-scale rule; reg_w > 0 adds DMD's regression on teacher pairs.
    Before G's first update the fake denoiser takes `warm` updates on G's initial samples: started as
    a copy of the teacher, it otherwise drags every sample the same way at first."""
    gen = torch.Generator().manual_seed(seed)
    G, F = copy.deepcopy(init), copy.deepcopy(init)
    og = torch.optim.Adam(G.parameters(), lr=5e-5, betas=(0.0, 0.99))
    of = torch.optim.Adam(F.parameters(), lr=1e-4, betas=(0.0, 0.99))
    s80 = torch.full((256, 1), SMAX)
    lo, hi = math.log(0.02), math.log(SMAX)           # DMD's t in [0.02 T, 0.98 T], as noise levels
    if reg_w > 0:
        zr = torch.tensor(pairs[0], dtype=torch.float32)
        yr = torch.tensor(pairs[1], dtype=torch.float32)
    z_probe = torch.randn(1024, N_PIX, generator=torch.Generator().manual_seed(9))
    trace = []
    for it in range(steps):
        for _ in range(n_fake + (warm if it == 0 else 0)):   # the fake denoiser tracks G's samples
            with torch.no_grad():
                x = D_net(G, SMAX * torch.randn(256, N_PIX, generator=gen), s80)
            s = sample_sigma(256, gen)
            xt = x + s * torch.randn(256, N_PIX, generator=gen)
            c_in, c_skip, c_out = precond(s)
            lf = ((((c_skip * xt + c_out * F(c_in * xt, s)) - x) / c_out) ** 2).mean()
            of.zero_grad(); lf.backward(); of.step()
        z = torch.randn(256, N_PIX, generator=gen)
        x = D_net(G, SMAX * z, s80)
        s = torch.exp(lo + torch.rand(256, 1, generator=gen) * (hi - lo))
        with torch.no_grad():
            xt = x + s * torch.randn(256, N_PIX, generator=gen)
            d_real = denoise_t(xt, s)
            d_fake = D_net(F, xt, s)
            grad = (d_fake - d_real) / (d_real - x).abs().mean(1, keepdim=True)   # DMD's Eq. 7-8
        loss = 0.5 * ((x - (x - grad).detach()) ** 2).sum(1).mean()   # its gradient in x is exactly grad
        if reg_w > 0:
            idx = torch.randint(0, len(zr), (256,), generator=gen)
            loss = loss + reg_w * ((D_net(G, SMAX * zr[idx], s80) - yr[idx]) ** 2).sum(1).mean()
        og.zero_grad(); loss.backward(); og.step()
        if it % trace_every == 0 or it == steps - 1:
            with torch.no_grad():
                xs = one_step(G, z_probe).numpy()
            trace.append({"step": it, "brightness_mean": round(float(xs.mean()), 4),
                          "cover": (np.bincount(crescent_of(xs), minlength=K) / len(xs)).round(3).tolist()})
    return G, trace


def u_sig(u):
    """sigma at u in [0, 1] on the rho = 7 spacing, with sigma(1) = 0."""
    s = sig_u(torch.clamp(u, max=1.0))
    return torch.where(u >= 1.0 - 1e-9, torch.zeros_like(s), s)


def fm_jump(net, x, s, s2):
    """A flow-map jump written as one DDIM step: X = (s'/s) x + (1 - s'/s) Dbar(x, s, s')."""
    dbar = D_net(net, x, s, "edm", s2)
    return (s2 / s) * x + (1 - s2 / s) * dbar


def student_shortcut(steps, seed, M=128):
    """Frans et al.: one network, conditioned on the jump's end as well as its start. Three quarters
    of each batch learn the plain denoiser from data (jump of size 0, no teacher); a quarter learn a
    jump of size 2d as two jumps of size d made by an EMA copy of the network itself."""
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    net = Net(two=True)
    ema = copy.deepcopy(net).requires_grad_(False)
    opt = torch.optim.AdamW(net.parameters(), lr=2e-3, weight_decay=0.1)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_schedule(steps))
    levels = int(math.log2(M))
    for _ in range(steps):
        x0 = torch.tensor(sample_data(rng, 384), dtype=torch.float32)
        s = u_sig(torch.rand(384, 1, generator=gen)).clamp(min=SMIN)
        xt = x0 + s * torch.randn(384, N_PIX, generator=gen)
        c_in, c_skip, c_out = precond(s)
        l_emp = ((((c_skip * xt + c_out * net(c_in * xt, s, s)) - x0) / c_out) ** 2).mean()
        k = torch.randint(1, levels + 1, (128, 1), generator=gen).float()
        d = 2.0 ** (-k)
        u0 = torch.floor(torch.rand(128, 1, generator=gen) * (1.0 / (2 * d)).round()) * 2 * d
        s0, s1, s2 = u_sig(u0), u_sig(u0 + d), u_sig(u0 + 2 * d)
        xs = torch.tensor(sample_data(rng, 128), dtype=torch.float32) + s0 * torch.randn(128, N_PIX, generator=gen)
        with torch.no_grad():
            small = k == levels                        # the smallest jump: ask the size-0 head
            xa = torch.where(small, _head_step(ema, xs, s0, s1), fm_jump(ema, xs, s0, s1))
            xb = torch.where(small, _head_step(ema, xa, s1, s2), fm_jump(ema, xa, s1, s2))
            r = s2 / s0
            tgt = (xb - r * xs) / (1 - r)
        c_in, c_skip, c_out = precond(s0)
        l_sc = ((((c_skip * xs + c_out * net(c_in * xs, s0, s2)) - tgt) / c_out) ** 2).mean()
        loss = 0.75 * l_emp + 0.25 * l_sc
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
        with torch.no_grad():
            for p, q in zip(ema.parameters(), net.parameters()):
                p.mul_(0.999).add_(q, alpha=0.001)
    return ema


def _head_step(net, x, s, s2):
    """One DDIM step with the size-0 head, which is the plain denoiser."""
    d0 = D_net(net, x, s, "edm", s)
    return (s2 / s) * x + (1 - s2 / s) * d0


def shortcut_sample(net, z, n):
    with torch.no_grad():
        x = SMAX * z
        for j in range(n):
            s = u_sig(torch.full((z.shape[0], 1), j / n))
            s2 = u_sig(torch.full((z.shape[0], 1), (j + 1) / n))
            x = fm_jump(net, x, s, s2)
    return x


# ---------------------------------------------------------------------------------- jobs
def _job(args):
    """One student (one seed): train, evaluate, cache the network and its numbers."""
    name, seed, budget, cfg = args
    path = cache_dir() / f"{name}-s{seed}-{budget['tag']}-{_SRC}.json"
    if path.exists():
        return json.loads(path.read_text())
    torch.manual_seed(seed)
    f = np.load(cache_dir() / f"eval-{_SRC}.npz")
    z = torch.tensor(f["z"], dtype=torch.float32)
    ref, data = f["ref"], f["data"]
    m = margins(f["z"])
    init = Net()
    init.load_state_dict(torch.load(cache_dir() / f"teacher-{budget['tag']}-{_SRC}.pt"))
    out = {"name": name, "seed": seed, "steps": {}}
    t0 = time.time()

    def record(key, samples, margin=True):
        ev = evaluate(samples, ref, data)
        out["steps"][key] = public(ev)
        if margin:
            out["steps"][key]["flip_by_margin"] = by_margin(ev["_flip_mask"], m)
            out["steps"][key]["blend_by_margin"] = by_margin(ev["_blend_mask"], m)

    if name == "regression":
        pairs = np.load(cache_dir() / f"pairs-{budget['tag']}-{_SRC}.npz")
        net = student_regression(init, (pairs["z"], pairs["y"]), budget["regression"], seed)
        record("1", one_step(net, z))
    elif name == "pd":
        def on_round(N, student):
            record(str(N), ddim(lambda x, s: D_net(student, x, s), SMAX * z, N))
            out.setdefault("round_seconds", []).append(round(time.time() - t0, 1))
            if N == 1:
                torch.save(student.state_dict(), cache_dir() / f"pd1-s{seed}-{budget['tag']}-{_SRC}.pt")
            if N == 4:
                torch.save(student.state_dict(), cache_dir() / f"pd4-s{seed}-{budget['tag']}-{_SRC}.pt")
        net = student_pd(init, budget["pd"], budget["pd_last"], seed, on_round)
    elif name == "cd":
        net = student_cd(init, budget["cd"], seed)
        for n, taus in CM_SCHEDULES.items():
            record(n, cm_sample(net, z, taus, 77 + seed), margin=(n == "1"))
    elif name.startswith("dmd"):
        nf, rw = cfg
        pairs = None
        if rw > 0:
            p = np.load(cache_dir() / f"pairs-{budget['tag']}-{_SRC}.npz")
            pairs = (p["z"], p["y"])
        net, trace = student_dmd(init, budget["dmd"], seed, n_fake=nf, reg_w=rw, pairs=pairs)
        record("1", one_step(net, z))
        out["trace"] = trace
    elif name == "shortcut":
        net = student_shortcut(budget["shortcut"], seed)
        for n in (1, 2, 4, 8, 16, 32, 64, 128):
            record(str(n), shortcut_sample(net, z, n), margin=(n == 1))
    out["seconds"] = round(time.time() - t0, 1)
    torch.save(net.state_dict(), cache_dir() / f"{name}-s{seed}-{budget['tag']}-{_SRC}.pt")
    path.write_text(json.dumps(out))
    return out


STUDENTS = {"regression": None, "pd": None, "cd": None, "dmd_1to1": (1, 0.0), "dmd_5to1": (5, 0.0),
            "dmd_regression": (1, 0.25), "shortcut": None}
LABEL = {"regression": "direct regression", "pd": "progressive distillation", "cd": "consistency distillation",
         "dmd_1to1": "DMD, 1:1 updates", "dmd_5to1": "DMD, 5:1 updates (DMD2's rule)",
         "dmd_regression": "DMD + regression loss", "shortcut": "shortcut model"}


def budgets(quick):
    if quick:
        return {"tag": "quick", "teacher": 4000, "pairs": 8192, "regression": 2000, "pd": 800, "pd_last": 1600,
                "cd": 2500, "dmd": 1600, "shortcut": 8000}
    return {"tag": "full", "teacher": 20000, "pairs": 32768, "regression": 10000, "pd": 4000, "pd_last": 8000,
            "cd": 12000, "dmd": 8000, "shortcut": 40000}


def run_teacher_and_pairs(budget, z, ref, data, workers):
    """Train (or load) the warm-start network; compute (or load) the teacher's noise-image pairs."""
    np.savez(cache_dir() / f"eval-{_SRC}.npz", z=z, ref=ref, data=data)
    tpath = cache_dir() / f"teacher-{budget['tag']}-{_SRC}.pt"
    t0 = time.time()
    if not tpath.exists():
        torch.save(train_teacher(budget["teacher"]).state_dict(), tpath)
    net = Net()
    net.load_state_dict(torch.load(tpath))
    zt = torch.tensor(SMAX * z, dtype=torch.float32)
    res = {"steps": budget["teacher"], "seconds": round(time.time() - t0, 1), "ddim": {}}
    for N in (8, 16, 32, 64, 128):
        res["ddim"][str(N)] = public(evaluate(ddim(lambda x, s: D_net(net, x, s), zt, N), ref, data))
    rng = np.random.default_rng(7)
    x0 = sample_data(rng, 4096)
    res["denoiser_rms"] = {}
    with torch.no_grad():
        for s in (0.1, 1.0, 2.0, 5.0, 20.0, 80.0):
            x = torch.tensor(x0 + s * rng.normal(size=x0.shape), dtype=torch.float32)
            st = torch.full((4096, 1), s)
            res["denoiser_rms"][str(s)] = round(float((D_net(net, x, st) - denoise_t(x, st)).pow(2).mean().sqrt()), 5)
    ppath = cache_dir() / f"pairs-{budget['tag']}-{_SRC}.npz"
    if not ppath.exists():
        zp = np.random.default_rng(11).normal(size=(budget["pairs"], N_PIX))
        with ProcessPoolExecutor(max_workers=workers) as ex:
            yp = np.concatenate(list(ex.map(_ref_chunk, [(c, 1000) for c in np.array_split(zp, workers)])))
        np.savez(ppath, z=zp, y=yp)
    print(f"  teacher network: {budget['teacher']} steps; error against the exact denoiser at sigma 1 / 2 / 80: "
          + " / ".join(f"{res['denoiser_rms'][k]:.4f}" for k in ("1.0", "2.0", "80.0"))
          + f"; its DDIM at 128 calls: error {res['ddim']['128']['err']:.4f}, flips {res['ddim']['128']['flip']:.4f}", flush=True)
    return res


def run_dmd_probe(budget, ratio, warm, steps, seed):
    """One distribution-matching student with a chosen critic ratio and warm-up (exercise E4)."""
    f = np.load(cache_dir() / f"eval-{_SRC}.npz")
    init = Net()
    init.load_state_dict(torch.load(cache_dir() / f"teacher-{budget['tag']}-{_SRC}.pt"))
    G, trace = student_dmd(init, steps, seed, n_fake=ratio, warm=warm, trace_every=250)
    ev = public(evaluate(one_step(G, torch.tensor(f["z"], dtype=torch.float32)), f["ref"], f["data"]))
    for row in trace:
        print(f"  dmd probe ratio {ratio}:1, warm-up {warm}: step {row['step']:5d} cover {row['cover']}", flush=True)
    print(f"  dmd probe final: flips {ev['flip']:.4f}, blends {ev['blend']:.4f}, sample distance {ev['swd']:.4f}, "
          f"cover {ev['cover']}", flush=True)
    return {"ratio": ratio, "warm": warm, "steps": steps, "seed": seed, "trace": trace, "final": ev}


def run_students(budget, workers, seeds):
    jobs = [(name, s, budget, cfg) for name, cfg in STUDENTS.items() for s in seeds]
    jobs.sort(key=lambda j: {"pd": 0, "shortcut": 1, "cd": 2, "dmd_5to1": 3}.get(j[0], 4))   # longest first
    res = {}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for out in ex.map(_job, jobs):
            res.setdefault(out["name"], {})[str(out["seed"])] = out
            one = out["steps"].get("1")
            print(f"  student {LABEL[out['name']]:30s} seed {out['seed']}: 1 call: flips {one['flip']:.4f}, "
                  f"blends {one['blend']:.4f}, error {one['err']:.4f}, sample distance {one['swd']:.4f}, "
                  f"cover {one['cover']} ({out['seconds']:.0f} s)", flush=True)
    for name in ("pd", "cd", "shortcut"):
        for seed, out in res[name].items():
            print(f"  student {LABEL[name]:30s} seed {seed}: " + " ".join(
                f"{n}:{v['flip']:.3f}/{v['swd']:.3f}" for n, v in sorted(out["steps"].items(), key=lambda kv: int(kv[0])))
                + "   (calls: flips / sample distance)", flush=True)
    return res


# -------------------------------------------------------------------------------- samples
def run_samples(budget, z, ref, seeds):
    """Six starting noises, three near a decision boundary and three far from one, through every method."""
    m = margins(z)
    near = [i for i in np.argsort(m) if m[i] < 0.02][:3]
    far = [i for i in range(len(m)) if m[i] > 0.8][:3]
    idx = [int(i) for i in near + far]
    zs = torch.tensor(z[idx], dtype=torch.float32)
    s = seeds[0]
    out = {"index": idx, "margin": [round(float(m[i]), 4) for i in idx], "exact": np.round(ref[idx], 3).tolist(), "methods": {}}

    def load(name, two=False):
        net = Net(two=two)
        net.load_state_dict(torch.load(cache_dir() / f"{name}-s{s}-{budget['tag']}-{_SRC}.pt"))
        return net

    put = lambda key, x: out["methods"].__setitem__(key, np.round(x.numpy(), 3).tolist())
    put("ddim_1", ddim(denoise_t, SMAX * zs, 1))
    put("ddim_4", ddim(denoise_t, SMAX * zs, 4))
    put("regression_1", one_step(load("regression"), zs))
    put("pd_1", one_step(load("pd1"), zs))
    put("pd_4", ddim(lambda x, sg, n=load("pd4"): D_net(n, x, sg), SMAX * zs, 4))
    put("cd_1", cm_sample(load("cd"), zs, [], 77 + s))
    put("cd_2", cm_sample(load("cd"), zs, CM_SCHEDULES["2"], 77 + s))
    put("shortcut_1", shortcut_sample(load("shortcut", True), zs, 1))
    put("shortcut_4", shortcut_sample(load("shortcut", True), zs, 4))
    for name in ("dmd_1to1", "dmd_5to1", "dmd_regression"):
        put(name + "_1", one_step(load(name), zs))
    print(f"  samples: noises {idx} with margins {out['margin']}", flush=True)
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
            "cpu": cpu, "cores": os.cpu_count(), "python": sys.version.split()[0], "numpy": np.__version__,
            "torch": torch.__version__}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["worked", "reference", "teacher", "students", "samples", "all", "dmd"])
    ap.add_argument("--quick", action="store_true", help="shorter training, about 6 minutes in all")
    ap.add_argument("--seeds", type=int, default=2, help="seeds per student (default 2)")
    ap.add_argument("--workers", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--out", default=str(HERE / "captures.json"))
    ap.add_argument("--x", type=float, default=40.0, help="worked: where the 4 -> 2 halving starts (default 40)")
    ap.add_argument("--ratio", type=int, default=1, help="dmd: fake-denoiser updates per generator update")
    ap.add_argument("--warm", type=int, default=2000, help="dmd: fake-denoiser updates before the first generator update")
    ap.add_argument("--steps", type=int, default=3000, help="dmd: generator updates")
    ap.add_argument("--seed", type=int, default=1, help="dmd: seed")
    args = ap.parse_args()
    prov = provenance()
    print(f"Captured {prov['captured_utc']} on {prov['cpu']} ({prov['cores']} cores), {prov['os']}, "
          f"Python {prov['python']}, numpy {prov['numpy']}, torch {prov['torch']}" + (" [quick]" if args.quick else ""))
    out_path = Path(args.out)
    cap = json.loads(out_path.read_text()) if out_path.exists() and args.what != "all" else {}
    cap["provenance"] = {**prov, "quick": args.quick, "seeds": args.seeds, "source_sha1": _SRC}
    budget = budgets(args.quick)
    seeds = list(range(1, args.seeds + 1))
    t0 = time.time()

    def timed(name, fn):
        t = time.time()
        r = fn()
        print(f"  [{name} took {time.time() - t:.0f} s]", flush=True)
        return r

    if args.what in ("worked", "all"):
        cap["worked"] = timed("worked", lambda: run_worked(args.x))
    if args.what != "worked":
        z, ref, data, rres = timed("reference", lambda: run_reference(args.workers))
        cap["reference"] = rres
        if args.what in ("teacher", "students", "samples", "all", "dmd"):
            cap["teacher"] = timed("teacher", lambda: run_teacher_and_pairs(budget, z, ref, data, args.workers))
        if args.what in ("students", "all"):
            cap["students"] = timed("students", lambda: run_students(budget, args.workers, seeds))
        if args.what in ("samples", "all"):
            cap["samples"] = timed("samples", lambda: run_samples(budget, z, ref, seeds))
        if args.what == "dmd":
            cap["dmd_probe"] = timed("dmd", lambda: run_dmd_probe(budget, args.ratio, args.warm, args.steps, args.seed))
    m = margins(np.random.default_rng(2026).normal(size=(N_EVAL, N_PIX)))
    cap["margin_bins"] = MARGIN_BINS
    cap["margin_share"] = [round(float(((m >= lo) & (m < hi)).mean()), 4) for lo, hi in zip(MARGIN_BINS[:-1], MARGIN_BINS[1:])]
    out_path.write_text(json.dumps(cap, indent=1))
    print(f"wrote {os.path.relpath(out_path)} in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
