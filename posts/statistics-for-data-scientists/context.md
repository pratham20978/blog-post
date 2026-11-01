# Series context — Statistics for Data Scientists

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** working data scientists, analysts and ML engineers who run tests and fit regressions
  and need to know what each number guarantees, and when. Expert standard; every part opens on its
  worked instance before any formula.
- **Shape:** hybrid, seven arcs, one parent per part (`plan.md`).
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

None is published; "ready" means built and gated.

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | distributions-as-generative-stories | ready 2026-10-24 | which distribution, chosen from the process | sampling to 2; MLE and the NB test to 4; counts to 16 |
| 2 | sampling-distribution-central-limit-theorem | ready 2026-10-26 | how a statistic varies; when the CLT fails | estimators to 3; tests and intervals to 5, 6; skew to 7; dependence to DS-4 |
| 3 | estimator-bias-variance-mse | ready 2026-10-28 | what makes an estimator good; when bias pays | likelihood to 4; the maximum to 7; pooling to 17, 18; prediction to ML-2 |
| 4 | likelihood-mle-fisher-information | ready 2026-10-28 | MLE, information, Wald/score/LR, boundaries | p-values to 5; coverage to 6; variance-component boundary to 17 |
| 5 | hypothesis-testing-p-values-power | ready 2026-10-29 | what a p-value and power are; type M/S | coverage to 6; test choice to 8; multiplicity to 9; sequential to DS-2 |
| 6 | confidence-intervals-coverage | ready 2026-10-31 | what 95% coverage means, measured | skew-adapting intervals to 7; the credible interval to 11 |
| 7 | bootstrap-confidence-intervals | ready 2026-11-01 | intervals with no formula; where they fail | regression bootstrap to 14; block bootstrap to DS-4; metrics to DS-2 |
| 8 | choosing-a-statistical-test | ready 2026-11-01 | the design picks the test; Welch by default | rank tests to 10; regressions to 13; experiment tests to DS-2 |
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

At most eight durable bullets per completed part (numbers, tolerances, broken conditions, corrected
claims, terms), reused rather than re-derived.

### Part 1 — Distributions as Generative Stories

- Clarke 1946 (576 squares, mean 0.9323); Greenwood & Yule 1920 (647 women, mean 0.4652, variance
  0.6919); NB by moments k̂ 0.955; a straight log–log line is not a power law.

### Part 2 — The Sampling Distribution

- UCI spend, 4,317 customers (CC BY 4.0), γ 21.58; Student's patients are R's `sleep`. A one-sided 5%
  t-test at n = 30 errs 39.82%/0.05%; the n needed grows like γ².

### Part 3 — Estimators and Their Errors

- **Tanks** (N = 342, k = 5): MSE 5,448 (MLE m), 3,303 (MVUE). **1970 batting:** James–Stein wins
  96.2% of replayed seasons. **Corrected:** "unbiased estimators are the best ones".

### Part 4 — Likelihood: The MLE, Three Tests, and Where χ² Fails

- **Clarke:** exact sizes at nλ₀ = 12.2: Wald 8.84%, LR 6.57%, score 4.26%. **NB by ML:** k̂ 0.865
  (statsmodels `method="newton"`). **Boundary:** the 50:50 mixture's 2.71 rejects 4.40%.

### Part 5 — p-Values and Power: How Wrong Can a Significant Result Be?

- Lu–Qiu–Deng: power 0.0570, type S 0.2396, exaggeration 9.537; false positive risk 16.7% at p = .03 and
  even odds; peeking 52.99% after 1,000 looks. **Trap:** `nct.cdf` is NaN past λ ≈ 8; use `nct.sf(c, df, -λ)`.

### Part 6 — Confidence Intervals: What 95% Means, Measured

- Exact coverage at n = 20, p = 0.1: Wald 87.6%, Wilson 95.7%, Clopper–Pearson 98.9%; Pfizer VE 90.0–97.9;
  non-overlap tests at 0.0056; spend t-interval 65.83% at n = 30. **Trap:** `proportion_confint` defaults to Wald.

### Part 7 — The Bootstrap: From Percentile to BCa, and Where It Breaks

- **Law schools** (CRAN `bootstrap` 2019.6, BSD-3): r 0.776, ρ 0.760; SE 0.135 (true 0.130); BCa 0.327–0.942.
  Coverage at n = 15: percentile 91.0%, BCa 92.0%, basic 80.7%; spend at n = 30, BCa 73.3%.
- **Failures:** maximum point mass 0.672 → 0.632; AR(1) SE ratio 0.574. **Traps:** SciPy's z0 is mid-rank and its BCa
  gives NaN on integer data; `boot.ci`'s acceleration is a regression. **Corrected:** "the bootstrap is assumption-free."

### Part 8 — Which Statistical Test? The Design Decides, Not the Data

- **Sleep** (Part 2 did the paired t): paired p 0.002833 against 0.0792 unpaired; r 0.795, Var(d) 1.513.
  **PlantGrowth** (R datasets, GPL): F 4.846, W 5.181 on 17.13 df.
- **Exact sizes** by quadrature, n 10 and 40: Student 18.25% at SD × 2, 29.37% at × 4; Welch 4.97–5.15%, costing 4.4
  points of power there and 0.08 balanced. **Pre-testing:** Levene decides 9.74% at ratio 1.5 (Welch 5.07%).
- **2 × 2** (Hellman via Yates 1934, 20 and 22): largest sizes Fisher 3.61%, Boschloo 4.63%, mid-p 5.14%; Boschloo
  contains Irwin's-rule Fisher at 20 and 22, not at 10 and 40. **Traps:** SciPy's `ttest_ind` and `f_oneway` pool by
  default; `barnard_exact` drops exactly tied tables. **Corrected:** "check the assumptions first."

## Decisions to preserve

- Every part follows the four-point angle (reconcile, condition, measure, read the output) and
  corrects one circulating claim, or says which point it omits and why.
- Streams are `SeedSequence([stage, sub, seed])`; R from a target MCSE. Finite outcome spaces, and normal-theory
  error rates by quadrature, are computed exactly with one simulated check. The article quotes the full
  budget; an E4 fault must still fail on `--quick`.
- Python is the lab language, versions pinned per part. R ships as an optional `crosscheck.R` only
  in Parts 7, 13, 15, 16 and 17; elsewhere it is the author's private check, output in the captures.
- Data ship as small CSVs with a provenance header (source, citation, licence), or are fetched with
  a checksum; simulated data are labelled. A CSV reused from an earlier part ships byte-identical
  under one added `#` line naming that part's lab.
- Results are stated with their conditions; proof sketches are labelled as sketches.
- Earlier parts are named by title in plain text, live or not, and listed in each manifest; the
  owner adds links. Later parts are "later in this series", with no number or title.
- Numbers are rounded once from the captures, half up from the exact decimal (lab `pc()`, figures
  `hp()`), and rechecked by script before the gate; plain-fact claims quote the exact value.
- Assets: copy Part 8's toolchain (`_build.py`, `_figs.py`, `_social.py`, `_cover.py`, `_overlap.py`, `_mermaid.py`,
  Mermaid laid out top to bottom) and its `lab/choosing.py` layout; one style per method or test. Bin a discrete
  estimator on its own support; write "MLE", not λ̂ (Geist Mono lacks the hat); `_figs.curve()` asserts no NaN.
- Social: feed cards only, no Stories (owner, 2026-10-30); `--social` then fails exactly its four
  Story checks.
- A real population is sampled with replacement; the finite-population correction is named, not
  applied.

## Open threads

- Checkpoint S not formally passed: part count (18, or 16 with 10 and 18 optional), survival
  placement, title and the optional smoothing part await the owner; Parts 1 to 8 were built on
  request (2026-10-24 to 11-01) and none of the four touches them.
- Part 6 promises Part 11 the trial's credible interval, 90.3–97.6, from its prior beta(0.700102, 1)
  adjusted for surveillance time.
- `data-science` category: still missing from the live DB (the owner's write at publish).
- Project Euclid, Taylor & Francis, Springer, the Royal Society and R's bug tracker refuse scripts:
  cite abstracts and say so. CASI is free from the authors; Rothamsted hosts Yates's papers.
- blog-forge's `subject-playbooks.md` has no statistics entry (the owner's change).
- Datasets still open: prostate or Hedenfalk for Part 9 (licence), the heteroskedastic set for 14,
  the `sleepstudy` source for 17.
- SciPy 1.18.1 `barnard_exact` compares |Z| without a tolerance (71 of 481 tables off; no 5% decision flips at 20
  and 22); not reported upstream.
- Available RAM has been 2 to 7 GiB: keep Parts 12 and 18's PyMC runs small.

## Next part brief

- **Part:** 9, *Multiple Comparisons: FWER, FDR, and the Tests You Didn't Count* (`multiple-comparisons-fwer-fdr`).
- **Can assume:** Part 5 by title (type I error, α).
- **Must teach:** `plan.md`'s Part 9 block, as written.
- **Must not repeat:** p-values and power (5); test choice and pre-testing (8); rank tests are 10's.
- **Evidence still needed:** the dataset by licence (Efron's prostate data or Hedenfalk), the plan's key sources, and
  every number in its worked example recomputed.
- **Handoff:** as `plan.md` states for Part 9.
