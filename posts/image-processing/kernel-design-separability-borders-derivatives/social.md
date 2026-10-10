---
social_schema: 2
canonical_url: "https://canery.in/blogs/kernel-design-separability-borders-derivatives"
---

# Social publishing package — kernel-design-separability-borders-derivatives

## LinkedIn post

Sobel and Scharr are the same filter with one number changed.

Every 3×3 x-derivative that treats up and down alike is a central difference times a smoothing column p, 1 − 2p, p. The central difference is p = 0, Scharr is 3/16, Sobel is 1/4, Prewitt is 1/3. Choosing an operator is choosing p.

Worked by hand on one 5×5 patch:

→ Direction. On stripes with a 4-pixel wavelength, Scharr's gradient is off by at most 0.29°, Sobel's by 3.24°, a plain central difference by 7.22°. Scharr's 3/16 makes the cross-smoothing match the difference's own blur down to a 3.45-pixel wavelength.
→ Robustness. Beside a single bad pixel the same choice runs the other way: Sobel's gradient is 67% wrong, Scharr's 84%. A direction-tuned filter weights the centre row, where the bad pixel sits.
→ Scale. On the same step, cv2.Sobel returns 640 and cv2.Scharr 2,560. Swap one for the other and every threshold is off by four.

Two more numbers the libraries choose for you: GaussianBlur with a (3, 3) kernel at σ = 2 has the spread of σ = 0.8, and OpenCV's default border makes every x-derivative on the edge column exactly zero.

Part 4 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

"Optimal" always names a criterion: direction, robustness, matching or scale. Name the measurement, and the p follows.

Read the full article on Canery: https://canery.in/blogs/kernel-design-separability-borders-derivatives

## Instagram caption

Sobel and Scharr are one stencil with one number changed. Swipe through where a kernel's numbers come from: the single free weight in every 3×3 derivative, why Scharr's output is four times Sobel's, how far each filter turns a gradient, why the direction-tuned filter is the fragile one beside a bad pixel, what cutting a Gaussian to three taps does to it, the default OpenCV kernel that isn't what the docs say, and the border rule that zeroes the edge column.

Every number is worked by hand from the article's own 5×5 patch.

Link in bio.

#imageprocessing #computervision #opencv #sobel #edgedetection #signalprocessing #python

## Shared feed order

1. `assets/social/feed-01-sobel-and-scharr-are-one-stencil.png` — every 3×3 x-derivative is one stencil with one free number p
2. `assets/social/feed-02-scharr-returns-four-times-sobel.png` — the same step reported at six different scales by four libraries
3. `assets/social/feed-03-the-gradient-turns.png` — the worst direction error of each filter on a 4-pixel pattern
4. `assets/social/feed-04-robust-or-isotropic.png` — beside a bad pixel, the direction-tuned filter is the more fragile one
5. `assets/social/feed-05-three-taps-at-sigma-2.png` — truncating a σ = 2 Gaussian keeps its brightness and takes its spread
6. `assets/social/feed-06-sigma-zero-is-not-sigma-point-eight.png` — OpenCV's 3×3 blur with sigma 0 is a fixed binomial table, not the documented σ = 0.8
7. `assets/social/feed-07-the-border-is-part-of-the-kernel.png` — four border rules give four derivatives at the same edge pixel
8. `assets/social/feed-08-read-the-article.png` — which choice to make for direction, bad pixels, Gaussians and borders, and the CTA

## Instagram Story

- CTA: Why does Scharr return four times Sobel? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### Story order

1. `assets/social/story-01-sobel-and-scharr-are-one-stencil.png` — Overlay: Only one number differs.
2. `assets/social/story-02-scharr-returns-four-times-sobel.png` — Overlay: Same step. Four scales.
3. `assets/social/story-03-three-taps-at-sigma-2.png` — Overlay: Three taps take the spread.
4. `assets/social/story-04-read-the-article.png` — Overlay: Four rules for every kernel. Link below.

## Asset metadata

### feed-01-sobel-and-scharr-are-one-stencil

- File: `assets/social/feed-01-sobel-and-scharr-are-one-stencil.png`
- Title: Sobel and Scharr are one stencil
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: every 3×3 x-derivative is one stencil with one free number p
- Technical source: The problem, Figure 1; Where do Scharr's 3, 10, 3 come from?, Figure 6 (L10, L32, L43)
- Visual structure: lockup and counter; serif title; deck; a panel with the generic 3×3 stencil, its outer cells in the accent, a note naming p, and a four-row table of filter, p and direction error; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Sobel and Scharr are one stencil. · Every 3×3 x-derivative that treats up and down alike is the same product. Only the weight on the neighbouring rows differs. · −p 0 p · −(1−2p) 0 1−2p · −p 0 p · ½ × the column p, 1 − 2p, p · times the central difference −1, 0, 1 · one free number: p · the weight on each neighbouring row · filter · p · direction error, 4-px pattern · central difference 0 7.22° · Scharr 3/16 0.29° · Sobel 1/4 3.24° · Prewitt 1/3 7.64° · Choosing a derivative filter is choosing one number. Scharr's p = 3/16 keeps direction within 0.3°; Sobel's 1/4 does not. · Kernel design · canery.in
- Alt text: A 3×3 derivative stencil whose outer rows carry one weight p, with central difference, Scharr, Sobel and Prewitt listed by p.
- Long description: The generic 3×3 x-derivative is drawn as a grid: −p, 0, p on the top and bottom rows and −(1−2p), 0, 1−2p on the middle row, all times one half. The single free number p is the weight on each neighbouring row. A table lists four named filters with their p and their worst gradient-direction error on a pattern with a 4-pixel wavelength: central difference, p = 0, 7.22°; Scharr, p = 3/16, 0.29°; Sobel, p = 1/4, 3.24°; Prewitt, p = 1/3, 7.64°. The takeaway: choosing a derivative filter is choosing one number, and Scharr's value keeps direction within 0.3° where Sobel's does not.
- Keywords: Sobel operator, Scharr operator, Prewitt, image gradient, derivative filter, filter design
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### feed-02-scharr-returns-four-times-sobel

- File: `assets/social/feed-02-scharr-returns-four-times-sobel.png`
- Title: Scharr returns four times Sobel
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the same step is reported at six different scales, so thresholds break when the operator changes
- Technical source: Worked example › One derivative, every p; Implementation tables; Figure 11 (L33, L34, L41, L43, L44)
- Visual structure: lockup and counter; title; deck; a table of six calls with their output at (r2, c3) and their scale, Scharr in the accent; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Scharr returns four times Sobel. · The patch's clean step rises 160 grey levels, a slope of 80 per pixel. Each call reports it at its own scale. · call · output at (r2, c3) · scale · cv2.Sobel(img, CV_32F, 1, 0, ksize=3) 640 × 8 · cv2.Scharr(img, CV_32F, 1, 0) 2,560 × 32 · scipy.ndimage.sobel(img, axis=1) 640 × 8 · skimage.filters.sobel, one axis 160 × 2 · skimage.filters.sobel, magnitude 113.1 × 2 ÷ √2 · normalised to slope 1 80 × 1 · All six mean a slope of 80. Normalise once, and threshold in grey levels per pixel. · Kernel design · canery.in
- Alt text: Table of one image step measured by six calls: Sobel 640, Scharr 2,560, SciPy 640, scikit-image 160 and 113.1, normalised 80.
- Long description: The shared patch's clean step rises 160 grey levels, a slope of 80 per pixel. OpenCV's Sobel returns 640 there, eight times the slope; OpenCV's Scharr returns 2,560, thirty-two times; SciPy's ndimage.sobel returns 640; scikit-image's Sobel gives 160 along one axis and 113.1 as a magnitude, because it scales each axis by two and divides the magnitude by the square root of two; a kernel normalised to unit slope gives 80. All six mean the same slope, so a threshold tuned on one operator is wrong on another until it is normalised.
- Keywords: cv2.Sobel, cv2.Scharr, scipy.ndimage.sobel, scikit-image, gradient magnitude, normalisation
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### feed-03-the-gradient-turns

- File: `assets/social/feed-03-the-gradient-turns.png`
- Title: The gradient turns
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: each filter turns a slanted gradient by a different amount; Scharr and the 5-tap matched pair turn it least
- Technical source: Intuition, Figure 4; Where do Scharr's 3, 10, 3 come from?, Figures 5 and 6; What does "optimal" mean?
- Visual structure: lockup and counter; one-line title; deck; a label, then six horizontal bars of worst direction error, Scharr in the accent; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · The gradient turns. · A central difference blurs along its own axis, so on stripes at an angle it shrinks one component more and the vector turns. · worst direction error over orientation · 4-px wavelength · closed form · Prewitt 7.64° · central difference 7.22° · Sobel 3.24° · [1 4 1]/6 0.64° · Scharr 0.29° · Farid–Simoncelli 5-tap 0.17° · Scharr's cross-weight matches that blur down to 3.45 px. Sobel's matches it only at the 2-pixel Nyquist pattern. · Kernel design · canery.in
- Alt text: Bars of each filter's worst gradient-direction error on a 4-pixel pattern, from 7.64° for Prewitt to 0.29° for Scharr and 0.17°.
- Long description: For a plane wave with a 4-pixel wavelength, evaluated from the filters' closed-form transfer functions over every orientation, the worst gradient-direction errors are: Prewitt 7.64°, central difference 7.22°, Sobel 3.24°, the [1 4 1]/6 column 0.64°, Scharr 0.29°, and Farid and Simoncelli's 5-tap matched pair 0.17°. The central difference blurs along its own axis, so on slanted stripes it shrinks one gradient component more than the other and the vector turns. Scharr's cross-weight matches that blur down to a 3.45-pixel wavelength; Sobel's matches it only at the 2-pixel Nyquist pattern.
- Keywords: rotation invariance, gradient direction, Scharr, Sobel, Farid-Simoncelli, isotropy
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### feed-04-robust-or-isotropic

- File: `assets/social/feed-04-robust-or-isotropic.png`
- Title: Robust or isotropic: pick one
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: beside a bad pixel a larger p is more robust, so the direction-tuned filter is the more fragile one
- Technical source: Worked example › One derivative, every p; Figure 2; What does "optimal" mean? › Robustness
- Visual structure: lockup and counter; title; deck; a panel with the 3×3 window at (r2, c2), the impulse outlined, its three row differences, the output formula, and a table of four filters with output and error; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Robust or isotropic: pick one. · Beside the patch's one bad pixel, the output is a straight line in p. The clean value is 80. · 40 40 200 · 255 40 200 · 40 40 200 · row 80.0 · row −27.5 · row 80.0 · 80 − 107.5 (1 − 2p) · output at (r2, c2), p on each neighbouring row · filter · output · error against 80 · Prewitt 44.17 45% · Sobel 26.25 67% · Scharr 12.81 84% · central difference −27.50 134% · A direction-tuned filter weights the centre row, and the centre row is where the bad pixel sits. · Kernel design · canery.in
- Alt text: A 3×3 window holding one bright pixel and the derivative beside it: Prewitt 45% wrong, Sobel 67%, Scharr 84%, central difference 134%.
- Long description: The 3×3 window at row 2, column 2 of the shared patch holds the bad pixel of 255 in its left column. Its three row differences are 80, −27.5 and 80, so the normalised derivative is 80 − 107.5 (1 − 2p) for cross-weight p, against a clean value of 80. Prewitt gives 44.17, a 45% error; Sobel 26.25, 67%; Scharr 12.81, 84%; the central difference −27.5, 134%. The filter tuned for direction puts more weight on the centre row, which is where the bad pixel sits, so it is the more fragile one here.
- Keywords: Sobel, Scharr, impulse noise, derivative filter, robustness, shared patch
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### feed-05-three-taps-at-sigma-2

- File: `assets/social/feed-05-three-taps-at-sigma-2.png`
- Title: (3, 3) at σ = 2 is a σ = 0.8 blur
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: truncating a Gaussian keeps its brightness and takes its spread
- Technical source: Worked example › Truncating a σ = 2 Gaussian; Figure 3; How many taps does a Gaussian need? (L30, L39)
- Visual structure: lockup and counter; title; deck; four horizontal bars of effective σ for 3, 5, 7 and 13 taps with a dashed σ = 2 target on the last, and a line of mass kept; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · (3, 3) at σ = 2 is a σ = 0.8 blur. · Truncating a Gaussian keeps its brightness, because the weights are renormalised. What it takes is the spread. · effective σ after renormalising · target 2.0 · 3 taps 0.80 · 5 taps 1.29 · 7 taps 1.64 · 13 taps 1.99 · σ = 2 · mass kept before renormalising · 3: 55.2% · 5: 79.4% · 7: 92.3% · 13: 99.9% · Use at least 2⌈3σ⌉ + 1 taps — 13 at σ = 2 — or pass ksize (0, 0) and let the library size the kernel. · Kernel design · canery.in
- Alt text: Bars of the effective σ of a σ = 2 Gaussian cut to 3, 5, 7 and 13 taps: 0.80, 1.29, 1.64 and 1.99 against a target of 2.
- Long description: A σ = 2 Gaussian sampled at the integers and cut to 3 taps keeps 55.2% of its mass; renormalising restores the brightness but leaves an effective σ of 0.80. At 5 taps the effective σ is 1.29 with 79.4% of the mass kept, at 7 taps 1.64 with 92.3%, and at 13 taps 1.99 with 99.9%. Truncation therefore costs spread rather than brightness. Use at least 2⌈3σ⌉ + 1 taps, 13 at σ = 2, or let the library choose the size.
- Keywords: Gaussian blur, kernel size, truncation, sigma, GaussianBlur, effective sigma
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### feed-06-sigma-zero-is-not-sigma-point-eight

- File: `assets/social/feed-06-sigma-zero-is-not-sigma-point-eight.png`
- Title: σ = 0 is not σ = 0.8
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: OpenCV's 3×3 Gaussian with sigma 0 is a fixed binomial table, not the documented σ = 0.8 kernel
- Technical source: How many taps does a Gaussian need? › What OpenCV builds when σ is zero; Figure 9 (L26, L28, L29)
- Visual structure: lockup and counter; title; deck; two rows of three weights, documented and actual, with their variances; a rule; the impulse result under each; a note on larger sizes; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · σ = 0 is not σ = 0.8. · For a 3×3 kernel with sigma 0, OpenCV documents σ = 0.8. The source returns a hard-coded binomial instead. · documented: sampled at σ = 0.8 · 0.239 0.522 0.239 · variance 0.478 · what runs with sigma 0: fixed table · 0.25 0.5 0.25 · variance 0.500 · on the patch's bad pixel, a 3×3 blur gives · 98.6 at σ = 0.8 · 93.75 with sigma 0 · the same kind of table covers ksize 5, 7 and 9 · Pass σ explicitly when the number matters. The table is already in OpenCV's 2.4 branch, and still undocumented. · Kernel design · canery.in
- Alt text: The documented 3×3 Gaussian weights 0.239, 0.522, 0.239 against the table OpenCV uses with sigma 0: 0.25, 0.5, 0.25.
- Long description: For a 3×3 kernel with sigma 0, OpenCV's documentation derives σ = 0.8, which would give the sampled weights 0.239, 0.522 and 0.239 with variance 0.478. The source instead returns a hard-coded binomial, 0.25, 0.5 and 0.25, with variance 0.5; a similar fixed table covers kernel sizes 5, 7 and 9. On the shared patch's bad pixel the σ = 0.8 kernel gives 98.6 and the default call gives 93.75. The table is already present in OpenCV's 2.4 branch and is not mentioned in the documentation, so pass σ explicitly when the number matters.
- Keywords: OpenCV, GaussianBlur, getGaussianKernel, binomial kernel, sigma, documentation
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### feed-07-the-border-is-part-of-the-kernel

- File: `assets/social/feed-07-the-border-is-part-of-the-kernel.png`
- Title: The border is part of the kernel
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: four border rules give four derivatives at the same edge pixel, and OpenCV's default gives zero
- Technical source: What does the border do to a derivative?; Figure 10 (L38, L40, L41)
- Visual structure: lockup and counter; title; deck; four rows, each with three invented pixels, the first three real pixels of row r2 and the Sobel output, OpenCV's default in the accent; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · The border is part of the kernel. · Row r2 extended past its left edge four ways, and the normalised Sobel on the edge pixel (r2, c0). · invented · c0 c1 c2 of row r2 · Sobel at (r2, c0) · 200 40 255 · 40 255 40 · 0.00 · reflect-101 · OpenCV default · 40 255 40 · 40 255 40 · 53.75 · reflect · SciPy default · 0 0 0 · 40 255 40 · 73.75 · constant 0 · 40 200 200 · 40 255 40 · −26.25 · wrap · OpenCV's default gives exactly 0 on the edge column for any image. SciPy's gives 430 here, raw — same stencil. · Kernel design · canery.in
- Alt text: Row r2 extended past its left edge four ways, with Sobel at the edge pixel: reflect-101 0, reflect 53.75, constant 73.75, wrap −26.25.
- Long description: The first three pixels of row r2 are 40, 255 and 40. Reflect-101, OpenCV's default, invents 200, 40, 255 beyond the edge and the normalised Sobel at (r2, c0) is exactly 0. Reflect, SciPy's default, invents 40, 255, 40 and gives 53.75. Constant zero invents 0, 0, 0 and gives 73.75. Wrap invents 40, 200, 200 from the far end and gives −26.25. Under OpenCV's default the x-derivative on the edge column is zero for any image; SciPy's raw Sobel gives 430 at the same pixel with the same stencil and scale.
- Keywords: border modes, BORDER_REFLECT_101, BORDER_REFLECT, scipy.ndimage, Sobel, padding
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Kernel design, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: which choice to make for direction, bad pixels, Gaussians and borders, and the article link
- Technical source: Key takeaways; Limitations and common mistakes; Implementation: the tooling map
- Visual structure: lockup and counter; title; deck; a four-item panel — direction, a bad pixel nearby, a Gaussian, the border — each with a choice and a one-line reason; takeaway; CTA footer with the article address
- Visible-text transcript: Canery.in · 08 / 08 · Kernel design, by hand. · Sobel, Scharr, Farid–Simoncelli, truncated and discrete Gaussians and five border rules, all on one 5×5 patch. · direction · Scharr, or Farid–Simoncelli's 5-tap pair · 0.29° and 0.17° at a 4-px wavelength · a bad pixel nearby · a larger p — Sobel over Scharr · 67% error against 84% · a Gaussian · 2⌈3σ⌉ + 1 taps, σ passed explicitly · no fixed table, no hidden truncation · the border · crop by the kernel radius before measuring · reflect-101 zeroes the edge column · The full walk-through, with the tooling map for OpenCV, SciPy, NumPy and scikit-image. · Read it at canery.in/blogs/kernel-design-separability-borders-derivatives
- Alt text: Summary card: Scharr for direction, a larger p near bad pixels, enough taps and an explicit σ, and crop before measuring at borders.
- Long description: The closing card lists four choices. For gradient direction, use Scharr or Farid and Simoncelli's 5-tap pair, which err by 0.29° and 0.17° on a 4-pixel pattern. Near a bad pixel, a larger cross-weight p is steadier: Sobel's error is 67% against Scharr's 84%. For a Gaussian, use at least 2⌈3σ⌉ + 1 taps and pass σ explicitly, avoiding OpenCV's fixed table and hidden truncation. At the border, crop by the kernel radius before measuring, because reflect-101 zeroes the derivative on the edge column. It links to the full article on Canery.
- Keywords: Sobel, Scharr, Gaussian blur, border modes, OpenCV, kernel design
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### story-01-sobel-and-scharr-are-one-stencil

- File: `assets/social/story-01-sobel-and-scharr-are-one-stencil.png`
- Title: Sobel and Scharr are one stencil
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: only p, the weight on the neighbouring rows, differs between Sobel and Scharr
- Technical source: The problem, Figure 1; Figure 6
- Visual structure: lockup and counter; title; deck; the generic stencil large and centred, outer cells in the accent; a two-row table of Scharr and Sobel with p and direction error; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Sobel and Scharr are one stencil. · Only p, the weight on the neighbouring rows, differs. · −p 0 p · −(1−2p) 0 1−2p · −p 0 p · direction error, 4-px pattern · Scharr p = 3/16 0.29° · Sobel p = 1/4 3.24° · Scharr's 3/16 keeps direction within 0.3° on a 4-pixel pattern. Sobel's 1/4: 3.2°. · Kernel design · canery.in
- Alt text: A 3×3 derivative stencil with its outer weight p highlighted; Scharr at p = 3/16 errs 0.29°, Sobel at p = 1/4 errs 3.24°.
- Long description: Story recomposition of the first feed card. The generic 3×3 x-derivative is drawn large, with −p, 0, p on its top and bottom rows and −(1−2p), 0, 1−2p on the middle row. Scharr's p = 3/16 keeps the gradient's direction within 0.29° on a pattern with a 4-pixel wavelength; Sobel's p = 1/4 errs by 3.24°.
- Keywords: Sobel, Scharr, derivative filter, image gradient, rotation invariance
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### story-02-scharr-returns-four-times-sobel

- File: `assets/social/story-02-scharr-returns-four-times-sobel.png`
- Title: Scharr returns four times Sobel
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the same step at four different scales
- Technical source: Worked example › One derivative, every p; Figure 11 (L34, L43)
- Visual structure: lockup and counter; title; deck; a four-row table of call and output on the clean step; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · Scharr returns four times Sobel. · Same step, same slope of 80. Four scales. · call · output on the clean step · cv2.Sobel 640 · cv2.Scharr 2,560 · skimage sobel, one axis 160 · normalised 80 · Normalise once, then threshold in grey levels per pixel. · Kernel design · canery.in
- Alt text: One image step measured four ways: cv2.Sobel 640, cv2.Scharr 2,560, scikit-image Sobel on one axis 160, normalised 80.
- Long description: The shared patch's clean step has a slope of 80 grey levels per pixel. OpenCV's Sobel reports 640, OpenCV's Scharr 2,560, scikit-image's Sobel along one axis 160, and a kernel normalised to unit slope 80. Normalise once and threshold in grey levels per pixel.
- Keywords: cv2.Sobel, cv2.Scharr, scikit-image, normalisation, thresholds
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### story-03-three-taps-at-sigma-2

- File: `assets/social/story-03-three-taps-at-sigma-2.png`
- Title: (3, 3) at σ = 2 is a σ = 0.8 blur
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: truncation keeps brightness and takes spread
- Technical source: Worked example › Truncating a σ = 2 Gaussian; Figure 3
- Visual structure: lockup and counter; title; deck; four bars of effective σ with the σ = 2 target on the last, and a line of mass kept; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · (3, 3) at σ = 2 is a σ = 0.8 blur. · Renormalising keeps the brightness. Truncation takes the spread. · effective σ after renormalising · target 2.0 · 3 taps 0.80 · 5 taps 1.29 · 7 taps 1.64 · 13 taps 1.99 · σ = 2 · mass kept before renormalising · 3: 55.2% · 5: 79.4% · 7: 92.3% · 13: 99.9% · 13 taps at σ = 2 reach 1.99. 3 taps reach 0.80. · Kernel design · canery.in
- Alt text: Bars of the effective σ of a σ = 2 Gaussian cut to 3, 5, 7 and 13 taps: 0.80, 1.29, 1.64 and 1.99.
- Long description: Story recomposition of the truncation card. A σ = 2 Gaussian cut to 3 taps and renormalised has an effective σ of 0.80; 5 taps give 1.29, 7 taps 1.64 and 13 taps 1.99. The mass kept before renormalising is 55.2%, 79.4%, 92.3% and 99.9%. Renormalising keeps the brightness; truncation takes the spread.
- Keywords: Gaussian blur, truncation, kernel size, effective sigma
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Four rules for every kernel
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the four rules the article works out, and the link
- Technical source: Key takeaways; Limitations and common mistakes
- Visual structure: lockup and counter; title; deck; a numbered four-rule panel; takeaway; CTA footer pointing at the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Four rules for every kernel. · Worked by hand on one 5×5 patch. · 1 direction: Scharr, not a bigger Sobel · 2 bad pixels: a larger p · 3 Gaussian: 2⌈3σ⌉ + 1 taps, σ explicit · 4 border: crop before you measure · The full walk-through is on Canery. · Link in the sticker above
- Alt text: Four numbered rules: Scharr for direction, a larger p near bad pixels, enough taps with explicit σ, crop before measuring at borders.
- Long description: The closing Story frame lists four rules from the article: for direction use Scharr rather than a bigger Sobel, whose extra taps do not change direction; near bad pixels prefer a larger cross-weight p; for a Gaussian use at least 2⌈3σ⌉ + 1 taps and pass σ explicitly; at the border crop by the kernel radius before measuring. It points to the article through the link sticker.
- Keywords: kernel design, Sobel, Scharr, Gaussian blur, border modes
- Canonical URL: https://canery.in/blogs/kernel-design-separability-borders-derivatives
