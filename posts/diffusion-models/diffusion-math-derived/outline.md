# Outline — diffusion-math-derived

Series: `diffusion-models`, part 3 of 12. Read `../plan.md` and `../context.md` before editing.

## Brief

- **Subject:** machine learning / generative modelling — the training objective.
- **Tier:** L4 · **Difficulty:** advanced. Set by the series plan, not re-proposed.
  L4 because the reader must learn four linked things — the bound, its decomposition into
  per-step Gaussian KLs, the reweighting that produces L_simple, and the score-matching reading
  that makes three formulations one — and the smallest honest worked example (one reverse step
  on one pixel, priced five ways) needs a page. Advanced because it assumes expectations, KL
  divergence and calculus, and it assumes part 2's map.
- **Audience:** an engineer or student who has read a diffusion paper's method section and seen
  `||eps - eps_theta||^2`, and wants to know why that regression trains a density model.
- **The one question this part owns:** where does the simple MSE loss actually come from?
- **What falls out of it, and the post also owns:**
  1. Why is each term of the bound a squared error? (both sides of each KL are Gaussians with the
     same variance)
  2. What did DDPM throw away to get L_simple, and what did it cost? (the per-step weights; a
     worse bound, better samples — with the measured numbers)
  3. Are ε-, x₀-, v- and score-prediction different objectives? (no — one integral, different
     weights over noise level; only the weight and the shared-parameter trade-off differ)
  4. How are DDPM, NCSN and the score SDE the same object? (one family of Gaussian corruptions
     indexed by SNR; three coordinate systems and three weightings)
- **Deliberately deferred:** backbone internals → part 4. Choosing a schedule, a weighting or a
  target *as a training decision* (Min-SNR, EMA, terminal SNR fixes) → part 5. Solvers and the
  probability-flow ODE as numerical analysis → part 6. Guidance → part 8. Flow matching beyond
  one sentence → not this series' derivation (Kingma & Gao place it on the same weighted-loss
  axis).
- **Must not repeat from part 1:** the free-target argument, the averaging argument, the
  amplification multiplier. Link to part 1's anchors.
- **Must not repeat from part 2:** part 2's `#the-math` compresses the chain in six equations.
  This post derives each step, prices it on numbers, and adds what part 2 does not have: the
  per-step weights, the SNR form, the weighting unification, DSM and Tweedie, and the continuous
  limit.
- **Target:** 8,000 words, 12 figures, one single-file lab.
- **Actual:** 9,752 words by the validator's count (about 1,000 of them in References, and LaTeX
  tokens count as words), 12 figures, one lab file. Inside the L4 band of 7,500–10,000.

## Section budget

L4 plan of 8,000; shares from `depth-tiers.md`, shifted toward the body because the math *is*
the body here, and a separate math section may only hold what the body does not.

| Section | Budget | Reader can now… |
|---|---:|---|
| Insights + who this is for + jump list | 200 | say in two sentences where the MSE comes from |
| Why this matters | 220 | recognise two real confusions (loss value ≠ likelihood; switching targets changes training) |
| The problem | 450 | state why log p(x₀) is an intractable integral over T latents, with sizes |
| Worked example | 850 | compute one reverse step's KL on one pixel, then price one error five ways |
| Intuition | 450 | explain why "same variance Gaussians" makes a squared error, and where the teacher analogy breaks |
| What is the ELBO, and why is diffusion a VAE? | 650 | derive the bound with its gap, and place diffusion as a fixed-encoder hierarchical VAE |
| How does the bound become one squared error per step? | 1,300 | decompose the bound, derive the posterior, turn a Gaussian KL into an ε-MSE with its weight, and write the SNR form |
| Why does DDPM throw the weights away? | 650 | read the per-step weight curve, and state the measured cost of dropping it |
| Is every diffusion loss the same loss? | 700 | convert any loss to w(λ), and say what the schedule does and does not change |
| Where does the score come from? | 800 | derive Tweedie and denoising score matching, and say why noisy targets are fine |
| How are DDPM, NCSN and the SDE one object? | 850 | map DDPM ↔ VP, NCSN ↔ VE, rescale one into the other, and state the continuous-time limit |
| The math | 650 | check the three derivations collapsed out of the body (posterior, Gaussian KL, DSM equivalence) |
| Implementation | 450 | compute a step's KL three ways and the per-step weights in ~40 lines |
| Limitations and common mistakes | 500 | avoid five specific misreadings |
| Key takeaways + exercises + references | 350 | carry away five claims and check three by hand |

Six body sections, the L4 maximum.

## Figure plan

Route gate run per figure against the real content, per `blog-visuals/references/visual-taxonomy.md`.

| # | File | Section | The one thing it must communicate | Route | Why (the clause that settled it) |
|---:|---|---|---|---|---|
| 1 | fig-01-teacher-and-student | Worked example | the forward posterior for one pixel is the precision-weighted combination of two Gaussians (5 + 4 = 9), and the network's step is the same Gaussian shifted by 0.0745 — KL 0.025 | `plot` | Q4 — four density curves over a real axis with the worked values; a box diagram cannot show a precision sum |
| 2 | fig-02-one-error-five-prices | Worked example | one +0.20 error in ε, carried into x₀, score, v and the ELBO step, gives five squared errors that are one number times five weights | `placed` | Q4/Q5 — a five-row ledger of real values with proportional bars; under nine elements, no crossings |
| 3 | fig-03-diffusion-is-a-fixed-encoder-vae | ELBO section | VAE, hierarchical VAE and diffusion as three small graphical models; only the last has a fixed encoder and latents the data's size | `placed` | Q4 — three small multiples compared side by side; each panel has ≤ 5 nodes |
| 4 | fig-04-where-each-elbo-term-lives | Decomposition | the chain x₀ … x_T with the three term types bracketed where they act, and which of them touch θ | `placed` | Q5 — 6 chain nodes plus 3 brackets, no crossings; term labels need to sit on the chain |
| 5 | fig-05-the-weight-ddpm-dropped | Why DDPM drops weights | DDPM's per-step ELBO weight over its real 1,000-step schedule, against L_simple's flat 1 | `plot` | Q4 — a curve computed from the published schedule on a log axis, with marked extremes |
| 6 | fig-06-bound-versus-samples | Why DDPM drops weights | measured NLL and FID for the bound, the hybrid and L_simple on CIFAR-10, two papers, setups stated | `chart` | Q1 — measured numbers from ledger rows L10 and L42 |
| 7 | fig-07-one-loss-many-weightings | Every loss the same | published losses as weights over log-SNR, with the worked example's noise level marked | `plot` | Q4 — curves evaluated from the published w(λ) formulas; not measured |
| 8 | fig-08-the-ideal-denoiser-is-an-average | Where the score comes from | for a three-level dataset, the ideal denoiser is a posterior-weighted average, and the score is the arrow from x_t to its scaled average | `plot` | Q4 — exact posterior weights and a real score field over a real axis |
| 9 | fig-09-noisy-targets-average-to-the-score | Where the score comes from | per-sample DSM targets are scattered widely, yet their conditional mean lies on the true score curve | `plot` | Q1/Q4 — a deterministic simulation from the lab, plotted against the exact curve |
| 10 | fig-10-three-formulations-one-object | One object | DDPM, NCSN, VP-SDE, VE-SDE, VDM and EDM as views of one SNR-indexed family, with the conversion on every edge | `mermaid` | Q3 — 12 nodes, edges cross between the discrete and continuous columns; the post's one end-to-end view |
| 11 | fig-11-vp-and-ve-are-one-path | One object | the same pixel under VP and VE corruption; VE explodes, VP stays bounded, and √ᾱ × VE lands exactly on VP | `plot` | Q4 — trajectories over log-SNR computed from the worked pixel |
| 12 | fig-12-more-steps-tighter-bound | One object | VDM's measured CIFAR-10 bits/dim falling from 4.31 at T = 10 to 2.65 in continuous time | `chart` | Q1 — measured numbers from ledger row L22 |

Figure budget: 12 over roughly 8,000 words is one per ~670 words, inside the 500–700 guidance and
the L4 band of 12–18.

### Paper-figure (`source` route) check

Inspected before planning originals: Luo Fig. 3 (the chain as an HVAE), VDM Fig. 2 (Riemann-sum
illustration), Kingma & Gao Fig. 3 (weighting curves), EDM Fig. 1 (ideal denoiser outputs). All
four carry only the arXiv non-exclusive distribution licence or no stated licence, so none takes
the `source` route (ledger, *Figure candidates*). Each original figure here is built on the
post's own numbers — the worked pixel, the three grey levels of the crescent motif, or ledger
rows — rather than redrawing a paper's composition. Figure 7 evaluates Kingma & Gao's published
formulas; it adds the worked example's noise level and DDPM's log-SNR range, which theirs does not.

## Term map

| Term | First section | What it is | Why it is used here | When it matters |
|---|---|---|---|---|
| evidence, log-likelihood | The problem | log p_θ(x₀), the log probability the model gives to a real image | it is the quantity training would ideally maximise | comparing models by bits per dimension |
| latent variable | The problem | an unobserved random variable the model integrates over | x₁ … x_T are latents; that is what makes p(x₀) an integral | reading any VAE or diffusion paper |
| KL divergence | Worked example | the expected log-ratio between two distributions; zero only when they match | every term of the bound is one | reading a loss as a bound |
| forward posterior q(x_{t−1} ∣ x_t, x₀) | Worked example | the distribution of the previous state given the noisy state *and* the clean image | it is the "teacher" each reverse step is trained against | any derivation of the ε-loss |
| precision | Worked example | 1/variance | adding precisions is how two Gaussian pieces of evidence combine | computing a posterior by hand |
| ELBO | ELBO section | evidence lower bound, E_q[log p(x,z) − log q(z∣x)] | it is the tractable quantity diffusion training descends | whenever someone calls the loss a likelihood |
| variational autoencoder (VAE), hierarchical VAE | ELBO section | a latent-variable model trained on the ELBO with a learned encoder; hierarchical = a chain of latents | diffusion is the special case with a fixed encoder | reading Luo's or VDM's framing |
| prior matching, reconstruction, denoising matching | Decomposition | the three kinds of term in the bound | only denoising matching trains the network in DDPM | deciding which term a loss drops |
| SNR, log-SNR λ | Decomposition | α²/σ², the signal power over noise power at a level; λ its log | the bound's per-step weight is a difference of SNRs | reading VDM, EDM and Kingma & Gao |
| L_simple | Why DDPM drops weights | the unweighted ε-MSE averaged over uniform t | it is the loss everyone ships | comparing training objectives |
| weighting function w(λ) | Every loss the same | the density over noise levels a loss implicitly puts on the ε-error | it is the only thing that distinguishes the losses | choosing a target or a schedule |
| v-prediction | Five prices / Every loss the same | predicting v = αε − σx₀ | a common alternative target with a different implied weight | reading SD 2.x-era and distillation code |
| score, conditional score, marginal score | Where the score comes from | ∇ log density; conditional = of q(x_t∣x₀), marginal = of q(x_t) | DSM regresses on the first to learn the second | reading NCSN or SDE papers |
| Tweedie's formula | Where the score comes from | posterior mean = observation + variance × marginal score | links the denoiser to the score | converting between D, ε̂ and s_θ |
| denoising score matching (DSM) | Where the score comes from | regressing a network onto the conditional score of a noising kernel | it is why the per-example target can be noisy and still correct | any score-based objective |
| VP / VE | One object | variance-preserving vs variance-exploding corruption | DDPM and NCSN are one of each | reading SDE-era papers |
| SDE, reverse-time SDE | One object | a continuous-time noise process and its time reversal | the T → ∞ limit of both chains | handing off to part 6 |

## Limitations section — the misreadings it must name

1. "L_simple is a log-likelihood." It is a reweighted bound; its value is not bits per dimension.
2. "ε, x₀, v and score prediction are different objectives." Same minimiser at each noise level;
   different weights over levels and different numerical conditioning.
3. "Training on the true bound gives the best samples." Measured: better NLL, worse FID.
4. "The prior term is zero." Small, not zero — terminal SNR is nonzero in common schedules.
5. "The network learns the data score." It learns the score of the *noised* data at each level;
   the two coincide only as noise → 0, where the DSM target's variance blows up.

## Handoffs this post must make explicitly

- Choosing a weighting or schedule for training → part 5.
- The reverse SDE and probability-flow ODE as things you integrate → part 6.
- The denoiser's internals → part 4.

## Gate

```bash
python3 .claude/blog-forge/scripts/validate_post.py posts/diffusion-models/diffusion-math-derived/
python3 .claude/blog-forge/scripts/lint_visuals.py posts/diffusion-models/diffusion-math-derived/assets/
```
