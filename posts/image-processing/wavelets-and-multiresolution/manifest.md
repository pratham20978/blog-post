# Asset manifest — wavelets-and-multiresolution

Series `image-processing`, part 6. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1–5 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/wavelets-and-multiresolution/ posts/image-processing/wavelets-and-multiresolution/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/wavelets-and-multiresolution/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and
the exercise ladder (E1–E4, the L3 requirement) lives in the post's `## Try it yourself`.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py`
(cover) on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value
drawn is computed in `_figs.py` from the definitions — Haar and 5/3 lifting on the patch's rows
with JPEG 2000's rounding and whole-sample mirror, one orthonormal 2-D Haar level of the patch
with PyWavelets' default half-sample padding, the coefficient counts from each library's size
rule, the closed-form responses of the published filter taps, and the threshold rules — and
asserted against the article's numbers, so a figure that disagrees with the text fails to build.
The route gate was run per figure against its real content. The `source` route was considered and
rejected for all eleven: five candidate paper figures are recorded in `research/ledger.md` under
**Figure candidates**, and none has verified reuse rights (IEEE and Springer copyright). No figure
is a `mermaid` route — the two ladder diagrams (Figures 1 and 7) have six nodes per lane, no
crossing edges and a value on every edge; the rest are grids, layouts, bars and plots.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 overlaps on the figures).
`lint_visuals.py`: 0 text overflows; its 24 arrow reports are the ladder arrows that end on the
± nodes (circles, which it does not count as nodes) or 3 px short of a value cell, checked by eye.
Review by eye caught and fixed: label plates cutting the 5/3 and 9/7 curves in Figure 6, a plate
notching the shaded dead zone in Figure 10, Figure 3's frequency label sitting under the position
axis, outlines sharing an edge in Figure 4, a tick collision between Figure 2's panels, and a wrong
Pillow cell in Figure 11.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social` measures the figures and the cards; its only reports on the cards
are the two known false positives (consecutive serif title lines, and the lockup's `.in`).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-wavelets-and-multiresolution.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 4's motif — a diagram-design build, not an external generator | — | — | cover-wavelets-and-multiresolution.png | A 6×6 grid split into four tinted 3×3 quadrants, one tangerine cell lit in each, against a band of 25 equal grey cells |
| FIG_01 | assets/fig-01-lifting-the-top-row-wavelets-and-multiresolution.png | placed | Q4 — two lifting ladders whose value is the cell-by-cell arithmetic; six nodes per lane, no crossings | — | — | fig-01-lifting-the-top-row-wavelets-and-multiresolution.png | Row 40 40 40 200 200 split into evens and odds, then predicted and updated by Haar and by the 5/3, giving details 0, 160 and 0, 80 |
| FIG_02 | assets/fig-02-coefficient-budget-wavelets-and-multiresolution.png | chart | Q1 — counts from each library's size rule and the pyramid's level sizes, compared across five representations on one scale | — | — | fig-02-coefficient-budget-wavelets-and-multiresolution.png | Bars of coefficients per pixel for a 5-sample row, the 5×5 patch and a 1920×1080 frame: lifting, PyWavelets and the pyramid |
| FIG_03 | assets/fig-03-position-frequency-tiling-wavelets-and-multiresolution.png | placed | Q4 — geometry: cell widths and heights to scale in four small multiples | — | — | fig-03-position-frequency-tiling-wavelets-and-multiresolution.png | Position-frequency tilings for eight samples: pixels as strips, the DFT as bands, fixed blocks, and dyadic wavelet cells |
| FIG_04 | assets/fig-04-one-haar-level-of-the-patch-wavelets-and-multiresolution.png | placed | Q4 — grids of real coefficient values, the padded patch beside its four subbands, plus the energy split | — | — | fig-04-one-haar-level-of-the-patch-wavelets-and-multiresolution.png | The 5×5 patch beside its four 3×3 Haar subbands, with the step's −160 column in HL and the impulse's four ±107.5 coefficients outlined |
| FIG_05 | assets/fig-05-three-levels-of-a-frame-wavelets-and-multiresolution.png | placed | Q4 — proportional areas: the subband layout drawn to scale | — | — | fig-05-three-levels-of-a-frame-wavelets-and-multiresolution.png | Three-level wavelet layout of a 1920×1080 frame drawn to scale, with subband sizes and the preview each LL decodes to |
| FIG_06 | assets/fig-06-frequency-responses-wavelets-and-multiresolution.png | plot | curves evaluated from the published taps (Skodras et al., Table 3 and 4; Haar) | — | — | fig-06-frequency-responses-wavelets-and-multiresolution.png | Low-pass and high-pass magnitude responses of the Haar, 5/3 and 9/7 filters from zero to the Nyquist frequency |
| FIG_07 | assets/fig-07-integer-lifting-forward-and-back-wavelets-and-multiresolution.png | placed | Q5 — two ladders of six nodes, no crossings, a rounded value on every edge | — | — | fig-07-integer-lifting-forward-and-back-wavelets-and-multiresolution.png | Row 40 255 40 200 200 through integer 5/3 lifting and back: predict, update with rounded values 108 and 74, then the exact inverse |
| FIG_08 | assets/fig-08-shift-variance-wavelets-and-multiresolution.png | placed | Q4 — small multiples of real values, five rows by two filters | — | — | fig-08-shift-variance-wavelets-and-multiresolution.png | Small multiples: the step at three positions and the impulse at two, with Haar and 5/3 level-1 details for each |
| FIG_09 | assets/fig-09-price-of-shift-invariance-wavelets-and-multiresolution.png | chart | Q1 — the published redundancy factors compared on one scale | — | — | fig-09-price-of-shift-invariance-wavelets-and-multiresolution.png | Coefficients per pixel in 2-D: decimated wavelet 1, pyramid 4/3, dual tree 4, undecimated 10 and 16 at three and five levels |
| FIG_10 | assets/fig-10-hard-and-soft-thresholds-wavelets-and-multiresolution.png | plot | threshold curves from their definitions, beside value grids of the thresholded patch | — | — | fig-10-hard-and-soft-thresholds-wavelets-and-multiresolution.png | Hard and soft threshold curves at λ = 50 with the patch's coefficients 107.5 and 160 marked, and the patch after each rule at λ = 50 and 120 |
| FIG_11 | assets/fig-11-tooling-map-wavelets-and-multiresolution.png | placed | Q5 — a 13 × 4 comparison grid with no edges | — | — | fig-11-tooling-map-wavelets-and-multiresolution.png | Grid of PyWavelets, scikit-image and Pillow/OpenJPEG calls with their extension mode, size rule, default and trap |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live).

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* (the series) | **live** at https://canery.in/blogs/image-processing-by-hand | series line: "This is part 6 of *Image Processing by Hand*." | the post root |
| Part 5 — *The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering* | built 2026-10-10, **not live** | the **Level** line: "*The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering* (part 5 of this series)" | the post root once live |
| Part 5 | not live | The problem: "Part 5's DFT put the patch's impulse … into all 25 coefficients with magnitude exactly 215" | `#the-spectrum-centred` once live |
| Part 5 | not live | One level in 2-D: "That is the comparison with Part 5." | `#the-spectrum-centred` once live |
| Part 5 | not live | Which wavelet: "Part 5's tool, the transfer function" | `#how-do-you-design-a-filter-in-the-frequency-domain` once live |
| Part 5 | not live | Shift variance: "Part 5's Fourier magnitude has no such problem" | `#what-survives-when-the-magnitude-is-destroyed` once live |
| Part 2 — *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening* | **live** at https://canery.in/blogs/laplacian-by-hand | the **Level** line: "the pyramid section of *The Laplacian by Hand* (part 2)" | `#the-pyramid-the-same-operator-resampled` |
| Part 2 | live | The problem: "Part 2's Laplacian pyramid already makes that trade one octave at a time" | `#the-pyramid-the-same-operator-resampled` |
| Part 2 | live | The coefficient budget: "One level of Part 2's Laplacian pyramid on this row" | `#the-pyramid-the-same-operator-resampled` |
| Part 3 — *Resampling and Aliasing: Interpolation Kernels in Practice* | built 2026-09-25, **not live** | The same trade in frequency: "the mechanism of *Resampling and Aliasing* (part 3)" | the post root once live |
