---
social_schema: 2
canonical_url: "https://canery.in/blogs/edge-preserving-smoothing"
---

# Social publishing package — edge-preserving-smoothing

## LinkedIn post

A bilateral filter keeps a hot pixel for the same reason it keeps an edge: to a filter that weighs neighbours by how alike their values are, a bright pixel is just a very strong edge.

Worked by hand on one 5×5 patch, an edge from 40 to 200 and one bright pixel of 255:

→ The bilateral filter (σr = 80) keeps 92% of the edge and 93% of the bright pixel. A neighbour across the edge keeps 13.5% of its weight; a neighbour of the bright pixel only 2.7%, because 215 is the bigger difference. No σr keeps the edge and lets the pixel go.
→ Non-local means compares whole patches instead. The edge's patch repeats down its column; the bright pixel's repeats nowhere. Whether that removes the pixel depends on one rule: the reference algorithm caps a pixel's own weight and gives 83, while OpenCV and scikit-image give it weight 1 and keep 255.
→ Perona–Malik diffusion conducts less across each face of the bright pixel than across the edge, but the pixel has four faces. It drains first, and the whole patch ends at its mean, 112.6, if you never stop.
→ Only the median and non-local means under the reference rule keep the edge and lower the bright pixel.

Part 7 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

Contrast cannot tell noise from an edge when the noise is the bigger jump. Repetition can.

Read the full article on Canery: https://canery.in/blogs/edge-preserving-smoothing

## Instagram caption

A bright pixel is a strong edge, to a bilateral filter. Swipe through edge-preserving smoothing worked by hand on one 5×5 patch: why a bilateral filter keeps the bright pixel, how non-local means tells it apart from the edge, the one rule that decides between 255 and 83, why Perona–Malik diffusion drains the pixel first and ends at the mean, and which methods actually keep the edge and drop the pixel.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#imageprocessing #computervision #denoising #bilateralfilter #opencv #python #signalprocessing

## Shared feed order

1. `assets/social/feed-01-a-bright-pixel-is-a-strong-edge.png` — the patch beside its bilateral-filtered version: the edge and the bright pixel both survive
2. `assets/social/feed-02-weight-by-value.png` — range weights at σr = 80 for differences of 0, 20, 160 and 215
3. `assets/social/feed-03-nl-means-asks-who-looks-like-me.png` — the edge's patch has an exact copy; the bright pixel's best match differs by 5,136
4. `assets/social/feed-04-the-pixels-own-vote.png` — own weight 1 gives 255; the reference rule gives 83
5. `assets/social/feed-05-four-faces-against-one.png` — three Perona–Malik iterations on the bright pixel and the edge
6. `assets/social/feed-06-diffusion-ends-at-the-mean.png` — contrast of both features over 100 iterations
7. `assets/social/feed-07-only-rank-and-repetition-win.png` — the scorecard of six methods
8. `assets/social/feed-08-read-the-article.png` — the four parts of the article, and the CTA

## Instagram Story

- CTA: Why does a bilateral filter keep a hot pixel? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/edge-preserving-smoothing

### Story order

1. `assets/social/story-01-a-bright-pixel-is-a-strong-edge.png` — Overlay: The edge stays. So does the pixel.
2. `assets/social/story-02-0-135-against-0-027.png` — Overlay: The bigger jump is better protected.
3. `assets/social/story-03-the-pixels-own-vote.png` — Overlay: One rule: 255 or 83.
4. `assets/social/story-04-read-the-article.png` — Overlay: Three ways to smooth without blurring. Link below.

## Asset metadata

### feed-01-a-bright-pixel-is-a-strong-edge

- File: `assets/social/feed-01-a-bright-pixel-is-a-strong-edge.png`
- Title: A bright pixel is a strong edge
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: a bilateral filter keeps a one-pixel outlier for the same reason it keeps an edge
- Technical source: Worked example, "The bilateral filter: weight by value", Figure 1 and the scorecard
- Visual structure: lockup and counter; serif title; deck; a panel with two 5×5 grids side by side, the patch and its bilateral-filtered version, the bright pixel outlined in the accent in both; three lines of results under the grids; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · A bright pixel is a strong edge. · One 5×5 patch: an edge of 160 and one pixel 215 above its neighbours. Then a bilateral filter. · the patch · grid: every row 40 40 40 200 200, with 255 at row 2, column 1 · bilateral filter, σr = 80 · grid rows: 40 40 46.5 193.5 200; 40.7 40.8 47.5 193.5 200; 41.9 240.5 48.8 193.5 200; 40.7 40.8 47.5 193.5 200; 40 40 46.5 193.5 200 · edge 40 | 200 → 46.5 | 193.5: 92% kept · bright pixel 255 → 240.5: 93% kept · the Gaussian would give 78.2 | 161.8 and 98.6 · Contrast cannot tell noise from an edge when the noise is the bigger jump. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: A 5×5 patch with an edge and one bright pixel, beside its bilateral-filtered version in which both survive almost unchanged.
- Long description: The series' 5×5 patch has a step from 40 to 200 between its third and fourth columns and one bright pixel of 255 among 40s. A bilateral filter with the series' 3×3 Gaussian as its spatial kernel and a range width of 80 grey levels turns the step's two sides into 46.5 and 193.5, keeping 92% of its height, and lowers the bright pixel only to 240.5, keeping 93% of its height. A plain Gaussian blur would have given 78.2 and 161.8 for the step and 98.6 for the pixel. The takeaway: a filter that weighs neighbours by how similar their values are treats a one-pixel outlier as a strong edge, so it cannot remove impulse noise while keeping edges.
- Keywords: bilateral filter, edge-preserving smoothing, impulse noise, hot pixel, range kernel, image denoising
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### feed-02-weight-by-value

- File: `assets/social/feed-02-weight-by-value.png`
- Title: Weight by value, and the bright pixel wins
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the range weight falls with the difference, so the bright pixel's neighbours count less than the edge's
- Technical source: Worked example, range-weight table; "How does the bilateral filter choose its weights?", Figure 5
- Visual structure: lockup and counter; serif title; deck; a panel with four labelled horizontal bars for differences 0, 20, 160 and 215 and their weights, then three result lines; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Weight by value, and the bright pixel wins. · A neighbour keeps e^(−Δ²/2σr²) of its weight. The bright pixel is the bigger difference. · weight kept for a difference Δ, σr = 80 · Δ = 0, alike 1.000 · Δ = 20, a small bump 0.969 · Δ = 160, across the edge 0.135 · Δ = 215, the bright pixel 0.027 · bright pixel: 255 → 240.5 · edge: 40 | 200 → 46.5 | 193.5 · a 60 among 40s → 45.6, as the Gaussian's 45.45 · Any σr that keeps the 160 edge keeps the 215 pixel harder. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: Bars of the bilateral range weight at σr = 80: 1.000 for no difference, 0.969 for 20, 0.135 for 160 and 0.027 for 215.
- Long description: The bilateral filter multiplies each neighbour's spatial weight by a range weight, the Gaussian of the difference in value, e to the minus difference squared over twice σr squared. With σr = 80 grey levels, a neighbour with the same value keeps all its weight, one that differs by 20 keeps 0.969, one across the patch's edge of 160 keeps 0.135 and one beside the bright pixel, 215 away, keeps 0.027. So the bright pixel stays at 240.5 and the edge becomes 46.5 and 193.5, while a small bump of 20 is smoothed to 45.6, almost exactly the Gaussian's 45.45. The takeaway: because the bright pixel is the bigger difference, any range width that keeps the edge keeps the pixel even more strongly.
- Keywords: bilateral filter, range weight, sigma color, contrast threshold, edge-preserving smoothing, impulse noise
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### feed-03-nl-means-asks-who-looks-like-me

- File: `assets/social/feed-03-nl-means-asks-who-looks-like-me.png`
- Title: NL-means asks who looks like me
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: non-local means compares whole patches, so the edge finds an exact copy and the bright pixel finds none
- Technical source: Worked example, "Non-local means: weight by neighbourhood", Figure 2
- Visual structure: lockup and counter; serif title; deck; a panel with two rows of paired 3×3 patches, the edge pixel's patch equal to its copy with d² = 0 and weight 1, and the bright pixel's patch unequal to its best flat match with d² = 5,136 and a tiny weight; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · NL-means asks who looks like me. · It compares whole 3×3 patches, not single values, with every pixel of the patch. · the edge pixel and its copy at (r4, c2) · patches 40 40 200 in each row, = · d² = 0 · weight 1 · the bright pixel and its best match · patch 40 40 40 / 40 255 40 / 40 40 40 ≠ flat patch of 40s · d² = 215² / 9 = 5,136 · weight 0.000003 at h = 20 · The edge repeats down its column. The bright pixel repeats nowhere. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: The edge pixel's 3×3 patch beside an identical copy, and the bright pixel's patch beside its best match, a flat patch 5,136 away.
- Long description: Non-local means weighs every candidate pixel by how alike the 3×3 patches around the two pixels are, measured as the mean squared difference d². The patch around the edge pixel at row 0, column 2 has an exact copy at row 4, column 2, so d² = 0 and the copy gets full weight; every close match has 40 at its centre, so the edge stays exact. The bright pixel's patch has no copy: its best matches are flat patches of 40 that differ only at the centre, d² = 215 squared over 9 = 5,136, which at h = 20 gives a weight of about 0.000003. The takeaway: the edge repeats down its column and the bright pixel repeats nowhere, so repetition can separate what contrast cannot.
- Keywords: non-local means, patch similarity, NL-means, image denoising, self-similarity, edge-preserving smoothing
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### feed-04-the-pixels-own-vote

- File: `assets/social/feed-04-the-pixels-own-vote.png`
- Title: 255 or 83: the pixel's own vote
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: whether non-local means removes the bright pixel depends on the weight its own patch gets
- Technical source: Worked example, NL-means; "Who gets the pixel's own vote", Figure 7; ledger L18, L44, L49
- Visual structure: lockup and counter; serif title; deck; a panel with two rows of five vote cells (255 and four 40s), the first row weighted 1 and 3e−6 with the result 255, the second row weighted equally with the result 83.0, then the arithmetic; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · 255 or 83: the pixel's own vote. · Its four best matches are flat 40s. What decides the outcome is how much it trusts itself. · own weight 1: OpenCV, scikit-image · 255 40 40 40 40 · 1 3e−6 3e−6 3e−6 3e−6 · → 255 · own weight = largest other: IPOL · 255 40 40 40 40 · equal equal equal equal equal · → 83.0 · (255 + 4 × 40) / 5 = 83.0; the edge stays exact either way · Same algorithm, one rule apart: the bright pixel survives, or loses 80% of its height. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: Two rows of five weighted votes: with its own weight 1 the bright pixel stays 255; with weights equalised it falls to 83.
- Long description: In non-local means a pixel's own patch always matches itself at distance zero. OpenCV and scikit-image give it weight 1, so on the series' patch the bright pixel's four best matches, flat patches of 40 weighted about 3 millionths each, cannot move it and it stays 255. The reference algorithm published on Image Processing On Line instead sets the pixel's own weight to the largest of the other weights, so five equal votes remain and the pixel becomes (255 + 4 × 40) / 5 = 83, while the edge stays exact under both rules. The takeaway: the same algorithm keeps the bright pixel or removes 80% of its height depending on one rule.
- Keywords: non-local means, self weight, IPOL, OpenCV fastNlMeansDenoising, scikit-image denoise_nl_means, rare patch effect
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### feed-05-four-faces-against-one

- File: `assets/social/feed-05-four-faces-against-one.png`
- Title: Perona–Malik: four faces against one
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: each face of the bright pixel conducts less than the edge's, but the pixel has four faces, so it drains first
- Technical source: Worked example, "Perona–Malik: three iterations", Figure 3; ledger L24, L25, L27
- Visual structure: lockup and counter; serif title; deck; a panel with the conductance formula and the two conductances, then a four-row table of iterations 0 to 3 with the bright pixel's value and the edge's two sides; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Perona–Malik: four faces against one. · The heat equation, with a conductance on every face that falls as the difference across it grows. · each face conducts g(s) = 1 / (1 + (s/80)²) · a step face: g(160) = 0.2 · a bright-pixel face: g(215) = 0.122, but four of them · ITERATION · BRIGHT PIXEL · EDGE, TOP ROW · 0 255 40 | 200 · 1 228.85 48 | 192 · 2 199.19 54.51 | 185.49 · 3 165.25 61.54 | 179.65 · λ = 1/4, K = 80, no flow through the border · Each bright-pixel face conducts less, but it has four. It drains first. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: Three Perona–Malik iterations: the bright pixel falls 255, 228.85, 199.19, 165.25 while the edge narrows from 40 | 200 to 61.54 | 179.65.
- Long description: Perona–Malik diffusion is the heat equation with a conductance on every face between neighbouring pixels, here g(s) = 1 / (1 + (s/80)²) for a difference s across the face, with time step 1/4 and no flow through the image border. A face of the patch's edge conducts g(160) = 0.2 and a face of the bright pixel g(215) = 0.122, less, but the bright pixel has four such faces. Over three iterations the bright pixel goes 255, 228.85, 199.19, 165.25 while the edge on the top row goes from 40 | 200 to 48 | 192, 54.51 | 185.49 and 61.54 | 179.65. The takeaway: diffusion judges contrast face by face, and the bright pixel drains first only because it has more faces.
- Keywords: Perona-Malik, anisotropic diffusion, conductance, heat equation, edge-stopping function, image smoothing
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### feed-06-diffusion-ends-at-the-mean

- File: `assets/social/feed-06-diffusion-ends-at-the-mean.png`
- Title: Diffusion ends at the mean
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: diffusion conserves brightness, so without a stopping time every feature flattens to the mean
- Technical source: "Why it needs a stopping time", Figure 9; ledger L30, L31, L35
- Visual structure: lockup and counter; serif title; deck; a panel with a line chart of contrast against iterations on a log axis, the bright pixel starting at 215 and the edge at 160, both reaching zero, then a note on the mean; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Diffusion ends at the mean. · The scheme conserves brightness, so the patch can only flatten to its average, 112.6. · contrast over iterations, K = 80 · 215 · 160 · 0 · bright pixel · edge · axis 0 1 3 10 30 100 · both reach 0: every pixel ends at 2,815 / 25 = 112.6 · The iteration count is a parameter: where you stop is the result. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: Contrast of the bright pixel and the edge over 100 Perona–Malik iterations: the pixel falls first, and both reach zero.
- Long description: Running Perona–Malik diffusion on the series' patch with K = 80 for 100 iterations, the bright pixel's contrast against its four neighbours falls from 215 to nearly zero within about five iterations, and the edge's contrast falls from 160 more slowly, reaching zero by about fifty. Because the scheme conserves total brightness, 2,815 grey levels over 25 pixels, every pixel ends at the patch mean, 112.6. The takeaway: diffusion has no end state but flat, so the number of iterations is as much a parameter as the conductance, and where you stop decides the result.
- Keywords: Perona-Malik, anisotropic diffusion, stopping time, conservation, scale space, image smoothing
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### feed-07-only-rank-and-repetition-win

- File: `assets/social/feed-07-only-rank-and-repetition-win.png`
- Title: Only rank and repetition win here
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: of six ways to smooth the patch, only the median and non-local means under the reference rule keep the edge and lower the bright pixel
- Technical source: Worked example, "The scorecard"; Figure 4
- Visual structure: lockup and counter; serif title; deck; a panel with a seven-row table of methods, the bright pixel's value and the edge's two sides, the median and the reference-rule NL-means rows tinted green; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Only rank and repetition win here. · Six ways to smooth the patch, and what each does to the bright pixel and the edge. · METHOD · BRIGHT PIXEL · EDGE, TOP ROW · input 255 40 | 200 · Gaussian, σ = 0.8 98.6 78.2 | 161.8 · median 3×3 40 40 | 200 · bilateral, σr = 80 240.5 46.5 | 193.5 · NL-means, own weight 1 255 40 | 200 · NL-means, IPOL's rule 83.0 40 | 200 · Perona–Malik, 3 iterations 165.2 61.5 | 179.7 · The median and IPOL's NL-means keep the edge and lower the bright pixel. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: A scorecard of six smoothing methods on the patch, with only the median and NL-means under IPOL's rule keeping the edge and lowering the pixel.
- Long description: Six ways to smooth the series' 5×5 patch compared on the bright pixel and on the edge's two sides in the top row. The Gaussian gives 98.6 for the pixel but blurs the edge to 78.2 | 161.8. The median gives 40 and keeps the edge at 40 | 200. The bilateral filter keeps the edge at 46.5 | 193.5 but also the pixel at 240.5. Non-local means with its own weight at 1 changes nothing; with the reference rule it gives 83.0 and keeps the edge exact. Three iterations of Perona–Malik give 165.2 and 61.5 | 179.7. The takeaway: only rank (the median) and repetition (non-local means under the reference rule) keep the edge and lower the bright pixel; the contrast-based methods cannot.
- Keywords: edge-preserving smoothing, median filter, bilateral filter, non-local means, Perona-Malik, Gaussian blur
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Edge-preserving smoothing, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four parts the article covers, and where to read it
- Technical source: the article's section structure and Figure 11
- Visual structure: lockup and counter; serif title; deck; a panel listing four topics, each with a short description and one result; takeaway; call to action with the article URL
- Visible-text transcript: Canery.in · 08 / 08 · Edge-preserving smoothing, by hand. · Bilateral, non-local means and Perona–Malik, all on one 5×5 patch. · the bilateral filter · weight by value · keeps the bright pixel: 240.5 · non-local means · weight by repetition · 83 or 255: the own-weight rule · Perona–Malik · heat with a brake on every face · ends at the mean, 112.6 · the tooling map · OpenCV, scikit-image, ITK, MedPy · d = 3 is five taps, not nine · The full walk-through, with every number worked by hand and the tooling map. · READ IT AT CANERY.IN/BLOGS/EDGE-PRESERVING-SMOOTHING
- Alt text: Four topics from the article: the bilateral filter, non-local means, Perona–Malik diffusion and the tooling map, with one result each.
- Long description: A summary card for the article Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion. The bilateral filter weighs neighbours by value and keeps the bright pixel at 240.5; non-local means weighs them by repetition, and its own-weight rule decides between 83 and 255; Perona–Malik diffusion is heat flow with a brake on every face and ends at the patch mean, 112.6; the tooling map covers OpenCV, scikit-image, ITK and MedPy, where for example OpenCV's bilateral filter with d = 3 uses a five-pixel disc rather than nine pixels. The call to action points to the full walk-through on Canery.
- Keywords: edge-preserving smoothing, bilateral filter, non-local means, Perona-Malik, OpenCV, scikit-image
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### story-01-a-bright-pixel-is-a-strong-edge

- File: `assets/social/story-01-a-bright-pixel-is-a-strong-edge.png`
- Title: A bright pixel is a strong edge
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: a bilateral filter keeps both the edge and the bright pixel
- Technical source: Worked example, "The bilateral filter: weight by value"; the scorecard
- Visual structure: lockup and counter; serif title; deck; row r2 of the patch as five large cells, then the same row after a bilateral filter, the bright pixel outlined in both; a caption; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · A bright pixel is a strong edge. · One 5×5 patch, one bilateral filter, by hand. · row r2 of the patch · 40 255 40 200 200 · after a bilateral filter, σr = 80 · 41.9 240.5 48.8 193.5 200 · the edge kept, and the bright pixel too · Contrast cannot tell noise from an edge when the noise is the bigger jump. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: The row 40 255 40 200 200 before and after a bilateral filter: 41.9 240.5 48.8 193.5 200, the edge and the bright pixel kept.
- Long description: Row r2 of the series' 5×5 patch holds both features: a bright pixel of 255 among 40s and a step from 40 to 200. After a bilateral filter with the series' 3×3 Gaussian and a range width of 80 grey levels, the row reads 41.9, 240.5, 48.8, 193.5, 200: the step is kept and so is the bright pixel. The takeaway: contrast cannot tell noise from an edge when the noise is the bigger jump.
- Keywords: bilateral filter, impulse noise, edge-preserving smoothing, hot pixel, image denoising
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### story-02-0-135-against-0-027

- File: `assets/social/story-02-0-135-against-0-027.png`
- Title: 0.135 against 0.027
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: a neighbour across the edge keeps five times the weight a neighbour of the bright pixel keeps
- Technical source: Worked example, range-weight table; Figure 1
- Visual structure: lockup and counter; serif title; deck; two large horizontal bars, across the edge 0.135 and beside the bright pixel 0.027, each with its value in large type; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · 0.135 against 0.027. · What a neighbour keeps of its weight, across the edge and beside the pixel. · weight a neighbour keeps, σr = 80 · across the edge (160) · 0.135 · beside the bright pixel (215) · 0.027 · The bright pixel is the bigger jump, so it is the better protected. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: Two bars of bilateral range weight at σr = 80: 0.135 for a neighbour across the edge, 0.027 beside the bright pixel.
- Long description: With a range width of 80 grey levels, a neighbour across the patch's edge, 160 away in value, keeps 0.135 of its spatial weight, while a neighbour of the bright pixel, 215 away, keeps only 0.027, five times less. The takeaway: the bright pixel is the bigger difference, so the bilateral filter protects it better than it protects the edge.
- Keywords: bilateral filter, range kernel, sigma color, edge-preserving smoothing, impulse noise
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### story-03-the-pixels-own-vote

- File: `assets/social/story-03-the-pixels-own-vote.png`
- Title: One rule: 255 or 83
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: non-local means keeps or removes the bright pixel depending on its own weight
- Technical source: "Who gets the pixel's own vote", Figure 7
- Visual structure: lockup and counter; serif title; deck; two rows of five vote cells with weights under them, the first giving 255 and the second 83.0; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · One rule: 255 or 83. · Non-local means, and how much a pixel trusts itself. · own weight 1 (OpenCV, scikit-image) · 255 40 40 40 40 · 1 3e−6 3e−6 3e−6 3e−6 · → 255 · own weight = largest other (IPOL) · 255 40 40 40 40 · equal equal equal equal equal · → 83.0 · IPOL caps the pixel's own weight. OpenCV and scikit-image do not. · EDGE-PRESERVING SMOOTHING · CANERY.IN
- Alt text: Five weighted votes twice: own weight 1 keeps the bright pixel at 255; equal weights take it to 83.
- Long description: The bright pixel's four best matches in non-local means are flat patches of 40. With its own weight at 1, as in OpenCV and scikit-image, their weights of about 3 millionths cannot move it and it stays 255. With its own weight capped at the largest of the others, as in the reference algorithm on Image Processing On Line, the five votes are equal and it becomes 83. The takeaway: one implementation rule decides whether non-local means removes an isolated outlier.
- Keywords: non-local means, self weight, IPOL, OpenCV, scikit-image, impulse noise
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Three ways to smooth without blurring
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the four ideas of the article and the link
- Technical source: the article's section structure
- Visual structure: lockup and counter; serif title; deck; a tinted panel listing four numbered points; takeaway; call to action pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Three ways to smooth without blurring. · Worked by hand on one 5×5 patch. · 1 bilateral: weight by value · 2 NL-means: weight by repetition · 3 Perona–Malik: heat with a brake · 4 the bright pixel: who keeps it · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: A numbered list of four points: bilateral weighs by value, NL-means by repetition, Perona–Malik is heat with a brake, and who keeps the pixel.
- Long description: The closing Story frame lists the article's four ideas: the bilateral filter weighs neighbours by value; non-local means weighs them by repetition; Perona–Malik diffusion is heat flow with a brake on every face; and the question of which method keeps the bright pixel. It points readers to the full walk-through on Canery through the link sticker.
- Keywords: edge-preserving smoothing, bilateral filter, non-local means, Perona-Malik, image processing
- Canonical URL: https://canery.in/blogs/edge-preserving-smoothing
