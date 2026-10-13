# Outline — Scale Space and SIFT

**Title:** Scale Space and SIFT: Why σ Is a Search Dimension (50 chars; the plan's title and the name
Part 1 published for this spoke).
**Slug:** `scale-space-and-sift`
**Series:** `image-processing`, part 10 · **Tier:** L4 pillar · **Category:** algorithms ·
**Difficulty:** advanced (Gaussian blur as convolution, the scale-normalised Laplacian from Part 2, a
second-order Taylor expansion, a 3×3 linear solve) · **Lab grade:** G0 — by hand, the series
invariant (no `lab/`)
**Budget:** about 9,000 words as the validator counts them (L4 range 7,500–10,000, references
included; prose about 7,900) · **Figures:** 13 (L4 range 12–18; the plan estimated 13)
**Assumes:** Part 2, *The Laplacian by Hand* — the scale-normalised Laplacian σ²∇²(G ∗ f), its peak
at σ = r/√2 for a disc and σ = w/2 for a bar, the DoG approximation, the 26-neighbour cube (its
Figure 13) and Mikolajczyk–Schmid's evidence for the Laplacian as a scale selector; Part 1, *Image
Processing by Hand* — σ drawn as an axis (its Figure 15); Part 3, *Resampling and Aliasing* — output
pixel j of a resize sits at x = (j + 0.5)/s − 0.5, which is the whole of OpenCV's quarter-pixel bias;
Part 9, *The Structure Tensor* — the scale-adapted tensor and Harris maxima per level (Harris–Laplace's
position half). Parts 1–2 live; 3 and 9 built, not live. All named in plain text.
**Hands off:** learned descriptors and detectors — out of scope, not deferred. Affine adaptation
(Harris-Affine) is named, not taught.

Nothing is run against an image. The ×7 patch is a sum of rectangles and the Gaussian blur of a
rectangle has a closed form (products of normal-CDF differences), so every scale-space value is
evaluated from that closed form at pixel centres. Plain Python (`math` only) in the session
scratchpad, not shipped: `octave.py` (closed-form octave, extrema), `fit.py` (quadratic fit, both
tests), `discrete.py` (sampled-kernel pyramid, two borders, direct and incremental blurs),
`sift_sim.py` (OpenCV's detection rules transcribed from `sift.dispatch.cpp`/`sift.simd.hpp` at
802cf95), `numbers.py` (curves, covariance, fixed-σ maps), `harris_laplace.py`.

**Checkpoints.** As with Parts 3–9, the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 30 sources in the ledger: 24 peer-reviewed with an identifier (floor 10), 7 of them used for
their abstracts only (Babaud 1986, Yuille & Poggio 1986, Lindeberg 1990, Pauwels 1995, Kannappan &
Sahoo 1992, Mikolajczyk & Schmid 2001, Kuijper 2002) and 2 not read at all and attributed only
through sources that were (Koenderink 1984, Weickert et al. 1999); 4 primary-source and 2
documentation entries for OpenCV, scikit-image, SciPy and MATLAB. Databases that answered: OpenAlex,
Crossref, Semantic Scholar, Google Scholar (arXiv's API rate-limited; its PDFs served). Blocked:
KTH's DiVA (no response; Lindeberg's KTH page carried the two 1998 papers as reports), Springer
(bot wall for Lindeberg's 2012 and 2015 JMIV papers), UNC's repository (Damon 1995), Utrecht's DSpace
(a JavaScript shell), Surrey's copy of Mikolajczyk et al. 2005. No paper figure reused: Lowe's are ©
Kluwer, IPOL's are CC BY-NC-SA, Witkin's carry no licence, and Lindeberg's PLoS figure (CC BY) is
337×172 pixels and says what one sentence says.
**B:** this file.

**Eight findings change what the plan expected.**
1. *The enlargement factor decides which octave sees the blob.* ×5 puts the impulse-square's DoG peak
   below the octave's first searchable level (σ 1.99 for the LoG, about 1.77 for the DoG), so only
   the doubled octave finds it; ×7 puts it on the middle level (σ 2.54). The post uses ×7 and says why.
2. *One octave yields exactly two candidates.* (10, 17) at level 2, D = −35.38, the square (kept), and
   (17, 17) at level 2, D = +14.74, between the square and the step (rejected by the edge test alone:
   Tr²/Det 23.2 against 12.1, after passing contrast at 0.059). The step itself gives no 3-D extremum.
3. *A fixed σ turns the ×14 square into four corners.* At the DoG level that finds the ×7 square
   (σ 2.54–3.2), the ×14 patch has minima of −20.43 at its four inner corners and only −9.66 at the
   centre. Searched, the square comes back at twice the σ.
4. *A square's characteristic scale is its equal-area disc's.* The normalised LoG at a square's centre
   peaks at σ = 0.3983 × side (u* = 1.2554), 0.17% below side/√(2π); the peak height, 0.7203 × contrast
   (154.9 at 215), is the same at every size.
5. *The DoG selects about √k below the LoG.* Continuous DoG maximum at σ 2.480 against the LoG's
   2.776 (ratio 1.119, √k = 1.122). Exactly, a DoG level is the normalised Laplacian averaged over one
   log-σ interval times ln k = 0.231; Lowe's k − 1 = 0.260 and Lindeberg's (k² − 1)/2 = 0.294 are
   first-order versions of it.
6. *OpenCV's default reports the square a quarter pixel off.* `enable_precise_upscale` defaults to
   false (PR #23270, "temporarily", 2023), so the doubling's half-pixel mapping (Part 3's j ↔ (j+0.5)/s
   − 0.5) shifts every keypoint by +0.25 px: predicted (10.23, 17.25) by default, (9.98, 17.00) with the
   flag. scikit-image's SIFT, by its code, should show the same offset (zoom with grid_mode=True).
7. *Uniqueness of the Gaussian depends on which axioms you keep.* The Poisson kernel passes linearity,
   shift invariance, the semigroup, scale and rotation invariance and positivity; it fails separability
   and strict causality (non-enhancement), and passes a relaxed causality. In 2-D the Gaussian itself
   can create extremum–saddle pairs; only non-enhancement is guaranteed.
8. *Harris–Laplace on the patch returns the same single point.* Levels 1.4^n, σD = 0.7σI: Harris has
   four corner maxima at σI = 1.96, all rejected by the Laplacian (−83.2 at 1.96 against −89.1 and
   −86.9); at 2.744 its only maximum is (10, 17), whose LoG (−154.6) beats 1.96 (−115.2) and 3.84
   (−127.5).

---

## The spine

A structure has no size until something measures it, and a detector that fixes σ measures every
structure against one size: what it reports depends on the zoom. Searching σ as a third coordinate,
for extrema of a scale-normalised operator, returns each structure at a σ proportional to its own
size, so the answer moves with the zoom instead of changing. SIFT does that search with differences
of Gaussians on a pyramid. The kernel doing it must not invent structure as σ grows, must let each
level be built from the last, and must be cheap; the Gaussian is the only kernel with all three
(non-enhancement, the semigroup, separability), and which of them you call an axiom decides whether
it is "the only" one at all. The patch shows each step: one octave, two candidates, one kept.

## Verified numbers

**×7 patch:** 35×35; square 255 at columns 7–13, rows 14–20 (centre (10, 17)); step at x = 20.5;
closed form L = 40 + 160Φ((x − 20.5)/σ) + 215[Φ((x − 6.5)/σ) − Φ((x − 13.5)/σ)][Φ((y − 13.5)/σ) −
Φ((y − 20.5)/σ)]. Octave σ: 1.600, 2.016, 2.540, 3.200, 4.032, 5.080.
**D at (10, 17), levels 0–4:** −21.855, −32.216, −35.379, −31.417, −23.124.
**26-block at (10, 17), level 2 (rows y = 16, 17, 18; columns x = 9, 10, 11):** level 1: −29.038
−30.586 −29.024 / −30.589 −32.216 −30.575 / same as row 1; level 2: −31.126 −33.169 −30.927 / −33.223
−35.379 −33.024 / row 1; level 3: −28.432 −29.723 −27.516 / −30.056 −31.417 −29.140 / row 1.
**Fit at (10, 17):** g = (0.0995, 0, 0.3993); H = [[4.5102, 0, 0.2256], [0, 4.4198, 0], [0.2256, 0,
7.1241]]; offset (−0.0193, 0, −0.0554); D(x̂) = −35.391 → 0.1388 (0–1 scale; ×3 = 0.416); σ 2.5075;
size 5.015; edge: Dxx 4.5102, Dyy 4.4198 → Tr²/Det 4.0004, ratio 1.0205.
**(17, 17), level 2:** D = 14.740; g = (1.5363, 0, −0.6512); H = [[−3.8037, 0, 0.6888], [0, −0.1801,
0], [0.6888, 0, −3.2821]]; offset (0.3825, 0, −0.1181); D(x̂) = 15.073 → 0.0591; edge Tr²/Det 23.168,
eigenvalue ratio 21.12 (t = 0.0473).
**Cross-checks:** discrete direct (replicate or reflect-101): blob −35.756, gap 14.909, gap ratio
22.09; incremental with σin = 0.5: −36.918, 15.427, 19.39; OpenCV replay default: (10, 17) −35.779,
gap at (18, 17) 15.074 ratio 15.32, third candidate (17, 12) at level 3 dropped in interpolation;
precise: −36.336, gap (17, 17) 15.167 ratio 20.66.
**OpenCV replay keypoints (×7):** default pt (10.2312, 17.2488), size 5.0208, response 0.14135,
angles 0.28° and 90.18° (third peak 0.789 of max: fragile); precise pt (9.9824, 17.0000), size
5.0294, response 0.14252, angles 0.00°, 90.57°, 269.43° (180° bin at 0.665). Octaves 70, 35, 17, 8, 4;
incremental σ 1.2263, 1.5450, 1.9466, 2.4525, 3.0900; first blur 1.2490. The 5×5 patch: no keypoints
(doubled to 10×10, 5-pixel border).
**Normalised LoG at a square's centre:** −4A·uφ(u)(2Φ(u) − 1), u = side/(2σ); u* = 1.255424; σ* =
0.398272 side (disc of equal area 0.398942; ratio 0.99832); peak 0.720303 A = 154.87 at A = 215. Sides
3, 5, 7, 9, 14 → σ* 1.195, 1.991, 2.788, 3.584, 5.576. On the full ×7 patch: σ* 2.776, N −154.671; N at
the octave levels −66.6, −121.1, −152.1, −148.8, −120.0, −79.4.
**DoG vs LoG:** continuous DoG max σ 2.4804, D −35.418; ratio 1.1192; √k 1.1225; k − 1 0.2599; (k² −
1)/2 0.2937; ln k 0.2310; peak D / peak N 0.229.
**Step:** σ²Lxx on its ridge 160φ(1) = 38.72 at every σ; σLx at the edge 160φ(0) = 63.83 at every σ.
**Fixed level σ 2.540–3.200:** ×7 strict extrema (3, 17) +6.27, (10, 17) −35.38, (17, 17) +14.74; ×14:
minima −20.431 at (17, 31), (24, 31), (17, 38), (24, 38); maxima +10.601 at (21, 24), (21, 45); centre
(20.5, 34.5) −9.658.
**Harris–Laplace (levels 1.4^n, σD = 0.7σI, Gaussian window):** σI 1.96: maxima (8, 15), (12, 15), (8,
19), (12, 19); σI 2.744 and 3.842: only (10, 17). LoG at (10, 17): 1.4 −37.2, 1.96 −115.2, 2.744 −154.6,
3.842 −127.5, 5.378 −69.1. At (8, 15): 1.4 −89.1, 1.96 −83.2, 2.744 −86.9, 3.842 −85.4.
**Edge test:** r/(r + 1)² = 10/121 = 0.08264 ⟺ t > 0.1; Harris boundaries 0.0436 (k 0.04), 0.0685 (0.06).
**Contrast in grey levels:** Lowe 0.03 → 7.65; OpenCV 0.04/3 → 3.40; IPOL 0.015 → 3.83; pre-test 1.
**Descriptor:** cell 3σ = 7.5 px, window 30 px at σ 2.51; radius round(10.61σ) = 27.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + jump + IMPORTANT | 330 | — |
| Why this matters | 180 | — |
| The problem | 420 | — |
| Worked example: the ×7 patch; the octave; the 26-neighbour test; the fit; the second candidate; scorecard | 1,500 | FIG_01, FIG_02, FIG_03, FIG_04 |
| Intuition: σ as a ruler | 350 | FIG_05 |
| Why must scale be searched rather than set? (fixed σ fails; covariance; the step has no scale; Harris–Laplace's scale half) | 950 | FIG_06, FIG_07 |
| Why is the Gaussian the only kernel allowed to search? (what the search needs; the derivations; the Poisson counterexample; 2-D; what SIFT needs) | 950 | FIG_08 |
| How does SIFT sample σ? (octaves and intervals; 3 and 1.6, contested; the DoG constant and its √k) | 850 | FIG_09, FIG_10 |
| Refine, then reject (fit; contrast in three units; the edge test is Harris's ratio test) | 600 | FIG_11 |
| What is the scale for? (orientation; descriptor) | 450 | FIG_12 |
| The math | 500 | — |
| Implementation: the tooling map | 700 | FIG_13 |
| Limitations and common mistakes | 420 | — |
| Key takeaways | 150 | — |
| Try it yourself (E1–E5) | 650 | — |

## Figure plan (route gate run per figure)

Source check for every paper-backed section: Lowe's Figures 1–2 (pyramid, 26-neighbour cube) carry no
reuse licence; Witkin's Figure 2 none; IPOL's octave figures are CC BY-NC-SA; Lindeberg's PLoS
Figure 1 is CC BY but 337×172 and replaceable by one sentence. So every figure is our own analysis on
the patch, none a redraw.

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | the ×7 patch's octave: six Gaussian images and five DoGs, the two candidates marked | placed | Q4 — small multiples of real values as shaded grids |
| 02 | Worked example | the 27 values around (10, 17): the centre is the lowest | placed | Q4 — a grid of real numbers |
| 03 | Worked example | the fit along scale: five DoG samples, the parabola through three, its vertex at −0.055 layer | plot | closed-form samples and a fitted curve |
| 04 | Worked example | the two candidates as surfaces: a round bowl (ratio 1.02) and a ridge (21.1) | plot | closed-form contours around real points |
| 05 | Intuition | the normalised LoG at the square's centre against log σ for sides 3, 5, 7, 14: one curve, shifted | plot | closed-form curves |
| 06 | Searched vs set | one DoG level on the ×7 and ×14 patches: one centre minimum against four corner minima | placed | Q4 — two real maps with extrema marked |
| 07 | Searched vs set | normalised LoG against σ at three points: the square's centre peaks, a corner does not, the step stays flat | plot | closed-form curves, Harris–Laplace levels marked |
| 08 | Why the Gaussian | which kernel satisfies which requirement: Gaussian, Poisson, box, sampled Gaussian, nonlinear diffusion | placed | Q5 — comparison grid, no edges |
| 09 | Octaves | the pyramid for the ×7 input: five octaves, sizes, σ per layer, incremental blurs, where the blob is found | placed | Q4 — sizes and σ to scale; 7 nodes, no crossings |
| 10 | Octaves | a DoG level is the normalised Laplacian averaged over one log-σ interval: the √k shift | plot | closed-form curves |
| 11 | Refine, reject | the edge test as Harris's ratio test: t/(1 + t)² with SIFT's 0.0826 and Harris's 0.04, 0.06; the two candidates | plot | closed-form curve, real points |
| 12 | Orientation | the kept keypoint's 36-bin histogram: three peaks over 80% | plot | values from the plain-Python replay of OpenCV's rules |
| 13 | Implementation | OpenCV, scikit-image, MATLAB: doubling, thresholds, units, size, border, defaults | placed | Q5 — the series' closing tooling map |

Cover: template (placed), from Figure 1's octave — the ×7 patch and three DoG levels with the kept
point in tangerine.

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| scale space; σ and t = σ² | Problem | the family of Gaussian-blurred images indexed by σ | holds every size at once | any multi-scale detector |
| scale-normalised derivative (γ = 1) | Problem | σ^m times an m-th derivative | makes responses comparable across σ | thresholds across scales |
| characteristic scale | Problem | σ where a normalised response peaks | a size estimate | keypoint size |
| scale covariance | Problem | the selected σ multiplies with the zoom | matching across zoom | — |
| difference of Gaussians (DoG) | Worked example | L(kσ) − L(σ) | the cheap normalised Laplacian | SIFT |
| octave; interval (layer) | Worked example | a doubling of σ; s steps per doubling | sampling the scale axis | nOctaveLayers |
| 26-neighbour test | Worked example | extremum over a 3×3×3 block | candidate detection | ties |
| quadratic (Taylor) fit | Worked example | second-order fit of D around the sample | sub-pixel, sub-scale position | offsets over 0.5 |
| contrast threshold | Worked example | minimum abs(D(x̂)) | removes weak extrema | units differ |
| edge test, principal-curvature ratio | Worked example | eigenvalue ratio of D's 2×2 Hessian | removes edge points | r = 10 |
| causality; non-enhancement | Why Gaussian | no structure invented as σ grows | the search's honesty | — |
| semigroup; cascade | Why Gaussian | blur then blur = one blur | incremental pyramid | — |
| separability | Why Gaussian | 2-D kernel = product of 1-D | speed; the Gaussian's uniqueness | — |
| Poisson kernel; α-scale space | Why Gaussian | other linear scale spaces | the disagreement | — |
| Harris–Laplace | Searched vs set | Harris for position, Laplacian for scale | corner-like features with a scale | — |
| orientation assignment; descriptor | What is the scale for? | histogram peaks; 4×4×8 histograms | rotation and size normalisation | matching |
| keypoint size, response, angle | Implementation | OpenCV's units | reading output | — |

## Not repeated from earlier parts

The four-stage frame (one sentence); Part 2's derivations of the bar and disc peaks and of the DoG
approximation (used, then refined by the exact integral); Part 2's 26-neighbour cube (used, now with
real numbers); Part 2's Mikolajczyk–Schmid evidence (one clause); Part 9's tensor and scores (used only
to run Harris–Laplace); Part 1's and Part 2's note on the sampled Gaussian's discrete axioms (one
clause); Part 3's resize mapping (used to explain the quarter pixel, not re-derived).
