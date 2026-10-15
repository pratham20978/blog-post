# Source ledger — colour-and-gamma

Series `image-processing`, part 13. Researched 2026-10-15, inline (no agents). The series is G0: every
library behaviour below is read from source at a pinned commit or tag, or from the vendor's
documentation, and replayed in plain Python; nothing was run against an image. The standards are read
from the bodies' own PDFs and datasets (ITU-R through WebFetch, because ITU's firewall rejects curl; CIE
open datasets; W3C) except IEC 61966-2-1, which is sold: its constants are taken from the open sources
that restate them (S5, S20, S23) and the post says so.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Sharma & Trussell, "Digital Color Imaging" (survey; journal version read in full from the authors' arXiv posting) | IEEE Transactions on Image Processing 6(7):901–932 | 1997 | 10.1109/83.597268 | peer-reviewed | https://arxiv.org/abs/cs/0109116 | 2026-10-15 |
| S2 | T1 | Anderson, Motta, Chandrasekar & Stokes, "Proposal for a Standard Default Color Space for the Internet — sRGB" (IS&T open copy) | IS&T/SID Color Imaging Conference 4(1):238–245 | 1996 | 10.2352/cic.1996.4.1.art00061 | peer-reviewed | https://library.imaging.org/admin/apis/public/api/ist/website/downloadArticle/cic/4/1/art00061 | 2026-10-15 |
| S3 | T2 | Stokes, Anderson, Chandrasekar & Motta, "A Standard Default Color Space for the Internet — sRGB", Version 1.10, 5 November 1996, with W3C's later note that the document is obsolete and that standardisation corrected a small rounding error | W3C (hosted proposal) | 1996 | — | official-docs | https://www.w3.org/Graphics/Color/sRGB.html | 2026-10-15 |
| S4 | T1 | IEC 61966-2-1:1999, "Multimedia systems and equipment – Colour measurement and management – Part 2-1: Default RGB colour space – sRGB", Edition 1.0, 1999-10-18, corrigendum COR1:2014 (catalogue entry only; the text is sold) | IEC | 1999 | IEC 61966-2-1:1999 | standard | https://webstore.iec.ch/en/publication/6169 | 2026-10-15 |
| S5 | T1 | W3C, CSS Color Module Level 4, Candidate Recommendation Draft 9 October 2026: §9.1 (CIE Lab), §10.2 (sRGB), §19 (sample code) | W3C | 2026 | CRD-css-color-4-20261009 | standard | https://www.w3.org/TR/2026/CRD-css-color-4-20261009/ | 2026-10-15 |
| S6 | T1 | ITU-R BT.709-6 (06/2015), "Parameter values for the HDTV standards for production and international programme exchange" | ITU-R | 2015 | Rec. ITU-R BT.709-6 | standard | https://www.itu.int/rec/R-REC-BT.709-6-201506-I/en | 2026-10-15 |
| S7 | T1 | ITU-R BT.601-7 (03/2011), "Studio encoding parameters of digital television for standard 4:3 and wide-screen 16:9 aspect ratios" | ITU-R | 2011 | Rec. ITU-R BT.601-7 | standard | https://www.itu.int/rec/R-REC-BT.601-7-201103-I/en | 2026-10-15 |
| S8 | T1 | ITU-R BT.470-6 (11/1998), "Conventional television systems", Table 2 and Annex 2 | ITU-R | 1998 | Rec. ITU-R BT.470-6 | standard | https://www.itu.int/rec/R-REC-BT.470-6-199811-S/en | 2026-10-15 |
| S9 | T1 | CIE, "Colour-matching functions of CIE 1931 standard colorimetric observer" (dataset, 360–830 nm at 1 nm, CC BY-SA 4.0) | CIE | 2019 | 10.25039/CIE.DS.xvudnb9b | standard | https://files.cie.co.at/Publications-datasets/CIE_xyz_1931_2deg.csv | 2026-10-15 |
| S10 | T1 | CIE, "CIE spectral luminous efficiency for photopic vision" V(λ) (dataset, 360–830 nm at 1 nm, CC BY-SA 4.0) | CIE | 2019 | 10.25039/CIE.DS.dktna2s3 | standard | https://files.cie.co.at/Publications-datasets/CIE_sle_photopic.csv | 2026-10-15 |
| S11 | T1 | CIE 015:2018, *Colorimetry*, 4th edition, §8.2.1 and Table 9.1 (read in the copy Public.Resource.Org posts as incorporated by reference; the CIE sells it) | CIE | 2018 | 10.25039/TR.015.2018 | standard | https://doi.org/10.25039/TR.015.2018 | 2026-10-15 |
| S12 | T1 | W3C, Portable Network Graphics (PNG) Specification (Third Edition), Recommendation 24 June 2025, §13.16 | W3C | 2025 | REC-png-3-20250624 | standard | https://www.w3.org/TR/2025/REC-png-3-20250624/ | 2026-10-15 |
| S13 | T2 | Hamilton, "JPEG File Interchange Format", Version 1.02, C-Cube Microsystems, 1 September 1992 (W3C copy) | — | 1992 | — | official-docs | https://www.w3.org/Graphics/JPEG/jfif3.pdf | 2026-10-15 |
| S14 | T1 | Poynton, "The rehabilitation of gamma" (author's reprint, 18 pp., read in full from the Wayback Machine's 2010 copy of poynton.com) | Proc. SPIE 3299, Human Vision and Electronic Imaging III:232–249 | 1998 | 10.1117/12.320126 | peer-reviewed | https://doi.org/10.1117/12.320126 | 2026-10-15 |
| S15 | T1 | Poynton & Funt, "Perceptual uniformity in digital image representation and display" (abstract only) | Color Research & Application 39(1):6–15 | 2014 | 10.1002/col.21768 | peer-reviewed | https://doi.org/10.1002/col.21768 | 2026-10-15 |
| S16 | T1 | Robertson, "The CIE 1976 Color-Difference Formulae" (abstract only) | Color Research & Application 2(1):7–11 | 1977 | 10.1002/j.1520-6378.1977.tb00104.x | peer-reviewed | https://doi.org/10.1002/j.1520-6378.1977.tb00104.x | 2026-10-15 |
| S17 | T1 | Fairchild & Pirrotta, "Predicting the lightness of chromatic object colors using CIELAB" (abstract only) | Color Research & Application 16(6):385–393 | 1991 | 10.1002/col.5080160608 | peer-reviewed | https://doi.org/10.1002/col.5080160608 | 2026-10-15 |
| S18 | T4 | Poynton, "Frequently Asked Questions about Color" (1997-03-02; PDF as served by poynton.ca) — cited only for what it itself prints, which two libraries copied | poynton.ca | 1997 | — | practitioner | https://poynton.ca/pdf/ColourFAQ.pdf | 2026-10-15 |
| S19 | T4 | Poynton, "Frequently Asked Questions about Gamma" (1998) — framing only | poynton.ca | 1998 | — | practitioner | https://poynton.ca/pdf/GammaFAQ.pdf | 2026-10-15 |
| S20 | T3 | OpenCV source, commit 802cf95: `modules/imgproc/src/color.simd_helpers.hpp`, `color_rgb.simd.hpp`, `color_rgb.dispatch.cpp`, `color_lab.cpp`, `color.cpp`, `color.hpp`, `include/opencv2/imgproc.hpp`, `doc/colors.markdown`; HAL files `hal/ipp/src/color_ipp.cpp`, `hal/ipp/include/ipp_hal_imgproc.hpp`, `hal/carotene/hal/tegra_hal.hpp`, `hal/carotene/src/colorconvert.cpp`, `hal/riscv-rvv/src/imgproc/color.cpp`, `hal/kleidicv/kleidicv.cmake` | — | 2026 | commit 802cf95aa3d42816995695bf68a86b3532f12760 | source | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src/color_lab.cpp | 2026-10-15 |
| S21 | T3 | OpenCV source, tags 4.10.0, 4.14.0 (2026-07-17) and 5.0.0 (2026-06-05): the same colour files | — | 2024–2026 | tags 4.10.0, 4.14.0, 5.0.0 | source | https://github.com/opencv/opencv/blob/5.0.0/modules/imgproc/src/color_rgb.dispatch.cpp | 2026-10-15 |
| S22 | T3 | KleidiCV 26.03 (the version OpenCV 802cf95 downloads), `adapters/opencv/kleidicv_hal.h` | — | 2026 | tag 26.03 | source | https://gitlab.arm.com/kleidi/kleidicv/-/blob/26.03/adapters/opencv/kleidicv_hal.h | 2026-10-15 |
| S23 | T3 | scikit-image source, commit b700edc and release v0.26.0 (2025-12-20): `color/colorconv.py` (and `_skimage2/color/colorconv.py` at b700edc), `transform/_warps.py` | — | 2025–2026 | commit b700edc8005e4ee9e74fc83259f09e8df3213f15; tag v0.26.0 | source | https://github.com/scikit-image/scikit-image/blob/v0.26.0/src/skimage/color/colorconv.py | 2026-10-15 |
| S24 | T3 | Pillow source, release 12.3.0 (2026-07-01): `src/libImaging/Convert.c`, `src/PIL/Image.py` | — | 2026 | tag 12.3.0 | source | https://github.com/python-pillow/Pillow/blob/12.3.0/src/libImaging/Convert.c | 2026-10-15 |
| S25 | T2 | MathWorks documentation, release R2026b: `rgb2gray` (MATLAB), `rgb2lin`, `rgb2lab` (Image Processing Toolbox) | — | 2026 | R2026b | official-docs | https://www.mathworks.com/help/matlab/ref/rgb2gray.html | 2026-10-15 |
| S26 | T3 | Part 1 of this series, *Image Processing by Hand* (published): the `BGR2GRAY` paragraph and the impulse's box (64) and Gaussian (98.6) answers | canery.in | 2026 | — | source | https://canery.in/blogs/image-processing-by-hand | 2026-10-15 |

Peer-reviewed or standard with an identifier: S1, S2, S4–S12 and S14–S17 (fifteen; L3 floor seven).
S15, S16 and S17 were read as abstracts only (OpenAlex), and every claim on them says no more than the
abstract. S4 was read only as its catalogue entry; every constant the post attributes to sRGB carries
S5, S20 or S23, which state it. S11 was read in full in the Public.Resource.Org copy; the post links the
CIE's DOI.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | filter title.search "digital color imaging", by citations | noise: galaxy colours, food colour measurement, a CRC handbook; no survey surfaced this way |
| 2 | 1 | OpenAlex | search "Sharma Trussell digital color imaging"; "Trussell Saber Vrhel color image processing basics" | a 2005 vector-filtering review and a 2008 EURASIP colour-trends review; not the survey |
| 3 | 1 | OpenAlex | search "Poynton rehabilitation of gamma"; "Poynton gamma and its disguises" | unrelated (MaxRGB, LCD fringe projection); relevance search misses both |
| 4 | 1 | Crossref | bibliographic "Poynton Gamma and its disguises SMPTE Journal 1993" (first burst hit 429; retried with backoff) | SMPTE Journal 102(12):1099–1108, doi 10.5594/j01651 |
| 5 | 1 | Crossref | bibliographic "Poynton The rehabilitation of gamma … 1998"; "Sharma Trussell Digital color imaging … 1997"; "Anderson Motta Chandrasekar Stokes … sRGB 1996" | SPIE 3299:232–249; the survey, TIP 6(7):901–932; the sRGB proposal at CIC 4, 238–245, and Nielsen & Stokes 1998 on the sRGB ICC profile |
| 6 | 1 | OpenAlex | the four DOIs above, for open copies | the survey's journal version on arXiv (cs/0109116); the CIC paper open at IS&T; the SMPTE paper only at IEEE Xplore (418, a bot wall) |
| 7 | 1 | OpenAlex | cites:W1981418116 (forward chase from Poynton 1998), by citations | Poynton & Funt 2014, the updated treatment of perceptual uniformity; quality-metric papers that use gamma coding; no correction |
| 8 | 1 | OpenAlex | cites:W4377983905 + title.search "gamma" (forward chase from the sRGB proposal) | CRT characterisation papers 2001–2024; nothing revises the encoding |
| 9 | 1 | OpenAlex, Crossref | DOI 10.1002/col.21768 | the Poynton & Funt abstract; Wiley, no open copy |
| 10 | 1 | Google Scholar (curl) | "Perceptual uniformity in digital image representation and display" (quoted), then unquoted with the authors | quoted: one unrelated hit; unquoted: the 2014 paper at Wiley, no PDF link |
| 11 | 1 | Semantic Scholar | citations of DOI:10.1109/83.597268 (100 citing papers, filtered on colour-space terms) | a 2018 review of colour spaces for compression; colour-to-grey conversions; nothing that corrects the survey's account of luminance or gamma |
| 12 | 1 | OpenAlex, Wayback Machine | abstracts of DOIs 10.1117/12.320126 and 10.5594/j01651; poynton.com/PDFs/ in 2010 snapshots | both abstracts; full author reprints of both papers (the 1998 one read in full) |
| 13 | 1 | Crossref | "Stokes Fairchild Berns Precision requirements for digital color reproduction" (backward chase from Poynton 1998's margin reference) | ACM TOG 11(4):406–422, doi 10.1145/146443.146482; not read, not cited |
| 14 | 1 | Crossref, OpenAlex | Robertson 1977; Fairchild & Pirrotta 1991 | both abstracts; the CIE's 1977 recommendation note (CRA 2(1):5–6); Nayatani et al. 1992 on the same effect |
| 15 | 1 | WebSearch | "CIE 015:2018 Colorimetry 4th edition free download" | the CIE sells it; Public.Resource.Org posts it as incorporated by reference |
| 16 | 1 | CIE website | datatable pages for the 1931 2° observer, V(λ), D65 | open CSV datasets under CC BY-SA 4.0 with DOIs |
| 17 | 1 | ITU (WebFetch) | BT.601-7, BT.709-6, BT.470-6 PDFs (curl gets "Request Rejected") | all three read in full; page images rendered to confirm primes in E′Y |
| 18 | 1 | W3C | 1996 sRGB proposal (HTML and its equation images), CSS Color 4 CRD 2026-10-09, PNG third edition, JFIF 1.02 | the 1996 thresholds 0.00304 and 0.03928; the IEC curve in CSS's code; D50 Lab with Bradford; PNG §13.16; JFIF's Y equation |
| 19 | 1 | IEC webstore | publication 6169 | IEC 61966-2-1:1999, edition 1.0, 1999-10-18, COR1:2014 |
| 20 | 6 | poynton.ca | /faq/, /publ/ | the Colour FAQ (1997) and Gamma FAQ (1998) PDFs; the publication list |
| 21 | 5 | GitHub raw and trees API | OpenCV 802cf95 colour files and the hal/ tree; tags 4.10.0, 4.14.0, 5.0.0 | 15-bit BT.601 grey; IPP grey only for 32F; Carotene and RVV with the same weights; XYZ without decode; Lab with decode, undocumented |
| 22 | 5 | gitlab.arm.com | KleidiCV 26.03 OpenCV adapter | overrides grey-to-BGR only |
| 23 | 5 | GitHub raw and API | scikit-image b700edc and v0.26.0 colorconv.py, _warps.py; releases | rgb2gray 0.2125/0.7154/0.0721 on encoded values, documented as luminance; rgb2xyz decodes; illuminant swap without adaptation |
| 24 | 5 | GitHub raw and API | Pillow 12.3.0 Convert.c and Image.py; releases | 16-bit BT.601 luma "assuming nonlinear RGB"; resize with no colour parameter |
| 25 | 5 | WebFetch | MathWorks R2026b rgb2gray, rgb2lin, rgb2lab (curl gets an Akamai 403) | 0.298936021293775/0.587043074451121/0.114020904255103 called luminance E′y; rgb2lin since R2017b; rgb2lab D65 by default |
| 26 | 4 | (by computation) | every 8-bit triple through BT.601 luma and BT.709 luminance; OpenCV's 15-bit and Pillow's 16-bit integer luma; the 12.92 line against the sRGB curve; luminance rows from each standard's primaries | the luma error spans −70.2 to +5.9 codes; equal-weight luma never exceeds the luminance grey; 21,745 integer disagreements; the 1996 thresholds are the tangent point, the IEC's the upper crossing; BT.601's own primaries give other weights |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | sRGB is standardised as IEC 61966-2-1:1999, which defines encoding transformations for RGB colours in computer systems; CSS uses sRGB as its default colour space | S4; S3 note; S5 §10.2 | edition 1.0 with COR1:2014 |
| L02 | The sRGB decode is c/12.92 for a normalised code c up to 0.04045 and ((c + 0.055)/1.055)^2.4 above it; the encode uses 12.92 L up to 0.0031308 and 1.055 L^(1/2.4) − 0.055 above | S5 §10.2; S20 color_lab.cpp (applyGamma, applyInvGamma); S23 rgb2xyz, xyz2rgb | the IEC values, as restated by these sources |
| L03 | sRGB uses the BT.709 primaries, red (0.64, 0.33), green (0.30, 0.60), blue (0.15, 0.06), and the D65 white (0.3127, 0.3290) | S5 §10.2; S6 items 1.3–1.4; S2 Table 2 | — |
| L04 | The 1996 proposal set the thresholds at 0.00304 (linear) and 0.03928 (encoded), with slope 12.92, offset 0.055 and exponent 2.4; W3C's note says standardisation later corrected a small rounding error | S2 eq. 1.2, 1.7 (p. 242); S3 header note and eq. 1.2, 1.7 | — |
| L05 | The proposal describes its curve as a close fit to a plain 2.2 power, with an offset added so that it inverts in integer arithmetic | S2 p. 242; S3 §1 | — |
| L06 | The sRGB authors separate a linear-intensity space, where optical and synthetic operations such as alpha masking belong, from a nearly perceptually uniform space, where visual operations, compression and most devices work; encoded with gamma 1.0, a mid grey would land at code 46 of 255 | S2 p. 240 | 24-bit (8 bits per channel) encoding |
| L07 | PNG specifies alpha compositing as alpha·foreground + (1 − alpha)·background, computed on intensity samples, not gamma-encoded ones | S12 §13.16 | — |
| L08 | Gamma correction before quantisation, like speech companding, gives wider steps at high amplitudes where the eye is less sensitive and makes contours less visible than linear quantisation | S1 p. 912 | — |
| L09 | With linear-light coding, steps of 1 per cent over a 100:1 range need about 9,900 codes (about 14 bits); with ratio-like nonlinear coding about 463 codes (about 9 bits); 8-bit linear coding contours below code 100 | S14 reprint p. 6 | 1 per cent visibility threshold |
| L10 | The main purpose of gamma correction is to code tristimulus values into a perceptually uniform domain so that a limited number of bits performs well; a CRT's nonlinearity is close to the inverse of lightness sensitivity, which is desirable, not a defect | S14 reprint p. 1 | — |
| L11 | sRGB, BT.709, Adobe RGB and DCI-P3 all code component values perceptually uniformly, and the property is poorly documented and widely confused | S15 abstract | — |
| L12 | A unit step of L* is taken as roughly the threshold of visibility; a ΔE*ab of about 2.3 corresponds to a just-noticeable difference | S14 reprint p. 4; S1 p. 908 | rule-of-thumb values |
| L13 | BT.709 item 3.2 defines E′Y = 0.2126 E′R + 0.7152 E′G + 0.0722 E′B and names it the luminance signal; item 3.1 gives the pre-correction exponent 0.45 | S6 §3 | primes mark gamma-corrected signals |
| L14 | BT.709's transfer characteristic is the camera's, V = 1.099 L^0.45 − 0.099 for L at least 0.018 and 4.5 L below; its footnote names BT.1886 for the reference display's decoding | S6 item 1.2 and footnote 1 | — |
| L15 | BT.601-7 §2.5.1 constructs E′Y = 0.299 E′R + 0.587 E′G + 0.114 E′B from the gamma pre-corrected primaries and calls it luminance | S7 §2.5, §2.5.1 | — |
| L16 | BT.601-7's own primaries are 625-line red (0.640, 0.330), green (0.290, 0.600), blue (0.150, 0.060) and 525-line red (0.630, 0.340), green (0.310, 0.595), blue (0.155, 0.070), with a D65 white | S7 §2.6.1–2.6.2 | — |
| L17 | The 1953 NTSC primaries were red (0.67, 0.33), green (0.21, 0.71), blue (0.14, 0.08) with white C (0.310, 0.316); PAL and SECAM coefficients were based on them, and in all systems the coding coefficients still are, though real phosphors have changed | S8 Annex 2 §1–3; Table 2 item 2.1–2.2 | — |
| L18 | BT.470 assumes a receiver gamma of 2.2 for System M (NTSC) | S8 Table 2 item 2.3 | — |
| L19 | For the CIE 1931 observer, Illuminant C has chromaticity (0.31006, 0.31617) and D65 (0.31271, 0.32903), with D65 tristimulus values 95.04, 100, 108.88 | S11 Table 9.1 | — |
| L20 | The CIE publishes the 1931 2° colour-matching functions and the photopic V(λ) as open tables from 360 to 830 nm; in them ȳ(λ) and V(λ) are the same function | S9; S10 | compared row by row (471 wavelengths) |
| L21 | The Y tristimulus value is usually called the luminance and correlates with perceived brightness | S1 p. 905 | — |
| L22 | CIE XYZ is perceptually non-uniform; a cube-root law fits brightness best; in 1976 the CIE recommended CIELAB and CIELUV, both only approximately uniform | S1 p. 908; S16 abstract | — |
| L23 | CIELAB: L* = 116 f(Y/Yn) − 16, a* = 500 (f(X/Xn) − f(Y/Yn)), b* = 200 (f(Y/Yn) − f(Z/Zn)), f(t) = t^(1/3) above (24/116)^3 and (841/108) t + 16/116 below; in 2002 the CIE replaced the decimals 0.008856 and 7.787 by these fractions | S11 §8.2.1 | — |
| L24 | CSS's lab() uses a D50 white and converts sRGB's D65 colours with the linear Bradford transform; D50 is also the ICC profile connection white and the Lab white of image editors | S5 §9.1, §19 | — |
| L25 | Chromatic colours look lighter than achromatic ones of the same luminance factor (the Helmholtz–Kohlrausch effect) | S17 abstract | — |
| L26 | Poynton's Colour FAQ gives Y = 0.2125 R + 0.7154 G + 0.0721 B as the BT.709 luminance weights for linear red, green and blue, and prints the six-decimal RGB-to-XYZ matrix 0.412453 … 0.950227; it says 0.299/0.587/0.114 computed luminance for the 1953 phosphors and remain right for luma only | S18 §9, §11, §18 | — |
| L27 | OpenCV documents BGR2GRAY as Y = 0.299 R + 0.587 G + 0.114 B; its 8-bit and 16-bit paths use the 15-bit integers 9798, 19235, 3735 with rounding; 32-bit float uses 0.299f, 0.587f, 0.114f | S20 colors.markdown; color.simd_helpers.hpp; color_rgb.simd.hpp | — |
| L28 | `cvtColor` hands BGR2GRAY to a HAL first: Intel IPP takes only 32-bit float input (at 802cf95, and inline in 4.10.0 and 5.0.0); Carotene (ARM) and RISC-V RVV use the same 15-bit weights; KleidiCV 26.03 does not override it | S20 color_rgb.dispatch.cpp, hal files; S21; S22 | — |
| L29 | OpenCV's BGR2XYZ multiplies the documented matrix (0.412453 … 0.950227, "Rec 709 with D65") into the values it is given, with no sRGB decode; its documentation says the range does not matter for linear transformations | S20 color_lab.cpp (RGB2XYZ_f, RGB2XYZ_i), color.cpp, imgproc.hpp, colors.markdown | — |
| L30 | OpenCV's BGR2Lab decodes sRGB first (constants 0.04045, 12.92, 0.055, 2.4) and uses the white (0.950456, 1, 1.088754); the LBGR2Lab codes skip the decode; the Lab documentation does not mention the decode; 8-bit output stores L·255/100, a + 128, b + 128 | S20 color_lab.cpp, color.hpp (is_sRGB), colors.markdown | — |
| L31 | The grey, XYZ and Lab behaviour above is the same in OpenCV 4.10.0, 4.14.0 and 5.0.0 | S21 | — |
| L32 | OpenCV's `resize` and `GaussianBlur`, Pillow's `Image.resize` and scikit-image's `transform.resize` take no transfer function or colour space; they weight whatever values they are given | S20 imgproc.hpp; S24 Image.py; S23 _warps.py | — |
| L33 | scikit-image's `rgb2gray` is documented as computing luminance, with 0.2125/0.7154/0.0721 "calibrated for contemporary CRT phosphors" and a reference to Poynton's FAQ; it applies them to the input converted to float, without decoding | S23 colorconv.py | v0.26.0 and b700edc |
| L34 | scikit-image's `rgb2xyz` decodes sRGB (0.04045 …) and uses the same six-decimal matrix as OpenCV; `rgb2lab` defaults to illuminant D65 (0.95047, 1, 1.08883), 2° observer; `xyz2lab` divides by the chosen white without chromatic adaptation | S23 colorconv.py | v0.26.0 and b700edc |
| L35 | scikit-image's module docstring calls its central space linear sRGB without gamma correction | S23 colorconv.py module docstring | — |
| L36 | Pillow's `convert("L")` is documented as the ITU-R 601-2 luma transform L = R·299/1000 + G·587/1000 + B·114/1000; the C code uses 19595, 38470, 7471 over 2^16 with rounding and a comment "assuming nonlinear RGB" | S24 Image.py, Convert.c | 12.3.0 |
| L37 | MATLAB's `rgb2gray` forms 0.298936021293775 R + 0.587043074451121 G + 0.114020904255103 B and its page calls these the luminance (E′y) coefficients of BT.601-7 after rounding; it moved into MATLAB in R2014b | S25 rgb2gray | R2026b |
| L38 | MATLAB's `rgb2lin` linearises gamma-corrected RGB (sRGB by default, R2017b); `rgb2lab` assumes sRGB input and a D65 white by default and offers D50 and ICC | S25 rgb2lin, rgb2lab | R2026b |
| L39 | JFIF stores YCbCr from CCIR 601 at full 256-level range, Y = 0.299 R + 0.587 G + 0.114 B from 8-bit RGB; a one-component file holds Y alone | S13 pp. 1–3 | — |
| L40 | Part 1 states BGR2GRAY returns luma, and gives the impulse's 3×3 box answer as 64 and its σ = 0.8 Gaussian answer as 98.6 | S26 | — |
| L42 | The proposal's linear-RGB-to-XYZ matrix is 0.4124 0.3576 0.1805 / 0.2126 0.7152 0.0722 / 0.0193 0.1192 0.9505; CSS gives the same matrix as exact fractions, whose Y row is 0.212639, 0.715169, 0.072192 | S3 eq. 1.8; S5 §19 (lin_sRGB_to_XYZ) | D65 white (0.3127, 0.3290) |
| L43 | OpenCV's 8-bit BGR2XYZ uses 12-bit integers, Y = (871 R + 2929 G + 296 B) / 4096 with rounding, on the codes as given | S20 color_lab.cpp (sRGB2XYZ_D65_i, RGB2XYZ_i) | 8-bit input |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S14 | Figure 7 (linear-light coding: the code 100 problem) | why a pixel is an encoding / L09 | shows step ratios at codes 25 and 100 | © Charles Poynton; no licence stated | https://doi.org/10.1117/12.320126 | do not reuse; the post computes its own codes-per-lightness chart |
| F2 | S2 | Figure 3 (sRGB and BT.709 viewing chain) | the transfer function / L04 | names the viewing-condition chain | © IS&T; no licence stated | https://doi.org/10.2352/cic.1996.4.1.art00061 | do not reuse; not needed |

No `source` figure; every figure is computed from the standards' constants, the CIE tables, or the
series' patch.

## Open questions

- **IEC 61966-2-1's text was not read.** Its constants are cited from CSS Color 4 and from the OpenCV
  and scikit-image sources that implement them; the post says so in the IMPORTANT block.
- **Why the IEC changed 0.03928 to 0.04045** is stated only as "a small numerical error caused by
  rounding" (S3). The geometry (a line from the origin is tangent to the curve at the encoded value
  0.055/1.4 = 0.0392857, slope 12.9232, which the proposal printed truncated as 0.03928; the line with
  slope 12.92 crosses the curve at 0.03815 and 0.04045) is our computation; the post presents it as
  such, not as the committee's reasoning.
- **Which Illuminant C produced 0.299/0.587/0.114.** With BT.470's rounded C (0.310, 0.316) the
  luminance row is 0.2990, 0.5864, 0.1146; with the CIE's (0.31006, 0.31617) it is 0.2989, 0.5866,
  0.1145. Only the second rounds to the standard's three decimals; the post uses the CIE value and says
  the coefficients follow from the 1953 primaries and C to three decimals.
- **OpenCV's six-decimal matrix** reproduces Poynton's FAQ; its white (0.950456, 1, 1.088754) is not
  the CIE's D65 nor the one the four-decimal chromaticities give (Z/Y 1.089058). The post does not
  explain its origin; the difference is in the fifth decimal.
- **OpenCV's 8-bit Lab** runs through lookup tables and fixed point; the post quotes the documented
  scaling (L·255/100) and says "about" for the stored value.
- **SMPTE 1993 ("Gamma and its disguises")** was found but not read beyond its abstract; not cited.
