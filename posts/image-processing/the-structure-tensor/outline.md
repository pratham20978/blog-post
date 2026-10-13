# Outline — The Structure Tensor

**Title:** The Structure Tensor: Harris, Shi–Tomasi, and Optical Flow (58 chars; the plan's title and
the name Part 1 published for this spoke, with "structure tensor" at the front).
**Slug:** `the-structure-tensor`
**Series:** `image-processing`, part 9 · **Tier:** L4 pillar · **Category:** algorithms ·
**Difficulty:** advanced (2×2 eigenvalues, least squares, a first-order Taylor expansion) ·
**Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** about 9,000 words as the validator counts them (L4 range 7,500–10,000, references
included; prose about 8,100) · **Figures:** 12 (L4 range 12–18; the plan estimated 12)
**Built 2026-10-12:** 7,971 words as the validator counts them (references included), 12
figures, 8 feed + 4 Story cards; `validate_post.py` and `--social` PASS with 0 warnings. The
figure asserts hold every drawn number to the article. Review by eye found what no gate did: a
hard-coded wrong boundary value (71,250 for 71,185) in Figure 5's inset, a miscount (six vertical
gradients for four) in Figure 7, uppercase eyebrows that changed notation in five figures, and on
re-reading the prose, gradient directions stated backwards in the orientation section (the
figures drew them right).
**Assumes:** Part 1, *Image Processing by Hand* — the shared patch, the Sobel gradient, and its
corner section (the gradient covariance M, its eigenvalue plane drawn as a sketch in its Figure
14, Harris's R with k "conventionally 0.04 to 0.06", `cornerMinEigenVal`); Part 4, *Kernel
Design* — Sobel's ×8 ramp gain and reflect-101 as OpenCV's default border; Part 8, *Canny Edge
Detection, Line by Line* — the patch's Sobel table (under replicate) and its junction failure.
Parts 1–2 live; 4 and 8 built. All named in plain text.
**Hands off:** scale selection for the window to Part 10, *Scale Space and SIFT: Why σ Is a
Search Dimension* (named by title; Part 1 published it). Harris–Laplace is finished here only in
its position half: the scale-adapted tensor and Harris maxima per level. Learned detectors and
trackers are out of scope.

Nothing is run against an image. Every number below is worked by hand on the shared patch and
cross-checked with plain Python using only `math` (`tensor_patch.py`, `tensor_scores.py`,
`lk_patch.py`, `final_numbers.py`, `exercises.py` in the session scratchpad; not shipped).
Library behaviour carries a ledger key to source at pinned commits (OpenCV 802cf95, scikit-image
b700edc — the commits Parts 5–8 pinned), OpenCV 4.10.0 checked for the same rules, and MathWorks'
documentation for MATLAB.

**Checkpoints.** As with Parts 3–8, the session ran without a stop at A and B; what each would
have shown is recorded here.
**A:** 23 sources in the ledger: 15 peer-reviewed (14 with a DOI or registry identifier; floor
10), 4 of them used for their abstracts only (Kenney 2005, Zuliani 2004, Bigün 1991, Simoncelli
1991); 2 technical reports (Tomasi & Kanade 1991, Bouguet); 1 survey for the map (Tuytelaars &
Mikolajczyk); primary source at pinned commits and MathWorks' pages. Databases that answered:
OpenAlex, Crossref, Semantic Scholar (citations endpoint; search gave 429), arXiv, Google Scholar.
Blocked or withheld: Cornell eCommons (AWS WAF challenge for Shi & Tomasi's report; the CVPR paper
was read from Tomasi's Duke page), the Horn & Schunck mirror (TLS failure), UCSB's copy of Zuliani
et al. (HTML redirect); Elsevier abstracts withheld for Kass & Witkin, Rao & Schunck, Noble and
Horn & Schunck, so none of them is cited. No paper figure reusable: Harris & Stephens' Figure 5 is
the eigenvalue plane, but the BMVA archive states no licence; IPOL is CC BY-NC-SA (non-commercial).
**B:** this file.

**Six findings change what the plan expected.**
1. *The patch has no flat window.* The tensor at a pixel reads a 5×5 neighbourhood (a 3×3 Sobel
   inside a 3×3 window), the patch is exactly that size, and every footprint holds the step or the
   impulse. The plan's "flat" position is stated as the zero matrix, not computed; at the pixel
   level the impulse itself is "flat" (its own gradient is 0, Part 8).
2. *Row r2 is diagonal.* By the patch's up–down symmetry B = 0 on row r2, so each eigenvalue is
   simply A or C and the whole row can be worked by hand: c4 rank 1 (the step), c3 nearly rank 1,
   c2 and c1 rank 2, c0 rank 1 the other way (reflect-101 mirrors the ring).
3. *k = 0.04 and 0.06 disagree on (r2, c3).* Harris's sign depends only on the eigenvalue ratio
   t = λ2/λ1: R > 0 iff t/(1+t)² > k, a boundary at t = 0.0436 for k = 0.04 and 0.0685 for 0.06.
   (r2, c3) has t = 0.0566. The disagreement is a box-window effect: with the series' Gaussian as
   the window its ratio is 0.0220, an edge for both.
4. *`goodFeaturesToTrack` returns one point, (2, 2), and not the impulse.* The min-eigenvalue
   map's maximum (616,155.8) sits on border rows, which the function never returns (it scans rows
   and columns 1 to size − 2); the only interior 3×3 maximum is (2, 2), whose window adds the
   step's horizontal variation to the impulse's vertical one. Harris (k = 0.04) picks it too. Only
   Förstner's roundness test with q_lim = 0.75 picks the impulse itself.
5. *One Lucas–Kanade step on the real moved frame is biased, and wrong in sign at the impulse.*
   For the patch moved one pixel right: (r2, c2) gives (1.28, 0), (r2, c1) gives (−0.89, 0),
   (r2, c4) gives u = 2.00 from its only non-zero equation. The aperture problem is exact at c4;
   the rest is the linearisation, which the post explains rather than hides.
6. *A fainter impulse moves the detection onto it.* With 120 for 255, `goodFeaturesToTrack`
   returns (1, 2): the bright impulse's ring had been cutting the step's own gradient at c2 (425,
   210, 425), starving its own window of horizontal variation. Used as E3.

---

## The spine

The structure tensor is the windowed sum of the gradient's outer products. To second order it is
how fast the window's sum of squared differences grows when the window shifts, so its two
eigenvalues say how many independent directions the window varies in. Corner detectors score
those eigenvalues; the leading eigenvector is the orientation; and Lucas–Kanade's flow equations
have the same matrix on the left, so a window is trackable only when it scores as a corner —
Tomasi and Kanade's point (necessary, not sufficient: the linearisation must also hold). The patch
shows each reading, and shows that "corner" means "two
directions in one window", whether the directions come from a corner, an impulse, or two
unrelated structures.

## Verified numbers

**Gradient (Sobel 3×3, reflect-101, OpenCV's corner default):** Gx r0 0 0 640 640 0; r1 0 0 425 640
0; r2 0 0 210 640 0; r3 = r1; r4 = r0. Gy r1 430 430 215 0 0; r3 negated; others 0. Differs from
Part 8's replicate table only in column c0 (replicate: Gx 215, 430, 215; Gy ±215).
**Box 3×3 window sums (A = ΣGx², B = ΣGxGy, C = ΣGy²):** row r2 (B = 0): c0 (0, 1,109,400); c1
(405,350, 832,050); c2 (1,634,150, 462,250); c3 (1,634,150, 92,450); c4 (2,457,600, 0). (r1, c2)
1,863,125 / 91,375 / 231,125 → λ 1,868,225.1, 226,024.9, θ 3.19°. (r0, c2) 1,999,650 / 182,750 /
462,250 → Harris 648.5e9 (global max, border). (r0, c1) min-eig 616,155.8 (global max, border).
**Scores, row r2 (R in 10⁹):** k = 0.04: −49.23, 276.03, 579.59, 31.83, −241.59; k = 0.06: −73.85,
245.40, 491.69, −27.79, −362.39. Ratio t: 0, 0.4872, 0.2829, 0.0566, 0. Sign boundary t(k): 0.0436
(0.04), 0.0557 (0.05), 0.0685 (0.06); k at which a ratio stops being a corner: c2 0.1719, c1 0.2203,
c3 0.0507. Förstner q: 0, 0.8811, 0.6875, 0.2027, 0; w: 0, 272,564.6, 360,325.2, 87,499.8, 0.
q_lim 0.75 → interior max (1, 2); 0.5 → (2, 2). q = 0.75 ↔ eigenvalue ratio 3 (axes √3); 0.5 ↔
5.83 (axes 2.41). Coherence (λ1−λ2)/(λ1+λ2): 1, 0.3448, 0.5590, 0.8929, 1.
**OpenCV units:** each derivative × 1/(4·3·255) = 1/3,060; tensor ÷ 9,363,600; R ÷ 8.7677e13.
cornerHarris (k = 0.04) at (r2, c2) 0.006611, (r2, c3) 3.631e-4 (k = 0.06: −3.170e-4), (r2, c4)
−0.002755; cornerMinEigenVal (r2, c2) 0.049367, (r2, c1) 0.043290.
**goodFeaturesToTrack:** min-eig max 616,155.8 at (x 1, y 0) and (1, 4); interior maximum (2, 2) =
462,250 = 0.7502 × max; returns (2, 2) for qualityLevel ≤ 0.7502, nothing at 0.8; Harris mode
(2, 2) too.
**Lucas–Kanade on M (Sobel/8 per pixel, so M d = −8 Σ G It):** patch moved 1 px right (c0 refilled
by 40): It −160 on c3 (every row), −215 at (r2, c1), +215 at (r2, c2). (r2, c4): 2,457,600 u =
4,915,200 → u = 2.00, v undetermined. (r2, c3) and (r2, c2): Σ Gx It = −262,050 → u = 1.283, v = 0.
(r2, c1): Σ Gx It = 45,150 → u = −0.891. (r2, c0): v = 0, u undetermined. Error-ellipse axis ratio
√(λ1/λ2): c3 4.20, c2 1.88, c1 1.43 (long axis horizontal at c1).
**Variants:** shared Gaussian window, row r2 ratios: c1 0.3603, c2 0.2107, c3 0.0220. Harris &
Stephens' own (−1, 0, 1) derivative: Gx non-zero only on c2, c3 (−55 at (r2, c2)); Gy only at
(r1, c1), (r3, c1) = ±215.
**Orientation:** impulse window's gradient sum (1,060, 0) against C = 832,050; doubled-angle sum
(A − C, 2B) = (−426,700, 0). θ map: (r0, c1) 49.75°, (r1, c1) 19.97°, (r0, c2) 6.69°, (r1, c2)
3.19°, (r0, c3) 5.42°, (r1, c3) 2.87°; c0 90°, c4 0°.
**Exercises:** E1 (r1, c2) above, R(0.04) 246.83e9. E2 k* = 0.172. E3 impulse 120: gftt → (1, 2);
(r2, c1) A 857,600, C 115,200; (r2, c2) A 2,086,400, C 64,000. E4 qualityLevel 0.8 → None. E5
space-time tensor at (r2, c4), per-pixel units: [38,400, 0, −76,800; 0, 0, 0; −76,800, 0, 153,600],
null space (0, 1, 0) and (2, 0, 1) → u = 2, v free.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + jump + IMPORTANT | 300 | — |
| Why this matters | 170 | — |
| The problem | 380 | — |
| Worked example: gradient; windows on row r2; scores; goodFeaturesToTrack; Lucas–Kanade; scorecard | 1,350 | FIG_01, FIG_02, FIG_03 |
| Intuition: the SSD bowl | 300 | FIG_04 |
| How do Harris, Shi–Tomasi and Förstner score the same two numbers? (k as a ratio; the tracker's criterion; precision and roundness) | 800 | FIG_05, FIG_06 |
| How does the same matrix give orientation? (doubled angle; coherence; space-time) | 450 | FIG_07, FIG_08 |
| Why is Lucas–Kanade the same matrix? (normal equations; aperture; three-way rule; selection = tracking; precision) | 750 | FIG_09 |
| When does one Lucas–Kanade step go wrong? (linearisation; smoothing, iteration, pyramid; one motion per window) | 550 | FIG_10 |
| Which window, and at what scale? (footprint; box against Gaussian; scale-adapted tensor) | 600 | FIG_11 |
| The math | 450 | — |
| Implementation: the tooling map | 600 | FIG_12 |
| Limitations and common mistakes | 380 | — |
| Key takeaways | 140 | — |
| Try it yourself (E1–E5) | 600 | — |

## Figure plan (route gate run per figure)

Source check for every paper-backed section: Harris & Stephens' Figure 5 (the classification
plane) is the only paper figure that teaches a planned point; the BMVA archive states no reuse
licence, so it is not reproduced and Figure 5 here is our own analysis (the plane to scale with
the patch's points), not a redraw. Shi & Tomasi, Tomasi & Kanade and Bouguet have no figure the
sections need; IPOL is CC BY-NC-SA.

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | the patch's gradient under reflect-101, with the four row-r2 windows the post sums | placed | Q4 — a grid of real values with vectors to scale |
| 02 | Worked example | row r2's tensors as ellipses: rank 1 at c4, nearly 1 at c3, 2 at c2 and c1, 1 the other way at c0 | placed | Q4 — small multiples of real matrices drawn as their shape |
| 03 | Worked example | the min-eigenvalue map, the excluded border, and why (2, 2) wins: two edges in one window | placed | Q4 — a grid of real values plus a decomposition |
| 04 | Intuition | the window's SSD against shift, dᵀMd, at c4 (trough), c3, c2, c1 (bowls) | plot | closed-form quadratic forms of the worked matrices |
| 05 | Scores | the eigenvalue plane to scale: Harris rays at k = 0.04 and 0.06, Förstner's q rays, the patch's windows | plot | geometry of the scores, real points |
| 06 | Scores | every score as a function of the ratio t at fixed trace; where 0.04 and 0.06 cross zero | plot | closed-form curves |
| 07 | Orientation | why products: the impulse window's nine gradients summed as vectors and as doubled angles | placed | Q4 — the real vectors drawn to scale |
| 08 | Orientation | all 25 tensors as oriented ellipses over the patch: orientation and coherence | placed | Q4 — a grid of real glyphs |
| 09 | Lucas–Kanade | the (u, v) plane: c4's line of solutions and the error ellipses σ²M⁻¹ at c3, c2, c1 | plot | closed-form ellipses of the worked matrices |
| 10 | Linearisation | row r2 moved one pixel: the actual It against the linear prediction −g·d | plot | real values, bar-style plot |
| 11 | Window and scale | the 5×5 footprint, box against Gaussian weights, and (r2, c3)'s ratio under each | placed | Q4 — weights and values to scale |
| 12 | Implementation | OpenCV, scikit-image, MATLAB: derivative, window, border, score, units, selection, flow defaults | placed | Q5 — comparison grid, the series' closing tooling map |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| structure tensor (second-moment matrix, autocorrelation matrix) | Problem | windowed sum of the gradient's outer products | one matrix behind detection, orientation and flow | any of the three |
| outer product g gᵀ; rank | Worked example | the 2×2 matrix of one gradient; how many directions | why one pixel cannot be a corner | windows |
| eigenvalues, eigenvector | Problem / Worked example | variation along the principal directions | what every score reads | scoring, orientation |
| window, integration scale; derivative scale | Problem / Window | the weights summed over; the derivative's own support | set the tensor's scale | choosing blockSize, σ |
| Harris response, k | Worked example | det − k tr² | cheap corner score with a free constant | Harris |
| Shi–Tomasi score | Worked example | the smaller eigenvalue | the tracker's own test | goodFeaturesToTrack |
| Förstner weight and roundness (w, q) | Scores | det/tr and 4 det/tr² | precision and isotropy of a point | photogrammetry, skimage |
| aperture problem; normal flow | Problem / Lucas–Kanade | only the component along the gradient is measurable | rank-1 windows | edges in motion |
| brightness constancy; It | Problem / Worked example | the frame difference the linear model explains | Lucas–Kanade's right-hand side | tracking |
| Lucas–Kanade | Worked example | least-squares solve for a window's shift | sparse tracking | after feature selection |
| coherence; doubled angle | Orientation | (λ1 − λ2)/(λ1 + λ2); angle × 2 so ±g agree | orientation without sign cancellation | texture |
| error ellipse | Scores / Lucas–Kanade | σ²M⁻¹ | how precisely a point or flow is located | choosing features |
| pyramid; coarse to fine | Linearisation | solve on smaller images first | extends the small-motion range | large motion |

## Not repeated from earlier parts

The four-stage frame (one sentence); Part 1's corner paragraph and its schematic plane (cited and
superseded by the plane to scale, not redrawn); Part 4's ×8 gain and border rules (used); Part 8's
Sobel table, suppression and hysteresis (the table is re-used under reflect-101 and the difference
stated; the junction failure named); Part 2's normalised Laplacian and Harris–Laplace's scale half
(named, handed to Part 10).
