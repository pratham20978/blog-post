# Outline — The 2-D DFT

**Title:** The 2-D DFT: Spectra, Phase, and Frequency-Domain Filtering (59 chars, the plan's title
unchanged).
**Slug:** `the-2d-dft-spectra-phase-filtering`
**Series:** `image-processing`, part 5 · **Tier:** L4 pillar · **Category:** algorithms ·
**Difficulty:** advanced · **Lab grade:** G0 — by hand, the series invariant (no `lab/`)
**Budget:** 7,500 words planned (L4 range 7,500–10,000) · **Figures:** 13 (L4 range 12–18)
**Assumes:** Part 1, *Image Processing by Hand* — its transform stage, its four-point DFT of
[40, 40, 200, 200] and the convolution theorem worked on those numbers, and its transfer-function
figure. Named in plain text; the owner adds links (convention since 2026-10-01).
**Owes:** Part 3 (*Resampling and Aliasing*, built, not published) names this post as the home of
"resizing through the spectrum, by padding or truncating the DFT" — covered in the filter-design
section. Part 4 (*Kernel Design*, built, not published) is not needed.
**Hands off:** local and non-stationary structure to *Wavelets and Multiresolution* (a later spoke,
named by title only — Part 1's published body already promises it under that title).
Periodic-noise removal is owned here.

Nothing is run against an image. Every number below is worked by hand on the shared 5×5 patch, its
transpose or its 2×2 tiling, and cross-checked with plain Python using only `math` and `cmath`
(`worked.py`, `worked2.py`, `worked3.py` in the session scratchpad; not shipped). Curves and cost
tables are evaluated from closed forms and captioned as models. Library behaviour carries a ledger
key to documentation or source at a pinned commit.

**Checkpoints.** The session could not pause for replies, as with Parts 3 and 4, so Checkpoints A
and B ran without a stop; what each would have shown is recorded here.
**A:** 26 sources, 15 of them peer-reviewed or standard with identifiers (floor 10; six used for
their abstracts only, and the ledger says so); 5 scholarly databases answered (OpenAlex, Google
Scholar, Semantic Scholar, Crossref, arXiv; floor 4) plus pinned library source; 49 claims; 4
paper figures considered, none reusable. The plan's lead source, Oppenheim & Lim 1981, was not
reachable in full (DTIC 403) and is cited for its abstract only; the two-image swap is described
through the Skarbnik–Zeevi–Sagiv review that reproduces it. Duhamel & Vetterli's FFT survey was
found and blocked, so it is not cited. **B:** this file.

**Two findings change what the plan expected.**
1. *The swap on two small images does not reproduce the photograph result, and that is the
   lesson.* With the patch and its transpose, the swapped images put every feature where the phase
   donor has it, but the dominant bar runs the way the magnitude donor's edge runs. Magnitude
   carries orientation and strength; phase carries position. The photograph swap looks like the
   phase donor because photographs share a roughly 1/f magnitude (L09, L10) — the post states
   that as its own reasoning, not as Oppenheim & Lim's.
2. *The crossover depends on what you count and whose direct loop you race.* The textbook model
   (L31, L32) says 7×7; counting the FFT route's real arithmetic says 9–11 for a full kernel and
   about 45 taps for a separable one; OpenCV's source switches at kernel area 130 on its SIMD paths
   (12×12 and up; an 11×11 stays direct, despite the docs' "~11 × 11"); SciPy's fitted model picks
   the FFT for 2-D kernels from 3×3. Four answers, each correct for what it counts.

---

## The spine

A 2-D spectrum is a list of waves. Each coefficient says how much of one wave the image contains
(magnitude) and where that wave's crests sit (phase). Three readings follow:

```
magnitude   how much, and which way      a vertical edge prints a horizontal line of energy
phase       where                         move the image, and only the phase changes
the frame   what the DFT assumes          the image is one tile of a periodic plane
```

Filtering there is one multiplication per coefficient. It is the right move when the thing to
remove is a few coefficients (periodic interference: a notch) or when the kernel is large enough
that one multiply per coefficient beats m² per pixel. It is the wrong move when the filter is
small, separable, or when what must be removed shares coefficients with the image.

---

## Verified numbers

### The patch, its row pass, its spectrum

Row DFT of `40 40 40 200 200` (N = 5, no forward scaling): since 1 + w + w² = −(w³ + w⁴) for
w = e^(−2πi/5), S(k) = 160(w^{3k} + w^{4k}) = 160 · 2cos(πk/5) · e^(−i·7πk/5) for k ≠ 0.

| k | S(k) | note |
|---|---|---|
| 0 | 520 | sum |
| ±1 | 258.885 ∠ ±108° | 160 × φ, φ = 2cos 36° = 1.618 |
| ±2 | 98.885 ∠ ∓144° | 160 / φ, 2cos 72° = 0.618 |

Row r2 (`40 255 40 200 200`) adds 215 at c1, i.e. 215 ∠ −72°k: R2 = 735, 43.885 ∠ ±108°,
313.885 ∠ ∓144° — the impulse is exactly antiparallel to the step at k = ±1 and parallel at ±2,
because it sits half a period (2.5 samples) from the centre of the 200 plateau (3.5).

Column pass: F(kr, kc) = 5·S(kc)·[kr = 0] + 215·w^(2kr + kc).

- F(0, 0) = 2,815 = the pixel sum (mean 112.6).
- Row kr = 0: 1,079.43 ∠ ±108°, 709.43 ∠ ∓144°.
- Every other bin: |F| = 215 exactly; phase −72°·(2kr + kc), the impulse's linear ramp
  (−144° per kr step, −72° per kc step).
- Centred (fftshift on 5: index order 3, 4, 0, 1, 2 = frequencies −2…2): DC at the centre, the
  bright row through it, a flat floor of 215 elsewhere.
- log10(1 + |F|): 3.45, 3.03, 2.85, 2.33. Linear, DC is 13.1× the floor.
- Parseval: Σ|F|² = 12,185,625 = 25 Σf². Energy: DC 65.0%, the rest of row kr = 0 27.4%,
  the 20 floor bins 7.6%.

### Keep the phase or keep the magnitude (unit magnitude / zero phase)

- Magnitude only: every row reads 212.71, 93.37, 60.28, 60.28, 93.37, symmetric about c0, plus
  215 extra at (0, 0) → 427.71. (427.71 is the mean of |F|.)
- Phase only: every row reads −0.0494, −0.1600, −0.0494, +0.1294, +0.1294; at (r2, c1) 0.8400.
  = a unit impulse at (r2, c1) plus (4/25)cos(108° + 72°c) along the rows.
- So phase keeps the impulse at (2, 1) exactly and the step's side (dark left, bright right,
  crossing between c2 and c3); magnitude moves both to the origin and makes them symmetric.
- Hayes et al. (L04): exact recovery from phase needs the phase at N − 1 = 4 frequencies strictly
  inside (0, π) per axis; a 5-point DFT has 2 — so the same-size phase-only image is a whitened
  approximation, not the image.

### Swap with the transpose

B = Aᵀ: horizontal step (rows 3–4 bright), impulse at (r1, c2). |F_B| = transpose of |F_A|
(a bright column).

|A| with phase of B (|B| with phase of A is its transpose):

```
  49.65   82.74  202.08   82.74   49.65
  25.88   58.97  393.31   58.97   25.88
  49.65   82.74  202.08   82.74   49.65
  88.11  121.20  240.54  121.20   88.11
  88.11  121.20  240.54  121.20   88.11
```

= 104 (mean) + a vertical bar profile (−43.7, −10.6, +108.7, −10.6, −43.7 across) + a weak
horizontal step (−10.6, −34.4, −10.6, +27.8, +27.8 down) + 215 at (1, 2). Positions from B
(impulse at (1, 2); rows 3–4 brighter), orientation and strength from |A| (a vertical bar).
A circular shift instead of a transpose leaves |F| unchanged to 2 × 10⁻¹² — the swap is then exact.

### The notch (tile 2×2 → 10×10; interference 20·cos(2π·3r/10))

- The tile occupies exactly the 25 bins with both indices even; FT(0, 0) = 11,260 = 4 × 2,815.
- Interference per row: 20, −6.18, −16.18, 16.18, 6.18, −20, 6.18, 16.18, −16.18, −6.18 (3 cycles
  down 10 rows; constant along each row: horizontal bands).
- It changes exactly two bins, (3, 0) and (7, 0), each to magnitude 1,000 (= 20 × 100 / 2); both
  have an odd row index, where the tile is zero. Centred: ±3 on the vertical axis.
- Notch: H = 0 at those two bins, 1 elsewhere. Restored − tile: 3 × 10⁻¹² (exact).
- Rounded to 8 bits before filtering: max error 0.16 grey levels.

### Off-bin interference (2.5 cycles in 10 rows: 20, 0, −20, 0, 20, …)

One column's 1-D transform: 20, 24.72, 64.72, 64.72, 24.72, 20, … (= 20/|sin(π(2k−5)/10)|),
energy 20,000; 83.8% in k = ±2, ±3. The bands are constant along rows, so the 2-D spectrum's
centre column is ten times that: 200, 247.2, 647.2, 647.2, 247.2, 200, … — the scale the tile's
column kc = 0 is on (11,260 at k = 0, 860 at k = ±2, ±4). (Caught at figure review: the first
draft quoted the 1-D values beside the 2-D 860.)

| notch on column 0 | rms error (interference alone: 14.14) | max |
|---|---|---|
| k = 3, 7 (image-free) | 10.78 | 16.00 |
| k = 2, 3, 7, 8 | 13.43 | 25.92 |
| eight bins (all but 0, 5) | 17.43 | 34.40 |

20-row crop: tile at row indices 0, 4, 8, 12, 16; interference exactly at 5 and 15 (4,000 each);
two-bin notch exact (4 × 10⁻¹²). Gaussian notch on the on-bin case, width D0 = 0.5 bin: H = 0.865
at the four neighbours, two of which carry tile content — rms error 2.33; D0 = 1: 10.95.

### Filter design on one row (N = 5, circular)

- Ideal low-pass keeping k = 0, ±1: 72.0, 0.45, 72.0, 187.78, 187.78 — dips 39.6 below the flat 40.
- Shared Gaussian [0.239, 0.522, 0.239]: H(k) = 1, 0.670, 0.135, 0.135, 0.670 → 78.24, 40.0, 78.24,
  161.76, 161.76 (spatial and spectral routes agree).
- 2× by zero-padding the spectrum: 40, 32.45, 40, 32.45, 40, 104, 200, 247.11, 200, 104 — passes
  through every sample and overshoots to 247.1 between the two 200s.
- Shrink 5 → 3 by truncating to k = 0, ±1: 72.0, 34.71, 205.29 — mean 104 kept, ringing.

### Phase correlation (A and C = A shifted by (1, 2) circularly)

- min |F_A| = 215, so the normalised cross-power spectrum is defined everywhere.
- Phase correlation: exactly 1 at (4, 3) ≡ (−1, −2), 0 elsewhere.
- Plain cross-correlation: 487,425 at (4, 3); 441,200 at the four other rows of column 3 — the peak
  is 10.5% above a ridge, because the step is constant down the rows; only the impulse breaks the tie.

### Cost

- Gonzalez & Woods (L31, L32): C_n(m) = m²/(4 log2 M) > 1 from m = 7 for M = 512…4096;
  C_s(m) = m/(2 log2 M) > 1 from m = 19 (512), 21 (1024), 23 (2048), 25 (4096); the book reads
  "around 27" at 2048 off its table.
- Refined model, flops per output pixel: direct 2m², separable 4m, FFT route = 3 real 2-D FFTs at
  2.5·PQ·log2(PQ) (FFTW's convention, L27) + 6 flops per half-spectrum bin, padded to the next
  2·3·5-smooth size ≥ M + m − 1.

| image | pad (m ≤ 29) | FFT route | non-sep. crossover | with cached kernel FFT | separable crossover |
|---|---|---|---|---|---|
| 512 × 512 | 540 × 540 | 154.8 | 9 | 8 | 45 |
| 1920 × 1080 | 1944 × 1125 | 169.8 | 10 | 8 | 44 |
| 2048 × 2048 | 2160 × 2160 | 188.2 | 10 | 8 | 48 |
| 4096 × 4096 | 4320 × 4320 | 204.8 | 11 | 9 | 52 |

- By hand, 11×11 on 1920 × 1080: pad 1,930 → 1,944, 1,090 → 1,125; PQ = 2,187,000; log2 = 21.06;
  one real FFT 1.15 × 10⁸ flops, three 3.45 × 10⁸, multiply 6.6 × 10⁶; 169.8 per pixel against
  242 direct.
- OpenCV (L41): DFT at area ≥ 130 (SSE3; 8U→8U/16S, 32F→32F) → first square 12×12; ≥ 50 otherwise
  → 8×8. sepFilter2D never (L42).
- SciPy (L44): 2-D 'same', FFT predicted faster from m = 3 for M = 64 … 2048.
- Split radix (L28) cuts the FFT count by about 20%, moving the full-kernel crossover down by
  about one size.

### Odd-size traps

- fftshift on N = 5: 3, 4, 0, 1, 2; ifftshift 2, 3, 4, 0, 1; fftshift twice 1, 2, 3, 4, 0 —
  DC lands at index 4. N = 10: both 5…9, 0…4.
- Undoing a 5×5 fftshift with fftshift and inverting returns f·e^(−2πi(r+c)/5); the real part is
  f·cos(72°(r + c)): 40 at (0, 0), −206.3 at (2, 1), −161.8 at (0, 3).
- Shift by (0, 1): |F| unchanged; phase at (0, 1) 108° → 36°, (1, 0) −144° unchanged, (1, 1)
  144° → 72°, (0, 2) −144° → 72°.

---

## Section budget

| # | Section | Target | Job |
|---|---|---|---|
| — | Insights + level + series line + jump + IMPORTANT | 300 | the answer: magnitude = how much/which way, phase = where; notch and crossover numbers |
| 1 | Why this matters | 230 | the bright cross you can't read, the ringing filter, the FFT that was slower |
| 2 | The problem | 450 | 2-D DFT defined on the patch's terms; three questions |
| 3 | Worked example | 1,700 | row then column (FIG_01), spectrum (FIG_02), phase/magnitude (FIG_03), swap (FIG_04), notch (FIG_05), one cost line |
| 4 | Intuition | 500 | phase is a ramp whose slope is position (FIG_06); parts list vs assembly drawing + break |
| 5 | How do you read a 2-D spectrum? | 700 | fftshift and odd sizes (FIG_07), conjugate symmetry, log scale, the cross (FIG_08) and its fixes |
| 6 | What survives when magnitude is destroyed? | 600 | Hayes' conditions, 2-D uniqueness, textures, symmetry, photographs' 1/f |
| 7 | How do you design a filter in the frequency domain? | 650 | zero phase, ideal vs Gaussian (FIG_09), padding, fast sizes, resizing through the spectrum |
| 8 | When does a notch work? | 600 | on-bin vs off-bin (FIG_10), the width bet, the 20-row crop, automated design, Cassini |
| 9 | When is the FFT round trip cheaper? | 750 | four answers (FIG_11) |
| 10 | Where position is the answer: phase correlation | 450 | FIG_12; illumination vs noise; sub-pixel |
| 11 | The math | 650 | definitions, separability, shift, symmetry, Parseval, phase-only, notch, costs; collapse to the patch |
| 12 | Implementation: the tooling map | 450 | FIG_13 + tables + a not-run snippet |
| 13 | Limitations and common mistakes | 380 | named mistakes |
| 14 | Key takeaways | 130 | five claims |
| 15 | Try it yourself | 550 | the G0 ladder, E1–E5 |
| 16 | References | — | 26 sources |
| | **Total** | **≈ 9,040** | |

---

## Figure plan (route gate run per figure; the source check rejected all four paper figures)

| # | Section | One thing it must say | Route | Why | Draft caption |
|---|---|---|---|---|---|
| FIG_01 | Worked example | the 2-D DFT is a row pass then a column pass; the impulse is why row r2 differs | placed | Q4 — three grids of real complex values side by side | Rows first, then columns: four identical rows collapse into one bright line, and the odd row out spreads into every bin |
| FIG_02 | Worked example | the centred spectrum: DC, the bright row, the flat floor of 215 | placed | Q4 — a grid of real magnitudes, log-shaded, beside the patch | A vertical edge prints a horizontal line; one bright pixel prints a flat floor |
| FIG_03 | Worked example | phase only keeps positions; magnitude only moves everything to the origin | placed | Q4 — three grids of computed values | Keep the phase and the impulse stays at (2, 1); keep the magnitude and it moves to the corner |
| FIG_04 | Worked example | the swap: positions follow phase, the bar follows magnitude | placed | Q4 — four grids of computed values | Neither image wins: B's phase puts things where B has them; A's magnitude makes the bar vertical |
| FIG_05 | Worked example | the notch: corrupted tile, its spectrum's two spikes on the image-free lattice, mask, restored | placed | Q4 — grids of real values and a 10 × 10 spectrum | The interference lands on two bins the tile never uses, so zeroing them restores the tile exactly |
| FIG_06 | Intuition | position is the slope of a phase ramp | placed | Q4 — a grid of phasor arrows at their computed angles | Move the impulse and every arrow turns by an amount proportional to its frequency |
| FIG_07 | Reading | where each index lands after fftshift for N = 5 and N = 10 | placed | Q5 — two index strips, no crossing edges | On odd sizes fftshift and ifftshift differ by one sample |
| FIG_08 | Reading | the DFT sees the patch tiled; the wrap edge; the cross and three fixes | placed | Q4 — a tiled grid of real values with the invented edges marked | The edge the DFT invents between c4 and the next tile's c0 |
| FIG_09 | Filter design | ideal vs Gaussian transfer functions and their outputs on the row | plot | Q4 — values from closed forms at five frequencies, outputs at five samples | A brick wall in frequency digs a hole to 0.45 beside the edge; the Gaussian does not |
| FIG_10 | Notch | on-bin vs off-bin interference spectra over the tile's own bins | plot | Q4 — computed magnitudes on one column as bars | Three cycles land on two bins; two and a half spread over every bin, two of which the image needs |
| FIG_11 | Cost | flops per pixel vs kernel size: direct, separable, FFT route; OpenCV and textbook marks | plot | Q1 is no — a model from closed forms, not measured; Q4 — curves with marked thresholds | A model, not a timing: the FFT route is nearly flat in kernel size, and the full kernel crosses it near 10 |
| FIG_12 | Phase correlation | plain correlation's ridge vs phase correlation's single peak | placed | Q4 — two grids of computed values | Normalising every coefficient to unit magnitude turns a ridge into one peak |
| FIG_13 | Tooling map | which call does what, its normalisation, its layout, its trap | placed | Q5 — a comparison grid with no edges | NumPy, OpenCV, SciPy and scikit-image disagree on scaling, layout and when they switch to the FFT |

Social: 6 feed cards + 1 CTA, 4 Story frames. Cover: diagram-design template cover (placed), built by
`_cover.py` in the series house layout, from the spectrum motif (bright row through DC over a flat
floor).

---

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| 2-D DFT | Problem | the sum of the image against every 2-D complex wave on the grid | the transform this post reads | any spectrum |
| bin / coefficient | Problem | one (kr, kc) entry of the DFT | what a filter multiplies | reading spectra |
| magnitude / phase | Problem | the length and angle of a coefficient | they carry different information | always |
| DC term | Worked example | the (0, 0) bin, the pixel sum | dominates the display | scaling |
| separability (of the DFT) | Worked example | rows then columns | why it costs two passes | implementation |
| fftshift / centring | Reading | reordering bins so DC sits in the middle | display only | odd sizes |
| conjugate symmetry | Reading | F(−k) = conj F(k) for a real image | half the spectrum is redundant | rfft2, CCS |
| log display | Reading | showing log(1 + abs F) | DC hides everything else | inspecting |
| periodic extension / wrap | Reading | the tiling the DFT assumes | invents edges at the border | every spectrum |
| spectral leakage | Notch | energy of an off-bin frequency spreading across bins | why notches need width | periodic noise |
| window (Hann) | Reading | a taper to zero at the borders | suppresses the cross | phase correlation |
| periodic-plus-smooth decomposition | Reading | splitting an image into a tileable part and a smooth part | removes the cross without tapering | spectra, interpolation |
| phase-only / magnitude-only image | Worked example | inverse of unit-magnitude or zero-phase coefficients | what each half carries | demonstrations |
| whitening | What survives | flattening the magnitude | why phase-only images look like edge maps | — |
| phase congruency | Intuition | features where components are maximally in phase | why edges live in phase | feature detection |
| transfer function / zero-phase filter | Filter design | the per-bin gain; a real, even gain moves nothing | non-zero phase shifts features | design |
| ideal low-pass / ringing | Filter design | a brick-wall gain; its sinc kernel overshoots | the Gibbs dip | choosing a shape |
| notch reject filter | Worked example | a gain of 0 at chosen bins, 1 elsewhere | removes periodic interference | periodic noise |
| zero padding / fast sizes | Filter design | growing the array to M + m − 1 and a 2·3·5-smooth length | linear, not circular, convolution; speed | FFT convolution |
| phase correlation | Phase correlation | the inverse of the unit-magnitude cross-power spectrum | finds a translation | registration |
| flop | Cost | one floating-point add or multiply | the model's unit | cost models |
