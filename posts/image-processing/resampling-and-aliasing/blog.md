---
title: "Resampling and Aliasing: Interpolation Kernels in Practice"
slug: resampling-and-aliasing
date: 2026-09-25
updated: 2026-09-25
summary: "Enlarging an image needs a good kernel; shrinking also needs a prefilter that widens with the scale. Nearest, bilinear, bicubic and Lanczos, worked by hand."
tags: [algorithms, image-processing, resampling, interpolation, aliasing, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: advanced
series: image-processing
series_position: 3
prerequisites: ["the sampling stage from Image Processing by Hand", "convolution as a weighted sum", "the Fourier transform of a box", "reading Python signatures"]
reading_minutes: 30
cover_image_url: "COVER"
cover_image_alt: "Row of five pixels under one new pixel of a shrink: a fixed-width kernel reads one of them, a kernel widened by 1/s reads all three"
canonical_url: "https://canery.in/blogs/resampling-and-aliasing"
---

> [!NOTE]
> **Insights** — Enlarging and shrinking an image are different problems that share one flag. Enlarging only has to fill in between samples, so the interpolation kernel — nearest, bilinear, bicubic, Lanczos — decides everything, as a trade between blocking, blur and ringing. Shrinking also has to *remove* the detail the coarser grid cannot hold, which means the kernel must get wider by the shrink factor. A fixed-width interpolator such as OpenCV's default `INTER_LINEAR` reads two pixels per output however far you shrink, and it aliases. Worked by hand on one five-pixel row: at 0.6× the default bilinear resize weights one input pixel three times as heavily as its neighbour, while area averaging weights all five exactly equally and keeps the row's mean at 147.

**Level:** advanced · **You need:** the sampling stage of [Image Processing by Hand](https://canery.in/blogs/image-processing-by-hand#stage-1--sample-the-grid-is-already-lossy), convolution as one weighted sum, the Fourier transform of a box, and enough Python to read a signature · **Time:** ~30 min

This is part 3 of *Image Processing by Hand*. It takes the one row of the shared 5×5 patch that holds both the impulse and the step, and it starts where the hub's sampling stage stopped. That stage showed the grid is already lossy and that a prefilter has to come before a resample. This part covers the other half: which kernel reconstructs the signal between the samples, and why the answer changes when you shrink instead of enlarge. Nyquist and spectral replication are not re-taught; the hub's Figure 5 is the picture to keep in mind.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Kernels in frequency](#what-does-each-kernel-do-to-the-spectrum) · [Bicubic is a family](#why-is-bicubic-not-one-kernel) · [The prefilter](#why-does-a-shrink-need-a-prefilter-and-an-enlarge-not) · [Cost](#what-does-the-choice-cost) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on one row of the shared patch; the arithmetic was cross-checked with plain Python and nothing else — no NumPy, OpenCV, Pillow, SciPy or scikit-image call was executed. What each library does comes from its documentation and from reading its source at a pinned commit. There are no timings and no measured curves. The figures that draw curves are evaluated from the kernels' closed-form definitions and say so in the caption.

## Why this matters

You build a thumbnail pipeline on `cv2.resize(img, None, fx=0.25, fy=0.25)`. Photos come out fine. Screenshots of spreadsheets come out with grey text broken into dotted fragments, and a striped shirt grows broad diagonal bands that were never in the photo. You switch to `INTER_CUBIC`, expecting a better kernel to fix it. It does not.

None of this is a bug. `resize` defaults to `INTER_LINEAR`, and OpenCV's own documentation recommends `INTER_AREA` for shrinking. <!-- L28 --> The two flags differ in something the word "interpolation" hides. At a quarter of the size, `INTER_LINEAR` reads the middle 2×2 pixels of every 4×4 block and ignores the other twelve. `INTER_CUBIC` reads all four columns of the block but weights the middle two at 0.59 and the outer two at −0.09. `INTER_AREA` reads all sixteen, equally. Only the last one is a shrink.

The mistake is common enough to have moved published numbers. A 2022 CVPR paper traced shifts in a standard generative-model score to the default resize in several libraries, which alias on downscale where Pillow's does not. <!-- L25 --> <!-- L26 -->

## The problem

Your array holds $`f[k]`$ at integer positions. A resize asks for values at positions that are not integers, and the samples say nothing about what lies between them. So every resize does two things, whether or not its signature admits it: it invents a continuous signal from the samples, and it samples that signal on a new grid.

The invented signal is a weighted sum of one shape — the **reconstruction kernel** $h$ — centred on every sample:

$$
\hat f(x) = \sum_k f[k]\, h(x - k)
$$

Each sample stamps a copy of $h$ scaled by its value, and the copies add up. The kernel is the whole decision. Shannon's answer is a sinc pulse on every sample: it is 1 at its own sample, 0 at every other, and its spectrum is flat inside the band and zero outside. <!-- L27 --> Nobody uses it on images. It decays too slowly to truncate cleanly, and no ideal low-pass filter exists as a device. <!-- L23 --> Every kernel in this post is a short stand-in for the sinc, and choosing one is choosing which way to fall short. A kernel with $h(0) = 1$ and $h = 0$ at every other integer is **interpolating**: an output that lands exactly on an input position returns that input's value.

**Where the new samples sit** is the second half of the problem. Call the scale factor $s$: output samples per input sample, so 0.6 shrinks and 1.7 enlarges. Most libraries treat a pixel as a unit cell with its sample at the centre, and put output $j$ at

$$
x_j = \frac{j + 0.5}{s} - 0.5
$$

in input-pixel coordinates. The half-pixel terms keep the first and last output cells flush with the first and last input cells. OpenCV's linear, cubic and Lanczos resizes compute exactly this. <!-- L33 --> Not every call does. OpenCV's `INTER_NEAREST` takes source index $`\lfloor j/s \rfloor`$ with no half-pixel offset, <!-- L31 --> and SciPy's `zoom` by default stretches the distance between the first and last pixel *centres*, so it treats five samples as a signal of length four. <!-- L42 --> Figure 1 puts the three conventions side by side for a shrink to 0.6×.

![Five input pixel cells with the sample points of a 0.6x shrink under half-pixel centres, OpenCV's floor index and a corner-aligned grid](FIG_01)

*Figure 1 — "Shrink to 0.6× with nearest-neighbour" is three different computations. Pixel centres put the samples at 1/3, 2 and 11/3 and read c0, c2 and c4. OpenCV's floor index reads c0, c1 and c3. A corner-aligned grid samples exactly at 0, 2 and 4. Only the second one ever sees the impulse at c1.*

The three grids disagree only by fractions of a pixel, and on this row that is the difference between keeping the brightest pixel and losing it. So the problem has three parts, and a library flag bundles all three: **which kernel** fills in, **where** it is sampled, and — the part this post is mostly about — **what is removed first** when the new grid is coarser than the old one. At $s < 1$ the new grid's Nyquist frequency is $s/2$ cycles per input pixel. Everything between $s/2$ and $1/2$ has to go before the samples are taken, or it folds into the output as a pattern that was never in the image.

## Worked example

The row is r2 of the shared patch, the only row with both features:

```text
      c0   c1   c2   c3   c4
      40  255   40  200  200       mean 147
```

An impulse at c1, a step between c2 and c3. We shrink it to 0.6× (three outputs) and enlarge it to 1.7× (eight outputs) with four kernels: **nearest** (the box, one tap), **linear** (the triangle, two taps), **Keys' cubic** with $a = -1/2$ (four taps), and **Lanczos-3** (six taps, a sinc windowed by a sinc three times wider, normalised so its taps sum to 1). Each kernel is written out in [the math](#the-math). A **tap** is one input sample a kernel reads for one output. Taps that fall off the end of the row reuse the edge pixel, which is what OpenCV does. <!-- L34 -->

### Shrinking to 0.6×: three outputs

The outputs sit at $x = 1/3$, $2$ and $11/3$.

**Nearest.** Rounding the positions picks c0, c2, c4: output **40, 40, 200**. The impulse is gone. OpenCV's floor index picks c0, c1, c3 instead: **40, 255, 200**, with the impulse at full strength. Same kernel, same factor, and the brightest pixel is either all there or entirely absent, depending on where the grid happened to fall.

**Linear.** At $x = 1/3$ the two nearest samples are c0 and c1, weighted by closeness: $\tfrac{2}{3}\cdot 40 + \tfrac{1}{3}\cdot 255 = 26.67 + 85 = 111.67$. At $x = 2$ the output lands exactly on c2 and returns 40. At $x = 11/3$ both taps are 200. Output **111.67, 40, 200**.

**Keys' cubic.** At $x = 1/3$ the four taps c−1, c0, c1, c2 sit at distances 4/3, 1/3, 2/3 and 5/3, where the kernel is worth **−2/27, 7/9, 1/3, −1/27**. The weights sum to 1, and c−1 is the replicated c0. The output is $40\cdot(-\tfrac{2}{27} + \tfrac{7}{9} - \tfrac{1}{27}) + 255\cdot\tfrac{1}{3} = 111.67$ — the same as linear, because the cubic's weight at distance 2/3 happens to equal the triangle's. At $x = 11/3$ the same weights run the other way, and the −1/27 lands on the dark c2: $-1.48 + 66.67 + 155.56 - 14.81 = 205.93$. The negative lobe reaches back across the step and pushes the bright side *above* 200. Output **111.67, 40, 205.93**.

**Lanczos-3** reads six taps and gives **124.25, 40, 215.70**.

**Area averaging** is the one that is not an interpolator. Each output owns the stretch of input it covers — 0 to 5/3, 5/3 to 10/3, and 10/3 to 5 — and averages it by overlap. The first output gets all of c0 and two-thirds of c1: $(40 + \tfrac{2}{3}\cdot 255)\cdot\tfrac{3}{5} = 126$. The second gets a third of c1, all of c2 and a third of c3: $(85 + 40 + 66.67)\cdot\tfrac{3}{5} = 115$. The third is **200**. Output **126, 115, 200**.

Figure 2 draws the four interpolators' windows under the row.

![Row 40 255 40 200 200 with nearest, linear, Keys cubic and Lanczos-3 kernels centred at 0.33, 2 and 3.67, taps and output values marked](FIG_02)

*Figure 2 — At 0.6× each kernel reads a window around its sample point, and the windows leave gaps. The middle output sits exactly on c2, so every interpolating kernel returns 40 there and the 255 next door counts for nothing. Kernel shapes are evaluated from their definitions.*

Put the results side by side:

| Method | Outputs | Mean |
|---|---|---|
| nearest, pixel centres | 40, 40, 200 | 93.3 |
| nearest, OpenCV floor index | 40, 255, 200 | 165.0 |
| linear | 111.67, 40, 200 | 117.2 |
| Keys, $a = -1/2$ | 111.67, 40, 205.93 | 119.2 |
| Lanczos-3 | 124.25, 40, 215.70 | 126.6 |
| area averaging | 126, 115, 200 | **147.0** |

The input's mean is 147. Only area averaging reproduces it. The interpolators miss by 18 to 54 grey levels, and the two nearest-neighbour conventions miss in opposite directions. [The prefilter section](#why-does-a-shrink-need-a-prefilter-and-an-enlarge-not) shows this is not a coincidence of this row.

### Enlarging to 1.7×: eight outputs

The outputs sit at $x_j = (20j - 7)/34$: −0.206, 0.382, 0.971, 1.559, 2.147, 2.735, 3.324, 3.912. The spacing is 1/1.7 = 0.588 input pixels, closer than the samples themselves, so every input sample is within reach of several outputs and nothing falls in a gap.

| Method | j0 | j1 | j2 | j3 | j4 | j5 | j6 | j7 |
|---|---|---|---|---|---|---|---|---|
| nearest | 40 | 40 | 255 | 40 | 40 | 200 | 200 | 200 |
| linear | 40.0 | 122.2 | 248.7 | 134.9 | 63.5 | 157.6 | 200.0 | 200.0 |
| Keys, $a = -1/2$ | **26.0** | 125.9 | 254.5 | 132.4 | 44.9 | 159.4 | **211.8** | 200.6 |
| Lanczos-3 | **14.1** | 139.3 | **255.6** | 135.6 | 37.1 | 148.3 | **225.0** | 203.4 |

Figure 3 shows where those numbers come from: each is a point on one continuous curve per kernel.

![Continuous reconstructions of the row by four kernels at 1.7x with eight sample dots; cubic and Lanczos dip below 40 and rise past 200](FIG_03)

*Figure 3 — Enlarging is reconstruction and nothing more; the eight samples are read off one curve per kernel. Nearest makes blocks of uneven width, linear never leaves the input's range, and the cubic and Lanczos curves dip below the flat 40 and rise past 200 and 255. Curves are evaluated from the kernels' closed forms.*

Every row of the table is defensible, and each fails differently. Nearest repeats c0 and c2 twice and c1 once, because 1.7 is not an integer. In two dimensions those uneven blocks are the staircase along a diagonal edge. Linear stays between 40 and 255, since every output is a weighted average with positive weights, but the impulse spreads into a broad hill from 122 to 249 to 135. Keys and Lanczos keep the impulse sharp — 254.5 and 255.6 at j2 — and pay for it in ringing. Keys dips to 26.0 beside the impulse, where the image is a flat 40, and overshoots the step to 211.8. Lanczos-3 dips to 14.1, overshoots to 225.0, and at j2 passes 255, which an 8-bit output clips.

The step on its own does the same thing. On the clean row `40 40 40 200 200`, Keys gives 29.0 just before the step and 211.8 just after it, and Lanczos-3 gives 21.4 and 218.3, with a smaller ripple of 42.6 and 40.9 further out.

The two resizes fail differently. At 1.7× the kernels differ in how they *shape* a signal the new grid can hold. At 0.6× they differ in which input pixels they *hear at all*.

<details>
<summary>Every tap and every output</summary>

`c0*` or `c4*` marks a tap that fell off the row and reads the edge pixel instead. Weights are rounded to four places; outputs are computed from the unrounded weights.

**Linear, 0.6×**

| j | x | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | 0.333 | c0: 0.6667, c1: 0.3333 | 111.67 |
| 1 | 2.000 | c2: 1.0000 | 40.00 |
| 2 | 3.667 | c3: 0.3333, c4: 0.6667 | 200.00 |

**Keys $a = -1/2$, 0.6×**

| j | x | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | 0.333 | c0*: −0.0741, c0: 0.7778, c1: 0.3333, c2: −0.0370 | 111.67 |
| 1 | 2.000 | c2: 1.0000 | 40.00 |
| 2 | 3.667 | c2: −0.0370, c3: 0.3333, c4: 0.7778, c4*: −0.0741 | 205.93 |

**Lanczos-3 (normalised), 0.6×**

| j | x | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | 0.333 | c0*: 0.0312, c0*: −0.1465, c0: 0.8139, c1: 0.3824, c2: −0.0937, c3: 0.0127 | 124.25 |
| 1 | 2.000 | c2: 1.0000 | 40.00 |
| 2 | 3.667 | c1: 0.0127, c2: −0.0937, c3: 0.3824, c4: 0.8139, c4*: −0.1465, c4*: 0.0312 | 215.70 |

**Area averaging, 0.6×**

| j | footprint | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | 0 to 1.667 | c0: 0.6000, c1: 0.4000 | 126.00 |
| 1 | 1.667 to 3.333 | c1: 0.2000, c2: 0.6000, c3: 0.2000 | 115.00 |
| 2 | 3.333 to 5 | c3: 0.4000, c4: 0.6000 | 200.00 |

**Stretched linear, 0.6×** (used in [the prefilter section](#why-does-a-shrink-need-a-prefilter-and-an-enlarge-not))

| j | x | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | 0.333 | c0: 0.5714, c1: 0.4286 | 132.14 |
| 1 | 2.000 | c1: 0.2222, c2: 0.5556, c3: 0.2222 | 123.33 |
| 2 | 3.667 | c3: 0.4286, c4: 0.5714 | 200.00 |

**Linear, 1.7×**

| j | x | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | −0.206 | c0*: 0.2059, c0: 0.7941 | 40.00 |
| 1 | 0.382 | c0: 0.6176, c1: 0.3824 | 122.21 |
| 2 | 0.971 | c0: 0.0294, c1: 0.9706 | 248.68 |
| 3 | 1.559 | c1: 0.4412, c2: 0.5588 | 134.85 |
| 4 | 2.147 | c2: 0.8529, c3: 0.1471 | 63.53 |
| 5 | 2.735 | c2: 0.2647, c3: 0.7353 | 157.65 |
| 6 | 3.324 | c3: 0.6765, c4: 0.3235 | 200.00 |
| 7 | 3.912 | c3: 0.0882, c4: 0.9118 | 200.00 |

**Keys $a = -1/2$, 1.7×**

| j | x | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | −0.206 | c0*: −0.0168, c0*: 0.1746, c0: 0.9071, c1: −0.0649 | 26.04 |
| 1 | 0.382 | c0*: −0.0729, c0: 0.7184, c1: 0.3997, c2: −0.0451 | 125.94 |
| 2 | 0.971 | c0*: −0.0004, c0: 0.0164, c1: 0.9979, c2: −0.0139 | 254.54 |
| 3 | 1.559 | c0: −0.0544, c1: 0.4811, c2: 0.6422, c3: −0.0689 | 132.41 |
| 4 | 2.147 | c1: −0.0535, c2: 0.9507, c3: 0.1120, c4: −0.0092 | 44.95 |
| 5 | 2.735 | c1: −0.0258, c2: 0.2447, c3: 0.8526, c4: −0.0716 | 159.44 |
| 6 | 3.324 | c2: −0.0740, c3: 0.7891, c4: 0.3203, c4*: −0.0354 | 211.84 |
| 7 | 3.912 | c2: −0.0035, c3: 0.0587, c4: 0.9816, c4*: −0.0367 | 200.57 |

**Lanczos-3 (normalised), 1.7×**

| j | x | taps (pixel: weight) | output |
|---|---|---|---|
| 0 | −0.206 | c0*: 0.0050, c0*: −0.0544, c0*: 0.2151, c0: 0.9266, c1: −0.1203, c2: 0.0279 | 14.13 |
| 1 | 0.382 | c0*: 0.0302, c0*: −0.1479, c0: 0.7595, c1: 0.4500, c2: −0.1080, c3: 0.0162 | 139.34 |
| 2 | 0.971 | c0*: 0.0001, c0*: −0.0064, c0: 0.0253, c1: 0.9985, c2: −0.0233, c3: 0.0058 | 255.60 |
| 3 | 1.559 | c0*: 0.0205, c0: −0.1234, c1: 0.5314, c2: 0.6881, c3: −0.1444, c4: 0.0278 | 135.61 |
| 4 | 2.147 | c0: 0.0229, c1: −0.0961, c2: 0.9622, c3: 0.1453, c4: −0.0368, c4*: 0.0026 | 37.09 |
| 5 | 2.735 | c0: 0.0082, c1: −0.0726, c2: 0.2902, c3: 0.8802, c4: −0.1366, c4*: 0.0306 | 148.26 |
| 6 | 3.324 | c1: 0.0313, c2: −0.1456, c3: 0.8241, c4: 0.3690, c4*: −0.0908, c4*: 0.0120 | 225.02 |
| 7 | 3.912 | c1: 0.0009, c2: −0.0207, c3: 0.0817, c4: 0.9863, c4*: −0.0638, c4*: 0.0156 | 203.36 |

</details>

## Intuition

A resize is three steps even when the code shows one: **reconstruct** a continuous signal with the kernel, **prefilter** it to remove what the new grid cannot hold, then **sample** it at the new positions. Heckbert's 1989 thesis draws resampling as exactly this pipeline, with a warp between the first two steps, and folds the stages into one resampling filter that gives the weight of every input sample in every output. <!-- L18 --> Which stage matters depends on which Nyquist frequency is lower, the old grid's or the new one's. Figure 4 shows both cases for the row.

![Two pipelines of reconstruct, prefilter, sample: at 1.7x the prefilter is skipped, at 0.6x it cuts the band from 0.5 to 0.3 cycles](FIG_04)

*Figure 4 — The prefilter's job depends on which Nyquist frequency is lower. Enlarging to 1.7× raises it to 0.85 cycles per input pixel, so everything the kernel passes fits. Shrinking to 0.6× lowers it to 0.30, so the band from 0.30 to 0.50 must go before the samples are taken.*

**Enlarging.** The new grid is finer, so everything in the reconstructed signal below 0.5 cycles per pixel fits under its Nyquist of 0.85. There is nothing for a prefilter to do. The only question is how well the kernel reconstructs. Heckbert's limiting case says the same: when magnifying, the resampling filter is dominated by the reconstruction filter, whose support of one to four pixels does not depend on the scale. <!-- L19 -->

**Shrinking.** The new grid is coarser, with a Nyquist of 0.3. Anything in the band from 0.3 to 0.5 cycles per pixel cannot be represented, and if it is still there at sample time it folds down into the band the grid *can* hold. When shrinking, Heckbert's resampling filter is dominated by the prefilter, whose support in the source grows as the reciprocal of the scale factor, without bound. <!-- L20 -->

Mitchell and Netravali give the two failures separate names. **Prealiasing** comes from undersampling or a missing prefilter. **Postaliasing** comes from a poor reconstruction kernel, and it happens even when the spectral copies do not overlap at all. <!-- L10 --> An enlarge can only postalias; the jaggies in Figure 3's nearest-neighbour row are postaliasing. A shrink without a prefilter prealiases, and the missing mean in the worked example's table is prealiasing.

An analogy: enlarging is paraphrasing a report at greater length, and shrinking is summarising it. The paraphrase cannot add facts, only style — smooth or crisp, which is the kernel. The summary has to decide what to drop, and a fixed-width kernel summarises each chapter by reading one sentence of it. The analogy breaks at what happens to the dropped material. A summary that skips a sentence simply loses it. A resize that skips detail does not lose it: the detail folds into a coarser pattern that was never in the image. That pattern is the moiré on the striped shirt.

## What does each kernel do to the spectrum?

The hub post settled that a kernel's behaviour is read from its transfer function, not from its name. Figure 5 shows the four kernels as shapes, beside the sinc they approximate.

![Box, triangle, Keys cubic and Lanczos-3 kernels drawn over the sinc, with supports of 1, 2, 4 and 6 taps and negative lobes shaded](FIG_05)

*Figure 5 — Four kernels and the sinc they approximate. Width buys closeness to the sinc, and from four taps on, closeness brings negative lobes. Evaluated from the kernels' definitions.*

Keys framed interpolation in frequency: the reconstructed signal's spectrum is the samples' spectrum times the kernel's transform. Any shortfall inside the band blurs, and any response outside it lets spectral copies through. <!-- L09 --> Mitchell and Netravali put it as two jobs: remove the copies, and pass the base band unchanged. Failing the second job is blur. <!-- L11 --> Figure 6 scores each kernel on both jobs.

![Transfer functions of box, triangle, Keys and Lanczos-3 against the ideal box, with Nyquist at 0.5 and the 0.6x Nyquist at 0.3 marked](FIG_06)

*Figure 6 — Below 0.5 cycles per pixel a kernel should pass everything, and above it nothing. Linear loses the most inside the band, nearest lets the most through outside it, and Lanczos-3 comes closest on both counts. Evaluated from the definitions.*

Read two numbers per kernel off the curves. **At 0.25 cycles per pixel**, half the Nyquist frequency, the ideal passes 1. Nearest passes 0.900, linear 0.811, Keys 0.939, and Lanczos-3 1.008 — a slight boost, which reads as sharpening. **At 0.75**, in the first copy's territory, the ideal passes 0. Nearest passes 0.300, linear 0.090, Keys 0.063, and Lanczos-3 −0.009. Nearest's 0.300 is the blocky staircase. Linear's 0.811 is the soft hill around the impulse in Figure 3.

All four kernels satisfy one condition exactly (Lanczos-3 once its taps are normalised): their copies, shifted to every integer, sum to 1. Mitchell and Netravali show why that matters. Without it the reconstruction of a flat image ripples at the sampling rate, the ripple is an alias of the image's mean, and the condition is the same as a transfer function that is zero at every nonzero multiple of the sampling rate. <!-- L13 --> That condition is why every row of every table above sums to 1. Lanczos-3's raw taps sum to 0.994 at a half-pixel offset, which is why both libraries divide by the sum. <!-- L30 --> <!-- L40 -->

**Ringing** is the price of the flat band. Keys and Lanczos-3 are the only kernels here with negative lobes, and negative lobes are where ringing comes from. Near an edge the output is pushed outside the input's range and then clamped. <!-- L12 --> The count of lobes matters as well as their depth. Keys has one side lobe on each side, negative; Lanczos-3 has two, one negative and one positive. One ringing lobe can read as sharpness, while several transients always degrade the image — a result Mitchell and Netravali cite from Brown's 1969 television study. <!-- L16 --> That is the 42.6 and 40.9 ripple ahead of Lanczos-3's dip on the clean row.

The same curves give the first hint about shrinking. At 0.6× the new Nyquist is 0.3, so a pattern at 0.4 cycles per pixel — a period of 2.5 pixels — should be removed. Unstretched, the kernels pass it at 0.757 (nearest), 0.573 (linear), 0.716 (Keys) and 0.821 (Lanczos-3). It then folds to 0.2 cycles per pixel, a stripe with a five-pixel period that was never in the image. Among the three smooth kernels, **the better interpolator is the worse downscaler**, because a flatter band up to 0.5 is exactly what lets more of 0.3–0.5 through.

## Why is bicubic not one kernel?

Keys' kernel is a symmetric piecewise cubic on $(-2, 2)$ with one free parameter $a$. It is 1 at 0 and 0 at every other integer, so it passes through the samples and reads four of them. <!-- L01 --> Every "bicubic" you have used is this kernel with some value of $a$, applied along rows and then along columns. The values in circulation have a history:

- **$a = -1$** is the original, Rifman and Bernstein's. It is the value that makes the kernel's slope match the sinc's at $x = 1$. <!-- L05 -->
- **$a = -1/2$** is Keys' 1981 result. It is the only value that makes the error fall as the cube of the sample spacing; every other value gives at most first order. <!-- L02 --> Park and Schowengerdt reached the same value from the frequency domain, as the best low-frequency match to the sinc, and Catmull and Rom's 1974 spline turns out to be the same kernel. <!-- L07 -->
- **$a = -3/4$** is the value that makes the kernel's second derivative continuous at $x = 1$, one of the criteria Simon proposed in 1975. <!-- L06 -->

"Third-order accurate" has a plain meaning. Halve the spacing between samples and the interpolation error falls by a factor of eight, where linear's falls by four and nearest's by two. <!-- L03 --> Equivalently, Keys' cubic reproduces any quadratic exactly; linear reproduces at most a straight line, and nearest only a constant. <!-- L04 --> Thévenaz, Blu and Unser call this the **approximation order**: a kernel of order $L$ has error proportional to the spacing to the power $L$ and reproduces every polynomial of degree $L - 1$, and order 1 is the sum-to-one condition from the previous section. <!-- L21 -->

The two libraries you are most likely to call disagree. OpenCV's `INTER_CUBIC` hard-codes $a = -0.75$. <!-- L32 --> Pillow's `BICUBIC` uses $a = -0.5$. <!-- L39 --> Swap one value for the other on the 1.7× row, holding everything else fixed, and j0 moves from 26.0 to 19.1 and j6 from 211.8 to 217.8. The overshoot on a step, worked out in [the math](#the-math), is exactly $-4a/27$ of the step height: **2/27 = 7.4%** for Pillow and Keys, and **1/9 = 11.1%** for OpenCV.

Mitchell and Netravali widened the family to two parameters, $(B, C)$. The cubic B-spline is $(1, 0)$, the cardinal cubics are $(0, C)$, and Catmull–Rom is $(0, 1/2)$. <!-- L14 --> Keys' $a$ is simply $(B, C) = (0, -a)$, which follows by expanding both formulas. Figure 7 places every named cubic on that plane.

![Plane of cubic parameters B and C with the B-spline, Mitchell, Catmull-Rom, OpenCV and Rifman kernels marked with overshoot and blur values](FIG_07)

*Figure 7 — Every library's "bicubic" is one point on Mitchell and Netravali's plane. The B = 0 axis passes through the samples. OpenCV and Pillow both sit on it, at C = 3/4 and C = 1/2, and overshoot an edge by 11.1% and 7.4%. Values are computed from the family's formula.*

Moving off the $B = 0$ axis trades ringing for blur and gives up interpolation. The kernel stops being 1 at 0 — it is 0.889 for Mitchell's $(1/3, 1/3)$ and 2/3 for the B-spline — so an output that lands on an input sample no longer returns it. Mitchell and Netravali recommend $(1/3, 1/3)$ after a subjective test with nine expert observers and more than 500 judgements, and they say plainly that other observers may prefer more or less ringing. <!-- L15 --> Its overshoot is 3.6%, and its gain at 0.25 cycles per pixel is 0.845, between linear and Keys.

The B-spline is not a poor choice everywhere. Used with its own **coefficient prefilter** — a digital filter that turns samples into spline coefficients before the kernel is applied — it reaches order 4 at the same four-tap support. Recursive filtering makes that step cheap, and Thévenaz, Blu and Unser judge Keys' speed gain not worth the quality it gives up. <!-- L22 --> SciPy's `zoom` defaults to exactly that route, and its parameter named `prefilter` means this coefficient step, not anti-aliasing. <!-- L42 --> Designing a kernel for a criterion, rather than choosing one, is the subject of Part 4, *Kernel Design: Separability, Borders, and Optimised Derivative Filters*.

## Why does a shrink need a prefilter and an enlarge not?

Every resize of a row is a matrix. Write $W_{ji}$ for the weight of input $i$ in output $j$; each output is one row of $W$ times the input row. Figure 8 shows four of the 0.6× matrices, with their sums in the margins.

![Four 3-by-5 resampling matrices at 0.6x with row sums of 1 and column sums below; only the area matrix has every column equal to 0.6](FIG_08)

*Figure 8 — A resize is a matrix. Every row sums to 1, so a flat row stays flat. The column sums are the total weight each input pixel gets: nearest gives c1 none, linear gives c2 three times what it gives c1, and only area averaging gives all five the same 0.6.*

**Rows** sum to 1 in all four, which is the sum-to-one condition: a flat row stays flat. **Columns** are the new information. A column sum is the total weight one input pixel gets across every output:

| Method | c0 | c1 | c2 | c3 | c4 |
|---|---|---|---|---|---|
| nearest, pixel centres | 1 | **0** | 1 | 0 | 1 |
| linear | 0.667 | **0.333** | 1 | 0.333 | 0.667 |
| Keys, $a = -1/2$ | 0.704 | **0.333** | 0.926 | 0.333 | 0.704 |
| Lanczos-3 | 0.699 | **0.395** | 0.813 | 0.395 | 0.699 |
| area averaging | 0.6 | **0.6** | 0.6 | 0.6 | 0.6 |

The output's mean is the average of the inputs weighted by their column sums. If every column sums to the same value — necessarily $s$, here 0.6 — the output's mean equals the input's for *every* input. That is why only area averaging returned 147. When the column sums ripple, the pattern of the ripple is an input pattern that aliases straight onto the output's mean. Linear's ripple, high on c0, c2 and c4 and low on c1 and c3, is a stripe at the new grid's spacing, and any real stripe near that frequency brightens or darkens the whole output. The column sums measure aliasing at one frequency, zero. It is the frequency that matters most for brightness, and the only one you can check with a pencil.

The column sums also answer the translation test. Move the impulse from c1 to c2 and its total contribution changes from 0 to 1 under centred nearest, and from 1/3 to 1 under linear. Under area averaging it stays at 0.6. Output that depends on *where* detail sits relative to the new grid, rather than on the detail itself, is what aliasing looks like in space.

**Why the columns ripple.** An unstretched kernel at $s = 0.6$ is centred on outputs 5/3 of a pixel apart, but it is only as wide as its own few taps. Its copies do not overlap enough to add to a constant along the input axis, so some inputs fall under a peak and some in a gap. The fix is to stretch the kernel by $1/s$, so its copies overlap exactly as they did at unit spacing. Figure 9 shows the triangle before and after.

![Triangle kernel at unit width and stretched by 1/0.6: its taps at x = 2, and its transfer function's cutoff moving from 0.5 to 0.3](FIG_09)

*Figure 9 — Widening the kernel by 1/s narrows its passband by s. At x = 2 the stretched triangle reads c1, c2 and c3 instead of c2 alone, and its cutoff moves from the old Nyquist frequency to the new one. Evaluated from the definitions.*

In space, the stretched triangle at $x = 2$ reads c1, c2 and c3 with weights 0.222, 0.556 and 0.222, and returns 123.33 where the plain triangle returned 40. In frequency, stretching a kernel by $1/s$ compresses its transfer function by $s$, so the cutoff that sat at the old Nyquist of 0.5 now sits at the new one, 0.3. The 0.4-cycle stripe that linear passed at 0.573 now passes at 0.171. **That is the prefilter**, built into the kernel rather than applied as a separate blur.

Area averaging is the box stretched this way, with the pixels treated as cells rather than points. Its footprints tile the input exactly, which is why its sums come out exact. Unser shows that a box is enough. Sampling without any prefilter is by far the worst scheme, since energy above Nyquist counts against you twice, once as missing and once folded back, while a simple box prefilter comes close to the optimal one. <!-- L24 --> Pillow stretches every one of its kernels this way when shrinking and drops the taps that fall off the image. <!-- L40 --> That gives **132.14, 123.33, 200** for the stretched triangle and column sums between 0.556 and 0.651. That is not exactly 0.6, because on a five-pixel row every pixel is near an edge, but it is a far cry from linear's range of 0.333 to 1. The 2022 CVPR paper states the requirement directly: the prefilter's width must scale with the downsampling factor, and the default resizes that use a fixed width alias like naive subsampling. <!-- L25 -->

**Why an enlarge does not need it.** At $s > 1$ the kernel's copies are *closer* than a pixel, so they already overlap, and nothing in the reconstruction lies above the new Nyquist except what the kernel itself leaked. Stretching by $1/s$ would *narrow* the kernel. So Pillow caps the stretch at 1 — it takes the larger of the in/out ratio and 1 — and an enlarge is plain interpolation. <!-- L40 -->

One OpenCV detail explains a folk rule. At exactly 0.5×, the half-pixel positions fall midway between two pixels, so bilinear reads each input once with weight ½. That is a width-2 box, which is area averaging, and OpenCV routes an exact 2× shrink through its area code. <!-- L36 --> Halving with the default flag is therefore safe. At 0.6× the same flag weights c2 three times as heavily as c1, and at 0.25× it reads two pixels of every four. Repeated halving — with `pyrDown`, which blurs with a 5×5 binomial kernel and then drops every other row and column, <!-- L37 --> or with `INTER_LINEAR` at 0.5 — is a legitimate prefilter chain.

## What does the choice cost?

An unstretched kernel reads a fixed number of taps per output along each axis: 1 for nearest, 2 for linear, 4 for Keys, 6 for Lanczos-3, and 8 for OpenCV's Lanczos variant. <!-- L30 --> Every kernel here is separable, so the 2-D resize is two 1-D passes and costs a number of multiplications proportional to the taps, not their square. <!-- L17 --> A 4×4 bicubic neighbourhood is two passes of 4, not 16.

Stretching changes the arithmetic. A stretched kernel reads $2\,r/s$ taps per output, where $r$ is its half-width:

| $s$ | linear | Keys | Lanczos-3 |
|---|---|---|---|
| ≥ 1 | 2 | 4 | 6 |
| 0.6 | 3.3 | 6.7 | 10 |
| 0.25 | 8 | 16 | 24 |
| 0.1 | 20 | 40 | 60 |

The output also shrinks by $s$, so the total work of a stretched pass is outputs × taps $= s n \times 2r/s = 2rn$. That is proportional to the *input* size, whatever the factor. An unstretched shrink costs in proportion to the output, which is why it looks free and why it is wrong. At 0.1× the honest resize does ten times the work of the default.

Two standard ways cut that cost without giving up the prefilter. A **pyramid** halves repeatedly with a small fixed kernel, then finishes with one short resample. Pillow's `reducing_gap` does the same thing internally: it reduces by an integer factor first, then resamples, and its documentation says that at 3.0 or above the result is indistinguishable from the full resample in most cases. <!-- L38 -->

## The math

| Symbol | Meaning | Units |
|---|---|---|
| $`f[k]`$ | input sample $k$ | grey level |
| $h$ | reconstruction kernel | — |
| $s$ | scale factor, outputs per input | — |
| $`x_j`$ | position of output $j$ on the input axis | input pixels |
| $`W_{ji}`$ | weight of input $i$ in output $j$ | — |
| $`c_i`$ | column sum, $`\sum_j W_{ji}`$ | — |
| $`H(\nu)`$ | transfer function of $h$ | gain at $\nu$ cycles per pixel |

**Resampling.** Output $j$ evaluates the reconstruction at its position:

$$
g[j] = \sum_k f[k]\, h(x_j - k), \qquad x_j = \frac{j + \tfrac12}{s} - \tfrac12 \tag{1}
$$

So $`W_{ji} = h(x_j - i)`$, one kernel evaluation per tap. For $s = 0.6$ and $j = 0$ this is $`h(1/3 - i)`$, which for the triangle gives 2/3 on c0 and 1/3 on c1.

**Keys' kernel.** With parameter $a$:

$$
h(x) = \begin{cases} (a+2)|x|^3 - (a+3)|x|^2 + 1 & 0 \le |x| < 1 \\ a|x|^3 - 5a|x|^2 + 8a|x| - 4a & 1 \le |x| < 2 \\ 0 & 2 \le |x| \end{cases} \tag{2}
$$

It is 1 at 0 and 0 at ±1 and ±2 for every $a$, so it interpolates for every $a$. At $a = -1/2$ and the distances 1/3, 2/3, 4/3 and 5/3 it gives 7/9, 1/3, −2/27 and −1/27 — the worked example's weights, which sum to 1.

<details>
<summary>Why only a = −1/2 is third-order, and where −4a/27 comes from</summary>

**Order.** Expand the four samples around the left one in a Taylor series in the spacing $\delta$ and substitute them into the kernel sum. The difference between the interpolant and the function comes out as $(2a + 1)$ times a combination of $\delta f'$ and $\delta^2 f''$, plus terms of order $\delta^3$. Only $a = -1/2$ removes the first part, which is Keys' derivation; any other $a$ leaves an error proportional to $\delta$. <!-- L02 -->

**Overshoot.** Take a unit step: samples $k \ge 0$ are 1, samples $k < 0$ are 0. At a third of a pixel past the first bright sample the reconstruction is $h(1/3) + h(2/3) + h(5/3)$. From equation (2), $h(1/3) = (20 - 2a)/27$, $h(2/3) = (7 - 4a)/27$ and $h(5/3) = 2a/27$, which sum to $1 - 4a/27$. For $a = -1/2$ that is $29/27$, an overshoot of $2/27$; the maximum over all positions sits exactly there. By symmetry the undershoot on the dark side is the same size.

**Continuity at $|x| = 1$.** The second derivative is $4a + 6$ from the inside and $-4a$ from the outside. They match when $a = -3/4$. <!-- L06 -->

</details>

**Stretching.** The prefiltering kernel for a shrink by $s$ is the kernel widened by $1/s$ and scaled to keep its area:

$$
h_s(x) = s\, h(s x), \qquad H_s(\nu) = H(\nu / s) \tag{3}
$$

Widening by $1/s$ compresses the transfer function by $s$, so a kernel whose cutoff was the old Nyquist of 1/2 cuts off at $s/2$, the new one. For the triangle at $s = 0.6$, with $`\operatorname{sinc}\nu = \sin(\pi\nu)/(\pi\nu)`$, $H(\nu) = \operatorname{sinc}^2\nu$ becomes $\operatorname{sinc}^2(\nu/0.6)$, which is 0.171 at $\nu = 0.4$.

**Column sums.** With $`W_{ji} = h_s(x_j - i)`$, write $`s(x_j - i) = j - \varphi_i`$ where $`\varphi_i = s(i + \tfrac12) - \tfrac12`$. Then

$$
c_i = \sum_j s\, h(j - \varphi_i) = s \tag{4}
$$

because $h$'s copies at unit spacing sum to 1 at any offset. Every input pixel gets the same total weight $s$, and the output's mean, $`\tfrac{1}{m}\sum_i c_i f[i]`$ over $m$ outputs, equals the input's mean. The unstretched kernel samples $h$ at spacing $1/s > 1$ instead, and none of the fixed-width kernels here sums to a constant at that spacing. For a smooth $h_s$ the rows then sum to 1 only approximately, and Pillow divides each row by its sum. For the box with pixels treated as cells, both sums are exact. At $s = 0.6$ the area weights are 0.6 and 0.4, then 0.2, 0.6 and 0.2, then 0.4 and 0.6. Each column adds to 0.6, and the mean comes back as 147.

## Implementation: the tooling map

Every call below is mapped to the arithmetic above. **None of it was executed for this post** — the mapping comes from each library's documentation and from its source at a pinned commit. Figure 10 is the same map in one picture.

![Grid of resize calls in OpenCV, Pillow, scikit-image and SciPy with kernel, cubic parameter, prefilter on shrink and sample positions](FIG_10)

*Figure 10 — The same words mean four libraries' worth of arithmetic. None of it was executed for this post; every cell comes from documentation or from source at a pinned commit.*

### OpenCV

| Want | Call | What it computes | Gotcha |
|---|---|---|---|
| default | `cv2.resize(img, dsize)` | `INTER_LINEAR`, 2 taps per axis <!-- L28 --> | no prefilter; shrinks correctly only at exactly 0.5× <!-- L36 --> |
| shrink | `interpolation=cv2.INTER_AREA` | box prefilter of width $1/s$, overlap weights <!-- L35 --> | documented as similar to nearest when enlarging <!-- L29 --> |
| enlarge | `interpolation=cv2.INTER_CUBIC` | Keys with $a = -0.75$ <!-- L32 --> | overshoots an edge by 11.1%; taps at the border replicate the edge pixel <!-- L34 --> |
| enlarge, sharper | `interpolation=cv2.INTER_LANCZOS4` | Lanczos-4, 8 taps, normalised <!-- L30 --> | not the Lanczos-3 most other tools mean |
| nearest | `cv2.INTER_NEAREST` / `cv2.INTER_NEAREST_EXACT` | index $`\lfloor j/s \rfloor`$ / pixel centres <!-- L31 --> | only `_EXACT` matches Pillow and scikit-image |
| halve with a prefilter | `cv2.pyrDown(img)` | 5×5 binomial blur, then every other row and column <!-- L37 --> | exactly 2×; repeat and finish with one resample |

Keys' own paper handled the borders by extrapolating one sample, $`c_{-1} = 3f(x_0) - 3f(x_1) + f(x_2)`$, to keep third order at the edge. <!-- L08 --> OpenCV replicates the edge pixel instead, so its first and last outputs are not third-order.

### Pillow, scikit-image, SciPy

| Library | Call | Default kernel | Prefilter on shrink | Gotcha |
|---|---|---|---|---|
| Pillow | `img.resize(size)` | `BICUBIC`, $a = -0.5$ <!-- L38 --> <!-- L39 --> | yes — every filter stretched by the in/out ratio <!-- L40 --> | `LANCZOS` is Lanczos-3; `reducing_gap` trades exactness for speed |
| scikit-image | `skimage.transform.resize(img, shape)` | order 1 (linear) | yes — Gaussian with $\sigma = (d - 1)/2$ for downscale factor $d$ <!-- L41 --> | at $d = 5/3$, $\sigma$ is only 0.33 |
| SciPy | `scipy.ndimage.zoom(img, z)` | order 3 B-spline | **no** — its `prefilter` computes spline coefficients <!-- L42 --> | corner-aligned grid unless `grid_mode=True` |

### Check any resize by hand

The column sums in Figure 8 can be read off any 1-D resize without looking at its source. Resize a row that is zero everywhere except for a 1 at position $i$, and add up the output. That total is column $i$'s sum.

```python
import numpy as np, cv2

def column_sums(n, scale, flag):
    """Total weight each of n input pixels receives in a resize by `scale`."""
    sums = []
    for i in range(n):
        row = np.zeros((1, n), np.float64)
        row[0, i] = 1.0                        # one input pixel switched on
        out = cv2.resize(row, None, fx=scale, fy=1, interpolation=flag)
        sums.append(out.sum())                  # its total weight across all outputs
    return sums

print(column_sums(5, 0.6, cv2.INTER_AREA))     # worked example: five equal values of 0.6
print(column_sums(5, 0.6, cv2.INTER_LINEAR))   # worked example: 0.667, 0.333, 1, 0.333, 0.667
```

This was not run for this post, and the output width for a given `fx` follows OpenCV's own rounding, so check `out.shape` first. The test itself does not depend on either. A flat result means the resize weighs every input equally; a ripple shows which grid phases it favours.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** shrinking with the default `INTER_LINEAR`, or with any interpolation flag of fixed width. It reads 2, 4 or 6 pixels per output however far you shrink, so below 0.5× some input pixels never contribute at all — three in four at 0.25× with `INTER_LINEAR` — and at every factor except 0.5× the rest are weighted unequally. The symptom is moiré on regular texture, text that breaks into fragments, and a detector threshold that has to be retuned for every input size. Use `INTER_AREA`, a stretched-kernel resize such as Pillow's, or scikit-image with its default anti-aliasing.

- **Blurring after the shrink instead of before.** The folded energy already sits at low frequency, indistinguishable from real content. The hub's [sampling stage](https://canery.in/blogs/image-processing-by-hand#stage-1--sample-the-grid-is-already-lossy) makes that argument; the column sums make it checkable.
- **Expecting a better interpolator to shrink better.** At 0.4 cycles per pixel on a 0.6× shrink, Lanczos-3 passes 82%, Keys 72% and linear 57%. Among these three, sharper means more aliasing, not less.
- **Treating "bicubic" as one computation.** OpenCV and Pillow differ in $a$, in whether they prefilter, in border handling, and — for nearest-neighbour — in where the samples sit. On the 1.7× row the two values of $a$ alone move j0 by 6.9 grey levels, before any other difference enters.
- **Forgetting that overshoot is clipped.** On 8-bit output, Lanczos-3's 255.6 becomes 255 and a dip below 0 becomes 0, which is the dark rim Mitchell and Netravali saw beside edges. <!-- L12 --> On float output nothing clips, and a negative value will break a later `log` or `sqrt`.
- **Resizing gamma-encoded values.** Averaging sRGB codes is not averaging light, so on a gamma-encoded image every weighted sum here averages the wrong quantity. That account belongs to Part 13, *Colour and Gamma*.
- **Beyond this post:** a rotation or warp resamples too, and the same rule applies along whichever axis is compressed. Resizing through the spectrum, by padding or truncating the DFT, is Part 5's subject, *The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering*. Learned super-resolution is out of scope for the series.

## Key takeaways

- **Enlarging is a reconstruction problem and shrinking is a filtering problem.** One interpolation flag answers only the first. The kernel trades blocking, blur and ringing; only a prefilter stops a shrink from folding detail into patterns that were never there.
- **A shrink by $s$ needs a kernel $1/s$ times wider.** A fixed-width interpolator reads the same 2, 4 or 6 pixels however far you shrink; at 0.6× linear already weights one input three times as heavily as its neighbour.
- **Audit a resize by its column sums.** Rows summing to 1 keep a flat image flat. Columns all summing to $s$ keep every input pixel counted equally, and with it the mean. Only area averaging achieves both exactly; stretched kernels come close.
- **"Bicubic" is a family.** OpenCV's $a = -3/4$ overshoots an edge by 1/9 and Pillow's $a = -1/2$ by 2/27. Only $a = -1/2$ is third-order accurate, meaning it reproduces every quadratic exactly.

## References

1. Keys, R. G. "Cubic Convolution Interpolation for Digital Image Processing." *IEEE Transactions on Acoustics, Speech, and Signal Processing* 29(6):1153–1160, 1981. doi:10.1109/TASSP.1981.1163711. [PDF](http://www.ncorr.com/download/publications/keysbicubic.pdf) (accessed 2026-09-25)
2. Mitchell, D. P., and Netravali, A. N. "Reconstruction Filters in Computer Graphics." *ACM SIGGRAPH Computer Graphics* 22(4):221–228, 1988. doi:10.1145/378456.378514. [PDF](https://www.cs.utexas.edu/~fussell/courses/cs384g-fall2013/lectures/mitchell/Mitchell.pdf) (accessed 2026-09-25)
3. Heckbert, P. S. *Fundamentals of Texture Mapping and Image Warping.* Master's thesis, University of California, Berkeley, 1989. Technical report UCB/CSD-89-516. [PDF](http://www.cs.cmu.edu/~ph/texfund/texfund.pdf) (accessed 2026-09-25)
4. Thévenaz, P., Blu, T., and Unser, M. "Interpolation Revisited." *IEEE Transactions on Medical Imaging* 19(7):739–758, 2000. doi:10.1109/42.875199. [PDF](https://bigwww.epfl.ch/publications/thevenaz0002.pdf) (accessed 2026-09-25)
5. Unser, M. "Sampling—50 Years After Shannon." *Proceedings of the IEEE* 88(4):569–587, 2000. doi:10.1109/5.843002. [PDF](https://bigwww.epfl.ch/publications/unser0001.pdf) (accessed 2026-09-25)
6. Meijering, E. "A Chronology of Interpolation: From Ancient Astronomy to Modern Signal and Image Processing." *Proceedings of the IEEE* 90(3):319–342, 2002. doi:10.1109/5.993400. [PDF](https://bigwww.epfl.ch/publications/meijering0201.pdf) (accessed 2026-09-25)
7. Parmar, G., Zhang, R., and Zhu, J.-Y. "On Aliased Resizing and Surprising Subtleties in GAN Evaluation." *CVPR*, 11400–11410, 2022. doi:10.1109/CVPR52688.2022.01112. [arXiv:2104.11222](https://arxiv.org/abs/2104.11222) (accessed 2026-09-25)
8. Shannon, C. E. "Communication in the Presence of Noise." *Proceedings of the IRE* 37(1):10–21, 1949. doi:10.1109/JRPROC.1949.232969. [PDF](https://www.math.unl.edu/~bdeng1/Teaching/math943/Topics/Genetics/Shannon1949.pdf) (accessed 2026-09-25)
9. OpenCV 4.x documentation. "Geometric Image Transformations" — `resize`, `InterpolationFlags`. <https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html> (accessed 2026-09-25)
10. OpenCV source, `modules/imgproc/src/resize.cpp`, commit cc293ea. <https://github.com/opencv/opencv/blob/cc293eaff62cd4f072ca808962a0e279221c13f3/modules/imgproc/src/resize.cpp> (accessed 2026-09-25)
11. OpenCV 4.x documentation. "Image Filtering" — `pyrDown`. <https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html> (accessed 2026-09-25)
12. Pillow documentation. `Image.resize` and "Concepts: Filters." <https://pillow.readthedocs.io/en/stable/reference/Image.html> (accessed 2026-09-25)
13. Pillow source, `src/libImaging/Resample.c`, commit c65fe08. <https://github.com/python-pillow/Pillow/blob/c65fe0814878fddcda13cacc57a297acb5019375/src/libImaging/Resample.c> (accessed 2026-09-25)
14. scikit-image documentation. `skimage.transform.resize`. <https://scikit-image.org/docs/stable/api/skimage.transform.html> (accessed 2026-09-25)
15. SciPy documentation. `scipy.ndimage.zoom`. <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.zoom.html> (accessed 2026-09-25)
