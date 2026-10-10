# Outline — Kernel Design

**Title:** Kernel Design: Separability, Borders, Optimised Derivatives (59 chars). The plan's
title, *Kernel Design: Separability, Borders, and Optimised Derivative Filters*, is 70 chars and
over the gate's 60; this keeps all four of its keywords and the slug is unchanged.
**Slug:** `kernel-design-separability-borders-derivatives`
**Series:** `image-processing`, part 4 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** advanced
**Budget:** 6,500 words planned; final draft 7,395 (L3 range 5,000–7,500) · **Figures:** 11 (L3 range 8–12)
**Parent:** `image-processing-by-hand` (https://canery.in/blogs/image-processing-by-hand) —
assumes its filter stage, anchor `#stage-2--filter-every-linear-filter-is-one-weighted-sum`,
its Figure 6 (separability) and Figure 7 (border modes). Extends both; repeats neither.
**Hands off:** edge-*preserving* kernels to Part 7 (*Edge-Preserving Smoothing: Bilateral,
Non-Local Means, Anisotropic Diffusion*); scale selection to Part 10 (*Scale Space and SIFT: Why σ
Is a Search Dimension*). Both by title only — neither is published. Part 3 is built but not
published, so it is not referenced.

Nothing is run against an image. Every number below is worked by hand on the shared patch and
cross-checked with plain-Python arithmetic (`math` only, no packages; `worked.py` and
`worked2.py` in the session scratchpad). Curves are evaluated from closed-form transfer
functions and captioned as such. Library behaviour carries a ledger key to source or docs at a
pinned commit.

**Checkpoints.** The session could not pause for replies, as with Part 3, so Checkpoints A and B
ran without a stop, and what each would have shown is recorded here. **A:** 18 sources, 8 of
them peer-reviewed with identifiers (floor 7; five used for their abstracts only, and the
ledger says so); 5 databases in the log (floor 4); 44 claims; 3 paper figures considered and
not reused. Two blocked primary sources (Scharr's 1997 paper and 2000 thesis) are recorded as
open questions, and the post never attributes a weighting function to Scharr. **B:** this file.

**One finding changes a published number.** OpenCV's `getGaussianKernel` returns a hard-coded
table when σ ≤ 0 and ksize is 3, 5, 7 or 9 (L26), and the table's 3-tap entry is the binomial
[0.25, 0.5, 0.25], not the sampled σ = 0.8 weights [0.239, 0.522, 0.239] that Part 1 derived
from the documented formula (L28). So `GaussianBlur(img, (3, 3), 0)` is the binomial. The
series' shared kernel remains a correct kernel — it is `GaussianBlur(img, (3, 3), 0.8)` — and
its variance of 0.478 stands, but Part 1's sentence "the default 3×3 Gaussian blur has σ = 0.8"
is wrong about the default. This post states the fact in its truncation section, as it owns
kernel provenance. Correcting Part 1 itself is a decision for the author, flagged in
`context.md`.

---

## The spine

A kernel's numbers are the solution to a stated criterion. Three things fix them:

```
constraints  what it must preserve    smoother sums to 1; derivative sums to 0 with unit slope on a ramp
budget       what it may cost         taps, and whether it separates into 1-D passes
criterion    what it optimises        direction, matching, mass, variance — "optimal" names one
```

And one thing the taps do not show: at the image border the kernel reads values that do not
exist, so the border rule is part of the kernel.

The worked example proves the central case on the patch: **every 3×3 first-derivative filter
is one stencil with one free number p**, [p, 1 − 2p, p]ᵀ ⊗ ½[−1, 0, 1]. Central difference,
Scharr, Sobel, Prewitt, a 3-tap sampled Gaussian derivative and Farid–Simoncelli's 3-tap pair
are values of p. "Optimal" picks p by a criterion: direction wants p near 3/16, the impulse on
the patch wants p large.

---

## Verified numbers

### The family

| Member | p | Note |
|---|---|---|
| central difference | 0 | no cross-smoothing |
| [1 4 1]/6 | 1/6 = 0.1667 | exact direction to second order in frequency |
| Scharr [3 10 3]/16 | 0.1875 | L10, L11 |
| Farid–Simoncelli 3-tap | 0.229879 | L04; ramp gain 2·0.425287 = 0.8506 |
| sampled Gaussian, σ = 0.8 (the shared kernel) | 0.2390 | e^(−1/1.28)/(1 + 2e^(−1/1.28)) |
| Sobel [1 2 1]/4 | 0.25 | L32; also OpenCV's σ = 0 3-tap blur (L26) |
| sampled Gaussian, σ = 1 | 0.2741 | |
| Prewitt [1 1 1]/3 | 1/3 | L43 |

3-tap sampled Gaussian with p = 1/6 has σ = 0.601; with p = 3/16, σ = 0.644; with p = 1/4,
σ = 0.849.

### On the patch (normalised to slope 1 on a ramp)

- (2, 3), clean edge: row differences 80, 80, 80 → every member gives **80**. Raw library
  scales: `cv2.Sobel` 640 (×8), `cv2.Scharr` 2560 (×32), scikit-image per axis 160 (×2),
  scikit-image magnitude 113.1 (÷√2).
- (2, 2), impulse at (2, 1): row differences **80, −27.5, 80** → output **80 − 107.5(1 − 2p)**.

| Member | (2, 2) | Error vs clean 80 |
|---|---|---|
| central difference | −27.5 | 134% |
| [1 4 1]/6 | 8.33 | 89.6% |
| Scharr | 12.81 | 84.0% |
| Farid–Simoncelli 3 (normalised) | 21.92 | 72.6% |
| sampled Gaussian σ = 0.8 | 23.88 | 70.1% |
| Sobel | 26.25 | 67.2% (Part 1's 640 → 210) |
| Prewitt | 44.17 | 44.8% |

Raw: `cv2.Sobel` 210, `cv2.Scharr` 410.

### Implicit smoothing and matching (closed form)

S(ω) = sin ω / ω; B_p(ω) = 1 − 2p + 2p cos ω; p that makes B_p = S at ω:
(1 − S)/(2(1 − cos ω)).

| wavelength (px) | S | matching p | B at 1/6 | B at 3/16 | B at 1/4 |
|---|---|---|---|---|---|
| ∞ | 1 | 0.1667 | 1 | 1 | 1 |
| 8 | 0.9003 | 0.1702 | 0.9024 | 0.8902 | 0.8536 |
| 4 | 0.6366 | 0.1817 | 0.6667 | 0.6250 | 0.5000 |
| 3.45 | — | **0.1875** | | | |
| 3 | 0.4135 | 0.1955 | 0.5000 | 0.4375 | 0.2500 |
| 2 (Nyquist) | 0 | **0.25** | 0.3333 | 0.25 | 0 |

For p = 3/16, B/S stays within 0.978–1 from DC to 3.45 px.

### Worst angular error over orientation (closed form, plane waves)

| Filter | 8 px | 4 px | 3 px |
|---|---|---|---|
| central difference | 1.54° | 7.22° | 15.49° |
| [1 4 1]/6 | 0.03° | 0.64° | 2.64° |
| Scharr | 0.16° | 0.29° | 0.64° |
| Farid–Simoncelli 3 | 0.56° | 2.26° | 3.92° |
| sampled Gaussian σ = 0.8 | 0.65° | 2.70° | 4.96° |
| Sobel (3 and 5 identical) | 0.75° | 3.24° | 6.26° |
| Prewitt | 1.56° | 7.64° | 17.71° |
| Farid–Simoncelli 5 | 0.09° | 0.17° | 0.06° |
| sampled Gaussian σ = 0.96, 5 taps | 0.41° | 1.42° | 1.68° |

Leading order: Δθ ≈ (ω²/4)(1/6 − p) sin 4θ; worst at 22.5°. Check: central difference at 8 px,
(0.617/4)(1/6) = 0.0257 rad = 1.47° against the exact 1.54°.

p that zeroes the 22.5° error: 0.1667 (∞), 0.1701 (8 px), 0.1811 (4 px), 0.1934 (3 px),
0.2069 (2.5 px).

RMS angular error over the band, optimum p: uniform to half-Nyquist 0.178; cos⁴(ω/2) weight
0.192; cos²(ω/2) weight 0.205; uniform to Nyquist 0.2375.

Sobel ksize=5 = Sobel 3 convolved with [1 2 1] ⊗ [1 2 1] on both components (L32), so the
same direction at every frequency.

### Farid–Simoncelli, recomputed

Minimising ∫₀^π (ωB_a(ω) − 2d sin ω)² / ∫₀^π B_a² over a and d: **a = 0.22984,
d = 0.42539** against the published 0.229879 and 0.425287 (L04). Ramp gains: 3-tap 0.8506,
5-tap 0.9918.

### Truncating σ = 2 (sampled, renormalised)

Full sampled sum 5.01326 = σ√(2π) to 6 places.

| taps | kept | lost | variance | σ_eff | centre weight |
|---|---|---|---|---|---|
| 3 | 55.15% | 44.85% | 0.638 | 0.80 | 0.3617 (sides 0.3192) |
| 5 | 79.35% | 20.65% | 1.663 | 1.29 | 0.2514 |
| 7 | 92.30% | 7.70% | 2.693 | 1.64 | 0.2161 |
| 9 | 97.70% | 2.30% | 3.428 | 1.85 | 0.2042 |
| 13 (OpenCV 8-bit auto) | 99.90% | 0.10% | 3.951 | 1.99 | 0.1997 |
| 17 (OpenCV float auto; SciPy truncate = 4) | 100.00% | 0.00% | 3.999 | 2.00 | 0.1995 |

### Sampled, integrated, discrete; OpenCV's tables

- σ = 0.8 (s = 0.64): sampled untruncated variance 0.6399; sampled 3-tap **0.478**; integrated
  0.7233 (= s + 1/12); discrete analogue exactly 0.64, taps 0.5827, 0.1775, 0.0279, 0.0030.
- Sampling alone: variance −91.5% at σ = 0.3 (raw sum 1.340), −49.5% at 0.4, −14.0% at 0.5,
  −2.3% at 0.6, 0.0% at 0.8. The shared kernel's deficit is truncation.
- OpenCV σ = 0 tables: 3 → [1 2 1]/4, variance 0.5 (docs σ² 0.64); 5 → [1 4 6 4 1]/16,
  1.0 (1.21); 7 → [2 7 14 18 14 7 2]/64, 1.875 (1.96); 9 → [4 13 30 51 60 51 30 13 4]/256,
  2.75 (2.89).
- Impulse under the table's 3×3: 0.25·255 + 0.75·40 = **93.75** (the σ = 0.8 kernel: 98.6).

### Borders on the patch (Sobel normalised; row differences in brackets)

Row r2 extended: constant-0 `0 0 0 | … | 0 0 0`; replicate `40 40 40 | … | 200 200 200`;
reflect `40 255 40 | … | 200 200 40`; reflect-101 `200 40 255 | … | 200 40 255`;
wrap `40 200 200 | … | 40 255 40`.

| Position | constant 0 | replicate | reflect | reflect-101 | wrap |
|---|---|---|---|---|---|
| (2, 0) | 73.75 [20, 127.5, 20] | 53.75 [0, 107.5, 0] | 53.75 | **0** | −26.25 [−80, 27.5, −80] |
| (2, 4) | −100 | 0 | 0 | 0 | **−80** |

Scharr at (2, 0): 87.19, 67.19, 67.19, 0, −12.81. Raw at (2, 0): `cv2.Sobel` (reflect-101) 0,
`scipy.ndimage.sobel` (reflect) 430.

σ = 2, 13 taps, constant 0 on a flat 40: edge column 24.0, one in 31.0, corner 14.4.

### Separability

[0 1 0; 1 −4 1; 0 1 0] = [0 1 0]ᵀ[1 −2 1] + [1 −2 1]ᵀ[0 1 0]. Costs: k² vs 2k vs 4k —
3: 9/6/12; 5: 25/10/20; 9: 81/18/36; 15: 225/30/60.

---

## Section budget

| # | Section | Target | Job |
|---|---|---|---|
| — | Insights + level + series line + jump + IMPORTANT | 280 | the answer: one free number per 3×3 derivative; criteria, not names |
| 1 | Why this matters | 220 | ×4 thresholds, (3,3) with σ = 2, the border column that reads 0 or 430 |
| 2 | The problem | 480 | constraints, budget, criterion; the family (FIG_01) |
| 3 | Worked example | 1,000 | the family on the patch (FIG_02); truncating σ = 2 (FIG_03); details block |
| 4 | Intuition | 480 | implicit smoothing rotates the gradient (FIG_04); map-projection analogy + break |
| 5 | Why is Scharr [3, 10, 3]? | 700 | matching curves (FIG_05), angular error (FIG_06), band weighting, bigger Sobel |
| 6 | What does "optimal" mean for a derivative? | 550 | Scharr, Farid–Simoncelli (FIG_07), Ando, Gaussian; the impulse pulls the other way |
| 7 | When does a kernel split into 1-D passes? | 420 | rank test, Laplacian = two terms, only the Gaussian is both (FIG_08) |
| 8 | How many taps does σ need? | 650 | truncation rules, OpenCV's σ = 0 table, sampled vs integrated vs discrete (FIG_09) |
| 9 | What does the border do to a derivative? | 600 | five modes on the patch (FIG_10), the odd-kernel rule, the naming clash |
| 10 | The math | 550 | family transfer function, angular error, F–S quotient, variance, border identity |
| 11 | Implementation: the tooling map | 450 | FIG_11 + tables + read-the-kernel-back snippet |
| 12 | Limitations and common mistakes | 350 | six named mistakes |
| 13 | Key takeaways | 120 | four claims |
| 14 | References | — | 18 sources |
| | **Total** | **≈ 6,850** | |

---

## Figure plan (route gate run per figure; the source check rejected all three paper figures)

| # | Section | One thing it must say | Route | Why | Draft caption |
|---|---|---|---|---|---|
| FIG_01 | Problem | every 3×3 derivative is one stencil with a value of p | placed | Q4 — named stencils placed at their true positions on a p axis, with real weights | Seven "different" derivative filters are one stencil with one free number |
| FIG_02 | Worked example | on the patch, every p gives 80 at the clean edge and 80 − 107.5(1 − 2p) beside the impulse | plot | Q4 — a line evaluated from the closed form with named points, beside the real window | At the clean edge the choice of p is invisible; beside the impulse it decides a 67% or 84% error |
| FIG_03 | Worked example | truncating σ = 2 to 3/5/7/13 taps: mass kept and variance left | plot | Q4 — sampled values and windows drawn to scale, with computed margins | Renormalising keeps the mass; the variance is what truncation takes |
| FIG_04 | Intuition | unequal smoothing of the two components rotates the gradient | plot | Q4 — vector geometry to scale with the computed components | The central difference shrinks each component by its own frequency; the vector turns 7.2° |
| FIG_05 | Scharr | cross-smoothing B_p against the difference's implicit smoothing S | plot | Q4 — transfer functions from closed form, crossings marked | Each p matches the difference's smoothing at one wavelength: 1/6 at DC, 3/16 at 3.45 px, 1/4 at 2 px |
| FIG_06 | Scharr | angular error against orientation at 4 px for the family and the 5-tap filters | plot | Q4 — closed-form error curves, a model not a measurement | Direction error at a 4-pixel wavelength: 7.2° central difference, 3.2° Sobel, 0.29° Scharr |
| FIG_07 | Optimal | matched pairs: D(ω) against ωP(ω) | plot | Q4 — four small multiples from the published taps | Farid–Simoncelli's criterion: the derivative filter must be the derivative of its own prefilter |
| FIG_08 | Separability | rank 1 splits into one pass pair, rank 2 into two | placed | Q4 — grids of real weights with their factors | A kernel separates exactly when every row is a multiple of one row |
| FIG_09 | Taps for σ | variance ratio vs σ for sampled, 3-tap, integrated, discrete, and OpenCV's tables | plot | Q4 — curves from closed forms with the shared kernel marked | Truncation, not sampling, is what shrinks the shared kernel's variance to 0.478 |
| FIG_10 | Border | row r2 extended five ways with the derivative at c0 and c4, plus the name map | placed | Q4 — a grid of real values per mode with outputs | Five border rules, five derivatives at the same pixel; one of them is always zero |
| FIG_11 | Tooling map | which call builds which kernel, at what scale, with which border | placed | Q5 — a comparison grid with no edges | The same kernel name means different weights, scales and borders in four libraries |

Social: 6 feed cards + 1 CTA, 4 Story frames. Cover: diagram-design template cover (placed),
built by `_cover.py` in the series house layout.

---

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| kernel / weights / stencil | Problem | the numbers of one weighted sum (series usage) | the object designed here | always |
| moment conditions | Problem | the sums a kernel must satisfy: Σw = 1 for a smoother; Σw = 0 and unit slope on a ramp for a derivative | they fix the scale and leave the shape free | normalising or comparing kernels |
| cross-smoothing | Problem | the smoothing a derivative applies perpendicular to its own axis, weights [p, 1 − 2p, p] | the one free number of every 3×3 derivative | choosing Sobel/Scharr/Prewitt |
| normalised vs raw kernel | Worked example | kernel scaled to slope 1 on a unit ramp vs the integer library form | libraries return raw, ×8 or ×32 | thresholds, switching operators |
| truncation | Worked example | cutting a kernel's infinite tails to a finite tap count | it removes mass, then variance after renormalising | every Gaussian |
| effective σ | Worked example | √(variance) of the kernel actually applied | what the blur really is | checking a ksize/σ pair |
| implicit smoothing | Intuition | the factor by which a difference under-reports a pattern's slope, sin ω / ω | why direction goes wrong | gradients on fine texture |
| rotation invariance / isotropy of a gradient | Intuition | the estimated direction does not depend on the pattern's orientation | the criterion Scharr optimises | orientation estimates |
| angular error | Scharr | estimated minus true gradient direction for a plane wave | the measure of isotropy | comparing derivative filters |
| weighting function | Scharr | how much each frequency counts in an optimisation | moves the optimum p | reading "optimal" claims |
| matched pair / prefilter | Optimal | a smoothing filter and a derivative filter where the second is the derivative of the first | Farid–Simoncelli's criterion | direction and consistency |
| Rayleigh quotient | Optimal | an error divided by an energy, minimised by an eigenvector | how F–S solve their design | reading the paper |
| steerable | Optimal | a filter whose rotated copy is a fixed combination of a few basis filters | why Gaussian derivatives rotate exactly | orientation analysis |
| rank / separable | Separability | a kernel is separable iff it is a column times a row, rank 1 | two 1-D passes | cost |
| sampled / integrated / discrete Gaussian | Taps for σ | three ways to put a Gaussian on a grid | differ in sum, variance, semigroup | σ below about 1 |
| discrete analogue of the Gaussian | Taps for σ | e^{−s} I_n(s), exact variance s | the discrete scale-space kernel | fine scales |
| border extension (constant, replicate, reflect, reflect-101, wrap) | Border | the rule inventing pixels beyond the edge | it is part of the kernel at the border | any filter near the edge |
| half-sample vs whole-sample symmetric | Border | reflection that repeats the edge pixel vs one that mirrors about it | names clash across libraries | porting code |
