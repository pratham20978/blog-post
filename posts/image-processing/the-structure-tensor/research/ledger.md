# Source ledger — the-structure-tensor

Series `image-processing`, part 9. Sweep run 2026-10-12. Tier L4, so the floor is 10 peer-reviewed
or standard sources carrying an identifier, across 4 scholarly databases.

How each source was read is stated per row. Read in full: Harris & Stephens 1988 (BMVA archive),
Lucas & Kanade 1981 (IJCAI proceedings PDF), Tomasi & Kanade 1991 (the technical report on
Birchfield's KLT page, over plain http), Shi & Tomasi 1994 (Tomasi's Duke page), Förstner &
Gülch 1987 (a scan on the Bonn photogrammetry group's page, read through OCR and checked against
the page images for every sentence used), Bouguet's report (Stanford course copy), Baker & Matthews
2004 (the CMU technical-report version marked "to appear in IJCV"), Barron, Fleet & Beauchemin
1994 (Fleet's Toronto copy), Bruhn, Weickert & Schnörr 2005 (Saarland copy), Schmid, Mohr &
Bauckhage 2000 (a Clemson course copy), Mikolajczyk & Schmid 2004 (Oxford VGG copy), Tuytelaars &
Mikolajczyk 2008 (an RWTH course copy; the post links the DOI), Sánchez, Monzón & Salgado 2018
(IPOL, open). Used **only for what their abstracts state** (OpenAlex record, venue and pages
checked against Crossref): Kenney, Zuliani & Manjunath 2005; Zuliani, Kenney & Manjunath 2004;
Bigün, Granlund & Wiklund 1991; Simoncelli, Adelson & Heeger 1991.

Library behaviour was read at pinned commits: OpenCV `802cf95aa3d4` (the commit Parts 5–8
pinned): `modules/imgproc/src/corner.cpp`, `corner.hpp`, `featureselect.cpp`,
`spatialgradient.cpp`, `modules/imgproc/include/opencv2/imgproc.hpp`,
`modules/video/src/lkpyramid.cpp`, `lkpyramid.simd.hpp`,
`modules/video/include/opencv2/video/tracking.hpp`, `hal/carotene/hal/tegra_hal.hpp`,
`hal/riscv-rvv/include/imgproc.hpp`, `hal/ipp/include/ipp_hal_imgproc.hpp`,
`hal/fastcv/include/fastcv_hal_imgproc.hpp`, `doc/opencv.bib`; OpenCV tag `4.10.0`: `corner.cpp`,
`featureselect.cpp`, `lkpyramid.cpp`; scikit-image `b700edc8005e` (the commit Parts 5–8 pinned):
`src/_skimage2/feature/corner.py`, `feature/util.py`, `filters/_gaussian.py`,
`registration/_optical_flow.py`. MATLAB behaviour is from MathWorks' documentation pages for
`detectHarrisFeatures`, `detectMinEigenFeatures` and `opticalFlowLK`, release R2026b. Nothing was
executed against an image. The only code run was plain Python (`math` only) reproducing the post's
hand-worked numbers: Sobel and Harris & Stephens' (−1, 0, 1) derivative on the shared patch under
reflect-101 and replicate borders, the box and Gaussian window sums, eigenvalues, every score,
`goodFeaturesToTrack`'s selection rule transcribed from `featureselect.cpp`, one-step Lucas–Kanade
on frames moved by bilinear shifts, and the closed forms behind the plots.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Harris & Stephens, "A Combined Corner and Edge Detector" | Proc. Alvey Vision Conference 1988, pp. 147–151 | 1988 | 10.5244/C.2.23 | peer-reviewed | https://www.bmva-archive.org.uk/bmvc/1988/avc-88-023.pdf | 2026-10-12 |
| S02 | T1 | Shi & Tomasi, "Good Features to Track" | Proc. IEEE CVPR 1994, pp. 593–600 | 1994 | 10.1109/CVPR.1994.323794 | peer-reviewed | https://users.cs.duke.edu/~tomasi/papers/shi/shiCvpr94.pdf | 2026-10-12 |
| S03 | T1 | Lucas & Kanade, "An Iterative Image Registration Technique with an Application to Stereo Vision" | Proc. IJCAI 1981, vol. 2, pp. 674–679 | 1981 | OpenAlex W2118877769 | peer-reviewed | https://www.ijcai.org/Proceedings/81-2/Papers/017.pdf | 2026-10-12 |
| S04 | T1 | Tomasi & Kanade, "Detection and Tracking of Point Features" (technical report) | Carnegie Mellon University | 1991 | CMU-CS-91-132 | preprint | http://cecas.clemson.edu/~stb/klt/tomasi-kanade-techreport-1991.pdf | 2026-10-12 |
| S05 | T1 | Förstner & Gülch, "A Fast Operator for Detection and Precise Location of Distinct Points, Corners and Centres of Circular Features" | ISPRS Intercommission Conference on Fast Processing of Photogrammetric Data, Interlaken, pp. 281–305 | 1987 | proceedings pp. 281–305; no DOI or registry ID found | peer-reviewed | https://www.ipb.uni-bonn.de/pdfs/Forstner1987Fast.pdf | 2026-10-12 |
| S06 | T2 | Bouguet, "Pyramidal Implementation of the Lucas Kanade Feature Tracker: Description of the Algorithm" | Intel Corporation, Microprocessor Research Labs (undated; OpenCV's bibliography gives 2001) | 2001 | — | official-docs | http://robots.stanford.edu/cs223b04/algo_tracking.pdf | 2026-10-12 |
| S07 | T1 | Baker & Matthews, "Lucas-Kanade 20 Years On: A Unifying Framework" | International Journal of Computer Vision 56(3), pp. 221–255 | 2004 | 10.1023/B:VISI.0000011205.11775.fd | peer-reviewed | https://www.ri.cmu.edu/pub_files/pub3/baker_simon_2004_1/baker_simon_2004_1.pdf | 2026-10-12 |
| S08 | T1 | Barron, Fleet & Beauchemin, "Performance of Optical Flow Techniques" | International Journal of Computer Vision 12(1), pp. 43–77 | 1994 | 10.1007/BF01420984 | peer-reviewed | http://www.cs.toronto.edu/~fleet/research/Papers/ijcv-94.pdf | 2026-10-12 |
| S09 | T1 | Simoncelli, Adelson & Heeger, "Probability Distributions of Optical Flow" (abstract only) | Proc. IEEE CVPR 1991, pp. 310–315 | 1991 | 10.1109/CVPR.1991.139707 | peer-reviewed | https://doi.org/10.1109/CVPR.1991.139707 | 2026-10-12 |
| S10 | T1 | Bruhn, Weickert & Schnörr, "Lucas/Kanade Meets Horn/Schunck: Combining Local and Global Optic Flow Methods" | International Journal of Computer Vision 61(3), pp. 211–231 | 2005 | 10.1023/B:VISI.0000045324.43199.43 | peer-reviewed | https://www.mia.uni-saarland.de/Publications/bruhn-ijcv05c.pdf | 2026-10-12 |
| S11 | T1 | Bigün, Granlund & Wiklund, "Multidimensional Orientation Estimation with Applications to Texture Analysis and Optical Flow" (abstract only) | IEEE TPAMI 13(8), pp. 775–790 | 1991 | 10.1109/34.85668 | peer-reviewed | https://doi.org/10.1109/34.85668 | 2026-10-12 |
| S12 | T1 | Schmid, Mohr & Bauckhage, "Evaluation of Interest Point Detectors" | International Journal of Computer Vision 37(2), pp. 151–172 | 2000 | 10.1023/A:1008199403446 | peer-reviewed | http://cecas.clemson.edu/~stb/ece847/internal/classic_vision_papers/schmid_interestpoints_ijcv2000.pdf | 2026-10-12 |
| S13 | T1 | Mikolajczyk & Schmid, "Scale & Affine Invariant Interest Point Detectors" | International Journal of Computer Vision 60(1), pp. 63–86 | 2004 | 10.1023/B:VISI.0000027790.02288.f2 | peer-reviewed | https://www.robots.ox.ac.uk/~vgg/research/affine/det_eval_files/mikolajczyk_ijcv2004.pdf | 2026-10-12 |
| S14 | T1 | Tuytelaars & Mikolajczyk, "Local Invariant Feature Detectors: A Survey" (survey) | Foundations and Trends in Computer Graphics and Vision 3(3), pp. 177–280 | 2008 | 10.1561/0600000017 | peer-reviewed | https://doi.org/10.1561/0600000017 | 2026-10-12 |
| S15 | T1 | Sánchez, Monzón & Salgado, "An Analysis and Implementation of the Harris Corner Detector" | Image Processing On Line 8, pp. 305–328 | 2018 | 10.5201/ipol.2018.229 | peer-reviewed | https://www.ipol.im/pub/art/2018/229/article.pdf | 2026-10-12 |
| S16 | T1 | Kenney, Zuliani & Manjunath, "An Axiomatic Approach to Corner Detection" (abstract only) | Proc. IEEE CVPR 2005, vol. 1, pp. 191–197 | 2005 | 10.1109/CVPR.2005.68 | peer-reviewed | https://doi.org/10.1109/CVPR.2005.68 | 2026-10-12 |
| S17 | T1 | Zuliani, Kenney & Manjunath, "A Mathematical Comparison of Point Detectors" (abstract only) | Proc. CVPR Workshops 2004, p. 172 | 2004 | 10.1109/CVPR.2004.282 | peer-reviewed | https://doi.org/10.1109/CVPR.2004.282 | 2026-10-12 |
| S18 | T3 | OpenCV source at commit 802cf95: `corner.cpp`, `corner.hpp`, `featureselect.cpp`, `spatialgradient.cpp`, `imgproc.hpp`, `lkpyramid.cpp`, `lkpyramid.simd.hpp`, `tracking.hpp`, `hal/carotene/hal/tegra_hal.hpp`, `hal/riscv-rvv/include/imgproc.hpp`, `doc/opencv.bib` | — | 2026 | — | source | https://github.com/opencv/opencv/tree/802cf95aa3d42816995695bf68a86b3532f12760 | 2026-10-12 |
| S19 | T3 | OpenCV source at tag 4.10.0: `corner.cpp`, `featureselect.cpp`, `lkpyramid.cpp` | — | 2024 | — | source | https://github.com/opencv/opencv/tree/4.10.0/modules | 2026-10-12 |
| S20 | T3 | scikit-image source at commit b700edc: `src/_skimage2/feature/corner.py`, `feature/util.py`, `filters/_gaussian.py`, `registration/_optical_flow.py` | — | 2026 | — | source | https://github.com/scikit-image/scikit-image/tree/b700edc8005e4ee9e74fc83259f09e8df3213f15/src/_skimage2 | 2026-10-12 |
| S21 | T2 | MathWorks, "detectHarrisFeatures", Computer Vision Toolbox documentation, R2026b | — | 2026 | — | official-docs | https://www.mathworks.com/help/vision/ref/detectharrisfeatures.html | 2026-10-12 |
| S22 | T2 | MathWorks, "detectMinEigenFeatures", Computer Vision Toolbox documentation, R2026b | — | 2026 | — | official-docs | https://www.mathworks.com/help/vision/ref/detectmineigenfeatures.html | 2026-10-12 |
| S23 | T2 | MathWorks, "opticalFlowLK", Computer Vision Toolbox documentation, R2026b | — | 2026 | — | official-docs | https://www.mathworks.com/help/vision/ref/opticalflowlk.html | 2026-10-12 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | search "corner detection survey", sort cited_by_count | noise (graphene, CMS, IPCC): the full-text search is unusable here, as in Parts 6–8 |
| 2 | 1 | OpenAlex | search "local invariant feature detectors survey"; "structure tensor review" | noise again; switched to title.search |
| 3 | 1 | OpenAlex | title.search "local invariant feature detectors" | Tuytelaars & Mikolajczyk, FnT CGV 2008 (1,186 cites): the survey, used for the map and the 0.04 convention |
| 4 | 1 | OpenAlex | title.search "interest point detectors evaluation" | Schmid, Mohr & Bauckhage, IJCV 2000 (1,484 cites): repeatability of Harris variants |
| 5 | 1 | OpenAlex | title.search "corner detection survey" | only low-cited regional surveys (2005–2019); none used |
| 6 | 1 | OpenAlex | title.search "structure tensor" | noise plus Knutsson et al. SCIA 2011; no survey of the tensor itself |
| 7 | 1 | OpenAlex | title.search "optical flow survey" | Fortun, Bouthemy & Kervrann, CVIU 2015 (431 cites); HAL copy behind Anubis, not read, not cited |
| 8 | 1 | OpenAlex | title.search for each central paper | Harris 1988 W2111308925 (12,399 cites), Shi & Tomasi W2130103520, Lucas & Kanade W2118877769, Baker & Matthews, Barron et al., Simoncelli et al., Bigün 1987 and 1991, Kass & Witkin, Rao & Schunck, Noble; Förstner & Gülch 1987 not indexed |
| 9 | 1 | OpenAlex | filter cites:W2111308925, title "corner detector" | forward chase: Sánchez et al. IPOL 2018 (analysis of Harris, compares OpenCV), Tissainayagam & Suter 2004 |
| 10 | 1 | OpenAlex | filter cites:W2111308925, title "structure tensor" | Brox et al. 2006 (nonlinear structure tensors), Köthe 2003, Bigün 2004; not needed for the post's claims |
| 11 | 1 | OpenAlex | filter cites:W2130103520, title "corner" | Rosten & Drummond (FAST, not tensor-based), Kenney et al. CVPR 2005 (axioms), IPOL 2018 |
| 12 | 1 | OpenAlex | filter cites:W2111308925, title "Harris" | applications (3-D meshes, event cameras) and IPOL 2018; nothing corrective |
| 13 | 1 | OpenAlex | filter cites:W2118877769, title "Lucas" | forward chase: Baker & Matthews 2004, Bruhn, Weickert & Schnörr 2005 |
| 14 | 4 | OpenAlex | filter cites:W2118877769, title "aperture" | nothing central (event cameras, radar) |
| 15 | 1 | OpenAlex | filter cites:W2118877769, title "structure tensor" | Brox 2006, Bigün 2004, "The Minors of the Structure Tensor" 2000 |
| 16 | 5 | OpenAlex | filter cites:W2130103520, title "tracking" | Bouguet's pyramidal LK report (1,535 cites) |
| 17 | 4 | OpenAlex | title.search "determining optical flow"; "mathematical comparison of point detectors"; "scale & affine invariant interest point detectors"; "Lucas/Kanade meets Horn/Schunck" | Horn & Schunck 1981 (Elsevier, no abstract), Zuliani et al. 2004, Mikolajczyk & Schmid 2004, Bruhn et al. 2005 |
| 18 | 4 | OpenAlex | abstracts of W1977241131, W1545934923, W2102586630, W2163205713, W2152231592 | Bigün 1991 and 1987, Kenney 2005 (only Shi–Tomasi meets four axioms), Zuliani 2004 (equivalent up to a matrix norm), Simoncelli 1991; Elsevier abstracts withheld for Kass & Witkin, Rao & Schunck, Noble, Horn & Schunck |
| 19 | 1 | Crossref | 13 DOIs (S01, S02, S07–S17) | every venue, year and page range confirmed; Harris & Stephens paginated 23.1–23.6 by BMVA, printed 147–151; the survey issued 2008 |
| 20 | 1 | Semantic Scholar | search for Förstner & Gülch 1987 | HTTP 429, twice |
| 21 | 1 | Semantic Scholar | citations of DOI:10.1109/CVPR.1994.323794 | answered: 100 most recent citing papers, 2026 applications, nothing corrective |
| 22 | 1 | arXiv | all:"structure tensor" AND all:corner | 5; Åström & Felsberg (ACCV 2014 workshops, posted 2026 as 2608.22314): gradient energy tensor as an alternative; not used |
| 23 | 1 | arXiv | all:"Lucas-Kanade" AND all:"aperture" | 3, unrelated |
| 24 | 1 | arXiv | ti:"Harris corner" | 5; HarrisZ+ 2021 and noisy-image variants; not used |
| 25 | 1 | Google Scholar | structure tensor corner detection optical flow survey | Brox et al. nonlinear structure tensors (375), adaptive structure tensors (132), a variational optic-flow survey (127); confirms no single survey of the tensor's three uses |
| 26 | 2 | Web | Förstner Gülch 1987 PDF | Bonn photogrammetry page hosts the scan (pdfs/Forstner1987Fast.pdf) |
| 27 | 2 | Web | Tuytelaars Mikolajczyk survey PDF; Schmid 2000 PDF; Zuliani 2004 PDF | RWTH course copy of the survey; Clemson copy of Schmid; UCSB copy of Zuliani redirects to HTML (not obtained) |
| 28 | 2 | Web | Shi & Tomasi CVPR 1994 PDF; Cornell report TR 93-1399 | Duke copy of the CVPR paper read; Cornell eCommons served an AWS WAF challenge |
| 29 | 5 | Web | MathWorks pages for detectHarrisFeatures, detectMinEigenFeatures, opticalFlowLK | read with WebFetch (curl gets a 0.4 kB redirect page) |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Moravec's detector shifts a binary rectangular window by (1,0), (1,1), (0,1) and (−1,1) and takes local maxima of the smallest change above a threshold | S01 p. 148–149 | as Harris & Stephens describe it |
| L02 | Harris & Stephens replaced the discrete shifts by an analytic expansion E(x,y) = Ax² + 2Cxy + By² built from first gradients X = I ⊗ (−1,0,1), replaced the binary window by a Gaussian, and replaced the minimum by a measure of how E varies with direction | S01 p. 149 | — |
| L03 | The matrix describes the shape of the local autocorrelation at zero shift; its eigenvalues are proportional to that function's principal curvatures; flat, ridge (edge) and peak (corner) are the three cases, and a corner or an isolated point makes every shift costly | S01 p. 148–150 | — |
| L04 | The response is R = Det − k Tr²; positive in the corner region, negative on edges, small where flat; the paper gives no numerical value for k | S01 p. 150 | — |
| L05 | Raising contrast by a factor p raises both eigenvalues by p², so a point's corner or edge class must not change along rays from the origin of the eigenvalue plane | S01 p. 150 | — |
| L06 | Tomasi & Kanade derived feature selection from the tracker: the 2×2 matrix must be above the noise and well conditioned, which leads to accepting a window when min(λ1, λ2) exceeds a threshold | S04 ch. 4 | — |
| L07 | Two large eigenvalues can mean corners, salt-and-pepper texture or any other pattern the tracker can follow; a large and a small one mean a one-directional pattern | S04 ch. 4; S02 §4 | — |
| L08 | Tomasi & Kanade found their selected corner windows placed with the corner at the window's edge, the window filled by the brighter side, because that maximises the window's intensity variation | S04 ch. 5 | their 100-frame experiment |
| L09 | At one patch the motion constraint is one equation in two unknowns, so only one component of displacement is measurable (the aperture problem); no features were selected along straight edges, whose smaller eigenvalue is near zero | S04 ch. 3 and 5 | — |
| L10 | The linearised equation is exact only as the displacement goes to zero or where intensity is linear; Tomasi & Kanade iterate, resampling by bilinear interpolation | S04 ch. 3 | — |
| L11 | Shi & Tomasi accept a window when min(λ1, λ2) exceeds a threshold and argue the criterion is optimal by construction because the right features are the ones that make the tracker work best | S02 §1, §4 | — |
| L12 | A foreground twig crossing a background twig makes an intersection that exists only in the image; any selection criterion would pick it; Shi & Tomasi monitor an affine dissimilarity to catch such features | S02 §5 | — |
| L13 | For a horizontal edge only the vertical component of motion can be determined | S02 §4 | — |
| L14 | Lucas & Kanade's method registers images for stereo: it linearises for a small disparity, iterates in Newton–Raphson style, and in two dimensions accumulates weighted sums of five products, including the three gradient products | S03 §4 | — |
| L15 | Smoothing extends the range of disparities over which the linear approximation works, at the cost of suppressing small details; an object much smaller than the smoothing may vanish; a coarse-to-fine strategy follows | S03 §4.3 | — |
| L16 | Förstner & Gülch show the same normal-equation matrix arises for least-squares matching, for locating a corner as the intersection of edge elements, and for a gradient-weighted centre of gravity, so one window selection serves all of them | S05 §1.1.2 | — |
| L17 | The covariance of the located point is the noise variance times the inverse normal matrix; its error ellipse gives a weight w = det N / tr N and a roundness q = 4 det N / (tr N)², which is 1 for a circle and 0 on an ideal edge | S05 §1.1.2, eqs. 10–15 | Gaussian observations |
| L18 | The direction of the error ellipse, tan 2θ = 2N12 / (N11 − N22), is the edge's direction or the predominant direction of a texture | S05 eq. 13 | — |
| L19 | Their operator sums the gradient products with box windows (5×5 or 7×7 for matching), notes a Gaussian gives stable maxima at step edges, keeps windows with q above q_lim between 0.5 and 0.75 and w above a threshold, then suppresses non-maxima | S05 §1.2 | — |
| L20 | Bouguet: the matrix G is invertible only when the neighbourhood holds gradient information in both x and y; the solution assumes a small displacement and is iterated; derivatives use the Scharr operator; pyramids of 2 to 4 levels multiply the reachable displacement by 2^(Lm+1) − 1, 15 for Lm = 3 | S06 §2 | — |
| L21 | Bouguet's feature selection: the smaller eigenvalue of G at every pixel, a percentage of its maximum as threshold, 3×3 local maxima, a minimum distance; a 3×3 window is enough for selection and too small for tracking | S06 §3 | — |
| L22 | Lucas–Kanade is a Gauss–Newton minimisation of the sum of squared differences, with the Gauss–Newton approximation to the Hessian built from the steepest-descent images | S07 §2 | forwards-additive formulation |
| L23 | The gradient constraint has two unknown velocity components and one equation, so further constraints are needed | S08 §2 | — |
| L24 | Barron et al.'s Lucas–Kanade: weighted least squares over a 5×5 neighbourhood with weights 0.0625, 0.25, 0.375, 0.25, 0.0625 after a 1.5 pixel-frame Gaussian | S08 §2.1 | their implementation |
| L25 | With τ = 1.0: both eigenvalues at least τ gives full velocity, only the larger one gives a normal velocity, neither gives nothing; the smaller eigenvalue was more reliable than the sum | S08 §2.1 | — |
| L26 | A Bayesian version of the gradient least squares gives each flow estimate a covariance, representing its uncertainty | S09 abstract; S08 §2.1 | — |
| L27 | Local methods such as Lucas–Kanade are robust to noise but not dense: the system is singular in flat regions and near-singular where the smaller eigenvalue is close to zero, which can serve as a confidence measure | S10 §2 | — |
| L28 | Bigün's method uses the spatio-temporal structure tensor of (fx, fy, ft) | S10 §2, §3 | — |
| L29 | Bigün, Granlund & Wiklund estimate orientation by a least-squares axis fit that reduces to an eigenvalue problem computed in the spatial domain, with a certainty measure, applied to texture segmentation and to optical flow | S11 abstract | — |
| L30 | Schmid et al.'s Harris used the derivative mask [−2 −1 0 1 2], a Gaussian window of σ = 2, α = 0.06, 3×3 non-maximum suppression and a threshold of 1% of the maximum | S12 §2 | their implementation |
| L31 | The standard Harris repeated worst under a 45° rotation, which they attribute to non-isotropic discrete derivative filters; Gaussian derivatives (σ = 1) improved repeatability, and that variant did best in their comparison | S12 §3 | their image sequences |
| L32 | The scale-adapted second moment matrix is σD² g(σI) ∗ [Lx², LxLy; LxLy, Ly²], σI the integration scale and σD the differentiation scale | S13 §2.1 | — |
| L33 | Harris–Laplace finds Harris maxima at scales σn = 1.4ⁿσ0 with σI = σn and σD = 0.7σn, then keeps points where the Laplacian of Gaussian peaks over scale | S13 §2.2 | — |
| L34 | The survey calls the matrix the second moment or auto-correlation matrix and gives 0.04 as a typical value of Harris's constant | S14 §3.2 | — |
| L35 | Detected "corners" are points of two-dimensional variation that need not be 3-D corners; the detectors also fire on T-junctions, high-curvature points and texture | S14 §3.1, §3.2.1 | — |
| L36 | Harris, Noble and Shi–Tomasi are equivalent up to the choice of a matrix norm, under certain hypotheses | S17 abstract; S14 §2.3 | — |
| L37 | IPOL's analysis gives κ typically between 0.04 and 0.06 and lists the harmonic mean of the eigenvalues as a score that needs no parameter | S15 §2 | — |
| L38 | OpenCV's cornerHarris (3.4.1) uses Sobel derivatives and box filtering with no Gaussian; it was faster but repeated poorly under rotation, which the authors attribute to aliasing that Sobel and box filtering do not reduce | S15 §4.4 | their building sequence |
| L39 | Of five detectors, only Shi–Tomasi (and an equivalent 2-norm detector) satisfies all four of Kenney et al.'s axioms | S16 abstract | — |
| L40 | OpenCV's corner functions scale each derivative by 1/(2^(ksize−1) · blockSize · 255) for 8-bit input, form the three products, sum them with an unnormalised blockSize × blockSize box filter, all with BORDER_DEFAULT (reflect-101); the gradient step is documented as bit-identical to two Sobel passes | S18 corner.cpp, spatialgradient.cpp, imgproc.hpp | default border |
| L41 | calcHarris returns a·c − b² − k(a + c)²; calcMinEigenVal returns (a + c)/2 − sqrt(((a − c)/2)² + b²) | S18 corner.cpp | — |
| L42 | cornerHarris requires k; goodFeaturesToTrack defaults to blockSize 3, gradientSize 3, useHarrisDetector false, k = 0.04 | S18 imgproc.hpp | — |
| L43 | goodFeaturesToTrack: quality map from cornerMinEigenVal or cornerHarris at the default border; maximum over the image; values at or below qualityLevel × maximum set to 0; a 3×3 dilation; candidates scanned only for rows and columns 1 to size − 2, kept where non-zero and equal to the dilated value; sorted; minDistance enforced | S18 featureselect.cpp | — |
| L44 | Which code runs: cornerHarris goes to IPP only for aperture 3 or 5, 8-bit or float input and a constant or replicate border; cornerMinEigenVal's IPP call is commented out; UMat inputs go to OpenCL; goodFeaturesToTrack's OpenVX path is disabled | S18 corner.cpp, featureselect.cpp | IPP builds |
| L45 | calcOpticalFlowPyrLK defaults: winSize 21×21, maxLevel 3, 30 iterations or 0.01, minEigThreshold 1e-4, which is compared with the smaller eigenvalue of the spatial gradient matrix divided by the window's pixel count | S18 tracking.hpp | — |
| L46 | calcOpticalFlowPyrLK uses Scharr derivatives (3, 10, 3 by −1, 0, 1) with a reflect-101 border, carries the image ×32, scales the matrix by 2⁻²⁰, rejects a point at level 0 when the scaled minimum eigenvalue is under the threshold, and iterates with bilinear interpolation | S18 lkpyramid.cpp, lkpyramid.simd.hpp | — |
| L47 | A platform replacement for the LK level solver exists only in Carotene builds for 32-bit ARMv7; Carotene's Scharr replacement is compiled out | S18 tegra_hal.hpp | — |
| L48 | Release 4.10.0 has the same scale factor, box filter, response formulas, IPP guards, border-skipping scan and LK constants | S19 | — |
| L49 | scikit-image's structure_tensor converts 8-bit input to 0–1, takes SciPy Sobel derivatives, and weights the products with a Gaussian of σ = 1 truncated at 4σ, padding with zeros (mode constant) in both steps by default | S20 corner.py, util.py, _gaussian.py | default arguments |
| L50 | corner_harris defaults to k = 0.05 (method "k") or returns 2 det/(tr + eps) (method "eps", which its docstring calls Noble's measure); corner_shi_tomasi returns the smaller eigenvalue; corner_foerstner returns w = det/tr and q = 4 det/tr²; corner_peaks excludes a 1-pixel border by default | S20 corner.py | — |
| L51 | optical_flow_ilk solves a per-pixel Lucas–Kanade over a (2·radius + 1)² uniform window (radius 7) or a Gaussian, with np.gradient derivatives, 10 warps and a coarse-to-fine pyramid, and returns zero flow where the system's determinant is under 1e-14 | S20 _optical_flow.py | defaults |
| L52 | detectHarrisFeatures smooths the gradient products with a FilterSize 5 Gaussian (σ = FilterSize/3), keeps corners above MinQuality 0.01 of the maximum, and states no value of k | S21 | R2026b |
| L53 | detectMinEigenFeatures uses Shi and Tomasi's minimum-eigenvalue score with the same FilterSize and MinQuality defaults | S22 | R2026b |
| L54 | opticalFlowLK compares both eigenvalues with NoiseThreshold (default 0.0039): both above, it solves; one below, it uses a normalised gradient flow; both below, the flow is zero | S23 | R2026b |
| L55 | Tomasi & Kanade adopted Lucas & Kanade's method to track features through image streams: the match is the sum of squared differences between windows, linearised for small inter-frame motion and minimised Newton–Raphson style | S04 abstract, ch. 1 | small inter-frame motion |
| L56 | cornerEigenValsAndVecs stores (λ1, λ2, x1, y1, x2, y2) per pixel; the documentation calls the eigenvalues non-sorted, but eigen2x2 writes the larger one first | S18 imgproc.hpp, corner.cpp | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S01 | Figure 5 | Scores / L03, L04 | the classification plane with R's contours, the plane this post draws to scale | none stated; © The Plessey Company plc 1988 on the paper | https://www.bmva-archive.org.uk/bmvc/1988/avc-88-023.pdf | do not reuse; our Figure 5 is our own analysis with the patch's points, not a redraw |
| F2 | S15 | Figures 5–6 | Scores / L37 | Harris and harmonic-mean contours | CC BY-NC-SA (non-commercial) | https://www.ipol.im/pub/art/2018/229/article.pdf | do not reuse |

## Open questions

- Whether the 1987 Interlaken proceedings were refereed is not stated; the paper has no DOI and
  no OpenAlex record. It is recorded as peer-reviewed by venue type, and nothing in the post rests
  on it alone except Förstner's own definitions.
- Bouguet's report is undated; OpenCV's bibliography gives 2001 (key Bouguet00) and OpenAlex 1999.
  The post cites it without a year beyond OpenCV's.
- The survey (S14) says Harris & Stephens used Sobel derivatives; the paper itself uses (−1, 0, 1).
  The post follows the primary source.
- IPOL (S15) writes the harmonic mean as 2λ1λ2/(λ1 + λ2) in its table and as det/tr in its text;
  the post defines it itself.
- MATLAB's documentation states no value for Harris's k and no derivative filter for its corner
  detectors; the tooling map says "not documented".
- What `cv2.calcOpticalFlowPyrLK` returns on the 5×5 patch is not predicted: its default 21×21
  window is four times the patch.
