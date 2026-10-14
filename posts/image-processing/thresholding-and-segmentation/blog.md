---
title: "Thresholding and Segmentation: Otsu, Sauvola, Watershed"
slug: thresholding-and-segmentation
date: 2026-10-13
updated: 2026-10-13
summary: "A threshold works only when the histogram is two humps of like size and spread. Otsu, Sauvola and marker watershed, worked by hand on a tiny 5×5 patch."
tags: [algorithms, image-processing, thresholding, otsu, image-segmentation, watershed, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: intermediate
series: image-processing
series_position: 11
prerequisites: ["the shared 5×5 patch and the decide stage from part 1 of this series", "the mean and variance of a list of numbers", "reading Python signatures"]
reading_minutes: 31
cover_image_url: "COVER"
cover_image_alt: "A histogram with a dark hump and a bright hump split by one tangerine cut, above a 5×5 grid flooded from two markers into two regions"
canonical_url: "https://canery.in/blogs/thresholding-and-segmentation"
---

> [!NOTE]
> **Insights** — A global threshold can only separate classes whose grey levels do not overlap, and Otsu's method, which tries every cut and keeps the one with the largest between-class variance, is the best cut only when the histogram is two humps of similar size and spread: on model histograms it costs 4.8% error where 0.8% is possible once one hump is more than four times wider, and below a 2% object it cuts through the background. Uneven light needs a local threshold, with a window wider than the objects and narrower than the shading; touching objects of one grey level need a watershed flooded from markers. On the series' 5×5 patch, three standard rules print 105, 125 and 160 for one smoothed image and draw the same mask, and one hot pixel turns a two-region watershed into four.

**Level:** intermediate · **You need:** *Image Processing by Hand* (part 1 of this series) for the shared patch and the decide stage, the mean and variance of a list of numbers, and enough Python to read a signature · **Time:** ~31 min

This is part 11 of *Image Processing by Hand*. Part 1 stated Otsu's criterion in its decide stage, called it a search over 256 candidates, and named this post for the rest: when a threshold can work, what to do when it cannot, and segmentation by marker-based watershed. <!-- L58 --> The watershed below floods the Sobel magnitudes that Part 8, *Canny Edge Detection, Line by Line: Setting the Thresholds*, worked out for the same patch.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Histogram shapes](#what-does-the-histogram-have-to-look-like) · [Uneven light](#what-if-the-light-changes-across-the-image) · [Library watersheds](#what-does-each-librarys-watershed-flood) · [Markers](#why-does-watershed-over-segment-and-where-do-markers-come-from) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch, or evaluated from a closed form, and cross-checked with plain Python using only its `math`, `heapq` and `collections` modules; that check is not published. No OpenCV, scikit-image or MATLAB call was executed: library behaviour comes from source read at pinned commits, replayed in that plain Python, and from MathWorks' documentation. There are no timings or measured curves. The histograms in Figure 6 are mixtures of normal distributions evaluated in closed form, and the caption says so.

## Why this matters

Call `cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)` and you always get a number back. Nothing in the call says whether any number could have worked. On a page lit from one side, on a speck that covers 1% of the frame, or on two coins that touch, Otsu's method returns a threshold as calmly as it does on a clean two-humped histogram, and the mask comes out wrong in a way no threshold can fix.

Watershed fails just as quietly. On the series' 5×5 patch, one bad pixel turns a two-region answer into four. This post works out what the histogram has to look like before a threshold can work at all, and what to use when it cannot: a local threshold when the light changes, and a watershed with markers when only space separates the objects.

## The problem

A **global threshold** turns a grey image into a binary one, **binarisation**, with one comparison per pixel. OpenCV writes `maxval` where the pixel is greater than the threshold t and 0 elsewhere, so a pixel equal to t goes to the dark side. <!-- L36 --> Because the answer at a pixel depends only on its value, the threshold sees nothing but the image's **histogram**, the count of pixels at each grey level.

**Segmentation** is the larger job: split the image into regions, each meant to be one object or the background. A threshold is the simplest segmentation. It decides each pixel's class, and the regions are whatever connected groups of each class come out.

That gives the condition for a threshold to work. If the two classes occupy separate ranges of grey level, some t lies between them and every pixel is classed correctly. If any grey level occurs in both classes, every t gets some pixels wrong. Three things break a threshold in practice:

- **Mixed pixels.** Blur and noise put values between the classes, so the histogram's valley fills in.
- **Unequal humps.** A gap may exist, but a small object or a widely spread class moves where it lies, and a rule that assumes equal humps misses it.
- **Uneven light.** The same surface reads darker in shadow, so a bright object in shadow can share grey levels with a dark one in the light.

A fourth case is sameness, not overlap: two touching coins have one grey level, and only the thin edge between them says there are two. No histogram separates them. So the problem has two halves: how to choose t from the histogram and tell whether a good t exists, and what to do when none does, deciding locally or by space.

## Worked example

The patch is the series' 5×5 8-bit patch: every row is `40 40 40 200 200` except r2, which has an impulse of 255 at (r2, c1).

```text
      c0   c1   c2   c3   c4
r0    40   40   40  200  200
r1    40   40   40  200  200
r2    40  255   40  200  200
r3    40   40   40  200  200
r4    40   40   40  200  200
```

### Step 1: the patch's own histogram

The histogram has three spikes: 14 pixels at 40, 10 at 200 and 1 at 255, with mean 2,815 / 25 = 112.6. A threshold anywhere from 40 to 199 splits them the same way, 14 dark against 11 bright.

The **between-class variance** scores a split. With $\omega_0$ and $\omega_1$ the fractions of pixels in the two classes and $\mu_0$ and $\mu_1$ their means, $\sigma_B^2 = \omega_0\,\omega_1\,(\mu_1 - \mu_0)^2$. Here $\omega_0$ = 0.56 with $\mu_0$ = 40, and $\omega_1$ = 0.44 with $\mu_1$ = (10 × 200 + 255) / 11 = 205, so $\sigma_B^2$ = 0.56 × 0.44 × 165² = 6,708.24. **Otsu's method** computes this for every possible threshold and keeps the largest. <!-- L01 --> The only other split, 200 against 255, scores 844.9.

The total variance of the 25 values is 6,818.24, so the best split explains 98.4% of it. That ratio, **η** = $\sigma_B^2 / \sigma_T^2$, is Otsu's measure of separability: 1 only for an image with two grey levels, 0 only for one with a single level. <!-- L04 --> The criterion is flat from 40 to 199, as Part 1 found, and OpenCV's own code returns the first level of the flat run, 40, <!-- L37 --> on top of the dark spike rather than in the middle of the gap. The mask has 11 bright pixels, one of them the impulse, a lone speck in the dark half.

### Step 2: blur it, as optics would

A real image has **mixed pixels**, values between the classes where blur averages across an edge. Smooth the patch with the series' 3×3 Gaussian, σ = 0.8. On an 8-bit image OpenCV's `GaussianBlur` works in fixed point: it rounds the weights to 1/256ths, [61, 134, 61] / 256, and rounds the result half up. <!-- L46 --> That moves two values from what the exact weights give: 64.415 rounds to 64 where 64.561 would round to 65, and 90.332 to 90 where 90.520 would give 91. Part 7, *Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion*, worked the exact-weight values. OpenCV returns:

```text
      c0   c1   c2   c3   c4
r0    40   40   78  162  200
r1    64   67   90  162  200
r2    94   99  105  162  200
r3    64   67   90  162  200
r4    40   40   78  162  200
```

The histogram now has ten levels: 40 four times, 64, 67, 78 and 90 twice each, 94, 99 and 105 once, 162 five times and 200 five times. The step's two sides spread to 78 and 162, and the impulse spreads into a bump of 64 to 105 in the dark half.

### Step 3: every cut, by hand

Ten levels give nine places to cut. For each one, count the pixels on each side, take each side's mean, and score the split:

| cut between | dark pixels | $\mu_0$ | $\mu_1$ | $\sigma_B^2$ | $\sigma_W^2$ |
|---|---|---|---|---|---|
| 40 and 64 | 4 | 40.00 | 128.86 | 1,061.2 | 2,309.3 |
| 64 and 67 | 6 | 48.00 | 135.68 | 1,402.4 | 1,968.1 |
| 67 and 78 | 8 | 52.75 | 143.76 | 1,802.5 | 1,567.9 |
| 78 and 90 | 10 | 57.80 | 152.53 | 2,153.9 | 1,216.6 |
| 90 and 94 | 12 | 63.17 | 162.15 | 2,445.7 | 924.8 |
| 94 and 99 | 13 | 65.54 | 167.83 | 2,611.9 | 758.6 |
| 99 and 105 | 14 | 67.93 | 174.09 | 2,777.0 | 593.4 |
| **105 and 162** | **15** | **70.40** | **181.00** | **2,935.8** | **434.7** |
| 162 and 200 | 20 | 93.30 | 200.00 | 1,821.6 | 1,548.9 |

Take the winning row. The 15 dark pixels sum to 4 × 40 + 2 × 64 + 2 × 67 + 2 × 78 + 2 × 90 + 94 + 99 + 105 = 1,056, a mean of 70.4. The 10 bright ones average (5 × 162 + 5 × 200) / 10 = 181. So $\sigma_B^2$ = (15/25)(10/25)(181 − 70.4)² = 0.24 × 12,232.36 = 2,935.77. Every threshold from 105 to 161 makes this split, and OpenCV returns 105. The best split explains η = 0.871 of the variance, down from 0.984: the mixed pixels have filled part of the valley. Figure 1 shows both histograms and the score at every cut.

![Two histograms with Otsu's score above: the raw patch scores flat from 40 to 199, the smoothed patch peaks at the cut after 105](FIG_01)

*Figure 1 — Otsu's criterion over two real histograms. The raw patch's score is flat across its whole gap, so any threshold there is "the" answer; the smoothed patch's score rises to one peak, the cut between 105 and 162. Computed from the definition.*

### Step 4: the same answer from the other side

The last column is the **within-class variance**, $\sigma_W^2 = \omega_0\sigma_0^2 + \omega_1\sigma_1^2$, the average spread inside the two classes. At the winning cut the dark class has variance 483.84 and the bright class 361, so $\sigma_W^2$ = 0.6 × 483.84 + 0.4 × 361 = 434.70.

Add the two columns on any row and you get 3,370.47, the total variance of the 25 values. That holds for any split: the total spread is the spread within the classes plus the spread between their means. <!-- L01 --> So the cut that maximises $\sigma_B^2$ is the cut that minimises $\sigma_W^2$, and Otsu's method reads either way, as pushing the class means apart or as making each class as tight as possible. Figure 2 shows it.

![Nine stacked bars of equal height 3,370.47; the tallest between-class part sits on the shortest within-class part, the cut at 105](FIG_02)

*Figure 2 — At every cut the two variances add up to the same total, so the largest $\sigma_B^2$ and the smallest $\sigma_W^2$ are the same cut. Computed from the smoothed patch's histogram.*

### Step 5: three rules, three numbers, one mask

Two other standard rules give different numbers for the same image. The **isodata** rule, also called Ridler–Calvard, looks for a threshold that sits halfway between the means of the two classes it makes; scikit-image returns the lowest such t, here 125, close to (70.4 + 181) / 2 = 125.7. <!-- L49 --> The **triangle method** draws a line from the histogram's highest bar to the far end of its longer tail and cuts where the histogram falls furthest below that line. <!-- L41 --> <!-- L50 --> Both libraries take the first of its two tallest bars, the five pixels at 162, and the method returns 160 in OpenCV, 161 in scikit-image.

So the same image gets 105, 125 and 160. No pixel lies between 106 and 161, so any threshold from 105 to 161 makes the same split, and all three draw the same mask, as Figure 3 shows. The impulse, bright in the raw patch's mask, is now dark: smoothing spread it to 105, below the gap. On the raw patch the three rules return 40, 122 and 42 (41 in scikit-image), again one mask.

![The smoothed histogram's gap holding thresholds 105, 125 and 160, beside the raw mask with the impulse bright and the smoothed one](FIG_03)

*Figure 3 — The number a threshold rule prints is not the result; the split is. Three rules land in one gap and draw one mask; smoothing first moved the impulse to the dark side. Worked by hand.*

### Step 6: flood the gradient from two markers

A threshold looks at values. **Watershed** looks at space. It is usually run on the gradient magnitude rather than the image, <!-- L26 --> read as a landscape with edges as ridges and flat areas as valleys, and it floods that landscape. Use the patch's Sobel magnitude from Part 8, which is what scikit-image's `sobel` returns up to a constant factor: <!-- L52 -->

```text
        c0      c1      c2      c3    c4
r0       0       0     640     640     0
r1   304.1     430   476.3     640     0
r2     430       0     210     640     0
r3   304.1     430   476.3     640     0
r4       0       0     640     640     0
```

Now draw two **markers** by hand: label (r0, c0) as region 1 and (r2, c4) as region 2. A marker is just a set of pixels declared to belong to one region. <!-- L24 --> Flooding takes the unlabelled pixels next to labelled ones, lowest relief first, and each joins the neighbour that reached it.

The water rises through five levels. At 0, region 1 takes (r0, c1) and region 2 the whole column c4. At 304.1, region 1 crosses into (r1, c0). At 430 it reaches the ring round the impulse, and through it the impulse's own 0 and the bottom-left pair, which flood at 430 because the water had to climb a 430 rim to reach them. At 476.3 it takes (r1, c2) and (r3, c2). Only at 640, the step, do the regions meet: region 1 takes the rest of c2 and region 2 all of c3. The split is the step, c0 to c2 against c3 and c4, with the impulse inside the dark region, as Figure 4 shows level by level.

![Five grids flooding the patch's gradient from two markers at levels 0, 304.1, 430, 476.3 and 640, ending in two regions at the step](FIG_04)

*Figure 4 — Flooding from two hand-drawn markers. The impulse is a pit inside a 430 rim, and the dark region fills it long before the 640 ridge of the step, where the two regions meet. Worked by hand; scikit-image's queue rule.*

### Step 7: over-segment on purpose

Now leave the markers out. scikit-image then uses every **regional minimum** of the relief as a marker: a flat set of pixels whose neighbours are all higher. <!-- L53 --> This relief has four: the top-left pair (r0, c0) and (r0, c1), the bottom-left pair, the bright column c4, and the impulse itself, whose own gradient is 0 inside its ring. Four minima give four regions:

```text
      c0   c1   c2   c3   c4
r0     1    1    1    2    2
r1     1    1    3    2    2
r2     3    3    3    2    2
r3     4    3    3    2    2
r4     4    4    4    2    2
```

The impulse cost two extra regions. Without it, the dark side's gradient would be 0 across c0 and c1 on every row, one flat valley and one region. Its ring of 304.1 to 476.3 cuts that valley into a top pair, a bottom pair and the impulse's own pit, as Figure 5 shows. With 8-connectivity, where diagonal neighbours count too, the regions change shape but there are still four. In floating point, ring values that are equal here can differ in the last digit, which can move the boundaries between the three dark regions again; it cannot change the count.

![The relief's four regional minima and the four regions they flood into: the impulse's ring cuts the dark side in three](FIG_05)

*Figure 5 — One hot pixel, four regions. Every regional minimum becomes a region unless something says otherwise, and the impulse makes three minima out of one flat valley. Worked by hand on exact values.*

| run | regions | the impulse |
|---|---|---|
| Otsu, raw patch | 2 classes | a separate bright speck |
| Otsu, isodata or triangle, smoothed | 2 classes | absorbed into the dark class |
| watershed, two markers | 2 | absorbed into the dark region |
| watershed, no markers | 4 | a region of its own |

## Intuition

Otsu's method is sorting pebbles into two piles with a single cut by weight, choosing the cut that makes each pile as uniform as possible. That is exactly what **k-means** clustering does with two clusters, and its objective is the same within-class variance. <!-- L15 --> The difference is the search: k-means moves the cut back and forth until it settles, and can settle in the wrong place, while Otsu tries every cut, so on a histogram it finds the best one. <!-- L15 --> At the best cut the threshold sits halfway between the two class means, which is why the isodata rule, which hunts for exactly that midpoint, landed in the same gap.

The analogy breaks at what the piles mean. A cut that makes two uniform piles need not separate two kinds of pebble: if one kind is rare, the tidiest split may cut the common kind in two. Nothing in the criterion knows which pixels belong together, only how spread out the values are.

Watershed is the landscape picture made literal. The gradient is a terrain, every pixel's height its edge strength; edges are ridges and flat regions are valleys. A marker is a spring you choose. Water from each spring fills its valley, spills over the lowest rim into the next, and where two springs' water would meet, a dam goes up. Every valley you do not give a spring is filled by whichever spring reaches its rim first.

This analogy breaks at flat ground and ties. Real water fills a flat valley all at once, but a program visits pixels one at a time, and when two pixels are at the same height the order it visits them decides who gets them. The watershed on the patch gave (r1, c1) to the top-left region and (r3, c1) to the impulse's region, though both sit at 430, purely because of the order the markers were queued in.

## What does the histogram have to look like?

Otsu's paper starts from the ideal: a deep, sharp valley between two peaks, which a broad valley or very unequal peaks make hard to find. <!-- L06 --> Start with the floor. If two classes overlap in grey level, even the best threshold misclassifies the overlap. For two humps of equal size and the same spread σ, with their means d σ apart, the best cut is the midpoint and it misclassifies Φ(−d/2) of the pixels, where Φ is the normal distribution's cumulative probability. That is 15.9% when the humps are 2σ apart, 6.7% at 3σ, 2.3% at 4σ, 1.0% at 4.65σ and 0.1% at 6σ. Below about 4σ, even the best global threshold gets more than 2% wrong.

### What Otsu assumes

Kurita, Otsu and Abdelmalek showed what each criterion assumes by deriving them all as maximum-likelihood fits of the histogram to a mixture of two normal distributions, as Ershov and colleagues summarise their result. Equal weights and equal variances give Otsu's criterion. Free weights and free variances give the minimum-error method of Kittler and Illingworth. Free weights with equal variances give an "unbalanced" Otsu. <!-- L13 --> <!-- L10 --> So Otsu's method is the right cut when the histogram is two humps of similar size and similar spread, and Sezgin and Sankur's survey says the same in practical terms: it does well when the classes have similar pixel counts. <!-- L09 -->

Figure 6 tests that in closed form, with four model histograms and both Otsu's cut and the best possible cut computed exactly:

- **Equal humps** (means 70 and 170, σ = 15 each): Otsu cuts at 120, the best cut is 119, and both misclassify 0.04%.
- **Unequal spreads** (σ = 8 against σ = 35): Otsu cuts at 124, near the midpoint of the means, which is deep in the wide hump's tail. It misclassifies 4.8%, where a cut at 92 would misclassify 0.8%.
- **Unequal sizes** (a 1% object): the criterion has two peaks, at 118 in the valley and at 72 inside the background, and the background one is higher. Otsu cuts through the background and misclassifies 43%, where 0.01% is possible. For these humps the jump happens once the object covers less than about 2.0% of the image.
- **Overlap** (means 100 and 150, σ = 25): Otsu and the best cut agree, at 125 and 124, and both misclassify 15.9%. Nothing does better; the histogram has no valley to find.

![Four model histograms: equal humps cut well; unequal spreads 4.8% against 0.8%; a 1% object cut through; overlap 15.9% for both](FIG_06)

*Figure 6 — Otsu's cut is the best cut only for its own model, two humps of equal size and spread. Model histograms: mixtures of two normal distributions binned to 0–255, evaluated in closed form; the criterion is drawn under each.*

### What η can and cannot say

Otsu offered η at the best cut as a measure of separability, and MATLAB returns it as `graythresh`'s effectiveness metric. <!-- L04 --> <!-- L55 --> It measures how much of the variance a two-class split explains, and that depends on class sizes as well as on overlap. A 5% object with the same humps as the first panel is cut almost perfectly, 0.05% wrong, and scores η = 0.68; the overlapping humps, where 15.9% is the best anyone can do, also score 0.68. A low η says "look at the histogram", not "give up".

Three humps are a different shape again. With three equal-spread humps at 50, 128 and 206, Otsu's criterion has two equal peaks, at 112 and 143, and which one wins can flip with a tiny change to the histogram. Otsu reported his criterion as smooth and single-peaked in his examples, but he had no proof, and it is not true in general. <!-- L07 --> He also gave the fix: search two thresholds at once for three classes, with the warning that the thresholds become less reliable as classes are added. <!-- L05 -->

### Picking a rule from the shape

Sezgin and Sankur sort thresholding methods into six families by the information they use, and the first family reads the histogram's shape. <!-- L08 --> The shape is also the quickest guide to a rule:

- Two humps of similar size and spread: Otsu, or isodata, which lands in the same gap.
- Two humps of different spread: a minimum-error fit such as Kittler–Illingworth, which ranked first among 40 methods on both of the survey's image sets. <!-- L11 --> Ershov and colleagues note it is also known to be unstable, with more parameters than a histogram can pin down. <!-- L14 -->
- One hump and a long tail, as for a small bright object: the triangle method, which is built for that shape.
- Three or more humps: multi-level Otsu.

No rule wins everywhere. On the survey's 40 degraded documents Otsu ranked 17th of 40 and Sauvola's local method second; on its 40 non-destructive-testing images Otsu ranked sixth and Sauvola 38th. <!-- L11 --> The image decides.

## What if the light changes across the image?

Put the patch next to a copy of itself at a fifth of the light, as if half the scene were in shadow. The shadowed copy reads 8 where the patch reads 40, 40 where it reads 200, and 51 for the impulse:

```text
r0    40   40   40  200  200  |   8    8    8   40   40
r2    40  255   40  200  200  |   8   51    8   40   40
```

The value 40 is now the dark class on the left and the bright class on the right. No global threshold can be right: whichever side of 40 the cut falls, at least ten pixels are wrong. Otsu cuts at 51, calls the shadowed bright side dark, and gets those ten wrong.

A **local threshold** gives every pixel its own threshold, computed from a window around it. OpenCV's `adaptiveThreshold` uses the window's mean minus a constant C. <!-- L42 --> Niblack's method uses the mean plus k times the window's standard deviation, with k negative. <!-- L16 --> Sauvola's method multiplies the mean by 1 + k(s/R − 1), where s is the window's standard deviation and R its largest expected value; the paper used R = 128 and k = 0.5 for 8-bit images. <!-- L17 -->

On this image the window size decides everything, as Figure 7 shows along row r0.

- **Window 3 fails.** The dark side is three pixels wide, so some windows hold only one value. A flat window carries no evidence, and each method then falls back on a fixed rule. Mean − C with C = 0 calls a flat window dark, so it gets the shadowed bright column c9 wrong; a positive C would call every flat window bright instead. Sauvola's threshold in a flat window is (1 − k) times the mean, half the mean here, so it calls flat windows bright and gets c0, c1 and c6 wrong. Over the whole image mean − C, Niblack and Sauvola make 5, 5 and 8 errors.
- **Window 7 works.** Every window now reaches across the step: from c0, three pixels either side is enough to see c3. All three methods make no errors. Window 5 also makes none, but not for the right reason: a 5-wide window centred on c0 still never reaches the step, and Sauvola gets c0 right only because the impulse falls inside that window. Without the impulse it would call c0 bright.
- **Window 9 fails again for mean − C.** At c8 the window reaches back into the lit copy's 200s, the mean rises to 48, and the shadowed 40 there is called dark: five errors, one per row. The window has started to see the other light.

![One row of the lit and shadowed patch with Otsu's cut at 51 and local thresholds at windows 3, 7 and 9; crosses mark wrong pixels](FIG_07)

*Figure 7 — One row, two lights. Otsu's one cut cannot serve both copies; a local threshold works once its window reaches across the dark region and before it reaches the other light. Computed from the definitions.*

So the rule for local thresholds is a window larger than the objects and smaller than the distance over which the light changes. Sauvola's form adds an assumption: in a flat window its threshold drops to (1 − k) times the mean, so plain background stays background, which suits dark text on light paper. <!-- L18 --> For bright objects on dark, invert the image first.

Two cautions about the name. scikit-image's `threshold_sauvola` defaults to k = 0.2, R = 127.5 for 8-bit images and a 15 × 15 window, not the paper's values. <!-- L51 --> And the paper first classifies each 10 to 20 pixel tile as text or not and treats the rest differently; libraries implement only the text formula. <!-- L19 --> The survey's document ranking also left out uneven illumination, the case local methods exist for. <!-- L12 -->

## What does each library's watershed flood?

"Watershed" names several algorithms. Vincent and Soille defined it by immersion: pierce every regional minimum, lower the landscape into water, and build a dam wherever water from two minima would meet. <!-- L20 --> Their algorithm sorts the pixels by height and floods level by level with a first-in, first-out queue. <!-- L21 --> Roerdink and Meijster's survey found that definitions, specifications and implementations often disagree. That algorithm does not implement its own definition, results on flat ground depend on the order pixels are processed, and changing the connectivity changes the result. <!-- L27 --> <!-- L29 --> <!-- L30 --> <!-- L31 --> The patch shows the last of these: with 4-connectivity the impulse's pit has a rim of 430, but with 8-connectivity the water can leave diagonally through (r1, c0), and the rim is 304.1.

The three libraries flood three different things:

- **scikit-image** floods whatever array you pass, normally a gradient, with 4-connectivity by default. Its queue orders pixels by height, then by arrival, and labels a pixel as soon as it is queued. <!-- L53 --> Since version 0.25.0 a queued pixel costs at least as much as the pixel that queued it, so the water level never drops along a path; that fixed results when markers are not at minima. <!-- L54 --> On the patch, versions 0.24 and 0.25 give the same labels in a different order.
- **MATLAB** uses Meyer's algorithm with 8-connectivity by default, and labels 0 the pixels that belong to no single region. <!-- L57 -->
- **OpenCV** does not take a gradient at all. `cv2.watershed` takes the colour image and floods by the largest channel difference between neighbouring pixels, 4-connected, first in first out within a level. A pixel that touches two labels when its turn comes becomes −1 and stops the flood, and the image's outer one-pixel frame is set to −1 before anything starts. <!-- L43 --> OpenCV credits Meyer's 1992 colour-segmentation paper. <!-- L44 -->

Run OpenCV's version on the patch, copied into three channels, and Figure 8 shows what those rules do. Markers drawn on the border, at (r0, c0) and (r2, c4), are overwritten by the frame, and nothing is labelled. Single pixels inside, at (r1, c1) and (r2, c3), go wrong: crossing the step costs 160 but reaching past the impulse costs 215, so the bright label crosses the step into the dark bottom row first. Strokes down c1 and c3 work, and the boundary comes back as a −1 line down c2. This is why OpenCV's own tutorial builds large markers before it calls the function. <!-- L47 -->

![Three cv2.watershed results: border markers erased by the −1 frame, one-pixel markers letting label 2 leak, strokes giving a clean line](FIG_08)

*Figure 8 — `cv2.watershed` floods neighbour differences, not a gradient you supply, and it owns the image border. Markers there vanish, and markers too small for the region let the other label in. Replayed from OpenCV's source.*

## Why does watershed over-segment, and where do markers come from?

Every regional minimum of the relief becomes a region unless something says otherwise. Vincent and Soille found that the watershed of a gradient mostly over-segments, whatever gradient is used and even after filtering, and that the cause is often noise. <!-- L22 --> Roerdink and Meijster call the over-segmentation severe and name markers and hierarchical watersheds as the remedies. <!-- L28 --> On the patch, one impulse made three minima of one valley.

A minimum's importance is the height of the rim the water must climb to leave it, its **pass**. Najman and Schmitt call the related measure the **dynamics** of a minimum and use it to fight over-segmentation. <!-- L32 --> On the patch, the three dark minima meet at 430 with 4-connectivity, or 304.1 with 8, and the dark side meets the bright one only at 640. Figure 9 draws the four minima merging as the level rises.

![Merge tree of the patch's four basins: the dark three join at 430, or 304.1 diagonally, and meet the bright column only at 640](FIG_09)

*Figure 9 — How deep each minimum is. Removing minima shallower than h keeps two regions for any h from 304.1 up to just below 640 with 8-connectivity. Worked by hand.*

That gives three ways to control the count:

1. **Remove shallow minima.** MATLAB's documentation recommends `imhmin` before `watershed` for exactly this. <!-- L57 --> On the patch, with 8-connectivity, any h from 304.1 to just below 640 leaves two minima and so two regions. The cost is that a real object with less contrast than h disappears too.
2. **Bring markers from knowledge.** Vincent and Soille's remedy was to impose markers as the only minima and fill every other. <!-- L23 --> <!-- L24 --> OpenCV's tutorial builds them from a threshold: Otsu, an opening to remove specks, a dilation for sure background, and a distance transform cut at 0.7 of its maximum for sure foreground. <!-- L47 --> For touching blobs in a binary image, flooding the negated **distance transform**, each pixel's distance to the background, splits them at their necks. <!-- L25 --> The cleaning operators are the subject of a later spoke, *Mathematical Morphology as Lattice Algebra*.
3. **Merge afterwards.** Take the over-segmented regions and merge neighbours bottom-up on a region adjacency graph, <!-- L33 --> or keep every level of the merge tree as a hierarchy and choose later. <!-- L32 --> Cousty and colleagues put the watershed on edge-weighted graphs, where it is equivalent to a minimum spanning forest and computable in linear time. <!-- L34 -->

Beucher, one of watershed's originators, puts it as two steps: choose the markers and the function to flood, then flood from the markers. <!-- L35 --> Markers are the decision about which minima are the same object, and the watershed only carries that decision out.

## The math

| Symbol | Meaning |
|---|---|
| $p_i$ | fraction of pixels at grey level $i$ |
| $t$ | threshold; class 0 is levels up to $t$, class 1 the rest <!-- L02 --> |
| $\omega_0, \omega_1$ | fraction of pixels in each class |
| $\mu_0, \mu_1, \mu$ | class means and the overall mean |
| $\sigma_B^2, \sigma_W^2, \sigma_T^2$ | between-class, within-class and total variance |
| $m, s$ | mean and standard deviation in a local window |

**Otsu's criterion.**

$$
\sigma_B^2(t) = \omega_0\,\omega_1\,(\mu_1 - \mu_0)^2, \qquad \sigma_W^2(t) + \sigma_B^2(t) = \sigma_T^2, \qquad t^\star = \arg\max_t \sigma_B^2(t) \tag{1}
$$

The total variance does not depend on t, so maximising the first is minimising the second: 2,935.77 at t = 105 on the smoothed patch. <!-- L01 --> <!-- L03 -->

**The midpoint condition.** Where the histogram is not empty at $t$, the best cut satisfies

$$
t^\star = \tfrac12\,(\mu_0 + \mu_1) \tag{2}
$$

halfway between the class means, the fixed point isodata iterates towards and two-cluster k-means shares. On the smoothed patch the midpoint is 125.7, inside the gap.

<details>
<summary>Deriving the midpoint condition</summary>

Write $S_0 = \omega_0 \mu_0$. Since $\omega_0\mu_0 + \omega_1\mu_1 = \mu$, the criterion is $\sigma_B^2 = (\omega_0\mu - S_0)^2 / (\omega_0 \omega_1)$, Otsu's own form. Moving $t$ by $dt$ adds $p\,dt$ to $\omega_0$ and $t\,p\,dt$ to $S_0$. Setting the derivative to zero and using $\omega_0\mu - S_0 = \omega_0\omega_1(\mu_1 - \mu_0)$ gives $2(\mu - t) = (\mu_1 - \mu_0)(1 - 2\omega_0)$. Substituting $\mu = \omega_0\mu_0 + \omega_1\mu_1$ leaves $t = (\mu_0 + \mu_1)/2$.

</details>

**What η measures.** For two classes of weights $\omega_0$ and $\omega_1$ with the same spread σ and means Δ apart,

$$
\eta = \frac{\sigma_B^2}{\sigma_T^2} = \frac{\omega_0\omega_1\Delta^2}{\sigma^2 + \omega_0\omega_1\Delta^2} \tag{3}
$$

so η falls when the classes overlap (Δ small against σ) and when one class is small ($\omega_0\omega_1$ small); a clean 5% object and two overlapping humps both read 0.68. For two equal humps d σ apart, the best cut misclassifies $\Phi(-d/2)$: 2.3% at d = 4.

**The family Otsu belongs to.** Fitting each class with a normal distribution and scoring a split by its log-likelihood per pixel gives, up to a constant, <!-- L13 -->

$$
\textstyle \ell(t) = \sum_i \omega_i \ln \omega_i - \tfrac12 \sum_i \omega_i \ln \sigma_i^2 \tag{4}
$$

Kittler and Illingworth's criterion. Equal variances turn the second term into $-\tfrac12 \ln \sigma_W^2$, the unbalanced Otsu; equal weights as well drop the first term, leaving Otsu's method. That first term favours unequal splits, which is what Otsu gives up.

**Local thresholds.**

$$
T_{\text{mean}} = m - C, \qquad T_{\text{Niblack}} = m + k\,s, \qquad T_{\text{Sauvola}} = m\,\bigl(1 + k\,(s/R - 1)\bigr) \tag{5}
$$

In a flat window $s = 0$, so the first two equal the mean (shifted by C) and Sauvola's drops to $(1 - k)\,m$. <!-- L16 --> <!-- L17 -->

**Flooding.** Each pixel joins the marker it can reach along the path whose highest point is lowest; that point is its flooding level. The impulse's pit is reached from the dark marker at 430 and from the bright one only at 640, so it joins the dark region.

## Implementation: the tooling map

Every entry below maps to the arithmetic above. **None of it was executed for this post**; it comes from source at pinned commits and from MathWorks' documentation. Figure 10 is the same map in one picture.

![Grid comparing OpenCV, scikit-image and MATLAB on Otsu's returned value, local defaults, what watershed floods and its labels](FIG_10)

*Figure 10 — Three libraries, three conventions. The thresholds agree on masks; the watersheds flood different surfaces with different neighbours.*

### OpenCV

| Want | Call | Note |
|---|---|---|
| Otsu | `t, bw = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)` | 8-bit or 16-bit single channel; `bw` is 255 where img > t; returns the first level of the best flat run <!-- L36 --> <!-- L37 --> |
| triangle | `cv2.THRESH_TRIANGLE` in place of `THRESH_OTSU` | 8-bit only <!-- L36 --> <!-- L41 --> |
| the threshold alone | add `cv2.THRESH_DRYRUN` | from release 4.12.0; 4.10.0 lacks it <!-- L45 --> |
| local mean − C | `cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block, C)` | box mean rounded to 8 bits, replicated border, C rounded up <!-- L42 --> |
| watershed | `cv2.watershed(img_bgr, markers)` | 8-bit colour image and 32-bit markers; −1 on boundaries and on the outer frame <!-- L43 --> |

Which code computes Otsu's number depends on the build. OpenCV builds with Intel IPP by default on x86, and there an 8-bit image without a mask goes to IPP's own Otsu routine, whose rule for a flat run is not in OpenCV's source. <!-- L38 --> <!-- L39 --> OpenCV's tests hold that path to the same binary output as its own code, <!-- L40 --> so expect the same mask but possibly a different number inside a gap. Release 4.10.0 has the same rules as the commit read here. <!-- L45 -->

### scikit-image and MATLAB

| Want | Call | Note |
|---|---|---|
| Otsu | `t = threshold_otsu(img)`; foreground `img > t` | integer images get one bin per level; first maximum <!-- L48 --> |
| isodata, triangle | `threshold_isodata(img)`, `threshold_triangle(img)` | lowest midpoint fixed point; peak-to-tail line <!-- L49 --> <!-- L50 --> |
| local | `threshold_sauvola(img, window_size=15, k=0.2)`, `threshold_niblack` | defaults differ from the paper's k = 0.5 and R = 128 <!-- L51 --> |
| watershed | `watershed(sobel(img), markers, connectivity=1)` | markers omitted means every regional minimum <!-- L52 --> <!-- L53 --> |
| MATLAB Otsu | `[t, em] = graythresh(I)`; `imbinarize(I)` | t from 0 to 1; `em` is Otsu's η <!-- L55 --> <!-- L56 --> |
| MATLAB local | `imbinarize(I, "adaptive")` | Bradley's local mean, sensitivity 0.5 <!-- L56 --> |
| MATLAB watershed | `watershed(imhmin(G, h))` | 8-connectivity; 0 marks pixels in no single region <!-- L57 --> |

### The worked example, in OpenCV and scikit-image

```python
import numpy as np
import cv2
from skimage.filters import sobel, threshold_otsu
from skimage.segmentation import watershed

patch = np.full((5, 5), 40, np.uint8)
patch[:, 3:] = 200
patch[2, 1] = 255

t_raw, _ = cv2.threshold(patch, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)       # 40 (own code)
smooth = cv2.GaussianBlur(patch, (3, 3), 0.8)                                       # 64 and 90, not 65 and 91
t_smooth, bw = cv2.threshold(smooth, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # 105; columns 3 and 4

relief = sobel(patch)                                     # Part 8's magnitudes / (4 * sqrt(2) * 255)
markers = np.zeros((5, 5), np.int32)
markers[0, 0], markers[2, 4] = 1, 2
two = watershed(relief, markers)                          # columns 0-2 and 3-4
four = watershed(relief)                                  # four regions, from four minima
```

This was not run for this post. The comments state what the worked example predicts.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** computing Otsu's threshold on one image and reusing the number on the next. On the patch the number is 40, the top of the dark spike, not the middle of the gap; a dark pixel two levels brighter in the next frame becomes foreground. Recompute per image, or keep the gap and use its middle.

- **Trusting a threshold on a small object.** For humps like Figure 6's, Otsu cuts through the background below a 2% object. Use the triangle method, or threshold a crop around the object.
- **Reading η alone.** It reads 0.68 both for a clean 5% object and for hopelessly overlapping humps.
- **Wrong window size.** Smaller than the objects and their interiors fall back on a fixed rule; larger than the shading and the method is global again.
- **Sauvola on bright objects.** Its flat-window rule keeps background bright; invert a dark-background image first. <!-- L18 -->
- **Passing a gradient to `cv2.watershed`.** It floods neighbour differences of what you pass, so a gradient there floods differences of differences. Pass the image; pass the gradient to scikit-image and MATLAB. <!-- L43 -->
- **Markers on the image border in OpenCV.** The frame is set to −1 first, so they vanish. <!-- L43 -->
- **Watershed without markers on a real gradient.** Every noise pit becomes a region, and smoothing alone does not cure it. <!-- L22 -->
- **Comparing watershed results across libraries.** Different queues, connectivities and line conventions give different boundaries from the same markers. <!-- L27 --> <!-- L31 -->

## Key takeaways

- **A threshold can only be as good as the histogram allows:** for two equal humps d standard deviations apart, any cut misclassifies at least $\Phi(-d/2)$ of the pixels.
- **Otsu's method is 2-means on the histogram, solved by trying every cut,** and it is the best cut only for two humps of similar size and spread; below a 2% object or with one hump more than four times wider, it misses.
- **The number is not the result:** on the smoothed patch Otsu, isodata and triangle print 105, 125 and 160 and draw one mask.
- **When light varies, threshold locally** with a window larger than the objects and smaller than the shading.
- **Watershed turns every regional minimum into a region:** one hot pixel gave the patch four; markers, or removing minima shallower than h, decide which minima count.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: one row of the table

For the smoothed patch, compute $\sigma_B^2$ and $\sigma_W^2$ for the cut between 99 and 105, and check that they add to 3,370.47.

**Self-check:** both numbers to one decimal place, and their sum.

<details><summary>Answer</summary>

The dark class is the 14 pixels up to 99, summing to 1,056 − 105 = 951, a mean of 67.93; the bright class is 105, five 162s and five 200s, 1,915 over 11 pixels, a mean of 174.09. So $\sigma_B^2$ = (14/25)(11/25)(106.16)² = 2,777.0, and $\sigma_W^2$ = 3,370.47 − 2,777.04 = 593.4.

</details>

### E2 — Inspect: the wrong peak

In Figure 6's 1% panel, how can you tell from the criterion curve alone that Otsu chose badly?

**Self-check:** the two local maxima and where each sits on the histogram.

<details><summary>Answer</summary>

The curve has two peaks, at 72 and 118. The one at 118 sits in the valley between the humps; the higher one, at 72, sits inside the background hump, so the chosen cut splits the background. A single-peaked curve whose peak lies in a valley is what a healthy two-hump histogram gives.

</details>

### E3 — Predict: the two lights at window 5

On row r0 of the lit-and-shadowed image, predict which pixels `cv2.adaptiveThreshold` marks bright with `ADAPTIVE_THRESH_MEAN_C`, block 5 and C = 0. Then check (r0, c9) by hand.

**Self-check:** the four bright columns, and the threshold at (r0, c9) with the window's values.

<details><summary>Answer</summary>

Columns c3, c4, c8 and c9, with no errors. At (r0, c9) the replicated window covers columns c7, c8, c9, c9 and c9, values 8, 40, 40, 40 and 40 on every row, so the mean is 33.6, rounded to 34; 40 is greater than 34, so the pixel is bright.

</details>

### E4 — Diagnose: the bright label in the dark rows

A colleague runs `cv2.watershed` on the patch copied into three channels, with markers (r1, c1) = 1 and (r2, c3) = 2, and gets label 2 at (r3, c1) and (r3, c2), which are dark pixels. Find the cause, and give markers that fix it.

**Self-check:** the pixel that blocked the dark label, the two costs that decided the order, and a working marker set.

<details><summary>Answer</summary>

The frame becomes −1. At cost 0, (r1, c2) joins label 1, (r1, c3) touches both labels and becomes −1, and (r3, c3) joins label 2 and queues (r3, c2) at the step's cost, 160. (r2, c2) leaves the 160 queue first, touches both labels and becomes −1, cutting label 1 off from row r3; its only other route is past the impulse, at 215. So (r3, c2) joins label 2 at 160, and (r3, c1) follows at 0. Strokes down c1 and c3 fix it: every c2 pixel then touches both labels and becomes −1, so neither label crosses the step, and the boundary is a −1 line down c2.

</details>

## References

1. Otsu, N. "A Threshold Selection Method from Gray-Level Histograms." *IEEE Transactions on Systems, Man, and Cybernetics* 9(1):62–66, 1979. doi:10.1109/TSMC.1979.4310076. [PDF](https://engineering.purdue.edu/kak/computervision/ECE661.08/OTSU_paper.pdf)
2. Sezgin, M., and Sankur, B. "Survey over Image Thresholding Techniques and Quantitative Performance Evaluation." *Journal of Electronic Imaging* 13(1):146–165, 2004. [doi:10.1117/1.1631315](https://doi.org/10.1117/1.1631315)
3. Ershov, E. I., Korchagin, S. A., Kokhan, V. V., and Bezmaternykh, P. V. "A Generalization of Otsu Method for Linear Separation of Two Unbalanced Classes in Document Image Binarization." *Computer Optics* 45(1):66–76, 2021. [doi:10.18287/2412-6179-CO-752](https://doi.org/10.18287/2412-6179-CO-752)
4. Liu, D., and Yu, J. "Otsu Method and K-means." *Ninth International Conference on Hybrid Intelligent Systems*, 344–349, 2009. [doi:10.1109/HIS.2009.74](https://doi.org/10.1109/HIS.2009.74)
5. Sauvola, J., and Pietikäinen, M. "Adaptive Document Image Binarization." *Pattern Recognition* 33(2):225–236, 2000. [doi:10.1016/S0031-3203(99)00055-2](https://doi.org/10.1016/S0031-3203(99)00055-2)
6. Vincent, L., and Soille, P. "Watersheds in Digital Spaces: An Efficient Algorithm Based on Immersion Simulations." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 13(6):583–598, 1991. doi:10.1109/34.87344. [PDF](https://people.cmm.minesparis.psl.eu/users/marcoteg/cv/publi_pdf/MM_refs/vincent/1991_PAMI_VincentSoille_watershed.pdf)
7. Roerdink, J. B. T. M., and Meijster, A. "The Watershed Transform: Definitions, Algorithms and Parallelization Strategies." *Fundamenta Informaticae* 41(1–2):187–228, 2000. [doi:10.3233/FI-2000-411207](https://doi.org/10.3233/FI-2000-411207)
8. Najman, L., and Schmitt, M. "Geodesic Saliency of Watershed Contours and Hierarchical Segmentation." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 18(12):1163–1173, 1996. [doi:10.1109/34.546254](https://doi.org/10.1109/34.546254)
9. Haris, K., Efstratiadis, S. N., Maglaveras, N., and Katsaggelos, A. K. "Hybrid Image Segmentation Using Watersheds and Fast Region Merging." *IEEE Transactions on Image Processing* 7(12):1684–1699, 1998. [doi:10.1109/83.730380](https://doi.org/10.1109/83.730380)
10. Cousty, J., Bertrand, G., Najman, L., and Couprie, M. "Watershed Cuts: Minimum Spanning Forests and the Drop of Water Principle." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 31(8):1362–1374, 2009. [doi:10.1109/TPAMI.2008.173](https://doi.org/10.1109/TPAMI.2008.173)
11. Beucher, S. "The Watershed Transformation page." Centre de Morphologie Mathématique, Mines ParisTech. <https://people.cmm.minesparis.psl.eu/users/beucher/wtshed.html> (accessed 2026-10-13)
12. OpenCV source, commit 802cf95: `thresh.cpp`, `segmentation.cpp`, `smooth.dispatch.cpp`, `fixedpoint.inl.hpp`, `imgproc.hpp`, the IPP and RISC-V threshold layers, `test_thresh.cpp` and `CMakeLists.txt`. <https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src> (accessed 2026-10-13)
13. OpenCV source, tags 4.10.0 and 4.12.0. <https://github.com/opencv/opencv/blob/4.10.0/modules/imgproc/src/thresh.cpp> (accessed 2026-10-13)
14. OpenCV Python tutorials, commit 802cf95: "Image Thresholding" and "Image Segmentation with Watershed Algorithm." <https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760/doc/py_tutorials/py_imgproc> (accessed 2026-10-13)
15. scikit-image source, commit b700edc: `filters/thresholding.py`, `filters/edges.py`, `segmentation/_watershed.py`, `segmentation/_watershed_cy.pyx`. <https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2> (accessed 2026-10-13)
16. scikit-image 0.25.0 release notes (pull request 7071). <https://github.com/scikit-image/scikit-image/releases/tag/v0.25.0> (accessed 2026-10-13)
17. MathWorks. "graythresh", "imbinarize", "adaptthresh" and "watershed." Image Processing Toolbox documentation, release R2026b. <https://www.mathworks.com/help/images/ref/watershed.html> (accessed 2026-10-13)
