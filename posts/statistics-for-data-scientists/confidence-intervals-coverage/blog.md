---
title: "Confidence Intervals: What 95% Means, Measured"
slug: confidence-intervals-coverage
date: 2026-10-31
updated: 2026-10-31
summary: "A 95% confidence interval promises coverage across repetitions, not a 95% chance for yours. Exact sums show the Wald interval covering 87.6% at n = 20."
tags: [data-science, statistics, confidence-interval, coverage-probability, binomial-proportion, wilson-interval, clopper-pearson]
category: data-science
series: statistics-for-data-scientists
series_position: 6
tier: L3
difficulty: advanced
prerequisites: ["hypothesis tests, α and p-values", "the t statistic and the standard error", "Python with NumPy and SciPy"]
reading_minutes: 31
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/confidence-intervals-coverage"
---

![Two coverage curves for 95% intervals at n = 50: the Wald interval's jagged and far below 95%, Clopper–Pearson's never below it](COVER)

> [!NOTE]
> **Insights** — A 95% confidence interval comes from a procedure that contains the true value in 95% of repetitions, whatever that value is; the interval you computed either contains it or does not, and a 95% probability for it needs a prior. Whether a procedure keeps its promise can be measured, and for a proportion computed exactly: with 20 trials and a true rate of 10%, the textbook Wald interval covers 87.6% of the time, the Wilson interval 95.7% and the Clopper–Pearson interval 98.9%. On heavily skewed customer spend, the 95% t-interval for the mean covers 65.8% at n = 30, and its narrowest intervals almost never contain the mean.

**Level:** advanced · **You need:** hypothesis tests, α and p-values; the t statistic; Python with NumPy and SciPy · **Time:** ~31 min

**Jump to:** [worked example](#worked-example) · [the promise](#what-does-a-95-interval-promise) · [choosing an interval](#which-interval-should-you-use-for-a-proportion) · [a real trial](#what-does-a-real-low-count-trial-give) · [overlap](#do-overlapping-intervals-mean-no-difference) · [the t-interval](#does-the-t-interval-keep-its-promise-on-skewed-data) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **computed** or **measured** come from its lab: one NumPy, SciPy and statsmodels script that runs in about 20 seconds and is seeded, so every number repeats exactly. The coverage of an interval for a proportion is computed exactly, by summing over every possible outcome; each simulated quantity is printed as an estimate ± its Monte Carlo standard error (MCSE). Published numbers are **quoted**, and the lab recomputes each one before it is used.

## Why this matters

The *New England Journal of Medicine* report of the Pfizer–BioNTech vaccine trial gives one efficacy, 95.0%, with two different 95% intervals. Among participants without prior infection there were 8 cases of Covid-19 in the vaccine group and 162 in the placebo group; Table 2 gives the interval as 90.3% to 97.6%, a Bayesian **credible interval**, and Table 3 as 90.0% to 97.9%, a confidence interval by the Clopper–Pearson method. <!-- L01 --> <!-- L02 --> The FDA's briefing document reads the first as a 97.5% probability that the true efficacy is at least 90.3%. <!-- L03 --> That sentence is right for the credible interval and wrong for the confidence interval, and it is the sentence most readers attach to every 95% interval they meet. A confidence interval makes a different promise, and some intervals keep it far better than others.

## The problem

A **confidence interval** is a procedure before it is a pair of numbers: a rule that turns the data X into two endpoints, L(X) and U(X). Before the data arrive the endpoints are random. The interval's **coverage probability** at a parameter value θ is the probability that it contains θ when θ is the truth. Neyman, who laid the theory's formal foundation in 1937, asked that the coverage reach the stated level, here 95%, for every possible value of the parameter. <!-- L04 --> The stated level is the **nominal coverage**; what the rule delivers at a given θ is its **actual coverage**; and the smallest actual coverage over all θ is the procedure's **confidence coefficient**. <!-- L05 -->

The fifth part of this series, *p-Values and Power: How Wrong Can a Significant Result Be?*, built the other half. A 5% test rejects a true null 5% of the time, and the two objects are one: the null values θ₀ that a 5% two-sided test does not reject form a 95% confidence interval, whose coverage at the true value is the test's 95% rate of not rejecting it. The textbook interval for a proportion inverts the Wald test, the Wilson interval inverts the score test of the fourth part, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, and the Clopper–Pearson interval inverts a pair of exact binomial tests. <!-- L06 -->

Two things make the promise hard to keep. Most intervals rest on a normal approximation, so their actual coverage only approaches 95% as n grows. And counts are discrete: a binomial X with n trials takes n + 1 values, so the coverage at a given p is a sum of a few binomial probabilities, which jumps as p or n changes. No interval for a proportion sits at exactly 95% for every p. This part measures how far each falls from it, and tests the claim **"there is a 95% probability that the true value is inside this interval."**

## Worked example

Suppose a classifier's true error rate is p = 0.1 and you hand-label 20 of its predictions to estimate it. The number of errors X is binomial with n = 20, so each outcome has a known probability: P(X = 0) = 0.1216, P(X = 1) = 0.2702, P(X = 2) = 0.2852, then 0.1901, 0.0898, 0.0319 and 0.0089 for 3 to 6 errors, 0.0020 for 7, and 0.0004 for 8 or more together.

**The textbook interval.** The Wald interval is p̂ ± 1.96 √(p̂(1 − p̂)/n), with p̂ = X/20. Run it on every outcome:

- X = 0 gives p̂ = 0 and a standard error of 0, so the interval is the single point 0. It misses 0.1.
- X = 1 gives 0.05 ± 1.96 × 0.0487, from −0.046 to 0.146. It contains 0.1, and so do the intervals for X = 2 to 5.
- X = 6 gives 0.30 ± 0.201, from 0.099 to 0.501, which contains 0.1 by a thousandth.
- X = 7 gives 0.141 to 0.559, and every larger X lies further right. They miss.

The interval contains the truth exactly when X is between 1 and 6, so its coverage is the probability of those outcomes: 0.2702 + 0.2852 + 0.1901 + 0.0898 + 0.0319 + 0.0089 = 0.8760. A procedure labelled 95% delivers 87.6% here. It misses 12.4% of the time, 12.2 points of that on the outcome with no errors, whose interval has zero width.

**Two others.** The Wilson interval contains 0.1 for X = 0 to 4: at X = 0 it runs from 0 to 0.161, and at X = 5 its lower end, 0.112, has passed 0.1. Its coverage is 0.1216 + 0.2702 + 0.2852 + 0.1901 + 0.0898 = 0.9568. The Clopper–Pearson interval still contains 0.1 at X = 5, where its lower end is 0.087, and stops at X = 6, where it is 0.119, so its coverage is 0.9568 + 0.0319 = 0.9887. Figure 1 draws each outcome's intervals beside its probability.

![Wald, Wilson and Clopper–Pearson intervals for each count of errors in 20 audits beside each count's probability; coverage 87.6%, 95.7%, 98.9%](FIG_01)
*Figure 1. Coverage at one p is the probability of the outcomes whose interval contains p. The Wald interval loses the zero-error audit, which happens 12% of the time.*

Nothing here was simulated. Simulation measures the same quantity with an error bar: a million simulated audits give 87.57% ± 0.03 for the Wald interval, 95.68% ± 0.02 for Wilson and 98.89% ± 0.01 for Clopper–Pearson, each within 1.3 MCSEs of the exact sum. When the outcomes can be listed, the exact sum is the better instrument; the t-interval at the end of this part needs simulation because they cannot.

## Intuition

Think of a confidence procedure as a machine that stamps intervals out of data, with 95% as its quality specification: run it again and again on the same truth, and 95% of what it produces contains that truth. The specification describes the machine, not any one interval. A given interval either contains the truth or does not, and inspecting it does not tell you which. For counts the machine's hit rate depends on the truth itself, so a specification can hold only as a floor, as it does for Clopper–Pearson, or on average, as for Wilson.

The analogy breaks in one place. A defective unit can look exactly like a good one, but an interval's own data sometimes reveal which runs went wrong. The last section shows a case where the narrowest intervals almost never contain the truth, so the machine's 95% is the wrong number for the interval in your hand.

## What does a 95% interval promise?

Figure 2 shows the inversion for an audit that found X = 2 errors in 20. Each curve is a test's two-sided p-value for the null p = p₀, plotted against p₀; the 95% interval is the range of p₀ where the curve stays at or above 0.05. The Wald test computes the standard error at p̂, so its curve is symmetric about p̂ = 0.1 and crosses 0.05 at −0.031 and 0.231, a lower limit below zero. The score test computes the standard error at p₀ and crosses at 0.028 and 0.301, the Wilson formula's endpoints to within 6 × 10⁻¹⁶. The exact test, twice the smaller binomial tail, crosses at 0.012 and 0.317, the Clopper–Pearson endpoints.

![Two-sided p-value against the null value for 2 errors in 20: Wald, score and exact tests, each crossing 0.05 at its interval's endpoints](FIG_02)
*Figure 2. An interval is the set of null values its test keeps. The Wald curve is symmetric about 0.1 and its interval runs below zero; the other two tests keep only proportions that are possible.*

The same picture explains the Wald interval's zero width at X = 0. With p̂ = 0 its standard error is 0, so its test rejects every p₀ above 0 and keeps only p₀ = 0; the score test, with the standard error at p₀, still keeps every p₀ up to 0.161.

What the interval does not promise is a probability about the computed range. Neyman was explicit that once the sample is drawn and the interval computed, the probability that this interval contains the true value is not the confidence level. <!-- L04 --> Greenland and colleagues list "the specific 95% interval has a 95% chance of containing the true effect" among the common misinterpretations: an observed interval contains the true value or does not, and the 95% describes how often intervals from many studies would contain it if the assumptions held. <!-- L07 -->

The misreading is common, though how common is disputed. Hoekstra and colleagues gave a reported 95% interval of 0.1 to 0.4 for a mean to 442 first-year psychology students, 34 master's students and 118 researchers, with six statements to mark true or false, all of which the authors considered false; one was that there is a 95% probability that the true mean lies between 0.1 and 0.4. The three groups endorsed 3.51, 3.24 and 3.45 of the six on average. <!-- L08 --> Miller and Ulrich argued that respondents could have read some statements in a correct way, and García-Pérez and Alcalá-Quintana that a questionnaire whose items are all false, with every item to be answered, cannot separate misunderstanding from confusion. <!-- L09 --> <!-- L10 --> Morey and colleagues replied that the answers were inconsistent under any reading: of the non-students who endorsed the 95%-probability statement, only 51% endorsed a weaker one that follows from it. <!-- L09 -->

The statement readers want, a probability that the parameter lies in a range given the data, requires a prior distribution, and the interval it produces is a credible interval. <!-- L07 --> <!-- L11 --> The trial's 90.3% to 97.6% is one; a later part of this series reproduces it from the trial's prior.

## Which interval should you use for a proportion?

Five intervals cover most practice. The **Wald** interval is the textbook form above. The **Wilson** interval inverts the score test; its centre is (X + z²/2)/(n + z²), pulled from p̂ toward ½. <!-- L06 --> The **Agresti–Coull** interval puts the Wald form around that centre, which at 95% is close to adding two successes and two failures before computing p̂. <!-- L16 --> The **Clopper–Pearson** interval inverts two one-sided exact binomial tests, each at 2.5%, and is guaranteed to cover at least 95% at every p. <!-- L13 --> The **Jeffreys** interval takes the 2.5% and 97.5% quantiles of a Beta(X + ½, n − X + ½) distribution, a Bayesian posterior used here as a frequentist procedure and judged by its coverage. <!-- L14 --> <!-- L31 -->

Figure 3 sums each one's exact coverage at n = 50, for every p from 0.001 to 0.999.

![Exact coverage of five 95% intervals against p at n = 50: Wald far below 95% for 40% of p, Clopper–Pearson never below 95%](FIG_03)
*Figure 3. Only Clopper–Pearson stays above 95% everywhere, and it is above 96% for 83% of p. Wilson and Jeffreys hover near 95% with dips at the edges; the Wald interval does not hover at all.*

The Wald interval covers less than 93% for 40% of the values of p, and near 0 and 1 its coverage falls toward zero. Wilson's coverage stays close to 95% except for dips at the edges, to 83.9% at p = 0.0035; Agresti and Coull showed that this dip, at np of about 0.18, does not close as n grows, with a limit of 0.838, and the lab finds 0.8387 at n = 10,000. <!-- L15 --> Jeffreys dips to 88.4% at the edges, Agresti–Coull never goes below 93.45%, and Clopper–Pearson never below 95.08%.

A large sample does not rescue the Wald interval. Brown, Cai and DasGupta showed that its erratic coverage is far more persistent than is generally appreciated, and that textbook rules for when it is safe are misleading. <!-- L14 --> Figure 4 fixes p = 0.1 and lets n grow.

![The Wald interval's coverage at p = 0.1 for n from 10 to 1,000, zigzagging between 81% and 95%, beside the Wilson interval's steadier curve](FIG_04)
*Figure 4. One more audit can cost 14 points: coverage falls from 94.7% at n = 29 to 80.9% at n = 30. At n = 50, where np = 5 and the rule of thumb says the approximation is fine, it is 87.9%.*

Coverage zigzags because the set of outcomes whose interval contains 0.1 changes one outcome at a time as n grows. The common rule, np ≥ 5 and n(1 − p) ≥ 5, admits coverage as low as 85.4% (at n = 12 and p = 0.5) for n up to 300, and at p = 0.1 the Wald interval is still below 94% for 22% of the sample sizes from 10 to 1,000. Wilson's coverage at the same p stays between 92.0% and 98.1%.

Averaging over p shows the trade-off between coverage and width (Figure 5). Agresti and Coull summarized each interval by its mean coverage when p is spread uniformly from 0 to 1. <!-- L12 --> The average can be computed exactly, because each outcome's binomial probability integrates to an incomplete beta function, and all 15 mean coverages in their Table 1 reproduce to the printed three decimals: the Wald interval's rises from 0.641 at n = 5 to 0.922 at n = 100, Clopper–Pearson's falls from 0.990 to 0.965, and Wilson's stays between 0.955 and 0.951. <!-- L12 -->

![Mean coverage and mean width over a uniform p against n for five intervals, with Agresti and Coull's printed means as rings](FIG_05)
*Figure 5. Clopper–Pearson buys its floor with width; the Wald interval's missing coverage buys almost none. Rings: Agresti and Coull's Table 1.*

At n = 50 the Clopper–Pearson interval is 8.3% wider than Wilson's on average, for a mean coverage of 96.9% against 95.2%. The Wald interval is only 0.8% narrower than Wilson's: as Agresti and Coull put it, the Wald interval does not fail by being short, it fails by centring on p̂ when the binomial is skewed. <!-- L17 --> Thulin measured the price of exactness as extra expected length, and as the extra sample size needed to buy it back. <!-- L18 -->

The choice follows. Brown, Cai and DasGupta recommend the Wilson or Jeffreys interval for small n and the Agresti–Coull interval for larger n. <!-- L14 --> Use Clopper–Pearson, the method behind the vaccine trial's subgroup intervals, when coverage below 95% is unacceptable at any p, and accept an interval a few percent wider. <!-- L02 --> Do not use the Wald interval for a proportion.

## What does a real low-count trial give?

The vaccine trial's estimand is **vaccine efficacy**, VE = 1 − IRR, where the **incidence rate ratio** IRR is the rate of cases per 1,000 person-years in the vaccine group over the rate in the placebo group. <!-- L20 --> A rate needs exposure, the **surveillance time** each group was followed: 2.214 thousand person-years for the vaccine group and 2.222 for placebo. <!-- L02 --> So VE = 1 − (8/2.214)/(162/2.222) = 95.0%.

A rate ratio becomes a proportion by conditioning on the total. Treat each group's cases as Poisson counts. Given that 170 cases occurred, the number in the vaccine group is binomial with n = 170 and a share π = IRR·r/(IRR·r + 1), where r = 2.214/2.222 is the ratio of surveillance times. Any interval for π therefore maps to one for VE, through IRR = π/((1 − π)r). For π̂ = 8/170 = 0.047, the Clopper–Pearson interval runs from 0.0205 to 0.0906, and the map gives VE from 90.0% to 97.9%: the trial's Table 3, to the digit. <!-- L02 --> The paper prints 14 more rows by subgroup and the FDA briefing one for severe disease. The lab recomputes all 16: 9 match every printed digit, and the other 7 differ by 0.1 to 0.3 points, each within what surveillance times printed to three decimals allow. <!-- L02 --> <!-- L22 -->

![Vaccine efficacy intervals from 8 of 170 cases by five methods beside the published credible interval, and each method's exact coverage at n = 170](FIG_06)
*Figure 6. The published 90.0% to 97.9% is the Clopper–Pearson interval, reproduced. At this size every method but Wald has a mean coverage within two points of 95%; only Clopper–Pearson never falls below it.*

The other four methods give 91.4% to 98.4% (Wald), 90.1% to 97.5% (Wilson), 89.9% to 97.7% (Agresti–Coull) and 90.5% to 97.7% (Jeffreys). The Wald interval is the outlier. Symmetric around 0.047 on the share scale, it puts the share's upper limit too low, so it overstates the lower limit of efficacy by 1.4 points. Its coverage at n = 170 shows why: for true shares between 0.01 and 0.12 it falls as low as 79.6%, while Wilson's never falls below 93.0% and Clopper–Pearson's below 95.2% (Figure 6).

The trial's prespecified analysis produced the other interval. A beta-binomial model with prior beta(0.700102, 1) on the share, adjusted for surveillance time, gave the credible interval of 90.3% to 97.6% and the posterior probability that efficacy exceeds 30%, the trial's success criterion. <!-- L21 --> Here the two intervals differ by at most 0.3 points, and they still answer different questions. The confidence interval says that the procedure behind it contains the true efficacy in at least 95% of repetitions; only the credible interval licenses the FDA's sentence about this efficacy.

## Do overlapping intervals mean no difference?

A common shortcut reads a difference off two intervals: if the 95% intervals do not overlap, the difference is significant, and if they overlap, it is not. Schenker and Gentleman showed that the first half holds and the second does not. Non-overlap implies that the standard test rejects, but overlap does not imply that it does not, so the rule rejects less often than a 5% test when there is no difference and misses more real differences when there is one. <!-- L23 -->

The geometry is short. Take two independent estimates with equal standard errors s. Their 95% intervals fail to overlap when the estimates differ by more than 2 × 1.96s = 3.92s, but the difference has standard error √2 s, so a 5% test rejects beyond 1.96 × √2 s = 2.77s. Between 2.77s and 3.92s the intervals overlap and the difference is significant; at the threshold of significance they overlap by 2 − √2 = 59% of one arm. Used as a test, the overlap rule's type I error rate is 0.56% at equal standard errors, 0.85% when one standard error is twice the other, and rises toward 5% as the ratio grows (Figure 7). Payton, Greenstone and Schenker restate the formula and note that 95% intervals overlap more than 99% of the time when there is no difference. <!-- L23 --> <!-- L24 -->

![The overlap rule's type I error against the ratio of standard errors, from 0.56% at 1 toward 5%, and its power against the standard test's](FIG_07)
*Figure 7. Read as a test, "no overlap" is a 0.56% test with equal standard errors. Where the standard test has 80% power, it has 51%.*

The price is power. A design with 80% power for the standard test has 51% under the overlap rule. In the lab's simulation of two groups of 10 with t-intervals, the t-test rejects 4.99% ± 0.05 of the time when there is no difference and the 95% intervals fail to overlap 0.57% ± 0.02 of the time; with a true difference of 1.32 standard deviations, the rates are 80.0% ± 0.09 and 44.9% ± 0.11. Narrower intervals restore the 5%: at equal standard errors, non-overlap of 83.4% intervals is a 5% test, 4.97% ± 0.05 and 79.85% ± 0.09 in the same simulation. That is the 83–84% rule Payton and colleagues give, after an analogous result for means by Goldstein and Healy. <!-- L24 --> <!-- L25 -->

Cumming's rules of eye for two independent 95% intervals, each from at least 10 observations and with widths within a factor of two: intervals that just touch mean p of about 0.01, and an overlap of half an arm about 0.05. <!-- L26 --> The exact values with known standard errors are smaller, 0.0056 and 0.038 when the standard errors are equal. Greenland and colleagues give an example of substantial overlap with a significant difference, (1.04, 4.96) against (4.16, 19.84) with P = 0.03; the lab gets 0.029. <!-- L27 --> Researchers misjudge such pictures: of 473 authors who moved two means with error bars until they judged them just significantly different, many showed severe misconceptions about how error bars relate to significance. <!-- L28 -->

The trial has a real case. After the first dose, 10 participants had severe Covid-19: 1 in the vaccine group over 4.021 thousand person-years, and 9 in the placebo group over 4.006. <!-- L22 --> Each group's rate has an exact Poisson interval, from χ² quantiles: <!-- L34 --> 0.25 cases per 1,000 person-years, from 0.006 to 1.39, against 2.25, from 1.03 to 4.26 (Figure 8). The intervals overlap from 1.03 to 1.39. The test of the difference, an exact binomial test on the 1-to-9 split, gives p = 0.021, and the efficacy interval of 20.1% to 99.7% excludes zero, as the FDA briefing reports. <!-- L22 -->

![Severe Covid-19 rates with exact 95% intervals: vaccine 0.25 (0.006 to 1.39), placebo 2.25 (1.03 to 4.26), overlapping; efficacy 20.1% to 99.7%](FIG_08)
*Figure 8. The arms' intervals overlap, yet the difference is significant at p = 0.021. The question is answered by the difference's own interval, not by the two arms'.*

## Does the t-interval keep its promise on skewed data?

Means raise the same question for a continuous statistic. The t-interval, x̄ ± t s/√n with t the 97.5% point of Student's t on n − 1 degrees of freedom, covers exactly 95% when the data are normal. The second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*, measured what skewness does to the t-test on a real population: the net spend of 4,317 customers of an online retailer, with skewness 21.6. <!-- L29 --> Read as an interval, the same failure is a coverage curve (Figure 9). Sampling customers with replacement, the 95% t-interval for the mean covers 64.42% ± 0.11 of the time at n = 10, 65.83% ± 0.11 at n = 30, 70.30% ± 0.10 at 100, 85.65% ± 0.14 at 1,000 and 93.84% ± 0.17 at 10,000.

![Coverage of the 95% t-interval for mean customer spend against n from 10 to 10,000: 64% to 94%, with nearly all misses below the mean](FIG_09)
*Figure 9. Two in three at n = 30. Almost every miss is an interval lying wholly below the mean; misses above it stay under 1.2% even at n = 10,000.*

Almost every miss is on one side. At n = 30 the interval lies entirely below the true mean in 34.17% of samples and above it in 1 of 200,000. A sample of 30 usually contains none of the few very large customers, so its mean is low and its standard deviation small: the interval is low and narrow at once.

That coupling makes the interval's own width a warning (Figure 10). Sort the 200,000 intervals at n = 30 by width into tenths. None of the 20,000 narrowest contains the mean, the next tenth covers 1.0%, the third 14.9%, and the widest half 99% to 100%. A normal population shows the same pattern, mildly: given its width, a t-interval at n = 30 covers 88.2% in the narrowest tenth and 98.7% in the widest, because a small s makes a narrow interval whatever the mean. Fisher called such identifiable groups **relevant subsets**: when the data pick out intervals with different coverage, the overall 95% is not the right number for yours. <!-- L30 -->

![Coverage of the t-interval at n = 30 by tenth of interval width: spend from 0% to 100%, a normal population from 88% to 99%](FIG_10)
*Figure 10. On skewed data the narrow intervals are the ones that miss. Overall coverage averages a 0% tenth with 100% ones.*

For skewed data, then, a narrow t-interval is the least trustworthy kind, and a larger n arrives at 95% only slowly. Intervals that adapt to the skew are the subject of a later part of this series.

## The math

| Symbol | Meaning |
|---|---|
| X, n, p, p̂ | binomial count, trials, true proportion, X/n |
| L(x), U(x) | the interval's endpoints when X = x |
| z | the standard normal 97.5% point, 1.960 |
| C_n(p) | actual coverage at p |
| I_t(a, b), B⁻¹(q; a, b) | the regularized incomplete beta function, and the beta distribution's q quantile |
| π, r | the vaccine group's share of cases; the ratio of surveillance times |
| k | the ratio of two standard errors |

**Coverage.** For any interval for a proportion, <!-- L12 -->

$$
C_n(p) = \sum_{x=0}^{n} \mathbf{1}\{L(x) \le p \le U(x)\} \binom{n}{x} p^x (1-p)^{n-x} \tag{1}
$$

Coverage at p is the probability of the outcomes whose interval contains p; at n = 20 and p = 0.1 the Wald interval keeps x = 1 to 6 and the sum is 0.8760.

**Confidence coefficient and mean coverage.** The confidence coefficient is the infimum of $C_n(p)$ over p; Agresti and Coull's mean is its average over a uniform p, which integrates in closed form: <!-- L05 -->

$$
\bar C_n = \int_0^1 C_n(p)\,dp = \frac{1}{n+1} \sum_{x=0}^{n} \left[ I_{U(x)}(x+1,\, n-x+1) - I_{L(x)}(x+1,\, n-x+1) \right] \tag{2}
$$

Each outcome's probability integrates to an incomplete beta function, so the averages in Figure 5 need no numerical integration; for the Wald interval at n = 50 the result is 0.9006.

**Wilson and Clopper–Pearson.** The Wilson limits solve |p̂ − p₀| = z √(p₀(1 − p₀)/n) for p₀; the Clopper–Pearson limits are beta quantiles, with L(0) = 0 and U(n) = 1: <!-- L06 -->

$$
\frac{\hat p + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat p(1-\hat p)}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}, \qquad L(x) = B^{-1}\!\left(0.025;\, x,\, n-x+1\right), \quad U(x) = B^{-1}\!\left(0.975;\, x+1,\, n-x\right) \tag{3}
$$

For 2 errors in 20 these give 0.028 to 0.301 and 0.012 to 0.317; each Clopper–Pearson limit is the p₀ at which one one-sided exact test has a tail of exactly 2.5%.

**Efficacy from a case split.** With r the vaccine-to-placebo ratio of surveillance times,

$$
\pi = \frac{\mathrm{IRR}\, r}{\mathrm{IRR}\, r + 1} \quad\Longleftrightarrow\quad \mathrm{VE} = 1 - \frac{\pi}{(1-\pi)\,r} \tag{4}
$$

The map reverses order, so the share's interval of 0.0205 to 0.0906 becomes efficacy from 97.9% down to 90.0%.

**The overlap rule.** For two independent estimates whose standard errors have ratio k, rejecting when the 95% intervals do not overlap has type I error <!-- L23 -->

$$
\alpha_{\text{overlap}}(k) = 2\left[1 - \Phi\!\left(\frac{z\,(1+k)}{\sqrt{1+k^2}}\right)\right] \tag{5}
$$

At k = 1 the argument is 1.96√2 = 2.77 and the rate 0.0056; as k grows the argument falls to 1.96 and the rate rises to 0.05.

<details>
<summary>Why a normal t-interval's coverage depends on its width</summary>

For normal data the mean and the standard deviation s are independent, and V = (n − 1)s²/σ² is χ² with n − 1 degrees of freedom. Given s, the interval x̄ ± t s/√n contains μ exactly when |x̄ − μ|/(σ/√n) ≤ t s/σ, which has probability 2Φ(t s/σ) − 1. Averaged over all s this is 95%, but it rises with s: a narrow interval comes from a small s and covers less. Averaging the expression over each tenth of the χ² distribution gives Figure 10's normal bars, from 88.2% to 98.7% at n = 30. For skewed data s and x̄ are not independent, and the narrow intervals also sit low, which is why the spend's narrowest tenth covers nothing.

</details>

## Implementation

Exact coverage for any interval in a few lines; the lab sums Figures 3, 4 and 6 the same way.

```python
import numpy as np
from scipy import stats


def wald(x, n, z=stats.norm.isf(0.025)):
    p = x / n
    half = z * np.sqrt(p * (1 - p) / n)
    return p - half, p + half


def coverage(interval, n, p):
    """Exact coverage at p: the total probability of the outcomes whose interval contains p."""
    x = np.arange(n + 1)
    lo, hi = interval(x, n)
    return stats.binom.pmf(x, n, p)[(lo <= p) & (p <= hi)].sum()


print(*(f"{coverage(wald, n, 0.1):.4f}" for n in (20, 29, 30, 50)))    # 0.8760 0.9467 0.8085 0.8789
```

It prints 0.8760, 0.9467, 0.8085 and 0.8789: the worked example, then the drop from n = 29 to n = 30 and the rule-of-thumb case at n = 50. Swap in any function that returns the two limits for an array of counts.

### Reading the library's output

The libraries name the intervals differently, and their defaults differ.

```python
from statsmodels.stats.proportion import proportion_confint

proportion_confint(2, 20)                       # method="normal", the Wald interval: (0.0, 0.2315)
proportion_confint(2, 20, method="wilson")      # (0.0279, 0.3010)
proportion_confint(2, 20, method="beta")        # Clopper-Pearson: (0.0123, 0.3170)
stats.binomtest(2, 20).proportion_ci()          # SciPy, method="exact": Clopper-Pearson again
```

In statsmodels 0.15.0, `proportion_confint` defaults to `method="normal"`, the Wald interval, and clips it to 0 and 1, which hides the negative limit without repairing the coverage. Its `"agresti_coull"` uses z² rather than 4, and its `"jeffreys"` leaves a lower limit of 2.4 × 10⁻⁵ at X = 0 of 20 where the convention above sets 0. <!-- L31 --> SciPy 1.18.1 defaults to `method="exact"`, Clopper–Pearson. <!-- L32 --> R's `binom.test` returns Clopper–Pearson too, and `poisson.test(c(8, 162), c(2.214, 2.222))` returns the rate ratio's interval, which is the trial's efficacy interval read as 1 − IRR. <!-- L33 -->

Exact p-values need the same care. For the severe split, `stats.binomtest(1, 10, p=0.5009)`, with 0.5009 the vaccine group's share of cases under no efficacy, returns p = 0.0116, and R's `poisson.test` the same: both add the probabilities of every outcome no more likely than the one observed. The Clopper–Pearson interval inverts twice the smaller tail, which gives 0.0212. <!-- L32 --> <!-- L33 --> Both are below 0.05 here, but near the threshold they can disagree, and the p-value to report is the one whose inversion is the interval you report. The lab's `intervals.py` computes every number in this post in six stages; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading a computed 95% interval as a 95% probability that the parameter is inside it. The 95% belongs to the procedure across repetitions. A probability for this interval needs a prior, and the result is a credible interval, which the vaccine trial reported alongside its confidence interval.

- **Using the Wald interval for a proportion.** It is statsmodels' default. At 20 trials and p = 0.1 it covers 87.6%, and at n = 50 with np = 5 it covers 87.9%. Use Wilson or Jeffreys for small n and Agresti–Coull for larger n, or Clopper–Pearson when 95% must be a floor.
- **Treating n ≥ 30 or np ≥ 5 as a guarantee.** The Wald interval's coverage at p = 0.1 falls from 94.7% to 80.9% between n = 29 and 30, and the t-interval for mean spend covers 65.8% at n = 30.
- **Reading "exact" as accurate.** Clopper–Pearson's coverage is at least 95% and usually more, 96.9% on average at n = 50, bought with intervals 8.3% wider than Wilson's.
- **Judging a difference by overlap.** Touching 95% intervals mean p of about 0.006; overlapping ones can still be significant. Compute the difference and its own interval. For paired measurements the two intervals cannot settle it at all, because the difference's standard error depends on the pairing. <!-- L36 --> <!-- L28 -->
- **Trusting a narrow interval on skewed data.** The width and the error are linked: at n = 30 on customer spend the narrowest tenth of t-intervals contains the mean in none of 20,000 samples.
- **Forgetting what coverage assumes.** Coverage holds for a procedure fixed in advance and applied to every sample. An interval reported because its estimate was significant can undercover, provably so when power is below 50%. <!-- L35 --> Stopping when an interval first excludes zero is the fifth part's peeking in interval form and breaks the guarantee the same way, as does reporting the best of many intervals.

## Key takeaways

- A confidence level belongs to a procedure: a 95% procedure contains the true value in 95% of repetitions, at every value. The interval you computed contains it or does not; a probability for it is a Bayesian credible interval.
- Coverage can be measured, and for a proportion it is an exact sum over outcomes. At 20 trials and p = 0.1: Wald 87.6%, Wilson 95.7%, Clopper–Pearson 98.9%.
- Do not use the Wald interval for a proportion; its coverage zigzags with n and falls to 80.9% at n = 30 for p = 0.1. Wilson and Jeffreys suit small n, Agresti–Coull larger n, and Clopper–Pearson guarantees 95% at about 8% more width at n = 50.
- Overlap of two 95% intervals is not a test of their difference: with equal standard errors it is a 0.56% test, with 51% power where the real test has 80%.
- On skewed data a 95% t-interval can cover far less: 65.8% at n = 30 for customer spend, with nearly every miss below the mean and the narrowest intervals missing most.

## Try it yourself

**E1, reproduce.** Repeat the worked example for a true error rate of p = 0.2 with 20 audits. Which counts give a Wald interval containing 0.2, and what is the coverage?

<details><summary>Answer</summary>

At X = 1 the interval is −0.046 to 0.146, which misses; at X = 2 it is −0.031 to 0.231, which contains 0.2, and so on up to X = 8, where 0.40 ± 0.215 runs from 0.185 to 0.615. At X = 9 it is 0.232 to 0.668 and misses. So the coverage is P(2 ≤ X ≤ 8) = 1 − P(X ≤ 1) − P(X ≥ 9) = 1 − 0.0692 − 0.0100 = 0.9208. The lab's `enumerate` stage with `--p 0.2` gives 0.9208 for Wald, 0.9563 for Wilson and 0.9785 for Clopper–Pearson.

</details>

**E3, predict.** Suppose the trial had stopped at half the cases with the same split, 4 in the vaccine group and 81 in the placebo group, with the same ratio of surveillance times. Before computing, predict the efficacy estimate and how the Clopper–Pearson interval changes.

<details><summary>Answer</summary>

The estimate stays at 95.0%, because the split and the surveillance ratio are unchanged. The interval widens to 86.8% to 98.7%, against 90.0% to 97.9%, and mostly downward, because a share near zero has a skewed binomial. On the log rate ratio scale its width grows 1.48 times, a little more than the √2 that halving the counts would give in large samples. The lab's `pfizer` stage with `--split 4 81` prints it, and `--split 16 324` gives 91.8% to 97.2%.

</details>

The lab carries the full ladder, from reproducing these numbers to finding why an interval guaranteed to cover 95% reports a minimum coverage of zero, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E4 exercises with answers, and cleanup.
- [`intervals.py`](LAB_02) — the six stages: enumerate, invert, coverage, pfizer, overlap and tcoverage.
- [`requirements.txt`](LAB_03) — the pinned NumPy, SciPy, statsmodels and pandas versions.
- [`online_retail_customer_spend.csv`](LAB_04) — net spend of 4,317 customers (UCI Online Retail, CC BY 4.0), with provenance; put it in a `data` folder.
- [`bnt162b2_case_splits.csv`](LAB_05) — the trial's 18 published case splits with surveillance times and intervals, with sources; put it in a `data` folder.
- [`captures.json`](LAB_06) — the author's full run, machine-readable, with the private cross-checks against R.
- [`captures-quick.json`](LAB_07) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_08) — the author's full run as printed.
- [`notebook.ipynb`](LAB_09) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-confidence-intervals-coverage.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. F. P. Polack, S. J. Thomas, N. Kitchin, J. Absalon, A. Gurtman, S. Lockhart et al. "Safety and efficacy of the BNT162b2 mRNA Covid-19 vaccine." *New England Journal of Medicine* 383(27): 2603–2615, 2020. https://doi.org/10.1056/NEJMoa2034577
2. U.S. Food and Drug Administration. *FDA Briefing Document: Pfizer-BioNTech COVID-19 Vaccine.* Vaccines and Related Biological Products Advisory Committee, 10 December 2020. https://www.fda.gov/media/144245/download (accessed 2026-10-31)
3. J. Neyman. "Outline of a theory of statistical estimation based on the classical theory of probability." *Philosophical Transactions of the Royal Society A* 236(767): 333–380, 1937. https://doi.org/10.1098/rsta.1937.0005
4. A. Agresti and B. A. Coull. "Approximate is better than 'exact' for interval estimation of binomial proportions." *The American Statistician* 52(2): 119–126, 1998. https://doi.org/10.1080/00031305.1998.10480550
5. S. Greenland, S. J. Senn, K. J. Rothman, J. B. Carlin, C. Poole, S. N. Goodman and D. G. Altman. "Statistical tests, P values, confidence intervals, and power: a guide to misinterpretations." *European Journal of Epidemiology* 31(4): 337–350, 2016. https://doi.org/10.1007/s10654-016-0149-3
6. R. D. Morey, R. Hoekstra, J. N. Rouder, M. D. Lee and E.-J. Wagenmakers. "The fallacy of placing confidence in confidence intervals." *Psychonomic Bulletin & Review* 23(1): 103–123, 2016. https://doi.org/10.3758/s13423-015-0947-8
7. R. Hoekstra, R. D. Morey, J. N. Rouder and E.-J. Wagenmakers. "Robust misinterpretation of confidence intervals." *Psychonomic Bulletin & Review* 21(5): 1157–1164, 2014. https://doi.org/10.3758/s13423-013-0572-3
8. J. Miller and R. Ulrich. "Interpreting confidence intervals: a comment on Hoekstra, Morey, Rouder, and Wagenmakers (2014)." *Psychonomic Bulletin & Review* 23(1): 124–130, 2016. https://doi.org/10.3758/s13423-015-0859-7
9. R. D. Morey, R. Hoekstra, J. N. Rouder and E.-J. Wagenmakers. "Continued misinterpretation of confidence intervals: response to Miller and Ulrich." *Psychonomic Bulletin & Review* 23(1): 131–140, 2016. https://doi.org/10.3758/s13423-015-0955-8
10. M. A. García-Pérez and R. Alcalá-Quintana. "The interpretation of scholars' interpretations of confidence intervals: criticism, replication, and extension of Hoekstra et al. (2014)." *Frontiers in Psychology* 7: 1042, 2016. https://doi.org/10.3389/fpsyg.2016.01042
11. E. B. Wilson. "Probable inference, the law of succession, and statistical inference." *Journal of the American Statistical Association* 22(158): 209–212, 1927. https://doi.org/10.1080/01621459.1927.10502953
12. C. J. Clopper and E. S. Pearson. "The use of confidence or fiducial limits illustrated in the case of the binomial." *Biometrika* 26(4): 404–413, 1934. https://doi.org/10.1093/biomet/26.4.404
13. L. D. Brown, T. T. Cai and A. DasGupta. "Interval estimation for a binomial proportion." *Statistical Science* 16(2): 101–133, 2001. https://doi.org/10.1214/ss/1009213286
14. M. Thulin. "The cost of using exact confidence intervals for a binomial proportion." *Electronic Journal of Statistics* 8(1): 817–840, 2014. https://doi.org/10.1214/14-EJS909
15. N. Schenker and J. F. Gentleman. "On judging the significance of differences by examining the overlap between confidence intervals." *The American Statistician* 55(3): 182–186, 2001. https://doi.org/10.1198/000313001317097960
16. M. E. Payton, M. H. Greenstone and N. Schenker. "Overlapping confidence intervals or standard error intervals: what do they mean in terms of statistical significance?" *Journal of Insect Science* 3: 34, 2003. https://doi.org/10.1093/jis/3.1.34
17. H. Goldstein and M. J. R. Healy. "The graphical presentation of a collection of means." *Journal of the Royal Statistical Society A* 158(1): 175–177, 1995. https://doi.org/10.2307/2983411
18. G. Cumming. "Inference by eye: reading the overlap of independent confidence intervals." *Statistics in Medicine* 28(2): 205–220, 2009. https://doi.org/10.1002/sim.3471
19. S. Belia, F. Fidler, J. Williams and G. Cumming. "Researchers misunderstand confidence intervals and standard error bars." *Psychological Methods* 10(4): 389–396, 2005. https://doi.org/10.1037/1082-989X.10.4.389
20. G. Cumming and S. Finch. "Inference by eye: confidence intervals and how to read pictures of data." *American Psychologist* 60(2): 170–180, 2005. https://doi.org/10.1037/0003-066X.60.2.170
21. F. Garwood. "Fiducial limits for the Poisson distribution." *Biometrika* 28(3–4): 437–442, 1936. https://doi.org/10.1093/biomet/28.3-4.437
22. E. W. van Zwet and E. A. Cator. "The significance filter, the winner's curse and the need to shrink." *Statistica Neerlandica* 75(4): 437–452, 2021. https://doi.org/10.1111/stan.12241
23. D. Chen. "Online Retail" [dataset]. UCI Machine Learning Repository, 2015. CC BY 4.0. https://doi.org/10.24432/C5BW33
24. statsmodels 0.15.0 documentation, `proportion_confint`. https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_confint.html (accessed 2026-10-31)
25. SciPy 1.18.1 documentation, `scipy.stats.binomtest`. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html (accessed 2026-10-31)
26. R Core Team. R 4.5.2 documentation, `binom.test` and `poisson.test`. https://stat.ethz.ch/R-manual/R-patched/library/stats/html/binom.test.html (accessed 2026-10-31)
