# Source ledger — resampling-and-aliasing

Series `image-processing`, part 3. Sweep run 2026-09-25. Tier L3, so the floor is 7
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

Every paper below was downloaded and read in full (PDF → `pdftotext`, or page images where the
text layer was missing or had lost its symbols), so each claim row was checked against the
paper's own equation, section or figure, not an abstract. Library behaviour was checked twice:
against the documentation and against the source code at a pinned commit. Nothing was executed
against an image; the only code run was plain-Python arithmetic reproducing the post's own
hand-worked numbers.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Keys, "Cubic Convolution Interpolation for Digital Image Processing" | IEEE Trans. ASSP 29(6), pp. 1153–1160 | 1981 | 10.1109/TASSP.1981.1163711 | peer-reviewed | http://www.ncorr.com/download/publications/keysbicubic.pdf | 2026-09-25 |
| S02 | T1 | Mitchell & Netravali, "Reconstruction Filters in Computer Graphics" | ACM SIGGRAPH Computer Graphics 22(4), pp. 221–228 | 1988 | 10.1145/378456.378514 | peer-reviewed | https://www.cs.utexas.edu/~fussell/courses/cs384g-fall2013/lectures/mitchell/Mitchell.pdf | 2026-09-25 |
| S03 | T1 | Heckbert, "Fundamentals of Texture Mapping and Image Warping" | MS thesis, UC Berkeley | 1989 | UCB/CSD-89-516 | preprint | http://www.cs.cmu.edu/~ph/texfund/texfund.pdf | 2026-09-25 |
| S04 | T1 | Thévenaz, Blu & Unser, "Interpolation Revisited" | IEEE Trans. Medical Imaging 19(7), pp. 739–758 | 2000 | 10.1109/42.875199 | peer-reviewed | https://bigwww.epfl.ch/publications/thevenaz0002.pdf | 2026-09-25 |
| S05 | T1 | Unser, "Sampling—50 Years After Shannon" | Proceedings of the IEEE 88(4), pp. 569–587 | 2000 | 10.1109/5.843002 | peer-reviewed | https://bigwww.epfl.ch/publications/unser0001.pdf | 2026-09-25 |
| S06 | T1 | Meijering, "A Chronology of Interpolation: From Ancient Astronomy to Modern Signal and Image Processing" | Proceedings of the IEEE 90(3), pp. 319–342 | 2002 | 10.1109/5.993400 | peer-reviewed | https://bigwww.epfl.ch/publications/meijering0201.pdf | 2026-09-25 |
| S07 | T1 | Parmar, Zhang & Zhu, "On Aliased Resizing and Surprising Subtleties in GAN Evaluation" | CVPR, pp. 11400–11410 | 2022 | 10.1109/CVPR52688.2022.01112; arXiv:2104.11222v3 | peer-reviewed | https://arxiv.org/abs/2104.11222 | 2026-09-25 |
| S08 | T1 | Shannon, "Communication in the Presence of Noise" (read in the Proc. IEEE 86(2) 1998 classic-paper reprint) | Proceedings of the IRE 37(1), pp. 10–21 | 1949 | 10.1109/JRPROC.1949.232969 | peer-reviewed | https://www.math.unl.edu/~bdeng1/Teaching/math943/Topics/Genetics/Shannon1949.pdf | 2026-09-25 |
| S09 | T2 | OpenCV 4.x documentation, Geometric Image Transformations — `resize`, `InterpolationFlags` | — | 2026 | imgproc.hpp @ 329e9c279c8b | official-docs | https://docs.opencv.org/4.x/da/d54/group__imgproc__transform.html | 2026-09-25 |
| S10 | T3 | OpenCV source, `modules/imgproc/src/resize.cpp` | — | 2026 | commit cc293eaff62c | source | https://github.com/opencv/opencv/blob/cc293eaff62cd4f072ca808962a0e279221c13f3/modules/imgproc/src/resize.cpp | 2026-09-25 |
| S11 | T2 | OpenCV 4.x documentation, Image Filtering — `pyrDown` | — | 2026 | imgproc.hpp @ 329e9c279c8b | official-docs | https://docs.opencv.org/4.x/d4/d86/group__imgproc__filter.html | 2026-09-25 |
| S12 | T2 | Pillow documentation — `Image.resize` and Concepts › Filters | — | 2026 | — | official-docs | https://pillow.readthedocs.io/en/stable/reference/Image.html | 2026-09-25 |
| S13 | T3 | Pillow source, `src/libImaging/Resample.c` | — | 2026 | commit c65fe0814878 | source | https://github.com/python-pillow/Pillow/blob/c65fe0814878fddcda13cacc57a297acb5019375/src/libImaging/Resample.c | 2026-09-25 |
| S14 | T2 | scikit-image documentation — `skimage.transform.resize` | — | 2026 | — | official-docs | https://scikit-image.org/docs/stable/api/skimage.transform.html | 2026-09-25 |
| S15 | T2 | SciPy documentation — `scipy.ndimage.zoom` | — | 2026 | — | official-docs | https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.zoom.html | 2026-09-25 |

Notes on individual sources:

- **S03** is a master's thesis, examined by committee but not journal-reviewed. It is marked
  `preprint` because none of the six statuses fits a thesis better, and the post names it as
  "Heckbert's 1989 thesis" so the reader sees what it is. The PDF is a 300-dpi scan with no
  text layer; §3.4 (Figure 3.12, eq. 3.1) and §3.5.6 were read as page images.
- **S06**'s text layer drops its Greek symbols, so every α value used here was read off the
  rendered page (pp. 328–329), not the extracted text.
- **S08** was read in the 1998 Proc. IEEE classic-paper reprint (86(2):447–457); equation
  numbers (6)–(7) are the reprint's and match the original's.
- **S09 / S11**: `docs.opencv.org` served a Cloudflare challenge to both curl and WebFetch on
  the access date. Both pages are generated by Doxygen from the comments in
  `modules/imgproc/include/opencv2/imgproc.hpp`; the quoted behaviour was verified in that
  header at commit 329e9c279c8b (2026-09-14). Part 1 read the rendered S09 page on 2026-09-10
  (its S28) and recorded the same `resize` recommendation.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | `image interpolation survey` | Page one is recent, lightly cited reviews centred on edge-directed and super-resolution methods; none maps the classical kernels. Moved to title-restricted search |
| 2 | 1 | OpenAlex | `title.search:image interpolation survey`, sorted by citations | Lehmann, Gönner & Spitzer 1999 (IEEE TMI, 1,347 citations) is the most-cited survey of classical kernels |
| 3 | 1 | OpenAlex | `title.search:interpolation revisited` | Thévenaz, Blu & Unser 2000 (IEEE TMI, 840) — the approximation-order framing; became S04 |
| 4 | 1 | OpenAlex | `title.search:chronology interpolation` | Meijering 2002 (Proc. IEEE, 661) — the history of the cubic parameter; became S06 |
| 5 | 1 | OpenAlex | `title.search:image resampling`, sorted by citations | Parker, Kenyon & Troxel 1983 (IEEE TMI, 839) and Dodgson 1997 (quadratic kernels); Parker is recounted in S06, not read directly |
| 6 | 1 | OpenAlex | `title.search:reconstruction filters computer graphics` | Mitchell & Netravali 1988 under two DOIs; 10.1145/378456.378514 is the journal-of-record one (S02) |
| 7 | 1 | OpenAlex | forward chase: works citing Keys 1981 (W2157494358), sorted by citations | 3,775 citing works; top classical hits Lehmann 1999 and Unser 2000 "Sampling—50 years after Shannon" (became S05) |
| 8 | 4 | OpenAlex | forward chase: works citing Keys 1981 with `alias` in the title | Parmar, Zhang & Zhu, CVPR 2022 — library resizers alias on downscale; became S07 |
| 9 | 1 | OpenAlex | forward chase: works citing Mitchell & Netravali (W1987278426), sorted by citations | Lehmann 1999, Meijering 2002, Meijering et al. 2001 (MedIA kernel evaluation — host unreachable, not read) |
| 10 | 1 | Crossref | DOI lookups for 13 candidate sources | Venue, volume, pages and year confirmed for 12; my recalled DOI for Park & Schowengerdt 404'd |
| 11 | 1 | Crossref | `query.bibliographic=Image reconstruction by parametric cubic convolution Park Schowengerdt` | CVGIP 23(3):258–272, 1983, DOI 10.1016/0734-189X(83)90026-9; paywalled, used only as recounted in S06 |
| 12 | 1 | arXiv | `ti:"Aliased Resizing" OR ti:"Buggy Resizing"` | 2104.11222v3 is the preprint of S07; the CVPR version is the one of record |
| 13 | 1 | arXiv | `abs:"image resizing" AND abs:aliasing` | Only S07 again |
| 14 | 1 | Semantic Scholar | `cubic convolution interpolation kernel` (graph API) | HTTP 429 for the whole session; no results, nothing relied on |
| 15 | 1 | Keys 1981 reference list | backward chase from S01 | Rifman 1973 and Bernstein 1976 as the origin of the a = −1 kernel; Hou & Andrews 1978 for splines |
| 16 | 1 | Mitchell & Netravali reference list | backward chase from S02 | Park & Schowengerdt 1983, Schreiber & Troxel 1985, Brown 1969 (single-lobe ringing) |
| 17 | 2 | OpenCV GitHub | `resize.cpp`, `imgproc.hpp` on branch 4.x | `A = -0.75`, nearest-neighbour index `floor(dx/fx)`, half-pixel mapping, area table, 8-tap normalised Lanczos (S09, S10) |
| 18 | 5 | Pillow GitHub | `src/libImaging/Resample.c` on main | a = −0.5, Lanczos support 3, support stretched by in/out on shrink (S13) |
| 19 | 5 | Library docs | Pillow `Image.resize`, scikit-image `resize`, SciPy `ndimage.zoom` | Default filters, the anti-aliasing default and σ rule, the two meanings of "prefilter" (S12, S14, S15) |
| 20 | 4 | Google Scholar | `cubic convolution parameter -0.75 -0.5 comparison` | Maeland 1988 (spline beats cubic convolution), Reichenbach & Geng 2003, Meijering et al. 1999 — the disagreement over a, all recounted in S06 |
| 21 | 4 | Google Scholar | `downsampling aliasing resize antialias library inconsistency` | S07 again plus unrelated deep-learning anti-aliasing work — stop condition reached |
| 22 | 1 | AMS journals | Duchon 1979, "Lanczos Filtering in One and Two Dimensions" (DOI confirmed via Crossref) | HTTP 403 to curl and WebFetch; not read, so not cited. The Lanczos kernel is defined from S13 and S09 instead |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Keys' kernel is a symmetric piecewise cubic on (−2, 2) with one free parameter a; it is 1 at 0 and 0 at every other integer, so it passes through the samples and uses four of them | S01 eq. (4) | one-dimensional; applied separably in 2-D |
| L02 | a = −1/2 is the only value giving third-order accuracy (error falls as h³); every other a gives at most first order | S01 pp. 1154–1155; S06 p. 328 | the sampled function needs a continuous third derivative |
| L03 | Linear interpolation converges as h², nearest-neighbour as h | S01 p. 1156 | smooth sampled function |
| L04 | Keys' cubic reproduces any quadratic exactly; linear reproduces at most a straight line; nearest-neighbour only a constant | S01 p. 1156 | a = −1/2 |
| L05 | Rifman and Bernstein's original cubic convolution used a = −1, the value that makes the kernel's slope match the sinc's at x = 1 | S01 p. 1154; S06 p. 328 | — |
| L06 | a = −3/4 is the value that makes the kernel's second derivative continuous at x = 1, one of Simon's 1975 criteria | S06 p. 328 | the source says nothing about which libraries adopted it or why |
| L07 | Park and Schowengerdt reached a = −1/2 independently from the frequency domain, as the best low-frequency match to the sinc; Catmull and Rom's 1974 spline is the same kernel | S06 pp. 328–329 | as recounted by Meijering; the originals were not read |
| L08 | Keys handled the borders with an extrapolated sample, c₋₁ = 3f(x₀) − 3f(x₁) + f(x₂), to keep third order at the edges | S01 eq. (19) | — |
| L09 | Keys framed interpolation in frequency as the data's spectrum times the kernel's transform: deviation inside the band blurs, deviation outside it lets replicas through | S01 pp. 1156–1157 | the ideal response is 1 in band and 0 outside |
| L10 | Mitchell and Netravali name two aliasing sources: prealiasing from undersampling or a missing prefilter, and postaliasing from poor reconstruction, which happens even when the replicas do not overlap | S02 §2 | — |
| L11 | A reconstruction filter has two jobs — remove the spectral replicas and pass the baseband unchanged — and failing the second is blur | S02 §3 | — |
| L12 | The ideal sinc filter rings; ringing comes from negative lobes, and values pushed below zero near an edge get clamped | S02 §3, Fig. 6, Fig. 10 | observed on 8-bit display |
| L13 | Requiring the kernel's shifted copies to sum to 1 everywhere removes sample-frequency ripple; the ripple is an alias of the image's DC, and the condition puts zeros in the frequency response at every nonzero multiple of the sampling rate | S02 eq. (7) | — |
| L14 | Mitchell and Netravali's two-parameter cubic family k(x; B, C): (1, 0) is the cubic B-spline, (0, C) the cardinal cubics, (0, 1/2) Catmull–Rom | S02 eq. (8) | Keys' a corresponds to B = 0, C = −a (checked algebraically here) |
| L15 | From a subjective test with nine expert observers and over 500 judgements, Mitchell and Netravali recommend (B, C) = (1/3, 1/3) as the compromise between ringing, blur and anisotropy | S02 §4 | subjective; the authors say other observers may prefer more or less ringing |
| L16 | One ringing lobe can read as sharpness; multiple transients always degrade the image (Brown 1969, as cited) | S02 §3 | subjective television study |
| L17 | A separable N-tap filter costs O(N) multiplications per output instead of O(N²) | S02 §3 | — |
| L18 | Resampling is reconstruct, warp, prefilter, sample; the stages fold into one resampling filter giving the weight of every input sample in every output sample | S03 §3.4, Fig. 3.12, eq. (3.1) | — |
| L19 | When magnifying, the resampling filter is dominated by the reconstruction filter, whose 1–4 pixel support does not depend on the mapping | S03 §3.5.6 | prefilter approximated by an impulse |
| L20 | When shrinking, it is dominated by the prefilter, whose support in the source grows as the reciprocal of the scale factor and is unbounded | S03 §3.5.6 | reconstruction filter approximated by an impulse |
| L21 | Approximation order L: the error falls as h^L, and a kernel of order L reproduces polynomials of degree L − 1; order 1 is the partition of unity | S04 §II-B | Strang–Fix conditions |
| L22 | Keys reaches order 3 at a = −1/2 while the cubic B-spline reaches 4 at the same support, at the cost of a coefficient prefilter that recursive filtering makes cheap; the authors judge Keys' speed gain not worth the quality loss | S04 §IV-F | — |
| L23 | The sinc is rarely used to reconstruct images because it decays slowly, and no ideal low-pass filter exists as a device | S05 §I | — |
| L24 | Sampling without a prefilter is by far the worst approximation scheme — energy above Nyquist counts twice, once as missing and once folded back — and a simple box prefilter comes close to optimal | S05 §III-C, Fig. 7 | linear-spline comparison |
| L25 | Signal processing requires the prefilter's width to scale with the downsampling factor; PIL does this, and the default resizes in OpenCV, PyTorch and TensorFlow use a fixed width and alias like naive subsampling | S07 §3, Figs. 1–2 | as tested by the authors for the libraries' default flags |
| L26 | The aliased resizes changed the FID scores the paper was measuring | S07 §§3–4 | FID pipelines; the paper's measurements, not ours |
| L27 | Shannon's reconstruction places a sin(2πWt)/(2πWt) pulse at every sample; it is 1 at its own sample, 0 at all others, and its spectrum is flat in the band and zero outside | S08 eqs. (6)–(7) | strictly band-limited signal |
| L28 | `cv2.resize` defaults to `INTER_LINEAR`; the docs recommend `INTER_AREA` to shrink and `INTER_CUBIC` or `INTER_LINEAR` to enlarge | S09 | documented guidance, not a measurement |
| L29 | `INTER_AREA` resamples by pixel-area relation, documented as moiré-free for decimation and similar to nearest-neighbour when zooming | S09 | — |
| L30 | `INTER_LANCZOS4` is Lanczos over an 8×8 neighbourhood; the source computes eight weights and divides them by their sum | S09; S10 `interpolateLanczos4` | — |
| L31 | `INTER_NEAREST` picks source index floor(dx/fx) with no half-pixel offset; `INTER_NEAREST_EXACT` uses pixel centres and is documented to match PIL, scikit-image and MATLAB | S10 `resizeNN`, `resizeNN_bitexact`; S09 | — |
| L32 | `INTER_CUBIC` hard-codes the Keys parameter at A = −0.75 | S10 `interpolateCubic` | commit cc293eaff62c |
| L33 | Linear, cubic and Lanczos resizes place output dx at source coordinate (dx + 0.5)·scale − 0.5 | S10 | half-pixel-centre convention |
| L34 | Cubic taps that fall outside the row are clamped to the nearest edge pixel | S10 `HResizeCubic` | replicate, not Keys' extrapolation |
| L35 | True area averaging runs only when shrinking — each source pixel weighted by its overlap with the destination pixel's footprint — and is emulated by a bilinear variant otherwise | S10 `computeResizeAreaTab` and dispatch | — |
| L36 | At exactly 2× shrink, `INTER_LINEAR` is switched to the area path | S10 dispatch | integer factor 2 on both axes |
| L37 | `pyrDown` convolves with the 5×5 kernel outer([1 4 6 4 1])/256 and then rejects the even rows and columns | S11 | — |
| L38 | Pillow's `Image.resize` defaults to BICUBIC; `reducing_gap` first reduces by an integer factor, then resamples, and at 3.0 or above is documented as indistinguishable from fair resampling in most cases | S12 | default `reducing_gap` is None |
| L39 | Pillow's BICUBIC uses a = −0.5, its LANCZOS is sinc(x)·sinc(x/3) on [−3, 3), its BILINEAR is the triangle | S13 | commit c65fe0814878 |
| L40 | When shrinking, Pillow multiplies the filter's support by the input/output ratio and evaluates the kernel at distance/ratio; taps outside the image are dropped and the rest renormalised to sum to 1 | S13 `precompute_coeffs` | — |
| L41 | `skimage.transform.resize` applies a Gaussian before downsampling by default, with σ = (s − 1)/2 for downscale factor s, and no filter when enlarging; default order is 1 | S14 | non-bool input |
| L42 | `scipy.ndimage.zoom` defaults to order 3; its `prefilter` computes B-spline coefficients and is not an anti-aliasing filter; with `grid_mode=False` a 5-sample signal is treated as length 4 | S15 | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S02 | Figure 13 (the B–C plane with subjective regions) | Why "bicubic" is a family / L14–L15 | would show the regions the recommendation came from | ACM copyright 1988; no licence found | https://doi.org/10.1145/378456.378514 | do not reuse; our own B–C figure plots computed overshoot and blur instead, not the subjective regions |
| F2 | S01 | Fig. 2 (amplitude spectra of three kernels) | Transfer functions / L09 | the original spectral comparison | IEEE copyright 1981; no licence found | https://doi.org/10.1109/TASSP.1981.1163711 | do not reuse; our figure adds Lanczos-3, OpenCV's a and the 0.6× Nyquist |
| F3 | S03 | Figure 3.12 (resampling filter block diagram) | Intuition / L18 | the pipeline in one picture | thesis, no licence stated | http://www.cs.cmu.edu/~ph/texfund/texfund.pdf | do not reuse; our pipeline figure carries the worked example's bandwidths instead |
| F4 | S07 | Figure 1 (downsampling a circle in six libraries) | Limitations / L25 | shows library aliasing on a real image | arXiv default non-exclusive licence; no reuse licence verified | https://arxiv.org/abs/2104.11222 | do not reuse; described in prose |

## Open questions

- **Rounding of the output size.** OpenCV's docs give `dsize = round(fx·src.cols)`, but the
  code computes it with `saturate_cast<int>`. For 5 × 1.7 = 8.5 the two conventions can
  disagree (9 vs 8). Not settled from the sources; the post states its eight-sample grid
  explicitly and makes no claim about what `cv2.resize(..., fx=1.7)` returns for this width.
- **Why OpenCV chose −0.75.** The source hard-codes it without comment. S06 records that −3/4
  is Simon's continuous-second-derivative value; the post says only that, never that OpenCV
  chose it for that reason.
- **Lehmann 1999 and Meijering et al. 2001** are the two quantitative evaluations the sweep
  pointed to. Neither was retrievable (paywall; host unreachable). The post makes no ranking
  claim that would need them; S04 and S06 carry the spline-versus-convolution conclusion.
- **Nothing was executed.** No claim rests on a measurement of ours. Every number in the post is
  hand-worked on the shared patch, evaluated from a kernel's closed form, or carries a key above.
