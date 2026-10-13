# Asset manifest — the-structure-tensor

Series `image-processing`, part 9. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1–8 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/the-structure-tensor/ posts/image-processing/the-structure-tensor/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/the-structure-tensor/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and
the exercise ladder (E1–E5, the L4 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check these predictions by running them.** Every OpenCV result in the
post comes from reading `corner.cpp`, `featureselect.cpp` and `spatialgradient.cpp` at commit
802cf95 (and the same rules at tag 4.10.0) and replaying the arithmetic in plain Python; nothing
was run, per the series' contract. On the patch
`p = np.full((5, 5), 40, np.uint8); p[:, 3:] = 200; p[2, 1] = 255`:

1. `cv2.goodFeaturesToTrack(p, 10, 0.01, 1)` should return one point, `[[[2., 2.]]]`; with
   `useHarrisDetector=True` the same point.
2. `cv2.cornerMinEigenVal(p, 3, 3)[2, 2]` should be about 0.04937, and the maximum of that map
   (about 0.06580) should sit at `[0, 1]` and `[4, 1]`.
3. `cv2.cornerHarris(p, 3, 3, 0.04)[2, 3]` should be about +0.000363 and
   `cv2.cornerHarris(p, 3, 3, 0.06)[2, 3]` about −0.000317 (the k disagreement).
4. `cv2.goodFeaturesToTrack(p, 10, 0.8, 1)` should return `None` (exercise E4).
5. With `p[2, 1] = 120`, `cv2.goodFeaturesToTrack(p, 10, 0.01, 1)` should return `[[[1., 2.]]]`
   (exercise E3).

If any differs, the worked example's steps 3–4 are wrong and need reopening before publish. The
default border (reflect-101) keeps `cornerHarris` on OpenCV's own code even in IPP builds; with
`BORDER_REPLICATE` or `BORDER_CONSTANT` an IPP build hands it to IPP, whose arithmetic the post
does not describe.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover)
on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn is
computed in `_figs.py` from the definitions — 3×3 Sobel under reflect-101, the box and the series'
Gaussian windows, eigenvalues, every score, `goodFeaturesToTrack`'s rule transcribed from
`featureselect.cpp`, one Lucas–Kanade step on the patch moved one pixel right — and asserted
against the article's numbers, so a figure that disagrees with the text fails to build. The route
gate was run per figure against its real content. The `source` route was considered and rejected
for all twelve: the two candidate paper figures are recorded in `research/ledger.md` under
**Figure candidates**, and neither has verified reuse rights (the BMVA archive states no licence;
IPOL is CC BY-NC-SA, non-commercial). No figure is a `mermaid` route: none is a node-and-edge
diagram past Q3.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on the twelve figures and the
cover). Review by eye caught and fixed: a hard-coded boundary value in Figure 5's inset that was
wrong (71,250; the computed value is 71,185), a note in Figure 7 that counted six vertical
gradients where the window has four, eyebrows whose uppercase changed notation (dᵀMd → DᵀMD,
t → T, r2 → R2) in Figures 4, 6, 7, 10 and 11, a hatch overlay that lightened zero-valued cells in
Figure 3 against the series' high-is-bright rule, weight grids shaded heavy-is-dark on two scales in
Figure 11, labels printed on lines in Figures 5, 6 and 11, a legend swatch in a different blue from
its marks in Figure 1, unequal u and v scales distorting Figure 9's ellipses, a mark with no legend
entry in Figure 5, dead bands above the legend in Figures 5 and 9, and a cover whose glyphs touched.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-the-structure-tensor.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 2's row-r2 tensors — a diagram-design build, not an external generator | — | — | cover-the-structure-tensor.png | A 5×5 grid split by a vertical step with one bright pixel, and three ellipses over it: a flat line, a narrow ellipse and a round one |
| FIG_01 | assets/fig-01-patch-gradient-the-structure-tensor.png | placed | Q4 — a grid of real values with vectors to scale, plus the five row-r2 windows drawn as small multiples | — | — | fig-01-patch-gradient-the-structure-tensor.png | The patch's Sobel gradient as arrows, 640 on both sides of the step and a ring round the impulse, with four 3×3 windows on row r2 outlined |
| FIG_02 | assets/fig-02-row-r2-tensors-the-structure-tensor.png | placed | Q4 — small multiples of real matrices drawn as their shape | — | — | fig-02-row-r2-tensors-the-structure-tensor.png | Five ellipses for row r2: a vertical line at c0, rounder ellipses at c1 and c2, a flat sliver at c3 and a horizontal line at c4 |
| FIG_03 | assets/fig-03-good-features-verdict-the-structure-tensor.png | placed | Q4 — a grid of real values with the selection rule and a decomposition of the winning tensor | — | — | fig-03-good-features-verdict-the-structure-tensor.png | The 5×5 map of smaller eigenvalues: the largest, 616,156, on the excluded top and bottom rows; the one kept local maximum at (r2, c2) |
| FIG_04 | assets/fig-04-shift-cost-surfaces-the-structure-tensor.png | plot | closed-form quadratic forms of the worked matrices | — | — | fig-04-shift-cost-surfaces-the-structure-tensor.png | Contour plots of the shift cost over a ±1 pixel square: a vertical trough at c4, a long bowl at c3, rounder bowls at c2 and c1 |
| FIG_05 | assets/fig-05-eigenvalue-plane-the-structure-tensor.png | plot | geometry of the scores to scale, with the worked eigenvalues as points | — | — | fig-05-eigenvalue-plane-the-structure-tensor.png | The eigenvalue plane to scale: Harris rays for k = 0.04 and 0.06, Förstner's roundness rays, and row r2's five windows as points |
| FIG_06 | assets/fig-06-scores-against-ratio-the-structure-tensor.png | plot | closed-form curves of each score against the eigenvalue ratio | — | — | fig-06-scores-against-ratio-the-structure-tensor.png | Scores against the eigenvalue ratio: Harris for k = 0.04 and 0.06 crosses zero at 0.044 and 0.069; Shi–Tomasi and Förstner stay above |
| FIG_07 | assets/fig-07-why-squares-the-structure-tensor.png | placed | Q4 — the real gradient vectors and their doubled angles drawn to scale | — | — | fig-07-why-squares-the-structure-tensor.png | The impulse window's nine gradients: as vectors the vertical parts cancel; as doubled angles they add to a length of 426,700 |
| FIG_08 | assets/fig-08-orientation-field-the-structure-tensor.png | placed | Q4 — a grid of 25 real tensors drawn as oriented glyphs | — | — | fig-08-orientation-field-the-structure-tensor.png | All 25 tensors as ellipses: vertical lines on c0, horizontal lines on c4, round ellipses near the impulse tilting up to 50 degrees |
| FIG_09 | assets/fig-09-aperture-and-precision-the-structure-tensor.png | plot | closed-form error ellipses and one-step solutions of the worked matrices | — | — | fig-09-aperture-and-precision-the-structure-tensor.png | The plane of possible motions: at c4 a vertical line of equally good solutions; at c3, c2 and c1 error ellipses, longest vertically at c3 |
| FIG_10 | assets/fig-10-linearisation-the-structure-tensor.png | plot | real frame differences against the linear model's prediction, one row | — | — | fig-10-linearisation-the-structure-tensor.png | Row r2 before and after a one-pixel move: at c2 the gradient predicts the pixel darkens by 26 but it brightens by 215 as the impulse arrives |
| FIG_11 | assets/fig-11-window-and-weights-the-structure-tensor.png | placed | Q4 — the footprint, the two weight grids to scale, and one ratio under each | — | — | fig-11-window-and-weights-the-structure-tensor.png | A 3×3 derivative in a 3×3 window reads 5×5; box against Gaussian weights; (r2, c3)'s ratio is 0.057 under the box, 0.022 under the Gaussian |
| FIG_12 | assets/fig-12-tooling-map-the-structure-tensor.png | placed | Q5 — an 11 × 3 comparison grid with no edges, the series' closing tooling map | — | — | fig-12-tooling-map-the-structure-tensor.png | Grid comparing OpenCV, scikit-image and MATLAB on derivative, window, border, response, units, selection and Lucas–Kanade defaults |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live). Later spokes are named by
title only, as this series allows, because Part 1 published the spoke list.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* | **live** at https://canery.in/blogs/image-processing-by-hand | series line: "This is part 9 of *Image Processing by Hand*. Part 1 built this matrix in one section" | `#the-same-construction-one-dimension-up-corners` |
| Part 1 | live | the **Level** line: "*Image Processing by Hand* (part 1 of this series)" | the post root |
| Part 1 | live | The problem: "Part 1 introduced $M$, its eigenvalues … and Harris's response" | `#the-same-construction-one-dimension-up-corners` |
| Part 1 | live | Figure 5's caption: "The plane Part 1 sketched, drawn to scale" | `#the-same-construction-one-dimension-up-corners` |
| Part 8 — *Canny Edge Detection, Line by Line: Setting the Thresholds* | built 2026-10-12, **not live** | series line: "Part 8, *Canny Edge Detection, Line by Line…*, ended where non-maximum suppression breaks at junctions" | `#where-suppression-fails` once live |
| Part 8 | not live | Worked example, step 1: "Part 8 tabulated the patch's Sobel gradient under the replicate border" | `#step-1-the-gradient` once live |
| *Scale Space and SIFT: Why σ Is a Search Dimension* | planned (Part 10), not built | Which window: "Choosing the scale belongs to the later spoke" | when live |

## Findings outside this post

- OpenCV's documentation for `cornerEigenValsAndVecs` calls the stored eigenvalues "non-sorted",
  but `eigen2x2` in `corner.cpp` always writes the larger one first. The corner functions'
  documentation does not mention the 1/(2^(ksize−1) · blockSize · 255) scale applied to each
  derivative. Neither was reported upstream.
- `goodFeaturesToTrack`'s documentation says corners closer than "maxDistance" are thrown away; the
  parameter is `minDistance`. Not reported upstream.
- The survey cited for the 0.04 convention says Harris and Stephens used Sobel derivatives; their
  paper uses (−1, 0, 1). The post follows the paper.
