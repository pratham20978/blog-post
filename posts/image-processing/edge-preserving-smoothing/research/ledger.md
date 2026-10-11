# Source ledger — edge-preserving-smoothing

Series `image-processing`, part 7. Sweep run 2026-10-11. Tier L3, so the floor is 7
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

How each source was read is stated per row. Read in full: Tomasi & Manduchi 1998 (the authors'
UCSC copy), Perona & Malik 1990 (Malik's Berkeley copy, a scan read as page images), Buades, Coll
& Morel's IPOL article (open, CC BY-NC-SA), Durand & Dorsey 2002 and Paris, Kornprobst, Tumblin &
Durand 2009 (MIT author copies), Milanfar 2013 (UCSC author copy), Black, Sapiro, Marimont & Heeger
1998 (NYU Heeger lab copy; equations read from page images), Elad 2002 (Technion author copy),
Salmon & Strozecki 2012 (author copy), Weickert's 1998 monograph (author copy). Used **only for
what their abstracts state** (OpenAlex record, venue and pages cross-checked against Crossref):
Buades, Coll & Morel CVPR 2005 and MMS 2005 (HAL served a bot wall), Catté et al. 1992,
Kichenassamy 1997, You et al. 1996 (the Georgia Tech repository returned a JavaScript shell),
Barash 2002, Garnett et al. 2005, Buades, Coll & Morel 2006, Xiong & Yin 2012.

Library behaviour was read at pinned commits: OpenCV `802cf95aa3d4` (2026-10-10), opencv_contrib
`6484ab27bd33` (2026-09-30), scikit-image `b700edc8005e` (2026-10-09, the commit Parts 5–6 pinned;
releases v0.21.0 and v0.25.2 compared for one function), ITK `dfef08165416` (2026-10-08) and MedPy
`d6abf41066cc` (2024-07-23). Nothing was executed against an image. The only code run was plain
Python (`math` only) reproducing the post's hand-worked numbers: the bilateral filter, the median,
NL-means under both self-weight rules and the Perona–Malik scheme on the shared patch, the
robust-estimator iteration at the impulse, and a replay of scikit-image's lookup-table index
arithmetic (integers and `math.hypot` only; the library itself was not run).

**Finding about Part 1 (published):** its reference 18, "Perona & Malik 1990 [PDF]", links
`https://www.math.uci.edu/~gpatrick/source/papers/G131.pdf`. That file is P. Guidotti's survey
*Anisotropic Diffusions of Image Processing From Perona-Malik on* (S19 here), not the 1990 paper.
The 1990 paper is at Malik's Berkeley page (S02). Reported to the owner; Part 1 not edited.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Tomasi & Manduchi, "Bilateral Filtering for Gray and Color Images" | Proc. ICCV 1998, pp. 839–846 | 1998 | 10.1109/ICCV.1998.710815 | peer-reviewed | https://users.soe.ucsc.edu/~manduchi/Papers/ICCV98.pdf | 2026-10-11 |
| S02 | T1 | Perona & Malik, "Scale-Space and Edge Detection Using Anisotropic Diffusion" | IEEE TPAMI 12(7), pp. 629–639 | 1990 | 10.1109/34.56205 | peer-reviewed | https://people.eecs.berkeley.edu/~malik/papers/MP-aniso.pdf | 2026-10-11 |
| S03 | T1 | Buades, Coll & Morel, "Non-Local Means Denoising" | Image Processing On Line 1, pp. 208–212 | 2011 | 10.5201/ipol.2011.bcm_nlm | peer-reviewed | https://www.ipol.im/pub/art/2011/bcm_nlm/article.pdf | 2026-10-11 |
| S04 | T1 | Buades, Coll & Morel, "A Non-Local Algorithm for Image Denoising" (abstract only) | Proc. CVPR 2005, vol. 2, pp. 60–65 | 2005 | 10.1109/CVPR.2005.38 | peer-reviewed | https://doi.org/10.1109/CVPR.2005.38 | 2026-10-11 |
| S05 | T1 | Buades, Coll & Morel, "A Review of Image Denoising Algorithms, with a New One" (abstract only) | Multiscale Model. Simul. 4(2), pp. 490–530 | 2005 | 10.1137/040616024 | peer-reviewed | https://doi.org/10.1137/040616024 | 2026-10-11 |
| S06 | T1 | Durand & Dorsey, "Fast Bilateral Filtering for the Display of High-Dynamic-Range Images" | ACM TOG 21(3), pp. 257–266 (SIGGRAPH 2002) | 2002 | 10.1145/566654.566574 | peer-reviewed | https://people.csail.mit.edu/fredo/PUBLI/Siggraph2002/DurandBilateral.pdf | 2026-10-11 |
| S07 | T1 | Paris, Kornprobst, Tumblin & Durand, "Bilateral Filtering: Theory and Applications" (survey) | Found. Trends Comput. Graph. Vis. 4(1), pp. 1–73 | 2009 | 10.1561/0600000020 | peer-reviewed | https://people.csail.mit.edu/sparis/publi/2009/fntcgv/Paris_09_Bilateral_filtering.pdf | 2026-10-11 |
| S08 | T1 | Milanfar, "A Tour of Modern Image Filtering" (survey) | IEEE Signal Processing Magazine 30(1), pp. 106–128 | 2013 | 10.1109/MSP.2011.2179329 | peer-reviewed | https://users.soe.ucsc.edu/~milanfar/publications/journal/ModernTour.pdf | 2026-10-11 |
| S09 | T1 | Black, Sapiro, Marimont & Heeger, "Robust Anisotropic Diffusion" | IEEE TIP 7(3), pp. 421–432 | 1998 | 10.1109/83.661192 | peer-reviewed | https://www.cns.nyu.edu/heegerlab/content/software/robanistdif/Black-IEEE-IP98.pdf | 2026-10-11 |
| S10 | T1 | Weickert, *Anisotropic Diffusion in Image Processing* (monograph) | B. G. Teubner, Stuttgart | 1998 | ISBN 3-519-02606-6 | standard | https://www.mia.uni-saarland.de/weickert/Papers/book.pdf | 2026-10-11 |
| S11 | T1 | Catté, Lions, Morel & Coll, "Image Selective Smoothing and Edge Detection by Nonlinear Diffusion" (abstract only) | SIAM J. Numer. Anal. 29(1), pp. 182–193 | 1992 | 10.1137/0729012 | peer-reviewed | https://doi.org/10.1137/0729012 | 2026-10-11 |
| S12 | T1 | Kichenassamy, "The Perona–Malik Paradox" (abstract only) | SIAM J. Appl. Math. 57(5), pp. 1328–1342 | 1997 | 10.1137/S003613999529558X | peer-reviewed | https://doi.org/10.1137/S003613999529558X | 2026-10-11 |
| S13 | T1 | You, Xu, Tannenbaum & Kaveh, "Behavioral Analysis of Anisotropic Diffusion in Image Processing" (abstract only) | IEEE TIP 5(11), pp. 1539–1553 | 1996 | 10.1109/83.541424 | peer-reviewed | https://doi.org/10.1109/83.541424 | 2026-10-11 |
| S14 | T1 | Elad, "On the Origin of the Bilateral Filter and Ways to Improve It" | IEEE TIP 11(10), pp. 1141–1151 | 2002 | 10.1109/TIP.2002.801126 | peer-reviewed | https://elad.cs.technion.ac.il/wp-content/uploads/2018/02/08_Bilateral_Filter_IP.pdf | 2026-10-11 |
| S15 | T1 | Barash, "Fundamental Relationship Between Bilateral Filtering, Adaptive Smoothing, and the Nonlinear Diffusion Equation" (abstract only) | IEEE TPAMI 24(6), pp. 844–847 | 2002 | 10.1109/TPAMI.2002.1008390 | peer-reviewed | https://doi.org/10.1109/TPAMI.2002.1008390 | 2026-10-11 |
| S16 | T1 | Garnett, Huegerich, Chui & He, "A Universal Noise Removal Algorithm with an Impulse Detector" (abstract only) | IEEE TIP 14(11), pp. 1747–1754 | 2005 | 10.1109/TIP.2005.857261 | peer-reviewed | https://doi.org/10.1109/TIP.2005.857261 | 2026-10-11 |
| S17 | T1 | Buades, Coll & Morel, "The Staircasing Effect in Neighborhood Filters and Its Solution" (abstract only) | IEEE TIP 15(6), pp. 1499–1505 | 2006 | 10.1109/TIP.2006.871137 | peer-reviewed | https://doi.org/10.1109/TIP.2006.871137 | 2026-10-11 |
| S18 | T1 | Salmon & Strozecki, "Patch Reprojections for Non-Local Methods" | Signal Processing 92(2), pp. 477–489 | 2012 | 10.1016/j.sigpro.2011.08.011 | peer-reviewed | https://josephsalmon.eu/papers/NLM_Reprojections_Salmon_Strozecki.pdf | 2026-10-11 |
| S19 | T1 | Guidotti, "Anisotropic Diffusions of Image Processing From Perona-Malik on" (survey; used to map the theory, not cited in the post) | Adv. Stud. Pure Math. 67, pp. 131–156 | 2015 | 10.2969/aspm/06710131 | peer-reviewed | https://www.math.uci.edu/~gpatrick/source/papers/G131.pdf | 2026-10-11 |
| S20 | T1 | Xiong & Yin, "A Universal Denoising Framework With a New Impulse Detector and Nonlocal Means" (abstract only) | IEEE TIP 21(4), pp. 1663–1675 | 2012 | 10.1109/TIP.2011.2172804 | peer-reviewed | https://doi.org/10.1109/TIP.2011.2172804 | 2026-10-11 |
| S21 | T3 | OpenCV source at commit 802cf95: `modules/imgproc/include/opencv2/imgproc.hpp`, `modules/imgproc/src/bilateral_filter.dispatch.cpp` and `.simd.hpp`, `modules/photo/include/opencv2/photo.hpp`, `modules/photo/src/fast_nlmeans_denoising_invoker.hpp` and `_commons.hpp` | — | 2026 | — | source | https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760 | 2026-10-11 |
| S22 | T3 | opencv_contrib source at commit 6484ab2: `modules/ximgproc/include/opencv2/ximgproc.hpp`, `modules/ximgproc/src/anisodiff.cpp` | — | 2026 | — | source | https://github.com/opencv/opencv_contrib/tree/6484ab27bd332762f36262bf3b3f743720f4ca1b/modules/ximgproc | 2026-10-11 |
| S23 | T3 | scikit-image source at commit b700edc: `src/_skimage2/restoration/_denoise.py`, `_denoise_cy.pyx`, `non_local_means.py`, `_nl_means_denoising.pyx`; `tests/skimage/restoration/test_denoise.py`; `skimage/restoration/_denoise.py` and `_denoise_cy.pyx` at tags v0.21.0 and v0.25.2 | — | 2026 | — | source | https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/restoration | 2026-10-11 |
| S24 | T3 | ITK source at commit dfef081: `Modules/Filtering/AnisotropicSmoothing/include/itkAnisotropicDiffusionImageFilter.h`, `.hxx`, `itkGradientAnisotropicDiffusionImageFilter.h`, `itkGradientNDAnisotropicDiffusionFunction.h`, `.hxx` | — | 2026 | — | source | https://github.com/InsightSoftwareConsortium/ITK/tree/dfef081654167268e754645b95f70d87c73b66fc/Modules/Filtering/AnisotropicSmoothing/include | 2026-10-11 |
| S25 | T3 | MedPy source at commit d6abf41: `medpy/filter/smoothing.py` (`anisotropic_diffusion`) | — | 2024 | — | source | https://github.com/loli/medpy/blob/d6abf41066cce75c84215a237a0be208e8294760/medpy/filter/smoothing.py | 2026-10-11 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search:bilateral filtering theory and applications, by citations | the survey: Paris, Kornprobst, Tumblin & Durand, FnT CGV 2009 (589 citations); became S07 |
| 2 | 1 | OpenAlex | title.search:a tour of modern image filtering | Milanfar, IEEE SPM 30(1) (620 citations), the survey that puts bilateral, NL-means and diffusion in one W·y frame; became S08 |
| 3 | 1 | OpenAlex | title.search:review of image denoising algorithms with a new one | Buades, Coll & Morel, MMS 2005 (4,110 citations); became S05 (HAL copy bot-walled, abstract only) |
| 4 | 1 | OpenAlex | title.search:image denoising methods a new nonlocal principle | Buades et al., SIAM Review 2010, the review's update; not needed once IPOL (S03) was read |
| 5 | 1 | OpenAlex | title.search:review of nonlinear diffusion filtering | Weickert 1997 LNCS review (515 citations); his 1998 monograph was read in full instead (S10) |
| 6 | 1 | OpenAlex | title.search:scale-space and edge detection using anisotropic diffusion | Perona & Malik 1990 TPAMI (12,180 citations); became S02 |
| 7 | 1 | OpenAlex | title.search:bilateral filtering for gray and color images | Tomasi & Manduchi ICCV 1998 (8,222 citations); became S01 |
| 8 | 1 | OpenAlex | title.search:a non-local algorithm for image denoising | Buades et al. CVPR 2005 (7,233 citations) became S04; fast-NLM follow-ups (ICIP 2006, 2009) not needed |
| 9 | 1 | OpenAlex | title.search:non-local means denoising | IPOL 2011 article, open access, with the parameter table and the self-weight rule; became S03 |
| 10 | 1 | OpenAlex | title.search:fast bilateral filtering for the display of high-dynamic-range images | Durand & Dorsey 2002, TOG and SIGGRAPH records; became S06 |
| 11 | 1 | OpenAlex | title.search:fast approximation of the bilateral filter using a signal processing approach | Paris & Durand ECCV 2006 / IJCV 2009; MIT DSpace copy served an AWS bot wall, so the grid is cited through the survey S07 §4.5 |
| 12 | 1 | OpenAlex | title.search:robust anisotropic diffusion | Black, Sapiro, Marimont & Heeger 1998 TIP; became S09 |
| 13 | 4 | OpenAlex | title.search:image selective smoothing and edge detection by nonlinear diffusion | Catté, Lions, Morel & Coll 1992 (part I) and its part II; part I became S11, abstract only |
| 14 | 4 | OpenAlex | title.search:the perona-malik paradox | Kichenassamy 1997; became S12, abstract only |
| 15 | 4 | OpenAlex | title.search:on the origin of the bilateral filter and ways to improve it | Elad 2002 TIP; became S14 |
| 16 | 4 | OpenAlex | title.search:fundamental relationship between bilateral filtering adaptive smoothing nonlinear diffusion | Barash 2002 TPAMI; became S15, abstract only |
| 17 | 4 | OpenAlex | title.search:universal noise removal algorithm with an impulse detector | Garnett et al. 2005 TIP (trilateral filter); became S16, abstract only |
| 18 | 4 | OpenAlex | title.search:staircasing effect in neighborhood filters | Buades, Coll & Morel 2006 TIP; became S17, abstract only |
| 19 | 4 | OpenAlex | title.search:behavioral analysis of anisotropic diffusion in image processing | You et al. 1996 TIP; Georgia Tech copy returned a JavaScript shell, so abstract only (S13) |
| 20 | 1 | Web (author pages) | Perona & Malik 1990 PDF | Part 1's link (math.uci.edu G131.pdf) is Guidotti's survey, not the paper (recorded as S19); Malik's Berkeley page hosts the 1990 scan (S02); the JHU course copy 404 |
| 21 | 1 | Google Scholar | robust anisotropic diffusion black sapiro marimont heeger | NYU Heeger-lab PDF of S09 (Brown and MPI copies had 404'd) |
| 22 | 1 | Google Scholar | a review of image denoising algorithms with a new one buades | HAL PDF only; HAL served an Anubis bot wall; logged as blocked |
| 23 | 1 | Google Scholar | on the origin of the bilateral filter and ways to improve it elad | Technion author PDF; became the URL for S14 |
| 24 | 1 | OpenAlex | forward chase: cites:W2099244020 (Tomasi & Manduchi), title.search:impulse | 51 works: Garnett 2005 (S16), Xiong & Yin 2012 (S20), a 2018 impulse-and-Gaussian survey; all add an impulse detector, none removes impulses with the plain bilateral |
| 25 | 1 | OpenAlex | forward chase: cites:W2097073572 (Buades CVPR), abstract.search:rare patch | 6 works, all applications; the term traced instead to Salmon & Strozecki (S18) |
| 26 | 1 | Google Scholar | "rare patch effect" non-local means | Salmon & Strozecki, Patch Reprojections (author copy, became S18); Deledalle, Duval & Salmon on shape-adaptive patches (not needed) |
| 27 | 1 | OpenAlex | forward chase: cites:W2150134853 (Perona & Malik), title.search:staircasing | Buades et al. 2006 (S17) and gradient-fidelity variants; nothing contradicts the staircasing account in S10 |
| 28 | 1 | OpenAlex | forward chase: cites:W2099244020, title.search:constant time | Porikli 2008 "Constant time O(1) bilateral filtering" and successors; the post cites the survey's complexity table (S07) instead |
| 29 | 1 | Semantic Scholar | citations of DOI 10.1109/CVPR.2005.38 | answered this session (no 429); returned recent applications only, nothing new for the post |
| 30 | 1 | arXiv | ti:bilateral AND ti:filter; all:"non-local means" AND all:impulse | Fourier/shiftable fast bilateral (Chaudhury et al. 2016–2018), Hu et al. 2014 patch-based weighted means for impulse noise; preprints, not cited |
| 31 | 1 | OpenAlex | title.search:anisotropic diffusions of image processing from perona-malik on | Guidotti, Adv. Stud. Pure Math. 67 (S19); a survey of the ill-posedness results, used to map the field |
| 32 | 1 | Crossref | DOI checks: 10.1109/ICCV.1998.710815, 10.1109/34.56205, 10.5201/ipol.2011.bcm_nlm, 10.1145/566654.566574, 10.1561/0600000020, 10.1109/MSP.2011.2179329, 10.1109/83.661192, 10.1016/j.sigpro.2011.08.011, 10.2969/aspm/06710131, 10.1109/TIP.2002.801126 | venues, volumes, issues and pages confirmed |
| 33 | 5 | GitHub | OpenCV, opencv_contrib, scikit-image, ITK, MedPy at the head commits named above | the window shape, colour distance and defaults of `bilateralFilter`; the weight rule and self-weight of `fastNlMeansDenoising`; `anisotropicDiffusion`'s type, conductance and neighbours; scikit-image's LUTs, defaults and cut-offs; ITK's time step and conductance scaling; MedPy's options |
| 34 | 4 | GitHub issues | repo:scikit-image "_compute_spatial_lut"; "denoise_bilateral spatial"; "bilateral win_size arange"; "denoise_bilateral wrong weights" | no issue reports the lookup-table size mismatch; open PR #8210 copies the same `arange` expression into a 3-D version |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | The bilateral filter averages nearby values weighted by geometric closeness times photometric similarity, normalised by the sum of those weights; it is non-iterative and local; range filtering alone only remaps the grey levels | S01 abstract, §2 eqs. 5–6, §3 | — |
| L02 | In the Gaussian case both closeness and similarity are Gaussians of distance; values much closer than σ_r are mixed and values much farther apart are not | S01 §2.1 | scalar case uses the absolute difference |
| L03 | Tomasi and Manduchi's own examples use σ_r = 50 grey levels, with σ_d = 5 on a 100-level step with noise σ = 10 and σ_d = 3 on a photograph | S01 Fig. 1, §4 | — |
| L04 | Thin bright whiskers stay crisp under the bilateral filter because the range term ignores the whisker's pixels when centred off it, and the dark pixels when centred on it | S01 §4 | — |
| L05 | The idea goes back to Aurich and Weule (1995) and Smith and Brady's SUSAN; Tomasi and Manduchi named it; it has two parameters, the size and the contrast of the features to keep | S07 ch. 1 | — |
| L06 | For salt-and-pepper or impulse noise the bilateral filter may need the input mollified first, because the bad pixels are too different from their neighbours to be filtered; one fix computes the range weights on a median-filtered copy | S07 §3.1.4, eq. 6 | — |
| L07 | For denoising, σ_s is usually small and σ_r is chosen to match the noise level | S07 §3.1.4 | — |
| L08 | The bilateral filter is a W-estimator (one step of iteratively reweighted least squares); because the robust energy has local minima, initialising with a median is recommended | S06 §4 | — |
| L09 | The bilateral filter is a single iteration of the Jacobi (diagonal-normalised steepest descent) algorithm on a Bayesian penalty | S14 abstract, §I | — |
| L10 | Barash relates bilateral filtering, adaptive smoothing and the nonlinear diffusion equation in one viewpoint | S15 abstract | abstract only |
| L11 | Durand and Dorsey linearise the bilateral filter by computing it at NB_SEGMENTS intensity levels, about (max − min)/σ_r, each a linear convolution done by FFT, then interpolating; with downsampling up to factors of 10 to 25 they saw no visible artefact and report a speed-up of two orders of magnitude; full-scale filtering of a 576×768 image took 173 s on their machine | S06 abstract, §5.1, §5.2, Fig. 10, Fig. 13 | 2002 hardware (700 MHz Pentium III quoted elsewhere in the paper) |
| L12 | The bilateral grid stores (w·I, w) in a 3-D grid over position and intensity, convolves it with a 3-D Gaussian of widths (σ_s, σ_s, σ_r), and reads the result at (p, I(p)) after dividing; this is exact, and because the result is band-limited the grid can be downsampled | S07 §4.5, eq. 17 | — |
| L13 | Complexities: brute force O(N²); window cut at 2σ_s O(N·σ_s²); separable approximation O(N·σ_s); local histograms O(N log σ_s); layered approximation and grid O(N + N·R/(σ_s²·σ_r)), R the intensity range | S07 §4.1, Table 4.4 | N = number of pixels |
| L14 | Neighbourhood filters, the bilateral among them, create flat regions separated by artefact boundaries (staircasing); their underlying PDE is an ill-posed variant of Perona–Malik; NL-means had the same effect; a regression variant fixes it | S17 abstract | abstract only |
| L15 | Garnett et al. add a statistic of how different a pixel is from its most similar neighbours to a Gaussian-noise filter, so it removes impulse noise too | S16 abstract | abstract only |
| L16 | NL-means replaces a pixel with an average of pixels whose surrounding windows resemble its own; the most similar pixels need not be close, so a large window is searched; the authors call it semi-local | S03 §1 | — |
| L17 | IPOL's NL-means weight is exp(−max(d² − 2σ², 0)/h²), with d² the mean squared difference over the (2f+1)² patch; the search window is 21×21 for small and moderate σ and 35×35 for large σ | S03 §2 | pixelwise implementation |
| L18 | In IPOL's algorithm the reference pixel's weight is set to the maximum weight of the others, to avoid over-weighting it; otherwise it would be 1 and a larger h would be needed | S03 §2 | — |
| L19 | IPOL parameter table for grey images: σ up to 15 uses 3×3 patches, a 21×21 window and h = 0.40σ; σ 15–30: 5×5, 21×21, 0.40σ; 30–45: 7×7, 35×35, 0.35σ; 45–75: 9×9, 35×35, 0.35σ; 75–100: 11×11, 35×35, 0.30σ | S03 Table 1 | patchwise implementation |
| L20 | NL-means was introduced with the method noise (image minus its denoised version) as an evaluation tool, and is asymptotically optimal under a generic statistical image model | S04, S05 abstracts | abstracts only |
| L21 | The central patch's weight is always the kernel at zero distance, so it is overestimated; Buades et al.'s seminal paper set it to the maximum of the other weights; where few patches are similar (edges, corners) NL-means suffers the rare patch effect, with similar patches growing linearly with the search radius along an edge and quadratically in flat regions | S18 §2, §3.1 | — |
| L22 | NL-means has been extended to impulse noise by adding an impulse detector and a reference image | S20 abstract | abstract only |
| L23 | In practice the NL-means search is limited, so it is more or less local; cutting weights to zero beyond some distance is the only distinction between local and non-local methods | S08 pp. 108–110 | — |
| L24 | Perona and Malik let the diffusion coefficient vary in space so that smoothing happens within regions in preference to across them: I_t = div(c ∇I), with c = g(‖∇I‖), g non-negative, decreasing and g(0) = 1 | S02 abstract, §III, eqs. 3–4 | — |
| L25 | Their discrete scheme updates each pixel by λ times the sum over its four neighbours of conductance times difference, with 0 ≤ λ ≤ 1/4 for stability; each arc's conductance is g of the absolute difference across that arc; the boundary is adiabatic (zero conductance at the image border) | S02 §V, eqs. 7, 8, 10 | — |
| L26 | For λ in [0, 1/4] and conductances in [0, 1] each new value lies between the smallest and largest of the pixel and its four neighbours at the previous iteration (eq. 11), so no extremum appears in the interior of the discretised scale space | S02 eqs. 11–13 | spatially, new local extrema can still form (one iteration on a 20-level bump makes a ring); the bound is on each pixel's range |
| L27 | Perona and Malik used g = exp(−(‖∇I‖/K)²), which privileges high-contrast edges, and g = 1/(1 + (‖∇I‖/K)²), which privileges wide regions over small ones | S02 §V | — |
| L28 | K was fixed by hand, or set at every iteration to the 90% point of the histogram of absolute gradient values (Canny's noise estimator) | S02 §V | — |
| L29 | The flux φ = g·I_x rises then falls; where φ' < 0 the edge sharpens (backward diffusion); in practice such regions shrink quickly and the process stays stable | S02 §IV-B, Fig. 6 | — |
| L30 | With constant conductance the scheme is Gaussian blurring; the scheme preserves the total brightness | S02 §V | — |
| L31 | In Perona and Malik's scale space edges remain sharp until they disappear | S02 Fig. 11 | — |
| L32 | The Perona–Malik equation is formally ill-posed and has no weak solutions even where computations succeed, yet simple discretisations are numerically stable | S12 abstract | abstract only |
| L33 | Catté et al.'s version is stable in the presence of noise, with existence and uniqueness; it evaluates the diffusivity on the gradient of a Gaussian-smoothed image | S11 abstract; S10 §1.3.2 | — |
| L34 | In Weickert's terminology diffusion is isotropic when the flux is parallel to the gradient (a scalar diffusivity) and anisotropic when a diffusion tensor makes them differ; Perona–Malik is isotropic in that sense; computer-vision usage calls inhomogeneous blurring anisotropic | S10 §1.1, §1.3.1 | — |
| L35 | Staircasing (a sigmoid edge turning into flat segments separated by jumps) is the main observable instability; a standard finite-difference discretisation makes Perona–Malik a well-posed ODE system whose solution obeys a maximum–minimum principle and converges to a constant steady state | S10 §1.3.1 | — |
| L36 | Anisotropic diffusion is the steepest descent of an energy; its ill-posedness corresponds to infinitely many global minima dense in image space | S13 abstract | abstract only |
| L37 | Anisotropic diffusion is gradient descent on a robust error norm with g(x) = ρ'(x)/x; Perona–Malik's rational g is the Lorentzian norm with K² = 2σ²; Tukey's biweight gives zero influence to large differences, so on a piecewise-constant image whose jumps all exceed the threshold it changes nothing, unlike the other two norms | S09 §III–IV, eqs. 6–17 | — |
| L38 | The robust scale is σ_e = 1.4826·MAD of the gradient, 1.4826 being 1/0.6745 for a unit normal; outlier rejection begins at σ_e = √2·σ for the Lorentzian and σ/√5 for Tukey | S09 eq. 21, §IV | — |
| L39 | Perona–Malik's exponential edge-stopping function has the same form as the bilateral filter's Gaussian range weight, so results about edge-stopping functions carry over; diffusion is energy-preserving while the bilateral filter is not, because its normalisation differs from pixel to pixel | S06 §3.1 eq. 2, §4 | — |
| L40 | All these filters compute each output as a weighted sum of the inputs with weights summing to one; W is a positive row-stochastic matrix with real non-negative eigenvalues and largest eigenvalue 1; the estimator is non-linear because the weights depend on the data | S08 eqs. 10–11, pp. 111–113 | — |
| L41 | OpenCV documents bilateralFilter as very slow compared with most filters; sigmas under 10 have little effect and over 150 look cartoonish; d over 5 is very slow, d = 5 is recommended for real time and d = 9 offline; it does not work in place; 8-bit or float, 1 or 3 channels | S21 imgproc.hpp | commit 802cf95 |
| L42 | OpenCV's bilateralFilter sets radius = round(1.5·sigmaSpace) when d ≤ 0 and d/2 otherwise, and keeps only offsets with sqrt(i² + j²) ≤ radius, a disc; 8-bit range weights come from a table exp(−k²/(2σ_c²)) of integer differences; for 3 channels the difference is the sum of the absolute channel differences; borders use BORDER_DEFAULT (reflect-101) | S21 bilateral_filter.dispatch.cpp, bilateral_filter.simd.hpp | commit 802cf95 |
| L43 | OpenCV's fastNlMeansDenoising defaults are h = 3, templateWindowSize = 7, searchWindowSize = 21; it expects Gaussian white noise; a big h removes noise and detail; the coloured variant converts to CIELAB and filters L and AB with different h | S21 photo.hpp | commit 802cf95 |
| L44 | OpenCV's NL-means weight is exp(−d/(h²·channels)) with d the per-pixel mean squared patch difference (approximated by a bit shift), weights under 0.001 are set to 0, and the averaging loop includes the zero offset, so the pixel's own patch gets weight 1; borders use BORDER_DEFAULT | S21 fast_nlmeans_denoising_invoker.hpp, _commons.hpp | commit 802cf95; NORM_L2 |
| L45 | opencv_contrib's anisotropicDiffusion asserts an 8-bit 3-channel image, K ≠ 0 and alpha > 0; its conductance is exp(−(n/(3·255·K))²) with n the sum of absolute channel differences, summed over 8 neighbours with replicated borders; only the exponential function is implemented; the docs call alpha normally between 0 and 1 | S22 ximgproc.hpp, anisodiff.cpp | commit 6484ab2 |
| L46 | scikit-image's denoise_bilateral defaults: win_size = max(5, 2·ceil(3·sigma_spatial) + 1), sigma_color = the image's standard deviation, sigma_spatial = 1, bins = 10000, mode = 'constant' with cval = 0; integer images are converted to floats in 0–1, so sigma_color is in those units; the window loop is square | S23 _denoise.py, _denoise_cy.pyx | commit b700edc |
| L47 | scikit-image builds the spatial lookup table on np.arange(−win_size // 2, win_size // 2 + 1), which has win_size + 1 points for odd win_size, and the Cython loop reads it at kr·win_size + kc; the same lines are in releases v0.21.0 and v0.25.2; the tests check smoothing and constants, not positions | S23 _denoise.py `_compute_spatial_lut`, _denoise_cy.pyx; tags v0.21.0, v0.25.2; test_denoise.py | read, not run |
| L48 | scikit-image's denoise_nl_means defaults: patch_size 7, patch_distance 11, h = 0.1, fast_mode True, sigma 0; slow-mode cost image.size × patch_size^ndim × patch_distance^ndim, fast mode image.size × patch_distance^ndim with uniform patch weights (Darbon et al.); reflect padding; with sigma given, h ≈ 0.8σ (fast) or 0.6σ (slow) is suggested | S23 non_local_means.py | commit b700edc |
| L49 | scikit-image's NL-means includes the zero offset, so the pixel's own patch gets weight exp(0) = 1 in both modes, and skips weights once the scaled distance exceeds 5 | S23 _nl_means_denoising.pyx | commit b700edc |
| L50 | ITK's GradientAnisotropicDiffusion is the classic Perona–Malik scheme with the exponential conductance, scaled by the average squared gradient magnitude (K = 2·k²·mean squared gradient); its default time step is 0.5/2^N and it warns above spacing/2^(N+1), 0.125 in 2-D | S24 | commit dfef081 |
| L51 | MedPy's anisotropic_diffusion defaults to niter 1, kappa 50 grey levels, gamma 0.1 (≤ 0.25 for stability) and option 1 (exponential); option 2 is the rational function, option 3 Tukey's biweight | S25 | commit d6abf41 |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S01 | Fig. 1 (similarity weights beside a noisy step) | Worked example / L01 | shows the range weights switching off across a step | IEEE copyright, no licence found | https://doi.org/10.1109/ICCV.1998.710815 | do not reuse; Figure 1 computes the weights on the patch instead |
| F2 | S02 | Fig. 6 (flux φ with a peak at K) | Perona–Malik / L29 | the flux that falls past K | IEEE copyright, no licence found | https://doi.org/10.1109/34.56205 | do not reuse; Figure 8 plots the flux of both conductances with the patch's differences marked |
| F3 | S07 | Fig. 4.1 (the bilateral grid) | Bilateral / L12 | the lift into space × intensity | Now Publishers copyright, no licence found | https://doi.org/10.1561/0600000020 | do not reuse; Figure 6 lifts the patch's own row |
| F4 | S03 | Fig. 1 (NL-means on a photograph) | NL-means / L16 | a real-image result | CC BY-NC-SA (article and image credit) | https://doi.org/10.5201/ipol.2011.bcm_nlm | do not reuse: non-commercial terms and not necessary for a by-hand post |
| F5 | S09 | Fig. 7 (ψ functions aligned) | Perona–Malik / L37 | the influence functions | IEEE copyright, no licence found | https://doi.org/10.1109/83.661192 | do not reuse; described in prose |

## Open questions

- **scikit-image's bilateral lookup table** (L47) was read, not run. Replaying the index arithmetic
  in plain Python says the loop reads each spatial weight from a shifted offset (largest weight at
  (2, −1) for win_size 5, at (2, −2) for the default 7). No issue reports it. The post states it as
  a reading of the source with a check the reader can run; the owner should confirm with one call
  before publishing, and may wish to report it upstream.
- OpenCV's NL-means distance uses a bit-shift approximation of the mean (dividing by the next power
  of two, then a table correction). The post quotes the threshold arithmetic for its defaults
  ("about 55 grey levels") as approximate for that reason.
- Guidotti's survey (S19) carries "Advanced Studies in Pure Mathematics 99, 20XX" in the PDF and
  2019 in OpenAlex; the year 2015 is that of volume 67. It is not cited in the post.
- Paris & Durand's IJCV paper could not be read (MIT DSpace bot wall); the grid is cited through
  the survey (S07), which three of the same authors wrote.
