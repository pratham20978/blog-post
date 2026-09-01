# The Mathematical Foundations of Classical Image Processing and Computer Vision: A Deep Reference Library

## TL;DR
- This is a source-first, math-first map of classical vision organized into five layers — filtering/transforms, feature detection, geometric vision, segmentation, and cross-cutting math — with the core formulation, the "why it works" principle, and annotated primary sources for every topic.
- The most efficient path: use **Szeliski 2nd ed. (free PDF at szeliski.org/Book)** as the spine, **Hartley & Zisserman** for all geometry, **Lindeberg** for scale-space, and read the original seminal papers (Canny 1986, Lowe 2004, Zhang 2000, Fischler-Bolles 1981, Otsu 1979, Perona-Malik 1990) rather than tutorials.
- Study reference implementations to bridge math and code: **VLFeat** (math-heavy docs for SIFT/MSER), **scikit-image**, and the **OpenCV source** — but derive the equations from the papers first.

## Key Findings
- Almost every classical operator reduces to a few mathematical cores: **convolution/linear systems theory** (filtering, edges, pyramids), **the structure/second-moment tensor and Hessian** (corners, blobs, SIFT/SURF), **projective geometry + linear algebra (SVD, least squares)** (all multi-view geometry), and **energy minimization** (segmentation, optical flow, active contours, MRFs).
- The seminal literature is remarkably accessible: original papers for Canny, Harris, Lowe/SIFT, Perona-Malik, Zhang, Otsu, Lucas-Kanade, Horn-Schunck, RANSAC, graph cuts, and mean shift are available as free PDFs (links verified below).
- Two textbooks are freely and legally downloadable in full: **Szeliski 2nd ed.** and the sample chapters of **Hartley & Zisserman**. These plus **Gonzalez & Woods**, **Forsyth & Ponce**, **Prince**, and **Lindeberg** cover the entire syllabus with rigor.
- Scale-space theory (Witkin → Koenderink → Lindeberg) is the unifying thread connecting Gaussian filtering, pyramids, LoG/DoG detection, and SIFT.

## Details

### 1. Core Filtering & Transforms

#### 1.1 Convolution and correlation
**Math.** Discrete convolution (f∗h)[m,n] = Σ_i Σ_j f[i,j] h[m−i, n−j]; correlation drops the flip. Convolution is commutative, associative, shift-invariant — the unique linear shift-invariant (LSI) operation. **Separability**: if h = h_x h_yᵀ (rank-1 kernel), 2D convolution factors into two 1D passes, O(N²K²)→O(N²K). **Boundary handling** (zero-pad, reflect, replicate, wrap) extends f outside its support; periodic extension is what the DFT assumes.
**Why it works.** The convolution theorem shows convolution is diagonalized by the Fourier basis — complex exponentials are eigenfunctions of LSI systems. Separability is a rank-1 outer-product factorization of the kernel.
**Sources.** Gonzalez & Woods, *Digital Image Processing*, 4th ed. (Pearson, 2018), Ch. 3–4. Szeliski, *Computer Vision: Algorithms and Applications*, 2nd ed., §3.2, free PDF: https://szeliski.org/Book/ . Oppenheim & Schafer, *Discrete-Time Signal Processing*.

#### 1.2 Linear filtering, kernels, the convolution theorem
**Math.** ℱ{f∗h}=ℱ{f}·ℱ{h}; dually ℱ{f·h}=ℱ{f}∗ℱ{h}. A spatial filter is a transfer function H(u,v); low/high/band-pass filters are characterized entirely by H.
**Why it works.** {e^{j2π(ux+vy)}} are eigenfunctions of convolution with eigenvalues H(u,v).
**Sources.** Gonzalez & Woods Ch. 4; Szeliski §3.4; Bracewell, *The Fourier Transform and Its Applications*.

#### 1.3 Fourier analysis: DFT, FFT, frequency-domain filtering, sampling/Nyquist
**Math.** Continuous FT F(u)=∫ f(x) e^{−j2πux} dx. DFT F[k]=Σ_{n=0}^{N−1} f[n] e^{−j2πkn/N}. The **FFT** (Cooley–Tukey) computes the DFT in O(N log N). **Sampling theorem**: a signal band-limited to B is reconstructible from samples at rate f_s>2B (Nyquist); undersampling causes aliasing.
**Why it works.** The FFT exploits periodicity/symmetry of roots of unity. Sampling convolves the spectrum with a Dirac comb, replicating it at f_s; replica overlap is aliasing.
**Sources.** Cooley & Tukey (1965), "An algorithm for the machine calculation of complex Fourier series," *Math. Comp.* 19(90):297–301, DOI: 10.1090/S0025-5718-1965-0178586-1. Shannon (1949), "Communication in the Presence of Noise," *Proc. IRE* 37(1):10–21, DOI: 10.1109/JRPROC.1949.232969. Bracewell; Gonzalez & Woods Ch. 4.

#### 1.4 Discrete Cosine Transform (DCT) and compression
**Math.** DCT-II: X[k]=Σ_{n=0}^{N−1} x[n] cos[(π/N)(n+½)k]. A real orthogonal transform. JPEG tiles into 8×8 blocks, 2D-DCTs, quantizes (lossy), entropy-codes.
**Why it works.** For AR(1) signals with high inter-pixel correlation (a good natural-image model) the DCT asymptotically approaches the **Karhunen–Loève transform** (optimal decorrelating basis) but with a fixed, fast basis. Energy compaction into few low-frequency coefficients makes quantization cheap.
**Sources.** Ahmed, Natarajan, Rao (1974), "Discrete Cosine Transform," *IEEE Trans. Computers* C-23(1):90–93, DOI: 10.1109/T-C.1974.223784. Wallace (1992), "The JPEG Still Picture Compression Standard," *IEEE Trans. Consumer Electronics*. Gonzalez & Woods Ch. 8.

#### 1.5 Wavelet transforms (CWT, DWT, multiresolution analysis)
**Math.** CWT W(a,b)=(1/√a)∫ f(x) ψ*((x−b)/a) dx. **DWT** uses a dyadic orthonormal basis {ψ_{j,k}(x)=2^{−j/2}ψ(2^{−j}x−k)}. **MRA**: nested subspaces …⊂V_1⊂V_0⊂V_{−1}… with scaling function φ; detail spaces W_j are orthogonal complements. Mallat's pyramidal algorithm computes the DWT via **quadrature mirror filters** and downsampling.
**Why it works.** Wavelets give simultaneous space-frequency localization (subject to the uncertainty principle), unlike the global Fourier basis; MRA formalizes "coarse approximation + successive details."
**Sources.** Mallat (1989), "A Theory for Multiresolution Signal Decomposition: The Wavelet Representation," *IEEE PAMI* 11(7):674–693, DOI: 10.1109/34.192463. Daubechies, *Ten Lectures on Wavelets* (SIAM, 1992). Mallat, *A Wavelet Tour of Signal Processing*, 3rd ed.

#### 1.6 Gaussian filtering and scale-space theory
**Math.** G_σ=(1/2πσ²)e^{−(x²+y²)/2σ²}. The **scale space** L(x,y;t)=G_{√t}∗f satisfies ∂_t L=½∇²L with L(·;0)=f. Larger t = coarser scale.
**Why it works.** The Gaussian is the unique kernel satisfying the scale-space axioms — linearity, shift/rotation invariance, the semigroup property (G_s∗G_t=G_{s+t}), and **non-enhancement of local extrema** (causality: no new structure at coarser scales).
**Sources.** Witkin (1983), "Scale-space filtering," *IJCAI*. Koenderink (1984), "The structure of images," *Biol. Cybernetics* 50:363–370, DOI: 10.1007/BF00336961. Lindeberg, *Scale-Space Theory in Computer Vision* (Kluwer, 1994). Lindeberg (1994), *J. Applied Statistics* 21(2):225–270.

#### 1.7 Edge/gradient operators (Sobel, Prewitt, Scharr, Laplacian, LoG, DoG)
**Math.** Gradient ∇f=(f_x,f_y); magnitude √(f_x²+f_y²), orientation atan2(f_y,f_x). Sobel/Prewitt/Scharr are separable smoothing⊗differencing 3×3 kernels (Scharr optimizes rotational symmetry). **Laplacian** ∇²f detects edges as zero-crossings. **LoG**=∇²(G_σ∗f). **DoG**=(G_{σ1}−G_{σ2})∗f approximates σ∇²G, since ∂G/∂σ=σ∇²G.
**Why it works.** Differentiation amplifies high-frequency noise, so operators pre-smooth; LoG/DoG couple smoothing and differentiation at a scale. Zero-crossings of ∇²(G∗f) localize edges (Marr–Hildreth).
**Sources.** Marr & Hildreth (1980), "Theory of edge detection," *Proc. Royal Society B* 207:187–217, DOI: 10.1098/rspb.1980.0020. Scharr PhD thesis (Heidelberg, 2000); Jähne, *Digital Image Processing*. Gonzalez & Woods Ch. 10; Szeliski §7.2.

#### 1.8 Canny edge detector (full derivation & optimality)
**Math & derivation.** Canny posed edge detection as optimizing three criteria as functionals of the filter response f, for a step edge in white noise: (1) **detection** — maximize SNR ∝ |∫ G(−x)f(x)dx|/(n₀√∫f²); (2) **localization** — maximize 1/σ_x ∝ |∫ G'(−x)f'(x)dx|/(n₀√∫f'²); (3) **single response** — constrain mean distance between false maxima. Maximizing the product (1)·(2) subject to (3) via calculus of variations yields an optimal 1D filter well-approximated by the **first derivative of a Gaussian** G'. Pipeline: smooth, gradient, **non-maximum suppression** along gradient direction, **hysteresis thresholding**.
**Why it works.** There is a fundamental detection–localization trade-off (an uncertainty principle): wider filters detect better but localize worse; G' is the optimizer. Hysteresis exploits edge connectivity to suppress streaking.
**Sources.** Canny (1986), "A Computational Approach to Edge Detection," *IEEE PAMI* PAMI-8(6):679–698, DOI: 10.1109/TPAMI.1986.4767851. Free PDF: https://cecas.clemson.edu/~ahoover/ece431/refs/Canny.pdf . Deriche (1987), "Using Canny's criteria to derive a recursively implemented optimal edge detector," *IJCV* 1:167–187.

#### 1.9 Anisotropic diffusion (Perona–Malik) and PDE / total-variation methods
**Math.** Perona–Malik: ∂_t I=div(c(|∇I|)∇I), with edge-stopping diffusivity c(s)=1/(1+(s/K)²) or exp(−(s/K)²). Small gradients → c≈1 (isotropic smoothing); large → c≈0 (diffusion halts, edges preserved). **Total variation (ROF)**: minimize ∫|∇u| dx + (λ/2)∫(u−f)² dx; the TV (L¹-of-gradient) term denoises while allowing discontinuities, unlike L² (Tikhonov).
**Why it works.** PM is forward-backward nonlinear diffusion that sharpens edges (can be ill-posed → regularized Catté et al. 1992 variant). TV works because the total-variation seminorm does not over-penalize jumps (the space BV of bounded variation).
**Sources.** Perona & Malik (1990), "Scale-Space and Edge Detection Using Anisotropic Diffusion," *IEEE PAMI* 12(7):629–639, DOI: 10.1109/34.56205. Free PDF: https://authors.library.caltech.edu/records/1p8h5-5x870 . Rudin, Osher, Fatemi (1992), "Nonlinear total variation based noise removal algorithms," *Physica D* 60(1–4):259–268, DOI: 10.1016/0167-2789(92)90242-F. Weickert, *Anisotropic Diffusion in Image Processing* (Teubner, 1998). Chambolle (2004), *J. Math. Imaging & Vision*.

#### 1.10 Bilateral filtering, non-local means, guided filter
**Math.** Bilateral: BF[I]_p=(1/W_p)Σ_q G_{σs}(‖p−q‖)G_{σr}(|I_p−I_q|)I_q — product of spatial and intensity (range) kernels; edge-preserving because pixels across an edge have large |I_p−I_q|. **Non-local means**: NL[I]_p=Σ_q w(p,q)I_q with w∝exp(−‖patch(p)−patch(q)‖²/h²) — averages over similar patches anywhere, exploiting self-similarity. **Guided filter**: output is a local linear transform of a guidance image, q_i=a_k I_i+b_k solved by ridge regression; O(N) with no gradient reversal.
**Why it works.** All three replace fixed weights with data-adaptive weights respecting image structure; NLM generalizes locality to appearance similarity.
**Sources.** Tomasi & Manduchi (1998), "Bilateral Filtering for Gray and Color Images," *ICCV* 839–846, DOI: 10.1109/ICCV.1998.710815. Buades, Coll, Morel (2005), "A non-local algorithm for image denoising," *CVPR* 2:60–65, DOI: 10.1109/CVPR.2005.38; IPOL reference code: https://www.ipol.im/pub/art/2011/bcm_nlm/ . He, Sun, Tang (2013), "Guided Image Filtering," *IEEE PAMI* 35(6):1397–1409, DOI: 10.1109/TPAMI.2012.213. Paris, Kornprobst, Tumblin, Durand (2009), "Bilateral Filtering: Theory and Applications," *Found. & Trends CGV* 4(1):1–73, DOI: 10.1561/0600000020.

#### 1.11 Mathematical morphology
**Math.** For binary A and structuring element B: **erosion** A⊖B={z|B_z⊆A}; **dilation** A⊕B={z|B̂_z∩A≠∅}; **opening** A∘B=(A⊖B)⊕B; **closing** A•B=(A⊕B)⊖B. Grayscale morphology replaces set ops with min/max over the SE.
**Why it works.** Founded on **lattice theory**: images form a complete lattice under pointwise order; erosion/dilation commute with infimum/supremum (an **adjunction**: A⊕B⊆C ⇔ A⊆C⊖B̂). Openings/closings are the induced idempotent increasing filters.
**Sources.** Serra, *Image Analysis and Mathematical Morphology* (Academic Press, 1982). Matheron, *Random Sets and Integral Geometry* (Wiley, 1975). Soille, *Morphological Image Analysis* (Springer, 2003). Haralick, Sternberg, Zhuang (1987), "Image Analysis Using Mathematical Morphology," *IEEE PAMI* 9(4):532–550, DOI: 10.1109/TPAMI.1987.4767941.

### 2. Feature Detection & Description

#### 2.1 Harris corner detector (structure tensor)
**Math.** Weighted SSD for a shift: E(u,v)≈[u v]M[u v]ᵀ, with the **second-moment/structure tensor** M=Σ w[[I_x², I_xI_y],[I_xI_y, I_y²]]. With eigenvalues λ₁,λ₂: response **R=det(M)−k·tr(M)²**. The constant k is an empirical value from Harris & Stephens (1988); OpenCV's `cornerHarris` and CUDA_ORB use **k = 0.04 by default** (per arXiv:2506.07164: "In CUDA_ORB and OpenCV library, k is set to a constant of 0.04"). Two large eigenvalues → corner; one → edge; none → flat.
**Why it works.** M is a first-order Taylor model of local autocorrelation; its eigenstructure captures directional intensity variation. Shi–Tomasi uses min(λ₁,λ₂).
**Sources.** Harris & Stephens (1988), "A Combined Corner and Edge Detector," *Alvey Vision Conf.* 147–151, DOI: 10.5244/C.2.23. Free PDF: https://www.bmva-archive.org.uk/bmvc/1988/avc-88-023.pdf . Shi & Tomasi (1994), "Good Features to Track," *CVPR*, DOI: 10.1109/CVPR.1994.323794. Förstner & Gülch (1987).

#### 2.2 Scale-space extrema and SIFT (full pipeline)
**Math.** (1) **DoG scale space** D=(G_{kσ}−G_σ)∗I≈(k−1)σ²∇²G∗I. (2) **Detection**: local extrema of D over the 3×3×3 space-scale neighborhood. (3) **Sub-pixel localization**: fit a 3D quadratic, x̂=−(∂²D/∂x²)⁻¹(∂D/∂x); reject low-contrast keypoints (Lowe discards those with |D(x̂)| < 0.03 for image values in [0,1]) and edge responses via the Hessian ratio tr(H)²/det(H) < (r+1)²/r with **r = 10**. In Lowe's own worked example these tests reduce 832 candidate extrema to 729 (after the contrast test) and then to 536 final keypoints (after the edge-ratio test). (4) **Orientation**: 36-bin gradient-orientation histogram; peaks ≥80% of max assign orientations. (5) **Descriptor**: 4×4 grid of 8-bin gradient histograms → 128-D vector, normalized, clamped at 0.2, renormalized.
**Why it works.** DoG approximates the scale-normalized LoG whose extrema are Lindeberg's scale-covariant blob detector; σ² normalization makes responses comparable across scale. The descriptor's spatial pooling gives robustness to small localization error and deformation.
**Sources.** Lowe (2004), "Distinctive Image Features from Scale-Invariant Keypoints," *IJCV* 60(2):91–110, DOI: 10.1023/B:VISI.0000029664.99615.94. Free PDF: https://www.cs.ubc.ca/~lowe/papers/ijcv04.pdf . Lindeberg (1998), "Feature Detection with Automatic Scale Selection," *IJCV* 30(2):79–116, DOI: 10.1023/A:1008045108935, PDF: https://people.kth.se/~tony/papers/cvap198.pdf . VLFeat SIFT tutorial: https://www.vlfeat.org/overview/sift.html and API: https://www.vlfeat.org/api/sift.html

#### 2.3 SURF (integral images, Hessian detection)
**Math.** **Integral image** ii(x,y)=Σ_{x'≤x,y'≤y} I gives any box sum in 4 lookups. SURF detects blobs at maxima of **det(H_approx)=D_xxD_yy−(0.9 D_xy)²**, where D_** are box-filter approximations of second Gaussian derivatives via integral images. Scale space upscales filters (not images). Descriptor: Haar-wavelet responses in 4×4 subregions → 64-D vector.
**Why it works.** Box filters + integral images make the Hessian scale space nearly free; det(H) is a stable blob measure.
**Sources.** Bay, Tuytelaars, Van Gool (2006), "SURF: Speeded Up Robust Features," *ECCV* LNCS 3951:404–417, DOI: 10.1007/11744023_32. Journal: Bay et al. (2008), *CVIU* 110(3):346–359, DOI: 10.1016/j.cviu.2007.09.014. Viola & Jones (2001) — integral images in vision.

#### 2.4 FAST corner detection
**Math.** Examine 16 pixels on a Bresenham circle (radius 3) around p; corner if ≥ n contiguous pixels are all brighter than I_p+t or darker than I_p−t (n=9 for FAST-9). A **decision tree** learned by ID3 (maximizing information gain over the ternary state of each position) gives an optimal early-rejection test.
**Why it works.** The segment test is a cheap surrogate for "intensity varies in many directions"; the learned tree tests the most discriminative pixels first.
**Sources.** Rosten & Drummond (2006), "Machine Learning for High-Speed Corner Detection," *ECCV* LNCS 3951:430–443, DOI: 10.1007/11744023_34. Rosten, Porter, Drummond (2010), "Faster and Better," *IEEE PAMI* 32(1):105–119, DOI: 10.1109/TPAMI.2008.275.

#### 2.5 Binary descriptors: BRIEF, ORB, BRISK, FREAK
**Math.** **BRIEF**: bit i=1 if I(a_i)<I(b_i) else 0, over a fixed random set of test-point pairs in a smoothed patch; similarity by **Hamming distance** (XOR + popcount). **ORB** = oriented FAST + rotated BRIEF: orientation via intensity centroid θ=atan2(m_01,m_10) (moments m_pq=Σ x^p y^q I), steers the pattern by θ, learns a decorrelated high-variance test set ("rBRIEF"). **BRISK**: concentric sampling pattern, orientation from long-distance pairs. **FREAK**: retinal (foveal) sampling pattern with coarse-to-fine bit ordering.
**Why it works.** Intensity-comparison bits are illumination-robust and near-free; Hamming distance is one instruction. Learning/decorrelating tests maximizes descriptor entropy.
**Sources.** Calonder, Lepetit, Strecha, Fua (2010), "BRIEF," *ECCV* LNCS 6314:778–792, DOI: 10.1007/978-3-642-15561-1_56, EPFL PDF: https://infoscience.epfl.ch/entities/publication/6206c1ef-8c33-43ef-ab5a-3221892fd43f . Rublee, Rabaud, Konolige, Bradski (2011), "ORB," *ICCV* 2564–2571, DOI: 10.1109/ICCV.2011.6126544. Leutenegger, Chli, Siegwart (2011), "BRISK," *ICCV*, DOI: 10.1109/ICCV.2011.6126542. Alahi, Ortiz, Vandergheynst (2012), "FREAK," *CVPR*, DOI: 10.1109/CVPR.2012.6247715.

#### 2.6 Feature matching theory (distance metrics, ratio test, RANSAC)
**Math.** Nearest neighbor in descriptor space (L² for float, Hamming for binary). **Lowe's ratio test**: accept a match only if d₁/d₂ < 0.8 (nearest / second-nearest distance). Lowe (2004) justifies this threshold empirically: "we reject all matches in which the distance ratio is greater than 0.8, which eliminates 90% of the false matches while discarding less than 5% of the correct matches" (measured on a 40,000-keypoint database). **RANSAC**: sample a minimal set (e.g. 4 for homography), fit, count inliers; keep best. Iterations N=log(1−p)/log(1−(1−ε)^s) for success prob p, outlier fraction ε, sample size s.
**Why it works.** The ratio test exploits that correct matches are distinctly closer than the second-nearest. RANSAC is robust because one all-inlier minimal sample recovers the model regardless of outlier fraction, given enough trials.
**Sources.** Fischler & Bolles (1981), "Random Sample Consensus," *Comm. ACM* 24(6):381–395, DOI: 10.1145/358669.358692. Lowe (2004) IJCV (ratio test). Torr & Zisserman (2000), "MLESAC," *CVIU* 78(1):138–156; Chum & Matas (2005), "PROSAC," *CVPR*; Barath et al. (2020), "MAGSAC++," *CVPR*.

#### 2.7 Hessian-affine / MSER
**Math.** **Harris/Hessian-affine**: iterate detection with an affine-adapted second-moment matrix for affine covariance. **MSER**: threshold at all levels, track connected components; a region is maximally stable where its area is stationary w.r.t. threshold (q(t)=|dArea/dt|/Area locally minimal).
**Why it works.** Affine adaptation normalizes the patch to a canonical frame; MSER regions are invariant to monotonic intensity changes and covariant to affine geometry.
**Sources.** Matas, Chum, Urban, Pajdla (2002), "Robust Wide Baseline Stereo from MSER," *BMVC*, DOI: 10.5244/C.16.36. Mikolajczyk & Schmid (2004), "Scale & Affine Invariant Interest Point Detectors," *IJCV* 60(1):63–86, DOI: 10.1023/B:VISI.0000027790.02288.f2. Mikolajczyk et al. (2005), "A Comparison of Affine Region Detectors," *IJCV* 65(1/2):43–72. VLFeat MSER: https://www.vlfeat.org/overview/tut.html

### 3. Geometric Vision

#### 3.1 Camera models (pinhole, intrinsics/extrinsics, projective geometry)
**Math.** x̃=K[R|t]X̃, with intrinsics K=[[f_x,s,c_x],[0,f_y,c_y],[0,0,1]], extrinsics [R|t], image point x̃ up to scale. Homogeneous coordinates linearize projective transforms and represent points at infinity.
**Why it works.** Projective geometry is the natural language of perspective; the projection nonlinear in Cartesian coordinates becomes a single matrix multiply in homogeneous coordinates.
**Sources.** Hartley & Zisserman, *Multiple View Geometry in Computer Vision*, 2nd ed. (Cambridge, 2004), Ch. 6, 2–3, ISBN 0-521-54051-8. Sample chapters: https://www.robots.ox.ac.uk/~vgg/hzbook/ . Szeliski §2.1, §11.

#### 3.2 Lens distortion models
**Math.** Radial: x_d=x_u(1+k₁r²+k₂r⁴+k₃r⁶); tangential adds p₁,p₂. Undistortion inverts iteratively.
**Sources.** Zhang (2000) below; Brown (1971), "Close-Range Camera Calibration," *Photogrammetric Engineering* 37(8):855–866; Hartley & Zisserman §7.4.

#### 3.3 Camera calibration (Zhang's method)
**Math.** The method requires the camera to observe a planar pattern at "a few (at least two) different orientations"; three independent orientations solve the five intrinsics linearly (two suffice if skew is ignored). Each view gives a homography H=K[r₁ r₂ t]. Orthonormality of r₁,r₂ gives h₁ᵀBh₂=0 and h₁ᵀBh₁=h₂ᵀBh₂ with B=K⁻ᵀK⁻¹ (image of the absolute conic) — two linear constraints per homography on the 6 unknowns of symmetric B. Stack, solve by SVD, recover K by Cholesky, then extrinsics, then refine all (incl. distortion) by nonlinear ML (Levenberg–Marquardt) over reprojection error.
**Why it works.** Rotation-column orthonormality encodes metric constraints on intrinsics via the absolute conic; a plane at multiple orientations supplies enough constraints without knowing the motion.
**Sources.** Zhang (2000), "A Flexible New Technique for Camera Calibration," *IEEE PAMI* 22(11):1330–1334, DOI: 10.1109/34.888718. Free PDF: https://opi-lab.github.io/topics-computer-vision/pdfs/PAMI_2000_Zhang.pdf . MSR-TR-98-71 (fuller derivation). Burger (2016), "Zhang's Camera Calibration Algorithm: In-Depth Tutorial and Implementation."

#### 3.4 Homography estimation (DLT, normalization)
**Math.** For x'∼Hx, the cross product x'×Hx=0 gives two independent linear equations per correspondence in H's 9 entries; stack 4+ into Ah=0, solve for h as the right singular vector of A with smallest singular value (**DLT**). **Normalization** (Hartley): translate to centroid, scale so mean distance is √2 before DLT, then de-normalize — essential for conditioning.
**Why it works.** DLT converts a geometric constraint into a homogeneous linear system solved by SVD; normalization equalizes entry magnitudes in A, reducing noise sensitivity.
**Sources.** Hartley & Zisserman Ch. 4. Szeliski §8.1.

#### 3.5 Epipolar geometry, fundamental & essential matrices, eight-point algorithm
**Math.** Epipolar constraint x'ᵀFx=0, **F** rank 2, 7 DOF, maps x to its epipolar line l'=Fx. **Essential** E=K'ᵀFK factors as E=[t]_×R. **Eight-point**: each correspondence gives one linear equation in F's 9 entries; stack 8+, solve by SVD, enforce rank-2 by zeroing F's smallest singular value. **Normalized** eight-point (Hartley) applies the √2 normalization first.
**Why it works.** The epipolar constraint is bilinear in the two points, hence linear in F. Rank-2 enforcement is required because a valid F maps all epipolar lines through one epipole.
**Sources.** Longuet-Higgins (1981), "A computer algorithm for reconstructing a scene from two projections," *Nature* 293(5828):133–135, DOI: 10.1038/293133a0. Hartley (1997), "In Defense of the Eight-Point Algorithm," *IEEE PAMI* 19(6):580–593, DOI: 10.1109/34.601246. Author PDF: https://users.cecs.anu.edu.au/~hartley/Papers/fundamental/fundamental.pdf . Nistér (2004), "An Efficient Solution to the Five-Point Relative Pose Problem," *IEEE PAMI* 26(6):756–770. Hartley & Zisserman Ch. 9, 11.

#### 3.6 Stereo, triangulation, disparity, rectification
**Math.** After **rectification** (warp so epipolar lines are horizontal/aligned), correspondence is a 1D search; **disparity** d=x_L−x_R gives depth Z=fB/d. **Triangulation**: linear DLT solves AX=0 from x×PX=0; the optimal Hartley–Sturm method minimizes reprojection error.
**Sources.** Hartley & Zisserman Ch. 11–12. Scharstein & Szeliski (2002), "A Taxonomy and Evaluation of Dense Two-Frame Stereo Correspondence Algorithms," *IJCV* 47:7–42, DOI: 10.1023/A:1014573219977. Szeliski §12.

#### 3.7 Structure from motion / bundle adjustment
**Math.** Minimize total reprojection error min Σ_{ij} ρ(‖π(C_j,X_i)−x_{ij}‖²) over camera params C_j and points X_i with robust kernel ρ, by Levenberg–Marquardt exploiting the **sparse block (Schur-complement) structure** of the normal equations.
**Why it works.** It is the ML estimate under Gaussian reprojection noise; sparsity (each point seen by few cameras) makes a huge nonlinear least-squares problem tractable.
**Sources.** Triggs, McLauchlan, Hartley, Fitzgibbon (2000), "Bundle Adjustment — A Modern Synthesis," *Vision Algorithms* LNCS 1883:298–372, DOI: 10.1007/3-540-44480-7_21. Open PDF: https://hal.science/inria-00548290 . Hartley & Zisserman Ch. 18 + App. 6. Schönberger & Frahm (2016), "Structure-from-Motion Revisited," *CVPR* (COLMAP).

#### 3.8 Pose estimation (PnP)
**Math.** Given n 3D–2D correspondences and known K, recover [R|t]. **P3P** gives up to 4 solutions from 3 points (disambiguated by a 4th). **EPnP** writes the n points as weighted sums of 4 virtual control points, reducing to an O(n) linear system plus a small fixed optimization.
**Sources.** Lepetit, Moreno-Noguer, Fua (2009), "EPnP: An Accurate O(n) Solution to the PnP Problem," *IJCV* 81(2):155–166, DOI: 10.1007/s11263-008-0152-6. PDF: https://www.iri.upc.edu/files/scidoc/moreno_ijcv2009.pdf . Gao et al. (2003), "Complete Solution Classification for the P3P Problem," *IEEE PAMI* 25(8):930–943.

### 4. Segmentation & Classical Methods

#### 4.1 Thresholding (Otsu)
**Math.** Choose t maximizing **between-class variance** σ²_B(t)=ω₀ω₁(μ₀−μ₁)², with class probabilities ω and means μ from the histogram. Equivalently minimizes within-class variance since σ²_total=σ²_B+σ²_W is constant.
**Why it works.** A 1-D Fisher discriminant on the intensity histogram: the optimal threshold best separates the two intensity populations; computable in one pass over the bins.
**Sources.** Otsu (1979), "A Threshold Selection Method from Gray-Level Histograms," *IEEE Trans. SMC* 9(1):62–66, DOI: 10.1109/TSMC.1979.4310076. Free PDF: https://engineering.purdue.edu/kak/computervision/ECE661.08/OTSU_paper.pdf

#### 4.2 Watershed
**Math.** Treat gradient magnitude as topography; flood from regional minima; **watershed lines** form where floods meet. Marker-controlled watershed floods only from seeds to avoid over-segmentation.
**Sources.** Beucher & Meyer (1993), "The Morphological Approach to Segmentation: The Watershed Transformation." Vincent & Soille (1991), "Watersheds in Digital Spaces," *IEEE PAMI* 13(6):583–598, DOI: 10.1109/34.87344.

#### 4.3 Graph cuts & energy minimization (max-flow/min-cut)
**Math.** Model labeling as an MRF; minimize E(f)=Σ_p D_p(f_p)+Σ_{(p,q)} V_{pq}(f_p,f_q). For binary labels with submodular V (V(0,0)+V(1,1)≤V(0,1)+V(1,0)), the global minimum equals a **min-cut**, solved exactly via max-flow. Multi-label: **α-expansion**/**α-β swap** reach a strong local minimum with an approximation bound.
**Why it works.** Max-flow/min-cut duality turns MAP inference in these MRFs into a combinatorial optimization with a global optimum for the binary submodular case.
**Sources.** Boykov, Veksler, Zabih (2001), "Fast Approximate Energy Minimization via Graph Cuts," *IEEE PAMI* 23(11):1222–1239, DOI: 10.1109/34.969114. PDF: https://www.cs.cornell.edu/rdz/Papers/BVZ-pami01-final.pdf . Boykov & Kolmogorov (2004), *IEEE PAMI* 26(9):1124–1137. Kolmogorov & Zabih (2004), "What Energy Functions Can Be Minimized via Graph Cuts?" *IEEE PAMI* 26(2):147–159, PDF: https://www.cs.cornell.edu/~rdz/Papers/KZ-PAMI04.pdf

#### 4.4 GrabCut
**Math.** Extends Boykov–Jolly graph-cut segmentation with **Gaussian Mixture Models** for FG/BG color, iterating: assign GMM components → learn params → min-cut → repeat — needing only a bounding box.
**Sources.** Rother, Kolmogorov, Blake (2004), "GrabCut: Interactive Foreground Extraction Using Iterated Graph Cuts," *ACM TOG (SIGGRAPH)* 23(3):309–314, DOI: 10.1145/1015706.1015720.

#### 4.5 Active contours / snakes and level sets
**Math.** **Snakes**: evolve v(s) minimizing E=∫[½(α|v'|²+β|v''|²)+E_ext(v)]ds; Euler–Lagrange gives the update PDE. **Level sets** (Osher–Sethian): represent the curve as the zero level set of φ(x,t), evolving ∂_t φ+F|∇φ|=0; handles topology changes. **Chan–Vese**: minimizes a Mumford–Shah-type region energy (intensity homogeneity) rather than edges.
**Why it works.** Snakes cast segmentation as variational minimization; level sets avoid explicit parameterization/reconnection; Chan–Vese is robust to weak edges via region statistics.
**Sources.** Kass, Witkin, Terzopoulos (1988), "Snakes: Active Contour Models," *IJCV* 1(4):321–331, DOI: 10.1007/BF00133570, PDF: https://www.lpi.tel.uva.es/muitic/pim/docus/Snakes.pdf . Osher & Sethian (1988), "Fronts Propagating with Curvature-Dependent Speed," *J. Comp. Physics* 79(1):12–49, DOI: 10.1016/0021-9991(88)90002-2, PDF: https://www.math.hkust.edu.hk/~masyleung/NCTS/oshset88.pdf . Chan & Vese (2001), "Active Contours Without Edges," *IEEE TIP* 10(2):266–277, DOI: 10.1109/83.902291, PDF: https://www.math.ucla.edu/~lvese/PAPERS/IEEEIP2001.pdf . Caselles, Kimmel, Sapiro (1997), "Geodesic Active Contours," *IJCV* 22(1):61–79.

#### 4.6 Hough transform (lines, circles, generalized)
**Math.** Each edge point votes in a **parameter space** for all curves through it. Lines use (ρ,θ): ρ=x cosθ+y sinθ; accumulator peaks = lines. Circles vote in (a,b,r). The **Generalized Hough Transform** (Ballard) handles arbitrary shapes via an R-table indexed by gradient orientation.
**Why it works.** It converts hard global detection (which points are collinear/co-circular?) into local peak-finding, robust to occlusion/noise because each point votes independently.
**Sources.** Duda & Hart (1972), "Use of the Hough Transformation to Detect Lines and Curves in Pictures," *Comm. ACM* 15(1):11–15, DOI: 10.1145/361237.361242, PDF: https://dl.acm.org/doi/pdf/10.1145/361237.361242 . Ballard (1981), "Generalizing the Hough Transform to Detect Arbitrary Shapes," *Pattern Recognition* 13(2):111–122, DOI: 10.1016/0031-3203(81)90009-1.

#### 4.7 Contour detection and analysis
**Math.** Border following (Suzuki–Abe) extracts ordered contour lists; analysis uses moments (m_pq=Σ x^p y^q), Hu invariants, polygonal approximation (Douglas–Peucker), Fourier descriptors.
**Sources.** Suzuki & Abe (1985), "Topological Structural Analysis of Digitized Binary Images by Border Following," *CVGIP* 30(1):32–46, DOI: 10.1016/0734-189X(85)90016-7. Gonzalez & Woods Ch. 11.

#### 4.8 Mean shift & clustering-based segmentation
**Math.** Iteratively move each point to the weighted neighbor mean within bandwidth h: m(x)=[Σ x_i g(‖(x−x_i)/h‖²)]/[Σ g(...)]−x, climbing the KDE gradient to its mode. Pixels converging to the same mode (in joint spatial-range space) form a segment.
**Why it works.** A provably convergent mode-seeking procedure on the KDE; needs only a bandwidth, not a preset cluster count.
**Sources.** Comaniciu & Meer (2002), "Mean Shift: A Robust Approach Toward Feature Space Analysis," *IEEE PAMI* 24(5):603–619, DOI: 10.1109/34.1000236. Fukunaga & Hostetler (1975).

#### 4.9 Markov Random Fields for segmentation
**Math.** Model labels as an MRF with Gibbs distribution P(f)∝exp(−E(f)/T); by the **Hammersley–Clifford theorem** an MRF ⇔ a Gibbs field, so MAP inference = energy minimization (graph cuts, belief propagation, simulated annealing/ICM).
**Sources.** Geman & Geman (1984), "Stochastic Relaxation, Gibbs Distributions, and the Bayesian Restoration of Images," *IEEE PAMI* 6(6):721–741, DOI: 10.1109/TPAMI.1984.4767596. Li, *Markov Random Field Modeling in Image Analysis* (Springer). Prince, *Computer Vision: Models, Learning, and Inference*, Ch. 12.

### 5. Foundational / Cross-Cutting Math

#### 5.1 Linear algebra backbone (SVD, eigendecomposition, least squares)
**Math.** **SVD** A=UΣVᵀ underlies solving homogeneous systems Ah=0 (h = last column of V), total least squares, rank enforcement (F matrix), and PCA. **Eigendecomposition** appears in the structure tensor, Hessian, and PCA. **Least squares**: x=(AᵀA)⁻¹Aᵀb; homogeneous/constrained via SVD.
**Why it works.** SVD gives the best low-rank approximation (Eckart–Young) and the stablest solver for the rank-deficient homogeneous systems ubiquitous in geometry.
**Sources.** Golub & Van Loan, *Matrix Computations* (JHU Press). Strang, *Introduction to Linear Algebra*. Hartley & Zisserman App. 4–5.

#### 5.2 Optimization for vision (LM, Gauss-Newton, gradient descent, RANSAC)
**Math.** Nonlinear least squares min Σ‖r_i(x)‖²: **Gauss–Newton** x←x−(JᵀJ)⁻¹Jᵀr; **Levenberg–Marquardt** interpolates GN and gradient descent via damping (JᵀJ+λI)δ=−Jᵀr. Used in calibration, bundle adjustment, homography refinement. **RANSAC** = robust estimation by sampling (§2.6).
**Sources.** Nocedal & Wright, *Numerical Optimization* (Springer). Madsen, Nielsen, Tingleff, *Methods for Non-Linear Least Squares Problems* (free, DTU). Triggs et al. (2000).

#### 5.3 Scale-space theory as a unifying framework
**Math/why.** The Gaussian scale space is axiomatically forced by causality + homogeneity + isotropy; scale-normalized (γ-normalized) derivatives give scale-covariant detectors, unifying LoG/DoG blob detection, automatic scale selection, and SIFT.
**Sources.** Lindeberg, *Scale-Space Theory in Computer Vision* (Kluwer, 1994). Lindeberg (1998) IJCV, PDF: https://people.kth.se/~tony/papers/cvap198.pdf . Witkin (1983); Koenderink (1984). KTH scale-space page: https://www.kth.se/profile/tony/page/scale-space-theory

#### 5.4 Sampling theory and interpolation (bilinear, bicubic, Lanczos)
**Math.** Reconstruction convolves samples with an interpolation kernel: nearest (box), **bilinear** (tent), **bicubic** (piecewise-cubic, Keys a=−0.5 approximates sinc), **Lanczos** (windowed sinc L(x)=sinc(x)sinc(x/a)). Ideal reconstruction is sinc (perfect low-pass) but infinite-support with ringing; practical kernels trade sharpness/ringing/cost.
**Sources.** Keys (1981), "Cubic Convolution Interpolation for Digital Image Processing," *IEEE Trans. ASSP* 29(6):1153–1160, DOI: 10.1109/TASSP.1981.1163711. Szeliski §3.5.2; Gonzalez & Woods Ch. 2.

#### 5.5 Image pyramids (Gaussian, Laplacian)
**Math.** **Gaussian pyramid**: repeatedly smooth-and-downsample. **Laplacian pyramid**: L_l=G_l−expand(G_{l+1}) stores band-pass residuals; the original is exactly reconstructible by adding back expanded levels.
**Why it works.** The Laplacian pyramid is a complete, near-orthogonal band-pass decomposition (a wavelet precursor); pyramids enable coarse-to-fine search (flow, stereo) and multi-band blending.
**Sources.** Burt & Adelson (1983), "The Laplacian Pyramid as a Compact Image Code," *IEEE Trans. Communications* 31(4):532–540, DOI: 10.1109/TCOM.1983.1095851. Szeliski §3.5.

#### 5.6 Color space theory and color transforms
**Math.** CIE XYZ from spectral matching functions; linear RGB↔XYZ is a 3×3 matrix; nonlinear/gamma sRGB. Perceptual spaces: HSV/HSL (cylindrical), CIELAB (approx. perceptually uniform, ΔE distance); YCbCr (luma/chroma) for compression.
**Sources.** Wyszecki & Stiles, *Color Science* (Wiley). Gonzalez & Woods Ch. 6. Szeliski §2.3.2.

#### 5.7 Optical flow (Lucas-Kanade, Horn-Schunck, brightness constancy)
**Math.** **Brightness constancy** I(x,y,t)=I(x+u,y+v,t+1); first-order Taylor gives the **optical flow constraint** I_x u+I_y v+I_t=0 — one equation, two unknowns (aperture problem). **Lucas–Kanade** assumes constant flow in a window, solving by least squares [u v]ᵀ=(AᵀA)⁻¹Aᵀb, where AᵀA is exactly the structure tensor — solvable iff well-conditioned (corners). **Horn–Schunck** adds a global smoothness regularizer min ∫(I_xu+I_yv+I_t)²+λ(‖∇u‖²+‖∇v‖²) dx, solved iteratively.
**Why it works.** LK resolves the aperture problem locally by pooling window constraints (needs 2D texture); HS resolves it globally by propagating flow from textured to untextured regions.
**Sources.** Lucas & Kanade (1981), "An Iterative Image Registration Technique with an Application to Stereo Vision," *IJCAI* 674–679. Horn & Schunck (1981), "Determining Optical Flow," *Artificial Intelligence* 17(1–3):185–203, DOI: 10.1016/0004-3702(81)90024-2. Baker & Matthews (2004), "Lucas-Kanade 20 Years On: A Unifying Framework," *IJCV* 56(3):221–255. Bruhn, Weickert, Schnörr (2005), "Lucas/Kanade Meets Horn/Schunck," *IJCV* 61(3):211–231.

### Canonical Textbooks — which to use for what
- **Szeliski, *Computer Vision: Algorithms and Applications*, 2nd ed. (2022)** — free PDF at https://szeliski.org/Book/ . Best single spine.
- **Hartley & Zisserman, *Multiple View Geometry in Computer Vision*, 2nd ed. (2004)**, ISBN 0-521-54051-8 — the bible for all of §3. Sample chapters: https://www.robots.ox.ac.uk/~vgg/hzbook/
- **Gonzalez & Woods, *Digital Image Processing*, 4th ed. (2018)** — best for §1 (filtering, Fourier, morphology, compression, thresholding, contours).
- **Forsyth & Ponce, *Computer Vision: A Modern Approach*, 2nd ed. (2012)** — broad, well-balanced.
- **Prince, *Computer Vision: Models, Learning, and Inference* (2012)** — free PDF at http://www.computervisionmodels.com/ ; best for the probabilistic/graphical-model view.
- **Lindeberg, *Scale-Space Theory in Computer Vision* (1994)** — definitive for §1.6/§5.3.
- **Ma, Soatto, Košecká, Sastry, *An Invitation to 3-D Vision* (Springer, 2004)** — alternative rigorous geometry text.

### Primary documentation & reference implementations
- **OpenCV source**: https://github.com/opencv/opencv
- **scikit-image**: https://scikit-image.org/ (docs https://scikit-image.org/docs/stable/); van der Walt et al. (2014), *PeerJ* 2:e453, DOI: 10.7717/peerj.453
- **VLFeat** (math-heavy SIFT/MSER docs): https://www.vlfeat.org/ (tutorials https://www.vlfeat.org/overview/tut.html)
- **IPOL — Image Processing On Line** (peer-reviewed algorithms with exact math + reference C source): https://www.ipol.im/

### University course materials with rigorous notes
- **Stanford CS231A** (3D geometry) — notes: https://web.stanford.edu/class/cs231a/course_notes.html
- **Stanford CS131**: https://cs131.stanford.edu/
- **CMU 16-385 Computer Vision**: http://16385.courses.cs.cmu.edu/
- **University of Michigan EECS 442**: https://eecs442.github.io/
- **Middlebury** stereo/flow benchmarks & taxonomy: https://vision.middlebury.edu/

## Recommendations
1. **Start with the spine, in this order:** Read Szeliski §2–3 alongside Gonzalez & Woods Ch. 3–4 to lock down convolution, the Fourier/convolution theorem, and sampling. Implement 2D convolution, a separable Gaussian, and a DFT-based filter from scratch.
2. **Then take one vertical slice end-to-end:** edges. Derive the Canny criteria from the 1986 paper, implement gradient → NMS → hysteresis, and compare LoG/DoG.
3. **Do scale-space as a unit** (Witkin → Koenderink → Lindeberg 1998), then implement a DoG pyramid and SIFT keypoints — this unlocks SIFT, SURF, blob detection, and pyramids at once.
4. **For geometry, commit to Hartley & Zisserman** and implement, in sequence: DLT homography (with normalization) → normalized eight-point F → Zhang calibration → PnP → two-view triangulation.
5. **For segmentation/energy methods, learn the MRF↔Gibbs↔graph-cut chain once** (Geman & Geman → Boykov-Veksler-Zabih → GrabCut), and separately the variational chain (snakes → level sets → Chan-Vese → ROF/TV). Otsu and Hough are quick warm-ups.
6. **Always read the original paper, then check a reference implementation** (VLFeat for features, IPOL for filtering/denoising, scikit-image for general algorithms, OpenCV source for production detail).

**Thresholds that should change your plan:** if you can derive the structure tensor and explain why its eigenvalues classify flat/edge/corner, you're ready for SIFT/optical flow. If you can implement the normalized eight-point algorithm and explain why normalization matters numerically, you're ready for calibration and SfM. If a topic's original paper reads easily, skip the textbook chapter; if not, use the textbook pointer above.

## Caveats
- **Patents/licensing:** SIFT and SURF were patented. SIFT's US Patent 6,711,293 (assignee: The University of British Columbia; inventor David G. Lowe), with priority/filing date March 6, 2000, expired March 6, 2020 — Google Patents lists its status as "Expired - Lifetime." Consequently SIFT was moved out of the nonfree `opencv_contrib/xfeatures2d` module into the main `features2d` module as of OpenCV 4.4.0 / 3.4.11. ORB/BRISK/FREAK were designed partly as free alternatives. Verify current status before commercial use.
- **A few primary papers are paywalled or lack a free author PDF** (Longuet-Higgins 1981 *Nature*; Comaniciu-Meer 2002; ROF 1992; DCT 1974). The DOIs given are authoritative; reputable university-hosted copies exist for most.
- **Citation drift:** the same paper is often cited with slightly varying pages/year (Horn-Schunck AI journal vs. MIT AI Memo; Lucas-Kanade IJCAI vs. DARPA IUW; Hartley & Zisserman 2003 reprint vs. 2004 2nd ed.). Verify against the DOI when precision matters.
- **Textbook editions matter:** chapter numbers cited are for the stated editions (G&W 4th, H&Z 2nd, Szeliski 2nd).
- This library is deliberately **classical** (pre-deep-learning); many tasks now have learned counterparts, but the classical math remains the foundation and is often still competitive where data/compute/interpretability constraints apply.