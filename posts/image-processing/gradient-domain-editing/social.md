---
social_schema: 2
canonical_url: "https://canery.in/blogs/gradient-domain-editing"
---

# Social publishing package — gradient-domain-editing

## LinkedIn post

Throw away nine pixels of an image, keep their Laplacian and the twelve pixels around them, and you can get all nine back exactly.

That is gradient-domain editing: the gradients inside a region and the values on its border fix every pixel, as the one solution of a Poisson equation. Worked by hand on one 5×5 patch, here is what it takes and what goes wrong.

→ Nine pixels are nine equations, each the five-point stencil with the known frame moved to the right-hand side. At the impulse: 4 × 255 − 40 − 40 − 40 = 900.
→ Three Gauss–Seidel sweeps from zero leave an error of 31 levels. The sweeps strip the jumps fast and leave a smooth bowl that halves per sweep; at 1,023 pixels wide, plain sweeps need 244,633 per digit.
→ One multigrid V-cycle, two sweeps and one coarse equation, leaves 15.4 where three sweeps leave 31.1.
→ Poisson cloning keeps differences, not ratios: cloned into a copy of itself at a fifth of the light, the patch goes to −40 in codes, and in log it comes out exactly right.
→ OpenCV's seamlessClone solves the mask's bounding box with a sine transform, ignores the outer 3 pixels of the mask, compares abs(gx − gy) for MIXED_CLONE, truncates, and since 4.11.0 edits a single-channel mask in place. Read from source, not run.

Part 14 of Image Processing by Hand, the last of its spokes. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

Gradients plus a border fix every pixel: clone across a change of light in log, and give multigrid or a transform the smooth error that sweeps cannot remove.

Read the full article on Canery: https://canery.in/blogs/gradient-domain-editing

## Instagram caption

Keep the gradients and you can lose the pixels. Swipe through gradient-domain editing worked by hand on nine pixels: the nine equations, why three Gauss–Seidel sweeps still leave 31 levels of error, how one multigrid V-cycle halves it, why a Poisson clone into a shadow goes below black, where OpenCV's seamlessClone departs from the paper, and how HDR compression shrinks gradients into a field no image has.

Every number is worked from the series' 5×5 patch. Nothing was run against an image.

Link in bio.

#computervision #imageprocessing #opencv #poissonediting #hdr #multigrid #python

## Shared feed order

1. `assets/social/feed-01-keep-the-gradients.png` — the patch's frame of twelve known pixels around nine unknowns, solved back to the patch
2. `assets/social/feed-02-nine-equations.png` — the equation at the impulse, 900, and the nine right-hand sides
3. `assets/social/feed-03-three-sweeps.png` — the largest error after each Gauss–Seidel sweep, 255 down to 0.97
4. `assets/social/feed-04-one-v-cycle.png` — the five steps of one V-cycle, from 89.7 to 15.4
5. `assets/social/feed-05-differences-not-ratios.png` — the clone into the fifth-light copy in codes (−40) and in log (exact)
6. `assets/social/feed-06-seamlessclone-is-not-the-paper.png` — five places where OpenCV's seamlessClone departs from Pérez et al.
7. `assets/social/feed-07-hdr-shrink-and-solve.png` — Fattal's factor on the step row, 5:1 to 2.70:1, and a square that does not close
8. `assets/social/feed-08-read-the-article.png` — kept, solved, cloned and tiled, and the CTA

## Instagram Story

- CTA: Keep the gradients, lose the pixels, get them back. Worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/gradient-domain-editing

### Story order

1. `assets/social/story-01-keep-the-gradients.png` — Overlay: Twelve values and nine Laplacians bring nine pixels back.
2. `assets/social/story-02-31-after-three-sweeps.png` — Overlay: Three sweeps leave 31 levels; one V-cycle leaves 15.4.
3. `assets/social/story-03-minus-40-or-8.png` — Overlay: Cloned into a shadow: −40 in codes, 8 in log.
4. `assets/social/story-04-read-the-article.png` — Overlay: Gradient-domain editing, by hand. Link below.

## Asset metadata

### feed-01-keep-the-gradients

- File: `assets/social/feed-01-keep-the-gradients.png`
- Title: Keep the gradients, get the pixels back
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: the 3×3 interior of the series' 5×5 patch is thrown away; its Laplacian and the twelve frame pixels around it are kept, and solving the Poisson equation brings the nine pixels back, 255 at the impulse
- Technical source: Worked example, steps 1 and 2; Figures 1 and 2; ledger L01, L03, L54
- Visual structure: lockup and counter; serif title; deck; a panel with two 5×5 grids, the left with nine question marks inside a blue outline, the right with the solved patch, joined by a tangerine arrow labelled solve; three lines of notes; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Keep the gradients. Get the pixels back. · Throw away the 3×3 interior of a 5×5 patch; keep its Laplacian and the 12 pixels around it. · 12 known · 9 unknown · the 9 pixels, back · 40 40 200 / 40 ? ? ? 200 / 40 ? ? ? 200 / 40 ? ? ? 200 / 40 40 200 · solve · 40 40 200 / 40 40 40 200 200 / 40 255 40 200 200 / 40 40 40 200 200 / 40 40 200 · kept inside: the Laplacian, 215 · 160 · −160 / −860 · 375 · −160 / … · solved: ∇²f = div v inside, f fixed on the frame · the series' 5×5 patch · Ω, outlined in blue, is rows r1–r3 × columns c1–c3 · Gradients plus a border fix every pixel: the one solution of a Poisson equation. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: Two 5×5 grids of the patch: twelve known frame pixels around nine question marks, and after solving, the nine pixels back with 255 at the impulse.
- Long description: The series' 5×5 patch has a step from 40 to 200 between columns c2 and c3 and one impulse of 255 at row r2, column c1. Its 3×3 interior, rows r1 to r3 by columns c1 to c3, is erased; what is kept is the twelve frame pixels that touch it (40, 40 and 200 along the top and bottom, 40 down the left, 200 down the right) and the interior's Laplacian (215, 160, −160; −860, 375, −160; 215, 160, −160). Solving the Poisson equation, ∇²f = div v inside with f fixed on the frame, returns the nine pixels exactly. The takeaway: the gradients plus the border fix every pixel, as the one solution of a Poisson equation.
- Keywords: Poisson image editing, gradient domain, Laplacian, Poisson equation, image processing
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### feed-02-nine-equations

- File: `assets/social/feed-02-nine-equations.png`
- Title: Nine pixels, nine equations
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: each unknown pixel gets one five-point equation with its known frame neighbours on the right-hand side; at the impulse the right-hand side is 40 + 860 = 900, which the patch satisfies
- Technical source: Worked example, step 2; Figure 2; ledger L03
- Visual structure: lockup and counter; serif title; deck; a panel with the equation at the impulse, its two right-hand terms labelled, the check with the patch's values, the nine right-hand sides and a note on the matrix; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Nine pixels, nine equations. · One five-point stencil per unknown, with the known frame moved to the right-hand side. · the equation at the impulse, (r2, c1): · 4f(r2,c1) − f(r1,c1) − f(r3,c1) − f(r2,c2) · = 40 · + 860 · known left pixel · minus its Laplacian, −860 · = 900 · check with the patch: 4 × 255 − 40 − 40 − 40 = 900 · all nine right-hand sides, row by row: · −135 −120 560 · 900 −375 360 · −135 −120 560 · A: 4 on the diagonal, −1 between neighbours; symmetric, positive definite · A is symmetric and positive definite, so the patch is the only solution. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: The equation at the patch's impulse, four times the pixel minus three unknown neighbours equals 40 plus 860, 900, with all nine right-hand sides.
- Long description: At the impulse, row r2 column c1, the five-point equation is 4f(r2,c1) − f(r1,c1) − f(r3,c1) − f(r2,c2) = 40 + 860 = 900: the known pixel to its left, 40, plus minus its Laplacian, 860. With the patch's own values, 4 × 255 − 40 − 40 − 40 = 900. The nine right-hand sides, row by row, are −135, −120, 560, 900, −375, 360, −135, −120 and 560. The matrix A has 4 on its diagonal and −1 between neighbouring unknowns; it is symmetric and positive definite, so the patch is the only solution.
- Keywords: Poisson equation, five-point stencil, linear system, Laplacian, image processing
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### feed-03-three-sweeps

- File: `assets/social/feed-03-three-sweeps.png`
- Title: Three sweeps leave 31 levels of error
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Gauss–Seidel from zero reduces the largest error 255, 89.7, 62.1, 31.1; from the third sweep it halves each sweep, the factor cos²(π/4) = 0.5 of the slowest pattern on nine unknowns
- Technical source: Worked example, steps 3 and 5; Figure 3; ledger L26, L27
- Visual structure: lockup and counter; serif title; deck; a panel with nine bars for the largest error at the start and after sweeps 1 to 8, sweep 3 in tangerine, and two lines of notes; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Three sweeps leave 31 levels of error. · Gauss–Seidel on the nine equations: each unknown from its neighbours, in turn. · largest error after each sweep, from all zeros · 255 · 89.7 · 62.1 · 31.1 · 15.5 · 7.8 · 3.9 · 1.9 · 0.97 · start 1 2 3 4 5 6 7 8 · sweep 3 leaves 31.1; from then on the error halves each sweep. · cos²(π/4) = 0.5 is the slowest pattern's factor on nine unknowns · Sweeps strip the jumps fast and the smooth bowl slowly, here halving per sweep. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: Bars for the largest error after each Gauss–Seidel sweep on nine unknowns: 255, 89.7, 62.1, then 31.1 after three sweeps, halving to 0.97.
- Long description: Gauss–Seidel updates each of the nine unknowns from its neighbours in turn, starting from all zeros. The largest error is 255 at the start, then 89.7, 62.1 and 31.1 after three sweeps, then 15.5, 7.8, 3.9, 1.9 and 0.97: from the third sweep on it halves each sweep, because cos²(π/4) = 0.5 is the slowest error pattern's factor on a 3×3 region. The takeaway: sweeps remove the error that jumps between neighbours quickly and the smooth bowl slowly.
- Keywords: Gauss–Seidel, iterative solver, convergence, Poisson equation, multigrid
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### feed-04-one-v-cycle

- File: `assets/social/feed-04-one-v-cycle.png`
- Title: One V-cycle halves what three sweeps leave
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one multigrid V-cycle on the nine unknowns, a sweep, a residual averaged onto one coarse point, one coarse equation with coefficient 3/4, the correction interpolated back and a sweep, leaves 15.4 where three plain sweeps leave 31.1
- Technical source: Worked example, step 4; Figure 4; The math; ledger L29, L30, L33
- Visual structure: lockup and counter; serif title; deck; a panel with five numbered steps and their values on the right, a rule, the comparison line and a note on 3/4; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · One V-cycle halves what three sweeps leave. · Multigrid removes the smooth error on a coarser grid, where it is no longer smooth. · 1 one sweep · largest error 89.7 · 2 residual, full weighting onto one point · r = 80.1 · 3 coarse equation: (3/4) · e = r · e = 106.8 · 4 interpolate back: centre, edges, corners · 106.8 · 53.4 · 26.7 · 5 add it, one more sweep · largest error 15.4 · three plain sweeps: 31.1 · one V-cycle: 15.4 · two: 0.82 · 3/4 = restriction × A × interpolation, on the one coarse point · At 1,023 pixels wide, plain sweeps need 244,633 per digit; multigrid's work is O(n). · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: Five steps of one multigrid V-cycle on nine unknowns, from an error of 89.7 to 15.4, against 31.1 after three plain Gauss–Seidel sweeps.
- Long description: One V-cycle: a Gauss–Seidel sweep leaves a largest error of 89.7; the residual is averaged onto the single coarse point by full weighting, r = 80.1; the coarse equation, with coefficient 3/4 (restriction times A times interpolation), gives e = 106.8; the correction is interpolated back as 106.8 at the centre, 53.4 on the edges and 26.7 at the corners; adding it and sweeping once more leaves 15.4. Three plain sweeps leave 31.1 and two V-cycles 0.82. The takeaway: at 1,023 pixels wide, plain sweeps need 244,633 per decimal digit, while multigrid's work is O(n).
- Keywords: multigrid, V-cycle, Gauss–Seidel, full weighting, Galerkin, Poisson equation
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### feed-05-differences-not-ratios

- File: `assets/social/feed-05-differences-not-ratios.png`
- Title: A clone keeps differences, not ratios
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the patch's gradients cloned into a copy of itself at a fifth of the light go below black in codes (−40 at r2, c2) and come out exactly the shadowed patch (8, 40, 51) in log
- Technical source: What does a clone keep, and what does it give up?; Figure 5; ledger L02, L55
- Visual structure: lockup and counter; serif title; deck; a panel with two 5×5 grids in the fifth-light frame, the left cloned in codes with its four negative cells outlined in tangerine, the right cloned in log, each with a caption, and two notes; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · A clone keeps differences, not ratios. · The patch's gradients cloned into a copy of itself at a fifth of the light. · in codes · in log · 8 8 40 / 8 −6.9 −32 70.9 40 / 8 203.6 −40 75.4 40 / 8 −6.9 −32 70.9 40 / 8 8 40 · 8 8 40 / 8 8 8 40 40 / 8 51 8 40 40 / 8 8 8 40 40 / 8 8 40 · −40 at (r2, c2): below black · the shadowed patch, exactly · frame: the patch at a fifth of the light (8 for 40, 40 for 200) · in log a fifth of the light is −ln 5 all round the frame: a flat membrane · In codes the dark side goes below black. Clone a change of light in log. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: The patch cloned into its fifth-light copy two ways: in codes four cells go below zero, to −40 at r2, c2; in log it is exactly 8, 40 and 51.
- Long description: The frame is the patch at a fifth of the light, 8 where the patch has 40 and 40 where it has 200. Cloning the patch's gradients into it in codes gives −6.9, −32 and 70.9 on the outer rows and 203.6, −40 and 75.4 in the middle: the clone keeps most of its full-light differences, so its dark side goes below black. In log a fifth of the light is the constant −ln 5 all round the frame, the correction is flat, and the clone is exactly the shadowed patch, 8, 40 and 51. The takeaway: clone a change of light in log.
- Keywords: Poisson cloning, seamless cloning, log domain, illumination, gradient domain
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### feed-06-seamlessclone-is-not-the-paper

- File: `assets/social/feed-06-seamlessclone-is-not-the-paper.png`
- Title: seamlessClone is not the paper
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: read from OpenCV's source, seamlessClone solves the mask's bounding box exactly by a sine transform, erodes the mask by 3 pixels, compares abs(gx − gy) in MIXED_CLONE, truncates, and from 4.11.0 edits a single-channel mask in place
- Technical source: Implementation: the tooling map; Figure 10; ledger L40–L48
- Visual structure: lockup and counter; serif title; deck; a panel with five headings, one blue and four tangerine, each with a one-line detail; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · seamlessClone is not the paper. · OpenCV's photo module, read from source at 802cf95 and 4.10.0 to 5.0.0, not run. · bounding box, sine transform · solves the mask's whole box exactly, no iteration · mask eroded 3 px · a mask under 7 px wide clones nothing (#17450, open) · MIXED_CLONE: abs(gx − gy) · the spike's own (−215, −215) gives 0: it never wins · truncation · a value that should be 40 can be stored as 39 · from 4.11.0 · a 1-channel mask is eroded and inverted in place · The 5×5 patch with a full mask clones nothing at all. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: Five ways OpenCV's seamlessClone departs from Poisson image editing: box-wide sine transform, 3-pixel mask erosion, abs(gx − gy) mixing, truncation, mask edits.
- Long description: Read from OpenCV's source at commit 802cf95 and releases 4.10.0 to 5.0.0, not run: seamlessClone solves the mask's whole bounding box exactly with a sine transform, with no iteration; it erodes the mask by three pixels before using any source gradient, so a mask under seven pixels wide clones nothing (issue 17450, open); MIXED_CLONE compares abs(gx − gy), so a one-pixel spike's own pair of differences, (−215, −215), gives 0 and never wins; results are clamped and truncated, so a value that should be 40 can be stored as 39; and from 4.11.0 a single-channel mask is eroded and inverted in place. The takeaway: the series' 5×5 patch with a full mask clones nothing.
- Keywords: OpenCV, seamlessClone, MIXED_CLONE, Poisson image editing, discrete sine transform
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### feed-07-hdr-shrink-and-solve

- File: `assets/social/feed-07-hdr-shrink-and-solve.png`
- Title: HDR: shrink the big gradients, solve again
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Fattal's factor φ = (|∇H|/α)^(β − 1) turns the step row's 5:1 into 2.70:1 at β = 0.85; on one square of the patch the attenuated differences sum to −0.337, so no image has them and least squares must pick the nearest
- Technical source: HDR compression: which gradients shrink?; Figures 7 and 8; ledger L11–L16
- Visual structure: lockup and counter; serif title; deck; a panel with the formula and its parameters, the step row's arithmetic, and a square whose top edge is ink and bottom edge tangerine beside the loop's four values and their sum; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · HDR: shrink the big gradients, solve again. · Fattal's attenuation on the log of the patch, with one pyramid level. · φ = (|∇H| / α)^(β − 1) · H = log luminance · α = 0.1 × mean gradient · β 0.8 to 0.9 · the step row, at β = 0.85: · ln 5 = 1.609 at 25α → × 0.617 → 0.993 · a 5:1 step becomes 2.70:1 · one square of the patch, attenuated: · row r1, left to right: +1.028 · row r2, left to right: +1.365 · down both columns: 0 · round the loop: 1.028 − 1.365 = −0.337 · an image's loops sum to zero · The shrunken field is no image's gradient, so least squares picks the nearest image. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: Fattal's attenuation turns the step row's 5:1 into 2.70:1, and on one square of the patch the attenuated differences sum to −0.337 instead of zero.
- Long description: Fattal's attenuation factor is φ = (|∇H|/α)^(β − 1), with H the log of luminance, α 0.1 times the mean gradient magnitude and β between 0.8 and 0.9. On the step row the log rise is ln 5 = 1.609 at 25α; at β = 0.85 φ is 0.617, the rise becomes 0.993 and a 5:1 step becomes 2.70:1. On one square of the patch, rows r1 and r2 by columns c2 and c3, the attenuated rise is +1.028 along r1 and +1.365 along r2, with nothing changing down either column, so the loop sums to 1.028 − 1.365 = −0.337 instead of zero. The takeaway: the shrunken field is no image's gradient, so least squares picks the nearest image.
- Keywords: HDR compression, tone mapping, Fattal, gradient domain, Poisson equation
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Gradient-domain editing, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four results of the post, what is kept, how it is solved, what cloning keeps and what tiling does, with the link
- Technical source: Key takeaways; Worked example; Seamless tiling: making opposite edges agree; Figure 9
- Visual structure: lockup and counter; serif title; deck; a panel with four headings, cloned in tangerine, each with two lines; takeaway; CTA footer
- Visible-text transcript: Canery.in · 08 / 08 · Gradient-domain editing, by hand. · Poisson cloning, HDR compression and seamless tiling on one 5×5 patch. · kept · 12 frame values and 9 Laplacians · the 9 pixels come back exactly · solved · 3 sweeps: 31.1 · one V-cycle: 15.4 · OpenCV uses a sine transform: exact · cloned · at (r2, c2): −40 in codes, 8 in log · clone a change of light in log · tiled · 40 40 40 200 200 → 120 80 40 160 120 · the seam's 160 becomes a slope · The full walk-through, every number worked by hand, and the tooling map. · READ IT AT CANERY.IN/BLOGS/GRADIENT-DOMAIN-EDITING
- Alt text: Four results: twelve values and nine Laplacians bring the pixels back, sweeps against a V-cycle, a clone in codes against log, and a tiled row.
- Long description: The closing card lists the post's four results. Kept: twelve frame values and nine Laplacians, from which the nine pixels come back exactly. Solved: three Gauss–Seidel sweeps leave 31.1 and one V-cycle 15.4, while OpenCV solves exactly with a sine transform. Cloned: at row r2, column c2 a clone into the fifth-light copy reads −40 in codes and 8 in log, so clone a change of light in log. Tiled: the row 40 40 40 200 200 becomes 120 80 40 160 120 and the seam's 160 becomes a slope. It invites the reader to the full article.
- Keywords: Poisson image editing, multigrid, seamless tiling, HDR, OpenCV
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### story-01-keep-the-gradients

- File: `assets/social/story-01-keep-the-gradients.png`
- Title: Keep the gradients, lose the pixels
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: the kept frame and Laplacians beside the solved patch: nine equations bring the nine pixels back
- Technical source: Worked example, steps 1 and 2; Figures 1 and 2; ledger L01, L54
- Visual structure: lockup and counter; serif title; deck; two 5×5 grids side by side, the left with a question mark and its Laplacian in each of the nine interior cells, the right solved; the equation in two lines; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Keep the gradients. Lose the pixels. · Twelve values and nine Laplacians are all that is kept. · kept: frame + Laplacians · solved · 40 40 200 / 40 ? 215 ? 160 ? −160 200 / 40 ? −860 ? 375 ? −160 200 / 40 ? 215 ? 160 ? −160 200 / 40 40 200 · 40 40 200 / 40 40 40 200 200 / 40 255 40 200 200 / 40 40 40 200 200 / 40 40 200 · ∇²f = div v inside, f fixed on the frame · Nine equations bring the pixels back. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: The patch's frame with each unknown interior pixel marked by a question mark and its Laplacian, beside the solved patch with 255 at the impulse.
- Long description: On the left, the twelve frame pixels of the series' 5×5 patch are kept and each of the nine interior pixels is unknown, marked with a question mark and its kept Laplacian: 215, 160 and −160; −860, 375 and −160; 215, 160 and −160. On the right is the solution, the patch itself, with the step from 40 to 200 and the impulse of 255. The equation is ∇²f = div v inside, with f fixed on the frame. The takeaway: nine equations bring the pixels back.
- Keywords: Poisson image editing, gradient domain, Laplacian, Poisson equation
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### story-02-31-after-three-sweeps

- File: `assets/social/story-02-31-after-three-sweeps.png`
- Title: 31 levels after three sweeps
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the largest error after each Gauss–Seidel sweep, with sweep 3's 31.1 highlighted, and one V-cycle's 15.4 as the takeaway
- Technical source: Worked example, steps 3 and 4; Figures 3 and 4
- Visual structure: lockup and counter; serif title; deck; nine horizontal bars labelled start and sweep 1 to sweep 8 with their values, sweep 3 in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · 31 levels after three sweeps. · Gauss–Seidel on nine unknowns, from all zeros. · start 255 · sweep 1 89.7 · sweep 2 62.1 · sweep 3 31.1 · sweep 4 15.5 · sweep 5 7.8 · sweep 6 3.9 · sweep 7 1.9 · sweep 8 0.97 · One multigrid V-cycle leaves 15.4. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: Horizontal bars for the largest error after each Gauss–Seidel sweep, 255 at the start to 31.1 after three sweeps and 0.97 after eight.
- Long description: Gauss–Seidel on the nine unknowns, from all zeros, leaves a largest error of 255 at the start, then 89.7, 62.1 and 31.1 after three sweeps, then 15.5, 7.8, 3.9, 1.9 and 0.97 after eight. The takeaway: one multigrid V-cycle leaves 15.4.
- Keywords: Gauss–Seidel, convergence, multigrid, Poisson equation
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### story-03-minus-40-or-8

- File: `assets/social/story-03-minus-40-or-8.png`
- Title: −40 or 8?
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: pixel (r2, c2) of the patch cloned into its fifth-light copy is −40 in codes and 8 in log
- Technical source: What does a clone keep, and what does it give up?; Figure 5; ledger L02, L55
- Visual structure: lockup and counter; serif title; deck; two large dark cells, −40 framed tangerine and 8 framed blue, with their labels and a two-line note; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · −40 or 8? · One pixel, cloned into a fifth of the light, two ways. · −40 · 8 · in codes · in log · pixel (r2, c2) of the patch, cloned into its fifth-light copy · Clone a change of light in log. · GRADIENT-DOMAIN EDITING · CANERY.IN
- Alt text: Two dark cells for one pixel of the patch cloned into its fifth-light copy: −40 when cloned in codes, 8 when cloned in log.
- Long description: Pixel (r2, c2) of the series' patch, cloned with its gradients into a copy of the patch at a fifth of the light, comes out −40, below black, when the clone is done on the pixel codes, and 8, the shadowed patch's own value, when it is done in log. The takeaway: clone a change of light in log.
- Keywords: Poisson cloning, log domain, illumination, gradient domain
- Canonical URL: https://canery.in/blogs/gradient-domain-editing

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Gradient-domain editing
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the post's four points and the link sticker
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tangerine-tinted panel with four numbered points, the third in bold; takeaway; CTA footer
- Visible-text transcript: Canery.in · 04 / 04 · Gradient-domain editing. · Worked on nine pixels of one 5×5 patch. · 1 gradients + a border = the image · 2 sweeps kill jumps fast, bowls slowly · 3 clone a change of light in log · 4 seamlessClone is not the paper · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Four points from the post: gradients and a border fix the image, sweeps and bowls, cloning in log, and seamlessClone's departures from the paper.
- Long description: The closing Story frame lists four points: the gradients plus a border fix the image; Gauss–Seidel sweeps remove jumps in the error fast and smooth bowls slowly; a change of light should be cloned in log; and OpenCV's seamlessClone is not the paper's algorithm. It points to the link sticker for the full article.
- Keywords: Poisson image editing, gradient domain, multigrid, OpenCV
- Canonical URL: https://canery.in/blogs/gradient-domain-editing
