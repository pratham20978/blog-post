# Source ledger — kernel-design-separability-borders-derivatives

Series `image-processing`, part 4. Sweep run 2026-09-25. Tier L3, so the floor is 7
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

How each source was read is stated per row, because it varies. Farid & Simoncelli 2004,
Lindeberg 2024 and the Weickert–Scharr technical report were read in full as PDFs
(`pdftotext`, with page images where the text layer garbled a formula). Freeman & Adelson 1991
is a scan with no text layer; its steering equation was read off the page image (p. 892). Five
peer-reviewed sources — Lindeberg 1990, Kannappan & Sahoo 1992, Treitel & Shanks 1971,
Martucci 1994 and Ando 2000 — were paywalled and are used **only for what their own abstracts
state** (retrieved from the OpenAlex record, cross-checked against Crossref for venue and
pages). Their claim rows say so in the Condition column, and the post does not lean on them for
anything their abstracts do not say.

Library behaviour was read at pinned commits, source and documentation both. Nothing was
executed against an image; the only code run was plain-Python (`math` module) arithmetic that
reproduces the post's own hand-worked numbers and evaluates closed-form transfer functions.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Farid & Simoncelli, "Differentiation of Discrete Multidimensional Signals" | IEEE Trans. Image Processing 13(4), pp. 496–508 | 2004 | 10.1109/TIP.2004.823819 | peer-reviewed | https://farid.berkeley.edu/downloads/publications/tip04.pdf | 2026-09-25 |
| S02 | T1 | Weickert & Scharr, "A Scheme for Coherence-Enhancing Diffusion Filtering with Optimized Rotation Invariance", Technical Report 4/2000, Computer Science Series, University of Mannheim (revised and shortened as JVCIR 13(1–2):103–118, 2002, doi:10.1006/jvci.2001.0495) | Univ. Mannheim tech. report | 2000 | Mannheim CS TR 4/2000 | preprint | https://www.mia.uni-saarland.de/weickert/Papers/TR-4-00.ps.gz | 2026-09-25 |
| S03 | T1 | Lindeberg, "Discrete Approximations of Gaussian Smoothing and Gaussian Derivatives" (read as arXiv:2311.11317v7) | J. Mathematical Imaging and Vision 66(5), pp. 759–800 | 2024 | 10.1007/s10851-024-01196-9 | peer-reviewed | https://arxiv.org/abs/2311.11317 | 2026-09-25 |
| S04 | T1 | Lindeberg, "Scale-Space for Discrete Signals" (abstract only) | IEEE Trans. PAMI 12(3), pp. 234–254 | 1990 | 10.1109/34.49051 | peer-reviewed | https://doi.org/10.1109/34.49051 | 2026-09-25 |
| S05 | T1 | Freeman & Adelson, "The Design and Use of Steerable Filters" | IEEE Trans. PAMI 13(9), pp. 891–906 | 1991 | 10.1109/34.93808 | peer-reviewed | https://people.csail.mit.edu/billf/publications/Design_and_Use_of_Steerable_Filters.pdf | 2026-09-25 |
| S06 | T1 | Kannappan & Sahoo, "Rotation Invariant Separable Functions are Gaussian" (abstract only) | SIAM J. Mathematical Analysis 23(5), pp. 1342–1351 | 1992 | 10.1137/0523076 | peer-reviewed | https://doi.org/10.1137/0523076 | 2026-09-25 |
| S07 | T1 | Treitel & Shanks, "The Design of Multistage Separable Planar Filters" (abstract only) | IEEE Trans. Geoscience Electronics 9(1), pp. 10–27 | 1971 | 10.1109/TGE.1971.271457 | peer-reviewed | https://doi.org/10.1109/TGE.1971.271457 | 2026-09-25 |
| S08 | T1 | Martucci, "Symmetric Convolution and the Discrete Sine and Cosine Transforms" (abstract only) | IEEE Trans. Signal Processing 42(5), pp. 1038–1051 | 1994 | 10.1109/78.295213 | peer-reviewed | https://doi.org/10.1109/78.295213 | 2026-09-25 |
| S09 | T1 | Ando, "Consistent Gradient Operators" (abstract only) | IEEE Trans. PAMI 22(3), pp. 252–265 | 2000 | 10.1109/34.841757 | peer-reviewed | https://doi.org/10.1109/34.841757 | 2026-09-25 |
| S10 | T3 | OpenCV source, `modules/imgproc/src/smooth.dispatch.cpp` | — | 2026 | commit bed6800f056e | source | https://github.com/opencv/opencv/blob/bed6800f056e57f6c945a7bd56e324e0fa965e24/modules/imgproc/src/smooth.dispatch.cpp | 2026-09-25 |
| S11 | T3 | OpenCV source, `modules/imgproc/src/deriv.cpp` | — | 2026 | commit bed6800f056e | source | https://github.com/opencv/opencv/blob/bed6800f056e57f6c945a7bd56e324e0fa965e24/modules/imgproc/src/deriv.cpp | 2026-09-25 |
| S12 | T2 | OpenCV 4.x documentation, Image Filtering — `Sobel`, `Scharr`, `getDerivKernels`, `getGaussianKernel`, `GaussianBlur`, `filter2D`, `sepFilter2D` | — | 2026 | imgproc.hpp @ bed6800f056e | official-docs | https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html | 2026-09-25 |
| S13 | T2 | OpenCV 4.x documentation, Core — `BorderTypes` | — | 2026 | core/base.hpp @ bed6800f056e | official-docs | https://docs.opencv.org/4.x/d2/de8/group__core__array.html | 2026-09-25 |
| S14 | T3 | OpenCV source, 2.4 branch, `modules/imgproc/src/smooth.cpp` | — | 2026 | branch 2.4 | source | https://github.com/opencv/opencv/blob/2.4/modules/imgproc/src/smooth.cpp | 2026-09-25 |
| S15 | T3 | SciPy source, `scipy/ndimage/_filters.py` | — | 2026 | commit 0aed21639223 | source | https://github.com/scipy/scipy/blob/0aed21639223d28e32bc0320a2b70767b14b432d/scipy/ndimage/_filters.py | 2026-09-25 |
| S16 | T2 | SciPy documentation, `scipy.ndimage` filters — the `mode` parameter (generated from `_ni_docstrings.py`) | — | 2026 | commit 0aed21639223 | official-docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_filter.html | 2026-09-25 |
| S17 | T2 | NumPy documentation, `numpy.pad` (generated from `_arraypad_impl.py`) | — | 2026 | commit a98529dfd92d | official-docs | https://numpy.org/doc/stable/reference/generated/numpy.pad.html | 2026-09-25 |
| S18 | T3 | scikit-image source, `src/_skimage2/filters/edges.py` | — | 2026 | commit 533b7694d200 | source | https://github.com/scikit-image/scikit-image/blob/533b7694d2004ae84e49e2cfd0bcfc5f8e562f22/src/_skimage2/filters/edges.py | 2026-09-25 |

Notes on individual sources:

- **S01** was read as the authors' accepted manuscript (header "VOL. XX, NO. XX"); section,
  equation and table numbers were checked against the version of record's venue and pages via
  Crossref. The comparison paragraph of §IV-A was read off a page image because the text layer
  dropped the square roots.
- **S02** is the long original of the JVCIR paper, which the authors' own publication list
  describes as a revised and shortened version of this report. The journal version was not read
  (ScienceDirect paywall). It is marked `preprint` because a technical report is not
  journal-reviewed, and the post names it as a technical report. The PostScript was converted
  with `ps2pdf` and read in full; the minus signs in its equation (7) are lost in the text layer
  and were read from the rendered page.
- **S03** is CC BY 4.0 in its version of record (Crossref licence field). The version of record
  on link.springer.com served a bot challenge, so the arXiv v7 was read; its figure numbers are
  therefore not verified against the journal (see Figure candidates).
- **S12 / S13**: `docs.opencv.org` served a Cloudflare challenge on 2026-09-25 (the same as for
  Part 3). The pages are generated by Doxygen from the header comments, which were read at
  commit bed6800f056e (2026-09-24).
- **S14** establishes only that the fixed 3/5/7-tap table predates the 4.x rewrite; the 4.x
  table (S10) adds a 9-tap entry.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | `search=derivative filter design image gradient survey`, sorted by citations | Noise — SciPy 1.0, Faster R-CNN, genetics guidelines; full-text search is useless for this topic. Moved to title filters |
| 2 | 1 | OpenAlex | `title.search:gradient operators`, sorted by citations | Complex-gradient papers and the Sobel 2014 retrospective (Part 1's source); no survey of discrete derivative design exists under that title |
| 3 | 1 | OpenAlex | `title.search:differentiation of discrete multidimensional signals` | Farid & Simoncelli 2004 (IEEE TIP, 231 citations); its §I is the closest thing to a survey — finite differences, polynomial fits, truncated Gaussians — and it became S01 |
| 4 | 1 | OpenAlex | `search=optimized rotation invariance derivative filter Scharr` | Diffusion and CT papers that use Scharr's filters; pointed to the Weickert–Scharr scheme |
| 5 | 1 | OpenAlex | forward chase: `cites:W2167272056` (Farid & Simoncelli), sorted by citations | 231 citing works, almost all applications (restoration, forensics, optical flow); none corrects the filters |
| 6 | 1 | OpenAlex | `title.search:coherence-enhancing diffusion filtering optimized rotation invariance` | Weickert & Scharr 2002, JVCIR 13(1–2):103–118 |
| 7 | 1 | OpenAlex | `title.search:consistent gradient operators` | Ando 2000, IEEE TPAMI 22(3) — a third definition of an optimal gradient; became S09 |
| 8 | 1 | OpenAlex | `title.search:scale-space for discrete signals` | Lindeberg 1990, IEEE TPAMI 12(3) (625 citations); became S04 |
| 9 | 1 | OpenAlex | `title.search:discrete approximations of gaussian smoothing and gaussian derivatives` | Lindeberg 2024, JMIV 66(5), and its arXiv preprint; became S03 |
| 10 | 1 | OpenAlex | `title.search:rotation invariant separable functions are gaussian` | Kannappan & Sahoo 1992, SIAM J. Math. Anal. 23(5); became S06 |
| 11 | 1 | OpenAlex | `title.search:design and use of steerable filters` | Freeman & Adelson 1991 (2,950 citations); became S05 |
| 12 | 1 | OpenAlex | `title.search:symmetric convolution and the discrete sine and cosine transforms` | Martucci 1994, IEEE TSP 42(5); became S08 |
| 13 | 1 | OpenAlex | `title.search:multistage separable planar filters` | Treitel & Shanks 1971, the origin of splitting a 2-D filter into separable stages; became S07 |
| 14 | 1 | OpenAlex | `title.search:design of multi-dimensional derivative filters` | Simoncelli, ICIP 1994 — the predecessor of S01; not read, S01 supersedes it |
| 15 | 1 | OpenAlex | `title.search:Isotropieoptimierung`; `title.search:optimale operatoren digitalen bildverarbeitung` | Scharr, Körkel & Jähne 1997 (DAGM, doi:10.1007/978-3-642-60893-3_39) and Scharr's 2000 thesis (doi:10.11588/heidok.00000962) — the two primary sources for the 3×3 optimisation |
| 16 | 1 | heiDOK | Scharr 2000 thesis PDF | Anubis proof-of-work bot challenge; not read, not cited |
| 17 | 1 | ResearchGate | author-uploaded copies of Scharr 1997 and Scharr's optical-flow filter paper | challenge page to curl; not read, not cited |
| 18 | 1 | Heidelberg HCI | record for Jähne, Scharr & Körkel 1999, "Principles of Filter Design" | server returned a database error; not read |
| 19 | 1 | Google Scholar | `"Numerische Isotropieoptimierung" Scharr` | the 1997 paper, the 2002 scheme, its Mannheim technical report and Scharr's later optical-flow filters; the report was fetched from the authors' group page and became S02 |
| 20 | 1 | Google Scholar | `Kroon "Numerical optimization of kernel based image derivatives"` | citation record only (scikit-image's reference for Scharr); a student report, not used |
| 21 | 1 | Crossref | DOI lookups for S01, S03–S09 and the JVCIR version of S02 | venue, volume, issue, pages and year confirmed for all nine |
| 22 | 1 | arXiv | `abs:"derivative filter" AND abs:rotation`; `ti:derivative AND ti:filters` | nothing relevant — this literature is journal-only; 2311.11317 was fetched directly |
| 23 | 4 | Semantic Scholar | forward chase: citations of 10.1109/TIP.2004.823819, influential only | MaxPol (Hosseini & Plataniotis 2017, SIAM J. Imaging Sci.) as the influential successor; a further criterion, not a correction; not read |
| 24 | 4 | Google Scholar | the S02 report's own reference list (backward chase) | Scharr 1997 and Jähne 1999 as the source of the 3×3 result; the report gives the criterion's form (weighted L2 fit in the Fourier domain) but not its weighting function |
| 25 | 5 | OpenCV GitHub | `smooth.dispatch.cpp`, `deriv.cpp`, `imgproc.hpp`, `base.hpp` at bed6800f056e | fixed 3/5/7/9-tap tables for σ ≤ 0; ksize-from-σ rule; Sobel and Scharr kernels and their normalisation; border types; `BORDER_WRAP` unsupported in five filters |
| 26 | 5 | OpenCV GitHub | 2.4 branch `smooth.cpp` | `small_gaussian_tab` with the same 3/5/7-tap entries — the table is at least as old as 2.4 |
| 27 | 5 | SciPy / NumPy / scikit-image GitHub | `_filters.py`, `_ni_docstrings.py`, `_arraypad_impl.py`, `filters/edges.py` at pinned commits | truncation radius, mode names and their extensions, `np.pad` semantics, derivative weights and magnitude scaling |
| 28 | 4 | link.springer.com | version of record of S03 (CC BY 4.0) | bot challenge; arXiv v7 read instead |
| 29 | 6 | Web search | `Scharr optimized derivative filter 3x3 "3, 10, 3" rotation invariance weighting` | Wikipedia's Sobel article (not citable) attributes the result to a weighted mean-squared angular-error optimisation in the thesis; no other copy of the weighting |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Farid and Simoncelli assume a separable, symmetric interpolator p(x)p(y); the x-derivative is then the 1-D derivative filter d₁ along x and the prefilter p along y | S01 §II, eqs. (10)–(11) | identical filters on every axis |
| L02 | Their design constraint is that a derivative in any direction must equal the matching linear combination of the axis derivatives; in the Fourier domain this reduces to a 1-D Rayleigh quotient, the energy of jωP(ω) − D₁(ω) over the energy of P(ω) | S01 §II-A, eqs. (9), (14)–(16) | a frequency weighting may be added to the numerator; the published filters use none |
| L03 | The optimum is the generalised eigenvector for the smallest eigenvalue, rescaled so the prefilter sums to 1 | S01 §III-A | — |
| L04 | Their 3-tap pair is p = [0.229879, 0.540242, 0.229879], d₁ = ±0.425287; the 5-tap pair is p = [0.037659, 0.249153, 0.426375, …], d₁ = [0.109604, 0.276691, 0, …] | S01 Table I | first-order set; the 5-tap row designed with a second-order filter differs slightly |
| L05 | Because the interpolator is no longer a sinc, the filters differentiate a spectrally reshaped signal rather than the original one | S01 §II | — |
| L06 | Adding steerability to a separable interpolator built from one symmetric 1-D function forces that function to be a Gaussian | S01 §II | stated by the authors as the reason they do not impose steerability |
| L07 | For comparison they tuned 5- and 7-tap sampled Gaussian derivatives to σ = 0.96 and 1.12, the values that minimise their matching error, against the σ = 1.5 that Barron et al. suggest | S01 §IV-A | their criterion, their tuning |
| L08 | Non-separable designs improved accuracy only marginally, not enough to justify the cost | S01 §II, §V | as tested by the authors |
| L09 | On 32×32 sinusoidal gratings from 0.0078 to 0.4062 cycles/pixel, their filters gave substantially smaller orientation errors than the conventional ones | S01 §IV-A, Figs. 5–6 | the authors' measurement, not ours |
| L10 | The optimised 3×3 x-derivative is (1/32)·[−3 0 3; −10 0 10; −3 0 3], shown to approximate rotation invariance significantly better than Sobel-type stencils | S02 §3, eq. (7) | first-order derivative only |
| L11 | The central difference's transfer function is the ideal derivative's times a smoothing term; keeping the gradient's direction requires a matching smoothing across the derivative, and a weighted L2 optimisation in the Fourier domain gave [3, 10, 3]/16 as that cross-smoothing | S02 §3 | the report does not state the weighting function; it defers to Scharr 1997 and Jähne 1999 |
| L12 | Both optimised filters hold only two distinct values, which keeps them cheap — two multiplications per pixel | S02 §3 | — |
| L13 | At very fine scales the sampled Gaussian kernel can have its coefficients sum to more than 1 and a spatial variance substantially below the continuous kernel's | S03 §2.3 | — |
| L14 | Dividing the sampled kernel by its sum fixes the sum but not the variance deficit | S03 §2.4 | variance is unaffected by uniform scaling |
| L15 | The integrated Gaussian kernel (the continuous Gaussian integrated over each pixel) sums to 1 but its variance exceeds s by an offset that approaches 1/12 at coarse scales | S03 §2.5, eqs. (20)–(24) | the 1/12 is a unit box's variance |
| L16 | The discrete analogue of the Gaussian, T(n; s) = e^{−s} I_n(s) with I_n the modified Bessel function, has coefficients in [0, 1] summing to 1, variance exactly s, and an exact semigroup property | S03 §2.6, eqs. (26)–(31) | — |
| L17 | Sampled Gaussian kernels and derivatives are numerically very good above σ ≈ 1; below about 0.75 the sampled derivative estimates are not accurate, and the discrete analogue with central differences is much better | S03 abstract, §2.8 | the paper's experiments; its Figs. 4–5 put the threshold near σ = 0.75 |
| L18 | A separable Gaussian truncated at ±N costs 2(2N+1) operations per pixel against (2N+1)² non-separably | S03 §2.1.4, eqs. (11)–(12) | — |
| L19 | The paper truncates its kernels so the discarded tail mass is about 10⁻⁸, and notes practical implementations may accept more to trade accuracy for speed | S03 §2.1.4, footnote 2 | — |
| L20 | Discrete scale space should be built by discretising the diffusion equation rather than the convolution integral, which yields the discrete analogue of the Gaussian; a sampled-kernel implementation may misbehave, especially at fine scales | S04 abstract | abstract only |
| L21 | The first derivative of a Gaussian at any angle θ is cos θ times the x-derivative plus sin θ times the y-derivative, so two basis filters steer it | S05 §III, p. 892, eqs. (12)–(13) | — |
| L22 | Every rotation-invariant separable real function of two variables is a Gaussian or identically zero | S06 abstract | abstract only; no regularity assumptions needed |
| L23 | A 2-D filter array can be expanded into a finite sum of stages, each exactly separable as a column vector times a row vector; when a few stages approximate it well, the filter becomes cheap | S07 abstract | abstract only |
| L24 | Each of the 16 discrete sine and cosine transforms corresponds to one type of symmetric-periodic extension of a sequence, and convolution of symmetrically extended sequences is their product in that transform — the symmetric counterpart of circular convolution and the DFT | S08 abstract | abstract only |
| L25 | Ando defines optimal gradient operators by a consistency criterion that makes the gradient direction of a locally one-dimensional pattern exact whatever its orientation, spectrum or sub-pixel shift, and computes optimal 3×3 to 5×5 operators | S09 abstract | abstract only; his coefficients were not read and are not quoted |
| L26 | With σ ≤ 0 and n = 1, 3, 5, 7 or 9, `getGaussianKernel` returns a hard-coded table — [0.25, 0.5, 0.25] at 3 taps, [1 4 6 4 1]/16 at 5, [2 7 14 18 14 7 2]/64 at 7, [4 13 30 51 60 51 30 13 4]/256 at 9 — and does not sample a Gaussian | S10 `getGaussianKernelBitExact` | commit bed6800f056e |
| L27 | For any other case it samples exp(−x²/2σ²) at the tap positions and divides by the sum; with σ ≤ 0 and another n it uses σ = 0.15n + 0.35, which equals the documented formula | S10 `getGaussianKernelBitExact` | — |
| L28 | The documentation gives only the formula σ = 0.3((ksize − 1)·0.5 − 1) + 0.8 for non-positive σ and does not mention the table | S12 `getGaussianKernel` | header at bed6800f056e |
| L29 | The same 3-, 5- and 7-tap table existed in the 2.4 branch's `getGaussianKernel` | S14 `small_gaussian_tab` | — |
| L30 | When ksize is zero, `GaussianBlur` derives it from σ as round(σ·k·2 + 1) forced odd, with k = 3 for 8-bit images and 4 otherwise | S10 `createGaussianKernels` | σ > 0 |
| L31 | The `GaussianBlur` documentation recommends specifying ksize, sigmaX and sigmaY explicitly, because the defaulting may change | S12 `GaussianBlur` | — |
| L32 | OpenCV's 3-tap Sobel factors are [1 2 1] and [−1 0 1]; larger apertures are built by repeated convolution with [1 1] (binomial smoothing) followed by differencing; normalisation divides each factor by 2^(ksize − order − 1) | S11 `getSobelKernels` | — |
| L33 | The Scharr factors are [3 10 3] and [−1 0 1]; normalisation divides the smoothing factor by 32 and leaves the difference alone | S11 `getScharrKernels` | — |
| L34 | `Sobel` and `Scharr` build their kernels unnormalised and multiply only by the optional `scale` argument, default 1 | S11 `cv::Sobel`, `cv::Scharr` | — |
| L35 | `Sobel` takes ksize 1, 3, 5 or 7, with FILTER_SCHARR (−1) selecting the Scharr aperture, documented as possibly more accurate than the 3×3 Sobel | S12 `Sobel` | the docs do not quantify it |
| L36 | `getDerivKernels` documents the normalising denominator 2^(ksize·2 − dx − dy − 2) and recommends normalised kernels for float images but not when 8-bit derivatives go into a 16-bit result | S12 `getDerivKernels` | — |
| L37 | `Sobel`, `Scharr`, `GaussianBlur`, `filter2D` and `sepFilter2D` document `BORDER_WRAP` as not supported | S12 | — |
| L38 | OpenCV's border types, written as padding before a row abcdefgh: CONSTANT pads with a fixed value (iiiiii), REPLICATE repeats the edge (aaaaaa), REFLECT mirrors and repeats the edge (fedcba), WRAP continues from the far end (cdefgh), REFLECT_101 mirrors about the edge without repeating it (gfedcb); BORDER_DEFAULT is REFLECT_101 | S13 `BorderTypes` | — |
| L39 | SciPy's Gaussian filter samples the Gaussian on a radius of int(truncate·σ + 0.5) and divides by the sum; truncate defaults to 4.0 | S15 `gaussian_filter1d`, `_gaussian_kernel1d` | radius argument overrides |
| L40 | SciPy's filters default to mode 'reflect', which repeats the edge sample (half-sample symmetric: d c b a before a b c d); 'mirror' does not (whole-sample: d c b before a b c d); 'nearest', 'wrap' and 'constant' complete the set | S16; S15 signatures | — |
| L41 | SciPy's `sobel` correlates with [−1, 0, 1] along the axis and [1, 2, 1] along the others, unnormalised | S15 `sobel` | default mode 'reflect' |
| L42 | NumPy's `pad` mode 'reflect' excludes the edge value (3 2 1 2 3 4 5 for 1…5), 'symmetric' repeats it (2 1 1 2 3 …), and reflect_type='odd' continues the signal linearly (−1 0 1 2 …) | S17 examples | — |
| L43 | scikit-image's Sobel uses [1, 0, −1] with [1, 2, 1]/4, its Scharr [1, 0, −1] with [3, 10, 3]/16, its Prewitt [1, 0, −1] with [1, 1, 1]/3, and its Farid filter the 5-tap weights of Farid & Simoncelli's Table 1 | S18 module constants | — |
| L44 | scikit-image's edge magnitude is the square root of the summed squared axis responses divided by √ndim, and its edge filters default to mode 'reflect' | S18 `_generic_edge_filter` | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S03 | Fig. 4 (absolute scale difference vs σ for sampled, integrated and discrete kernels) | How many taps does σ need? / L13–L17 | shows directly where sampling alone loses variance | CC BY 4.0 on the version of record; the reachable arXiv copy carries arXiv's non-exclusive licence, and the version of record (and so its figure numbering) was unreachable | https://doi.org/10.1007/s10851-024-01196-9 | do not reuse; our FIG_09 separates truncation from sampling, which Fig. 4 does not show (it truncates at 10⁻⁸) |
| F2 | S01 | Figs. 5–6 (orientation error on gratings, per filter) | What does "optimal" mean? / L09 | the authors' measured comparison | IEEE copyright 2004; no licence found | https://doi.org/10.1109/TIP.2004.823819 | do not reuse; our FIG_06 plots closed-form angular error for the same filter family, labelled as a model |
| F3 | S02 | Fig. 2 (filter-design illustration for the optimised derivative) | Why is Scharr [3, 10, 3]? / L11 | the design in one picture | technical report, no licence stated | https://www.mia.uni-saarland.de/weickert/Papers/TR-4-00.ps.gz | do not reuse; our FIG_05 draws the matching curves with the worked numbers |

## Open questions

- **Scharr's exact weighting function.** The technical report says the cross-smoothing came from
  a weighted L2 optimisation in the Fourier domain and defers the details to Scharr 1997 and
  Jähne 1999. Both, and the 2000 thesis, were unreachable. The post therefore derives the
  leading-order optimum itself (p = 1/6), shows where the optimum moves under several stated
  weightings, and says only that 3/16 is the published result of a weighted fit. It never
  attributes a specific weighting to Scharr.
- **Why OpenCV keeps the fixed table.** The source hard-codes it without comment; the post says
  what it is and how old it is, not why.
- **Whether the JMIV version of S03 renumbered its figures.** Irrelevant to the post, which
  reuses no figure from it and cites sections and equations that were checked in v7.
- **Nothing was executed.** No claim rests on a measurement of ours. Every number in the post is
  hand-worked on the shared patch, evaluated from a closed form (and captioned so), or carries a
  key above.
