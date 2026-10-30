# Series plan — Statistics for Data Scientists

**Slug:** statistics-for-data-scientists · **Shape:** hybrid · **Parts:** 18 ·
**Category:** `data-science` for every part · **Map code:** DS-1, the entry series of the category ·
**Status:** Checkpoint S — awaiting approval (planned 2026-10-23)
**Display title (platform):** *Statistics for Data Scientists: Every Guarantee, Measured*

## Why this is a series and not one post

The reader objective is to *use statistical inference correctly and know the condition each answer
rests on*, and it splits at hard prerequisite seams. No interval or test can be explained until the
reader accepts that a statistic has a sampling distribution. A GLM cannot be fitted until both the
linear model and the likelihood exist. A hierarchical model needs regression, and its Bayesian form
needs a sampler the reader can trust. Budgeted as one article, the 45 objectives below come to
roughly 139,000 words and 216 figures, in eighteen prerequisite-separated groups, each with its own
worked example and its own search audience ("what is a p-value", "BCa bootstrap interval",
"negative binomial vs Poisson", "lme4 random slopes" are four different readers). That is a series
by every one of the skill's three tests.

This is **DS-1**. Every other data-science series assumes it (DS-2 to DS-7), as do ML-2 (Classical
ML) and ML-4 (Probabilistic ML). Its job is the inferential core: distributions, estimation,
likelihood, tests and intervals, Bayesian inference, and the regression family through mixed
models. Experiments, causality, time series, wrangling, communication and product metrics each have
their own series; the seams are listed under *What this series will not cover* and kept in
`context.md`.

## The angle, and why it is not another intro-statistics course

Introductory statistics is the most saturated subject on this map. OpenIntro, Wasserman's *All of
Statistics*, Casella & Berger, Gelman, Hill & Vehtari's *Regression and Other Stories*, McElreath's
*Statistical Rethinking*, Bruce, Bruce & Gedeck's *Practical Statistics for Data Scientists* and
thousands of p-value explainers already own the definitions and the formulas. Restating them is
worthless. Each part's literature sweep must confirm the gap for its own method, but what those
sources mostly do not do *together* is the four things this series is built on:

1. **Reconcile every number three ways.** Each method is computed from first principles in NumPy,
   printing its intermediates, and matched to the reference implementation (SciPy or statsmodels,
   and R where R is the field's reference) to a stated tolerance. Wherever a *certified value* or an
   *exact closed form* exists, it is matched to that too: NIST's Statistical Reference Datasets for
   regression, the conjugate posterior for MCMC, exact binomial sums for interval coverage. This is
   the series' test vector.
2. **State the condition, then break it.** Every guarantee (95% coverage, a 5% type I error rate,
   unbiasedness, a χ² reference distribution) is stated with the condition it needs, and the lab
   violates the condition on purpose to show what the guarantee becomes.
3. **Measure the guarantee.** A frequentist guarantee is a long-run property, so the series simulates
   the long run. Every coverage, error rate and power figure is measured by Monte Carlo and reported
   with its Monte Carlo standard error (MCSE), or computed exactly when it can be.
4. **Read the output line by line.** Regression, GLM and mixed-model summary tables and MCMC
   diagnostics are decoded number by number, so the reader can recompute each one and knows which
   to distrust.

Every part does all four, or says which one it omits and why. Each part also **corrects one claim**
that circulates without its condition, listed per part as **Corrects**.

Every worked example uses **real published data** (historical tables, certified reference
datasets, the datasets R ships, public government surveys), chosen so that a result in the
literature can be reproduced: Greenwood and Yule's munition-worker accidents, the German tank
problem, Efron and Morris's batting averages, the Pfizer–BioNTech efficacy analysis, Darwin's *Zea
mays* pairs, NIST's Longley data, the Challenger launches, the eight schools. Several recur, so the
series reads as one investigation rather than eighteen unrelated exercises.

## Shape

Hybrid. A four-part ladder lays the foundations: the data-generating process, then the sampling
distribution, then estimators, then likelihood. The frequentist arc is a decomposition with two
short ladders inside it (tests → intervals → bootstrap; tests → choosing a test → nonparametric
alternatives). Bayesian inference is a two-rung ladder. Modelling is a ladder (linear → generalized
→ multilevel) whose every rung splits in two. Each part names at most one parent, and every parent
sits at a lower position, so publication order 1→18 never links backward to an unpublished part.
Dependencies: 2←1, 3←2, 4←3, 5←2, 6←5, 7←6, 8←5, 9←5, 10←8, 11←4, 12←11, 13←8, 14←13, 15←13,
16←15, 17←13, 18←17.

Re-teach or assume: inside the foundations ladder (1–4) each part restates its parent's conclusion
in one paragraph, because its reader may arrive from search. Everywhere else a part assumes its
parent and names it in plain text.

Adjacent options the owner can overrule in one word:
(a) **16 committed + 2 optional**: hold Part 10 (permutation and rank tests) and Part 18 (Bayesian
hierarchical models) as optional spokes. Nothing else in this series depends on them, but the map
card lists both, and ML-4 would then have to teach the funnel itself. Not recommended.
(b) **Split the modelling arc (13–18) into its own series.** The seam between inference and
modelling is real, but regression is the inferential workhorse every DS series assumes, so the map
keeps it here.
(c) **Fewer, longer parts.** Rejected: every candidate merge (3+4, 5+6, 13+14, 17+18) budgets
above the 10,000-word L4 ceiling.

## Arcs

| Parts  | Arc                       | Purpose                                                                                                                                  |
| ------ | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 1–4   | Foundations               | Where the numbers come from, how a statistic varies, what makes an estimator good, and the likelihood most later parts run on. A ladder. |
| 5–7   | Tests and intervals       | What a p-value and power are, what 95% coverage means, and the bootstrap for when no formula exists. A ladder.                           |
| 8–10  | Choosing a method         | Picking a test from the design, controlling error across many tests, and the permutation and rank methods. Spokes from Part 5.           |
| 11–12 | Bayesian inference        | Priors and posteriors in closed form, then a sampler and the diagnostics that say when to trust it.                                      |
| 13–14 | The linear model          | Regression as an inferential model, every number in its output, and the diagnostics that say when to distrust them.                      |
| 15–16 | Generalized linear models | The GLM machinery and logistic regression, then counts, exposure and overdispersion.                                                     |
| 17–18 | Multilevel models         | Mixed-effects models and partial pooling, then the Bayesian hierarchical model and its geometry.                                         |

## Reading paths

- **From scratch:** 1 → 2 → 3 → 4, then 5 → 6 → 7, 8 → 9 → 10, 11 → 12, 13 → 14 → 15 → 16 → 17 → 18.
- **"I analyse experiments"** (then DS-2): 2 → 5 → 6 → 8 → 9 → 7.
- **"I fit regressions":** 2 → 4 → 13 → 14 → 15 → 16 → 17.
- **"I want to work Bayesian":** 4 → 11 → 12 → 17 → 18.
- **Before ML-2:** 3 → 4 → 13 → 15.

## Reader objectives

| #  | After this the reader can ...                                                                                                                                      | Part |
| -- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---- |
| 1  | write the generative story behind a dataset and derive the distribution family from it, not from the histogram                                                     | 1    |
| 2  | explain overdispersion as heterogeneity, by deriving the negative binomial as a gamma–Poisson mixture                                                             | 1    |
| 3  | say why a straight log–log tail is not evidence of a power law                                                                                                    | 1    |
| 4  | simulate the sampling distribution of any statistic and report every simulated rate with its Monte Carlo standard error                                            | 2    |
| 5  | judge how fast the CLT works for a given population, and recognise the infinite-variance cases where it never does                                                 | 2    |
| 6  | separate the standard error from the standard deviation, and say why Student's t replaces z when σ is estimated                                                   | 2    |
| 7  | compute an estimator's bias, variance and MSE by formula and by simulation, and choose between estimators on MSE                                                   | 3    |
| 8  | solve the German tank problem with the MLE and the minimum-variance unbiased estimator, and compare their errors                                                   | 3    |
| 9  | explain why the James–Stein estimator beats separate means in total squared error                                                                                 | 3    |
| 10 | derive an MLE and its standard error from the observed or expected Fisher information                                                                              | 4    |
| 11 | compute the Wald, score and likelihood-ratio statistics for one hypothesis, and say when they disagree                                                             | 4    |
| 12 | build a profile-likelihood interval, and use the delta method for a function of parameters                                                                         | 4    |
| 13 | say why the likelihood-ratio test's χ² reference fails on a parameter boundary, and what replaces it                                                             | 4    |
| 14 | state what a p-value is and is not, and describe its distribution under the null and under an alternative                                                          | 5    |
| 15 | compute power analytically and by simulation, and the type M and type S errors of a low-powered design                                                             | 5    |
| 16 | test for equivalence instead of reading a non-significant result as "no effect"                                                                                    | 5    |
| 17 | explain coverage as a property of a procedure, and measure an interval's actual coverage                                                                           | 6    |
| 18 | choose a binomial interval from its exact coverage curve                                                                                                           | 6    |
| 19 | read two overlapping intervals correctly                                                                                                                           | 6    |
| 20 | compute percentile, studentised and BCa bootstrap intervals by hand, including BCa's bias correction and acceleration                                              | 7    |
| 21 | say when the bootstrap fails: extremes, infinite variance and dependence                                                                                           | 7    |
| 22 | choose a test from the study design and the hypothesis rather than from how the data look                                                                          | 8    |
| 23 | say why Welch's t-test should be the default, and measure Student's t-test's error under unequal variances                                                         | 8    |
| 24 | choose between the chi-squared test, Fisher's exact test and their alternatives for a 2×2 table                                                                   | 8    |
| 25 | control the family-wise error rate (Bonferroni, Holm) or the false discovery rate (Benjamini–Hochberg, Benjamini–Yekutieli), and say which question each answers | 9    |
| 26 | find the multiplicity in a forking-paths analysis that no table of p-values shows                                                                                  | 9    |
| 27 | run an exact permutation test, state its exchangeability condition, and recognise when that fails                                                                  | 10   |
| 28 | say what the Wilcoxon and Mann–Whitney tests actually test, and estimate a Hodges–Lehmann shift                                                                  | 10   |
| 29 | update a conjugate prior by hand, report a credible interval, and say what it claims that a confidence interval does not                                           | 11   |
| 30 | reproduce a published Bayesian analysis (the Pfizer–BioNTech efficacy interval) from its stated prior                                                             | 11   |
| 31 | write a Metropolis sampler and verify it against a closed-form posterior                                                                                           | 12   |
| 32 | diagnose a chain with rank-normalised R̂, bulk and tail ESS and MCSE, and name what those diagnostics cannot see                                                  | 12   |
| 33 | recompute every number in a regression summary table from the design matrix                                                                                        | 13   |
| 34 | reproduce NIST's certified regression results, and say why the normal equations lose digits                                                                        | 13   |
| 35 | read a coefficient as a conditional association, and state the omitted-variable bias                                                                               | 13   |
| 36 | find the observations driving a fit with leverage, studentised residuals and Cook's distance                                                                       | 14   |
| 37 | repair inference under non-constant variance with HC3 standard errors, and measure the repair                                                                      | 14   |
| 38 | fit a GLM by iteratively reweighted least squares, and read its deviance, Wald and likelihood-ratio tests                                                          | 15   |
| 39 | interpret logistic coefficients as odds ratios without reading them as risk ratios, and handle separation                                                          | 15   |
| 40 | model counts with an exposure offset, diagnose overdispersion, and choose between quasi-Poisson, robust standard errors and the negative binomial                  | 16   |
| 41 | choose between zero-inflated and hurdle models from the generative story                                                                                           | 16   |
| 42 | fit a linear mixed model, explain partial pooling and REML, and test a variance component correctly                                                                | 17   |
| 43 | choose between a mixed model, cluster-robust standard errors and GEE from whether the question is conditional or marginal                                          | 17   |
| 44 | fit a Bayesian hierarchical model, diagnose divergences, and remove them with a non-centred parameterisation                                                       | 18   |
| 45 | choose a prior for a group-level standard deviation, and compare pooling structures with PSIS-LOO                                                                  | 18   |

## Parts

> Numbers quoted below are recalled from the sources for scoping. Three were re-computed on
> 2026-10-23 (the R `sleep` p-values, the Pfizer–BioNTech interval, the t₅ tail ratio). Each part's
> research re-verifies and ledgers its own numbers; none is a claim yet.

### Part 1 — Distributions as Generative Stories: Let the Process Pick the Model

- **Slug:** distributions-as-generative-stories · **Arc:** Foundations · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** Which probability distribution describes my data, and how do I choose it from the
  process that produced the numbers rather than from the shape of a histogram?
- **Assumes:** No prior part. Expectation, variance and random variables; Python with NumPy. No
  prior statistical inference.
- **Hands off:** How a statistic computed from these data varies to 2; fitting by maximum
  likelihood and the formal Poisson-versus-negative-binomial test to 4; count regression with
  covariates to 16.
- **Worked example:** Each distribution derived from a process and checked against a historical
  count table. Bernoulli trials lead to the binomial, and the binomial's rare-event limit to the
  Poisson, tested on Clarke's 1946 tally of V-1 impacts over 576 squares of south London. Waiting
  times lead to the exponential and gamma, sums of many small effects to the normal, products to
  the lognormal. Then Greenwood and Yule's 1920 munition-worker accidents, where the Poisson fails:
  give each worker an individual accident rate drawn from a gamma distribution and the counts
  follow a negative binomial with variance μ + μ²/k, so the "overdispersion" is the heterogeneity
  itself, not noise. Observed and expected counts are compared on a rootogram, with fits by
  moments only (likelihood arrives in Part 4). Last, a unit-variance Student t₅ beside the normal:
  indistinguishable in the body of a histogram, yet the probability beyond four standard deviations
  differs by a factor of about 56.
- **Corrects:** "A straight line on a log–log plot shows a power law." A lognormal sample draws a
  convincingly straight tail; Clauset, Shalizi and Newman (2009) give the procedure that actually
  decides, which Part 4's likelihood makes runnable.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Simulators for each generative story;
  the historical tables as CSVs with provenance; moment fits, rootograms and Q–Q plots; the t₅ tail
  computation; the lognormal-on-log–log demonstration.
- **Key sources (confirm at research):** Clarke 1946 (J. Inst. Actuaries); Greenwood & Yule 1920
  (JRSS); Bortkiewicz 1898; Clauset, Shalizi & Newman 2009 (SIAM Review); Kleiber & Zeileis 2016
  (The American Statistician, rootograms).
- **Search intent:** "which probability distribution should I use", "poisson vs negative binomial",
  "overdispersion explained", "lognormal vs power law"

### Part 2 — The Sampling Distribution: The CLT by Simulation, and Where n = 30 Fails

- **Slug:** sampling-distribution-central-limit-theorem · **Arc:** Foundations · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** A statistic computed from a sample is itself a random variable. What is its
  distribution, how fast does it become normal, and when does it never?
- **Assumes:** Part 1's generative stories, as the populations being sampled.
- **Hands off:** What makes one estimator better than another to 3; using the sampling distribution
  to test and to build intervals to 5 and 6; dependent data to DS-4.
- **Worked example:** A real, heavily skewed population (per-customer spend from a public
  transactions dataset, e.g. UCI Online Retail, licence settled at research) sampled at n = 10, 30,
  100 and 1,000. The sampling distribution of the mean is simulated, the standard error separated
  from the standard deviation, and the two one-sided error rates of a nominal 5% t-test measured
  with their MCSE: the skew pushes one tail over 5% and the other under. The Berry–Esseen bound is
  evaluated for this population to contrast the n at which normality is guaranteed with the n at
  which it is good enough. Infinite variance is the case that never converges: the running mean of
  a Cauchy sample, and a Pareto with tail index 1.5. Student's t is introduced where it was born,
  on Cushny and Peebles' sleep data in Student's 1908 paper (R's `sleep`), as the correction for
  estimating σ. Simulation is set up here as the series' instrument: seeds, replication counts
  chosen from a target MCSE, and the MCSE of a simulated proportion.
- **Corrects:** "The CLT kicks in at n = 30." For a skewed population the t-test's one-sided error
  rates are still visibly off at n = 30; how fast they converge depends on the skewness, not on a
  sample-size rule.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. A sampling-distribution simulator for
  any statistic; the tail-error measurement with MCSE; Berry–Esseen evaluated from the population's
  moments; the Cauchy and Pareto running means.
- **Key sources:** Student 1908 (Biometrika); Berry 1941 and Esseen 1942, with a current constant
  (Shevtsova 2011); Wilcox, *Introduction to Robust Estimation and Hypothesis Testing*; Morris,
  White & Crowther 2019 (Statistics in Medicine, simulation studies and MCSE).
- **Search intent:** "central limit theorem explained", "is n=30 enough", "standard error vs
  standard deviation", "sampling distribution of the mean"

### Part 3 — Estimators and Their Errors: Bias, Variance, and Why the Best One Can Be Biased

- **Slug:** estimator-bias-variance-mse · **Arc:** Foundations · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** What makes an estimator good, and why can a deliberately biased one beat every
  unbiased alternative?
- **Assumes:** Part 2's sampling distribution.
- **Hands off:** Maximum likelihood as a general recipe, and its asymptotic variance, to 4; the
  bootstrap's failure on the sample maximum to 7; shrinkage as partial pooling to 17 and 18;
  bias–variance in prediction error to ML-2.
- **Worked example:** The German tank problem on serial numbers. The maximum likelihood estimator
  (the sample maximum) is biased low; the minimum-variance unbiased estimator m(1 + 1/k) − 1
  corrects it. Their sampling distributions and MSEs are simulated side by side, then set against
  Ruggles and Brodie's 1947 comparison of statistical and intelligence estimates of German
  production with the postwar records. Bias, variance and MSE = bias² + variance are then worked
  on the variance estimator: dividing by n − 1 is unbiased, yet the standard deviation stays
  biased and, for normal data, dividing by n + 1 has lower MSE. Then Stein's paradox on Efron and
  Morris's 1975 batting averages (18 players after 45 at-bats): the James–Stein estimator, shrinking
  every player toward the grand mean, beats the 18 separate averages in total squared error
  against the rest of the season. Consistency versus unbiasedness, and sufficiency (Rao–Blackwell
  as how the German tank estimator is built), are named and used.
- **Corrects:** "Unbiased estimators are the best ones." Unbiasedness is one property, not a
  virtue; under squared-error loss a biased estimator often wins, and n − 1 is not the MSE-optimal
  divisor.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Both German-tank estimators simulated
  with MSE and MCSE; the n − 1, n and n + 1 divisors compared; James–Stein on the Efron–Morris table,
  reproducing their published error comparison.
- **Key sources:** Ruggles & Brodie 1947 (JASA); Goodman 1954 (JASA, serial-number estimation);
  James & Stein 1961; Efron & Morris 1975 (JASA) and 1977 (Scientific American); Lehmann & Casella,
  *Theory of Point Estimation*.
- **Search intent:** "german tank problem", "why divide by n-1", "biased vs unbiased estimator",
  "james-stein estimator", "stein's paradox"

### Part 4 — Likelihood: The MLE, Fisher Information, and the Wald, Score and Likelihood-Ratio Tests

- **Slug:** likelihood-mle-fisher-information · **Arc:** Foundations · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** How does the likelihood turn a model and data into an estimate, a standard error and
  a test, and when do its asymptotic promises fail?
- **Assumes:** Part 3's estimator properties.
- **Hands off:** Using these statistics as tests and inverting them into intervals to 5 and 6; the
  likelihood times a prior to 11; Fisher scoring as the GLM fitting algorithm to 15; the boundary
  problem for variance components to 17.
- **Worked example:** The Poisson rate of Part 1's V-1 data: log-likelihood, score, MLE, observed
  and expected information and the standard error, all by hand. On the same curve, the three ways
  to measure how far a null value sits from the MLE (horizontal distance for Wald, slope for score,
  height for the likelihood ratio) are drawn as one figure, after Buse's 1982 geometry, and
  computed: they agree asymptotically and disagree at small n. Then a two-parameter likelihood: the
  negative binomial fitted to Greenwood and Yule's accidents by maximum likelihood, its surface
  contoured, the dispersion's profile-likelihood interval shown asymmetric where the Wald interval
  is not, and the delta method used for a function of the parameters. Finally, testing Poisson
  against negative binomial puts the null on the boundary of the parameter space (no extra
  variance), where the likelihood-ratio statistic follows a 50:50 mixture of χ²₀ and χ²₁, not χ²₁,
  measured by simulation. Part 1's lognormal-versus-power-law question is settled with the
  likelihood-ratio comparison it deferred.
- **Corrects:** "The likelihood-ratio statistic is χ²-distributed." Only when the null lies inside
  the parameter space; on a boundary the reference distribution changes, and the naive p-value is
  about twice the correct one.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. Hand-coded log-likelihoods, scores and
  information for the Poisson and negative binomial, checked against `scipy.optimize` and
  statsmodels; the Wald, score and LR comparison across n; profile-likelihood intervals; the
  boundary simulation.
- **Key sources:** Fisher 1922 (Phil. Trans. A); Wilks 1938 (Ann. Math. Stat.); Buse 1982 (The
  American Statistician); Efron & Hinkley 1978 (Biometrika, observed versus expected information);
  Self & Liang 1987 (JASA, boundary asymptotics); Pawitan, *In All Likelihood*.
- **Search intent:** "maximum likelihood estimation explained", "fisher information", "wald vs
  score vs likelihood ratio test", "profile likelihood confidence interval", "delta method"

### Part 5 — Hypothesis Testing Done Right: p-Values, Power, and Type M and S Errors

- **Slug:** hypothesis-testing-p-values-power · **Arc:** Tests and intervals · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** What does a p-value measure, what does a test promise, and how wrong can a
  "significant" estimate be?
- **Assumes:** Part 2's sampling distribution and the t statistic. (Links Part 4 for the three
  test statistics.)
- **Hands off:** Inverting tests into intervals to 6; choosing among tests to 8; many tests at once
  to 9; optional stopping and sequential designs to DS-2.
- **Worked example:** The p-value treated as what it is, a random variable: its distribution
  simulated under the null (uniform) and under alternatives of increasing size, with the Fisher
  reading (evidence) and the Neyman–Pearson reading (a decision rule with α and power) kept apart.
  Power is derived for the two-sample comparison and checked by simulation. Then Gelman and
  Carlin's 2014 "retrodesign" is reproduced on a published low-powered study: given a plausible
  true effect, the power, the probability that a significant estimate has the wrong sign (type S)
  and the factor by which it exaggerates the effect (type M). That mechanism is why the Open
  Science Collaboration's 2015 replications found smaller effects. The share of p < 0.05 results
  that are false is computed as a function of power and prior odds (Ioannidis 2005, Colquhoun
  2014). Equivalence testing (two one-sided tests) is the honest way to claim "no meaningful
  effect". Optional stopping inflating α is shown in one simulation and handed to DS-2.
- **Corrects:** "p = 0.03 means a 3% chance the result is a fluke." A p-value is computed assuming
  the null is true; the chance a significant finding is false depends on power and prior odds, and
  at modest prior odds it passes 30% for results at p < 0.05.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. A p-value distribution simulator;
  analytic and simulated power curves; a `retrodesign` implementation reproducing Gelman and
  Carlin's published numbers; the false-positive-risk calculator; TOST matched to statsmodels.
- **Key sources:** Wasserstein & Lazar 2016 (ASA statement, The American Statistician); Gelman &
  Carlin 2014 (Perspectives on Psychological Science); Open Science Collaboration 2015 (Science);
  Ioannidis 2005 (PLoS Medicine); Colquhoun 2014 (Royal Society Open Science); Lakens 2017 (Social
  Psychological and Personality Science, TOST).
- **Search intent:** "what is a p-value", "p-value misconceptions", "statistical power explained",
  "type m and type s errors", "equivalence test tost"

### Part 6 — Confidence Intervals: What 95% Means, Measured

- **Slug:** confidence-intervals-coverage · **Arc:** Tests and intervals · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** What does a 95% confidence interval promise, how do I check that an interval keeps
  the promise, and which interval should I use for a proportion?
- **Assumes:** Part 5's tests: an interval is the set of null values a test does not reject.
- **Hands off:** Intervals without a formula to 7; credible intervals to 11; showing uncertainty to
  an audience to DS-6.
- **Worked example:** Coverage defined as a property of the procedure, then measured. For a
  binomial proportion the exact coverage of any interval can be summed over all outcomes, with no
  simulation: Wald, Wilson (the inverted score test), Agresti–Coull, Clopper–Pearson (inverted
  exact tests) and Jeffreys are plotted against p at fixed n, reproducing Brown, Cai and
  DasGupta's 2001 oscillation, where Wald's coverage stays erratic even at large n. Then a real
  low-count proportion: the Pfizer–BioNTech phase 3 result (8 vaccine and 162 placebo cases)
  becomes an exact conditional interval for vaccine efficacy, the frequentist number Part 11 sets
  beside the trial's published Bayesian interval. The overlap rule is tested: two 95% intervals can
  overlap substantially while their difference is significant (Schenker and Gentleman 2001).
  Finally, the t-interval's coverage on Part 2's skewed population, the case that motivates Part 7.
- **Corrects:** "There is a 95% probability the true value is inside this interval." The 95%
  belongs to the procedure across repetitions; a computed interval contains the value or it does
  not, and the statement the reader wants is a Bayesian one (Part 11).
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Exact coverage sums for five binomial
  intervals; the conditional exact interval for efficacy; the overlap demonstration; t-interval
  coverage with MCSE.
- **Key sources:** Neyman 1937 (Phil. Trans. A); Brown, Cai & DasGupta 2001 (Statistical Science);
  Agresti & Coull 1998 (The American Statistician); Schenker & Gentleman 2001 (The American
  Statistician); Polack et al. 2020 (NEJM); Hoekstra et al. 2014 (Psychonomic Bulletin & Review).
- **Search intent:** "confidence interval interpretation", "wilson vs wald interval",
  "clopper-pearson exact interval", "overlapping confidence intervals significance"

### Part 7 — The Bootstrap: From Percentile to BCa, and Where It Breaks

- **Slug:** bootstrap-confidence-intervals · **Arc:** Tests and intervals · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** How do I get a standard error or an interval for a statistic that has no formula,
  which bootstrap interval should I trust, and when does the bootstrap fail?
- **Assumes:** Part 6's coverage. (Links Part 3 for the sample maximum.)
- **Hands off:** Bootstrapping a regression (pairs versus residuals) to 14; the block bootstrap for
  dependent data to DS-4; bootstrapping experiment metrics to DS-2.
- **Worked example:** Efron's law-school data: 15 schools sampled from a published population of
  82, with the correlation of LSAT and GPA bootstrapped by hand. The percentile, basic, studentised
  and BCa intervals are computed, BCa's bias correction z₀ from the share of replicates below the
  estimate and its acceleration a from the jackknife, every intermediate printed, and checked
  against R's `boot.ci`. Because the 82-school population is published, each interval's actual
  coverage is measured by drawing fresh samples of 15 from it, beside Fisher's z-interval. Then the
  failures, each as a condition: the sample maximum (Part 3's German tank), where the bootstrap
  distribution keeps a point mass of about 1 − 1/e ≈ 0.63 at the observed maximum; infinite-variance
  data; and dependent data, where resampling single observations destroys the correlation.
- **Corrects:** "The bootstrap is assumption-free." It assumes the sample stands in for the
  population and the statistic is smooth in it; it is inconsistent for extremes and wrong for
  dependent data.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. A from-scratch bootstrap with all four
  intervals, matched to R's `boot.ci` and `scipy.stats.bootstrap`; the coverage study against the
  82-school population; the maximum and heavy-tail failure demonstrations.
- **Key sources:** Efron 1979 (Annals of Statistics); Efron 1987 (JASA, BCa); Efron & Tibshirani,
  *An Introduction to the Bootstrap*; DiCiccio & Efron 1996 (Statistical Science); Bickel & Freedman
  1981 (Annals of Statistics); Athreya 1987 (Annals of Statistics, heavy tails).
- **Search intent:** "bootstrap confidence interval", "bca bootstrap explained", "percentile vs bca
  bootstrap", "when does the bootstrap fail"

### Part 8 — Choosing a Statistical Test: The Design Decides, Not the Data

- **Slug:** choosing-a-statistical-test · **Arc:** Choosing a method · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** Which test answers my question, given how the data were collected, and what happens
  to its error rate when its conditions fail?
- **Assumes:** Part 5's testing framework.
- **Hands off:** Rank and permutation alternatives to 10; the t-test and ANOVA rebuilt as
  regressions to 13; experiment-specific tests (ratio metrics, CUPED) to DS-2.
- **Worked example:** R's `sleep` data, Student's own 1908 example. The same ten patients took both
  drugs, so the paired t-test (p ≈ 0.003) is the analysis the design dictates, while the unpaired
  test the data's two-column layout invites gives p ≈ 0.08: the design, not the data, chooses the
  test. Student's and Welch's t-tests are then measured: type I error by simulation across unequal
  variances and unequal group sizes, showing Student's error rate far from 5% when the smaller
  group has the larger variance. The two-stage habit (test normality and equal variances first,
  then pick the test) is simulated as a procedure and shown to control error worse than always
  using Welch. For a 2×2 table: Fisher's lady tasting tea (eight cups, one chance in 70), the
  chi-squared test and its expected-count condition, Fisher's exact test's conservatism, and the
  mid-p and unconditional alternatives. One-way ANOVA's F as a ratio of two variance estimates, and
  Welch's ANOVA beside it.
- **Corrects:** "Check normality and equal variances first, then choose the test." Pre-testing makes
  the overall procedure worse; choose from the design and use Welch by default.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. A type I error and power harness for
  any two-sample test; the pre-testing procedure simulated; exact and asymptotic 2×2 tests matched
  to SciPy and R.
- **Key sources:** Student 1908; Welch 1947 (Biometrika); Fisher 1935, *The Design of Experiments*;
  Delacre, Lakens & Leys 2017 (International Review of Social Psychology); Zimmerman 2004 (British
  J. Math. Stat. Psych.); Rasch, Kubinger & Moder 2011 (Statistical Papers); Lydersen, Fagerland &
  Laake 2009 (Statistics in Medicine).
- **Search intent:** "which statistical test to use", "welch vs student t-test", "paired vs
  unpaired t-test", "chi-square vs fisher exact test", "test normality before t-test"

### Part 9 — Multiple Comparisons: FWER, FDR, and the Tests You Didn't Count

- **Slug:** multiple-comparisons-fwer-fdr · **Arc:** Choosing a method · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** When I run many tests, what error am I controlling, which correction controls it, and
  how many tests did I really run?
- **Assumes:** Part 5's type I error.
- **Hands off:** Many metrics and guardrails in an experiment to DS-2; screening features for a
  predictive model to ML-2.
- **Worked example:** A real large-scale testing problem: Efron's prostate-cancer microarray data
  (about 6,000 genes, one test each), or the Hedenfalk data Storey and Tibshirani used, chosen at
  research by licence. It is corrected by hand with Bonferroni, Holm's step-down,
  Benjamini–Hochberg and Storey's q-values, and the discovery counts compared. Then simulation with
  known truth: the family-wise error rate and the false discovery proportion measured for each
  procedure, including under positive and arbitrary dependence, where Benjamini–Hochberg keeps or
  loses its guarantee and Benjamini–Yekutieli restores it. Then the forking paths: Simmons, Nelson
  and Simonsohn's 2011 researcher degrees of freedom (choice of outcome, covariate, stopping point,
  subgroup) simulated to show the false-positive rate they produce with no table of p-values in
  sight, and Freedman's 1983 screening result, where pure-noise regressors screened at 0.25 and
  refitted return a significant F (regression used here only as a fitting routine; Part 13 opens
  it).
- **Corrects:** "Controlling FDR at 5% means 5% of my discoveries are false." FDR is an expectation
  over repetitions; the realised proportion in one study varies, and Benjamini–Hochberg's guarantee
  needs a dependence condition.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. The four procedures by hand, matched to
  `statsmodels.stats.multitest` and R's `p.adjust`; the FWER and FDP simulator under three
  dependence structures; the forking-paths and Freedman simulations.
- **Key sources:** Holm 1979 (Scand. J. Stat.); Benjamini & Hochberg 1995 (JRSS-B); Benjamini &
  Yekutieli 2001 (Annals of Statistics); Storey & Tibshirani 2003 (PNAS); Efron, *Large-Scale
  Inference* (2010); Simmons, Nelson & Simonsohn 2011 (Psychological Science); Freedman 1983 (The
  American Statistician); Gelman & Loken 2014 (American Scientist).
- **Search intent:** "benjamini-hochberg explained", "bonferroni vs fdr", "family-wise error rate",
  "garden of forking paths", "p-hacking simulation"

### Part 10 — Permutation and Rank Tests: What Nonparametric Methods Actually Test

- **Slug:** permutation-and-rank-tests · **Arc:** Choosing a method · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How can a test be exact without assuming a distribution, and what hypothesis does
  each rank test actually test?
- **Assumes:** Part 8's two-sample tests and their measured error rates.
- **Hands off:** Randomisation inference for experiments to DS-2 and DS-3.
- **Worked example:** Darwin's 15 pairs of cross- and self-fertilised *Zea mays*, the data Fisher
  used in 1935 to introduce the randomisation test: all 2¹⁵ = 32,768 sign assignments enumerated
  and the exact p-value read off, beside the paired t-test and the Wilcoxon signed-rank test on the
  same pairs. Exchangeability is the condition that makes a permutation test exact; a two-sample
  permutation test with unequal variances is shown failing as a test of means (Romano 1990) and
  fixed by studentising the statistic. Mann–Whitney is shown to test P(X > Y) = ½, not medians:
  two populations with equal medians and different shapes, on which it rejects far more than 5% of
  the time. The Hodges–Lehmann shift estimate and its interval, and the efficiency cost of ranks:
  3/π ≈ 0.955 relative to the t-test under normality and never below 0.864 (Hodges and Lehmann
  1956). Spearman and Kendall as rank correlations; Kruskal–Wallis named. Monte Carlo permutation
  p-values with the +1 correction (Phipson and Smyth 2010).
- **Corrects:** "Mann–Whitney compares medians, so use it when the data are not normal." It tests
  stochastic ordering; the choice follows the hypothesis, not the histogram.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Exact enumeration on Darwin's pairs; a
  permutation engine with studentised statistics; the equal-medians Mann–Whitney simulation;
  Hodges–Lehmann matched to R's `wilcox.test(conf.int = TRUE)`.
- **Key sources:** Fisher 1935, *The Design of Experiments*; Hodges & Lehmann 1956 (Ann. Math.
  Stat.); Romano 1990 (JASA); Chung & Romano 2013 (Annals of Statistics); Divine et al. 2018 (The
  American Statistician); Phipson & Smyth 2010 (Stat. Appl. Genet. Mol. Biol.).
- **Search intent:** "permutation test explained", "what does the mann-whitney test test",
  "wilcoxon signed-rank test", "parametric vs nonparametric test"

### Part 11 — Bayesian Inference by Hand: Priors, Conjugacy and Credible Intervals

- **Slug:** bayesian-inference-conjugate-priors · **Arc:** Bayesian inference · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How do a prior and a likelihood become a posterior, what does a credible interval say
  that a confidence interval cannot, and how did a vaccine trial use one?
- **Assumes:** Part 4's likelihood.
- **Hands off:** Posteriors without a closed form to 12; hierarchical priors to 18; Bayesian
  modelling machinery in depth to ML-4; Bayesian A/B testing to DS-2.
- **Worked example:** Laplace's question about the children baptised in Paris (how probable is it
  that a birth is a boy with probability below ½?) solved with a uniform prior and a beta posterior.
  Then the Pfizer–BioNTech phase 3 primary analysis reproduced from its protocol: a Beta(0.700102, 1)
  prior on the vaccine group's share of cases, updated by 8 of 170 cases to Beta(8.700102, 163) and
  transformed to vaccine efficacy, gives the published 95% credible interval of 90.3% to 97.6%
  (re-computed for this plan). The conjugate pairs (beta–binomial, gamma–Poisson, normal–normal) are
  derived from the likelihood kernels; equal-tailed versus highest-density intervals; the posterior
  predictive distribution; prior sensitivity, and why a flat prior stops being "uninformative" once
  the parameter is transformed (flat on p is not flat on the log-odds; Jeffreys' prior as the
  invariant choice). The Bayes factor versus the posterior for estimation, with Lindley's paradox
  on a large-n birth-ratio test where the two schools disagree.
- **Corrects:** "With a flat prior the Bayesian answer is objective." Flatness depends on the
  parameterisation; the prior is always a modelling choice, and its effect is checked, not assumed
  away.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Conjugate updates by hand, checked
  against `scipy.stats`; the Pfizer posterior reproduced to the published decimals; HDI computation;
  a prior-sensitivity sweep; the Lindley's-paradox calculation.
- **Key sources:** Laplace's memoirs of 1774–1781 and *Théorie analytique des probabilités* (1812);
  Polack et al. 2020 (NEJM) with the trial protocol's statistical analysis plan; Jeffreys 1946
  (Proc. R. Soc. A); Lindley 1957 (Biometrika); Gelman et al., *Bayesian Data Analysis* (3rd ed.).
- **Search intent:** "bayesian inference explained", "beta-binomial conjugate prior", "credible
  interval vs confidence interval", "pfizer vaccine bayesian analysis", "lindley's paradox"

### Part 12 — MCMC You Can Trust: Metropolis by Hand and the Convergence Diagnostics

- **Slug:** mcmc-diagnostics-metropolis-nuts · **Arc:** Bayesian inference · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** When the posterior has no closed form, how do I draw from it, and how do I know the
  draws describe it?
- **Assumes:** Part 11's posterior.
- **Hands off:** Divergences and the hierarchical funnel to 18; how HMC and NUTS work inside, Gibbs
  sampling and variational inference to ML-4.
- **Worked example:** A random-walk Metropolis sampler written from scratch and first run on Part
  11's Pfizer posterior, where the exact answer is known: the chain's mean, quantiles and interval
  are checked against the closed form within their Monte Carlo error. Then a posterior with no
  closed form, Part 1's negative binomial for Greenwood and Yule's accidents with weak priors on the
  mean and dispersion, sampled by the same code and checked against a brute-force grid evaluation
  of the two-dimensional posterior. Tuning by acceptance rate; autocorrelation and the effective
  sample size; the Monte Carlo standard error of a posterior mean; split, rank-normalised R̂ with
  the current 1.01 threshold and bulk and tail ESS (Vehtari et al. 2021), each computed by hand and
  matched to ArviZ. A badly tuned chain, and chains that all start in one mode of a bimodal
  posterior, show what each diagnostic catches and what it misses. The same model is then fitted
  with NUTS in PyMC as the production tool, its diagnostics read but its internals not derived
  (those are ML-4's).
- **Corrects:** "R̂ below 1.1 means the chain converged." The threshold is now 1.01 with rank
  normalisation, and no within- or between-chain statistic can see a mode no chain visited.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. The from-scratch Metropolis sampler;
  the exact-posterior and grid checks; hand-computed R̂, ESS and MCSE matched to ArviZ; the same
  model in PyMC with NUTS (versions pinned at research).
- **Key sources:** Metropolis et al. 1953 (J. Chem. Phys.); Hastings 1970 (Biometrika); Gelman &
  Rubin 1992 (Statistical Science); Roberts, Gelman & Gilks 1997 (Ann. Appl. Prob., optimal
  scaling); Vehtari, Gelman, Simpson, Carpenter & Bürkner 2021 (Bayesian Analysis); Hoffman &
  Gelman 2014 (JMLR, NUTS).
- **Search intent:** "mcmc explained", "metropolis-hastings algorithm", "r-hat and effective sample
  size", "how to check mcmc convergence"

### Part 13 — Linear Regression as an Inferential Model: Every Number in the Summary Table

- **Slug:** linear-regression-inference · **Arc:** The linear model · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** What exactly does a regression estimate, where does every number in its output come
  from, and what may I conclude from a coefficient?
- **Assumes:** Part 8's t-test and one-way ANOVA, rebuilt here as the linear model with one dummy
  and with a factor. (Links Part 4: least squares is the Gaussian MLE.)
- **Hands off:** Checking the model's conditions and robust standard errors to 14; non-normal
  outcomes to 15; grouped data to 17; causal readings of coefficients to DS-3; regularisation and
  prediction to ML-2.
- **Worked example:** NIST's Statistical Reference Datasets as the test vector. The Longley economic
  data (16 years, six highly collinear predictors) are fitted by QR decomposition, reproducing
  NIST's certified coefficients and standard errors to the digits they certify, while solving the
  normal equations in double precision loses digits measurably (McCullough's log relative error);
  NIST's Filip polynomial is the case where the naive route fails outright. Then every number in an
  R `lm` and statsmodels summary is recomputed from the design matrix: coefficients, σ̂ with its
  n − p divisor, standard errors from σ̂²(XᵀX)⁻¹, t and p, R² and adjusted R², the overall F and the
  nested-model F that Part 8's ANOVA was. Interpretation: a coefficient as a conditional
  association, the omitted-variable bias formula (handed to DS-3), interactions and centring,
  collinearity and the variance inflation factor on Longley. The confidence interval for the mean
  response against the prediction interval for a new observation.
- **Corrects:** "Linear regression needs normally distributed variables." Normality concerns the
  errors and matters only for exact small-sample inference; linearity, independence and constant
  variance carry the weight.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. OLS by QR and by the normal equations,
  scored in log relative error against NIST's certified values; a summary table recomputed line by
  line and matched to statsmodels and R's `lm`; the collinearity and interval demonstrations.
- **Key sources:** NIST StRD (Longley, Filip, certified values); Longley 1967 (JASA); McCullough 1998
  (The American Statistician); Golub & Van Loan, *Matrix Computations*; Gelman, Hill & Vehtari,
  *Regression and Other Stories*; Lindeløv, "Common statistical tests are linear models".
- **Search intent:** "linear regression output explained", "regression standard error formula",
  "interpret regression coefficients", "multicollinearity vif", "prediction interval vs confidence
  interval"

### Part 14 — Regression Diagnostics: Residuals, Leverage, Influence and Robust Standard Errors

- **Slug:** regression-diagnostics-robust-standard-errors · **Arc:** The linear model · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** How do I tell whether a regression's numbers can be trusted, which observations are
  driving them, and how do I repair inference when the variance is not constant?
- **Assumes:** Part 13's fitted model and its summary.
- **Hands off:** Grouped and clustered errors to 17 (randomisation-unit clustering to DS-2);
  autocorrelated errors and HAC standard errors to DS-4; outlier handling as a data step to DS-5.
- **Worked example:** Anscombe's 1973 quartet: four datasets with the same fitted line, R² and
  standard errors, told apart only by their residual and leverage plots. Then Duncan's 1961
  occupational-prestige data, where a few occupations (ministers and railroad conductors among
  them) pull the fit: the hat matrix's leverage, studentised residuals and Cook's distance computed
  by hand, and the fit compared with and without them. Heteroskedasticity on a real dataset (chosen
  at research): the Breusch–Pagan test, then HC0 to HC3 sandwich standard errors computed from
  their formulas and their coverage measured by simulation at small n, reproducing Long and Ervin's
  case for HC3. Nonlinearity found with partial-residual plots and fixed with a regression spline;
  the Box–Cox transformation; Huber's robust regression named as the alternative to deleting
  points. The pairs and residual bootstraps deferred from Part 7, and when each is valid.
- **Corrects:** "First check that the residuals are normal." Of the conditions, normality matters
  least at moderate n; linearity and the variance structure decide whether the estimates and their
  standard errors mean anything.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Leverage, studentised residuals and
  Cook's distance by hand, matched to statsmodels' influence measures and R's `influence.measures`;
  the HC0–HC3 coverage study; the pairs-versus-residual bootstrap comparison.
- **Key sources:** Anscombe 1973 (The American Statistician); Cook 1977 (Technometrics); Belsley,
  Kuh & Welsch 1980, *Regression Diagnostics*; White 1980 (Econometrica); MacKinnon & White 1985
  (J. Econometrics); Long & Ervin 2000 (The American Statistician); Fox, *Applied Regression
  Analysis and Generalized Linear Models*.
- **Search intent:** "regression diagnostics", "residual plot interpretation", "cook's distance",
  "heteroskedasticity robust standard errors", "anscombe's quartet"

### Part 15 — Generalized Linear Models: Logistic Regression and IRLS by Hand

- **Slug:** glm-logistic-regression · **Arc:** Generalized linear models · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** How does one fitting algorithm cover binary, count and continuous outcomes, and how
  do I read a logistic regression without the usual mistakes?
- **Assumes:** Part 13's linear model. (Links Part 4: a GLM is fitted by Fisher scoring on its
  likelihood.)
- **Hands off:** Counts, exposure and overdispersion to 16; random effects in a GLM to 17 and 18;
  classification metrics, thresholds and calibration to ML-2.
- **Worked example:** The 23 shuttle launches before Challenger, with O-ring damage against launch
  temperature (Dalal, Fowlkes and Hoadley 1989). A logistic regression is fitted by iteratively
  reweighted least squares written from scratch, each iteration's working response, weights and
  coefficients printed, converging to R's `glm` and statsmodels to ten digits. The exponential
  family, the link and the variance function are the three choices that define every GLM; then
  deviance, the likelihood-ratio test between nested fits, and the Wald test's failure for large
  effects (the Hauck–Donner effect, linking Part 4). The extrapolation to the 31 °F forecast for
  28 January 1986, with its interval computed on the logit scale and transformed, and an honest
  statement of how far outside the data it lies. Odds ratios against risk ratios on the same fit.
  Complete and quasi-complete separation shown on a modified dataset, with Firth's penalised
  likelihood as the fix.
- **Corrects:** "An odds ratio of 2 means twice as likely." The odds ratio approximates the risk
  ratio only for rare outcomes; for common ones it overstates it.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. IRLS from scratch for the logit, probit
  and complementary log-log links, matched to R and statsmodels; deviance and LR tests; the 31 °F
  prediction and its interval; separation and a Firth fit.
- **Key sources:** Nelder & Wedderburn 1972 (JRSS-A); McCullagh & Nelder, *Generalized Linear
  Models* (2nd ed.); Dalal, Fowlkes & Hoadley 1989 (JASA); Hauck & Donner 1977 (JASA); Albert &
  Anderson 1984 (Biometrika); Firth 1993 (Biometrika).
- **Search intent:** "logistic regression explained", "irls algorithm glm", "odds ratio vs relative
  risk", "perfect separation logistic regression", "challenger o-ring logistic regression"

### Part 16 — Count Data: Poisson, Offsets, Overdispersion and the Negative Binomial

- **Slug:** count-regression-poisson-negative-binomial · **Arc:** Generalized linear models · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** How do I model counts that accrue over different exposures, and what should I do
  when they vary more than a Poisson allows?
- **Assumes:** Part 15's GLM machinery. (Links Part 1's gamma–Poisson story.)
- **Hands off:** Event counts in metric design to DS-7; counts over time to DS-4; random effects for
  grouped counts to 18.
- **Worked example:** McCullagh and Nelder's ship-damage data (R's `MASS::ships`): incidents by ship
  type, construction period and operating period, with months of service entering as a log offset,
  so the model is for the rate, not the count. Overdispersion is measured (the Pearson statistic
  over its degrees of freedom), then three responses are compared on the same data: quasi-Poisson
  (rescale the standard errors), sandwich standard errors (the Poisson estimate is still consistent
  for the mean) and the negative binomial (a different variance function, so different observation
  weights, Ver Hoef and Boveng's point, shown on the fitted weights). Part 1's gamma–Poisson
  derivation reappears as the NB2 variance μ + μ²/k, with NB1 beside it. School absence days
  (`MASS::quine`) are the second dataset. Zeros are handled by zero-inflated and hurdle models,
  chosen from the generative story (two processes versus one barrier), and every fit's expected
  counts are compared on a rootogram.
- **Corrects:** "Overdispersion means the Poisson model is wrong, so switch to the negative
  binomial." The Poisson mean model can be right while its standard errors are wrong; the negative
  binomial changes the weights, and the choice is about the variance function.
- **Lab:** G1 · runs anywhere · ladder E1–E4 · access: none. Poisson with an offset by Part 15's
  IRLS; quasi-Poisson, sandwich and NB2/NB1 fits matched to R's `glm` and `MASS::glm.nb`;
  zero-inflated and hurdle fits in statsmodels; rootograms.
- **Key sources:** McCullagh & Nelder (ships data); Cameron & Trivedi, *Regression Analysis of Count
  Data* (2nd ed.); Ver Hoef & Boveng 2007 (Ecology); Lambert 1992 (Technometrics); Mullahy 1986 (J.
  Econometrics); Zeileis, Kleiber & Jackman 2008 (J. Stat. Software); Venables & Ripley, *Modern
  Applied Statistics with S*.
- **Search intent:** "poisson regression offset", "overdispersion in poisson regression", "negative
  binomial vs poisson", "quasi-poisson vs negative binomial", "zero-inflated vs hurdle model"

### Part 17 — Mixed-Effects Models: Random Effects, REML and Partial Pooling

- **Slug:** linear-mixed-effects-models · **Arc:** Multilevel models · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** When observations come in groups, how does a mixed model share information between
  groups, how is it estimated, and how do I test what it estimates?
- **Assumes:** Part 13's linear model. (Links Part 3's shrinkage and Part 4's boundary problem.)
- **Hands off:** The Bayesian hierarchical model, its priors and its sampler geometry to 18;
  clustered randomisation in experiments to DS-2; repeated measures with autocorrelation to DS-4.
- **Worked example:** The sleep-deprivation study (Belenky et al. 2003; `sleepstudy`, 18 subjects
  over 10 days). Complete pooling (one line), no pooling (18 lines) and partial pooling (a mixed
  model with random intercepts and slopes) are fitted and drawn on one figure, each partial-pooling
  line pulled toward the population line by an amount set by its subject's noise: Part 3's
  James–Stein shrinkage again, now as BLUPs. The model is written in Laird and Ware's form; REML is
  derived as likelihood on residual contrasts and shown removing ML's downward bias in the variance
  (Patterson and Thompson 1971); a random-intercept fit is computed by hand and matched to R's
  `nlme::lme` and statsmodels `MixedLM`. Testing: the random-slope variance sits on a boundary (Part
  4's χ² mixture), and fixed effects need approximate degrees of freedom (Satterthwaite,
  Kenward–Roger), which is why `lme4` prints no p-values. Singular fits, and "keep it maximal"
  against parsimony, by simulation. The choice between a mixed model, cluster-robust standard
  errors and GEE is framed as conditional versus marginal questions.
- **Corrects:** "Use random effects when the levels are a random sample from a population, fixed
  effects otherwise." The term has at least five conflicting definitions (Gelman 2005); the working
  question is whether the groups should share information, and how much.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. The pooling comparison; REML versus ML
  by hand for the random-intercept model; matched fits in `nlme`, statsmodels and a
  self-provisioned `lme4`; the boundary-test and degrees-of-freedom simulations; cluster-robust and
  GEE fits beside the mixed model.
- **Key sources:** Laird & Ware 1982 (Biometrics); Patterson & Thompson 1971 (Biometrika); Bates,
  Mächler, Bolker & Walker 2015 (J. Stat. Software); Belenky et al. 2003 (J. Sleep Research);
  Kenward & Roger 1997 (Biometrics); Stram & Lee 1994 (Biometrics); Barr et al. 2013 and Matuschek
  et al. 2017 (J. Memory and Language); Gelman 2005 (Annals of Statistics).
- **Search intent:** "linear mixed effects model explained", "random vs fixed effects", "reml vs
  ml", "partial pooling", "lme4 p-values"

### Part 18 — Bayesian Hierarchical Models: Eight Schools, the Funnel and Partial Pooling

- **Slug:** bayesian-hierarchical-models · **Arc:** Multilevel models · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** How does a fully Bayesian hierarchical model pool groups, why does its sampler fail
  in a characteristic way, and how do I fix it and compare models?
- **Assumes:** Part 17's mixed model and partial pooling. (Links Part 12's NUTS and diagnostics.)
- **Hands off:** Nothing in this series; it closes the series. Hierarchical models as graphical
  models, and their inference algorithms, to ML-4; Bayesian experiment analysis to DS-2.
- **Worked example:** Rubin's 1981 eight schools (coaching effects and their standard errors): no
  pooling, complete pooling and the hierarchical model compared, the posterior of the between-school
  standard deviation τ drawn, and each school's estimate traced as τ varies. The centred
  parameterisation sampled with NUTS produces divergent transitions; their locations are plotted in
  the funnel between τ and the school effects, and the non-centred parameterisation is shown
  removing them. The prior on τ: Gelman's 2006 analysis of why inverse-gamma(ε, ε) misbehaves on
  exactly this dataset, and half-normal or half-Cauchy instead. Then Gelman and Hill's Minnesota
  radon survey (919 homes in 85 counties) with varying intercepts and slopes as the larger model,
  posterior predictive checks, and PSIS-LOO with its Pareto-k̂ diagnostic to compare pooling
  structures. Marginal versus conditional effects in a hierarchical logistic model close the
  decision Part 17 opened.
- **Corrects:** "Divergent transitions are only a warning; if R̂ looks fine, carry on." Divergences
  mean the sampler cannot reach part of the posterior, and the estimates are biased even when R̂ and
  ESS look healthy.
- **Lab:** G1 · runs anywhere · ladder E1–E5 · access: none. Eight schools in PyMC, centred and
  non-centred, with divergences located; the τ-prior comparison; radon varying-intercept and
  varying-slope models; PSIS-LOO and posterior predictive checks with ArviZ; an empirical-Bayes fit
  for comparison.
- **Key sources:** Rubin 1981 (J. Educational Statistics); Gelman 2006 (Bayesian Analysis);
  Papaspiliopoulos, Roberts & Sköld 2007 (Statistical Science); Betancourt & Girolami 2015
  (Hamiltonian Monte Carlo for hierarchical models); Vehtari, Gelman & Gabry 2017 (Statistics and
  Computing); Gelman & Hill 2007, *Data Analysis Using Regression and Multilevel/Hierarchical
  Models*; Zeger, Liang & Albert 1988 (Biometrics).
- **Search intent:** "eight schools hierarchical model", "bayesian hierarchical model explained",
  "non-centered parameterization", "divergent transitions pymc", "radon partial pooling"

## Publication order and cadence

Strict prerequisite order. A part may publish once the one part it names under **Assumes** is
live, so two tracks can interleave after Part 2 (3 → 4 → 11 → 12, and 5 → 6 → 7 with 8 → 9 → 10),
and the modelling arc can start once Part 8 is live. The arcs are the natural release waves. One
part per week keeps each arc coherent in the feed. Versions (NumPy, SciPy, pandas, statsmodels,
PyMC, ArviZ, R) are pinned per part at research time, never from this plan.

DS-1 is the data-science category's entry series. Per the roadmap it starts after Wave 0, in
parallel with DB-3 (still the recommended single next start across categories); nothing in Wave 0
is touched.

## Cross-links

Within the series, each part names the one part it assumes, and any part its **Assumes** line
links, by title in plain text; the owner inserts the links once the target is live. Across the map,
links run only from the later-published part, and published parts are never edited to add forward
links:

- **DS-2 Experimentation** uses Parts 5, 6 and 9 (testing, intervals, multiplicity), Part 4's delta
  method and Part 7's bootstrap.
- **DS-3 Causal Inference** uses Part 13's omitted-variable bias and Part 17's conditional-versus-
  marginal distinction.
- **DS-4 Time Series** picks up Part 7's dependence failure (the block bootstrap) and Part 14's
  autocorrelated errors.
- **DS-5 Data Wrangling** owns the selection bias and missing data that Part 2's sampling condition
  excludes.
- **DS-6 Visualization** uses Part 6's intervals and Part 14's diagnostic plots.
- **DS-7 Product Analytics** uses Part 16 (counts and rates) and Part 5 (testing); survival analysis
  is DS-7's.
- **ML-2 Classical ML** extends Part 3's bias–variance of estimators to prediction error, and uses
  Parts 13 and 15.
- **ML-4 Probabilistic ML** continues Parts 11, 12 and 18 into HMC internals, variational inference
  and EM.
- **DL-1 Deep Learning Foundations** reads losses as negative log-likelihoods, Part 4's object.
- **CV-2 Diffusion Models, Part 9** (*Evaluating Generative Models: What FID Measures and Hides*,
  built, not live) measures an estimator whose bias shrinks with sample size; Part 3 may name it in
  plain text as an applied case.

## Lab policy

Every part is **G1 — runs anywhere**, self-provisioned, no access request. The toolchain is a `uv`
environment per part pinning NumPy, SciPy, pandas, statsmodels and Matplotlib, plus PyMC and ArviZ
for Parts 12 and 18. R 4.5.2 is already on the machine with MASS, boot, nlme, mgcv and survival, and
serves as the independent reference implementation; packages it lacks (`lme4`, `sandwich`) are
installed only into an isolated library under `~/.cache` when a part needs them. The pattern for
every method:

1. a from-scratch NumPy implementation that prints its intermediates;
2. matched to the reference implementations to a stated tolerance, and to certified values or exact
   closed forms where they exist;
3. its guarantee measured by Monte Carlo with MCSE, on two budgets: a `--quick` budget the reader
   runs and the full budget the article's numbers come from, both captured;
4. real data shipped as small CSVs with a provenance header (source, citation, licence), or fetched
   from the public source with a checksum where the licence does not allow redistribution.

Python is the lab language. R ships as an optional `crosscheck.R` only where an R function is the
field's reference (`boot.ci` in Part 7, `lm` in 13, `glm` and `MASS::glm.nb` in 15 and 16, `nlme`
and `lme4` in 17); elsewhere the R cross-check is the author's private check, and its output is
recorded in the captures. No number is invented: every simulated number ships with its seed,
replication count and MCSE, and anything simulated is labelled simulated.

### Access requests

None. The probe (see `access.md`) shows that everything the series needs is present or user-space
installable. No GPU, container, root, credential or service is load-bearing for any worked example,
figure or claim.

## What this series will not cover

- **Experiment design and A/B testing practice:** randomisation units, sample-size and MDE
  planning, CUPED, ratio metrics, sequential and always-valid tests, SRM. That is DS-2. Optional
  stopping appears once, in Part 5, as the condition that breaks a fixed-n p-value.
- **Causal identification:** potential outcomes, DAGs, matching and weighting, difference in
  differences, regression discontinuity, instrumental variables. That is DS-3; Part 13 states the
  omitted-variable bias and stops.
- **Dependent data:** autocorrelation, HAC errors, the block bootstrap, forecasting. That is DS-4;
  Parts 7 and 14 name where independence fails.
- **Missing data, imputation, outliers and selection bias:** DS-5. Every part states the
  complete-case, independent-sampling condition it relies on.
- **Communicating uncertainty and chart design:** DS-6.
- **Survival analysis** (censoring, Kaplan–Meier, Cox): DS-7, as the map has it (owner decision
  below).
- **Predictive modelling:** regularisation, cross-validation, calibration, classification metrics.
  That is ML-2.
- **Inference algorithms in depth:** HMC and NUTS internals, Gibbs sampling, variational inference,
  EM, graphical models. That is ML-4.
- **Formal probability and proofs:** measure theory, proofs of the CLT or of asymptotic normality.
  Results are stated with their conditions and checked by simulation; sketches are labelled as
  sketches.
- **Nonparametric curve estimation** (kernel density bandwidths, LOESS, smoothing splines, GAMs)
  beyond the regression spline in Part 14. A candidate later part (owner decision below).
- **Survey sampling and weighting** (design-based inference, Horvitz–Thompson, design effects),
  **multivariate analysis** (MANOVA, factor analysis; PCA is ML-2's), **extreme-value theory**,
  **copulas** and **spatial statistics**: each is its own subject.

## Risks

- **Saturation.** This is the most crowded subject on the map. Each part's literature sweep must
  find the gap the four-point angle claims; a part whose sweep finds its angle already done well is
  re-cut at its brief, never padded.
- **Title collision.** "Statistics for Data Scientists" is close to Bruce, Bruce & Gedeck's
  O'Reilly title *Practical Statistics for Data Scientists*; the subtitle carries the distinction in
  search.
- **Simulation honesty.** Every simulated rate needs enough replications that its MCSE is well below
  the effect shown, and a noisy comparison is measured at the full budget before a narrative or a
  figure is built on it (the lesson of Diffusion Models Part 9). An injected fault for an E4 rung is
  run on the reader's `--quick` budget, where it must still fail.
- **Reference disagreements.** SciPy, statsmodels and R differ in defaults: variance divisors,
  p-value conventions, the negative binomial's dispersion as k, α = 1/k or θ. Each part states its
  convention and the mapping, and treats a disagreement as a finding to explain, never a rounding to
  hide.
- **Data licences.** Historical tables and NIST data are free to reuse; GPL-packaged R datasets and
  UCI data are reusable with attribution; anything else is fetched, not shipped. Settled per part at
  research.
- **Seams with siblings.** DS-2 (testing practice), ML-2 (regression for prediction) and ML-4
  (Bayesian computation) sit closest. The boundary recorded in `context.md` is kept.
- **Version currency.** statsmodels 0.15, PyMC 6 and ArviZ 1.x (as resolved on 2026-10-23) are
  recent and their APIs move; pin per part at research, never from this plan.
- **Difficulty drift.** Fifteen of the eighteen parts are advanced. Each still opens on its worked
  instance before any formula, so a reader can enter at any method.

## Open decisions for the owner

1. **18 committed parts** (recommended), or 16 with Parts 10 and 18 held as optional spokes.
2. **Survival analysis:** leave it in DS-7 as the map has it (recommended), or add the general
   machinery here as Part 19 and let DS-7 apply it to churn.
3. **Title:** *Statistics for Data Scientists: Every Guarantee, Measured*. One word to overrule.
4. **A smoothing part** (KDE, LOESS, splines, GAMs) as a later Part 19 or 20: not planned unless
   you want it.

Not a decision now: the `data-science` category row does not exist in the live DB. It is a
production write at publish time, your call then; blog-forge's category list gains the key when
Part 1 is built (roadmap decision 10).
