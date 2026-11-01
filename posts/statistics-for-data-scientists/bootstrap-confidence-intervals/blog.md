---
title: "The Bootstrap: From Percentile to BCa, and Where It Breaks"
slug: bootstrap-confidence-intervals
date: 2026-11-01
updated: 2026-11-01
summary: "The bootstrap gives a 95% interval for any statistic, but it treats the sample as the population. Measured coverage of seven intervals, and where each breaks."
tags: [data-science, statistics, bootstrap, confidence-interval, coverage-probability, bca-interval, resampling]
category: data-science
series: statistics-for-data-scientists
series_position: 7
tier: L4
difficulty: advanced
prerequisites: ["confidence intervals and coverage", "the standard error and the t statistic", "Python with NumPy and SciPy"]
reading_minutes: 35
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/bootstrap-confidence-intervals"
---

![Two cdfs of the largest of five tank serials: the bootstrap's jumps by 0.67 at 303 and stops there; the true one rises smoothly to 342](COVER)

> [!NOTE]
> **Insights** — The bootstrap estimates a statistic's sampling distribution by recomputing it on resamples of the data, so it gives a standard error and a confidence interval where no formula exists, but it is not assumption-free: it treats the sample as the population. For the correlation of LSAT and GPA in Efron and Tibshirani's 15 law schools, fresh samples from the 82 schools they came from show 95% bootstrap intervals covering 80.7% (basic), 91.0% (percentile) and 92.0% (BCa). On skewed customer spend at n = 30, BCa covers 73.3% and the bootstrap-t 80.3%, against the t-interval's 66.0%, because most samples hold none of the few large customers. For a sample maximum every percentile-type interval stops at the largest value it has seen, and infinite variance and dependent data break the method too.

**Level:** advanced · **You need:** confidence intervals and coverage; the standard error and the t statistic; Python with NumPy and SciPy · **Time:** ~35 min

**Jump to:** [worked example](#worked-example) · [the intervals](#how-does-each-interval-turn-replicates-into-limits) · [coverage](#which-interval-keeps-its-promise-for-the-law-schools) · [how many resamples](#how-many-resamples-does-an-interval-need) · [skewed means](#does-the-bootstrap-rescue-the-skewed-mean) · [failures](#when-does-the-bootstrap-fail) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **computed** or **measured** come from its lab: one NumPy and SciPy script, seeded so every number repeats exactly, plus an optional R script whose output ships with it. Each simulated rate is printed as an estimate ± its Monte Carlo standard error (MCSE). Published numbers are **quoted**, and library conventions are read from the libraries' source code.

## Why this matters

A correlation, a median, a ratio of two means or an AUC has either no standard-error formula or one that rests on assumptions you cannot check, and the bootstrap is the standard answer: recompute the statistic on thousands of resamples of the data and read its spread. Libraries make it one call. SciPy's `stats.bootstrap` returns a BCa interval unless told otherwise, and R's `boot.ci` returns up to five intervals from one bootstrap. <!-- L01 --> <!-- L02 --> Ask for a 95% interval for the correlation between average LSAT score and average GPA across 15 American law schools and the common constructions disagree: 0.33 to 0.94 from one, 0.59 to 1.10 from another, −0.46 to 1.00 from a third. Two of the seven reach above 1, which no correlation can. Which one keeps its 95%, and is the method as assumption-free as its reputation? Both questions have measured answers here, because the 15 schools are a sample from a published population of 82.

## The problem

A statistic θ̂ = s(x) is computed from an independent sample x = (x₁, …, xₙ) of an unknown distribution F. Its standard error is the standard deviation of θ̂ over repeated samples from F, which you cannot draw. Efron's **bootstrap**, introduced in 1979, substitutes an estimate for F: the **empirical distribution** F̂, which puts probability 1/n on each observed point. <!-- L03 --> Drawing an independent sample of size n from F̂ is the same as drawing n points with replacement from the data. That resample is a **bootstrap sample** x\*, the statistic computed on it is a **bootstrap replicate** θ̂\* = s(x\*), and the standard deviation of B replicates is the **bootstrap standard error**. It is a plug-in estimate: the true standard error is a function of F, evaluated at F̂ instead. <!-- L04 --> About 200 replicates usually fix a standard error; an interval needs 1,000 to 2,000, because it reads the tails. <!-- L05 -->

An interval needs more than a spread. The replicates' distribution, the **bootstrap distribution**, also has a shape, and the methods below turn it into limits in different ways. Each rests on conditions, and the three that matter are worth stating before any arithmetic:

1. **The data are an independent sample, and the resampling copies how they were drawn.** Resampling single observations assumes the observations are exchangeable draws; pairs must be resampled as pairs, and a time series is not a set of independent points.
2. **The sample stands in for the population.** F̂ has only the n values the sample holds. Whatever the statistic depends on, its tail, its extremes, its rare large values, must be represented in them.
3. **The statistic is smooth in F.** A small change in the distribution must make a small change in the statistic's sampling distribution. Means, correlations and most estimators are smooth; the maximum is not.

Bickel and Freedman proved the bootstrap asymptotically valid in many situations, including t statistics, empirical and quantile processes and von Mises functionals, and gave counterexamples where it fails. <!-- L06 --> This part computes the common intervals by hand, measures what each delivers against a population it can sample, and tests the claim that **"the bootstrap is assumption-free"** by breaking each condition in turn.

## Worked example

The law-school data come from Efron and Tibshirani's *An Introduction to the Bootstrap*, through its companion R package: a random sample of 15 American law schools from a universe of 82, with two measurements per school: average score on a national law test (LSAT) and average undergraduate grade-point average (GPA). <!-- L07 --> The 15 schools' correlation is r = 0.776; the correlation across all 82 is ρ = 0.760 (Figure 1).

![LSAT against GPA for 82 law schools with the 15 sampled schools highlighted; correlation 0.776 in the sample, 0.760 in all 82](FIG_01)
*Figure 1. The population is published, so every interval's coverage can be checked against ρ. Schools keep their numbers among the 82; school 6, a high GPA for its LSAT, is the point that pulls the sample's r down.*

**One resample.** Number the table's 15 rows 1 to 15 and draw 15 row numbers with replacement. The lab's first draw is 10, 13, 15, 11, 11, 6, 15, 5, 6, 12, 8, 3, 12, 2, 1: rows 6, 11, 12 and 15 twice each, rows 4, 7, 9 and 14 not at all. Each row keeps its school's LSAT and GPA together, so the resample is 15 rows of the original table with repeats. Its correlation is r\* = 0.720. Any given school is missing from a resample with probability (14/15)¹⁵ = 0.355, so a resample holds about 9.7 distinct schools; this one holds 11.

**The bootstrap standard error.** Ten thousand resamples give 10,000 replicates with mean 0.769 and standard deviation 0.135. That is the bootstrap standard error. The normal-theory formula (1 − r²)/√(n − 3) gives 0.115, and it assumes the 15 pairs are bivariate normal. Because the population is published, the true standard error can be measured: a million fresh samples of 15 from the 82 schools give 0.130 (Figure 2). The bootstrap's 0.135 is close; the formula is 0.015 too small.

![Histogram of 10,000 bootstrap correlations beside the true sampling distribution from the 82 schools; both skewed left, SE 0.135 and 0.130](FIG_02)
*Figure 2. The bootstrap copies the shape and the spread of the sampling distribution, centred on the sample's r rather than on ρ. Both have a long left tail.*

Both distributions are skewed left: a correlation near 0.8 has more room below than above. Seven intervals turn the 10,000 replicates into limits.

1. **Percentile.** The replicates' 2.5% and 97.5% points: 0.452 to 0.962.
2. **Basic.** Reflect those points about r: 2r − 0.962 = 0.590 to 2r − 0.452 = 1.100. The long left tail becomes a long right arm, past 1.
3. **Normal with the bootstrap SE.** r ± 1.96 × 0.135: 0.511 to 1.042, past 1 again.
4. **Studentized.** Give every replicate its own standard error, from the delta-method formula under The math (0.124 for the original 15 schools), and collect t\* = (r\* − r)/SE\*. Its 2.5% and 97.5% points are −1.78 and 9.97, so the interval is 0.776 − 0.124 × 9.97 = −0.462 to 0.776 + 0.124 × 1.78 = 0.997.
5. **Studentized on Fisher's scale.** The same, after transforming r to z = atanh r: −0.142 to 0.946.
6. **BCa.** Two numbers adjust the percentile levels. The **bias correction** z₀ asks whether the replicates sit centred on r: 4,630 of the 10,000 lie below it, a share of 0.463, and z₀ = Φ⁻¹(0.463) = −0.093, where Φ is the standard normal cdf. Its target is the share of real samples whose r falls below ρ: 46.8% in the million fresh samples, close to the bootstrap's 46.3%. The **acceleration** a measures how fast the standard error changes with the parameter, and is estimated from the **jackknife**: recompute r with each school left out in turn (Figure 3). With d the jackknife mean minus each leave-one-out value, a = Σd³/(6(Σd²)^1.5) = −0.0757. The levels become Φ(z₀ + (z₀ + z)/(1 − a(z₀ + z))) for z = ±1.96: the 0.58% and 93.86% points of the replicates, 0.327 to 0.942. <!-- L08 -->
7. **Fisher's z, normal theory.** tanh(atanh 0.776 ± 1.96/√12) = 0.439 to 0.922, assuming bivariate normal data. <!-- L09 -->

![The 15 leave-one-out correlations: 14 between 0.73 and 0.82, school 6 at 0.893; the acceleration is −0.0757](FIG_03)
*Figure 3. One school sets the acceleration. Leaving out school 6 raises r to 0.893; its term is 110% of Σd³, because the other schools' terms partly cancel.*

Figure 4 sets the seven side by side. On the same replicates, SciPy's `stats.bootstrap` and R's `boot.ci` give the same limits as the hand computation to 14 decimal places, once their conventions are matched; the conventions differ, and the Implementation section reads them.

![Seven 95% intervals for the same 15 schools, from the percentile's 0.45 to 0.96 to the studentized −0.46 to 1.00 and the basic past 1](FIG_04)
*Figure 4. One sample, seven answers. The basic and normal intervals cross 1; the studentized interval reaches below zero; BCa stretches the percentile interval down.*

## Intuition

The bootstrap sets up a second world beside the real one (Figure 5). In the real world, the population F generates samples, and r varies around ρ with some sampling distribution: that variation is what an interval needs and what you cannot see. In the bootstrap world, the sample plays the population: F̂ generates resamples, and r\* varies around r. That variation you can compute, as often as you like. The method's bet is that the second relation copies the first: that r\* − r behaves like r − ρ.

![Two parallel chains: the 82 schools generate samples and r around rho; the 15 schools generate resamples and r* around r](FIG_05)
*Figure 5. The bootstrap swaps the population for the sample. Every interval below is a different way of reading the bottom row as if it were the top.*

The analogy breaks wherever the bootstrap world is missing something the real world has. Its population holds only the n values the sample holds: no value larger than the sample's maximum, no customer the sample did not catch, no time order the resampling did not keep. Every failure later in this part is one of those absences.

## How does each interval turn replicates into limits?

The constructions differ in what they assume about the relation between the two worlds.

**Percentile.** It takes the replicates' own quantiles as the limits. The justification is a transformation: if some monotone function m makes m(θ̂) normal around m(θ) with a constant variance and no bias, the percentile interval is exactly right, and the analyst never needs to know m. The interval is **transformation invariant**: compute it for r or for atanh r and map the limits, and you get the same answer. <!-- L10 --> What it ignores is a bias or a standard error that changes with θ.

**Basic.** It treats r\* − r as a copy of r − ρ: if the replicates run from 0.324 below r to 0.186 above it, ρ should run from 0.186 below r to 0.324 above. The reflection is right when the sampling distribution keeps its shape as θ moves, and wrong when it does not. Davison and Hinkley call this the basic interval, and Hesterberg calls it the reverse percentile interval: for skewed data it is asymmetric in the wrong direction, and in his simulations on an exponential population its coverage was the worst of the seven intervals he compared. <!-- L15 -->

**Studentized (bootstrap-t).** It copies Student's construction: divide by an estimated standard error to make a near-pivot, then let the bootstrap estimate the pivot's distribution instead of the t table. It needs a standard error for every replicate, and it is not transformation invariant. For a correlation, Efron and Hastie report that it agrees well with exact intervals on Fisher's scale and looks out of place on the raw scale. <!-- L16 --> The worked example shows why: a resample that misses school 6 has r\* close to 1, where a correlation's standard error is small, so its t\* can be huge, and the 97.5% point of t\* lands at 9.97 instead of near 2.

**BCa (bias-corrected and accelerated).** Efron's 1987 method starts from the percentile interval and adds two corrections. <!-- L08 --> z₀ corrects median bias: if fewer than half the replicates lie below θ̂, the estimate is biased upward on the transformed scale, and the levels shift down. a corrects a standard error that changes with the parameter; for a positive correlation the standard error shrinks as ρ approaches 1, so a should be negative, as it is here, and the lower level is stretched further than the upper. With a = 0, BCa reduces to the bias-corrected (BC) interval, and with z₀ = 0 too, to the percentile interval. <!-- L12 --> Figure 6 draws the map from nominal to adjusted levels for the law schools.

![BCa's adjusted levels against nominal levels for z0 = −0.093 and a = −0.076, beside BC's curve and the percentile method's diagonal](FIG_06)
*Figure 6. z₀ shifts the levels and a bends them: the nominal 2.5% point becomes the 0.58% point and the 97.5% point the 93.86% point.*

Efron and Hastie advise that BC and BCa work most dependably when z₀ and a are small, say no more than 0.2 in absolute value, and treat a large z₀ as a warning of bias. <!-- L13 --> Here both are below 0.1.

**What "second-order accurate" means.** An interval is **first-order accurate** if its one-sided coverage errors shrink like 1/√n, so quartering the error needs sixteen times the data, and **second-order accurate** if they shrink like 1/n. BCa and the bootstrap-t are second-order accurate in smooth problems; the percentile and BC intervals are not. <!-- L11 --> Hall's comparison of seven bootstrap methods singled out the bootstrap-t and BCa and confirmed Efron's conjecture that BCa is second-order correct. <!-- L14 --> The advantage is in the tails taken one at a time. For an interval symmetric about θ̂, even the normal approximation's coverage error is of order 1/n, while its one-sided errors are of order 1/√n. <!-- L36 --> So a fair test of an interval counts its misses on each side: a 95% interval should miss 2.5% of the time below and 2.5% above, because a miss on one side is not repaired by fewer misses on the other. <!-- L37 -->

## Which interval keeps its promise for the law schools?

The population is published, so coverage can be measured, as the sixth part of this series, *Confidence Intervals: What 95% Means, Measured*, measured it for proportions. Draw 15 schools with replacement from the 82, build all seven intervals from 2,000 replicates, check whether each contains ρ = 0.760, and repeat 20,000 times (Figure 7).

![Coverage of seven 95% intervals over 20,000 samples of 15 from the 82 schools, split into misses on each side; 80.7% to 95.7%](FIG_07)
*Figure 7. At n = 15 no percentile-type interval reaches 95%. The raw bootstrap-t does, by producing upper limits above 1 in 23.5% of samples.*

| Interval | Coverage | Interval above ρ | Interval below ρ | Median width |
|---|---|---|---|---|
| Normal, bootstrap SE | 89.0% | 10.2% | 0.9% | 0.465 |
| Percentile | 91.0% | 6.9% | 2.2% | 0.454 |
| Basic | 80.7% | 18.7% | 0.7% | 0.454 |
| Studentized | 95.7% | 2.6% | 1.7% | 0.685 |
| Studentized, Fisher scale | 93.8% | 2.9% | 3.3% | 0.599 |
| BCa | 92.0% | 5.0% | 3.0% | 0.490 |
| Fisher z, normal theory | 93.6% | 4.5% | 2.0% | 0.497 |

Each coverage carries an MCSE between 0.1 and 0.3 points. Four results stand out.

- **The basic interval covers 80.7%.** It misses high in 18.7% of samples, seven and a half times its 2.5% share, because it puts the long arm on the wrong side, and 69.6% of its upper limits are above 1.
- **BCa improves on the percentile interval, but only by a point.** Its corrections move misses from the high side to the low side, 5.0% and 3.0% against 6.9% and 2.2%, and the coverage from 91.0% to 92.0%. Across the 20,000 samples the median z₀ was −0.095 and the median a 0.003, with half of all a values between −0.028 and 0.041: at n = 15 the jackknife's estimate of a is mostly noise around a small value.
- **The raw bootstrap-t reaches 95.7% by width.** Its median width is 0.685, 40% wider than BCa's, and its upper limit exceeds 1 in 23.5% of samples. On Fisher's scale it covers 93.8% with the best-balanced misses, 2.9% and 3.3%, at a median width of 0.599.
- **Normal theory holds up.** Fisher's z-interval assumes bivariate normal data, which a population of 82 schools cannot be, and still covers 93.6%, better than any percentile-type interval.

Second-order accuracy is a rate, not a guarantee at n = 15. Polansky showed that intervals read off the percentiles of a bootstrap distribution have upper bounds on their finite-sample coverage, which can be low even for second-order accurate methods. <!-- L20 --> The doubts are older than BCa: Schenker found that the percentile and BC intervals for a normal variance cover well below their nominal level in small and moderate samples. <!-- L18 -->

## How many resamples does an interval need?

B sets how much of an interval is Monte Carlo noise rather than data. Rerun the worked example's bootstrap 200 times on the same 15 schools, changing only the random draws, and record how much each endpoint moves (Figure 8).

![Monte Carlo SD of the percentile and BCa endpoints against B on log axes; BCa's lower limit needs about five times the replicates](FIG_08)
*Figure 8. BCa's lower limit sits near the 0.6th percentile of the replicates, the noisiest number in the analysis.*

At B = 2,000 the percentile interval's lower limit moves with a standard deviation of 0.012 and BCa's with 0.026; at B = 10,000 BCa's still moves by 0.012, as much as the percentile limit at 2,000. The upper limits move by 0.001 to 0.003, and the bootstrap standard error itself by 0.003 at B = 2,000, about 2% of its value. BCa's lower limit is the 0.58% point: at B = 2,000 only about 12 replicates lie below it, so it is a statistic of a dozen values. R's own run of the analysis, with its own 2,000 replicates and its own acceleration, puts the lower limit at 0.302; SciPy's convention on 10,000 other resamples puts it at 0.355; the worked example's 0.327 lies between. Each is right for its draws.

The rule of thumb, about 200 replicates for a standard error and 1,000 to 2,000 for an interval, is a floor. <!-- L05 --> Hall showed that for the bootstrap-t a small B keeps the coverage improvement when the nominal level is a multiple of 1/(B + 1), at the price of longer intervals. <!-- L17 --> When an endpoint matters, rerun it with a second seed and report its Monte Carlo error, or raise B until that error is small against the interval's width.

## Does the bootstrap rescue the skewed mean?

The sixth part of this series ended on a failure. On the net spend of 4,317 customers of an online retailer, skewness 21.6, the 95% t-interval for the mean covered 65.8% of the time at n = 30, and intervals that adapt to skew were left for later. <!-- L35 --> The bootstrap intervals adapt: BCa's acceleration for a mean is the sample's skewness divided by 6√n, and the bootstrap-t reads the skew of t\* directly. Figure 9 measures them with 2,000 replicates per interval, on 20,000 samples at n = 30 and 8,000 at n = 100.

![Coverage of six intervals for mean spend at n = 30 and 100, overall and split by whether the sample holds a top-1% customer](FIG_09)
*Figure 9. With a large customer in the sample, every interval covers at least 92% of the time; without one, none covers more than 74%, because no resample can contain what the sample lacks.*

At n = 30 the t-interval covers 66.0% ± 0.3, in line with the sixth part's 65.8%; the percentile interval 66.8%, the basic 60.3%, BCa 73.3% and the bootstrap-t 80.3%. At n = 100: 70.1%, 72.0%, 66.2%, 77.0% and 80.3%. Adapting to skew buys 7 to 14 points at n = 30 and leaves every interval at least 14 points short of 95%. The bootstrap-t did best, as it did for skewed populations in Hesterberg's comparisons. <!-- L19 -->

The split shows where the misses come from. The top 1% of customers, 44 people who spent £17,507 or more, account for 29.9% of all spending. A sample of 30 contains at least one of them with probability 1 − (1 − 44/4,317)³⁰ = 26.5%. When it does, BCa covers 97.0% and the bootstrap-t 99.4%. When it does not, nearly three times in four, they cover 64.8% and 73.5%: the sample's mean is low, its spread is small, and its bootstrap world has no large customer at all, so no resample can show one. At n = 100, the 36% of samples without a top-1% customer are covered by BCa only 40.4% of the time. This is the second condition failing, not a defect of BCa: the sample does not stand in for the population's tail, and no rule for reading replicates can supply values that none of them contain.

## When does the bootstrap fail?

Three conditions, each broken on purpose.

### The maximum

The third part of this series, *Estimators and Their Errors: Why the Best One Can Be Biased*, estimated the number of German tanks N from five captured serial numbers, 58, 171, 272, 273 and 303, with N = 342 the truth. Bootstrap the maximum of those five. With only 5⁵ = 3,125 equally likely resamples, its bootstrap distribution can be listed exactly: a resample's maximum is 303 unless all five draws miss serial 303, so P\*(M\* = 303) = 1 − (4/5)⁵ = 0.672, and the rest falls on 273, 272, 171 and 58. The true distribution of the maximum of five serials from 342 has no such atom: it puts 0.009 on 303 and spreads its mass up to 342 (Figure 10).

![Bootstrap distribution of the maximum of five tank serials, 67% on 303, beside the true distribution of the maximum for N = 342](FIG_10)
*Figure 10. The bootstrap puts two thirds of its mass on the observed maximum, and none above it. The sampling distribution it should copy is smooth and runs to 342.*

Every interval read from percentiles of this distribution ends at 303 or below: percentile 272 to 303, BCa 171 to 303 or 273 to 303, depending on how z₀ counts the replicates that tie the maximum (Figure 11). Over every possible capture of five tanks, these intervals contain N only when tank 342 itself is captured, which happens 5/342 = 1.46% of the time. The basic interval reflects past 303, to 334, and covers 75.73%. An interval built from the exact distribution of the maximum, the distribution the third part computed, runs from 303 to 549 and covers at least 95%.

![Intervals for the tank count from five serials: percentile, basic and two BCa variants stop at 334 or below; N = 342; exact bound 549](FIG_11)
*Figure 11. Every percentile-type interval stops at the largest serial. Over all captures they cover N = 342 only when tank 342 itself is caught: 1.46%.*

More data does not fix it. For a sample of n from a uniform distribution, the bootstrap maximum equals the sample maximum with probability 1 − (1 − 1/n)ⁿ, which is 0.634 at n = 100 and tends to 1 − 1/e = 0.632, while the true maximum has no atom at all. The bootstrap therefore cannot estimate the maximum's distribution, the counterexample Bickel and Freedman gave in 1981. <!-- L21 --> The percentile and BCa intervals for the upper endpoint cover 0%, at every n. The basic interval reflects at the fourth-largest value, and it covers exactly when the gap above the maximum is shorter than the three gaps below it: 7/8 = 87.5% at every n from 10 up (simulated: 87.4% to 87.6% ± 0.1). The repair is to resample fewer points: drawing m observations, with m growing more slowly than n, makes the bootstrap consistent for the maximum and for Bickel and Freedman's other counterexamples. <!-- L22 -->

### Infinite variance

Take a Pareto population with tail index 1.5: P(X > x) = x^−1.5 for x ≥ 1, with mean 3 and infinite variance. A sample of 100 from it is dominated by its few largest values. A resample contains the largest one 0, 1, 2 or 3 times with probabilities close to 0.37, 0.37, 0.18 and 0.06, and each copy moves the resample's mean up by that value divided by n. The bootstrap distribution of the mean is a mixture of overlapping lumps, one per count, so the largest value alone sets much of its spread (Figure 12).

![Bootstrap distributions of the mean for three Pareto samples, coloured by copies of the largest value, and coverage rising from 66% to 85%](FIG_12)
*Figure 12. Resamples sort themselves by how many copies of the largest value they drew, and that one value sets much of the spread. Coverage stays well short of 95% as n grows.*

In the first of three samples the largest value is 22.2, 8.5% of the sample's sum. The other 99 values alone would give the bootstrap mean a standard deviation of 0.188; with the largest it is 0.271, so one value in a hundred supplies about half the bootstrap variance. In the third sample the largest value, 17.5, supplies about a fifth. Same population, same n: how wide the bootstrap distribution is depends on which extreme values the sample happened to catch. Athreya proved that in this setting the bootstrap distribution of the normalized mean converges to a random distribution rather than to the right one, and Knight gave a second proof; Hall showed that the bootstrap distribution then has no fixed limit, and that a few extreme sample values determine it. <!-- L23 --> <!-- L25 --> Giné and Zinn proved that finite variance is necessary for the bootstrap of the mean to work almost surely. <!-- L24 -->

The coverage confirms it. BCa covers 73.2% at n = 30, 78.2% at 100, 80.9% at 300 and 83.6% at 1,000; the bootstrap-t 80.8% and 84.8% at the ends of that range; the t-interval 65.9% and 77.2%. Thirty-three times the data buys about 10 points. The t-interval has no better footing: with infinite variance the t statistic converges to a non-normal limit. <!-- L26 -->

### Dependence

Take a series in which each value is half the previous one plus fresh noise with standard deviation 1, an **autoregressive series of order 1** (AR(1)) with φ = 0.5, so neighbours have a correlation of 0.5. With n = 200, the standard deviation of its mean is 0.141. Resample its 200 values as if they were independent and the bootstrap standard error comes out at 0.574 of that, close to the large-sample value √((1 − φ)/(1 + φ)) = 0.577, because the resamples have lost the correlation: their lag-1 autocorrelation averages −0.005 against the series' 0.487 (Figure 13).

![An AR(1) series and one bootstrap resample of it: lag-1 autocorrelation 0.487 against −0.005; the bootstrap SE is 57% of the true one](FIG_13)
*Figure 13. Resampling single observations shuffles time away. The standard error shrinks to 57% of the truth, and the interval covers 73.5%.*

Over 4,000 series the percentile interval for the mean covers 73.5% ± 0.7. Positive dependence means each new value carries less new information than an independent one would, and independent resampling counts every value as new. Künsch's block bootstrap resamples runs of consecutive observations, which keeps short-range dependence, and Politis and Romano's stationary bootstrap draws runs of random length; both are time-series methods, outside this part. <!-- L27 --> <!-- L28 -->

## The math

| Symbol | Meaning |
|---|---|
| F, F̂ | the population distribution; the empirical distribution, mass 1/n on each observation |
| θ, θ̂, θ̂\* | the parameter; its estimate; the estimate on a bootstrap sample |
| B, Ĝ | the number of replicates; their empirical cdf |
| z_α, Φ | the standard normal α quantile and cdf |
| z₀, a | BCa's bias correction and acceleration |
| θ̂₍ᵢ₎, θ̂₍.₎ | the estimate with observation i left out; their mean |
| ℓᵢ | the empirical influence value of observation i |

**The bootstrap standard error** is the standard deviation of the replicates, the plug-in estimate of the true standard error: <!-- L04 -->

$$
\widehat{\mathrm{se}}_{\mathrm{boot}} = \left[\frac{1}{B-1}\sum_{b=1}^{B}\left(\hat\theta^{*}_{b} - \bar\theta^{*}\right)^{2}\right]^{1/2} \;\to\; \mathrm{Sd}(\hat F) \quad (B \to \infty) \tag{1}
$$

As B grows, the computed value approaches the ideal bootstrap estimate, the standard error the statistic would have if F̂ were the population; for the law schools, 0.135 at B = 10,000.

**Percentile, basic and studentized limits.** With Ĝ the replicates' cdf and t\* = (θ̂\* − θ̂)/se\*, the lower limits are

$$
\hat\theta_{\%}[\alpha] = \hat G^{-1}(\alpha), \qquad \hat\theta_{\mathrm{basic}}[\alpha] = 2\hat\theta - \hat G^{-1}(1-\alpha), \qquad \hat\theta_{t}[\alpha] = \hat\theta - \widehat{\mathrm{se}}\, t^{*(1-\alpha)} \tag{2}
$$

and the upper limits swap α and 1 − α. For the law schools at α = 0.025: 0.452, 2(0.776) − 0.962 = 0.590, and 0.776 − 0.124 × 9.97 = −0.462.

**BCa.** <!-- L08 --> With p₀ the share of replicates below θ̂ and the acceleration estimated from the jackknife,

$$
z_0 = \Phi^{-1}(p_0), \qquad \hat a = \frac{\sum_{i}\left(\hat\theta_{(\cdot)} - \hat\theta_{(i)}\right)^{3}}{6\left[\sum_{i}\left(\hat\theta_{(\cdot)} - \hat\theta_{(i)}\right)^{2}\right]^{3/2}}, \qquad \hat\theta_{\mathrm{BCa}}[\alpha] = \hat G^{-1}\!\left(\Phi\!\left(z_0 + \frac{z_0 + z_\alpha}{1 - \hat a\,(z_0 + z_\alpha)}\right)\right) \tag{3}
$$

The bracket inside Φ is the nominal z shifted twice by z₀, with the second shift divided by a term that falls below 1 when a and the tail have the same sign, which stretches that tail. With z₀ = −0.0929 and a = −0.07567, z_α = −1.96 maps to Φ(−2.524) = 0.0058 and +1.96 to Φ(1.543) = 0.9386.

**The correlation's influence values and standard error.** With xᵢ and yᵢ standardised by their means and standard deviations (divisor n), each school's influence on r is ℓᵢ = x̃ᵢỹᵢ − r(x̃ᵢ² + ỹᵢ²)/2, and the nonparametric delta-method standard error is

$$
\widehat{\mathrm{se}}_{\delta} = \frac{1}{n}\Big(\sum_{i=1}^{n} \ell_i^{2}\Big)^{1/2} \tag{4}
$$

For the 15 schools it is 0.124, the SE used to studentize. The same ℓᵢ, put into Σℓ³/(6(Σℓ²)^1.5), give the acceleration's exact-influence version, −0.08168, which a regression on many replicates approaches.

**The point mass at the maximum.** A resample's maximum equals the sample's when at least one of its n draws picks the largest observation:

$$
P^{*}\left(M^{*} = M\right) = 1 - \left(1 - \tfrac{1}{n}\right)^{n} \;\to\; 1 - e^{-1} = 0.632 \tag{5}
$$

At n = 5 it is 0.672, the tank example's atom; the true maximum of a continuous population has no atom anywhere.

<details>
<summary>Why the basic interval covers exactly 7/8 of the time for a uniform maximum</summary>

P\*(M\* ≤ x₍ₙ₋ⱼ₎) = ((n − j)/n)ⁿ, which is at least 0.025 for j = 3 and below it for j = 4 at every n from 10 up, so the bootstrap's 2.5% point is the fourth-largest observation and the basic interval is M to 2M − x₍ₙ₋₃₎. It contains θ exactly when θ − M ≤ M − x₍ₙ₋₃₎: the top spacing is shorter than the next three together. Uniform spacings are exchangeable and behave as normalised independent exponentials, so the probability is P(E₁ ≤ E₂ + E₃ + E₄) = 1 − (1/2)³ = 7/8, whatever n is.

</details>

**Independent resampling of an AR(1).** For a stationary AR(1) with coefficient φ, the variance of the mean is about (1 + φ)/(1 − φ) times what independent data would give, so a bootstrap that resamples single points estimates √((1 − φ)/(1 + φ)) of the true standard error: 0.577 at φ = 0.5, which the lab measured as 0.574 at n = 200.

## Implementation

A from-scratch BCa in twenty lines. Seeded as the lab's worked example, it prints that example's numbers.

```python
import numpy as np
from scipy import stats

lsat = np.array([576, 635, 558, 578, 666, 580, 555, 661, 651, 605, 653, 575, 545, 572, 594])
gpa = np.array([3.39, 3.30, 2.81, 3.03, 3.44, 3.07, 3.00, 3.43, 3.36, 3.13, 3.12, 2.74, 2.76, 2.88, 2.96])


def corr(x, y):
    """Pearson correlation along the last axis, so one call handles every resample."""
    x, y = x - x.mean(-1, keepdims=True), y - y.mean(-1, keepdims=True)
    return (x * y).sum(-1) / np.sqrt((x * x).sum(-1) * (y * y).sum(-1))


def bca(x, y, rng, B=10_000, alpha=0.025):
    n, r = len(x), corr(x, y)
    idx = rng.integers(0, n, size=(B, n))           # one row of school indices per resample: pairs stay together
    rb = corr(x[idx], y[idx])
    z0 = stats.norm.ppf(np.mean(rb < r))            # bias correction: the share of replicates below r
    jack = np.array([corr(np.delete(x, i), np.delete(y, i)) for i in range(n)])
    d = jack.mean() - jack
    a = (d**3).sum() / (6 * (d**2).sum() ** 1.5)    # acceleration, from the jackknife
    z = stats.norm.ppf([alpha, 1 - alpha])
    levels = stats.norm.cdf(z0 + (z0 + z) / (1 - a * (z0 + z)))
    return r, z0, a, levels, np.quantile(rb, [alpha, 1 - alpha]), np.quantile(rb, levels)


rng = np.random.default_rng(np.random.SeedSequence([0, 0, 20261101]))   # the lab's example stream
r, z0, a, levels, perc, ci = bca(lsat, gpa, rng)
print(f"r {r:.4f}, z0 {z0:+.4f}, a {a:+.5f}, levels {levels.round(5)}, percentile {perc.round(4)}, BCa {ci.round(4)}")
```

It prints r 0.7764, z0 −0.0929, a −0.07567, levels 0.00581 and 0.93859, the percentile interval 0.4523 to 0.9624 and BCa 0.3273 to 0.9421. The one line that matters most is the index array: each resample is a set of rows, so a school's LSAT and GPA travel together.

### Reading the library's output

```python
res = stats.bootstrap((lsat, gpa), lambda x, y, axis: corr(x, y), paired=True, vectorized=True,
                      n_resamples=10_000, rng=np.random.default_rng(1))    # method="BCa" by default
print(res.confidence_interval, res.standard_error)
```

`paired=True` is required for a correlation: without it SciPy resamples each argument separately and destroys the pairing. In SciPy 1.18.1, BCa is the default method and 9,999 the default number of resamples. Its z₀ counts ties as half below and half above, ((#below) + (#at or below))/2B; its acceleration is the jackknife's; its limits are linear-interpolation (type 7) quantiles; and its basic interval is 2θ̂ minus the percentile limits. <!-- L31 --> Fed the same resamples, the hand computation matches all three of its intervals to 2.2 × 10⁻¹⁶.

```r
library(boot)                                   # law: a data frame of the 15 schools' LSAT and GPA
b <- boot(law, function(d, i) cor(d$LSAT[i], d$GPA[i]), R = 2000)
boot.ci(b, type = c("perc", "basic", "bca"))
```

R's `boot.ci` (boot 1.3.32) differs in three places. Its z₀ counts only the replicates strictly below θ̂. Its acceleration comes from `empinf`, which, when no influence values are passed and B is at least n, regresses the replicates on how often each observation was drawn; passing `L = empinf(b, type = "jack")` uses the jackknife instead, uncentred, (n − 1)(θ̂ − θ̂₍ᵢ₎). Its quantiles take the (B + 1)α-th order statistic and interpolate on the normal scale. <!-- L32 --> Its `norm` interval subtracts the bootstrap bias estimate before adding ±1.96 SE, its studentized interval reads the variance as the statistic's second returned value, and its `h`, `hdot` and `hinv` arguments compute any interval on a transformed scale, which is how `crosscheck.R` runs the Fisher-scale bootstrap-t. <!-- L33 --> The package written for Efron and Tibshirani's book, `bootstrap`, has a third BCa, `bcanon`: z₀ strictly below, the centred jackknife, and inverse-cdf (type 1) quantiles. <!-- L34 -->

On one set of 10,000 replicates the four conventions give BCa lower limits of 0.3493 (`boot.ci`'s default), 0.3547 (`bcanon`), 0.3548 (SciPy) and 0.3551 (`boot.ci` with jackknife influence values). The acceleration accounts for most of the spread: −0.08175 from the regression, −0.07567 from the centred jackknife, −0.07409 uncentred, and −0.08168 from the exact influence values of equation (4). From R's own 2,000 replicates, the lab's functions with R's conventions reproduce all seven of `boot.ci`'s limits to 3.9 × 10⁻¹⁵. The lab's `bootstrap.py` computes every number in this post in seven stages, and `crosscheck.R` reruns the worked example in R; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** treating the bootstrap as assumption-free. It assumes an independent sample resampled the way it was drawn, a sample that stands in for the population, and a statistic that changes smoothly with the distribution. Break the first and the standard error shrinks (57% of the truth for an AR(1) with φ = 0.5); break the second and intervals cover 64.8% (BCa on spend samples without a large customer); break the third and percentile intervals cover 0% (a uniform maximum).

- **Using the basic interval for a skewed statistic.** It reflects the bootstrap distribution, so its long arm points the wrong way: 80.7% coverage for the law-school correlation, with upper limits above 1 in 69.6% of samples.
- **Bootstrapping the t statistic of a correlation on the raw scale.** At n = 15 it covered 95.7% only through intervals 40% wider than BCa's, nearly a quarter of them past 1. Studentize on Fisher's scale.
- **Reading BCa's second-order accuracy as small-sample accuracy.** At n = 15 it covered 92.0%, one point more than the percentile interval and less than Fisher's normal-theory interval.
- **Reporting a BCa limit from 1,000 or 2,000 replicates without its Monte Carlo error.** The law schools' lower limit moved with an SD of 0.026 at B = 2,000; rerun with another seed before quoting three decimals.
- **Resampling columns separately.** A correlation, a regression or any paired statistic needs whole rows resampled; drawing each column on its own gives replicates centred on zero.
- **Bootstrapping extremes, endpoints or boundaries.** The maximum, the minimum and an estimated support endpoint break the smoothness condition, and the nonparametric bootstrap is also inconsistent when a parameter sits on the boundary of its space. <!-- L29 --> The fourth part of this series, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, met the same kind of boundary breaking the likelihood-ratio test. Use the m-out-of-n bootstrap or an exact pivot.
- **Heavy tails.** With infinite variance the bootstrap of the mean has no fixed limit; even with finite variance, a small sample of heavily skewed data rarely contains the values that set the mean, and no interval can resample values the sample lacks.
- **Dependent or clustered data.** Resample the independent units: whole clusters, whole subjects, or blocks of a time series.

Bootstrap failures and their repairs, from the m-out-of-n bootstrap to diagnostics for a bootstrap that has gone wrong, are reviewed by Davison, Hinkley and Young and by Canty and colleagues. <!-- L30 --> <!-- L38 -->

## Key takeaways

- The bootstrap estimates a sampling distribution by resampling the data, and its standard error is a plug-in estimate: for 15 law schools, 0.135 against a true 0.130 and a normal-theory 0.115.
- Intervals differ in how they read the replicates. The percentile interval respects transformations of the parameter; BCa adds a bias correction z₀ and an acceleration a, here −0.093 and −0.076, which moved the levels to 0.58% and 93.86%. The basic interval reflects the skew the wrong way.
- Measured against the 82-school population at n = 15, the percentile interval covered 91.0%, BCa 92.0%, Fisher's normal-theory interval 93.6% and the basic interval 80.7%. Second-order accuracy is a rate, not a small-sample guarantee.
- The bootstrap cannot resample values the sample lacks. For skewed spend at n = 30, BCa covered 73.3% and the bootstrap-t 80.3%; samples without a top-1% customer were covered 64.8% and 73.5% of the time.
- It fails outright for extremes (a 63% point mass at the maximum; percentile intervals cover 0%), for infinite variance (no fixed limit) and for dependence (resampling single points erased an autocorrelation of 0.49 and 43% of the standard error).

## Try it yourself

**E1, reproduce.** From the worked example's z₀ = −0.0929 and a = −0.07567, compute BCa's adjusted levels for a 90% interval (nominal 5% and 95%), and the BC levels (a = 0) for the 95% interval.

<details><summary>Answer</summary>

For the 90% interval, z = ∓1.645. Lower: z₀ + z = −1.7378, divided by 1 − a(−1.7378) = 1 − 0.1315 = 0.8685, gives −2.0009; adding z₀ gives −2.0938, and Φ(−2.0938) = 0.0181. Upper: z₀ + z = 1.5520, divided by 1 + 0.1174 = 1.1174, gives 1.3889; adding z₀ gives 1.2960, and Φ(1.2960) = 0.9025. So BCa reads the 1.81% and 90.25% points. The BC levels for 95% are Φ(2z₀ ∓ 1.96) = Φ(−2.1458) = 0.0159 and Φ(1.7742) = 0.9620: the shift alone, without the stretch, moves both levels by about a point.

</details>

**E3, predict.** Leave school 6 out and bootstrap the other 14. Before computing, predict r, whether the bootstrap standard error grows or shrinks and roughly by how much, and what happens to the acceleration.

<details><summary>Answer</summary>

r becomes 0.893, the leave-one-out value in Figure 3. The 14 remaining schools lie close to a line, and a correlation near 1 has little room to vary, so the bootstrap standard error falls from 0.135 to 0.061. The acceleration shrinks from −0.076 to −0.026, because school 6 supplied 110% of Σd³. BCa then reads the 1.17% and 95.37% points, and its interval, 0.714 to 0.970, sits close to the percentile interval, 0.749 to 0.977. The lab's `example` stage with `--drop 6` prints these.

</details>

The lab carries the full ladder, from reproducing these numbers to diagnosing a bootstrap whose interval excludes its own estimate and building the m-out-of-n repair for the maximum, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E5 exercises with answers, and cleanup.
- [`bootstrap.py`](LAB_02) — the seven stages: example, reconcile, coverage, spend, maximum, heavy and dependent.
- [`crosscheck.R`](LAB_03) — optional: the worked example in R's boot package, which writes `crosscheck-r.csv`.
- [`crosscheck-r.csv`](LAB_04) — R's intervals, constants, influence values and 2,000 replicates, so the R comparison runs without R.
- [`law_school_82.csv`](LAB_05) — the 82 law schools and the 15-school sample (BSD 3-clause), with provenance; put it in a `data` folder.
- [`online_retail_customer_spend.csv`](LAB_06) — net spend of 4,317 customers (UCI Online Retail, CC BY 4.0), with provenance; put it in a `data` folder.
- [`requirements.txt`](LAB_07) — the pinned NumPy and SciPy versions.
- [`captures.json`](LAB_08) — the author's full run, machine-readable.
- [`captures-quick.json`](LAB_09) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_10) — the author's full run as printed.
- [`notebook.ipynb`](LAB_11) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-bootstrap-confidence-intervals.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. B. Efron. "Bootstrap methods: another look at the jackknife." *The Annals of Statistics* 7(1): 1–26, 1979. https://doi.org/10.1214/aos/1176344552
2. B. Efron. "Better bootstrap confidence intervals." *Journal of the American Statistical Association* 82(397): 171–185, 1987. https://doi.org/10.1080/01621459.1987.10478410
3. B. Efron and R. J. Tibshirani. *An Introduction to the Bootstrap.* Chapman & Hall/CRC, 1993. https://doi.org/10.1201/9780429246593
4. R. Tibshirani and F. Leisch. `bootstrap`: functions for the book "An Introduction to the Bootstrap", R package version 2019.6 (datasets `law` and `law82`, function `bcanon`). https://cran.r-project.org/package=bootstrap (accessed 2026-11-01)
5. B. Efron and T. Hastie. *Computer Age Statistical Inference: Algorithms, Evidence, and Data Science*, chapters 10 and 11. Cambridge University Press, 2016. https://doi.org/10.1017/CBO9781316576533
6. T. J. DiCiccio and B. Efron. "Bootstrap confidence intervals." *Statistical Science* 11(3): 189–228, 1996. https://doi.org/10.1214/ss/1032280214
7. P. Hall. "Theoretical comparison of bootstrap confidence intervals." *The Annals of Statistics* 16(3): 927–953, 1988. https://doi.org/10.1214/aos/1176350933
8. T. C. Hesterberg. "What teachers should know about the bootstrap: resampling in the undergraduate statistics curriculum." *The American Statistician* 69(4): 371–386, 2015. https://doi.org/10.1080/00031305.2015.1089789
9. J. L. Horowitz. "Bootstrap methods in econometrics." *Annual Review of Economics* 11: 193–224, 2019. https://doi.org/10.1146/annurev-economics-080218-025651
10. P. J. Bickel and D. A. Freedman. "Some asymptotic theory for the bootstrap." *The Annals of Statistics* 9(6): 1196–1217, 1981. https://doi.org/10.1214/aos/1176345637
11. J. W. H. Swanepoel. "A note on proving that the (modified) bootstrap works." *Communications in Statistics — Theory and Methods* 15(11): 3193–3203, 1986. https://doi.org/10.1080/03610928608829303
12. P. J. Bickel, F. Götze and W. R. van Zwet. "Resampling fewer than n observations: gains, losses, and remedies for losses." *Statistica Sinica* 7(1): 1–31, 1997. MR1441142. https://www3.stat.sinica.edu.tw/statistica/oldpdf/A7n11.pdf
13. K. B. Athreya. "Bootstrap of the mean in the infinite variance case." *The Annals of Statistics* 15(2): 724–731, 1987. https://doi.org/10.1214/aos/1176350371
14. K. Knight. "On the bootstrap of the sample mean in the infinite variance case." *The Annals of Statistics* 17(3): 1168–1175, 1989. https://doi.org/10.1214/aos/1176347262
15. P. Hall. "Asymptotic properties of the bootstrap for heavy-tailed distributions." *The Annals of Probability* 18(3): 1342–1360, 1990. https://doi.org/10.1214/aop/1176990748
16. E. Giné and J. Zinn. "Necessary conditions for the bootstrap of the mean." *The Annals of Statistics* 17(2): 684–691, 1989. https://doi.org/10.1214/aos/1176347134
17. B. F. Logan, C. L. Mallows, S. O. Rice and L. A. Shepp. "Limit distributions of self-normalized sums." *The Annals of Probability* 1(5): 788–809, 1973. https://doi.org/10.1214/aop/1176996846
18. H. R. Künsch. "The jackknife and the bootstrap for general stationary observations." *The Annals of Statistics* 17(3): 1217–1241, 1989. https://doi.org/10.1214/aos/1176347265
19. D. N. Politis and J. P. Romano. "The stationary bootstrap." *Journal of the American Statistical Association* 89(428): 1303–1313, 1994. https://doi.org/10.1080/01621459.1994.10476870
20. D. W. K. Andrews. "Inconsistency of the bootstrap when a parameter is on the boundary of the parameter space." *Econometrica* 68(2): 399–405, 2000. https://doi.org/10.1111/1468-0262.00114
21. A. M. Polansky. "Upper bounds on the true coverage of bootstrap percentile type confidence intervals." *The American Statistician* 53(4): 362–369, 1999. https://doi.org/10.1080/00031305.1999.10474491
22. N. Schenker. "Qualms about bootstrap confidence intervals." *Journal of the American Statistical Association* 80(390): 360–361, 1985. https://doi.org/10.1080/01621459.1985.10478123
23. P. Hall. "On the number of bootstrap simulations required to construct a confidence interval." *The Annals of Statistics* 14(4): 1453–1462, 1986. https://doi.org/10.1214/aos/1176350169
24. A. C. Davison, D. V. Hinkley and G. A. Young. "Recent developments in bootstrap methodology." *Statistical Science* 18(2): 141–157, 2003. https://doi.org/10.1214/ss/1063994969
25. A. J. Canty, A. C. Davison, D. V. Hinkley and V. Ventura. "Bootstrap diagnostics and remedies." *Canadian Journal of Statistics* 34(1): 5–27, 2006. https://doi.org/10.1002/cjs.5550340103
26. R. A. Fisher. "Frequency distribution of the values of the correlation coefficient in samples from an indefinitely large population." *Biometrika* 10(4): 507–521, 1915. https://doi.org/10.1093/biomet/10.4.507
27. D. Chen. "Online Retail" [dataset]. UCI Machine Learning Repository, 2015. CC BY 4.0. https://doi.org/10.24432/C5BW33
28. SciPy 1.18.1 documentation, `scipy.stats.bootstrap`. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html (accessed 2026-11-01)
29. A. Canty and B. D. Ripley. `boot`: bootstrap functions, R package version 1.3.32 (`boot.ci`, `empinf`). https://cran.r-project.org/package=boot (accessed 2026-11-01)
