#!/usr/bin/env python3
"""Lab for "Discrete Diffusion Language Models" (Diffusion Models series, part 11).

Crescent world as tokens. Every image is 8 x 8 tokens over a vocabulary of 28 grey levels: one of four
crescents, faint or strong, at one of nine brightness levels, with each pixel rounded to its grey level.
That is exactly 72 images, so a sample is valid only if it is one of them, and the exact denoiser of a
partly masked image is a lookup: which of the 72 images agree with the tokens already written. Every
failure below therefore belongs to the sampler, never to a badly trained network.

  worked     the article's worked example: part 1's 4x4 patch rounded to four grey levels, masked at
             abar = 0.64 with part 1's own noise draw, the uniform alternative, and the world made of the
             patch's four quarter turns, decoded one token at a time and all at once
  world      the 72-image world: its entropy, how many tokens decide an image, and the check that every
             order of revealing tokens gives the same total log-likelihood
  decode     samplers on the exact denoiser, 4,096 images each: one token per step (random order, ranked by
             how sure each position is, ranked by the probability of the token just drawn), greedy decoders,
             2 to 64 tokens per step, MDLM's ancestral update with 64 to 1,024 steps, a certainty threshold
  precision  MDLM's Gumbel race between [MASK] and one token, run in float32 and in float64
  all        everything, in that order (about a minute on one core)

Run:   python tokens.py all                       # the article's run
       python tokens.py all --quick               # 1,024 images per sampler, noisier numbers
       python tokens.py decode --levels 1         # exercise E3: every image at one brightness
       python tokens.py decode --fault            # exercise E4: something is wrong with one sampler
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
R = 8                                   # image side; 64 tokens
L = R * R
TURNS = 4                               # crescent orientations
A_C = 0.9                               # strong crescent RMS amplitude (parts 5-10)
AMPS = (0.5, 1.0)                       # faint and strong contrast
S_B = 0.3                               # brightness spread (parts 5-10)
STEP = 0.15                             # one grey level, and one brightness level
N_LEVELS = 9                            # brightness levels: -0.6 to 0.6 in steps of 0.15


# --------------------------------------------------------------------------- crescent world
def crescent_shape(r=R, inner=(0.64, 0.42, 0.30), supersample=8):
    """A crescent: a disc minus an offset disc, area-sampled onto r x r pixels (parts 5-10)."""
    g = (np.arange(r * supersample) + 0.5) / (r * supersample)
    yy, xx = np.meshgrid(g, g, indexing="ij")
    outer = (xx - 0.5) ** 2 + (yy - 0.5) ** 2 < 0.36 ** 2
    hole = (xx - inner[0]) ** 2 + (yy - inner[1]) ** 2 < inner[2] ** 2
    return (outer & ~hole).astype(float).reshape(r, supersample, r, supersample).mean(axis=(1, 3))


def unit(m):
    m = m.reshape(-1) - m.mean()
    return m * A_C / np.sqrt((m ** 2).mean())


MU = np.stack([unit(np.rot90(crescent_shape(), k)) for k in range(TURNS)])    # (4, 64)


class World:
    """The images, their probabilities, and the exact denoiser of a partly masked image."""

    def __init__(self, levels=N_LEVELS):
        b = STEP * (np.arange(levels) - levels // 2)
        pb = np.exp(-b ** 2 / (2 * S_B ** 2))
        pb /= pb.sum()
        imgs, prior, meta = [], [], []
        for k in range(TURNS):
            for j, a in enumerate(AMPS):
                for i, bb in enumerate(b):
                    imgs.append(np.floor((a * MU[k] + bb) / STEP + 0.5).astype(int))
                    prior.append(pb[i] / (TURNS * len(AMPS)))
                    meta.append((k, j, i))
        imgs = np.array(imgs)
        self.lowest = int(imgs.min())
        self.img = imgs - self.lowest                       # tokens 0 .. K-1
        self.K = int(self.img.max()) + 1
        self.prior = np.array(prior)
        self.meta = np.array(meta)                          # turn, contrast (0 faint, 1 strong), brightness level
        self.bright = b
        self.n = len(self.img)
        self.key = {tuple(r): i for i, r in enumerate(self.img)}
        assert len(self.key) == self.n, "two images rounded to the same tokens"
        oh = np.zeros((self.n, L, self.K))
        oh[np.arange(self.n)[:, None], np.arange(L)[None, :], self.img] = 1.0
        self.onehot = oh.reshape(self.n, L * self.K)

    def entropy(self):
        return float(-(self.prior * np.log(self.prior)).sum())

    def predict(self, mism):
        """Exact denoiser. mism[m, c] counts the written tokens of image m that image c disagrees with.
        The posterior keeps the images that disagree least (none, whenever the tokens are consistent),
        weighted by their probability; a sampler that wrote an impossible combination is continued from
        its nearest images instead of from nothing."""
        w = self.prior[None] * (mism == mism.min(1, keepdims=True))
        w /= w.sum(1, keepdims=True)
        return (w @ self.onehot).reshape(len(mism), L, self.K)

    def write(self, x, mism, sel, vals):
        """Write vals where sel is set and update every image's disagreement count."""
        m, i = np.nonzero(sel)
        x[m, i] = vals[m, i]
        np.add.at(mism, m, (self.img[:, i].T != vals[m, i][:, None]).astype(np.int32))


def r4(v):
    return round(float(v), 4)


def r6(v):
    return round(float(v), 6)


def draw(P, u):
    """One token from each row of P (..., K), by inverse CDF with the uniforms u (...)."""
    c = np.cumsum(P, -1)
    c[..., -1] = 1.0
    return (c < u[..., None]).sum(-1)


def report(world, x, calls=None, examples=0):
    """Valid share, how many of the 72 images appear, distance to the world, and two attributes."""
    v = np.array([world.key.get(tuple(r), -1) for r in x])
    ok = v >= 0
    out = {"valid": r4(ok.mean())}
    if calls is not None:
        out["calls"] = r4(np.mean(calls))
    if examples:
        out["examples"] = x[:examples].tolist()
    if ok.any():
        freq = np.bincount(v[ok], minlength=world.n) / ok.sum()
        nz = freq[freq > 0]
        out.update(images_found=int((freq > 0).sum()), tv_to_world=r4(0.5 * np.abs(freq - world.prior).sum()),
                   entropy=r4(-(nz * np.log(nz)).sum()), strong=r4(world.meta[v[ok], 1].mean()),
                   brightness_sd=r4(world.bright[world.meta[v[ok], 2]].std()))
    return out


def fmt(res):
    return ", ".join(f"{k} {v}" for k, v in res.items() if k != "examples")


# --------------------------------------------------------------------------------- worked
X0 = np.array([[0.95, 0.60, -0.30, -0.85], [0.80, 0.45, -0.55, -0.90],
               [0.55, 0.10, -0.70, -0.95], [0.25, -0.20, -0.85, -1.00]])     # part 1's patch
EPS = np.array([[-0.55, 1.40, 0.45, -1.10], [0.85, -1.35, -0.25, 0.70],
                [1.25, 0.30, -0.95, 0.15], [-1.05, 0.90, 1.45, -1.10]])      # part 1's noise draw
ABAR = 0.64
EDGES = (-0.5, 0.0, 0.5)                                                      # four grey levels


def norm_ppf(p):
    """Inverse of the standard normal CDF, by bisection on erf (no scipy)."""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 0.5 * (1 + math.erf(mid / math.sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def run_worked(quick):
    tok = np.digitize(X0, EDGES)                            # 0 darkest .. 3 brightest
    turns = np.stack([np.rot90(tok, k) for k in range(4)])  # the four-turn world, equally likely
    cut = norm_ppf(ABAR)                                    # Phi(eps) > 0.64 masks: the same draw, as a uniform
    masked = EPS > cut
    res = {"tokens": tok.tolist(), "turns": turns.tolist(), "abar": ABAR, "eps_cut": r4(cut),
           "masked": masked.astype(int).tolist(), "n_masked": int(masked.sum()), "expected_masked": r4(16 * (1 - ABAR))}
    res["uniform"] = {"stay": r4(ABAR + (1 - ABAR) / 4), "each_other": r4((1 - ABAR) / 4)}
    res["absorbing"] = {"stay": ABAR, "to_mask": r4(1 - ABAR)}
    # the exact denoiser of the four-turn world, given the unmasked tokens
    agree = [(turns[k][~masked] == tok[~masked]).all() for k in range(4)]
    res["consistent_turns_at_mask"] = [k for k in range(4) if agree[k]]
    # a reverse step from abar 0.64 to 0.8: each masked token is revealed with this probability
    res["reveal_prob_064_to_08"] = r4((0.8 - ABAR) / (1 - ABAR))
    res["loss_weight_at_t"] = {"t": r4(1 - ABAR), "weight": r4(1 / (1 - ABAR))}
    # everything masked: per-position marginals over the four turns
    marg = np.zeros((4, 4, 4))
    for k in range(4):
        marg[np.arange(4)[:, None], np.arange(4)[None, :], turns[k]] += 0.25
    res["marginals"] = marg.round(4).tolist()
    res["marginal_top_left"] = [r4(p) for p in marg[0, 0]]
    sure = marg.max(-1)
    res["positions_with_one_answer"] = int((sure == 1).sum())
    # the two dark-or-bright corners drawn at once: top-left and bottom-right
    a, b = marg[0, 0], marg[3, 3]
    pairs_ok = {(int(turns[k][0, 0]), int(turns[k][3, 3])) for k in range(4)}
    res["corners"] = {"pairs_in_world": sorted([list(p) for p in pairs_ok]),
                      "p_consistent": r4(sum(a[i] * b[j] for i, j in pairs_ok)),
                      "p_both_darkest": r4(a[0] * b[0])}
    ex_rng = np.random.default_rng(5)                       # one draw of all 16 at once, for the figure
    res["all_at_once_example"] = draw(marg, ex_rng.random((4, 4))).tolist()
    p_all = sum(np.prod([marg[i, j, turns[k][i, j]] for i in range(4) for j in range(4)]) for k in range(4))
    res["p_valid_all_16_at_once"] = float(f"{p_all:.6g}")
    # two tokens at once, first step: the chance they come from one turn
    pairs = []
    for a in range(16):
        for b in range(a + 1, 16):
            ia, ja, ib, jb = a // 4, a % 4, b // 4, b % 4
            pv = sum(marg[ia, ja, va] * marg[ib, jb, vb]
                     for va in range(4) for vb in range(4)
                     if any(turns[k][ia, ja] == va and turns[k][ib, jb] == vb for k in range(4)))
            pairs.append(pv)
    res["p_two_at_once_consistent_mean"] = r4(np.mean(pairs))
    # one token at a time, in a fixed order: the costs add up to ln 4 for every turn
    order = [(0, 0), (0, 3), (3, 3), (1, 1)] + [(i, j) for i in range(4) for j in range(4) if (i, j) not in
                                                 [(0, 0), (0, 3), (3, 3), (1, 1)]]
    chain = []
    for k in range(4):
        alive, total, steps = [0, 1, 2, 3], 0.0, []
        for (i, j) in order:
            vals = [turns[c][i, j] for c in alive]
            p = vals.count(turns[k][i, j]) / len(vals)
            total += -math.log(p)
            alive = [c for c in alive if turns[c][i, j] == turns[k][i, j]]
            steps.append({"pos": [i, j], "token": int(turns[k][i, j]), "p": r4(p), "turns_left": len(alive)})
        chain.append({"turn": k, "nats": r6(total), "decided_after": next(n + 1 for n, s in enumerate(steps)
                                                                         if s["turns_left"] == 1),
                      "first_steps": steps[:4]})
    res["sequential"] = chain
    res["ln4"] = r6(math.log(4))
    print(f"  patch as tokens: {tok.tolist()}; masked at abar 0.64 where eps > {cut:.4f}: "
          f"{int(masked.sum())} of 16 (expected {16 * (1 - ABAR):.2f}); uniform keeps each token with "
          f"probability {ABAR + (1 - ABAR) / 4:.2f}", flush=True)
    print(f"  four-turn world: turns consistent with the unmasked tokens {res['consistent_turns_at_mask']}; "
          f"the two corners at once belong to a turn {res['corners']['p_consistent']} of the time "
          f"(both darkest {res['corners']['p_both_darkest']}); "
          f"all 16 at once valid with probability {p_all:.3g}; two at once {np.mean(pairs):.4f}; "
          f"sequential costs {[c['nats'] for c in chain]} nats (ln 4 = {math.log(4):.4f}), decided after "
          f"{[c['decided_after'] for c in chain]} tokens", flush=True)
    return res


# ---------------------------------------------------------------------------------- world
def run_world(world, quick, rng):
    res = {"images": world.n, "vocabulary": world.K, "tokens": L, "entropy_nats": r4(world.entropy()),
           "entropy_bits": r4(world.entropy() / math.log(2)), "brightness_levels": [r4(b) for b in world.bright],
           "brightness_sd": r4(math.sqrt((world.prior * world.bright[world.meta[:, 2]] ** 2).sum())),
           "rarest_image": r6(world.prior.min()), "commonest_image": r6(world.prior.max())}
    mid = len(world.bright) // 2
    pick = lambda k, j, i: int(np.nonzero((world.meta == (k, j, i)).all(1))[0][0])
    res["examples"] = {"turn0_strong_by_level": [world.img[pick(0, 1, i)].tolist() for i in range(len(world.bright))],
                       "middle_level": [world.img[pick(k, j, mid)].tolist() for k in range(TURNS) for j in (0, 1)]}
    # every order of revealing one image's tokens gives -log p(image): the exact denoiser is a consistent joint
    orders = 16 if quick else 64
    worst, decided = 0.0, []
    for c in range(world.n):
        for _ in range(orders):
            order = rng.permutation(L)
            mism = np.zeros((1, world.n), np.int32)
            x = -np.ones((1, L), int)
            total, done = 0.0, None
            for n, pos in enumerate(order):
                P = world.predict(mism)[0, pos]
                total += -math.log(P[world.img[c, pos]])
                sel = np.zeros((1, L), bool)
                sel[0, pos] = True
                world.write(x, mism, sel, world.img[c][None])
                if done is None and (mism[0] == 0).sum() == 1:
                    done = n + 1
            worst = max(worst, abs(total + math.log(world.prior[c])))
            decided.append(done)
    decided = np.array(decided)
    res["order_check"] = {"orders_per_image": orders, "max_abs_error_nats": float(f"{worst:.3g}")}
    res["decided_after"] = {"median": float(np.median(decided)), "mean": r4(decided.mean()),
                            "p90": float(np.quantile(decided, 0.9)), "max": int(decided.max()),
                            "histogram": {str(k): r4((decided == k).mean()) for k in range(1, int(decided.max()) + 1)}}
    print(f"  {world.n} images of {L} tokens over {world.K} grey levels; entropy {world.entropy():.4f} nats; "
          f"brightness sd {res['brightness_sd']}", flush=True)
    print(f"  every reveal order gives -log p(image) to {worst:.1e} nats ({orders} orders x {world.n} images); "
          f"a random order decides the image after {np.median(decided):.0f} tokens (median), "
          f"{np.quantile(decided, 0.9):.0f} (90th percentile), {decided.max()} at most", flush=True)
    return res


# --------------------------------------------------------------------------------- decode
def decode(world, rng, M, steps=None, rank="random", greedy=False, threshold=None, fault=False):
    """LLaDA-style decoding: each step predicts every masked token, then keeps some of them. rank decides
    which: 'random' positions, 'position' (how sure the denoiser is of a position, before drawing) or
    'drawn' (the probability of the token just drawn there, as LLaDA's low_confidence does). With
    threshold, keep every position at least that sure, and always the surest one."""
    x = -np.ones((M, L), int)
    mism = np.zeros((M, world.n), np.int32)
    calls = np.zeros(M, int)
    if threshold is None:
        per = np.full(steps, L // steps)
        per[:L % steps] += 1
    for s in range(L if threshold is not None else steps):
        masked = x < 0
        if not masked.any():
            break
        P = world.predict(mism)
        x0 = P.argmax(-1) if greedy else draw(P, rng.random((M, L)))
        p_drawn = np.take_along_axis(P, x0[..., None], -1)[..., 0]
        sure = P.max(-1)
        if rank == "random":
            score = rng.random((M, L))
        elif rank == "drawn" or (rank == "position" and fault):
            score = p_drawn + 1e-9 * rng.random((M, L))     # ties broken at random
        else:
            score = sure + 1e-9 * rng.random((M, L))
        score = np.where(masked, score, -np.inf)
        if threshold is None:
            idx = np.argsort(-score, 1)[:, :per[s]]
            sel = np.zeros_like(masked)
            np.put_along_axis(sel, idx, True, 1)
            sel &= masked
        else:
            sel = masked & (sure >= threshold)
            best = np.argmax(score, 1)
            sel[np.arange(M), best] |= masked[np.arange(M), best]
        calls += masked.any(1)
        world.write(x, mism, sel, x0)
    return x, calls


def ancestral(world, rng, M, N):
    """MDLM's ancestral update, linear schedule alpha_t = 1 - t, N uniform steps: from t to s each masked
    token is revealed with probability (t - s) / t and then drawn from the denoiser; the network is called
    again only when something changed (MDLM's caching). This is the float64 race, drawn exactly."""
    x = -np.ones((M, L), int)
    mism = np.zeros((M, world.n), np.int32)
    calls = np.zeros(M, int)
    t = np.linspace(1.0, 0.0, N + 1)
    P = world.predict(mism)
    calls += 1
    stale = np.zeros(M, bool)
    together = 0                                            # tokens revealed in a step that revealed another
    for n in range(N):
        masked = x < 0
        if not masked.any():
            break
        if stale.any():
            P[stale] = world.predict(mism[stale])
            calls += stale
            stale[:] = False
        go = masked & (rng.random((M, L)) < (t[n] - t[n + 1]) / t[n])
        if go.any():
            k = go.sum(1)
            together += int(k[k >= 2].sum())
            x0 = draw(P, rng.random((M, L)))
            world.write(x, mism, go, x0)
            stale = go.any(1)
    return x, calls, together / (M * L)


def run_decode(world, quick, rng, fault=False):
    M = 1024 if quick else 4096
    ex = 8                                                  # sample images kept for the figures
    res = {"images_per_sampler": M, "one_per_step": {}, "parallel": {}, "ancestral": {}}
    for rank in ("random", "position", "drawn"):
        x, c = decode(world, rng, M, steps=L, rank=rank, fault=fault)
        res["one_per_step"][rank] = report(world, x, c, ex)
        print(f"  one token per step, {rank:8s}: {fmt(res['one_per_step'][rank])}", flush=True)
    for rank in ("random", "drawn"):
        x, c = decode(world, rng, M, steps=L, rank=rank, greedy=True)
        res["one_per_step"]["greedy_" + rank] = report(world, x, c, ex)
        print(f"  greedy, {rank:8s}         : {fmt(res['one_per_step']['greedy_' + rank])}", flush=True)
    for k in (2, 4, 8, 16, 64):
        for rank in ("random", "drawn"):
            x, c = decode(world, rng, M, steps=L // k, rank=rank)
            res["parallel"][f"{rank}_{k}"] = report(world, x, c, ex if rank == "random" else 0)
            print(f"  {k:2d} per step, {rank:8s}  : {fmt(res['parallel'][f'{rank}_{k}'])}", flush=True)
    for N in (64, 256, 1024):
        x, c, together = ancestral(world, rng, M, N)
        res["ancestral"][str(N)] = report(world, x, c)
        res["ancestral"][str(N)]["revealed_alongside_another"] = r4(together)
        print(f"  MDLM ancestral, {N:4d} steps: {fmt(res['ancestral'][str(N)])}", flush=True)
    for name, tau in (("0.9", 0.9), ("certain", 1 - 1e-9)):
        x, c = decode(world, rng, M, rank="position", threshold=tau)
        res[f"threshold_{name}"] = report(world, x, c, ex)
        print(f"  certainty threshold {name:7s}: {fmt(res[f'threshold_{name}'])}", flush=True)
    return res


# ------------------------------------------------------------------------------- precision
def race_e(u, dtype):
    """MDLM's and SEDD's race variable, E = 1e-10 - log(u + 1e-10), computed in dtype."""
    u = u.astype(dtype)
    return (dtype(1e-10) - np.log(u + dtype(1e-10))).astype(dtype)


def run_precision(quick, rng):
    """[MASK] has weight 1 and a token weight c; the token wins when c / E_token > 1 / E_mask, which in
    exact arithmetic happens with probability c / (1 + c). E_mask is at most 23.03 (the 1e-10 offset caps
    it), so the token can only win when E_token < 23.03 c, that is when its uniform lands within about 30 c
    of 1. The race is drawn there: E_mask from a full uniform in the given precision, the token's uniform
    from that interval (in float32, from the representable values 1 - j 2^-24 inside it), and every win is
    reweighted by the interval's probability. Nothing outside the interval can win, so this is exact."""
    n = 200_000 if quick else 2_000_000
    cs = [1e-9, 3e-9, 1e-8, 2e-8, 3e-8, 5e-8, 1e-7, 2e-7, 5e-7, 1e-6, 1e-5]
    out = {"draws_per_c": n, "c": cs, "float32": [], "float64": [], "closed_form_float32": []}
    for c in cs:
        span = 30 * c                                       # probability of the token's interval below 1
        J = max(1, int(span * 2 ** 24))                     # float32 grid points 1 - j 2^-24 inside it
        e_m32 = race_e(rng.random(n, dtype=np.float32), np.float32)
        j = rng.integers(1, J + 1, n)
        e_t32 = race_e((1.0 - j * 2.0 ** -24).astype(np.float32), np.float32)
        win32 = (np.float32(c) / e_t32 > np.float32(1.0) / e_m32).mean() * J * 2.0 ** -24
        e_m64 = race_e(rng.random(n), np.float64)
        e_t64 = race_e(1.0 - rng.random(n) * span, np.float64)
        win64 = (c / e_t64 > 1.0 / e_m64).mean() * span
        x = 2.0 ** -24 / c
        out["float32"].append(r6(win32 / c))
        out["float64"].append(r6(win64 / c))
        out["closed_form_float32"].append(r6(x / math.expm1(x)))
    lo, hi = 0.1, 5.0                                       # x / (e^x - 1) = 1/2: float32 halves a token's chance
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if mid / math.expm1(mid) > 0.5 else (lo, mid)
    half = 2.0 ** -24 / lo
    out["half_share_x"] = r6(lo)
    out["half_share_c"] = float(f"{half:.4g}")
    out["half_share_p_first_step"] = {str(N): float(f"{half * (N - 1):.3g}") for N in (1000, 2048, 10000, 50000)}
    out["even_share"] = {"gpt2_50257": float(f"{1 / 50257:.3g}"), "llada_126464": float(f"{1 / 126464:.3g}")}
    print("  token weight c / [MASK] weight -> share of its fair chance (float32, float64, closed form):", flush=True)
    for c, a, b, f in zip(cs, out["float32"], out["float64"], out["closed_form_float32"]):
        print(f"    c = {c:.0e}: {a:.4f}  {b:.4f}  {f:.4f}", flush=True)
    print(f"  float32 halves a token's chance below c = {half:.3g}; at the first step of an N-step MDLM run "
          f"that is p below {out['half_share_p_first_step']}", flush=True)
    return out


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
            f"numpy {np.__version__}; tokens.py {_SRC}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stage", choices=["worked", "world", "decode", "precision", "all"])
    ap.add_argument("--quick", action="store_true", help="1,024 images per sampler and fewer race draws")
    ap.add_argument("--out", default=None, help="write here instead of captures.json")
    ap.add_argument("--levels", type=int, default=N_LEVELS, help="brightness levels in the world (odd; 1 = none)")
    ap.add_argument("--fault", action="store_true", help="decode: exercise E4's fault")
    args = ap.parse_args()
    out = Path(args.out) if args.out else HERE / "captures.json"
    prov = provenance()
    print(prov, flush=True)
    world = World(args.levels)
    cap = json.loads(out.read_text()) if out.exists() and args.stage != "all" else {}
    cap.update({"provenance": prov, "source_sha1": _SRC, "quick": args.quick, "levels": args.levels,
                "fault": args.fault})
    t0 = time.time()
    stages = ["worked", "world", "decode", "precision"] if args.stage == "all" else [args.stage]
    for stage in stages:
        t = time.time()
        rng = np.random.default_rng({"worked": 11, "world": 12, "decode": 13, "precision": 14}[stage])
        if stage == "worked":
            cap["worked"] = run_worked(args.quick)
        elif stage == "world":
            cap["world"] = run_world(world, args.quick, rng)
        elif stage == "decode":
            cap["decode"] = run_decode(world, args.quick, rng, args.fault)
        elif stage == "precision":
            cap["precision"] = run_precision(args.quick, rng)
        print(f"  ({stage}: {time.time() - t:.0f} s)", flush=True)
        out.write_text(json.dumps(cap, indent=1) + "\n")
    print(f"wrote {os.path.relpath(out, Path.cwd())} in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
