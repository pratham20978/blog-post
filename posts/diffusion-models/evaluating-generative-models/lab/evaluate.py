#!/usr/bin/env python3
"""Lab for "Evaluating Generative Models: What FID Measures and Hides" (Diffusion Models series, part 9).

Crescent world again: every 8x8 image shows one of four crescents, faint or strong, with a random
brightness and a little pixel noise. The world is known exactly, so every generator below has a known
defect, and every metric can be checked against what is actually wrong with the samples.

  worked     the article's worked example: eight real crescent contrasts and three generators, the
             Frechet distance by the one-number formula and by the general code; then precision,
             recall, density and coverage on a second small set, with and without one stray sample
  failures   five generators against a 32,768-image training set: a perfect one, a copier, one that
             drops the faint crescents, a grainy one whose grain is turned up until its FD matches,
             and a Gaussian with the data's mean and covariance; FD on the pixels and on five
             "detector" features, KID, precision, recall, density and coverage (about 11 s)
  bias       FD against the number of samples N, from 1,000 to 64,000, for a perfect and a slightly
             grainy generator, 24 repeats each, and the 1/N fit that extrapolates N to infinity (10 s)
  guidance   part 8's exact guidance sweep (w = 1 to 7.5) seen through every metric, with recall and
             coverage split by faint and strong real images, and what covers the faint ones (22 s)
  all        everything, in that order (about 45 s on one core)

Every number is computed on the 64 pixel values (or the five detector features). The real metric runs
the same arithmetic on 2,048 Inception-v3 features; nothing here downloads a network.

Run:   python evaluate.py all                 # the article's run
       python evaluate.py all --quick         # fewer repeats and samples, noisier numbers
       python evaluate.py failures --grain 0.3    # the failures stage with a grain you choose
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
R = 8                                   # image side; 64 pixels
N_PIX = R * R
SMAX, SMIN, RHO = 80.0, 0.002, 7.0      # EDM's noise range and step spacing (part 8's sampler)
N_TRAIN = 32768                         # the "training set" FD and KID compare against
N_EVAL = 4096                           # images per generated set, and real images for the k-NN metrics
K_PR, K_DC = 3, 5                       # neighbours: Kynkaanniemi et al.'s k for P/R, Naeem et al.'s for D/C


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


MU = np.stack([unit(np.rot90(crescent_shape(), k)) for k in range(K)])    # (K, 64), zero mean, equal norms
NORM = float(np.linalg.norm(MU[0]))                                        # 7.2
MU_HAT = MU / NORM
V_E = S_B ** 2 * N_PIX + TAU ** 2                          # data variance along the brightness axis
LAM = TAU ** 2 + (S_A * NORM) ** 2                         # data variance along a component's own crescent
SPREAD = math.sqrt(S_A ** 2 + (TAU / NORM) ** 2)           # contrast spread of one sub-mode: 0.0616
OVER = AMPS[1] + 3 * SPREAD                                 # contrast no real strong crescent exceeds (1.185)
MID = (AMPS[0] + 3 * SPREAD, AMPS[1] - 3 * SPREAD)          # contrasts no real crescent has (0.685..0.815)
WEAK = AMPS[0] - 3 * SPREAD                                 # below this, weaker than any real faint crescent (0.315)
DETECTOR = np.vstack([MU_HAT, np.ones(N_PIX) / math.sqrt(N_PIX)])   # 5 unit directions: 4 crescents, brightness


def sample_data(rng, n, cls=None, faint=None):
    """x0 = a mu_k + b 1 + tau z: k uniform (or fixed), a faint or strong (+ jitter), b ~ N(0, s_b^2).
    faint=False draws only strong crescents, faint=True only faint ones."""
    k = rng.integers(0, K, n) if cls is None else np.full(n, cls)
    if faint is None:
        j = (rng.random(n) >= P_FAINT).astype(int)        # 0 faint, 1 strong
    else:
        j = np.full(n, 0 if faint else 1)
    a = np.array(AMPS)[j] + S_A * rng.normal(size=n)
    b = rng.normal(0.0, S_B, n)
    return a[:, None] * MU[k] + b[:, None] + TAU * rng.normal(size=(n, N_PIX))


def contrast(x, cls=None):
    """Which crescent an image shows (the largest projection), and how strongly, as a fraction of
    a strong crescent; with cls given, the amount of that crescent instead."""
    c = (x - x.mean(1, keepdims=True)) @ MU_HAT.T / NORM
    shown = np.argmax(c, 1)
    amp = c[np.arange(len(x)), shown if cls is None else np.full(len(x), cls)]
    return shown, amp


def truth(x, cls=None):
    """What is actually in a set of images, read with the world's own rulers."""
    shown, amp = contrast(x, cls)
    resid = x - x.mean(1, keepdims=True) - ((x - x.mean(1, keepdims=True)) @ MU_HAT.T) @ np.linalg.pinv(MU_HAT).T
    out = {"faint": float((amp < 0.75).mean()),
           "blend": float(((amp > MID[0]) & (amp < MID[1])).mean()),
           "over": float((amp > OVER).mean()),
           "off_contrast": float(((amp < WEAK) | ((amp > MID[0]) & (amp < MID[1])) | (amp > OVER)).mean()),
           "brightness_sd": float(x.mean(1).std()),
           "detail_sd": float(resid.std() * math.sqrt(N_PIX / (N_PIX - 1 - K)))}
    if cls is None:
        out["classes"] = [float((shown == k).mean()) for k in range(K)]
    return out


# ------------------------------------------------------------------- part 8's exact sampler
def components(cls):
    return [(k, j) for k in (range(K) if cls is None else [cls]) for j in (0, 1)]


def denoise(x, s, cls=None):
    """Exact D(x; s) = E[x0 | x0 + s eps = x], or E[x0 | x, class cls] (part 8, unchanged)."""
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
    return [float(sig_u(i / n)) for i in range(n)] + [0.0]


def sample_exact(z, cls, w=1.0, n=128):
    """DDIM on the exact denoisers with classifier-free guidance at weight w (part 8, unchanged)."""
    x = SMAX * z
    g = grid(n)
    for s, s2 in zip(g[:-1], g[1:]):
        dc = denoise(x, s, cls)
        if w == 1.0:
            d = dc
        else:
            du = denoise(x, s)
            d = du + w * (dc - du)
        x = d + (s2 / s) * (x - d)
    return x


# --------------------------------------------------------------------------------- metrics
def moments(f):
    """The two numbers per dimension FID keeps: the mean vector and the covariance matrix."""
    return f.mean(0), np.cov(f, rowvar=False)


def sqrtm_psd(a):
    """Square root of a symmetric positive semi-definite matrix, through its eigenvectors."""
    w, v = np.linalg.eigh(a)
    return (v * np.sqrt(np.clip(w, 0, None))) @ v.T


def frechet(m1, s1, m2, s2):
    """||m1 - m2||^2 + Tr(S1 + S2 - 2 (S1 S2)^(1/2)), with the trace of the square root taken from
    the symmetric matrix S1^(1/2) S2 S1^(1/2), which has the same eigenvalues as S1 S2."""
    r1 = sqrtm_psd(s1)
    tr_cross = float(np.sqrt(np.clip(np.linalg.eigvalsh(r1 @ s2 @ r1), 0, None)).sum())
    return float(((m1 - m2) ** 2).sum() + np.trace(s1) + np.trace(s2) - 2 * tr_cross)


def fd(x, ref):
    """Frechet distance between a set of feature vectors and reference moments (mean, covariance)."""
    return frechet(*moments(x), *ref)


def kid(x, y, subset=1000, n_sub=20, seed=0):
    """Kernel distance (KID): unbiased squared MMD with the cubic kernel (a.b/d + 1)^3, averaged over
    random subsets of `subset` images from each set; returns (mean, standard deviation)."""
    rng = np.random.default_rng(seed)
    d = x.shape[1]
    m = min(subset, len(x), len(y))
    vals = []
    for _ in range(n_sub):
        a = x[rng.choice(len(x), m, replace=False)]
        b = y[rng.choice(len(y), m, replace=False)]
        kaa = (a @ a.T / d + 1) ** 3
        kbb = (b @ b.T / d + 1) ** 3
        kab = (a @ b.T / d + 1) ** 3
        vals.append((kaa.sum() - np.trace(kaa)) / (m * (m - 1)) + (kbb.sum() - np.trace(kbb)) / (m * (m - 1))
                    - 2 * kab.mean())
    return float(np.mean(vals)), float(np.std(vals))


def _dist(a, b):
    return np.sqrt(np.maximum((a ** 2).sum(1)[:, None] + (b ** 2).sum(1)[None] - 2 * a @ b.T, 0))


def kth_radius(a, k, chunk=1024):
    """Distance from each row of a to its k-th nearest other row: the radius of its k-NN ball."""
    out = np.empty(len(a))
    for i in range(0, len(a), chunk):
        out[i:i + chunk] = np.sort(_dist(a[i:i + chunk], a), 1)[:, k]     # column 0 is the row itself
    return out


def inside(points, centres, radii, chunk=1024):
    """Boolean matrix: point p lies in the ball of centre c (distance <= c's radius)."""
    out = np.empty((len(points), len(centres)), bool)
    for i in range(0, len(points), chunk):
        out[i:i + chunk] = _dist(points[i:i + chunk], centres) <= radii[None]
    return out


def prdc(real, fake, k_pr=K_PR, k_dc=K_DC, detail=False):
    """Improved precision and recall (Kynkaanniemi et al. 2019, k = 3) and density and coverage
    (Naeem et al. 2020, k = 5). Precision: share of fakes inside some real ball. Recall: share of reals
    inside some fake ball. Density: real balls per fake, over k. Coverage: share of real balls that
    hold a fake."""
    r_real_pr, r_real_dc, r_fake = kth_radius(real, k_pr), kth_radius(real, k_dc), kth_radius(fake, k_pr)
    in_real_pr = inside(fake, real, r_real_pr)
    in_real_dc = inside(fake, real, r_real_dc)
    in_fake = inside(real, fake, r_fake)
    res = {"precision": float(in_real_pr.any(1).mean()), "recall": float(in_fake.any(1).mean()),
           "density": float(in_real_dc.sum() / (k_dc * len(fake))), "coverage": float(in_real_dc.any(0).mean())}
    if detail:
        res["_recalled"] = in_fake.any(1)              # per real image: inside some fake ball
        res["_covered"] = in_real_dc.any(0)            # per real image: its ball holds a fake
        res["_in_fake"] = in_fake
        res["_r_fake"] = r_fake
    return res


def r4(v):
    return round(float(v), 4)


def r6(v):
    return round(float(v), 6)


# --------------------------------------------------------------------------------- worked
WORKED_REAL = [0.45, 0.50, 0.50, 0.55, 0.95, 1.00, 1.00, 1.05]        # faint and strong crescents
WORKED_GEN = {"strong only": [0.95, 1.00, 1.00, 1.05, 0.95, 1.00, 1.00, 1.05],
              "all too faint": [0.35, 0.40, 0.40, 0.45, 0.85, 0.90, 0.90, 0.95],
              "moment matched": [0.35, 0.50, 0.60, 0.65, 0.85, 0.90, 1.00, 1.15]}
PR_REAL = [0.40, 0.45, 0.50, 0.55, 0.60, 0.90, 0.95, 1.00, 1.05, 1.10]  # five faint, five strong
PR_GEN = [0.92, 0.96, 1.00, 1.04, 1.08]                                  # strong only
PR_OUTLIER = 0.25                                                        # one stray, too-faint image


def run_worked():
    real = np.array(WORKED_REAL)
    m_r, s_r = real.mean(), real.std()           # the population formula: divide by 8, as on paper
    res = {"real": {"values": WORKED_REAL, "mean": r6(m_r), "sd": r6(s_r)}, "generators": {}}
    print(f"  worked: real contrasts {WORKED_REAL}: mean {m_r:.4f}, spread {s_r:.4f}", flush=True)
    for name, vals in WORKED_GEN.items():
        g = np.array(vals)
        m_g, s_g = g.mean(), g.std()
        fd1 = (m_r - m_g) ** 2 + (s_r - s_g) ** 2
        general = frechet(np.array([m_r]), np.array([[s_r ** 2]]), np.array([m_g]), np.array([[s_g ** 2]]))
        near = int(sum(np.min(np.abs(real - v)) <= 0.05 + 1e-9 for v in g))
        res["generators"][name] = {"values": vals, "mean": r6(m_g), "sd": r6(s_g), "mean_term": r6((m_r - m_g) ** 2),
                                   "spread_term": r6((s_r - s_g) ** 2), "fd": r6(fd1), "fd_general": r6(general),
                                   "within_0.05_of_a_real": near}
        print(f"  worked: {name:>14}: mean {m_g:.4f}, spread {s_g:.4f}; FD = {(m_r - m_g) ** 2:.4f} + "
              f"{(s_r - s_g) ** 2:.4f} = {fd1:.4f} (general code {general:.4f}); {near}/8 within 0.05 of a real value",
              flush=True)
    pr = {}
    real2 = np.array(PR_REAL)[:, None]
    for name, fake in (("strong only", PR_GEN), ("strong + one stray", PR_GEN + [PR_OUTLIER])):
        f = np.array(fake)[:, None]
        m = prdc(real2, f, k_pr=2, k_dc=2, detail=True)
        pr[name] = {"fake": fake, "precision": r4(m["precision"]), "recall": r4(m["recall"]),
                    "density": r4(m["density"]), "coverage": r4(m["coverage"]),
                    "real_radii": [r4(v) for v in kth_radius(real2, 2)], "fake_radii": [r4(v) for v in m["_r_fake"]]}
        print(f"  worked: k-NN metrics (k = 2), {name:>16}: precision {m['precision']:.3f}, recall {m['recall']:.3f}, "
              f"density {m['density']:.3f}, coverage {m['coverage']:.3f}", flush=True)
    res["prdc"] = {"real": PR_REAL, "k": 2, "sets": pr}
    return res


# ------------------------------------------------------------------------------- failures
def grainy(x, g, seed):
    return x + g * np.random.default_rng(seed).normal(size=x.shape)


def tune_grain(target, base, ref, seed):
    """Turn the grain up until the grainy set's FD equals target (bisection; FD rises with grain)."""
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if fd(grainy(base, mid, seed), ref) < target else (lo, mid)
    return 0.5 * (lo + hi)


def run_failures(quick, grain=None):
    n_train = N_TRAIN // 4 if quick else N_TRAIN
    n = N_EVAL // 2 if quick else N_EVAL
    train = sample_data(np.random.default_rng(1), n_train)
    real = train[:n]                                           # real images for the k-NN metrics
    ref_pix, ref_det = moments(train), moments(train @ DETECTOR.T)
    m_t, c_t = ref_pix
    sets = {"perfect": sample_data(np.random.default_rng(2), n),
            "copier": train[np.random.default_rng(3).choice(n_train, n, replace=False)],
            "drops faint": sample_data(np.random.default_rng(4), n, faint=False)}
    base = sample_data(np.random.default_rng(5), n)
    tuned = tune_grain(fd(sets["drops faint"], ref_pix), base, ref_pix, 6)
    g = tuned if grain is None else grain
    sets["grainy"] = grainy(base, g, 6)
    sets["gaussian"] = np.random.default_rng(7).multivariate_normal(m_t, c_t, n, method="eigh")
    res = {"n_train": n_train, "n": n, "grain": r4(g), "grain_tuned": r4(tuned), "data": truth(real), "sets": {}}
    print(f"  failures: training set {n_train:,}, {n:,} images per set; grain tuned to {tuned:.4f}"
          + (f", run at {g:.4f}" if grain is not None else ""), flush=True)
    for name, x in sets.items():
        st = {"fd": fd(x, ref_pix), "fd_detector": fd(x @ DETECTOR.T, ref_det)}
        st["kid"], st["kid_sd"] = kid(x, train, seed=11)
        st.update(prdc(real, x))
        st.update(truth(x))
        st["samples"] = [[round(float(v), 3) for v in img] for img in x[:8]]
        res["sets"][name] = {k: (r6(v) if isinstance(v, float) else v) for k, v in st.items()}
        print(f"  failures: {name:>11}: FD {st['fd']:.4f} (detector {st['fd_detector']:.4f}), KID {st['kid']:.5f}, "
              f"precision {st['precision']:.3f}, recall {st['recall']:.3f}, density {st['density']:.3f}, "
              f"coverage {st['coverage']:.3f} | faint {st['faint']:.3f}, blends {st['blend']:.3f}, "
              f"off-contrast {st['off_contrast']:.3f}, detail sd {st['detail_sd']:.3f}", flush=True)
    return res


# ----------------------------------------------------------------------------------- bias
BIAS_NS = (1000, 2000, 4000, 8000, 16000, 32000, 64000)
FIT_FROM = 2000                          # fit FD = FD_inf + K/N on N >= 2,000, as the FD-infinity papers fit 5k-50k
BIAS_GRAIN = 0.07                        # a mild fidelity flaw: a little pixel grain


def run_bias(quick):
    """FD of a perfect generator and of a slightly grainy one against N, repeated, against a reference
    so large that its own estimation error is negligible."""
    reps = 6 if quick else 24
    ns = BIAS_NS[:-2] if quick else BIAS_NS
    n_ref = 32768 if quick else 262144
    ref_m = moments(sample_data(np.random.default_rng(21), n_ref))
    res = {"n_ref": n_ref, "repeats": reps, "ns": list(ns), "fit_from": FIT_FROM, "grain": BIAS_GRAIN, "gens": {}}
    for gi, name in enumerate(("perfect", "grainy")):
        rows = {"fd_mean": [], "fd_sd": []}
        for ni, n in enumerate(ns):
            fds = []
            for rep in range(reps):
                rng = np.random.default_rng(10000 * gi + 100 * ni + rep + 7)
                x = sample_data(rng, n)
                if name == "grainy":
                    x = x + BIAS_GRAIN * rng.normal(size=x.shape)
                fds.append(fd(x, ref_m))
            rows["fd_mean"].append(r6(np.mean(fds)))
            rows["fd_sd"].append(r6(np.std(fds)))
        keep = [i for i, n in enumerate(ns) if n >= FIT_FROM]
        slope, icpt = np.polyfit(1 / np.array([ns[i] for i in keep], float), [rows["fd_mean"][i] for i in keep], 1)
        rows["fd_inf"], rows["slope"] = r6(icpt), round(float(slope), 2)
        res["gens"][name] = rows
        print(f"  bias: {name:>8}: FD at N = {', '.join(f'{n:,}: {v:.4f}' for n, v in zip(ns, rows['fd_mean']))}; "
              f"fit FD = {icpt:.4f} + {slope:.1f}/N", flush=True)
    return res


# ------------------------------------------------------------------------------- guidance
WEIGHTS = (1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 7.5)


def run_guidance(quick):
    n = 2048 if quick else 4096
    z = np.random.default_rng(2026).normal(size=(n, N_PIX))       # part 8's starting noises
    real = sample_data(np.random.default_rng(31), n, 0)           # part 8's real class-0 set
    ref = sample_data(np.random.default_rng(33), N_TRAIN // 4 if quick else N_TRAIN, 0)
    ref_m = moments(ref)
    faint_real = contrast(real, 0)[1] < 0.75
    res = {"n": n, "weights": {}}
    data = sample_data(np.random.default_rng(32), n, 0)
    for label, x in [("data", data)] + [(str(w), None) for w in WEIGHTS]:
        if x is None:
            x = sample_exact(z, 0, float(label))
        m = prdc(real, x, detail=True)
        st = {"fd": fd(x, ref_m)}
        st["kid"], st["kid_sd"] = kid(x, ref, seed=12)
        st.update({k: v for k, v in m.items() if not k.startswith("_")})
        st.update(truth(x, 0))
        st["recall_faint"] = float(m["_recalled"][faint_real].mean())
        st["recall_strong"] = float(m["_recalled"][~faint_real].mean())
        st["coverage_faint"] = float(m["_covered"][faint_real].mean())
        st["coverage_strong"] = float(m["_covered"][~faint_real].mean())
        rf = m["_r_fake"]
        st["fake_radius_median"], st["fake_radius_p99"] = float(np.median(rf)), float(np.quantile(rf, 0.99))
        amp = contrast(x, 0)[1]
        hit = m["_in_fake"][faint_real]                     # faint reals x fakes: which fake balls hold them
        holders = np.where(hit.any(0))[0]
        st["faint_holders"] = int(len(holders))
        st["faint_holder_contrast_median"] = float(np.median(amp[holders])) if len(holders) else None
        st["faint_holder_radius_median"] = float(np.median(rf[holders])) if len(holders) else None
        st["faint_holders_over"] = float((amp[holders] > OVER).mean()) if len(holders) else None
        if label in ("1.0", "3.0", "7.5"):
            st["samples"] = [[round(float(v), 3) for v in img] for img in x[:8]]
        res["weights"][label] = {k: (r6(v) if isinstance(v, float) else v) for k, v in st.items()}
        print(f"  guidance {label:>4}: FD {st['fd']:.4f}, KID {st['kid']:.5f}, precision {st['precision']:.3f}, "
              f"recall {st['recall']:.3f} (faint {st['recall_faint']:.3f}, strong {st['recall_strong']:.3f}), "
              f"density {st['density']:.3f}, coverage {st['coverage']:.3f} (faint {st['coverage_faint']:.3f}) | "
              f"faint {st['faint']:.3f}, over {st['over']:.4f}; fake radius median {st['fake_radius_median']:.3f}, "
              f"p99 {st['fake_radius_p99']:.3f}; {st['faint_holders']} fakes hold faint reals"
              + (f" (median contrast {st['faint_holder_contrast_median']:.3f}, radius "
                 f"{st['faint_holder_radius_median']:.3f}, over-saturated {st['faint_holders_over']:.2f})"
                 if st['faint_holders'] else ""), flush=True)
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
            f"numpy {np.__version__}; evaluate.py {_SRC}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stage", choices=["worked", "failures", "bias", "guidance", "all"])
    ap.add_argument("--quick", action="store_true", help="fewer samples and repeats")
    ap.add_argument("--out", default=None, help="write here instead of captures.json")
    ap.add_argument("--grain", type=float, default=None, help="failures: use this grain instead of the tuned one")
    args = ap.parse_args()
    out = Path(args.out) if args.out else HERE / "captures.json"
    prov = provenance()
    print(prov, flush=True)
    cap = json.loads(out.read_text()) if out.exists() and args.stage != "all" else {}
    cap.update({"provenance": prov, "source_sha1": _SRC, "quick": args.quick,
                "world": {"classes": K, "contrasts": list(AMPS), "faint_share": P_FAINT, "contrast_jitter": S_A,
                          "brightness_sd": S_B, "detail": TAU, "pixels": N_PIX, "crescent_norm": round(NORM, 4),
                          "over_threshold": round(OVER, 4), "blend_band": [round(MID[0], 4), round(MID[1], 4)],
                          "k_pr": K_PR, "k_dc": K_DC}})
    t0 = time.time()
    stages = ["worked", "failures", "bias", "guidance"] if args.stage == "all" else [args.stage]
    for stage in stages:
        t = time.time()
        if stage == "worked":
            cap["worked"] = run_worked()
        elif stage == "failures":
            cap["failures"] = run_failures(args.quick, args.grain)
        elif stage == "bias":
            cap["bias"] = run_bias(args.quick)
        elif stage == "guidance":
            cap["guidance"] = run_guidance(args.quick)
        print(f"  ({stage}: {time.time() - t:.0f} s)", flush=True)
        out.write_text(json.dumps(cap, indent=1) + "\n")
    print(f"wrote {os.path.relpath(out, Path.cwd())} in {time.time() - t0:.0f} s", flush=True)


if __name__ == "__main__":
    main()
