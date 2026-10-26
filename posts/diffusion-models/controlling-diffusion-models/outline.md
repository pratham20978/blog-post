# Outline — controlling-diffusion-models

Series: `diffusion-models`, part 8 of 12. Read `../plan.md`, `../context.md` and `../access.md`
before editing.

## Brief

- **Subject:** machine learning / generative modelling — making a trained diffusion model obey a
  condition other than its text prompt: guidance and its variants, ControlNet and adapters, LoRA and
  personalisation, inpainting, instruction editing.
- **Tier:** L4 · **Difficulty:** advanced. Set by the series plan, not re-proposed. L4 because the post
  owns six method families that share one mechanism and each needs its own evidence, and the honest
  worked example (guidance on one number) needs a page. Advanced because it assumes the denoiser as
  E[x₀ | x], DDIM's update in σ coordinates and the probability-flow ODE (part 6), and fine-tuning a
  network.
- **Audience:** an engineer who ships or fine-tunes text-to-image models and has to choose between
  turning up the guidance scale, attaching a ControlNet or adapter, training a LoRA, or inpainting or
  editing, and wants to know what each one changes and what it breaks.
- **The one question this part owns:** how do you make it obey something other than a prompt?
- **The post's answer, as a frame:** there are three places to put a condition — the sampler's
  arithmetic (guidance, inpainting by replacement, SDEdit, inversion), new inputs wired into a frozen
  network through paths that start at zero (ControlNet, adapters, inpainting and editing channels),
  or the weights (LoRA, DreamBooth, textual inversion's token). Each place has a measurable price.
- **What falls out of it, and the post also owns:**
  1. What classifier-free guidance does to the distribution (coverage lost, contrast overshot, network
     error amplified) and why the published FID curve is U-shaped
  2. Which fixes keep guidance's benefit (rescale, thresholding, interval, APG, autoguidance, CADS,
     guidance distillation)
  3. How ControlNet adds a condition without breaking the model (zero convolution, trainable copy),
     and the adapter family (T2I-Adapter, IP-Adapter, GLIGEN)
  4. What LoRA and personalisation change and forget (TI, DreamBooth, prior preservation, Custom
     Diffusion)
  5. How inpainting fills a hole (replacement, RePaint, DPS/TDS, trained inpainting channels)
  6. How editing changes an image you already have (SDEdit, DDIM and null-text inversion,
     Prompt-to-Prompt, InstructPix2Pix)
- **Deliberately deferred:** what FID measures and hides → "later in this series" (part 9); the post
  says which metric each failure moves and quotes FIDs only within one paper's table; video, audio,
  3-D control → later (part 10). Prompt-engineering craft is out of the series' scope.
- **Series links (owner's instruction 2026-10-09):** name earlier parts by title whether or not they
  are live; the owner adds the links. Named: part 6 (Diffusion Samplers and Solvers: 1,000 Steps
  Into 20) for DDIM in σ coordinates and the ODE — the prerequisite; part 5 (Training a Diffusion
  Model) for crescent world and the sliced Wasserstein sample distance; part 7 (Few-Step Diffusion and
  Distillation) for guidance distillation's second stage; part 4 (Diffusion Backbones: U-Net to DiT)
  for the U-Net's skips and cross-attention; part 1 (What a Diffusion Model Actually Does, live) for
  the averaging argument. Later parts stay "later in this series".
- **Must not repeat:** part 6's solver order and NFE accounting; part 7's few-step students and DMD;
  part 4's block-by-block U-Net. Three sentences of recap at most each.
- **Lab:** **G1** — CPU PyTorch in the series' pinned environment, plus an optional `census` stage that
  needs diffusers 0.40.0 and downloads nothing. Crescent world with a contrast dial (each crescent
  faint or strong) gives exact unconditional and conditional denoisers; networks are trained the way
  real models are (data targets, label dropout). No access request: a GPU would train bigger networks
  whose ideal answer is unknown, which measures less, not more (see `../access.md`).
- **Target:** ~8,000 words of prose (References add ~1,100; the L4 ceiling of 10,000 counts both), 14
  figures, one lab (README, `control.py`, requirements, captures, expected output, notebook, zip).

## Section budget

| Section | Budget | Reader can now… |
|---|---:|---|
| Insights + who this is for + jump list + notice | 330 | name the three places control can live and one price of each |
| Why this matters | 180 | see that the control knob chosen decides what breaks |
| The problem | 650 | write any condition as Bayes' extra term and say why each place estimates it differently |
| Worked example | 800 | compute a guided denoiser on one number, take one guided step, and read how far guidance moves the faint/strong boundary |
| Intuition | 350 | describe guidance as exaggerating a difference, say where the analogy breaks, read the three-places map |
| What does classifier-free guidance do to the distribution? | 750 | explain label dropout, the CFG combination, and the measured costs: coverage, contrast, error amplification; read the published U-curve |
| Which fixes keep guidance's benefit? | 700 | place rescale, thresholding, interval, APG, autoguidance, CADS and guidance distillation by what they remove |
| How does ControlNet add a condition without breaking the model? | 700 | explain the trainable copy, zero convolutions, sudden convergence; compare adapters by what they train |
| What do LoRA and personalisation change, and what do they forget? | 700 | explain TI, DreamBooth, LoRA, Custom Diffusion, prior preservation, and the measured drift, forgetting and memorisation |
| How do you fill in part of an image? | 500 | explain why replacement is incoherent, what resampling buys, and when to train mask channels |
| How do you edit an image you already have? | 600 | explain SDEdit's single dial and its closed form, inversion and null-text inversion, Prompt-to-Prompt, InstructPix2Pix |
| The math | 550 | write the conditional score by Bayes in denoiser form, CFG's tilt and its failure, zero-init gradients, LoRA's count, SDEdit's τ/√(τ²+σ₀²) |
| Implementation | 350 | write CFG with its variants, a zero-initialised branch, a LoRA layer and a replacement step |
| Limitations and common mistakes | 450 | avoid six concrete mistakes |
| Key takeaways + Try it yourself | 400 | — |

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| condition, control | Insights / problem | any information the sample must agree with | the post's subject | always |
| Bayes' split of the conditional score | The problem | ∇log p(x ∣ y) = ∇log p(x) + ∇log p(y ∣ x), in denoiser form | every method estimates the second term somewhere | reading any control paper |
| guidance weight w (and its conventions) | The problem | the multiplier on D_c − D_u; w = 1 is no guidance | papers disagree on the zero point | comparing scales across codebases |
| classifier guidance | body 1 | adding a noisy-image classifier's gradient | CFG's predecessor | — |
| classifier-free guidance, label dropout, null token | body 1 / worked | one network, condition dropped 10–20% | the default control knob | any text-to-image sampler |
| faint/strong sub-modes, coverage (faint share) | Worked example | the toy's two contrasts per class; share of samples faint | measures mode loss directly | reading recall |
| over-saturation | body 1 | contrast beyond any real sample | guidance's visible artefact | high guidance scales |
| blends | body 1 | contrasts no real crescent has | the network's own error that guidance removes | judging what guidance buys |
| sample distance | The problem | part 5's sliced Wasserstein distance | one number for the set | comparing settings |
| dynamic thresholding, CFG-rescale, APG | body 2 | fixes for saturation | what each removes | high guidance scales |
| guidance interval | body 2 | guidance only for σ in a band | high-noise guidance drops modes | EDM2, SDXL |
| autoguidance | body 2 | guiding with a weaker copy of the same model | keeps coverage | when a weak copy exists |
| CADS, guidance distillation | body 2 | noise on the condition; a student that bakes guidance in | diversity; the halved cost | — |
| ControlNet, trainable copy, zero convolution | body 3 | a copied encoder added through zero-initialised 1×1 convs | structure control without damage | edges, depth, pose |
| sudden convergence | body 3 | control learned abruptly | what training looks like | training a ControlNet |
| adapter (T2I-Adapter), IP-Adapter, GLIGEN gate | body 3 | lighter side paths | cost/fidelity choices | image prompts, boxes |
| LoRA (rank, A, B, α) | body 4 | low-rank weight update, B = 0 at start | the cheap fine-tune | styles, subjects |
| textual inversion | body 4 | a learned token only | the cheapest | when the model can already draw it |
| DreamBooth, identifier, class noun, prior preservation, language drift | body 4 | full fine-tune on 3–5 photos plus own-class samples | personalisation's standard | subjects |
| Custom Diffusion | body 4 | only cross-attention K, V | a middle ground | multi-concept |
| inpainting, known region, posterior | body 5 | filling a masked region consistently with the rest | the hole-filling task | edits with masks |
| replacement, RePaint resampling, DPS, TDS | body 5 | sampler-side approximations to the posterior | training-free inpainting | when no inpainting model exists |
| inpainting channels | body 5 | mask and masked image as zero-initialised inputs | the trained route | production inpainting |
| SDEdit, σ₀ | body 6 | noise then denoise under a new condition | edit by partial regeneration | sketches, global edits |
| DDIM inversion, null-text inversion | body 6 | the deterministic map back to noise; fixing it under guidance | faithful edits | real-image editing |
| Prompt-to-Prompt | body 6 | reusing cross-attention maps | layout-preserving prompt edits | generated images |
| InstructPix2Pix, two guidance scales | body 6 | an editor trained on synthetic pairs | "make it X" edits | instruction editing |

## Figure plan

Route gate run per figure (source check first: of the five candidates in the ledger, F1 —
InstructPix2Pix's Figure 2 — is CC BY 4.0 and is the method itself; F3 and F4 carry only arXiv's
non-exclusive licence; F2 is CC BY 4.0 but the section's point is measured, not drawn; F5 is numbers).
Every measured or computed number is read from `lab/captures.json`.

| # | Section | One thing it must communicate | Route | Why |
|---|---|---|---|---|
| 1 | Worked example | guided paths overshoot early, then commit, and the faint basin shrinks | plot | Q1/Q4 — closed-form 1-D paths |
| 2 | Intuition | the three places a condition can live, each method in its place with what it changes and costs | mermaid | Q3 — 16 nodes in three parallel paths |
| 3 | CFG | what guidance does to real samples: faint crescents turn strong, strong ones over-brighten | placed | Q4 — real 8×8 images from the exact model |
| 4 | CFG | coverage, blends and over-saturation against w for the exact model and two networks | chart | Q1 — measured, lab |
| 5 | CFG | the published U-shape: FID best at a little guidance, IS rising throughout | chart | Q1 — quoted table numbers (L08–L09) |
| 6 | Fixes | where guidance decides: faint share with guidance only above or only below a noise level | chart | Q1 — measured, lab |
| 7 | Fixes | every fix in one plane: blends against coverage | chart | Q1 — measured, lab |
| 8 | ControlNet | SD 1.5 with a ControlNet: frozen U-Net, trainable copy, zero convs into the skips, shapes and counts | mermaid | Q3 — the post's one architecture view, edges cross |
| 9 | ControlNet | zero vs Gaussian connectors over training: control error and sample distance | chart | Q1 — measured, lab |
| 10 | Adapters / LoRA | what each method trains on SD 1.5, log scale | chart | Q1 — computed (census) and quoted counts |
| 11 | Personalisation | subject, drift, forgetting and the five photos' spread, per method | chart | Q1 — measured, lab |
| 12 | Inpainting | completions and coherence: replacement, resampling, mask channels, exact | placed | Q4 — real 8×8 images plus a bar row |
| 13 | Editing | SDEdit's one dial against inversion: ghost, detail, brightness | chart | Q1 — measured, lab, with the closed form drawn |
| 14 | Editing | how InstructPix2Pix manufactures its training pairs | source | the paper's own CC BY 4.0 figure is the method (ledger F1) |
