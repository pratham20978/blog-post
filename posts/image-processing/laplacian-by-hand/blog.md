---
title: "The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening"
slug: laplacian-by-hand
date: 2026-09-14
updated: 2026-11-20
summary: "The Laplacian is what Gaussian blur removes per unit of scale. One identity explains sharpening, zero-crossing edges, blob scale selection and the pyramid."
tags: [algorithms, image-processing, laplacian, edge-detection, scale-space, opencv, convolution]
category: algorithms
categories: [algorithms]
tier: L4
difficulty: advanced
series: image-processing
series_position: 2
prerequisites: ["the four stages from Image Processing by Hand", "second derivatives and a Taylor expansion", "complex exponentials", "reading Python signatures"]
reading_minutes: 58
cover_image_url: "https://minio.canery.in/media/cover-laplacian-by-hand.png"
cover_image_alt: "The Laplacian stencil at the centre with five arrows out to sharpening, zero-crossing edges, blob scale selection, the pyramid and Poisson editing"
canonical_url: "https://canery.in/blogs/laplacian-by-hand"
---

> [!NOTE]
> **Insights** — The Laplacian is the quantity Gaussian blur removes, per unit of scale: blur an image slightly and the difference from the original *is* the Laplacian, exactly on smooth data. Every use of the operator follows from that one identity. Sharpening adds the Laplacian back, zero-crossing edge detection locates where it is zero, blob detection scales it by σ² and searches for the σ that makes it extremal, the Laplacian pyramid stores it once per octave, and Poisson editing keeps it and discards the pixels. All of it is worked here by hand on one 5×5 patch, then mapped onto what `cv2.Laplacian`, `scipy.ndimage` and `skimage.feature.blob_log` actually compute — including why `ksize=3` returns four times the value `ksize=1` does.

**Level:** advanced · **You need:** the four stages from [Image Processing by Hand](https://canery.in/blogs/image-processing-by-hand), second derivatives and one Taylor expansion, complex exponentials for a single transfer function, and enough Python to read a signature · **Time:** ~58 min

This is the first child of *Image Processing by Hand*. It reuses that post's 5×5 patch, its 3×3 Gaussian and its border rules, and it does not re-teach sampling, separability or correlation-versus-convolution. Where one of those matters here, it is named and linked.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Which discrete Laplacian?](#which-discrete-laplacian) · [Sharpening](#sharpening-the-thing-blur-removes) · [Zero-crossings](#zero-crossings-why-the-laplacian-finds-edges-twice) · [Scale selection](#scale-selection-the-laplacian-as-a-ruler) · [The pyramid](#the-pyramid-the-same-operator-resampled) · [Keeping the Laplacian](#keeping-the-laplacian-instead-of-the-pixels) · [The math](#the-math) · [Implementation](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on integers you can check on paper; the arithmetic was cross-checked with plain Python and nothing else — no NumPy, OpenCV, SciPy or scikit-image call was executed. There are no timings, no benchmarks, and no measured curves. The figures that draw curves are plotted from closed-form expressions, and each caption says so; the off-centre responses in the 26-neighbour test are the same closed form integrated numerically.

## Why this matters

You have a working edge map from `cv2.Laplacian(img, cv2.CV_64F, ksize=1)` and a threshold tuned against it. You change `ksize` to 3, expecting a slightly smoother version of the same thing. Three things happen at once, and the patch this post works on shows all three:

| Pixel | `ksize=1` | `ksize=3` | What changed |
|---|---|---|---|
| The hot pixel itself | −860 | −1,720 | twice as loud, not four times — the ×4 holds only on smooth data |
| Beside it, on the edge | 375 | 640 | the smear is gone: 640 is exactly 4 × the clean 160 |
| Diagonal to it | 160 | 1,070 | a new smear: the clean value would be 640 |

Every value in the output is about four times larger, so yesterday's threshold now passes almost everything. The smear the hot pixel made on the pixels beside it has gone. And a new smear has appeared on the four pixels diagonal to it.

None of that is a bug in your code. OpenCV's `ksize=3` is not a smoothed version of `ksize=1`; it is a different discrete Laplacian — one that weights only the diagonal neighbours — at four times the scale. <!-- L59 --> <!-- L61 -->

That is the shape of nearly every surprise this operator produces. "The Laplacian" names a family of stencils that agree on smooth data and disagree on exactly the pixels you care about: edges, impulses, corners. Libraries pick different members of the family, apply different scale factors, and drop the sign at different points, and the documentation states each of these facts on a different page.

The way out is not to memorise the pages. It is to know what the operator measures — how far a pixel sits from what its neighbours predict — and then the ×4, the moved impulse, the halo in sharpening, the phantom edge in a zero-crossing map and the missing σ² in a scale search each become a one-line consequence you can derive at the keyboard.

## The problem

Your code holds an array of integers, $I[r, c]$. You want its second derivative. The array does not have one.

The parent post made the point for first derivatives, and it is sharper here: a sampled signal has no derivative of any order, because between the samples there is nothing to differentiate. What you can compute is a *difference*. A difference estimates the derivative of the continuous signal the samples were taken from only to the extent that the signal was smooth at the sampling scale. For a second derivative the estimate is worse than for a first, because differencing twice amplifies whatever roughness is present twice.

So there are two decisions hiding in the phrase "take the Laplacian", and every library makes both for you.

**Which continuous operator.** The Laplacian is the sum of the two second partial derivatives, $\nabla^2 f = f_{xx} + f_{yy}$. Marr and Hildreth chose it for edge detection because it is the only linear second-order differential operator that does not depend on orientation: rotate the image and the Laplacian rotates with it, unchanged. <!-- L01 --> A second derivative *across* an edge would be more selective, but it needs the edge direction first, and a rotation-invariant operator does not.

**How to estimate it from samples.** Torre and Poggio showed that numerical differentiation of an image is ill-posed in Hadamard's sense — a small change in the input can produce an arbitrarily large change in the output — and that the only cure is to regularise by filtering before differentiating. <!-- L35 --> Every discrete Laplacian you will ever compute is therefore really $\nabla^2 (G_\sigma * f)$ for some smoothing $G_\sigma$. The bare 3×3 stencil is simply the case where the only smoothing is the sampling grid itself.

Figure 1 shows the shape of the answer on the parent patch's middle row, before any of that is decided.

![The patch's middle row 40, 40, 40, 200, 200 as a step; below it the first difference with one peak of 160 on the step; below that the second difference, +160 then −160, crossing zero at column 2.5.](https://minio.canery.in/media/fig-01-two-signatures-laplacian-by-hand.png)

*Figure 1 — The edge is a peak in the first difference and a zero-crossing in the second — the same place, two signatures. The second difference also has twice the peak-to-peak swing, which is the noise story in miniature.*

Read the middle row of the patch as a 1-D profile, $f = [40, 40, 40, 200, 200]$, and take its two differences:

$$
\Delta f[c] = f[c+1] - f[c], \qquad \Delta^2 f[c] = f[c-1] - 2f[c] + f[c+1] .
$$

The first is the slope between a sample and the next; the second is the change in that slope, centred on the sample.

| Column | c0 | c1 | c2 | c3 | c4 |
|---|---|---|---|---|---|
| $f$ | 40 | 40 | 40 | 200 | 200 |
| first difference, written under $c$ | 0 | 0 | 160 | 0 | · |
| second difference | · | 0 | +160 | −160 | · |

The edge appears once in the first difference, as a peak. It appears twice in the second, as a positive lobe on the dark side and a negative lobe on the bright side, and the quantity is zero *between* them, which is where the step is. That is what "finding edges twice" means. It is also why the second derivative can locate an edge to within a pixel without any threshold: you look for the sign change, not for a large value.

The cost is in the same row. The stencil weights sum to zero, so a flat region returns exactly 0 and the output has no DC term. But the centre weight is −2 in one dimension and −4 in two, so a single sample that differs from its neighbours by $\delta$ returns $-4\delta$.

The problem statement is therefore three choices, and each is one section below:

1. **Choose a stencil.** It decides the scale factor and the anisotropy.
2. **Choose a σ.** It decides which structures survive and how much noise is amplified.
3. **Choose what to do with the output.** Locate its zero, search for its extremum over σ, or keep its value.

## Worked example

One patch carries this post, the same one that carried the parent: 5 rows by 5 columns, 8-bit grayscale, dark on the left, bright on the right, a step between column 2 and column 3, and a single bad pixel of value 255 at row 2, column 1.

|       | c0 | c1  | c2 | c3  | c4  |
|-------|----|-----|----|-----|-----|
| **r0** | 40 | 40  | 40 | 200 | 200 |
| **r1** | 40 | 40  | 40 | 200 | 200 |
| **r2** | 40 | **255** | 40 | 200 | 200 |
| **r3** | 40 | 40  | 40 | 200 | 200 |
| **r4** | 40 | 40  | 40 | 200 | 200 |

The operator is the four-neighbour stencil, which is what OpenCV applies for `ksize=1` and what `scipy.ndimage.laplace` applies always: <!-- L54 --> <!-- L62 -->

```
 0   1   0
 1  -4   1
 0   1   0
```

Lay it over a pixel, multiply each neighbour by its weight, add. There are only five products, and one of them is the centre times −4.

### The clean patch: the step

Start with the impulse removed, so that (2,1) holds 40 like everything else on the left. Figure 2 shows the two windows that matter.

![Two 3 by 3 windows from the clean patch: at (2,2) the four neighbours sum to 320 and 320 − 4 × 40 = +160; at (2,3) they sum to 640 and 640 − 4 × 200 = −160. The zero-crossing lies between them.](https://minio.canery.in/media/fig-02-clean-windows-laplacian-by-hand.png)

*Figure 2 — The zero-crossing lies between column 2 and column 3, which is exactly where the step is. Neither window needed a threshold to say so.*

| Pixel | Up | Down | Left | Right | Neighbour sum | 4 × centre | Laplacian |
|---|---|---|---|---|---|---|---|
| (2,2), dark side | 40 | 40 | 40 | 200 | 320 | 160 | **+160** |
| (2,3), bright side | 200 | 200 | 40 | 200 | 640 | 800 | **−160** |
| (2,1), flat | 40 | 40 | 40 | 40 | 160 | 160 | **0** |

Two things to read off. The sign is positive on the dark side of the step and negative on the bright side. That will be the sign convention throughout, and it is why sharpening *subtracts* the Laplacian.

And the values are symmetric, so a straight line between them crosses zero midway:

$$
c_0 = 2 + \frac{160}{160 + 160} = 2.5 ,
$$

the boundary between the two pixels, which is the sub-pixel position of the step. No first-derivative operator locates the edge that cheaply; the parent's Sobel put a peak of 640 on column 3 and left the sub-pixel question open.

### The impulse: what one pixel does

Now restore the 255 at (2,1). Figure 3 repeats the arithmetic.

![Three 3 by 3 windows from the patch with the impulse: at (2,1) the centre 255 gives 160 − 1020 = −860; at (2,2) the left neighbour 255 gives 535 − 160 = 375; at (1,2) the impulse sits diagonally, outside the stencil, and the result stays 160.](https://minio.canery.in/media/fig-03-impulse-windows-laplacian-by-hand.png)

*Figure 3 — One pixel three columns from nothing in particular changes the edge response at (2,2) by 134% and produces the largest magnitude in the whole patch at its own location. The window at (1,2) does not see it at all, because the four-neighbour stencil has no diagonal weights.*

| Pixel | Neighbours | Sum | 4 × centre | Laplacian | Clean value |
|---|---|---|---|---|---|
| (2,1), the impulse | 40, 40, 40, 40 | 160 | 1,020 | **−860** | 0 |
| (2,2), the edge | 40, 40, 255, 200 | 535 | 160 | **375** | 160 |
| (1,2), above the edge | 40, 40, 40, 200 | 320 | 160 | **160** | 160 |

At the impulse itself the Laplacian is −860, 5.4 times the magnitude of the genuine edge response. A hot pixel is, to this operator, the most edge-like thing in the image.

At the edge pixel (2,2) the left neighbour is now 255, and the response is 375 instead of 160. That is a 134% error in the edge response, caused by a pixel that is not adjacent to the step. The parent post found a 67% error in the Sobel response from the same pixel. The Laplacian doubles it, because Sobel's [1 2 1] smoothing along the edge averages the damage over three rows and the four-neighbour stencil averages over nothing.

At (1,2), directly above the edge pixel, the impulse sits diagonally. The stencil has a 0 there, and the response is still 160. Keep that in mind for the `ksize=3` story: a stencil with diagonal weights sees the impulse from (1,2) and not from (2,2), which is the smear that moved in the opening section.

### Does the zero-crossing survive?

With the impulse present, row 2 of the Laplacian reads $[\,\cdot\,, -860, 375, -160, \,\cdot\,]$. The genuine crossing between columns 2 and 3 is still there, but linear interpolation now puts it a fifth of a pixel toward the bright side. And a second crossing has appeared between −860 and 375:

$$
c_0 = 2 + \frac{375}{375 + 160} = 2.70, \qquad c_1 = 1 + \frac{860}{860 + 375} = 1.70 .
$$

The clean patch has one edge in this row; the patch with one bad pixel has two. That second crossing is the whole argument for smoothing first, and it is the subject of the zero-crossing section.

### Smooth first, then difference

The parent post's 3×3 Gaussian has weights 0.0571 at the corners, 0.1248 at the edges and 0.2725 at the centre, sampled at nominal σ = 0.8. Smooth the patch with it, then apply the four-neighbour stencil at (2,2). Because both operations are linear, the same answer comes from applying the combined 5×5 kernel once, and that combined kernel is shown as numbers in the zero-crossing section. The results:

| At (2,2) | Raw Laplacian | After the 3×3 Gaussian |
|---|---|---|
| Clean patch | 160 | 45.3 |
| With the impulse | 375 | 21.1 |
| Error from the impulse | +215 (134%) | −24.2 (53%) |

Smoothing at σ = 0.8 cut the absolute damage nine times over. It did not cut the relative error below half, because σ = 0.8 is a smoothing radius smaller than a pixel and the impulse is a pixel wide: the Gaussian spread the bad value over its neighbours rather than removing it.

It also shrank the genuine edge response from 160 to 45, because the second derivative of a smoothed step is lower and wider than the second derivative of a sharp one. Every design decision in the rest of this post is a version of that trade.

## Intuition

The four-neighbour stencil has a reading in plain words, and it is worth stating before the symbol appears, because it explains all four behaviours seen so far — the sign, the zero on a flat region, the −860, and why smoothing helps.

### Neighbour average minus centre

Rewrite the stencil. Call $f_C$ the centre, $f_U, f_D, f_L, f_R$ its four neighbours and $m$ their mean; then

$$
\nabla^2_5 f = f_U + f_D + f_L + f_R - 4 f_C = 4\,(m - f_C) ,
$$

so that

$$
f_C - m = -\frac{\nabla^2_5 f}{4} .
$$

The stencil is four times the gap between the neighbours' mean and the centre. Figure 4 shows the two readings side by side on the numbers you already have.

![The window at (2,2) read two ways: as stencil arithmetic, 320 − 4 × 40 = 160, and as the neighbour mean 80 minus the centre 40, times four. Below, the impulse window: mean 40 minus centre 255 is −215, times four is −860.](https://minio.canery.in/media/fig-04-mean-minus-centre-laplacian-by-hand.png)

*Figure 4 — The Laplacian asks one question: how far is this pixel from what its neighbours expect? Four times that gap, with the sign chosen so that a pixel brighter than its surroundings scores negative.*

| Pixel | Neighbour mean $m$ | Centre $f_C$ | $m - f_C$ | × 4 |
|---|---|---|---|---|
| (2,2), dark side of the step | 80 | 40 | 40 | **160** |
| (2,3), bright side | 160 | 200 | −40 | **−160** |
| (2,1), the impulse | 40 | 255 | −215 | **−860** |

A pixel exactly matching its neighbours' average scores zero, which is why flat regions and straight ramps both vanish: on a ramp the neighbours' average *is* the centre.

That reading gives the sign convention a meaning. A negative Laplacian says "brighter than the neighbourhood predicts", a positive one "darker". The dark side of a step is darker than its average neighbour (one of the four is on the bright side), so it scores positive; the bright side scores negative.

And it gives the noise behaviour a meaning. A pixel that disagrees with its neighbours by $\delta$ scores $4\delta$ no matter what caused the disagreement, so an isolated defect produces the largest response in the image, not the smallest.

### Curvature, summed in two directions

The second reading is geometric. In one dimension, the second difference is the curvature of the profile: positive where it bends upward, negative where it bends downward, zero where it is straight. The Laplacian adds the curvature in two perpendicular directions.

On a straight edge running vertically, the curvature along the edge is zero, so the Laplacian *is* the curvature across it. That is why the numbers at (2,2) and (2,3) match the 1-D profile of Figure 1 exactly. On a corner or a blob, both directions contribute. That second term is the whole disagreement between Marr–Hildreth and Canny, and it returns in the zero-crossing section.

### What blur removes

The third reading is the one this post is built on. Replace every pixel by the average of itself and its four neighbours — the crudest blur there is — and substitute the first reading:

$$
f_{\text{new}} = \frac{f_C + 4m}{5} = f_C + \frac{4}{5}\,(m - f_C) = f_C + \frac{1}{5}\,\nabla^2_5 f .
$$

The pixel moves four-fifths of the way to its neighbours' mean in one step, and the move is exactly one fifth of the Laplacian. The patch confirms it at every pixel:

| Pixel | Before | After the five-pixel average | Change | Laplacian ÷ 5 |
|---|---|---|---|---|
| (2,2), dark side | 40 | 72 | +32 | 160 ÷ 5 = +32 |
| (2,3), bright side | 200 | 168 | −32 | −160 ÷ 5 = −32 |
| (2,1), the impulse | 255 | 83 | −172 | −860 ÷ 5 = −172 |

The fifth is not arbitrary. This blur gives weight 1/5 to the centre and to each of its four neighbours, so its variance along one axis is $v = \tfrac15 + \tfrac15 = \tfrac25$, and half of that is the $\tfrac15$ above.

That is the general rule. A symmetric blur whose weights sum to one changes each pixel by half its variance times the Laplacian, $\tfrac{v}{2}\nabla^2 f$. A Gaussian does the same thing as the five-pixel average with better weights. For the parent's 3×3 Gaussian, $v = 0.478$, so on $x^2 + y^2$, whose Laplacian is 4 everywhere, blurring raises the origin by $0.478 \times 4 / 2 = 0.956$. The sharpening section derives the rule and says exactly when it holds.

### The analogy, and where it breaks

Think of the image as a temperature map. Heat flows from warm pixels to cool ones at a rate proportional to the Laplacian: a hot spot cools, a cold spot warms, a linear gradient stays as it is. Gaussian blurring is letting the image cool for a while, and σ² is how long. That is not a metaphor — it is the heat equation, and it is why the Laplacian is the generator of Gaussian scale space.

The analogy breaks in two places. Heat flow is a process in time and the image has no time in it: a Gaussian blur is the solution at one instant, so you cannot get "half the blur back" by subtracting, only the leading term. And temperatures have no ceiling, while pixel values are clipped at 0 and 255; every halo in a sharpened image is a temperature the display could not show.

## Which discrete Laplacian?

There is more than one 3×3 stencil with the right symmetry, and they are not interchangeable. Figure 5 lists the five that matter.

![Five 3 by 3 stencils with their weights and scale factors: five-point ×1, diagonal ×2, eight-neighbour ×3, OpenCV ksize=3 with 2 at the corners and −8 at the centre ×4, and the nine-point stencil divided by 6, ×1.](https://minio.canery.in/media/fig-05-five-stencils-laplacian-by-hand.png)

*Figure 5 — Five-point ×1, diagonal ×2, eight-neighbour ×3, OpenCV's ksize=3 ×4, nine-point ×1: the same operator at four scales, with two different anisotropies. The scale factors are what libraries forget to mention.*

The multiple of $\nabla^2$ each one approximates on smooth data comes from applying it to $f = x^2 + y^2$, whose Laplacian is exactly 4. Around the origin, the four edge-neighbours each hold 1 and the four corners each hold 2.

| Stencil | Weights | On $x^2 + y^2$ | Scale | At (2,2), clean patch |
|---|---|---|---|---|
| Five-point | [0 1 0; 1 −4 1; 0 1 0] | 4 × 1 − 0 = 4 | ×1 | 160 |
| Diagonal | [1 0 1; 0 −4 0; 1 0 1] | 4 × 2 = 8 | ×2 | 320 |
| Eight-neighbour | [1 1 1; 1 −8 1; 1 1 1] | 4 + 8 = 12 | ×3 | 480 |
| OpenCV `ksize=3` | [2 0 2; 0 −8 0; 2 0 2] | 2 × 8 = 16 | ×4 | 640 |
| Nine-point | [1 4 1; 4 −20 4; 1 4 1] ÷ 6 | (16 + 8) ÷ 6 = 4 | ×1 | 160 |

Same edge, five answers, and the ratios are the scale factors.

The **diagonal** stencil reads ×2 because the diagonal spacing is $\sqrt{2}$, and a second difference across a gap of $\sqrt{2}$ reads twice the curvature. The **eight-neighbour** stencil is the sum of the first two.

**OpenCV's `ksize=3`** kernel is twice the diagonal stencil. <!-- L59 --> It is not an arbitrary choice: it is exactly the Sobel second-x kernel $[1\ 2\ 1]^T [1\ {-2}\ 1]$ plus its transpose, which the documentation describes and the source precomputes as one 3×3 array. <!-- L61 --> <!-- L54 -->

The **nine-point** stencil is four five-point stencils plus one diagonal, divided by six. That combination is chosen for its direction behaviour, which is the next point.

### Anisotropy: which direction the stencil believes

The scale factor is a nuisance; the anisotropy is a property. To see it, feed each stencil a wave.

A stencil is a weighted sum of shifted copies of the image, and shifting the wave $e^{i(\omega_x c + \omega_y r)}$ by one pixel multiplies it by $e^{\pm i\omega_x}$ or $e^{\pm i\omega_y}$. The left and right neighbours together contribute $e^{i\omega_x} + e^{-i\omega_x} = 2\cos\omega_x$, the upper and lower ones $2\cos\omega_y$, and the centre −4:

$$
H_5(\omega_x, \omega_y) = 2\cos\omega_x + 2\cos\omega_y - 4 .
$$

The wave comes back unchanged in shape, multiplied by $H_5$; that multiplier is the stencil's transfer function. The continuous Laplacian multiplies the same wave by $-(\omega_x^2 + \omega_y^2)$, so the comparison is between those two numbers.

Frequency here is in radians per pixel. A frequency magnitude of π is a wavelength of two pixels — the alternating pattern +1, −1, +1, −1 — and the highest frequency the grid can hold.

Two waves at that magnitude make the test fair: one along the axis, $(\omega_x, \omega_y) = (\pi, 0)$, and one along the diagonal, $(\pi/\sqrt2, \pi/\sqrt2)$. Both have $\omega_x^2 + \omega_y^2 = \pi^2$, so the continuous operator returns $-\pi^2 = -9.87$ for both. Any difference between a stencil's two answers is therefore orientation, not frequency.

| At the top of the band | Along the axis | Along the diagonal | Diagonal over axis |
|---|---|---|---|
| Continuous, $-(\omega_x^2 + \omega_y^2)$ | −9.87 | −9.87 | 0 |
| Five-point, $H_5$ | 2cos π + 2cos 0 − 4 = **−4.00** | 4cos(π/√2) − 4 = **−6.42** | **+60.6%** |
| Nine-point, $H_9$ | **−4.00** | **−4.70** | **+17.6%** |

Figure 6 draws the full curves from zero frequency to the top of the band.

![Transfer-function magnitude against frequency from 0 to π: the continuous ω² curve ends at 9.87, the five-point diagonal at 6.42, the nine-point diagonal at 4.70, and both stencils along the axis at 4.00.](https://minio.canery.in/media/fig-06-transfer-functions-laplacian-by-hand.png)

*Figure 6 — A model, plotted from the closed forms in the math section. At the top of the band the five-point stencil reads 60.6% more curvature on the diagonal than on the axis; the nine-point stencil reads 17.6% more; both under-read the continuous operator, by a factor of 2.5 on the axis.*

Two different errors are visible, and they have different cures.

**The scale error.** On the axis, both stencils return $4 / 9.87 = 0.405$ of the continuous value: an under-read by a factor of 2.5, at the scale of a pixel, which is exactly the scale at which the raw stencil is usually applied.

**The direction error.** The same edge, the same sharpness, and the five-point stencil gives a 60.6% different answer depending on its orientation. The nine-point stencil cuts that spread to 17.6%, by 71%. It does not touch the scale error, which is identical for both stencils on the axis. A constant factor can fix the scale at one frequency; no constant fixes the direction, because it multiplies both orientations alike.

The nine-point stencil's leading error term depends only on the frequency's magnitude, not its direction. Patra and Karttunen derived that stencil, and its three-dimensional relatives, from the requirement that the lowest-order error be isotropic, at a computational cost they put at under 20% extra. <!-- L51 --> The Taylor expansions that produce these numbers are in the math section, and LeVeque's chapter on elliptic equations treats both stencils. <!-- L52 -->

Two rules fall out. A Laplacian output is comparable with another only after dividing by the stencil's scale factor: `scale=0.25` makes OpenCV's `ksize=3` agree with `ksize=1` on smooth data, and nothing makes them agree on an impulse.

And near the top of the band, no 3×3 stencil returns the continuous Laplacian. If the number matters rather than the sign, smooth first so that there is no energy up there. OpenCV's `ksize=5` and `7` do that smoothing implicitly, with Sobel second-derivative kernels whose scale factor is $2^{2\cdot\text{ksize}-4}$ unless normalised. <!-- L55 --> <!-- L60 --> The design of such kernels is the parent's kernel-design child post.

## Sharpening: the thing blur removes

Now make the intuition section's third reading exact, because sharpening is that reading run backwards.

### Where the factor v/2 comes from

Take a smoothing kernel $K$ and write $(a, b)$ for the offset of each weight from the centre. Ask four things of it: its weights sum to one, it is symmetric, it has the same variance $v$ along both axes, and it has no mixed moment:

$$
\begin{aligned}
&\textstyle\sum K = 1, \qquad \sum K\,a = \sum K\,b = 0, \\
&\textstyle\sum K\,a^2 = \sum K\,b^2 = v, \qquad \sum K\,ab = 0 .
\end{aligned}
$$

The first keeps a flat image flat; the second stops the blur from shifting the image; the last two are true of any separable symmetric kernel.

Now expand the image around the pixel to second order,

$$
\begin{aligned}
f(x - a,\, y - b) = {} & f - a f_x - b f_y \\
& + \tfrac12 a^2 f_{xx} + ab\, f_{xy} + \tfrac12 b^2 f_{yy} + \dots
\end{aligned}
$$

and average both sides with the weights $K$. The constant term survives because the weights sum to one. The two slope terms cancel by symmetry. The mixed term cancels with the mixed moment. The two curvature terms each pick up $v$:

$$
\boxed{\;Kf - f = \frac{v}{2}\left(f_{xx} + f_{yy}\right) + \dots = \frac{v}{2}\,\nabla^2 f + \dots\;}
$$

A blur moves each pixel by half its kernel's variance times the Laplacian. On a quadratic surface the dots are zero and the identity is exact; on a general image it is the leading term.

Check it on $f = x^2 + y^2$ with the parent's 3×3 Gaussian. Its one-dimensional weights are $[0.239, 0.522, 0.239]$, so

$$
v = 0.239\,(-1)^2 + 0.522 \cdot 0^2 + 0.239 \cdot 1^2 = 0.478 .
$$

The centre weight contributes nothing, because it sits at offset zero. The identity predicts that blurring raises the origin from 0 to $\tfrac{0.478}{2} \times 4 = 0.956$, and the nine multiplications agree. Around the origin the surface holds 2 at the four corners and 1 at the four edge-neighbours, so

$$
\begin{aligned}
Kf(0,0) &= 4 \times 0.0571 \times 2 + 4 \times 0.1248 \times 1 \\
&= 0.457 + 0.499 = 0.956 .
\end{aligned}
$$

There is a shorter route to the same number. The blurred origin is the kernel-weighted mean of $a^2 + b^2$, and that is $v + v$ by the definition of variance.

### The nominal σ is not the variance

The kernel was sampled at nominal σ = 0.8, and $\sigma^2 = 0.64$ predicts a change of 1.28 at the origin. That is wrong by a third.

| Gaussian at σ = 0.8, renormalised | Variance per axis | Change at the origin of $x^2 + y^2$ |
|---|---|---|
| Cut to 3 taps, the parent's kernel | 0.478 | **0.956** |
| Cut to 5 taps | 0.632 | 1.265 |
| Cut to 7 taps | 0.640 | 1.280 |
| Every integer offset | 0.640 | 1.280 |
| Continuous, $\sigma^2$ | 0.640 | 1.280 |

The loss is truncation, not sampling. Sampled at every integer offset, the σ = 0.8 Gaussian keeps its variance of 0.640 to three decimals. Cutting it to three taps is what costs 0.162: the weights at offsets ±2 are small, but they enter the variance multiplied by 4. Prediction from the nominal σ² overshoots the true change by 0.324, or 33.9%.

Sampling itself starts to cost variance only at smaller σ: at σ = 0.5, the untruncated sampled Gaussian has variance 0.215, not 0.25. That is the regime Lindeberg's analysis of sampled kernels is about. <!-- L31 --> At σ = 0.8 the whole gap is the cut.

### On the grid, the identity is exact

For the 3×3 Gaussian the dots in the boxed identity can be written down, because the kernel is separable. A one-dimensional blur with weights $[w_1,\ 1 - 2w_1,\ w_1]$ changes a sample by exactly $w_1$ times its second difference, with nothing left over. Blur the rows, then the columns, and multiply out:

$$
Kf - f = w_1\,\nabla^2_5 f + w_1^2\,\delta_x^2\delta_y^2 f, \qquad w_1 = 0.239 = \frac{v}{2} .
$$

Here $\delta_x^2\delta_y^2$ is the second difference along rows of the second difference along columns: a stencil with 1 at the corners, −2 at the edges and 4 at the centre. Its coefficient, $w_1^2 = 0.0571$, is the kernel's corner weight.

On the clean patch the cross term is zero, because every column is constant, so the identity holds to the last digit on every pixel. The impulse is where the two terms part:

| Pixel | $f$ | Blurred | Change | $0.239 \times \nabla^2_5 f$ | Cross term, $0.0571 \times \delta_x^2\delta_y^2 f$ |
|---|---|---|---|---|---|
| (2,2), clean | 40 | 78.2 | +38.2 | +38.2 | 0 |
| (2,3), clean | 200 | 161.8 | −38.2 | −38.2 | 0 |
| (2,1), the impulse | 255 | 98.6 | −156.4 | −205.5 | +49.1 |
| (1,2), with the impulse | 40 | 90.5 | +50.5 | +38.2 | +12.3 |

The last row is the diagonal story again. At (1,2) the five-point stencil does not see the impulse, but the blur does, through its corner weight: the cross term is 0.0571 times the impulse's excess of 215.

In the continuous limit the statement is the heat equation, $\partial L / \partial s = \tfrac{1}{2} \nabla^2 L$ with $s = \sigma^2$, <!-- L28 --> and the discrete analogue of the Gaussian satisfies the same equation with the five-point stencil in place of $\nabla^2$. <!-- L29 --> The math section works through what that equation predicts.

### Three consequences

**Unsharp masking is Laplacian sharpening.** The unsharp mask adds back a multiple of what blurring removed. Substitute the identity:

$$
g = f + k\,(f - K f) = f - k\,\frac{v}{2}\,\nabla^2 f .
$$

That is Laplacian sharpening with strength $c = kv/2$. Gonzalez and Woods present the two as neighbours in one section; they are one operator with the strength parameter written two ways. <!-- L53 -->

The minus sign is what makes it sharpen. A pixel darker than its neighbourhood has a positive Laplacian and is pushed down; a brighter one is pushed up. On the clean patch, with the 3×3 Gaussian and $k = 1$, the two forms agree to the last digit: (2,2) goes to $2 \times 40 - 78.2 = 1.8$ and (2,3) to $400 - 161.8 = 238.2$, exactly $f - 0.239\,\nabla^2_5 f$.

**The halo is the Laplacian with its sign flipped.** Apply $g = f - \nabla^2 f$ to the clean patch, which is the stencil `[0 −1 0; −1 5 −1; 0 −1 0]` in one pass. Figure 7 shows the row.

![The middle row three times: the original step 40, 40, 40, 200, 200; its Laplacian 0, +160, −160 at c1 to c3; and the sharpened row, where −120 clips to 0 on the dark side and 360 clips to 255 on the bright side.](https://minio.canery.in/media/fig-07-sharpening-halo-laplacian-by-hand.png)

*Figure 7 — The halo is the Laplacian subtracted, and it is one pixel wide on each side because the stencil is. Both lobes are clipped by the 8-bit range, which is why sharpening artefacts look like a hard dark line beside a hard bright one.*

At (2,2): $40 - 160 = -120$, clipped to 0. At (2,3): $200 + 160 = 360$, clipped to 255. The step of 160 has become a step of 255 flanked by a dark and a bright fringe, each exactly as wide as the stencil's reach. Use a wider Gaussian in the unsharp mask and the fringe widens with the kernel's negative lobe.

At the impulse the arithmetic is worse: (2,1) goes to $255 + 860$, already clipped, and its neighbour (2,2) goes to $40 - 375 = -335$, clipped to 0. Sharpening manufactures a dark ring around every hot pixel.

**Noise is amplified by $1 + 4c$ on the axis and $1 + 8c$ on a checkerboard.** The five-point stencil returns −8 on an alternating ±1 pattern, so $c = 1$ turns a one-level checkerboard into a nine-level one. This is the direct cost of the identity: whatever blur removes, sharpening adds back, noise included.

Sharpening without halos means smoothing that stops at edges, which is the parent's edge-preserving child post; and the pyramid section names the modern way to do it with Laplacians alone. Sharpening also cannot restore what the blur set to zero: it amplifies what survived.

## Zero-crossings: why the Laplacian finds edges twice

The Laplacian had been tried as an edge detector before 1980 — Rosenfeld and Kak discuss it — without much to show for it, and Marr and Hildreth's diagnosis was that it had been applied without band-limiting and without looking for zero-crossings. <!-- L06 --> Their detector fixes both. It is three steps: convolve with $\nabla^2 G$, locate the zero-crossings of the result, and check that neighbouring crossings line up into oriented segments. <!-- L09 --> The worked example already did the first two on the raw stencil; this section says what the Gaussian adds and what the method gets wrong.

### The operator

The choice of the Laplacian rests on a theorem. If the smoothed intensity varies linearly *along* a line of zero-crossings, then the zeros of $\nabla^2 (G * I)$ coincide with the zeros of the second derivative taken across the line, which are the edge. Where that condition fails — the intensity varies non-linearly along the edge, as at a corner — the Laplacian's zero is displaced to one side. <!-- L01 -->

Smoothing and differentiating commute, so the two steps collapse into one kernel, the Laplacian of the Gaussian. Written two equivalent ways,

$$
\nabla^2 G(r) = \frac{r^2 - 2\sigma^2}{2\pi\sigma^6}\, e^{-r^2/2\sigma^2} = -\frac{1}{\pi \sigma^4}\left(1 - \frac{r^2}{2\sigma^2}\right) e^{-r^2/2\sigma^2} .
$$

The factor $r^2 - 2\sigma^2$ sets the sign. The kernel is negative inside the circle $r = \sqrt{2}\,\sigma$, zero on it, and positive outside, decaying to zero: a negative disc surrounded by a positive ring, the Mexican hat. <!-- L02 -->

Its integral over the plane is zero, so a constant image returns exactly nothing — the continuous form of the stencil's weights summing to zero. A sampled kernel cut off at a finite radius loses part of its positive ring and no longer sums to zero; re-zero it, or flat regions return a small constant.

The zero circle fixes the size of the disc, $w = 2\sqrt{2}\,\sigma$, and Marr and Hildreth ran the operator with $w$ = 6, 12 and 24 pixels: <!-- L03 -->

| σ (pixels) | Zero radius, $\sqrt2\,\sigma$ | Disc diameter, $w = 2\sqrt2\,\sigma$ | Wavelength passed best, $\sqrt2\,\pi\sigma$ |
|---|---|---|---|
| 0.80, the parent's | 1.13 | 2.26 | 3.6 |
| 2.12 | 3 | 6 | 9.4 |
| 4.24 | 6 | 12 | 18.8 |
| 8.49 | 12 | 24 | 37.7 |

The last column comes from the kernel's spectrum. With $\rho$ in cycles per pixel,

$$
\widehat{\nabla^2 G}(\rho) = -4\pi^2\rho^2\, e^{-2\pi^2\sigma^2\rho^2} .
$$

The $\rho^2$ factor removes the mean and boosts high frequencies; the Gaussian factor removes the highest. Their product is a band-pass filter that peaks at $\rho = 1/(\sqrt2\,\pi\sigma)$, a wavelength of $\sqrt2\,\pi\sigma \approx 4.44\,\sigma$.

At half power the band runs from 0.62 to 1.44 times that peak frequency, a ratio of 2.34, which is 1.22 octaves. That is Marr and Hildreth's half-power bandwidth of about 1.2 octaves, so each σ looks at roughly one octave of the image's spectrum. <!-- L07 --> Measured at half amplitude instead, the same band is 1.76 octaves. Figure 8 draws the kernel.

![The Laplacian of Gaussian at σ = 1 against radius: a negative lobe reaching −0.191 at the centre with zeros at ±1.41σ, and the difference of Gaussians at ratio 1.6 drawn over it, reaching −0.097 with zeros at ±1.76σ.](https://minio.canery.in/media/fig-08-mexican-hat-dog-laplacian-by-hand.png)

*Figure 8 — A model, plotted from the two closed forms. The difference-of-Gaussians at ratio 1.6 has a central lobe 24% wider and half as deep as the Laplacian of Gaussian at the same σ; neither matters for where the zero is, and neither matters for extrema across scale.*

At σ = 0.8 the same kernel is small enough to write as numbers. Convolving the five-point stencil with the parent's 3×3 Gaussian gives the 5×5 kernel in Figure 9, which is what the worked example's "smooth first" column applied in one pass.

![A 5 by 5 grid of weights: the centre −0.591 and its four neighbours −0.1123 shaded as the negative disc, the diagonals +0.021, the outer ring 0.1248 on the axes and 0.0571 beside them, zeros in the corners; all 25 sum to zero.](https://minio.canery.in/media/fig-09-log-kernel-laplacian-by-hand.png)

*Figure 9 — This is the Mexican hat at σ = 0.8: a negative disc of radius 1.13 pixels covering the centre and its four neighbours, a positive ring outside it, and weights that sum to zero so that flat regions return exactly nothing.*

The centre weight is −0.591 and the four neighbours are −0.1123. The diagonals, at distance 1.41, are already positive, +0.021, because $\sqrt{2}\,\sigma = 1.13$ falls between 1 and 1.41. The ring at distance 2 carries the parent's Gaussian weights unchanged.

On the patch this kernel gives 45.3 at the clean edge pixel and 21.1 with the impulse: the numbers from the worked example, now with a picture of what produced them. These are the weights of this construction — the five-point stencil on a three-tap Gaussian — not universal Laplacian-of-Gaussian coefficients; sampling $\nabla^2 G$ directly at σ = 0.8 gives different numbers.

Marr and Hildreth also proposed computing the kernel as a difference of two Gaussians, which is cheaper, and settled on a ratio of 1.6 between the two standard deviations. <!-- L04 --> That number is often repeated as if it were a best fit. It is not. Their appendix chooses 1.6 as the point where the filter's bandwidth is still narrow but its sensitivity has recovered to about a third of the single Gaussian's: a bandwidth-versus-sensitivity trade-off, with the resulting filter having a half-sensitivity bandwidth of 1.8 octaves. <!-- L05 -->

The closed forms behind Figure 8 show what the trade costs pointwise: at ratio 1.6 the difference of Gaussians has half the central depth of $(k-1)\sigma^2 \nabla^2 G$ and a lobe 24% wider than $\nabla^2 G$ at σ. For locating a zero, or an extremum over scale, a constant factor and a slightly larger effective σ change nothing. That is why the scale-selection section can use the same trick without apology, and why `skimage.feature.blob_dog` still defaults to `sigma_ratio=1.6` forty-six years later. <!-- L66 --> Why a difference of Gaussians approximates $\nabla^2 G$ at all is derived there.

### The edges that are not there

The logic runs one way only. If the gradient $g = f'$ has an extremum at $x_0$, then

$$
g'(x_0) = f''(x_0) = 0 ,
$$

so every extremum of the gradient is a zero of the second derivative. The converse fails: a zero of $f''$ does not say whether $|g|$ has a maximum there, which is an edge, or a minimum, which is not. Figure 10 shows the second case.

![A model profile with two nearby rising steps, 40 to 120 to 200; its first derivative with two peaks and a dip between them; its second derivative with three zero-crossings, the two under the peaks marked authentic and the one under the dip marked phantom.](https://minio.canery.in/media/fig-10-phantom-edges-laplacian-by-hand.png)

*Figure 10 — A model profile. All three are zeros of the second derivative; two sit on maxima of the gradient and are edges, one sits on the minimum between them and is not. The slope of the crossing — whether the second derivative falls or rises through zero in the gradient direction — tells them apart.*

Two steps of the same sign, close together, give the gradient two peaks and a dip, and the second derivative crosses zero at all three. The middle crossing marks the place where the gradient is weakest — the opposite of an edge. At an edge on a rising profile, the second derivative falls through zero, from + to −; at the phantom between two such edges, it rises.

Clark named these phantom edges and gave the practical test: shrink the filter scale and an authentic edge's contrast rises while a phantom's falls, so "the closer one examines it, the weaker it becomes". <!-- L37 --> The worked example produced one — the crossing at column 1.70 that exists only because of the bad pixel — and OpenCV's own Laplace tutorial warns that zeros "can actually appear in other meaningless locations". <!-- L58 -->

Marr and Hildreth's detector has no threshold to suppress them, because it never computes an edge strength. A zero-crossing between −1 and +1 satisfies the same condition as one between −860 and +375. Canny's detector does compute a strength, and that is one of his two arguments against the Laplacian. <!-- L08 -->

### Canny's argument, and the one that answers it

Canny's first point is that in one dimension his operator and the Marr–Hildreth detector are almost the same thing, since the maxima of a first-derivative response are the zero-crossings of the second. <!-- L32 --> His second is the one that matters in two dimensions, and Figure 11 draws it.

![A straight edge, dark on the left and bright on the right, with axis n across it and axis t along it; beside it the Laplacian written as the second derivative across, which carries the edge, plus the second derivative along, zero on a straight edge and noise elsewhere.](https://minio.canery.in/media/fig-11-canny-decomposition-laplacian-by-hand.png)

*Figure 11 — The Laplacian is the second derivative across the edge plus the second derivative along it. On a straight edge the second term is zero; on a noisy one it is pure noise, which is Canny's case for a directional operator.*

Rotate the axes so that $n$ points along the gradient, across the edge, and $t$ along the edge. The Laplacian does not change under rotation, so

$$
\nabla^2 I = \frac{\partial^2 I}{\partial n^2} + \frac{\partial^2 I}{\partial t^2} .
$$

The first term is the directional operator Canny derived. The second contributes nothing to detection or localisation on a straight edge, because the intensity is constant along it, but it adds its full share of noise to the output. <!-- L33 --> Torre and Poggio worked out the same relation between the Laplacian and the second derivative along the gradient from the regularisation side, and drew the same conclusion: the Laplacian's zero-crossings are not the only thing worth computing. <!-- L36 --> Haralick's tests of the same period ranked zero-crossings of the second directional derivative first and the Marr–Hildreth Laplacian last, on synthetic step edges and with his own implementation of $\nabla^2 G$. <!-- L38 -->

The counter-argument is Yuille and Poggio's, and it is about scale rather than noise. As the Gaussian's σ increases, new zero-crossings of the Laplacian are never created, in any number of dimensions, and the Gaussian is the only linear filter with that property. For the second derivative along the gradient, no filter has it. <!-- L39 --> Babaud, Witkin, Baudin and Duda proved the one-dimensional version in the same journal issue: the Gaussian is the only kernel for which extrema of the first derivative only ever disappear as the bandwidth narrows. <!-- L40 -->

So if edges are to be tracked from coarse to fine — which is how Marr and Hildreth intended their channels to be combined, and how every scale-space method since has worked — the Laplacian's zero-crossings are the ones that behave, and the directional operator's are not. Canny wins on a single scale; the Laplacian wins across scales.

| | Marr–Hildreth | Canny |
|---|---|---|
| Response | $\nabla^2 (G * I)$, one number per pixel | $\nabla (G * I)$, a magnitude and a direction |
| Edge criterion | the response changes sign | the magnitude is a maximum along the gradient |
| Direction | none: two second derivatives summed | the gradient's own |
| Crossing at a gradient minimum | accepted unless tested | rejected by keeping only maxima |
| Edge strength | none, so nothing to threshold | the magnitude, thresholded |
| As σ grows | crossings are never created | no such guarantee |

Marr and Hildreth's operator also did something neither argument mentions: it made large-support operators practical at all, because a Gaussian window has the narrowest bandwidth for its width. <!-- L34 --> The four steps that replaced zero-crossings in practice — smooth, gradient, thin, link — are the parent's Canny child post.

## Scale selection: the Laplacian as a ruler

The zero-crossing section held σ fixed. This section varies only σ, and the Laplacian becomes a measuring instrument.

### Why the raw response cannot be compared across σ

Convolve a structure with $\nabla^2 G$ at increasing σ and the response falls off like $1/\sigma^2$ regardless of the structure, because the kernel's amplitude shrinks as $1/\sigma^4$ while its area grows as $\sigma^2$. Any search for "the σ with the strongest response" therefore returns the smallest σ tried.

Lindeberg's fix is to multiply each derivative by $\sigma$ per order — for a second derivative, by $\sigma^2$ — which makes the operator dimensionless and the comparison across scales meaningful: <!-- L16 -->

$$
R(x, y;\, \sigma) = \sigma^2\, \nabla^2 (G_\sigma * f) .
$$

The claim is that the σ at which $R$ is extremal is the size of the structure under the kernel. For a Gaussian blob of scale $t_0$, Lindeberg showed the extremum falls exactly at $t = t_0$. <!-- L17 --> For two shapes you can draw, the closed forms are short enough to work by hand, and Figure 12 plots them.

![The scale-normalised response at the centre against σ from 0.5 to 4: a bar of width 3 peaks at σ = 1.5 with 77.4, and a disc of radius 3 peaks at σ = 2.12 with 117.7.](https://minio.canery.in/media/fig-12-scale-selection-laplacian-by-hand.png)

*Figure 12 — A model, plotted from the closed forms in the math section, for structures of contrast 160. The σ at the peak is the size: half the width for a bar, the radius over √2 for a disc. Neither curve is sharp, which is why the search compares neighbours first and fits only afterwards.*

For a bar of width $w$ and contrast $A$, the normalised response at the centre is

$$
R_{\text{bar}}(\sigma) = -\frac{A w}{\sqrt{2\pi}\,\sigma}\, e^{-w^2/8\sigma^2} ,
$$

and for a disc of radius $r$ and the same contrast it is

$$
R_{\text{disc}}(\sigma) = -A\, \frac{r^2}{\sigma^2}\, e^{-r^2/2\sigma^2} .
$$

Setting the σ-derivative to zero puts the bar's peak at $\sigma = w/2$ and the disc's at $\sigma = r/\sqrt{2}$. With the patch's contrast of 160, a bar three pixels wide and a disc of radius 3 give:

| σ | 1.0 | 1.5 | 2.12 | 3.0 | 4.0 |
|---|---|---|---|---|---|
| Bar, $w = 3$ | −62.2 | **−77.4** | −70.3 | −56.3 | −44.6 |
| Disc, $r = 3$ | −16.0 | −86.6 | **−117.7** | −97.0 | −67.9 |

The disc result is why Lindeberg draws each detected blob as a circle whose radius is proportional to the selected scale, <!-- L19 --> and why `skimage.feature.blob_log` reports the radius of each blob as $\sqrt{2}\,\sigma$ in two dimensions. <!-- L64 --> For a sinusoid the same calculation gives $\sigma = \lambda / (\sqrt{2}\,\pi)$, the wavelength over 4.44 <!-- L18 --> — the same 4.44 as the Mexican hat's best-passed wavelength in the zero-crossing section, read the other way round.

### The difference of Gaussians, again

Lowe's observation makes this cheap. Start from the heat equation in the scale $s = \sigma^2$ and change variable to σ with the chain rule, $ds/d\sigma = 2\sigma$:

$$
\frac{\partial G}{\partial \sigma} = \frac{\partial G}{\partial s}\,\frac{ds}{d\sigma} = \frac{1}{2}\nabla^2 G \cdot 2\sigma = \sigma\, \nabla^2 G .
$$

Now replace the derivative by a finite difference over one step, from σ to $k\sigma$:

$$
\begin{aligned}
\frac{G(k\sigma) - G(\sigma)}{k\sigma - \sigma} &\approx \sigma\, \nabla^2 G \\
\Longrightarrow\quad G(k\sigma) - G(\sigma) &\approx (k - 1)\,\sigma^2 \nabla^2 G .
\end{aligned}
$$

A difference of two Gaussians whose σ differ by a constant factor therefore already carries the $\sigma^2$ normalisation. <!-- L22 --> The factor $(k-1)$ is the same at every scale, so it moves no extremum; dividing by it, as `blob_dog` does, only restores the amplitude. The approximation degrades as $k$ grows, and Lowe reports it makes almost no difference to the stability of the extrema even at $k = \sqrt{2}$. <!-- L23 --> The check behind Figure 8 agrees: at $k = 1.6$ the amplitude is half and the lobe is wider, and both are the same at every σ.

SIFT builds its octaves this way, with a base σ of 1.6 chosen for efficiency and $k = 2^{1/3}$: <!-- L27 --> three equal multiplicative steps per doubling of σ, because $k^3 = 2$.

| Step | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| σ, in units of the octave's first | 1 | 1.26 | 1.59 | 2 |

### The 26-neighbour test

Figure 13 shows what the search actually does.

![A stack of five image planes drawn as layers along a vertical scale axis labelled with sigma values increasing by a factor k, each plane the scale-normalised Laplacian response, with one pixel on the middle plane highlighted and its 8 spatial neighbours plus the 9 pixels above and 9 below marked as the 26 comparisons](https://minio.canery.in/media/fig-13-scale-space-cube-laplacian-by-hand.png)

*Figure 13 — A blob is a point that beats its 8 spatial neighbours and its 18 neighbours one scale up and one scale down. In a DoG stack each plane is (k−1)σ²∇²G, so the σ² is built in; in a `gaussian_laplace` stack it must be multiplied in by hand.*

A scale-space extremum is a pixel whose normalised response exceeds all 26 neighbours in the 3×3×3 block around it in space and scale, refined by fitting a parabola over σ. <!-- L20 --> The count is three 3×3 slices less the candidate itself:

$$
\underbrace{(9 - 1)}_{\text{same scale}} + \underbrace{9}_{\text{one scale down}} + \underbrace{9}_{\text{one scale up}} = 26 .
$$

Scale is a third axis, searched exactly like the two spatial ones. A bright blob gives a negative Laplacian, so detectors either flip the sign and look for maxima, or test both maxima and minima.

On the disc of radius 3 from Figure 12, sampled on that ladder of σ, the candidate at σ = 2.00 holds 116.9. Its largest neighbour is 111.6, one scale up at the same pixel; the eight spatial neighbours at every scale are smaller, because the disc is centred on the pixel. So the search reports a blob at the disc's centre at σ = 2.00 — not at 2.12, because 2.12 is not on the ladder.

The parabola recovers most of the difference. Fit one through the three responses at the centre — 95.8, 116.9 and 111.6, at three equally spaced values of $\log \sigma$ — and its vertex sits a fraction $\delta$ of a step above σ = 2.00:

$$
\delta = \frac{1}{2}\,\frac{R_{-} - R_{+}}{R_{-} - 2R_{0} + R_{+}} = \frac{1}{2}\,\frac{95.8 - 111.6}{95.8 - 233.8 + 111.6} = 0.30 .
$$

The ladder has three steps per doubling and σ = 2.00 is step 3, so the refined scale is

$$
\sigma^\ast = 2^{(3 + 0.30)/3} = 2.14 ,
$$

about 1% above the closed form's 2.12. Fit in the coordinate that was sampled evenly: the same three points fitted as a parabola in σ itself put the vertex at 2.18, and in σ² at 2.22. SIFT fits a quadratic in position and scale at once; that fit is worked in the parent's scale-space child post.

That is the test `blob_log` runs, after multiplying each `gaussian_laplace` plane by σ² and flipping the sign so that bright blobs are maxima; `blob_dog` instead multiplies its differences by $1/(k-1)$. <!-- L65 --> <!-- L66 --> Lindeberg notes that for discrete kernels the plain $\sigma^2$ factor is one of two options, and that normalising each discrete kernel's $l_p$ norm to match the continuous one gives more accurate scales when the kernel is only a few pixels wide. <!-- L21 -->

### What the evidence says

Mikolajczyk and Schmid compared the candidates and found that the Laplacian of Gaussian selects the correct characteristic scale most often, and that the Harris measure, good at locating a corner, rarely reaches a maximum over scale at all. <!-- L41 --> Their reading of why is the matched-filter one: the normalised $\nabla^2 G$ peaks when its size matches the blob under it. <!-- L44 --> Their Harris-Laplace detector splits the job accordingly: Harris for position, normalised Laplacian for scale. <!-- L43 -->

The Laplacian's weakness is the one Canny identified in a different costume. It also peaks along straight edges, where the change is in one direction only and the position along the edge is undetermined, and such maxima are unstable. <!-- L42 --> SIFT rejects them with the Hessian $H$ of the response, whose eigenvalues $\lambda_1, \lambda_2$ are its two principal curvatures. Writing $r = \lambda_1/\lambda_2$, Lowe tests the trace and determinant instead of computing eigenvalues:

$$
\frac{\operatorname{Tr}(H)^2}{\operatorname{Det}(H)} = \frac{(\lambda_1 + \lambda_2)^2}{\lambda_1 \lambda_2} = \frac{(r+1)^2}{r} .
$$

The ratio is 4 for a round blob, $r = 1$, and grows with $r$, so a bound on it is a bound on the curvature ratio. With $r = 10$ the bound is $121/10 = 12.1$, and a keypoint at or above it is discarded. <!-- L26 --> A negative determinant means the two curvatures have opposite signs, a saddle rather than an extremum, and the point is discarded outright. <!-- L71 -->

Lindeberg's normalisation is what makes any of this scale-invariant, and Mikolajczyk's earlier experiments found the extrema of $\sigma^2 \nabla^2 G$ more stable than those of the gradient, the Hessian or the Harris function. <!-- L24 --> Why σ is a search dimension at all is the parent's scale-space child post; the structure tensor that Harris-Laplace borrows is another.

## The pyramid: the same operator, resampled

Burt and Adelson's Laplacian pyramid, published in 1983, <!-- L69 --> is what you get when the difference of Gaussians from the last section is computed at octave spacing with the arithmetic reordered so that nothing is stored twice.

### REDUCE, EXPAND, subtract

Build a Gaussian pyramid by blurring with a small separable kernel and keeping every other sample; call that REDUCE. Blurring first is what stops the decimation from aliasing: the blur removes the frequencies the coarser grid cannot hold.

Burt and Adelson constrain the five-tap kernel $[c, b, a, b, c]$ three ways: it is symmetric, it sums to one, and every input sample contributes the same total weight to the next level. <!-- L10 --> The last constraint does the work. A sample on a kept position reaches the next level through the taps $a$ and $c$, $c$; a sample between kept positions reaches it through $b$, $b$. Equal contribution sets the two totals equal:

$$
a + 2c = 2b, \qquad a + 2b + 2c = 1 \quad\Longrightarrow\quad b = \frac14, \qquad c = \frac14 - \frac{a}{2} .
$$

One parameter is left, and it decides the shape:

| $a$ | Kernel | Shape of the equivalent weighting | Variance per axis |
|---|---|---|---|
| 0.5 | [0, ¼, ½, ¼, 0] | triangular | 0.5 |
| 0.4 | [0.05, 0.25, 0.4, 0.25, 0.05] | Gaussian-like | 0.9 |
| 0.375 | [1, 4, 6, 4, 1] / 16 | binomial — OpenCV's `pyrDown` | 1.0 |
| 0.3 | [0.1, 0.25, 0.3, 0.25, 0.1] | broader than Gaussian | 1.3 |

The shape descriptions are Burt and Adelson's; <!-- L11 --> the third row is a derivation. Put $a = 0.375$ into $c = \tfrac14 - \tfrac{a}{2}$ and the kernel is $[1, 4, 6, 4, 1]/16$, the fourth row of Pascal's triangle over its sum. Its outer product with itself is the $5 \times 5$ kernel that `cv2.pyrDown` convolves with before keeping every other row and column. <!-- L57 --> Applied as two passes of the five-tap kernel it costs 10 multiplications per output instead of 25.

EXPAND inserts zeros between the samples and filters with the same kernel times 4, which is what `cv2.pyrUp` does. <!-- L57 --> The 4 — a 2 per axis — restores the brightness the zeros diluted, and equal contribution is what makes it work at every pixel. After zero insertion, an output on a kept position sees the taps $c, a, c$ and an output between kept positions sees $b, b$, so per axis the two phases interpolate with

$$
2\,[c,\ a,\ c] = \tfrac{1}{8}\,[1,\ 6,\ 1] \qquad\text{and}\qquad 2\,[b,\ b] = \tfrac{1}{2}\,[1,\ 1] .
$$

Both sum to one only because $a + 2c = 2b$: that is what the constraint is for. A constant image comes back constant at both phases.

Run it on the clean patch, with reflect-101 borders. Every column of the clean patch is constant, so each level is one row repeated, and one row tells the whole story:

| | c0 | c1 | c2 | c3 | c4 |
|---|---|---|---|---|---|
| $g_0$, the middle row | 40 | 40 | 40 | 200 | 200 |
| blurred by [1, 4, 6, 4, 1] / 16 | 40 | 50 | 90 | 150 | 180 |
| $g_1$, every other sample | 40 | · | 90 | · | 180 |
| EXPAND($g_1$) | 52.5 | 65 | 95 | 135 | 157.5 |
| $L_0 = g_0 - $ EXPAND($g_1$) | −12.5 | −25 | **−55** | **+65** | +42.5 |

EXPAND puts 95 at c2 from the kept-position weights, $(40 + 6 \times 90 + 180)/8$, and 135 at c3 from the in-between ones, $(90 + 180)/2$. Figure 14 shows the whole construction: two levels down, and the way back up.

![Flowchart of a two-level pyramid: the image g0 passes through REDUCE, blur and keep every other sample, to g1, and g1 through REDUCE to g2, the residual, stored whole as L2; each level minus the EXPAND of the level above gives L0 = g0 − E(g1), fine detail, and L1 = g1 − E(g2), coarser detail; a dashed return path expands and adds L1, then L0, to give g0 again](https://minio.canery.in/media/fig-14-laplacian-pyramid-laplacian-by-hand.png)

*Figure 14 — The pyramid stores the Laplacian at each octave and the residual blur at the top; adding them back is exact by construction, because the same EXPAND that was subtracted is added. Redrawn from the construction in Burt and Adelson 1983.*

The Laplacian level is the prediction error: $L_l = g_l - \text{EXPAND}(g_{l+1})$, with the smallest level stored whole, $L_N = g_N$. <!-- L12 --> On the patch it is negative on the dark side of the step, positive on the bright side, and crosses zero at c = 2.46: the Laplacian's two lobes with the sign flipped. The level is the image minus a blurred prediction of itself, and by the blur identity that is about $-\tfrac{v}{2}\nabla^2 f$.

The lobes are unequal, −55 and +65, because the two sides of the step are predicted by different phases: c2 sits on a kept position, c3 between two. A pyramid level depends on where the samples fall, which is the price of decimating.

Reconstruction reverses the steps — expand the top, add the next level, repeat — and it is exact, not approximately so, because the same EXPAND($g_{l+1}$) is subtracted and added back. <!-- L12 --> On the patch, 52.5 + (−12.5) = 40 and 135 + 65 = 200. REDUCE loses information; the pyramid does not, because it keeps what REDUCE lost. Quantise the levels, as a coder does, and reconstruction is only as exact as the quantiser.

### Why it is called a Laplacian

Each level is the difference between the image blurred at two scales an octave apart: measured in the original image's pixels, $g_1$ has been blurred and then sampled at twice the spacing, so its effective σ is about double. By the last section that difference is a scaled $\sigma^2 \nabla^2 G$ — loosely, at $k = 2$.

Burt and Adelson say as much: each level equals the image convolved with the difference of two Gaussian-like functions, which resembles a Laplacian at that scale, so the pyramid is a set of band-pass copies with the operator's scale doubling per level. <!-- L13 --> It is a band-pass copy of the image, not $\nabla^2$ applied to it; the patch's $L_0$ has the Laplacian's shape, not its values.

### What the redundancy buys

The levels of a $256 \times 256$ image hold a third more samples than the image:

| Level | Size | Samples |
|---|---|---|
| $L_0$ | 256 × 256 | 65,536 |
| $L_1$ | 128 × 128 | 16,384 |
| $L_2$ | 64 × 64 | 4,096 |
| $L_3$ | 32 × 32 | 1,024 |
| $g_4$, stored whole | 16 × 16 | 256 |
| **Total** | | **87,296, or 1.332 × the image** |

Each level has a quarter of the samples of the one below, so the total tends to

$$
1 + \frac14 + \frac{1}{16} + \dots = \frac{1}{1 - 1/4} = \frac43
$$

times the image. Five full-size blurred copies would cost five times. The third extra buys the exact reconstruction.

The levels compress because they are prediction errors: most of their values sit near zero, which quantises coarsely and codes short. Burt and Adelson's 257×257 "Lady" image has 66,049 pixels whose histogram carries an estimated 7.57 bits of entropy each — 499,991 bits in all, against 528,392 at a flat 8 bits. <!-- L14 -->

That entropy is first order, $H = -\sum_i p_i \log_2 p_i$ over the 256 grey levels: the floor for a lossless coder that sees one pixel at a time, with 8 bits meaning a flat histogram. Quantising the Laplacian levels and coding them with variable-length codes reached 1.58 bits per pixel; "Walter" reached 0.73. <!-- L14 --> Those rates are lossy, so they do not beat the 7.57-bit floor. They show how much of it is predictable from the neighbours, which a histogram cannot see and the pyramid stores only as error.

Sending the top levels first gives progressive transmission. Levels 4 to 8 alone are 0.03 bits per pixel and already a recognisable picture; adding the lower levels raises the rate to 0.31, 0.81 and finally 1.58. <!-- L15 -->

Two later uses show what a per-scale Laplacian buys. The multiresolution spline blends two images level by level, with a transition zone as wide as the wavelengths in that level, so coarse content blends over a long distance while fine detail is joined sharply. <!-- L67 --> Written with a Gaussian pyramid $M^l$ of the blending mask, each level of the result is

$$
L^l_{\text{blend}} = M^l\, L^l_A + (1 - M^l)\, L^l_B ,
$$

and reconstruction does the rest: the mask is blurred more at each coarser level, which is what widens the transition there.

Local Laplacian filters apply a point-wise nonlinearity per level and obtain edge-preserving smoothing, detail enhancement and tone mapping — the halo-free sharpening the sharpening section asked for — from nothing but pyramids and small Gaussian blurs. <!-- L68 --> Where the pyramid stops being enough and orthogonal bases take over — no redundancy, and detail split by orientation — is the parent's wavelets child post.

## Keeping the Laplacian instead of the pixels

The last job inverts the others. Instead of reading the Laplacian off an image, keep the Laplacian, throw the pixels away, and ask what image is consistent with it.

### Poisson image editing

A function on a bounded region is determined by two things: its values on the boundary and its Laplacian inside. Given both, the Poisson equation has exactly one solution. <!-- L45 --> Pérez, Gangnet and Blake turned that into an editing tool: cut a region Ω out of a source image, take its Laplacian, keep the *target* image's values on the boundary of Ω, and solve for the pixels inside. Figure 15 shows what is kept from where.

![A source image whose Laplacian is transplanted into a region Ω of a target image; on the boundary of Ω the pixels are the target's, inside Ω the unknown pixels satisfy one five-point equation each, ∇²f = ∇²g.](https://minio.canery.in/media/fig-15-poisson-editing-laplacian-by-hand.png)

*Figure 15 — What is transplanted is the source's Laplacian; the pixel values inside are whatever makes that Laplacian consistent with the target's boundary. The seam disappears because the only thing that changed across it is a slow gradient.*

Why the seam vanishes is a perceptual fact Pérez and colleagues cite from Land and McCann: slow gradients of intensity, which are exactly what the Laplacian suppresses, can be laid over an image without being noticed. <!-- L46 --> Solving for the interior lets a slow gradient absorb the mismatch between the source's brightness and the target's, while the source's edges, textures and highlights — the second derivatives — come through untouched.

In discrete form the equation at every interior pixel is the five-point stencil: $4 f_p - \sum f_q = 4 g_p - \sum g_q$ over the four neighbours, with $f_q$ replaced by the target's value wherever $q$ lies on the boundary. The authors recommend discretising the variational form rather than the differential equation when the boundary is irregular. <!-- L47 -->

On the patch, what would be kept from the middle row is $[0, 160, -160, 0]$ — the shape of the step — while the levels 40 and 200 come from whatever the target holds at the ends. Burt and Adelson's blending is the approximate version of this, inserting the source Laplacian at the finest level only; Poisson editing does it exactly. <!-- L48 -->

### The variance of the Laplacian

The other way to keep the Laplacian is as a statistic. An in-focus image has large second derivatives and a defocused one does not, so the variance of the Laplacian response over an image, or a window, is a focus measure. Pech-Pacheco and colleagues reported a modified-Laplacian measure outperforming the Tenengrad gradient measure for microscope autofocus, <!-- L49 --> and it has been a default choice since.

Its weakness follows from the worked example: a single hot pixel contributes $860^2$ to the variance, which is 29 times what the genuine edge contributes at $160^2$. Pertuz, Puig and Garcia's comparison of focus measures found the Laplacian-based ones the most sensitive to noise, and concluded that no absolute ranking of focus measures holds across conditions. <!-- L50 --> Smooth first, or measure the median of the absolute response instead of the variance, and the hot pixel counts once rather than 29 times.

Gradient-domain editing in general — Poisson cloning, HDR compression, seamless tiling — is its own child post.

## The math

The symbols, then the forms, then each collapsed back onto the patch.

| Symbol | Meaning | Units |
|---|---|---|
| $f$, $I$ | the image as a continuous surface, and as a sampled array | intensity |
| $\nabla^2$ | the Laplacian, $\partial^2/\partial x^2 + \partial^2/\partial y^2$ | intensity / length² |
| $\nabla^2_5$ | the five-point stencil $[0\ 1\ 0;\ 1\ {-4}\ 1;\ 0\ 1\ 0]$ | intensity / pixel² |
| $m$ | the mean of a pixel's four neighbours | intensity |
| $H$ | the Hessian matrix of second partial derivatives | intensity / length² |
| $\omega$ | spatial frequency, radians per pixel; $\pi$ is the highest the grid holds | rad / pixel |
| $\sigma$, $s = \sigma^2$ | the Gaussian's standard deviation and variance; $s$ is the scale parameter | pixel, pixel² |
| $v$ | a discrete kernel's actual variance along one axis | pixel² |
| $w_1$ | the 3×3 Gaussian's one-dimensional side weight, 0.239, equal to $v/2$ | dimensionless |
| $G_\sigma$ | the Gaussian, $e^{-r^2/2\sigma^2} / 2\pi\sigma^2$ | 1 / length² |
| $R$ | the scale-normalised response, $\sigma^2 \nabla^2 (G_\sigma * f)$ | intensity |
| $k$ | the ratio between adjacent scales in a difference of Gaussians | dimensionless |

### The operator

$$
\nabla^2 f = f_{xx} + f_{yy} = \operatorname{tr} H .
$$

The Laplacian is the trace of the Hessian, and the trace of a matrix does not change under rotation of the axes, which is the algebraic reason it is the one orientation-free second-order operator. Rotate the axes so that one points along the gradient and the trace becomes the second derivative across the edge plus the second derivative along it — Canny's decomposition, in one line.

On the grid the second derivative along a row is the second difference $f[c-1] - 2f[c] + f[c+1]$, and the five-point stencil is that difference along rows plus the same along columns. At (2,2) on the clean patch the row term is $40 - 80 + 200 = 160$ and the column term is $40 - 80 + 40 = 0$; their sum is the 160 from the worked example.

### The transfer function

A stencil applied to the wave $e^{i(\omega_x c + \omega_y r)}$ returns the same wave times a number, and that number is the transfer function. For the five-point stencil,

$$
H_5(\omega_x, \omega_y) = 2\cos\omega_x + 2\cos\omega_y - 4 = -4\left[\sin^2\tfrac{\omega_x}{2} + \sin^2\tfrac{\omega_y}{2}\right],
$$

against the continuous operator's $-(\omega_x^2 + \omega_y^2)$. At low frequency the two agree; at the top of the band the stencil returns −4 for a wave along the axis, where the continuous value is −9.87, and −6.42 for a wave of the same frequency along the diagonal.

**Where the anisotropy comes from.** Expand each cosine to fourth order, $\cos\omega = 1 - \omega^2/2 + \omega^4/24 - \dots$:

$$
H_5 = -(\omega_x^2 + \omega_y^2) + \frac{\omega_x^4 + \omega_y^4}{12} + \dots
$$

The leading error, $(\omega_x^4 + \omega_y^4)/12$, is not a function of the frequency's magnitude alone: for a fixed magnitude it is largest on the axes and smallest on the diagonal, which is why the diagonal wave is over-read relative to the axis wave by a growing margin as the frequency rises.

The same expansion for the nine-point stencil, $\tfrac16(8\cos\omega_x + 8\cos\omega_y + 4\cos\omega_x\cos\omega_y - 20)$, gives

$$
H_9 = -(\omega_x^2 + \omega_y^2) + \frac{(\omega_x^2 + \omega_y^2)^2}{12} + \dots
$$

whose leading error depends only on the magnitude: the first correction is isotropic. The residual 17.6% spread at the top of the band comes from the sixth-order terms. Evaluating both exact forms at $(\pi, 0)$ and $(\pi/\sqrt2, \pi/\sqrt2)$ gives the four numbers in Figure 6.

### The heat equation and the sharpening identity

$$
\frac{\partial L}{\partial s} = \frac{1}{2}\nabla^2 L, \qquad L(\cdot\,; 0) = f, \qquad s = \sigma^2 .
$$

Gaussian blurring to scale $s$ is the same as running this equation for time $s$; the Laplacian is the rate at which blur changes the image, per unit of scale. <!-- L28 --> The scale is measured as a variance because variances add under convolution: blurring at $s_1$ and then at $s_2$ is blurring at $s_1 + s_2$, and only in that variable does the equation have a constant coefficient.

The sign of the Laplacian says which way a pixel moves as blur begins. Where $\nabla^2 L \gt 0$, a pixel below its neighbours, it rises; where $\nabla^2 L \lt 0$ it falls; where it is zero it does not move, for the moment. Under the 3×3 Gaussian the patch's (2,2), at +160, rises from 40 to 78.2; (2,3), at −160, falls from 200 to 161.8; and the impulse, at −860, falls hardest, from 255 to 98.6.

On the quadratic $x^2 + y^2$ the equation reads $\partial L/\partial s = \tfrac12 \times 4 = 2$, so the origin climbs at 2 per unit of variance: to 1.28 under the continuous σ = 0.8 Gaussian, $s = 0.64$, and to 0.956 under the 3×3 kernel, $v = 0.478$. Two kernels, two variances, no contradiction.

The Gaussian is not one choice among many here: Koenderink and Lindeberg showed that, under mild assumptions, it is the only kernel whose family of blurs never creates structure that was not in the image, so "the Laplacian of the smoothing kernel" means the Laplacian of the Gaussian and nothing else. <!-- L25 --> Integrate for a short time and $G_s * f - f \approx \tfrac{s}{2}\nabla^2 f$; for a discrete kernel the exact statement on quadratics replaces $s$ by the kernel's own variance $v$.

The discrete analogue of the Gaussian satisfies the same equation with $\nabla^2_5$ in place of $\nabla^2$, so the five-point stencil is not merely an approximation to the generator of blur on the grid; it is that generator. <!-- L29 --> Step the equation forward explicitly and each step is a small blur:

$$
L \leftarrow L + \frac{\Delta s}{2}\, \nabla^2_5 L .
$$

With $\Delta s = 2/5$ the step is exactly the five-pixel average from the intuition section, whose variance is $2/5$. A step is stable while its gain, $1 + \tfrac{\Delta s}{2} H_5(\omega)$, stays between −1 and 1 at every frequency. $H_5$ runs from 0 down to −8 at the checkerboard $(\pi, \pi)$, so the gain there is $1 - 4\Delta s$ and the limit is $\Delta s \le 1/2$:

| Step $\Delta s$ | Gain on the checkerboard, $1 - 4\Delta s$ | Effect |
|---|---|---|
| 1/4 | 0 | removes it in one step |
| 2/5, the five-pixel average | −0.6 | stable, but flips its sign each step |
| 1/2 | −1 | the limit: it never decays |
| 3/5 | −1.4 | unstable: it grows every step |

The five-pixel average maps a checkerboard of ±1 to ∓0.6, which a Gaussian never does: its gain is positive at every frequency.

### The Laplacian of Gaussian and its stand-in

Differentiating $G_\sigma$ twice in $r$ and once in $\sigma$ gives two results that look different and are the same:

$$
\nabla^2 G = -\frac{1}{\pi\sigma^4}\left(1 - \frac{r^2}{2\sigma^2}\right)e^{-r^2/2\sigma^2}, \qquad \frac{\partial G}{\partial\sigma} = \sigma\,\nabla^2 G .
$$

The first is the Mexican hat, with zeros at $r = \sqrt2\,\sigma$; <!-- L02 --> the second is the heat equation in σ rather than in $s$, and a one-step finite difference of it is Lowe's $G(k\sigma) - G(\sigma) \approx (k-1)\sigma^2\nabla^2 G$. <!-- L22 --> At $k = 1.6$ and $\sigma = 1$ the two sides evaluate at the centre to −0.097 and −0.191, and the difference of Gaussians crosses zero at $r = 1.76$ rather than 1.41; those are the 0.51 and 24% in Figure 8, and they are the same at every σ.

### The normalised Laplacian on a disc

**Why the peak sits at σ = r/√2.** The response of $\sigma^2\nabla^2 G$ at the centre of a disc of radius $r$ and unit contrast is $\sigma^2$ times the integral of $\nabla^2 G$ over the disc. By the divergence theorem that integral is the flux of $\nabla G$ through the circle, $2\pi r\, G'(r)$, and $G'(r) = -\tfrac{r}{\sigma^2} G(r)$, so

$$
\sigma^2 \iint_{\text{disc}} \nabla^2 G = -\frac{r^2}{\sigma^2}\, e^{-r^2/2\sigma^2} .
$$

Differentiate the magnitude with respect to $s = \sigma^2$: $\tfrac{d}{ds}\left[\tfrac{r^2}{s}e^{-r^2/2s}\right] = 0$ gives $-\tfrac1s + \tfrac{r^2}{2s^2} = 0$, so $s = r^2/2$ and $\sigma = r/\sqrt2$. For $r = 3$ that is 2.12, and the response there, times the patch's contrast of 160, is −117.7. The bar result $\sigma = w/2$ comes from the same manipulation in one dimension, where the flux is $2G'(w/2)$.

The same flux, taken around the circle from a point off the centre, gives the off-centre responses in the 26-neighbour test; it has no closed form there, so they were integrated numerically.

The peak of the normalised response over σ is a *size*, not a strength; the strength at the peak still depends on the contrast, which is why blob detectors threshold on it afterwards. Lindeberg's general statement is that for a Gaussian blob the peak falls at the blob's own scale, <!-- L17 --> and the disc and bar are the two cases you can check on paper.

### The pyramid and the Poisson equation

$$
L_l = g_l - E(g_{l+1}), \qquad g_{l+1} = R(g_l), \qquad g_l = L_l + E(g_{l+1}) .
$$

The third equation is the first rearranged; reconstruction is exact because it is the same $E(g_{l+1})$ subtracted and added back. <!-- L12 --> And for editing, on the interior of Ω with $f$ pinned to the target on its boundary,

$$
\nabla^2 f = \nabla^2 g \quad\Longleftrightarrow\quad 4f_p - \sum_{q \sim p} f_q = 4g_p - \sum_{q \sim p} g_q ,
$$

one linear equation per interior pixel, five unknowns each, which is the five-point stencil written as a constraint rather than as a filter. <!-- L47 -->

## Implementation: the tooling map

None of the library calls below were executed for this post; the OpenCV entries follow the 4.13.0 documentation build and the 4.x source. <!-- L70 --> The first block is the by-hand arithmetic written as code, and it is the only code here that was run. The rest is the map from each job to the call that performs it, with the scale factor each call applies written down, because that is what the documentation leaves for the reader to find.

```python
"""The worked example, as code. Pure Python; this is what was actually run."""
P = [[40, 40, 40, 200, 200],
     [40, 40, 40, 200, 200],
     [40, 255, 40, 200, 200],
     [40, 40, 40, 200, 200],
     [40, 40, 40, 200, 200]]

def laplacian5(img, r, c):
    """Neighbour sum minus four times the centre: the four-neighbour stencil."""
    return img[r-1][c] + img[r+1][c] + img[r][c-1] + img[r][c+1] - 4 * img[r][c]

def average5(img, r, c):
    """The five-pixel average: moves the centre by exactly laplacian5 / 5."""
    return (img[r-1][c] + img[r+1][c] + img[r][c-1] + img[r][c+1] + img[r][c]) / 5

print(laplacian5(P, 2, 1), laplacian5(P, 2, 2), laplacian5(P, 2, 3))   # -860 375 -160
print(average5(P, 2, 2) - P[2][2], laplacian5(P, 2, 2) / 5)            # 75.0 75.0
```

Figure 16 is the map.

![The tooling map: six jobs, each with its call and an alternative — the five-point Laplacian ×1, OpenCV's ksize=3 ×4 with scale=0.25 to compare, the Laplacian of Gaussian with no σ², blob scale selection with σ² or 1/(k−1), the pyramid, and Poisson editing as a sparse solve.](https://minio.canery.in/media/fig-16-tooling-map-laplacian-by-hand.png)

*Figure 16 — The map from math to call site, with the ×4, the missing σ² and the 1/(k−1) written on the arrows. None of it was executed for this post.*

**The stencil.** `cv2.Laplacian(src, ddepth, ksize=1)` applies the five-point stencil. `ksize=3` applies `[2 0 2; 0 −8 0; 2 0 2]`, which is 4× the scale, so pass `scale=0.25` to compare the two on smooth data. `ksize=5` and `7` sum Sobel second derivatives with scale $2^{2\cdot\text{ksize}-4}$. <!-- L54 --> <!-- L59 --> <!-- L55 -->

Give `ddepth` as `cv2.CV_16S` or `cv2.CV_64F`: an 8-bit destination truncates every negative value, which is half of the output and the half the zero-crossing needs. <!-- L56 --> `scipy.ndimage.laplace` is the five-point stencil with `reflect` borders and no options to get anything else. <!-- L62 -->

**The Laplacian of Gaussian.** Either `cv2.GaussianBlur` followed by `cv2.Laplacian` — the pattern in OpenCV's own tutorial, which then calls `convertScaleAbs` and so discards the sign, making zero-crossing detection impossible on its output <!-- L58 --> — or `scipy.ndimage.gaussian_laplace(img, sigma)`, which sums the analytic second derivative of a sampled Gaussian along each axis, truncated at 4σ, with no σ² factor. <!-- L63 --> For σ below about a pixel, Lindeberg's analysis says the sampled derivative is the wrong discretisation and the discrete Gaussian followed by the plain stencil is the right one. <!-- L30 -->

**Blob scale selection.** `skimage.feature.blob_log(img, min_sigma, max_sigma, num_sigma, threshold)` returns rows of `(r, c, σ)`; multiply σ by √2 for the radius. <!-- L64 --> It builds `-gaussian_laplace(img, s) * s**2` per scale and runs a 3×3×3 maximum search over the cube. <!-- L65 --> `blob_dog` does the same with Gaussian differences scaled by `1/(sigma_ratio − 1)`, ratio 1.6 by default. <!-- L66 -->

**The pyramid.** `cv2.pyrDown` is REDUCE with the binomial kernel; `cv2.pyrUp(x, dstsize=...)` is EXPAND; the Laplacian level is `g − pyrUp(pyrDown(g), dstsize=g.shape[::-1])`, and `cv2.buildPyramid` produces the Gaussian levels in one call. <!-- L57 -->

**Poisson editing.** One five-point equation per interior pixel, assembled as a sparse linear system with the target's boundary values moved to the right-hand side, and handed to any sparse solver; the reference formulation is in the paper. <!-- L47 -->

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** writing the Laplacian into an 8-bit image. Half of the output is negative, and an unsigned destination stores it as zero — or, after `convertScaleAbs`, as its magnitude. Either way the sign is gone, and with it every zero-crossing. The symptom is an edge map that shows two parallel lines where there is one edge, or no edge at all where the crossing was. Use `CV_16S` or a float depth, and keep the sign until the last step. <!-- L56 -->

- **Comparing `ksize=1` with `ksize=3`.** They are different stencils at different scales, not two smoothings of one operator. Symptoms: magnitudes ×4, and an impulse whose spill moves from its four edge-neighbours to its four diagonal neighbours. <!-- L59 --> Pass `scale=0.25`, and expect agreement only on smooth data.
- **Detecting anything on the raw stencil.** On the patch the impulse scores −860 and the genuine edge 160. Every discrete Laplacian without smoothing is a defect detector first and an edge detector second; the fix is σ, and the cost is the reduction from 160 to 45.
- **Trusting every zero-crossing.** Between two nearby edges of the same sign there is always a third crossing, at the minimum of the gradient, that is not an edge. <!-- L37 --> Shrink σ: real edges strengthen, phantoms fade.
- **Searching over σ without σ².** The raw response falls as $1/\sigma^2$, so the smallest scale always wins and every blob is reported at `min_sigma`. `gaussian_laplace` does not normalise; `blob_log` does. <!-- L63 --> <!-- L65 -->
- **Reading a small kernel's nominal σ as its variance.** The parent's 3×3 Gaussian at σ = 0.8 has variance 0.478, not 0.64, so an unsharp mask that assumes 0.64 is 34% stronger than intended. <!-- L31 --> The cause is the three-tap cut, not the sampling. For kernels under about five taps, measure the variance of the weights you actually have.
- **Taking a box-like blur for a gentle one.** The five-pixel average moves a pixel four-fifths of the way to its neighbours' mean in one step, a fifth of the Laplacian. Its per-axis variance is 2/5, close to the explicit-step limit of 1/2, and it flips the sign of a checkerboard.
- **Expecting the five-point stencil to be isotropic.** At the top of the band it over-reads diagonal structure by 60.6% relative to axis-aligned structure. If the magnitude matters, either smooth away the top of the band or use the nine-point stencil. <!-- L51 -->
- **Fitting the scale parabola in the wrong coordinate.** A geometric ladder of σ is even in $\log \sigma$. On the disc of radius 3 the parabola in $\log\sigma$ gives 2.14 against the true 2.12; the same three points fitted in σ give 2.18.
- **Using the variance of the Laplacian on unsmoothed frames.** One hot pixel counts 29 times a real edge in that statistic. Smooth, or use a robust summary. <!-- L50 -->

Where the operator itself fails: at a corner, the linear-variation condition breaks and the zero-crossing is displaced from the true edge; <!-- L01 --> on a straight noisy edge, half of the Laplacian's output is noise from the along-edge term; <!-- L33 --> and across a tuning of σ it will always find some structure at some scale, so a threshold on the normalised response is not optional.

What to use instead: a directional second derivative or Canny's gradient chain for edge position at one scale, the Hessian determinant to reject edge-like blobs, and the Laplacian for what it does better than anything else — choosing the scale.

## Key takeaways

- The Laplacian is what Gaussian blur removes per unit of scale: $\partial L/\partial s = \tfrac12\nabla^2 L$, and on the grid the five-point stencil is that generator exactly.
- A blur moves each pixel by half its kernel's variance times the Laplacian. The five-pixel average has variance 2/5 and moves a pixel by exactly a fifth of the Laplacian; the parent's 3×3 Gaussian has 0.478, not σ² = 0.64, because three taps cut off its tails.
- The four-neighbour stencil is four times "neighbour average minus centre", so it scores a straight edge as ±160 with a zero between, and a single bad pixel as −860.
- There are at least five 3×3 Laplacians; they approximate ×1, ×2, ×3, ×4 and ×1 of $\nabla^2$, and OpenCV's `ksize=3` is the ×4 one.
- A zero of the second derivative is an edge only if it sits on a maximum of the gradient; the others are phantoms, and they fade as σ shrinks.
- Multiply the Laplacian response by σ² and the σ at its extremum is the size of the structure — $w/2$ for a bar, $r/\sqrt2$ for a disc — and a difference of Gaussians at constant ratio carries that σ² for free.

## Try it yourself

1. Apply the eight-neighbour stencil `[1 1 1; 1 −8 1; 1 1 1]` at (2,2) of the patch with the impulse present. What multiple of the five-point answer would you expect on smooth data, and why does the patch not give that multiple?

   **Answer.** The eight neighbours are (1,1) = 40, (1,2) = 40, (1,3) = 200, (2,1) = 255, (2,3) = 200, (3,1) = 40, (3,2) = 40 and (3,3) = 200, which sum to 1015. Subtract 8 × 40 = 320: the result is 695. On smooth data the eight-neighbour stencil is ×3 (five-point plus diagonal), and the clean patch gives 480 = 3 × 160 at this pixel. The impulse adds 215 once, not three times, because it sits in exactly one of the eight cells.

2. A round cell in a microscope image has a radius of about 5 pixels. At which σ should `blob_log` report it, and what does scikit-image's radius convention return?

   **Answer.** $\sigma = r/\sqrt2 = 5/1.414 = 3.54$. scikit-image multiplies the reported σ by √2 to give the radius, so it returns 5.0.

3. Your `cv2.Laplacian(img, cv2.CV_64F, ksize=3)` output has a mean absolute value of 48 on a region where `ksize=1` gives 12. Is that consistent, and what argument restores the match?

   **Answer.** Yes: 48/12 = 4, the scale factor of the `[2 0 2; 0 −8 0; 2 0 2]` kernel. `scale=0.25` restores the match on smooth regions; on impulses and diagonal edges the two will still differ, because they are different stencils.

4. Replace (2,2) of the patch with the impulse present by the average of itself and its four neighbours. How far does it move, and what does that tell you about the Laplacian there without computing the stencil?

   **Answer.** The five values are 40, 40, 255, 200 and the centre 40, which average to 115: a move of +75. The move is exactly a fifth of the Laplacian, so the stencil must return 5 × 75 = 375 — the value the worked example found.

## References

**Papers and books**

1. D. Marr and E. Hildreth. *Theory of edge detection.* Proc. R. Soc. Lond. B 207(1167):187–217, 1980. https://www.hms.harvard.edu/bss/neuro/bornlab/qmbc/beta/day4/marr-hildreth-edge-prsl1980.pdf (accessed 2026-09-14)
2. P. J. Burt and E. H. Adelson. *The Laplacian pyramid as a compact image code.* IEEE Trans. Commun. COM-31(4):532–540, 1983. https://persci.mit.edu/pub_pdfs/pyramid83.pdf (accessed 2026-09-14)
3. T. Lindeberg. *Feature detection with automatic scale selection.* Int. J. Comput. Vis. 30(2):79–116, 1998. https://people.kth.se/~tony/papers/cvap198.pdf (accessed 2026-09-14)
4. T. Lindeberg. *Scale selection.* In K. Ikeuchi (ed.), Computer Vision: A Reference Guide, Springer, 701–713, 2014. https://people.kth.se/~tony/papers/Lin14-ScSel-CompVisRefGuide.pdf (accessed 2026-09-14)
5. D. G. Lowe. *Distinctive image features from scale-invariant keypoints.* Int. J. Comput. Vis. 60(2):91–110, 2004. https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf (accessed 2026-09-14)
6. J. J. Koenderink. *The structure of images.* Biol. Cybern. 50(5):363–370, 1984. https://doi.org/10.1007/BF00336961 — cited through references 5 and 7.
7. T. Lindeberg. *Discrete approximations of Gaussian smoothing and Gaussian derivatives.* J. Math. Imaging Vis., 2024. https://arxiv.org/abs/2311.11317 (accessed 2026-09-14)
8. J. Canny. *A computational approach to edge detection.* IEEE Trans. Pattern Anal. Mach. Intell. 8(6):679–698, 1986. https://cecas.clemson.edu/~ahoover/ece431/refs/Canny.pdf (accessed 2026-09-14)
9. V. Torre and T. Poggio. *On edge detection.* IEEE Trans. Pattern Anal. Mach. Intell. 8(2):147–163, 1986. https://dspace.mit.edu/handle/1721.1/5636 (accessed 2026-09-14)
10. J. J. Clark. *Authenticating edges produced by zero-crossing algorithms.* IEEE Trans. Pattern Anal. Mach. Intell. 11(1):43–57, 1989. https://doi.org/10.1109/34.23112 (accessed 2026-09-14)
11. R. M. Haralick. *Digital step edges from zero crossing of second directional derivatives.* IEEE Trans. Pattern Anal. Mach. Intell. 6(1):58–68, 1984. https://www.haralick.org/journals/04767475.pdf (accessed 2026-09-14)
12. A. L. Yuille and T. Poggio. *Scaling theorems for zero crossings.* IEEE Trans. Pattern Anal. Mach. Intell. 8(1):15–25, 1986. https://doi.org/10.1109/TPAMI.1986.4767748 (accessed 2026-09-14)
13. K. Mikolajczyk and C. Schmid. *Scale & affine invariant interest point detectors.* Int. J. Comput. Vis. 60(1):63–86, 2004. https://www.robots.ox.ac.uk/~vgg/research/affine/det_eval_files/mikolajczyk_ijcv2004.pdf (accessed 2026-09-14)
14. P. Pérez, M. Gangnet and A. Blake. *Poisson image editing.* ACM Trans. Graph. 22(3):313–318, 2003. http://www.irisa.fr/vista/Papers/2003_siggraph_perez.pdf (accessed 2026-09-14)
15. J. L. Pech-Pacheco, G. Cristóbal, J. Chamorro-Martínez and J. Fernández-Valdivia. *Diatom autofocusing in brightfield microscopy: a comparative study.* Proc. ICPR 2000, vol. 3, 314–317. https://doi.org/10.1109/icpr.2000.903548 (accessed 2026-09-14)
16. S. Pertuz, D. Puig and M. A. Garcia. *Analysis of focus measure operators for shape-from-focus.* Pattern Recognit. 46(5):1415–1432, 2013. Used through the authors' summary page, https://sites.google.com/view/cvia/focus-measure (accessed 2026-09-14)
17. M. Patra and M. Karttunen. *Stencils with isotropic discretization error for differential operators.* Numer. Methods Partial Differ. Equ. 22(4):936–953, 2006. https://doi.org/10.1002/num.20129 (accessed 2026-09-14)
18. R. J. LeVeque. *Finite Difference Methods for Ordinary and Partial Differential Equations.* SIAM, 2007, ch. 3. https://faculty.washington.edu/rjl/fdmbook/ (accessed 2026-09-14)
19. R. C. Gonzalez and R. E. Woods. *Digital Image Processing*, 4th ed., Pearson, 2018, §3.6 and §4.9.
20. P. J. Burt and E. H. Adelson. *A multiresolution spline with application to image mosaics.* ACM Trans. Graph. 2(4):217–236, 1983. https://doi.org/10.1145/245.247 (accessed 2026-09-14)
21. S. Paris, S. W. Hasinoff and J. Kautz. *Local Laplacian filters: edge-aware image processing with a Laplacian pyramid.* ACM Trans. Graph. 30(4), 2011. https://doi.org/10.1145/2010324.1964963 (accessed 2026-09-14)

**Documentation and source**

22. OpenCV 4.13.0, Image Filtering module: `Laplacian`, `Sobel`, `getDerivKernels`, `pyrDown`, `pyrUp`, `buildPyramid`. https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html (accessed 2026-09-14)
23. OpenCV source, `modules/imgproc/src/deriv.cpp` at commit 2f779c5. https://github.com/opencv/opencv/blob/2f779c5c36b33dd48355ae841664e7df52a805b2/modules/imgproc/src/deriv.cpp (accessed 2026-09-14)
24. OpenCV 4.13.0, tutorial *Laplace Operator*. https://docs.opencv.org/4.x/d5/db5/tutorial_laplace_operator.html (accessed 2026-09-14)
25. SciPy 1.18.0, `scipy.ndimage.laplace` and `scipy.ndimage.gaussian_laplace`; source `scipy/ndimage/_filters.py` at commit 3f34207. https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_laplace.html (accessed 2026-09-14)
26. scikit-image 0.26.0, `skimage.feature.blob_log` and `blob_dog`; source `src/_skimage2/feature/blob.py` at commit 5d91fed. https://scikit-image.org/docs/stable/api/skimage.feature.html (accessed 2026-09-14)
