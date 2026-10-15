# Asset manifest — colour-and-gamma

Series `image-processing`, part 13. **Status: local draft assets ready for upload.** Upload each PNG
below to the public `media` bucket under the object key shown (the store is flat, so every key carries
the post slug, as Parts 1–12 do), write the resulting URLs to `urls.txt` in table order, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/colour-and-gamma/ posts/image-processing/colour-and-gamma/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/colour-and-gamma/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract rejects a
non-URL there, so it must be resolved before upload.

**Lab grade:** G0 — by hand, the series invariant: nothing is executed, so there is no `lab/` and the
exercise ladder (E1–E4, the L3 requirement) lives in the post's `## Try it yourself`.

**Before publishing, please check these predictions by running them.** Every library result in the
post comes from source read at pinned commits and releases (OpenCV 802cf95 with tags 4.10.0, 4.14.0
and 5.0.0; scikit-image b700edc with v0.26.0; Pillow 12.3.0; KleidiCV 26.03) or from MathWorks'
R2026b documentation, and is replayed in plain Python; nothing was run, per the series' contract. With
`px = np.array([[[255, 200, 40]]], np.uint8)` (BGR order, the azure) and `rgb = px[..., ::-1]`:

1. **The load-bearing one:** `cv2.cvtColor(px, cv2.COLOR_BGR2GRAY)` should be 158 and
   `Image.fromarray(rgb).convert("L")` should be 158 too. If either differs, step 4, Figure 2, Figure
   9, feeds 2 and 7, Story 2, the Insights and E4 need reopening.
2. `cv2.cvtColor(px, cv2.COLOR_BGR2XYZ)[0, 0, 1]` should be 170 (the matrix on codes, no decode), and
   `cv2.cvtColor(px.astype(np.float32) / 255, cv2.COLOR_BGR2XYZ)[0, 0, 1]` about 0.6664.
3. `cv2.cvtColor(px.astype(np.float32) / 255, cv2.COLOR_BGR2Lab)` should be about (75.44, −20.77,
   −38.02), and the 8-bit `cv2.cvtColor(px, cv2.COLOR_BGR2Lab)` about (192, 107, 90); the 8-bit path
   runs through lookup tables, so ±1 is possible.
4. `skimage.color.rgb2gray(rgb)` should be 0.66653, `skimage.color.rgb2xyz(rgb)[0, 0, 1]` 0.48974,
   `skimage.color.rgb2lab(rgb)` about (75.44, −20.77, −38.01), and
   `skimage.color.rgb2lab(np.ones((1, 1, 3)), illuminant="D50")` about (100, −2.39, −19.36).
5. OpenCV and Pillow should disagree on `(R, G, B) = (0, 1, 201)`: `cv2.cvtColor` 23, Pillow 24 (exact
   luma 23.501). The post's count of 21,745 such colours comes from replaying both integer formulas.
6. `cv2.GaussianBlur(np.float32([[40, 40, 40, 200, 200]]), (3, 1), 0.8)` should give 78.24 and 161.76
   at c2 and c3; decoding first, blurring, and encoding gives 109.42 and 177.89. (On 8-bit input
   OpenCV's GaussianBlur is fixed point, Part 11's finding, so use float.)

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover) on
top of `assets/_build.py`; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn is computed
in `assets/_data.py` from the standards' constants — the sRGB curve with the IEC and 1996 thresholds,
the 4-decimal, exact (CSS) and six-decimal (OpenCV and scikit-image) matrices, CIELAB with the CIE's
fractions, the luminance rows from the BT.709, NTSC 1953 and BT.601 primaries, the blurred step and
impulse in both encodings, the codes per lightness band, OpenCV's and Pillow's integer luma, and one
sweep over all 16,777,216 8-bit colours — and asserted against the article's numbers, so a figure that
disagrees with the text fails to build. `_data.py` also reads the CIE's 1931 colour-matching and V(λ)
tables (`_cie_xyz_1931_2deg.csv`, `_cie_sle_photopic.csv`, CC BY-SA 4.0, private build inputs) to plot
the spectral locus and to check that ȳ(λ) and V(λ) are identical. The asserts caught four slips in
drafting: the lower crossing of the 12.92 line is 0.03815, not 0.03816; green's luma error in L* is
25.8, not 25.7; the two greys are 28 levels apart once rounded, not 27; and the 1996 threshold 0.03928
is the tangent value 0.055/1.4 = 0.0392857 truncated, not rounded.

The route gate was run per figure against its real content. The `source` route was considered and
rejected for all nine: two candidate paper figures are recorded in `research/ledger.md` under **Figure
candidates**, neither with verified reuse rights (SPIE/Poynton, IS&T). No figure is a `mermaid` route:
none is a node-and-edge diagram past Q3. Figure 5's spectral locus is plotted from the CIE's table
(CC BY-SA 4.0), credited in the caption.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on figures 2–9 and the cover; on
Figure 1 five "spills" that are the code labels on their own white plates over the 13-pixel gradient
cells, a false positive; on the social cards only the two known false positives, consecutive serif
title lines and the lockup's `.in`). `lint_visuals.py`: 0 text overflows; 3 arrow reports, all Figure
7's free vectors between plot points, advisory. Swatch colours were read back from the PNGs: the azure
is (40, 200, 255) and the greys 158 and 186 exactly, in a figure and on a card. Review by eye caught
and fixed: value labels on plotted lines and a label cut off at the canvas edge (Figure 3), a reference
line through bar labels (Figure 4), shared vertices drawn in the wrong colour, a label on an edge, a
wavelength label on the axis and a stray unit (Figure 5), a difference chart that ran into its note and
printed −0.0 (Figure 6), a plot that ran off the canvas, a legend over the axis and a label on the
a* = 0 line (Figure 7), labels touching axes (Figures 1, 5, 8), the luminance grey's L* shown for the
rounded code (Figure 2); on the cards, a label on the horseshoe (feed 3), a legend without swatches
(feed 6), a title count a reader could dispute (feed 7, retitled), two labels on lines (Story 1), and
low-contrast text on mid-grey swatches (feed 1, Story 3).

Re-render: `cd assets && python3 _data.py && python3 _figs.py && python3 _cover.py && python3
_social.py && python3 ../../../../.claude/blog-forge/scripts/render_social.py social/` (paths resolve
from the script directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-colour-and-gamma.png | placed | template cover in the series house layout, built by `_cover.py` from Figure 8's first chord — a diagram-design build in the locked palette, not an external generator | — | — | cover-colour-and-gamma.png | The sRGB curve over linear light with a chord from code 40 to code 200; a tangerine gap marks the chord's 120 below the curve's 148.7 |
| FIG_01 | assets/fig-01-three-rulers-colour-and-gamma.png | plot | Q4 — three aligned scales drawn to their own spacing, joined at real values | — | — | fig-01-three-rulers-colour-and-gamma.png | Three aligned rulers, sRGB code, lightness L* and linear light, with codes 40, 119, 128, 200 and 255 joined to their places on the other two |
| FIG_02 | assets/fig-02-one-pixel-two-greys-colour-and-gamma.png | placed | Q5 — seven boxes in two paths, a real number on every edge, true-colour swatches | — | — | fig-02-one-pixel-two-greys-colour-and-gamma.png | The azure (40, 200, 255) decoded, turned into XYZ and Lab, with luma 158 taken from the codes and the luminance grey 186 from Y |
| FIG_03 | assets/fig-03-blur-in-two-encodings-colour-and-gamma.png | chart | Q1-like — ten values computed from closed forms, in two units, with the rows as true greys | — | — | fig-03-blur-in-two-encodings-colour-and-gamma.png | The step 40 40 40 200 200 blurred in codes (78.2 and 161.8 at the edge) and in light (109.4 and 177.9), plotted as codes and as light |
| FIG_04 | assets/fig-04-codes-per-lightness-colour-and-gamma.png | chart | Q1-like — twenty counts computed from the definitions, paired bars | — | — | fig-04-codes-per-lightness-colour-and-gamma.png | Codes per tenth of lightness: sRGB spends 21 to 29 codes on every band, linear 8-bit coding 3 on the darkest band and 61 on the brightest |
| FIG_05 | assets/fig-05-primaries-and-weights-colour-and-gamma.png | plot | Q4 — geometry: the CIE locus from its table and the standards' primaries and whites to scale | CIE 1931 2° colour-matching functions, doi:10.25039/CIE.DS.xvudnb9b (spectral locus only) | CC BY-SA 4.0 (dataset; credited in the caption) | fig-05-primaries-and-weights-colour-and-gamma.png | CIE xy diagram with the spectral locus and the BT.709, NTSC 1953 and BT.601 625-line triangles, each with its luminance weights |
| FIG_06 | assets/fig-06-luma-against-luminance-colour-and-gamma.png | chart | Q4 — true-colour and true-grey swatches beside their values, with the differences as bars | — | — | fig-06-luma-against-luminance-colour-and-gamma.png | Nine colours with their luma and luminance greys: red 76 and 127, green 150 and 220, blue 29 and 76, pink 206 and 200, grey 128 twice |
| FIG_07 | assets/fig-07-lab-and-its-white-colour-and-gamma.png | plot | Q4 — positions in the a*b* plane at equal scale on both axes | — | — | fig-07-lab-and-its-white-colour-and-gamma.png | The a*b* plane with the azure under D65, CSS's adapted D50 and scikit-image's unadapted D50, and sRGB white moved to b* −19.4 |
| FIG_08 | assets/fig-08-chords-under-the-curve-colour-and-gamma.png | plot | Q4 — a curve and two chords to scale | — | — | fig-08-chords-under-the-curve-colour-and-gamma.png | The sRGB curve with chords from code 40 to 200 and 0 to 255; at the average light the chords give 120 and 127.5, the curve 148.7 and 187.5 |
| FIG_09 | assets/fig-09-tooling-map-colour-and-gamma.png | placed | Q5 — a 9 × 4 comparison grid with no edges, the series' closing tooling map | — | — | fig-09-tooling-map-colour-and-gamma.png | Grid comparing OpenCV, scikit-image, Pillow and MATLAB on grey weights, decoding before grey, XYZ and Lab, Lab white and resize |

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01, and
since 2026-10-09 earlier parts are named whether or not they are live). Later spokes are named by
title only, as this series allows; this post names none.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Image Processing by Hand* | **live** at https://canery.in/blogs/image-processing-by-hand | the **Level** line: "*Image Processing by Hand* (part 1 of this series)" | the post root |
| Part 1 | live | series line: "Part 1 warned in one paragraph that `BGR2GRAY` returns luma rather than luminance" | `#limitations-and-common-mistakes` |
| Part 1 | live | "Why codes average dark": "Part 1's 3×3 box gave 64 at the impulse and its σ = 0.8 Gaussian gave 98.6" | `#worked-example` (its box-mean and Gaussian steps) |
| Part 3 — *Resampling and Aliasing: Interpolation Kernels in Practice* | built 2026-09-25, **not live** | series line: "sent the question of resizing gamma-encoded values here too"; "Two limits apply": "the negative lobes of the bicubic and Lanczos kernels in Part 3" | `#limitations-and-common-mistakes`; `#what-does-each-kernel-do-to-the-spectrum` once live |

Part 3 names this post as "Part 13, *Colour and Gamma*"; once this post is live, that mention can link
here (`#which-operations-need-linear-light`).

## Findings outside this post

- **OpenCV's Lab documentation omits the sRGB decode.** `colors.markdown` describes RGB → Lab as the
  matrix applied to R, G, B scaled to 0–1, but `COLOR_BGR2Lab` decodes sRGB first (`is_sRGB`), and only
  the `LBGR` codes skip it. Same at 4.10.0, 4.14.0, 5.0.0 and 802cf95. Not reported upstream.
- **OpenCV's `BGR2XYZ` and scikit-image's `rgb2gray`** both return a BT.709-weighted average of codes
  (170/255 and 0.6665 on the azure) while their names or documentation promise CIE XYZ and luminance.
  Behaviour, not a bug, in OpenCV's case (its docs treat the conversion as linear); scikit-image's
  docstring calls the result luminance. Not reported upstream.
- **scikit-image's module docstring** describes its central space as linear sRGB "w/o gamma
  correction", which `rgb2xyz`'s decode contradicts. Not reported upstream.
- **The plan's luminance row (0.2127) is OpenCV's documented 0.212671 rounded**, not the standard's
  0.2126; the post uses 0.2126. `plan.md` is not edited.
