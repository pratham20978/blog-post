# Source ledger — the-2d-dft-spectra-phase-filtering

Series `image-processing`, part 5. Sweep run 2026-10-10. Tier L4, so the floor is 10
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

How each source was read is stated per row, because it varies. Read in full as PDFs
(`pdftotext`): Hayes, Lim & Oppenheim 1980 (MIT DSP group's copy), Moisan (author's preprint),
Sur & Grédiac (author's copy), Galerne, Gousseau & Morel (IPOL, open), Cooley & Tukey (AMS, open),
Johnson & Frigo (author's copy on fftw.org), Field 1987 (a course-page copy; the DOI is what the
post cites) and the Skarbnik–Zeevi–Sagiv review (Technion CCIT report). Gonzalez & Woods was read
only where the publisher's sample chapters reach: the detailed table of contents and pp. 249–252,
307, 309 and 348; every claim row names the page. Six peer-reviewed sources were not reachable in
full and are used **only for what their abstracts state** (retrieved from the OpenAlex record,
venue and pages cross-checked against Crossref): Oppenheim & Lim 1981, Hayes 1982, Lohmann et al.
1997, Harris 1978, Stockham 1966 and Foroosh et al. 2002. Their claim rows say so in the Condition
column, and the post leans on them for nothing beyond the abstract.

Library behaviour was read at pinned commits: OpenCV `802cf95aa3d4` (2026-10-10), NumPy
`70fa99843c75` (2026-10-09), SciPy `95e01a4004e2` (2026-10-10), scikit-image `b700edc8005e`
(2026-10-09). Nothing was executed against an image. The only code run was plain Python (`math`
and `cmath`, no packages) that reproduces the post's hand-worked numbers: the patch's 2-D DFT, the
phase and magnitude reconstructions, the swap, the notch and the cost models.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Oppenheim & Lim, "The Importance of Phase in Signals" (abstract only) | Proc. IEEE 69(5), pp. 529–541 | 1981 | 10.1109/PROC.1981.12022 | peer-reviewed | https://doi.org/10.1109/PROC.1981.12022 | 2026-10-10 |
| S02 | T1 | Hayes, Lim & Oppenheim, "Signal Reconstruction from Phase or Magnitude" | IEEE Trans. ASSP 28(6), pp. 672–680 | 1980 | 10.1109/TASSP.1980.1163463 | peer-reviewed | https://dsp-group.mit.edu/wp-content/uploads/2024/11/signrecons_1980.pdf | 2026-10-10 |
| S03 | T1 | Hayes, "The Reconstruction of a Multidimensional Sequence from the Phase or Magnitude of Its Fourier Transform" (abstract only) | IEEE Trans. ASSP 30(2), pp. 140–154 | 1982 | 10.1109/TASSP.1982.1163863 | peer-reviewed | https://doi.org/10.1109/TASSP.1982.1163863 | 2026-10-10 |
| S04 | T1 | Lohmann, Mendlovic & Shabtay, "Significance of Phase and Amplitude in the Fourier Domain" (abstract only) | J. Opt. Soc. Am. A 14(11), p. 2901 | 1997 | 10.1364/JOSAA.14.002901 | peer-reviewed | https://doi.org/10.1364/JOSAA.14.002901 | 2026-10-10 |
| S05 | T1 | Galerne, Gousseau & Morel, "Micro-Texture Synthesis by Phase Randomization" | Image Processing On Line 1, pp. 213–237 | 2011 | 10.5201/ipol.2011.ggm_rpn | peer-reviewed | https://www.ipol.im/pub/art/2011/ggm_rpn/article.pdf | 2026-10-10 |
| S06 | T1 | Field, "Relations between the Statistics of Natural Images and the Response Properties of Cortical Cells" | J. Opt. Soc. Am. A 4(12), pp. 2379–2394 | 1987 | 10.1364/JOSAA.4.002379 | peer-reviewed | https://doi.org/10.1364/JOSAA.4.002379 | 2026-10-10 |
| S07 | T1 | Moisan, "Periodic Plus Smooth Image Decomposition" (read as the author's preprint) | J. Math. Imaging and Vision 39(2), pp. 161–179 | 2011 | 10.1007/s10851-010-0227-1 | peer-reviewed | https://helios2.mi.parisdescartes.fr/~moisan/papers/2009-11r.pdf | 2026-10-10 |
| S08 | T1 | Sur & Grédiac, "Automated Removal of Quasiperiodic Noise Using Frequency Domain Statistics" | J. Electronic Imaging 24(1), 013003 | 2015 | 10.1117/1.JEI.24.1.013003 | peer-reviewed | https://members.loria.fr/FSur/articles/sur15automated.pdf | 2026-10-10 |
| S09 | T1 | Cooley & Tukey, "An Algorithm for the Machine Calculation of Complex Fourier Series" | Math. Comp. 19(90), pp. 297–301 | 1965 | 10.1090/S0025-5718-1965-0178586-1 | peer-reviewed | https://www.ams.org/journals/mcom/1965-19-090/S0025-5718-1965-0178586-1/S0025-5718-1965-0178586-1.pdf | 2026-10-10 |
| S10 | T1 | Johnson & Frigo, "A Modified Split-Radix FFT with Fewer Arithmetic Operations" | IEEE Trans. Signal Processing 55(1), pp. 111–119 | 2007 | 10.1109/TSP.2006.882087 | peer-reviewed | https://www.fftw.org/newsplit.pdf | 2026-10-10 |
| S11 | T1 | Frigo & Johnson, "The Design and Implementation of FFTW3" (abstract and introduction) | Proc. IEEE 93(2), pp. 216–231 | 2005 | 10.1109/JPROC.2004.840301 | peer-reviewed | https://www.fftw.org/fftw-paper-ieee.pdf | 2026-10-10 |
| S12 | T1 | Stockham, "High-Speed Convolution and Correlation" (abstract only) | AFIPS Spring Joint Computer Conference, p. 229 | 1966 | 10.1145/1464182.1464209 | peer-reviewed | https://doi.org/10.1145/1464182.1464209 | 2026-10-10 |
| S13 | T1 | Gonzalez & Woods, *Digital Image Processing*, 4th ed. (TOC and sample chapters: pp. 249–252, 307, 309, 348) | Pearson | 2018 | ISBN 978-0-13-335672-4 | standard | https://imageprocessingplace.com/downloads_V3/dip4e_downloads/dip4e_sample_book_material/dip4e_sample_chapters.pdf | 2026-10-10 |
| S14 | T1 | Harris, "On the Use of Windows for Harmonic Analysis with the Discrete Fourier Transform" (abstract only) | Proc. IEEE 66(1), pp. 51–83 | 1978 | 10.1109/PROC.1978.10837 | peer-reviewed | https://doi.org/10.1109/PROC.1978.10837 | 2026-10-10 |
| S15 | T1 | Foroosh, Zerubia & Berthod, "Extension of Phase Correlation to Subpixel Registration" (abstract only) | IEEE Trans. Image Processing 11(3), pp. 188–200 | 2002 | 10.1109/83.988953 | peer-reviewed | https://doi.org/10.1109/83.988953 | 2026-10-10 |
| S16 | T1 | Skarbnik, Zeevi & Sagiv, "The Importance of Phase in Image Processing", CCIT Report #773 | Technion tech. report | 2010 | CCIT Report 773 | preprint | https://ece.technion.ac.il/wp-content/uploads/2021/01/publication_773-1.pdf | 2026-10-10 |
| S17 | T2 | FFTW, "FFT Benchmark Methodology" (benchFFT) | — | 2026 | — | official-docs | https://www.fftw.org/speed/method.html | 2026-10-10 |
| S18 | T3 | OpenCV source, `modules/imgproc/src/filter.dispatch.cpp` | — | 2026 | commit 802cf95aa3d4 | source | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/src/filter.dispatch.cpp | 2026-10-10 |
| S19 | T2 | OpenCV 4.x documentation — `filter2D` (Image Filtering) and `phaseCorrelate` (Motion Analysis), generated from `imgproc.hpp` | — | 2026 | imgproc.hpp @ 802cf95aa3d4 | official-docs | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/imgproc/include/opencv2/imgproc.hpp | 2026-10-10 |
| S20 | T2 | OpenCV 4.x documentation — `dft`, `DftFlags`, `getOptimalDFTSize`, `mulSpectrums` (Operations on arrays), generated from `core.hpp` and `core/base.hpp` | — | 2026 | core.hpp, base.hpp @ 802cf95aa3d4 | official-docs | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/modules/core/include/opencv2/core.hpp | 2026-10-10 |
| S21 | T3 | OpenCV tutorial sample, `samples/cpp/tutorial_code/core/discrete_fourier_transform/discrete_fourier_transform.cpp` | — | 2026 | commit 802cf95aa3d4 | source | https://github.com/opencv/opencv/blob/802cf95aa3d42816995695bf68a86b3532f12760/samples/cpp/tutorial_code/core/discrete_fourier_transform/discrete_fourier_transform.cpp | 2026-10-10 |
| S22 | T2 | NumPy documentation — `numpy.fft.fftshift`, `ifftshift`, `fftfreq` (docstrings in `numpy/fft/_helper.py`) | — | 2026 | commit 70fa99843c75 | official-docs | https://github.com/numpy/numpy/blob/70fa99843c75ae12434805bb4b1b07b94598c5c9/numpy/fft/_helper.py | 2026-10-10 |
| S23 | T2 | NumPy documentation — `numpy.fft` normalisation, `fft2`, `rfft2` (docstrings in `numpy/fft/_pocketfft.py`) | — | 2026 | commit 70fa99843c75 | official-docs | https://github.com/numpy/numpy/blob/70fa99843c75ae12434805bb4b1b07b94598c5c9/numpy/fft/_pocketfft.py | 2026-10-10 |
| S24 | T3 | SciPy source, `scipy/signal/_signaltools.py` — `choose_conv_method`, `_fftconv_faster`, `_conv_ops` | — | 2026 | commit 95e01a4004e2 | source | https://github.com/scipy/scipy/blob/95e01a4004e2781c91a26d9836d82c103dd8513c/scipy/signal/_signaltools.py | 2026-10-10 |
| S25 | T3 | scikit-image source, `src/_skimage2/registration/_phase_cross_correlation.py` | — | 2026 | commit b700edc8005e | source | https://github.com/scikit-image/scikit-image/blob/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2/registration/_phase_cross_correlation.py | 2026-10-10 |
| S26 | T2 | SciPy documentation — `scipy.fft.next_fast_len` (docstring in `scipy/fft/_helper.py`) | — | 2026 | commit 95e01a4004e2 | official-docs | https://github.com/scipy/scipy/blob/95e01a4004e2781c91a26d9836d82c103dd8513c/scipy/fft/_helper.py | 2026-10-10 |

Notes on individual sources:

- **S01** is the paper the plan names and the post's framing rests on. Its full text was not
  reachable: DTIC's technical-report copy (ADA091726) returned 403 to curl and to WebFetch, and a
  third-party copy that a search returned now redirects to an unrelated dataset page. Every claim
  attributed to Oppenheim & Lim is one its abstract makes. The famous two-image swap is described
  through S16, which reproduces it and attributes it to S01.
- **S06** was read from a copy on a UCSD course page; the post cites the DOI.
- **S07** is CC-licensed nowhere that could be verified (Springer's TDM licence only), so none of
  its figures is reused; the preprint was read in full.
- **S11**: only the abstract and introduction are used, for one sentence (FFTW adapts to the
  hardware).
- **S13**: the 4th edition's sample-chapter PDF is a selection of pages, not whole chapters. The
  cost model (pp. 250–252), the filtering equation and centring (p. 307), the padding comparison
  (p. 309) and Example 4.25 on notch filtering (p. 348) were read; the TOC confirms §4.10 (notch
  filters) and §5.4 (periodic noise reduction, optimum notch filtering), whose pages were not
  available. Nothing is attributed to those sections beyond the fact that they exist.
- **S16** is a technical report, not journal-reviewed, so it is marked `preprint` and named in the
  post as a Technion report.
- **S19 / S20**: `docs.opencv.org` was not fetched; the documentation pages are generated by
  Doxygen from the header comments, which were read at the pinned commit.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | title.search:importance of phase in signals, sorted by citations | Oppenheim & Lim 1981 Proc. IEEE (1,881 citations) became S01; Ni & Huo 2006 (statistical interpretation, no abstract, not used) |
| 2 | 1 | OpenAlex | title.search:fast fourier transforms tutorial review | Duhamel & Vetterli 1990 Signal Processing survey (1,152 citations) — the FFT survey; see row 29 |
| 3 | 1 | OpenAlex | title.search:machine calculation of complex fourier series | Cooley & Tukey 1965 Math. Comp. (12,462 citations), AMS open PDF; became S09 |
| 4 | 1 | OpenAlex | forward chase: cites:W264456315 (Oppenheim & Lim) with "phase" in the title, by citations | 623 citing works; Morrone & Burr 1988 (phase-dependent energy model), Galerne et al. 2010 (random phase textures), Wang & Lim 1982 ("the unimportance of phase" in speech), Horner & Gianino 1984 (phase-only matched filter) |
| 5 | 4 | OpenAlex | forward chase: cites:W264456315 with "amplitude" in the title | Tolhurst et al. 1992 (amplitude spectra of natural images); Guyader et al. 2004 (rapid scene categorisation is amplitude-based) — the counterpoint line |
| 6 | 1 | OpenAlex | title.search:signal reconstruction from phase or magnitude | Hayes, Lim & Oppenheim 1980 IEEE TASSP 28(6) (376 citations), open MIT DSP group copy; became S02 |
| 7 | 1 | OpenAlex | title.search:reconstruction of a multidimensional sequence from the phase or magnitude | Hayes 1982 IEEE TASSP 30(2) (437 citations), abstract only; became S03 |
| 8 | 4 | OpenAlex | title.search:significance of phase and amplitude in the Fourier domain | Lohmann, Mendlovic & Shabtay 1997 JOSA A 14(11): symmetry and one changed pixel can change which of phase and amplitude matters; abstract only; became S04 |
| 9 | 1 | OpenAlex | title.search:feature detection from local energy | Morrone & Owens 1987 Pattern Recognition Letters (656 citations), no abstract or open copy; its idea is cited through S16 |
| 10 | 1 | DTIC and a lab web server | Oppenheim & Lim 1981 full text (DTIC ADA091726; a third-party copy found by web search) | DTIC 403 to curl and WebFetch; the third-party copy redirects to a dataset page; S01 used for its abstract only |
| 11 | 1 | Google Scholar | "the importance of phase in signals" | Oppenheim & Lim cluster and its "all versions" list (no open full text); Skarbnik, Zeevi & Sagiv 2010 CCIT report (Technion PDF), a review that reproduces the swap — became S16; Lohmann 1997 on Optica (paywalled) |
| 12 | 1 | OpenAlex | title.search:periodic plus smooth image decomposition | Moisan, JMIV 39(2) (107 citations) — the boundary cross and its removal; the author's preprint became S07 |
| 13 | 1 | OpenAlex | title.search:use of windows for harmonic analysis with the discrete fourier transform | Harris 1978 Proc. IEEE 66(1) (7,314 citations), abstract only; became S14 |
| 14 | 1 | OpenAlex | title.search:relations between the statistics of natural images and the response properties of cortical cells | Field 1987 JOSA A 4(12) (3,280 citations): natural-image amplitude falls roughly as 1/f; became S06 |
| 15 | 1 | OpenAlex | title.search:image features from phase congruency | Kovesi 1999 (1,109 citations), no DOI; the Videre PDF returned 403 (row 20) |
| 16 | 1 | OpenAlex | title.search:phase correlation image alignment | Kuglin & Hines 1975 (1,096 citations), no DOI, no venue record, no copy; cited through S25 |
| 17 | 1 | OpenAlex | title.search:extension of phase correlation to subpixel registration | Foroosh, Zerubia & Berthod 2002 IEEE TIP 11(3) (981 citations), abstract only; became S15 |
| 18 | 1 | OpenAlex | title.search:removal of quasiperiodic noise | Sur & Grédiac 2015 J. Electronic Imaging 24(1); HAL served a bot wall, the author's page served the PDF; became S08 |
| 19 | 4 | OpenAlex | title.search:periodic noise AND title.search:frequency domain, by citations | Aizenberg & Butakoff 2002 (median-like spectral filter) and adaptive notch variants 2012–2022; none replaces notch filtering, all still locate spikes first |
| 20 | 1 | web search | author copies: Moisan preprint, Field 1987, Kovesi 1999 | Moisan's own preprint (read); Field 1987 on a UCSD course page (read); Kovesi's Videre PDF 403 |
| 21 | 3 | OpenAlex | title.search:modified split-radix FFT with fewer arithmetic operations | Johnson & Frigo, IEEE TSP 55(1) 2007: exact flop counts, Yavne's split radix 4N lg N − 6N + 8, 20% under radix-2; became S10 |
| 22 | 3 | OpenAlex | title.search:design and implementation of FFTW3 | Frigo & Johnson 2005 Proc. IEEE 93(2) (5,162 citations); became S11 |
| 23 | 3 | OpenAlex | title.search:high-speed convolution and correlation | Stockham 1966 AFIPS SJCC (320 citations), FFT-based convolution; became S12 (abstract only, row 30) |
| 24 | 1 | OpenAlex | title.search:Gauss and the history of the fast fourier transform | Heideman, Johnson & Burrus 1984 IEEE ASSP Magazine (537 citations); no abstract or copy; not cited |
| 25 | 5 | fftw.org | FFT benchmark methodology page | the "mflops" scaling: 5 N log2 N for complex, 2.5 N log2 N for real transforms, explicitly not an actual flop count; became S17 |
| 26 | 4 | OpenAlex | title.search:micro-texture synthesis by phase randomization | Galerne, Gousseau & Morel 2011, IPOL (peer-reviewed, CC BY-NC-SA): micro-textures are characterised by their Fourier modulus; became S05 |
| 27 | 1 | Semantic Scholar | citations of DOI:10.1109/PROC.1981.12022, influential flag | answered: the 100 most recent citers, 6 flagged influential, all learned-model applications from 2026 — out of this series' scope |
| 28 | 1 | Crossref | venue and page check: Johnson & Frigo, Lohmann, Sur & Grédiac, Galerne, Moisan, Rindfleisch, Field, Hayes 1980, Frigo & Johnson, Stockham | all confirmed; Moisan is JMIV 39(2):161–179, online 2010, issue 2011 |
| 29 | 1 | ScienceDirect and EPFL infoscience | Duhamel & Vetterli 1990 full text | ScienceDirect 403, infoscience 405, and OpenAlex holds no abstract — the survey was found but not read, so it is not cited |
| 30 | 1 | ACM Digital Library | Stockham 1966 full text | 403 to curl; S12 used for its OpenAlex abstract only |
| 31 | 4 | arXiv | all:"periodic noise" AND all:notch | two hits — a deepfake-evasion preprint and a bicycle-sensor paper; nothing in image restoration newer than S08 |
| 32 | 5 | GitHub (OpenCV 802cf95) | filter.dispatch.cpp, imgproc.hpp, core.hpp, core/base.hpp, phasecorr.cpp, the DFT tutorial sample | filter2D goes to the DFT at kernel area ≥ 130 (SSE3, 8U→8U/16S or 32F→32F) or ≥ 50, never for an ROI; sepFilter2D has no DFT path; dft flags and CCS packing; getOptimalDFTSize = 2^p 3^q 5^r; phaseCorrelate's cross-power spectrum; the tutorial crops odd spectra before swapping quadrants |
| 33 | 5 | GitHub (NumPy 70fa998, SciPy 95e01a4, scikit-image b700edc) | numpy/fft/_helper.py, numpy/fft/_pocketfft.py, scipy/signal/_signaltools.py, scipy/fft/_helper.py, skimage phase_cross_correlation | fftshift rolls n//2 and ifftshift −(n//2); norm="backward" by default; SciPy's chooser compares 3·N·ln N with kernel × output under fitted constants; scikit-image defaults to phase normalisation and credits Kuglin & Hines |
| 34 | 2 | imageprocessingplace.com | Gonzalez & Woods 4e detailed TOC and sample chapters | §4.1 cost model C_n(m) = m²/(4 log2 M) and C_s(m) = m/(2 log2 M); §4.7 filtering equation; p. 309 padding; Example 4.25, notch filtering of Cassini interference; became S13 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | In a Fourier representation magnitude and phase play different roles, and in some situations many important features survive if only the phase is kept | S01 abstract | abstract only |
| L02 | Under conditions such as finite length, phase alone determines a signal up to a scale factor; the paper illustrates phase-only reconstruction for images, speech and crystallographic structures, and presents algorithms for approximate and exact reconstruction from phase | S01 abstract | abstract only |
| L03 | Two finite-length sequences whose z-transforms have no zeros in reciprocal pairs or on the unit circle, and whose Fourier phases agree, differ only by a positive scale factor | S02 Theorem 1 | real sequences, rational z-transforms; zeros on the unit circle or in reciprocal pairs break it |
| L04 | For a sequence zero outside 0…N−1, equal phase at N − 1 distinct frequencies strictly between 0 and π is enough for the same conclusion | S02 Theorems 3 and 5 | same zero conditions; Theorem 5 also needs x[0] ≠ 0 and the support known |
| L05 | Phase or magnitude alone does not specify a multidimensional sequence in general, but a large class of them is recoverable from either; in 1982 no practical magnitude-only algorithm existed | S03 abstract | abstract only |
| L06 | Very similar objects can behave radically differently when phase is discarded or amplitude flattened; symmetry strongly affects which matters, and changing one pixel can change it | S04 abstract | abstract only |
| L07 | Randomising the Fourier phase of a sample synthesises a texture; it reproduces textures characterised by their Fourier modulus — random-phase textures, or micro-textures — and most failures are macro-textures: strong edges, definite shapes, large-period or strictly periodic patterns | S05 abstract, §1, §5.1 (failure catalog) | micro-textures only |
| L08 | Randomising the phase of a non-periodic image produces strong horizontal and vertical waves, so the input is replaced by Moisan's periodic component first | S05 §2.3 | — |
| L09 | Natural-image amplitude spectra fall off roughly as 1/f, so power falls roughly as 1/f²; measured on six images | S06, Fig. 8 and text | six photographs of natural scenes, 256×256 |
| L10 | The expected power spectrum of natural images is modelled as an inverse power of frequency, with exponent near 2 for power (near 1 for amplitude); refined models let both depend on orientation | S08 §2, citing Field 1987 and later work | natural images; a statistical model, not a law for any one image |
| L11 | The two-image swap — magnitude from one, phase from the other — gives an image resembling the phase donor; the report repeats it on two photographs and attributes it to Oppenheim | S16 §Global phase, Fig. 1 | photographs; a technical report |
| L12 | Phase congruency, after Morrone & Owens' local energy, holds that features sit where Fourier components are maximally in phase | S16 §Phase congruency | as summarised by a review |
| L13 | The DFT implicitly treats the image as periodic; opposite borders rarely match, so the periodic image has strong jumps across the frame, which put a "cross" of high-energy coefficients along the axes of both modulus and phase | S07 abstract, §2.1 | any image whose opposite borders differ |
| L14 | Mirroring the image before the DFT removes the border jumps, turning the discontinuity into one of the normal derivative; the mirrored DFT equals a DCT plus a half-pixel phase shift | S07 §2.2 | — |
| L15 | The periodic-plus-smooth decomposition removes the cross and costs O(N² log N) for an N×N image via the FFT | S07 abstract, §1 | — |
| L16 | Window tapering and mirroring are the established alternatives; Harris catalogues windows and the common errors in applying them with the FFT | S14 abstract; S07 §1–2 | abstract only for S14 |
| L17 | OpenCV's DFT tutorial pads with zeros to getOptimalDFTSize, displays log(1 + magnitude), and crops an odd-sized spectrum to even before swapping quadrants | S21 lines 34–36, 49–83 | the tutorial, not the library |
| L18 | numpy.fft.fftshift rolls each axis by n//2 and ifftshift by −(n//2); they agree for even n and differ by one sample for odd n | S22 | — |
| L19 | For odd n the frequency order is 0, 1, …, (n−1)/2, −(n−1)/2, …, −1 | S22 (`fftfreq`) | — |
| L20 | NumPy's default normalisation is "backward": the forward transform is unscaled and the inverse divides by n | S23 | — |
| L21 | cv2.dft packs a real input's conjugate-symmetric result into a real array (CCS) by default; DFT_COMPLEX_OUTPUT returns the full complex array; DFT_SCALE divides by the number of elements; DFT_REAL_OUTPUT requests a real inverse | S20 (base.hpp DftFlags) | — |
| L22 | cv2.getOptimalDFTSize returns the smallest N ≥ the input size with N = 2^p 3^q 5^r | S20 | current implementation |
| L23 | OpenCV's DFT-convolution example pads both arrays to getOptimalDFTSize(A.cols + B.cols − 1) and likewise for rows | S20 (core.hpp dft example) | — |
| L24 | cv2.mulSpectrums multiplies CCS-packed or complex spectra element by element; conjB = true gives correlation | S20 | — |
| L25 | Direct evaluation of an N-point DFT takes N² operations (a complex multiply and add each); Cooley & Tukey's algorithm takes fewer than 2N log2 N | S09 p. 297 | N highly composite |
| L26 | Cost per factor r grows as r/log2 r — 2.00 for 2, 1.88 for 3, 2.15 for 5; radix 3 gains only about 6% over 2 or 4, and highly composite sizes exist within a few percent of any large N | S09 p. 299 | — |
| L27 | FFTW reports speed by scaling with 5 N log2 N for complex and 2.5 N log2 N for real transforms; this is a convention from radix-2's asymptotic count, not a flop count | S17 | — |
| L28 | Yavne's split-radix needs 4N lg N − 6N + 8 real flops for a complex power-of-two DFT, 20% fewer than radix-2; Johnson & Frigo's variant needs about 6% fewer again | S10 abstract, §I | power-of-two N, complex data |
| L29 | FFTW adapts its algorithm to the hardware to maximise performance | S11 abstract | — |
| L30 | Stockham applied Cooley & Tukey's procedure to high-speed convolution and correlation, with computation time proportional to N log2 N | S12 abstract | abstract only |
| L31 | Spatial filtering of an M×N image with an m×n kernel takes on the order of MNmn operations, MN(m + n) if separable; the frequency domain takes about 2MN log2 MN, for a forward and an inverse FFT | S13 p. 250 | operation counts, not timings |
| L32 | The advantage C_n(m) = m²/(4 log2 M) over non-separable and C_s(m) = m/(2 log2 M) over separable kernels; at M = 2048 the FFT wins from 7×7, the separable crossover is "around 27", and the counts ignore complex arithmetic, so they are guidelines | S13 pp. 251–252 | square M×M image, m×m kernel |
| L33 | Frequency-domain filtering is g = Real{IDFT[H·F]}; a real symmetric H on a real image gives a real result in theory; centring multiplies the image by (−1)^(x+y); software that does not centre needs filters laid out uncentred | S13 p. 307 | — |
| L34 | Filtering without padding and with zero padding give visibly different results at the image's vertical edges | S13 p. 309, Fig. 4.31 | Gaussian low-pass example |
| L35 | Cassini images of Saturn's rings carried a nearly sinusoidal pattern from an AC signal on the camera video before digitising; it shows as bursts along the spectrum's vertical axis and is removed by a narrow notch rectangle along that axis; 1 − notch reject isolates the pattern | S13 p. 348, Example 4.25 | — |
| L36 | The textbook treats notch filters in §4.10 and periodic-noise reduction, including optimum notch filtering, in §5.4 | S13 TOC | coverage only |
| L37 | Periodic noise arises from electrical interference, miscalibrated sensors, halftone printing and scanlines; it gives sharp spikes in the spectrum that notch filters remove; the method dates to robotic-probe imaging (Rindfleisch et al. 1971, Mariner 6 and 7) | S08 §1 | — |
| L38 | Automating notch design is hard because every coefficient depends on the whole image, and telling noise spikes from texture or man-made repetition needs prior knowledge | S08 §1 | — |
| L39 | Sur & Grédiac detect noise spikes as outliers against the power-law spectrum expected of a natural image, averaged over patches, and their notch can remove a whole set of frequency pairs | S08 §2–3 | natural images only, by their own statement |
| L40 | filter2D's documentation says it uses a DFT-based algorithm for kernels of about 11×11 or larger and the direct sum below that; it computes correlation, not mirroring the kernel | S19 (imgproc.hpp, filter2D) | documentation |
| L41 | In source, filter2D takes the DFT path only when kernel area ≥ 130 (SSE3 present and 8U→8U/16S or 32F→32F) or ≥ 50 otherwise, never for an ROI, and only after any vendor replacement declines | S18 lines 1226–1253, 1410–1458 | OpenCV 4.x at 802cf95 |
| L42 | The DFT path passes the caller's border type to crossCorr, and sepFilter2D has no DFT path at all | S18 lines 1277–1287, 1462–1487 | — |
| L43 | SciPy's choose_conv_method predicts the faster method from precomputed constants, or times both with measure=True; its notes report 99% accuracy for 2-D on random sizes, tuning on a mid-2014 MacBook Pro and testing on an EC2 r5a.2xlarge, and say the 2-D implementation is the same as for 3-D and 4-D while 1-D differs | S24 (choose_conv_method docstring) | SciPy's own experiments |
| L44 | SciPy's model counts fft_ops = 3·N·ln N for three FFTs of the full output size and direct_ops = kernel size × output size, and picks the FFT when O_fft·fft_ops < O_direct·direct_ops + offset; for 2-D 'same' the constants are 2.04735e-9, 1.55367e-8 and −1e-4 | S24 (_conv_ops, _fftconv_faster) | SciPy at 95e01a4 |
| L45 | SciPy falls back to the direct method for integer inputs whose products could exceed float precision, and for booleans | S24 (choose_conv_method body) | — |
| L46 | scipy.fft.next_fast_len returns the smallest size ≥ the target that the FFT handles fast, composed of the small prime factors it implements | S26 | result may change between versions |
| L47 | scikit-image's phase_cross_correlation defaults to phase normalisation, credits phase correlation to Kuglin & Hines 1975, and notes it copes with illumination changes but is not very robust to noise | S25 (docstring) | — |
| L48 | cv2.phaseCorrelate optionally applies a Hanning window against edge effects, forms R = G_a G_b* / abs(G_a G_b*), inverts it, and refines the peak with a 5×5 weighted centroid | S19 (imgproc.hpp, phaseCorrelate) | — |
| L49 | For downsampled images the phase-correlation power spreads over several coherent adjacent peaks, which give a closed-form sub-pixel estimate | S15 abstract | abstract only |
| L50 | Periodic sinc interpolation is zero-padding in the Fourier domain, done with the FFT; it often rings strongly at the frame borders, so symmetrisation is usually added at extra cost, and the periodic-plus-smooth split avoids the ringing | S07 §4.2, Fig. 6 | — |
| L51 | scipy.signal.fftconvolve convolves through the FFT, generally much faster than convolve for large arrays but slower when few outputs are needed, and returns floats; oaconvolve uses overlap-add and is much faster than fftconvolve when one array is much larger than the other | S24 (fftconvolve, oaconvolve docstrings) | SciPy's own guidance |
| L52 | A real-input FFT keeps n/2 + 1 entries along the transformed axis for even n and (n + 1)/2 for odd n | S23 (rfft docstring) | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S07 | Figure 1 | the boundary cross / L13 | shows the periodised image and the cross in modulus and phase | Springer copyright; the preprint carries no licence; built on the Lena image | https://helios2.mi.parisdescartes.fr/~moisan/papers/2009-11r.pdf | do not reuse — rights not verified; our tiled-patch figure carries the point |
| F2 | S05 | the RPN result figures | magnitude carries texture / L07 | a micro-texture and its phase-randomised copy | CC BY-NC-SA (IPOL) — non-commercial and share-alike terms not verified for this site | https://www.ipol.im/pub/art/2011/ggm_rpn/article.pdf | do not reuse — the licence's NC/SA terms are not cleared for canery.in |
| F3 | S16 | Figure 1 | the classic swap / L11 | the photograph swap | no licence stated; the photographs are third-party | https://ece.technion.ac.il/wp-content/uploads/2021/01/publication_773-1.pdf | do not reuse — rights unclear |
| F4 | S13 | Figure 4.2, Figure 4.65 | cost model / L32; notch / L35 | the C(m) curves; the Cassini notch | Pearson copyright | the sample-chapter PDF | do not reuse — copyright; the post computes its own model |

## Open questions

- **Oppenheim & Lim's full text** was not reachable. The post attributes to S01 only what its
  abstract says, and describes the swap through S16. If the paper becomes reachable, check whether
  its own swap used photographs with similar magnitude spectra; the post argues that is why the
  swap looks like the phase donor, as its own reasoning from L09/L10, not as S01's claim.
- **Kuglin & Hines 1975** was not located; the attribution rests on scikit-image's docstring (L47).
- **Duhamel & Vetterli's survey** was found but not read (row 29); the FFT op counts rest on S09,
  S10 and S17 instead.
- **Part 1's filter2D sentence** ("switches strategies at large kernel sizes", L12 there, from the
  documentation's "~11 × 11") is accurate to the docs; the source's rule is area ≥ 130 or ≥ 50
  (L41), so an 11×11 kernel (area 121) stays direct on OpenCV's SIMD paths. This post states the
  source rule; Part 1 needs no correction because it quoted the documentation.
