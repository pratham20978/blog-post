---
title: "Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion"
slug: edge-preserving-smoothing
date: 2026-10-11
updated: 2026-10-11
summary: "The bilateral filter and Perona–Malik weigh neighbours by contrast, NL-means by repetition. On one 5×5 patch: which keeps the edge and drops the bright pixel?"
tags: [algorithms, image-processing, denoising, bilateral-filter, non-local-means, anisotropic-diffusion, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: advanced
series: image-processing
series_position: 7
prerequisites: ["the linear-filter sum and the shared 5×5 patch from part 1 of this series", "the heat-equation identity from part 2", "Gaussian kernels and their variance", "reading Python signatures"]
reading_minutes: 30
cover_image_url: "COVER"
cover_image_alt: "A 5×5 grid split by a vertical edge, with dots sized by bilateral weight: large on the dark side, tiny across the edge and on one tangerine cell"
canonical_url: "https://canery.in/blogs/edge-preserving-smoothing"
---

> [!NOTE]
> **Insights** — Edge-preserving smoothing averages a pixel only with neighbours that are like it, and the three classical methods differ in what "like" means: the bilateral filter compares values, non-local means compares whole neighbourhoods, and Perona–Malik diffusion lets value flow only across small differences. Worked by hand on the series' 5×5 patch, the two contrast-based methods cannot keep its edge from 40 to 200 and drop its one bright pixel of 255, because the bright pixel is the bigger jump: a bilateral filter with σ_r = 80 keeps more than 90% of both. Non-local means separates them by repetition, since the edge has copies down its column and the pixel has none, but only when a pixel's own patch cannot outvote its best matches. That is the reference algorithm's rule, and neither OpenCV's nor scikit-image's.

**Level:** advanced · **You need:** *Image Processing by Hand* (part 1 of this series) for the linear-filter sum and the shared patch, the heat-equation section of *The Laplacian by Hand* (part 2), Gaussian kernels and their variance, and enough Python to read a signature · **Time:** ~30 min

This is part 7 of *Image Processing by Hand*. Part 1 showed that no linear filter stops at an edge; this part makes the weights depend on the image in three ways, works each one on the shared patch, and prices them.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [The bilateral filter](#how-does-the-bilateral-filter-choose-its-weights) · [Non-local means](#non-local-means-similarity-by-repetition) · [Diffusion](#anisotropic-diffusion-the-heat-equation-with-a-conductance) · [Cost](#what-does-each-one-cost) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch and cross-checked with plain Python using only its `math` module; that check is not published. No OpenCV, scikit-image, ITK or MedPy call was executed: library behaviour comes from source read at a pinned commit, and one claim about scikit-image comes from replaying its index arithmetic, not from running it. There are no timings or measured curves. Curves are evaluated from the definitions, and the speeds quoted are the ones the papers measured.

## Why this matters

A camera with a few hot pixels makes a clean test. Run a bilateral filter over its frames and the grain goes while every hot pixel stays, nearly as bright as before; run a 3×3 median and the hot pixels go. The bilateral filter is not broken. To a filter that weighs neighbours by how similar their values are, a hot pixel is a very strong edge, and keeping strong edges is its job. Its own literature says so and prescribes a median first. <!-- L06 -->

OpenCV's non-local means at its default strength leaves an isolated hot pixel exactly as it is, for a different reason, <!-- L43 --> <!-- L44 --> and Perona–Malik diffusion removes one only if you stop it at the right iteration. Which of these you want depends on what each method means by a neighbour like me. This post computes all three on the series' patch, which happens to contain both an edge and a hot pixel.

## The problem

Part 1 averaged the impulse's 3×3 neighbourhood three ways: the box mean gave 64, the median 40 and the series' 3×3 Gaussian (σ = 0.8) 98.6. The same Gaussian applied to the clean row r0 turns its step from 40 | 200 into 78.2 | 161.8, taking 48% of the edge's contrast in one pass of the smallest blur in the series.

That is not a bad choice of weights. A linear, shift-invariant filter applies the same weights at every position, so the weights at c2 cannot know that c3 is on the other side of an edge. Any filter that stops at the edge must look at the values before it weighs them, and is therefore no longer linear.

So the requirements, stated on the patch, are three.

1. **Flat regions are averaged.** A pixel of 60 among 40s, a deviation small next to the edge, should come down as it would under the Gaussian.
2. **The step stays 40 | 200**, or close to it.
3. **The impulse is a decision.** A pixel of 255 among 40s is either *impulse noise* (salt-and-pepper: isolated pixels far from all their neighbours, from a hot sensor element or a bit error) or a real one-pixel feature. A filter should remove it in the first case and keep it in the second.

The name for requirements 1 and 2 together is **edge-preserving smoothing**, and there are three classical ways to meet them: the bilateral filter, non-local means and Perona–Malik diffusion. All three replace each pixel by a weighted average of other pixels; they differ only in which pixels count as alike. Requirement 3 is where they part company.

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

It has two features: a step of 160 between c2 and c3 in every row, and an impulse of 215 above its neighbours. Row r2 carries both. Borders mirror without repeating the edge pixel (reflect-101, OpenCV's default). <!-- L42 -->

### The bilateral filter: weight by value

The **bilateral filter** multiplies each spatial weight by a *range weight* that falls with the difference in value, and divides by the total so the weights sum to one. <!-- L01 --> With Gaussians for both, the spatial kernel has width σ_s and the range kernel width σ_r: values much closer than σ_r are mixed and values much farther apart are not. <!-- L02 --> Here the spatial kernel is the series' 3×3 Gaussian (centre 0.2725, edges 0.1248, corners 0.0571) and σ_r = 80 grey levels, so a neighbour that differs by Δ keeps $e^{-\Delta^2/(2\cdot 80^2)}$ of its spatial weight.

| Δ | 0 | 20 | 160 (the step) | 215 (the impulse) |
|---|---|---|---|---|
| range weight | 1 | 0.969 | $e^{-2}$ = 0.135 | 0.027 |

At the impulse all eight neighbours differ by 215, so they share 0.7275 of the spatial weight times 0.027:

$$
\frac{0.2725 \times 255 + 0.7275 \times 0.027 \times 40}{0.2725 + 0.7275 \times 0.027} = \frac{70.27}{0.2922} = 240.5
$$

On the clean row r0, pixel c2 sees columns c1 and c2 at 40 (spatial weight 0.761) and column c3 at 200 (0.239, times 0.135):

$$
\frac{0.761 \times 40 + 0.0323 \times 200}{0.761 + 0.0323} = 46.5
$$

By symmetry c3 becomes 193.5. The step keeps 147 of its 160, 92%, and the impulse still stands 200.5 above the 40s around it, 93% of its 215. Figure 1 lays out the weights.

![The bilateral weights at the impulse and at the step's dark side: spatial times range gives 2.7% for each of the impulse's neighbours and 13.5% across the step](FIG_01)

*Figure 1 — The bilateral filter's weights at two pixels, σ_r = 80. The impulse's neighbours keep 2.7% of their spatial weight; the step's far column keeps 13.5%. The impulse is the better-protected feature. Worked by hand.*

### Non-local means: weight by neighbourhood

**Non-local means** (NL-means) weighs every candidate pixel in a search window by how alike the *patches* around the two pixels are, rather than the two values. <!-- L16 --> With $d^2$ the mean squared difference between two patches and a strength h, the weight is $e^{-d^2/h^2}$. <!-- L17 --> Take 3×3 patches, let every pixel of the 5×5 patch be a candidate, and set h = 20.

The step pixel (r0, c2) has the patch `40 40 200` three times over. Its exact copy sits at (r4, c2): $d^2 = 0$, weight 1. Three more copies down the column differ in one pixel, the impulse, so $d^2 = 215^2/9 = 5{,}136$ and the weight is $e^{-12.8}$, about 0.000003. Every candidate that counts has 40 at its centre, so the step survives exactly.

The impulse has no copy. Its nearest patches are four flat patches of 40, at (r0, c0), (r0, c1), (r4, c0) and (r4, c1), which differ from it only at the centre: $d^2 = 5{,}136$ again, an RMS difference of 71.7. What decides its fate is the weight of its *own* patch, which always matches itself at distance 0. OpenCV and scikit-image give it weight 1, so four weights of 0.000003 cannot move it: the impulse stays 255. <!-- L44 --> <!-- L49 --> The reference algorithm on Image Processing On Line (IPOL) instead gives the pixel the largest of the other weights, to stop it outvoting everything else. <!-- L18 --> Then five equal votes remain, and the impulse becomes $(255 + 4 \times 40)/5 = 83.0$ while the step stays exact. Figure 2 shows both distance maps.

![Patch distances from the step pixel and from the impulse to every candidate: the step has an exact copy at distance 0, the impulse's nearest patches are at 5,136](FIG_02)

*Figure 2 — NL-means compares neighbourhoods, not values. The step's patch repeats down its column; the impulse's repeats nowhere, so its answer depends on how its own patch is weighted: 255 or 83.0. Worked by hand, h = 20.*

### Perona–Malik: three iterations

**Perona–Malik diffusion** runs the heat equation of Part 2 with a *conductance* on every face between neighbours that falls as the difference across that face grows. <!-- L24 --> Each iteration adds to every pixel λ times the sum, over its four neighbours, of conductance × difference; λ = 1/4 is the largest step that stays stable, and the image border passes nothing. <!-- L25 --> With the conductance $g(s) = 1/(1 + (s/K)^2)$ and K = 80: <!-- L27 -->

- a flat face carries no difference, so nothing flows;
- a step face conducts $g(160) = 1/5 = 0.2$, a flow of 160/5 = 32;
- an impulse face conducts $g(215) = 1/8.223 = 0.122$, a flow of 215/8.223 = 26.15.

In iteration 1 every step pixel on a clean row moves by ¼ × 32 = 8, to 48 | 192. The impulse loses ¼ × 4 × 26.15 = 26.15 and becomes 228.85; each of its four neighbours gains 6.54; (r2, c2) gains from both sides, to 40 + 6.54 + 8 = 54.54. The next two iterations work the same way on the new values:

| iteration | row r2 | row r0 |
|---|---|---|
| 0 | 40, 255, 40, 200, 200 | 40, 40, 40, 200, 200 |
| 1 | 46.54, 228.85, 54.54, 192, 200 | 40, 40, 48, 192, 200 |
| 2 | 50.65, 199.19, 67.57, 185.29, 198.02 | 40, 43.60, 54.51, 185.49, 198.02 |
| 3 | 55.33, 165.25, 80.90, 179.19, 194.91 | 41.71, 47.22, 61.54, 179.65, 194.96 |

![Perona–Malik on the patch at iterations 0 to 3, with the step's faces conducting 0.2 and the impulse's 0.122](FIG_03)

*Figure 3 — Three iterations of Perona–Malik, K = 80, λ = 1/4. Each impulse face conducts less than a step face, but the impulse has four faces and a step pixel one, so the impulse drains faster. Worked by hand.*

### The scorecard

| method | (r2, c1) impulse | (r2, c0) beside it | r0, c2 | r0, c3 |
|---|---|---|---|---|
| input | 255 | 40 | 40 | 200 |
| Gaussian, σ = 0.8 | 98.6 | 93.6 | 78.2 | 161.8 |
| median, 3×3 | 40 | 40 | 40 | 200 |
| bilateral, σ_r = 80 | 240.5 | 41.9 | 46.5 | 193.5 |
| NL-means, h = 20, own weight 1 | 255 | 40 | 40 | 200 |
| NL-means, h = 20, own weight = max | 83.0 | 40 | 40 | 200 |
| Perona–Malik, 3 iterations | 165.2 | 55.3 | 61.5 | 179.7 |

Two rows keep the step and lower the impulse: the median and NL-means under IPOL's rule. Neither of them weighs contrast.

## Intuition

All three methods answer one question for every pixel: which neighbours are like me? What each counts as alike decides what it keeps.

The bilateral filter compares one value with one value. The impulse differs from everything around it by 215, more than anything else in the patch, so it is the most protected feature. A range kernel is a contrast threshold, and a threshold cannot rank noise below an edge when the noise is the bigger jump. Perona–Malik also judges by contrast, one face at a time, but it keeps going: the impulse leaks through four faces while a step pixel leaks through one, so after enough iterations the impulse goes first. That is counting faces, not recognising noise.

NL-means compares neighbourhoods. The step's neighbourhood repeats down its column; the impulse's repeats nowhere. Repetition is a property of structure, which is why NL-means can separate the two, as the median does by rank.

Picture each pixel holding a vote on its own new value, in which it counts only the voters who already agree with it. The impulse agrees with no one and counts only itself. NL-means asks a different question, who lives in a neighbourhood like mine, and the impulse's honest answer is nobody; that is why the rule for counting its own vote decides the result. The analogy breaks for diffusion, which holds no vote at all: it moves value across faces until someone stops the clock. Figure 4 puts every method on two axes.

![Step contrast kept against impulse contrast left: the bilateral and Perona–Malik trace curves from no change to the Gaussian, while the median and NL-means under the max rule sit at the right edge](FIG_04)

*Figure 4 — The contrast-based methods trade the step against the impulse along one curve, whatever σ_r or iteration count is chosen; nothing on it keeps the step and drops the impulse. The median and IPOL's NL-means sit off the curve. Impulse contrast is measured against the mean of its four neighbours. Computed from the definitions.*

## How does the bilateral filter choose its weights?

The idea is older than its name: Aurich and Weule's non-linear Gaussian filters and Smith and Brady's SUSAN came first, Tomasi and Manduchi named it, and its two parameters set the size and the contrast of the features it keeps. <!-- L05 --> σ_s is how far the average reaches. σ_r is the contrast the filter treats as an edge: differences much smaller are averaged, much larger are kept. <!-- L02 --> Tomasi and Manduchi's own examples use σ_r = 50 grey levels; <!-- L03 --> for denoising, σ_s is usually small and σ_r is set to match the noise. <!-- L07 --> Figure 5 draws the range weight for four values of σ_r with the patch's differences marked.

![Range weight against intensity difference for σ_r of 20, 50, 80 and 160, with the differences 20, 160 and 215 marked](FIG_05)

*Figure 5 — The range kernel is a soft contrast threshold. Every curve passes the step's 160 before the impulse's 215, so no σ_r keeps the step and lets the impulse through. Evaluated from the definition.*

Requirement 1 holds. A pixel of 60 among 40s differs by 20, keeps a range weight of 0.969, and comes down to 45.6, against the Gaussian's 45.45. Requirement 3 cannot: there is no σ_r for which 160 is large and 215 small. The design is doing what it was built for. In Tomasi and Manduchi's photograph a cat's whiskers, thinner than the window, stay crisp because the range term ignores their bright pixels. <!-- L04 --> An impulse is a whisker one pixel long.

### What to do about impulses

The literature puts the fix outside the range kernel. One way is to mollify: compute the range weights on a median-filtered copy and average the original values with them. <!-- L06 --> On the patch the median copy is flat around the impulse, so every neighbour counts in full and the impulse falls to 98.6, the Gaussian's answer. That is better than 240.5 but not removal, because the 255 still votes. The other way is to change where the estimate starts. The bilateral filter is one step of a robust estimator, a statistic that discounts values far from its current guess, and that step begins at the pixel's own value; Durand and Dorsey recommend starting it from a median instead. <!-- L08 --> One step from 40 gives 42.2; steps from 255 run 240.5, 232.4, 226.3 and need about sixty to reach 42.3.

### Why it is slow, and how to make it fast

The weights change at every pixel, so the filter is not a convolution and a fast Fourier transform cannot apply it directly. A brute-force pass over a window cut at 2σ_s costs on the order of N·σ_s² for N pixels. <!-- L13 --> The way out is to lift the image. Put every pixel at a point (position, intensity), and the bilateral filter becomes an ordinary Gaussian blur of that lifted image, read back at each pixel's own intensity: the *bilateral grid*. <!-- L12 --> Figure 6 lifts row r2.

![Row r2 drawn in the position–intensity plane on a grid of cells σ_s wide and σ_r tall: the impulse sits 2.69 σ_r above its neighbours and the step 2.00 σ_r](FIG_06)

*Figure 6 — Lifted into position × intensity, the bilateral filter is a linear Gaussian blur. The impulse sits 2.69 σ_r above its neighbours and the step 2.00 σ_r apart, so the blur barely mixes either. The blurred grid is smooth, so it can be sampled at one cell per σ_s × σ_r.*

Because the blurred grid is smooth, it can be downsampled, which brings the cost to about N + N·R/(σ_s²σ_r), with R the intensity range. <!-- L13 --> Durand and Dorsey's earlier version computed about (max − min)/σ_r intensity layers, each a linear convolution done by FFT, and interpolated between them, then downsampled; they reported a speed-up of two orders of magnitude overall. On a 576×768 image with 17 layers, filtering at full resolution still took 173 s on their 2002 machine, before downsampling. <!-- L11 -->

The filter's own artefact is staircasing. Buades, Coll and Morel showed that neighbourhood filters, the bilateral among them, behave like an ill-posed variant of Perona–Malik and build flat plateaus separated by false boundaries. <!-- L14 -->

## Non-local means: similarity by repetition

Buades, Coll and Morel's idea is that the pixels most like a given pixel need not be near it, so the filter should search a large window for every pixel whose surroundings resemble its own. They introduced it with the *method noise*, the difference between an image and its denoised version, as a way to see what a denoiser takes away, and proved it asymptotically optimal under a generic image model. <!-- L20 --> They call the result semi-local rather than non-local, <!-- L16 --> and Milanfar points out that limiting the search is the only thing that separates it from local filters. <!-- L23 --> On noisy images the weight is $e^{-\max(d^2 - 2\sigma^2,\,0)/h^2}$. The $2\sigma^2$ is what two noisy copies of one patch differ by on average, so such pairs get weight 1. <!-- L17 --> Their published settings tie everything to the noise level: for σ up to 15, 3×3 patches, a 21×21 window and h = 0.4σ. <!-- L19 -->

### Who gets the pixel's own vote

A patch always matches itself at distance 0, so its weight is the kernel's largest value, and Salmon and Strozecki describe that weight as overestimated. <!-- L21 --> IPOL's algorithm caps it at the largest of the other weights; OpenCV and scikit-image leave it at 1. <!-- L18 --> <!-- L44 --> <!-- L49 --> On most pixels the difference is small, because a good match exists and its weight is close to 1 anyway. On a pixel with no good match it decides everything. Figure 7 follows the impulse and a step pixel as h grows.

![NL-means estimate at the impulse and at a step pixel against h, under own-patch weight 1 and under the max rule](FIG_07)

*Figure 7 — With its own weight at 1, the impulse falls only once h is large enough to blur the step as well; under the max rule it sits at 83 for every small h while the step stays exact. Computed from the definitions on the patch.*

To remove the impulse with weight 1, h has to grow until even mismatched patches count. At h = 80 the impulse falls to 110.7, but by then the step has slid to 82.0 | 170.4: the cure is a blur. Under the max rule the impulse sits at 83.0 for every h up to about 30 and the step does not move.

### Rare patches

Salmon and Strozecki call the general version the *rare patch effect*. In a flat region the number of similar patches grows with the square of the search radius; along an edge it grows only linearly, so NL-means averages fewer pixels there and leaves a halo of noise. <!-- L21 --> An impulse is the extreme case, with no similar patch at all, and real impulse noise needs a detector: Xiong and Yin add one, and a reference image, before running NL-means. <!-- L22 --> Garnett and colleagues did the same for the bilateral filter. <!-- L15 -->

### The price

A naive implementation compares every patch in the window: with OpenCV's defaults of 7×7 patches and a 21×21 window, that is 21² × 7² = 21,609 pixel differences per pixel. Summing the squared differences for one shift over the whole image into an integral image, a table of running sums from which any box sum costs four reads, removes the patch-size factor, leaving about 441 shifts per pixel; scikit-image documents its fast mode as costing image.size × patch_distance^ndim on that principle. <!-- L48 -->

## Anisotropic diffusion: the heat equation with a conductance

Start from the linear case. With every conductance at 1 and λ = 1/4, one iteration replaces each interior pixel by the mean of its four neighbours. The impulse becomes 40, but each neighbour rises to 93.75, and the step halves to 80 | 160 in a single step. That is the heat equation, Part 2's identity, and its result is a Gaussian blur. <!-- L30 -->

Perona and Malik's change is the conductance per face. The scheme conserves the total brightness, <!-- L30 --> and for λ ≤ 1/4 with conductances between 0 and 1 it obeys a maximum principle: each new value lies between the smallest and largest of its neighbourhood's previous values, so the image's range never grows. <!-- L26 -->

### Why edges survive

What crosses a face is the flux, conductance × difference, $s\,g(s)$. For the rational conductance it peaks at $s = K$ and falls beyond, as Figure 8 shows. Below K, larger differences flow faster, which is ordinary smoothing. Above K, larger differences flow *slower*, so in the continuous equation the steepest part of an edge runs backwards in time and sharpens. Perona and Malik observed that these regions shrink quickly and the process stays stable. <!-- L29 --> Their exponential conductance favours high-contrast edges, and the rational one favours wide regions over small ones. <!-- L27 -->

![Flux against difference for the rational and exponential conductances at K = 80, beside the linear flux of the heat equation, with 20, 160 and 215 marked](FIG_08)

*Figure 8 — The flux rises to K = 80 and falls beyond it. The patch's step (160) and impulse (215) both sit on the falling side, where a bigger jump leaks less. A 20-level bump sits on the rising side and is smoothed. Evaluated from the definitions.*

### Why it needs a stopping time

Diffusion has no end state but flat. The patch holds 2,815 grey levels in total, Part 5's DC term, so it converges to 112.6 everywhere. Figure 9 follows both features. After five iterations the impulse keeps 6% of its contrast and the step 58%; after ten, none and 25%; by a hundred the patch is a single grey. Perona and Malik describe edges that stay sharp until they disappear, <!-- L31 --> and Weickert shows that the standard discretisation converges to a constant. <!-- L35 --> The iteration count is a parameter.

![Contrast of the impulse and of the step over 100 iterations of Perona–Malik: the impulse falls first and both reach the mean 112.6](FIG_09)

*Figure 9 — Perona–Malik on the patch, K = 80. The impulse drains through four faces and goes first; the step follows. Both end at the patch mean, 112.6, so where you stop is the result. Iterated from the scheme's definition.*

### Choosing K

Perona and Malik set K by hand or at the 90% point of the histogram of gradient magnitudes. <!-- L28 --> Counting the differences the scheme itself uses, the patch has 40 faces: 31 carry no difference, 5 carry 160 and 4 carry 215. The 90% point is 160, so the rule puts K on the edge itself and gives it half the heat equation's conductance. Black, Sapiro, Marimont and Heeger estimate a robust scale instead, 1.4826 times the median absolute deviation of the gradient. <!-- L38 --> On the patch the median face difference is 0, so that scale is 0 and every non-zero difference counts as an edge. Both rules assume most differences are noise, and a noise-free patch has none.

### Ill-posed, and what that means here

The continuous Perona–Malik equation is ill-posed: it has no weak solutions even where computations succeed, yet simple discretisations are stable. <!-- L32 --> Catté, Lions, Morel and Coll fixed it by evaluating the conductance on the gradient of a Gaussian-smoothed copy, which gives existence and uniqueness. <!-- L33 --> What survives into practice is staircasing: a smooth edge breaks into piecewise-linear segments separated by jumps. <!-- L35 -->

One word of terminology. Weickert calls diffusion *anisotropic* only when a diffusion tensor makes the flow differ by direction; Perona–Malik's conductance is a single number per face, so in his terms it is non-linear isotropic diffusion. <!-- L34 --> It slows flow across an edge but does nothing special along it.

## What does each one cost?

Figure 10 and the table price the three against the median, counting work per pixel from each method's definition.

| method | parameters | work per pixel | keeps | fails on |
|---|---|---|---|---|
| bilateral | σ_s, σ_r, window | 13 taps at OpenCV's d = 5, 49 at d = 9 or scikit-image's default 7×7 | differences above σ_r, impulses included | impulse noise; staircasing |
| NL-means | h (and σ), patch, window | 21,609 differences naively at 7×7 in 21×21; about 441 shifts with integral images | whatever repeats | rare patches; impulses under weight 1 |
| Perona–Malik | K, λ, iterations, g | 4 differences per iteration, times the iterations | jumps above K, for a while | everything, given time; staircasing |
| median | window | sort 9 values | the step, and removes the impulse | a one-pixel line, 3 of the 9 values, outvoted like the impulse |

![Operations per pixel on a log scale for the median, the bilateral filter at three window sizes, NL-means naive and with integral images, and Perona–Malik at 10 and 100 iterations](FIG_10)

*Figure 10 — Work per pixel, counted from each definition rather than measured. Naive NL-means is two to three orders of magnitude dearer than a bilateral pass, and integral images bring it within about one; Perona–Malik's price is whatever iteration count the result needs.*

## The math

| Symbol | Meaning |
|---|---|
| $y_i$, $\hat{y}_i$ | input and output value at pixel i |
| $W_{ij}$ | weight of input j in output i |
| $G_\sigma$ | Gaussian of width σ |
| $d^2(P_i, P_j)$ | mean squared difference between the patches around i and j |
| $g$, $K$, $\lambda$ | conductance, its contrast parameter, the time step |
| $\rho$, $\psi$ | a robust error norm and its derivative |

**One form for all three.** Each output is a weighted sum of inputs whose weights are non-negative and sum to one: <!-- L40 -->

$$
\hat{y}_i = \sum_j W_{ij}\, y_j, \qquad \sum_j W_{ij} = 1 \tag{1}
$$

With W fixed this is Part 1's linear filter. Building W from y makes it non-linear, and the three methods are three recipes for W.

**Bilateral.**

$$
W_{ij} \propto G_{\sigma_s}(\lVert x_i - x_j \rVert)\; G_{\sigma_r}(y_i - y_j) \tag{2}
$$

At the impulse the product is 0.2725 for itself and 0.7275 × 0.027 for the eight 40s, which normalises to the 240.5 of the worked example.

**NL-means.**

$$
W_{ij} \propto e^{-\max(d^2(P_i, P_j) - 2\sigma^2,\,0)/h^2}, \qquad W_{ii} = \max_{j \ne i} W_{ij} \;\text{(IPOL) or } 1 \;\text{(libraries)} \tag{3}
$$

Patches that differ only by noise get weight 1, distant ones next to nothing, and the pixel's own patch gets either the best of the others or 1: the choice that sent the impulse to 83.0 or left it at 255.

**Perona–Malik**, one explicit step:

$$
y_i \leftarrow y_i + \lambda \sum_{j \in \mathcal{N}_4(i)} g(\lvert y_j - y_i \rvert)\,(y_j - y_i) \tag{4}
$$

This is equation (1) with $W_{ij} = \lambda g$ for each neighbour and $W_{ii} = 1 - \lambda \sum g$. Since $g \le 1$, λ ≤ 1/4 keeps $W_{ii} \ge 0$, which is the maximum principle. At the impulse $W_{ii} = 1 - 4 \times \tfrac14 \times 0.122 = 0.878$, and the update is $255 - 215/8.223 = 228.85$, iteration 1's value.

**The robust view.** Black and colleagues showed that equation (4) is gradient descent on $\sum \rho(y_j - y_i)$ with $g(x) = \rho'(x)/x$: the rational conductance is the Lorentzian error norm, $\rho(x) = \log\!\big(1 + \tfrac12 (x/\sigma)^2\big)$ with $K^2 = 2\sigma^2$, and Tukey's biweight, whose derivative, the pull a difference exerts, is exactly zero beyond a cut-off, leaves a piecewise-constant image whose jumps all exceed it unchanged. <!-- L37 --> You and colleagues traced Perona–Malik's ill-posedness to that energy having infinitely many global minima, dense in image space, <!-- L36 --> and Barash joined the bilateral filter to the diffusion equation through adaptive smoothing. <!-- L10 --> The bilateral filter is one step of the matching estimator, a single Jacobi iteration in Elad's derivation, <!-- L09 --> and Perona–Malik's exponential conductance has the same form as its Gaussian range weight. <!-- L39 --> One step from the pixel's own value explains the impulse. At σ_r = 50 the robust energy has a local minimum at 254.9 and the estimate stays there; at σ_r = 80 there is none, but one step moves 255 only to 240.5.

## Implementation: the tooling map

Every call below maps to arithmetic above. **None of it was executed for this post**; the mapping comes from source at pinned commits. Figure 11 is the same map in one picture.

![Grid of OpenCV, opencv_contrib, scikit-image, ITK and MedPy calls for the three methods with their window, default and trap](FIG_11)

*Figure 11 — The same three methods in five libraries: different windows, units, self-weights and stability limits. None of it was executed; every cell comes from source at a pinned commit.*

### OpenCV and opencv_contrib

| Want | Call | Note |
|---|---|---|
| bilateral | `cv2.bilateralFilter(img, d, sigmaColor, sigmaSpace)` | the window is a disc: d = 3 keeps 5 taps, d = 5 13, d = 9 49; d ≤ 0 sets the radius to round(1.5 × sigmaSpace); colour difference is the sum of absolute channel differences <!-- L42 --> |
| NL-means | `cv2.fastNlMeansDenoising(img, None, h, 7, 21)` | h = 3 by default, in grey levels; own patch weight 1; weights under 0.001 dropped <!-- L43 --> <!-- L44 --> |
| Perona–Malik | `cv2.ximgproc.anisotropicDiffusion(img, alpha, K, niters)` | 8-bit 3-channel only; exponential conductance only; 8 neighbours; K is a fraction of 3 × 255 <!-- L45 --> |

OpenCV's own guidance for the bilateral filter is that sigmas under 10 barely act and over 150 look cartoonish, that d = 5 suits real time and d = 9 offline work, and that it is very slow next to most filters. <!-- L41 --> Two consequences follow from the source. At OpenCV's NL-means defaults a lone pixel Δ above flat surroundings has $d^2 \approx \Delta^2/49$, and its matches keep a weight of at least 0.001 only while $\Delta^2/(49 \times 9) < \ln 1000$, that is for Δ below about 55: a brighter pixel is left exactly as it is. And opencv_contrib documents alpha as normally between 0 and 1, but with eight neighbours equation (4) keeps $W_{ii} \ge 0$ only for alpha ≤ 1/8. <!-- L45 -->

### scikit-image, ITK and MedPy

| Want | Call | Note |
|---|---|---|
| bilateral | `skimage.restoration.denoise_bilateral(img, sigma_color=..., sigma_spatial=...)` | integer images are rescaled to 0–1, so σ_r = 80 is sigma_color ≈ 0.31; default window 7×7; border padded with zeros <!-- L46 --> |
| NL-means | `skimage.restoration.denoise_nl_means(img, h=0.1, patch_size=7, patch_distance=11)` | h in 0–1 units, so 0.1 is 25.5 grey levels; own patch weight 1; with `sigma`, try h ≈ 0.8σ <!-- L48 --> <!-- L49 --> |
| Perona–Malik | ITK's `GradientAnisotropicDiffusionImageFilter` | exponential conductance scaled by the image's mean squared gradient; default time step 0.125 in 2-D, with a warning above it <!-- L50 --> |
| Perona–Malik | `medpy.filter.smoothing.anisotropic_diffusion(img, niter, kappa, gamma, option)` | kappa in grey levels (default 50), gamma ≤ 0.25; option 2 is this post's conductance, option 3 Tukey's biweight <!-- L51 --> |

One warning about scikit-image comes from reading its source at commit b700edc. `_compute_spatial_lut` builds its table on `np.arange(-win_size // 2, win_size // 2 + 1)`, which has win_size + 1 points for an odd window, while the loop reads it as if it had win_size; <!-- L47 --> replaying that index arithmetic puts the largest spatial weight two rows down and one column left of the centre for a 5×5 window, and two down and two left for the default 7×7. This was not run. Before relying on `denoise_bilateral`, filter an image of one bright pixel with a very large `sigma_color` and check that the peak stays where it was.

### The worked example, in OpenCV

```python
import numpy as np
import cv2

patch = np.full((5, 5), 40, np.uint8)
patch[:, 3:] = 200
patch[2, 1] = 255

bil = cv2.bilateralFilter(patch, 3, 80, 0.8)   # disc of 5 taps, not the 3x3 square used above
nlm = cv2.fastNlMeansDenoising(patch, None, h=20, templateWindowSize=3, searchWindowSize=5)
print(bil[2, 1], nlm[2, 1])                    # about 245, and 255: own patch weight 1
```

This was not run for this post. The 245 is equation (2) on the 5-tap disc, worked by hand; the 255 follows from equation (3) with the libraries' weight of 1.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** smoothing impulse noise with a contrast-based filter. Any σ_r or K that keeps an edge of 160 keeps an impulse of 215 harder; on the patch, σ_r = 80 keeps more than 90% of both. Put a median in front, or mollify the range weights with one. <!-- L06 -->

- **sigma_color in the wrong units.** scikit-image rescales integer images to 0–1, so `sigma_color=80` there treats every difference as small and the filter becomes a Gaussian blur. <!-- L46 -->
- **Expecting d = 3 to mean 3×3 in OpenCV.** It is a disc of five taps; the worked example's impulse comes out near 245 rather than 240.5. <!-- L42 -->
- **Carrying h between libraries.** OpenCV's default 3 is in grey levels; scikit-image's 0.1 is a tenth of the full range, 25.5 levels. <!-- L43 --> <!-- L48 -->
- **Running diffusion without a stopping rule.** It ends at the image mean, 112.6 on the patch. <!-- L35 -->
- **Taking opencv_contrib's alpha range at its word.** Eight neighbours need alpha ≤ 1/8 for the maximum principle. <!-- L45 -->
- **Expecting Perona–Malik to smooth along edges.** Its conductance is a scalar; smoothing along an edge needs a diffusion tensor. <!-- L34 -->
- **Iterating a bilateral filter for more denoising.** Repeated passes build plateaus. <!-- L14 -->

## Key takeaways

- **Edge-preserving smoothing is still one weighted sum per pixel;** the weights now come from the image, which is what makes it non-linear.
- **Contrast cannot tell noise from an edge when the noise is the bigger jump.** The bilateral filter keeps more than 90% of both the patch's step and its 255.
- **NL-means separates them by repetition,** since the step has copies and the impulse none, but only when a pixel's own patch cannot outvote its best matches: IPOL's rule, not OpenCV's or scikit-image's.
- **Perona–Malik is the heat equation with a brake on every face.** It conserves brightness, ends at the mean (112.6 here) and needs a stopping time.
- **Impulses need rank or detection:** a median, or an impulse detector, in front of any of the three.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: the bright side of the step

Compute the bilateral filter at (r2, c3) with the series' 3×3 Gaussian and σ_r = 80.

**Self-check:** 193.5, the same as on the clean row r0.

<details><summary>Answer</summary>

The window covers c2 to c4 on rows r1 to r3. Column c2 holds 40s, which differ by 160 and keep 0.135 of their spatial weight 0.239; columns c3 and c4 hold 200s with weight 0.761. $(0.761 \times 200 + 0.0323 \times 40)/(0.761 + 0.0323) = 193.5$. The impulse at c1 is outside the window, so row r2 matches row r0 here.

</details>

### E2 — Inspect: when does the impulse fall below the step?

From Figure 9, after which iteration is the impulse's contrast first smaller than the step's?

**Self-check:** an iteration number and the two contrasts there.

<details><summary>Answer</summary>

After the third. At iteration 2 the impulse still stands 144.1 above its neighbours' mean and the step is 131.0; at iteration 3 they are 102.5 and 118.1.

</details>

### E3 — Predict: an impulse exactly σ_r high

Replace the 255 by 120, so the impulse is 80 above its neighbours, exactly σ_r. Before computing, predict whether the bilateral filter (σ_r = 80) now keeps more or less of the impulse than of the step, then compute the impulse's new value.

**Self-check:** a value near 70, about 38% of the impulse kept, against 92% for the step. A right number without the reason does not count.

<details><summary>Answer</summary>

Its neighbours now keep $e^{-1/2} = 0.607$ of their weight instead of 0.027, so the impulse is averaged nearly as the Gaussian would: $(0.2725 \times 120 + 0.7275 \times 0.607 \times 40)/(0.2725 + 0.7275 \times 0.607) = 70.5$. It keeps 30.5 of its 80, 38%, while the step still keeps 92%. σ_r is the line between averaged and kept; an impulse of 215 is on the far side of it, and one of 80 is not.

</details>

### E4 — Diagnose: a check that does not match

A colleague checks the worked example with `cv2.bilateralFilter(patch, 3, 80, 0.8)` and reads about 245 at the impulse instead of 240.5. Find the cause, predict one other pixel on row r0 that will also disagree and by how much, and say how to get 240.5.

**Self-check:** the cause named; the second pixel's value predicted from it; the fix.

<details><summary>Answer</summary>

OpenCV's window is a disc, and d = 3 means radius 1: the four corners are dropped. At the impulse the centre now carries weight 1 against four edge neighbours of $e^{-1/1.28} = 0.458$ each, times 0.027: $(255 + 4 \times 0.458 \times 0.027 \times 40)/(1 + 4 \times 0.458 \times 0.027) = 244.9$. Pixel (r0, c2) also changes. Its two corner neighbours across the step are gone, leaving one 200 at weight 0.458 × 0.135, so it becomes 44.1 rather than 46.5. OpenCV has no square 3×3 bilateral; compute equation (2) directly, or accept the disc and its numbers.

</details>

## References

1. Tomasi, C., and Manduchi, R. "Bilateral Filtering for Gray and Color Images." *Proceedings of ICCV 1998*, 839–846. doi:10.1109/ICCV.1998.710815. [PDF](https://users.soe.ucsc.edu/~manduchi/Papers/ICCV98.pdf)
2. Perona, P., and Malik, J. "Scale-Space and Edge Detection Using Anisotropic Diffusion." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 12(7):629–639, 1990. doi:10.1109/34.56205. [PDF](https://people.eecs.berkeley.edu/~malik/papers/MP-aniso.pdf)
3. Buades, A., Coll, B., and Morel, J.-M. "A Non-Local Algorithm for Image Denoising." *Proceedings of CVPR 2005*, 2:60–65. [doi:10.1109/CVPR.2005.38](https://doi.org/10.1109/CVPR.2005.38)
4. Buades, A., Coll, B., and Morel, J.-M. "A Review of Image Denoising Algorithms, with a New One." *Multiscale Modeling and Simulation* 4(2):490–530, 2005. [doi:10.1137/040616024](https://doi.org/10.1137/040616024)
5. Buades, A., Coll, B., and Morel, J.-M. "Non-Local Means Denoising." *Image Processing On Line* 1:208–212, 2011. doi:10.5201/ipol.2011.bcm_nlm. [PDF](https://www.ipol.im/pub/art/2011/bcm_nlm/article.pdf)
6. Durand, F., and Dorsey, J. "Fast Bilateral Filtering for the Display of High-Dynamic-Range Images." *ACM Transactions on Graphics* 21(3):257–266, 2002. doi:10.1145/566654.566574. [PDF](https://people.csail.mit.edu/fredo/PUBLI/Siggraph2002/DurandBilateral.pdf)
7. Paris, S., Kornprobst, P., Tumblin, J., and Durand, F. "Bilateral Filtering: Theory and Applications." *Foundations and Trends in Computer Graphics and Vision* 4(1):1–73, 2009. doi:10.1561/0600000020. [PDF](https://people.csail.mit.edu/sparis/publi/2009/fntcgv/Paris_09_Bilateral_filtering.pdf)
8. Milanfar, P. "A Tour of Modern Image Filtering." *IEEE Signal Processing Magazine* 30(1):106–128, 2013. doi:10.1109/MSP.2011.2179329. [PDF](https://users.soe.ucsc.edu/~milanfar/publications/journal/ModernTour.pdf)
9. Black, M. J., Sapiro, G., Marimont, D. H., and Heeger, D. "Robust Anisotropic Diffusion." *IEEE Transactions on Image Processing* 7(3):421–432, 1998. doi:10.1109/83.661192. [PDF](https://www.cns.nyu.edu/heegerlab/content/software/robanistdif/Black-IEEE-IP98.pdf)
10. Weickert, J. *Anisotropic Diffusion in Image Processing.* B. G. Teubner, Stuttgart, 1998. ISBN 3-519-02606-6. [PDF](https://www.mia.uni-saarland.de/weickert/Papers/book.pdf)
11. Catté, F., Lions, P.-L., Morel, J.-M., and Coll, T. "Image Selective Smoothing and Edge Detection by Nonlinear Diffusion." *SIAM Journal on Numerical Analysis* 29(1):182–193, 1992. [doi:10.1137/0729012](https://doi.org/10.1137/0729012)
12. Kichenassamy, S. "The Perona–Malik Paradox." *SIAM Journal on Applied Mathematics* 57(5):1328–1342, 1997. [doi:10.1137/S003613999529558X](https://doi.org/10.1137/S003613999529558X)
13. You, Y.-L., Xu, W., Tannenbaum, A., and Kaveh, M. "Behavioral Analysis of Anisotropic Diffusion in Image Processing." *IEEE Transactions on Image Processing* 5(11):1539–1553, 1996. [doi:10.1109/83.541424](https://doi.org/10.1109/83.541424)
14. Barash, D. "Fundamental Relationship Between Bilateral Filtering, Adaptive Smoothing, and the Nonlinear Diffusion Equation." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 24(6):844–847, 2002. [doi:10.1109/TPAMI.2002.1008390](https://doi.org/10.1109/TPAMI.2002.1008390)
15. Elad, M. "On the Origin of the Bilateral Filter and Ways to Improve It." *IEEE Transactions on Image Processing* 11(10):1141–1151, 2002. doi:10.1109/TIP.2002.801126. [PDF](https://elad.cs.technion.ac.il/wp-content/uploads/2018/02/08_Bilateral_Filter_IP.pdf)
16. Garnett, R., Huegerich, T., Chui, C., and He, W. "A Universal Noise Removal Algorithm with an Impulse Detector." *IEEE Transactions on Image Processing* 14(11):1747–1754, 2005. [doi:10.1109/TIP.2005.857261](https://doi.org/10.1109/TIP.2005.857261)
17. Buades, A., Coll, B., and Morel, J.-M. "The Staircasing Effect in Neighborhood Filters and Its Solution." *IEEE Transactions on Image Processing* 15(6):1499–1505, 2006. [doi:10.1109/TIP.2006.871137](https://doi.org/10.1109/TIP.2006.871137)
18. Salmon, J., and Strozecki, Y. "Patch Reprojections for Non-Local Methods." *Signal Processing* 92(2):477–489, 2012. doi:10.1016/j.sigpro.2011.08.011. [PDF](https://josephsalmon.eu/papers/NLM_Reprojections_Salmon_Strozecki.pdf)
19. Xiong, B., and Yin, Z. "A Universal Denoising Framework With a New Impulse Detector and Nonlocal Means." *IEEE Transactions on Image Processing* 21(4):1663–1675, 2012. [doi:10.1109/TIP.2011.2172804](https://doi.org/10.1109/TIP.2011.2172804)
20. OpenCV source, commit 802cf95: `bilateralFilter` (`imgproc.hpp`, `bilateral_filter.dispatch.cpp`, `bilateral_filter.simd.hpp`) and `fastNlMeansDenoising` (`photo.hpp`, `fast_nlmeans_denoising_invoker.hpp`). <https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760> (accessed 2026-10-11)
21. opencv_contrib source, commit 6484ab2: `ximgproc.hpp` and `anisodiff.cpp`. <https://github.com/opencv/opencv_contrib/tree/6484ab27bd332762f36262bf3b3f743720f4ca1b/modules/ximgproc> (accessed 2026-10-11)
22. scikit-image source, commit b700edc: `denoise_bilateral` and `denoise_nl_means` (`_denoise.py`, `_denoise_cy.pyx`, `non_local_means.py`, `_nl_means_denoising.pyx`). <https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/restoration> (accessed 2026-10-11)
23. ITK source, commit dfef081: `itkAnisotropicDiffusionImageFilter` and `itkGradientNDAnisotropicDiffusionFunction`. <https://github.com/InsightSoftwareConsortium/ITK/tree/dfef081654167268e754645b95f70d87c73b66fc/Modules/Filtering/AnisotropicSmoothing/include> (accessed 2026-10-11)
24. MedPy source, commit d6abf41: `medpy.filter.smoothing.anisotropic_diffusion`. <https://github.com/loli/medpy/blob/d6abf41066cce75c84215a237a0be208e8294760/medpy/filter/smoothing.py> (accessed 2026-10-11)
