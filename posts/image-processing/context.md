# Series context — Image Processing by Hand

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** CS students and working engineers who write image code and cannot explain why it
  behaves as it does. Most parts are advanced; Parts 8, 11 and 13 drop to intermediate on purpose.
- **Shape:** hybrid — one L4 hub (Part 1) whose eleven named handoffs become disjoint sibling
  spokes, plus Part 14, whose sole prerequisite is Part 2.
- **Shared promise:** name which of four stages produced any number in a pipeline, derive what a
  set of weights does to the signal, and predict a library call's output before running it.
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
  second patch; enlarge or tile this one and say so.
- **Shared 3×3 Gaussian:** the sampled σ = 0.8 kernel, 1-D **[0.239, 0.522, 0.239]**, which is what
  `GaussianBlur(img, (3, 3), 0.8)` builds. **It is not OpenCV's sigma-0 default:** with σ ≤ 0 and
  ksize 3–9 OpenCV returns a fixed table, [1 2 1]/4 at ksize 3 (Part 4; source at bed6800). 2-D:
  centre 0.2725, edge 0.1248, corner 0.0571. **Variance 0.478, not σ² = 0.64** — a truncation
  effect (untruncated σ = 0.8 samples keep 0.6399); using 0.64 makes an unsharp mask 34% too
  strong (Part 2). Use 0.478.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | image-processing-by-hand | published | the four-stage frame and the shared arithmetic | eleven areas, named by title in prose and drawn in Figure 17 |
| 2 | laplacian-by-hand | published | one operator and its five uses | gradient-domain editing, to Part 14 |
| 3 | resampling-and-aliasing | gate PASS 2026-09-25, **not published** | which kernel reconstructs; why a shrink needs a prefilter | Part 4, Part 5 (DFT resize), Part 13 (sRGB), by title only |
| 4 | kernel-design-separability-borders-derivatives | gate PASS 2026-09-25, **not published** | where a kernel's numbers come from: 3×3 derivative family, Gaussian truncation, borders | Part 7 (edge-preserving), Part 10 (scale), by title only |

Parts 5–14 are `planned`; slugs and scope live in `plan.md`. Add a row when a part passes its gate.

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
- **Transfer functions decide behaviour, not names.** Any spoke arguing about a kernel argues from
  its transfer function.
- **`BGR2GRAY` returns luma, not luminance**; Part 13 owns the account.
- **Sources:** 30 references by stage; Parts 5 and 10 can start from that ledger.

### Part 2 — The Laplacian by Hand (published)

- **The identity:** the Laplacian is what Gaussian blur removes per unit of scale. A symmetric
  unit-sum kernel of 1-D variance *v* changes each pixel by (v/2)∇²f; the continuous limit is the
  heat equation ∂L/∂s = ½∇²L. Part 7 enters anisotropic diffusion through this.
- **"The Laplacian" is a family.** OpenCV's `ksize=3` is the diagonal-weighting member at four
  times the scale of `ksize=1`, and the ×4 holds only on smooth data.
- **Zero-crossings give sub-pixel position** (column 2.5 from +160/−160). **Coarse-to-fine**
  (Part 10): Laplacian zero-crossings are never created as σ grows, and only the Gaussian does that.
- **Sharpening's cost:** noise × (1 + 4c) on the axis, × (1 + 8c) on a checkerboard.
- **Scale selection** (closed form): the normalised Laplacian peaks at σ = 1.5 (77.4) for a bar of
  width 3 and σ = 2.12 (117.7) for a disc of radius 3. Part 10 builds on these.

### Part 3 — Resampling and Aliasing (built, not published)

- **Spine:** enlarging is reconstruction, shrinking is filtering; a shrink by *s* needs the kernel
  widened by 1/*s*. Output j sits at x = (j + 0.5)/s − 0.5.
- **Reusable (r2, 0.6×):** linear 111.67/40/200 (mean 117.2); area 126/115/200 (mean **147**);
  OpenCV `INTER_NEAREST` 40/**255**/200.
- **Column-sum audit:** uniform column sums (= s) iff the mean survives.
- **Kernels:** Keys overshoot −4a/27 (7.4% at −1/2, 11.1% at OpenCV's −3/4); Keys(a) ≡ (B, C) =
  (0, −a). Gain at 0.4 cycles/px: Lanczos-3 0.821, Keys 0.716, linear 0.573, stretched triangle
  0.171 — the sharper interpolator is the worse downscaler.
- **Libraries:** OpenCV cubic a = −0.75, exact 0.5× linear → area; Pillow stretches every kernel,
  BICUBIC a = −0.5; SciPy's `prefilter` fits splines, it does not anti-alias.

### Part 4 — Kernel Design (built, not published)

- **Spine:** every 3×3 first derivative with the obvious symmetries is [p, 1−2p, p]ᵀ ⊗ ½[−1 0 1].
  Central difference 0, Scharr 3/16, F–S 3-tap 0.2299, shared Gaussian 0.239, Sobel 1/4,
  Prewitt 1/3. "Optimal" names a criterion.
- **Direction:** direction is exact iff cross-smoothing equals sin ω/ω. p = 1/6 matches to second
  order, 3/16 at 3.45 px, 1/4 at Nyquist. Worst error at 4 px (closed form): central 7.22°, Sobel
  3.24°, Scharr 0.29°, F–S 5-tap 0.17°. Sobel `ksize=5` has the same direction error as 3.
- **Robustness runs the other way:** at (r2, c2), 80 − 107.5(1 − 2p): Sobel 67%, Scharr 84%.
- **Raw ramp gains:** cv2.Sobel 8, Scharr 32, Sobel ksize 5 128, skimage 2 per axis (magnitude
  ÷ √2). **Part 8 must normalise before any threshold.**
- **Truncation:** σ = 2 at 3/5/7/13 taps → effective σ 0.80/1.29/1.64/1.99.
- **Borders:** reflect-101 (OpenCV default) zeroes every normal derivative on the edge column; at
  (r2, c0) constant 73.75, reflect 53.75, reflect-101 0, wrap −26.25. SciPy 'reflect' = OpenCV
  REFLECT = NumPy 'symmetric'.

## Decisions to preserve

- **No body H1**; ledger keys are HTML comments beside the sentence they support; **British
  spelling** throughout.
- Every part opens with: `> [!NOTE]` Insights, the **Level / You need / Time** line, one line
  placing it in the series, **Jump to:**, then the `> [!IMPORTANT]` block. Every part closes with
  a **tooling map** figure plus tables.
- Figures come from a per-post copy of the toolchain (`_build.py`, `_figs.py`, `_cover.py`,
  `_social.py`). Copy the previous part's; never import across posts; resolve paths from `HERE`.
  **Start from Part 4's** (central difference is violet `#8e7aa6`, never Sobel's blue-grey).
- Every asset file, `.html` and `.svg` included, carries the slug suffix.
- Pixel cells are **high value = bright** everywhere. The blog cover is unbranded; social cards
  carry the canery.in lockup.
- Cross-post links use the canonical URL plus a heading anchor, added in the *later* post.
- Parts 1–2 predate blog-forge 0.4 and warn by design; do not retrofit. Parts 3–4 pass
  `validate_post.py` and `--social` with 0 warnings.
- Titles stay under 60 characters even when `plan.md`'s is longer.

## Open threads

- **Part 1 misstates OpenCV's default Gaussian (found by Part 4, not fixed).** Line ~123 says the
  default 3×3 blur has σ = 0.8; line ~712's comment expects `GaussianBlur(patch, (3, 3), 0)[2, 1]`
  to give 99 — the table gives 93.75 (94 in uint8). Fixing it reopens a published post; the
  author decides. Part 2's line ~189 credits the 0.478 to sampling where it is truncation.
- **Parts 1–2 lack `series` / `series_position` on the live site**; owed to the next publish run.
- **Part 1's Figure 17 lacks the Laplacian branch.** Fixing it reopens a published post.
- **Parts 3 and 4 are built but not published:** upload COVER and FIG_ PNGs, `urls.txt`,
  `fill_urls.py`, `--publish`.
- Part 4 could not read Scharr's 1997 paper or 2000 thesis (bot challenges); it never attributes a
  weighting function to Scharr.
- Part 14 must read as a sibling, not "Part 2, continued". No labs: a spoke wanting one changes an
  invariant and must say so.
- Part 3: OpenCV's `dsize` rounding at 5 × 1.7 = 8.5 is unsettled; the post avoids it.

## Next part brief

- **Part:** the plan's order is Part 8 (Canny), then 10, then 5. Part 8 follows naturally: Part 4
  hands it the Sobel/Scharr family, the raw ×8/×32 scales that set Canny's thresholds, and the
  reflect-101 border zero.
- **Can assume:** everything under *Knowledge established*.
- **Must teach:** only what that part's row in `plan.md` owns.
- **Must not repeat:** the four-stage frame beyond one sentence, the three answers, the 67%/134%
  results, correlation vs convolution, Part 3's column sums, Part 4's p-family. Link the anchor.
- **Evidence:** Parts 3–4's ledgers cover kernels, derivative design, Gaussian discretisation and
  OpenCV/SciPy/NumPy/skimage internals at pinned commits. OpenAlex, Crossref, Google Scholar and
  Semantic Scholar answered on 2026-09-25; heiDOK, ResearchGate, Springer and docs.opencv.org served
  bot challenges. Part 8 needs Canny 1986 and OpenCV's implementation notes.
