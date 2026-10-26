# Outline — sampling-distribution-central-limit-theorem

Series `statistics-for-data-scientists`, Part 2 of 18 (Foundations ladder; parent: Part 1). Private build file.

## Brief

- **Title:** The Sampling Distribution: The CLT and Where n = 30 Fails (56 characters; the plan's title
  runs to 72, over the 60-character limit).
- **Answers:** a statistic computed from a sample is a random variable. What is its distribution, how fast
  does it become normal, and when does it never?
- **Tier:** L3 (plan). Five distinct things to learn (the sampling distribution and SE, Student's t, the
  skewness rate, Berry–Esseen, infinite variance) plus the simulation instrument; the smallest honest worked
  example (a real skewed population sampled at four n) fills a screen. **Adjacent option:** L4 would add the
  bootstrap-t and skewness-corrected intervals, which belong to later parts.
- **Difficulty:** intermediate. Assumes Part 1's populations, expectation and variance, NumPy. The Edgeworth
  and characteristic-function material is stated and checked, not derived. **Adjacent option:** advanced
  would derive the Edgeworth terms; beginner would drop Berry–Esseen, which carries the "guaranteed versus
  good enough" contrast the plan asks for.
- **Lab:** G1 · runs anywhere · E1–E4 · access none (probe 2026-10-26 matches `access.md`: RAM available
  4 GiB). NumPy 2.5.4 and SciPy 1.18.1 in the series venv; R 4.5.2 as the private check of Student's numbers.
- **Corrects:** "The CLT kicks in at n = 30."
- **Four-point angle:** reconcile (simulated SE against σ/√n; the inverted characteristic function against
  the exponential's exact gamma CDF; Student's 1908 numbers against R's `t.test`; Wilcox and Rousselet's
  published lognormal rates rerun); condition (independent draws and finite variance stated, then broken:
  sampling without replacement in E4, Cauchy and Pareto in the body); measure (every rate with MCSE and R);
  read the output (Student's table and his z against today's t; the t statistic's two tails read separately).

## Population decision (settled at research)

UCI Online Retail (CC BY 4.0). Net spend per customer: every line with a CustomerID, cancellations and
adjustments included, rounded to the penny, positive totals kept: 4,317 of 4,372 customers. Gross purchases
were rejected because two customers who cancelled bulk orders (£168,473 and £77,184) would count as big
spenders. Skewness 21.6 either way. `lab/derive_spend.py` rebuilds the CSV from the archive by checksum.

## Sections and budget

Validator words (decimals count twice). Target about 6,400 prose plus about 950 references.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 260 | state the answer | — | — |
| Why this matters | 200 | see what a miscalibrated revenue alert costs | — | — |
| The problem | 430 | define estimand, estimator, sampling distribution, SE; say what the CLT does not promise | — | L03, L06, L13, L24 |
| Worked example | 1,050 | simulate a sampling distribution, separate SD from SE, measure a t-test's two tails | FIG_01–04 | L01, L02, L04 |
| Intuition | 380 | explain why skew splits the tails: mean and SD move together | FIG_05 | L11 |
| Why does Student's t replace z? | 600 | say what t corrects (σ estimated) and what it cannot (skew) | FIG_06 | L05–L09 |
| How fast does the CLT work? | 700 | predict a tail error from γ/√n; compare Cochran's rule with the one-sided need | FIG_07 | L10–L16 |
| What does Berry–Esseen guarantee? | 450 | contrast the guaranteed n with the n that is good enough | FIG_08 | L17–L19 |
| When does the CLT never arrive? | 450 | recognise infinite variance and its consequences | FIG_09 | L20–L23 |
| How many replications does a simulation need? | 450 | choose R from a target MCSE; seed streams; read a published simulation | FIG_10 | L15, L16, L24–L27 |
| The math | 650 | the formulas, each tied back to the worked numbers | — | L10, L11, L17, L22, L24 |
| Implementation | 300 | run the core simulation | — | L28 |
| Limitations and common mistakes | 400 | avoid six mistakes | — | L04, L29–L31 |
| Key takeaways | 150 | carry five claims | — | — |
| Try it yourself | 220 | E1, E3 from the article | — | — |
| References | ~950 | — | — | — |

## Figure plan (route gate run per figure)

| Fig | Section | One thing it says | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 01 | Worked example | the population is a few whales and many small customers: mean far above median | chart | Q1: the dataset's own distribution, binned by the lab | Spend on a log scale; 79% of customers sit below the mean |
| 02 | Worked example | the sampling distribution keeps the population's skew, shrinking as γ/√n | plot | Q4: small multiples of simulated distributions against one normal curve | Same axis in standard errors; only the shape changes |
| 03 | Worked example | SD describes customers, SE describes means, s/√n usually underestimates SE | plot | Q4: theory lines against simulated quantile bands on log axes | The estimated SE is usually far below the true one |
| 04 | Worked example | the two one-sided error rates of a 5% t-test against n | chart | Q1: rates measured by simulation, with MCSE | One tail fires too often, the other almost never |
| 05 | Intuition | samples that miss the big customers have a low mean and a low SD, so t is very negative | plot | Q4: a scatter of 3,000 simulated samples with the rejection boundary | The t-test rejects where the mean and the SD fall together |
| 06 | Student's t | t₉ against the normal; 1.96 with an estimated s rejects 8.2% | plot | Q4: exact densities with Student's data and a simulated rate | What Student corrected |
| 07 | How fast | the tail error collapses onto 0.110 γ/√n across eight populations | plot | Q4: simulated rates against a first-order curve, a construction | Skewness over √n, not n, sets the error |
| 08 | Berry–Esseen | the guarantee arrives 50 to 72 times later than the exact distance | plot | Q4: exact distances and bounds on log–log axes | Guaranteed against good enough |
| 09 | Never | Cauchy means never settle; Pareto(1.5) means settle slowly and t-test errors stay near 26% | plot | Q4: simulated running means and rates, three panels | Infinite variance: the CLT's condition, broken |
| 10 | Replications | reruns of a published simulation spread by their MCSE | plot | Q4: a distribution of simulated estimates with published values marked | The MCSE says which differences are noise |
| Cover | — | the n = 30 sampling distribution against the normal curve, its lower-tail error highlighted | placed | template cover in the series house layout; no external generator | — |

Source-route check: Wilcox and Rousselet's Fig. 1 is CC BY 4.0 and relevant, but our Figures 2 and 5 show the
same mechanism on the post's own data and the lab reruns their numbers (ledger F1). Hesterberg's Figs. 21–22 carry
only arXiv's licence (F2). Morris et al.'s ADEMP figure is not needed (F3).

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| estimand / estimator / estimate | The problem | the population quantity, the rule as a random variable, its realised value | series terminology | every inference |
| sampling distribution | The problem | the distribution of a statistic over repeated samples | the post's object | any test or interval |
| standard error (SE) | The problem | the SD of a statistic's sampling distribution; σ/√n for a mean | separates from SD | reporting precision |
| central limit theorem (CLT) | The problem | a limit statement: standardised means tend to N(0, 1) under finite variance | the claim being dated | normal-based methods |
| Monte Carlo simulation, replication R | The problem | repeating a random experiment R times to estimate a property | the instrument | any guarantee check |
| Monte Carlo standard error (MCSE) | The problem | SD of a simulated estimate; √(p(1 − p)/R) for a rate | every simulated number | always |
| seed, stream | Worked example | the start of a pseudo-random sequence; independent sequences per experiment | reproducibility | every simulation |
| skewness γ | Worked example | standardised third central moment | sets the CLT's speed | skewed metrics |
| one-sided t-test, nominal level | Worked example | test of μ = μ0 against one direction at α = 5% | the error measured | alerting, directional claims |
| type I error rate | Worked example | the share of tests rejecting a true null | the guarantee measured | every test |
| sample SD s (divisor n − 1) | Worked example | the estimate of σ | the t's denominator | every t |
| Student's t / degrees of freedom | Student's t | the distribution of (x̄ − μ)/(s/√n) for normal data | corrects for estimated σ | small samples |
| Edgeworth expansion | How fast | a correction to the normal approximation in powers of 1/√n | the γ/√n rate | judging n |
| Cochran's rule | How fast | n > 25γ² for a two-sided 95% interval to cover at least 94% | the best-known skewness rule | survey practice |
| Kolmogorov distance | Berry–Esseen | the largest vertical gap between two CDFs | what Berry–Esseen bounds | normal approximations |
| Berry–Esseen inequality, β3 | Berry–Esseen | a bound C0 β3/√n on that gap | the guaranteed n | worst-case guarantees |
| characteristic function | Berry–Esseen | E e^(itX); inverting it gives the exact CDF | the exact distance | exact computation |
| Cauchy distribution | Never | symmetric, no mean; mean of n draws has the same law | CLT's condition broken | ratios of normals |
| Pareto, tail index α | Never | P(X > x) = x^(−α); variance infinite for α ≤ 2 | slow, non-normal convergence | power-law tails |
| stable law, domain of attraction | Never | the possible limits of normalised sums | why no normal | heavy tails |
| finite population correction | Limitations (E4 in the lab) | √((N − n)/(N − 1)) on the SE when drawing without replacement | the independence condition | sampling a fixed table |

## Handoffs (plain text in the post, no numbers or titles)

- What makes one estimator better than another: later in this series.
- Using the sampling distribution to test and to build intervals: later in this series.
- The bootstrap and skewness-corrected intervals: later in this series.
- Dependent data: a different series (DS-4), named as "time-series methods" without a title.
- Part 1, *Distributions as Generative Stories: Let the Process Pick*, named by title where its populations
  and its log–log material are used.
