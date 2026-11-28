
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
  11, 12); Anscombe and Duncan (14); Challenger (15);
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
| 11 | bayesian-inference-conjugate-priors           | ready 2026-11-25 | prior to posterior in closed form                | MCMC to 12; hierarchies to 18; machinery to ML-4; Bayesian A/B to DS-2     |
| 12 | mcmc-diagnostics-metropolis-nuts              | ready 2026-11-27 | sampling a posterior and trusting the draws      | divergences and funnels to 18; NUTS internals, Gibbs, VI to ML-4           |
| 13 | linear-regression-inference                   | ready 2026-11-28 | every number in the regression table             | robust SEs, normality tests to 14; causal to DS-3; dependent errors to DS-4  |
| 14 | regression-diagnostics-robust-standard-errors | planned          | when to distrust the table, and the repair       | —                                                                          |
| 15 | glm-logistic-regression                       | planned          | one algorithm for every GLM; logistic read right | —                                                                          |
| 16 | count-regression-poisson-negative-binomial    | planned          | rates, exposure and overdispersion               | —                                                                          |
| 17 | linear-mixed-effects-models                   | planned          | grouped data, partial pooling, REML              | —                                                                          |
| 18 | bayesian-hierarchical-models                  | planned          | the Bayesian hierarchy and its funnel            | —                                                                          |

## Knowledge established

Durable numbers, traps and corrected claims, reused rather than re-derived.

### Parts 1–12

- **1–4:** Clarke 1946 (576 squares, mean 0.9323); Greenwood & Yule (647 women, mean 0.4652); tanks MSE 5,448 against
  3,303; Clarke Wald/LR/score sizes 8.84/6.57/4.26%; NB k̂ 0.865 (`method="newton"`). **5–7:** Lu–Qiu–Deng power 0.0570,
  exaggeration 9.537; coverage at n = 20, p = 0.1: Wald 87.6%, Clopper–Pearson 98.9%; Pfizer CI 90.0–97.9; law school
  BCa 0.327–0.942.
- **8–10:** sleep paired p 0.002833; Student 18.25% at SD × 2 (10 and 40); Hedenfalk BH 94; Darwin exact p 0.0527,
  t 0.0497; Mann–Whitney 79.7% at equal medians; Spearman exact 0.000638. Corrected: FDR as "5% of my discoveries",
  Mann–Whitney as a median test.
- **11–12:** Laplace's 1781 tail 1.1461 × 10⁻⁴²; trial beta(8.700102, 163) → VE 90.317–97.617; Metropolis → VE
  90.474–97.519, ESS 4,032; mean ± 1.96 SE covers 65.1% naive, 94.9% with SD/√ESS; split R̂ reaches 1.1 only at a
  0.99-SD shift. Corrected: "a flat prior is objective", "R̂ below 1.1 means converged".
- **Traps:** `nct.cdf` NaN past λ ≈ 8; `proportion_confint` defaults to Wald; SciPy BCa NaN on integer data; `ttest_ind`
  pools; `barnard_exact` drops ties; `permutation_test` draws 9,999 by default; SciPy `gamma` takes `scale=1/rate`;
  ArviZ 1.3 tail ESS on xarray uses 11%/89%; PyMC `alpha` is k; set `PYTENSOR_FLAGS` before import.

### Part 13 — Linear Regression by Hand: Every Number in the Summary

- **Checks:** exact rationals reproduce all 121 NIST certified values. Worst-coefficient digits: Longley QR 10.92,
  normal equations 7.38; Filip 8.55 and 0. The column-scaled κ predicts the loss; centring cuts Longley's κ, never a
  VIF (GNP 1,788.5). Matches statsmodels to 5.6 × 10⁻¹², R to 1.2 × 10⁻¹¹. Sleep t 1.861 (dummy), 4.062 (with
  patients); dropping Year turns GNP's −0.0358 into +0.0720.
- **Measured:** the slope's CI covers 93.4–95.4% under skewed predictors or errors, n = 5 to 1,000; unequal variance
  82.9%, dependent errors 59.0%. Skewed errors leave PI tails wrong at any n; a CI used as a PI covers 34.1%.
- **Traps:** on Filip every default keeps no digit: NumPy ≥ 2.0 `lstsq` (`rcond=-1` fixes), statsmodels `pinv` (warns;
  `method="qr"`), R `lm` tol 1e-7 drops x¹⁰. AIC counts p in statsmodels, p + 1 in R; statsmodels adds no intercept.
  NIST answers 403 to Python-urllib's User-Agent. Strided arrays change BLAS last bits. Six-digit captures
  double-round (R̂, AIC, TSS): store what the prose quotes at full precision. Corrected: "regression needs normally
  distributed variables".

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
  style per method or test. Bin a discrete estimator on its own support; no hats in figures (Geist Mono drops the
  combining mark: write "MLE", "residual SD"); `_figs.curve()` asserts no NaN.
- Literal section headings, fenced `$$` display math: Part 9's cloud build broke both; `_export.py` needs
  Playwright. Jump links use canery's `slugify` (en dashes vanish: `mannwhitney`); answers keep `<details>` and
  open with **Answer.**, which canery shows when it strips the tag.
- Social: feed cards only, no Stories (owner, 2026-10-30); `--social` then fails exactly its four
  Story checks.
- A real population is sampled with replacement; the finite-population correction is named, not
  applied.

## Open threads

- Checkpoint S still open: part count (18 or 16), survival placement, title and the optional smoothing part await
  the owner; none touches a built part.
- `data-science` category: still missing from the live DB (the owner's write at publish).
- Project Euclid, Taylor & Francis, Springer, the Royal Society and R's bug tracker refuse scripts: cite abstracts.
- blog-forge's `subject-playbooks.md` has no statistics entry (the owner's change).
- Datasets still open: the heteroskedastic set for 14, the `sleepstudy` source for 17.
- Part 9: owner's R check pending; BH counts differ from the paper's.
- SciPy's `barnard_exact` tie bug (no 5% decision flips) is not reported upstream.
- Part 11: protocol Table 8's >0.999 at VE 70% is 0.994; the FDA briefing's 99.5% threshold is 98.6%. Not reported.
- `plan.md` holds the plan twice (a truncated copy in lines 1–888, uncommitted); the owner's call.

## Next part brief

- **Part:** 14, *Regression Diagnostics: Residuals, Leverage, Influence and Robust Standard Errors*
  (`regression-diagnostics-robust-standard-errors`).
- **Can assume:** Part 13 by its title, *Linear Regression by Hand: Every Number in the Summary*: SEs from
  σ̂²(XᵀX)⁻¹ with n − p, QR, Frisch–Waugh–Lovell, VIF, a new point's leverage, and its coverage sweep (82.9% under
  unequal variance is the failure 14 repairs).
- **Must teach:** `plan.md`'s Part 14 block, as written.
- **Must not repeat:** the summary rebuild, solver digits, collinearity or the normality sweep; cite Part 13's numbers.
- **Evidence still needed:** Anscombe 1973; Duncan's data source and licence; the heteroskedastic dataset; White 1980,
  MacKinnon–White 1985, Long–Ervin 2000. R `influence.measures` is a private check (no `crosscheck.R` in 14).
- **Handoff:** as `plan.md` states.
