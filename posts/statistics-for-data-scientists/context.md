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

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | distributions-as-generative-stories | ready 2026-10-24, not published | which distribution, chosen from the process | sampling to 2; MLE, the Poisson-vs-NB test and CSN fitting to 4; count regression to 16 |
| 2 | sampling-distribution-central-limit-theorem | ready 2026-10-26, not published | how a statistic varies; when the CLT fails | estimator quality to 3; tests and intervals to 5 and 6; skewness-corrected intervals to 7; dependent data to DS-4 |
| 3 | estimator-bias-variance-mse | ready 2026-10-28, not published | what makes an estimator good; when bias pays | likelihood to 4; bootstrap on the maximum to 7; partial pooling to 17 and 18; prediction error to ML-2 |
| 4 | likelihood-mle-fisher-information | ready 2026-10-28, not published | MLE, information, Wald/score/LR, boundaries | p-values to 5; coverage to 6; variance-component boundary to 17; Bayes (11) and Fisher scoring (15) not previewed |
| 5 | hypothesis-testing-p-values-power | ready 2026-10-29, not published | what a p-value and power are; type M/S | coverage to 6; test choice to 8; multiplicity to 9; sequential designs to DS-2 |
| 6 | confidence-intervals-coverage | ready 2026-10-31, not published | what 95% coverage means, measured | skew-adapting intervals to 7; the trial's credible interval to 11; DS-6 not previewed |
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

At most eight durable bullets per completed part (numbers, tolerances, broken conditions, corrected
claims, terms), reused rather than re-derived.

### Part 1 — Distributions as Generative Stories

- **Data** (CSVs with provenance): Clarke 1946, 537 bombs on 576 squares, mean 0.9323; Greenwood &
  Yule 1920, 647 women, mean 0.4652, variance 0.6919; Bortkiewicz's corps.
- **NB by moments:** k̂ = 0.955. **Tails:** a straight log–log line is not a power law.

### Part 2 — The Sampling Distribution

- **Data:** UCI Online Retail spend of 4,317 customers (CC BY 4.0), γ 21.58; Student's ten patients
  equal R's `sleep`.
- **Core:** one-sided 5% t-test at n = 30 errs 39.82%/0.05% (lower/upper); needed n grows like γ²
  ("the CLT kicks in at n = 30" corrected).

### Part 3 — Estimators and Their Errors

- **Tanks** (N = 342, k = 5): MSE 5,448 (MLE m), 3,303 (MVUE). **1970 batting:** James–Stein wins
  96.2% of replayed seasons. **Corrected:** "unbiased estimators are the best ones".

### Part 4 — Likelihood: The MLE, Three Tests, and Where χ² Fails

- **Poisson (Clarke):** SE 0.0402; exact sizes at nλ₀ = 12.2: Wald 8.84%, LR 6.57%, score 4.26%.
- **NB by ML** (Greenwood–Yule): k̂ 0.865; statsmodels needs `method="newton"`.
- **Boundary:** χ²₁ rejects 2.17%, the 50:50 mixture's 2.71 rejects 4.40%. **Corrected:** "the LR
  statistic is χ²": only for an interior null.

### Part 5 — p-Values and Power: How Wrong Can a Significant Result Be?

- **Data:** Durante et al. 2013 via Gelman & Carlin; OSC 2015's `rpp_data.csv` (OSF fgjvw, CC0 1.0).
- **Design analysis** (Lu–Qiu–Deng): power 0.0570, type S 0.2396, exaggeration 9.537. **Power:** 16
  per group at d = 1 is 0.781398 in four tools.
- **False positive risk** (not FDR, Part 9's): p = .03 gives 16.7% at even odds, 64.3% at prior 0.1.
  **Peeking:** 52.99% after 1,000 looks.
- **Tool trap:** SciPy 1.18.1 `nct.cdf(-c, df, λ)` returns NaN past λ ≈ 8; use `nct.sf(c, df, -λ)`.
- **Corrected:** "p = 0.03 means a 3% chance of a fluke" (true only at a prior of 0.87).

### Part 6 — Confidence Intervals: What 95% Means, Measured

- **Exact coverage** at n = 20, p = 0.1: Wald 87.6%, Wilson 95.7%, Clopper–Pearson 98.9%; at n = 50
  Wald is under 93% for 40% of p.
- **Pfizer–BioNTech** (8 of 170): Clopper–Pearson gives VE 90.0–97.9, Table 3 to the digit; all 16
  printed rows reproduce within rounding.
- **Overlap:** non-overlap of two 95% intervals tests at 0.0056 (equal SEs); 83.4% intervals give 5%.
- **t-interval, Part 2's spend:** 65.83% ± 0.11 at n = 30, 93.84% at 10,000; 0% to 100% across width
  deciles at n = 30.
- **Tool traps:** statsmodels 0.15.0 `proportion_confint` defaults to Wald; SciPy's and R's exact
  two-sided p is minlike and does not invert to their Clopper–Pearson interval.
- **Corrected:** "There is a 95% probability the true value is inside this interval."

## Decisions to preserve

- Every part follows the four-point angle (reconcile, condition, measure, read the output) and
  corrects one circulating claim, or says which point it omits and why.
- Seeded streams are `SeedSequence([stage, sub, seed])`; R = p(1 − p)/MCSE² from a target MCSE. Finite
  outcome spaces are summed exactly, with one simulated check. Two budgets, `--quick` and full: the
  article quotes full, a noisy comparison is settled at full budget before a figure rests on it,
  and an E4 fault must still fail on `--quick`.
- Python is the lab language, versions pinned per part. R ships as an optional `crosscheck.R` only
  in Parts 7, 13, 15, 16 and 17; elsewhere it is the author's private check, output in the captures.
- Data ship as small CSVs with a provenance header (source, citation, licence), or are fetched with
  a checksum; simulated data are labelled. A CSV reused from an earlier part ships byte-identical
  under one added `#` line naming that part's lab.
- Results are stated with their conditions; proof sketches are labelled as sketches.
- Earlier parts are named by title in plain text, live or not, and listed in each manifest; the
  owner adds links. Later parts are "later in this series", with no number or title.
- Prose and card numbers are rounded once from the captures and rechecked by script before the
  gate; plain-fact claims quote the exact value.
- Assets: copy Part 6's toolchain (`_build.py`, `_figs.py`, `_social.py`, `_cover.py`,
  `_overlap.py`), Part 1's `_mermaid.py` and Part 6's `lab/intervals.py` layout; keep
  `_figs.STYLE`, one style per interval method. Bin a discrete estimator's histogram on its own
  support; write "MLE", not λ̂ (Geist Mono lacks the hat); `_figs.curve()` asserts no NaN, which
  the browser silently drops.
- Social: feed cards only, no Stories (owner, 2026-10-30); `--social` then fails exactly its four
  Story checks.
- A real population is sampled with replacement; the finite-population correction is named, not
  applied.

## Open threads

- Checkpoint S not formally passed: part count (18, or 16 with 10 and 18 optional), survival
  placement, title and the optional smoothing part await the owner; Parts 1 to 6 were built on
  request (2026-10-24 to 10-31) and none of the four touches them.
- Part 6 promises two later parts: intervals that adapt to skew (7), and the trial's credible
  interval, 90.3–97.6, rebuilt from its prior beta(0.700102, 1) adjusted for surveillance time (11).
- `data-science` category: still missing from the live DB (the owner's write at publish).
- Ledgers list second-hand and abstract-only sources. Project Euclid, Taylor & Francis, the Royal
  Society and Penn's, Groningen's and Cardiff's repositories refuse scripts; Tilburg's shows a
  Cloudflare check.
- blog-forge's `subject-playbooks.md` has no statistics entry (the owner's change).
- Datasets still open: prostate or Hedenfalk for Part 9 (licence), the heteroskedastic set for 14,
  the `sleepstudy` source for 17.
- Available RAM has been 2 to 7 GiB: keep Parts 12 and 18's PyMC runs small. PyPI was unreachable
  on 2026-10-31; uv's `--offline` cache sufficed (`access.md`).

## Next part brief

- **Part:** 7, *The Bootstrap: From Percentile to BCa, and Where It Breaks* (`bootstrap-confidence-intervals`).
- **Can assume:** Part 6 by title (coverage belongs to the procedure; actual coverage, confidence
  coefficient, test inversion, relevant subsets); Part 3 by title for the sample maximum.
- **Must teach:** `plan.md`'s Part 7 block, as written.
- **Must not repeat:** what 95% means or the binomial intervals; point to Part 6.
- **Evidence still needed:** the plan's six key sources; the 82-school population's provenance and
  licence; BCa's coverage on the spend population at n = 30 against the t-interval's 65.83%, which
  keeps Part 6's promise.
- **Handoff:** as `plan.md` states for Part 7.
