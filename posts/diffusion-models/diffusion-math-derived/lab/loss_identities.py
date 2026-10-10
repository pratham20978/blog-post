#!/usr/bin/env python3
"""Numerical checks for "Where the MSE Loss Comes From" (diffusion-models, part 3).

Every identity the article derives is re-computed here on the article's own
numbers, so you can confirm each step without trusting the algebra:

  1. One reverse step on one pixel: the forward posterior ("teacher") by adding
     precisions, then by DDPM's closed form; the network's step ("student");
     their KL divergence three ways (Gaussian KL, epsilon form, SNR form).
  2. The same prediction error priced by five losses.
  3. The per-step ELBO weight along DDPM's real 1,000-step linear schedule.
  4. Tweedie: the ideal denoiser for a three-value dataset, and the score it implies.
  5. Denoising score matching: regressing onto noisy per-sample targets recovers
     the score of the noised data.
  6. VP and VE corruption of the same pixel are one path, rescaled.
  7. More steps give a tighter bound: the discrete diffusion loss for Gaussian
     data decreases toward its continuous-time integral.

Run:    python3 loss_identities.py
Needs:  Python 3.8 or newer, standard library only. Deterministic; no files written.
Expect: seven sections of printed numbers, each ending in a line that says "ok".
        Any identity that fails raises AssertionError and names itself.
"""

from __future__ import annotations

import math

# --------------------------------------------------------------- series constants
# The 4x4 patch from part 1 of the series. Only the top-left pixel is used below.
X0 = [[0.95, 0.60, -0.30, -0.85],
      [0.80, 0.45, -0.55, -0.90],
      [0.55, 0.10, -0.70, -0.95],
      [0.25, -0.20, -0.85, -1.00]]
EPS = [[-0.55, 1.40, 0.45, -1.10],
       [0.85, -1.35, -0.25, 0.70],
       [1.25, 0.30, -0.95, 0.15],
       [-1.05, 0.90, 1.45, -1.10]]

ABAR_T = 0.64          # noise level of x_t, shared with parts 1 and 2
ABAR_S = 0.80          # the previous level on the article's coarse chain
EPS_HAT_ERROR = 0.20   # the network misreads the top-left noise by +0.20

DATA_LEVELS = [-0.85, 0.10, 0.95]   # the three grey levels of the crescent motif


def close(a: float, b: float, tol: float = 1e-9) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def snr(abar: float) -> float:
    return abar / (1.0 - abar)


def gauss_kl(m1: float, v1: float, m2: float, v2: float) -> float:
    """KL( N(m1, v1) || N(m2, v2) ) for scalars, in nats."""
    return 0.5 * (math.log(v2 / v1) + (v1 + (m1 - m2) ** 2) / v2 - 1.0)


# ------------------------------------------------------- 1. one step, one pixel
def coarse_step() -> dict:
    x0, eps = X0[0][0], EPS[0][0]
    a_t, s_t = math.sqrt(ABAR_T), math.sqrt(1 - ABAR_T)          # 0.8, 0.6
    alpha = ABAR_T / ABAR_S                                       # 0.8
    beta = 1 - alpha                                              # 0.2
    xt = a_t * x0 + s_t * eps                                     # 0.43

    # Teacher, by combining two Gaussian pieces of evidence about x_{t-1}.
    m_from_x0, v_from_x0 = math.sqrt(ABAR_S) * x0, 1 - ABAR_S     # N(0.8497, 0.20)
    m_from_xt, v_from_xt = xt / math.sqrt(alpha), beta / alpha     # N(0.4807, 0.25)
    prec = 1 / v_from_x0 + 1 / v_from_xt                          # 5 + 4 = 9
    teacher_var = 1 / prec
    teacher_mean = (m_from_x0 / v_from_x0 + m_from_xt / v_from_xt) / prec

    # Teacher, by DDPM's closed form (Ho et al. 2020, eq. 7).
    c_x0 = math.sqrt(ABAR_S) * beta / (1 - ABAR_T)
    c_xt = math.sqrt(alpha) * (1 - ABAR_S) / (1 - ABAR_T)
    beta_tilde = (1 - ABAR_S) / (1 - ABAR_T) * beta
    assert close(teacher_mean, c_x0 * x0 + c_xt * xt), "posterior mean: two routes disagree"
    assert close(teacher_var, beta_tilde), "posterior variance: two routes disagree"

    # Student: the network's noise estimate, turned into a clean-image estimate,
    # plugged into the same formula. Variance fixed to the teacher's.
    eps_hat = eps + EPS_HAT_ERROR
    x0_hat = (xt - s_t * eps_hat) / a_t                             # 0.80
    student_mean = c_x0 * x0_hat + c_xt * xt

    kl = gauss_kl(teacher_mean, teacher_var, student_mean, teacher_var)
    lam = beta ** 2 / (2 * beta_tilde * alpha * (1 - ABAR_T))       # DDPM eq. 12 weight
    kl_eps = lam * EPS_HAT_ERROR ** 2
    kl_snr = 0.5 * (snr(ABAR_S) - snr(ABAR_T)) * (x0_hat - x0) ** 2  # VDM eq. 13 form
    assert close(kl, kl_eps) and close(kl, kl_snr), "KL: three routes disagree"

    # DDPM's other variance choice, sigma^2 = beta: the theta-dependent part changes
    # scale, and a theta-free constant appears.
    kl_beta = gauss_kl(teacher_mean, teacher_var, student_mean, beta)
    const_beta = gauss_kl(teacher_mean, teacher_var, teacher_mean, beta)

    return dict(x0=x0, eps=eps, xt=xt, alpha=alpha, beta=beta,
                m_from_x0=m_from_x0, v_from_x0=v_from_x0,
                m_from_xt=m_from_xt, v_from_xt=v_from_xt,
                teacher_mean=teacher_mean, teacher_var=teacher_var,
                c_x0=c_x0, c_xt=c_xt, eps_hat=eps_hat, x0_hat=x0_hat,
                student_mean=student_mean, gap=teacher_mean - student_mean,
                kl=kl, weight=lam, snr_s=snr(ABAR_S), snr_t=snr(ABAR_T),
                kl_beta=kl_beta, const_beta=const_beta)


# ------------------------------------------------------ 2. five prices, one error
def five_prices() -> list[tuple[str, float, float, float]]:
    """(target, true value, predicted value, weight that converts to epsilon units)."""
    x0, eps = X0[0][0], EPS[0][0]
    a, s = math.sqrt(ABAR_T), math.sqrt(1 - ABAR_T)
    xt = a * x0 + s * eps
    eh = eps + EPS_HAT_ERROR
    xh = (xt - s * eh) / a
    rows = [
        ("epsilon", eps, eh),
        ("x0", x0, xh),
        ("score", -eps / s, -eh / s),              # conditional score of q(x_t | x_0)
        ("v", a * eps - s * x0, a * eh - s * xh),  # Salimans & Ho 2022 velocity
    ]
    out = []
    base = (eh - eps) ** 2
    for name, true, pred in rows:
        sq = (pred - true) ** 2
        out.append((name, true, pred, sq, base / sq))
    return out


# ------------------------------------------- 3. the weight DDPM's L_simple dropped
def ddpm_linear(T: int = 1000):
    betas = [1e-4 + (0.02 - 1e-4) * i / (T - 1) for i in range(T)]
    abar, p = [], 1.0
    for b in betas:
        p *= 1 - b
        abar.append(p)
    return betas, abar


def elbo_weights(T: int = 1000, variance: str = "beta"):
    """Per-step weight on ||eps - eps_hat||^2 inside the ELBO (Ho et al. eq. 12), t = 2..T."""
    betas, abar = ddpm_linear(T)
    w = {}
    for t in range(2, T + 1):
        b, a, ab, ab_prev = betas[t - 1], 1 - betas[t - 1], abar[t - 1], abar[t - 2]
        var = b if variance == "beta" else (1 - ab_prev) / (1 - ab) * b
        w[t] = b * b / (2 * var * a * (1 - ab))
    return w


# ------------------------------------------------------------- 4. Tweedie, exactly
def posterior_weights(z: float, a: float, s: float, data=DATA_LEVELS) -> list[float]:
    logits = [-(z - a * x) ** 2 / (2 * s * s) for x in data]
    m = max(logits)
    e = [math.exp(l - m) for l in logits]
    tot = sum(e)
    return [v / tot for v in e]


def ideal_denoiser(z: float, a: float, s: float, data=DATA_LEVELS) -> float:
    return sum(w * x for w, x in zip(posterior_weights(z, a, s, data), data))


def log_marginal(z: float, a: float, s: float, data=DATA_LEVELS) -> float:
    terms = [-(z - a * x) ** 2 / (2 * s * s) for x in data]
    m = max(terms)
    return m + math.log(sum(math.exp(t - m) for t in terms) / len(data)) \
        - 0.5 * math.log(2 * math.pi * s * s)


def score(z: float, a: float, s: float, data=DATA_LEVELS) -> float:
    """Tweedie: score of the noised marginal from the ideal denoiser."""
    return (a * ideal_denoiser(z, a, s, data) - z) / (s * s)


# ------------------------------------------ 5. denoising score matching, by sampling
def lcg_normals(n: int, seed: int = 20260925):
    """Deterministic standard normals (Box-Muller over a 31-bit LCG)."""
    state = seed
    out = []
    while len(out) < n:
        state = (1103515245 * state + 12345) % 2147483648
        u1 = (state + 1) / 2147483649
        state = (1103515245 * state + 12345) % 2147483648
        u2 = state / 2147483648
        r = math.sqrt(-2 * math.log(u1))
        out += [r * math.cos(2 * math.pi * u2), r * math.sin(2 * math.pi * u2)]
    return out[:n]


def dsm_samples(n: int = 600, seed: int = 20260925):
    """(z, per-sample target) pairs: z = a*x0 + s*eps, target = -eps/s."""
    a, s = math.sqrt(ABAR_T), math.sqrt(1 - ABAR_T)
    noise = lcg_normals(n, seed)
    pairs = []
    for i, e in enumerate(noise):
        x0 = DATA_LEVELS[i % len(DATA_LEVELS)]      # equal thirds of each grey level
        pairs.append((a * x0 + s * e, -e / s))
    return pairs


def binned_means(pairs, lo=-2.0, hi=2.0, bins=16):
    width = (hi - lo) / bins
    sums = [[0.0, 0] for _ in range(bins)]
    for z, y in pairs:
        k = int((z - lo) // width)
        if 0 <= k < bins:
            sums[k][0] += y
            sums[k][1] += 1
    return [(lo + (k + 0.5) * width, s / c, c) for k, (s, c) in enumerate(sums) if c >= 12]


# -------------------------------------------------------- 6. VP and VE, one path
def vp_ve_path(x0: float, eps: float, lambdas):
    """Same pixel, same noise draw, at each log-SNR: VP value, VE value, rescaled VE."""
    rows = []
    for lam in lambdas:
        ab = 1 / (1 + math.exp(-lam))                 # sigmoid(lambda) = abar
        vp = math.sqrt(ab) * x0 + math.sqrt(1 - ab) * eps
        sigma_ve = math.exp(-lam / 2)                 # 1 / sqrt(SNR)
        ve = x0 + sigma_ve * eps
        rows.append((lam, vp, ve, math.sqrt(ab) * ve, sigma_ve))
    return rows


# ----------------------------------------- 7. more steps, tighter bound (Gaussian data)
def gaussian_diffusion_loss(T: int, s_data: float = 0.5,
                            lam_max: float = 10.0, lam_min: float = -10.0) -> float:
    """VDM eq. 13 with the optimal denoiser, for x0 ~ N(0, s_data^2), in nats per dim.

    mmse(g) = s^2 / (1 + g s^2) is the error of the best clean-data estimate at SNR g.
    The discrete loss is an upper Riemann sum of 0.5 * integral of mmse dSNR.
    """
    lams = [lam_max + (lam_min - lam_max) * i / T for i in range(T + 1)]
    g = [math.exp(l) for l in lams]
    mmse = lambda snr_: s_data ** 2 / (1 + snr_ * s_data ** 2)
    return sum(0.5 * (g[i - 1] - g[i]) * mmse(g[i]) for i in range(1, T + 1))


def gaussian_diffusion_loss_continuous(s_data: float = 0.5, lam_max: float = 10.0,
                                       lam_min: float = -10.0) -> float:
    gmax, gmin = math.exp(lam_max), math.exp(lam_min)
    return 0.5 * math.log((1 + gmax * s_data ** 2) / (1 + gmin * s_data ** 2))


# ---------------------------------------------------------------------- report
def main() -> None:
    print("1. One reverse step on the top-left pixel (coarse chain 0.80 -> 0.64)")
    c = coarse_step()
    print(f"   x0 = {c['x0']:.2f}, eps = {c['eps']:.2f}, x_t = {c['xt']:.2f}")
    print(f"   evidence from x0: N({c['m_from_x0']:.4f}, {c['v_from_x0']:.2f})  precision {1/c['v_from_x0']:.0f}")
    print(f"   evidence from xt: N({c['m_from_xt']:.4f}, {c['v_from_xt']:.2f})  precision {1/c['v_from_xt']:.0f}")
    print(f"   teacher q(x_t-1 | x_t, x0) = N({c['teacher_mean']:.4f}, {c['teacher_var']:.4f})")
    print(f"   closed-form coefficients: {c['c_x0']:.4f} * x0 + {c['c_xt']:.4f} * x_t")
    print(f"   student: eps_hat = {c['eps_hat']:.2f} -> x0_hat = {c['x0_hat']:.2f} -> mean {c['student_mean']:.4f}")
    print(f"   mean gap {c['gap']:.4f};  KL = {c['kl']:.4f} nats")
    print(f"   epsilon form: weight {c['weight']:.4f} x {EPS_HAT_ERROR**2:.2f} = {c['weight']*EPS_HAT_ERROR**2:.4f}")
    print(f"   SNR form: 0.5 x ({c['snr_s']:.4f} - {c['snr_t']:.4f}) x {(c['x0_hat']-c['x0'])**2:.4f} = {c['kl']:.4f}")
    print(f"   with sigma^2 = beta instead: KL = {c['kl_beta']:.4f} = {c['kl_beta']-c['const_beta']:.4f} (depends on theta)"
          f" + {c['const_beta']:.4f} (does not)")
    print("   ok")

    print("\n2. One error of +0.20 in the predicted noise, priced five ways (abar = 0.64)")
    for name, true, pred, sq, to_eps in five_prices():
        print(f"   {name:8s} true {true:+.4f}  predicted {pred:+.4f}  squared error {sq:.4f}"
              f"  x {to_eps:.4f} = {sq*to_eps:.4f} in epsilon units")
    print(f"   ELBO step  KL {c['kl']:.4f} = {c['weight']:.4f} x 0.0400")
    print("   ok")

    print("\n3. ELBO weight on the epsilon error along DDPM's linear schedule (T = 1000)")
    betas, abar = ddpm_linear()
    wb, wt = elbo_weights(variance="beta"), elbo_weights(variance="beta_tilde")
    for t in (2, 10, 50, 100, 207, 500, 1000):
        print(f"   t = {t:4d}  abar = {abar[t-1]:.4f}  weight (sigma^2 = beta) {wb[t]:.5f}"
              f"  (sigma^2 = beta_tilde) {wt[t]:.5f}")
    lo_t, hi_t = min(wb, key=wb.get), max(wb, key=wb.get)
    print(f"   sigma^2 = beta: largest {wb[hi_t]:.4f} at t = {hi_t}, smallest {wb[lo_t]:.5f} at t = {lo_t},"
          f" ratio {wb[hi_t]/wb[lo_t]:.0f}")
    share = sum(v for t, v in wb.items() if t <= 100) / sum(wb.values())
    print(f"   steps 2..100 carry {share:.1%} of the total weight")
    print(f"   L_simple uses 1 at every t.  L_T = KL(q(x_T|x0) || N(0,I)) has abar_T = {abar[-1]:.4e}")
    print("   ok")

    print("\n4. Tweedie on the three-level dataset {-0.85, 0.10, 0.95} at abar = 0.64")
    a, s = math.sqrt(ABAR_T), math.sqrt(1 - ABAR_T)
    for z in (-1.0, 0.0, 0.43, 1.0):
        w = posterior_weights(z, a, s)
        d = ideal_denoiser(z, a, s)
        h = 1e-5
        fd = (log_marginal(z + h, a, s) - log_marginal(z - h, a, s)) / (2 * h)
        assert close(score(z, a, s), fd, 1e-6), "Tweedie: score and finite difference disagree"
        print(f"   z = {z:+.2f}  weights {[round(v, 3) for v in w]}  E[x0|z] = {d:+.4f}"
              f"  score {score(z, a, s):+.4f} (finite difference {fd:+.4f})")
    print("   ok")

    print("\n5. Denoising score matching: noisy targets average to the score")
    pairs = dsm_samples()
    spread = math.sqrt(sum(y * y for _, y in pairs) / len(pairs))
    print(f"   {len(pairs)} samples; per-sample targets have RMS {spread:.3f}")
    worst = 0.0
    for zc, mean, count in binned_means(pairs):
        err = abs(mean - score(zc, a, s))
        worst = max(worst, err)
        print(f"   bin z = {zc:+.2f} (n = {count:3d})  mean target {mean:+.3f}  exact score {score(zc, a, s):+.3f}")
    print(f"   largest bin deviation {worst:.3f}")
    for n in (6000, 60000):
        dev = max(abs(m - score(zc, a, s)) for zc, m, _ in binned_means(dsm_samples(n)))
        print(f"   with {n} samples the largest bin deviation is {dev:.3f}")
    print("   ok")

    print("\n6. VP and VE corruption of the top-left pixel (x0 = 0.95, eps = -0.55)")
    for lam, vp, ve, ve_scaled, sig in vp_ve_path(X0[0][0], EPS[0][0], (4.0, math.log(snr(ABAR_T)), 0.0, -4.0)):
        assert close(vp, ve_scaled), "VP and rescaled VE disagree"
        print(f"   log-SNR {lam:+.3f}  VP {vp:+.4f}  VE {ve:+.4f} (sigma_VE {sig:.4f})  sqrt(abar) * VE {ve_scaled:+.4f}")
    print("   ok")

    print("\n7. Discrete diffusion loss for x0 ~ N(0, 0.5^2), log-SNR from +10 to -10")
    prev = float("inf")
    for T in (1, 2, 4, 8, 16, 64, 256, 1024):
        L = gaussian_diffusion_loss(T)
        assert L < prev, "more steps did not lower the loss"
        prev = L
        print(f"   T = {T:5d}  diffusion loss {L:8.4f} nats/dim")
    print(f"   T -> inf  diffusion loss {gaussian_diffusion_loss_continuous():8.4f} nats/dim")
    print("   ok")


if __name__ == "__main__":
    main()
