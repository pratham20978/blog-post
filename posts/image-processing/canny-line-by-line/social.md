---
social_schema: 2
canonical_url: "https://canery.in/blogs/canny-line-by-line"
---

# Social publishing package — canny-line-by-line

## LinkedIn post

Run cv2.Canny with its defaults on a 5×5 patch that holds one clean step edge and one bright pixel, and no pair of thresholds returns the edge as a line.

Worked by hand, the reason is in the last two steps of the method, not in the thresholds:

→ cv2.Canny takes Sobel derivatives of the image as it is. It has no Gaussian step, and it pads the border by replicating the edge pixel.
→ Its default magnitude is L1, |Gx| + |Gy|. Beside the bright pixel, an oblique gradient of (425, 215) reads 640 in L1, exactly the edge's own value. The tie fails OpenCV's suppression test, and two rows of the edge disappear. With L2 it reads 476.3 and the edge survives.
→ Hysteresis grades connected chains, not pixels. The bright pixel's ring of candidates touches the edge at a corner, so any low threshold below 430 lets it ride in, and Canny's own ratio of 2 to 3 always does.
→ Smooth with a 3×3 Gaussian first, and the ring shrinks to two isolated pixels with no seed. Now thresholds of 450 and 180 return the edge alone.

The thresholds themselves are raw Sobel units: a step of h grey levels reads 4h at aperture 3 and 48h at aperture 5. Set them from the noise, not by trial: a high threshold a chosen number of noise widths above flat-region gradient, a low one a half to a third of it.

Part 8 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

Hysteresis does not grade pixels. The high threshold decides which chains exist; the low one decides where each one ends.

Read the full article on Canery: https://canery.in/blogs/canny-line-by-line

## Instagram caption

Every threshold pair fails this edge, until you smooth first. Swipe through Canny edge detection worked by hand on one 5×5 patch: why the bright pixel has no gradient but a ring of edge candidates, how OpenCV's default L1 magnitude deletes two rows of a clean edge, the three tie rules that give zero, one or two edge pixels, why hysteresis grades chains rather than pixels, why smoothing is what makes Canny's 2:1 to 3:1 ratio work, and how to set both thresholds from the noise.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#computervision #imageprocessing #edgedetection #canny #opencv #python #signalprocessing

## Shared feed order

1. `assets/social/feed-01-every-threshold-pair-fails.png` — the patch beside cv2.Canny's default result: three dots of the edge and a ring from the bright pixel
2. `assets/social/feed-02-the-bright-pixel-has-no-gradient.png` — the Sobel magnitude grid: 640 on both sides of the step, 0 on the bright pixel, a ring around it
3. `assets/social/feed-03-one-tie-two-lost-rows.png` — row r1 under L2 and L1: the L1 tie at 640 costs the row its edge pixel
4. `assets/social/feed-04-zero-one-or-two-pixels.png` — three tie rules on 0, 0, 640, 640, 0
5. `assets/social/feed-05-chains-not-pixels.png` — hysteresis at 450 and 180, before and after smoothing: 10 pixels against 5
6. `assets/social/feed-06-smooth-first.png` — what it takes to get the edge alone on each version of the patch
7. `assets/social/feed-07-set-them-from-the-noise.png` — thresholds from a Rayleigh noise model: 29.7 and 14.9 for noise of 2 levels
8. `assets/social/feed-08-read-the-article.png` — the four parts of the article, and the CTA

## Instagram Story

- CTA: Why does cv2.Canny miss a perfectly clean edge? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/canny-line-by-line

### Story order

1. `assets/social/story-01-every-threshold-pair-fails.png` — Overlay: Three dots, or the dots and a ring.
2. `assets/social/story-02-640-equals-640.png` — Overlay: One tie deletes two rows.
3. `assets/social/story-03-chains-not-pixels.png` — Overlay: Smooth first, and the ratio works.
4. `assets/social/story-04-read-the-article.png` — Overlay: Canny, line by line. Link below.

## Asset metadata

### feed-01-every-threshold-pair-fails

- File: `assets/social/feed-01-every-threshold-pair-fails.png`
- Title: Every threshold pair fails this edge
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: with its defaults, cv2.Canny cannot return the patch's clean step as a line at any pair of thresholds
- Technical source: Worked example, steps 2 and 3, Figure 2 (L1 panel) and Figure 4 (raw L1 panel)
- Visual structure: lockup and counter; serif title; deck; a panel with two 5×5 grids side by side, the patch with its bright pixel outlined and cv2.Canny's default result with the edge pixels in blue and the ring in orange; three lines of outcomes; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Every threshold pair fails this edge. · cv2.Canny, defaults, on one 5×5 patch: a clean step of 160 and one bright pixel. · the patch · grid: every row 40 40 40 200 200, with 255 at row 2, column 1 · cv2.Canny, defaults: L1 · grid: 640 at (r0, c2), (r2, c3) and (r4, c2); 430 at (r1, c0), (r1, c1), (r2, c0), (r3, c0), (r3, c1) · low 430 or more: three separate dots · low below 430: the dots and a ring of five · high at 640 or more: nothing at all · The thresholds were not the problem. What they were compared with was. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: A 5×5 patch with a step edge and one bright pixel, beside cv2.Canny's default result: three dots of the edge and a ring from the pixel.
- Long description: The series' 5×5 patch has a step from 40 to 200 between its third and fourth columns and one bright pixel of 255 among 40s. With OpenCV's defaults — no smoothing, the L1 magnitude, aperture 3 — suppression keeps only three pixels of the edge, at rows 0, 2 and 4, each reading 640, and five pixels of 430 around the bright pixel. Hysteresis then gives three separate dots if the low threshold is 430 or more, the dots plus the ring of five if it is lower, and nothing if the high threshold is 640 or more. No pair returns the edge as a connected line. The takeaway: the thresholds were compared with gradient values that the default settings had already distorted.
- Keywords: Canny edge detector, cv2.Canny, hysteresis thresholding, non-maximum suppression, edge detection, OpenCV
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### feed-02-the-bright-pixel-has-no-gradient

- File: `assets/social/feed-02-the-bright-pixel-has-no-gradient.png`
- Title: The bright pixel has no gradient
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the Sobel gradient reads the step on two columns at once and reads the bright pixel itself as zero, inside a ring of large values
- Technical source: Worked example, step 1, Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with a 5×5 grid of L2 magnitudes shaded high = bright, the bright pixel's cell outlined, and four notes to its right; a scale note; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · The bright pixel has no gradient. · Sobel on the raw patch, as cv2.Canny computes it: no smoothing first. · Sobel magnitude, L2, replicate border · grid rows: 0 0 640 640 0; 304.1 430 476.3 640 0; 430 0 210 640 0; 304.1 430 476.3 640 0; 0 0 640 640 0 · the step: 4 × 160 = 640 · on c2 and c3 at once · the 255 itself: 0 · left and right cancel, so do above and below · around it: 210 to 476.3 · magnitude cells shaded high = bright, 640 the brightest · A bright pixel becomes a ring of edge candidates around a zero. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: A 5×5 grid of Sobel magnitudes: 640 down both sides of the step, 0 on the bright pixel and a ring of 210 to 476.3 around it.
- Long description: The 3×3 Sobel operator, applied to the raw patch with a replicate border as cv2.Canny does, reads the step of 160 as 640, four times its height, on both of its sides, the third and fourth columns. The bright pixel itself has a gradient of 0, because its left and right columns are equal and so are the rows above and below it. Around it the magnitudes run from 210 to 476.3. The takeaway: a single bright pixel does not become one edge pixel; it becomes a ring of edge candidates around a zero.
- Keywords: Sobel operator, gradient magnitude, impulse noise, Canny edge detector, replicate border
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### feed-03-one-tie-two-lost-rows

- File: `assets/social/feed-03-one-tie-two-lost-rows.png`
- Title: One tie, two lost rows
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: OpenCV's default L1 magnitude makes an oblique gradient tie the edge pixel next to it, and the tie deletes the edge on two rows
- Technical source: Worked example, step 2, Figure 2; Units section, L1 against L2
- Visual structure: lockup and counter; serif title; deck; a panel with row r1 drawn twice, once with L2 values and once with L1 values, survivors coloured and the tied pair outlined in dashed orange; a colour note; three lines of arithmetic; a note on row r3; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · One tie, two lost rows. · OpenCV's default magnitude is L1, |Gx| + |Gy|. On an oblique gradient it reads high. · row r1, columns c0 to c4 · L2: 304.1 430 476.3 640 0 · L1: 430 430 640 640 0 · orange: the bright pixel's ring, kept either way · (r1, c2): Gx 425, Gy 215 · L2 √(425² + 215²) = 476.3 → (r1, c3) wins · L1 425 + 215 = 640: a tie, and both lose · the same happens on row r3 · L2gradient=True keeps the edge on every row of the patch. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: Row r1 of the patch under L2 and L1: in L1 the oblique pixel reads 640, ties the edge pixel beside it, and both are suppressed.
- Long description: At row 1, column 2, next to the bright pixel, the Sobel gradient is (425, 215). Its Euclidean length is 476.3, so the true edge pixel to its right, at 640, wins suppression and the edge survives on that row. OpenCV's default L1 magnitude adds the two components, 425 + 215 = 640, which equals the edge pixel's value; OpenCV's test needs the edge pixel to be strictly greater than its left neighbour, so it fails, and the oblique pixel loses its own diagonal test, so neither survives. The same happens on row 3. The ring pixels around the bright pixel survive under either norm. The takeaway: L2gradient=True keeps the edge on every row of the patch.
- Keywords: L1 norm, L2gradient, gradient magnitude, non-maximum suppression, cv2.Canny, tie
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### feed-04-zero-one-or-two-pixels

- File: `assets/social/feed-04-zero-one-or-two-pixels.png`
- Title: Zero, one or two pixels
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: when a step falls exactly between two pixels, the suppression tie rule decides whether the edge gets zero, one or two pixels a row
- Technical source: Non-maximum suppression section, "Ties", Figure 6
- Visual structure: lockup and counter; serif title; deck; a panel with three rows of five cells, 0 0 640 640 0, each under a rule name, kept cells filled blue and suppressed cells dashed, with a verdict to the right of each row; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Zero, one or two pixels. · The step falls between c2 and c3, so Sobel reads 640 on both. Three tie rules, three answers. · strict on both sides · 0 0 640 640 0 · no pixel: the edge vanishes · OpenCV: > before, ≥ after · 0 0 640 640 0 · one pixel, the left of the pair · scikit-image: ≥ on both sides · 0 0 640 640 0 · two pixels: a double-width edge · On an edge between pixels, the tie rule decides what you get. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: The profile 0, 0, 640, 640, 0 under three tie rules: strict keeps no pixel, OpenCV's keeps the left one, scikit-image's keeps both.
- Long description: On a clean row of the patch the gradient magnitude is 0, 0, 640, 640, 0, because the step lies exactly between the third and fourth pixels. A suppression test that is strict on both sides, as Grompone von Gioi and Randall state Canny's condition, keeps neither 640 and the edge vanishes. OpenCV's test, strictly greater than the neighbour before and at least equal to the one after, keeps exactly one, the left pixel. scikit-image keeps a pixel when no neighbour exceeds it, so it keeps both and the edge is two pixels wide. The takeaway: on an edge that falls between pixels, the tie rule, not the threshold, decides what you get.
- Keywords: non-maximum suppression, tie breaking, edge thickness, OpenCV, scikit-image, Canny edge detector
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### feed-05-chains-not-pixels

- File: `assets/social/feed-05-chains-not-pixels.png`
- Title: Hysteresis grades chains, not pixels
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: with the same thresholds, hysteresis keeps ten pixels on the raw patch and five after smoothing, because what it judges is connectivity
- Technical source: Worked example, steps 3 and 4, Figure 3
- Visual structure: lockup and counter; serif title; deck; a panel with two 5×5 result grids, the raw patch with the line in blue and the ring in orange, and the smoothed patch with a blue column and two dashed cells; three lines of explanation; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Hysteresis grades chains, not pixels. · High 450, low 180, a ratio of 2.5, before and after smoothing. · raw patch, L2 · grid: 640 at (r0, c2), (r1, c3), (r2, c3), (r3, c3), (r4, c2); 304.1 at (r1, c0) and (r3, c0); 430 at (r1, c1), (r2, c0), (r3, c1) · after the 3×3 Gaussian · grid: column c3 reads 474.9, 436.5, 408.8, 436.5, 474.9; 219.7 at (r1, c0) and (r3, c0), dashed · raw: the ring touches the line at a corner, so all 10 pixels come out · smoothed: two lone 219.7s have no seed: 5 out · High decides which chains exist. Low decides where each one ends. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: Hysteresis at 450 and 180: on the raw patch the ring joins the line and ten pixels survive; after smoothing only the five-pixel column does.
- Long description: With a high threshold of 450 and a low one of 180, a ratio of 2.5 within Canny's recommended range, hysteresis on the raw patch keeps all ten suppression survivors: the five-pixel line of 640s and the bright pixel's ring of 304.1s and 430s, because the ring touches the line at a corner and every ring pixel is above the low threshold. After the series' 3×3 Gaussian the line is a straight column at 474.9, 436.5, 408.8, 436.5 and 474.9, and the ring shrinks to two pixels of 219.7 that touch nothing and contain no seed, so they are dropped and five pixels come out. The takeaway: the high threshold decides which connected chains exist, and the low threshold decides where each one ends.
- Keywords: hysteresis thresholding, connected components, Canny edge detector, Gaussian smoothing, edge linking
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### feed-06-smooth-first

- File: `assets/social/feed-06-smooth-first.png`
- Title: Smooth first, and the ratio works
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: only after Gaussian smoothing does a threshold pair in Canny's 2:1 to 3:1 ratio return the edge alone
- Technical source: Worked example, the scorecard; Intuition, Figure 4
- Visual structure: lockup and counter; serif title; deck; a panel with a four-row table, each pipeline on the left and what it takes to get the edge alone on the right; a closing note; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Smooth first, and the ratio works. · What it takes to get the step's line alone, on each version of the patch. · TO GET THE STEP ALONE · cv2.Canny defaults, raw (L1) — no pair works · raw, L2gradient=True — high ÷ low under 1.49 · 3×3 Gaussian first, L2 — high 219.7 to 474.9, low under 408.8 · Canny's own ratio: 2 to 3 — fits only the last · smoothing detaches the ring from the step · cv2.Canny does not smooth. The Gaussian is yours to add. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: A table of what returns the patch's edge alone: no pair with defaults, ratios under 1.49 with L2, and Canny's 2 to 3 only after smoothing.
- Long description: On the raw patch with OpenCV's defaults, no pair of thresholds returns the step's line by itself. With L2gradient=True it comes out alone only when the low threshold is at least 430 and the high one below 640, a ratio under 1.49. After the series' 3×3 Gaussian, any high threshold from 219.7 to just under 474.9 with a low one under 408.8 returns the line alone. Canny's own ratio of 2 to 3 fits only that last case, because smoothing detaches the bright pixel's ring from the step. The takeaway: cv2.Canny does not smooth, so the Gaussian is the user's to add.
- Keywords: Canny thresholds, threshold ratio, Gaussian blur, cv2.Canny, L2gradient
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### feed-07-set-them-from-the-noise

- File: `assets/social/feed-07-set-them-from-the-noise.png`
- Title: Set them from the noise
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: under a Gaussian noise model the flat-region gradient is Rayleigh, so a chosen false-seed rate gives the high threshold directly
- Technical source: "How do you set the thresholds without searching?", Figure 9, equation (4)
- Visual structure: lockup and counter; serif title; deck; a panel with the threshold formula, a Rayleigh curve with the low and high thresholds marked, three results to its right, the weakest seeding step and a model note; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Set them from the noise. · Pick how many false seeds a flat region may produce, and derive the number. · high = s √(2 ln(1/α)), s = √12 σ · flat-region magnitude is Rayleigh with scale s · low 14.9 · high 29.7 · gradient magnitude, σ = 2 · α = 1 in 10,000 → high 29.7 · low = high ÷ 2 → 1 flat pixel in 10 above it · weakest step that can seed: 29.7 / 4 = 7.4 grey levels · model: Gaussian pixel noise, Sobel aperture 3, L2 · A ratio of 2 to 3 is what chains of 4 to 9 pixels can afford under that model. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: A Rayleigh curve of flat-region gradient with the low threshold at 14.9 and the high at 29.7, derived from noise of 2 grey levels.
- Long description: If every pixel carries independent Gaussian noise of standard deviation σ, each 3×3 Sobel derivative has noise of √12 σ and the two are independent, so the L2 gradient magnitude on a flat region follows a Rayleigh distribution with scale s = √12 σ. Choosing the fraction α of flat pixels allowed to become false seeds gives the high threshold as s √(2 ln(1/α)). For σ = 2 and α of one in ten thousand, s is 6.93 and the high threshold 29.7, so the weakest step that can start an edge is 7.4 grey levels. A low threshold of half that, 14.9, lets one flat pixel in ten through as a candidate. The takeaway, within that model: a ratio of 2 to 3 is the contrast drop that chains of 4 to 9 pixels can afford.
- Keywords: Canny thresholds, Rayleigh distribution, noise estimation, false alarm rate, Sobel operator
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Canny edge detection, line by line
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four parts of the article, and where to read it
- Technical source: the article's section structure: suppression, hysteresis, units, setting the thresholds
- Visual structure: lockup and counter; serif title; deck; a panel listing four topics, each with a one-line summary and a detail; takeaway; the canonical URL as the footer
- Visible-text transcript: Canery.in · 08 / 08 · Canny edge detection, line by line. · Every step worked by hand on one 5×5 patch. · suppression — four bins, or interpolation — and a tie rule: 0, 1 or 2 pixels a row · hysteresis — chains, not pixels — 450 and 180: 10 pixels raw, 5 smoothed · units — raw Sobel: 4h at aperture 3, 48h at 5 — L1 reads diagonals up to 41% high · thresholds — from the noise, not by trial — high = s √(2 ln(1/α)), low a half to a third · The full walk-through, with every number worked by hand and the tooling map. · READ IT AT CANERY.IN/BLOGS/CANNY-LINE-BY-LINE
- Alt text: A summary card listing suppression, hysteresis, threshold units and setting thresholds from noise, with the article's address.
- Long description: The closing card lists the article's four parts: suppression, with its direction bins or interpolation and a tie rule that gives zero, one or two pixels a row; hysteresis, which grades chains rather than pixels and keeps 10 pixels of the raw patch but 5 of the smoothed one at thresholds of 450 and 180; the units of the thresholds, raw Sobel output at 4h for a step at aperture 3 and 48h at aperture 5, with L1 reading diagonals up to 41% high; and thresholds set from the noise with a high threshold of s √(2 ln(1/α)) and a low one a half to a third of it. It ends with the article's address on Canery.
- Keywords: Canny edge detector, edge detection tutorial, hysteresis, non-maximum suppression, image processing
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### story-01-every-threshold-pair-fails

- File: `assets/social/story-01-every-threshold-pair-fails.png`
- Title: Every threshold pair fails
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: cv2.Canny's default result on the patch: three dots of the edge, or the dots with a ring
- Technical source: Worked example, steps 2 and 3, Figure 2 (L1 panel)
- Visual structure: lockup and counter; serif title; deck; one large 5×5 result grid, the edge pixels in blue and the ring in orange; a caption; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Every threshold pair fails. · One clean step of 160, one bright pixel. · cv2.Canny, defaults, on the patch · grid: 640 at (r0, c2), (r2, c3), (r4, c2); 430 at (r1, c0), (r1, c1), (r2, c0), (r3, c0), (r3, c1) · three dots, or the dots and a ring · Smoothing first is what fixes it. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: cv2.Canny's default result on the 5×5 patch: three separate pixels of the edge and five pixels of a ring around the bright pixel.
- Long description: With its defaults, cv2.Canny keeps three pixels of the patch's step edge, each 640, at rows 0, 2 and 4, and five pixels of 430 around the bright pixel. Depending on the low threshold the output is the three separate dots or the dots with the ring; no pair of thresholds returns the edge as a line. The takeaway: smoothing the patch first is what fixes it.
- Keywords: Canny edge detector, cv2.Canny, edge detection, hysteresis, OpenCV
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### story-02-640-equals-640

- File: `assets/social/story-02-640-equals-640.png`
- Title: 640 = 640
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the L1 magnitude makes an oblique pixel tie the edge pixel beside it, and the tie deletes that row of the edge
- Technical source: Worked example, step 2; Figure 2
- Visual structure: lockup and counter; serif title; deck; large arithmetic for L1 in orange, a line on the tie, and the L2 value in blue; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · 640 = 640. · OpenCV's default L1 magnitude on row r1 of the patch. · at (r1, c2), Gx 425 and Gy 215 · L1: 425 + 215 = 640 · ties (r1, c3) = 640: both lost · L2: 476.3 · (r1, c3) wins with 640 · The default norm deletes two rows of the edge. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: At row 1, column 2, the L1 magnitude 425 + 215 = 640 ties the edge pixel's 640 and both are lost; with L2 it reads 476.3.
- Long description: Next to the bright pixel, at row 1, column 2, the gradient is (425, 215). OpenCV's default L1 magnitude adds them to 640, equal to the edge pixel beside it, and the tie makes both fail suppression. The Euclidean magnitude, 476.3, is smaller, so the edge pixel wins. The takeaway: the default norm deletes two rows of the edge, rows 1 and 3.
- Keywords: L1 norm, L2gradient, cv2.Canny, non-maximum suppression, gradient magnitude
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### story-03-chains-not-pixels

- File: `assets/social/story-03-chains-not-pixels.png`
- Title: Chains, not pixels
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the same thresholds keep ten pixels of the raw patch and five of the smoothed one
- Technical source: Worked example, steps 3 and 4, Figure 3
- Visual structure: lockup and counter; serif title; deck; two 5×5 result grids side by side with their counts below; a note on the thresholds; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Chains, not pixels. · Hysteresis keeps a chain if it holds a seed. · raw patch · grid: the line of 640s and a ring of 304.1s and 430s · after the Gaussian · grid: a column of 474.9, 436.5, 408.8, 436.5, 474.9 and two dashed 219.7s · 10 pixels out · 5 pixels out · same thresholds: high 450, low 180 · The ratio works only after smoothing. · CANNY, LINE BY LINE · CANERY.IN
- Alt text: Two hysteresis results at 450 and 180: ten pixels on the raw patch, ring included; five on the smoothed patch, the column alone.
- Long description: Hysteresis keeps every connected chain of candidates that contains at least one pixel above the high threshold. At a high threshold of 450 and a low one of 180, the raw patch keeps ten pixels, because the bright pixel's ring touches the edge's line at a corner. After a 3×3 Gaussian the ring is two isolated pixels of 219.7 with no seed, and only the five-pixel column survives. The takeaway: Canny's ratio works here only after smoothing.
- Keywords: hysteresis thresholding, connected components, Canny edge detector, smoothing
- Canonical URL: https://canery.in/blogs/canny-line-by-line

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Canny, line by line, by hand
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the article's four steps, and the link
- Technical source: the article's section structure
- Visual structure: lockup and counter; serif title; deck; a tinted panel listing four numbered steps; takeaway; a call to action pointing at the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Canny, line by line, by hand. · Worked on one 5×5 patch. · 1 gradient: cv2.Canny does not smooth · 2 suppression: bins, ties, the norm · 3 hysteresis: chains, not pixels · 4 thresholds: from the noise · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: A numbered list of the article's four steps, gradient, suppression, hysteresis and thresholds, with a pointer to the link sticker.
- Long description: The closing Story frame lists the four steps the article works through: the gradient, where cv2.Canny does no smoothing; suppression, where the direction bins, the tie rule and the norm decide which pixels survive; hysteresis, which grades chains rather than pixels; and the thresholds, set from the noise. It points to the link sticker for the full article on Canery.
- Keywords: Canny edge detector, edge detection, image processing, computer vision
- Canonical URL: https://canery.in/blogs/canny-line-by-line
