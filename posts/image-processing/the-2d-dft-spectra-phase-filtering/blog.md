---
title: "The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering"
slug: the-2d-dft-spectra-phase-filtering
date: 2026-10-10
updated: 2026-10-10
summary: "A 2-D spectrum says how much of each wave an image holds and which way it runs; phase says where. Worked on a 5×5 patch: phase swap, notch filter, FFT cost."
tags: [algorithms, image-processing, fourier-transform, signal-processing, filter-design, opencv]
category: algorithms
categories: [algorithms]
tier: L4
difficulty: advanced
series: image-processing
series_position: 5
prerequisites: ["the transform stage from Image Processing by Hand", "the 1-D DFT and complex exponentials", "the convolution theorem", "reading Python signatures"]
reading_minutes: 45
cover_image_url: "COVER"
cover_image_alt: "A 5×5 grid of spectrum cells with one bright row through a tangerine centre, over an even grey floor"
canonical_url: "https://canery.in/blogs/the-2d-dft-spectra-phase-filtering"
---

> [!NOTE]
> **Insights** — A 2-D DFT spectrum records how much of each wave an image contains and which way each wave runs; where the image's features are is held almost entirely in the phase. On the series' 5×5 patch the vertical edge prints a horizontal line of energy, the one bright pixel prints a flat floor of 215, and an image rebuilt from the phase alone keeps that pixel exactly where it was. Filtering in the frequency domain is the right move when the thing to remove occupies a few coefficients, like periodic interference, or when the kernel is large: counting the arithmetic puts the break-even for a full kernel near 10×10, and OpenCV's own code switches at a kernel area of 130.

**Level:** advanced · **You need:** the transform stage of *Image Processing by Hand: Sample, Filter, Transform, Decide* (part 1 of this series) and its four-point DFT, complex exponentials, the convolution theorem, and enough Python to read a signature · **Time:** ~45 min

This is part 5 of *Image Processing by Hand*. The hub's transform stage worked a four-point DFT and the convolution theorem on one row of the patch. This part takes the transform to two dimensions and asks three things of it: what its spectrum shows, what its phase holds, and when filtering there beats filtering in space.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Reading a spectrum](#how-do-you-read-a-2-d-spectrum) · [What phase keeps](#what-survives-when-the-magnitude-is-destroyed) · [Filter design](#how-do-you-design-a-filter-in-the-frequency-domain) · [Notches](#when-does-a-notch-work) · [The crossover](#when-is-the-fft-round-trip-cheaper-than-the-direct-sum) · [Phase correlation](#where-position-is-the-answer-phase-correlation) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. Every number is worked by hand on the shared patch, its transpose or its 2×2 tiling; the arithmetic was cross-checked with plain Python using only its `math` and `cmath` modules, and that check is not published. No NumPy, OpenCV, SciPy or scikit-image call was executed: what each library does comes from its documentation and from reading its source at a pinned commit. There are no timings and no measured curves. The cost figure is an operation-count model, and every figure that draws a curve says it was evaluated from a closed form.

## Why this matters

You take the FFT of a photograph, centre it, log-scale it, and see a bright cross through the middle, a few bright dots and a fog. You cannot tell which of them is the image and which the transform made up. You design a low-pass filter by zeroing everything outside a disc, and every edge in the result grows rings. You switch a 5×5 convolution to `fftconvolve` because the FFT is fast, and it gets slower.

Each of these has a number behind it, and this post computes all three on the series' patch. The cross is an edge the DFT invents at the image border. The rings are the dip a brick-wall filter digs beside a step: on one row of the patch, from 40 grey levels down to 0.45. And the FFT round trip costs about 170 operations per pixel on a 1920×1080 frame whatever the kernel, which a 5×5 kernel's 50 never reaches.

## The problem

The two-dimensional discrete Fourier transform (2-D DFT) is the hub's one-dimensional transform applied along both axes at once. For an image $f(r, c)$ with $M$ rows and $N$ columns it is

$$
F(k_r, k_c) = \sum_{r=0}^{M-1} \sum_{c=0}^{N-1} f(r, c)\, e^{-2\pi i \left( \frac{k_r r}{M} + \frac{k_c c}{N} \right)}
$$

Each **coefficient**, or **bin**, $F(k_r, k_c)$ measures how much the image contains of one 2-D wave: a wave that completes $k_r$ cycles down the rows and $k_c$ cycles across the columns. Like every complex number it has a **magnitude**, how strong that wave is, and a **phase**, where its crests sit. The convention here is the hub's and NumPy's default: no scaling on the forward transform and $1/(MN)$ on the inverse. <!-- L20 -->

The spectrum has exactly as many numbers as the image, but none of them is local. Every coefficient depends on every pixel, <!-- L38 --> so a 1920×1080 frame becomes about two million complex numbers, each a weighted sum over all two million pixels. Three questions decide whether that change of basis helps.

1. **What does the magnitude show?** Which waves are present and which way they run. Not, it will turn out, where anything is.
2. **What does the phase hold?** If position is not in the magnitude it must be in the phase. How much of an image survives in the phase alone?
3. **When is filtering there the right move?** A frequency-domain filter is one multiplication per coefficient, which is cheap. Getting there and back is two transforms, which are not. And the transform assumes the image tiles the plane, which it does not.

The difficulty is that all three answers sit in one array of complex numbers that nobody can read by eye. The worked example reads it on 25 of them.

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

### Rows first, then columns

The 2-D DFT **separates**: transform every row, then transform every column of the result. With $N = 5$ the waves are powers of $w = e^{-2\pi i/5}$, and one identity does most of the work. The five powers of $w^k$ sum to zero for $k \neq 0$, so $1 + w^k + w^{2k} = -(w^{3k} + w^{4k})$, and the row `40 40 40 200 200` collapses from five terms to two:

$$
S(k) = 40\,(1 + w^k + w^{2k}) + 200\,(w^{3k} + w^{4k}) = 160\,(w^{3k} + w^{4k})
$$

Only the jump of 160 survives; the flat 40 contributes nothing but the $k = 0$ sum. Pairing the two powers about their midpoint gives $S(k) = 160 \cdot 2\cos(\pi k/5)\, e^{-i\,7\pi k/5}$:

| k | 0 | ±1 | ±2 |
|---|---|---|---|
| S(k) | 520 | 258.89 ∠ ±108° | 98.89 ∠ ∓144° |

The two magnitudes are 160 times $2\cos 36° = 1.618$, the golden ratio, and 160 times $2\cos 72° = 0.618$, its reciprocal. Row r2 is the same row plus 215 at c1, and an impulse in column 1 adds $215\,w^k$: a fixed length of 215 at angle −72°·k. At $k = \pm1$ that points exactly opposite the step's ±108°, and at $k = \pm2$ exactly along its ∓144°, because the impulse sits half a period, 2.5 samples, from the centre of the 200 plateau. So row r2 transforms to 735, then 258.89 − 215 = 43.89 ∠ ±108°, then 98.89 + 215 = 313.89 ∠ ∓144°.

Now the columns. Four of the five rows produced the same five numbers, and a column of equal entries transforms to five times that entry at $k_r = 0$ and to zero everywhere else. Only row r2's difference, $215\,w^{k_c}$ in every column, survives at other $k_r$, as the wave $w^{2k_r}$ because it sits in row 2. The whole spectrum is

$$
F(k_r, k_c) = 5\,S(k_c)\,[k_r = 0] + 215\, w^{2k_r + k_c}
$$

where the bracket is 1 when $k_r = 0$ and 0 otherwise. Figure 1 shows the two passes.

![The 5×5 patch, its five row transforms with row r2 standing out, and the final spectrum: one bright row and every other bin at 215](FIG_01)

*Figure 1 — Rows first, then columns. Four identical rows transform to the same five numbers, and the column pass collapses them into one bright row; row r2's difference, an impulse, spreads into every bin with magnitude 215. Worked by hand.*

### The spectrum, centred

Three readings come straight off that formula.

- **DC.** $F(0, 0) = 5 \times 520 + 215 = 2{,}815$, the sum of the pixels: 25 times their mean of 112.6.
- **The bright row.** At $k_r = 0$ the magnitudes are 1,079.43 at $k_c = \pm1$ and 709.43 at $\pm2$, with the step's angles. These are waves that vary across the columns and are constant down each column, which is what a vertical edge is built from. A vertical edge prints a horizontal line of energy: the spectrum runs perpendicular to the edge that made it.
- **The flat floor.** Every other bin has magnitude exactly 215. That is the impulse. One bright pixel contains every wave in equal measure, and $215\,w^{2k_r + k_c}$ has the same length wherever it is evaluated.

For display, the DC term is usually moved to the middle. NumPy's `fftshift` reorders each 5-point axis as 3, 4, 0, 1, 2, so frequencies read −2 to 2 with DC at the centre. <!-- L18 --> The display also needs a log scale. DC is 13 times the floor, and by Parseval's relation, $\sum |F|^2 = 25 \sum f^2 = 12{,}185{,}625$, it holds 65.0% of the energy; the rest of the bright row holds 27.4% and the twenty floor bins 7.6% between them. On a linear scale only DC is visible. Taking $\log_{10}(1 + |F|)$ maps 2,815, 1,079, 709 and 215 to 3.45, 3.03, 2.85 and 2.33. Figure 2 shows the result beside the patch.

![The patch beside its centred 5×5 magnitude spectrum: DC 2,815 at the centre, a bright horizontal row, and a flat floor of 215 elsewhere](FIG_02)

*Figure 2 — A vertical edge prints a horizontal line; one bright pixel prints a flat floor. Centred with fftshift and shaded on a log scale, because DC is 13 times the floor and holds 65% of the energy.*

Where is the impulse in Figure 2? Not in the magnitudes. The floor would read 215 everywhere whichever pixel held the impulse. Its position is in the phase: the floor's angles are $-72^\circ \times (2k_r + k_c)$, a ramp whose slopes, 2 and 1, are the impulse's row and column.

### Keep the phase, or keep the magnitude

Two rebuilds separate the halves. For a **magnitude-only image**, set every phase to zero and invert. For a **phase-only image**, set every magnitude to 1, keep the phases, and invert.

Magnitude only: with zero phase, each of the twenty floor waves becomes a cosine that peaks at (0, 0), and together they put 215 at the origin. The bright row becomes a profile symmetric about column 0. Every row reads 212.71, 93.37, 60.28, 60.28, 93.37, and (r0, c0) reads 427.71. The step has turned into a hump centred on c0, and the impulse has moved to the corner.

Phase only: the floor's unit arrows $w^{2k_r + k_c}$ add up to a unit impulse at (2, 1), exactly where the impulse was. The bright row adds a single cosine along every row, because the impulse's contribution to that row pointed along the step's at $k_c = \pm2$ and against it at $\pm1$. Every row reads −0.049, −0.160, −0.049, +0.129, +0.129, and (r2, c1) reads 0.840. The numbers are small, because unit magnitudes carry little energy, but the layout is the patch's: the impulse at (2, 1), dark on the left, bright on the right, and the crossing between c2 and c3. Figure 3 puts the three side by side.

![Three 5×5 grids: the patch, its magnitude-only rebuild with the impulse moved to the corner, and its phase-only rebuild keeping it in place](FIG_03)

*Figure 3 — Keep only the phase and the impulse stays at (r2, c1), with the step on the correct side; keep only the magnitude and both move to the corner. Each panel is shaded on its own range; every value is printed.*

Oppenheim and Lim's review collected this effect across images, speech and crystallographic structures: in some situations many of a signal's important features survive when only its phase is kept, and under conditions such as finite length the phase determines the signal up to a scale factor. <!-- L01 --> <!-- L02 -->

### Swapping phase between two images

The demonstration usually associated with that review exchanges the phases of two images: the magnitude of one with the phase of the other. On two photographs the result looks like the image that supplied the phase. <!-- L11 -->

To do it by hand, the second image has to come from the same patch, so turn the patch on its side. Image B is the transpose of A: a horizontal step with rows 3 and 4 bright, and the impulse at (r1, c2). Its spectrum is A's transposed, a bright column instead of a bright row. The magnitude of A with the phase of B inverts to

```text
  49.65   82.74  202.08   82.74   49.65
  25.88   58.97  393.31   58.97   25.88
  49.65   82.74  202.08   82.74   49.65
  88.11  121.20  240.54  121.20   88.11
  88.11  121.20  240.54  121.20   88.11
```

B's impulse is back at full strength at (1, 2), 393 against a background of 26 to 240. Rows 3 and 4 are brighter than rows 0 to 2, which is where B's step is. Phase put both where B has them. But the strongest structure is a vertical bar down column 2, from 202 to 393, and B has no vertical bar. The bar is A's bright row: A's magnitude says "strong waves that vary across the columns", and B's phase says "line them up at column 2". The other swap, B's magnitude with A's phase, is the exact transpose: a horizontal bar through row 2 with A's impulse at (2, 1). Figure 4 shows all four.

![Four 5×5 grids: the patch, its transpose, and the two swaps, A's magnitude giving a vertical bar and B's magnitude a horizontal one](FIG_04)

*Figure 4 — The swap with the patch's transpose. B's phase puts the impulse at (r1, c2) and brightens rows 3 and 4, where B has them; A's magnitude makes the dominant bar vertical. Neither image wins.*

On this pair, phase decided where things are and magnitude decided which way the dominant structure runs and how strong it is. The photograph swap looks like the phase donor because photographs' magnitude spectra share a shape. Their amplitude falls off roughly as 1/f, which Field measured on six natural images, <!-- L09 --> and later models refine only the exponent and let it vary with orientation, <!-- L10 --> so exchanging two photographs' magnitudes exchanges little. The patch and its transpose differ in exactly what magnitude records, the orientation of their edge. Lohmann, Mendlovic and Shabtay make the general point: symmetry, or one changed pixel, can change which of the two halves matters. <!-- L06 --> Swap with a circularly shifted copy of the patch instead and the magnitudes agree to $2 \times 10^{-12}$; the swap then returns both images exactly.

### One periodic artefact, removed with a notch

Now a problem the frequency domain solves outright. Tile the patch 2×2 into a 10×10 image, and add horizontal bands that run three cycles down the frame, $20\cos(2\pi \cdot 3r/10)$. Bands like these are what an AC signal riding on a camera's video line produces. <!-- L35 --> Every row of the tile shifts by its band's value, 20, −6.18, −16.18, 16.18, 6.18, −20 and so on down the frame.

Tiling makes the image periodic with period 5 in both directions, so its 10×10 DFT is the patch's 5×5 DFT placed on every other bin. Only the 25 bins whose indices are both even are non-zero, each 4 times the patch's: DC is 11,260. The bands are constant along each row and complete 3 cycles down 10 rows, so they add to exactly two bins, (3, 0) and (7, 0), which are ±3 on the vertical axis. Each takes magnitude 20 × 100 / 2 = 1,000. Both have an odd row index, where the tile has nothing.

A **notch reject filter** is a gain of 0 at chosen bins and 1 everywhere else. Design it from the spectrum: find the bins that are large where the image's own structure says they should be empty, and zero them. Here that is two bins. Multiply, invert, and the result equals the tile to $3 \times 10^{-12}$, exact up to rounding. Rounding the corrupted image to 8 bits before filtering leaves at most 0.16 grey levels of error. Figure 5 lays out the four stages.

![The tiled 10×10 patch with interference bands, its spectrum with two spikes off the even lattice, the two-bin notch, and the restored tile](FIG_05)

*Figure 5 — The interference lands on two bins, ±3 on the vertical axis, where the tile has nothing; zeroing them restores the tile to within 3 × 10⁻¹². The spectrum is centred and log-shaded; the lattice of tile bins is outlined.*

The notch was exact because of two facts, and [the notch section](#when-does-a-notch-work) breaks them one at a time: the interference completes a whole number of cycles across the frame, so it occupies two bins, and the image has nothing in those bins.

### What the round trip costs

For a convolution with an 11×11 kernel on a 1920×1080 frame, the direct sum costs 121 multiplications and about as many additions per pixel: 242 operations. The FFT route pads to 1,930 × 1,090 so the convolution is linear rather than circular, then to 1,944 × 1,125, the next sizes built only from 2s, 3s and 5s. <!-- L22 --> <!-- L23 --> Counting a real-input transform as $2.5\,PQ\log_2(PQ)$ operations, FFTW's convention, <!-- L27 --> each transform costs $1.15 \times 10^8$. Three of them, for the image, the kernel and the product, plus six operations per complex product, come to 169.8 per output pixel. On paper the FFT wins at 11×11, yet OpenCV's `filter2D` computes this one directly; <!-- L41 --> [the crossover section](#when-is-the-fft-round-trip-cheaper-than-the-direct-sum) explains why.

## Intuition

Moving an image moves its phase and nothing else. Shift the patch one column to the right and every coefficient keeps its magnitude while its phase turns by −72° times its column frequency: bin (0, 1) goes from 108° to 36°, bin (1, 1) from 144° to 72°, and bin (1, 0) does not move. A shift adds a ramp to the phase, and the ramp's slope is the shift. That is why the floor's phase is $-72^\circ \times (2k_r + k_c)$: read the slopes off and you have the impulse's row and column. Figure 6 draws those phases as arrows.

![Phase arrows for the patch's spectrum, turning −72° per column step and −144° per row step, before and after a one-column shift](FIG_06)

*Figure 6 — Position is the slope of a phase ramp. The floor's arrows turn by −72° per column step and −144° per row step, the impulse's column 1 and row 2. Shift the patch and every arrow turns by an amount proportional to its frequency.*

Edges live in phase for a related reason. A step is a place where many waves cross zero together on their way up. Phase congruency, the idea after Morrone and Owens that features sit where an image's Fourier components are maximally in phase, <!-- L12 --> makes that alignment the definition of a feature. Flatten the magnitudes and the waves still line up at the edge, which is why a phase-only image looks like an edge map.

An analogy: the magnitude spectrum is a parts list and the phase is the assembly drawing. The parts list says how many of each part there are, how much of each wave at each orientation, and the drawing says where each part goes. Swap two machines' drawings and you get one machine's parts bolted where the other's go, which is what Figure 4 showed: A's vertical bar in B's places. The analogy breaks in two places, both taken up in [what phase keeps](#what-survives-when-the-magnitude-is-destroyed). For a texture the parts list is the whole description. And in two dimensions the parts list nearly always determines the machine, so magnitude is not empty; it is unreadable by eye.

## How do you read a 2-D spectrum?

### Where each frequency sits

Bin $k$ of an $N$-point DFT is frequency $k$ for the first half of the axis and $k - N$ for the second. On 5 points the order is 0, 1, 2, −2, −1. <!-- L19 --> NumPy's `fftshift` rolls each axis by $\lfloor N/2 \rfloor$ so DC lands in the middle, and `ifftshift` rolls it back by $-\lfloor N/2 \rfloor$. The two agree for even $N$ and differ by one sample for odd $N$. <!-- L18 --> On the 5-point axis fftshift gives the order 3, 4, 0, 1, 2 and ifftshift 2, 3, 4, 0, 1; applying fftshift twice gives 1, 2, 3, 4, 0, which leaves DC in the last place. On 10 points both give 5 to 9, then 0 to 4: DC sits at index 5, and the Nyquist frequency −5 sits alone at the left edge with no positive partner. Figure 7 lays out both.

![Frequency strips for 5 and 10 points through fftshift, then ifftshift or a second fftshift, with DC and the Nyquist bin marked](FIG_07)

*Figure 7 — Where each bin goes. On 5 points fftshift and ifftshift differ by one place, and fftshift applied twice leaves DC in the last place; on 10 points the two agree and the Nyquist bin sits alone at the left.*

OpenCV has no fftshift. Its DFT tutorial swaps the four quadrants of the magnitude image by hand, and first crops an odd-sized spectrum to even, discarding a row and a column. <!-- L17 -->

### Half of it is redundant

A real image has a **conjugate-symmetric** spectrum: $F(-k_r, -k_c)$ is the complex conjugate of $F(k_r, k_c)$, the same magnitude with the opposite phase. The patch shows it at once, with 1,079.43 ∠ 108° at (0, 1) and 1,079.43 ∠ −108° at (0, −1). Libraries store about half. NumPy's `rfft2` keeps $N/2 + 1$ columns for even $N$ and $(N+1)/2$ for odd, <!-- L52 --> and `cv2.dft` packs the symmetric result of a real input into a real array of the input's size, its CCS format, unless the `DFT_COMPLEX_OUTPUT` flag asks for the full complex array. <!-- L21 --> Displaying a CCS array as if it were a magnitude image shows a spectrum that is not there.

Two more readings carry over from the worked example. Turning an image by 90° turns its spectrum by 90°, as the patch and its transpose showed, and fine structure sits far from DC while coarse structure sits near it.

### The cross the DFT invents

The DFT treats an image as one tile of a periodic plane. Opposite borders rarely match, so the periodic image has jumps across every border, and those jumps put a cross of strong coefficients along both axes, in magnitude and in phase. <!-- L13 --> The patch shows the mechanism in one row: tiled, the right column's 200 runs straight into the next tile's 40, a second step that the patch does not contain. Figure 8 tiles it.

![The patch tiled three by three, the invented 200-to-40 edge marked at every tile border, beside three fixes for the cross and one non-fix](FIG_08)

*Figure 8 — The DFT computes the spectrum of this tiling. At every tile border the 200 of c4 meets the 40 of the next tile's c0: a second step the patch does not contain.*

On the patch the invented step is vertical, like the real one, so both land on the same bright row and cannot be told apart. On a photograph whose left and right columns differ, the invented step adds a horizontal line through DC, and mismatched top and bottom rows add a vertical one. Three fixes are in use, and one tempting non-fix.

- **Taper.** Multiply by a window that falls to zero at the borders, such as the Hann window `cv2.phaseCorrelate` accepts for exactly this reason. <!-- L48 --> A window reweights every pixel, and the choice of window is a literature of its own. <!-- L16 -->
- **Mirror.** Reflect the image before transforming. The borders then match and the jump becomes a kink in the slope, which is much weaker. The mirrored DFT equals a discrete cosine transform plus a half-pixel phase shift. <!-- L14 -->
- **Split.** The **periodic-plus-smooth decomposition** writes the image as a part that tiles cleanly plus a smooth part that absorbs the border mismatch, and removes the cross at FFT cost. <!-- L15 -->
- **Not zero padding.** Padding with zeros to reach a fast size adds a jump to black at the new border. OpenCV's tutorial pads exactly this way before displaying its spectrum. <!-- L17 -->

## What survives when the magnitude is destroyed?

For finite signals the answer is a theorem. Hayes, Lim and Oppenheim proved that two finite-length sequences whose z-transforms have no zeros on the unit circle and none in reciprocal pairs, and whose Fourier phases agree, differ only by a positive scale factor. <!-- L03 --> The phase does not even need to be known everywhere: for a sequence that is zero outside $N$ samples, agreement at $N - 1$ distinct frequencies strictly between 0 and π is enough. <!-- L04 -->

That condition explains Figure 3. A 5-point DFT supplies only two frequencies strictly between 0 and π along each axis, half of the four the one-dimensional theorem asks for a 5-point signal. So the same-size phase-only image is an approximation, a **whitened** version of the patch in which every wave has been given equal strength, not the patch itself. Pad the image with zeros before transforming and there are enough phase samples; an algorithm that knows the image's extent can then rebuild it up to scale, which is the exact reconstruction Oppenheim and Lim review. <!-- L02 -->

In two dimensions the picture is more generous to magnitude. Hayes showed that neither phase nor magnitude alone determines a multidimensional sequence in general, but that a large class of them can be recovered from either; for magnitude, no practical algorithm existed when he wrote. <!-- L05 --> The information is in the magnitude. It is just not arranged so that an inverse transform, or an eye, can use it.

What magnitude visibly carries is what a texture is. Galerne, Gousseau and Morel synthesise a texture from a sample by keeping its Fourier magnitude and randomising its phase. The method reproduces micro-textures, whose look is set by their Fourier modulus, and fails on macro-textures with strong edges, definite shapes or large periodic patterns, which need their phase. <!-- L07 --> They ran into this post's cross along the way: randomising the phase of a sample that does not tile produced strong horizontal and vertical waves, until they replaced the sample by its periodic component. <!-- L08 -->

So "phase matters more than magnitude" is a statement about position and about photographs.

| | The magnitude carries | The phase carries |
|---|---|---|
| a translation | nothing; it is unchanged | all of it, as a ramp |
| an edge | its orientation, as a line through DC | where the edge sits |
| a micro-texture | its look | nothing visible |
| a photograph | a roughly 1/f falloff that every photograph shares | the layout |

## How do you design a filter in the frequency domain?

A frequency-domain filter multiplies the spectrum by a **transfer function** $H$, one gain per bin, and inverts: $g = \mathrm{Re}\,\mathcal{F}^{-1}[H \cdot F]$. Gonzalez and Woods take the real part at the end, because a real, symmetric $H$ applied to a real image gives a real result in theory and rounding leaves tiny imaginary residue in practice. <!-- L33 --> Three design rules follow from the rest of this post.

**Keep the phase.** A real, even $H$, the same real gain at $k$ and $-k$, is **zero-phase**: it changes how much of each wave there is and moves nothing. Any $H$ with a phase moves its waves, and moving waves by different amounts moves edges. The worked example showed how much of an image lives in phase; a filter should not touch it unless moving things is the point.

**Choose the shape for its kernel, not its cutoff.** The gain profile's inverse transform is the spatial kernel, and the kernel is what the image actually meets. On the patch row, an **ideal low-pass** that keeps $k = 0$ and $\pm1$ and zeroes $\pm2$, a brick wall, returns 72.0, 0.45, 72.0, 187.8, 187.8: the flat 40 beside the edge has been dug down to 0.45. That dip is **ringing**, the brick wall's sinc-shaped kernel overshooting. The shared Gaussian's gains at the same frequencies are 1, 0.670 and 0.135, and its output is 78.2, 40.0, 78.2, 161.8, 161.8, all within the input's 40 to 200. Figure 9 sets the two side by side.

![Gains of an ideal low-pass and the shared Gaussian at five frequencies, and their outputs on the row, the ideal one dipping to 0.45](FIG_09)

*Figure 9 — A brick wall in frequency digs a hole to 0.45 beside the edge; the Gaussian's gains fall smoothly and its output stays between 40 and 200. Evaluated from the closed forms at the row's five frequencies.*

**Pad, then round up.** The DFT's product is circular convolution: the hub's four-point example pulled the far end's 200 into the first sample. Linear convolution needs both arrays padded to $M + m - 1$ first, which is what OpenCV's DFT-convolution example does with `getOptimalDFTSize(A.cols + B.cols - 1)`. <!-- L23 --> Gonzalez and Woods show the difference padding makes at an image's vertical edges. <!-- L34 --> Then round up to a fast length. Cooley and Tukey's own analysis puts the cost of a factor $r$ in proportion to $r/\log_2 r$: 2.00 for 2, 1.88 for 3 and 2.15 for 5, so a length built from 2s, 3s and 5s costs within a few percent of the best. <!-- L26 --> `getOptimalDFTSize` returns lengths of exactly that form, $2^p 3^q 5^r$, <!-- L22 --> and SciPy's `next_fast_len` does the same for the factors its FFT implements. <!-- L46 -->

### Resizing through the spectrum

The same machinery resizes. Enlarge by **zero-padding the spectrum**: insert zeros at the high frequencies and invert on a larger grid. Doubling the patch row this way gives 40, 32.45, 40, 32.45, 40, 104, 200, 247.11, 200, 104. Every original sample survives at the even positions, and between them the output rings, overshooting to 247.1 between the two 200s. Shrink by **truncating the spectrum**, keeping only the low frequencies and inverting on a smaller grid, and the row's three samples come out 72.0, 34.7, 205.3: the mean of 104 survives exactly, and the ringing again leaves the input's range. Zero-padding is periodic sinc interpolation, and it rings at frame borders because the DFT's periodisation puts a jump there; mirroring first or the periodic-plus-smooth split avoids that. <!-- L50 --> The kernels that resize well in space are the subject of part 3, *Resampling and Aliasing: Interpolation Kernels in Practice*.

## When does a notch work?

Periodic interference comes from electrical pickup, miscalibrated sensors, halftone printing and the scan lines of a monitor. It shows up as sharp spikes in the spectrum, and notch filters that remove those spikes are the basic method, essentially unchanged since the processing of the Mariner 6 and 7 pictures in 1971. <!-- L37 --> The standard textbook gives notch filters a section of their own, and periodic-noise reduction, including optimum notch filtering, another. <!-- L36 --> The worked example's notch was exact. Change one thing and it stops being.

Make the bands complete 2.5 cycles down the 10 rows instead of 3. The values become 20, 0, −20, 0, 20 and so on, a period of 4 pixels, which does not divide 10, and the energy no longer fits in two bins. Down the spectrum's centre column the magnitudes are 200, 247.2, 647.2, 647.2, 247.2, 200, then the mirror image: every bin of the column holds some, with 83.8% in $k = \pm2$ and $\pm3$. This is **spectral leakage**. A wave that does not complete a whole number of cycles across the frame is not one of the DFT's waves, so the DFT writes it as a mixture of all of them. Figure 10 shows both cases over the tile's own bins on that column.

![Bar charts of interference magnitude on one spectrum column for 3 and 2.5 cycles, over the tile's own bins at even frequencies](FIG_10)

*Figure 10 — Three cycles in ten rows land on two bins the tile never uses; two and a half spread over every bin, two of which carry 860 of the tile's own content. Computed magnitudes.*

Two of the leaked bins, ±2, hold the tile's own content, 860 each, so every notch is now a trade.

| Notch on that column | rms error (unfiltered: 14.14) | Max error |
|---|---|---|
| ±3 only, where the tile is empty | 10.78 | 16.0 |
| ±2 and ±3 | 13.43 | 25.9 |
| every bin but DC and Nyquist | 17.43 | 34.4 |

Notching only the image-free bins removes 42% of the interference's energy and touches nothing else. Widening the notch to catch the leakage removes more interference and more image, and at eight bins the result is worse than not filtering at all. A notch's width is a bet on what the image does not contain.

The cleanest fix is to make the interference fit the frame. Crop or pad to 20 rows and the same 4-pixel period completes exactly five cycles: it lands on bins 5 and 15, the tile occupies only multiples of 4, and a two-bin notch is exact again. A softer notch, a Gaussian dip in place of a zero, trades the other way. On the on-bin case a Gaussian of width 0.5 bins scales the four bins around each spike by 0.865, two of which carry the tile, and leaves an rms error of 2.33 where the ideal notch left none.

On a photograph the hard part is deciding which spikes are interference. Every coefficient depends on the whole image, and a man-made repetitive structure or a localised texture makes spikes too, so telling them apart needs prior knowledge. <!-- L38 --> Sur and Grédiac automate the decision by comparing the spectrum, averaged over many small patches, with the power law that a natural image's spectrum is expected to follow, and notching the outliers, which may be whole sets of frequency pairs rather than two bins. <!-- L39 --> Gonzalez and Woods' worked case is a Cassini image of Saturn's rings: an AC signal on the camera's video put bursts of energy along the spectrum's vertical axis, a narrow notch along that axis removed them, and subtracting the notch from 1 isolated the interference pattern itself. <!-- L35 -->

## When is the FFT round trip cheaper than the direct sum?

Cooley and Tukey cut the DFT's direct $N^2$ operations to fewer than $2N\log_2 N$, <!-- L25 --> and within a year Stockham had applied their procedure to convolution and correlation. <!-- L30 --> The hub said that past some kernel size, transforming, multiplying and transforming back beats the direct sum. Four sources put that size in four places, and each is right about what it counts.

**The textbook.** Gonzalez and Woods count on the order of $MNm^2$ operations for an m×m kernel on an M×N image, $MN \cdot 2m$ if the kernel separates, and $2MN\log_2 MN$ for a forward and an inverse FFT. <!-- L31 --> Their ratio for square images, $C_n(m) = m^2/(4\log_2 M)$, passes 1 at 7×7 for every size from 512 to 4,096. For separable kernels, $C_s(m) = m/(2\log_2 M)$ passes 1 between 19 and 25 taps; the book reads "around 27" off its own table at 2,048. They call these comparisons guidelines, because the counts ignore that the FFT works in complex numbers. <!-- L32 -->

**The arithmetic.** Count what the round trip actually does: pad to $M + m - 1$ and up to a fast size, run three real 2-D FFTs at FFTW's $2.5\,PQ\log_2(PQ)$ each, <!-- L27 --> and spend six operations on each complex product over the half spectrum. Against $2m^2$ operations per pixel for a full kernel and $4m$ for a separable one, the crossover moves.

| Image | FFT route, operations per pixel | Full kernel crosses at | Kernel's FFT cached | Separable crosses at |
|---|---|---|---|---|
| 512 × 512 | 154.8 | 9×9 | 8×8 | 45 taps |
| 1920 × 1080 | 169.8 | 10×10 | 8×8 | 44 taps |
| 2048 × 2048 | 188.2 | 10×10 | 8×8 | 48 taps |
| 4096 × 4096 | 204.8 | 11×11 | 9×9 | 52 taps |

The FFT route barely depends on the kernel. It changes only when the padding crosses to the next fast size, so it is a nearly flat line, and the direct sum's parabola crosses it near 10. Counting with Yavne's split radix instead of radix 2, 20% fewer operations, <!-- L28 --> moves the full-kernel crossover down by about one size. A separable kernel almost never crosses: it needs more than 40 taps, a Gaussian with σ near 7 if cut at three sigma. Figure 11 draws the model for the 1920×1080 frame.

![Operations per pixel against kernel width for direct, separable and FFT convolution on a 1920×1080 frame, with OpenCV and textbook marks](FIG_11)

*Figure 11 — A model, not a timing: operations per output pixel on a 1920×1080 frame. The FFT route is nearly flat in kernel width; the full kernel's 2m² crosses it near 10 and the separable 4m near 44. OpenCV switches at area 130, the textbook ratio at 7.*

**OpenCV.** The documentation of `filter2D` says it uses a DFT-based algorithm for kernels of about 11×11 or larger. <!-- L40 --> The source is more precise. The DFT path runs only when the kernel's area is at least 130, on machines with SSE3 and for 8-bit to 8-bit or 16-bit and float to float filtering, or at least 50 otherwise, and never on a sub-matrix. <!-- L41 --> An 11×11 kernel, area 121, is filtered directly, and 12×12 is the first square kernel to switch. The higher threshold applies only when the CPU has SSE3, which reads as the vectorised direct loop beating its operation count, so OpenCV switches later than the model. Its DFT path keeps the border rule the caller asked for rather than wrapping, and `sepFilter2D` has no DFT path at all. <!-- L42 -->

**SciPy.** `scipy.signal.convolve` with `method='auto'` asks `choose_conv_method`, which predicts from fitted constants rather than timing. Its model counts $3N\ln N$ operations for three FFTs of the full output size against the kernel's size times the output's, and for 2-D 'same' output it weights one direct operation about 7.6 times as heavily as one FFT operation. <!-- L44 --> On that model the FFT is predicted faster for 2-D kernels from 3×3 upward, for images from 64×64 to 2048×2048. The constants were tuned on a 2014 laptop and checked on a cloud machine, and the notes report 99% accuracy in 2-D. <!-- L43 --> Its direct path is a general N-dimensional loop, so it loses early. For one large and one small array, SciPy's documentation describes `oaconvolve`, which applies the FFT block by block with overlap-add, as generally much faster than `fftconvolve`. <!-- L51 -->

So the crossover is not a property of the mathematics. The arithmetic puts it near 10×10 for a full kernel, but an operation is not a nanosecond: memory traffic and vector units decide the rest, which is why FFTW adapts its algorithm to the machine it runs on. <!-- L29 --> Measure on yours. `choose_conv_method(..., measure=True)` times both methods and returns the faster. <!-- L43 -->

## Where position is the answer: phase correlation

If position lives in phase, a translation between two images is a phase difference, and one division isolates it. Multiply one spectrum by the conjugate of the other, divide every product by its own magnitude, and invert. That is **phase correlation**, which scikit-image credits to Kuglin and Hines in 1975 and uses by default. <!-- L47 --> OpenCV's `phaseCorrelate` does the same — an optional Hann window against the border cross, the normalised cross-power spectrum, an inverse DFT — and refines the peak with a 5×5 weighted centroid. <!-- L48 -->

On the patch, let C be A shifted circularly by one row down and two columns right. By the shift theorem $F_C = F_A\, w^{k_r + 2k_c}$, so the normalised product $F_A \overline{F_C} / |F_A \overline{F_C}|$ is $w^{-(k_r + 2k_c)}$, a pure ramp. Its inverse is a single 1 at (4, 3), which is (−1, −2) read circularly: the shift, with its sign set by which spectrum was conjugated. The other 24 positions are exactly 0. Without the division, plain cross-correlation peaks at the same place, at 487,425, but the four other positions in column 3 all reach 441,200. The peak stands only 10.5% above a ridge, because the step is constant down the rows and cannot say how far it moved vertically; only the impulse breaks the tie. Figure 12 shows both surfaces.

![Two 5×5 surfaces for the patch and its shifted copy: plain correlation with a ridge down one column, and phase correlation with a single 1](FIG_12)

*Figure 12 — Normalising every coefficient to unit magnitude turns a ridge into one peak. Plain correlation's maximum stands 10.5% above four equal values down column 3; phase correlation is 1 at the shift and 0 everywhere else.*

The division needs every $|F|$ to be non-zero, and on the patch the smallest is 215. It also gives every frequency equal weight, including the ones that are mostly noise. scikit-image's documentation records the consequence: phase correlation copes well with changes of illumination, is not very robust to noise, and the unnormalised version can be the better choice when noise is high. <!-- L47 --> A sub-pixel shift does not give one peak either. For downsampled images the power spreads over several adjacent, coherent peaks, and their pattern yields a closed-form sub-pixel estimate. <!-- L49 -->

## The math

| Symbol | Meaning | Units |
|---|---|---|
| $f(r, c)$ | image, row $r$, column $c$ | grey levels |
| $M, N$ | numbers of rows and columns | — |
| $F(k_r, k_c)$ | 2-D DFT coefficient | grey levels, summed |
| $w$ | $e^{-2\pi i/5}$, the 5-point root of unity | — |
| $H(k_r, k_c)$ | transfer function, one gain per bin | — |
| $m$ | kernel width | pixels |
| $P, Q$ | padded transform sizes | pixels |

**The transform pair.**

$$
F(k_r,k_c) = \sum_{r=0}^{M-1}\sum_{c=0}^{N-1} f(r,c)\, e^{-2\pi i\,(k_r r/M + k_c c/N)}, \qquad f(r,c) = \frac{1}{MN}\sum_{k_r=0}^{M-1}\sum_{k_c=0}^{N-1} F(k_r,k_c)\, e^{2\pi i\,(k_r r/M + k_c c/N)} \tag{1}
$$

The forward sum is unscaled and the inverse divides by $MN$, NumPy's default and OpenCV's with `DFT_SCALE` on the inverse. <!-- L20 --> <!-- L21 -->

**Separability.**

$$
F(k_r, k_c) = \sum_{r=0}^{M-1} e^{-2\pi i\,k_r r/M} \left[ \sum_{c=0}^{N-1} f(r,c)\, e^{-2\pi i\,k_c c/N} \right] \tag{2}
$$

The bracket is a row transform, and the outer sum transforms each resulting column. On the patch the bracket is $S(k_c)$ for four rows and $S(k_c) + 215\,w^{k_c}$ for row 2, which is how Figure 1's spectrum came out as $5S(k_c)$ on the $k_r = 0$ row plus $215\,w^{2k_r + k_c}$ everywhere.

**Shift.** If $g(r, c) = f(r - a, c - b)$, indices taken circularly, then

$$
G(k_r, k_c) = F(k_r, k_c)\, e^{-2\pi i\,(k_r a/M + k_c b/N)} \tag{3}
$$

The magnitude is unchanged and the phase gains a ramp whose slope is the shift. With $a = 0$ and $b = 1$ on the patch the ramp is $-72^\circ \times k_c$, which turned bin (0, 1) from 108° to 36°.

**Symmetry and energy.** For a real image $F(-k_r, -k_c) = \overline{F(k_r, k_c)}$, and

$$
\sum_{k_r, k_c} |F(k_r, k_c)|^2 = MN \sum_{r, c} f(r, c)^2 \tag{4}
$$

On the patch both sides are 12,185,625, which is where the energy shares of 65.0%, 27.4% and 7.6% came from.

**Phase only and magnitude only.**

$$
f_{\text{phase}} = \mathcal{F}^{-1}\!\left[ \frac{F}{|F|} \right], \qquad f_{\text{mag}} = \mathcal{F}^{-1}\big[\, |F| \,\big] \tag{5}
$$

On the patch the floor's unit arrows invert to a unit impulse at (2, 1), and the bright row adds $\tfrac{4}{25}\cos(108° + 72°c)$ along every row, which gives the worked example's 0.840, −0.049, −0.160 and +0.129. The magnitude-only value at the origin is the mean of all 25 magnitudes, 427.71.

<details>
<summary>Why the phase-only row is a single cosine</summary>

At $k_c = \pm1$ the bright row's phase is the step's, ±108°, while the floor term $w^{\pm1}$ alone would point at ∓72°, exactly opposite. At $k_c = \pm2$ the two point the same way. Normalising each bin to unit length, the bright row therefore differs from a pure floor term by $e^{\pm i\,108°} - e^{\mp i\,72°} = 2e^{\pm i\,108°}$ at $k_c = \pm1$ and by 0 at $\pm2$. Inverting those two terms over 25 bins gives

$$
\frac{1}{25}\left( 2e^{i\,108°}e^{2\pi i c/5} + 2e^{-i\,108°}e^{-2\pi i c/5} \right) = \frac{4}{25}\cos(108° + 72°c)
$$

which is −0.049, −0.160, −0.049, +0.129, +0.129 for $c = 0$ to 4. Adding the unit impulse at (2, 1) turns −0.160 into 0.840 there.

</details>

**Filters and notches.**

$$
g = \mathrm{Re}\,\mathcal{F}^{-1}[H \cdot F], \qquad H_{\text{notch}}(k) = \begin{cases} 0, & k = \pm k_0 \\ 1, & \text{otherwise} \end{cases} \tag{6}
$$

Equation (6) is Gonzalez and Woods' filtering step with a notch for $H$. <!-- L33 --> A wave $A\cos(2\pi k_0 r/M)$ with a whole number $k_0$ of cycles lands entirely on $\pm k_0$, each with magnitude $A \cdot MN/2$: 20 × 100 / 2 = 1,000 in the worked example. The 2.5-cycle bands are constant along each row, so the centre column of their 2-D spectrum is ten times one column's 1-D transform, $|X(k)| = 200 / |\sin(\pi(2k - 5)/10)|$: 647.2 at $k = \pm2, \pm3$, 247.2 at $\pm1, \pm4$, and 200 at 0 and 5.

**Cost per output pixel.**

$$
C_{\text{direct}} = 2m^2, \qquad C_{\text{separable}} = 4m, \qquad C_{\text{FFT}} = \frac{3 \cdot 2.5\,PQ\log_2(PQ) + 6P\left(\lfloor Q/2 \rfloor + 1\right)}{MN} \tag{7}
$$

Here $P$ and $Q$ are the smallest 2·3·5-smooth sizes at least $M + m - 1$ and $N + m - 1$. Gonzalez and Woods' simpler ratio is equation (7) without the padding, the kernel's transform, the real-input halving or the complex arithmetic. <!-- L32 --> For an 11×11 kernel on 1920×1080, equation (7) gives the worked example's 169.8 against 242.

## Implementation: the tooling map

Every call below maps to arithmetic above. **None of it was executed for this post**; the mapping comes from documentation and from source at a pinned commit. Figure 13 is the same map in one picture.

![Grid of NumPy, OpenCV, SciPy and scikit-image calls with their normalisation, layout, FFT switch rule and the trap each sets](FIG_13)

*Figure 13 — The same transform in four libraries: different scaling, layouts, switch rules and traps. None of it was executed for this post; every cell comes from documentation or source at a pinned commit.*

### NumPy

| Want | Call | Note |
|---|---|---|
| the spectrum | `np.fft.fft2(img)` | unscaled forward, $1/(MN)$ inverse; `norm="ortho"` or `"forward"` move the scaling <!-- L20 --> |
| half the spectrum of a real image | `np.fft.rfft2(img)` | $N/2 + 1$ columns for even $N$ <!-- L52 --> |
| DC in the middle, for display | `np.fft.fftshift(F)` | rolls each axis by $\lfloor N/2 \rfloor$ <!-- L18 --> |
| undo that | `np.fft.ifftshift(F)` | not `fftshift`: they differ on odd sizes |
| which frequency each bin is | `np.fft.fftfreq(n)` | 0, 1, …, then the negatives <!-- L19 --> |

### OpenCV

| Want | Call | Note |
|---|---|---|
| the spectrum | `cv2.dft(np.float32(img), flags=cv2.DFT_COMPLEX_OUTPUT)` | without the flag a real input gives a CCS-packed real array <!-- L21 --> |
| the inverse | `cv2.idft(F, flags=cv2.DFT_SCALE \| cv2.DFT_REAL_OUTPUT)` | `DFT_SCALE` divides by $MN$ |
| a fast padded size | `cv2.getOptimalDFTSize(n)` | the next $2^p 3^q 5^r$ <!-- L22 --> |
| a spectral product | `cv2.mulSpectrums(A, B, 0, conjB=False)` | `conjB=True` for correlation <!-- L24 --> |
| convolution | `cv2.filter2D(img, -1, kernel)` | correlation, not convolution; DFT only at area ≥ 130 or ≥ 50 <!-- L40 --> <!-- L41 --> |
| a translation | `cv2.phaseCorrelate(a, b, window)` | Hann window optional; 5×5 centroid <!-- L48 --> |

### SciPy and scikit-image

| Want | Call | Note |
|---|---|---|
| FFT convolution | `scipy.signal.fftconvolve(a, k, mode="same")` | always the FFT; slower when few outputs are needed <!-- L51 --> |
| one huge array, one small | `scipy.signal.oaconvolve(a, k)` | overlap-add <!-- L51 --> |
| let it choose | `scipy.signal.convolve(a, k, method="auto")` | fitted model: FFT from 3×3 in 2-D; direct for booleans and for integers that could outrun float precision <!-- L44 --> <!-- L45 --> |
| choose by timing | `scipy.signal.choose_conv_method(a, k, measure=True)` | runs both <!-- L43 --> |
| a fast padded size | `scipy.fft.next_fast_len(n)` | may change between versions <!-- L46 --> |
| a translation | `skimage.registration.phase_cross_correlation(a, b)` | phase normalisation by default <!-- L47 --> |

### A notch, in NumPy

```python
import numpy as np

F = np.fft.fft2(img)                          # unscaled forward transform
view = np.log1p(np.abs(np.fft.fftshift(F)))   # for looking only: DC centred, log scale

H = np.ones(F.shape)
for kr, kc in [(3, 0), (-3, 0)]:              # spikes read off `view`, in fft2's own layout
    H[kr % F.shape[0], kc % F.shape[1]] = 0.0

restored = np.real(np.fft.ifft2(H * F))      # real and even H: the imaginary part is rounding
```

This was not run for this post. The mask is built in the transform's own layout, with negative frequencies wrapped by `%`, so nothing is shifted back and the odd-size trap cannot occur. `fftshift` appears only in the line that makes a picture.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** undoing `fftshift` with `fftshift`. On an odd-sized array the two shifts differ by one sample, so DC lands in the last row and column, and inverting that spectrum multiplies the image by a wave instead of returning it. On the patch the real part reads 40 at (0, 0), as it should, and −206.3 at (2, 1), where 255 belongs: it is $f \cdot \cos(72°(r + c))$. Use `ifftshift`, or build masks in the unshifted layout and never shift back.

- **Filtering without padding.** The DFT's product is circular, so the far border leaks into the near one. Pad to $M + m - 1$ first.
- **Reading the cross as content.** A bright line through DC along an axis is usually the border jump, not an edge in the image. Taper, mirror or split before reading a spectrum.
- **Padding with zeros to reach a fast size.** Zeros add a border jump of their own. Pad by reflection when the spectrum will be read.
- **A notch wider than its spike.** Width removes whatever the image keeps in those bins. In the off-bin example an eight-bin notch did more damage than the interference.
- **Choosing the FFT for a small or separable kernel.** On arithmetic alone the round trip costs 155 to 205 operations per pixel; a full 5×5 kernel costs 50, and a separable kernel needs about 44 taps to cost as much.
- **Phase correlation on noisy images.** Normalising to unit magnitude gives noise-dominated frequencies full weight; the unnormalised correlation can do better.
- **Trusting "phase matters more" for textures.** For a micro-texture the magnitude is the content.
- **Beyond this post:** a global basis cannot say where in the image a frequency occurs. Local and non-stationary structure is the subject of a later part of this series, *Wavelets and Multiresolution*.

## Key takeaways

- **Magnitude says how much and which way; phase says where.** On the patch the vertical edge printed a horizontal line of 1,079 and 709, the impulse a flat floor of 215, and the impulse's position appeared only as the slope of a phase ramp.
- **Phase alone keeps the layout; magnitude alone loses it.** The photograph swap looks like the phase donor because photographs share a roughly 1/f magnitude; with the patch and its transpose, positions followed the phase and the dominant bar followed the magnitude.
- **The DFT sees a tiled image.** Its border jumps print a cross, so taper, mirror or split before reading a spectrum, and pad to $M + m - 1$ before filtering with one.
- **A notch is exact when the interference completes whole cycles and the image is empty there.** At 2.5 cycles the image-free notch cut the error from 14.1 to 10.8 rms, and an eight-bin notch made it worse than doing nothing.
- **The FFT round trip costs about 150 to 200 operations per pixel whatever the kernel.** A full kernel crosses it near 10×10, OpenCV switches at area 130, SciPy's model at 3×3, and a separable kernel almost never.

## Try it yourself

The exercises are pen and paper, matching the post. Each names its rung, from reproducing the worked example to extending it.

### E1 — Reproduce: one bin of each kind

Compute $F(1, 0)$ and $F(0, 2)$ of the patch from the definition, not from the closed form.

**Self-check:** 215 ∠ −144° and 709.43 ∠ −144°.

<details><summary>Answer</summary>

$F(1, 0)$ weights each row's total by $w^{r}$: $520\,(1 + w + w^3 + w^4) + 735\,w^2 = -520\,w^2 + 735\,w^2 = 215\,w^2$, which is 215 ∠ −144°. $F(0, 2)$ transforms the column totals 200, 415, 200, 1,000, 1,000 at $k = 2$: five times $S(2)$ gives 494.4 ∠ −144°, and column 1's extra 215 adds $215\,w^2$ at the same angle, for 709.4 ∠ −144°.

</details>

### E2 — Inspect: row r2 after the row pass

In Figure 1's middle grid, row r2's entry at $k_c = 2$ is larger than every other row's entry in that column. Without recomputing the whole row, give its value and the reason.

**Self-check:** a magnitude and an angle, and one sentence saying why the impulse adds in phase there and not at $k_c = 1$.

<details><summary>Answer</summary>

313.89 ∠ −144°. The impulse adds $215\,w^2$ = 215 ∠ −144°, the same angle as $S(2)$ = 98.89 ∠ −144°, so the magnitudes add: 98.89 + 215. At $k_c = 1$ it adds 215 ∠ −72°, opposite to $S(1)$'s 108°, so the magnitudes subtract to 43.89. The impulse is 2.5 samples from the plateau's centre, half a period of the $k = 1$ wave.

</details>

### E3 — Predict: shift the patch one column right

Before computing anything, write down what happens to $|F|$ and to the phases at (0, 1), (1, 0) and (1, 1) when every row is shifted circularly one column to the right. Then check one bin by hand.

**Self-check:** all magnitudes unchanged; phases 36°, −144° and 72°; the reason is the shift theorem's ramp of $-72^\circ \times k_c$. A right answer with a different reason does not count.

<details><summary>Answer</summary>

Equation (3) with $a = 0$, $b = 1$ multiplies every bin by $e^{-2\pi i k_c/5}$, a turn of $-72^\circ \times k_c$ that leaves the length alone. Bin (0, 1) goes from 108° to 36°, bin (1, 1) from 144° to 72°, and bin (1, 0), with $k_c = 0$, stays at −144°.

</details>

### E4 — Diagnose: a spectrum shifted twice

A colleague centres the patch's spectrum with `fftshift`, applies a mask of all ones, undoes the centring with `fftshift` again, inverts, and takes the real part. The output reads 40 at (0, 0) and −206.3 at (2, 1). Find the cause, the one observation that proves it, and the fix.

**Self-check:** the cause named; a value at another pixel predicted from your explanation and confirmed; the fix.

<details><summary>Answer</summary>

On an odd axis `fftshift` is not its own inverse. Applied twice it moves every bin one place further, so the array holds $F(k_r + 1, k_c + 1)$ and DC sits at (4, 4). Shifting a spectrum by one bin multiplies the image by $e^{-2\pi i(r + c)/5}$, so the real part is $f \cdot \cos(72°(r + c))$. The proof is a prediction: (0, 3) should read 200 × cos 216° = −161.8, and it does; (2, 1) is 255 × cos 216° = −206.3. The fix is `ifftshift`, or never shifting the spectrum that gets inverted.

</details>

### E5 — Extend: a diagonal interference

The 10×10 tile is corrupted by $15\cos(2\pi(2r + 3c)/10)$. Design the notch from the spectrum and show that it leaves the tile untouched.

**Acceptance test:** the mask is 0 at exactly the bins the interference occupies and 1 at all 25 bins the tile occupies, those with both indices even, so the restored image equals the tile.

<details><summary>One answer</summary>

The interference lands on (2, 3) and (8, 7), each with magnitude 15 × 100 / 2 = 750. Both have an odd column index, where the tile has nothing, so a two-bin notch at those positions restores the tile exactly.

</details>

## References

1. Oppenheim, A. V., and Lim, J. S. "The Importance of Phase in Signals." *Proceedings of the IEEE* 69(5):529–541, 1981. [doi:10.1109/PROC.1981.12022](https://doi.org/10.1109/PROC.1981.12022) (accessed 2026-10-10)
2. Hayes, M. H., Lim, J. S., and Oppenheim, A. V. "Signal Reconstruction from Phase or Magnitude." *IEEE Transactions on Acoustics, Speech, and Signal Processing* 28(6):672–680, 1980. doi:10.1109/TASSP.1980.1163463. [PDF](https://dsp-group.mit.edu/wp-content/uploads/2024/11/signrecons_1980.pdf) (accessed 2026-10-10)
3. Hayes, M. H. "The Reconstruction of a Multidimensional Sequence from the Phase or Magnitude of Its Fourier Transform." *IEEE Transactions on Acoustics, Speech, and Signal Processing* 30(2):140–154, 1982. [doi:10.1109/TASSP.1982.1163863](https://doi.org/10.1109/TASSP.1982.1163863) (accessed 2026-10-10)
4. Lohmann, A. W., Mendlovic, D., and Shabtay, G. "Significance of Phase and Amplitude in the Fourier Domain." *Journal of the Optical Society of America A* 14(11):2901, 1997. [doi:10.1364/JOSAA.14.002901](https://doi.org/10.1364/JOSAA.14.002901) (accessed 2026-10-10)
5. Galerne, B., Gousseau, Y., and Morel, J.-M. "Micro-Texture Synthesis by Phase Randomization." *Image Processing On Line* 1:213–237, 2011. doi:10.5201/ipol.2011.ggm_rpn. [PDF](https://www.ipol.im/pub/art/2011/ggm_rpn/article.pdf) (accessed 2026-10-10)
6. Field, D. J. "Relations between the Statistics of Natural Images and the Response Properties of Cortical Cells." *Journal of the Optical Society of America A* 4(12):2379–2394, 1987. [doi:10.1364/JOSAA.4.002379](https://doi.org/10.1364/JOSAA.4.002379) (accessed 2026-10-10)
7. Moisan, L. "Periodic Plus Smooth Image Decomposition." *Journal of Mathematical Imaging and Vision* 39(2):161–179, 2011. doi:10.1007/s10851-010-0227-1. [Preprint](https://helios2.mi.parisdescartes.fr/~moisan/papers/2009-11r.pdf) (accessed 2026-10-10)
8. Sur, F., and Grédiac, M. "Automated Removal of Quasiperiodic Noise Using Frequency Domain Statistics." *Journal of Electronic Imaging* 24(1):013003, 2015. doi:10.1117/1.JEI.24.1.013003. [PDF](https://members.loria.fr/FSur/articles/sur15automated.pdf) (accessed 2026-10-10)
9. Cooley, J. W., and Tukey, J. W. "An Algorithm for the Machine Calculation of Complex Fourier Series." *Mathematics of Computation* 19(90):297–301, 1965. doi:10.1090/S0025-5718-1965-0178586-1. [PDF](https://www.ams.org/journals/mcom/1965-19-090/S0025-5718-1965-0178586-1/S0025-5718-1965-0178586-1.pdf) (accessed 2026-10-10)
10. Johnson, S. G., and Frigo, M. "A Modified Split-Radix FFT with Fewer Arithmetic Operations." *IEEE Transactions on Signal Processing* 55(1):111–119, 2007. doi:10.1109/TSP.2006.882087. [PDF](https://www.fftw.org/newsplit.pdf) (accessed 2026-10-10)
11. Frigo, M., and Johnson, S. G. "The Design and Implementation of FFTW3." *Proceedings of the IEEE* 93(2):216–231, 2005. doi:10.1109/JPROC.2004.840301. [PDF](https://www.fftw.org/fftw-paper-ieee.pdf) (accessed 2026-10-10)
12. Stockham, T. G. "High-Speed Convolution and Correlation." *Proceedings of the AFIPS Spring Joint Computer Conference*, 229, 1966. [doi:10.1145/1464182.1464209](https://doi.org/10.1145/1464182.1464209) (accessed 2026-10-10)
13. Gonzalez, R. C., and Woods, R. E. *Digital Image Processing*, 4th ed. Pearson, 2018. ISBN 978-0-13-335672-4. [Sample chapters](https://imageprocessingplace.com/downloads_V3/dip4e_downloads/dip4e_sample_book_material/dip4e_sample_chapters.pdf) (accessed 2026-10-10)
14. Harris, F. J. "On the Use of Windows for Harmonic Analysis with the Discrete Fourier Transform." *Proceedings of the IEEE* 66(1):51–83, 1978. [doi:10.1109/PROC.1978.10837](https://doi.org/10.1109/PROC.1978.10837) (accessed 2026-10-10)
15. Foroosh, H., Zerubia, J. B., and Berthod, M. "Extension of Phase Correlation to Subpixel Registration." *IEEE Transactions on Image Processing* 11(3):188–200, 2002. [doi:10.1109/83.988953](https://doi.org/10.1109/83.988953) (accessed 2026-10-10)
16. Skarbnik, N., Zeevi, Y. Y., and Sagiv, C. "The Importance of Phase in Image Processing." CCIT Report 773, Technion, 2010 (technical report). [PDF](https://ece.technion.ac.il/wp-content/uploads/2021/01/publication_773-1.pdf) (accessed 2026-10-10)
17. FFTW. "FFT Benchmark Methodology." <https://www.fftw.org/speed/method.html> (accessed 2026-10-10)
18. OpenCV source, `modules/imgproc/src/filter.dispatch.cpp`, commit 802cf95. <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src/filter.dispatch.cpp> (accessed 2026-10-10)
19. OpenCV 4.x documentation. "Image Filtering" (`filter2D`) and "Motion Analysis and Object Tracking" (`phaseCorrelate`), generated from `imgproc.hpp` at commit 802cf95. <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/include/opencv2/imgproc.hpp> (accessed 2026-10-10)
20. OpenCV 4.x documentation. "Operations on arrays" (`dft`, `DftFlags`, `getOptimalDFTSize`, `mulSpectrums`), generated from `core.hpp` and `core/base.hpp` at commit 802cf95. <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/core/include/opencv2/core.hpp> (accessed 2026-10-10)
21. OpenCV tutorial sample, `discrete_fourier_transform.cpp`, commit 802cf95. <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/samples/cpp/tutorial_code/core/discrete_fourier_transform/discrete_fourier_transform.cpp> (accessed 2026-10-10)
22. NumPy documentation. `numpy.fft.fftshift`, `ifftshift` and `fftfreq`, from `numpy/fft/_helper.py` at commit 70fa998. <https://github.com/numpy/numpy/blob/70fa99843c75ae12434805bb4b1b07b94598c5c9/numpy/fft/_helper.py> (accessed 2026-10-10)
23. NumPy documentation. `numpy.fft` normalisation, `fft2`, `rfft` and `rfft2`, from `numpy/fft/_pocketfft.py` at commit 70fa998. <https://github.com/numpy/numpy/blob/70fa99843c75ae12434805bb4b1b07b94598c5c9/numpy/fft/_pocketfft.py> (accessed 2026-10-10)
24. SciPy source, `scipy/signal/_signaltools.py` (`choose_conv_method`, `fftconvolve`, `oaconvolve`), commit 95e01a4. <https://github.com/scipy/scipy/blob/95e01a4004e2781c91a26d9836d82c103dd8513c/scipy/signal/_signaltools.py> (accessed 2026-10-10)
25. scikit-image source, `phase_cross_correlation`, commit b700edc. <https://github.com/scikit-image/scikit-image/blob/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/registration/_phase_cross_correlation.py> (accessed 2026-10-10)
26. SciPy documentation. `scipy.fft.next_fast_len`, from `scipy/fft/_helper.py` at commit 95e01a4. <https://github.com/scipy/scipy/blob/95e01a4004e2781c91a26d9836d82c103dd8513c/scipy/fft/_helper.py> (accessed 2026-10-10)
