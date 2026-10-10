# Series plan — Image Processing by Hand

**Slug:** image-processing · **Shape:** hybrid (hub and spokes) · **Parts:** 14 (2 published, 12 planned)

## Why this is a series and not one post

The seam was cut in public and is already load-bearing. The hub post budgets the four stages —
sample, filter, transform, decide — at 9,990 words and 17 figures, which is the top of L4, and it
reaches that number only because it stops at the frame: eleven times in its body it names an area,
states the one fact the frame needs from it, and hands the rest to a child post by title. Part 2
took one of those handoffs and spent another 9,201 words and 16 figures on a single operator. The
remaining eleven promises are the same size. Budgeting the whole territory as one post gives
roughly 97,000 words and 160 figures.

This is a **hybrid**, but not the usual kind. There is no low rung: the hub is L4 advanced and so
are most spokes. What makes the hub a hub is breadth, not shallowness — it owns the shared frame,
the shared 5×5 patch, the shared 3×3 Gaussian and the shared border rules, and every spoke assumes
those rather than re-teaching them. Parts 3–14 are disjoint siblings at roughly the same depth,
each cut at the boundary of one area of the frame. Part 14 is the one spoke whose prerequisite is
Part 2 rather than Part 1.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | name which of four stages produced a given number, and therefore which stage holds the bug | 1 |
| 2 | evaluate a linear filter as one weighted sum over a neighbourhood, on real integers | 1 |
| 3 | say what a set of weights does to the signal, from its transfer function rather than its name | 1 |
| 4 | say where the arithmetic stops being linear, and what that costs | 1 |
| 5 | derive every use of the Laplacian from one identity — it is what blur removes per unit of scale | 2 |
| 6 | predict what changes when a library's Laplacian aperture changes, before running it | 2 |
| 7 | choose a resampling kernel from what it does to the spectrum, not from its name | 3 |
| 8 | say why a downscale needs a filter and an upscale needs a different one | 3 |
| 9 | choose or design a derivative kernel, and say what "optimal" means for one | 4 |
| 10 | read a 2-D spectrum, and say what survives in phase when magnitude is destroyed | 5 |
| 11 | design a frequency-domain filter and say when the spatial equivalent is cheaper | 5 |
| 12 | say where Fourier stops being the right basis, and what replaces it | 6 |
| 13 | smooth an image without moving its edges, and price the three ways of doing it | 7 |
| 14 | set Canny's two thresholds from the gradient statistics rather than by search | 8 |
| 15 | read the structure tensor's eigenvalues and say what the neighbourhood contains | 9 |
| 16 | say why optical flow and corner detection are the same matrix | 9 |
| 17 | treat σ as a search dimension, and say why the Gaussian is the only legal kernel for it | 10 |
| 18 | pick a thresholding or segmentation method from the histogram's shape | 11 |
| 19 | use erosion and dilation as an algebra with laws, not as a pair of tricks | 12 |
| 20 | say when a pixel value is a physical quantity and when it is an encoding | 13 |
| 21 | edit an image by its gradients and say why the pixels can be discarded | 14 |

## Parts

### Part 1 — Image Processing by Hand: Sample, Filter, Transform, Decide

- **Slug:** image-processing-by-hand
- **Tier:** L4 · **Difficulty:** advanced · **Words:** 9,990 · **Figures:** 17
- **Answers:** which of four stages produced this number, and therefore where is the bug?
- **Assumes:** basic calculus, complex exponentials, matrix notation, reading Python signatures.
- **Hands off:** eleven areas, each named in the body as a child post by title, plus the tree in
  Figure 17.
- **Worked example:** one 5×5 8-bit patch — flat 40 on the left, flat 200 on the right, a step
  between c2 and c3, one impulse of 255 at (r2, c1) — carried through all four stages.
- **Search intent:** "image processing basics", "how does convolution work on images", "what is a
  kernel in image processing"
- **Status:** **published** at https://canery.in/blogs/image-processing-by-hand

### Part 2 — The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening

- **Slug:** laplacian-by-hand
- **Tier:** L4 · **Difficulty:** advanced · **Words:** 9,201 · **Figures:** 16
- **Answers:** why do sharpening, zero-crossing edges, blob scale selection, the pyramid and
  Poisson editing all reduce to one operator?
- **Assumes:** Part 1's four stages, its patch, its 3×3 Gaussian and its border rules. Second
  derivatives and one Taylor expansion.
- **Hands off:** gradient-domain editing to Part 14. Names Parts 4, 7, 6, 8, 9 and 10 as the
  hub's children where they bite.
- **Worked example:** the same 5×5 patch, second-differenced by hand; the ×4 between OpenCV's
  `ksize=1` and `ksize=3` derived rather than quoted.
- **Search intent:** "laplacian filter explained", "cv2.Laplacian ksize", "laplacian of gaussian",
  "zero crossing edge detection"
- **Status:** **published** at https://canery.in/blogs/laplacian-by-hand

### Part 3 — Resampling and Aliasing: Interpolation Kernels in Practice

- **Slug:** resampling-and-aliasing
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** which kernel should reconstruct the signal between the samples, and what does the
  choice cost?
- **Assumes:** Part 1's sampling stage — the `#stage-1--sample-the-grid-is-already-lossy` anchor —
  and its spectral-replication figure. Does not re-teach Nyquist.
- **Hands off:** kernel *design* proper to Part 4; the frequency-domain view of a resize to Part 5.
- **Worked example:** one row of the shared patch resized to 0.6× and 1.7× by nearest, bilinear,
  bicubic and Lanczos-3, every tap and every output value printed, with the prefilter that the
  downscale needs and the upscale does not.
- **Key sources:** Keys 1981 (cubic convolution, where "third-order accurate" is defined);
  Mitchell–Netravali 1988; OpenCV `resize` / `INTER_AREA` documentation.
- **Search intent:** "bilinear vs bicubic", "why does my resized image look bad", "image downscale
  aliasing", "INTER_AREA vs INTER_LINEAR", "Lanczos resampling"
- **Status:** **built** 2026-09-25 — 6,626 words, 10 figures, gate PASS; not yet published
  (canonical https://canery.in/blogs/resampling-and-aliasing once live)

### Part 4 — Kernel Design: Separability, Borders, and Optimised Derivative Filters

- **Slug:** kernel-design-separability-borders-derivatives
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 11
- **Answers:** where do a kernel's numbers come from, and what does "optimal" mean for a derivative
  filter?
- **Assumes:** Part 1's filter stage — the `#stage-2--filter-every-linear-filter-is-one-weighted-sum`
  anchor — plus its separability and border figures, which it extends rather than repeats.
- **Hands off:** edge-*preserving* kernels to Part 7; scale selection to Part 10.
- **Worked example:** the Scharr coefficients derived from the rotation-invariance criterion they
  optimise, then compared against Sobel and against a sampled Gaussian derivative on the shared
  patch; the cost of truncating a σ = 2 Gaussian at 3, 5 and 7 taps, in lost mass and in changed
  variance.
- **Key sources:** Scharr's optimisation criterion; Farid & Simoncelli 2004 (matched
  derivative/interpolator pairs); Lindeberg on discrete vs sampled Gaussians.
- **Search intent:** "Scharr vs Sobel", "separable convolution", "how to choose Gaussian kernel
  size", "border mode convolution", "derivative filter design"
- **Status:** **built** 2026-09-25 — 7,395 words, 11 figures, gate PASS; not yet published. Title
  shortened to *Kernel Design: Separability, Borders, Optimised Derivatives* (59 chars) for the
  60-char limit (canonical https://canery.in/blogs/kernel-design-separability-borders-derivatives
  once live)

### Part 5 — The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering

- **Slug:** the-2d-dft-spectra-phase-filtering
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 13
- **Answers:** what does a 2-D spectrum actually show, and when is filtering there the right move?
- **Assumes:** Part 1's transform stage — the `#stage-3--transform-what-frequency-shows-that-pixels-hide`
  anchor — and its four-point DFT worked by hand.
- **Hands off:** non-stationary and local structure to Part 6; periodic-noise removal is owned
  here, not in Part 7.
- **Worked example:** the phase-swap demonstration done on two small images, then one periodic
  artefact removed with a notch filter designed from the spectrum, with the crossover point where
  a spatial convolution becomes cheaper than the FFT round trip computed for real kernel sizes.
- **Key sources:** Oppenheim & Lim 1981 (the importance of phase); Cooley & Tukey 1965; Gonzalez &
  Woods on frequency-domain filter design.
- **Search intent:** "2D FFT of an image", "what does phase contain in an image", "frequency
  domain filtering", "remove periodic noise from image", "fftshift explained"

### Part 6 — Wavelets and Multiresolution

- **Slug:** wavelets-and-multiresolution
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 11
- **Answers:** what do you get when you give up on one basis for the whole image?
- **Assumes:** Part 5's spectrum — the one prerequisite — and Part 2's pyramid section for the
  redundant version of the same idea.
- **Hands off:** nothing; it is a leaf.
- **Worked example:** one Haar level computed by hand on the shared patch's top row, then the
  same row through a 5/3 lifting step, with the coefficient budget of both compared against the
  Laplacian pyramid's 4/3 overcompleteness.
- **Key sources:** Mallat 1989 (multiresolution); Daubechies; the JPEG 2000 specification for the
  5/3 and 9/7 filters.
- **Search intent:** "wavelet transform image", "Haar wavelet explained", "JPEG2000 vs JPEG",
  "wavelet denoising", "what is multiresolution analysis"

### Part 7 — Edge-Preserving Smoothing: Bilateral, Non-Local Means, Anisotropic Diffusion

- **Slug:** edge-preserving-smoothing
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 11
- **Answers:** how do you average a neighbourhood without averaging across the edge in it?
- **Assumes:** Part 1's linear-filter sum, and its point that a linear filter cannot do this. Part
  2's heat-equation identity is the cleanest way in to diffusion, and is linked rather than
  re-derived.
- **Hands off:** learned denoisers — out of scope, not deferred.
- **Worked example:** the shared patch's impulse row through all three, with the bilateral's range
  weights computed for the impulse and for the step so the reader sees why one is preserved and
  the other is not; Perona–Malik run for three iterations by hand.
- **Key sources:** Perona & Malik 1990; Tomasi & Manduchi 1998 (bilateral); Buades 2005 (NL-means);
  Durand & Dorsey 2002 for the fast approximation.
- **Search intent:** "bilateral filter explained", "non-local means denoising", "anisotropic
  diffusion", "blur without losing edges", "cv2.bilateralFilter parameters"

### Part 8 — Canny, Line by Line

- **Slug:** canny-line-by-line
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** what do Canny's two thresholds actually select, and how do you set them without
  searching?
- **Assumes:** Part 1's Canny chain figure and its L1-vs-L2 gradient point. The difficulty drops
  here on purpose: this is the spoke a practitioner reads first, and it needs no calculus beyond
  a first derivative.
- **Hands off:** the zero-crossing alternative to Part 2, which owns the coarse-to-fine argument.
- **Worked example:** non-maximum suppression run on the shared patch's gradient with both the
  interpolated and the quantised-direction variants, showing where they disagree; hysteresis run
  as a connected-component walk with the two thresholds derived from the gradient histogram.
- **Key sources:** Canny 1986; OpenCV's `Canny` implementation notes on `L2gradient` and the
  quantised direction.
- **Search intent:** "Canny edge detection explained", "how to choose Canny thresholds",
  "non-maximum suppression", "hysteresis thresholding", "Canny aperture size"

### Part 9 — The Structure Tensor: Harris, Shi–Tomasi, and Optical Flow

- **Slug:** the-structure-tensor
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** why are corner detection, texture orientation and optical flow the same 2×2 matrix?
- **Assumes:** Part 1's eigenvalue-plane figure and its Harris paragraph, which it starts from
  rather than repeats.
- **Hands off:** scale selection for the tensor's window to Part 10 (Harris-Laplace is named in
  Part 2 and finished here only in its position half).
- **Worked example:** the tensor assembled by hand at three positions of the shared patch — flat,
  step, and the impulse — with its eigenvalues, the Harris response at two values of k, the
  Shi–Tomasi score, and then the same matrix solved as the Lucas–Kanade system, showing the
  aperture problem as a rank deficiency in the matrix already computed.
- **Key sources:** Harris & Stephens 1988; Shi & Tomasi 1994; Lucas & Kanade 1981; Förstner 1987.
- **Search intent:** "Harris corner detector explained", "structure tensor", "Lucas-Kanade optical
  flow", "Shi-Tomasi vs Harris", "aperture problem"

### Part 10 — Scale Space and SIFT: Why σ Is a Search Dimension

- **Slug:** scale-space-and-sift
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 13
- **Answers:** why must scale be searched rather than set, and why is the Gaussian the only kernel
  allowed to do the searching?
- **Assumes:** Part 2's normalised Laplacian and its scale-selection figure — the one prerequisite,
  linked by anchor. Part 1's scale-axis figure for the framing.
- **Hands off:** learned descriptors — out of scope, not deferred.
- **Worked example:** one octave of a DoG pyramid built on an enlarged version of the shared patch,
  with the 26-neighbour extremum test run at one position, the sub-pixel quadratic fit solved, and
  the edge-response test applied with r = 10.
- **Key sources:** Witkin 1983; Koenderink 1984; Lindeberg 1998 (feature detection with automatic
  scale selection); Lowe 2004 (SIFT); Mikolajczyk & Schmid 2004.
- **Search intent:** "SIFT explained", "scale space", "why Gaussian scale space", "difference of
  Gaussians", "SIFT octaves and intervals"

### Part 11 — Thresholding and Segmentation

- **Slug:** thresholding-and-segmentation
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** what does the histogram have to look like before a threshold can work at all?
- **Assumes:** Part 1's decide stage — the `#stage-4--decide-where-linearity-stops` anchor. Like
  Part 8, intermediate on purpose.
- **Hands off:** the morphological operators watershed's markers are built from, to Part 12.
- **Worked example:** Otsu's between-class variance computed over every threshold of a small
  histogram, with the answer shown to be the same as minimising within-class variance; then the
  same image segmented by marker-based watershed with the markers drawn by hand, and one
  over-segmentation produced deliberately.
- **Key sources:** Otsu 1979; Vincent & Soille 1991 (watershed by immersion); Sauvola 2000 for the
  local-threshold family.
- **Search intent:** "Otsu threshold explained", "adaptive thresholding", "watershed segmentation",
  "why is my watershed over-segmenting", "binarise an image"

### Part 12 — Mathematical Morphology as Lattice Algebra

- **Slug:** mathematical-morphology
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 11
- **Answers:** what laws do erosion and dilation obey, and what do those laws let you build?
- **Assumes:** Part 1's non-linear-families figure, which places morphology inside the rank
  operators. Basic lattice and set notation is taught here, not assumed.
- **Hands off:** segmentation use of morphological markers back to Part 11 — the two link to each
  other and neither re-teaches the other.
- **Worked example:** the shared patch binarised, then eroded, dilated, opened and closed by a 3×3
  cross, with the adjunction verified numerically on those results and idempotence of opening
  demonstrated by applying it twice; then a granulometry curve computed over four structuring
  element sizes.
- **Key sources:** Serra 1982; Matheron 1975; Heijmans & Ronse 1990 (the algebraic basis);
  Soille's handbook for the grey-level extension.
- **Search intent:** "erosion and dilation", "opening vs closing", "morphological gradient",
  "top-hat transform", "structuring element"

### Part 13 — Colour and Gamma: Luma, Luminance, and the Spaces in Between

- **Slug:** colour-and-gamma
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 5,500 · **Figures:** 9
- **Answers:** when is a pixel value a physical quantity and when is it an encoding?
- **Assumes:** nothing but Part 1's framing. The most standalone spoke in the series, and the one
  a non-specialist reads.
- **Owns:** the limitation Part 1 states in one paragraph — that `BGR2GRAY` returns luma $Y'$ and
  not CIE luminance $Y$ — expanded into the full account.
- **Worked example:** one sRGB triple carried through the transfer function to linear light, to
  XYZ, to Lab, with the two grey values (0.299/0.587/0.114 luma against 0.2127/0.7152/0.0722
  luminance) computed side by side and the error shown on a saturated colour; then one blur
  performed in both encodings, with the difference measured.
- **Key sources:** IEC 61966-2-1 (sRGB); ITU-R BT.601 and BT.709; Poynton's colour FAQ; the CIE
  standard observer.
- **Search intent:** "luma vs luminance", "gamma correction explained", "sRGB to linear",
  "BGR2GRAY weights", "why does resizing in sRGB look wrong"

### Part 14 — Gradient-Domain Editing: Poisson Cloning, HDR Compression, Seamless Tiling

- **Slug:** gradient-domain-editing
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,000 · **Figures:** 10
- **Answers:** what happens when you keep an image's gradients and throw the pixels away?
- **Assumes:** **Part 2**, not Part 1 — the `#keeping-the-laplacian-instead-of-the-pixels` anchor.
  The one spoke whose prerequisite is another spoke, because Part 2 promised it by name.
- **Hands off:** nothing; it is a leaf.
- **Worked example:** the Poisson system assembled for a 3×3 interior region with Dirichlet
  boundary from the shared patch, written out as the 9×9 linear system, and solved by hand by
  Gauss–Seidel for three sweeps so the reader sees the convergence; then the same solve read as
  one multigrid V-cycle.
- **Key sources:** Pérez, Gangnet & Blake 2003 (Poisson image editing); Fattal 2002 (gradient-domain
  HDR compression); Agarwala 2007 for the large-scale solve.
- **Search intent:** "Poisson image editing", "seamless cloning OpenCV", "gradient domain image
  processing", "how does seamlessClone work"

## Publication order and cadence

`series_position` follows the numbering above and it is also the reading order. Parts 1 and 2 are
already published in that order, which fixes positions 1 and 2 permanently.

Publication order for the twelve planned spokes does not have to follow the numbering, because
they are siblings — any spoke can ship as soon as it is written. Two orderings are defensible:

- **By promise pressure.** Parts 3, 4, 5 and 9 are the handoffs a reader of Part 1 hits earliest
  and most often, so they repay the wait soonest.
- **By search volume.** Parts 8, 10 and 13 have the strongest standalone intent — "Canny
  thresholds", "SIFT explained" and "luma vs luminance" are typed far more often than "structure
  tensor".

Recommended: Part 8, then 3, then 10, then 5, alternating the two orderings so the series gains
both traffic and coherence. One L3 spoke per two weeks; these are 6,000-word posts with ten
figures each and a weekly cadence will not survive contact with the figure budget.

## Cross-links

Part 1 is the hub every spoke links back to, by anchor, for the four stages and the shared patch.
Part 2 is the second hub for anything that touches the Laplacian identity, and Part 14 treats it
as its sole prerequisite.

Parts 1 and 2 are already published and are **not reopened** to add forward links. The published
Part 1 already names all eleven spokes by title in its prose and draws them in Figure 17, so a
reader who finishes it knows what is coming; the series index supplies the links once each spoke
is live. The single exception worth considering is Figure 17 itself, which predates Part 2 and does
not show the Laplacian branch. Fixing that is an expansion of a published post — re-run the gate
and bump `updated` — and it is listed as an open thread rather than done silently.

Every spoke links back to at most one prior part. No spoke links forward to an unpublished post.

## What this series will not cover

Learned methods of every kind — CNN denoisers, learned descriptors, segmentation networks,
super-resolution models. The series is about the classical arithmetic and stops where the weights
stop being designed. Also out of scope: compression codecs as codecs (the wavelet part covers the
transform, not the entropy coder), camera ISP pipelines end to end, 3-D and volumetric imaging,
video as a temporal signal beyond Part 9's optical flow, and GPU implementation.
