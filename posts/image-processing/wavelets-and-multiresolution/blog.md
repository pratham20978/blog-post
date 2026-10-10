---
title: "Wavelets and Multiresolution: Haar, Lifting, JPEG 2000"
slug: wavelets-and-multiresolution
date: 2026-10-10
updated: 2026-10-10
summary: "A wavelet transform keeps the position that Fourier gives up. Worked on a 5×5 patch: Haar and 5/3 lifting, JPEG 2000's integer path, shift variance, denoising."
tags: [algorithms, image-processing, wavelets, signal-processing, image-compression, denoising]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: advanced
series: image-processing
series_position: 6
prerequisites: ["the 2-D DFT and its spectrum from part 5 of this series", "the Laplacian pyramid from part 2", "transfer functions and the convolution theorem", "reading Python signatures"]
reading_minutes: 34
cover_image_url: "COVER"
cover_image_alt: "A 6×6 grid split into four tinted 3×3 quadrants, one tangerine cell lit in each, against a band of 25 equal grey cells"
canonical_url: "https://canery.in/blogs/wavelets-and-multiresolution"
---

> [!NOTE]
> **Insights** — A wavelet transform records how much of a wave an image holds *and where*, by asking at every position and every scale how far a sample is from what its neighbours predict. On the series' 5×5 patch, the bright pixel that the 2-D DFT spread across all 25 bins at 215 each lands in four Haar coefficients of 107.5, a quarter of its energy apiece. Computed by lifting, the transform keeps exactly one number per pixel, where the Laplacian pyramid keeps 4/3, and inverts exactly in integers, which is how JPEG 2000 codes losslessly. The price is shift variance: move the patch's edge one pixel and the Haar detail that held it drops from 160 to 0.

**Level:** advanced · **You need:** *The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering* (part 5 of this series), the pyramid section of *The Laplacian by Hand* (part 2), transfer functions, and enough Python to read a signature · **Time:** ~34 min

This is part 6 of *Image Processing by Hand*. Part 5 ended where one global basis cannot say where a frequency occurs; this part trades it for short waves at every scale, works one level by hand two ways, and counts what the trade buys and costs.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [One level in 2-D](#what-does-one-level-do-to-an-image) · [Which wavelet](#which-wavelet-vanishing-moments-and-the-frequency-response) · [Lifting and JPEG 2000](#lifting-how-jpeg-2000-gets-integers-back-exactly) · [Shift variance](#what-does-the-decimated-transform-get-wrong) · [Denoising](#denoising-by-shrinking-coefficients) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch, its rows and its transpose, and cross-checked with plain Python using only its `math` and `cmath` modules; that check is not published. No PyWavelets, scikit-image, OpenJPEG or Pillow call was executed: library behaviour comes from source read at a pinned commit. There are no timings or measured curves. Frequency responses are evaluated from closed forms, and compression comparisons are quoted from the studies that measured them.

## Why this matters

JPEG cuts an image into 8×8 blocks and transforms each one on its own, <!-- L01 --> so at low bit rates the block grid shows through. JPEG 2000 transforms whole tiles with a wavelet, and a tile can be the entire image; <!-- L02 --> the blocking artefacts went with the blocks. <!-- L03 --> The same transform sits under classical denoisers: scikit-image's `denoise_wavelet` thresholds Haar coefficients by default. <!-- L50 -->

Each looks arbitrary until you know what one coefficient means. `pywt.dwt` returns six numbers for a five-sample row, and ten if you ask for the wavelet JPEG 2000 uses losslessly. <!-- L13 --> <!-- L14 --> A soft-thresholding denoiser takes the same amount off every edge it keeps, and a one-pixel shift can zero a whole band of coefficients. This post computes all three on the series' patch.

## The problem

Part 5's DFT put the patch's impulse, one pixel of 255 among 40s at (r2, c1), into all 25 coefficients with magnitude exactly 215; its position survived only as a phase ramp. Every Fourier basis function covers the whole image, so a feature that occupies one pixel occupies the whole spectrum.

Cutting the image into blocks, as JPEG does with 8×8, localises at one size only. <!-- L01 --> An *n*-point DFT puts its frequencies 1/*n* cycles per pixel apart: 0.125 for an 8-sample block, 0.016 for a 64-sample one. The short block knows where an edge is but barely separates slow gradients; the long block resolves the gradients and loses the edge. Images want both. Fine detail needs short support to say *where*; slow shading needs long support to say *what*.

Part 2's Laplacian pyramid already makes that trade one octave at a time, but it stores 4/3 as many numbers as the image has pixels in 2-D and twice as many in 1-D, <!-- L05 --> its levels are correlated with each other, and it does not separate orientations. <!-- L06 --> So the requirements are four.

1. **Local:** an impulse touches a few coefficients.
2. **Multiscale:** short functions for fine detail, long ones for coarse structure.
3. **Critically sampled:** exactly as many coefficients as pixels.
4. **Exactly invertible**, ideally integers to integers, so a lossless codec can use it.

A **wavelet transform** meets all four. A *wavelet* is a short oscillation whose weights sum to zero, like the Laplacian's, at one position and one scale. Mallat's **multiresolution analysis** made the transform an algorithm: split the signal into a half-resolution approximation and the detail lost in halving, then repeat on the approximation with the same pair of filters. <!-- L07 --> The worked example computes one level by hand, twice.

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

Start with the top row, r0: a step of 160 between c2 and c3.

### One Haar level, by lifting

The **Haar wavelet** is the oldest orthonormal wavelet basis, from Haar's 1910 paper: <!-- L26 --> each pair of samples becomes its average and its difference. Computing it by **lifting** takes three steps, and the same three steps will compute JPEG 2000's wavelet next. <!-- L16 -->

1. **Split** the row into even and odd samples: evens c0, c2, c4 are 40, 40, 200; odds c1, c3 are 40, 200.
2. **Predict** each odd sample from its even neighbour on the left, and keep the error. That error is the **detail coefficient**: $d_0 = 40 - 40 = 0$ and $d_1 = 200 - 40 = 160$.
3. **Update** each even sample by half its detail, so that it becomes the pair's average. That average is the **coarse** (approximation) coefficient: $s_0 = 40 + 0 = 40$ and $s_1 = 40 + 80 = 120$.

c4 has no partner, so it passes through as $s_2 = 200$, as if paired with a copy of itself. Five samples became five numbers: coarse 40, 120, 200, the row at half resolution, and detail 0, 160. The flat pair costs nothing; the pair straddling the step costs exactly the step. The inverse runs the steps backwards: each even sample is $s - d/2$, then each odd sample is that plus $d$.

### The same row through the 5/3

JPEG 2000's reversible wavelet, the **5/3** (after its 5-tap and 3-tap filters), predicts each odd sample from *both* neighbours, and rounds: <!-- L04 --> <!-- L08 -->

$$
d_k = x_{2k+1} - \left\lfloor \frac{x_{2k} + x_{2k+2}}{2} \right\rfloor, \qquad
s_k = x_{2k} + \left\lfloor \frac{d_{k-1} + d_k + 2}{4} \right\rfloor
$$

Here $x$ is the row, $d_k$ the detail at odd position $2k+1$, $s_k$ the coarse value at even position $2k$, and $\lfloor\cdot\rfloor$ rounds down. Missing neighbours at the ends come from mirroring the row about its end samples, which are not repeated (beyond c4 come c3, c2, …): the **whole-sample symmetric extension** JPEG 2000 specifies. <!-- L09 -->

- **Predict:** $d_0 = 40 - \lfloor (40 + 40)/2 \rfloor = 0$ and $d_1 = 200 - \lfloor (40 + 200)/2 \rfloor = 200 - 120 = 80$.
- **Update:** $s_0 = 40 + \lfloor (0 + 0 + 2)/4 \rfloor = 40$, $s_1 = 40 + \lfloor (0 + 80 + 2)/4 \rfloor = 60$ and $s_2 = 200 + \lfloor (80 + 80 + 2)/4 \rfloor = 240$, the mirror supplying the missing detail at each end.

| | coarse $s$ | detail $d$ |
|---|---|---|
| Haar | 40, 120, 200 | 0, 160 |
| 5/3 | 40, 60, 240 | 0, 80 |

OpenJPEG's forward row code performs exactly these two steps, with the same mirror at the ends. <!-- L10 --> Figure 1 lays both computations side by side.

![Row 40 40 40 200 200 split into evens and odds, then predicted and updated by Haar and by the 5/3, giving details 0, 160 and 0, 80](FIG_01)

*Figure 1 — One level of the top row, two ways. Haar predicts each odd sample from its left neighbour and pays the whole step, 160; the 5/3 predicts from both neighbours and pays half, 80. The 5/3's coarse 240 is its low-pass overshooting beside the mirrored step. Worked by hand.*

Two differences carry the rest of the post. The step costs the 5/3 half what it costs Haar, because the 5/3 predicts an odd sample as the midpoint of its neighbours: a straight line between them costs nothing, and a step costs half its height. And the 5/3's coarse row is not a block average. Its analysis low-pass filter is (−1, 2, 6, 2, −1)/8, <!-- L11 --> and at c4 it sees the mirrored neighbourhood 40, 200, [200], 200, 40: (−40 + 400 + 1,200 + 400 − 40)/8 = 240. The negative outer taps overshoot beside a jump, 40 grey levels past the brightest pixel in the row.

The inverse undoes the update, then the prediction, with the same rounding: $x_0 = 40$, $x_2 = 60 - 20 = 40$, $x_4 = 240 - 40 = 200$, then $x_1 = 0 + 40$ and $x_3 = 80 + 120 = 200$. The integers come back exactly, because each step added a rounded function of the *other* half of the samples, which the inverse can recompute before it needs it.

### The coefficient budget

Both levels kept 5 numbers for 5 samples: the detail is stored only at odd positions, and the evens become the coarse signal rather than being stored again. A pyramid stores the prediction error at *every* sample. One level of Part 2's Laplacian pyramid on this row keeps the five-sample difference plus the three-sample reduced row, 8 numbers, and the full pyramid 5 + 3 + 2 + 1 = 11. For long signals that ratio tends to 2 in 1-D and 4/3 in 2-D; the wavelet transform's stays at 1. <!-- L05 -->

Libraries do not all keep the count. In its default mode PyWavelets returns $\lfloor (N + L - 1)/2 \rfloor$ coefficients per band for a filter of length $L$, and $\lceil N/2 \rceil$ only in `periodization` mode. <!-- L13 --> Its Haar has 2 taps, `bior2.2` (the 5/3 × √2) 6 and `bior4.4` (JPEG 2000's 9/7 × √2) 10, <!-- L14 --> so the row comes back as 6, 10 or 14 coefficients and the patch as 36, 100 or 196. The padding fades with size, to 2.3% for `bior4.4` on a 1920×1080 frame at five levels; the pyramid's extra third does not. Figure 2 sets the counts side by side.

![Bars of coefficients per pixel for a 5-sample row, the 5×5 patch and a 1920×1080 frame: lifting, PyWavelets and the pyramid](FIG_02)

*Figure 2 — Coefficients kept per pixel. Lifting keeps exactly one; PyWavelets' default padding costs most on small arrays and long filters; the pyramid's extra third never goes away. Counted from each library's size rule, not run.*

## Intuition

Every wavelet coefficient answers one local question: how far is this sample from what its neighbours predict? Where the image is smooth the answer is zero; where it jumps, the answer is the jump, or half of it. The coarse signal carries the rest to the next level, which asks the same question at twice the spacing, so a slow gradient eventually shows up as a difference between coarse samples far apart.

A one-dimensional Haar transform works like a knockout tournament. Each pair's average goes through to the next round and its difference is recorded; after $\log_2 N$ rounds the overall average is left beside $N - 1$ recorded differences, $N$ numbers in all. The analogy even predicts the main weakness: who meets whom is fixed by the seating, so shift every player one seat and different pairs meet. It breaks for the 5/3, where every sample deals with two neighbours, so the matches overlap and no bracket can draw them.

The second picture is how each representation divides position and frequency between its numbers; Figure 3 draws it for eight samples. Pixels are eight tall strips: exact position, no frequency. The DFT is eight wide bands: exact frequency, no position. Fixed blocks use one cell shape everywhere. Wavelets use four narrow cells across the top half of the band, two wider ones across the next quarter, then one, then the coarse cell, so fine detail gets a position and slow change a frequency, the trade the problem asked for.

![Position-frequency tilings for eight samples: pixels as strips, the DFT as bands, fixed blocks, and dyadic wavelet cells](FIG_03)

*Figure 3 — Every representation of eight samples has eight cells of equal area; they differ only in shape. Wavelets give fine detail a position and slow change a frequency. An idealisation: real filters are not brick walls, so each cell leaks into its neighbours.*

The section on shift variance puts numbers on that leak.

## What does one level do to an image?

In 2-D the transform separates, like Part 5's DFT: rows, then columns. Each pass splits into a low (coarse) and a high (detail) half, so one level yields four **subbands**, named horizontal filter first. LL is the half-resolution image. HL is high-pass horizontally and low-pass vertically, so it responds to vertical edges; LH responds to horizontal edges; HH to diagonal structure. A decomposition of $N_L$ levels has $3N_L + 1$ subbands. <!-- L34 -->

For hand arithmetic the orthonormal Haar is cleanest. For a 2×2 block with top row $p, q$ and bottom row $r, s$:

$$
\text{LL} = \tfrac{p+q+r+s}{2}, \quad
\text{HL} = \tfrac{p-q+r-s}{2}, \quad
\text{LH} = \tfrac{p+q-r-s}{2}, \quad
\text{HH} = \tfrac{p-q-r+s}{2}
$$

The four outputs are the block's sum and its three signed differences, each halved. This is what PyWavelets' `dwt2` computes with Haar, sign included: its Haar high-pass takes left minus right. <!-- L36 --> **Orthonormal** means the four squared outputs add up to the four squared inputs, so the square of a coefficient is its share of the image's energy.

The patch is 5×5, so PyWavelets first repeats its last row and column, its default mirror, to make 6×6, and returns four 3×3 subbands: 36 numbers. <!-- L13 --> <!-- L15 --> Figure 4 shows all of them.

- **LL** reads 80, 240, 400 in each block row, twice each block's mean, except 187.5 in the impulse's block.
- **HL** holds −160 down its middle column, the block of c2 and c3 that straddles the step: the edge lives in one column of one subband.
- **The impulse's block**, 40, 255 over 40, 40, gives 187.5, −107.5, 107.5, −107.5 for LL, HL, LH, HH. A flat block would give 80, 0, 0, 0, so the impulse contributes 107.5 to every subband, one coefficient each.

![The 5×5 patch beside its four 3×3 Haar subbands, with the step's −160 column in HL and the impulse's four ±107.5 coefficients outlined](FIG_04)

*Figure 4 — One orthonormal Haar level of the patch, padded to 6×6 as PyWavelets' default does. The impulse lands in one coefficient per subband, 25% of its energy each; Part 5's DFT gave every one of 25 bins 4%. Worked by hand.*

That is the comparison with Part 5. The impulse adds energy 215² = 46,225. The DFT spread it over 25 bins of magnitude 215, so by Parseval's relation each holds 4% of it; one Haar level puts it in four coefficients of 107.5, and 4 × 107.5² = 46,225, a quarter each. The edge, a line of energy through a whole row of DFT bins, sits in three coefficients of −160.

The next level transforms LL again. Because Haar blocks at each level tile the image without overlapping, a single bright pixel in a $2^J \times 2^J$ image touches one coefficient per subband per level, $3J + 1$ in all: 31 for a 1024×1024 image taken down to 1×1, against the DFT's 1,048,576 bins. Longer filters overlap, so an impulse touches a few coefficients per subband per level, but the count still grows with the number of levels, not of pixels.

JPEG 2000 Part 1 allows only these dyadic decompositions, LL split again each time. <!-- L37 --> Figure 5 draws three levels of a 1920×1080 frame to scale: three 960×540 subbands, three 480×270, three 240×135 and a 240×135 LL, 2,073,600 coefficients, the pixel count. Dropping one level's three detail subbands halves the image in each direction, <!-- L37 --> so a decoder that reads only LL3 and the level-3 details has a 480×270 preview from a sixteenth of the coefficients. That resolution scalability comes free.

![Three-level wavelet layout of a 1920×1080 frame drawn to scale, with subband sizes and the preview each LL decodes to](FIG_05)

*Figure 5 — Three levels of a 1920×1080 frame keep 2,073,600 coefficients, the pixel count. Reading LL3 and the level-3 details alone decodes a 480×270 preview from one sixteenth of them.*

## Which wavelet? Vanishing moments and the frequency response

Haar's prediction, that an odd sample equals its left neighbour, is right only on flat data: on the ramp 10, 17, 24, 31, … every Haar detail is 7, the slope. The 5/3's midpoint prediction is right on every straight line, so on that ramp every 5/3 detail is 0. The property at work is the number of **vanishing moments**: one more than the highest polynomial degree the high-pass filter annihilates. Haar has one, the 5/3 two, <!-- L27 --> and JPEG 2000's lossy 9/7 four. <!-- L28 -->

Vanishing moments make wavelet coefficients sparse. Wherever the image is close to a low-degree polynomial, which in a photograph is most places, the details are essentially zero, and long runs of zeros cost almost nothing to code. <!-- L29 --> The large coefficients sit near edges, and their magnitudes persist from one scale to the next. <!-- L30 -->

### Why JPEG 2000's filters are biorthogonal

Why not an orthonormal wavelet with many vanishing moments? Daubechies built them in 1988: the $N$th filter has $2N$ taps and grows smoother as it grows longer, but apart from Haar none of them is symmetric. <!-- L24 --> Their coefficients are irrational, with no closed form beyond $N = 3$, so integer pixels give non-integer coefficients. <!-- L23 --> Symmetry matters at the border: a symmetric filter applied to a mirrored signal gives a mirrored result, so the mirror adds no coefficients.

The way out is to let the analysis and synthesis filters differ. Cohen, Daubechies and Feauveau showed that such **biorthogonal** pairs give genuine wavelet bases and can be symmetric, which an orthonormal pair longer than Haar cannot. <!-- L25 --> The price is energy, which only an orthonormal transform preserves; boundary effects persuaded image coders to pay it. <!-- L33 --> The 5/3 is the shortest symmetric biorthogonal pair with two vanishing moments, <!-- L27 --> and it descends from Le Gall and Tabatabai's short symmetric subband filters, which need only additions and simple multiplications. <!-- L32 --> The 9/7 is the pair Antonini, Barlaud, Mathieu and Daubechies used to code images with a biorthogonal pyramid that keeps the pixel count constant, <!-- L31 --> and it is very nearly orthonormal: its Riesz bounds, the range of energy it passes, are 0.926 to 1.065, where orthonormal means exactly 1. <!-- L28 -->

### The same trade in frequency

Part 5's tool, the transfer function, shows the trade directly; Figure 6 plots it. With every low-pass scaled to gain 1 at zero frequency, Haar's low-pass is $|\cos(\omega/2)|$: it still passes 0.707 at the half-band point $\omega = \pi/2$ and 0.5 at $2\pi/3$. Those frequencies belong to the detail band, yet they reach the coarse band, and **decimation**, keeping every second sample, folds them back as aliases, the mechanism of *Resampling and Aliasing* (part 3). The 5/3's low-pass, $(3 + 2\cos\omega - \cos 2\omega)/4$, overshoots to 1.125 at $\pi/3$ and passes 0.625 at $2\pi/3$. The 9/7's stays at 0.955 at $\pi/3$ and falls to 0.354 at $2\pi/3$.

![Low-pass and high-pass magnitude responses of the Haar, 5/3 and 9/7 filters from zero to the Nyquist frequency](FIG_06)

*Figure 6 — Haar passes 0.707 at the half-band point; the 9/7 is flattest and cuts hardest. Near zero the high-pass curves rise as ω, ω² and ω⁴: the vanishing moments, read in frequency. Evaluated from the published taps.*

Near zero frequency the high-pass responses rise like $\omega$, $\omega^2$ and $\omega^4$: double the frequency and they grow 2, 4 and 16 times, the vanishing moments seen from the other side. None of the filters is a brick wall, so every decimated band aliases; the inverse cancels it exactly, but only if the coefficients reach it unchanged. <!-- L44 -->

## Lifting: how JPEG 2000 gets integers back exactly

In general lifting is three operations on the two halves of the signal: **split** into even and odd samples; **predict** each odd sample from the evens and keep the error; **update** the evens from the errors so that the coarse signal keeps the running average. For the 5/3 the update adds a quarter of each neighbouring detail: a detail $d$ marks area $d/2$ that the prediction took out around an odd sample, and the two even samples beside it share the job of putting it back. <!-- L16 -->

Daubechies and Sweldens showed that every wavelet transform with finite filters factors into such steps. <!-- L17 --> The 9/7 takes four, predict, update, predict, update, with coefficients α ≈ −1.586134342, β ≈ −0.05298011854, γ ≈ 0.8829110762 and δ ≈ 0.4435068522, and a final scaling. <!-- L18 --> OpenJPEG uses those four constants, then multiplies the detail band by $K = 1.230174105$ and the coarse band by $1/K$. <!-- L20 --> In the private cross-check, one unit sample pushed through those six steps reproduces, to six decimals, the filters printed in the JPEG 2000 overview: a 9-tap low-pass of 0.6029490 at the centre, then 0.2668641, −0.0782233, −0.0168641 and 0.0267488 on either side. <!-- L21 -->

Lifting is also cheaper: each step overwrites half the samples in place, and for long filters it needs half the arithmetic of filtering each band separately. <!-- L17 --> For the 9/7, Daubechies and Sweldens count 14 operations per pair of samples against 23, a 64% speed-up; for Haar both counts are 3. <!-- L19 -->

### Rounding inside the steps

Orthonormal filters turn integer pixels into irrational coefficients. <!-- L23 --> Lifting with rounding inside each step does not, and stays exactly invertible: the inverse recomputes each rounded quantity from the half of the samples it has already restored. The S-transform, an integer version of Haar, is the old example; Calderbank, Daubechies, Sweldens and Yeo showed that lifting plus reversible rounding gives a whole family of integer wavelet transforms for lossless coding. <!-- L22 -->

Figure 7 runs row r2, the one with the impulse, through the integer 5/3 and back. Its update meets sums that 4 does not divide: $s_0 = 40 + \lfloor (215 + 215 + 2)/4 \rfloor = 148$ where exact arithmetic gives 147.5, and $s_1 = 40 + \lfloor (215 + 80 + 2)/4 \rfloor = 114$ against 113.75. The inverse subtracts the same 108 and 74 and gets 40, 255, 40, 200, 200 back.

![Row 40 255 40 200 200 through integer 5/3 lifting and back: predict, update with rounded values 108 and 74, then the exact inverse](FIG_07)

*Figure 7 — The integer 5/3, forward and back, on row r2. The update rounds 107.5 up to 108 and 73.75 up to 74; the inverse subtracts the same integers, so the row returns exactly. Worked by hand.*

So JPEG 2000 Part 1 has two paths. The **reversible** one runs the 5/3 in integers and is lossless provided the decoder does not clip its output; <!-- L12 --> the **irreversible** one runs the 9/7 in floating point for lossy coding. <!-- L04 --> OpenJPEG and Pillow both default to the 5/3. <!-- L38 --> <!-- L39 -->

### What the transform changed against JPEG

Baseline JPEG transforms each 8×8 block on its own, <!-- L01 --> so at high compression its errors follow the block grid; JPEG 2000's errors sit where the large coefficients are, around edges. Its tiles behave like separate images, though, so large tiles do better: on one test image, 64×64 tiles cost more than 4.5 dB at 0.125 bits per pixel against no tiling. <!-- L02 -->

The measured gains depend on bit rate and picture. Skodras, Christopoulos and Ebrahimi report about 2 dB of PSNR over JPEG on a natural image at every compression ratio, shrinking as the rate rises, and files 53% smaller at 0.25 bits per pixel but only 11% smaller at 1.0. <!-- L40 --> A later study of 29 images, scored by predicted opinion rather than PSNR, found JPEG slightly ahead at low compression ratios and JPEG 2000 clearly ahead at medium and high ones, <!-- L41 --> and a psychophysical study found both codecs' quality depends on scene content. <!-- L42 --> The other half of the codec, which codes the bit planes of each block of coefficients with an arithmetic coder, <!-- L55 --> is outside this series.

## What does the decimated transform get wrong?

In row r0 the Haar pairs are (c0, c1), (c2, c3) and the lone c4, and the step between c2 and c3 falls inside a pair, so level 1 records it as 160. Move the step one pixel left, to `40 40 200 200 200`, or one pixel right, to `40 40 40 40 200`, and it falls between pairs: every level-1 Haar detail is 0, and the step reappears only at level 2. The 5/3 keeps it. Its level-1 detail is 80 in the original position and −80 in both shifted ones, because a step always lands between some odd sample and the midpoint of its neighbours.

The 5/3 fails on the other feature. Put the impulse of 255 on a flat row of 40 at an odd column, and both filters give one detail of 215. Move it to an even column: Haar gives −215, the same energy, but the 5/3 gives two details of −107.5, half the energy (23,112.5 against 46,225), and its coarse values become −13.75, 201.25, −13.75, negative grey levels. Figure 8 lays the cases out.

![Small multiples: the step at three positions and the impulse at two, with Haar and 5/3 level-1 details for each](FIG_08)

*Figure 8 — Move a feature one pixel and the decimated coefficients change. Haar loses the step at level 1 when it moves; the 5/3 keeps the step but halves the impulse's energy. Worked by hand on rows of the patch.*

Neither transform is **shift-invariant**: the coefficients depend on where a feature sits relative to the even–odd grid. Simoncelli, Freeman, Adelson and Heeger made this the central objection to orthogonal wavelet transforms: subband content is unstable under translation, and in 2-D under dilation and rotation, and the property they called shiftability is the absence of aliasing. <!-- L43 --> That is the leak Figure 6 showed: the decimated bands alias, and only an untouched inverse cancels it. <!-- L44 --> Part 5's Fourier magnitude has no such problem, because a shift changes only the phase. <!-- L46 --> In 2-D there is a second weakness. The HH subband's wavelet is a checkerboard that responds to +45° and −45° alike, so it cannot tell the two diagonals apart. <!-- L44 -->

The remedies buy invariance back with storage. The **undecimated** (stationary) transform skips the downsampling and keeps $J + 1$ full-length bands for $J$ levels in 1-D, <!-- L45 --> so $3J + 1$ full-size images in 2-D. The **dual-tree complex wavelet transform** runs two real trees whose wavelets form an approximate Hilbert pair, like the cosine and sine of one Fourier wave; it is nearly shift-invariant and separates six orientations, at a redundancy of 2 in 1-D and 4 in 2-D. <!-- L45 --> Perfect shift invariance costs a factor of $\log_2 N$. <!-- L45 --> Figure 9 sets these beside the pyramid's 4/3, which buys no orientation at all. <!-- L06 -->

![Coefficients per pixel in 2-D: decimated wavelet 1, pyramid 4/3, dual tree 4, undecimated 10 and 16 at three and five levels](FIG_09)

*Figure 9 — What shift invariance costs in storage, in 2-D. The factors are the published ones; the undecimated 3J + 1 follows from the same count as the 1-D J + 1.*

## Denoising by shrinking coefficients

Add independent Gaussian noise of standard deviation σ to every pixel, and every orthonormal coefficient carries independent Gaussian noise of exactly σ: the transform is a rotation, and rotating a round cloud leaves it round. The image does not stay spread out; its energy gathers in a few large coefficients near edges. <!-- L30 --> So keep the large coefficients and shrink the small ones.

There are two rules. **Hard thresholding** keeps a coefficient whose magnitude is at least λ and zeroes the rest. **Soft thresholding** also zeroes the small ones, and pulls every survivor toward zero by λ: $\operatorname{sgn}(w)\max(|w| - \lambda, 0)$. <!-- L47 --> <!-- L51 -->

### Choosing λ and σ

Donoho and Johnstone's **universal threshold**, $\lambda = \sigma\sqrt{2\ln N}$ for $N$ coefficients, used by their VisuShrink, rests on one fact: the largest of $N$ independent standard normal values stays below $\sqrt{2\ln N}$ with probability tending to 1. <!-- L47 --> For a 512×512 image $\sqrt{2\ln N} = 4.995$, so with σ = 10 grey levels λ = 49.95, and of the 262,144 pure-noise coefficients the expected number that survive is 0.15. σ itself is estimated from the finest detail coefficients, which hold mostly noise: their median absolute value divided by 0.6745, the standard normal's 75th percentile. <!-- L48 --> Only the detail coefficients are shrunk; the coarse band is left alone. <!-- L48 -->

### What the rules do to the patch

Apply λ = 50, the σ = 10 threshold, to the noise-free patch, so that what changes is the signal itself. Hard thresholding changes nothing: every detail coefficient of the patch is at least 107.5. Soft thresholding takes 50 off each. The step's −160 becomes −110, so the pair across it reconstructs as 65, 175 and the edge's contrast drops from 160 to 110 in every row. The impulse's details become ±57.5 and its block reconstructs as 65, 180 over 65, 65: the 255 drops to 180, three neighbours rise to 65, and the block's mean of 93.75 survives because LL was never touched.

At λ = 120, above the impulse's 107.5, both rules flatten the impulse's block to 93.75; hard leaves the edge alone and soft cuts it to a 100, 140 pair. Figure 10 draws the four outcomes.

![Hard and soft threshold curves at λ = 50 with the patch's coefficients 107.5 and 160 marked, and the patch after each rule at λ = 50 and 120](FIG_10)

*Figure 10 — Soft thresholding subtracts λ from every survivor, so the edge loses contrast; hard thresholding keeps a coefficient whole or kills it. Above 107.5 both replace the impulse by its 2×2 mean, 93.75. Worked by hand on the noise-free patch.*

Hard thresholding keeps edges whole, but a noise coefficient pushed just over λ survives at full size as an isolated blip. Chang, Yu and Vetterli's **BayesShrink** picks λ per subband from a Bayesian model of the coefficients, in closed form, and comes within about 5% of the error of the best soft threshold chosen with the clean image in hand. <!-- L49 --> It is scikit-image's default, as $\sigma^2/\sigma_X$ per subband, where $\sigma_X^2$ is the subband's variance minus $\sigma^2$. <!-- L50 -->

Two warnings follow. The rotation argument needs an orthonormal transform, and scikit-image warns when handed a wavelet that is not orthogonal; <!-- L50 --> in the worked example's lifting scale, $d = x_{2k+1} - x_{2k}$ carries noise of $\sigma\sqrt{2}$, so one λ for every band is a different threshold in each. And thresholding upsets the alias cancellation, leaving alignment-dependent artefacts <!-- L44 --> that the undecimated and dual-tree transforms reduce.

## The math

| Symbol | Meaning |
|---|---|
| $a_j[k]$, $d_j[k]$ | coarse and detail coefficients at level $j$; $a_0$ is the input |
| $h$, $g$ | analysis low-pass and high-pass filters |
| $x_e$, $x_o$ | the even and odd halves of the input |
| $P$, $U$ | lifting's predict and update operators |
| $p$ | number of vanishing moments |

**Multiresolution.** Mallat's construction nests approximation spaces, each at half the resolution of the next; the detail lost between two of them is spanned by shifts of one wavelet, and one pair of filters reaches both, <!-- L07 --> which gives the algorithm:

$$
a_{j+1}[k] = \sum_n h[n - 2k]\, a_j[n], \qquad d_{j+1}[k] = \sum_n g[n - 2k]\, a_j[n] \tag{1}
$$

Filter, then keep every other output. With Haar's $h = \tfrac{1}{\sqrt2}(1, 1)$ and $g = \tfrac{1}{\sqrt2}(1, -1)$, row r0 gives coarse $\sqrt2 \times (40, 120, 200)$ and detail $(0, -160, 0)/\sqrt2$: the worked example's values rescaled, signed left minus right, with c4 paired with its copy.

**Lifting.** With the input split into $x_e$ and $x_o$,

$$
d = x_o - P(x_e), \qquad s = x_e + U(d) \tag{2}
$$

is the forward step, and running the lines backwards with the signs flipped is the inverse:

$$
x_e = s - U(d), \qquad x_o = d + P(x_e) \tag{3}
$$

Equation (3) inverts equation (2) whatever $P$ and $U$ are, including when they round, because each line recomputes its operator from a half that is already known. That is the whole integer property. For Haar, $P(x_e)_k = x_{2k}$ and $U(d)_k = d_k/2$; for the 5/3, $P(x_e)_k = \lfloor (x_{2k} + x_{2k+2})/2 \rfloor$ and $U(d)_k = \lfloor (d_{k-1} + d_k + 2)/4 \rfloor$.

**Vanishing moments.** The high-pass $g$ has $p$ vanishing moments when $\sum_n n^m g[n] = 0$ for $m = 0, \dots, p - 1$, so its response vanishes like $\omega^p$ at zero frequency: the 2, 4 and 16 of Figure 6 for $p = 1, 2, 4$. <!-- L29 -->

**Thresholds.** For a detail coefficient $w$,

$$
\eta_{\text{soft}}(w) = \operatorname{sgn}(w)\,\max(|w| - \lambda,\ 0), \qquad \lambda = \sigma\sqrt{2\ln N} \tag{4}
$$

so at λ = 50 the patch's 160 becomes 110 and its 107.5 becomes 57.5, the numbers behind Figure 10. <!-- L47 -->

## Implementation: the tooling map

Every call below maps to arithmetic above. **None of it was executed for this post**; the mapping comes from source at a pinned commit. Figure 11 is the same map in one picture.

![Grid of PyWavelets, scikit-image and Pillow/OpenJPEG calls with their extension mode, size rule, default and trap](FIG_11)

*Figure 11 — The same transform in three libraries: different mirrors, sizes, names and defaults. None of it was executed; every cell comes from source at a pinned commit.*

### PyWavelets

| Want | Call | Note |
|---|---|---|
| one level, 1-D | `pywt.dwt(x, "haar")` | default `mode="symmetric"` repeats the end sample; ⌊(N + L − 1)/2⌋ per band <!-- L13 --> <!-- L15 --> |
| JPEG 2000's mirror | `mode="reflect"` | whole-sample; `"symmetric"` is half-sample <!-- L15 --> |
| one level, 2-D | `pywt.dwt2(img, "haar")` | returns `(cA, (cH, cV, cD))`; `cH` is JPEG 2000's LH, `cV` its HL <!-- L34 --> <!-- L35 --> |
| the 5/3 and the 9/7 | `"bior2.2"`, `"bior4.4"` | analysis filters × √2, padded to 6 and 10 taps <!-- L14 --> |
| shrink | `pywt.threshold(w, lam)` | soft by default; `mode="hard"` keeps survivors whole <!-- L51 --> |
| undecimated | `pywt.swt2(img, "haar", level)` | each side a multiple of 2**level <!-- L52 --> |

### scikit-image

| Want | Call | Note |
|---|---|---|
| denoise | `skimage.restoration.denoise_wavelet(img)` | Haar, soft, BayesShrink, max levels − 3; details only <!-- L50 --> |
| the noise level | `skimage.restoration.estimate_sigma(img)` | `db2`, finest diagonal band, median ÷ 0.6745, zeros skipped <!-- L50 --> |

### Pillow and OpenJPEG

| Want | Call | Note |
|---|---|---|
| lossless JPEG 2000 | `img.save("out.jp2")` | the 5/3; OpenJPEG's 6 resolutions, lowered for small images <!-- L38 --> <!-- L39 --> |
| lossy | `irreversible=True` | the 9/7 <!-- L39 --> |
| level count | `num_resolutions=n` | n − 1 decomposition levels <!-- L39 --> |
| a preview | `im.reduce = k` before `im.load()` | discards k resolutions, each halving the size <!-- L39 --> |

### The worked example, in PyWavelets

```python
import numpy as np
import pywt

row = np.array([40, 40, 40, 200, 200], dtype=float)
cA, cD = pywt.dwt(row, "haar")               # 3 + 3: c4 is paired with its own copy
s, d = cA / np.sqrt(2), -cD * np.sqrt(2)     # back to the lifting scale used above
print(s, d)                                  # [40 120 200] [0 160 0]

patch = np.full((5, 5), 40.0)
patch[:, 3:] = 200
patch[2, 1] = 255
cA, (cH, cV, cD) = pywt.dwt2(patch, "haar")  # four 3 x 3 arrays: 36 numbers
print(cV[:, 1], cH[1, 0], cD[1, 0])          # [-160 -160 -160] 107.5 -107.5
```

This was not run for this post. The scaling line bridges PyWavelets' orthonormal scale and the worked example's lifting scale: they differ by √2 and a sign.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** expecting a wavelet transform to return as many numbers as it was given. PyWavelets' default mode turns the 5×5 patch into 36 Haar coefficients and 100 with `bior2.2`, <!-- L13 --> so code that writes them into an image-sized buffer, or compares counts with a JPEG 2000 file, breaks on odd sizes and long filters. Use `mode="periodization"` on even sizes, or keep the shapes the call returns.

- **Reading `cH` as JPEG 2000's HL.** PyWavelets' "horizontal detail" is high-pass down the columns, which is JPEG 2000's LH; the names cross. <!-- L34 --> <!-- L35 -->
- **Taking "symmetric" to mean one thing.** PyWavelets' `symmetric` repeats the end sample; JPEG 2000 mirrors about it, which PyWavelets calls `reflect`. <!-- L15 --> The worked example's 240 at c4 becomes 220 if the end sample is repeated.
- **One threshold for a transform that is not orthonormal.** The 5/3 and 9/7 do not preserve energy, <!-- L33 --> so scale λ per band or use an orthonormal wavelet.
- **Thresholding the coarse band.** It holds the mean and the slow shading, not noise; shrinking it flattens the image.
- **Matching features on decimated coefficients.** For registration or tracking, use an undecimated or dual-tree transform.
- **Odd sizes in the undecimated transform.** `swt2` needs each side to be a multiple of 2**level; <!-- L52 --> the 5×5 patch cannot go through it even at one level.
- **Quoting 4/3 for a row.** The pyramid's 4/3 is a 2-D figure; in 1-D it doubles the data. <!-- L05 -->

## Key takeaways

- **A wavelet coefficient measures how far a sample is from what its neighbours predict, at one scale.** The impulse's 215 became four Haar coefficients of 107.5, 25% of its energy each; the DFT gave each of 25 bins 4%.
- **Computed by lifting, a level keeps exactly N numbers and inverts exactly in integers.** That is JPEG 2000's lossless 5/3 path; the Laplacian pyramid keeps 4/3 N in 2-D.
- **Vanishing moments decide sparsity.** Haar zeroes constants, the 5/3 straight lines, the 9/7 cubics; JPEG 2000's filters are biorthogonal so that they can be symmetric.
- **Decimated wavelets are shift-variant.** One pixel took the step's Haar detail from 160 to 0 and halved the impulse's 5/3 energy; invariance costs storage, 4× for the dual tree in 2-D.
- **Noise stays at σ in every orthonormal coefficient while the image concentrates.** That is why thresholding works; soft thresholding takes λ off every edge it keeps.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: row r2 through both

Compute one Haar level and one integer 5/3 level of row r2, `40 255 40 200 200`, with the rules of the worked example.

**Self-check:** Haar coarse 147.5, 120, 200 and detail 215, 160; 5/3 coarse 148, 114, 240 and detail 215, 80.

<details><summary>Answer</summary>

Haar: $d = 255 - 40, 200 - 40$; $s = 40 + 107.5, 40 + 80, 200$. 5/3: $d_0 = 255 - 40$, $d_1 = 200 - 120$; $s_0 = 40 + \lfloor 432/4 \rfloor$, $s_1 = 40 + \lfloor 297/4 \rfloor$, $s_2 = 200 + \lfloor 162/4 \rfloor$. The impulse costs both filters its full height, because both its neighbours are 40.

</details>

### E2 — Inspect: a preview from Figure 5

From Figure 5, how many coefficients must a decoder read for a 480×270 preview of the 1920×1080 frame, and what fraction of the total is that?

**Self-check:** a count, a fraction, and which subbands it reads.

<details><summary>Answer</summary>

LL3 and the three level-3 details, each 240×135: 4 × 32,400 = 129,600 coefficients, 1/16 of 2,073,600.

</details>

### E3 — Predict: the transpose

Part 5's image B is the patch's transpose: a horizontal edge between r2 and r3, the impulse at (r1, c2). Before computing, predict one orthonormal Haar level of it: which subband holds the edge, with what values, and where the impulse's coefficients go. Then check the impulse's block by hand.

**Self-check:** the edge as −160 across one block row of LH; HL zero except for the impulse; the impulse in block (0, 1), 107.5 in every subband. A right answer without the reason does not count.

<details><summary>Answer</summary>

Transposing swaps HL and LH and transposes every subband. The edge moves from HL's middle column to LH's middle row: rows r2 and r3 read 40, 40 over 200, 200, so LH = (40 + 40 − 200 − 200)/2 = −160 in all three block columns. The impulse's block, rows r0–r1 and columns c2–c3, is 40, 40 over 255, 40: LL 187.5, LH −107.5, HL +107.5, HH −107.5.

</details>

### E4 — Diagnose: an inverse that is off by one

A colleague decodes coarse 148, 114, 240 and detail 215, 80 with their own inverse 5/3 and gets `41 256 41 200 200`. Find the cause, the one observation that proves it, and the fix.

**Self-check:** the cause named; which samples should be wrong, predicted from your explanation and confirmed against the output; the fix.

<details><summary>Answer</summary>

The inverse update drops the +2: it subtracts $\lfloor (d_{k-1} + d_k)/4 \rfloor$ where the forward added $\lfloor (d_{k-1} + d_k + 2)/4 \rfloor$. They differ exactly when the sum leaves a remainder of 2 or 3 on division by 4: at c0 it is 430, so $x_0 = 41$; at c2 295, so $x_2 = 41$; at c4 160 (remainder 0), so $x_4$ is right. The odd samples inherit the error through the prediction: $x_1 = 215 + \lfloor 82/2 \rfloor = 256$, which no longer fits in 8 bits, while $x_3 = 80 + \lfloor 241/2 \rfloor = 200$ survives. The fix: recompute the forward's rounded quantity exactly, +2 included.

</details>

## References

1. Mallat, S. "A Theory for Multiresolution Signal Decomposition: The Wavelet Representation." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 11(7):674–693, 1989. doi:10.1109/34.192463. [PDF](https://www.di.ens.fr/~mallat/papiers/MallatTheory89.pdf)
2. Haar, A. "Zur Theorie der orthogonalen Funktionensysteme." *Mathematische Annalen* 69(3):331–371, 1910. [doi:10.1007/BF01456326](https://doi.org/10.1007/BF01456326)
3. Daubechies, I. "Orthonormal Bases of Compactly Supported Wavelets." *Communications on Pure and Applied Mathematics* 41(7):909–996, 1988. doi:10.1002/cpa.3160410705. [PDF](https://sites.math.duke.edu/~ingrid/publications/cpam41-1988.pdf)
4. Cohen, A., Daubechies, I., and Feauveau, J.-C. "Biorthogonal Bases of Compactly Supported Wavelets." *Communications on Pure and Applied Mathematics* 45(5):485–560, 1992. doi:10.1002/cpa.3160450502. [PDF](https://sites.math.duke.edu/~ingrid/publications/CPAM_1992_p485.pdf)
5. Le Gall, D., and Tabatabai, A. "Sub-Band Coding of Digital Images Using Symmetric Short Kernel Filters and Arithmetic Coding Techniques." *Proceedings of IEEE ICASSP 1988*, 761–764. [doi:10.1109/ICASSP.1988.196696](https://doi.org/10.1109/ICASSP.1988.196696)
6. Antonini, M., Barlaud, M., Mathieu, P., and Daubechies, I. "Image Coding Using Wavelet Transform." *IEEE Transactions on Image Processing* 1(2):205–220, 1992. doi:10.1109/83.136597. [PDF](https://sites.math.duke.edu/~ingrid/publications/ieee1-1992.pdf)
7. Daubechies, I., and Sweldens, W. "Factoring Wavelet Transforms into Lifting Steps." *Journal of Fourier Analysis and Applications* 4(3):247–269, 1998. doi:10.1007/BF02476026. [PDF](https://sites.math.duke.edu/~ingrid/publications/J_Four_Anal_Appl_4_p247.pdf)
8. Calderbank, A. R., Daubechies, I., Sweldens, W., and Yeo, B.-L. "Wavelet Transforms That Map Integers to Integers." *Applied and Computational Harmonic Analysis* 5(3):332–369, 1998. [doi:10.1006/acha.1997.0238](https://doi.org/10.1006/acha.1997.0238)
9. Unser, M., and Blu, T. "Mathematical Properties of the JPEG2000 Wavelet Filters." *IEEE Transactions on Image Processing* 12(9):1080–1090, 2003. doi:10.1109/TIP.2003.812329. [PDF](https://bigwww.epfl.ch/publications/unser0305.pdf)
10. Unser, M., and Blu, T. "Wavelet Theory Demystified." *IEEE Transactions on Signal Processing* 51(2):470–483, 2003. doi:10.1109/TSP.2002.807000. [PDF](https://bigwww.epfl.ch/publications/unser0301.pdf)
11. Usevitch, B. E. "A Tutorial on Modern Lossy Wavelet Image Compression: Foundations of JPEG 2000." *IEEE Signal Processing Magazine* 18(5):22–35, 2001. [doi:10.1109/79.952803](https://doi.org/10.1109/79.952803)
12. Skodras, A., Christopoulos, C., and Ebrahimi, T. "The JPEG 2000 Still Image Compression Standard." *IEEE Signal Processing Magazine* 18(5):36–58, 2001. [doi:10.1109/79.952804](https://doi.org/10.1109/79.952804)
13. ISO/IEC JTC 1/SC 29/WG 1. *JPEG 2000 Image Coding System*, Committee Draft ISO/IEC CD 15444-1 (ITU-T T.800 draft), Annex F, December 1999. [PDF](https://www.eecis.udel.edu/~amer/CISC651/JPEG2000_draft_std_cd15444-1.pdf)
14. Wallace, G. K. "The JPEG Still Picture Compression Standard." *IEEE Transactions on Consumer Electronics* 38(1):xviii–xxxiv, 1992. doi:10.1109/30.125072. [PDF](https://www.comp.nus.edu.sg/~cs5342/readings/wallace.pdf)
15. Ebrahimi, F., Chamik, M., and Winkler, S. "JPEG vs. JPEG 2000: An Objective Comparison of Image Encoding Quality." *Proceedings of SPIE* 5558, 300, 2004. [doi:10.1117/12.564835](https://doi.org/10.1117/12.564835)
16. Triantaphillidou, S., Allen, E., and Jacobson, R. E. "Image Quality Comparison Between JPEG and JPEG2000. II. Scene Dependency, Scene Analysis, and Classification." *Journal of Imaging Science and Technology* 51(3):259–270, 2007. [doi:10.2352/J.ImagingSci.Technol.(2007)51:3(259)](https://doi.org/10.2352/J.ImagingSci.Technol.(2007)51:3(259))
17. Simoncelli, E. P., Freeman, W. T., Adelson, E. H., and Heeger, D. J. "Shiftable Multiscale Transforms." *IEEE Transactions on Information Theory* 38(2):587–607, 1992. [doi:10.1109/18.119725](https://doi.org/10.1109/18.119725)
18. Selesnick, I. W., Baraniuk, R. G., and Kingsbury, N. G. "The Dual-Tree Complex Wavelet Transform." *IEEE Signal Processing Magazine* 22(6):123–151, 2005. doi:10.1109/MSP.2005.1550194. [PDF](https://eeweb.engineering.nyu.edu/iselesni/pubs/CWT_Tutorial.pdf)
19. Donoho, D. L., and Johnstone, I. M. "Ideal Spatial Adaptation by Wavelet Shrinkage." *Biometrika* 81(3):425–455, 1994. [doi:10.1093/biomet/81.3.425](https://doi.org/10.1093/biomet/81.3.425)
20. Donoho, D. L. "De-Noising by Soft-Thresholding." *IEEE Transactions on Information Theory* 41(3):613–627, 1995. doi:10.1109/18.382009. [Preprint](https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/denoiserelease3.pdf)
21. Donoho, D. L., Johnstone, I. M., Kerkyacharian, G., and Picard, D. "Wavelet Shrinkage: Asymptopia?" *Journal of the Royal Statistical Society, Series B* 57(2):301–337, 1995. doi:10.1111/j.2517-6161.1995.tb02032.x. [PDF](https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/asymp.pdf)
22. Chang, S. G., Yu, B., and Vetterli, M. "Adaptive Wavelet Thresholding for Image Denoising and Compression." *IEEE Transactions on Image Processing* 9(9):1532–1546, 2000. [doi:10.1109/83.862633](https://doi.org/10.1109/83.862633)
23. PyWavelets source, commit c9b542b: signal extension modes, `dwt_coeff_len`, `dwt2`, the wavelet filter tables, `threshold` and `swt`. <https://github.com/PyWavelets/pywt/tree/c9b542b2d2c37d28ed1d9bd49d178d2769608905> (accessed 2026-10-10)
24. scikit-image source, `denoise_wavelet` and `estimate_sigma`, commit b700edc. <https://github.com/scikit-image/scikit-image/blob/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/restoration/_denoise.py> (accessed 2026-10-10)
25. OpenJPEG source, `src/lib/openjp2` (`dwt.c`, `openjpeg.c`, `opj_common.h`, `tcd.c`), commit 8314119. <https://github.com/uclouvain/openjpeg/tree/8314119b067c0fc77834731168daaebd379fdb12/src/lib/openjp2> (accessed 2026-10-10)
26. Pillow handbook, "Image file formats: JPEG 2000", commit c15d19b. <https://github.com/python-pillow/Pillow/blob/c15d19b957327d8e00b1e60084fb1c70573ba63e/docs/handbook/image-file-formats.rst> (accessed 2026-10-10)
