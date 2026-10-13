---
social_schema: 2
canonical_url: "https://canery.in/blogs/scale-space-and-sift"
---

# Social publishing package — scale-space-and-sift

Feed cards only. By the owner's choice for this post there are no Instagram Story frames, so
`validate_post.py --social` reports the missing Story section; nothing else is expected to fail.

## LinkedIn post

Take one blob detector at a fixed σ and show it a square. It finds one blob at the centre. Enlarge the image twice and run the same detector: it now finds four wells near the corners, and the centre reads half as deep.

That is why SIFT searches σ instead of setting it. Worked by hand on the series' 5×5 patch, enlarged seven times:

→ One octave is six Gaussian blurs and five differences. The square becomes a well in the differences, deepest on the middle level, at its own scale.
→ A candidate must beat all 26 neighbours in x, y and σ. At the square's centre, −35.379 is below every one of them.
→ A quadratic fit refines σ the way it refines position: 0.055 of a level down, to σ = 2.508, 1% from the true minimum of the continuous curve.
→ Lowe's edge test is Harris's ratio test with k = 0.0826. A point between the square and the step passes Harris at 0.04 and fails SIFT, 23.2 against 12.1.
→ "Only the Gaussian may search" holds under non-enhancement or separability. Drop both, and the Poisson kernel qualifies too.

Part 10 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

One detail for OpenCV users: by default SIFT doubles the image with resize, and on this patch every keypoint lands a quarter pixel out, at (10.23, 17.25) instead of near (10, 17). enable_precise_upscale=True, added in 4.8, removes the shift.

Read the full article on Canery: https://canery.in/blogs/scale-space-and-sift

## Instagram caption

σ is a search dimension. Swipe through SIFT's scale search worked by hand on one patch: why a detector at a fixed σ sees the same square as one blob or four corners depending on the zoom, how one octave of differences of Gaussians turns the square into a well, the 26-neighbour test, the quadratic fit that refines σ like position, why the edge test is a stricter Harris, why only the Gaussian may do the searching, and the quarter pixel OpenCV adds by default.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#computervision #imageprocessing #sift #scalespace #opencv #featuredetection #python

## Shared feed order

1. `assets/social/feed-01-sigma-is-a-search-dimension.png` — one DoG level on the square at ×7 and ×14: one well, then four corner wells, then one well again at twice the σ
2. `assets/social/feed-02-six-blurs-five-differences.png` — the octave's five DoG levels, the square's centre deepest on the middle one
3. `assets/social/feed-03-lower-than-all-26-neighbours.png` — the 3×3×3 block at (10, 17), the centre below all 26 neighbours
4. `assets/social/feed-04-scale-is-refined-like-position.png` — the DoG along scale, the fitted minimum at σ 2.508 against the curve's 2.480
5. `assets/social/feed-05-the-edge-test-is-a-stricter-harris.png` — Tr²/Det for the two candidates against SIFT's 12.1 and Harris's 25
6. `assets/social/feed-06-why-only-the-gaussian.png` — three kernels against four requirements; non-enhancement or separability leaves the Gaussian
7. `assets/social/feed-07-a-quarter-pixel-by-default.png` — OpenCV's default keypoint a quarter pixel out, the precise-upscale one at the centre
8. `assets/social/feed-08-read-the-article.png` — the four answers the article works through, and the CTA

## Asset metadata

### feed-01-sigma-is-a-search-dimension

- File: `assets/social/feed-01-sigma-is-a-search-dimension.png`
- Title: σ is a search dimension
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: one DoG level finds the ×7 square as one well, but the same square enlarged to ×14 as four corner wells; at twice the σ the single well returns
- Technical source: Why must scale be searched; At a fixed σ, the bigger square is four corners; Figure 6
- Visual structure: lockup and counter; serif title; deck; a panel with three DoG maps side by side, blue below zero and warm grey above, the minima ringed in orange; a note under each map; a legend; one line on the searched result; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · σ is a search dimension. · Fix σ and the answer depends on the zoom: the same square, enlarged twice as much. · one DoG level on the patch at ×7, then at ×14 · ×7, σ 2.540 → 3.200 · ×14, the same σ · ×14, σ doubled · maps: one ringed well at the ×7 square's centre; four ringed wells near the ×14 square's corners; one ringed well at the ×14 square's centre · one well, −35.38 at the centre · four wells, −20.43; the centre −9.66 · one well again, −35.38 at the centre · below zero · above zero · searched, the ×14 square returns: size 10.03 against 5.03 · closed form at pixel centres; worked by hand, not run · A fixed σ sees one size. Search σ, and only the reported size changes. · SCALE SPACE AND SIFT · CANERY.IN
- Alt text: Three DoG maps: one well on the ×7 square, four corner wells on the ×14 square, one well again at twice the σ.
- Long description: The series' 5×5 patch, enlarged seven times, holds a square of 255 beside a step. The difference of Gaussians between σ 2.540 and 3.200 shows one well at the square's centre, −35.38. Applied unchanged to the patch enlarged fourteen times, the same level shows four wells of −20.43 near the corners, and the centre reads only −9.66. On the level whose σ is twice as large, the ×14 square's single well returns with the same value. Searched over σ, OpenCV's rules report the ×14 square with size 10.03 against 5.03 for ×7. The takeaway: a fixed σ sees one size; searched, only the reported size changes.
- Keywords: scale space, SIFT, difference of Gaussians, scale invariance, blob detection, scale selection
- Canonical URL: https://canery.in/blogs/scale-space-and-sift

### feed-02-six-blurs-five-differences

- File: `assets/social/feed-02-six-blurs-five-differences.png`
- Title: Six blurs, five differences
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one octave of six Gaussian blurs gives five differences, and the square's centre is deepest on the middle one
- Technical source: Worked example, step 1; Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with five small DoG maps in a row, labelled D0 to D4 with their σ pairs and the centre's value, D2 highlighted and ringed; a bracket over D1 to D3; two lines on the deepest level; one line on the σ schedule; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Six blurs, five differences. · One octave on the 5×5 patch enlarged seven times: a square of 255 beside a step. · the five DoG levels of the ×7 patch · D0 σ 1.60→2.02 −21.86 · D1 σ 2.02→2.54 −32.22 · D2 σ 2.54→3.20 −35.38 · D3 σ 3.20→4.03 −31.42 · D4 σ 4.03→5.08 −23.12 · searched: D1 to D3, each has a level above and below · the square's centre, (10, 17), is deepest on D2: −35.38, below −32.22 on D1 and −31.42 on D3 · six blurs at σ = 1.6 × 2^(i/3); three intervals per octave · closed form at pixel centres; worked by hand, not run · Subtract neighbouring blurs and the square becomes a well, deepest at its own scale. · SCALE SPACE AND SIFT · CANERY.IN
- Alt text: Five DoG levels of the enlarged patch in a row, the square's centre deepest on the middle level at −35.38.
- Long description: One octave starts at σ = 1.6 and multiplies by 2^(1/3) per level, giving six Gaussian blurs and five differences, D0 to D4. At the square's centre, (10, 17), the differences read −21.86, −32.22, −35.38, −31.42 and −23.12: the well is deepest on D2, between σ 2.54 and 3.20. Only D1 to D3 are searched for extrema, because each needs a level above and below. The takeaway: subtracting neighbouring blurs turns the square into a well that is deepest at its own scale.
- Keywords: difference of Gaussians, SIFT octave, Gaussian pyramid, scale levels, σ = 1.6, three intervals
- Canonical URL: https://canery.in/blogs/scale-space-and-sift

### feed-03-lower-than-all-26-neighbours

- File: `assets/social/feed-03-lower-than-all-26-neighbours.png`
- Title: Lower than all 26 neighbours
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the candidate test compares a sample with 26 neighbours in x, y and level, and the square's centre is below all of them
- Technical source: Worked example, step 2; Figure 2
- Visual structure: lockup and counter; serif title; deck; a panel with three 3×3 grids of numbers for levels 1, 2 and 3, shaded blue by depth, the centre of level 2 outlined in orange; two lines on the closest neighbour; two lines on the octave's two candidates; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Lower than all 26 neighbours. · The candidate test compares a sample with its neighbours in x, y and the levels either side. · the 3×3×3 block around (10, 17) on level 2 · level 1 · σ 2.016: −29.038 −30.586 −29.024 / −30.589 −32.216 −30.575 / −29.038 −30.586 −29.024 · level 2 · σ 2.540: −31.126 −33.169 −30.927 / −33.223 −35.379 −33.024 / −31.126 −33.169 −30.927 · level 3 · σ 3.200: −28.432 −29.723 −27.516 / −30.056 −31.417 −29.140 / −28.432 −29.723 −27.516 · x = 9 · 10 · 11 · −35.379 is below all 26 others; the closest, −33.223, sits one pixel to its left · over the whole octave, two samples pass: (10, 17), the square, and (17, 17), between square and step · closed form at pixel centres; worked by hand, not run · Every one of the 26 comparisons goes the same way: (10, 17) is a candidate. · SCALE SPACE AND SIFT · CANERY.IN
- Alt text: Three 3×3 grids of DoG values around (10, 17); the centre, −35.379, is lower than all 26 neighbours.
- Long description: SIFT keeps a sample as a candidate only if it is larger or smaller than all 26 neighbours in the 3×3×3 block across x, y and the levels either side. At (10, 17) on level 2 the centre is −35.379; the closest neighbour, −33.223, is one pixel to its left, and rows 16 and 18 are equal because the patch is symmetric about row 17. Over the whole octave exactly two samples pass: the square's centre and (17, 17), a maximum between the square and the step. The takeaway: all 26 comparisons go the same way, so (10, 17) is a candidate.
- Keywords: SIFT keypoint detection, 26 neighbours, scale-space extrema, DoG extremum, local minimum
- Canonical URL: https://canery.in/blogs/scale-space-and-sift

### feed-04-scale-is-refined-like-position

- File: `assets/social/feed-04-scale-is-refined-like-position.png`
- Title: Scale is refined like position
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the quadratic fit moves the extremum 0.055 of a level down, to σ 2.508, 1% from the continuous curve's minimum
- Technical source: Worked example, step 3; The fit; Figure 3
- Visual structure: lockup and counter; serif title; deck; a chart of the DoG at the square's centre against level 0 to 4, the closed-form curve in grey, five samples (the three fitted ones filled), the fitted parabola dashed orange and its minimum ringed; annotations for the fit and the curve's minimum; three lines on the offset and contrast; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Scale is refined like position. · A quadratic fit through the 3×3×3 block puts the extremum between samples, in σ too. · the DoG at the square's centre, along scale; filled: the samples fitted · axis −20 to −35 · level 0 σ 1.600 · level 1 σ 2.016 · level 2 σ 2.540 · level 3 σ 3.200 · level 4 σ 4.032 · closed-form curve (grey): its minimum at σ 2.480 · fit: σ 2.508 · 0.055 of a level below 2 · offset in (x, y, level): (−0.0193, 0, −0.0554) · value at the fit −35.391, or 0.139 on 0 to 1 · Lowe's contrast threshold is 0.03: kept · closed form at pixel centres; worked by hand, not run · The keypoint's σ is 2.508, 1% from the continuous curve's own minimum. · SCALE SPACE AND SIFT · CANERY.IN
- Alt text: The DoG at the square's centre across five levels, with a fitted parabola whose minimum sits just below level 2.
- Long description: Plotted along scale, the square's centre reads −21.86, −32.22, −35.38, −31.42 and −23.12 on levels 0 to 4. Brown and Lowe's quadratic fit through the 3×3×3 block gives an offset of (−0.0193, 0, −0.0554) in x, y and level, so the keypoint's σ is 1.6 × 2^((2 − 0.0554)/3) = 2.508. The continuous closed-form curve has its own minimum at σ 2.480, 1% away. The value at the fit, −35.391, is 0.139 on a 0-to-1 scale, far above Lowe's contrast threshold of 0.03. The takeaway: scale is refined like position.
- Keywords: SIFT subpixel refinement, quadratic fit, Taylor expansion, scale interpolation, contrast threshold
- Canonical URL: https://canery.in/blogs/scale-space-and-sift

### feed-05-the-edge-test-is-a-stricter-harris

- File: `assets/social/feed-05-the-edge-test-is-a-stricter-harris.png`
- Title: The edge test is a stricter Harris
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Lowe's Tr²/Det < 12.1 is Harris's sign test with k = 0.0826, so the gap point that Harris at 0.04 would keep is rejected
- Technical source: Worked example, step 4; The edge test is Harris's ratio test; Figure 11
- Visual structure: lockup and counter; serif title; deck; a horizontal Tr²/Det axis from 0 to 30 with SIFT's line at 12.1 and Harris's dashed line at 25, the bands each keeps tinted, and the two candidates as dots at 4.00 and 23.2; three lines on the curvatures; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · The edge test is a stricter Harris. · Lowe's Tr²/Det < 12.1 is Harris's sign test with k = 0.0826, on the DoG's Hessian. · Tr²/Det of the DoG's 2×2 Hessian in x and y · SIFT keeps · Harris, k = 0.04, keeps too · the square 4.00 · the gap 23.2 · 0 10 20 30 · SIFT, r = 10: 12.1 · k = 10/121 = 0.0826 · Harris: 25 · k = 0.04 · the square: Dxx 4.510, Dyy 4.420, a round bowl · the gap: Dxx −3.804, Dyy −0.180, a ridge; rejected · 4 is the floor: two equal curvatures · closed form at pixel centres; worked by hand, not run · The gap point would pass Harris at 0.04. SIFT's edge test is what removes it. · SCALE SPACE AND SIFT · CANERY.IN
- Alt text: A Tr²/Det axis with the square at 4.00 inside SIFT's 12.1 limit and the gap point at 23.2, inside only Harris's 25.
- Long description: Lowe rejects a candidate whose 2×2 DoG Hessian has Tr²/Det of (r + 1)²/r = 12.1 or more, with r = 10; that is the same inequality as Harris's sign test with k = 10/121 = 0.0826. The square's centre has curvatures 4.510 and 4.420 and a test value of 4.00, the floor for two equal curvatures. The point between the square and the step has −3.804 and −0.180, a ridge with test value 23.2: above SIFT's 12.1, but below the 25 that Harris with k = 0.04 allows. The takeaway: SIFT's edge test is a stricter Harris, and it alone removes the gap point.
- Keywords: SIFT edge test, Harris corner detector, Hessian ratio, principal curvatures, edge response
- Canonical URL: https://canery.in/blogs/scale-space-and-sift

### feed-06-why-only-the-gaussian

- File: `assets/social/feed-06-why-only-the-gaussian.png`
- Title: Why only the Gaussian may search
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the Poisson kernel passes linearity, the semigroup and invariance; only non-enhancement or separability leaves the Gaussian alone
- Technical source: Why is the Gaussian the only kernel; The Poisson kernel, and what "only" depends on; Figure 8
- Visual structure: lockup and counter; serif title; deck; a table of three kernels against four requirements with dots for yes and orange crosses for no, the non-enhancement and separability columns boxed in dashed orange; two lines on what all three share; two lines on the box counterexample; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Why only the Gaussian may search. · Blurring more must never invent structure. Which requirement rules each kernel out? · three kernels against the requirements that differ · semi-group · rotation-invariant · non-enhancement · separable · Gaussian: yes yes yes yes · Poisson: yes yes no no · box: no no no yes · either one leaves only the Gaussian · all three are linear, shift- and scale-invariant and positive (Felsberg & Sommer, for Poisson) · box: on 2 9 1 4 1 7 7 7 6, a peak of 4.40 rises to 4.43 when the box widens from 5 to 7 · Non-enhancement or separability leaves only the Gaussian. Without both, Poisson fits. · SCALE SPACE AND SIFT · CANERY.IN
- Alt text: A table of three kernels against four requirements; only the Gaussian passes non-enhancement and separability both.
- Long description: The Gaussian, the Poisson kernel and the box are all linear, shift- and scale-invariant and positive. The box fails the semigroup, rotation invariance and non-enhancement: on the signal 2 9 1 4 1 7 7 7 6, a five-wide box's local maximum of 4.40 rises to 4.43 at width seven. The Poisson kernel, as Felsberg and Sommer showed, passes the semigroup and rotation invariance but fails non-enhancement and separability. Either of those two requirements leaves only the Gaussian. The takeaway: "only the Gaussian" holds under non-enhancement or separability, and without both the Poisson kernel qualifies.
- Keywords: Gaussian scale space, scale-space axioms, Poisson kernel, non-enhancement, separability, causality
- Canonical URL: https://canery.in/blogs/scale-space-and-sift

### feed-07-a-quarter-pixel-by-default

- File: `assets/social/feed-07-a-quarter-pixel-by-default.png`
- Title: OpenCV's SIFT is off by a quarter pixel
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: OpenCV's default doubling with resize reports the square at (10.23, 17.25); the precise upscale reports (9.98, 17.00)
- Technical source: Implementation: the tooling map, OpenCV; E4 — the quarter pixel
- Visual structure: lockup and counter; serif title; deck; a 3×3 pixel grid around (10, 17) with the square's centre ringed, the default keypoint as an orange cross and the precise-upscale keypoint as a blue dot; the two calls and their results to the right; two lines on the resize mapping; one line on the remaining offset; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · OpenCV's SIFT is off by a quarter pixel. · By default it doubles the image with resize, and every keypoint lands +0.25 px out. · the 3×3 pixels around the square's centre, ×7 patch · columns 9 10 11, rows 16 17 18 · cv2.SIFT_create(), the default · × (10.23, 17.25), size 5.02 · enable_precise_upscale=True · ● (9.98, 17.00), size 5.03 · ○ the square's centre, (10, 17) · resize maps output pixel j to input j/2 − 0.25; halving keeps the even pixels: +0.25 px in x and y · the −0.02 px left after the fix is real: the step's pull · OpenCV's rules replayed in plain Python; not run · Pass enable_precise_upscale=True, added in OpenCV 4.8, and the shift goes. · SCALE SPACE AND SIFT · CANERY.IN
- Alt text: A 3×3 pixel grid: OpenCV's default keypoint a quarter pixel down-right of the square's centre, the precise one on it.
- Long description: By default OpenCV's SIFT doubles the input with resize, which maps output pixel j to input j/2 − 0.25, and halves by keeping the even pixels, so every keypoint is reported +0.25 pixel out in x and y. Replayed in plain Python from OpenCV's rules, the square is reported at (10.23, 17.25) with size 5.02. With enable_precise_upscale=True, added in OpenCV 4.8, it is reported at (9.98, 17.00) with size 5.03; the remaining −0.02 pixel is real, the step's blur pulling the minimum away. The takeaway: pass the flag and the shift goes.
- Keywords: OpenCV SIFT, enable_precise_upscale, keypoint bias, image upscaling, SIFT_create, subpixel accuracy
- Canonical URL: https://canery.in/blogs/scale-space-and-sift

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Scale space and SIFT, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four answers the article works through, and where to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel listing four headings, the last in orange, each with a mono line and a muted line; takeaway; orange call to action with the article URL
- Visible-text transcript: Canery.in · 08 / 08 · Scale space and SIFT, by hand. · Why σ is searched, and why only the Gaussian may search it. · why search σ: a fixed σ sees one size; the ×14 square splits into four corner wells · the octave: 26 neighbours in x, y and σ; one blob kept, σ = 2.508, offsets fitted · the edge test: Harris's ratio test, k = 0.0826; the gap point fails, 23.2 against 12.1 · the Gaussian: non-enhancement or separability; without both, the Poisson kernel passes · The full walk-through, every number worked by hand, and the tooling map. · READ IT AT CANERY.IN/BLOGS/SCALE-SPACE-AND-SIFT
- Alt text: Closing card listing four answers: why search σ, the octave, the edge test and the Gaussian, with the article link.
- Long description: The closing card lists the four answers the article works through: a fixed σ sees one size, so the ×14 square splits into four corner wells; the octave tests 26 neighbours in x, y and σ and keeps one blob at σ 2.508; the edge test is Harris's ratio test with k = 0.0826, which the gap point fails at 23.2 against 12.1; and only non-enhancement or separability singles out the Gaussian. The call to action points to the full article at canery.in/blogs/scale-space-and-sift.
- Keywords: SIFT explained, scale space, difference of Gaussians, image processing, feature detection
- Canonical URL: https://canery.in/blogs/scale-space-and-sift
