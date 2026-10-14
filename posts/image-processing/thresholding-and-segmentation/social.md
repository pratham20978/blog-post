---
social_schema: 2
canonical_url: "https://canery.in/blogs/thresholding-and-segmentation"
---

# Social publishing package — thresholding-and-segmentation

## LinkedIn post

Call OpenCV's threshold with the Otsu flag and you always get a number back. On a 5×5 patch with one clean step and one bright pixel it returns 40: the top of the dark spike, not the middle of the gap.

Worked by hand, the question is what the histogram has to look like before any threshold can work.

→ Otsu's method is 2-means on the histogram, solved by trying every cut. On the patch smoothed by OpenCV's 8-bit blur, the nine cuts score from 1,061.2 to 2,935.8, and the best one also minimises the within-class variance: the two always add up to 3,370.47.
→ Three standard rules print 105, 125 and 160 for that image and draw the same mask. The number is not the result; the split is.
→ Otsu's hidden model is two humps of similar size and spread. On a model histogram with a 1% object it cuts through the background and gets 43% wrong, where the best cut gets 0.01%.
→ Uneven light breaks every global cut: put the patch beside itself at a fifth of the light, and 40 is dark in one half and bright in the other. A local threshold works once its window is wider than the objects and narrower than the shading.
→ Watershed floods every regional minimum unless markers say otherwise: one hot pixel turns the patch's two regions into four.

Part 11 of Image Processing by Hand. Every number is worked on paper; nothing was run against an image.

## LinkedIn first comment

A threshold only decides; the histogram decides whether deciding can work. When it can't, decide locally, or by space with markers.

Read the full article on Canery: https://canery.in/blogs/thresholding-and-segmentation

## Instagram caption

Otsu always returns a number. Swipe through thresholding and segmentation worked by hand on one 5×5 patch: why Otsu is 2-means on the histogram, how nine cuts score and why the best one is also the tightest, three rules that print three numbers and draw one mask, the 1% object that Otsu cuts through the background, the separability score that reads 0.68 for a clean object and for hopeless overlap alike, one grey level with two meanings under uneven light, and the hot pixel that turns a two-region watershed into four.

Every number is worked from the article's own patch. Nothing was run against an image.

Link in bio.

#computervision #imageprocessing #opencv #segmentation #thresholding #python #scikitimage

## Shared feed order

1. `assets/social/feed-01-otsu-always-returns-a-number.png` — the patch's histogram and the smoothed patch's, each with the run of thresholds that splits it the same way and the value Otsu returns
2. `assets/social/feed-02-nine-cuts-one-winner.png` — Otsu's between-class variance for all nine cuts of the smoothed histogram, the winner highlighted
3. `assets/social/feed-03-three-numbers-one-mask.png` — Otsu 105, isodata 125 and triangle 160 inside one gap, and the single mask they all draw
4. `assets/social/feed-04-a-small-object.png` — a model histogram with a 1% object: Otsu's criterion peaks inside the background
5. `assets/social/feed-05-eta-twice.png` — η = 0.68 for a cleanly separable 5% object and for two overlapping humps
6. `assets/social/feed-06-one-value-two-meanings.png` — one row of the patch beside its shadowed copy, with Otsu's single cut and Sauvola's local thresholds
7. `assets/social/feed-07-one-hot-pixel-four-regions.png` — watershed on the patch's gradient: four regions with no markers, two with two markers
8. `assets/social/feed-08-read-the-article.png` — the four ideas of the post, and the CTA

## Instagram Story

- CTA: Why does Otsu return 40 on this patch? One 5×5 patch, worked by hand — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/thresholding-and-segmentation

### Story order

1. `assets/social/story-01-otsu-returned-40.png` — Overlay: Otsu returned 40, the top of the dark spike.
2. `assets/social/story-02-a-small-object.png` — Overlay: A 1% object, cut through the background.
3. `assets/social/story-03-the-label-crossed-the-step.png` — Overlay: cv2.watershed let the bright label in.
4. `assets/social/story-04-read-the-article.png` — Overlay: Thresholding and segmentation, by hand. Link below.

## Asset metadata

### feed-01-otsu-always-returns-a-number

- File: `assets/social/feed-01-otsu-always-returns-a-number.png`
- Title: Otsu always returns a number
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: on the patch, any threshold from 40 to 199 splits the histogram the same way and Otsu returns the first, 40; on the smoothed patch the run is 105 to 161 and it returns 105
- Technical source: Worked example, steps 1–3; Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with two histograms, each with its run of equivalent thresholds shaded and a line of numbers beneath; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Otsu always returns a number. · Whether any number can work is written in the histogram, before you call it. · the patch: 40, 200 and 255 · any t from 40 to 199 splits it the same way · returns 40 · smoothed, 8-bit: ten levels · any t from 105 to 161 · σB² 2,935.8 · returns 105 · A threshold works only when the two classes do not share grey levels. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: Two histograms of the 5×5 patch, raw and smoothed, each with the run of thresholds that splits it the same way shaded.
- Long description: The series' patch has three grey levels, 14 pixels at 40, 10 at 200 and 1 at 255, so every threshold from 40 to 199 gives the same split, and OpenCV's Otsu code returns the first of them, 40. Smoothed by OpenCV's 8-bit Gaussian blur, the patch has ten levels; the best split is any threshold from 105 to 161, with a between-class variance of 2,935.8, and OpenCV returns 105. The takeaway: a threshold works only when the two classes do not share grey levels.
- Keywords: Otsu threshold, histogram, between-class variance, OpenCV threshold, binarisation, image segmentation
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### feed-02-nine-cuts-one-winner

- File: `assets/social/feed-02-nine-cuts-one-winner.png`
- Title: Nine cuts, one winner
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the smoothed patch's ten levels give nine cuts; their between-class variances rise to 2,935.8 at the cut between 105 and 162, and with the within-class variance they always total 3,370.47
- Technical source: Worked example, steps 3–4; Figure 2
- Visual structure: lockup and counter; serif title; deck; a panel of nine horizontal bars labelled by cut with their values, the winner in orange; one line on the constant total; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Nine cuts, one winner. · The smoothed 5×5 patch has ten grey levels, so nine places to cut. σB² for each: · 40 | 64 1,061.2 · 64 | 67 1,402.4 · 67 | 78 1,802.5 · 78 | 90 2,153.9 · 90 | 94 2,445.7 · 94 | 99 2,611.9 · 99 | 105 2,777.0 · 105 | 162 2,935.8 · 162 | 200 1,821.6 · σB² + σW² = 3,370.47 on every row · The cut that pushes the class means apart is the cut that makes each class tightest. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: Nine bars of between-class variance for the nine cuts of the smoothed histogram, the cut between 105 and 162 highest.
- Long description: For each of the nine places to cut the smoothed patch's histogram, the bar shows the between-class variance: 1,061.2, 1,402.4, 1,802.5, 2,153.9, 2,445.7, 2,611.9, 2,777.0, then 2,935.8 at the cut between 105 and 162, the winner, and 1,821.6 at the last cut. On every row the between-class and within-class variances add up to the total, 3,370.47, so the cut that maximises one minimises the other.
- Keywords: Otsu's method, between-class variance, within-class variance, threshold selection, 2-means
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### feed-03-three-numbers-one-mask

- File: `assets/social/feed-03-three-numbers-one-mask.png`
- Title: 105, 125, 160: one mask
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Otsu, isodata and the triangle method return 105, 125 and 160 for the smoothed patch, all inside the empty gap, so all three draw the same mask
- Technical source: Worked example, step 5; Figure 3
- Visual structure: lockup and counter; serif title; deck; a panel with the histogram zoomed to 30–210, the gap shaded and three labelled threshold lines, and the 5×5 mask to the right; one line on the run; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · 105, 125, 160. · Otsu, isodata and the triangle method on the same smoothed patch print three numbers. · triangle 160 · isodata 125 · Otsu 105 · 40 80 120 160 200 · the mask, all three · grid: 40 40 78 162 200 / 64 67 90 162 200 / 94 99 105 162 200 / 64 67 90 162 200 / 40 40 78 162 200, columns 3 and 4 bright · the impulse, 99: dark · every threshold from 105 to 161 draws this mask · One mask. The split is the result; the number is only where it landed. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: The smoothed histogram's gap with thresholds 105, 125 and 160 inside it, and the one mask they all produce.
- Long description: On the patch smoothed by OpenCV's 8-bit blur, Otsu's method returns 105, the isodata rule 125 and OpenCV's triangle method 160. No pixel lies between 106 and 161, so all three thresholds give the same mask: only the last two columns, 162 and 200, are bright, and the blurred impulse, 99, is dark. The takeaway: the split is the result, and the number is only where in the gap a rule happened to land.
- Keywords: Otsu, isodata, Ridler-Calvard, triangle threshold, OpenCV THRESH_TRIANGLE, binary mask
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### feed-04-a-small-object

- File: `assets/social/feed-04-a-small-object.png`
- Title: A 1% object, 43% wrong
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: with a 1% object, Otsu's criterion has two peaks and the higher one, at 72, sits inside the background; the best cut, 130, gets 0.01% wrong
- Technical source: What does the histogram have to look like?; Figure 6
- Visual structure: lockup and counter; serif title; deck; a panel with a model histogram, the invisible object marked, Otsu's criterion beneath, and two cut lines labelled Otsu 72 and best 130; one line of error rates; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · A 1% object, 43% wrong. · Otsu's criterion has two peaks, and the higher one sits inside the background. · Otsu 72 · best 130 · the object, too small to see · σB² · 0 100 200 · Otsu: 43% wrong · best cut: 0.01% wrong · Below about a 2% object, Otsu cuts through the background. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: A model histogram with a 1% object: Otsu's cut at 72 splits the background; the best cut at 130 sits in the valley.
- Long description: A closed-form histogram of two equal-spread humps at 70 and 170, where the second covers only 1% of the pixels and is too small to see. Otsu's criterion has two peaks, a lower one at 118 in the valley and a higher one at 72 inside the background, so Otsu cuts the background in two and misclassifies 43% of the pixels; the best possible cut, at 130, misclassifies 0.01%. For these humps the jump happens once the object covers less than about 2% of the image.
- Keywords: Otsu limitations, small object thresholding, class imbalance, unimodal histogram, threshold selection
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### feed-05-eta-twice

- File: `assets/social/feed-05-eta-twice.png`
- Title: η = 0.68, twice
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Otsu's separability score reads 0.68 both for a 5% object that a cut separates almost perfectly and for two humps that overlap so much 15.9% is the best possible
- Technical source: What does the histogram have to look like?, "What η can and cannot say"; equation (3)
- Visual structure: lockup and counter; serif title; deck; a panel with two model histograms side by side, each with its η in orange and its error beneath; one line; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · η = 0.68, twice. · Otsu's separability score for a clean small object and for two hopelessly mixed humps. · a 5% object, cut cleanly · η = 0.68 · 0.05% wrong · two humps that overlap · η = 0.68 · 15.9% wrong at best · same score, opposite verdicts · η measures the variance a split explains, not whether a clean cut exists. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: Two model histograms, a small separated object and two overlapping humps, both scoring η = 0.68.
- Long description: Otsu offered η, the share of the total variance that the best two-class split explains, as a measure of separability, and MATLAB returns it from graythresh. A histogram with a 5% object well away from the background is cut with 0.05% error and scores 0.68; two equal humps that overlap so much that the best possible cut misclassifies 15.9% also score 0.68. η falls with class imbalance as well as with overlap, so it cannot say on its own whether a clean cut exists.
- Keywords: Otsu effectiveness metric, separability, graythresh, histogram bimodality, threshold quality
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### feed-06-one-value-two-meanings

- File: `assets/social/feed-06-one-value-two-meanings.png`
- Title: 40 is dark here and bright there
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: beside a copy at a fifth of the light, the value 40 is the dark class in one half and the bright class in the other, so Otsu's single cut at 51 gets 10 pixels wrong while Sauvola's window-7 thresholds get none
- Technical source: What if the light changes across the image?; Figure 7
- Visual structure: lockup and counter; serif title; deck; a panel with one row of ten bars, lit and shadowed halves divided, a dashed blue global cut, orange local thresholds on each bar, and blue crosses under the two pixels the global cut gets wrong; one line of counts; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · 40 is dark here and bright there. · The patch beside itself at a fifth of the light, one row of it. · lit · a fifth of the light · dark dark dark bright bright dark dark dark bright bright · global Otsu, 51 (blue): 10 wrong · Sauvola, window 7 (orange): 0 wrong · Threshold locally: a window wider than the objects and narrower than the shading. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: One row of the lit and shadowed patch: a single cut at 51 misses the shadowed bright pixels; local thresholds do not.
- Long description: The patch placed beside a copy of itself at a fifth of the light reads 40 40 40 200 200 then 8 8 8 40 40 along a row, so the value 40 means dark in the lit half and bright in the shadowed half. Otsu's global threshold, 51, calls the shadowed bright pixels dark and gets 10 of the image's pixels wrong. Sauvola's local threshold with a 7 × 7 window, wide enough to reach across every step, adapts to each half and gets none wrong.
- Keywords: adaptive thresholding, Sauvola, uneven illumination, local threshold, document binarisation, OpenCV adaptiveThreshold
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### feed-07-one-hot-pixel-four-regions

- File: `assets/social/feed-07-one-hot-pixel-four-regions.png`
- Title: One hot pixel, four regions
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: with no markers, watershed on the patch's gradient floods its four regional minima into four regions; with two hand-drawn markers it gives two, split at the step
- Technical source: Worked example, steps 6–7; Figures 4 and 5
- Visual structure: lockup and counter; serif title; deck; a panel with two 5×5 label maps side by side, four colours on the left and two on the right with the markers outlined; one line on the cause; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · One hot pixel, four regions. · Watershed on the patch's gradient floods every regional minimum unless you say otherwise. · no markers · grid: 1 1 1 2 2 / 1 1 3 2 2 / 3 3 3 2 2 / 4 3 3 2 2 / 4 4 4 2 2 · 4 regions · two markers, drawn by hand · grid: 1 1 1 2 2 on every row · 2 regions · the impulse's ring cuts the dark side's flat zeros in three · Markers decide which minima are the same object. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: Two label maps of the patch: four regions from watershed without markers, two with two hand-drawn markers.
- Long description: The patch's Sobel gradient has four regional minima: the top-left pair, the bottom-left pair, the bright column and the impulse's own pixel, whose ring of high gradient cuts the dark side's flat zeros into three. Watershed without markers gives each minimum a region, four in all; with one marker drawn on each side it gives two regions split exactly at the step. The takeaway: markers decide which minima belong to the same object.
- Keywords: watershed segmentation, over-segmentation, regional minima, markers, scikit-image watershed
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Thresholding and segmentation, by hand
- Platforms: Instagram feed, LinkedIn
- Role: CTA
- Dimensions: 1080×1350
- Narrative beat: the four ideas of the post, and where to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel of four headed items, the last in orange; takeaway; CTA footer
- Visible-text transcript: Canery.in · 08 / 08 · Thresholding and segmentation, by hand. · Otsu, Sauvola and watershed on one 5×5 patch. · Otsu · 2-means on the histogram · best only for two humps of like size and spread · η · variance explained · not separability: 0.68 twice · local · a threshold per window · wider than objects, narrower than shading · watershed · a flood from markers · every unmarked minimum becomes a region · The full walk-through, every number worked by hand, and the tooling map. · READ IT AT CANERY.IN/BLOGS/THRESHOLDING-AND-SEGMENTATION
- Alt text: A summary card listing Otsu, η, local thresholds and watershed, each with one line on what it does and when it fails.
- Long description: The closing card restates the post in four lines. Otsu's method is 2-means on the histogram and is the best cut only for two humps of similar size and spread. η measures the variance a split explains, not separability, and reads 0.68 for opposite cases. Local thresholds need a window wider than the objects and narrower than the shading. Watershed floods from markers, and every unmarked minimum becomes a region. It ends with the article's address.
- Keywords: thresholding, image segmentation, Otsu, Sauvola, watershed, Canery
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### story-01-otsu-returned-40

- File: `assets/social/story-01-otsu-returned-40.png`
- Title: Otsu returned 40
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: on the patch, Otsu's threshold sits at the top of the dark spike rather than in the middle of the gap, so reusing it on a noisier frame misclassifies dark pixels
- Technical source: Worked example, step 1; Limitations and common mistakes
- Visual structure: lockup and counter; serif title; deck; the patch's histogram with the equivalent run shaded and a line marked "returns 40"; two lines beneath; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Otsu returned 40. · The top of the dark spike, not the middle of the gap. · the patch's histogram: 40, 200, 255 · returns 40 · any t from 40 to 199 splits it the same way · and Otsu returns the first of them · Reuse that number on a noisy frame and a dark pixel at 42 turns bright. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: The patch's three-spike histogram with Otsu's returned threshold, 40, on the edge of the dark spike.
- Long description: The patch's histogram has spikes at 40, 200 and 255. Every threshold from 40 to 199 splits it the same way, and OpenCV's own Otsu code returns the first, 40, which sits on top of the dark spike instead of in the middle of the empty gap. Reused on another frame where noise lifts a dark pixel to 42, that threshold calls the pixel bright.
- Keywords: Otsu threshold value, threshold reuse, OpenCV, histogram gap
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### story-02-a-small-object

- File: `assets/social/story-02-a-small-object.png`
- Title: 43% wrong
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Otsu's cut on a histogram with a 1% object lands inside the background; the best cut, 130, gets 0.01% wrong
- Technical source: What does the histogram have to look like?; Figure 6
- Visual structure: lockup and counter; serif title; deck; a model histogram with the object marked and Otsu's criterion beneath, two labelled cut lines; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · 43% wrong. · Otsu's cut on a small object lands inside the background. · a histogram with a 1% object at 170 · Otsu 72 · best 130 · the object, too small to see · σB² · 0 100 200 · The best cut, 130, gets 0.01% wrong. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: A model histogram with a 1% object at 170: Otsu's cut at 72 inside the background, the best cut at 130.
- Long description: A closed-form histogram with a background hump at 70 and an object at 170 that covers 1% of the pixels. Otsu's criterion peaks at 72, inside the background, so the cut misclassifies 43% of the pixels, while the best possible cut, at 130 in the valley, misclassifies 0.01%.
- Keywords: Otsu failure, small objects, class imbalance, thresholding
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### story-03-the-label-crossed-the-step

- File: `assets/social/story-03-the-label-crossed-the-step.png`
- Title: Label 2 crossed the step
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: cv2.watershed with one marker pixel per region floods neighbour differences, so the bright label crosses the step at a cost of 160 before the dark label can pass the impulse at 215
- Technical source: What does each library's watershed flood?; Figure 8; exercise E4
- Visual structure: lockup and counter; serif title; deck; a large 5×5 label map with −1 cells hatched, the two markers outlined in blue and orange, and the two wrongly labelled dark pixels in dashed boxes; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Label 2 crossed the step. · OpenCV floods neighbour differences: the step costs 160, the impulse 215. · cv2.watershed, markers (r1, c1) and (r2, c3) · grid: −1 −1 −1 −1 −1 / −1 1 1 −1 −1 / −1 −1 −1 2 −1 / −1 2 2 2 −1 / −1 −1 −1 −1 −1 · Two dark pixels come back with the bright label. · THRESHOLDING AND SEGMENTATION · CANERY.IN
- Alt text: cv2.watershed's result on the patch with one-pixel markers: label 2 has spread into two dark pixels of the bottom row.
- Long description: Replayed from OpenCV's source, cv2.watershed on the patch with marker 1 at row 1, column 1 and marker 2 at row 2, column 3 sets the outer frame to −1, floods by the grey-level difference between neighbours, and turns pixels touching both labels into −1 boundaries. Crossing the step costs 160 while reaching past the impulse costs 215, so the bright label reaches the dark bottom row first and two dark pixels come back labelled 2.
- Keywords: cv2.watershed, OpenCV watershed markers, watershed boundary -1, marker-based segmentation
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Thresholding and segmentation
- Platforms: Instagram Story
- Role: CTA
- Dimensions: 1080×1920
- Narrative beat: the post's four steps in order, and the link
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel with four numbered lines, the last in bold; takeaway; CTA footer
- Visible-text transcript: Canery.in · 04 / 04 · Thresholding and segmentation. · Worked on one 5×5 patch. · 1 the histogram decides first · 2 Otsu: two humps of like size · 3 uneven light: threshold locally · 4 touching objects: watershed · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: A Story card listing four steps: histogram first, Otsu for two like humps, local thresholds, and watershed.
- Long description: The closing Story frame lists the post's argument in four steps: the histogram decides first whether a threshold can work; Otsu suits two humps of similar size and spread; uneven light needs a local threshold; touching objects need a watershed with markers. It points to the link sticker for the full article.
- Keywords: image segmentation, thresholding, Otsu, watershed, Canery
- Canonical URL: https://canery.in/blogs/thresholding-and-segmentation
