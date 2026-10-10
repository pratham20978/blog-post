# Source ledger — wavelets-and-multiresolution

Series `image-processing`, part 6. Sweep run 2026-10-10. Tier L3, so the floor is 7
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

How each source was read is stated per row, because it varies. Read in full as PDFs
(`pdftotext`, with page images rendered where equations were lost): Mallat 1989 (author's copy on
di.ens.fr), Daubechies 1988, Cohen–Daubechies–Feauveau 1992, Antonini et al. 1992 and
Daubechies–Sweldens 1998 (all from Daubechies' Duke publication page), Skodras–Christopoulos–
Ebrahimi 2001 (a University of Crete course copy of the IEEE SPM article), both Unser–Blu 2003
papers (EPFL Biomedical Imaging Group), Wallace 1992 (an NUS course copy of the submitted
version), Donoho 1995 and Donoho–Johnstone–Kerkyacharian–Picard 1995 (Stanford copies), and
Selesnick–Baraniuk–Kingsbury 2005 (NYU copy). Calderbank et al. 1998 was read only as far as the
Duke copy reaches: the introduction and section 2; its claim rows say so. Seven peer-reviewed
sources were not reachable in full and are used **only for what their abstracts state** (from the
OpenAlex record, venue and pages cross-checked against Crossref): Donoho–Johnstone 1994, Chang–Yu–
Vetterli 2000, Simoncelli et al. 1992, Le Gall–Tabatabai 1988, Usevitch 2001, Ebrahimi–Chamik–
Winkler 2004 and Triantaphillidou–Allen–Jacobson 2007. Haar 1910 is cited for its date and venue
only (OpenAlex and Crossref metadata).

The normative JPEG 2000 text (ITU-T T.800) could not be fetched: itu.int's firewall rejected both
curl and WebFetch. Its 2019 table of contents was readable and confirms that Annex F holds the
1D_EXTR extension procedure and the 5-3 reversible and 9-7 irreversible filters. The ledger uses the
December 1999 committee draft (ISO/IEC CD 15444-1, V1.0) for structure and naming only, and takes
every filter coefficient and rounding rule from Skodras et al. 2001 and from OpenJPEG's source,
which implements the final standard. The draft's 9/7 scaling constant (1.149604) differs from the
final standard's; it is not used.

Library behaviour was read at pinned commits: PyWavelets `c9b542b2d2c3` (2026-10-01),
scikit-image `b700edc8005e` (2026-10-09, the commit Part 5 pinned), OpenJPEG `8314119b067c`
(2026-09-05) and Pillow `c15d19b95732` (2026-10-10). Nothing was executed against an image. The
only code run was plain Python (`math` and `cmath`, no packages) that reproduces the post's
hand-worked numbers: the Haar and 5/3 lifting steps on rows of the patch, one 2-D Haar level on
the patch, the coefficient counts, the closed-form frequency responses, the 9/7 lifting impulse
responses, and the threshold arithmetic.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Mallat, "A Theory for Multiresolution Signal Decomposition: The Wavelet Representation" | IEEE TPAMI 11(7), pp. 674–693 | 1989 | 10.1109/34.192463 | peer-reviewed | https://www.di.ens.fr/~mallat/papiers/MallatTheory89.pdf | 2026-10-10 |
| S02 | T1 | Daubechies, "Orthonormal Bases of Compactly Supported Wavelets" | Comm. Pure Appl. Math. 41(7), pp. 909–996 | 1988 | 10.1002/cpa.3160410705 | peer-reviewed | https://sites.math.duke.edu/~ingrid/publications/cpam41-1988.pdf | 2026-10-10 |
| S03 | T1 | Cohen, Daubechies & Feauveau, "Biorthogonal Bases of Compactly Supported Wavelets" | Comm. Pure Appl. Math. 45(5), pp. 485–560 | 1992 | 10.1002/cpa.3160450502 | peer-reviewed | https://sites.math.duke.edu/~ingrid/publications/CPAM_1992_p485.pdf | 2026-10-10 |
| S04 | T1 | Daubechies & Sweldens, "Factoring Wavelet Transforms into Lifting Steps" | J. Fourier Anal. Appl. 4(3), pp. 247–269 | 1998 | 10.1007/BF02476026 | peer-reviewed | https://sites.math.duke.edu/~ingrid/publications/J_Four_Anal_Appl_4_p247.pdf | 2026-10-10 |
| S05 | T1 | Calderbank, Daubechies, Sweldens & Yeo, "Wavelet Transforms That Map Integers to Integers" (introduction and §2 only) | Appl. Comput. Harmon. Anal. 5(3), pp. 332–369 | 1998 | 10.1006/acha.1997.0238 | peer-reviewed | https://sites.math.duke.edu/~ingrid/publications/ACH-5-1998.pdf | 2026-10-10 |
| S06 | T1 | Skodras, Christopoulos & Ebrahimi, "The JPEG 2000 Still Image Compression Standard" | IEEE Signal Processing Magazine 18(5), pp. 36–58 | 2001 | 10.1109/79.952804 | peer-reviewed | https://www.csd.uoc.gr/~hy371/bibliography/JPEG2000.pdf | 2026-10-10 |
| S07 | T1 | Unser & Blu, "Mathematical Properties of the JPEG2000 Wavelet Filters" | IEEE Trans. Image Processing 12(9), pp. 1080–1090 | 2003 | 10.1109/TIP.2003.812329 | peer-reviewed | https://bigwww.epfl.ch/publications/unser0305.pdf | 2026-10-10 |
| S08 | T1 | Unser & Blu, "Wavelet Theory Demystified" | IEEE Trans. Signal Processing 51(2), pp. 470–483 | 2003 | 10.1109/TSP.2002.807000 | peer-reviewed | https://bigwww.epfl.ch/publications/unser0301.pdf | 2026-10-10 |
| S09 | T1 | Wallace, "The JPEG Still Picture Compression Standard" (submitted version) | IEEE Trans. Consumer Electronics 38(1), pp. xviii–xxxiv | 1992 | 10.1109/30.125072 | peer-reviewed | https://www.comp.nus.edu.sg/~cs5342/readings/wallace.pdf | 2026-10-10 |
| S10 | T1 | ISO/IEC CD 15444-1 / ITU-T T.800 committee draft, "JPEG 2000 Image Coding System", Annex F (structure and naming only) | ISO/IEC JTC 1/SC 29/WG 1 | 1999 | ISO/IEC CD 15444-1:1999 (V1.0) | standard | https://www.eecis.udel.edu/~amer/CISC651/JPEG2000_draft_std_cd15444-1.pdf | 2026-10-10 |
| S11 | T1 | Donoho, "De-Noising by Soft-Thresholding" (Stanford preprint of the journal paper) | IEEE Trans. Information Theory 41(3), pp. 613–627 | 1995 | 10.1109/18.382009 | peer-reviewed | https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/denoiserelease3.pdf | 2026-10-10 |
| S12 | T1 | Donoho, Johnstone, Kerkyacharian & Picard, "Wavelet Shrinkage: Asymptopia?" | J. R. Statist. Soc. B 57(2), pp. 301–337 | 1995 | 10.1111/j.2517-6161.1995.tb02032.x | peer-reviewed | https://web.stanford.edu/dept/statistics/cgi-bin/donoho/wp-content/uploads/2018/08/asymp.pdf | 2026-10-10 |
| S13 | T1 | Donoho & Johnstone, "Ideal Spatial Adaptation by Wavelet Shrinkage" (abstract only) | Biometrika 81(3), pp. 425–455 | 1994 | 10.1093/biomet/81.3.425 | peer-reviewed | https://doi.org/10.1093/biomet/81.3.425 | 2026-10-10 |
| S14 | T1 | Chang, Yu & Vetterli, "Adaptive Wavelet Thresholding for Image Denoising and Compression" (abstract only) | IEEE Trans. Image Processing 9(9), pp. 1532–1546 | 2000 | 10.1109/83.862633 | peer-reviewed | https://doi.org/10.1109/83.862633 | 2026-10-10 |
| S15 | T1 | Simoncelli, Freeman, Adelson & Heeger, "Shiftable Multiscale Transforms" (abstract only) | IEEE Trans. Information Theory 38(2), pp. 587–607 | 1992 | 10.1109/18.119725 | peer-reviewed | https://doi.org/10.1109/18.119725 | 2026-10-10 |
| S16 | T1 | Selesnick, Baraniuk & Kingsbury, "The Dual-Tree Complex Wavelet Transform" | IEEE Signal Processing Magazine 22(6), pp. 123–151 | 2005 | 10.1109/MSP.2005.1550194 | peer-reviewed | https://eeweb.engineering.nyu.edu/iselesni/pubs/CWT_Tutorial.pdf | 2026-10-10 |
| S17 | T1 | Antonini, Barlaud, Mathieu & Daubechies, "Image Coding Using Wavelet Transform" | IEEE Trans. Image Processing 1(2), pp. 205–220 | 1992 | 10.1109/83.136597 | peer-reviewed | https://sites.math.duke.edu/~ingrid/publications/ieee1-1992.pdf | 2026-10-10 |
| S18 | T1 | Le Gall & Tabatabai, "Sub-Band Coding of Digital Images Using Symmetric Short Kernel Filters and Arithmetic Coding Techniques" (abstract only) | Proc. IEEE ICASSP 1988, pp. 761–764 | 1988 | 10.1109/ICASSP.1988.196696 | peer-reviewed | https://doi.org/10.1109/ICASSP.1988.196696 | 2026-10-10 |
| S19 | T1 | Usevitch, "A Tutorial on Modern Lossy Wavelet Image Compression: Foundations of JPEG 2000" (abstract only) | IEEE Signal Processing Magazine 18(5), pp. 22–35 | 2001 | 10.1109/79.952803 | peer-reviewed | https://doi.org/10.1109/79.952803 | 2026-10-10 |
| S20 | T1 | Ebrahimi, Chamik & Winkler, "JPEG vs. JPEG 2000: An Objective Comparison of Image Encoding Quality" (abstract only) | Proc. SPIE 5558, Applications of Digital Image Processing XXVII, p. 300 | 2004 | 10.1117/12.564835 | peer-reviewed | https://doi.org/10.1117/12.564835 | 2026-10-10 |
| S21 | T1 | Triantaphillidou, Allen & Jacobson, "Image Quality Comparison Between JPEG and JPEG2000. II. Scene Dependency, Scene Analysis, and Classification" (abstract only) | J. Imaging Sci. Technol. 51(3), pp. 259–270 | 2007 | 10.2352/J.ImagingSci.Technol.(2007)51:3(259) | peer-reviewed | https://doi.org/10.2352/J.ImagingSci.Technol.(2007)51:3(259) | 2026-10-10 |
| S22 | T1 | Haar, "Zur Theorie der orthogonalen Funktionensysteme" (date and venue only) | Mathematische Annalen 69(3), pp. 331–371 | 1910 | 10.1007/BF01456326 | peer-reviewed | https://doi.org/10.1007/BF01456326 | 2026-10-10 |
| S23 | T1 | Rioul & Vetterli, "Wavelets and Signal Processing" (survey; abstract used to map the field, not cited in the post) | IEEE Signal Processing Magazine 8(4), pp. 14–38 | 1991 | 10.1109/79.91217 | peer-reviewed | https://doi.org/10.1109/79.91217 | 2026-10-10 |
| S24 | T3 | PyWavelets source and docs at commit c9b542b: `doc/source/ref/signal-extension-modes.rst`, `pywt/_dwt.py`, `pywt/_multidim.py`, `pywt/_thresholding.py`, `pywt/_swt.py`, `pywt/_extensions/c/{common.c, wavelets.c, wavelets_coeffs.template.h, convolution.template.c}` | — | 2026 | — | source | https://github.com/PyWavelets/pywt/tree/c9b542b2d2c37d28ed1d9bd49d178d2769608905 | 2026-10-10 |
| S25 | T3 | scikit-image source at commit b700edc: `src/_skimage2/restoration/_denoise.py` (`denoise_wavelet`, `_wavelet_threshold`, `estimate_sigma`), re-exported by `src/skimage/restoration/_denoise.py` | — | 2026 | — | source | https://github.com/scikit-image/scikit-image/blob/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/restoration/_denoise.py | 2026-10-10 |
| S26 | T3 | OpenJPEG source at commit 8314119: `src/lib/openjp2/dwt.c`, `openjpeg.c`, `openjpeg.h`, `opj_common.h`, `tcd.c` | — | 2026 | — | source | https://github.com/uclouvain/openjpeg/tree/8314119b067c0fc77834731168daaebd379fdb12/src/lib/openjp2 | 2026-10-10 |
| S27 | T2 | Pillow handbook, "Image file formats: JPEG 2000", and `src/libImaging/Jpeg2KEncode.c`, at commit c15d19b | — | 2026 | — | official-docs | https://github.com/python-pillow/Pillow/blob/c15d19b957327d8e00b1e60084fb1c70573ba63e/docs/handbook/image-file-formats.rst | 2026-10-10 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | search:wavelet image processing review tutorial, sorted by citations | full-text search misfired (SciPy, IoT surveys); one hit worth keeping: Vetterli & Kovačević's *Wavelets and Subband Coding*, open EPFL manuscript (not needed in the end) |
| 2 | 1 | OpenAlex | search:wavelets and signal processing tutorial; search:wavelet theory demystified | full-text noise again; switched to title filters |
| 3 | 1 | OpenAlex | title.search:wavelets and signal processing, by citations | the survey: Rioul & Vetterli 1991 IEEE SPM (2,793 citations) became S23; Mallat's *Wavelet Tour* (book) |
| 4 | 1 | OpenAlex | title.search:wavelet theory demystified | Unser & Blu 2003 IEEE TSP, open on EPFL; became S08 |
| 5 | 1 | OpenAlex | title.search:theory for multiresolution signal decomposition | Mallat 1989 TPAMI (21,467 citations); became S01 |
| 6 | 1 | OpenAlex | title.search:orthonormal bases of compactly supported wavelets | Daubechies 1988 CPAM (8,234 citations); became S02 |
| 7 | 1 | OpenAlex | title.search:biorthogonal bases of compactly supported wavelets | Cohen, Daubechies & Feauveau 1992 CPAM; became S03 |
| 8 | 1 | OpenAlex | title.search:lifting scheme custom-design construction | Sweldens 1996 ACHA; ScienceDirect PDF 403 to curl, so lifting is cited through S04, which reviews it |
| 9 | 1 | OpenAlex | title.search:factoring wavelet transforms into lifting steps | Daubechies & Sweldens 1998 JFAA; became S04 |
| 10 | 1 | OpenAlex | title.search:wavelet transforms that map integers to integers | Calderbank et al. 1998 ACHA; became S05 |
| 11 | 1 | OpenAlex | title.search:JPEG 2000 still image compression standard | Skodras et al. 2001 IEEE SPM (1,813 citations) became S06; Christopoulos et al. 2000 overview (not needed) |
| 12 | 1 | OpenAlex | title.search:mathematical properties of the JPEG2000 wavelet filters | Unser & Blu 2003 IEEE TIP, open on EPFL; became S07 |
| 13 | 1 | OpenAlex | title.search:tutorial on modern lossy wavelet image compression | Usevitch 2001 IEEE SPM, abstract only; became S19 |
| 14 | 1 | OpenAlex | title.search:image coding using wavelet transform | Antonini et al. 1992 IEEE TIP (3,532 citations); full text on Duke page; became S17 |
| 15 | 1 | OpenAlex | title.search:sub-band coding of digital images using symmetric short kernel filters | Le Gall & Tabatabai, ICASSP 1988; abstract only; became S18 |
| 16 | 1 | OpenAlex | title.search:ideal spatial adaptation by wavelet shrinkage; de-noising by soft-thresholding | Donoho & Johnstone 1994 Biometrika (S13, abstract) and Donoho 1995 IEEE TIT (S11) |
| 17 | 1 | OpenAlex | title.search:adaptive wavelet thresholding for image denoising | Chang, Yu & Vetterli 2000 (BayesShrink), abstract only; became S14 |
| 18 | 4 | OpenAlex | title.search:shiftable multiscale transforms | Simoncelli et al. 1992 IEEE TIT, abstract only; became S15 |
| 19 | 4 | OpenAlex | title.search:translation-invariant de-noising; stationary wavelet transform and some statistical applications | Coifman & Donoho 1995 and Nason & Silverman 1995: no abstract, no reachable copy; not cited |
| 20 | 4 | OpenAlex | title.search:complex wavelets for shift invariant analysis; dual-tree complex wavelet transform | Kingsbury 2001 ACHA (ScienceDirect 403); Selesnick, Baraniuk & Kingsbury 2005 IEEE SPM, open NYU copy; became S16 |
| 21 | 1 | OpenAlex | title.search:steerable pyramid flexible architecture | Simoncelli & Freeman 1995 ICIP abstract; gives no redundancy figure, so not cited |
| 22 | 1 | OpenAlex | title.search:JPEG still picture compression standard | Wallace 1991 CACM (ACM 403) and the revised 1992 IEEE TCE version; became S09 |
| 23 | 1 | ITU website | T.800 recommendation page and PDF | itu.int firewall rejected curl and WebFetch; the dms_pubrec table of contents (2019) was readable: Annex F holds 1D_EXTR, 1D_FILTR5-3R and 1D_FILTR9-7I |
| 24 | 1 | Web search | "T.800" JPEG 2000 core coding system pdf Annex F "5-3 reversible" | ISO/IEC CD 15444-1 (Dec 1999) on a University of Delaware course page; became S10 |
| 25 | 1 | Web search | Skodras Christopoulos Ebrahimi JPEG 2000 pdf | University of Crete copy of the 2001 SPM article (EPFL handle returned 405) |
| 26 | 1 | Web search | Wallace JPEG still picture compression standard pdf | NUS course copy of the submitted IEEE TCE version |
| 27 | 1 | Web search | Daubechies Sweldens factoring lifting pdf | Daubechies' Duke page; the same page held Daubechies 1988, CDF 1992, Antonini 1992 and part of Calderbank 1998 |
| 28 | 1 | Web search | Donoho Johnstone ideal spatial adaptation pdf | statweb.stanford.edu did not answer (no HTTP status); web.stanford.edu hosts Donoho 1995 and Asymptopia (S12); the 1994 Biometrika paper was not found there |
| 29 | 1 | Web search | Mallat 1989 multiresolution signal decomposition pdf | the author's own copy on di.ens.fr |
| 30 | 1 | OpenAlex | forward chase: cites:W2132984323 (Mallat) with "shift invariant" in the title | 42 citing works; Kingsbury 2001 (1,680 citations) first, then the DT-CWT shift-invariance follow-ups |
| 31 | 1 | OpenAlex | forward chase: cites:W2132984323 with "translation" in the title | translation-invariant shrinkage follow-ups (2013, 1999, 2000); none changes a claim here |
| 32 | 1 | OpenAlex | forward chase: cites:W4251101141 (Daubechies–Sweldens) with "integer" in the title | 115 works: lossless coding with integer wavelets, reversible watermarking, matrix factorisations for reversible integer mapping — confirms the integer path is mainstream, nothing contradicts S04/S05 |
| 33 | 1 | OpenAlex | forward chase: cites:W2130561641 (Unser–Blu JPEG2000) with "JPEG" in the title | 2 works, neither relevant |
| 34 | 1 | Semantic Scholar | citations of DOI 10.1007/BF02476026, influential only; then title search "factoring wavelet transforms into lifting steps" | 404 on the DOI route, then 429 (rate limit) for the rest of the session; logged as blocked |
| 35 | 1 | arXiv | ti:lifting AND ti:wavelet | recent variants only (directional lifting, adaptive lifting for video, lifting in graph and spherical CNNs); learned and adaptive transforms are out of the series' scope |
| 36 | 1 | Google Scholar | wavelet image denoising review | surveys: Fan et al. 2019 (1,044 citations), Halidou et al. 2023 (219); both confirm the VisuShrink → SureShrink → BayesShrink line the post follows; not cited |
| 37 | 4 | OpenAlex | title.search:JPEG 2000 JPEG comparison | Ebrahimi, Chamik & Winkler 2004 (SPIE): JPEG slightly ahead at low compression ratios; became S20 |
| 38 | 4 | Google Scholar | JPEG 2000 versus JPEG subjective quality comparison | Ebrahimi et al. again (118 citations); Allen/Triantaphillidou et al. 2007 JIST parts I and II (scene dependency) — part II became S21 |
| 39 | 1 | Crossref | DOI checks: 10.1109/79.952804, 10.1109/30.125072, 10.1109/MSP.2005.1550194, 10.1117/12.564835, 10.1111/j.2517-6161.1995.tb02032.x, 10.1007/BF02476026 | venues, volumes, issues and pages confirmed for S06, S09, S16, S20, S12, S04 |
| 40 | 5 | GitHub | PyWavelets, scikit-image, OpenJPEG, Pillow at the head commits named above | the extension modes, length rule, filter tables, threshold rules, default parameters and the 5/3 and 9/7 code quoted in the claims |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Baseline JPEG treats each 8×8 block of samples as a separate 64-point signal and turns it into 64 DCT coefficients, one DC and 63 AC | S09 §4, §4.1 | DCT-based sequential modes |
| L02 | JPEG 2000 compresses tiles independently, as if they were separate images; a tile can be as large as the whole image; smaller tiles give more tiling artefacts, over 4.5 dB worse at 0.125 b/p for 64×64 tiles against no tiling | S06 "Image Tiling", Table 1 | Part I; one test image ("ski", 720×576) |
| L03 | JPEG 2000 removed JPEG's best-known defect, its blocking artefacts | S07 §I | — |
| L04 | JPEG 2000 Part I allows two wavelets: the Daubechies 9/7 for lossy coding and the LeGall 5/3, whose coefficients are rational, for reversible coding; both are specified as lifting | S07 §I; S06 "Wavelet Transform" | Part I |
| L05 | An orthogonal wavelet representation of an N-pixel image has exactly N coefficients; a correlated pyramid such as the Laplacian pyramid has 2 times as many in one dimension and 4/3 as many in two | S01 pp. 684–685 | — |
| L06 | The Laplacian pyramid's levels are correlated, and it has no orientation selectivity | S01 p. 675 | — |
| L07 | The wavelet representation sits between the spatial and Fourier domains, is computed by a pyramidal algorithm of filter convolutions, and gives three detail images per level, one per orientation; Mallat handled image borders by symmetric extension | S01 abstract, pp. 683–685 | — |
| L08 | JPEG 2000's reversible 5/3 lifting: each odd sample loses the floor of the mean of its two even neighbours, then each even sample gains the floor of (left detail + right detail + 2)/4 | S06 eqs. (3a), (3b) | extended signal |
| L09 | JPEG 2000 extends a signal by whole-sample symmetric reflection about its first and last samples, which appear once — type (1,1) — because both kernels have odd length | S06 "Wavelet Transform", Fig. 7; S10 F.2.7 | — |
| L10 | OpenJPEG's forward 5/3 row code computes exactly those two steps, with the end samples' missing neighbours taken from the mirror | S26 `dwt.c`, `opj_dwt_encode_and_deinterleave_h_one_row` | commit 8314119; even-start rows |
| L11 | The 5/3 analysis filters are low-pass (−1, 2, 6, 2, −1)/8 and high-pass (−1/2, 1, −1/2); the synthesis low-pass (1/2, 1, 1/2) is the linear B-spline | S06 Table 4; S07 §V-A | — |
| L12 | The 5/3 path codes losslessly as long as the decoded values are not clipped; quantisation is lossy except with step 1 on the 5/3's integer coefficients | S06 "Wavelet Transform", "Quantization" | — |
| L13 | PyWavelets' DWT returns floor((N + L − 1)/2) coefficients per band for a filter of length L in every mode except periodization, which returns ceil(N/2); the default mode is `symmetric` | S24 `_dwt.py` `dwt_coeff_len`, `common.c` `dwt_buffer_length` | commit c9b542b |
| L14 | PyWavelets stores Haar as two taps, `bior2.2` as six (the 5/3 low-pass times √2, padded with a zero) and `bior4.4` as ten (the 9/7 low-pass times √2) | S24 `wavelets.c`, `wavelets_coeffs.template.h` | commit c9b542b |
| L15 | In PyWavelets `symmetric` is half-sample symmetric (the end sample repeats), `reflect` is whole-sample symmetric, the non-periodization modes are slightly redundant, and periodization gives the fewest coefficients | S24 `signal-extension-modes.rst` | commit c9b542b |
| L16 | Lifting predicts each odd sample from its even neighbours and keeps the error; an update then adds a quarter of the neighbouring errors to the evens so the coarse signal keeps the running average; the two-step construction is the biorthogonal (2,2) transform of Cohen–Daubechies–Feauveau | S04 §1–2, Fig. 2 | — |
| L17 | Every two-band FIR filter bank factors into lifting steps; lifting asymptotically halves the arithmetic, runs in place without extra memory, and makes integer-to-integer transforms easy | S04 abstract, §6, §9 | — |
| L18 | The 9-7 pair has 9 analysis and 7 synthesis taps, both high-pass filters have four vanishing moments, and it factors into four lifting steps with α ≈ −1.586134342, β ≈ −0.05298011854, γ ≈ 0.8829110762, δ ≈ 0.4435068522 plus a scaling | S04 §7.7 | — |
| L19 | Operations per sample pair: Haar 3 standard, 3 lifting; 9-7 23 standard, 14 lifting, a 64% speed-up; asymptotically lifting is twice as fast | S04 Table 1.1 | multiplications plus additions |
| L20 | OpenJPEG's 9/7 encoder uses α = −1.586134342, β = −0.052980118, γ = 0.882911075, δ = 0.443506852 and K = 1.230174105, multiplying the high band by K and the low band by 1/K | S26 `dwt.c` | commit 8314119 |
| L21 | The JPEG 2000 9/7 analysis low-pass taps are 0.6029490, ±0.2668641, ±−0.0782233, ±−0.0168641, ±0.0267488; high-pass 1.1150871, ±−0.5912718, ±−0.0575435, ±0.0912718 | S06 Table 3 | — |
| L22 | The S-transform is a non-orthonormal Haar that maps integers to integers; combining lifting with reversible rounding gives a large family of integer wavelet transforms for lossless coding | S05 §1, §2.1 | introduction and §2 read |
| L23 | Orthonormal filters with N vanishing moments and minimal length have real coefficients, with no closed form beyond N = 3, so integer inputs give non-integer outputs | S05 §1 | — |
| L24 | Daubechies' compactly supported orthonormal wavelets: the Nth filter has 2N coefficients and support [0, 2N − 1]; regularity grows linearly with support; apart from Haar, none is symmetric or antisymmetric | S02 §4, discussion of Fig. 5 | — |
| L25 | Allowing different analysis and synthesis filters gives biorthogonal bases with symmetric (linear-phase) filters, which is impossible when the two coincide | S03 abstract, §1.D | — |
| L26 | The Haar basis is the oldest orthonormal wavelet basis; Haar's paper appeared in Mathematische Annalen in 1910 | S03 §1; S22 | — |
| L27 | The LeGall 5/3 is the shortest symmetric biorthogonal pair with two vanishing moments | S07 §I, §V-A | — |
| L28 | The 9/7 has four vanishing moments and is very nearly orthonormal: Riesz bounds 0.926–1.065 (analysis) and 0.943–1.084 (synthesis) | S07 §V-B, Table II | — |
| L29 | Vanishing moments let a wavelet transform kill polynomials, so coefficients are essentially zero wherever the signal is close to a low-degree polynomial; the result is long runs of zeros that code cheaply | S08 §III-D | — |
| L30 | A piecewise-smooth image's wavelet coefficients split into large ones near edges and small ones in smooth regions, and magnitudes persist across scales | S07 §III | — |
| L31 | Antonini et al. coded images with a biorthogonal wavelet pyramid that keeps the pixel count constant, using a 9-7 filter pair | S17 abstract, Figs. 14, 18–20 | — |
| L32 | Le Gall and Tabatabai designed short symmetric subband filters that need only simple additions and multiplications | S18 abstract | abstract only |
| L33 | Orthogonal filters preserve energy; modern wavelet coders use biorthogonal filters, which do not; boundary effects are what motivate them | S19 abstract | abstract only |
| L34 | JPEG 2000 names subbands by horizontal then vertical filtering: HL is high-pass horizontally and low-pass vertically; a decomposition of N_L levels has 3N_L + 1 subbands | S10 F.2.9; S26 `tcd.c` band numbering | — |
| L35 | `pywt.dwt2` returns (cA, (cH, cV, cD)), and "horizontal" refers to array axis 0: cH is the detail across rows | S24 `_multidim.py` | commit c9b542b |
| L36 | PyWavelets' Haar high-pass is (−1/√2, +1/√2), so its detail coefficient is (left − right)/√2 | S24 `wavelets.c`, `convolution.template.c` | commit c9b542b |
| L37 | JPEG 2000 Part I allows only dyadic decompositions; discarding one level's HL, LH and HH subbands halves the image in each direction | S06 "Wavelet Transform", "Multiple Component Transformation" | Part I |
| L38 | OpenJPEG defaults to 6 resolutions (5 decomposition levels), 64×64 code-blocks and the reversible 5/3 unless `irreversible` is set | S26 `openjpeg.c`, `openjpeg.h`, `opj_common.h` | commit 8314119 |
| L39 | Pillow's JPEG 2000 writer uses the lossless 5-3 unless `irreversible=True`; `num_resolutions` is decompositions plus one; no tiling unless `tile_size` is given; setting `reduce` before load discards resolutions, each halving the size; without `num_resolutions` Pillow lowers OpenJPEG's 6 until 2^(n−1) fits the tile | S27 handbook, `Jpeg2KEncode.c` | commit c15d19b |
| L40 | On a natural image JPEG 2000 measured about 2 dB above JPEG at every compression ratio; the advantage shrinks as the bit rate rises; in a visual study its files were 11% smaller at 1.0 b/p, 18% at 0.75, 36% at 0.5 and 53% at 0.25 | S06 "Lossy Compression Results", Fig. 19 | one image for the PSNR curve; the size figures are the study S06 cites as [37] |
| L41 | On 29 images, using predicted mean opinion scores, JPEG had a slight edge at low compression ratios and JPEG 2000 was clearly better at medium and high ratios | S20 abstract | IrfanView encoders; abstract only |
| L42 | Subjective quality of both JPEG and JPEG 2000 depends on scene content | S21 abstract | abstract only |
| L43 | The content of orthogonal wavelet subbands is unstable under translation of the input (and under dilation and rotation); shiftability corresponds to the absence of aliasing | S15 abstract | abstract only |
| L44 | Real wavelets oscillate around singularities; a small shift greatly changes the coefficients; downsampling after non-ideal filters aliases, and the inverse cancels that only if the coefficients are left unchanged, so thresholding or quantisation leaves artefacts; the separable HH wavelet is a checkerboard mixing +45° and −45° | S16 "Four problems", Fig. 2 | — |
| L45 | The dual-tree complex wavelet transform runs two real trees whose wavelets form an approximate Hilbert transform pair; it is nearly shift-invariant and separates six orientations in 2-D at a redundancy of 2^d (2 in 1-D, 4 in 2-D); the undecimated DWT is redundant by J + 1 for J stages; a perfectly shift-invariant DWT costs log2 N | S16 abstract, intro, "Undecimated" discussion | — |
| L46 | The Fourier transform's magnitude is perfectly shift-invariant, the shift showing only as a linear phase | S16 "One solution" | — |
| L47 | Soft thresholding is sgn(y)·max(abs(y) − t, 0); Donoho and Johnstone's VisuShrink uses t = σ√(2 log n) on orthonormal coefficients; the largest of n independent standard normals stays below √(2 log n) with probability tending to 1; the soft-thresholded estimate is, with high probability, at least as smooth as the truth | S11 §1, §4 eq. (4.1), [Smooth] | i.i.d. Gaussian noise |
| L48 | In practice only the detail coefficients are shrunk, not the coarse ones; an unknown σ is estimated as the median absolute finest-scale coefficient divided by 0.6745 | S12 §3.1 | — |
| L49 | BayesShrink derives a closed-form threshold per subband in a Bayesian framework with a generalised Gaussian prior, and comes within about 5% of the MSE of the best soft-threshold benchmark | S14 abstract | abstract only |
| L50 | scikit-image's `denoise_wavelet` defaults: Haar (`db1`), soft mode, BayesShrink, the maximum level count minus 3; only detail arrays are thresholded; VisuShrink's threshold is σ√(2 ln size); BayesShrink's is σ²/√(max(var − σ², ε)); σ is the median absolute finest diagonal coefficient over Φ⁻¹(0.75), skipping exact zeros; it warns for non-orthogonal wavelets; `estimate_sigma` uses `db2` | S25 | commit b700edc |
| L51 | `pywt.threshold` defaults to soft; hard leaves values at or above the threshold untouched | S24 `_thresholding.py` | commit c9b542b |
| L52 | PyWavelets' stationary transform `swt` needs the axis length to be a multiple of 2^level | S24 `_swt.py` | commit c9b542b |
| L55 | After quantisation, JPEG 2000 entropy-codes the bit planes of each code block's coefficients with an adaptive binary arithmetic coder (the MQ coder) | S06 architecture list, "Entropy Coding" | Part I |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S01 | Fig. 12 (image decomposition block diagram) | One level in 2-D / L07 | shows the row-then-column filter bank | IEEE copyright, no licence found | https://doi.org/10.1109/34.192463 | do not reuse; our Figure 4 computes the same level on the patch instead |
| F2 | S06 | Fig. 7 (periodic symmetric extension of "ABCDEFG") | Worked example / L09 | shows the mirror | IEEE copyright, no licence found | https://doi.org/10.1109/79.952804 | do not reuse; Figure 1 draws the mirrored sample on the patch's own row |
| F3 | S06 | Fig. 8 (forward lifting, P and U) | Lifting / L08 | the lifting structure | IEEE copyright, no licence found | https://doi.org/10.1109/79.952804 | do not reuse; Figure 7 carries the r2 row's own values through forward and inverse |
| F4 | S04 | Fig. 2 (geometric view of the update) | Lifting / L16 | why the update is d/4 | Springer copyright, no licence found | https://doi.org/10.1007/BF02476026 | do not reuse; explained in prose |
| F5 | S16 | Fig. 2 (shift variance of a step's coefficients) | Shift variance / L44 | the step's coefficients change with shift | IEEE copyright, no licence found | https://doi.org/10.1109/MSP.2005.1550194 | do not reuse; Figure 8 shows the same effect on the patch's row |

## Open questions

- The normative ITU-T T.800 text was unreachable. The post never quotes it; every rule it states
  is confirmed by Skodras et al. and by OpenJPEG's source.
- Skodras et al.'s file-size percentages come from a visual comparison study they cite as [37];
  the post attributes them to Skodras et al.'s report and gives the bit rates.
- Coifman and Donoho's cycle spinning could not be read, so the post names the undecimated
  transform and the dual tree as the remedies, with Selesnick et al.'s redundancy figures, and does
  not describe cycle spinning.
- The 9/7's scaling constant differs by normalisation between sources (Daubechies–Sweldens
  ζ ≈ 1.1496, the 1999 draft 1.149604, OpenJPEG 1.230174105). The post quotes OpenJPEG's, the one
  that reproduces Skodras et al.'s Table 3 taps exactly (low band × 1/K), as checked in the private
  cross-check.
