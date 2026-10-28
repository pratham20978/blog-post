# Series context — Statistics for Data Scientists

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** working data scientists, analysts and ML engineers who run tests and fit regressions
  and need to know what each number guarantees, and when. Expert standard; every part opens on its
  worked instance before any formula.
- **Shape:** hybrid. Foundations ladder (1–4), tests and intervals (5–7), choosing a method (8–10),
  Bayesian inference (11–12), the linear model (13–14), GLMs (15–16), multilevel models (17–18).
  One parent per part; see `plan.md`.
- **Shared promise:** for any standard method the reader can compute it by hand, match it to the
  library, state the condition its guarantee needs, and measure what the guarantee becomes when
  the condition fails.
- **Terminology and notation (keep):**
  - estimand θ, estimator θ̂ (a random variable), estimate (its realised value). "Standard error"
    is the standard deviation of an estimator's sampling distribution, never of the data.
  - Every variance names its divisor (n, n − 1, n − p), as every count states its convention.
  - α is the test level, power is 1 − β. "Statistically significant" always carries its α, and
    estimates are reported with intervals rather than as significant or not.
  - "Confidence interval" (coverage of a procedure) and "credible interval" (posterior
    probability) are never interchanged. "Coverage" is the long-run share of intervals containing
    θ; "nominal" and "actual" coverage are kept distinct.
  - R = Monte Carlo replications, B = bootstrap replicates, S = posterior draws. Every simulated
    rate is printed as estimate ± MCSE with its R.
  - log is the natural log; tests are two-sided unless stated.
  - Parameterisations are stated with the library mapping wherever libraries differ. Negative
    binomial as (μ, k) with Var = μ + μ²/k (statsmodels α = 1/k; R `MASS` θ = k; SciPy
    `nbinom(n=k, p=k/(k+μ))`). Gamma as shape–rate; exponential as rate.
  - Software is named by exact function and pinned version.
- **Recurring examples (each confirmed with its licence at its part's research):**
  Clarke's V-1 counts (1, 4); Greenwood & Yule's accidents (1, 4, 12, 16); the German tank problem
  (3, 7); Efron–Morris batting averages (3, 17); R's `sleep` (2, 8); Pfizer–BioNTech efficacy (6,
  11, 12); the law-school data (7); Darwin's *Zea mays* (10); NIST Longley and Filip (13);
  Anscombe and Duncan (14); Challenger (15); `MASS::ships` and `quine` (16); `sleepstudy` (17);
  eight schools and Minnesota radon (18).
- **Lab:** G1 throughout, no access requests (see `access.md`). Pattern: by hand → matched to the
  library and R → guarantee measured with MCSE → real data with provenance.

## The data-science category boundary (keep this)

DS-1 owns the inferential core; the siblings apply it. Each seam names the owner of the mechanism.

- **DS-2 Experimentation.** DS-1 teaches p-values, power, intervals, multiplicity, the delta method
  (Part 4) and cluster-robust SEs (Part 17); DS-2 owns design, MDE planning, CUPED, ratio metrics,
  sequential tests, SRM, interference and bandits. DS-1 shows optional stopping once (Part 5).
- **DS-3 Causal Inference.** DS-1 reads coefficients as conditional associations and states the
  omitted-variable bias (Part 13). Identification strategies belong to DS-3.
- **DS-4 Time Series.** DS-1 assumes independence outside grouped data. It names autocorrelated
  errors (Part 14) and the block bootstrap (Part 7) and stops.
- **DS-5 Data Wrangling.** Missing-data mechanisms, imputation, outliers and selection bias are
  DS-5's. DS-1 states the complete-case, independent-sampling condition it relies on.
- **DS-6 Visualization** communicates DS-1's intervals and diagnostics. **DS-7 Product Analytics**
  owns survival analysis (pending the owner), metric design and Simpson's paradox in metric moves.
- **ML-2 Classical ML.** Prediction versus inference: regularisation, cross-validation,
  calibration and classification metrics are ML-2's. Part 3's estimator MSE decomposition is the
  seed ML-2 extends to prediction error.
- **ML-4 Probabilistic ML.** DS-1 uses MCMC (Metropolis by hand, NUTS as a tool read through its
  diagnostics) and hierarchical models. HMC and NUTS internals, Gibbs, variational inference, EM
  and graphical models are ML-4's.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | distributions-as-generative-stories | ready 2026-10-24, not published | which distribution, chosen from the process | sampling to 2; MLE, the Poisson-vs-NB test and CSN fitting to 4; count regression to 16 |
| 2 | sampling-distribution-central-limit-theorem | ready 2026-10-26, not published | how a statistic varies; when the CLT fails | estimator quality to 3; tests and intervals to 5 and 6; skewness-corrected intervals to 7; dependent data to DS-4 |
| 3 | estimator-bias-variance-mse | ready 2026-10-28, not published | what makes an estimator good; when bias pays | likelihood to 4; bootstrap on the maximum to 7; partial pooling to 17 and 18; prediction error to ML-2 |
| 4 | likelihood-mle-fisher-information | planned | MLE, information, Wald/score/LR, boundaries | — |
| 5 | hypothesis-testing-p-values-power | planned | what a p-value and power are; type M/S | — |
| 6 | confidence-intervals-coverage | planned | what 95% coverage means, measured | — |
| 7 | bootstrap-confidence-intervals | planned | intervals with no formula; where they fail | — |
| 8 | choosing-a-statistical-test | planned | the design picks the test | — |
| 9 | multiple-comparisons-fwer-fdr | planned | error across many tests, counted and uncounted | — |
| 10 | permutation-and-rank-tests | planned | exact tests; what rank tests test | — |
| 11 | bayesian-inference-conjugate-priors | planned | prior to posterior in closed form | — |
| 12 | mcmc-diagnostics-metropolis-nuts | planned | sampling a posterior and trusting the draws | — |
| 13 | linear-regression-inference | planned | every number in the regression table | — |
| 14 | regression-diagnostics-robust-standard-errors | planned | when to distrust the table, and the repair | — |
| 15 | glm-logistic-regression | planned | one algorithm for every GLM; logistic read right | — |
| 16 | count-regression-poisson-negative-binomial | planned | rates, exposure and overdispersion | — |
| 17 | linear-mixed-effects-models | planned | grouped data, partial pooling, REML | — |
| 18 | bayesian-hierarchical-models | planned | the Bayesian hierarchy and its funnel | — |

## Knowledge established

Per completed part, at most eight durable bullets (data and numbers, reference and tolerance,
broken condition, corrected claim, terms), reused rather than re-derived.

### Part 1 — Distributions as Generative Stories

- **Data** (CSVs with provenance in its `lab/data/`): Clarke 1946, 537 bombs on 576 squares,
  229/211/93/35/7/1, mean 0.9323, variance 0.9711 (n − 1). Greenwood & Yule 1920, 647 women,
  447/132/42/21/3/2, mean 0.4652, variance 0.6919. Also Bortkiewicz's 280 corps-years, `boot::coal`.
- **NB by moments:** k̂ = 0.955; χ² 103.1 (Poisson) against 4.20 (NB); Part 4 refits by ML. A Pólya
  (contagion) process gives the same one-period NB as proneness.
- **Tails, corrected claim:** unit-variance t₅ beyond 4σ is ×56.4 the normal; a straight log–log line
  is not a power law (lognormal: R² ≥ 0.98 in 91.4% of R = 1,000).

### Part 2 — The Sampling Distribution

- **Data:** UCI Online Retail (CC BY 4.0), net spend of 4,317 customers: mean £1,925.71, σ £8,266.70
  (divisor N), γ 21.58. Student's ten patients equal R's `sleep` (t 4.0621).
- **Core** (R = 100,000): one-sided 5% t-test, lower/upper: n = 30, 39.82%/0.05%; n = 1,000,
  17.69/0.94; n = 10,000, 7.86/2.99; corr(x̄, s) 0.972; s < σ in 88.1%, though s² is unbiased.
- **Pace:** lower tail ≈ 5% + 11.02 points × γ/√n, so ±10% of 5% needs n ≥ 486γ². Berry–Esseen
  (C₀ ≤ 0.469) guarantees distance 0.01 from n = 1,025,322; the exact distance gets there at 20,652.
- **Infinite variance:** Cauchy mean IQR 2.00 at every n; Pareto (index 1.5) lower tail stuck at
  26.4%.
- **Corrected:** "the CLT kicks in at n = 30": needed n grows like γ².

### Part 3 — Estimators and Their Errors

- **Data:** Efron & Morris's 1975 table of 18 players (equals Rdatasets `pscl::EfronMorris`); Ruggles &
  Brodie's three months via two reproductions (the 1947 paper not read).
- **Tanks** (N = 342, k = 5): MSE 5,448 for the MLE m (bias −56.17), 3,303 for the MVUE
  m(1 + 1/k) − 1, 3,212 for the biased m(k + 2)/(k + 1) − 1, 38,988 for one tank's serial.
  Rao–Blackwell: Var(2x̄ − 1) 7,706 = 4,403 + 3,303.
- **Rates:** maximum-based RMSE falls like 1/k, mean-based like 1/√k. The tank MLE is non-regular
  (support depends on N), outside Part 4's asymptotics.
- **Divisors** (n = 10, normal): MSE 0.2222 with n − 1, 0.1818 with n + 1; the best divisor
  n + 1 + (n − 1)κ/n is never n − 1 (16.4 for exponential data).
- **1970:** c 0.2117; total squared error 0.0753 against 0.0213 (the 1977 article's 0.077 and 0.022 do
  not reproduce); 79% of the spread was noise; hindsight slope 0.190. Replayed, James–Stein wins 96.2%
  of seasons (efficiency 2.66); exact risk for 18 means runs from 3 to 18, 6.81 at the batters' spread.
- **Corrected:** "unbiased estimators are the best ones": unbiasedness does not rank estimators.

## Decisions to preserve

- Every part follows the four-point angle (reconcile, condition, measure, read the output) and
  corrects one circulating claim, or says which point it omits and why.
- Every simulated number ships with its seed, replication count and MCSE; streams are
  `SeedSequence([stage, sub, seed])` and R comes from a target MCSE, R = p(1 − p)/MCSE². Two
  budgets are captured, the reader's `--quick` and the full one; the article quotes the full budget.
  A noisy comparison is measured at full budget before any narrative or figure rests on it, and an
  E4 fault is checked on the `--quick` budget, where it must still fail.
- Python is the lab language, with versions pinned per part at research. R ships as an optional
  `crosscheck.R` only in Parts 7, 13, 15, 16 and 17; elsewhere it is the author's private check, with
  its output in the captures.
- Data ship as small CSVs with a provenance header (source, citation, licence), or are fetched from
  the public source with a checksum. Simulated data are always labelled simulated.
- Results are stated with their conditions; proof sketches are labelled as sketches.
- Earlier parts are named by title in plain text, live or not, and listed in each manifest; the
  owner adds links. Later parts are "later in this series", with no number or title.
- Prose and social-card numbers are rounded once from the captures and rechecked by script before
  the gate. Plain-fact claims quote the exact value where one exists.
- Assets: copy Part 3's toolchain (`_build.py`, `_figs.py` helpers, `_social.py`, `_cover.py`,
  `_overlap.py`) and Part 1's `_mermaid.py`; labs follow Part 3's `lab/estimators.py`. Bin a discrete
  estimator's histogram on its own support.
- A real population is sampled with replacement, so draws are independent; the finite-population
  correction is named, not applied.

## Open threads

- Checkpoint S not formally passed: part count (18, or 16 with 10 and 18 optional), survival
  placement, title, and the optional smoothing part await the owner. Parts 1 to 3 were built on the
  owner's build requests of 2026-10-24, 2026-10-26 and 2026-10-28; none of the four decisions touches them.
- `data-science` category: in the validator and `frontmatter.md` since 2026-10-24, still missing
  from the live DB (a production write at publish, the owner's).
- Read second-hand (each ledger lists them): Greenwood & Yule 1920, Berry 1941, Ruggles & Brodie 1947,
  Goodman 1952, Blackwell 1947, Stigler 1990. Project Euclid serves a bot check to curl and WebFetch.
- blog-forge's `subject-playbooks.md` has no statistics entry (the owner's change to make).
- Dataset choices still open: prostate versus Hedenfalk for Part 9 (licence), the heteroskedastic
  dataset for Part 14, and the `sleepstudy` source for Part 17 (`lme4` or Rdatasets).
- Available RAM has been 2 to 6 GiB (`access.md`): keep the PyMC runs in Parts 12 and 18 small.

## Next part brief

- **Part:** 4, *Likelihood: The MLE, Fisher Information, and the Wald, Score and Likelihood-Ratio Tests*
  (`likelihood-mle-fisher-information`).
- **Can assume:** Parts 1 to 3, named by title: Part 1's V-1 and Greenwood–Yule counts and moment fits;
  Part 2's standard error and MCSE; Part 3's MSE = bias² + variance, consistency, sufficiency and the
  tank MLE (likelihood 1/C(N, k), biased, converging like 1/k).
- **Must teach:** `plan.md`'s Part 4 block, as written. Name the regularity conditions and use the tank
  MLE as the case outside them (Part 3 promised "likelihood in general" here).
- **Must not repeat:** the bias–variance decomposition, Rao–Blackwell, James–Stein; point to Part 3.
- **Evidence still needed:** Fisher 1922, Wilks 1938, Buse 1982, Efron & Hinkley 1978, Self & Liang
  1987, Pawitan. Project Euclid blocks curl and WebFetch: look for author, archive or Berkeley copies.
- **Handoff:** as `plan.md` states for Part 4.
