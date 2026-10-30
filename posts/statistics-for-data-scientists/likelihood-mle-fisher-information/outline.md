# Outline — likelihood-mle-fisher-information

Series `statistics-for-data-scientists`, Part 4 of 18 (Foundations ladder; parent: Part 3). Private build file.

## Brief

- **Title:** Likelihood: The MLE, Three Tests, and Where χ² Fails (52 characters; the plan's title runs to 88).
- **Answers:** how does the likelihood turn a model and data into an estimate, a standard error and a test,
  and when do its asymptotic promises fail?
- **Tier:** L4 (plan). Six things to learn: the log-likelihood, score and MLE; observed and expected
  information and the standard error; the Wald, score and likelihood-ratio statistics and why they disagree;
  a two-parameter likelihood with profile intervals and the delta method; the boundary mixture; the
  regularity conditions with three cases outside them. The worked example (one rate, one curve, three
  distances) fits a screen; the negative binomial needs a second. **Adjacent option:** L3 would drop the
  power-law comparison and the tank section, leaving the plan's Part 1 promise unkept.
- **Difficulty:** advanced. Assumes Part 3's estimator properties (bias, variance, MSE, consistency,
  sufficiency) and calculus to second derivatives. Proofs are sketched (Wilks via a Taylor expansion) or
  cited (Chernoff, Self–Liang, Vuong). **Adjacent option:** intermediate would drop the math section's
  expansions and the Vuong statistic.
- **Lab:** G1 · runs anywhere · E1–E5 · access none. Probe 2026-10-28 matches `access.md` (RAM available
  7 GiB; the lab peaks at 0.27 GB). statsmodels 0.15.0 and pandas 3.1.0 added to the series venv. R 4.5.2 with
  MASS 7.3.65, and the `powerlaw` 2.0.0 package in a throwaway venv, are the private checks.
- **Corrects:** "The likelihood-ratio statistic is χ²-distributed": only for a null inside the parameter space.
- **Four-point angle:** reconcile (every hand computation against SciPy and statsmodels, R and `powerlaw`
  privately); condition (regularity conditions named, then broken three ways: boundary, support, non-nested
  families; plus small n); measure (exact sizes of the three tests over the expected count; the boundary null
  simulated with R = 200,000; k̂'s sampling distribution); read the output (statsmodels' NB summary line,
  α and its SE, the χ²₁ p-value it invites).

## Settled at research

- Wilks, Chernoff, Rao and Fisher 1925 could not be read; attributions rest on Brazzale & Mameli, Self &
  Liang, Lawless, Buse and Stigler, and the post says "as stated by" where it matters.
- The V-1 null value λ₀ = 0.85 is a device (2.05 SE below the estimate), stated as one. The small-sample case
  uses real data with a real question: Bortkiewicz's corps XI against the ten regular corps' 0.61, taking
  0.61 as known (its SE, 0.055, is a fifth of XI's).
- Part 1's sample is regenerated bit for bit (threshold 26.140414260414); the `powerlaw` package reproduces
  the comparison exactly.
- Pawitan's book (plan) unreadable: not cited.

## Sections and budget

Validator words (decimals count twice; References add about 1,300). Target about 8,000 prose.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 280 | state the answer | — | — |
| Why this matters | 200 | see that a standard overdispersion test reports a p-value twice too large | — | L23 |
| The problem | 420 | define likelihood, log-likelihood, MLE; state the three promises and the claim tested | — | L01, L02, L34 |
| Worked example | 1,050 | compute λ̂, score, observed and expected information, SE for Clarke's squares; compute the three statistics and read them off one curve | FIG_01, FIG_02 | L03, L09, L10 |
| Intuition | 350 | picture a curve's peak, curvature and drop; know where the hill analogy breaks | — | — |
| When do the three tests disagree? | 850 | see the disagreement on 20 years of one corps, read exact sizes over the expected count, see Wald change with the parameter's scale | FIG_03–FIG_05 | L11–L14, L36 |
| What does a second parameter change? | 700 | fit the NB by Newton, check it, read the likelihood surface and the information matrix; observed versus expected | FIG_06 | L15, L16, L32, L33, L35 |
| Why is the profile interval lopsided? | 650 | build a profile interval, compare Wald on two scales, apply the delta method and check it by simulation | FIG_07, FIG_08 | L20, L37 |
| What happens when the null sits on a boundary? | 900 | test Poisson against NB correctly, explain the 50:50 mixture, measure it, read R's `odTest` | FIG_09, FIG_10 | L17–L19, L21–L24 |
| Which conditions does the χ² promise need? | 550 | name the regularity conditions and the reference distribution each break leads to; read the tank likelihood | FIG_11 | L05–L07, L25–L27 |
| Power law or lognormal? | 600 | run Vuong's comparison on the first part's sample, and read what threshold and sample size do to it | FIG_12, FIG_13 | L28–L31 |
| The math | 700 | the formulas, each tied to the worked numbers; Wilks's expansion sketched | — | L03, L07, L08 |
| Implementation | 400 | fit the NB by hand and check it; simulate the boundary | — | — |
| Limitations and common mistakes | 480 | avoid seven mistakes | — | L13, L25, L27 |
| Key takeaways | 190 | carry five claims | — | — |
| Try it yourself | 230 | E1, E3 from the article | — | — |
| References | ~1,300 | — | — | — |

## Figure plan

| # | Section | One thing it communicates | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | the curve's peak is λ̂, its curvature the information; the score crosses zero at λ̂ with slope −J | plot | Q1/Q4: a curve and its quadratic, computed from the data | The log-likelihood's peak is the estimate; how sharply it falls is the information, 617.8, which gives the SE 0.040 |
| 2 | Worked example | Wald = horizontal gap, score = slope at λ₀, LR = height drop, on Clarke's real curve | plot | Q4: geometry on a real curve | Three distances from λ̂ to λ₀ = 0.85: 4.18, 4.59, 4.45 |
| 3 | Three tests disagree | the same three distances on corps XI's 20 years: a skewed curve, 6.55 / 10.27 / 13.43 | plot | Q4: geometry, small sample | With 25 deaths the curve is lopsided, and the three statistics spread by a factor of two |
| 4 | Three tests disagree | exact size of each 5% test against the expected count m | plot | Q1: computed exactly over 400 values of m | Below an expected count of about 20 the Wald test's error rate swings far from 5% |
| 5 | Three tests disagree | Wald on the scale λ^c from c = −1 to 2, score and LR flat | plot | Q1: a computed curve | One data set, one null, Wald statistics from 3.6 to 27.5 |
| 6 | Second parameter | the NB likelihood region in (μ, k), skewed toward large k, against the Wald ellipse | plot | Q4: a 2-D region | The 95% likelihood region reaches k = 1.58; the Wald ellipse stops at 1.32 |
| 7 | Profile interval | profile log-likelihood for k and for D = 1 + μ/k, with their Wald quadratics | plot | Q4: curves and cut lines | The profile interval for k runs 0.28 below k̂ and 0.52 above |
| 8 | Profile interval | simulated k̂ over 20,000 data sets against the Wald normal | plot | Q1: measured histogram | k̂ is skewed right: it falls above the Wald limit in 7.5% of samples and below it in 0.14% |
| 9 | Boundary | profile log-likelihood in α for Clarke's data (peak at α = 0.04) and for a simulated Poisson data set (peak at α = 0) | plot | Q4: two curves meeting a boundary | Half of all Poisson data sets have their maximum on the edge, α = 0 |
| 10 | Boundary | simulated P(LR > x) under a boundary null and an interior null, against χ²₁ and the mixture | plot | Q1: measured survival curves | Inside the parameter space χ²₁ fits; on the boundary the mixture does |
| 11 | Regularity | the tank log-likelihood (a wall at m, convex beyond) beside a regular one; the MLE's error is exponential, not normal | plot | Q4: two shapes and a distribution | Where the support moves with N, the log-likelihood has no peak, no curvature and no normal limit |
| 12 | Power law | the first part's tail with both fitted CCDFs on log–log axes | plot | Q1: data and two fitted curves | Both fits pass through the 1,000 points; the lognormal fits 7.0 log-units better |
| 13 | Power law | normalised log-likelihood ratio against tail size, with the p < 0.1 band and the simulated spread | plot | Q1: computed and simulated | The verdict depends on how many points the threshold leaves |
| cover | — | the three distances on one curve | generated / placed | the cover only | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| likelihood, log-likelihood | The problem | the probability of the observed data as a function of the parameter; its log | turns a model and data into a function to maximise | whenever a model has a density or mass function |
| maximum likelihood estimate (MLE) | The problem | the parameter value with the largest likelihood | the general recipe Part 3 promised | point estimation in any parametric model |
| score | Worked example | the derivative of the log-likelihood | zero at an interior MLE; its variance is the information | solving for the MLE; the score test |
| observed information | Worked example | minus the second derivative of the log-likelihood at the MLE | its inverse is the variance estimate | the default SE from an optimiser's Hessian |
| expected (Fisher) information | Worked example | the expected value of minus the second derivative | the theoretical variance of the score | analytic SEs; Fisher scoring later in the series |
| standard error from the information | Worked example | 1/√information | the MLE's large-sample spread | whenever a library prints an SE beside an MLE |
| Wald, score, likelihood-ratio statistics | Worked example | three measures of distance from a null value | the three standard tests | testing one parameter value |
| χ² distribution, p-value | Worked example | the reference distribution of the statistics; the tail probability | turns a statistic into evidence | (p-values in depth come later in the series) |
| parameterisation, invariance | Three tests disagree | writing the same model with a transformed parameter | Wald changes, LR and score do not | before trusting a Wald interval |
| exact size | Three tests disagree | the actual probability a nominal 5% test rejects a true null | measures the guarantee | small counts |
| negative binomial (μ, k), dispersion α = 1/k | Second parameter | Part 1's overdispersed count model | the two-parameter case | counts with variance above the mean |
| nuisance parameter, orthogonal parameters | Second parameter | a parameter not of interest; parameters whose information is uncorrelated | profiling removes the nuisance; orthogonality makes μ̂ = ȳ for every k | multi-parameter models |
| profile likelihood, profile interval | Profile interval | the likelihood maximised over the nuisance parameters for each value of the parameter of interest | intervals that follow the curve's shape | dispersion, variance and other skewed parameters |
| delta method | Profile interval | a first-order Taylor expansion for the SE of a function of estimates | SEs for derived quantities | dispersion index, ratios, rates |
| boundary of the parameter space, mixture distribution | Boundary | a null value at the edge of the allowed range; a weighted mix of χ²₀ and χ²₁ | replaces χ²₁ on the edge | variance components, overdispersion, zero inflation |
| regularity conditions | Which conditions | the assumptions behind the asymptotic results | each failure changes the reference distribution | before using χ², normal SEs or Wald |
| nested and non-nested models, Vuong's test | Power law | one family inside another, or neither | LR for non-nested models is normal after standardising | choosing between families |
