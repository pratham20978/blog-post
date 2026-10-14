# Asset manifest — thresholding-and-segmentation

Series `image-processing`, part 11. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every key
carries the post slug, as Parts 1–10 do), write the resulting URLs to `urls.txt` in table order, then
run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/thresholding-and-segmentation/ posts/image-processing/thresholding-and-segmentation/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/thresholding-and-segmentation/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract rejects a
non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and the
exercise ladder (E1–E4, the L3 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check these predictions by running them.** Every library result in the
post comes from source read at pinned commits (OpenCV 802cf95 with tags 4.10.0 and 4.12.0;
scikit-image b700edc with tags 0.24.0 and 0.25.0) and replayed in plain Python; nothing was run, per
the series' contract. On the patch `p = np.full((5, 5), 40, np.uint8); p[:, 3:] = 200; p[2, 1] = 255`:

1. `cv2.GaussianBlur(p, (3, 3), 0.8)` should return rows `40 40 78 162 200`, `64 67 90 162 200`,
   `94 99 105 162 200` (rows 3 and 4 mirror 1 and 0): **64 and 90, not 65 and 91.** The post's whole
   smoothed example rests on these integers (OpenCV's 8-bit blur is fixed point, kernel
   [61, 134, 61]/256).
2. `cv2.threshold(p, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)` should return 40.0 from OpenCV's
   own code and mark columns 3–4 plus (2, 1). On the smoothed patch it should return 105.0 and mark
   columns 3–4 only. **On an x86 build with IPP (the default pip wheel) the 8-bit Otsu value comes
   from IPP**, whose rule inside a flat run is not public: any value from 40 to 199 (raw) or 105 to
   161 (smoothed) is consistent with the post, the mask must not change. Please note which number
   your build prints; the post says the number "may differ" and would be sharper with it.
3. `cv2.THRESH_TRIANGLE` should give 42 (raw) and 160 (smoothed); scikit-image's `threshold_otsu`,
   `threshold_isodata` and `threshold_triangle` should give 40, 122, 41 (raw) and 105, 125, 161
   (smoothed).
4. `cv2.watershed(cv2.cvtColor(p, cv2.COLOR_GRAY2BGR), m)` with `m` int32, `m[1, 1] = 1`,
   `m[2, 3] = 2`, everything else 0, should return the frame all −1 and the interior rows
   `1 1 −1`, `−1 −1 2`, `2 2 2` (columns 1–3). With the markers at (0, 0) and (2, 4) instead, nothing
   should be labelled (frame −1, interior 0).
5. `skimage.segmentation.watershed(skimage.filters.sobel(p))` should return **four** labels, and with
   markers 1 at (0, 0) and 2 at (2, 4), columns 0–2 against 3–4. The exact split of the three dark
   regions depends on floating-point ties and may differ from the post's table; the count may not.
6. `cv2.adaptiveThreshold(t2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 5, 0)` on the
   two-light tiling `t2 = np.hstack([p, np.round(0.2 * p).astype(np.uint8)])` should mark columns 3,
   4, 8 and 9 bright on every row (plus the lit impulse); with block size 9, column 8 should come out
   dark.

If 1 differs, the smoothed worked example needs reopening before publish. If 4 differs, Figure 8,
story 3 and exercise E4 need reopening.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover) on
top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn is computed
in `assets/_data.py` from the definitions — OpenCV's fixed-point blur, Otsu's criterion over both
histograms, OpenCV's and scikit-image's threshold rules replayed, the Sobel relief, scikit-image's and
OpenCV's watersheds replayed, the two-light tiling's local thresholds, and the closed-form mixtures —
and asserted against the article's numbers, so a figure that disagrees with the text fails to build.
The asserts caught two slips in drafting: the smoothed table's first guess used float-rounded values
(65 and 91) where OpenCV returns 64 and 90, and dropping the tail pile-up at grey level 255 moved the
unequal-spreads panel from 125 and 5.1% to 124 and 4.8%. The route gate was run per figure against its
real content. The `source` route was considered and rejected for all ten: four candidate paper
figures are recorded in `research/ledger.md` under **Figure candidates**, and none has verified reuse
rights (IEEE and IOS Press copyright; Elsevier). No figure is a `mermaid` route: none is a
node-and-edge diagram past Q3.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on the ten figures and the cover; on
the social cards only the two known false positives, consecutive serif title lines and the lockup's
`.in`). `lint_visuals.py`: 0 text overflows, 0 arrow reports. Review by eye caught and fixed: a label
touching the y-axis and a legend swatch darker than its bars (Figure 2), a white-on-white legend
swatch and a gap note crossing a threshold line (Figure 3), a spurious spike at 255 from piling the
tails into the last bin and an invisible 1% object (Figure 6), error crosses on the next panel's title
and threshold segments past the frame (Figure 7), marker swatches that did not match the markers and
hatch lines through the −1 labels (Figure 8), a merge node rising from the impulse's own stem and
legend dots that did not match the coloured basins (Figure 9), and on the cards a literal number not
drawn from the data (three places), hatch showing round the −1 plates, and an unexplained orange line.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py && python3 _social.py && python3
../../../../.claude/blog-forge/scripts/render_social.py social/` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-thresholding-and-segmentation.png | placed | template cover in the series house layout, built by `_cover.py` from Figures 6 and 4 — a diagram-design build, not an external generator | — | — | cover-thresholding-and-segmentation.png | A histogram with a dark hump and a bright hump split by one tangerine cut, above a 5×5 grid flooded from two markers into two regions |
| FIG_01 | assets/fig-01-otsu-criterion-thresholding-and-segmentation.png | plot | Otsu's criterion evaluated from the definition over two real histograms | — | — | fig-01-otsu-criterion-thresholding-and-segmentation.png | Two histograms with Otsu's score above: the raw patch scores flat from 40 to 199, the smoothed patch peaks at the cut after 105 |
| FIG_02 | assets/fig-02-variance-split-thresholding-and-segmentation.png | chart | Q1 — nine values computed from the histogram, drawn as stacked bars on one scale | — | — | fig-02-variance-split-thresholding-and-segmentation.png | Nine stacked bars of equal height 3,370.47; the tallest between-class part sits on the shortest within-class part, the cut at 105 |
| FIG_03 | assets/fig-03-three-rules-one-mask-thresholding-and-segmentation.png | placed | Q4 — a real histogram axis beside real 5×5 masks | — | — | fig-03-three-rules-one-mask-thresholding-and-segmentation.png | The smoothed histogram's gap holding thresholds 105, 125 and 160, beside the raw mask with the impulse bright and the smoothed one |
| FIG_04 | assets/fig-04-flooding-from-markers-thresholding-and-segmentation.png | placed | Q4 — small multiples of a real 5×5 grid, one per flood level | — | — | fig-04-flooding-from-markers-thresholding-and-segmentation.png | Five grids flooding the patch's gradient from two markers at levels 0, 304.1, 430, 476.3 and 640, ending in two regions at the step |
| FIG_05 | assets/fig-05-four-minima-four-regions-thresholding-and-segmentation.png | placed | Q4 — small multiples of real grids: minima, then regions under two connectivities | — | — | fig-05-four-minima-four-regions-thresholding-and-segmentation.png | The relief's four regional minima and the four regions they flood into: the impulse's ring cuts the dark side in three |
| FIG_06 | assets/fig-06-histogram-shapes-thresholding-and-segmentation.png | plot | closed-form mixture densities and their criteria, four small multiples | — | — | fig-06-histogram-shapes-thresholding-and-segmentation.png | Four model histograms: equal humps cut well; unequal spreads 4.8% against 0.8%; a 1% object cut through; overlap 15.9% for both |
| FIG_07 | assets/fig-07-two-lights-thresholding-and-segmentation.png | plot | thresholds evaluated from the definitions along one row of the two-light tiling | — | — | fig-07-two-lights-thresholding-and-segmentation.png | One row of the lit and shadowed patch with Otsu's cut at 51 and local thresholds at windows 3, 7 and 9; crosses mark wrong pixels |
| FIG_08 | assets/fig-08-opencv-watershed-thresholding-and-segmentation.png | placed | Q4 — small multiples of real grids replayed from OpenCV's source | — | — | fig-08-opencv-watershed-thresholding-and-segmentation.png | Three cv2.watershed results: border markers erased by the −1 frame, one-pixel markers letting label 2 leak, strokes giving a clean line |
| FIG_09 | assets/fig-09-merge-tree-thresholding-and-segmentation.png | placed | Q5 — a four-leaf merge tree, under nine nodes, no crossings | — | — | fig-09-merge-tree-thresholding-and-segmentation.png | Merge tree of the patch's four basins: the dark three join at 430, or 304.1 diagonally, and meet the bright column only at 640 |
| FIG_10 | assets/fig-10-tooling-map-thresholding-and-segmentation.png | placed | Q5 — a 10 × 3 comparison grid with no edges, the series' closing tooling map | — | — | fig-10-tooling-map-thresholding-and-segmentation.png | Grid comparing OpenCV, scikit-image and MATLAB on Otsu's returned value, local defaults, what watershed floods and its labels |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live). Later spokes are named by
title only, as this series allows, because Part 1 published the spoke list.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* | **live** at https://canery.in/blogs/image-processing-by-hand | the **Level** line: "*Image Processing by Hand* (part 1 of this series)" | the post root |
| Part 1 | live | series line: "Part 1 stated Otsu's criterion in its decide stage" | `#thresholding-ordering-against-a-constant` |
| Part 1 | live | Step 1: "The criterion is flat from 40 to 199, as Part 1 found" | `#thresholding-ordering-against-a-constant` |
| Part 8 — *Canny Edge Detection, Line by Line: Setting the Thresholds* | built 2026-10-12, **not live** | series line: "the Sobel magnitudes that Part 8 … worked out for the same patch"; Step 6: "the patch's Sobel magnitude from Part 8" | `#step-1-the-gradient` once live |
| Part 7 — *Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion* | built 2026-10-11, **not live** | Step 2: "Part 7 … worked the exact-weight values" | `#worked-example` once live |
| *Mathematical Morphology as Lattice Algebra* | planned (Part 12), not built | markers section: "The cleaning operators are the subject of a later spoke" | when live |

## Findings outside this post

- **Part 1 (published) gives the patch's histogram as 16 pixels at 40 and 8 at 200**; the patch has 14
  and 10 (sum 2,815, as `context.md` records). Its conclusion, a flat criterion across the gap, holds.
  This post states the correct counts and does not mention Part 1's; fixing Part 1 is the owner's
  call.
- **OpenCV's 8-bit `GaussianBlur` is fixed point**: for σ = 0.8 the weights become [61, 134, 61]/256,
  and on the patch two pixels round to 64 and 90 where the float convolution rounds to 65 and 91.
  `context.md` describes the shared Gaussian as "what `GaussianBlur(img, (3, 3), 0.8)` builds"; that
  holds for float input. Part 8 said rounding the float values to 8 bits changes no survivor; with
  OpenCV's integers that is worth re-checking before Part 8 publishes.
- **OpenCV's watershed tutorial and `imgproc.hpp` do not mention that the outer one-pixel frame is
  set to −1** before flooding, so markers drawn there vanish. Not reported upstream.
- scikit-image 0.25.0 changed `watershed` when markers do not sit at minima (PR #7071). On this
  patch 0.24 and 0.25 agree on labels; on other images they need not.
