---
title: "Scale Space and SIFT: Why σ Is a Search Dimension"
slug: scale-space-and-sift
date: 2026-10-13
updated: 2026-10-13
summary: "A fixed σ sees each structure at one size, so SIFT searches σ. Worked by hand on a 5×5 patch: one DoG octave, the 26-neighbour test, the fit, the edge test."
tags: [algorithms, image-processing, scale-space, sift, feature-detection, difference-of-gaussians, opencv]
category: algorithms
categories: [algorithms]
tier: L4
difficulty: advanced
series: image-processing
series_position: 10
prerequisites: ["the scale-normalised Laplacian from part 2 of this series", "Gaussian blur as a convolution", "a second-order Taylor expansion and a 3×3 linear solve"]
reading_minutes: 38
cover_image_url: "COVER"
cover_image_alt: "A grid split by a vertical step with a bright square, and a stack of blurred copies above it with one point marked on the middle level"
canonical_url: "https://canery.in/blogs/scale-space-and-sift"
---

> [!NOTE]
> **Insights** — An image structure has no built-in size, so a detector that fixes σ describes the same structure differently at every zoom; SIFT instead searches σ as a third coordinate, for extrema of a scale-normalised Laplacian, and returns each structure at a σ proportional to its size. On the series' 5×5 patch enlarged seven times, one octave of SIFT's difference-of-Gaussians pyramid finds two candidates: it keeps the bright square at σ = 2.51 and rejects the other with the edge test, at a curvature ratio of 23. At that same σ, the square enlarged fourteen times shows up as four corners. The Gaussian does the searching because it is the only kernel that is separable and never enhances an extremum as σ grows; keep only linearity, a semigroup, scale invariance and positivity, and the Poisson kernel qualifies too.

**Level:** advanced · **You need:** *The Laplacian by Hand* (part 2 of this series) for the scale-normalised Laplacian, Gaussian blur as a convolution, a second-order Taylor expansion, and a 3×3 linear solve · **Time:** ~38 min

This is part 10 of *Image Processing by Hand*. Part 1 drew σ as an axis and named this post. Part 2, *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening*, showed that the scale-normalised Laplacian peaks at a structure's size and that a difference of Gaussians carries the normalisation for free. Part 9, *The Structure Tensor: Harris, Shi–Tomasi, and Optical Flow*, left the scale half of Harris–Laplace for here. This post runs the search on the shared patch and asks why the Gaussian is the kernel allowed to do it.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Searched, not set](#why-must-scale-be-searched-rather-than-set) · [Why the Gaussian](#why-is-the-gaussian-the-only-kernel-allowed-to-search) · [Octaves](#how-does-sift-sample-σ) · [Refine and reject](#refine-then-reject) · [Orientation and descriptor](#what-is-the-scale-for) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. The enlarged patch is a sum of rectangles, and the Gaussian blur of a rectangle has a closed form, so every scale-space value below is evaluated from that closed form at pixel centres. Three cross-checks in plain Python, using only its `math` module, are not published: a pyramid built from sampled kernels, a replay of OpenCV's SIFT detection rules transcribed from its source, and the scale-adapted Harris measure. No OpenCV, scikit-image or MATLAB call was executed: library behaviour comes from source read at pinned commits and from MathWorks' documentation. There are no timings or measured curves. Figures that draw curves or surfaces evaluate closed forms, and their captions say so.

## Why this matters

Give OpenCV's SIFT detector the series' 5×5 patch and it returns nothing: it never looks within five pixels of the border, which is all of a 5×5 image. <!-- L56 --> Enlarge the patch seven times, so that each pixel becomes a 7×7 block, and it returns the bright square, a quarter of a pixel down and to the right of the square's centre, because of a default that the library's own log calls deprecated. <!-- L71 --> Enlarge it fourteen times and the same square comes back at twice the size. Ask a detector with a fixed σ instead, and the bigger square shows up as four corners.

Those are the subject in four sentences. A keypoint is a position and a size; the size is searched for, not set; the kernel that does the searching is chosen by axioms that not everyone agrees on; and a library's version of the search has defaults that move your points. Knowing which is which tells you what a keypoint's `size` means, which keypoints to distrust, and why a detector tuned at one zoom fails at another.

## The problem

An image structure does not come with a size attached. The patch's bright pixel is one pixel wide in the original, seven after enlarging the patch seven times, fourteen after fourteen; a camera does the same to an object that moves away from it. A feature detector must return, for each structure, a position and a size such that enlarging the image by a factor $s$ moves the position to the corresponding point and multiplies the size by $s$. That property is **scale covariance**. It is what lets a feature found in one photograph be matched in another taken from a different distance: the ratio of the two sizes is the zoom between them. <!-- L45 -->

A filter with a fixed σ cannot have it. Part 2's tool was the **scale-normalised Laplacian**, $N(x, y; \sigma) = \sigma^2 \nabla^2 L$: the Laplacian of the image blurred by a Gaussian of standard deviation σ, multiplied by $\sigma^2$ so that the result carries no unit of length. At the centre of a square of side $\ell$ and contrast $A$ it equals $-4A\,u\,\varphi(u)\,\big(2\Phi(u) - 1\big)$, with $u = \ell/(2\sigma)$, where $\varphi$ and $\Phi$ are the standard normal density and its cumulative distribution. It depends on σ only through the ratio $\ell/\sigma$. A detector at one σ reads small squares and large squares at different points of that curve; what it reports is a fact about $\ell/\sigma$, not about the square.

The way out is to stop choosing. **Scale space** is the family of blurred images $L(x, y; \sigma) = G_\sigma * f$ for every σ > 0, the Gaussian $G_\sigma$ having standard deviation σ and variance $t = \sigma^2$. <!-- L01 --> Treat σ as a third coordinate and look for points where the normalised response is an extremum in $x$, $y$ and σ together. The σ found there is the structure's **characteristic scale**, and when the image is enlarged by $s$ it is multiplied by $s$, because the normalised response at $(s x, s \sigma)$ in the enlarged image equals the response at $(x, \sigma)$ in the original. <!-- L24 --> <!-- L25 -->

Two questions follow, and they are this post's. Why must the search range over σ rather than settle on one good value? And why must the blur be Gaussian: what goes wrong if a box filter, or any other smoothing kernel, generates the scales? The constraint behind both is cost. σ is continuous, but each sample of it is a full-image blur, so it can only be sampled at a handful of values.

## Worked example

The patch is the series' 5×5 8-bit patch: every row is `40 40 40 200 200` except r2, which has an impulse of 255 at (r2, c1). Enlarged seven times, each pixel becomes a 7×7 block, so the image is 35×35: a square of 255 in columns 7–13 and rows 14–20, centred on pixel (10, 17), and a step from 40 to 200 between columns 20 and 21. Coordinates below are (x, y), column first, as OpenCV reports keypoints.

Why seven? The octave used below searches σ from about 2 to 3.2. The ×5 patch's square would peak below that range, where SIFT finds it only in an extra octave built on a doubled image; ×7 puts it on the middle level, where every neighbour of the test below exists.

### Step 1: the octave, in closed form

Blurring a step of height $h$ at $x_0$ by a Gaussian of width σ gives $h\,\Phi\big((x - x_0)/\sigma\big)$. A square is a step up and a step down in each direction, and a 2-D Gaussian blur factors into a horizontal and a vertical one, so the whole scale space of the enlarged patch, with its border extended outward, is one line:

$$
L(x, y; \sigma) = 40 + 160\,\Phi\!\left(\tfrac{x - 20.5}{\sigma}\right) + 215\left[\Phi\!\left(\tfrac{x - 6.5}{\sigma}\right) - \Phi\!\left(\tfrac{x - 13.5}{\sigma}\right)\right]\left[\Phi\!\left(\tfrac{y - 13.5}{\sigma}\right) - \Phi\!\left(\tfrac{y - 20.5}{\sigma}\right)\right]
$$

The half-pixel offsets are the block edges: pixel 7's left edge is at 6.5. Following Lowe, one **octave** (a doubling of σ) is split into $s = 3$ intervals, so neighbouring scales differ by $k = 2^{1/3}$, starting at σ = 1.6. <!-- L03 --> <!-- L07 --> That gives six Gaussian images, at σ = 1.600, 2.016, 2.540, 3.200, 4.032 and 5.080. Subtracting neighbours gives five **difference-of-Gaussians** (DoG) images, $D_i = L(\sigma_{i+1}) - L(\sigma_i)$, the stand-in for the normalised Laplacian that Part 2 introduced. <!-- L02 --> Extrema are searched for only in the middle three, $D_1$ to $D_3$, because each needs a level above and below. Figure 1 shows the octave.

![Six blurred copies of the enlarged patch and the five differences between them, with the square's minimum and one maximum between square and step marked on the middle difference](FIG_01)

*Figure 1 — One octave on the patch enlarged seven times. The square becomes a dark well in the differences, deepest on the middle level; the step becomes a pair of ridges. Evaluated from the closed form at pixel centres.*

### Step 2: the 26-neighbour test

A sample is a candidate if it is larger than all 26 neighbours in the 3×3×3 block around it in $x$, $y$ and level, or smaller than all of them. <!-- L04 --> At pixel (10, 17) on level 2, the values are, in grey levels:

```text
           level 1 (σ 2.016)          level 2 (σ 2.540)          level 3 (σ 3.200)
y = 16   -29.038 -30.586 -29.024    -31.126 -33.169 -30.927    -28.432 -29.723 -27.516
y = 17   -30.589 -32.216 -30.575    -33.223 -35.379 -33.024    -30.056 -31.417 -29.140
y = 18   -29.038 -30.586 -29.024    -31.126 -33.169 -30.927    -28.432 -29.723 -27.516
          x = 9     10      11        9      10      11          9      10      11
```

The centre, −35.379, is below every neighbour; the closest in value is −33.223, one pixel to its left. Rows 16 and 18 are equal because the patch is symmetric about row 17, and columns 9 and 11 differ because the step pulls on the right side. Figure 2 draws the block. Over the whole octave, exactly two samples pass: this one, and (17, 17) on level 2, a maximum of +14.740 in the gap between the square and the step.

![Three 3×3 grids of numbers for the levels above, at and below the candidate, with the centre −35.379 highlighted as lower than all 26 others](FIG_02)

*Figure 2 — The 27 values of the test at (10, 17). Every one of the 26 comparisons goes the same way. Evaluated from the closed form.*

### Step 3: the fit

The extremum of the continuous function is not on the sample. Brown and Lowe fit a second-order Taylor expansion of $D$ around the sample and take its extremum, $\hat{x} = -H^{-1} g$, where $g$ is the gradient and $H$ the 3×3 Hessian in $(x, y, \text{level})$, both from differences of neighbouring samples. <!-- L10 --> <!-- L16 --> At (10, 17):

$$
g = \begin{bmatrix} 0.0995 \\ 0 \\ 0.3993 \end{bmatrix}, \qquad H = \begin{bmatrix} 4.5102 & 0 & 0.2256 \\ 0 & 4.4198 & 0 \\ 0.2256 & 0 & 7.1241 \end{bmatrix}, \qquad \hat{x} = \begin{bmatrix} -0.0193 \\ 0 \\ -0.0554 \end{bmatrix}
$$

The fit moves the point 0.02 pixel left, away from the step, and 0.055 of a level down in scale. The keypoint's σ is $1.6 \times 2^{(2 - 0.0554)/3} = 2.508$. The value at the extremum is $D(\hat{x}) = D + \tfrac12 g^{\top}\hat{x} = -35.391$, or 0.139 on a 0-to-1 intensity scale, far above Lowe's contrast threshold of 0.03. <!-- L10 --> Figure 3 shows the fit along scale.

![The DoG value at the square's centre on five levels, a parabola through the middle three, and its lowest point just below level 2](FIG_03)

*Figure 3 — Scale is refined like position. The sampled levels bracket a minimum that sits 0.055 of a level below level 2. The continuous curve is the closed form; its own minimum, at σ = 2.480, is 1% from the fitted 2.508. Evaluated from the closed form.*

### Step 4: the second candidate, and the edge test

At (17, 17) the same fit gives an offset of +0.38 pixel toward the step and −0.12 of a level, and $D(\hat{x}) = 15.073$, or 0.059: above the contrast threshold too. What separates the two candidates is shape. Lowe's last test takes the 2×2 Hessian of $D$ in $x$ and $y$ and rejects a point whose principal curvatures, the Hessian's eigenvalues, differ by a factor of more than $r = 10$, through ${\operatorname{Tr}(H)^2}/{\operatorname{Det}(H)} \lt (r + 1)^2/r = 12.1$. <!-- L12 -->

At the square, $D_{xx} = 4.510$ and $D_{yy} = 4.420$, so the test value is 4.0004, essentially the minimum of 4 that two equal curvatures give: a round bowl. At (17, 17), $D_{xx} = -3.804$ and $D_{yy} = -0.180$: the function curves sharply across the gap and hardly at all along it, an eigenvalue ratio of 21.1 and a test value of 23.2. It is rejected. Figure 4 draws both surfaces.

![Contour maps of the DoG around both candidates: nearly circular rings around the square's centre, long vertical contours around the gap point](FIG_04)

*Figure 4 — The edge test reads the shape of the extremum. Around the square the contours are round; around the gap point they run along the step, whose own DoG ridge the square has bent into a weak maximum. Evaluated from the closed form.*

### The scorecard

| candidate | D | offset (x, y, level) | abs D(x̂), 0–1 scale | Tr²/Det | verdict |
|---|---|---|---|---|---|
| (10, 17), level 2: the square | −35.38 | (−0.02, 0, −0.06) | 0.139 | 4.00 | kept, σ = 2.51 |
| (17, 17), level 2: between square and step | +14.74 | (+0.38, 0, −0.12) | 0.059 | 23.2 | rejected by the edge test |

A library builds this octave from sampled, truncated kernels on the pixel grid rather than from the closed form. Replaying that construction in plain Python, with either border rule and with the blur added level by level, moves the values by 1% to 5% and the rejected point's test value to between 15.3 and 23.2; no decision changes. Note what is missing from the list: the step. A long straight edge gives no candidate of its own, for a reason the section after next explains.

## Intuition

Searching σ is like measuring a coin in a photograph by laying circular templates of every size over it and keeping the best fit. The best template's size tells you the coin's size, and if the photograph is enlarged the best template grows with it. A single template tells you only how well one size fits. The normalised Laplacian is that template: a centre-surround kernel whose response at the centre of a square peaks when its centre lobe matches the square.

The peak is at σ = 0.398 times the side, 0.17% below the value for a disc of the same area, and its height is the same for every square, 0.720 times the contrast, or 154.9 for the patch's 215. Figure 5 plots the curve for four sizes; on a logarithmic σ axis they are one curve, shifted.

![Four identical bell-shaped curves of normalised response against σ on a log axis, peaking at σ 1.19, 1.99, 2.79 and 5.58 for squares of side 3, 5, 7 and 14, all at height 154.9](FIG_05)

*Figure 5 — Searching σ turns size into position on a log axis. Squares of side 3, 5, 7 and 14, contrast 215: one curve, slid by the logarithm of the side. A detector at one σ reads each square at a different height. Closed forms, for isolated squares.*

The analogy breaks in two places. A coin has one size, but an image structure can have several: the ×14 square has corners as well as a body. And some structures have none: a straight edge looks the same at every magnification, so no template fits it best.

## Why must scale be searched rather than set?

### At a fixed σ, the bigger square is four corners

Take the DoG level that found the ×7 square, the difference between σ = 2.540 and 3.200, and apply it unchanged to the patch enlarged fourteen times. The ×7 square is one well, −35.38 at its centre. The ×14 square is not: its deepest minima are four, each −20.43, three pixels in from each corner, and the centre reads only −9.66, half as deep. Figure 6 shows both. Lindeberg found the same in natural images: a blob detector run at one scale ranks structures of one size highest, while a search over scale treats every size between the image's finest and coarsest scales alike. <!-- L26 -->

![The same DoG level on the ×7 and ×14 patches: one minimum at the ×7 square's centre, four near the ×14 square's corners, and one at the ×14 square's centre on the level twice as coarse](FIG_06)

*Figure 6 — Set σ, and the answer depends on the zoom; search it, and only the size changes. Left and middle: one DoG level on the two enlargements. Right: the ×14 patch on the level whose σ is twice as large, where its one minimum returns, at the same value. Evaluated from the closed form.*

Searched, the ×14 square comes back on the level whose σ is twice as large, with the same value. The replay of OpenCV's rules, with precise upscaling, puts it at (20.46, 34.50) with size 10.03, against (9.98, 17.00) and size 5.03 for ×7: the image of the smaller point under $x \to 2x + 0.5$, which maps a block's centre at ×7 to the same block's centre at ×14.

### The normalisation is what makes the search covariant

Without the $\sigma^2$, a search over σ is useless: blurring never raises a local maximum or lowers a local minimum, so derivative amplitudes fall as σ grows and an unnormalised search ends at the finest scale it tries. <!-- L23 --> Lindeberg's **normalised derivatives** multiply an $m$-th derivative by $\sigma^m$. With that factor, enlarging the image by $s$ leaves every normalised derivative unchanged at matching points and scales, so maxima over scale move to $(s x, s \sigma)$ and nothing else about them changes. <!-- L24 --> That is why the curves in Figure 5 have one height: a threshold on the normalised response means the same thing at every size.

### The step has no scale

A straight step is the structure the normalisation cannot size. Its normalised second derivative along its ridge, where the blurred step curves most, is $160\,\varphi(1) = 38.7$ at every σ, and its normalised gradient at the edge is $160\,\varphi(0) = 63.8$ at every σ. Lindeberg showed the general case: with this normalisation a diffuse step's edge strength grows monotonically with σ and would select an infinitely large scale, so he used a weaker normalisation, $\gamma = 1/2$ in his notation, to give edges a scale equal to their own blur. <!-- L27 --> In the space of position and scale the step is a ridge of constant height, not a peak. Figure 7 shows the difference.

![Two heat maps over position and σ: along the square's row, one peak at x 10 and σ 2.78; along the top row, two straight diagonal ridges of constant height on either side of the step](FIG_07)

*Figure 7 — A blob is a peak in position and scale; an edge is a ridge. Left: the normalised Laplacian along row 17, through the square. Right: along row 0, far from the square; the step's ridges run diagonally, one pixel out per unit of σ, at a constant 38.7. Closed forms.*

On a ridge, whether a sample looks like an extremum depends on how the grid happens to cut it. In this octave no step sample passes the 26-neighbour test; on other grids some do, and the edge test exists to remove them.

### Harris–Laplace: the scale half

Part 9 built the scale-adapted structure tensor and its Harris maxima per level, the position half of **Harris–Laplace**. Mikolajczyk and Schmid's detector computes Harris maxima on levels $\sigma_n = 1.4^n \sigma_0$ with a derivative scale of 0.7 times the integration scale, then keeps a point only if the normalised Laplacian at its level exceeds the levels on either side. <!-- L41 --> <!-- L42 --> <!-- L43 --> They chose the Laplacian for scale because the Harris measure itself rarely peaks over scale, and the Laplacian found correct characteristic scales most often. <!-- L44 -->

On the ×7 patch, with $\sigma_0 = 1$: at integration scale 1.96, Harris has four maxima, near the square's corners, at (8, 15), (12, 15), (8, 19) and (12, 19). Their normalised Laplacian is −83.2 there, against −89.1 one level finer and −86.9 one level coarser: a minimum over scale, so all four are rejected. At 2.744 the only Harris maximum is (10, 17), and its Laplacian, −154.6, beats −115.2 and −127.5 on either side. Harris–Laplace returns one point, the square, with a characteristic scale of 2.744, the same structure SIFT keeps.

## Why is the Gaussian the only kernel allowed to search?

### What the search asks of the kernel

The search compares responses across σ, so the kernel that generates the scales must not put anything into the image that was not already there; otherwise an extremum found at a coarse scale might belong to the kernel. It must let each scale be computed from the previous one: blurring by $\sigma_1$ and then by $\sigma_2$ must equal one blur, a **semigroup**. And it must have no preferred size, because a preferred size is exactly what the search is trying to avoid. Add linearity, shift invariance and rotation invariance, and the question is which kernels remain.

### The derivations

The answer has a long history. Weickert, Ishikawa and Imiya traced linear scale space to Iijima's axioms in Japan, two decades before the work usually cited. <!-- L38 --> <!-- L37 --> Witkin introduced scale-space filtering in 1983 and observed that, for a 1-D signal under Gaussian smoothing, zero-crossings may appear as σ decreases but existing ones cannot in general disappear, which made them trackable from coarse to fine. <!-- L17 --> <!-- L18 --> Koenderink required **causality**: every feature at a coarse scale must have a cause at a finer one; his formal version of it leads to the diffusion equation, whose solution is Gaussian blurring. <!-- L19 --> Babaud, Witkin, Baudin and Duda proved the Gaussian unique in a broad class of 1-D kernels, and Yuille and Poggio proved that in any dimension only the Gaussian creates no generic zero-crossings of the Laplacian as scale increases. <!-- L20 --> <!-- L21 -->

Lindeberg's version is the one closest to what a detector needs. Require linearity, shift invariance, a semigroup, some regularity, and **non-enhancement of local extrema**: at a local maximum the value must not increase with scale, and at a local minimum it must not decrease. Those force a diffusion equation; mirror symmetry and rotational symmetry then leave only the Gaussian. <!-- L28 -->

### The Poisson kernel, and what "only" depends on

Change the axioms and the answer changes. Pauwels and colleagues showed that linear, isotropic convolution with a semigroup and scale invariance leaves a one-parameter family, of which the Gaussian is one member. <!-- L33 --> Felsberg and Sommer took a second member, the Poisson kernel, and showed that it is linear, shift-invariant, a semigroup, scale- and rotation-invariant and positivity-preserving: a counterexample to Iijima's uniqueness proof, which had silently assumed a smooth frequency response at zero. <!-- L34 --> What it lacks is **separability**: a 2-D kernel that is the product of two 1-D kernels. Adding separability, or closure under all affine maps, leaves only the Gaussian. <!-- L35 --> A separate theorem says the same from the other side: every rotation-invariant separable function of two variables is a Gaussian or zero. <!-- L39 -->

The Poisson kernel also fails non-enhancement; only the Gaussian has it, so it fails Koenderink's causality in its strict form, though it satisfies a relaxed form in which every level surface connects to scale zero. <!-- L70 --> Members of the family past the Gaussian are not even positive: they break the maximum–minimum principle outright. <!-- L37 --> So "the Gaussian is the only scale-space kernel" is true under non-enhancement or under separability, and false under the bare list of linearity, a semigroup, invariance and positivity. Figure 8 lays the requirements against four kernels.

![A grid of four kernels against seven requirements: the Gaussian meets all; the Poisson kernel fails non-enhancement and separability; the box fails rotation invariance and the semigroup; the sampled Gaussian meets them only approximately](FIG_08)

*Figure 8 — Which requirement picks the Gaussian. Linearity, a semigroup and scale invariance admit the Poisson kernel; non-enhancement or separability excludes it. Box ∗ box is a triangle, not a box, so boxes are no semigroup. Entries from the cited theorems and, for the box, from its definition.*

### In two dimensions, even the Gaussian creates extrema

There is a catch in the guarantee itself. "Blurring never creates a new local extremum" holds for 1-D signals; in two or more dimensions what holds is non-enhancement. <!-- L29 --> <!-- L36 --> Kuijper's analysis of Gaussian scale space found its critical points generically annihilated with increasing scale and sometimes created, in extremum–saddle pairs. <!-- L40 --> What survives in 2-D is the weaker promise: the value at a local maximum of the blurred image never rises as σ grows, and at a local minimum never falls.

### What SIFT needs from the kernel

SIFT leans on the Gaussian's properties three times. Separability makes each blur two 1-D passes. <!-- L29 --> The semigroup lets each level be blurred from the one before, by a small extra σ, and each octave start from a halved copy of the previous octave's level at twice its starting σ. <!-- L28 --> And the heat equation turns a difference of two blurs into the normalised Laplacian. <!-- L02 --> A sampled Gaussian keeps separability exactly and the semigroup only approximately: the error is below $10^{-4}$ on a 0-to-1 scale for σ of 0.7 and above, and the proper discrete kernel is a different one. <!-- L48 --> <!-- L22 --> SURF chose to give the guarantees up: it replaces Gaussian second derivatives by box filters evaluated at constant cost, the 9×9 box standing in for σ = 1.2, and enlarges the filter instead of shrinking the image. <!-- L51 --> Its authors noted that box filters keep high frequencies a zoomed-out view loses, which can limit scale invariance. <!-- L52 --> Drop linearity instead and you arrive at the edge-preserving diffusion of Part 7, *Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion*: useful for denoising, but no longer a neutral ruler.

## How does SIFT sample σ?

### Octaves and intervals

Lowe's construction, Figure 9, has one rule per octave. Divide the doubling of σ into $s$ intervals, $k = 2^{1/s}$; make $s + 3$ Gaussian images so that the $s$ middle DoG levels each have a neighbour above and below; then start the next octave from the image whose σ is twice the first, taking every second pixel. <!-- L03 --> With $s = 3$ and σ = 1.6, the extra blurs within an octave are 1.226, 1.545, 1.947, 2.453 and 3.090: each takes the previous level to the next, because blurs combine in variance. <!-- L55 -->

![Five octaves of the pyramid for the 35×35 input: 70, 35, 17, 8 and 4 pixels wide, six blurred levels each with their σ, the extra blur on each arrow, and the square found on level 2 of the 35-pixel octave](FIG_09)

*Figure 9 — The pyramid OpenCV would build for the ×7 patch. The input is doubled first; detection needs 5 pixels of margin, so the last two octaves contribute nothing. The square is found in the octave at the input's own resolution. Sizes and σ from the transcribed rules.*

Before the first octave the input is doubled, by linear interpolation. Lowe assumes the camera has already blurred the image by at least σ = 0.5, the minimum needed to avoid significant aliasing, so the doubled image has σ = 1.0 and needs only $\sqrt{1.6^2 - 1^2} = 1.249$ more. <!-- L08 --> <!-- L54 --> Doubling raised the number of stable keypoints by almost a factor of four in his experiments. <!-- L08 --> OpenCV then builds as many octaves as $\operatorname{round}(\log_2 70 - 2) + 1 = 5$ for the doubled 70-pixel image. <!-- L55 -->

### Why three intervals and σ = 1.6, and why that is contested

No sampling interval catches every extremum, because two extrema can be arbitrarily close, as when an ellipse stretches from one maximum into two, and such close pairs are unstable anyway; so the sampling is a trade-off, and Lowe chose it by experiment. <!-- L05 --> His 1999 detector used a ratio of √2 between scales and resampled each level at a spacing of 1.5 pixels. <!-- L15 --> The 2004 values came from experiments on 32 images, rotated and scaled by random amounts with 1% noise added: repeatability was highest with three scales per octave, because finer sampling found more extrema that were on average less stable; and it kept rising with the prior σ, of which 1.6 was close to optimal at acceptable cost. <!-- L06 --> <!-- L07 -->

That conclusion is not settled. Rey-Otero, Morel and Delbracio simulated scale changes under controlled sampling and found many of SIFT's keypoints unstable even in favourable conditions. Sampling 15 scales per octave instead of 3, with finer spatial sampling, improved stability, and a wrong assumed camera blur or aliasing degraded invariance. <!-- L50 --> The two studies measure different things: Lowe counted keypoints that reappear within a factor of √2 in scale and σ in position, while the later study asked how reliably the same scale-space extremum is found at all.

### What one DoG level measures

The heat equation, written in σ, says $\partial L/\partial \sigma = \sigma \nabla^2 L$. Integrate it from σ to $k\sigma$ and the difference of two blurs is exact:

$$
D(\sigma) = L(k\sigma) - L(\sigma) = \int_{\sigma}^{k\sigma} \tau^2 \nabla^2 L \,\frac{d\tau}{\tau} = \int_{\ln \sigma}^{\ln \sigma + \ln k} N \, d(\ln \tau)
$$

A DoG level is the normalised Laplacian averaged over one interval of log-scale, times $\ln k = 0.231$. Lowe's $(k - 1) = 0.260$ and Lindeberg's variance-based $(k^2 - 1)/2 = 0.294$ are first-order versions of the same factor, and since all three are constants, none moves an extremum. <!-- L02 --> <!-- L30 --> On the patch the peak DoG over the peak normalised Laplacian is 35.42/154.67 = 0.229.

The averaging does move the scale. The DoG with the lower edge at σ peaks when the interval straddles the Laplacian's peak, so it reports about $\sqrt{k}$ less: 2.480 against 2.776 at the square's centre, a ratio of 1.119 against $\sqrt{k} = 1.122$. Figure 10 shows it. A keypoint's σ in SIFT is by definition the smaller Gaussian of its pair, <!-- L09 --> so SIFT's sizes and a Laplacian blob detector's sizes for the same structure differ by about 12%. Within one detector the factor is constant and covariance survives.

![The normalised Laplacian at the square's centre against log σ, peaking at 2.78, and the DoG divided by ln k, the same curve averaged over one interval, peaking at 2.48](FIG_10)

*Figure 10 — A DoG level is a moving average of the normalised Laplacian over one interval of log σ, so its peak arrives √k early. Closed forms on the ×7 patch.*

## Refine, then reject

### The fit

The quadratic fit of step 3 matters most at coarse octaves, where one sample spans many input pixels. <!-- L16 --> If any offset exceeds 0.5 the extremum is nearer another sample; OpenCV moves there and refits, up to five times, and drops the point if it has not settled. <!-- L10 --> <!-- L57 -->

### Contrast, in three units

The contrast test compares abs $D(\hat{x})$ with a threshold, and the threshold's units differ by implementation. Lowe used 0.03 on a 0-to-1 scale. <!-- L10 --> OpenCV's `contrastThreshold` of 0.04 is divided by the number of layers, 3, so it is 0.0133, and its documentation says to pass 0.09 for Lowe's value; candidates must also exceed 1 grey level before any fitting. <!-- L53 --> <!-- L56 --> The IPOL description uses 0.015 for three scales per octave, rescaled for other sampling, and MATLAB defaults to 0.0133. <!-- L46 --> <!-- L69 --> The patch's square passes all of them at 0.139, and so does the rejected point at 0.059. In Lowe's example image the contrast test took 832 extrema to 729, and the edge test took those to 536. <!-- L11 --> The stability study found the contrast threshold ineffective at removing unstable detections anyway. <!-- L50 -->

### The edge test is Harris's ratio test

Write $t$ for the ratio of the smaller to the larger principal curvature. The edge test $\operatorname{Tr}^2/\operatorname{Det} \lt (r+1)^2/r$ is the same inequality as

$$
\frac{\operatorname{Det}(H)}{\operatorname{Tr}(H)^2} = \frac{t}{(1 + t)^2} \gt \frac{r}{(r + 1)^2} = \frac{10}{121} = 0.0826
$$

which Lindeberg's article states in this better-conditioned form. <!-- L31 --> It is Part 9's Harris sign test with k = 0.0826, applied to the Hessian of the DoG instead of the structure tensor: it passes ratios above $t = 0.1$, where Harris with k = 0.04 passes ratios above 0.0436. Lowe borrowed the trace-and-determinant form from Harris and Stephens, <!-- L12 --> and a negative determinant, a saddle, is rejected outright. Figure 11 places the patch's two candidates on Part 9's curve.

![The curve t over (1 + t) squared against t, with horizontal lines at 0.04, 0.06 and SIFT's 0.0826, the square at t = 0.98 far above and the gap point at t = 0.047 below SIFT's line](FIG_11)

*Figure 11 — SIFT's edge test is a stricter Harris. The gap point (t = 0.047) fails SIFT's test though it would pass Harris at k = 0.04. Closed form, with the patch's two candidates.*

On real images the IPOL authors found this test has a negligible effect, because the refinement already discards many edge candidates. <!-- L49 --> On the patch it is the only thing that removes (17, 17).

## What is the scale for?

### Orientation

The search's output exists to set the size of what comes next. Each keypoint gets an orientation from a 36-bin histogram of gradient directions around it, weighted by gradient magnitude and by a Gaussian 1.5 times the keypoint's σ; every peak within 80% of the highest makes another keypoint at the same place and size. Lowe found about 15% of points get more than one. <!-- L13 --> OpenCV reads a radius of 4.5σ, smooths the histogram and interpolates each peak. <!-- L58 --> For the square, σ = 2.51: an 11-pixel radius and a weighting width of 3.8 pixels.

A square has four equal edges, but the step's gradients, in every row of the window, feed the 0° bin. In the replay with OpenCV's precise upscaling, the bins at 90° and 270° reach 0.826 of the highest and the 180° bin 0.665, so the square gets three keypoints, at 0°, 90.6° and 269.4°. With the default upscaling the same square is sampled a quarter pixel differently, one peak falls to 0.789, and it gets two. Figure 12 shows both histograms.

![Two 36-bin orientation histograms for the square's keypoint, one per upscaling mode, with the 80% line: three peaks clear it in one, two in the other](FIG_12)

*Figure 12 — The orientation count of a nearly symmetric blob is decided by sub-pixel sampling. Bins from the plain-Python replay of OpenCV's rules on the ×7 patch; not run.*

### The descriptor

The descriptor is a 4×4 grid of 8-bin orientation histograms, 128 numbers, Gaussian-weighted, normalised to unit length, clipped at 0.2 and renormalised. <!-- L14 --> OpenCV makes each cell 3σ wide. <!-- L59 --> For the square that is 7.5 pixels a cell and 30 pixels a side, nearly the whole 35-pixel image; for the ×14 square, 60 pixels over the same content. That is what searching σ buys: the window covers the same structure at any zoom, so the 128 numbers can match.

## The math

| Symbol | Meaning |
|---|---|
| $f$; $L(x, y; \sigma) = G_\sigma * f$ | image; its scale space |
| σ; $t = \sigma^2$ | Gaussian standard deviation; variance |
| $N = \sigma^2 \nabla^2 L$ | scale-normalised Laplacian |
| $k = 2^{1/s}$ | ratio between neighbouring levels, $s$ levels per octave |
| $D = L(k\sigma) - L(\sigma)$ | difference of Gaussians |
| $g$, $H$ | gradient and Hessian of $D$ at a sample |
| $t$ (in the edge test) | ratio of the smaller to the larger principal curvature |

**Scale space.** $L$ solves the diffusion equation, written in σ:

$$
\frac{\partial L}{\partial \sigma} = \sigma \nabla^2 L \tag{1}
$$

Increasing σ diffuses brightness, and the Laplacian sets the rate.

**Covariance.** If $f_s(x) = f(x/s)$ is the image enlarged by $s$,

$$
N_s(s x;\ s\sigma) = N(x;\ \sigma) \tag{2}
$$

so an extremum of $N$ at $(x, \sigma)$ reappears at $(sx, s\sigma)$ with the same value: the shift along log σ in Figure 5. <!-- L24 -->

**The square.** At the centre of a square of side $\ell$ and contrast $A$, with $u = \ell/(2\sigma)$,

$$
N = -4A\,u\,\varphi(u)\big(2\Phi(u) - 1\big), \qquad \text{extremal at } u^* = 1.2554,\ \ \sigma^* = 0.3983\,\ell \tag{3}
$$

For the ×7 square, $\ell = 7$ gives σ* = 2.788; with the step present the peak moves to 2.776.

<details>
<summary>Where equation (3) comes from</summary>

The blurred square at its centre is $A\,B(0)^2$ with $B(x) = \Phi\big((x + a)/\sigma\big) - \Phi\big((x - a)/\sigma\big)$, $a = \ell/2$, so $\nabla^2 L(0) = 2A\,B(0)\,B''(0)$. With $B(0) = 2\Phi(u) - 1$ and $B''(0) = -2a\,\varphi(u)/\sigma^3$, multiplying by σ² gives (3). Setting its derivative in $u$ to zero gives $u^* = 1.2554$; the equal-area disc, radius $\ell/\sqrt{\pi}$, peaks at radius over √2 (Part 2), which is $0.3989\,\ell$.

</details>

**DoG.** Integrating (1) over one interval,

$$
D(\sigma) = \int_{\ln\sigma}^{\ln\sigma + \ln k} N\, d(\ln\tau) \approx (\ln k)\, N \tag{4}
$$

and the approximations $(k - 1)N$ and $\tfrac12(k^2 - 1)N$ agree with $\ln k$ to first order in $k - 1$. <!-- L02 --> <!-- L30 -->

**Fit and tests.** With $g$ and $H$ from central differences,

$$
\hat{x} = -H^{-1} g, \qquad D(\hat{x}) = D + \tfrac12 g^{\top} \hat{x}, \qquad \frac{\operatorname{Tr}^2}{\operatorname{Det}} \lt \frac{(r+1)^2}{r} \tag{5}
$$

At the square these give the offsets (−0.019, 0, −0.055), the value −35.39 and the test value 4.0004 of the worked example. <!-- L10 --> <!-- L12 -->

## Implementation: the tooling map

Every entry maps to the arithmetic above. **None of it was executed for this post**; it comes from source at pinned commits and MathWorks' documentation. Figure 13 is the same map in one picture.

![Grid comparing OpenCV, scikit-image and MATLAB on doubling, scales per octave, base σ, contrast threshold, edge threshold, extremum test, border, keypoint size and position conventions](FIG_13)

*Figure 13 — One search, three libraries. The thresholds have different units and the size fields different meanings; check the row before carrying a number across.*

### OpenCV

| Want | Call | Note |
|---|---|---|
| keypoints | `cv2.SIFT_create().detect(img, None)` | 3 layers, σ 1.6, contrast 0.04 ÷ 3, edge 10 <!-- L53 --> |
| unbiased positions | `cv2.SIFT_create(enable_precise_upscale=True)` | 4.8.0 and later; off by default <!-- L63 --> <!-- L64 --> |
| keypoint fields | `kp.pt`, `kp.size`, `kp.angle`, `kp.response` | size = 2σ; response = abs D(x̂) on 0–1 <!-- L57 --> |

SIFT entered OpenCV's main module in 4.4.0, released in July 2020, after the patent on it expired in March 2020. <!-- L63 --> <!-- L62 --> Its 26-neighbour test is not Lowe's: it keeps a value equal to its largest neighbour (`>=`), so the ties along a perfectly straight edge pass and are left to the edge test. <!-- L56 --> <!-- L04 -->

The quarter pixel is Part 3's resize arithmetic, *Resampling and Aliasing: Interpolation Kernels in Practice*. Doubling by linear interpolation puts output pixel $j$ at input position $j/2 - 0.25$, and the next octave keeps the even pixels, so every keypoint is reported 0.25 pixel right and down. <!-- L61 --> An issue opened in January 2023 reports exactly that bias; a fix mapping $x$ to $2x$ was merged and switched off by default the same day, "temporarily", because `warpAffine` is not bit-exact and tests failed intermittently. <!-- L64 --> The issue is still open, and disabling the fix logs that it is deprecated. <!-- L71 --> Blurs pick `ksize = round(8σ + 1) | 1` for float images and use the reflect-101 border, <!-- L60 --> which puts mirrored copies of anything near the border just outside it.

### scikit-image and MATLAB

| Want | Call | Note |
|---|---|---|
| SIFT | `skimage.feature.SIFT()` then `.detect(img)` | IPOL parameters; DoG threshold 0.04/3 rescaled for other sampling <!-- L65 --> |
| Laplacian blobs | `skimage.feature.blob_log(img)` | σ² normalisation; radius ≈ √2 σ <!-- L67 --> |
| DoG blobs | `skimage.feature.blob_dog(img)` | divides by sigma_ratio − 1, default 1.6 <!-- L67 --> |
| MATLAB | `detectSIFTFeatures(I)` | 0.0133, 10, 3 layers, σ 1.6; ROI at least 63×63 <!-- L69 --> |

scikit-image's SIFT follows the IPOL description, but it upsamples with `rescale`, which calls SciPy's `zoom` with `grid_mode=True`, the full-pixel-extent mapping, and then reads positions as index times the sample spacing. <!-- L66 --> <!-- L68 --> IPOL's own interpolator has no such offset, <!-- L47 --> so by its code scikit-image should report the same quarter-pixel offset as OpenCV's default. It keeps only extrema more than one sample inside each octave's border, and it reports `sigmas`, the blur values themselves, and orientations in radians from `arctan2`, where OpenCV gives degrees. <!-- L72 --> MATLAB's `Scale` field is the detection scale itself, not a diameter, and its 63-pixel minimum region means the 35-pixel patch is too small to pass. <!-- L69 -->

### The worked example, in OpenCV

```python
import numpy as np
import cv2

patch = np.full((5, 5), 40, np.uint8)
patch[:, 3:] = 200
patch[2, 1] = 255
big = np.repeat(np.repeat(patch, 7, axis=0), 7, axis=1)       # 35 x 35, each pixel a 7 x 7 block

none = cv2.SIFT_create().detect(patch, None)                  # []: the 5-pixel margin is the whole image
kps = cv2.SIFT_create().detect(big, None)                     # pt (10.23, 17.25), size 5.02
fix = cv2.SIFT_create(enable_precise_upscale=True).detect(big, None)   # 3 at (9.98, 17.00), size 5.03
```

This was not run for this post. The comments state what the replay of OpenCV's rules predicts.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading a keypoint's size as the structure's width. OpenCV's `size` is twice the keypoint's σ: 5.02 for a square 7 pixels wide. The σ is the smaller Gaussian of a DoG pair, about 12% below the Laplacian's characteristic scale, and scikit-image's blob radius is √2 σ. MATLAB's `Scale` is σ itself. <!-- L57 --> <!-- L09 --> <!-- L67 --> <!-- L69 -->

- **Carrying a contrast threshold between libraries.** OpenCV's 0.04 means 0.0133 per DoG level; Lowe's 0.03 is OpenCV's 0.09. <!-- L53 -->
- **Trusting positions to a quarter pixel.** OpenCV's default reports every keypoint 0.25 pixel right and down; for anything metric, pass `enable_precise_upscale=True` (4.8.0 and later). <!-- L64 -->
- **Assuming blur never creates structure.** In 2-D, Gaussian scale space can create extremum–saddle pairs; only non-enhancement is guaranteed. <!-- L40 --> <!-- L29 -->
- **Taking three scales per octave as optimal.** It maximised repeatability in one study; a later one found 15 more stable. <!-- L06 --> <!-- L50 -->
- **Expecting covariance at every size.** It holds between the image's finest and coarsest scales. <!-- L26 --> The ×5 square peaks at the top level of the doubled-image octave, its fit 0.47 of a level from leaving it; in the replay, precise upscaling keeps it and the default loses it and keeps two points in the gap instead. Structures at an octave boundary or near the pixel scale are the fragile ones.
- **Counting orientations on symmetric structures.** A blob with several near-equal edges gets a different number of keypoints depending on sub-pixel sampling: two or three for the patch's square.
- **Small images.** OpenCV's 5-pixel margin and MATLAB's 63-pixel minimum leave nothing to detect on a tiny crop. <!-- L56 --> <!-- L69 -->
- **Box-filter detectors.** SURF's speed comes from giving up the Gaussian's guarantees; its authors document the scale-invariance risk. <!-- L52 -->
- **Taking the Laplacian as the last word.** Lindeberg reports substantially better matching with determinant-of-Hessian interest points than with Laplacian ones, and argues the same for SIFT's DoG points. <!-- L32 -->

## Key takeaways

- **Scale must be searched because size is relative.** A fixed σ reads every structure through the ratio of its size to σ: the σ that finds the ×7 square as one blob finds the ×14 square as four corners.
- **The normalisation is what makes the search covariant.** With σ² on the Laplacian, an extremum at (x, σ) moves to (sx, sσ) when the image is enlarged by s, at the same height; a square's characteristic scale is 0.398 times its side.
- **The Gaussian is "the only" kernel under non-enhancement or separability,** not under linearity, a semigroup and scale invariance alone; the Poisson kernel passes those. SIFT needs separability, the semigroup and the heat equation, which only the Gaussian provides together.
- **A DoG level is the normalised Laplacian averaged over one log-scale interval,** so it reports σ about √k below the Laplacian, 2.48 against 2.78 at the patch's square.
- **SIFT's edge test is Harris's ratio test with k = 0.0826 on the DoG's Hessian;** on the patch it alone rejects the point between the square and the step, at 23.2 against 12.1.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: the scale offset

From the five DoG values at (10, 17) in Figure 3, −21.855, −32.216, −35.379, −31.417 and −23.124, fit a parabola through levels 1 to 3 and find its vertex. Compare it with the 3-D fit's −0.0554.

**Self-check:** a level offset and the σ it gives.

<details><summary>Answer</summary>

The offset is $-\tfrac12 (D_3 - D_1)/(D_3 + D_1 - 2D_2) = -0.3995/7.125 = -0.0561$ level, so σ = $1.6 \times 2^{1.9439/3} = 2.507$. The 3-D fit gives −0.0554 because its $x$–level cross term, 0.2256, couples scale to the small leftward shift in $x$.

</details>

### E2 — Inspect: which level, which octave?

Using Figure 5 and the √k shift of Figure 10, find the σ at which the DoG of the ×5 square peaks, and say whether the octave of the worked example, levels 1 to 3 at σ 2.016 to 3.200, can find it.

**Self-check:** two values of σ and a yes or no.

<details><summary>Answer</summary>

The Laplacian peaks at 0.398 × 5 = 1.99, so the DoG peaks near 1.99/1.12 = 1.77, between level 0 (1.600) and level 1 (2.016). On the patch the ×5 DoG at the square's centre is −34.66 on level 0 and −34.31 on level 1: the extremum is on level 0, which has no level below it. Not in this octave. It belongs to the top of the octave built on the doubled image, whose searched levels are 1.008, 1.270 and 1.600 in input pixels.

</details>

### E3 — Predict: fourteen times

Before computing, predict the keypoint for the ×14 patch: its σ, its position and which level of which octave finds it. Then use equation (2).

**Self-check:** σ, (x, y), and an octave.

<details><summary>Answer</summary>

Twice everything: σ = 5.02 on level 2 of the octave one step coarser, at the image of (9.98, 17.00) under $x \to 2x + 0.5$, which is (20.46, 34.50). The replay of OpenCV's rules agrees to 0.004 pixel with precise upscaling, at size 10.03. That replay also returns the ×14 square's four corners at σ ≈ 2.2: at ×7 the same corners would sit near σ 1.1, close to the pixel, where nothing is found. With the default upscaling it does not return them.

</details>

### E4 — Diagnose: the quarter pixel

A colleague compares `cv2.SIFT_create().detect(big, None)` with the square's centre, (10, 17), and finds (10.23, 17.25). Name the cause, the fix, and the error that remains after it.

**Self-check:** a resize mapping, a flag, and a residual in pixels.

<details><summary>Answer</summary>

Doubling by `resize` maps output pixel $j$ to input $j/2 - 0.25$, and halving keeps the even pixels, so every point is reported +0.25 pixel in both axes. `enable_precise_upscale=True` maps $x$ to $2x$ and gives (9.98, 17.00). The remaining −0.02 pixel in $x$ is real: the step's blur pulls the DoG's minimum away from it.

</details>

### E5 — Extend: Harris–Laplace's verdicts

Run the scale half of simplified Harris–Laplace on two Harris maxima of the ×7 patch. At the corner point (8, 15), found at integration scale 1.96, the normalised Laplacian is −89.1 at 1.4, −83.2 at 1.96 and −86.9 at 2.744. At the centre (10, 17), found at 2.744 and again at 3.842, it is −115.2 at 1.96, −154.6 at 2.744, −127.5 at 3.842 and −69.1 at 5.378. Which detections survive, and at which scale?

**Self-check:** a verdict for each of the three detections, with the two neighbours it was compared with.

<details><summary>Answer</summary>

The corner at 1.96 is rejected: 83.2 is smaller in magnitude than both 89.1 and 86.9, a minimum over scale, and the other three corners match it by symmetry. The centre at 2.744 is kept: 154.6 beats 115.2 and 127.5. The centre at 3.842 is rejected: 127.5 lies between 154.6 and 69.1. One point survives, the square, with a characteristic scale of 2.744: Harris supplies the position, the Laplacian the scale.

</details>

## References

1. Lowe, D. G. "Distinctive Image Features from Scale-Invariant Keypoints." *International Journal of Computer Vision* 60(2):91–110, 2004. [doi:10.1023/B:VISI.0000029664.99615.94](https://doi.org/10.1023/B:VISI.0000029664.99615.94) · [PDF](https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf)
2. Lowe, D. G. "Object Recognition from Local Scale-Invariant Features." *Proceedings of ICCV 1999*, vol. 2, 1150–1157. [doi:10.1109/ICCV.1999.790410](https://doi.org/10.1109/ICCV.1999.790410) · [PDF](https://www.cs.ubc.ca/~lowe/papers/iccv99.pdf)
3. Brown, M., and Lowe, D. G. "Invariant Features from Interest Point Groups." *Proceedings of BMVC 2002*, 23.1–23.10. doi:10.5244/C.16.23. [PDF](https://www.bmva-archive.org.uk/bmvc/2002/papers/92/full_92.pdf)
4. Witkin, A. P. "Scale-Space Filtering." *Proceedings of IJCAI 1983*, 1019–1022. [PDF](https://www.ijcai.org/Proceedings/83-2/Papers/091.pdf)
5. Koenderink, J. J. "The Structure of Images." *Biological Cybernetics* 50(5):363–370, 1984. [doi:10.1007/BF00336961](https://doi.org/10.1007/BF00336961)
6. Babaud, J., Witkin, A. P., Baudin, M., and Duda, R. O. "Uniqueness of the Gaussian Kernel for Scale-Space Filtering." *IEEE TPAMI* 8(1):26–33, 1986. [doi:10.1109/TPAMI.1986.4767749](https://doi.org/10.1109/TPAMI.1986.4767749)
7. Yuille, A. L., and Poggio, T. A. "Scaling Theorems for Zero Crossings." *IEEE TPAMI* 8(1):15–25, 1986. [doi:10.1109/TPAMI.1986.4767748](https://doi.org/10.1109/TPAMI.1986.4767748)
8. Lindeberg, T. "Scale-Space for Discrete Signals." *IEEE TPAMI* 12(3):234–254, 1990. [doi:10.1109/34.49051](https://doi.org/10.1109/34.49051)
9. Lindeberg, T. "Feature Detection with Automatic Scale Selection." *International Journal of Computer Vision* 30(2):79–116, 1998. [doi:10.1023/A:1008045108935](https://doi.org/10.1023/A:1008045108935) · [Report](https://people.kth.se/~tony/papers/cvap198.pdf)
10. Lindeberg, T. "Edge Detection and Ridge Detection with Automatic Scale Selection." *International Journal of Computer Vision* 30(2):117–156, 1998. [doi:10.1023/A:1008097225773](https://doi.org/10.1023/A:1008097225773) · [Report](https://people.kth.se/~tony/papers/cvap191.pdf)
11. Lindeberg, T. "Invariance of Visual Operations at the Level of Receptive Fields." *PLoS ONE* 8(7):e66990, 2013. [doi:10.1371/journal.pone.0066990](https://doi.org/10.1371/journal.pone.0066990)
12. Lindeberg, T. "Scale Invariant Feature Transform." *Scholarpedia* 7(5):10491, 2012. [doi:10.4249/scholarpedia.10491](https://doi.org/10.4249/scholarpedia.10491)
13. Lindeberg, T. "Discrete Approximations of Gaussian Smoothing and Gaussian Derivatives." *Journal of Mathematical Imaging and Vision* 66(5):759–800, 2024. [doi:10.1007/s10851-024-01196-9](https://doi.org/10.1007/s10851-024-01196-9) · [arXiv:2311.11317](https://arxiv.org/abs/2311.11317)
14. Pauwels, E. J., Van Gool, L. J., Fiddelaers, P., and Moons, T. "An Extended Class of Scale-Invariant and Recursive Scale Space Filters." *IEEE TPAMI* 17(7):691–701, 1995. [doi:10.1109/34.391411](https://doi.org/10.1109/34.391411)
15. Felsberg, M., and Sommer, G. "The Monogenic Scale-Space: A Unifying Approach to Phase-Based Image Processing in Scale-Space." *Journal of Mathematical Imaging and Vision* 21(1–2):5–26, 2004. [doi:10.1023/B:JMIV.0000026554.79537.35](https://doi.org/10.1023/B:JMIV.0000026554.79537.35) · [Report version](https://macau.uni-kiel.de/servlets/MCRFileNodeServlet/macau_derivate_00002910/2002_tr08.pdf)
16. Didas, S., Burgeth, B., Imiya, A., and Weickert, J. "Regularity and Scale-Space Properties of Fractional High Order Linear Filtering." *Scale-Space 2005*, LNCS 3459, 13–25. [doi:10.1007/11408031_2](https://doi.org/10.1007/11408031_2)
17. Weickert, J., Ishikawa, S., and Imiya, A. "Linear Scale-Space has First been Proposed in Japan." *Journal of Mathematical Imaging and Vision* 10(3):237–252, 1999. [doi:10.1023/A:1008344623873](https://doi.org/10.1023/A:1008344623873)
18. Kannappan, Pl., and Sahoo, P. K. "Rotation Invariant Separable Functions are Gaussian." *SIAM Journal on Mathematical Analysis* 23(5):1342–1351, 1992. [doi:10.1137/0523076](https://doi.org/10.1137/0523076)
19. Kuijper, A. *The Deep Structure of Gaussian Scale Space Images.* PhD thesis, Utrecht University, 2002. [Record](https://dspace.library.uu.nl/handle/1874/872)
20. Mikolajczyk, K., and Schmid, C. "Indexing Based on Scale Invariant Interest Points." *Proceedings of ICCV 2001*, vol. 1, 525–531. [doi:10.1109/ICCV.2001.937561](https://doi.org/10.1109/ICCV.2001.937561)
21. Mikolajczyk, K., and Schmid, C. "Scale & Affine Invariant Interest Point Detectors." *International Journal of Computer Vision* 60(1):63–86, 2004. [doi:10.1023/B:VISI.0000027790.02288.f2](https://doi.org/10.1023/B:VISI.0000027790.02288.f2)
22. Rey-Otero, I., and Delbracio, M. "Anatomy of the SIFT Method." *Image Processing On Line* 4:370–396, 2014. [doi:10.5201/ipol.2014.82](https://doi.org/10.5201/ipol.2014.82)
23. Rey-Otero, I., Morel, J.-M., and Delbracio, M. "An Analysis of the Factors Affecting Keypoint Stability in Scale-Space." *Journal of Mathematical Imaging and Vision* 56(3):554–572, 2016. [doi:10.1007/s10851-016-0657-5](https://doi.org/10.1007/s10851-016-0657-5) · [arXiv:1511.08478](https://arxiv.org/abs/1511.08478)
24. Bay, H., Ess, A., Tuytelaars, T., and Van Gool, L. "Speeded-Up Robust Features (SURF)." *Computer Vision and Image Understanding* 110(3):346–359, 2008. [doi:10.1016/j.cviu.2007.09.014](https://doi.org/10.1016/j.cviu.2007.09.014)
25. OpenCV source, commit 802cf95: `sift.dispatch.cpp`, `sift.simd.hpp`, `features2d.hpp`, `smooth.dispatch.cpp`, `resize.cpp`. <https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760> (accessed 2026-10-13)
26. OpenCV releases 4.3.0, 4.4.0, 4.7.0, 4.8.0 and 4.10.0. <https://github.com/opencv/opencv/releases> (accessed 2026-10-13)
27. OpenCV issue 23123 and pull requests 23124 and 23270. <https://github.com/opencv/opencv/issues/23123>, <https://github.com/opencv/opencv/pull/23124>, <https://github.com/opencv/opencv/pull/23270> (accessed 2026-10-13)
28. scikit-image source, commit b700edc: `feature/sift.py`, `feature/blob.py`, `transform/_warps.py`. <https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2> (accessed 2026-10-13)
29. SciPy. "scipy.ndimage.zoom." SciPy v1.18.0 manual. <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.zoom.html> (accessed 2026-10-13)
30. MathWorks. "detectSIFTFeatures" and "SIFTPoints." Computer Vision Toolbox documentation, release R2026b. <https://www.mathworks.com/help/vision/ref/detectsiftfeatures.html>, <https://www.mathworks.com/help/vision/ref/siftpoints.html> (accessed 2026-10-13)
