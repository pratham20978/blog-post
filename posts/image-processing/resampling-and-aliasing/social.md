---
social_schema: 2
canonical_url: "https://canery.in/blogs/resampling-and-aliasing"
---

# Social publishing package — resampling-and-aliasing

## LinkedIn post

Shrinking an image is not enlarging it backwards, and one interpolation flag hides the difference.

Enlarging only has to fill in between samples. The kernel — nearest, bilinear, bicubic, Lanczos — decides everything, as a trade between blocking, blur and ringing.

Shrinking also has to remove the detail the coarser grid cannot hold. That needs a kernel that gets wider as you shrink. A fixed-width interpolator reads the same few pixels per output however far you go.

Worked by hand on one five-pixel row, 40 255 40 200 200, shrunk to 0.6×:

→ OpenCV's default `INTER_LINEAR` gives 111.67, 40, 200. The row's mean falls from 147 to 117.2.
→ `INTER_AREA` gives 126, 115, 200. Mean: 147, exactly.
→ Nearest-neighbour keeps the bright pixel at full strength or drops it entirely, depending only on where the grid falls.

The check you can run on any resize: the total weight each input pixel gets across all outputs. For a 0.6× shrink every one should be 0.6. Linear's range from 0.333 to 1; area averaging's are all 0.6.

And "bicubic" is not one kernel. OpenCV uses a = −3/4 and overshoots an edge by 1/9; Pillow uses Keys' a = −1/2 and overshoots by 2/27. Only −1/2 is third-order accurate.

Part 3 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

A shrink by s needs a kernel 1/s times wider. The default resize reads two pixels per output however far you shrink.

Read the full article on Canery: https://canery.in/blogs/resampling-and-aliasing

## Instagram caption

Shrinking an image is not enlarging it backwards. Enlarging fills in between samples; shrinking also has to remove what the smaller grid cannot hold, and a fixed-width kernel cannot do that.

Swipe through one five-pixel row: the default resize against area averaging, an impulse that survives or vanishes with the grid, the column sums that audit any resize, why "bicubic" means different arithmetic in OpenCV and Pillow, the ringing an enlarge pays for, and why the sharper kernel is the worse downscaler.

Every number is worked by hand from the article's own row.

Link in bio.

#imageprocessing #computervision #opencv #signalprocessing #aliasing #interpolation #python

## Shared feed order

1. `assets/social/feed-01-shrinking-is-not-enlarging-backwards.png` — row r2 shrunk to 0.6× by the default bilinear and by area averaging, with their means
2. `assets/social/feed-02-the-impulse-is-there-or-not.png` — two nearest-neighbour grids half a cell apart keep or lose the 255
3. `assets/social/feed-03-audit-a-resize-by-its-column-sums.png` — column sums for nearest, linear and area averaging at 0.6×
4. `assets/social/feed-04-bicubic-is-a-family.png` — the Keys parameter a in four named cubics and the edge overshoot each gives
5. `assets/social/feed-05-enlarging-rings.png` — Lanczos-3 at 1.7× dipping to 14.1, rising to 225.0 and passing 255
6. `assets/social/feed-06-better-interpolator-worse-downscaler.png` — each kernel's gain at 0.4 cycles per pixel, above the 0.6× Nyquist
7. `assets/social/feed-07-read-the-article.png` — which call to use for shrink, enlarge and halve, and the CTA

## Instagram Story

- CTA: Why does a shrunk image look worse than an enlarged one? One five-pixel row, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/resampling-and-aliasing

### Story order

1. `assets/social/story-01-shrinking-is-not-enlarging-backwards.png` — Overlay: The default resize reads two pixels per output.
2. `assets/social/story-02-the-impulse-is-there-or-not.png` — Overlay: Same kernel, same factor. The grid decided.
3. `assets/social/story-03-audit-a-resize-by-its-column-sums.png` — Overlay: Every pixel should count 0.6.
4. `assets/social/story-04-read-the-article.png` — Overlay: Five rules for every resize. Link below.

## Asset metadata

### feed-01-shrinking-is-not-enlarging-backwards

- File: `assets/social/feed-01-shrinking-is-not-enlarging-backwards.png`
- Title: Shrinking is not enlarging backwards
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: the default bilinear shrink loses the row's mean; area averaging keeps it
- Technical source: Worked example › Shrinking to 0.6×; Figure 2; Implementation › OpenCV table (L28)
- Visual structure: lockup and counter; serif title; deck; row r2 as five pixel cells with c1 outlined; two 0.6× outputs below it, the default and INTER_AREA, each with its mean; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 07 · Shrinking is not enlarging backwards. · Enlarging fills in between samples. Shrinking also has to remove the detail the coarser grid cannot hold. · Row r2 · mean 147 · 40 255 40 200 200 · c0 c1 c2 c3 c4 · 0.6× · INTER_LINEAR, the default · 2 taps · 111.67 40 200 · mean 117.2 · 0.6× · INTER_AREA · width 1/s · 126 115 200 · mean 147.0 · A shrink by s needs a kernel 1/s times wider. The default reads the same two pixels however far you shrink. · Resampling and aliasing · canery.in
- Alt text: A five-pixel row 40 255 40 200 200 shrunk to 0.6× two ways: the default gives mean 117.2, area averaging keeps the mean at 147.
- Long description: The input row has pixel values 40, 255, 40, 200 and 200 with mean 147; the 255 is outlined. Below it, OpenCV's default bilinear resize at 0.6× produces three pixels, 111.67, 40 and 200, with mean 117.2. Area averaging (INTER_AREA), whose kernel is a box as wide as one new pixel, produces 126, 115 and 200, with mean 147.0. The takeaway: a shrink by factor s needs a kernel 1/s times wider, and the default reads the same two pixels per output however far you shrink.
- Keywords: image resizing, downscaling, bilinear interpolation, INTER_AREA, OpenCV, aliasing
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### feed-02-the-impulse-is-there-or-not

- File: `assets/social/feed-02-the-impulse-is-there-or-not.png`
- Title: The impulse is there, or it isn't
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the same nearest-neighbour shrink keeps or drops the bright pixel depending only on grid placement
- Technical source: The problem, Figure 1; Worked example › Nearest; L31
- Visual structure: lockup and counter; title; deck; row r2 as five cells; two three-pixel outputs labelled with the pixels each reads, the second with its 255 outlined; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 07 · The impulse is there, or it isn't. · Row r2 shrunk to 0.6× by nearest-neighbour, twice. Same kernel, same factor, grids laid half a cell apart. · 40 255 40 200 200 · c0 c1 c2 c3 c4 · pixel centres · reads c0 c2 c4 · 40 40 200 · OpenCV INTER_NEAREST · reads c0 c1 c3 · 40 255 200 · Output that depends on where the grid happens to fall, not on the image, is what aliasing looks like in space. · Resampling and aliasing · canery.in
- Alt text: Two nearest-neighbour shrinks of the same row: sampling at pixel centres gives 40 40 200, OpenCV's floor index gives 40 255 200.
- Long description: Row r2, 40 255 40 200 200, is shrunk to three pixels by nearest-neighbour twice. Sampling at pixel centres reads c0, c2 and c4 and outputs 40, 40, 200, losing the 255. OpenCV's INTER_NEAREST, which takes source index floor(j/s), reads c0, c1 and c3 and outputs 40, 255, 200, keeping it at full strength. The two grids sit half an output cell apart. The takeaway: output that depends on where the grid falls rather than on the image is what aliasing looks like in space.
- Keywords: nearest neighbour, INTER_NEAREST, INTER_NEAREST_EXACT, pixel centres, aliasing, downscaling
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### feed-03-audit-a-resize-by-its-column-sums

- File: `assets/social/feed-03-audit-a-resize-by-its-column-sums.png`
- Title: Audit a resize by its column sums
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the total weight each input pixel gets exposes aliasing; only area averaging is uniform
- Technical source: Why does a shrink need a prefilter and an enlarge not?; Figure 8; The math, equation (4)
- Visual structure: lockup and counter; title; deck; three rows of five bars — nearest, linear, area — labelled with each column sum; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 07 · Audit a resize by its column sums. · A column sum is the total weight one input pixel gets across every output. For a 0.6× shrink they should all be 0.6. · c0 c1 c2 c3 c4 · nearest 1 0 1 0 1 · linear 0.667 0.333 1 0.333 0.667 · area 0.6 0.6 0.6 0.6 0.6 · Equal columns count every pixel equally, and keep the mean: 147 in, 147 out. Only area averaging manages it. · Resampling and aliasing · canery.in
- Alt text: Bar rows of the total weight each of five input pixels gets in a 0.6× shrink: nearest 1 0 1 0 1, linear uneven, area all 0.6.
- Long description: For a 0.6× shrink of a five-pixel row, each bar shows one input pixel's total weight across the three outputs. Nearest-neighbour gives 1, 0, 1, 0, 1, so two pixels are never read. Bilinear gives 0.667, 0.333, 1, 0.333, 0.667, so c2 counts three times as much as c1. Area averaging gives 0.6 to every pixel. Equal column sums mean every pixel counts equally and the output keeps the input's mean, 147.
- Keywords: resampling matrix, column sums, area averaging, bilinear, nearest neighbour, prefilter
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### feed-04-bicubic-is-a-family

- File: `assets/social/feed-04-bicubic-is-a-family.png`
- Title: "Bicubic" is not one kernel
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: each library's bicubic is a different value of Keys' parameter, with a different overshoot
- Technical source: Why is bicubic not one kernel?; Figure 7; L02, L05, L06, L15, L32, L39
- Visual structure: lockup and counter; title; deck; a four-row table of cubic kernel, parameter and edge overshoot, OpenCV highlighted; the overshoot formula; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 07 · "Bicubic" is not one kernel. · Keys' cubic has a free parameter a. Each library picks its own, and the edge overshoot changes with it. · cubic kernel · parameter · overshoot on an edge · Rifman a = −1 14.8% · OpenCV INTER_CUBIC a = −3/4 11.1% · Keys · Pillow BICUBIC a = −1/2 7.4% · Mitchell (B, C) = (1/3, 1/3) off the axis 3.6% · Keys family: overshoot = −4a/27 of the step height · Only a = −1/2 is third-order accurate: it reproduces every quadratic exactly. OpenCV uses −3/4. · Resampling and aliasing · canery.in
- Alt text: Table of four cubic kernels and their edge overshoot: Rifman 14.8%, OpenCV a = −3/4 11.1%, Keys and Pillow 7.4%, Mitchell 3.6%.
- Long description: Keys' cubic convolution kernel has one free parameter, a. Rifman's original a = −1 overshoots a step edge by 14.8% of its height; OpenCV's INTER_CUBIC uses a = −3/4 and overshoots by 11.1%; Keys' a = −1/2, used by Pillow's BICUBIC, overshoots by 7.4%; Mitchell and Netravali's recommended (B, C) = (1/3, 1/3), off the interpolating axis, overshoots by 3.6%. For the Keys family the overshoot is exactly −4a/27 of the step. Only a = −1/2 is third-order accurate, reproducing every quadratic exactly.
- Keywords: bicubic interpolation, cubic convolution, Keys kernel, Catmull-Rom, Mitchell-Netravali, OpenCV, Pillow
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### feed-05-enlarging-rings

- File: `assets/social/feed-05-enlarging-rings.png`
- Title: Enlarging rings
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: a sharp enlarging kernel overshoots and undershoots near edges and impulses
- Technical source: Worked example › Enlarging to 1.7×; Figure 3; L12
- Visual structure: lockup and counter; one-line title; deck; the Lanczos-3 reconstruction of row r2 with reference lines at 40, 200 and 255, eight samples dotted and three labelled; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 07 · Enlarging rings. · Lanczos-3 keeps the impulse sharp at 1.7× and pays for it: 14.1 in a region that is flat 40, 225.0 over a flat 200. · 255 · 200 · 40 · 8-bit ceiling · 255.6 · 225.0 · 14.1 · Row r2 enlarged 1.7× by Lanczos-3 · eight samples · Negative lobes buy sharpness. Near an edge they push values past the input's range, and 8-bit output clips. · Resampling and aliasing · canery.in
- Alt text: Lanczos-3 curve through the row enlarged 1.7×: samples dip to 14.1 below a flat 40, reach 225.0 over 200 and pass 255.
- Long description: Row r2, 40 255 40 200 200, is enlarged to eight samples by Lanczos-3. The continuous reconstruction dips below the flat 40 to a sample of 14.1 beside the impulse, peaks at 255.6 on the impulse, just past the 8-bit ceiling of 255, and overshoots the flat 200 to 225.0 after the step. The negative lobes that keep the impulse sharp are what push values past the input's range; an 8-bit output clips them.
- Keywords: Lanczos resampling, ringing, overshoot, image upscaling, 8-bit clipping
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### feed-06-better-interpolator-worse-downscaler

- File: `assets/social/feed-06-better-interpolator-worse-downscaler.png`
- Title: The better interpolator is the worse downscaler
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: sharper kernels pass more of the band a shrink must remove; widening the kernel fixes it
- Technical source: What does each kernel do to the spectrum?; Figures 6 and 9
- Visual structure: lockup and counter; title; deck; four horizontal bars of gain at 0.4 cycles per pixel, the widened triangle in accent; a note on folding; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 07 · The better interpolator is the worse downscaler. · A 0.6× shrink must remove everything between 0.3 and 0.5 cycles per pixel. Sharper kernels let more of it through. · kernel · gain at 0.4 cycles/px — above the 0.6× Nyquist · Lanczos-3 0.821 · Keys, a = −1/2 0.716 · linear 0.573 · triangle widened by 1/0.6 0.171 · whatever passes folds to a period-5 stripe · A flat band up to 0.5 is exactly what leaks 0.3 to 0.5. Widening the kernel by 1/s moves its cutoff to 0.3. · Resampling and aliasing · canery.in
- Alt text: Bars of each kernel's gain at 0.4 cycles per pixel: Lanczos-3 0.821, Keys 0.716, linear 0.573, the widened triangle 0.171.
- Long description: A 0.6× shrink has a new Nyquist frequency of 0.3 cycles per input pixel, so a pattern at 0.4 must be removed before sampling. Unwidened, Lanczos-3 passes it at 0.821, Keys' cubic at 0.716 and linear at 0.573; whatever passes folds into a stripe with a five-pixel period. The triangle widened by 1/0.6 passes it at only 0.171, because widening a kernel by 1/s moves its cutoff from 0.5 to 0.3. The sharper the interpolator, the more it aliases when used to shrink.
- Keywords: transfer function, aliasing, Nyquist frequency, Lanczos, bicubic, prefilter
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### feed-07-read-the-article

- File: `assets/social/feed-07-read-the-article.png`
- Title: Resampling and aliasing, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: which call to reach for when shrinking, enlarging and halving, and the article link
- Technical source: Implementation: the tooling map; Figure 10; L28, L32, L36, L37, L39–L41
- Visual structure: lockup and counter; title; deck; a four-item panel — shrink, enlarge, halve, never — each with calls and a one-line reason; takeaway; CTA footer with the article address
- Visible-text transcript: Canery.in · 07 / 07 · Resampling and aliasing, by hand. · Nearest, bilinear, bicubic, Lanczos and area averaging on one five-pixel row: every tap and every output value. · shrink · INTER_AREA · Pillow resize · skimage resize · a kernel that widens with 1/s · enlarge · INTER_CUBIC (a = −3/4) · Pillow BICUBIC (a = −1/2) · pick the ringing you can live with · halve · pyrDown · INTER_LINEAR at exactly 0.5× · the one factor the default gets right · never · blur after the shrink · the folded detail is already there · The full walk-through, with the tooling map for OpenCV, Pillow, scikit-image and SciPy. · Read it at canery.in/blogs/resampling-and-aliasing
- Alt text: Summary card: shrink with INTER_AREA or Pillow, enlarge with a chosen cubic, halve with pyrDown, never blur after shrinking.
- Long description: The closing card lists four rules. Shrink with a kernel that widens by 1/s: OpenCV's INTER_AREA, Pillow's resize or scikit-image's resize. Enlarge with a cubic whose ringing you accept: OpenCV's INTER_CUBIC uses a = −3/4, Pillow's BICUBIC a = −1/2. Halve with pyrDown or with INTER_LINEAR at exactly 0.5×, the one factor where the default averages correctly. Never blur after the shrink, because the folded detail is already in the low frequencies. It links to the full article on Canery.
- Keywords: image resizing, OpenCV resize, Pillow resize, scikit-image, pyrDown, INTER_AREA
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### story-01-shrinking-is-not-enlarging-backwards

- File: `assets/social/story-01-shrinking-is-not-enlarging-backwards.png`
- Title: Shrinking is not enlarging backwards
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: the default shrink drops the mean; area averaging keeps it
- Technical source: Worked example › Shrinking to 0.6×; Figure 2; L28
- Visual structure: lockup and counter; title; two-line deck; the row and its two 0.6× outputs at Story scale with means; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Shrinking is not enlarging backwards. · The default resize reads two pixels per output, however far you shrink. · Row r2 · mean 147 · 40 255 40 200 200 · c0 c1 c2 c3 c4 · 0.6× · INTER_LINEAR, the default · 2 taps · 111.67 40 200 · mean 117.2 · 0.6× · INTER_AREA · width 1/s · 126 115 200 · mean 147.0 · Area averaging keeps the mean at 147. The default drops it to 117.2. · Resampling and aliasing · canery.in
- Alt text: A five-pixel row shrunk to 0.6×: the default resize gives mean 117.2, area averaging keeps the input's mean of 147.
- Long description: Story recomposition of the first feed card. Row r2, 40 255 40 200 200 with mean 147, is shrunk to three pixels. OpenCV's default bilinear gives 111.67, 40 and 200 with mean 117.2; area averaging gives 126, 115 and 200 with mean 147.0. The default reads two pixels per output however far the image is shrunk.
- Keywords: image resizing, downscaling, INTER_AREA, INTER_LINEAR, OpenCV, aliasing
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### story-02-the-impulse-is-there-or-not

- File: `assets/social/story-02-the-impulse-is-there-or-not.png`
- Title: The impulse is there, or it isn't
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: grid placement alone decides whether the bright pixel survives a nearest-neighbour shrink
- Technical source: The problem, Figure 1; L31
- Visual structure: lockup and counter; title; deck; the row and two three-pixel nearest-neighbour outputs; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · The impulse is there, or it isn't. · Two nearest-neighbour grids, half a cell apart. · 40 255 40 200 200 · c0 c1 c2 c3 c4 · pixel centres · reads c0 c2 c4 · 40 40 200 · OpenCV INTER_NEAREST · reads c0 c1 c3 · 40 255 200 · Same kernel, same factor. The grid decided, not the image. · Resampling and aliasing · canery.in
- Alt text: Two nearest-neighbour shrinks of one row half a cell apart: one outputs 40 40 200, the other keeps the 255 as 40 255 200.
- Long description: Row r2 is shrunk to 0.6× by nearest-neighbour on two grids half an output cell apart. Sampling at pixel centres reads c0, c2, c4 and outputs 40, 40, 200. OpenCV's INTER_NEAREST reads c0, c1, c3 and outputs 40, 255, 200. The kernel and the factor are the same; only the grid placement differs.
- Keywords: nearest neighbour, INTER_NEAREST, aliasing, pixel centres, downscaling
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### story-03-audit-a-resize-by-its-column-sums

- File: `assets/social/story-03-audit-a-resize-by-its-column-sums.png`
- Title: Audit a resize by its column sums
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: uniform column sums are the signature of a resize that counts every pixel equally
- Technical source: Why does a shrink need a prefilter and an enlarge not?; Figure 8
- Visual structure: lockup and counter; title; deck; three rows of five bars with column sums; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Audit a resize by its column sums. · The total weight each input pixel gets, for a 0.6× shrink. · c0 c1 c2 c3 c4 · nearest 1 0 1 0 1 · linear 0.667 0.333 1 0.333 0.667 · area 0.6 0.6 0.6 0.6 0.6 · All equal to 0.6: every pixel counted. Only area averaging does it. · Resampling and aliasing · canery.in
- Alt text: Column sums at 0.6×: nearest 1 0 1 0 1, linear 0.667 0.333 1 0.333 0.667, area averaging 0.6 for all five pixels.
- Long description: The total weight each of five input pixels receives in a 0.6× shrink. Nearest-neighbour: 1, 0, 1, 0, 1. Bilinear: 0.667, 0.333, 1, 0.333, 0.667. Area averaging: 0.6 for every pixel. Only equal sums count every pixel equally.
- Keywords: resampling matrix, column sums, area averaging, prefilter, aliasing
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Five rules for every resize
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the five rules the article works out, and the link
- Technical source: Key takeaways; Implementation › Check any resize by hand
- Visual structure: lockup and counter; title; deck; a numbered five-rule panel; takeaway; CTA footer pointing at the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Five rules for every resize. · Worked by hand on one five-pixel row. · 1 enlarging: choose the kernel · 2 shrinking: widen it by 1/s · 3 bicubic: check which a · 4 audit: resize an impulse, sum it · 5 never blur after the shrink · The full walk-through is on Canery. · Link in the sticker above
- Alt text: Five numbered rules: choose the kernel when enlarging, widen it by 1/s when shrinking, check the bicubic a, audit, never blur after.
- Long description: The closing Story frame lists five rules from the article: when enlarging, the kernel is the whole decision; when shrinking, widen the kernel by 1/s; for bicubic, check which value of a the library uses; audit any resize by resizing a single bright pixel and summing the output; and never blur after the shrink. It points to the article through the link sticker.
- Keywords: image resizing, interpolation, aliasing, bicubic, resampling
- Canonical URL: https://canery.in/blogs/resampling-and-aliasing
