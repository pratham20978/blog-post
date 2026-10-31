# Upload manifest — image-processing-by-hand

Every placeholder in `blog.md`, in order of appearance. Upload each file to object
storage, put the resulting public URLs into `urls.txt` **in this row order**, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/image-processing/image-processing-by-hand/ posts/image-processing/image-processing-by-hand/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/image-processing/image-processing-by-hand/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery
contract rejects a non-URL there, so it must be resolved before upload.

| Placeholder | File                                       | Suggested path                                  | Alt text                                                                                                                                                                                                                                                                                                          |
| ----------- | ------------------------------------------ | ----------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| COVER       | `assets/cover.png`                       | `blog/image-processing-by-hand/cover-v1.png`  | Four-stage image processing pipeline: sample, filter, transform, decide, over a 2-D signal                                                                                                                                                                                                                        |
| FIG_01      | `assets/fig-01-four-stages.png`          | `blog/image-processing-by-hand/fig-01-v1.png` | Four-stage pipeline diagram: a continuous scene enters a sample stage marked irreversible, then a filter stage, a transform stage marked invertible, and a decide stage marked irreversible, with the array representation shown between each stage                                                               |
| FIG_02      | `assets/fig-02-grid-and-surface.png`     | `blog/image-processing-by-hand/fig-02-v1.png` | The same 5 by 5 patch shown twice: on the left a labelled grid of integers with the value 255 highlighted, on the right row 2 drawn as a step profile where 40 is a plateau, 255 a narrow spike, and 200 a wide step                                                                              |
| FIG_03      | `assets/fig-03-three-answers.png`        | `blog/image-processing-by-hand/fig-03-v1.png` | The 3 by 3 window over the impulse pixel, with three outputs branching from it: box mean 64, Gaussian 99, and median 40, each annotated with the arithmetic that produced it                                                                                                                                      |
| FIG_04      | `assets/fig-04-weight-stencils.png`      | `blog/image-processing-by-hand/fig-04-v1.png` | Three 3 by 3 weight stencils side by side with their numeric values: a box filter of nine equal ninths, a Gaussian with corner 0.0571, edge 0.1248, centre 0.2725, and a Sobel x-derivative with minus one, zero, one across the top row and minus two, zero, two across the middle                               |
| FIG_05      | `assets/fig-05-spectral-replication.png` | `blog/image-processing-by-hand/fig-05-v1.png` | Frequency-domain diagram showing a signal spectrum replicated at multiples of the sampling frequency, with a well-separated case above and an overlapping case below where the tails of adjacent copies sum into the passband                                                                                     |
| FIG_05B     | `assets/fig-05-moire-bricks.jpg`         | `blog/image-processing-by-hand/fig-05b-v1.jpg` | The same brick wall shown twice at one height: on the left a 250-pixel-wide copy with even brick texture, on the right a 205-pixel-wide copy, badly downsampled, crossed by broad diagonal bands that are not on the wall |
| FIG_06      | `assets/fig-06-separability.png`         | `blog/image-processing-by-hand/fig-06-v1.png` | Two routes from the 3 by 3 window over the impulse to one output: the upper path applies the 3 by 3 Gaussian stencil with nine multiplies, the lower path applies a 1 by 3 row pass that gives 40, 152.2 and 40, then a 3 by 1 column pass, three multiplies each, and both arrive at 98.6 |
| FIG_07      | `assets/fig-07-border-modes.png`         | `blog/image-processing-by-hand/fig-07-v1.png` | One row of pixels at the left boundary shown five times, each with a different border extrapolation filling the missing positions: constant zero, replicated edge value, reflected, reflected without duplicating the edge, and wrapped from the opposite side                                                    |
| FIG_08      | `assets/fig-08-dft-four-point.png`       | `blog/image-processing-by-hand/fig-08-v1.png` | The four-point computation in four panels: the input step, its DFT magnitudes 480, 226.3, 0 and 226.3, the filter's gain per frequency 1, 0.5, 0 and 0.5, and the output 80, 80, 160 and 160, with the route in space and the route through frequency written beneath |
| FIG_09      | `assets/fig-09-transfer-functions.png`   | `blog/image-processing-by-hand/fig-09-v1.png` | Transfer function curves for a box filter, a Gaussian, and a Laplacian plotted against normalised frequency: the box oscillates and goes negative, the Gaussian decays smoothly and monotonically, the Laplacian rises from zero                                                                                  |
| FIG_10      | `assets/fig-10-nonlinear-families.png`   | `blog/image-processing-by-hand/fig-10-v1.png` | Three nested groups of non-linear operators: threshold operators ordered on intensity against a global value, rank operators ordered on intensity within a neighbourhood, and morphological operators ordered on intensity within a structuring element with set semantics                                        |
| FIG_11      | `assets/fig-11-l1-vs-l2.png`             | `blog/image-processing-by-hand/fig-11-v1.png` | The gradient vector with components Gx equals 480 and Gy equals 480 drawn on axes, with the Euclidean hypotenuse of 678.8 marked against the L1 path of 960 traced along the two legs                                                                                                                             |
| FIG_12      | `assets/fig-12-canny-chain.png`          | `blog/image-processing-by-hand/fig-12-v1.png` | Flowchart of the Canny chain: Gaussian smooth, then Sobel gradient, then non-maximum suppression along the gradient direction, then double-threshold hysteresis, with the first two boxes labelled as stage 2 operators and the last two as stage 4                                                               |
| FIG_13      | `assets/fig-13-nms-hysteresis.png`       | `blog/image-processing-by-hand/fig-13-v1.png` | A one-dimensional brightness profile across an edge with its gradient magnitude below, showing a broad ridge reduced to a single surviving column by non-maximum suppression, with the high and low hysteresis thresholds marked |
| FIG_14      | `assets/fig-14-eigenvalue-plane.png`     | `blog/image-processing-by-hand/fig-14-v1.png` | The lambda-1 versus lambda-2 plane divided into flat, edge, and corner regions, with the Harris response contours overlaid and an arrow showing how changing k moves the boundary between edge and corner                                                                                                         |
| FIG_15      | `assets/fig-15-scale-axis.png`           | `blog/image-processing-by-hand/fig-15-v1.png` | A stack of increasingly blurred versions of one signal along a scale axis, with differences between adjacent levels shown as a second stack, and a feature appearing as an extremum at one specific scale                                                                                                         |
| FIG_16      | `assets/fig-16-tooling-map.png`          | `blog/image-processing-by-hand/fig-16-v1.png` | A four-column map with each pipeline stage above the specific NumPy and OpenCV calls that implement it, with the math expression each call corresponds to written beneath it                                                                                                                                      |
| FIG_17      | `assets/fig-17-series-map.png`           | `blog/image-processing-by-hand/fig-17-v1.png` | Tree diagram with the pillar post at the root and its child posts branching by stage: resampling and interpolation, kernel design, the 2-D DFT, wavelets, thresholding and segmentation, morphology, edge-preserving smoothing, Canny in detail, the structure tensor, scale space and SIFT, and colour and gamma |

## Notes

- **Resolved 2026-09-11.** All 18 images are live in MinIO under their own asset
  filenames, not the suggested paths above: `https://minio.canery.in/media/<asset
  filename>` — e.g. `assets/fig-01-four-stages.png` →
  `https://minio.canery.in/media/fig-01-four-stages.png`. `urls.txt` holds the
  resolved list and `blog.md` is already filled; the pre-fill copy is `blog.md.bak`.
- **Revision 2026-10-31 — to upload.** New: `assets/fig-05-moire-bricks.jpg` →
  `https://minio.canery.in/media/fig-05-moire-bricks.jpg` (already in `blog.md` and
  `urls.txt`). Re-rendered under their existing keys: `fig-06-separability.png`
  (rebuilt: the arrows ran along box borders and ended short of the output),
  `fig-08-dft-four-point.png` (labels on bars, `H[K]`, a wrong "nine multiplies"),
  `fig-13-nms-hysteresis.png` (label plates cut the curve), `fig-15-scale-axis.png`
  (the title's σ was uppercased to Σ), `fig-07-border-modes.png` (its eyebrow claimed
  five answers where row 0 gives three; now drawn on row 2, where the five rules differ).
  `media/*` is served immutable, so purge those five URLs in Cloudflare after
  uploading, then re-publish `blog.md`.
- Every figure is our own redraw except the lower half of Figure 5 (FIG_05B): two
  Wikimedia Commons copies of one photograph by Cburnett, licensed CC BY-SA 3.0 and
  GFDL 1.2, embedded byte-for-byte from `assets/_src-bricks-*.jpg` and only scaled
  for display. That composite is CC BY-SA 3.0, and its caption carries the credit,
  the licence link and the change. None of the rest is reproduced from a paper,
  textbook, or documentation site; captions credit the source of the idea where one exists.
- FIG_09 and FIG_13 show curves plotted from closed-form expressions. Their captions
  say **model, not measurement**, because nothing was executed for this post.
- Keep the `.html` (and `.mmd` where used) sources in `assets/` so figures stay
  editable. Export PNG at 2× for the post and SVG for zooming.
- When a figure is revised, keep its filename and overwrite it in place (owner's rule
  since 2026-10-08), then purge its URL in Cloudflare so no cache serves the old one.
