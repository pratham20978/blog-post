---
title: "Kernel Design: Separability, Borders, Optimised Derivatives"
slug: kernel-design-separability-borders-derivatives
date: 2026-09-25
updated: 2026-09-25
summary: "Every 3×3 derivative filter is one stencil with one free number. Where Scharr's 3, 10, 3 comes from, what truncating a Gaussian costs, and what borders do."
tags: [algorithms, image-processing, convolution, filter-design, image-gradient, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: advanced
series: image-processing
series_position: 4
prerequisites: ["the filter stage from Image Processing by Hand", "transfer functions of short kernels", "a second-order Taylor expansion", "reading Python signatures"]
reading_minutes: 31
cover_image_url: "COVER"
cover_image_alt: "A 3×3 derivative stencil whose two outer rows carry one free weight p, with Sobel, Scharr and Prewitt marked as values of p"
canonical_url: "https://canery.in/blogs/kernel-design-separability-borders-derivatives"
---

> [!NOTE]
> **Insights** — A kernel's numbers are the answer to a stated criterion, not a convention. Every 3×3 first-derivative filter — central difference, Sobel, Scharr, Prewitt, a sampled Gaussian derivative — is the same stencil with one free number, the weight p on the two neighbouring rows. Scharr's p = 3/16 keeps a gradient's direction within 0.3° on a 4-pixel pattern, where Sobel's 1/4 is 3.2° off; Sobel's larger p is instead the more robust of the two beside a bad pixel. The same accounting prices the rest of a kernel: a σ = 2 Gaussian cut to 3 taps has the spread of σ = 0.8, and OpenCV's default border makes every x-derivative on the edge column exactly zero.

**Level:** advanced · **You need:** the filter stage of [Image Processing by Hand](https://canery.in/blogs/image-processing-by-hand#stage-2--filter-every-linear-filter-is-one-weighted-sum), the transfer function of a short kernel, a second-order Taylor expansion, and enough Python to read a signature · **Time:** ~31 min

This is part 4 of *Image Processing by Hand*. The hub's filter stage showed that separable kernels save work and that the border rule is a decision. This part asks where a kernel's numbers come from, priced on the same 5×5 patch in grey levels and degrees.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Scharr's numbers](#where-do-scharrs-3-10-3-come-from) · [What "optimal" means](#what-does-optimal-mean-for-a-derivative) · [Separability](#when-does-a-kernel-split-into-1-d-passes) · [Taps for a Gaussian](#how-many-taps-does-a-gaussian-need) · [Borders](#what-does-the-border-do-to-a-derivative) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch; the arithmetic was cross-checked with plain Python using only its `math` module — no NumPy, OpenCV, SciPy or scikit-image call was executed. What each library does comes from its documentation and from reading its source at a pinned commit. There are no timings and no measured curves. The figures that draw curves or angular errors are evaluated from closed-form transfer functions and say so in the caption.

## Why this matters

You replace `cv2.Sobel` with `cv2.Scharr`, because the documentation says the Scharr aperture may give more accurate results. <!-- L35 --> Every edge in the pipeline now clears its threshold. On the patch's clean step of 160 grey levels, `Sobel` returns 640 and `Scharr` returns 2,560: both build their kernels from unnormalised integers, and the integers add up to different totals. <!-- L34 --> The accuracy you were promised is real. It is also not what changed your output.

You ask for a σ = 2 blur with `GaussianBlur(img, (3, 3), 2)` and get weights of 0.319, 0.362 and 0.319 — nearly a box, with the spread of σ = 0.8. You compute gradients up to the image border, and at one pixel of the patch's left column OpenCV's `Sobel` returns 0 while SciPy's returns 430, with the same stencil at the same scale.

None of these is a library bug. Each is a number inside a kernel — a cross-weight, a tap count, an invented pixel — that came from a criterion somebody chose. This post shows where each comes from, so that you choose it instead.

## The problem

A kernel is a handful of numbers, and three separate things decide them.

**Constraints** say what it must preserve. A smoother's weights sum to 1, so a flat region keeps its brightness. A first derivative's weights sum to 0, so a flat region gives zero, and they are scaled so that a ramp rising one grey level per pixel gives exactly 1. These **moment conditions** — rules on the weights' sum and first moment — fix a kernel's scale but not its shape. Libraries mostly ship **raw** integer kernels that skip the scaling, and the gap between raw and **normalised** is a factor you must know: 8 for Sobel, 32 for Scharr.

**The budget** says what it may cost: how many taps, and whether it splits into 1-D passes. **The criterion** says what it optimises: a gradient's direction, the agreement between a derivative and a smoother, a blur's mass or spread. Two kernels that meet the same constraints on the same budget differ only here, so a kernel called "optimal" without its criterion has told you nothing.

The constraints leave very little room. A 3×3 x-derivative should be antisymmetric left to right, since a derivative changes sign when the image is mirrored, and symmetric top to bottom. Antisymmetry forces the centre column to zero and the outer columns to be negatives of each other; symmetry makes the top and bottom rows match. Two numbers are left, and the unit-slope condition fixes their total. So every such kernel is

$$
K_x(p) \;=\; \begin{bmatrix} p \\ 1-2p \\ p \end{bmatrix} \cdot \frac{1}{2}\begin{bmatrix} -1 & 0 & 1 \end{bmatrix}
$$

one column times one row, with a single free number $p$. The row is a **central difference**, the right neighbour minus the left, halved. The column is a **cross-smoothing**, an average across the derivative's direction with weight $p$ on each neighbouring row. Every such kernel is this product for some $p$, so every one of them is separable. Figure 1 places the named ones on the line.

![Number line of the cross-weight p from 0 to 1/3 with the central difference, Scharr, Sobel, Prewitt and Gaussian stencils at their positions](FIG_01)

*Figure 1 — Seven derivative filters with separate names are one stencil with one free number. Scaled to slope 1 on a ramp, each is the column p, 1 − 2p, p times the central difference; only the position on this line differs.*

The central difference is $p = 0$; Scharr's aperture is 3/16, <!-- L10 --> Sobel's 1/4 <!-- L32 --> and Prewitt's 1/3. <!-- L43 --> A 3-tap sampled Gaussian derivative sits on the line too, since its derivative taps are always proportional to −1, 0, 1; at the series' σ = 0.8 its column is the shared [0.239, 0.522, 0.239], so $p = 0.239$. Farid and Simoncelli's 3-tap pair sits at 0.2299. <!-- L04 --> "Sobel or Scharr?" really asks "which $p$?"

A kernel also does not stop at its taps. At the image border the window hangs off the array and the library invents the missing values, so the border rule belongs to the design as much as $p$ does.

## Worked example

The patch is the series' 5×5 8-bit patch. Every row is `40 40 40 200 200` except r2, which has an impulse of 255 at (r2, c1):

```text
      c0   c1   c2   c3   c4
r0    40   40   40  200  200
r1    40   40   40  200  200
r2    40  255   40  200  200
r3    40   40   40  200  200
r4    40   40   40  200  200
```

### One derivative, every p

Evaluate the normalised family at two positions, the way its factors suggest: take the central difference along each of the window's three rows, then weight the results by $p$, $1 - 2p$ and $p$.

**At (r2, c3)**, on the clean step, every row gives (200 − 40)/2 = 80. Weights that sum to 1 leave an agreed value alone, so every member of the family outputs **80**. On a straight edge running along the cross-smoothing direction, $p$ is invisible.

**At (r2, c2)**, one column to the left, the window's left column holds the impulse. The rows give

- r1: (200 − 40)/2 = 80
- r2: (200 − 255)/2 = −27.5
- r3: (200 − 40)/2 = 80

and the output is $80p + (1 - 2p)(-27.5) + 80p$, which simplifies to

$$
G_x(p) = 80 - 107.5\,(1 - 2p)
$$

The clean value is 80, and the impulse pulls it down by 107.5 times the centre row's weight. Put in the named members:

| Filter | p | Output at (r2, c2) | Error against 80 |
|---|---|---|---|
| central difference | 0 | −27.5 | 134% |
| [1 4 1]/6 | 1/6 | 8.33 | 90% |
| Scharr | 3/16 | 12.81 | 84% |
| Farid–Simoncelli, 3-tap | 0.2299 | 21.92 | 73% |
| shared Gaussian, σ = 0.8 | 0.239 | 23.88 | 70% |
| Sobel | 1/4 | 26.25 | 67% |
| Prewitt | 1/3 | 44.17 | 45% |

The Sobel row is [the hub's 67% result](https://canery.in/blogs/image-processing-by-hand#why-the-filter-stage-has-to-come-first) — its raw 640 falling to 210 — seen as one point on a line. Figure 2 draws the line.

![The 3×3 window at (r2, c2) with row differences 80, −27.5 and 80, beside the line 80 − 107.5(1 − 2p) with named filters marked](FIG_02)

*Figure 2 — On the clean edge every value of p gives 80. Beside the impulse the output falls on a straight line in p, so the choice of filter decides between a 67% error (Sobel) and an 84% error (Scharr). Evaluated from the closed form.*

The more weight the neighbouring rows carry, the less one bad row can move the answer. Scharr, the better filter for direction, is the worse one here: "optimal" already pulls two ways.

The libraries return these numbers multiplied. OpenCV builds Sobel from the integers 1, 2, 1 and −1, 0, 1, and Scharr from 3, 10, 3 and −1, 0, 1, <!-- L32 --> <!-- L33 --> and normalises neither, <!-- L34 --> so at (r2, c3) `Sobel` returns 640 and `Scharr` 2,560. scikit-image normalises the smoothing factor but not the difference and divides its magnitude by √2, <!-- L43 --> <!-- L44 --> so its Sobel and Scharr give 160 along the axis and 113.1 as a magnitude. All of them mean a slope of 80 grey levels per pixel.

### Truncating a σ = 2 Gaussian

A Gaussian's weights never reach zero, so every implementation cuts them off. Sample $e^{-n^2/8}$, the σ = 2 Gaussian before normalising, at the integers:

| n | 0 | ±1 | ±2 | ±3 | ±4 | ±5 | ±6 |
|---|---|---|---|---|---|---|---|
| $e^{-n^2/8}$ | 1 | 0.8825 | 0.6065 | 0.3247 | 0.1353 | 0.0439 | 0.0111 |

Summed over all the integers these come to 5.0133, which is $\sigma\sqrt{2\pi}$ to four places. Cut at 3 taps, the kept samples sum to 1 + 2 × 0.8825 = 2.765, 55.2% of the total. Every implementation then divides by the kept sum so that a flat region stays flat, giving weights 0.319, 0.362 and 0.319. The image's brightness loses nothing. What is lost is spread: the renormalised kernel's variance is 2 × 0.319 × 1² = 0.638, against the σ² = 4 that was asked for.

| Taps | Mass kept before renormalising | Variance after | Effective σ |
|---|---|---|---|
| 3 | 55.2% | 0.638 | 0.80 |
| 5 | 79.4% | 1.663 | 1.29 |
| 7 | 92.3% | 2.693 | 1.64 |
| 13 | 99.90% | 3.951 | 1.99 |
| 17 | 100.00% | 3.999 | 2.00 |

The **effective σ** is the square root of the variance the kernel actually has — the blur you get. Three taps at σ = 2 is a σ = 0.8 blur, nearly a box; seven taps reach only 1.64. Figure 3 shows why the tail matters more than its mass: variance weights each sample by $n^2$.

![Bars of the sigma 2 Gaussian samples from minus 8 to 8 with brackets for 3, 5, 7 and 13 taps, and each window's kept mass and variance](FIG_03)

*Figure 3 — Renormalising keeps the mass; the variance is what truncation takes. At 7 taps the window already holds 92% of the weight but only two-thirds of the variance, because variance counts each sample by n². Sampled from the Gaussian's definition.*

The last two rows are the tap counts libraries choose for you; [Gaussian taps](#how-many-taps-does-a-gaussian-need) gives their rules.

<details>
<summary>Every weight after renormalising</summary>

Weights from the centre outwards; each kernel is symmetric.

| Taps | n = 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | Variance |
|---|---|---|---|---|---|---|---|---|---|---|
| 3 | 0.3617 | 0.3192 | | | | | | | | 0.638 |
| 5 | 0.2514 | 0.2218 | 0.1525 | | | | | | | 1.663 |
| 7 | 0.2161 | 0.1907 | 0.1311 | 0.0702 | | | | | | 2.693 |
| 9 | 0.2042 | 0.1802 | 0.1238 | 0.0663 | 0.0276 | | | | | 3.428 |
| 13 | 0.1997 | 0.1762 | 0.1211 | 0.0648 | 0.0270 | 0.0088 | 0.0022 | | | 3.951 |
| 17 | 0.1995 | 0.1760 | 0.1210 | 0.0648 | 0.0270 | 0.0088 | 0.0022 | 0.0004 | 0.0001 | 3.999 |

The variance is $\sum n^2 w_n$: for 5 taps, 2 × (0.2218 × 1 + 0.1525 × 4) = 1.663.

</details>

## Intuition

A kernel is a short stand-in for an ideal operator, and a short stand-in cannot be right at every frequency. The design question is where to put its error.

The ideal derivative multiplies a pattern of frequency ω, in radians per pixel, by ω. On a pattern $\sin(\omega x)$ the central difference returns $\sin\omega$ instead — short by a factor $\sin\omega/\omega$, the difference's **implicit smoothing**. It behaves like a true derivative followed by a blur along its own axis, reporting 90% of the slope at an 8-pixel wavelength, 64% at 4 pixels and nothing on the 2-pixel Nyquist pattern.

For one derivative that is a loss of gain; for a gradient it is a change of direction. Take stripes — a **plane wave**, one frequency at one orientation — whose gradient points at θ = 22.5°. Their frequency splits into ω cos θ along x and ω sin θ along y, and each gradient component is shrunk at its own frequency. The x component, at the higher frequency, shrinks more, so the vector turns towards y — by 7.2° at a 4-pixel wavelength. Figure 4 draws it.

![True gradient at 22.5° and its central-difference, Sobel and Scharr estimates at a 4-pixel wavelength, with each component's shrink factor](FIG_04)

*Figure 4 — The central difference shrinks x by 0.68 and y by 0.94, so the vector turns 7.2° towards y. Sobel's cross-smoothing over-corrects to −3.2°; Scharr's lands within 0.3°. A model plane wave at a 4-pixel wavelength, evaluated from the closed form.*

Cross-smoothing is the repair. The x-derivative's column shrinks the x component by a factor set by the y frequency, and the y-derivative mirrors it. If that factor equals the implicit smoothing, both components end up multiplied by the same product and the direction comes out right. Choosing $p$ is choosing how well that match holds, and over which frequencies.

An analogy: every flat map of the globe distorts something. Mercator keeps angles and inflates areas, and an equal-area projection keeps areas and bends angles, so you choose the projection by what you will measure on the map. Scharr's kernel is the angle-keeping projection for gradients, and a renormalised Gaussian is the area-keeping one for blur. The analogy breaks at where the distortion lives. A map's error is fixed by position on the globe; a kernel's error depends on the frequencies in the image. On a smooth image every kernel in this post is nearly exact, and the differences appear only at edges, fine texture and noise — which is where you were measuring.

## Where do Scharr's 3, 10, 3 come from?

In the frequency domain the central difference multiplies by $i\sin\omega$, which is the ideal $i\omega$ times the smoothing factor

$$
S(\omega) = \frac{\sin\omega}{\omega}
$$

and the cross-smoothing column multiplies by

$$
B_p(\omega) = (1 - 2p) + 2p\cos\omega
$$

Weickert and Scharr frame the argument in these terms: the central difference is a derivative plus a smoothing along its own axis, and keeping the gradient's direction needs a similar smoothing across it. <!-- L11 --> The estimate's x component is proportional to $`S(\omega_x) B_p(\omega_y)\,\omega_x`$ and its y component to $`S(\omega_y) B_p(\omega_x)\,\omega_y`$, so their ratio is the true one at every orientation exactly when $B_p = S$. No $p$ makes a cosine equal $\sin\omega/\omega$ everywhere; the question is where to make them agree.

**At long wavelengths.** For small ω, $S \approx 1 - \omega^2/6$ and $B_p \approx 1 - p\,\omega^2$, which agree to second order when $p = 1/6$: the column [1, 4, 1]/6, exact in the limit of a smooth image.

**At one wavelength.** Solving $B_p(\omega) = S(\omega)$ at a chosen ω gives the curves in Figure 5.

![sin ω / ω, the central difference's own smoothing, against cross-smoothing curves for p = 1/6, 3/16 and 1/4, with their crossing points](FIG_05)

*Figure 5 — Each p matches the difference's own smoothing at one wavelength: 1/6 in the smooth limit, 3/16 at 3.45 pixels, 1/4 at the 2-pixel Nyquist pattern, where both curves reach zero. Evaluated from the closed forms.*

The matching $p$ rises from 1/6 at long wavelengths to 0.182 at 4 pixels, exactly 3/16 at 3.45 pixels, and 1/4 at the 2-pixel pattern, where $S$ and $B_{1/4}$ both vanish. So Sobel's column is not arbitrary either: it matches the central difference at the one frequency where there is no direction left to get right.

**Over a band.** A real criterion fits the curves over a range of frequencies with a **weighting function** that says how much each frequency counts. The Weickert–Scharr report describes a weighted least-squares fit in the Fourier domain and gives [3, 10, 3]/16 as its outcome, <!-- L11 --> but not the weighting, and the answer depends on it. Minimising the root-mean-square (RMS) angular error over every orientation, the best $p$ here is 0.178 if frequencies up to half of Nyquist count equally, 0.192 if the whole band counts with weight $\cos^4(\omega/2)$, and 0.2375 if everything up to Nyquist counts equally. 3/16 = 0.1875 sits where the near-Nyquist frequencies, which most images carry mostly as noise, count for little; at that value $B$ stays within 2.2% of $S$ down to a 3.45-pixel wavelength. As integers over 32 the x-kernel is −3, 0, 3 over −10, 0, 10 over −3, 0, 3, <!-- L10 --> with only two distinct magnitudes, so two multiplications per pixel. <!-- L12 -->

Figure 6 shows what the choice does to direction at every orientation.

![Angular error against orientation at a 4-pixel wavelength for seven derivative filters, from 7.6° for Prewitt to 0.17° for a 5-tap pair](FIG_06)

*Figure 6 — Direction error at a 4-pixel wavelength: 7.2° for the central difference, 3.2° for Sobel, 0.29° for Scharr, all zero on the axes and the diagonal and largest near 22.5° and 67.5°. A model plane wave, evaluated from the closed-form transfer functions; not a measurement.*

| Worst error over orientation | 8 px | 4 px | 3 px |
|---|---|---|---|
| central difference | 1.54° | 7.22° | 15.49° |
| Prewitt | 1.56° | 7.64° | 17.71° |
| Sobel | 0.75° | 3.24° | 6.26° |
| [1 4 1]/6 | 0.03° | 0.64° | 2.64° |
| Scharr | 0.16° | 0.29° | 0.64° |

[1 4 1]/6 wins on smooth patterns and Scharr below a wavelength of about 4.7 pixels. Scharr stays under a third of a degree for every wavelength from 3.2 pixels up; Sobel is four to ten times worse throughout. Every curve has the same shape, zero on the axes and diagonals, because to leading order the error is proportional to $\sin 4\theta$ ([the math](#the-math)).

**A bigger Sobel is not a more isotropic one.** OpenCV builds larger Sobel apertures by convolving with 1, 1 repeatedly and then differencing, <!-- L32 --> so its 5×5 x-kernel — [1 4 6 4 1] down times [−1 −2 0 2 1] across — is the 3×3 Sobel convolved with the binomial [1 2 1] in both directions. That blur multiplies both gradient components by the same factor, so `ksize=5` turns the gradient exactly as much as `ksize=3`. It removes noise; it does not fix direction.

## What does "optimal" mean for a derivative?

Scharr's criterion is one answer. Three others are in print, and the worked example supplied a fourth.

**Farid and Simoncelli: a matched pair.** A derivative in any direction must equal the matching combination of the x and y derivatives — cos θ times one plus sin θ times the other — and they require the discrete filters to honour that. <!-- L02 --> With a separable design the x derivative is a 1-D derivative filter $d$ along x and a 1-D **prefilter** $p$ across it, <!-- L01 --> and the constraint reduces to one condition: $d$ must be the derivative of whatever $p$ leaves behind, $D(\omega) = i\omega P(\omega)$. They minimise that equation's error divided by the prefilter's energy, a **Rayleigh quotient** whose minimum is an eigenvector. <!-- L03 --> The result is a **matched pair**, where the derivative is exact for the signal as the prefilter reshapes it rather than for the original. <!-- L05 -->

Their 3-tap pair is a prefilter of 0.229879, 0.540242, 0.229879 with a derivative of ±0.425287; the 5-tap pair has prefilter 0.037659, 0.249153, 0.426375, 0.249153, 0.037659 and derivative 0.109604, 0.276691, 0, −0.276691, −0.109604. <!-- L04 --> Minimising their quotient over the 3-tap family here, in plain Python, gives 0.22984 and 0.42539, the published values to four places. So the 3-tap pair is a member of the family, at $p = 0.2299$, and its gain on a unit ramp is 2 × 0.4253 = 0.85: a Rayleigh quotient ignores scale, so the design fixes the prefilter's sum and lets the derivative's gain fall where the fit puts it. Direction is unaffected; magnitudes read 15% low. Figure 7 shows the matching the criterion asks for.

![Four plots of a derivative filter's response against ω times its prefilter's, for Sobel, Scharr and two Farid–Simoncelli pairs](FIG_07)

*Figure 7 — Farid and Simoncelli's criterion is that each pair of curves coincide: the derivative filter must be the derivative of its own prefilter. Sobel's pair parts early, Scharr's holds to mid-band, and the 5-tap matched pair holds almost to Nyquist. Evaluated from the published taps.*

Their criterion weights every frequency up to Nyquist equally, which is why its 3-tap optimum sits near the equal-weight angular optimum of 0.2375 rather than near Scharr's. Their 5-tap pair is the most isotropic filter in this post, at 0.17° worst for a 4-pixel wavelength and 0.06° at 3 pixels, and the authors report the same ranking from orientation estimates on synthetic gratings — their measurement, not one made here. <!-- L09 --> Non-separable designs gained them too little to justify the cost. <!-- L08 -->

**Ando: consistency.** Ando calls a gradient optimal when it gets the direction of any locally one-dimensional pattern exactly right, whatever its orientation, spectrum or sub-pixel position, and derives 3×3 to 5×5 operators from that. <!-- L25 -->

**The Gaussian derivative: a scale, not an accuracy.** Its σ says what size of structure you are differentiating, not how accurately. Its distinction is elsewhere: every rotation-invariant separable function is a Gaussian, <!-- L22 --> so it is the only kernel both cheap and the same in every direction, and Farid and Simoncelli note that requiring steerability would have forced it on them. <!-- L06 --> Its first derivative **steers** exactly — the derivative at angle θ is cos θ times the x-derivative plus sin θ times the y-derivative, so two filters cover every orientation. <!-- L21 --> That exactness belongs to the continuous kernel. Sampled on 5 taps at σ = 0.96, the value Farid and Simoncelli found best on their criterion, <!-- L07 --> it still errs by 1.4° at 4 pixels, and at 3 taps it is just the family again, with $p = 3/16$ at σ = 0.644. Below σ ≈ 0.75 Lindeberg finds sampled Gaussian derivatives numerically unreliable. <!-- L17 --> Choosing σ is Part 10's subject, *Scale Space and SIFT: Why σ Is a Search Dimension*.

**Robustness.** Beside a bad pixel a larger $p$ is better — 67% error for Sobel, 84% for Scharr — because a direction-tuned filter weights the centre row, where the impulse sits. Averaging that refuses to cross the bad pixel is Part 7's subject, *Edge-Preserving Smoothing: Bilateral, Non-Local Means, Anisotropic Diffusion*.

So "optimal" always means optimal for something: direction over a band (Scharr, the 5-tap matched pair), consistency (Ando), scale (the Gaussian) or robustness (a larger $p$). Name the measurement, and the $p$ follows.

## When does a kernel split into 1-D passes?

The hub showed that a separable kernel, a column times a row, costs $2k$ multiplications per pixel instead of $k^2$. <!-- L18 --> The question here is how to tell whether one separates, and what to do when it does not.

A kernel is separable exactly when it has **rank** 1: every row is a multiple of one row. Sobel's rows are −1, 0, 1 and −2, 0, 2 and −1, 0, 1 — one, two and one times the same row — so it separates, and the multipliers are its column. Every member of the derivative family passes by construction.

The 4-neighbour Laplacian does not. Its rows are 0, 1, 0 and 1, −4, 1 and 0, 1, 0, and the middle one is not a multiple of the others. It has rank 2, and it splits into two separable terms:

$$
\begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix}
= \begin{bmatrix} 0 \\ 1 \\ 0 \end{bmatrix} \begin{bmatrix} 1 & -2 & 1 \end{bmatrix}
+ \begin{bmatrix} 1 \\ -2 \\ 1 \end{bmatrix} \begin{bmatrix} 0 & 1 & 0 \end{bmatrix}
$$

A second difference along x plus the same along y: each term is a pair of 1-D passes, so a rank-2 kernel costs $4k$. At 3 taps that is 12 against 9 and the direct sum is cheaper; for a 9-tap Laplacian of Gaussian, which splits the same way because $\nabla^2 G = G''(x)G(y) + G(x)G''(y)$, it is 36 against 81. Treitel and Shanks gave the general version in 1971: any 2-D filter array expands into a finite sum of exactly separable stages, and when a few stages approximate it well the filter becomes cheap. <!-- L23 --> The rank says how many an exact split needs. Figure 8 shows the three cases.

![Sobel and Scharr as one column times one row, and the Laplacian as the sum of two column-times-row terms, each labelled with its rank](FIG_08)

*Figure 8 — A kernel separates exactly when every row is a multiple of one row. Sobel and Scharr have rank 1 and cost one pair of passes; the Laplacian has rank 2 and costs two.*

Separability is paid for in direction. A kernel built from a horizontal and a vertical profile treats axes and diagonals differently unless the profiles are chosen with care — Prewitt's box column errs by 7.6° on a 4-pixel pattern. Only one function is both separable and rotation-invariant: every rotation-invariant separable function of two variables is a Gaussian, or zero. <!-- L22 --> The box and the binomial are separable and anisotropic; the Gaussian is the one smoother that is both.

## How many taps does a Gaussian need?

### The rules libraries use

Given a ksize of zero, OpenCV's `GaussianBlur` takes round(σ × 3 × 2 + 1) taps for an 8-bit image and round(σ × 4 × 2 + 1) otherwise, forced odd — ±3σ or ±4σ. <!-- L30 --> SciPy's `gaussian_filter` samples to a radius of int(4σ + 0.5) and divides by the sum. <!-- L39 --> At σ = 2 that is 13, 17 and 17 taps: 99.90% of the mass and a variance of 3.95 at 13, all of both at 17. Lindeberg, where truncation must not matter, discards only about $10^{-8}$ of the mass, and notes that practical code can accept more. <!-- L19 -->

The trap is fixing both. `GaussianBlur(img, (3, 3), 2)` does exactly what it says — three taps sampled at σ = 2, an effective σ of 0.80 — and OpenCV's documentation recommends passing ksize, sigmaX and sigmaY together because its defaults interact. <!-- L31 --> Make them agree, with at least $2\lceil 3\sigma \rceil + 1$ taps.

### What OpenCV builds when σ is zero

For a non-positive σ the documentation gives σ = 0.3((ksize − 1) × 0.5 − 1) + 0.8, which is 0.8 at ksize 3, <!-- L28 --> and [the hub computed its 3×3 kernel](https://canery.in/blogs/image-processing-by-hand#the-gaussian) from that formula as 0.239, 0.522, 0.239. The source does something else. When σ ≤ 0 and ksize is 3, 5, 7 or 9, `getGaussianKernel` returns a hard-coded table: 0.25, 0.5, 0.25 at 3 taps, [1 4 6 4 1]/16 at 5, [2 7 14 18 14 7 2]/64 at 7 and a 9-tap row over 256. <!-- L26 --> Only other sizes use the formula. <!-- L27 --> The table is old — the 2.4 branch already had the 3-, 5- and 7-tap rows <!-- L29 --> — and undocumented.

So `GaussianBlur(img, (3, 3), 0)` is the binomial [1 2 1]/4, Sobel's smoothing column, with variance 0.5. The series' shared σ = 0.8 kernel is what `sigmaX=0.8` gives; its numbers stand for everything the series computed with them, and the correction is to the claim that it is the default. On the impulse the default gives 0.25 × 255 + 0.75 × 40 = 93.75, not 98.6. The tables' variances are close to the documented σ² without matching it: 0.5 against 0.64 at 3 taps, 1.0 against 1.21 at 5, 1.875 against 1.96 at 7, 2.75 against 2.89 at 9.

### Sampled, integrated and discrete Gaussians

Lindeberg compares three ways of putting a Gaussian on the grid.

- The **sampled** Gaussian takes the continuous values at the integers. At very fine scales they can sum to more than 1, and the variance falls well below σ²; <!-- L13 --> dividing by the sum repairs only the first. <!-- L14 -->
- The **integrated** Gaussian averages the continuous kernel over each pixel. It sums to 1, and its variance is too large by an amount approaching 1/12, a one-pixel box's variance. <!-- L15 -->
- The **discrete analogue**, $T(n; s) = e^{-s} I_n(s)$ with $`I_n`$ the modified Bessel function of integer order, has weights between 0 and 1 summing to 1, a variance of exactly $s = \sigma^2$, and the semigroup property: blurring by $s_1$ then $s_2$ is blurring by $s_1 + s_2$. <!-- L16 --> Lindeberg's 1990 argument is that discrete scale space should be built this way, from the diffusion equation rather than a sampled kernel. <!-- L20 -->

Figure 9 separates truncation from sampling for the series' kernel.

![Kernel variance over σ² against σ for sampled, 3-tap, integrated and discrete Gaussians, with OpenCV's σ = 0 tables and the shared kernel](FIG_09)

*Figure 9 — Truncation, not sampling, is what shrinks the shared kernel's variance to 0.478. Untruncated, the sampled σ = 0.8 kernel keeps 99.98% of its variance; cut to 3 taps it keeps 75%. Sampling alone costs under 3% of the variance from σ = 0.6 up. Evaluated from the definitions.*

At σ = 0.8 sampling alone is harmless: the untruncated sampled kernel has variance 0.6399. It fails only below that, by −14% at σ = 0.5, −50% at 0.4 and −92% at 0.3, where the raw samples also sum to 1.34. The shared kernel's 0.478 is a truncation effect: the ±2 taps it lacks hold 4.4% of the weight but, at $n^2 = 4$, over a quarter of the variance. The integrated kernel's variance at σ = 0.8 is 0.723; the discrete analogue's is exactly 0.640, with weights 0.583, 0.178, 0.028 and 0.003 from the centre out. Lindeberg puts the practical line near σ = 0.75: above it sampled kernels are fine, below it the discrete analogue is much better. <!-- L17 -->

## What does the border do to a derivative?

The hub's border figure showed five rules giving five values at one pixel. What matters for design is what each rule does to an operator, and a derivative shows it most sharply. Here is row r2 extended three pixels each way under OpenCV's five rules: <!-- L38 -->

```text
constant 0     0    0    0 |  40  255   40  200  200 |    0    0    0
replicate     40   40   40 |  40  255   40  200  200 |  200  200  200
reflect       40  255   40 |  40  255   40  200  200 |  200  200   40
reflect-101  200   40  255 |  40  255   40  200  200 |  200   40  255
wrap          40  200  200 |  40  255   40  200  200 |   40  255   40
```

**Reflect** mirrors and repeats the edge pixel, so c−1 is c0. **Reflect-101**, OpenCV's default, <!-- L38 --> mirrors about the edge pixel without repeating it, so c−1 is c1 — here the impulse. The normalised Sobel on the two edge columns:

| Position | constant 0 | replicate | reflect | reflect-101 | wrap |
|---|---|---|---|---|---|
| (r2, c0) | 73.75 | 53.75 | 53.75 | **0** | −26.25 |
| (r2, c4) | −100 | 0 | 0 | 0 | −80 |

Figure 10 lays out the rows that produce these numbers.

![Row r2 extended three pixels each way under five border rules, with the Sobel derivative at the left and right edge columns under each](FIG_10)

*Figure 10 — Five border rules, five derivatives at the same pixel. Reflect-101, OpenCV's default, gives exactly 0 on the edge column for any image; constant 0 and wrap invent edges that are not there. Worked by hand on row r2.*

**Reflect-101 zeroes every derivative normal to the border.** It makes the image symmetric about the edge pixel, so the value one step outside equals the value one step inside, and an antisymmetric kernel — every first derivative — cancels exactly: at (r2, c0) all three row differences are (c1 − c1)/2 = 0. That holds for any image. Under OpenCV's default the x-derivative on the left and right columns and the y-derivative on the top and bottom rows are always zero, so a gradient crossing the border at an angle turns parallel to the edge there.

**Constant 0 invents an edge at every border.** At (r2, c4) the flat 200 runs into black and the derivative reports a step of −100. Smoothers suffer too: the 13-tap σ = 2 Gaussian on a flat 40 returns 24.0 on the edge column, 31.0 one pixel in and 14.4 in a corner.

**Wrap invents an edge from the far side.** At (r2, c4) it reads c0's 40 as the next pixel and reports −80, as large as the real step. Wrap is the border the DFT assumes, and OpenCV's `Sobel`, `Scharr`, `GaussianBlur`, `filter2D` and `sepFilter2D` all refuse it. <!-- L37 --> The symmetric extensions have transforms of their own: each discrete cosine or sine transform corresponds to one kind of symmetric extension, the counterpart of the DFT and circular convolution. <!-- L24 -->

**Replicate and reflect agree at 3 taps and nowhere wider.** Both put c0 at c−1; at c−2 replicate repeats 40 while reflect reads c1's 255, so any 5-tap kernel tells them apart. None of the five keeps a ramp's slope on the edge column. NumPy's **odd** reflection does, by continuing the signal linearly: 1 2 3 4 5 padded as −1 0 before the 1. <!-- L42 -->

The names do not travel between libraries:

| Extension | OpenCV | SciPy `ndimage` | NumPy `pad` |
|---|---|---|---|
| repeat the edge pixel (half-sample): c b a ‖ a b c | `BORDER_REFLECT` | `'reflect'` (its default) | `'symmetric'` |
| mirror about it (whole-sample): c b ‖ a b c | `BORDER_REFLECT_101` (its default) | `'mirror'` | `'reflect'` |

`'reflect'` means one extension in SciPy and the other in NumPy, <!-- L40 --> and the defaults differ: OpenCV uses reflect-101, SciPy and scikit-image's edge filters SciPy's reflect. <!-- L44 --> SciPy's `sobel` is −1, 0, 1 across and 1, 2, 1 along, unnormalised like OpenCV's, <!-- L41 --> so the same image gives 0 in OpenCV and 8 × 53.75 = 430 in SciPy at (r2, c0).

## The math

| Symbol | Meaning | Units |
|---|---|---|
| $p$ | cross-weight on each neighbouring row | — |
| ω, θ | a plane wave's frequency and the direction of its gradient | radians per pixel, degrees |
| $S(\omega)$ | the central difference's implicit smoothing, $\sin\omega/\omega$ | — |
| $B_p(\omega)$ | the cross-smoothing's transfer function | — |
| $P, D$ | a prefilter's and a derivative filter's transfer functions | — |
| σ, $s$ | a Gaussian's standard deviation and variance, $s = \sigma^2$ | pixels, pixels² |
| $T(n; s)$ | the discrete analogue of the Gaussian | — |

**The family.** The normalised x-derivative with cross-weight $p$ has the transfer function

$$
\hat K_x(\omega_x, \omega_y) = i\sin\omega_x \cdot B_p(\omega_y), \qquad B_p(\omega) = 1 - 2p\,(1 - \cos\omega) \tag{1}
$$

The first factor is the central difference and the second the cross-smoothing; $`\hat K_y`$ swaps the arguments.

**Direction.** For a plane wave whose frequency vector is ω(cos θ, sin θ), the estimated gradient angle φ satisfies

$$
\tan\varphi = \tan\theta \cdot \frac{S(\omega\sin\theta)\, B_p(\omega\cos\theta)}{S(\omega\cos\theta)\, B_p(\omega\sin\theta)} \tag{2}
$$

The direction is exact at every θ when $B_p = S$, and at 0°, 45° and 90° for any $p$. To leading order in ω,

$$
\varphi - \theta \approx \frac{\omega^2}{4}\left(\frac{1}{6} - p\right)\sin 4\theta \tag{3}
$$

So $p = 1/6$ removes the error to second order, and any other member's error peaks at 22.5° and 67.5°. At an 8-pixel wavelength, ω = π/4, equation (3) gives 1.47° for the central difference against the exact 1.54°, and −0.74° for Sobel against −0.75°.

<details>
<summary>Deriving equation (3)</summary>

Write $u = \omega\cos\theta$ and $v = \omega\sin\theta$. For small arguments $S(u) \approx 1 - u^2/6$ and $B_p(v) \approx 1 - p\,v^2$, so the ratio in equation (2) is

$$
\frac{1 - v^2/6 - p\,u^2}{1 - u^2/6 - p\,v^2} \approx 1 + (u^2 - v^2)\left(\frac16 - p\right) = 1 + \omega^2\cos 2\theta\left(\frac16 - p\right)
$$

Call the correction ε, so $\tan\varphi = \tan\theta\,(1 + \varepsilon)$. For small ε, $\varphi \approx \theta + \varepsilon\sin\theta\cos\theta = \theta + \tfrac{\varepsilon}{2}\sin 2\theta$, and $\tfrac12\,\omega^2\cos 2\theta\,\sin 2\theta\,(\tfrac16 - p) = \tfrac{\omega^2}{4}\,(\tfrac16 - p)\sin 4\theta$. With $p = 0$ the error is positive, so the central difference turns the gradient towards y, as Figure 4 shows.

</details>

**The matched pair.** Farid and Simoncelli minimise

$$
E(P, D) = \frac{\int \lvert\, i\omega P(\omega) - D(\omega) \,\rvert^2 \, d\omega}{\int \lvert P(\omega) \rvert^2 \, d\omega} \tag{4}
$$

over the prefilter and derivative taps. <!-- L02 --> For the 3-tap family $P = B_p$ and $D = 2d\,i\sin\omega$. Scaling $P$ and $D$ together leaves $E$ unchanged, which is why the ramp gain is left at $2d = 0.85$.

**The discrete analogue.**

$$
T(n; s) = e^{-s} I_n(s), \qquad \sum_n T(n; s) = 1, \qquad \sum_n n^2\, T(n; s) = s \tag{5}
$$

At $s = 0.64$, $I_0 = 1.1051$ and $I_1 = 0.3367$, times $e^{-0.64} = 0.5273$, give the text's 0.583 and 0.178. <!-- L16 -->

**The border.** Reflect-101 makes the row even about the edge pixel, $f(-n) = f(n)$. A first-derivative kernel is odd, $d(-n) = -d(n)$, and $d(0) = 0$, so on the edge pixel

$$
\sum_n d(n)\, f(n) = \sum_{n > 0} d(n)\,\big(f(n) - f(-n)\big) = 0 \tag{6}
$$

That is the zero in Figure 10's reflect-101 column, for any image and any odd kernel.

## Implementation: the tooling map

Every call below maps to the arithmetic above. **None of it was executed for this post**; the mapping comes from documentation and from source at a pinned commit. Figure 11 is the same map in one picture.

![Grid of derivative and Gaussian calls in OpenCV, SciPy, NumPy and scikit-image with weights, raw scale, default border and a gotcha](FIG_11)

*Figure 11 — The same kernel name means different weights, scales and borders in four libraries. None of it was executed for this post; every cell comes from documentation or from source at a pinned commit.*

### OpenCV

| Want | Call | What it builds | Gotcha |
|---|---|---|---|
| 3×3 derivative | `cv2.Sobel(img, cv2.CV_32F, 1, 0, ksize=3)` | 1, 2, 1 times −1, 0, 1; raw, ×8 <!-- L32 --> <!-- L34 --> | $p = 1/4$; `ksize=5` and 7 add blur, not isotropy |
| isotropic 3×3 | `cv2.Scharr(img, cv2.CV_32F, 1, 0)` | 3, 10, 3 times −1, 0, 1; raw, ×32 <!-- L33 --> <!-- L35 --> | four times Sobel's output; rescale thresholds |
| the factors | `cv2.getDerivKernels(1, 0, ksize, normalize=True)` | both 1-D factors, scaled to unit slope <!-- L36 --> | `ksize=-1` gives Scharr's |
| Gaussian blur | `cv2.GaussianBlur(img, ksize, sigmaX, sigmaY)` | sampled and renormalised; ksize 0 means round(6σ + 1) for 8-bit, round(8σ + 1) otherwise <!-- L30 --> | σ = 0 with ksize 3 to 9 is a fixed table <!-- L26 --> |
| Gaussian weights | `cv2.getGaussianKernel(ksize, sigma)` | the same 1-D weights <!-- L27 --> | the documented σ-from-ksize rule is not what runs for small ksize <!-- L28 --> |
| two passes | `cv2.sepFilter2D(img, ddepth, kx, ky)` | any rank-1 kernel | `BORDER_WRAP` is refused <!-- L37 --> |
| border | `borderType=` on all of the above | default `BORDER_REFLECT_101` <!-- L38 --> | first derivatives are 0 on the edge column |

### SciPy, NumPy and scikit-image

| Library | Call | Kernel | Default border | Gotcha |
|---|---|---|---|---|
| SciPy | `ndimage.sobel(img, axis)` | −1, 0, 1 times 1, 2, 1; raw, ×8 <!-- L41 --> | `'reflect'`, half-sample <!-- L40 --> | 430 at (r2, c0) where OpenCV gives 0 |
| SciPy | `ndimage.gaussian_filter(img, sigma)` | radius int(4σ + 0.5), sampled, renormalised <!-- L39 --> | `'reflect'` | 17 taps at σ = 2 |
| NumPy | `np.pad(a, n, mode)` | — | — | `'reflect'` is whole-sample, `'symmetric'` half-sample; `reflect_type='odd'` extends a ramp <!-- L42 --> |
| scikit-image | `filters.sobel`, `scharr`, `prewitt`, `farid` | $p$ = 1/4, 3/16, 1/3, and Farid–Simoncelli's 5-tap pair <!-- L43 --> | `'reflect'` <!-- L44 --> | ×2 per axis; the magnitude is divided by √2 |

### Read a kernel back

When documentation and source disagree, as over the σ = 0 table, ask the function. Filter one bright pixel in a field of zeros and the output is the kernel, mirrored through its centre — the hub's point about correlation.

```python
import numpy as np, cv2

impulse = np.zeros((7, 7), np.float64)
impulse[3, 3] = 1.0                                  # one bright pixel in a zero field

blur = cv2.GaussianBlur(impulse, (3, 3), 0)          # expected centre row: 0.125 0.25 0.125
print(blur[2:5, 2:5])                                # the table's [1 2 1]/4, not 0.239 0.522 0.239

gx = cv2.Sobel(impulse, cv2.CV_64F, 1, 0, ksize=3)   # the Sobel stencil, mirrored left to right
print(gx[2:5, 2:5] / 8)                              # divide by 8 for the normalised form
```

This was not run for this post. The zero field keeps the border out of the answer while the kernel fits inside the array. The same test recovers `scipy.ndimage`'s and `skimage.filters`' weights and scale, and lighting an edge pixel instead recovers the border rule.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** switching derivative operators, or libraries, without rescaling. `cv2.Sobel` returns 8 times the slope, `cv2.Scharr` 32 times, scikit-image's per-axis filters 2 times, with its magnitude divided by √2 on top. A threshold tuned on one is off by up to a factor of 4 on another, and the edge map suddenly fills or empties. Normalise once — `getDerivKernels(..., normalize=True)`, or divide by the gain on a unit ramp — and threshold in grey levels per pixel.

- **Passing a ksize too small for σ.** `GaussianBlur(img, (3, 3), 2)` has an effective σ of 0.80 and is nearly a box. Use at least $2\lceil 3\sigma \rceil + 1$ taps, or pass `(0, 0)` and let the library size it.
- **Trusting the documented σ for small default kernels.** With `sigmaX=0` and ksize 3 to 9, OpenCV uses a fixed table whose spread is not the documented σ. Pass σ explicitly when the number matters.
- **Measuring gradients on the border column.** Under reflect-101 the normal derivative there is always 0; under constant 0 or wrap it is invented. Crop by the kernel's radius before measuring, or choose the border rule for the measurement.
- **Porting a border mode by its name.** SciPy's `'reflect'` is OpenCV's `BORDER_REFLECT` and NumPy's `'symmetric'`; NumPy's `'reflect'` is the other one.
- **Expecting a bigger Sobel to fix direction.** `ksize=5` smooths more and turns the gradient exactly as much as `ksize=3`. For direction use Scharr, or the 5-tap matched pair.
- **Sampled derivatives at very small σ.** Below about σ = 0.75, sampled Gaussian derivatives are unreliable, and the discrete analogue with central differences is the better tool. <!-- L17 -->
- **Beyond this post:** no linear kernel stops averaging at an edge, whatever its numbers — that is Part 7, *Edge-Preserving Smoothing*; which σ to use is Part 10, *Scale Space and SIFT*.

## Key takeaways

- **Every 3×3 first derivative is one stencil with one free number.** Scaled to unit slope it is p, 1 − 2p, p down times half of −1, 0, 1: central difference 0, Scharr 3/16, Sobel 1/4, Prewitt 1/3. Choosing an operator is choosing $p$.
- **"Optimal" names a criterion.** Scharr's $p$ keeps direction within 0.3° at a 4-pixel wavelength where Sobel is 3.2° off; Sobel's larger $p$ is more robust beside a bad pixel; Farid–Simoncelli match the derivative to its prefilter; the Gaussian buys scale and exact steering.
- **Truncation takes variance, not mass.** A σ = 2 Gaussian at 3 taps is a σ = 0.80 blur, and 7 taps reach only 1.64. OpenCV's σ = 0 small kernels are a fixed table, not the documented σ.
- **The border is part of the kernel.** OpenCV's default reflect-101 makes the normal derivative on the edge 0, constant 0 and wrap invent edges, and `'reflect'` names different extensions in SciPy and NumPy.

## References

1. Farid, H., and Simoncelli, E. P. "Differentiation of Discrete Multidimensional Signals." *IEEE Transactions on Image Processing* 13(4):496–508, 2004. doi:10.1109/TIP.2004.823819. [PDF](https://farid.berkeley.edu/downloads/publications/tip04.pdf) (accessed 2026-09-25)
2. Weickert, J., and Scharr, H. "A Scheme for Coherence-Enhancing Diffusion Filtering with Optimized Rotation Invariance." Technical Report 4/2000, Computer Science Series, University of Mannheim, 2000; revised and shortened in *Journal of Visual Communication and Image Representation* 13(1–2):103–118, 2002, doi:10.1006/jvci.2001.0495. [Report](https://www.mia.uni-saarland.de/weickert/Papers/TR-4-00.ps.gz) (accessed 2026-09-25)
3. Lindeberg, T. "Discrete Approximations of Gaussian Smoothing and Gaussian Derivatives." *Journal of Mathematical Imaging and Vision* 66(5):759–800, 2024. doi:10.1007/s10851-024-01196-9. [arXiv:2311.11317](https://arxiv.org/abs/2311.11317) (accessed 2026-09-25)
4. Lindeberg, T. "Scale-Space for Discrete Signals." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 12(3):234–254, 1990. [doi:10.1109/34.49051](https://doi.org/10.1109/34.49051) (accessed 2026-09-25)
5. Freeman, W. T., and Adelson, E. H. "The Design and Use of Steerable Filters." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 13(9):891–906, 1991. doi:10.1109/34.93808. [PDF](https://people.csail.mit.edu/billf/publications/Design_and_Use_of_Steerable_Filters.pdf) (accessed 2026-09-25)
6. Kannappan, P., and Sahoo, P. K. "Rotation Invariant Separable Functions are Gaussian." *SIAM Journal on Mathematical Analysis* 23(5):1342–1351, 1992. [doi:10.1137/0523076](https://doi.org/10.1137/0523076) (accessed 2026-09-25)
7. Treitel, S., and Shanks, J. L. "The Design of Multistage Separable Planar Filters." *IEEE Transactions on Geoscience Electronics* 9(1):10–27, 1971. [doi:10.1109/TGE.1971.271457](https://doi.org/10.1109/TGE.1971.271457) (accessed 2026-09-25)
8. Martucci, S. A. "Symmetric Convolution and the Discrete Sine and Cosine Transforms." *IEEE Transactions on Signal Processing* 42(5):1038–1051, 1994. [doi:10.1109/78.295213](https://doi.org/10.1109/78.295213) (accessed 2026-09-25)
9. Ando, S. "Consistent Gradient Operators." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 22(3):252–265, 2000. [doi:10.1109/34.841757](https://doi.org/10.1109/34.841757) (accessed 2026-09-25)
10. OpenCV source, `modules/imgproc/src/smooth.dispatch.cpp`, commit bed6800. <https://github.com/opencv/opencv/blob/bed6800f056e57f6c945a7bd56e324e0fa965e24/modules/imgproc/src/smooth.dispatch.cpp> (accessed 2026-09-25)
11. OpenCV source, `modules/imgproc/src/deriv.cpp`, commit bed6800. <https://github.com/opencv/opencv/blob/bed6800f056e57f6c945a7bd56e324e0fa965e24/modules/imgproc/src/deriv.cpp> (accessed 2026-09-25)
12. OpenCV 4.x documentation. "Image Filtering" — `Sobel`, `Scharr`, `getDerivKernels`, `getGaussianKernel`, `GaussianBlur`, `filter2D`, `sepFilter2D`. <https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html> (accessed 2026-09-25)
13. OpenCV 4.x documentation. "Core functionality" — `BorderTypes`. <https://docs.opencv.org/4.x/d2/de8/group__core__array.html> (accessed 2026-09-25)
14. OpenCV source, 2.4 branch, `modules/imgproc/src/smooth.cpp`. <https://github.com/opencv/opencv/blob/2.4/modules/imgproc/src/smooth.cpp> (accessed 2026-09-25)
15. SciPy source, `scipy/ndimage/_filters.py`, commit 0aed216. <https://github.com/scipy/scipy/blob/0aed21639223d28e32bc0320a2b70767b14b432d/scipy/ndimage/_filters.py> (accessed 2026-09-25)
16. SciPy documentation. `scipy.ndimage.gaussian_filter` and the `mode` parameter. <https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html> (accessed 2026-09-25)
17. NumPy documentation. `numpy.pad`. <https://numpy.org/doc/stable/reference/generated/numpy.pad.html> (accessed 2026-09-25)
18. scikit-image source, `src/_skimage2/filters/edges.py`, commit 533b769. <https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/filters/edges.py> (accessed 2026-09-25)
