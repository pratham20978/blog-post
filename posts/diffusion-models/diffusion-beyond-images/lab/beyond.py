#!/usr/bin/env python3
"""Lab for "Diffusion Beyond Images: Video, Audio, 3-D and Molecules" (Diffusion Models series, part 10).

Crescent world again, now also in motion. Every 8x8 frame shows one of four crescents, faint or strong,
with a random brightness and a little pixel noise. In a clip of four frames the crescent turns a quarter
turn per frame, always the same way, and keeps its contrast and its brightness. The frame distribution
and the clip distribution are both Gaussian mixtures, so both have exact denoisers: every failure below
belongs to how the sampler is driven or conditioned, never to a badly trained network.

  worked     the article's worked example: part 1's 16 numbers, one forward step, read as an image, a
             waveform, a 4-frame strip and 8 points; then the one-pixel video, whose two frames agree with
             probability 1/2 + arcsin(rho)/pi when their noises are correlated by rho
  video      a per-frame (image) model sampled with independent, mixed, shared and warped noise, against
             the joint (video) model: valid frames, flicker, freezing and coherent motion, 4,096 clips each
  forecast   the rest of a clip from its first 1, 2 or 3 frames: replacement with the joint model against
             exact conditioning
  sds        score distillation sampling on crescent world with an identity "renderer", at eight guidance
             weights, 256 runs each, against ancestral (DDIM) sampling at the same weights
  census     numbers per sample for the article's modalities, computed from the papers' configurations;
             how flat a wrapped normal is on a circle
  all        everything, in that order (about a minute on one core)

Run:   python beyond.py all                       # the article's run
       python beyond.py all --quick               # fewer clips and runs, noisier numbers
       python beyond.py video --warp-variance 0.5 # warped noise that lost half its variance (exercise E3)
       python beyond.py video --fault             # exercise E4: something is wrong with the warp
Writes captures.json beside this file (or --out) and prints the same numbers.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")     # one thread, so timings and sums repeat on any machine

import numpy as np

HERE = Path(__file__).resolve().parent
K = 4                                   # crescent orientations: the classes
A_C, S_B, TAU = 0.9, 0.3, 0.1           # strong crescent RMS amplitude, brightness spread, detail noise
AMPS = (0.5, 1.0)                       # faint and strong contrast, as fractions of a strong crescent
P_FAINT = 0.5                           # half of each class is faint
S_A = 0.06                              # contrast jitter within each sub-mode
R = 8                                   # frame side; 64 pixels
N_PIX = R * R
SMAX, SMIN, RHO = 80.0, 0.002, 7.0      # EDM's noise range and step spacing (parts 6-9's sampler)
T = 4                                   # frames per clip
DIRS = (1, -1)                          # a quarter turn per frame: counter-clockwise (np.rot90's way) or clockwise
BRIGHT_TOL = 0.1                        # brightness change between frames that counts as flicker (real: sd 0.018)


# --------------------------------------------------------------------------- crescent world
def crescent_shape(r=R, inner=(0.64, 0.42, 0.30), supersample=8):
    """A crescent: a disc minus an offset disc, area-sampled onto r x r pixels."""
    g = (np.arange(r * supersample) + 0.5) / (r * supersample)
    yy, xx = np.meshgrid(g, g, indexing="ij")
    outer = (xx - 0.5) ** 2 + (yy - 0.5) ** 2 < 0.36 ** 2
    hole = (xx - inner[0]) ** 2 + (yy - inner[1]) ** 2 < inner[2] ** 2
    return (outer & ~hole).astype(float).reshape(r, supersample, r, supersample).mean(axis=(1, 3))


def unit(m):
    m = m.reshape(-1) - m.mean()
    return m * A_C / np.sqrt((m ** 2).mean())


MU = np.stack([unit(np.rot90(crescent_shape(), k)) for k in range(K)])    # (K, 64): crescent k+1 is crescent k turned
NORM = float(np.linalg.norm(MU[0]))                                        # 7.2
MU_HAT = MU / NORM
V_E = S_B ** 2 * N_PIX + TAU ** 2                          # frame variance along the brightness axis
LAM = TAU ** 2 + (S_A * NORM) ** 2                         # frame variance along a component's own crescent
SPREAD = math.sqrt(S_A ** 2 + (TAU / NORM) ** 2)           # contrast spread of one sub-mode: 0.0616
OVER = AMPS[1] + 3 * SPREAD                                 # contrast no real strong crescent exceeds (1.185)
MID = (AMPS[0] + 3 * SPREAD, AMPS[1] - 3 * SPREAD)          # contrasts no real crescent has (0.685..0.815)
WEAK = AMPS[0] - 3 * SPREAD                                 # below this, weaker than any real faint crescent (0.315)


def rot(z, k):
    """Turn frames (..., 64) a quarter turn k times, the way np.rot90 turns an 8x8 image."""
    return np.rot90(z.reshape(z.shape[:-1] + (R, R)), k, axes=(-2, -1)).reshape(z.shape)


def sample_frames(rng, n, cls=None):
    """Images: x0 = a mu_k + b 1 + tau z, k uniform (or cls), a faint or strong (+ jitter), b ~ N(0, s_b^2)."""
    k = rng.integers(0, K, n) if cls is None else np.full(n, cls)
    j = (rng.random(n) >= P_FAINT).astype(int)
    a = np.array(AMPS)[j] + S_A * rng.normal(size=n)
    b = rng.normal(0.0, S_B, n)
    return a[:, None] * MU[k] + b[:, None] + TAU * rng.normal(size=(n, N_PIX))


def sample_clips(rng, n):
    """Clips (n, T, 64): crescent k0 + d f in frame f, one contrast and one brightness for the whole clip."""
    k0 = rng.integers(0, K, n)
    d = np.array(DIRS)[rng.integers(0, 2, n)]
    j = (rng.random(n) >= P_FAINT).astype(int)
    a = np.array(AMPS)[j] + S_A * rng.normal(size=n)
    b = rng.normal(0.0, S_B, n)
    x = np.empty((n, T, N_PIX))
    for f in range(T):
        x[:, f] = a[:, None] * MU[(k0 + d * f) % K] + b[:, None] + TAU * rng.normal(size=(n, N_PIX))
    return x


def read_frames(x):
    """Which crescent each frame shows (largest projection), how strongly (fraction of a strong crescent),
    its brightness (mean pixel), and the leftover pixel detail."""
    c = x - x.mean(-1, keepdims=True)
    proj = c @ MU_HAT.T / NORM
    shown = np.argmax(proj, -1)
    amp = np.take_along_axis(proj, shown[..., None], -1)[..., 0]
    resid = c - (c @ MU_HAT.T) @ np.linalg.pinv(MU_HAT).T
    return shown, amp, x.mean(-1), resid.std(-1) * math.sqrt(N_PIX / (N_PIX - 1 - K))


def valid(amp):
    """A real crescent at a real contrast: inside the faint band or the strong band."""
    return ((amp > WEAK) & (amp < MID[0])) | ((amp > MID[1]) & (amp < OVER))


# ------------------------------------------------------------- exact denoisers: frame and clip
def _mixture_denoise(x, s, dirs, means, prior, lam, v_e):
    """E[x0 | x0 + s eps = x] for a mixture whose component c is Gaussian with mean means[c] * dirs[c],
    variance lam along dirs[c] (unit), v_e along the all-ones direction and TAU^2 elsewhere. s may be a
    scalar or one noise level per row."""
    s2 = np.asarray(s, float) ** 2
    s2c = s2[:, None] if s2.ndim else s2
    p = x.mean(1, keepdims=True)
    u = x @ dirs.T                                          # (n, components)
    a_o, a_k, a_e = TAU ** 2 / (TAU ** 2 + s2c), lam / (lam + s2c), v_e / (v_e + s2c)
    logits = -0.5 * ((u - means) ** 2 / (lam + s2c) - u ** 2 / (TAU ** 2 + s2c)) + np.log(prior)
    logits -= logits.max(1, keepdims=True)
    w = np.exp(logits)
    w /= w.sum(1, keepdims=True)
    coef = w * (means + a_k * (u - means) - a_o * u)        # each component's correction along its direction
    return a_o * (x - p) + a_e * p + coef @ dirs


FRAME_COMPS = [(k, j) for k in range(K) for j in (0, 1)]
FRAME_DIRS = np.stack([MU_HAT[k] for k, _ in FRAME_COMPS])
FRAME_MEANS = np.array([AMPS[j] * NORM for _, j in FRAME_COMPS])
FRAME_PRIOR = np.array([(P_FAINT if j == 0 else 1 - P_FAINT) / K for _, j in FRAME_COMPS])


def denoise_frame(x, s, cls=None):
    """Exact frame denoiser, unconditional or for one class (parts 8-9, unchanged)."""
    sel = [i for i, (k, _) in enumerate(FRAME_COMPS) if cls is None or k == cls]
    return _mixture_denoise(x, s, FRAME_DIRS[sel], FRAME_MEANS[sel], FRAME_PRIOR[sel], LAM, V_E)


CLIP_COMPS = [(k0, d, j) for k0 in range(K) for d in DIRS for j in (0, 1)]          # 16 components
CLIP_DIRS = np.stack([np.concatenate([MU_HAT[(k0 + d * f) % K] for f in range(T)]) / math.sqrt(T)
                      for k0, d, _ in CLIP_COMPS])
CLIP_MEANS = np.array([AMPS[j] * NORM * math.sqrt(T) for _, _, j in CLIP_COMPS])
CLIP_PRIOR = np.array([(P_FAINT if j == 0 else 1 - P_FAINT) / (K * len(DIRS)) for _, _, j in CLIP_COMPS])
LAM_CLIP = TAU ** 2 + (S_A * NORM) ** 2 * T               # one contrast for all frames
V_E_CLIP = S_B ** 2 * N_PIX * T + TAU ** 2                 # one brightness for all frames


def denoise_clip(x, s):
    """Exact joint denoiser for whole clips, x of shape (n, T * 64), frame-major."""
    return _mixture_denoise(x, s, CLIP_DIRS, CLIP_MEANS, CLIP_PRIOR, LAM_CLIP, V_E_CLIP)


def sig_u(u):
    return (SMAX ** (1 / RHO) + u * (SMIN ** (1 / RHO) - SMAX ** (1 / RHO))) ** RHO


def grid(n):
    return [float(sig_u(i / n)) for i in range(n)] + [0.0]


def ddim(z, denoise, n=128):
    """Deterministic DDIM from noise z (scaled to sigma_max) with the given denoiser (part 6's sampler)."""
    x = SMAX * z
    g = grid(n)
    for s, s2 in zip(g[:-1], g[1:]):
        d = denoise(x, s)
        x = d + (s2 / s) * (x - d)
    return x


def sample_frames_guided(z, cls, w, n=128):
    """DDIM on the exact frame denoisers with classifier-free guidance at weight w (part 8's convention)."""
    def den(x, s):
        dc = denoise_frame(x, s, cls)
        if w == 1.0:
            return dc
        du = denoise_frame(x, s)
        return du + w * (dc - du)
    return ddim(z, den, n)


def r4(v):
    return round(float(v), 4)


def r6(v):
    return round(float(v), 6)


# --------------------------------------------------------------------------------- worked
X0 = np.array([[0.95, 0.60, -0.30, -0.85], [0.80, 0.45, -0.55, -0.90],
               [0.55, 0.10, -0.70, -0.95], [0.25, -0.20, -0.85, -1.00]])     # part 1's patch
EPS = np.array([[-0.55, 1.40, 0.45, -1.10], [0.85, -1.35, -0.25, 0.70],
                [1.25, 0.30, -0.95, 0.15], [-1.05, 0.90, 1.45, -1.10]])      # part 1's noise draw
SQ_AB, SQ_1MAB = 0.8, 0.6                                                     # abar = 0.64


def agreement(rho):
    """Two frames of a symmetric two-valued pixel, sampled by a deterministic sampler from noises with
    correlation rho, agree when the two noises have the same sign: Sheppard's 1/2 + arcsin(rho)/pi."""
    return 0.5 + math.asin(rho) / math.pi


def run_worked(quick):
    xt = SQ_AB * X0 + SQ_1MAB * EPS
    res = {"x0": X0.tolist(), "eps": EPS.tolist(), "xt": [[r4(v) for v in row] for row in xt],
           "top_left": {"x0": X0[0, 0], "eps": EPS[0, 0], "xt": r4(xt[0, 0])}}
    i, j = 1, 1
    res["image"] = {"value": X0[i, j], "neighbours": {"up": X0[i - 1, j], "down": X0[i + 1, j],
                                                      "left": X0[i, j - 1], "right": X0[i, j + 1]}}
    flat = X0.reshape(-1)
    res["audio"] = {"rate_hz": 16000, "ms": r4(16 / 16000 * 1000), "value": flat[5],
                    "neighbours": [flat[4], flat[6]], "per_second": 16000, "patches_per_second": 16000 // 16}
    d0 = np.abs(np.diff(X0, axis=0))                        # rows are frames of a 1 x 4 strip
    dt = np.abs(np.diff(xt, axis=0))
    res["video"] = {"mean_abs_change_clean": r4(d0.mean()), "mean_abs_change_noisy": r4(dt.mean()),
                    "ratio": r4(dt.mean() / d0.mean()), "changes_clean": d0.round(2).tolist(),
                    "changes_noisy": dt.round(2).tolist()}
    pts0, ptse, ptst = X0.reshape(8, 2), EPS.reshape(8, 2), xt.reshape(8, 2)
    res["points"] = {"x0": pts0.tolist(), "eps": ptse.tolist(), "orderings": math.factorial(8),
                     "centroid_x0": [r6(v) for v in pts0.mean(0)], "centroid_eps": [r6(v) for v in ptse.mean(0)],
                     "centroid_xt": [r6(v) for v in ptst.mean(0)],
                     "centroid_shift_by_noise": [r6(v) for v in SQ_1MAB * ptse.mean(0)],
                     "eps_zero_centre": (ptse - ptse.mean(0)).round(4).tolist()}
    print(f"  forward step: x_t[0,0] = 0.8 x {X0[0, 0]} + 0.6 x {EPS[0, 0]} = {xt[0, 0]:.2f}; "
          f"frame-to-frame change clean {d0.mean():.4f}, noisy {dt.mean():.4f} ({dt.mean() / d0.mean():.2f}x); "
          f"noise centroid {ptse.mean(0).round(4).tolist()}, shifts the cloud by {(SQ_1MAB * ptse.mean(0)).round(4).tolist()}",
          flush=True)
    # the one-pixel video: a symmetric two-valued pixel (+1 or -1, spread 0.1), exact denoiser, DDIM
    rng = np.random.default_rng(7)
    n = 50_000 if quick else 400_000
    s_in = 0.1

    def den1(x, s):
        s2 = s * s
        v = s_in ** 2 + s2
        lp = -0.5 * (x - 1) ** 2 / v
        lm = -0.5 * (x + 1) ** 2 / v
        wp = 1 / (1 + np.exp(np.clip(lm - lp, -60, 60)))
        shrink = s_in ** 2 / v
        return wp * (1 + shrink * (x - 1)) + (1 - wp) * (-1 + shrink * (x + 1))

    one = {"rho": {}, "n": n}
    for rho in (-1.0, 0.0, 0.5, 0.9, 0.99, 1.0):
        z1 = rng.normal(size=n)
        z2 = rho * z1 + math.sqrt(max(0.0, 1 - rho * rho)) * rng.normal(size=n)
        f1 = ddim(z1[:, None], den1)[:, 0]
        f2 = ddim(z2[:, None], den1)[:, 0]
        meas = float((np.sign(f1) == np.sign(f2)).mean())
        one["rho"][str(rho)] = {"formula": r4(agreement(rho)), "measured": r4(meas)}
        print(f"  one-pixel video, rho {rho:+.2f}: frames agree {meas:.4f} (formula {agreement(rho):.4f})", flush=True)
    res["one_pixel"] = one
    return res


# ---------------------------------------------------------------------------------- video
def clip_report(x):
    """Read clips (n, T, 64): frame validity, frozen/quarter/half turns, contrast flips, brightness
    flicker, and whole-clip coherence (every frame real, one consistent quarter turn per frame, one
    contrast, no flicker)."""
    shown, amp, bright, detail = read_frames(x)
    ok = valid(amp)
    dk = (shown[:, 1:] - shown[:, :-1]) % K
    strong = amp >= 0.75
    flip = strong[:, 1:] != strong[:, :-1]
    flick = np.abs(np.diff(bright, axis=1)) > BRIGHT_TOL
    turn = (dk == 1) | (dk == 3)
    steady = np.all(dk == dk[:, :1], axis=1)
    motion = steady & turn[:, 0]
    coherent = motion & ok.all(1) & ~flip.any(1) & ~flick.any(1)
    return {"valid_frames": float(ok.mean()), "frozen_turns": float((dk == 0).mean()),
            "quarter_turns": float(turn.mean()), "half_turns": float((dk == 2).mean()),
            "contrast_flips": float(flip.mean()), "flicker": float(flick.mean()),
            "frozen_clips": float(np.all(dk == 0, axis=1).mean()), "motion_clips": float(motion.mean()),
            "coherent_clips": float(coherent.mean()),
            "_example": [[[round(float(v), 3) for v in fr] for fr in clip] for clip in x[:4]]}


def warp(z, k, fault=False):
    """Move frame noise along the clip's motion: k quarter turns. With fault=True, the warp from an
    earlier draft of this lab (exercise E4)."""
    if not fault:
        return rot(z, k)
    img = z.reshape(z.shape[:-1] + (R, R))
    for _ in range(abs(k)):
        img = np.swapaxes(img, -2, -1)
    return img.reshape(z.shape)


def per_frame_noise(rng, n, scheme, rho=0.0, warp_variance=1.0, fault=False):
    """Starting noise (n, T, 64) for a per-frame model. 'mixed' is PYoCo's mixed noise with correlation
    rho between frames; 'warped' moves frame 0's noise a quarter turn per frame (Text2Video-Zero's idea,
    exact here because a quarter turn only moves pixels)."""
    if scheme == "independent":
        return rng.normal(size=(n, T, N_PIX))
    if scheme == "mixed":
        shared = rng.normal(size=(n, 1, N_PIX))
        return math.sqrt(rho) * shared + math.sqrt(1 - rho) * rng.normal(size=(n, T, N_PIX))
    z0 = rng.normal(size=(n, N_PIX))
    if scheme == "shared":
        return np.repeat(z0[:, None], T, axis=1)
    d = np.array(DIRS)[rng.integers(0, 2, n)]
    z = np.empty((n, T, N_PIX))
    for f in range(T):
        for dd in DIRS:
            m = d == dd
            z[m, f] = warp(z0[m], dd * f, fault)
        if f:
            z[:, f] *= math.sqrt(warp_variance)              # E3: a warp that lost variance
    return z


MIXED_RHOS = (0.25, 0.5, 0.75, 0.9, 0.95, 0.99)


def run_video(quick, warp_variance=1.0, fault=False):
    n = 1024 if quick else 4096
    res = {"n": n, "frames": T, "bright_tol": BRIGHT_TOL, "schemes": {}}
    rows = [("data", None, 0.0)]
    rows += [("independent", "independent", 0.0)] + [(f"mixed {r}", "mixed", r) for r in MIXED_RHOS]
    rows += [("shared", "shared", 1.0), ("warped", "warped", 1.0), ("joint", "joint", 0.0)]
    for label, scheme, rho in rows:
        rng = np.random.default_rng(2610)                    # the same seeds for every scheme
        if scheme is None:
            x = sample_clips(np.random.default_rng(41), n)
        elif scheme == "joint":
            x = ddim(rng.normal(size=(n, T * N_PIX)), denoise_clip).reshape(n, T, N_PIX)
        else:
            z = per_frame_noise(rng, n, scheme, rho, warp_variance, fault)
            x = ddim(z.reshape(n * T, N_PIX), denoise_frame).reshape(n, T, N_PIX)
        st = clip_report(x)
        if scheme == "mixed":
            st["pyoco_alpha"] = math.sqrt(rho / (1 - rho))   # rho = alpha^2 / (1 + alpha^2)
        res["schemes"][label] = {k: (r6(v) if isinstance(v, float) else v) for k, v in st.items()}
        print(f"  video {label:>11}: frames valid {st['valid_frames']:.4f} | turns: frozen {st['frozen_turns']:.3f}, "
              f"quarter {st['quarter_turns']:.3f}, half {st['half_turns']:.3f} | contrast flips {st['contrast_flips']:.3f}, "
              f"flicker {st['flicker']:.3f} | clips: frozen {st['frozen_clips']:.4f}, moving {st['motion_clips']:.4f}, "
              f"coherent {st['coherent_clips']:.4f}", flush=True)
    # does the frame denoiser commute with the warp in use? and after how many steps does the warp repeat?
    x = sample_frames(np.random.default_rng(5), 512) + 2.0 * np.random.default_rng(6).normal(size=(512, N_PIX))
    d = denoise_frame(x, 2.0)
    period = next(p for p in range(1, 9) if np.array_equal(warp(x, p, fault), x))
    res["warp_check"] = {"commute_error": float(np.abs(denoise_frame(warp(x, 1, fault), 2.0) - warp(d, 1, fault)).max()),
                         "period": period}
    print(f"  warp in use: max |D(warp x) - warp D(x)| at sigma 2 = {res['warp_check']['commute_error']:.2e}; "
          f"it repeats every {period} frames", flush=True)
    res["warp_variance"], res["fault"] = warp_variance, fault
    return res


# ------------------------------------------------------------------------------- forecast
def exact_condition(rng, x_obs, k_obs):
    """Sample the unobserved frames exactly from p(rest | first k_obs frames): the posterior over the 16
    clip components, then contrast a and brightness b given the observed frames, then fresh detail."""
    n = len(x_obs)
    flat = x_obs.reshape(n, -1)
    n_a = k_obs * N_PIX
    norm_a = NORM * math.sqrt(k_obs)
    dirs = np.stack([np.concatenate([MU_HAT[(k0 + d * f) % K] for f in range(k_obs)]) / math.sqrt(k_obs)
                     for k0, d, _ in CLIP_COMPS])
    means = np.array([AMPS[j] * norm_a for _, _, j in CLIP_COMPS])
    lam_a = TAU ** 2 + (S_A * norm_a) ** 2
    u = flat @ dirs.T
    logits = -0.5 * ((u - means) ** 2 / lam_a - u ** 2 / TAU ** 2) + np.log(CLIP_PRIOR)
    logits -= logits.max(1, keepdims=True)
    w = np.exp(logits)
    w /= w.sum(1, keepdims=True)
    c = (w.cumsum(1) > rng.random((n, 1))).argmax(1)
    out = np.empty((n, T, N_PIX))
    out[:, :k_obs] = x_obs
    prec_b = 1 / S_B ** 2 + n_a / TAU ** 2                   # the observed mean pixel is b + noise of variance tau^2 / n_a
    b = rng.normal((n_a * flat.mean(1) / TAU ** 2) / prec_b, 1 / math.sqrt(prec_b))
    for i, (k0, d, j) in enumerate(CLIP_COMPS):
        m = c == i
        if not m.any():
            continue
        ui = u[m, i] / NORM / math.sqrt(k_obs)               # observed contrast along this component
        prec_a = 1 / S_A ** 2 + (NORM ** 2 * k_obs) / TAU ** 2
        mean_a = (AMPS[j] / S_A ** 2 + ui * NORM ** 2 * k_obs / TAU ** 2) / prec_a
        a = rng.normal(mean_a, 1 / math.sqrt(prec_a))
        for f in range(k_obs, T):
            out[m, f] = a[:, None] * MU[(k0 + d * f) % K] + b[m, None] + TAU * rng.normal(size=(int(m.sum()), N_PIX))
    return out


def replacement(rng, x_obs, k_obs, n_steps=128):
    """Predict the rest of each clip with the joint model, forcing the observed frames: at every step
    they are replaced by a fresh forward-noised copy of the truth (Video Diffusion Models' section 3.1)."""
    n = len(x_obs)
    obs = x_obs.reshape(n, -1)
    na = k_obs * N_PIX
    x = SMAX * rng.normal(size=(n, T * N_PIX))
    g = grid(n_steps)
    for s, s2 in zip(g[:-1], g[1:]):
        x[:, :na] = obs + s * rng.normal(size=obs.shape)
        d = denoise_clip(x, s)
        x = d + (s2 / s) * (x - d)
    x[:, :na] = obs
    return x.reshape(n, T, N_PIX)


def run_forecast(quick):
    n = 1024 if quick else 4096
    res = {"n": n, "observed": {}}
    real = sample_clips(np.random.default_rng(43), n)
    for k_obs in (1, 2, 3):
        row = {}
        for label, fn in (("replacement", replacement), ("exact", exact_condition)):
            x = fn(np.random.default_rng(2620 + k_obs), real[:, :k_obs], k_obs)
            st = clip_report(x)
            shown, amp, bright, _ = read_frames(x)
            dk = (shown[:, k_obs] - shown[:, k_obs - 1]) % K
            if k_obs == 1:
                cont = (dk == 1) | (dk == 3)
            else:
                cont = dk == (shown[:, 1] - shown[:, 0]) % K
            st["continues_motion"] = float(cont.mean())
            st["keeps_contrast"] = float(((amp[:, k_obs:] >= 0.75) == (amp[:, :1] >= 0.75)).all(1).mean())
            st["keeps_brightness"] = float((np.abs(bright[:, k_obs:] - bright[:, :1]) <= BRIGHT_TOL).all(1).mean())
            row[label] = {k: (r6(v) if isinstance(v, float) else v) for k, v in st.items() if k != "_example"}
            if label == "replacement":
                row[label]["_example"] = st["_example"]
            print(f"  forecast from {k_obs} frame{'s' if k_obs > 1 else ''}, {label:>11}: coherent {st['coherent_clips']:.4f} "
                  f"(motion continues {st['continues_motion']:.4f}, contrast kept {st['keeps_contrast']:.4f}, "
                  f"brightness kept {st['keeps_brightness']:.4f}; frames valid {st['valid_frames']:.4f})", flush=True)
        res["observed"][str(k_obs)] = row
    return res


# ------------------------------------------------------------------------------------ sds
SDS_WEIGHTS = (1.0, 2.0, 3.0, 5.0, 7.5, 15.0, 30.0, 101.0)


def sds(rng, n_runs, w, cls=0, n_iter=3000, lr=(0.3, 0.003)):
    """Score distillation sampling (DreamFusion's eq. 3) on one frame with an identity renderer:
    t ~ U(0.02, 0.98) on a cosine schedule (sigma_t / alpha_t = tan(pi t / 2)), weight sigma_t^2 with
    alpha_t absorbed, guidance x0_hat = D_u + w (D_c - D_u). The gradient alpha_t sigma_t (x - x0_hat)
    is DreamFusion's w(t) (eps_hat - eps) written through the denoiser."""
    x = 0.25 * rng.normal(size=(n_runs, N_PIX))              # a random start, like a fresh NeRF
    rates = np.geomspace(lr[0], lr[1], n_iter)
    for i in range(n_iter):
        t = rng.uniform(0.02, 0.98, n_runs)
        s = np.tan(np.pi * t / 2)
        xs = x + s[:, None] * rng.normal(size=x.shape)
        dc = denoise_frame(xs, s, cls)
        if w == 1.0:
            x0_hat = dc
        else:
            du = denoise_frame(xs, s)
            x0_hat = du + w * (dc - du)
        x = x - rates[i] * (0.5 * np.sin(np.pi * t))[:, None] * (x - x0_hat)
    return x


def frame_stats(x, cls=0):
    shown, amp, bright, detail = read_frames(x)
    a = amp
    return {"right_class": float((shown == cls).mean()), "faint": float(((a > WEAK) & (a < MID[0])).mean()),
            "blend": float(((a >= MID[0]) & (a <= MID[1])).mean()), "strong": float(((a > MID[1]) & (a < OVER)).mean()),
            "over": float((a >= OVER).mean()), "weak": float((a <= WEAK).mean()),
            "contrast_mean": float(a.mean()), "contrast_sd": float(a.std()),
            "contrast_faint_mean": float(a[a < 0.75].mean()) if (a < 0.75).any() else None,
            "contrast_strong_mean": float(a[a >= 0.75].mean()) if (a >= 0.75).any() else None,
            "brightness_sd": float(bright.std()), "detail_sd": float(detail.mean()),
            "distinct": int(len({(int(k), int(round(c / 0.05)), int(round(b / 0.05))) for k, c, b in zip(shown, a, bright)})),
            "nearest_other_median": float(np.median(np.sort(np.sqrt(np.maximum(
                (x ** 2).sum(1)[:, None] + (x ** 2).sum(1)[None] - 2 * x @ x.T, 0)), 1)[:, 1]))}


def run_sds(quick):
    n_runs = 64 if quick else 256
    n_iter = 1500 if quick else 3000
    res = {"runs": n_runs, "iterations": n_iter, "weights": {}, "real": frame_stats(sample_frames(np.random.default_rng(51), 4096, 0))}
    print(f"  real class-0 frames: {res['real']}", flush=True)
    for w in SDS_WEIGHTS:
        xs = sds(np.random.default_rng(2630), n_runs, w, n_iter=n_iter)
        xa = sample_frames_guided(np.random.default_rng(2631).normal(size=(n_runs * 4, N_PIX)), 0, w)
        st = {"sds": frame_stats(xs), "ancestral": frame_stats(xa)}
        st["sds"]["_example"] = [[round(float(v), 3) for v in img] for img in xs[:4]]
        st["ancestral"]["_example"] = [[round(float(v), 3) for v in img] for img in xa[:4]]
        st["sds"]["_contrast_runs"] = [round(float(v), 4) for v in read_frames(xs)[1]]
        st["ancestral"]["_contrast_quantiles"] = {str(q): round(float(np.quantile(read_frames(xa)[1], q)), 4)
                                                  for q in (0.05, 0.25, 0.5, 0.75, 0.95)}
        res["weights"][str(w)] = {side: {k: (r6(v) if isinstance(v, float) else v) for k, v in d.items()}
                                  for side, d in st.items()}
        a, b = st["sds"], st["ancestral"]
        print(f"  sds w {w:>5}: contrast {a['contrast_mean']:.3f} (sd {a['contrast_sd']:.3f}; faint {a['faint']:.3f} "
              f"blend {a['blend']:.3f} strong {a['strong']:.3f} over {a['over']:.3f}), brightness sd {a['brightness_sd']:.4f}, "
              f"detail {a['detail_sd']:.4f}, distinct {a['distinct']} | ancestral: contrast {b['contrast_mean']:.3f} "
              f"(faint {b['faint']:.3f} over {b['over']:.3f}), brightness sd {b['brightness_sd']:.3f}, detail {b['detail_sd']:.3f}",
              flush=True)
    return res


# --------------------------------------------------------------------------------- census
def wrapped_normal(theta, sigma, windings=12):
    k = np.arange(-windings, windings + 1)
    return np.exp(-(theta[..., None] + 2 * np.pi * k) ** 2 / (2 * sigma ** 2)).sum(-1) / (sigma * math.sqrt(2 * np.pi))


def run_census():
    rows = [  # (label, numbers, how) -- every factor from the papers' stated configurations
        ("QM9 molecule, EDM (29 atoms x 3 coordinates + 5 atom types + 1 charge)", 29 * (3 + 5 + 1), "raw"),
        ("GEOM-DRUGS molecule, average (44 atoms x 3 coordinates)", 44 * 3, "raw"),
        ("GEOM-DRUGS molecule, average torsion angles", 7.9, "reduced"),
        ("PVD point cloud (2,048 points x 3)", 2048 * 3, "raw"),
        ("Point-E point cloud (4,096 points x xyz + RGB)", 4096 * 6, "raw"),
        ("1 s of speech at 16 kHz (DiffWave)", 16000, "raw"),
        ("10 s of audio at 16 kHz (AudioLDM waveform)", 160000, "raw"),
        ("same 10 s as a 64-band mel spectrogram (hop 160)", (160000 // 160) * 64, "reduced"),
        ("same 10 s as AudioLDM's latent (r = 4, C = 8)", (160000 // 160 // 4) * (64 // 4) * 8, "latent"),
        ("95.1 s of 44.1 kHz stereo (Stable Audio window)", 2 * 4194304, "raw"),
        ("same window as Stable Audio's latent (1/1024 in time, 64 channels)", 64 * (4194304 // 1024), "latent"),
        ("16 frames of 64 x 64 RGB (Video Diffusion Models)", 16 * 64 * 64 * 3, "raw"),
        ("14 frames of 576 x 1024 RGB (Stable Video Diffusion)", 14 * 576 * 1024 * 3, "raw"),
        ("same 14 frames as SVD's latent (1/8 per side, 4 channels)", 14 * (576 // 8) * (1024 // 8) * 4, "latent"),
        ("one 256 x 256 RGB image, for scale", 256 * 256 * 3, "raw"),
    ]
    res = {"sizes": [{"label": l, "numbers": v, "kind": k} for l, v, k in rows]}
    res["compression"] = {"audio_stable_audio": (2 * 4194304) / (64 * (4194304 // 1024)),
                          "audio_audioldm_vs_waveform": 160000 / ((160000 // 160 // 4) * (64 // 4) * 8),
                          "video_svd": (14 * 576 * 1024 * 3) / (14 * 72 * 128 * 4)}
    res["receptive_field"] = {"samples": (3 - 1) * 3 * sum(2 ** i for i in range(10)) + 1,
                              "seconds_at_16k": ((3 - 1) * 3 * sum(2 ** i for i in range(10)) + 1) / 16000}
    theta = np.linspace(-np.pi, np.pi, 721)
    sig = {}
    for frac in (0.01, 0.1, 0.25, 0.5, 0.75, 1.0):
        s = frac * np.pi
        top = float(wrapped_normal(np.array([0.0]), s)[0])
        bottom = float(wrapped_normal(np.array([np.pi]), s)[0])
        line_mass = float(math.erf(np.pi / (s * math.sqrt(2))))    # a line Gaussian's mass inside -pi..pi
        sig[str(frac)] = {"sigma": s, "max_over_min": top / bottom if bottom > 0 else None,
                          "max_over_uniform": top * 2 * np.pi,
                          "line_gaussian_mass_inside": line_mass}
    res["wrapped_normal"] = sig
    res["curves"] = {"theta": [r4(v) for v in theta[::6]],
                     **{str(f): [r6(v) for v in wrapped_normal(theta[::6], f * np.pi)] for f in (0.25, 0.5, 1.0)},
                     **{f"line {f}": [r6(v) for v in np.exp(-theta[::6] ** 2 / (2 * (f * np.pi) ** 2)) / (f * np.pi * math.sqrt(2 * np.pi))]
                        for f in (0.25, 0.5, 1.0)}}
    for r in res["sizes"]:
        print(f"  {r['numbers']:>12,} {r['kind']:>7}  {r['label']}", flush=True)
    print(f"  compression: Stable Audio {res['compression']['audio_stable_audio']:.0f}x, AudioLDM vs waveform "
          f"{res['compression']['audio_audioldm_vs_waveform']:.0f}x, SVD {res['compression']['video_svd']:.0f}x; DiffWave "
          f"receptive field {res['receptive_field']['samples']} samples = {res['receptive_field']['seconds_at_16k']:.3f} s",
          flush=True)
    for f, v in sig.items():
        mm = f"{v['max_over_min']:.4f}" if v["max_over_min"] else "inf"
        print(f"  wrapped normal, sigma {f} pi: max/min {mm}, max/uniform {v['max_over_uniform']:.4f}, "
              f"line Gaussian keeps {v['line_gaussian_mass_inside']:.4f} of its mass in one turn", flush=True)
    return res


# ----------------------------------------------------------------------------------- main
_SRC = hashlib.sha1(Path(__file__).read_bytes()).hexdigest()[:12]


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
            f"numpy {np.__version__}; beyond.py {_SRC}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stage", choices=["worked", "video", "forecast", "sds", "census", "all"])
    ap.add_argument("--quick", action="store_true", help="fewer clips and runs")
    ap.add_argument("--out", default=None, help="write here instead of captures.json")
    ap.add_argument("--warp-variance", type=float, default=1.0,
                    help="video: scale the variance of the warped frames' noise (1 = an exact warp)")
    ap.add_argument("--fault", action="store_true", help="video: exercise E4's fault")
    args = ap.parse_args()
    out = Path(args.out) if args.out else HERE / "captures.json"
    prov = provenance()
    print(prov, flush=True)
    cap = json.loads(out.read_text()) if out.exists() and args.stage != "all" else {}
    cap.update({"provenance": prov, "source_sha1": _SRC, "quick": args.quick,
                "world": {"classes": K, "contrasts": list(AMPS), "faint_share": P_FAINT, "contrast_jitter": S_A,
                          "brightness_sd": S_B, "detail": TAU, "pixels": N_PIX, "frames": T,
                          "crescent_norm": round(NORM, 4), "over_threshold": round(OVER, 4),
                          "blend_band": [round(MID[0], 4), round(MID[1], 4)], "weak_threshold": round(WEAK, 4)}})
    t0 = time.time()
    stages = ["worked", "video", "forecast", "sds", "census"] if args.stage == "all" else [args.stage]
    for stage in stages:
        t = time.time()
        if stage == "worked":
            cap["worked"] = run_worked(args.quick)
        elif stage == "video":
            cap["video"] = run_video(args.quick, args.warp_variance, args.fault)
        elif stage == "forecast":
            cap["forecast"] = run_forecast(args.quick)
        elif stage == "sds":
            cap["sds"] = run_sds(args.quick)
        elif stage == "census":
            cap["census"] = run_census()
        print(f"  ({stage}: {time.time() - t:.0f} s)", flush=True)
        out.write_text(json.dumps(cap, indent=1) + "\n")
    print(f"wrote {os.path.relpath(out, Path.cwd())} in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
