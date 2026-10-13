---
social_schema: 2
canonical_url: "https://canery.in/blogs/the-structure-tensor"
---

# Social publishing package — the-structure-tensor

## LinkedIn post

Ask OpenCV's goodFeaturesToTrack for the best feature on a 5×5 patch that holds one clean step edge and one bright pixel, and it returns a single point. It is not the bright pixel, and it is not on the edge.

Worked by hand, the reason is one 2×2 matrix, the structure tensor: a window's sum of gradient outer products.

→ No single pixel can be a corner. One gradient has one direction, and the bright pixel's own gradient is zero. Only a window can vary in two directions.
→ The point it returns, column 2 of row 2, holds the step's horizontal variation and the bright pixel's ring of vertical variation in one 3×3 window. Two unrelated edges, summed, score as a corner.
→ Harris's k is a threshold on the ratio of the two eigenvalues: 1 to 23 at k = 0.04, 1 to 14.6 at 0.06. A pixel on the edge, with a ratio of 0.057, is a corner at one setting and an edge at the other.
→ Lucas–Kanade optical flow solves with the same matrix. At the edge's own window the second eigenvalue is exactly zero, so the equation for vertical motion reads 0 · v = 0: the aperture problem.

Part 9 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

To these detectors a "corner" is any window whose gradients point two ways. That is exactly what a tracker needs, which is why the detectors and Lucas–Kanade share one matrix.

Read the full article on Canery: https://canery.in/blogs/the-structure-tensor

## Instagram caption

The best feature to track is not the bright pixel. Swipe through the structure tensor worked by hand on one 5×5 patch: why no single pixel can be a corner, how one 2×2 matrix counts the directions a window varies in, why goodFeaturesToTrack picks a window that holds two unrelated edges, why Harris's k is a threshold on an eigenvalue ratio, why the aperture problem is a zero eigenvalue, and how one linear Lucas–Kanade step can point backwards.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#computervision #imageprocessing #opticalflow #harriscorner #opencv #python #featuredetection

## Shared feed order

1. `assets/social/feed-01-the-best-feature-is-not-the-bright-pixel.png` — the patch with goodFeaturesToTrack's one returned point beside the bright pixel, not on it
2. `assets/social/feed-02-no-pixel-is-a-corner.png` — each pixel's Sobel gradient: one direction per pixel, zero on the bright pixel
3. `assets/social/feed-03-zero-one-or-two-directions.png` — row r2's window tensors as ellipses, from a line on the step to round ellipses near the pixel
4. `assets/social/feed-04-k-is-a-ratio.png` — Harris's sign as an eigenvalue-ratio threshold, with (r2, c3) between k = 0.04 and k = 0.06
5. `assets/social/feed-05-two-edges-in-one-window.png` — why (2, 2) wins: the step's horizontal variation plus the ring's vertical variation
6. `assets/social/feed-06-the-aperture-problem-is-a-zero-eigenvalue.png` — Lucas–Kanade at the step's window: 0 · v = 0
7. `assets/social/feed-07-one-linear-step-can-point-backwards.png` — one Lucas–Kanade step after a one-pixel move: 1.28 at (2, 2), −0.89 at the bright pixel
8. `assets/social/feed-08-read-the-article.png` — the four readings of the matrix, and the CTA

## Instagram Story

- CTA: Why doesn't OpenCV pick the bright pixel? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/the-structure-tensor

### Story order

1. `assets/social/story-01-the-best-feature-is-not-the-bright-pixel.png` — Overlay: Not the bright pixel. Two edges in one window.
2. `assets/social/story-02-k-is-a-ratio.png` — Overlay: One pixel, two verdicts: k is a ratio.
3. `assets/social/story-03-zero-eigenvalue.png` — Overlay: The aperture problem is a zero.
4. `assets/social/story-04-read-the-article.png` — Overlay: The structure tensor, by hand. Link below.

## Asset metadata

### feed-01-the-best-feature-is-not-the-bright-pixel

- File: `assets/social/feed-01-the-best-feature-is-not-the-bright-pixel.png`
- Title: The best feature is not the bright pixel
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: on the series' patch, goodFeaturesToTrack returns one point, (2, 2), which is neither the bright pixel nor on the step
- Technical source: Why this matters; Worked example, step 4; Figure 3
- Visual structure: lockup and counter; serif title; deck; a panel with the 5×5 patch, the returned pixel outlined in orange and the bright pixel outlined in dashed blue, and the call and its result to the right; two lines on the eigenvalues; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · The best feature is not the bright pixel. · OpenCV's goodFeaturesToTrack on one 5×5 patch: a step of 160 and one pixel of 255. · the patch · grid: every row 40 40 40 200 200, with 255 at row 2, column 1 · goodFeaturesToTrack(p, 10, 0.01, 1) · → one point: x = 2, y = 2 · the bright pixel, x = 1: not returned · the step runs between x = 2 and x = 3 · (2, 2): smaller eigenvalue 462,250, the largest inside the patch; the border's 616,156 is never returned · worked by hand from OpenCV's source; not run · It returns a window whose gradients point two ways: the step's and the pixel's. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: The 5×5 patch with goodFeaturesToTrack's single returned point outlined beside the bright pixel, not on it.
- Long description: The series' 5×5 patch has a step from 40 to 200 between its third and fourth columns and one bright pixel of 255. Worked from OpenCV's source, goodFeaturesToTrack with quality level 0.01 and minimum distance 1 returns exactly one point, x = 2 and y = 2, the dark pixel between the bright pixel and the step. Its window's smaller eigenvalue, 462,250 in raw Sobel units, is the largest inside the patch; the map's overall maximum, 616,156, lies on the border rows, which the function never returns. The takeaway: the detector returns a window whose gradients point two ways, here the step's and the bright pixel's.
- Keywords: goodFeaturesToTrack, Shi-Tomasi, structure tensor, corner detection, OpenCV, feature tracking
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### feed-02-no-pixel-is-a-corner

- File: `assets/social/feed-02-no-pixel-is-a-corner.png`
- Title: No single pixel can be a corner
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: each pixel's gradient has one direction, and the bright pixel's own gradient is zero, so one pixel alone can never vary in two directions
- Technical source: Worked example, step 1; Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with the 5×5 patch and each pixel's gradient arrow, the bright pixel marked 0; notes to the right; one line on the step's value; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · No single pixel can be a corner. · Sobel on the patch, with the border rule cv2.cornerHarris uses. · Sobel gradient, reflect-101 border · arrows: rightward on columns c2 and c3 of every row, downward above the bright pixel, upward below it, none on c4 or on the bright pixel, which shows 0 · each pixel: one gradient, one direction · its outer product has rank 1 at most · the 255 itself: gradient 0, the same zero matrix as a flat pixel · the step reads 640 = 4 × 160 on c2 and c3 · A corner needs a window: a sum of gradients from different directions. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: Gradient arrows on the 5×5 patch: one direction per pixel, rightward across the step, none on the bright pixel itself.
- Long description: The 3×3 Sobel gradient of the patch, with OpenCV's default reflect-101 border, points right across the step on columns c2 and c3, where it reads 640, four times the step's height, and points toward the bright pixel from the rows above and below it. The bright pixel's own gradient is zero, because its opposite neighbours are equal, so on its own it gives the same zero matrix as a flat pixel. Every pixel's outer product of the gradient with itself has rank at most 1. The takeaway: a corner needs a window that sums gradients from different directions.
- Keywords: Sobel gradient, outer product, structure tensor, rank, reflect-101 border, cornerHarris
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### feed-03-zero-one-or-two-directions

- File: `assets/social/feed-03-zero-one-or-two-directions.png`
- Title: Zero, one or two directions
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: summing outer products over a 3×3 window gives a 2×2 tensor whose eigenvalues count the directions the window varies in
- Technical source: Worked example, step 2; Figure 2
- Visual structure: lockup and counter; serif title; deck; a panel with four tensor glyphs in a row for windows (r2, c4), (r2, c3), (r2, c2) and (r2, c1), each with its eigenvalues and rank; two notes; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Zero, one or two directions. · Sum each pixel's outer product over a 3×3 window: a 2×2 matrix, drawn as an ellipse. · row r2: each 3×3 window's tensor · (r2, c4) λ1 2,457,600 λ2 0 rank 1 · (r2, c3) λ1 1,634,150 λ2 92,450 rank 2, barely · (r2, c2) λ1 1,634,150 λ2 462,250 rank 2 · (r2, c1) λ1 832,050 λ2 405,350 rank 2 · c4: the step alone · c1: the bright pixel · semi-axes ∝ √λ, along the eigenvectors · The two eigenvalues count the directions a window varies in. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: Four window tensors as shapes: a flat line on the step, a thin sliver, and two rounder ellipses near the bright pixel.
- Long description: Each 3×3 window on row r2 of the patch sums the outer products of nine Sobel gradients into a 2×2 matrix, drawn as an ellipse with semi-axes proportional to the square roots of its eigenvalues. The window at (r2, c4) holds only the step: eigenvalues 2,457,600 and 0, rank 1, a line. At (r2, c3) two ring pixels add a second eigenvalue of 92,450, a thin sliver. At (r2, c2), the window goodFeaturesToTrack returns, the eigenvalues are 1,634,150 and 462,250; at the bright pixel's window, (r2, c1), 832,050 and 405,350. The takeaway: the two eigenvalues count the directions a window varies in.
- Keywords: structure tensor, eigenvalues, second moment matrix, corner detection, rank
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### feed-04-k-is-a-ratio

- File: `assets/social/feed-04-k-is-a-ratio.png`
- Title: Harris's k is a ratio threshold
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Harris's response changes sign at one eigenvalue ratio set by k, and the step pixel (r2, c3) falls between the ratios for k = 0.04 and k = 0.06
- Technical source: Worked example, step 3; How do Harris, Shi–Tomasi and Förstner score the same two numbers?; Figures 5 and 6; equation (3)
- Visual structure: lockup and counter; serif title; deck; a panel with the response formula, its sign condition, a ratio axis from 0 to 0.08 with the two boundaries and (r2, c3)'s point between them, and two lines with the responses; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Harris's k is a ratio threshold. · R changes sign at one eigenvalue ratio: 1 to 23 at k = 0.04, 1 to 14.6 at 0.06. · R = λ1² [t − k(1 + t)²], t = λ2 / λ1 · R > 0, a corner, exactly when t / (1 + t)² > k · axis 0 to 0.08 · k = 0.04 at 0.0436 · k = 0.06 at 0.0685 · (r2, c3): 0.057 · k = 0.04: R = +31.8 × 10⁹ → corner · k = 0.06: R = −27.8 × 10⁹ → edge · (r2, c3) is a pixel on the step itself · Choose how elongated a corner may be. That choice is k. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: A ratio axis with Harris's boundaries for k = 0.04 and 0.06, and one step pixel's ratio of 0.057 falling between them.
- Long description: Harris's response R = λ1λ2 − k(λ1 + λ2)² can be written as λ1² times t − k(1 + t)², with t the ratio of the smaller eigenvalue to the larger, so its sign depends on the ratio alone: R is positive when t/(1 + t)² exceeds k. The boundary is t = 0.0436, a ratio of 1 to 23, for k = 0.04, and t = 0.0685, 1 to 14.6, for k = 0.06. The window at (r2, c3), on the step itself, has t = 0.057, between the two, so its response is +31.8 × 10⁹ at k = 0.04, a corner, and −27.8 × 10⁹ at k = 0.06, an edge. The takeaway: k is the choice of how elongated a window may be and still count as a corner.
- Keywords: Harris corner detector, Harris k parameter, eigenvalue ratio, corner response, cornerHarris
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### feed-05-two-edges-in-one-window

- File: `assets/social/feed-05-two-edges-in-one-window.png`
- Title: Two edges in one window
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the window at (2, 2) wins because it adds the step's horizontal variation to the bright pixel's ring of vertical variation
- Technical source: Worked example, steps 2 and 4; Figure 3
- Visual structure: lockup and counter; serif title; deck; a panel with a horizontal line plus a vertical line equalling an ellipse, each labelled with its sum; two notes on the bright pixel's own window; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Two edges in one window. · The step varies across x, the pixel's ring across y. Summed, they look like a corner. · why (2, 2) wins · the step's Gx², A = 1,634,150 · + · the pixel's ring, Gy², C = 462,250 · = · (2, 2)'s tensor, λ2 = 462,250 · the bright pixel's own window, (1, 2): λ2 = 405,350 · its ring cuts the step's 640 at c2 to 425, 210, 425 · Detectors find two directions, not geometric corners. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: A horizontal line plus a vertical line equal one ellipse: the step's and the ring's variation summed in window (2, 2).
- Long description: The window centred on (2, 2) covers columns 1 to 3 of rows 1 to 3. Its horizontal variation, A = 1,634,150 in raw Sobel units, comes almost entirely from the step on columns 2 and 3; its vertical variation, C = 462,250, comes entirely from the ring of gradients above and below the bright pixel. Summed, the window has two large eigenvalues and scores as a corner, although it holds no corner, only two unrelated edges at right angles. The bright pixel's own window, (1, 2), scores lower, 405,350, because the ring's negative horizontal gradients cut the step's 640 at column 2 to 425, 210 and 425. The takeaway: detectors find two directions, not geometric corners.
- Keywords: structure tensor, corner detection, Shi-Tomasi, goodFeaturesToTrack, false corner
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### feed-06-the-aperture-problem-is-a-zero-eigenvalue

- File: `assets/social/feed-06-the-aperture-problem-is-a-zero-eigenvalue.png`
- Title: The aperture problem is a zero eigenvalue
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Lucas–Kanade's normal equations use the same matrix, and at the step's window its zero eigenvalue makes the vertical equation read 0 · v = 0
- Technical source: Worked example, step 5; Why is Lucas–Kanade the same matrix?; Figure 9
- Visual structure: lockup and counter; serif title; deck; a panel with the Lucas–Kanade equation, the window's matrix times (u, v), a large 0 · v = 0, and a small (u, v) plot with a vertical line of solutions; two notes; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · The aperture problem is a zero eigenvalue. · Optical flow solves with the same matrix the corner detectors score. · Lucas–Kanade: M d = −Σ g It · at (r2, c4), the step's own window: · matrix rows 2,457,600 0 and 0 0, times u, v · 0 · v = 0 · for any pair of frames · plot: axes u and v, a vertical line at u = 2 labelled every v fits · slide the step down by any amount: nothing in this window changes · An edge's window cannot see motion along the edge. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: The step window's matrix with a zero row, the equation 0 · v = 0, and a vertical line of equally good motions.
- Long description: Lucas–Kanade finds a window's shift by solving M d = −Σ g It, whose matrix is the structure tensor. At the step's own window, (r2, c4), the matrix is diagonal with entries 2,457,600 and 0, because no pixel in the window has a vertical gradient. The second equation therefore reads 0 · v = 0 for every pair of frames: sliding the step down changes nothing in this window, so the vertical component of motion is not in the data. For the patch moved one pixel right, the first equation gives u = 2.00 and every value of v fits equally well. The takeaway: an edge's window cannot see motion along the edge; that is the aperture problem.
- Keywords: aperture problem, Lucas-Kanade, optical flow, normal flow, structure tensor, rank deficiency
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### feed-07-one-linear-step-can-point-backwards

- File: `assets/social/feed-07-one-linear-step-can-point-backwards.png`
- Title: One linear step can point backwards
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one Lucas–Kanade step on the patch moved one pixel right gives 1.28 at (2, 2) and −0.89 at the bright pixel's window, because a one-pixel feature moving one pixel breaks the linear model
- Technical source: Worked example, step 5; When does one Lucas–Kanade step go wrong?; Figure 10
- Visual structure: lockup and counter; serif title; deck; a panel with two windows and their one-step estimates, a rule, the predicted and actual change at column 2, and a two-line note; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · One linear step can point backwards. · Lucas–Kanade, one step, on two windows that both pass a corner test. · the patch moved one pixel right; one step · (2, 2) u = 1.28 right way, 28% long · (1, 2), the bright pixel u = −0.89 the wrong way · at c2 the step's slope predicts −26.25; the bright pixel arrives: +215 · the linear model holds only for motions small against the structure; this one is 1 pixel on 1 · Smooth, iterate, or go coarse to fine: the remedies Lucas and Kanade gave. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: One Lucas–Kanade step after a one-pixel move: 1.28 at window (2, 2), and −0.89, the wrong way, at the bright pixel.
- Long description: With the patch moved one pixel to the right, one Lucas–Kanade step solved on 3×3 windows gives u = 1.28 at (2, 2), the right direction but 28% long, and u = −0.89 at the bright pixel's window, the wrong direction, although both windows score as corners. At column 2 the step's slope, 26.25 grey levels per pixel, predicts that the pixel darkens by 26.25; instead the bright pixel arrives there and it brightens by 215. The linear model holds only when the motion is small compared with the structure, and here a one-pixel feature moved one pixel. The takeaway: smooth, iterate or work coarse to fine, the remedies Lucas and Kanade gave in 1981.
- Keywords: Lucas-Kanade, optical flow, linearisation, brightness constancy, coarse to fine, image pyramid
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: The structure tensor, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four readings of one matrix that the article works through, and where to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel listing four topics, each with a one-line claim and a one-line example from the patch, Lucas–Kanade in orange; takeaway; call to action
- Visible-text transcript: Canery.in · 08 / 08 · The structure tensor, by hand. · Corners, orientation and optical flow from one 2×2 matrix. · eigenvalues: zero, one or two directions; rank 1 on the step, rank 2 at (2, 2) · Harris's k: a threshold on λ2 / λ1; 1 to 23 at 0.04, 1 to 14.6 at 0.06 · Shi–Tomasi: the tracker's own test; goodFeaturesToTrack returns (2, 2) · Lucas–Kanade: the same matrix, solved; a zero eigenvalue is the aperture problem · The full walk-through, every number worked by hand, and the tooling map. · READ IT AT CANERY.IN/BLOGS/THE-STRUCTURE-TENSOR
- Alt text: Summary card: eigenvalues count directions, Harris's k is a ratio, Shi–Tomasi is the tracker's test, Lucas–Kanade solves the same matrix.
- Long description: The closing card lists the article's four readings of the structure tensor. Its eigenvalues count the directions a window varies in: rank 1 on the step, rank 2 at window (2, 2). Harris's k is a threshold on the eigenvalue ratio, 1 to 23 at 0.04 and 1 to 14.6 at 0.06. Shi–Tomasi's smaller-eigenvalue test is the tracker's own criterion, and goodFeaturesToTrack returns (2, 2) on the patch. Lucas–Kanade solves with the same matrix, and a zero eigenvalue is the aperture problem. The call to action points to the full article on canery.in.
- Keywords: structure tensor, Harris corner detector, Shi-Tomasi, Lucas-Kanade, optical flow, image processing
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### story-01-the-best-feature-is-not-the-bright-pixel

- File: `assets/social/story-01-the-best-feature-is-not-the-bright-pixel.png`
- Title: The best feature is not the bright pixel
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: goodFeaturesToTrack returns the window beside the bright pixel, recomposed for a tall frame
- Technical source: Why this matters; Worked example, step 4; Figure 3
- Visual structure: lockup and counter; serif title; deck; the 5×5 patch large, with the returned pixel outlined in orange and the bright pixel in dashed blue; one line below; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · The best feature is not the bright pixel. · One step of 160, one pixel of 255. · goodFeaturesToTrack on the patch · grid: every row 40 40 40 200 200, with 255 at row 2, column 1 · returned: (2, 2), not the bright pixel · Two edges in one window count as a corner. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: A tall view of the 5×5 patch with the returned point outlined next to the bright pixel rather than on it.
- Long description: The series' 5×5 patch, drawn large: a step from 40 to 200 between the third and fourth columns and one bright pixel of 255 in the middle row. goodFeaturesToTrack returns one point, (2, 2), the dark pixel between the bright pixel and the step, outlined in orange; the bright pixel itself, outlined in dashed blue, is not returned. The takeaway: two edges in one window count as a corner.
- Keywords: goodFeaturesToTrack, corner detection, structure tensor, OpenCV
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### story-02-k-is-a-ratio

- File: `assets/social/story-02-k-is-a-ratio.png`
- Title: k = 0.04 says corner, k = 0.06 says edge
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: one step pixel's eigenvalue ratio sits between Harris's sign boundaries for the two common values of k
- Technical source: Worked example, step 3; Figures 5 and 6
- Visual structure: lockup and counter; two-line serif title; deck; a large ratio axis from 0 to 0.08 with the two boundaries and the pixel's ratio between them; two verdict lines; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · k = 0.04 says corner. k = 0.06 says edge. · One pixel on the step, two common settings of Harris's k. · Harris on (r2, c3), a pixel on the step · axis 0 to 0.08 · k = 0.04 at 0.0436 · k = 0.06 at 0.0685 · (r2, c3) 0.057 · k = 0.04: R > 0, a corner · k = 0.06: R < 0, an edge · k is a threshold on the eigenvalue ratio. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: A tall ratio axis: one step pixel at 0.057 lies between Harris's boundaries at 0.0436 and 0.0685.
- Long description: Harris's response changes sign at an eigenvalue ratio set by k: 0.0436 for k = 0.04 and 0.0685 for k = 0.06. The window at (r2, c3), a pixel on the patch's step, has a ratio of 0.057, between the two, so k = 0.04 calls it a corner and k = 0.06 an edge. The takeaway: k is a threshold on the eigenvalue ratio.
- Keywords: Harris corner detector, k parameter, eigenvalue ratio, cornerHarris
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### story-03-zero-eigenvalue

- File: `assets/social/story-03-zero-eigenvalue.png`
- Title: 0 · v = 0
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: at the step's window the Lucas–Kanade matrix has a zero eigenvalue, so the vertical equation is empty
- Technical source: Worked example, step 5; Figure 9
- Visual structure: lockup and counter; serif title; deck; the window's matrix times (u, v); a large 0 · v = 0; two lines; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · 0 · v = 0 · The same matrix the corner detectors score. · Lucas–Kanade at the step's window · matrix rows 2,457,600 0 and 0 0, times u, v · 0 · v = 0 · whatever the frames hold · u is measured, v is not · Any vertical motion fits. That is the aperture problem. · THE STRUCTURE TENSOR · CANERY.IN
- Alt text: The step window's Lucas–Kanade matrix with a zero row, and the equation 0 · v = 0 written large below it.
- Long description: At the step's own window, (r2, c4), the Lucas–Kanade matrix is the structure tensor with entries 2,457,600 and 0: no pixel in the window has a vertical gradient. The equation for vertical motion reads 0 · v = 0 whatever the two frames hold, so the horizontal component u is measured and the vertical component v is not. The takeaway: any vertical motion fits, which is the aperture problem.
- Keywords: aperture problem, Lucas-Kanade, optical flow, structure tensor
- Canonical URL: https://canery.in/blogs/the-structure-tensor

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: The structure tensor, by hand
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the four readings of the matrix, and the link to the article
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel listing four numbered readings, the fourth in bold; takeaway; call to action pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · The structure tensor, by hand. · Worked on one 5×5 patch. · 1 eigenvalues: how many directions · 2 Harris's k: a ratio threshold · 3 Shi–Tomasi: the tracker's test · 4 Lucas–Kanade: the same matrix · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Closing Story frame listing four readings of the structure tensor, with a pointer to the article link sticker.
- Long description: The closing Story frame lists the four readings the article works through: the eigenvalues count how many directions a window varies in; Harris's k is a threshold on their ratio; Shi–Tomasi's test is the tracker's own; Lucas–Kanade solves with the same matrix. The call to action points to the link sticker for the full article on canery.in.
- Keywords: structure tensor, corner detection, optical flow, image processing
- Canonical URL: https://canery.in/blogs/the-structure-tensor
