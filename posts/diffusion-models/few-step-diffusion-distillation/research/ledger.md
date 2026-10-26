# Source ledger — few-step-diffusion-distillation

Series `diffusion-models`, part 7. Sweep run 2026-10-16. Tier L3, so the floor is 7 peer-reviewed
or standard sources carrying an identifier, across 4 scholarly databases (Google Scholar, OpenAlex,
arXiv, Semantic Scholar, plus the ICLR, PMLR and ICLR-virtual proceedings listings for venues).

Every arXiv source was read in full text in the session scratchpad: from the arXiv PDF with
`pdftotext -layout` where the download was complete, otherwise from arXiv's own HTML rendering
(arxiv.org/html/<id>) or ar5iv, converted to text with the math kept as LaTeX `alttext`. Every claim
row was checked against the paper's own text, table, algorithm or equation, not against an abstract
or a search snippet. Model cards were read on huggingface.co. DBLP served its bot wall again, so
venues were confirmed through OpenAlex DOIs, the ICLR 2024/2025 proceedings indexes, the ICLR 2023
virtual-site listing, the PMLR v202 index, and arXiv comment fields, as the search log records.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang, "Diffusion Models: A Comprehensive Survey of Methods and Applications" | ACM Computing Surveys | 2023 | 10.1145/3626235; arXiv:2209.00796 | peer-reviewed | https://doi.org/10.1145/3626235 | 2026-10-16 |
| S02 | T1 | Ma, Zhang, Jia, Zhao, Ma, Ma, Liu, Zhang, Li & Zhou, "Efficient Diffusion Models: A Comprehensive Survey From Principles to Practices" | IEEE TPAMI 47(9):7506–7525 | 2025 | 10.1109/TPAMI.2025.3569700; arXiv:2410.11795 | peer-reviewed | https://doi.org/10.1109/TPAMI.2025.3569700 | 2026-10-16 |
| S03 | T1 | Fan, Wu & Wu, "A Survey on Pre-Trained Diffusion Model Distillations" | arXiv | 2025 | arXiv:2502.08364v2 | preprint | https://arxiv.org/abs/2502.08364 | 2026-10-16 |
| S04 | T1 | Karras, Aittala, Aila & Laine, "Elucidating the Design Space of Diffusion-Based Generative Models" (EDM) | NeurIPS 35 | 2022 | 10.52202/068431-1926; arXiv:2206.00364 | peer-reviewed | https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html | 2026-10-16 |
| S05 | T1 | Luhman & Luhman, "Knowledge Distillation in Iterative Generative Models for Improved Sampling Speed" | arXiv | 2021 | arXiv:2101.02388v1 | preprint | https://arxiv.org/abs/2101.02388 | 2026-10-16 |
| S06 | T1 | Salimans & Ho, "Progressive Distillation for Fast Sampling of Diffusion Models" | ICLR | 2022 | arXiv:2202.00512v2 | peer-reviewed | https://arxiv.org/abs/2202.00512 | 2026-10-16 |
| S07 | T1 | Meng, Rombach, Gao, Kingma, Ermon, Ho & Salimans, "On Distillation of Guided Diffusion Models" | CVPR | 2023 | 10.1109/CVPR52729.2023.01374; arXiv:2210.03142 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.01374 | 2026-10-16 |
| S08 | T1 | Song, Dhariwal, Chen & Sutskever, "Consistency Models" | ICML (PMLR 202) | 2023 | pmlr-v202-song23a; arXiv:2303.01469 | peer-reviewed | https://proceedings.mlr.press/v202/song23a.html | 2026-10-16 |
| S09 | T1 | Song & Dhariwal, "Improved Techniques for Training Consistency Models" (iCT) | ICLR | 2024 | ICLR 2024 hash 41bd71e7bf7f9fe68f1c936940fd06bd; arXiv:2310.14189 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2024/hash/41bd71e7bf7f9fe68f1c936940fd06bd-Abstract-Conference.html | 2026-10-16 |
| S10 | T1 | Lu & Song, "Simplifying, Stabilizing and Scaling Continuous-time Consistency Models" (sCM) | ICLR | 2025 | ICLR 2025 hash 7e9c2053258b1bdd32ff2654802cd594; arXiv:2410.11081 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2025/hash/7e9c2053258b1bdd32ff2654802cd594-Abstract-Conference.html | 2026-10-16 |
| S11 | T1 | Kim, Lai, Liao, Murata, Takida, Uesaka, He, Mitsufuji & Ermon, "Consistency Trajectory Models: Learning Probability Flow ODE Trajectory of Diffusion" (CTM) | ICLR | 2024 | ICLR 2024 hash c204d12afa0175285e5aac65188808b4; arXiv:2310.02279 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2024/hash/c204d12afa0175285e5aac65188808b4-Abstract-Conference.html | 2026-10-16 |
| S12 | T1 | Liu, Gong & Liu, "Flow Straight and Fast: Learning to Generate and Transfer Data with Rectified Flow" | ICLR | 2023 | arXiv:2209.03003 | peer-reviewed | https://arxiv.org/abs/2209.03003 | 2026-10-16 |
| S13 | T1 | Yin, Gharbi, Zhang, Shechtman, Durand, Freeman & Park, "One-step Diffusion with Distribution Matching Distillation" (DMD) | CVPR | 2024 | 10.1109/CVPR52733.2024.00632; arXiv:2311.18828 | peer-reviewed | https://doi.org/10.1109/CVPR52733.2024.00632 | 2026-10-16 |
| S14 | T1 | Yin, Gharbi, Park, Zhang, Shechtman, Durand & Freeman, "Improved Distribution Matching Distillation for Fast Image Synthesis" (DMD2) | NeurIPS 37 | 2024 | 10.52202/079017-1505; arXiv:2405.14867 | peer-reviewed | https://doi.org/10.52202/079017-1505 | 2026-10-16 |
| S15 | T1 | Sauer, Lorenz, Blattmann & Rombach, "Adversarial Diffusion Distillation" (ADD) | ECCV (LNCS) | 2024 | 10.1007/978-3-031-73016-0_6; arXiv:2311.17042 | peer-reviewed | https://doi.org/10.1007/978-3-031-73016-0_6 | 2026-10-16 |
| S16 | T1 | Frans, Hafner, Levine & Abbeel, "One Step Diffusion via Shortcut Models" | ICLR | 2025 | ICLR 2025 hash 559a0998fab1d19b80e7e43a5852401c; arXiv:2410.12557 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2025/hash/559a0998fab1d19b80e7e43a5852401c-Abstract-Conference.html | 2026-10-16 |
| S17 | T1 | Boffi, Albergo & Vanden-Eijnden, "How to build a consistency model: Learning flow maps via self-distillation" | NeurIPS 38 | 2025 | 10.52202/085713-1121; arXiv:2505.18825 | peer-reviewed | https://doi.org/10.52202/085713-1121 | 2026-10-16 |
| S18 | T1 | Geng, Deng, Bai, Kolter & He, "Mean Flows for One-step Generative Modeling" (MeanFlow) | NeurIPS 38 | 2025 | 10.52202/085713-2534; arXiv:2505.13447 | peer-reviewed | https://doi.org/10.52202/085713-2534 | 2026-10-16 |
| S19 | T1 | Sabour, Fidler & Kreis, "Align Your Flow: Scaling Continuous-Time Flow Map Distillation" | NeurIPS 38 | 2025 | 10.52202/085713-4900; arXiv:2506.14603 | peer-reviewed | https://doi.org/10.52202/085713-4900 | 2026-10-16 |
| S20 | T1 | Luo, Tan, Huang, Li & Zhao, "Latent Consistency Models: Synthesizing High-Resolution Images with Few-Step Inference" (LCM) | arXiv | 2023 | arXiv:2310.04378v1 | preprint | https://arxiv.org/abs/2310.04378 | 2026-10-16 |
| S21 | T1 | Vouitsis, Hosseinzadeh, Ross, Villecroze, Gorti, Cresswell & Loaiza-Ganem, "Inconsistencies In Consistency Models: Better ODE Solving Does Not Imply Better Samples" | NeurIPS 2024 ATTRIB workshop | 2024 | arXiv:2411.08954v2 | preprint | https://arxiv.org/abs/2411.08954 | 2026-10-16 |
| S22 | T1 | Zheng, Wang, Ma, Chen, Zhang, Balaji, Chen, Liu, Zhu & Zhang, "Large Scale Diffusion Distillation via Score-Regularized Continuous-Time Consistency" (rCM) | ICLR | 2026 | arXiv:2510.08431v3 | peer-reviewed | https://arxiv.org/abs/2510.08431 | 2026-10-16 |
| S23 | T2 | Stability AI, `stabilityai/sdxl-turbo` model card | Hugging Face | 2023 | — | official-docs | https://huggingface.co/stabilityai/sdxl-turbo | 2026-10-16 |
| S24 | T2 | Black Forest Labs, `black-forest-labs/FLUX.1-schnell` model card | Hugging Face | 2024 | — | official-docs | https://huggingface.co/black-forest-labs/FLUX.1-schnell | 2026-10-16 |
| S25 | T1 | Kynkäänniemi, Karras, Laine, Lehtinen & Aila, "Improved Precision and Recall Metric for Assessing Generative Models" | NeurIPS 32 | 2019 | arXiv:1904.06991 | peer-reviewed | https://arxiv.org/abs/1904.06991 | 2026-10-16 |

Nineteen peer-reviewed sources carry an identifier (S01, S02, S04, S06–S19, S22, S25). Four are preprints
and are labelled so in the post: Luhman & Luhman (S05, never published at a venue as far as OpenAlex
and Google Scholar show), Fan et al. (S03), LCM (S20) and Vouitsis et al. (S21, a non-archival
workshop paper). rCM (S22) carries "ICLR 2026" in its arXiv comment field; the ICLR 2026 proceedings
index was not checked. The ICLR papers without DOIs carry their proceedings hash or arXiv id.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex (full-text search) | diffusion model distillation survey; fast sampling diffusion models survey; efficient diffusion models survey | noise: AlphaFold 3, PRISMA, unrelated reviews; full-text search unusable, switched to title search |
| 2 | 1 | OpenAlex (title.search) | diffusion distillation survey | Luo 2023 (arXiv:2304.04262) and Fan, Wu & Wu 2025 (arXiv:2502.08364), both preprints |
| 3 | 1 | OpenAlex (title.search) | fast sampling diffusion survey; accelerating diffusion survey | nothing for images; two 2026 surveys of diffusion language-model inference, out of scope |
| 4 | 1 | OpenAlex (title.search) | few-step diffusion; one-step diffusion | applications plus DMD (CVPR 2024) and Trajectory Distribution Matching (ICCV 2025) |
| 5 | 1 | Google Scholar | survey diffusion model distillation few-step | Luo 2023 (66 cites), Ma et al. TPAMI 2025 (106), Shen et al. 2025, Song et al. AI Review 2024, ADD ECCV 2024 (1,187 cites) |
| 6 | 1 | Google Scholar | survey efficient diffusion models sampling acceleration | diffusion-LLM and cache-method surveys; no image distillation survey beyond #5 |
| 7 | 1 | OpenAlex (DOI lookup) | 10.1109/tpami.2025.3569700 | Ma et al. TPAMI 47(9), arXiv copy 2410.11795; its distillation section read in full |
| 8 | 1 | arXiv API (id_list) | 26 ids of the method papers | titles, authors, versions, comments; ICML/ICLR/NeurIPS/CVPR notes where authors added them |
| 9 | 1 | OpenAlex (title.search, per paper) | the 25 method and survey titles | DOIs and venues for Meng (CVPR 2023), DMD (CVPR 2024), DMD2 (NeurIPS 2024), ADD (ECCV 2024), LADD (SIGGRAPH Asia 2024), MeanFlow, flow-map self-distillation and Align Your Flow (NeurIPS 2025), Diff-Instruct (NeurIPS 2023), moment matching (NeurIPS 2024); the ICLR and ICML papers show only arXiv |
| 10 | 1 | ICLR proceedings index 2024, 2025 | titles of iCT, CTM, InstaFlow, sCM, ECT, shortcut models | all six listed with hashes; the 2022 and 2023 indexes do not exist on that site |
| 11 | 1 | ICLR 2023 virtual site | Flow Straight and Fast | listed: rectified flow is ICLR 2023 |
| 12 | 1 | PMLR v202 index | Consistency Models | listed as song23a (ICML 2023) |
| 13 | 1 | Semantic Scholar (citations API) | forward citations of Consistency Models (arXiv:2303.01469) | the newest 1,000 citers; influential ones include AlphaFlow (MeanFlow analysis), Improved Training Technique for Shortcut Models (NeurIPS 2025), Stabilizing Consistency Training |
| 14 | 1 | Semantic Scholar (citations API) | forward citations of progressive distillation (arXiv:2202.00512) | "paper not found" for the arXiv id, then 429 on the title search; chased forward through Google Scholar and OpenAlex instead |
| 15 | 1 | OpenAlex (filter cites:) | citers of PD (W4221159371) and CM (W4323076585) with title words diversity, collapse, inconsistency, bias, theory, failure | sparse graph for arXiv records; only exposure-bias and unrelated papers |
| 16 | 4 | arXiv API (title search) | "Inconsistencies in Consistency Models" | Vouitsis et al. 2024 (NeurIPS 2024 workshop): a consistency model that solves the ODE more accurately gives worse FID |
| 17 | 4 | arXiv API (title search) | "Improved Training Technique for Shortcut Models"; "score-regularized continuous-time consistency" | Nguyen et al. NeurIPS 2025 (accumulated guidance, frequency bias in shortcut models); rCM, ICLR 2026 (consistency models blur at scale; reverse-divergence distillation loses diversity) |
| 18 | 4 | Google Scholar | distilled diffusion models diversity loss mode collapse one-step | rCM (ICLR 2026), CrossDistill and Uncertainty DMD (2026 preprints, not used) |
| 19 | 2 | arXiv full text | progressive distillation, consistency models, iCT, sCM, CTM, DMD, DMD2, ADD, shortcut, flow-map self-distillation, MeanFlow, Align Your Flow, Meng, LCM, Luhman, rectified flow | read in full; claims below |
| 20 | 3 | arXiv full text | result tables: PD Table, CM Tables 1–2, iCT Tables 2–3, sCM Table 1, DMD Tables 1–2, DMD2 Tables 1, 3, shortcut Table 1 | the numbers below, each with its setup |
| 21 | 5 | Hugging Face | stabilityai/sdxl-turbo; black-forest-labs/FLUX.1-schnell model cards | ADD and latent ADD in shipped 1–4-step models; guidance disabled; stated limitations |

Databases queried for the literature: Google Scholar, OpenAlex, arXiv and Semantic Scholar (four),
plus three proceedings indexes for venue checks. DBLP was not tried this session after serving a bot
wall in every session since 2026-09-24 (see the series' earlier ledgers).

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | A survey sorts fast sampling into learning-free methods (SDE and ODE solvers) and learning-based ones, which include knowledge distillation | S01 §3 | survey taxonomy |
| L02 | A TPAMI survey divides distillation-based sampling into distribution-based, trajectory-based and GAN-based groups, and files Luhman, progressive distillation and Meng et al. under distribution-based | S02 §"Knowledge distillation" | survey taxonomy |
| L03 | A second survey divides distillation into fidelity (output) distillation, trajectory distillation and adversarial distillation, and files progressive distillation under fidelity distillation and shortcut models under trajectory distillation | S03 §1, Fig. 1 | preprint |
| L04 | Luhman & Luhman train a student to map a noise vector straight to the image a DDIM teacher produces from it, in one network call | S05 §3 | preprint |
| L05 | Luhman & Luhman's students were trained on 1.024 million teacher-generated pairs per dataset, reused over many epochs | S05 §3 | preprint |
| L06 | Building such a pair dataset means running the teacher at its full step count for every pair, so the cost grows with that step count | S06 §6; S13 §1 | — |
| L07 | In progressive distillation the student starts as a copy of the teacher, and its target makes one student DDIM step land where two teacher DDIM steps land; the student then becomes the next teacher and the step count halves | S06 §3, Alg. 2 | — |
| L08 | The distillation target is fully determined by the teacher and the noisy input, so the student can make a sharp prediction, whereas the ordinary denoising target averages over all clean images consistent with the input and is blurry | S06 §3 | — |
| L09 | Progressive distillation trains on noised training data, sampling the student's step uniformly from its grid | S06 Alg. 2 | — |
| L10 | Predicting ε breaks at zero signal-to-noise ratio, the regime one-step students live in; predicting x, v, or both, with truncated-SNR or SNR+1 weighting, is stable; ε prediction with truncated-SNR weighting diverged | S06 §4, Table 1 | — |
| L11 | Progressive distillation started CIFAR-10 at 8,192 teacher steps and the larger datasets at 1,024, trained 50,000 updates per halving (100,000 for 2 and 1 steps), and cost no more than training the original model to reach 4 steps | S06 §5.2 | — |
| L12 | On CIFAR-10 progressive distillation reaches FID 9.12, 4.51, 3.00 and 2.57 at 1, 2, 4 and 8 steps; quality holds to 4–8 steps and degrades faster at 2 and 1, while DDIM degrades sharply below 128 steps | S06 §5.2, Fig. 4, table in §6 | CIFAR-10, unconditional, its own teacher |
| L13 | A consistency model maps any point on a probability-flow ODE trajectory to the trajectory's origin, and its outputs agree for all points on one trajectory (self-consistency) | S08 §3 | — |
| L14 | The boundary condition f(x, ε) = x is built in with skip parameterisation f = c_skip(t) x + c_out(t) F, with c_skip(ε) = 1 and c_out(ε) = 0; the boundary condition is what rules out the trivial solution f ≡ 0 of the consistency loss | S08 §3, Eq. 5; §4 after Thm. 1 | — |
| L15 | Multistep consistency sampling alternates a consistency-model call with fresh noise injection at a chosen lower noise level | S08 Alg. 1 | — |
| L16 | Consistency distillation takes one numerical ODE step with the teacher from a noised data point at t_{n+1} to t_n and trains f(x_{n+1}) to match a target network's f at the result; the target network is an EMA of the online one | S08 §4, Alg. 2 | — |
| L17 | The best consistency-distillation settings on CIFAR-10 were the LPIPS metric, Heun's solver and N = 18 discretisation points; the target EMA rate was 0 on CIFAR-10 and 0.95 on ImageNet 64 and LSUN | S08 §6.1, App. C Table 3 | — |
| L18 | Consistency training needs no pretrained diffusion model, and is sensitive to N: small N converges faster to worse samples | S08 §5, §6.1 | — |
| L19 | On CIFAR-10, with both methods distilling the same EDM teacher, PD scores FID 8.34 at 1 step and 5.58 at 2, CD 3.55 and 2.93; knowledge distillation (Luhman) is listed at 9.36 for 1 step | S08 Table 1 | CIFAR-10, the CM paper's runs |
| L20 | On ImageNet 64, the same comparison gives PD 15.39 at 1 step (precision 0.59, recall 0.62) and 8.95 at 2; CD 6.20 (0.68, 0.63) and 4.70; the EDM teacher 2.44 at 79 NFE (0.71, 0.67); consistency training 13.0 at 1 step with recall 0.47 | S08 Table 2 | class-conditional ImageNet 64×64 |
| L21 | iCT trains consistency models without a teacher or LPIPS, reaching FID 2.51 on CIFAR-10 and 3.25 on ImageNet 64 in one step, with recall 0.63 on ImageNet 64 | S09 abstract, Tables 2–3 | iCT-deep |
| L57 | iCT's ImageNet-64 table reports FID (precision, recall): EDM teacher with Heun at 79 NFE 2.44 (0.71, 0.67); PD (ℓ2, re-implemented) 1 step 15.39 (0.59, 0.62), 2 steps 8.95 (0.63, 0.65), 4 steps 6.77 (0.66, 0.65); PD (LPIPS) 1 step 7.88 (0.66, 0.63); CD 1 step 6.20 (0.68, 0.63), 2 steps 4.70 (0.69, 0.64); CT 1 step 13.0 (0.71, 0.47), 2 steps 11.1 (0.69, 0.56); iCT-deep 1 step 3.25 (0.72, 0.63), 2 steps 2.77 (0.74, 0.62); BOOT 1 step 16.3 (0.68, 0.36); BigGAN-deep 4.06 (0.79, 0.48) | S09 Table 3 | class-conditional ImageNet 64×64; most rows taken from earlier papers, starred rows re-implemented by iCT's authors |
| L22 | iCT argues the target network's EMA rate should be zero for consistency training (though it may be nonzero for distillation), and removing it improved samples | S09 §3.2 | — |
| L23 | sCM trains continuous-time consistency models at up to 1.5B parameters and reaches FID 2.06 on CIFAR-10, 1.48 on ImageNet 64 and 1.88 on ImageNet 512 with two steps | S10 abstract | — |
| L24 | sCM's compiled table puts 1-step/2-step ImageNet-64 FID at PD 10.70/4.70, CD 6.20/4.70, iCT-deep 3.25/2.77, sCD 2.44/1.66 and sCT 2.04/1.48 | S10 Table 1 | values compiled from each method's own report |
| L25 | sCM's authors report that variational score distillation raises precision and lowers recall, like strong guidance, ending in mode collapse at high guidance, while two-step sCD keeps the teacher's precision and recall | S10 §5, Fig. 7 | EDM2-M, ImageNet 512 |
| L26 | sCM lists the failure of each family: direct distillation costs many teacher samples, adversarial distillation brings GAN training's complexity, progressive distillation needs many stages and is weak at 1–2 steps, and score distillation gives overly smooth, low-diversity samples | S10 §1 | authors' summary |
| L27 | CTM learns jumps from any time t to any earlier time s, written G(x_t, t, s) = (s/t) x_t + (1 − s/t) g(x_t, t, s); s = t recovers the denoiser and s = 0 the consistency function | S11 §3, Fig. 2 | — |
| L28 | CTM reports FID 1.92 on ImageNet 64 in one step, combining its jump loss with denoising and GAN losses | S11 abstract, §4; S14 Table 1 | — |
| L29 | Rectified flow's reflow procedure retrains on noise–image pairs from the current model, making paths straighter so that few Euler steps, even one, suffice | S12 §1, §2 | — |
| L30 | DMD trains a one-step generator to match the teacher at the level of distributions by minimising an approximate reverse KL divergence whose gradient is the difference of two scores: one from the frozen teacher and one from a second diffusion model trained online on the generator's own outputs | S13 §3.2 | — |
| L31 | DMD's scores are evaluated after adding noise to generator outputs, at noise levels between 0.02 T and 0.98 T, and its per-sample weight divides by the mean absolute gap between the teacher's denoised image and the sample | S13 §3.2, Eqs. 7–8 | — |
| L32 | DMD adds a regression loss on teacher noise–image pairs to stop mode collapse, since the score is blind to how much mass each mode gets | S13 §3.3 | — |
| L58 | Precision is the probability that a generated image falls within the estimated support of real images, recall the probability that a real image falls within the support of generated ones, both estimated with k-nearest-neighbour hyperspheres in a feature space; they separate sample quality from coverage | S25 §1–2, Fig. 1 | — |
| L56 | In DMD's own two-mode toy, the distribution-matching objective without the regression loss covers more of the target than the real score alone but recovers only the closest mode and misses the other entirely; adding the regression loss recovers both | S13 Fig. 3 | 2-D toy |
| L33 | On ImageNet 64 DMD reaches FID 2.62 in one step against its EDM teacher's 2.32 at 512 NFE; on CIFAR-10/ImageNet-64 the ablations give 3.82/9.21 without distribution matching and 5.58/5.61 without the regression loss | S13 Tables 1–2 | — |
| L34 | DMD's text-to-image model distils Stable Diffusion 1.5 to FID 11.49 on COCO-30k in 0.09 s per image against the teacher's 8.78 in 2.59 s, after about 36 hours on 72 A100 GPUs | S13 §4.3, Table 3 | guidance scale 3 |
| L35 | DMD2 removes the regression loss, which costs about 700 A100-days to build for SDXL and ties the student to the teacher's paths; without it training is unstable, with mean brightness oscillating, unless the fake score gets five updates per generator update | S14 §3, §4.2, App. C | — |
| L36 | DMD2's ImageNet-64 ablation: DMD 2.62; without regression 3.48; with the two-time-scale rule 2.61; adding a GAN loss on real data 1.51; longer training 1.28, against the teacher's 2.32 (ODE) and 1.36 (SDE) at 511 NFE | S14 Tables 1, 3 | — |
| L37 | DMD2 extends to 4-step generators that alternate denoising and re-noising, trained on their own simulated intermediate inputs ("backward simulation") rather than on noised real images | S14 §4.4–4.5 | — |
| L38 | DMD2's 4-step SDXL student scores FID 19.32 on COCO; without the GAN term its images are oversaturated and smooth (26.90) | S14 Tables 2, 4, Fig. 7 | 10K COCO-2014 prompts |
| L39 | ADD combines an adversarial loss against real images with a score-distillation loss from the teacher, sampling large models in 1–4 steps; its own paper notes lower sample diversity than its teacher SDXL | S15 §1, §3, §4 | — |
| L40 | Shortcut models condition one network on the step size as well as the noise level; a jump of size 2d is trained to equal two jumps of size d made by the model itself, and size 0 is ordinary flow matching, all in one training run without a teacher | S16 §3, Eqs. 3–5, Alg. 1 | — |
| L41 | Shortcut training uses 128 as the smallest step unit (eight step sizes), a quarter of each batch for self-consistency targets, EMA weights to make them, and weight decay for stability; it costs about 16% more than a diffusion model | S16 §3.1 | DiT-B experiments |
| L42 | In one codebase at equal or greater compute on DiT-B, FID-50k at 128/4/1 steps is, on CelebA-HQ 256: flow matching 7.3/(63.3)/(280.5), PD (302.9)/(251.3)/14.8, CD 59.5/39.6/38.2, CT 53.7/19.0/33.2, reflow 16.1/18.4/23.2, shortcut 6.9/13.8/20.5; on ImageNet 256: flow matching 17.3/(108.2)/(324.8), PD (201.9)/(142.5)/35.6, CD 132.8/98.01/136.5, CT 42.8/43.0/69.7, reflow 16.9/32.8/44.8, shortcut 15.5/28.3/40.3; parentheses mark budgets the objective is not meant for | S16 Table 1 | DiT-B, sd-vae latents; plain diffusion and live-reflow rows not used |
| L43 | Shortcut models' few-step errors look like wrong fine details, where flow models' few-step errors look like blur and mode collapse | S16 §5.1 | — |
| L44 | A flow map X_{s,t} jumps between any two times on a probability-flow trajectory; written X_{s,t}(x) = x + (t − s) v_{s,t}(x), its slope on the diagonal is the ODE's velocity (the tangent condition); consistency models, CTM, shortcut models and MeanFlow are special cases | S17 §2, Lemma 2.1, Eq. 6 | — |
| L45 | That paper groups ways to learn the flow map into Eulerian, Lagrangian and progressive self-distillation, and found the Lagrangian family most stable | S17 §1 | — |
| L46 | MeanFlow learns the average velocity over an interval through an identity linking it to the instantaneous velocity, and reaches FID 3.43 in one network call on ImageNet 256 trained from scratch, with no pretraining, distillation or curriculum | S18 abstract, §1 | ImageNet 256×256 |
| L47 | Align Your Flow argues analytically and empirically that consistency models degrade as the number of steps grows (error accumulation in multistep sampling), while flow-map models keep improving | S19 §1 | — |
| L48 | Meng et al. distil classifier-free-guided models in two stages, first matching the combined conditional and unconditional output with one student, then progressively distilling it, reaching 1–4 steps on latent models | S07 §1 | — |
| L49 | A 768×768 latent consistency model distilled from Stable Diffusion for 2–4-step inference trains in about 32 A100 GPU hours | S20 abstract, §1 | preprint |
| L50 | A consistency model trained to match an ODE solver directly solves the ODE better (error 0.29 → 0.25) yet gives worse FID (103.9 → 158.6) | S21 §4, Table 1 | workshop paper; their setting |
| L51 | rCM reports that consistency distillation at application scale loses fine detail, that DMD2-style reverse-divergence distillation limits diversity, and combines the two | S22 §1, Figs. 1–2 | — |
| L52 | SDXL-Turbo is SDXL distilled with ADD; it samples in 1–4 steps, a single step being enough, at 512×512, with guidance disabled, and its card lists imperfect photorealism, no legible text and poor faces | S23 | model card, accessed 2026-10-16 |
| L53 | FLUX.1 [schnell] is a 12-billion-parameter rectified-flow transformer trained with latent adversarial diffusion distillation to sample in 1–4 steps | S24 | model card, accessed 2026-10-16 |
| L54 | EDM's preconditioning writes the denoiser as c_skip(σ) x + c_out(σ) F(c_in(σ) x; c_noise(σ)) with c_skip = σ_d²/(σ² + σ_d²), c_out = σσ_d/√(σ² + σ_d²), c_in = 1/√(σ² + σ_d²), c_noise = ¼ ln σ, and weights the loss by 1/c_out² | S04 Table 1, §5 | — |
| L55 | EDM's step levels are σ_i = (σ_max^{1/ρ} + i/(N−1)(σ_min^{1/ρ} − σ_max^{1/ρ}))^ρ with ρ = 7, σ_max = 80 and σ_min = 0.002 | S04 Eq. 5, Table 1 | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S11 | Figure 2 (the (t, s) triangle: score line, distillation line, CTM's triangle) | flow maps / L27 | shows which jumps each family learns | arXiv non-exclusive licence; no CC licence on the record | https://arxiv.org/abs/2310.02279 | do not reuse; our own figure plots measured data instead |
| F2 | S16 | Table 1 (FID at 128/4/1 steps for eight objectives) | which metric shows the damage / L42 | a controlled comparison in one codebase | numbers only; charted as our own figure with credit | https://arxiv.org/abs/2410.12557 | chart the numbers, quoted |
| F3 | S14 | Figure 8 (brightness oscillation without TTUR) | DMD2 / L35 | the instability the toy reproduces | arXiv non-exclusive licence | https://arxiv.org/abs/2405.14867 | do not reuse; the lab measures the toy's own trace |

## Open questions

- Whether Luhman & Luhman (S05) ever appeared at a venue: OpenAlex and Google Scholar show only the
  arXiv record. Carried as a preprint.
- DMD's 2.62 against its teacher's 2.32 (ODE, 512 NFE) is a single comparison in one paper; DMD2's
  1.28 beats the same teacher's ODE sampler but not by "surpassing the teacher" in every sense: the
  teacher's SDE sampler scores 1.36. The post says which teacher number each comparison uses.
- The surveys disagree on where progressive distillation belongs (S02 distribution-based, S03
  fidelity distillation, while its own paper and CM treat it as following the teacher's sampler). The
  post sorts by whether the student keeps the teacher's noise-to-image pairing, which is measurable,
  and says the survey labels differ.
