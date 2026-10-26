# Series context — Diffusion Models

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** CS students and working engineers. Part 1 assumes no generative-modelling
  background; Parts 2–8, 10, 11 assume it; Parts 9 and 12 drop to intermediate on purpose.
- **Shape:** hybrid — a two-rung ladder (1 → 2) whose upper rung fans out into nine sibling spokes.
- **Shared promise:** after the series a reader can read any diffusion paper's method section,
  place its contribution on a named design axis, and predict which axis a failure belongs to.
- **Notation:** $x_0$ clean data, $x_t$ noisy state, $\epsilon$ the Gaussian draw, $\beta_t$
  per-step variance, $\alpha_t = 1-\beta_t$ (**always per-step**; never the literature's
  signal coefficient — write √ᾱ_t and √(1−ᾱ_t)), $\bar\alpha_t = \prod_{s\le t}\alpha_s$.
  "Forward" means data → noise. The learned network is **the denoiser**, its architecture family
  **the backbone**; the procedure that calls it is **the sampler** (never "the model"); the fixed
  $\{\beta_t\}$ is **the schedule**. Established terms, not to be redefined: forward/reverse
  process, timestep, ε-prediction, seed, score, conditional mean, ELBO, forward posterior, SNR,
  log-SNR λ, w(λ), VP/VE, token, patch size, adaLN, skip connection, [MASK], Gen PPL.
- **Recurring example:** part 1's 4×4 patch at ᾱ = 0.64 (√ᾱ = 0.8, √(1−ᾱ) = 0.6):
  $x_0 = [[0.95,0.60,-0.30,-0.85],[0.80,0.45,-0.55,-0.90],[0.55,0.10,-0.70,-0.95],[0.25,-0.20,-0.85,-1.00]]$,
  $\epsilon = [[-0.55,1.40,0.45,-1.10],[0.85,-1.35,-0.25,0.70],[1.25,0.30,-0.95,0.15],[-1.05,0.90,1.45,-1.10]]$,
  $x_t = [[0.43,1.32,0.03,-1.34],[1.15,-0.45,-0.59,-0.30],[1.19,0.26,-1.13,-0.67],[-0.43,0.38,0.19,-1.46]]$.
  Part 2 uses a 2×2 patch at the same ᾱ; part 11 quantises the 4×4 to tokens of four grey levels.
  Reuse these; do not invent a third patch.
- **Recurring visual motif:** a bright crescent on a dark field, drawn as discrete cells, clean
  and noised; `motif()` and the seed-7 noise are copied into each part's
  `_figures.py`/`_social.py`.
- **Recurring instrument (parts 5–11):** "crescent world", a Gaussian mixture with exact E[x₀|x_t]
  (`World.denoise`); part 10 adds 4-frame clips; part 11 tokenises it (nine brightness levels,
  72 images, an exact lookup denoiser). Reuse it, not another toy, and say so where its exact
  denoiser hides trained-network error or exposure bias.

## Part status

From part 4 on, gate PASS includes `--social`.

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | what-a-diffusion-model-actually-does | published 2026-09-22 | why undoing noise can invent an image | the four moving parts, denoiser marked as Part 2's subject |
| 2 | diffusion-model-architecture | ready, unpublished | the parts and their seams | five design axes, one per spoke |
| 3 | diffusion-math-derived | ready (gate PASS 2026-09-25) | where the MSE loss comes from | w(λ) to 5; reverse SDE/ODE to 6 |
| 4 | diffusion-backbones-unet-to-dit | ready (gate PASS 2026-10-03) | the denoiser block by block | ControlNet and adapters to 8; training cost to 5 |
| 5 | training-a-diffusion-model | ready (gate PASS 2026-10-08) | decisions before the first gradient step | sampler error to 6; guidance rescaling to 8; FID's limits to 9 |
| 6 | diffusion-samplers-and-solvers | ready (gate PASS 2026-10-09) | 1,000 steps into 20 | 20 steps into 1 to 7; guidance under high-order solvers to 8 |
| 7 | few-step-diffusion-distillation | ready (gate PASS 2026-10-16) | 20 steps into 1 | guidance distillation to 8; precision/recall to 9 |
| 8 | controlling-diffusion-models | ready (gate PASS 2026-10-19) | obeying something other than a prompt | precision/recall to 9; memorised photos to 12 |
| 9 | evaluating-generative-models | ready (gate PASS 2026-10-21) | what FID measures and hides | measuring memorisation to 12 |
| 10 | diffusion-beyond-images | ready (gate PASS 2026-10-21) | non-grid data | categorical data to 11 |
| 11 | discrete-diffusion-language-models | ready (gate PASS 2026-10-23) | denoising tokens | none; names no later part |
| 12 | diffusion-memorization-and-provenance | planned | when a sample stops being new | — |

## Knowledge established

### Part 1 — What a Diffusion Model Actually Does

- The forward process is a zero-parameter formula; the network exists because it cannot be run
  backwards, and its targets are free. **Averaging:** the MSE-optimal denoiser returns E[x₀|x_t], a
  correct blur at high noise (Tweedie). **Amplification:** an ε̂ error reaches the image
  ×√(1−ᾱ)/√ᾱ (×0.75 at ᾱ 0.64, ×7.00 at 0.02); part 6 builds on it.
- Novelty comes from the seed, bounded by measured memorisation (part 12). Four moving parts:
  schedule, training loop, denoiser, sampler. DDPM linear ᾱ_T = 4.0358×10⁻⁵.

### Part 3 — Where the Diffusion MSE Loss Comes From

- Five-step chain from the ELBO to one squared error per step, four steps exact; cite
  `#how-does-the-bound-become-one-squared-error-per-step`. Every loss = ½∫ w(λ)‖ε − ε̂‖² dλ (Kingma &
  Gao); steps 2–100 hold 34% of DDPM's ELBO weight.

### Part 4 — Diffusion Backbones: U-Net to DiT, Block by Block

- SD 1.5 U-Net 859.5M params, 803.27 GFLOP per 512 px call; DiT-XL/2 118.62 GMAC at 256 px.
  Attention share of a block = N/(N+6D). DiT's "Gflops" are multiply-adds (2 FLOPs each).

### Part 5 — Training a Diffusion Model

- √ᾱ_T 0.068265 on SD's scaled-linear schedule; x₀ and v targets survive zero terminal SNR, ε
  does not. SNR weighting starves λ = −9; EMA 0.9999's half-life is 6,931 steps.

### Part 6 — Diffusion Samplers and Solvers

- **Frame:** DDIM coordinates, dx/dσ = (x − D)/σ; DDIM = Euler in σ = DPM-Solver-1; "Euler a" =
  DDPM ancestral. Count NFE. **Measured** calls to one grey level (ρ = 7, against RK4): DDIM 100, Heun 49, 2M 25,
  DPM-Solver-3 16; with an exact denoiser deterministic samplers win.

### Part 7 — Few-Step Diffusion and Distillation

- **Frame:** a jump σ → σ′ is a DDIM step whose D̄ is the 1/s²-weighted path average of D;
  distillation methods learn D̄ at different (σ, σ′). **Measured** one-call flips: regression 3.0%,
  PD 3.7%, CD 3.2%; DMD 15–16%, on one crescent by update 100.

### Part 8 — Controlling Diffusion Models

- **Convention:** D_w = D_u + w(D_c − D_u), w = 1 unguided (Ho & Salimans' w + 1); control lives
  in the sampler, in new inputs that start at zero, or in the weights.
- **Measured:** exact model faint 52.9% → 9.5% at w = 3; only autoguidance improved the trained
  net. Prior preservation cuts drift 100% → 0–0.2%; fine-tunes copy the photos' brightness spread.
  SD 1.5's ControlNet: 361,279,120 parameters (42.0%).

### Part 9 — Evaluating Generative Models

- **Instrument:** `evaluate.py` (numpy): five generators with known defects; FD on pixels and five
  feature sets, KID, precision/recall, density/coverage. Pixel-space k-NN metrics are hypersensitive.
- **Measured:** opposite defects tie at FD 3.6221 (P/R/C 0.817/0.394/0.504 vs 0.0005/1.000/0.0005);
  a copier's FD 0.0133 beats the perfect generator's 0.0143. Guided recall rises again at w = 7.5
  from 4 stray samples; coverage 0.984 → 0.266.
- **Quoted:** StyleGAN-XL vs DiT-XL/2: FID 2.26 vs 2.27, human error 15.3 vs 28.6% (Stein 2023).
  A flip seen with 6 repeats vanished at 24: repeat before trusting a noisy gap.

### Part 10 — Diffusion Beyond Images

- **Frame:** the forward step is shape-blind; a modality changes what the denoiser looks across:
  size (latents cut audio 32×, video 48×), symmetry, geometry, or how evidence enters.
- **Measured** (`beyond.py`): independent per-frame noise 0 coherent clips, rot90-warped noise
  99.56%, a joint model 99.39%; replacement forecasts 17/63/96% from 1/2/3 frames. **Quoted:** VDM
  FVD 451.45 vs 136.22 (replacement vs reconstruction guidance).

### Part 11 — Discrete Diffusion Language Models

- **Frame:** mask tokens instead of adding noise; the loss is BERT's masked cross-entropy weighted
  1/t, an any-order autoregressive loss, tight for an exact denoiser. Several tokens per step draw
  from the product of marginals; most-confident-first decoders return modes, not samples.
- **Measured** (`tokens.py`, 72 images): 2/4/8 tokens per step 17.9/0.3/0% valid; MDLM ancestral
  64/1,024 steps 51.9/95.8%; a certainty threshold exact in 7.24 calls. Certainty order stays exact;
  drawn-token ranking finds 8 of 72 images, LLaDA's greedy default 4.
- **Computed:** float32's race gives a token of weight c a share x/(eˣ − 1) of its chance,
  x = 2⁻²⁴/c. **Quoted:** Zheng et al. Gen PPL 31.24 (float32) vs 126.11 (float64); LLaDA GSM8K
  21.3 → 70.0 with low-confidence remasking.

## Decisions to preserve

- **No body H1.** Ledger keys are HTML comments next to the sentence they support.
- **Naming earlier parts:** since 2026-10-09 (owner), name earlier parts by title in plain text,
  live or not, and list each spot in the manifest's *Series links to add*; the owner adds links.
  Parts 1–5 predate this.
- **Toolchain:** each part copies the previous part's `assets/` toolchain, never imports across
  posts; `ROOT` is `HERE.parents[3]`. Figures and cards read every number from the shipped capture;
  files are numbered by appearance; keys `blog/<slug>/fig-NN-<name>-v1.png`. High value = bright, one
  range across panels. Spell ε̂, β̃, σ̂ out on figures (Geist Mono misplaces accents). `Axes` take
  raw values on log axes; `footnote()` raises past the canvas (5.95 px per mono glyph).
  `eyebrow()` and `label()` uppercase ASCII, so Latin notation (x_t, w) goes in `text()`.
- **Mermaid:** `_mermaid.py` needs a 45 s budget, `document.fonts.load` before `mermaid.run`,
  `wrappingWidth: 420` and part 6's opaque-label themeCSS; over ~10 nodes use TB, with block
  titles in the first node.
- **Labs:** G1 unless a part truly needs more; `access.md` records why no request was raised.
  `~/.cache/diffusion-models-lab` serves parts 4–11. Labs over ~10 min cache finished runs and
  resume; output prints relative paths only; figures and cards share one median. Freeze the script
  before the final capture (`source_sha1`); test the E4 fault at `--quick`; delete caches over a few
  MB after capture. Torch: seed the global generator in every worker job; notebook builds add
  `--extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match` to
  `uv run`.
- **Checkers:** `_overlap.py` misreads rotated axis titles and Mermaid edge labels;
  `lint_visuals.py` skips nodes under 60 × 40, so arrows onto token cells read as dangling.
  Hard-coded panel ranges clip silently: assert every plotted value fits.
- Part 2's ledger and manifest predate blog-forge 0.4; leave them unless part 2 reopens.

## Open threads

- **Publication order:** part 1 is live; parts 2–11 are ready. Part 3 links part 2's
  `#the-math`, so part 2 goes live first; parts 4–11 link no unpublished part and name earlier
  parts in plain text only (each manifest lists where). Part 2 still lacks `series`/`series_position`.
- Parts 8–11 ship feed cards only (owner's request for part 8, 2026-10-19), so their
  gates fail exactly the four Story checks; build Story frames only if the owner asks.
- Part 1 (live) errata found by part 3, unfixed: reference 16's authors are Lin, Liu, Li & Yang;
  `abar[207]` is 0.6375, not 0.6405. It links forward to nothing; add links once a target is live.
- Unfixed in gated parts: part 5's Mermaid fig-01 likely shows edges through labels;
  `samplers.py --quick` help says ~2 min (64 s measured), `distill.py --quick` ~6 min (4.5).

## Next part brief

- **Part:** 12, diffusion-memorization-and-provenance (L2, intermediate; optional in `plan.md`):
  when does a sample stop being new? **Must teach:** only part 12's row in `plan.md`, which deepens
  part 1's account of where novelty comes from; it closes the series.
- **Can assume:** part 1. Name parts 8 and 9 in plain text where used: part 8's fine-tunes copied
  their photos' brightness spread; part 9's copier beat the perfect generator on FD and handed
  measuring memorisation to 12.
- **Must not repeat:** part 9's metric mechanics or part 8's fine-tuning methods.
- **Evidence still needed:** replication and extraction studies on trained diffusion models
  (Somepalli et al., Carlini et al., both 2023), how memorisation changes as training sets grow,
  and provenance (watermarks, content credentials). Every rate keeps its model, data and match
  threshold.
- **Handoff:** none; part 12 is the last part.
