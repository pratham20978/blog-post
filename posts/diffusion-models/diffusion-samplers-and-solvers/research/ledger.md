# Source ledger — diffusion-samplers-and-solvers

Series `diffusion-models`, part 6. Sweep run 2026-10-09. Tier L4, so the floor is 10
peer-reviewed or standard sources carrying an identifier, across 4 scholarly databases.

Every arXiv source was read as arXiv's own HTML rendering (arxiv.org/html/<id>), converted to text
with the math kept as LaTeX `alttext`, in the session scratchpad. EDM has no HTML rendering, so it
was read from the NeurIPS proceedings PDF and its 36-page supplementary PDF; Hochbruck & Ostermann
from the KITopen repository copy of the Acta Numerica paper. Every claim row below was checked
against the paper's own text, table, algorithm or equation, not against an abstract or a search
snippet, except the four rows marked "abstract" in the Condition column. Venues were confirmed
through OpenAlex DOIs, the PMLR v235 index, the ICLR 2024 proceedings listing and arXiv comment
fields, as the search log records.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S01 | T1 | Yang, Zhang, Song, Hong, Xu, Zhao, Zhang, Cui & Yang, "Diffusion Models: A Comprehensive Survey of Methods and Applications" | ACM Computing Surveys | 2023 | 10.1145/3626235; arXiv:2209.00796 | peer-reviewed | https://doi.org/10.1145/3626235 | 2026-10-09 |
| S02 | T1 | Ho, Jain & Abbeel, "Denoising Diffusion Probabilistic Models" | NeurIPS 33 | 2020 | NeurIPS hash 4c5bcfec8584af0d967f1ab10179ca4b; arXiv:2006.11239 | peer-reviewed | https://proceedings.neurips.cc/paper/2020/hash/4c5bcfec8584af0d967f1ab10179ca4b-Abstract.html | 2026-10-09 |
| S03 | T1 | Song, Meng & Ermon, "Denoising Diffusion Implicit Models" | ICLR | 2021 | arXiv:2010.02502 | peer-reviewed | https://arxiv.org/abs/2010.02502 | 2026-10-09 |
| S04 | T1 | Song, Sohl-Dickstein, Kingma, Kumar, Ermon & Poole, "Score-Based Generative Modeling through Stochastic Differential Equations" | ICLR | 2021 | arXiv:2011.13456 | peer-reviewed | https://arxiv.org/abs/2011.13456 | 2026-10-09 |
| S05 | T1 | Bao, Li, Zhu & Zhang, "Analytic-DPM: an Analytic Estimate of the Optimal Reverse Variance in Diffusion Probabilistic Models" | ICLR | 2022 | arXiv:2201.06503 | peer-reviewed | https://arxiv.org/abs/2201.06503 | 2026-10-09 |
| S06 | T1 | Liu, Ren, Lin & Zhao, "Pseudo Numerical Methods for Diffusion Models on Manifolds" (PNDM) | ICLR | 2022 | arXiv:2202.09778 | peer-reviewed | https://arxiv.org/abs/2202.09778 | 2026-10-09 |
| S07 | T1 | Lu, Zhou, Bao, Chen, Li & Zhu, "DPM-Solver: A Fast ODE Solver for Diffusion Probabilistic Model Sampling in Around 10 Steps" | NeurIPS 35 | 2022 | 10.52202/068431-0418; arXiv:2206.00927 | peer-reviewed | https://doi.org/10.52202/068431-0418 | 2026-10-09 |
| S08 | T1 | Karras, Aittala, Aila & Laine, "Elucidating the Design Space of Diffusion-Based Generative Models" (EDM) | NeurIPS 35 | 2022 | 10.52202/068431-1926; arXiv:2206.00364 | peer-reviewed | https://proceedings.neurips.cc/paper_files/paper/2022/hash/a98846e9d9cc01cfb87eb694d946ce6b-Abstract-Conference.html | 2026-10-09 |
| S09 | T1 | Lu, Zhou, Bao, Chen, Li & Zhu, "DPM-Solver++: Fast Solver for Guided Sampling of Diffusion Probabilistic Models" | Machine Intelligence Research | 2025 | 10.1007/s11633-025-1562-4; arXiv:2211.01095 | peer-reviewed | https://doi.org/10.1007/s11633-025-1562-4 | 2026-10-09 |
| S10 | T1 | Zhao, Bai, Rao, Zhou & Lu, "UniPC: A Unified Predictor-Corrector Framework for Fast Sampling of Diffusion Models" | NeurIPS 36 | 2023 | 10.52202/075280-2170; arXiv:2302.04867 | peer-reviewed | https://doi.org/10.52202/075280-2170 | 2026-10-09 |
| S11 | T1 | Zheng, Lu, Chen & Zhu, "DPM-Solver-v3: Improved Diffusion ODE Solver with Empirical Model Statistics" | NeurIPS 36 | 2023 | 10.52202/075280-2423; arXiv:2310.13268 | peer-reviewed | https://doi.org/10.52202/075280-2423 | 2026-10-09 |
| S12 | T1 | Xu, Deng, Cheng, Tian, Liu & Jaakkola, "Restart Sampling for Improving Generative Processes" | NeurIPS 36 | 2023 | 10.52202/075280-3356; arXiv:2306.14878 | peer-reviewed | https://doi.org/10.52202/075280-3356 | 2026-10-09 |
| S13 | T1 | Chen, Chewi, Lee, Li, Lu & Salim, "The probability flow ODE is provably fast" | NeurIPS 36 | 2023 | 10.52202/075280-2998; arXiv:2305.11798 | peer-reviewed | https://doi.org/10.52202/075280-2998 | 2026-10-09 |
| S14 | T1 | Sabour, Fidler & Kreis, "Align Your Steps: Optimizing Sampling Schedules in Diffusion Models" | ICML (PMLR 235:42947–42975) | 2024 | pmlr-v235-sabour24a; arXiv:2404.14507 | peer-reviewed | https://proceedings.mlr.press/v235/sabour24a.html | 2026-10-09 |
| S15 | T1 | Xue, Liu, Chen, Zhang, Hu, Xie & Li, "Accelerating Diffusion Sampling with Optimized Time Steps" | CVPR | 2024 | 10.1109/CVPR52733.2024.00792; arXiv:2402.17376 | peer-reviewed | https://doi.org/10.1109/CVPR52733.2024.00792 | 2026-10-09 |
| S16 | T1 | Chen, Zhou, Wang, Shen & Lyu, "On the Trajectory Regularity of ODE-based Diffusion Sampling" | ICML (PMLR 235:7905–7934) | 2024 | pmlr-v235-chen24bm; arXiv:2405.11326 | peer-reviewed | https://proceedings.mlr.press/v235/chen24bm.html | 2026-10-09 |
| S17 | T1 | Zhou, Chen, Wang & Chen, "Fast ODE-based Sampling for Diffusion Models in Around 5 Steps" (AMED-Solver) | CVPR | 2024 | 10.1109/CVPR52733.2024.00743; arXiv:2312.00094 | peer-reviewed | https://doi.org/10.1109/CVPR52733.2024.00743 | 2026-10-09 |
| S18 | T1 | Ning, Li, Su, Salah & Ertugrul, "Elucidating the Exposure Bias in Diffusion Models" | ICLR | 2024 | ICLR 2024 hash 4267d84ca2f6fbb4aa5172b76b433aca; arXiv:2308.15321 | peer-reviewed | https://proceedings.iclr.cc/paper_files/paper/2024/hash/4267d84ca2f6fbb4aa5172b76b433aca-Abstract-Conference.html | 2026-10-09 |
| S19 | T1 | Hochbruck & Ostermann, "Exponential integrators" | Acta Numerica 19 | 2010 | 10.1017/S0962492910000048 | peer-reviewed | https://doi.org/10.1017/S0962492910000048 | 2026-10-09 |
| S20 | T3 | Hugging Face diffusers v0.40.0: `schedulers/scheduling_dpmsolver_multistep.py`, `scheduling_ddim.py`, `scheduling_heun_discrete.py` (installed package source) | — | 2026 | diffusers==0.40.0 | source | https://github.com/huggingface/diffusers/tree/v0.40.0/src/diffusers/schedulers | 2026-10-09 |
| S21 | T3 | crowsonkb/k-diffusion v0.1.1.post1, `k_diffusion/sampling.py` | — | 2023 | tag v0.1.1.post1 (commit 0c6cc822e050) | source | https://github.com/crowsonkb/k-diffusion/blob/v0.1.1.post1/k_diffusion/sampling.py | 2026-10-09 |
| S22 | T3 | CompVis/stable-diffusion, `scripts/txt2img.py` at commit 21f890f (2022-11-16) | — | 2022 | commit 21f890f9da3c | source | https://github.com/CompVis/stable-diffusion/blob/21f890f9da3cfbeaba8e2ac3c425ee9e998d5229/scripts/txt2img.py | 2026-10-09 |

Nineteen peer-reviewed sources carry an identifier. DPM-Solver++ (S09) circulated as an arXiv
preprint from 2022 and is now in Machine Intelligence Research (DOI on its arXiv record, confirmed by
OpenAlex), so it is carried as peer-reviewed. S20–S22 are implementation evidence for what the
libraries and the reference Stable Diffusion script actually do.

**Checked and not carried.** Nichol & Dhariwal, "Improved Denoising Diffusion Probabilistic Models"
(ICML 2021, arXiv:2102.09672): read for its learned-variance result (good samples in about 50 steps);
the post makes the ancestral-variance point through Analytic-DPM (S06) and DPM-Solver's Table 4.
Lin et al., "Common Diffusion Noise Schedules and Sample Steps are Flawed" (WACV 2024): part 5 cites
it for the zero-terminal-SNR schedule and trailing spacing that this post's worked example reuses; this
post makes no new claim from it. Ma et al., "Efficient Diffusion Models: A Comprehensive Survey from
Principles to Practices" (TPAMI 2025, 10.1109/TPAMI.2025.3569700): read for the map; S01's taxonomy
is the one the post uses. DEIS (Zhang & Chen, ICLR 2023, arXiv:2204.13902): read; DPM-Solver (S07)
carries the exponential-integrator argument the post makes, and S01 groups the two. Jolicoeur-Martineau
et al., "Gotta Go Fast" (arXiv:2105.14080): no venue found, and EDM (S08) and Restart (S12) already
report its adaptive SDE solver as a baseline. Chen et al., "Sampling is as easy as learning the score"
(arXiv:2209.11215): read the abstract; S13 states the SDE-versus-ODE guarantee contrast the post needs.
Sohl-Dickstein et al. 2015: the small-step Gaussian argument is cited through DDPM (S02), which
states it for its own choice of T.

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Google Scholar | survey-first: diffusion models sampling survey fast sampler | Yang et al. (ACM CSUR 2023, cited 3,837), Cao (TKDE 2024), Shen efficient survey (2025), Croitoru (TPAMI 2023), Ulhaq, Watson 2022; Yang's §3 gave the learning-free / learning-based map |
| 2 | 1 | Google Scholar | survey training-free samplers diffusion models ODE solver numerical | DPM-Solver (NeurIPS 2022, cited 3,024), Ma et al. TPAMI 2025, S4S (2025), Luo distillation survey; confirmed DPM-Solver as a central paper |
| 3 | 1 | Google Scholar | efficient diffusion models survey sampling acceleration solver | Xue et al. optimized time steps (CVPR 2024), parallel-sampling papers, Li et al. provable acceleration; the schedule-optimisation forward lead |
| 4 | 1 | arXiv API | id_list for 25 candidate ids: titles, comments, journal-ref, DOI | ICLR 2021 (DDIM, score SDE), ICLR 2022 (PNDM, Analytic-DPM, progressive distillation), NeurIPS 2022 (DPM-Solver, EDM), NeurIPS 2023 (UniPC, DPM-Solver-v3), ICML 2024 (GITS), DPM-Solver++ DOI in Machine Intelligence Research |
| 5 | 1 | arXiv HTML | full text of 18 papers via arxiv.org/html | about 230k words in the scratchpad for grep verification; EDM has no HTML rendering |
| 6 | 1 | NeurIPS proceedings | EDM main paper PDF and supplementary PDF (NeurIPS 2022) | full text including Algorithms 1–3, Appendix D.1 (truncation error), Table 5 (stochastic settings) |
| 7 | 1 | DBLP | search/publ/api?q=DPM-Solver | Anubis bot-verification page; DBLP unusable this session, as in parts 1–5 |
| 8 | 1 | OpenAlex | title search for DPM-Solver and EDM | NeurIPS DOIs 10.52202/068431-0418 and 10.52202/068431-1926; work ids for the forward chase |
| 9 | 1 | OpenAlex | cited-by DPM-Solver (W4281661987) and EDM (W4281969232), title filtered to solver/sampling/schedule/steps, by citations | DPM-Solver++ (MIR 2025), Lin et al. (WACV 2024), AMED-Solver and Xue et al. (both CVPR 2024), exact inversion of DPM-Solvers; OpenAlex's citation graph for these preprints is thin (25 hits) |
| 10 | 1 | Semantic Scholar Graph API | citations of arXiv:2206.00927 and 2206.00364, influential only | 81 and 161 influential among the latest 1,000; mostly 2025–26 preprints (few-step schedulers, flow maps); no correction of the order claims found |
| 11 | 1 | OpenAlex | title search: Restart, UniPC, DPM-Solver-v3, AYS, GITS, DEIS | NeurIPS 2023 DOIs for Restart, UniPC and DPM-Solver-v3; AYS, GITS and DEIS only as arXiv records |
| 12 | 1 | PMLR | v235 index grepped for "Align Your Steps" and "Trajectory Regularity" | both in ICML 2024: PMLR 235:42947–42975 and 235:7905–7934 |
| 13 | 1 | OpenAlex | title search: PNDM, Analytic-DPM, score SDE, Yang survey, Ma survey, "Exponential integrators" | ACM CSUR DOI for S01, TPAMI DOI for Ma, ICLR 2021 for score SDE, Acta Numerica DOI and the KITopen open copy for Hochbruck & Ostermann |
| 14 | 1 | KITopen | publikationen.bibliothek.kit.edu/1000024914 | the published Acta Numerica version as an open PDF (28k words) |
| 15 | 1 | OpenAlex | abstracts: optimized time steps, AMED-Solver, DPM-Solver-v3 | CVPR 2024 DOIs for S15 and S17; S11's abstract numbers (arXiv API was rate-limited, 429) |
| 16 | 1 | ICLR proceedings | 2024 listing grepped for "Elucidating the Exposure Bias" | listed, hash 4267d84c…; the 2022 and 2023 listings returned 404, so ICLR 2021–2023 venues rest on arXiv comments and OpenAlex |
| 17 | 2 | arXiv HTML | DDIM §§4–5, Table 1, App. B; DDPM §§2–4, Alg. 2; score SDE §§4, App. D–E | DDIM as Euler in (x̄, σ) vs Euler in t; η family; same-model FID at 10–1,000 steps; T = 1000 chosen for NFE parity; ancestral as a reverse-SDE discretisation; RK45 tolerance and NFE |
| 18 | 2 | arXiv HTML | DPM-Solver §§3–5, Tables 1 and 4, App. C–D | semi-linear structure, variation of constants, λ change of variable, DPM-Solver-1 = DDIM, order theorem, RK-vs-DPM-Solver ablation, five samplers on one CIFAR-10 model, the 0.0078 tolerance |
| 19 | 2 | NeurIPS PDF | EDM §§2–4, Alg. 1–2, App. D.1–D.2, Table 5 | Euler O(h²) vs Heun O(h³) local error, Euler last step, ρ schedule and its truncation-error analysis, σ(t) = t straight trajectories, churn sampler and its settings, the 7.3×/300×/3.2× NFE reductions |
| 20 | 2 | arXiv HTML | DPM-Solver++ §§3–4, 6.1, Alg. 1–2; UniPC abstract and §3 | data prediction, multistep 2M and why it shrinks effective step size, instability of high order under large guidance, stochastic DDIM = SDE-DPM-Solver++1; UniC adds order without NFE |
| 21 | 2 | KITopen PDF | Hochbruck & Ostermann §1 | variation-of-constants, exponential Euler, bounded exact propagator vs explicit Euler, stiff vs classical order |
| 22 | 3 | arXiv HTML | AYS Table 5 and §5; Restart Tables 2 and 4 | same-model numbers: solver × schedule at 10–50 NFE (EDM's CIFAR-10 model); Heun vs EDM SDE vs Euler–Maruyama by NFE on ImageNet-64 |
| 23 | 4 | arXiv HTML | Restart §§1–3 | ODE samplers plateau, SDE samplers win at large NFE; Euler O(δ²) vs Euler–Maruyama O(δ^{3/2}) local error; contraction of accumulated error |
| 24 | 4 | Google Scholar | exposure bias diffusion models sampling error accumulation | Ning et al. (ICLR 2024), Li et al. shifted time steps (ICLR 2024), Ning 2023 input perturbation; real samplers feed the network its own imperfect samples |
| 25 | 4 | Google Scholar | deterministic versus stochastic sampler diffusion ODE SDE error contraction | Beyler & Bach 2025 (preprint), contractive diffusion policies, "contractivity trap" (2026 preprint); S13 is the peer-reviewed statement used |
| 26 | 4 | arXiv API | abstracts of arXiv:2209.11215 and 2305.11798 | SDE guarantees under L2 score error; the first polynomial PF-ODE guarantee needs a stochastic corrector (NeurIPS 2023) |
| 27 | 5 | Local source | diffusers 0.40.0 schedulers in the lab venv | DPMSolverMultistep defaults (dpmsolver++, order 2, lower_order_final, Karras ρ = 7 hard-coded), DDIM eta 0.0, Heun order 2 |
| 28 | 5 | GitHub | k-diffusion tags API; raw `sampling.py` at v0.1.1.post1 | get_sigmas_karras ρ = 7, Euler ancestral's σ_up/σ_down, Heun with Euler last step, DPM-Solver++(2M) with first-order first and last steps |
| 29 | 5 | GitHub | CompVis/stable-diffusion latest commit; raw `scripts/txt2img.py` | DDIM by default, 50 steps, η = 0.0; `--plms` and `--dpm_solver` flags |
| 30 | 6 | arXiv HTML | Restart Figure 1(b); EDM Figure 3; DPM-Solver Figure 2 | how the regimes are usually drawn; licences checked (only Restart's is CC BY 4.0) |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | A survey sorts fast sampling into learning-free methods (SDE solvers and ODE solvers that discretise the reverse SDE or the probability-flow ODE) and learning-based ones (optimised discretisation, truncated diffusion, knowledge distillation) | S01 §3, §3.1, §3.2 | survey taxonomy |
| L02 | DDPM set T = 1000 so its sampler would make as many network evaluations as previous work, and chose small, linearly increasing variances so the reverse and forward processes have approximately the same (Gaussian) functional form | S02 §2, §4 | pixel-space DDPM |
| L03 | DDIM's authors measured the time to produce samples growing linearly with the length of the sampling trajectory | S03 §5.1, Fig. 4 | one 2080 Ti, 50k samples |
| L04 | Because the DDIM objective depends only on the marginals q(x_t given x_0), forward processes shorter than T define faster generative processes without training a different model | S03 §4.2 | models trained with the DDPM objective |
| L05 | Rewriting DDIM with x̄ = x/√ᾱ and σ = √((1−ᾱ)/ᾱ) shows it is Euler's method on dx̄ = ε_θ dσ; the score-SDE probability-flow sampler takes Euler steps in t instead, and the two differ when steps are few | S03 §4.3, App. B | — |
| L06 | DDIM's Table 1, CIFAR-10, one model (T = 1000): FID for η = 0 is 13.36, 6.84, 4.67, 4.16, 4.04 at 10, 20, 50, 100, 1000 steps; η = 0.5 is 16.66, 8.35, 5.25, 4.46, 4.29; η = 1 is 41.07, 18.36, 8.01, 5.78, 4.73; σ̂ (larger DDPM noise) is 367.43, 133.37, 32.72, 9.99, 3.17 | S03 Table 1 | CIFAR-10, FID on 50k samples |
| L07 | With the same initial latent, DDIM samples generated with different trajectory lengths share high-level features; DDPM samples do not | S03 §1, §5.2 | — |
| L08 | DDIM's σ_τi(η) family includes the original DDPM generative process at η = 1 and DDIM at η = 0, on any subsequence τ of the timesteps | S03 §4.2, eq. 16 | — |
| L09 | DDPM's ancestral sampling corresponds to one particular discretisation of the reverse-time VP SDE | S04 §4.2, App. E | — |
| L10 | The probability-flow ODE is a deterministic process whose trajectories share the same marginal densities as the SDE, so solving it from the prior gives samples from the data distribution | S04 §4.3, App. D | exact score |
| L11 | Analytic-DPM shows the optimal reverse variance has an analytic form in terms of the score, and uses it to improve DPMs' sample quality with a 20× to 80× speed-up | S05 abstract, §1, Thm 1 | pretrained score models |
| L12 | PNDM treats DDPM sampling as solving differential equations on manifolds; DDIM is a simple case of its pseudo numerical methods, and the pseudo linear multistep method is best in most of its tests | S06 abstract, §3 | — |
| L13 | The diffusion ODE is semi-linear; the variation-of-constants formula solves its linear part exactly, leaving an exponentially weighted integral of the network's output to approximate | S07 §3.1, eq. 3.1, Prop. 3.1 | — |
| L14 | DPM-Solver-k (k = 1, 2, 3) is a k-th-order solver: its error at time 0 is O(h_max^k) in half-log-SNR, using k function evaluations per step | S07 Thm 3.2, §3.2 | regularity conditions of App. B.1 |
| L15 | A step of DDIM and a step of DPM-Solver-1 are identical | S07 §4.1 | — |
| L16 | At 12 NFE on one CIFAR-10 model, RK2 in t scores FID 16.40, RK2 in λ 107.81 and DPM-Solver-2 5.28; RK3 in t 48.75, RK3 in λ 34.29, DPM-Solver-3 6.03 (full Table 1 at 12/18/24/30/36/42/48 NFE: RK2 t 16.40/7.25/3.90/3.63/3.58/3.59/3.54; RK2 λ 107.81/42.04/17.71/7.65/4.62/3.58/3.17; DPM-Solver-2 5.28/3.43/3.02/2.85/2.78/2.72/2.69; RK3 t 48.75/21.86/10.90/6.96/5.22/4.56/4.12; RK3 λ 34.29/4.90/3.50/3.03/2.85/2.74/2.69; DPM-Solver-3 6.03/2.90/2.75/2.70/2.67/2.65/2.65); explicit RK methods also discretise the linear term, whose exact solution is exponential, and can be unstable at large step sizes | S07 §4.2, §5.1, Table 1 | continuous VP model, uniform steps in t (RK in t) or λ (others) |
| L17 | DPM-Solver reaches FID 4.70 with 10 NFE, 3.75 with 12, 3.24 with 15 and 2.87 with 20 on CIFAR-10 | S07 §5.1 | continuous "VP deep" model, end time 10⁻⁴ / 10⁻³ as reported |
| L18 | On DDPM's discrete-time CIFAR-10 model, FID at 10 / 12 / 15 / 20 / 50 / 200 / 1000 NFE is 278.67 / 246.29 / 197.63 / 137.34 / 32.63 / 4.03 / 3.16 for DDPM, 35.03 / 27.69 / 20.82 / 15.35 / 7.34 / 4.11 / 3.84 for Analytic-DDPM, 13.58 / 11.02 / 8.92 / 6.94 / 4.73 / 4.07 / 3.95 for DDIM, 14.74 / 11.68 / 9.16 / 7.20 / 4.28 / 3.60 / 3.86 for Analytic-DDIM; DPM-Solver is 6.37 at 10, 4.65 at 12, 3.78 at 15 (end time 10⁻³), 3.80 at 20 and 3.57 at 46 adaptive (10⁻⁴) | S07 Table 4, App. E | linear schedule, 50k samples |
| L19 | Discrete-time noise-prediction models can be queried at non-integer times and still work well, which lets DPM-Solver run on them | S07 §3.4 | smooth time embeddings |
| L20 | DPM-Solver's adaptive solver uses an absolute tolerance of (x_max − x_min)/256, which is 0.0078 for VP image data | S07 App. C | image data in [−1, 1] |
| L21 | Euler's method has O(h²) local error; Heun's adds a correction for O(h³) local error at the cost of one more evaluation of D per step, and reverts to Euler on the step to σ = 0 to avoid dividing by zero | S08 §3, Alg. 1, App. D.1 | — |
| L22 | EDM's time steps are σ_i = (σ_max^{1/ρ} + i/(N−1)(σ_min^{1/ρ} − σ_max^{1/ρ}))^ρ, σ_N = 0; ρ = 3 nearly equalises truncation error, ρ between 5 and 10 samples images much better, and ρ = 7 is used throughout | S08 §3, eq. 5, App. D.1 | — |
| L23 | With σ(t) = t and s(t) = 1, also DDIM's choice, the ODE is dx/dt = (x − D)/t, a single Euler step to t = 0 gives D, the tangent always points toward the denoiser output, and solution trajectories are largely linear with curvature confined to a narrow σ range | S08 §3, Fig. 3 | — |
| L24 | EDM's sampling changes together (Heun, its time steps, σ(t) = t) cut the NFE needed for high-quality results 7.3× for VP, 300× for VE and 3.2× for DDIM on ImageNet-64 | S08 §3, Fig. 2 | three pretrained models |
| L25 | With a Lipschitz D the global error is bounded by a constant times the largest local error; measured on a CIFAR-10 VE model, uniform σ steps give Euler an RMSE near 0.56 at σ ≤ 0.5, while Heun with ρ = 3 keeps RMSE between 0.0030 and 0.0045 at every level, and ρ > 3 gives better FID | S08 App. D.1, Fig. 13 | VE CIFAR-10 model, N = 64 |
| L26 | EDM writes the SDE as the probability-flow ODE plus a Langevin term; the Langevin part drives samples toward the right marginal, correcting errors made in earlier steps, while discretising it adds error, so the right amount of stochasticity is empirical | S08 §4, eq. 6 | — |
| L27 | EDM's stochastic sampler adds noise to raise the level by γ_i = min(S_churn/N, √2 − 1) inside [S_tmin, S_tmax], then takes one Heun step; the four parameters were set per model by grid search (ImageNet-64, own model: 40, 0.05, 50, 1.003) | S08 Alg. 2, §4, App. E.2, Table 5 | — |
| L28 | Excessive churn gradually loses detail and drifts colours with trained denoisers; EDM's experiments with analytical denoisers showed no such degradation | S08 §4 | — |
| L29 | Sampler improvements alone brought the ImageNet-64 model from FID 2.07 to 1.55 | S08 §4 | class-conditional ImageNet-64, ADM model |
| L30 | NFE counts evaluations of D per image; because sampling is dominated by the cost of D, NFE translates directly to speed | S08 §3 | — |
| L31 | Earlier high-order solvers become unstable for guided sampling with large guidance scales, even worse than DDIM; DPM-Solver++ solves the ODE for the data-prediction model, adds thresholding, and uses a multistep variant to reduce the effective step size | S09 abstract, §3, §4 | guided sampling |
| L32 | DPM-Solver++(2M) updates with D = (1 + 1/(2r))D_i − (1/(2r))D_{i−1}, r = h_{i−1}/h_i; with N evaluations a multistep method takes N steps where a k-th-order singlestep one takes N/k, so its steps are about 1/k as long | S09 §4.2, Alg. 2 | — |
| L33 | UniPC's corrector UniC reuses the model output at the new point, so it adds no evaluations, and raises order p to p + 1; UniPC reports FID 3.87 on CIFAR-10 and 7.51 on ImageNet 256 with 10 NFE | S10 abstract, §3, Thm 3.1 | regularity conditions of App. E.2 |
| L34 | DPM-Solver-v3 reports FID 12.21 with 5 NFE and 2.51 with 10 on unconditional CIFAR-10 | S11 abstract | its pretrained models |
| L35 | ODE samplers have smaller discretisation error but plateau, SDE samplers do better at large NFE; Euler on the ODE has local error O(δ²), Euler–Maruyama on the SDE O(δ^{3/2}); SDE stochasticity contracts accumulated error, and the network's approximation error dominates at large NFE; Restart alternates large forward noise additions with backward ODE steps in chosen intervals | S12 §1, §3, §4 | Wasserstein upper bounds |
| L36 | On EDM's ImageNet 64×64 model, Heun's FID is 2.46, 2.30, 2.25, 2.24 at 35, 63, 127, 255+ NFE; EDM's stochastic sampler 2.97, 2.24, 1.75, 1.50, 1.45, 1.40 at 35 to 1023; Euler–Maruyama 59.71, 11.91, 3.38, 1.89 at 128 to 1024; Restart 2.38 at 39 down to 1.36 at 623 | S12 Tables 4, 5 | 50k samples, class-conditional |
| L37 | The first polynomial-time convergence guarantees for the probability-flow ODE implementation use an added corrector step and need new techniques for deterministic dynamics without contractivity | S13 abstract | L² score error assumptions |
| L38 | Align Your Steps optimises sampling schedules per solver, model and dataset; on EDM's CIFAR-10 model at 10/20/30/50 NFE, DDIM scores 16.44/6.01/3.97/2.82 with log-SNR steps and 10.73/4.67/3.30/2.56 with AYS steps; DPM-Solver++(2M) 5.07/2.37/2.12/2.04 and 2.98/2.10/2.02/2.01 | S14 §5, Table 5 | CIFAR-10, 50k samples |
| L39 | Optimised time steps minimise the distance between the ground-truth ODE solution and the solver's approximation, solved with a constrained trust-region method in under 15 seconds | S15 abstract | — |
| L40 | ODE sampling trajectories show a strong shape regularity regardless of the content generated, and a dynamic-programming time schedule fits steps to that structure | S16 abstract | — |
| L41 | Each sampling trajectory lies almost in a two-dimensional subspace; AMED-Solver reports FID 6.61 on CIFAR-10 and 10.74 on ImageNet 64×64 with 5 NFE | S17 abstract | learns a small mean-direction predictor |
| L42 | Exposure bias is the input mismatch between training and sampling; the prediction error at each sampling step is its root cause | S18 abstract, §3 | — |
| L43 | For semilinear problems the variation-of-constants formula represents the exact solution; interpolating the nonlinearity at the known starting value gives the exponential Euler method, whose exact linear propagator stays bounded independent of the step size, unlike explicit Euler's | S19 §1 | stiff semilinear problems |
| L44 | diffusers 0.40.0's multistep DPM-Solver scheduler defaults to algorithm "dpmsolver++", solver_order 2, and lower_order_final (first-order final steps below 15 steps, for stability); its Karras sigmas hard-code ρ = 7; with zero terminal SNR its Euler and DPM-Solver schedulers set ᾱ_T = 2⁻²⁴ (σ ≈ 4,096); DDIM's default η is 0 | S20 (`scheduling_dpmsolver_multistep.py` __init__, `_convert_to_karras`, step(); `scheduling_euler_discrete.py`; `scheduling_ddim.py`) | v0.40.0 |
| L45 | k-diffusion's get_sigmas_karras defaults to ρ = 7; sample_euler is the Euler update; sample_euler_ancestral steps to σ_down then adds σ_up noise (σ_up = √(σ′²(σ² − σ′²)/σ²) at η = 1); sample_heun is EDM's Algorithm 2 with an Euler last step; sample_dpmpp_2m is DPM-Solver++(2M) with first-order first and last steps | S21 | tag v0.1.1.post1 |
| L46 | Stable Diffusion's original txt2img script samples with DDIM by default, 50 steps, η = 0.0, with flags for PLMS and DPM-Solver | S22 (`--ddim_steps`, `--ddim_eta`, `--plms`, `--dpm_solver`) | commit 21f890f |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S12 | Figure 1(b) (schematic: ODE, SDE and Restart error against NFE) | Should the sampler add noise? | draws the two regimes | CC BY 4.0 (arXiv HTML) | https://arxiv.org/abs/2306.14878 | not reused: a schematic, and the post measures the same crossover (Figure 11) and charts Restart's own Table 4 (Figure 12) |
| F2 | S12 | Figure 3 (FID against NFE, CIFAR-10 VP and ImageNet-64 EDM) | Should the sampler add noise? | the measured crossover on real models | CC BY 4.0 | https://arxiv.org/html/2306.14878v2 | no extractable image in the HTML rendering; the numbers are in Tables 2 and 4, charted as Figure 12 |
| F3 | S08 | Figure 3 (1-D ODE curvature for VP, VE and DDIM schedules) | What does DDIM compute? | shows why σ(t) = t straightens trajectories | arXiv non-exclusive licence only | https://arxiv.org/abs/2206.00364 | do not reuse; Figure 3 draws the toy's own exact trajectories |
| F4 | S08 | Figure 13 (local truncation error per σ for ρ = 1…7) | Where should the steps go? | the canonical per-step error plot | arXiv non-exclusive licence only | https://arxiv.org/abs/2206.00364 | do not reuse; the lab repeats the measurement on the toy (Figure 9) |
| F5 | S07 | Figure 2 (FID against NFE across samplers) | How do higher-order solvers buy accuracy? | many samplers on one model | arXiv non-exclusive licence only | https://arxiv.org/abs/2206.00927 | do not reuse; Figure 7 charts the same paper's Tables 1 and 4 |

## Open questions

- The toy's denoiser is exact, so it cannot show exposure bias (S18) or the non-conservative errors
  EDM blames for churn's loss of detail (S08 §4). The post says so and takes those effects from the
  papers.
- Which sampler wins at a given NFE on a given model is an empirical question every source answers
  for its own models only. The post reports each comparison inside one paper's setup and never across
  papers.
- Whether optimised schedules (S14, S15) keep their margin under strong guidance is outside this part.
