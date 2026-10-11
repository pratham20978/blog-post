# Asset manifest — edge-preserving-smoothing

Series `image-processing`, part 7. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1–6 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/edge-preserving-smoothing/ posts/image-processing/edge-preserving-smoothing/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/edge-preserving-smoothing/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and
the exercise ladder (E1–E4, the L3 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check one claim by running it.** The tooling map says scikit-image's
`denoise_bilateral` (commit b700edc, and releases v0.21.0 and v0.25.2) builds its spatial lookup
table on `win_size + 1` points and reads it as `win_size`, so each spatial weight is read from a
shifted offset. That comes from reading the source and replaying its index arithmetic in plain
Python; it was not run, per the series' contract. One call settles it: filter a float image of
zeros with a single 1.0 in the middle, `sigma_color=10`, and see whether the output's peak stays
on the centre pixel. If the peak moves, the post is right and the issue is worth reporting
upstream (no issue or PR mentions it; open PR #8210 copies the same line into a 3-D version). If
it does not move, delete that paragraph, the Figure 11 row and the `L47` ledger row.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py`
(cover) on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value
drawn is computed in `_figs.py` from the definitions — the bilateral filter with the shared 3×3
Gaussian, the median, NL-means with 3×3 patches under both self-weight rules, the Perona–Malik
scheme with adiabatic borders — and asserted against the article's numbers, so a figure that
disagrees with the text fails to build (during the build the asserts caught a scorecard value of
93.7 that is 93.6 and a worked check that did not add up, and Figure 3 exposed a scorecard
value of 165.3 that is 165.2). The
route gate was run per figure against its real content. The `source` route was considered and
rejected for all eleven: five candidate paper figures are recorded in `research/ledger.md` under
**Figure candidates**, and none has verified reuse rights (IEEE and Now Publishers copyright;
IPOL's is non-commercial). No figure is a `mermaid` route: there are no node-and-edge diagrams.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on the figures and the cover).
`lint_visuals.py`: 0 text overflows, 0 arrow reports. Review by eye caught and fixed: label
plates cutting gaps in curves and marker lines (Figures 4, 5, 7, 8, 9), ellipses spilling out of
Figure 6's plot, a whole render of Figure 6 in a fallback font (the rasteriser's virtual-time
budget is now 15 s), eyebrow uppercasing that turned σr into σR and g(s) into G(S), a
"values read" axis that was counting shifts (Figure 10), a dangling arrow label and a short arrow
in Figure 1, and a distance grid running past Figure 2's margin.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social` measures the figures and the cards; its only reports on the cards
should be the two known false positives (consecutive serif title lines, and the lockup's `.in`).

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-edge-preserving-smoothing.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 1's weights — a diagram-design build, not an external generator | — | — | cover-edge-preserving-smoothing.png | A 5×5 grid split by a vertical edge, with dots sized by bilateral weight: large on the dark side, tiny across the edge and on one tangerine cell |
| FIG_01 | assets/fig-01-bilateral-weights-edge-preserving-smoothing.png | placed | Q4 — grids of real weights: window, spatial, range and normalised product at two pixels | — | — | fig-01-bilateral-weights-edge-preserving-smoothing.png | The bilateral weights at the impulse and at the step's dark side: spatial times range gives 2.7% for each of the impulse's neighbours and 13.5% across the step |
| FIG_02 | assets/fig-02-patch-distances-edge-preserving-smoothing.png | placed | Q4 — grids of real patch distances from two pixels, with the patches themselves | — | — | fig-02-patch-distances-edge-preserving-smoothing.png | Patch distances from the step pixel and from the impulse to every candidate: the step has an exact copy at distance 0, the impulse's nearest patches are at 5,136 |
| FIG_03 | assets/fig-03-perona-malik-three-iterations-edge-preserving-smoothing.png | placed | Q4 — small multiples of real values, four iterations of the scheme | — | — | fig-03-perona-malik-three-iterations-edge-preserving-smoothing.png | Perona–Malik on the patch at iterations 0 to 3, with the step's faces conducting 0.2 and the impulse's 0.122 |
| FIG_04 | assets/fig-04-the-trade-off-edge-preserving-smoothing.png | plot | curves computed from the definitions: σr sweep and iteration count on the patch | — | — | fig-04-the-trade-off-edge-preserving-smoothing.png | Step contrast kept against impulse contrast left: the bilateral and Perona–Malik trace curves from no change to the Gaussian, while the median and NL-means under the max rule sit at the right edge |
| FIG_05 | assets/fig-05-range-weights-edge-preserving-smoothing.png | plot | closed-form curves for four values of σr | — | — | fig-05-range-weights-edge-preserving-smoothing.png | Range weight against intensity difference for σ_r of 20, 50, 80 and 160, with the differences 20, 160 and 215 marked |
| FIG_06 | assets/fig-06-position-intensity-lift-edge-preserving-smoothing.png | placed | Q4 — geometry drawn to scale: the row in position × intensity, 1σ ellipses, σs × σr grid | — | — | fig-06-position-intensity-lift-edge-preserving-smoothing.png | Row r2 drawn in the position–intensity plane on a grid of cells σ_s wide and σ_r tall: the impulse sits 2.69 σ_r above its neighbours and the step 2.00 σ_r |
| FIG_07 | assets/fig-07-nl-means-against-h-edge-preserving-smoothing.png | plot | curves computed from the definitions on the patch, two self-weight rules | — | — | fig-07-nl-means-against-h-edge-preserving-smoothing.png | NL-means estimate at the impulse and at a step pixel against h, under own-patch weight 1 and under the max rule |
| FIG_08 | assets/fig-08-flux-edge-preserving-smoothing.png | plot | closed-form flux curves for both conductances at K = 80 | — | — | fig-08-flux-edge-preserving-smoothing.png | Flux against difference for the rational and exponential conductances at K = 80, beside the linear flux of the heat equation, with 20, 160 and 215 marked |
| FIG_09 | assets/fig-09-stopping-time-edge-preserving-smoothing.png | plot | the scheme iterated from its definition for 100 iterations | — | — | fig-09-stopping-time-edge-preserving-smoothing.png | Contrast of the impulse and of the step over 100 iterations of Perona–Malik: the impulse falls first and both reach the mean 112.6 |
| FIG_10 | assets/fig-10-cost-per-pixel-edge-preserving-smoothing.png | chart | Q1 — counts from each method's definition compared on one log scale | — | — | fig-10-cost-per-pixel-edge-preserving-smoothing.png | Operations per pixel on a log scale for the median, the bilateral filter at three window sizes, NL-means naive and with integral images, and Perona–Malik at 10 and 100 iterations |
| FIG_11 | assets/fig-11-tooling-map-edge-preserving-smoothing.png | placed | Q5 — a 10 × 4 comparison grid with no edges, the series' closing tooling map | — | — | fig-11-tooling-map-edge-preserving-smoothing.png | Grid of OpenCV, opencv_contrib, scikit-image, ITK and MedPy calls for the three methods with their window, default and trap |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live).

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* (the series) | **live** at https://canery.in/blogs/image-processing-by-hand | series line: "This is part 7 of *Image Processing by Hand*. Part 1 showed that no linear filter stops at an edge" | `#the-operators-that-break-the-split` |
| Part 1 | live | the **Level** line: "*Image Processing by Hand* (part 1 of this series)" | the post root |
| Part 1 | live | The problem: "Part 1 averaged the impulse's 3×3 neighbourhood three ways" | `#worked-example` |
| Part 1 | live | The math: "With W fixed this is Part 1's linear filter." | `#stage-2--filter-every-linear-filter-is-one-weighted-sum` |
| Part 2 — *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening* | **live** at https://canery.in/blogs/laplacian-by-hand | the **Level** line: "the heat-equation section of *The Laplacian by Hand* (part 2)" | `#the-heat-equation-and-the-sharpening-identity` |
| Part 2 | live | Worked example: "runs the heat equation of Part 2 with a *conductance*" | `#the-heat-equation-and-the-sharpening-identity` |
| Part 2 | live | Diffusion: "That is the heat equation, Part 2's identity" | `#sharpening-the-thing-blur-removes` |
| Part 5 — *The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering* | built 2026-10-10, **not live** | Diffusion: "The patch holds 2,815 grey levels in total, Part 5's DC term" | `#the-spectrum-centred` once live |

## Finding outside this post

Part 1 (published) lists "Perona, P. and Malik, J. ... [PDF](https://www.math.uci.edu/~gpatrick/source/papers/G131.pdf)"
as reference 18. That PDF is P. Guidotti's survey *Anisotropic Diffusions of Image Processing From
Perona-Malik on*, not the 1990 paper. The paper itself is at
https://people.eecs.berkeley.edu/~malik/papers/MP-aniso.pdf (Malik's page; this post's reference
2). Part 1 was not edited; changing it reopens a published post.
