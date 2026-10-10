# Source ledger — diffusion-backbones-unet-to-dit

Series `diffusion-models`, part 4. Sweep run 2026-10-03. Tier L4, so the floor is 10
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

Every arXiv paper below was downloaded as a PDF (or, where the PDF download truncated, read as the
arXiv HTML or ar5iv rendering) and converted to text in the session scratchpad, so each claim row
was checked against the paper's own section, table or equation. The configs and code rows were
read from the files themselves, at the versions stated.

Numbers the article calls **measured** do not appear here: they come from the post's own lab
(`lab/census.py`, captured in `lab/captures.json` with its provenance line), which builds the real
architectures and counts their shapes, parameters and FLOPs.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Ronneberger, Fischer & Brox, "U-Net: Convolutional Networks for Biomedical Image Segmentation" | MICCAI, LNCS 9351, pp. 234–241 | 2015 | 10.1007/978-3-319-24574-4_28; arXiv:1505.04597 | peer-reviewed | https://doi.org/10.1007/978-3-319-24574-4_28 | 2026-10-03 |
| S02 | T1 | Ho, Jain & Abbeel, "Denoising Diffusion Probabilistic Models" | NeurIPS 33 | 2020 | NeurIPS hash 4c5bcfec8584af0d967f1ab10179ca4b; arXiv:2006.11239 | peer-reviewed | https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html | 2026-10-03 |
| S03 | T1 | Dhariwal & Nichol, "Diffusion Models Beat GANs on Image Synthesis" | NeurIPS 34 | 2021 | NeurIPS hash 49ad23d1ec9fa4bd8d77d02681df5cfa; arXiv:2105.05233 | peer-reviewed | https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html | 2026-10-03 |
| S04 | T1 | Rombach, Blattmann, Lorenz, Esser & Ommer, "High-Resolution Image Synthesis with Latent Diffusion Models" | CVPR, pp. 10684–10695 | 2022 | 10.1109/CVPR52688.2022.01042; arXiv:2112.10752 | peer-reviewed | https://doi.org/10.1109/CVPR52688.2022.01042 | 2026-10-03 |
| S05 | T1 | Podell, English, Lacey, Blattmann, Dockhorn, Müller, Penna & Rombach, "SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis" | ICLR | 2024 | ICLR 2024 proceedings hash 081b08068e4733ae3e7ad019fe8d172f; arXiv:2307.01952 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2024/hash/081b08068e4733ae3e7ad019fe8d172f-Abstract-Conference.html | 2026-10-03 |
| S06 | T1 | Peebles & Xie, "Scalable Diffusion Models with Transformers" | ICCV, pp. 4195–4205 | 2023 | 10.1109/ICCV51070.2023.00387; arXiv:2212.09748 | peer-reviewed | https://doi.org/10.1109/ICCV51070.2023.00387 | 2026-10-03 |
| S07 | T1 | Bao, Nie, Xue, Cao, Li, Su & Zhu, "All are Worth Words: A ViT Backbone for Diffusion Models" | CVPR | 2023 | 10.1109/CVPR52729.2023.02171; arXiv:2209.12152 | peer-reviewed | https://doi.org/10.1109/CVPR52729.2023.02171 | 2026-10-03 |
| S08 | T1 | Esser, Kulal, Blattmann, Entezari, Müller, Saini, Levi, Lorenz, Sauer, Boesel, Podell, Dockhorn, English, Lacey, Goodwin, Marek & Rombach, "Scaling Rectified Flow Transformers for High-Resolution Image Synthesis" | ICML (PMLR v235) | 2024 | pmlr-v235-esser24a; arXiv:2403.03206 | peer-reviewed | https://proceedings.mlr.press/v235/esser24a.html | 2026-10-03 |
| S09 | T1 | Vaswani, Shazeer, Parmar, Uszkoreit, Jones, Gomez, Kaiser & Polosukhin, "Attention Is All You Need" | NeurIPS 30 | 2017 | NeurIPS hash 3f5ee243547dee91fbd053c1c4a845aa; arXiv:1706.03762 | peer-reviewed | https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html | 2026-10-03 |
| S10 | T1 | Dosovitskiy et al., "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale" | ICLR | 2021 | arXiv:2010.11929 | peer-reviewed | https://arxiv.org/abs/2010.11929 | 2026-10-03 |
| S11 | T1 | Dao, Fu, Ermon, Rudra & Ré, "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness" | NeurIPS 35 | 2022 | 10.52202/068431-1189; arXiv:2205.14135 | peer-reviewed | https://arxiv.org/abs/2205.14135 | 2026-10-03 |
| S12 | T1 | Hoogeboom, Heek & Salimans, "simple diffusion: End-to-end diffusion for high resolution images" | ICML (PMLR v202) | 2023 | pmlr-v202-hoogeboom23a; arXiv:2301.11093 | peer-reviewed | https://proceedings.mlr.press/v202/hoogeboom23a.html | 2026-10-03 |
| S13 | T1 | Crowson, Baumann, Birch, Abraham, Kaplan & Shippole, "Scalable High-Resolution Pixel-Space Image Synthesis with Hourglass Diffusion Transformers" | ICML (PMLR v235) | 2024 | pmlr-v235-crowson24a; arXiv:2401.11605 | peer-reviewed | https://proceedings.mlr.press/v235/crowson24a.html | 2026-10-03 |
| S14 | T1 | Chen et al., "PixArt-α: Fast Training of Diffusion Transformer for Photorealistic Text-to-Image Synthesis" | arXiv (venue not confirmed this session) | 2023 | arXiv:2310.00426 | preprint | https://arxiv.org/abs/2310.00426 | 2026-10-03 |
| S15 | T1 | Karras, Aittala, Lehtinen, Hellsten, Aila & Laine, "Analyzing and Improving the Training Dynamics of Diffusion Models" | CVPR | 2024 | 10.1109/CVPR52733.2024.02282; arXiv:2312.02696 | peer-reviewed | https://doi.org/10.1109/CVPR52733.2024.02282 | 2026-10-03 |
| S16 | T1 | Rajbhandari, Rasley, Ruwase & He, "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models" | SC20 | 2020 | 10.1109/SC41405.2020.00024; arXiv:1910.02054 | peer-reviewed | https://doi.org/10.1109/SC41405.2020.00024 | 2026-10-03 |
| S17 | T1 | Korthikanti, Casper, Lym, McAfee, Andersch, Shoeybi & Catanzaro, "Reducing Activation Recomputation in Large Transformer Models" | MLSys 5 | 2023 | MLSys hash 80083951326cf5b35e5100260d64ed81; arXiv:2205.05198 | peer-reviewed | https://proceedings.mlsys.org/paper_files/paper/2023/hash/80083951326cf5b35e5100260d64ed81-Abstract-mlsys2023.html | 2026-10-03 |
| S18 | T1 | Perez, Strub, de Vries, Dumoulin & Courville, "FiLM: Visual Reasoning with a General Conditioning Layer" | AAAI 32 | 2018 | 10.1609/aaai.v32i1.11671; arXiv:1709.07871 | peer-reviewed | https://doi.org/10.1609/aaai.v32i1.11671 | 2026-10-03 |
| S19 | T1 | Tian, Tu, Chen, Hu, Xu & Wang, "U-DiTs: Downsample Tokens in U-Shaped Diffusion Transformers" | NeurIPS 37 | 2024 | 10.52202/079017-1648; arXiv:2405.02730 | peer-reviewed | https://arxiv.org/abs/2405.02730 | 2026-10-03 |
| S20 | T1 | Yan, Gu & Rush, "Diffusion Models Without Attention" | CVPR | 2024 | 10.1109/CVPR52733.2024.00787; arXiv:2311.18257 | peer-reviewed | https://doi.org/10.1109/CVPR52733.2024.00787 | 2026-10-03 |
| S21 | T1 | Ma, Goldstein, Albergo, Boffi, Vanden-Eijnden & Xie, "SiT: Exploring Flow and Diffusion-based Generative Models with Scalable Interpolant Transformers" | ECCV, LNCS | 2024 | 10.1007/978-3-031-72980-5_2; arXiv:2401.08740 | peer-reviewed | https://doi.org/10.1007/978-3-031-72980-5_2 | 2026-10-03 |
| S22 | T1 | Liang et al., "Scaling Laws For Diffusion Transformers" | ICLR (per the paper's own header) | 2026 | arXiv:2410.08184 | peer-reviewed | https://arxiv.org/abs/2410.08184 | 2026-10-03 |
| S23 | T1 | Saharia et al., "Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding" (Imagen) | NeurIPS 35 | 2022 | 10.52202/068431-2643; arXiv:2205.11487 | peer-reviewed | https://arxiv.org/abs/2205.11487 | 2026-10-03 |
| S24 | T1 | Ma, Zhang, Jia, Zhao, Ma, Ma, Liu, Chen, Zhou & Zhou, "Efficient Diffusion Models: A Comprehensive Survey From Principles to Practices" | IEEE TPAMI 47(9), pp. 7506–7525 | 2025 | 10.1109/TPAMI.2025.3569700; arXiv:2410.11795 | peer-reviewed | https://doi.org/10.1109/TPAMI.2025.3569700 | 2026-10-03 |
| S25 | T1 | Ignacio, Shin, Jin, Yoo, Han & Kim, "Revisiting U-Net: a foundational backbone for modern generative AI" | Artificial Intelligence Review 59(2) | 2025 | 10.1007/s10462-025-11450-0 | peer-reviewed | https://doi.org/10.1007/s10462-025-11450-0 | 2026-10-03 |
| S26 | T1 | Black Forest Labs et al., "FLUX.1 Kontext: Flow Matching for In-Context Image Generation and Editing in Latent Space" | arXiv | 2025 | arXiv:2506.15742 | preprint | https://arxiv.org/abs/2506.15742 | 2026-10-03 |
| S27 | T3 | CompVis/stable-diffusion, `configs/stable-diffusion/v1-inference.yaml` (main branch) | — | 2022 | — | source | https://github.com/CompVis/stable-diffusion/blob/main/configs/stable-diffusion/v1-inference.yaml | 2026-10-03 |
| S28 | T3 | stable-diffusion-v1-5, `unet/config.json` (diffusers format) | — | 2022 | — | source | https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/unet/config.json | 2026-10-03 |
| S29 | T3 | facebookresearch/DiT, `models.py` and `README.md` (main branch) | — | 2023 | — | source | https://github.com/facebookresearch/DiT/blob/main/models.py | 2026-10-03 |
| S30 | T3 | Hugging Face diffusers v0.40.0: `unet_2d_condition.py`, `resnet.py`, `transformer_sd3.py`, and `scripts/convert_sd3_to_diffusers.py` | — | 2026 | diffusers==0.40.0 | source | https://github.com/huggingface/diffusers | 2026-10-03 |
| S31 | T2 | PyTorch 2.14 documentation for `torch.nn.functional.scaled_dot_product_attention` and `torch.utils.flop_counter` (docstrings of the installed package) | — | 2026 | torch==2.14.0 | official-docs | https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html | 2026-10-03 |
| S32 | T3 | stabilityai/stable-diffusion-xl-base-1.0, `unet/config.json` | — | 2023 | — | source | https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/unet/config.json | 2026-10-03 |

Twenty-four peer-reviewed sources carry an identifier; S14 (PixArt-α) and S26 (FLUX.1 Kontext)
are preprints, and the post labels them so wherever they are used. S14's venue could not be
confirmed this session (OpenReview served a bot check and the ICLR 2024 proceedings index did not
list it under its arXiv title), so it is carried as a preprint rather than guessed. S22 states its
own venue in its header ("Published as a conference paper at ICLR 2026"); no second database
could confirm it. S25 was read as its OpenAlex abstract only — Springer served a bot wall to the
PDF — and is used for one framing sentence that its abstract states.

**Not carried, and why.** Rabe & Staats, *Self-attention Does Not Need O(n²) Memory*
(arXiv:2112.05682) — downloaded and read, but no venue could be found and S11 carries the same
point peer-reviewed. Wu & He, *Group Normalization* — downloaded, but the post does not explain
GroupNorm beyond naming it, which Part 2 of the series covers. Yang et al.'s ACM CSUR diffusion
survey was re-read for a backbone taxonomy and has none at the depth S24 has, so S24 is the
survey this post leans on. The SD3-Medium and FLUX.1 model cards and configs on Hugging Face are
gated (HTTP 401 without an account), so the SD3 configuration is built from S08's stated
parameterisation plus S30's conversion script, and FLUX is described only from S26.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | diffusion model backbone architecture survey U-Net transformer | S25 (AI Review 2025 U-Net review), S07 (U-ViT), a CMC transformer survey (too broad, not used), medical U-Net reviews (off-topic) |
| 2 | 1 | Google Scholar | diffusion transformer survey | S24 (TPAMI efficient-diffusion survey, has a backbone taxonomy), a diffusion-LM survey (off-topic), a 2026 pixel-space DiT preprint (not used) |
| 3 | 1 | OpenAlex | survey diffusion transformers architecture | Yang et al. ACM CSUR survey (no backbone taxonomy at this depth), general transformer surveys (off-topic) |
| 4 | 1 | Semantic Scholar | survey of diffusion model architectures backbone | HTTP 429 for the whole session — logged as blocked |
| 5 | 1 | OpenAlex | "Revisiting U-Net: a foundational backbone…", "Efficient diffusion models: a comprehensive survey…" | confirmed S25 (AI Review 59(2), OA hybrid) and S24 (TPAMI 47(9), pp. 7506–7525) |
| 6 | 1 | arXiv API | ti:"diffusion transformers" AND ti:survey | no entries returned; the API returned empty for a later metadata query too — treated as rate-limited |
| 7 | 1 | Google Scholar | U-Net vs transformer backbone diffusion token count attention cost scaling | S19 (U-DiT), S06 (DiT, 9,371 citations), S20 (attention-free DiffuSSM), an efficient-scaling DiT preprint (not used) |
| 8 | 2 | arXiv (PDF) | the 28 candidate papers by id | 24 PDFs read in full; DiT, SD3, LDM and ADM PDFs truncated on download and were re-read as ar5iv/arXiv HTML (DiT, SD3, LDM appendix), the CVF open-access PDF (LDM) and the NeurIPS PDF (ADM) |
| 9 | 2 | GitHub / Hugging Face | SD 1.5 U-Net config, CompVis v1 inference config, DiT models.py, SDXL U-Net config, SD3 and FLUX configs | S27, S28, S29, S32 read; SD3-Medium and FLUX.1 configs returned "access restricted" (gated) |
| 10 | 2 | GitHub | diffusers scripts/convert_sd3_to_diffusers.py | S30: SD3 sets heads = depth, patch 2, 16 input channels, joint width 4096, pos-embed size 192 for SD3.0 |
| 11 | 3 | DiT paper (S06) | Table 1, Table 4, §5 | Gflops, params and FID-50K for all 12 configs; XL/2 at 512 = 524.6 Gflops |
| 12 | 3 | SD3 paper (S08) | §4, App. B.2, App. E.1 Table 7 | width 64·d, heads d, 77+77 text tokens, T5 19.05 GB to load |
| 13 | 3 | ZeRO (S16), Korthikanti (S17) | §3.1; §4.1 eq. 1 | 16 bytes/param for mixed-precision Adam; activations s·b·h·(34 + 5as/h) per layer |
| 14 | 1 | OpenAlex | titles of all 25 candidate papers (venue and DOI lookup) | venues and DOIs for S01, S04, S06, S07, S11, S15, S16, S18–S21, S23; DDPM, ADM, SDXL, SD3, simple diffusion, HDiT returned only their arXiv records |
| 15 | 1 | PMLR, NeurIPS, MLSys proceedings | the six papers OpenAlex had only as arXiv records | confirmed S03 (NeurIPS 2021), S08 and S13 (ICML 2024, PMLR v235), S12 (ICML 2023, PMLR v202), S09 (NeurIPS 2017), S17 (MLSys 2023) |
| 16 | 1 | OpenReview | forum pages for SDXL, PixArt-α, ViT | "Verifying your browser" bot check — logged as blocked |
| 17 | 1 | ICLR 2024 proceedings index | SDXL; PixArt-α | SDXL listed (S05 confirmed); PixArt-α not found under its title — S14 kept as preprint |
| 18 | 1 | Google Scholar | SDXL / PixArt-α venue lookups | empty pages (Scholar began refusing the session's requests) — logged as blocked from here |
| 19 | 1 | DBLP | Scalable Diffusion Models with Transformers | Anubis "not a bot" wall — logged as blocked |
| 20 | 1 | OpenAlex (forward) | cites:DiT, sorted by citations | 2,026 citing works, top results applications (medical survey, 4D humans, 3D latents); no correction of DiT's Gflops–FID result |
| 21 | 1 | OpenAlex (forward) | cites:DiT, title contains "transformer" / "backbone" | SiT (S21), PixArt-Σ, Masked Diffusion Transformer, DiffiT, GenTron, a Mamba backbone — S21 carried; the rest are variants, not corrections |
| 22 | 1 | OpenAlex (forward) | cites:SD3 (arXiv record), all and title "transformer" | 92 citing works on that record, none an architecture correction; cross-attention-map analysis of MM-DiT (not used) |
| 23 | 4 | U-DiT (S19), EDM2 (S15), SD3 §5.2.2 (S08) | the disagreement: does the transformer win? | U-DiT beats DiT-XL/2 at 1/6 the compute; EDM2's U-Net set ImageNet-512 records; SD3 found vanilla DiT below UViT on CC12M — the U-Net-vs-DiT question is not settled |
| 24 | 4 | simple diffusion (S12), SD3 (S08) | "U-ViT" name | two different architectures share the name: Bao et al.'s (S07) and Hoogeboom et al.'s (S12); SD3 compares against the latter |
| 25 | 5 | diffusers v0.40.0 source (S30) | `attention_head_dim`, `resnet_time_scale_shift` | SD 1.5's `attention_head_dim: 8` is the head count (a naming error kept for compatibility); SD 1.5 ResNets add time as a per-channel bias |
| 26 | 5 | PyTorch 2.14 (S31) | `scaled_dot_product_attention` docstring | three implementations: FlashAttention-2, memory-efficient attention, and a C++ math path |
| 27 | 6 | Part 2 of this series | backbone sections | framing only: Part 2 already introduces U-Net, DiT, U-ViT, MM-DiT at map depth; this post must go to exact shapes, counts and costs |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | The original U-Net is a contracting path and a roughly symmetric expansive path; each downsampling step doubles channels, and each upsampling step concatenates the matching feature map from the contracting path | S01 §2 | segmentation network, unpadded convolutions with cropping |
| L02 | DDPM's denoiser is the PixelCNN++ U-Net (a Wide-ResNet U-Net) with group normalisation, two residual blocks per resolution, self-attention at 16×16, and time added to every residual block through a sinusoidal embedding; 35.7M parameters for CIFAR-10 and 114M for the 256×256 models | S02 App. B | as trained in the paper |
| L03 | ADM ablated U-Net changes on ImageNet 128: attention at 32, 16 and 8 rather than only 16, more heads, and BigGAN residual up/down-sampling each lowered FID, together by 3.14 at 700K iterations; rescaling residuals by 1/√2 did not help | S03 §3, Table 1 | ImageNet 128×128, FID at 700K and 1200K iterations |
| L04 | ADM settled on 64 channels per attention head, attention at 32, 16 and 8, BigGAN up/down-sampling and adaptive group normalisation; removing AdaGN worsened FID by 2.02 | S03 §3, Tables 2 and 6 | ADM's ablation setup |
| L05 | In latent diffusion, cross-attention takes queries from the flattened U-Net features and keys and values from a condition encoder's output | S04 §3.3 | LDM's conditioning mechanism |
| L06 | LDM found downsampling factors 1–2 train slowly, large factors stall at poor fidelity, and f = 4–8 is the best-behaved regime | S04 §4.1 | ImageNet and CelebA, 2M / 500K steps |
| L07 | SD 1.x's U-Net has 860M parameters, one transformer block at each of four levels and a 768-wide text context; SDXL's has 2.6B, transformer blocks [0, 2, 10], drops the 8× level and uses a 2048-wide context | S05 Table 1, §2.1 | as released |
| L08 | SD 1.5's U-Net config: block widths 320/640/1280/1280, two layers per block, 768-wide cross-attention, a 64×64 latent with 4 channels; the CompVis config gives 8 heads, attention at the first three levels, and latent scale factor 0.18215 | S27, S28 | v1 inference config; v1.5 diffusers config |
| L09 | In diffusers' U-Net, the config key `attention_head_dim` actually sets the number of heads; the library keeps the wrong name because tens of thousands of configs depend on it | S30 `unet_2d_condition.py` | diffusers 0.40.0 |
| L10 | SD 1.5's ResNet blocks add the projected time embedding as a per-channel bias after the first convolution; the alternative `scale_shift` mode splits it into a scale and a shift | S30 `resnet.py` | `resnet_time_scale_shift="default"` |
| L11 | Imagen's Efficient U-Net moves parameters from high-resolution to low-resolution blocks by adding residual blocks there, scales skips by 1/√2, and reorders up/down-sampling to speed up the forward pass | S23 App. B.1 | Imagen's super-resolution models |
| L12 | simple diffusion found it sufficient to scale the U-Net at 16×16, and its "U-ViT" is a U-Net whose low-resolution part is a transformer | S12 §1, §3.3, §3.5 | pixel-space ImageNet |
| L13 | EDM2 keeps ADM's U-Net structure, makes its layers magnitude-preserving, and set record ImageNet-512 FIDs of 1.81 | S15 abstract, §1 | ImageNet-512, latent 64×64×4 |
| L14 | DiT patchifies a latent into (I/p)² tokens; halving p quadruples the tokens and at least quadruples Gflops while barely changing parameters | S06 §3.1 | DiT design |
| L15 | DiT-XL has 28 layers, width 1152 and 16 heads | S06 Table 1 | — |
| L16 | At 400K steps on ImageNet 256 without guidance, DiT-XL/8, /4 and /2 cost 7.39, 29.05 and 118.64 Gflops with 676M, 675M and 675M parameters, and reach FID-50K 106.41, 43.01 and 19.47 | S06 Table 4 | 400K iterations, batch 256, FID-50K, no guidance |
| L17 | DiT-XL/2 at 512×512 processes 1024 tokens at 524.6 Gflops and reaches FID 3.04 | S06 §5.2, Table 4 | 3M iterations, with guidance |
| L18 | Among DiT block designs, in-context, cross-attention, adaLN and adaLN-Zero cost 119.4, 137.6, 118.6 and 118.6 Gflops and reach FID 35.24, 26.14, 25.21 and 19.47 at 400K steps; cross-attention adds about 15% Gflops; adaLN-Zero initialises every block as the identity | S06 §3.2, §5.1, Table 4 | DiT-XL/2, 400K iterations |
| L19 | DiT reports that Gflops, not parameters, track FID: configs with similar Gflops reach similar FID (S/2 and B/4) | S06 §5.1 | ImageNet 256, 400K iterations |
| L20 | DiT-XL/2 reached FID 2.27 on ImageNet 256 with guidance at 118.6 Gflops, against LDM-4 at 103.6, ADM at 1120 and ADM-U at 742 Gflops | S06 §5.2 | class-conditional, cfg, 7M steps |
| L21 | In DiT, more sampling steps do not make up for a smaller model: L/2 at 1000 steps loses to XL/2 at 128 steps (FID-10K 25.9 vs 23.7) | S06 §5.3 | 400K-iteration checkpoints |
| L22 | The official DiT code stores its fixed sine-cosine position embedding as a frozen parameter, regresses six width-sized modulation vectors per block, zero-initialises the modulation and final layers, doubles output channels to learn a variance, and adds one extra label row for classifier-free guidance | S29 `models.py` | main branch |
| L23 | ViT turns an image into N = HW/P² patches, which is the transformer's sequence length | S10 §3.1 | — |
| L24 | A preprint reports that adaLN's linear projections are 27% of the parameters in its DiT-based text-to-image model (which adds a cross-attention layer to every block), replaces them with one shared "adaLN-single", and trains in about 753 A100 GPU-days against 6,250 for SD 1.5 | S14 §2.3, Table 2 | PixArt-α's own model; the lab counts 33% for plain DiT-XL/2, and 6D² of 22D² per block reproduces 27%; GPU-days converted from V100 |
| L25 | MM-DiT gives text and image tokens separate weights, equivalent to two transformers that join their sequences only for attention; it patchifies the latent with 2×2 patches and modulates with the timestep and pooled text vector as DiT does | S08 §4 | SD3 |
| L26 | SD3 sizes its models by depth d: width 64·d, MLP width 4·64·d, d heads; d = 24 is the 2B model and d = 38 the largest (8B) | S08 §4, Fig. 5 caption, §5.3 | — |
| L27 | SD3's text context is 77 CLIP tokens (CLIP-L and CLIP-G hidden states concatenated to 2048 channels, zero-padded to 4096) plus 77 T5-XXL tokens of width 4096; the pooled CLIP vectors give a 2048-wide vector condition | S08 App. B.2, Fig. 2 | as trained |
| L28 | SD3 uses a 16-channel autoencoder with downsampling factor 8 | S08 App. B.2, §5.2.1 | — |
| L29 | Loading SD3's frozen encoders takes 19.05 GB for T5-XXL, 2.78 GB for CLIP-G, 0.49 GB for CLIP-L and 0.14 GB for the VAE encoder | S08 App. E.1, Table 7 | the paper's GPU measurement |
| L30 | On CC12M, SD3 found vanilla DiT (text concatenated, shared weights) below UViT, CrossDiT above UViT, and MM-DiT best; a third weight set gave only a small gain | S08 §5.2.2 | 5.1's experimental setup |
| L31 | SD3 normalises Q and K with RMSNorm in both streams because attention logits grew without bound in the last blocks of a 2B model | S08 §5.3.2, Fig. 5 | — |
| L32 | A preprint describes FLUX.1 as double-stream blocks (separate image and text weights, joint attention) followed by 38 single-stream blocks over the concatenated tokens | S26 §2 | FLUX.1 as described by its authors |
| L33 | diffusers' SD3 conversion sets heads equal to depth, 2×2 patches, 16 input channels, a 4096-wide joint context, and a position grid of 192 for SD3.0 | S30 `convert_sd3_to_diffusers.py` | diffusers 0.40.0 |
| L34 | Self-attention costs O(n²·d) per layer | S09 Table 1 | — |
| L35 | Standard attention's time and memory grow quadratically with sequence length; FlashAttention computes exact attention with memory linear in sequence length and fewer HBM accesses | S11 abstract, §1, §3 | GPU implementation |
| L36 | PyTorch's `scaled_dot_product_attention` has three implementations: FlashAttention-2, memory-efficient attention, and a C++ math path | S31 | torch 2.14 |
| L37 | Mixed-precision Adam holds 2 bytes of fp16 weights, 2 of fp16 gradients and 12 of fp32 weights, momentum and variance per parameter: 16 bytes | S16 §3.1 | without partitioning |
| L38 | A transformer layer keeps s·b·h·(34 + 5·a·s/h) bytes of activations for the backward pass; the 5·a·s²·b part is the attention scores, softmax and dropout | S17 §4.1, eq. 1 | fp16 activations, with dropout, no recomputation |
| L39 | HDiT uses local (neighbourhood) attention at high-resolution levels and global attention only at the lowest, scaling linearly with pixel count | S13 abstract, §3 | pixel-space hourglass transformer |
| L40 | U-ViT treats time, condition and patches all as tokens with long skips between shallow and deep layers; it found the long skips crucial and the CNN's down/up-sampling not always necessary; FID 2.29 on ImageNet 256 and 5.48 on MS-COCO | S07 abstract | class-conditional ImageNet; text-to-image without extra data |
| L41 | U-DiT performs self-attention over downsampled tokens in a U-shape and reports beating DiT-XL/2 with one sixth of its compute | S19 abstract | ImageNet 256 |
| L42 | DiffuSSM replaces attention with a state-space backbone to avoid attention's quadratic cost at high resolution | S20 abstract, §1 | — |
| L43 | SiT keeps DiT's backbone with the exact same structure, parameter count and Gflops, varies the interpolant, objective and sampling, and surpasses DiT at every model size on conditional ImageNet 256×256 and 512×512 (FID-50K 2.06 and 2.62) | S21 abstract | class-conditional ImageNet |
| L44 | DiT pretraining loss follows a power law in compute between 1e17 and 6e18 FLOPs | S22 abstract | text-to-image setting of that paper |
| L45 | A TPAMI survey sorts diffusion backbones into U-shaped (U-Net, U-ViT) and F-shaped (DiT, state-space) denoisers | S24 §3.2, Fig. 5 | — |
| L46 | FiLM conditions a network with a feature-wise affine transform whose scale and shift are predicted from the condition | S18 §2 | — |
| L47 | A 2025 review describes U-Net as adapted from segmentation with normalisation, self- and cross-attention and residual connections, and lists computational efficiency and scalability among its open challenges | S25 abstract | abstract only |
| L48 | SDXL's U-Net config: a 128×128 latent at 1024×1024, widths 320/640/1280, no attention at the 128×128 level, transformer depth 2 at 64×64 and 10 at 32×32, head counts [5, 10, 20] (64 wide each), 2048-wide context | S32 | released config |
| L49 | SD 1.5's transformer block runs self-attention, cross-attention whose keys and values are projected from the 768-wide text tokens to the block width, and a GEGLU feed-forward whose inner width is 4× the block width | S30 `attention.py` (BasicTransformerBlock, FeedForward) | diffusers 0.40.0 |
| L50 | In diffusers' SD3 transformer the last block is built "context pre-only": its text stream supplies keys and values but has no output projection or MLP | S30 `transformer_sd3.py`, `attention.py` (JointTransformerBlock) | diffusers 0.40.0 |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S06 | Figure 3 (DiT architecture and block variants) | What a DiT block is / L18 | shows the four conditioning blocks side by side | DiT paper: arXiv non-exclusive licence; code and weights CC BY-NC — no reuse licence for the figure | https://arxiv.org/abs/2212.09748 | do not reuse; our Figure 7 draws the adaLN-Zero block with measured shapes instead |
| F2 | S08 | Figure 2 (MM-DiT overview and block) | Dual streams / L25 | the canonical MM-DiT picture | arXiv non-exclusive licence only | https://arxiv.org/abs/2403.03206 | do not reuse; our Figure 8 carries the 2B model's real shapes, which the paper's figure does not |
| F3 | S06 | Figure 2 left (Gflops vs FID bubbles) | Two patch sizes / L16, L19 | shows Gflops–FID correlation | no reuse licence | https://arxiv.org/abs/2212.09748 | do not reuse; Figure 6 plots Table 4's numbers, which are facts, with our own reproduction beside them |
| F4 | S01 | Figure 1 (the U-Net) | U-Net lineage / L01 | the original U shape | Springer chapter; arXiv copy without licence | https://arxiv.org/abs/1505.04597 | do not reuse; not needed — Figure 3 traces SD 1.5's real shapes |

## Open questions

- Whether PixArt-α appeared at a venue: not confirmable this session; carried as a preprint.
- SD3-Medium's exact released config is gated. The post builds the d = 24 model from S08's
  parameterisation and S30's conversion script; its 2,028,328,000 parameters match the "2B" the
  paper uses for d = 24, but a released checkpoint could differ in details such as QK-norm (S08's
  RMSNorm option), which adds a few thousand parameters per block.
- DiT's paper does not define its "Gflops" unit. Our reproduction matches its numbers when one
  multiply-add counts once (118.62 vs 118.64), so the post says the paper's Gflops are
  multiply-adds, as a measured inference rather than a quoted fact.
