# Outline — Canny, Line by Line

**Title:** Canny Edge Detection, Line by Line: Setting the Thresholds (58 chars; the plan's title
"Canny, Line by Line" is the name Part 1 published for this spoke, kept as the second half so a
reader of Part 1 recognises it, with the two search phrases — "Canny edge detection", "thresholds"
— at the front).
**Slug:** `canny-line-by-line`
**Series:** `image-processing`, part 8 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** intermediate (on purpose, per the plan: the spoke a practitioner reads first; no
calculus beyond a first derivative) · **Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** 6,500 words planned (L3 range 5,000–7,500, references included) · **Figures:** 11 (L3
range 8–12; the plan estimated 10 and the owner allowed more)
**Assumes:** Part 1, *Image Processing by Hand* — the Canny chain (its Figure 12), the Sobel
gradient, the L1-vs-L2 point (960 against 678.8 at 45°) and the shared patch; Part 4, *Kernel
Design* — Sobel's raw ×8 ramp gain and reflect-101's zero on the border column; Part 7,
*Edge-Preserving Smoothing* — the shared Gaussian's 78.2 | 161.8 and 98.6. Parts 1–2 live; 4 and 7
built. All named in plain text.
**Hands off:** the zero-crossing alternative to Part 2, *The Laplacian by Hand*, which owns the
coarse-to-fine argument (named, not re-argued). Learned edge detectors are out of scope.
**Built 2026-10-12:** 7,105 words as the validator counts them (references included), 11
figures, 8 feed + 4 Story cards; `validate_post.py` and `--social` PASS with 0 warnings. The
figure asserts caught one rounding slip (1.343 at exactly 26.8°, 1.344 at the pixel's true
26.83°); the by-eye review caught nine figure and card defects, listed in the manifest. A late
source check found that `Canny` hands single-threaded calls to Intel IPP's own implementation in
IPP builds; the post now says which code it describes, and that release 4.10.0 matches.

Nothing is run against an image. Every number below is worked by hand on the shared patch and
cross-checked with plain Python using only `math` (`canny_patch.py`, `canny_smoothed.py`,
`final.py` in the session scratchpad; not shipped). Library behaviour carries a ledger key to
source at a pinned commit (OpenCV 802cf95, scikit-image b700edc — the commits Parts 5–7 pinned).

**Checkpoints.** As with Parts 3–7, the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 13 sources in the post (8 peer-reviewed with identifiers, floor 7; 2 used for their
abstracts only), 6 more located and not used (abstracts withheld by Elsevier and Springer, or a
duplicate of a source read in full). Scholarly databases that answered: OpenAlex, Semantic
Scholar, Crossref, arXiv (floor 4). DBLP served an Anubis bot wall; MIT DSpace returned 405 for
Canny's 1983 report, so its suppression scheme is cited through Grompone von Gioi & Randall, who
quote it with section numbers. 45 claims. No paper figure reusable (IEEE copyright; IPOL is
CC BY-NC-SA, non-commercial).
**B:** this file.

**Five findings change what the plan expected.**
1. *`cv2.Canny` has no Gaussian step.* It computes Sobel derivatives directly, with a
   **replicate** border (not the library's reflect-101 default). OpenCV's own Python tutorial lists
   a 5×5 Gaussian as Canny's first step and says `cv.Canny()` "puts all the above" in one function;
   the C++ demo blurs with a 3×3 box filter before calling it. Source settles it.
2. *On the raw patch the plan's comparison is a tie rule, not interpolation.* Every gradient on
   the unsmoothed patch points at 0°, 45°, 90° or 26.8° between two equal magnitudes, so
   interpolated and quantised suppression agree everywhere except on the step's two-pixel plateau
   (640 | 640): a strict test keeps 0 pixels per row, OpenCV's (`>` before, `>=` after) keeps 1,
   scikit-image's (`<=` both sides) keeps 2. Interpolation disagrees only after smoothing: at
   (r1, c1), 222.2 at 62.8°, the quantised rule compares 316.2 and suppresses, interpolation reads
   198.8 and keeps.
3. *OpenCV's default L1 magnitude breaks the step.* At (r1, c2) the gradient (425, 215) has L2
   476.3 but L1 640 — tying the true edge pixel (r1, c3), which then loses the `>` test, while
   (r1, c2) loses its own diagonal test to (r2, c3). Rows r1 and r3 have no edge pixel: the line is
   three dots. L2 keeps it connected (r0c2, r1c3, r2c3, r3c3, r4c2). Li, Sullivan & Baker's "false
   suppression" at junctions is the same mechanism.
4. *Without smoothing no Canny ratio separates the impulse from the step.* The impulse's own
   gradient is 0; its ring (430, 430, 430, 304.1, 304.1) is 8-connected to the step's line, so only
   a low threshold ≥ 430 cuts it off: high/low < 640/430 = 1.49. After the shared Gaussian the ring
   shrinks to two isolated pixels of 219.7 and any high threshold from 219.7 to 408.8 rejects them:
   Canny's 2:1–3:1 works.
5. *Histogram rules assume edges are rare.* 15 of the patch's 25 magnitudes are non-zero; the
   80th percentile — Canny's "below about 80% is noise" — is 640, the step itself. The a contrario
   rule of Desolneux, Moisan & Morel, with a Rayleigh noise tail as H, gives a contrast threshold
   falling as 1/√(chain length): half the single-pixel threshold at 4 pixels, a third at 9 — which
   is what Canny's ratio of 2–3 approximates.

---

## The spine

Canny's last two steps decide what a "line" is. Non-maximum suppression keeps one pixel across
each ridge, and how it breaks ties and reads off-grid neighbours decides which pixel and whether
any survives. Hysteresis then judges connected chains, not pixels: the high threshold decides
which chains exist, the low one where each ends. Both thresholds are in raw gradient units, so
they belong to the noise and the gradient operator, not to the image: set the high one a chosen
number of noise scales above flat-region magnitude and the low one by the chain length you are
willing to trust. The patch shows all of it, and shows that smoothing first is what makes the
ratio work.

## Verified numbers

**Raw patch, Sobel 3×3, replicate border (cv2.Canny):** Gx r0 0 0 640 640 0; r1 215 0 425 640 0;
r2 430 0 210 640 0 (r3 = r1, r4 = r0). Gy r1 215 430 215 0 0; r3 negated; others 0. L2 r1 304.1 430
476.3 640 0; r2 430 0 210 640 0. L1 at (r1, c2) 640, at (r1, c0) 430. Angle at (r1, c2) 26.8°.
Reflect-101 would give (r2, c0) 0 and (r1, c0) Gy only, 430.
**NMS (OpenCV rule):** L2 survivors r0c2 640, r1c3 640, r2c3 640, r3c3 640, r4c2 640, r1c0 304.1,
r1c1 430, r2c0 430, r3c0 304.1, r3c1 430. L1 survivors r0c2, r2c3, r4c2 (640) and r1c0, r1c1,
r2c0, r3c0, r3c1 (430). Interpolated, ties kept: L2 set plus r0c3, r4c3.
**Hysteresis (8-connected, strict):** L2 one component of 10. High < 640 and low ≥ 430 → the line
(5); 304.1 ≤ low < 430 → 8; low < 304.1 → 10. L1: low ≥ 430 → 3 dots; low < 430 → 8.
**Smoothed (shared 3×3 Gaussian, reflect-101, float):** r0 40, 40, 78.24, 161.76, 200; r1 64.56,
66.82, 90.52, 161.76, 200; r2 93.65, 98.59, 105.06, 161.76, 200. L2 row0 100.5 167.3 463.1 474.9
153.0; row1 219.7 222.2 391.3 436.5 153.0; row2 14.4 74.7 316.2 408.8 153.0. Survivors (L2,
OpenCV): c3 474.9, 436.5, 408.8, 436.5, 474.9; (r1, c0), (r3, c0) 219.7. Interpolated adds (r1, c1),
(r3, c1) 222.2. L1: c2 on r0/r1/r3/r4 (511.6, 487.0), c3 on r2 (408.8), dots 229.0. Rounded to
8 bits, the survivors do not change.
**Devernay offsets:** raw r0 2.5, r1 2.70, r2 2.90; smoothed 2.54, 2.64, 2.77.
**Aperture gains (OpenCV kernels):** 3: step 4h, ramp 8; 5: 48h, 128; 7: 640h, 2,048 (stored /16).
The patch's step: 640, 7,680, 102,400. 3 → 5 is ×12 on a step and ×16 on a ramp.
**Noise model:** Sobel 3×3 component std √12 σ = 3.464σ (uncorrelated components → Rayleigh);
after the shared Gaussian 1.709σ. high = s√(2 ln(1/α)): 10⁻³ → 3.717s, 10⁻⁴ → 4.292s. Ratio r →
α_low = α_high^(1/r²): 10⁻⁴ → 0.10 (r = 2), 0.36 (r = 3). σ = 2: s = 6.93, high 29.7, smallest
seeding step 7.4, low 14.9. Rayleigh percentiles: median 1.177s, 80th 1.794s. A contrario with
Rayleigh H, N = 10⁶: l = 1 5.257s, 4 2.628s, 9 1.752s.
**E3 (impulse 120):** ring 160, 160, 113.1; (r1, c2) 565.7; clean line at high 600, low 200.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + jump + IMPORTANT | 260 | — |
| Why this matters | 160 | — |
| The problem | 320 | — |
| Worked example: gradient; suppression; hysteresis; smooth first; scorecard | 1,050 | FIG_01, FIG_02, FIG_03 |
| Intuition: chains, not pixels | 300 | FIG_04 |
| What does non-maximum suppression keep? (bins, ties, interpolation, sub-pixel, junctions) | 700 | FIG_05, FIG_06, FIG_07 |
| What do the two thresholds select? (streaking, seeds and extent, connectivity) | 400 | — |
| What units are the thresholds in? (aperture, L1/L2, colour, other libraries) | 450 | FIG_08 |
| How do you set the thresholds without searching? (noise model, ratio, percentiles, a contrario) | 700 | FIG_09, FIG_10 |
| The math | 380 | — |
| Implementation: the tooling map | 420 | FIG_11 |
| Limitations and common mistakes | 300 | — |
| Key takeaways | 120 | — |
| Try it yourself (E1–E4) | 420 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | the patch's Sobel gradient: arrows on every pixel, L2 magnitudes, the impulse at 0 inside a ring | placed | Q4 — a grid of real values with vectors drawn to scale |
| 02 | Worked example | suppression on the raw patch, L2 against L1: bins, survivors, the gap at r1 and r3 under L1 | placed | Q4 — small multiples of real grids |
| 03 | Worked example | hysteresis as components: raw L2 (ring attached), smoothed L2 (two isolated pixels) | placed | Q4 — small multiples of real grids with connectivity |
| 04 | Intuition | the (low, high) plane partitioned by what comes out, raw and smoothed | plot | regions computed from the definitions |
| 05 | NMS | the four bins and what each variant reads at (r1, c1) of the smoothed patch: 316.2 against 198.8 | placed | Q4 — geometry of the gradient line through the grid |
| 06 | NMS | three tie rules on the profile 0, 640, 640, 0: zero, one or two pixels kept | placed | Q4 — small multiples of one real profile |
| 07 | NMS | Devernay's parabola on rows r0 and r2: vertex 2.5 against 2.90 | plot | closed-form parabola through real values |
| 08 | Units | the patch's step and a unit ramp through apertures 3, 5, 7, and L1/L2 against angle | chart | Q1 — values from the kernels' definitions on one log scale |
| 09 | Thresholds | Rayleigh noise magnitude for σ = 2 with the high and low thresholds and a step's 4h | plot | closed-form density |
| 10 | Thresholds | a contrario contrast against chain length, with hysteresis's two steps and ratios 2, 3 | plot | closed-form curve (model inputs) |
| 11 | Implementation | OpenCV, scikit-image, MATLAB: smoothing, border, magnitude, suppression, ties, units, defaults | placed | Q5 — a comparison grid with no edges, the series' closing tooling map |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| gradient magnitude, direction; L1 and L2 norm | Problem | edge strength and its orientation | what the thresholds compare | always: know which norm |
| non-maximum suppression (NMS) | Problem | keep a pixel only if no neighbour along the gradient is larger | thins a ridge to one pixel | every Canny call |
| direction bin; quantised vs interpolated | Worked example / NMS | read the nearest of 8 neighbours, or interpolate between two | the two implementations | slanted edges |
| tie rule | Worked example | strict or non-strict comparison on equal neighbours | decides 0, 1 or 2 pixels on a plateau | edges between pixels |
| hysteresis thresholding; seed; candidate; 8-connectivity | Problem / Worked example | keep connected chains of candidates that contain a seed | repairs a single threshold's streaking | setting the two thresholds |
| streaking | Thresholds | a contour broken where its response dips below one threshold | why two thresholds | noisy edges |
| aperture | Units | the Sobel kernel size, 3, 5 or 7 | sets the units of the thresholds | changing apertureSize |
| replicate border | Worked example | pad by repeating the edge pixel | what cv2.Canny uses | border pixels |
| sub-pixel position; Devernay correction | NMS | vertex of a parabola through three magnitudes | position finer than the grid | measurement |
| Rayleigh distribution; noise scale s | Thresholds | magnitude of two independent Gaussians | turns σ into thresholds | estimating thresholds |
| false-alarm rate α | Thresholds | fraction of flat pixels above a threshold | what the high threshold buys | choosing high |
| a contrario; number of false alarms | Thresholds | expected count of chance detections | justifies a length-dependent threshold | why two thresholds |

## Not repeated from earlier parts

The four-stage frame (one sentence), Part 1's L1-vs-L2 geometry (960 against 678.8 cited, not
redrawn), Part 1's Canny chain and the "respond, localise, commit" decomposition (one sentence),
Canny's optimality conditions (Part 1's section; not re-argued), Part 2's zero-crossings and the
coarse-to-fine argument (named, handed off), Part 4's border rules and ×8 gain (used, cited), Part
7's Gaussian numbers (quoted).
