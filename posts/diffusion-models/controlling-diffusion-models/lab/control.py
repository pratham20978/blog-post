#!/usr/bin/env python3
"""Lab for "Controlling Diffusion Models" (Diffusion Models series, part 8).

Crescent world again, with a contrast dial: every image shows one of four crescents (the class), and
each crescent comes faint or strong, half and half. Its unconditional and class-conditional denoisers
E[x0 | x] and E[x0 | x, class] have closed forms, so every control method can be run against an exact
model before it is run against a network trained the way real models are trained.

  worked      one number, the requested crescent's contrast, in closed form: the guided denoiser at
              x = 40, sigma = 80, one DDIM step, and the faint share that guidance leaves (about 5 s)
  exact       classifier-free guidance on the exact 64-pixel model: a weight sweep, and guidance that
              is switched on only above or only below a noise level
  networks    a conditional network trained with label dropout, and a weaker copy trained a quarter as
              long; guidance, autoguidance, guidance intervals, CFG-rescale and APG on them (2 seeds)
  controlnet  a ControlNet branch on the frozen network, steered by a 4x4 layout, zero- vs
              Gaussian-initialised connectors, measured over training
  personal    teaching the frozen network one new subject from 5 images: textual inversion, LoRA and
              full fine-tuning, with and without prior preservation
  inpaint     filling in the right half of an image: the exact posterior, replacement, RePaint-style
              resampling, and a network fine-tuned with mask inputs
  edit        changing an image's class: SDEdit at nine noise levels against DDIM inversion
  census      trainable parameters of each control method on Stable Diffusion 1.5 (needs diffusers)
  all         everything except census, in that order

Every sample lives in the coordinates of parts 5 to 7: x = x0 + sigma * eps, sigma from 80 to 0.

Run:   python control.py all              # the article's run (timings are in the README)
       python control.py all --quick      # shorter training, noisier numbers
       python control.py worked --w 2     # the worked example at another guidance weight
       python control.py personal --quick --method full --steps 1000    # one fine-tune: the run E4 diagnoses
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
import torch.nn.functional as F

torch.set_num_threads(1)
HERE = Path(__file__).resolve().parent
K = 4                                   # crescent orientations: the classes
A_C, S_B, TAU = 0.9, 0.3, 0.1           # strong crescent RMS amplitude, brightness spread, detail noise
AMPS = (0.5, 1.0)                       # faint and strong contrast, as fractions of a strong crescent
P_FAINT = 0.5                           # half of each class is faint
S_A = 0.06                              # contrast jitter within each sub-mode
R = 8                                   # image side; 64 pixels
N_PIX = R * R
SMAX, SMIN, RHO = 80.0, 0.002, 7.0      # EDM's noise range and step spacing
N_EVAL = 4096                           # starting noises per evaluated setting
WIDTH = 256                             # hidden width of every network
NULL = K                                # the empty prompt's token


# --------------------------------------------------------------------------- crescent world
def crescent_shape(r=R, inner=(0.64, 0.42, 0.30), supersample=8):
    """A zero-mean crescent: a disc minus an offset disc, scaled to RMS amplitude A_C."""
    g = (np.arange(r * supersample) + 0.5) / (r * supersample)
    yy, xx = np.meshgrid(g, g, indexing="ij")
    outer = (xx - 0.5) ** 2 + (yy - 0.5) ** 2 < 0.36 ** 2
    hole = (xx - inner[0]) ** 2 + (yy - inner[1]) ** 2 < inner[2] ** 2
    m = (outer & ~hole).astype(float).reshape(r, supersample, r, supersample).mean(axis=(1, 3))
    return m


def unit(m):
    m = m.reshape(-1) - m.mean()
    return m * A_C / np.sqrt((m ** 2).mean())


MU = np.stack([unit(np.rot90(crescent_shape(), k)) for k in range(K)])    # (K, 64), equal norms
NORM = float(np.linalg.norm(MU[0]))                                        # 7.2
MU_HAT = MU / NORM
MU_V = unit(crescent_shape(inner=(0.58, 0.45, 0.31)))     # part 8's new subject: a thinner crescent 0
V_E = S_B ** 2 * N_PIX + TAU ** 2                          # data variance along the brightness axis
LAM = TAU ** 2 + (S_A * NORM) ** 2                         # data variance along a component's own crescent
SIGMA_DATA = math.sqrt(A_C ** 2 * ((1 - P_FAINT) * AMPS[1] ** 2 + P_FAINT * AMPS[0] ** 2) + S_B ** 2 + TAU ** 2)
SPREAD = math.sqrt(S_A ** 2 + (TAU / NORM) ** 2)           # contrast spread of one sub-mode: 0.0616
OVER = AMPS[1] + 3 * SPREAD                                 # contrast no real strong crescent exceeds (1.185)
MID = ((AMPS[0] + 3 * SPREAD), (AMPS[1] - 3 * SPREAD))      # contrasts no real crescent has (0.685..0.815)


def sample_data(rng, n, cls=None):
    """x0 = a mu_k + b 1 + tau z, with k uniform (or fixed), a faint or strong (+ jitter), b ~ N(0, s_b^2)."""
    k = rng.integers(0, K, n) if cls is None else np.full(n, cls)
    j = (rng.random(n) >= P_FAINT).astype(int)            # 0 faint, 1 strong
    a = np.array(AMPS)[j] + S_A * rng.normal(size=n)
    b = rng.normal(0.0, S_B, n)
    return a[:, None] * MU[k] + b[:, None] + TAU * rng.normal(size=(n, N_PIX)), k, j


def sample_subject(rng, n):
    a = AMPS[1] + S_A * rng.normal(size=n)
    b = rng.normal(0.0, S_B, n)
    return a[:, None] * MU_V + b[:, None] + TAU * rng.normal(size=(n, N_PIX))


def components(cls):
    return [(k, j) for k in (range(K) if cls is None else [cls]) for j in (0, 1)]


def denoise(x, s, cls=None):
    """Exact D(x; s) = E[x0 | x0 + s eps = x], or E[x0 | x, class cls], in float64 for a scalar s.
    Each sub-mode is a Gaussian whose covariance has three eigenvalues: V_E along the brightness axis,
    LAM along its own crescent and TAU^2 elsewhere, so the posterior is a softmax over sub-modes."""
    s2 = s * s
    p = x.mean(1, keepdims=True)
    u = x @ MU_HAT.T
    a_o, a_k, a_e = TAU ** 2 / (TAU ** 2 + s2), LAM / (LAM + s2), V_E / (V_E + s2)
    comps = components(cls)
    logits = np.stack([-0.5 * ((u[:, k] - AMPS[j] * NORM) ** 2 / (LAM + s2) - u[:, k] ** 2 / (TAU ** 2 + s2))
                       + math.log(P_FAINT if j == 0 else 1 - P_FAINT) for k, j in comps], 1)
    logits -= logits.max(1, keepdims=True)
    w = np.exp(logits)
    w /= w.sum(1, keepdims=True)
    out = a_o * (x - p) + a_e * p
    for i, (k, j) in enumerate(comps):
        m = AMPS[j] * NORM
        out += w[:, i:i + 1] * ((m + a_k * (u[:, k] - m) - a_o * u[:, k])[:, None] * MU_HAT[k])
    return out


def sig_u(u):
    return (SMAX ** (1 / RHO) + u * (SMIN ** (1 / RHO) - SMAX ** (1 / RHO))) ** RHO


def grid(n):
    """n DDIM steps on EDM's rho = 7 spacing: the levels sigma(i/n) for i < n, then 0."""
    return [float(sig_u(i / n)) for i in range(n)] + [0.0]


# -------------------------------------------------------------------------------- metrics
def swd(a, b, n_dir=256, seed=5):
    """Sliced Wasserstein distance between two sample sets (part 5's instrument). Unequal sizes are
    compared at matched quantiles of the smaller set."""
    d = np.random.default_rng(seed).normal(size=(a.shape[1], n_dir))
    d /= np.linalg.norm(d, axis=0, keepdims=True)
    pa, pb = np.sort(a @ d, 0), np.sort(b @ d, 0)
    if len(pa) != len(pb):
        n = min(len(pa), len(pb))
        q = (np.arange(n) + 0.5) / n
        pa, pb = np.quantile(pa, q, axis=0), np.quantile(pb, q, axis=0)
    return float(np.sqrt(((pa - pb) ** 2).mean()))


def contrast(x, cls=None):
    """Which crescent a sample shows, and how strongly, as a fraction of a strong crescent."""
    c = (x - x.mean(1, keepdims=True)) @ MU_HAT.T / NORM
    shown = np.argmax(c, 1)
    amp = c[np.arange(len(x)), shown if cls is None else np.full(len(x), cls)]
    return shown, amp


def _kth(a, b, k, chunk=1024, same=False):
    """k-th nearest distance from each row of a to the rows of b (excluding itself when same)."""
    out = np.empty(len(a))
    bb = (b ** 2).sum(1)
    for i in range(0, len(a), chunk):
        aa = a[i:i + chunk]
        d = (aa ** 2).sum(1)[:, None] + bb[None] - 2 * aa @ b.T
        out[i:i + chunk] = np.sqrt(np.maximum(np.sort(d, 1)[:, k if same else k - 1], 0))
    return out


def _covered(a, b, radii_b, chunk=1024):
    """Share of rows of a that fall inside at least one hypersphere around the rows of b."""
    inside = 0
    bb = (b ** 2).sum(1)
    for i in range(0, len(a), chunk):
        aa = a[i:i + chunk]
        d = np.sqrt(np.maximum((aa ** 2).sum(1)[:, None] + bb[None] - 2 * aa @ b.T, 0))
        inside += int((d <= radii_b[None]).any(1).sum())
    return inside / len(a)


_RADII = {}


def precision_recall(gen, real, k=3):
    """Kynkaanniemi et al.'s improved precision and recall, with k = 3, on the 64 pixel values."""
    key = (real.shape, float(real[0, 0]), float(real[-1, -1]), k)
    if key not in _RADII:
        _RADII[key] = _kth(real, real, k, same=True)
    return _covered(gen, real, _RADII[key]), _covered(real, gen, _kth(gen, gen, k, same=True))


def stats(x, cls, real, pr=True):
    """Everything the article reads off one set of class-cls samples."""
    shown, amp = contrast(x, cls)
    st = {"accuracy": float((shown == cls).mean()),
          "faint": float((amp < 0.75).mean()),
          "blend": float(((amp > MID[0]) & (amp < MID[1])).mean()),
          "over": float((amp > OVER).mean()),
          "strong_contrast": float(amp[amp >= 0.75].mean()) if (amp >= 0.75).any() else None,
          "brightness_sd": float(x.mean(1).std()),
          "swd": swd(x, real)}
    if pr:
        st["precision"], st["recall"] = precision_recall(x, real)
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in st.items()}


# --------------------------------------------------------------------------------- worked
WORKED_MODES = (-AMPS[1] * NORM, -AMPS[0] * NORM, AMPS[0] * NORM, AMPS[1] * NORM)   # -7.2 -3.6 3.6 7.2
WORKED_SD = math.sqrt(LAM)                                                            # 0.4434


def d1(x, s, cls):
    """The one-number world: the requested crescent's contrast, in the units of sigma. Class +1 sits at
    3.6 or 7.2, class -1 (the crescent pointing the other way) at -3.6 or -7.2, each with spread 0.443.
    cls = 0 is the unconditional denoiser over all four sub-modes."""
    modes = [m for m in WORKED_MODES if cls == 0 or np.sign(m) == cls]
    v = LAM + s * s
    lg = np.stack([-(x - m) ** 2 / (2 * v) for m in modes], -1)
    lg -= lg.max(-1, keepdims=True)
    w = np.exp(lg)
    w /= w.sum(-1, keepdims=True)
    return sum(w[..., i] * (m + (LAM / v) * (x - m)) for i, m in enumerate(modes))


def d1_guided(x, s, w):
    du = d1(x, s, 0)
    return du + w * (d1(x, s, 1) - du)


def ode1d(x, w, steps=4000, s_from=SMAX):
    """The guided probability-flow ODE dx/du = x - D_w(x, e^u), u = log sigma, by RK4, then D at SMIN."""
    u0, u1 = math.log(s_from), math.log(SMIN)
    h = (u1 - u0) / steps
    u = u0
    f = lambda xx, uu: xx - d1_guided(xx, math.exp(uu), w)
    for _ in range(steps):
        k1 = f(x, u); k2 = f(x + 0.5 * h * k1, u + 0.5 * h)
        k3 = f(x + 0.5 * h * k2, u + 0.5 * h); k4 = f(x + h * k3, u + h)
        x = x + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        u += h
    return d1_guided(x, SMIN, w)


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


PATH_EPS = (-2.2, -1.9, -1.5, -1.0, -0.6, -0.3, -0.1, 0.0, 0.05, 0.1, 0.3, 0.6, 1.0, 1.5, 2.0)


def run_worked(w_main=3.0):
    x, s, s2 = 40.0, SMAX, grid(4)[1]
    du, dc = float(d1(np.array([x]), s, 0)[0]), float(d1(np.array([x]), s, 1)[0])
    dw = du + w_main * (dc - du)
    step = lambda d: d + (s2 / s) * (x - d)
    res = {"x": x, "sigma": s, "sigma_next": round(s2, 4), "modes": [round(m, 4) for m in WORKED_MODES],
           "spread": round(WORKED_SD, 4), "w": w_main, "D_uncond": round(du, 4), "D_cond": round(dc, 4),
           "D_guided": round(dw, 4), "step_uncond": round(step(du), 4), "step_cond": round(step(dc), 4),
           "step_guided": round(step(dw), 4), "weights": {}}
    # The ODE is monotone in its start, so the faint share of class +1 is Phi(eps*), with eps* the
    # starting noise whose path ends on the faint/strong boundary at contrast 5.4; found by bisection.
    cut = 0.5 * (AMPS[0] + AMPS[1]) * NORM                  # contrast 5.4: halfway between faint and strong
    probe = (-0.5, 0.0, 0.1, 0.5)
    prior = np.linspace(-6.0, 6.0, 1201)                       # starting noises, weighted by their density
    dens = np.exp(-0.5 * prior ** 2)
    for w in (1.0, 1.5, 2.0, 3.0, 5.0, 7.5):
        e = np.linspace(-15.0, 15.0, 241)                      # bracket the boundary, then refine it three times
        for _ in range(4):
            ends = ode1d(SMAX * e, w, steps=2000)
            i = int(np.flatnonzero((ends[:-1] < cut) & (ends[1:] >= cut))[0])
            if _ < 3:
                e = np.linspace(e[i], e[i + 1], 101)
        e_star = float(e[i] + (cut - ends[i]) / (ends[i + 1] - ends[i]) * (e[i + 1] - e[i]))
        ends_p = ode1d(SMAX * prior, w, steps=2000)
        strong = ends_p >= cut
        at = ode1d(SMAX * np.array(probe), w, steps=2000)
        res["weights"][str(w)] = {"eps_boundary": round(e_star, 5), "faint_share": float(f"{norm_cdf(e_star):.4g}"),
                                  "mean_strong_end": round(float((ends_p * dens)[strong].sum() / dens[strong].sum()), 4),
                                  "end_at_eps": {str(e0): round(float(v), 4) for e0, v in zip(probe, at)}}
    # the paths themselves, for the figure: 15 starting noises, two of them below w = 3's boundary
    taus = [float(sig_u(i / 200)) for i in range(200)] + [SMIN]
    paths = {"eps": list(PATH_EPS)}
    for w in (1.0, w_main):
        xs = SMAX * np.array(PATH_EPS)
        rows = [xs.copy()]
        for a, b in zip(taus[:-1], taus[1:]):            # fine DDIM steps: visually the exact path
            d = d1_guided(xs, a, w)
            xs = d + (b / a) * (xs - d)
            rows.append(xs.copy())
        paths[str(w)] = {"sigma": [round(t, 5) for t in taus], "x": np.round(np.array(rows).T, 4).tolist()}
    res["paths"] = paths
    wm = res["weights"]
    print(f"  worked: x=40, sigma=80: D_uncond {du:.3f}, D_cond {dc:.3f}, guided (w={w_main:g}) {dw:.3f}; "
          f"one DDIM step to {s2:.2f}: {step(du):.2f} / {step(dc):.2f} / {step(dw):.2f}", flush=True)
    print("  worked: faint share of class +1 by weight: " + "  ".join(
        f"w={k} {v['faint_share']:.3f} (eps* {v['eps_boundary']:+.4f})" for k, v in wm.items()), flush=True)
    return res


# ---------------------------------------------------------------------------- exact model
def sample_exact(z, cls, w=1.0, n=128, on=None):
    """DDIM on the exact denoisers with classifier-free guidance at weight w; on(sigma) says whether
    guidance is active at that step (the guidance-interval experiments)."""
    x = SMAX * z
    g = grid(n)
    for s, s2 in zip(g[:-1], g[1:]):
        dc = denoise(x, s, cls)
        if w != 1.0 and (on is None or on(s)):
            du = denoise(x, s)
            d = du + w * (dc - du)
        else:
            d = dc
        x = d + (s2 / s) * (x - d)
    return x


CUTS = (40.0, 20.0, 10.0, 5.0, 3.0, 2.0, 1.4, 1.0, 0.7, 0.5, 0.3, 0.2, 0.1, 0.05)


def _exact_job(args):
    kind, val, z, real = args
    if kind == "w":
        x = sample_exact(z, 0, val)
    elif kind == "above":                     # guidance at w = 3 only for sigma > val
        x = sample_exact(z, 0, 3.0, on=lambda s, c=val: s > c)
    else:                                     # guidance at w = 3 only for sigma <= val
        x = sample_exact(z, 0, 3.0, on=lambda s, c=val: s <= c)
    return kind, val, stats(x, 0, real, pr=(kind == "w"))


def run_exact(workers, quick):
    n = 2048 if quick else N_EVAL
    z = np.random.default_rng(2026).normal(size=(n, N_PIX))
    real = sample_data(np.random.default_rng(31), n, 0)[0]
    real2 = sample_data(np.random.default_rng(32), n, 0)[0]
    res = {"n": n, "data": stats(real2, 0, real), "weights": {}, "above": {}, "below": {}}
    jobs = [("w", w, z, real) for w in (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.5)]
    jobs += [("above", c, z, real) for c in CUTS] + [("below", c, z, real) for c in CUTS]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for kind, val, st in ex.map(_exact_job, jobs):
            res["weights" if kind == "w" else kind][str(val)] = st
    d = res["data"]
    print(f"  exact data: faint {d['faint']:.3f}, blends {d['blend']:.4f}, over {d['over']:.4f}, "
          f"precision {d['precision']:.3f}, recall {d['recall']:.3f}, distance {d['swd']:.4f} (two real sets)", flush=True)
    for w, st in res["weights"].items():
        print(f"  exact cfg w={w:>4}: faint {st['faint']:.3f}, over {st['over']:.4f}, strong contrast "
              f"{st['strong_contrast']:.3f}, brightness sd {st['brightness_sd']:.3f}, precision {st['precision']:.3f}, "
              f"recall {st['recall']:.3f}, distance {st['swd']:.4f}", flush=True)
    print("  exact guidance only above sigma: " + " ".join(f"{c}:{res['above'][str(c)]['faint']:.2f}" for c in CUTS)
          + "   (faint share)", flush=True)
    print("  exact guidance only below sigma: " + " ".join(f"{c}:{res['below'][str(c)]['faint']:.2f}" for c in CUTS)
          + "   (faint share)", flush=True)
    return res


# --------------------------------------------------------------------------------- networks
def precond(s):
    """EDM's preconditioning (Karras et al., Table 1)."""
    sd2 = SIGMA_DATA ** 2
    return 1.0 / torch.sqrt(s * s + sd2), sd2 / (s * s + sd2), s * SIGMA_DATA / torch.sqrt(s * s + sd2)


class Fourier(nn.Module):
    def __init__(self, n=16):
        super().__init__()
        self.register_buffer("f", 2.0 ** torch.linspace(-1, 5, n))

    def forward(self, c):
        a = c * self.f
        return torch.cat([torch.sin(a), torch.cos(a)], 1)


class Net(nn.Module):
    """F(c_in x, embed(ln sigma / 4), embed(token)): three hidden layers of WIDTH. Tokens 0..3 are the
    classes and token 4 the empty prompt, which label dropout trains."""

    def __init__(self, width=WIDTH, emb=32):
        super().__init__()
        self.emb = Fourier(16)
        self.cls = nn.Embedding(K + 1, emb)
        self.f = nn.Sequential(nn.Linear(N_PIX + 32 + emb, width), nn.SiLU(), nn.Linear(width, width), nn.SiLU(),
                               nn.Linear(width, width), nn.SiLU(), nn.Linear(width, N_PIX))

    def cond(self, c):
        return self.cls(c)

    def forward(self, xin, s, c):
        return self.f(torch.cat([xin, self.emb(torch.log(s) / 4), self.cond(c)], 1))


def D_of(net, x, s, *cond):
    c_in, c_skip, c_out = precond(s)
    return c_skip * x + c_out * net(c_in * x, s, *cond)


def lr_schedule(steps, warm=200):
    return lambda i: min(1.0, (i + 1) / warm) * max(0.0, 1 - i / steps)


def sample_sigma(n, gen):
    return torch.exp(math.log(SMIN) + torch.rand(n, 1, generator=gen) * (math.log(SMAX) - math.log(SMIN)))


def dsm_loss(net, x0, cond, gen):
    """Denoising score matching with EDM's weight 1/c_out^2: the network is trained on data, not on the
    exact denoiser, the way every real diffusion model is trained."""
    s = sample_sigma(x0.shape[0], gen)
    x = x0 + s * torch.randn(x0.shape, generator=gen)
    c_in, c_skip, c_out = precond(s)
    return ((((c_skip * x + c_out * net(c_in * x, s, *cond)) - x0) / c_out) ** 2).mean()


def train_model(steps, seed, p_drop=0.1, batch=512):
    """A class-conditional network with label dropout (Ho & Salimans): with probability p_drop the class
    token is replaced by the empty prompt, so one network learns both D(x | c) and D(x)."""
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    net = Net()
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    sch = torch.optim.lr_scheduler.LambdaLR(opt, lr_schedule(steps))
    for _ in range(steps):
        x0n, k, _ = sample_data(rng, batch)
        c = torch.tensor(k)
        c = torch.where(torch.rand(batch, generator=gen) < p_drop, torch.full_like(c, NULL), c)
        loss = dsm_loss(net, torch.tensor(x0n, dtype=torch.float32), (c,), gen)
        opt.zero_grad(); loss.backward(); opt.step(); sch.step()
    return net.eval()


@torch.no_grad()
def sample_guided(net, z, cls, w=1.0, n=64, mode="cfg", bad=None, lo=0.0, hi=1e9, phi=0.7, eta=0.0):
    """DDIM with a guided denoised image. mode: 'cfg' (D_u + w (D_c - D_u)), 'auto' (autoguidance: the
    weaker network bad, with the same class, replaces D_u), 'rescale' (Lin et al.: the guided image is
    rescaled toward the conditional one's standard deviation, by phi) or 'apg' (Sadat et al.: only the
    part of D_c - D_u orthogonal to D_c is extrapolated, plus eta times the parallel part). Guidance is
    active for lo < sigma <= hi, else the conditional prediction is used."""
    x = SMAX * torch.tensor(z, dtype=torch.float32)
    m = x.shape[0]
    cc, cu = torch.full((m,), cls), torch.full((m,), NULL)
    g = grid(n)
    for s, s2 in zip(g[:-1], g[1:]):
        st = torch.full((m, 1), s)
        dc = D_of(net, x, st, cc)
        if w == 1.0 or not (lo < s <= hi):
            d = dc
        else:
            du = D_of(bad, x, st, cc) if mode == "auto" else D_of(net, x, st, cu)
            if mode == "apg":
                diff = dc - du
                par = (diff * dc).sum(1, keepdim=True) / (dc * dc).sum(1, keepdim=True) * dc
                d = dc + (w - 1) * ((diff - par) + eta * par)
            else:
                d = du + w * (dc - du)
                if mode == "rescale":
                    d = phi * d * dc.std(1, keepdim=True) / d.std(1, keepdim=True) + (1 - phi) * d
        x = d + (s2 / s) * (x - d)
    return x.numpy().astype(np.float64)


NET_SETTINGS = ([("cfg", w, {}) for w in (1.0, 1.5, 2.0, 3.0, 4.0, 5.0)]
                + [("auto", w, {}) for w in (1.5, 2.0, 2.5, 3.0)]
                + [("interval", 3.0, {"lo": lo, "hi": hi}) for lo, hi in ((0.0, 1.0), (0.0, 2.0), (0.5, 3.0), (1.0, 5.0), (2.0, 80.0))]
                + [("rescale", w, {}) for w in (3.0, 5.0)]
                + [("apg", w, {}) for w in (3.0, 5.0)])


def setting_key(mode, w, kw):
    return f"{mode} w={w:g}" + (f" ({kw['lo']:g},{kw['hi']:g}]" if kw else "")


def cache_dir():
    d = HERE / ".cache"
    d.mkdir(exist_ok=True)
    return d


def model_path(kind, seed, budget):
    return cache_dir() / f"{kind}-{budget['tag']}-s{seed}-{_SRC}.pt"


def load_net(kind, seed, budget):
    net = Net()
    net.load_state_dict(torch.load(model_path(kind, seed, budget)))
    net.eval()
    for p in net.parameters():
        p.requires_grad_(False)
    return net


def _train_job(args):
    kind, seed, budget = args
    path = model_path(kind, seed, budget)
    if not path.exists():
        t0 = time.time()
        net = train_model(budget["model" if kind == "model" else "weak"], seed)
        torch.save(net.state_dict(), path)
        print(f"  trained {kind} network seed {seed}: {budget['model' if kind == 'model' else 'weak']} steps "
              f"({time.time() - t0:.0f} s)", flush=True)
    return kind, seed


def _net_eval_job(args):
    seed, budget, n, group = args
    z = np.random.default_rng(2026).normal(size=(n, N_PIX))
    real = sample_data(np.random.default_rng(31), n, 0)[0]
    model, weak = load_net("model", seed, budget), load_net("weak", seed, budget)
    out = {}
    if group == "weak":
        for w in (1.0, 1.5, 2.0, 3.0, 4.0, 5.0):
            out[setting_key("cfg", w, {})] = stats(sample_guided(weak, z, 0, w), 0, real)
        return seed, "weak", out
    for mode, w, kw in NET_SETTINGS:
        if mode == group or (group == "fixes" and mode in ("rescale", "apg")):
            m = "cfg" if mode == "interval" else mode
            out[setting_key(mode, w, kw)] = stats(sample_guided(model, z, 0, w, mode=m, bad=weak, **kw), 0, real)
    return seed, "model", out


def run_networks(budget, workers, seeds):
    with ProcessPoolExecutor(max_workers=workers) as ex:
        list(ex.map(_train_job, [(k, s, budget) for s in seeds for k in ("model", "weak")]))
        res = {"steps": {"model": budget["model"], "weak": budget["weak"]}, "label_dropout": 0.1, "seeds": {}}
        groups = ("cfg", "auto", "interval", "fixes", "weak")
        for seed, tag, out in ex.map(_net_eval_job, [(s, budget, budget["n_eval"], g) for s in seeds for g in groups]):
            res["seeds"].setdefault(str(seed), {"model": {}, "weak": {}})[tag].update(out)
        for seed in res["seeds"].values():                          # keep the settings in a fixed order
            seed["model"] = {setting_key(m, w, kw): seed["model"][setting_key(m, w, kw)] for m, w, kw in NET_SETTINGS}
    for seed, out in res["seeds"].items():
        for tag in ("model", "weak"):
            line = "  ".join(f"{k.replace('cfg ', '')}: {v['faint']:.2f}/{v['blend']:.3f}/{v['over']:.3f}"
                             for k, v in out[tag].items() if k.startswith("cfg"))
            print(f"  {tag:5s} network seed {seed} cfg   {line}   (faint / blends / over)", flush=True)
        line = "  ".join(f"{k}: {v['faint']:.2f}/{v['blend']:.3f}/{v['swd']:.3f}" for k, v in out["model"].items()
                         if not k.startswith("cfg"))
        print(f"  model network seed {seed} other {line}   (faint / blends / distance)", flush=True)
    return res


# ------------------------------------------------------------------------------- controlnet
def pool4(x):
    """The control: a 4x4 average-pooled layout of the 8x8 image (16 numbers)."""
    return x.reshape(-1, 4, 2, 4, 2).mean((2, 4)).reshape(-1, 16)


class ControlNet(nn.Module):
    """Zhang et al.'s wiring on the toy network. A trainable copy of the frozen network's first two
    hidden layers reads x + Z1(E(y)); its activations are added to the frozen network's after its first
    and second hidden layers through Za and Zb. zero=True starts Z1, Za and Zb at zero (ControlNet's
    zero convolutions); zero=False gives them Gaussian weights (the paper's ablation)."""

    def __init__(self, base, zero=True, seed=0):
        super().__init__()
        torch.manual_seed(seed)
        self.base = base
        self.copy0, self.copy2 = copy.deepcopy(base.f[0]), copy.deepcopy(base.f[2])
        for p in list(self.copy0.parameters()) + list(self.copy2.parameters()):
            p.requires_grad_(True)
        self.E = nn.Sequential(nn.Linear(16, 64), nn.SiLU(), nn.Linear(64, 64))
        self.Z1, self.Za, self.Zb = nn.Linear(64, N_PIX), nn.Linear(WIDTH, WIDTH), nn.Linear(WIDTH, WIDTH)
        for z in (self.Z1, self.Za, self.Zb):
            if zero:
                nn.init.zeros_(z.weight)
            else:
                nn.init.normal_(z.weight, std=1.0 / math.sqrt(z.in_features))
            nn.init.zeros_(z.bias)

    def forward(self, xin, s, c, y):
        b = self.base
        e = [b.emb(torch.log(s) / 4), b.cond(c)]
        h1c = F.silu(self.copy0(torch.cat([xin + self.Z1(self.E(y))] + e, 1)))
        h2c = F.silu(self.copy2(h1c))
        h1 = F.silu(b.f[0](torch.cat([xin] + e, 1))) + self.Za(h1c)
        h2 = F.silu(b.f[2](h1)) + self.Zb(h2c)
        return b.f[6](F.silu(b.f[4](h2)))


@torch.no_grad()
def sample_with(fn, z, n=64):
    """DDIM with any denoiser fn(x, sigma_column)."""
    x = SMAX * torch.tensor(z, dtype=torch.float32)
    m = x.shape[0]
    g = grid(n)
    for s, s2 in zip(g[:-1], g[1:]):
        d = fn(x, torch.full((m, 1), s))
        x = d + (s2 / s) * (x - d)
    return x.numpy().astype(np.float64)


CN_EVALS = (0, 25, 50, 100, 200, 400, 800, 1600, 3200)


def _controlnet_job(args):
    zero, seed, budget = args
    base = load_net("model", seed, budget)
    cn = ControlNet(base, zero=zero, seed=seed)
    opt = torch.optim.Adam([p for p in cn.parameters() if p.requires_grad], lr=2e-4)
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed)
    ev = np.random.default_rng(99)
    xe, ke, _ = sample_data(ev, 1024)
    ye, ce, ze = torch.tensor(pool4(xe), dtype=torch.float32), torch.tensor(ke), ev.normal(size=(1024, N_PIX))
    probe = torch.tensor(2.0 * ze[:256], dtype=torch.float32)       # inputs at sigma = 2 for the step-0 check
    out = {}
    steps = budget["controlnet"]
    for it in range(steps + 1):
        if it in CN_EVALS or it == steps:
            xs = sample_with(lambda x, s: D_of(cn, x, s, ce, ye), ze)
            with torch.no_grad():
                s2 = torch.full((256, 1), 2.0)
                diff = float((D_of(cn, probe, s2, ce[:256], ye[:256]) - D_of(base, probe, s2, ce[:256])).abs().max())
            out[str(it)] = {"control_error": round(float(np.sqrt(((pool4(xs) - pool4(xe)) ** 2).mean())), 4),
                            "swd": round(swd(xs, xe), 4), "max_change": float(f"{diff:.3e}")}
        if it == steps:
            break
        x0n, k, _ = sample_data(rng, 512)
        c = torch.tensor(k)
        c = torch.where(torch.rand(512, generator=gen) < 0.5, torch.full_like(c, NULL), c)   # 50% empty prompts
        x0 = torch.tensor(x0n, dtype=torch.float32)
        loss = dsm_loss(cn, x0, (c, torch.tensor(pool4(x0n), dtype=torch.float32)), gen)
        opt.zero_grad(); loss.backward(); opt.step()
    trainable = sum(p.numel() for p in cn.parameters() if p.requires_grad)
    if zero:
        ex = {"control": pool4(xe[:6]).round(4).tolist(), "source": xe[:6].round(4).tolist(),
              "sample": xs[:6].round(4).tolist()}
    else:
        ex = None
    return zero, seed, out, trainable, ex


def run_controlnet(budget, workers, seeds):
    res = {"steps": budget["controlnet"], "control": "4x4 average pool", "lr": 2e-4, "empty_prompts": 0.5,
           "zero": {}, "gaussian": {}}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for zero, seed, out, trainable, example in ex.map(_controlnet_job, [(z, s, budget) for z in (True, False) for s in seeds]):
            res["zero" if zero else "gaussian"][str(seed)] = out
            res["trainable"] = trainable
            if example:
                res.setdefault("examples", example)
    base_err = res["zero"][str(seeds[0])]["0"]["control_error"]
    for tag in ("zero", "gaussian"):
        for seed, out in res[tag].items():
            print(f"  controlnet {tag:8s} seed {seed}: " + " ".join(f"{k}:{v['control_error']:.3f}/{v['swd']:.3f}" for k, v in out.items())
                  + f"   (step: control error / distance; step-0 change {out['0']['max_change']:.1e})", flush=True)
    print(f"  controlnet: base model's control error {base_err:.3f}; branch trains {res['trainable']} parameters", flush=True)
    return res


# ---------------------------------------------------------------------------- personalization
class LoRA(nn.Module):
    """W x + (alpha / r) B A x with B = 0 at the start (Hu et al.), so the layer begins unchanged."""

    def __init__(self, lin, r=4, alpha=4.0):
        super().__init__()
        self.lin = lin
        self.A = nn.Parameter(torch.randn(r, lin.in_features) / math.sqrt(lin.in_features))
        self.B = nn.Parameter(torch.zeros(lin.out_features, r))
        self.scale = alpha / r

    def forward(self, x):
        return self.lin(x) + self.scale * (x @ self.A.T) @ self.B.T


class Personal(nn.Module):
    """The frozen network plus one new token. 'ti': textual inversion, only a new token is trained and
    the prompt is that token alone, starting from the word 'crescent 0'. 'lora' and 'full': a fixed rare
    token (a vector the model never saw) is added to 'crescent 0', and LoRA updates or every weight are
    trained, as DreamBooth does."""

    def __init__(self, base, mode, r=4):
        super().__init__()
        self.net, self.mode = copy.deepcopy(base), mode
        for p in self.net.f.parameters():
            p.requires_grad_(mode == "full")         # the token embeddings stay frozen, like a text encoder
        if mode == "lora":
            for i in (0, 2, 4, 6):
                self.net.f[i] = LoRA(self.net.f[i], r)
        if mode == "ti":
            self.v = nn.Parameter(base.cls.weight[0].clone())
        else:
            g = torch.Generator().manual_seed(123)
            v = torch.randn(base.cls.weight.shape[1], generator=g)
            self.register_buffer("v", v * base.cls.weight[:K].norm(dim=1).mean() / v.norm())

    def cond(self, c, use_v):
        e = self.net.cls(c)
        if self.mode == "ti":
            return torch.where(use_v[:, None], self.v.expand_as(e), e)
        return e + use_v[:, None].float() * self.v

    def forward(self, xin, s, c, use_v):
        n = self.net
        return n.f(torch.cat([xin, n.emb(torch.log(s) / 4), self.cond(c, use_v)], 1))


def looks_like_subject(x):
    xc = x - x.mean(1, keepdims=True)
    return np.linalg.norm(xc - MU[0], axis=1) > np.linalg.norm(xc - MU_V, axis=1)


PERSONAL = {"ti": ("ti", False), "lora": ("lora", False), "lora+ppl": ("lora", True),
            "full": ("full", False), "full+ppl": ("full", True)}
LR = {"ti": 5e-3, "lora": 1e-3, "full": 1e-4}


def _personal_job(args):
    name, seed, budget, steps = args
    mode, ppl = PERSONAL[name]
    base = load_net("model", seed, budget)
    torch.manual_seed(seed)                  # LoRA's A starts from torch's global generator: seed it per job
    m = Personal(base, mode)
    opt = torch.optim.Adam([p for p in m.parameters() if p.requires_grad], lr=LR[mode])
    rng = np.random.default_rng(seed)
    gen = torch.Generator().manual_seed(seed)
    train = torch.tensor(sample_subject(rng, 5), dtype=torch.float32)            # the five photos
    zp = np.random.default_rng(seed + 50).normal(size=(1000, N_PIX))
    prior = torch.tensor(sample_with(lambda x, s: D_of(base, x, s, torch.zeros(len(x), dtype=torch.long)), zp),
                         dtype=torch.float32)                                     # the model's own crescent 0s
    z = np.random.default_rng(7).normal(size=(1024, N_PIX))
    truth = sample_subject(np.random.default_rng(77), 4096)
    real = {k: sample_data(np.random.default_rng(78 + k), 4096, k)[0] for k in range(K)}
    tr = train.numpy().astype(np.float64)
    near_true = float(np.sqrt(((truth[:1024, None, :] - tr[None]) ** 2).sum(-1)).min(1).mean())
    one, zero_ = torch.ones(1024, dtype=torch.bool), torch.zeros(1024, dtype=torch.bool)

    def evaluate():
        fn = lambda c, uv: (lambda x, s: D_of(m, x, s, torch.full((len(x),), c), uv))
        xv = sample_with(fn(0, one), z)
        x0 = sample_with(fn(0, zero_), z)
        others = [swd(sample_with(fn(k, zero_), z), real[k]) for k in (1, 2, 3)]
        near = float(np.sqrt(((xv[:, None, :] - tr[None]) ** 2).sum(-1)).min(1).mean())
        return {"subject_share": round(float(looks_like_subject(xv).mean()), 4), "subject_swd": round(swd(xv, truth), 4),
                "subject_brightness_sd": round(float(xv.mean(1).std()), 4), "nearest_train_ratio": round(near / near_true, 4),
                "drift": round(float(looks_like_subject(x0).mean()), 4), "class0_swd": round(swd(x0, real[0]), 4),
                "others_swd": round(float(np.mean(others)), 4)}, xv[:4], x0[:4]

    out, B = {"trainable": sum(p.numel() for p in m.parameters() if p.requires_grad),
              "photos_brightness_sd": round(float(tr.mean(1).std()), 4)}, 40
    checks = sorted({c for c in (250, 500, 1000, 2000) if c <= steps} | {steps})
    for it in range(1, steps + 1):
        x0 = train[torch.randint(0, 5, (B,), generator=gen)]
        c, uv = torch.zeros(B, dtype=torch.long), torch.ones(B, dtype=torch.bool)
        if ppl:                                       # DreamBooth's prior preservation, weight 1
            x0 = torch.cat([x0, prior[torch.randint(0, 1000, (B,), generator=gen)]])
            c, uv = torch.zeros(2 * B, dtype=torch.long), torch.cat([uv, torch.zeros(B, dtype=torch.bool)])
        loss = dsm_loss(m, x0, (c, uv), gen)
        opt.zero_grad(); loss.backward(); opt.step()
        if it in checks:
            out[str(it)], xs_v, xs_0 = evaluate()
    out["examples"] = {"subject": xs_v.round(4).tolist(), "class0": xs_0.round(4).tolist(), "train": tr[:4].round(4).tolist()}
    return name, seed, out


def base_personal_stats(seed, budget):
    base = load_net("model", seed, budget)
    z = np.random.default_rng(7).normal(size=(1024, N_PIX))
    xs = {k: sample_with(lambda x, s, k=k: D_of(base, x, s, torch.full((len(x),), k)), z) for k in range(K)}
    real = {k: sample_data(np.random.default_rng(78 + k), 4096, k)[0] for k in range(K)}
    return {"drift": round(float(looks_like_subject(xs[0]).mean()), 4), "class0_swd": round(swd(xs[0], real[0]), 4),
            "others_swd": round(float(np.mean([swd(xs[k], real[k]) for k in (1, 2, 3)])), 4),
            "subject_floor": round(swd(sample_subject(np.random.default_rng(79), 4096), sample_subject(np.random.default_rng(77), 4096)), 4)}


def run_personal(budget, workers, seeds, names=tuple(PERSONAL), steps=None):
    steps = steps or budget["personal"]
    res = {"steps": steps, "images": 5, "prior_images": 1000, "lr": LR, "methods": {}, "base": {}}
    with ProcessPoolExecutor(max_workers=workers) as ex:
        for name, seed, out in ex.map(_personal_job, [(n, s, budget, steps) for n in names for s in seeds]):
            res["methods"].setdefault(name, {})[str(seed)] = out
        for seed, st in zip(seeds, ex.map(base_personal_stats, seeds, [budget] * len(seeds))):
            res["base"][str(seed)] = st
    for name, by_seed in res["methods"].items():
        for seed, out in by_seed.items():
            last = out[str(steps)]
            print(f"  personal {name:8s} seed {seed}: {out['trainable']:>6d} trained; after {steps} steps subject "
                  f"{last['subject_share']:.3f} (distance {last['subject_swd']:.3f}), drift {last['drift']:.3f}, "
                  f"crescent-0 distance {last['class0_swd']:.3f}, other classes {last['others_swd']:.3f}", flush=True)
    for seed, st in res["base"].items():
        print(f"  personal base     seed {seed}: drift {st['drift']:.3f}, crescent-0 distance {st['class0_swd']:.3f}, "
              f"other classes {st['others_swd']:.3f}; two real subject sets {st['subject_floor']:.3f}", flush=True)
    return res


# ---------------------------------------------------------------------------------- inpainting
KNOWN = np.zeros((R, R), bool)
KNOWN[:, :R // 2] = True                  # the left half is known; the right half is generated
KNOWN = KNOWN.reshape(-1)


def posterior_parts(y):
    """Exact inpainting: each sub-mode is Gaussian, so p(x0 | known pixels) is a Gaussian mixture. Returns
    its weights, each component's mean of the unknown half, and each component's Cholesky factor."""
    n_k = int(KNOWN.sum())
    lls, means, chols = [], [], []
    for k, j in components(None):
        m = AMPS[j] * MU[k]
        cov = TAU ** 2 * np.eye(N_PIX) + S_B ** 2 + S_A ** 2 * np.outer(MU[k], MU[k])
        ckk, cuk, cuu = cov[np.ix_(KNOWN, KNOWN)], cov[np.ix_(~KNOWN, KNOWN)], cov[np.ix_(~KNOWN, ~KNOWN)]
        inv = np.linalg.inv(ckk)
        dlt = y - m[KNOWN]
        lls.append(-0.5 * np.einsum("ij,jk,ik->i", dlt, inv, dlt) - 0.5 * np.linalg.slogdet(ckk)[1] + math.log(P_FAINT))
        means.append(m[~KNOWN] + dlt @ (cuk @ inv).T)
        chols.append(np.linalg.cholesky(cuu - cuk @ inv @ cuk.T + 1e-9 * np.eye(N_PIX - n_k)))
    ll = np.stack(lls, 1)
    w = np.exp(ll - ll.max(1, keepdims=True))
    return w / w.sum(1, keepdims=True), means, chols


def posterior_mean(y):
    w, means, _ = posterior_parts(y)
    return sum(w[:, i:i + 1] * means[i] for i in range(len(means)))


def coherence(x, post_mean):
    """A completion is coherent when its generated half sits within 3 tau (RMS per pixel) of the exact
    posterior's mean for that half: a wrong crescent or a wrong contrast misses it by about 0.9 per pixel."""
    rms = np.sqrt(((x[:, ~KNOWN] - post_mean) ** 2).mean(1))
    return {"coherent": round(float((rms < 3 * TAU).mean()), 4), "median_rms": round(float(np.median(rms)), 4)}


def posterior_sample(y, rng):
    w, means, chols = posterior_parts(y)
    n_u = N_PIX - int(KNOWN.sum())
    out = np.empty((len(y), N_PIX))
    pick = np.array([rng.choice(len(means), p=wi) for wi in w])
    for i in range(len(means)):
        sel = pick == i
        if sel.any():
            out[np.ix_(sel, ~KNOWN)] = means[i][sel] + rng.normal(size=(sel.sum(), n_u)) @ chols[i].T
    out[:, KNOWN] = y
    return out


def replacement(y, n=64, resample=1, seed=0):
    """Song et al.'s imputation: at every step the known half is replaced by the known pixels noised to the
    current level, and the exact unconditional denoiser fills the rest. resample > 1 is RePaint's
    resampling: after a step, noise is added back to the previous level and the step is redone."""
    g = np.random.default_rng(seed)
    x = SMAX * g.normal(size=(len(y), N_PIX))
    lv = grid(n)
    for s, s2 in zip(lv[:-1], lv[1:]):
        for r in range(resample):
            x[:, KNOWN] = y + s * g.normal(size=(len(y), int(KNOWN.sum())))
            d = denoise(x, s)
            x = d + (s2 / s) * (x - d)
            if r < resample - 1:
                x = x + math.sqrt(s * s - s2 * s2) * g.normal(size=x.shape)
    x[:, KNOWN] = y
    return x


class InpaintNet(nn.Module):
    """Stable Diffusion's inpainting recipe on the toy: the masked image and the mask enter the first
    layer through new weights that start at zero, so training begins from the pretrained network."""

    def __init__(self, base):
        super().__init__()
        self.net = copy.deepcopy(base)
        for p in self.net.parameters():
            p.requires_grad_(True)
        self.extra = nn.Linear(2 * N_PIX, WIDTH, bias=False)
        nn.init.zeros_(self.extra.weight)

    def forward(self, xin, s, c, masked, mask):
        n = self.net
        h = n.f[0](torch.cat([xin, n.emb(torch.log(s) / 4), n.cond(c)], 1)) + self.extra(torch.cat([masked, mask], 1))
        for layer in list(n.f)[1:]:
            h = layer(h)
        return h


def random_masks(n, gen):
    """Training masks: a random half (left, right, top or bottom) known, or (25%) nothing known."""
    halves = torch.zeros(5, R, R)
    halves[0, :, :R // 2] = 1; halves[1, :, R // 2:] = 1; halves[2, :R // 2, :] = 1; halves[3, R // 2:, :] = 1
    pick = torch.randint(0, 4, (n,), generator=gen)
    pick = torch.where(torch.rand(n, generator=gen) < 0.25, torch.full_like(pick, 4), pick)
    return halves[pick].reshape(n, N_PIX)


def _inpaint_net_job(args):
    seed, budget = args
    base = load_net("model", seed, budget)
    m = InpaintNet(base)
    opt = torch.optim.Adam([p for p in m.parameters() if p.requires_grad], lr=2e-4)
    gen = torch.Generator().manual_seed(seed)
    rng = np.random.default_rng(seed)
    for _ in range(budget["inpaint"]):
        x0n, _, _ = sample_data(rng, 512)
        x0 = torch.tensor(x0n, dtype=torch.float32)
        mask = random_masks(512, gen)
        c = torch.full((512,), NULL)
        loss = dsm_loss(m, x0, (c, x0 * mask, mask), gen)
        opt.zero_grad(); loss.backward(); opt.step()
    src, k0, j0 = sample_data(np.random.default_rng(11), 2048)
    mask = torch.tensor(KNOWN, dtype=torch.float32).expand(2048, N_PIX)
    masked = torch.tensor(src, dtype=torch.float32) * mask
    z = np.random.default_rng(12).normal(size=(2048, N_PIX))
    xs = sample_with(lambda x, s: D_of(m, x, s, torch.full((len(x),), NULL), masked, mask), z)
    xs[:, KNOWN] = src[:, KNOWN]
    return seed, coherence(xs, posterior_mean(src[:, KNOWN])), xs[:4].round(4).tolist()


def run_inpaint(budget, workers, seeds):
    src, k0, j0 = sample_data(np.random.default_rng(11), 2048)
    y = src[:, KNOWN]
    res = {"known": "left half", "n": 2048, "steps": 64, "methods": {}, "examples": {"source": src[:4].round(4).tolist()}}
    pm = posterior_mean(y)
    post = posterior_sample(y, np.random.default_rng(5))
    res["methods"]["exact posterior"] = coherence(post, pm) | {"calls": 0}
    res["examples"]["exact posterior"] = post[:4].round(4).tolist()
    jobs = [(r,) for r in (1, 2, 5, 10)]
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futs = {r: ex.submit(replacement, y, 64, r) for (r,) in jobs}
        nets = list(ex.map(_inpaint_net_job, [(s, budget) for s in seeds]))
        for r, f in futs.items():
            x = f.result()
            key = "replacement" if r == 1 else f"resample {r}"
            res["methods"][key] = coherence(x, pm) | {"calls": 64 * r}
            res["examples"][key] = x[:4].round(4).tolist()
    res["methods"]["inpainting network"] = {str(s): v for s, v, _ in nets}
    res["examples"]["inpainting network"] = nets[0][2]
    res["inpaint_steps"] = budget["inpaint"]
    for key, v in res["methods"].items():
        if key == "inpainting network":
            for s, vv in v.items():
                print(f"  inpaint {key} seed {s}: coherent {vv['coherent']:.3f}, median rms from the posterior mean {vv['median_rms']:.3f}", flush=True)
        else:
            print(f"  inpaint {key:16s}: coherent {v['coherent']:.3f}, median rms from the posterior mean "
                  f"{v['median_rms']:.3f}  ({v['calls']} denoiser calls)", flush=True)
    return res


# ------------------------------------------------------------------------------------- editing
def ddim_between(x, cls, levels, w=1.0):
    """DDIM steps through `levels` (rising levels invert); the class-cls exact denoiser, guided at w."""
    for s, s2 in zip(levels[:-1], levels[1:]):
        dc = denoise(x, s, cls)
        if w != 1.0:
            du = denoise(x, s)
            dc = du + w * (dc - du)
        x = dc + (s2 / s) * (x - dc)
    return x


_B01 = np.stack([MU[0], MU[1]], 1)                       # the old and the new crescent, as two columns


def two_crescents(x):
    """Least-squares amounts of crescent 0 and crescent 1 in each brightness-free image, and the rest."""
    xc = x - x.mean(1, keepdims=True)
    coef = np.linalg.lstsq(_B01, xc.T, rcond=None)[0].T     # (n, 2), in units of a strong crescent
    return coef, xc - coef @ _B01.T


def edit_reading(out, src, src_j):
    """success: the output shows crescent 1; ghost: how much of the source's crescent 0 is left (1 = all,
    0 = none); contrast kept: faint stays faint and strong stays strong; detail: correlation of the fine
    detail left after both crescents and the brightness are removed."""
    shown, _ = contrast(out)
    co, ro = two_crescents(out)
    cs, rs = two_crescents(src)
    corr = float(np.mean([np.corrcoef(ro[i], rs[i])[0, 1] for i in range(len(src))]))
    return {"success": round(float((shown == 1).mean()), 4), "ghost": round(float(np.median(co[:, 0] / cs[:, 0])), 4),
            "contrast_kept": round(float(((co[:, 1] >= 0.75).astype(int) == src_j).mean()), 4),
            "brightness_error": round(float(np.abs(out.mean(1) - src.mean(1)).mean()), 4),
            "detail_corr": round(corr, 4)}


SIGMA0 = (0.1, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0, 80.0)


def run_edit():
    src, _, j_src = sample_data(np.random.default_rng(13), 1024, 0)
    res = {"n": 1024, "from_class": 0, "to_class": 1, "sdedit": {}, "examples": {"source": src[:4].round(4).tolist()}}
    for s0 in SIGMA0:
        g = np.random.default_rng(3)
        lv = [s0] + [s for s in grid(256) if s < s0]
        out = ddim_between(src + s0 * g.normal(size=src.shape), 1, lv)
        res["sdedit"][str(s0)] = edit_reading(out, src, j_src)
        if s0 in (0.5, 2.0, 8.0):
            res["examples"][f"sdedit {s0:g}"] = out[:4].round(4).tolist()
    up = grid(512)[::-1]
    up = [SMIN] + [s for s in up if s > SMIN]
    noise = ddim_between(src, 0, up)                      # DDIM inversion with the class-0 ODE
    down = grid(512)
    recon = ddim_between(noise.copy(), 0, down)
    edited = ddim_between(noise.copy(), 1, down)
    res["inversion"] = edit_reading(edited, src, j_src) | {
        "reconstruction_rms": round(float(np.sqrt(((recon - src) ** 2).mean())), 5),
        "guided_reconstruction_rms": {str(w): round(float(np.sqrt(((ddim_between(noise.copy(), 0, down, w) - src) ** 2).mean())), 4)
                                      for w in (1.5, 2.0, 3.0)}}
    res["examples"]["inversion"] = edited[:4].round(4).tolist()
    for s0, v in res["sdedit"].items():
        print(f"  edit sdedit sigma0={s0:>5}: success {v['success']:.3f}, ghost {v['ghost']:+.3f}, contrast kept "
              f"{v['contrast_kept']:.3f}, brightness error {v['brightness_error']:.3f}, detail corr {v['detail_corr']:.3f}", flush=True)
    v = res["inversion"]
    print(f"  edit inversion: success {v['success']:.3f}, ghost {v['ghost']:+.3f}, contrast kept {v['contrast_kept']:.3f}, "
          f"brightness error {v['brightness_error']:.4f}, detail corr {v['detail_corr']:.3f}; reconstruction rms "
          f"{v['reconstruction_rms']:.5f}, guided: " + ", ".join(f"w={w} {e:.3f}" for w, e in v["guided_reconstruction_rms"].items()), flush=True)
    return res


# -------------------------------------------------------------------------------- figure samples
def run_samples(quick):
    """Ten starting noises through the exact model at four guidance weights, for the figures: the first
    five of a fixed pool that end faint without guidance, and the first five that end strong."""
    pool = np.random.default_rng(404).normal(size=(64, N_PIX))
    _, amp = contrast(sample_exact(pool, 0, 1.0), 0)
    pick = list(np.flatnonzero(amp < 0.75)[:5]) + list(np.flatnonzero(amp >= 0.75)[:5])
    z = pool[pick]
    out = {str(w): sample_exact(z, 0, w).round(4).tolist() for w in (1.0, 2.0, 3.0, 5.0)}
    out["pool_index"] = [int(i) for i in pick]
    return out


# ------------------------------------------------------------------------------------- census
SD15_UNET = {   # stable-diffusion-v1-5/stable-diffusion-v1-5, unet/config.json, as in part 4's lab
    "act_fn": "silu", "attention_head_dim": 8, "block_out_channels": [320, 640, 1280, 1280],
    "center_input_sample": False, "cross_attention_dim": 768,
    "down_block_types": ["CrossAttnDownBlock2D", "CrossAttnDownBlock2D", "CrossAttnDownBlock2D", "DownBlock2D"],
    "downsample_padding": 1, "flip_sin_to_cos": True, "freq_shift": 0, "in_channels": 4, "layers_per_block": 2,
    "mid_block_scale_factor": 1, "norm_eps": 1e-05, "norm_num_groups": 32, "out_channels": 4, "sample_size": 64,
    "up_block_types": ["UpBlock2D", "CrossAttnUpBlock2D", "CrossAttnUpBlock2D", "CrossAttnUpBlock2D"],
}


def run_census():
    """Trainable parameters of each control method on SD 1.5, counted on PyTorch's meta device: the
    published config builds the modules without weights, so nothing is downloaded."""
    import re
    try:
        from diffusers import ControlNetModel, UNet2DConditionModel
    except ImportError:
        print("  census: skipped (needs diffusers==0.40.0)", flush=True)
        return None
    with torch.device("meta"):
        unet = UNet2DConditionModel(**SD15_UNET)
        cn = ControlNetModel.from_unet(unet)
    count = lambda mod: sum(p.numel() for p in mod.parameters())
    attn = [mod for name, mod in unet.named_modules()
            if isinstance(mod, nn.Linear) and re.search(r"attn[12]\.(to_q|to_k|to_v|to_out\.0)$", name)]
    res = {"unet": count(unet), "controlnet": count(cn),
           "controlnet_zero_convs": sum(p.numel() for n, p in cn.named_parameters() if "controlnet_down_blocks" in n or "controlnet_mid_block" in n),
           "controlnet_condition_encoder": sum(p.numel() for n, p in cn.named_parameters() if "controlnet_cond_embedding" in n),
           "attention_projections": len(attn),
           "lora": {str(r): sum(r * (m.in_features + m.out_features) for m in attn) for r in (1, 4, 16, 64)},
           "cross_attention_kv": sum(p.numel() for n, p in unet.named_parameters() if re.search(r"attn2\.(to_k|to_v)\.weight", n)),
           "token_embedding": 768}
    print(f"  census SD 1.5: U-Net {res['unet']:,}; ControlNet {res['controlnet']:,} ({res['controlnet'] / res['unet']:.1%}); "
          f"LoRA r=4 on {res['attention_projections']} attention projections {res['lora']['4']:,}; cross-attention K,V "
          f"{res['cross_attention_kv']:,}; one token embedding {res['token_embedding']}", flush=True)
    return res


# --------------------------------------------------------------------------------------- main
_SRC = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]   # caches are keyed to this file


def provenance():
    cpu = platform.processor() or platform.machine()
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return (f"Captured {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} on {platform.system()} {platform.release()} "
            f"{platform.machine()}, {cpu}, {os.cpu_count()} logical CPUs; Python {platform.python_version()}, "
            f"numpy {np.__version__}, torch {torch.__version__}; control.py {_SRC}")


def budgets(quick):
    if quick:
        return {"tag": "quick", "model": 6000, "weak": 1500, "controlnet": 800, "personal": 500, "inpaint": 1000, "n_eval": 2048}
    return {"tag": "full", "model": 20000, "weak": 5000, "controlnet": 3200, "personal": 2000, "inpaint": 4000, "n_eval": N_EVAL}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stage", choices=["worked", "exact", "networks", "controlnet", "personal", "inpaint", "edit",
                                      "samples", "census", "all"])
    ap.add_argument("--quick", action="store_true", help="shorter training and fewer samples")
    ap.add_argument("--out", default=None, help="write here instead of captures.json")
    ap.add_argument("--workers", type=int, default=max(1, min(8, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--w", type=float, default=3.0, help="worked: the guidance weight of the worked step")
    ap.add_argument("--method", choices=list(PERSONAL), default=None, help="personal: train only this method")
    ap.add_argument("--steps", type=int, default=None, help="personal: fine-tuning steps")
    args = ap.parse_args()
    out = Path(args.out) if args.out else HERE / "captures.json"
    prov = provenance()
    print(prov, flush=True)
    budget = budgets(args.quick)
    seeds = list(range(1, args.seeds + 1))
    cap = json.loads(out.read_text()) if out.exists() and args.stage != "all" else {}
    cap.update({"provenance": prov, "source_sha1": _SRC, "budget": budget,
                "world": {"classes": K, "contrasts": list(AMPS), "faint_share": P_FAINT, "contrast_jitter": S_A,
                          "brightness_sd": S_B, "detail": TAU, "pixels": N_PIX, "crescent_norm": round(NORM, 4),
                          "over_threshold": round(OVER, 4), "blend_band": [round(MID[0], 4), round(MID[1], 4)],
                          "sigma_max": SMAX, "sigma_min": SMIN}})
    t0 = time.time()
    stages = ["worked", "exact", "networks", "controlnet", "personal", "inpaint", "edit", "samples"] if args.stage == "all" else [args.stage]
    for stage in stages:
        if stage == "worked":
            cap["worked"] = run_worked(args.w)
        elif stage == "exact":
            cap["exact"] = run_exact(args.workers, args.quick)
        elif stage == "networks":
            cap["networks"] = run_networks(budget, args.workers, seeds)
        elif stage == "controlnet":
            run_networks_if_needed(budget, args.workers, seeds)
            cap["controlnet"] = run_controlnet(budget, args.workers, seeds)
        elif stage == "personal":
            run_networks_if_needed(budget, args.workers, seeds)
            names = (args.method,) if args.method else tuple(PERSONAL)
            res = run_personal(budget, args.workers, seeds, names, args.steps)
            if args.method or args.steps:
                cap.setdefault("personal_probe", {})[f"{','.join(names)} {res['steps']}"] = res
            else:
                cap["personal"] = res
        elif stage == "inpaint":
            run_networks_if_needed(budget, args.workers, seeds)
            cap["inpaint"] = run_inpaint(budget, args.workers, seeds)
        elif stage == "edit":
            cap["edit"] = run_edit()
        elif stage == "samples":
            cap["samples"] = run_samples(args.quick)
        elif stage == "census":
            c = run_census()
            if c:
                cap["census"] = c
        out.write_text(json.dumps(cap, indent=1) + "\n")
    print(f"wrote {os.path.relpath(out, Path.cwd())} in {time.time() - t0:.0f} s", flush=True)


def run_networks_if_needed(budget, workers, seeds):
    """The later stages fine-tune the trained network; train it first if the cache has none."""
    if not all(model_path(k, s, budget).exists() for s in seeds for k in ("model", "weak")):
        with ProcessPoolExecutor(max_workers=workers) as ex:
            list(ex.map(_train_job, [(k, s, budget) for s in seeds for k in ("model", "weak")]))


if __name__ == "__main__":
    main()
