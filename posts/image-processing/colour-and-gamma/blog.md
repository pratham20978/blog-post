---
title: "Colour and Gamma: Luma, Luminance and the Spaces in Between"
slug: colour-and-gamma
date: 2026-10-15
updated: 2026-10-15
summary: "An 8-bit pixel is an sRGB code, not light: decode before you blur or resize, and know that BGR2GRAY returns BT.601 luma, not luminance. Worked by hand."
tags: [algorithms, image-processing, gamma-correction, srgb, colour-space, opencv]
category: algorithms
categories: [algorithms]
tier: L3
difficulty: intermediate
series: image-processing
series_position: 13
prerequisites: ["the shared 5×5 patch and its Gaussian from part 1 of this series", "weighted averages", "powers, cube roots and a 3×3 matrix product"]
reading_minutes: 31
cover_image_url: "COVER"
cover_image_alt: "The sRGB curve over linear light with a chord from code 40 to code 200; a tangerine gap marks the chord's 120 below the curve's 148.7"
canonical_url: "https://canery.in/blogs/colour-and-gamma"
---

> [!NOTE]
> **Insights** — An 8-bit pixel value is a code, not an amount of light: sRGB maps light to codes through a curve close to a 2.2 power, so code 128 sends 21.6% of white's light, not half. A weighted sum means something physical only after decoding: averaged as light, the patch's 40 and 200 give code 148.7, not 120. `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` applies BT.601's 0.299, 0.587 and 0.114 to the codes, which is luma, not CIE luminance. The two agree on greys and part on colours: on the azure (40, 200, 255) luma reads 158, while the grey of equal luminance is 186.

**Level:** intermediate · **You need:** *Image Processing by Hand* (part 1 of this series) for the 5×5 patch and its Gaussian, weighted averages, and powers, cube roots and a 3×3 matrix product · **Time:** ~31 min

This is part 13 of *Image Processing by Hand*, and the part that stands most on its own. Part 1 warned in one paragraph that `BGR2GRAY` returns luma rather than luminance, and named this post for the full account; <!-- L40 --> Part 3, *Resampling and Aliasing: Interpolation Kernels in Practice*, sent the question of resizing gamma-encoded values here too. Nothing else from the series is assumed.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Encoding](#why-is-a-pixel-value-an-encoding) · [Grey weights](#where-do-the-grey-weights-come-from) · [Luma's error](#how-wrong-is-luma) · [Lab](#what-does-lab-add) · [Linear light](#which-operations-need-linear-light) · [The math](#the-math) · [Tooling map](#implementation-the-tooling-map) · [Limitations](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Nothing in this post was run against an image. The series' 5×5 patch is read as colour twice: its three grey levels 40, 200 and 255 become the red, green and blue of one pixel, the **azure** (40, 200, 255), and its 40 and 200 are read as sRGB codes for the blur. Every number is worked by hand from the standards' constants and cross-checked with plain Python using only `math`, including one pass over all 16,777,216 8-bit colours; that check is not published. IEC 61966-2-1, the sRGB standard, is sold, so its constants are quoted from the W3C's CSS Color 4 and from OpenCV's and scikit-image's source, which implement them. No OpenCV, scikit-image, Pillow or MATLAB call was executed: library behaviour comes from source read at pinned commits and releases and from MathWorks' documentation. Figure 5's spectral locus is plotted from the CIE's published table. There are no timings or measured curves.

## Why this matters

Halve a picture of one-pixel black and white stripes with any resize that averages neighbours, and every output pixel is their average, code 127.5. From across the room the stripes looked like a grey sending half of white's light; code 127.5 sends 21.4%. The result looks darker than the stripes did, and the grey that matches them is code 187.5.

Convert a saturated green to grey with `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` and you get 150; the grey with the same luminance is 220. Neither is a bug. Both follow from one fact: an 8-bit pixel value is an encoded number, and a weighted sum of encoded numbers is not the encoding of the weighted sum. This post works out when a pixel value is a physical quantity and when it is an encoding, and which library call computes which.

## The problem

A pixel in an 8-bit image holds a **code value**, an integer from 0 to 255 per channel. The light a display sends for it is not proportional to the code. A **transfer function** connects the two: a camera or renderer **encodes** light into codes, and the display **decodes** codes back into light. Numbers proportional to light are called **linear light**; numbers after the curve are **encoded**, often "gamma-encoded" after **gamma**, the exponent that summarises the curve. The usual encoding for computer graphics and the web is **sRGB**, standardised as IEC 61966-2-1 in 1999 and the default colour space of CSS. <!-- L01 -->

So two kinds of number share the same 0–255 range, and image code mixes them up in four places:

- **Weighted sums.** A blur, a resize, a composite and an average are all weighted sums. Should they add up light, or codes?
- **Grey conversion.** A grey is a weighted sum of three channels. Which weights, applied to which numbers?
- **Colour spaces.** A conversion to another colour space, such as CIE XYZ or Lab, both introduced below, starts from one of the two kinds. Which does a library's conversion assume?
- **Comparisons.** Thresholds and colour differences are judgements about appearance. On which scale are equal steps equal?

What makes this hard is that nothing in a NumPy array says which kind it holds, and library functions with similar names assume different things, as the tooling map at the end shows. The problem is to know, for each operation, which kind of number it needs, and for each call, which kind it computes.

## Worked example

Five steps: decode three codes, carry one colour into XYZ and then into Lab, compute its two greys, and blur one edge two ways.

### Step 1: decode three codes

Divide a code by 255 to get v between 0 and 1. The sRGB decode is a straight line for the darkest codes and a power curve above them: <!-- L02 -->

$$
L = \frac{v}{12.92} \;\text{ if } v \le 0.04045, \qquad L = \left(\frac{v + 0.055}{1.055}\right)^{2.4} \;\text{ otherwise}
$$

The patch's three levels decode as follows. Code 40 is v = 0.1569, so L = ((0.1569 + 0.055)/1.055)^2.4 = 0.0212: 2.1% of white's light. Code 200 decodes to 0.5776, and code 255 to exactly 1. Code 128, the middle of the range, sends 21.6%.

The scale on which codes are nearly even is lightness. **Lightness**, written L\*, is the scale the International Commission on Illumination (CIE) defined for how light a grey looks, from 0 for black to 100 for white; it grows roughly as the cube root of light. <!-- L22 --> <!-- L23 --> Code 40 has L\* 16.1, code 128 has 53.6 and code 200 has 80.6. The grey that looks halfway between black and white, L\* 50, is code 119, and it sends only 18.4% of white's light. Figure 1 lines up the three scales.

![Three aligned rulers, sRGB code, lightness L* and linear light, with codes 40, 119, 128, 200 and 255 joined to their places on the other two](FIG_01)

*Figure 1 — Codes sit close to lightness and far from light. Code 119 looks halfway between black and white but sends 18.4% of white's light. Computed from the sRGB and CIELAB definitions.*

### Step 2: one colour, into XYZ

Read the three levels as one pixel: red 40, green 200, blue 255. That is the azure, a light sky blue, and decoded it is (0.0212, 0.5776, 1.0000) in linear light.

A display's red, green and blue are three lights. Colour science describes any light by three **tristimulus values**, X, Y and Z: the amounts of three reference stimuli that a standard observer would mix to match it. The CIE fixed that observer's matching functions in 1931 and chose them so that the one behind Y is the eye's sensitivity to brightness. <!-- L20 --> So **Y is luminance**, the brightness of a light as the eye weighs it. <!-- L21 --> For linear sRGB, XYZ is one matrix product: <!-- L42 -->

$$
\begin{pmatrix} X \\ Y \\ Z \end{pmatrix} = \begin{pmatrix} 0.4124 & 0.3576 & 0.1805 \\ 0.2126 & 0.7152 & 0.0722 \\ 0.0193 & 0.1192 & 0.9505 \end{pmatrix} \begin{pmatrix} R \\ G \\ B \end{pmatrix}
$$

For the azure, X = 0.4124 × 0.0212 + 0.3576 × 0.5776 + 0.1805 × 1 = 0.3958. In the same way Y = 0.4898 and Z = 1.0198. Its luminance is 49.0% of white's.

### Step 3: into Lab

**CIELAB**, or Lab, re-expresses XYZ so that equal distances look roughly equally different. <!-- L22 --> It divides each value by the white's, here (0.9505, 1, 1.0890), takes cube roots, and combines them: <!-- L23 -->

- ratios to white (0.4164, 0.4898, 0.9364), cube roots (0.7467, 0.7883, 0.9783);
- L\* = 116 × 0.7883 − 16 = 75.4, the lightness;
- a\* = 500 × (0.7467 − 0.7883) = −20.8, on the green side of the red–green axis;
- b\* = 200 × (0.7883 − 0.9783) = −38.0, on the blue side of the yellow–blue axis.

The azure is (75.4, −20.8, −38.0) in Lab: light, and well away from grey.

### Step 4: two greys

There are two ways to turn this pixel into a grey.

**Luma**, written Y′, applies weights to the codes themselves. `cv2.cvtColor` with `COLOR_BGR2GRAY` uses the weights of BT.601, the ITU's recommendation for digital studio television: <!-- L27 --> 0.299 × 40 + 0.587 × 200 + 0.114 × 255 = 158.4, which OpenCV's 8-bit path rounds to 158.

**Luminance** takes Y from step 2, 0.4898, and encodes it back into a code: 1.055 × 0.4898^(1/2.4) − 0.055 = 0.7286, which is code 185.8, so 186. That is the grey that sends the same light as the azure.

The two greys are 28 levels apart. The luma grey, 158, has L\* 65.3: 10.2 below the azure's 75.4, ten times the step Poynton takes as roughly the threshold of visibility. <!-- L12 --> Figure 2 draws both paths.

![The azure (40, 200, 255) decoded, turned into XYZ and Lab, with luma 158 taken from the codes and the luminance grey 186 from Y](FIG_02)

*Figure 2 — One pixel, two greys. Luma weighs the codes and gives 158; luminance weighs the light and, encoded back, gives 186. Worked by hand.*

### Step 5: one blur, two encodings

Row r0 of the patch is `40 40 40 200 200`, a step between c2 and c3. Blur it with the series' 3×3 Gaussian, whose weights along a row are 0.239, 0.522 and 0.239. In codes, c2 becomes 0.761 × 40 + 0.239 × 200 = 78.2, and c3 becomes 161.8.

In light, decode first. Then c2 becomes 0.761 × 0.0212 + 0.239 × 0.5776 = 0.1542, which encodes to code 109.4, and c3 becomes 0.4446, code 177.9. The blur done in light is 31 codes brighter at c2 and 16 at c3. Each blur is symmetric in its own units: halfway between 40 and 200 is code 120, but halfway between their lights, 0.2994, is code 148.7. Figure 3 plots both.

![The step 40 40 40 200 200 blurred in codes (78.2 and 161.8 at the edge) and in light (109.4 and 177.9), plotted as codes and as light](FIG_03)

*Figure 3 — The same weights, two answers. Blurring codes makes the edge symmetric in codes; blurring light makes it symmetric in light, and in codes it sits higher. Computed from the definitions.*

## Intuition

Telephone networks store speech **companded**: each sample passes through a curve that gives quiet sounds more levels before it is quantised, and the receiver expands it again. Sharma and Trussell make the comparison for gamma: encoding before quantising puts the coarse steps where the eye is least sensitive and hides the contours. <!-- L08 --> And just as you cannot mix two companded audio streams by adding their samples, you cannot add up light by adding codes. Decode, add, encode.

The analogy breaks in two places. A sound sample is signed and swings either side of silence, while light never goes below black, and sRGB's curve has a straight toe so that code 0 is exactly black. And colour has three channels with different weights, which a sound sample does not.

The deeper point is that luma and the blurred step make the same mistake. A blur is a weighted average of neighbouring codes; luma is a weighted average of one pixel's three codes. Both average after the curve instead of before it. The sRGB curve bends downward everywhere, which makes it **concave**, so an average of codes is never above the code of the average light, and is below it whenever the values differ, unless all of them sit on the straight toe, codes 0 to 10. That is **Jensen's inequality**, and it is why the step's midpoint is 120 instead of 148.7. Luma would come out darker for the same reason even with luminance's own weights; BT.601's older weights add a second error, which the section on luma separates out.

## Why is a pixel value an encoding?

### Eight bits, spent on lightness

An 8-bit channel has 256 codes. Spend them evenly in light, and the darkest tenth of lightness gets 3 codes while the brightest tenth gets 61: each step near black jumps up to 3.5 units of L\*, while near white the steps shrink to 0.15. Spend them along the sRGB curve, and every tenth of lightness gets between 21 and 29 codes, with no step larger than 0.51. Figure 4 counts them.

![Codes per tenth of lightness: sRGB spends 21 to 29 codes on every band, linear 8-bit coding 3 on the darkest band and 61 on the brightest](FIG_04)

*Figure 4 — Where the 256 codes go. The sRGB curve spreads them almost evenly in lightness; linear coding crowds them into the highlights. Computed from the definitions.*

Poynton takes one unit of L\* as roughly the threshold of visibility, and Sharma and Trussell give about 2.3 in ΔE\*ab, the Lab distance, for a just-noticeable difference. <!-- L12 --> Linear 8-bit coding has 15 steps above the first figure and 4 above the second, all at the dark end, which is where banding shows. To shade a 100:1 range in steps of 1%, Poynton counts about 9,900 codes, about 14 bits, for linear coding, and about 463, about 9 bits, for a ratio-like curve. <!-- L09 --> One number makes the same point: L\* 50 is 18.4% of white's light, which is code 119 in sRGB and code 47 in linear 8-bit coding. The sRGB authors give 46 for the same example. <!-- L06 -->

So the curve is not the correction of a defect. Poynton argues that the main purpose of gamma correction is to code light into a **perceptually uniform** domain, where one code step looks about the same size anywhere on the scale, and that a CRT's own nonlinearity happened to be close to the inverse of lightness perception. <!-- L10 --> sRGB, BT.709, Adobe RGB and DCI-P3 all code values this way. <!-- L11 -->

### The curve itself

sRGB uses the primaries of BT.709, the high-definition television standard, and a D65 white, both introduced in the next section. <!-- L03 --> Its decode is the two-piece formula of step 1. <!-- L02 --> Its proposers described it as a close fit to a plain 2.2 power, the receiver gamma NTSC had assumed, with an offset that lets it invert cleanly in integer arithmetic. <!-- L05 --> <!-- L18 --> The fit is close in the midtones and poor near black: code 118 decodes to 0.181 against the power's 0.184, but code 10 decodes to 0.0030 against 0.0008, a factor of 3.8.

The straight toe has a small history. The 1996 proposal switched from line to curve at 0.03928, or 0.00304 in light. The standard switches at 0.04045, or 0.0031308, and W3C's archived copy of the proposal notes that standardisation corrected a small rounding error. <!-- L04 --> <!-- L02 --> The geometry is easy to check. A line from the origin just touches the power curve at the encoded value 0.055/1.4 = 0.0392857, with slope 12.9232; the proposal printed that point truncated, as 0.03928. Rounding the slope to 12.92 makes the line cross the curve twice instead, at 0.03815 and 0.04045, and the standard takes the upper crossing, where the two pieces meet. For 8-bit data it makes no difference: code 10 is 0.0392 and code 11 is 0.0431, so no code falls between the two thresholds. In 16-bit data, 76 codes do.

## Where do the grey weights come from?

### Luminance from primaries

Any light can be placed by its **chromaticity** (x, y), its X and Y divided by X + Y + Z: the colour of the light without its amount. The pure spectral colours trace the horseshoe-shaped **spectral locus** in Figure 5, plotted from the CIE's 1931 tables. <!-- L20 --> A display is fixed by three **primaries**, the chromaticities of its red, green and blue, and a **white point**, the chromaticity it shows when all three are equal. For BT.709 and sRGB the primaries are red (0.64, 0.33), green (0.30, 0.60) and blue (0.15, 0.06), and the white is **D65**, a standard daylight at (0.3127, 0.3290). <!-- L03 -->

Those eight numbers fix the 3×3 matrix of step 2, as the math section derives, and its middle row is luminance: 0.2126, 0.7152 and 0.0722 to four decimals, or 0.212639, 0.715169 and 0.072192 in full. <!-- L42 --> Green dominates because the eye is most sensitive there: the CIE's luminous efficiency function, identical to its Y matching function, peaks at 555 nm. <!-- L20 -->

### Where 0.299 comes from

Run the same computation on the primaries of NTSC, the US colour-television standard adopted in 1953: red (0.67, 0.33), green (0.21, 0.71) and blue (0.14, 0.08). Its white is **Illuminant C**, <!-- L17 --> at the CIE's (0.31006, 0.31617). <!-- L19 --> The middle row comes out as 0.2989, 0.5866 and 0.1145, which is BT.601's 0.299, 0.587 and 0.114.

BT.601 itself specifies different primaries, for 625-line and 525-line systems, with a D65 white. <!-- L16 --> They would give 0.222, 0.707, 0.071 and 0.212, 0.701, 0.087. The ITU records why the old numbers stayed: the later colour systems PAL and SECAM took their coefficients from the 1953 primaries, and in every system the coding coefficients still come from them, though the phosphors of real tubes have changed. <!-- L17 --> Figure 5 draws the three triangles.

![CIE xy diagram with the spectral locus and the BT.709, NTSC 1953 and BT.601 625-line triangles, each with its luminance weights](FIG_05)

*Figure 5 — Weights belong to primaries and a white. The 1953 NTSC triangle with white C gives 0.299/0.587/0.114; BT.709's with D65 gives 0.2126/0.7152/0.0722. Spectral locus plotted from the CIE's 1931 table (CC BY-SA 4.0).*

### Luma: the same weights on codes

Television never applied these weights to light. BT.601 builds its luminance signal from the **gamma pre-corrected** primaries, E′R, E′G and E′B, and BT.709 does the same with its own weights. Both standards call the result the luminance signal, and the prime is the only clue that it is not CIE luminance. <!-- L15 --> <!-- L13 --> Video engineers call it **luma**, and Poynton's colour FAQ says the 1953 coefficients remain right for luma and wrong for the luminance of modern displays. <!-- L26 --> JPEG files in JFIF, the JPEG File Interchange Format, store this quantity: each pixel becomes a luma channel, Y = 0.299R + 0.587G + 0.114B of the 8-bit codes, plus two colour-difference channels, and a one-channel JFIF file holds the luma alone. <!-- L39 -->

## How wrong is luma?

On a grey, luma is exact. The weights sum to 1, so three equal codes give the same code back, and encoding the luminance gives that code too. Off the grey axis the two part. Figure 6 sets `BGR2GRAY`'s luma beside the luminance grey for nine colours.

![Nine colours with their luma and luminance greys: red 76 and 127, green 150 and 220, blue 29 and 76, pink 206 and 200, grey 128 twice](FIG_06)

*Figure 6 — Luma against luminance. Equal on grey, up to 70 codes darker on green, and 6 codes brighter on a pale pink. Computed from the definitions over all 16,777,216 8-bit colours.*

Pure blue gives 29 against 76, red 76 against 127 and green 150 against 220. Across all 16,777,216 8-bit colours, luma minus the luminance grey runs from −70.2 codes at pure green to +5.9 at the pale pink (255, 172, 255). In lightness, pure green's luma grey is 25.8 units of L\* too dark.

Two errors add up. The first is the curve: luma averages codes, and Jensen's inequality makes that average no brighter than the code of the average light. With BT.709's weights on the codes, luma never exceeds the luminance grey for any 8-bit colour. The second is the weights: BT.601's 1953 weights give red and blue more and green less than sRGB's primaries call for. That pulls greens down further and lifts reds and blues part of the way back; in pinks, where green is the dark channel, the second error outweighs the first and luma comes out brighter.

When does it matter? A threshold, a histogram or a brightness measurement meant to track light should use luminance. A grey for display or for compression can be luma, which is what video and JFIF chose. <!-- L39 --> What matters is knowing which one you have.

## What does Lab add?

### Lightness, then colour

Luminance measures light, not appearance: XYZ is perceptually non-uniform, so equal steps in Y do not look equal. The CIE's answer in 1976 was two approximately uniform spaces, CIELAB and CIELUV. <!-- L22 --> L\* is a cube root of Y relative to the white, with a straight segment near black, and a\* and b\* measure red against green and yellow against blue from the cube roots of X, Y and Z. <!-- L23 --> The distance between two Lab colours, ΔE\*ab, is their colour difference, and about 2.3 is just noticeable. <!-- L12 -->

### Lab depends on its white

Every Lab coordinate is relative to a **reference white**, and libraries choose different ones. OpenCV, scikit-image and MATLAB use D65 by default, sRGB's own white, so the azure is (75.4, −20.8, −38.0). <!-- L30 --> <!-- L34 --> <!-- L38 --> CSS uses D50, which is also the white of colour management by International Color Consortium (ICC) profiles and of the Lab in image editors. It converts sRGB colours with the linear **Bradford** transform, a **chromatic adaptation**: a matrix that re-expresses a colour as it would look under the other white. <!-- L24 --> The same azure becomes (74.8, −26.4, −39.0), 5.8 ΔE away. Both are correct; they are two spaces with one name.

scikit-image lets you pick another white, but its `xyz2lab` only divides by it, without adapting the colour. <!-- L34 --> Ask for D50 and sRGB's white comes out at (100, −2.4, −19.4), visibly blue, where it should be (100, 0, 0). Figure 7 places these points.

![The a*b* plane with the azure under D65, CSS's adapted D50 and scikit-image's unadapted D50, and sRGB white moved to b* −19.4](FIG_07)

*Figure 7 — One pixel, three Labs. Adapting to D50 moves the azure 5.8 ΔE; swapping the white without adapting moves it further and tints white blue. Computed from the definitions.*

### Still not brightness

Neither Y nor L\* is perceived brightness for saturated colours: chromatic colours look lighter than greys of the same luminance, the Helmholtz–Kohlrausch effect. <!-- L25 --> Luminance is the right grey for physics, and L\* the right scale for differences between greys; neither models how bright a saturated colour looks.

## Which operations need linear light?

### The rule

The sRGB authors drew the line in 1996: optical and synthetic operations, such as alpha masking, work in linear intensity, while visual operations, compression and most devices work in a nearly perceptually uniform space. <!-- L06 --> PNG's specification says the same for **alpha compositing**, layering a foreground over a background with opacity α: the output is α × foreground + (1 − α) × background, computed on intensity samples, not gamma-encoded ones. <!-- L07 --> Anything that models light adding up belongs in linear light: blurring, defocus, resizing, compositing, exposure, averaging frames. Anything that models perception belongs in an encoded or perceptual space: quantisation, compression, colour differences and thresholds meant to match appearance.

### Why codes average dark

Figure 8 draws the encode curve with two chords. The chord from code 40 to code 200 passes, at their average light 0.2994, through code 120, the answer computed on codes; the curve at that light is code 148.7, the answer computed on light. A concave curve lies above every chord, so for any weights that are non-negative and sum to 1, the average of codes is at most the code of the average light. The stripes of the opening are the extreme case: the chord from code 0 to code 255 gives 127.5 at half light, where the curve gives 187.5.

![The sRGB curve with chords from code 40 to 200 and 0 to 255; at the average light the chords give 120 and 127.5, the curve 148.7 and 187.5](FIG_08)

*Figure 8 — Why averaging codes darkens. Each chord is an average of codes, and the curve above it is the same average done in light. Computed from the definitions.*

The patch's impulse shows the size of the effect on a real neighbourhood. Part 1's 3×3 box gave 64 at the impulse and its σ = 0.8 Gaussian gave 98.6; <!-- L40 --> averaged as light and encoded back, they are 101 and 146.1.

Two limits apply. Jensen's inequality needs non-negative weights, so a sharpening kernel, or the negative lobes of the bicubic and Lanczos kernels in Part 3, can land on either side. And none of the common calls decides for you: OpenCV's `resize` and `GaussianBlur`, Pillow's `resize` and scikit-image's `resize` take no transfer function and weight whatever values they are given. <!-- L32 --> Decode, operate, encode.

## The math

| Symbol | Meaning |
|---|---|
| $c$, $v = c/255$ | an 8-bit code and its normalised value |
| $L$; $g$, $g^{-1}$ | linear light from 0 to 1; the sRGB encode and decode |
| $R, G, B$ | the three channels in linear light |
| $X, Y, Z$ | CIE tristimulus values; $Y$ is luminance |
| $Y'$ | luma: weights applied to the codes |
| $(x_k, y_k)$, $(x_w, y_w)$ | chromaticity of primary $k$ and of the white; $z = 1 - x - y$ |
| $L^*, a^*, b^*$; $X_n, Y_n, Z_n$ | CIELAB coordinates; the white's tristimulus values |

**Encode and decode.** <!-- L02 -->

$$
g(L) = \begin{cases} 12.92\,L & L \le 0.0031308 \\ 1.055\,L^{1/2.4} - 0.055 & \text{otherwise} \end{cases} \qquad g^{-1}(v) = \begin{cases} v/12.92 & v \le 0.04045 \\ \left(\dfrac{v + 0.055}{1.055}\right)^{2.4} & \text{otherwise} \end{cases} \tag{1}
$$

The encode is a straight line near black and a 1/2.4 power above it, and the decode undoes it: v = 0.1569, code 40, decodes to 0.0212.

**From primaries to the matrix.**

$$
M = \begin{pmatrix} x_r/y_r & x_g/y_g & x_b/y_b \\ 1 & 1 & 1 \\ z_r/y_r & z_g/y_g & z_b/y_b \end{pmatrix} \begin{pmatrix} S_r & 0 & 0 \\ 0 & S_g & 0 \\ 0 & 0 & S_b \end{pmatrix}, \qquad M \begin{pmatrix} 1 \\ 1 \\ 1 \end{pmatrix} = \begin{pmatrix} x_w/y_w \\ 1 \\ z_w/y_w \end{pmatrix} \tag{2}
$$

Each column is one primary's XYZ at unit luminance, scaled so that equal red, green and blue make the white. The middle row of M is then $(S_r, S_g, S_b)$: the luminance weights are exactly those scales.

<details>
<summary>Solving (2) for BT.709 and for NTSC 1953</summary>

For BT.709 with D65 the unscaled columns are (1.9394, 1, 0.0909), (0.5, 1, 0.1667) and (2.5, 1, 13.1667), and the white is (0.9505, 1, 1.0891). The second equation says $S_r + S_g + S_b = 1$; with the other two, the solution is $S = (0.212639, 0.715169, 0.072192)$, which is sRGB's luminance row. The first row of M is then (0.4124, 0.3576, 0.1805), as in step 2.

For NTSC 1953 with Illuminant C at (0.31006, 0.31617) the columns are (2.0303, 1, 0), (0.2958, 1, 0.1127) and (1.75, 1, 9.75), the white is (0.9807, 1, 1.1822), and $S = (0.2989, 0.5866, 0.1145)$. With C rounded to (0.310, 0.316), as BT.470 prints it, the row is 0.2990, 0.5864, 0.1146: the third decimal of the green weight depends on the fourth decimal of the white.

</details>

**Luminance and luma.** <!-- L13 --> <!-- L15 -->

$$
Y = 0.2126\,R + 0.7152\,G + 0.0722\,B, \qquad Y' = 0.299\,c_R + 0.587\,c_G + 0.114\,c_B \tag{3}
$$

The first weighs light with sRGB's own weights; the second weighs codes with the 1953 weights. On the azure, Y = 0.4898, whose code is 185.8, and Y′ = 158.4.

**Jensen's inequality.** For weights $w_k \ge 0$ that sum to 1,

$$
g\Big(\sum_k w_k L_k\Big) \ge \sum_k w_k\, g(L_k) \tag{4}
$$

because g is concave. The left side is a blur in light, encoded; the right side is the same blur on codes. On the step: 148.7 against 120 at the midpoint, and 109.4 against 78.2 at c2.

**CIELAB.** <!-- L23 -->

$$
L^* = 116\, f(Y/Y_n) - 16, \qquad a^* = 500\,\big(f(X/X_n) - f(Y/Y_n)\big), \qquad b^* = 200\,\big(f(Y/Y_n) - f(Z/Z_n)\big) \tag{5}
$$

Here $f(t) = t^{1/3}$ above $(24/116)^3$ and $\tfrac{841}{108}\,t + \tfrac{16}{116}$ below it; in 2002 the CIE replaced the decimals 0.008856 and 7.787 with these fractions. On the azure, f gives 0.7467, 0.7883 and 0.9783, and Lab is (75.4, −20.8, −38.0).

## Implementation: the tooling map

Every entry below maps to a section above. **None of it was executed for this post**; it comes from source at pinned commits and releases and from MathWorks' documentation. Figure 9 is the same map in one picture.

![Grid comparing OpenCV, scikit-image, Pillow and MATLAB on grey weights, decoding before grey, XYZ and Lab, Lab white and resize](FIG_09)

*Figure 9 — Four libraries. Every grey call weighs codes; only the calls marked in blue decode sRGB first and work on light.*

### OpenCV

| Want | Call | Note |
|---|---|---|
| grey | `cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)` | BT.601 luma of the codes; 8-bit and 16-bit use the integers 9798, 19235 and 3735 over 2^15 <!-- L27 --> |
| XYZ | `cv2.COLOR_BGR2XYZ` | the matrix applied to whatever it is given: on codes, Y is not luminance (170 for the 8-bit azure) <!-- L29 --> <!-- L43 --> |
| Lab | `cv2.COLOR_BGR2Lab`; `cv2.COLOR_LBGR2Lab` | the first decodes sRGB, though the documentation never says so; the second takes linear input; white (0.950456, 1, 1.088754); 8-bit stores L·255/100, a + 128, b + 128 <!-- L30 --> |
| resize, blur | `cv2.resize`, `cv2.GaussianBlur` | no transfer function: they weight the values given <!-- L32 --> |

`cvtColor` offers the grey conversion to a hardware layer first. For 8-bit grey none of them changes the answer: Intel IPP takes only 32-bit float input, the ARM (Carotene) and RISC-V layers use the same 15-bit weights, and KleidiCV 26.03 does not take the conversion at all. <!-- L28 --> The behaviour above is the same in 4.10.0, 4.14.0 and 5.0.0. <!-- L31 -->

### scikit-image, Pillow and MATLAB

| Want | Call | Note |
|---|---|---|
| scikit-image grey | `skimage.color.rgb2gray(img)` | documented as luminance, but 0.2125, 0.7154 and 0.0721 on the codes: BT.709-style luma, 0.6665 for the azure <!-- L33 --> |
| scikit-image luminance | `skimage.color.rgb2xyz(img)[..., 1]` | decodes sRGB first: 0.4897 <!-- L34 --> |
| scikit-image Lab | `skimage.color.rgb2lab(img)` | D65 by default; another `illuminant` swaps the white without adapting <!-- L34 --> |
| Pillow grey | `img.convert("L")` | BT.601 luma in 16-bit integers, "assuming nonlinear RGB" in its source <!-- L36 --> |
| MATLAB | `rgb2gray`, `rgb2lin`, `rgb2lab` | 0.298936…, 0.587043…, 0.114021…, called luminance (E′y); `rgb2lin` decodes; `rgb2lab` decodes, D65 by default <!-- L37 --> <!-- L38 --> |

The weights travel in odd ways. scikit-image's 0.2125/0.7154/0.0721 and the six-decimal matrix that OpenCV and scikit-image share both appear in Poynton's 1997 colour FAQ, where the weights are meant for linear light. <!-- L26 --> <!-- L33 --> scikit-image applies them to codes, and its module docstring describes its central space as linear sRGB, though `rgb2xyz` decodes. <!-- L35 --> OpenCV and Pillow use the same BT.601 weights at 15 and 16 bits, and they disagree by one grey level on 21,745 of the 16,777,216 colours; the first is (0, 1, 201), whose exact luma is 23.501.

### The worked example, in OpenCV and scikit-image

```python
import numpy as np
import cv2
from skimage.color import rgb2gray, rgb2xyz

px = np.array([[[255, 200, 40]]], np.uint8)          # BGR order: the azure (R, G, B) = (40, 200, 255)
rgb = px[..., ::-1]

gray = cv2.cvtColor(px, cv2.COLOR_BGR2GRAY)          # 158: BT.601 luma of the codes
xyz8 = cv2.cvtColor(px, cv2.COLOR_BGR2XYZ)           # Y = 170: the matrix on codes, no decode
lab = cv2.cvtColor(px.astype(np.float32) / 255, cv2.COLOR_BGR2Lab)   # about (75.4, -20.8, -38.0)

lum = rgb2xyz(rgb)[0, 0, 1]                          # 0.4897: luminance, decoded first
luma709 = rgb2gray(rgb)[0, 0]                        # 0.6665: BT.709-style weights on codes

v = rgb[0, 0] / 255
lin = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)
grey = 1.055 * (lin @ [0.2126, 0.7152, 0.0722]) ** (1 / 2.4) - 0.055   # 0.7286: code 185.8
```

This was not run for this post. The comments state what the worked example predicts.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** resizing, blurring or alpha-blending 8-bit sRGB images as they are. Every weighted sum then averages codes, and wherever values differ the result is darker than the light would be: one-pixel black and white stripes halve to code 127.5, which sends 21.4% of white's light instead of 50%. Decode to linear light in floating point, operate, then encode.

- **Calling `BGR2GRAY` luminance.** It is BT.601 luma of the codes, up to 70 levels from the luminance grey on saturated colours. MATLAB's documentation calls the same weights luminance (E′y), and scikit-image documents its own luma as luminance. <!-- L37 --> <!-- L33 -->
- **Taking Y from `BGR2XYZ` on 8-bit data.** OpenCV applies the matrix to the codes without decoding, so for the azure "Y" is 170 of 255, not 49% of white. Decode first, or use `BGR2Lab`, which decodes. <!-- L29 --> <!-- L30 -->
- **Reading 8-bit Lab as L\*.** OpenCV stores L·255/100 and adds 128 to a and b: the azure's L\* of 75.4 is stored as about 192. <!-- L30 -->
- **Changing the white without adapting.** scikit-image's `illuminant="D50"` turns sRGB white blue, b\* −19.4. For a D50 Lab that matches CSS or an image editor, adapt with Bradford first. <!-- L34 --> <!-- L24 -->
- **Decoding with a plain 2.2 power.** It is close in the midtones and off by a factor of 3.8 at code 10, which matters wherever the shadows carry signal: noise estimates, exposure fusion, dark scenes.
- **Treating video as sRGB.** BT.709's curve is the camera's encoding, and its reference display decodes with the curve of a separate recommendation, BT.1886; neither is sRGB's curve, so decoding video frames with sRGB's formula is an approximation. <!-- L14 -->
- **Decoding twice, or not at all.** A floating-point image may already hold linear light, depending on where it came from. Know which kind you hold before applying the decode.

## Key takeaways

- **An 8-bit pixel value is a code, not light.** sRGB spends the 256 codes almost evenly in lightness, so code 128 sends 21.6% of white's light and the middle grey sits at code 119.
- **Weighted sums are physical only on decoded values.** Blurs, resizes and composites on codes come out darker, by Jensen's inequality: 120 against 148.7 between the patch's 40 and 200.
- **Luma is not luminance.** `BGR2GRAY`, Pillow, MATLAB and JFIF JPEGs weigh codes with BT.601's 1953 weights; luminance decodes first and uses the primaries' own weights, 0.2126/0.7152/0.0722 for sRGB. They agree on greys and differ by up to 70 levels on colours.
- **Weights belong to primaries and a white.** 0.299/0.587/0.114 follow from the 1953 NTSC primaries and Illuminant C, not from BT.601's own primaries.
- **Lab is relative to a white.** D65 Lab and CSS's D50 Lab put the same pixel 5.8 ΔE apart, and swapping the white without adapting tints greys.

## Try it yourself

The exercises are pen and paper, matching the post; each names its rung.

### E1 — Reproduce: decode two codes

Decode codes 128 and 119 with equation (1), then compute their L\*.

**Self-check:** two light values and two lightnesses; one code should land within 0.1 of L\* 50.

<details><summary>Answer</summary>

Code 128 is v = 0.5020, so L = ((0.5020 + 0.055)/1.055)^2.4 = 0.2159, and L\* = 116 × 0.2159^(1/3) − 16 = 53.6. Code 119 is v = 0.4667, L = 0.1845 and L\* = 50.0. The middle of the code range, 128, is lighter than the middle of the lightness range, which is code 119.

</details>

### E2 — Inspect: the darkest and the brightest tenth

From Figure 4, read how many codes each encoding spends on L\* from 0 to 10 and on L\* from 90 to 100, and the ratio of the two for each encoding.

**Self-check:** four counts; one ratio near 1 and one far from it.

<details><summary>Answer</summary>

sRGB spends 28 codes on the darkest tenth and 29 on the brightest, a ratio of about 1. Linear 8-bit coding spends 3 and 61, a ratio of about 20: its codes crowd into the highlights, where the eye can barely tell neighbours apart.

</details>

### E3 — Predict: a colour where luma is brighter

Predict `BGR2GRAY` and the luminance grey for (R, G, B) = (255, 172, 255), and say which of the two errors in the section on luma decides which grey is brighter.

**Self-check:** two codes, and the brighter one named with its reason.

<details><summary>Answer</summary>

Luma is 0.299 × 255 + 0.587 × 172 + 0.114 × 255 = 206.3, so 206. For luminance, green 172 decodes to 0.4125, so Y = 0.2126 + 0.7152 × 0.4125 + 0.0722 = 0.5799, which is code 200.4, so 200. Luma is 5.9 codes brighter. The weights decide it: BT.601 gives red and blue 0.413 together against luminance's 0.285, and here they are the bright channels, which outweighs the darkening from the curve.

</details>

### E4 — Diagnose: luminance from BGR2XYZ

A colleague measures the azure's luminance as `cv2.cvtColor(px, cv2.COLOR_BGR2XYZ)[0, 0, 1] / 255` on the 8-bit pixel, gets 0.667, and cannot reconcile it with a light meter that reads 49% of white. Find the error and give the fix with its result.

**Self-check:** the missing step, the corrected value, and why the wrong value came out higher.

<details><summary>Answer</summary>

`BGR2XYZ` applies the matrix to the codes without decoding them, so 170/255 = 0.667 is a BT.709-weighted average of codes, not luminance. Decode first, 40, 200 and 255 to 0.0212, 0.5776 and 1, and apply the matrix in floating point: Y = 0.4898, or 0.4897 with OpenCV's six-decimal matrix. The wrong value is higher because the decode lies below the diagonal: every code between 0 and 255, divided by 255, is larger than the light it encodes, so a weighted sum of codes is never below the same sum of light, and here it is well above it.

</details>

## References

1. Sharma, G., and Trussell, H. J. "Digital Color Imaging." *IEEE Transactions on Image Processing* 6(7):901–932, 1997. doi:10.1109/83.597268. [Author posting](https://arxiv.org/abs/cs/0109116)
2. Anderson, M., Motta, R., Chandrasekar, S., and Stokes, M. "Proposal for a Standard Default Color Space for the Internet — sRGB." *IS&T/SID Color Imaging Conference* 4:238–245, 1996. [doi:10.2352/CIC.1996.4.1.art00061](https://doi.org/10.2352/CIC.1996.4.1.art00061)
3. Stokes, M., Anderson, M., Chandrasekar, S., and Motta, R. "A Standard Default Color Space for the Internet — sRGB," version 1.10, 1996, with W3C's note on standardisation. <https://www.w3.org/Graphics/Color/sRGB.html> (accessed 2026-10-15)
4. IEC 61966-2-1:1999. *Multimedia systems and equipment — Colour measurement and management — Part 2-1: Default RGB colour space — sRGB.* <https://webstore.iec.ch/en/publication/6169> (accessed 2026-10-15)
5. W3C. *CSS Color Module Level 4*, Candidate Recommendation Draft, 9 October 2026, §9.1, §10.2 and §19. <https://www.w3.org/TR/2026/CRD-css-color-4-20261009/>
6. ITU-R Recommendation BT.709-6 (06/2015). *Parameter values for the HDTV standards for production and international programme exchange.* <https://www.itu.int/rec/R-REC-BT.709-6-201506-I/en>
7. ITU-R Recommendation BT.601-7 (03/2011). *Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios.* <https://www.itu.int/rec/R-REC-BT.601-7-201103-I/en>
8. ITU-R Recommendation BT.470-6 (11/1998). *Conventional television systems*, Table 2 and Annex 2. <https://www.itu.int/rec/R-REC-BT.470-6-199811-S/en>
9. CIE. "Colour-matching functions of CIE 1931 standard colorimetric observer" (dataset, CC BY-SA 4.0). [doi:10.25039/CIE.DS.xvudnb9b](https://doi.org/10.25039/CIE.DS.xvudnb9b)
10. CIE. "CIE spectral luminous efficiency for photopic vision" (dataset, CC BY-SA 4.0). [doi:10.25039/CIE.DS.dktna2s3](https://doi.org/10.25039/CIE.DS.dktna2s3)
11. CIE 015:2018. *Colorimetry*, 4th edition, §8.2.1 and Table 9.1. [doi:10.25039/TR.015.2018](https://doi.org/10.25039/TR.015.2018)
12. W3C. *Portable Network Graphics (PNG) Specification (Third Edition)*, Recommendation, 24 June 2025, §13.16. <https://www.w3.org/TR/2025/REC-png-3-20250624/>
13. Hamilton, E. *JPEG File Interchange Format*, version 1.02, C-Cube Microsystems, 1992. <https://www.w3.org/Graphics/JPEG/jfif3.pdf>
14. Poynton, C. "The Rehabilitation of Gamma." *Proc. SPIE* 3299, Human Vision and Electronic Imaging III, 232–249, 1998. [doi:10.1117/12.320126](https://doi.org/10.1117/12.320126)
15. Poynton, C., and Funt, B. "Perceptual Uniformity in Digital Image Representation and Display." *Color Research & Application* 39(1):6–15, 2014. [doi:10.1002/col.21768](https://doi.org/10.1002/col.21768)
16. Robertson, A. R. "The CIE 1976 Color-Difference Formulae." *Color Research & Application* 2(1):7–11, 1977. [doi:10.1002/j.1520-6378.1977.tb00104.x](https://doi.org/10.1002/j.1520-6378.1977.tb00104.x)
17. Fairchild, M. D., and Pirrotta, E. "Predicting the Lightness of Chromatic Object Colors Using CIELAB." *Color Research & Application* 16(6):385–393, 1991. [doi:10.1002/col.5080160608](https://doi.org/10.1002/col.5080160608)
18. Poynton, C. "Frequently Asked Questions about Color," 1997, §9, §11 and §18. <https://poynton.ca/pdf/ColourFAQ.pdf> (accessed 2026-10-15)
19. OpenCV source, commit 802cf95: `color.simd_helpers.hpp`, `color_rgb.simd.hpp`, `color_rgb.dispatch.cpp`, `color_lab.cpp`, `colors.markdown` and the HAL layers. <https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src/color_lab.cpp> (accessed 2026-10-15)
20. OpenCV source, tags 4.10.0, 4.14.0 and 5.0.0. <https://github.com/opencv/opencv/blob/5.0.0/modules/imgproc/src/color_rgb.dispatch.cpp> (accessed 2026-10-15)
21. KleidiCV 26.03, OpenCV adapter `kleidicv_hal.h`. <https://gitlab.arm.com/kleidi/kleidicv/-/blob/26.03/adapters/opencv/kleidicv_hal.h> (accessed 2026-10-15)
22. scikit-image source, commit b700edc and release v0.26.0: `color/colorconv.py`, `transform/_warps.py`. <https://github.com/scikit-image/scikit-image/blob/v0.26.0/src/skimage/color/colorconv.py> (accessed 2026-10-15)
23. Pillow source, release 12.3.0: `libImaging/Convert.c`, `PIL/Image.py`. <https://github.com/python-pillow/Pillow/blob/12.3.0/src/libImaging/Convert.c> (accessed 2026-10-15)
24. MathWorks. "rgb2gray," "rgb2lin" and "rgb2lab." MATLAB and Image Processing Toolbox documentation, release R2026b. <https://www.mathworks.com/help/matlab/ref/rgb2gray.html> (accessed 2026-10-15)
