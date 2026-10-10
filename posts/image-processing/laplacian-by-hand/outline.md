# Outline — The Laplacian by Hand

**Title:** The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening (57 chars)
**Slug:** `laplacian-by-hand`
**Tier:** L4 pillar · **Category:** algorithms · **Difficulty:** advanced
**Budget:** 8,700 words (L4 range 7,500–10,000) · **Figures:** 16 (L4 range 12–18)
**Parent:** `image-processing-by-hand` (https://canery.in/blogs/image-processing-by-hand) —
this is the first child post. It reuses the parent's 5×5 patch and its Gaussian, and it
links back rather than re-teaching sampling, separability or borders.

Nothing was run against an image. Every number is worked by hand on the patch (and
cross-checked with plain-Python arithmetic, no packages), evaluated from a closed form and
captioned as a model, or carries a ledger key.

---

## The spine

One operator, five jobs, and one identity that ties them together:

```
∇²  =  what Gaussian blur removes per unit of scale        (∂L/∂s = ½∇²L)
```

| Job | What the Laplacian is used as | Section |
|---|---|---|
| Sharpen | the thing you add back | body 2 |
| Find edges | the thing whose zero you locate | body 3 |
| Find blobs and their size | the thing whose σ²-scaled extremum you search | body 4 |
| Split scales | the thing each pyramid level stores | body 5 |
| Keep instead of pixels | the thing you transplant or measure | body 6 |

The teaching rule from the parent applies without exception: **number first, then the
symbol, then one plain sentence.** The 4-neighbour kernel appears as arithmetic on the
patch before it is ever written as ∇².

---

## The shared patch (from the parent)

```
        c0   c1   c2   c3   c4
r0      40   40   40  200  200
r1      40   40   40  200  200
r2      40  255   40  200  200      ← impulse at (2,1); "clean" = 40 there
r3      40   40   40  200  200
r4      40   40   40  200  200
```

Every hand-computed value in the post, verified before drafting:

| Quantity | Where | Value |
|---|---|---|
| 4-nbr Laplacian at (2,2), clean / with impulse | worked example | **+160** / **375** (a 134% error from one pixel) |
| 4-nbr Laplacian at (2,3) | worked example | **−160** → zero-crossing sits exactly on the step |
| 4-nbr Laplacian at the impulse (2,1) | worked example | **−860** (5.4× the edge response) |
| Sharpen g = f − ∇²f at (2,2) / (2,3), clean | body 2 | **−120 → 0** / **360 → 255**: the halo, both sides |
| Sharpen at (2,2) with impulse; at the impulse | body 2 | **−335 → 0**; **1115 → 255** |
| 8-nbr kernel at (2,2), clean / impulse | body 1 | **480** / 695 (≈ 3∇²) |
| OpenCV ksize=3 kernel at (2,2), clean / impulse | body 1 | **640** / **640** — the impulse is invisible here |
| OpenCV ksize=3 at (1,2), clean / impulse | body 1 | 640 / **1070** — the damage moved diagonally (67%) |
| 9-point kernel at (2,2), clean / impulse | body 1 | 160 / 303.3 |
| 3×3 Gaussian σ=0.8 (parent's) | body 2, 3 | corner 0.0571, edge 0.1248, centre 0.2725; **true variance 0.478**, not 0.64 |
| Blur-minus-original on f = x²+y² (∇²f = 4) | body 2 | **0.956 = (0.478/2)·4** — the heat-equation identity, exact with the true variance |
| 5×5 LoG kernel = ∇²₅ ∘ G₃ | body 3 | centre −0.591, 4-nbr −0.1123, diagonal +0.021, ring 0.0571/0.1248; sums to 0 |
| LoG at (2,2), clean / impulse | body 3 | **45.3** / **21.1** — damage cut 9× in absolute terms, still a 53% relative error |
| Smoothed row 2, cols 1–3, clean / impulse | body 3 | [40.0, 78.2, 161.8] / [98.6, 105.1, 161.8] |
| Transfer function at \|ω\|=π, five-point, axis / diagonal | body 1 | **−4 / −6.42** (continuous −π² = −9.87) |
| Same, nine-point | body 1 | −4 / −4.70 |
| Low-frequency expansions | the math | five-point −\|ω\|² + (ωₓ⁴+ω_y⁴)/12 (anisotropic); nine-point −\|ω\|² + \|ω\|⁴/12 (isotropic) |
| 1-D second difference at Nyquist | the math | −4 vs −π²: the discrete operator under-reads curvature by 2.47× at the top of the band |
| DoG at k=1.6, σ=1, vs (k−1)σ²∇²G | body 3 | centre amplitude ratio **0.51**; DoG zero at r = 1.756 vs ∇²G zero at √2 = 1.414 (**24% wider**) |
| Scale-normalised bar response, width 3, amplitude 160 | body 4 | peak at **σ = w/2 = 1.5** (−77.4); σ = 1.0: −62.2; σ = 3.0: −56.3 |
| Scale-normalised disc response, radius 3, amplitude 160 | body 4 | peak at **σ = r/√2 = 2.12** (−117.7); σ = 1.5: −86.6; σ = 4.0: −67.9 |
| Burt–Adelson kernel with a = 0.375 | body 5 | [1 4 6 4 1]/16 — OpenCV's `pyrDown` kernel |
| Pyramid storage | body 5 | 1 + ¼ + 1/16 + … = **4/3** of the image |

The 45°-rotated and diagonal facts follow from the same patch; nothing new is introduced.

---

## Sections and budget

| # | Section | Words | What the reader can do after it that no other section gives them |
|---|---|---|---|
| 1 | Insights + Who this is for | 260 | Name the one identity (blur removes the Laplacian) and the five jobs it explains |
| 2 | Why this matters | 350 | Recognise that `Laplacian(ksize=3)` returning 4× the expected magnitude is not a bug in their code |
| 3 | The problem | 700 | State what a second derivative of a sampled signal can and cannot mean, and why every discrete Laplacian is a choice |
| 4 | Worked example | 1,300 | Compute the 4-neighbour Laplacian, locate a zero-crossing, and quantify what one bad pixel does to it |
| 5 | Intuition | 875 | Say in one sentence what ∇² measures (neighbour average minus centre) and why that is both an edge finder and a noise amplifier |
| 6 | Body 1 — Which discrete Laplacian? | 520 | Read any 3×3 second-derivative kernel and say what multiple of ∇² it approximates and along which directions it is wrong |
| 7 | Body 2 — Sharpening: the thing blur removes | 510 | Show that unsharp masking and Laplacian sharpening are one operator, and predict the halo's sign and width |
| 8 | Body 3 — Zero-crossings: why the Laplacian finds edges twice | 560 | Run a zero-crossing detector and know which of its edges to distrust, and why Canny replaced it |
| 9 | Body 4 — Scale selection: σ²∇²G as a ruler | 540 | Pick σ from a target blob size, or read a detected σ back as a size, and say why DoG is allowed to stand in |
| 10 | Body 5 — The pyramid: the same operator, resampled | 470 | Build a Laplacian pyramid with `pyrDown`/`pyrUp` and say why reconstruction is exact |
| 11 | Body 6 — Keeping the Laplacian instead of the pixels | 450 | State what Poisson cloning preserves and why the seam vanishes; use variance-of-Laplacian knowing what it is sensitive to |
| 12 | The math | 875 | Read ∇² as the trace of the Hessian, its transfer function, the LoG closed form and the normalised-derivative argument, and collapse each back onto the patch numbers |
| 13 | Implementation: the tooling map | 700 | Map each job to the exact OpenCV / SciPy / scikit-image call, with the scaling that each one silently applies |
| 14 | Limitations and common mistakes | 440 | Avoid six documented traps, each with its symptom |
| 15 | Key takeaways + References | 150 | — |

Total: 8,700.

Body sections are 6 (rows 6–11), the L4 maximum. Rows 8 and 9 are distinct: row 8 is
about *where* the response is zero, row 9 about *at which σ* it is extremal. Rows 10 and 11
are distinct: row 10 stores the Laplacian to reconstruct the same image; row 11 keeps the
Laplacian to build a different one.

---

## The padding test, answered per section

- **The problem** vs **Intuition**: the problem section says what a discrete second
  derivative *is not* (a derivative of anything you have); intuition says what it *is*
  (neighbour average minus centre). No overlap.
- **Body 1** vs **The math**: body 1 gives the kernels and the two numbers that show
  anisotropy; the math gives the Taylor and Fourier forms that produce those numbers. The
  math never restates the kernel table.
- **Body 2** vs **Body 3**: both use the Gaussian, but body 2 subtracts it from the image
  and body 3 takes its Laplacian. Different output, different failure.
- **Body 4** vs **Body 3**: body 3 never varies σ; body 4 only varies σ.
- **Body 5** vs **Body 6**: reconstruction vs editing, as above.
- **Why this matters** vs **Limitations**: the opening names one symptom (4×); limitations
  names six with their conditions and does not repeat the 4× story, it points back to it.

No section ends with a summary sentence. Key takeaways is the only summary.

---

## Child / sibling posts named, not expanded

| Named in | Post |
|---|---|
| Body 3 | Canny, line by line: NMS and hysteresis (parent's stage 5 child) |
| Body 4 | Scale space and SIFT: why σ is a search dimension (parent's scale child) |
| Body 4 | The structure tensor: Harris, Shi–Tomasi, optical flow (parent's child; Harris-Laplace is named here) |
| Body 5 | Wavelets and multiresolution (parent's stage 3 child; the pyramid is where they start) |
| Body 6 | Gradient-domain editing: Poisson, HDR compression, seamless cloning (new child) |
| Body 1, The math | Kernel design: separability, borders, optimised derivative filters (parent's stage 2 child) |
| Body 2 | Edge-preserving smoothing (parent's stage 4 child) — named as the answer to halos |

---

## Figure plan

All 16 are diagrams or closed-form illustrations. The three that draw curves (6, 8, 12)
and the two profile figures (7, 10) are captioned as models. No data plots — nothing was
measured.

| ID | Section | The one thing it must communicate | Route | Draft caption |
|---|---|---|---|---|
| FIG_01 | The problem | First difference peaks at a step; second difference goes +/− and crosses zero on it | hand-authored SVG (the row profile 40 40 40 200 200 with both differences) | The edge is a peak in the first difference and a zero-crossing in the second — the same place, two signatures |
| FIG_02 | Worked example | The 3×3 window at (2,2) and (2,3) and the arithmetic that gives +160 and −160 | diagram-design | The zero-crossing lies between column 2 and column 3, which is exactly where the step is |
| FIG_03 | Worked example | The same arithmetic with the impulse present: 375 at (2,2), −860 at (2,1) | diagram-design | One pixel three columns from the edge changes the edge response by 134% and produces the largest value in the patch |
| FIG_04 | Intuition | ∇²f = 4 × (neighbour average − centre) | diagram-design | The Laplacian asks one question: how far is this pixel from what its neighbours expect? |
| FIG_05 | Body 1 | Five stencils and the multiple of ∇² each approximates | diagram-design | Five-point ×1, diagonal ×2, eight-neighbour ×3, OpenCV ksize=3 ×4, nine-point ×1 — same operator, four scales, two anisotropies |
| FIG_06 | Body 1 | Transfer function along the axis vs the diagonal for five-point, nine-point and the continuous −ω² | hand-authored SVG, **model** | At the top of the band the five-point stencil reads 60% more curvature on the diagonal than on the axis; the nine-point stencil reads 18% more |
| FIG_07 | Body 2 | Blur minus original is the Laplacian; adding it back overshoots on both sides | hand-authored SVG on the row values | The halo is the Laplacian with its sign flipped, and it is one pixel wide because the stencil is |
| FIG_08 | Body 3 | The Mexican hat ∇²G with w = 2√2σ, and the DoG at ratio 1.6 laid over it | hand-authored SVG, **model** | The DoG's central lobe is 24% wider and half as deep; neither matters for where the zero is |
| FIG_09 | Body 3 | The 5×5 LoG kernel as numbers, built from the 3×3 Gaussian and the five-point stencil | diagram-design | This is the Mexican hat at σ = 0.8: a negative disc of radius 1.13 pixels and a positive ring, summing to zero |
| FIG_10 | Body 3 | An authentic zero-crossing (maximum of \|f'\|) next to a phantom one (minimum of \|f'\|) between two edges | hand-authored SVG, **model** | Both are zeros of the second derivative; only one is an edge, and the slope of the crossing tells them apart |
| FIG_11 | Body 3 | Canny's decomposition: ∇² = second derivative across the edge + second derivative along it | hand-authored SVG | The along-edge term is zero on a straight edge and pure noise everywhere else |
| FIG_12 | Body 4 | Scale-normalised response vs σ for the width-3 bar and the radius-3 disc, peaks at 1.5 and 2.12 | hand-authored SVG, **model** | The σ at the peak is the size: w/2 for a bar, r/√2 for a disc |
| FIG_13 | Body 4 | The space–scale cube and the 26-neighbour extremum test; DoG levels as (k−1)σ²∇²G | diagram-design layers | A blob is a point that beats its 8 spatial neighbours and its 18 neighbours one scale up and down |
| FIG_14 | Body 5 | REDUCE, EXPAND, subtract, and the exact reconstruction path | Mermaid flowchart → diagram-design | The pyramid stores the Laplacian at each scale and the residual at the top; adding them back is exact by construction |
| FIG_15 | Body 6 | Poisson editing: boundary from the target, Laplacian from the source, pixels solved for | diagram-design nested | What is transplanted is the source's Laplacian; the pixel values are whatever makes that consistent with the target's boundary |
| FIG_16 | Implementation | Each job mapped to the exact call and the scale factor that call silently applies | diagram-design | The map from math to call site — with the ×4, the missing σ², and the 1/(k−1) written on the arrows |

Plus `COVER`.

---

## Hard constraints carried from the brief

- **Nothing run against an image.** Plain-Python arithmetic was used to cross-check the
  hand computations; no NumPy, OpenCV, SciPy or scikit-image call was executed, and the
  post says so. No timings, no benchmarks, no measured curves.
- **Number, symbol, sentence** — every operator is evaluated on the patch before it is
  written in notation, and every equation is followed by a plain sentence.
- **Every figure is our own redraw**; captions credit the source of the idea.
- **Frontmatter carries both schemas** — the nine fields `validate_post.py` requires plus
  `categories`, `cover_image_url`, `cover_image_alt` for the canery parser; `cover_image_url`
  holds the `COVER` placeholder until `fill_urls.py` resolves it.
- **Series link**: the Insights block names the parent, and the parent's child list gains
  this post at the next parent edit (not touched here).
