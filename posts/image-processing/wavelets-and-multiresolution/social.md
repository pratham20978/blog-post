---
social_schema: 2
canonical_url: "https://canery.in/blogs/wavelets-and-multiresolution"
---

# Social publishing package — wavelets-and-multiresolution

## LinkedIn post

The Fourier transform tells you how much of each wave an image holds. A wavelet transform also tells you where.

Worked by hand on one 5×5 patch, a step from 40 to 200 and one bright pixel of 255:

→ The 2-D DFT spreads the bright pixel across all 25 bins at magnitude 215, 4% of its energy each. One Haar wavelet level puts it in four coefficients of 107.5, a quarter each, and the edge in one column of one subband.
→ A Haar level is a prediction error: on the row 40 40 40 200 200 the flat pair costs 0 and the pair across the step costs exactly 160. JPEG 2000's 5/3 wavelet predicts from both neighbours and pays half, 80.
→ Computed by lifting, a level keeps exactly one number per pixel and inverts exactly in integers. On the impulse's row the update rounds 107.5 up to 108, and the inverse subtracts the same 108. That is JPEG 2000's lossless path.
→ The price is shift variance. Move the step one pixel and Haar's level-1 detail drops from 160 to 0. Move the bright pixel to an even column and the 5/3 halves its detail energy.

And the libraries keep their own counts: PyWavelets' default mode returns 36 Haar coefficients for the 25-pixel patch, and 100 for the wavelet JPEG 2000 uses losslessly.

Part 6 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

A wavelet coefficient asks how far a sample is from what its neighbours predict. Smooth regions answer zero; edges answer loudly; one pixel of movement can change the answer.

Read the full article on Canery: https://canery.in/blogs/wavelets-and-multiresolution

## Instagram caption

One bright pixel: 25 numbers in a Fourier spectrum, or 4 in a wavelet transform. Swipe through wavelets worked by hand on one 5×5 patch: a Haar level as a prediction error, the 5/3 that pays half for an edge, integer lifting that returns every pixel exactly, the coefficient budget against the Laplacian pyramid, what a one-pixel shift does, and why soft thresholding takes the same amount off every edge.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#imageprocessing #computervision #wavelets #jpeg2000 #signalprocessing #denoising #python

## Shared feed order

1. `assets/social/feed-01-four-numbers-not-twenty-five.png` — the bright pixel in Fourier (25 bins of 215) against one Haar level (4 coefficients of 107.5)
2. `assets/social/feed-02-a-haar-level-is-a-prediction-error.png` — Haar on row r0: details 0 and 160, coarse 40, 120, 200
3. `assets/social/feed-03-the-5-3-pays-half-for-an-edge.png` — the 5/3 on the same row: details 0 and 80, coarse 40, 60, 240
4. `assets/social/feed-04-integers-in-integers-out.png` — row r2 through the integer 5/3 and back, with the rounded 108, 74, 40
5. `assets/social/feed-05-the-coefficient-budget.png` — coefficients for the 5×5 patch under lifting, PyWavelets and the pyramid
6. `assets/social/feed-06-one-pixel-empties-a-subband.png` — level-1 details for a step and an impulse at two alignments
7. `assets/social/feed-07-soft-thresholding-taxes-every-edge.png` — the patch before and after soft thresholding at λ = 50
8. `assets/social/feed-08-read-the-article.png` — the four parts the article covers, and the CTA

## Instagram Story

- CTA: Why does one pixel of movement empty a wavelet subband? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/wavelets-and-multiresolution

### Story order

1. `assets/social/story-01-four-numbers-not-twenty-five.png` — Overlay: 25 numbers, or 4.
2. `assets/social/story-02-an-edge-costs-its-height.png` — Overlay: Predict, keep the error.
3. `assets/social/story-03-one-pixel-empties-a-subband.png` — Overlay: One pixel, and it's gone.
4. `assets/social/story-04-read-the-article.png` — Overlay: Four things a wavelet level does. Link below.

## Asset metadata

### feed-01-four-numbers-not-twenty-five

- File: `assets/social/feed-01-four-numbers-not-twenty-five.png`
- Title: One bright pixel: 25 numbers, or 4
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Fourier spreads a single pixel over every coefficient; one wavelet level keeps it in one coefficient per subband
- Technical source: One level in 2-D ("What does one level do to an image?"), Figure 4; Part 5's floor of 215
- Visual structure: lockup and counter; serif title; deck; a panel with a 5×5 grid of 215s on the left and four 3×3 subbands on the right, each with one 107.5 outlined in the accent and zeros elsewhere; captions under each side; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · One bright pixel: 25 numbers, or 4. · The series' 5×5 patch has one pixel of 255 among 40s. Fourier spreads it everywhere; a wavelet does not. · THE PIXEL IN FOURIER · 25 BINS OF 215 · grid: 215 in all 25 cells · each bin: 4% of the pixel's energy · IN ONE HAAR LEVEL · 4 COEFFICIENTS · LL, HL, LH, HH: 107.5 at the middle-left cell of each, 0 elsewhere · each: 25% of its energy · A wavelet coefficient knows where it is: the pixel lands in one coefficient per subband. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: A 5×5 grid of 215s beside four 3×3 subbands that each hold one 107.5 and zeros, contrasting Fourier with one Haar level.
- Long description: The series' 5×5 patch has one bright pixel of 255 among 40s, an impulse of 215 above its neighbours. Its contribution to the 2-D discrete Fourier transform is magnitude 215 in all 25 bins, so each bin holds 4% of its energy. One orthonormal Haar wavelet level puts the same impulse into four coefficients, one in each of the subbands LL, HL, LH and HH, each of magnitude 107.5; four times 107.5 squared equals 215 squared, so each holds a quarter of the energy. The takeaway: a wavelet coefficient is local, so the pixel stays in one place per subband instead of spreading everywhere.
- Keywords: wavelet transform, Haar wavelet, subbands, discrete Fourier transform, impulse, energy compaction, image processing
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### feed-02-a-haar-level-is-a-prediction-error

- File: `assets/social/feed-02-a-haar-level-is-a-prediction-error.png`
- Title: A Haar level is a prediction error
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Haar predicts each odd sample from its left neighbour; the detail is the error and the coarse value the pair's average
- Technical source: Worked example, "One Haar level, by lifting", Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with the row r0 as five shaded cells, two detail cells aligned with the pairs (c0, c1) and (c2, c3), the 160 outlined in the accent, then three coarse cells aligned with the pairs and c4; notes beside and below; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · A Haar level is a prediction error. · Predict each odd sample from its left neighbour, keep the error, then average the pair. · ROW R0 OF THE PATCH · 40 40 40 200 200 · DETAIL · ODD SAMPLE − ITS LEFT NEIGHBOUR · 0 160 · pair across the step: 160 · COARSE · EACH PAIR'S AVERAGE · 40 120 200 · c4 has no partner: it passes through · Smooth data costs nothing; an edge inside a pair costs its height. Five samples in, five numbers out. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: The row 40 40 40 200 200 with Haar details 0 and 160 under its pairs and coarse values 40, 120 and 200.
- Long description: One Haar level computed by lifting on the top row of the patch, 40 40 40 200 200. Each odd sample is predicted by its left neighbour: the pair c0, c1 gives a detail of 0 and the pair c2, c3, which straddles the step, gives 160, exactly the step's height. Each even sample is then updated by half its detail, so the coarse values are the pair averages 40 and 120, and c4, which has no partner, passes through as 200. Five samples become five numbers. The takeaway: smooth data costs nothing, and an edge that falls inside a pair costs its full height.
- Keywords: Haar wavelet, lifting scheme, predict and update, detail coefficient, approximation coefficient, image processing
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### feed-03-the-5-3-pays-half-for-an-edge

- File: `assets/social/feed-03-the-5-3-pays-half-for-an-edge.png`
- Title: The 5/3 pays half for an edge
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: JPEG 2000's reversible 5/3 predicts from both neighbours, so a step costs half its height and its coarse row overshoots
- Technical source: Worked example, "The same row through the 5/3", Figure 1; ledger L08–L11
- Visual structure: lockup and counter; serif title; deck; a panel with the row r0, the 5/3 details 0 and 80 with 80 outlined in the accent, the coarse values 40, 60, 240, and the arithmetic for 240 underneath; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · The 5/3 pays half for an edge. · JPEG 2000's reversible wavelet predicts from both neighbours, so a straight line costs nothing. · THE SAME ROW THROUGH THE 5/3 · 40 40 40 200 200 · DETAIL · ODD − ⌊(LEFT + RIGHT) / 2⌋ · 0 80 · the step costs half: 80 · COARSE · EVEN + ⌊(DL + DR + 2) / 4⌋ · 40 60 240 · 240 = (−40 + 400 + 1200 + 400 − 40) / 8 · Its coarse row is no block average: the low-pass overshoots to 240 beside the mirrored step. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: The row 40 40 40 200 200 through JPEG 2000's 5/3: details 0 and 80, coarse values 40, 60 and 240.
- Long description: The same row, 40 40 40 200 200, through one level of JPEG 2000's reversible 5/3 wavelet. Each odd sample is predicted by the rounded-down mean of its two neighbours, so the details are 0 and 200 − 120 = 80: half the step. Each even sample is updated by the rounded quarter of its neighbouring details plus a rounding offset, with the row mirrored about its end samples, giving coarse values 40, 60 and 240. The 240 is the 5/3 low-pass filter (−1, 2, 6, 2, −1)/8 applied to the mirrored neighbourhood 40, 200, 200, 200, 40. The takeaway: predicting from both neighbours halves an edge's cost and makes a straight line cost nothing, and the coarse row is not a block average.
- Keywords: LeGall 5/3 wavelet, JPEG 2000, lifting scheme, symmetric extension, low-pass filter, image compression
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### feed-04-integers-in-integers-out

- File: `assets/social/feed-04-integers-in-integers-out.png`
- Title: Integers in, integers out
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: rounding inside each lifting step keeps the transform exactly invertible in integers
- Technical source: "Lifting: how JPEG 2000 gets integers back exactly", "Rounding inside the steps", Figure 7; ledger L12, L22
- Visual structure: lockup and counter; serif title; deck; a panel with row r2, the three rounded update amounts in the accent, the coarse and detail values side by side, the exact values for comparison, and the restored row with the 255 outlined; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Integers in, integers out. · Lifting rounds inside each step; the inverse recomputes the same rounded numbers. · ROW R2 · FORWARD, ROUNDING INSIDE THE STEPS · 40 255 40 200 200 · update: ⌊432/4⌋ = 108 · ⌊297/4⌋ = 74 · ⌊162/4⌋ = 40 · COARSE · 148 114 240 · DETAIL · 215 80 · exact arithmetic: 147.5, 113.75, 240 · INVERSE · SUBTRACT THE SAME 108, 74, 40 · 40 255 40 200 200 · That is how JPEG 2000 codes losslessly with its 5/3 wavelet. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: Row 40 255 40 200 200 through the integer 5/3: coarse 148, 114, 240 and detail 215, 80, then back exactly.
- Long description: Row r2 of the patch, 40 255 40 200 200, through one level of the integer 5/3 lifting transform. The details are 215 and 80. The update adds rounded quarters of the neighbouring details: floor of 432/4 is 108, floor of 297/4 is 74 and floor of 162/4 is 40, giving coarse values 148, 114 and 240 where exact arithmetic would give 147.5, 113.75 and 240. The inverse subtracts the same rounded 108, 74 and 40, then adds back the predictions, and returns 40 255 40 200 200 exactly. The takeaway: rounding inside each step keeps the transform invertible in integers, which is JPEG 2000's lossless path.
- Keywords: integer wavelet transform, lifting scheme, reversible transform, lossless compression, JPEG 2000, 5/3 wavelet
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### feed-05-the-coefficient-budget

- File: `assets/social/feed-05-the-coefficient-budget.png`
- Title: N pixels, N coefficients
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: lifting keeps exactly one number per pixel; library padding and the Laplacian pyramid keep more
- Technical source: Worked example, "The coefficient budget", Figure 2; ledger L05, L13, L14
- Visual structure: lockup and counter; serif title; deck; a panel of five horizontal bars on one scale with counts at their ends, then three lines of large-frame percentages; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · N pixels, N coefficients. · Lifting keeps exactly one number per pixel. Library padding and the pyramid keep more. · COEFFICIENTS FOR THE 5×5 PATCH (25 PIXELS) · lifting (JPEG 2000) 25 · PyWavelets haar 36 · PyWavelets bior2.2 100 · PyWavelets bior4.4 196 · Laplacian pyramid 39 · 1920×1080, five levels: haar +0.01% · bior2.2 +1.2% · bior4.4 +2.3% · Laplacian pyramid +33% (4/3) · the patch's pyramid: 39 for 25, +56% · The padding fades on large images; the pyramid's extra third never does. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: Bars of coefficients kept for the 25-pixel patch: lifting 25, PyWavelets haar 36, bior2.2 100, bior4.4 196, pyramid 39.
- Long description: How many coefficients each representation keeps for the series' 5×5 patch of 25 pixels. Lifting, as JPEG 2000 does it, keeps exactly 25. PyWavelets in its default symmetric mode pads each band to floor((N + L − 1)/2) coefficients for a filter of length L, so it returns 36 for Haar, 100 for bior2.2 (the 5/3) and 196 for bior4.4 (the 9/7). The Laplacian pyramid down to one pixel keeps 25 + 9 + 4 + 1 = 39. On a 1920×1080 frame at five levels the padding shrinks to 0.01%, 1.2% and 2.3% over the pixel count, while the pyramid stays a third over, the 4/3 of two-dimensional pyramids. The takeaway: a wavelet level is critically sampled, and the overhead that remains comes from padding or from redundancy.
- Keywords: critically sampled, wavelet coefficients, PyWavelets, signal extension mode, Laplacian pyramid, redundancy
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### feed-06-one-pixel-empties-a-subband

- File: `assets/social/feed-06-one-pixel-empties-a-subband.png`
- Title: Move the edge one pixel
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: decimated wavelets are shift-variant, and Haar and the 5/3 fail on different features
- Technical source: "What does the decimated transform get wrong?", Figure 8; ledger L43, L44
- Visual structure: lockup and counter; serif title; deck; a panel of four labelled rows, each a five-sample row with its Haar and 5/3 level-1 details beside it; the Haar zeros for the moved step and the 5/3 split impulse outlined in the accent; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Move the edge one pixel. · Decimated wavelets are not shift-invariant, and each filter fails on a different feature. · HAAR D · 5/3 D · STEP AT C2 | C3 · 40 40 40 200 200 · 0 160 · 0 80 · STEP ONE PIXEL LEFT · 40 40 200 200 200 · 0 0 · −80 0 · IMPULSE AT ODD C1 · 40 255 40 40 40 · 215 0 · 215 0 · IMPULSE AT EVEN C2 · 40 40 255 40 40 · 0 −215 · −107.5 −107.5 · Haar loses the step at level 1; the 5/3 keeps it but halves the impulse's detail energy. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: Four rows of the patch with Haar and 5/3 details: a moved step gives Haar zeros; a moved impulse splits the 5/3.
- Long description: Level-1 details of Haar and of the 5/3 for four rows. With the step between c2 and c3, Haar gives 0, 160 and the 5/3 gives 0, 80. Moved one pixel left, the step falls between Haar's pairs and both Haar details are 0, while the 5/3 gives −80, 0. An impulse of 255 on a row of 40s at the odd column c1 gives one detail of 215 in both. Moved to the even column c2, Haar gives −215 with the same energy, but the 5/3 gives two details of −107.5, half the detail energy. The takeaway: the decimated transform is not shift-invariant, and each filter fails on a different feature.
- Keywords: shift variance, decimated wavelet transform, aliasing, Haar wavelet, 5/3 wavelet, translation invariance
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### feed-07-soft-thresholding-taxes-every-edge

- File: `assets/social/feed-07-soft-thresholding-taxes-every-edge.png`
- Title: Soft thresholding taxes every edge
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: soft thresholding subtracts λ from every surviving coefficient, so real edges lose contrast
- Technical source: "Denoising by shrinking coefficients", "What the rules do to the patch", Figure 10; ledger L47, L48
- Visual structure: lockup and counter; serif title; deck; a panel with the patch and the soft-thresholded patch side by side as 5×5 value grids, the impulse cell outlined in each, then three lines of notes; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Soft thresholding taxes every edge. · Noise stays σ in every orthonormal coefficient; the image gathers in a few large ones. · THE PATCH · rows 40 40 40 200 200, r2 40 255 40 200 200 · SOFT THRESHOLD, λ = 50 · rows 40 40 65 175 200, r2 65 180 65 175 200, r3 65 65 65 175 200 · edge across c2 | c3: 160 → 110 in every row · impulse 255 → 180; hard thresholding: unchanged · λ = σ√(2 ln N) = 4.995σ at 512×512: 50 for σ = 10 · Soft takes λ off every survivor; hard keeps it whole or kills it. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: The patch before and after soft thresholding at λ = 50: the edge pair becomes 65, 175 and the 255 becomes 180.
- Long description: The noise-free patch and the same patch after one orthonormal Haar level, soft thresholding of the detail coefficients at λ = 50, and the inverse. Soft thresholding subtracts 50 from every surviving coefficient: the step's −160 becomes −110, so the pair across the edge reconstructs as 65, 175 in every row, and the impulse's three details shrink from 107.5 to 57.5, so the 255 becomes 180 and three neighbours rise from 40 to 65. Hard thresholding at the same λ changes nothing, because every detail of the patch is at least 107.5. The threshold 50 is the universal threshold σ√(2 ln N) for σ = 10 on a 512×512 image, 4.995σ. The takeaway: soft thresholding biases real edges by λ; hard thresholding keeps them whole.
- Keywords: wavelet denoising, soft thresholding, hard thresholding, universal threshold, VisuShrink, image processing
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Wavelets and multiresolution, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four parts of the article and where to read it
- Technical source: the article's structure; Figures 1, 2, 7 and 8
- Visual structure: lockup and counter; serif title; deck; a panel listing four headed items with a line and a value under each, "lifting" in the accent; takeaway; CTA footer in the accent
- Visible-text transcript: Canery.in · 08 / 08 · Wavelets and multiresolution, by hand. · Haar, lifting, JPEG 2000 and denoising, all on one 5×5 patch. · one level by hand · Haar and the 5/3 on one row · an edge costs 160, or 80 · the budget · N numbers, not 4/3 N · PyWavelets pads: 25 → 36 or 100 · lifting · integers in, integers out · JPEG 2000's lossless path · the price · shift variance, thresholds · one pixel empties a subband · The full walk-through, with the tooling map for PyWavelets, scikit-image and Pillow. · READ IT AT CANERY.IN/BLOGS/WAVELETS-AND-MULTIRESOLUTION
- Alt text: A summary card listing one level by hand, the budget, lifting and the price, with the article's address.
- Long description: The closing card lists what the article covers. One level by hand: Haar and the 5/3 on one row, where an edge costs 160 or 80. The budget: N numbers rather than the pyramid's 4/3 N, and PyWavelets' padding from 25 to 36 or 100. Lifting: integers in, integers out, JPEG 2000's lossless path. The price: shift variance and thresholds, where one pixel of movement empties a subband. It points to the full article, which includes a tooling map for PyWavelets, scikit-image and Pillow, at canery.in/blogs/wavelets-and-multiresolution.
- Keywords: wavelets, multiresolution, JPEG 2000, lifting scheme, image processing, Canery
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### story-01-four-numbers-not-twenty-five

- File: `assets/social/story-01-four-numbers-not-twenty-five.png`
- Title: One bright pixel: 25 numbers, or 4
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: Fourier spreads a single pixel over every coefficient; one wavelet level keeps it in one per subband
- Technical source: One level in 2-D, Figure 4; Part 5's floor of 215
- Visual structure: lockup and counter; serif title; deck; a 5×5 grid of 215s on the left and four 3×3 subbands on the right, one 107.5 outlined in each; one caption under each side at the same height; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · One bright pixel: 25 numbers, or 4. · The series' 5×5 patch, one wavelet level, by hand. · THE PIXEL IN FOURIER · 215 × 25 · grid: 215 in all 25 cells · HAAR · 4 COEFFICIENTS · LL, HL, LH, HH: 107.5 at the middle-left cell of each, 0 elsewhere · 4% each, everywhere · 25% each, one place · A wavelet coefficient knows where it is. Fourier spreads the pixel everywhere. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: A grid of 25 cells reading 215 beside four small subbands that each hold one 107.5, the rest zeros.
- Long description: The patch's single bright pixel, an impulse of 215, appears in all 25 bins of its Fourier transform at magnitude 215, 4% of its energy each. One orthonormal Haar level puts it in four coefficients of 107.5, one per subband, a quarter of its energy each. The takeaway: wavelet coefficients are local; Fourier coefficients are not.
- Keywords: wavelet transform, Haar wavelet, Fourier transform, subbands, energy compaction
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### story-02-an-edge-costs-its-height

- File: `assets/social/story-02-an-edge-costs-its-height.png`
- Title: An edge costs its height, or half
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Haar pays the whole step as its detail; the 5/3 pays half
- Technical source: Worked example, Figure 1
- Visual structure: lockup and counter; serif title; deck; the row r0 as five cells, then the Haar details and the 5/3 details aligned with the pairs, the nonzero detail outlined in each, with a short note to the right; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · An edge costs its height, or half. · Predict each odd sample; keep only the error. · ROW R0 · 40 40 40 200 200 · HAAR DETAIL · 0 160 · whole step · 5/3 DETAIL · 0 80 · half step · Smooth data costs nothing. Five samples in, five numbers out. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: The row 40 40 40 200 200 with Haar details 0, 160 and 5/3 details 0, 80 under it.
- Long description: The top row of the patch, 40 40 40 200 200, has a step of 160 inside the pair c2, c3. Haar predicts each odd sample from its left neighbour and records the whole step, details 0 and 160. The 5/3 predicts from both neighbours and records half, details 0 and 80. The takeaway: smooth data costs nothing, and a level keeps five numbers for five samples.
- Keywords: Haar wavelet, 5/3 wavelet, lifting scheme, detail coefficient, prediction error
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### story-03-one-pixel-empties-a-subband

- File: `assets/social/story-03-one-pixel-empties-a-subband.png`
- Title: Move the edge one pixel
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: a one-pixel shift moves the step between Haar's pairs and empties the level-1 details
- Technical source: "What does the decimated transform get wrong?", Figure 8
- Visual structure: lockup and counter; serif title; deck; two blocks, each a five-sample row with its two Haar details aligned to the pairs underneath; the second block's zeros outlined in the accent; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Move the edge one pixel. · Decimated wavelets are not shift-invariant. · HAAR · STEP INSIDE A PAIR · 40 40 40 200 200 · 0 160 · HAAR · STEP ONE PIXEL LEFT · 40 40 200 200 200 · 0 0 · The level-1 detail drops from 160 to 0. The step reappears a level down. · WAVELETS AND MULTIRESOLUTION · CANERY.IN
- Alt text: Two rows: with the step inside a pair Haar gives 0, 160; moved one pixel left it gives 0, 0.
- Long description: Haar's level-1 details depend on where an edge falls relative to its pairs. With the step between c2 and c3, inside the pair c2, c3, the details are 0 and 160. Moved one pixel left, to 40 40 200 200 200, the step falls between the pairs and both details are 0; it reappears only at the next level, where the coarse values 40 and 200 meet. The takeaway: decimated wavelet transforms are not shift-invariant.
- Keywords: shift variance, Haar wavelet, decimation, translation invariance, wavelet transform
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Four things a wavelet level does
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the four takeaways and the link
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel with four numbered lines, the second in bold; takeaway; CTA footer in the accent
- Visible-text transcript: Canery.in · 04 / 04 · Four things a wavelet level does. · Worked by hand on one 5×5 patch. · 1 a coefficient: local, at one scale · 2 lifting: N numbers, exact integers · 3 JPEG 2000: the 5/3 and the 9/7 · 4 the price: shift variance · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: A numbered list of four takeaways about wavelets, with a prompt to use the link sticker.
- Long description: The closing Story frame lists four takeaways: a wavelet coefficient is local, at one scale; lifting keeps N numbers and exact integers; JPEG 2000 uses the 5/3 and the 9/7; and the price is shift variance. It points the viewer to the link sticker for the full article.
- Keywords: wavelets, lifting scheme, JPEG 2000, shift variance, Canery
- Canonical URL: https://canery.in/blogs/wavelets-and-multiresolution
