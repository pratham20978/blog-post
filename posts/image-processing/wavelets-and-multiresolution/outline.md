# Outline — Wavelets and Multiresolution

**Title:** Wavelets and Multiresolution: Haar, Lifting, JPEG 2000 (54 chars; the plan's title plus
the three things the post works by hand, matching how Parts 3–5 were titled).
**Slug:** `wavelets-and-multiresolution`
**Series:** `image-processing`, part 6 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** advanced · **Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** 6,500 words planned (L3 range 5,000–7,500) · **Figures:** 11 (L3 range 8–12)
**Built 2026-10-11:** 7,491 words as the validator counts them (references included; the first
draft ran to 8,857 and was cut to the L3 ceiling by removing restatements, not sections), 11
figures, 8 feed + 4 Story cards; `validate_post.py` and `--social` PASS with 0 warnings.
**Assumes:** Part 5, *The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering* — its spectrum
of the patch, the impulse's flat floor of 215, the shift theorem, transfer functions — and Part 2's
pyramid section (*The Laplacian by Hand*) for the redundant version of the same idea. Both named
in plain text; Part 5 is not live yet, Part 2 is.
**Hands off:** nothing; it is a leaf. Compression codecs as codecs are out of scope (the entropy
coder is named, not taught).

Nothing is run against an image. Every number below is worked by hand on the shared patch, its rows
and its transpose, and cross-checked with plain Python using only `math` and `cmath`
(`worked.py`, `worked2.py`, `worked3.py` in the session scratchpad; not shipped). Curves are
evaluated from closed forms. Library behaviour carries a ledger key to source at a pinned commit.

**Checkpoints.** As with Parts 3–5 the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 27 sources, 22 peer-reviewed or standard with identifiers (floor 7; seven used for their
abstracts only and one for metadata only, and the ledger says so); scholarly databases OpenAlex,
Crossref, Google Scholar and arXiv answered, Semantic Scholar was queried and rate-limited (floor 4);
54 claims; 5 paper figures considered, none reusable (IEEE and Springer copyright). The normative
T.800 text was unreachable (ITU firewall); the 1999 committee draft is used for naming and
structure only, and every coefficient and rounding rule comes from Skodras et al. and OpenJPEG.
**B:** this file.

**Three findings change what the plan expected.**
1. *The row has five samples, so "one Haar level" is not defined until the odd sample is.* Lifting
   handles it for free — three coarse, two detail, five numbers — and that is exactly the budget
   point: JPEG 2000 keeps 5, PyWavelets' default returns 6 for Haar and 10 for `bior2.2`, the
   pyramid keeps 8 per level. The budget section is built on that.
2. *Neither filter is shift-invariant, and they fail on different features.* Move the step one
   pixel and Haar's level-1 detail goes 160 → 0, while the 5/3 keeps |80|. Move the impulse from an
   odd to an even column and Haar keeps 215, while the 5/3 splits it into two −107.5 (half the
   energy). One table, the patch's own rows.
3. *The 2-D Haar level is the cleanest bridge back to Part 5.* In the orthonormal scaling the
   impulse lands in four coefficients of 107.5, a quarter of its energy each (4 × 107.5² = 215²);
   Part 5's DFT put it in 25 bins of 215, 4% each.

---

## The spine

Fourier gives up position to get frequency. A wavelet transform asks a local question at every
scale: how far is this sample from what its neighbours predict? Smooth regions answer zero; edges
and impulses answer loudly; the coarse signal carries the rest to the next level, which asks again
at twice the spacing. Lifting computes it as split → predict → update, which keeps exactly N numbers
and, with rounding inside each step, inverts exactly in integers — the JPEG 2000 5/3 path. The costs
are shift variance (aliasing in the decimated bands), weak orientation, and border handling; the
remedies buy invariance back with redundancy.

## Verified numbers

**Row r0 = 40 40 40 200 200.** Haar by lifting (d = odd − even, s = even + d/2, the unpaired c4
copied): s = 40, 120, 200; d = 0, 160. 5/3 (JPEG 2000 rounding, whole-sample mirror): d = 0, 80;
s = 40, 60, 240 (the 240 is the low-pass (−1,2,6,2,−1)/8 on the mirrored 40 200 [200] 200 40).
Inverse returns the row exactly.

**Row r2 = 40 255 40 200 200.** Haar s = 147.5, 120, 200; d = 215, 160. 5/3 integer s = 148, 114,
240 (real 147.5, 113.75, 240); d = 215, 80. Inverse exact. Planted error (update undone without
the +2): 41, 256, 41, 200, 200.

**Shift.** Step at c1|c2 or c3|c4: Haar d = 0, 0 at level 1; 5/3 d = −80 (one coefficient). Impulse
of 255 on flat 40 at c1: both give 215; at c2: Haar −215, 5/3 −107.5, −107.5 with coarse −13.75,
201.25, −13.75.

**2-D orthonormal Haar on the patch** (PyWavelets default: half-sample mirror pads 5 → 6, 3×3
subbands, 36 coefficients). LL = 80 240 400 / 187.5 240 400 / 80 240 400. cH (JPEG 2000 LH) 107.5
at (1, 0). cV (HL) −160 down column 1, −107.5 at (1, 0). cD (HH) −107.5 at (1, 0). Impulse:
four coefficients of 107.5 = 215/2; energy 4 × 11,556.25 = 46,225 = 215². Transpose (E3): the
step moves to cH row 1 (−160 ×3); impulse at (0, 1): cH −107.5, cV +107.5, cD −107.5.

**Budgets.** Row of 5: lifting 5; pywt haar 6, bior2.2 10, bior4.4 14, periodization 6; pyramid one
level 8, all levels 11. Patch: lifting 25; pywt haar 36, bior2.2 100, bior4.4 196; pyramid 34 / 39.
1920×1080 at 5 levels: lifting 2,073,600; pywt haar +0.01%, bior2.2 +1.18%, bior4.4 +2.29%;
pyramid 2,764,200 (1.333). Three levels: 3 × 960×540 + 3 × 480×270 + 3 × 240×135 + 240×135 =
2,073,600; a 480×270 preview needs 129,600 coefficients, 1/16.

**Responses** (low DC gain 1, high Nyquist gain 2). Haar low |cos(ω/2)|: 0.707 at π/2, 0.5 at
2π/3. 5/3 low (3 + 2cos ω − cos 2ω)/4: 1.125 at π/3 (max), 1.0 at π/2, 0.625 at 2π/3. 9/7 low:
0.955, 0.813, 0.354. High-pass near ω = 0 rises as ω, ω², ω⁴ (ratio over an octave 2, 4, 16).
Ramp 10, 17, 24, …: Haar d = 7 everywhere, 5/3 d = 0.

**9/7 lifting check.** OpenJPEG's α…δ, low × 1/K, high × K reproduce Skodras' Table 3 taps to six
decimals.

**Thresholds.** √(2 ln N): 2.54 (N = 25), 4.995 (512²), 5.39 (1920×1080). σ = 10 on 512² → λ =
49.95. Expected pure-noise survivors 0.154 (512²). Patch at λ = 50: soft → rows 40 40 65 175 200,
r2 65 180 65 175 200, r3 65 65 65 175 200; hard unchanged. λ = 120: hard → impulse block 93.75 ×4,
step intact; soft → impulse block 93.75, step pair 100 / 140.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + IMPORTANT | 250 | — |
| Why this matters | 220 | — |
| The problem | 450 | — |
| Worked example: Haar on the row; 5/3 on the row; the budget | 1,000 | FIG_01, FIG_02 |
| Intuition: a local question at every scale; the tiling | 520 | FIG_03 |
| What does one level do to an image? | 650 | FIG_04, FIG_05 |
| Which wavelet: vanishing moments and the frequency response | 600 | FIG_06 |
| Lifting: how JPEG 2000 gets integers back (with JPEG vs JPEG 2000) | 650 | FIG_07 |
| What the decimated transform gets wrong | 600 | FIG_08, FIG_09 |
| Denoising by shrinking coefficients | 600 | FIG_10 |
| The math | 550 | — |
| Implementation: the tooling map | 400 | FIG_11 |
| Limitations and common mistakes | 300 | — |
| Key takeaways | 130 | — |
| Try it yourself (E1–E4) | 450 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | Haar and 5/3 on row r0: split, predict, update, every value; the step costs 160 vs 80 | placed | Q4 — a grid of real values, two lanes side by side |
| 02 | Worked example | coefficients kept: lifting = N; pywt pads; the pyramid adds 1/3 (2-D) | chart | Q1 — counts from the ledger's rules, compared across five representations |
| 03 | Intuition | how pixels, the DFT, fixed blocks and wavelets tile position × frequency for 8 samples | placed | Q4 — geometry: tile widths and heights to scale |
| 04 | One level in 2-D | the patch's four subbands, every value; the impulse in four coefficients (25% each) against the DFT's 25 bins (4% each) | placed | Q4 — grids of real values |
| 05 | One level in 2-D | three levels of a 1920×1080 frame drawn to scale; what each LL decodes to | placed | Q4 — proportional areas |
| 06 | Which wavelet | low- and high-pass responses of Haar, 5/3, 9/7 from closed forms | plot | math curves |
| 07 | Lifting | r2 through the integer 5/3, forward and inverse, rounded values on every edge | placed | Q5 — 6 nodes per lane, no crossings, a number on every edge |
| 08 | Shift variance | step and impulse at two alignments: Haar and 5/3 level-1 details | placed | Q4 — small multiples of real values |
| 09 | Shift variance | coefficients per pixel (2-D) bought for invariance: DWT 1, pyramid 4/3, dual tree 4, undecimated 3J + 1 | chart | Q1 — counts from the ledger |
| 10 | Denoising | hard and soft threshold curves with the patch's coefficients marked, and the patch after each at λ = 50 and 120 | plot | curve plus value grids |
| 11 | Implementation | PyWavelets, scikit-image, Pillow/OpenJPEG calls: scaling, size rule, default, trap | placed | Q4 — a dense table-figure, the series' closing tooling map |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| wavelet / wavelet transform | Problem | a short oscillation at one scale and position; the transform's basis | localises frequency content | when structure is local |
| multiresolution analysis | Problem / Math | Mallat's nested approximations, each half the resolution | gives the recursive algorithm | reading any DWT |
| Haar wavelet | Worked example | the two-sample average/difference wavelet | simplest; the oldest orthonormal basis | teaching, piecewise-constant data, denoising default |
| lifting: split, predict, update | Worked example | the three-step in-place factorisation | integer, in place, half the arithmetic | implementing or inverting a DWT |
| detail / coarse (approximation) coefficients | Worked example | the prediction errors / the half-resolution signal | what thresholds and codecs act on | always |
| 5/3 (LeGall) and 9/7 (CDF) | Worked example | JPEG 2000's two filter pairs | reversible vs lossy coding | choosing a JPEG 2000 path |
| whole- vs half-sample symmetric extension | Worked example | mirror about the end sample vs repeat it | decides the border values and the count | odd sizes, borders |
| critically sampled / redundancy | Worked example | N in, N out vs more | storage and shift-invariance trade | choosing a transform |
| subbands LL, HL, LH, HH | One level | the four outputs of a 2-D level, named by filtering direction | where edges of each orientation land | reading coefficients, mapping to pywt |
| vanishing moments | Which wavelet | polynomial degrees the high-pass kills | sparsity on smooth regions | choosing a wavelet |
| orthonormal vs biorthogonal | Which wavelet | same vs different analysis and synthesis filters | symmetry vs energy preservation | thresholding, quantising |
| reversible / irreversible transform | Lifting | integer-exact vs floating point | lossless vs lossy | JPEG 2000 settings |
| shift variance / aliasing | Shift | coefficients change under a shift | registration, features, artefacts | before relying on coefficients |
| undecimated (stationary), dual-tree complex | Shift | redundant transforms with near shift invariance | the remedies | when invariance matters |
| soft / hard thresholding; universal threshold; VisuShrink; BayesShrink; MAD | Denoising | the shrink rules and how λ and σ are chosen | denoising | tuning a denoiser |

## Not repeated from earlier parts

The four-stage frame (one sentence at most), Part 5's spectrum and swap (only the 215 floor is
quoted), Part 2's REDUCE/EXPAND construction (named, 4/3 quoted), correlation vs convolution.
