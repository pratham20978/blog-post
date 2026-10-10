# Asset manifest — resampling-and-aliasing

Series `image-processing`, part 3. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1 and 2 do), write the resulting URLs to `urls.txt` in
table order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/resampling-and-aliasing/ posts/image-processing/resampling-and-aliasing/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/resampling-and-aliasing/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py`
(cover) on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. The route
gate was run per figure against its real content. The `source` route was considered and
rejected for all ten: four candidate paper figures are recorded in `research/ledger.md` under
**Figure candidates**, and none has verified reuse rights. No figure is a `mermaid` route —
none has more than nine nodes, crossing edges or three parallel paths. There is no lab; the
series' "nothing is executed" contract rules one out.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-resampling-and-aliasing.png | placed | template cover in the series house layout, built by `_cover.py` from the post's central motif — a diagram-design build, not an external generator | — | — | cover-resampling-and-aliasing.png | Row of five pixels under one new pixel of a shrink: a fixed-width kernel reads one of them, a kernel widened by 1/s reads all three |
| FIG_01 | assets/fig-01-where-the-samples-sit-resampling-and-aliasing.png | placed | Q4 — sample positions drawn to scale over the pixel cells; three conventions compared on one ruler | — | — | fig-01-where-the-samples-sit-resampling-and-aliasing.png | Five input pixel cells with the sample points of a 0.6x shrink under half-pixel centres, OpenCV's floor index and a corner-aligned grid |
| FIG_02 | assets/fig-02-shrink-taps-resampling-and-aliasing.png | plot | Q4 — kernel curves evaluated at the three real output positions over the row, taps as points | — | — | fig-02-shrink-taps-resampling-and-aliasing.png | Row 40 255 40 200 200 with nearest, linear, Keys cubic and Lanczos-3 kernels centred at 0.33, 2 and 3.67, taps and output values marked |
| FIG_03 | assets/fig-03-enlarge-reconstructions-resampling-and-aliasing.png | plot | Q4 — continuous reconstructions from the closed-form kernels, with the 8-bit clip line | — | — | fig-03-enlarge-reconstructions-resampling-and-aliasing.png | Continuous reconstructions of the row by four kernels at 1.7x with eight sample dots; cubic and Lanczos dip below 40 and rise past 200 |
| FIG_04 | assets/fig-04-two-regimes-resampling-and-aliasing.png | placed | Q5 — four stages in two rows, no crossings, a bandwidth on every edge and a frequency strip per row | — | — | fig-04-two-regimes-resampling-and-aliasing.png | Two pipelines of reconstruct, prefilter, sample: at 1.7x the prefilter is skipped, at 0.6x it cuts the band from 0.5 to 0.3 cycles |
| FIG_05 | assets/fig-05-four-kernels-resampling-and-aliasing.png | plot | Q4 — four functions of x from their definitions, small multiples over the sinc | — | — | fig-05-four-kernels-resampling-and-aliasing.png | Box, triangle, Keys cubic and Lanczos-3 kernels drawn over the sinc, with supports of 1, 2, 4 and 6 taps and negative lobes shaded |
| FIG_06 | assets/fig-06-transfer-functions-resampling-and-aliasing.png | plot | Q4 — transfer functions evaluated from the definitions, with both Nyquist frequencies marked | — | — | fig-06-transfer-functions-resampling-and-aliasing.png | Transfer functions of box, triangle, Keys and Lanczos-3 against the ideal box, with Nyquist at 0.5 and the 0.6x Nyquist at 0.3 marked |
| FIG_07 | assets/fig-07-bicubic-family-resampling-and-aliasing.png | plot | Q4 — a two-parameter plane with overshoot and blur computed for each named point | — | — | fig-07-bicubic-family-resampling-and-aliasing.png | Plane of cubic parameters B and C with the B-spline, Mitchell, Catmull-Rom, OpenCV and Rifman kernels marked with overshoot and blur values |
| FIG_08 | assets/fig-08-resampling-matrices-resampling-and-aliasing.png | placed | Q4 — a grid of real weights with row and column margins; the values are the figure | — | — | fig-08-resampling-matrices-resampling-and-aliasing.png | Four 3-by-5 resampling matrices at 0.6x with row sums of 1 and column sums below; only the area matrix has every column equal to 0.6 |
| FIG_09 | assets/fig-09-stretched-kernel-resampling-and-aliasing.png | plot | Q4 — one kernel at two widths, in space and in frequency, evaluated from the definition | — | — | fig-09-stretched-kernel-resampling-and-aliasing.png | Triangle kernel at unit width and stretched by 1/0.6: its taps at x = 2, and its transfer function's cutoff moving from 0.5 to 0.3 |
| FIG_10 | assets/fig-10-tooling-map-resampling-and-aliasing.png | placed | Q5 — an 11 × 5 comparison grid with no edges | — | — | fig-10-tooling-map-resampling-and-aliasing.png | Grid of resize calls in OpenCV, Pillow, scikit-image and SciPy with kernel, cubic parameter, prefilter on shrink and sample positions |
