# Source ledger — mathematical-morphology

Series `image-processing`, part 12. Researched 2026-10-14, inline (no agents). The series is G0: every
library behaviour below is read from source at a pinned commit or tag, or from the vendor's
documentation, and replayed in plain Python; nothing was run against an image.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Heijmans & Ronse, "The algebraic basis of mathematical morphology I. Dilations and erosions" (read as CWI report AM-R8807, June 1988, the submitted version) | Computer Vision, Graphics, and Image Processing 50(3):245–295 | 1990 | 10.1016/0734-189X(90)90148-O | peer-reviewed | https://ir.cwi.nl/pub/5977/5977D.pdf | 2026-10-14 |
| S2 | T1 | Heijmans, "Mathematical Morphology: A Modern Approach in Image Processing Based on Algebra and Geometry" (survey; journal version on the CWI repository) | SIAM Review 37(1):1–36 | 1995 | 10.1137/1037001 | peer-reviewed | https://ir.cwi.nl/pub/2230/2230D.pdf | 2026-10-14 |
| S3 | T1 | Serra & Vincent, "An overview of morphological filtering" (tutorial; author copy) | Circuits, Systems and Signal Processing 11(1):47–108 | 1992 | 10.1007/BF01189221 | peer-reviewed | https://web.archive.org/web/2006id_/http://www.vincent-net.com/luc/papers/92cssp_filtering.pdf | 2026-10-14 |
| S4 | T1 | Vincent, "Morphological Grayscale Reconstruction in Image Analysis: Applications and Efficient Algorithms" (author copy) | IEEE Transactions on Image Processing 2(2):176–201 | 1993 | 10.1109/83.217222 | peer-reviewed | https://web.archive.org/web/2006id_/http://www.vincent-net.com/luc/papers/93ieeeip_recons.pdf | 2026-10-14 |
| S5 | T1 | Haralick, Sternberg & Zhuang, "Image Analysis Using Mathematical Morphology" (tutorial; author-hosted copy) | IEEE Transactions on Pattern Analysis and Machine Intelligence 9(4):532–550 | 1987 | 10.1109/TPAMI.1987.4767941 | peer-reviewed | http://haralick.org/journals/04767941.pdf | 2026-10-14 |
| S6 | T1 | Maragos & Schafer, "Morphological filters — Part II: Their relations to median, order-statistic, and stack filters" (abstract only) | IEEE Transactions on Acoustics, Speech, and Signal Processing 35(8):1170–1184 | 1987 | 10.1109/TASSP.1987.1165254 | peer-reviewed | https://doi.org/10.1109/TASSP.1987.1165254 | 2026-10-14 |
| S7 | T1 | Maragos, "Pattern spectrum and multiscale shape representation" (abstract only) | IEEE Transactions on Pattern Analysis and Machine Intelligence 11(7):701–716 | 1989 | 10.1109/34.192465 | peer-reviewed | https://doi.org/10.1109/34.192465 | 2026-10-14 |
| S8 | T1 | Rivest, Soille & Beucher, "Morphological gradients" (abstract only) | Journal of Electronic Imaging 2(4):326–336 | 1993 | 10.1117/12.159642 | peer-reviewed | https://doi.org/10.1117/12.159642 | 2026-10-14 |
| S9 | T1 | Heijmans, "Theoretical aspects of gray-level morphology" (abstract only) | IEEE Transactions on Pattern Analysis and Machine Intelligence 13(6):568–582 | 1991 | 10.1109/34.87343 | peer-reviewed | https://doi.org/10.1109/34.87343 | 2026-10-14 |
| S10 | T3 | OpenCV source, commit 802cf95: `modules/imgproc/src/morph.dispatch.cpp`, `morph.simd.hpp`, `hal_replacement.hpp`, `include/opencv2/imgproc.hpp`; the HAL headers `hal/carotene/hal/tegra_hal.hpp`, `hal/openvx/hal/openvx_hal.hpp`, `hal/riscv-rvv/include/imgproc.hpp`, `hal/ipp/include/ipp_hal_imgproc.hpp`, `hal/fastcv/include/fastcv_hal_imgproc.hpp` | — | 2026 | commit 802cf95aa3d42816995695bf68a86b3532f12760 | source | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src/morph.dispatch.cpp | 2026-10-14 |
| S11 | T3 | OpenCV source, tags 4.10.0, 4.11.0 and 4.12.0: `morph.dispatch.cpp`, `imgproc.hpp` | — | 2024–2025 | tags 4.10.0, 4.11.0, 4.12.0 | source | https://github.com/opencv/opencv/blob/4.10.0/modules/imgproc/src/morph.dispatch.cpp | 2026-10-14 |
| S12 | T2 | OpenCV Python tutorial "Morphological Transformations" at commit 802cf95 | — | 2026 | commit 802cf95 | official-docs | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/doc/py_tutorials/py_imgproc/py_morphological_ops/py_morphological_ops.markdown | 2026-10-14 |
| S13 | T3 | OpenCV issue #23605, "Morphological openings are not anti extensive (because dilation or opening is not well implemented)", opened 2023-05-11, open on the access date | — | 2023 | issue 23605 | source | https://github.com/opencv/opencv/issues/23605 | 2026-10-14 |
| S14 | T3 | scikit-image source, commit b700edc: `src/skimage/morphology/gray.py`, `binary.py`; `src/_skimage2/morphology/_grayscale_operators.py`, `binary.py`, `footprints.py`, `grayreconstruct.py`, `extrema.py` | — | 2026 | commit b700edc8005e4ee9e74fc83259f09e8df3213f15 | source | https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src | 2026-10-14 |
| S15 | T3 | scikit-image releases v0.26.0 (2025-12-20) and v0.25.2: `morphology/gray.py`, `morphology/binary.py` | — | 2025 | tags v0.26.0, v0.25.2 | source | https://github.com/scikit-image/scikit-image/blob/v0.26.0/src/skimage/morphology/gray.py | 2026-10-14 |
| S16 | T3 | scikit-image issue #6676, "Morphological closing and opening are incorrect", opened 2023-01-18, closed 2023-11-07 | — | 2023 | issue 6676 | source | https://github.com/scikit-image/scikit-image/issues/6676 | 2026-10-14 |
| S17 | T3 | SciPy source, tag v1.18.1: `scipy/ndimage/_morphology.py`, `scipy/ndimage/src/ni_morphology.c` | — | 2026 | tag v1.18.1 | source | https://github.com/scipy/scipy/blob/v1.18.1/scipy/ndimage/_morphology.py | 2026-10-14 |
| S18 | T2 | MathWorks Image Processing Toolbox documentation, release R2026b: `imdilate`, `imerode`, `imopen`, `strel`, `imtophat`, `imreconstruct`, "Morphological Dilation and Erosion" | — | 2026 | R2026b | official-docs | https://www.mathworks.com/help/images/ref/imdilate.html | 2026-10-14 |
| S19 | T3 | Part 1 of this series, *Image Processing by Hand* (published): its stage-4 morphology section, Figure 10, and Figure 7's caption | canery.in | 2026 | — | source | https://canery.in/blogs/image-processing-by-hand | 2026-10-14 |

Peer-reviewed with an identifier: S1–S9 (nine; L3 floor seven). S1 was read in its 1988 report
version and every claim on it was checked against statements that the 1990 paper's abstract and the
1995 survey (S2) also make; S6, S7, S8 and S9 were read as abstracts only (OpenAlex), and every claim
on them says no more than the abstract.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search "mathematical morphology survey", "… overview", "morphological filtering overview", "… tutorial", by citations | Serra & Vincent 1992 (406 citations) and Serra 1994 as the overviews; a 2014 adaptive-morphology survey, off topic |
| 2 | 1 | OpenAlex | title.search "algebraic basis of mathematical morphology", "why mathematical morphology needs complete lattices", "image analysis using mathematical morphology" | Heijmans & Ronse 1990 (409) with an open CWI report copy (1988); Ronse & Heijmans 1991; Ronse 1990 (Elsevier, no copy); Haralick et al. 1987 (2,709) |
| 3 | 1 | OpenAlex | search "algebraic basis mathematical morphology openings closings" | Heijmans 1995, SIAM Review — the survey, open on the CWI repository; a 1987 CWI report |
| 4 | 1 | CWI repository | ir.cwi.nl/pub/5977 and /2230 | both read in full: the Heijmans & Ronse report and the SIAM Review survey |
| 5 | 1 | OpenAlex | title.search Maragos & Schafer I and II, "pattern spectrum", "morphological grayscale reconstruction", "grayscale morphology", Meyer 1979, Soille 1999 handbook, Serra 1982, Matheron 1975, "morphological image operators" | venues and DOIs for all; no open copies; the three books are not accessible |
| 6 | 1 | Google Scholar (curl) | "algebraic basis of mathematical morphology" "openings and closings" | only the Part I CWI report and an unrelated CWI paper; Part II (Ronse & Heijmans 1991) has no open copy |
| 7 | 1 | Google Scholar (curl) | Maragos Part II; "pattern spectrum and multiscale shape representation"; "morphological grayscale reconstruction in image analysis" | no Maragos copies; a pointer to Luc Vincent's archived publication page |
| 8 | 1 | Wayback Machine | vincent-net.com/luc/papers/ (2006 snapshot) | author copies of Vincent 1993 and Serra & Vincent 1992 — both read in full |
| 9 | 1 | Google Scholar (curl) | "image analysis using mathematical morphology" haralick sternberg zhuang | Haralick's own site hosts the 1987 tutorial (haralick.org/journals/04767941.pdf) — read in full |
| 10 | 1 | OpenAlex | cites:W2170949105 (forward chase from Heijmans & Ronse 1990), then + title.search "bounded", "border" | Serra & Vincent 1992, Heijmans 1991 (grey-level), Jackway & Deriche 1996, Ronse 1990; nothing on border effects or on bounded domains |
| 11 | 1 | Semantic Scholar | citations of Heijmans 1995 (DOI 10.1137/1037001), 100 most-cited | applications and a 2002 paper on rank-based morphological operators; no correction to the adjunction results |
| 12 | 1 | OpenAlex | abstracts by DOI: Maragos & Schafer I and II, Maragos 1989, Meyer 1979, Rivest et al. 1993, Heijmans 1991, Ronse 1990 | usable IEEE and SPIE abstracts; Meyer's does not mention the top-hat; Ronse 1990 (Elsevier) withheld |
| 13 | 1 | Crossref | DOIs of Heijmans 1995, Serra & Vincent 1992, Heijmans & Ronse 1990 | volume, issue and page ranges confirmed for all three |
| 14 | 6 | Mines Paris CMM | smil.cmm.minesparis.psl.eu/publis/Cours-Serra/ | Serra's 2000 course slides, chapters I–X; used for orientation only (slide text is doubled by the PDF layers) |
| 15 | 4 | GitHub issues | repo:opencv/opencv "morphological closing not extensive"; "morphologyEx asymmetric kernel"; "dilate kernel reflected" | issue #23605, open since 2023-05-11, with a reproducible example |
| 16 | 4 | GitHub issues | scikit-image issue 6676 | the same defect, fixed in 2023 by mirroring inside opening and closing |
| 17 | 5 | GitHub raw | OpenCV 802cf95 morph.dispatch.cpp, morph.simd.hpp, imgproc.hpp, hal_replacement.hpp | erode and dilate share unreflected offsets; border values; IPP compiled out; iterations and the rectangle merge |
| 18 | 5 | GitHub raw | OpenCV 4.10.0, 4.11.0, 4.12.0 morph.dispatch.cpp, imgproc.hpp | the same code in all three; IPP compiled out in all; MORPH_DIAMOND from 4.12.0 |
| 19 | 5 | GitHub API and raw | scikit-image b700edc morphology tree; releases list; v0.26.0 and v0.25.2 gray.py and binary.py | v0.26.0 is the latest release; mirroring inside opening and closing; skimage2 drops it at b700edc |
| 20 | 5 | GitHub raw | SciPy v1.18.1 (latest release) _morphology.py, ni_morphology.c; issue search "binary_closing border" | border_value defaults to 0 and is the value assumed outside the input; no issue about extensivity |
| 21 | 5 | WebFetch | MathWorks R2026b imdilate, imerode, imopen, strel, imtophat, imreconstruct, "Morphological Dilation and Erosion" (curl gets an Akamai 403; the border-padding page returned 404) | imdilate reflects the element; ±∞ outside the image; exact disks unsuitable for granulometries |
| 22 | 6 | GitHub raw | OpenCV py_morphological_ops tutorial at 802cf95 | the printed 5×5 ellipse, cross and diamond; plain-language uses of each operator |
| 23 | 4 | (by computation) | the adjunction under two border rules on random pairs; OpenCV's composition with a 2×2 element; issue #23605's example replayed | 0 and 616 failures on the same 20,000 pairs; a closing that loses five pixels; the issue's output reproduced exactly |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | A complete lattice is a partial order in which every subset, the empty one included, has a supremum and an infimum; the subsets of a set under inclusion (union, intersection) and functions under the pointwise order (max, min) are complete lattices | S1 §1.3; S2 §3, §6.1 | — |
| L02 | A dilation is an operator that commutes with suprema of every family, so it maps the empty set to itself; an erosion commutes with infima; the general definition is Serra's | S1 Def. 2.1 | — |
| L03 | Minkowski dilation distributes over unions and erosion over intersections; for the erosion of a union only containment holds | S2 eq. 2.7–2.8; S5 Prop. 15, 27 | — |
| L04 | Dilation and erosion by the same element satisfy X ⊕ B ⊆ Y if and only if X ⊆ Y ⊖ B, the adjunction | S1 eq. 1.6, Def. 2.2; S2 eq. 2.14 | Minkowski operations; erosion written without reflection |
| L05 | In an adjunction the lower map is a dilation and the upper an erosion; every dilation has exactly one adjoint erosion and every erosion one adjoint dilation; Serra called this morphological duality, and it is a Galois connection | S1 Prop. 2.5, Thm. 2.7, §2.3.2 | — |
| L06 | From the adjunction: εδ is extensive, δε is anti-extensive, δεδ = δ and εδε = ε, so opening and closing are idempotent | S1 Prop. 2.6, 2.8; S2 eq. 2.15–2.18; S5 Prop. 37, 39, Thm. 38, 40 | — |
| L07 | Minkowski addition and subtraction are the only translation-invariant dilations and erosions of a Euclidean or digital space | S1 §1.2, §3 | — |
| L08 | The opening by B is the union of all translates of B contained in X; it removes narrow parts of a set, and closing fills narrow holes | S1 §1.1.3; S2 eq. 2.19 | — |
| L09 | An algebraic opening is increasing, idempotent and anti-extensive, a closing increasing, idempotent and extensive; a union of openings is an opening; in morphology "filter" means increasing and idempotent | S2 Def. 2.3, §2.3; S3 §1.1 | — |
| L10 | The filter axiomatics (increasing and idempotent) are due to Serra in 1982 | S3 §1.1 | — |
| L11 | Matheron proved that every increasing translation-invariant set operator is a union of erosions, and dually an intersection of dilations | S2 Thm. 2.2; S1 §2.2 eq. 2.6 | sets on Euclidean or digital space |
| L12 | The rank-k operator over a window is the supremum of the erosions by all k-point subsets of the window; k = (p + 1)/2 gives the median | S3 §3.5.3 eq. 56; S2 §2.4 | finite symmetric window of p points |
| L13 | Any median or order-statistic filter equals a maximum of erosions and a minimum of dilations | S6 abstract | — |
| L14 | The complement of the erosion of X by B is the dilation of the complement by the reflected element; dilating the foreground acts like eroding the background with the reflected element | S5 Thm. 25; S2 eq. 2.13; S1 Prop. 4.2 | binary images |
| L15 | Authors disagree on where the reflection goes: Matheron and Serra write Minkowski subtraction with it, Hadwiger and Sternberg without, so formulas look different for the same opening | S1 §1.1.3, §4.1.1; S5 §III | — |
| L16 | Dilating by A then B equals dilating by A ⊕ B, and eroding by A then B equals eroding by A ⊕ B; this is how large elements are decomposed for speed | S2 eq. 2.9–2.10 | — |
| L17 | Flat grey-level dilation and erosion are the supremum and infimum of translates of the function over the element | S2 eq. 6.5 | flat element |
| L18 | Flat operators commute with thresholding: the threshold sets of the output are the binary operator applied to the threshold sets of the input | S2 §6.4 eq. 6.9; S9 abstract | increasing binary operator |
| L19 | Meyer and Sternberg were among the first to extend morphology to grey-level images | S1 §1.1.4 | — |
| L20 | The top-hat transform is the image minus its opening and extracts narrow peaks | S2 §6.2 | — |
| L21 | The morphological gradient is built from dilation and erosion; half-gradients and directional gradients are variants; it generalises to any space where dilation is defined | S8 abstract | — |
| L22 | Heijmans normalises the gradient as half of dilation minus erosion, which tends to the gradient magnitude for a smooth function | S2 §6.2 | continuously differentiable function |
| L23 | A granulometry is a family of openings with γ_s γ_r = γ_r γ_s = γ_max(r,s); the measure of γ_r(X) is the volume of particles of size at least r | S2 §5.4; S3 Def. 4.1 | — |
| L24 | If the elements satisfy B(r) ⊕ B(s) = B(r + s), the openings by B(r) form a granulometry; for a compact element this requires convexity | S2 §5.4 | — |
| L25 | Maragos built the pattern spectrum from Matheron's size distributions; large jumps mark substructures at that scale | S7 abstract | — |
| L26 | Binary reconstruction keeps the connected components of the mask that contain a marker pixel, and equals iterated elementary geodesic dilation, the dilation intersected with the mask, until stability | S4 Def. 2.1–2.2, Prop. 2.3; S2 §5.3 | — |
| L27 | Opening by reconstruction removes components that cannot contain the element and restores the others exactly; it is an algebraic opening | S4 §3.1; S2 eq. 5.10 | — |
| L28 | A regional maximum is a connected plateau whose neighbours are all lower; the regional maxima are I minus the reconstruction of I from I − 1, and the h-domes I minus the reconstruction from I − h, which select by height rather than size or shape | S4 Def. 3.1, Prop. 3.3, Def. 3.4 | — |
| L29 | The distance transform's level sets are the metric dilations of the set | S2 Prop. 5.9 | finitely compact metric space |
| L30 | Haralick et al. describe opening as smoothing contours, breaking narrow isthmuses and removing small islands, and closing as fusing narrow breaks and filling small holes | S5 §III | disk element |
| L31 | Haralick et al. compare opening and closing to ideal band-pass filters: once filtered, filtering again changes nothing | S5 §III | — |
| L32 | Morphology began in 1964 with Matheron (porous media) and Serra (iron ore) at the Paris School of Mines | S1 §1.1; S2 §1 | — |
| L33 | Serra and Matheron were the first to observe that a general theory should assume the image space is a complete lattice | S2 §1; S1 §1.2 | — |
| L34 | OpenCV's erode takes the minimum and its dilate the maximum of src(x + x′, y + y′) over the same kernel offsets, so dilate does not reflect the element | S10 imgproc.hpp, morph.simd.hpp | offsets measured from the anchor |
| L35 | OpenCV's morphology defaults to a constant border whose value becomes the type's maximum for erosion (255 for 8-bit) and minimum for dilation (0 for 8-bit; −DBL_MAX only for 64-bit float) | S10 createMorphologyFilter | default borderValue |
| L36 | OpenCV's default kernel for erode, dilate and morphologyEx is the 3×3 rectangle | S10 | kernel left empty |
| L37 | OpenCV's MORPH_OPEN erodes then dilates with the same kernel and anchor; with iterations = n it erodes n times then dilates n times, as its documentation notes | S10 morphologyEx and imgproc.hpp note; S11 | — |
| L38 | For a full rectangular kernel with iterations above 1, OpenCV substitutes one larger rectangle | S10 morphOp; S11 | — |
| L39 | OpenCV defines MORPH_GRADIENT as dilate minus erode, MORPH_TOPHAT as the source minus its opening, MORPH_BLACKHAT as the closing minus the source | S10 imgproc.hpp, morphologyEx | — |
| L40 | OpenCV's 3×3 MORPH_ELLIPSE is the cross; its 5×5 ellipse has 17 pixels; MORPH_DIAMOND exists from 4.12.0 | S10, S11 getStructuringElement; S12 | — |
| L41 | OpenCV's IPP path for morphology is compiled out at 802cf95 and in 4.10.0–4.12.0; the morphology HAL hooks are implemented only by the Carotene (ARM), OpenVX and RISC-V layers | S10, S11 | — |
| L42 | OpenCV issue #23605 reports that morphological opening is not anti-extensive with non-symmetric elements because dilation does not flip the element, while MATLAB and Octave give the expected result; it was open on 2026-10-14 | S13 | — |
| L43 | scikit-image issue #6676 found its closing not extensive and its opening not anti-extensive because the element was not mirrored between the two steps; it was closed in 2023 | S16 | — |
| L44 | In scikit-image v0.25.2 and v0.26.0 grey dilation does not mirror the footprint while opening and closing mirror it internally; binary_dilation mirrors and dilation does not, as its docstring states | S15; S14 gray.py | — |
| L45 | At b700edc scikit-image's skimage2 namespace drops all mirroring to follow SciPy and changes the grey default border mode from 'reflect' to 'ignore' | S14 | not yet released |
| L46 | scikit-image's default footprint is the cross; its grey functions default to mode 'reflect' (added in 0.23); its binary functions default to 'ignore', which treats the outside as foreground for erosion | S14, S15 | — |
| L47 | scikit-image's disk(r) keeps pixels with x² + y² ≤ r², diamond(r) the city-block ball; reconstruction defaults to a 3×3 square | S14 footprints.py, grayreconstruct.py | — |
| L48 | SciPy's binary_erosion, binary_dilation, binary_opening and binary_closing default to border_value = 0, the value assumed outside the input, and to the cross | S17 _morphology.py, ni_morphology.c | — |
| L49 | SciPy's grey_dilation and binary_dilation reflect the structuring element | S17 _morphology.py | — |
| L50 | MATLAB's imdilate reflects the element (binary and grey), assumes −∞ outside the image, and notes that some applications do not reflect | S18 imdilate | R2026b |
| L51 | MATLAB's imerode keeps z where the translated element lies inside the image's foreground, assumes +∞ outside, and imopen erodes then dilates with the same element | S18 imerode, imopen | R2026b |
| L52 | MATLAB's strel("disk", r) approximates the disk with periodic lines by default (n = 4); exact disks (n = 0) are not suitable for granulometries | S18 strel | R2026b |
| L53 | MATLAB's imreconstruct uses Vincent's hybrid algorithm, defaults to 8-connectivity, and underlies imfill, imclearborder, imhmax and imhmin | S18 imreconstruct | R2026b |
| L54 | Part 1 placed morphology inside the rank operators, gave erosion and dilation as Minkowski subtraction and addition, and named this post | S19 | — |
| L55 | Open-closing and clos-opening suppress impulse noise like the median and can tell positive from negative impulses | S6 abstract | — |
| L56 | For non-flat elements on a finite grey-level set, plain truncation gives wrong results | S9 abstract | — |
| L57 | OpenCV's imgproc module declares no morphological reconstruction function | S10 imgproc.hpp | at 802cf95 |
| L58 | SciPy's binary_opening with iterations = n erodes n times then dilates n times, and binary_propagation grows a marker inside a mask, which is binary reconstruction | S17 _morphology.py | v1.18.1 |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S2 | Fig. 3 (a set and its opening and closing by a disk) | opening and closing / L08 | the classic picture of what each removes | SIAM copyright, no licence | S2 URL | do not reuse |
| F2 | S5 | Fig. 8 (closing then dilation equals dilation) | idempotence / L06 | shows δφ = δ on a real image | IEEE copyright, no licence | S5 URL | do not reuse |
| F3 | S4 | Figs. 11–12 (regional maxima and h-domes by reconstruction) | reconstruction / L28 | shows reconstruction from I − h | IEEE copyright, no licence | S4 URL | do not reuse |
| F4 | S3 | Fig. 1 (chronology of openings, granulometries and filter axiomatics) | history / L10 | dates the ideas | Springer copyright, no licence on the author copy | S3 URL | do not reuse |

No `source` figure; every figure is computed on the series' patch or from the definitions.

## Open questions

- **The plan's three books were not accessible.** Serra 1982, Matheron 1975 and Soille's handbook
  have no open copy. Their results are cited through the survey (S2), the Heijmans–Ronse paper (S1)
  and the Serra–Vincent tutorial (S3), which state them; the post names Matheron's and Serra's
  results in prose with those keys and lists none of the three books.
- **Ronse & Heijmans 1991 (Part II, openings) and Ronse 1990** are Elsevier with no open copy; the
  algebra of openings is cited from S2 and S3.
- **Nothing in the literature sweep treats the bounded image.** The adjunction on a finite grid
  with the outside ignored is derived in the post, not cited; the random-pair check (0 failures
  against 616 on the same pairs) is ours.
- **The top-hat's origin** is commonly credited to Meyer, but his 1979 abstract does not name it; the
  post does not attribute it.
- **OpenCV issue #23605 is open.** Whether OpenCV will reflect in `dilate` or mirror inside
  `morphologyEx` is unknown; the post describes the behaviour at 802cf95 and 4.10.0–4.12.0.
- **Part 1 (published) says morphology's border value "becomes −DBL_MAX for dilation".** That is
  true only for 64-bit float images; for 8-bit images it is 0 (and 255 for erosion), with the same
  effect. Reported to the owner, not edited.
