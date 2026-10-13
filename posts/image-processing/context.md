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
| 9 | the-structure-tensor | gate PASS 2026-10-12, **not published** | the tensor on the patch, scores as functions of λ1, λ2, orientation, Lucas–Kanade on the same matrix | scale half of Harris–Laplace to Part 10, by title |
| 10 | scale-space-and-sift | gate PASS 2026-10-13 bar the Story checks (feed cards only, owner's choice), **not published** | σ searched not set, the Gaussian's uniqueness and its conditions, one DoG octave on the patch ×7, OpenCV's SIFT replayed | learned descriptors out of scope |

Parts 11–14 are `planned`; slugs and scope live in `plan.md`. Add a row when a part passes its gate.

## Knowledge established

### Parts 1–2 (published)

- **Part 1:** stages 1 and 4 are irreversible, 2 and 3 are not (restate in one sentence at most).
  Three answers on the impulse: box 64, median 40, σ = 0.8 Gaussian 98.6 (sigma-0 default 93.75).
  The impulse moves Sobel at (r2, c2) 640 → 210 (67%). `BGR2GRAY` returns luma; Part 13 owns it.
- **Part 2:** a unit-sum kernel of 1-D variance *v* changes each pixel by (v/2)∇²f; the limit is the
  heat equation (`#the-heat-equation-and-the-sharpening-identity`). Zero-crossings own the
  coarse-to-fine argument; scale selection is `#scale-selection-the-laplacian-as-a-ruler`.

### Parts 3–7 (built, not published)

- **Part 3:** a shrink by *s* widens the kernel by 1/*s*; output j sits at x = (j + 0.5)/s − 0.5.
  Keys overshoot 7.4% (a = −1/2), 11.1% (−3/4); OpenCV cubic a = −0.75.
- **Part 4:** every 3×3 first derivative is [p, 1−2p, p]ᵀ ⊗ ½[−1 0 1] (Scharr 3/16, Sobel 1/4).
  Raw ramp gains: Sobel 8, Scharr 32. Reflect-101 (OpenCV's default) zeroes the normal derivative
  on the edge column.
- **Part 5:** DC 2,815; phase keeps the impulse's position. `filter2D` goes to the DFT only at
  kernel area ≥ 130 (SSE3) or ≥ 50, never `sepFilter2D`.
- **Part 6:** lifting keeps N numbers and inverts in integers (5/3). One 2-D Haar level puts the
  impulse in four coefficients of 107.5. Soft λ = 50 takes the edge 160 → 110.
- **Part 7:** every method is ŷ = W·y with W built from the data. The bilateral at σr = 80 keeps
  impulse and step (240.5; 46.5 | 193.5); NL-means removes the impulse only under IPOL's self-weight
  rule (83.0); Perona–Malik ends at the mean, 112.6.

### Parts 8–9 (built, not published)

- **Part 8:** `cv2.Canny` has no smoothing step and pads by replicate. Raw Sobel: the step reads 640
  on c2 and c3 (a tie); the impulse's ring L2 304.1, 430, 476.3, 210. Suppression bins at tan 22.5°,
  `>` before and `>=` after on H/V; L1 (the default) deletes rows r1 and r3. Ties on 0, 640, 640, 0:
  strict 0, OpenCV 1, scikit-image 2. Hysteresis grades 8-connected chains. Units: step 4h at
  aperture 3, 48h at 5, 640h at 7. One-threaded IPP builds hand `Canny` to IPP.
- **Part 9:** OpenCV's corner pipeline is Sobel 3×3 in an unnormalised 3×3 box, reflect-101, each
  derivative ÷ 2^(ksize−1)·blockSize·255; the footprint is 5×5, so no window is flat. Row r2 is
  diagonal: c2 (1,634,150, 462,250), c4 (2,457,600, 0). **Harris's sign is a ratio test:** R > 0 iff
  t/(1+t)² > k; boundaries 0.0436 (0.04), 0.0685 (0.06); (r2, c3), t = 0.057, flips.
  `goodFeaturesToTrack` scans 1..N−2 and returns (2, 2). Lucas–Kanade at c4: v is free.

### Part 10 — Scale Space and SIFT (built, not published)

- **The patch ×7** (35×35, coordinates (x, y) as OpenCV reports): square of 255 in columns 7–13,
  rows 14–20, centre (10, 17); step between columns 20 and 21. Its scale space is a closed form in
  Φ. Octave σ = 1.6·2^(i/3); DoG at the centre −21.86, −32.22, −35.38, −31.42, −23.12.
- **Two candidates:** (10, 17) on level 2, −35.379; fit offset (−0.0193, 0, −0.0554), σ 2.508,
  0.139 on 0–1, edge test 4.0004, kept. (17, 17), +14.740 between square and step: 23.2 > 12.1,
  rejected. **The edge test is Harris's sign test with k = 10/121 = 0.0826.**
- **Fixed σ fails:** the same DoG level on ×14 gives four corner wells (−20.43), centre −9.66; at
  2σ, ×14 equals ×7 exactly. DoG ≈ LoG at σ/√k (2.48 against 2.776).
- **"Only the Gaussian"** holds under non-enhancement or separability; the Poisson kernel passes
  the rest. In 2-D even the Gaussian creates extremum–saddle pairs.
- **OpenCV SIFT (802cf95, 4.10.0), replayed:** the 5×5 patch gives nothing (5-px border). ×7 default
  (10.23, 17.25), size 5.02: resize's +0.25 px (issue #23123 open; `enable_precise_upscale` since
  4.8.0, off by default). Precise (9.98, 17.00), size 5.03, three orientations. size = 2σ.
  MATLAB `Scale` = σ; `blob_log` radius √2σ.

## Decisions to preserve

- **No body H1**; ledger keys are HTML comments beside the sentence they support; **British
  spelling** throughout.
- Every part opens with: `> [!NOTE]` Insights, the **Level / You need / Time** line, one line
  placing it in the series, **Jump to:**, then the `> [!IMPORTANT]` block. Every part closes with
  a **tooling map** figure plus tables.
- Figures come from a per-post copy of the toolchain (`_build.py`, `_figs.py`, `_cover.py`,
  `_social.py`, `_overlap.py`); never import across posts; resolve paths from `HERE`. **Start from
  Part 10's**: it inlines the local font cache (`~/.cache/blog-forge-fonts/fonts.local.css`) when
  rasterising, and keeps Part 8's `legend2` kinds and clipped plots. A `_data.py` or `_figs.py`
  asserts the article's numbers; it has caught slips in Parts 7, 8 and 10.
- **Eyebrows uppercase ASCII**, so notation goes in `mono()`/`title()`. **No labels over plotted
  lines** — check ratio lines, leaders and dashed outlines too. Open every PNG after its last
  render; legends drifted from their marks on six of Part 8's figures.
- Every asset file carries the slug suffix. Pixel cells are **high value = bright** everywhere. The
  blog cover is unbranded; social cards carry the canery.in lockup.
- Earlier parts are named in plain text and listed in the manifest's *Series links to add*; later
  spokes may be named by title because Part 1 published them.
- Parts 1–2 predate blog-forge 0.4 and warn by design; Parts 3–9 pass with 0 warnings.
- Titles stay under 60 characters even when `plan.md`'s is longer. Write `\lt`/`\gt` in math: the
  validator's word count strips `<…>` as tags.
- Compute every number a figure prints from the data. SVG collapses spaces: draw matrices as
  positioned cells. Shaded grids need opaque fills and crisp edges, or seams show.

## Open threads

- **Part 1 misstates OpenCV's default Gaussian** (~line 123, ~line 712; the table gives 93.75), and
  **its reference 18 links the wrong PDF** (Guidotti's survey, not Perona & Malik). Part 2 (~line
  189) credits 0.478 to sampling. Parts 1–2 also lack `series` / `series_position` live, and Part 1's
  Figure 17 lacks the Laplacian branch. All reopen published posts.
- **Owner checks before publishing:** Part 7's scikit-image `denoise_bilateral` table offset (one
  call); Part 8's three `cv2.Canny` predictions (default threading); Part 9's five corner and
  `goodFeaturesToTrack` predictions; Part 10's four SIFT predictions. All listed in the manifests.
- **Parts 3–10 are built but not published:** upload COVER and FIG_ PNGs, `urls.txt`,
  `fill_urls.py`, `--publish`.
- Not reported upstream: OpenCV's Python Canny tutorial claims a Gaussian step `cv::Canny` lacks;
  `cornerEigenValsAndVecs` documents unsorted eigenvalues; `goodFeaturesToTrack` says "maxDistance"; scikit-image's SIFT +0.25 px (by code).
- Part 10 ships feed cards only (owner's choice, 2026-10-13); `--social` fails only on Story checks.
- Part 5 cites Oppenheim & Lim by abstract only; Part 3's `dsize` rounding at 8.5 is unsettled.
- Part 14 must read as a sibling, not "Part 2, continued". No labs: a spoke wanting one changes an
  invariant and must say so.

## Next part brief

- **Part:** Part 11 (thresholding and segmentation), L3 and **intermediate on purpose**, like Part 8.
  It inherits Part 1's decide stage (`#stage-4--decide-where-linearity-stops`) and nothing else.
  The patch's histogram is 40 ×14, 200 ×10, 255 ×1 (total 2,815).
- **Can assume** everything under *Knowledge established*; **teach** only that part's `plan.md` row.
  Part 12 owns the morphological operators that watershed's markers come from; name it by title.
- **Must not repeat:** the four-stage frame beyond one sentence, Part 1's three answers and 67%
  result, Part 7's three methods, Part 8's hysteresis, Part 10's scale search. Name the earlier part
  in plain text. Budget L3 prose at 6,000–6,500 (the count includes references).
- **Evidence:** OpenAlex (title.search), Crossref, Semantic Scholar (citations; search often 429),
  arXiv (https only) and Google Scholar answer; DBLP, HAL, MIT DSpace, ITU, ACM, ScienceDirect and
  Cornell eCommons block; Springer shows a bot wall (cite via Scholarpedia or authors' pages). IPOL,
  the BMVA archive, authors' pages (KTH serves Lindeberg's reports) and course copies rescue most
  papers. Pin OpenCV at a commit and check one release tag too.
