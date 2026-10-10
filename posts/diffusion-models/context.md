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
  log-SNR λ, w(λ), VP/VE, token, patch size, adaLN, skip connection.
- **Recurring example:** part 1's 4×4 patch at ᾱ = 0.64 (√ᾱ = 0.8, √(1−ᾱ) = 0.6):
  $x_0 = [[0.95,0.60,-0.30,-0.85],[0.80,0.45,-0.55,-0.90],[0.55,0.10,-0.70,-0.95],[0.25,-0.20,-0.85,-1.00]]$,
  $\epsilon = [[-0.55,1.40,0.45,-1.10],[0.85,-1.35,-0.25,0.70],[1.25,0.30,-0.95,0.15],[-1.05,0.90,1.45,-1.10]]$,
  $x_t = [[0.43,1.32,0.03,-1.34],[1.15,-0.45,-0.59,-0.30],[1.19,0.26,-1.13,-0.67],[-0.43,0.38,0.19,-1.46]]$.
  Part 2 uses a 2×2 patch at the same ᾱ. Reuse these; do not invent a third patch.
- **Recurring visual motif:** a bright crescent on a dark field, drawn as discrete cells (n = 11,
  12, 14, 32), clean and noised; `motif()` and the seed-7 noise are copied into each part's
  `_figures.py`/`_social.py`.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | what-a-diffusion-model-actually-does | published 2026-09-22 | why undoing noise can invent an image | the four moving parts, denoiser marked as Part 2's subject |
| 2 | diffusion-model-architecture | ready, unpublished | the parts and their seams | five design axes, one per spoke |
| 3 | diffusion-math-derived | ready, unpublished (gate PASS 2026-09-25) | where the MSE loss comes from | per-step weights and w(λ) to 5; reverse SDE/ODE to 6 |
| 4 | diffusion-backbones-unet-to-dit | ready, unpublished (gate and `--social` PASS 2026-10-03) | the denoiser block by block | conditioning mechanics beyond the block (ControlNet, adapters) to 8; training cost and scaling to 5 |
| 5 | training-a-diffusion-model | ready, unpublished (gate, `--social` and `render_social --check` PASS 2026-10-08) | decisions before the first gradient step | sampler error to 6 (done); guidance rescaling (Lin's fourth fix) to 8; FID's limits to 9 |
| 6 | diffusion-samplers-and-solvers | ready, unpublished (gate, `--social` and `render_social --check` PASS 2026-10-09) | 1,000 steps into 20 | 20 steps into 1 to 7; guidance under high-order solvers to 8; FID's limits to 9 |
| 7 | few-step-diffusion-distillation | planned | 20 steps into 1 | — |
| 8 | controlling-diffusion-models | planned | obeying something other than a prompt | — |
| 9 | evaluating-generative-models | planned | what FID hides | — |
| 10 | diffusion-beyond-images | planned | non-grid data | — |
| 11 | discrete-diffusion-language-models | planned | denoising tokens | — |
| 12 | diffusion-memorization-and-provenance | planned | when a sample stops being new | — |

## Knowledge established

### Part 1 — What a Diffusion Model Actually Does

- The forward process is a zero-parameter formula; the network exists only because it cannot be
  run backwards. Training targets are free (ε is drawn before it is added).
- **Averaging argument:** the MSE-optimal denoiser returns E[x₀|x_t], so a high-noise call returns
  a correct blur (Kadkhodaie §2.1, Tweedie). **Amplification argument** (part 1's own): an error δ
  in ε̂ reaches the image scaled by √(1−ᾱ)/√ᾱ — ×0.75 at ᾱ 0.64, ×7.00 at 0.02. Part 6 builds on it.
- Novelty comes from the seed, bounded by measured memorisation (Carlini, Somepalli, Kadkhodaie);
  part 12 deepens this. Four moving parts — schedule, training loop, denoiser, sampler.
- DDPM linear schedule: ᾱ_T = 4.0358×10⁻⁵. 18 sources (S01–S18).

### Part 3 — Where the Diffusion MSE Loss Comes From

- Five-step chain, four exact: Jensen → per-step KLs → equal-variance Gaussian KL = squared mean gap
  → mean through ε → drop weights. Cite `#how-does-the-bound-become-one-squared-error-per-step`.
- Worked step on part 1's top-left pixel, ᾱ 0.80 → 0.64: teacher N(0.6857, 1/9), student mean
  0.6112, KL 0.0250 nats; five prices of one error (ε 0.04, x₀ 0.0225, score 0.1111, v 0.0625).
- DDPM per-step ELBO weight: 0.2727 at t = 2, min 0.00497 at t = 349, 0.0102 at t = 1000; steps
  2–100 hold 34% of the total. Every loss = ½∫ w(λ)‖ε − ε̂‖² dλ (Kingma & Gao). Tweedie toy at
  x_t 0.43: E[x₀|x_t] = 0.3968. 23 sources, one preprint (Luo).

### Part 4 — Diffusion Backbones: U-Net to DiT, Block by Block

- **Measured (`lab/captures.json`, meta device, torch 2.14 CPU, diffusers 0.40):** SD 1.5 U-Net
  859,520,964 params, 803.27 GFLOP per 512 px call, 87% of attention comparisons at 64×64; DiT-XL/{8,4,2}
  at 256 px 7.39/29.04/118.62 GMAC, 675.1M params, adaLN 33%; SD3 MM-DiT d=24 2,028,328,000 params,
  8,437 GFLOP at 1024 px (joint attention 31.6%).
- **Attention share of a standard block = N/(N+6D)**, matching the FLOP counter to 0.1 points.
  **FLOP convention:** a multiply-add is 2 FLOPs; DiT's "Gflops" are multiply-adds. Say which.
- Memory: ZeRO's 16 B/param includes the weights; Korthikanti's formula gives SD3-2B 57.3 GB of
  activations per image at 1024 px. Traps: diffusers' `attention_head_dim` is the head count; two
  different "U-ViT"s; diffusers' DiT class counts 750M. 24 peer-reviewed sources + 2 preprints.

### Part 5 — Training a Diffusion Model

- **Computed (float64, matches Lin et al. Table 1):** √ᾱ_T is 0.068265 for SD's scaled-linear
  schedule; last λ −5.4 (SD), −10.1 (linear), −19.8 (cosine). Lin's rescale moves
  part 1's ᾱ 0.64 to 0.617.
- **Leak closed form:** a perfect deterministic sampler keeps ρ = 1/√(1−ᾱ_T+ᾱ_T(n s_b²+τ²)) of the
  brightness spread: 0.999, 0.607, 0.357 at n = 16, 4,096, 16,384 with s_b 0.3 (an assumed spread,
  not SD's). Measured with the exact denoiser within 0.02; more steps converge on 0.357.
  The rescaled schedule's 0.851 at 50 steps is DDIM's own error (part 6).
- **Targets:** an output error reaches x₀ ×e^(−λ/2) for ε (×90 at λ = −9), the ε estimate
  ×e^(λ/2) for x₀, ≤1 both ways for v; x₀ and v survive zero terminal SNR, ε does not.
- **Weighting and EMA (measured, x₀-net, 3 seeds):** SNR weighting starves λ = −9 (samplers blew
  up 80/84); constant and Min-SNR-5 sample alike, so
  the toy does not reproduce Min-SNR's speed-up. EMA 0.9999: half-life 6,931 steps; 61% random
  start at 5k steps, 1.8% at 40k.
- **Instrument:** "crescent world", a Gaussian mixture with exact E[x₀|x_t] (`World.denoise`),
  DDIM written through x₀, sliced Wasserstein sample distance (blow-up > 10), per-level excess
  error on λ ∈ [−9, 9]. Reuse it; do not build another toy.
- 31 sources (S01–S31), 63 claims; Lin et al. Fig. 3 reused unchanged (CC BY-SA 4.0).

### Part 6 — Diffusion Samplers and Solvers

- **Frame:** DDIM coordinates, dx/dσ = (x − D)/σ. DDIM = Euler in σ = EDM's Euler = DPM-Solver-1 =
  exponential Euler; "Euler a" = DDIM η = 1 = DDPM ancestral. Count NFE (Heun: N steps, 2N − 1 calls).
- **Computed, one Gaussian direction (V₀ 1,474.57):** part 5's 0.851 is DDIM's own error — closed
  form 0.8554, measured 0.854 (se 0.014). Log-SNR steps 0.941, DPM-Solver++(2M) 1.0035; 1% costs 778
  calls vs 30. Heun from σ = 4096 on part 5's 25-step spacing keeps 12.2× the spread.
- **Measured against an RK4 reference:** calls to one grey level (2/256) on ρ = 7:
  DDIM 100, Heun 49, DPM-Solver-2 41, 2M 25, DPM-Solver-3 16; slopes −1, −2, −2.75. Below 10 calls
  singlestep solvers lose to DDIM. Schedules move cost 5–16×; 2M needs 320 on time-uniform VP steps.
- **Noise:** with an exact denoiser deterministic samplers win; on part 5's flawed start the exact
  ODE keeps 0.357, the SDE 0.487. The real-model crossover is quoted.
- **Toy limits:** VP-time Euler ≈ DDIM here (160 vs 200), so coordinate gains are cited, not
  measured; exposure bias is invisible. 22 sources (19 peer-reviewed), 46 claims.

## Decisions to preserve

- **No body H1.** Ledger keys are HTML comments next to the sentence they support.
- **Naming earlier parts:** since 2026-10-09 (owner) name earlier parts by title in plain text
  whether or not they are live, and list each spot in the manifest's *Series links to add*; the
  owner adds links. Parts 4–5 predate this and name only part 1. Parts 1–3 keep canonical-URL links.
- **Toolchain:** each part copies the previous part's `assets/` toolchain (`_build.py`,
  `_figures.py`, `_mermaid.py`, `_social.py`), never imports across posts. `TEMPLATES`/`ROOT` is
  `HERE.parents[3]` for a series member. Figures read every number from the shipped lab capture.
  Figure files are numbered by order of appearance. Object keys `blog/<slug>/fig-NN-<name>-v1.png`.
  Display: high value = bright, shared range across panels. `ascii_upper` keeps Greek in labels;
  spell ε̂, β̃ and σ̂ out on figures (Geist Mono misplaces the accent). Part 6's `Axes` take raw
  values on log axes; `footnote()` raises past the canvas (5.95 px per mono glyph).
- **Mermaid:** `_mermaid.py` needs a 45 s budget, `document.fonts.load` before `mermaid.run`, and
  (since part 4) `wrappingWidth: 420`. Over ~10 nodes use TB; put block titles inside the first node,
  because edges entering a subgraph cut through its title. Mermaid 11 draws edge-label boxes at
  opacity 0.5; part 6's `_mermaid.py` themeCSS makes them opaque.
- **Labs:** G1 unless a part truly needs more; `access.md` records why no request was raised.
  Part 4's environment (`~/.cache/diffusion-models-lab`) is reusable for parts 5–8. A lab that
  runs over ~10 min caches each finished run and resumes; shipped output prints relative paths only; figures and social cards share one median.
  Freeze the script before the final capture: any edit changes the `source_sha1` the capture records.
  Part 6's `samplers.py` (exact ODE by RK4 in log σ, eight samplers, five schedules, `gaussian_1d`)
  is the teacher and reference for part 7.
- Part 2's ledger and manifest predate blog-forge 0.4; do not retrofit unless it is reopened.

## Open threads

- **Publication order:** part 1 is live; parts 2–6 are ready. Part 3 links part 2's
  `#the-math`, so part 2 must go live first; parts 4–6 link no unpublished part. Part 2 still lacks
  `series`/`series_position`.
- Part 1 errata found by part 3, not fixed (part 1 is live): reference 16's authors are Lin, Liu,
  Li & Yang; its Implementation's `abar[207]` is 0.6375, not 0.6405.
- Part 1 links forward to nothing; add forward links only once a target is live.
- Part 5's Mermaid fig-01 probably shows lines through edge labels (the opacity defect above); not
  fixed, since part 5 is gated. `samplers.py --quick` help says ~2 min (measured 64 s); fix on its
  next edit.
- Benchmark numbers move: every part states model, dataset and evaluation beside any FID or NFE;
  part 9 owns the argument.

## Next part brief

- **Part:** whichever the owner picks; strongest claim **part 7** (few-step distillation), because
  part 6 left an exact teacher: crescent world's ODE solution, so a student's error is measurable.
- **Can assume:** the knowledge above. **Must teach:** only that part's row in `plan.md`.
- **Must not repeat:** parts 3–5's lists above, plus solver order, NFE accounting, step schedules and
  ODE vs SDE (part 6). Three sentences of recap at most.
- **Evidence still needed:** distil 1–4-step students from `samplers.py`'s exact ODE on CPU and
  measure them against it; quote progressive, consistency and DMD2 results with their setups.
