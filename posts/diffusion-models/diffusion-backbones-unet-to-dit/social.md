---
social_schema: 2
canonical_url: "https://canery.in/blogs/diffusion-backbones-unet-to-dit"
---

# Social publishing package — diffusion-backbones-unet-to-dit

## LinkedIn post

Two DiT-XL diffusion models have the same 675M parameters. One costs 29.04 GMAC per call, the other 118.62, and the second reaches FID 19.47 where the first reaches 43.01. The only difference is the patch size.

That is the pattern across diffusion backbones: the parameter count tells you what you store, not what you compute.

→ Stable Diffusion 1.5's U-Net keeps 84% of its 860M parameters at its 16×16 and 8×8 levels, but spends 38% of its 803 GFLOP per call at 64×64, where attention compares 4,096 positions.
→ DiT patchifies once and keeps the token count fixed through 28 blocks. Halving the patch from 4 to 2 quadruples the tokens and multiplies compute by 4.08 at the same size.
→ SD3's 2B MM-DiT gives text its own stream of weights. That stream holds 49% of the parameters and does 2.4% of the arithmetic at 1024×1024.
→ For any standard transformer block, attention's share of the FLOPs is N/(N+6D): a third at N = 3D, half at N = 6D.
→ Memory has four parts. SD3's T5 text encoder alone needs 19.05 GB to load, nearly five times the 2B denoiser's weights.

Every count in the article is measured: a CPU-only lab builds the real architectures on PyTorch's meta device and counts every shape, parameter and FLOP. You can run it on a laptop.

Part 4 of the Diffusion Models series.

## LinkedIn first comment

Count tokens before parameters: the patch size and the resolution decide what a diffusion backbone costs.

Read the full article on Canery: https://canery.in/blogs/diffusion-backbones-unet-to-dit

## Instagram caption

Two diffusion transformers, the same 675M parameters, 4.08 times the compute apart. The patch size did it.

Swipe through part 1's noisy patch shrunk two ways, Stable Diffusion 1.5's U-Net level by level, SD3's two streams, the one-line rule for when attention takes over, and what the naive way of computing attention does to memory.

Every number was measured in a lab you can run on a laptop CPU, or is quoted from its paper with the setup.

Link in bio.

#diffusionmodels #machinelearning #deeplearning #generativeai #transformers #stablediffusion #computervision

## Shared feed order

1. `assets/social/feed-01-count-tokens-not-parameters.png` — DiT-XL/4 against DiT-XL/2: same parameters, 4× the tokens, 4.08× the compute
2. `assets/social/feed-02-two-ways-to-shrink-a-patch.png` — part 1's 4×4 patch pooled by a U-Net and patchified by a DiT
3. `assets/social/feed-03-params-bottom-compute-top.png` — SD 1.5's U-Net per level: share of weights against share of FLOPs
4. `assets/social/feed-04-half-the-weights.png` — SD3's MM-DiT: half the weights in the text stream, 2.4% of the FLOPs
5. `assets/social/feed-05-attention-takes-over.png` — attention's share of a block is N/(N+6D), with measured models on the curve
6. `assets/social/feed-06-same-flops-different-bytes.png` — naive against fused attention at 4,096 tokens: 58× the memory
7. `assets/social/feed-07-read-the-article.png` — the five measured findings and the CTA

## Instagram Story

- CTA: What does a diffusion backbone actually spend? Shapes, FLOPs and memory, block by block — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### Story order

1. `assets/social/story-01-count-tokens-not-parameters.png` — Overlay: Same 675M parameters. 4× the compute.
2. `assets/social/story-02-params-bottom-compute-top.png` — Overlay: The finest level is cheap to store and expensive to run.
3. `assets/social/story-03-attention-takes-over.png` — Overlay: Attention is half the block at N = 6D.
4. `assets/social/story-04-read-the-article.png` — Overlay: The denoiser, block by block. Link above.

## Asset metadata

### feed-01-count-tokens-not-parameters

- File: `assets/social/feed-01-count-tokens-not-parameters.png`
- Title: Count tokens, not parameters
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: the same DiT-XL weights cost four times as much when the patch is halved, and the quality follows the compute
- Technical source: article section "What does DiT's patch size buy?", Figure 6, ledger L16, lab captures (dit)
- Visual structure: Canery lockup and counter; serif headline; two-line deck; two 32×32 latents side by side with orange patch lattices (4×4 left, 2×2 right); under each, the model name and four rows of numbers; takeaway below the rule
- Visible-text transcript: Canery.in · 01 / 07 · Count tokens, not parameters. · Two DiT-XL models with the same 675M parameters. One cuts its latent into 4×4 patches, the other into 2×2. · DiT-XL/4 · patch 4×4 · 64 tokens · 29.04 GMAC per call · FID 43.01 at 400K steps · 675,074,432 parameters · DiT-XL/2 · patch 2×2 · 256 tokens · 118.62 GMAC per call · FID 19.47 at 400K steps · 675,129,632 parameters · Halving the patch quadruples the tokens every block sees: 4.08× the compute, and FID falls from 43.01 to 19.47. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: Two copies of the same noisy latent cut into 4×4 and 2×2 patches, with 64 against 256 tokens and 29.04 against 118.62 GMAC
- Long description: Two identical 32×32 noisy latents of a bright crescent. The left is overlaid with an 8×8 lattice of 4×4 patches, the right with a 16×16 lattice of 2×2 patches. Beneath the left: DiT-XL/4, 64 tokens, 29.04 GMAC per call, FID 43.01 at 400K training steps, 675,074,432 parameters. Beneath the right, in orange: DiT-XL/2, 256 tokens, 118.62 GMAC per call, FID 19.47 at 400K steps, 675,129,632 parameters. Compute and parameters are measured by the article's lab; FID is from the DiT paper's Table 4 (ImageNet 256×256, no guidance). The takeaway: halving the patch quadruples the tokens every block sees, so compute rises 4.08 times while the parameter count stays the same.
- Keywords: DiT, diffusion transformer, patch size, tokens, GMAC, FID, ImageNet, diffusion backbone
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### feed-02-two-ways-to-shrink-a-patch

- File: `assets/social/feed-02-two-ways-to-shrink-a-patch.png`
- Title: Two ways to shrink a patch
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: a U-Net pools and needs a skip to recover what pooling drops; a DiT patchifies and keeps every value in the token's width
- Technical source: article section "Worked example", Figure 2, lab captures (patch)
- Visual structure: headline and deck; the 4×4 patch of values with its four 2×2 blocks outlined in orange on the left; on the right, the pooled 2×2 grid with notes, then the four patch tokens with notes; an orange box stating the pair count
- Visible-text transcript: Canery.in · 02 / 07 · Two ways to shrink a patch. · Part 1's noisy 4×4 patch, made smaller before attention compares every position with every other. · 0.43 1.32 0.03 −1.34 / 1.15 −0.45 −0.59 −0.30 / 1.19 0.26 −1.13 −0.67 / −0.43 0.38 0.19 −1.46 · 16 positions · 256 pairs · U-NET · AVERAGE POOL · 0.6125 −0.5500 / 0.3500 −0.7675 · 4 positions · 12 values gone · a skip keeps them · DIT · PATCHIFY, P = 2 · 0.43 1.32 1.15 −0.45 · 0.03 −1.34 −0.59 −0.30 · 1.19 0.26 −0.43 0.38 · −1.13 −0.67 0.19 −1.46 · 4 tokens · all 16 values kept · in token width · attention pairs: 256 → 16, either way · Pooling throws 12 of 16 values away and needs a skip. Patchifying keeps all 16 in the token's width. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: A 4×4 grid of noisy values pooled into four means and, beside it, cut into four tokens of four values each
- Long description: Part 1's noisy 4×4 patch, values printed in cells shaded so higher values are brighter, with its four 2×2 blocks outlined. Pooling each block gives 0.6125, −0.5500, 0.3500 and −0.7675: four positions, with twelve of the sixteen values gone, which is why a U-Net keeps the original on a skip connection. Patchifying with patch size 2 gives four tokens holding all sixteen values: 0.43, 1.32, 1.15, −0.45; 0.03, −1.34, −0.59, −0.30; 1.19, 0.26, −0.43, 0.38; −1.13, −0.67, 0.19, −1.46. Either way attention compares 16 pairs instead of 256.
- Keywords: U-Net, patchify, average pooling, skip connection, tokens, attention pairs, worked example
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### feed-03-params-bottom-compute-top

- File: `assets/social/feed-03-params-bottom-compute-top.png`
- Title: Parameters at the bottom, compute at the top
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: SD 1.5's U-Net stores its weights where the grid is small and spends its arithmetic where the grid is large
- Technical source: article section "What does a real U-Net do to a tensor?", Figure 5, lab captures (unet levels)
- Visual structure: headline and deck; a colour key; four rows, one per resolution level, each with a weights bar in blue and a FLOPs bar in grey whose attention part is orange
- Visible-text transcript: Canery.in · 03 / 07 · Parameters at the bottom, compute at the top. · Stable Diffusion 1.5's U-Net, measured level by level for one 512×512 image: 860M parameters, 803 GFLOP. · WEIGHTS · FLOPS · OF WHICH ATTENTION COMPARISONS · 64×64 width 320 · 3.4% of weights · 38.2% of FLOPs · 32×32 width 640 · 12.6% of weights · 29.3% of FLOPs · 16×16 width 1,280 · 46.3% of weights · 26.8% of FLOPs · 8×8 + middle width 1,280 · 37.4% of weights · 5.7% of FLOPs · The 64×64 level holds 3.4% of the weights and does 38.2% of the work, mostly attention over 4,096 positions. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: Paired bars per U-Net level: 64×64 holds 3.4% of weights but 38.2% of FLOPs; 16×16 holds 46.3% of weights
- Long description: Four rows for Stable Diffusion 1.5's U-Net levels, measured by the article's lab for one 512×512 image (859.5M parameters, 803.3 GFLOP). 64×64, width 320: 3.4% of the weights, 38.2% of the FLOPs, with a large orange share for attention comparisons. 32×32, width 640: 12.6% and 29.3%. 16×16, width 1,280: 46.3% and 26.8%. 8×8 plus the middle block, width 1,280: 37.4% and 5.7%. Convolution weights grow with the square of the width while their cost grows with the number of positions, so the finest level is cheap to store and expensive to run.
- Keywords: Stable Diffusion 1.5, U-Net, parameters, FLOPs, attention, resolution levels, diffusion backbone
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### feed-04-half-the-weights

- File: `assets/social/feed-04-half-the-weights.png`
- Title: Half the weights, 2.4% of the arithmetic
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: an MM-DiT's text stream costs parameters by width but FLOPs by tokens, and joint attention is almost a third of the call
- Technical source: article section "How does MM-DiT run two streams through one attention?", Figure 9, ledger L25–L27, lab captures (mmdit)
- Visual structure: headline and deck; a stacked bar of parameters split into image stream and text stream; a stacked bar of FLOPs split into image stream, joint attention and a thin text-stream sliver with a leader label; a two-line note on token counts
- Visible-text transcript: Canery.in · 04 / 07 · Half the weights, 2.4% of the arithmetic. · SD3's 2B MM-DiT gives text its own stream of weights. One 1024×1024 call, measured stream by stream. · PARAMETERS · 2.03B · image stream 50.3% · text stream 48.8% · FLOPS PER 1024×1024 CALL · 8,437 GFLOP · image stream 66.0% · joint attention 31.6% · text stream: 2.4% · 4,096 image tokens and 154 text tokens, one joint attention over all 4,250 of them · Weights cost by width; FLOPs cost by tokens. Joint attention over 4,250 tokens is 31.6% of the call. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: Stacked bars for SD3's 2B MM-DiT: the text stream holds 48.8% of parameters but does 2.4% of one call's FLOPs
- Long description: Two stacked bars measured by the article's lab on SD3's MM-DiT at depth 24 (2.03B parameters). Parameters: image stream 50.3%, text stream 48.8%, the rest outside the blocks. FLOPs for one 1024×1024 call (8,437 GFLOP): image stream 66.0%, joint attention comparisons 31.6%, text stream 2.4%. The call has 4,096 image tokens and 154 text tokens, so the two streams have the same weight shapes but the text stream processes about 27 times fewer tokens; one attention runs over all 4,250.
- Keywords: SD3, MM-DiT, Stable Diffusion 3, joint attention, text stream, parameters, FLOPs, transformer
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### feed-05-attention-takes-over

- File: `assets/social/feed-05-attention-takes-over.png`
- Title: Attention's share is N / (N + 6D)
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one closed form predicts when attention dominates a transformer block, and measured models sit on it
- Technical source: article sections "When does attention dominate the bill?" and "The math", Figure 10, lab captures (attention flops, mmdit)
- Visual structure: headline and deck; a curve of attention share against N/D on a log axis with dashed guides at N = 3D and N = 6D; three labelled points, one orange
- Visible-text transcript: Canery.in · 05 / 07 · Attention's share is N / (N + 6D). · N tokens, width D, a standard transformer block with a 4× MLP. Every measured model lands on the same curve. · 80% 60% 40% 20% · DiT-XL at 16,384 tokens · 70.3% · SD3-2B · 1024 px · 31.6% · DiT-XL/2 · 256 px · 3.6% · N = 3D · N = 6D · 0.1 · 1 · 10 · N / D, tokens per unit of width (log scale) · A third at N = 3D, half at N = 6D. The same DiT-XL block is 3.6% attention at 256 px and 70.3% at 2048 px. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: Curve of attention's share of a transformer block rising with tokens per width, through 3.6%, 31.6% and 70.3% measured points
- Long description: A curve of N/(N+6D), attention's share of one transformer block's FLOPs, plotted against N/D on a log axis from 0.03 to 30, with dashed guides where the share is one third (N = 3D) and one half (N = 6D). Measured points from the article's lab: DiT-XL/2 at 256×256 (256 tokens at width 1,152) at 3.6%; SD3-2B for a whole 1024×1024 call (4,250 tokens at width 1,536) at 31.6%; a DiT-XL block at 16,384 tokens, its count at 2048×2048, at 70.3%. Each lies on the closed-form curve.
- Keywords: attention cost, transformer, token count, FLOPs, DiT, SD3, quadratic attention, scaling
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### feed-06-same-flops-different-bytes

- File: `assets/social/feed-06-same-flops-different-bytes.png`
- Title: Same FLOPs, 58× the memory
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: computing attention naively stores the whole score matrix; a fused kernel computes the same result without it
- Technical source: article section "FLOPs are not the whole cost: memory", Figure 11, ledger L35–L36, lab captures (attention cpu)
- Visual structure: headline and deck; two pairs of horizontal bars, time per call and largest allocation, naive in grey and fused in orange; two lines giving the score-matrix arithmetic and the setup
- Visible-text transcript: Canery.in · 06 / 07 · Same FLOPs, 58× the memory. · One 16-head attention layer at 4,096 tokens on a laptop CPU, computed naively and with PyTorch's fused kernel. · TIME PER CALL, 4,096 TOKENS · naive 864 ms · fused 169 ms · LARGEST SINGLE ALLOCATION · naive 1,093 MB · fused 18.9 MB · score matrix: 16 heads × 4,096² × 4 bytes = 1,073.7 MB · fp32, batch 1, AMD Ryzen 7 5825U, 8 threads · The naive path stores the full score matrix. The fused kernel computes the same numbers without ever holding it. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: Bars for one attention layer at 4,096 tokens on a laptop CPU: naive 864 ms and 1,093 MB against fused 169 ms and 18.9 MB
- Long description: One 16-head attention layer with head width 72 at 4,096 tokens, fp32, batch 1, measured on an AMD Ryzen 7 5825U with 8 threads by the article's lab. The naive path, which writes out softmax(QKᵀ/√d)·V, took 864 ms and made a largest single allocation of 1,093 MB: the 16 × 4,096² fp32 score matrix of 1,073.7 MB plus its output. PyTorch's fused scaled_dot_product_attention took 169 ms with a largest allocation of 18.9 MB. Both compute the same arithmetic; the fused kernel never stores the score matrix. CPU times vary between runs and are not GPU times.
- Keywords: attention, FlashAttention, fused kernel, scaled dot product attention, memory, PyTorch, score matrix
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### feed-07-read-the-article

- File: `assets/social/feed-07-read-the-article.png`
- Title: The denoiser, block by block
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the five measured findings in one list, and where to read the full article
- Technical source: Key takeaways; ledger L16, L29; lab captures (unet, dit, mmdit, attention)
- Visual structure: headline and deck; a white panel of five headed findings; takeaway; orange CTA footer with the article URL
- Visible-text transcript: Canery.in · 07 / 07 · The denoiser, block by block. · Shapes, parameters, FLOPs and memory for SD 1.5's U-Net, DiT-XL and SD3's MM-DiT, measured in a lab you can run. · U-Net · SD 1.5 · 84% of the weights at 16² and 8²; 38% of FLOPs at 64² · DiT-XL · patch 4 → 2: ×4 tokens, ×4.08 compute, same 675M · MM-DiT · SD3-2B · text stream: 49% of weights, 2.4% of FLOPs · Attention · share = N / (N + 6D): half at N = 6D · Memory · SD3's T5 encoder alone needs 19.05 GB · Count tokens before parameters when you choose, fine-tune or serve a diffusion model. · READ IT AT CANERY.IN/BLOGS/DIFFUSION-BACKBONES-UNET-TO-DIT
- Alt text: A list of five findings about diffusion backbones, from U-Net weight placement to SD3's T5 memory, with the article link
- Long description: A closing card listing the article's measured findings. SD 1.5's U-Net: 84% of the weights at the 16×16 and 8×8 levels, 38% of the FLOPs at 64×64. DiT-XL: halving the patch from 4 to 2 gives four times the tokens and 4.08 times the compute at the same 675M parameters. SD3's 2B MM-DiT: the text stream holds 49% of the weights and does 2.4% of the FLOPs. Attention: its share of a transformer block is N/(N+6D), half at N = 6D. Memory: SD3's T5 encoder alone needs 19.05 GB to load. The call to action reads: count tokens before parameters when you choose, fine-tune or serve a diffusion model.
- Keywords: diffusion backbone, U-Net, DiT, MM-DiT, attention, memory, Stable Diffusion
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### story-01-count-tokens-not-parameters

- File: `assets/social/story-01-count-tokens-not-parameters.png`
- Title: Count tokens, not parameters
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: the same DiT-XL weights at two patch sizes, recomposed for a vertical frame
- Technical source: article section "What does DiT's patch size buy?", Figure 6, ledger L16, lab captures (dit)
- Visual structure: lockup and counter; serif headline; two-line deck; the two patched latents side by side with their numbers beneath; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Count tokens, not parameters. · Same 675M parameters. 4× the tokens, 4.08× the compute. · DiT-XL/4 · patch 4×4 · 64 tokens · 29.04 GMAC per call · FID 43.01 at 400K steps · 675,074,432 parameters · DiT-XL/2 · patch 2×2 · 256 tokens · 118.62 GMAC per call · FID 19.47 at 400K steps · 675,129,632 parameters · Patch size is a compute dial, not a size dial. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: The same noisy latent cut into 4×4 and 2×2 patches: 64 against 256 tokens at the same 675M parameters
- Long description: Two identical 32×32 noisy latents of a bright crescent, one overlaid with a lattice of 4×4 patches and one with 2×2 patches. DiT-XL/4: 64 tokens, 29.04 GMAC per call, FID 43.01 at 400K steps, 675,074,432 parameters. DiT-XL/2: 256 tokens, 118.62 GMAC, FID 19.47, 675,129,632 parameters. Compute and parameters are measured by the article's lab; FID is the DiT paper's (ImageNet 256×256, no guidance). Patch size changes the compute, not the size.
- Keywords: DiT, patch size, tokens, compute, diffusion transformer, FID
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### story-02-params-bottom-compute-top

- File: `assets/social/story-02-params-bottom-compute-top.png`
- Title: Parameters at the bottom, compute at the top
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: SD 1.5's U-Net per level, weights against FLOPs, in a vertical frame
- Technical source: article section "What does a real U-Net do to a tensor?", Figure 5, lab captures (unet levels)
- Visual structure: lockup and counter; headline; deck; a colour key; four level rows with a weights bar and a FLOPs bar each; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · Parameters at the bottom, compute at the top. · SD 1.5's U-Net, level by level, for one 512×512 image. · WEIGHTS · FLOPS · OF WHICH ATTENTION COMPARISONS · 64×64 width 320 · 3.4% of weights · 38.2% of FLOPs · 32×32 width 640 · 12.6% of weights · 29.3% of FLOPs · 16×16 width 1,280 · 46.3% of weights · 26.8% of FLOPs · 8×8 + middle width 1,280 · 37.4% of weights · 5.7% of FLOPs · The finest level is cheap to store and expensive to run. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: Paired bars for SD 1.5's U-Net levels: 3.4% of weights but 38.2% of FLOPs at 64×64, the reverse at 16×16 and 8×8
- Long description: Stable Diffusion 1.5's U-Net measured per level for one 512×512 image. 64×64: 3.4% of the weights and 38.2% of the FLOPs, much of it attention comparisons. 32×32: 12.6% and 29.3%. 16×16: 46.3% and 26.8%. 8×8 plus the middle block: 37.4% and 5.7%. The finest level is cheap to store and expensive to run.
- Keywords: U-Net, Stable Diffusion 1.5, parameters, FLOPs, attention, levels
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### story-03-attention-takes-over

- File: `assets/social/story-03-attention-takes-over.png`
- Title: Attention's share is N / (N + 6D)
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the closed form for attention's share, with measured points, in a vertical frame
- Technical source: article sections "When does attention dominate the bill?" and "The math", Figure 10, lab captures (attention flops, mmdit)
- Visual structure: lockup and counter; headline; deck; the share curve on a log axis with dashed guides at N = 3D and N = 6D and three labelled points; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Attention's share is N / (N + 6D). · N tokens, width D: half the block at N = 6D. · 80% 60% 40% 20% · 16,384 tokens · 70.3% · SD3-2B · 31.6% · DiT-XL/2 · 256 px · 3.6% · N = 3D · N = 6D · 0.1 · 1 · 10 · N / D, tokens per unit of width (log scale) · Token count, not parameter count, decides when to swap backbones. · DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN
- Alt text: Curve of attention's share of a transformer block against tokens per width, with points at 3.6%, 31.6% and 70.3%
- Long description: The closed form N/(N+6D) for attention's share of a standard transformer block's FLOPs, against N/D on a log axis, with guides at one third (N = 3D) and one half (N = 6D). Measured points: DiT-XL/2 at 256×256 at 3.6%, SD3-2B at 1024×1024 at 31.6%, and a DiT-XL block at 16,384 tokens at 70.3%. The token count, not the parameter count, decides when attention dominates.
- Keywords: attention, transformer, token count, FLOPs, DiT, SD3
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: The denoiser, block by block
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: what the article covers, and where the link is
- Technical source: the article's section list
- Visual structure: lockup and counter; headline; deck; an orange-tinted panel listing five numbered topics; takeaway; orange CTA footer pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · The denoiser, block by block. · Every number measured in a lab you can run. · 1 trace a real U-Net, block by block · 2 DiT at two patch sizes · 3 MM-DiT's two streams, one attention · 4 attention cost against token count · 5 the memory bill, and when to swap · The full article is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: A numbered list of the article's five topics, from tracing a real U-Net to the memory bill, with a pointer to the link sticker
- Long description: The closing Story frame lists what the article covers: a block-by-block trace of a real U-Net, DiT at two patch sizes, MM-DiT's two streams joined by one attention, attention cost against token count, and the memory bill with guidance on when to swap backbones. Every number in the article is measured in a downloadable lab. The footer points to the link sticker above the frame.
- Keywords: diffusion models, U-Net, DiT, MM-DiT, attention, memory
- Canonical URL: https://canery.in/blogs/diffusion-backbones-unet-to-dit
