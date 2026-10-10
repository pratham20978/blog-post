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
  second patch; enlarge or tile this one and say so.
- **Shared 3×3 Gaussian:** the sampled σ = 0.8 kernel, 1-D **[0.239, 0.522, 0.239]**, which is what
  `GaussianBlur(img, (3, 3), 0.8)` builds. **It is not OpenCV's sigma-0 default:** with σ ≤ 0 and
  ksize 3–9 OpenCV returns a fixed table, [1 2 1]/4 at ksize 3 (Part 4; source at bed6800). 2-D is
  its outer product. **Variance 0.478, not σ² = 0.64** — a truncation effect; using 0.64 makes an
  unsharp mask 34% too strong (Part 2). Use 0.478.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | image-processing-by-hand | published | the four-stage frame and the shared arithmetic | eleven areas, named by title in prose and drawn in Figure 17 |
| 2 | laplacian-by-hand | published | one operator and its five uses | gradient-domain editing, to Part 14 |
| 3 | resampling-and-aliasing | gate PASS 2026-09-25, **not published** | which kernel reconstructs; why a shrink needs a prefilter | Part 4, Part 5 (DFT resize), Part 13 (sRGB), by title only |
| 4 | kernel-design-separability-borders-derivatives | gate PASS 2026-09-25, **not published** | where a kernel's numbers come from: 3×3 derivative family, Gaussian truncation, borders | Part 7 (edge-preserving), Part 10 (scale), by title only |
| 5 | the-2d-dft-spectra-phase-filtering | gate PASS 2026-10-10, **not published** | what a 2-D spectrum shows, what phase holds, notches, the FFT crossover, phase correlation | *Wavelets and Multiresolution* (local structure), by title only |
| 6 | wavelets-and-multiresolution | gate PASS 2026-10-11, **not published** | lifting by hand, the coefficient budget, JPEG 2000's two filters, shift variance, thresholding | nothing (a leaf) |

Parts 7–14 are `planned`; slugs and scope live in `plan.md`. Add a row when a part passes its gate.

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
- **Sources:** 30 references by stage; Part 10 can start from that ledger.

### Part 2 — The Laplacian by Hand (published)

- **The identity:** a symmetric unit-sum kernel of 1-D variance *v* changes each pixel by
  (v/2)∇²f; the limit is the heat equation ∂L/∂s = ½∇²L. Part 7 enters diffusion through this.
- **"The Laplacian" is a family:** OpenCV's `ksize=3` is four times `ksize=1`, on smooth data only.
- **Zero-crossings give sub-pixel position** (column 2.5 from +160/−160). **Coarse-to-fine**
  (Part 10): as σ grows no zero-crossing is created, and only the Gaussian guarantees it.
- **Sharpening's cost:** noise × (1 + 4c) on the axis, × (1 + 8c) on a checkerboard.
- **Scale selection** (closed form): the normalised Laplacian peaks at σ = 1.5 (77.4) for a bar of
  width 3 and σ = 2.12 (117.7) for a disc of radius 3. Part 10 builds on these.

### Part 3 — Resampling and Aliasing (built, not published)

- **Spine:** enlarging is reconstruction, shrinking is filtering; a shrink by *s* needs the kernel
  widened by 1/*s*. Output j sits at x = (j + 0.5)/s − 0.5.
- **Reusable (r2, 0.6×):** linear 111.67/40/200 (mean 117.2); area 126/115/200 (mean **147**);
  OpenCV `INTER_NEAREST` 40/**255**/200.
- **Column-sum audit:** uniform column sums (= s) iff the mean survives.
- **Kernels:** Keys overshoot −4a/27 (7.4% at −1/2, 11.1% at −3/4). Gain at 0.4 cycles/px:
  Lanczos-3 0.821, Keys 0.716, linear 0.573 — the sharper interpolator is the worse downscaler.
- **Libraries:** OpenCV cubic a = −0.75; Pillow stretches every kernel (BICUBIC a = −0.5); SciPy's
  `prefilter` fits splines and does not anti-alias.

### Part 4 — Kernel Design (built, not published)

- **Spine:** every 3×3 first derivative with the obvious symmetries is [p, 1−2p, p]ᵀ ⊗ ½[−1 0 1].
  Central difference 0, Scharr 3/16, F–S 3-tap 0.2299, shared Gaussian 0.239, Sobel 1/4,
  Prewitt 1/3. "Optimal" names a criterion.
- **Direction:** exact iff cross-smoothing equals sin ω/ω. Worst error at 4 px: central 7.22°,
  Sobel 3.24°, Scharr 0.29°, F–S 5-tap 0.17°; Sobel `ksize=5` errs as 3 does.
- **Robustness runs the other way:** at (r2, c2), 80 − 107.5(1 − 2p): Sobel 67%, Scharr 84%.
- **Raw ramp gains:** cv2.Sobel 8, Scharr 32, Sobel ksize 5 128, skimage 2 per axis (magnitude
  ÷ √2). **Part 8 must normalise before any threshold.**
- **Truncation:** σ = 2 at 3/5/7/13 taps → effective σ 0.80/1.29/1.64/1.99.
- **Borders:** reflect-101 (OpenCV default) zeroes every normal derivative on the edge column; at
  (r2, c0) constant 73.75, reflect 53.75, reflect-101 0, wrap −26.25. SciPy 'reflect' = OpenCV
  REFLECT = NumPy 'symmetric'.

### Part 5 — The 2-D DFT (built, not published)

- **Spectrum by hand:** F = 5S(kc)[kr = 0] + 215·w^(2kr + kc): DC 2,815; row 1,079.43, 709.43;
  floor exactly 215. Energy 65.0/27.4/7.6%.
- **Phase keeps position:** phase-only keeps the impulse at (2, 1) (0.840); magnitude-only moves
  it to (0, 0) (427.71).
- **Swap with the transpose:** positions follow the phase, the bar's orientation the magnitude;
  photographs share ~1/f magnitude, so there phase wins (the post's reasoning).
- **Notch:** on-bin interference (spikes of 1,000 where the tile is empty) is removed exactly; at
  2.5 cycles rms 14.14 → 10.78 / 13.43 / 17.43, and the 2-D column is 10× the 1-D.
- **Crossover:** G&W 7×7; arithmetic ~10×10 full, ~45 taps separable; OpenCV filter2D DFT only
  at kernel area ≥ 130 (SSE3) or ≥ 50, never sepFilter2D; SciPy's model 3×3.
- **Traps:** fftshift twice on odd n → f·cos(72°(r + c)); ideal low-pass dips to 0.45; phase
  correlation is an exact delta. Part 3's DFT resize is covered (2× zero-pad overshoots to 247.1).

### Part 6 — Wavelets and Multiresolution (built, not published)

- **Lifting** keeps N numbers and, rounding inside each step, inverts in integers (JPEG 2000's
  5/3). Row r0: Haar d 0/160, s 40/120/200; 5/3 d 0/80, s 40/60/240. Row r2: s 148/114/240.
- **2-D Haar** (PyWavelets pads to 6×6, 36 numbers): impulse → 107.5 per subband, 25% of its
  energy each (DFT: 4%); the step → one HL column of −160. Pyramid 4/3 in 2-D, 2 in 1-D.
- **Shift:** a step moved a pixel → Haar d 0, 5/3 keeps |80|; an impulse at an even column halves
  the 5/3's detail energy.
- **Names:** JPEG 2000 HL = PyWavelets `cV`, LH = `cH`; PyWavelets `symmetric` is half-sample,
  JPEG 2000's mirror is `reflect`. Soft λ = 50 on the patch: edge 160 → 110, impulse → 180.

## Decisions to preserve

- **No body H1**; ledger keys are HTML comments beside the sentence they support; **British
  spelling** throughout.
- Every part opens with: `> [!NOTE]` Insights, the **Level / You need / Time** line, one line
  placing it in the series, **Jump to:**, then the `> [!IMPORTANT]` block. Every part closes with
  a **tooling map** figure plus tables.
- Figures come from a per-post copy of the toolchain (`_build.py`, `_figs.py`, `_cover.py`,
  `_social.py`); never import across posts; resolve paths from `HERE`.
  **Start from Part 6's**: Part 5's `legend2` and `_overlap.py`, plus lifting-ladder lanes and
  pair-aligned social cells; central difference stays violet `#8e7aa6`.
- Every asset file, `.html` and `.svg` included, carries the slug suffix.
- Pixel cells are **high value = bright** everywhere. The blog cover is unbranded; social cards
  carry the canery.in lockup.
- Earlier parts are named in plain text and listed in the manifest's *Series links to add*; the
  owner adds the links (Parts 1–4 kept canonical URLs).
- Parts 1–2 predate blog-forge 0.4 and warn by design; do not retrofit. Parts 3–6 pass
  `validate_post.py` and `--social` with 0 warnings. The word count includes references and URLs:
  budget L3 prose at about 6,500.
- Titles stay under 60 characters even when `plan.md`'s is longer.

## Open threads

- **Part 1 misstates OpenCV's default Gaussian (found by Part 4, not fixed):** ~line 123 says
  σ = 0.8 and ~line 712 expects 99 at (2, 1); the table gives 93.75. Part 2 (~line 189) credits the
  0.478 to sampling, not truncation. Both reopen published posts; the author decides.
- **Parts 1–2 lack `series` / `series_position` on the live site**; owed to the next publish run.
- **Part 1's Figure 17 lacks the Laplacian branch.** Fixing it reopens a published post.
- **Parts 3–6 are built but not published:** upload COVER and FIG_ PNGs, `urls.txt`,
  `fill_urls.py`, `--publish`.
- Part 5 cites Oppenheim & Lim 1981 by abstract only; Part 6 used T.800's 1999 draft for naming
  only (ITU firewall).
- Part 4 never attributes a weighting function to Scharr (his papers were unreachable).
- Part 14 must read as a sibling, not "Part 2, continued". No labs: a spoke wanting one changes an
  invariant and must say so.
- Part 3: OpenCV's `dsize` rounding at 5 × 1.7 = 8.5 is unsettled; the post avoids it.

## Next part brief

- **Part:** Part 8 (Canny) or Part 10 next. Part 8 follows naturally: Part 4 hands it the
  Sobel/Scharr family, the raw ×8/×32 scales that set Canny's thresholds, and the reflect-101
  border zero.
- **Can assume** everything under *Knowledge established*; **teach** only that part's `plan.md` row.
- **Must not repeat:** the four-stage frame beyond one sentence, the three answers, the 67%/134%
  results, correlation vs convolution, Part 3's column sums, Part 4's p-family, Part 5's spectrum
  and swap, Part 6's lifting. Name the earlier part in plain text.
- **Evidence:** Parts 3–6's ledgers cover kernels, Gaussians, the 2-D DFT, wavelets and library
  internals at pinned commits. OpenAlex, Crossref, Scholar and arXiv answer; Semantic Scholar
  429s; ITU, HAL, DTIC, ACM and ScienceDirect block. Part 8 needs Canny 1986 and OpenCV's notes.
