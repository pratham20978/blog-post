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
| FIG_01 | `assets/fig-01-two-signatures-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-01-two-signatures-laplacian-by-hand.png` | Row profile 40 40 40 200 200 drawn as a step, with its first difference below showing one positive peak of 160 at the step and its second difference below that showing a positive lobe of 160 then a negative lobe of minus 160 with the zero between them on the step |
| FIG_02 | `assets/fig-02-clean-windows-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-02-clean-windows-laplacian-by-hand.png` | Two 3 by 3 windows from the clean patch side by side: the window centred at row 2 column 2 giving 320 minus 160 equals plus 160, and the window at row 2 column 3 giving 640 minus 800 equals minus 160, with the zero-crossing marked between them |
| FIG_03 | `assets/fig-03-impulse-windows-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-03-impulse-windows-laplacian-by-hand.png` | Three 3 by 3 windows from the patch with the impulse: at row 2 column 1 the centre 255 gives minus 860; at row 2 column 2 the left neighbour 255 gives 375; at row 1 column 2 the impulse is diagonal and the result stays 160 |
| FIG_04 | `assets/fig-04-mean-minus-centre-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-04-mean-minus-centre-laplacian-by-hand.png` | The window at row 2 column 2 shown twice: as the stencil arithmetic 320 minus 160 equals 160, and as the neighbour mean 80 minus the centre 40 equals 40, times four; below, the impulse window as mean 40 minus centre 255 equals minus 215, times four equals minus 860 |
| FIG_05 | `assets/fig-05-five-stencils-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-05-five-stencils-laplacian-by-hand.png` | Five 3 by 3 stencils with their integer weights: five-point labelled times 1, diagonal times 2, eight-neighbour times 3, OpenCV ksize 3 with 2 at the corners and minus 8 at the centre labelled times 4, and the nine-point stencil divided by 6 labelled times 1 and isotropic |
| FIG_06 | `assets/fig-06-transfer-functions-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-06-transfer-functions-laplacian-by-hand.png` | Curves of the transfer-function magnitude against spatial frequency for the five-point and nine-point stencils along the axis and along the diagonal, with the continuous omega squared curve; at pi the five-point reads 4 and 6.42, the nine-point 4 and 4.70, the continuous 9.87 |
| FIG_07 | `assets/fig-07-sharpening-halo-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-07-sharpening-halo-laplacian-by-hand.png` | The row profile 40 40 40 200 200 drawn three times: the original step, the Laplacian 0, 160, minus 160, 0, and the sharpened row 40, minus 120, 360, 200 with the clipped values 0 and 255 marked, an undershoot on the dark side and an overshoot on the bright side |
| FIG_08 | `assets/fig-08-mexican-hat-dog-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-08-mexican-hat-dog-laplacian-by-hand.png` | The Mexican hat profile of the Laplacian of Gaussian against radius with the zero at root two sigma and the width w equals two root two sigma marked, and a difference of two Gaussians with ratio 1.6 drawn over it, visibly wider and about half as deep at the centre |
| FIG_09 | `assets/fig-09-log-kernel-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-09-log-kernel-laplacian-by-hand.png` | A 5 by 5 grid of decimal weights: centre minus 0.591, the four edge-neighbours minus 0.1123, the four diagonals plus 0.021, the next ring 0.1248 on the axes and 0.0571 off them, zeros in the corners, negative cells shaded and the sum annotated as zero |
| FIG_10 | `assets/fig-10-phantom-edges-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-10-phantom-edges-laplacian-by-hand.png` | A one-dimensional profile with two nearby steps, its first derivative showing two peaks with a dip between them, and its second derivative with three zero-crossings marked: two at the peaks labelled authentic, one at the dip labelled phantom |
| FIG_11 | `assets/fig-11-canny-decomposition-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-11-canny-decomposition-laplacian-by-hand.png` | A straight edge with the frame rotated so one axis points across it and the other along it; the Laplacian written as the second derivative across plus the second derivative along, the across term labelled signal and the along term labelled zero on the edge and noise elsewhere |
| FIG_12 | `assets/fig-12-scale-selection-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-12-scale-selection-laplacian-by-hand.png` | Two curves of the scale-normalised Laplacian response at the centre of a structure against sigma from 0.5 to 4: a bar of width 3 peaking at sigma 1.5 with value 77.4 and a disc of radius 3 peaking at sigma 2.12 with value 117.7, with the values at sigma 1 and 3 marked |
| FIG_13 | `assets/fig-13-scale-space-cube-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-13-scale-space-cube-laplacian-by-hand.png` | Five image planes stacked along a vertical scale axis labelled with sigma values increasing by a factor k, one pixel on the middle plane highlighted with its 8 spatial neighbours and the 9 pixels above and 9 below marked as the 26 comparisons |
| FIG_14 | `assets/fig-14-laplacian-pyramid-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-14-laplacian-pyramid-laplacian-by-hand.png` | Flowchart of the Laplacian pyramid: g0 passes through REDUCE to g1 and g2, each Gaussian level is expanded and subtracted from the level below to give a Laplacian level, the top level is stored whole, and a dashed return path shows reconstruction by expanding and adding each level back down |
| FIG_15 | `assets/fig-15-poisson-editing-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-15-poisson-editing-laplacian-by-hand.png` | A target image with a region omega outlined; the boundary of omega carries the target's pixel values, the interior carries the source's Laplacian, and the interior pixel values are labelled as the unknowns solved for by one five-point equation per pixel |
| FIG_16 | `assets/fig-16-tooling-map-laplacian-by-hand.png` | `https://minio.canery.in/media/fig-16-tooling-map-laplacian-by-hand.png` | Six rows, one per job, each with the math on the left and the exact library call on the right, with the scale factor on the arrow: times 1, times 4 with scale 0.25, no sigma squared, sigma squared and 1 over k minus 1, exact, and a sparse solve |

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
- When a figure is revised, bump its path to `-v2.png` so no cache serves the old one.
- The cover at `assets/cover-laplacian-by-hand.png` is the deterministic template cover. An external
  illustration route is written out in `assets/cover-prompt.md`.
