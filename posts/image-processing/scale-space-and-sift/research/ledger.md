# Source ledger — scale-space-and-sift

Series `image-processing`, part 10. Sweep run 2026-10-13. Tier L4, so the floor is 10 peer-reviewed
or standard sources carrying an identifier, across 4 scholarly databases.

How each source was read is stated per row. Read in full: Lowe 2004 and Lowe 1999 (Lowe's UBC
copies), Brown & Lowe 2002 (BMVA archive), Witkin 1983 (IJCAI proceedings PDF), Lindeberg 1998
"Feature detection" and Lindeberg 1998 "Edge and ridge detection" (the KTH technical-report versions,
ISRN KTH/NA/P--96/18--SE and --96/06--SE, on Lindeberg's KTH page; KTH's DiVA repository did not
answer), Lindeberg 2013 (PLoS ONE, via arXiv 1210.0754), Lindeberg 2024 (via arXiv 2311.11317),
Lindeberg 2012 (Scholarpedia, revision 153939), Felsberg & Sommer (the 2002 Kiel technical report,
Bericht Nr. 0208, which became the 2004 JMIV paper), Didas et al. 2005 (Saarland copy), Mikolajczyk &
Schmid 2004 (Oxford VGG copy), Rey-Otero & Delbracio 2014 (IPOL, open), Rey-Otero, Morel & Delbracio
(arXiv 1511.08478v1, which became the 2016 JMIV paper), Bay et al. 2008 (KU Leuven copy). Used **only
for what their abstracts state** (OpenAlex record; venue and pages checked against Crossref): Babaud et
al. 1986, Yuille & Poggio 1986, Lindeberg 1990, Pauwels et al. 1995, Kannappan & Sahoo 1992,
Mikolajczyk & Schmid 2001, Kuijper 2002 (thesis). **Not read** (no open copy; abstracts withheld by
Springer): Koenderink 1984 and Weickert, Ishikawa & Imiya 1999 — cited only for what the sources that
were read say about them, and the condition column says so.

Library behaviour was read at pinned commits: OpenCV `802cf95aa3d4` (the commit Parts 5–9 pinned):
`modules/features2d/src/sift.dispatch.cpp`, `sift.simd.hpp`,
`modules/features2d/include/opencv2/features2d.hpp`, `modules/imgproc/src/smooth.dispatch.cpp`,
`modules/imgproc/src/resize.cpp`; OpenCV tag `4.10.0` for the same SIFT files (they differ only in
comments and buffer types), and `features2d.hpp` at tags 4.3.0, 4.4.0, 4.7.0 and 4.8.0; OpenCV issue
#23123 and pull requests #23124 and #23270 through the GitHub API. scikit-image `b700edc8005e` (the
commit Parts 5–9 pinned): `src/_skimage2/feature/sift.py`, `feature/blob.py`, `transform/_warps.py`.
SciPy's `ndimage.zoom` page (v1.18.0) and MathWorks' `detectSIFTFeatures` and `SIFTPoints` pages
(R2026b). Nothing was executed against an image. The only code run was plain Python (`math` only):
the closed-form scale space of the enlarged patch, one DoG octave, the 26-neighbour test, the
quadratic fit and both rejection tests; a discrete pyramid (sampled kernels, replicate and reflect-101
borders, direct and incremental blurs) as a cross-check; a replay of OpenCV's SIFT detection rules
transcribed from the files above; the normalised-Laplacian and DoG curves; and the scale-adapted
Harris measure for the Harris–Laplace check.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Lowe, "Distinctive Image Features from Scale-Invariant Keypoints" | International Journal of Computer Vision 60(2), pp. 91–110 | 2004 | 10.1023/B:VISI.0000029664.99615.94 | peer-reviewed | https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf | 2026-10-13 |
| S02 | T1 | Lowe, "Object Recognition from Local Scale-Invariant Features" | Proc. IEEE ICCV 1999, vol. 2, pp. 1150–1157 | 1999 | 10.1109/ICCV.1999.790410 | peer-reviewed | https://www.cs.ubc.ca/~lowe/papers/iccv99.pdf | 2026-10-13 |
| S03 | T1 | Brown & Lowe, "Invariant Features from Interest Point Groups" | Proc. BMVC 2002, pp. 23.1–23.10 | 2002 | 10.5244/C.16.23 | peer-reviewed | https://www.bmva-archive.org.uk/bmvc/2002/papers/92/full_92.pdf | 2026-10-13 |
| S04 | T1 | Witkin, "Scale-Space Filtering" | Proc. 8th IJCAI, Karlsruhe, pp. 1019–1022 (reprinted in Readings in Computer Vision, 1987) | 1983 | reprint 10.1016/B978-0-08-051581-6.50036-2 | peer-reviewed | https://www.ijcai.org/Proceedings/83-2/Papers/091.pdf | 2026-10-13 |
| S05 | T1 | Koenderink, "The Structure of Images" (not read; no open copy) | Biological Cybernetics 50(5), pp. 363–370 | 1984 | 10.1007/BF00336961 | peer-reviewed | https://doi.org/10.1007/BF00336961 | 2026-10-13 |
| S06 | T1 | Babaud, Witkin, Baudin & Duda, "Uniqueness of the Gaussian Kernel for Scale-Space Filtering" (abstract only) | IEEE TPAMI 8(1), pp. 26–33 | 1986 | 10.1109/TPAMI.1986.4767749 | peer-reviewed | https://doi.org/10.1109/TPAMI.1986.4767749 | 2026-10-13 |
| S07 | T1 | Yuille & Poggio, "Scaling Theorems for Zero Crossings" (abstract only) | IEEE TPAMI 8(1), pp. 15–25 | 1986 | 10.1109/TPAMI.1986.4767748 | peer-reviewed | https://doi.org/10.1109/TPAMI.1986.4767748 | 2026-10-13 |
| S08 | T1 | Lindeberg, "Scale-Space for Discrete Signals" (abstract only) | IEEE TPAMI 12(3), pp. 234–254 | 1990 | 10.1109/34.49051 | peer-reviewed | https://doi.org/10.1109/34.49051 | 2026-10-13 |
| S09 | T1 | Lindeberg, "Feature Detection with Automatic Scale Selection" | International Journal of Computer Vision 30(2), pp. 79–116 | 1998 | 10.1023/A:1008045108935 | peer-reviewed | https://people.kth.se/~tony/papers/cvap198.pdf | 2026-10-13 |
| S10 | T1 | Lindeberg, "Edge Detection and Ridge Detection with Automatic Scale Selection" | International Journal of Computer Vision 30(2), pp. 117–156 | 1998 | 10.1023/A:1008097225773 | peer-reviewed | https://people.kth.se/~tony/papers/cvap191.pdf | 2026-10-13 |
| S11 | T1 | Lindeberg, "Invariance of Visual Operations at the Level of Receptive Fields" | PLoS ONE 8(7), e66990 | 2013 | 10.1371/journal.pone.0066990 | peer-reviewed | https://doi.org/10.1371/journal.pone.0066990 | 2026-10-13 |
| S12 | T1 | Lindeberg, "Discrete Approximations of Gaussian Smoothing and Gaussian Derivatives" | Journal of Mathematical Imaging and Vision 66(5), pp. 759–800 | 2024 | 10.1007/s10851-024-01196-9 | peer-reviewed | https://arxiv.org/abs/2311.11317 | 2026-10-13 |
| S13 | T1 | Lindeberg, "Scale Invariant Feature Transform" (Scholarpedia article, two named reviewers, revision 153939) | Scholarpedia 7(5), 10491 | 2012 | 10.4249/scholarpedia.10491 | peer-reviewed | http://www.scholarpedia.org/article/Scale_Invariant_Feature_Transform | 2026-10-13 |
| S14 | T1 | Pauwels, Van Gool, Fiddelaers & Moons, "An Extended Class of Scale-Invariant and Recursive Scale Space Filters" (abstract only) | IEEE TPAMI 17(7), pp. 691–701 | 1995 | 10.1109/34.391411 | peer-reviewed | https://doi.org/10.1109/34.391411 | 2026-10-13 |
| S15 | T1 | Felsberg & Sommer, "The Monogenic Scale-Space: A Unifying Approach to Phase-Based Image Processing in Scale-Space" (read as the 2002 Kiel report "The Poisson Scale-Space", Bericht Nr. 0208) | Journal of Mathematical Imaging and Vision 21(1–2), pp. 5–26 | 2004 | 10.1023/B:JMIV.0000026554.79537.35 | peer-reviewed | https://macau.uni-kiel.de/servlets/MCRFileNodeServlet/macau_derivate_00002910/2002_tr08.pdf | 2026-10-13 |
| S16 | T1 | Didas, Burgeth, Imiya & Weickert, "Regularity and Scale-Space Properties of Fractional High Order Linear Filtering" | Scale-Space 2005, LNCS 3459, pp. 13–25 | 2005 | 10.1007/11408031_2 | peer-reviewed | http://www.mia.uni-saarland.de/didas/pub/didas-scsp05.pdf | 2026-10-13 |
| S17 | T1 | Weickert, Ishikawa & Imiya, "Linear Scale-Space has First been Proposed in Japan" (not read; no open copy) | Journal of Mathematical Imaging and Vision 10(3), pp. 237–252 | 1999 | 10.1023/A:1008344623873 | peer-reviewed | https://doi.org/10.1023/A:1008344623873 | 2026-10-13 |
| S18 | T1 | Kannappan & Sahoo, "Rotation Invariant Separable Functions are Gaussian" (abstract only) | SIAM Journal on Mathematical Analysis 23(5), pp. 1342–1351 | 1992 | 10.1137/0523076 | peer-reviewed | https://doi.org/10.1137/0523076 | 2026-10-13 |
| S19 | T1 | Kuijper, "The Deep Structure of Gaussian Scale Space Images" (PhD thesis; abstract only) | Utrecht University | 2002 | hdl:1874/872 | peer-reviewed | https://dspace.library.uu.nl/handle/1874/872 | 2026-10-13 |
| S20 | T1 | Mikolajczyk & Schmid, "Indexing Based on Scale Invariant Interest Points" (abstract only) | Proc. IEEE ICCV 2001, vol. 1, pp. 525–531 | 2001 | 10.1109/ICCV.2001.937561 | peer-reviewed | https://doi.org/10.1109/ICCV.2001.937561 | 2026-10-13 |
| S21 | T1 | Mikolajczyk & Schmid, "Scale & Affine Invariant Interest Point Detectors" | International Journal of Computer Vision 60(1), pp. 63–86 | 2004 | 10.1023/B:VISI.0000027790.02288.f2 | peer-reviewed | https://www.robots.ox.ac.uk/~vgg/research/affine/det_eval_files/mikolajczyk_ijcv2004.pdf | 2026-10-13 |
| S22 | T1 | Rey-Otero & Delbracio, "Anatomy of the SIFT Method" | Image Processing On Line 4, pp. 370–396 | 2014 | 10.5201/ipol.2014.82 | peer-reviewed | http://www.ipol.im/pub/art/2014/82/article.pdf | 2026-10-13 |
| S23 | T1 | Rey-Otero, Morel & Delbracio, "An Analysis of the Factors Affecting Keypoint Stability in Scale-Space" (read as arXiv 1511.08478v1) | Journal of Mathematical Imaging and Vision 56(3), pp. 554–572 | 2016 | 10.1007/s10851-016-0657-5 | peer-reviewed | https://arxiv.org/abs/1511.08478 | 2026-10-13 |
| S24 | T1 | Bay, Ess, Tuytelaars & Van Gool, "Speeded-Up Robust Features (SURF)" | Computer Vision and Image Understanding 110(3), pp. 346–359 | 2008 | 10.1016/j.cviu.2007.09.014 | peer-reviewed | https://homes.esat.kuleuven.be/~konijn/publications/2008/CVIU-HB-08.pdf | 2026-10-13 |
| S25 | T3 | OpenCV source at commit 802cf95: `sift.dispatch.cpp`, `sift.simd.hpp`, `features2d.hpp`, `smooth.dispatch.cpp`, `resize.cpp` | — | 2026 | — | source | https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760 | 2026-10-13 |
| S26 | T3 | OpenCV tags 4.3.0, 4.4.0, 4.7.0, 4.8.0, 4.10.0: `features2d.hpp`, `sift.dispatch.cpp`, `sift.simd.hpp`; release dates from the GitHub releases API | — | 2024 | — | source | https://github.com/opencv/opencv/releases | 2026-10-13 |
| S27 | T3 | OpenCV issue #23123 ("SIFT detector has bias of 0.25 pixels…"), pull requests #23124 and #23270 | — | 2023 | — | source | https://github.com/opencv/opencv/issues/23123 | 2026-10-13 |
| S28 | T3 | scikit-image source at commit b700edc: `src/_skimage2/feature/sift.py`, `feature/blob.py`, `transform/_warps.py` | — | 2026 | — | source | https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2 | 2026-10-13 |
| S29 | T2 | SciPy, `scipy.ndimage.zoom` reference page, v1.18.0 | — | 2026 | — | official-docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.zoom.html | 2026-10-13 |
| S30 | T2 | MathWorks, `detectSIFTFeatures` and `SIFTPoints`, Computer Vision Toolbox documentation, R2026b | — | 2026 | — | official-docs | https://www.mathworks.com/help/vision/ref/detectsiftfeatures.html | 2026-10-13 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search "scale-space theory", sort cited_by_count | Lindeberg's 1994 book (2,169 cites) and his 1994 J. Applied Statistics tutorial (1,195): the survey to start from; physics noise otherwise |
| 2 | 1 | OpenAlex | title.search "scale-space axioms" | Duits et al. JMIV 2004 (124 cites); four 2026 Zenodo deposits on "hemigroup axioms", unreviewed, not used |
| 3 | 1 | OpenAlex | title.search "scale invariant feature transform survey" | two low-cited regional surveys; none used |
| 4 | 1 | OpenAlex | title.search "uniqueness of the gaussian kernel" | Babaud et al. TPAMI 1986 (804 cites) |
| 5 | 1 | OpenAlex | title.search "linear scale-space" | Weickert, Ishikawa & Imiya 1999 (180), Lindeberg's 2011 generalized axiomatics (121), Florack et al. 1994 (121) |
| 6 | 1 | OpenAlex | title.search for Koenderink 1984, Witkin, Yuille & Poggio, Lindeberg 1990 and 1998 (two), Pauwels 1995, Lifshitz & Pizer 1990 | all located with venue and pages; Witkin indexed through the 1987 reprint |
| 7 | 1 | OpenAlex | title.search for Lowe 2004 and 1999, Brown & Lowe, Mikolajczyk & Schmid 2001/2005, Mikolajczyk et al. 2005, Rey-Otero 2014 and 2016 | all located; Lowe 2004 has 55,530 cites |
| 8 | 1 | OpenAlex | open-access locations for 22 works | Lindeberg's papers point to KTH DiVA; Duits to TU/e; IPOL open; Mikolajczyk 2001 and 2005 to HAL |
| 9 | 1 | Web | urn.kb.se and kth.diva-portal.org resolvers for five Lindeberg URNs | no response within 40 s, twice: DiVA unreachable this session |
| 10 | 1 | Semantic Scholar | paper API for 9 DOIs (openAccessPdf) | answered; open PDFs only on DiVA and TU/e |
| 11 | 1 | Google Scholar | "Feature detection with automatic scale selection" Lindeberg | citing works; PLoS ONE 2013 printable PDF; SURF author copy at KU Leuven |
| 12 | 1 | Web | KTH CVAP abstract pages (cvap191–199) | technical-report versions of both 1998 IJCV papers on people.kth.se/~tony/papers (cvap198, cvap191) |
| 13 | 1 | arXiv | API, au:Lindeberg | "Rate exceeded" for the session |
| 14 | 1 | OpenAlex | works of author A5054396186 with arXiv locations | 36 works; 1210.0754 (PLoS ONE 2013), 2311.11317 (JMIV 2024), 1709.08603 fetched from arxiv.org/pdf |
| 15 | 1 | Web | link.springer.com PDFs of Lindeberg JMIV 2012 and 2015 (hybrid OA) | 3 kB HTML bot wall; not read |
| 16 | 4 | OpenAlex | title.search "local morse theory heat equation", "scale space hierarchy", "deep structure of gaussian scale space", "catastrophe theory scale space" | Damon 1995 (UNC copy unreachable); Kuijper's 2002 thesis abstract: critical points sometimes created in pairs |
| 17 | 4 | OpenAlex | title.search "hierarchical structure of images", "evolution of critical points under gaussian blurring" | Kuijper & Florack ECCV 2002, no abstract; not cited |
| 18 | 4 | Web | Saarland MIA publication list; TU/e author pages | Weickert 1999 and Duits 2004 not hosted (404); not read |
| 19 | 4 | Google Scholar | "Linear scale-space has first been proposed in Japan" | Didas et al. 2005 (Saarland PDF) and Felsberg & Sommer's 2002 Kiel report: both read, both carry the Poisson counterexample |
| 20 | 1 | Google Scholar | Koenderink 1984 "The structure of images" Biological Cybernetics | no open copy |
| 21 | 1 | OpenAlex | abstracts of 12 works | Babaud, Yuille & Poggio, Lindeberg 1990, Pauwels, Brown & Lowe, Mikolajczyk & Schmid 2001; Springer withheld Koenderink, Weickert, Duits, Florack |
| 22 | 1 | Crossref | 23 DOIs | every venue, year and page range confirmed; Lindeberg 1998 is pp. 79–116 (his own page says 77) |
| 23 | 1 | OpenAlex | title.search "monogenic scale-space", "fractional high order linear filtering", "discrete approximations of gaussian smoothing", "rotation invariant separable functions are gaussian" | identifiers for S15, S16, S12; Kannappan & Sahoo's abstract |
| 24 | 4 | OpenAlex | filter cites:W2151103935 (Lowe 2004) with title "scale invariant" (604), "SIFT" (1,996), "difference of gaussians" (20) | Lindeberg's Scholarpedia SIFT article; descriptors (ORB, BRISK, PCA-SIFT), out of scope; nothing corrective beyond Rey-Otero et al. |
| 25 | 4 | OpenAlex | filter cites:W2109200236 (Lindeberg 1998) with title "scale selection" (58), "interest point" (57) | edge/ridge 1998, Lindeberg JMIV 2012, Mikolajczyk & Schmid 2004, Brown & Lowe 2002 |
| 26 | 4 | Web | Scholarpedia SIFT article (curl; WebFetch refused an expired certificate) | read: DoG as (k²−1)/2 times the normalised Laplacian, the det/trace² edge test, Lindeberg 2015's determinant-of-Hessian result |
| 27 | 5 | GitHub | issues search "enable_precise_upscale", "SIFT upscale bias" in opencv/opencv | issue #23123, PRs #23124 and #23270 |
| 28 | 5 | GitHub | opencv/opencv releases API | release dates of 4.3.0, 4.4.0, 4.7.0, 4.8.0, 4.10.0 |
| 29 | 5 | GitHub | raw files at 802cf95 and tags | SIFT, GaussianBlur and resize rules (S25, S26) |
| 30 | 5 | GitHub | scikit-image tree at b700edc; issues search "SIFT bias / offset / half pixel / keypoint position" | sift.py, blob.py, _warps.py; no issue reports a position offset |
| 31 | 5 | Web | SciPy ndimage.zoom page; MathWorks detectSIFTFeatures and SIFTPoints pages | grid_mode semantics; MATLAB defaults, the 63-pixel ROI floor, Scale and Orientation conventions |
| 32 | 2 | Web | author copies: Lowe (UBC), Witkin (IJCAI), Brown & Lowe (BMVA), IPOL, arXiv 1511.08478, Mikolajczyk (VGG), SURF (KU Leuven), Surrey epubs | all read except Surrey's copy of Mikolajczyk et al. 2005 (an HTML login page) |
| 33 | 1 | Web | PLoS ONE figure g001 at sizes large, original, inline | CC BY; the original is 337×172 pixels |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Lowe defines the scale space as the image convolved with a variable-σ Gaussian and cites Koenderink 1984 and Lindeberg 1994 for the Gaussian being the only possible scale-space kernel under a variety of reasonable assumptions | S01 §3 | — |
| L02 | A difference of Gaussians with a constant scale ratio k approximates (k − 1)σ²∇²G through the heat equation written in σ; the factor is the same at every scale, so it moves no extremum; the error vanishes as k → 1 and Lowe found almost no effect on stability even at k = √2 | S01 §3 | first-order finite difference in σ |
| L03 | Each octave is split into s intervals, k = 2^(1/s); s + 3 Gaussian images are needed so detection covers a full octave; the next octave starts from the image whose σ is twice the initial one, resampled by taking every second pixel | S01 §3 | — |
| L04 | A sample is kept as a candidate only if it is larger than all 26 neighbours (8 in its image, 9 in each adjacent scale) or smaller than all of them | S01 §3.1 | Lowe's wording is strict |
| L05 | No sampling interval detects every extremum, because extrema can be arbitrarily close (one maximum for a circle, two for a long ellipse); close extrema are unstable under small perturbations | S01 §3.1 | — |
| L06 | On 32 real images rotated randomly and scaled by 0.2 to 0.9 with 1% noise, repeatability peaked at 3 scales per octave; more scales gave more extrema that were on average less stable; matching scale meant within a factor of √2 and location within σ | S01 §3.2 | Lowe's synthetic-transformation experiment |
| L07 | Repeatability kept increasing with the prior smoothing σ of each octave; 1.6 was chosen as close to optimal at acceptable cost | S01 §3.3 | same experiment |
| L08 | Lowe doubles the input by linear interpolation, assumes the original has blur of at least 0.5 (the minimum to avoid significant aliasing) so the doubled image has 1.0; doubling raises the number of stable keypoints by almost a factor of 4, and larger expansion gave no significant gain | S01 §3.3 | — |
| L09 | A keypoint's σ is defined as the standard deviation of the smaller of the two Gaussians in its DoG | S01 §3.2 | — |
| L10 | Brown's method fits a 3-D quadratic (Taylor expansion to second order) to D around the sample and takes its extremum, x̂ = −H⁻¹∇D; an offset above 0.5 in any dimension moves the sample point; D(x̂) = D + ½∇Dᵀx̂; extrema with abs(D(x̂)) below 0.03 are discarded for pixel values in 0–1 | S01 §4 | pixel values scaled to 0–1 |
| L11 | On a 233×189 image, 832 DoG extrema became 729 after the contrast test and 536 after the curvature-ratio test | S01 §4, §4.1, Fig. 5 | one image |
| L12 | The DoG responds strongly along edges where position along the edge is poorly determined; the 2×2 Hessian's eigenvalue ratio is tested through Tr²/Det < (r + 1)²/r with r = 10; a negative determinant means curvatures of opposite sign and the point is discarded; the idea is borrowed from Harris and Stephens | S01 §4.1 | — |
| L13 | Orientation: 36-bin gradient-orientation histogram from the Gaussian image closest in scale, weighted by magnitude and a Gaussian window of 1.5 times the keypoint's σ; any other peak within 80% of the highest makes another keypoint; about 15% of points get several orientations; a parabola refines each peak | S01 §5 | — |
| L14 | Descriptor: a 4×4 array of 8-bin orientation histograms (128 values) from a window scaled by the keypoint's σ, Gaussian-weighted with σ half the window width, trilinear interpolation, normalised to unit length, values clipped at 0.2 (set experimentally) and renormalised | S01 §6.1 | — |
| L15 | Lowe's 1999 detector smoothed with σ = √2, formed DoGs with ratio √2, resampled each next level by bilinear interpolation at a pixel spacing of 1.5, and expanded the input by 2 beforehand | S02 §3 | — |
| L16 | Brown and Lowe fitted a 3-D quadratic to the scale-space Laplacian (DoG) samples, with derivatives from pixel differences, to locate interest points to sub-pixel and sub-scale accuracy; it matters most at high pyramid levels, whose sample spacing is large, and clearly improved repeatability | S03 §2, §5.1, Fig. 9 | their Annapurna image set |
| L17 | Witkin: no single scale of description is categorically correct; computing descriptions at many scales does not by itself relate them; scale-space filtering sweeps σ continuously into a scale-space image in which extrema are tracked across scale | S04 §1 | — |
| L18 | Witkin: under Gaussian smoothing, zero-crossings may appear as σ decreases but existing ones cannot in general disappear, and among well-behaved kernels the Gaussian is the only one guaranteed this | S04 §2 | one-dimensional signals |
| L19 | Koenderink's causality: every feature at a coarse resolution must have a cause at a finer one, though not the reverse; his formal version (at an extremum the convex side of an isophote points to coarser scales) is essentially non-enhancement of local extrema, and leads to the diffusion equation | S15 §1.2 (A8), §2.4; S01 §3 | not read; as described by S15 and S01 |
| L20 | Babaud et al. proved that the Gaussian is the only kernel in a broad class with this monotone behaviour of maxima and minima as the bandwidth grows, and drew the consequences for zero-crossing contours in scale space | S06 abstract | abstract only |
| L21 | Yuille and Poggio proved that in any dimension the only filter that creates no generic zero-crossings of the Laplacian as scale increases is the Gaussian; for the second derivative along the gradient no filter avoids creating them | S07 abstract | abstract only |
| L22 | For discrete signals the right construction discretises the diffusion equation, which gives the discrete analogue of the Gaussian; a sampled Gaussian can misbehave, especially at fine scales | S08 abstract | abstract only |
| L23 | Under the diffusion equation, a local maximum cannot increase and a local minimum cannot decrease with scale, so unnormalised derivative amplitudes always decrease with scale | S09 §3 | — |
| L24 | γ-normalised derivatives multiply each derivative by t^(γ/2), t = σ²; with γ = 1 they are dimensionless and give perfect scale invariance: if the image is rescaled by s, maxima over scale occur at corresponding points with t multiplied by s² (σ by s) | S09 §3, §4.1 eqs. 17–23 | — |
| L25 | Lindeberg's principle: in the absence of other evidence, a scale at which a combination of normalised derivatives has a local maximum over scales reflects a characteristic length of a structure | S09 §4 | heuristic, to be verified empirically |
| L26 | A blob detector at one fixed scale ranks structures of one size highest (50 strongest responses differ at t = 4, 16, 64); detecting scale-space maxima treats all sizes between the inner and outer scale alike | S09 §5.2, Fig. 6 | — |
| L27 | For a diffuse step edge, the γ-normalised gradient peaks at t = γt0/(1 − γ), so γ = 1/2 selects the edge's own diffuseness; with γ = 1 the edge strength grows monotonically with scale and would select an infinitely large scale | S10 §4.5.1 | — |
| L28 | Linearity, shift invariance, a semigroup over scale, regularity and non-enhancement of local extrema force a diffusion equation with a covariance matrix and a drift; mirror symmetry removes the drift and rotational symmetry leaves the Gaussian; the semigroup gives the cascade property L(s2) = T(s2 − s1) ∗ L(s1) | S11 §2.1–2.2 | Lindeberg 2011 Theorem 5, as restated |
| L29 | Non-creation of new local extrema with scale is guaranteed for one-dimensional signals; in N dimensions the guarantee is non-enhancement (a maximum's value does not grow, a minimum's does not fall); Gaussian smoothing is separable into 1-D passes | S12 §2.1 | — |
| L30 | Lindeberg writes the DoG as a difference in variance s = σ², DoG ≈ (Δs/2)∇²L, so with σ(i+1) = kσ(i) it equals ((k² − 1)/2) times the scale-normalised Laplacian | S13 §1 | first-order in Δs |
| L31 | Scholarpedia states SIFT's edge test as det/trace² ≥ r/(r + 1)², a reformulation that avoids dividing by a determinant that approaches zero along edges | S13 §1 | — |
| L32 | Lindeberg reports that replacing Laplacian interest points by determinant-of-Hessian interest points gave substantially better matching on 12 posters under scalings up to 6 and slants up to 45°, and argues the same holds for SIFT's DoG points | S13 §1, summarising Lindeberg 2015 | his JMIV 2015 paper not read |
| L33 | Requiring linear, isotropic convolution with a semigroup (recursivity) and scale invariance leaves a one-parameter family of filters; the Gaussian is one member and the others have more complex excitatory and inhibitory regions; only a discrete subset evolves by a partial differential equation | S14 abstract | abstract only |
| L34 | The Poisson kernel is linear, shift invariant, a semigroup, scale and rotation invariant and positivity preserving, which makes it a counterexample to Iijima's uniqueness proof; that proof implicitly assumed the kernel's frequency response is continuously differentiable at the origin | S15 §2.2 | — |
| L35 | Adding separability (equivalently, closure under the full affine group) to those axioms leaves only the Gaussian from the family exp(−2π abs(ξ)^α b), 0 < α ≤ 2: separability is the only axiomatic difference between the Poisson and Gaussian kernels | S15 §2.2 | — |
| L36 | Felsberg and Sommer list "no new maxima with increasing scale" as an axiom valid only in one dimension, citing Babaud et al. | S15 §1.2 (A10) | — |
| L70 | Only the Gaussian scale space has the non-enhancement property, so the Poisson scale space fails causality in its strict form (a one-dimensional example due to Babaud et al.); it does satisfy a relaxed causality, in which every level-crossing surface connects to scale zero, for DC-free 2-D signals | S15 §2.4, Fig. 3, Theorem 3 | — |
| L37 | Iijima's 1960s axioms were linearity, translation invariance, scale invariance and the semigroup property; α-scale-spaces generalise them, and the admissible α is limited by a maximum–minimum principle that orders above the Gaussian's violate; the Poisson scale-space is the best-known fractional member | S16 §1, §7 | — |
| L38 | Weickert, Ishikawa and Imiya traced linear scale-space to Iijima's work in Japan, before Witkin and Koenderink | S17 title; S15 ref. 41; S16 §1 | not read; as described by S15 and S16 |
| L39 | Every rotation-invariant separable real function of two variables is a Gaussian or identically zero | S18 abstract | abstract only |
| L40 | Spatial critical points of a Gaussian scale-space image are generically annihilated with increasing scale and sometimes created, in extremum–saddle pairs | S19 abstract | abstract only |
| L41 | Harris–Laplace (2001): compute a multi-scale Harris representation, then keep points where the Laplacian is maximal over scales, which gives each point a characteristic scale | S20 abstract | abstract only |
| L42 | The scale-adapted second-moment matrix is σD² times a Gaussian of σI applied to the gradient outer products; Harris–Laplace uses levels σn = ξ^n σ0 with ξ = 1.4 and σD = 0.7 σI, and keeps Harris maxima over each 8-neighbourhood above a threshold | S21 §2.1–2.2, eqs. 1–2 | — |
| L43 | Simplified Harris–Laplace keeps a point only if the Laplacian at its level exceeds the finer and coarser levels and passes a threshold; accuracy needs a small level ratio (1.2); the iterative version is more accurate | S21 §2.2 | — |
| L44 | The scale-adapted Harris measure rarely attains a maximum over scales, and the Laplacian of Gaussian found the highest percentage of correct characteristic scales in their comparison | S21 §2.1 | citing their 2001 experiments |
| L45 | The ratio of the characteristic scales found at corresponding points equals the scale factor between the two neighbourhoods | S21 §2.1 | — |
| L46 | The IPOL description of SIFT uses σmin 0.8, δmin 0.5, nspo 3, σin 0.5; a DoG threshold CDoG = 0.015 for 3 scales per octave, rescaled by (2^(1/nspo) − 1)/(2^(1/3) − 1), with 80% of it as a pre-test; Cedge = 10 | S22 §2–3, Table 3 | — |
| L47 | IPOL's bilinear interpolator samples the input at x = δ′m′, with no half-pixel offset | S22 Alg. 2 | — |
| L48 | For σ of 0.7 and above, the digital Gaussian obeys the semigroup relation to within 1e-4 for intensities between 0 and 1 | S22 §2 | as stated by IPOL |
| L49 | IPOL finds that the edge threshold has a negligible effect in practice, because refinement already discards many edge candidates | S22 §5 | their experiments |
| L50 | Even in a favourable simulated setting many SIFT keypoints are unstable; sampling scale at 15 per octave instead of 3 (with finer spatial sampling) improves stability; the contrast threshold does not remove unstable detections; the quadratic refinement matters; aliasing or a wrong assumed blur degrade invariance, asymmetrically | S23 abstract, §7 | simulation study |
| L51 | SURF: Gaussians are optimal for scale-space analysis but must be discretised and cropped, which costs repeatability under rotations near odd multiples of 45°; SURF replaces Gaussian second derivatives by box filters on integral images at constant cost, the 9×9 filter standing for σ = 1.2, and builds scale by enlarging the filter instead of shrinking the image | S24 §3.2–3.3 | — |
| L52 | SURF's authors note that box filters keep high frequencies that zoomed-out views lose, which can limit scale invariance, though they did not notice it in their experiments | S24 §3.3 | their experiments |
| L53 | `SIFT::create` defaults: nfeatures 0, nOctaveLayers 3, contrastThreshold 0.04, edgeThreshold 10, sigma 1.6, enable_precise_upscale false; the documentation says the contrast threshold is divided by nOctaveLayers and that Lowe's 0.03 corresponds to 0.09 | S25 features2d.hpp | at 802cf95; same at 4.10.0 |
| L54 | The initial image is the 8-bit input as float, doubled when firstOctave is −1 (by resize with linear interpolation, or by warpAffine mapping x to 2x when precise upscale is on), then blurred by sqrt(max(σ² − (2 × 0.5)², 0.01)) = 1.249; SIFT_INIT_SIGMA is 0.5 | S25 sift.dispatch.cpp, sift.simd.hpp | default sigma 1.6 |
| L55 | Each octave's layers are blurred incrementally by sqrt((k^i σ)² − (k^(i−1) σ)²), the next octave starts from layer nOctaveLayers halved by nearest-neighbour resize, and nOctaves = round(log2(min side of the doubled image) − 2) + 1 | S25 sift.dispatch.cpp | — |
| L56 | Candidates must exceed floor(0.5 × 0.04 / 3 × 255) = 1 grey level in absolute value, lie at least 5 pixels from the border, and be ≥ (maxima) or ≤ (minima) all 26 neighbours | S25 sift.dispatch.cpp, sift.simd.hpp | non-strict comparison |
| L57 | Refinement runs at most 5 steps; derivatives are scaled by 1/255; a point is rejected if abs(D(x̂)) × nOctaveLayers < contrastThreshold, or if det ≤ 0 or r·tr² ≥ (r + 1)²·det; size = σ·2^((layer + ξ)/s)·2^octave·2 and response = abs(D(x̂)); coordinates and size are halved for the doubled first octave | S25 sift.simd.hpp, sift.dispatch.cpp | — |
| L58 | Orientation uses radius round(4.5σ), a Gaussian weight of 1.5σ, 36 bins smoothed by [1 4 6 4 1]/16, peaks at least 0.8 of the maximum, parabolic interpolation, and angle = 360 − 10 × bin | S25 sift.simd.hpp | — |
| L59 | Descriptor cells are 3σ wide in a 4×4 grid of 8 bins; values are clipped at 0.2 of the vector norm | S25 sift.simd.hpp | — |
| L60 | GaussianBlur on float images picks ksize = round(8σ + 1), forced odd, builds the sampled normalised Gaussian, and uses reflect-101 by default; Intel IPP is used only in builds that enable it, and is not bit-exact | S25 smooth.dispatch.cpp | — |
| L61 | resize with linear interpolation maps output x to input (x + 0.5) × scale − 0.5, the pixel-area convention | S25 resize.cpp line 3907 | generic path |
| L62 | OpenCV's SIFT source notes patent US 6,711,293 (issued 23 March 2004, provisional filed 8 March 1999, assigned to the University of British Columbia) and that it expired in March 2020 | S25 sift.dispatch.cpp header | — |
| L63 | SIFT is in the main features2d module from 4.4.0 (released 2020-07-18), not in 4.3.0; enable_precise_upscale first appears in 4.8.0 (released 2023-06-28), not in 4.7.0; 4.10.0's SIFT files carry the same rules as 802cf95 | S26 | — |
| L64 | Issue #23123 (opened 2023-01-10, still open) reports a 0.25-pixel bias from doubling by linear interpolation then halving by nearest neighbour; PR #23124 (merged 2023-02-17) added the x → 2x upscaling; PR #23270 (merged the same day) made it false by default "temporarily", because warpAffine is not bit-exact and regression tests failed sporadically | S27 | — |
| L71 | Constructing SIFT with precise upscale disabled logs, once, that this is deprecated because it was found to induce a location bias | S25 sift.dispatch.cpp (SIFT_Impl constructor) | at 802cf95 |
| L65 | scikit-image's SIFT defaults: upsampling 2, n_octaves 8, n_scales 3, sigma_min 1.6, sigma_in 0.5, c_dog 0.04/3 rescaled by (2^(1/n_scales) − 1)/(2^(1/3) − 1), c_edge 10, n_bins 36, lambda_ori 1.5, c_max 0.8, lambda_descr 6, n_hist 4, n_ori 8; it follows the IPOL description | S28 sift.py | — |
| L66 | scikit-image's SIFT upsamples with rescale (order 1), which calls ndi.zoom with grid_mode=True, and reports positions as (index + offset) × δ, δ = 2^o / upsampling | S28 sift.py, _warps.py | — |
| L72 | scikit-image's SIFT finds 3×3×3 extrema with a compiled helper, refines them, keeps only those more than one sample inside each octave's border, and reports sigmas (blur values) and orientations in radians from arctan2 | S28 sift.py (_find_localize_evaluate, _inrange, orientation loop) | at b700edc |
| L67 | scikit-image's blob_log multiplies the negated Laplacian of Gaussian by s²; blob_dog divides differences by (sigma_ratio − 1), default ratio 1.6; both report a blob radius of about √2 σ in 2-D | S28 blob.py | — |
| L68 | In ndimage.zoom, grid_mode=False zooms the distance between pixel centres; True uses the full pixel extent (a 5-sample signal counts as length 5) | S29 | v1.18.0 |
| L69 | MATLAB's detectSIFTFeatures (introduced R2021b) defaults to ContrastThreshold 0.0133, EdgeThreshold 10, NumLayersInOctave 3, Sigma 1.6, and requires the ROI to be at least 63 pixels wide and high; SIFTPoints.Scale is the detection scale (default 1.6) and Orientation is in radians | S30 | R2026b |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S01 | Figures 1 and 2 | Octaves / L03, L04 | the pyramid and the 26-neighbour cube | © Kluwer 2004; no reuse licence on the author copy | https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf | do not reuse; our Figures 2 and 9 draw the patch's own numbers |
| F2 | S04 | Figure 2 | Why the Gaussian / L18 | zero-crossing contours in a scale-space image | no licence stated | https://www.ijcai.org/Proceedings/83-2/Papers/091.pdf | do not reuse |
| F3 | S11 | Figure 1 | Why the Gaussian / L28 | the non-enhancement requirement drawn on a 1-D signal | CC BY (PLoS ONE) | https://doi.org/10.1371/journal.pone.0066990 | rights clear, but one sentence carries it and the original is 337×172 pixels: not needed |
| F4 | S22 | Figures 4–6 | Octaves / L46 | the digital scale-space and DoG octaves | CC BY-NC-SA (non-commercial) | http://www.ipol.im/pub/art/2014/82/article.pdf | do not reuse |

## Open questions

- Koenderink 1984 and Weickert et al. 1999 could not be read (no open copy; Springer withholds both
  abstracts). The post attributes to them only what Lowe, Felsberg & Sommer and Didas et al. say.
- Duits et al. 2004 (the α-scale-space analysis) was not read; its result enters only through Didas et
  al.'s summary (S16), and the post does not cite it directly.
- Lindeberg's JMIV 2012 and 2015 papers sit behind Springer's bot wall; the determinant-of-Hessian
  result is cited as Lindeberg summarises it in S13.
- The orientation count predicted for OpenCV's default (two keypoints at the blob) is fragile: the
  third histogram peak sits at 0.789 of the highest against the 0.8 cut. The post states the count
  only for `enable_precise_upscale=True` (three, the nearest rival at 0.665) and flags the default.
- Whether scikit-image's SIFT shows the same 0.25-pixel offset is predicted from its code (zoom with
  grid_mode=True, positions as index × δ); no issue reports it and it was not run.
- Lindeberg's own pages give the 1998 IJCV paper as pp. 77–116; Crossref gives 79–116. The post uses
  Crossref.
