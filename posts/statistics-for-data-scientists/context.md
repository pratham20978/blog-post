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
| 4 | likelihood-mle-fisher-information | ready 2026-10-28, not published | MLE, information, Wald/score/LR, boundaries | p-values to 5; coverage to 6; variance-component boundary to 17; Bayes (11) and Fisher scoring (15) not previewed |
| 5 | hypothesis-testing-p-values-power | ready 2026-10-29, not published | what a p-value and power are; type M/S | coverage to 6; test choice to 8; multiplicity to 9; sequential designs to DS-2 |
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

- **Data** (CSVs with provenance): Clarke 1946, 537 bombs on 576 squares, 229/211/93/35/7/1, mean 0.9323;
  Greenwood & Yule 1920, 647 women, 447/132/42/21/3/2, mean 0.4652, variance 0.6919; Bortkiewicz's corps.
- **NB by moments:** k̂ = 0.955. **Tails:** unit-variance t₅ beyond 4σ is ×56.4 the normal; a straight
  log–log line is not a power law.

### Part 2 — The Sampling Distribution

- **Data:** UCI Online Retail spend of 4,317 customers (CC BY 4.0), γ 21.58; Student's ten patients equal
  R's `sleep` (t 4.0621).
- **Core:** one-sided 5% t-test at n = 30 errs 39.82%/0.05% (lower/upper); needed n grows like γ²
  ("the CLT kicks in at n = 30" corrected).

### Part 3 — Estimators and Their Errors

- **Tanks** (N = 342, k = 5): MSE 5,448 (MLE m), 3,303 (MVUE). **Divisors** (n = 10, normal): MSE 0.2222
  with n − 1, 0.1818 with n + 1. **1970 batting:** James–Stein wins 96.2% of replayed seasons.
- **Corrected:** "unbiased estimators are the best ones".

### Part 4 — Likelihood: The MLE, Three Tests, and Where χ² Fails

- **Poisson (Clarke):** λ̂ 0.9323, information 617.8, SE 0.0402; Wald, LR, score at 0.85: 4.18, 4.45, 4.59.
  Exact sizes at nλ₀ = 12.2: 8.84%, 6.57%, 4.26%.
- **NB by ML** (Greenwood–Yule): k̂ 0.865 (statsmodels needs `method="newton"`); profile 95% for k
  0.585–1.383 against Wald 0.500–1.230.
- **Boundary:** LR = 0 in 52.61%; χ²₁ rejects 2.17%, the mixture's 2.71 rejects 4.40%; V-1 p 0.52 → 0.26.
- **Corrected:** "the LR statistic is χ²": only for an interior null.

### Part 5 — p-Values and Power: How Wrong Can a Significant Result Be?

- **Data:** Durante et al. 2013 as Gelman & Carlin report it (17 points, SE 8.1, plausible 2);
  OSC 2015's `rpp_data.csv` (OSF fgjvw, CC0 1.0), 100 rows in the lab CSV.
- **Design analysis** (Lu–Qiu–Deng closed form): power 0.0570, type S 0.2396, exaggeration 9.537, bar
  ±15.88; Gelman & Carlin's simulated 9.7 is a high draw (SD 0.059).
- **Power:** 16 per group at d = 1 is 0.781398 (integral = `nct` = statsmodels = R `strict = TRUE`).
- **False positive risk** (not FDR, Part 9's): p = .03 gives 16.7% at even odds, 64.3% at prior 0.1;
  p ≤ .05 at prior 0.1 and 80% power, 36%.
- **Replication:** 97 → 36 significant, mean r 0.396 → 0.197. **TOST:** 16 per group shows only ±1.06
  SD at 80% power. **Peeking:** 8.31%, 37.36%, 52.99% after 2, 100, 1,000 looks.
- **Tool trap:** SciPy 1.18.1 `nct.cdf(-c, df, λ)` can return NaN past λ ≈ 8, statsmodels power `nan`;
  use `nct.sf(c, df, -λ)`.
- **Corrected:** "p = 0.03 means a 3% chance of a fluke" (true only at a prior of 0.87).

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
- Assets: copy Part 5's toolchain (`_build.py`, `_figs.py` helpers, `_social.py`, `_cover.py`,
  `_overlap.py`) and Part 1's `_mermaid.py`; labs follow Part 5's `lab/testing.py`. Bin a discrete
  estimator's histogram on its own support. Geist Mono has no combining hat: write "MLE", not λ̂.
  Assert no plotted curve holds a NaN: the browser drops a polyline with one.
- Social: feed cards only, no Stories (owner, 2026-10-30); `--social` then fails exactly its four
  Story checks, as expected.
- A real population is sampled with replacement, so draws are independent; the finite-population
  correction is named, not applied.

## Open threads

- Checkpoint S not formally passed: part count (18, or 16 with 10 and 18 optional), survival
  placement, title, and the optional smoothing part await the owner. Parts 1 to 5 were built on the
  owner's requests (2026-10-24 to 10-29); none of the four decisions touches them.
- `data-science` category: in the validator and `frontmatter.md` since 2026-10-24, still missing
  from the live DB (the owner's write at publish).
- Sources read second-hand or as abstracts only are listed in each ledger. Project Euclid, Taylor &
  Francis and the Royal Society serve bot pages; Tilburg's repository a Cloudflare check.
- blog-forge's `subject-playbooks.md` has no statistics entry (the owner's change to make).
- Dataset choices still open: prostate versus Hedenfalk for Part 9 (licence), the heteroskedastic
  dataset for Part 14, and the `sleepstudy` source for Part 17 (`lme4` or Rdatasets).
- Available RAM has been 2 to 7 GiB (`access.md`): keep the PyMC runs in Parts 12 and 18 small.

## Next part brief

- **Part:** 6, *Confidence Intervals: What 95% Means, Measured* (`confidence-intervals-coverage`).
- **Can assume:** Part 5 by title: tests, α, power, the p-value as a random variable, TOST's 90%
  interval, and van Zwet & Cator's undercoverage after the significance filter below 50% power.
- **Must teach:** `plan.md`'s Part 6 block, as written.
- **Must not repeat:** the Fisher/Neyman–Pearson readings or the false positive risk; point to Part 5.
- **Evidence still needed:** the plan's six key sources, Neyman 1937 to Hoekstra et al. 2014.
- **Handoff:** as `plan.md` states for Part 6.
