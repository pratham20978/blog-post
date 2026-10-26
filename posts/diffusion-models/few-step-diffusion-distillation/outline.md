# Outline — few-step-diffusion-distillation

Series: `diffusion-models`, part 7 of 12. Read `../plan.md`, `../context.md` and `../access.md`
before editing.

## Brief

- **Subject:** machine learning / generative modelling — sampling in one to four network calls by
  training something new: distillation, consistency models, distribution matching, flow maps.
- **Tier:** L3 · **Difficulty:** advanced. Set by the series plan, not re-proposed. L3 because the
  reader learns four method families plus one synthesis, each with a mechanism and evidence, and the
  honest worked example is one number on one screen. Advanced because it assumes the denoiser as
  E[x₀ | x], the probability-flow ODE and DDIM's update in σ coordinates (part 6), and what training
  a network with a loss means.
- **Audience:** an engineer choosing or training a few-step model (the "Turbo", "LCM", "Lightning",
  "schnell" variants) who wants to know what each method trains, what it costs, and what breaks.
- **The one question this part owns:** how do 20 steps become 1, and what breaks?
- **What falls out of it, and the post also owns:**
  1. Why no solver can take one step (the denoiser averages; the endpoint map has cliffs)
  2. How progressive distillation halves the steps (sharp targets; rounds; error per round)
  3. What a consistency model learns (endpoint of the path; boundary condition; multistep sampling)
  4. What happens when the student stops following the path (DMD/DMD2/ADD; reverse KL; fake score;
     mode dropping; TTUR)
  5. How one network takes any number of steps (shortcut models, CTM, MeanFlow: the flow map)
  6. Which metric shows the damage (pairing error vs distribution distance; blur vs diversity)
- **Deliberately deferred:** classifier-free guidance and its distillation → "later in this series"
  (part 8), mentioned only where Meng et al. and SDXL-Turbo need it; what FID measures and hides →
  later (part 9), the post only says which metric each failure moves; discrete tokens → part 11.
- **Series links (owner's instruction 2026-10-09):** name earlier parts by title whether or not they
  are live; the owner adds the links. Named: part 6 (Diffusion Samplers and Solvers) for the ODE,
  DDIM's update and NFE; part 5 (Training a Diffusion Model) for crescent world and why ε-prediction
  fails at zero SNR; part 1 (What a Diffusion Model Actually Does, live) for the averaging argument.
  Later parts stay "later in this series".
- **Must not repeat:** part 6's solver order, NFE accounting, step schedules and ODE vs SDE (three
  sentences of recap at most); part 5's targets and weighting beyond one sentence.
- **Lab:** **G1** — CPU PyTorch in the series' pinned environment. The exact denoiser and exact ODE of
  crescent world at 8×8 are the teacher, so every student error is the student's; students are small
  MLPs trained on CPU. No access request: a GPU would train bigger students on a teacher whose true
  path is unknown, which measures less, not more (see `../access.md`).
- **Target:** ~6,300 words of prose (References add ~900; L3 ceiling 7,500 counts both), 10 figures,
  one lab (README, `distill.py`, requirements, captures, expected output, notebook, zip).

## Section budget

| Section | Budget | Reader can now… |
|---|---:|---|
| Insights + who this is for + jump list + notice | 300 | say what every few-step method learns and the two ways it fails |
| Why this matters | 170 | see that the step count is now a training decision with a measurable price |
| The problem | 550 | state why a solver's one-step answer is the blur, and what a student must learn instead |
| Worked example | 700 | compute the exact endpoint, DDIM's few-step answers and one distillation target on one number, and see the cliff |
| Intuition | 280 | describe distillation as learning where paths end, and say where the analogy breaks |
| How does progressive distillation halve the steps? | 600 | explain the halving target, why ε fails, and read error per round |
| What does a consistency model learn? | 600 | explain self-consistency, the boundary condition, and why multistep sampling stalls |
| What happens when the student stops following the path? | 650 | explain DMD's two scores, why it drops modes, and how DMD2 fixes it |
| Can one network take any number of steps? | 550 | explain shortcut models, CTM and MeanFlow as one object, the flow map |
| Which metric shows the damage? | 450 | match each failure to the metric that sees it |
| The math | 500 | write the flow map in DDIM form, each method's target, and DMD's gradient |
| Implementation | 300 | write the PD target, the CD loss and the DMD update over any denoiser |
| Limitations and common mistakes | 330 | avoid five concrete failures |
| Key takeaways + Try it yourself | 300 | — |

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| distillation (teacher, student) | Insights / The problem | training a new network to reproduce what a slower procedure produces | it is how 20 calls become 1 | whenever a few-step model is trained from a pretrained one |
| flow map | The problem | the exact map from a sample at one noise level to the ODE's point at a lower one | every path-following method learns a piece of it | reading any few-step paper |
| one-step student | The problem | a network whose single call is meant to equal the whole ODE solve | the target of the post | judging a 1-step claim |
| decision (between modes) | Worked example | the noise range where nearby starts end on different modes | where the flow map has a cliff | where students fail |
| progressive distillation | body 1 | halving the step count round by round with a sharp target | first working few-step method | when a fixed step count is fine |
| consistency model, boundary condition, consistency distillation / training | body 2 | a network mapping any point on a path to its end; f(x, σ_min) = x; with or without a teacher | the line of iCT, sCM, LCM | when one network should serve 1–2 steps |
| target network (EMA) | body 2 | a slowly updated copy that produces training targets | CM stability | training CMs |
| multistep consistency sampling | body 2 | denoise to the end, add fresh noise, denoise again | how CMs use more calls | why CM quality stalls with steps |
| distribution matching (DMD), reverse KL, fake score | body 3 | a generator trained only to match the output distribution, by the difference of two scores | DMD/DMD2's route | when pairing does not matter but diversity does |
| mode collapse / dropping | body 3 | a generator covering only some modes of the data | DMD's failure | reading recall |
| two time-scale update rule (TTUR) | body 3 | several critic updates per generator update | DMD2's fix | training any critic-based distiller |
| adversarial loss (GAN) | body 3 | a discriminator trained to tell real from generated | ADD, DMD2, LADD | shipped Turbo/schnell models |
| shortcut model, self-consistency | body 4 | a network conditioned on step size; one big jump = two half jumps | trains in one run | any-step sampling |
| flow matching | body 4 | training the velocity of a straight-line noise-to-data interpolation | shortcut models and MeanFlow build on it | reading flow-based papers |
| CTM, MeanFlow (average velocity) | body 4 | other parameterisations of the same flow map | the unification | — |
| pairing error (flip rate), sliced Wasserstein distance | The problem / body 5 | per-noise distance to the exact endpoint; distance between sample sets | the post's two yardsticks | deciding what "works" means |
| precision, recall | body 5 | fidelity and coverage of a sample set | where the published failures show | reading tables |

## Figure plan

Route gate run per figure (source check first: no candidate paper figure carries a reuse licence;
ledger F1–F3). Every measured number is read from `lab/captures.json`.

| # | Section | One thing it must communicate | Route | Why |
|---|---|---|---|---|
| 1 | Worked example | the exact endpoint is a cliff in the starting noise; DDIM's few-step answers and a least-squares student are ramps | plot | Q1/Q4 — closed-form and fitted curves on one number |
| 2 | The problem | every method sorted by where its training target comes from: teacher endpoints, teacher steps, its own jumps, data, two scores | mermaid | Q3 — 13 nodes, two families joined at the teacher |
| 3 | Progressive distillation | students against solvers at matched calls, on pairing and on sample distance | chart | Q1 — measured, lab |
| 4 | Progressive distillation / consistency | what one-call samples look like near and far from a decision | placed | Q4 — real 8×8 images from the lab |
| 5 | Consistency models | errors live at the decisions: flips and blends by distance from the nearest boundary | chart | Q1 — measured, lab |
| 6 | Distribution matching | the DMD update: generator, noise, two denoisers, the difference, and the critic's own loop | placed | Q5 — 7 nodes, labelled edges |
| 7 | Distribution matching | crescent coverage over training for 1:1, 5:1 and regression | chart | Q1 — measured, lab |
| 8 | Shortcut models | one network at any step count (shortcut, CM multistep) against one student per count (PD) | chart | Q1 — measured, lab |
| 9 | Shortcut models | one codebase, six objectives, three step budgets | chart | Q1 — quoted table numbers (L42) |
| 10 | Which metric | published precision and recall: which method loses fidelity and which loses coverage | chart | Q1 — quoted table numbers (L57) |
