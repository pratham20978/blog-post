# Outline — Resampling and Aliasing

**Title:** Resampling and Aliasing: Interpolation Kernels in Practice (58 chars)
**Slug:** `resampling-and-aliasing`
**Series:** `image-processing`, part 3 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** advanced
**Budget:** 6,300 words (L3 range 5,000–7,500) · **Figures:** 10 (L3 range 8–12)
**Parent:** `image-processing-by-hand` (https://canery.in/blogs/image-processing-by-hand) —
assumes its sampling stage, anchor `#stage-1--sample-the-grid-is-already-lossy`, and its
Figure 5 (spectral replication). Does not re-teach Nyquist or replication.
**Hands off:** kernel *design* to Part 4 (*Kernel Design: Separability, Borders, and Optimised
Derivative Filters*); resizing in the frequency domain to Part 5 (*The 2-D DFT: Spectra, Phase,
and Frequency-Domain Filtering*); resizing in gamma-encoded sRGB to Part 13 (*Colour and
Gamma*). All three named by title only — none is published, so none is linked.

Nothing is run against an image. Every number below is worked by hand on row r2 of the
shared patch and cross-checked with plain-Python arithmetic (no packages); curves are
evaluated from the kernels' closed forms and captioned as such; library behaviour carries a
ledger key to docs or to source at a pinned commit.

**Checkpoints.** The session could not pause for replies, so Checkpoints A and B ran without
a stop, and what each would have shown is recorded here. **A:** 15 sources, 7 of them
peer-reviewed with identifiers (floor 7), 5 databases in the log (floor 4), 42 claims, 4 paper
figures considered and rejected for unverified rights. **B:** this file.

---

## The spine

A resize makes two decisions, and every library bundles them into one flag:

```
reconstruct  (which kernel fills in between samples)   → matters when ENLARGING
prefilter    (what is removed before the new grid)     → matters when SHRINKING
```

The post's one claim: **when enlarging, only the kernel matters; when shrinking, the kernel
must also widen by 1/s, and a fixed-width interpolator cannot.** Heckbert's two limiting
cases (L19, L20) are that claim in primary form. Mitchell–Netravali's postaliasing and
prealiasing (L10) are its two failure modes.

The worked example proves it on five integers, with one new tool the reader can use on any
resize: **the resampling matrix**. Its rows must sum to 1 (a flat image stays flat — every
kernel here does that, L13). Its **columns** must all sum to s (every input pixel counts
equally), and only a prefiltered resize does that. A column-sum ripple shows which input
frequencies alias onto the output's mean. It is aliasing you can check with a pencil.

---

## The row (from the parent)

```
r2:   c0   c1   c2   c3   c4
      40  255   40  200  200       mean 147; impulse at c1, step between c2 and c3
```

Clean row for the step alone: `40 40 40 200 200`.

Coordinate convention (half-pixel centres, OpenCV linear/cubic/Lanczos, Pillow, skimage —
L33): output j sits at x = (j + 0.5)/s − 0.5 in input pixels.

| Resize | s | Output positions x_j | Exact |
|---|---|---|---|
| shrink | 0.6 (3 outputs) | 0.333, 2.000, 3.667 | 1/3, 2, 11/3 |
| enlarge | 1.7 (8 outputs) | −0.206, 0.382, 0.971, 1.559, 2.147, 2.735, 3.324, 3.912 | (20j − 7)/34 |

---

## Verified numbers (plain-Python cross-check, `worked.py` in the session scratchpad)

### Shrink to 0.6×

| Method | Outputs | Mean | Column sums c0..c4 |
|---|---|---|---|
| OpenCV `INTER_NEAREST` (index floor(j/s) → c0, c1, c3) | 40, **255**, 200 | 165.0 | 1, 1, 0, 1, 0 |
| nearest, pixel centres (→ c0, c2, c4) | 40, **40**, 200 | 93.3 | 1, 0, 1, 0, 1 |
| linear (2 taps) | 111.67, 40, 200 | 117.2 | 0.667, 0.333, 1, 0.333, 0.667 |
| Keys a = −1/2 (4 taps) | 111.67, 40, 205.93 | 119.2 | 0.704, 0.333, 0.926, 0.333, 0.704 |
| Lanczos-3 (6 taps, normalised) | 124.25, 40, 215.70 | 126.6 | 0.699, 0.395, 0.813, 0.395, 0.699 |
| **area** (box prefilter, `INTER_AREA`) | **126, 115, 200** | **147.0** | **0.6, 0.6, 0.6, 0.6, 0.6** |
| stretched linear (Pillow BILINEAR) | 132.14, 123.33, 200 | 151.8 | 0.571, 0.651, 0.556, 0.651, 0.571 |
| stretched Keys (Pillow BICUBIC) | 131.00, 126.49, 198.31 | 151.9 | 0.547, 0.662, 0.581, 0.662, 0.547 |
| stretched Lanczos-3 (Pillow LANCZOS) | 131.48, 132.58, 193.31 | 152.5 | 0.537, 0.671, 0.585, 0.671, 0.537 |

Input mean **147**. Only area reproduces it exactly; the stretched kernels land within 3.7%
(their residual comes from dropping-and-renormalising at the borders of a five-pixel row).

Hand-checkable taps:
- linear j0 (x = 1/3): 2/3 · 40 + 1/3 · 255 = 26.67 + 85 = **111.67**.
- Keys j0, taps c−1..c2 at distances 4/3, 1/3, 2/3, 5/3: **−2/27, 7/9, 1/3, −1/27** (sum 1).
  40·(−2/27 + 7/9 − 1/27) + 255·1/3 = 26.67 + 85 = **111.67** — identical to linear, because
  Keys' weight at distance 2/3 happens to equal the triangle's (1/3).
- Keys j2 (x = 11/3), taps c2..c5→c4: −1/27, 1/3, 7/9, −2/27 → −1.48 + 66.67 + 155.56 − 14.81 =
  **205.93**. The negative lobe reaches back to the dark c2 and pushes the bright side up.
- area j0 covers [0, 5/3): c0 whole, c1 two-thirds → (40 + 170)·3/5 = **126**; j1 covers
  [5/3, 10/3): (85 + 40 + 66.67)·3/5 = **115**; j2 = **200**. Weights 0.6/0.4, 0.2/0.6/0.2,
  0.4/0.6.
- stretched linear j1 (x = 2, tent half-width 5/3): taps c1, c2, c3 at 0.4, 1, 0.4 → /1.8 →
  0.222, 0.556, 0.222 → **123.33**. Unstretched: c2 only → 40.

Impulse moved from c1 to c2 (read off the column sums): centred nearest 0 → 1; OpenCV nearest
1 → 0; linear 0.333 → 1; area **0.6 → 0.6**.

### Enlarge to 1.7×

| Method | j0 | j1 | j2 | j3 | j4 | j5 | j6 | j7 |
|---|---|---|---|---|---|---|---|---|
| nearest | 40 | 40 | 255 | 40 | 40 | 200 | 200 | 200 |
| linear | 40.0 | 122.2 | 248.7 | 134.9 | 63.5 | 157.6 | 200.0 | 200.0 |
| Keys a = −1/2 | **26.0** | 125.9 | 254.5 | 132.4 | 44.9 | 159.4 | **211.8** | 200.6 |
| Keys a = −3/4 (OpenCV) | 19.1 | 133.8 | 254.6 | 134.3 | 42.7 | 153.0 | 217.8 | 200.9 |
| Lanczos-3 | **14.1** | 139.3 | **255.6** | 135.6 | 37.1 | 148.3 | **225.0** | 203.4 |

Clean row: Keys −1/2 → 40, 40, 40, **29.0**, 56.4, 165.0, **211.8**, 200.6; Lanczos-3 → 40,
42.6, 40.9, **21.4**, 57.8, 163.9, **218.3**, 203.2.

- Nearest repeats c0 and c2 twice and c1 once: 1.7 is not an integer, so block widths are uneven.
- Linear never leaves the input range (every output is a convex combination).
- Keys and Lanczos go below 40 and above 200; Lanczos-3 passes 255 at j2 → clipped in 8-bit.

### Kernel facts (closed form, Simpson's rule on the definition)

| Kernel | Taps | H(0.25) | H(0.4) | H(0.5) | H(0.75) | Step overshoot |
|---|---|---|---|---|---|---|
| nearest (box) | 1 | 0.900 | 0.757 | 0.637 | 0.300 | 0 |
| linear (triangle) | 2 | 0.811 | 0.573 | 0.405 | 0.090 | 0 |
| Keys a = −1/2 | 4 | 0.939 | 0.716 | 0.493 | 0.063 | **2/27 = 7.41%** |
| Keys a = −3/4 | 4 | 0.986 | 0.753 | 0.493 | 0.012 | 1/9 = 11.1% |
| Lanczos-3 | 6 | 1.008 | 0.821 | 0.500 | −0.009 | 11.8% |
| ideal (sinc) | ∞ | 1 | 1 | ½ | 0 | ≈ 9% (Gibbs) — not used |

- Keys overshoot is exactly −4a/27 of the step height, peaking one third of a pixel past the
  first bright sample: at a = −1/2, S(1/3) = 7/9 + 1/3 − 1/27 = 29/27.
- At 0.6×, the new Nyquist is 0.3 cycles/input px. A pattern at 0.4 (period 2.5 px) passes
  linear at 57%, area (box 5/3 wide) at 41%, stretched triangle at 17%, and aliases to
  0.2 cycles/input px — a period-5 moiré.
- Lanczos-3 un-normalised taps sum to 0.994 at half-pixel phase; both libraries divide by the
  sum (L30, L40).
- a = −3/4 makes the second derivative continuous at x = 1: 4a + 6 = −4a.

### B–C family (Mitchell–Netravali eq. 8)

| Member | (B, C) | Interpolates? k(0), k(1) | Overshoot | H(0.25) |
|---|---|---|---|---|
| cubic B-spline | (1, 0) | no — 2/3, 1/6 | 0% | 0.657 |
| Mitchell | (1/3, 1/3) | no — 0.889, 0.056 | 3.6% | 0.845 |
| Catmull–Rom = Keys −1/2 (Pillow) | (0, 1/2) | yes | 7.4% | 0.939 |
| Keys −3/4 (OpenCV) | (0, 3/4) | yes | 11.1% | 0.986 |
| Rifman −1 | (0, 1) | yes | 14.8% | 1.032 |

Keys(a) ≡ (B, C) = (0, −a), checked on a grid to 1e-12.

### Cost (taps per output per axis)

| s | linear | Keys | Lanczos-3 |
|---|---|---|---|
| ≥ 1 (fixed) | 2 | 4 | 6 |
| 0.6 stretched | 3.3 | 6.7 | 10 |
| 0.25 stretched | 8 | 16 | 24 |
| 0.1 stretched | 20 | 40 | 60 |

---

## Section budget

| # | Section | Target | Job |
|---|---|---|---|
| — | Insights + level + series line + jump + IMPORTANT | 260 | the answer: fixed-width kernels alias on shrink; the prefilter widens by 1/s |
| 1 | Why this matters | 220 | the thumbnail with moiré, and the threshold that moves when resolution changes |
| 2 | The problem | 480 | a resize evaluates a function the samples do not define; two decisions; where the new samples sit (FIG_01) |
| 3 | Worked example | 1,050 | r2 at 0.6× (FIG_02) and at 1.7× (FIG_03); every tap in a `<details>` |
| 4 | Intuition | 520 | reconstruct → prefilter → sample; enlarge vs shrink on the frequency axis (FIG_04); analogy + break |
| 5 | What does each kernel do to the spectrum? | 650 | kernels (FIG_05), transfer functions (FIG_06); blur vs leakage vs ringing |
| 6 | Why is "bicubic" not one kernel? | 600 | Keys' a, its history, the B–C plane (FIG_07); OpenCV −3/4 vs Pillow −1/2 |
| 7 | Why does a shrink need a prefilter and an enlarge not? | 750 | resampling matrix, column sums (FIG_08), the stretched kernel (FIG_09) |
| 8 | What does the choice cost? | 330 | taps, separability, the cost of stretching, pyramids and `reducing_gap` |
| 9 | The math | 560 | reconstruction sum; Keys and order 3; stretched kernel; column-sum identity; back to 0.6 |
| 10 | Implementation: the tooling map | 480 | FIG_10 + three tables |
| 11 | Limitations and common mistakes | 330 | five named mistakes |
| 12 | Key takeaways | 120 | four claims |
| 13 | References | — | 15 sources |
| | **Total** | **≈ 6,350** | |

---

## Figure plan (route gate run per figure; the source check rejected all four paper figures)

| # | Section | One thing it must say | Route | Why | Draft caption |
|---|---|---|---|---|---|
| FIG_01 | The problem | the same "0.6× nearest" reads different pixels under three coordinate conventions | placed | Q4 — sample positions drawn to scale over the pixel cells | Half-pixel centres, OpenCV's floor index and SciPy's corner-aligned grid put the three new samples at different places, so they read different pixels |
| FIG_02 | Worked example | each kernel's taps under each of the three shrink outputs, and the values they produce | plot | Q4 — kernel curves evaluated at real positions over the row | At 0.6× every kernel reads a narrow window around its sample point; the impulse enters with weight 0, 1/3, 1/3, 0.38 — or not at all |
| FIG_03 | Worked example | the continuous reconstructions at 1.7× and the eight samples taken from them | plot | Q4 — curves from the closed-form kernels, with the 8-bit clip lines | Enlarging is only reconstruction: nearest blocks unevenly, linear stays in range, Keys and Lanczos ring below 40 and above 200 |
| FIG_04 | Intuition | enlarging keeps every input frequency; shrinking must remove [0.3, 0.5] cycles/px first | placed | Q5 — six stages in two rows, no crossings, bandwidth on every edge | Reconstruct, (prefilter), sample: at 1.7× the new Nyquist is above the old one, at 0.6× it is below it |
| FIG_05 | Spectrum | the five kernels as shapes, with support and taps | plot | Q4 — functions of x, from definitions | Four kernels and the sinc they approximate: support grows 1 → 2 → 4 → 6 taps, negative lobes appear at 4 |
| FIG_06 | Spectrum | passband droop and stopband leakage per kernel, with both Nyquists marked | plot | Q4 — transfer functions evaluated from the definitions | Each kernel's transfer function against the ideal box: what it blurs below 0.5 and lets through above it |
| FIG_07 | Bicubic | the named cubics as points on one plane, with their overshoot and blur | plot | Q4 — a 2-D parameter plane with computed values | "Bicubic" is a point on a plane: OpenCV and Pillow sit on the interpolating axis at different heights |
| FIG_08 | Prefilter | the 3×5 resampling matrices and their column sums | placed | Q4 — a grid of real weights with row and column margins | Every row sums to 1; only the area matrix gives every input pixel the same total weight, 0.6 |
| FIG_09 | Prefilter | the triangle before and after stretching by 1/0.6, in space and in frequency | plot | Q4 — kernel and transfer function at two widths, evaluated | Widening the kernel by 1/s moves its cutoff from the old Nyquist to the new one — that is the prefilter |
| FIG_10 | Tooling map | which call does which kernel, with what a, with or without a prefilter | placed | Q5 — a 5×5 comparison grid, no edges | The same three words mean different arithmetic in four libraries |

Social: 6 feed cards, 4 Story frames (cover, impulse, bicubic family, CTA). Cover is a
diagram-design template cover (placed), built by `_cover.py` in the series house layout.

---

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| resampling | The problem | evaluating an image at a new set of positions | every resize, rotation and warp is one | whenever the output grid differs from the input grid |
| scale factor s | The problem | output samples per input sample (0.6 shrinks, 1.7 enlarges) | sets the new grid spacing 1/s | every resize |
| reconstruction kernel h | The problem | the function that fills in between samples, f̂(x) = Σ f[k] h(x − k) | the samples alone define nothing between them | choosing an interpolation flag |
| interpolating kernel | The problem | h(0) = 1, h(n) = 0 at other integers — passes through the samples | the Keys family does, B-spline and Mitchell do not | when outputs landing on input positions must return input values |
| half-pixel centres | The problem | output j at (j + 0.5)/s − 0.5 | the convention most libraries use for linear/cubic | comparing libraries, or porting code |
| tap / support | Worked example | the input samples a kernel reads for one output / the width over which it is nonzero | cost and reach | cost estimates, border handling |
| prefilter | Intuition | low-pass applied before the new grid samples | removes what the coarser grid cannot represent | shrinking |
| prealiasing / postaliasing | Intuition | aliasing from a missing prefilter / from a poor reconstruction kernel | names the two failure modes | diagnosing moiré vs jaggies |
| transfer function H(ν) | Spectrum | the kernel's Fourier transform; the gain at frequency ν | Part 1 established it decides behaviour | comparing kernels |
| passband droop / leakage | Spectrum | H < 1 below Nyquist (blur) / H ≠ 0 above it (replicas pass) | the two ways a kernel falls short of the ideal | choosing sharpness vs artefacts |
| ringing / overshoot | Spectrum | output beyond the input's range beside an edge | caused by negative lobes | edges, 8-bit clipping |
| approximation order | Bicubic | error falls as h^L; reproduces polynomials of degree L − 1 | what "third-order accurate" means | reading Keys |
| B–C family | Bicubic | Mitchell–Netravali's two-parameter cubics | shows every "bicubic" as one point | comparing library cubics |
| resampling matrix | Prefilter | W[j][i] = weight of input i in output j | makes a resize checkable by hand | auditing a resize |
| partition of unity | Prefilter | shifted kernels sum to 1 — rows of W sum to 1 | flat stays flat | every kernel here |
| column sum | Prefilter | total weight input i receives | uniform = no aliasing onto the mean | shrinking |
| stretched kernel | Prefilter | h_s(x) = s·h(s·x), support 1/s times wider | the prefilter built into the kernel | Pillow, MATLAB-style resizes |
| area averaging | Prefilter | box prefilter of width 1/s, weights = overlap | `INTER_AREA` | shrinking in OpenCV |
