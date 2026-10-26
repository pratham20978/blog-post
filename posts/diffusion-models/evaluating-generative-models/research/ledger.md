# Source ledger — evaluating-generative-models

Series `diffusion-models`, part 9. Sweep run 2026-10-21. Tier L2, so the floor is 4 peer-reviewed or
standard sources carrying an identifier, across 3 scholarly databases (Google Scholar, OpenAlex, arXiv,
Crossref; Semantic Scholar was tried and answered 429).

Every arXiv source was read in full text in the session scratchpad, from arXiv's own HTML rendering
(arxiv.org/html/<id>, math kept as LaTeX `alttext`), except Heusel et al. (the NeurIPS proceedings PDF
and the arXiv v6 PDF, both through `pdftotext -layout`, because ar5iv served "no content") and Karras et
al. (the CVF open-access PDF and the arXiv v2 PDF; the FD_DINOv2 comparison is only in arXiv v2's
Appendix A.5). Every claim row was checked against the paper's own text, table or equation, not an
abstract or a search snippet. Stein et al.'s Table 5 and Appendix A.2 were read as HTML tables.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Heusel, Ramsauer, Unterthiner, Nessler & Hochreiter, "GANs Trained by a Two Time-Scale Update Rule Converge to a Local Nash Equilibrium" (introduces FID) | NeurIPS (NIPS 2017) | 2017 | arXiv:1706.08500 | peer-reviewed | https://arxiv.org/abs/1706.08500 | 2026-10-21 |
| S2 | T1 | Borji, "Pros and Cons of GAN Evaluation Measures: New Developments" (survey) | Computer Vision and Image Understanding 215 | 2022 | 10.1016/j.cviu.2021.103329 | peer-reviewed | https://arxiv.org/abs/2103.09396 | 2026-10-21 |
| S3 | T1 | Sajjadi, Bachem, Lucic, Bousquet & Gelly, "Assessing Generative Models via Precision and Recall" | NeurIPS 2018 | 2018 | arXiv:1806.00035 | peer-reviewed | https://arxiv.org/abs/1806.00035 | 2026-10-21 |
| S4 | T1 | Kynkäänniemi, Karras, Laine, Lehtinen & Aila, "Improved Precision and Recall Metric for Assessing Generative Models" | NeurIPS 2019 | 2019 | arXiv:1904.06991 | peer-reviewed | https://arxiv.org/abs/1904.06991 | 2026-10-21 |
| S5 | T1 | Naeem, Oh, Uh, Choi & Yoo, "Reliable Fidelity and Diversity Metrics for Generative Models" | ICML 2020 (PMLR 119) | 2020 | arXiv:2002.09797 | peer-reviewed | https://proceedings.mlr.press/v119/naeem20a.html | 2026-10-21 |
| S6 | T1 | Bińkowski, Sutherland, Arbel & Gretton, "Demystifying MMD GANs" (introduces KID) | ICLR 2018 | 2018 | arXiv:1801.01401 | peer-reviewed | https://arxiv.org/abs/1801.01401 | 2026-10-21 |
| S7 | T1 | Chong & Forsyth, "Effectively Unbiased FID and Inception Score and Where to Find Them" | CVPR 2020 | 2020 | 10.1109/CVPR42600.2020.00611 | peer-reviewed | https://arxiv.org/abs/1911.07023 | 2026-10-21 |
| S8 | T1 | Parmar, Zhang & Zhu, "On Aliased Resizing and Surprising Subtleties in GAN Evaluation" (clean-fid) | CVPR 2022 | 2022 | 10.1109/CVPR52688.2022.01112 | peer-reviewed | https://arxiv.org/abs/2104.11222 | 2026-10-21 |
| S9 | T1 | Kynkäänniemi, Karras, Aittala, Aila & Lehtinen, "The Role of ImageNet Classes in Fréchet Inception Distance" | ICLR 2023 | 2023 | arXiv:2203.06026 | peer-reviewed | https://arxiv.org/abs/2203.06026 | 2026-10-21 |
| S10 | T1 | Stein, Cresswell, Hosseinzadeh, Sui, Ross, Villecroze, Liu, Caterini, Taylor & Loaiza-Ganem, "Exposing flaws of generative model evaluation metrics and their unfair treatment of diffusion models" | NeurIPS 2023 | 2023 | arXiv:2306.04675 | peer-reviewed | https://arxiv.org/abs/2306.04675 | 2026-10-21 |
| S11 | T1 | Jayasumana, Ramalingam, Veit, Glasner, Chakrabarti & Kumar, "Rethinking FID: Towards a Better Evaluation Metric for Image Generation" (CMMD) | CVPR 2024 | 2024 | 10.1109/CVPR52733.2024.00889 | peer-reviewed | https://arxiv.org/abs/2401.09603 | 2026-10-21 |
| S12 | T1 | Karras, Aittala, Lehtinen, Hellsten, Aila & Laine, "Analyzing and Improving the Training Dynamics of Diffusion Models" (EDM2) | CVPR 2024 | 2024 | 10.1109/CVPR52733.2024.02282 | peer-reviewed | https://arxiv.org/abs/2312.02696 | 2026-10-21 |
| S13 | T1 | Dhariwal & Nichol, "Diffusion Models Beat GANs on Image Synthesis" (ADM) | NeurIPS 2021 | 2021 | arXiv:2105.05233 | peer-reviewed | https://arxiv.org/abs/2105.05233 | 2026-10-21 |
| S14 | T1 | Podell, English, Lacey, Blattmann, Dockhorn, Müller, Penna & Rombach, "SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis" | ICLR 2024 | 2024 | arXiv:2307.01952 | peer-reviewed | https://arxiv.org/abs/2307.01952 | 2026-10-21 |
| S15 | T1 | Kirstain, Polyak, Singer, Matiana, Penna & Levy, "Pick-a-Pic: An Open Dataset of User Preferences for Text-to-Image Generation" (PickScore) | NeurIPS 2023 | 2023 | arXiv:2305.01569 | peer-reviewed | https://arxiv.org/abs/2305.01569 | 2026-10-21 |
| S16 | T1 | Hessel, Holtzman, Forbes, Le Bras & Choi, "CLIPScore: A Reference-free Evaluation Metric for Image Captioning" | EMNLP 2021 | 2021 | 10.18653/v1/2021.emnlp-main.595 | peer-reviewed | https://aclanthology.org/2021.emnlp-main.595/ | 2026-10-21 |
| S17 | T3 | pytorch-fid v0.3.0, `src/pytorch_fid/fid_score.py` (the common PyTorch port of the reference FID code) | — | 2020 | v0.3.0 | source | https://github.com/mseitzer/pytorch-fid/blob/v0.3.0/src/pytorch_fid/fid_score.py | 2026-10-21 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | evaluation of generative models survey metrics FID | low-tier surveys only (a 2024 vision-GenAI preprint, two 2025–2026 book chapters, a 2019 GAN survey); no evaluation-specific review worth reading |
| 2 | 1 | OpenAlex | title.search "pros and cons of GAN evaluation measures", sort cited_by_count | Borji 2019 (CVIU, 961 citations) and Borji 2022 (CVIU, 341): the field's two reviews; read 2022 (S2) for its taxonomy and FID section |
| 3 | 1 | OpenAlex | title.search "evaluation generative models", type article, sort cited_by_count | off-topic (LLM and medical-chatbot evaluations); confirms no newer image-generation review outranks Borji |
| 4 | 1 | OpenAlex | title.search "fréchet inception distance", sort cited_by_count | Kynkäänniemi 2023 (ICLR, S9) as the FID-specific study; the rest apply FID in other fields |
| 5 | 1 | arXiv | abstract pages of 22 candidates found through Borji 2022's bibliography and the papers' own related work | licences and versions: Stein 2023, SDXL, GenEval and Borji 2022 are CC BY 4.0, Pick-a-Pic CC0, Jayasumana CC BY-NC-SA, the rest arXiv's non-exclusive licence; venue comments for NeurIPS 2019, ICML 2020, ICLR 2023, NeurIPS 2023 |
| 6 | 2 | arXiv | full text (arxiv.org/html) of S2–S11, S13–S15 | the mechanisms and numbers in the Claims table; Heusel and EDM2 HTML missing (ar5iv "no content") |
| 7 | 2 | NeurIPS proceedings | Heusel et al. 2017 PDF, and arXiv v6 PDF | FID's definition, the two-moment restriction, the 50,000-sample protocol and the six disturbances (Appendix A1) |
| 8 | 3 | arXiv | Karras et al. 2312.02696v2 PDF (CVF camera-ready lacks the appendix) | Appendix A.5: FD_DINOv2 against FID, optimal guidance 1.9 against 1.4, EMA 14% against 2% |
| 9 | 4 | arXiv | Stein et al. Table 5 and Appendix A.2 as HTML tables | human error rates and reported-versus-recomputed FIDs for the 11 ImageNet models |
| 10 | 1 | Crossref | bibliographic titles of S2, S7, S8, S11, S12, S16 | DOIs for the CVIU, CVPR and EMNLP versions |
| 11 | 1 | OpenAlex | locations of S3, S4, S5, S6, S9, S10, S13, S14, S15 | NeurIPS confirmed for S3, S10, S13, S15; ICLR for S6; S4, S5, S9, S14 only as arXiv there |
| 12 | 1 | PMLR, NeurIPS and ICLR proceedings | proceedings pages for S4, S5, S9, S14 | NeurIPS 2019 (S4), PMLR 119 (S5), ICLR 2023 virtual site (S9), ICLR 2024 proceedings (S14) |
| 13 | 1 | OpenAlex | forward chase: works citing Kynkäänniemi 2019 (W2937274663) with "precision recall" in the title | Park & Kim 2023 (ICCV), probabilistic precision and recall, a later fix for the same outlier sensitivity; OpenAlex counts only 296 citers, so the graph is incomplete; not used, Naeem 2020 makes the point |
| 14 | 1 | OpenAlex | forward chase: works citing Heusel 2017 (W2963981733) with "FID" or "Frechet distance" in the title | Chong & Forsyth 2020 (S7), Parmar et al.'s 2021 preprint of S8, conditional and compound FID variants (not used) |
| 15 | 1 | Semantic Scholar | citations of arXiv:1904.06991 | HTTP 429 for the session; nothing returned |
| 16 | 1 | Google Scholar | cited-by list of Kynkäänniemi 2019 | the cluster id resolved to a different entry ("Cited by 2"); results were information-retrieval precision/recall papers plus Simon et al. 2019 (ICML); not used |
| 17 | 4 | arXiv | Jayasumana et al. 2401.09603 full text | normality tests on COCO-30K Inception features, Fréchet distance blind to non-normal change (Table 2), CMMD |
| 18 | 5 | GitHub | pytorch-fid v0.3.0 `fid_score.py` | `calculate_frechet_distance`: SciPy `sqrtm` of the covariance product, a diagonal offset when singular, imaginary parts dropped (S17) |
| 19 | 5 | GitHub | bioinf-jku/TTUR README | recommends at least 10,000 samples but says the true FID is otherwise "underestimated", which conflicts with the positive bias in S6 and S7; not used |
| 20 | 5 | GitHub | GaParmar/clean-fid README | the resize and JPEG tables and the CLIP-FID and KID options; covered by S8, not cited separately |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | FID passes real and generated images through an ImageNet-trained Inception-v3, takes its last pooling layer as features, fits a mean and covariance to each set and reports the Fréchet (Wasserstein-2) distance between the two Gaussians: squared mean gap plus Tr(C1 + C2 − 2(C1 C2)^(1/2)) | S1 §5 eq. 6, App. A1; S9 §1 eq. 1 | — |
| L02 | Heusel et al. kept only the first two moments for practical reasons, and justified the Gaussian as the maximum-entropy distribution for a given mean and covariance | S1 App. A1 | — |
| L03 | The features are the 2,048-dimensional pool3 activations of an Inception-v3 trained to classify ImageNet's 1,000 classes | S6 §2.3; S9 §1; S11 §3.3 | the standard Inception-v3 instance |
| L04 | Heusel et al. computed FID from 50,000 generated images against the statistics of the whole training set; quoting FID at 50k samples became standard practice | S1 §5; S4 §2.1 | — |
| L05 | The Inception Score, FID's predecessor, never compares with real images; a model that memorises a small subset still scores high on it | S1 §5; S13 §2.2 | — |
| L07 | Two GANs with similar FIDs (32 and 29 on MNIST; 65 and 62 on CelebA) fail differently: one makes good images of only some digits, the other poorer images of all of them | S3 §1, Fig. 1 | MNIST and CelebA GANs |
| L08 | Improved precision is the share of generated samples inside the union of balls around real samples, each reaching its k-th nearest real neighbour; recall swaps the roles; features from VGG-16's second fully connected layer, k = 3, 50,000 samples | S4 §2 | — |
| L09 | StyleGAN on FFHQ: setup B (FID 16.9) and setup D (FID 16.7) look almost equal by FID, yet D's images are nearly all broken (low precision) and B's are good with less variety; FID weights variation heavily | S4 §3, Fig. 4 | StyleGAN, FFHQ, four truncation/training setups |
| L11 | Density counts how many real-sample balls hold each generated sample (divided by k, can exceed 1); coverage is the share of real samples whose own ball holds at least one generated sample; Naeem et al. use k = 5 with 10,000 samples each, where identical distributions give expected coverage 1 − 1/2^k, about 0.969 | S5 §3.2, §3.3 | — |
| L12 | k-NN precision and recall overestimate the manifold around outliers: one stray generated sample's large ball lets recall count real samples that no generated sample resembles | S5 §3.1 | — |
| L13 | For two identical 64-dimensional standard Gaussians, precision and recall came out 0.68 and 0.67 while density and coverage came out 1.06 and 0.97 | S5 §4.1.1 | N(0, I) in 64 dimensions |
| L15 | The FID estimator is biased (it can be positive but never negative when the true value is zero), and no unbiased estimator of FID exists | S6 §2.3, App. D.3 | — |
| L16 | KID is the squared maximum mean discrepancy between the feature sets with the cubic kernel (x·y/d + 1)^3; it assumes no parametric form, compares skewness as well as mean and variance, and has an unbiased estimator | S6 §2.3 | — |
| L17 | Between the CIFAR-10 training and test sets, FID was still falling from about 8.1 at n = 10,000, while KID sat at its true value of zero by n = 2,000; FIDs compare only at the same n | S6 §2.3, Fig. 1 | CIFAR-10 train against test |
| L18 | Even at equal n, FID's bias differs between model pairs: Bińkowski et al. give a 2,048-dimensional example where 50,000 samples reliably rank two models the wrong way | S6 §2.3, App. D.2 | constructed example |
| L19 | FID measured on N samples equals its infinite-sample value plus K/N plus smaller terms; K depends on the generator, so rankings depend on N, and fitting a line in 1/N and reading it at 1/N = 0 gives an effectively unbiased FID-infinity | S7 §3.1, §3.2, §4.1 | GAN experiments, CIFAR-10 and others |
| L20 | Practice for FD-infinity: evaluate at 15 sample counts from 5,000 to 50,000 and extrapolate the linear fit | S10 App. B.1 | Stein et al.'s implementation |
| L21 | FID resizes every image to 299 × 299 before Inception; the TensorFlow and PyTorch FID implementations use fixed-width bilinear filters that alias, while PIL adapts the filter to the scale | S8 §3, Fig. 2 | the implementations current in 2021–2022 |
| L22 | The same real FFHQ images resized two ways score FID 0.64 apart for PIL bilinear against PIL bicubic, 4.3 for the PyTorch or TensorFlow resize, 7.4 for no filtering at all | S8 §4.1, Table 1 | FFHQ 1024 → 299 |
| L23 | Saving FFHQ images as JPEG at PIL's default quality 75 gives FID 21 against the same images as PNG, while StyleGAN2 scores about 3 and recent methods differ by under 1 | S8 §3.2, Fig. 6 | FFHQ at 256 px |
| L24 | When the training images had been stored as JPEG-75, JPEG-compressing the generated images too improved FID from 4.00 to 3.48 | S8 §4.2, Fig. 8 | StyleGAN2 on LSUN Churches at 256 px |
| L25 | FID's pre-logit features sit one affine map from ImageNet's class logits, and Grad-CAM shows FID on FFHQ attending to ImageNet objects such as seat belts and bow ties rather than the faces | S9 §1, §2, Fig. 4 | FFHQ, StyleGAN2 samples |
| L26 | Resampling generated images to match the real set's ImageNet top-1 class histogram lowered FID by about 10% across datasets | S9 §3, Table 1 | several datasets, StyleGAN2-class models |
| L27 | Resampling generated images to match all "fringe" features lowered FID by 63–72% on four datasets (FFHQ 5.30 to 1.78) with no visible improvement in the images, fooled KID as well, and moved FID on CLIP features by only 4–11% | S9 §3, Table 2, App. D | FFHQ, LSUN Cat, Car, Places |
| L28 | An ImageNet-pre-trained Projected FastGAN reached an FID comparable to StyleGAN2 on FFHQ while human evaluation rated it worse | S9 §4 | FFHQ |
| L29 | Stein et al. ran the largest human evaluation of generative models: 41 models on CIFAR-10, ImageNet, FFHQ and LSUN-Bedroom, over 1,000 paid participants and 207,000 real-or-fake judgements; a model's human error rate is the share of judgements participants got wrong | S10 §1, §3 | two-alternative forced choice, HYPE-style design |
| L30 | No common metric correlated strongly with human error rate; Inception-space metrics ranked GANs above diffusion models that people found more realistic; replacing Inception-v3 with DINOv2-ViT-L/14, a self-supervised network trained on a large and diverse dataset, restored the agreement | S10 abstract, §1, §4.2 | the four datasets above |
| L31 | ImageNet 256: StyleGAN-XL reported FID 2.26 (2.91 under Stein et al.'s protocol), human error rate 0.153; DiT-XL/2 reported 2.27 (2.80), human error rate 0.286 | S10 Table 5, App. A.2 | Stein et al.'s 50k-against-50k protocol for the recomputed values |
| L32 | Stein et al. also sampled DiT-XL/2 at guidance 4.0 instead of 1.5: FID 17.24 under their protocol, yet the highest human error rate of the 11 ImageNet models, 0.330, with visibly lower variety within each class | S10 App. A.2, Table 5, §5.1 | — |
| L33 | Within one encoder, FD, FD-infinity and KD rank models almost identically, so the encoder, not the distance, decides agreement with people; precision does not track human error rate reliably even in good encoders | S10 §4.2 | — |
| L34 | No published memorisation metric separated memorisation from underfitting or mode shrinkage, although models did memorise on CIFAR-10 | S10 abstract, §5.2 | — |
| L35 | The Inception features of COCO-30K, the usual reference set for text-to-image FID, fail Mardia's skewness, Mardia's kurtosis and Henze–Zirkler normality tests with p-values of essentially zero | S11 §3.3 | COCO 30K |
| L36 | A Fréchet distance computed under the normality assumption stayed at zero while non-normal distributions with the same mean and covariance moved apart; CMMD replaces Inception with CLIP features and the Fréchet distance with an unbiased RBF-kernel MMD | S11 §3.2, Table 2, §4 | — |
| L37 | EDM2 on ImageNet-512, S-sized models: with FD_DINOv2 (50,000 generated against all 1,281,167 real images) the best guidance was 1.9 against FID's 1.4, and the best EMA length 14% against 2%; each metric rated the other's optimum a poor choice | S12 arXiv v2 App. A.5, Fig. 14 | — |
| L38 | ADM's protocol: FID as the overall number, precision for fidelity and recall for diversity, the entire training set as the reference, and every model re-scored with one codebase because implementation details move FID | S13 §2.2 | — |
| L39 | Raising the classifier-guidance scale above 1 trades recall for precision, with FID best at an intermediate scale | S13 §4.4, Fig. 4 | ImageNet 128 |
| L42 | On 100 COCO captions and 9 models, model win rates from expert rankings correlated 0.917 with PickScore and −0.900 with FID | S15 §6, Fig. 6 | MS-COCO validation captions |
| L43 | FID never sees the prompt; Kirstain et al. attribute FID's negative correlation to higher guidance making vivid images people prefer that sit further from COCO's distribution | S15 §6 | their hypothesis |
| L44 | CLIPScore rates an image against text as 2.5 × max(cosine similarity of their CLIP embeddings, 0), with no reference images | S16 §3 | proposed for captioning; reused for text-to-image alignment |
| L46 | Borji's review: human inspection judges quality but not diversity, is subjective, and is hard to replicate across papers because protocols differ | S2 §2 | — |
| L47 | Stein et al. frame evaluation as three properties: fidelity (samples resemble the training data), diversity (they span the training distribution) and memorisation (whether they are reproductions of training samples) | S10 §1, Fig. 1 | — |
| L48 | Distance on raw pixels misreads images: two perceptually identical images can be far apart, as with a one-pixel shift, which is why metrics embed images with a pre-trained network | S5 §2 | Naeem et al., citing Theis et al. 2016 |
| L49 | FID remained the primary metric for ranking generative models when Kynkäänniemi et al. wrote in 2022–2023 | S9 abstract, §1 | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S10 | Figure 2 | What can't the Inception network see? / L29–L31 | it is the evidence: human error rate for 41 models laid out in FID order on four datasets, with the non-rising pattern the section argues from | CC BY 4.0 (arXiv record) | https://arxiv.org/html/2306.04675v2/summary.svg | send to route gate (selected: `source`) |
| F2 | S4 | Figure 4 | Which failures does one number hide? / L09 | StyleGAN setups A–D with FID, precision and recall | arXiv non-exclusive licence only | https://arxiv.org/abs/1904.06991 | do not reuse; the point is made in prose and with our own crescent-world figure |
| F3 | S5 | Figure 1 | precision against density, recall against coverage / L12 | the outlier scenarios | arXiv non-exclusive licence only | https://arxiv.org/abs/2002.09797 | do not reuse; our Figure 4 draws the mechanism on our own numbers |
| F4 | S8 | Figure 6 | Why don't FIDs compare across papers? / L23 | JPEG quality against FID | arXiv non-exclusive licence only | https://arxiv.org/abs/2104.11222 | do not reuse; numbers quoted in prose |
| F5 | S14 | Figure 12 | FID against CLIP score / L41 | SDXL's worse FID beside its user-study win | CC BY 4.0 (arXiv record) | https://arxiv.org/abs/2307.01952 | not selected: F1 carries the human-alignment point; two would repeat each other |
| F6 | S1 | Figure 3 | FID against six disturbances / L06 | shows FID working, not what it hides | arXiv non-exclusive licence only | https://arxiv.org/abs/1706.08500 | do not reuse |

## Open questions

- Whether the toy's copier result (FD and the k-NN metrics score a copier like a perfect generator)
  carries over to Inception space. Stein et al. (L34) find that no published memorisation metric
  separates memorisation from other failures; a later part of the series owns memorisation, so this
  post states the blind spot and defers the measurement.
- The TTUR README's "underestimated" wording conflicts with the positive bias shown by S6 and S7. The
  post uses the papers, not the README.
- Stein et al. say their protocol changes "do not affect any model rankings", yet their table puts
  StyleGAN-XL ahead of DiT-XL/2 by reported FID (2.26 against 2.27) and behind it by their recomputed
  FID (2.91 against 2.80). The reported values came from each paper's own code, so the post presents the
  two columns as published, states that the reported ones were computed by different codebases, and
  does not claim Stein et al.'s protocol reorders models in general.
- The toy computes every k-NN metric on raw pixels, where extra grain moves every sample away from all
  real neighbours; in a learned feature space the same grain matters less. The post labels toy numbers
  as mechanism, not scale.
