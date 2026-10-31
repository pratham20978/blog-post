# Outline — confidence-intervals-coverage

Series `statistics-for-data-scientists`, Part 6 of 18 (Tests and intervals arc; parent: Part 5). Private build file.

## Brief

- **Title:** Confidence Intervals: What 95% Means, Measured (47 characters; the plan's title).
- **Answers:** what does a 95% confidence interval promise, how do I check that an interval keeps the promise, and
  which interval should I use for a proportion?
- **Tier:** L3 (plan). Five things to learn: coverage as a property of the procedure, computed exactly; the interval
  as an inverted test; five intervals for a proportion and their exact coverage and length; the overlap rule;
  coverage of the t-interval on skewed data, including coverage given the interval's width. The worked example
  (20 audited predictions, 21 outcomes) is summed by hand. **Adjacent option:** L4 would add the difference of two
  proportions (Newcombe's intervals) and the mid-p interval; L2 would drop the overlap rule and the t-interval.
- **Difficulty:** advanced. Assumes Part 5's tests, α and p-values, and Part 2's t statistic and spend population.
  **Adjacent option:** intermediate would drop the incomplete-beta averages and the relevant-subset argument.
- **Lab:** G1 · runs anywhere · E1–E4 · access none. Probe 2026-10-31 matches `access.md` (RAM available 4 GiB; the
  lab peaks at 0.28 GB). The series venv (NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0) is reused unchanged; the
  lab needs no pandas. R 4.5.2, base only, is the private check (`binom.test`, `prop.test`, `poisson.test`).
- **Corrects:** "There is a 95% probability the true value is inside this interval."
- **Four-point angle:** reconcile (five intervals against statsmodels, SciPy and R; Agresti and Coull's Table 1;
  all 16 of the trial's Clopper–Pearson rows); condition (coverage at every p, not on average; n ≥ 30 and np ≥ 5
  are not conditions; skewness breaks the t-interval); measure (exact coverage sums, simulated coverage with MCSE);
  read the output (statsmodels' default `method="normal"` is the Wald interval; two definitions of a two-sided
  exact p-value).

## Settled at research

- The trial prints two 95% intervals for VE 95.0%: 90.3–97.6 (Table 2, credible, beta-binomial with prior
  beta(0.700102, 1)) and 90.0–97.9 (Table 3, Clopper–Pearson adjusted for surveillance time). The FDA briefing
  reads the credible one as a 97.5% probability that VE is at least 90.3%. That is the hook.
- The lab reproduces 90.0–97.9 exactly; 9 of the 16 published Clopper–Pearson rows to every digit and all 16 within
  the rounding of three-decimal surveillance times. FDA Table 12's severe split (1 vs 9, 88.9 with 20.1–99.7)
  reproduces exactly and becomes the real-data overlap case.
- Brown, Cai and DasGupta could be read only as an abstract (Project Euclid, Penn, CiteSeerX and the Wayback
  Machine all failed): the article quotes only the abstract and reproduces the oscillation by exact computation.
  Agresti and Coull were read in full: all 15 means in their Table 1 reproduce; their RMSE column reproduces in 9 of
  15 cells (largest gap 0.0021) and is not quoted.
- Hoekstra et al. 2014 could not be read (403s, elided abstract); its design and averages come from two CC BY
  papers (García-Pérez and Alcalá-Quintana 2016; Morey et al.'s reply to Miller and Ulrich), which also carry the
  dispute.
- The t-interval on Part 2's spend covers 65.8% at n = 30 and 93.8% at 10,000 (Part 2's 93.9% agrees); the new
  result is coverage by width: 0% for the narrowest tenth at n = 30. The normal comparison is our own derivation
  (Brown 1967 on the conditional level of the t-test has no readable abstract and is not cited).

## Sections and budget

Validator words (decimals count twice; References add about 1,100). Target about 5,700 prose.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 250 | state the answer | — | — |
| Why this matters | 190 | see two 95% intervals for one efficacy, and which sentence each supports | — | L01–L03 |
| The problem | 380 | define coverage, nominal and actual, the confidence coefficient, test inversion; state the claim | — | L04–L06 |
| Worked example | 560 | sum the exact coverage of three intervals for 20 audited predictions by hand | FIG_01 | — |
| Intuition | 200 | picture a procedure's hit rate, and where the analogy breaks | — | — |
| What does a 95% interval promise? | 560 | read an interval as inverted tests; know the misreading and the dispute over measuring it | FIG_02 | L04, L07–L11 |
| Which interval should you use for a proportion? | 820 | choose among five intervals from exact coverage curves, the n-oscillation and the price in width | FIG_03–FIG_05 | L12–L19 |
| What does a real low-count trial give? | 520 | turn a case split into an efficacy interval and check it against all published rows | FIG_06 | L01, L02, L20–L22 |
| Do overlapping intervals mean no difference? | 560 | judge a difference from two intervals, and when the overlap rule misleads | FIG_07, FIG_08 | L23–L28 |
| Does the t-interval keep its promise on skewed data? | 470 | measure t-interval coverage on a skewed population and distrust its narrow intervals | FIG_09, FIG_10 | L29, L30 |
| The math | 420 | the formulas, each with the worked numbers | — | L12, L23 |
| Implementation | 330 | compute exact coverage; map library names and defaults; read exact p-values | — | L31–L33 |
| Limitations and common mistakes | 330 | avoid seven mistakes | — | — |
| Key takeaways | 170 | carry five claims | — | — |
| Try it yourself | 200 | E1 and E3 from the article | — | — |
| References | ~1,100 | — | — | — |

## Figure plan

| # | Section | One thing it communicates | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | coverage at one p is the probability of the outcomes whose interval contains p: Wald x = 1..6, Wilson 0..4, Clopper–Pearson 0..5 | plot | Q4: intervals for every outcome drawn to scale beside their probabilities | Coverage is a sum over outcomes |
| 2 | Promise | an interval is the set of null values a 5% test keeps: three p-value functions for 2 of 20 and their 0.05 crossings | plot | Q4: three computed curves cut by a threshold | Each interval is where its test's p-value stays above 0.05 |
| 3 | Which interval | exact coverage against p at n = 50 for five intervals | plot | Q1: five computed curves, small multiples on one scale | Only Clopper–Pearson stays above 95% everywhere |
| 4 | Which interval | the Wald interval's coverage at p = 0.1 as n runs 10 to 1,000, beside Wilson | plot | Q1: a computed sawtooth on a log axis | One more observation can cost 14 points |
| 5 | Which interval | mean coverage and mean width over a uniform p against n, with Agresti and Coull's printed means | plot | Q1: computed curves with published points | Coverage costs width; Wald's shortfall buys almost none |
| 6 | Real trial | efficacy intervals from 8 of 170 by five methods beside the published credible interval; coverage at n = 170 | plot | Q1: computed intervals and curves from published counts | The published 90.0–97.9 reproduced; how each method covers at this size |
| 7 | Overlap | the overlap rule's error rate against the SE ratio, and its power at an 80% design | plot | Q4: geometry plus computed curves | Two 95% intervals overlap more than 99% of the time when there is no difference |
| 8 | Overlap | the severe split: arm rates with exact intervals overlapping, and the efficacy interval excluding 0 | plot | Q1: published counts, computed intervals | Overlapping intervals, significant difference |
| 9 | t-interval | coverage of the t-interval on the spend against n, split by side of the miss | plot | Q1: simulated rates with MCSE on a log axis | Two in three at n = 30, and nearly every miss below the mean |
| 10 | t-interval | coverage by tenth of interval width at n = 30: spend against normal | plot | Q1: simulated and exact rates, ten bars each | The narrow intervals are the ones that miss |
| cover | — | Figure 3's argument: a jagged Wald coverage curve beside a steady exact interval | placed | template cover in the series house layout | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| confidence interval (procedure), endpoints L(X), U(X) | The problem | a rule that turns data into an interval; random before the data | the object whose promise is measured | every interval |
| coverage probability, nominal and actual coverage | The problem | P(L ≤ θ ≤ U) at a fixed θ; the level in the name against what the rule delivers | the promise, stated so it can be checked | choosing a method |
| confidence coefficient | The problem | the smallest coverage over all θ | Neyman's definition; exact intervals guarantee it | when every θ must be covered |
| test inversion | The problem / Promise | the interval as the null values a test does not reject | links Part 5's tests to intervals | reading any interval |
| Wald, score (Wilson), Agresti–Coull, Clopper–Pearson, Jeffreys | Worked example / Which interval | five 95% intervals for a proportion | the candidates compared | proportions, rates |
| conservative interval | Which interval | coverage at or above nominal everywhere, usually above | Clopper–Pearson's price | regulated settings |
| p-value function | Promise | the two-sided p-value as a function of the null value | shows inversion | reading an interval's shape |
| credible interval | Why this matters | a posterior probability interval, given a prior | the statement readers want | a later part |
| vaccine efficacy, incidence rate ratio, surveillance time | Real trial | 1 − IRR; ratio of case rates; person-years at risk | the trial's estimand and its exposure | rates with exposure |
| conditional binomial (case split) | Real trial | given the total cases, the vaccine count is binomial | turns a rate ratio into a proportion | two Poisson counts |
| overlap rule, SE ratio | Overlap | "no overlap means significant"; ratio of the two standard errors | the common misreading and its error rate | figures with error bars |
| relevant subset, conditional coverage | t-interval | coverage among intervals the data can pick out, here by width | the overall 95% need not apply to yours | skewed data, any interval |
| Monte Carlo standard error (MCSE) | (Part 2) | the standard error of a simulated rate | every simulated number | always |
