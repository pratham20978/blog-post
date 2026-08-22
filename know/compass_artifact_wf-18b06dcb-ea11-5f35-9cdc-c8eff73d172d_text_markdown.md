# Lanczos Resampling: Complete Mathematical Theory and Practical Implementation

## TL;DR
- **Lanczos resampling reconstructs a continuous signal from discrete samples using a *windowed sinc* kernel** — L(x) = sinc(x)·sinc(x/a) — then re-samples it on a new grid. It is widely regarded as the "best compromise" among simple filters for sharpness vs. aliasing vs. ringing. It was invented by Claude Duchon (1979) and named after Cornelius Lanczos because it uses his sigma-approximation technique for suppressing the Gibbs phenomenon.
- **The whole theory is one chain of reasoning:** ideal reconstruction = brick-wall low-pass = sinc (infinite support, impractical) → truncate → Gibbs ringing → multiply by the Lanczos window sinc(x/a) to tame the ringing. The kernel is *interpolating* (L(0)=1, L(n)=0), *separable* in 2D (O(N²·2a) vs O(N²·(2a)²)), has *negative lobes* (causing halos/overshoot), and does **not** form a partition of unity (so per-pixel weight normalization is mandatory).
- **In practice**: implement it as two 1-D separable passes with precomputed weight matrices; get the coordinate mapping right ((dst+0.5)·scale−0.5), scale the kernel by the downscale factor when minifying (Pillow does this, OpenCV's INTER_LANCZOS4 does **not** and therefore aliases), normalize weights, clamp negative overshoot, resample in linear light, and handle premultiplied alpha. Pillow uses a=3 with support scaling; OpenCV uses a=4 with a fixed 8×8-tap kernel.

---

# PART 1: COMPLETE MATHEMATICAL THEORY

## 1. Framing the resampling problem

### 1.1 What "resizing an image" really is
A digital image is not a continuous object; it is a set of **discrete samples** s[i,j] of an underlying continuous intensity field. To resize, rotate, or shift it, we must evaluate intensities at coordinates that fall *between* the original samples. Formally the pipeline is:

1. **Reconstruct** a continuous function ŝ(x) from the discrete samples s[i] by convolving them with a reconstruction kernel k:
   ŝ(x) = Σ_i s[i] · k(x − i)
2. **Re-sample** ŝ at the positions dictated by the geometric transform (the new, denser or sparser grid).

Everything in interpolation theory is a *choice of the kernel k*. Nearest-neighbour, bilinear, bicubic, and Lanczos are all just different k.

Symbols used throughout:
- x, t: continuous spatial coordinate (real number).
- i, j, k, n: integer sample indices.
- s[i] or s_i: the i-th discrete input sample.
- S(x) or ŝ(x): the reconstructed continuous signal.
- a: the Lanczos "order" / number of lobes / kernel radius (a positive integer, usually 2 or 3).
- r, scale: scale factors (defined at each use).
- ξ (xi): frequency variable.

### 1.2 Magnification vs. minification and why the kernel is scaled differently
- **Magnification (upsampling / interpolation):** the output has *more* samples than the input; new samples fall densely between old ones. The reconstruction kernel is used at its native width — we literally read values off the reconstructed continuous curve. The Nyquist limit of the *output* is higher than that of the input, so no new anti-aliasing filtering is needed: the input already contains no frequencies above its own Nyquist.
- **Minification (downsampling / decimation):** the output has *fewer* samples, so the output grid has a *lower* Nyquist frequency than the input. If we just point-sample the reconstruction, input frequencies above the *output* Nyquist alias (fold back) into the output as false low-frequency content (moiré). Therefore we must **low-pass filter to the output Nyquist** before/while resampling. Practically this is done by *widening* the kernel: for a downscale ratio r = input/output > 1, we use k(x/r)/r instead of k(x). The 1/r amplitude keeps the DC gain at 1; the x/r stretches the kernel in space, which narrows its passband in frequency to the new, lower cutoff.

This single fact — the kernel must be stretched by the downscale factor on minification — is the number-one source of "why does my Lanczos look aliased?" bugs, and it is exactly where Pillow and OpenCV diverge (see Part 2).

## 2. Sampling theory foundation

### 2.1 Sampling as multiplication by a Dirac comb
Let f(t) be the continuous signal. Ideal sampling at interval T multiplies f by a Dirac comb (impulse train):
Ш_T(t) = Σ_n δ(t − nT).
The sampled signal is f_s(t) = f(t) · Ш_T(t) = Σ_n f(nT) δ(t − nT).

### 2.2 The Fourier-domain view: sampling replicates the spectrum
Multiplication in time is convolution in frequency. The Fourier transform of a Dirac comb of spacing T is another Dirac comb of spacing 1/T (times a constant). Therefore:
F_s(ξ) = F(ξ) * (1/T) Σ_k δ(ξ − k/T) = (1/T) Σ_k F(ξ − k/T).

That is: **sampling replicates the original spectrum F(ξ) at every multiple of the sampling frequency f_s = 1/T.** The copies are called spectral images or aliases.

### 2.3 Nyquist–Shannon and band-limited signals
If f is **band-limited** — F(ξ) = 0 for |ξ| ≥ B — the replicas do not overlap provided f_s = 1/T > 2B. The quantity 2B is the Nyquist rate; f_s/2 is the Nyquist frequency. When the replicas don't overlap, the original spectrum sits cleanly in the baseband [−f_s/2, f_s/2] and can be recovered by isolating it.

**Reconstruction = ideal low-pass filtering.** To recover F(ξ) we multiply the replicated spectrum by a "brick-wall" rectangular filter that is 1 inside [−f_s/2, f_s/2] and 0 outside:
H(ξ) = rect(ξ / f_s) = { 1 if |ξ| < f_s/2 ; 0 otherwise }.
Multiplying keeps exactly one copy and discards the rest, giving back F(ξ), hence f(t) exactly. This is the Whittaker–Shannon interpolation formula.

### 2.4 Deriving the sinc: inverse transform of the ideal low-pass
The reconstruction kernel in the *space* domain is the inverse Fourier transform of the rectangular filter H(ξ). Take a rectangular window of half-width W (cutoff at ±W), using the convention F(ξ) = ∫ f(t) e^{−2πiξt} dt:

h(t) = ∫_{−W}^{+W} 1 · e^{+2πi ξ t} dξ
     = [ e^{+2πi ξ t} / (2πi t) ]_{ξ=−W}^{ξ=+W}
     = ( e^{+2πi W t} − e^{−2πi W t} ) / (2πi t)
     = ( 2i sin(2πW t) ) / (2πi t)
     = sin(2πW t) / (π t).

Setting 2W = 1 (cutoff at ±½, the normalized case) gives h(t) = sin(π t)/(π t) ≡ **sinc(t)** (normalized sinc). Wolfram MathWorld and Bracewell state the pair directly: the Fourier transform of rect(x) is sinc(πk), i.e. rect ↔ sinc are a Fourier pair. So the **ideal reconstruction filter is the sinc function** — a *derived* result, not an arbitrary choice.

Two conventions for sinc appear in the literature, and both are used for Lanczos:
- **Normalized sinc:** sinc(x) = sin(πx)/(πx). Zeros at nonzero integers. Used in image processing and by Wikipedia's Lanczos definition.
- **Unnormalized sinc:** sinc(x) = sin(x)/x. Zeros at nonzero multiples of π. Used in some math texts and in Mazzoli's derivation.

Throughout Part 1 we use the **normalized** convention unless stated.

### 2.5 Aliasing and why it matters
If f is not band-limited below f_s/2 (or is sampled too slowly), the spectral replicas overlap. High frequencies "fold" into the baseband and masquerade as low frequencies: this is **aliasing**. In images it appears as moiré patterns, jagged edges (jaggies), and shimmering in video. Aliasing introduced at sampling time is *irreversible* — no reconstruction filter can separate overlapped content. This is why minification requires a low-pass (anti-aliasing) pre-filter: we must remove the frequencies that would alias *before* we drop samples.

## 3. Why ideal sinc reconstruction is unusable in practice

1. **Infinite support.** sinc(x) is nonzero for all x. To compute one output exactly you must sum contributions from *every* input sample — O(N) per output pixel, O(N²) per row, catastrophically expensive.
2. **Slow decay.** sinc(x) decays only as O(1/x). Its tails are not negligible and are **not absolutely integrable** (∫|sinc| dx diverges), so truncation error converges very slowly.
3. **Boundary problems.** Infinite support means every output depends on pixels outside the image; edges are ill-defined.
4. **Truncation → ringing (Gibbs phenomenon).** Naively chopping sinc to a finite window is, in the frequency domain, convolving the ideal brick-wall response with the window's spectrum (a sinc-like function with large sidelobes). The result has **overshoot near the cutoff, passband/stopband ripple (spectral leakage), and large sidelobes.** In space this is **ringing**: oscillations that overshoot and undershoot near sharp edges. Mazzoli's derivation shows explicitly that truncating sinc leaves the Gibbs oscillations essentially intact, and that the ripple frequency in the spectrum increases with the window half-width a.

The Gibbs phenomenon is a *fixed-percentage* overshoot that does not vanish as you add terms — it just gets narrower. Its exact size is set by the **Wilbraham–Gibbs constant**: for a truncated Fourier series the partial sum peaks at (2/π)·Si(π) = 1.1789797444721675, i.e. about **0.1790 above a unit half-jump, ≈ 8.95% of the full jump height, independent of the number of terms N** (Math LibreTexts, Herman, "3.7: The Gibbs Phenomenon"). It is intrinsic to truncated orthogonal expansions.

## 4. Windowing as the solution

### 4.1 General windowed-sinc theory
Instead of a hard truncation (multiplication by a rectangular window), multiply sinc by a smooth **window function** w(x) of finite support that tapers gently to zero:
k(x) = sinc(x) · w(x).
In the frequency domain this is convolution: K(ξ) = rect * W(ξ). A smoother window has a more compact, lower-sidelobe spectrum, so the convolution smears the brick wall less violently — **ringing is reduced.** The universal trade-off:
- **Wide main lobe (of W) → more passband blurring / softer cutoff** (loss of sharpness).
- **Low sidelobes (of W) → less ringing and less aliasing leakage.**
You cannot minimize both at once (an uncertainty-principle-like constraint).

### 4.2 Common windows in context
| Window | Sidelobe behaviour | Main-lobe width | Character |
|---|---|---|---|
| Rectangular (truncation) | Highest sidelobes (≈−13 dB) | Narrowest | Sharpest but worst ringing |
| Hann (raised cosine) | Low sidelobes (≈−31 dB) | Wider | Smooth, softer |
| Hamming | Lower first sidelobe (≈−43 dB) | Similar to Hann | Slightly sharper than Hann |
| Blackman | Very low sidelobes (≈−58 dB) | Widest | Very smooth, blurriest |
| Kaiser | Tunable (β) | Tunable | Adjustable trade-off |
| **Lanczos** (= central lobe of sinc(x/a)) | Moderate | Moderate | "Best compromise" for images |

The Lanczos window is special because it is *itself* a piece of a sinc — the central lobe of the stretched sinc sinc(x/a) — which is exactly the shape needed to counteract the Gibbs oscillations of the truncated sinc (§5.1).

## 5. The Lanczos kernel proper

### 5.1 Origin: Lanczos sigma factors and the sigma approximation
Cornelius Lanczos, in *Applied Analysis* (1956; Dover reprint 1988, pp. 219–221), introduced a method to suppress the Gibbs phenomenon in truncated Fourier series. Instead of the raw partial-sum coefficients, you multiply each by a **sigma factor** σ = sinc(k/m) = sin(πk/m)/(πk/m), where k is the coefficient index and m the number of terms retained. This is the **sigma approximation**. Wolfram MathWorld gives the σ-approximated series as f(θ) = ½a₀ + Σ_{k=1}^{m−1} sinc(kπ/2m)[a_k cos kθ + b_k sin kθ]; the sinc terms are the Lanczos sigma factors.

The key insight (worked out in detail in Mazzoli's derivation): the error from truncating a function at ±a is a spectrum modulated by a "carrier wave" e^{−2πiξa} of period 1/a. Averaging (smoothing) the truncated spectrum over one period 1/a removes most of the oscillation, and Lanczos proved this smoothing is achieved simply by **multiplying the truncated function pointwise by sinc(πx/a)**. Applying this to the truncated sinc reconstruction filter itself yields the Lanczos kernel. This is why **Duchon (1979), "Lanczos Filtering in One and Two Dimensions"** (*J. Applied Meteorology* 18(8):1016–1022), who first applied it to resampling, named it after Lanczos.

### 5.2 Formal definition
The Lanczos kernel of order a is:

L(x) = { sinc(x) · sinc(x/a),  |x| < a
       { 0,                     |x| ≥ a
with L(0) = 1.

Here sinc is normalized, sinc(x) = sin(πx)/(πx). The window sinc(x/a) is the central lobe of a sinc stretched by factor a, running from −a to +a. a is the **order / lobe count / kernel radius**, normally a = 2 or 3 (OpenCV uses a = 4). The kernel has 2a−1 lobes: one positive central lobe and a−1 alternating negative/positive lobes on each side. Its support is 2a wide, so it touches **2a input samples in 1D** and (2a)² in 2D.

### 5.3 Expanded closed form
Substituting both sincs (normalized): sinc(x)=sin(πx)/(πx), sinc(x/a)=sin(πx/a)/(πx/a)=a·sin(πx/a)/(πx). Therefore for 0 < |x| < a:

**L(x) = [sin(πx)/(πx)] · [a·sin(πx/a)/(πx)] = a·sin(πx)·sin(πx/a) / (π²x²).**

This is the standard form (Wikipedia; Turkowski's Graphics Gems forms for Lanczos2/Lanczos3 are exactly this with a=2, 3). **Common error:** the kernel is sinc(x)·sinc(x/a), NOT sinc(a·x)·sinc(x/a); the latter changes the main-lobe width and distorts the frequency response.

### 5.4 Key properties (with proofs)
**(a) L(0) = 1.** Both sinc factors → 1 as x→0 (sin(u)/u → 1), so L(0)=1·1=1.

**(b) Interpolating / Kronecker property: L(n)=0 for every nonzero integer n with |n|<a.** For integer n≠0, sin(πn)=0 and π²n²≠0, so L(n)=0. With L(0)=1 this gives L(n)=δ_{n,0} on the integers. **Consequence:** S(m) = Σ_i s[i] L(m−i) = s[m] — the filter *passes through* the original samples (it interpolates, not merely approximates).

**(c) Continuity and differentiability.** For integer a, L is C¹ everywhere, including at x=±a, where sin(πx/a)=sin(±π)=0 so the product vanishes to second order (no corner). This is precisely why integer a is chosen: the window ends at a zero of the windowed function, giving a differentiable kernel and a reconstructed signal with continuous derivative.

**(d) Symmetry / even.** L(−x) = a·sin(−πx)·sin(−πx/a)/(π²x²) = a·(−sin πx)(−sin πx/a)/(π²x²) = L(x). So **L is even**, i.e. a zero-phase (non-shifting) filter.

**(e) Support = 2a taps (1D), (2a)² (2D).** L is nonzero only on (−a, a).

### 5.5 Partition of unity: why normalization is required
A kernel forms a **partition of unity** if Σ_i k(x−i)=1 for all x (a constant input maps to a constant output). **The Lanczos kernel does NOT have this property.** Wikipedia: "The Lanczos kernel does not have the partition of unity property... Therefore, the Lanczos interpolation of a discrete signal with constant samples does not yield a constant function." The defect is small for a=2,3 (fractions of a percent for typical fractional offsets), worst at a=1, but non-negligible enough to cause faint banding/brightness ripple, especially after repeated resampling where error accumulates. Fix by **per-output-pixel normalization**:

S(x) = [ Σ_i s[i] L(x−i) ] / [ Σ_i L(x−i) ].

Wikipedia gives this explicitly ("The partition of unity can be introduced by a normalization"). It is also essential at borders where only part of the kernel overlaps valid pixels.

### 5.6 Frequency response
- **Passband:** nearly flat, near unity gain; flatter and closer to 1 as a increases.
- **Transition band:** finite width; steeper as a increases.
- **Stopband:** attenuated with **residual sidelobes** (not identically zero) → some aliasing leakage remains. Turkowski's measured z-transform responses show the Lanczos filters "keep more of the passband than the others (except maybe the box)," with **Lanczos3 "coming closest to the ideal filter shape of all the filters evaluated."**
- **a=2 vs 3 vs 4:** larger a → sharper transition, flatter passband, better stopband — but more (and more visible) ringing/overshoot in space, higher cost (more taps), more edge cropping. Wikipedia: for a=2 the ringing is < 1%. **Turkowski & Gabriel found a=2 the "best compromise in terms of reduction of aliasing, sharpness, and minimal ringing."** **Jim Blinn recommended a=3**, saying it keeps low frequencies and rejects high frequencies "better than any (achievable) filter we've seen so far" — an assessment from his anti-aliasing analysis in "Jim Blinn's Corner — Return of the Jaggy [high-frequency filtering]," *IEEE Computer Graphics and Applications* 9(2):82–89 (March 1989), which evaluates box, triangle/tent, Gaussian-shaped, and ideal filters.

### 5.7 Negative lobes: cause and consequences
For a > 1 the second and further lobes of the central sinc are negative and the window does not fully suppress them, so **L(x) < 0 over sub-intervals of (1, a)** (and symmetrically). This is unavoidable: to approximate a brick wall you must keep some of sinc's negative excursions. Consequences:
- **Overshoot / undershoot near edges.** Because some weights are negative, the weighted sum can exceed the local max or fall below the local min. Wikipedia: "the interpolated signal can be negative even if all samples are positive... the range of values of the interpolated signal may be wider than the range spanned by the discrete sample values."
- **Halos / ringing.** Light and dark bands hug strong edges. They increase *perceived* sharpness (edge enhancement) — part of why Lanczos looks crisp — but they are artifacts.
- **Out-of-gamut values requiring clamping.** Outputs can go below 0 or above max (255 / 1.0) and must be **clamped**. In HDR/linear-light pipelines, low-end clipping can be mitigated by working in a log domain (Wikipedia: interpolated values then become a weighted *geometric* rather than arithmetic mean).

## 6. From 1D to 2D

### 6.1 Separability (proof) and complexity
The 2D Lanczos kernel is the tensor product L₂(x,y)=L(x)·L(y). The full 2D convolution
S(x,y) = Σ_i Σ_j s[i,j] L(x−i) L(y−j)
factors because L(x−i)L(y−j) factors:
S(x,y) = Σ_i L(x−i) [ Σ_j s[i,j] L(y−j) ].
The inner sum is a 1D pass producing an intermediate image; the outer sum is a 1D pass in the other direction. So **applying the 1D kernel along rows then columns is exactly equal to the 2D tensor-product convolution** for a genuinely separable kernel (Lanczos, being a product, is).

**Complexity** (N×N output, 2a-tap kernel):
- Non-separable (direct 2D): (2a)² products per output → **O(N²·(2a)²)**.
- Separable (two 1D passes): 2a products per pixel per pass → **O(N²·2a)**.
For a=3, 36 vs 12 multiply-adds per pixel — a 3× win; the ratio is (2a)²/(2·2a)=a. This is why every production library resizes separably.

### 6.2 Full 2D interpolation formula with limits and normalization
With source coordinate (u,v), and u₀=⌊u⌋, v₀=⌊v⌋:

S(u,v) = [ Σ_{i=u₀−a+1}^{u₀+a} Σ_{j=v₀−a+1}^{v₀+a} s[i,j]·L(u−i)·L(v−j) ] / [ Σ_i Σ_j L(u−i) L(v−j) ]

The sums cover the (2a)² neighbourhood where L is nonzero. By separability the denominator equals (Σ_i L(u−i))·(Σ_j L(v−j)), so you can normalize each 1D pass independently.

### 6.3 Coordinate mapping and half-pixel offsets
The correct convention treats a pixel's *value* as living at its **center**. With output index x_dst (0-based) and scale = dst_size/src_size, the source coordinate is:

**u = (x_dst + 0.5) / scale − 0.5   ≡   (x_dst + 0.5)·(src/dst) − 0.5.**

The +0.5/−0.5 are the **half-pixel offsets** that align pixel *centers* rather than *edges*. Skipping them (u = x_dst/scale) shifts the whole image by a fraction of a pixel — subtle but real, most visible as directional blur/shift after round trips. OpenCV's docs adopt "origin at the center of the top-left pixel."

**align_corners=True vs False** (PyTorch/TensorFlow):
- **align_corners=False** (half-pixel-centers model; PyTorch default since 0.4; what Pillow/OpenCV effectively do): u = (x_dst+0.5)/scale − 0.5. Geometrically consistent and scale-factor consistent.
- **align_corners=True** (match-endpoints model): u = x_dst·(src−1)/(dst−1), forcing corner pixel *centers* to coincide and preserving their values. Changes effective sample spacing and gives slightly shifted/stretched results; PyTorch documents it only affects linear/bilinear/bicubic/trilinear. PyTorch issue #76487 shows that with align_corners=True the correct output size is (size−1)·scale+1, an off-by-one vs the align_corners=False formula ⌊size·scale⌋ — a real cross-framework mismatch (TensorFlow/TensorRT/tfjs have all had bugs here).

### 6.4 Kernel scaling for downscaling
For a downscale ratio r = src/dst > 1, use the *stretched, renormalized* kernel:

L_scaled(x) = (1/r) · L(x/r),  with support widened to 2a·r taps.

The 1/r keeps DC gain = 1; the x/r lowers the cutoff to the output Nyquist (anti-aliasing). **Omitting this stretch is the classic aliasing bug on minification.** Pillow does the stretch (`precompute_coeffs` sets `filterscale = scale` when scale>1 and `support = filter->support * filterscale`); OpenCV's INTER_LANCZOS4 does **not** — it always uses a fixed 8-tap kernel regardless of downscale factor, so it aliases when shrinking (Part 2).

## 7. Boundary / edge handling

| Mode | Rule | Effect on normalization |
|---|---|---|
| **Zero-pad** (constant) | Out-of-bounds = 0 | Denominator ΣL includes those taps' weights; unless you exclude them, edges darken. Best combined with renormalizing over valid taps only. |
| **Clamp / replicate** ("edge") | Repeat nearest edge pixel | Edge pixel over-weighted; denominator unaffected; safe, mild bias. |
| **Reflect** ("symmetric", `…cb\|abc…`) | Mirror including edge pixel | Good continuity; real values. |
| **Reflect_101** ("reflect", excludes edge) | Mirror excluding edge pixel | OpenCV's default border; smooth, no duplication. |
| **Wrap** (periodic) | Tile the image | Correct only for genuinely tiling textures. |

Best practice: compute the weighted sum only over in-bounds taps and **divide by the sum of just those weights** (border renormalization) — equivalent to a well-behaved edge extension, avoiding frame darkening/brightening.

## 8. Rigorous comparison with alternative kernels

### 8.1 The kernels
- **Nearest neighbour (box), support 1:** k(x)=1 for |x|<½ else 0. Zero ringing, but blocky; broad-sinc spectrum → heavy aliasing/jaggies.
- **Bilinear (tent/triangle), support 2:** k(x)=1−|x| for |x|<1. Continuous but with a corner at 0; tapered spectrum → blurring; no ringing (weights ≥0). Turkowski: 15 dB better alias suppression than box but loses passband detail.
- **Bicubic — Keys' cubic convolution (1981), support 4:** piecewise cubic with a free parameter a. From Keys (IEEE ASSP-29(6):1153–1160):
  W(x) = (a+2)|x|³ − (a+3)|x|² + 1, 0≤|x|<1;
  W(x) = a|x|³ − 5a|x|² + 8a|x| − 4a, 1≤|x|<2; 0 otherwise.
  - **a = −0.5**: Keys proved this is the unique value giving *third-order* accuracy; equals **Catmull–Rom**. In expanded form: (3/2)|x|³−(5/2)|x|²+1 and −(1/2)|x|³+(5/2)|x|²−4|x|+2.
  - **a = −0.75**: OpenCV's INTER_CUBIC default (`const float A = -0.75f;`), slightly softer.
- **Mitchell–Netravali (1988) (B,C) family, support 4:** (1,0)=cubic B-spline (very smooth/blurry, approximating); (0,0.5)=Catmull–Rom; **(1/3,1/3)=recommended Mitchell filter**, an excellent sharpness/ringing balance. Mitchell & Netravali: "Ringing results when k(x) has negative side lobes."
- **B-spline (cubic):** (1,0); pure smoothing, no ringing, blurs, does not interpolate the samples.
- **Lanczos2/3/4:** windowed sinc; sharpest classical filters, mild ringing, good alias suppression.
- **Area / box averaging:** for minification, average all input pixels covered by each output pixel — excellent, moiré-free downscaling (OpenCV INTER_AREA); degenerates toward nearest on upscaling.
- **Magic Kernel Sharp (John Costella):** the "magic kernel" {1/4, 3/4, 3/4, 1/4} for 2× doubling plus a sharpening post-filter. Per Costella's "Solving the mystery of Magic Kernel Sharp" (johncostella.com/magic/mks.pdf), the **"Magic Kernel Sharp 2013" version powers Facebook and Instagram image resizing**; a sharpened variant **"Magic Kernel Sharp+" (s=1.32) was deployed to Instagram in 2015 by Georges Berenger** "with greater CPU and storage efficiency." Now available in libvips/sharp (`mks2013`, `mks2021`) and proposed for Pillow. Extremely cheap (integer adds/shifts).
- **EWA (Elliptical Weighted Average, Heckbert 1989):** a true 2D *anisotropic* filter fitting an ellipse to the pixel's source-space footprint and weighting texels by a radially symmetric kernel over that ellipse. The gold standard for texture minification under perspective; non-separable and expensive; used in high-quality texture filtering and splatting.
- **Learned / ML super-resolution (SRCNN, VDSR, LapSRN, SwinIR, ESRGAN, …):** a *different category* — these hallucinate plausible high-frequency detail from training priors rather than reconstructing a band-limited signal. They beat all fixed kernels on PSNR/SSIM/perceptual metrics but are orders of magnitude more expensive and can invent detail that isn't real.

### 8.2 Trade-off table
| Filter | Taps (1D) | Sharpness | Ringing | Aliasing (minify) | Cost | Interpolating? |
|---|---|---|---|---|---|---|
| Nearest | 1 | N/A (blocky) | None | Severe | Trivial | Yes |
| Bilinear | 2 | Low (blurry) | None | Moderate | Very low | Yes |
| Bicubic (Keys a=−0.5) | 4 | Good | Mild | Moderate | Low | Yes |
| Mitchell (B=C=1/3) | 4 | Good | Very low | Low | Low | No (approx.) |
| B-spline | 4 | Low (smooth) | None | Low | Low | No |
| Catmull–Rom | 4 | High | Mild | Moderate | Low | Yes |
| Lanczos2 | 4 | High | <1% | Low–moderate | Moderate | Yes |
| Lanczos3 | 6 | Very high | Moderate | Low | Higher | Yes |
| Lanczos4 (OpenCV) | 8 | Very high | Higher | Low (if scaled) | High | Yes |
| Area/box | varies | N/A | None | Excellent (minify) | Low | — |
| Magic Kernel Sharp | 4–6 | High | Very low | Very low | Very low | ~Yes |
| EWA (anisotropic) | many | High | Low | Excellent | High | — |
| ML super-res | — | Highest | — | — | Very high | — |

### 8.3 PSNR/SSIM behaviour and empirical caveats
Empirical results are **mixed and content-dependent** — worth stating honestly:
- Several studies find bicubic ≈ Lanczos, and sometimes bicubic *ahead*. The study "Resolution Enhancement of Scanning Electron Micrographs using Artificial Intelligence" (arXiv:2410.03746), on a dual-phase steel dataset (DP-small), reports **Bi-Cubic SSIM 0.622±0.002 / PSNR 25.57 dB±0.05 vs Lanczos 0.574±0.002 / 24.38 dB±0.04** (bicubic better), noting "Contrary to the expectations, the bi-cubic interpolation performs better than the Lanczos interpolation."
- A digital-rock SEM study found *bilinear* gave the highest PSNR on downscale-then-compare (PSNR rewards smoothness/low ringing, penalizing Lanczos's edge overshoot).
- ML methods (e.g., SwinIR) clearly outperform all fixed kernels on PSNR at 4×.

Takeaway: **PSNR/SSIM often favor smoother filters** because they penalize the very edge overshoot that makes Lanczos look subjectively sharper. Choose by task and by eye, not by PSNR alone.

### 8.4 When Lanczos is right — and when it is not
**Use Lanczos (a=2 or 3) when:** photographic/continuous-tone content, high-quality downscaling (with proper kernel scaling), general-purpose upscaling where perceived sharpness matters, live-action video upscaling.

**Avoid or reconsider when:**
- **Pixel art / hard-edged graphics:** ringing destroys crisp edges — use nearest or dedicated pixel-art scalers.
- **Text / line art / motion graphics:** halos around glyphs and lines are objectionable (ffmpeg guidance: animation "may suffer due to the ringing effects of lanczos").
- **HDR / linear-light correctness:** always resample in **linear light** (below).
- **Alpha masks, depth maps, normal maps, label/index maps:** negative-lobe overshoot creates invalid values — use non-negative kernels (bilinear/box) or nearest for labels.

**Gamma-correct (linear-light) resampling — why it matters.** sRGB pixel values are *perceptually* encoded (roughly value = intensity^{1/2.2}); they are **not** proportional to light intensity. Interpolation is linear and is only physically correct on *linear* quantities. Blending sRGB values directly makes results too dark (downscaling a black/white checker yields muddy gray instead of 50% gray). Correct pipeline: **(1) decode sRGB→linear, (2) [premultiply alpha], (3) resample in linear light, (4) [un-premultiply], (5) encode linear→sRGB.** The sRGB *encode* transfer function is 12.92·c for c ≤ 0.0031308, else 1.055·c^{1/2.4} − 0.055. GIMP, ImageMagick, and Paint.NET do this correctly; many naive pipelines do not. This is independent of the kernel but doubly important for Lanczos because its overshoot interacts with the nonlinearity.

---

# PART 2: PRACTICAL IMPLEMENTATION

All code is Python 3 with NumPy: clarity first, then optimization.

## 2.1 Minimal 1D Lanczos kernel and naive 1D interpolation

```python
import numpy as np

def lanczos_kernel(x, a=3):
    """
    Lanczos kernel L(x) = sinc(x) * sinc(x/a) for |x| < a, else 0.
    numpy.sinc IS the NORMALIZED sinc: sinc(t) = sin(pi t)/(pi t), sinc(0)=1.
    Maps directly to Part 1 sec 5.2-5.3.
    """
    x = np.asarray(x, dtype=np.float64)
    out = np.sinc(x) * np.sinc(x / a)         # product of two sincs (sec 5.2); L(0)=1 automatic
    out = np.where(np.abs(x) < a, out, 0.0)    # hard support: zero for |x| >= a
    return out

def resample_1d_naive(samples, out_len, a=3):
    """1D Lanczos resample with half-pixel mapping (6.3), minify stretch (6.4),
       clamp border (7), per-output normalization (5.5)."""
    samples = np.asarray(samples, dtype=np.float64)
    in_len = samples.shape[0]
    scale = out_len / in_len
    inv_scale = 1.0 / scale                     # source units per dest pixel
    filt_scale = max(1.0, inv_scale)            # widen kernel when shrinking (Pillow's filterscale)
    support = a * filt_scale
    out = np.empty(out_len, dtype=np.float64)
    for xo in range(out_len):
        u = (xo + 0.5) * inv_scale - 0.5        # dest center -> source coord (6.3)
        i0 = int(np.ceil(u - support)); i1 = int(np.floor(u + support))
        acc = wsum = 0.0
        for i in range(i0, i1 + 1):
            ic = min(max(i, 0), in_len - 1)     # clamp/replicate border
            w = lanczos_kernel((u - i) / filt_scale, a)  # scaled kernel argument
            acc += w * samples[ic]; wsum += w
        out[xo] = acc / wsum if wsum != 0 else 0.0        # normalize (5.5)
    return out
```

## 2.2 From-scratch 2D magnification, naive (non-separable)

```python
def resample_2d_naive(img, out_h, out_w, a=3):
    """Correct but slow O(out_h*out_w*(2a)^2) 2D Lanczos, to make sec 6.2 concrete."""
    img = np.asarray(img, dtype=np.float64)
    single = (img.ndim == 2)
    if single: img = img[:, :, None]
    H, W, C = img.shape
    sy, sx = out_h / H, out_w / W
    iny, inx = 1.0 / sy, 1.0 / sx
    fsy, fsx = max(1.0, iny), max(1.0, inx)
    supy, supx = a * fsy, a * fsx
    out = np.zeros((out_h, out_w, C), dtype=np.float64)
    for yo in range(out_h):
        v = (yo + 0.5) * iny - 0.5
        j0, j1 = int(np.ceil(v - supy)), int(np.floor(v + supy))
        for xo in range(out_w):
            u = (xo + 0.5) * inx - 0.5
            i0, i1 = int(np.ceil(u - supx)), int(np.floor(u + supx))
            acc = np.zeros(C); wsum = 0.0
            for j in range(j0, j1 + 1):
                wj = lanczos_kernel((v - j) / fsy, a); jc = min(max(j, 0), H - 1)
                for i in range(i0, i1 + 1):
                    wi = lanczos_kernel((u - i) / fsx, a); ic = min(max(i, 0), W - 1)
                    w = wi * wj                  # 2D tensor weight (6.2)
                    acc += w * img[jc, ic]; wsum += w
            out[yo, xo] = acc / wsum if wsum else 0.0
    return out[:, :, 0] if single else out
```

## 2.3 Optimized separable implementation (precomputed sparse weight matrices)

The "resize as two matrix multiplies" trick: build a sparse (out × in) weight matrix per axis, then `out = Wy @ img @ Wx.T`.

```python
import numpy as np
from scipy import sparse

def build_weights(in_len, out_len, a=3):
    """(out_len x in_len) sparse Lanczos weight matrix for one axis, with
       half-pixel mapping, minify stretch, border clamp, per-row normalization."""
    scale = out_len / in_len; inv = 1.0 / scale
    filt = max(1.0, inv); support = a * filt
    ksize = int(np.ceil(support) * 2 + 1)       # matches Pillow's ksize formula
    rows = np.repeat(np.arange(out_len), ksize)
    cols = np.empty(out_len * ksize, dtype=np.int64)
    data = np.empty(out_len * ksize, dtype=np.float64)
    for xo in range(out_len):
        u = (xo + 0.5) * inv - 0.5
        left = int(np.floor(u - support)) + 1
        idx = left + np.arange(ksize)
        t = (u - idx) / filt
        w = np.where(np.abs(t) < a, np.sinc(t) * np.sinc(t / a), 0.0)
        s = w.sum()
        if s != 0: w = w / s                    # normalize per output pixel (5.5)
        cidx = np.clip(idx, 0, in_len - 1)      # clamp border
        base = xo * ksize
        cols[base:base+ksize] = cidx; data[base:base+ksize] = w
    # coo->csr sums duplicate (clamped) columns automatically
    return sparse.coo_matrix((data, (rows, cols)), shape=(out_len, in_len)).tocsr()

def resize_separable(img, out_h, out_w, a=3):
    img = np.asarray(img, dtype=np.float64)
    single = img.ndim == 2
    if single: img = img[:, :, None]
    H, W, C = img.shape
    Wx = build_weights(W, out_w, a)             # (out_w x W)
    Wy = build_weights(H, out_h, a)             # (out_h x H)
    tmp = np.stack([img[:, :, c] @ Wx.T for c in range(C)], axis=-1)  # horizontal pass
    out = np.stack([Wy @ tmp[:, :, c] for c in range(C)], axis=-1)    # vertical pass
    return out[:, :, 0] if single else out
```

**Measured speedup.** On a 512×512 → 1024×1024 RGB upscale, the naive triple-loop `resample_2d_naive` runs on the order of tens of seconds, while `resize_separable` completes in tens of milliseconds — a speedup of roughly two to three orders of magnitude on a typical laptop CPU. Exact numbers are machine- and size-dependent; the point is the asymptotic O((2a)²)→O(2a) win per pixel *plus* moving the inner loops into BLAS. Measure on your own hardware.

## 2.4 Correct handling of the tricky details

```python
def srgb_to_linear(x):        # decode sRGB (0..1 float) -> linear light (8.4)
    a = 0.055
    return np.where(x <= 0.04045, x / 12.92, ((x + a) / (1 + a)) ** 2.4)

def linear_to_srgb(x):        # encode linear -> sRGB
    a = 0.055
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, x * 12.92, (1 + a) * x ** (1/2.4) - a)

def resize_image_correct(img_u8, out_h, out_w, a=3, has_alpha=False):
    """Production path: dtype handling, linear-light, premultiplied alpha, clamp overshoot."""
    f = img_u8.astype(np.float64) / 255.0       # uint8 -> float (precision)
    if has_alpha:
        rgb, alpha = f[..., :3], f[..., 3:4]
        rgb_lin = srgb_to_linear(rgb)           # linearize color only, NOT alpha
        prem = rgb_lin * alpha                   # PREMULTIPLY (alpha)
        prem_r = resize_separable(prem, out_h, out_w, a)
        a_r = np.clip(resize_separable(alpha, out_h, out_w, a), 0.0, 1.0)
        rgb_lin_r = np.divide(prem_r, a_r, out=np.zeros_like(prem_r), where=a_r > 1e-6)
        out = np.concatenate([linear_to_srgb(rgb_lin_r), a_r], axis=-1)
    else:
        out = linear_to_srgb(resize_separable(srgb_to_linear(f), out_h, out_w, a))
    out = np.clip(out, 0.0, 1.0)                 # CLAMP overshoot (5.7)
    return (out * 255.0 + 0.5).astype(np.uint8)
```

Key points: compute in float, quantize once at the end (+0.5 rounding); **clamp** only at the final encode in the right color space (never clamp intermediate premultiplied buffers); **premultiply alpha** before resampling and divide out after (otherwise transparent-edge dark halos); **never gamma-encode the alpha channel**.

## 2.5 Verification against Pillow, OpenCV, scikit-image, PyTorch

```python
import numpy as np
from PIL import Image
import cv2, torch, torch.nn.functional as F
from skimage.transform import resize as sk_resize

src = (np.random.rand(64, 64, 3) * 255).astype(np.uint8)
mine = resize_separable(src.astype(np.float64)/255., 128, 128, a=3)          # ours (raw, no gamma)
pil  = np.asarray(Image.fromarray(src).resize((128,128), Image.LANCZOS))/255.# a=3, support-scaled
ocv  = cv2.resize(src, (128,128), interpolation=cv2.INTER_LANCZOS4)/255.     # a=4, fixed 8x8, no scale
skb  = sk_resize(src, (128,128), order=3, anti_aliasing=True)                # bicubic (no Lanczos)
t = torch.from_numpy(src.transpose(2,0,1)[None].astype(np.float32))/255.
pt = F.interpolate(t, size=(128,128), mode='bicubic', align_corners=False)   # bicubic (no Lanczos)
print("mine vs pillow MAE:", np.abs(mine-pil).mean())
print("mine vs opencv MAE:", np.abs(mine-ocv).mean())
```

**Why they differ (documented facts):**
- **Pillow `Image.LANCZOS`**: order **a = 3** (`_filters_support[LANCZOS] = 3.0`). It **scales the support on downscale** (`filterscale = scale; support = filter->support * filterscale`, `ksize = ceil(support)*2 + 1`), so it anti-aliases correctly when minifying. Center-based (half-pixel) mapping. Your from-scratch a=3 with support scaling should match Pillow to well under 1 LSB on upscale; residual differences on downscale come from Pillow's fixed-point 8-bit coefficient quantization and clip semantics.
- **OpenCV `INTER_LANCZOS4`**: order **a = 4**, an **8-tap / 8×8** neighborhood. Its `interpolateLanczos4` computes 8 coefficients using constant `s45 = 0.70710678118654752440084436210485` (=√2/2) and a table `cs[][2]` of 45°-spaced (cos,sin) pairs (a trig reconstruction of sin((x+3−i)·π/4)/y²), then **normalizes the 8 weights to sum to 1**. It receives only the fractional offset and produces a **fixed 8-tap kernel with no scale argument** — OpenCV does **not** widen the kernel for downscaling, so **INTER_LANCZOS4 aliases badly when shrinking** (OpenCV recommends `INTER_AREA` for decimation). It uses fixed-point arithmetic (`INTER_BITS = 5`, a 32-entry coefficient table). This is the single biggest behavioral difference from Pillow.
- **scikit-image**: `resize` has **no Lanczos kernel**; only spline `order` 0–5 (0 nearest, 1 bilinear, 3 bicubic-equivalent) with optional Gaussian `anti_aliasing` for downscale. It will never match a Lanczos result exactly.
- **PyTorch `F.interpolate`**: modes are nearest/linear/bilinear/bicubic/trilinear/area — **no Lanczos**. Its bicubic uses Keys a=−0.75. `align_corners` changes the coordinate mapping (§6.3); default False matches the half-pixel convention. Documented cross-framework disagreement (PyTorch vs TensorFlow/tfjs/TensorRT) exists on align_corners semantics and output-size computation.

**Known gotchas / bugs:** OpenCV issue #16192 documents `resize(INTER_LANCZOS4)` operating with invalid coefficients on certain sizes (e.g., full zero/NaN rows). Pillow historically had a bug where LANCZOS *upscaling* quality "was almost the same as BILINEAR," fixed in **Pillow 2.7.0**; `ANTIALIAS` is a deprecated alias for `LANCZOS`.

## 2.6 Visual and quantitative evaluation

```python
import numpy as np, matplotlib.pyplot as plt

# (a) Kernel shape and frequency response
x = np.linspace(-4, 4, 2001)
for a in (2, 3, 4): plt.plot(x, lanczos_kernel(x, a), label=f'a={a}')
plt.axhline(0, color='k', lw=0.5); plt.legend(); plt.title('Lanczos kernels (note negative lobes)')
k = lanczos_kernel(np.arange(-64, 64, 0.25), a=3)
H = np.abs(np.fft.rfft(k, 4096)); H /= H.max()
plt.figure(); plt.plot(20*np.log10(H + 1e-9)); plt.title('Lanczos3 magnitude response (dB)')

# (b) Step edge -> over/undershoot (ringing)
edge = np.concatenate([np.zeros(16), np.ones(16)])
plt.figure(); plt.plot(resample_1d_naive(edge, 256, a=3)); plt.title('Step edge: ringing')

# (c) Zone plate (radial chirp) -> aliasing test on minify
n = 512; yy, xx = np.mgrid[-n//2:n//2, -n//2:n//2]
zone = 0.5 + 0.5*np.cos(0.0009*(xx**2 + yy**2))
small = resize_separable(zone, 128, 128, a=3)   # proper scaled kernel -> little moire

# (d) PSNR on a downscale-then-upscale round trip
def psnr(a, b):
    mse = np.mean((a.astype(np.float64) - b)**2)
    return 100.0 if mse == 0 else 10*np.log10((255.0**2)/mse)
orig = (zone*255).astype(np.uint8)
back = resize_separable(resize_separable(orig/255., 128, 128, 3), 512, 512, 3)*255.
print("round-trip PSNR:", psnr(orig, back))
```

To *see* ringing/halos: upscale a black/white block or text glyph with Lanczos3 and look for light/dark bands hugging edges. To *see* aliasing: minify a zone plate **without** kernel scaling (bug) vs **with** scaling (correct) and compare moiré. For SSIM use `skimage.metrics.structural_similarity`.

## 2.7 Performance and production notes
- **Cost.** Separable Lanczos is O(N²·2a) MACs plus one intermediate buffer; for a=3, 12 MACs/pixel/pass. Memory bandwidth (the intermediate transpose) often dominates over arithmetic.
- **Fixed-point + SIMD.** Production libraries (Pillow, OpenCV, libswscale) precompute integer coefficients (Pillow: 8-bit fractional; OpenCV: `INTER_BITS = 5` → 32-entry table) and use integer MACs with SIMD (SSE/AVX/NEON), processing several pixels per instruction — faster and bit-exact reproducible. OpenCV converts float coordinate maps to fixed-point `(CV_16SC2, CV_16UC1)` for ~2× faster remap.
- **GPU.** Lanczos is a fragment/compute shader: for each output texel, sample the 2a×2a neighborhood, evaluate weights (or read a small LUT texture), accumulate, normalize. PyTorch has no native Lanczos; implement it with precomputed separable weight tensors via `conv2d`/`unfold`, or a custom CUDA kernel. GLSL Lanczos shaders are common in emulators and players (RetroArch; mpv `--scale=lanczos`).
- **Separable-pass caching.** Resizing many images by the same factor: precompute `build_weights` once and reuse. Resizing one image to many sizes: cache per-axis coefficients.
- **Throughput.** A well-vectorized CPU Lanczos3 resize of a multi-megapixel image runs in the low-milliseconds-to-tens-of-milliseconds range per image on a modern core; GPU implementations reach real-time video rates.
- **Pipelines.**
  - **ffmpeg / libswscale**: `-vf scale=w:h -sws_flags lanczos`. The Lanczos "width (alpha)" **defaults to 3** and is set via `param0` (e.g., `param0=5` widens to a=5). `alphablend` controls alpha handling when output lacks alpha. Consensus favors lanczos for live action; animation/motion-graphics may show its ringing.
  - **Video upscaling / texture filtering**: Lanczos for live action; EWA/anisotropic for 3D textures under perspective.
  - **Preprocessing for OCR / vision models**: Lanczos (or area for downscale) is a common high-quality resize; but many ML pipelines used PIL bicubic/bilinear, and *mismatched* resize (OpenCV vs PIL, or antialias on/off) between train and inference measurably degrades accuracy — match the exact resize used in training.

## 2.8 Common mistakes checklist
1. **Forgetting normalization** (dividing by Σweights) → faint brightness ripple/banding (Lanczos isn't a partition of unity).
2. **Wrong coordinate mapping** — using `x/scale` instead of `(x+0.5)/scale − 0.5`, or mixing align_corners conventions → half-pixel shift.
3. **Resampling in sRGB instead of linear light** → darkened downscales, wrong edge colors.
4. **Not scaling the kernel when downscaling** → aliasing/moiré (exactly why OpenCV INTER_LANCZOS4 aliases and Pillow does not).
5. **Clamp vs clip confusion** — clamp only at the final encode, in the right space; never clamp intermediate premultiplied buffers.
6. **Mishandling alpha** — always premultiply before resampling, divide after; never gamma-encode alpha.
7. **Quantizing too early / dtype errors** — compute in float, round once at the end.
8. **Using Lanczos for labels/masks/pixel art** — negative-lobe overshoot invalidates index maps and wrecks crisp edges; use nearest or non-negative kernels.

---

# Recommendations

1. **Understand the pipeline, then implement in stages.** Read Part 1 §§2–5 (sampling → sinc → windowing → Lanczos), code the §2.1 1-D kernel, and verify L(0)=1, L(n)=0, and the visible negative lobes for a≥2. This grounds every later decision.
2. **Ship the separable precomputed-weights version (§2.3), not the naive loop.** The naive 2D version is pedagogy only. Benchmark both to see the ~100–1000× gap firsthand.
3. **Default to a = 3 for photographic upscaling and high-quality downscaling.** Use a = 2 if ringing is objectionable or speed matters; reserve a = 4 for maximum sharpness where you tolerate more ringing/cost. This matches Pillow (a=3) and Blinn's recommendation.
4. **Always apply the six correctness rules:** half-pixel mapping, per-pixel normalization, kernel scaling on minification, linear-light resampling, premultiplied alpha, final-only clamping. The §2.4/§2.5 code encodes all of them.
5. **When matching a library, know its conventions.** Reproduce Pillow: a=3 + support scaling + half-pixel + normalize. Reproduce OpenCV INTER_LANCZOS4: a=4, fixed 8 taps, no downscale kernel scaling, fixed-point rounding — and expect aliasing on shrink (prefer INTER_AREA for decimation). scikit-image and PyTorch have **no** Lanczos; don't expect a match.
6. **Choose the filter by task, not by PSNR.** Nearest for pixel art/labels; bilinear/box for masks/normal maps; Mitchell (B=C=1/3) for text/animation to avoid halos; ML super-resolution for extreme-quality upscaling. Validate by eye on your actual content (step edges, zone plate, text).
7. **Thresholds that change the plan:** moiré on downscale → kernel not being scaled (fix §6.4); consistent directional shift → coordinate-mapping/align_corners bug (fix §6.3); downscaled images too dark → resampling in sRGB (fix with linear light); transparent-edge halos → premultiply alpha.

# Caveats
- **Convention disagreements are real and flagged rather than hidden:** (i) normalized vs unnormalized sinc (π factors) — both appear; I used normalized. (ii) "a" is variously called order, lobe count, radius, and shares the letter with Keys' bicubic parameter. (iii) Whether the kernel is scaled on downscale differs by library (Pillow yes, OpenCV no). (iv) align_corners True/False and output-size formulas differ across PyTorch/TensorFlow/TensorRT and have had documented bugs.
- **Empirical PSNR/SSIM results are mixed and content-dependent.** Peer-reviewed studies (e.g., arXiv:2410.03746, dual-phase steel: Bicubic 0.622/25.57 dB vs Lanczos 0.574/24.38 dB) find bicubic ≈ or > Lanczos, largely because these metrics penalize Lanczos's edge overshoot. "Lanczos is best" is a *subjective* "best compromise," not a universal quantitative claim.
- **The §2.3 speedup figures are order-of-magnitude, machine-dependent estimates**, not a specific benchmark run — measure on your target hardware.
- **OpenCV's `interpolateLanczos4` code, Pillow's `precompute_coeffs`, and Keys' coefficients** were verified from the OpenCV and Pillow sources and Keys (1981); minor version drift is possible, so check the version you ship against.
- **Primary sources** used: Lanczos, *Applied Analysis* (1956); Duchon (1979, *J. Appl. Meteorol.* 18(8):1016–1022); Keys (1981, IEEE ASSP-29(6):1153–1160); Mitchell & Netravali (1988); Blinn, *IEEE CG&A* 9(2), 1989; Turkowski, "Filters for Common Resampling Tasks" (Graphics Gems I, 1990); Pillow and OpenCV source/docs; ffmpeg swscale docs; Costella, "Solving the mystery of Magic Kernel Sharp"; and Mazzoli's derivation for the Gibbs-suppression argument.