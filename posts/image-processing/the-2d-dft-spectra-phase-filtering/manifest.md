# Asset manifest — the-2d-dft-spectra-phase-filtering

Series `image-processing`, part 5. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1–4 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/the-2d-dft-spectra-phase-filtering/ posts/image-processing/the-2d-dft-spectra-phase-filtering/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/the-2d-dft-spectra-phase-filtering/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and
the exercise ladder (E1–E5) lives in the post's `## Try it yourself`.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py`
(cover) on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value
drawn is computed in `_figs.py` from the definitions — the 2-D DFT of the patch, its transpose,
its circular shift and its 2×2 tiling, closed-form transfer functions, and the operation-count
model — and asserted against the article's numbers, so a figure that disagrees with the text
fails to build. The route gate was run per figure against its real content. The `source` route
was considered and rejected for all thirteen: four candidate paper figures are recorded in
`research/ledger.md` under **Figure candidates**, and none has verified reuse rights (Springer
copyright, IPOL's CC BY-NC-SA with unverified NC/SA terms for this site, an unlicensed technical
report, and Pearson copyright). No figure is a `mermaid` route — none has more than nine nodes
joined by edges, crossing edges or three parallel paths; they are grids, strips and plots. There
is no lab.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`getBBox()` against other text, the canvas and its own
cell): 0 overlaps. Checked by eye: arithmetic against the article, legend swatches against the
marks they name, label plates against the lines beneath them, and dead bands. Figure review caught
one article error — the off-bin interference was quoted as one column's 1-D transform (64.7) beside
the 2-D tile value (860); the article now quotes the 2-D 647.2.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check: `python3 _overlap.py`
measures the figures, the cover and `social/`; its only reports on this post are the two known false
positives on the social cards (consecutive serif title lines, and the lockup's `.in`).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-the-2d-dft-spectra-phase-filtering.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 2's spectrum motif — a diagram-design build, not an external generator | — | — | cover-the-2d-dft-spectra-phase-filtering.png | A 5×5 grid of spectrum cells with one bright row through a tangerine centre, over an even grey floor |
| FIG_01 | assets/fig-01-rows-then-columns-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — three grids of real complex values side by side; the row-by-row values are the figure | — | — | fig-01-rows-then-columns-the-2d-dft-spectra-phase-filtering.png | The 5×5 patch, its five row transforms with row r2 standing out, and the final spectrum: one bright row and every other bin at 215 |
| FIG_02 | assets/fig-02-centred-spectrum-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — a grid of real magnitudes, log-shaded, beside the patch, with the energy split | — | — | fig-02-centred-spectrum-the-2d-dft-spectra-phase-filtering.png | The patch beside its centred 5×5 magnitude spectrum: DC 2,815 at the centre, a bright horizontal row, and a flat floor of 215 elsewhere |
| FIG_03 | assets/fig-03-phase-only-magnitude-only-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — three grids of computed values; positions are read cell by cell | — | — | fig-03-phase-only-magnitude-only-the-2d-dft-spectra-phase-filtering.png | Three 5×5 grids: the patch, its magnitude-only rebuild with the impulse moved to the corner, and its phase-only rebuild keeping it in place |
| FIG_04 | assets/fig-04-phase-swap-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — four grids of computed values with the impulse and bar marked | — | — | fig-04-phase-swap-the-2d-dft-spectra-phase-filtering.png | Four 5×5 grids: the patch, its transpose, and the two swaps, A's magnitude giving a vertical bar and B's magnitude a horizontal one |
| FIG_05 | assets/fig-05-notch-on-the-tile-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — 10 × 10 grids of real values, spectrum and mask; four stages that need room | — | — | fig-05-notch-on-the-tile-the-2d-dft-spectra-phase-filtering.png | The tiled 10×10 patch with interference bands, its spectrum with two spikes off the even lattice, the two-bin notch, and the restored tile |
| FIG_06 | assets/fig-06-phase-ramp-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — phasor arrows drawn at their computed angles, before and after a shift | — | — | fig-06-phase-ramp-the-2d-dft-spectra-phase-filtering.png | Phase arrows for the patch's spectrum, turning −72° per column step and −144° per row step, before and after a one-column shift |
| FIG_07 | assets/fig-07-fftshift-odd-even-the-2d-dft-spectra-phase-filtering.png | placed | Q5 — strips of index boxes with no edges; under nine elements per row | — | — | fig-07-fftshift-odd-even-the-2d-dft-spectra-phase-filtering.png | Frequency strips for 5 and 10 points through fftshift, then ifftshift or a second fftshift, with DC and the Nyquist bin marked |
| FIG_08 | assets/fig-08-tiled-patch-cross-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — a tiled grid of real values with the invented edges marked | — | — | fig-08-tiled-patch-cross-the-2d-dft-spectra-phase-filtering.png | The patch tiled three by three, the invented 200-to-40 edge marked at every tile border, beside three fixes for the cross and one non-fix |
| FIG_09 | assets/fig-09-ideal-vs-gaussian-the-2d-dft-spectra-phase-filtering.png | plot | Q4 — gains and outputs evaluated from closed forms; stems and lines to scale | — | — | fig-09-ideal-vs-gaussian-the-2d-dft-spectra-phase-filtering.png | Gains of an ideal low-pass and the shared Gaussian at five frequencies, and their outputs on the row, the ideal one dipping to 0.45 |
| FIG_10 | assets/fig-10-leakage-on-and-off-bin-the-2d-dft-spectra-phase-filtering.png | plot | Q4 — computed magnitudes on one spectrum column as bars, log scale | — | — | fig-10-leakage-on-and-off-bin-the-2d-dft-spectra-phase-filtering.png | Bar charts of interference magnitude on one spectrum column for 3 and 2.5 cycles, over the tile's own bins at even frequencies |
| FIG_11 | assets/fig-11-cost-model-the-2d-dft-spectra-phase-filtering.png | plot | Q1 no (a model, not ledger measurements); Q4 — curves from closed forms with marked thresholds | — | — | fig-11-cost-model-the-2d-dft-spectra-phase-filtering.png | Operations per pixel against kernel width for direct, separable and FFT convolution on a 1920×1080 frame, with OpenCV and textbook marks |
| FIG_12 | assets/fig-12-phase-correlation-the-2d-dft-spectra-phase-filtering.png | placed | Q4 — two grids of computed correlation values | — | — | fig-12-phase-correlation-the-2d-dft-spectra-phase-filtering.png | Two 5×5 surfaces for the patch and its shifted copy: plain correlation with a ridge down one column, and phase correlation with a single 1 |
| FIG_13 | assets/fig-13-tooling-map-the-2d-dft-spectra-phase-filtering.png | placed | Q5 — a 12 × 4 comparison grid with no edges | — | — | fig-13-tooling-map-the-2d-dft-spectra-phase-filtering.png | Grid of NumPy, OpenCV, SciPy and scikit-image calls with their normalisation, layout, FFT switch rule and the trap each sets |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01; later
parts named by title only where Part 1's published body already promises them).

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand: Sample, Filter, Transform, Decide* | **live** at https://canery.in/blogs/image-processing-by-hand | the **Level** line: "the transform stage of *Image Processing by Hand: Sample, Filter, Transform, Decide* (part 1 of this series)" | `#stage-3--transform-what-frequency-shows-that-pixels-hide` |
| Part 1 (as "the hub") | live | Filter design: "the hub's four-point example pulled the far end's 200 into the first sample" | `#the-convolution-theorem-on-those-same-numbers` |
| Part 1 (as "the hub") | live | Crossover: "The hub said that past some kernel size, transforming, multiplying and transforming back beats the direct sum." | `#why-this-basis-is-worth-the-change` |
| Part 3 — *Resampling and Aliasing: Interpolation Kernels in Practice* | built 2026-09-25, **not live** | end of "Resizing through the spectrum": "The kernels that resize well in space are the subject of part 3, …" | the post root once live |
| *Wavelets and Multiresolution* (a later spoke) | not written | Limitations, "Beyond this post": "the subject of a later part of this series, *Wavelets and Multiresolution*" | none until it is live |
