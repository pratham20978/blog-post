---
social_schema: 2
canonical_url: "https://canery.in/blogs/mathematical-morphology"
---

# Social publishing package — mathematical-morphology

## LinkedIn post

OpenCV's closing deleted five pixels from a 5×5 mask. A closing, by definition, only ever adds pixels.

Worked by hand, the question is which laws erosion and dilation obey, and what keeps those laws true in a real library.

→ Erosion and dilation are an adjoint pair: dilating A stays inside Y exactly when A stays inside the erosion of Y. Every law follows from that one line: opening never adds a pixel, closing never removes one.
→ Opening twice is opening once, so iterations=2 in cv2.morphologyEx cannot mean "twice". It erodes twice and dilates twice, an opening by a bigger element. On the patch: 10 pixels against none.
→ Grey morphology is binary morphology at every threshold, stacked. The morphological gradient reads the patch's step as 160, its height; Sobel reads 640 and gives the impulse 0.
→ The border rule is part of the operator. Ignore the outside, as OpenCV and MATLAB do, and the laws hold; assume 0 outside, as SciPy's binary functions do, and the closing loses 7 of 11 pixels.
→ OpenCV's dilate does not reflect the kernel, so with np.ones((2, 2)) its MORPH_CLOSE loses 5 pixels. Dilating with anchor=(0, 0) restores the law.

Part 12 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

Erosion and dilation are one law, and every opening, closing and sieve inherits it, as long as the library keeps the pair adjoint.

Read the full article on Canery: https://canery.in/blogs/mathematical-morphology

## Instagram caption

OpenCV's closing deleted five pixels. Swipe through mathematical morphology worked by hand on one 5×5 patch: why erosion and dilation are one law, why opening twice changes nothing and what iterations=2 really does, how grey erosion is binary erosion stacked level by level, why the morphological gradient reads 160 where Sobel reads 640, how a sieve of growing elements sizes the speck and the bar, and why a border rule can break a closing.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#computervision #imageprocessing #opencv #morphology #python #scikitimage #scipy

## Shared feed order

1. `assets/social/feed-01-a-closing-that-deletes-pixels.png` — the patch's mask, OpenCV's 2×2 MORPH_CLOSE losing five of its pixels, and a true closing that keeps them all
2. `assets/social/feed-02-one-law.png` — the adjunction, δ(A) ⊆ Y exactly when A ⊆ ε(Y), checked on two pairs of the patch's sets
3. `assets/social/feed-03-twice-is-once.png` — the opening applied once and twice give the same 10 pixels; iterations=2 gives none
4. `assets/social/feed-04-grey-is-binary-stacked.png` — the grey erosion of the patch built from the binary erosions of its threshold sets
5. `assets/social/feed-05-heights-not-slopes.png` — the morphological gradient (160 at the step, 215 round the impulse) beside Sobel (640 and 0)
6. `assets/social/feed-06-a-sieve-with-four-meshes.png` — the granulometry, 11, 10, 0, 0 pixels, and its pattern spectrum: the speck at size 0, the bar at size 1
7. `assets/social/feed-07-the-border-decides.png` — erosion and closing with the outside ignored and with the outside 0
8. `assets/social/feed-08-read-the-article.png` — the four ideas of the post, and the CTA

## Instagram Story

- CTA: Why did a closing delete five pixels? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/mathematical-morphology

### Story order

1. `assets/social/story-01-the-closing-deleted-five-pixels.png` — Overlay: OpenCV's 2×2 closing lost five pixels.
2. `assets/social/story-02-twice-is-once.png` — Overlay: Opening twice is opening once; iterations=2 is not.
3. `assets/social/story-03-160-not-640.png` — Overlay: The gradient reads heights, not slopes.
4. `assets/social/story-04-read-the-article.png` — Overlay: Mathematical morphology, by hand. Link below.

## Asset metadata

### feed-01-a-closing-that-deletes-pixels

- File: `assets/social/feed-01-a-closing-that-deletes-pixels.png`
- Title: OpenCV's closing deleted five pixels
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: with np.ones((2, 2)), OpenCV's MORPH_CLOSE on the patch's 11-pixel mask returns 7 pixels and loses 5 of the mask's, which a closing must never do; the true closing keeps all 11
- Technical source: Where do libraries break the laws?, "The reflection"; Figure 10; ledger L34, L42
- Visual structure: lockup and counter; serif title; deck; a panel with three 5×5 grids side by side (the mask, OpenCV's closing, a true closing) with pixel counts, a legend and the fix in code; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · OpenCV's closing deleted five pixels. · A 2×2 kernel, the series' 5×5 mask, and cv2.MORPH_CLOSE, which may only add pixels. · the mask · 11 px · MORPH_CLOSE, 2×2 · 7 px, 5 lost · a true closing · 13 px, none lost · in the set · not in it · added · removed · fix: cv2.dilate(mask, k, anchor=(0, 0)), then cv2.erode · OpenCV's dilate does not reflect the kernel, so the pair is no longer adjoint. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: Three 5×5 masks: the 11-pixel original, OpenCV's 2×2 closing that loses five of its pixels, and a true closing that keeps them all.
- Long description: The series' patch binarised at 40 gives an 11-pixel mask: a two-column bar and a lone speck. OpenCV's morphologyEx with MORPH_CLOSE and a 2×2 kernel returns only 7 pixels, column c4 plus two pixels in row r3, losing four pixels of column c3 and the speck; a closing must keep every pixel it is given. The true closing, with the dilation's offsets reflected, returns 13 pixels and contains the whole mask. Dilating with anchor (0, 0) before eroding gives that true result. The takeaway: OpenCV's dilate does not reflect the kernel, so erode and dilate are no longer an adjoint pair.
- Keywords: morphological closing, OpenCV morphologyEx, structuring element, even-sized kernel, anchor, dilation reflection
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### feed-02-one-law

- File: `assets/social/feed-02-one-law.png`
- Title: Erosion and dilation are one law
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the adjunction δ(A) ⊆ Y exactly when A ⊆ ε(Y), checked on the speck and on column c4 against the mask, gives the same answer both ways
- Technical source: Worked example, step 4; Figure 3; ledger L04, L06
- Visual structure: lockup and counter; serif title; deck; a panel with the law in code type, then two rows of four small grids (δ(A) and Y, A and ε(Y)) each with its yes or no; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Erosion and dilation are one law. · Stamping A inside Y is the same question as A fitting inside the erosion of Y. · δ(A) ⊆ Y exactly when A ⊆ ε(Y) · A = the speck, Y = X · no · no · A = column c4, Y = X · yes · yes · left: is δ(A) inside Y? right: is A inside ε(Y)? · the same answer every time, on all 64 pairs of the post's sets · Put Y = δ(A): closing never removes a pixel. Put A = ε(Y): opening never adds one. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: The law δ(A) ⊆ Y exactly when A ⊆ ε(Y), checked on two pairs of the patch's masks: no and no, then yes and yes.
- Long description: Erosion by the cross keeps the pixels where the cross fits; dilation stamps the cross on every pixel. The adjunction says the dilation of A lies inside Y exactly when A lies inside the erosion of Y. For A the speck and Y the mask, both answers are no: the speck's cross reaches outside the mask, and the mask's erosion is column c4. For A column c4 and Y the mask, both are yes. All 64 pairs of the eight sets in the post agree. Substituting Y = δ(A) shows a closing never removes a pixel; substituting A = ε(Y) shows an opening never adds one.
- Keywords: adjunction, Galois connection, erosion, dilation, mathematical morphology, opening, closing
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### feed-03-twice-is-once

- File: `assets/social/feed-03-twice-is-once.png`
- Title: Opening twice changes nothing
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: opening the mask once and twice gives the same 10 pixels, while OpenCV's iterations=2 erodes twice then dilates twice and leaves no pixels
- Technical source: Worked example, step 5; Why this matters; ledger L06, L37
- Visual structure: lockup and counter; serif title; deck; a panel with three grids (opened once, opened twice, iterations=2) and their counts, then two lines on what iterations=2 does; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Opening twice changes nothing. · So iterations=2 cannot mean 'open twice'. OpenCV's documentation says what it does. · opened once · = · opened twice · iterations=2 · 10 px · 10 px · 0 px · iterations=2: erode, erode, dilate, dilate · an opening by the 13-pixel diamond, not a second pass · An opening is idempotent; iterations=n is an opening by an element n times the size. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: The mask opened once and twice, both the same 10 pixels, beside OpenCV's iterations=2, which leaves an empty mask.
- Long description: Opening the patch's mask by the cross removes the speck and keeps the 10-pixel bar; opening that result again changes nothing, because an opening is idempotent. OpenCV's morphologyEx with iterations=2 is not a second pass: as its documentation notes, it erodes twice and then dilates twice, which is an opening by the 13-pixel diamond, and on the patch it removes every pixel. The takeaway: iterations=n is an opening by an element n times the size.
- Keywords: opening, idempotent, OpenCV iterations, morphologyEx, structuring element size, morphology
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### feed-04-grey-is-binary-stacked

- File: `assets/social/feed-04-grey-is-binary-stacked.png`
- Title: Grey erosion is binary erosion, stacked
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the patch's threshold set from 41 to 200 is the mask, which erodes to column c4; the impulse's set erodes to nothing; stacking gives the grey erosion, 200 on c4 and 40 elsewhere
- Technical source: How do grey levels inherit the laws?, "Threshold sets"; Figure 6; ledger L17, L18
- Visual structure: lockup and counter; serif title; deck; a panel with three grids joined by arrows (the patch's values, the eroded threshold set, the grey erosion's values) and five lines explaining the levels; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Grey erosion is binary, stacked. · Cut the patch at every level, erode each set, and stack the results back up. · f, the patch (rows of 40 40 40 200 200, with 255 at r2, c1) · X_41, eroded · ε(f), stacked (rows of 40 40 40 40 200) · t from 41 to 200: the threshold set is the mask · t from 201 to 255: the impulse alone, which erodes to nothing · t up to 40: the whole grid, which stays whole · each pixel takes the highest t that survives: 200 on c4, 40 elsewhere · Flat operators commute with thresholds, so every binary law holds in grey. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: The 5×5 patch, its threshold set at 41 eroded to column c4, and the stacked grey erosion with 200 on c4 and 40 elsewhere.
- Long description: Cutting the series' patch at a grey level t gives one of three sets: the whole grid for t up to 40, the 11-pixel mask for t from 41 to 200, and the impulse alone for t from 201 to 255. Eroding each by the cross gives the whole grid, column c4, and nothing. Each pixel of the grey erosion takes the highest level whose eroded set still contains it, so the grey erosion is 200 on column c4 and 40 everywhere else: the impulse is gone and the step has moved one column right. Because flat operators commute with thresholds, every binary law holds for grey images.
- Keywords: grey-level morphology, threshold decomposition, flat structuring element, erosion, stacking, mathematical morphology
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### feed-05-heights-not-slopes

- File: `assets/social/feed-05-heights-not-slopes.png`
- Title: Gradient 160, Sobel 640
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the morphological gradient reads the patch's step as 160, its height, and the impulse as 215; Part 8's Sobel reads 640 on the step and 0 on the impulse itself
- Technical source: How do grey levels inherit the laws?, "Gradients and top-hats"; Figure 7; ledger L21
- Visual structure: lockup and counter; serif title; deck; a panel with two 5×5 value grids side by side, the morphological gradient and Sobel, each with two caption lines; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Gradient: 160. Sobel: 640. · The patch's step is 160 grey levels high. Dilation minus erosion reads it as it is. · dilation − erosion (values 0, 160 and 215) · Sobel, Part 8's table (values 0, 210, 304.1, 430, 476.3 and 640) · 160: the step's height · 215: the impulse · 640 = 4 × 160 on the step · 0 on the impulse itself · A range never cancels: the impulse reads 215 where Sobel's two halves give 0. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: Two 5×5 grids: the morphological gradient, 160 at the step and 215 round the impulse, beside Sobel, 640 at the step and 0 at the impulse.
- Long description: Dilation minus erosion by the cross is the range of grey levels under the cross at each pixel. On the patch it reads 160 on both sides of the step, which is the step's height, and 215 on the impulse and its four neighbours. Part 8's Sobel magnitude reads 640 along column c3, four times the step's height, and 0 on the impulse itself, where its two derivative halves cancel. A range never cancels, so the morphological gradient marks the impulse where Sobel cannot.
- Keywords: morphological gradient, Sobel, edge detection, dilation minus erosion, grey-level morphology, OpenCV MORPH_GRADIENT
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### feed-06-a-sieve-with-four-meshes

- File: `assets/social/feed-06-a-sieve-with-four-meshes.png`
- Title: The speck is size 0, the bar is size 1
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: opening by the cross family nB keeps 11, 10, 0 and 0 pixels for n = 0 to 3, so the pattern spectrum puts the speck at size 0 and the bar at size 1, a size the bar gets only because it touches the edge
- Technical source: Worked example, step 6; Figure 4; ledger L23, L25
- Visual structure: lockup and counter; serif title; deck; a panel with a bar chart of the area kept for n = 0 to 3 with the elements drawn under each bar, and a list of what each size removes; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · The speck is size 0. The bar is size 1. · Open by growing elements and count what each size removes: a pattern spectrum. · mask area kept by the opening by nB · 11 · 10 · 0 · 0 · n = 0 · n = 1 · n = 2 · n = 3 · what each size removes · size 0 · 1 px: the speck · size 1 · 10 px: the bar · size 2 and up · nothing left · The bar is 2 pixels wide yet survives the 3-wide cross, because it touches the edge. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: Bars of 11, 10, 0 and 0 pixels for openings by four growing elements, with the speck removed at size 0 and the bar at size 1.
- Long description: Opening the patch's mask by the cross summed with itself n times, for n from 0 to 3, keeps 11, 10, 0 and 0 pixels. The drops form the pattern spectrum: one pixel of size 0, the speck, removed by the first opening, and ten pixels of size 1, the bar, removed at n = 2. The bar is only two pixels wide but survives the three-pixel-wide cross because it touches the image's edge and the outside is ignored, so a sieve measures objects touching the border as larger than they are.
- Keywords: granulometry, pattern spectrum, opening, size distribution, structuring element, mathematical morphology
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### feed-07-the-border-decides

- File: `assets/social/feed-07-the-border-decides.png`
- Title: SciPy's closing lost seven pixels
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: with the outside ignored the mask erodes to 5 pixels and closes to 14 that contain it; with SciPy's default of 0 outside it erodes to nothing and closes to 7, losing 7 pixels
- Technical source: Where do libraries break the laws?, "The border rule"; Figure 9; ledger L35, L48
- Visual structure: lockup and counter; serif title; deck; a panel with a two-by-two block of grids (erosion and closing, outside ignored and outside 0) with counts, and the adjunction's failure count; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · SciPy's closing lost seven pixels. · Its binary functions assume 0 outside the image; OpenCV and MATLAB ignore the outside. · erosion · closing · outside ignored · OpenCV, MATLAB · 5 px · 14 px · keeps X · outside = 0 · SciPy's default · 0 px · 7 px · loses 7 · outside = 0: the adjunction fails on 616 of 20,000 random pairs · Ignore the outside and the laws hold; pad it with 0 and they fail at the edge. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: Erosion and closing of the patch's mask under two border rules: 5 and 14 pixels with the outside ignored, 0 and 7 with it set to 0.
- Long description: A finite image needs a rule for its outside. OpenCV and MATLAB make the outside never win a minimum or a maximum; then the cross erodes the 11-pixel mask to column c4, 5 pixels, and the closing has 14 pixels and contains the mask. SciPy's binary functions assume 0 outside; then the erosion is empty and the closing has 7 pixels, losing column c4 and both ends of column c3. The adjunction between erosion and dilation fails on 616 of 20,000 random pairs of masks with the outside set to 0, and on none with it ignored.
- Keywords: border handling, SciPy binary_closing, border_value, OpenCV erode, adjunction, mathematical morphology
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Mathematical morphology, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four ideas of the post, the adjunction, idempotence, grey levels and libraries, and where to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel listing four ideas, each with a heading and two lines; takeaway; call to action in the footer
- Visible-text transcript: Canery.in · 08 / 08 · Mathematical morphology, by hand. · Erosion, dilation and the laws behind them, on one 5×5 patch. · adjunction · δ(A) ⊆ Y exactly when A ⊆ ε(Y) · opening never adds, closing never removes · idempotence · twice is once · iterations=n is a bigger element · grey levels · binary at every threshold · gradient 160 at the step, top-hat 215 · libraries · border and reflection decide · OpenCV's 2×2 closing loses 5 · The full walk-through, every number worked by hand, and the tooling map. · READ IT AT CANERY.IN/BLOGS/MATHEMATICAL-MORPHOLOGY
- Alt text: A summary card listing the adjunction, idempotence, grey levels and libraries, with a link to the full article on Canery.
- Long description: The closing card restates the article's four ideas. Erosion and dilation form an adjunction, so an opening never adds pixels and a closing never removes them. Openings and closings are idempotent, so iterations=n means a bigger element, not repetition. Grey morphology is binary morphology at every threshold; the gradient reads the patch's step as 160 and the top-hat isolates the impulse at 215. Libraries keep or break these laws through their border rule and their reflection: OpenCV's 2×2 closing loses five pixels. The full article is on Canery.
- Keywords: mathematical morphology, erosion, dilation, opening, closing, image processing
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### story-01-the-closing-deleted-five-pixels

- File: `assets/social/story-01-the-closing-deleted-five-pixels.png`
- Title: The closing deleted five pixels
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: OpenCV's 2×2 closing turns the 11-pixel mask into 7 pixels, losing 5; dilating with anchor (0, 0) keeps all 11
- Technical source: Where do libraries break the laws?, "The reflection"; Figure 10; ledger L34, L42
- Visual structure: lockup and counter; serif title; deck; two large 5×5 grids side by side (the mask and OpenCV's closing) with counts and a legend; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · The closing deleted five pixels. · OpenCV, a 2×2 kernel, the 5×5 patch's mask. · the mask · MORPH_CLOSE, 2×2 · 11 px · 7 px, 5 lost · in the set · not in it · added · removed · Dilate with anchor=(0, 0) and the closing keeps all 11. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: The patch's 11-pixel mask beside OpenCV's 2×2 closing of it, 7 pixels with five of the original crossed out.
- Long description: The series' 5×5 patch binarised at 40 gives an 11-pixel mask. OpenCV's MORPH_CLOSE with a 2×2 kernel returns 7 pixels: it keeps column c4, adds one pixel in row r3, and loses four pixels of column c3 and the speck. Because OpenCV's dilate does not reflect the kernel, its closing is not a true closing; dilating with the anchor at (0, 0) before eroding gives a closing that keeps all 11 pixels.
- Keywords: OpenCV closing, morphologyEx, 2×2 kernel, anchor, mathematical morphology
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### story-02-twice-is-once

- File: `assets/social/story-02-twice-is-once.png`
- Title: Opening twice is opening once
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: opening twice keeps the same 10 pixels as opening once, while iterations=2 erodes twice then dilates twice and leaves none
- Technical source: Worked example, step 5; Why this matters; ledger L06, L37
- Visual structure: lockup and counter; serif title; deck; two grids side by side (opened twice, iterations=2) with counts and two lines on what iterations=2 does; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · Opening twice is opening once. · So iterations=2 must be something else. · opened twice · iterations=2 · 10 px, as once · 0 px · erode, erode, dilate, dilate: an opening by a 13-pixel diamond · On the patch: the same 10 pixels, against none. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: The mask opened twice, the same 10-pixel bar as opened once, beside OpenCV's iterations=2 result, which is empty.
- Long description: An opening is idempotent: opening the patch's mask a second time leaves the same 10-pixel bar. OpenCV's iterations=2 erodes twice and dilates twice, which is an opening by the 13-pixel diamond, and on the patch it leaves no pixels at all.
- Keywords: opening, idempotence, OpenCV iterations, morphologyEx, morphology
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### story-03-160-not-640

- File: `assets/social/story-03-160-not-640.png`
- Title: 160, not 640
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the morphological gradient reads the step's height, 160, and marks the impulse with 215, where Sobel reads 640 and 0
- Technical source: How do grey levels inherit the laws?, "Gradients and top-hats"; Figure 7; ledger L21
- Visual structure: lockup and counter; serif title; deck; one large 5×5 grid of the morphological gradient, centred, with a line on Sobel; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · 160, not 640. · The morphological gradient reads the step's height, not its slope. · dilation − erosion, by the cross (values 0, 160 and 215) · Sobel reads 640 on the step, 0 on the impulse · And it marks the impulse with 215, where Sobel reads 0. · MATHEMATICAL MORPHOLOGY · CANERY.IN
- Alt text: The patch's morphological gradient as a 5×5 grid: 160 along the step and 215 on the impulse and its four neighbours.
- Long description: Dilation minus erosion by the cross reads 160 on both sides of the patch's step, the step's height, and 215 on the impulse and its four neighbours. Sobel reads 640 on the step, four times its height, and 0 on the impulse itself, where its two halves cancel.
- Keywords: morphological gradient, Sobel, edge detection, grey-level morphology
- Canonical URL: https://canery.in/blogs/mathematical-morphology

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Mathematical morphology
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the post in four steps, and the link
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel with four numbered steps; takeaway; call to action in the footer
- Visible-text transcript: Canery.in · 04 / 04 · Mathematical morphology. · Worked on one 5×5 patch. · 1 erosion and dilation are adjoint · 2 so twice is once, by law · 3 grey inherits it, level by level · 4 libraries keep it, or break it · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Four numbered steps: erosion and dilation are adjoint, twice is once, grey inherits it, libraries keep or break it.
- Long description: The closing Story frame lists the article in four steps: erosion and dilation are adjoint; so opening and closing are idempotent; grey levels inherit the laws threshold by threshold; and libraries keep them or break them. The link sticker leads to the full article on Canery.
- Keywords: mathematical morphology, erosion, dilation, image processing
- Canonical URL: https://canery.in/blogs/mathematical-morphology
