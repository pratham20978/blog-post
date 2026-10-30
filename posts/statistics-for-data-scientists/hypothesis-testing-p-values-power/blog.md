---
title: "p-Values and Power: How Wrong Can a Significant Result Be?"
slug: hypothesis-testing-p-values-power
date: 2026-10-29
updated: 2026-10-29
summary: "A p-value assumes no effect; it is not the chance of a fluke. In a low-powered study a significant estimate can point the wrong way and be nine times too big."
tags: [data-science, statistics, hypothesis-testing, p-value, statistical-power, type-s-and-m-errors, equivalence-testing]
category: data-science
series: statistics-for-data-scientists
series_position: 5
tier: L4
difficulty: advanced
prerequisites: ["the sampling distribution and the standard error", "the t statistic", "Python with NumPy and SciPy"]
reading_minutes: 34
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/hypothesis-testing-p-values-power"
---

![A normal curve centred at 2 cut by a significance bar at ±15.9: only its far tails count as significant results](COVER)

> [!NOTE]
> **Insights** — A p-value is the probability, computed as if there were no effect, of a test statistic at least as extreme as the one observed. It is not the chance that the result is a fluke, and it is itself a random variable, uniform when the null is true. What a significant estimate means depends on power: in a design like a published 2013 study of voting over the menstrual cycle, every significant estimate is at least 7.9 times the plausible effect and one in four has the wrong sign. And in a well-powered experiment an observed p = 0.03 still leaves a 17% chance of no effect at even prior odds, and 64% if one tested effect in ten is real.

**Level:** advanced · **You need:** the sampling distribution and the standard error; the t statistic; Python with NumPy and SciPy · **Time:** ~34 min

**Jump to:** [worked example](#worked-example) · [the distribution of p](#what-is-the-distribution-of-a-p-value) · [power](#how-is-power-computed) · [type S and M](#how-wrong-can-a-significant-estimate-be) · [replications](#why-do-replications-find-smaller-effects) · [false positives](#what-share-of-significant-results-are-false) · [no effect](#how-do-you-show-there-is-no-effect) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: one NumPy, SciPy and statsmodels script that runs in about 30 seconds and is seeded, so every number repeats exactly. Each simulated quantity is printed as an estimate ± its Monte Carlo standard error (MCSE) with its number of replications R; powers, error rates and risks that have a closed form are computed exactly. Published numbers are **quoted**, and the lab recomputes each one before it is used.

## Why this matters

In 2013 *Psychological Science* published a study reporting that single women's voting preferences moved by 17 percentage points between phases of the menstrual cycle, with p = .035. <!-- L01 --> Read the common way, that is a 3.5% chance of a fluke and evidence of a 17-point effect. Gelman and Carlin asked what a study built like this could detect. Obama's support in the 2012 polls moved by only 7 points over the whole campaign, so they took 2 points as an upper plausible value for the true difference; with the study's standard error of 8.1 points, a true 2-point effect reaches significance in 6% of such studies, and a quarter of those point the wrong way. <!-- L02 --> The 17 is not evidence of a big effect. It is how big an estimate from this design has to be to clear the bar, and the same arithmetic governs every underpowered A/B test whose winner ships because its p-value crossed 0.05.

## The problem

A test starts from a **null hypothesis**, H₀, a model in which the effect is absent, and a **test statistic**, a number computed from the data whose distribution under H₀ is known. The second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*, built one: the t statistic, an estimate divided by its standard error. The **p-value** is the probability, computed with H₀ true, of a statistic at least as extreme as the one observed; for a two-sided test, extreme in either direction. The fourth part, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, computed p-values as tail areas of χ² and left their meaning to this part.

Two readings of that number are in use, and they answer different questions. Fisher's 1925 textbook treated p as graded evidence against H₀, and took P = .05, a deviation of 1.96 or about two standard deviations, as a convenient line for calling a result significant. <!-- L03 --> Neyman and Pearson's 1933 theory treats a test as a decision rule fixed before the data: a **significance level** α, the rate at which it rejects a true H₀ (a **type I error**), and **power**, 1 − β, the rate at which it rejects H₀ when a stated alternative is true (missing it is a **type II error**, with rate β). The test taught in most courses is a hybrid of the two, and Hubbard and Bayarri argue that Fisher's evidential p and Neyman–Pearson's α are incompatible quantities that the hybrid conflates; Lehmann argued that in practice the two theories complement each other. <!-- L04 --> In this series "statistically significant" always carries its α, here 5% two-sided.

Either way, the promise is about the procedure: when H₀ is true, a 5% test rejects in 5% of repetitions. It is not the probability that H₀ is true, nor the probability that chance alone produced the data, and it does not measure the size of an effect. That is the American Statistical Association's 2016 statement, <!-- L05 --> and Greenland and colleagues list among the common misreadings the belief that rejecting at P ≤ 0.05 carries a 5% chance of being wrong. <!-- L06 --> This part tests the claim **"p = 0.03 means a 3% chance the result is a fluke"**, and measures what significance does to the estimates that pass it.

## Worked example

Take the 2013 study as Gelman and Carlin analysed it: an estimated difference of d = 17 percentage points with p = .035. A two-sided p of .035 corresponds to z = 2.1, so the standard error is s = 17/2.1 = 8.1 points. <!-- L02 -->

**The p-value.** If the true difference were 0, the estimate would be roughly normal with mean 0 and standard deviation 8.1. Then z = 17/8.1 = 2.099, and the chance of an estimate at least 17 points from 0 in either direction is 2 × P(Z ≥ 2.099) = 0.0358. That is all p measures: how unusual 17 would be if there were nothing there.

**The bar.** At 5% two-sided, an estimate is significant when it lies beyond 1.96 standard errors: |d| above 1.96 × 8.1 = 15.88 points. Every significant estimate this design can produce is at least 15.88 points from 0.

**A plausible truth.** Gelman and Carlin's design analysis asks what would happen in replications of the same design if the true effect were D = 2 points. <!-- L07 --> The replicated estimate is then normal with mean 2 and standard deviation 8.1, a **signal-to-noise ratio** λ = D/s = 0.247.

- It lands above +15.88 with probability P(Z ≥ (15.88 − 2)/8.1) = P(Z ≥ 1.713) = 0.0434.
- It lands below −15.88 with probability P(Z ≤ (−15.88 − 2)/8.1) = P(Z ≤ −2.207) = 0.0137.
- So the **power**, the chance of a significant result, is 0.0434 + 0.0137 = 0.0570, barely above the 0.05 a true null would give.

**The wrong sign.** Of the significant results, 0.0137/0.0570 = 24.0% point the wrong way. Gelman and Carlin call this the **type S error** rate: the probability that a significant estimate has the wrong sign. <!-- L07 -->

**The wrong size.** A significant estimate above the bar averages +19.19, one below it averages −18.72 (the means of the normal's two tails beyond the bar). Weighting by 0.0434 and 0.0137, the average magnitude of a significant estimate is 19.08 points, and 19.08/2 = 9.54 is the **exaggeration ratio**, or expected **type M** (magnitude) error. The floor is stark: since no significant estimate can be smaller than 15.88, each one overstates a 2-point effect at least 15.88/2 = 7.94 times (Figure 1).

![Normal curve of replicated estimates centred at 2 with SD 8.1; only 4.34% beyond +15.9 and 1.37% beyond −15.9 are significant](FIG_01)
*Figure 1. The design, not the data, sets the size of a significant result. With a true effect of 2 points, a significant estimate is at least 7.9 times too large, and 24% of them have the wrong sign.*

Ten million simulated replications of the design agree with the hand calculation: 5.71% significant, 23.9% of those with the wrong sign, and an exaggeration ratio of 9.540 ± 0.002. Gelman and Carlin print power 0.06, type S 24% and an exaggeration ratio of 9.7 for this design. <!-- L02 --> The first two match the exact values above; the third differs because they simulated it from 10,000 draws, and the lab measures below how much such a simulation wanders. The design was far too small for the question: 80% power at D = 2 would need a standard error of 0.71 points, about 129 times the data.

## Intuition

Think of significance as a net with a fixed mesh: here it keeps only estimates longer than 15.9 points. Whatever lives in the lake, everything in the net is at least 15.9 long, so measuring the catch tells you about the mesh rather than about the fish. When the true effects are large compared with the mesh, nearly everything is caught and the catch is a fair sample. When they are small, only the few estimates inflated by noise make it in, and their average says more about the noise than the effect.

The analogy breaks in one place. A fish has one length; an estimate is the effect plus noise, and noise has a sign. A small positive effect plus a large negative error is caught on the wrong side of the net, which is the type S error. No mesh, however fine, removes it: only less noise, a smaller standard error, does.

## What is the distribution of a p-value?

A p-value is computed from data, so it varies from sample to sample like any statistic. Under a true null with a continuous test statistic it is **uniform** on 0 to 1: P(p ≤ a) = a for every a, whatever the sample size. Under an alternative its distribution depends on the sample size and the true effect. <!-- L08 --> Murdoch and colleagues argue that this is how p-values should be taught: as random variables, by simulation. <!-- L09 -->

For a z-test the distribution depends only on λ. The lab draws 200,000 z statistics at each of five values: at λ = 0, 4.98% ± 0.05 of p-values fall at or below .05, and the twenty bins of width .05 pass a χ² check of uniformity (p = 0.55). The probability of p ≤ .05 is the power, and the median p shows how a typical study reads:

| λ = true effect / SE | Power at 5% | Median p | p ≤ .001 |
|---|---|---|---|
| 0 (null) | 5.0% | 0.500 | 0.10% |
| 0.247 (the worked example) | 5.7% | 0.487 | 0.14% |
| 1 | 17.0% | 0.293 | 1.1% |
| 2 | 51.6% | 0.045 | 9.8% |
| 2.8 | 80.0% | 0.0051 | 31.2% |

![Histograms of simulated p-values for five signal-to-noise ratios: flat at 0, nearly flat at 0.25, piled near 0 at 2.8](FIG_02)
*Figure 2. Same test, five true effects. At the worked example's λ the p-value is almost uniform, so it carries almost no information about the effect.*

The two-sample t-test behaves the same way on real samples. The running design of this post is Colquhoun's: two groups of 16, a true difference of one standard deviation, a power of 78.14%. Over 100,000 simulated experiments, 78.40% ± 0.13 reach p ≤ .05 and the median p is 0.0077; with no true difference, 4.85% ± 0.07 do, within about two MCSEs of 5%. Figure 2 shows why a single p says so little: at 52% power the median study sits right at the bar.

Run the 78%-power experiment 25 times and the p-values scatter across four orders of magnitude, from 0.00007 to 0.33, with 19 of 25 significant (Figure 3). Cumming showed that after an original p of .05, a replication's one-tailed p has an 80% chance of falling between .00008 and .44, whatever the sample size. <!-- L10 --> The lab reproduces that interval in closed form and by simulation: 80.05% ± 0.24 of 28,439 simulated replications fall inside it. Even at 80% power, two independent studies both reach significance only 64% of the time, and one does while the other does not 32% of the time. <!-- L11 -->

![Twenty-five repeats of one experiment: estimates with 95% intervals, p-values from 0.00007 to 0.33, nineteen significant](FIG_03)
*Figure 3. Nothing differs between the rows but the sample. A p of 0.03 and a p of 0.0003 are ordinary draws from the same experiment.*

### Does the promise survive peeking?

Uniformity needs the sample size fixed in advance. Test after every new observation and stop at the first p ≤ .05, and each look is a new chance to reject a true null. For a z-test the error rate can be computed exactly by carrying the distribution of the running sum forward and removing the mass that crosses the bar at each look: 8.31% with 2 looks, 14.17% with 5, 19.33% with 10, 37.36% with 100 and 52.99% with 1,000 (Figure 4). Armitage, McPherson and Rowe computed such rates in 1969, and noted that with enough looks a null is eventually rejected with certainty. <!-- L12 -->

![Error rate of a 5% z-test repeated after each observation, rising from 5% at 1 look to 53% at 1,000, with simulated checks](FIG_04)
*Figure 4. Stopping when significant turns a 5% test into a 37% test after 100 looks. The simulated points use 100,000 paths.*

The common version is milder, and it still inflates the rate. Simmons, Nelson and Simonsohn showed that such flexibility in data collection inflates false positives; <!-- L13 --> in the lab, testing at 20 per group and adding 10 per group when the first test fails rejects a true null 7.77% ± 0.06 of the time, and checking a t-test after every added pair from 10 to 100 per group rejects 28.5% ± 0.3. Group sequential designs raise the bar at each planned look so that the overall rate stays at 5%. <!-- L14 --> Designing them belongs to experimentation practice, which this series does not cover.

## How is power computed?

Power is a Neyman–Pearson quantity, fixed before the data, and Figure 5 draws the running design in those terms. Under H₀ the pooled t statistic with 30 degrees of freedom has a Student t distribution, and a 5% test rejects beyond ±2.042. Under the alternative, a difference of 1 SD with 16 per group, it has a **noncentral t** distribution with noncentrality λ = d√(n/2) = 2.83, where d is the **standardised effect size**, the difference in standard deviations. The area beyond the bars is 78.14%.

![Null and alternative t densities for 16 per group: 5% of the null beyond ±2.04, 78.1% of the alternative, and t = 2.28 for p = .03](FIG_05)
*Figure 5. Fisher reads the null's tail beyond the observed t, 3% for t = 2.28. Neyman and Pearson read the areas fixed in advance: reject, with α 5% and β 21.9%.*

The noncentral t is a ratio, T = (Z + λ)/√(V/30), of a shifted standard normal and the square root of an independent χ² variable V over its degrees of freedom. Given V, rejection is a pair of normal tails, so power is their average over V: one integral. The lab evaluates it by hand and gets 0.781398, the same to six digits as SciPy's `nct`, statsmodels' `TTestIndPower` and R's `power.t.test` with `strict = TRUE` (its default counts only the upper tail and gives 0.781397). <!-- L15 --> The normal approximation says 0.8074. It overstates power because it treats the standard deviation as known: with 30 degrees of freedom the bar sits at 2.042 rather than 1.960, and the estimated standard deviation adds spread that the normal leaves out. The gap closes as the sample grows; at 64 per group and d = 0.5 the two give 0.8015 and 0.8074.

![Power against sample size per group for effect sizes 0.2, 0.5, 0.8 and 1: exact curves, normal approximations and simulated points](FIG_06)
*Figure 6. 80% power needs 64 per group for d = 0.5 and 394 for d = 0.2. Thirteen simulated points sit within 2.3 MCSE of the exact curves.*

Solving the exact power for n gives the familiar sample sizes: 17 per group for d = 1, 26 for d = 0.8, 64 for d = 0.5 and 394 for d = 0.2 (statsmodels' continuous solution for d = 0.5 is 63.77). The lab also simulates thirteen designs with R = 20,000 each; the largest gap from the exact curve is 2.3 MCSE (Figure 6).

After a study, software and reviewers sometimes ask for its **observed power**: the power at the effect the data estimated. It adds nothing. For a z-test it is a fixed function of the p-value, 0.50 at p = .05, 0.25 at p = .2 and 0.10 at p = .5 (Figure 7), so a non-significant result always has low observed power. Hoenig and Heisey document how widely such calculations are used to interpret non-significant results, and why the logic fails. <!-- L16 --> Gelman and Carlin's design analysis is a different calculation: its effect size comes from outside the data. <!-- L17 -->

![Observed power plotted against the p-value for a z-test and for the 16-per-group t-test: 0.50 at p = .05](FIG_07)
*Figure 7. Observed power is the p-value on another scale. It cannot say whether a non-significant study was too small.*

## How wrong can a significant estimate be?

The worked example generalises. For an unbiased, normally distributed estimate, power, the type S rate and the exaggeration ratio depend only on λ, so each can be read against power (Figure 8). At 50% power significant estimates exaggerate by 1.41 on average, at 20% by 2.26, at 10% by 3.71, and at 6% by 8.0, where 20% of them also have the wrong sign. Gelman and Carlin put the thresholds at about 50% power for exaggeration and 10% for sign errors, and computed 80% power at 2.8 standard errors, with a type S rate of 1.2 × 10⁻⁶ and an exaggeration ratio of 1.12. <!-- L18 -->

![Exaggeration ratio on a log scale and type S rate against λ and power, with the Kanazawa and 2013 designs and their printed values marked](FIG_08)
*Figure 8. Below 50% power a significant estimate overstates the effect; below 10% it can also flip. Both published studies sit at the far left.*

Their first example was Kanazawa's 2007 finding that the most attractive parents had more daughters, 56% against 48% girls: 8 points with p = .015, so a standard error of 3.28 and a bar at 6.43 points. With true differences of 0.1, 0.3 and 1 point, plausible for sex ratios, they report type S rates of 46%, 40% and 19% and exaggeration ratios of 77, 25 and 8. <!-- L19 --> The lab's closed form gives 46.4%, 39.5% and 19.4%, and 76.7, 25.6 and 7.75.

Their `retrodesign()` function computes power and the type S rate exactly but simulates the exaggeration ratio from 10,000 draws. <!-- L20 --> Lu, Qiu and Deng derived its closed form, <!-- L21 --> which gives 9.537 for the worked example against the published 9.7. The lab repeats the 10,000-draw simulation 2,000 times: its results have a standard deviation of 0.059 and a 95% range of 9.43 to 9.65, and R's own `retrodesign()`, run over 1,000 seeds, reaches 9.65 or more in 3.2% of them. The 9.7 was a high draw. Ten million draws give 9.540 ± 0.002, which agrees with the closed form.

Two qualifications. The smallest significant estimate, here 15.88, is the **critical effect size**, and Lakens and colleagues argue that it, bias-adjusted estimates and tests against a minimum effect serve design and interpretation better than type S and M errors, which they see as most useful in teaching and in criticising studies that skipped good practice. <!-- L22 --> The critical effect size needs no assumed truth: the study's 17 points sit just 1.1 points above its bar of 15.88, about as small as a significant estimate from this design can be. And conditioning on significance breaks more than the estimate: van Zwet and Cator prove that the relative bias of a significant estimate falls as power rises, and that the usual confidence interval undercovers when power is below 50%. <!-- L23 -->

## Why do replications find smaller effects?

The Open Science Collaboration repeated 100 studies from three psychology journals with high-powered designs and the original materials where available. Of the originals 97% were statistically significant; of the replications 36% were. Replication effects were half the size of the originals, and replication success was better predicted by the strength of the original evidence than by who ran either study. <!-- L24 --> The project's data are public under CC0, and the lab reads the 100 coded replications from them; the team's own significance codes give 97 and 36 again. <!-- L25 -->

On the 97 pairs with both effect sizes, expressed as correlations r, the original mean is 0.396 and the replication mean 0.197, a ratio of 0.497. The replication is the smaller of the two in 83.5% of pairs, and 17 replications have the opposite sign. Split by the original p-value (seven originals above .05 are left out), the pattern is the one Figure 8 predicts. Originals with p below .001 replicated 19 times in 31 and kept two thirds of their effect (0.49 to 0.33); originals between .001 and .05 replicated 14 times in 59 and kept 38% (0.37 to 0.14). The originals also crowd the bar: their median r is 1.30 times the smallest significant r for their sample size, and 67% sit within 1.5 times it.

![Original against replication effect size r for 97 pairs, most below the diagonal, coloured by whether the replication was significant](FIG_09)
*Figure 9. Replications kept half the original effect. Originals with p below .001 kept two thirds; those between .001 and .05 kept 38%.*

Selection for significance predicts all three: shrinkage on replication, more shrinkage where the original evidence was weaker, and originals clustered just above the bar. Ioannidis made the same argument for newly discovered associations: when discovery is claimed by crossing a significance threshold in an underpowered study, the published effect is expected to be inflated. <!-- L27 --> The data cannot separate that mechanism from others, though. Gilbert and colleagues argued that the project's analysis contained statistical errors and that its data are consistent with high reproducibility; the project's authors replied that both optimistic and pessimistic readings are possible and neither is yet warranted. <!-- L26 --> The practical lesson survives the dispute: a published effect has passed the filter, so planning a study's power around it overstates the power.

## What share of significant results are false?

The chance that a result is a fluke is a different conditional probability: the probability that H₀ is true given a significant result. It needs one more number, the **prior probability** π that a tested effect is real, and the share of significant results that are false is then the **false positive risk** (Colquhoun's term, which avoids the multiple-testing sense of "false discovery rate"). <!-- L31 --> Colquhoun's tree makes it concrete: of 1,000 tests with 10% real effects and 80% power, 80 real effects and 45 of the 900 nulls reach p ≤ .05, so 45/125 = 36% of the significant results are false. <!-- L28 --> In general the risk is α(1 − π) / (α(1 − π) + (1 − β)π), the complement of what Ioannidis called the positive predictive value; the lab recomputes all nine rows of his table, with and without his bias term, to his printed precision. <!-- L29 -->

![False positive risk of p ≤ .05 results against the prior probability of a real effect, for power 0.2 and 0.8, above the floor set by power 1](FIG_10)
*Figure 10. At a prior of 0.1, 36% of significant results are false even at 80% power, and 69% at 20% power.*

Benjamin and colleagues put the prior odds for psychology experiments at about 1:10, from prediction markets and replication results; at those odds more than 33% of p ≤ .05 results are false whatever the power, and a threshold of .005 would cut that floor to 5%. <!-- L30 --> The lab gives 33.3% at power 1, 38.5% at power 0.8, and 4.8% at the stricter threshold.

The tree treats every p ≤ .05 alike, which Colquhoun calls the **p-less-than** view. A single study reports one p, and the **p-equals** view asks how much more likely that exact result is if the effect is real. That is a **likelihood ratio**: the density of the observed t under the alternative over its density under H₀. For the running design, p = .05 means t = 2.042 and a ratio of 2.76, so the false positive risk is 1/(1 + 2.76) = 26.6% at even prior odds and 76.6% at a prior of 0.1. At p = .001 the ratio is 99.6, and the risks are 1.0% and 8.3%. All four match Colquhoun's 2017 values. <!-- L31 --> His 2014 simulation counted tests landing between .045 and .05 and found 26% false at even odds; <!-- L32 --> the lab simulates 500,000 null and 500,000 real experiments and finds 25.90% ± 0.44 in the same window.

![False positive risk of an observed p, p-equals and p-less-than, for priors 0.5 and 0.1, with p = .05, .03 and .001 marked](FIG_11)
*Figure 11. An observed p = .03 leaves a 17% risk at even odds and 64% at a prior of 0.1; counting every result at or below .03 alike gives 4% and 28%.*

So the claim fails. An observed p = .03 in this 78%-power design is a likelihood ratio of 5.0: a false positive risk of 16.7% at even odds and 64.3% at a prior of 0.1. It falls to 3% only when the prior odds reach (0.97/0.03)/5.0 = 6.5, a prior of 0.87: you would have to be 87% sure of the effect before seeing the data. The risk depends on a prior nobody knows, which is the honest objection to it. Goodman and Greenland argued that Ioannidis's model reached its headline by counting only significance verdicts rather than the observed p and by adding a bias term; <!-- L33 --> Jager and Leek, fitting the p-values reported in five medical journals, estimated a rate of false discoveries of 14%. <!-- L34 --> The policy debate has the same shape: Lakens and colleagues answered the .005 proposal by asking researchers to justify their α, <!-- L35 --> a 2019 editorial urged dropping "statistically significant" altogether, and an ASA president's task force replied in 2021 that p-values and significance tests, properly used, should not be abandoned. <!-- L36 -->

## How do you show there is no effect?

A non-significant result is not evidence of no effect: Lakens found "no effect" in 108 articles of one journal, almost all of them resting on non-significance. <!-- L37 --> The honest test reverses the null. Choose an **equivalence bound** Δ, the smallest effect that would matter, and run **two one-sided tests (TOST)**: one rejects "the difference is at most −Δ", the other "the difference is at least +Δ", each at 5%. Rejecting both is the same as the 90% confidence interval lying inside ±Δ. <!-- L37 --> Schuirmann introduced the procedure for bioequivalence, <!-- L38 --> and Lakens, Scheel and Isager describe how to choose the smallest effect size of interest. <!-- L40 -->

On one simulated running-design experiment with no true difference, the observed difference is −0.098 SD and the ordinary t-test gives p = 0.83. With Δ = 0.5 SD, the 90% interval runs from −0.88 to 0.69 and crosses both bounds; TOST's p, the larger of the two one-sided p-values, is 0.195, so the result is undetermined, neither different from 0 nor equivalent to it. statsmodels' `ttost_ind` returns that p, then each one-sided test's t statistic, p-value and degrees of freedom, <!-- L39 --> and the lab's implementation from first principles agrees to every digit. Its size holds: with the truth on the bound, 0.5 SD at 69 per group, it rejects 5.04% ± 0.07 of the time.

Showing absence costs more than showing presence (Figure 12). With 16 per group, TOST at ±0.5 SD succeeds in 0.8% of experiments with no true difference. The normal approximation asks for 69 per group for 80% power, where the exact power is 79.85%, against 64 to detect a difference of 0.5 SD; ±0.1 SD needs 1,713. Turned around, 16 per group can establish equivalence with 80% power only within ±1.06 SD, a bound wider than the 1 SD effect the design was built to detect.

![Narrowest equivalence bound against sample size per group: ±1.06 SD at 16, ±0.50 at 69, ±0.10 at 1,713; TOST power at ±0.5 SD](FIG_12)
*Figure 12. Sixteen per group can only rule out effects larger than 1.06 SD, more than the effect the design was built to find. Ruling out ±0.1 SD takes 1,713 per group.*

That is the right lens for the 63 replications that were not significant. Testing each for equivalence to r = 0 with a Fisher-z 90% interval, only 2 show the effect is below 0.1 in magnitude, and 17 that it is below 0.2 (Figure 13). Showing |r| below 0.1 with 80% power when the truth is 0 needs n = 854; the replications' median n was 71. Most failed replications could not rule out a small effect, so they say "not shown" rather than "absent".

![Ninety-percent intervals for 63 non-significant replications against bands at ±0.1 and ±0.2: 2 and 17 fall inside](FIG_13)
*Figure 13. "Failed to replicate" mostly means undetermined: 2 of 63 intervals fit inside ±0.1 and 17 inside ±0.2.*

## The math

| Symbol | Meaning |
|---|---|
| T, t | test statistic and its observed value |
| p | p-value; α the significance level; 1 − β the power |
| D, s, λ | true effect, standard error, signal-to-noise ratio λ = D/s |
| Φ, φ, z | standard normal distribution and density; z = Φ⁻¹(1 − α/2), 1.960 at 5% |
| π | prior probability that a tested effect is real |
| Δ | equivalence bound |

**The p-value and its null distribution.** For a two-sided test with a continuous statistic,

$$
p = P_{H_0}\left(|T| \geq |t|\right), \qquad P_{H_0}(p \leq a) = a \quad \text{for all } 0 \leq a \leq 1 \tag{1}
$$

Under H₀ the p-value is the statistic pushed through its own tail probability, so it is uniform; that uniformity is the test's guarantee, and it needs the design fixed in advance.

**Under an alternative,** for a z statistic with mean λ, the probability of p ≤ a is the power at level a:

$$
P(p \leq a) = 1 - \Phi\left(z_a - \lambda\right) + \Phi\left(-z_a - \lambda\right), \qquad z_a = \Phi^{-1}(1 - a/2) \tag{2}
$$

At a = .05 and λ = 0.247 this is 0.0434 + 0.0137 = 0.0570, the worked example's power.

**Power of the two-sample t-test.** With n per group, df = 2n − 2, λ = d√(n/2) and c the two-sided critical t,

$$
1 - \beta = \int_0^\infty \left[\Phi\!\left(\lambda - c\sqrt{v/\text{df}}\right) + \Phi\!\left(-\lambda - c\sqrt{v/\text{df}}\right)\right] f_{\chi^2_{\text{df}}}(v)\, dv \tag{3}
$$

Power is the normal power averaged over the sampling distribution of the variance estimate; for d = 1 and n = 16 it is 0.781398.

**Observed power.** Plugging the estimate in as the truth sets λ to the observed |z|, so for a z-test

$$
\text{observed power} = \Phi\left(|z_{\text{obs}}| - z\right) + \Phi\left(-|z_{\text{obs}}| - z\right) \tag{4}
$$

At p = .05 the observed |z| is 1.96 itself, and the formula gives 0.50004: a function of p and nothing else.

**Type S and M.** Conditioning on significance, with the Lu–Qiu–Deng closed form for the exaggeration ratio, <!-- L21 -->

$$
\text{type S} = \frac{\Phi(-z - \lambda)}{1 - \beta}, \qquad \text{exaggeration} = \frac{\varphi(\lambda + z) + \varphi(\lambda - z) + \lambda\,\{\Phi(\lambda + z) + \Phi(\lambda - z) - 1\}}{\lambda\,(1 - \beta)} \tag{5}
$$

The exaggeration ratio is the mean magnitude of the significant estimates over the true effect; at λ = 0.247 the two give 0.2396 and 9.537.

**False positive risk.** For the p-less-than and p-equals views, with LR the likelihood ratio of the observed t,

$$
\text{FPR}_{\leq} = \frac{\alpha(1 - \pi)}{\alpha(1 - \pi) + (1 - \beta)\pi}, \qquad \text{FPR}_{=} = \frac{1}{1 + \text{LR} \cdot \pi/(1 - \pi)} \tag{6}
$$

The first treats every p ≤ α alike; the second uses the p actually observed, which for p = .03 in the running design gives LR = 5.0.

**TOST.** With observed difference Δ̂ and standard error s,

$$
t_1 = \frac{\hat\Delta + \Delta}{s}, \qquad t_2 = \frac{\hat\Delta - \Delta}{s}, \qquad p_{\text{TOST}} = \max\{P(T \geq t_1),\ P(T \leq t_2)\} \tag{7}
$$

Each one-sided test runs at α, so the equivalence verdict matches a 1 − 2α confidence interval inside ±Δ.

<details>
<summary>Why optional stopping eventually rejects every null</summary>

With independent unit-variance observations, the running sum S_k after k of them has standard deviation √k, and the test at look k rejects when |S_k| ≥ 1.96√k. The law of the iterated logarithm says |S_k| reaches √(2k log log k) infinitely often, and that grows faster than 1.96√k, so with unlimited looks the crossing happens with probability one. The lab computes the rate for a finite number of looks by keeping the distribution of S_k on a grid: convolve with a standard normal, remove the mass beyond the bar, repeat. Its two-look value, 8.307%, is within 0.005 points of the exact bivariate-normal 8.312%.

</details>

## Implementation

Gelman and Carlin's design analysis in a screen of Python: the closed form and their simulation side by side.

```python
import numpy as np
from scipy import stats


def retrodesign(A, s, alpha=0.05, n_sims=10_000, rng=np.random.default_rng(1)):
    """Power, type S and exaggeration for an unbiased normal estimate with true effect A and SE s."""
    z, lam = stats.norm.isf(alpha / 2), A / s
    hi, lo = stats.norm.sf(z - lam), stats.norm.cdf(-z - lam)
    power = hi + lo
    exact = (stats.norm.pdf(lam + z) + stats.norm.pdf(lam - z)
             + lam * (stats.norm.cdf(lam + z) + stats.norm.cdf(lam - z) - 1)) / (lam * power)
    est = A + s * rng.standard_normal(n_sims)              # hypothetical replications
    sig = np.abs(est) > s * z
    return power, lo / power, exact, np.abs(est[sig]).mean() / A   # abs() matters: wrong-sign estimates count by size


print("power %.4f  type S %.4f  exaggeration %.4f (simulated %.2f)" % retrodesign(2, 8.1))
```

It prints power 0.0570, type S 0.2396 and exaggeration 9.5366, and 9.61 from this seed's 10,000 draws; other seeds move the simulated value by about 0.06. The equivalence test is six lines, and statsmodels returns the same p-value, 0.0399, to every printed digit.

```python
from statsmodels.stats.weightstats import ttost_ind


def tost(x, y, bound):
    n1, n2 = len(x), len(y)
    df = n1 + n2 - 2
    diff = np.mean(x) - np.mean(y)
    se = np.sqrt(((n1 - 1) * np.var(x, ddof=1) + (n2 - 1) * np.var(y, ddof=1)) / df * (1 / n1 + 1 / n2))
    return max(stats.t.sf((diff + bound) / se, df), stats.t.cdf((diff - bound) / se, df))


rng = np.random.default_rng(7)
x, y = rng.standard_normal(100), rng.standard_normal(100)
print(tost(x, y, 0.3), ttost_ind(x, y, -0.3, 0.3)[0])     # the same p-value twice
```

### Reading the library's output

`ttost_ind` returns three things, and each is a test. For the 16-per-group experiment with bounds of ±0.5 SD it returns 0.1954, then (0.871, 0.1954, 30) and (−1.293, 0.1029, 30). The first number is the equivalence p-value, the larger of the two one-sided ones. The first triple is the lower test, of "the difference is at most −0.5": t = (−0.0975 + 0.5)/0.4621 = 0.871 with 30 degrees of freedom and p = 0.195. The second is the upper test, of "the difference is at least +0.5": t = (−0.0975 − 0.5)/0.4621 = −1.293, p = 0.103. Neither rejects at 5%, so neither bound is ruled out; that is the 90% interval from −0.88 to 0.69, read as two tests.

In the power module, `TTestIndPower().power(1.0, 16, 0.05)` returns 0.781398, and `solve_power(effect_size=0.5, power=0.8, alpha=0.05)` returns 63.77. That is a continuous solution of the power equation; round it up to 64 per group, where the exact power is 0.8015.

One output to distrust. In SciPy 1.18.1 the lower tail, `nct.cdf(-c, df, λ)`, can return `nan` once λ passes about 8, and statsmodels 0.15.0 passes it on: `TTestIndPower().power(1.0, 132, 0.05)` returns `nan` for a design whose power the integral puts at 1 to nine decimals. The lab takes the lower tail as `nct.sf(c, df, -λ)`, the same number by symmetry, which underflows cleanly to 0.

The lab's `testing.py` runs every number in this post in seven stages; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading p = 0.03 as a 3% chance that the result is a fluke. The p-value is computed assuming no effect, so it cannot be the probability of no effect. In a 78%-power experiment, an observed p of .03 leaves a 17% chance of no effect at even prior odds and 64% at a prior of 0.1, and a significant estimate from a low-powered design is exaggerated however small its p.

- **Reading a non-significant result as no effect.** Of 63 non-significant replications, only 2 could rule out an effect of 0.1. Name the smallest effect that matters and run TOST, with a sample sized for it.
- **Observed power.** It is the p-value on another scale. For design analysis, take the effect from outside the data: earlier literature, a meta-analysis, or what the measurement can plausibly move.
- **Planning with a published effect.** It passed the significance filter, so it is inflated, and most when the original study was small. Shrink it before computing power.
- **Peeking.** Testing as data arrive and stopping at significance turned a 5% test into 28.5% over 91 looks. Fix the sample size, or use a sequential design with adjusted bars.
- **Trusting one design analysis.** Type S and M are only as good as the assumed effect; report a range, and consider the critical effect size and tests against a minimum effect.
- **Counting tests one at a time.** Each p-value is uniform under its own null, so many tests produce small p-values by design. Correcting for many tests at once is the subject of a later part of this series.
- **Discrete tests.** For counts and small tables the p-value takes few values and is not uniform; a nominal 5% test can reject less, or more, as the fourth part's exact sizes showed.

## Key takeaways

- A p-value is a tail area computed assuming no effect, and a random variable: uniform under a true null with a fixed design, and only weakly informative when power is low (median p 0.487 at 5.7% power).
- Power is fixed before the data. For two groups it comes from the noncentral t: 64 per group for d = 0.5 at 80%. Observed power is just p re-expressed.
- Significance is a filter. At 5.7% power every significant estimate is at least 7.9 times a plausible 2-point effect and 24% point the wrong way; replications in psychology kept half the original effect.
- The chance a significant result is false needs a prior: 36% at a prior of 0.1 and 80% power. An observed p = .03 leaves 17% at even odds, and 3% only if you were already 87% sure of the effect.
- A non-significant result is not evidence of no effect. Equivalence needs two one-sided tests and more data than detection: 16 per group can rule out only effects larger than 1.06 SD.

## Try it yourself

**E1, reproduce.** For the worked example's design (standard error 8.1, significance at |d| above 15.88), compute power, the type S rate and the smallest possible exaggeration if the true effect were 4 points instead of 2.

<details><summary>Answer</summary>

λ = 4/8.1 = 0.494. Above the bar: P(Z ≥ (15.88 − 4)/8.1) = P(Z ≥ 1.466) = 0.0713; below it: P(Z ≤ −2.454) = 0.0071. Power 0.0784, type S 0.0071/0.0784 = 9.0%, and every significant estimate is at least 15.88/4 = 3.97 times the effect. The lab's closed form gives 0.0784 and 0.0902, and an exaggeration ratio of 4.85.

</details>

**E3, predict.** Double the worked example's sample size, so the standard error falls to 8.1/√2 = 5.73, and keep D = 2. Before computing, predict whether power, type S and the exaggeration ratio rise or fall, and roughly how far.

<details><summary>Answer</summary>

λ rises from 0.247 to 0.349: power 6.41%, type S 16.3%, exaggeration 6.78, and the bar falls to 11.23 points. Doubling the data barely helps, because the effect is small compared with the noise: power grows with λ, and λ grows only with the square root of the sample size. Getting to 80% power needs λ = 2.80, about 129 times the original data.

</details>

The lab carries the full ladder, from reproducing these numbers to diagnosing a simulation whose exaggeration ratio comes out half the closed form and designing a sequential test that keeps its 5%, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E5 exercises with answers, and cleanup.
- [`testing.py`](LAB_02) — the seven stages: pvalues, power, retrodesign, replication, fpr, tost and stopping.
- [`requirements.txt`](LAB_03) — the pinned NumPy, SciPy, statsmodels and pandas versions.
- [`osc2015_rpp_pairs.csv`](LAB_04) — the Reproducibility Project's 100 coded replications (CC0), with provenance; put it in a `data` folder.
- [`captures.json`](LAB_05) — the author's full run, machine-readable, with the private cross-checks against R.
- [`captures-quick.json`](LAB_06) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_07) — the author's full run as printed.
- [`notebook.ipynb`](LAB_08) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-hypothesis-testing-p-values-power.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. K. M. Durante, A. Rae and V. Griskevicius. "The fluctuating female vote: politics, religion, and the ovulatory cycle." *Psychological Science* 24(6): 1007–1016, 2013. https://doi.org/10.1177/0956797612466416
2. A. Gelman and J. Carlin. "Beyond power calculations: assessing type S (sign) and type M (magnitude) errors." *Perspectives on Psychological Science* 9(6): 641–651, 2014. https://doi.org/10.1177/1745691614551642
3. R. A. Fisher. *Statistical Methods for Research Workers*. Oliver and Boyd, 1925. https://psychclassics.yorku.ca/Fisher/Methods/
4. J. Neyman and E. S. Pearson. "On the problem of the most efficient tests of statistical hypotheses." *Philosophical Transactions of the Royal Society A* 231: 289–337, 1933. https://doi.org/10.1098/rsta.1933.0009
5. R. Hubbard and M. J. Bayarri. "Confusion over measures of evidence (p's) versus errors (α's) in classical statistical testing." *The American Statistician* 57(3): 171–178, 2003. https://doi.org/10.1198/0003130031856
6. E. L. Lehmann. "The Fisher, Neyman-Pearson theories of testing hypotheses: one theory or two?" *Journal of the American Statistical Association* 88(424): 1242–1249, 1993. https://doi.org/10.1080/01621459.1993.10476404
7. R. L. Wasserstein and N. A. Lazar. "The ASA statement on p-values: context, process, and purpose." *The American Statistician* 70(2): 129–133, 2016. https://doi.org/10.1080/00031305.2016.1154108
8. S. Greenland, S. J. Senn, K. J. Rothman, J. B. Carlin, C. Poole, S. N. Goodman and D. G. Altman. "Statistical tests, P values, confidence intervals, and power: a guide to misinterpretations." *European Journal of Epidemiology* 31(4): 337–350, 2016. https://doi.org/10.1007/s10654-016-0149-3
9. H. M. J. Hung, R. T. O'Neill, P. Bauer and K. Köhne. "The behavior of the p-value when the alternative hypothesis is true." *Biometrics* 53(1): 11–22, 1997. https://doi.org/10.2307/2533093
10. D. J. Murdoch, Y.-L. Tsai and J. Adcock. "P-values are random variables." *The American Statistician* 62(3): 242–245, 2008. https://doi.org/10.1198/000313008X332421
11. G. Cumming. "Replication and p intervals: p values predict the future only vaguely, but confidence intervals do much better." *Perspectives on Psychological Science* 3(4): 286–300, 2008. https://doi.org/10.1111/j.1745-6924.2008.00079.x
12. P. Armitage, C. K. McPherson and B. C. Rowe. "Repeated significance tests on accumulating data." *Journal of the Royal Statistical Society A* 132(2): 235–244, 1969. https://doi.org/10.2307/2343787
13. J. P. Simmons, L. D. Nelson and U. Simonsohn. "False-positive psychology: undisclosed flexibility in data collection and analysis allows presenting anything as significant." *Psychological Science* 22(11): 1359–1366, 2011. https://doi.org/10.1177/0956797611417632
14. S. J. Pocock. "Group sequential methods in the design and analysis of clinical trials." *Biometrika* 64(2): 191–199, 1977. https://doi.org/10.1093/biomet/64.2.191
15. statsmodels 0.15.0 documentation, `TTestIndPower` and `ttost_ind`. https://www.statsmodels.org/stable/generated/statsmodels.stats.weightstats.ttost_ind.html (accessed 2026-10-29)
16. SciPy 1.18.1 documentation, `scipy.stats.nct`. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nct.html (accessed 2026-10-29)
17. J. M. Hoenig and D. M. Heisey. "The abuse of power: the pervasive fallacy of power calculations for data analysis." *The American Statistician* 55(1): 19–24, 2001. https://doi.org/10.1198/000313001300339897
18. S. Kanazawa. "Beautiful parents have more daughters: a further implication of the generalized Trivers–Willard hypothesis." *Journal of Theoretical Biology* 244(1): 133–140, 2007. https://doi.org/10.1016/j.jtbi.2006.07.017
19. J. Lu, Y. Qiu and A. Deng. "A note on Type S/M errors in hypothesis testing." *British Journal of Mathematical and Statistical Psychology* 72(1): 1–17, 2019. https://doi.org/10.1111/bmsp.12132
20. D. Lakens, C. Mesquida, G. Xavier-Quintais, S. Rasti, E. Toffalini and G. Altoè. "Rethinking type S and type M errors." *Advances in Methods and Practices in Psychological Science* 9(2), 2026. https://doi.org/10.1177/25152459261432530
21. E. W. van Zwet and E. A. Cator. "The significance filter, the winner's curse and the need to shrink." *Statistica Neerlandica* 75(4): 437–452, 2021. https://doi.org/10.1111/stan.12241
22. Open Science Collaboration. "Estimating the reproducibility of psychological science." *Science* 349(6251): aac4716, 2015. https://doi.org/10.1126/science.aac4716
23. Reproducibility Project: Psychology. `rpp_data.csv`, Open Science Framework, CC0 1.0, 2015. https://osf.io/fgjvw/ (accessed 2026-10-29)
24. J. P. A. Ioannidis. "Why most discovered true associations are inflated." *Epidemiology* 19(5): 640–648, 2008. https://doi.org/10.1097/EDE.0b013e31818131e7
25. D. T. Gilbert, G. King, S. Pettigrew and T. D. Wilson. "Comment on 'Estimating the reproducibility of psychological science'." *Science* 351(6277): 1037, 2016. https://doi.org/10.1126/science.aad7243
26. C. J. Anderson, Š. Bahník, M. Barnett-Cowan et al. "Response to comment on 'Estimating the reproducibility of psychological science'." *Science* 351(6277): 1037, 2016. https://doi.org/10.1126/science.aad9163
27. D. Colquhoun. "An investigation of the false discovery rate and the misinterpretation of p-values." *Royal Society Open Science* 1(3): 140216, 2014. https://doi.org/10.1098/rsos.140216
28. D. Colquhoun. "The reproducibility of research and the misinterpretation of p-values." *Royal Society Open Science* 4(12): 171085, 2017. https://doi.org/10.1098/rsos.171085
29. J. P. A. Ioannidis. "Why most published research findings are false." *PLoS Medicine* 2(8): e124, 2005. https://doi.org/10.1371/journal.pmed.0020124
30. D. J. Benjamin, J. O. Berger, M. Johannesson, B. A. Nosek, E.-J. Wagenmakers et al. "Redefine statistical significance." *Nature Human Behaviour* 2(1): 6–10, 2018. https://doi.org/10.1038/s41562-017-0189-z
31. S. Goodman and S. Greenland. "Why most published research findings are false: problems in the analysis." *PLoS Medicine* 4(4): e168, 2007. https://doi.org/10.1371/journal.pmed.0040168
32. L. R. Jager and J. T. Leek. "An estimate of the science-wise false discovery rate and application to the top medical literature." *Biostatistics* 15(1): 1–12, 2014. https://doi.org/10.1093/biostatistics/kxt007
33. D. Lakens, F. G. Adolfi, C. J. Albers, F. Anvari, M. A. J. Apps et al. "Justify your alpha." *Nature Human Behaviour* 2(3): 168–171, 2018. https://doi.org/10.1038/s41562-018-0311-x
34. R. L. Wasserstein, A. L. Schirm and N. A. Lazar. "Moving to a world beyond 'p below 0.05'." *The American Statistician* 73(sup1): 1–19, 2019. https://doi.org/10.1080/00031305.2019.1583913
35. Y. Benjamini, R. D. De Veaux, B. Efron, S. Evans, M. Glickman, B. I. Graubard et al. "The ASA president's task force statement on statistical significance and replicability." *The Annals of Applied Statistics* 15(3): 1084–1085, 2021. https://doi.org/10.1214/21-AOAS1501
36. D. Lakens. "Equivalence tests: a practical primer for t tests, correlations, and meta-analyses." *Social Psychological and Personality Science* 8(4): 355–362, 2017. https://doi.org/10.1177/1948550617697177
37. D. J. Schuirmann. "A comparison of the two one-sided tests procedure and the power approach for assessing the equivalence of average bioavailability." *Journal of Pharmacokinetics and Biopharmaceutics* 15(6): 657–680, 1987. https://doi.org/10.1007/BF01068419
38. D. Lakens, A. M. Scheel and P. M. Isager. "Equivalence testing for psychological research: a tutorial." *Advances in Methods and Practices in Psychological Science* 1(2): 259–269, 2018. https://doi.org/10.1177/2515245918770963
