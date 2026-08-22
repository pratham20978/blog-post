# Classical Image Preprocessing for Camera-Captured Document OCR — A Rigorous Booklet

## TL;DR
- For your camera-captured identity/trade documents feeding PaddleOCR / Nemotron OCR / Qwen-VL, the highest-value classical operators are: (1) geometry correction (perspective + deskew), (2) illumination flattening via black-hat / large-SE background division, and (3) upscaling small glyphs to ~300 DPI-equivalent with Lanczos or a learned SR model — but you should generally **NOT** hard-binarize before modern deep/VLM engines.
- The canonical MRZ / ID-field detection pipeline you are already using (black-hat → Scharr-x → wide morphological close → Otsu → connected-component filtering) is sound and well-attested; Scharr-x is the correct 3×3 derivative because it minimizes Fourier-domain angular error (α=3/10 vs Sobel's α=1/2).
- "Always binarize", "INTER_LANCZOS4 is always best", and "iterations=2 equals a bigger kernel" are all wrong in general; this booklet flags each with the math and evidence.

## Key Findings
1. **Binarization often HURTS modern OCR.** Tesseract 4/5's LSTM recognizer uses the grayscale image, not the binarized one, and empirical multi-parameter studies show CRNN models score dramatically worse on binarized input than grayscale. For PaddleOCR/Nemotron/Qwen-VL, keep grayscale/RGB into the recognizer; binarize only for the classical detection/segmentation stages (MRZ band, line removal).
2. **Black-hat is your single most valuable illumination operator** for dark text on a bright page: BTH = (f•b) − f estimates local background via a closing with an SE larger than stroke width, then subtracts, yielding a flat-field image of the dark strokes.
3. **Divide, don't subtract, for multiplicative (shadow/vignette) illumination**; subtract for additive. This follows directly from the illumination–reflectance model I = L·R.
4. **Lanczos upscaling helps OCR on small glyphs but only up to a point**; classical interpolation is beaten by text-specific super-resolution (TSRN/TATT on TextZoom) when glyphs are truly sub-resolution. INTER_LANCZOS4 does NOT stretch its kernel on downscale, so use INTER_AREA for shrinking.
5. **Scharr > Sobel at 3×3**; the 3/10/3 kernel is the fixed-point optimum of a weighted-mean-squared angular-error functional in the Fourier domain (Scharr 2000 dissertation).
6. **Otsu fails on sparse text / uneven illumination** (its bimodality and equal-variance assumptions break); apply it on the black-hat output, or switch to Sauvola for degraded documents.

## Details

---

# NOTATION TABLE

| Symbol | Meaning |
|---|---|
| f, f(x,y) | input image (grayscale intensity) |
| b, B | structuring element (SE) / probe set |
| ⊕, ⊖ | dilation, erosion |
| ∘, • | opening, closing |
| ⊗ | outer product / convolution (context-dependent) |
| L(x,y), R(x,y) | illumination, reflectance components |
| sinc(x) | normalized sinc = sin(πx)/(πx) |
| a | Lanczos lobe parameter (support radius) |
| Gx, Gy | horizontal/vertical image gradients |
| σ²_B, σ²_W, σ²_T | between-class, within-class, total variance (Otsu) |
| ω₀,ω₁,μ₀,μ₁ | class probabilities and means (Otsu) |
| t, T | threshold value |
| k̃ | normalized wavenumber (∈[−1,1] per axis) |
| CER/WER | character/word error rate |

---

# CHAPTER 1 — LANCZOS RESAMPLING / MAGNIFICATION

## 1.1 Intuition
Resampling asks: given samples of a signal on one grid, estimate its values on another grid. The theoretically ideal answer comes from the sampling theorem: reconstruct the continuous band-limited signal exactly, then re-sample it.

## 1.2 From Nyquist–Shannon to the sinc reconstruction filter
A signal band-limited to |ω| < π (samples at unit spacing) is reconstructed exactly by

  f(x) = Σ_n f[n] · sinc(x − n),  sinc(x) = sin(πx)/(πx).

This is convolution with the ideal brick-wall low-pass filter whose frequency response is the rectangle Π(ω/2π). The sinc kernel is unrealizable because (a) it has infinite support and (b) it decays only as 1/x, so truncation causes large ringing (Gibbs phenomenon).

## 1.3 The Lanczos kernel
Windowing multiplies sinc by a smooth finite window — itself a stretched sinc lobe:

  L(x) = sinc(x)·sinc(x/a) for |x| < a, else 0.

- a = tap radius (lobes); support is 2a. Common a = 2 (4 taps/axis), a = 3 (6 taps), a = 4 (8 taps). OpenCV's INTER_LANCZOS4 uses a = 4 → 8×8 neighborhood.
- Normalized sinc = sin(πx)/(πx) (zeros at integers); unnormalized sinc = sin(x)/x. Image processing uses the normalized form.
- Larger a → sharper (closer to ideal brick-wall) but more ringing and cost.

The kernel is a "sinc window" because the window function is itself the central lobe of a sinc, stretched by a. History: named after Cornelius Lanczos, whose sigma-factor smoothing of Fourier series (Discourse on Fourier Series, 1966) mitigates Gibbs; adapted to filtering by Claude E. Duchon, "Lanczos Filtering in One and Two Dimensions," Journal of Applied Meteorology 18 (1979): 1016–1022, DOI 10.1175/1520-0450(1979)018<1016:LFIOAT>2.0.CO;2. Duchon's principal contribution was the use of "sigma factors" to reduce the amplitude of Gibbs oscillation.

## 1.4 Comparison to other windowed sincs and cubics
- Other windowed sincs: Hamming, Blackman, Kaiser (parametric β trade-off), Bartlett (triangular). Lanczos is generally regarded as a good sharpness/ringing compromise.
- Cubic families (Mitchell–Netravali BC-splines): Catmull–Rom (B=0, C=0.5) is interpolating and sharp; B-spline (B=1, C=0) is smooth/blurry; Mitchell (B=C=1/3) balances. OpenCV's INTER_CUBIC is a Catmull–Rom-like bicubic with a = −0.75 convolution kernel over a 4×4 neighborhood.

## 1.5 Separability
2D Lanczos = outer product of 1D kernels: L₂(x,y) = L(x)·L(y). Separable filtering costs O(2a) per axis = O(4a) per output pixel instead of O((2a)²). For a=4: 16 vs 64 multiply-adds.

## 1.6 Resampling equations
For output position u mapping to source coordinate s = u/scale (upscale) with fractional phase φ = s − ⌊s⌋:

  f_out(u) = Σ_{k=−a+1}^{a} f[⌊s⌋+k] · L(k − φ)  /  Σ_k L(k − φ).

- The denominator is weight normalization: because Σ_k L(k−φ) ≠ 1 in general (the partition of unity fails, most severely at a=1), skipping normalization produces intensity ripple/DC error (a flat input would not reproduce as flat).
- **Downscaling anti-aliasing:** to avoid aliasing when scale < 1, the kernel must be *stretched* by 1/scale (i.e. L(scale·(k−φ))·scale), which lowers the cutoff to the output Nyquist. **OpenCV's INTER_LANCZOS4 does NOT do this stretch** — it always uses the fixed 8-tap kernel — so downsampling with it aliases. This is exactly why INTER_AREA (area-averaging, equivalent to a box prefilter) is preferred for shrinking; per the OpenCV docs it "may be a preferred method for image decimation, as it gives moire'-free results," but "when the image is zoomed, it is similar to the INTER_NEAREST method."

## 1.7 Frequency-domain analysis
The DTFT of the Lanczos kernel approximates a rectangle with: a fairly flat passband, finite stopband attenuation, and a transition band that narrows as a grows. Because of the negative lobes, the response overshoots near cutoff → ringing/halos around high-contrast text edges (Gibbs). Compared with:
- Nearest: sinc-shaped response, severe aliasing.
- Bilinear: sinc², over-smooth, poor stopband.
- Bicubic (a=−0.5 / −0.75): sharper than bilinear; −0.75 has mild overshoot.
- INTER_AREA: excellent antialiasing on downscale (box in frequency = sinc envelope on the input).

Artifacts to expect: ringing/overshoot (negative lobes → under/overshoot and clipping at 0/255), halos around black text on white, and aliasing/moiré when downsampling with a non-stretched kernel.

## 1.8 Quantitative comparison methodology
- Fidelity: PSNR, SSIM, MS-SSIM.
- Sharpness: MTF50 and edge-spread function from a slanted-edge (ISO 12233) target.
- **Most important for you: downstream CER** after upscaling small text.

Evidence on OCR: Super-resolution can raise OCR accuracy close to native high-res; Dong et al. (ICDAR2015 TextSR winner, arXiv:1506.02211) reached 77.19% OCR accuracy from LR input vs 78.80% from HR. On the TextZoom benchmark, Wang et al., "Scene Text Image Super-Resolution in the Wild," ECCV 2020 (arXiv:2005.03341) report that "our TSRN largely improves the recognition accuracy by over 13% of CRNN, and by nearly 9.0% of ASTER and MORAN compared to synthetic SR [bicubic] data." The gap grows for the strongest text-SR models: TATT (Ma et al., CVPR 2022), per the RGDiffSR paper (arXiv:2311.13317) Table 1, reaches 63.6% (ASTER), 59.5% (MORAN), 52.6% (CRNN) average recognition accuracy vs bicubic's 47.2%/44.1%/26.8% — CRNN accuracy nearly doubles over bicubic upsampling. So classical Lanczos/bicubic upscaling gives a modest gain on borderline text, but learned text-SR (TSRN, TATT, TextSR diffusion) wins clearly when glyphs are sub-resolution.

## 1.9 OpenCV specifics
- cv2.resize flags: INTER_NEAREST(0), INTER_LINEAR(1), INTER_CUBIC(2), INTER_AREA(3), INTER_LANCZOS4(4), INTER_LINEAR_EXACT(5), INTER_NEAREST_EXACT(6).
- INTER_LANCZOS4 = 8×8 neighborhood (a=4). Weights are precomputed into fixed-point tables; sub-pixel phase is quantized to INTER_BITS (5 bits → 32 phases; coordinate math uses INTER_BITS2). Border handling via BORDER_REFLECT_101 by default in filtering; resize clamps to edge.
- warpAffine/warpPerspective/remap accept INTER_LANCZOS4 as a flag; remap converts float maps to fixed-point (CV_32FC2 → CV_16SC2 + CV_16UC1 table indices) via convertMaps for a "more compact and much faster fixed-point representation."
- Note: geometric transforms do not work with CV_8S or CV_32S images.

## 1.10 Practical guidance for OCR
- Upscaling helps when x-height/glyph height is small (sub-~10px) or DPI < ~200. Rule of thumb: target ~300 DPI equivalent. Per ABBYY FineReader support ("What are the recommended scanning parameters"): "300 dpi for regular texts (printed in fonts of size 10 pt or larger)" and "400-600 dpi for texts printed in smaller fonts (9 pt or smaller)"; the FineReader Engine issues the warning "increase resolution to improve recognition of small text," noting "All ABBYY technologies are tuned for that [300 dpi] resolution." Above ~600 DPI only inflates size with no accuracy gain.
- Pattern: **upscale 2×–4× (Lanczos or cubic) then binarize/segment** for classical detection; but feed grayscale to the deep recognizer.
- Where classical loses: use cv2.dnn_superres (EDSR/ESPCN/FSRCNN/LapSRN), Real-ESRGAN, or text-specific SR (TextZoom/TSRN/TATT) for truly tiny text.

## 1.11 Implementation differences
ImageMagick (default Lanczos = 3-lobe with proper down-scale support scaling), ffmpeg (lanczos with param), PIL/Pillow (Image.LANCZOS = a=3, high quality, correctly antialiases on downscale) differ from OpenCV's fixed 8-tap non-stretching INTER_LANCZOS4. So Pillow's LANCZOS downscale ≠ OpenCV's.

## 1.12 Experiment protocol
- Sweep scale 0.25×–8× on cameraman/slanted-edge/zone-plate; compare NEAREST/LINEAR/CUBIC/AREA/LANCZOS4; record PSNR/SSIM (vs high-res ground truth) and edge-profile plots.
- Zone plate: visualize aliasing rings (shows AREA >> LANCZOS4 on downscale).
- CER experiment: take MIDV-500/2020 fields, downsample to simulate low DPI, upscale with each method, run OCR, plot CER vs method and vs scale.

## 1.13 Failure modes
Ringing halos harming thin strokes; clipping from negative lobes; aliasing on downscale with LANCZOS4; over-sharpened JPEG blocks.

---

# CHAPTER 2 — MATHEMATICAL MORPHOLOGY (with black-hat & close for shading)

## 2.1 Foundations
Mathematical morphology (Matheron, Random Sets and Integral Geometry, 1975; Serra, Image Analysis and Mathematical Morphology, 1982) treats images as sets (binary) or functions (grayscale) probed by a structuring element B.

Binary Minkowski operations, with B̌ the reflection and B_x the translate:
- Dilation: A ⊕ B = {z : (B̌)_z ∩ A ≠ ∅} = ∪_{b∈B} A_b.
- Erosion: A ⊖ B = {z : B_z ⊆ A} = ∩_{b∈B} A_{−b}.

## 2.2 Grayscale generalization
Flat SE: dilation = local max, erosion = local min over the SE window:
- (f ⊕ b)(x) = max_{s∈b} f(x−s); (f ⊖ b)(x) = min_{s∈b} f(x+s).
Non-flat SE with additive structuring function b: (max,+) algebra:
- (f ⊕ b)(x) = max_s [f(x−s)+b(s)]; (f ⊖ b)(x) = min_s [f(x+s)−b(s)].
Umbra / threshold decomposition: grayscale morphology equals stacking binary morphology applied to every threshold set (level set) of f — this links the two theories.

## 2.3 Opening and closing
- Opening: f ∘ b = (f ⊖ b) ⊕ b. Removes bright features smaller than b; anti-extensive (f∘b ≤ f).
- Closing: f • b = (f ⊕ b) ⊖ b. Fills dark features smaller than b; extensive (f•b ≥ f).

## 2.4 Algebraic properties (why they matter)
- Duality: (A⊖B)ᶜ = Aᶜ ⊕ B̌ — erosion of foreground = dilation of background.
- Increasingness (monotone) — enables threshold decomposition.
- Extensivity (closing/dilation) / anti-extensivity (opening/erosion).
- Idempotence: (f∘b)∘b = f∘b; (f•b)•b = f•b — an opening/closing is a morphological filter that "settles."
- Translation invariance.
- Non-commutativity: erode-then-dilate ≠ dilate-then-erode (opening ≠ closing).

## 2.5 White top-hat
WTH = f − (f∘b) — extracts bright objects smaller than the SE (e.g. specular highlights, bright text on dark). OpenCV: dst = tophat(src, elem) = src − open(src, elem).

## 2.6 BLACK-HAT (bottom-hat) — the key operator
BTH = (f • b) − f. OpenCV: dst = blackhat(src, element) = close(src, element) − src.
Derivation: closing f•b with an SE larger than the stroke width cannot fit inside the thin dark strokes, so it "paints over" them, producing an estimate of the local bright background L̂. Subtracting the original leaves BTH ≈ L̂ − f = the dark strokes with the (shading-varying) background removed — a flat-field image of the dark text. Because both terms carry the same slow illumination, subtraction cancels it; this is why black-hat is illumination-robust. This is the single most useful operator for dark-text-on-bright-page documents. (In the passport MRZ recipe, "a blackhat operator is used to reveal dark regions (i.e., MRZ text) against light backgrounds.")

## 2.7 Shading / illumination correction recipes and decision table
Illumination–reflectance model: I(x,y) = L(x,y)·R(x,y), L slowly varying.
(i) Background = morphological CLOSE (large SE) → then **divide** f/L̂·255 (multiplicative model, correct for shadows/vignette) vs **subtract** L̂−f (additive model). Division is right when illumination is multiplicative (most camera shadows, glare gradients); subtraction is the black-hat special case and is right when the degradation is additive.
(ii) Background by large-kernel median/Gaussian blur (huge σ), then divide — cheaper than morphology, but text can bleed into the estimate if strokes are dense.
(iii) Rolling-ball background subtraction (Sternberg, "Biomedical Image Processing," IEEE Computer, Jan 1983, DOI 10.1109/MC.1983.1654163) — as in ImageJ; "a ball of given radius is rolled over the bottom side of this surface; the hull of the volume reachable by the ball is the background," equivalent to a grayscale opening with a ball SE. scikit-image restoration.rolling_ball; watch integer underflow on subtraction.
(iv) Homomorphic filtering: log turns I=L·R into ln I = ln L + ln R; DFT; high-pass H(u,v) (often Butterworth/Gaussian high-frequency-emphasis, H = γ_L + γ_H·H_HP with γ_L<1<γ_H) suppresses low-freq L and boosts high-freq R; inverse DFT; exp. "Illumination is usually characterized by slow spatial variations thus being of low frequency... reflectance... being generally of higher frequency." Full model handles smooth shading + contrast simultaneously.
(v) Retinex / MSRCR — multi-scale center/surround log-ratio; strong for color casts and dynamic range but can halo.
(vi) CLAHE — local contrast alternative (Ch. 9).

Decision table (your cases):
- Phone-camera soft shadow: division by large-SE/Gaussian background, or homomorphic.
- Glossy laminate glare on ID: specular is additive bright → white-top-hat suppression / inpainting; homomorphic helps partially; polarization at capture or multi-frame (MIDV video) selection is best.
- Fold/crease shadow: black-hat or division (multiplicative), SE spanning the crease width.
- Uneven scanner illumination: division by large-SE close background (classic flat-field).

## 2.8 Structuring element design
cv2.getStructuringElement(MORPH_RECT|MORPH_ELLIPSE|MORPH_CROSS, (w,h)).
Heuristics:
- Black-hat SE ≈ 2–3× stroke width (must exceed stroke to erase it, but stay smaller than the features you keep).
- Long horizontal SE (e.g. 25×1 to 51×1) to merge glyphs into text-line blobs (your deskew step).
- Vertical SE to detect table row rules; long horizontal SE for column rules — subtract to remove borders.
- Anisotropic SEs isolate horizontal vs vertical strokes for table-line removal.

## 2.9 Other operators
- Morphological gradient: (f⊕b) − (f⊖b); half-gradients: internal = f − (f⊖b), external = (f⊕b) − f.
- Hit-or-miss: (A⊖B₁) ∩ (Aᶜ⊖B₂) — template matching of foreground/background patterns.
- Thinning/skeletonization: Zhang–Suen (Zhang & Suen, "A fast parallel algorithm for thinning digital patterns," CACM 1984), morphological skeleton, cv2.ximgproc.thinning.
- Morphological reconstruction: geodesic dilation δ_g^{(n)} iterated to idempotence under a mask; opening-by-reconstruction preserves the shape of surviving components better than plain opening (which rounds corners).
- Granulometry / pattern spectrum: series of openings with growing SE; the derivative of surviving area vs size gives a size distribution → automatic stroke-width and character-size estimation.
- Alternating sequential filter: alternate openings/closings with growing SE for gentle noise removal.

## 2.10 Connection to your work
Dilation+erosion (a closing) with a wide horizontal SE merges characters into text-line blobs; fit minAreaRect to those blobs to estimate skew angle. Same machinery removes table rules before OCR.

## 2.11 OpenCV API & pitfalls
cv2.morphologyEx op codes: MORPH_ERODE, DILATE, OPEN, CLOSE, GRADIENT, TOPHAT, BLACKHAT, HITMISS.
- **iterations pitfall:** iterations=n with a 3×3 SE equals one pass with a (2n+1)×(2n+1) SE ONLY for flat convex SEs (dilation semigroup: B⊕B⊕…). For non-flat SEs or open/close, iterations re-apply the whole compound operation and this identity fails.
- borderType/borderValue: erosion pads with +∞ (max) conceptually; wrong border can create artifacts at edges. Set BORDER_CONSTANT with appropriate value for erosion vs dilation.
- dtype: black-hat/top-hat outputs can require CV_16S/float if you subtract; on uint8 they saturate.

---

# CHAPTER 3 — SOBEL FILTER

## 3.1 From finite differences
Central difference: f'(x) ≈ [f(x+1) − f(x−1)]/2 → kernel [−1,0,+1]/2. Taylor expansion gives truncation error O(h²). Raw central differences amplify high-frequency noise (the derivative's jω response grows with ω).

History: Irwin Sobel and Gary Feldman presented "An Isotropic 3×3 Image Gradient Operator" at the Stanford Artificial Intelligence Project (SAIL) in 1968; the design goal was a "relatively isotropic 3×3 gradient operator" improving on Roberts' 2×2 cross.

## 3.2 Separability
Sobel-3 = smoothing [1,2,1]ᵀ ⊗ derivative [−1,0,+1]:
Gx = [[−1,0,1],[−2,0,2],[−1,0,1]] = [1,2,1]ᵀ · [−1,0,1].
Gy is the transpose. The smoothing binomial [1,2,1] is Pascal's triangle row; larger kernels (ksize 5,7) use higher binomial rows convolved with the derivative. OpenCV's getDerivKernels returns these row/column kernels.

## 3.3 Magnitude and orientation
|G| = √(Gx²+Gy²) (L2) or |Gx|+|Gy| (L1 approx, cheaper). Orientation θ = atan2(Gy, Gx). OpenCV scale/delta params rescale/offset the (unnormalized) output.

## 3.4 Critical pitfall: ddepth=CV_8U
Gradients are signed. With ddepth=cv2.CV_8U, negative gradients (bright→dark edges) are clamped to 0 and vanish. Correct pattern: compute in CV_16S/CV_32F/CV_64F, then cv2.convertScaleAbs to get |G| in uint8. Demonstration: a white-to-black vertical edge produces a strong response with CV_16S but disappears (one side only) with CV_8U. This is the most common practical Sobel bug.

## 3.5 Frequency response
The ideal derivative has response jω (linear in frequency, phase +90°). Sobel's derivative row [−1,0,1] has response 2i·sin(ω) — accurate only at low ω (sin ω ≈ ω), rolling off and returning to zero at ω=π. The smoothing [1,2,1] = (1+cos ω) attenuates high frequencies (noise suppression). Phase is exactly 90° (pure imaginary, antisymmetric kernel).

## 3.6 Rotational-invariance error
Because Sobel's cross-smoothing (α=1/2) is not optimal, the estimated gradient direction has an angular error that grows for diagonal, high-frequency edges (see Ch. 4 for the quantified Scharr comparison).

## 3.7 Related
Gaussian-derivative (DroG) is the scale-space-correct alternative (derivative of a Gaussian at scale σ). Sobel is Canny's internal gradient stage. Laplacian/LoG/DoG are second-order relatives.

---

# CHAPTER 4 — SCHARR X-GRADIENT

## 4.1 The optimization (Scharr 2000)
Hanno Scharr, Optimale Operatoren in der digitalen Bildverarbeitung, doctoral dissertation, Ruprecht-Karls-Universität Heidelberg, 2000 (DOI 10.11588/heidok.00000962; oral exam 10 May 2000; referees Bernd Jähne and Gabriel Wittum), casts filter design as minimizing a weighted L2 norm in wavenumber space (his Eq. 4.12):

  e²(h) = ∫ w²(k̃) [ f_r(k̃) − f_a(k̃,h) ]² dk̃

over the first Brillouin zone (normalized k̃∈[−1,1]²), with weighting w(k̃) = ∏ᵢ cos⁴(π k̃ᵢ/2) (the spectrum of natural, pre-smoothed images), subject to numerical-consistency constraints (Σ r d_r = 1/2, i.e. correct slope iπ at the origin). For the gradient/orientation filters, f_r − f_a is replaced by the nonlinear **angular-error functional**: the weighted mean-squared deviation between the true gradient angle φ and the discrete-filter-estimated angle arctan(D̂_y/D̂x), integrated over the wavenumber plane. The fixed-point minimizer (via branch-and-bound over integer/power-of-two coefficients) is the derivative [1,0,−1] with cross-smoothing p = [3,10,3]/16.

References: Jähne, Scharr & Körkel, "Principles of Filter Design," in Handbook of Computer Vision and Applications, Vol. 2, Ch. 6, pp. 125–151, Academic Press, 1999; earlier precursor Scharr, Körkel & Jähne, "Numerische Isotropieoptimierung von FIR-Filtern mittels Querglättung," Mustererkennung 1997 (DAGM), 367–374.

## 4.2 The kernel
Scharr-x = (1/32)·[[−3,0,3],[−10,0,10],[−3,0,3]] = [1,0,−1] ⊗ (1/16)[3,10,3].
- Scharr smoothing p = [3,10,3]/16 = [0.1875, 0.625, 0.1875], i.e. α = 3/10.
- Sobel smoothing p = [1,2,1]/4 = [0.25,0.5,0.25], i.e. α = 1/2.
Scharr shifts weight to the center (0.625 vs 0.5). The full-precision L2-optimum is ≈[0.183,0.634,0.183]; the [3,10,3]/16 form is the clean fixed-point optimum. The normalization 1/32 matters: omit it and downstream thresholds (Otsu, fixed) shift by 32×.

## 4.3 Comparison
Angular error curves: Prewitt (α=1/3, no binomial smoothing) worst; Sobel (α=1/2) better; Scharr (α=3/10) best at 3×3; Farid–Simoncelli optimal derivative filters (Farid & Simoncelli, "Differentiation of discrete multidimensional signals," IEEE TIP 13(4), 2004, 496–508) even better at 5×5 (but NOT numerically consistent, unlike Scharr). Roberts (2×2) and plain central difference are poorest and most anisotropic. Scharr's dissertation abstract reports error reductions of "more than one order of magnitude" (up to 3 orders in specific cases) vs standard parameter choices. Per the scikit-image "Edge operators" documentation: "the Scharr filter results in a less rotational variance than the Sobel filter that is in turn better than the Prewitt filter... The discrepancy between the Prewitt and Sobel filters, and the Scharr filter is stronger for regions of the image where the direction of the gradient is close to diagonal, and for regions with high spatial frequencies."

## 4.4 Equivalence & API
cv2.Sobel(..., ksize=-1) == cv2.Scharr(...). Both use the 3/10/3 kernel. Per OpenCV docs: "If ksize = -1, a 3x3 Scharr filter is used which gives better results than 3x3 Sobel filter."

## 4.5 Why Scharr-x for text/MRZ/barcode
A horizontal derivative (dx=1,dy=0) responds to vertical intensity transitions → vertical strokes of glyphs and vertical barcode bars produce strong x-gradients, while horizontal page structure is suppressed. This makes Scharr-x the standard first gradient step in the black-hat → Scharr-x → normalize/abs → wide-horizontal close → Otsu → connected-components pipeline (the classic MRZ / credit-card / license-plate recipe). Each step: black-hat isolates dark text on bright background; Scharr-x lights up the dense vertical edges of a text row; scaling to 0–255 normalizes; wide close bridges inter-character gaps into a solid band; Otsu thresholds; a second larger close bridges inter-line gaps; erosions detach the band from noise; contour filtering by aspect ratio and fill selects the MRZ.

---

# CHAPTER 5 — "MORPH CLOSE WIDE / SHADE" (both readings) + full MRZ pipeline

## 5.1 (a) Wide/anisotropic close to fuse glyphs into regions
Closing with a wide rectangular SE bridges inter-character and inter-word gaps, fusing glyphs into text-line or text-block regions (MRZ band, paragraphs, ROI proposals).
- SE width heuristic: ≈ 1–1.5× the inter-word gap (or several× the inter-character gap) to bridge within a line but NOT across lines; SE height ≈ ~0.6× x-height.
- Failure modes: too-wide SE bridges adjacent lines or merges text with borders/margins.

## 5.2 (b) Close for SHADE — cross-reference Ch. 2.7 (large-SE close for background estimation).

## 5.3 Full canonical MRZ pipeline (PyImageSearch reference recipe; also used verbatim in production Android/JS scanners)
```
rectKernel = getStructuringElement(MORPH_RECT, (13,5))
sqKernel   = getStructuringElement(MORPH_RECT, (21,21))  # or (34,34)
gray = cvtColor(img, COLOR_BGR2GRAY)
gray = GaussianBlur(gray, (3,3), 0)                       # reduce high-freq noise
blackhat = morphologyEx(gray, MORPH_BLACKHAT, rectKernel) # dark MRZ on light bg
gradX = Sobel(blackhat, CV_32F, 1, 0, ksize=-1)          # Scharr-x
gradX = abs(gradX); scale to [0,255] via convertScaleAbs/normalize
gradX = morphologyEx(gradX, MORPH_CLOSE, rectKernel)     # close gaps between letters
thresh = threshold(gradX, 0, 255, THRESH_BINARY|THRESH_OTSU)
thresh = morphologyEx(thresh, MORPH_CLOSE, sqKernel)     # close gaps between MRZ lines
thresh = erode(thresh, None, iterations=4)               # break spurious connections
# find contours; filter by aspect ratio (wide & short band) and coverage; crop
```
Parameter reasoning: rectKernel is ~3× wider than tall (13×5) because MRZ characters are packed horizontally; the square kernel bridges the ~2 MRZ lines vertically; 4 erosions detach the band from the page border; aspect-ratio + fraction-of-width filtering picks the two-line MRZ band. Production scanners (e.g. alsenet-labs/mrz-scanner) implement exactly "resize → greyscale → Gaussian blur → bottom-hat morphology → Scharr x-edges → Otsu threshold → close/erode/dilate → connected components → aspect-ratio filter → rotation correction → crop," and try all four 90° orientations so rotated uploads still work — recommended for your passports (MRZ = two 44-character lines of digits 0–9, A–Z, and filler '<').

---

# CHAPTER 6 — OTSU THRESHOLDING

## 6.1 Derivation
Normalize the histogram to a pmf p(i), i=0..L−1 (Otsu uses only the zeroth- and first-order cumulative moments). For threshold t, class C₀={0..t}, C₁={t+1..L−1}:
- ω₀(t)=Σ_{i≤t}p(i), ω₁(t)=1−ω₀(t).
- μ₀(t)=Σ_{i≤t} i·p(i)/ω₀, μ₁(t)=Σ_{i>t} i·p(i)/ω₁, μ_T=Σ i·p(i).
Total variance decomposes: σ²_T = σ²_W(t) + σ²_B(t) where
- within-class σ²_W = ω₀σ₀² + ω₁σ₁²,
- between-class σ²_B(t) = ω₀ω₁(μ₀−μ₁)² = (μ_T·ω₀ − μ(t))²/(ω₀(1−ω₀)), with μ(t)=Σ_{i≤t} i·p(i).
Since σ²_T is constant in t, maximizing σ²_B is equivalent to minimizing σ²_W. Otsu (N. Otsu, "A Threshold Selection Method from Gray-Level Histograms," IEEE Trans. SMC 9(1), 1979, 62–66, DOI 10.1109/TSMC.1979.4310076) exhaustively searches t∈[0,L) with running sums, O(L). Separability η = σ²_B/σ²_T ∈[0,1] measures class separability. Otsu is equivalent to Fisher LDA on the histogram and models it as a mixture of two equal-variance, equal-size Gaussians.

## 6.2 Failure modes
Otsu's paper itself notes difficulty "especially in such cases as when the valley is flat and broad, imbued with noise, or when the two peaks are extremely unequal in height."
- Bimodality required — sparse text on a large page gives a huge unimodal background peak; Otsu puts the threshold in the wrong place.
- Class-size imbalance (few text pixels) biases the threshold into the background.
- Uneven illumination → the single global threshold can't fit all regions.
- Noise/low contrast broadens the histogram valley.
Show histograms for each: unimodal (sparse text), skewed (imbalance), smeared (illumination).

## 6.3 Fixes
- Gaussian blur before Otsu (the classic "Otsu with noise" example).
- Restrict Otsu to a foreground-relevant histogram range.
- **Apply Otsu on the black-hat output** rather than raw image — black-hat makes the strokes a compact bright class on a near-zero background, restoring bimodality (this is what the MRZ pipeline exploits).
- Per-block / adaptive Otsu; 2D Otsu (uses pixel + local-mean).

## 6.4 Alternatives with equations
- Fixed global threshold T.
- Adaptive mean / adaptive Gaussian (cv2.adaptiveThreshold): T(x,y) = mean_{block}(x,y) − C, or Gaussian-weighted mean − C; choose blockSize > glyph size, C small positive.
- Niblack (1986): T = m(x,y) + k·s(x,y), k≈−0.2.
- Sauvola & Pietikäinen (2000): T = m·[1 + k·(s/R − 1)], k≈0.2–0.5, R≈128; O(1) per pixel via integral images (mean and mean-of-squares). Best classic method for degraded/uneven documents.
- Wolf–Jolion: normalizes contrast using global min and dynamic range.
- NICK: T = m + k·√(Σx² − m²), robust for low-contrast.
- Bradley–Roth: integral-image adaptive mean.
- Kittler–Illingworth minimum-error (1986): models histogram as two Gaussians, minimizes classification error (better than Otsu under unequal variances).
- Triangle method (cv2.THRESH_TRIANGLE): geometric, good for unimodal-with-tail histograms.
- Yen, Li (min cross-entropy), Huang (fuzzy) entropy methods.
- Multi-Otsu (skimage.filters.threshold_multiotsu; OpenCV doesn't ship it).
- Su et al. (local image contrast), Howe (energy minimization / graph cut).
- Learned: DE-GAN, DeepOtsu, SauvolaNet.

## 6.5 DIBCO benchmark numbers (F-measure / DRD)
On the DIBCO 2011 dataset, verified against He & Schomaker, "DeepOtsu" (Pattern Recognition 2019, arXiv:1901.06081), Table 5: Otsu FM 82.1 / DRD 9.0; Sauvola FM 82.1 / DRD 8.5; Howe FM 91.7 / DRD 3.4; Vo (deep) FM 93.3 / DRD 2.0; DeepOtsu(SR) FM 93.4 / DRD 1.9. So classic global/local thresholds trail modern deep methods by ~10 FM points on degraded documents, but Sauvola remains the best cheap local method (and better DRD than Otsu).

## 6.6 Binarization metrics
DIBCO uses F-measure, pseudo-F-measure (p-FM), PSNR, DRD (distance reciprocal distortion, correlates with human perception), MPM (misclassification penalty). Plus downstream OCR CER.

## 6.7 OpenCV specifics
cv2.threshold(src, thresh, maxval, THRESH_BINARY|THRESH_OTSU) — Otsu **ignores the passed thresh**, computes and RETURNS the optimal t (as the first return value). Combine with THRESH_BINARY_INV to get white text on black. Otsu requires 8-bit single channel.

---

# CHAPTER 7 — GLYPH-LEVEL ANALYSIS

## 7.1 Typographic fundamentals
Glyph (visual mark) vs character (abstract) vs grapheme vs codepoint (Unicode). Baseline, x-height, cap-height, ascender/descender, stroke width, counters (holes), serifs, kerning/tracking, ligatures.
- Arabic: cursive joining → four contextual forms (initial/medial/final/isolated); a single character maps to multiple glyphs, and words connect along a baseline (kashida). Binarization/thinning must preserve connectivity.
- CJK: high stroke density, square em-box; needs higher resolution per glyph.

## 7.2 Glyph geometry drives preprocessing parameters
- Stroke width → morphological SE size and black-hat kernel (SE ≈ 2–3× stroke).
- x-height → minimum resolution / upscale factor (cap-height ≥ ~20px, ~300 DPI).
- Inter-glyph spacing → closing kernel width.

## 7.3 Glyph-level algorithms
- Connected components: cv2.connectedComponentsWithStats; filter by area, aspect, extent, stroke-width consistency to separate text from noise.
- Stroke Width Transform (Epshtein, Ofek & Wexler, "Detecting Text in Natural Scenes with Stroke Width Transform," CVPR 2010, 2963–2970): shoot rays along gradient from an edge pixel to the opposite edge; if gradient orientations are roughly opposite, assign the ray length as stroke width; group pixels of consistent width into letters.
- Distance transform / run-length estimate of stroke width.
- Projection profiles for line/word/glyph segmentation.
- Contour hierarchies (cv2.findContours RETR_CCOMP/TREE) to find counters (holes in o,a,e).
- Glyph normalization: size, slant/italic correction, moment normalization, nonlinear/pseudo-2D normalization (classical OCR).
- Skeletonization for stroke topology.
- Synthesis: FreeType/Pillow ImageFont, TextRecognitionDataGenerator (trdg), SynthText for training data.

## 7.4 MSER
Maximally Stable Extremal Regions (Matas et al., "Robust wide-baseline stereo from maximally stable extremal regions," BMVC 2002 / IVC 2004) is the traditional glyph-region detector: thresholds at all levels, keeps regions stable across a range. Weaknesses: sensitive to blur, low contrast, and connected/overlapping glyphs (Arabic cursive), and produces many false positives — reasons you've moved to the morphological black-hat/Scharr pipeline, which is faster and more robust for uniform documents but gives up MSER's multi-level adaptivity to arbitrary backgrounds.

---

# CHAPTER 8 — COLOUR / INTENSITY

## 8.1 Grayscale conversion
- BT.601 luma: Y = 0.299R + 0.587G + 0.114B (OpenCV COLOR_BGR2GRAY).
- BT.709: Y = 0.2126R + 0.7152G + 0.0722B.
- Simple average: (R+G+B)/3.
Channel selection/mixing can beat luma: to drop a colored security background or blue guilloche, choose/mix the channel where text contrast is highest (e.g. red channel kills red stamps; blue-vs-background separation). Max-RGB (per-pixel channel maximum) or a custom projection often improves OCR contrast on colored security print.

## 8.2 Gamma & sRGB
sRGB transfer: linear→display encoding ≈ V = 1.055·L^(1/2.4) − 0.055 (L>0.0031308). Gamma correction I' = 255·(I/255)^γ. Operate denoise/blur in linear light for physical correctness; contrast ops often done in perceptual (gamma) space.

## 8.3 Contrast/normalization
cv2.normalize (min-max to [0,255]); histogram equalization (global CDF mapping); CLAHE (Ch. 9).

---

# CHAPTER 9 — CLAHE
Zuiderveld, "Contrast Limited Adaptive Histogram Equalization," Graphics Gems IV, 1994, 474–485.
Divide image into tiles (e.g. 8×8), equalize each tile's histogram, but clip the histogram at a clip limit and redistribute the excess to prevent noise amplification:
  H'(i) = min(H(i), C_limit) + [Σ_j max(0, H(j) − C_limit)]/N.
Bilinearly interpolate the per-tile mappings to avoid tile boundaries. cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)). For documents: modest clip (1.5–3) improves faint text without over-amplifying paper texture. Prefer CLAHE over global equalization for unevenly lit IDs.

---

# CHAPTER 10 — SMOOTHING / DENOISING

- Box/mean: cv2.blur — fast, blurs edges.
- Gaussian: cv2.GaussianBlur; σ↔ksize: default ksize from σ or vice versa; kernel truncated at ~3–4σ. Separable.
- Median: cv2.medianBlur — removes salt-and-pepper impulse noise, preserves edges; good for scan speckle.
- Bilateral (Tomasi & Manduchi, "Bilateral Filtering for Gray and Color Images," ICCV 1998, 839–846): edge-preserving.
  J(x) = (1/k(x)) Σ_ξ f(ξ)·g_s(‖ξ−x‖)·g_r(|I(ξ)−I(x)|), k(x)=Σ_ξ g_s·g_r (normalization). Spatial kernel g_s and range kernel g_r; nonlinear because weights depend on intensity. cv2.bilateralFilter(d, sigmaColor, sigmaSpace).
- Non-Local Means (Buades, Coll & Morel 2005): average pixels weighted by patch similarity. cv2.fastNlMeansDenoising.
- Guided filter (cv2.ximgproc.guidedFilter): edge-preserving, O(1).
- Anisotropic diffusion (Perona & Malik, "Scale-space and edge detection using anisotropic diffusion," IEEE PAMI 1990): ∂I/∂t = div(c(‖∇I‖)∇I), c decreasing → smooth within regions, preserve edges.
- Total variation / ROF (Rudin–Osher–Fatemi 1992): min ∫|∇u| + (λ/2)‖u−f‖².
Safe before OCR: median (speckle), mild bilateral/NLM. **Dangerous:** aggressive Gaussian/bilateral destroys thin strokes (sub-2px) — test CER before adopting.

---

# CHAPTER 11 — SHARPENING & DECONVOLUTION
- Unsharp mask: g = f + λ(f − G_σ*f). cv2.addWeighted(f,1+λ,blur,−λ,0).
- High-boost: generalization with amplified original.
- Laplacian sharpening: g = f − c·∇²f.
- Deconvolution: Wiener (frequency-domain, known/estimated PSF and noise SNR), Richardson–Lucy (iterative, Poisson). Motion blur PSF = line kernel; defocus PSF = disk. Relevant for camera-captured IDs with motion/defocus.

---

# CHAPTER 12 — EDGE & FEATURE
- Canny (Canny, "A Computational Approach to Edge Detection," IEEE PAMI 1986): (1) Gaussian smoothing, (2) Sobel gradient, (3) non-maximum suppression along gradient, (4) double threshold + hysteresis. Auto thresholds via median: lo=0.66·med, hi=1.33·med. cv2.Canny.
- Laplacian: ∇²f, cv2.Laplacian (CV_16S then abs).
- LoG (Marr–Hildreth) and DoG (Gaussian difference approximating LoG); zero-crossings mark edges.

---

# CHAPTER 13 — GEOMETRY

## 13.1 Deskew
Methods and trade-offs (from comparative surveys grouping methods into projection-profile, feature-point, Hough, and orientation-sensitive families):
- Hough transform on edges/text pixels: robust and accurate (a modified Hough method achieved ~99.9% page-orientation accuracy in one study), but memory- and compute-heavy; struggles on sparse text and needs careful peak detection. Fast Hough variants reduce runtime from ~21 ms (discrete Radon) to ~45 µs on a test image.
- Radon transform / projection-profile variance maximization: rotate over angles, maximize row-sum variance (text lines align → sharp profile). One study reports Radon giving 100% skew-estimation accuracy on printed docs with text, and being the fastest for small images and robust even with pictures.
- minAreaRect on merged text blobs (your approach): fast, robust for uniform pages; fit rectangle to the largest text region and read its angle.
- FFT-based: the magnitude spectrum shows a directional streak perpendicular to text lines; measure its angle. Fast, but ambiguous on sparse/mixed content. Modern FFT-radial-projection (jdeskew, DISE-2021) is a strong default.

## 13.2 Orientation 0/90/180/270
Small CNN in ONNX, or classical cues: ascender/descender asymmetry, text-line density, and the fact that aspect ratio + face/MRZ location disambiguate (ID pipelines rotate through all four and pick the readable one; note that a 90° rotation is undetectable by skew-only methods, so ID-card pipelines often use aspect ratio thresholds, e.g. rotate if W/H < 1.58, before cropping).

## 13.3 Perspective / keystone
Detect document quadrilateral (largest 4-point contour after edge detection), then cv2.getPerspectiveTransform + cv2.warpPerspective (or cv2.findHomography with RANSAC for noisy correspondences). Page-border/background removal by contour masking.

## 13.4 Dewarping curved pages
OpenCV ships none; use DocUNet, DewarpNet, DocTr (learned), or classical text-line-based dewarping (fit baselines, warp to straighten).

## 13.5 Lens distortion
cv2.undistort with calibrated K, dist coefficients (barrel/pincushion), rarely needed for documents but relevant for wide-angle phone lenses.

---

# CHAPTER 14 — DOCUMENT-SPECIFIC OPS
- Shadow removal: divide by large-SE/Gaussian background, or dilate-then-median background estimate then normalize.
- Glare/specular suppression on laminated IDs: white-top-hat detect + inpaint; multi-frame from video (MIDV) to pick glare-free frames.
- Moiré removal (screen photos): notch filter in FFT at the periodic peaks; or FFT band-stop.
- JPEG blocking: deblocking filters / mild bilateral on the 8×8 grid.
- Holographic overlay: multi-frame median across video frames.
- Table/rule-line removal: long anisotropic morphological SEs (horizontal for row rules, vertical for columns), subtract detected lines.
- Watermark/stamp suppression: color-channel selection (remove red stamps), morphological reconstruction, K-means color removal (shown to lift Sauvola/Otsu binarization on stamped documents).
- Salt-and-pepper: median filter.
- Border noise removal: connected-component removal touching image border.
- DPI normalization: resize to ~300 DPI equivalent using glyph-height estimate.

---

# CHAPTER 15 — PIPELINE DESIGN

## 15.1 Canonical order and why
geometry (perspective, deskew, rotation) → illumination (black-hat/division/homomorphic) → denoise (median/bilateral) → contrast (CLAHE/normalize) → [binarize only if a classical stage needs it] → morphological cleanup.
Rationale: correct geometry first so later local operators see axis-aligned text; flatten illumination before contrast so global stats are meaningful; denoise before threshold; morphology last to clean the mask.
Commutativity: point ops (gamma, normalize) commute with each other but not with neighborhood ops; geometry (resampling) does not commute with denoise (resample-then-denoise ≠ denoise-then-resample).

## 15.2 When NOT to binarize
Modern deep OCR (PaddleOCR, Nemotron OCR) and VLMs (Qwen-VL) are trained on grayscale/RGB. Evidence: since Tesseract 4.0 "recognition does not (under normal circumstances) use that binarized image, but uses the greyscale-converted raw image" (Tesseract issue #3083); the binarized image is retained only for segmentation/layout. A multi-parameter CRNN study (Reul et al., arXiv:2008.02777) found "Tesseract's models actually work much better on grayscale input than on binarized input," and that models "are trained to a specific binarization context... and break down when used with a different algorithm" (their own model reaches CER >10% on binarized but "very well on grayscale"). Practical rule: **feed grayscale/RGB to the recognizer; use binarization only inside classical detection/segmentation (MRZ band, table removal).** Over-aggressive preprocessing (heavy denoise, binarize, sharpen) frequently HURTS transformer OCR/VLMs by destroying anti-aliasing cues. Caveat: for some heavily degraded historical/scanned material, a good binarization can still beat grayscale — always A/B test.

## 15.3 A/B testing a chain
Build a golden dataset (your real docs + MIDV-500/2020 for IDs). Metric: field-level CER/WER and per-field extraction accuracy. Use ablation matrices (toggle each stage) and factorial/grid search over key parameters (SE size, clip limit, upscale factor), selecting on downstream CER, not on visual appeal or PSNR.

## 15.4 Performance
- UMat/OpenCL (cv2.UMat) for transparent GPU; cv2.cuda module for explicit CUDA; IPP backend on Intel.
- float32 vs uint8: uint8 faster and less memory; float32 needed for signed gradients and division.
- In-place ops (dst=src) where allowed reduce allocations.
- Rough latency: point ops and separable filters are ~sub-ms to few-ms per MP on CPU; bilateral/NLM/rolling-ball are 10–100× slower; FFT-based ops scale as MP·log MP. (For reference, one vendor measured Lanczos 1080p→4K at ~35 ms CPU.) Budget accordingly for latency-constrained serving.

---

# CHAPTER 16 — EXPERIMENTS

## 16.1 Individual
- Lanczos vs bicubic vs area across 0.25×–8×: PSNR/SSIM + CER curves; zone-plate aliasing images.
- Black-hat SE size 5→51: plot recovered-text contrast and OCR CER vs SE; intensity profile across one stroke at each SE.
- Sobel/Scharr ksize & ddepth: demonstrate CV_8U truncation; angular-error-vs-orientation curves for Sobel/Scharr/Prewitt.
- Otsu vs Sauvola vs adaptive across illumination conditions: F-measure vs illumination gradient; histograms with threshold + σ²_B(t) overlay.

## 16.2 Combined / ablation
(a) MRZ pipeline ablation: toggle black-hat, Scharr-x, wide close, second close, erosions; report MRZ-band IoU and end-to-end field CER.
(b) Shadow-corrected binarization chain for phone ID.
(c) Upscale-then-binarize chain for low-DPI small text.
(d) Table/line-removal chain.
Use a factorial design over {SE width, clip limit, upscale factor, threshold method} scored on CER.

## 16.3 Datasets
- Synthetic: cameraman, lena, slanted-edge MTF chart, Siemens star, zone plate (for interpolation/aliasing).
- Documents: DIBCO & H-DIBCO 2009–2019 (binarization GT with FM/p-FM/PSNR/DRD), ICDAR RDD, SmartDoc-QA, and the MIDV family (directly relevant). MIDV-500 (Arlazarov et al., arXiv:1807.05786): 500 video clips of 50 identity-document types — "17 types of ID cards, 14 types of passports, 13 types of driving licences and 6 other identity documents of various countries" — 15,000 annotated 1080×1920 frames, 546 text fields in different languages. MIDV-2019 adds distorted and low-light clips; MIDV-2020 adds 1000 clips + 2000 scans + 1000 photos of 1000 unique mock documents with generated faces (72,409 annotated images). Also FUNSD, SROIE, CORD, IIIT5K, TextZoom (paired LR/HR text).

## 16.4 Required plots
1D kernel shapes (Lanczos-2/3/4 vs cubic vs linear); DTFT magnitude in dB; 2D kernel heatmaps; zone-plate resampling artifacts; histograms with Otsu threshold + σ²_B(t) curve; gradient-direction angular-error-vs-orientation curves; before/after grids; intensity profiles across a stroke at each stage; illumination-field surface plots; PSNR/SSIM-vs-parameter; CER-vs-parameter; ablation bar chart.

---

# CHEAT SHEET — OpenCV functions & flags
| Task | Function | Key flags/params |
|---|---|---|
| Resize | cv2.resize | INTER_NEAREST/LINEAR/CUBIC/AREA/LANCZOS4/LINEAR_EXACT/NEAREST_EXACT |
| Warp | cv2.warpAffine/warpPerspective/remap | interpolation flags, borderMode |
| Structuring element | cv2.getStructuringElement | MORPH_RECT/ELLIPSE/CROSS |
| Morphology | cv2.morphologyEx | MORPH_ERODE/DILATE/OPEN/CLOSE/GRADIENT/TOPHAT/BLACKHAT/HITMISS; iterations |
| Gradient | cv2.Sobel / cv2.Scharr | ddepth=CV_16S/32F; ksize=-1 → Scharr; scale, delta |
| Deriv kernels | cv2.getDerivKernels | ksize, normalize |
| Threshold | cv2.threshold | THRESH_BINARY[_INV]\|THRESH_OTSU\|THRESH_TRIANGLE |
| Adaptive | cv2.adaptiveThreshold | ADAPTIVE_THRESH_MEAN_C/GAUSSIAN_C, blockSize, C |
| Blur | cv2.blur/GaussianBlur/medianBlur/bilateralFilter | ksize, sigma |
| Denoise | cv2.fastNlMeansDenoising | h, templateWindow, searchWindow |
| CLAHE | cv2.createCLAHE | clipLimit, tileGridSize |
| Equalize | cv2.equalizeHist | — |
| Normalize | cv2.normalize | NORM_MINMAX |
| Canny | cv2.Canny | thr1, thr2, apertureSize, L2gradient |
| CC | cv2.connectedComponentsWithStats | connectivity |
| Contours | cv2.findContours | RETR_*, CHAIN_APPROX_* |
| Perspective | cv2.getPerspectiveTransform/findHomography | RANSAC |
| SuperRes | cv2.dnn_superres | EDSR/ESPCN/FSRCNN/LapSRN |
| Thinning | cv2.ximgproc.thinning | THINNING_ZHANGSUEN/GUOHALL |

---

# GLOSSARY (selected)
- **Black-hat:** closing minus original; extracts dark features smaller than SE.
- **Top-hat:** original minus opening; extracts bright features smaller than SE.
- **DRD:** Distance Reciprocal Distortion, DIBCO metric for binarization visual distortion.
- **DroG:** Derivative of Gaussian.
- **Gibbs phenomenon:** overshoot/ringing near discontinuities from band-limited reconstruction.
- **Homomorphic filtering:** log → high-pass → exp for multiplicative illumination correction.
- **MRZ:** Machine-Readable Zone (two/three OCR-B lines of 44 chars on passports/IDs).
- **MTF50:** spatial frequency at which modulation transfer function falls to 50%.

## Recommendations
1. **Keep your existing MRZ pipeline** (black-hat → Scharr-x → wide close → Otsu → CC filter); it is textbook-correct. Tune rectKernel width to your capture DPI (~3:1 aspect, e.g. 13×5 at moderate resolution) and rotate through all 4 orientations. Benchmark on MIDV-2020 passports.
2. **Do NOT hard-binarize before PaddleOCR / Nemotron / Qwen-VL.** Feed deskewed, illumination-flattened grayscale/RGB. Reserve binarization for detection/segmentation only. Change this only if an A/B test on your golden set shows binarized CER lower (possible for heavily degraded scans).
3. **Illumination:** default to division by a large-SE morphological-close background for camera shadows (multiplicative); use black-hat when you specifically want dark strokes isolated; homomorphic for combined shading+contrast; white-top-hat + inpaint for laminate glare.
4. **Upscaling:** upscale sub-10px x-height text to ~300 DPI with INTER_CUBIC or INTER_LANCZOS4; use INTER_AREA for any downscaling. If CER on tiny fields stays high, add a learned text-SR stage (FSRCNN via dnn_superres, or a TSRN/TATT-class model — TATT roughly doubled CRNN accuracy over bicubic on TextZoom).
5. **Thresholding (when needed):** Sauvola (k≈0.3, R=128, window ≈ 1.5× line height) beats Otsu on uneven documents (better DRD at equal FM on DIBCO 2011); run Otsu on the black-hat image, never the raw image, for sparse text.
6. **Measure on CER, not PSNR.** Build ablation matrices and factorial parameter sweeps against per-field extraction accuracy.

Thresholds that change the recommendations: if measured field CER with grayscale ≥ binarized on your golden set, revisit binarization; if x-height ≥ ~20px already, skip upscaling; if capture is controlled/flat-lit, skip illumination correction to save latency.

## Caveats
- Several DIBCO/benchmark numbers come from competition and re-implementation papers; exact figures vary by dataset year and re-implementation. The DIBCO 2011 numbers here are taken specifically from the DeepOtsu paper's comparison table. Treat cross-paper comparisons as indicative.
- The specific Scharr angular-error degree figures (Sobel ~a few degrees vs Scharr <~0.2°) are widely cited to the Jähne Handbook but could not be verified as an exact numeral from the primary source; the dissertation states error reductions of "more than one order of magnitude" (up to three), which is confirmed.
- OpenCV internal fixed-point details (INTER_BITS quantization, weight tables) are accurate as of current 4.x but are implementation details that can change.
- "iterations=n = bigger kernel" holds only for flat convex SEs; do not rely on it for non-flat SEs or compound ops.
- Whether preprocessing helps is engine- and dataset-specific; the grayscale-beats-binarized finding is strong for LSTM/CRNN/transformer OCR but always validate on your own golden set.
- Some SR-for-OCR gains are reported on scene text (TextZoom), not identity documents specifically; validate any SR stage on MIDV-class data before production.