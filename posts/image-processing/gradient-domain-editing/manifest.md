# Asset manifest — gradient-domain-editing

Series `image-processing`, part 14, the last spoke. **Status: local draft assets ready for upload.**
Upload each PNG below to the public `media` bucket under the object key shown (the store is flat, so
every key carries the post slug, as Parts 1–13 do), write the resulting URLs to `urls.txt` in table
order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/gradient-domain-editing/ posts/image-processing/gradient-domain-editing/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/gradient-domain-editing/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract rejects a
non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and the
exercise ladder (E1–E4, the L3 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check these predictions by running them.** Every library result in the
post comes from source read at pinned commits and releases (OpenCV 802cf95 with tags 4.10.0, 4.11.0,
4.12.0, 4.13.0, 4.14.0 and 5.0.0; Luminance HDR 764fb836) or from MathWorks' R2026b and SciPy 1.18.0
documentation, and is replayed line by line in plain Python (`assets/_data.py`, `cv_seamless_clone`);
nothing was run, per the series' contract. `seamlessClone` needs 8-bit 3-channel `src` and `dst`, so
stack the grey arrays: `three = lambda a: np.dstack([a] * 3).astype(np.uint8)`.

1. **The load-bearing one, the MIXED_CLONE spike (E4, the tooling map, Limitations, feed 6).** With
   `spike = np.full((15, 15), 40); spike[7, 7] = 255` (the patch's left three columns padded with 40),
   `sky = np.full((15, 15), 40)` and `mask = np.full((15, 15), 255, np.uint8)`,
   `cv2.seamlessClone(three(spike), three(sky), mask.copy(), (7, 7), cv2.MIXED_CLONE)[..., 0]` should
   be about 147 at (7, 7), about 1 at (7, 6) and (6, 7), and about 78 at (7, 8) and (8, 7); ±1 is
   possible because OpenCV solves in float32 and truncates. The same call with `cv2.NORMAL_CLONE`
   should return 255 at (7, 7) and 40 elsewhere, with a few sky pixels possibly 39 (the float64 replay
   gives nine). If MIXED_CLONE returns 255 at the spike, E4 and the abs(gx − gy) sentences need
   reopening.
2. **A 5×5 source clones nothing.** `p5 = np.array(PATCH)` (the series' patch) and
   `cv2.seamlessClone(three(p5), three(np.full((5, 5), 40)), np.full((5, 5), 255, np.uint8), (2, 2),
   cv2.NORMAL_CLONE)` should return the flat 40 destination unchanged (±1 from truncation): the frame
   is cleared to a 3×3 mask, which the 7×7 erosion removes.
3. **The mask edited in place (4.11.0 onward).** After
   `m = np.full((15, 15), 255, np.uint8); cv2.seamlessClone(three(spike), three(sky), m, (7, 7),
   cv2.NORMAL_CLONE)`, `m` should be 0 on its outer frame and on rows and columns 4–10, and 255 on the
   three-pixel ring between them (the eroded mask, inverted). On 4.10.0 `m` should be unchanged.
4. **The worked example's direct solve.** `scipy.fft.idstn(scipy.fft.dstn(b, type=1) / lam, type=1)`
   with `b` and `lam` as in the post's SciPy block should return 40, 40, 200 / 255, 40, 200 /
   40, 40, 200 to rounding error.
5. **`p` without a `_WIDE` flag.** With a 15 × 15 `src` whose mask is 255 only on rows 2–12 and
   columns 2–6, `cv2.seamlessClone(..., p=(7, 7), cv2.NORMAL_CLONE)` should centre the mask's bounding
   box (columns 2–6) on column 7 of `dst`, so the clone lands at columns 5–9, not at 2–6; with
   `cv2.NORMAL_CLONE_WIDE` it should land at columns 2–6.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover) on
top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn is computed
in `assets/_data.py` — the nine equations, exact rational Gauss–Seidel sweeps, one V-cycle with the
Galerkin coarse coefficient 3/4 (and the re-discretised 1), the sine-transform solve, the closed-form
sweep counts, the four fills of the hole, Fattal's factor on the step row and on the patch, Pérez's
tiling rule, and a line-by-line replay of OpenCV's `seamlessClone` (mask frame, 7×7 erosion, forward
differences, sine transform, clamp and truncation) — and asserted against the article's numbers, so a
figure that disagrees with the text fails to build. The asserts and the figures caught three slips in
drafting: at β = 0.9 the attenuated step is 1.166, not 1.167; the first draft said the first sweep
makes every error negative, but the starting error (minus the patch) is already all negative, and the
real change is the error's shape (56%, 92% and 97% of its energy in the smoothest pattern after zero,
one and two sweeps), which the text now says, and E2's answer repeated the slip; and the cover's alt
text, written before the cover, described a picture it did not draw.

The route gate was run per figure against its real content. The `source` route was considered and
rejected for all ten: three candidate paper figures are recorded in `research/ledger.md` under
**Figure candidates** (Pérez Fig. 1, Fattal Fig. 3: ACM copyright; IPOL Figs. 5 and 10: CC BY-NC-SA,
non-commercial). No figure is a `mermaid` route: Figure 4, the only one with connectors, has seven
stages and no crossings.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on all ten figures; on the cover and
the social cards only the two known false positives, consecutive serif title lines and the lockup's
`.in`). `lint_visuals.py`: 0 text overflows; 8 arrow reports, all free vectors by design (Figure 1's
operation arrow, Figure 3's arrows between columns, Figure 8's loop edges between corner dots),
advisory. Review by eye caught and fixed: notes printed over the legend (Figure 3), a label struck
through by its own connector and arrows ending at stage titles instead of box edges (Figure 4),
value plates cutting gaps in plotted lines (Figures 6 and 7), a non-integer label (244,633.1, Figure
6), a note against the x-axis label (Figure 6), a legend dot that matched one of three marks (Figure
7), a strip run into the legend and tangerine meaning two things (Figure 9), a trap listed under one
mode when it applies to all three (Figure 10), a legend digit that read as the stencil's 4 (Figure 1);
on the cards, collapsed spaces that merged two labels (feed 2), a loop value that read as a negative
rise (feed 7), a caption into the box edge (feed 5), a grid labelled "kept" that showed only the frame
and then, after an edit, a Story frame that lost its solved grid (Story 1), and an overclaim, "sweeps
kill jumps, not bowls" (Story 4).

Re-render: `cd assets && python3 _data.py && python3 _figs.py && python3 _cover.py && python3
_social.py && python3 ../../../../.claude/blog-forge/scripts/render_social.py social/` (paths resolve
from the script directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-gradient-domain-editing.png | placed | template cover in the series house layout, built by `_cover.py` from Figures 1 and 2 — a diagram-design build in the locked palette, not an external generator | — | — | cover-gradient-domain-editing.png | Twelve known frame pixels around nine question marks, an arrow labelled solve, and the frame with the nine pixels back, 255 at the impulse |
| FIG_01 | assets/fig-01-what-is-kept-gradient-domain-editing.png | placed | Q4 — a grid of real values, cell by cell | — | — | fig-01-what-is-kept-gradient-domain-editing.png | The 5×5 patch with its 3×3 interior erased, the kept Laplacian printed in each erased cell, and the twelve frame pixels that touch it kept |
| FIG_02 | assets/fig-02-nine-equations-gradient-domain-editing.png | placed | Q4 — a matrix of real values with its vectors | — | — | fig-02-nine-equations-gradient-domain-editing.png | The nine equations as a 9×9 matrix with 4 on the diagonal and −1 between neighbours, times the patch's nine pixels, equal to b |
| FIG_03 | assets/fig-03-three-sweeps-gradient-domain-editing.png | placed | Q4 — small multiples of real grids | — | — | fig-03-three-sweeps-gradient-domain-editing.png | Four 3×3 iterates and their errors, zero and three Gauss–Seidel sweeps; the largest error falls 255, 89.7, 62.1, 31.1 into a bowl |
| FIG_04 | assets/fig-04-one-v-cycle-gradient-domain-editing.png | placed | Q4 — seven stages each carrying a grid or a number; no crossings | — | — | fig-04-one-v-cycle-gradient-domain-editing.png | One V-cycle: a sweep, the residual, its average 80.1 on one coarse point, the solve 106.8, interpolation back, a sweep; error 15.4 |
| FIG_05 | assets/fig-05-four-fills-gradient-domain-editing.png | placed | Q4 — small multiples of real grids | — | — | fig-05-four-fills-gradient-domain-editing.png | Four fills of the patch's interior: the membrane, guided by the patch, cloned into the shadowed copy in codes with negatives, and in log |
| FIG_06 | assets/fig-06-sweeps-per-digit-gradient-domain-editing.png | plot | Q4 — two curves from closed forms, to scale on log axes | — | — | fig-06-sweeps-per-digit-gradient-domain-editing.png | Log–log curves of sweeps per digit against region width: Gauss–Seidel from 3.3 at width 3 to 244,633 at 1,023; optimal SOR 375 |
| FIG_07 | assets/fig-07-attenuation-factor-gradient-domain-editing.png | plot | Q4 — curves from a closed form, to scale on log axes | — | — | fig-07-attenuation-factor-gradient-domain-editing.png | Fattal's factor against gradient size in units of alpha for beta 0.8, 0.85, 0.9; the step at 25 alpha keeps 0.617 at 0.85 |
| FIG_08 | assets/fig-08-not-a-gradient-gradient-domain-editing.png | placed | Q4 — real values on the cells and edges of a grid | — | — | fig-08-not-a-gradient-gradient-domain-editing.png | One square of the patch after attenuation: 1.028 along row r1, 1.365 along row r2, 0 up both columns; the loop sums to −0.337 |
| FIG_09 | assets/fig-09-seamless-tiling-gradient-domain-editing.png | placed | Q4 — strips of real cells | — | — | fig-09-seamless-tiling-gradient-domain-editing.png | The step row tiled three times, before with a 160 jump at each seam, after Pérez's rule as 120 80 40 160 120 with no jump |
| FIG_10 | assets/fig-10-tooling-map-gradient-domain-editing.png | placed | Q5 — a 7 × 5 comparison grid with no edges, the series' closing tooling map | — | — | fig-10-tooling-map-gradient-domain-editing.png | Tooling map: OpenCV seamlessClone, illuminationChange, textureFlattening, TonemapMantiuk; MATLAB regionfill; SciPy solvers |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live). Later spokes: none, this is
the last.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 2 — *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening* | **live** at https://canery.in/blogs/laplacian-by-hand | the **Level** line: "*The Laplacian by Hand* (part 2 of this series)" | the post root |
| Part 2 | live | series line: "Its one prerequisite is Part 2, … which computed the five-point Laplacian on the patch and closed its section "Keeping the Laplacian instead of the pixels"" | `#keeping-the-laplacian-instead-of-the-pixels` |
| Part 2 | live | The problem: "That is Part 2's five-point stencil used as a constraint instead of a filter." | `#which-discrete-laplacian` |
| Part 2 | live | Worked example, step 1: "On Ω that is Part 2's table" | `#worked-example` |
| Part 11 — *Thresholding and Segmentation: Otsu, Sauvola, Watershed* | built 2026-10-14, **not live** | "A change of light is not a difference": "the shadowed copy that Part 11, *Thresholding and Segmentation: Otsu, Sauvola, Watershed*, set beside the patch" | its local-threshold section once live |

Part 2 ends its Poisson section with "Gradient-domain editing in general — Poisson cloning, HDR
compression, seamless tiling — is its own child post"; once this post is live, that sentence can link
here (the post root). Part 2 is published, so that is an edit to a live post, the owner's call.

## Findings outside this post

- **OpenCV `seamlessClone` edits a single-channel mask in place again, from 4.11.0.** Commit
  860ae77ec9 (2018) fixed issue #12053 by copying the mask; PR #26511 (merged 2024-12-19, the `_WIDE`
  flags) replaced the copy with `return mask.getMat()`, so `seamlessClone` clears the caller's mask
  frame and erodes and inverts its bounding box, and `colorChange`, `illuminationChange` and
  `textureFlattening` erode and invert theirs. In 4.11.0–4.14.0 and 5.0.0. Read from source, not run
  (owner check 3). Not reported upstream.
- **`MIXED_CLONE` compares abs(gx − gy), not the gradient's magnitude.** Pérez et al.'s rule compares
  each edge's two differences; OpenCV compares the difference of the x and y components and takes both
  from the winner, so any gradient with equal components (a one-pixel spike's own, a 45° edge's) never
  wins. Same in every version read. Not reported upstream.
- **The `p` documentation matches only the `_WIDE` flags,** and the `_WIDE` flags' own description
  ("processes a larger source region by considering the entire mask area") does not match their code,
  which only moves the box. The three-pixel erosion is issue #17450, open since 2020.
- **`textureFlattening`'s documentation** gives `high_threshold` as "Value > 100" while its default is
  45. Not used in the post; noted only.
- **Saad's 2-D V-cycle cost** is printed as "≤ 7/3 ηn"; the geometric series over grids a quarter the
  size gives 4/3, which the post derives itself.
- **Fattal's factor at zero central difference** is unbounded by the paper's formula; one
  implementation (Luminance HDR) floors the magnitude at 10⁻⁴, which on the patch magnifies the spike's
  differences 2.46 times. The post states the formula's limit and that floor only.
