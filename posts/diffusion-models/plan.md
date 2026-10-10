# Series plan — Diffusion Models

**Slug:** diffusion-models · **Shape:** hybrid · **Parts:** 12 (11 committed, 1 optional)

## Why this is a series and not one post

The objectives split at two different kinds of seam. The first is a genuine prerequisite seam:
nothing about prediction targets, samplers or guidance can be explained until the reader accepts
that a known corruption path can be walked backwards, and that acceptance is itself a post. The
second is a decomposition seam: once Part 2 has drawn the whole map, the map's regions — math,
backbones, training, samplers, distillation, control, evaluation, other modalities, discrete
tokens — are disjoint enough that each is its own 6,000–9,000-word post with its own search
intent. Budgeting all of it as one article gives roughly 75,000 words and 120 figures.

So this is a **hybrid**: a two-rung ladder (Part 1 → Part 2) whose upper rung fans out into nine
sibling spokes. Part 1 and Part 2 cover the same territory at different depths; Parts 3–12 cover
disjoint territory at roughly the same depth.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | say what a diffusion model is without the word "denoise" doing all the work | 1 |
| 2 | compute one forward-noising step on real numbers by hand | 1 |
| 3 | say why the reverse step needs a learned network when the forward one is a formula | 1 |
| 4 | explain where a *new* image comes from, given the model only ever saw corruptions of old ones | 1 |
| 5 | say why it takes many steps rather than one | 1 |
| 6 | name the four moving parts of a diffusion system and say which is swappable without retraining | 1 |
| 7 | trace a tensor through a diffusion U-Net and name every block and seam | 2 |
| 8 | say where the timestep and the text condition enter, and by which mechanism | 2 |
| 9 | place any diffusion paper's contribution on one of five independent design axes | 2 |
| 10 | derive the simplified MSE objective from the variational bound | 3 |
| 11 | reconcile the DDPM, score-matching and SDE formulations as one object | 3 |
| 12 | choose a backbone from token count, memory arithmetic and attention cost | 4 |
| 13 | fix every training decision — schedule, target, weighting, EMA — before the first gradient step | 5 |
| 14 | pick a sampler and a step count from measured error at matched NFE, not folklore | 6 |
| 15 | say what distillation to 1–4 steps costs, and in which metric it shows up | 7 |
| 16 | condition a model on something that is not a prompt | 8 |
| 17 | say what FID measures and what it hides | 9 |
| 18 | say what changes when the data is not a 2-D grid | 10 |
| 19 | say whether denoising tokens is the same object as denoising pixels | 11 |
| 20 | say when a sample stops being new | 12 |

## Parts

### Part 1 — What a Diffusion Model Actually Does

- **Slug:** what-a-diffusion-model-actually-does
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 3,500 · **Figures:** 6
- **Answers:** why can a model that only ever learned to undo noise invent an image?
- **Assumes:** what a neural network is; that a Gaussian is a bell curve with a mean and a spread.
  No prior generative modelling, no variational inference, no SDEs.
- **Hands off:** every network internal to Part 2; the ELBO derivation to Part 3; sampler
  numerics to Part 6; memorisation to Part 12.
- **Worked example:** one 4×4 greyscale patch pushed forward to a chosen noise level with every
  intermediate value printed, then one reverse step taken on those same numbers.
- **Key sources:** Sohl-Dickstein 2015; Ho 2020 (DDPM); Song & Ermon 2019; Croitoru 2023 survey;
  Yang 2023 ACM survey.
- **Search intent:** "what is a diffusion model", "how do diffusion models work",
  "how does stable diffusion actually work", "why do diffusion models take many steps"

### Part 2 — Diffusion Model Architecture: The Complete Guide

- **Slug:** diffusion-model-architecture
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,184 · **Figures:** 16
- **Answers:** what are all the parts and where are their seams?
- **Assumes:** Part 1's forward and reverse process. Convolution, attention, tensor shapes.
- **Hands off:** each of its five design axes to a spoke — targets and weighting to 3 and 5,
  backbones to 4, solvers to 6, control to 8, evaluation to 9.
- **Status:** drafted, folder currently at `posts/diffusion-model-architecture/`. See the note
  under *Publication order*.

### Part 3 — Where the MSE Loss Comes From

- **Slug:** diffusion-math-derived
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 12
- **Answers:** where does the simple MSE loss actually come from?
- **Assumes:** Part 2's map (`#the-math` anchor). Calculus, expectations, KL divergence.
- **Owns:** the full ELBO → denoising-score-matching derivation, and reconciling DDPM / NCSN /
  SDE as one object. Luo's unified perspective is the spine.

### Part 4 — Diffusion Backbones, U-Net to DiT

- **Slug:** diffusion-backbones-unet-to-dit
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 13
- **Answers:** what is the denoiser, block by block, and when do you swap it?
- **Owns:** tensor-shape trace through a real U-Net, DiT at two patch sizes, MM-DiT's dual
  streams, attention cost vs token count, memory arithmetic.

### Part 5 — Training a Diffusion Model

- **Slug:** training-a-diffusion-model
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 13
- **Answers:** what do you decide before the first gradient step?
- **Owns:** schedules, terminal SNR, prediction target as a training decision, loss weighting
  (Min-SNR), EMA, scaling behaviour.

### Part 6 — Diffusion Samplers and Solvers

- **Slug:** diffusion-samplers-and-solvers
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** how do 1,000 steps become 20 without retraining?
- **Owns:** ancestral vs DDIM vs DPM-Solver vs EDM's Heun, as numerical analysis with measured
  error at matched NFE.

### Part 7 — Few-Step Diffusion and Distillation

- **Slug:** few-step-diffusion-distillation
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** how do 20 steps become 1, and what breaks?
- **Owns:** progressive distillation → consistency → DMD2 → shortcut models → flow maps.

### Part 8 — Controlling Diffusion Models

- **Slug:** controlling-diffusion-models
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,000 · **Figures:** 13
- **Answers:** how do you make it obey something other than a prompt?
- **Owns:** CFG variants, ControlNet, adapters, LoRA and personalisation, inpainting,
  instruction editing.

### Part 9 — Evaluating Generative Models

- **Slug:** evaluating-generative-models
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** what does FID measure, and what does it hide?
- **Note:** the level drops here on purpose. This is a decomposition spoke, not a ladder rung, so
  a lower difficulty is legal — it is the one part a product person reads.

### Part 10 — Diffusion Beyond Images

- **Slug:** diffusion-beyond-images
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 11
- **Answers:** what changes when the data isn't a 2-D grid?
- **Owns:** video, audio, 3-D, molecules, time series. The ACM survey's application taxonomy
  lands here.

### Part 11 — Discrete Diffusion Language Models

- **Slug:** discrete-diffusion-language-models
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** can you denoise tokens instead of pixels?
- **Owns:** masked and discrete diffusion, LLaDA-class models, why sampler correctness is
  contested. Strongest standalone search intent in the series.

### Part 12 (optional) — Memorisation and Provenance

- **Slug:** diffusion-memorization-and-provenance
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,000 · **Figures:** 6
- **Answers:** when does a sample stop being new?
- **Assumes:** Part 1's account of where novelty comes from, and deepens exactly that.

## Publication order and cadence

Reading order is the numbering above; `series_position` follows it. Publication order does not
have to. Part 2 is already drafted, so it can ship first or second; Part 1 is the entry point
every other part links back to, so it should not ship later than third.

**One open item.** Part 2 currently lives at `posts/diffusion-model-architecture/`, outside this
series folder, and carries no `series` / `series_position` frontmatter. The convention is
`posts/diffusion-models/<post-slug>/`. Moving it is a build-artifact move plus two frontmatter
keys; it does not change the published slug or URL. Left as-is until the user says.

## Cross-links

Part 1 is the hub every later part links back to for the forward process and the four moving
parts. Part 1 itself links forward only to Part 2, and only once Part 2 is live. Parts 3–12 each
name at most one prior part as a prerequisite — Part 2 — and link to its anchor rather than
re-teaching it. No part links forward to an unpublished post.

## What this series will not cover

Training infrastructure and cluster engineering; the licensing and provenance of pretrained
checkpoints as a legal question (Part 12 covers the technical question only); prompt-engineering
craft; and product comparisons between hosted image services.
