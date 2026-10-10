---
title: "Diffusion Model Architecture: The Complete Guide"
slug: diffusion-model-architecture
date: 2026-09-20
updated: 2026-09-20
summary: "A complete map of diffusion model architecture: forward process, denoisers, conditioning, objectives, samplers, training, evaluation, and practical limits."
tags: [machine-learning, diffusion-model, generative-model, transformer, computer-vision, deep-learning]
category: machine-learning
tier: L4
difficulty: advanced
prerequisites: ["probability distributions", "linear algebra", "neural-network basics", "PyTorch tensor shapes"]
reading_minutes: 42
cover_image: "https://minio.canery.in/media/cover-diffusion-model-architecture.png"
canonical_url: "https://canery.in/blogs/diffusion-model-architecture"
---
> [!NOTE]
> **Insights** — A diffusion model is not one neural network that “removes noise.” It is a complete generative system: a known path that corrupts data, a time-conditioned neural network that estimates how to move back, a conditioning interface, and a numerical sampler that follows those estimates. U-Nets and diffusion transformers are interchangeable *backbone families* inside that system; schedules, prediction targets, guidance, latent encoders, and solvers are separate design axes.

**Level:** advanced · **You need:** probability distributions, linear algebra, neural-network basics, PyTorch tensor shapes · **Time:** ~42 min

**Jump to:** [the numeric example](#worked-example) · [system map](#what-is-a-complete-diffusion-system) · [U-Net](#how-does-a-diffusion-u-net-denoise) · [transformers](#why-are-transformers-replacing-some-u-nets) · [conditioning](#how-do-text-and-other-conditions-enter) · [prediction targets](#what-exactly-should-the-network-predict) · [samplers](#how-does-sampling-turn-predictions-into-data) · [math](#the-math) · [implementation](#implementation)

## Why this matters

Suppose a text-to-image model produces good texture but ignores spatial words. “Use a better sampler” is probably the wrong repair: a sampler integrates the field the network already learned; it cannot manufacture missing text-image interactions. Suppose another model follows prompts but needs too many denoiser calls. Replacing its text encoder will not solve that; the bottleneck belongs to the trajectory, solver, or distillation strategy.

Diffusion systems fail at their interfaces. An autoencoder may erase tiny text before the denoiser sees it. A nonzero terminal signal-to-noise ratio may give training inputs that never look like inference inputs. High classifier-free guidance may improve prompt adherence while reducing coverage. A transformer may run out of memory because patch size quadrupled its token count. The phrase “diffusion architecture” hides all of these independent decisions.

This article gives each decision a name, tensor shape, equation, and boundary. Once the layers are separated, you can read a paper, inspect a checkpoint, or design a new model without treating every improvement as a mysterious property of “the diffusion model.”

## The problem

We have samples $`x_0 \sim p_{data}`$ from an unknown data distribution: images, audio waveforms, actions, molecules, or another high-dimensional object. We want a mechanism that draws a new sample with the same structure. Directly describing $`p_{data}(x)`$ is difficult because its probability mass lies on a complicated subset of a vast ambient space.

A **diffusion model** is a generative model that connects this complex data distribution to a simple reference distribution, normally Gaussian noise. The original diffusion-probabilistic construction makes the connection with a **forward process**: a fixed Markov chain that adds a small amount of noise at each step. It then learns a **reverse process** whose transitions remove that corruption.  “Forward” refers to data-to-noise, not generation; generation runs the learned direction from noise back to data.

At discrete timestep $t$, a common forward transition is

$$
q(x_t \mid x_{t-1}) = \mathcal{N}\!\left(x_t; \sqrt{1-\beta_t}\,x_{t-1},\,\beta_t I\right).
$$

Here $x_t$ is the noisy sample, $β_t$ is the variance added at step $t$, $I$ is the identity covariance, and $q$ denotes the known forward distribution. The square-root scaling prevents variance from growing without control.

The **noise schedule** is the sequence $`\{\beta_t\}_{t=1}^{T}`$. It decides how quickly information is destroyed, which noise levels the network sees, and how a discrete sampler indexes the path. It is configuration, not a learned layer in the usual DDPM setup.

The reverse conditional $q(x_{t-1}\mid x_t)$ depends on the unknown data distribution, so it is not available at generation time. We approximate it with

$$
p_\theta(x_{t-1}\mid x_t) = \mathcal{N}\!\left(x_{t-1};\mu_\theta(x_t,t),\Sigma_\theta(x_t,t)\right),
$$

where $θ$ contains learned parameters. The network may output the mean directly, but modern parameterizations usually make it predict the added noise, the clean sample, a velocity, or the score, then convert that prediction into a reverse update.

Figure 1 is the first boundary to keep straight: the forward arrows are analytically chosen; the neural network learns the information required to construct arrows in the opposite direction.

![One chain of noisy states with fixed forward noising above it, learned reverse denoising below it, and a closed-form shortcut from clean data to any level](https://minio.canery.in/media/fig-01-forward-reverse-diffusion-model-architecture.png)

*Figure 1. A diffusion system learns the reverse field, not the forward corruption. Training can jump directly from $x_0$ to any $x_t$, even though sampling follows a sequence of reverse updates.*

The Denoising Diffusion Probabilistic Model (DDPM) connected this probabilistic chain to denoising score matching and popularized a simplified noise-prediction loss.  A **score-based model** expresses closely related information as the score $`\nabla_x \log p_t(x)`$: the gradient of the log density at noise level $t$. It points toward locally higher probability. Noise-conditional score networks learn that field over many Gaussian perturbation levels and can sample with annealed Langevin dynamics. 

These are two views of the same central problem: learn a vector field over noisy data, conditioned on how noisy the data is. But that sentence still leaves three engineering questions unanswered:

1. What neural architecture represents the field?
2. What target and loss teach it?
3. What numerical procedure follows it at inference?

The rest of the article keeps those questions separate.

## Worked example

Use the smallest image that still exposes shape: a $2\times2$ single-channel tensor. Flattening it only for arithmetic, let

$$
x_0 = \begin{bmatrix}1 & -1 \\ 0.5 & 0\end{bmatrix},
\qquad
\epsilon = \begin{bmatrix}0.2 & 1.0 \\ -0.4 & 0.6\end{bmatrix}.
$$

$x_0$ is the clean sample after scaling pixel values into a model-friendly range. The tensor $ε$ is one draw from a standard Gaussian with the same shape. In real training it is random; the fixed numbers here let us check the computation.

Define $`\alpha_t=1-\beta_t`$ and the cumulative product $`\bar\alpha_t=\prod_{s=1}^{t}\alpha_s`$. The Markov chain has a useful closed form:

$$
x_t = \sqrt{\bar\alpha_t}\,x_0 + \sqrt{1-\bar\alpha_t}\,\epsilon.
$$

This equation says every noisy sample is a known mixture of clean signal and Gaussian noise. It lets training choose any timestep and create $x_t$ in one operation instead of simulating all earlier steps.

Choose a timestep whose cumulative signal coefficient is $`\bar\alpha_t=0.64`$. Then $`\sqrt{\bar\alpha_t}=0.8`$ and $`\sqrt{1-\bar\alpha_t}=0.6`$. Multiply the two tensors separately:

$$
0.8x_0 = \begin{bmatrix}0.8 & -0.8 \\ 0.4 & 0\end{bmatrix},
\qquad
0.6\epsilon = \begin{bmatrix}0.12 & 0.60 \\ -0.24 & 0.36\end{bmatrix}.
$$

The two terms are the surviving signal and the injected noise. Adding them gives

$$
x_t = \begin{bmatrix}0.92 & -0.20 \\ 0.16 & 0.36\end{bmatrix}.
$$

Figure 2 keeps the intermediate tensors visible. The bottom-right value is especially useful: a clean zero became $0.36$, entirely due to noise; the top-left retained most of its positive signal.

![Three two-by-two matrices of numbers above the same three tensors as intensity, so 0.80 plus 0.12 equals 0.92 is visible rather than stated](https://minio.canery.in/media/fig-02-numeric-corruption-diffusion-model-architecture.png)

*Figure 2. A training pair is synthesized, not labeled by a human. The model receives $x_t$ and $t$; the exact $ε$ used to create it is the target.*

### The target is known for free

An $ε$-prediction network $`\epsilon_\theta(x_t,t)`$ sees the noisy matrix and a representation of the timestep. Suppose its current output is

$$
\hat\epsilon = \begin{bmatrix}0.1 & 0.8 \\ -0.2 & 0.7\end{bmatrix}.
$$

For mean-squared error averaged across four elements,

$$
\mathcal{L}_{simple}
= \frac{1}{4}\lVert \epsilon-\hat\epsilon\rVert_2^2
= \frac{0.01+0.04+0.04+0.01}{4}
= 0.025.
$$

The loss is supervised because the training procedure generated the corruption and retained the answer. No iterative sampling occurs inside this training example.

We can also turn the predicted noise into an estimate of the clean image:

$$
\hat{x}_0 = \frac{x_t-\sqrt{1-\bar\alpha_t}\,\hat\epsilon}{\sqrt{\bar\alpha_t}}.
$$

Subtract the predicted noise contribution, then divide by the remaining signal coefficient. With our numbers,

$$
\hat{x}_0
= \frac{1}{0.8}
\left(
\begin{bmatrix}0.92 & -0.20 \\ 0.16 & 0.36\end{bmatrix}
-0.6\begin{bmatrix}0.1 & 0.8 \\ -0.2 & 0.7\end{bmatrix}
\right)
= \begin{bmatrix}1.075 & -0.85 \\ 0.35 & -0.075\end{bmatrix}.
$$

The estimate is imperfect because the predicted noise is imperfect. A sampler uses this estimate—or an algebraically equivalent mean, score, or velocity—to move toward a slightly cleaner state.

### Signal-to-noise ratio names the difficulty

The **signal-to-noise ratio (SNR)** at this timestep is the signal variance coefficient divided by the noise variance coefficient:

$$
\operatorname{SNR}(t)=\frac{\bar\alpha_t}{1-\bar\alpha_t}=\frac{0.64}{0.36}\approx1.78.
$$

An SNR above one means the forward mixture contains more signal power than noise power under the standardized model. Near the final noise state SNR approaches zero, so predicting fine $x_0$ detail from $x_t$ becomes much more ambiguous.

This one ratio appears repeatedly. It describes noise schedules, relates parameterizations, and supplies loss weights. Variational Diffusion Models showed that, under its continuous-time construction, the variational lower bound depends on SNR endpoints rather than the interior schedule.  Min-SNR weighting later proposed clamping SNR-derived weights to reduce conflicts between the denoising tasks at different timesteps. 

### One example is not one sampling step

During training we drew one $t$, made one $x_t$, and computed one loss. During generation there is no $x_0$ and no known $ε$. We start at $x_T\sim\mathcal N(0,I)$, query the network, take an update to a lower noise level, and repeat.

The original DDPM experiments used a chain with $1{,}000$ discrete diffusion steps.  That number is neither a law nor the mandatory inference count. Improved Diffusion examples expose $4{,}000$ training steps while allowing respaced sampling schedules.  Training discretization, sampler steps, and neural-function evaluations are related configuration values, not synonyms.

## Intuition

The cleanest mental model has three objects: a **path**, a **field**, and an **integrator**.

The path says which intermediate distributions connect data and noise. A DDPM uses a variance-preserving Gaussian corruption path. A variance-exploding score model uses another. Flow matching can prescribe diffusion paths or different probability paths. 

The field says which direction to move at every point and noise level. A neural **denoiser** is a time-conditioned function approximator for that field. “Denoiser” is convenient shorthand, but the output need not literally be a clean image: it may be $ε$, $x_0$, velocity $v$, or a score.

The integrator—or **sampler/solver**—turns repeated field evaluations into a trajectory. A stochastic ancestral sampler injects fresh noise. DDIM can trace a deterministic path. A high-order ODE solver combines several evaluations to reduce numerical error. A distilled or consistency model changes what the network has learned so fewer calls are required.

Figure 3 places those objects, together with the representation and conditioning interfaces, on separate axes, and marks which of them a checkpoint fixes. This is the single most useful picture for reasoning about diffusion architecture because it prevents “sampler,” “schedule,” and “model” from collapsing into one knob.

![Five stacked design axes, each with a pictogram of itself, labelled with whether it survives a checkpoint swap or needs retraining](https://minio.canery.in/media/fig-03-five-layer-system-diffusion-model-architecture.png)

*Figure 3. You can often replace the solver without retraining, but you cannot freely replace the representation or learned target: those change the function the checkpoint represents.*

The analogy is a navigation app. The path family is the road network, the learned field is a map that tells you which way heads toward the destination from every location, and the solver is the driving policy that decides step size and whether to add exploration. The analogy breaks because diffusion fields evolve over a probability distribution, not a single physical landscape, and stochastic trajectories are a mathematical part of the model rather than driver indecision.

### The score is local information with global consequences

At time $t$, define

$$
s_t(x)=\nabla_x\log p_t(x).
$$

$p_t$ is the density of noisy data and $s_t$ is its score. The gradient points toward a local increase in log probability, but following it across many noise levels can produce a globally structured sample. A neural score estimator $s_θ(x,t)$ is therefore not a database of training images; it is a field over the noisy space.

The continuous-time score framework derives a reverse-time stochastic differential equation (SDE) and a corresponding probability-flow ordinary differential equation (ODE) whose marginals match when the score is exact.  The SDE produces stochastic paths; the ODE produces deterministic paths and enables a numerical-solver view. “Same marginals” does not mean their individual trajectories are identical.

### Why iterative refinement is useful

High noise levels determine coarse, globally ambiguous structure because fine detail is absent. Low noise levels refine local detail because most of the signal is already known. One network can handle both regimes because the timestep or noise embedding tells its blocks which task they are solving.

That decomposition makes generation controllable. Measurements, masks, text, class labels, depth maps, or other conditions can influence every refinement stage. It also makes inference expensive: a large denoiser may be evaluated dozens of times in sequence, and sequence length cannot be parallelized in the same way as examples in a batch.

## What is a complete diffusion system?

A production image generator usually contains more than the diffusion backbone:

- A **data representation** converts raw data into the space where noise is applied. Pixel-space models use the image directly. Latent models first use an autoencoder.
- A **condition encoder** turns text, class labels, layouts, masks, audio, or other signals into vectors or spatial feature maps.
- A **time/noise embedding** converts a scalar noise coordinate into features used throughout the denoiser.
- The **denoiser backbone** predicts a chosen target from the noisy representation plus conditions.
- A **guidance rule** modifies conditional predictions at inference.
- A **scheduler/solver** chooses noise levels and computes the next state.
- A **decoder** maps the final latent back to the public data domain when generation happened in a compressed representation.

Figure 4 gives each part its interface. The same denoiser checkpoint can support multiple compatible solvers, but its input channel count, latent scaling, text-embedding width, prediction target, and noise parameterization must agree with training.

![An end-to-end graph placing the training loop, the conditioning chain and the N-step inference loop around the one shared learned denoiser](https://minio.canery.in/media/fig-04-complete-system-diffusion-model-architecture.png)

*Figure 4. The denoiser sits at the center, but the representation and conditioning interfaces determine what its tensors mean; the solver determines how often and where it is evaluated.*

This separation explains several misleading phrases:

- “The model uses a transformer” normally means the denoiser backbone is transformer-based. A separate transformer may also encode text.
- “The model has 30 steps” normally describes inference, not the number of layers and not necessarily the training diffusion horizon.
- “The scheduler predicts noise” is backwards. The network predicts; the scheduler converts that prediction into a state update.
- “Latent diffusion” names the representation in which the process runs, not one specific U-Net or sampler.

Official implementations expose these boundaries differently. OpenAI’s guided-diffusion release implements a U-Net with timestep-conditioned residual blocks and attention at selected resolutions.  CompVis separates first-stage autoencoding, conditioning, and latent denoising in configuration and code.  The abstractions have different class names, but the interfaces above remain.

## How does a diffusion U-Net denoise?

A **U-Net** is a multiscale encoder-decoder with long skip connections between matching resolutions. The original architecture used a contracting path to capture context and a symmetric expanding path for precise localization.  Diffusion U-Nets keep that topology but replace segmentation-specific blocks with residual blocks, time conditioning, normalization, and often attention.

Assume a latent input $z_t$ has shape $`B\times4\times64\times64`$: batch, channel, height, width. An input convolution lifts four latent channels to a wider feature width. Down blocks reduce spatial resolution while increasing channels; a middle block works at the coarsest scale; up blocks reverse the pyramid and concatenate or add stored skip features.

Figure 5 traces an illustrative three-level model. Exact channel multipliers vary, but every edge states the shape so the memory and interface costs are visible.

![A U-shaped trace whose block heights are spatial resolution and widths are channel count, with one dashed skip joining each resolution to its mirror](https://minio.canery.in/media/fig-05-unet-shapes-diffusion-model-architecture.png)

*Figure 5. The main path buys receptive field by lowering resolution. Long skips return high-frequency spatial evidence that would otherwise have to pass through the bottleneck.*

### Residual blocks do most local computation

A **residual block** learns an update $F(h)$ and returns $h+F(h)$, possibly after projecting the skip when channel counts differ. In a diffusion U-Net, a typical block applies normalization, a smooth activation such as SiLU, convolution, and timestep-derived modulation.

Group Normalization is common because it normalizes channel groups within each example instead of depending on batch statistics. That matters when high-resolution models force small per-device batches. A sinusoidal or Fourier feature mapping first expands the scalar timestep/noise level; a multilayer perceptron then produces an embedding that each block projects to its channel width.

The projection may be added as a bias, or split into scale and shift values for feature-wise affine modulation:

$$
\operatorname{Mod}(h,t)=\bigl(1+s(t)\bigr)\odot \operatorname{Norm}(h)+b(t).
$$

$s(t)$ and $b(t)$ are channel-wise scale and bias derived from time, and $\odot$ is elementwise multiplication. The block can therefore change its computation continuously from coarse denoising at high noise to detail restoration at low noise.

Figure 6 shows why “the timestep is an input” is an incomplete architectural description. Time reaches repeated blocks across the network, not just the first layer.

![A normalized feature map, a per-channel scale and shift bar for each of its six channels, and the modulated map those values produce](https://minio.canery.in/media/fig-06-time-residual-block-diffusion-model-architecture.png)

*Figure 6. The identity path carries features unchanged; the conditioned branch learns a noise-level-specific update. Time modulation is distributed through depth.*

### Attention supplies nonlocal interaction

Convolutions mix nearby positions efficiently, but their direct interaction range is local. Diffusion U-Nets insert attention at selected resolutions, where token count is affordable and global relationships matter.

**Self-attention** is a mechanism in which queries, keys, and values all come from the noisy feature tokens. It lets one spatial position aggregate information from any other. **Cross-attention** changes the source of keys and values: queries come from noisy image/latent features, while keys and values come from condition tokens such as text. Scaled dot-product attention computes a compatibility matrix and uses its softmax values to weight the values. 

For queries $Q$, keys $K$, values $V$, and key width $d_k$,

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V.
$$

The $QK^\top$ matrix contains every permitted query-key pairing. Dividing by $\sqrt{d_k}$ controls logit scale; the softmax makes each query’s weights sum to one.

Figure 7 holds the query stream fixed so the difference is unambiguous.

![Two score matrices drawn to scale: self-attention is a square N by N grid, cross-attention a narrow N by L grid over the prompt tokens](https://minio.canery.in/media/fig-07-self-vs-cross-attention-diffusion-model-architecture.png)

*Figure 7. Self-attention asks “which image positions matter to this position?” Cross-attention asks “which condition tokens matter to this image position?” The operations look alike, but their information sources differ.*

Attention at a $64\times64$ map would create $4{,}096$ spatial tokens per example before heads and batching. Full attention’s pair matrix grows quadratically with token count, so many U-Nets concentrate it at lower resolutions or use memory-efficient kernels. Convolutional blocks then carry the fine-resolution work.

## Why are transformers replacing some U-Nets?

A transformer denoiser keeps the diffusion objective and replaces the multiresolution convolutional backbone. The important phrase is **replaces the backbone**: a Diffusion Transformer (DiT) is still trained at noisy timesteps and still plugs into a sampler.

DiT starts with a noisy latent $z_t$ of shape $`B\times C\times H\times W`$. A **patch embedding** uses a strided projection to divide the grid into non-overlapping patches and map each patch to a token of width $D$. With patch size $P$, the sequence length is

$$
N=\frac{H}{P}\frac{W}{P}.
$$

$N$ is the number of noisy image tokens. Halving $P$ in both dimensions creates four times as many tokens, so attention and activation memory rise sharply even though the latent resolution did not change.

Patchification destroys spatial order: a transformer block treats its input as a set, so nothing in the sequence says which patch came from the top-left corner. A **positional embedding** is the vector added to each token that restores that information. The official DiT implementation adds a fixed two-dimensional sine-cosine embedding to the patch tokens rather than learning one.  Treat it as a fifth thing that must agree between training and inference: the embedding is built for a particular token grid, so changing latent resolution or patch size changes the grid it has to cover, and a checkpoint asked to run at a size its positional scheme never saw can degrade in ways no sampler setting repairs.

The original DiT study applied transformers to latent patches, conditioned blocks with adaptive layer normalization, and found that increasing forward-pass compute through model size or token count consistently lowered FID in its class-conditional ImageNet experiments.  Its DiT-XL/2 setup reported FID 2.27 on ImageNet $256\times256$ under that paper’s evaluation.  That is evidence about a controlled family and setup, not proof that transformers dominate every dataset and compute budget.

Figure 8 shows the shape-preserving route. The model never creates a convolutional resolution pyramid: global token mixing happens in every full-attention block, while unpatchification reconstructs the spatial output.

![The same latent under a two-by-two and a one-by-one patch lattice, flattened into token strips of visibly different length](https://minio.canery.in/media/fig-08-dit-token-flow-diffusion-model-architecture.png)

*Figure 8. DiT moves spatial structure into a token sequence. Patch size becomes an architecture knob because it changes both granularity and sequence length.*

### What is inside a DiT block?

Each token passes through multi-head self-attention and a feed-forward network with residual connections. The time embedding and class or other global condition modulate normalization. The official DiT implementation uses adaptive LayerNorm conditioning around these sublayers. 

Adaptive Layer Normalization (adaLN) is a conditioning mechanism that predicts scale, shift, and often residual gates from a condition vector. Unlike cross-attention, it does not create token-to-token alignment. It is efficient for global labels or pooled conditions; token-level text usually needs concatenation, cross-attention, joint attention, or a combination.

Transformers trade convolutional inductive bias for uniform, scalable blocks. A U-Net has translation-friendly local filters and explicit multiscale structure. DiT gives every token a direct global communication route but pays attention costs. On small data or constrained compute, the U-Net’s bias may be valuable. At large scale, transformer depth/width scaling and mature distributed implementations can be attractive.

### U-ViT keeps the skip idea

A U-shaped Vision Transformer (U-ViT) treats noisy patches, time, and conditions as tokens, while adding long skips between shallow and deep transformer layers. The studied U-ViT results suggest that these long skips were important even without CNN downsampling and upsampling.  

This is a useful correction to a false binary. “U-Net versus transformer” mixes topology and operator. You can keep long encoder-decoder-style skips while replacing convolutions with attention, or place transformer blocks inside a convolutional U-Net.

### MM-DiT gives modalities separate streams

Text-to-image systems have two sequences with different statistics: noisy image tokens change at every denoising call, while text tokens come from a frozen or separately trained encoder. A Multi-Modal Diffusion Transformer (MM-DiT) gives the modalities separate learned projections/weights while letting them interact through joint attention. The rectified-flow transformer study that introduced this design describes bidirectional information flow between image and text tokens. 

That is different from classic cross-attention, where image queries read text keys and values but the text stream is not symmetrically updated inside the denoiser. It is also different from vanilla concatenation under fully shared weights. Figure 16 later positions these architectures by the locality and modality structure they assume.

> [!IMPORTANT]
> A modern text-to-image transformer may be trained with rectified flow rather than a DDPM objective. The 2024 MM-DiT work is one such system. Calling every transformer generator “a DDPM” erases the actual training path. 

## How do text and other conditions enter?

Conditional generation estimates $p(x\mid c)$, where $c$ may be a class, text, a segmentation mask, depth, an edge map, another image, audio, or a structured record. “Conditioning” covers several interfaces that should be inspected separately.

### Tokenizer and encoder are not the denoiser

For text, a **tokenizer** converts a string into discrete token IDs. An **embedding** maps each ID and position to a continuous vector. A **text encoder** then contextualizes those vectors so the representation of a word depends on surrounding words.

CLIP learned aligned image-text representations through contrastive prediction of matching captions and images.  T5 is a text-to-text transformer trained in a unified transfer-learning framework.  Both can supply text features to an image generator, but their pretraining objectives and output semantics differ. Imagen’s ablations found larger gains from scaling its frozen T5 language encoder than from scaling its image diffusion model within that study. 

The practical lesson is not “T5 always wins.” It is that prompt comprehension can bottleneck outside the denoiser. If the text encoder loses word order, counts, or relational meaning, no rearrangement of image blocks can recover information that never crossed the interface.

### Four injection patterns

Conditions enter denoisers in four common ways:

1. **Additive/global modulation.** A class label or pooled text vector joins the time embedding and produces per-channel scale, shift, or bias. Use it when the condition is global and compact.
2. **Cross-attention.** Noisy spatial queries attend to a variable-length condition sequence. Use it when individual condition tokens need spatially varying influence.
3. **Concatenation.** A spatial condition such as a mask or low-resolution image is concatenated along channels, or a condition token sequence is concatenated with noisy tokens. Use it when alignment is already explicit or joint attention is intended.
4. **Separate stream with joint interaction.** Each modality has its own transformations before/after joint attention, as in MM-DiT. Use it when modalities need different capacity and bidirectional updates.

Latent Diffusion Models introduced cross-attention as a general conditioning interface for text, boxes, and other inputs while running the expensive denoising process in a compressed autoencoder space.  The system can therefore change the condition encoder without changing the mathematical definition of the forward noising path, provided dimensions and training are updated.

### Latent diffusion changes the representation boundary

A **latent diffusion model (LDM)** applies noise to an autoencoder representation $z=E(x)$ rather than raw pixels. The encoder $E$ compresses the image; the decoder $D$ maps the final latent back. The denoiser learns the distribution of latents.

Figure 9 shows the two-stage contract. The autoencoder is typically pretrained, then held fixed while the diffusion model learns. Its compression reduces the spatial tensor repeatedly processed by the denoiser, but any detail discarded by $E$ is beyond the diffusion model’s reach.

![A pixel grid beside a latent drawn eight times smaller per side, with the denoiser loop attached to the small tensor and one decode back out](https://minio.canery.in/media/fig-09-latent-diffusion-diffusion-model-architecture.png)

*Figure 9. The compute saving is multiplicative because compression happens before every denoiser call. The reconstruction error is also structural because the final decoder cannot restore information absent from the latent.*

This is the latent trade: less repeated compute and a representation biased toward perceptual content, in exchange for an autoencoder reconstruction ceiling.  Do not confuse the diffusion latent with the random $x_T$ prior. “Latent” names a learned representation; “noise” names a distribution/state on the trajectory.

### Guidance changes the field at inference

**Classifier guidance** adds the gradient of a classifier trained to predict condition $y$ from noisy $x_t$. The gradient steers samples toward states the classifier associates with $y$, trading coverage for fidelity as its scale grows.  It requires a classifier that works across noise levels.

**Classifier-free guidance (CFG)** avoids the external classifier. During training, the denoiser sometimes receives the condition and sometimes a null condition. At inference, it computes both predictions and extrapolates:

$$
\hat\epsilon_{cfg}
=\hat\epsilon_{uncond}
+w\left(\hat\epsilon_{cond}-\hat\epsilon_{uncond}\right).
$$

$w$ is the guidance scale. The parenthesized difference is a direction associated with the condition; scaling it above the ordinary conditional prediction strengthens adherence but can reduce diversity or push states outside the training distribution. CFG combines conditional and unconditional estimates from one jointly trained model. 

GLIDE compared CLIP guidance and CFG and reported a human preference for CFG in its studied setup.  That result helped make CFG common, but guidance scale is still a fidelity-coverage control, not a universal quality slider. 

Figure 15 later traces a guided inference step. Implementations often concatenate conditional and unconditional items into one larger batch, so “two predictions” may mean one batched forward call but roughly twice the denoiser work and activation footprint.

## What exactly should the network predict?

At a noisy point

$$
x_t=\alpha_t x_0+\sigma_t\epsilon,
$$

$α_t$ is the signal coefficient and $σ_t$ is the noise coefficient. In variance-preserving notation, $`\alpha_t^2+\sigma_t^2=1`$. Several prediction targets contain equivalent information when coefficients are known.

### Noise prediction

The network predicts $ε$. This makes the target standardized across data examples and gives the familiar loss

$$
\mathcal L_\epsilon=\mathbb E_{x_0,\epsilon,t}
\left[w(t)\lVert\epsilon-\epsilon_\theta(x_t,t,c)\rVert_2^2\right].
$$

$w(t)$ is an optional loss weight and $c$ is an optional condition. DDPM’s simplified objective used this form with a particular weighting interpretation. 

### Clean-data prediction

The network predicts $x_0$ directly. This aligns the target with reconstruction, but target scale follows the data and errors at low SNR can be amplified when converted into other quantities. You can recover noise as

$$
\hat\epsilon=\frac{x_t-\alpha_t\hat x_0}{\sigma_t}.
$$

The conversion divides by $σ_t$, so behavior near a zero-noise endpoint needs careful numerical handling.

### Score prediction

For Gaussian perturbations, the conditional score relates to noise by

$$
\nabla_{x_t}\log q(x_t\mid x_0)=-\frac{\epsilon}{\sigma_t}.
$$

The score is scaled negative noise. A score-network output can therefore be translated into the same reverse dynamics when the schedule convention is known.

### Velocity prediction

A common velocity target is

$$
v=\alpha_t\epsilon-\sigma_t x_0.
$$

Together with $x_t=\alpha_t x_0+\sigma_t\epsilon$, this is a rotation of the $(x_0,ε)$ coordinate pair when $`\alpha_t^2+\sigma_t^2=1`$. Inverting it gives

$$
x_0=\alpha_t x_t-\sigma_t v,
\qquad
\epsilon=\sigma_t x_t+\alpha_t v.
$$

Velocity prediction was studied as a stable parameterization for progressive distillation, where its DDIM step size becomes independent of SNR in an angular parameterization.  It is not automatically superior; target choice interacts with loss weighting, schedule, preconditioning, data scaling, and the solver.

Figure 10 shows these outputs as coordinate descriptions of the same noisy point, not four unrelated model families.

![In the clean-data and noise plane, x-t sits at coefficients 0.8 and 0.6, velocity sits perpendicular to it, and score points along negative noise](https://minio.canery.in/media/fig-10-prediction-geometry-diffusion-model-architecture.png)

*Figure 10. Prediction type changes the regression problem and numerical conditioning. Once the schedule coefficients are known, the sampler can convert among the common targets.*

### Preconditioning is part of the model interface

EDM made a valuable engineering move: it separated noise schedule, input/output preconditioning, loss weighting, and solver design into explicit choices.  Input preconditioning scales noisy data before the backbone; skip and output coefficients combine the network output with the input to produce a denoised estimate. The released implementation makes those sigma-dependent coefficients and solver choices explicit. 

This is why checkpoint configuration must travel with weights. A raw tensor of parameters does not tell you whether the network expects discrete $t$, continuous $σ$, log-SNR, scaled latents, or which target its final channels encode.

### Loss weighting decides which noise levels win

Uniformly sampling timesteps does not imply equal effective importance. The target’s scale and conversion to likelihood terms create noise-level-dependent weights. High-SNR examples emphasize precise reconstruction; low-SNR examples emphasize coarse distributional structure.

Improved DDPM studied a cosine schedule, learned reverse variances, and a hybrid likelihood/simple objective.  Variational Diffusion Models analyzed objectives through SNR.  Min-SNR treats timestep tasks as potentially conflicting and clips SNR-derived weights.  These choices change optimization without changing whether the backbone is a U-Net or transformer.

Before that, Figure 11 plots the two schedules the section has been naming. They are definitions, not measurements: both curves come straight from the schedule formulas. The cosine curve holds signal further along the path, and the linear curve's right-hand endpoint is the one that matters at inference time.

![Two panels plot the signal coefficient and the log signal-to-noise ratio against normalised timestep for the linear and cosine schedules](https://minio.canery.in/media/fig-11-noise-schedule-diffusion-model-architecture.png)

*Figure 11. The linear schedule's terminal SNR is small but not zero, so its noisiest training input still carries signal that a sample drawn from $\mathcal N(0,I)$ does not. That endpoint gap is the train-inference mismatch, visible as a curve rather than asserted as a sentence.* 

Figure 12 reduces training to the operations that must agree. Notice that a batch usually contains randomly chosen timesteps rather than one globally advancing diffusion clock.

![A batch of six thumbnails at six different noise levels enters one shared network, producing one weighted loss and one parameter update](https://minio.canery.in/media/fig-12-training-loop-diffusion-model-architecture.png)

*Figure 12. The network learns across the entire path because each example is corrupted at a sampled noise level. Sampling the model is not part of the ordinary denoising loss.*

## How does sampling turn predictions into data?

Training learns a field at arbitrary noise levels. Sampling chooses a decreasing sequence of noise levels $t_N>\cdots>t_0$ and a numerical update. Three questions characterize a sampler:

- Is the trajectory stochastic or deterministic?
- How many neural function evaluations (NFE) does it require?
- Can it use the checkpoint without retraining?

**NFE** counts denoiser evaluations, a better first-order latency proxy than nominal “steps” because a solver step may make more than one model call and CFG may evaluate two condition branches.

### Ancestral DDPM sampling

An ancestral sampler approximates the learned reverse Markov transition and injects Gaussian noise except at the last step. Its stochasticity can explore multiple reverse trajectories. With all training steps it is straightforward but slow; respacing uses a subset or a derived transition schedule.

The network may also predict reverse variance. Improved DDPM found learned variances allowed substantially fewer forward passes in its experiments with little sample-quality change.  Variance prediction often doubles output channels, so the sampler must split the tensor correctly.

### DDIM sampling

Denoising Diffusion Implicit Models (DDIM) preserve the DDPM training objective while defining a family of non-Markovian generative processes. One setting yields deterministic sampling.  Determinism enables repeatable trajectories and inversion/editing uses, and it made progressive distillation’s teacher composition tractable. 

Do not translate “deterministic” into “no model uncertainty.” A fixed starting noise and condition yield a fixed output, but different initial noise still gives different samples.

### Reverse SDE and probability-flow ODE

In continuous time, a forward SDE can be written

$$
dx=f(x,t)\,dt+g(t)\,dW_t,
$$

where $f$ is drift, $g$ is diffusion strength, and $W_t$ is Brownian motion. Reversing time introduces the learned score. The probability-flow ODE removes stochastic noise and adjusts the drift so its time marginals match the SDE under an exact score. 

Figure 13 shows the branch. Both routes query the same learned field, but an SDE solver and ODE solver follow different sample paths.

![Two lanes of trajectories between the same endpoints: jittering crossing paths for the reverse SDE, smooth non-crossing paths for the ODE](https://minio.canery.in/media/fig-13-sde-ode-diffusion-model-architecture.png)

*Figure 13. Score learning and trajectory choice are separable. The reverse SDE keeps stochastic diffusion; the probability-flow ODE turns generation into deterministic integration.*

Dedicated solvers exploit diffusion ODE structure. DPM-Solver analytically handles a linear part and approximates the remaining integral with high-order updates.  Its paper reported CIFAR-10 FID 4.70 at 10 NFE and 2.87 at 20 NFE for the stated setups.  Treat those as paper-specific results, not expected numbers for an arbitrary text-to-image checkpoint.

### Distillation and consistency change the learned function

Solver improvements reduce discretization error without necessarily retraining. **Distillation** instead trains a student to reproduce a more expensive teacher trajectory in fewer calls. Progressive distillation repeatedly halved a deterministic sampler and reported CIFAR-10 FID 3.0 at four steps in its setup. 

A **consistency model** learns to map points on the same probability-flow trajectory to a common endpoint. It supports one-step generation by design and can use extra steps for a quality-compute trade.  Because its training objective differs, you cannot obtain a consistency model merely by selecting “one step” on an ordinary DDPM checkpoint.

### Flow matching and rectified flow: adjacent, not identical

**Flow matching** trains a continuous normalizing flow by regressing a vector field associated with chosen conditional probability paths. The loss can be simulation-free: training samples points on a path rather than numerically solving the model ODE inside every update.  Diffusion paths fit inside the framework, but flow matching also allows non-diffusion paths. 

**Rectified flow** is a related construction that regresses velocity along straight interpolants between paired noise and data samples, with reflow available to straighten learned trajectories further.  Straight paths are attractive because coarse numerical steps approximate them more easily.

These methods share denoiser-like transformer architectures, conditioning systems, and ODE solvers with diffusion. They differ in the path and training target. Modern usage sometimes calls the whole family “diffusion” because the products and interfaces look alike; architecture work should retain the distinction.

Figure 14 is a selection map, not a leaderboard.

![A decision tree on whether the checkpoint may change, with each leaf carrying a sketch of the trajectory it produces, from many noisy steps to one jump](https://minio.canery.in/media/fig-14-sampler-decision-diffusion-model-architecture.png)

*Figure 14. First decide whether the checkpoint may change. If not, choose a compatible stochastic or deterministic solver; if yes, distillation or consistency training can alter the NFE frontier.*

### One classifier-free-guided inference step

At noise level $σ_i$, a conditional system performs the following conceptual sequence:

1. Scale the current latent according to the model’s input preconditioning.
2. Build the time/noise embedding.
3. Run the denoiser with null and real conditions, often as one doubled batch.
4. Combine outputs with CFG.
5. Convert the configured target into the denoised quantity required by the solver.
6. Advance from $σ_i$ to $σ_{i-1}$, optionally adding stochastic noise.

Figure 15 makes the two condition branches and one solver update explicit.

![Unconditional and conditional predictions define one ray, with guided tips marked at guidance scales of one, three and six along it](https://minio.canery.in/media/fig-15-cfg-step-diffusion-model-architecture.png)

*Figure 15. CFG changes the predicted field before integration. The solver sees one guided prediction; it does not know whether that prediction came from one condition branch or two.*

The order matters. Mixing outputs after converting to incompatible parameterizations or using a schedule that starts at a noise level the model did not train on creates subtle drift. One published analysis found common schedules with nonzero terminal SNR produced a train-inference mismatch and proposed zero-terminal-SNR rescaling, $v$ prediction, starting at the last timestep, and CFG rescaling as a coordinated correction. 

### Choosing the backbone and trajectory together

Figure 16 positions four backbone families qualitatively. It is not measured data. A U-Net concentrates computation through locality and a pyramid. U-ViT keeps the long skips but mixes tokens globally. DiT uses shared transformer blocks over image tokens. MM-DiT adds modality-specific capacity and joint interactions. Token count, training scale, and condition structure decide more than fashion.

![A qualitative map placing U-Net, U-ViT, DiT and MM-DiT by how far their token mixing reaches and how separately they treat modalities](https://minio.canery.in/media/fig-16-backbone-map-diffusion-model-architecture.png)

*Figure 16. U-Net is the locality-heavy choice; U-ViT keeps its long skips while dropping convolutional resampling; DiT is the uniform scalable token model; MM-DiT earns its extra structure when modality streams need different transformations and bidirectional interaction.*

## The math

This section compresses the discrete DDPM derivation and then connects it to scores and continuous dynamics. It reuses the worked example’s notation.

| Symbol           | Meaning                                       | Shape or range                  |
| ---------------- | --------------------------------------------- | ------------------------------- |
| $x_0$          | clean data sample                             | data shape                      |
| $x_t$          | sample corrupted to timestep$t$             | same as$x_0$                  |
| $T$            | training diffusion horizon                    | positive integer                |
| $β_t$         | forward variance at step$t$                 | $(0,1)$                       |
| $α_t$         | retained variance factor,$1-β_t$           | $(0,1)$                       |
| $\bar\alpha_t$ | cumulative product$`\prod_{s=1}^t\alpha_s`$ | $(0,1)$                       |
| $ε$           | standard Gaussian noise                       | same as$x_0$                  |
| $q$            | fixed forward distribution                    | distribution                    |
| $p_θ$         | learned reverse distribution                  | distribution                    |
| $μ_θ,Σ_θ$  | learned/derived reverse mean and covariance   | data shape / covariance         |
| $s_θ$         | learned score                                 | same as$x_t$                  |
| $c$            | optional condition                            | label, tokens, map, or features |

### From many noise steps to one

The forward transition can be reparameterized as

$$
x_t=\sqrt{\alpha_t}x_{t-1}+\sqrt{1-\alpha_t}\epsilon_t,
\qquad \epsilon_t\sim\mathcal N(0,I).
$$

Each step scales the previous state and adds independent standard Gaussian noise.

Because a linear combination of independent Gaussians is Gaussian, composing transitions gives

$$
q(x_t\mid x_0)=
\mathcal N\!\left(x_t;\sqrt{\bar\alpha_t}x_0,(1-\bar\alpha_t)I\right).
$$

The entire forward chain up to $t$ is therefore summarized by one scalar $\bar\alpha_t$.

Reparameterization produces the training equation used earlier:

$$
x_t=\sqrt{\bar\alpha_t}x_0+\sqrt{1-\bar\alpha_t}\epsilon,
\qquad \epsilon\sim\mathcal N(0,I).
$$

Training can draw $t$ uniformly or from another proposal, then construct its noisy input in constant sequential depth.

<details>
<summary>Deriving the closed form for two steps</summary>

Apply two transitions:

$$
x_2=\sqrt{\alpha_2}
\left(\sqrt{\alpha_1}x_0+\sqrt{1-\alpha_1}\epsilon_1\right)
+\sqrt{1-\alpha_2}\epsilon_2.
$$

The clean coefficient becomes $`\sqrt{\alpha_1\alpha_2}=\sqrt{\bar\alpha_2}`$.

The two independent noise terms have total variance

$$
\alpha_2(1-\alpha_1)+(1-\alpha_2)
=1-\alpha_1\alpha_2
=1-\bar\alpha_2.
$$

Their normalized sum is another standard Gaussian, which gives the closed form. Induction repeats the same argument for any $t$.

</details>

### The tractable posterior used during training

Although $q(x_{t-1}\mid x_t)$ is unknown without the data distribution, conditioning additionally on $x_0$ makes the posterior Gaussian:

$$
q(x_{t-1}\mid x_t,x_0)
=\mathcal N\!\left(x_{t-1};\tilde\mu_t(x_t,x_0),\tilde\beta_t I\right),
$$

where

$$
\tilde\mu_t
=\frac{\sqrt{\bar\alpha_{t-1}}\beta_t}{1-\bar\alpha_t}x_0
+\frac{\sqrt{\alpha_t}(1-\bar\alpha_{t-1})}{1-\bar\alpha_t}x_t,
$$

and

$$
\tilde\beta_t
=\frac{1-\bar\alpha_{t-1}}{1-\bar\alpha_t}\beta_t.
$$

The posterior mean is a schedule-dependent weighted combination of the clean sample and current noisy sample; its variance is known from the schedule.

At generation time $x_0$ is absent. Substituting the network-derived estimate $\hat x_0$ into this posterior—or algebraically expressing it through $\hat\epsilon$—produces the learned reverse mean.

### Why a simple MSE can train a probabilistic model

The negative log-likelihood admits a variational upper bound because the fixed forward chain is an approximate posterior over latents. Its terms can be grouped into endpoint reconstruction, prior matching, and intermediate Kullback–Leibler (KL) divergences:

$$
\mathcal L_{VLB}
=\mathcal L_0+\sum_{t=2}^{T}\mathcal L_{t-1}+\mathcal L_T.
$$

$\mathcal L_{t-1}$ compares the tractable forward posterior with the learned reverse transition at one noise level; $\mathcal L_T$ compares the final forward distribution with the prior.

With Gaussian transitions and an $ε$ parameterization, the intermediate mean-matching terms reduce to weighted squared noise-prediction errors. DDPM found that a simplified unweighted form worked well for sample quality even though it is not the original bound’s exact weighting. 

$$
\mathcal L_{simple}
=\mathbb E_{t,x_0,\epsilon}
\left[\lVert\epsilon-\epsilon_\theta(x_t,t)\rVert_2^2\right].
$$

The neural training problem is ordinary regression over synthetically corrupted examples, while the probabilistic interpretation determines how those predictions become reverse transitions.

### Noise prediction and score prediction

For the Gaussian corruption kernel,

$$
\nabla_{x_t}\log q(x_t\mid x_0)
=-\frac{x_t-\sqrt{\bar\alpha_t}x_0}{1-\bar\alpha_t}
=-\frac{\epsilon}{\sqrt{1-\bar\alpha_t}}.
$$

Predicting noise is equivalent to predicting the conditional score up to a known scale and sign.

The optimal denoising regressor averages over all clean samples that could have produced $x_t$. That conditional expectation yields the marginal score needed by reverse dynamics, which is why supervised-looking denoising learns a generative field rather than merely memorizing individual corruptions.

### Reverse SDE, probability-flow ODE, and flow matching

For forward SDE drift $f(x,t)$ and diffusion magnitude $g(t)$, the reverse-time SDE has drift corrected by the score:

$$
dx=\left[f(x,t)-g(t)^2\nabla_x\log p_t(x)\right]dt+g(t)d\bar W_t.
$$

$\bar W_t$ is reverse-time Brownian motion. In generation, time is integrated from the noisy endpoint toward data, and the learned $s_θ(x,t)$ replaces the unknown score.

The corresponding probability-flow ODE is

$$
\frac{dx}{dt}=f(x,t)-\frac{1}{2}g(t)^2\nabla_x\log p_t(x).
$$

The factor of one half accompanies removal of the stochastic diffusion term so the ODE shares time marginals with the SDE under the exact field. 

Flow matching instead specifies a probability path $p_t$ and learns a velocity $u_t(x)$ satisfying the continuity equation

$$
\partial_t p_t(x)+\nabla\cdot\bigl(p_t(x)u_t(x)\bigr)=0.
$$

The equation says probability mass is transported by a vector field without appearing or disappearing. Diffusion probability paths are one option; optimal-transport-like or straight interpolants are others. 

This is the formal boundary: score-based diffusion learns the score needed to reverse an SDE or construct its ODE; flow matching directly regresses a transport velocity for a chosen path. Their networks and solvers may look nearly identical while their supervised targets do not.

## Implementation

The following PyTorch program trains a tiny $ε$-predicting DDPM on a four-component distribution of 2-D points. It deliberately uses an MLP instead of an image U-Net so every diffusion operation is visible. Replace the MLP with a U-Net or DiT and the schedule/training interfaces remain the same.

```python
import math
import torch
from torch import nn


device = "cuda" if torch.cuda.is_available() else "cpu"
T = 200

beta = torch.linspace(1e-4, 0.02, T, device=device)  # Toy linear schedule.
alpha = 1.0 - beta
alpha_bar = torch.cumprod(alpha, dim=0)


def gather(values, t, ndim):
    """Gather one schedule scalar per item and add broadcast dimensions."""
    return values[t].reshape(t.shape[0], *([1] * (ndim - 1)))


def time_features(t, width=32):
    """Fourier features let one network vary smoothly across noise levels."""
    half = width // 2
    freq = torch.exp(
        -math.log(10_000) * torch.arange(half, device=t.device) / (half - 1)
    )
    phase = (t.float() / (T - 1))[:, None] * freq[None] * 1_000
    return torch.cat([phase.sin(), phase.cos()], dim=1)


class EpsilonMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2 + 32, 128), nn.SiLU(),
            nn.Linear(128, 128), nn.SiLU(),
            nn.Linear(128, 2),
        )

    def forward(self, x_t, t):
        return self.net(torch.cat([x_t, time_features(t)], dim=1))


def sample_data(batch):
    centers = torch.tensor(
        [[-2.0, -2.0], [-2.0, 2.0], [2.0, -2.0], [2.0, 2.0]],
        device=device,
    )
    choice = torch.randint(0, len(centers), (batch,), device=device)
    return centers[choice] + 0.25 * torch.randn(batch, 2, device=device)


def training_loss(model, x_0):
    t = torch.randint(0, T, (x_0.shape[0],), device=device)
    eps = torch.randn_like(x_0)
    a = gather(alpha_bar, t, x_0.ndim)
    x_t = a.sqrt() * x_0 + (1.0 - a).sqrt() * eps
    return (model(x_t, t) - eps).square().mean()


@torch.no_grad()
def ddpm_sample(model, batch):
    x = torch.randn(batch, 2, device=device)
    for step in reversed(range(T)):
        t = torch.full((batch,), step, device=device, dtype=torch.long)
        eps_hat = model(x, t)

        # Convert predicted noise into the DDPM reverse mean.
        mean = (
            x - beta[step] / (1.0 - alpha_bar[step]).sqrt() * eps_hat
        ) / alpha[step].sqrt()

        if step > 0:
            posterior_var = (
                beta[step]
                * (1.0 - alpha_bar[step - 1])
                / (1.0 - alpha_bar[step])
            )
            x = mean + posterior_var.sqrt() * torch.randn_like(x)
        else:
            x = mean
    return x


torch.manual_seed(7)
model = EpsilonMLP().to(device)
opt = torch.optim.AdamW(model.parameters(), lr=2e-3)

for update in range(3_000):
    loss = training_loss(model, sample_data(512))
    opt.zero_grad(set_to_none=True)
    loss.backward()
    opt.step()

points = ddpm_sample(model, 16)
print(points.cpu().round(decimals=2))
```

The seed is fixed before the model is built, so one machine and one PyTorch build reproduce the same sixteen coordinates on every run; they shift across devices and library versions. What should hold either way is that the points cluster around the four centers. Three details transfer directly to image-scale systems.

First, `training_loss` jumps to a random timestep with the closed-form forward equation. It does not run a 200-step corruption loop. Second, the model receives both $x_t$ and $t$; removing the time features asks one function to solve incompatible denoising problems without telling it which problem is active. Third, the reverse loop is sequential even though each model call processes the batch in parallel.

### What production code adds

An image system needs more than swapping in convolutions:

- exponential moving average (EMA) weights for evaluation; OpenAI’s released training recipes sample from EMA checkpoints, not merely the latest optimizer weights ;
- mixed precision, gradient scaling, distributed data parallelism, activation checkpointing, and memory-efficient attention;
- exact data/latent scaling and preprocessing stored with the checkpoint;
- conditioning dropout for CFG and attention masks for variable-length text;
- prediction-type-aware conversions, learned variance handling, clipping or dynamic thresholding where appropriate;
- solver tests that compare one-step updates against a trusted implementation at edge timesteps.

For architecture debugging, log tensor shapes and semantic ranges at the interfaces from Figure 4. A finite output with the right shape can still be wrong because a latent scale, $σ$ convention, token padding mask, or target type is mismatched.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** treating a scheduler name as enough checkpoint metadata. Two implementations can both say “DDIM” while using different timestep indexing, alpha conventions, prediction targets, terminal SNR, or latent scaling. The symptom is plausible but washed-out, overexposed, or unstable output—not necessarily a shape error.

### “Diffusion” is an overloaded family name

DDPM, score-SDE, probability-flow ODE, flow matching, and rectified flow share a noise-to-data product shape, but not one training objective. Use the exact path and target when reproducing a model. Flow matching subsumes diffusion paths as options; that does not make every flow a diffusion process. 

### A stronger condition can be a narrower distribution

High CFG often makes a prompt more obvious while reducing variation, exaggerating contrast, or creating artifacts. Classifier guidance experiments explicitly showed a fidelity-diversity trade.  Evaluate several seeds and measure coverage; do not select guidance solely from one attractive sample.

### More sampling steps are not monotonically better

A solver has a stability region and an error profile. A schedule trained with one endpoint or target may not benefit from arbitrary respacing. Distilled models are optimized for a particular small-step regime, while an off-the-shelf ODE solver assumes a sufficiently smooth field. Match the solver to the checkpoint and validate step-count changes empirically.

### A latent model cannot denoise information its encoder deleted

If small text, faces, or high-frequency patterns reconstruct poorly through $D(E(x))$ before diffusion training, the denoiser cannot exceed that representation ceiling reliably. Test autoencoder reconstruction separately from generation. Pixel-space super-resolution or a different first-stage model may be the correct repair.

### Transformer scaling is not free

Patch size and latent resolution determine token count. Full self-attention grows quadratically in that count, so moving from $32\times32$ to $64\times64$ latent tokens at the same patch size creates four times the tokens and sixteen times the raw pairwise attention entries. That arithmetic is architectural, not a benchmark claim. Windowed, factorized, sparse, or efficient attention changes the cost and interaction pattern.

### FID is not “image quality”

Fréchet Inception Distance (FID) compares the first two moments of real and generated feature distributions and was introduced in the TTUR work.  It mixes fidelity and coverage, depends on feature extraction and preprocessing, and can miss prompt faithfulness. Precision/recall metrics were developed to separate sample quality from distribution coverage more directly.  Use FID with precision/recall, condition-alignment tests, human evaluation, memorization checks, and task-specific failure suites rather than treating one scalar as the objective. 

### The denoising loss does not certify safety or originality

A low validation loss says the model predicts its training target on held-out corruptions. It does not establish that training data was licensed, sensitive content was removed, outputs are unbiased, or memorized examples cannot be elicited. Those are dataset governance, privacy, evaluation, and deployment-control problems surrounding the architecture.

### Shape correctness is not semantic correctness

Text embeddings with the wrong normalization can still have the expected width. Latents encoded with a different scale can still be $`B\times4\times64\times64`$. An $ε$ checkpoint interpreted as $v$ still returns the correct number of channels. Unit-test conversions with synthetic values like the worked example before judging generations.

## Key takeaways

- A diffusion system has five separable design axes: representation, probability path, learned field, conditioning interface, and numerical solver; most design confusion comes from mixing their responsibilities.
- U-Net, U-ViT, DiT, and MM-DiT are backbone choices. They do not, by themselves, determine the noising process, prediction target, guidance rule, or sampler.
- Noise, clean-data, score, and velocity predictions encode convertible information, but their optimization and numerical conditioning differ; checkpoint metadata must name the parameterization.
- Classifier-free guidance alters the conditional field before a solver step. It trades adherence/fidelity against coverage and costs conditional plus unconditional prediction work.
- DDPM/DDIM, reverse SDE/ODE solvers, distillation, consistency models, flow matching, and rectified flow occupy different points in the path–solver–training design space; similar inference code does not make their objectives identical.

## Try it yourself

1. In the worked example, recompute $x_t$ with $`\bar\alpha_t=0.36`$. Which coefficient multiplies signal and which multiplies noise? What is the new SNR?

<details><summary>Answer</summary>

$`\sqrt{\bar\alpha_t}=0.6`$ multiplies $x_0$ and $`\sqrt{1-\bar\alpha_t}=0.8`$ multiplies $ε$. The SNR is $0.36/0.64=0.5625$, so noise power now exceeds signal power.

</details>

2. A latent is $`B\times16\times64\times64`$. A DiT uses $2\times2$ patches. How many image tokens does each example contain? What happens if patch size becomes $1\times1$?

<details><summary>Answer</summary>

With $P=2$, $N=(64/2)^2=1{,}024$ tokens. With $P=1$, $N=4{,}096$: four times as many tokens and, for full attention, sixteen times as many query-key pairs per head.

</details>

3. You inherit a checkpoint that generates recognizable but overexposed images. List four metadata checks before changing network weights.

<details><summary>Answer</summary>

Check the prediction target ($ε$, $x_0$, or $v$), training and inference timestep indexing, terminal SNR/start noise level, latent scaling, and CFG/rescale convention. Any four of those can create a semantic mismatch while preserving tensor shapes.

</details>

## References

### Foundational diffusion and score models

1. Sohl-Dickstein et al. [*Deep Unsupervised Learning using Nonequilibrium Thermodynamics*](https://proceedings.mlr.press/v37/sohl-dickstein15.html). ICML, 2015.
2. Ho, Jain & Abbeel. [*Denoising Diffusion Probabilistic Models*](https://papers.nips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html). NeurIPS, 2020.
3. Song & Ermon. [*Generative Modeling by Estimating Gradients of the Data Distribution*](https://papers.nips.cc/paper_files/paper/2019/hash/3001ef257407d5a371a96dcd947c7d93-Abstract.html). NeurIPS, 2019.
4. Song et al. [*Score-Based Generative Modeling through Stochastic Differential Equations*](https://arxiv.org/abs/2011.13456). ICLR, 2021.
5. Nichol & Dhariwal. [*Improved Denoising Diffusion Probabilistic Models*](https://proceedings.mlr.press/v139/nichol21a.html). ICML, 2021.
6. Kingma et al. [*Variational Diffusion Models*](https://proceedings.neurips.cc/paper/2021/hash/b578f2a52a0229873fefc2a4b06377fa-Abstract.html). NeurIPS, 2021.
7. Karras et al. [*Elucidating the Design Space of Diffusion-Based Generative Models*](https://arxiv.org/abs/2206.00364). NeurIPS, 2022.

### Architecture and conditioning

8. Ronneberger, Fischer & Brox. [*U-Net: Convolutional Networks for Biomedical Image Segmentation*](https://arxiv.org/abs/1505.04597). MICCAI, 2015.
9. Vaswani et al. [*Attention Is All You Need*](https://proceedings.neurips.cc/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html). NeurIPS, 2017.
10. Rombach et al. [*High-Resolution Image Synthesis with Latent Diffusion Models*](https://openaccess.thecvf.com/content/CVPR2022/html/Rombach_High-Resolution_Image_Synthesis_With_Latent_Diffusion_Models_CVPR_2022_paper.html). CVPR, 2022.
11. Peebles & Xie. [*Scalable Diffusion Models with Transformers*](https://openaccess.thecvf.com/content/ICCV2023/html/Peebles_Scalable_Diffusion_Models_with_Transformers_ICCV_2023_paper.html). ICCV, 2023.
12. Bao et al. [*All Are Worth Words: A ViT Backbone for Diffusion Models*](https://openaccess.thecvf.com/content/CVPR2023/html/Bao_All_Are_Worth_Words_A_ViT_Backbone_for_Diffusion_Models_CVPR_2023_paper.html). CVPR, 2023.
13. Esser et al. [*Scaling Rectified Flow Transformers for High-Resolution Image Synthesis*](https://arxiv.org/abs/2403.03206). ICML, 2024.
14. Radford et al. [*Learning Transferable Visual Models From Natural Language Supervision*](https://proceedings.mlr.press/v139/radford21a.html). ICML, 2021.
15. Raffel et al. [*Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer*](https://jmlr.org/papers/v21/20-074.html). JMLR, 2020.
16. Saharia et al. [*Photorealistic Text-to-Image Diffusion Models with Deep Language Understanding*](https://arxiv.org/abs/2205.11487). NeurIPS, 2022.
17. Nichol et al. [*GLIDE*](https://proceedings.mlr.press/v162/nichol22a.html). ICML, 2022.
18. Dhariwal & Nichol. [*Diffusion Models Beat GANs on Image Synthesis*](https://papers.nips.cc/paper/2021/hash/49ad23d1ec9fa4bd8d77d02681df5cfa-Abstract.html). NeurIPS, 2021.
19. Ho & Salimans. [*Classifier-Free Diffusion Guidance*](https://arxiv.org/abs/2207.12598). NeurIPS Workshop, 2021.

### Sampling, flows, and acceleration

20. Song, Meng & Ermon. [*Denoising Diffusion Implicit Models*](https://arxiv.org/abs/2010.02502). ICLR, 2021.
21. Lu et al. [*DPM-Solver*](https://proceedings.neurips.cc/paper_files/paper/2022/hash/260a14acce2a89dad36adc8eefe7c59e-Abstract-Conference.html). NeurIPS, 2022.
22. Salimans & Ho. [*Progressive Distillation for Fast Sampling of Diffusion Models*](https://arxiv.org/abs/2202.00512). ICLR, 2022.
23. Song et al. [*Consistency Models*](https://proceedings.mlr.press/v202/song23a.html). ICML, 2023.
24. Lipman et al. [*Flow Matching for Generative Modeling*](https://arxiv.org/abs/2210.02747). ICLR, 2023.
25. Liu, Gong & Liu. [*Flow Straight and Fast*](https://arxiv.org/abs/2209.03003). ICLR, 2023.
26. Hang et al. [*Efficient Diffusion Training via Min-SNR Weighting Strategy*](https://arxiv.org/abs/2303.09556). ICCV, 2023.
27. Lin et al. [*Common Diffusion Noise Schedules and Sample Steps are Flawed*](https://arxiv.org/abs/2305.08891). WACV, 2024.

### Evaluation and official implementations

28. Heusel et al. [*GANs Trained by a Two Time-Scale Update Rule*](https://proceedings.neurips.cc/paper/2017/hash/8a1d694707eb0fefe65871369074926d-Abstract.html). NeurIPS, 2017.
29. Kynkäänniemi et al. [*Improved Precision and Recall Metric for Assessing Generative Models*](https://proceedings.neurips.cc/paper/2019/hash/0234c510bc6d908b28c70ff313743079-Abstract.html). NeurIPS, 2019.
30. OpenAI. [`guided-diffusion`](https://github.com/openai/guided-diffusion). Official implementation, accessed 2026-09-20.
31. OpenAI. [`improved-diffusion`](https://github.com/openai/improved-diffusion). Official implementation, accessed 2026-09-20.
32. CompVis. [`latent-diffusion`](https://github.com/CompVis/latent-diffusion). Official implementation, accessed 2026-09-20.
33. Meta AI. [`DiT`](https://github.com/facebookresearch/DiT). Official implementation, accessed 2026-09-20.
34. NVIDIA. [`edm`](https://github.com/NVlabs/edm). Official implementation, accessed 2026-09-20.
