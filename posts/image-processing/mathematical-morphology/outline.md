# Outline — Mathematical Morphology as Lattice Algebra

**Title:** Mathematical Morphology as Lattice Algebra (42 chars; Part 1 published the spoke's name as
*Mathematical morphology as lattice algebra* and Part 11 names it by this title, so it is kept as is;
the search phrases — "erosion and dilation", "opening vs closing", "morphological gradient", "top-hat
transform", "structuring element" — go into the summary, the Insights and the headings).
**Slug:** `mathematical-morphology`
**Series:** `image-processing`, part 12 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** advanced (the post states and proves laws; set notation and the lattice are taught
in place, not assumed) · **Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** about 6,900 words as the validator counts them (L3 range 5,000–7,500, references and
math tokens included) · **Figures:** 11 (L3 range 8–12; the plan estimated 11)
**Assumes:** Part 1, *Image Processing by Hand* — the stage-4 section that defines erosion and
dilation as a local minimum and maximum over a structuring element and draws morphology inside the
rank operators (its Figure 10, `#morphology-ordering-within-a-structuring-element`); the shared patch.
Part 11, *Thresholding and Segmentation: Otsu, Sauvola, Watershed* — the raw patch's Otsu cut (40),
which binarises the patch here. Part 8, *Canny Edge Detection, Line by Line: Setting the Thresholds*
— the patch's Sobel table, quoted for comparison with the morphological gradient. Named in plain
text; Parts 8 and 11 are built, not live.
**Hands off:** the segmentation use of markers (h-minima, distance transform, cleaned masks) back to
Part 11, by title; learned morphology is out of scope, as for the series.

Nothing is run against an image. Every number is worked by hand on the shared patch (and on the
patch tiled beside a copy of itself, for one border check), cross-checked with plain Python using
only built-in sets and lists (`assets/_data.py`, which asserts each number the article prints; a
private build file, not published). Library behaviour carries a ledger key to source at pinned
commits: OpenCV 802cf95 (and tags 4.10.0, 4.11.0, 4.12.0), scikit-image b700edc (and v0.25.2,
v0.26.0), SciPy v1.18.1, MathWorks R2026b documentation.

**Checkpoints.** As with Parts 3–11, the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 19 sources (9 peer-reviewed with identifiers, floor 7; four read as abstracts only), five
scholarly databases (OpenAlex, Google Scholar, Semantic Scholar, Crossref, the CWI repository; floor
4). The survey is Heijmans' 1995 SIAM Review article, read in full from the CWI repository with the
Heijmans–Ronse report (1988 version of the 1990 paper). Vincent 1993 and Serra–Vincent 1992 were read
from Luc Vincent's archived page, Haralick et al. 1987 from Haralick's own site. The plan's three
books (Serra 1982, Matheron 1975, Soille's handbook) have no open copy; their results are cited
through the sources that state them. 57 claims. No paper figure is reusable (SIAM, IEEE, Springer).
**B:** this file.

**Eight findings change what the plan expected.**
1. *The binary example is a slice of the grey one.* The mask at Otsu's raw cut (pixels above 40) is
   the patch's threshold set at every t from 41 to 200, and also exactly the patch's set of regional
   maxima. Because flat operators commute with thresholds, the grey operators are the binary worked
   example done at three levels and stacked; the post uses that instead of a second example.
2. *The border rule is load-bearing on a 5×5 patch.* With the rule OpenCV, MATLAB and scikit-image
   use by default (the outside never wins a minimum or a maximum), the cross erodes the 11-pixel mask
   to column c4 (5 px). With SciPy's default (border value 0) the erosion is empty and the binary
   closing keeps 7 pixels, losing 7 of the mask's 11 — a closing that is not extensive. The
   adjunction holds exactly on the bounded grid with the first rule (0 failures in 20,000 random
   pairs) and fails with the second (616; smallest counterexample one corner pixel).
3. *The granulometry has two steps, and one is a border artefact.* Areas 11, 10, 0, 0 for n = 0–3
   (grey volumes 2,815, 2,600, 1,000, 1,000): the speck goes at n = 1, the bar at n = 2. The bar is
   two pixels wide yet survives the three-wide cross because it touches the edge: on the patch tiled
   beside a copy (5 × 10) the inner bar vanishes at n = 1 with the specks and only the edge bar
   survives.
4. *OpenCV's dilate does not reflect the element.* Its `erode` and `dilate` use the same offsets, so
   they are complement duals, not adjoints; for any asymmetric kernel (every even-sized one)
   `MORPH_OPEN` and `MORPH_CLOSE` are not an opening and a closing. On the mask with `np.ones((2, 2))`
   OpenCV's closing returns 7 pixels and loses 5 of the mask's; its opening keeps only c4, where the
   true opening keeps the bar. Issue #23605 has been open since 2023; scikit-image fixed the same
   defect in 2023 (#6676). Dilating with `anchor=(0, 0)` restores both laws (13 and 10 px).
5. *`iterations=2` is a bigger element, not a second pass.* Opening twice is opening once (10 px);
   OpenCV's documented `iterations=2` erodes twice and dilates twice, an opening by the 13-pixel
   diamond: the mask becomes empty and the grey patch flat 40.
6. *The morphological gradient reads heights, not slopes.* δ − ε is 160 on both sides of the step
   (the step's height, no gain) and 215 on the impulse and its four neighbours; Part 8's Sobel reads
   640 (a ×4 gain) on the step and 0 on the impulse itself.
7. *Reconstruction measures height.* The bar's dynamic is 160 and the impulse's 215: h-maxima with
   h = 100 keeps both (100 and 155), h = 180 keeps only the impulse (75), h = 215 neither. Opening by
   reconstruction equals the opening on this patch, because the opening already restores the bar
   exactly.
8. *Same names, different sets.* OpenCV's default kernel is the 3×3 square, scikit-image's the cross;
   OpenCV's 3×3 "ellipse" is the cross; its 5×5 ellipse has 17 pixels, scikit-image's `disk(2)` 13.
   Exact Euclidean disks break the sieve law (disk(3) opened by disk(2) loses four corner pixels),
   which is why MATLAB approximates disks with periodic lines and warns that exact disks are
   unsuitable for granulometries.

---

## The spine

Images form a lattice: masks under inclusion, grey images under the pixelwise order. An operator that
commutes with unions is a dilation, and on a grid every translation-invariant one is a Minkowski sum
with an element. Erosion is dilation's adjoint: δ(A) ⊆ Y exactly when A ⊆ ε(Y). That one equivalence
gives every law people quote — opening never adds, closing never removes, both are idempotent, sizes
compose — and grey levels inherit them because flat operators commute with thresholds. The laws hold
only if the implementation keeps the pair adjoint: its border rule and its reflection convention
decide that, and OpenCV's convention breaks it for asymmetric elements.

## Verified numbers (all asserted in `assets/_data.py`)

**Mask** X = P > 40: c3, c4 (all rows) + (r2, c1) — 11 px. Cross B (5 px).
**Binary, outside ignored:** ε = c4 (5); δ = c2–c4 + (r1, c1), (r2, c0), (r2, c1), (r3, c1) (19);
γ = c3–c4 (10); φ = c3–c4 + (r1–r3, c2) + (r2, c1) (14). γγ = γ, φφ = φ; εγ = ε; δφ = δ.
Adjunction: 64 named pairs of {∅, speck, ε, γ, X, φ, δ, all}, 0 mismatches; 20,000 random pairs, 0.
**Outside = 0 (SciPy default):** ε = ∅; φ = (r1–r3, c2), (r1–r3, c3), (r2, c1) (7): loses (r0, c3),
(r4, c3) and all of c4, gains (r1–r3, c2). 616 of the same 20,000 random pairs fail; A = {(r0, c4)} fails.
**Laws:** δ(bar ∪ speck) = δ(bar) ∪ δ(speck) (15 and 5 → 19); B ⊕ B = 13-px diamond; εε = ε_{B⊕B}.
Median over the cross = max of erosions by its ten 3-point subsets (interior), = patch without impulse.
**Grey:** ε: c0–c3 40, c4 200. δ: r0 40 40 200 200 200; r1 40 255 200 200 200; r2 255 255 255 200 200.
γ = patch without impulse (sum 2,600). φ: r1 and r3 40 40 200 200 200; r2 40 255 200 200 200 (sum
3,295). δ − ε: 160 on c2, c3; 215 at (r2, c0–c2), (r1, c1), (r3, c1). f − γ: 215 at (r2, c1) only.
φ − f: 160 at (r1–r3, c2). Half-gradients: f − ε 160 on c3, 215 at the impulse; δ − f 160 on c2,
215 at its four neighbours. Square element gradient: 215 on (r1–r3, c0–c2), 160 on c3 and (r0, r4, c2).
Threshold decomposition holds at every t; levels 41–200 give the mask, 201–255 the impulse.
**Granulometry (cross family nB, |nB| = 1, 5, 13, 25):** area 11, 10, 0, 0; volume 2,815, 2,600,
1,000, 1,000; spectrum 1 px and 10 px (215 and 1,600 above 40). Sieve law holds for m, n in 0–3.
'reflect' border and squares give the same. Tiling 5 × 10: 22, 10 (cols 8–9 only), 0.
Disk(3) (29 px) opened by disk(2) (13 px): 25 px, the four (±2, ±2) corners lost.
**OpenCV 2×2 (anchor (1, 1)):** MORPH_OPEN → c4 (5); MORPH_CLOSE → c4 + (r3, c2), (r3, c3) (7);
true opening 10, true closing 13 (X + r2 whole row). 1×2: same opening; closing c4 + (r2, c2), (r2, c3).
Fix `dilate(anchor=(0, 0))`: 10 and 13. #23605's example reproduced exactly.
**iterations=2 (cross):** mask 0 px, grey flat 40 (1,000); opening twice: 10 px.
**Reconstruction (8-conn):** opening by reconstruction = opening. HMAX_h: bar max(40, 200 − h), impulse
max(40, 255 − h) for h ≤ 215; regional maxima = X (11 px). Distance transform (city block) = sum of
erosions: c3 1, c4 2, impulse 1.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + jump + IMPORTANT | 300 | — |
| Why this matters | 170 | — |
| The problem | 330 | — |
| Worked example: binarise; erode and dilate; open and close; check the adjunction; apply twice; sieve by four sizes | 1,150 | FIG_01–FIG_04 |
| Intuition: stamping and fitting; the band-pass analogy and where it breaks | 280 | — |
| What makes an operator a dilation? | 480 | FIG_05 |
| Why are opening and closing idempotent? | 450 | — |
| How do grey levels inherit the laws? | 520 | FIG_06, FIG_07 |
| What do the laws let you build? | 500 | FIG_08 |
| Where do libraries break the laws? | 480 | FIG_09, FIG_10 |
| The math | 400 | — |
| Implementation: the tooling map | 380 | FIG_11 |
| Limitations and common mistakes | 280 | — |
| Key takeaways | 130 | — |
| Try it yourself (E1–E4) | 420 | — |
| References (17 entries) | 600 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | the mask, the cross, its erosion (5 px) and dilation (19 px) | placed | Q4 — small multiples of a real 5×5 grid |
| 02 | Worked example | opening keeps the bar and drops the speck; closing bridges the gap; each applied twice is unchanged | placed | Q4 — small multiples of real grids |
| 03 | Worked example | the adjunction checked on four pairs: δ(A) ⊆ Y and A ⊆ ε(Y) agree each time | placed | Q4 — paired grids per row, a yes/no per side |
| 04 | Worked example | the granulometry over n = 0–3 (area and grey volume) and its pattern spectrum | chart | Q1 — eight values computed from the definitions, on two scales side by side |
| 05 | What makes a dilation | four laws on the patch: δ of a point is the element; δ distributes over union; cross ⊕ cross = diamond; the median is the max of ten erosions | placed | Q4 — real grids and element shapes |
| 06 | Grey levels | the patch's threshold sets at 41 and 201 eroded one by one, stacked back into the grey erosion | placed | Q4 — small multiples of real grids |
| 07 | Grey levels | morphological gradient against Part 8's Sobel; white and black top-hats | placed | Q4 — grids of real values side by side |
| 08 | Build | h-maxima at h = 100, 180, 215: the bar's dynamic 160, the impulse's 215 | placed | Q4 — small multiples of real grids, with a height scale |
| 09 | Libraries | border rules: erosion and closing with the outside ignored and with the outside 0; the tiled bar measured twice | placed | Q4 — small multiples of real grids |
| 10 | Libraries | OpenCV's 2×2 opening and closing against the true ones; the anchor fix | placed | Q4 — small multiples of real grids with element offsets |
| 11 | Implementation | OpenCV, scikit-image, SciPy, MATLAB: default element, border rule, reflection, iterations, shapes | placed | Q5 — a comparison grid with no edges, the series' closing tooling map |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| binary image as a set; structuring element; translate | Problem | a mask is the set of its foreground pixels; the element a small set of offsets | the probe every operator moves around | always |
| erosion; dilation; Minkowski sum | Worked example | pixels where the element fits; union of stamped copies | the two primitives | every call |
| border rule | Worked example | what the outside counts as | decides the edge pixels and the laws | bounded images |
| opening; closing | Worked example | erode then dilate; dilate then erode | remove specks, fill gaps | cleaning masks |
| adjunction (Galois connection) | Worked example | δ(A) ⊆ Y exactly when A ⊆ ε(Y) | source of every law | reasoning about composites |
| extensive; anti-extensive; idempotent; increasing | Worked example | X ⊆ ψ(X); ψ(X) ⊆ X; ψψ = ψ; order-preserving | the laws | trusting a filter |
| granulometry; pattern spectrum | Worked example | openings by growing elements; area removed per size | size distributions | measuring sizes |
| partial order; lattice; supremum and infimum; complete lattice | What makes a dilation | order with least upper and greatest lower bounds for every family | the structure replacing linearity | binary and grey alike |
| translation invariance; Matheron's representation; rank filter | What makes a dilation | operators that commute with shifts; union of erosions | morphology contains the median | Part 1's Figure 10 |
| algebraic opening and closing; morphological filter | Idempotent | increasing + idempotent (+ anti-extensive or extensive) | what "filter" means here | building filters |
| complement duality; reflection | Idempotent | (ε_B X)ᶜ = δ_B̌(Xᶜ) | the second duality, needs the reflected element | asymmetric elements |
| threshold set; flat operator | Grey levels | {x : f(x) ≥ t}; operator commuting with thresholds | grey from binary | grey morphology |
| morphological gradient; half-gradients; top-hats | Grey levels | δ − ε; f − ε, δ − f; f − γ, φ − f | edges, peaks, valleys | feature extraction |
| reconstruction; geodesic dilation; opening by reconstruction | Build | grow a marker inside a mask until stable | keep whole components | markers |
| regional maximum; h-maxima; dynamic | Build | plateau with lower neighbours; maxima taller than h | select by height | marker selection |
| distance transform | Build | city-block distance to the background | stacked erosions | splitting blobs |
| anchor | Libraries | the element's origin in OpenCV | where the offsets are measured | even-sized kernels |

## Not repeated from earlier parts

The four-stage frame (one sentence), Part 1's three answers on the impulse (the median's 40 is
quoted once, for the rank-filter link), Part 1's Minkowski definitions (restated as the starting
point, then proved from), Part 11's Otsu computation (its cut, 40, is used, not re-derived) and its
watershed and h-minima (named as the use of this post's operators), Part 8's Sobel table (quoted for
comparison, not recomputed in prose).
