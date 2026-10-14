# Outline — Thresholding and Segmentation

**Title:** Thresholding and Segmentation: Otsu, Sauvola, Watershed (55 chars; Part 1 published the
spoke's name as *Thresholding and segmentation*, kept at the front, with the three search phrases —
"Otsu", "adaptive thresholding" through Sauvola, "watershed" — after it).
**Slug:** `thresholding-and-segmentation`
**Series:** `image-processing`, part 11 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** intermediate (on purpose, per the plan, like Part 8: no calculus; means, variances and
a histogram are all it needs) · **Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** about 6,800 words as the validator counts them (L3 range 5,000–7,500, references
included) · **Figures:** 10 (L3 range 8–12; the plan estimated 10)
**Assumes:** Part 1, *Image Processing by Hand* — the decide stage (`#stage-4--decide-where-linearity-stops`),
where Otsu's criterion was stated as a search and the patch's criterion called flat; the shared patch
and Gaussian. Part 8, *Canny Edge Detection, Line by Line* — the patch's Sobel magnitudes (the
watershed relief here is that table). Part 7 for the shared Gaussian's float numbers. All named in
plain text; Parts 7 and 8 are built, not live.
**Hands off:** the morphological operators that markers are built from (opening, reconstruction,
h-minima as an operator) to *Mathematical Morphology as Lattice Algebra*, named by title. Learned
segmentation is out of scope, as for the series.

Nothing is run against an image. Every number is worked by hand on the shared patch, or evaluated
from a closed form, and cross-checked with plain Python using only `math`, `heapq` and
`collections` (`assets/_data.py`, which asserts each number the article prints; it is a private
build file and not published). Library behaviour carries a ledger key to source at pinned commits:
OpenCV 802cf95 (and tags 4.10.0, 4.11.0, 4.12.0), scikit-image b700edc (and v0.24.0, v0.25.0),
MathWorks R2026b documentation.

**Checkpoints.** As with Parts 3–10, the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 18 sources (10 peer-reviewed with identifiers, floor 7; four read as abstracts only), six
databases queried (OpenAlex, Crossref, Semantic Scholar, Google Scholar, Unpaywall, Europe PMC; floor
4). Sauvola 2000, Roerdink & Meijster 2000 and Sezgin & Sankur 2004 were read from Wayback Machine
copies of the authors' own pages; Vincent & Soille 1991 from a Mines Paris author page. Kurita 1992,
Kittler & Illingworth 1986, Xu 2011 and Zack 1977 were not readable; their results are cited through
sources that state them. 58 claims. No paper figure is reusable (IEEE, IOS Press, Elsevier copyright).
**B:** this file.

**Seven findings change what the plan expected.**
1. *The patch's own histogram leaves Otsu nothing to decide.* It is three spikes, 14 × 40, 10 × 200,
   1 × 255; every cut from 40 to 199 scores σ_B² = 6,708.24, η = 0.984. Part 1 published the counts
   as 16 and 8 (they are 14 and 10; its conclusion holds) — reported to the owner, not edited. The
   worked example therefore uses the patch after the series' Gaussian, as OpenCV computes it on 8
   bits.
2. *OpenCV's 8-bit GaussianBlur is fixed point.* The σ = 0.8 kernel becomes [61, 134, 61]/256, so two
   values round differently from the float convolution: 64 (64.415, float 64.561) and 90 (90.332,
   float 90.520). The smoothed patch has ten levels; Otsu's best cut is 105 | 162, σ_B² = 2,935.77,
   σ_W² = 434.70, σ_T² = 3,370.47, η = 0.871. The impulse, bright in the raw patch's mask, is dark
   after smoothing.
3. *Three rules, three numbers, one mask.* On the smoothed patch Otsu returns 105, isodata 125, the
   triangle method 160 (scikit-image 161); on the raw patch 40, 122 and 42 (41). The criterion is
   bit-for-bit flat across each gap, so OpenCV's own code returns the gap's first level; IPP builds
   ask IPP, whose tie rule is not public (owner check).
4. *One hot pixel, four regions.* The patch's gradient has four regional minima: two corner pairs, the
   bright column and the impulse itself, whose ring of 304.1–476.3 cuts the dark side's zeros in
   three. Watershed with no markers returns four regions; with two hand-drawn markers, two, split
   between c2 and c3. The impulse's rim is 430 with 4-connectivity and 304.1 with 8-connectivity;
   the step is 640 either way.
5. *`cv2.watershed` floods a different surface.* It takes the colour image, not a gradient, and floods
   by the largest channel difference between 4-neighbours; it overwrites the one-pixel frame with −1
   (markers drawn there vanish); single-pixel markers at (r1, c1) and (r2, c3) let the bright label
   cross the step into the dark bottom row.
6. *Otsu's hidden model is two humps of equal size and spread* (Kurita, via Ershov et al.). In closed
   form: equal humps 0.04% error, as good as possible; spreads 8 against 35, 4.8% against 0.8%
   possible; a 1% object (any object under about 2% for these humps) and the cut jumps into the
   background, 43% wrong. η reads 0.68 both for a 5% object that a cut separates perfectly and for
   two humps that overlap so much 15.9% is the best possible: η measures variance explained, not
   separability.
7. *Local thresholds and the window.* The patch beside a copy at a fifth of the light (8 | 40 | 51)
   makes 40 mean dark in one tile and bright in the other: no global cut works (Otsu's 51 gets 10
   pixels wrong). Mean − C, Niblack and Sauvola all fail at window 3 (flat windows), all work at 5
   and 7, and OpenCV's mean − C fails again at 9, when the window reaches the other tile's light.
   The article teaches window 7: at 5, Sauvola is right at c0 only because the impulse is in its
   window, which never reaches the step (5 errors without the impulse).

---

## The spine

A threshold is a two-class decision made from the histogram alone, so it can only work when the
classes do not overlap in grey level. Otsu's method is 2-means on the histogram, solved by trying
every cut: it is the best cut when the histogram is two humps of similar size and spread, and it says
nothing useful when they are not. When shading makes the same value mean different things in
different places, the decision has to be local, with a window bigger than the objects and smaller than
the shading. When objects touch at the same grey level, no histogram separates them, and the decision
moves to space: flood the gradient from markers, because every unmarked minimum would otherwise become
a region.

## Verified numbers (all asserted in `assets/_data.py`)

**Raw patch:** histogram 40 ×14, 200 ×10, 255 ×1; mean 112.6, σ_T² 6,818.24. Cut 40 | 200: σ_B²
6,708.24, σ_W² 110.0, η 0.984; cut 200 | 255: σ_B² 844.9, η 0.124. Otsu (OpenCV own code, scikit-image)
40; isodata 122; triangle 42 (OpenCV), 41 (scikit-image). Mask: 11 bright, the impulse one of them.
**Smoothed (OpenCV 8-bit):** r0 40 40 78 162 200; r1 64 67 90 162 200; r2 94 99 105 162 200; r3 = r1;
r4 = r0. Histogram 40 ×4, 64 ×2, 67 ×2, 78 ×2, 90 ×2, 94, 99, 105, 162 ×5, 200 ×5. Mean 114.64,
σ_T² 3,370.47. σ_B² over the nine cuts: 1,061.2, 1,402.4, 1,802.5, 2,153.9, 2,445.7, 2,611.9,
2,777.0, 2,935.8, 1,821.6. Best 105 | 162: 15 | 10 pixels, μ0 70.4, μ1 181.0, σ_W² 434.7, η 0.871.
Otsu 105 (flat to 161), isodata 125, triangle 160 (161). Mask: c3 and c4 only.
**Relief (Sobel L2, replicate border = Part 8's table):** r0 0 0 640 640 0; r1 304.1 430 476.3 640 0;
r2 430 0 210 640 0. Minima (4- and 8-connected alike): {(0,0),(0,1)}, column c4, {(2,1)},
{(4,0),(4,1)}. Passes: dark trio 430 (4-conn), 304.1 (8-conn); dark to bright 640. No markers: four
regions; (0,0) and (2,4) as markers: c0–c2 | c3–c4, flood levels 0, 304.1, 430, 476.3, 640.
h-minima (8-conn): four minima below 304.1, two from 304.1 to below 640, one from 640.
**OpenCV watershed:** markers on the frame → nothing labelled; (1,1)=1, (2,3)=2 → interior r1 1 1 −1,
r2 −1 −1 2, r3 2 2 2; strokes c1 and c3 → −1 line on c2.
**Two lights:** 8 ×14, 40 ×24, 51, 200 ×10, 255; Otsu 51, 10 errors. Window 3: mean − C 5, Niblack 5,
Sauvola 8 errors; 5 and 7: none (Sauvola at 5 by luck, see finding 7); 9: mean − C 5, Sauvola 0.
**Closed forms (σ 15, means 70 and 170 unless stated):** equal: Otsu 120, best 119, 0.04%, η 0.918;
99:1: Otsu 72, best 130, 43% against 0.01%, η 0.51; spreads 8 and 35: Otsu 124, best 92, 4.8% against
0.8%; overlap (means 100 and 150, σ 25): 125, 15.9% for both, η 0.68; 5% object: η 0.68, cut fine.
Flip below a 2.0% object. Three humps: two equal maxima, 112 and 143. Best error for equal humps
d apart: 15.9% at 2σ, 6.7% at 3σ, 2.3% at 4σ, 1.0% at 4.65σ, 0.1% at 6σ.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + jump + IMPORTANT | 290 | — |
| Why this matters | 160 | — |
| The problem | 330 | — |
| Worked example: the raw histogram; smooth; every cut; the same answer; three numbers one mask; flood from markers; over-segment on purpose | 1,150 | FIG_01–FIG_05 |
| Intuition: 2-means, and a landscape with lakes | 330 | — |
| What does the histogram have to look like? | 650 | FIG_06 |
| What if the light changes across the image? | 520 | FIG_07 |
| What does each library's watershed actually flood? | 430 | FIG_08 |
| Why does watershed over-segment, and where do markers come from? | 450 | FIG_09 |
| The math | 430 | — |
| Implementation: the tooling map | 450 | FIG_10 |
| Limitations and common mistakes | 300 | — |
| Key takeaways | 120 | — |
| Try it yourself (E1–E4) | 450 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | the raw patch's three spikes give a flat criterion from 40 to 199; the smoothed patch's ten levels give one peak, the cut between 105 and 162 | plot | the criterion evaluated from the definition over two real histograms |
| 02 | Worked example | at every cut σ_B² + σ_W² is the same 3,370.47, so the tallest σ_B² is the shortest σ_W² | chart | Q1 — nine values computed from the histogram, drawn as stacked bars on one scale |
| 03 | Worked example | Otsu 105, isodata 125, triangle 160 land in the same empty gap and draw one mask; the raw patch's mask keeps the impulse | placed | Q4 — real grids and a histogram axis side by side |
| 04 | Worked example | flooding from two hand markers: the levels 0, 304.1, 430, 476.3, 640, ending in two regions split at the step | placed | Q4 — small multiples of a real 5×5 grid |
| 05 | Worked example | four regional minima become four regions; with 8-connectivity the shapes change, the count does not | placed | Q4 — small multiples of real grids |
| 06 | Histogram shapes | four closed-form histograms with Otsu's cut, the best cut, the errors and η | plot | closed-form mixture densities and criteria |
| 07 | Local thresholds | one row through both lights: Otsu's one cut against local thresholds at windows 3, 7 and 9 | plot | thresholds evaluated from the definitions on the two-light tiling |
| 08 | Library watersheds | `cv2.watershed` on the patch: the −1 frame erases border markers, single pixels leak, strokes work | placed | Q4 — small multiples of real grids |
| 09 | Markers | the basins' merge tree: three dark basins join at 304.1 (8-conn) or 430 (4-conn), the dark and bright at 640; where h cuts it | placed | Q5 — a four-leaf tree, under nine nodes, no crossings |
| 10 | Implementation | OpenCV, scikit-image, MATLAB: Otsu's return value, ties, local methods, what watershed floods, connectivity, lines, markers, defaults | placed | Q5 — a comparison grid with no edges, the series' closing tooling map |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| histogram; grey level | Problem | count of pixels at each value | all a global threshold sees | always |
| threshold; binarisation; `>` convention | Problem | a point operation, value against a constant | the simplest decision | two classes |
| segmentation; region | Problem | partition of the image into connected parts | what thresholding approximates | many objects |
| class; between-, within-, total variance | Worked example | spread of the two classes' grey levels | Otsu's criterion | every cut |
| Otsu's method; η | Worked example | the cut maximising between-class variance; its share of the total | automatic threshold; a score | global thresholding |
| isodata (Ridler–Calvard); triangle method | Worked example | midpoint of class means; distance below a peak-to-tail line | other global rules | unimodal or skewed histograms |
| gradient magnitude as relief | Worked example | the Sobel length, read as height | what watershed floods | segmentation by edges |
| regional minimum; catchment basin; watershed line | Worked example | a flat area with only higher neighbours; the area draining to it; the divide | the units of a watershed | every watershed call |
| marker; over-segmentation | Worked example | a pixel set declared to belong to one region; too many regions | control the count | real images |
| flooding; priority queue; age | Worked example | process pixels lowest first, ties by arrival | how libraries implement it | reading results |
| k-means | Intuition | iterate means and assignments | Otsu is its global version | multi-class |
| mixture model; minimum error; Bayes error | Histogram shapes | two humps as weighted Gaussians; the least possible misclassification | what Otsu assumes | choosing a method |
| Kittler–Illingworth | Histogram shapes | minimum-error fit with unequal variances | unequal spreads | skewed classes |
| multi-level Otsu | Histogram shapes | several cuts at once | three or more humps | trimodal images |
| local (adaptive) threshold; window; mean − C; Niblack; Sauvola | Local thresholds | a threshold per pixel from its neighbourhood | shading | documents, uneven light |
| connectivity (4, 8) | Library watersheds | which neighbours count | changes passes and lines | every call |
| pass; dynamics; h-minima | Markers | lowest rim between basins; its height; removing minima shallower than h | marker-free control | noisy gradients |
| distance transform | Markers | distance of each foreground pixel to the background | markers for touching blobs | binary objects |

## Not repeated from earlier parts

The four-stage frame (one sentence), Part 1's three answers on the impulse and its 67% result, Part
1's statement of Otsu's formula (restated in the math section only as the start of the derivation),
Part 7's three methods (the shared Gaussian's numbers are used, not re-derived), Part 8's hysteresis
and its Sobel table (used as the relief, cited), Part 10's scale search.
