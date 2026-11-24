
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
- **Recurring examples still to come (each confirmed with its licence at its part's research):**
  Greenwood & Yule's accidents (1, 4, 12, 16); Efron–Morris batting averages (3, 17); Pfizer–BioNTech efficacy (6,
  11, 12); NIST Longley and Filip (13); Anscombe and Duncan (14); Challenger (15);
  `MASS::ships` and `quine` (16); `sleepstudy` (17); eight schools and Minnesota radon (18).
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
- **ML-2 Classical ML.** Regularisation, cross-validation, calibration and classification metrics are
  ML-2's; it extends Part 3's MSE decomposition to prediction error.
- **ML-4 Probabilistic ML.** DS-1 uses MCMC (Metropolis by hand, NUTS as a tool read through its
  diagnostics) and hierarchical models. HMC and NUTS internals, Gibbs, variational inference, EM
  and graphical models are ML-4's.

## Part status

None is published; "ready" means built and gated.

| #  | Slug                                          | Status           | Owns                                             | Actual handoff                                                              |
| -- | --------------------------------------------- | ---------------- | ------------------------------------------------ | --------------------------------------------------------------------------- |
| 1  | distributions-as-generative-stories           | ready 2026-10-24 | which distribution, chosen from the process      | sampling to 2; MLE and the NB test to 4; counts to 16                       |
| 2  | sampling-distribution-central-limit-theorem   | ready 2026-10-26 | how a statistic varies; when the CLT fails       | estimators to 3; tests and intervals to 5, 6; skew to 7; dependence to DS-4 |
| 3  | estimator-bias-variance-mse                   | ready 2026-10-28 | what makes an estimator good; when bias pays     | likelihood to 4; the maximum to 7; pooling to 17, 18; prediction to ML-2    |
| 4  | likelihood-mle-fisher-information             | ready 2026-10-28 | MLE, information, Wald/score/LR, boundaries      | p-values to 5; coverage to 6; variance-component boundary to 17             |
| 5  | hypothesis-testing-p-values-power             | ready 2026-10-29 | what a p-value and power are; type M/S           | coverage to 6; test choice to 8; multiplicity to 9; sequential to DS-2      |
| 6  | confidence-intervals-coverage                 | ready 2026-10-31 | what 95% coverage means, measured                | skew-adapting intervals to 7; the credible interval to 11                   |
| 7  | bootstrap-confidence-intervals                | ready 2026-11-01 | intervals with no formula; where they fail       | regression bootstrap to 14; block bootstrap to DS-4; metrics to DS-2        |
| 8  | choosing-a-statistical-test                   | ready 2026-11-01 | the design picks the test; Welch by default      | rank tests to 10; regressions to 13; experiment tests to DS-2               |
| 9  | multiple-comparisons-fwer-fdr                 | ready 2026-11-23 | error across many tests, counted and uncounted   | regression to 13                                                            |
| 10 | permutation-and-rank-tests                    | ready 2026-11-23 | exact tests; what rank tests test                | randomisation inference to DS-2, DS-3; median tests named, not built        |
| 11 | bayesian-inference-conjugate-priors           | planned          | prior to posterior in closed form                | —                                                                          |
| 12 | mcmc-diagnostics-metropolis-nuts              | planned          | sampling a posterior and trusting the draws      | —                                                                          |
| 13 | linear-regression-inference                   | planned          | every number in the regression table             | —                                                                          |
| 14 | regression-diagnostics-robust-standard-errors | planned          | when to distrust the table, and the repair       | —                                                                          |
| 15 | glm-logistic-regression                       | planned          | one algorithm for every GLM; logistic read right | —                                                                          |
| 16 | count-regression-poisson-negative-binomial    | planned          | rates, exposure and overdispersion               | —                                                                          |
| 17 | linear-mixed-effects-models                   | planned          | grouped data, partial pooling, REML              | —                                                                          |
| 18 | bayesian-hierarchical-models                  | planned          | the Bayesian hierarchy and its funnel            | —                                                                          |

## Knowledge established

Durable numbers, traps and corrected claims, reused rather than re-derived.

### Parts 1–7

- **1:** Clarke 1946 (576 squares, mean 0.9323); Greenwood & Yule (647 women, mean 0.4652, variance 0.6919); NB k̂ 0.955.
  **2:** UCI spend (CC BY 4.0), γ 21.58; a one-sided 5% t at n = 30 errs 39.82%/0.05%.
- **3:** tanks (N = 342, k = 5) MSE 5,448 (MLE) against 3,303 (MVUE); James–Stein wins 96.2% of 1970 seasons. **4:** Clarke
  sizes at nλ₀ = 12.2: Wald 8.84%, LR 6.57%, score 4.26%; NB k̂ 0.865 (`method="newton"`); boundary mixture 4.40%.
- **5:** Lu–Qiu–Deng power 0.0570, type S 0.2396, exaggeration 9.537; peeking 52.99% after 1,000 looks. **6:** coverage at
  n = 20, p = 0.1: Wald 87.6%, Wilson 95.7%, Clopper–Pearson 98.9%; Pfizer VE 90.0–97.9.
- **7:** law schools (CRAN `bootstrap`, BSD-3): r 0.776, BCa 0.327–0.942; maximum 0.672 → 0.632; AR(1) SE ratio 0.574.
- **Traps:** `nct.cdf` NaN past λ ≈ 8 (use `nct.sf(c, df, -λ)`); `proportion_confint` defaults to Wald; SciPy BCa NaN on
  integer data; `boot.ci`'s acceleration is a regression.

### Part 8 — Which Statistical Test? The Design Decides, Not the Data

- **Sleep** paired p 0.002833 against 0.0792 unpaired; **PlantGrowth** F 4.846, W 5.181. Exact sizes, 10 and 40: Student
  18.25% at SD × 2, Welch 4.97–5.15%. **2 × 2** (Hellman, 20 and 22): Fisher 3.61%, Boschloo
  4.63%. **Traps:** SciPy's `ttest_ind` and `f_oneway` pool by default; `barnard_exact` drops tied tables.

### Part 9 — Multiple Comparisons: FWER, FDR, and Tests You Didn't Count

- **Hedenfalk** (3,170 genes): at 5% Bonferroni and Holm 2, BH 94, BY 0, Storey 162. **Equicorrelated, R 20,000:**
  BH FDR 0.0335, 0.0260 at ρ 0.5, with 19.8% of lists > 10% false; Storey 0.0500 → 0.2723.
  **Corrected:** "FDR 5% means 5% of my discoveries are false."

### Part 10 — Permutation and Rank Tests: What They Actually Test

- **Darwin** (1876 scans, public domain): t 2.148, p 0.0497; Fisher's count
  835 + 28 = 863 of 32,768, p 0.0527; signed-rank V⁺ 96, p 0.0413; sign 0.0074; Hodges–Lehmann 3.125 (0.5 to 5.1875,
  95.21%); Galton's re-pairing t 5.171.
- **Monte Carlo:** SciPy's default (9,999 draws) puts Darwin at p ≤ 0.05 in 19.4% of runs; b/m gives FWER 63.2% (m 999,
  1,000 tests); SciPy's two-sided p doubles the smaller tail.
- **10 and 40, R 50,000:** raw permutation 18.31% at SD × 2 (Student 18.34%), studentised 5.73%; equal sizes, one test.
- **Mann–Whitney:** equal medians (normal against Exp − ln 2, θ 0.4431) 79.7% at 400 per group; equal-centre normals 14.81%
  where Brunner–Munzel gives 5.27%. ARE 3/π, ≥ 0.864; at n = 20 the uniform loses 6.3 points, t₃ gains 10.9.
- **Law school:** Spearman exact 0.000638 (DP over 15!) against SciPy's t 0.00038, R's AS 89 0.00061. **Corrected:**
  "Mann–Whitney compares medians, so use it when the data are not normal."

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
- Numbers are rounded once from the captures, half up from the exact decimal (lab `pc()` and `hu()`, figures
  `hp()`, never `:.4f`), and rechecked by script before the gate; plain-fact claims quote the exact value.
- Assets: copy Part 8's toolchain and `lab/choosing.py` layout, or Part 9's builders; Mermaid top to bottom; one
  style per method or test. Bin a discrete estimator on its own support; write "MLE", not λ̂ (Geist Mono lacks the
  hat); `_figs.curve()` asserts no NaN.
- Literal section headings, fenced `$$` display math: Part 9's cloud build broke both; `_export.py` needs
  Playwright. Jump links use canery's `slugify` (en dashes vanish: `mannwhitney`); answers keep `<details>` and
  open with **Answer.**, which canery shows when it strips the tag.
- Social: feed cards only, no Stories (owner, 2026-10-30); `--social` then fails exactly its four
  Story checks.
- A real population is sampled with replacement; the finite-population correction is named, not
  applied.

## Open threads

- Checkpoint S still open: part count (18 or 16), survival placement, title and the optional smoothing part await
  the owner; none touches Parts 1–10.
- `data-science` category: still missing from the live DB (the owner's write at publish).
- Project Euclid, Taylor & Francis, Springer, the Royal Society and R's bug tracker refuse scripts:
  cite abstracts and say so. CASI is free from the authors.
- blog-forge's `subject-playbooks.md` has no statistics entry (the owner's change).
- Datasets still open: the heteroskedastic set for 14, the `sleepstudy` source for 17.
- Part 9: owner's R check pending; BH counts differ from the paper's.
- SciPy 1.18.1 `barnard_exact` compares |Z| without a tolerance (71 of 481 tables; no 5% decision flips); not
  reported upstream.
- Available RAM has been 2 to 7 GiB: keep Parts 12 and 18's PyMC runs small.
- `plan.md` holds the plan twice (a truncated copy in lines 1–888, uncommitted); the owner's call.

## Next part brief

- **Part:** 11, *Bayesian Inference by Hand: Priors, Conjugacy and Credible Intervals* (`bayesian-inference-conjugate-priors`).
- **Can assume:** Part 4 by title; Part 6 for coverage.
- **Must teach:** `plan.md`'s Part 11 block, as written.
- **Must not repeat:** intervals and coverage (6); MCMC (12); hierarchies (18); Bayesian A/B testing (DS-2).
- **Evidence still needed:** Laplace's Paris baptisms with source; the Pfizer protocol's prior; Jeffreys 1946, Lindley 1957.
- **Handoff:** as `plan.md` states. Part 6 promised the credible interval 90.3–97.6 from beta(0.700102, 1), adjusted for
  surveillance time: check it first.
