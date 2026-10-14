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
  mask" (a mask is a binary image, Parts 11–12). Laplacian sign (Part 2): **positive on the dark
  side of a step**. Positions are `(row, column)`, zero-indexed, as `(r2, c1)`.
- **Recurring example:** one 5×5 8-bit patch — every row `40 40 40 200 200` except r2,
  `40 255 40 200 200`: a step between c2 and c3, one impulse of 255 at (r2, c1). Never invent a
  second patch; enlarge or tile this one and say so. Its total is 2,815 (mean 112.6).
- **Shared 3×3 Gaussian:** sampled σ = 0.8, 1-D **[0.239, 0.522, 0.239]**, what
  `GaussianBlur(img, (3, 3), 0.8)` builds on float input — **not** OpenCV's sigma-0 default
  ([1 2 1]/4, Part 4). **Variance 0.478, not σ² = 0.64.** On 8-bit input OpenCV runs it in fixed
  point, [61, 134, 61]/256: two patch pixels give 64 and 90, not 65 and 91 (Part 11).

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | image-processing-by-hand | published | the four-stage frame, the shared arithmetic | eleven areas by title, Figure 17 |
| 2 | laplacian-by-hand | published | one operator, five uses | gradient-domain editing, Part 14 |
| 3 | resampling-and-aliasing | gate PASS 2026-09-25, **not published** | reconstruction kernels, prefiltering | Parts 4, 5, 13 |
| 4 | kernel-design-separability-borders-derivatives | gate PASS 2026-09-25, **not published** | 3×3 derivatives, truncation, borders | Parts 7, 10 |
| 5 | the-2d-dft-spectra-phase-filtering | gate PASS 2026-10-10, **not published** | spectrum, phase, notches, FFT crossover | Part 6 |
| 6 | wavelets-and-multiresolution | gate PASS 2026-10-11, **not published** | lifting, coefficient budget, JPEG 2000 | a leaf |
| 7 | edge-preserving-smoothing | gate PASS 2026-10-11, **not published** | bilateral, NL-means, Perona–Malik | learned denoisers out |
| 8 | canny-line-by-line | gate PASS 2026-10-12, **not published** | suppression, ties, hysteresis, thresholds | Parts 2, 9, 10 |
| 9 | the-structure-tensor | gate PASS 2026-10-12, **not published** | the tensor, corner scores, Lucas–Kanade | Part 10 |
| 10 | scale-space-and-sift | gate PASS 2026-10-13 bar Story checks (feed only, owner's choice), **not published** | σ searched, one DoG octave ×7, SIFT replayed | learned descriptors out |
| 11 | thresholding-and-segmentation | gate PASS 2026-10-14, **not published** | Otsu as 2-means, local windows, three watersheds | markers' operators, Part 12 |
| 12 | mathematical-morphology | gate PASS 2026-10-14, **not published** | the adjunction and its laws, grey by thresholds, sieves, reconstruction, library conventions | markers' use, back to Part 11 |

Parts 13–14 are `planned`; slugs and scope live in `plan.md`. Add a row when a part passes its gate.

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
  Keys overshoot 7.4% (a = −1/2), 11.1% (−3/4).
- **Part 4:** every 3×3 first derivative is [p, 1−2p, p]ᵀ ⊗ ½[−1 0 1] (Scharr 3/16, Sobel 1/4);
  ramp gains Sobel 8, Scharr 32. Reflect-101 zeroes the normal derivative on the edge column.
- **Part 5:** DC 2,815; phase keeps the impulse's position. `filter2D` uses the DFT only at kernel
  area ≥ 130 (SSE3) or ≥ 50, never `sepFilter2D`.
- **Part 6:** lifting keeps N numbers and inverts in integers (5/3); one Haar level puts the impulse in
  four coefficients of 107.5.
- **Part 7:** every method is ŷ = W·y with W from the data. The bilateral at σr = 80 keeps impulse
  and step; NL-means removes the impulse only under IPOL's self-weight rule; Perona–Malik ends at 112.6.

### Parts 8–12 (built, not published)

- **Part 8:** `cv2.Canny` has no smoothing and pads by replicate. Raw Sobel L2: 640 on c2 and c3; the
  impulse's ring 304.1, 430, 476.3, 210. L1 (the default) deletes rows r1 and r3. One-threaded IPP
  builds hand `Canny` to IPP.
- **Part 9:** OpenCV's corner pipeline reads a 5×5 footprint, so no window is flat. **Harris's sign
  is a ratio test** (boundary 0.0436 at k = 0.04). `goodFeaturesToTrack` returns (2, 2).
- **Part 10:** the patch ×7 puts a square of 255 at columns 7–13, rows 14–20. **SIFT's edge test is
  Harris's sign test with k = 10/121.** OpenCV's SIFT reports ×7 at (10.23, 17.25), +0.25 px.
- **Part 11:** histogram 40 ×14, 200 ×10, 255 ×1; raw Otsu 40, smoothed 105. **Otsu is 2-means**,
  right only for two humps of like size and spread. Watershed on Part 8's Sobel table: four minima;
  passes 430 (4-conn) or 304.1 (8-conn), the step 640. `cv2.watershed` sets the frame to −1.
- **Part 12:** the mask X = patch > 40 (bar c3–c4 + speck) is the threshold set for t 41–200 and the
  patch's regional maxima. By the cross, outside ignored: ε 5 px (c4), δ 19, opening 10 (the bar),
  closing 14 (c2 filled in r1–r3); adjunction holds on all pairs (with outside = 0 it fails, 616 of
  20,000). Grey: opening = patch without impulse; gradient 160 at the step, 215 round the impulse;
  white top-hat 215 at (r2, c1). Granulometry 11, 10, 0, 0; the bar's size 1 is a border artefact
  (tiled, the inner bar goes at n = 1). Dynamics: bar 160, impulse 215. **OpenCV's `dilate` is
  unreflected:** a 2×2 `MORPH_CLOSE` loses 5 of 11 (issue #23605); `anchor=(0, 0)` fixes it. SciPy's
  binary border 0 makes closing lose 7. OpenCV's IPP morphology is compiled out (802cf95, 4.10–4.12).

## Decisions to preserve

- **No body H1**; ledger keys are HTML comments beside the sentence they support; **British
  spelling** throughout.
- Every part opens with: `> [!NOTE]` Insights, the **Level / You need / Time** line, one line
  placing it in the series, **Jump to:**, then the `> [!IMPORTANT]` block. Every part closes with
  a **tooling map** figure plus tables.
- Figures come from a per-post copy of the toolchain (`_build.py`, `_figs.py`, `_cover.py`,
  `_social.py`, `_overlap.py`, `_data.py`); never import across posts; resolve paths from `HERE`.
  **Start from Part 12's** (Part 10's base: local font cache when rasterising, `legend2` kinds,
  clipped plots; Part 12 adds `bgrid`/`vgrid`/`elem` cells and `legend4`). `_data.py` asserts every
  article number; it has caught slips in Parts 7, 8, 10 and 12.
- **Eyebrows uppercase ASCII**, so notation goes in `mono()`/`title()`. **No labels over plotted
  lines**; draw reference lines behind bars. Open every PNG after its last render; legends drift
  from their marks.
- Every asset file carries the slug suffix. Pixel cells are **high value = bright**; masks are white
  in the set, dark out, added pixels tinted, removed ones crossed (Part 12). The blog cover is
  unbranded; social cards carry the canery.in lockup.
- Earlier parts are named by title in plain text and listed in the manifest's *Series links to
  add*; later spokes may be named by title because Part 1 published them.
- Parts 1–2 predate blog-forge 0.4 and warn by design; Parts 3–12 pass with 0 warnings (Part 10
  bar its Story checks).
- Titles stay under 60 characters. Write `\lt`/`\gt` in math: the validator strips `<…>` as tags.
- Compute every number a figure prints from the data. SVG collapses spaces: draw matrices as
  positioned cells with opaque fills and crisp edges.

## Open threads

- **Part 1 (published)** misstates OpenCV's default Gaussian (~lines 123, 712; 93.75), the patch's
  histogram (16 and 8; it is 14 and 10) and, in Figure 7's caption, morphology's border value
  (−DBL_MAX only for 64-bit floats; 0 and 255 for 8-bit); its reference 18 links the wrong PDF.
  Part 2 (~line 189) credits 0.478 to sampling. Parts 1–2 lack `series` / `series_position` live;
  Part 1's Figure 17 lacks the Laplacian branch. All reopen published posts.
- **Owner checks before publishing:** Part 7's `denoise_bilateral` offset; Part 8's three `cv2.Canny`
  predictions (and 8-bit rounding with the fixed-point blur); Part 9's five; Part 10's four SIFT;
  Part 11's six; Part 12's six (the 2×2 closing is load-bearing). All in the manifests.
- **Parts 3–12 are built but not published:** upload COVER and FIG_ PNGs, `urls.txt`,
  `fill_urls.py`, `--publish`.
- Not reported upstream: OpenCV's Canny tutorial's Gaussian step; `cornerEigenValsAndVecs`'s
  unsorted eigenvalues; `goodFeaturesToTrack`'s "maxDistance"; scikit-image's SIFT +0.25 px;
  `cv::watershed`'s −1 frame; a second reproduction of OpenCV #23605.
- Part 5 cites Oppenheim & Lim by abstract only; Part 3's `dsize` rounding at 8.5 is unsettled.
- Part 14 must read as a sibling, not "Part 2, continued". No labs: a spoke wanting one changes an
  invariant and must say so.

## Next part brief

- **Part:** Part 13 (colour and gamma: luma, luminance and the spaces in between), L3,
  **intermediate**, the most standalone spoke: it assumes only Part 1's framing and owns the
  `BGR2GRAY`-returns-luma limitation Part 1 states in one paragraph.
- **Worked example:** one sRGB triple through the transfer function to linear light, XYZ and Lab;
  the luma and luminance greys side by side on a saturated colour (the plan quotes both weight
  sets; verify them against the standards, the plan's luminance row has not been checked). For "one blur in both encodings", read the patch's 40 and 200 as sRGB codes and blur the
  step in codes and in linear light: the midpoints differ. Say so in the IMPORTANT block; it is the
  patch read as colour, not a second patch.
- **Can assume** *Knowledge established*; **must not repeat** the four stages beyond one sentence or
  Part 3's resampling. Name earlier parts by title in plain text. L3 counts include references.
- **Evidence:** the standards (IEC 61966-2-1, ITU-R BT.601/709, CIE) may be paywalled: cite the
  constants from open sources that state them and say so. OpenAlex, Crossref, Semantic Scholar and
  Google Scholar answer; author pages and Wayback copies served Parts 11–12. Pin OpenCV and
  scikit-image at a commit and check one release tag; check `cvtColor`'s 8-bit path for HAL/IPP.
