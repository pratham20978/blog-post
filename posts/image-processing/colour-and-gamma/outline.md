# Outline — Colour and Gamma: Luma, Luminance and the Spaces in Between

**Title:** Colour and Gamma: Luma, Luminance and the Spaces in Between (59 chars; the plan's title is
60 with a serial comma, so the comma goes, British style, to keep the series' under-60 rule. Part 3
names this post *Colour and Gamma*, which stays at the front. The search phrases — "luma vs
luminance", "gamma correction explained", "sRGB to linear", "BGR2GRAY weights", "why does resizing
in sRGB look wrong" — go into the summary, Insights and headings.)
**Slug:** `colour-and-gamma`
**Series:** `image-processing`, part 13 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** intermediate (the most standalone spoke: powers, cube roots and a 3×3 matrix product;
every colour term is taught in place) · **Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** about 6,700 words as the validator counts them (L3 range 5,000–7,500, references and math
tokens included) · **Figures:** 9 (L3 range 8–12; the plan estimated 9)
**Assumes:** Part 1, *Image Processing by Hand: Sample, Filter, Transform, Decide* — its four-stage
frame (one sentence), its 5×5 patch, its σ = 0.8 Gaussian and its `BGR2GRAY` paragraph, which this
post owns. Part 3, *Resampling and Aliasing: Interpolation Kernels in Practice*, handed "resizing
gamma-encoded values" here by name. Both named in plain text; Part 1 is live, Part 3 is built.
**Hands off:** nothing; a leaf. Camera pipelines end to end, HDR transfer functions and video beyond
BT.709 stay out of scope, as for the series.

Nothing is run against an image. The patch is read as colour twice, and the IMPORTANT block says so:
its three grey levels 40, 200 and 255 become the red, green and blue of one pixel, the **azure**
(40, 200, 255); and its 40 and 200 are read as sRGB codes for the blur. Every number is worked by hand
from the standards' constants and asserted in `assets/_data.py` (plain Python, `math` and `fractions`
only; private, not published), including one pass over all 16,777,216 8-bit colours. Library behaviour
carries a ledger key to source at pinned commits: OpenCV 802cf95 (and 4.10.0, 4.14.0, 5.0.0), KleidiCV
26.03, scikit-image b700edc (and v0.26.0), Pillow 12.3.0, MathWorks R2026b documentation.

**Checkpoints.** As with Parts 3–12, the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 26 sources, 15 peer-reviewed or standard with identifiers (floor 7), four scholarly databases
(OpenAlex, Crossref, Semantic Scholar, Google Scholar; floor 4) plus the ITU, CIE, W3C and IEC. The
survey is Sharma & Trussell 1997 (IEEE TIP), read in full; the sRGB authors' peer-reviewed 1996 paper
and their W3C proposal, BT.601-7, BT.709-6, BT.470-6, CIE 015:2018 and the CIE's open observer and
V(λ) tables were read in full; Poynton's 1998 SPIE paper from his archived reprint. IEC 61966-2-1 is
sold, so its constants come from CSS Color 4 and the OpenCV and scikit-image source. 43 claims. No
paper figure is reusable.
**B:** this file.

**Eight findings change what the plan expected.**
1. *The plan's luminance row is OpenCV's, rounded.* The standards print 0.2126/0.7152/0.0722 (BT.709
   item 3.2, the 1996 sRGB matrix); the exact row from the primaries and D65 is 0.212639, 0.715169,
   0.072192 (CSS's fractions). OpenCV and scikit-image document 0.212671/0.715160/0.072169, Poynton's
   1997 FAQ matrix, which rounds to the plan's 0.2127. The post uses 0.2126.
2. *BT.601's weights do not come from BT.601.* Its own 625- and 525-line primaries with D65 give
   0.222/0.707/0.071 and 0.212/0.701/0.087. The 1953 NTSC primaries with Illuminant C give
   0.2989/0.5866/0.1145 (C at the CIE's 0.31006, 0.31617), which is 0.299/0.587/0.114; BT.470-6
   Annex 2 says every system still codes with the 1953 coefficients though phosphors changed.
3. *Luma is not always darker than luminance.* Over all 16.7 million 8-bit colours, BT.601 luma minus
   the luminance-matched grey runs from −70.2 (pure green: 149.7 against 219.9) to +5.9 ((255, 172,
   255): 206.3 against 200.4). With equal weights (BT.709 luma, scikit-image's case) the luma is never
   brighter, which is Jensen's inequality on the concave encode; the pinks come from BT.601's 1953
   weights. Two errors, not one.
4. *Luma and the blurred step are the same inequality.* A weighted sum of codes against the code of a
   weighted sum of light: the blur's midpoint (120 against 148.7) and the azure's grey (158 against
   186 with the different weights) are both instances. The intuition section is built on this.
5. *The two sRGB thresholds are a tangent and a crossing.* The 1996 proposal's 0.00304/0.03928 is
   where a line from the origin with slope 12.9232 touches the curve, at exactly 0.055/1.4 = 0.0392857,
   printed truncated; rounding the slope to 12.92 makes
   the line cross the curve at 0.03815 and 0.04045, and the standard's 0.04045 is the upper crossing.
   No 8-bit code falls between 0.03928 and 0.04045 (code 10 is 0.0392, code 11 is 0.0431), so 8-bit
   decodes agree; 76 16-bit codes do not.
6. *OpenCV has three different "Y"s.* `BGR2GRAY` is BT.601 luma (158 on the azure); `BGR2XYZ` applies
   the six-decimal matrix to the codes without decoding (8-bit Y = 170, float Y = 0.666); `BGR2Lab`
   decodes first (L* 75.4), which its documentation never says. Only the last is CIE.
7. *scikit-image's "luminance" is BT.709 luma.* `rgb2gray` (documented "Compute luminance") applies
   Poynton's 0.2125/0.7154/0.0721 to the codes: 0.6665 on the azure, where `rgb2xyz` gives Y = 0.4897.
   Its `illuminant="D50"` swaps the white without adaptation: sRGB white becomes b* −19.4.
8. *Lab is a family indexed by its white.* The azure is (75.4, −20.8, −38.0) at D65 (OpenCV,
   scikit-image, MATLAB) and (74.8, −26.4, −39.0) at CSS's Bradford-adapted D50: ΔE 5.8 apart for the
   same pixel.

---

## The spine

An 8-bit pixel value is a code on the sRGB curve, not an amount of light. The curve exists because 8
bits spent evenly in light would band in the shadows: it spends them evenly in lightness instead.
Weighted sums are physical only on decoded values, so a blur, a resize or a composite on codes comes
out darker than the light would (Jensen's inequality on a concave curve). Grey conversion is a
weighted sum too: luminance weighs decoded channels with weights fixed by the primaries and white;
luma weighs the codes, with BT.601's 1953 weights in OpenCV, Pillow, MATLAB and every JPEG. Lab
re-encodes luminance for perception, relative to a white that libraries choose differently.

## Verified numbers (all asserted in `assets/_data.py`)

**Decode:** 40 → 0.021219 (2.1%), 200 → 0.577580 (57.8%), 255 → 1, 128 → 0.215861 (21.6%), 118 →
0.181164, 10 → 0.003035 (plain 2.2 power: 0.000805). L* of codes 40, 118, 119, 128, 200: 16.1, 49.6,
50.0, 53.6, 80.6. L* 50 ⇔ Y 0.184187 ⇔ sRGB code 118.9, linear 8-bit code 47.0.
**Azure (40, 200, 255):** linear (0.0212, 0.5776, 1.0000); XYZ with the 4-decimal matrix (0.3958,
0.4898, 1.0198); ratios to white (0.9505, 1, 1.0890): (0.4164, 0.4898, 0.9364); cube roots (0.7467,
0.7883, 0.9783); Lab (75.44, −20.76, −38.02). OpenCV matrix: (75.44, −20.77, −38.02). Luma 158.43 →
158 (OpenCV 15-bit and Pillow 16-bit both 158; MATLAB 158.44). Luminance 0.4898 → code 185.79 → 186.
L* of the luma grey 65.28 (Y 0.3440): 10.2 below the colour's 75.44. scikit-image rgb2gray 0.66653
(169.97). OpenCV BGR2XYZ Y: 8-bit 170, float 0.66644. 8-bit Lab ≈ (192, 107, 90) by the documented
scaling. D50 (CSS, Bradford): (74.79, −26.43, −38.95), ΔE 5.79. scikit-image illuminant D50 without
adaptation: white (100, −2.39, −19.38).
**Greys (luma / luminance grey):** red 76.2/127.1, green 149.7/219.9, blue 29.1/76.0, cyan
178.8/229.5, magenta 105.3/145.4, yellow 225.9/246.7, grey 128 128/128. All 2^24 colours: BT.601
luma − luminance grey in [−70.25 at (0, 255, 0), +5.93 at (255, 172, 255)]; BT.709-weight luma never
above (max 0 on greys).
**Weights from primaries:** BT.709 + D65 (0.3127, 0.3290): 0.212639, 0.715169, 0.072192. NTSC 1953 +
C (0.31006, 0.31617): 0.298891, 0.586639, 0.114470; with C (0.310, 0.316): 0.298967, 0.586421,
0.114612. BT.601 625-line + D65: 0.222004, 0.706655, 0.071341; 525-line + D65: 0.212376, 0.701060,
0.086564. ȳ(λ) = V(λ) at all 471 wavelengths, 360–830 nm.
**Blur (σ = 0.8: side 0.238994, centre 0.522011):** step row c2 78.24 codes against 109.42 in light, c3
161.76 against 177.89; midpoint of 40 and 200: 120 against 148.74. Impulse, 2-D Gaussian: 98.59 against
146.11; 3×3 box: 63.89 against 100.94. Stripes 0/255 averaged: 127.5 (21.4% of white) against 187.5
(50%).
**Encoding budget:** codes per tenth of L*: sRGB 28, 21, 22, 24, 24, 26, 27, 27, 28, 29; linear 8-bit 3,
5, 8, 13, 18, 25, 32, 41, 50, 61. Largest L* step: sRGB 0.51 (code 24 → 25), linear 3.54 (0 → 1); linear
has 15 steps above 1 L*, 4 above 2.3.
**Thresholds:** tangent from the origin at L 0.0030399, V 0.039286, slope 12.92321; the 12.92 line
crosses at L 0.0029532 (V 0.038155) and 0.0031307 (V 0.040448); 8-bit codes between 0.03928 and
0.04045: none; 16-bit: 76.
**Integer luma:** OpenCV 15-bit vs Pillow 16-bit differ by one on 21,745 of 16,777,216 colours (first:
(0, 1, 201), exact 23.501, OpenCV 23, Pillow 24).

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + jump + IMPORTANT | 330 | — |
| Why this matters | 170 | — |
| The problem | 320 | — |
| Worked example: decode three codes; one colour to XYZ; to Lab; two greys; one blur in two encodings | 1,050 | FIG_01–FIG_03 |
| Intuition: companding, and one inequality behind two symptoms | 280 | — |
| Why is a pixel value an encoding? | 500 | FIG_04 |
| Where do the grey weights come from? | 520 | FIG_05 |
| How wrong is luma? | 330 | FIG_06 |
| What does Lab add? | 330 | FIG_07 |
| Which operations need linear light? | 450 | FIG_08 |
| The math | 450 | — |
| Implementation: the tooling map | 450 | FIG_09 |
| Limitations and common mistakes | 300 | — |
| Key takeaways | 130 | — |
| Try it yourself (E1–E4) | 420 | — |
| References (22 entries) | 900 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | three rulers — code, light, L* — with the patch's codes 40, 128, 200, 255 and mid-grey: codes sit near lightness, far from light | plot | Q4 — three aligned scales drawn to their own spacing, real values |
| 02 | Worked example | the azure through decode → XYZ → Lab, with the luma (158) and luminance (186) greys branching off and their swatches | placed | Q5 — 7 nodes in two paths, a real number on every edge |
| 03 | Worked example | the step blurred in codes and in light, plotted in both units: each blur is symmetric only in its own domain | chart | Q1-like — ten values computed from closed forms, two panels |
| 04 | Encoding | codes per tenth of lightness, sRGB against linear 8-bit (28 against 3 in the darkest tenth) | chart | Q1-like — twenty computed counts, paired bars |
| 05 | Grey weights | xy chromaticity diagram with the CIE spectral locus, the BT.709, 1953 NTSC and BT.601 625-line triangles and whites, each labelled with its luminance row | plot | Q4 — geometry from the CIE table and the standards' coordinates |
| 06 | How wrong is luma | luma against the luminance-matched grey for eight colours, as paired swatches and values, with the all-colour range | chart | Q4 — swatches of the real greys beside their values |
| 07 | Lab | the azure and sRGB white in the a*b* plane under D65, CSS's D50 and scikit-image's unadapted D50 | plot | Q4 — positions in a plane, real coordinates |
| 08 | Linear light | the encode curve with two chords (40–200 and 0–255): the gap between chord and curve is the blur's error | plot | Q4 — a curve and chords to scale |
| 09 | Implementation | OpenCV, scikit-image, Pillow, MATLAB: grey weights, decode before grey, XYZ and Lab, Lab white, resize domain | placed | Q5 — the series' closing tooling map, a comparison grid with no edges |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| code value; transfer function; encode, decode; linear light | Problem | the stored integer; the curve between light and code | which quantity a number is | every weighted sum |
| gamma; sRGB; IEC 61966-2-1 | Problem | the exponent shorthand; the default web and desktop encoding | the curve the codes follow | decoding an 8-bit file |
| tristimulus values; CIE XYZ; luminance Y; standard observer | Worked example | light weighted by the CIE's three matching functions | physical brightness of a colour | photometry, true grey |
| luma Y′ | Worked example | the same kind of weighted sum taken on codes | what BGR2GRAY returns | grey conversion |
| CIELAB; L*, a*, b*; reference white | Worked example | lightness and two opponent axes, relative to a white | perceptual coordinates | colour differences |
| lightness; perceptual uniformity; just-noticeable difference | Encoding | perceived grey scale; equal steps look equal | why the curve exists | bit depth |
| companding | Intuition | compress before quantising, expand before adding | the analogy | mixing signals |
| chromaticity x, y; primaries; white point; D65; Illuminant C | Grey weights | the colour of a light without its amount; the three emitters and the white | where weights come from | comparing standards |
| BT.601, BT.709, BT.470 (NTSC 1953) | Grey weights | the video standards that fix luma weights | provenance of 0.299 | reading docs |
| Helmholtz–Kohlrausch effect | Lab | saturated colours look lighter than their luminance | limits of Y and L* | perceptual grey |
| chromatic adaptation; Bradford | Lab | re-expressing colours for another white | D50 against D65 Lab | CSS, ICC, editors |
| Jensen's inequality; concave | Linear light | a concave curve lies above its chords | why codes average dark | blur, resize, composite |
| alpha compositing | Linear light | out = α·fg + (1 − α)·bg | PNG says do it in light | layering |

## Not repeated from earlier parts

The four-stage frame (one sentence), Part 1's patch (shown once as a row, not the grid), its Gaussian
(the weights quoted, not derived), Part 1's impulse answers (box 64, Gaussian 98.6, quoted and redone in
light), Part 3's resampling kernels (named; negative lobes break Jensen's bound, one sentence).
