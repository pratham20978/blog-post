# Source ledger — diffusion-beyond-images

Series `diffusion-models`, part 10. Sweep run 2026-10-21. Tier L3, so the floor is 7 peer-reviewed or
standard sources carrying an identifier, across 4 scholarly databases (Google Scholar, OpenAlex, arXiv,
Crossref; PMLR, NeurIPS and ICLR proceedings indexes confirmed venues; DBLP served its Anubis bot wall and
Semantic Scholar answered 429, both logged below).

Every arXiv source was read in full text in the session scratchpad from arXiv's own HTML rendering
(arxiv.org/html/<id>, math kept as LaTeX `alttext`). The two Nature papers were read as their open-access
article pages. MVDream's Figure 1 was checked in the arXiv v4 PDF (page 2). Every claim row was checked
against the paper's own text, table or equation, not an abstract or a search snippet. The ACM survey was
read in its latest arXiv version (v15, revised 2025-09-27), which extends the 2023 journal version; the
rows below cite only parts present in both (the six-category application table and Section 5's three
special-structure classes).

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang, "Diffusion Models: A Comprehensive Survey of Methods and Applications" (survey) | ACM Computing Surveys 56(4) | 2023 | 10.1145/3626235 | peer-reviewed | https://arxiv.org/abs/2209.00796 | 2026-10-21 |
| S2 | T1 | Ho, Salimans, Gritsenko, Chan, Norouzi & Fleet, "Video Diffusion Models" | NeurIPS 2022 | 2022 | arXiv:2204.03458 | peer-reviewed | https://arxiv.org/abs/2204.03458 | 2026-10-21 |
| S3 | T1 | Blattmann, Rombach, Ling, Dockhorn, Kim, Fidler & Kreis, "Align your Latents: High-Resolution Video Synthesis with Latent Diffusion Models" | CVPR 2023 | 2023 | 10.1109/CVPR52729.2023.02161 | peer-reviewed | https://arxiv.org/abs/2304.08818 | 2026-10-21 |
| S4 | T1 | Ge, Nah, Liu, Poon, Tao, Catanzaro, Jacobs, Huang, Liu & Balaji, "Preserve Your Own Correlation: A Noise Prior for Video Diffusion Models" (PYoCo) | ICCV 2023 | 2023 | 10.1109/ICCV51070.2023.02096 | peer-reviewed | https://arxiv.org/abs/2305.10474 | 2026-10-21 |
| S5 | T1 | Khachatryan, Movsisyan, Tadevosyan, Henschel, Wang, Navasardyan & Shi, "Text2Video-Zero: Text-to-Image Diffusion Models are Zero-Shot Video Generators" | ICCV 2023 | 2023 | 10.1109/ICCV51070.2023.01462 | peer-reviewed | https://arxiv.org/abs/2303.13439 | 2026-10-21 |
| S6 | T1 | Blattmann, Dockhorn, Kulal, Mendelevitch, Kilian, Lorenz, Levi, English, Voleti, Letts, Jampani & Rombach, "Stable Video Diffusion: Scaling Latent Video Diffusion Models to Large Datasets" | arXiv | 2023 | arXiv:2311.15127 | preprint | https://arxiv.org/abs/2311.15127 | 2026-10-21 |
| S7 | T1 | Chang, Tang, Gross & Azevedo, "How I Warped Your Noise: a Temporally-Correlated Noise Prior for Diffusion Models" | ICLR 2024 | 2024 | arXiv:2504.03072 | peer-reviewed | https://arxiv.org/abs/2504.03072 | 2026-10-21 |
| S8 | T1 | Unterthiner, van Steenkiste, Kurach, Marinier, Michalski & Gelly, "Towards Accurate Generative Models of Video: A New Metric & Challenges" (FVD) | arXiv | 2018 | arXiv:1812.01717 | preprint | https://arxiv.org/abs/1812.01717 | 2026-10-21 |
| S9 | T1 | Kong, Ping, Huang, Zhao & Catanzaro, "DiffWave: A Versatile Diffusion Model for Audio Synthesis" | ICLR 2021 | 2021 | arXiv:2009.09761 | peer-reviewed | https://arxiv.org/abs/2009.09761 | 2026-10-21 |
| S10 | T1 | Liu, Chen, Yuan, Mei, Liu, Mandic, Wang & Plumbley, "AudioLDM: Text-to-Audio Generation with Latent Diffusion Models" | ICML 2023 (PMLR 202) | 2023 | arXiv:2301.12503 | peer-reviewed | https://proceedings.mlr.press/v202/liu23f.html | 2026-10-21 |
| S11 | T1 | Evans, Carr, Taylor, Hawley & Pons, "Fast Timing-Conditioned Latent Audio Diffusion" (Stable Audio) | ICML 2024 (PMLR 235) | 2024 | arXiv:2402.04825 | peer-reviewed | https://proceedings.mlr.press/v235/evans24a.html | 2026-10-21 |
| S12 | T1 | Luo & Hu, "Diffusion Probabilistic Models for 3D Point Cloud Generation" | CVPR 2021 | 2021 | 10.1109/CVPR46437.2021.00286 | peer-reviewed | https://arxiv.org/abs/2103.01458 | 2026-10-21 |
| S13 | T1 | Zhou, Du & Wu, "3D Shape Generation and Completion through Point-Voxel Diffusion" (PVD) | ICCV 2021 | 2021 | 10.1109/ICCV48922.2021.00577 | peer-reviewed | https://arxiv.org/abs/2104.03670 | 2026-10-21 |
| S14 | T1 | Nichol, Jun, Dhariwal, Mishkin & Chen, "Point-E: A System for Generating 3D Point Clouds from Complex Prompts" | arXiv | 2022 | arXiv:2212.08751 | preprint | https://arxiv.org/abs/2212.08751 | 2026-10-21 |
| S15 | T1 | Poole, Jain, Barron & Mildenhall, "DreamFusion: Text-to-3D using 2D Diffusion" | ICLR 2023 | 2023 | arXiv:2209.14988 | peer-reviewed | https://arxiv.org/abs/2209.14988 | 2026-10-21 |
| S16 | T1 | Wang, Lu, Wang, Bao, Li, Su & Zhu, "ProlificDreamer: High-Fidelity and Diverse Text-to-3D Generation with Variational Score Distillation" | NeurIPS 2023 | 2023 | arXiv:2305.16213 | peer-reviewed | https://arxiv.org/abs/2305.16213 | 2026-10-21 |
| S17 | T1 | Shi, Wang, Ye, Long, Li & Yang, "MVDream: Multi-view Diffusion for 3D Generation" | ICLR 2024 | 2024 | arXiv:2308.16512 | peer-reviewed | https://arxiv.org/abs/2308.16512 | 2026-10-21 |
| S18 | T1 | Hoogeboom, Satorras, Vignac & Welling, "Equivariant Diffusion for Molecule Generation in 3D" (EDM) | ICML 2022 (PMLR 162) | 2022 | arXiv:2203.17003 | peer-reviewed | https://proceedings.mlr.press/v162/hoogeboom22a.html | 2026-10-21 |
| S19 | T1 | Xu, Yu, Song, Shi, Ermon & Tang, "GeoDiff: a Geometric Diffusion Model for Molecular Conformation Generation" | ICLR 2022 | 2022 | arXiv:2203.02923 | peer-reviewed | https://arxiv.org/abs/2203.02923 | 2026-10-21 |
| S20 | T1 | Jing, Corso, Chang, Barzilay & Jaakkola, "Torsional Diffusion for Molecular Conformer Generation" | NeurIPS 2022 | 2022 | arXiv:2206.01729 | peer-reviewed | https://arxiv.org/abs/2206.01729 | 2026-10-21 |
| S21 | T1 | Corso, Stärk, Jing, Barzilay & Jaakkola, "DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking" | ICLR 2023 | 2023 | arXiv:2210.01776 | peer-reviewed | https://arxiv.org/abs/2210.01776 | 2026-10-21 |
| S22 | T1 | Watson, Juergens, Bennett, Trippe, Yim, Eisenach, Ahern, Borst, Ragotte, Milles et al., "De novo design of protein structure and function with RFdiffusion" | Nature 620 | 2023 | 10.1038/s41586-023-06415-8 | peer-reviewed | https://www.nature.com/articles/s41586-023-06415-8 | 2026-10-21 |
| S23 | T1 | Abramson, Adler, Dunger et al., "Accurate structure prediction of biomolecular interactions with AlphaFold 3" | Nature 630 | 2024 | 10.1038/s41586-024-07487-w | peer-reviewed | https://www.nature.com/articles/s41586-024-07487-w | 2026-10-21 |
| S24 | T1 | Wang, Elhag, Jaitly, Susskind & Bautista, "Swallowing the Bitter Pill: Simplified Scalable Conformer Generation" (MCF) | ICML 2024 (PMLR 235) | 2024 | arXiv:2311.17932 | peer-reviewed | https://proceedings.mlr.press/v235/wang24q.html | 2026-10-21 |
| S25 | T1 | De Bortoli, Mathieu, Hutchinson, Thornton, Teh & Doucet, "Riemannian Score-Based Generative Modelling" | NeurIPS 2022 | 2022 | arXiv:2202.02763 | peer-reviewed | https://arxiv.org/abs/2202.02763 | 2026-10-21 |
| S26 | T1 | Tashiro, Song, Song & Ermon, "CSDI: Conditional Score-based Diffusion Models for Probabilistic Time Series Imputation" | NeurIPS 2021 | 2021 | arXiv:2107.03502 | peer-reviewed | https://arxiv.org/abs/2107.03502 | 2026-10-21 |
| S27 | T1 | Rasul, Seward, Schuster & Vollgraf, "Autoregressive Denoising Diffusion Models for Multivariate Probabilistic Time Series Forecasting" (TimeGrad) | ICML 2021 (PMLR 139) | 2021 | arXiv:2101.12072 | peer-reviewed | https://proceedings.mlr.press/v139/rasul21a.html | 2026-10-21 |
| S28 | T1 | Kollovieh, Ansari, Bohlke-Schneider, Zschiegner, Wang & Wang, "Predict, Refine, Synthesize: Self-Guiding Diffusion Models for Probabilistic Time Series Forecasting" (TSDiff) | NeurIPS 2023 | 2023 | arXiv:2307.11494 | peer-reviewed | https://arxiv.org/abs/2307.11494 | 2026-10-21 |
| S29 | T3 | Stability AI generative-models, `configs/inference/svd.yaml` at commit 059d8e9 (Stable Video Diffusion's inference config) | — | 2023 | 059d8e9cd9c55aea1ef2ece39abf605efb8b7cc9 | source | https://github.com/Stability-AI/generative-models/blob/059d8e9cd9c55aea1ef2ece39abf605efb8b7cc9/configs/inference/svd.yaml | 2026-10-21 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | survey diffusion models applications video audio molecules | low-tier and very recent surveys (a TechRxiv LLM survey, a 2025 conditional-diffusion survey, a molecule-diffusion preprint, a thesis); none outranks the ACM survey, which this query did not surface but OpenAlex did |
| 2 | 1 | OpenAlex | title.search "diffusion models comprehensive survey methods applications", sort cited_by_count | Yang et al., ACM Computing Surveys 2023, 1,691 citations (S1): the map whose application taxonomy this post owns |
| 3 | 1 | arXiv | 2209.00796 abstract and HTML (v15) | Table 3's six task categories and Section 5's discrete, invariant and manifold structures (L01–L03); arXiv non-exclusive licence, so its Figure 1 taxonomy cannot be reused |
| 4 | 1 | OpenAlex | title.search "survey video diffusion models"; "diffusion models time series survey" | Xing et al. 2024 (ACM CSUR, 134 citations) and Lin et al. 2023 (FITEE, 130); read for orientation, not cited (S2–S8 and S26–S28 carry every claim) |
| 5 | 1 | arXiv | 2209.04747 (Croitoru et al., TPAMI vision survey), 2310.10647 (Xing et al. video survey), full text | confirmed VDM, Make-A-Video, Align your Latents and Imagen Video as the core video line; not cited |
| 6 | 2 | arXiv | full text of 2204.03458, 2304.08818, 2305.10474, 2303.13439, 2311.15127 | factorized space-time U-Net, temporal layers on a frozen image model, correlated noise priors, latent warping (L04–L17) |
| 7 | 3 | arXiv | VDM Tables 4 and 6, Align your Latents Table 3, PYoCo Tables 1 and 5 as HTML tables | FVD and FID numbers with their setups (L05, L07, L10, L14, L16) |
| 8 | 2 | arXiv | full text of 2009.09761, 2009.00713, 2301.12503, 2402.04825, 1812.08466 | DiffWave receptive field, mel and latent sizes, Stable Audio's 32x VAE (L20–L25); WaveGrad and FAD read, not cited (DiffWave covers vocoding; no FAD number is quoted) |
| 9 | 2 | arXiv | full text of 2103.01458, 2104.03670, 2212.08751, 2209.14988, 2305.16213, 2308.16512 | points as i.i.d. particles, PVD completion, Point-E without positional encodings, SDS and its failure modes, VSD, the Janus problem (L26–L39) |
| 10 | 2 | arXiv | full text of 2203.17003, 2203.02923, 2206.01729, 2210.01776, 2311.17932, 2102.09844, 2202.02763 | zero centre of gravity, one-hot atom types, the invariance proposition, torsions on a torus, product-space docking, non-equivariant scaling, compact-manifold priors (L40–L56) |
| 11 | 2 | Nature | s41586-023-06415-8 (RFdiffusion) and s41586-024-07487-w (AlphaFold 3) article pages | frames with Brownian motion on rotations (L51); a diffusion module with no equivariant processing (L53); both CC BY 4.0 |
| 12 | 2 | arXiv | full text of 2107.03502, 2101.12072, 2307.11494 | conditional vs replacement imputation with CRPS, autoregressive forecasting, self-guidance (L57–L63) |
| 13 | 1 | OpenAlex | batch title.search of 22 sources | CVPR/ICCV DOIs for S3, S4, S5, S12, S13; Nature DOIs; ICLR, ICML and NeurIPS papers listed only as arXiv, so confirmed below |
| 14 | 1 | DBLP | search API, "DreamFusion Text-to-3D" | Anubis bot wall ("Making sure you're not a bot"); nothing returned; not retried |
| 15 | 1 | Semantic Scholar | paper API, arXiv:2209.14988 | HTTP 429 for the session |
| 16 | 1 | PMLR | volume indexes v139, v162, v202, v235 | ICML pages for EGNN and TimeGrad (2021), EDM (2022), AudioLDM (2023), Stable Audio and MCF (2024) |
| 17 | 1 | NeurIPS proceedings | papers.nips.cc 2021, 2022, 2023 indexes | CSDI (2021), Torsional Diffusion, RSGM and VDM (2022), ProlificDreamer and TSDiff (2023) |
| 18 | 1 | ICLR proceedings, iclr.cc, OpenReview API | proceedings.iclr.cc 2021–2024; iclr.cc/virtual/{2021,2022,2023}/papers.html; api.openreview.net notes search | MVDream in ICLR 2024 proceedings; DiffWave and WaveGrad (2021), GeoDiff (2022), DreamFusion and DiffDock (2023) on the ICLR virtual sites; the OpenReview API returned DreamFusion's ICLR 2023 submission |
| 19 | 1 | OpenAlex | forward chase: works citing VDM (W4226057201) with "noise" in the title | a CVPR 2024 noise-prior line (motion priors by optimizing noise, RAVE noise shuffling, TRIP) and Blue noise (SIGGRAPH 2024); pointed to noise warping as the live correction to fixed noise |
| 20 | 1 | arXiv | API title search "warped your noise" | Chang et al., ICLR 2024 oral (S7): interpolated noise loses variance; fixed noise sticks to the screen |
| 21 | 1 | OpenAlex | forward chase: works citing EDM (W4226070784) with "equivariant" or "scalable" in the title | applications of equivariant diffusion (co-design, catalysts, docking); no retraction or failed replication |
| 22 | 4 | Nature | AlphaFold 3 reference list | ref. 34 is MCF's preprint, the work AF3 follows in dropping equivariance (S23 to S24, backward chase) |
| 23 | 4 | arXiv | MCF Section 5.4 | the canonical-frame experiment that qualifies the non-equivariant result (L55) |
| 24 | 1 | Crossref | ACM survey DOI metadata; FAD bibliographic query | ACM CSUR 56(4), 2023 for S1; Interspeech 2019 DOI for FAD (not cited) |
| 25 | 5 | GitHub | Stability-AI/stablediffusion (404, repository gone); Stability-AI/generative-models `configs/inference/svd.yaml`, commit from the file's atom feed | SVD's autoencoder: 4 latent channels, ch_mult [1, 2, 4, 4], so 8x per side (S29, L13) |
| 26 | 1 | arXiv | MVDream 2308.16512v4 PDF, page 2; licence on the abstract page | Figure 1 (Janus and content drift) is the published composite; CC BY 4.0 (F1) |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | The ACM survey groups diffusion applications by task into six categories: computer vision, natural language generation, temporal data modelling, multi-modal learning, robust learning, and interdisciplinary applications; video and point clouds sit under vision, time series and waveforms under temporal data, text-to-3-D, text-to-video and text-to-audio under multi-modal, molecules under interdisciplinary | S1 §7, Table 3 | arXiv v15 table; the 2023 journal version has the same six categories |
| L02 | The same survey sorts methods for data with special structure into three classes: discrete data, data with invariant structure (graphs permutation-invariant, point clouds translation- and rotation-invariant), and data on manifolds, known (spheres, tori) or learned (an autoencoder's latent space, as in latent diffusion) | S1 §5.1–5.3 | — |
| L03 | The survey notes that ignoring a data domain's invariances in a diffusion model can lead to suboptimal performance | S1 §5.2 | stated as a general observation, not measured there |
| L04 | Video Diffusion Models factorizes a 3-D U-Net over space and time: each 3x3 convolution becomes 1x3x3 (space only), spatial attention treats frames as a batch, and a temporal attention block after each spatial one attends across frames with positions as the batch, using relative position embeddings for frame order | S2 §3 | — |
| L05 | Masking the temporal attention lets VDM train on independent images as well as videos; adding 8 independent images per 16-frame video improved FVD from 202.28 to 57.84 | S2 §4.3.1, Table 4 | text-conditioned 16x64x64 videos, 4,096 samples, FVD against the training set (validation set: 205.42 to 60.72) |
| L06 | VDM found that replacement conditioning (forward-noised observed frames swapped in at each step) gave new frames that looked good alone but were often incoherent with the given frames, because it uses E[x^b given z_t] where E[x^b given z_t and x^a] is needed; the missing term is a gradient of log q(x^a given z_t), which their reconstruction guidance approximates | S2 §3.1 | assumes a perfect denoiser for the exactness argument |
| L07 | Extending 16-frame models to 64 frames, VDM measured FVD 451.45 with replacement against 136.22 with reconstruction guidance | S2 Table 6 | 64x64x64 videos, guidance weight 2.0, FVD against the training set, 4,096 samples |
| L08 | VDM trains on short clips (for example 16 frames) to fit memory, though real videos have hundreds to thousands of frames at 24 fps or more | S2 §3.1 | — |
| L09 | Align your Latents inserts temporal layers (temporal attention and 3-D-convolution residual blocks) between the frozen spatial layers of a pre-trained image latent diffusion model and trains only the temporal layers; the spatial layers treat the frames as a batch of independent images | S3 §3.1 | — |
| L10 | In Align your Latents, upsampling each frame independently with an image upsampler scored FVD 165.98 and FID 19.71, the video-fine-tuned upsampler FVD 45.39 and FID 19.85: frame quality the same, temporal consistency lost | S3 §4.1, Table 3 | in-house real driving scene (RDS) data, 4x pixel-space upsampler conditioned on 128x256 30 fps ground-truth videos |
| L12 | Stable Video Diffusion follows Align your Latents: temporal convolution and attention after every spatial layer of Stable Diffusion 2.1, 656M new parameters for 1,521M in total; it is fine-tuned at 576x1024 into 14- and 25-frame models | S6 §3–4, App. D | preprint |
| L13 | SVD's autoencoder has 4 latent channels and four resolution levels (ch_mult [1, 2, 4, 4]), so it halves each side three times: 8x per side; its video U-Net takes 8 input channels (the noisy latent plus the conditioning frame's latent, concatenated) and outputs 4 | S29; S6 App. D | inference config; the factor follows from three downsampling steps between four levels |
| L14 | Inverting real video frames to noise one frame at a time with an image diffusion model gives noise maps whose average pairwise cosine similarity is 0.206 (± 0.156) within a video against 0.001 (± 0.009) across videos | S4 §3, Table 1 | PYoCo's text-to-image model, diffusion ODE run from sigma 0 to sigma max |
| L15 | PYoCo's mixed noise model gives every frame a shared noise of variance a²/(1+a²) plus its own of variance 1/(1+a²) (a their alpha); a → infinity gives identical noise and a frozen video, a = 0 gives i.i.d. noise | S4 §3, eq. 3 | — |
| L16 | Fine-tuning an image model to video on UCF-101, PYoCo measured FVD 566.67 with i.i.d. noise, 337.40 with mixed noise and 339.67 with progressive noise; training from scratch gave 903.37 | S4 §5.3, Table 5 | UCF-101; IS and frame FID move the same way (41.25 to 52.71; 56.43 to 31.57) |
| L17 | Text2Video-Zero reports that sampling frames from independent noise with an image model gives unrelated images that share only the prompt; it builds frame k's starting latent from frame 1's (after some DDIM steps), translated by a global motion vector proportional to k − 1 and re-noised, and adds cross-frame attention on the first frame | S5 §3.3 | zero-shot, Stable Diffusion, no training |
| L18 | How I Warped Your Noise: reusing fixed noise across frames causes texture-sticking; warping noise by linear interpolation of a sub-pixel shift a gives values with variance a² + (1 − a)², below one for 0 < a < 1 (one half at a = 0.5); their integral noise keeps unit variance | S7 §1, §3 (1-D toy) | — |
| L19 | FVD computes the Fréchet distance on features of an I3D network trained for action recognition on Kinetics, over whole videos, so it responds to temporal as well as per-frame defects | S8 §3 | preprint |
| L20 | One second of speech at 16 kHz is 16,000 samples, a sequence long enough that unconditional autoregressive waveform models produce word-like babble | S9 §1 | — |
| L21 | DiffWave's denoiser is a stack of bidirectional dilated convolutions (kernel 3, dilation doubling within a block); its receptive field r = (k − 1) times the sum of dilations plus 1 is 6,139 samples for 30 layers with dilation cycle 1 to 512, only 0.38 s at 16 kHz; running T reverse steps lets the effective receptive field grow to T times r | S9 §3.1, §3.3 | — |
| L22 | DiffWave as a mel-spectrogram vocoder matched a strong WaveNet vocoder in listener ratings (MOS 4.44 vs 4.43) while synthesizing far faster | S9 §1 | 22.05 kHz speech (LJ Speech) |
| L23 | AudioLDM resamples audio to 16 kHz mono 10 s clips, computes 64-band mel spectrograms (window 1,024, hop 160), compresses them with a VAE by r in time and frequency into C channels (r = 4 with C = 8 by default), runs latent diffusion there, and turns the decoded mel back into a waveform with a HiFi-GAN vocoder | S10 §3, App. D–E | — |
| L24 | Stable Audio's VAE downsamples 44.1 kHz stereo by 1,024 in time into 64 channels (2 x L to 64 x L/1024), a 32x compression; its training window is 4,194,304 samples (95.1 s), and it renders 95 s in 8 s on one A100 | S11 §3 | — |
| L25 | Diffusion on magnitude spectrograms needs an extra step to render a waveform, since the magnitude drops phase | S11 §2 | — |
| L26 | Luo and Hu treat a point cloud's points as particles diffusing in a heat bath and model each point as an independent draw given a shape latent, so the cloud's probability is a product over points | S12 §3 | — |
| L27 | Early point-cloud generators treated a cloud as an N x 3 matrix with a fixed point count, turning it into matrix generation | S12 §2 | — |
| L28 | PVD diffuses point coordinates directly with a point-voxel network, using 2,048 points per ShapeNet shape (airplane, chair, car); for completion it keeps the partial shape fixed in both forward and reverse processes and denoises only the missing points | S13 §3.2, §4 | — |
| L29 | Point-E represents a cloud as a K x 6 tensor (xyz and RGB, scaled to −1..1), denoised by a transformer without positional encodings, so the model is permutation-invariant to the input points (output order follows input order); it makes 1,024 points then upsamples to 4,096, conditioned on a synthetic view from a 3B-parameter GLIDE model | S14 §4.3–4.4 | preprint |
| L30 | DreamFusion optimizes a randomly initialized NeRF per prompt so that its renders score well under a frozen 2-D text-to-image diffusion model, using no 3-D data | S15 §1, §3 | Imagen 64x64 base model |
| L31 | DreamFusion's score distillation sampling (SDS) gradient is the expected weighted noise residual (predicted noise minus injected noise) times the render's Jacobian, dropping the U-Net Jacobian | S15 §2, eq. 3 | — |
| L32 | DreamFusion uses guidance weight omega = 100 (predicted noise = (1 + omega) conditional − omega unconditional), far above the 5 to 30 used for image sampling, because small weights oversmooth under SDS's mode-seeking objective | S15 §3.2, App. A | omega = w − 1 in this series' convention, so w = 101 |
| L33 | DreamFusion reports that SDS often gives oversaturated and oversmoothed results compared with ancestral sampling, lacks diversity, and gives 3-D results that differ little across seeds, which it attributes to the mode-seeking reverse KL | S15 §5 | — |
| L34 | DreamFusion appends view text ("front view", "side view", "back view", "overhead view") chosen from the sampled camera angle | S15 §3.2 | — |
| L35 | DreamFusion renders at 64x64 and runs 15,000 iterations, about 1.5 hours on a 4-chip TPUv4 | S15 §3.2 | — |
| L36 | ProlificDreamer shows SDS is variational score distillation with a single-point (Dirac) variational distribution, which explains its limited diversity | S16 §3.3 | — |
| L37 | With the renderer set to the identity (pure 2-D), ProlificDreamer found SDS poor at guidance 7.5 and oversaturated at 100, while VSD at 7.5 matched ancestral sampling | S16 §3.3, Fig. 3 | Stable Diffusion prior |
| L38 | 2-D-lifting text-to-3-D methods suffer the multi-face Janus problem (the prompt's subject regenerated on several sides) and content drift across views | S17 §1, Fig. 1 | — |
| L39 | MVDream trains a multi-view diffusion model that inflates the image model's 2-D self-attention to 3-D across views and adds camera embeddings, on rendered 3-D data (Objaverse) plus LAION images, in the manner of video diffusion models | S17 §3.1 | — |
| L40 | EDM diffuses atom coordinates and atom types together and denoises with an E(3)-equivariant graph network (EGNN) | S18 §1, §3 | — |
| L41 | No non-zero distribution on all of space can be translation-invariant (it cannot integrate to one), so EDM keeps positions on the subspace where the centre of gravity is zero, subtracting the centre of gravity from sampled and predicted noise | S18 §3.1, Alg. 1–2 | — |
| L42 | EDM diffuses atom types as one-hot vectors with Gaussian noise and integer charges as ordinal values | S18 §3.2 | — |
| L43 | QM9 holds about 130k small molecules with up to 9 heavy atoms (29 atoms counting hydrogens) of types H, C, N, O and F | S18 §5.1 | — |
| L44 | On QM9, the same diffusion setup gave molecule stability 63.2% with a non-equivariant network (GDM), 71.6% with that network trained on randomly rotated data (GDM-aug) and 82.0% (± 0.4) equivariant (EDM); atom stability 97.0, 97.6 and 98.7%; training data 95.2% and 99.0% | S18 Table 1 | 10,000 samples per model, 3 runs; all models 9 layers, 256 features |
| L45 | A Markov chain started from an invariant prior with equivariant transition kernels has an invariant marginal, so an invariant noise prior plus an equivariant denoiser gives samples whose distribution is rotation- and translation-invariant | S19 §4.2 (Prop. 1); S18 §2 | GeoDiff works on centre-of-mass-free coordinates |
| L46 | GEOM-DRUGS molecules have on average 44 atoms (132 Cartesian coordinates) but only 7.9 torsion angles, and torsion angles live on a torus, not a line | S20 §1 | — |
| L47 | Torsional diffusion uses noise from 0.01 pi to pi; because the torus is compact its prior is the uniform distribution, not a Gaussian; its perturbation kernel is a wrapped normal, sampled as an ordinary normal taken mod 2 pi | S20 §3.1 | — |
| L48 | Torsional diffusion needs 20 denoising steps (and already beats GeoDiff with 5) where the Euclidean GeoDiff used 5,000 | S20 §4 | GEOM-DRUGS |
| L49 | DiffDock diffuses a ligand pose over an (m + 6)-dimensional space: 3 translations, 3 rotations and m torsion angles | S21 §3 | — |
| L51 | RFdiffusion represents each residue as a frame (C-alpha position plus N-C-alpha-C orientation), noising positions with 3-D Gaussian noise and orientations with Brownian motion on rotation matrices, for up to 200 steps, fine-tuning RoseTTAFold as the denoiser | S22 | — |
| L53 | AlphaFold 3's diffusion module works on raw atom coordinates with no rotational frames or equivariant processing; its authors found no invariance or equivariance to global rotations and translations was needed in the architecture | S23 | — |
| L54 | MCF, a non-equivariant transformer (PerceiverIO, 13M to 242M parameters) diffusing atom coordinates directly, outperformed equivariant and torsional baselines on GEOM conformer generation, and its authors argue equivariance can be traded for scale | S24 §1, §5 | GEOM-QM9 and GEOM-DRUGS |
| L55 | MCF found that rotating each training conformer once at random hurt, suggesting GEOM's data share a canonical frame; random rotation every epoch cost a little recall, and a larger model recovered most of the gap | S24 §5.4, Fig. 5 | GEOM-QM9 |
| L56 | Diffusion extends to compact Riemannian manifolds such as spheres and tori, where the natural noise endpoint is the uniform distribution and sampling uses geodesic random walks | S25 §3–4 | compactness assumed |
| L57 | CSDI trains a conditional diffusion model for imputation self-supervised, by hiding some observed values as targets; for forecasting it hides the future time points | S26 §4 | — |
| L58 | CSDI's denoiser alternates a temporal transformer (across the L time steps) and a feature transformer (across the K features) | S26 §4 (Fig. 3) | — |
| L59 | CSDI's CRPS for probabilistic imputation was 0.238, 0.330 and 0.522 at 10, 50 and 90% missing on a healthcare dataset against 0.360, 0.458 and 0.671 for imputation with an unconditional diffusion model; 0.108 against 0.135 on air quality | S26 §6.1, Table 2 | 5 trials, 100 samples per missing value |
| L60 | CSDI's unconditional baseline imputes by feeding forward-noised observed values in place of the observations at each step, which the authors say can harm the information in them | S26 §3.3, App. C.1 | — |
| L61 | CRPS (continuous ranked probability score) measures how compatible a predicted distribution is with the observed value; lower is better | S26 §6.1 | — |
| L62 | TimeGrad forecasts autoregressively: a recurrent network summarizes the past and a conditional diffusion model samples the next time step's multivariate vector from that summary | S27 §3 | — |
| L63 | TSDiff conditions an unconditionally trained time-series diffusion model at inference with observation self-guidance and is competitive with task-specific conditional forecasters | S28 §1, §5 | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S17 | Figure 1 (multi-face Janus problem; content drift) | 3-D without 3-D data / L38 | a horse with two faces shows the failure in one glance; prose cannot | CC BY 4.0 (arXiv record, v4) | https://arxiv.org/abs/2308.16512 | reuse unchanged, cropped from the v4 PDF page 2 |
| F2 | S4 | Figure 2 (t-SNE of inverted noise maps) | video / L14 | shows same-video noise maps cluster; Table 1's two numbers carry the point | CC BY 4.0 | https://arxiv.org/abs/2305.10474 | do not reuse: the lab's figure shows the consequence, the numbers carry the evidence |
| F3 | S24 | Figure 5 (rotation strategies on GEOM-QM9) | molecules / L55 | evidence for the canonical-frame finding | CC BY 4.0 | https://arxiv.org/abs/2311.17932 | do not reuse: one sentence carries it, and the section already has a figure |
| F4 | S19 | Figure 1 (forward and reverse process on a molecule) | molecules / L45 | merely illustrative | CC BY 4.0 | https://arxiv.org/abs/2203.02923 | do not reuse: adjacent, not necessary |
| F5 | S2, S3, S15, S16 | VDM Fig. 1, Align your Latents Figs. 2–4, DreamFusion Fig. 3, ProlificDreamer Fig. 3 | video architecture, SDS | each directly relevant | arXiv non-exclusive licence only | — | do not reuse; the post draws its own figures from its lab and the papers' stated shapes |

## Open questions

- No source reports a per-frame image model's clip coherence as a number; the post measures it in
  crescent world and quotes Align your Latents' FVD/FID pair as the real-model evidence.
- Whether equivariance or augmentation wins at scale is contested (L44 against L53–L55); the post states
  both sides with their settings and does not choose.
- No published FVD, FAD or CRPS value is compared across papers; every quoted score stays inside its own
  table, as part 9 requires.
