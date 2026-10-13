# Asset manifest — canny-line-by-line

Series `image-processing`, part 8. **Status: local draft assets ready for upload.** Upload each
PNG below to the public `media` bucket under the object key shown (the store is flat, so every
key carries the post slug, as Parts 1–7 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/canny-line-by-line/ posts/image-processing/canny-line-by-line/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/canny-line-by-line/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract
rejects a non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and
the exercise ladder (E1–E4, the L3 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check three predictions by running them.** Every OpenCV result in
the post comes from reading `canny.cpp` and `canny.simd.hpp` at commit 802cf95 (and the same
rules at tag 4.10.0) and replaying the integer arithmetic in plain Python; nothing was run, per
the series' contract. With OpenCV's default threading (more than one thread), on the patch
`p = np.full((5, 5), 40, np.uint8); p[:, 3:] = 200; p[2, 1] = 255`:

1. `cv2.Canny(p, 450, 600)` should mark exactly (0, 2), (2, 3) and (4, 2): three dots (the L1 gap).
2. `cv2.Canny(p, 450, 600, L2gradient=True)` should mark (0, 2), (1, 3), (2, 3), (3, 3), (4, 2).
3. `cv2.Canny(cv2.GaussianBlur(p, (3, 3), 0.8), 180, 450, L2gradient=True)` should mark column 3, all five rows.

If any differs, the worked example's step 2 is wrong and needs reopening before publish. One
caveat the post states: with `cv2.setNumThreads(1)` on a build with Intel IPP, `Canny` hands the
call to IPP's own implementation, whose tie rule is not in OpenCV's source, so run the check with
default threading.

**A documentation mismatch worth reporting upstream (not done).** OpenCV's Python Canny tutorial
(`doc/py_tutorials/py_imgproc/py_canny/py_canny.markdown`) lists a 5×5 Gaussian as Canny's first
step and says `cv.Canny()` puts all the steps in one function; `cv::Canny` has no smoothing step.
The C++ tutorial's demo smooths with a 3×3 box `blur` before calling it. The post states both,
with the source, and does not call it a bug.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover)
on top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn is
computed in `_figs.py` from the definitions — the 3×3 Sobel under the replicate border, OpenCV's
suppression rule transcribed from `canny.simd.hpp`, scikit-image's interpolated rule from
`_canny_cy.pyx`, hysteresis as 8-connected components, the shared Gaussian, Devernay's parabola,
OpenCV's Sobel kernel generator and the noise model — and asserted against the article's numbers,
so a figure that disagrees with the text fails to build (the asserts caught a rounding slip: at
exactly 26.8°, cos + sin rounds to 1.343, while the pixel's true angle, 26.83°, gives the
article's 1.344). The route gate was run per figure against its real content. The `source` route
was considered and rejected for all eleven: four candidate paper figures are recorded in
`research/ledger.md` under **Figure candidates**, and none has verified reuse rights (IEEE
copyright; IPOL is CC BY-NC-SA, non-commercial; the BMVA archive states no licence). No figure is
a `mermaid` route: none is a node-and-edge diagram past Q3.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on the eleven figures; on the
cover and the social cards only the two known false positives, consecutive serif title lines and
the lockup's `.in`, both checked by eye). `lint_visuals.py`: 0 text overflows; 8 arrow reports, all free vectors (Figure 1's
gradient arrows and Figure 5's direction arrow). Review by eye caught and fixed: ratio lines
running through region labels (Figure 4), interpolation values printed on dashed outlines and an
angle label on a sector letter (Figure 5), a leader line crossing a threshold line (Figure 9), a
label cut by its own curve (Figure 8), legend swatches that did not match their marks (Figures 2,
3, 4, 5, 7, 9), a Story frame whose grid ran into the takeaway, a feed card that drew surviving
ring pixels as suppressed, and dashed outlines cutting through numbers on two cards.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-canny-line-by-line.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 3's smoothed run — a diagram-design build, not an external generator | — | — | cover-canny-line-by-line.png | A 5×5 grid split by a vertical edge, with a chain of linked dots down the edge from one tangerine seed, and two hollow dots left unlinked |
| FIG_01 | assets/fig-01-patch-gradient-canny-line-by-line.png | placed | Q4 — a grid of real values with each pixel's gradient vector drawn to scale | — | — | fig-01-patch-gradient-canny-line-by-line.png | The patch's Sobel gradient as arrows: 640 on both sides of the step, a ring of shorter arrows round the impulse, and none on the impulse itself |
| FIG_02 | assets/fig-02-suppression-l2-l1-canny-line-by-line.png | placed | Q4 — small multiples of real grids: survivors and direction bins under each norm | — | — | fig-02-suppression-l2-l1-canny-line-by-line.png | Suppression on the raw patch: with L2 a connected five-pixel line plus a ring of five; with L1 only three line pixels, rows r1 and r3 blank |
| FIG_03 | assets/fig-03-hysteresis-chains-canny-line-by-line.png | placed | Q4 — small multiples of real grids with their 8-connections drawn | — | — | fig-03-hysteresis-chains-canny-line-by-line.png | Hysteresis at 450 and 180: on the raw patch the ring joins the line at two corners, all ten pixels kept; smoothed, a clean column of five |
| FIG_04 | assets/fig-04-threshold-plane-canny-line-by-line.png | plot | regions of the (low, high) plane computed from the definitions, three versions of the patch | — | — | fig-04-threshold-plane-canny-line-by-line.png | Maps of the low–high threshold plane: raw L1 never gives the line alone, raw L2 only above low 430, smoothed in a wide band crossed by ratios 2 and 3 |
| FIG_05 | assets/fig-05-bins-and-interpolation-canny-line-by-line.png | placed | Q4 — geometry: the bins, and the gradient line through a real 3×3 neighbourhood | — | — | fig-05-bins-and-interpolation-canny-line-by-line.png | OpenCV's four direction bins, and (r1, c1) of the smoothed patch: rounding compares 222.2 with 316.2, interpolation with 198.8 and 133.0 |
| FIG_06 | assets/fig-06-tie-rules-canny-line-by-line.png | placed | Q4 — small multiples of one real profile under three comparison rules | — | — | fig-06-tie-rules-canny-line-by-line.png | The profile 0, 640, 640, 0 under three tie rules: strict keeps no pixel, OpenCV's keeps the left one, scikit-image's keeps both |
| FIG_07 | assets/fig-07-sub-pixel-position-canny-line-by-line.png | plot | closed-form parabolas through the worked magnitudes | — | — | fig-07-sub-pixel-position-canny-line-by-line.png | Parabolas through three magnitudes: row r0 peaks at column 2.5, where the step is; row r2, lowered by the impulse, peaks at 2.90 |
| FIG_08 | assets/fig-08-threshold-units-canny-line-by-line.png | chart | Q1 — responses computed from OpenCV's kernels on one log scale, beside a closed-form curve | — | — | fig-08-threshold-units-canny-line-by-line.png | Log-scale bars: the 160-level step reads 640, 7,680 and 102,400 at apertures 3, 5 and 7; beside them L1 over L2 rising to 1.41 at 45° |
| FIG_09 | assets/fig-09-noise-thresholds-canny-line-by-line.png | plot | closed-form Rayleigh density under a stated noise model | — | — | fig-09-noise-thresholds-canny-line-by-line.png | Rayleigh density of flat-region magnitude for noise of 2 levels, with the low threshold at 14.9, the high at 29.7, and a 20-level step at 80 |
| FIG_10 | assets/fig-10-a-contrario-length-canny-line-by-line.png | plot | closed-form curve under a stated model (Rayleigh tail, N = 10⁶) | — | — | fig-10-a-contrario-length-canny-line-by-line.png | Required contrast against chain length, falling as one over its square root: half the one-pixel threshold at length 4, a third at length 9 |
| FIG_11 | assets/fig-11-tooling-map-canny-line-by-line.png | placed | Q5 — a 12 × 3 comparison grid with no edges, the series' closing tooling map | — | — | fig-11-tooling-map-canny-line-by-line.png | Grid comparing OpenCV, scikit-image and MATLAB on smoothing, border, norm, suppression, ties, threshold tests, linking, units and defaults |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live). Later spokes are named by
title only, as this series allows, because Part 1 published the spoke list.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* | **live** at https://canery.in/blogs/image-processing-by-hand | series line: "This is part 8 of *Image Processing by Hand*. Part 1 drew Canny's method as four steps" | `#steps-3-and-4-localise-and-commit` |
| Part 1 | live | the **Level** line: "*Image Processing by Hand* (part 1 of this series)" | the post root |
| Part 1 | live | The problem: "Part 1 split Canny's method into four steps" | `#detecting` |
| Part 1 | live | The problem: "Part 1 showed that L1 reads a 45° edge 41% high" | `#step-2-combine-the-two-derivatives` |
| Part 2 — *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening* | **live** at https://canery.in/blogs/laplacian-by-hand | NMS section: "the zero-crossings of the Laplacian, belongs to Part 2, *The Laplacian by Hand*" | `#zero-crossings-why-the-laplacian-finds-edges-twice` |
| Part 4 — *Kernel Design: Separability, Borders, Optimised Derivatives* | built 2026-09-25, **not live** | Step 1: "the border zero of Part 4, *Kernel Design…*" | `#what-does-the-border-do-to-a-derivative` once live |
| Part 4 | not live | Units: "a ramp rising one grey level per pixel reads 8, Part 4's factor" | the post root once live |
| Part 7 — *Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion* | built 2026-10-11, **not live** | Step 4: "Part 7, *Edge-Preserving Smoothing…*, worked this blur" | `#worked-example` once live |
| *The Structure Tensor: Harris, Shi–Tomasi, and Optical Flow* | planned (Part 9), not built | NMS section, junctions: "that is a later spoke" | when live |
| *Scale Space and SIFT: Why σ Is a Search Dimension* | planned (Part 10), not built | Limitations: "the subject of the later spoke" | when live |

## Findings outside this post

- OpenCV's Python Canny tutorial describes a Gaussian step that `cv::Canny` does not perform
  (above). Not reported upstream.
- Canny's own 1983 report (MIT AI-TR-720) was not reachable (DSpace returned 405); its suppression
  scheme is cited through Grompone von Gioi & Randall's IPOL article, which quotes it by section.
