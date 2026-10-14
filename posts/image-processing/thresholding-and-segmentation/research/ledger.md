# Source ledger — thresholding-and-segmentation

Series `image-processing`, part 11. Researched 2026-10-13, inline (no agents). The series is G0: every
library behaviour below is read from source at a pinned commit and replayed in plain Python; nothing
was run against an image.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Otsu, "A Threshold Selection Method from Gray-Level Histograms" | IEEE Transactions on Systems, Man, and Cybernetics 9(1):62–66 | 1979 | 10.1109/TSMC.1979.4310076 | peer-reviewed | https://engineering.purdue.edu/kak/computervision/ECE661.08/OTSU_paper.pdf | 2026-10-13 |
| S2 | T1 | Sezgin & Sankur, "Survey over image thresholding techniques and quantitative performance evaluation" | Journal of Electronic Imaging 13(1):146–165 | 2004 | 10.1117/1.1631315 | peer-reviewed | https://web.archive.org/web/20070820165409/http://www.busim.ee.boun.edu.tr/~sankur/SankurFolder/Threshold_survey.pdf | 2026-10-13 |
| S3 | T1 | Ershov, Korchagin, Kokhan & Bezmaternykh, "A generalization of Otsu method for linear separation of two unbalanced classes in document image binarization" | Computer Optics 45(1):66–76 | 2021 | 10.18287/2412-6179-CO-752 | peer-reviewed | http://computeroptics.ru/KO/PDF/KO45-1/450109.pdf | 2026-10-13 |
| S4 | T1 | Liu & Yu, "Otsu Method and K-means" (abstract only) | Int. Conf. on Hybrid Intelligent Systems (HIS), 344–349 | 2009 | 10.1109/HIS.2009.74 | peer-reviewed | https://doi.org/10.1109/HIS.2009.74 | 2026-10-13 |
| S5 | T1 | Sauvola & Pietikäinen, "Adaptive document image binarization" | Pattern Recognition 33(2):225–236 | 2000 | 10.1016/S0031-3203(99)00055-2 | peer-reviewed | https://web.archive.org/web/20191221223120/http://www.mediateam.oulu.fi/publications/pdf/24.pdf | 2026-10-13 |
| S6 | T1 | Vincent & Soille, "Watersheds in Digital Spaces: An Efficient Algorithm Based on Immersion Simulations" | IEEE Transactions on Pattern Analysis and Machine Intelligence 13(6):583–598 | 1991 | 10.1109/34.87344 | peer-reviewed | https://people.cmm.minesparis.psl.eu/users/marcoteg/cv/publi_pdf/MM_refs/vincent/1991_PAMI_VincentSoille_watershed.pdf | 2026-10-13 |
| S7 | T1 | Roerdink & Meijster, "The Watershed Transform: Definitions, Algorithms and Parallelization Strategies" | Fundamenta Informaticae 41(1–2):187–228 | 2000 | 10.3233/FI-2000-411207 | peer-reviewed | https://web.archive.org/web/20221110134657/https://www.cs.rug.nl/~roe/publications/parwshed.pdf | 2026-10-13 |
| S8 | T1 | Najman & Schmitt, "Geodesic saliency of watershed contours and hierarchical segmentation" (abstract only) | IEEE TPAMI 18(12):1163–1173 | 1996 | 10.1109/34.546254 | peer-reviewed | https://doi.org/10.1109/34.546254 | 2026-10-13 |
| S9 | T1 | Haris, Efstratiadis, Maglaveras & Katsaggelos, "Hybrid image segmentation using watersheds and fast region merging" (abstract only) | IEEE Transactions on Image Processing 7(12):1684–1699 | 1998 | 10.1109/83.730380 | peer-reviewed | https://doi.org/10.1109/83.730380 | 2026-10-13 |
| S10 | T1 | Cousty, Bertrand, Najman & Couprie, "Watershed Cuts: Minimum Spanning Forests and the Drop of Water Principle" (abstract only) | IEEE TPAMI 31(8):1362–1374 | 2009 | 10.1109/TPAMI.2008.173 | peer-reviewed | https://doi.org/10.1109/TPAMI.2008.173 | 2026-10-13 |
| S11 | T4 | Beucher, "The Watershed Transformation page", Centre de Morphologie Mathématique (archived; linked by OpenCV's tutorial and scikit-image's docstring) | — | 2018 snapshot | — | practitioner | https://web.archive.org/web/20180702213110/http://cmm.ensmp.fr/~beucher/wtshed.html | 2026-10-13 |
| S12 | T3 | OpenCV source, commit 802cf95: `thresh.cpp`, `segmentation.cpp`, `smooth.dispatch.cpp`, `fixedpoint.inl.hpp`, `imgproc.hpp`, `hal/ipp/src/threshold_ipp.cpp`, `hal/riscv-rvv/src/imgproc/threshold.cpp`, `test/test_thresh.cpp`, `CMakeLists.txt`, `doc/opencv.bib` | — | 2026 | commit 802cf95aa3d42816995695bf68a86b3532f12760 | source | https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760 | 2026-10-13 |
| S13 | T3 | OpenCV source, tags 4.10.0, 4.11.0, 4.12.0: `thresh.cpp`, `segmentation.cpp`, `smooth.dispatch.cpp`, `fixedpoint.inl.hpp`, `imgproc.hpp` | — | 2024–2025 | tags 4.10.0, 4.11.0, 4.12.0 | source | https://github.com/opencv/opencv/tree/4.10.0/modules/imgproc | 2026-10-13 |
| S14 | T2 | OpenCV Python tutorials at 802cf95: "Image Thresholding" and "Image Segmentation with Watershed Algorithm" | — | 2026 | commit 802cf95 | official-docs | https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760/doc/py_tutorials/py_imgproc | 2026-10-13 |
| S15 | T3 | scikit-image source, commit b700edc: `filters/thresholding.py`, `filters/edges.py`, `segmentation/_watershed.py`, `segmentation/_watershed_cy.pyx`, `morphology/extrema.py` | — | 2026 | commit b700edc8005e4ee9e74fc83259f09e8df3213f15 | source | https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2 | 2026-10-13 |
| S16 | T3 | scikit-image release v0.25.0 notes (PR #7071) and `_watershed_cy.pyx` at v0.24.0 and v0.25.0 | — | 2024 | tags v0.24.0, v0.25.0; PR 7071 | source | https://github.com/scikit-image/scikit-image/releases/tag/v0.25.0 | 2026-10-13 |
| S17 | T2 | MathWorks Image Processing Toolbox documentation, release R2026b: `graythresh`, `imbinarize`, `adaptthresh`, `watershed` | — | 2026 | R2026b | official-docs | https://www.mathworks.com/help/images/ref/graythresh.html | 2026-10-13 |
| S18 | T3 | Part 1 of this series, *Image Processing by Hand* (published), its decide-stage section | canery.in | 2026 | — | source | https://canery.in/blogs/image-processing-by-hand | 2026-10-13 |

Peer-reviewed with an identifier: S1–S10 (ten; L3 floor seven). S4, S8, S9 and S10 were read as
abstracts only (OpenAlex), and every claim on them says no more than the abstract.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search "image thresholding techniques survey", by citations | Sezgin & Sankur 2004 (4,583 citations) — the survey; nothing else close |
| 2 | 1 | OpenAlex | title.search "watershed transform definitions algorithms" | Roerdink & Meijster 2000 (1,376 citations) — the watershed survey, with an open repository copy |
| 3 | 1 | OpenAlex | title.search for Otsu 1979, Vincent & Soille 1991, Sauvola 2000, Kittler & Illingworth 1986, Kurita 1992, Xu 2011, Ridler & Calvard 1978, Zack 1977, Meyer 1994, Meyer & Beucher 1990, Cousty 2009, Rosin 2001, Glasbey 1993, Chow & Kaneko 1972 | venues, DOIs and citation counts for all fourteen; no open copies except Zack (SAGE) and Cousty (HAL) |
| 4 | 1 | Unpaywall | the fourteen DOIs above | open copies only for Roerdink & Meijster (rug.nl, Cloudflare wall), Zack (SAGE, 403 to curl and WebFetch) and Cousty (HAL, Anubis wall) |
| 5 | 1 | Google Scholar (curl) | "watersheds in digital spaces" vincent soille | an author-hosted PDF at people.cmm.minesparis.psl.eu — read in full |
| 6 | 1 | Google Scholar (curl) | "adaptive document image binarization" sauvola | only the 1997 ICDAR version on ResearchGate (bot wall); not the journal paper |
| 7 | 1 | Wayback Machine | cs.rug.nl/~roe/publications/parwshed.pdf; mediateam.oulu.fi/publications/pdf/24.pdf | both archived author copies — Roerdink & Meijster and Sauvola & Pietikäinen read in full |
| 8 | 1 | Wayback Machine (CDX) | busim.ee.boun.edu.tr/~sankur/SankurFolder/Threshold_survey.pdf (the link in scikit-image's isodata docstring) | Sankur's own copy of the survey, 2004–2007 snapshots — read in full |
| 9 | 1 | Semantic Scholar | DOIs of Kurita 1992, Xu 2011, Kittler & Illingworth 1986, Ridler & Calvard 1978, Rosin 2001, Glasbey 1993 | metadata only; Elsevier and IEEE abstracts withheld |
| 10 | 1 | Google Scholar (curl) | quoted titles of Kittler & Illingworth, Kurita, Xu 2011, Rosin 2001 | only papers citing them; no author copies |
| 11 | 1 | Google Scholar (curl) | "maximum likelihood thresholding based on population mixture models" | Ershov et al. 2021 (Computer Optics, open) — states Kurita et al.'s three cases with equations; read in full |
| 12 | 1 | Crossref | 10.18287/2412-6179-CO-752 | volume, issue and the publisher's PDF link for Ershov et al. |
| 13 | 1 | OpenAlex | cites:Otsu 1979 + title.search "otsu" | Xu 2011, Liu & Yu 2009 ("Otsu Method and K-means"), multilevel variants — forward chase |
| 14 | 1 | OpenAlex | cites:Otsu 1979 + "valley emphasis"; + "bias" | the valley-emphasis line (Fan & Lei 2011) for small objects; nothing on bias in titles |
| 15 | 1 | OpenAlex | cites:Vincent & Soille 1991 + title.search "watershed" | Roerdink & Meijster, Haris 1998, Najman & Schmitt 1996, Cousty 2009 — forward chase |
| 16 | 1 | OpenAlex | abstracts by DOI: Liu & Yu 2009, Najman & Schmitt 1996, Haris 1998, Cousty 2009, Fan & Lei 2011, Magid 1990 | four usable IEEE abstracts; Elsevier withheld |
| 17 | 2 | WebSearch | Kittler Illingworth 1986 "minimum error thresholding" pdf | first-page scans only; the paper's method is cited through the survey (S2) |
| 18 | 2 | Europe PMC | DOI 10.1177/25.7.70454 (Zack 1977) | abstract only, which does not describe the triangle rule; the rule is cited from OpenCV and scikit-image source |
| 19 | 5 | GitHub raw / trees API | OpenCV 802cf95: thresh.cpp, segmentation.cpp, hal/*/ for threshold, imgproc.hpp, opencv.bib | Otsu loop, IPP call, RVV HAL, watershed (Meyer 1992), the −1 frame |
| 20 | 5 | GitHub raw | OpenCV 4.10.0, 4.11.0, 4.12.0 | 4.10.0 has the same Otsu loop and watershed; THRESH_DRYRUN and thresholdWithMask arrive in 4.12.0 |
| 21 | 5 | GitHub raw | OpenCV 802cf95 and 4.10.0 smooth.dispatch.cpp, fixedpoint.inl.hpp, smooth.simd.hpp | 8-bit GaussianBlur is fixed point: kernel [61, 134, 61]/256 for σ = 0.8 |
| 22 | 5 | GitHub raw / API | scikit-image b700edc thresholding, edges, watershed; v0.24.0 vs v0.25.0 `_watershed_cy.pyx`; v0.25.0 release notes | the cost clamp and PR #7071 |
| 23 | 5 | WebFetch | MathWorks graythresh, imbinarize, adaptthresh, watershed (curl gets an Akamai 403) | R2026b behaviour and defaults |
| 24 | 6 | GitHub raw | OpenCV py_thresholding and py_watershed tutorials | the coins pipeline; boundaries −1; no mention of the frame |
| 25 | 4 | (by computation) | Otsu's unimodality remark tested on a four-spike histogram and on mixtures | counterexamples: two local maxima (6,966 / 6,320 / 6,967 on 0, 120, 135, 255; and 99:1 and three-hump mixtures) |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Otsu picks the threshold that maximises the between-class variance; three criteria (λ, κ, η) are equivalent because σ_W² + σ_B² = σ_T² for every threshold | S1 §II eq. 12–16 | two classes, one histogram |
| L02 | Otsu's classes for a threshold at level k are levels 1 to k and k + 1 to L | S1 §II | — |
| L03 | The search needs only the zeroth- and first-order cumulative moments of the histogram, evaluated at every k | S1 §II eq. 17–19 | — |
| L04 | η at the optimum measures separability or bimodality; it is invariant to affine grey-level changes, 0 only for a one-level image and 1 only for a two-valued image | S1 §III-A | — |
| L05 | Otsu extends the criterion to several thresholds and warns that the thresholds become less credible as classes are added | S1 §III-B | — |
| L06 | Otsu's paper says the ideal histogram has a deep, sharp valley between two peaks, and that broad valleys and very unequal peaks make the valley hard to find | S1 §I | — |
| L07 | Otsu reported the criterion as smooth and unimodal in his experiments but had no proof | S1 §III-D | his examples |
| L08 | The survey groups thresholding methods into six families by the information they use: histogram shape, clustering, entropy, object attributes, spatial and local | S2 §2 | — |
| L09 | Sezgin & Sankur describe Otsu as satisfactory when the two classes have similar numbers of pixels | S2 §4 | — |
| L10 | Minimum-error methods model the histogram as a mixture of two Gaussians; Kittler & Illingworth drop the equal-variance assumption | S2 §4 | — |
| L11 | On 40 degraded document images, Kittler–Illingworth ranked 1st, Sauvola 2nd, Otsu 17th and Niblack 29th of 40 methods; on 40 NDT images Kittler–Illingworth 1st, Otsu 6th and Sauvola 38th | S2 Tables 7–8 | their images and five combined measures |
| L12 | The survey's document comparison covers noise and blur; non-uniform illumination and shadow were outside its scope | S2 §10 | — |
| L13 | Kurita, Otsu & Abdelmalek derived threshold criteria as maximum likelihood for a mixture of two normals: equal weights and equal variances give Otsu's criterion; free weights and variances give Kittler–Illingworth; free weights with equal variances give an "unbalanced" Otsu criterion | S3 §2–3 eq. 4–6 | as Ershov et al. summarise Kurita 1992 |
| L14 | Ershov et al. describe Kittler–Illingworth as widely known to be unstable, with too many degrees of freedom for a histogram method | S3 §2 | — |
| L15 | Otsu's objective equals k-means' within-class variance; Otsu searches every threshold for the global optimum, while k-means finds a local one | S4 abstract | one-dimensional data |
| L16 | Niblack's threshold is the local mean plus k times the local standard deviation, with negative k, and it struggles on lightly textured backgrounds | S5 §3.3 | — |
| L17 | Sauvola's threshold is m(1 + k(s/R − 1)) with R the dynamic range of the standard deviation; the paper used R = 128 and k = 0.5 on 8-bit images and found it insensitive to k | S5 §3.3 eq. 5 | text regions |
| L18 | The mean factor lowers Sauvola's threshold in low-contrast background areas, which removes stains | S5 §3.3 | dark text on a light background |
| L19 | Sauvola's paper is a hybrid: it classifies windows (10–20 px tiles) and applies a soft-decision method to non-text regions; libraries implement only the text formula | S5 §2–3.1; S15 | — |
| L20 | Vincent & Soille define watersheds by immersion: holes in each regional minimum, the surface lowered into water, dams built where water from two minima meets | S6 §II-C | — |
| L21 | Their algorithm sorts the pixels by grey level, then floods level by level with a FIFO queue | S6 §III | — |
| L22 | Watersheds of a gradient mostly over-segment, whatever gradient is used, even after filtering; the over-segmentation is often due to noise | S6 §V-A | — |
| L23 | Two remedies: remove irrelevant contours (merge regions), or modify the gradient so its only minima are markers of the desired regions | S6 §V-A | — |
| L24 | A marker is a connected set of pixels, possibly one pixel, inside a region; markers are imposed as minima and all other minima are filled | S6 §V-A | — |
| L25 | Touching binary objects are separated by the watershed of the negated distance function | S6 §V-A | binary images |
| L26 | The watershed transform is usually applied to the gradient, not to the image | S7 §1 | — |
| L27 | Definitions, specifications and implementations of the watershed often disagree, and speed-ups change outcomes in ways that go unnoticed on natural images | S7 §1 | — |
| L28 | In its original form the watershed severely over-segments because of the many minima; markers and hierarchical watersheds are the remedies | S7 §1 | — |
| L29 | The Vincent–Soille algorithm does not implement its own recursive definition | S7 §4.1 | — |
| L30 | Ordered-queue algorithms assign plateau pixels in ways that may differ from the definition, and some results depend on the order pixels are processed | S7 §1, §3 | — |
| L31 | Watershed results change with the connectivity used | S7 Fig. 2 | — |
| L32 | Najman & Schmitt measure a minimum's contrast by its dynamics, proposed to prevent over-segmentation, and extend it to contours to build a hierarchy of segmentations | S8 abstract | — |
| L33 | A hybrid scheme takes the watershed of the gradient as primitive regions and merges them bottom-up on a region adjacency graph | S9 abstract | — |
| L34 | Cousty et al. define watershed cuts on edge-weighted graphs, prove them equivalent to minimum spanning forests, and give a linear-time algorithm | S10 abstract | — |
| L35 | Beucher frames marker-controlled watershed as two steps: choose markers and a criterion, then flood from the markers; markers may be drawn by hand | S11 | framing only |
| L36 | `cv::threshold` with THRESH_BINARY sets maxval where src > thresh; THRESH_OTSU accepts 8-bit and 16-bit single-channel images, THRESH_TRIANGLE only 8-bit; the computed threshold is returned | S12 imgproc.hpp, thresh.cpp | — |
| L37 | OpenCV's own Otsu loop scans levels 0–255 and keeps the first level whose between-class variance is strictly larger | S12 thresh.cpp getThreshVal_Otsu | non-IPP path |
| L38 | For 8-bit images without a mask, OpenCV first asks Intel IPP (`ippiComputeThreshold_Otsu_8u_C1R`, IPP ≥ 2018); IPP's threshold HAL covers only TRUNC, TOZERO and TOZERO_INV; the RISC-V vector HAL has its own Otsu | S12 thresh.cpp, hal/ipp/src/threshold_ipp.cpp, hal/riscv-rvv | — |
| L39 | OpenCV builds with IPP by default on x86 | S12 CMakeLists.txt WITH_IPP | not MinGW, optimisations on |
| L40 | OpenCV's Otsu test checks the output against a reference that applies the same strict-maximum rule | S12 test_thresh.cpp | random images |
| L41 | OpenCV's triangle method finds the histogram peak, takes the longer tail, and maximises the distance below the line from the peak to the tail's end, then subtracts one | S12 thresh.cpp getThreshVal_Triangle_8u | — |
| L42 | `adaptiveThreshold` compares each pixel with the box mean (rounded to 8 bits) or a Gaussian-weighted mean minus C over a blockSize window, with a replicate border; C is rounded up for THRESH_BINARY | S12 thresh.cpp, imgproc.hpp | 8-bit input |
| L43 | `cv::watershed` needs an 8-bit 3-channel image and 32-bit markers; it floods from the markers in order of the largest channel difference between 4-neighbours, first in first out within a level; a pixel that touches two labels becomes −1 and stops the flood; the outer one-pixel frame is set to −1 | S12 segmentation.cpp | — |
| L44 | OpenCV attributes its watershed to Meyer's 1992 "Color image segmentation" | S12 imgproc.hpp, opencv.bib | — |
| L45 | Release 4.10.0 has the same Otsu loop, IPP call, triangle method and watershed as 802cf95; THRESH_DRYRUN and `thresholdWithMask` first appear in 4.12.0 | S13 | — |
| L46 | OpenCV's 8-bit GaussianBlur is fixed point: the 1-D kernel is quantised to 8 fraction bits by error diffusion, and the result rounds half up; IPP is not used on this path | S12, S13 smooth.dispatch.cpp, fixedpoint.inl.hpp | sigma > 0, default algorithm hint |
| L47 | OpenCV's watershed tutorial builds markers by Otsu, opening, dilation for sure background, a distance-transform threshold at 0.7 of its maximum for sure foreground, and labels the rest 0; boundaries come back as −1 | S14 | — |
| L48 | scikit-image's `threshold_otsu` returns t with foreground = image > t, uses one bin per integer level from min to max for integer images, and takes the first maximum | S15 | integer images |
| L49 | `threshold_isodata` (Ridler–Calvard) returns the lowest t equal, to within one level, to the mean of the means below and above it | S15 | integer images |
| L50 | `threshold_triangle` credits Zack, Rogers & Latt (1977) and implements the same peak-to-tail line rule | S15 | — |
| L51 | `threshold_niblack` computes m − k·s with k = 0.2, and `threshold_sauvola` computes m(1 + k(s/r − 1)) with k = 0.2 and r half the dtype range, both over a centred 15×15 window by default with reflect padding | S15 | — |
| L52 | `filters.sobel` is the root mean square of [1, 0, −1] × [1, 2, 1]/4 responses on the image as floats 0–1, with scipy's 'reflect' border | S15 edges.py | — |
| L53 | scikit-image's `watershed` defaults to 4-connectivity, uses the local minima as markers when none are given, orders its queue by value then age, and labels a pixel when it is queued unless compactness or watershed lines are requested | S15 | — |
| L54 | Since v0.25.0, a queued pixel's cost is at least the cost of the pixel that queued it, fixing results when markers do not sit at minima (PR #7071); v0.24.0 lacks this | S16 | — |
| L55 | MATLAB's `graythresh` uses Otsu's method on a 256-bin histogram, returns a level from 0 to 1 and an effectiveness metric from 0 to 1 with the same bounds as Otsu's η | S17 | R2026b |
| L56 | `imbinarize` defaults to global Otsu; its adaptive mode is Bradley's local-mean method with sensitivity 0.5 and a window of about one-eighth of the image | S17 | R2026b |
| L57 | MATLAB's `watershed` uses Meyer's algorithm, defaults to 8-connectivity, labels pixels that belong to no single region 0, and recommends removing shallow minima with `imhmin` to prevent over-segmentation | S17 | R2026b |
| L58 | Part 1 stated Otsu's criterion and that it is a search over 256 candidates, and named this spoke *Thresholding and segmentation* | S18 | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S1 | Fig. 2 (textures, a broad valley and a unimodal peak with η) | histogram shapes / L06–L07 | shows real histograms where a threshold struggles | IEEE copyright, no licence | S1 URL | do not reuse |
| F2 | S6 | Fig. 16 (watersheds of a gradient, markers, final segmentation) | over-segmentation / L22–L24 | the classic before and after of markers | IEEE copyright, no licence | S6 URL | do not reuse |
| F3 | S7 | Fig. 2 (watershed on a square grid with 4- and 8-connectivity) | definitions / L31 | connectivity changes the result | IOS Press copyright, no licence stated on the author copy | S7 URL | do not reuse |
| F4 | S5 | Fig. 12 (comparison on illuminated text) | local thresholds / L16–L18 | shows Niblack against Sauvola | Elsevier copyright | S5 URL | do not reuse |

No `source` figure; every figure is computed on the series' patch or from closed forms.

## Open questions

- **IPP's Otsu tie rule.** On a histogram with an empty gap the criterion is flat across the gap;
  OpenCV's own code returns the gap's first level, and IPP's rule is not public. The binary output
  should match (L40), the returned number may not. Owner check listed in the manifest.
- **Otsu's unimodality remark (L07)** is contradicted by our own computations (four-spike histogram,
  99:1 and three-hump mixtures). No published counterexample was located in this sweep; the post
  shows ours and does not claim a citation for it.
- **Part 1's histogram counts.** Part 1 (published) gives the patch's histogram as 16 pixels at 40 and
  8 at 200; the patch has 14 and 10 (sum 2,815). Its conclusion, a flat criterion from 41 to 199,
  holds. Reported to the owner, not edited.
- Kurita et al. (1992), Kittler & Illingworth (1986), Xu et al. (2011), Ridler & Calvard (1978) and
  Zack et al. (1977) were located but not readable; the post cites Kurita's result through Ershov
  et al. (S3), Kittler–Illingworth through the survey (S2), Ridler–Calvard and Zack only as the
  methods scikit-image credits.
