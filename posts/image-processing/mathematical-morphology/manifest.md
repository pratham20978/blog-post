# Asset manifest — mathematical-morphology

Series `image-processing`, part 12. **Status: local draft assets ready for upload.** Upload each PNG
below to the public `media` bucket under the object key shown (the store is flat, so every key
carries the post slug, as Parts 1–11 do), write the resulting URLs to `urls.txt` in table order, then
run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/mathematical-morphology/ posts/image-processing/mathematical-morphology/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/mathematical-morphology/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract rejects a
non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and the
exercise ladder (E1–E4, the L3 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check these predictions by running them.** Every library result in the
post comes from source read at pinned commits and tags (OpenCV 802cf95 with tags 4.10.0, 4.11.0 and
4.12.0; scikit-image b700edc with v0.25.2 and v0.26.0; SciPy v1.18.1) and replayed in plain Python;
nothing was run, per the series' contract. With
`p = np.full((5, 5), 40, np.uint8); p[:, 3:] = 200; p[2, 1] = 255`,
`m = (p > 40).astype(np.uint8)` and `k = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))`:

1. `cv2.erode(m, k)` should be column 4 only (5 pixels) and `cv2.dilate(m, k)` 19 pixels: columns
   2–4 plus (1, 1), (2, 0), (2, 1), (3, 1).
2. `cv2.morphologyEx(m, cv2.MORPH_OPEN, k)` should be columns 3–4 (10 pixels);
   `cv2.MORPH_CLOSE` columns 3–4 plus (1, 2), (2, 2), (3, 2), (2, 1) (14 pixels);
   `cv2.MORPH_OPEN` with `iterations=2` all zeros. The 3×3 square kernel (OpenCV's default) gives 10
   and 0 too.
3. **The load-bearing one:** `cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))` should
   return 7 pixels, column 4 plus (3, 2) and (3, 3), and `cv2.MORPH_OPEN` with the same kernel column 4
   only; `cv2.erode(cv2.dilate(m, k2, anchor=(0, 0)), k2)` should return 13 pixels (the mask plus (2, 0)
   and (2, 2)). If 3 differs, the reflection section, Figure 10, feed card 1, Story 1, the WARNING and
   exercise E4 need reopening. Issue #23605's own example reproduces exactly under the same replay.
4. `cv2.morphologyEx(p, cv2.MORPH_GRADIENT, k)` should match Figure 7's left grid (160 on columns 2–3,
   215 at (1, 1), (2, 0), (2, 1), (2, 2), (3, 1)); `cv2.MORPH_TOPHAT` 215 at (2, 1) only;
   `cv2.MORPH_BLACKHAT` 160 at (1, 2), (2, 2), (3, 2) only.
5. `scipy.ndimage.binary_erosion(m)` should be all False and `scipy.ndimage.binary_closing(m)` 7
   pixels: (1–3, 2), (1–3, 3) and (2, 1).
6. `skimage.morphology.opening(p)` should equal OpenCV's `MORPH_OPEN` with the cross, and
   `skimage.morphology.binary_erosion(m)` column 4 only.

OpenCV's IPP morphology path is compiled out in every version checked, so builds with and without IPP
should agree; ARM (Carotene), OpenVX and RISC-V builds route through their own HAL and were not read.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover) on
top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn is computed
in `assets/_data.py` from the definitions — binary and flat grey erosion, dilation, opening and closing
by the cross under two border rules, the adjunction on named and random pairs, the granulometry and the
tiling, the threshold decomposition, the median as a maximum of erosions, the gradient, top-hats and
Part 8's Sobel table, reconstruction and h-maxima, the distance transform, and OpenCV's erode and dilate
replayed from its source — and asserted against the article's numbers, so a figure that disagrees with
the text fails to build. The asserts caught two slips in drafting: OpenCV's 5×5 ellipse has 17 pixels,
not the 21 first written, and drawing the random pairs once for both border rules gives 616 failures,
not the 651 of a first run that drew them separately. The route gate was run per figure against its
real content. The `source` route was considered and rejected for all eleven: four candidate paper
figures are recorded in `research/ledger.md` under **Figure candidates**, and none has verified reuse
rights (SIAM, IEEE, Springer copyright). No figure is a `mermaid` route: none is a node-and-edge
diagram past Q3.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on the eleven figures and the cover;
on the social cards only the two known false positives, consecutive serif title lines and the lockup's
`.in`). `lint_visuals.py`: 0 text overflows, 0 arrow reports. Review by eye caught and fixed: uneven
panel spacing (Figures 1 and 2), a footnote over the last row (Figure 3), legend swatches that did not
match their marks and a reference line drawn over bars (Figure 4), one tint meaning two things and two
identical swatches (Figure 5), notes over a grid and two arrows stopping short of their targets
(Figure 6), a duplicated axis label and a mismatched dash (Figure 8), captions under notes (Figure 9),
a swatch a shade off its glyph and a dead band (Figure 10); on the cards, two captions running into
each other (feed 5), a bar label crowding its panel title (feed 6), and two takeaways that claimed more
than the post shows (feeds 6 and 7).

Re-render: `cd assets && python3 _figs.py && python3 _cover.py && python3 _social.py && python3
../../../../.claude/blog-forge/scripts/render_social.py social/` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-mathematical-morphology.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 2's first step — a diagram-design build, not an external generator | — | — | cover-mathematical-morphology.png | A 5×5 mask with a bright bar and a tangerine speck, opened by a blue cross into the bar alone, beside the adjunction law |
| FIG_01 | assets/fig-01-erosion-and-dilation-mathematical-morphology.png | placed | Q4 — small multiples of a real 5×5 grid beside the element | — | — | fig-01-erosion-and-dilation-mathematical-morphology.png | The 11-pixel mask, the 3×3 cross, the 19-pixel dilation and the 5-pixel erosion, which is column c4 only |
| FIG_02 | assets/fig-02-opening-and-closing-mathematical-morphology.png | placed | Q4 — small multiples of real grids, once and twice | — | — | fig-02-opening-and-closing-mathematical-morphology.png | Opening keeps the 10-pixel bar and drops the speck; closing fills c2 in rows r1 to r3; each applied twice is unchanged |
| FIG_03 | assets/fig-03-adjunction-mathematical-morphology.png | placed | Q4 — paired grids per row with the violating pixels outlined | — | — | fig-03-adjunction-mathematical-morphology.png | Four rows of paired grids: δ(A) beside Y and A beside ε(Y), with the same yes or no on both sides of every row |
| FIG_04 | assets/fig-04-granulometry-mathematical-morphology.png | chart | Q1 — eight values computed from the definitions, on two scales, plus the spectrum | — | — | fig-04-granulometry-mathematical-morphology.png | Mask area 11, 10, 0, 0 and grey volume 2,815, 2,600, 1,000, 1,000 over sizes 0 to 3, with the pattern spectrum's two bars |
| FIG_05 | assets/fig-05-laws-of-dilation-mathematical-morphology.png | placed | Q4 — real grids and element shapes, four small panels | — | — | fig-05-laws-of-dilation-mathematical-morphology.png | Four panels: a pixel dilates to the cross; two dilations union to 19 pixels; two crosses make a diamond; the cross's ten 3-pixel subsets |
| FIG_06 | assets/fig-06-threshold-decomposition-mathematical-morphology.png | placed | Q4 — real grids at each threshold, fanned out and stacked back; five boxes, no crossings | — | — | fig-06-threshold-decomposition-mathematical-morphology.png | The patch's threshold sets at 41 and 201, each eroded by the cross, stacked back into the grey erosion with 200 on c4 and 40 elsewhere |
| FIG_07 | assets/fig-07-gradient-and-top-hats-mathematical-morphology.png | placed | Q4 — grids of real values side by side | — | — | fig-07-gradient-and-top-hats-mathematical-morphology.png | The morphological gradient (160 at the step, 215 round the impulse), Part 8's Sobel (640 and 0), and the white and black top-hats |
| FIG_08 | assets/fig-08-h-maxima-mathematical-morphology.png | placed | Q4 — small multiples of real grids, with the closed-form heights beside them | — | — | fig-08-h-maxima-mathematical-morphology.png | Three grids of the patch reconstructed from itself minus h, for h = 100, 180 and 215, with the bar and impulse heights shrinking to 40 |
| FIG_09 | assets/fig-09-border-rules-mathematical-morphology.png | placed | Q4 — small multiples of real grids under two border rules, and the tiling | — | — | fig-09-border-rules-mathematical-morphology.png | Erosion and closing of the mask with the outside ignored (5 and 14 px) and set to 0 (0 and 7), and the tiled patch keeping its edge bar |
| FIG_10 | assets/fig-10-opencv-2x2-kernel-mathematical-morphology.png | placed | Q4 — small multiples of real grids replayed from OpenCV's source, with the element offsets | — | — | fig-10-opencv-2x2-kernel-mathematical-morphology.png | OpenCV's 2×2 opening (5 pixels) and closing (7 pixels, missing mask pixels) beside the true opening (10) and closing (13) and the anchor fix |
| FIG_11 | assets/fig-11-tooling-map-mathematical-morphology.png | placed | Q5 — an 8 × 4 comparison grid with no edges, the series' closing tooling map | — | — | fig-11-tooling-map-mathematical-morphology.png | Grid comparing OpenCV, scikit-image, SciPy and MATLAB on default element, border rule, reflection in dilation, iterations and disk shapes |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live). Later spokes are named by
title only, as this series allows, because Part 1 published the spoke list.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* | **live** at https://canery.in/blogs/image-processing-by-hand | the **Level** line: "*Image Processing by Hand* (part 1 of this series)" | the post root |
| Part 1 | live | series line: "Part 1 defined erosion and dilation … drew morphology inside the rank operators in its Figure 10" | `#morphology-ordering-within-a-structuring-element` |
| Part 1 | live | The problem: "Part 1 gave the two primitives as a local minimum and maximum"; "Part 1 placed it in the stage where linearity stops" | `#morphology-ordering-within-a-structuring-element`; `#stage-4--decide-where-linearity-stops` |
| Part 1 | live | "The median is morphology too": "Part 1's Figure 10 drew morphology inside the rank filters"; "as Part 1's median did" | `#rank-filters-ordering-within-a-neighbourhood` |
| Part 11 — *Thresholding and Segmentation: Otsu, Sauvola, Watershed* | built 2026-10-14, **not live** | series line; Step 1: "the cut Otsu's method returns on this patch in Part 11"; Reconstruction: "the h-minima filter that Part 11 used"; Distance: "Part 11 floods the negated distance transform" | `#worked-example`; `#why-does-watershed-over-segment-and-where-do-markers-come-from` once live |
| Part 8 — *Canny Edge Detection, Line by Line: Setting the Thresholds* | built 2026-10-12, **not live** | Gradients and top-hats: "The Sobel magnitude that Part 8 … worked out for the patch"; Figure 7's panel title | `#step-1-the-gradient` once live |

Part 11 names this post by title as *Mathematical Morphology as Lattice Algebra* for "the cleaning
operators"; once this post is live, that mention can link here (`#what-do-the-laws-let-you-build`).

## Findings outside this post

- **Part 1 (published), Figure 7's caption,** says OpenCV's morphology border value "becomes −DBL_MAX
  for dilation". That holds only for 64-bit float images: for 8-bit images the default border value is
  0 for dilation and 255 for erosion (`createMorphologyFilter`), with the same effect, that the outside
  never wins. Fixing the caption is the owner's call; this post states the 8-bit values and does not
  mention Part 1's.
- **OpenCV issue #23605** (opening not anti-extensive with asymmetric kernels) is still open at
  802cf95; this post's patch gives a second, smaller reproduction (the 2×2 closing that loses five
  pixels). Not reported upstream.
- **scikit-image** keeps a grey `dilation` that does not mirror while `binary_dilation` does
  (documented); its unreleased `skimage2` namespace changes both the mirroring and the border default
  ('reflect' to 'ignore'), so `skimage2` results on asymmetric footprints and at the border will differ
  from `skimage` v0.26.0 ones. Worth a line in Part 13 or 14 only if they use scikit-image morphology.
