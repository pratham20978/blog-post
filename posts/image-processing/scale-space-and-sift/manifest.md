# Asset manifest — scale-space-and-sift

Series `image-processing`, part 10. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1–9 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/scale-space-and-sift/ posts/image-processing/scale-space-and-sift/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/scale-space-and-sift/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and
the exercise ladder (E1–E5, the L4 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check these predictions by running them.** Every OpenCV result in the
post comes from reading `sift.dispatch.cpp`, `sift.simd.hpp` and `resize.cpp` at commit 802cf95
(and the same rules at tag 4.10.0) and replaying the arithmetic in plain Python
(`assets/_replay.py`); nothing was run, per the series' contract. On the patch
`p = np.full((5, 5), 40, np.uint8); p[:, 3:] = 200; p[2, 1] = 255`, enlarged by
`big = np.kron(p, np.ones((7, 7), np.uint8))` (35×35):

1. `cv2.SIFT_create().detect(p, None)` should return no keypoints (the 5-pixel border).
2. `cv2.SIFT_create().detect(big, None)` should return keypoints at about (10.23, 17.25) with
   `size` about 5.02 — the quarter-pixel bias. Their **count** (two in the replay, one per
   orientation peak) is fragile: one histogram peak sits at 0.789 of the highest, against the 0.8
   cut, so one keypoint more or fewer is not a failure.
3. `cv2.SIFT_create(enable_precise_upscale=True).detect(big, None)` should return three keypoints
   at about (9.98, 17.00), `size` about 5.03, angles about 0, 90.6 and 269.4 degrees.
4. With `big14 = np.kron(p, np.ones((14, 14), np.uint8))` and precise upscaling, the square's
   keypoint should be at about (20.46, 34.50) with `size` about 10.03 (exercise E3); the
   corner keypoints at size about 4.4 appear only in precise mode.

If 2 or 3 differs in position or size, the worked example's OpenCV paragraphs and E3–E4 need
reopening before publish. SIFT's own source has no IPP or HAL calls, but the `GaussianBlur` it
calls can dispatch to a HAL or IPP (`smooth.dispatch.cpp`) and `resize` to a HAL
(`resize.cpp`), in builds that have them. The replay follows OpenCV's own separable filter and
resize; if a run differs by more than a hundredth of a pixel, check the build's dispatch first.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover)
on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn is
computed in `assets/_data.py` from the closed form of the enlarged patch's scale space (the patch
is a step and a square, so its Gaussian blur is a sum of normal CDFs) and from `_replay.py`, and
asserted against the article's numbers, so a figure that disagrees with the text fails to build.
The route gate was run per figure against its real content. The `source` route was considered and
rejected for all thirteen: the four candidate paper figures are recorded in `research/ledger.md`
under **Figure candidates** (Lowe's carry no reuse licence, Witkin's none, IPOL's are CC BY-NC-SA;
Lindeberg's PLoS figure is CC BY but 337×172 and replaced by one sentence). No figure is a
`mermaid` route: Figure 9, the only node-and-edge picture, draws sizes to scale.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on the thirteen figures and the
cover). `lint_visuals.py` reports 0 text overflows and 25 arrow findings, all false positives: 24
on Figure 9, because the linter counts only rectangles of at least 60×40 as nodes and Figure 9
draws the pyramid's octaves to scale, so its 8- and 4-pixel octaves are smaller than that; and one
on the cover, its σ axis arrow, a free vector with no node to touch. Review by eye
caught and fixed: seams between shaded cells (now opaque fills with crisp edges), a D0 label that
called the centre a minimum, labels printed over lines in Figures 3, 11 and 12, a crowded marker in
Figure 3, eyebrows whose uppercase changed notation (√k → √K, k = → K =) in Figures 10 and 11,
Figure 7's square-root shading that hid the ridge (now linear per panel with dotted ridge guides),
Figure 8's cut-off box, collisions and arrows ending inside nodes in Figure 9 (redrawn), fallback
fonts in early renders (now local base64 webfonts, below), and a cover ring floating over a level
the stack hid (now an oblique stack).

**Fonts.** Earlier renders on a slow network fell back to system fonts. `_build.py` and
`_overlap.py` now inline a local copy of the webfonts when
`~/.cache/blog-forge-fonts/fonts.local.css` exists (base64 `@font-face` rules for Instrument Serif,
Geist and Geist Mono, generated from the same Google Fonts CSS), and fall back to the remote
`@import` otherwise. The committed SVG and HTML still reference Google Fonts; only rasterising uses
the cache.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py && python3 _social.py`, then
`python3 ../../../../.claude/blog-forge/scripts/render_social.py social/` (paths resolve from the
script directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

**Social.** Eight feed cards in `assets/social/` (`feed-01` … `feed-08`, 1080×1350, `.html`,
`.svg`, `.png`), built by `_social.py` with every number from `_data.py`. **No Story frames, by the
owner's choice for this post**, so `validate_post.py --social` reports the missing Instagram Story
section and nothing else. `_overlap.py social` reports only shell artefacts that Part 9's cards
show too: the two serif title lines' font boxes overlap (the glyphs do not), the lockup's `.in`
is measured before its group is scaled, and on card 5 the "the square" label straddles the edge of
the tinted band, on purpose, since the square's value 4.00 is the band's floor.
`assets/linkedin-prompts.md` (five text-free frames) and `assets/cover-prompt.md` are the
alternative image-model routes.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-scale-space-and-sift.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 1's octave — a diagram-design build, not an external generator | — | — | cover-scale-space-and-sift.png | A grid split by a vertical step with a bright square, and a stack of blurred copies above it with one point marked on the middle level |
| FIG_01 | assets/fig-01-octave-scale-space-and-sift.png | placed | Q4 — small multiples of real values as shaded grids | — | — | fig-01-octave-scale-space-and-sift.png | Six blurred copies of the enlarged patch and the five differences between them, with the square's minimum and one maximum between square and step marked on the middle difference |
| FIG_02 | assets/fig-02-neighbour-test-scale-space-and-sift.png | placed | Q4 — a grid of real numbers | — | — | fig-02-neighbour-test-scale-space-and-sift.png | Three 3×3 grids of numbers for the levels above, at and below the candidate, with the centre −35.379 highlighted as lower than all 26 others |
| FIG_03 | assets/fig-03-fit-in-scale-scale-space-and-sift.png | plot | closed-form samples and a fitted curve | — | — | fig-03-fit-in-scale-scale-space-and-sift.png | The DoG value at the square's centre on five levels, a parabola through the middle three, and its lowest point just below level 2 |
| FIG_04 | assets/fig-04-two-candidates-scale-space-and-sift.png | plot | closed-form contours around real points | — | — | fig-04-two-candidates-scale-space-and-sift.png | Contour maps of the DoG around both candidates: nearly circular rings around the square's centre, long vertical contours around the gap point |
| FIG_05 | assets/fig-05-size-on-log-sigma-scale-space-and-sift.png | plot | closed-form curves | — | — | fig-05-size-on-log-sigma-scale-space-and-sift.png | Four identical bell-shaped curves of normalised response against σ on a log axis, peaking at σ 1.19, 1.99, 2.79 and 5.58 for squares of side 3, 5, 7 and 14, all at height 154.9 |
| FIG_06 | assets/fig-06-set-against-searched-scale-space-and-sift.png | placed | Q4 — real maps with extrema marked | — | — | fig-06-set-against-searched-scale-space-and-sift.png | The same DoG level on the ×7 and ×14 patches: one minimum at the ×7 square's centre, four near the ×14 square's corners, and one at the ×14 square's centre on the level twice as coarse |
| FIG_07 | assets/fig-07-peak-and-ridge-scale-space-and-sift.png | plot | closed-form maps over position and σ, Harris–Laplace levels marked | — | — | fig-07-peak-and-ridge-scale-space-and-sift.png | Two heat maps over position and σ: along the square's row, one peak at x 10 and σ 2.78; along the top row, two straight diagonal ridges of constant height on either side of the step |
| FIG_08 | assets/fig-08-which-requirement-scale-space-and-sift.png | placed | Q5 — comparison grid, no edges | — | — | fig-08-which-requirement-scale-space-and-sift.png | A grid of four kernels against seven requirements: the Gaussian meets all; the Poisson kernel fails non-enhancement and separability; the box fails rotation invariance and the semigroup; the sampled Gaussian meets them only approximately |
| FIG_09 | assets/fig-09-pyramid-scale-space-and-sift.png | placed | Q4 — sizes and σ to scale; 7 nodes, no crossings | — | — | fig-09-pyramid-scale-space-and-sift.png | Five octaves of the pyramid for the 35×35 input: 70, 35, 17, 8 and 4 pixels wide, six blurred levels each with their σ, the extra blur on each arrow, and the square found on level 2 of the 35-pixel octave |
| FIG_10 | assets/fig-10-dog-averages-log-scale-space-and-sift.png | plot | closed-form curves | — | — | fig-10-dog-averages-log-scale-space-and-sift.png | The normalised Laplacian at the square's centre against log σ, peaking at 2.78, and the DoG divided by ln k, the same curve averaged over one interval, peaking at 2.48 |
| FIG_11 | assets/fig-11-edge-test-is-harris-scale-space-and-sift.png | plot | closed-form curve, real points | — | — | fig-11-edge-test-is-harris-scale-space-and-sift.png | The curve t over (1 + t) squared against t, with horizontal lines at 0.04, 0.06 and SIFT's 0.0826, the square at t = 0.98 far above and the gap point at t = 0.047 below SIFT's line |
| FIG_12 | assets/fig-12-orientation-histograms-scale-space-and-sift.png | plot | values from the plain-Python replay of OpenCV's rules | — | — | fig-12-orientation-histograms-scale-space-and-sift.png | Two 36-bin orientation histograms for the square's keypoint, one per upscaling mode, with the 80% line: three peaks clear it in one, two in the other |
| FIG_13 | assets/fig-13-tooling-map-scale-space-and-sift.png | placed | Q5 — the series' closing tooling map | — | — | fig-13-tooling-map-scale-space-and-sift.png | Grid comparing OpenCV, scikit-image and MATLAB on doubling, scales per octave, base σ, contrast threshold, edge threshold, extremum test, border, keypoint size and position conventions |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live). Learned descriptors are
out of the series' scope and named nowhere as a part.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* | **live** at https://canery.in/blogs/image-processing-by-hand | series line: "Part 1 drew σ as an axis and named this post" | its σ-axis figure (Figure 15), or the post root |
| Part 2 — *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening* | **live** at https://canery.in/blogs/laplacian-by-hand | the **Level** line: "*The Laplacian by Hand* (part 2 of this series)" | the post root |
| Part 2 | live | series line: "Part 2, *The Laplacian by Hand…*, showed that the scale-normalised Laplacian peaks at a structure's size" | `#scale-selection-the-laplacian-as-a-ruler` |
| Part 2 | live | The problem: "Part 2's tool was the **scale-normalised Laplacian**" | `#scale-selection-the-laplacian-as-a-ruler` |
| Part 2 | live | Worked example, step 1: "the stand-in for the normalised Laplacian that Part 2 introduced" | `#scale-selection-the-laplacian-as-a-ruler` |
| Part 3 — *Resampling and Aliasing: Interpolation Kernels in Practice* | gate PASS 2026-09-25, **not live** | Implementation, OpenCV: "The quarter pixel is Part 3's resize arithmetic" | the resize-mapping section, once live |
| Part 7 — *Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion* | gate PASS 2026-10-11, **not live** | What SIFT needs from the kernel: "the edge-preserving diffusion of Part 7" | the Perona–Malik section, once live |
| Part 9 — *The Structure Tensor: Harris, Shi–Tomasi, and Optical Flow* | gate PASS 2026-10-12, **not live** | series line: "Part 9 … left the scale half of Harris–Laplace for here" | its "Which window" section, once live |
| Part 9 | not live | Harris–Laplace: "Part 9 built the scale-adapted structure tensor and its Harris maxima per level" | the post root, once live |
| Part 9 | not live | The edge test: "It is Part 9's Harris sign test with k = 0.0826" and Figure 11 "on Part 9's curve" | its Harris-as-ratio section, once live |

Part 9's own manifest lists this post as "planned (Part 10), not built" where it says "Choosing
the scale belongs to the later spoke"; that row can now point here.

## Findings outside this post

- **scikit-image SIFT, by its code:** `rescale` calls SciPy's `zoom` with `grid_mode=True` and
  positions are then read as index × sample spacing, so by the code at b700edc it should report
  the same +0.25-pixel offset as OpenCV's default. Predicted, not run, and not reported upstream.
- **OpenCV:** issue #23123 (the quarter-pixel bias, January 2023) is still open; the fix
  (`enable_precise_upscale`, PR #23270) shipped in 4.8.0 switched off by default, and leaving it
  off logs that the behaviour is deprecated. The `SIFT_create` documentation does not mention the
  bias. Not reported further.
