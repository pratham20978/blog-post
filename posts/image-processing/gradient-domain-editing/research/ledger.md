# Source ledger — gradient-domain-editing

Series `image-processing`, part 14. Researched 2026-10-15, inline (no agents). The series is G0: every
library behaviour below is read from source at a pinned commit or tag, or from the vendor's
documentation, and replayed in plain Python (`math` and `fractions`); nothing was run against an image.
The three central papers (Pérez 2003, Fattal 2002, Agarwala 2007) and the IPOL review were read in full
from author or open copies. Brandt 1977 and Saad 2003 were read from open copies (AMS archive, author's
site). Six follow-ups are cited for what their abstracts state, and the rows say so.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Pérez, Gangnet & Blake, "Poisson image editing" (read in full from the INRIA/IRISA author copy) | ACM Transactions on Graphics 22(3):313–318 (SIGGRAPH 2003) | 2003 | 10.1145/882262.882269 | peer-reviewed | http://www.irisa.fr/vista/Papers/2003_siggraph_perez.pdf | 2026-10-15 |
| S2 | T1 | Fattal, Lischinski & Werman, "Gradient domain high dynamic range compression" (read in full from the authors' copy) | ACM Transactions on Graphics 21(3):249–256 (SIGGRAPH 2002) | 2002 | 10.1145/566654.566573 | peer-reviewed | https://www.cs.huji.ac.il/~danix/hdr/hdrc.pdf | 2026-10-15 |
| S3 | T1 | Agarwala, "Efficient gradient-domain compositing using quadtrees" (read in full from the author's preprint) | ACM Transactions on Graphics 26(3), article 94 (SIGGRAPH 2007) | 2007 | 10.1145/1276377.1276495 | peer-reviewed | https://agarwala.org/efficient_gdc/preprint.pdf | 2026-10-15 |
| S4 | T1 | Di Martino, Facciolo & Meinhardt-Llopis, "Poisson Image Editing" (review of the method since 2003 plus two implementations; read in full) | Image Processing On Line 6:300–325 | 2016 | 10.5201/ipol.2016.163 | peer-reviewed | https://www.ipol.im/pub/art/2016/163/article_lr.pdf | 2026-10-15 |
| S5 | T1 | Saad, *Iterative Methods for Sparse Linear Systems*, 2nd edition, SIAM (author's copy): §4.2 (Theorem 4.16, eq. 4.47), §13.2–13.4 | SIAM | 2003 | 10.1137/1.9780898718003 | peer-reviewed | https://www-users.cse.umn.edu/~saad/IterMethBook_2ndEd.pdf | 2026-10-15 |
| S6 | T1 | Brandt, "Multi-level adaptive solutions to boundary-value problems" (abstract and §3 read in the AMS open archive) | Mathematics of Computation 31(138):333–390 | 1977 | 10.1090/S0025-5718-1977-0431719-X | peer-reviewed | https://www.ams.org/journals/mcom/1977-31-138/S0025-5718-1977-0431719-X/S0025-5718-1977-0431719-X.pdf | 2026-10-15 |
| S7 | T1 | Jia, Sun, Tang & Shum, "Drag-and-drop pasting" (abstract only) | ACM Transactions on Graphics 25(3):631–637 | 2006 | 10.1145/1141911.1141934 | peer-reviewed | https://doi.org/10.1145/1141911.1141934 | 2026-10-15 |
| S8 | T1 | Farbman, Hoffer, Lipman, Cohen-Or & Lischinski, "Coordinates for instant image cloning" (abstract only) | ACM Transactions on Graphics 28(3), article 67 | 2009 | 10.1145/1531326.1531373 | peer-reviewed | https://doi.org/10.1145/1531326.1531373 | 2026-10-15 |
| S9 | T1 | McCann & Pollard, "Real-time gradient-domain painting" (abstract only) | ACM Transactions on Graphics 27(3), article 93 | 2008 | 10.1145/1360612.1360692 | peer-reviewed | https://doi.org/10.1145/1360612.1360692 | 2026-10-15 |
| S10 | T1 | Kazhdan & Hoppe, "Streaming multigrid for gradient-domain operations on large images" (abstract only) | ACM Transactions on Graphics 27(3), article 21 | 2008 | 10.1145/1360612.1360620 | peer-reviewed | https://doi.org/10.1145/1360612.1360620 | 2026-10-15 |
| S11 | T1 | Simchony, Chellappa & Shao, "Direct analytical methods for solving Poisson equations in computer vision problems" (abstract only) | IEEE Transactions on Pattern Analysis and Machine Intelligence 12(5):435–446 | 1990 | 10.1109/34.55103 | peer-reviewed | https://doi.org/10.1109/34.55103 | 2026-10-15 |
| S12 | T1 | Mantiuk, Myszkowski & Seidel, "A perceptual framework for contrast processing of high dynamic range images" (abstract only) | ACM Transactions on Applied Perception 3(3):286–308 | 2006 | 10.1145/1166087.1166095 | peer-reviewed | https://doi.org/10.1145/1166087.1166095 | 2026-10-15 |
| S13 | T3 | OpenCV source, commit 802cf95: `modules/photo/src/seamless_cloning.cpp`, `seamless_cloning_impl.cpp`, `seamless_cloning.hpp`, `include/opencv2/photo.hpp`, `src/tonemap.cpp`; `modules/imgproc/src/morph.dispatch.cpp` | — | 2026 | commit 802cf95aa3d42816995695bf68a86b3532f12760 | source | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/photo/src/seamless_cloning_impl.cpp | 2026-10-15 |
| S14 | T3 | OpenCV source, tags 4.10.0 (2024-06-03), 4.11.0 (2025-01-09), 4.12.0, 4.13.0, 4.14.0 (2026-07-19) and 5.0.0 (2026-06-06): the same photo files, compared with 802cf95; release dates from the GitHub releases list | — | 2024–2026 | tags 4.10.0, 4.11.0, 4.12.0, 4.13.0, 4.14.0, 5.0.0 | source | https://github.com/opencv/opencv/blob/4.14.0/modules/photo/src/seamless_cloning.cpp | 2026-10-15 |
| S15 | T3 | OpenCV issue tracker and history: issue #17450 (open), #12053 (closed 2018-08-20), #21902 (closed 2024-12-19), #25947; commit 860ae77ec9 (2018-08-06); pull request #26511 (merged 2024-12-19) | — | 2018–2024 | issues #17450, #12053, #21902; PR #26511 | source | https://github.com/opencv/opencv/issues/17450 | 2026-10-15 |
| S16 | T2 | MathWorks, `regionfill` (Image Processing Toolbox) documentation, release R2026b | — | 2026 | R2026b | official-docs | https://www.mathworks.com/help/images/ref/regionfill.html | 2026-10-15 |
| S17 | T3 | Luminance HDR source, `src/TonemappingOperators/fattal02/tmo_fattal02.cpp` (Krawczyk's pfstmo port of Fattal 2002), last commit 764fb836 | — | 2019 | commit 764fb83683c03385b1986a8b6da3122a24798d68 | source | https://github.com/LuminanceHDR/LuminanceHDR/blob/764fb83683c03385b1986a8b6da3122a24798d68/src/TonemappingOperators/fattal02/tmo_fattal02.cpp | 2026-10-15 |
| S18 | T2 | SciPy documentation, `scipy.fft.dstn` and `idstn`, v1.18.0 | — | 2026 | v1.18.0 | official-docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.fft.dstn.html | 2026-10-15 |
| S19 | T3 | Part 2 of this series, *The Laplacian by Hand: Edges, Blobs, Pyramids, Sharpening* (published): the five-point stencil, its values on the patch and the section "Keeping the Laplacian instead of the pixels" | canery.in | 2026 | — | source | https://canery.in/blogs/laplacian-by-hand | 2026-10-15 |
| S20 | T3 | Part 11 of this series, *Thresholding and Segmentation: Otsu, Sauvola, Watershed* (built, not yet published): the patch's shadowed copy at a fifth of the light | canery.in | 2026 | — | source | https://canery.in/blogs/thresholding-and-segmentation | 2026-10-15 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar (curl) | "gradient domain" image editing survey | no survey of gradient-domain image editing; the hits were Bhat 2008 (screened Poisson), a mesh-deformation survey, Fattal 2002 (1,983 citations) and a stitching survey, so the IPOL review (row 7) serves as the map |
| 2 | 1 | OpenAlex | title.search "Poisson image editing" | Pérez 2003 in TOG (1,773 citing works) and its SIGGRAPH record (2,020); the 2023 ACM reprint; DOIs recorded |
| 3 | 1 | OpenAlex | title.search "Gradient domain high dynamic range compression" | Fattal 2002 in TOG (777) and its SIGGRAPH record (1,120) |
| 4 | 1 | OpenAlex | title.search "Efficient gradient-domain compositing using quadtrees" | Agarwala 2007 in TOG, article 94 (113) |
| 5 | 1 | OpenAlex | forward chase: cites Pérez 2003, sorted by citations | applications dominate (face forgery, inpainting, Szeliski's stitching tutorial, Interactive Digital Photomontage, Levin 2004 gradient-domain stitching); no correction among the top 40 |
| 6 | 4 | OpenAlex | forward chase: cites Pérez 2003 with title terms drag-and-drop, coordinates, error-tolerant, convolution pyramids, multigrid, screened, gradient domain, blending, bleeding | the corrections and faster solvers: Jia 2006 (boundary optimisation), Farbman 2009 (mean-value coordinates), Tao 2010/2013 (error-tolerant compositing), Kazhdan and Hoppe 2008, McCann and Pollard 2008, Bhat 2008, Farbman 2011 convolution pyramids, Krishnan and Szeliski 2011, Morel IPOL 2014, "Avoiding bleeding in image blending" (ICIP 2017, 5 citations) |
| 7 | 1 | OpenAlex | title.search "poisson image editing", year 2016 | Di Martino, Facciolo and Meinhardt-Llopis, IPOL 2016: a peer-reviewed review of the method since 2003 with finite-difference and Fourier implementations |
| 8 | 1 | Crossref | DOI lookups for 20 sources (Brandt, Jia, Farbman ×2, Tao, Kazhdan, McCann, Bhat, IPOL, Land, Horn, Frankot, Szeliski, Saad, Burt, Levin, Pérez, Fattal, Agarwala, Simchony, Mantiuk) | all resolved; venues, volumes and pages recorded from Crossref |
| 9 | 1 | Semantic Scholar | influential citations of Pérez 2003; search "gradient domain image editing poisson survey" | HTTP 429 on both, blocked for the session |
| 10 | 4 | arXiv | ti:poisson AND ti:blending | one hit, a 2024 learned Poisson solver: learned methods are out of the series' scope |
| 11 | 4 | Google Scholar (curl) | "gradient domain high dynamic range compression" halo OR artifacts critique | one tone-mapping paper; no published critique of Fattal's attenuation found this way, so the zero-gradient case (L37) rests on the paper's own formula |
| 12 | 2 | author and open pages | irisa.fr (Pérez), cs.huji.ac.il (Fattal), agarwala.org (Agarwala), ipol.im (IPOL review) | all four read in full; equations, parameters and reported results recorded below |
| 13 | 3 | AMS open archive | Brandt 1977, Math. Comp. 31(138) | abstract and §3 read: O(n) work, the O(h⁻²) sweeps of plain relaxation, smoothing factor 0.5 for Gauss–Seidel on Poisson |
| 14 | 3 | author's site | Saad, *Iterative Methods for Sparse Linear Systems*, 2nd ed. | §4.2 (Young's theorem 4.16, ω_opt 4.47), §13.2 (model-problem eigenvalues, Jacobi and Gauss–Seidel factors), §13.3–13.4 (full weighting, Galerkin coarse operator, V-cycle, cost) |
| 15 | 5 | GitHub issues | repo:opencv/opencv seamlessClone is:issue | 26 issues: #17450 (the three-pixel erosion, open since 2020), #12053 (mask changed in place, closed 2018), #21902 and #25947 (placement), #19646 (time grows with image size) |
| 16 | 5 | GitHub pull requests | repo:opencv/opencv seamlessClone is:pr | 8 PRs; #26511 (2024-11-24, merged 2024-12-19) adds the `*_WIDE` flags and also rewrites `checkMask` |
| 17 | 5 | GitHub raw files | seamless_cloning*.cpp, photo.hpp, tonemap.cpp at 802cf95; tags 4.10.0, 4.11.0, 4.12.0, 4.13.0, 4.14.0, 5.0.0; morph.dispatch.cpp at 802cf95 | 802cf95 equals 4.14.0 and, for the solver, 5.0.0; 4.10.0 differs in `checkMask`, the `*_WIDE` cases and a `.clone()` of the destination ROI |
| 18 | 4 | GitHub history | commits touching modules/photo/src/seamless_cloning.cpp; diffs of 860ae77ec9 and PR #26511 | 860ae77ec9 (2018-08-06) replaced `gray = mask` with `mask.copyTo(gray)`; PR #26511 replaced the copy with `return mask.getMat()`; every release from 4.11.0 carries it |
| 19 | 2 | OpenAlex | abstracts for Jia 2006, Farbman 2009, McCann 2008, Kazhdan 2008, Simchony 1990, Mantiuk 2006, Bhat 2008, Tao 2013 | six abstracts read; Bhat 2008 and Tao 2013 (Springer) withheld, so neither is cited |
| 20 | 5 | WebFetch (MathWorks) | `regionfill` documentation | R2026b page: inward interpolation from the region's outer boundary by solving the Dirichlet problem of the discrete Laplacian, introduced R2015a; stencil not stated |
| 21 | 5 | GitHub raw files | Luminance HDR `tmo_fattal02.cpp` | the gradient magnitude is floored at 1e-4 and a user-set noise term is added before the power; GPL-2.0 file, read only |
| 22 | 5 | WebFetch (SciPy) | `scipy.fft.dstn` | v1.18.0: types 1–4, `idstn` the inverse |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | The membrane interpolant (no guidance) solves the Laplace equation with the destination's boundary values and gives a blurred fill; with a guidance field v the minimiser of the squared distance between the image's gradient and v, with the boundary fixed, solves the Poisson equation Laplacian f = div v | S1 §2, eq. 1–4 | continuous form; Dirichlet boundary |
| L02 | When v is the gradient of a source g, the correction f − g inside the region is the membrane interpolant of the mismatch between destination and source on the boundary | S1 §2, eq. 5 | conservative guidance only |
| L03 | The discrete form gives, at each pixel of the region, the number of in-image neighbours times f_p minus the sum of the unknown neighbours equals the sum of known boundary neighbours plus the sum of guidance differences; with imported gradients the guidance difference on an edge is g_p − g_q; the authors discretise the variational problem directly for irregular boundaries, and the system is sparse, symmetric and positive definite | S1 §2, eq. 6–8, 11 | 4-connected neighbours |
| L04 | Pérez et al. solved the system by Gauss–Seidel with successive over-relaxation or by V-cycle multigrid, about 0.4 s per system for a 60,000-pixel disc on a Pentium 4 | S1 §2 | their 2003 hardware |
| L05 | Mixed seamless cloning keeps, on each edge, the destination's difference where its magnitude exceeds the source's and the source's otherwise; the paper shows it stopping a destination object that touches the region from bleeding into it | S1 §3, eq. 12–13, Fig. 8 | per edge |
| L06 | Monochrome transfer turns the source grey before cloning, so only its intensity pattern transfers | S1 §3, Fig. 5 | — |
| L07 | Texture flattening keeps a difference only where an edge detector marks an edge between the two pixels, and sets the rest to zero | S1 §4, eq. 14–15 | — |
| L08 | Local illumination change uses the guidance alpha^beta times the gradient over its magnitude to the power beta, in the log domain, with alpha 0.2 times the mean gradient norm over the region and beta 0.2 | S1 §4, eq. 16 | — |
| L09 | Seamless tiling: for a rectangular region the source is the image itself and opposite sides receive identical Dirichlet values, north and south both set to half the sum of the original north and south rows, and likewise east and west | S1 §4, Fig. 12 | rectangular region |
| L10 | Pérez et al. cite Land and McCann for the observation that slow gradients of intensity can be laid over an image with barely noticeable effect | S1 §1 | perceptual claim, cited secondhand |
| L11 | Fattal et al. work on the logarithm of luminance, where gradients correspond to ratios (local contrasts) | S2 §3 | — |
| L12 | In one dimension the attenuated derivatives integrate directly; the paper's example scanline goes from 2,415:1 to 7.5:1 | S2 §3, Fig. 3 | their example |
| L13 | In two dimensions the attenuated field is not necessarily a gradient, so the method seeks the image whose gradient is closest in least squares, which satisfies the Poisson equation with the field's divergence; projecting onto an integrable basis (Frankot and Chellappa) is the alternative they mention | S2 §3, eq. 2–3 | — |
| L14 | The attenuation factor at each level is (alpha over the gradient magnitude) times (magnitude over alpha) to the power beta, with alpha 0.1 times the average gradient magnitude and beta between 0.8 and 0.9; gradients below alpha are slightly magnified; the factors from a Gaussian pyramid whose coarsest level is at least 32 pixels wide are upsampled and multiplied; level gradients use central differences | S2 §4 | the paper's settings |
| L15 | Fattal et al. use Neumann boundary conditions, so the solution is defined up to a constant, which they remove by shifting and scaling to the display | S2 §5 | — |
| L16 | They take the gradient by forward differences and the divergence by backward differences, consistent with the five-point Laplacian, and solve with the Full Multigrid algorithm with Gauss–Seidel smoothing in O(n); an FFT solver would be O(n log n) | S2 §5 | — |
| L17 | Fattal et al.'s example scenes span about 25,000:1 (the lobby), over 100,000:1 (a streetlight at night) and over 250,000:1 (a church interior), against a monitor typically below 100:1 | S2 §1, §6 | their radiance maps and their display figure |
| L19 | The residual of the colour-copy starting image is zero away from seams, so the correction is smooth there; a quadtree reduces the unknowns to O(p), p the seam length, typically O(sqrt n) | S3 §3, §3.2 | — |
| L20 | In Agarwala's tests the reduced system had 0.38–0.94% as many variables as pixels, with per-pixel RMS error in the hundredths and colours differing by at most two levels after rounding | S3 §4, Table 1 | five-image panoramas and one paste, 8-bit red channel |
| L21 | The original image is recovered exactly only when the gradient discretisation and the Laplacian match (forward differences with backward divergence for the five-point stencil); central differences give a close but different image | S4 §3, Remarks | discrete setting |
| L22 | The finite-difference solve leaves the destination unchanged outside the region; the Fourier approach solves the whole rectangle with the background's gradients outside the region and Neumann boundaries, an approximation | S4 §3.2, §5 | — |
| L24 | Results of a modified field leave the display range and must be renormalised; IPOL uses the simplest colour balance, saturating a small percentage at each end | S4 §4 | — |
| L25 | The 2-D model problem's eigenvalues are 4 − 2cos(kπ/(n+1)) − 2cos(lπ/(m+1)) with eigenvectors sin(kπx)sin(lπy) | S5 §13.2, eq. 13.14 | Dirichlet model problem |
| L26 | Richardson/Jacobi reduces each mode by one minus its eigenvalue over four: the smoothest mode by 1 − O(h²), the oscillatory modes by at most a half in 1-D | S5 §13.2.1–13.2.2 | — |
| L27 | Gauss–Seidel's eigenvalues on the model problem are the squares of Jacobi's, cos²(kπ/(n+1)), by Young's theorem for consistently ordered matrices | S5 §13.2.3, Theorem 4.16 | lexicographic ordering |
| L28 | The best SOR factor is 2/(1 + sqrt(1 − rho_J²)) for consistently ordered matrices | S5 §4.2, eq. 4.47 | — |
| L29 | A V-cycle pre-smooths, forms the residual, restricts it, solves or recurses on the coarse grid, interpolates the correction back, adds it and post-smooths | S5 §13.4.3, Algorithm 13.3 | — |
| L30 | Full weighting in 2-D averages with the stencil 1/16 [1 2 1; 2 4 2; 1 2 1], bilinear interpolation is four times its transpose, the Galerkin coarse operator is restriction times the fine operator times interpolation, and in 2-D with full weighting it differs from the re-discretised operator | S5 §13.3, eq. 13.36, 13.39 | — |
| L31 | The cost of one V-cycle is linear in the number of unknowns | S5 §13.4.3, eq. 13.44 | fixed smoothing steps |
| L32 | Multigrid solves the n discrete equations in O(n) operations, about 40n additions and shifts for Poisson problems | S6 abstract | — |
| L33 | Plain relaxation converges at 1 − O(h²) per sweep, so O(h⁻²) sweeps per order of magnitude; in multigrid relaxation only smooths the error and coarser grids remove the smooth part; Gauss–Seidel's smoothing factor on Poisson is 0.5, so three sweeps cut high-frequency error by almost an order of magnitude | S6 §3 | — |
| L34 | Poisson editing works well only when salient structures of source and target do not conflict along the boundary; Jia et al. optimise the boundary with a shortest closed path | S7 abstract | — |
| L35 | The membrane of the boundary discrepancy can be evaluated at each pixel as a weighted combination of boundary values (mean-value coordinates) instead of solving a linear system | S8 abstract | approximation of the membrane |
| L36 | Multigrid scales: a GPU multigrid integrates megapixel gradient fields at over 20 frames per second (McCann and Pollard), and a streaming multigrid tone-maps and stitches gigapixel images in about an hour on a notebook (Kazhdan and Hoppe) | S9 abstract; S10 abstract | their hardware |
| L37 | Fattal's factor uses central differences, which read zero at a lone one-pixel spike, so the formula is unbounded there for beta below 1; Luminance HDR's port floors the magnitude at 1e-4 and adds a user-set noise term | S2 §4 (formula); S17 lines 250–255 | single level, our arithmetic on the patch |
| L38 | Fast orthogonal transforms solve the Poisson equation directly on a rectangle | S11 abstract | rectangular domain |
| L39 | Mantiuk et al.'s contrast framework, inspired by gradient-domain methods, constrains contrasts at all scales and avoids reversing contrast polarity | S12 abstract | — |
| L40 | `seamlessClone` zeroes the mask's outer one-pixel frame, takes the mask's bounding rectangle as the region, places it so that p is the rectangle's centre (without a `_WIDE` flag), and uses the destination rectangle's frame as the boundary | S13 seamless_cloning.cpp L66–103 | 802cf95; same at 4.14.0 and 5.0.0 |
| L41 | Its guidance is forward differences ([0 −1 1]) of the source inside the mask and of the destination elsewhere in the rectangle, and its divergence uses backward differences | S13 seamless_cloning_impl.cpp L48–96, L290–321 | — |
| L42 | Before use the mask is eroded by a 3×3 square three times, which `morphOp` folds into a single 7×7 erosion that reads the zeros outside the bounding rectangle; issue #17450, open since 2020, reports it | S13 impl L259–261, morph.dispatch.cpp L1010–1033; S15 #17450 | all versions read |
| L43 | The solve is a discrete sine transform (a DFT of an odd extension) dividing by 2cos(π(i+1)/(w−1)) + 2cos(π(j+1)/(h−1)) − 4: a direct solve, no iteration | S13 impl L98–162, L235–246 | rectangle only |
| L44 | Interior results are clamped to 0–255 and truncated rather than rounded; a source comment says saturate_cast is avoided on purpose | S13 impl L181–192 | 8-bit output |
| L45 | `MIXED_CLONE` compares abs(gx − gy) of source and destination, per channel, and takes both components from the winner | S13 impl L340–375 | Pérez compares each edge's magnitude (L05) |
| L46 | `MONOCHROME_TRANSFER` converts the source to grey before taking its gradients | S13 impl L377–386 | — |
| L47 | The `*_WIDE` flags came with PR #26511 (merged 2024-12-19, first released in 4.11.0); with them p locates the centre of the source image, which is how the documentation describes p for every flag | S13 seamless_cloning.cpp L85–92, photo.hpp L753–795; S14; S15 PR #26511, #21902 | — |
| L48 | From 4.11.0 `checkMask` returns a single-channel mask without copying it, so `seamlessClone` zeroes its frame and then erodes and inverts its bounding rectangle in the caller's own array, and `colorChange`, `illuminationChange` and `textureFlattening`, which pass the same mask to the same `Cloning` code, erode and invert it too; 4.10.0 copied it, the fix from commit 860ae77ec9 for issue #12053 | S13 seamless_cloning.cpp L50–64, L79–80, L106–154, impl L261, L311; S14; S15 #12053, 860ae77ec9, PR #26511 | read from source, not run |
| L49 | `illuminationChange` scales the gradient by alpha^beta times its magnitude to the power −beta on the 8-bit codes, with alpha as given (default 0.2, beta 0.4), not in log and not relative to the mean gradient | S13 impl L407–432, photo.hpp L825–826 | compare L08 |
| L50 | `textureFlattening` keeps gradients only where Canny (defaults 30, 45, aperture 3) marks an edge in the masked source | S13 impl L434–451, photo.hpp L843–845 | — |
| L51 | OpenCV's gradient-domain tone mapper is Mantiuk's: log of grey, contrasts on all pyramid levels, mapped, then reconstructed by at most 100 conjugate-gradient iterations to a relative tolerance of 1e-3 | S13 tonemap.cpp L299–360, photo.hpp L421–445 | no Fattal operator in OpenCV's photo module |
| L52 | `regionfill` interpolates inward from the region's outer boundary by solving the Dirichlet problem for the discrete Laplacian; introduced in R2015a | S16 Algorithms | stencil not documented |
| L53 | `scipy.fft.dstn` and `idstn` support the type-1 transform and invert each other | S18 | — |
| L54 | Part 2 computed the five-point Laplacian on the patch: −860 at the impulse, 375 at (r2, c2), +160 and −160 across the step, and introduced Poisson editing as keeping the Laplacian and discarding the pixels | S19 Worked example; "Keeping the Laplacian instead of the pixels" | published |
| L55 | Part 11's shadowed copy of the patch reads 8, 40 and 51 where the patch reads 40, 200 and 255 | S20 §Local thresholds | built, not published |
| L56 | OpenCV release dates: 4.10.0 on 2024-06-03, 4.11.0 on 2025-01-09, 5.0.0 on 2026-06-06, 4.14.0 on 2026-07-19 | S14 | GitHub releases list |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S1 | Figure 1 (guided-interpolation notation) | The problem / L01 | names Ω, ∂Ω, f*, g, v in one picture | ACM copyright; the author copy grants personal and classroom use only | http://www.irisa.fr/vista/Papers/2003_siggraph_perez.pdf | do not reuse; Figure 1 here draws the same roles on the patch with its numbers |
| F2 | S2 | Figure 3 (1-D scanline: log, derivative, attenuated, reconstructed) | HDR section / L12 | the 1-D pipeline in one strip | ACM copyright | https://www.cs.huji.ac.il/~danix/hdr/hdrc.pdf | do not reuse; Figure 7 works the patch's own step row instead |
| F3 | S4 | Figures 5 and 10 (seamless cloning example; extended guidance field) | Tooling map / L22 | shows the whole-rectangle Fourier solve | CC BY-NC-SA (non-commercial) | https://www.ipol.im/pub/art/2016/163/article_lr.pdf | do not reuse: the non-commercial term is not cleared for this site |

## Open questions

- The in-place mask change (L48) and the `MIXED_CLONE` criterion at a one-pixel spike (L45) are read
  from source, not run. They are owner checks in the manifest. Neither is reported upstream (searched
  2026-10-15).
- The documentation says the `*_WIDE` flags process "a larger source region by considering the entire
  mask area"; the code only moves the rectangle. The post describes the code.
- Saad prints the 2-D V-cycle cost as "≤ 7/3 ηn"; the geometric series over grids that shrink by four
  gives 4/3. The post derives 4/3 itself and does not quote the constant.
- Fattal's factor at zero central difference is left undefined by the paper; L37 states the formula's
  limit and one implementation's floor, not what every implementation does.
