# Outline — Image Processing by Hand

**Title:** Image Processing by Hand: Sample, Filter, Transform, Decide (59 chars)
**Slug:** `image-processing-by-hand`
**Tier:** L4 pillar · **Category:** algorithms · **Difficulty:** advanced
**Budget:** 8,750 words (L4 range 7,500–10,000) · **Figures:** 17 (L4 range 12–18)

This is the parent of a series. Every area it names points at a child post and stops
there. Nothing was executed to write it: no packages, no notebook, no measurements.
Every number in the post is either worked by hand in the post or carries a ledger key.

---

## The spine

Four stages, in the order the data moves:

```
sample  →  filter  →  transform  →  decide
```

Two frames run through all four: the image is a **2-D signal**, and almost every
classical operator is a **weighted sum over a neighbourhood**. OpenCV is the lens —
used specifically at the points where its API and the math disagree.

The teaching rule, applied without exception: **numbers first, then the symbol, then
one plain sentence.** No operator appears as notation before it has been evaluated on
real integers.

---

## The shared patch

One 5×5 grayscale patch carries the whole post. Background 40, foreground 200, a
single impulse of 255 at row 2, col 1.

```
        c0   c1   c2   c3   c4
r0      40   40   40  200  200
r1      40   40   40  200  200
r2      40  255   40  200  200
r3      40   40   40  200  200
r4      40   40   40  200  200
```

Every hand-computed value in the post, verified before drafting:

| Quantity | Where | Value |
|---|---|---|
| 3×3 box mean at (2,1) | worked example | 575/9 = 63.9 → **64** |
| 3×3 median at (2,1) | worked example | **40** (impulse removed exactly) |
| 3×3 Gaussian σ=0.8 at (2,1) | worked example | **98.6 → 99** (worse than the box) |
| OpenCV 1-D Gaussian, ksize=3 | filter stage | **[0.239, 0.522, 0.239]** |
| OpenCV 2-D weights σ=0.8 | filter stage | corner 0.0571, edge 0.1248, centre 0.2725 |
| σ from ksize (OpenCV formula) | filter stage | 3→**0.8**, 5→**1.1**, 7→**1.4** |
| Sobel Gx at (2,3), clean edge | detector | **640**, Gy = 0 |
| Sobel Gx at (2,2), impulse present | detector | **210** |
| Sobel Gx at (2,2), impulse removed | detector | **640** — a 67.2% error from one pixel |
| Diagonal variant, Gx, Gy at centre | detector | **480, 480**, θ = 45° |
| L1 vs L2 magnitude, 45° edge | detector | **960 vs 678.8** — L1 overstates by √2 |
| 4-point DFT of [40,40,200,200] | transform | **[480, −160+160i, 0, −160−160i]** |
| Transfer function of [1,2,1]/4 | transform | **H = [1, 0.5, 0, 0.5] = cos²(πk/4)** |
| Filtered row, both routes agree | transform | **[80, 80, 160, 160]** |

The 45° variant is the same step rotated, so the reuse is honest rather than a second
example. The 4-point row is the middle four samples of row 0.

---

## Sections and budget

| # | Section | Words | What the reader can do after it that no other section gives them |
|---|---|---|---|
| 1 | Insights + Who this is for | 260 | Name the four stages and the one operator that spans three of them |
| 2 | Why this matters | 350 | Recognise that a wrong result usually comes from the stage before the one being debugged |
| 3 | The problem | 700 | State precisely what is lost between the scene and the array, and why that is not recoverable |
| 4 | Worked example | 1,310 | Compute a box mean, a median, and a Gaussian on real integers, and say which one to reach for |
| 5 | Intuition | 875 | Say what "a signal" and "detecting a signal" mean as operations, not as metaphors |
| 6 | Stage 1 — Sample: why the grid is already lossy | 520 | Predict when downscaling will produce a wrong pattern, and why the fix must precede the resample |
| 7 | Stage 2 — Filter: every linear filter is one weighted sum | 560 | Write any linear filter as a stencil, factor it into two passes, and choose a border rule |
| 8 | Stage 3 — Transform: what frequency shows that pixels hide | 540 | Read a kernel's transfer function and predict what it keeps |
| 9 | Stage 4 — Decide: where linearity stops | 520 | Tell threshold, rank, and morphological operators apart by what they are ordered on |
| 10 | Stage 5 — Assembling a detector | 520 | Trace Canny end to end and say what each of its four steps contributes |
| 11 | Scale: the parameter nobody sets on purpose | 420 | Name σ as a measurement decision rather than a smoothing knob |
| 12 | The math | 875 | Read the general operator forms and collapse them back onto the patch numbers |
| 13 | Implementation: the tooling map | 700 | Map each piece of math to the exact library call, knowing none of it ran here |
| 14 | Limitations and common mistakes | 440 | Avoid six specific documented traps, each with its symptom |
| 15 | Key takeaways + References | 175 | — |

Total: 8,745.

Body sections are 6 (rows 6–11), the L4 maximum. Rows 9 and 10 are distinct: row 9 is
the taxonomy of non-linear operators, row 10 is how linear and non-linear stages
compose into one detector.

---

## Child posts named, not expanded

Each is named at the point where the frame stops. None is taught here.

| Named in | Child post |
|---|---|
| Stage 1 | Resampling and aliasing: interpolation kernels in practice (S15) |
| Stage 2 | Kernel design: separability, borders, and optimised derivative filters (S22) |
| Stage 3 | The 2-D DFT: spectra, phase, and frequency-domain filtering (S2, S17) |
| Stage 3 | Wavelets and multiresolution, where Fourier stops helping (S21) |
| Stage 4 | Thresholding and segmentation from Otsu to watershed (S6, S20) |
| Stage 4 | Mathematical morphology as lattice algebra (S30) |
| Stage 4 | Edge-preserving smoothing: bilateral, non-local means, anisotropic diffusion (S7, S8, S9) |
| Stage 5 | Canny, line by line: NMS and hysteresis (S3) |
| Stage 5 | The structure tensor: Harris, Shi–Tomasi, and optical flow (S5) |
| Scale | Scale space and SIFT: why σ is a search dimension (S11, S16) |
| Colour | Luma, luminance, and gamma: the colour bug in every pipeline (S23, S29) |
| Decide | Histogram equalisation and CLAHE (S19) |

---

## Figure plan

All 17 are diagrams or math illustrations. No data plots — nothing was measured. The
two figures that show curves (9 and 12) are captioned as models.

| ID | Section | The one thing it must communicate | Route | Draft caption |
|---|---|---|---|---|
| FIG_01 | The problem | The four stages and what is irreversible at each | Mermaid flowchart → diagram-design | The only stage that destroys information is the first one |
| FIG_02 | The problem | A patch is simultaneously a number grid and a sampled surface | diagram-design | Same data twice: the array you index and the signal you reason about |
| FIG_03 | Stage 1 | Sampling replicates the spectrum; overlap is aliasing | hand-authored SVG | The copies overlap before the sample is taken, which is why the fix cannot come after |
| FIG_04 | Worked example | The 3×3 window at the impulse, and the three answers it produces | diagram-design | Box 64, Gaussian 99, median 40 — from the identical nine numbers |
| FIG_05 | Worked example | Three stencils are the same shape holding different weights | diagram-design | Box, Gaussian σ=0.8, and Sobel Gx: one operation, three weight sets |
| FIG_06 | Stage 2 | Separability: one 3×3 pass equals a row pass then a column pass | diagram-design | Nine multiplies become six, and the result is identical |
| FIG_07 | Stage 2 | The five border rules produce five different answers at the same pixel | diagram-design | OpenCV's linear default and its morphology default are not the same rule |
| FIG_08 | Stage 3 | The 4-point step, its DFT, the transfer function, and the product | hand-authored SVG | Two routes to [80, 80, 160, 160]: nine multiplies, or one multiply per frequency |
| FIG_09 | Stage 3 | Box, Gaussian and Laplacian transfer functions on one axis | hand-authored SVG | **A model, not a measurement** — plotted from the closed forms |
| FIG_10 | Stage 5 | Gx and Gy as a vector, and L1 vs L2 as two different lengths | hand-authored SVG | At 45° the default L1 magnitude is √2 times the true one |
| FIG_11 | Stage 5 | Canny as four stages, each from an earlier section | Mermaid flowchart → diagram-design | Three of the four steps are the earlier stages reused |
| FIG_12 | Stage 5 | NMS along the gradient, then two-threshold hysteresis on a profile | hand-authored SVG | **A model profile.** The thin edge is produced by the suppression step, not the gradient |
| FIG_13 | Stage 5 | The λ₁–λ₂ plane: flat, edge, corner, and where k moves the boundary | diagram-design quadrant | The free parameter k is the position of one boundary in this plane |
| FIG_14 | Scale | The scale axis: Gaussian octaves and their differences | diagram-design layers | σ chooses which structures exist, so it is part of the question asked |
| FIG_15 | Stage 4 | The three non-linear families and what each is ordered on | diagram-design nested | Threshold, rank, morphology: all three sort, none of them sums |
| FIG_16 | Implementation | Each stage mapped to the exact NumPy/OpenCV call | diagram-design | The map from math to call site. None of it was executed for this post |
| FIG_17 | Key takeaways | This pillar and the children it hands off to | diagram-design tree | What this post deliberately does not cover |

Plus `COVER`.

---

## Hard constraints carried from the brief

- **Nothing installed, nothing run, nothing persisted.** No timings, no benchmarks, no
  measured curves. FIG_09 and FIG_12 say "model" in the caption.
- **Code is illustrative** and marked as not executed here. The Implementation section
  is a tooling map, not a tutorial.
- **Numbers before symbols**, every time. The general form always arrives after the
  patch has already produced the answer.
- **Every figure is our own redraw.** Caption credits the source of the idea.
- **Both frontmatter schemas in one block** — the nine fields `validate_post.py`
  requires, plus `categories`, `cover_image_url`, `cover_image_alt` for the canery
  parser. `cover_image_url` carries the `COVER` placeholder until `fill_urls.py`
  resolves it, because the platform's contract rejects a non-URL there.
