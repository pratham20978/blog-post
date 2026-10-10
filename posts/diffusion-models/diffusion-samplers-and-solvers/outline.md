# Outline — diffusion-samplers-and-solvers

Series: `diffusion-models`, part 6 of 12. Read `../plan.md`, `../context.md` and `../access.md`
before editing.

## Brief

- **Subject:** machine learning / generative modelling — sampling a trained diffusion model as
  numerical integration.
- **Tier:** L4 · **Difficulty:** advanced. Set by the series plan, not re-proposed. L4 because the
  reader must learn five coupled things (why the step count is free, what DDIM computes, how
  higher order buys accuracy, where the steps go, when noise helps), each with its own mechanism and
  evidence, and the honest worked example needs a full step table. Advanced because it assumes the
  forward process, the denoiser as E[x0 | x], and what an ODE and Euler's method are.
- **Audience:** an engineer choosing a sampler and a step count for a trained model, who has seen
  DDIM, Euler a, Heun, DPM++ 2M Karras and UniPC in a menu and wants to know what each computes,
  what it costs, and how to measure the choice instead of guessing it.
- **The one question this part owns:** how do 1,000 steps become 20 without retraining?
- **What falls out of it, and the post also owns:**
  1. Why can the step count change at all? (the network learned a continuous field; the ODE fixes the answer)
  2. What does DDIM compute? (Euler in the right coordinates = exponential integrator; exact when D is constant)
  3. How do higher-order solvers buy accuracy? (Heun, DPM-Solver-2/3, DPM-Solver++(2M); order is asymptotic)
  4. Where should the steps go? (error is made where trajectories bend; schedules move it)
  5. Should the sampler add noise? (discretisation error vs error contraction; the crossover)
  6. How to choose and measure (NFE, a reference run, the failure modes)
- **Deliberately deferred:** distillation and consistency models → "later in this series" (part 7);
  classifier-free guidance and its stability → later (part 8), mentioned once where DPM-Solver++'s
  motivation needs it; what FID measures → later (part 9).
- **Series links (owner's instruction 2026-10-09):** name earlier parts by title even though only
  part 1 is live; the owner adds the links. Named: part 1 (live), part 3 and part 5 (not live).
  Parts 2 and 4 are not needed by this post's argument. Later parts stay "later in this series".
- **Must not repeat:** part 3's ELBO chain and VP↔VE derivation (one sentence of recap, with the
  rescaling stated); part 5's schedules, leak and targets (three sentences of recap for the worked
  example's setup).
- **Lab:** **G1** — numpy only, in the series' pinned environment. The exact denoiser of part 5's
  crescent world, so every error is the sampler's own; reference ODE solutions by RK4 to ~1e-12.
  No access request: a GPU model's true trajectory is unknown, so it would measure less, not more.
- **Target:** ~8,500 words, 12 figures (one Mermaid), one lab (README, `samplers.py`,
  requirements, captures, expected output).

## Section budget

| Section | Budget | Reader can now… |
|---|---:|---|
| Insights + who this is for + jump list + notice | 280 | say what a sampler is and what decides its error |
| Why this matters | 180 | see that the sampler menu is a 5× cost knob with measured consequences |
| The problem | 600 | state sampling as an ODE solve, count NFE, and name the error being measured |
| Worked example | 1,150 | compute DDIM's error on one Gaussian direction step by step, and see 50 NFE range from 0.855 to 1.0035 |
| Intuition | 420 | describe a solver as a guess about how the denoiser's answer drifts, and say where the analogy breaks |
| Why can the step count change without retraining? | 750 | explain why no retraining is needed and why the ancestral chain needed small steps |
| What does DDIM actually compute? | 750 | derive DDIM as Euler in σ / an exponential integrator and say why coordinates matter |
| How do higher-order solvers buy accuracy? | 950 | read an error-vs-NFE plot, know each solver's NFE per step and order, and spot the pre-asymptotic trap |
| Where should the steps go? | 800 | choose a step schedule from where the trajectory bends |
| Should the sampler add noise? | 850 | say when stochastic samplers win and why, with the start-mismatch demonstration |
| The math | 800 | derive the exponential-integrator update, Heun's order, the 2M coefficient and the Gaussian factors |
| Implementation | 450 | write DDIM, Heun and DPM-Solver++(2M) over a denoiser, and measure error at matched NFE |
| Limitations and common mistakes | 450 | avoid six concrete failures |
| Key takeaways + Try it yourself + References | 450 | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| sampler, solver | Insights | the procedure that turns noise into a sample using the denoiser | it is a numerical integrator; its error is separate from the network's | every inference call |
| NFE | The problem | number of denoiser (network) evaluations per sample | the cost unit; steps ≠ NFE | comparing samplers |
| probability-flow ODE | The problem | the deterministic equation whose solution maps noise to data with the right marginals | fixes the target a deterministic sampler approximates | DDIM, Heun, DPM-Solver |
| denoiser D(x; σ) | The problem | the network's estimate of the clean image at noise level σ | every update rule is written in it | all |
| VE coordinates x̄, σ | The problem | x/√ᾱ and √((1−ᾱ)/ᾱ) | the coordinates where trajectories are straightest | DDIM, EDM |
| global vs local truncation error | The problem / higher-order | error at the end vs error made by one step | what order describes; where to put steps | reading solver plots |
| order (p) | Worked example | global error ∝ h^p | doubling NFE cuts error 2^p× — asymptotically | choosing solver |
| exponential integrator | DDIM | a solver that integrates the linear part exactly | DDIM is one; why it beats plain Euler | DPM-Solver family |
| log-SNR λ | DDIM | ln(ᾱ/(1−ᾱ)) = −2 ln σ (series convention; DPM-Solver uses half) | the natural step variable | schedules |
| singlestep vs multistep | higher-order | extra calls inside a step vs reuse of past calls | 2M is second order at one NFE per step | DPM++ 2M |
| step schedule / discretisation | Where should steps go | the σ values a sampler visits | moves error between noise levels | Karras ρ, log-SNR, time-uniform |
| ρ (Karras schedule) | Where should steps go | exponent of EDM's polynomial spacing | ρ=7 default | `use_karras_sigmas` |
| ancestral sampling, η | Should it add noise | DDPM's reverse Markov chain; DDIM's η interpolates | stochastic = SDE discretisation | "Euler a" |
| churn | Should it add noise | EDM's add-noise-then-Heun step | Langevin correction | EDM stochastic sampler |
| error contraction | Should it add noise | fresh noise forgets earlier errors | why SDE wins at high NFE | Restart |
| exposure bias | Limitations | the network sees its own imperfect samples | real models compound errors the toy cannot show | — |

## Figure plan

The source check ran first for every paper-backed figure. Only Restart (CC BY 4.0) and Lin et al.
(CC BY-SA 4.0) carry reuse licences. Restart's Figure 1(b) is a schematic of the regimes and the
post measures the same crossover itself; its measured Figure 3 has no extractable image, so its
Table 4 numbers are charted instead. EDM's Figure 3 (the 1-D curvature sketch) and DPM-Solver's
figures carry only arXiv's non-exclusive licence: not reused; the post computes its own versions.

| # | Section | Communicates | Route | Why | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | one Gaussian direction: exact trajectory vs DDIM's steps on part 5's trailing grid, and the fraction each step keeps | plot | Q1/Q4 — closed-form curve and computed per-step factors | DDIM loses its 14.5% in the five steps that straddle √V₀ |
| 2 | Worked example | spread kept vs NFE for DDIM and DPM-Solver++(2M) on trailing and log-SNR spacing, Heun on both | chart | Q1 — computed convergence curves from the lab | Same NFE, a 40× range of error; Heun overshoots after a giant first step |
| 3 | Why can the step count change? | exact ODE paths of the toy vs DDIM's 6-step polylines in two coordinates against σ | plot | Q4 — real trajectories from the exact denoiser | Straight lines at both ends, a bend where the image is decided |
| 4 | What does DDIM compute? | the samplers as one family: which is a special case of which, with order, NFE per step and noise | mermaid | Q3 — 13 nodes, equivalence edges cross between families | Six names, three algorithms |
| 5 | How do higher-order solvers buy accuracy? | where each solver evaluates the denoiser within one step on the log-σ axis, and how it combines the answers | placed | Q4 — evaluation points to scale on an axis | Higher order = more information about how D drifts |
| 6 | How do higher-order solvers buy accuracy? | global error vs NFE for six samplers (EDM ρ=7 grid), with slopes and the one-grey-level line | chart | Q1 — lab measurements | Order shows up as slope, but only after the first few steps |
| 7 | How do higher-order solvers buy accuracy? | DPM-Solver Table 1 (RK vs DPM-Solver at matched NFE) and Table 4 (five samplers on DDPM's CIFAR-10 model) | chart | Q1 — quoted numbers with setup; the paper's figures carry no reuse licence | Same order, different formulation; same model, many samplers |
| 8 | How do higher-order solvers buy accuracy? | the toy's samples at 5, 10 and 20 NFE for four samplers beside the exact ODE endpoint | placed | Q4 — real sample images | Too few steps give blur, not noise |
| 9 | Where should the steps go? | local error of one step vs σ for DDIM and Heun under four schedules, with the toy's structure scales marked | chart | Q1 — lab measurements | Error is made where the trajectory bends |
| 10 | Where should the steps go? | NFE to reach one grey level per solver × schedule (measured), beside AYS Table 5 (published) | chart | Q1 — lab + quoted numbers | The schedule matters as much as the order |
| 11 | Should the sampler add noise? | toy: blur vs NFE for ODE and SDE samplers (exact start); spread kept vs steps on part 5's flawed schedule, with the two closed-form limits | chart | Q1 — lab measurements and closed forms | Noise costs accuracy, and buys forgetting |
| 12 | Should the sampler add noise? | Restart Table 4: Heun vs EDM's SDE vs Euler–Maruyama on ImageNet-64 by NFE | chart | Q1 — quoted numbers with setup | Deterministic wins below ~60 NFE; stochastic wins above |
