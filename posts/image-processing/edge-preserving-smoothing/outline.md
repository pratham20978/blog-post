# Outline — Edge-Preserving Smoothing

**Title:** Edge-Preserving Smoothing: Bilateral, NL-Means, Diffusion (57 chars; the plan's title is
79, over the 60-character limit, so "Non-Local Means" is shortened to the name OpenCV's and
scikit-image's users search for, and "Anisotropic Diffusion" to "Diffusion", the word Weickert's
terminology point makes the more accurate one).
**Slug:** `edge-preserving-smoothing`
**Series:** `image-processing`, part 7 · **Tier:** L3 deep dive · **Category:** algorithms ·
**Difficulty:** advanced · **Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** 6,500 words planned (L3 range 5,000–7,500, references included) · **Figures:** 11 (L3
range 8–12)
**Assumes:** Part 1, *Image Processing by Hand* — the linear-filter sum, its three answers on the
impulse (box 64, Gaussian 98.6, median 40) and its point that a linear filter cannot stop at an
edge; Part 2, *The Laplacian by Hand* — the heat-equation identity, linked rather than re-derived.
Both live. Part 4's robustness note hands this part "averaging that refuses to cross the bad
pixel"; Part 5's DC term (2,815) reappears as the value diffusion converges to. All named in plain
text.
**Hands off:** learned denoisers — out of scope, not deferred.
**Built 2026-10-11:** 6,608 words as the validator counts them (references included), 11
figures, 8 feed + 4 Story cards; `validate_post.py` and `--social` PASS with 0 warnings. The
figure asserts and the by-eye review caught three text errors before handoff (93.7 → 93.6,
165.3 → 165.2, and a Perona–Malik check that did not add up with rounded weights).

Nothing is run against an image. Every number below is worked by hand on the shared patch and
cross-checked with plain Python using only `math` (`worked.py`, `nlm.py`, `pm.py`, `robust.py`,
`final.py`, `sklut.py` in the session scratchpad; not shipped). Library behaviour carries a ledger
key to source at a pinned commit.

**Checkpoints.** As with Parts 3–6, the session ran without a stop at A and B; what each would have
shown is recorded here.
**A:** 25 sources, 19 peer-reviewed or standard with identifiers (floor 7; nine used for their
abstracts only and one survey for mapping only, and the ledger says so); scholarly databases
OpenAlex, Crossref, Google Scholar, Semantic Scholar and arXiv all answered (floor 4); 53 claims; 5
paper figures considered, none reusable (IEEE, Now Publishers copyright; IPOL's is non-commercial).
Blocked: HAL (bot wall), MIT DSpace (AWS bot wall), Georgia Tech repository (JavaScript shell).
**B:** this file.

**Five findings change what the plan expected.**
1. *The plan expected the bilateral's range weights to keep the step and drop the impulse. They do
   the opposite.* The impulse differs from its neighbours by 215, the step by 160, so at σ_r = 80
   a neighbour across the step keeps e⁻² = 13.5% of its weight and a neighbour of the impulse
   2.7%. The bilateral keeps 92% of both. No σ_r separates them, because 215 > 160; the survey
   (S07) and Durand–Dorsey (S06) prescribe a median for impulses. The post's spine is this.
2. *NL-means is the one that tells them apart — by repetition, not contrast — and only under
   IPOL's self-weight rule.* The step pixel has an exact copy down its column; the impulse has
   none, and its four best matches are flat patches. IPOL gives the pixel's own patch the largest
   of the other weights, so those four outvote it: 255 → 83.0 = (255 + 4·40)/5 at any small h,
   step exact. OpenCV and scikit-image give it weight 1, and keep 255.
3. *Perona–Malik counts faces.* The impulse's arcs conduct less (0.122) than the step's (0.2),
   but it has four, so three iterations leave 48% of its contrast and 74% of the step's. The
   scheme conserves brightness and converges to 112.6, the patch mean (Part 5's 2,815 / 25), so the
   iteration count is a hidden fourth parameter.
4. *Two library traps the plan did not know.* scikit-image's bilateral builds its spatial table on
   win_size + 1 points and reads it as win_size (read, not run; flagged for the owner);
   opencv_contrib's `anisotropicDiffusion` takes only 8-bit colour, sums 8 neighbours and documents
   alpha "between 0 and 1" where the maximum principle needs ≤ 1/8.
5. *Part 1's Perona–Malik link points at the wrong PDF* (Guidotti's survey). Reported, not edited.

---

## The spine

A linear filter applies the same weights everywhere, so it cannot stop at an edge (Part 1). Make
the weights depend on the image and it can: the output is still one weighted sum, ŷ = W·y, but W is
built from the data. The three classical methods differ only in what "a neighbour like me" means —
the same value (bilateral), the same surroundings (NL-means), a small enough difference across one
face, applied over and over (Perona–Malik). Two of the three measure contrast, and contrast cannot
tell this patch's noise from its edge, because the impulse is the bigger jump. The third measures
repetition, which can. Each is priced in parameters, cost and failure mode.

## Verified numbers

**Shared kernel:** 2-D weights centre 0.2725, edge 0.1248, corner 0.0571 (σ_s = 0.8, square 3×3,
reflect-101 borders).

**Bilateral, σ_r = 80:** range weights w(0) = 1, w(20) = 0.969, w(160) = e⁻² = 0.135, w(215) =
0.027. Impulse (r2, c1): (0.2725·255 + 0.7275·0.027·40)/(0.2725 + 0.7275·0.027) = 70.27/0.2922 =
240.5. Step r0: c2 = (0.761·40 + 0.239·0.135·200)/(0.761 + 0.0323) = 46.5, c3 = 193.5. Row r2: 41.9,
240.5, 48.8, 193.5, 200. Gaussian (σ_r → ∞): impulse 98.6, step 78.2 | 161.8, row r2 93.7, 98.6,
105.1, 161.8, 200. σ_r sweep, impulse | step c2–c3: 20 → 255 | 40–200; 50 → 254.9 | 40.3–199.7;
100 → 210.0 | 52.9–187.2; 160 → 143.3 | 65.6–174.4. Bump of 20 (a 60): Gaussian 45.45, bilateral
45.58. Mollified (range on the median image): impulse 98.6, step 46.5 | 193.5. Robust step from the
median 40: 42.2; IRLS from 255: 240.5, 232.4, 226.3, … 42.3 after 60.

**NL-means (3×3 patches, every pixel of the patch a candidate, reflect-101, d² = mean squared
difference, h = 20):** impulse's patch to the four flat patches (0,0), (0,1), (4,0), (4,1): d² =
215²/9 = 5,136 (RMS 71.7), weight e^(−12.84) = 2.7×10⁻⁶; next (1,1), (3,1): 10,272. Step pixel
(r0, c2): exact copy (r4, c2) d² = 0; (r1–r3, c2) 5,136; flat and bright patches 8,533 (= 3·160²/9,
RMS 92.4). Self-weight 1 → identity (impulse 255). Max rule → impulse 83.0, everything else exact.
h = 80, self 1: impulse 110.7, step 82.0 | 170.4, row r2 65.4, 110.7, 81.1, 170.4, 184.4. h = 80, max:
impulse 90.6.

**Perona–Malik (g = 1/(1 + (s/K)²), K = 80, λ = 1/4, 4 neighbours, adiabatic border):** g(160) =
0.2 (flux 32, so ±8 per side in iteration 1), g(215) = 0.1216 (flux 26.15). Iteration 1: impulse
228.85, its neighbours 46.54, (r2, c2) 54.54, step 48 | 192. Iteration 2: impulse 199.19, step r0
54.51 | 185.49. Iteration 3: impulse 165.25, row r2 55.33, 165.25, 80.90, 179.19, 194.91; r0 41.71,
47.22, 61.54, 179.65, 194.96. Local contrast (minus the mean of 4 neighbours) after 1, 2, 3, 5, 10:
impulse 180.3, 144.1, 102.5, 13.4, −2.9; step 144.0, 131.0, 118.1, 92.4, 39.2. Converges to 112.6
everywhere by ~100. Linear (g ≡ 1) one step: impulse → 40, its neighbours 93.75, step 80 | 160.
K from the 90% rule on the patch's 40 arc differences (31 zero, 5 at 160, 4 at 215): 160. σ_e =
1.4826·MAD = 0.

**OpenCV NL-means defaults (h = 3, 7×7):** a lone pixel Δ from flat surroundings has d² ≈ Δ²/49;
weight ≥ 0.001 needs Δ²/(49·9) < ln 1000 = 6.91, so Δ < about 55.

**Cost per pixel (from definitions):** 3×3 Gaussian separable 6; bilateral OpenCV d = 5 13 taps,
d = 9 49; scikit-image default 7×7 49; NL-means naive 21²·7² = 21,609 distances, fast ~21² = 441
shifts; Perona–Malik 4 per iteration.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line + IMPORTANT | 240 | — |
| Why this matters | 180 | — |
| The problem | 380 | — |
| Worked example: bilateral; NL-means; Perona–Malik ×3; the scorecard | 1,050 | FIG_01, FIG_02, FIG_03 |
| Intuition: who counts as "like me"; the trade-off | 420 | FIG_04 |
| How does the bilateral filter choose its weights? (σ_r as a threshold; impulses; the lift and the fast versions) | 650 | FIG_05, FIG_06 |
| Non-local means: similarity by repetition (self-weight, rare patches, h, cost) | 650 | FIG_07 |
| Perona–Malik: the heat equation with a conductance (flux, stopping, ill-posedness, terminology) | 700 | FIG_08, FIG_09 |
| What does each one cost? | 280 | FIG_10 |
| The math | 450 | — |
| Implementation: the tooling map | 420 | FIG_11 |
| Limitations and common mistakes | 300 | — |
| Key takeaways | 120 | — |
| Try it yourself (E1–E4) | 400 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | bilateral weights at the impulse and at the step: spatial × range → normalised; the step's cross neighbours keep 13.5%, the impulse's 2.7% | placed | Q4 — grids of real weights |
| 02 | Worked example | NL-means patch distances from the impulse and from a step pixel: the step has an exact copy, the impulse none | placed | Q4 — grids of real distances |
| 03 | Worked example | Perona–Malik on the patch, iterations 0–3, with the arc conductances 0.2 and 0.12 | placed | Q4 — small multiples of real values |
| 04 | Intuition | step contrast kept against impulse contrast left: bilateral (σ_r sweep) and Perona–Malik (iterations) trace one trade-off; median and NL-means (max rule) sit off it | plot | curves computed from the definitions |
| 05 | Bilateral | the range weight against intensity difference for σ_r = 20, 50, 80, 160, with 20, 160 and 215 marked | plot | closed-form curves |
| 06 | Bilateral | row r2 lifted into position × intensity: grid cells σ_s × σ_r, the impulse 2.69 σ_r and the step 2.00 σ_r from their neighbours | placed | Q4 — geometry to scale |
| 07 | NL-means | estimate at the impulse and at a step pixel against h, under self-weight 1 and the max rule | plot | curves computed from the definitions |
| 08 | Perona–Malik | flux s·g(s) for both conductances at K = 80 against the heat equation, with 20, 160, 215 marked | plot | closed-form curves |
| 09 | Perona–Malik | local contrast of impulse and step over 100 iterations; both reach the mean 112.6 | plot | the scheme iterated from its definition |
| 10 | Cost | operations per pixel and the parameters each method needs | chart | Q1 — counts from definitions compared on one scale |
| 11 | Implementation | OpenCV, opencv_contrib, scikit-image, ITK, MedPy: what each call does, its default, its trap | placed | Q5 — a comparison grid with no edges, the series' closing tooling map |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| edge-preserving smoothing | Problem | averaging that stops at intensity discontinuities | the job of all three methods | denoising without blurring edges |
| bilateral filter; spatial (domain) kernel σ_s; range kernel σ_r | Worked example | weighted mean whose weights multiply closeness and similarity | the simplest data-dependent weights | one pass, moderate noise |
| impulse (salt-and-pepper) noise | Problem | isolated pixels far from their neighbours | the patch's 255 is one | before choosing any contrast-based filter |
| non-local means (NL-means); patch; search window; h; self-weight | Worked example | weights from the similarity of whole neighbourhoods anywhere in a window | similarity by repetition | textured or repetitive images |
| anisotropic (Perona–Malik) diffusion; conductance g; contrast K; time step λ | Worked example | the heat equation with a per-face conductance that falls with the difference | iterated, local, conserves brightness | when an iteration count can be chosen |
| flux; backward diffusion | Perona–Malik | conductance × difference; where it falls with contrast, edges sharpen | explains why edges survive | choosing K |
| maximum principle | Perona–Malik | no new extrema, guaranteed for λ ≤ 1/4 on 4 neighbours | stability | setting the time step |
| ill-posed; regularisation; staircasing | Perona–Malik | no weak solutions; smoothing the gradient first; plateaus | the PDE's failure modes | long runs |
| robust estimator; error norm; influence function; W-estimator | Math | a statistic that discounts outliers | unifies all three | reading or designing an edge-stopping function |
| rare patch effect | NL-means | few similar patches along edges and corners, none for an impulse | NL-means' failure mode | edges and impulses |
| bilateral grid | Bilateral | the filter as a linear blur in position × intensity | the fast implementations | large σ_s |
| row-stochastic W | Math | non-negative weights summing to one per output | the common form | analysing any of them |

## Not repeated from earlier parts

The four-stage frame (one sentence at most), Part 1's three answers (quoted, not re-derived),
Part 2's heat-equation identity (quoted with v/2 and linked), Part 4's p-family, Part 5's spectrum
(only the DC 2,815 is used), Part 6's wavelet shrinkage (named once as the transform-domain
alternative), correlation vs convolution.
