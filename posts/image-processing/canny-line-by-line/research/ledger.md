# Source ledger — canny-line-by-line

Series `image-processing`, part 8. Sweep run 2026-10-12. Tier L3, so the floor is 7 peer-reviewed
or standard sources carrying an identifier, across 4 scholarly databases.

How each source was read is stated per row. Read in full: Canny 1986 (the Clemson course copy, a
scan read through its text layer; sections VI and VII read line by line), Grompone von Gioi &
Randall 2017 (IPOL, open), Spontón & Cardelino 2015 (IPOL, open), Papari & Petkov 2011 (the
authors' copy on Petkov's Groningen page), Li, Sullivan & Baker 1989 (BMVA archive), Desolneux,
Moisan & Morel 2001 (Desolneux's CNRS page). Used **only for what their abstracts state** (OpenAlex
record, venue and pages cross-checked against the publisher's DOI): Hancock & Kittler 1991,
Henstock & Chelberg 1996.

Library behaviour was read at pinned commits: OpenCV `802cf95aa3d4` (2026-10-10, the commit Part 7
pinned): `modules/imgproc/src/canny.cpp`, `canny.simd.hpp`, `canny.hpp`, `spatialgradient.cpp`,
`deriv.cpp`, `include/opencv2/imgproc.hpp`, `modules/core/include/opencv2/core/base.hpp`, the C++
and Python Canny tutorials and `samples/cpp/tutorial_code/ImgTrans/CannyDetector_Demo.cpp`;
scikit-image `b700edc8005e` (2026-10-09, the commit Parts 5–7 pinned): `src/_skimage2/feature/_canny.py`,
`_canny_cy.pyx`, `src/skimage/feature/_canny.py`, `src/_skimage2/util/_value_rescaling.py`. MATLAB
behaviour is from MathWorks' documentation page for `edge`, release R2026b. Nothing was executed
against an image. The only code run was plain Python (`math` only) reproducing the post's
hand-worked numbers: Sobel on the shared patch under replicate and reflect-101 borders, OpenCV's
suppression rule transcribed from `canny.simd.hpp`, scikit-image's interpolated rule transcribed
from `_canny_cy.pyx`, hysteresis as 8-connected components, the shared Gaussian, Devernay's
correction, OpenCV's Sobel kernel generator, and the noise-model and a contrario closed forms.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Canny, "A Computational Approach to Edge Detection" | IEEE TPAMI 8(6), pp. 679–698 | 1986 | 10.1109/TPAMI.1986.4767851 | peer-reviewed | https://cecas.clemson.edu/~ahoover/ece431/refs/Canny.pdf | 2026-10-12 |
| S02 | T1 | Grompone von Gioi & Randall, "A Sub-Pixel Edge Detector: an Implementation of the Canny/Devernay Algorithm" | Image Processing On Line 7, pp. 347–372 | 2017 | 10.5201/ipol.2017.216 | peer-reviewed | https://www.ipol.im/pub/art/2017/216/article.pdf | 2026-10-12 |
| S03 | T1 | Spontón & Cardelino, "A Review of Classic Edge Detectors" | Image Processing On Line 5, pp. 90–123 | 2015 | 10.5201/ipol.2015.35 | peer-reviewed | https://www.ipol.im/pub/art/2015/35/article.pdf | 2026-10-12 |
| S04 | T1 | Papari & Petkov, "Edge and line oriented contour detection: State of the art" (survey) | Image and Vision Computing 29(2–3), pp. 79–103 | 2011 | 10.1016/j.imavis.2010.08.009 | peer-reviewed | https://www.cs.rug.nl/~petkov/publications/2011ivc-contour_survey.pdf | 2026-10-12 |
| S05 | T1 | Li, Sullivan & Baker, "Edge Detection at Junctions" | Proc. Alvey Vision Conference 1989, pp. 21.1–21.6 | 1989 | 10.5244/C.3.21 | peer-reviewed | https://www.bmva-archive.org.uk/bmvc/1989/avc-89-021.pdf | 2026-10-12 |
| S06 | T1 | Desolneux, Moisan & Morel, "Edge Detection by Helmholtz Principle" | Journal of Mathematical Imaging and Vision 14(3), pp. 271–284 | 2001 | 10.1023/A:1011290230196 | peer-reviewed | https://desolneux.perso.math.cnrs.fr/papers/DMM_Edge_01.pdf | 2026-10-12 |
| S07 | T1 | Hancock & Kittler, "Adaptive Estimation of Hysteresis Thresholds" (abstract only) | Proc. CVPR 1991, pp. 196–201 | 1991 | 10.1109/CVPR.1991.139687 | peer-reviewed | https://doi.org/10.1109/CVPR.1991.139687 | 2026-10-12 |
| S08 | T1 | Henstock & Chelberg, "Automatic Gradient Threshold Determination for Edge Detection" (abstract only) | IEEE TIP 5(5), pp. 784–787 | 1996 | 10.1109/83.499917 | peer-reviewed | https://doi.org/10.1109/83.499917 | 2026-10-12 |
| S09 | T3 | OpenCV source at commit 802cf95: `modules/imgproc/src/canny.cpp`, `canny.simd.hpp`, `canny.hpp`, `spatialgradient.cpp`, `deriv.cpp`; `modules/imgproc/include/opencv2/imgproc.hpp`; `modules/core/include/opencv2/core/base.hpp`; `hal/ipp/src/canny_ipp.cpp`, `hal/ipp/include/ipp_hal_imgproc.hpp` | — | 2026 | — | source | https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src | 2026-10-12 |
| S10 | T2 | OpenCV documentation at commit 802cf95: `doc/tutorials/imgproc/imgtrans/canny_detector/canny_detector.markdown`, `doc/py_tutorials/py_imgproc/py_canny/py_canny.markdown`, `samples/cpp/tutorial_code/ImgTrans/CannyDetector_Demo.cpp` | — | 2026 | — | official-docs | https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760/doc | 2026-10-12 |
| S11 | T3 | scikit-image source at commit b700edc: `src/_skimage2/feature/_canny.py`, `_canny_cy.pyx`, `src/skimage/feature/_canny.py`, `src/_skimage2/util/_value_rescaling.py` | — | 2026 | — | source | https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/feature | 2026-10-12 |
| S13 | T3 | OpenCV source at tag 4.10.0: `modules/imgproc/src/canny.cpp`, `modules/core/include/opencv2/core/private.hpp` (a release, to check the pinned commit against what users install) | — | 2024 | — | source | https://github.com/opencv/opencv/blob/4.10.0/modules/imgproc/src/canny.cpp | 2026-10-12 |
| S12 | T2 | MathWorks, `edge` — Find edges in 2-D grayscale image (Image Processing Toolbox), release R2026b | — | 2026 | — | official-docs | https://www.mathworks.com/help/images/ref/edge.html | 2026-10-12 |

Located and not used in the post: McIlhagga, "The Canny Edge Detector Revisited", IJCV 91(3)
251–261, 2011, 10.1007/s11263-010-0392-0 (abstract withheld by Springer in OpenAlex and Semantic
Scholar; its subject, Canny's optimality criteria, is Part 1's); Ding & Goshtasby, "On the Canny
edge detector", Pattern Recognition 34(3) 721–725, 2001, 10.1016/S0031-3203(00)00023-6 (abstract
withheld; its point, edges missed by the two-sided maximum test, is carried by S05, read in full);
Rosin, "Edges: saliency measures and automatic thresholding", Machine Vision and Applications 9(4)
139–159, 1997, 10.1007/s001380050036 (author copy returned 403; S04 covers the Rayleigh model);
Medina-Carnicer, Muñoz-Salinas, Yeguas-Bolívar & Díaz-Más, "A novel method to look for the
hysteresis thresholds for the Canny edge detector", Pattern Recognition 44(6) 1201–1211, 2011,
10.1016/j.patcog.2010.12.008 (abstract withheld); Sen & Pal, "Gradient histogram: Thresholding in a
region of interest for edge detection", Image and Vision Computing 28(4) 677–695, 2010,
10.1016/j.imavis.2009.10.010; Canny, *Finding Edges and Lines in Images*, MIT AI-TR-720, 1983
(DSpace returned 405; its suppression scheme is cited through S02 §2, which quotes it with its
section number).

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | web (general) | edge detection survey review "Canny" hysteresis non-maximum suppression state of the art | course notes and arXiv comparisons only; no survey, so the sweep turned to the databases |
| 2 | 1 | Semantic Scholar | citations of 10.5201/ipol.2017.216 | 61 citing works, nearly all applications; one methods follow-up (subpixel weighting, IEEE TIP 2018); nothing contradicting S02 |
| 3 | 1 | web (general) | Papari Petkov "Edge and line oriented contour detection: State of the art" pdf | the survey (S04) with the authors' copy on Petkov's page; read §3.1 and §8.2 |
| 4 | 1 | IPOL references of S02 | backward chase from S02 | Canny's AI-TR-720 (S02 quotes §5.3), Devernay RR-2724, S03, S04 |
| 5 | 1 | web (general) | Canny "Finding edges and lines in images" MIT AI Technical Report 720 1983 pdf | DSpace handle 1721.1/6939; the PDF returned HTTP 405 (bot wall) |
| 6 | 1 | OpenAlex | DOIs of S01, S07, Ding & Goshtasby, McIlhagga, Rosin, Medina-Carnicer, Sen & Pal | venues, volumes and pages confirmed; abstracts only for S01 and S07 |
| 7 | 1 | Semantic Scholar | the same five DOIs, abstract field | titles and venues; abstracts withheld for all five |
| 8 | 4 | web (general) | McIlhagga "The Canny edge detector revisited" IJCV 2011 | the localisation criterion was derived incorrectly and the criteria give an infinitely wide operator; Part 1's subject, not used |
| 9 | 4 | web (general) | Ding Goshtasby "On the Canny edge detector" Pattern Recognition 2001 | abstract via an aggregator only: the two-sided maximum test misses obvious edges; led to S05 |
| 10 | 4 | web (general) | Li Sullivan Baker 1989 Alvey Vision Conference Canny junction non-maximal suppression | S05 on the BMVA archive; read in full |
| 11 | 1 | Crossref | bibliographic: Edge detection at junctions Li Sullivan Baker 1989 | 10.5244/c.3.21, pages 21.1–21.6 confirmed |
| 12 | 3 | web (general) | automatic selection of hysteresis thresholds Canny edge detector gradient magnitude histogram | percentile and fixed-ratio heuristics in course notes and code; Sen & Pal 2010 as the journal reference |
| 13 | 3 | web (general) | Medina-Carnicer "hysteresis thresholds" Canny Pattern Recognition 2011 | PR 44(6) 1201–1211; abstract not reachable |
| 14 | 3 | web (general) | Hancock Kittler "Adaptive estimation of hysteresis thresholds" CVPR 1991 | S07, pages 196–201; abstract read in OpenAlex |
| 15 | 3 | web (general) | Voorhees Poggio Rayleigh distribution gradient magnitude noise estimate edge threshold | only secondary mentions of the 1987 paper; Rosin's note named as the reference for Rayleigh fits |
| 16 | 3 | web (general) | Rosin "Edges: saliency measures and automatic thresholding" MVA 1997 | MVA 9(4) 139–159; the author copy returned 403 |
| 17 | 3 | OpenAlex | title: automatic gradient threshold determination for edge detection | S08, IEEE TIP 5(5) 784–787, abstract read |
| 18 | 3 | OpenAlex | title: edge detection by helmholtz principle | S06, JMIV 14 271–284 |
| 19 | 3 | web (general) | Desolneux Moisan Morel "Edge detection by Helmholtz principle" pdf | S06 on Desolneux's CNRS page; §2 and §3.1 read |
| 20 | 5 | web (general) | MATLAB edge Canny "PercentOfPixelsNotEdges" "ThresholdRatio" | only MATLAB Answers threads (not citable); MathWorks' own page (S12) read instead |
| 21 | 1 | arXiv | abs:canny AND abs:hysteresis | one coastline-detection paper; the topic's literature is in journals |
| 22 | 1 | DBLP | Canny edge detector revisited | Anubis bot wall; venues checked in Crossref and OpenAlex instead |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | `cv2.Canny` computes both derivatives with a Sobel of the given aperture directly on the input image, with a replicate border; the function has no Gaussian smoothing step | S09 canny.cpp `parallelCanny` (spatialGradient with BORDER_REPLICATE), `Canny()` | commit 802cf95; 8-bit input path |
| L02 | `Canny` asserts an 8-bit input; an overload takes precomputed 16-bit signed dx and dy | S09 canny.cpp `Canny()` asserts | commit 802cf95 |
| L03 | Aperture must be odd from 3 to 7, or −1; −1 reaches Sobel as ksize −1, which OpenCV turns into Scharr kernels | S09 canny.cpp aperture check, spatialgradient.cpp assert and fallback, deriv.cpp `getDerivKernels` | commit 802cf95; −1 is not in the documentation |
| L04 | With aperture 7 the derivatives are computed at scale 1/16 and both thresholds are divided by 16 | S09 canny.cpp `Canny()` and `parallelCanny` | commit 802cf95 |
| L05 | If the low threshold is larger than the high one, OpenCV swaps them | S09 canny.cpp `Canny()` | commit 802cf95 |
| L06 | The default magnitude is the sum of absolute derivatives; with L2gradient the thresholds are capped at 32767, squared, and compared with dx² + dy² | S09 canny.cpp `Canny()`, canny.simd.hpp `canny_calc_magnitude` | commit 802cf95 |
| L07 | Suppression sorts each pixel into one of four direction bins using tan 22.5° in fixed point (13573 over 2 to the 15th) and tan 67.5° = tan 22.5° + 2; the horizontal bin requires greater-than the left neighbour and greater-or-equal to the right, the vertical bin greater-than above and greater-or-equal below, the diagonal bins strictly greater than both diagonal neighbours chosen by the signs of dx and dy | S09 canny.simd.hpp `canny_nms_row` | commit 802cf95 |
| L08 | Only pixels whose magnitude exceeds the low threshold are tested; a local maximum above the high threshold is marked an edge and pushed on a stack, other local maxima are kept as candidates | S09 canny.simd.hpp `canny_nms_row`, `CANNY_CHECK` | strict comparisons |
| L09 | Hysteresis pops each edge pixel and marks every candidate among its 8 neighbours as an edge, pushing it in turn | S09 canny.cpp, global hysteresis loop | commit 802cf95 |
| L10 | In suppression, magnitudes beyond the image border are read as 0 | S09 canny.cpp `parallelCanny` (zeroed ring buffers and border entries) | commit 802cf95 |
| L11 | For a multi-channel input, each pixel takes the magnitude and direction of the channel with the largest magnitude | S09 canny.cpp `parallelCanny` | cn > 1 |
| L12 | OpenCV documents that the smaller threshold is used for linking and the larger for finding strong segments, apertureSize as the Sobel aperture, and L1 as the default norm | S09 imgproc.hpp, `Canny` doc comment | commit 802cf95 |
| L13 | OpenCV's default border mode is reflect-101 | S09 core/base.hpp `BORDER_DEFAULT` | commit 802cf95 |
| L14 | OpenCV's Python tutorial gives a 5×5 Gaussian as Canny's first step, rounds the gradient direction to four angles, and says `cv.Canny()` puts all the steps in one function | S10 py_canny.markdown | commit 802cf95 |
| L15 | OpenCV's C++ tutorial attributes an upper-to-lower ratio of 2:1 to 3:1 to Canny; its demo smooths with a 3×3 box `blur`, then calls Canny with ratio 3 and aperture 3 | S10 canny_detector.markdown, CannyDetector_Demo.cpp | commit 802cf95 |
| L16 | OpenCV's 5- and 7-tap Sobel kernels are smoothing 1 4 6 4 1 and 1 6 15 20 15 6 1 with derivatives −1 −2 0 2 1 and −1 −4 −5 0 5 4 1, built from repeated [1 1] sums and one difference | S09 deriv.cpp `getSobelKernels` | commit 802cf95 |
| L17 | scikit-image's `canny` smooths with a Gaussian of sigma (default 1.0), takes SciPy Sobel derivatives along both axes, and uses the Euclidean magnitude | S11 _canny.py | commit b700edc |
| L18 | scikit-image's thresholds default to 10% and 20% of the dtype maximum; explicit thresholds are divided by that maximum while integer images are rescaled to 0–1; `use_quantiles` reads them as percentiles of the magnitude image; low above high raises an error | S11 _canny.py, _value_rescaling.py | commit b700edc |
| L19 | scikit-image's suppression interpolates linearly between the two neighbours the gradient line passes between, with weight the smaller gradient component over the larger, and keeps a pixel when both interpolated values are less than or equal to its magnitude | S11 _canny_cy.pyx | commit b700edc |
| L20 | scikit-image's hysteresis labels 8-connected components of the candidates (magnitude at least low) and keeps each component that holds a pixel at least the high threshold | S11 _canny.py | commit b700edc |
| L21 | scikit-image masks out the one-pixel image border; the Gaussian's border mode defaults to constant in `skimage.feature.canny` and nearest in the skimage2 version | S11 _canny.py, skimage/feature/_canny.py | commit b700edc |
| L22 | MATLAB's `edge` with "canny" takes thresholds in 0–1 as [low high]; a scalar is the high threshold and the low one is 0.4 times it; omitted thresholds are chosen heuristically; sigma defaults to the square root of 2 | S12 | release R2026b |
| L23 | Canny's hysteresis outputs every point of a contour above the high threshold and the whole connected segment of that contour that stays above the low one | S01 §VI, p. 690 | his implementation |
| L24 | With one threshold set at a contour's mean response, noise keeps the contour above it only about half the time, so it breaks: streaking | S01 §VI | — |
| L25 | With hysteresis, isolated false points must exceed the high threshold, and a contour breaks only if it fluctuates from above the high threshold to below the low one | S01 §VI | — |
| L26 | Canny's implementation used a high-to-low ratio of two or three to one | S01 §VI | his implementation |
| L27 | Canny estimated noise from a global histogram of the operator output, arguing that the low percentiles, say below 80%, are set mainly by noise | S01 §VI | edges assumed rare |
| L28 | Canny defined an edge point as a maximum of the operator output along the direction of the smoothed gradient, with the smoothed gradient magnitude as its strength | S01 §VII | — |
| L29 | Canny's technical report suppresses a pixel unless it is strictly greater than both neighbours along the gradient, approximating the off-grid neighbours by linear interpolation of the two nearest grid values | S02 §2, eq. (4), quoting Canny's AI-TR-720 §5.3 | — |
| L30 | Canny's noise estimation, multiple scales and directional operators did not become part of the standard Canny detector | S02 §2 | — |
| L31 | Devernay's correction places the edge at the vertex of the parabola through the three magnitudes, an offset of one half of (A − C) over (A + C − 2B) | S02 §3, eq. (5) | B a strict local maximum |
| L32 | For slanted edges the interpolation of off-grid magnitudes is the main source of sub-pixel error, up to about five times the axis-aligned error for Gaussian edges of sigma 1 | S02 §4 | synthetic Gaussian edges |
| L33 | Hysteresis makes the result less sensitive to the threshold values, but their choice has no universal rule | S02 §9 | — |
| L34 | Without smoothing, edges on a noisy image come out fragmented; smoothing rounds corners and makes close contours interact | S02 §9 | their experiments |
| L35 | Single-threshold first-derivative detectors give discontinuous edges and respond to noise, and one threshold that suits a broad class of images is very hard to find | S03 §5, §6 | — |
| L36 | Canny's is by far the most popular differential edge operator | S04 §3.1 | 2011 |
| L37 | A threshold is easy to tune on one image and practically impossible to make universal; gradient histograms are rarely bimodal, so valley-seeking rarely applies; Bayesian methods model edge and non-edge distributions, most often as Rayleigh, chi-squared or gamma, but these fit poorly | S04 §8.2 | — |
| L38 | At junctions of three edges, Canny's suppression destroys connectivity, leaving a gap on the weaker edge; the authors call it false suppression | S05 abstract, §1 | T- and Y-junctions |
| L39 | A curve of length l whose weakest point has contrast µ is meaningful when the number of curves times H(µ) to the power l is at most ε, with H(µ) the image's fraction of pixels whose gradient is at least µ and the points treated as independent | S06 §2.1, eqs. (4)–(6) | ε = 1 in their experiments |
| L40 | The minimal contrast for a meaningful curve of length l is the inverse of H at (ε/N) to the power 1/l, so it falls as the curve gets longer | S06 §2.2, eq. (9) | — |
| L41 | Desolneux and colleagues found Canny's output strongly threshold-dependent: low thresholds mark flat regions, high ones give correct but broken edges | S06 §3.1 | their test images |
| L42 | Hancock and Kittler cast hysteresis as a Bayesian contextual decision whose thresholds follow from the parameters of an image model estimated from image statistics, and add a third threshold | S07 abstract | — |
| L43 | Henstock and Chelberg fit a weighted sum of two gamma densities to edge and non-edge gradient values to choose a threshold, and report thresholds close to human ones | S08 abstract | their 16 test images |
| L44 | `Canny` sends a UMat to an OpenCL kernel and first offers every other call to a platform HAL; the IPP HAL accepts it only when OpenCV runs on one thread, for single-channel images larger than 3×3 at aperture 3 or 5, and then runs IPP's own Canny with a replicate border; otherwise OpenCV's code runs | S09 canny.cpp `Canny()` (CV_OCL_RUN, CALL_HAL), hal/ipp/src/canny_ipp.cpp, ipp_hal_imgproc.hpp (IPP_DISABLE_PERF_CANNY_MT 1, commented that OpenCV's multithreaded Canny is faster) | builds with Intel IPP; IPP's own suppression is not in OpenCV's source |
| L45 | Release 4.10.0 has the same suppression rule and constant, the same replicate border and aperture-7 scaling, and its IPP path under the same one-thread condition | S13 canny.cpp, private.hpp | tag 4.10.0 |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S01 | Fig. 7 | What the thresholds select / L24, L25 | thresholding at T1, 2T1 and with hysteresis on one image shows streaking directly | IEEE copyright, no licence | https://doi.org/10.1109/TPAMI.1986.4767851 | do not reuse |
| F2 | S02 | Figure 1 | NMS / L29 | the support of Canny's suppression, A, B, C on the grid | CC BY-NC-SA (non-commercial) | https://www.ipol.im/pub/art/2017/216/article.pdf | do not reuse; Figure 5 draws our own case on the patch |
| F3 | S02 | Figures 19, 20 | Thresholds / L33 | hysteresis on a natural image at fixed L and fixed H | CC BY-NC-SA (non-commercial) | https://www.ipol.im/pub/art/2017/216/article.pdf | do not reuse |
| F4 | S05 | Figure 2 | NMS / L38 | the gap left on the weaker edge at a T-junction | BMVA archive, no licence stated | https://www.bmva-archive.org.uk/bmvc/1989/avc-89-021.pdf | do not reuse |

## Open questions

- Canny's AI-TR-720 was not read (DSpace 405). Its suppression scheme is cited through S02, which
  quotes it with the section number. Whether the report states a tie rule beyond "strictly
  greater" is not settled; the post attributes the strict test to S02's statement of it.
- MATLAB's automatic threshold rule is not documented beyond "heuristic"; forum posts give a 70%
  percentile, which is not citable. The post states only what MathWorks documents.
- OpenCV's Python tutorial and its source disagree on smoothing (L14 against L01). Reported in the
  manifest as a documentation issue; not raised upstream.
