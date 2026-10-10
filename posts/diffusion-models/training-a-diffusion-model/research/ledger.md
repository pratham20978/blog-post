# Source ledger — training-a-diffusion-model

Series `diffusion-models`, part 5. Sweep run 2026-10-03. Tier L4, so the floor is 10
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

Every arXiv source was read in full as arXiv's own HTML rendering (arxiv.org/html/<id>), converted
to text with the math kept as LaTeX `alttext`, in the session scratchpad. arXiv PDFs arrived at
about 33 KB/s this session, so EDM and EDM2, which have no HTML rendering, were read from the
NeurIPS and CVF proceedings PDFs instead. Every claim row below was checked against the paper's
own text, table or equation, not against an abstract or a search snippet. Venues were confirmed
through OpenAlex DOIs, Google Scholar, and the proceedings sites named in the search log.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Chang, Koulieris, Chang & Shum, "On the design fundamentals of diffusion models: A survey" | Pattern Recognition | 2025 | 10.1016/j.patcog.2025.111934; arXiv:2306.04542 | peer-reviewed | https://doi.org/10.1016/j.patcog.2025.111934 | 2026-10-03 |
| S02 | T1 | Ho, Jain & Abbeel, "Denoising Diffusion Probabilistic Models" | NeurIPS 33 | 2020 | NeurIPS hash 4c5bcfec8584af0d967f1ab10179ca4b; arXiv:2006.11239 | peer-reviewed | https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html | 2026-10-03 |
| S03 | T1 | Nichol & Dhariwal, "Improved Denoising Diffusion Probabilistic Models" | ICML (PMLR v139) | 2021 | pmlr-v139-nichol21a; arXiv:2102.09672 | peer-reviewed | https://proceedings.mlr.press/v139/nichol21a.html | 2026-10-03 |
| S04 | T1 | Rombach, Blattmann, Lorenz, Esser & Ommer, "High-Resolution Image Synthesis with Latent Diffusion Models" | CVPR | 2022 | 10.1109/CVPR52688.2022.01042; arXiv:2112.10752 | peer-reviewed | https://doi.org/10.1109/CVPR52688.2022.01042 | 2026-10-03 |
| S05 | T3 | CompVis/stable-diffusion, `configs/stable-diffusion/v1-inference.yaml` (main branch) | — | 2022 | — | source | https://github.com/CompVis/stable-diffusion/blob/main/configs/stable-diffusion/v1-inference.yaml | 2026-10-03 |
| S06 | T3 | Hugging Face diffusers v0.40.0: `schedulers/scheduling_ddim.py`, `scheduling_euler_discrete.py`, `scheduling_dpmsolver_multistep.py` (installed package source) | — | 2026 | diffusers==0.40.0 | source | https://github.com/huggingface/diffusers/tree/v0.40.0/src/diffusers/schedulers | 2026-10-03 |
| S07 | T1 | Song, Meng & Ermon, "Denoising Diffusion Implicit Models" | ICLR | 2021 | arXiv:2010.02502 | peer-reviewed | https://arxiv.org/abs/2010.02502 | 2026-10-03 |
| S08 | T1 | Kingma & Gao, "Understanding Diffusion Objectives as the ELBO with Simple Data Augmentation" | NeurIPS 36 | 2023 | 10.52202/075280-2858; arXiv:2303.00848 | peer-reviewed | https://proceedings.neurips.cc/paper_files/paper/2023/hash/ce79fbf9baef726645bc2337abb0ade2-Abstract-Conference.html | 2026-10-03 |
| S09 | T1 | Karras, Aittala, Aila & Laine, "Elucidating the Design Space of Diffusion-Based Generative Models" (EDM) | NeurIPS 35 | 2022 | NeurIPS hash a98846e9d9cc01cfb87eb694d946ce6b; arXiv:2206.00364 | peer-reviewed | https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html | 2026-10-03 |
| S10 | T1 | Hoogeboom, Heek & Salimans, "simple diffusion: End-to-end diffusion for high resolution images" | ICML (PMLR v202) | 2023 | pmlr-v202-hoogeboom23a; arXiv:2301.11093 | peer-reviewed | https://proceedings.mlr.press/v202/hoogeboom23a.html | 2026-10-03 |
| S11 | T1 | Chen, "On the Importance of Noise Scheduling for Diffusion Models" | arXiv (tech report; no venue found) | 2023 | arXiv:2301.10972 | preprint | https://arxiv.org/abs/2301.10972 | 2026-10-03 |
| S12 | T1 | Esser et al., "Scaling Rectified Flow Transformers for High-Resolution Image Synthesis" (SD3) | ICML (PMLR v235) | 2024 | pmlr-v235-esser24a; arXiv:2403.03206 | peer-reviewed | https://proceedings.mlr.press/v235/esser24a.html | 2026-10-03 |
| S13 | T1 | Lin, Liu, Li & Yang, "Common Diffusion Noise Schedules and Sample Steps are Flawed" | WACV | 2024 | 10.1109/WACV57701.2024.00532; arXiv:2305.08891 | peer-reviewed | https://doi.org/10.1109/WACV57701.2024.00532 | 2026-10-03 |
| S14 | T1 | Everaert, Fitsios, Bocchio, Arpa, Süsstrunk & Achanta, "Exploiting the Signal-Leak Bias in Diffusion Models" | WACV | 2024 | 10.1109/WACV57701.2024.00398; arXiv:2309.15842 | peer-reviewed | https://doi.org/10.1109/WACV57701.2024.00398 | 2026-10-03 |
| S15 | T1 | Wu, Si, Jiang, Huang & Liu, "FreeInit: Bridging Initialization Gap in Video Diffusion Models" | ECCV (LNCS) | 2024 | 10.1007/978-3-031-72646-0_22; arXiv:2312.07537 | peer-reviewed | https://doi.org/10.1007/978-3-031-72646-0_22 | 2026-10-03 |
| S16 | T1 | Podell et al., "SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis" | ICLR | 2024 | ICLR 2024 hash 081b08068e4733ae3e7ad019fe8d172f; arXiv:2307.01952 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2024/hash/081b08068e4733ae3e7ad019fe8d172f-Abstract-Conference.html | 2026-10-03 |
| S17 | T1 | Salimans & Ho, "Progressive Distillation for Fast Sampling of Diffusion Models" | ICLR | 2022 | arXiv:2202.00512 | peer-reviewed | https://arxiv.org/abs/2202.00512 | 2026-10-03 |
| S18 | T1 | Ho et al., "Imagen Video: High Definition Video Generation with Diffusion Models" | arXiv (no venue found) | 2022 | arXiv:2210.02303 | preprint | https://arxiv.org/abs/2210.02303 | 2026-10-03 |
| S19 | T1 | Li & He, "Back to Basics: Let Denoising Generative Models Denoise" (JiT) | CVPR | 2026 | CVF open access, CVPR 2026; arXiv:2511.13720 | peer-reviewed | https://openaccess.thecvf.com/content/CVPR2026/html/Li_Back_to_Basics_Let_Denoising_Generative_Models_Denoise_CVPR_2026_paper.html | 2026-10-03 |
| S20 | T1 | Hang, Gu, Li, Bao, Chen, Hu, Geng & Guo, "Efficient Diffusion Training via Min-SNR Weighting Strategy" | ICCV, pp. 7407–7417 | 2023 | 10.1109/ICCV51070.2023.00684; arXiv:2303.09556 | peer-reviewed | https://doi.org/10.1109/ICCV51070.2023.00684 | 2026-10-03 |
| S21 | T1 | Choi, Lee, Shin, Kim, Kim & Yoon, "Perception Prioritized Training of Diffusion Models" (P2) | CVPR | 2022 | 10.1109/CVPR52688.2022.01118; arXiv:2204.00227 | peer-reviewed | https://doi.org/10.1109/CVPR52688.2022.01118 | 2026-10-03 |
| S22 | T1 | Hang, Gu, Geng & Guo, "Improved Noise Schedule for Diffusion Training" | ICCV | 2025 | 10.1109/ICCV51701.2025.00456; arXiv:2407.03297 | peer-reviewed | https://doi.org/10.1109/ICCV51701.2025.00456 | 2026-10-03 |
| S23 | T1 | Karras, Aittala, Lehtinen, Hellsten, Aila & Laine, "Analyzing and Improving the Training Dynamics of Diffusion Models" (EDM2) | CVPR | 2024 | 10.1109/CVPR52733.2024.02282; arXiv:2312.02696 | peer-reviewed | https://openaccess.thecvf.com/content/CVPR2024/papers/Karras_Analyzing_and_Improving_the_Training_Dynamics_of_Diffusion_Models_CVPR_2024_paper.pdf | 2026-10-03 |
| S24 | T1 | Song & Ermon, "Improved Techniques for Training Score-Based Generative Models" (NCSNv2) | NeurIPS 33 | 2020 | NeurIPS hash 92c3b916311a5517d9290576e3ea37ad; arXiv:2006.09011 | peer-reviewed | https://proceedings.neurips.cc/paper_files/paper/2020/hash/92c3b916311a5517d9290576e3ea37ad-Abstract.html | 2026-10-03 |
| S25 | T1 | Dhariwal & Nichol, "Diffusion Models Beat GANs on Image Synthesis" (ADM) | NeurIPS 34 | 2021 | NeurIPS hash 49ad23d1ec9fa4bd8d77d02681df5cfa; arXiv:2105.05233 | peer-reviewed | https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html | 2026-10-03 |
| S26 | T1 | Peebles & Xie, "Scalable Diffusion Models with Transformers" (DiT) | ICCV | 2023 | 10.1109/ICCV51070.2023.00387; arXiv:2212.09748 | peer-reviewed | https://doi.org/10.1109/ICCV51070.2023.00387 | 2026-10-03 |
| S27 | T1 | Morales-Brotons, Vogels & Hendrikx, "Exponential Moving Average of Weights in Deep Learning: Dynamics and Benefits" | TMLR | 2024 | OpenReview 2M9CUnYnBA; arXiv:2411.18704 | peer-reviewed | https://openreview.net/forum?id=2M9CUnYnBA | 2026-10-03 |
| S28 | T1 | Hoffmann et al., "Training Compute-Optimal Large Language Models" (Chinchilla) | NeurIPS 35 | 2022 | 10.52202/068431-2176; arXiv:2203.15556 | peer-reviewed | https://doi.org/10.52202/068431-2176 | 2026-10-03 |
| S29 | T1 | Liang, He, Yang & Dai, "Scaling Laws for Diffusion Transformers" | ICLR | 2026 | ICLR 2026 hash 880d8999c07a8efc9bbbeb0c38f50765; arXiv:2410.08184 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2026/hash/880d8999c07a8efc9bbbeb0c38f50765-Abstract-Conference.html | 2026-10-03 |
| S30 | T1 | Mei, Tu, Delbracio, Talebi, Patel & Milanfar, "Bigger is not Always Better: Scaling Properties of Latent Diffusion Models" | TMLR | 2024 | OpenReview 0u7pWfjri5; arXiv:2404.01367 | peer-reviewed | https://openreview.net/forum?id=0u7pWfjri5 | 2026-10-03 |
| S31 | T1 | Li et al., "On the Scalability of Diffusion-based Text-to-Image Generation" | CVPR | 2024 | 10.1109/CVPR52733.2024.00898; arXiv:2404.02883 | peer-reviewed | https://doi.org/10.1109/CVPR52733.2024.00898 | 2026-10-03 |

Twenty-seven peer-reviewed sources carry an identifier. S11 (Chen) and S18 (Imagen Video) are
preprints and are labelled so in the post. S19 (JiT) was a tech report on arXiv but is in the CVPR
2026 open-access proceedings (checked on the listing page and on Google Scholar), so it is carried
as peer-reviewed. S29 is in the ICLR 2026 proceedings (listing page, hash above). S05 and S06 are
implementation evidence for what Stable Diffusion and diffusers actually ship.

**Checked and not carried.** Kaplan et al. 2020 (arXiv:2001.08361, never at a venue): S28 states
the same "backward is twice the forward" assumption and credits it. Yang et al. 2023 (ACM CSUR)
and Ma et al. 2025 (TPAMI) surveys: read for the map, but neither has a training-decision claim the
post uses; S01 carries the framing. Flow matching (Lipman et al.) and rectified flow (Liu et al.):
S12 defines the rectified-flow path and target the post uses. Yazıcı et al. 2019 (ICLR, EMA in GAN
training): read; S24 and S27 carry the EMA points with diffusion-specific evidence. The Stable
Diffusion 2 `v` config: the Stability-AI/stablediffusion repository returned 404 and the Hugging Face
SD 2.1 config is gated, so the post makes no claim about SD 2's shipped parameterisation; S13's own
fine-tuning setup is what it uses.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | survey-first: diffusion models survey training noise schedule loss weighting | Yang (ACM CSUR), Cao (TKDE), Shen efficient survey, Hang 2025 improved noise schedule (ICCV 2025), Croitoru (TPAMI), Ma efficient survey (TPAMI); gave the map and the Hang 2025 forward lead |
| 2 | 1 | OpenAlex | cited-by Lin et al. (W4394625831), sorted by citations | 126 citing works; adopters Lumiere, Emu Edit, W.A.L.T., CLAY; FreeInit (ECCV 2024) on the same low-frequency init gap in video; the design-fundamentals survey (Pattern Recognition 2025) |
| 3 | 1 | OpenAlex | title search for S01, S13, S14, S15, S20, S21, S22, S23, chen 2023, EMA dynamics | DOIs for WACV ×2, ICCV ×2, CVPR ×2, ECCV, Pattern Recognition; Chen 2023 only as arXiv (preprint); EMA-dynamics paper only as arXiv in OpenAlex |
| 4 | 1 | OpenAlex | cited-by Min-SNR (W4390873030) | 101 citing works, mostly applications; Lightweight-diffusion survey; no correction or failed replication found |
| 5 | 1 | Google Scholar | exponential moving average weights diffusion models training post-hoc | EDM2 (CVPR 2024), Morales-Brotons et al. (EMA dynamics), early weight averaging for LLMs; confirmed EDM2 is the EMA reference for diffusion |
| 6 | 1 | Google Scholar | scaling laws diffusion models compute model size | Liang et al. at ICLR 2026, Mei et al. in TMLR 2024, Li et al. CVPR 2024, video-DiT scaling (CVPR 2025), DiT (ICCV 2023) |
| 7 | 1 | arXiv | abs pages for 35 ids: Comments and Journal-ref fields | ICLR 2022 (S17), ICLR 2019 (Yazıcı), NeurIPS 2020 (S24), CVPR 2022 (S04, S21), CVPR 2024 (S31), TMLR (S27, S30), "tech report" for Chen 2023 and JiT |
| 8 | 1 | arXiv HTML | full text of 34 papers via arxiv.org/html | about 360k words in the scratchpad for grep verification; EDM and EDM2 have no HTML rendering |
| 9 | 1 | NeurIPS / CVF proceedings | EDM main paper PDF (NeurIPS 2022), EDM2 PDF (CVPR 2024 open access) | both full texts; EDM Table 1 and Table 2, EDM2 sections 2–4 and Table 2 |
| 10 | 1 | NeurIPS proceedings | 2020 listing grepped for "Improved Techniques for Training Score-Based" | hash 92c3b916311a5517d9290576e3ea37ad for NCSNv2 |
| 11 | 1 | ICLR proceedings | 2026 listing grepped for "Scaling Laws for Diffusion Transformers", "Back to Basics", "Improved Noise Schedule" | Liang et al. listed (hash 880d8999…); JiT and Hang 2025 not at ICLR |
| 12 | 1 | CVF open access | CVPR 2026 listing grepped for "Let Denoising Generative Models Denoise" | JiT listed in CVPR 2026; carried as peer-reviewed rather than as the arXiv tech report |
| 13 | 1 | Google Scholar | "Back to Basics: Let Denoising Generative Models Denoise" | Li & He, Proceedings of the IEEE/CVF Conference, 2026 — confirms the CVF listing |
| 14 | 1 | Semantic Scholar Graph API | citations of arXiv:2305.08891, influential only | 385 returned, 36 influential: Stable Video Diffusion, MVDream, CLAY, guidance-oversaturation work (ICLR 2025); answered this session (429 in earlier sessions) |
| 15 | 1 | Semantic Scholar Graph API | citations of arXiv:2303.09556, influential only | 337 returned, 42 influential: Hang 2025, FasterDiT, "Addressing Negative Transfer in Diffusion Models" (NeurIPS 2023), Denoising Task Routing (ICLR 2024); the multi-task reading is a line of work, not one paper |
| 16 | 1 | DBLP | search/publ/api "Min-SNR Weighting Strategy" | Anubis bot-verification page; DBLP unusable this session, as in parts 1–4 |
| 17 | 2 | arXiv full text | Lin et al. §§1–6, Tables 1–3, Algorithms 1–2 | terminal √ᾱ and SNR per schedule, x_T = 0.068265 x0 + 0.997667 ε, the four fixes, leading/linspace/trailing, COCO FID/IS, offset-noise critique, the x0-form sampler |
| 18 | 2 | arXiv full text | Min-SNR §§3–4, Tables 1, 2, 5 | weights in x0 units, ε and v conversions, 3.4× claim and its setup, UNet ablation, γ robustness, ImageNet 256 records |
| 19 | 2 | arXiv full text + NeurIPS PDF | EDM §5 and Table 1; Salimans & Ho §4; Imagen Video §2.4 | preconditioning formulas and their rationale; ε errors amplified as α → 0; v and the SNR+1 weighting; v for stability and colour shift |
| 20 | 2 | arXiv full text | SD3 §§2–3, 5.1, 5.3, B.3 | 61-formulation study and ranking, logit-normal sampling, resolution-dependent shift (eq. 23–24), training and EMA settings, scaling study and Table 6 |
| 21 | 2 | arXiv full text | simple diffusion §3.1 and Table 2; Chen 2023 §§1–2; iDDPM §3.2; LDM §4.3.2 and App. G; DDPM §4 and App. B | SNR × s² under pooling and the shifted schedule with its FIDs; image-size-dependent optimum and input scaling; cosine clip at 0.999; latent rescaling to unit std; linear β range and EMA 0.9999 |
| 22 | 3 | arXiv full text | P2 §3.2 and Table 1; Kingma & Gao Table 2; Hang 2025 Tables 3–4 | reweighting results with their setups; resample-vs-reweight comparison at a fixed 500K-iteration budget |
| 23 | 3 | CVPR PDF | EDM2 §3.3, §4, Table 2 | EMA-length optimum per config, drift over training, guidance and learning-rate dependence; ImageNet-512 size ladder |
| 24 | 3 | arXiv full text | Liang et al. §3; Hoffmann App. F; DiT §5 | isoFLOP fits N_opt = 0.0009 C^0.5681; backward ≈ 2× forward; DiT's training recipe and EMA 0.9999 |
| 25 | 4 | arXiv full text | JiT §§1–4 and Table 2 | ε- and v-prediction fail at 768 values per patch while x-prediction works; all nine combinations work at 48 values per patch — the target decision depends on capacity, not only on weighting |
| 26 | 4 | arXiv full text | Hang 2025 §3.2 | resampling log-SNR beats reweighting at the same budget — a direct challenge to reading Min-SNR as the last word |
| 27 | 4 | arXiv full text | Mei et al. abstract and §4; Everaert §1; Lin §5.4 | smaller models can win at a fixed inference budget; the signal leak can be exploited rather than removed; offset noise called a trick |
| 28 | 5 | GitHub raw | CompVis v1-inference.yaml | linear_start 0.00085, linear_end 0.012, timesteps 1000, scale_factor 0.18215 |
| 29 | 5 | Local source + run | diffusers 0.40.0 `DDIMScheduler` and `rescale_zero_terminal_snr`, run in the lab venv | scaled_linear formula; leading first step 981, trailing 999; rescaled ᾱ_T = 0 exactly; Euler/DPM set ᾱ_T = 2⁻²⁴ |
| 30 | 5 | GitHub / Hugging Face | Stability-AI/stablediffusion v2-inference-v.yaml; stabilityai/stable-diffusion-2-1 scheduler config | 404 and an authentication wall; no claim made about SD 2's shipped target |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | A recent review organises diffusion design choices by three functional components — the forward process, the reverse process and the sampling process — each with its own design factors | S01 abstract, §1 | survey framing |
| L02 | DDPM used T = 1000 and variances rising linearly from 10⁻⁴ to 0.02, small relative to data in [−1, 1] while keeping the SNR at x_T small | S02 §4 | pixel-space DDPM |
| L03 | DDPM kept an EMA of the weights with decay 0.9999 and did not sweep it | S02 App. B | — |
| L04 | iDDPM's cosine schedule sets ᾱ_t = f(t)/f(0) with f(t) = cos²(((t/T)+s)/(1+s)·π/2), s = 0.008, clips β_t at 0.999 to avoid a singularity near t = T, and was designed because the linear schedule destroys information faster than necessary | S03 §3.2, eq. 17 | — |
| L05 | Stable Diffusion v1 trains with 1,000 steps and a "scaled linear" schedule whose √β runs linearly from √0.00085 to √0.012, denoises a 4-channel 64×64 latent, and multiplies VAE latents by 0.18215 | S05 (`linear_start`, `linear_end`, `timesteps`, `image_size: 64`, `channels: 4`, `scale_factor`); S06 `scheduling_ddim.py` | v1 config as published; diffusers' formula |
| L06 | LDM rescales the autoencoder's latents by the inverse of their standard deviation, estimated on the first batch, so the latents have unit variance, and found that the SNR induced by the latent scale significantly affects results | S04 §4.3.2, App. D.1, App. G | KL-regularised latents |
| L07 | Lin et al.'s Table 1: at T = 1000 the linear schedule ends at √ᾱ_T = 0.006353 (SNR 4.035993×10⁻⁵), the cosine at 4.928220×10⁻⁵ (SNR 2.428735×10⁻⁹), and Stable Diffusion's at 0.068265 (SNR 0.004682), so its last step is x_T = 0.068265·x0 + 0.997667·ε | S13 §3.1, Table 1, eq. 10 | T = 1000 |
| L08 | The leaked signal at the last step is the lowest-frequency information, such as each channel's mean; the model learns to respect it, and pure noise at inference has zero mean, so Stable Diffusion up to 2.1 generates only medium-brightness images and fails prompts like "solid black background" | S13 §1, §3.1 | SD up to v2.1 at the time of writing |
| L09 | Lin et al. propose four fixes: rescale the schedule to zero terminal SNR (keep √ᾱ_1, set √ᾱ_T to 0, rescale linearly between, Algorithm 1), train with v-prediction, always start sampling from the last timestep, and rescale classifier-free guidance | S13 abstract, §§3.1–3.4 | — |
| L10 | The cosine schedule's β clip exists to keep the terminal SNR from reaching zero, and a variance-exploding process cannot reach zero terminal SNR at all | S13 §3.1 | — |
| L11 | At zero SNR ε-prediction becomes a trivial task that teaches the model nothing about the data, so Lin et al. switch to v-prediction, where the last step's target is x0 itself | S13 §3.2 | — |
| L12 | Leading timestep spacing, used by the official DDIM and PNDM code, never includes the last training step; trailing spacing starts at it | S13 §3.3, Table 2 | — |
| L13 | Lin et al. fine-tuned SD 2.1-base on filtered LAION (batch 2048, lr 10⁻⁴, EMA 0.9999, 50k iterations); on 10k COCO-2014 captions with DDIM 50 steps and guidance 7.5, FID/IS went from 22.96/34.11 (same data, no fixes) to 21.66/36.16 (all fixes); the official model scored 23.76/32.84 | S13 §4, Table 3 | COCO-2014 val, 10k images |
| L14 | An ideal model trained with zero terminal SNR predicts the same data mean at the first step whatever the noise input; samples start to differ from the second step | S13 §5.2 | unconditional, perfectly converged |
| L15 | Offset noise shifts each channel's noise by a shared random offset so the model learns to ignore its input mean; it does allow very bright and dark images but can produce brightness that does not fit the data, and Lin et al. call it a trick that leaves the cause in place | S13 §5.4 | offset 0.1 in their description |
| L16 | Sampler code must not route a zero-SNR model through the ε form, which divides by zero; convert the output to x0 first and sample in the x0 form | S13 §6 | — |
| L17 | diffusers implements Lin's rescale as `rescale_zero_terminal_snr`, gives a 50-step sampler first timestep 981 under leading spacing (with steps_offset 1) and 999 under trailing, and its Euler and DPM-Solver schedulers patch the rescaled ᾱ_T to 2⁻²⁴, "close to 0 without being 0", so the first σ is not infinite | S06 | diffusers 0.40.0 |
| L18 | SDXL's final multi-aspect training stage at about 1024² used an offset-noise level of 0.05 | S16 §2.5 | SDXL base training |
| L19 | In video diffusion models, the initial noise's spatio-temporal frequency content at inference differs from training, and the low-frequency part strongly steers what is generated; FreeInit refines it at inference | S15 abstract, §1 | text-to-video models studied |
| L20 | The signal-leak bias can also be exploited: adding a modelled leak to the initial latent gives control over brightness and style with no training | S14 abstract | existing pretrained models |
| L21 | For a fixed weighting, the noise schedule acts as an importance-sampling distribution for estimating the loss: it changes the estimate's variance, not the objective | S08 §3.2 | weighting held fixed |
| L22 | EDM trains with ln σ ~ N(−1.2, 1.2²), weights the loss by (σ² + σ_data²)/(σ·σ_data)², and uses σ_data = 0.5, σ_min = 0.002, σ_max = 80, because a reduction in loss is possible only at intermediate noise: at very low noise the task is difficult and irrelevant, and at very high noise the target is far from the answer, the dataset average | S09 §5, Table 1 | — |
| L23 | Under EDM's log-normal σ the log-SNR is distributed N(−2P_m, (2P_s)²); rectified flow uses z_t = (1−t)x0 + tε, predicts the velocity ε − x0, and SD3 samples t from a logit-normal; changing the t-distribution is equivalent to reweighting the loss | S12 §§2–3.1, eqs. 13, 15, 18–19 | — |
| L24 | SD3 trained 61 formulations on ImageNet and CC12M and ranked them over 24 settings (EMA or not, dataset, sampler): rectified flow with logit-normal(0, 1) ranked first on average (1.54; 1.25 at 5 steps, 1.50 at 50), LDM's eps/linear 2.88, uniform rectified flow 5.67, v/linear 6.83, v/cos 9.17, and EDM's own (−1.2, 1.2) last at 15.58; only rectified flows with modified timestep sampling beat eps/linear | S12 §5.1, Table 1 | their models, datasets and samplers |
| L25 | SD3 notes that loss values of different formulations are not comparable and need not track sample quality, so formulations were compared by CLIP score and FID | S12 §5.1 | — |
| L26 | SD3's formulation study used batch 1024, AdamW at 10⁻⁴ with 1,000 warm-up steps, and an EMA copy updated every 100 batches with decay 0.99; each text encoder was dropped 46.4% of the time so about 10% of steps were unconditional | S12 App. B.3 | formulation study |
| L27 | SD3 argues higher resolutions need more noise because a constant image's n pixels give n observations of its value; matching the uncertainty gives t_m = √(m/n)·t_n / (1 + (√(m/n) − 1)·t_n), a log-SNR shift of −log(m/n); a human-preference study favoured shifts above 1.5, and SD3 trains and samples at 1024² with shift 3.0 | S12 §5.3.2, eqs. 23–24 | rectified flow, constant-image argument |
| L28 | simple diffusion: averaging an s×s window multiplies the SNR by s², so it shifts a reference schedule by (64/d)² (log-SNR by 2·log(64/d)); on ImageNet 256 the FID (train/eval) went from 7.65/6.87 for the unshifted cosine to 3.94/3.89 shifted to 64 and 3.76/3.71 shifted to 32; at 128 from 2.96/3.38 to 2.41/3.03 and 2.26/2.88 | S10 §3.1, eqs. 4–5, Table 2 | pixel-space ImageNet, their U-ViT |
| L29 | A preprint finds the optimal schedule depends on image size and shifts noisier as images grow, because pixels become more redundant, and that scaling the input by a factor b shifts the log-SNR curve without changing its shape | S11 abstract, §§1, 2.2 | preprint; pixel-space RIN models |
| L30 | EDM2 standardises ImageNet-512 latents to zero mean and σ_data = 0.5, trains on 2³¹ images in batches of 2048 at a constant learning rate, and samples with 32 deterministic second-order steps | S23 §2 | — |
| L31 | ε-prediction is a weighted x0 loss with weight SNR (w(λ) = e^λ); as the SNR goes to zero, small changes in the network's ε output are increasingly amplified in x0, since x0 = (z − σε)/α divides by α → 0; v ≡ αε − σx0 gives x0 = αz − σv | S17 §4, eq. 9, App. D | — |
| L32 | Salimans & Ho propose "truncated SNR" max(SNR, 1) and "SNR + 1" (the v loss) weightings in x0 units and find both good for training ordinary diffusion models | S17 §4, §5.1 | cosine schedule, t uniform |
| L33 | EDM: with ε-style preconditioning, D = x − σF, any error the network makes is amplified by σ; EDM instead picks c_skip = σ_data²/(σ² + σ_data²), c_out = σ·σ_data/√(σ² + σ_data²), c_in = 1/√(σ² + σ_data²), c_noise = ¼ ln σ, so inputs and targets have unit variance and errors are amplified as little as possible, and sets λ = 1/c_out² | S09 §5, Table 1 | — |
| L34 | EDM's Table 2: on CIFAR-10 conditional VP, FID went 2.48 (baseline), 2.18, 2.08, 2.09 (preconditioning), 1.88 (loss weighting and p_train), 1.79; on FFHQ 64 VE, 25.95, 22.53, 41.62, 3.39, 2.81, 2.53. The preconditioning alone left results largely unchanged except VE at 64², its main benefit being robustness; the new loss and noise distribution improved FID in every case | S09 §5, Table 2 | 35 NFE (CIFAR), 79 NFE (64²) |
| L35 | Imagen Video uses v-prediction for every model: it keeps the process numerically stable for distillation, avoids colour-shifting artefacts at high resolution and temporal colour shifts seen with ε-prediction, and converges faster in sample-quality metrics | S18 §2.4 | preprint; video cascade |
| L36 | JiT, at ImageNet 256 with JiT-B/16 (768 values per patch, 200 epochs, CFG), measured FID-50K for x-prediction 10.14, 10.45 and 8.62 with x, ε and v losses; ε-prediction 379.21, 394.58, 372.38; v-prediction 107.55, 126.88, 96.53. At ImageNet 64 with 48 values per patch all nine lay between 3.46 and 6.20 | S19 §3, Table 2 | their transformer, pixel space |
| L37 | JiT's argument: clean images lie near a low-dimensional manifold and noised quantities do not, so a network with too little capacity for the patch dimension can still predict clean data; loss weighting alone does not explain the failures | S19 abstract, §§1, 3 | manifold assumption |
| L38 | If each noise level had its own unshared network, the optimum would not depend on the per-level weights; weights matter only because parameters are shared | S07 §3, remark after Theorem 1 | — |
| L39 | Min-SNR treats each timestep as a task: fine-tuning on one band of timesteps helped nearby bands and hurt distant ones, which it reads as conflicting gradients | S20 §3.2, Fig. 2 | their models |
| L40 | Min-SNR's weights, in x0 units: constant 1, SNR (the ε loss), max(SNR, γ) with γ = 1 (from Salimans & Ho) and min(SNR, γ) with γ = 5 by default; for ε-prediction Min-SNR is min(γ/SNR, 1), and for v the weight is divided by SNR + 1 | S20 §3.4, §4.2 | — |
| L41 | Min-SNR-5 reached FID 10 3.4× faster than the other weightings with x0-prediction on ViT-B, ImageNet 256 latents; SNR weighting was worst; constant weighting was good at high noise and poor at low noise, and SNR weighting the opposite | S20 §4.2, Fig. 1, Figs. 5–6 | cosine, T = 1000, AdamW 10⁻⁴, batch 256, EMA 0.9999, EDM Heun sampler, FID-50K |
| L42 | Min-SNR's UNet ablation, FID at 200K / 1M iterations: x0 baseline 25.93 / 8.33, with Min-SNR-5 7.99 / 4.28; ε baseline 8.55 / 4.21, with Min-SNR-5 7.32 / 4.14 | S20 §4.2, Table 1 | UNet at ViT-B parameter count, ImageNet 256 latents |
| L43 | Min-SNR's γ ablation moved FID by at most 0.57 across γ = 1, 5, 10, 20 in any of four settings (ViT ε 4.89, 4.84, 4.94, 5.41; UNet ε 4.30, 4.14, 4.14, 4.12) | S20 Table 2 | ImageNet 256 |
| L44 | P2 weighting multiplies the standard weight by 1/(k + SNR)^γ to down-weight the low-noise steps, which teach imperceptible detail; FID-50k on FFHQ 256 (1000 steps) went from 7.86 to 6.92, CUB 9.60 to 6.95, MetFaces (250 steps) 44.34 to 36.80 | S21 §3.2, eq. 8, Table 1 | 256², ADM-style models |
| L45 | Kingma & Gao, ImageNet 64, ε-prediction with the cosine schedule: the standard sech weighting gave FID 1.85 with the DDPM sampler; the monotonic sigmoid(−λ + 2) weighting gave 1.68 | S08 §5.1, Table 2 | their VDM++ models |
| L46 | Hang et al. 2025 show that importance-sampling log-SNR is the same as modifying the schedule, and that putting more samples near log-SNR 0 beats raising the loss weight there at the same budget: DiT-B/2 on ImageNet 256 latents, Adam 10⁻⁴, batch 256, 500K iterations, best FID-10K over guidance 1.5–3.0 — cosine 10.85, Min-SNR 9.70, Soft-Min-SNR 9.07, Laplace 7.96, scaled cosine 8.04, Cauchy 8.14, shifted cosine (simple diffusion) 11.13, EDM 11.56, flow matching 11.98 | S22 §§2–3.2, Table 3 | FID-10K; best of three guidance scales per method |
| L47 | The Laplace schedule beat cosine at 500K iterations for every target: x0 11.16 → 8.48, v 11.06 → 7.96, ε 10.46 → 9.53 (FID-10K) | S22 §3.3, Table 4 | same setup as L46 |
| L48 | EDM2 found EDM's weighting, which equalises the loss at initialisation, drifts as training proceeds; it tracks the raw loss per noise level and scales the loss by its reciprocal, a continuous form of Kendall et al.'s multi-task weighting | S23 §2.1 | — |
| L49 | EDM2: the usual EMA is θ̂ ← βθ̂ + (1 − β)θ; a very long EMA keeps weight on the near-random early parameters, and longer runs want longer averages, so EDM2 uses a power-function average with β_γ(t) = (1 − 1/t)^(γ+1), which puts zero weight on θ(0) and stretches with training time; its width is σ_rel = (γ+1)^½(γ+2)^−1(γ+3)^−½, and σ_rel 0.10 is γ ≈ 6.94 | S23 §3.1, eqs. 1–2 | — |
| L50 | EDM2 reconstructs any EMA after training from two stored averages (γ = 16.97 and 6.94, σ_rel 0.05 and 0.10) saved every ~8M images (4096 steps at batch 2048), by a least-squares fit whose error falls roughly as 1/n⁴ in the number of snapshots | S23 §3.2 | — |
| L51 | EDM2's analysis: the best EMA length differs considerably between configurations (9% and 13% for two of them) and slowly shifts longer as training proceeds; it depends strongly on guidance strength; it gets shorter with a higher learning rate (σ_rel ∝ 1/(α_ref²·t_ref)), with a larger model and with simpler data | S23 §3.3, §4, Figs. 5–6 | ImageNet-512 |
| L52 | EDM2 on ImageNet-512 (FID without / with guidance, 63 NFE): XS 125M 3.53/2.91, S 280M 2.56/2.23, M 498M 2.25/2.01, L 777M 2.06/1.88, XL 1,119M 1.96/1.85, XXL 1,523M 1.91/1.81 | S23 §4, Table 2 | their U-Net, latent 64×64×4 |
| L53 | NCSNv2 recommends sampling with an EMA of the weights (momentum typically 0.999): it stabilises FID during training, removes colour-shift artefacts and improves FID in most cases, across many datasets | S24 §5, Technique 5 | score-based models |
| L54 | ADM used an EMA rate of 0.9999 for all experiments | S25 App. | — |
| L55 | DiT trains with AdamW at a constant 10⁻⁴, no weight decay, batch 256, horizontal flips only and no warm-up, keeps an EMA with decay 0.9999 and reports every result from the EMA weights | S26 §5 | ImageNet 256 and 512 |
| L56 | EMA of weights reduces the noise of stochastic updates, needs less learning-rate decay than plain SGD, acts as an implicit regulariser and gives solutions that differ from the last iterate | S27 abstract | image classification studies |
| L57 | Training compute is usually estimated as about 6 FLOPs per parameter per token, assuming the backward pass costs twice the forward pass | S28 App. F | transformers; the factor 3 over the forward pass carries to any network |
| L58 | DiT-XL/2 costs 118.64 Gflops per forward pass at 256 px and reaches FID 2.27 with guidance after 7M steps; at 400K steps its FID tracks model Gflops | S26 Table 4, §5, Fig. 2 | ImageNet 256; DiT's Gflops are multiply-adds |
| L59 | SD3 trained MM-DiTs of several depths for 500k steps at 256² with batch 4096: validation loss fell smoothly with model size and steps, tracked GenEval, human preference and T2I-CompBench, and showed no saturation; depth 38 needed a learning-rate change at 3×10⁵ steps to avoid divergence | S12 §5.3.3, Fig. 8 | their data and models |
| L60 | SD3's Table 6: larger models lose less at few sampling steps — the CLIP-score drop at 5 of 50 steps was 4.30% (depth 15), 3.59% (30), 2.71% (38) | S12 Table 6 | fixed seed |
| L61 | Liang et al. fit isoFLOP curves for rectified-flow DiTs (v-prediction, logit-normal sampling) at 10¹⁷–6×10¹⁸ FLOPs and found N_opt = 0.0009·C^0.5681 and D_opt = 186.85·C^0.4319, predicting loss for about 1B parameters at 1.5×10²¹ FLOPs; pretraining loss tracked FID | S29 §3, eqs. 6–8 | AdamW 10⁻⁴, batch 1024, EMA 0.99, 108M LAION pairs |
| L62 | Under a fixed inference (sampling) budget, smaller latent diffusion models frequently beat larger ones | S30 abstract, §4 | text-to-image LDMs studied |
| L63 | Scaling T2I backbones from 0.4B to 4B on up to 600M images, Li et al. find the training set's quality and diversity matter more than its size | S31 abstract | their UNet and transformer variants |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S13 | Figure 3 (eight prompt pairs, flawed vs fixed SD) | Why must the last step be pure noise / L08, L13 | the only evidence in the post of the flaw on a real model; "solid black background" coming out grey is what the toy cannot show | arXiv HTML states CC BY-SA 4.0 | https://arxiv.org/abs/2305.08891 | reuse unchanged on the `source` route, credited, licence named |
| F2 | S20 | Figure 5 (FID vs iterations for four weightings) | Loss weighting / L41 | shows the 3.4× | arXiv non-exclusive licence only | https://arxiv.org/abs/2303.09556 | do not reuse; the post quotes Table 1's numbers and measures its own per-level errors |
| F3 | S12 | Figure 6 (timestep shift and human preference) | Resolution / L27 | shows the shift curve | arXiv non-exclusive licence only | https://arxiv.org/abs/2403.03206 | do not reuse; our Figure 5 computes the shift from eq. 23 |
| F4 | S23 | Figure 5 (FID vs EMA length) | EMA / L51 | the canonical EMA sweep | no reuse licence found on the CVF copy | https://openaccess.thecvf.com/content/CVPR2024/papers/Karras_Analyzing_and_Improving_the_Training_Dynamics_of_Diffusion_Models_CVPR_2024_paper.pdf | do not reuse; the lab measures its own sweep |

## Open questions

- Whether Min-SNR's convergence gain survives once the schedule is also tuned: S22 suggests
  resampling log-SNR beats reweighting, but both are one group's measurements on DiT-B. The post
  reports both and does not choose.
- The best target at very high per-token dimension rests on one paper (S19). The post labels it
  one study and shows the mechanism on the toy rather than claiming generality.
- Lin et al. fine-tuned an existing model rather than training from scratch with zero terminal
  SNR; the FID gain (L13) is for that fine-tune.
- Chen 2023 (S11) never reached a venue that OpenAlex, Scholar or the proceedings listings show; it
  stays labelled a preprint.
