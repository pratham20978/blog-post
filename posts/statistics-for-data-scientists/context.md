# Series context — Statistics for Data Scientists

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** working data scientists, analysts and ML engineers who already run tests and fit
  regressions and need to know what each number guarantees and under which condition. Not
  statisticians proving new results. Expert standard; every part opens on its worked instance
  before any formula, so a reader can enter at any method.
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
    `nbinom(n=k, p=k/(k+μ))`), verified in Part 1 to 1.5 × 10⁻¹¹. Gamma as shape–rate; exponential
    as rate.
  - Software is named by exact function and pinned version (statsmodels `GLM`, R `glm`,
    `scipy.stats.bootstrap`).
- **Recurring examples (candidates, each confirmed with its licence at its part's research):**
  Clarke's V-1 counts (1, 4); Greenwood & Yule's accidents (1, 4, 12, 16); the German tank problem
  (3, 7); Efron–Morris batting averages (3, 17); R's `sleep` (2, 8); Pfizer–BioNTech efficacy (6,
  11, 12); the law-school data (7); Darwin's *Zea mays* (10); NIST Longley and Filip (13);
  Anscombe and Duncan (14); Challenger (15); `MASS::ships` and `quine` (16); `sleepstudy` (17);
  eight schools and Minnesota radon (18).
- **Lab:** G1 throughout, no access requests (see `access.md`). Pattern: by hand → matched to the
  library and R → guarantee measured with MCSE → real data with provenance.

## The data-science category boundary (keep this)

DS-1 owns the inferential core; the siblings apply it. Each seam names the owner of the mechanism.

- **DS-2 Experimentation.** DS-1 teaches p-values, power, effect sizes, intervals, multiplicity,
  the delta method as a general tool (Part 4) and cluster-robust standard errors (Part 17). DS-2
  owns design, randomisation units, MDE planning, CUPED, ratio metrics, sequential and
  always-valid tests, SRM and A/A tests, interference and bandits. DS-1 shows optional stopping
  once (Part 5) and hands it off.
- **DS-3 Causal Inference.** DS-1 reads coefficients as conditional associations and states the
  omitted-variable bias (Part 13). Identification strategies belong to DS-3.
- **DS-4 Time Series.** DS-1 assumes independence outside grouped data. It names autocorrelated
  errors (Part 14) and the block bootstrap (Part 7) and stops.
- **DS-5 Data Wrangling.** Missing-data mechanisms, imputation, outliers and selection bias are
  DS-5's. DS-1 states the complete-case, independent-sampling condition it relies on.
- **DS-6 Visualization.** DS-1 produces intervals and diagnostic plots; communicating them to an
  audience is DS-6's.
- **DS-7 Product Analytics.** Survival analysis (pending the owner's decision), metric design and
  Simpson's paradox in metric moves are DS-7's.
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
| 3 | estimator-bias-variance-mse | planned | what makes an estimator good | — |
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
  229/211/93/35/7/1, mean 0.9323, variance 0.9711 (n − 1), χ² 1.17. Greenwood & Yule 1920, 647 women,
  447/132/42/21/3/2, mean 0.4652, variance 0.6919. Bortkiewicz 1898, all 280 corps-years (mean 0.70,
  variance 0.763). `boot::coal`, 191 explosions.
- **NB by moments:** k̂ = 0.955; χ² 103.1 (Poisson) against 4.20 (NB); variance 0.692 = 0.465 Poisson
  noise + 0.227 spread of rates. Part 4 refits by ML.
- **Proneness against contagion:** a Pólya process gives the same one-period NB; the second-period
  mean is 0.692 against 0.465.
- **Tails:** unit-variance t₅ against the normal beyond 4, ×56.4; peaks 0.490 and 0.399.
- **Corrected:** a straight log–log line is not a power law (lognormal σ = 2.5, top 10% of 10,000:
  R² ≥ 0.98 in 91.4% of R = 1,000).

### Part 2 — The Sampling Distribution

- **Data** (in its `lab/data/`): UCI Online Retail (CC BY 4.0), net spend of 4,317 customers: mean
  £1,925.71, median £658.26, σ £8,266.70 (divisor N), γ 21.58; the top 1% (43) hold 29.7%.
  Student's ten patients equal R's `sleep`: t 4.0621.
- **Core** (R = 100,000): one-sided 5% t-test, lower/upper tail: n = 30, 39.82% / 0.05%; n = 1,000,
  17.69 / 0.94; n = 10,000, 7.86 / 2.99. Samples of 30 without a top-1% customer (74.1%) reject
  53.7%; corr(x̄, s) 0.972; s < σ in 88.1%, though s² is unbiased.
- **Pace:** lower tail ≈ 5% + 11.02 points × γ/√n (first-order Edgeworth), so ±10% of 5% needs
  n ≥ 486γ². At n = 30: exponential 9.84/2.26, standard lognormal 15.44/0.98.
- **Berry–Esseen:** C₀ ≤ 0.469 (Shevtsova 2013). The exact Kolmogorov distance (Gil-Pelaez
  inversion) reaches 0.01 at n = 20,652 for spend; the bound guarantees it from 1,025,322.
- **Infinite variance:** a Cauchy mean's IQR is 2.00 at every n. Pareto, tail index 1.5 (NumPy Lomax
  + 1): lower tail flat at 26.4% from n = 10⁴ to 10⁵.
- **Published rates:** Wilcox & Rousselet's lognormal 0.111 at n = 30 (R = 5,000) sits 1.3 MCSEs
  from a truth of 0.1170 ± 0.0002.
- **Corrected:** "the CLT kicks in at n = 30". Needed n grows like γ²; Student's t corrects for the
  estimated σ, not for skew.

## Decisions to preserve

- Every part follows the four-point angle (reconcile, condition, measure, read the output) and
  corrects one circulating claim, or says which point it omits and why.
- Every simulated number ships with its seed, replication count and MCSE; streams are
  `SeedSequence([stage, sub, seed])` and R comes from a target MCSE, R = p(1 − p)/MCSE². Two
  budgets are captured, the reader's `--quick` and the full one; the article quotes the full budget.
  A noisy comparison is measured at full budget before any narrative or figure rests on it, and an
  E4 fault is checked on the `--quick` budget, where it must still fail.
- Python is the lab language. R ships as an optional `crosscheck.R` only in Parts 7, 13, 15, 16 and
  17, where an R function is the field's reference; elsewhere it is the author's private check,
  with its output in the captures.
- Data ship as small CSVs with a provenance header (source, citation, licence), or are fetched from
  the public source with a checksum. Simulated data are always labelled simulated.
- Results are stated with their conditions; proof sketches are labelled as sketches.
- Earlier parts are named by title in plain text, live or not, and listed in each manifest; the
  owner adds links. Later parts are "later in this series", with no number or title.
- Prose and social-card numbers are rounded once from the captures and rechecked by script before
  the gate. Plain-fact claims quote the exact value where one exists.
- Versions are pinned per part at research; the resolver's scoping list is in `access.md`.
- Assets: copy Part 2's `assets/_build.py`, `_figs.py`, `_social.py`, `_cover.py` and `_overlap.py`,
  and Part 1's `_mermaid.py` for diagrams; labs follow Part 2's staged `lab/sampling.py`.
- A real population is sampled with replacement, so draws are independent; the finite-population
  correction is named, not applied.

## Open threads

- Checkpoint S not formally passed: part count (18, or 16 with 10 and 18 optional), survival
  placement, title, and the optional smoothing part await the owner. Parts 1 and 2 were built on the
  owner's build requests of 2026-10-24 and 2026-10-26; none of the four decisions touches them.
- `data-science` category: added to the validator's `CATEGORIES` and `frontmatter.md` on
  2026-10-24 (blog-forge tests pass). Still missing from the live DB: a production write at
  publish, the owner's.
- Read second-hand in Part 1: Greenwood & Yule's table (two printed reproductions agree; the 301
  accidents check), Shaw & Shaw (abstract only). In Part 2: Berry 1941 and Cushny & Peebles 1905 (not
  read), five papers from abstracts (its ledger). Verify against the originals given access.
- blog-forge's `subject-playbooks.md` has no statistics entry; parts use the Theory and Machine
  learning entries plus this file. Adding one is the owner's blog-forge change.
- Dataset choices still open: prostate versus Hedenfalk for Part 9 (licence), the heteroskedastic
  dataset for Part 14, and the `sleepstudy` source for Part 17 (`lme4` or Rdatasets).
- Available RAM has been 3 to 6 GiB (`access.md`): keep the PyMC runs in Parts 12 and 18 small.

## Next part brief

- **Part:** 3, *Estimators and Their Errors: Bias, Variance, and Why the Best One Can Be Biased*
  (`estimator-bias-variance-mse`).
- **Can assume:** Parts 1 and 2, named by title: the sampling distribution, the standard error, MCSE,
  seeded streams, the n − 1 divisor, and Part 2's finding that s runs small on skewed data although
  s² is unbiased.
- **Must teach:** `plan.md`'s Part 3 block, as written: both German-tank estimators' sampling
  distributions and MSEs with MCSE are the core.
- **Must not repeat:** the CLT's pace, Berry–Esseen, the SD–SE distinction, the t-test's tail errors.
  Point to Part 2 by title instead.
- **Evidence still needed:** Ruggles & Brodie 1947; Goodman 1954; Efron & Morris 1975 and the
  provenance of its 18-player table; James & Stein 1961.
- **Handoff:** the MLE recipe and its variance to 4; the bootstrap on the maximum to 7; shrinkage as
  partial pooling to 17 and 18; prediction error to ML-2.
