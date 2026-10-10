# Outline — diffusion-model-architecture

## Brief

- Subject: machine learning / generative modeling
- Tier: L4 pillar
- Audience: advanced ML students and working engineers who know neural-network basics
- Promise: explain the complete architecture of a modern diffusion system—from stochastic process to denoiser, conditioning, sampler and evaluation—without conflating DDPM, score, and flow formulations
- Target: 8,500–9,500 substantive words; 15 figures

## Section budget

| Section | Budget | Reader can now… |
|---|---:|---|
| Insights + who | 220 | state what the learned network does and what the sampler does |
| Why this matters | 320 | identify which subsystem a design or failure belongs to |
| The problem | 650 | frame generation as learning a reversible route between data and a simple prior |
| Worked example | 1,150 | compute one forward corruption and one denoising target by hand |
| Intuition | 750 | separate the path, learned vector field and numerical integrator |
| What is a complete diffusion system? | 650 | map all production components and interfaces |
| How does a diffusion U-Net denoise? | 900 | trace tensor shapes and conditioning through a U-Net |
| Why are transformers replacing some U-Nets? | 900 | compare U-Net, U-ViT, DiT and MM-DiT roles |
| How do text and other conditions enter? | 800 | distinguish tokenization, text encoding, cross-attention and guidance |
| What exactly should the network predict? | 700 | translate epsilon, x0, score and v parameterizations |
| How does sampling turn predictions into data? | 900 | choose among ancestral, DDIM, ODE solvers and distilled models |
| The math | 900 | derive q(x_t|x_0), posterior, loss, score and ODE views |
| Implementation | 650 | implement and audit a minimal DDPM training/sampling core |
| Limitations and common mistakes | 500 | spot taxonomy, schedule, guidance and evaluation errors |
| Key takeaways + exercises + references | 350 | retain a durable architecture checklist |

## Figure plan

| # | Section | One job | Route | Draft caption |
|---:|---|---|---|---|
| 1 | The problem | distinguish fixed forward corruption from learned reverse transitions | architecture | A diffusion system learns the arrows pointing back; it does not learn the noise process |
| 2 | Worked example | show one 2-D numeric corruption with shapes and values | math / small multiples | At one timestep, signal and noise are mixed by known scalars |
| 3 | Intuition | separate path, vector field and solver | layers | Changing the sampler does not retrain the denoiser |
| 4 | Complete system | place encoder, denoiser, condition and sampler in one map | architecture | The denoiser is only one component of the generation system |
| 5 | U-Net | trace B×C×H×W shapes through three resolutions | architecture | Skips preserve local detail while the bottleneck carries global context |
| 6 | U-Net block | show timestep modulation inside a residual block | architecture | Time changes features throughout the network, not only at the input |
| 7 | Attention | contrast self-attention and cross-attention Q/K/V sources | architecture | The query source determines whether attention mixes image context or injects a condition |
| 8 | Transformers | trace patchify → tokens → DiT blocks → unpatchify | architecture | DiT keeps spatial shape in the token sequence rather than a resolution pyramid |
| 9 | Latent diffusion | show pixels → latent → denoise → pixels | architecture | Compression saves repeated denoiser compute but creates a reconstruction ceiling |
| 10 | Parameterization | relate x0, epsilon, score and v | math / geometry | Different targets describe the same noisy point with different conditioning |
| 11 | Training | show random-timestep training loop | flowchart / Mermaid redraw | Training observes one randomly selected noise level per example |
| 12 | SDE/ODE | show reverse SDE and probability-flow ODE branches | architecture | Same learned score can drive stochastic or deterministic trajectories |
| 13 | Samplers | choose a sampler by stochasticity, NFE and retraining | flowchart / Mermaid redraw | Sampler choice is a numerical-method decision constrained by the trained parameterization |
| 14 | Inference | show one classifier-free guided denoising step | process | CFG costs conditional and unconditional predictions, often batched together |
| 15 | Architecture choices | compare U-Net, DiT and MM-DiT across locality and modalities | quadrant | Backbone choice follows token count, compute scale and conditioning structure |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| diffusion model | Insights | generative model with a known corruption path and learned reverse/transport field | turns simple noise into data | whole article |
| forward/noising process | The problem | fixed Markov corruption | creates supervised denoising pairs | training design |
| reverse process | The problem | learned transitions toward data | generates samples | inference |
| timestep/noise level | Worked example | coordinate on the corruption path | tells the network how much signal remains | every model call |
| SNR | Worked example | signal power relative to noise | indexes task difficulty and weights losses | schedules and objectives |
| score | Intuition | gradient of log density | defines reverse-time dynamics | score/SDE view |
| sampler / solver | Intuition | numerical integration rule | converts field evaluations into a path | latency/quality tradeoff |
| denoiser | Complete system | time-conditioned neural field estimator | predicts noise, clean data, velocity or score | training and sampling |
| U-Net | U-Net section | multiscale encoder-decoder with skips | combines local detail and broad context | convolutional backbone |
| residual block | U-Net section | learned update plus identity skip | stabilizes deep feature transformation | backbone internals |
| self-attention | Attention subsection | attention within noisy tokens | global spatial mixing | long-range structure |
| cross-attention | Conditioning section | noisy queries attend to condition tokens | injects text/layout/context | conditional generation |
| token/embedding | Conditioning section | vector representation of a discrete unit | interface between encoder and denoiser | transformer conditioning |
| classifier-free guidance | Conditioning section | conditional/unconditional extrapolation | strengthens condition adherence | inference tuning |
| latent diffusion | Conditioning section | diffusion in autoencoder representation | cuts spatial compute | high-resolution generation |
| DiT | Transformer section | transformer over noisy latent patches | scalable uniform backbone | large compute/data regimes |
| MM-DiT | Transformer section | separate modality streams with joint attention | bidirectional text-image mixing | multimodal generators |
| epsilon/x0/v prediction | Parameterization section | alternative regression targets | changes optimization and solver interface | model configuration |
| DDPM/DDIM | Sampling section | stochastic ancestral vs implicit deterministic-compatible sampling | different trajectories using related training | baseline sampling |
| SDE/ODE | Sampling section | stochastic/deterministic continuous dynamics | unifies score-based samplers | solver design |
| flow matching/rectified flow | Sampling section | vector-field regression along prescribed paths | non-diffusion transport alternative | modern transformer systems |
| NFE | Sampling section | number of network evaluations | practical latency proxy | compare samplers |
| EMA | Implementation | moving average of model weights | smoother sampling checkpoint | training practice |
| FID / precision / recall | Limitations | feature-distribution metrics | quantify fidelity and coverage imperfectly | evaluation |
