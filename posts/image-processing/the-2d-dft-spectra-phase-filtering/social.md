---
social_schema: 2
canonical_url: "https://canery.in/blogs/the-2d-dft-spectra-phase-filtering"
---

# Social publishing package — the-2d-dft-spectra-phase-filtering

## LinkedIn post

A 2-D spectrum tells you how much of each wave an image holds and which way it runs. It does not tell you where anything is. That lives in the phase.

Worked by hand on one 5×5 patch, a vertical edge and one bright pixel:

→ The edge prints a horizontal line of energy through the centre of the spectrum: 1,079 and 709 on either side of the DC term's 2,815.
→ The bright pixel prints a flat floor: magnitude 215 in every other bin, wherever the pixel sits. Its position is the slope of the phase, −72° per step one way and −144° the other.
→ Rebuild the patch from the phase alone and the pixel stays where it was. Rebuild it from the magnitude alone and everything moves to the corner.
→ Swap magnitude and phase between the patch and its transpose, and neither image wins: positions follow the phase, but the dominant bar runs the way the magnitude donor's edge runs.

When is filtering in that domain worth it? When the thing to remove is a few coefficients: periodic interference that completes whole cycles across the frame lands on two bins, and a notch removes it exactly. When it doesn't fit, a wide notch can do more damage than the interference. And when the kernel is big enough: the FFT round trip costs about 170 operations per pixel on a 1920×1080 frame whatever the kernel, so a full kernel crosses it near 10×10 by count. OpenCV's own code switches at a kernel area of 130.

Part 5 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

Magnitude says how much and which way; phase says where. The cross in your spectrum is usually the image border, not the image.

Read the full article on Canery: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

## Instagram caption

A spectrum says how much. Phase says where. Swipe through the 2-D DFT worked by hand on one 5×5 patch: the edge that prints a line and the bright pixel that prints a flat floor of 215, the phase ramp that holds its position, what survives when you keep only the phase, the swap where neither image wins, the tile the DFT thinks your image is, the notch that is exact only on-bin, and the fixed toll of the FFT round trip.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#imageprocessing #computervision #fourier #fft #signalprocessing #opencv #python

## Shared feed order

1. `assets/social/feed-01-a-spectrum-says-how-much.png` — the patch's centred spectrum: DC, the edge's bright row, and the bright pixel's flat floor
2. `assets/social/feed-02-position-is-a-phase-ramp.png` — the bright pixel's position is the slope of its phase
3. `assets/social/feed-03-keep-the-phase-keep-the-layout.png` — phase-only and magnitude-only rebuilds of the patch, side by side
4. `assets/social/feed-04-neither-image-wins.png` — the swap with the transpose: positions from phase, orientation from magnitude
5. `assets/social/feed-05-the-dft-sees-a-tile.png` — the DFT treats the image as a tile and invents an edge at the border
6. `assets/social/feed-06-a-notch-is-exact-only-on-bin.png` — on-bin interference is removed exactly; off-bin, every notch is a trade
7. `assets/social/feed-07-the-fft-is-a-fixed-toll.png` — operations per pixel for direct and FFT convolution, and where each library switches
8. `assets/social/feed-08-read-the-article.png` — the four readings the article covers, and the CTA

## Instagram Story

- CTA: Why does keeping only the phase keep the picture? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### Story order

1. `assets/social/story-01-a-spectrum-says-how-much.png` — Overlay: How much, and where.
2. `assets/social/story-02-keep-the-phase-keep-the-layout.png` — Overlay: The phase keeps the layout.
3. `assets/social/story-03-a-notch-is-exact-only-on-bin.png` — Overlay: Exact only on-bin.
4. `assets/social/story-04-read-the-article.png` — Overlay: Four readings of every spectrum. Link below.

## Asset metadata

### feed-01-a-spectrum-says-how-much

- File: `assets/social/feed-01-a-spectrum-says-how-much.png`
- Title: A spectrum says how much, phase says where
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: the patch's centred magnitude spectrum shows which waves are present, not where anything is
- Technical source: Worked example, "The spectrum, centred", Figure 2
- Visual structure: lockup and counter; serif title; deck; a panel with the centred 5×5 magnitude spectrum, log-shaded, the DC cell outlined in the accent and the middle row outlined dashed, beside three labelled values; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · A spectrum says how much. Phase says where. · The series' 5×5 patch, transformed by hand: one vertical edge, one bright pixel, 25 coefficients. · grid: 215 in the twenty cells off the middle row; middle row 709.4, 1079.4, 2815, 1079.4, 709.4 · |F(kr, kc)| centred · kc across, kr down · 2,815 · DC: the pixel sum · 1,079 · 709 · the edge's row · 215 · every other bin: the bright pixel · The edge prints a horizontal line; the pixel prints a flat floor. Where anything sits is in the phase, not here. · The 2-D DFT · canery.in
- Alt text: A centred 5×5 magnitude spectrum: 2,815 at the centre, 1,079 and 709 along the middle row, and 215 in every other cell.
- Long description: The magnitude spectrum of the series' 5×5 patch is drawn centred, with the zero-frequency (DC) term in the middle and log shading in which brighter means larger. DC is 2,815, the sum of the pixels. The middle row, the waves that vary across the columns and are constant down them, reads 709.4, 1,079.4, 2,815, 1,079.4, 709.4: the patch's vertical edge prints a horizontal line of energy. Every other cell reads exactly 215: the patch's single bright pixel contributes every wave in equal amount. The takeaway: the magnitudes record which waves are present, and the position of the edge and of the pixel is held in the phase.
- Keywords: 2-D DFT, Fourier spectrum, magnitude spectrum, fftshift, image processing, frequency domain
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### feed-02-position-is-a-phase-ramp

- File: `assets/social/feed-02-position-is-a-phase-ramp.png`
- Title: One bright pixel is every wave at once
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the bright pixel's magnitude is the same in every bin, and its position is the slope of its phase
- Technical source: Intuition, Figure 6; The math, equation (3)
- Visual structure: lockup and counter; serif title; deck; a panel with five phase arrows for the floor bins along kc at kr = 1, their angles beneath, two accent lines giving the slopes and their meaning, and two mono lines with the general rule; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · One bright pixel is every wave at once. · Its magnitude is 215 in every bin. Its position is the slope of the phase, read straight off the arrows. · The floor's phase along kc, at kr = 1 · −144° kc 0 · 144° kc 1 · 72° kc 2 · 0° kc 3 · −72° kc 4 · −72° per step along kc → column 1 · −144° per step along kr → row 2 · every floor bin: 215 at angle −72°·(2kr + kc) · shift one column right: each turns −72°·kc · Moving an image changes no magnitude at all. Every arrow turns in proportion to its frequency. · The 2-D DFT · canery.in
- Alt text: Five phase arrows at −144°, 144°, 72°, 0° and −72°, each turning −72° per step, with the slopes giving the pixel's row and column.
- Long description: The bright pixel at row 2, column 1 of the patch contributes 215 to every bin of the spectrum, at the angle −72° × (2kr + kc). Along the row kr = 1 the five floor bins sit at −144°, 144°, 72°, 0° and −72°, so each step in kc turns the arrow by −72°, which is one fifth of a turn per column: column 1. Each step in kr turns it by −144°: row 2. Shifting the patch one column to the right changes no magnitude and turns every arrow by a further −72° times its column frequency.
- Keywords: Fourier phase, shift theorem, phase ramp, 2-D DFT, image position, frequency domain
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### feed-03-keep-the-phase-keep-the-layout

- File: `assets/social/feed-03-keep-the-phase-keep-the-layout.png`
- Title: Keep the phase, keep the layout
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: an image rebuilt from phase alone keeps its layout; rebuilt from magnitude alone, it does not
- Technical source: Worked example, "Keep the phase, or keep the magnitude", Figure 3
- Visual structure: lockup and counter; serif title; deck; a panel with two shaded 5×5 grids side by side, the phase-only rebuild (values × 100) with the impulse outlined at (2, 1) and the magnitude-only rebuild with the impulse outlined at (0, 0), each with a two-line note; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Keep the phase, keep the layout. · Rebuild the patch from phase alone, with every magnitude set to 1, then from magnitude alone, with phase set to 0. · Phase only, × 100 · every row −5, −16, −5, 13, 13, except row 2: −5, 84, −5, 13, 13 · Magnitude only · row 0: 428, 93, 60, 60, 93; rows 1–4: 213, 93, 60, 60, 93 · impulse stays at (2, 1) · dark left, bright right · impulse moves to (0, 0) · the step becomes a hump · Phase holds where things are. Magnitude alone moves everything to the origin. · The 2-D DFT · canery.in
- Alt text: Two 5×5 rebuilds of the patch: phase only keeps the bright pixel at row 2, column 1; magnitude only moves it to the corner.
- Long description: The patch's spectrum is inverted twice. With every magnitude set to 1 and the phase kept, the result, shown times 100, is a unit impulse at row 2, column 1 (84 there) on rows that read −5, −16, −5, 13, 13: dark on the left, bright on the right, the edge between columns 2 and 3 in place. With every phase set to zero and the magnitude kept, the result is symmetric about column 0: rows of 213, 93, 60, 60, 93 and 428 at the corner, so the edge has become a hump and the bright pixel has moved to the origin. Phase holds where things are.
- Keywords: phase-only reconstruction, Fourier magnitude, importance of phase, 2-D DFT, image reconstruction
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### feed-04-neither-image-wins

- File: `assets/social/feed-04-neither-image-wins.png`
- Title: Swap the halves and neither image wins
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: magnitude from the patch with phase from its transpose gives positions from the phase donor and orientation from the magnitude donor
- Technical source: Worked example, "Swapping phase between two images", Figure 4
- Visual structure: lockup and counter; serif title; deck; a panel with the shaded 5×5 swap result, the bright pixel outlined at (1, 2) and the column-2 bar outlined dashed, beside three labelled findings; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Swap the halves and neither image wins. · Magnitude from the patch, phase from the patch turned on its side. The result belongs to neither. · |A| with the phase of B = Aᵀ · rows: 50 83 202 83 50 · 26 59 393 59 26 · 50 83 202 83 50 · 88 121 241 121 88 · 88 121 241 121 88 · 393 at (1, 2) · B's impulse, from B's phase · rows 3–4 brighter · B's step, from B's phase · a vertical bar · A's edge runs that way: from A's magnitude · Phase decided where; magnitude decided which way. Photographs share a roughly 1/f magnitude, so there phase wins. · The 2-D DFT · canery.in
- Alt text: The swap of the patch's magnitude with its transpose's phase: a vertical bar down column 2 and the bright pixel at row 1, column 2.
- Long description: Image A is the patch, with a vertical edge and its bright pixel at row 2, column 1; image B is its transpose, with a horizontal edge and the pixel at row 1, column 2. Inverting A's magnitudes with B's phases gives rows of 50, 83, 202, 83, 50; 26, 59, 393, 59, 26; 50, 83, 202, 83, 50; then 88, 121, 241, 121, 88 twice. B's pixel is back at full strength at (1, 2) and rows 3 and 4 are brighter, where B's step is: positions came from B's phase. But the strongest structure is a vertical bar down column 2, the way A's edge runs: orientation came from A's magnitude. Photographs share a roughly 1/f magnitude, so for them the swap looks like the phase donor.
- Keywords: phase swap, Oppenheim and Lim, Fourier magnitude, Fourier phase, 2-D DFT, image structure
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### feed-05-the-dft-sees-a-tile

- File: `assets/social/feed-05-the-dft-sees-a-tile.png`
- Title: Your DFT thinks the image is a tile
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the DFT treats the image as periodic, so mismatched borders become an edge that prints a cross in the spectrum
- Technical source: How do you read a 2-D spectrum?, "The cross the DFT invents", Figure 8 (L13, L14, L15)
- Visual structure: lockup and counter; serif title; deck; a panel with row r0 tiled as nine pixel cells, the patch's five outlined and the two tile borders in the accent, a note on the invented step, two mono lines on the cross, and a line of fixes; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Your DFT thinks the image is a tile. · Across the right border, the 200 of the last column runs straight into the next tile's 40. · Row r0, as the DFT sees it: tiled · 200 200 40 40 40 200 200 40 40 · the patch's row · 200 → 40 at every tile border: a step of −160 the patch does not contain · left ≠ right → a line through DC · top ≠ bottom → another: the cross · fixes: taper · mirror · periodic + smooth · Before you read a spectrum, taper, mirror or split. Zero padding to a fast size adds a jump of its own. · The 2-D DFT · canery.in
- Alt text: Row r0 of the patch tiled, with the 200-to-40 jump at each tile border marked as an edge the DFT invents.
- Long description: The DFT computes the spectrum of the image as one tile of a periodic plane. Tiled, row r0 of the patch reads 200, 200 | 40, 40, 40, 200, 200 | 40, 40: at every tile border the last column's 200 runs into the next tile's 40, a step of −160 that the patch does not contain. On a photograph, mismatched left and right borders put a line through the spectrum's centre along one axis and mismatched top and bottom borders a line along the other: the cross. Tapering with a window, mirroring the image, or splitting it into periodic and smooth parts removes it; padding with zeros to a fast size adds a new jump.
- Keywords: spectral cross artefact, periodic boundary, windowing, periodic plus smooth decomposition, DFT, image processing
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### feed-06-a-notch-is-exact-only-on-bin

- File: `assets/social/feed-06-a-notch-is-exact-only-on-bin.png`
- Title: A notch is exact only on-bin
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: interference that completes whole cycles fills two empty bins and a notch removes it exactly; off-bin, every notch trades interference for image
- Technical source: Worked example, "One periodic artefact, removed with a notch"; When does a notch work?, Figure 10
- Visual structure: lockup and counter; serif title; deck; a panel with the on-bin result as three lines, a rule, then four horizontal bars of rms error for the off-bin case with their values; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · A notch is exact only on-bin. · Bands that fit the frame land on two empty bins. Bands that don't leak into the image's own. · 3 cycles in 10 rows · two bins, (±3, 0), both empty in the tile · two-bin notch: error 3 × 10⁻¹², exact · 2.5 cycles in 10 rows: every bin · rms error, grey levels · bands at 2.5 cycles · no filter 14.1 · notch ±3 only 10.8 · notch ±2 and ±3 13.4 · notch eight bins 17.4 · A notch's width is a bet on what the image doesn't contain. Crop to whole cycles: at 20 rows it's exact again. · The 2-D DFT · canery.in
- Alt text: Notch results on the tiled patch: exact for bands at 3 cycles; at 2.5 cycles the rms error is 10.8, 13.4 or 17.4 against 14.1 unfiltered.
- Long description: The patch tiled to 10×10 is corrupted by horizontal bands. When the bands complete 3 cycles down the 10 rows they occupy exactly two bins, (±3, 0), where the tile has nothing, and zeroing those two bins restores the tile to 3 × 10⁻¹². When they complete 2.5 cycles, their energy leaks into every bin of the column, including bins that carry the tile's own content. The rms error is then 14.1 grey levels unfiltered, 10.8 with a notch at ±3 only, 13.4 at ±2 and ±3, and 17.4 with an eight-bin notch, worse than no filter. Cropping to 20 rows makes the bands complete five whole cycles, and a two-bin notch is exact again.
- Keywords: notch filter, periodic noise, spectral leakage, frequency-domain filtering, 2-D DFT, image restoration
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### feed-07-the-fft-is-a-fixed-toll

- File: `assets/social/feed-07-the-fft-is-a-fixed-toll.png`
- Title: The FFT round trip is a fixed toll
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the FFT route costs about the same at every kernel size, the direct sum grows as 2m², and libraries put the switch in different places
- Technical source: When is the FFT round trip cheaper than the direct sum?, Figure 11; worked example, "What the round trip costs" (L22, L27, L32, L41, L44)
- Visual structure: lockup and counter; serif title; deck; a panel with a table of kernel width, direct operations, FFT-route operations and the cheaper route for seven sizes, the 10×10 row in the accent, then two lines on OpenCV, SciPy and the textbook; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · The FFT round trip is a fixed toll. · About 170 operations per pixel whatever the kernel. A full m × m kernel costs 2m². · operations per pixel, 1920 × 1080 · counted, not timed · m × m · direct 2m² · fft route · cheaper · 3 × 3 18 169.8 direct · 5 × 5 50 169.8 direct · 7 × 7 98 169.8 direct · 9 × 9 162 169.8 direct · 10 × 10 200 169.8 fft · 11 × 11 242 169.8 fft · 13 × 13 338 169.8 fft · OpenCV filter2D switches at area ≥ 130: 12 × 12 · SciPy's model: 3 × 3 · textbook ratio: 7 × 7 · The crossover depends on what you count and on whose direct loop you race. · The 2-D DFT · canery.in
- Alt text: Operations per pixel on a 1920×1080 frame: the FFT route at 169.8 for every size, the direct sum passing it at 10×10.
- Long description: A flop-count model for convolving a 1920×1080 frame, not a timing. The FFT route pads the frame to the next sizes built from 2, 3 and 5 and costs 169.8 operations per output pixel for every kernel up to 29 wide; a full m×m kernel costs 2m² directly: 18 at 3×3, 50 at 5×5, 98 at 7×7, 162 at 9×9, 200 at 10×10, 242 at 11×11 and 338 at 13×13, so the crossover is near 10×10. OpenCV's filter2D switches to the DFT at a kernel area of 130, 12×12, on its fast paths; SciPy's fitted model predicts the FFT from 3×3 in 2-D; Gonzalez and Woods' ratio passes 1 at 7×7.
- Keywords: FFT convolution, convolution cost, OpenCV filter2D, SciPy convolve, crossover, operation count
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: The 2-D DFT, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four readings the article covers, with the link to read it
- Technical source: the article's section structure: reading a spectrum, what phase keeps, filter design and notches, the crossover
- Visual structure: lockup and counter; serif title; deck; a panel of four headed items, each with one mono line of contents and one line of result; takeaway; accent CTA footer
- Visible-text transcript: Canery.in · 08 / 08 · The 2-D DFT, by hand. · Spectra, phase, notches and the FFT crossover, all on one 5×5 patch. · read a spectrum · fftshift on odd sizes, the cross, log scale · DC 65% of the energy · what phase keeps · phase-only rebuilds, the swap, phase correlation · a ridge becomes one peak · filter there · zero-phase gains, padding, notches · exact on-bin, a bet off it · what it costs · four answers to the crossover · ≈ 10 × 10 by count, 12 × 12 on OpenCV's fast path · The full walk-through, with the tooling map for NumPy, OpenCV, SciPy and scikit-image. · Read it at canery.in/blogs/the-2d-dft-spectra-phase-filtering
- Alt text: Four topics from the article: reading a spectrum, what phase keeps, filtering there, and what the FFT costs, with the article link.
- Long description: A closing card listing the article's four readings of the 2-D DFT, each worked on the series' 5×5 patch. Reading a spectrum covers fftshift on odd sizes, the cross the DFT invents at the border and the log scale, with DC holding 65% of the patch's energy. What phase keeps covers phase-only rebuilds, the phase swap and phase correlation, which turns a correlation ridge into one peak. Filtering there covers zero-phase gains, padding and notch filters, exact on-bin and a trade off it. What it costs gives four answers to the FFT crossover: near 10×10 by operation count and 12×12 on OpenCV's fast path.
- Keywords: 2-D DFT, Fourier transform, phase, notch filter, FFT convolution, image processing
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### story-01-a-spectrum-says-how-much

- File: `assets/social/story-01-a-spectrum-says-how-much.png`
- Title: A spectrum says how much, phase says where
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: the patch's centred spectrum, recomposed for a vertical frame: the bright pixel is 215 in every bin
- Technical source: Worked example, "The spectrum, centred", Figure 2
- Visual structure: lockup and counter; serif title; deck; the centred 5×5 magnitude spectrum, log-shaded, DC outlined in the accent and the middle row dashed, with a caption beneath; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · A spectrum says how much. Phase says where. · One edge, one bright pixel, 25 coefficients, by hand. · grid: 215 in the twenty cells off the middle row; middle row 709.4, 1079.4, 2815, 1079.4, 709.4 · the edge's row · the pixel's floor of 215 · One bright pixel: 215 in every bin. Its position is only in the phase. · The 2-D DFT · canery.in
- Alt text: A centred 5×5 magnitude spectrum with 2,815 at the centre, a bright middle row and 215 in every other cell.
- Long description: The magnitude spectrum of the series' 5×5 patch, centred and log-shaded. The middle row, 709.4, 1,079.4, 2,815, 1,079.4, 709.4, is the patch's vertical edge printed as a horizontal line of energy, with DC, the pixel sum, at its centre. Every other cell is 215: the patch's single bright pixel contributes every wave equally, whatever pixel it occupies, so its position is held only in the phase.
- Keywords: 2-D DFT, magnitude spectrum, fftshift, Fourier phase, image processing
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### story-02-keep-the-phase-keep-the-layout

- File: `assets/social/story-02-keep-the-phase-keep-the-layout.png`
- Title: Keep the phase, keep the layout
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the phase-only rebuild keeps the bright pixel in place; the magnitude-only rebuild moves it to the corner
- Technical source: Worked example, "Keep the phase, or keep the magnitude", Figure 3
- Visual structure: lockup and counter; serif title; deck; the shaded phase-only 5×5 grid (× 100) with the pixel outlined, a note to its right, and a two-line statement about the magnitude-only rebuild beneath; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · Keep the phase, keep the layout. · Every magnitude set to 1; only the phase kept. · Phase only, × 100 · every row −5, −16, −5, 13, 13, except row 2: −5, 84, −5, 13, 13 · impulse stays at (2, 1) · Magnitude only: the impulse moves to (0, 0), with the value 428. · Phase holds where things are. Magnitude alone moves them to the corner. · The 2-D DFT · canery.in
- Alt text: The phase-only rebuild of the patch, times 100, with the bright pixel kept at row 2, column 1 as 84.
- Long description: The patch rebuilt from its phase alone, every magnitude set to 1, shown times 100: rows of −5, −16, −5, 13, 13, dark on the left and bright on the right, with 84 at row 2, column 1, where the bright pixel was. Rebuilt from its magnitude alone, with every phase set to zero, the pixel moves to (0, 0) with the value 428. Phase holds where things are.
- Keywords: phase-only reconstruction, importance of phase, 2-D DFT, Fourier magnitude
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### story-03-a-notch-is-exact-only-on-bin

- File: `assets/social/story-03-a-notch-is-exact-only-on-bin.png`
- Title: A notch is exact only on-bin
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: a two-bin notch removes on-bin interference exactly; off-bin, every notch trades interference for image
- Technical source: When does a notch work?, Figure 10, and its table
- Visual structure: lockup and counter; serif title; deck; a green headline for the on-bin case with one supporting line, then four horizontal bars of rms error for the off-bin case; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · A notch is exact only on-bin. · At 2.5 cycles the bands leak into the image's own bins. · 3 cycles in 10 rows: exact · two empty bins, a two-bin notch · rms error, grey levels · bands at 2.5 cycles · no filter 14.1 · notch ±3 only 10.8 · notch ±2 and ±3 13.4 · notch eight bins 17.4 · Crop to whole cycles first. At 20 rows the notch is exact again. · The 2-D DFT · canery.in
- Alt text: Bars of rms error for notches on off-bin interference: 14.1 unfiltered, 10.8 at ±3, 13.4 at ±2 and ±3, 17.4 with eight bins.
- Long description: Horizontal bands on the tiled patch that complete 3 cycles in 10 rows fill two empty bins, and a two-bin notch removes them exactly. Bands at 2.5 cycles leak into every bin of the column, including the tile's own. The rms error is 14.1 grey levels unfiltered, 10.8 with a notch at ±3 only, 13.4 at ±2 and ±3, and 17.4 with an eight-bin notch. Cropping to 20 rows makes the bands complete whole cycles, and the notch is exact again.
- Keywords: notch filter, spectral leakage, periodic noise, 2-D DFT, image restoration
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Four readings of every spectrum
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: four rules from the article, and the link
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; an accent-tinted panel with four numbered rules; takeaway; accent CTA footer
- Visible-text transcript: Canery.in · 04 / 04 · Four readings of every spectrum. · Worked by hand on one 5×5 patch. · 1 magnitude: how much, which way · 2 phase: where · 3 notch: only where the image is empty · 4 FFT: a toll of ~170 per pixel at 1080p · The full walk-through is on Canery. · Link in the sticker above
- Alt text: Four numbered rules: magnitude says how much and which way, phase says where, notch where the image is empty, FFT costs a fixed toll.
- Long description: A closing Story frame with four rules from the article. Magnitude says how much of each wave there is and which way it runs. Phase says where things are. A notch belongs only where the image itself is empty. The FFT round trip costs a near-fixed toll, about 170 operations per pixel on a 1920×1080 frame. The link sticker above points to the full article.
- Keywords: 2-D DFT, Fourier phase, notch filter, FFT convolution, image processing
- Canonical URL: https://canery.in/blogs/the-2d-dft-spectra-phase-filtering
