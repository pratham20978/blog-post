# Source ledger — laplacian-by-hand

Tier L4 pillar, child of `image-processing-by-hand`. Research pass run 2026-09-14.
Every row below was taken from a fetched document (PDF text, rendered HTML, or a
publisher/OpenAlex abstract record), never from a search snippet. OpenCV rows resolve
to the 4.13.0 documentation build (generated 2025-12-31), which is what
`docs.opencv.org/4.x/` serves on the access date; source rows carry a commit hash.

Nothing was executed against an image for this post. Every number in the post is
either worked by hand on the shared 5×5 patch (and cross-checked with plain-Python
arithmetic, no packages), evaluated from a closed form and labelled as a model, or
carries a key from this ledger.

## Sources

| ID | Tier | Source | URL | Accessed |
|---|---|---|---|---|
| S1 | T1 | Marr & Hildreth, "Theory of Edge Detection", Proc. R. Soc. Lond. B 207(1167):187–217, 1980 | https://www.hms.harvard.edu/bss/neuro/bornlab/qmbc/beta/day4/marr-hildreth-edge-prsl1980.pdf | 2026-09-14 |
| S2 | T1 | Burt & Adelson, "The Laplacian Pyramid as a Compact Image Code", IEEE Trans. Commun. COM-31(4):532–540, 1983 | https://persci.mit.edu/pub_pdfs/pyramid83.pdf | 2026-09-14 |
| S3 | T1 | Lindeberg, "Feature Detection with Automatic Scale Selection", IJCV 30(2):79–116, 1998 | https://people.kth.se/~tony/papers/cvap198.pdf | 2026-09-14 |
| S4 | T1 | Lindeberg, "Scale Selection", in Ikeuchi (ed.) *Computer Vision: A Reference Guide*, Springer, 701–713, 2014 | https://people.kth.se/~tony/papers/Lin14-ScSel-CompVisRefGuide.pdf | 2026-09-14 |
| S5 | T1 | Lowe, "Distinctive Image Features from Scale-Invariant Keypoints", IJCV 60(2):91–110, 2004 | https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf | 2026-09-14 |
| S6 | T1 | Koenderink, "The Structure of Images", Biol. Cybern. 50(5):363–370, 1984 — **cited through S5 and S7**; bibliographic record verified via Crossref, full text not reachable | https://doi.org/10.1007/BF00336961 | 2026-09-14 |
| S7 | T1 | Lindeberg, "Discrete Approximations of Gaussian Smoothing and Gaussian Derivatives", J. Math. Imaging Vis., 2024 (arXiv:2311.11317; DOI 10.1007/s10851-024-01196-9) | https://arxiv.org/abs/2311.11317 | 2026-09-14 |
| S8 | T1 | Canny, "A Computational Approach to Edge Detection", IEEE TPAMI 8(6):679–698, 1986 | https://cecas.clemson.edu/~ahoover/ece431/refs/Canny.pdf | 2026-09-14 |
| S9 | T1 | Torre & Poggio, "On Edge Detection", IEEE TPAMI 8(2):147–163, 1986 (also MIT AI Memo 768, 1984) — abstract via OpenAlex and the DSpace record | https://dspace.mit.edu/handle/1721.1/5636 | 2026-09-14 |
| S10 | T1 | Clark, "Authenticating Edges Produced by Zero-Crossing Algorithms", IEEE TPAMI 11(1):43–57, 1989 — abstract via OpenAlex | https://doi.org/10.1109/34.23112 | 2026-09-14 |
| S11 | T1 | Haralick, "Digital Step Edges from Zero Crossing of Second Directional Derivatives", IEEE TPAMI 6(1):58–68, 1984 | https://www.haralick.org/journals/04767475.pdf | 2026-09-14 |
| S12 | T1 | Yuille & Poggio, "Scaling Theorems for Zero Crossings", IEEE TPAMI 8(1):15–25, 1986 — abstract via OpenAlex | https://doi.org/10.1109/TPAMI.1986.4767748 | 2026-09-14 |
| S13 | T1 | Babaud, Witkin, Baudin & Duda, "Uniqueness of the Gaussian Kernel for Scale-Space Filtering", IEEE TPAMI 8(1):26–33, 1986 — abstract via OpenAlex | https://doi.org/10.1109/TPAMI.1986.4767749 | 2026-09-14 |
| S14 | T1 | Mikolajczyk & Schmid, "Scale & Affine Invariant Interest Point Detectors", IJCV 60(1):63–86, 2004 | https://www.robots.ox.ac.uk/~vgg/research/affine/det_eval_files/mikolajczyk_ijcv2004.pdf | 2026-09-14 |
| S15 | T1 | Pérez, Gangnet & Blake, "Poisson Image Editing", ACM Trans. Graph. 22(3):313–318, 2003 | http://www.irisa.fr/vista/Papers/2003_siggraph_perez.pdf | 2026-09-14 |
| S16 | T1 | Pech-Pacheco, Cristóbal, Chamorro-Martínez & Fernández-Valdivia, "Diatom Autofocusing in Brightfield Microscopy: A Comparative Study", Proc. ICPR 2000, vol. 3, 314–317 — abstract via OpenAlex | https://doi.org/10.1109/icpr.2000.903548 | 2026-09-14 |
| S17 | T3 | Pertuz, Puig & Garcia, "Analysis of Focus Measure Operators for Shape-from-Focus", Pattern Recognition 46(5):1415–1432, 2013 — **full text not reachable**; claims taken only from the authors' own summary page for the paper | https://sites.google.com/view/cvia/focus-measure | 2026-09-14 |
| S18 | T1 | Patra & Karttunen, "Stencils with Isotropic Discretization Error for Differential Operators", Numer. Methods Partial Differ. Equ. 22(4):936–953, 2006 — abstract via OpenAlex | https://doi.org/10.1002/num.20129 | 2026-09-14 |
| S19 | T1 | LeVeque, *Finite Difference Methods for Ordinary and Partial Differential Equations*, SIAM, 2007, ch. 3 (Elliptic Equations) — book site and table of contents | https://faculty.washington.edu/rjl/fdmbook/ | 2026-09-14 |
| S20 | T1 | Gonzalez & Woods, *Digital Image Processing*, 4th ed., Pearson, 2018 — detailed table of contents | https://imageprocessingplace.com/downloads_V3/dip4e_downloads/dip4e_sample_book_material/dip4e_detailed_TOC.pdf | 2026-09-14 |
| S21 | T2 | OpenCV 4.13.0 docs, Image Filtering module (`Laplacian`, `Sobel`, `getDerivKernels`, `pyrDown`, `pyrUp`, `buildPyramid`) | https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html | 2026-09-14 |
| S22 | T3 | OpenCV source, `modules/imgproc/src/deriv.cpp`, branch 4.x at commit 2f779c5c36b33dd48355ae841664e7df52a805b2 | https://github.com/opencv/opencv/blob/2f779c5c36b33dd48355ae841664e7df52a805b2/modules/imgproc/src/deriv.cpp | 2026-09-14 |
| S23 | T2 | OpenCV 4.13.0 docs, tutorial "Laplace Operator" | https://docs.opencv.org/4.x/d5/db5/tutorial_laplace_operator.html | 2026-09-14 |
| S24 | T2 | SciPy 1.18.0 manual, `scipy.ndimage.laplace` and `scipy.ndimage.gaussian_laplace` | https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.gaussian_laplace.html | 2026-09-14 |
| S25 | T3 | SciPy source, `scipy/ndimage/_filters.py`, main at commit 3f342072018bad9dc1c2dddad7e1ea203d8652f5 | https://github.com/scipy/scipy/blob/3f342072018bad9dc1c2dddad7e1ea203d8652f5/scipy/ndimage/_filters.py | 2026-09-14 |
| S26 | T2 | scikit-image 0.26.0 docs, `skimage.feature.blob_log`, `blob_dog`, `blob_doh` | https://scikit-image.org/docs/stable/api/skimage.feature.html | 2026-09-14 |
| S27 | T3 | scikit-image source, `src/_skimage2/feature/blob.py`, main at commit 5d91fed804ec8d9133118f02b3a785790df75934 | https://github.com/scikit-image/scikit-image/blob/5d91fed804ec8d9133118f02b3a785790df75934/src/_skimage2/feature/blob.py | 2026-09-14 |
| S28 | T1 | Burt & Adelson, "A Multiresolution Spline with Application to Image Mosaics", ACM Trans. Graph. 2(4):217–236, 1983 — abstract via OpenAlex | https://doi.org/10.1145/245.247 | 2026-09-14 |
| S29 | T1 | Paris, Hasinoff & Kautz, "Local Laplacian Filters: Edge-Aware Image Processing with a Laplacian Pyramid", ACM Trans. Graph. 30(4), 2011 — abstract via OpenAlex | https://doi.org/10.1145/2010324.1964963 | 2026-09-14 |
| S30 | T1 | Lindeberg, *Scale-Space Theory in Computer Vision*, Kluwer, 1994 — **cited through S7** (Proposition 4.14) and S5; not fetched | https://doi.org/10.1007/978-1-4757-6465-9 | 2026-09-14 |
| S31 | T1 | Witkin, "Scale-Space Filtering", Proc. IJCAI-83, 1019–1022, 1983 — **cited through S5, S7 and S12**; not fetched | — | 2026-09-14 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | The Laplacian is the only orientation-independent linear second-order differential operator; its zero values coincide with the zero-crossings of the second directional derivative provided the smoothed intensity varies linearly *along* the line of zero-crossings, and are displaced to one side when it does not | S1 p.194 (theorem 2, appendix A) | the "condition of linear variation"; approximately true after Gaussian smoothing |
| L02 | In two dimensions ∇²G(r) = −(1/πσ⁴)(1 − r²/2σ²)·exp(−r²/2σ²), the "Mexican hat" | S1 p.194 | continuous, radially symmetric |
| L03 | The central negative region of ∇²G has diameter w = 2√2σ, so the zeros sit at r = √2σ; Marr & Hildreth ran filters with w = 6, 12 and 24 pixels | S1 fig. 6 p.201; follows from L02 | — |
| L04 | ∇²G is the limit of a difference of two Gaussians as their space constants approach each other | S1 p.193 and appendix B p.215–216 | — |
| L05 | Marr & Hildreth chose σ_i/σ_e ≈ 1.6 for the DOG as the best *engineering* approximation to ∇²G: below 1.6 the bandwidth is roughly constant but sensitivity is poor (about 33% of the excitatory peak at 1.6); at 1.6 the half-sensitivity bandwidth is 1.8 octaves and half-power 1.3 octaves | S1 appendix B p.216–217, fig. 11 | a bandwidth-versus-sensitivity trade-off, not a claim of best pointwise fit |
| L06 | Rosenfeld & Kak (1976) had discussed the Laplacian for edge detection without it being used effectively; Marr & Hildreth attribute that to using it outside a band-limited setting and without zero-crossings | S1 p.200 | historical attribution as stated by S1 |
| L07 | ∇²G is an approximately band-pass operator with a half-power bandwidth of about 1.2 octaves and half-sensitivity bandwidth of about 1.75 octaves | S1 p.193, p.195 | — |
| L08 | The Marr–Hildreth detector applies no threshold; Canny's operator supplies an edge-strength estimate that can be thresholded | S8 p.691 | Canny's characterisation |
| L09 | Zero-crossing detection has three steps: convolve with the second-derivative operator, locate the zero-crossings, and check the alignment and orientation of local segments | S1 p.193–194 | — |
| L10 | The Gaussian pyramid's generating kernel is a separable 5-tap weight that is normalised, symmetric, and satisfies "equal contribution" (a + 2c = 2b), forcing ŵ(±1) = 1/4 and ŵ(±2) = 1/4 − a/2 with ŵ(0) = a free | S2 p.533 | separable 5×5 REDUCE; sample density halves per level |
| L11 | a = 0.5 gives triangular equivalent weights, a = 0.4 Gaussian-like, a = 0.3 broader than Gaussian | S2 p.534, fig. 2 | equivalent weighting functions after repeated REDUCE |
| L12 | Laplacian pyramid level L_l = g_l − EXPAND(g_{l+1}), with L_N = g_N; the original is recovered exactly by expanding and summing the levels | S2 p.535 | — |
| L13 | Each Laplacian level equals the difference of two Gaussian-like equivalent weighting functions convolved with the image, "similar to convolving an appropriately scaled Laplacian"; the levels are band-pass copies and the operator scale doubles per level | S2 p.535 | — |
| L14 | With their quantisation and assuming variable-length codes, the 257×257 "Lady" image coded at 1.58 bits/pixel and "Walter" at 0.73 bits/pixel; the estimated entropy of the original "Lady" is 7.57 bits/pixel | S2 p.537–539 | their images, uniform quantisation, entropy × sample density accounting |
| L15 | Progressive transmission: pyramid levels 4–8 alone reconstruct a coarse image at 0.03 bits/pixel, growing to 0.31, 0.81 and 1.58 as lower levels are added | S2 fig. 9 p.539 | "Lady" image |
| L16 | The γ-normalised derivative is ∂_ξ = t^{γ/2}∂_x; with γ = 1 the operator is dimensionless and perfectly scale-invariant, so the scale-normalised Laplacian is t∇²L = σ²∇²L | S3 §4 eq. 9–10 | t = σ² |
| L17 | For a Gaussian blob with t₁ = t₂ = t₀ the magnitude of the normalised Laplacian at the centre has a unique maximum over scales at t = t₀, i.e. the selected scale equals the blob's own scale | S3 §5.1 eqs. 36–37 | Gaussian blob model |
| L18 | For a sinusoid of wavelength λ₀ an m-th order γ-normalised derivative peaks at σ = √(γm)·λ₀/(2π); for the second derivative with γ = 1 that is σ = λ₀/(√2π) | S3 §4.1 eq. 12 | 1-D sinusoid |
| L19 | Blob detection is done by finding scale-space extrema of the normalised Laplacian and drawing a circle whose radius is proportional to the selected scale | S3 §5, fig. 3 | — |
| L20 | Scale-space extrema are found by comparison with the 26 neighbours of a 3×3×3 space-scale neighbourhood, refined by fitting a parabola over scale | S4 "Discrete implementation" p.708 | 2-D images |
| L21 | Discrete scale normalisation is either variance-based (multiply the discrete derivative by t^{γ|α|/2}) or l_p-based; experiments show l_p-normalisation gives more accurate scale estimates when discretisation effects matter | S4 eqs. 14–16 | — |
| L22 | The Gaussian obeys ∂G/∂σ = σ∇²G, so G(kσ) − G(σ) ≈ (k − 1)σ²∇²G: a difference of Gaussians already carries the σ² normalisation | S5 §3 p.6 | first-order finite difference in σ |
| L23 | The (k − 1) factor is constant over scales and therefore does not move extrema; the approximation error vanishes as k → 1 and has "almost no impact" on extremum stability even at k = √2 | S5 §3 p.6 | Lowe's experience, not a bound |
| L24 | Lindeberg showed the σ² normalisation is required for true scale invariance; Mikolajczyk (2002) found the extrema of σ²∇²G more stable than those of the gradient, Hessian or Harris functions | S5 §3 p.6 | as reported by Lowe |
| L25 | Koenderink (1984) and Lindeberg (1994) showed that under reasonable assumptions the only scale-space kernel is the Gaussian | S5 §3 p.5; S6, S30 | cited through S5 |
| L26 | A DoG (and LoG) responds strongly along edges where the location is poorly determined; SIFT rejects keypoints with Tr(H)²/Det(H) ≥ (r+1)²/r, using r = 10 | S5 §4.1 p.11–12 | keypoint filtering, not edge detection |
| L27 | SIFT's base smoothing σ = 1.6 was chosen as an efficiency trade-off; k = 2^{1/s} with s = 3 intervals per octave | S5 §3.1 p.9–10 | — |
| L28 | Gaussian scale space is equivalently the solution of the diffusion equation ∂_s L = ½(∂_xx L + ∂_yy L) with s = σ² and L(·;0) = f | S7 §2 eq. 3 | continuous; attributed there to Iijima 1962, Witkin 1983, Koenderink 1984, Lindeberg 1993 |
| L29 | The separable discrete analogue of the Gaussian satisfies the semi-discrete diffusion equation ∂_s L = ½∇²₅L, where ∇²₅ is the five-point stencil [0 1 0; 1 −4 1; 0 1 0] | S7 §2.6 eqs. 37–38, citing S30 Prop. 4.14 | discrete scale space; the five-point Laplacian is its generator |
| L30 | Sampled Gaussian kernels and sampled Gaussian derivatives show severe artefacts at very fine scales; convolving with the discrete analogue of the Gaussian and then applying small central-difference operators has the best properties at fine scales | S7 abstract, §1 | fine scales, roughly σ below one pixel |
| L31 | The sampled-and-renormalised Gaussian's variance is not σ² at small σ; the discrete analogue's variance is exactly s | S7 §2.7–3, figs. 4–5 | — |
| L32 | In one dimension the Marr–Hildreth detector is almost identical to Canny's, because maxima of the first-derivative response are zero-crossings of the second | S8 §VII p.691 | 1-D step edge |
| L33 | In two dimensions the Laplacian splits into a second derivative along the gradient plus one along the edge; the along-edge term contributes nothing to detection or localisation and only adds noise, which is why a directional operator performs better | S8 §VII p.692 | Canny's argument for directional operators |
| L34 | Marr & Hildreth's work is what made large-support operators practical, because the Gaussian window has minimal bandwidth for its spatial width | S8 §VII p.691–692 | — |
| L35 | Numerical differentiation of images is ill-posed in Hadamard's sense and must be regularised by a filtering step before the differentiation step | S9 abstract | — |
| L36 | Torre & Poggio characterise the relation between the Laplacian and the second directional derivative along the gradient, and note the Laplacian's zero-crossings are not the only feature computed in early vision | S9 abstract | — |
| L37 | Zero-crossing detectors produce "phantom" edges that correspond to no significant intensity change; an authentic edge's contrast rises as the filter scale shrinks while a phantom's falls, and authentic edges are denser and stronger on average | S10 abstract | 1-D and 2-D synthetic and real signals |
| L38 | On Haralick's synthetic step-edge tests, zero-crossings of the second directional derivative ranked best, Prewitt next, and the Marr–Hildreth Laplacian zero-crossings worst | S11 abstract p.58 | his test images and his implementation of ∇²G; see open questions |
| L39 | In any dimension the Gaussian is the only linear filter that does not create new zero-crossings of the Laplacian as scale increases; for the second derivative along the gradient no filter avoids creating them unless filtering follows differentiation | S12 abstract | generic zero-crossings |
| L40 | In one dimension the Gaussian is the only kernel in a broad class for which the number of first-derivative extrema decreases monotonically as bandwidth grows | S13 abstract | 1-D signals |
| L41 | Among the differential operators Mikolajczyk & Schmid compared, the Laplacian-of-Gaussian found the highest percentage of correct characteristic scales, and the scale-adapted Harris measure rarely reached a maximum over scales | S14 §2.1 p.66–67 | their image set with known scale factors |
| L42 | LoG and DoG also produce local maxima near contours and straight edges where the signal changes in one direction; those are less stable, and the Hessian determinant penalises them | S14 §2.1 p.65 | — |
| L43 | Harris-Laplace uses the Harris function for position and the normalised Laplacian for scale | S14 §2.2 p.67 | — |
| L44 | The normalised LoG acts as a matched filter: its response peaks when the kernel size matches a blob-like structure | S14 p.66 (citing Duda & Hart 1973) | — |
| L45 | A scalar function on a bounded domain is uniquely determined by its boundary values plus its Laplacian in the interior; the Poisson equation with Dirichlet conditions therefore has a unique solution | S15 §1 p.313 | — |
| L46 | Slow intensity gradients, which the Laplacian suppresses, can be superimposed on an image with barely noticeable effect (Land & McCann 1971), which is why transplanting a Laplacian rather than pixel values gives a seamless result | S15 §1 p.313 | perceptual argument |
| L47 | The discrete Poisson solver works on the pixel grid with 4-connected neighbours, and for arbitrary boundaries it is better to discretise the variational problem than the PDE | S15 §2 p.315 | — |
| L48 | Burt–Adelson multiresolution blending is an approximate insertion of the source Laplacian at the finest pyramid level; Poisson editing performs that insertion exactly | S15 §2 p.314 | — |
| L49 | Modified-Laplacian focus measures were reported to outperform the Tenengrad gradient measure for microscope autofocus | S16 abstract | brightfield microscopy of diatoms |
| L50 | Laplacian-based focus measures are more sensitive to noise than statistics-based ones, and the authors judge an absolute ranking of focus measures infeasible | S17 authors' summary page | full paper not reached; treat as the authors' summary |
| L51 | The standard five-point Laplacian's leading discretisation error is anisotropic; nine-point stencils exist whose leading error is isotropic, at extra cost usually under 20% | S18 abstract | 2-D, O(h²) and O(h⁴) variants |
| L52 | LeVeque's chapter 3 treats the five-point and nine-point Laplacian and their truncation errors | S19 table of contents | textbook location only; the expansions are worked in the post |
| L53 | Gonzalez & Woods treat Laplacian sharpening, unsharp masking and highboost filtering in §3.6 (pp. 199–208) and the Laplacian in the frequency domain in §4.9 (p. 335) | S20 table of contents | 4th edition |
| L54 | `cv::Laplacian` computes ∂²src/∂x² + ∂²src/∂y² from Sobel second derivatives when ksize > 1; when ksize == 1 it filters with [0 1 0; 1 −4 1; 0 1 0]; ksize must be positive and odd; `scale` multiplies and `delta` offsets the result; BORDER_WRAP is unsupported | S21 `Laplacian()` | 4.13.0 |
| L55 | `getDerivKernels` accepts ksize ∈ {FILTER_SCHARR, 1, 3, 5, 7}; with normalize=true the coefficients are divided by 2^(ksize·2 − dx − dy − 2), and the docs suggest leaving them un-normalised when storing 8-bit derivatives in 16-bit | S21 `getDerivKernels()` | 4.13.0 |
| L56 | `Sobel` with ksize = 1 uses a bare 3×1 or 1×3 kernel with no smoothing and supports only first or second derivatives; an 8-bit `ddepth` truncates derivatives | S21 `Sobel()` | 4.13.0 |
| L57 | `pyrDown` convolves with (1/256)[1 4 6 4 1]ᵀ[1 4 6 4 1] and then drops even rows and columns; `pyrUp` injects zero rows and columns and convolves with the same kernel times 4; `buildPyramid` applies `pyrDown` recursively; the `pyrUp` entry notes it can be used to construct the Laplacian pyramid | S21 `pyrDown()`, `pyrUp()`, `buildPyramid()` | 4.13.0; BORDER_CONSTANT unsupported in pyrDown |
| L58 | OpenCV's Laplace tutorial smooths with `GaussianBlur` first, calls `Laplacian` with kernel_size 3 into CV_16S, converts with `convertScaleAbs`, and warns that zeros of the second derivative also appear at "meaningless locations" | S23 | tutorial code, compatibility OpenCV ≥ 3.0 |
| L59 | In the source, ksize 1 and ksize 3 both use a precomputed 3×3 kernel — {0,1,0,1,−4,1,0,1,0} and {2,0,2,0,−8,0,2,0,2} respectively — applied with `filter2D`; ksize 5 and 7 build Sobel second-derivative kernels with `getSobelKernels(…, 2, 0, ksize)` and add two separable passes | S22 lines 625–700 | 4.x branch at the cited commit |
| L60 | `getSobelKernels` uses [1 2 1], [−1 0 1], [1 −2 1] for ksize 3 and a Pascal-triangle recursion for larger sizes; kernel size must be odd and ≤ 31; normalisation divides each 1-D kernel by 2^(ksize − order − 1) | S22 lines 86–160 | — |
| L61 | The ksize 3 kernel {2,0,2,0,−8,0,2,0,2} is exactly the sum of the Sobel second-x kernel [1 2 1]ᵀ[1 −2 1] and its transpose | derived in the post from L59–L60 | shown arithmetic |
| L62 | `scipy.ndimage.laplace` sums, over the axes, a correlation with [1, −2, 1]; the default border mode is 'reflect' | S24; S25 lines 1079–1081 | SciPy 1.18.0 |
| L63 | `scipy.ndimage.gaussian_laplace(sigma)` sums, over the axes, `gaussian_filter` with derivative order 2 on that axis: the analytic second derivative of a sampled Gaussian, truncated at `truncate`·σ (default 4.0), with no σ² normalisation | S24; S25 lines 666–720, 1085–1134 | SciPy 1.18.0 |
| L64 | `skimage.feature.blob_log` returns each blob's coordinates and the σ that detected it, with radius ≈ √2σ in 2-D and √3σ in 3-D | S26 | scikit-image 0.26.0 |
| L65 | `blob_log` builds its scale cube as −gaussian_laplace(image, s)·mean(s)² — the σ² normalisation plus a sign flip so bright blobs are maxima — and finds extrema with `peak_local_max` over a 3×3×3 footprint in space and scale | S27 lines 626–639 | main at the cited commit |
| L66 | `blob_dog` defaults to sigma_ratio = 1.6, forms each DoG level as G(previous σ) − G(current σ), and multiplies the cube by 1/(sigma_ratio − 1) | S26; S27 lines 244, 416–427 | Marr–Hildreth's ratio and Lowe's (k − 1) factor, in library code |
| L67 | Burt & Adelson's multiresolution spline blends images band by band, with a transition zone proportional to the wavelengths in that band, so coarse features blend over long distances without blurring fine detail | S28 abstract | — |
| L68 | Paris, Hasinoff & Kautz showed edge-preserving smoothing, detail enhancement and tone mapping using standard Laplacian pyramids with point-wise nonlinearities, contradicting the belief that the pyramid cannot represent edges well | S29 abstract | — |
| L69 | Burt & Adelson published the Laplacian pyramid in IEEE Trans. Commun. in April 1983 | S2 header | — |
| L70 | The OpenCV documentation consulted is the 4.13.0 build | S21 footer | generated 2025-12-31 |

## Open questions

- Haralick's ranking (L38) placed the Marr–Hildreth detector last. Published comments on
  that paper (IEEE TPAMI, 1985) reportedly argue his ∇²G implementation differed from
  Marr & Hildreth's and that a faithful one performs comparably. Those comments could not
  be fetched, so the post reports Haralick's ranking with its condition and does not
  assert the rebuttal as fact.
- Berzins, "Accuracy of Laplacian Edge Detectors", CVGIP 27(2):195–210, 1984, analyses
  localisation error of ∇²G zero-crossings under non-linear illumination. No abstract or
  text was reachable from any open record, so it is not used. The post's statements about
  zero-crossing displacement rest on L01 (Marr & Hildreth's own theorem 2) instead.
- Pertuz et al. 2013 (S17) is used only through the authors' summary page, and the post
  says so. The "best at low noise, most noise-sensitive" phrasing seen in search snippets is
  *not* used; only the summary page's weaker statement (L50) is.
- Koenderink 1984 (S6), Lindeberg 1994 (S30) and Witkin 1983 (S31) are cited through the
  papers that restate their results (S5, S7, S12). Their bibliographic records are verified;
  the post attributes the results to them as those papers do.
- Marr & Hildreth's 1.6 is a bandwidth–sensitivity trade-off (L05). Our own closed-form
  check (in the post) shows that at k = 1.6 the DoG's pointwise amplitude is about half of
  the (k − 1)σ²∇²G prediction and its central lobe is about 24% wider than the ∇²G at σ.
  This is not a contradiction: Lowe's argument (L23) is about extrema over scale, where a
  constant factor is irrelevant. The post says both.
- Nothing in this post rests on a measurement taken by us. Every curve is a closed form and
  is captioned as a model.
