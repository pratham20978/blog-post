# Outline — Gradient-Domain Editing: Poisson Cloning, HDR and Tiling

**Title:** Gradient-Domain Editing: Poisson Cloning, HDR and Tiling (56 chars; the plan's title,
*Gradient-Domain Editing: Poisson Cloning, HDR Compression, Seamless Tiling*, is 75, over the series'
60-character rule. Part 2 promised "gradient-domain editing — Poisson cloning, HDR compression,
seamless tiling", so all three stay in the title, shortened. The search phrases — "Poisson image
editing", "seamless cloning OpenCV", "gradient domain image processing", "how does seamlessClone
work" — go into the summary, Insights and headings.)
**Slug:** `gradient-domain-editing`
**Series:** `image-processing`, part 14, the last spoke · **Tier:** L3 deep dive · **Category:**
algorithms · **Difficulty:** advanced (partial derivatives, divergence, a 9×9 linear system, one
eigen-decomposition; the multigrid vocabulary is taught in place) · **Lab grade:** G0 — by hand, the
series invariant (no `lab/`)
**Budget:** about 6,900 words as the validator counts them (L3 range 5,000–7,500, references and math
tokens included) · **Figures:** 10 (L3 range 8–12; the plan estimated 10)
**Assumes:** Part 2, *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening* — its five-point
stencil, its values on the patch (−860 at the impulse, 375 at (r2, c2), ±160 across the step) and its
section "Keeping the Laplacian instead of the pixels", which named this post. Part 2 is the sole
prerequisite; Part 1 is assumed only through it. Part 11 (*Thresholding and Segmentation: Otsu,
Sauvola, Watershed*) supplies the shadowed copy (8, 40, 51); Parts 5, 8 and 12 are named where their
tools appear (the DFT, Canny, erosion). All named in plain text; Part 2 is live, the rest built.
**Hands off:** nothing; a leaf. Learned blending and inpainting stay out of scope, as for the series.

Nothing is run against an image. Every number is worked by hand on the series' 5×5 patch and asserted
in `assets/_data.py` (plain Python, `math` and `fractions` only; private, not published): exact
rational Gauss–Seidel and elimination, the sine-transform solve, the V-cycle, the attenuation
factors. Library behaviour carries a ledger key to source at pinned commits: OpenCV 802cf95 (and
4.10.0, 4.11.0–4.14.0, 5.0.0), Luminance HDR 764fb836, MathWorks R2026b, SciPy 1.18.0.

**Checkpoints.** As with Parts 3–13, the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 20 sources, 12 peer-reviewed with identifiers (floor 7), four scholarly databases answered
(OpenAlex, Crossref, Google Scholar, arXiv; floor 4; Semantic Scholar 429). No survey of
gradient-domain editing exists; the IPOL review (Di Martino et al. 2016) is the map. Pérez 2003,
Fattal 2002, Agarwala 2007 and the IPOL review read in full; Brandt 1977 and Saad 2003 from open
copies; six follow-ups by abstract. OpenCV's photo module read at 802cf95 and six tags, with its issue
tracker and the history of `seamless_cloning.cpp`. 56 claims. No paper figure is reusable (ACM
copyright; IPOL is CC BY-NC-SA).
**B:** this file.

**Seven findings change what the plan expected.**
1. *The plan's system has no edit in it until a guidance field is chosen.* With the patch's own
   differences as guidance and its ring as boundary, the nine equations return the patch exactly, and
   only because Pérez's per-edge differences match the five-point stencil (IPOL's remark). So the
   worked example is the round trip — keep the gradients, throw the pixels away, get them back — and
   the edits come after it.
2. *Three Gauss–Seidel sweeps from zero leave 31.1 levels of error.* The first sweep takes the error
   from 255 to 89.7 and leaves it smooth (all of one sign); after that it halves every sweep exactly
   (ρ = cos²(π/4) = 0.5); nine sweeps before the 8-bit answer is right.
3. *The V-cycle's coarse equation is 3/4, not 1.* With full weighting and bilinear interpolation the
   Galerkin operator on one coarse point is RAP = 3/4, where re-discretising gives 1 (Saad: they differ
   in 2-D). One V(1,1) cycle leaves 15.4 against three sweeps' 31.1, and two cycles 0.82. On nine
   unknowns that is a factor of two; the gap that matters grows as (N + 1)².
4. *Cloning keeps differences, not ratios.* The patch's interior cloned into Part 11's shadowed copy
   (a fifth of the light) goes to −32 and −40 on the dark side and keeps a 243.6 spike; done in log the
   mismatch is the constant −ln 5 and the clone is the shadowed patch exactly, 8, 40, 51.
5. *OpenCV's `seamlessClone` is not the paper's algorithm.* It solves the mask's bounding rectangle by a
   sine transform (no iteration), takes source gradients only 3 px inside the mask (issue #17450, open),
   so a 3×3 clone imports nothing, compares abs(gx − gy) for `MIXED_CLONE` — the impulse's own
   differences (−215, −215) never win — and truncates. Since 4.11.0 it also edits a single-channel
   mask in place (the 2018 fix for #12053 was undone by PR #26511).
6. *Fattal's attenuation turns the step's 5:1 into 2.70:1 and makes a field no image has.* At β = 0.85
   the step row's gradient sits at 25α and keeps 0.617 of its log size. In 2-D the impulse lowers the
   central difference at (r2, c2) to 0.12, so row r2's step is squeezed less than row r1's (3.92:1
   against 2.80:1) while the vertical differences stay zero: circulation −0.337. At the spike itself
   central differences read zero and the factor is unbounded.
7. *Pérez's tiling rule on the step row gives 120 80 40 160 120.* The seam disappears and the step
   shrinks from 160 to 120; on the 3×3 interior the impulse rides up to 289.3 and must be clipped.

---

## The spine

Keep an image's gradients and throw its pixels away, and the pixels can be recovered: the gradients
inside a region and the values on its border fix every pixel inside, as the unique solution of a
Poisson equation. Editing in the gradient domain changes one of the two and solves again. Cloning
swaps the border, and the mismatch spreads inward as a smooth membrane. HDR compression shrinks the
large gradients, which leaves a field that is no image's gradient, so the solve finds the closest
image in least squares. Tiling makes opposite borders agree. The solve is one sparse equation per
pixel; Gauss–Seidel removes rough error fast and smooth error slowly, so large regions need multigrid,
a transform on a rectangle, or fewer unknowns.

## Verified numbers (all asserted in `assets/_data.py`)

**Region and boundary:** Ω = rows r1–r3 × columns c1–c3; the 12 ring pixels that touch Ω: top and
bottom 40, 40, 200; left 40 ×3; right 200 ×3; corners unused. Boundary sums per pixel (row-major):
80, 40, 400, 40, 0, 200, 80, 40, 400. Laplacian on Ω: 215, 160, −160 / −860, 375, −160 / 215, 160,
−160 (sum −215 = the net flux through the ring, all of it at the impulse's left edge).
**System:** A = 4 on the diagonal, −1 per in-Ω neighbour; b = boundary − Laplacian = −135, −120, 560,
900, −375, 360, −135, −120, 560; x* = 40, 40, 200, 255, 40, 200, 40, 40, 200.
**Gauss–Seidel from zero (row-major):** sweep 1: −33.75, −38.44, 130.39, 216.56, −49.22, 110.29, 20.39,
−37.21, 158.27 (max error 89.7, RMS 68.3); sweep 2: 10.78, −7.01, 165.82, 220.49, −22.11, 165.50,
12.07, 7.06, 183.14 (62.1); sweep 3: 19.62, 10.83, 184.08, 227.40, 8.95, 184.04, 24.86, 24.24, 192.07
(31.1, RMS 21.2); then 15.5, 7.8, 3.9, 1.9, 0.97, 0.49 (sweep 9).
**V(1,1):** residual after sweep 1: 178.12, 81.17, 110.29, −28.83, 73.09, 158.27, −37.21, 158.27, 0;
full weighting r_c = 80.08; A_c = RAP = 3/4 (re-discretised 1); e_c = 106.78; prolongation 26.69 /
53.39 / 106.78; after correction max error 47.1; after post-smoothing 37.48, 33.03, 189.18, 260.53,
24.61, 189.69, 35.43, 31.25, 195.23 (max 15.4, RMS 8.6); second cycle 0.82; asymptotic factor 0.0054
per cycle (re-discretised: 27.1, then 2.9, factor 0.048).
**Sine transform:** eigenvalues of A 4 − 2cos(kπ/4) − 2cos(lπ/4): 1.172, 2.586 ×2, 4 ×3, 5.414 ×2,
6.828; coefficients of b with k = 2 vanish (rows r1 and r3 equal); the solve returns x* exactly.
Jacobi mode factors 0.707, 0.354, 0, −0.354, −0.707; Gauss–Seidel ρ 0.5.
**Scale:** Gauss–Seidel sweeps per digit ln 10 / −ln cos²(π/(N+1)) ≈ 0.2333 (N+1)²: N = 3: 3.3; 31:
238.5; 255: 15,289; 1,023: 244,633. Optimal SOR ω = 2/(1 + sin(π/(N+1))): N = 3: ω 1.172, ρ 0.172,
1.3 sweeps per digit; N = 1,023: ω 1.99388, ρ 0.99388, 375 sweeps per digit.
**Four fills of Ω (row-major):** membrane (no guidance) 58.57, 90, 161.43 / 64.29, 100, 155.71 / 58.57,
90, 161.43. Guided by the patch, patch frame: the patch. Clone into the shadowed copy (frame 8 and 40),
codes: −6.86, −32, 70.86 / 203.57, −40, 75.43 / −6.86, −32, 70.86 (the correction −46.86, −72, −129.14
/ −51.43, −80, −124.57 / …); step at r1 102.86, spike 243.57 above its neighbour; OpenCV-style
clamp-and-truncate 0, 0, 70 / 203, 0, 75 / 0, 0, 70. Same clone in log: 8, 8, 40 / 51, 8, 40 / 8, 8, 40.
Frame 60 darker: −20, −20, 140 / 195, −20, 140.
**HDR, step row (single level, central differences, zero outside):** H differences ln 5 = 1.6094; central
0.8047 at c2 and c3; mean 0.3219, α 0.0322 (step at 25α). φ = 25^(β−1): 0.525, 0.617, 0.725 for β
0.8, 0.85, 0.9; attenuated 0.845, 0.993, 1.167; ratio 5:1 → 2.33, 2.70, 3.21:1.
**HDR, 2-D patch:** central magnitudes 0.8047 on the step, 0.9262 beside the impulse, 0.1215 at
(r2, c2), 0 at the impulse; mean 0.4057, α 0.0406; Φ(r1, c2) 0.6388, Φ(r2, c2) 0.8483 (ratio 1.328);
G_x(r1, c2) 1.028 (2.80:1), G_x(r2, c2) 1.365 (3.92:1); circulation −0.337. At the impulse with a 10⁻⁴
floor: φ 2.46, outgoing −1.852 → −4.56.
**Tiling:** step row, Pérez's rule: ends 120; membrane +80 → −80; result 120, 80, 40, 160, 120; tiled
seam 120 | 120; step 120. 3×3 interior: 68.57, 40, 171.43 / 289.29, 40, 165.71 / 68.57, 40, 171.43.
**OpenCV:** a 5×5 source with a full mask: frame cleared → 3×3; 7×7 erosion → empty; output the
destination (to within float rounding and truncation). `MIXED_CLONE` at the impulse: forward
differences (−215, −215), abs(gx − gy) = 0, so the destination's wins even against a flat 0.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + jump + IMPORTANT | 330 | — |
| Why this matters | 170 | — |
| The problem | 360 | — |
| Worked example: what is kept; nine equations; three sweeps; one V-cycle; no iteration at all | 1,000 | FIG_01–FIG_04 |
| Intuition: a membrane, and why sweeps are slow | 300 | — |
| What does a clone keep, and what does it give up? | 500 | FIG_05 |
| Why is the solve slow, and what makes it fast? | 430 | FIG_06 |
| HDR compression: which gradients shrink? | 500 | FIG_07, FIG_08 |
| Seamless tiling: making opposite edges agree | 240 | FIG_09 |
| The math | 430 | — |
| Implementation: the tooling map | 500 | FIG_10 |
| Limitations and common mistakes | 320 | — |
| Key takeaways | 130 | — |
| Try it yourself (E1–E4) | 400 | — |
| References (20 entries) | 850 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | what is kept and what is thrown away: the ring's 12 values stay, Ω's 9 pixels are erased, its Laplacian (215 … −860 … 375) stays | placed | Q4 — a grid of real values, cell by cell |
| 02 | Worked example | the nine equations as one 9×9 system: A's stencil rows, x*, and b split into boundary sums minus the Laplacian | placed | Q4 — a matrix of real values |
| 03 | Worked example | three Gauss–Seidel sweeps from zero as small multiples, with the error shrinking 255 → 89.7 → 62.1 → 31.1 and turning smooth | placed | Q4 — small multiples of real grids |
| 04 | Worked example | one V-cycle: pre-smooth, residual, restrict to one number, solve 3/4·e = 80.1, interpolate, correct, post-smooth: error 15.4 | placed | Q4 — seven stages each carrying a grid or a number; no crossings |
| 05 | Clone | four fills of one hole in the same frame: membrane, guided (exact), cloned into the shadowed copy in codes (negatives), and in log (exact) | placed | Q4 — small multiples of real grids |
| 06 | Scale | Gauss–Seidel and optimal-SOR sweeps per digit against region width, log–log, from the closed forms | plot | Q4 — two curves from closed forms, to scale |
| 07 | HDR | Fattal's factor φ against gradient magnitude in units of α for β 0.8, 0.85, 0.9, with the step at 25α and its 5:1 → 2.70:1 | plot | Q4 — curves from a closed form, to scale |
| 08 | HDR | one square of the patch after attenuation: 1.028 on row r1, 1.365 on row r2, zero up both columns — the loop does not close | placed | Q4 — real values on the edges of a grid |
| 09 | Tiling | the step row repeated three times, before (a 160 jump at every seam) and after Pérez's rule (120 80 40 160 120, seamless) | placed | Q4 — strips of real cells |
| 10 | Implementation | OpenCV's photo module, MATLAB and SciPy: region, solver, gradients used, boundary and quirks | placed | Q5 — the series' closing tooling map, a comparison grid with no edges |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| gradient field; guidance field v | Problem | the per-pixel differences to the right and below; the field the result's gradient should match | what gradient-domain editing keeps | every edit |
| region Ω; boundary ∂Ω; Dirichlet condition | Problem | the pixels solved for; their outside neighbours; values fixed there | where an edit lives | cloning, tiling |
| divergence | Problem | net outflow of the field at a pixel | the Poisson equation's right side | any edited field |
| Poisson equation; Laplace equation; membrane (harmonic) interpolant | Problem / Intuition | ∇²f = div v; ∇²f = 0; the smoothest fill | the core equation | always |
| least squares | Problem | the image whose gradient is closest to the field | a field may be no image's gradient | HDR, mixing |
| Gauss–Seidel; sweep | Worked example | update each unknown from its neighbours, newest values first | the simplest solver | small regions |
| smooth and rough error; smoothing | Worked example | slowly and quickly varying error; what a sweep removes fast | why multigrid exists | large regions |
| multigrid; V-cycle; restriction; full weighting; prolongation; coarse grid; Galerkin operator | Worked example | solve the smooth error on a coarser grid and bring the correction back | O(n) solves | large regions |
| discrete sine transform | Worked example | the basis that makes the stencil diagonal on a rectangle | a direct solve | OpenCV, rectangles |
| convergence factor; spectral radius | Scale | the per-sweep shrink of the slowest error | sweeps per digit | choosing a solver |
| successive over-relaxation (SOR) | Scale | Gauss–Seidel with a step longer than one | what Pérez used | medium regions |
| quadtree; mean-value coordinates | Scale | fewer unknowns where the correction is smooth; a weighted sum of boundary values | beating O(n) unknowns | gigapixels, real time |
| seamless cloning; importing, mixing gradients; monochrome transfer; bleeding | Clone | Pérez's modes; a destination edge smearing into a clone | what each keeps | cloning |
| dynamic range; tone mapping; high dynamic range (HDR) | Why / HDR | brightest to darkest ratio; mapping to a display | why compress gradients | sun and shade |
| log domain; attenuation factor φ; α, β | HDR | ratios become differences; a per-pixel scale on the gradient | Fattal's method | HDR |
| integrable (conservative); circulation; Neumann condition | HDR | a field that is some image's gradient; its sum around a loop; zero normal derivative at the image edge | least squares, whole-image solves | HDR |
| seamless tiling; periodic | Tiling | edges that match when repeated | textures | backgrounds |

## Not repeated from earlier parts

Part 2's identity (one sentence: the Laplacian is what blur removes per unit of scale), the five-point
stencil (shown once, inside Figure 2's rows), Part 2's Poisson figure (not redrawn; Figure 1 adds the
numbers), Land and McCann (one clause), the DFT (Part 5, named for the sine transform), Canny (Part 8,
named for `textureFlattening`), erosion (Part 12, named for the mask's three pixels).
