# Series context — Image Processing by Hand

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** CS students and working engineers who write image code and cannot explain why it
  behaves as it does. Most parts are advanced; Parts 8, 11 and 13 are intermediate on purpose.
- **Shape:** hybrid — one L4 hub (Part 1) whose eleven named handoffs become disjoint sibling
  spokes, plus Part 14, whose sole prerequisite is Part 2.
- **Shared promise:** name the stage behind any number, derive what weights do to the signal,
  and predict a library call's output before running it.
- **The "by hand" contract — the defining constraint.** Nothing is executed: no image loaded, no
  notebook run, no package installed. Every number is hand-worked, evaluated from a closed form
  (and captioned so), or cited — no timings, benchmarks or measured curves. Every part states this
  in a `> [!IMPORTANT]` block after the "Level / You need / Time" line.
- **Terminology:** the four stages are **sample, filter, transform, decide**. A filter is *one
  weighted sum over a neighbourhood*; its numbers are **weights** or the **stencil**, never "the
  mask". Correlation vs convolution is settled in Part 1. Laplacian sign (Part 2): **positive on
  the dark side of a step**. Positions are `(row, column)`, zero-indexed, as `(r2, c1)`.
- **Recurring example:** one 5×5 8-bit patch — every row `40 40 40 200 200` except r2,
  `40 255 40 200 200`: a step between c2 and c3, one impulse of 255 at (r2, c1). Never invent a
  second patch; enlarge or tile this one and say so. Its total is 2,815 (mean 112.6).
- **Shared 3×3 Gaussian:** sampled σ = 0.8, 1-D **[0.239, 0.522, 0.239]**, what
  `GaussianBlur(img, (3, 3), 0.8)` builds — **not** OpenCV's sigma-0 default ([1 2 1]/4 at ksize 3,
  Part 4). 2-D centre 0.2725, edge 0.1248, corner 0.0571. **Variance 0.478, not σ² = 0.64.**

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | image-processing-by-hand | published | the four-stage frame and the shared arithmetic | eleven areas, named by title in prose and drawn in Figure 17 |
| 2 | laplacian-by-hand | published | one operator and its five uses | gradient-domain editing, to Part 14 |
| 3 | resampling-and-aliasing | gate PASS 2026-09-25, **not published** | which kernel reconstructs; why a shrink needs a prefilter | Parts 4, 5, 13 by title |
| 4 | kernel-design-separability-borders-derivatives | gate PASS 2026-09-25, **not published** | 3×3 derivative family, Gaussian truncation, borders | Parts 7, 10 by title |
| 5 | the-2d-dft-spectra-phase-filtering | gate PASS 2026-10-10, **not published** | 2-D spectrum, phase, notches, FFT crossover | Part 6 by title |
| 6 | wavelets-and-multiresolution | gate PASS 2026-10-11, **not published** | lifting, coefficient budget, JPEG 2000's filters | nothing (a leaf) |
| 7 | edge-preserving-smoothing | gate PASS 2026-10-11, **not published** | bilateral, NL-means, Perona–Malik on the patch | learned denoisers out of scope |
| 8 | canny-line-by-line | gate PASS 2026-10-12, **not published** | suppression variants, ties, hysteresis as chains, threshold units, thresholds from noise | zero-crossings to Part 2; junctions to Part 9 and σ to Part 10, by title |

Parts 9–14 are `planned`; slugs and scope live in `plan.md`. Add a row when a part passes its gate.

## Knowledge established

### Parts 1–2 (published)

- **Part 1:** stages 1 and 4 are irreversible, 2 and 3 are not; bugs surface at the decision and
  are caused earlier (restate in one sentence at most). Three answers on the impulse: box 64,
  median 40, σ = 0.8 Gaussian 98.6 (sigma-0 default 93.75). The impulse moves Sobel at (r2, c2)
  640 → 210 (67%); Canny drawn as four steps (Figure 12); L1 reads 45° as 960 against 678.8.
  `BGR2GRAY` returns luma; Part 13 owns it.
- **Part 2:** a symmetric unit-sum kernel of 1-D variance *v* changes each pixel by (v/2)∇²f; the
  limit is the heat equation (anchor `#the-heat-equation-and-the-sharpening-identity`). OpenCV's
  Laplacian `ksize=3` is 4 × `ksize=1` on smooth data. Zero-crossings give sub-pixel position and
  own the coarse-to-fine argument; the normalised Laplacian peaks at σ = 1.5 (bar of 3) and 2.12
  (disc of radius 3), which Part 10 builds on.

### Parts 3–7 (built, not published)

- **Part 3:** a shrink by *s* widens the kernel by 1/*s*; output j sits at x = (j + 0.5)/s − 0.5.
  Keys overshoot 7.4% (a = −1/2), 11.1% (−3/4); OpenCV cubic a = −0.75.
- **Part 4:** every 3×3 first derivative is [p, 1−2p, p]ᵀ ⊗ ½[−1 0 1] (Scharr 3/16, Sobel 1/4).
  Raw ramp gains: Sobel 8, Scharr 32. Reflect-101 (OpenCV's default) zeroes the normal derivative
  on the edge column.
- **Part 5:** DC 2,815; phase keeps the impulse's position. `filter2D` goes to the DFT only at
  kernel area ≥ 130 (SSE3) or ≥ 50, never `sepFilter2D`. A row-constant image's 2-D spectrum is N×
  its 1-D one.
- **Part 6:** lifting keeps N numbers and inverts in integers (5/3). One 2-D Haar level puts the
  impulse in four coefficients of 107.5. Soft λ = 50 takes the edge 160 → 110.
- **Part 7:** every method is ŷ = W·y with W built from the data. Contrast cannot separate the
  impulse (215) from the step (160): the bilateral at σr = 80 keeps both (240.5; 46.5 | 193.5).
  NL-means separates by repetition only under IPOL's self-weight rule (83.0; OpenCV and
  scikit-image keep 255). Perona–Malik ends at the mean, 112.6. The Gaussian takes the step to
  78.2 | 161.8.

### Part 8 — Canny, Line by Line (built, not published)

- **`cv2.Canny` has no smoothing step** and pads by **replicate**, not reflect-101. Raw patch
  Sobel: the step reads 640 on c2 and c3 (a tie); the impulse's own gradient is 0 inside a ring
  (L2 304.1, 430, 476.3, 210); (r2, c0) reads 430 under replicate.
- **Suppression (OpenCV, `canny.simd.hpp`):** four bins at tan 22.5° = 13573/2¹⁵; `>` before and
  `>=` after for H and V, `>` both on diagonals; 0 outside. L2 keeps a 5-pixel line (r0c2, r1c3,
  r2c3, r3c3, r4c2) plus a 5-pixel ring; **L1 (the default) reads (r1, c2) as 640, ties (r1, c3),
  and deletes rows r1 and r3**. Tie rules on 0, 640, 640, 0: strict → 0 pixels, OpenCV → 1 (the
  left), scikit-image (`<=`) → 2.
- **Interpolation** is Canny's own 1983 scheme (via Grompone von Gioi & Randall); scikit-image uses
  it. It differs from OpenCV only after smoothing: at (r1, c1), 222.2 at 62.8°, the bin reads 316.2,
  interpolation 198.8.
- **Hysteresis grades 8-connected chains.** Raw L2: one chain of 10; the line alone needs low ≥ 430
  and high < 640 (ratio < 1.49), so Canny's 2–3 always attaches the ring. After the shared Gaussian:
  column c3 (474.9, 436.5, 408.8) and two isolated 219.7s; (450, 180) returns the line alone.
- **Units:** step 4h / ramp 8 at aperture 3, 48h / 128 at 5, 640h / 2,048 at 7 (stored ÷16).
  Aperture −1 is Scharr. scikit-image thresholds end up in raw-Sobel grey levels after a σ = 1 blur;
  MATLAB uses 0–1, low = 0.4 × high, σ = √2.
- **Thresholds from noise:** Sobel noise √12 σ, magnitude Rayleigh; T_H = s√(2 ln 1/α); α_L =
  α^(1/r²). Desolneux et al.'s a contrario rule with a Rayleigh tail gives μ ∝ 1/√l: ratio 2–3 ↔
  chains of 4–9. Devernay on row r0: 2.5; on r2: 2.90.
- **Library trap:** with one thread, IPP builds hand `Canny` to IPP's own code (unread).

## Decisions to preserve

- **No body H1**; ledger keys are HTML comments beside the sentence they support; **British
  spelling** throughout.
- Every part opens with: `> [!NOTE]` Insights, the **Level / You need / Time** line, one line
  placing it in the series, **Jump to:**, then the `> [!IMPORTANT]` block. Every part closes with
  a **tooling map** figure plus tables.
- Figures come from a per-post copy of the toolchain (`_build.py`, `_figs.py`, `_cover.py`,
  `_social.py`, `_overlap.py`); never import across posts; resolve paths from `HERE`. **Start from
  Part 8's**: `legend2` kinds that draw each swatch like its mark (`area`, `plain`, `outline`,
  `diamond`, `bridge`), clipped plots, a 15 s rasteriser budget. `_figs.py` asserts the article's
  numbers; it caught a rounding slip in Part 8 and two text errors in Part 7.
- **Eyebrows uppercase ASCII**, so notation goes in `mono()`/`title()`. **No labels over plotted
  lines** — check ratio lines, leaders and dashed outlines too. Open every PNG after its last
  render; legends drifted from their marks on six of Part 8's figures.
- Every asset file carries the slug suffix. Pixel cells are **high value = bright** everywhere. The
  blog cover is unbranded; social cards carry the canery.in lockup.
- Earlier parts are named in plain text and listed in the manifest's *Series links to add*; later
  spokes may be named by title because Part 1 published them.
- Parts 1–2 predate blog-forge 0.4 and warn by design. Parts 3–8 pass `validate_post.py` and
  `--social` with 0 warnings. The word count includes references: budget L3 prose at 6,000–6,500.
- Titles stay under 60 characters even when `plan.md`'s is longer.

## Open threads

- **Part 1 misstates OpenCV's default Gaussian** (~line 123, ~line 712; the table gives 93.75), and
  **its reference 18 links the wrong PDF** (Guidotti's survey, not Perona & Malik). Part 2 (~line
  189) credits 0.478 to sampling. Parts 1–2 also lack `series` / `series_position` live, and Part 1's
  Figure 17 lacks the Laplacian branch. All reopen published posts.
- **Owner checks before publishing:** Part 7's scikit-image `denoise_bilateral` table offset (one
  call); Part 8's three `cv2.Canny` predictions (manifest lists them; run with default threading).
- **Parts 3–8 are built but not published:** upload COVER and FIG_ PNGs, `urls.txt`,
  `fill_urls.py`, `--publish`.
- OpenCV's Python Canny tutorial claims a Gaussian step `cv::Canny` lacks; not reported upstream.
- Part 5 cites Oppenheim & Lim by abstract only; Part 6 used T.800's 1999 draft for naming; Part 4
  never attributes a weighting function to Scharr; Part 3's `dsize` rounding at 8.5 is unsettled.
- Part 14 must read as a sibling, not "Part 2, continued". No labs: a spoke wanting one changes an
  invariant and must say so.

## Next part brief

- **Part:** Part 9 (structure tensor) or Part 10 (scale space). Part 9 follows from Part 8's
  junction failure (Li, Sullivan & Baker's false suppression) and reuses its Sobel gradient tables;
  Part 10 inherits Part 2's normalised Laplacian and Part 8's point that σ sets the scale.
- **Can assume** everything under *Knowledge established*; **teach** only that part's `plan.md` row.
- **Must not repeat:** the four-stage frame beyond one sentence, Part 1's three answers and 67%
  result, Part 4's p-family, Part 7's three methods, Part 8's suppression and hysteresis. Name the
  earlier part in plain text.
- **Evidence:** OpenAlex, Crossref, Semantic Scholar and arXiv answer; DBLP (Anubis), HAL, MIT
  DSpace (405), ITU, ACM and ScienceDirect block; Elsevier and Springer abstracts are withheld from
  the APIs. Authors' pages, IPOL and the BMVA archive rescue most papers. Pin OpenCV at a commit and
  check one release tag too.
