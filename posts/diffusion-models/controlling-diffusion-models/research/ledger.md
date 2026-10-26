# Source ledger — controlling-diffusion-models

Series `diffusion-models`, part 8. Sweep run 2026-10-18. Tier L4, so the floor is 10 peer-reviewed
or standard sources carrying an identifier, across 4 scholarly databases (Google Scholar, OpenAlex,
arXiv, Semantic Scholar, plus the ICLR 2022–2026, ICML 2022/2024 (PMLR v162, v235) and NeurIPS 2024
proceedings indexes for venues).

Every arXiv source was read in full text in the session scratchpad, from arXiv's own HTML rendering
(arxiv.org/html/<id>, math kept as LaTeX `alttext`) or, for Ho & Salimans, the PDF through
`pdftotext -layout`. Every claim row was checked against the paper's own text, table, algorithm or
equation, not against an abstract or a search snippet, except where a row says "abstract". The Stable
Diffusion inpainting model card was read on huggingface.co. DBLP was not tried (it has served a bot
wall in every session since 2026-09-24); venues were confirmed through OpenAlex DOIs, the proceedings
indexes and arXiv comment and journal-ref fields, as the search log records. The parameter counts in
the post are computed, not quoted: the lab's `census` stage builds SD 1.5's published U-Net config
and diffusers' ControlNet on PyTorch's meta device (S43, S44).

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Cao, Zhou, Song & Yang, "Controllable Generation with Text-to-Image Diffusion Models: A Survey" | IEEE TPAMI | 2025 | 10.1109/TPAMI.2025.3646548; arXiv:2403.04279 | peer-reviewed | https://doi.org/10.1109/TPAMI.2025.3646548 | 2026-10-18 |
| S02 | T1 | Huang, Huang, Liu, Yan, Lv, Liu, Xiong, Zhang, Cao & Chen, "Diffusion Model-Based Image Editing: A Survey" | IEEE TPAMI | 2025 | 10.1109/TPAMI.2025.3541625; arXiv:2402.17525 | peer-reviewed | https://doi.org/10.1109/TPAMI.2025.3541625 | 2026-10-18 |
| S03 | T1 | Dhariwal & Nichol, "Diffusion Models Beat GANs on Image Synthesis" | NeurIPS 34 | 2021 | arXiv:2105.05233 | peer-reviewed | https://arxiv.org/abs/2105.05233 | 2026-10-18 |
| S04 | T1 | Ho & Salimans, "Classifier-Free Diffusion Guidance" | arXiv (short version at the NeurIPS 2021 Workshop on Deep Generative Models) | 2022 | arXiv:2207.12598v1 | preprint | https://arxiv.org/abs/2207.12598 | 2026-10-18 |
| S05 | T1 | Nichol, Dhariwal, Ramesh, Shyam, Mishkin, McGrew, Sutskever & Chen, "GLIDE: Towards Photorealistic Image Generation and Editing with Text-Guided Diffusion Models" | ICML (PMLR 162) | 2022 | pmlr-v162-nichol22a; arXiv:2112.10741 | peer-reviewed | https://proceedings.mlr.press/v162/nichol22a.html | 2026-10-18 |
| S06 | T1 | Saharia, Chan, Saxena, Li, Whang, Denton, Ghasemipour, Ayan et al., "Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding" (Imagen) | NeurIPS 35 | 2022 | 10.52202/068431-2643; arXiv:2205.11487 | peer-reviewed | https://doi.org/10.52202/068431-2643 | 2026-10-18 |
| S07 | T1 | Lin, Liu, Li & Yang, "Common Diffusion Noise Schedules and Sample Steps are Flawed" | WACV | 2024 | 10.1109/WACV57701.2024.00532; arXiv:2305.08891 | peer-reviewed | https://doi.org/10.1109/WACV57701.2024.00532 | 2026-10-18 |
| S08 | T1 | Kynkäänniemi, Aittala, Karras, Laine, Aila & Lehtinen, "Applying Guidance in a Limited Interval Improves Sample and Distribution Quality in Diffusion Models" | NeurIPS 37 | 2024 | 10.52202/079017-3892; arXiv:2404.07724 | peer-reviewed | https://doi.org/10.52202/079017-3892 | 2026-10-18 |
| S09 | T1 | Karras, Aittala, Kynkäänniemi, Lehtinen, Aila & Laine, "Guiding a Diffusion Model with a Bad Version of Itself" | NeurIPS 37 | 2024 | 10.52202/079017-1679; arXiv:2406.02507 | peer-reviewed | https://doi.org/10.52202/079017-1679 | 2026-10-18 |
| S10 | T1 | Sadat, Hilliges & Weber, "Eliminating Oversaturation and Artifacts of High Guidance Scales in Diffusion Models" (APG) | ICLR | 2025 | ICLR 2025 hash d1450d6c10c6b6cf1b80964357f5fa08; arXiv:2410.02416 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2025/hash/d1450d6c10c6b6cf1b80964357f5fa08-Abstract-Conference.html | 2026-10-18 |
| S11 | T1 | Sadat, Buhmann, Bradley, Hilliges & Weber, "CADS: Unleashing the Diversity of Diffusion Models through Condition-Annealed Sampling" | ICLR | 2024 | ICLR 2024 hash 6769bfdeb7313ded45714aabf759adfe; arXiv:2310.17347 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2024/hash/6769bfdeb7313ded45714aabf759adfe-Abstract-Conference.html | 2026-10-18 |
| S12 | T1 | Chidambaram, Gatmiry, Chen, Lee & Lu, "What does guidance do? A fine-grained analysis in a simple setting" | NeurIPS 37 | 2024 | arXiv:2409.13074 | peer-reviewed | https://arxiv.org/abs/2409.13074 | 2026-10-18 |
| S13 | T1 | Wu, Chen, Li, Wang & Wei, "Theoretical Insights for Diffusion Guidance: A Case Study for Gaussian Mixture Models" | ICML (PMLR 235) | 2024 | arXiv:2403.01639 | peer-reviewed | https://arxiv.org/abs/2403.01639 | 2026-10-18 |
| S14 | T1 | Bradley & Nakkiran, "Classifier-Free Guidance is a Predictor-Corrector" | arXiv | 2024 | arXiv:2408.09000v2 | preprint | https://arxiv.org/abs/2408.09000 | 2026-10-18 |
| S15 | T1 | Jin, Shi & Gu, "Stage-wise Dynamics of Classifier-Free Guidance in Diffusion Models" | ICLR | 2026 | ICLR 2026 hash f9e2800a251fa9107a008104f47c45d1; arXiv:2509.22007 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2026/hash/f9e2800a251fa9107a008104f47c45d1-Abstract-Conference.html | 2026-10-18 |
| S16 | T1 | Lehman Pavasovic, Verbeek, Biroli & Mezard, "Overshoot and Shrinkage in Classifier-Free Guidance: From Theory to Practice" | ICLR | 2026 | ICLR 2026 hash d7168ad82b4780797ffa8202c531ef6a; arXiv:2502.07849 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2026/hash/d7168ad82b4780797ffa8202c531ef6a-Abstract-Conference.html | 2026-10-18 |
| S17 | T1 | Meng, Rombach, Gao, Kingma, Ermon, Ho & Salimans, "On Distillation of Guided Diffusion Models" | CVPR | 2023 | 10.1109/CVPR52729.2023.01374; arXiv:2210.03142 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.01374 | 2026-10-18 |
| S18 | T1 | Zhang, Rao & Agrawala, "Adding Conditional Control to Text-to-Image Diffusion Models" (ControlNet) | ICCV | 2023 | 10.1109/ICCV51070.2023.00355; arXiv:2302.05543 | peer-reviewed | https://doi.org/10.1109/ICCV51070.2023.00355 | 2026-10-18 |
| S19 | T1 | Mou, Wang, Xie, Wu, Zhang, Qi, Shan & Qie, "T2I-Adapter: Learning Adapters to Dig Out More Controllable Ability for Text-to-Image Diffusion Models" | AAAI 38 | 2024 | 10.1609/aaai.v38i5.28226; arXiv:2302.08453 | peer-reviewed | https://doi.org/10.1609/aaai.v38i5.28226 | 2026-10-18 |
| S20 | T1 | Ye, Zhang, Liu, Han & Yang, "IP-Adapter: Text Compatible Image Prompt Adapter for Text-to-Image Diffusion Models" | arXiv | 2023 | arXiv:2308.06721v1 | preprint | https://arxiv.org/abs/2308.06721 | 2026-10-18 |
| S21 | T1 | Li, Liu, Wu, Mu, Yang, Gao, Li & Lee, "GLIGEN: Open-Set Grounded Text-to-Image Generation" | CVPR | 2023 | 10.1109/CVPR52729.2023.02156; arXiv:2301.07093 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.02156 | 2026-10-18 |
| S22 | T1 | Li, Yang, Kuang, Wu, Wang, Xiao & Chen, "ControlNet++: Improving Conditional Controls with Efficient Consistency Feedback" | ECCV (LNCS) | 2024 | 10.1007/978-3-031-72667-5_8; arXiv:2404.07987 | peer-reviewed | https://doi.org/10.1007/978-3-031-72667-5_8 | 2026-10-18 |
| S23 | T1 | Zavadski, Feiden & Rother, "ControlNet-XS: Rethinking the Control of Text-to-Image Diffusion Models as Feedback-Control Systems" | ECCV (LNCS) | 2024 | 10.1007/978-3-031-73223-2_20; arXiv:2312.06573 | peer-reviewed | https://doi.org/10.1007/978-3-031-73223-2_20 | 2026-10-18 |
| S24 | T1 | Hu, Shen, Wallis, Allen-Zhu, Li, Wang, Wang & Chen, "LoRA: Low-Rank Adaptation of Large Language Models" | ICLR | 2022 | arXiv:2106.09685 | peer-reviewed | https://arxiv.org/abs/2106.09685 | 2026-10-18 |
| S25 | T1 | Gal, Alaluf, Atzmon, Patashnik, Bermano, Chechik & Cohen-Or, "An Image is Worth One Word: Personalizing Text-to-Image Generation using Textual Inversion" | ICLR | 2023 | arXiv:2208.01618 | peer-reviewed | https://arxiv.org/abs/2208.01618 | 2026-10-18 |
| S26 | T1 | Ruiz, Li, Jampani, Pritch, Rubinstein & Aberman, "DreamBooth: Fine Tuning Text-to-Image Diffusion Models for Subject-Driven Generation" | CVPR | 2023 | 10.1109/CVPR52729.2023.02155; arXiv:2208.12242 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.02155 | 2026-10-18 |
| S27 | T1 | Kumari, Zhang, Zhang, Shechtman & Zhu, "Multi-Concept Customization of Text-to-Image Diffusion" (Custom Diffusion) | CVPR | 2023 | 10.1109/CVPR52729.2023.00192; arXiv:2212.04488 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.00192 | 2026-10-18 |
| S28 | T1 | Biderman, Portes, Gonzalez Ortiz, Paul, Greengard, Jennings, King, Havens et al., "LoRA Learns Less and Forgets Less" | TMLR | 2024 | OpenReview aloEru2qCG; arXiv:2405.09673 | peer-reviewed | https://arxiv.org/abs/2405.09673 | 2026-10-18 |
| S29 | T1 | Yeh, Hsieh, Gao, Yang, Oh & Gong, "Navigating Text-To-Image Customization: From LyCORIS Fine-Tuning to Model Evaluation" | ICLR | 2024 | ICLR 2024 hash 727658ad24ba28e02dffd379bdc69448; arXiv:2309.14859 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2024/hash/727658ad24ba28e02dffd379bdc69448-Abstract-Conference.html | 2026-10-18 |
| S30 | T1 | Song, Sohl-Dickstein, Kingma, Kumar, Ermon & Poole, "Score-Based Generative Modeling through Stochastic Differential Equations" | ICLR | 2021 | arXiv:2011.13456 | peer-reviewed | https://arxiv.org/abs/2011.13456 | 2026-10-18 |
| S31 | T1 | Lugmayr, Danelljan, Romero, Yu, Timofte & Van Gool, "RePaint: Inpainting using Denoising Diffusion Probabilistic Models" | CVPR | 2022 | 10.1109/CVPR52688.2022.01117; arXiv:2201.09865 | peer-reviewed | https://doi.org/10.1109/CVPR52688.2022.01117 | 2026-10-18 |
| S32 | T1 | Chung, Kim, McCann, Klasky & Ye, "Diffusion Posterior Sampling for General Noisy Inverse Problems" (DPS) | ICLR | 2023 | arXiv:2209.14687 | peer-reviewed | https://arxiv.org/abs/2209.14687 | 2026-10-18 |
| S33 | T1 | Wu, Trippe, Naesseth, Blei & Cunningham, "Practical and Asymptotically Exact Conditional Sampling in Diffusion Models" (TDS) | NeurIPS 36 | 2023 | 10.52202/075280-1363; arXiv:2306.17775 | peer-reviewed | https://doi.org/10.52202/075280-1363 | 2026-10-18 |
| S34 | T2 | Stable Diffusion v1.5 inpainting model card, `stable-diffusion-v1-5/stable-diffusion-inpainting` | Hugging Face | 2022 | — | official-docs | https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-inpainting | 2026-10-18 |
| S35 | T1 | Meng, He, Song, Song, Wu, Zhu & Ermon, "SDEdit: Guided Image Synthesis and Editing with Stochastic Differential Equations" | ICLR | 2022 | arXiv:2108.01073 | peer-reviewed | https://arxiv.org/abs/2108.01073 | 2026-10-18 |
| S36 | T1 | Song, Meng & Ermon, "Denoising Diffusion Implicit Models" (DDIM) | ICLR | 2021 | arXiv:2010.02502 | peer-reviewed | https://arxiv.org/abs/2010.02502 | 2026-10-18 |
| S37 | T1 | Hertz, Mokady, Tenenbaum, Aberman, Pritch & Cohen-Or, "Prompt-to-Prompt Image Editing with Cross Attention Control" | ICLR | 2023 | arXiv:2208.01626 | peer-reviewed | https://arxiv.org/abs/2208.01626 | 2026-10-18 |
| S38 | T1 | Mokady, Hertz, Aberman, Pritch & Cohen-Or, "Null-text Inversion for Editing Real Images using Guided Diffusion Models" | CVPR | 2023 | 10.1109/CVPR52729.2023.00585; arXiv:2211.09794 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.00585 | 2026-10-18 |
| S39 | T1 | Brooks, Holynski & Efros, "InstructPix2Pix: Learning to Follow Image Editing Instructions" | CVPR | 2023 | 10.1109/CVPR52729.2023.01764; arXiv:2211.09800 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.01764 | 2026-10-18 |
| S40 | T1 | Karras, Aittala, Aila & Laine, "Elucidating the Design Space of Diffusion-Based Generative Models" (EDM) | NeurIPS 35 | 2022 | 10.52202/068431-1926; arXiv:2206.00364 | peer-reviewed | https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html | 2026-10-16 |
| S41 | T2 | Stable Diffusion v1.5 U-Net config, `stable-diffusion-v1-5/stable-diffusion-v1-5`, `unet/config.json` | Hugging Face | 2022 | — | official-docs | https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/unet/config.json | 2026-10-03 |
| S42 | T3 | diffusers v0.40.0, `ControlNetModel.from_unet` (`src/diffusers/models/controlnets/controlnet.py`) | GitHub | 2026 | — | source | https://github.com/huggingface/diffusers/tree/v0.40.0/src/diffusers/models/controlnets | 2026-10-18 |

Thirty-six sources are peer-reviewed and carry an identifier (S01–S03, S05–S13, S15–S19, S21–S33, S35–S40).
Three are preprints and are labelled so in the post: Ho & Salimans (S04; only a short workshop version
appeared, and no archival venue was found in OpenAlex or the ICLR, ICML and NeurIPS indexes searched),
Bradley & Nakkiran (S14) and IP-Adapter (S20). S40 and S41 were read in the series' part 7
(2026-10-16) and part 4 (2026-10-03) sweeps; their rows here repeat claims verified then. The ICLR
papers without DOIs carry their proceedings hash or arXiv id.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | arXiv API (id_list) | 52 ids of the guidance, control, adapter, personalisation, inpainting and editing papers | titles, authors, versions, comments and journal refs; venue notes for 30 of them (e.g. "Published at CVPR 2023", "NeurIPS 2024", "ICLR 2025") |
| 2 | 1 | Google Scholar | controllable generation text-to-image diffusion models survey | Cao et al.'s survey (S01, TPAMI 2025 per its arXiv comment) as the top hit |
| 3 | 1 | Google Scholar | classifier-free guidance diffusion diversity oversaturation | forward hop from CFG: Jin et al. ICLR 2026 (S15), Lehman Pavasovic et al. ICLR 2026 (S16), Kynkäänniemi et al. NeurIPS 2024 (S08, 262 citations), Sadat et al.'s frequency-domain guidance (2025 preprint, not used), feedback guidance (not used) |
| 4 | 1 | arXiv API (title, author) | "overshoot and shrinkage"; "stage-wise dynamics" AND guidance; au:Pavasovic | S15 is arXiv:2509.22007; S16's arXiv version is 2502.07849 under an earlier title |
| 5 | 1 | OpenAlex (title.search) | 38 titles of the sources | DOIs and venues for 20 sources (ICCV, CVPR, WACV, AAAI, ECCV, NeurIPS, TPAMI); arXiv-only records for the ICLR and ICML papers; HTTP 400 for one title with a question mark |
| 6 | 1 | ICLR proceedings index 2024, 2025, 2026 | titles of APG, CADS, CFG++, the two 2026 theory papers, LyCORIS | APG and CFG++ (2025), CADS and LyCORIS (2024), S15 and S16 (2026) listed with hashes; S16's page confirms the four authors of arXiv:2502.07849 |
| 7 | 1 | ICLR virtual site 2022, 2023 | LoRA, SDEdit, Textual Inversion, Prompt-to-Prompt, DPS | LoRA and SDEdit in 2022; Textual Inversion, Prompt-to-Prompt and DPS in 2023 |
| 8 | 1 | NeurIPS 2024 proceedings index; PMLR v235, v162 | What does guidance do; Theoretical insights for diffusion guidance; GLIDE | S12 at NeurIPS 2024; S13 at ICML 2024; GLIDE at ICML 2022 (nichol22a); Bradley & Nakkiran in none of them |
| 9 | 1 | Semantic Scholar (citations API) | forward citations of ControlNet (arXiv:2302.05543) | the newest 1,000 citers only (2026 applications); 97 flagged influential; no correction among them — chased through Google Scholar instead (#10) |
| 10 | 1 | Google Scholar | ControlNet zero convolution conditional control limitations controllability | forward hop from ControlNet: ControlNet++ (S22, ECCV 2024), Ctrl-LoRA (ICLR 2025), FlexControl (ICML 2025), RepControlNet (preprint); S22 is the correction used |
| 11 | 1 | OpenAlex (title.search) | ControlNet-XS | ECCV 2024 (LNCS) DOI for S23 |
| 12 | 4 | Google Scholar | personalization text-to-image diffusion fine-tuning forgetting overfitting LoRA DreamBooth | Yeh et al. ICLR 2024 (S29, 200 citations), HyperDreamBooth (CVPR 2024, not used), Preserve and Personalize (ICLR 2026, not used) |
| 13 | 2 | arXiv full text | CFG, classifier guidance, GLIDE, Imagen, Lin, guidance interval, autoguidance, APG, CADS | read in full; mechanisms and the numbers below |
| 14 | 4 | arXiv full text | Chidambaram, Wu, Bradley & Nakkiran, Jin, Lehman Pavasovic | what guidance provably does and does not sample; the low-dimension caveat |
| 15 | 2 | arXiv full text | ControlNet, T2I-Adapter, IP-Adapter, GLIGEN, ControlNet++, ControlNet-XS | wiring, initialisation, sizes and the zero-convolution ablation |
| 16 | 2 | arXiv full text | LoRA, Textual Inversion, DreamBooth, Custom Diffusion, LoRA Learns Less, LyCORIS | recipes, parameter sets, costs, the prior-preservation ablation |
| 17 | 2 | arXiv full text | score SDE imputation, RePaint, DPS, TDS | replacement, resampling, posterior approximations |
| 18 | 2 | arXiv full text | SDEdit, DDIM, Prompt-to-Prompt, null-text inversion, InstructPix2Pix | editing by noise, inversion, attention and paired training |
| 19 | 3 | arXiv full text | CFG Tables 1–2, guidance-interval Table 1, autoguidance §5, DreamBooth Table 3, ControlNet §3–4, InstructPix2Pix §3 and App. A | the numbers below, each with its setup |
| 20 | 5 | Hugging Face | stable-diffusion-v1-5/stable-diffusion-inpainting model card | 5 extra zero-initialised input channels, 440k inpainting steps, 25% fully masked |
| 21 | 5 | diffusers v0.40.0 on the meta device | SD 1.5 U-Net config; `ControlNetModel.from_unet`; the U-Net's attention projections | computed counts: U-Net 859,520,964; ControlNet 361,279,120; LoRA r = 4 on 128 projections 797,184; cross-attention K,V 19,169,280 |
| 22 | 1 | arXiv abs pages | licence of 16 candidate figures' papers | CC BY 4.0: InstructPix2Pix, T2I-Adapter, DreamBooth, S01, S15, S16; CC BY-SA 4.0: Lin et al.; the rest the arXiv non-exclusive licence |

Databases queried for the literature: Google Scholar, OpenAlex, arXiv and Semantic Scholar (four), plus
the ICLR, ICML and NeurIPS proceedings indexes for venue checks.

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | A TPAMI survey sorts controllable text-to-image generation by condition (adding new conditions, combining several, universal control) and splits new-condition methods into conditional score prediction, which is tuning-based, adapter-based or training-free, and condition-guided score estimation | S01 §II-F, §III | survey taxonomy |
| L02 | A TPAMI survey of diffusion image editing sorts more than 100 methods into training-based, test-time fine-tuning, and training- and fine-tuning-free approaches | S02 §I, Table I | survey taxonomy |
| L03 | Classifier guidance trains a classifier on noisy images and adds its gradient, scaled by s, to the diffusion model's score; a scale s samples in proportion to p(y given x) to the power s, which is sharper than p(y given x) | S03 §4.1–4.2 | — |
| L04 | At classifier scale 1 an unconditional ImageNet model's samples got about 50% probability for the intended class but did not look like it; a larger scale fixed it (corgi samples: FID 33.0 at scale 1, 12.0 at scale 10) | S03 §4.2, Fig. 3 | unconditional ImageNet model |
| L05 | Raising the classifier scale raises precision and IS and lowers recall | S03 Fig. 4–5 | class-conditional ImageNet 128 |
| L06 | Classifier-free guidance trains one network for conditional and unconditional denoising by replacing the condition with a null token with probability p_uncond, and samples with (1 + w) times the conditional estimate minus w times the unconditional one; w = 0 is unguided in the paper's convention | S04 Alg. 1–2, Eq. 6 | the paper's w is this post's w minus 1 |
| L07 | p_uncond of 0.1 and 0.2 performed about equally across the FID/IS frontier and 0.5 worse | S04 §4.2, Table 1 | ImageNet 64 |
| L08 | On ImageNet 64 with p_uncond = 0.1, FID is 1.8 unguided, 1.55 at the paper's w = 0.1, 3.03 at 0.3, 12.6 at 1.0 and 26.22 at 4.0, while IS rises from 53.71 to 260.2 | S04 Table 1 | ImageNet 64×64, 400k training steps |
| L09 | On ImageNet 128 (256 sampling steps), FID is 7.27 unguided, 2.43 at the paper's w = 0.3 and 21.53 at 4.0, while IS rises from 82.45 to 421.03 | S04 Table 2 | ImageNet 128×128, 2.7M training steps |
| L10 | Strongly guided samples (the paper's w = 3.0) display saturated colours, and more guidance decreases sample variety while increasing individual fidelity | S04 Fig. 3 caption, §4.1 | ImageNet 128 |
| L11 | With exact scores, the CFG combination is classifier guidance by the implicit classifier p(c given z) proportional to p(z given c)/p(z); with networks the CFG direction need not be the gradient of any classifier | S04 §3.2 | — |
| L12 | GLIDE compared CLIP guidance with classifier-free guidance, and human evaluators preferred classifier-free guidance for photorealism and caption similarity | S05 abstract, §4 | GLIDE's 3.5B model |
| L13 | Imagen reports that raising the CFG weight improves image-text alignment but yields highly saturated, unnatural images, which it attributes to the predicted clean image leaving the training range of -1 to 1; static thresholding clips the prediction to that range, dynamic thresholding divides by a percentile s when s exceeds 1 | S06 §2.3 | pixel-space models |
| L14 | Lin et al. found CFG over-exposes images as terminal SNR approaches zero and proposed rescaling the guided output's standard deviation to the conditional output's, mixed back by phi; w = 7.5 with phi = 0.7 worked, phi from 0.5 to 0.75 looked best, and full rescaling looked plain | S07 §3.4, §5.3 | SD 2.1 retrained with v-prediction and zero terminal SNR |
| L15 | Guidance is harmful at high noise levels, largely unnecessary at low ones and beneficial in the middle; at high noise it reduces each prompt's variety to a handful of template images | S08 §1 | — |
| L16 | In a 1-D example with ideal analytic denoisers, guidance at w = 6 at every noise level drops one mode almost entirely, and switching it off at high noise restores both | S08 §2–3, Fig. 1–2 | toy; the paper notes guidance is strictly harmful with ideal denoisers |
| L17 | Limiting guidance to an interval of noise levels improves ImageNet-512 FID: EDM2-S 2.23 to 1.68 (w 1.4 to 2.1, sigma in 0.28–2.90), EDM2-XXL 1.81 to 1.40 (sigma in 0.19–1.61), DiT-XL/2 3.04 to 2.40 (sigma in 0.34–1.02); SDXL used 0.28–5.42 | S08 Table 1, §4 | grid-searched settings; this post's convention for w |
| L18 | A single network is usually trained on both conditional and unconditional denoising by dropping the condition 10–20% of the time | S08 §2 | — |
| L19 | Autoguidance guides a model with a smaller, less-trained version of itself instead of the unconditional model and so controls quality without reducing variation: ImageNet-512 FID 2.56 unguided to 1.34 (EDM2-S, an XS guide trained 1/16 as long) and 1.25 (EDM2-XXL), ImageNet-64 1.01, and unconditional EDM2-S 11.67 to 3.86 | S09 abstract, §5 | ImageNet, EDM2 models |
| L20 | The guide must suffer the same kinds of degradation as the main model: shorter training alone gave FID 1.51 and reduced capacity alone 2.13; synthetic degradations of the main model did not work, and a guidance interval on top reduced the benefit | S09 §5.1 | EDM2-S, ImageNet-512 |
| L21 | APG splits the CFG update into parts parallel and orthogonal to the conditional prediction; the parallel part acts as a gain that saturates, the orthogonal part improves quality, so APG down-weights the parallel part and adds a norm limit and reverse momentum | S10 §3 | — |
| L22 | CADS adds scheduled, decreasing Gaussian noise to the conditioning vector during sampling, raising diversity at high guidance scales | S11 abstract | — |
| L23 | Guidance does not sample from the tilted distribution it is usually described as; as guidance grows, samples come increasingly from the edge of the conditional's support away from other classes, and with any error in the score, large guidance samples outside the support | S12 abstract, §1 | mixtures of compactly supported distributions and of Gaussians |
| L24 | In Gaussian mixtures, guidance raises classification confidence and lowers the differential entropy of the samples, for DDPM and DDIM | S13 abstract | Gaussian mixture models |
| L25 | CFG interacts differently with DDPM and DDIM, and neither produces the gamma-powered distribution; in the SDE limit CFG is a DDIM predictor for the conditional plus a Langevin corrector for a powered distribution | S14 abstract | preprint |
| L26 | With multimodal conditionals, CFG sampling passes through three stages: early guidance pulls toward the weighted mean and leaves a bias, the bias then suppresses weaker modes, and late guidance amplifies within-mode contraction; early strong guidance erodes global diversity, late strong guidance fine variation | S15 abstract, §3 | theory with experiments |
| L27 | In high enough dimension CFG reproduces the correct target distribution; its mean overshoot and variance shrinkage appear in lower dimensions and grow as the dimension falls | S16 abstract | Gaussian-mixture theory |
| L28 | Guidance distillation's first stage trains one student, given w as an input, to match the combined conditional and unconditional output; progressive distillation then cuts the steps, reaching 1–4 steps on latent models, at least 10 times fewer than the base | S17 §1, §3.1 | — |
| L29 | ControlNet locks the pretrained model and trains a copy of its encoding layers, joined to it by zero convolutions, 1×1 convolutions whose weight and bias start at zero: y_c = F(x; Θ) + Z(F(x + Z(c; Θz1); Θc); Θz2) | S18 §3.1, Eq. 1–2 | — |
| L30 | At the first training step both zero-convolution terms vanish, so the ControlNet's output equals the locked model's; the paper credits this with keeping random noise out of the trainable copy early in training | S18 §3.1, Eq. 3 | — |
| L31 | For SD 1.5, ControlNet copies the 12 encoder blocks and the middle block, whose outputs are added to the U-Net's 12 skip connections and its middle block; the 512×512 condition image is encoded to 64×64 by four 4×4 stride-2 convolutions with 16, 32, 64 and 128 channels | S18 §3.2 | SD 1.5 / 2.1 |
| L32 | Training SD with a ControlNet takes about 23% more GPU memory and 34% more time per iteration than training SD alone, because the locked encoder needs no gradients | S18 §3.2 | one A100 PCIe 40GB |
| L33 | ControlNet training replaces half of the text prompts with empty strings | S18 §3.3 | — |
| L34 | ControlNet does not learn the condition gradually: it abruptly starts following it, usually within 10k optimization steps ("sudden convergence") | S18 §3.3, Fig. 4 | — |
| L35 | Replacing the zero convolutions with Gaussian-initialised convolutions drops ControlNet to about ControlNet-lite's level, which the authors read as the pretrained copy being destroyed during fine-tuning | S18 §4.2, Fig. 8 | qualitative ablation, sketch condition |
| L36 | A depth ControlNet for SD 2 trained on 200k samples on one RTX 3090Ti for 5 days was hard to tell from SDv2-Depth (trained on an A100 cluster with more than 12M images): users' precision 0.52 ± 0.17; training did not collapse with 1k images | S18 §4.3–4.4 | 12 users, 200 images |
| L37 | Adding a ControlNet only to the conditional branch makes guidance too strong without a prompt; ControlNet's CFG resolution weighting multiplies each connection by 64/h_i | S18 §3.4 | — |
| L38 | ControlNet's images often fail to match their conditions; optimising cycle consistency against a reward model improved controllability by 11.1% mIoU (segmentation), 13.4% SSIM (line art) and 7.6% RMSE (depth) | S22 abstract, §4 | ControlNet++'s benchmarks |
| L39 | A control network of 1.7M parameters performed on par with ControlNet's 361M on ControlNet-XS's depth benchmark | S23 §3 | its own evaluation |
| L40 | T2I-Adapter trains small adapters, about 77M parameters and 300MB, whose features enter a frozen SD at the four scales of its encoder, computed once per generation | S19 §1, §3 | — |
| L41 | IP-Adapter adds a second cross-attention for image features beside each of SD's 16 text cross-attention layers, sharing the query, initialised from the text layer's key and value weights and added with weight lambda (lambda = 0 is the original model); about 22M trainable parameters | S20 §3.2, §4.1 | preprint |
| L42 | GLIGEN freezes the pretrained attention layers and inserts a gated self-attention, v = v + beta·tanh(gamma)·TS(SelfAttn([v, h^e])), with gamma initialised to 0 | S21 §3.2, Eq. 8 | — |
| L43 | LoRA writes the update to a frozen weight W0 as BA with rank r much smaller than its sides, A Gaussian and B zero so the update starts at zero, scaled by alpha/r; the merged weights add no inference latency | S24 §4.1 | — |
| L44 | On GPT-3 175B, LoRA cut trainable parameters 10,000 times and GPU memory 3 times compared with fine-tuning with Adam | S24 §1 | GPT-3 175B |
| L45 | Textual inversion learns one new word embedding for a concept from 3–5 images with the model frozen, starting from the embedding of a coarse descriptor, with 5,000 optimization steps | S25 §1, §3, §4 | LDM |
| L46 | DreamBooth fine-tunes the diffusion model on 3–5 images captioned "a [identifier] [class noun]" with a rare-token identifier: about 1,000 iterations, lambda = 1, learning rate 5e-6 for SD and about 1,000 generated class images, 5 minutes on one A100 | S26 §3.1–3.3 | SD and Imagen |
| L47 | Fine-tuning all layers causes language drift (the class noun loses its meaning) and reduced output diversity; the class-specific prior-preservation loss supervises the model with its own samples of the class | S26 §3.3 | — |
| L48 | DreamBooth's prior-preservation ablation on Imagen: PRES (how much random class samples resemble the subject, lower is better) 0.664 without against 0.493 with; DIV 0.371 against 0.391; subject fidelity DINO 0.712 against 0.684 | S26 Table 3 | 15 subjects, Imagen |
| L49 | DreamBooth describes textual inversion as limited by the expressiveness of the frozen diffusion model | S26 §2 | — |
| L50 | Custom Diffusion updates only the cross-attention key and value projections, the layers that change most under full fine-tuning though they are about 5% of the parameters, with a regularization set of real images; about 6 minutes on 2 A100s against about an hour on 4 A100s for DreamBooth, and 75MB of weights | S27 §3, Fig. 3, §4 | SD 1.x |
| L51 | In language-model fine-tuning on code and maths, LoRA underperformed full fine-tuning on the target domain but kept more of the base model's ability outside it and more diverse generations | S28 abstract | Llama-2 models, not diffusion |
| L52 | In LoRA-style fine-tuning of SD, more training generally raises concept fidelity and lowers text alignment, diversity and preservation of the base model; a higher learning rate acts like more training | S29 §5 | SD, LyCORIS algorithms |
| L53 | Score-based imputation samples the data given a known subset of its dimensions with an unconditional model, by conditioning the reverse process on the known part | S30 §5, App. I.2 | — |
| L54 | RePaint conditions an unconditional DDPM by replacing the known region at every step with a noised copy of the input; the plain version produces matching textures but semantically wrong completions, and resampling (re-noising and redoing steps) harmonises the image, with the benefit saturating at about 10 resamplings | S31 §4.1–4.2, Fig. 3 | — |
| L55 | RePaint's per-image sampling is much slower than GAN and autoregressive inpainting | S31 §6 | — |
| L56 | DPS approximates the intractable likelihood of the measurement given the noisy image by the likelihood given the denoiser's clean estimate, and takes a gradient step on the measurement error at every sampling step | S32 §3.1 | — |
| L57 | The twisted diffusion sampler is a sequential Monte Carlo method that targets a diffusion model's conditional distributions exactly as the number of particles grows, where other methods rely on heuristic approximations | S33 abstract | — |
| L58 | SD's inpainting model has 5 extra input channels (4 for the encoded masked image, 1 for the mask), zero-initialised on the restored checkpoint, then 440k inpainting steps at 512×512 with synthetic masks, a quarter of them masking everything, and 10% text dropping | S34 | model card, accessed 2026-10-18 |
| L59 | SDEdit noises an input to an intermediate time t0 and denoises it; more noise gives more realistic but less faithful results, and t0 from 0.3 to 0.6 works for reasonable inputs | S35 §1, §3, Fig. 3 | — |
| L60 | SDEdit beat GAN baselines by up to 98.09% on realism and 91.72% on overall satisfaction in human judgements of stroke-based synthesis | S35 §1, §4 | human study |
| L61 | DDIM's deterministic sampler is an ODE that can be run backwards, encoding an image into the noise that generates it and reconstructing it from that noise | S36 §4.3, §5.4 | — |
| L62 | DDIM inversion reconstructs well for an unguided model but breaks under CFG, which magnifies its accumulated error; SD's default guidance weight is 7.5; null-text inversion inverts at w = 1 as a pivot, then optimises the null-text embedding at each step to reconstruct at w = 7.5 | S38 §3 | SD |
| L63 | Prompt-to-Prompt edits by injecting the source image's cross-attention maps into the generation with the edited prompt during some of the steps, so the edited prompt keeps the source's layout | S37 §1, §3 | generated images; real ones need inversion |
| L64 | InstructPix2Pix's training data: GPT-3 fine-tuned on 700 human-written edit triplets generated 454,445 instruction and caption examples; SD with Prompt-to-Prompt made 100 image pairs per caption pair, filtered by CLIP directional similarity | S39 §3.1 | — |
| L65 | InstructPix2Pix starts from SD and adds input channels for the input image whose weights start at zero; it trained 10,000 steps on 8 A100 40GB over 25.5 hours at 256×256 with batch 1024 | S39 §3.2, App. A | — |
| L66 | InstructPix2Pix drops the image, the instruction, or both, 5% of the time each, and samples with two guidance scales, s_I for the input image and s_T for the instruction; s_T = 7.5 with s_I from 1.0 to 2.2 trades consistency with the input against the edit | S39 §3.2.1, Eq. 3, Fig. 8 | — |
| L67 | EDM writes the denoiser with input, skip and output scalings set by the noise level and the data's standard deviation, and spaces the sampling noise levels with rho = 7 between 80 and 0.002 | S40 Table 1, Eq. 5 | verified in part 7's sweep |
| L68 | SD 1.5's U-Net has block channels 320, 640, 1280 and 1280, two layers per block and cross-attention width 768 | S41 | published config |
| L69 | diffusers' ControlNetModel.from_unet copies the U-Net's input, down and middle blocks and adds the condition embedding and one zero-initialised 1×1 convolution per added output | S42 | diffusers v0.40.0 |
| L70 | Stable Diffusion was trained with the text condition dropped 10% of the time, for classifier-free guidance | S34 | v1.x model card, accessed 2026-10-18 |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S39 | Figure 2 (the GPT-3 + Prompt-to-Prompt data pipeline and the trained editor) | instruction editing / L64–L65 | shows in one picture how the paired training data is manufactured, which is the method | CC BY 4.0 (arXiv record) | https://arxiv.org/abs/2211.09800 | send to the route gate |
| F2 | S26 | Figure 3 (fine-tuning with the prior-preservation loss) | personalisation / L46–L47 | the method's two losses side by side | CC BY 4.0 (arXiv record) | https://arxiv.org/abs/2208.12242 | do not reuse: the lab's own measured figure carries the section, and the method fits in a sentence |
| F3 | S18 | Figure 2–3 (ControlNet block and SD wiring) | ControlNet / L29–L31 | the wiring | arXiv non-exclusive licence | https://arxiv.org/abs/2302.05543 | do not reuse; an original figure with SD 1.5's shapes and our computed counts |
| F4 | S08 | Figure 1–2 (1-D guided trajectories, mode drop) | guidance / L16 | the mechanism | arXiv non-exclusive licence | https://arxiv.org/abs/2404.07724 | do not reuse; the lab computes its own one-number example |
| F5 | S04 | Tables 1–2 (FID and IS against guidance strength) | guidance / L08–L09 | the published U-shape | numbers only | https://arxiv.org/abs/2207.12598 | chart the numbers, quoted |

## Open questions

- Ho & Salimans (S04) never appeared at an archival venue as far as OpenAlex and the indexes searched
  show; carried as a preprint, with the workshop version named.
- The toy measures what guidance does in a world whose relevant directions are few (four crescents);
  S16 proves the overshoot and shrinkage grow as dimension falls. The post states toy numbers as
  mechanism and quotes the papers' numbers for scale.
- ControlNet's zero-convolution ablation (L35) is qualitative in the paper. The lab reproduces the
  step-0 difference and a slower start, not a permanent loss; the post says which.
- The k-NN precision and recall of Kynkäänniemi et al. (2019) were computed in the lab but are not
  quoted: on the exact model, recall rose again at w = 7.5 because over-saturated outliers widen their
  own radii. The post measures coverage directly (the faint share) instead.
