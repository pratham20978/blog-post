# Outline — training-a-diffusion-model

Series: `diffusion-models`, part 5 of 12. Read `../plan.md`, `../context.md` and `../access.md`
before editing.

## Brief

- **Subject:** machine learning / generative modelling — the training recipe of a diffusion model.
- **Tier:** L4 · **Difficulty:** advanced. Set by the series plan, not re-proposed. L4 because the
  reader must learn six coupled decisions (schedule, endpoint, target, weighting, EMA, scale), each
  with its own mechanism and evidence, and the smallest honest example of the endpoint flaw needs
  real numbers at two resolutions. Advanced because it assumes the forward process, ε-prediction
  and what a training loop is.
- **Audience:** an engineer about to train or fine-tune a diffusion model who has seen
  `beta_schedule`, `prediction_type`, `snr_gamma` and `ema_decay` in a config and wants to know
  what each one decides and what goes wrong when it is wrong.
- **The one question this part owns:** what do you decide before the first gradient step?
- **What falls out of it, and the post also owns:**
  1. What does the schedule decide? (endpoints and where training samples; resolution and data scale move it)
  2. Why must the last step be pure noise? (the leak lives in the mean; it grows with √n)
  3. Which target? (same optimum, different error amplification; capacity decides at high dimension)
  4. Which weighting? (allocates finite capacity across levels; reweight vs resample)
  5. Which EMA? (a half-life measured in steps; the best length moves with training)
  6. How does it scale? (training compute ≈ 3× forward; loss falls smoothly; data quality)
- **Deliberately deferred:** sampler numerics and step counts → part 6 ("later in this series");
  guidance and CFG rescale → part 8; FID's meaning → part 9. Training infrastructure is out of
  scope for the series (plan.md).
- **Series links:** only part 1 is published, so only part 1 is named, in plain text. Parts 2–4 are
  not live and not named. The two facts this post needs from part 3 (every loss is ∫w(λ)·error dλ;
  the schedule is an importance sampler) are restated in two sentences with their primary sources.
- **Must not repeat:** part 3's ELBO chain, five prices, Tweedie/DSM, VP↔VE; part 4's backbone
  shapes, N/(N+6D) and memory formulas. The target section restates "same optimum" in one sentence.
- **Lab:** **G1** — numpy and CPU PyTorch in the series' pinned environment. A toy (crescent world)
  whose ideal denoiser is a closed form, so every error is measured against the optimum. No access
  request: no claim depends on GPU speed or a production checkpoint; published scale results are
  cited with their setups.
- **Target:** ~8,500 words, 14 figures (one `source`), one lab (README, `training_decisions.py`,
  requirements, two captures).

## Section budget

| Section | Budget | Reader can now… |
|---|---:|---|
| Insights + who this is for + jump list + notice | 260 | name the five decisions and the one measured consequence |
| Why this matters | 200 | see why "solid black background" failing is a training decision |
| The problem | 450 | write one training step and mark where each decision enters |
| Worked example | 900 | compute what survives SD's last step at 16 and 16,384 values, and what the rescale changes |
| Intuition | 380 | describe training as a budget over noise levels, and where that analogy breaks |
| What does the noise schedule decide? | 1,000 | read any schedule as endpoints + sampling density; shift it for resolution and data scale |
| Why must the last step be pure noise? | 950 | predict the leak from n and SNR_T; fix it and know what the fix costs |
| Which target should the network predict? | 850 | choose ε, x0, v or EDM's F from where errors amplify and from capacity |
| Which noise levels should win? | 950 | choose a weighting, read its evidence with setups, and know resample vs reweight |
| What does the EMA buy, and how long should it be? | 700 | convert a decay into a half-life, pick a length, and avoid averaging the initialisation |
| How does training scale? | 650 | estimate training FLOPs and read scaling results without over-reading them |
| The math | 650 | derive the leak ratio, the rescale, the amplification factors and EDM's c_out |
| Implementation | 450 | write the schedule, rescale, weighted loss and EMA in 40 lines |
| Limitations and common mistakes | 450 | avoid seven concrete failures |
| Key takeaways + Try it yourself + References | 500 | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| noise schedule, ᾱ_t, β_t | The problem | the fixed map from timestep to noise level | decides which noise levels exist and how often training visits them | every config; changing it means retraining |
| SNR, log-SNR λ | The problem | ᾱ/(1−ᾱ) and its log | the coordinate every decision is stated in | comparing schedules, weightings, targets |
| terminal SNR | Worked example | the SNR at the last training step | if > 0, training never sees pure noise | any schedule; any sampler's first step |
| signal leak | Worked example | image content surviving the last step, mostly the mean | the model learns to read it; pure noise at inference carries none | high resolution, latent models |
| zero-terminal-SNR rescale | Worked example | Lin's shift-and-scale of √ᾱ | removes the leak without redesigning the schedule | fine-tuning SD-family models |
| leading / trailing timesteps | Terminal SNR | which training steps a sampler visits | leading never starts at t = T | any sampler config (`timestep_spacing`) |
| sampling density p(λ) | Schedule | how often training draws each log-SNR | importance sampling; the practical meaning of "schedule" | EDM log-normal, SD3 logit-normal |
| resolution shift, input scaling | Schedule | moving log-SNR by 2·log(64/d) or scaling x0 by b | more pixels make each noise level easier | training at a new resolution |
| latent scale factor | Schedule | 0.18215 for SD's VAE latents | SNR is relative to data variance | any latent model; swapping a VAE |
| prediction target (ε, x0, v, F) | Target | what the network's output represents | same optimum, different error amplification | config `prediction_type` |
| preconditioning (c_skip, c_out, c_in) | Target | EDM's input/output scalings | unit-variance target, least amplification | EDM-family code |
| loss weighting w(λ) | Weighting | the per-level multiplier on the squared error | allocates shared capacity | `snr_gamma`, P2, EDM λ(σ) |
| Min-SNR-γ | Weighting | min(SNR, γ) in x0 units | caps the clean end | default γ = 5 |
| EMA, decay β, half-life | EMA | running average of weights | the weights you sample with | every run; decay vs run length |
| power-function EMA, σ_rel, post-hoc EMA | EMA | EDM2's scale-free average and its reconstruction | choose EMA length after training | long runs, sweeps |
| training FLOPs ≈ 3× forward | Scaling | backward costs twice the forward | budget arithmetic | planning a run |

## Figure plan

Route gate run per figure; the `source` check ran first for every paper-backed figure. Lin et
al.'s Figure 3 is the only candidate with a reuse licence (CC BY-SA 4.0) and it shows something
our toy cannot: the flaw on a real model. The others (Min-SNR Fig. 5, SD3 Fig. 6, EDM2 Fig. 5)
have no reuse licence; the post draws its own analysis instead.

| # | Section | Communicates | Route | Why | Draft caption |
|---|---|---|---|---|---|
| 1 | The problem | one training step, with the five decisions marked where they enter | mermaid | Q3 — 15 nodes (ten steps, five decisions); the decisions feed six points on the path, edges cross | Every decision enters at a different point of one step |
| 2 | Worked example | the series' patch at SD's last step; the mean's leak against its noise at 16, 256, 4,096 and 16,384 values | placed | Q4 — a grid of real values and a bar of real numbers | 16 values hide the leak; 16,384 reveal it |
| 3 | Schedule | log-SNR against t/T for linear, cosine, SD, SD rescaled | plot | Q1/Q4 — closed-form curves computed by the lab | The schedules differ most where they end |
| 4 | Schedule | where training draws log-SNR: SD, cosine, EDM log-normal, SD3 logit-normal and its 1024² shift | plot | Q1/Q4 — densities computed from published formulas | Each recipe spends its samples somewhere else |
| 5 | Schedule | the resolution shift: the cosine schedule per pixel and for 4×4 and 16×16 block means, beside the schedule shifted down for a 4× larger image | plot | Q4 — curves | More pixels make every noise level easier |
| 6 | Terminal SNR | toy samples at 16,384 px from the data, the flawed schedule and the fixed one, with brightness histograms | placed | Q4 — real sample images and measured histograms | Same starting noise: grey, then full range |
| 7 | Terminal SNR | measured brightness spread vs pixels (with the closed form) and vs sampling steps | chart | Q1 — lab measurements | The flaw is a fixed point; the fix converges |
| 8 | Terminal SNR | SD 2.1-base flawed vs fixed on eight prompts | source | Source check — Lin et al. Figure 3, CC BY-SA 4.0, the real-model evidence | Reproduced unchanged |
| 9 | Target | how an output error reaches x0 and ε for each target, against log-SNR | plot | Q4 — closed-form curves | ε amplifies at high noise, x0 at low, v nowhere |
| 10 | Target | measured per-level excess error for ε, x0, v at width 32 and 256 | chart | Q1 — lab | Below the data's dimension, only x0 survives |
| 11 | Weighting | measured per-level excess error for four weightings | chart | Q1 — lab | Each weighting buys accuracy at one end with error at the other; SNR weighting starves the noisy end |
| 12 | Weighting | reweighting vs resampling at a fixed budget (Hang 2025 Table 3) | chart | Q1 — ledger numbers with setup | Moving samples beat moving weights |
| 13 | EMA | EMA profiles over a 40k-step run, and the lab's sample distance by EMA length at four checkpoints | chart | Q1 — closed-form profiles plus lab measurements | The best EMA grows with the run; long EMAs remember the initialisation |
| 14 | Scaling | EDM2's size ladder; the lab's excess error vs width for two weightings | chart | Q1 — ledger and lab numbers | Bigger keeps helping; it does not rescue a starved noise level |
