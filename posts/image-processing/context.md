# Series context — Image Processing by Hand

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** CS students and working engineers who write image code and cannot explain why it
  behaves as it does. Most parts are advanced; Parts 8, 11 and 13 drop to intermediate on purpose.
- **Shape:** hybrid — one L4 hub (Part 1) whose eleven named handoffs become disjoint sibling
  spokes, plus Part 14, whose sole prerequisite is Part 2.
- **Shared promise:** name the stage behind any number, derive what weights do to the signal,
  and predict a library call's output before running it.
- **The "by hand" contract — the defining constraint.** Nothing is executed: no image loaded, no
  notebook run, no package installed. Every number is hand-worked, evaluated from a closed form
  (and captioned so), or cited — no timings, benchmarks or measured curves. Every part states this
  in a `> [!IMPORTANT]` block after the "Level / You need / Time" line.
- **Terminology:** the four stages are **sample, filter, transform, decide**, in that order. A
  filter is *one weighted sum over a neighbourhood*; its numbers are **weights** or the
  **stencil**, never "the mask". Correlation vs convolution is settled in Part 1 and never
  relitigated. Laplacian sign (Part 2): **positive on the dark side of a step**. Positions are
  `(row, column)`, zero-indexed, as `(r2, c1)`.
- **Recurring example:** one 5×5 8-bit patch — every row `40 40 40 200 200` except r2,
  `40 255 40 200 200`: a step between c2 and c3, one impulse of 255 at (r2, c1). Never invent a
  second patch; enlarge or tile this one and say so. Its total is 2,815 (mean 112.6).
- **Shared 3×3 Gaussian:** the sampled σ = 0.8 kernel, 1-D **[0.239, 0.522, 0.239]**, which is what
  `GaussianBlur(img, (3, 3), 0.8)` builds. **It is not OpenCV's sigma-0 default:** with σ ≤ 0 and
  ksize 3–9 OpenCV returns a fixed table, [1 2 1]/4 at ksize 3 (Part 4). 2-D is its outer product
  (centre 0.2725, edge 0.1248, corner 0.0571). **Variance 0.478, not σ² = 0.64** — a truncation
  effect (Part 2). Use 0.478.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | image-processing-by-hand | published | the four-stage frame and the shared arithmetic | eleven areas, named by title in prose and drawn in Figure 17 |
| 2 | laplacian-by-hand | published | one operator and its five uses | gradient-domain editing, to Part 14 |
| 3 | resampling-and-aliasing | gate PASS 2026-09-25, **not published** | which kernel reconstructs; why a shrink needs a prefilter | Parts 4, 5, 13 by title |
| 4 | kernel-design-separability-borders-derivatives | gate PASS 2026-09-25, **not published** | 3×3 derivative family, Gaussian truncation, borders | Parts 7, 10 by title |
| 5 | the-2d-dft-spectra-phase-filtering | gate PASS 2026-10-10, **not published** | 2-D spectrum, phase, notches, FFT crossover, phase correlation | Part 6 by title |
| 6 | wavelets-and-multiresolution | gate PASS 2026-10-11, **not published** | lifting, coefficient budget, JPEG 2000's filters, shift variance, thresholding | nothing (a leaf) |
| 7 | edge-preserving-smoothing | gate PASS 2026-10-11, **not published** | bilateral, NL-means, Perona–Malik on the patch; why contrast cannot separate impulse from edge | learned denoisers out of scope |

Parts 8–14 are `planned`; slugs and scope live in `plan.md`. Add a row when a part passes its gate.

## Knowledge established

### Part 1 — Image Processing by Hand (published)

- **The frame.** Stages 1 and 4 are irreversible, 2 and 3 are not; bugs surface at the decision
  and are caused earlier. Spokes restate it in one sentence at most.
- **Almost every classical operation is one weighted sum**, so the question is what a set of
  weights does to the signal, not *which filter*.
- **Three answers** on the impulse neighbourhood: box → 64, median → 40, σ = 0.8 Gaussian → 98.6
  (OpenCV's sigma-0 default gives 93.75). The standing argument for rank filters.
- **The 67% number:** the impulse moves the Sobel gradient at (r2, c2) 640 → 210; Part 2's
  Laplacian at (r2, c2) goes 160 → 375 (134%). Cite both; re-derive neither.
- **`BGR2GRAY` returns luma, not luminance**; Part 13 owns the account. 30 references by stage.

### Part 2 — The Laplacian by Hand (published)

- **The identity:** a symmetric unit-sum kernel of 1-D variance *v* changes each pixel by
  (v/2)∇²f; the limit is the heat equation ∂L/∂s = ½∇²L (anchor
  `#the-heat-equation-and-the-sharpening-identity`).
- **"The Laplacian" is a family:** OpenCV's `ksize=3` is four times `ksize=1`, on smooth data only.
- **Zero-crossings give sub-pixel position**; as σ grows no zero-crossing is created, and only the
  Gaussian guarantees it (Part 10). Sharpening amplifies noise × (1 + 4c) on the axis.
- **Scale selection:** the normalised Laplacian peaks at σ = 1.5 (bar of width 3) and 2.12 (disc of
  radius 3). Part 10 builds on these.

### Parts 3–6 (built, not published)

- **Part 3:** a shrink by *s* needs the kernel widened by 1/*s*; output j sits at
  x = (j + 0.5)/s − 0.5. Row r2 at 0.6×: linear 111.67/40/200, area 126/115/200, OpenCV nearest
  40/255/200. Keys overshoot 7.4% (a = −1/2), 11.1% (−3/4); OpenCV cubic a = −0.75.
- **Part 4:** every 3×3 first derivative with the obvious symmetries is [p, 1−2p, p]ᵀ ⊗ ½[−1 0 1]
  (central 0, Scharr 3/16, shared Gaussian 0.239, Sobel 1/4). Raw ramp gains: Sobel 8, Scharr 32
  — **Part 8 must normalise before any threshold.** Reflect-101 (OpenCV's default) zeroes the
  normal derivative on the edge column.
- **Part 5:** DC 2,815, floor 215; phase keeps the impulse's position, magnitude-only moves it to
  (0, 0). OpenCV `filter2D` goes to the DFT only at kernel area ≥ 130 (SSE3) or ≥ 50, never
  `sepFilter2D`. Trap: a row-constant image's 2-D spectrum is N× its 1-D one.
- **Part 6:** lifting keeps N numbers and inverts in integers (JPEG 2000's 5/3). One 2-D Haar
  level puts the impulse in four coefficients of 107.5, 25% of its energy each (DFT: 4%). A step
  moved one pixel empties Haar's level-1 detail. Soft λ = 50 takes the edge 160 → 110.

### Part 7 — Edge-Preserving Smoothing (built, not published)

- **Spine:** every method is ŷ = W·y with W built from the data (Milanfar); they differ in what
  "alike" means. Bilateral and Perona–Malik judge contrast, and the impulse (215) is a bigger jump
  than the step (160), so no σr or K keeps the step and drops the impulse. NL-means judges
  repetition (the step's patch repeats down its column, the impulse's nowhere) and can.
- **Bilateral** (shared 3×3, σr = 80): range weights 0.969 (Δ 20), e⁻² = 0.135 (160), 0.027
  (215); impulse 240.5, step 46.5 | 193.5. Mollified with a median copy → 98.6; one robust step
  started from the median → 42.2.
- **NL-means** (3×3 patches, every pixel a candidate, h = 20): the impulse's best matches are four
  flat patches at d² = 5,136. Own patch weight 1 (OpenCV, scikit-image) → 255; IPOL's
  max-of-others rule → 83.0, step exact. h = 80, weight 1: impulse 110.7, step 82.0 | 170.4.
- **Perona–Malik** (g = 1/(1 + (s/80)²), λ = 1/4, adiabatic): g(160) = 0.2, g(215) = 0.122;
  impulse 228.85, 199.19, 165.25; the impulse drains first (four faces) and everything ends at
  112.6. P–M's 90% rule gives K = 160 on the patch; Black's MAD scale gives 0.
- **Library facts:** `cv2.bilateralFilter`'s window is a disc (d = 3 → 5 taps, 5 → 13, 9 → 49);
  OpenCV NL-means zeroes weights below 0.001 (a lone pixel over ~55 above flat surroundings
  survives h = 3); `ximgproc.anisotropicDiffusion` is 8-bit 3-channel with 8 neighbours, so
  alpha ≤ 1/8; scikit-image rescales ints to 0–1 (σr 80 ≈ 0.31; NL-means h 0.1 ≈ 25.5 levels).

## Decisions to preserve

- **No body H1**; ledger keys are HTML comments beside the sentence they support; **British
  spelling** throughout.
- Every part opens with: `> [!NOTE]` Insights, the **Level / You need / Time** line, one line
  placing it in the series, **Jump to:**, then the `> [!IMPORTANT]` block. Every part closes with
  a **tooling map** figure plus tables.
- Figures come from a per-post copy of the toolchain (`_build.py`, `_figs.py`, `_cover.py`,
  `_social.py`, `_overlap.py`); never import across posts; resolve paths from `HERE`. **Start from
  Part 7's**: Axes with `raw=True` labels, `title()`, clipped plot areas, and a 15 s rasteriser
  budget (6 s once rendered a figure in a fallback font). `_figs.py` asserts the article's numbers.
- **Eyebrows uppercase ASCII**, so notation (σr, g(s), h, r2) goes in `mono()`/`title()`, never
  `eyebrow()` or the social `label()`. **No label plates over plotted lines**: put labels in clear
  space. Open every PNG after its last render; font fallback is invisible to every gate.
- Every asset file, `.html` and `.svg` included, carries the slug suffix.
- Pixel cells are **high value = bright** everywhere. The blog cover is unbranded; social cards
  carry the canery.in lockup.
- Earlier parts are named in plain text and listed in the manifest's *Series links to add*; the
  owner adds the links (Parts 1–4 kept canonical URLs).
- Parts 1–2 predate blog-forge 0.4 and warn by design; do not retrofit. Parts 3–7 pass
  `validate_post.py` and `--social` with 0 warnings. The word count includes references and URLs:
  budget L3 prose at about 6,000–6,500.
- Titles stay under 60 characters even when `plan.md`'s is longer.

## Open threads

- **Part 1 misstates OpenCV's default Gaussian** (~line 123 σ = 0.8, ~line 712 expects 99; the
  table gives 93.75). Part 2 (~line 189) credits 0.478 to sampling. Reopens published posts.
- **Part 1's reference 18 links the wrong PDF:** `math.uci.edu/~gpatrick/.../G131.pdf` is
  Guidotti's survey, not Perona & Malik 1990 (at `people.eecs.berkeley.edu/~malik/papers/MP-aniso.pdf`).
- **Part 7 claims, from source read at b700edc, that scikit-image's `denoise_bilateral` reads
  its spatial table at shifted offsets.** Not run; the owner should confirm with one call before
  publishing (manifest has the check) and may report it upstream.
- **Parts 1–2 lack `series` / `series_position` on the live site**; Part 1's Figure 17 lacks the
  Laplacian branch. Both reopen published posts.
- **Parts 3–7 are built but not published:** upload COVER and FIG_ PNGs, `urls.txt`,
  `fill_urls.py`, `--publish`.
- Part 5 cites Oppenheim & Lim by abstract only; Part 6 used T.800's 1999 draft for naming; Part 4
  never attributes a weighting function to Scharr; Part 3's `dsize` rounding at 8.5 is unsettled.
- Part 14 must read as a sibling, not "Part 2, continued". No labs: a spoke wanting one changes an
  invariant and must say so.

## Next part brief

- **Part:** Part 8 (Canny) or Part 10 next. Part 8 follows naturally: Part 4 hands it the
  Sobel/Scharr family, the raw ×8/×32 scales that set its thresholds and the reflect-101 border
  zero; Part 7 hands it the trade its smoothing stage faces (the Gaussian blurs the step to
  78.2 | 161.8, the bilateral keeps the impulse).
- **Can assume** everything under *Knowledge established*; **teach** only that part's `plan.md` row.
- **Must not repeat:** the four-stage frame beyond one sentence, the three answers, the 67%/134%
  results, Part 4's p-family, Part 5's spectrum, Part 6's lifting, Part 7's three methods. Name the
  earlier part in plain text.
- **Evidence:** OpenAlex, Crossref, Scholar, arXiv and (this time) Semantic Scholar answer; HAL,
  MIT DSpace, ITU, ACM and ScienceDirect block; authors' pages rescue most papers. Malik's page has
  Perona & Malik 1990. Part 8 needs Canny 1986 and OpenCV's `Canny` source.
