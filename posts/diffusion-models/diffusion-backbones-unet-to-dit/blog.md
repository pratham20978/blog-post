---
title: "Diffusion Backbones: U-Net to DiT, Block by Block"
slug: diffusion-backbones-unet-to-dit
date: 2026-10-03
updated: 2026-10-03
summary: "SD 1.5's U-Net keeps 84% of its weights at 16×16 and 8×8 but spends compute at 64×64; DiT's patch size buys 4× compute at equal size. Count tokens first."
tags: [machine-learning, diffusion-model, transformer, generative-model, computer-vision, deep-learning]
category: machine-learning
series: diffusion-models
series_position: 4
tier: L4
difficulty: advanced
prerequisites: ["Part 1 of this series", "convolution", "attention", "PyTorch tensor shapes"]
reading_minutes: 39
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/diffusion-backbones-unet-to-dit"
---

![A U-shaped stack of shrinking and growing feature maps beside the noisy crescent patch cut into 2×2 patches and laid out as a strip of tokens](COVER)

> [!NOTE]
> **Insights** — A diffusion backbone is any network that maps a noisy latent, a timestep and a condition to a tensor of the latent's own shape; what separates a U-Net from a DiT is where it spends its arithmetic. Stable Diffusion 1.5's U-Net keeps 84% of its 860M parameters at its two coarsest levels, yet spends 38% of its 803 GFLOPs at the finest, where attention compares 4,096 positions. DiT spends on a token sequence set by its patch size: halving the patch keeps 675M parameters, quadruples tokens and compute, and more than halves FID. A transformer block's attention share is N/(N+6D), so the token count, not the parameter count, decides when to swap.

**Level:** advanced · **You need:** Part 1 of this series (What a Diffusion Model Actually Does), convolution, attention, PyTorch tensor shapes · **Time:** ~39 min

**Jump to:** [worked example](#worked-example) · [a real U-Net](#what-does-a-real-u-net-do-to-a-tensor) · [DiT's patch size](#what-does-dits-patch-size-buy) · [MM-DiT](#how-does-mm-dit-run-two-streams-through-one-attention) · [attention cost](#when-does-attention-dominate-the-bill) · [memory](#how-much-memory-does-a-backbone-need) · [when to swap](#when-should-you-swap-the-backbone) · [math](#the-math) · [implementation](#implementation)

> [!IMPORTANT]
> Every parameter count, tensor shape and FLOP count in this post is **measured**: the lab builds Stable Diffusion 1.5's U-Net from its published config, DiT-XL from its paper's configuration, and SD3's MM-DiT from its paper's sizing rule, then counts them in PyTorch 2.14. Numbers quoted from papers say so and carry their setup. A FLOP here is one multiply or one add, so a multiply-add (a MAC) is 2 FLOPs and 1 GMAC, a billion multiply-adds, is 2 GFLOP; the DiT paper counts a multiply-add once, which is why its "Gflops" are half of ours. Timings are from one laptop CPU and say so.

## Why this matters

A model card says "2B parameters". That number tells you the weights take 4.06 GB in bf16, the 2-byte floating-point format models are usually served in, and very little else you need. It does not tell you how long one denoising call takes, whether 1024×1024 fits on your GPU, or why the same model at twice the resolution costs four to sixteen times as much.

Those answers live in the backbone's shape. Two DiT-XL models with the same 675M parameters differ by a factor of 4.08 in compute, and by 43.01 against 19.47 in FID (Fréchet Inception Distance, a sample-quality score where lower is better), purely because one cuts its input into 4×4 patches and the other into 2×2. <!-- L16 --> SD3's T5-XXL text encoder needs 19.05 GB just to load, nearly five times its 2B denoiser's weights. <!-- L29 --> If you choose, fine-tune or serve these models, the parameter count is the wrong first question.

## The problem

The denoiser has one contract. It takes the noisy latent $x_t$, the timestep $t$ and a condition $c$ such as a text prompt, and returns a tensor of exactly the latent's shape: in Stable Diffusion 1.5's case, an estimate of the noise that was added. Part 1 of this series, What a Diffusion Model Actually Does, shows how one reverse step turns that estimate into a less noisy state. This post is about the network in the middle, which the literature calls the **backbone**: the architecture family that turns that input into that output.

For a 512×512 image, Stable Diffusion's autoencoder hands the backbone a **latent**: a compressed grid with 4 channels at 64×64 positions, so 16,384 numbers. <!-- L08 --> The autoencoder's **downsampling factor** $f = 8$ is why 512 becomes 64; latent diffusion found factors of 4 to 8 the best trade between training speed and fidelity. <!-- L06 -->

Three requirements pull against each other:

- **Every output position needs global context.** The left eye and the right eye of a face must agree. A 3×3 convolution only mixes neighbours, so it reaches the far side of a 64×64 grid only after dozens of layers.
- **Global context is quadratic.** Self-attention reaches every position in one layer by comparing every pair: $4{,}096^2 = 16{,}777{,}216$ comparisons per head per layer at 64×64. Its cost per layer is $O(n^2 \cdot d)$ in sequence length $n$ and width $d$. <!-- L34 -->
- **The call repeats.** The sampler calls the denoiser once per step, tens of times per image, and twice per step when classifier-free guidance runs a conditional and an unconditional pass.

So every backbone must reduce the number of positions before it compares them all, and then get the detail back. There are two families of answer, shown in Figure 1. A **U-Net** shrinks the grid in stages and saves each stage's output to restore detail later. A **diffusion transformer (DiT)** cuts the grid into patches once, treats each patch as a token, and keeps that token count fixed through every layer. A multimodal DiT (**MM-DiT**) does the same with a second sequence of text tokens running beside the image tokens.

![Three panels mapping a C×64×64 latent to a same-shaped prediction: a U-Net pyramid down to 8×8, a DiT strip of 1,024 tokens, and an MM-DiT with image and text strips](FIG_01)

*Figure 1. One contract, three internals. Every backbone returns a tensor of the input latent's shape; they differ in how many positions each layer sees, which is where their cost comes from. Token counts are for a 512×512 image with a 2×2 patch; C is 4 for SD 1.5 and DiT, 16 for SD3.*

The question this post answers is how each family spends its parameters, its arithmetic and its memory, block by block, and when that spending is reason to swap one family for another.

## Worked example

Start with numbers small enough to check by hand. Part 1 of this series noised a 4×4 greyscale patch of a bright crescent to $\bar\alpha_t = 0.64$ and got this $x_t$:

$$
x_t = \begin{bmatrix} 0.43 & 1.32 & 0.03 & -1.34 \\ 1.15 & -0.45 & -0.59 & -0.30 \\ 1.19 & 0.26 & -1.13 & -0.67 \\ -0.43 & 0.38 & 0.19 & -1.46 \end{bmatrix}
$$

Sixteen positions, one channel. Full attention over them compares $16^2 = 256$ pairs. Both backbone families shrink that count, in different ways.

### The U-Net's move: pool, and keep a copy

A U-Net halves the grid. Take the simplest version, averaging each 2×2 block. The top-left block holds 0.43, 1.32, 1.15 and −0.45, whose mean is 0.6125. The other three blocks give −0.55, 0.35 and −0.7675:

$$
\operatorname{pool}(x_t) = \begin{bmatrix} 0.6125 & -0.55 \\ 0.35 & -0.7675 \end{bmatrix}
$$

Four positions remain, so attention would compare 16 pairs instead of 256. But twelve of the sixteen numbers are gone: no function of the four means can recover that the top-left block held both 1.32 and −0.45. A U-Net solves this by keeping the full-resolution tensor aside, on a **skip connection**, and concatenating it back in when the decoder returns to that resolution. Real U-Nets use a learned stride-2 convolution instead of an average, but the information budget is the same: fewer positions, and a saved copy to restore what the reduction dropped.

### The transformer's move: patchify, and keep everything

A DiT **patchifies**: it cuts the grid into $p \times p$ squares and makes each square one **token**, a vector holding all its values. With patch size $p = 2$, the same four blocks become four tokens of length four:

| Token | Values (row-major within the patch) |
|---|---|
| 1 (top-left) | 0.43, 1.32, 1.15, −0.45 |
| 2 (top-right) | 0.03, −1.34, −0.59, −0.30 |
| 3 (bottom-left) | 1.19, 0.26, −0.43, 0.38 |
| 4 (bottom-right) | −1.13, −0.67, 0.19, −1.46 |

Nothing is lost: this is a reshape, and reversing it rebuilds $x_t$ exactly. The 16 numbers moved from the position axis into the token width. Attention now compares $4^2 = 16$ pairs. With $p = 4$ the whole patch is one token of length 16 and there is one pair; with $p = 1$ there are 16 tokens of length 1 and all 256 pairs come back. A learned linear layer then maps each token to the model's working width $D$, which is 1,152 in DiT-XL. <!-- L15 -->

Figure 2 sets the two moves side by side on these values.

![Part 1's 4×4 noisy patch pooled into a 2×2 grid of means beside the same patch cut into four 4-value tokens, with 256, 16 and 16 attention pairs marked](FIG_02)

*Figure 2. The same 16 values shrunk two ways. Pooling leaves four numbers and needs a skip to recover the other twelve; patchifying leaves four tokens that still carry all sixteen. Either way attention compares 16 pairs instead of 256.*

### The same arithmetic on a real latent

Scale the patch up to the 4×64×64 latent of a 512×512 image. Patchifying with $p$ gives $(64/p)^2$ tokens, each of length $4p^2$:

| Patch size $p$ | Tokens $N$ | Token length | Attention pairs per head per layer |
|---:|---:|---:|---:|
| 8 | 64 | 256 | 4,096 |
| 4 | 256 | 64 | 65,536 |
| 2 | 1,024 | 16 | 1,048,576 |
| 1 | 4,096 | 4 | 16,777,216 |

Each halving of $p$ quadruples the tokens and multiplies the pairs by sixteen. DiT's main experiments use 256×256 images, where the latent is 4×32×32. There the lab measures DiT-XL at 7.39 GMAC with $p = 8$ (16 tokens), 29.04 GMAC with $p = 4$ (64 tokens) and 118.62 GMAC with $p = 2$ (256 tokens), while the parameter count barely moves: 675.7M, 675.1M and 675.1M. The paper reports 7.39, 29.05 and 118.64 for the same three. <!-- L16 -->

The U-Net reduces the same 64×64 latent in stages instead. SD 1.5 goes 64×64 → 32×32 → 16×16 → 8×8, so its positions fall 4,096 → 1,024 → 256 → 64, and its channel width rises 320 → 640 → 1,280 → 1,280 on the way down. <!-- L08 --> The rest of this post follows those two tables to where the parameters, FLOPs and bytes actually go.

## Intuition

Two numbers price every layer of either backbone: the number of positions $N$ and the channel width $D$. A convolution, a projection or an MLP touches each position once with a $D \times D$-sized weight, so it costs on the order of $N D^2$. Attention compares positions in pairs, so its comparisons cost on the order of $N^2 D$. Parameters cost $D^2$ per layer and do not depend on $N$ at all.

A U-Net varies $N$ and $D$ against each other: wide where the grid is small, narrow where it is large. A DiT fixes both for its whole depth. That one difference predicts most of what follows: where the U-Net stores its parameters (where $D$ is large), where it spends its arithmetic (where $N$ is large), and why a DiT's cost is set almost entirely by its patch size.

A U-Net behaves like reading a city map at several zoom levels. Street view shows every name but only a few blocks; satellite view shows the whole city and no names; the skip connections pin the street names back onto the satellite view as you zoom in. The analogy breaks at attention. SD 1.5 also runs global attention at street view, so every street compares itself with every other street, and that is exactly where its compute concentrates. A DiT is the opposite reading: the whole city at one zoom, as a list of tiles, where the patch size is the tile size and every layer compares every tile.

## What does a real U-Net do to a tensor?

The original U-Net was a segmentation network: a contracting path that doubled channels at each downsampling, and a mirrored expanding path that concatenated each stage's saved feature map back in. <!-- L01 --> DDPM adopted it as the denoiser, with residual blocks, group normalisation, two blocks per resolution, self-attention at 16×16, and the timestep added inside every residual block. <!-- L02 --> Stable Diffusion's version keeps that skeleton and adds cross-attention to text. Here it is with every shape measured.

### The trace, block by block

The lab builds SD 1.5's U-Net from its published config: block widths 320, 640, 1,280 and 1,280, two layers per block, a 768-wide text context. <!-- L08 --> It has 859,520,964 parameters, matching the 860M that SDXL's paper lists for SD 1.x. <!-- L07 --> A forward hook on every block records what goes in and what comes out for one 512×512 image and a 77-token prompt. Figure 3 draws the trace to scale.

![SD 1.5's U-Net drawn to scale, block width by channels and height by resolution, from 320×64×64 down to 1280×8×8 and back, with all 12 skips and their shapes](FIG_03)

*Figure 3. The measured trace of SD 1.5's U-Net for one 512×512 image. Going down, the grid shrinks fourfold per level while channels grow; coming up, each ResNet block concatenates one of the 12 saved skips, so the decoder's inputs are wider than its outputs.*

Reading it top to bottom:

1. **`conv_in`** lifts the 4-channel latent to 320 channels: 4×64×64 → 320×64×64, with 11,840 parameters.
2. **Down level 0 (64×64, 320 channels)** runs ResNet, transformer, ResNet, transformer, each 320×64×64 in and out, then a stride-2 convolution to 320×32×32. Its transformer blocks attend over $64 \times 64 = 4{,}096$ tokens.
3. **Down level 1 (32×32)** widens to 640 channels in its first ResNet block and attends over 1,024 tokens, then halves to 16×16.
4. **Down level 2 (16×16)** widens to 1,280 and attends over 256 tokens, then halves to 8×8.
5. **Down level 3 (8×8)** has two ResNet blocks and no attention.
6. **The middle block** runs ResNet, transformer, ResNet at 1,280×8×8 and holds 97.0M parameters on its own.
7. **The up path** mirrors it with three ResNet blocks per level instead of two, and each of those blocks first concatenates one saved skip along channels. That is why the first ResNet block at 16×16 on the way up sees 2,560 = 1,280 + 1,280 channels, and the first at 64×64 sees 960 = 640 + 320.
8. **`conv_out`** maps 320 channels back to 4: the output is 4×64×64, the input's shape.

The **skip stack** has 12 tensors: the output of `conv_in`, then on the way down the output of every ResNet-and-transformer pair (or lone ResNet block at 8×8) and of every downsampler. They hold 6,635,520 numbers, 13.3 MB per image in fp16, kept alive from the moment they are pushed until the decoder pops them. The lab also ran the real fp32 model once on the CPU, with random weights, to confirm the hooks: the output came back 4×64×64 after 4.43 seconds.

### Inside one level

Figure 4 opens level 0, the 64×64 stage, to its two kinds of block.

![Flowchart of one SD 1.5 level: a ResNet block with group norm, SiLU, 3×3 convolutions and an added time bias, then a transformer block with self-attention, cross-attention to 77 text tokens and a gated feed-forward](FIG_04)

*Figure 4. One 64×64 stage of SD 1.5. The timestep enters the ResNet block as a per-channel bias; the prompt enters only the transformer block, and only as cross-attention's keys and values.*

A **ResNet block** is the U-Net's local workhorse: group normalisation (which normalises groups of channels within one example, so it does not depend on batch size), a SiLU activation, a 3×3 convolution, the same three again, and an identity path that adds the input back. The **timestep** enters between the two convolutions. A small MLP turns $t$ into a 1,280-wide embedding; each block projects it to its own width and adds it to every position as a per-channel bias. <!-- L10 --> ADM's U-Net instead predicts a scale and a shift from the embedding and applies them after normalisation, a variant it calls adaptive group normalisation (AdaGN); removing AdaGN cost it 2.02 FID. <!-- L04 --> Both are forms of feature-wise modulation, where a condition sets an affine transform of each channel. <!-- L46 -->

A **transformer block** flattens the 320×64×64 map into 4,096 tokens of width 320 and runs three sublayers. **Self-attention** lets every token read every other token: queries, keys and values all come from the image. **Cross-attention** is where the prompt enters: queries come from the 4,096 image tokens, and keys and values are projected from the 77 tokens of its CLIP text encoder, each 768 wide, down to 320. <!-- L05 --> <!-- L49 --> A gated feed-forward layer then widens each token to 1,280 and back. <!-- L49 --> The block reshapes its tokens back into a 320×64×64 map and adds its input.

SD 1.5 splits each attention into 8 **heads**, parallel attentions over slices of the width, so the head widths are 40, 80 and 160 at the three attention levels. <!-- L08 --> Read the config carefully: in diffusers' U-Net, the key `attention_head_dim: 8` is the number of heads, not their width, a naming error the library keeps because tens of thousands of configs depend on it. <!-- L09 -->

### The parameters live at the bottom, the compute at the top

Now count. The lab's FLOP counter attributes every convolution and matrix multiply to the level that ran it, and Figure 5 sets that against where the parameters sit.

![Paired bars per U-Net level: the 64×64 level holds 3.4% of parameters and 38.2% of FLOPs, while the 16×16 level holds 46.3% of parameters and 26.8% of FLOPs](FIG_05)

*Figure 5. Where SD 1.5's U-Net stores its weights and where it spends its arithmetic, per level, for one 512×512 image (803.3 GFLOP in total). The finest level is cheap to store and expensive to run; the two coarsest are the reverse.*

| Level | Grid | Width | Parameters | Share | GFLOP | Share | of which attention comparisons |
|---|---|---:|---:|---:|---:|---:|---:|
| 0 | 64×64 | 320 | 29.3M | 3.4% | 307.1 | 38.2% | 109.4 |
| 1 | 32×32 | 640 | 108.2M | 12.6% | 235.2 | 29.3% | 14.4 |
| 2 | 16×16 | 1,280 | 398.3M | 46.3% | 215.3 | 26.8% | 2.2 |
| 3 + middle | 8×8 | 1,280 | 321.6M | 37.4% | 45.5 | 5.7% | 0.05 |

The inversion follows from the intuition. A 3×3 convolution from $C$ to $C$ channels has $9C^2$ weights wherever it runs, but costs $9C^2$ multiply-adds *per position*. Level 0 has width 320, so its layers are small, but it has 4,096 positions. Level 3 has width 1,280, so each layer has 16 times the weights of a level-0 layer, but only 64 positions. Levels 2 and 3 together hold 84% of the parameters and do 32% of the work.

Attention sharpens the inversion. Of the 126.1 GFLOP that attention spends comparing tokens (the $QK^\top$ products and the weighted sums of values, excluding the projections), 109.4 GFLOP, 87%, happen at level 0, where five self-attention layers each compare 4,096 tokens. The U-Net's design history reads as a negotiation over exactly this. DDPM attended only at 16×16. <!-- L02 --> ADM showed that attending at 32, 16 and 8 lowered FID, alongside more heads and better up/down-sampling. <!-- L03 --> SD 1.x attends at 64, 32 and 16, and once more in its 8×8 middle block. <!-- L08 --> SDXL then removed the transformer from its highest-resolution level "for efficiency", put 2 and 10 transformer blocks at the two lower levels, dropped the 8× level, and grew to 2.6B parameters. <!-- L07 --> <!-- L48 --> Imagen's Efficient U-Net and simple diffusion made the same move by a different route, shifting capacity to low resolution where width is cheap to compute. <!-- L11 --> <!-- L12 --> The U-Net is not a finished design: EDM2 kept ADM's U-Net layout, reworked its layers to preserve activation magnitudes, and set record ImageNet-512 FIDs of 1.81. <!-- L13 -->

## What does DiT's patch size buy?

A DiT removes the pyramid. It patchifies once, adds a fixed sine-cosine position embedding so each token knows where it came from, and then runs 28 transformer blocks of one design, each with its own weights, at a constant $N$ tokens of width 1,152 with 16 heads. <!-- L14 --> <!-- L15 --> <!-- L22 --> After the last block, a linear layer turns each token back into a $p \times p$ patch of noise and variance estimates, and the patches are reassembled into the latent's grid. <!-- L22 --> Vision transformers introduced the patch-to-token step: $N = HW/P^2$ patches become the sequence. <!-- L23 -->

### Two patch sizes, one parameter count

Figure 6 puts DiT-XL/4 and DiT-XL/2 side by side on the same 4×32×32 latent, the 256×256 ImageNet setting of the paper.

![DiT-XL/4 and DiT-XL/2 on the same 32×32 latent: an 8×8 lattice of 64 tokens against a 16×16 lattice of 256, each labelled with parameters, compute and FID](FIG_06)

*Figure 6. Same 675M parameters, four times the tokens, 4.08 times the compute, and less than half the FID. Compute is measured by the lab and matches the paper to within 0.02 GMAC; FID is the paper's, at 400K training steps on ImageNet 256×256 without guidance.*

| | DiT-XL/4 | DiT-XL/2 |
|---|---:|---:|
| Tokens | 64 | 256 |
| Parameters (lab) | 675,074,432 | 675,129,632 |
| GMAC per call (lab) | 29.04 | 118.62 |
| Gflops per call (paper) | 29.05 | 118.64 |
| FID-50K at 400K steps (paper) | 43.01 | 19.47 |

The patch size touches only three things: the patchify layer ($4p^2 \times 1{,}152$ weights), the output layer ($1{,}152 \times 8p^2$), and the frozen position table ($N \times 1{,}152$). Halving $p$ shrinks the first two and grows the third, and the changes nearly cancel: the two models differ by 55,200 parameters out of 675 million. Every one of the 28 blocks is unchanged, so their weights are identical in size, but each block now processes four times as many tokens.

This is the paper's central finding: compute, not parameter count, tracked sample quality. Configurations with similar Gflops reached similar FID even at very different sizes, and DiT-XL/2 at 400K steps beat smaller models given more sampling steps, so test-time compute did not substitute for model compute. <!-- L19 --> <!-- L21 --> With guidance and longer training, DiT-XL/2 reached FID 2.27 on ImageNet 256×256 at 118.6 Gflops, against 1,120 for ADM's pixel-space U-Net. <!-- L20 --> At 512×512 the latent is 64×64, so $p = 2$ gives 1,024 tokens and 524.6 Gflops; the lab measures 524.54 GMAC. <!-- L17 -->

> [!NOTE]
> The lab's counter reports 237.24 GFLOP for DiT-XL/2, within 0.02% of twice the paper's 118.64. The paper does not define its unit, but its numbers match ours only when one multiply-add counts once, so its "Gflops" are multiply-adds. Halve any FLOP count from a tool that counts the multiply and the add separately before comparing it with DiT's table.

### Inside the block: the condition never becomes a token

A DiT block conditions differently from the U-Net. Figure 7 traces one.

![Flowchart of a DiT block with adaLN-Zero: the timestep and class embedding produce six 1152-wide vectors that shift, scale and gate the attention and MLP sublayers of 256 tokens](FIG_07)

*Figure 7. One DiT-XL/2 block. The timestep and class label are summed into one vector, which predicts six modulation vectors; tokens never attend to the condition, they are rescaled by it.*

The timestep embedding and the class embedding are added into one 1,152-wide condition vector. A SiLU and a linear layer turn it into six 1,152-wide vectors: a shift, a scale and a gate for the attention sublayer, and the same three for the MLP. Each sublayer normalises its input with a parameter-free LayerNorm, applies the condition's scale and shift, runs, and is multiplied by the condition's gate before being added back to the residual stream. This is **adaptive LayerNorm (adaLN)**; the "-Zero" means the modulation layer starts at zero, so every gate starts at zero and every block starts as the identity function. <!-- L18 --> <!-- L22 -->

DiT tested four ways to bring the condition in, all on DiT-XL/2 for 400K steps. Appending the condition as two extra tokens cost 119.4 Gflops and reached FID 35.24. A cross-attention layer added about 15% compute, 137.6 Gflops, and reached 26.14. Plain adaLN reached 25.21 at 118.6 Gflops, and adaLN-Zero reached 19.47 at the same cost. <!-- L18 --> Initialising each block as the identity was worth almost 6 FID points on its own.

adaLN is cheap in FLOPs because it runs once per image, not once per token, but it is not cheap in parameters. The lab counts the modulation projections at 223.1M of DiT-XL/2's 675.1M parameters, 33%. A preprint, PixArt-α, reports 27% for its text-to-image DiT, whose blocks also carry cross-attention weights, and replaces the per-block projections with one shared "adaLN-single". <!-- L24 --> The two figures agree once you count widths: adaLN is $6D^2$ of a plain block's $18D^2$, a third, and $6D^2$ of $22D^2$, 27%, once cross-attention adds its $4D^2$. adaLN carries one vector for the whole image, so it suits the timestep and a class label; a prompt of 77 tokens, each meaning something different, needs cross-attention or the joint attention of the next section.

## How does MM-DiT run two streams through one attention?

Stable Diffusion 3 builds on DiT but gives the text its own transformer. Its paper calls the design MM-DiT. <!-- L25 --> The image side is a DiT: a 1024×1024 image becomes a 16×128×128 latent through an autoencoder with 16 channels and the same factor of 8, and 2×2 patches turn that into 64×64 = 4,096 image tokens. <!-- L28 --> The text side is a sequence of 154 tokens: 77 from two CLIP encoders, whose hidden states are concatenated to 2,048 channels and zero-padded to 4,096, plus 77 from a T5-XXL encoder at 4,096 channels. <!-- L27 --> Both sequences are projected to the model's width.

SD3 sizes everything by depth $d$: width $64d$, MLP width $4 \cdot 64d$, and $d$ heads of 64. The 2B model is $d = 24$, so its width is 1,536 with 24 heads; the largest is $d = 38$. <!-- L26 --> The lab builds both through diffusers' SD3 implementation with the settings its conversion script uses for SD3.0, and counts 2,028,328,000 and 8,056,617,792 parameters. <!-- L33 --> Figure 8 opens one block of the 2B model.

![Flowchart of one SD3 MM-DiT block: 4,096 image tokens and 154 text tokens each pass their own modulation and QKV projections, meet in one joint attention over 4,250 tokens, then split into their own output projections and MLPs](FIG_08)

*Figure 8. One block of SD3's 2B MM-DiT at 1024×1024. Each modality has its own weights everywhere except inside attention, where the two sequences are concatenated and every token can read every other.*

Each stream has its own adaLN modulation, driven by one shared condition vector made from the timestep and the pooled CLIP embedding. Each stream also has its own Q, K and V projections. The six projected tensors are concatenated along the sequence, so one attention runs over $4{,}096 + 154 = 4{,}250$ tokens: image tokens read text tokens, text tokens read image tokens, and each reads its own kind. The result is split back, and each stream runs its own output projection and MLP. SD3's paper describes this as two independent transformers that join their sequences only for attention. <!-- L25 --> The last block is cut short: diffusers builds it "context pre-only", because nothing reads the text tokens after the last attention. <!-- L50 -->

This is different from both earlier designs. In SD 1.5's cross-attention, text tokens are fixed inputs: image tokens read them, but the denoiser never updates them. In a plain DiT that concatenates text tokens to image tokens, both modalities share one set of weights. SD3's paper treats that shared-weight DiT as the special case of MM-DiT with one weight set, and on CC12M it found vanilla DiT behind a UViT baseline, the cross-attention variant ahead of it, and MM-DiT best; a third weight set, separating CLIP from T5, added little. <!-- L30 --> It also normalises queries and keys with RMSNorm in both streams, after attention logits grew without bound in the last blocks of a 2B model. <!-- L31 --> FLUX.1, described in a preprint by its authors, runs double-stream blocks of this kind first and then 38 single-stream blocks over the concatenated tokens. <!-- L32 -->

### Half the weights, 2.4% of the arithmetic

The two streams have nearly the same parameter count, but very different costs. Figure 9 shows the split for one 1024×1024 call.

![Two stacked bars for SD3's 2B MM-DiT: parameters split about evenly between image and text streams, while FLOPs are 66% image stream, 31.6% joint attention and 2.4% text stream](FIG_09)

*Figure 9. The text stream holds 989M of the 2.03B parameters and does 2.4% of the 8,437 GFLOP one 1024×1024 call costs. Weights cost by width; arithmetic costs by tokens.*

| Where | Parameters | GFLOP per call | Share of FLOPs |
|---|---:|---:|---:|
| Image stream (all 24 blocks) | 1,019.8M | 5,567.0 | 66.0% |
| Text stream | 989.1M | 203.4 | 2.4% |
| Joint attention comparisons | — | 2,663.4 | 31.6% |
| Embeddings and output, outside the blocks | 19.5M | 3.6 | 0.04% |

Both streams have the same layer shapes, so they have the same number of weights per block; the text stream is 30.7M smaller only because its last block stops after attention. But every linear layer costs per token, and the text stream has 154 tokens against 4,096, so each of its layers does 3.8% of the image stream's arithmetic. The text stream doubles what you store and barely changes what you compute. The joint attention, comparing 4,250 tokens with each other in every block, is almost a third of the call.

## When does attention dominate the bill?

Every number so far has followed one rule, and it fits in one line. In a standard transformer block of width $D$ with a 4× MLP, each token costs $24D^2$ FLOPs in its linear layers, and attention's comparisons cost $4ND$ more per token, so attention's share of the block is $N/(N + 6D)$. The derivation is in [The math](#the-math). Figure 10 plots that share against $N/D$ and puts the measured models on it.

![Curve of attention's share of a transformer block's FLOPs against tokens per unit width, rising through 1/3 at N = 3D and 1/2 at N = 6D, with DiT-XL/2 at 256 and 512 pixels and SD3-2B at 1024 pixels on it](FIG_10)

*Figure 10. Attention's share of a transformer block's FLOPs depends only on tokens per unit of width. Every measured point, from five token counts on a DiT-XL block to SD3-2B at 1024×1024, lies on the closed-form curve.*

| Model and resolution | $N$ | $D$ | $N/(N+6D)$ | Measured |
|---|---:|---:|---:|---:|
| DiT-XL/2, 256×256 | 256 | 1,152 | 3.6% | 3.6% |
| DiT-XL/2, 512×512 | 1,024 | 1,152 | 12.9% | 12.9% |
| SD3-2B, 1024×1024 | 4,250 | 1,536 | 31.6% | 31.6% |
| DiT-XL block, 4,096 tokens | 4,096 | 1,152 | 37.2% | 37.2% |
| DiT-XL block, 16,384 tokens | 16,384 | 1,152 | 70.3% | 70.3% |

The rule says when attention becomes the problem: at a third of the block when $N = 3D$, and half when $N = 6D$, which is 6,912 tokens for DiT-XL and 9,216 for SD3-2B. At DiT's native 256×256, attention is under 4% of the work, and the MLP and projections are the model. Double the image side and $N$ quadruples, so a DiT run at 2048×2048 with $p = 2$ has 16,384 tokens, and attention is 70% of every block. U-Nets met this wall earlier, because they attend at full latent resolution: SD 1.5's level 0 attends over 4,096 tokens at width 320, so $N/D = 12.8$, well past $6D$, which is why 87% of the whole U-Net's attention comparisons happen there.

### FLOPs are not the whole cost: memory

Attention has a second cost that the share does not show. The naive way to compute it materialises the score matrix $QK^\top$, one $N \times N$ table per head, before the softmax. FlashAttention showed that exact attention can be computed in tiles without ever storing that table, with memory linear in $N$ and fewer slow-memory accesses. <!-- L35 --> PyTorch's `scaled_dot_product_attention` dispatches to such fused kernels, FlashAttention-2 or memory-efficient attention, with a C++ math path as the fallback. <!-- L36 --> The lab times one 16-head attention layer at DiT-XL's head width on this laptop's CPU, both ways, and records the largest single allocation each makes. Figure 11 shows the result.

![Two log-scale panels, naive against fused attention on a laptop CPU from 256 to 4,096 tokens: time grows to 864 ms against 169 ms, and the largest allocation to 1,093 MB against 19 MB](FIG_11)

*Figure 11. One 16-head attention layer, fp32, batch 1, on an AMD Ryzen 7 5825U with 8 threads. Both paths do the same arithmetic; the naive one also allocates the full score matrix. CPU timings are illustrative of the ratio, not of GPU speed.*

At 4,096 tokens, the naive path's largest allocation is 1,092.6 MB: the score matrix, $16 \times 4{,}096^2$ fp32 values, plus a little. The fused path's largest is 18.9 MB, 58 times smaller, and it ran in 169 ms against 864 ms. The profiler names the fused operator `_scaled_dot_product_flash_attention_for_cpu`. Both compute the same function, and the lab checks that their outputs agree to within $10^{-4}$. The arithmetic is identical; what differs is how many bytes are written to memory and read back.

## How much memory does a backbone need?

Memory has four parts, and the parameter count prices only the first. The **weights** cost parameters times bytes per parameter. The **training state** replaces the weights with everything training keeps per parameter: mixed-precision Adam holds 2 bytes of half-precision weights, 2 of gradients, and 12 of fp32 master weights, momentum and variance, so 16 bytes per parameter, weights included. <!-- L37 --> The **activations** are the tensors each layer keeps for the backward pass. For a transformer layer, Korthikanti and colleagues count them at $s b h (34 + 5 a s / h)$ bytes for $s$ tokens, batch $b$, width $h$ and $a$ heads; the $5 a s^2 b$ term is the attention scores and softmax. <!-- L38 --> Their count includes dropout masks these models do not use, so read it as an upper estimate. Last, the **frozen encoders** that produce the condition have to fit too.

Figure 12 applies those formulas to the measured parameter counts, per image.

![Stacked bars on one gigabyte scale: what SD 1.5, DiT-XL/2 and SD3-2B with its encoders must load for inference, and per-image training memory split into state, activations and attention scores](FIG_12)

*Figure 12. The memory bill on one scale, computed from measured parameter counts and the formulas above: bf16 weights, the 16-byte-per-parameter training state, and training activations per image with and without stored attention scores. SD3's encoder sizes are the paper's own load measurement.*

| Model | Params | Weights, bf16 | Training state, 16 B/param | Activations per image | …without scores | One layer's scores, fp16 |
|---|---:|---:|---:|---:|---:|---:|
| SD 1.5 U-Net, 512×512 | 0.86B | 1.72 GB | 13.8 GB | — | — | 268.4 MB |
| DiT-XL/2, 256×256 | 0.68B | 1.35 GB | 10.8 GB | 0.43 GB | 0.28 GB | 2.1 MB |
| DiT-XL/2, 512×512 | 0.68B | 1.35 GB | 10.8 GB | 3.47 GB | 1.12 GB | 33.6 MB |
| SD3-2B, 1024×1024 | 2.03B | 4.06 GB | 32.5 GB | 57.3 GB | 5.33 GB | 867.0 MB |
| SD3-8B, 1024×1024 | 8.06B | 16.1 GB | 128.9 GB | 143.8 GB | 13.4 GB | 1,372.8 MB |

Three things stand out. First, for inference the denoiser's weights are often not the largest item: SD3's paper measured 19.05 GB to load T5-XXL, 2.78 GB for CLIP-G, 0.49 GB for CLIP-L and 0.14 GB for the VAE encoder, against 4.06 GB for the 2B denoiser in bf16. <!-- L29 --> Second, materialised attention scores dominate training activations once tokens pass about a thousand: they are 2.35 of DiT-XL/2's 3.47 GB per image at 512×512, and for SD3-2B at 1024×1024 the estimate falls from 57.3 GB to 5.3 GB per image when the scores are not stored, which is what fused attention or recomputing attention in the backward pass buys. Third, inference stores one layer's scores at a time, because each layer frees them before the next: SD 1.5 with a fused kernel never holds its 268 MB tables at all, and without one it holds one layer's 268 MB at a time, 537 MB when guidance batches two passes. The U-Net's 13.3 MB skip stack is small next to any of these.

## When should you swap the backbone?

Swapping a backbone means training from scratch, because a checkpoint, its fine-tunes and its adapters are tied to the layer shapes. So the decision deserves the arithmetic above rather than a trend. Figure 13 places the models measured here on the two axes that decide it.

![Decision map with attention tokens on a log axis and conditioning type on the other, placing SD 1.5, SDXL, DiT-XL/2 at two sizes and SD3-2B either side of the N = 6D line](FIG_13)

*Figure 13. Swap when the token count or the conditioning changes, not when the parameter count does. Each model sits at the largest token count it attends over at its native resolution; the dashed line marks N = 6D for a 1,152-wide transformer, where attention becomes half of every block.*

**Count tokens first.** At your target resolution, $N = (H/8p) \times (W/8p)$ for a latent DiT with factor 8 and patch $p$. If $N$ stays below a few thousand, a uniform transformer spends most of its compute in dense matrix multiplies, which hardware runs well, and DiT's evidence that compute buys quality applies. <!-- L19 --> Liang and colleagues report DiT pretraining loss following a power law in compute across 1e17 to 6e18 FLOPs, which makes that trade plannable. <!-- L44 --> If $N$ passes $6D$, attention dominates, and the hierarchical idea comes back. HDiT runs local neighbourhood attention at high resolution and global attention only at its coarsest level, so its cost grows linearly with pixel count. <!-- L39 --> U-DiT downsamples tokens inside a U-shaped DiT and reports beating DiT-XL/2 at one sixth of the compute. <!-- L41 --> DiffuSSM drops attention for a state-space layer, a sequence layer whose cost grows linearly with length, for the same reason. <!-- L42 -->

**Then match the conditioning.** A timestep and a class label are one vector per image: adaLN is the cheapest and best-tested choice. <!-- L18 --> A prompt is a sequence. Cross-attention, as in SD 1.5 or PixArt-α, lets image tokens read fixed text tokens at little parameter cost. <!-- L05 --> <!-- L24 --> MM-DiT pays roughly double the block parameters for text tokens that are themselves updated, which SD3's comparison found worth it. <!-- L30 -->

**Do not treat the question as settled.** The evidence points both ways. U-ViT, a transformer that keeps the U-Net's long skips, reported that the skips were crucial and the down- and up-sampling were not. <!-- L40 --> EDM2's U-Net set ImageNet-512 records in 2024. <!-- L13 --> SD3's own comparison put a hybrid UViT ahead of vanilla DiT. <!-- L30 --> A TPAMI survey sorts the field into U-shaped denoisers (U-Net, U-ViT) and flat ones (DiT, state-space) rather than declaring a winner, <!-- L45 --> and a 2025 review of U-Net in generative models lists computational efficiency and scalability among its open problems, not as reasons to retire it. <!-- L47 --> SiT kept DiT's structure, parameter count and Gflops exactly, changed the interpolant, objective and sampler, and beat DiT at every model size on ImageNet 256×256 and 512×512. <!-- L43 --> Some of what is credited to backbones belongs to training choices instead.

## The math

Three formulas account for every FLOP in this post. A FLOP counts one multiply or one add, so each multiply-add is 2.

| Symbol | Meaning |
|---|---|
| $k$ | convolution kernel side (3 for SD's ResNet convolutions) |
| $`C_{in}, C_{out}`$ | input and output channels |
| $H, W$ | grid height and width at that layer |
| $N$ | tokens (positions) in an attention or linear layer |
| $D$ | token width |

A convolution and a linear layer cost

$$
F_{conv} = 2 k^2 C_{in} C_{out} H W, \qquad F_{lin} = 2 N D_{in} D_{out}.
$$

Both cost the same per position wherever they run, so their total scales with the grid; their parameter counts, $`k^2 C_{in} C_{out}`$ and $`D_{in} D_{out}`$, do not. One 3×3 convolution at SD 1.5's level 0 costs $2 \cdot 9 \cdot 320^2 \cdot 4{,}096 = 7.55$ GFLOP with 0.92M weights; the same convolution at level 3 with 1,280 channels has 14.7M weights and costs 1.89 GFLOP.

Attention's comparisons, over all heads together, cost

$$
F_{attn} = \underbrace{2N^2 D}_{QK^\top} + \underbrace{2N^2 D}_{\text{softmax}(\cdot)V} = 4 N^2 D.
$$

Splitting $D$ into heads does not change this total, because $h$ heads of width $D/h$ do $h \cdot N^2 \cdot D/h$ multiply-adds per product.

A standard transformer block has a QKV projection ($3D^2$ multiply-adds per token), an output projection ($D^2$) and an MLP of width $4D$ ($8D^2$), so its linear layers cost $2 \cdot 12 D^2 = 24 D^2$ FLOPs per token. Its total and its attention share are

$$
F_{block} = 24 N D^2 + 4 N^2 D, \qquad \frac{4N^2D}{24ND^2 + 4N^2D} = \frac{N}{N + 6D}.
$$

The share depends only on $N/D$: it is 1/3 at $N = 3D$ and 1/2 at $N = 6D$, whatever the width.

Plug in DiT-XL/2 at 256×256, $N = 256$ and $D = 1{,}152$. Per block, $24 \cdot 256 \cdot 1{,}152^2 = 8.154$ GFLOP of linear work and $4 \cdot 256^2 \cdot 1{,}152 = 0.302$ GFLOP of comparisons; across 28 blocks, 236.8 GFLOP. The lab's total is 237.2 GFLOP, the extra 0.5 coming from the adaLN projections, the timestep and label MLPs, and the patchify and output layers. Halved, that is 118.6 GMAC, the paper's number. The comparisons alone, $28 \times 0.302 = 8.456$ GFLOP, match the lab's measured attention total to the last digit. And on the worked example, Part 1's patch with $p = 2$ and no projection has $N = 4$ and $D = 4$, so a block over it would spend $4/(4 + 24) = 14\%$ on attention.

<details>
<summary>The memory formulas</summary>

Weights cost $P \cdot b$ bytes for $P$ parameters at $b$ bytes each, so SD3-2B is $2{,}028{,}328{,}000 \times 2 = 4.06$ GB in bf16. Mixed-precision Adam costs $16P$, so 32.5 GB. One layer's attention scores, stored in fp16 for $h$ heads, cost $2hN^2$ bytes: $2 \cdot 24 \cdot 4{,}250^2 = 867.0$ MB for SD3-2B at 1024×1024. Korthikanti's per-layer activation count, with batch 1, is $N D (34 + 5hN/D)$ bytes. For SD3-2B, $4{,}250 \cdot 1{,}536 \cdot (34 + 5 \cdot 24 \cdot 4{,}250 / 1{,}536) = 2.39$ GB per layer, and 57.3 GB across 24 layers; without the scores term, $4{,}250 \cdot 1{,}536 \cdot 34 \cdot 24 = 5.33$ GB.

</details>

## Implementation

The core of a DiT fits in a few lines. This is the patchify step and an adaLN-Zero block, written out so that every matrix multiply is visible; the lab's `census.py` holds the full model, which reproduces DiT's published compute to 0.02 GMAC.

```python
import torch, torch.nn as nn, torch.nn.functional as F

def patchify(x, p):                      # x: B, C, H, W  ->  B, (H/p)(W/p), C*p*p
    b, c, h, w = x.shape
    x = x.reshape(b, c, h // p, p, w // p, p).permute(0, 2, 4, 1, 3, 5)
    return x.reshape(b, (h // p) * (w // p), c * p * p)

class AdaLNZeroBlock(nn.Module):
    def __init__(self, d, heads):
        super().__init__()
        self.heads = heads
        self.norm1 = nn.LayerNorm(d, elementwise_affine=False)
        self.norm2 = nn.LayerNorm(d, elementwise_affine=False)
        self.qkv, self.proj = nn.Linear(d, 3 * d), nn.Linear(d, d)
        self.mlp = nn.Sequential(nn.Linear(d, 4 * d), nn.GELU(approximate="tanh"), nn.Linear(4 * d, d))
        self.ada = nn.Sequential(nn.SiLU(), nn.Linear(d, 6 * d))
        nn.init.zeros_(self.ada[1].weight); nn.init.zeros_(self.ada[1].bias)  # block starts as identity

    def forward(self, x, cond):              # x: B, N, D   cond: B, D (timestep + label)
        b, n, d = x.shape
        sh1, sc1, g1, sh2, sc2, g2 = self.ada(cond)[:, None].chunk(6, dim=-1)
        h = self.norm1(x) * (1 + sc1) + sh1
        q, k, v = self.qkv(h).reshape(b, n, 3, self.heads, d // self.heads).permute(2, 0, 3, 1, 4)
        a = F.scaled_dot_product_attention(q, k, v).transpose(1, 2).reshape(b, n, d)
        x = x + g1 * self.proj(a)
        return x + g2 * self.mlp(self.norm2(x) * (1 + sc2) + sh2)
```

`patchify` on Part 1's patch with `p=2` returns exactly the four tokens in the worked example's table. Counting a model needs no weights and no memory. PyTorch's `meta` device records shapes without allocating storage, and `FlopCounterMode` counts every convolution and matrix multiply as the model runs:

```python
from torch.utils.flop_counter import FlopCounterMode

with torch.device("meta"):
    block = AdaLNZeroBlock(1152, 16)
    x, cond = torch.randn(1, 256, 1152), torch.randn(1, 1152)
counter = FlopCounterMode(display=False)
with counter:
    block(x, cond)
print(counter.get_total_flops() / 1e9)   # 8.47 GFLOP: 8.15 linear + 0.30 attention + 0.02 adaLN
```

That is how the lab counts SD 1.5's 860M-parameter U-Net and SD3's 8B MM-DiT on a laptop in seconds. The counter counts convolutions and matrix multiplies only, not normalisations, activations or the softmax, which is why its DiT-XL/2 total sits 0.02 GMAC under the paper's. The full script, its captured output and the exercise ladder are under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake: reading a parameter count as a cost.** DiT-XL/4 and DiT-XL/2 have the same 675M parameters and differ 4.08× in compute and more than 2× in FID. <!-- L16 --> SD3's text stream holds half its parameters and does 2.4% of its arithmetic. Count tokens and widths instead.

- **Mixing FLOP conventions.** One tool's 237 GFLOP is another paper's 118.6 Gflops. DiT's table counts a multiply-add once; PyTorch's counter, and this post, count it twice. Comparing across the two silently doubles or halves a model.
- **Trusting config key names.** In SD-era diffusers configs, `attention_head_dim` is the number of heads. <!-- L09 --> Reading it as a width gives SD 1.5 heads of 8 instead of 40, 80 and 160, and any memory or FLOP estimate built on that is wrong.
- **Confusing the two U-ViTs.** Bao and colleagues' U-ViT is a transformer with long skips; <!-- L40 --> Hoogeboom and colleagues' U-ViT, in simple diffusion, is a U-Net whose low-resolution stages are transformers. <!-- L12 --> SD3's comparison uses the second. <!-- L30 --> Check the citation before carrying a result from one to the other.
- **Taking FLOP share as time share.** The naive and fused attention in Figure 11 do identical arithmetic and differ 5.1× in time on this CPU, because one moves a 1 GB matrix through memory. FLOP counts also omit normalisation, activations and softmax, which are cheap in arithmetic and not always cheap in time.
- **Adding up every layer's attention memory at inference.** Each layer frees its scores before the next runs, so the inference peak is one layer's tables, not the sum. Training is the opposite: every layer's activations are kept until the backward pass.
- **Comparing FIDs across setups.** Every FID here is tied to its paper's dataset, resolution, step count, guidance and evaluation, and the series treats a number without its setup as unusable. DiT's 19.47 is at 400K steps without guidance; its 2.27 is after 7M steps with guidance. <!-- L16 --> <!-- L20 --> The two backbones in a comparison should share everything else.
- **Expecting a resolution change to be free.** A DiT's position table and token count are tied to its training grid, and quadrupling the pixels quadruples $N$ and pushes attention's share up the curve in Figure 10.

## Key takeaways

- A diffusion backbone is defined by its contract (noisy latent, timestep and condition in; a same-shaped tensor out) and distinguished by where it spends: SD 1.5's U-Net stores 84% of its weights at 16×16 and 8×8 but spends 38% of its compute, and 87% of its attention, at 64×64.
- DiT's patch size is a compute dial, not a size dial: halving it keeps 675M parameters and multiplies tokens by 4 and compute by about 4, and DiT's results tracked compute.
- MM-DiT doubles the weights per block to give text its own stream, but those weights cost 2.4% of the arithmetic at 1024×1024; joint attention over 4,250 tokens costs 31.6%.
- Attention's share of a transformer block is $N/(N + 6D)$, half at $N = 6D$; above that, hierarchical or local attention and fused kernels stop being optional.
- Memory is weights, 16 bytes per parameter of training state, activations dominated by attention scores at high resolution, and frozen encoders that can outweigh the denoiser.

## Try it yourself

These three can be answered from the article alone. The full five-rung ladder, with the lab's own run as the answer key, is in the lab's README under [Lab downloads](#lab-downloads).

### E1 — Reproduce: tokens for a 768×768 image

A latent DiT with downsampling factor 8 and patch size 2 receives a 768×768 image. How many tokens does it attend over, and how many comparisons is that per head per layer?

**Self-check:** your token count is a perfect square, and your pair count is its square.

<details><summary>Answer</summary>

The latent is 96×96, and 2×2 patches give 48×48 = 2,304 tokens. Each head compares $2{,}304^2 = 5{,}308{,}416$ pairs per layer.

</details>

### E2 — Inspect: read the decoder's widths off Figure 3

How many input channels does the first ResNet block of SD 1.5's up level at 32×32 receive, and which two tensors make them up?

**Self-check:** the number is the sum of the incoming tensor's channels and one skip's channels.

<details><summary>Answer</summary>

1,920: the 1,280-channel tensor upsampled from 16×16, concatenated with the 640×32×32 skip saved after down level 1's second ResNet-and-transformer pair. The lab's trace shows `up_blocks.2.resnets.0` taking 1,920×32×32.

</details>

### E3 — Predict: DiT-XL/2 at 1024×1024

Before running anything, predict attention's share of one DiT-XL block if DiT-XL/2 is run at 1024×1024, then check it against the lab's 4,096-token row.

**Self-check:** within a percentage point of the lab, with the reason coming from $N/(N+6D)$.

<details><summary>Answer</summary>

The latent is 128×128, so $p = 2$ gives 4,096 tokens. $4{,}096 / (4{,}096 + 6 \cdot 1{,}152) = 4{,}096 / 11{,}008 = 37.2\%$. The lab measures 37.2% for one DiT-XL block at 4,096 tokens: about ten times the 3.6% at the model's native 256×256.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, what was executed, provenance, run order, and the E1–E5 exercise ladder.
- [`census.py`](LAB_02) — builds SD 1.5's U-Net, DiT-XL and SD3's MM-DiT on the meta device and measures every shape, parameter and FLOP count in this post, plus the CPU attention sweep.
- [`requirements.txt`](LAB_03) — the pinned CPU PyTorch and diffusers versions.
- [`captures.json`](LAB_04) — the author's run, machine-readable, which every figure was drawn from.
- [`expected-output.txt`](LAB_05) — the same run as printed, to compare against your own.
- [Complete lab](https://minio.canery.in/media/lab-diffusion-backbones-unet-to-dit.zip) — every file above in one zip.

### Sources

**Backbones**

1. Ronneberger, Fischer & Brox. [U-Net: Convolutional Networks for Biomedical Image Segmentation](https://doi.org/10.1007/978-3-319-24574-4_28). MICCAI 2015.
2. Ho, Jain & Abbeel. [Denoising Diffusion Probabilistic Models](https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html). NeurIPS 2020.
3. Dhariwal & Nichol. [Diffusion Models Beat GANs on Image Synthesis](https://proceedings.neurips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html). NeurIPS 2021.
4. Rombach, Blattmann, Lorenz, Esser & Ommer. [High-Resolution Image Synthesis with Latent Diffusion Models](https://doi.org/10.1109/CVPR52688.2022.01042). CVPR 2022.
5. Podell et al. [SDXL: Improving Latent Diffusion Models for High-Resolution Image Synthesis](https://proceedings.iclr.cc/paper_files/paper/2024/hash/081b08068e4733ae3e7ad019fe8d172f-Abstract-Conference.html). ICLR 2024.
6. Saharia et al. [Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding](https://arxiv.org/abs/2205.11487) (Imagen). NeurIPS 2022.
7. Hoogeboom, Heek & Salimans. [simple diffusion: End-to-end diffusion for high resolution images](https://proceedings.mlr.press/v202/hoogeboom23a.html). ICML 2023.
8. Karras et al. [Analyzing and Improving the Training Dynamics of Diffusion Models](https://doi.org/10.1109/CVPR52733.2024.02282) (EDM2). CVPR 2024.
9. Peebles & Xie. [Scalable Diffusion Models with Transformers](https://doi.org/10.1109/ICCV51070.2023.00387) (DiT). ICCV 2023.
10. Bao et al. [All are Worth Words: A ViT Backbone for Diffusion Models](https://doi.org/10.1109/CVPR52729.2023.02171) (U-ViT). CVPR 2023.
11. Esser et al. [Scaling Rectified Flow Transformers for High-Resolution Image Synthesis](https://proceedings.mlr.press/v235/esser24a.html) (SD3, MM-DiT). ICML 2024.
12. Chen et al. [PixArt-α: Fast Training of Diffusion Transformer for Photorealistic Text-to-Image Synthesis](https://arxiv.org/abs/2310.00426). Preprint, arXiv:2310.00426.
13. Black Forest Labs et al. [FLUX.1 Kontext: Flow Matching for In-Context Image Generation and Editing in Latent Space](https://arxiv.org/abs/2506.15742). Preprint, arXiv:2506.15742.
14. Crowson et al. [Scalable High-Resolution Pixel-Space Image Synthesis with Hourglass Diffusion Transformers](https://proceedings.mlr.press/v235/crowson24a.html) (HDiT). ICML 2024.
15. Tian et al. [U-DiTs: Downsample Tokens in U-Shaped Diffusion Transformers](https://arxiv.org/abs/2405.02730). NeurIPS 2024.
16. Yan, Gu & Rush. [Diffusion Models Without Attention](https://doi.org/10.1109/CVPR52733.2024.00787). CVPR 2024.
17. Ma et al. [SiT: Exploring Flow and Diffusion-based Generative Models with Scalable Interpolant Transformers](https://doi.org/10.1007/978-3-031-72980-5_2). ECCV 2024.
18. Liang et al. [Scaling Laws For Diffusion Transformers](https://arxiv.org/abs/2410.08184). ICLR 2026, per the paper's own header.

**Attention, conditioning and memory**

19. Vaswani et al. [Attention Is All You Need](https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html). NeurIPS 2017.
20. Dosovitskiy et al. [An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale](https://arxiv.org/abs/2010.11929). ICLR 2021.
21. Perez, Strub, de Vries, Dumoulin & Courville. [FiLM: Visual Reasoning with a General Conditioning Layer](https://doi.org/10.1609/aaai.v32i1.11671). AAAI 2018.
22. Dao, Fu, Ermon, Rudra & Ré. [FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness](https://arxiv.org/abs/2205.14135). NeurIPS 2022.
23. Rajbhandari, Rasley, Ruwase & He. [ZeRO: Memory Optimizations Toward Training Trillion Parameter Models](https://doi.org/10.1109/SC41405.2020.00024). SC20.
24. Korthikanti et al. [Reducing Activation Recomputation in Large Transformer Models](https://proceedings.mlsys.org/paper_files/paper/2023/hash/80083951326cf5b35e5100260d64ed81-Abstract-mlsys2023.html). MLSys 2023.

**Surveys**

25. Ma et al. [Efficient Diffusion Models: A Comprehensive Survey From Principles to Practices](https://doi.org/10.1109/TPAMI.2025.3569700). IEEE TPAMI 47(9), 2025.
26. Ignacio et al. [Revisiting U-Net: a foundational backbone for modern generative AI](https://doi.org/10.1007/s10462-025-11450-0). Artificial Intelligence Review 59(2), 2025.

**Configs and code** (accessed 2026-10-03)

27. CompVis. [stable-diffusion v1 inference config](https://github.com/CompVis/stable-diffusion/blob/main/configs/stable-diffusion/v1-inference.yaml).
28. [stable-diffusion-v1-5 U-Net config](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/unet/config.json).
29. [stable-diffusion-xl-base-1.0 U-Net config](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/blob/main/unet/config.json).
30. facebookresearch. [DiT models.py](https://github.com/facebookresearch/DiT/blob/main/models.py).
31. Hugging Face. [diffusers](https://github.com/huggingface/diffusers), v0.40.0: the U-Net, ResNet and SD3 transformer modules and the SD3 conversion script.
32. PyTorch. [torch.nn.functional.scaled_dot_product_attention](https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html), version 2.14.
