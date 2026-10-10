# Asset manifest — kernel-design-separability-borders-derivatives

Series `image-processing`, part 4. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1–3 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/kernel-design-separability-borders-derivatives/ posts/image-processing/kernel-design-separability-borders-derivatives/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/kernel-design-separability-borders-derivatives/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py`
(cover) on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value
drawn is computed in `_figs.py` from the closed forms and published taps named in its
docstring. The route gate was run per figure against its real content. The `source` route was
considered and rejected for all eleven: three candidate paper figures are recorded in
`research/ledger.md` under **Figure candidates** — Lindeberg 2024's Fig. 4 is CC BY 4.0 in the
version of record, but that version was unreachable and the reachable arXiv copy carries only
arXiv's licence, so its reuse rights could not be verified on the copy that would be extracted.
No figure is a `mermaid` route — none has more than nine nodes, crossing edges or three parallel
paths. There is no lab; the series' "nothing is executed" contract rules one out.

Every PNG was opened and checked by eye after its last render: arithmetic against the article,
label collisions, legend swatches against the marks they name, and dead bands.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-kernel-design-separability-borders-derivatives.png | placed | template cover in the series house layout, built by `_cover.py` from the post's central motif — a diagram-design build, not an external generator | — | — | cover-kernel-design-separability-borders-derivatives.png | A 3×3 derivative stencil whose two outer rows carry one free weight p, with Sobel, Scharr and Prewitt marked as values of p |
| FIG_01 | assets/fig-01-derivative-family-kernel-design-separability-borders-derivatives.png | placed | Q4 — seven named stencils with their real column weights, placed at their true positions on a p axis | — | — | fig-01-derivative-family-kernel-design-separability-borders-derivatives.png | Number line of the cross-weight p from 0 to 1/3 with the central difference, Scharr, Sobel, Prewitt and Gaussian stencils at their positions |
| FIG_02 | assets/fig-02-family-on-the-patch-kernel-design-separability-borders-derivatives.png | plot | Q4 — the real window beside a line evaluated from the closed form, with named points | — | — | fig-02-family-on-the-patch-kernel-design-separability-borders-derivatives.png | The 3×3 window at (r2, c2) with row differences 80, −27.5 and 80, beside the line 80 − 107.5(1 − 2p) with named filters marked |
| FIG_03 | assets/fig-03-truncating-sigma-2-kernel-design-separability-borders-derivatives.png | plot | Q4 — sampled weights and truncation windows drawn to scale, with computed mass and variance | — | — | fig-03-truncating-sigma-2-kernel-design-separability-borders-derivatives.png | Bars of the sigma 2 Gaussian samples from minus 8 to 8 with brackets for 3, 5, 7 and 13 taps, and each window's kept mass and variance |
| FIG_04 | assets/fig-04-gradient-turns-kernel-design-separability-borders-derivatives.png | plot | Q4 — vector geometry to scale with the computed shrink factor on each component | — | — | fig-04-gradient-turns-kernel-design-separability-borders-derivatives.png | True gradient at 22.5° and its central-difference, Sobel and Scharr estimates at a 4-pixel wavelength, with each component's shrink factor |
| FIG_05 | assets/fig-05-matching-the-difference-kernel-design-separability-borders-derivatives.png | plot | Q4 — transfer functions from closed form with the crossing wavelengths computed | — | — | fig-05-matching-the-difference-kernel-design-separability-borders-derivatives.png | sin ω / ω, the central difference's own smoothing, against cross-smoothing curves for p = 1/6, 3/16 and 1/4, with their crossing points |
| FIG_06 | assets/fig-06-angular-error-kernel-design-separability-borders-derivatives.png | plot | Q4 — closed-form angular-error curves for seven filters, labelled as a model | — | — | fig-06-angular-error-kernel-design-separability-borders-derivatives.png | Angular error against orientation at a 4-pixel wavelength for seven derivative filters, from 7.6° for Prewitt to 0.17° for a 5-tap pair |
| FIG_07 | assets/fig-07-matched-pairs-kernel-design-separability-borders-derivatives.png | plot | Q4 — four small multiples evaluated from the published taps, mismatch shaded | — | — | fig-07-matched-pairs-kernel-design-separability-borders-derivatives.png | Four plots of a derivative filter's response against ω times its prefilter's, for Sobel, Scharr and two Farid–Simoncelli pairs |
| FIG_08 | assets/fig-08-rank-and-separability-kernel-design-separability-borders-derivatives.png | placed | Q4 — grids of real weights with their column and row factors | — | — | fig-08-rank-and-separability-kernel-design-separability-borders-derivatives.png | Sobel and Scharr as one column times one row, and the Laplacian as the sum of two column-times-row terms, each labelled with its rank |
| FIG_09 | assets/fig-09-sampled-truncated-discrete-kernel-design-separability-borders-derivatives.png | plot | Q4 — variance curves from the definitions, OpenCV's tables and the shared kernel marked | — | — | fig-09-sampled-truncated-discrete-kernel-design-separability-borders-derivatives.png | Kernel variance over σ² against σ for sampled, 3-tap, integrated and discrete Gaussians, with OpenCV's σ = 0 tables and the shared kernel |
| FIG_10 | assets/fig-10-borders-and-derivatives-kernel-design-separability-borders-derivatives.png | placed | Q4 — a grid of real pixel values per border rule, drawn high value = bright, with worked outputs | — | — | fig-10-borders-and-derivatives-kernel-design-separability-borders-derivatives.png | Row r2 extended three pixels each way under five border rules, with the Sobel derivative at the left and right edge columns under each |
| FIG_11 | assets/fig-11-tooling-map-kernel-design-separability-borders-derivatives.png | placed | Q5 — an 11 × 5 comparison grid with no edges | — | — | fig-11-tooling-map-kernel-design-separability-borders-derivatives.png | Grid of derivative and Gaussian calls in OpenCV, SciPy, NumPy and scikit-image with weights, raw scale, default border and a gotcha |
