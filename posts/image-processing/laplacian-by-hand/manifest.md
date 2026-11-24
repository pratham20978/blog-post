# Upload manifest — laplacian-by-hand

Every placeholder in `blog.md`, in order of appearance. Upload each file to object
storage, put the resulting public URLs into `urls.txt` **in this row order**, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/laplacian-by-hand/ posts/image-processing/laplacian-by-hand/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/laplacian-by-hand/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery
contract rejects a non-URL there, so it must be resolved before upload.

| Placeholder | File | Live URL | Alt text |
|---|---|---|---|
| COVER | `assets/cover-laplacian-by-hand.png` | `https://minio.canery.in/media/cover-laplacian-by-hand.png` | The Laplacian stencil at the centre with five arrows out to sharpening, zero-crossing edges, blob scale selection, the pyramid and Poisson editing |
| FIG_01 | `assets/fig-01-two-signatures-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-01-two-signatures-laplacian-by-hand.png` | The patch's middle row 40, 40, 40, 200, 200 as a step; below it the first difference with one peak of 160 on the step; below that the second difference, +160 then −160, crossing zero at column 2.5. |
| FIG_02 | `assets/fig-02-clean-windows-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-02-clean-windows-laplacian-by-hand.png` | Two 3 by 3 windows from the clean patch: at (2,2) the four neighbours sum to 320 and 320 − 4 × 40 = +160; at (2,3) they sum to 640 and 640 − 4 × 200 = −160. The zero-crossing lies between them. |
| FIG_03 | `assets/fig-03-impulse-windows-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-03-impulse-windows-laplacian-by-hand.png` | Three 3 by 3 windows from the patch with the impulse: at (2,1) the centre 255 gives 160 − 1020 = −860; at (2,2) the left neighbour 255 gives 535 − 160 = 375; at (1,2) the impulse sits diagonally, outside the stencil, and the result stays 160. |
| FIG_04 | `assets/fig-04-mean-minus-centre-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-04-mean-minus-centre-laplacian-by-hand.png` | The window at (2,2) read two ways: as stencil arithmetic, 320 − 4 × 40 = 160, and as the neighbour mean 80 minus the centre 40, times four. Below, the impulse window: mean 40 minus centre 255 is −215, times four is −860. |
| FIG_05 | `assets/fig-05-five-stencils-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-05-five-stencils-laplacian-by-hand.png` | Five 3 by 3 stencils with their weights and scale factors: five-point ×1, diagonal ×2, eight-neighbour ×3, OpenCV ksize=3 with 2 at the corners and −8 at the centre ×4, and the nine-point stencil divided by 6, ×1. |
| FIG_06 | `assets/fig-06-transfer-functions-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-06-transfer-functions-laplacian-by-hand.png` | Transfer-function magnitude against frequency from 0 to π: the continuous ω² curve ends at 9.87, the five-point diagonal at 6.42, the nine-point diagonal at 4.70, and both stencils along the axis at 4.00. |
| FIG_07 | `assets/fig-07-sharpening-halo-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-07-sharpening-halo-laplacian-by-hand.png` | The middle row three times: the original step 40, 40, 40, 200, 200; its Laplacian 0, +160, −160 at c1 to c3; and the sharpened row, where −120 clips to 0 on the dark side and 360 clips to 255 on the bright side. |
| FIG_08 | `assets/fig-08-mexican-hat-dog-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-08-mexican-hat-dog-laplacian-by-hand.png` | The Laplacian of Gaussian at σ = 1 against radius: a negative lobe reaching −0.191 at the centre with zeros at ±1.41σ, and the difference of Gaussians at ratio 1.6 drawn over it, reaching −0.097 with zeros at ±1.76σ. |
| FIG_09 | `assets/fig-09-log-kernel-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-09-log-kernel-laplacian-by-hand.png` | A 5 by 5 grid of weights: the centre −0.591 and its four neighbours −0.1123 shaded as the negative disc, the diagonals +0.021, the outer ring 0.1248 on the axes and 0.0571 beside them, zeros in the corners; all 25 sum to zero. |
| FIG_10 | `assets/fig-10-phantom-edges-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-10-phantom-edges-laplacian-by-hand.png` | A model profile with two nearby rising steps, 40 to 120 to 200; its first derivative with two peaks and a dip between them; its second derivative with three zero-crossings, the two under the peaks marked authentic and the one under the dip marked phantom. |
| FIG_11 | `assets/fig-11-canny-decomposition-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-11-canny-decomposition-laplacian-by-hand.png` | A straight edge, dark on the left and bright on the right, with axis n across it and axis t along it; beside it the Laplacian written as the second derivative across, which carries the edge, plus the second derivative along, zero on a straight edge and noise elsewhere. |
| FIG_12 | `assets/fig-12-scale-selection-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-12-scale-selection-laplacian-by-hand.png` | The scale-normalised response at the centre against σ from 0.5 to 4: a bar of width 3 peaks at σ = 1.5 with 77.4, and a disc of radius 3 peaks at σ = 2.12 with 117.7. |
| FIG_13 | `assets/fig-13-scale-space-cube-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-13-scale-space-cube-laplacian-by-hand.png` | A stack of five image planes drawn as layers along a vertical scale axis labelled with sigma values increasing by a factor k, each plane the scale-normalised Laplacian response, with one pixel on the middle plane highlighted and its 8 spatial neighbours plus the 9 pixels above and 9 below marked as the 26 comparisons |
| FIG_14 | `assets/fig-14-laplacian-pyramid-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-14-laplacian-pyramid-laplacian-by-hand.png` | Flowchart of a two-level pyramid: the image g0 passes through REDUCE, blur and keep every other sample, to g1, and g1 through REDUCE to g2, the residual, stored whole as L2; each level minus the EXPAND of the level above gives L0 = g0 − E(g1), fine detail, and L1 = g1 − E(g2), coarser detail; a dashed return path expands and adds L1, then L0, to give g0 again |
| FIG_15 | `assets/fig-15-poisson-editing-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-15-poisson-editing-laplacian-by-hand.png` | A source image whose Laplacian is transplanted into a region Ω of a target image; on the boundary of Ω the pixels are the target's, inside Ω the unknown pixels satisfy one five-point equation each, ∇²f = ∇²g. |
| FIG_16 | `assets/fig-16-tooling-map-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-16-tooling-map-laplacian-by-hand.png` | The tooling map: six jobs, each with its call and an alternative — the five-point Laplacian ×1, OpenCV's ksize=3 ×4 with scale=0.25 to compare, the Laplacian of Gaussian with no σ², blob scale selection with σ² or 1/(k−1), the pyramid, and Poisson editing as a sparse solve. |

## Notes

- **Resolved 2026-09-14.** All 17 images are live in MinIO at
  `https://minio.canery.in/media/<asset filename>` — the local PNGs were renamed with a
  `-laplacian-by-hand` suffix before upload so they cannot collide with the parent post's
  figures in the same bucket. `urls.txt` holds the resolved list and `blog.md` is already
  filled; the pre-fill copy is `blog.md.bak`. A revised figure therefore needs a new
  filename, since there is no version segment in the path to bump.
- Every figure is our own redraw. None is reproduced from a paper, textbook, or
  documentation site; captions credit the source of the idea where one exists
  (Burt & Adelson 1983 for FIG_14, Marr & Hildreth 1980 for FIG_08, Canny 1986 and
  Yuille & Poggio 1986 for FIG_11, Lindeberg 1998 for FIG_12 and FIG_13).
- FIG_06, FIG_08, FIG_10 and FIG_12 show curves plotted from closed-form expressions,
  and FIG_07 shows a profile computed by hand. Their captions say **model, not
  measurement**, because nothing was executed against an image for this post.
- The `.html` sources in `assets/` (and `_build.py`, `_figs.py`, `_cover.py`,
  `_linkedin.py`) are what make the figures editable. PNG is exported at 2× for the
  post, SVG kept for zooming.
- When a figure is revised, keep its exact file name and re-upload it under the same key; then
  purge the URL in Cloudflare, because `minio.canery.in/media/*` is served `immutable` for a
  year. Never add `-v2` (owner's instruction, 2026-10-08; it supersedes the note this line replaced).
- The cover at `assets/cover-laplacian-by-hand.png` is the deterministic template cover. An external
  illustration route is written out in `assets/cover-prompt.md`.

## Revision 2026-11-20 — post revised, first-edition figures kept

The text was revised on 2026-11-20; `outline.md` and `research/ledger.md` list what changed.
The figures were redrawn the same day on a 680-px canvas and then put back at the owner's
request: the owner prefers the first edition's diagram-design figures, FIG_14's REDUCE / EXPAND
flow diagram above all. All sixteen files are the first edition's again, byte-identical to what
MinIO serves, except FIG_11. Its label reads "dark on the left, bright on the right", but the
first edition shaded the bright side; the shading now sits on the dark side, and nothing else in
the figure moved. The captions and alt text of FIG_13 and FIG_14 describe these figures again, and
FIG_07's alt text no longer gives a value where the figure prints a dash. `_build.py` rasterises
from the local font cache and writes the published names; with the first edition's `_figs.py` it
reproduces the old PNGs pixel for pixel. `assets/_data.py` asserts the numbers the text prints.

**Owner steps:** upload `assets/fig-11-canny-decomposition-laplacian-by-hand.png` to MinIO
`media/` under its existing key, purge that one URL in Cloudflare, then re-publish `blog.md`.
The other fifteen figures, the cover and the LinkedIn cards need no upload.
