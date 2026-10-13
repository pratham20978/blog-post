---
title: "Canny Edge Detection, Line by Line: Setting the Thresholds"
slug: canny-line-by-line
date: 2026-10-12
updated: 2026-10-12
summary: "Canny's two thresholds grade connected chains, not pixels. Worked by hand on one 5×5 patch: what each threshold selects, and how to set both from the noise."
tags: [algorithms, image-processing, edge-detection, canny, non-maximum-suppression, hysteresis-thresholding, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: intermediate
series: image-processing
series_position: 8
prerequisites: ["the Sobel gradient and the shared 5×5 patch from part 1 of this series", "what a first derivative measures", "reading Python signatures"]
reading_minutes: 32
cover_image_url: "COVER"
cover_image_alt: "A 5×5 grid split by a vertical edge, with a chain of linked dots down the edge from one tangerine seed, and two hollow dots left unlinked"
canonical_url: "https://canery.in/blogs/canny-line-by-line"
---

> [!NOTE]
> **Insights** — Canny's two thresholds do not grade pixels; they grade connected chains of the pixels that survive non-maximum suppression. The high threshold decides which chains exist at all, because each needs one pixel above it, and the low threshold decides where each chain ends. Both are compared with raw gradient values, which OpenCV's default reads as 4 × the height of a step and up to 41% high on diagonals, so set them from the image noise: the high one a chosen number of noise widths above what flat regions produce, the low one a half to a third of it. Worked by hand on the series' 5×5 patch, `cv2.Canny` with its defaults returns the patch's edge as a clean line at no threshold pair at all; after the series' 3×3 Gaussian, pairs in Canny's own 2:1 to 3:1 ratio do.

**Level:** intermediate · **You need:** *Image Processing by Hand* (part 1 of this series) for the shared patch and the Sobel gradient, what a first derivative measures, and enough Python to read a signature · **Time:** ~32 min

This is part 8 of *Image Processing by Hand*. Part 1 drew Canny's method as four steps and promised a post on the last two, suppression and hysteresis, line by line; this is that post, worked on the shared patch, followed by a way to set the thresholds.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Suppression](#what-does-non-maximum-suppression-keep) · [The two thresholds](#what-do-the-two-thresholds-select) · [Units](#what-units-are-the-thresholds-in) · [Setting them](#how-do-you-set-the-thresholds-without-searching) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch and cross-checked with plain Python using only its `math` module; that check is not published. No OpenCV, scikit-image or MATLAB call was executed: library behaviour comes from source read at pinned commits and, for MATLAB, from MathWorks' documentation. There are no timings or measured curves. Figures that draw curves or regions are evaluated from the definitions, or from closed forms under a stated noise model, and their captions say which.

## Why this matters

Run `cv2.Canny` with its defaults on the series' 5×5 patch and try every pair of thresholds. The patch holds the cleanest edge an image can have, a straight step from 40 to 200 down all five rows, and the function never returns it as a line. Either you get three separate pixels of it, or you get the line with five extra pixels attached: a ring round the patch's one bright pixel.

Smooth the patch with the series' 3×3 Gaussian first, and threshold pairs in the ratio Canny himself used return exactly the line. <!-- L26 --> Nothing about the thresholds changed. What changed is what they were compared with, and that is the subject of this post: the last two steps of Canny's method walked pixel by pixel, and then a way to set the two numbers from the noise instead of by trial.

## The problem

Part 1 split Canny's method into four steps: smooth with a Gaussian, take the gradient, thin it, and threshold it with hysteresis. The first two respond to edges, the third localises them and the fourth commits to a decision. This post is about the last two, and the two numbers every `Canny` call asks for. Canny's is by far the most widely used differential edge detector, <!-- L36 --> so those two numbers sit in a great deal of code.

The gradient at a pixel is a vector of two first derivatives. The Sobel operator estimates them with 3×3 weights: $G_x$ is the right column minus the left column, the three rows weighted 1, 2, 1, and $G_y$ is the same turned on its side. The vector's length, the **gradient magnitude**, says how fast brightness changes there, and it points from dark to bright, across the edge. The length can be measured two ways: the Euclidean or **L2** norm $\sqrt{G_x^2 + G_y^2}$, or the cheaper **L1** norm $|G_x| + |G_y|$, which OpenCV's `Canny` uses unless you pass `L2gradient=True`. <!-- L06 --> <!-- L12 --> Part 1 showed that L1 reads a 45° edge 41% high.

A step does not give a one-pixel answer: its magnitude is large over a band two or more pixels wide. **Non-maximum suppression** (NMS) thins the band. A pixel survives only if its magnitude is the largest along the gradient direction, compared with its neighbour on each side. Survivors keep their magnitudes; everything else becomes 0.

**Hysteresis thresholding** then decides which survivors are edges, using two thresholds. A survivor above the **high threshold** is a **seed**, and is an edge. A survivor between the two is a **candidate**: it becomes an edge only if a chain of candidates connects it to a seed, where connected means **8-connected**, touching along a side or at a corner. Anything at or below the low threshold is dropped. <!-- L08 --> <!-- L09 --> <!-- L23 -->

So the problem has two halves. What do the two thresholds actually select, given that they act on suppression's output rather than on the image? And how do you set them without trying values until the picture looks right? The second half hides a catch: the thresholds are compared with raw Sobel output, not with grey levels, so a threshold means nothing until you know the gain of the operator in front of it.

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

It has a step of 160 between c2 and c3 on every row, and one bright pixel. Steps 1 to 3 below are what `cv2.Canny(patch, low, high)` computes, in its own order; step 4 adds the smoothing that Canny's method assumes.

### Step 1: the gradient

`cv2.Canny` takes Sobel derivatives of the image as it is: the function has no smoothing step. Past the border it repeats the edge pixel, a **replicate** border, <!-- L01 --> instead of the reflect-101 rule that is OpenCV's default everywhere else. <!-- L13 --> That matters at column c0, beside the impulse.

Take (r1, c2). $G_x$ weighs the differences between columns c3 and c1 on rows r0, r1 and r2 by 1, 2 and 1: (200 − 40) + 2 × (200 − 40) + (200 − 255) = 160 + 320 − 55 = 425. $G_y$ weighs the differences between rows r2 and r0 on columns c1, c2 and c3 by 1, 2 and 1: (255 − 40) + 0 + 0 = 215. The magnitude is $\sqrt{425^2 + 215^2} = 476.3$ in L2, and 425 + 215 = 640 in L1. Every pixel:

```text
Gx                         Gy                         L2 magnitude
  0   0  640  640   0        0     0     0   0   0       0      0    640    640   0
215   0  425  640   0      215   430   215   0   0     304.1  430    476.3  640   0
430   0  210  640   0        0     0     0   0   0     430      0    210    640   0
215   0  425  640   0     -215  -430  -215   0   0     304.1  430    476.3  640   0
  0   0  640  640   0        0     0     0   0   0       0      0    640    640   0
```

Three things stand out. The step reads 640, four times its height, on both of its sides, c2 and c3: a tie that suppression has to break. The impulse's own pixel has no gradient at all, because its left and right neighbours are equal and so are the ones above and below it; instead it sits inside a ring of non-zero magnitudes, from 210 to 476.3. And at (r2, c0) the replicate border gives $G_x$ = 2 × (255 − 40) = 430, where reflect-101 would mirror the impulse onto the far side and give 0, the border zero of Part 4, *Kernel Design: Separability, Borders, Optimised Derivatives*. Figure 1 draws the vectors.

![The patch's Sobel gradient as arrows: 640 on both sides of the step, a ring of shorter arrows round the impulse, and none on the impulse itself](FIG_01)

*Figure 1 — The patch's Sobel gradient under cv2.Canny's replicate border. The step reads 640 on two columns at once, and the impulse's own pixel reads 0 inside a ring of non-zero magnitudes. Worked by hand.*

### Step 2: non-maximum suppression

OpenCV sorts each gradient direction into one of four bins: horizontal when $|G_y| < 0.414\,|G_x|$, which is tan 22.5°; vertical when $|G_y| > 2.414\,|G_x|$, which is tan 67.5°; diagonal otherwise. <!-- L07 --> A pixel then survives if it beats both neighbours along its bin's direction. For the horizontal and vertical bins it must be strictly greater than the neighbour before it (left or above) and at least equal to the one after it; for the diagonal bins it must be strictly greater than both. <!-- L07 --> Outside the image the magnitude counts as 0. <!-- L10 -->

Walk row r1 with the L2 magnitude:

- (r1, c3) has $G_y$ = 0, so its bin is horizontal. 640 > 476.3 on its left and 640 ≥ 0 on its right: it survives.
- (r1, c2) points at 26.8°, a diagonal bin, so it is compared with (r0, c1) = 0 and (r2, c3) = 640. It loses.
- (r1, c1) points straight down, vertical bin, compared with (r0, c1) = 0 and (r2, c1) = 0: it survives with 430.
- (r1, c0) points at 45°, diagonal, compared with 0 outside the image and (r2, c1) = 0: it survives with 304.1.

On the clean row r0 the tie is broken by the asymmetric test. (r0, c2) beats 0 on its left and equals 640 on its right, so it survives; (r0, c3) is not strictly greater than 640, so it does not. The result is a five-pixel line, (r0, c2), (r1, c3), (r2, c3), (r3, c3) and (r4, c2), that steps from c2 to c3 round the impulse, plus a five-pixel ring.

Now repeat it with OpenCV's default L1 magnitude. At (r1, c2) the L1 magnitude is 640, the same as (r1, c3). So (r1, c3) fails its strict test against its left neighbour, and (r1, c2) still loses its diagonal test to (r2, c3). Rows r1 and r3 lose their edge pixel, and the line becomes three dots. Figure 2 shows both.

![Suppression on the raw patch: with L2 a connected five-pixel line plus a ring of five; with L1 only three line pixels, rows r1 and r3 blank](FIG_02)

*Figure 2 — Suppression on the raw patch. With L2 the step survives on every row; with OpenCV's default L1, the oblique gradient at (r1, c2) reads 640, ties the edge pixel beside it, and both lose. Worked by hand.*

### Step 3: hysteresis

Hysteresis works on connected chains. Under L2, all ten survivors form one 8-connected chain: (r1, c1) touches (r0, c2) at a corner, and (r3, c1) touches (r4, c2). The ring hangs off the line. Its magnitudes are 640 on the five line pixels, 430 on three ring pixels and 304.1 on two.

- Any high threshold below 640 makes the line pixels seeds, and the whole chain is reachable from them.
- Which pixels come out is then set by the low threshold alone: below 304.1, all ten; from 304.1 up to 430, the line and the three 430s; from 430 up, the line alone.

So the line comes out clean only with a low threshold of at least 430 and a high one below 640: a ratio of high to low under 640 / 430 = 1.49. Canny's own implementation used ratios of two or three to one, <!-- L26 --> and on this patch every such pair attaches the ring. Under L1 it is worse. A low threshold of 430 or more leaves the three isolated dots, and anything lower attaches the ring.

### Step 4: smooth first, then run it again

Now do what Canny's method assumes and smooth first, with the series' 3×3 Gaussian (σ = 0.8, weights 0.239, 0.522 and 0.239). Part 7, *Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion*, worked this blur: the impulse falls to 98.6 and the step spreads to 78.2 | 161.8. Repeating steps 1 and 2 on the smoothed patch, the strongest pixel on every row is c3: 474.9 on r0 and r4, 436.5 on r1 and r3, and 408.8 on r2, where the blurred impulse has raised the dark side. The ring shrinks to two pixels, (r1, c0) and (r3, c0), at 219.7, and they no longer touch the line: two empty columns separate them from it.

That changes what the thresholds can do. A high threshold anywhere from 219.7 up to 474.9 leaves the two ring pixels without a seed, so they go, and a low threshold under 408.8 keeps the column joined. A pair in Canny's range now works: 450 and 180, a ratio of 2.5, return the line alone, where on the raw patch the same pair returned all ten pixels. Figure 3 shows both runs. Rounding the smoothed values to whole grey levels, as an 8-bit image would hold them, changes no survivor.

![Hysteresis at 450 and 180: on the raw patch the ring joins the line at two corners, all ten pixels kept; smoothed, a clean column of five](FIG_03)

*Figure 3 — The same thresholds, 450 and 180, on two inputs. Unsmoothed, the ring touches the line and rides in on it; smoothed, the ring is two isolated pixels with no seed. Worked by hand.*

### The scorecard

| run | the step's line | pixels from the impulse | thresholds that give the line alone |
|---|---|---|---|
| `cv2.Canny` defaults (L1), raw | 3 pixels, not connected | 5, attached | none |
| raw, `L2gradient=True` | 5 pixels, connected | 5, attached | low from 430 to below 640, high between it and 640 |
| 3×3 Gaussian first, L2 | 5 pixels, all on c3 | 2, separate | high from 219.7 to below 474.9, low under 408.8 |
| as above, interpolated suppression | 5 pixels, all on c3 | 4, separate | high from 222.2 to below 474.9, low under 408.8 |

Only the smoothed runs leave room for Canny's ratio. The last row uses the other way of doing suppression, which the section after next explains.

## Intuition

The two thresholds look as if they grade pixels: strong, weak, dropped. They grade chains. Suppression has already reduced the image to ridges one pixel wide, and hysteresis asks two questions of each connected ridge: does it contain a seed, and where does it fall below the low threshold?

Picture each ridge as a chain hanging from hooks. The high threshold decides whether a chain has a link strong enough to hang from; the low threshold decides which links are strong enough to hold, so a chain splits wherever a link is weaker than the low threshold, and each piece then needs a hook of its own. The analogy breaks at "connected". A real chain link has two neighbours, but a pixel has eight, so one pixel touching the chain at a corner is enough to join it: the ring's (r1, c1) touching (r0, c2) is how the impulse got in.

Figure 4 maps every (low, high) pair to what comes out of the patch.

![Maps of the low–high threshold plane: raw L1 never gives the line alone, raw L2 only above low 430, smoothed in a wide band crossed by ratios 2 and 3](FIG_04)

*Figure 4 — What each threshold pair returns. On the raw patch the high threshold only decides whether anything comes out and the low one decides what; after smoothing, the high threshold also deletes the ring. The ratio-2 and ratio-3 lines never enter the raw patch's clean region and run through the smoothed one. Computed from the definitions on the patch.*

## What does non-maximum suppression keep?

Canny defined an edge point as a maximum of the smoothed gradient's magnitude along the gradient's own direction. <!-- L28 --> On a grid the direction rarely points at a pixel, so every implementation has to decide what "the neighbour along the gradient" is, and what to do when two magnitudes are equal.

### Four bins, or interpolation

Canny's own suppression did not round the direction. In his 1983 technical report, each pixel is compared with the magnitude at the two points where the gradient line crosses the neighbouring rows or columns, each estimated by linear interpolation between the two pixels it falls between; the pixel must be strictly greater than both. <!-- L29 --> scikit-image interpolates the same way. <!-- L19 --> OpenCV rounds to four bins and reads the nearest of the eight neighbours. <!-- L07 -->

The two read the same neighbour values whenever the gradient points at 0°, 45° or 90°, or the two pixels being mixed are equal. On the raw patch that covers every pixel: (r1, c2) at 26.8° mixes (r1, c3) and (r2, c3), and both are 640. The libraries still disagree there at (r0, c3) and (r4, c3), but through their tie rules, below. After smoothing the two methods part at (r1, c1), where the magnitude is 222.2 and the gradient points at 62.8°, as Figure 5 shows. OpenCV puts 62.8° in a diagonal bin and compares with (r2, c2) = 316.2, so the pixel goes. Interpolation follows the gradient line to row r2, where it crosses 0.514 of the way from (r2, c1) = 74.7 to (r2, c2) = 316.2, and reads 198.8; on the other side it reads 133.0. The pixel stays.

![OpenCV's four direction bins, and (r1, c1) of the smoothed patch: rounding compares 222.2 with 316.2, interpolation with 198.8 and 133.0](FIG_05)

*Figure 5 — Two ways to find "the neighbour along the gradient". Rounding 62.8° to the diagonal compares 222.2 with 316.2 and suppresses it; interpolating along the true direction compares it with 198.8 and keeps it. Worked by hand on the smoothed patch.*

### Ties

The raw patch's step lies exactly between c2 and c3, so its magnitude profile along any clean row is 0, 640, 640, 0. Three tests give three answers, drawn in Figure 6. A strict test on both sides, which is how Grompone von Gioi and Randall state Canny's condition, <!-- L29 --> keeps neither pixel and the edge vanishes. OpenCV's test, strict before and non-strict after, keeps exactly one. <!-- L07 --> scikit-image keeps a pixel when neither interpolated neighbour exceeds it, <!-- L19 --> so it keeps both, and the edge is two pixels wide.

![The profile 0, 640, 640, 0 under three tie rules: strict keeps no pixel, OpenCV's keeps the left one, scikit-image's keeps both](FIG_06)

*Figure 6 — Ties decide whether a step that falls between pixels gives zero, one or two edge pixels per row. OpenCV's choice keeps the left one here, the dark side; mirror the step and it keeps the left one again, now the bright side.*

OpenCV's rule always keeps the left pixel of a horizontal plateau and the upper pixel of a vertical one, whatever the edge's polarity, so its line sits half a pixel left of, or above, a symmetric edge. Ties are not exotic: integer images and integer weights give integer magnitudes, and any straight edge that falls exactly between two pixels produces one.

### Where exactly is the edge?

Suppression returns pixels, but an edge has a position between them. Devernay's correction fits a parabola through the three magnitudes used in the test, the pixel and its two neighbours, and moves the edge to its vertex, an offset of $\tfrac12 (A - C)/(A + C - 2B)$ from the pixel. <!-- L31 --> On row r0 the three values are 0, 640 and 640, and the vertex lands at 2.5, exactly where the step is. On row r2 they are 210, 640 and 0, and the vertex lands at 2.90: the impulse two columns away lowers the dark side's magnitude and drags the estimate 0.4 pixel towards the bright side, as Figure 7 shows. On the smoothed patch the same rows give 2.54 and 2.77.

![Parabolas through three magnitudes: row r0 peaks at column 2.5, where the step is; row r2, lowered by the impulse, peaks at 2.90](FIG_07)

*Figure 7 — Sub-pixel position from three magnitudes. A clean row recovers the step at 2.5; the impulse's row reads 2.90. Evaluated from the parabola through the worked values.*

For slanted edges, the interpolation that suppression uses becomes the main source of sub-pixel error, up to about five times the error on axis-aligned edges for Gaussian edges of σ = 1. <!-- L32 --> The other route to sub-pixel position, the zero-crossings of the Laplacian, belongs to Part 2, *The Laplacian by Hand*, which also owns the argument for tracking edges from coarse to fine scales.

### Where suppression fails

Suppression assumes one edge per neighbourhood. Where three regions meet, at a T-junction, the weaker edge's magnitude is smaller than the stronger edge's next to it, so its pixels near the junction are suppressed and the weaker edge is left hanging, a gap Li, Sullivan and Baker called false suppression. <!-- L38 --> The L1 gap in step 2 is the same thing in miniature: the ring's oblique gradient met the step and both lost. Corners and junctions need an operator that sees two directions at once; that is a later spoke, *The Structure Tensor: Harris, Shi–Tomasi, and Optical Flow*.

## What do the two thresholds select?

Canny introduced the second threshold to fix one failure. With a single threshold set at the mean response of a contour, noise pushes the contour above the threshold only about half the time, and the contour breaks into dashes: **streaking**. <!-- L24 --> With hysteresis, a contour is kept whole if any part of it exceeds the high threshold and every pixel stays above the low one. To break, it now has to dip below the low threshold; to appear from nothing, an isolated false point now has to exceed the high one. <!-- L23 --> <!-- L25 -->

So the two thresholds select different things. The high threshold selects **which chains exist**: every connected set of candidates that contains no seed is deleted, however long it is. The low threshold selects **where each chain ends**, and with it whether two pieces join. On the raw patch there is one chain and it contains the strongest pixels, so the high threshold only decides between something and nothing, and every interesting boundary in Figure 4 is vertical. After smoothing, the two ring pixels form chains of their own, and the high threshold gets its proper job, deleting them.

The implementations agree on the set and differ in details. OpenCV tests only pixels above the low threshold, marks seeds as it suppresses, then walks outwards from each seed through 8-connected candidates on a stack; <!-- L08 --> <!-- L09 --> its comparisons are strict, so a pixel exactly at a threshold falls below it. scikit-image labels the 8-connected components of its candidates and keeps those that contain a seed, with comparisons that include the threshold itself. <!-- L20 --> Pass OpenCV the thresholds in the wrong order and it swaps them; <!-- L05 --> pass scikit-image a low threshold above the high one and it raises an error. <!-- L18 -->

## What units are the thresholds in?

A threshold is compared with whatever the derivative operator returns, so its units are set by that operator, and OpenCV leaves its operators unnormalised. With the default aperture of 3, a step of h grey levels reads 4h at its two flank pixels, which is the patch's 640, and a ramp rising one grey level per pixel reads 8, Part 4's factor. The `apertureSize` argument changes the Sobel weights. At 5 the smoothing weights are 1, 4, 6, 4, 1 and the derivative weights −1, −2, 0, 2, 1; at 7 they are 1, 6, 15, 20, 15, 6, 1 and −1, −4, −5, 0, 5, 4, 1. <!-- L16 --> The same step then reads 48h and 640h, and the same ramp 128 and 2,048. Figure 8 puts them on one scale.

![Log-scale bars: the 160-level step reads 640, 7,680 and 102,400 at apertures 3, 5 and 7; beside them L1 over L2 rising to 1.41 at 45°](FIG_08)

*Figure 8 — The units of a Canny threshold. Moving from aperture 3 to 5 multiplies a sharp step by 12 and a ramp by 16, so no single factor converts thresholds between apertures. Computed from OpenCV's kernels.*

Four more facts set the units in OpenCV:

- **Aperture 7 is stored divided by 16.** `Canny` computes those derivatives at 1/16 scale, which keeps them inside 16-bit integers (a 255-level step would otherwise read 163,200), and divides both thresholds by 16 to match, so you still pass thresholds in raw 7-tap units. <!-- L04 -->
- **L1 reads oblique edges high.** The ratio of L1 to L2 is $|\cos\theta| + |\sin\theta|$: 1 on the axes, 1.414 at 45°, and 1.344 at the 26.8° of (r1, c2), which is how 476.3 became 640. With `L2gradient=True`, OpenCV squares both thresholds and compares them with $G_x^2 + G_y^2$. <!-- L06 --> L1 can also move an edge: on the smoothed patch it puts the line on c2 on every row but r2, where L2 puts it on c3, because the blurred impulse gives c2 a vertical component that L1 counts in full.
- **Aperture −1 means Scharr.** `Canny` accepts it, though the documentation describes only Sobel apertures, <!-- L03 --> <!-- L12 --> and Scharr's weights read a step as 16h.
- **Colour takes the strongest channel.** For a 3-channel image, each pixel uses the magnitude and direction of whichever channel's magnitude is largest. <!-- L11 --> The input must be 8-bit; for anything else you compute 16-bit derivatives yourself and pass them to the overload that accepts them. <!-- L02 -->

Other libraries chose other units. scikit-image smooths with a Gaussian of σ = 1 by default, takes SciPy's Sobel and uses L2. <!-- L17 --> It rescales an 8-bit image to 0–1 and divides your thresholds by 255 to match, so they end up in the same raw-Sobel grey levels as OpenCV's, but measured after a blur; its defaults, 10% and 20% of the dtype's maximum, are 25.5 and 51 for 8-bit input. <!-- L18 --> MATLAB's `edge` takes thresholds as fractions from 0 to 1, sets the low one to 0.4 times the high one when you give a single number, and smooths with σ = √2 by default. <!-- L22 -->

## How do you set the thresholds without searching?

A threshold is a statement about the noise: values like this are not produced by flat regions. So the principled route starts from a model of what flat regions produce, picks how many false seeds you will accept, and derives both thresholds from that.

### Start from the noise

Suppose each pixel carries independent Gaussian noise of standard deviation σ grey levels. Each Sobel derivative is a weighted sum of six noisy pixels with weights ±1, ±2 and ±1, so its noise has standard deviation $\sqrt{1 + 4 + 1 + 1 + 4 + 1}\,\sigma = \sqrt{12}\,\sigma = 3.464\,\sigma$. The two derivatives share pixels, but the products of their weights, pixel by pixel, sum to zero, so they are uncorrelated and, being Gaussian, independent. The length of a vector of two independent Gaussians has a **Rayleigh distribution**, here with scale $s = 3.464\,\sigma$: on a flat region the L2 magnitude exceeds a value $t$ with probability $e^{-t^2/2s^2}$.

That gives the high threshold directly. Choose the fraction α of flat pixels you will accept as false seeds, and set

$$
T_H = s\sqrt{2\ln(1/\alpha)}
$$

so α = 1 in 1,000 gives 3.72 s and 1 in 10,000 gives 4.29 s. The weakest step that can seed is then $T_H/4$ grey levels at aperture 3. With σ = 2, s = 6.93, and α = 1 in 10,000 puts $T_H$ at 29.7: steps of 7.4 grey levels or more can start an edge. Figure 9 draws the case.

![Rayleigh density of flat-region magnitude for noise of 2 levels, with the low threshold at 14.9, the high at 29.7, and a 20-level step at 80](FIG_09)

*Figure 9 — Thresholds from the noise. With σ = 2 and one false seed per 10,000 flat pixels, the high threshold is 29.7 and the low one, at half, lets one flat pixel in ten through as a candidate. Model inputs: Gaussian noise, Sobel aperture 3, L2.*

The low threshold follows from the ratio. If $T_L = T_H / r$, the fraction of flat pixels above it is $\alpha_L = \alpha^{1/r^2}$: with α = 1 in 10,000, a ratio of 2 lets one flat pixel in ten through as a candidate, and a ratio of 3 about one in three. Candidates are harmless until they touch a seeded chain, which is why the low threshold can afford a false-alarm rate a thousand times higher.

If you smooth first, recompute s for the combined operator. After the series' 3×3 Gaussian, each derivative's noise standard deviation falls from 3.464 σ to 1.709 σ, while a clean step's peak falls only from 4h to 3.04h, so the step's margin over the noise grows about 1.5 times.

### Read the noise off the histogram

Canny estimated the noise from the image itself. His argument was that edges are rare, so the lower percentiles of the gradient magnitude's histogram, say below 80%, are set mainly by noise. <!-- L27 --> Under the Rayleigh model the median magnitude is 1.177 s and the 80th percentile 1.794 s, so either one gives s and then both thresholds.

The argument needs a mostly flat image, and the patch is the counter-example: 15 of its 25 magnitudes are non-zero, and its 80th percentile is 640, the step itself. A tight crop of an edge, a texture, or a page of text breaks the same assumption. scikit-image's `use_quantiles=True`, which reads the thresholds as percentiles of the magnitude image, <!-- L18 --> carries it too: it fixes in advance the fraction of pixels that may be edges. MathWorks describes MATLAB's automatic choice only as heuristic. <!-- L22 --> Estimate the noise from a region you know is flat, or from a calibration frame, when you can. Libraries do not estimate it for you: Canny's noise estimation, like his multiple scales and directional operators, never became part of the standard detector they ship. <!-- L30 -->

### Why two thresholds, and why a ratio of 2 to 3

Desolneux, Moisan and Morel came at the question from Canny's threshold problem: they found its output strongly threshold-dependent, marking flat regions at low thresholds and breaking real edges at high ones. <!-- L41 --> They made "unlikely in noise" exact for curves. A curve of length $l$ whose weakest point has contrast µ is meaningful when the number of curves tested, N, times $H(\mu)^l$ is at most 1, where $H(\mu)$ is the fraction of pixels whose gradient is at least µ, read from the image's own histogram, and the points are treated as independent. <!-- L39 --> The contrast a curve needs falls as it gets longer. <!-- L40 -->

Put the Rayleigh tail in for $H$, which is this post's model rather than theirs, and the required contrast is

$$
\mu_{\min}(l) = s\sqrt{\frac{2\ln N}{l}}
$$

With N = 10⁶ a single pixel needs 5.26 s, a chain of 4 needs 2.63 s, half as much, and a chain of 9 needs 1.75 s, a third. Hysteresis is a two-step version of that curve, as Figure 10 shows: a high threshold for the chain's best pixel and a low one for the rest. A ratio of 2 to 3 is the drop this model allows for chains of 4 to 9 pixels, whatever N is.

![Required contrast against chain length, falling as one over its square root: half the one-pixel threshold at length 4, a third at length 9](FIG_10)

*Figure 10 — Why two thresholds. The contrast a chain needs to be unlikely in noise falls with its length; hysteresis approximates the curve with a high step and a low one. Model inputs: Rayleigh noise tail, N = 10⁶ curves, independent points.*

Other principled routes exist. Hancock and Kittler cast hysteresis as a Bayesian decision whose thresholds follow from an image model estimated from the image, and added a third threshold. <!-- L42 --> Henstock and Chelberg fit edge and non-edge magnitudes with a mixture of two gamma densities. <!-- L43 --> A survey of the field notes why the simplest route, putting the threshold at the valley between two peaks of the histogram, rarely works: gradient histograms are seldom bimodal, and the distributions that Bayesian methods assume fit them poorly. <!-- L37 --> None of this removes judgement. Hysteresis makes the result less sensitive to the exact values, but no rule fits every image. <!-- L33 --> <!-- L35 --> What a model buys is a threshold you can explain, and one that moves correctly when the noise or the aperture does.

## The math

| Symbol | Meaning |
|---|---|
| $G_x$, $G_y$ | Sobel derivatives at a pixel |
| $M$, $\theta$ | gradient magnitude and direction |
| $T_H$, $T_L$ | high and low thresholds |
| σ, $s$ | pixel noise and the derivative's noise scale |
| α | fraction of flat pixels above $T_H$ |

**Magnitude.**

$$
M_2 = \sqrt{G_x^2 + G_y^2}, \qquad M_1 = |G_x| + |G_y| = M_2\,(|\cos\theta| + |\sin\theta|) \tag{1}
$$

The two norms agree on the axes and differ by up to √2 on the diagonals; at (r1, c2) they are 476.3 and 640.

**Suppression.** With $p$ the pixel and $p_-$, $p_+$ its neighbours before and after it along the gradient,

$$
M(p) > M(p_-) \quad\text{and}\quad M(p) \ge M(p_+) \tag{2}
$$

is OpenCV's horizontal and vertical test. Interpolation replaces each neighbour by a mix of an axial and a diagonal pixel, with weight $w = \min(|G_x|, |G_y|)/\max(|G_x|, |G_y|)$ on the diagonal: 0.514 at (r1, c1) of the smoothed patch, giving 198.8.

**Hysteresis.** The edges are

$$
E = \bigcup \{\, C : C \text{ an 8-connected component of } \{p \text{ kept by (2)},\ M(p) > T_L\},\ \max_{p \in C} M(p) > T_H \,\} \tag{3}
$$

Every component without a seed disappears whole, and $T_L$ alone decides how far each surviving one extends.

**Thresholds from noise.** On a flat region with Gaussian noise σ, $M_2$ is Rayleigh with scale $s = \sqrt{12}\,\sigma$ at aperture 3, so

$$
P(M_2 > t) = e^{-t^2/2s^2}, \qquad T_H = s\sqrt{2\ln(1/\alpha)}, \qquad \alpha_L = \alpha^{1/r^2} \tag{4}
$$

for $T_L = T_H/r$. With σ = 2 and α = 10⁻⁴ that is 29.7, and a ratio of 2 gives $T_L$ = 14.9 with one flat pixel in ten above it.

**Length.** The a contrario test $N\,H(\mu)^l \le 1$, with the Rayleigh tail for $H$, gives <!-- L39 -->

$$
\mu_{\min}(l) = s\sqrt{2\ln N / l} \tag{5}
$$

A chain $k^2$ times longer needs $1/k$ of the contrast, which is what a ratio of 2 or 3 encodes.

## Implementation: the tooling map

Every entry below maps to the arithmetic above. **None of it was executed for this post**; it comes from source at pinned commits and from MathWorks' documentation. Figure 11 is the same map in one picture.

![Grid comparing OpenCV, scikit-image and MATLAB on smoothing, border, norm, suppression, ties, threshold tests, linking, units and defaults](FIG_11)

*Figure 11 — Three implementations of one method: different smoothing, borders, norms, tie rules and units. Read the row before you carry a threshold from one library to another.*

### OpenCV

| Want | Call | Note |
|---|---|---|
| the full method | `cv2.GaussianBlur(img, (3, 3), 0.8)` then `cv2.Canny(img, low, high, apertureSize=3, L2gradient=True)` | `Canny` itself does not smooth; replicate border; L1 unless `L2gradient=True` <!-- L01 --> <!-- L06 --> |
| your own derivatives | `cv2.Canny(dx, dy, low, high, L2gradient=True)` | dx and dy as 16-bit signed integers; the route for 16-bit or float images <!-- L02 --> |
| a wider derivative | `apertureSize=5` or `7` | multiply thresholds by 12 to 16 (5) or 160 to 256 (7), depending on edge sharpness <!-- L16 --> |

OpenCV's tutorials describe more than the function does. The Python tutorial lists a 5×5 Gaussian as Canny's first step and says `cv.Canny()` puts all the steps in one function, <!-- L14 --> and the C++ tutorial's demo smooths with a 3×3 box `blur` before calling `Canny` with a ratio of 3. <!-- L15 --> The smoothing is yours to add, and its kind and size are part of the thresholds' meaning.

Which code runs is itself a setting. `Canny` first offers the call to a platform layer: in builds with Intel IPP, IPP takes it only when OpenCV runs on a single thread, for single-channel images larger than 3×3 at aperture 3 or 5, and IPP's own suppression is not in OpenCV's source; an OpenCL array goes to a separate kernel. <!-- L44 --> Everything in this post is the code that runs otherwise, and release 4.10.0 has the same rules. <!-- L45 --> If you call `cv2.setNumThreads(1)`, check ties on your own build.

### scikit-image and MATLAB

| Want | Call | Note |
|---|---|---|
| the full method | `skimage.feature.canny(img, sigma=1.0, low_threshold=None, high_threshold=None)` | Gaussian first; L2; interpolated suppression keeping ties; one-pixel border masked; Gaussian border defaults to constant <!-- L17 --> <!-- L19 --> <!-- L21 --> |
| thresholds as percentiles | `canny(img, low_threshold=0.8, high_threshold=0.95, use_quantiles=True)` | percentiles of the magnitude over all pixels, before suppression <!-- L18 --> |
| MATLAB | `edge(I, "canny", [low high], sigma)` | thresholds from 0 to 1; a scalar sets low to 0.4 × high; σ defaults to √2 <!-- L22 --> |

### The worked example, in OpenCV

```python
import numpy as np
import cv2

patch = np.full((5, 5), 40, np.uint8)
patch[:, 3:] = 200
patch[2, 1] = 255

raw = cv2.Canny(patch, 450, 600, L2gradient=True)      # the line alone: low 430 or more, high under 640
smooth = cv2.GaussianBlur(patch, (3, 3), 0.8)
edges = cv2.Canny(smooth, 180, 450, L2gradient=True)   # Canny's ratio works after smoothing

def thresholds(sigma, alpha=1e-4, ratio=2.0):          # from equation (4), aperture 3, L2, no smoothing
    s = 12 ** 0.5 * sigma
    high = s * (2 * np.log(1 / alpha)) ** 0.5
    return high / ratio, high
```

This was not run for this post. The comments state what the worked example predicts: the first call returns the five-pixel line, and so does the second.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** tuning `low` and `high` on one image and carrying them to the next. They are absolute numbers in raw Sobel units, so they change meaning with the image's contrast, the aperture, the norm and whatever smoothing came first. Re-derive them from the noise, or at least from the same pipeline.

- **Expecting `cv2.Canny` to smooth.** It does not; on the patch that is the difference between Canny's ratio working and the ring riding in on the edge. <!-- L01 -->
- **Changing `apertureSize` and keeping the thresholds.** Every magnitude grows 12 to 16 times from 3 to 5; edges flood in. <!-- L16 -->
- **Leaving the L1 default on oblique edges.** Diagonals read up to 41% high, and a tie it creates can delete an edge pixel, as at (r1, c2). <!-- L06 -->
- **Reading the thinned line as the edge's position.** OpenCV keeps the left or upper pixel of a tie, and every implementation rounds to the grid; fit a parabola when position matters. <!-- L07 --> <!-- L31 -->
- **A low threshold that lets the background touch.** One candidate at a corner joins a noise blob or a texture to a real edge, as the ring joined the step.
- **Percentile thresholds on an edge-dense crop.** On the patch the 80th percentile is the edge itself. <!-- L27 -->
- **Expecting junctions to stay connected.** Suppression breaks the weaker edge at a T-junction. <!-- L38 -->
- **Treating smoothing as free.** It is what made the ratio work here, but on real images it also rounds corners and makes nearby contours interact. <!-- L34 --> Its σ is a choice of scale, the subject of the later spoke *Scale Space and SIFT: Why σ Is a Search Dimension*.

## Key takeaways

- **Hysteresis grades chains, not pixels.** The high threshold decides which chains exist; the low threshold decides where each ends.
- **Suppression is three decisions: bins or interpolation, the tie rule, and the norm.** On the patch they decide between zero, one and two edge pixels a row, and the L1 default deletes two rows of the edge.
- **`cv2.Canny` does not smooth, and smoothing is what made Canny's ratio work here:** it detached the impulse's ring from the step.
- **Thresholds are in raw gradient units** — 4h for a step at aperture 3, 48h at 5 — so they belong to the operator and the noise, not to the image.
- **Set them from the noise:** $T_H = s\sqrt{2\ln(1/\alpha)}$ with $s = 3.46\,\sigma$, and a low threshold a half to a third of it, which under a Rayleigh noise model is the contrast a chain of 4 to 9 pixels needs.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: one more suppression test

Compute $G_x$, $G_y$ and the L2 magnitude at (r3, c2) of the raw patch, find its bin, and run OpenCV's test.

**Self-check:** the gradient (425, −215), a diagonal bin, and a verdict with the neighbour that decides it.

<details><summary>Answer</summary>

$G_x$ = (200 − 255) + 2 × 160 + 160 = 425; $G_y$ = (40 − 255) + 0 + 0 = −215, so the magnitude is 476.3 at −26.8°. That is a diagonal bin, and because the two derivatives have opposite signs OpenCV compares with (r2, c3) above-right and (r4, c1) below-left. (r2, c3) holds 640, so (r3, c2) is suppressed, as (r1, c2) was.

</details>

### E2 — Inspect: the clean band on the raw patch

From Figure 4's middle panel, what is the largest ratio of high to low threshold that still returns the step's line alone, under L2?

**Self-check:** a number and the two magnitudes it comes from.

<details><summary>Answer</summary>

Just under 640 / 430 = 1.49. The low threshold must reach the ring's 430, and the high one must stay below the line's 640.

</details>

### E3 — Predict: a fainter impulse

Replace the 255 by 120, so the impulse stands 80 above its neighbours. Before computing, predict whether `cv2.Canny(patch, 200, 600, L2gradient=True)`, with no smoothing, now returns the line alone. Then compute the ring's largest magnitude.

**Self-check:** the ring's largest magnitude, and a yes or no with the reason. A right answer for the wrong reason does not count.

<details><summary>Answer</summary>

Yes. The ring scales with the impulse: (r1, c1) and (r2, c0) read 2 × 80 = 160 and (r1, c0) 113.1, all below the low threshold of 200, so they are never candidates. The step still reads 640 on its line, and (r1, c2) now reads 565.7, below its neighbour, so (r1, c3) survives. The ratio of 3 works because the ring's peak is a quarter of the step's, where with 255 it was two-thirds.

</details>

### E4 — Diagnose: three dots

A colleague runs `cv2.Canny(patch, 450, 600)` on the raw patch, expecting the step's line, and gets three isolated pixels at (r0, c2), (r2, c3) and (r4, c2). Find the cause, say what `L2gradient=True` returns with the same thresholds, and why.

**Self-check:** the cause named with the pixel and the number that prove it; the five pixels predicted.

<details><summary>Answer</summary>

The default L1 magnitude. At (r1, c2) it reads 425 + 215 = 640, tying (r1, c3), which then fails OpenCV's strict test against its left neighbour, while (r1, c2) loses its diagonal test to (r2, c3); the same happens on r3. With `L2gradient=True`, (r1, c2) reads 476.3, (r1, c3) survives, and with the low threshold above the ring's 430 the output is (r0, c2), (r1, c3), (r2, c3), (r3, c3) and (r4, c2), connected.

</details>

## References

1. Canny, J. "A Computational Approach to Edge Detection." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 8(6):679–698, 1986. doi:10.1109/TPAMI.1986.4767851. [PDF](https://cecas.clemson.edu/~ahoover/ece431/refs/Canny.pdf)
2. Grompone von Gioi, R., and Randall, G. "A Sub-Pixel Edge Detector: an Implementation of the Canny/Devernay Algorithm." *Image Processing On Line* 7:347–372, 2017. [doi:10.5201/ipol.2017.216](https://doi.org/10.5201/ipol.2017.216)
3. Spontón, H., and Cardelino, J. "A Review of Classic Edge Detectors." *Image Processing On Line* 5:90–123, 2015. [doi:10.5201/ipol.2015.35](https://doi.org/10.5201/ipol.2015.35)
4. Papari, G., and Petkov, N. "Edge and Line Oriented Contour Detection: State of the Art." *Image and Vision Computing* 29(2–3):79–103, 2011. doi:10.1016/j.imavis.2010.08.009. [PDF](https://www.cs.rug.nl/~petkov/publications/2011ivc-contour_survey.pdf)
5. Li, D., Sullivan, G. D., and Baker, K. D. "Edge Detection at Junctions." *Proceedings of the Alvey Vision Conference 1989*, 21.1–21.6. doi:10.5244/C.3.21. [PDF](https://www.bmva-archive.org.uk/bmvc/1989/avc-89-021.pdf)
6. Desolneux, A., Moisan, L., and Morel, J.-M. "Edge Detection by Helmholtz Principle." *Journal of Mathematical Imaging and Vision* 14(3):271–284, 2001. doi:10.1023/A:1011290230196. [PDF](https://desolneux.perso.math.cnrs.fr/papers/DMM_Edge_01.pdf)
7. Hancock, E. R., and Kittler, J. "Adaptive Estimation of Hysteresis Thresholds." *Proceedings of CVPR 1991*, 196–201. [doi:10.1109/CVPR.1991.139687](https://doi.org/10.1109/CVPR.1991.139687)
8. Henstock, P. V., and Chelberg, D. M. "Automatic Gradient Threshold Determination for Edge Detection." *IEEE Transactions on Image Processing* 5(5):784–787, 1996. [doi:10.1109/83.499917](https://doi.org/10.1109/83.499917)
9. OpenCV source, commit 802cf95: `canny.cpp`, `canny.simd.hpp`, `spatialgradient.cpp`, `deriv.cpp`, `imgproc.hpp`, `core/base.hpp`, and the IPP layer's `canny_ipp.cpp` and `ipp_hal_imgproc.hpp`. <https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src> (accessed 2026-10-12)
10. OpenCV documentation, commit 802cf95: the C++ and Python Canny tutorials and `CannyDetector_Demo.cpp`. <https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760/doc> (accessed 2026-10-12)
11. scikit-image source, commit b700edc: `feature/_canny.py`, `_canny_cy.pyx`, `util/_value_rescaling.py`. <https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/feature> (accessed 2026-10-12)
12. MathWorks. "edge — Find edges in 2-D grayscale image." Image Processing Toolbox documentation, release R2026b. <https://www.mathworks.com/help/images/ref/edge.html> (accessed 2026-10-12)
13. OpenCV source, tag 4.10.0: `canny.cpp` and `core/private.hpp`. <https://github.com/opencv/opencv/blob/4.10.0/modules/imgproc/src/canny.cpp> (accessed 2026-10-12)
