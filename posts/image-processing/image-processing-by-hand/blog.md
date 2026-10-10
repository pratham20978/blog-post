---
title: "Image Processing by Hand: Sample, Filter, Transform, Decide"
slug: image-processing-by-hand
date: 2026-09-10
updated: 2026-09-10
summary: "An image is a 2-D signal, and almost every classical operation on it is one weighted sum over a neighbourhood. Four stages, worked by hand on real integers."
tags: [algorithms, image-processing, convolution, signal-processing, opencv, fourier-transform]
category: algorithms
categories: [algorithms]
tier: L4
difficulty: advanced
series: image-processing
series_position: 1
prerequisites: ["basic calculus", "complex exponentials", "matrix notation", "reading Python signatures"]
reading_minutes: 40
cover_image_url: "https://minio.canery.in/media/cover.png"
cover_image_alt: "Four-stage image processing pipeline: sample, filter, transform, decide, over a 2-D signal"
canonical_url: "https://canery.in/blogs/image-processing-by-hand"
---

> [!NOTE]
> **Insights** — An image is a 2-D signal that was already damaged before your code opened it, and almost every classical operation you then apply is one arithmetic move: lay a small grid of weights over a neighbourhood, multiply, add. Gaussian blur, Sobel, sharpening and the Laplacian are that same sum with different weights. So the useful question is never *which filter* — it is what a given set of weights does to the signal, and where the arithmetic stops being linear. Image processing is four stages, and three of them are that sum.

**Level:** advanced · **You need:** basic calculus, complex exponentials, matrix notation, and enough Python to read a function signature · **Time:** ~40 min

This is the parent post of a series. It builds the frame and the shared math and then stops: where an area deserves a full treatment, it is named and handed to a child post rather than half-taught here.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Stage 1: sample](#stage-1--sample-the-grid-is-already-lossy) · [Stage 2: filter](#stage-2--filter-every-linear-filter-is-one-weighted-sum) · [Stage 3: transform](#stage-3--transform-what-frequency-shows-that-pixels-hide) · [Stage 4: decide](#stage-4--decide-where-linearity-stops) · [Assembling a detector](#assembling-a-detector-from-the-four-stages) · [Scale](#scale-the-parameter-nobody-sets-on-purpose) · [The math](#the-math) · [Implementation](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was executed. No packages were installed, no notebook was run, no image was loaded. Every number below is worked by hand on integers you can check on paper, or it carries a citation. There are consequently no timings, no benchmarks, and no measured curves — the two figures that show curves are plotted from closed-form expressions and say so in the caption.

## Why this matters

Your edge detector works on the test image and finds lace everywhere on the production one. You raise the threshold and it stops finding the actual edge. You try a different detector and get the same behaviour with different artefacts. Nothing in that loop converges, because the problem is not the detector.

Here is the specific version of that. In the 5×5 patch this post uses throughout, one single bad pixel — one sensor hot spot, one dead element, one compression artefact — changes the Sobel horizontal gradient at a neighbouring position from 640 to 210. That is a 67% error in the quantity your threshold is being compared against, produced by a pixel three columns away from the edge you care about.

No threshold value fixes that. The fix is one stage earlier. That is the recurring shape of image-processing bugs: the symptom appears at the decision, the cause lives at the sampling or the filtering, and enough math separates them that people stop tracing and start guessing parameters.

The four-stage frame exists to make that trace short. Once you can name which stage produced a number and which operator produced it, "the threshold is wrong" becomes "the derivative was taken before the noise was removed" — and that has an answer.

## The problem

Image processing is what happens after an optical system has turned a scene into a finite array of integers, and the honest starting point is what that conversion cost.

Model the pre-sensor quantity as a continuous function of two spatial variables:

$$
f(x, y) \in \mathbb{R}, \qquad (x, y) \in \mathbb{R}^2
$$

$f$ is brightness as a function of position: feed it any point on the image plane, however finely specified, and it returns a real number. Nothing is discrete yet.

Two things then happen to $f$, and both are irreversible. **Sampling** replaces the continuous domain with a grid: you keep $f$ at integer positions and discard it everywhere else, producing an array $`I[r, c]`$. The values between grid points are not approximated or compressed — they are gone. **Quantisation** replaces the continuous range with a finite set: a real brightness becomes one of 256 levels in an 8-bit image, so any two brightnesses closer than one level become the same integer.

Figure 1 shows the four stages that follow, and marks which can be undone.

![Four-stage pipeline diagram: a continuous scene enters a sample stage marked irreversible, then a filter stage, a transform stage marked invertible, and a decide stage marked irreversible, with the array representation shown between each stage](https://minio.canery.in/media/fig-01-four-stages.png)

*Figure 1 — The only stage that destroys information is the first one. Filtering is usually not invertible in practice, the transform is invertible by construction, and the decision throws away everything except the answer.*

Read Figure 1 backwards and the structure of every bug becomes visible. The decide stage is where you look, because that is where the wrong answer appears. The sample stage is where the information went, and no downstream cleverness recovers it.

So your code holds a table of integers, but the object you have to *reason* about is the signal that table was taken from, because the operators are all defined against the signal. Figure 2 puts the two side by side.

![The same 5 by 5 patch shown twice: on the left a labelled grid of integers with the value 255 highlighted, on the right row 2 drawn as a step profile where 40 is a plateau, 255 a narrow spike, and 200 a wide step](https://minio.canery.in/media/fig-02-grid-and-surface.png)

*Figure 2 — Same data twice: the array you index and the signal you reason about. The spike is one cell on the left and a discontinuity on the right.*

### What a problem statement looks like here

"Find the edges" is not a problem statement, and that is why it produces unfixable code. A statement this frame can act on names four things: **what in the signal** distinguishes the target — a step, a local extremum, a texture, a colour; **at what scale** it exists, since a 2-pixel line and a 200-pixel band are different objects and no single operator finds both; **what corrupts it** — sensor noise, impulse defects, blur, aliasing from an earlier resize; and **what answer is required** — a label, a count, a sub-pixel position, a yes or no.

Every stage below answers one of those. Scale chooses $\sigma$. Corruption decides whether you may use a linear filter at all. The required answer decides whether you ever threshold.

## Worked example

One patch carries this entire post. It is 5 rows by 5 columns, 8-bit grayscale, with a flat dark region on the left, a flat bright region on the right, a step between column 2 and column 3, and a single bad pixel of value 255 at row 2, column 1.

|       | c0 | c1  | c2 | c3  | c4  |
|-------|----|-----|----|-----|-----|
| **r0**| 40 | 40  | 40 | 200 | 200 |
| **r1**| 40 | 40  | 40 | 200 | 200 |
| **r2**| 40 | **255** | 40 | 200 | 200 |
| **r3**| 40 | 40  | 40 | 200 | 200 |
| **r4**| 40 | 40  | 40 | 200 | 200 |

Three operators, all of which "remove noise", all applied to the *same nine numbers*. The nine are the 3×3 neighbourhood centred on the bad pixel at (2, 1):

```
40   40   40
40  255   40
40   40   40
```

### The box mean

Add the nine values and divide by nine. Eight of them are 40 and one is 255:

$$
8 \times 40 + 255 = 320 + 255 = 575, \qquad \frac{575}{9} = 63.9
$$

Rounded to an integer, the centre pixel becomes **64**. The impulse is not removed. It is spread: the centre went from 255 down to 64, and — because this same window slides over every position — each of the eight neighbours also rises from 40 to 64 when its own window contains the 255. One bad pixel became nine mediocre ones.

### The median

Sort the nine values and take the middle one. Sorted, they are eight 40s followed by a single 255, so the fifth value is **40**.

The impulse is gone exactly, and the neighbours are untouched: any window that contains the 255 has at least five 40s in it, so the 255 never reaches the middle position. This is the whole argument for rank filters, and it is visible in nine numbers.

### The Gaussian

The Gaussian is the weighted sum people reach for by default, so it is worth using the exact weights OpenCV would use rather than a textbook approximation. Its documented kernel is

$$
G_i = \alpha \exp\!\left(-\frac{\left(i - \tfrac{k-1}{2}\right)^2}{2\sigma^2}\right)
$$

with $i = 0 \ldots k-1$ over a kernel of size $k$, and $\alpha$ chosen so the coefficients sum to 1. <!-- L13 --> When you pass a non-positive $\sigma$, OpenCV derives one from the kernel size as $\sigma = 0.3\big((k-1) \cdot 0.5 - 1\big) + 0.8$. <!-- L14 -->

For $k = 3$ that gives $\sigma = 0.3(1 - 1) + 0.8 = 0.8$ exactly. So the default 3×3 Gaussian blur has $\sigma = 0.8$, and its three coefficients are computable by hand. The unnormalised values are $e^{-1/1.28}$, $e^{0}$, $e^{-1/1.28}$, that is $0.4578$, $1$, $0.4578$, summing to $1.9157$. Dividing through:

$$
G = \begin{bmatrix} 0.239 & 0.522 & 0.239 \end{bmatrix}
$$

Those three numbers are the 1-D Gaussian at $\sigma = 0.8$, normalised so a flat region keeps its brightness. Note they are *not* the familiar $\tfrac{1}{4}[1\ 2\ 1] = [0.25, 0.5, 0.25]$ — the binomial kernel is a different filter that people call by the same name.

The 2-D weights are the outer product $G^{\top}G$, which gives three distinct values: the centre $0.522^2 = 0.2725$, the four edge-adjacent cells $0.239 \times 0.522 = 0.1248$, and the four corners $0.239^2 = 0.0571$.

Now evaluate it. The centre holds 255 and all eight neighbours hold 40, so the weighted sum splits into two terms:

$$
0.2725 \times 255 \;+\; (1 - 0.2725) \times 40 \;=\; 69.5 + 29.1 \;=\; 98.6
$$

The centre becomes **99**.

That result is worth stopping on, because it is the opposite of the Gaussian's reputation. Against a single impulse it performs *worse* than the box mean — 99 versus 64 — for a mechanical reason: it puts 27% of the total weight on the one pixel that is wrong. Its smoothness buys good behaviour against noise spread across many pixels and nothing against noise concentrated in one.

Figure 3 shows the three answers next to the window that produced them.

![The 3 by 3 window over the impulse pixel, with three outputs branching from it: box mean 64, Gaussian 99, and median 40, each annotated with the arithmetic that produced it](https://minio.canery.in/media/fig-03-three-answers.png)

*Figure 3 — Box 64, Gaussian 99, median 40, from the identical nine numbers. The operator, not the data, decides.*

### The shape all three share

Two of the three are the same operation: the box and the Gaussian both multiply each of nine neighbours by a fixed number and add, differing only in the nine numbers. Figure 4 shows them alongside a third stencil that nobody calls a smoother.

![Three 3 by 3 weight stencils side by side with their numeric values: a box filter of nine equal ninths, a Gaussian with corner 0.0571, edge 0.1248, centre 0.2725, and a Sobel x-derivative with minus one, zero, one across the top row and minus two, zero, two across the middle](https://minio.canery.in/media/fig-04-weight-stencils.png)

*Figure 4 — Box, Gaussian at σ = 0.8, and the Sobel x-derivative. One operation, three weight sets. The third one sums to zero, which is what makes it a derivative rather than an average.*

The median is not in that family, and cannot be written that way. It sorts. That single distinction — sums versus sorts — is what separates stages 2 and 4 of the pipeline, and the rest of this post is organised around it.

## Intuition

Two words in this field get used as metaphors when they are actually operations, and the metaphor is where readers lose the thread.

### "Signal"

There is no property of a pixel that makes it signal or noise. The split is entirely a claim about *structure*, and it is a claim you supply.

Take the patch. The 255 at (2, 1) is noise if your model says brightness varies slowly across space, because a lone pixel 215 levels above its neighbours contradicts that model. It is signal if you are hunting hot pixels, in which case the 40s are the noise. Nothing changed but the question.

So "extract the signal" always unpacks to: *state the structural property, then build an operator whose output is large where it holds and small where it does not.* The Gaussian's property is "brightness varies slowly", so it responds strongly to flat regions. The Sobel's is "brightness changes along $x$", and its weights sum to zero precisely so flat regions produce no response — check the third stencil in Figure 4 against nine equal values and you get zero.

An operator is a hypothesis about structure, expressed as arithmetic.

### "Detecting"

Detection is not one act but three, and conflating them is why "which detector should I use" is unanswerable.

1. **Respond.** Build a number at every position that is large where the thing is. For an edge, the gradient magnitude. For a corner, the smaller eigenvalue of a local gradient covariance. This step is a filter, and it is linear or near-linear.
2. **Localise.** The response is broad — a step edge produces a large gradient over several pixels, not one. Reduce it to a single position, usually by keeping only local maxima along a specific direction.
3. **Commit.** Turn the surviving numbers into a decision with a threshold, and accept that you now have false positives and false negatives in a ratio you chose.

Canny is exactly those three with a fourth step bolted on to repair step 3, and once you see the decomposition you can substitute into any stage independently. That is what the frame buys.

### The analogy, and where it breaks

An image behaves like a photograph of a landscape, and a filter like looking at that landscape through frosted glass of varying thickness: thicker glass, more blur, large shapes surviving while fine texture goes.

The analogy breaks at three points, and each break is a section of this post. It breaks at **the grid** — frosted glass acts on a continuous scene, while your array has already been sampled, so some of its "detail" is not detail at all but a low-frequency ghost of detail too fine to sample, which no glass removes. It breaks at **direction**, because real filters need not be isotropic and the useful ones usually are not, a derivative having an axis. And it breaks at **linearity**: the median is not glass of any thickness, since no amount of blurring deletes an impulse without touching its neighbours.

## Stage 1 — Sample: the grid is already lossy

Sampling is the only unconditionally irreversible stage in Figure 1, and it runs before your code does. What it costs is governed by one theorem.

Shannon's statement: a function containing no frequency higher than $W$ is completely determined by its ordinates spaced $1/(2W)$ apart. <!-- L01 --> The paper was received in 1940 and held until 1949 by the war. <!-- L02 -->

Concretely: if the finest detail in the scene oscillates at most $W$ times per unit distance, then samples taken more than twice that often lose nothing at all, and the continuous signal can be reconstructed exactly. Two samples per cycle of the fastest thing present.

The frequency-domain mechanism is what makes the failure mode predictable. Ideal sampling multiplies the signal by an impulse train, and multiplication by an impulse train in space becomes *replication* in frequency: the signal's spectrum is copied at every multiple of the sampling frequency. <!-- L03 --> If the copies do not overlap, you can isolate the original and reconstruction is exact. If they do overlap, high frequencies land on top of low frequencies and become indistinguishable from them. That overlap is aliasing, and Figure 5 shows it.

![Frequency-domain diagram showing a signal spectrum replicated at multiples of the sampling frequency, with a well-separated case above and an overlapping case below where the tails of adjacent copies sum into the passband](https://minio.canery.in/media/fig-05-spectral-replication.png)

*Figure 5 — The copies overlap before the sample is taken, which is why the fix cannot come after. Redrawn from the standard spectral-replication argument (Torralba, Isola & Freeman, ch. 20).*

The condition for non-overlap is a strict inequality — the sampling frequency must *exceed* twice the maximum signal frequency, not merely equal it. <!-- L04 -->

### The theorem never actually applies to your image

Here is the part that textbook treatments state and tutorials drop. A signal of finite extent cannot be band-limited: Fourier duality makes finite support and finite bandwidth mutually exclusive. <!-- L05 --> Your image is finite. Therefore its spectrum extends to infinity, therefore the replicated copies overlap at *every* sampling rate, therefore some aliasing is always present and exact reconstruction is never available even in principle.

This is not pedantry. It changes what you can promise. "Sample above Nyquist and you are fine" is false for images; the true statement is "sample fast enough that the aliased energy is small relative to what you care about". The first version implies a correctness threshold. The second implies a budget, which is what you actually manage.

### The operational consequence

Because information is destroyed at sample time, the anti-aliasing filter has to run *before* the samples are taken. <!-- L06 --> That ordering is the entire practical content of this stage:

- **Downscaling an image is resampling.** You are choosing a new, coarser grid, so you must low-pass filter first. Blurring after you downscale removes nothing, because the aliased energy is already sitting in the low frequencies, indistinguishable from real content.
- **A filter that only interpolates does not prefilter.** This is a real trap with a documented default, and it appears again in [Limitations](#limitations-and-common-mistakes).
- **Rotation and warping are resampling too**, and the same ordering applies along whichever axis is being compressed.

The reconstruction half of this — which interpolation kernel to use when you resample, and what "third-order accurate" buys you <!-- L50 --> — is a child post: *Resampling and aliasing: interpolation kernels in practice*.

## Stage 2 — Filter: every linear filter is one weighted sum

The worked example already did this arithmetic; the general form compresses it. A linear shift-invariant filter is fully described by one small array of weights $K$, and its output at every position is the same weighted sum you computed by hand:

$$
J[r, c] \;=\; \sum_{i}\sum_{j} K[i, j] \cdot I[r + i,\; c + j]
$$

For each output pixel, lay the weight grid over the input centred at that pixel, multiply each weight by the value underneath it, add the products. That is the whole operation: the box mean is this with every $K[i,j] = 1/9$, the Gaussian with the nine numbers from Figure 4, the Sobel derivative with weights summing to zero.

**Linear** means the sum of two inputs filters to the sum of their outputs; **shift-invariant** means the weights do not depend on position. Together they are exactly the conditions under which stage 3 becomes available.

### Correlation is not convolution, and OpenCV computes the first one

The expression above is *correlation*. Convolution has a sign flip:

$$
(K * I)[r, c] \;=\; \sum_{i}\sum_{j} K[i, j] \cdot I[r - i,\; c - j]
$$

The kernel is mirrored through its centre before being applied. For any kernel with 180° rotational symmetry — the box, the Gaussian, the Laplacian — the two expressions give identical results and the distinction is invisible. For an asymmetric kernel, they give mirror-image answers.

OpenCV's `filter2D` is documented under the summary line "Convolves an image with the kernel", and then states plainly that it computes correlation, not convolution, and that the kernel is not mirrored around the anchor. <!-- L10 --> The documented remedy is to flip the kernel yourself and move the anchor to `(cols - anchor.x - 1, rows - anchor.y - 1)`. <!-- L11 -->

This is the cleanest example in the library of the gap this post is about: the name encodes the math, the implementation does something adjacent, and every symmetric kernel you test with agrees with both — so the bug survives until you pass a derivative or a motion blur and the result comes out backwards.

### Separability halves the work

Some 2-D kernels factor into a column vector times a row vector, $K = g^{\top} h$. When they do, the 2-D sum splits into two 1-D passes: filter every row with $h$, then filter every column with $g$.

The Gaussian from the worked example factors exactly, which is why its three distinct weights were products of $[0.239, 0.522, 0.239]$ with itself. One 3×3 stencil costs nine multiplies per pixel; two 1-D passes cost three plus three. For a $k \times k$ kernel that is $k^2$ against $2k$, so the saving grows: nine versus six at $k = 3$, and 225 versus 30 at $k = 15$. Figure 6 shows both routes producing the same output.

![Two routes from input to output: the upper path applies one 3 by 3 stencil with nine multiplies, the lower path applies a 1 by 3 row kernel then a 3 by 1 column kernel with three multiplies each, both arriving at the same output value](https://minio.canery.in/media/fig-06-separability.png)

*Figure 6 — Nine multiplies become six, and the result is identical. OpenCV's separable filters auto-detect symmetric kernels that sum to one and handle them accordingly.* <!-- L60 -->

The Sobel operator is separable too, and factoring it reveals what it actually is: $[1, 2, 1]^{\top}$ times $[-1, 0, 1]$ — a smoothing pass and a differencing pass. OpenCV's documentation makes the same point, that the Sobel operators combine smoothing with differentiation, which is why they resist noise better than a bare difference. <!-- L20 --> With `ksize=1` you get the bare $3 \times 1$ difference and no smoothing at all. <!-- L21 --> The library's other 3×3 aperture, `FILTER_SCHARR`, comes from a different objective again: its coefficients were optimised for rotation invariance rather than derived as an approximation to a continuous derivative. <!-- L23 -->

### Borders are a decision, not a detail

At the boundary the window hangs off the array and the sum has no values to use. Every implementation invents them, and the invention is a parameter. Figure 7 shows the options producing different answers at the same pixel.

![One row of pixels at the left boundary shown five times, each with a different border extrapolation filling the missing positions: constant zero, replicated edge value, reflected, reflected without duplicating the edge, and wrapped from the opposite side](https://minio.canery.in/media/fig-07-border-modes.png)

*Figure 7 — Five rules, five answers, same pixel. OpenCV's linear filters default to `BORDER_DEFAULT`, while its morphology defaults to `BORDER_CONSTANT` with a magic value that becomes −DBL_MAX for dilation.* <!-- L43 -->

Two library facts worth carrying: the linear filters and the morphological operators do not share a default border rule, and `filter2D` silently switches to a DFT-based algorithm for kernels around 11×11 or larger. <!-- L12 --> The second is stage 3 arriving as an implementation detail.

Kernel design proper — how the Scharr coefficients are chosen, what "optimal" means for a derivative filter, how truncation interacts with $\sigma$ — is a child post: *Kernel design: separability, borders, and optimised derivative filters*.

## Stage 3 — Transform: what frequency shows that pixels hide

The pixel view tells you what a filter computes. It does not tell you what a filter *does*. For that you change basis — and the standard textbook treatment organises the field around exactly this pairing, spatial and frequency-domain filtering as two views of one operation. <!-- L59 -->

The discrete Fourier transform rewrites a signal as a sum of complex exponentials:

$$
X[k] \;=\; \sum_{n=0}^{N-1} x[n] \, e^{-2\pi i k n / N}
$$

$X[k]$ measures how much of a length-$N$ sequence is a wave completing $k$ cycles across its length. Everything below is a 4-point instance, with no symbol appearing before its value.

### A 4-point DFT by hand

Take the middle four samples of row 0 of the patch: $x = [40, 40, 200, 200]$, a clean step.

For $N = 4$ the exponentials collapse to powers of $-i$, so the basis is just four sign-and-swap patterns:

| $k$ | pattern | means |
|---|---|---|
| 0 | $1, 1, 1, 1$ | the average |
| 1 | $1, -i, -1, i$ | one cycle across the four samples |
| 2 | $1, -1, 1, -1$ | two cycles: alternating pixels, the fastest representable |
| 3 | $1, i, -1, -i$ | one cycle the other way |

Now evaluate. Each coefficient is four multiplications and an addition:

$$
X[0] = 40 + 40 + 200 + 200 = 480
$$

The zeroth coefficient is the plain sum, so $X[0]/4 = 120$ is the mean of the four samples — check it against the numbers. The other three use the sign patterns from the table:

$$
X[1] = -160 + 160i, \qquad X[2] = 40 - 40 + 200 - 200 = 0, \qquad X[3] = -160 - 160i
$$

The magnitudes are $480$, $226.3$, $0$, $226.3$: a step has a large mean, substantial energy at the lowest non-zero frequency, and — because this step is symmetric about its midpoint — exactly nothing at the alternating frequency.

### The convolution theorem, on those same numbers

Now filter that row with the binomial kernel $\tfrac{1}{4}[1, 2, 1]$. As a length-4 sequence with its centre tap at position 0 and wrapping, that is $h = [0.5, 0.25, 0, 0.25]$. Transform it the same way:

$$
H = \begin{bmatrix} 1 & 0.5 & 0 & 0.5 \end{bmatrix}
$$

Those four numbers are the filter's **transfer function**, the factor by which it scales each frequency. $H[0] = 1$ means the average passes untouched; $H[2] = 0$ means the alternating-pixel component is annihilated — not attenuated, multiplied by zero. That is what "low-pass" means as arithmetic, and here it has a closed form: $H[k] = \cos^2(\pi k / 4)$.

The convolution theorem says filtering in space is multiplication in frequency. <!-- L09 --> So multiply term by term:

$$
Y = H \cdot X = \begin{bmatrix} 480 & -80 + 80i & 0 & -80 - 80i \end{bmatrix}
$$

Each input frequency has been scaled by its own gain, and nothing else has happened. Inverting gives

$$
y = \begin{bmatrix} 80 & 80 & 160 & 160 \end{bmatrix}
$$

Now check it the other way. Circular convolution of $x$ with $h$ directly: $y[0] = 0.5(40) + 0.25(200) + 0.25(40) = 20 + 50 + 10 = 80$, and the remaining three positions give $80$, $160$, $160$. The two routes agree exactly, which is the theorem holding on numbers you just added up.

Figure 8 lays the whole computation out.

![The four-point computation in four panels: the input step and its DFT magnitudes, the kernel and its transfer function shaped like cosine squared, the term-by-term product, and the output row with the two agreeing routes marked](https://minio.canery.in/media/fig-08-dft-four-point.png)

*Figure 8 — Two routes to [80, 80, 160, 160]: nine multiplies in space, or one multiply per frequency. Both are shown because the agreement is the point.*

Two things fall out of that output. The step softened, as expected. And the first value went from 40 up to 80 — a large change — because circular convolution wrapped around and pulled in the 200 from the far end. That is stage 2's border question reappearing as a mathematical necessity rather than an implementation choice: the DFT's convolution is inherently circular, and spatial filters use border extrapolation precisely to avoid this.

### Why this basis is worth the change

Once a filter is a list of per-frequency gains, opaque questions become arithmetic. Figure 9 puts three familiar kernels on one axis.

![Transfer function curves for a box filter, a Gaussian, and a Laplacian plotted against normalised frequency: the box oscillates and goes negative, the Gaussian decays smoothly and monotonically, the Laplacian rises from zero](https://minio.canery.in/media/fig-09-transfer-functions.png)

*Figure 9 — **A model, not a measurement.** Plotted from the closed-form transfer functions, not from filtering an image. The box filter's negative lobes are why it is a poor smoother despite being an average.*

The box filter's transfer function oscillates and goes negative, so it inverts some frequencies rather than merely reducing them. The Gaussian's decays monotonically and never changes sign, which is precisely what "well-behaved smoother" means. The Laplacian's rises from zero, which is what makes it a sharpener and equally what makes it a noise amplifier — noise lives at high frequencies, and that is where its gain is largest.

The cost argument lives here too. Computing the DFT directly is a sum over every sample for every frequency; the Cooley–Tukey decomposition, published in 1965, gets the same result in far fewer operations by recursively splitting that sum. <!-- L07 --> <!-- L08 --> That is why `filter2D` switches strategies at large kernel sizes — past some size, transforming, multiplying and transforming back beats the direct sum.

The 2-D transform, phase, and frequency-domain filter design are a child post: *The 2-D DFT: spectra, phase, and frequency-domain filtering*. Where Fourier stops being the right basis — image structure is local and non-stationary, which is what multiresolution wavelet decomposition addresses <!-- L58 --> — is another: *Wavelets and multiresolution*.

## Stage 4 — Decide: where linearity stops

Everything so far has been sums. This stage sorts and compares, and none of it has a transfer function, because none of it is linear.

Three families, distinguished by the set the ordering happens over. Figure 10 separates them.

![Three nested groups of non-linear operators: threshold operators ordered on intensity against a global value, rank operators ordered on intensity within a neighbourhood, and morphological operators ordered on intensity within a structuring element with set semantics](https://minio.canery.in/media/fig-10-nonlinear-families.png)

*Figure 10 — Threshold, rank, morphology: all three sort, none of them sums. What differs is the set the ordering happens over.*

### Thresholding: ordering against a constant

One comparison per pixel. The only real question is where the constant comes from.

Otsu's answer is to read it off the histogram: treat a candidate threshold $t$ as splitting the pixels into two classes, and choose the $t$ maximising the variance *between* those classes, which is algebraically the same as minimising the variance within them. <!-- L39 -->

$$
t^{\star} = \arg\max_{t} \; \omega_0(t)\,\omega_1(t)\,\big(\mu_0(t) - \mu_1(t)\big)^2
$$

$\omega_0, \omega_1$ are the fractions of pixels in each class and $\mu_0, \mu_1$ their mean intensities, all functions of $t$. The product is largest when the two groups are both substantial and far apart in brightness.

The notation hides something worth saying plainly: this is a **search**, not a formula. <!-- L40 --> An 8-bit image has 256 candidate thresholds, and the method evaluates the criterion at each and keeps the best.

The patch's histogram is 16 pixels at 40, 8 at 200, and 1 at 255. Any threshold from 41 to 199 separates the flat regions perfectly and puts the impulse in the bright class, so the criterion is flat across that whole range. Otsu gives you *a* good threshold, not a unique one.

### Rank filters: ordering within a neighbourhood

The median is the general case at its midpoint. Sort the $n$ values in the window and take a chosen position: $n/2$ is the median, $n$ the local maximum, $1$ the local minimum.

There is no weight array, so there is nothing to transform, and superposition fails outright — the median of a sum is not the sum of the medians. Everything stage 3 offers is unavailable. In exchange you get the behaviour computed earlier: exact removal of an outlier without disturbing its neighbours, which no linear filter achieves at any $\sigma$.

### Morphology: ordering within a structuring element

Erosion and dilation are the local minimum and maximum over a shape called the structuring element, formally Minkowski subtraction and addition — the infimum and supremum over translates of that shape. <!-- L41 --> Composing them both ways gives the operators actually used: opening is erosion then dilation, closing is dilation then erosion. <!-- L42 --> Opening removes structures smaller than the element; closing fills gaps smaller than it.

On the patch, a 3×3 erosion sets (2, 1) to the minimum of its neighbourhood, 40 — so erosion removes the impulse too, by a completely different argument from the median's. Dilation does the opposite and spreads the 255 across all nine positions.

Morphology as an algebra rather than a pair of tricks — the lattice structure, adjunctions, idempotence — is a child post: *Mathematical morphology as lattice algebra*. Segmentation from Otsu through marker-based watershed, which floods the gradient surface by simulated immersion <!-- L57 -->, is another: *Thresholding and segmentation*.

### The operators that break the split

Two families sit across the boundary, and they are why this stage is called "decide" rather than "threshold".

The bilateral filter is a weighted sum whose weights depend on the image — a spatial kernel times a range kernel on intensity difference, so a neighbour differing sharply in brightness gets little weight however close it is. <!-- L44 --> That makes it non-linear and shift-variant: it smooths within regions, not across boundaries. Non-local means goes further, matching *patches* by similarity anywhere in the image instead of averaging over a spatial neighbourhood at all. <!-- L46 --> Perona–Malik diffusion makes the same move in PDE form, letting the diffusion coefficient fall where the gradient is large. <!-- L47 -->

That last one is the field's cautionary tale: the equation is formally ill-posed and generally admits no weak solution for non-analytic data near high gradients, yet simple discretisations are stable and useful, with staircasing as the visible signature of the pathology. <!-- L48 --> An operator can be effective and mathematically broken at once, and knowing which you rely on matters when it fails.

These three are a child post: *Edge-preserving smoothing: bilateral, non-local means, anisotropic diffusion*.

## Assembling a detector from the four stages

Nothing so far detects anything. This section builds one from pieces already defined, and it is where "detecting a signal" becomes a sequence of arithmetic operations.

### Step 1: respond, with a derivative

An edge is where brightness changes fast, so the response is a spatial derivative. On a discrete grid a derivative is a difference, and stage 2 already gave the operator: OpenCV's `Sobel` with `ksize=3` applies

$$
K_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}
$$

for the $x$-derivative, and its transpose for $y$. <!-- L19 --> The centre column is zero because a symmetric difference does not use the pixel it sits on; the middle row is doubled because that is the $[1,2,1]$ smoothing factor from the separable decomposition. Worth knowing about the most-taught operator in the field: Sobel and Feldman presented it as a talk at the Stanford AI Lab in 1968 and never published it, which is why citations for it vary. <!-- L25 -->

Evaluate it on the patch at (2, 3), a position sitting on the clean edge. The neighbourhood is columns 2 to 4, rows 1 to 3:

```
40  200  200
40  200  200
40  200  200
```

$$
G_x = (-1)(40) + (1)(200) + (-2)(40) + (2)(200) + (-1)(40) + (1)(200) = 160 + 320 + 160 = 640
$$

And $G_y = 0$, because the three rows are identical and the top and bottom weights cancel. The operator reports a strong horizontal change and no vertical change, which is exactly right for a vertical edge.

### Why the filter stage has to come first

Now evaluate the same operator at (2, 2), one column to the left, where the neighbourhood catches the impulse:

```
40   40  200
255  40  200
40   40  200
```

$$
G_x = (-40 + 200) + (-510 + 400) + (-40 + 200) = 160 - 110 + 160 = 210
$$

With the impulse replaced by its correct value of 40, the same position gives 640. So one bad pixel changes the gradient by 430, a **67% error**, and it does so at a position where the impulse is not even the centre pixel.

That is the argument for the ordering in Figure 1. A derivative amplifies high frequencies — Figure 9 showed the Laplacian's gain rising with frequency — and noise is high frequency, so differentiating before smoothing amplifies exactly what you did not want. It is also why the Sobel kernel carries $[1,2,1]$ internally, and why that is not enough here: it is a linear filter, and the worked example showed what those do to impulses.

Marr and Hildreth formalised the pairing: the right operator for detecting intensity change at a given scale is the second derivative of a Gaussian, with edges at the zero crossings of $\nabla^2 G * I$. <!-- L27 --> Smoothing and differentiation are one operator, not two.

### Step 2: combine the two derivatives

Two numbers per pixel become one magnitude and one direction:

$$
\|\nabla I\| = \sqrt{G_x^2 + G_y^2}, \qquad \theta = \operatorname{atan2}(G_y, G_x)
$$

The magnitude is how fast brightness changes at that point; the angle is the direction of steepest increase, which is perpendicular to the edge.

At (2, 3) this is trivial: $G_x = 640$, $G_y = 0$, magnitude 640, $\theta = 0$. For the interesting case, rotate the same step onto the diagonal — background 40 below the anti-diagonal, foreground 200 above — and evaluate at the centre. Both derivatives now read 480, so

$$
\|\nabla I\| = \sqrt{480^2 + 480^2} = 480\sqrt{2} \approx 678.8, \qquad \theta = 45^{\circ}
$$

Here the library and the math part company. OpenCV's `Canny` defaults to the $L_1$ magnitude $|G_x| + |G_y|$ and computes the Euclidean one only if you pass `L2gradient=True`. <!-- L31 --> On this diagonal edge $L_1$ gives $480 + 480 = 960$ against a true 678.8 — larger by exactly $\sqrt{2}$, or 41% — while on the axis-aligned edge, where $G_y = 0$, the two agree. So the default overstates diagonal edges relative to axis-aligned ones, and a threshold tuned on one orientation is miscalibrated on the other. Figure 11 shows the two lengths as the geometry they are.

![The gradient vector with components Gx equals 480 and Gy equals 480 drawn on axes, with the Euclidean hypotenuse of 678.8 marked against the L1 path of 960 traced along the two legs](https://minio.canery.in/media/fig-11-l1-vs-l2.png)

*Figure 11 — At 45° the default L1 magnitude is √2 times the true one. The two agree only where one component is zero.*

### Steps 3 and 4: localise and commit

The magnitude map is broad — an edge produces large values over several columns, not one. Canny's contribution was to make the criteria explicit: he defined detection and localisation as functionals on the operator's impulse response and added a single-response constraint. <!-- L28 --> The resulting optimal operator is closely approximated by the first derivative of a Gaussian. <!-- L29 -->

The single-response constraint is delivered by **non-maximum suppression**: at each pixel, compare the magnitude against its two neighbours along the gradient direction $\theta$ and zero it unless it is the largest of the three. A broad ridge becomes a one-pixel line. Note the dependency — this step needs the *direction*, which is why step 2 computes both quantities.

Then **hysteresis** replaces one threshold with two: pixels above the high threshold are edges, and pixels above the low one are edges only if they connect to a high one. That fixes the failure mode from [Why this matters](#why-this-matters), where a single threshold on a noisy magnitude map either fragments real edges or admits noise — connectivity is the extra information separating them. In OpenCV the smaller argument is used for linking and the larger for seeding, so the order you pass them does not decide which is which. <!-- L32 -->

Figures 12 and 13 show the assembled chain and the two steps that are not filters.

![Flowchart of the Canny chain: Gaussian smooth, then Sobel gradient, then non-maximum suppression along the gradient direction, then double-threshold hysteresis, with the first two boxes labelled as stage 2 operators and the last two as stage 4](https://minio.canery.in/media/fig-12-canny-chain.png)

*Figure 12 — Three of the four steps are earlier stages reused. Only hysteresis is new, and it exists to repair the threshold.*

![A one-dimensional brightness profile across an edge with its gradient magnitude below, showing a broad ridge reduced to a single peak by non-maximum suppression, and the high and low thresholds marked with a connected weak segment retained](https://minio.canery.in/media/fig-13-nms-hysteresis.png)

*Figure 13 — **A model profile**, drawn from the closed forms, not measured. The thin edge is produced by the suppression step, not by the gradient.*

### The same construction, one dimension up: corners

Swap the structural hypothesis and the same machinery finds corners. At an edge brightness changes in one direction and not the perpendicular one; at a corner it changes in both. So the quantity to build is a *gradient covariance* over a neighbourhood:

$$
M = \sum_{\text{window}} \begin{bmatrix} G_x^2 & G_x G_y \\ G_x G_y & G_y^2 \end{bmatrix}
$$

$M$ accumulates products of derivatives already computed, so its eigenvalues $\lambda_1, \lambda_2$ say how much brightness varies along the window's two principal directions. Both small means flat, one large means edge, both large means corner.

Harris and Stephens wanted that test without computing eigenvalues, so they built a response from the cheap determinant and trace instead. <!-- L34 --> OpenCV's `cornerHarris` implements it as documented:

$$
R = \det M - k \, (\operatorname{tr} M)^2
$$

$R$ is large and positive at corners, negative at edges, and near zero on flat regions, with $k$ a free parameter. <!-- L33 --> That parameter is the honest weak point: empirical, conventionally 0.04 to 0.06, and given no default by OpenCV. <!-- L34 --> Figure 14 shows what it controls.

![The lambda-1 versus lambda-2 plane divided into flat, edge, and corner regions, with the Harris response contours overlaid and an arrow showing how changing k moves the boundary between edge and corner](https://minio.canery.in/media/fig-14-eigenvalue-plane.png)

*Figure 14 — The free parameter k is the position of one boundary in this plane. Redrawn from the eigenvalue argument in Harris & Stephens (1988).*

OpenCV also ships the version without it: `cornerMinEigenVal` returns $\min(\lambda_1, \lambda_2)$ directly, the same test with nothing to tune. <!-- L35 --> When one formulation has a magic constant and an equivalent one does not, that is worth knowing before you spend an afternoon tuning the constant.

### And once more, by voting: lines

A third construction reuses the same edge map and changes only what comes after it. The Hough transform lets every surviving edge pixel vote for every line that could pass through it, then reads lines off the accumulator's peaks. Hough's 1962 patent parameterised lines by slope and intercept, leaving the accumulator unbounded because the slope diverges for vertical lines. <!-- L36 --> Duda and Hart replaced it with the normal's length $\rho$ and angle $\theta$, which bounds it. <!-- L37 --> That is what OpenCV implements, with $\rho$ from the top-left corner and $\theta = 0$ meaning vertical — a convention differing from most textbook figures. <!-- L38 -->

The structure tensor as a general tool — the same matrix drives optical flow and texture orientation — is a child post: *The structure tensor: Harris, Shi–Tomasi, and optical flow*. Canny's suppression and hysteresis in implementation detail are another: *Canny, line by line*.

## Scale: the parameter nobody sets on purpose

$\sigma$ has appeared in almost every section as a smoothing amount. It is not a smoothing amount. It is a statement about what size of structure counts as real, and it belongs to the question rather than the implementation.

The reason is in the worked example. At $\sigma = 0.8$ the Gaussian's centre weight is 0.27, so a one-pixel feature substantially survives — which is why the impulse only fell to 99. At larger $\sigma$ that centre weight shrinks, one-pixel features vanish entirely, and features spanning several pixels blend into each other. Choosing $\sigma$ chooses which structures exist in the image your operator sees, and Figure 15 shows the consequence: there is no single correct value, so the principled move is to treat it as an axis and work across it.

![A stack of increasingly blurred versions of one signal along a scale axis, with differences between adjacent levels shown as a second stack, and a feature appearing as an extremum at one specific scale](https://minio.canery.in/media/fig-15-scale-axis.png)

*Figure 15 — σ chooses which structures exist, so it is part of the question asked. Redrawn from the scale-space construction.*

Lowe made scale a search dimension, locating features as extrema of differences of Gaussians across octaves of a pyramid — a feature is not just at a position but *at a scale*, and finding it means searching both. <!-- L56 --> OpenCV's Laplacian implements the discrete second derivative directly: with `ksize=1` it filters with $[0\ 1\ 0;\ 1\ -4\ 1;\ 0\ 1\ 0]$, and for larger apertures it sums second Sobel derivatives. <!-- L26 --> That stencil sums to zero, like every derivative operator.

### The theory OpenCV does not implement

There is a genuine gap here, and it is the most interesting disagreement in this post.

OpenCV builds Gaussian kernels by evaluating the continuous Gaussian at integer points and normalising — exactly what the $\alpha$ in the documented formula does. <!-- L16 --> Scale-space theory says that is not the right discrete object. Lindeberg showed the discrete analogue is uniquely determined by four axioms — no new local extrema as scale increases, a semi-group property, spatial symmetry, and unit $\ell^1$ norm — and the sampled Gaussian does not satisfy them. <!-- L17 --> Later work reports that sampled and locally integrated Gaussians degrade badly at very fine scales, roughly below one pixel of standard deviation. <!-- L18 -->

So at $\sigma = 0.8$ — the default for a 3×3 kernel, the most common blur call in the library — you are in the regime where the approximation is documented to be worst. The practical consequence is bounded: for most tasks it does not matter. But if you rely on scale-space *properties* — that structures only ever disappear as you blur, that two successive blurs compose into one — the kernel you are actually using does not guarantee them.

Scale space proper is a child post: *Scale space and SIFT: why σ is a search dimension*.

## The math

This section is the compression. Every form here has already been evaluated on the patch, so it should read as shorthand for arithmetic you have done rather than as new material.

| Symbol | Meaning | Range or units |
|---|---|---|
| $f(x,y)$ | continuous pre-sample brightness | real, unbounded |
| $`I[r,c]`$ | sampled, quantised image | integer, 0–255 for 8-bit |
| $K$ | kernel, the weight array | real, often summing to 1 or 0 |
| $\sigma$ | Gaussian standard deviation | pixels |
| $X[k]$ | $k$-th DFT coefficient | complex |
| $H[k]$ | transfer function, gain at frequency $k$ | complex, real for symmetric kernels |
| $G_x, G_y$ | image derivatives | same units as intensity per pixel |
| $M$ | gradient covariance matrix | 2×2, positive semi-definite |
| $\lambda_1, \lambda_2$ | eigenvalues of $M$ | real, non-negative |

### The four stages as four expressions

**Sample.** The grid is the signal multiplied by an impulse train, whose effect in frequency is replication:

$$
I[r,c] = f(r\Delta, c\Delta), \qquad \widehat{I}(\omega) = \frac{1}{\Delta}\sum_{n=-\infty}^{\infty} \widehat{f}\!\left(\omega - \frac{2\pi n}{\Delta}\right)
$$

The sampled signal's spectrum is a sum of shifted copies of the original's, spaced by the sampling frequency; when they overlap, the sum is not separable back into its parts.

**Filter.** One weighted sum, in the correlation convention the libraries use:

$$
J[r,c] = \sum_i \sum_j K[i,j] \, I[r+i, c+j]
$$

Slide the weights, multiply, add — the computation done three times by hand in the worked example.

**Transform.** A change of basis, and the multiplication that replaces convolution in it:

$$
X[k] = \sum_{n} x[n] e^{-2\pi i k n/N}, \qquad \widehat{K * I} = \widehat{K} \cdot \widehat{I}
$$

Filtering costs one multiply per frequency in this basis instead of one multiply per weight per pixel, which is why large kernels are applied here.

**Decide.** A comparison, with no weights and no transform:

$$
B[r,c] = \begin{cases} 1 & \text{if } J[r,c] > t \\ 0 & \text{otherwise}\end{cases}
$$

Everything upstream existed to make $J$ a quantity for which some threshold $t$ actually separates the two cases.

### Collapsing the general forms onto the patch

The value of the frame is that each general expression reproduces a number already computed.

- The filter sum with $K[i,j] = 1/9$ and the nine neighbours of (2, 1) gives $575/9 = 63.9$ — the box mean.
- The same sum with $K = G^{\top}G$ at $\sigma = 0.8$, centre weight $0.2725$, gives $0.2725(255) + 0.7275(40) = 98.6$ — the Gaussian.
- The same sum with $K_x$ at (2, 3) gives $160 + 320 + 160 = 640$ — the Sobel derivative.
- The DFT applied to $[40, 40, 200, 200]$ gives $[480, -160+160i, 0, -160-160i]$, and the transfer function of $\tfrac{1}{4}[1,2,1]$ gives $[1, 0.5, 0, 0.5]$, whose product inverts to $[80, 80, 160, 160]$ — which direct circular convolution also produces.

Four expressions, four numbers you can check. The abstraction is not a separate thing to trust; it is a compression of arithmetic already done.

One consequence is worth stating because it makes the whole zoo sortable: apply any kernel to a constant region of value $v$ and the output is $v \sum_{i,j} K[i,j]$. Weights summing to 1 leave a flat region unchanged, which is what an average must do — and is exactly what the normaliser $\alpha$ in the documented Gaussian formula enforces. <!-- L13 --> Weights summing to 0 produce exactly zero there, which is what a derivative must do. Check $K_x$: $(-1+0+1) + (-2+0+2) + (-1+0+1) = 0$.

### Canny's optimality, stated with its conditions

Canny's result is widely cited as "the optimal edge detector", and the qualification matters more than the claim. The derivation is for a **step edge in additive white Gaussian noise, in one dimension**. <!-- L30 --> Real edges are not steps, real noise is not white, and images are not one-dimensional.

The approximation by a first derivative of Gaussian carries a cost of roughly 20% against the true optimum <!-- L29 --> — but that figure is a cost measured against Canny's own analytic criteria, not an accuracy measurement on images, and this post does not restate it as one. What survives the qualifications is the useful part: the *decomposition* into respond, localise, and commit, and the argument that those three objectives trade off against each other and cannot all be maximised at once.

## Implementation: the tooling map

Every function below is named for the piece of math it implements. **None of this was executed for this post** — nothing was installed and nothing was run, so the code is illustrative and the mapping comes from documented behaviour. Figure 16 is the same map in one picture.

![A four-column map with each pipeline stage above the specific NumPy and OpenCV calls that implement it, with the math expression each call corresponds to written beneath it](https://minio.canery.in/media/fig-16-tooling-map.png)

*Figure 16 — The map from math to call site. None of it was executed for this post.*

### What each library is for

- **NumPy** holds the array: slicing is windowing, broadcasting is per-pixel arithmetic. Every operation below can be written in NumPy alone, and doing that once per operator is the fastest way to believe the math.
- **OpenCV** (`cv2`) is the operator library — the four stages, optimised, with the border and depth handling hand-written loops get wrong.
- **SciPy** (`scipy.ndimage`, `scipy.signal`) overlaps it but uses the *convolution* convention, which makes it a useful cross-check when a result comes out mirrored.

### Stage 1 — sample

| Math | Call | Note |
|---|---|---|
| Resample to a coarser grid | `cv2.resize(img, dsize, interpolation=...)` | defaults to `INTER_LINEAR`; no prefilter <!-- L51 --> |
| Prefilter then decimate | `cv2.pyrDown(img)` | blurs then downsamples — the correct ordering |
| Area-averaged shrink | `cv2.resize(..., interpolation=cv2.INTER_AREA)` | documented for shrinking <!-- L51 --> |
| Cubic reconstruction | `cv2.resize(..., interpolation=cv2.INTER_CUBIC)` | the Keys kernel; for enlarging <!-- L50 --> |

### Stage 2 — filter

| Math | Call | Note |
|---|---|---|
| $\sum K[i,j] I[r+i,c+j]$ | `cv2.filter2D(src, ddepth, kernel)` | correlation, not convolution <!-- L10 --> |
| True convolution | `cv2.filter2D(src, ddepth, cv2.flip(kernel, -1), anchor=...)` | flip and move the anchor <!-- L11 --> |
| Two 1-D passes | `cv2.sepFilter2D(src, ddepth, kx, ky)` | the separable form from Figure 6 |
| Gaussian coefficients | `cv2.getGaussianKernel(ksize, sigma)` | the $\alpha$-normalised sampled Gaussian <!-- L13 --> |
| Gaussian smoothing | `cv2.GaussianBlur(src, ksize, sigmaX, sigmaY)` | specify all three; defaulting runs both ways <!-- L15 --> |
| Box mean | `cv2.blur(src, ksize)` | the nine-ninths stencil |
| Median | `cv2.medianBlur(src, ksize)` | a rank filter — stage 4 |
| Derivative | `cv2.Sobel(src, ddepth, dx, dy, ksize)` | `ksize=1` means no smoothing <!-- L21 --> |
| Optimised derivative | `cv2.Scharr(src, ddepth, dx, dy)` | equivalent to `Sobel(..., ksize=cv2.FILTER_SCHARR)` <!-- L22 --> |
| Second derivative | `cv2.Laplacian(src, ddepth, ksize)` | `ksize=1` uses the 5-point aperture <!-- L26 --> |

The full-precision derivative call, since the depth argument is where this stage goes wrong:

```python
import cv2, numpy as np

gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)   # CV_32F, not CV_8U:
gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)   # derivatives are signed

mag = cv2.magnitude(gx, gy)                        # L2, matching the math
ang = cv2.phase(gx, gy, angleInDegrees=True)       # the direction NMS needs
```

### Stage 3 — transform

| Math | Call | Note |
|---|---|---|
| $X[k] = \sum x[n] e^{-2\pi ikn/N}$ | `cv2.dft(src, flags=cv2.DFT_COMPLEX_OUTPUT)` | real input, complex output |
| Inverse | `cv2.idft(...)` | pair it with `DFT_SCALE` to normalise |
| Efficient size | `cv2.getOptimalDFTSize(n)` | pad to a size the FFT factors well <!-- L08 --> |
| Same, in NumPy | `np.fft.fft2` / `np.fft.ifft2` | different normalisation convention; check before comparing |
| Spectrum for inspection | `np.fft.fftshift(np.abs(F))` | moves DC to the centre |

### Stage 4 — decide

| Math | Call | Note |
|---|---|---|
| $J > t$ | `cv2.threshold(src, t, maxval, cv2.THRESH_BINARY)` | one comparison per pixel |
| Otsu's search | `cv2.threshold(src, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)` | the criterion of <!-- L39 -->, searched over 256 candidates <!-- L40 --> |
| Local minimum | `cv2.erode(src, kernel)` | Minkowski subtraction <!-- L41 --> |
| Local maximum | `cv2.dilate(src, kernel)` | Minkowski addition <!-- L41 --> |
| Opening / closing | `cv2.morphologyEx(src, cv2.MORPH_OPEN, kernel)` | erosion then dilation <!-- L42 --> |
| Structuring element | `cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize)` | the shape the ordering happens over |
| Edge-preserving smooth | `cv2.bilateralFilter(src, d, sigmaColor, sigmaSpace)` | `d=5` real-time, `d=9` offline per the docs <!-- L45 --> |
| Patch-based denoise | `cv2.fastNlMeansDenoising(src, h, ...)` | non-local means <!-- L46 --> |

### Assembled detectors

| Math | Call | Note |
|---|---|---|
| Respond, localise, commit | `cv2.Canny(img, t1, t2, apertureSize=3, L2gradient=True)` | pass `L2gradient=True` for the Euclidean magnitude <!-- L31 --> |
| $\det M - k(\operatorname{tr} M)^2$ | `cv2.cornerHarris(src, blockSize, ksize, k)` | `k` has no default <!-- L33 --> |
| $\min(\lambda_1, \lambda_2)$ | `cv2.cornerMinEigenVal(src, blockSize, ksize)` | the same test with no free parameter <!-- L35 --> |
| Corner list | `cv2.goodFeaturesToTrack(...)` | wraps the min-eigenvalue response with suppression |
| $(\rho, \theta)$ accumulator | `cv2.HoughLines(edges, rho, theta, threshold)` | Duda–Hart parameterisation <!-- L37 --> |
| Scale-space keypoints | `cv2.SIFT_create()` | difference-of-Gaussian extrema across octaves <!-- L56 --> |
| Marker-based flooding | `cv2.watershed(img, markers)` | simulated immersion <!-- L57 --> |
| Local contrast | `cv2.createCLAHE(clipLimit, tileGridSize)` | clipping bounds the noise amplification <!-- L49 --> |

To reproduce the worked example, if you do run it yourself:

```python
patch = np.array([[ 40,  40,  40, 200, 200],
                  [ 40,  40,  40, 200, 200],
                  [ 40, 255,  40, 200, 200],
                  [ 40,  40,  40, 200, 200],
                  [ 40,  40,  40, 200, 200]], dtype=np.uint8)

cv2.blur(patch, (3, 3))[2, 1]              # expect 64
cv2.medianBlur(patch, 3)[2, 1]             # expect 40
cv2.GaussianBlur(patch, (3, 3), 0)[2, 1]   # expect 99, sigma defaults to 0.8
cv2.getGaussianKernel(3, 0)                # expect [0.239, 0.522, 0.239]
```

Those four values are the ones computed by hand in the [worked example](#worked-example). At (2, 1) the window sits fully inside the array, so the border mode cannot explain a disagreement — which makes any disagreement informative.

## Limitations and common mistakes

Six specific traps, each with the condition that triggers it and the symptom it produces. All six are documented behaviour, not folklore.

> [!WARNING]
> **Common mistake:** treating `cv2.filter2D` as convolution because its summary line says "Convolves an image with the kernel". It computes correlation — the kernel is not mirrored around the anchor. <!-- L10 --> Every symmetric kernel you test with agrees under both conventions, so the bug is invisible until you pass an asymmetric one: a derivative, a motion blur, or a hand-designed directional filter comes out mirrored, and the sign of your gradient flips. Flip the kernel and move the anchor if you need true convolution. <!-- L11 -->

**Writing derivatives into an 8-bit destination.** Passing `cv2.CV_8U` as `ddepth` to `Sobel` truncates the result, which the docs state for 8-bit input. <!-- L24 --> Derivatives are signed, and an unsigned destination clips every negative value to zero — so half your edges, the ones where brightness falls rather than rises, silently disappear. Use `CV_16S` or `CV_32F` and convert afterwards.

**Tuning a threshold against the L1 gradient magnitude.** `Canny` defaults to `L2gradient=False`. <!-- L31 --> The worked numbers show the consequence: at 45° the reported magnitude is 960 where the true one is 678.8, so diagonal edges clear a fixed threshold that axis-aligned edges of the same real strength do not. The symptom is an edge map that over-detects diagonals and looks orientation-biased for no visible reason.

**Calling `BGR2GRAY` output "luminance".** OpenCV documents it as $Y \leftarrow 0.299R + 0.587G + 0.114B$. <!-- L52 --> Those are the BT.601 luma weights, standardised for gamma-corrected signals and inherited from the 1953 NTSC primaries. <!-- L53 --> Applied to gamma-encoded values they give luma $Y'$, related to brightness but not CIE luminance. <!-- L55 --> The proof is on the same page: its RGB→XYZ matrix gives the luminance row as $0.212671, 0.715160, 0.072169$ <!-- L54 --> — a green weight of 0.715 against 0.587, for the quantity also written $Y$. Two numbers, one letter, one page. If a threshold depends on physical brightness, linearise first.

**Downscaling with the default interpolation.** `resize` defaults to `INTER_LINEAR`, while the docs recommend `INTER_AREA` for shrinking. <!-- L51 --> Bilinear interpolation reads a fixed handful of source pixels however far you shrink, so it does not prefilter — and stage 1 says the prefilter must precede the resample. <!-- L06 --> The symptom is moiré on textures and a threshold that moves when you change input resolution.

**Assuming scale-space guarantees from a sampled Gaussian.** OpenCV's Gaussian is the continuous kernel evaluated at integer points and normalised. <!-- L16 --> The discrete analogue satisfying the scale-space axioms is a different kernel, and the sampled version does not satisfy them. <!-- L17 --> Sampled kernels are reported to degrade worst at very fine scales <!-- L18 --> — including $\sigma = 0.8$, the default for a 3×3 window. If your algorithm depends on structures never being created as scale increases, or on two blurs composing into one, that is an assumption about a kernel that does not provide it.

**One non-mistake worth stating**, because the parameter looks like a bug and is not: `Canny`'s two thresholds may be passed in either order. The smaller is used for linking and the larger for seeding regardless. <!-- L32 -->

## Key takeaways

- **The four stages are ordered, and only the first destroys information.** Sampling runs before your code does, so every downstream fix is damage limitation. A prefilter must precede a resample; applied afterwards it removes nothing, because the aliased energy is already indistinguishable from signal. <!-- L06 -->
- **Three of the four stages are one operation.** Filtering, the transform that explains it, and the response step of every detector are all a weighted sum over a neighbourhood. Weights summing to 1 give an average, weights summing to 0 give a derivative, and the frequency view says which frequencies survive either.
- **An operator is a hypothesis about structure, and the median is a different kind of hypothesis.** Linear filters sum, so they can be transformed and analysed by frequency — and can never delete an impulse without disturbing its neighbours. Rank and morphological operators sort, so none of that analysis applies and the impulse goes exactly. Choosing between them is choosing what you claim about the corruption.
- **Every "optimal" operator here is optimal under conditions its name does not carry.** Canny assumes a 1-D step edge in additive white Gaussian noise <!-- L30 -->; Harris carries an empirical constant while an equivalent formulation has none <!-- L34 --> <!-- L35 -->; Perona–Malik is formally ill-posed and works anyway <!-- L48 -->. The conditions are the part worth reading.
- **The library is not the math, and the gaps are documented.** `filter2D` computes correlation <!-- L10 -->, `Canny` defaults to the L1 magnitude <!-- L31 -->, `BGR2GRAY` gives luma not luminance <!-- L52 --> <!-- L53 -->, and OpenCV's Gaussian is a sampled approximation missing the discrete scale-space axioms <!-- L17 -->. Each gap is in the official documentation, and each is invisible in the common case.

Figure 17 shows what this post covered and what it handed off.

![Tree diagram with the pillar post at the root and its child posts branching by stage: resampling and interpolation, kernel design, the 2-D DFT, wavelets, thresholding and segmentation, morphology, edge-preserving smoothing, Canny in detail, the structure tensor, scale space and SIFT, and colour and gamma](https://minio.canery.in/media/fig-17-series-map.png)

*Figure 17 — What this post deliberately does not cover. Each branch is a child post that goes deep on one area of the frame built here.*

## References

**Foundations and signal theory**

1. Shannon, C. E. "Communication in the Presence of Noise." *Proc. IRE* 37(1):10–21, 1949. [PDF](https://www.math.unl.edu/~bdeng1/Teaching/math943/Topics/Genetics/Shannon1949.pdf)
2. Cooley, J. W. and Tukey, J. W. "An Algorithm for the Machine Calculation of Complex Fourier Series." *Mathematics of Computation* 19:297–301, 1965. [PDF](https://www.ams.org/journals/mcom/1965-19-090/S0025-5718-1965-0178586-1/S0025-5718-1965-0178586-1.pdf)
3. Gonzalez, R. C. and Woods, R. E. *Digital Image Processing*, 4th ed. Pearson, 2018. [Contents](https://imageprocessingplace.com/downloads_V3/dip4e_downloads/dip4e_sample_book_material/dip4e_detailed_TOC.pdf)
4. Torralba, A., Isola, P. and Freeman, W. T. *Foundations of Computer Vision*, ch. 20, "Image Sampling and Aliasing." MIT Press. [Chapter](https://visionbook.mit.edu/sampling_and_aliasing.html) — accessed 2026-09-10
5. Mallat, S. "A Theory for Multiresolution Signal Decomposition: The Wavelet Representation." *IEEE TPAMI* 11(7):674–693, 1989. [DOI](https://doi.org/10.1109/34.192463)

**Operators and detectors**

6. Canny, J. "A Computational Approach to Edge Detection." *IEEE TPAMI* 8(6):679–698, 1986. [DOI](https://doi.org/10.1109/TPAMI.1986.4767851)
7. Marr, D. and Hildreth, E. "Theory of Edge Detection." *Proc. R. Soc. B* 207(1167):187–217, 1980. [Article](https://royalsocietypublishing.org/rspb/article/207/1167/187/33191/Theory-of-edge-detection)
8. Harris, C. and Stephens, M. "A Combined Corner and Edge Detector." *Proc. Alvey Vision Conference*, 147–151, 1988. [PDF](https://www.bmva-archive.org.uk/bmvc/1988/avc-88-023.pdf)
9. Sobel, I. "An Isotropic 3×3 Image Gradient Operator." 2014 retrospective of the 1968 Stanford AI Lab talk. [Record](https://www.researchgate.net/publication/281104656)
10. Jähne, B., Scharr, H. and Körkel, S. "Principles of Filter Design." *Handbook of Computer Vision and Applications*, vol. 2, 125–152. Academic Press, 1999. [Record](https://hci.iwr.uni-heidelberg.de/node/5375)
11. Hough, P. V. C. "Method and Means for Recognizing Complex Patterns." US Patent 3,069,654, 1962. [Patent](https://patents.google.com/patent/US3069654A/en)
12. Duda, R. O. and Hart, P. E. "Use of the Hough Transformation to Detect Lines and Curves in Pictures." *CACM* 15(1):11–15, 1972. [DOI](https://doi.org/10.1145/361237.361242)
13. Lowe, D. G. "Distinctive Image Features from Scale-Invariant Keypoints." *IJCV* 60(2):91–110, 2004. [PDF](https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf)

**Scale space, smoothing and segmentation**

14. Lindeberg, T. "Scale-Space for Discrete Signals." *IEEE TPAMI* 12(3):234–254, 1990. [Record](https://www.semanticscholar.org/paper/f306444acc81b0af1875e5633e921148cb3a8977)
15. Lindeberg, T. "Discrete Approximations of Gaussian Smoothing and Gaussian Derivatives." arXiv:2311.11317. **Preprint.** [arXiv](https://arxiv.org/abs/2311.11317)
16. Tomasi, C. and Manduchi, R. "Bilateral Filtering for Gray and Color Images." *ICCV'98*, 839–846. [PDF](https://users.soe.ucsc.edu/~manduchi/Papers/ICCV98.pdf)
17. Buades, A., Coll, B. and Morel, J.-M. "A Non-Local Algorithm for Image Denoising." *CVPR 2005*, II:60–65. [DOI](https://doi.org/10.1109/CVPR.2005.38)
18. Perona, P. and Malik, J. "Scale-Space and Edge Detection Using Anisotropic Diffusion." *IEEE TPAMI* 12(7):629–639, 1990. [PDF](https://www.math.uci.edu/~gpatrick/source/papers/G131.pdf)
19. Kichenassamy, S. "The Perona–Malik Paradox." *SIAM J. Appl. Math.* 57(5):1328–1342, 1997. [Record](https://www.academia.edu/43267662)
20. Otsu, N. "A Threshold Selection Method from Gray-Level Histograms." *IEEE TSMC* 9(1):62–66, 1979. [PDF](https://engineering.purdue.edu/kak/computervision/ECE661.08/OTSU_paper.pdf)
21. Vincent, L. and Soille, P. "Watersheds in Digital Spaces." *IEEE TPAMI* 13(6):583–598, 1991. [DOI](https://doi.org/10.1109/34.87344)
22. Serra, J. Course on Mathematical Morphology, ch. 2. Ecole des Mines de Paris. [PDF](https://smil.cmm.minesparis.psl.eu/publis/Cours-Serra/chap-02-en.pdf)
23. Zuiderveld, K. "Contrast Limited Adaptive Histogram Equalization." *Graphics Gems IV*, 474–485. Academic Press, 1994. [DOI](https://doi.org/10.5555/180895.180940)
24. Keys, R. G. "Cubic Convolution Interpolation for Digital Image Processing." *IEEE TASSP* 29(6):1153–1160, 1981. [PDF](http://www.ncorr.com/download/publications/keysbicubic.pdf)

**Implementation and colour**

25. OpenCV 4.13.0 documentation, Image Filtering. [Docs](https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html) — accessed 2026-09-10
26. OpenCV 4.13.0 documentation, Feature Detection. [Docs](https://docs.opencv.org/4.x/dd/d1a/group__imgproc__feature.html) — accessed 2026-09-10
27. OpenCV 4.13.0 documentation, Color conversions. [Docs](https://docs.opencv.org/4.x/de/d25/imgproc_color_conversions.html) — accessed 2026-09-10
28. OpenCV 4.13.0 documentation, Geometric Image Transformations. [Docs](https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html) — accessed 2026-09-10
29. ITU-R Recommendation BT.601-7, *Studio encoding parameters of digital television*. [PDF](https://www.itu.int/dms_pubrec/itu-r/rec/bt/R-REC-BT.601-7-201103-I!!PDF-E.pdf)
30. Poynton, C. *Colour FAQ* — luma versus luminance. Used for framing only. [Page](https://homepages.inf.ed.ac.uk/rbf/CVonline/LOCAL_COPIES/POYNTON1/ColorFAQ.html) — accessed 2026-09-10
