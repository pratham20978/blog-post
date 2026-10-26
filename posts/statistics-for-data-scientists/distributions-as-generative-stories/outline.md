# Outline — distributions-as-generative-stories

Series `statistics-for-data-scientists`, Part 1 of 18 (root of the Foundations ladder). Private build file.

## Brief

- **Title:** Distributions as Generative Stories: Let the Process Pick (57 characters; the plan's
  title runs to 67, over the 60-character limit).
- **Answers:** which probability distribution describes my data, and how do I choose it from the
  process that produced the numbers rather than from the histogram's shape?
- **Tier:** L3 (plan). Seven stories, each with a check on real or exactly computable data, a formal
  section and code; the smallest honest worked example (Clarke's table and its binomial origin)
  fills a screen. **Adjacent option:** L4 would add the full CSN fit, which needs likelihood
  (later in this series).
- **Difficulty:** intermediate. Assumes expectation, variance, random variables and NumPy; no
  inference. **Adjacent option:** beginner would mean dropping the mixture integral and Le Cam's
  bound, which carry the post's two corrections.
- **Lab:** G1 · runs anywhere · E1–E4 · access none (probe 2026-10-24 matches `access.md`; RAM
  available rose from 3 to 7 GiB). NumPy 2.5.4 and SciPy 1.18.1 in a uv venv; R 4.5.2 as the
  author's private cross-check.
- **Corrects:** "A straight line on a log–log plot shows a power law."
- **Four-point angle:** reconcile (from-scratch pmfs against SciPy, against Clarke's printed table,
  against Bortkiewicz's printed table, privately against R); condition (constant rate,
  independence, additivity) stated and broken; measure (Monte Carlo with MCSE wherever a
  simulated number appears, exact sums otherwise); read the output (the negative binomial as SciPy,
  statsmodels and R each spell it). Point four is light here by design: Part 1 has no model summary
  table to decode, so it reads parameterisations instead.

## Computed before outlining (lab will reproduce)

- Clarke: Poisson expected equals his printed 226.74/211.39/98.54/30.62/7.14/1.57; chi-square 1.169,
  P 0.883; mean 0.9323, variance 0.9711 (n − 1), ratio 1.04; binomial and Poisson differ by 0.55
  squares in total (TV 4.8e-4, Le Cam bound 1.6e-3).
- Bortkiewicz: 200 corps-years mean 0.61, variance 0.611; 280 corps-years mean 0.70, variance 0.763.
- G&Y: mean 0.4652, variance 0.6919, ratio 1.49; Poisson chi-square 103.1; NB moments k 0.955,
  chi-square 4.2; top 20% of women carry 53% of expected accidents.
- t5 (unit variance): 56.4 times the normal beyond 4 sigma; peak 0.490 against 0.399 (so the body
  is *not* identical — the post says so); at n = 100, 70% of t5 samples show no point beyond 4.
- Lognormal: top 10% of 10,000 draws gives R² 0.989 on log–log axes at any sigma.
- Coal: pooled gap CV 1.47; 1851–1889 gaps CV about 1.06.

## Sections and budget

Validator words, which count decimals twice. Target 6,300 prose + ~900 references.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 230 | state the answer | — | L04, L16 |
| Why this matters | 220 | see what a wrong family costs (SEs, tail risk) | — | L16 |
| The problem | 430 | state the choice precisely and why the histogram cannot make it | — | L23, L35 |
| Worked example (Clarke; Bortkiewicz) | 950 | derive Poisson counts from a story and check them | FIG_02 | L01–L08, L10–L14, L29, L41 |
| Intuition | 380 | separate "story predicts family" from "family proves story" | FIG_01 | L17–L23 |
| What do waiting times, sums and products produce? | 700 | write the story for gaps, sums and products | FIG_03, FIG_04 | L28, L30, L31, L47 |
| Why do accident counts break the Poisson? | 950 | derive and fit the NB as a gamma mixture, and say what it cannot prove | FIG_05, FIG_06 | L16–L22, L24, L25 |
| What can't a histogram show? | 500 | quantify a tail the body hides | FIG_07, FIG_08 | L26 |
| Is a straight line on a log–log plot a power law? | 620 | refuse the log–log argument and name the procedure | FIG_09, FIG_10 | L32–L40, L48 |
| The math | 620 | the derivations with symbols, and the parameterisation map | — | L25, L29, L42–L46 |
| Implementation | 400 | compute expected counts and the moment fit, and map to SciPy | — | L42 |
| Limitations and common mistakes | 380 | avoid the five mistakes | — | L09, L11, L24, L27 |
| Key takeaways | 130 | carry five claims | — | — |
| Try it yourself | 230 | E1, E3 from the article | — | — |
| References | ~900 | — | — | — |

## Figure plan (route gate run per figure)

| Fig | Section | One thing it says | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 01 | Intuition | each family is the end of a process; mixing a rate or a variance fattens it | mermaid | Q3: 11 nodes with labelled edges, branches cross between the count and continuous families | The process decides the family; each arrow is the operation that turns one story into the next |
| 02 | Worked example | Clarke's squares and Bortkiewicz's corps sit on the Poisson curve | chart | Q1: published counts (L04, L12) against fitted expectations from the lab | Hanging rootograms: every bar ends within Tukey's ±1 band |
| 03 | Waiting times | the exponential needs one constant rate; the coal record has two | chart | Q1: real dates (L47) with gaps measured by the lab | Pooled gaps are too often long; within 1851–1889 they are close to exponential |
| 04 | Sums and products | the same twelve effects added make a normal, multiplied make a lognormal | plot | Q4: simulated distributions from one set of factors, a construction | Only the combination rule changed |
| 05 | Accidents | the Poisson misses both ends of Greenwood and Yule's table; the NB fits | chart | Q1: published counts (L16) against two fitted models | Too many zeros and too many threes: the Poisson's signature failure |
| 06 | Accidents | the fitted gamma: most women below the mean, a few carry half the accidents | plot | Q4: a density curve with shaded shares, a model | What the mixture says about the 647 women |
| 07 | Tails | t5 and the normal differ by 56 times beyond 4 sigma | plot | Q4: exact curves on a log scale | The tail ratio grows faster than either tail shrinks |
| 08 | Tails | a Q–Q plot shows what a histogram hides, at n = 1,000 | plot | Q4: simulated samples against normal quantiles | The ends bend for t5 and not for the normal |
| 09 | Log–log | a lognormal sample draws a straight tail with R² 0.99 | plot | Q4: simulated CCDFs on log–log axes | A straight line the lognormal drew |
| 10 | Log–log | one rule (a floor) turns the lognormal into a power law | plot | Q4: exact distributions of Champernowne's process with and without a floor | The process decides what the plot cannot |
| Cover | — | Clarke's grid as a field of counts, Poisson curve over it | placed | template cover in the series house style; no external generator | — |

Source-route check: CSN Fig. 4.1a, K&Z Fig. 1, Limpert Fig. 2 and Böhning Fig. 3 are directly
relevant but not rights-cleared (ledger F1–F3, F5); Bortkiewicz's p. 24 is public domain but in
German and carries no comparison (F4). All figures are our own analysis from the lab.

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| generative story | The problem | a step-by-step account of how one observation came to be, precise enough to simulate | the post's method | every time a family is chosen |
| probability distribution / family | The problem | a rule giving each value its probability; a family is the set indexed by parameters | the object being chosen | — |
| Bernoulli trial | Worked example | one yes/no event with probability p | the bomb-lands-in-square event | building counts |
| binomial | Worked example | count of successes in n independent trials with common p | each square's count | fixed n, common p |
| Poisson distribution | Worked example | counts with P(k) = e^{-λ}λ^k/k!, variance = mean | the rare-event limit | many rare independent chances |
| dispersion index (variance-to-mean ratio) | Worked example | s²/x̄; 1 for a Poisson | the story's first testable prediction | before any count model |
| rootogram (hanging) | Worked example | bars of √observed hung from √expected | compares a fit at every count | after any count fit |
| total variation distance | Worked example | half the summed absolute difference of two pmfs | how far binomial is from Poisson | judging an approximation |
| Le Cam's inequality | Worked example | TV ≤ Σp² | puts a number on "rare" | before using a Poisson for counts |
| Poisson process | Waiting times | events at a constant rate, independently in disjoint intervals | links counts and gaps | arrivals in time |
| exponential distribution | Waiting times | gap between Poisson events; memoryless; CV = 1 | the story's prediction for gaps | inter-event times |
| gamma distribution | Waiting times | time to the k-th event; shape k, rate λ | waiting times, and later the rate mixture | k-th arrival; rate heterogeneity |
| coefficient of variation (CV) | Waiting times | sd/mean | tests the exponential story | gaps |
| central limit theorem (CLT) | Sums | sums of many small independent effects tend to the normal | the normal's story | additive effects |
| lognormal | Products | log X is normal; products of many small effects | the product story | multiplicative growth |
| overdispersion | Accidents | variance above the Poisson's mean | G&Y's signature | count data |
| negative binomial (μ, k) | Accidents | Poisson whose rate is gamma distributed; Var = μ + μ²/k | the heterogeneity story | overdispersed counts |
| mixture distribution | Accidents | draw a parameter, then the data given it | names the move | heterogeneity |
| law of total variance | Accidents | Var Y = E Var(Y given λ) + Var E(Y given λ) | splits μ and μ²/k | reading overdispersion |
| method of moments | Accidents | set model moments equal to sample moments | Part 1's only fitting tool | before likelihood (later in the series) |
| contagion (true / false) | Accidents | accidents raising later chances / proneness that only looks like it | the NB's rival story | one-period counts |
| Student's t (unit variance) | Tails | normal with random variance; scaled to variance 1 | the tail story | heavy-tailed measurements |
| Q–Q plot | Tails | sorted data against a family's quantiles | shows tails | after any continuous fit |
| complementary CDF (CCDF) | Log–log | P(X ≥ x) | what log–log plots draw | heavy-tail claims |
| power law (Pareto) | Log–log | P(X ≥ x) ∝ x^{-α} above xmin | the claim being corrected | heavy-tail claims |
| Monte Carlo standard error (MCSE) | IMPORTANT notice / tails | sd of a simulated estimate, √(p(1−p)/R) for a share | every simulated number | always |

## Handoffs (plain text in the post, no numbers)

- How a statistic computed from these data varies: later in this series.
- Fitting by maximum likelihood, the formal Poisson-versus-NB test, and running the CSN procedure:
  later in this series.
- Count regression with covariates: later in this series.
