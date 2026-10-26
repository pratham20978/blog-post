---
title: "The Sampling Distribution: The CLT and Where n = 30 Fails"
slug: sampling-distribution-central-limit-theorem
date: 2026-10-26
updated: 2026-10-26
summary: "A mean's sampling distribution turns normal at a pace set by skewness, not n = 30: on real customer spend, a 5% t-test errs 39.8% of the time at n = 30."
tags: [data-science, statistics, central-limit-theorem, sampling-distribution, standard-error, t-test, monte-carlo-simulation]
category: data-science
series: statistics-for-data-scientists
series_position: 2
tier: L3
difficulty: intermediate
prerequisites: ["expectation and variance", "probability distributions", "Python with NumPy"]
reading_minutes: 30
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/sampling-distribution-central-limit-theorem"
---

![Means of 30 customers' spend in standard errors, piled left of the tangerine true-mean line, beside the dashed normal curve](COVER)

> [!NOTE]
> **Insights** — A statistic computed from a random sample is itself a random variable, and its distribution across samples, the sampling distribution, is what every standard error, test and interval describes. The central limit theorem says the sampling distribution of a mean becomes normal; it does not say when. The pace is set by the population's skewness, not by a sample size such as 30: drawing customers from 4,317 real online-retail accounts, whose spend has skewness 21.6, a nominal 5% t-test for a lower mean rejects the true mean 39.8% of the time at n = 30 and 17.7% at n = 1,000. When the variance is infinite, the normal limit never arrives.

**Level:** intermediate · **You need:** expectation and variance, probability distributions, Python with NumPy · **Time:** ~31 min

**Jump to:** [worked example](#worked-example) · [standard error](#standard-deviation-or-standard-error) · [Student's t](#why-does-students-t-replace-z) · [how fast](#how-fast-does-the-clt-work) · [Berry–Esseen](#what-does-berryesseen-guarantee) · [infinite variance](#when-does-the-clt-never-arrive) · [replications](#how-many-replications-does-a-simulation-need) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: one NumPy and SciPy script that runs in about three and a half minutes and is seeded, so every number repeats exactly. Each simulated rate is printed as an estimate ± its Monte Carlo standard error (MCSE), the standard deviation of the simulation's own estimate, with the number of replications R behind it. Published numbers are **quoted** from their sources.

## Why this matters

Suppose you track average revenue per customer and each month test a random sample of 1,000 customers against last year's mean with a one-sided t-test at 5%, to catch a fall. On the real spend data below, when nothing has changed, that test raises a false alarm 17.7% of the time, not 5% (measured). The mirror-image test, for a rise, fires 0.9% of the time when nothing has changed. Both failures have one cause: the test treats the mean's sampling distribution as normal, and for this population, at n = 1,000, it is not normal yet. The rule of thumb most of us were taught says it has been since n = 30.

## The problem

You want a population quantity, the **estimand**: here the mean spend μ of all customers. You compute it from a sample of n with a rule, the **estimator**: here the sample mean X̄. Before the sample is drawn X̄ is a random variable; once drawn, its value x̄ is the **estimate**. The distribution X̄ would have over all possible samples is its **sampling distribution**. Every standard error, p-value and confidence interval is a statement about that distribution: its spread, one of its tail areas, its quantiles.

The **standard error (SE)** is the standard deviation of the sampling distribution. For the mean of n independent draws it is σ/√n, where σ is the population's standard deviation. Keep the two apart: σ measures how much customers differ, the SE how much sample means differ. <!-- L04 -->

The **central limit theorem (CLT)**, met in the first part of this series, *Distributions as Generative Stories: Let the Process Pick*, as the story behind the normal, makes the promise most of statistics leans on: for independent draws with a finite variance, the standardised mean (X̄ − μ)/(σ/√n) tends to a standard normal as n grows. <!-- L03 --> That is a statement about a limit. It says nothing about how large n must be, and the rule usually taught in its place, use normal-based t methods once n ≥ 30 if the data are not too skewed, has been called imprecise and inadequate. <!-- L13 -->

Student put the question precisely in 1908: where is the line between a "large" sample and a "small" one? <!-- L06 --> Two things decide it. The first is shape: a skewed population passes some of its skew to X̄. The second is scale: σ is unknown, so the SE has to be estimated from the same sample. Student solved the second exactly, for normal data. This post measures the first.

Measuring needs an instrument, because for real data the sampling distribution has no formula. A **Monte Carlo simulation** builds it: draw a sample, compute the statistic, repeat. Each repetition is a **replication**, and R replications give R draws from the sampling distribution. The simulation's own error is computable too. For a simulated rate p, the **MCSE** is √(p(1 − p)/R), <!-- L24 --> and every simulated rate below carries one.

## Worked example

### The population

UCI's Online Retail dataset holds the invoice lines of a UK-based online retailer of mainly all-occasion gifts from 1 December 2010 to 9 December 2011; many of its customers are wholesalers. <!-- L01 --> It was introduced in a 2012 study of customer segmentation. <!-- L02 --> Adding every line per customer, cancellations included, gives net spend for 4,372 customers, and 4,317 have a positive total. Those 4,317 numbers are this post's population. Drawing customers with replacement makes every draw independent, as if from a customer base too large to exhaust, so the CLT's conditions hold exactly.

Figure 1 shows the shape behind every result that follows. The median customer spent £658.26 over the period, the mean is £1,925.71, and 79.1% of customers sit below the mean. The 43 biggest customers, the top 1%, account for 29.7% of all spend, and the largest, at £279,489.02, sits 33.6 standard deviations above the mean. The population SD is σ = £8,266.70, with divisor N, because these customers are the whole population.

![Customers' net spend on a log scale: median £658, mean £1,926 far to its right, and a bracket over the top 1% holding 29.7% of spend](FIG_01)
*Figure 1. On a log axis the bulk looks tame. The lopsidedness lives in the bracket: 43 customers, 29.7% of all spend.*

The **skewness** γ, the average cubed deviation from the mean divided by σ³, puts a number on that lopsidedness. It is 0 for any symmetric population and 2 for an exponential. For this spend it is 21.6.

### The sampling distribution, by simulation

The instrument is short. For each sample size n, draw n customers with replacement, record the sample mean x̄ and the sample SD s (divisor n − 1), and repeat R = 100,000 times. That R keeps the MCSE of any rate at or below 0.16 percentage points, the worst case being a rate of 50%, and near 0.07 points for rates around 5%. Each n draws from its own seeded stream of random numbers, so the whole run repeats exactly.

Figure 2 plots the 100,000 means for n = 10, 30, 100 and 1,000, each measured in true standard errors from μ, against the standard normal the CLT promises.

![Four histograms of simulated means in standard errors: a spike left of the true mean at n = 10 and 30, near-normal but skewed at n = 1,000](FIG_02)
*Figure 2. The same axis in every panel, so only the shape changes. The spike left of μ is the samples that hold no big customer.*

Three things hold at every n. The means centre on μ. Their spread is σ/√n: £2,614 at n = 10, £1,509 at 30, £827 at 100 and £261 at 1,000, and the simulated SD of the means matches each within its MCSE (1.002 ± 0.013 times σ/√n at n = 10, 0.998 ± 0.003 at n = 1,000). And the shape keeps the population's skew, divided by √n: 6.82 at n = 10, 3.94 at 30 and 0.68 at 1,000. <!-- L10 --> At n = 30, 71.8% of sample means fall below μ.

### Standard deviation or standard error?

σ = £8,267 describes one customer. The SE describes the mean of n customers: £1,509 at n = 30. Reporting one where the other belongs is a recurring error in published papers, and the SE's smallness tempts authors to use it to describe their data. <!-- L04 -->

In practice σ is unknown and the SE is estimated by s/√n. For this population the estimate is usually far too small (Figure 3). At n = 30 the median sample SD is 0.256 σ, so the typical estimated SE is £386 against a true £1,509, and s falls below σ in 88.1% of samples. That is not bias in s²: averaged over samples, s² is 0.986 ± 0.014 times σ². The rare samples that catch a big customer have an s many times σ, and they balance the rest.

![Log–log plot of σ, σ/√n and the simulated SD of means, with the band of s/√n far below σ/√n for small n](FIG_03)
*Figure 3. The simulated SD of the means sits on σ/√n. The estimate s/√n, which every t-test divides by, usually sits far below it until n reaches the thousands.*

### The t-test's two tails

Now test the true mean. The one-sided **t-test** at 5% rejects μ = £1,925.71 in favour of a lower mean when t = (x̄ − μ)/(s/√n) falls at or below −t₀.₉₅, where t₀.₉₅ is the 95th percentile of Student's t distribution with n − 1 degrees of freedom, the reference the t-test assumes and the subject of a section below: 1.699 at n = 30. The mirror test rejects in favour of a higher mean when t ≥ t₀.₉₅. Each is built to reject a true null 5% of the time, its nominal **type I error rate**.

Figure 4 measures both. At n = 30 the lower test rejects 39.82% ± 0.15 of the time and the upper 0.05% ± 0.01. At n = 1,000 they reject 17.69% ± 0.12 and 0.94% ± 0.03; at n = 10,000, 7.86% ± 0.09 and 2.99% ± 0.05. The two-sided test at 5% sits between them, 34.41% at n = 30 and 6.06% at n = 10,000, because its two tails' errors partly cancel.

![Rejection rates of a 5% t-test against n: the lower tail falls from 41.6% to 7.9%, the upper rises from 0.03% to 3.0%](FIG_04)
*Figure 4. One tail fires far too often and the other almost never. Both approach 5% as n grows, slowly and from opposite sides.*

## Intuition

Why does skew push one tail up and the other down? Count the big customers. A sample of 30 holds at least one of the 43 biggest with probability 1 − (1 − 43/4,317)³⁰ = 25.9%, and the simulation agrees: 25.9% ± 0.1. In the other three samples in four, every customer is ordinary. The mean of those samples falls below μ 92.4% of the time, and their s is small, because s is computed from the same ordinary values. A low mean divided by a small SE makes t very negative, so the lower test rejects 53.7% ± 0.2 of those samples. A sample that does catch a big customer has a higher mean and an enormous s, so its t stays small: none of the 25,855 such samples was rejected.

![Scatter of 3,000 samples' mean against SD on log axes: rejected samples cluster at low mean and low SD below a boundary curve](FIG_05)
*Figure 5. The rejected samples (tangerine) are the ones whose mean and SD fell together, below the curve where t = −1.70.*

The mean and the SD rise and fall together: across samples their correlation is 0.972 (Figure 5). That coupling, more than the skew of x̄ alone, is what wrecks the t-test. The t statistic is about twice as skewed as the mean and in the opposite direction, −2γ/√n against γ/√n. <!-- L11 --> For a normal population the sample mean and SD are independent, the property Student's derivation rests on. <!-- L32 -->

An analogy: estimate a lake's average depth from 30 soundings when one trench holds much of the water. Most sets of soundings miss the trench, read shallow, and agree with one another, so they look precise and are wrong. The analogy breaks at the remedy: a surveyor can map the trench and sound it on purpose, while a random sample of customers has no map.

## Why does Student's t replace z?

The first correction is for scale. With σ known, z = (x̄ − μ)/(σ/√n) is exactly standard normal for normal data at every n. With σ replaced by s the statistic inherits the randomness of s: a sample whose s happens to be small yields a large ratio. For normal data at n = 10, comparing that ratio with the normal's 1.96 rejects a true null 8.16% of the time, exactly, and the lab measures 8.14% ± 0.03 over a million samples.

Student derived the right reference in 1908. He assumed a normal population and judged that only an extreme departure from normality would cause serious error. <!-- L05 --> His statistic, which he called z, divides the distance between the sample and population means by the sample SD computed with divisor n. <!-- L06 --> Today's t is the same quantity rescaled, t = z√(n − 1). Its distribution, **Student's t** with n − 1 **degrees of freedom**, has heavier tails than the normal: its two-sided 5% cutoff at n = 10 is 2.262, not 1.960 (Figure 6).

![A dot strip of 10 sleep differences with mean 1.58, and t with 9 degrees of freedom against the normal, tails beyond ±1.96 shaded](FIG_06)
*Figure 6. Left: Student's data. Right: t₉ has more mass beyond ±1.96 than the normal does, 8.16% of it, which is what using 1.96 with an estimated σ costs.*

His illustration survives as a dataset R still ships. Ten patients took two sleep-inducing drugs, and Student tabulated the extra hours of sleep each gained, taking the figures from a table by Cushny and Peebles. The differences, drug 2 minus drug 1, are 1.2, 2.4, 1.3, 1.3, 0, 1.0, 1.8, 0.8, 4.6 and 1.4 hours: mean 1.58, s.d. 1.17 with divisor n. That puts the mean 1.35 s.d. above zero, and Student's table gave a probability of 0.9985 that drug 2 is better, odds of about 666 to 1. <!-- L07 --> The same ten numbers are R's `sleep` dataset. <!-- L08 --> Today, with divisor n − 1, s = 1.230 and t = 1.58/(1.230/√10) = 4.062 = 1.354 × 3; the one-sided P(T₉ ≥ 4.062) is 0.00142, odds of 705 to 1, and R's `t.test` gives a two-sided p of 0.00283. The trial behind the table was run at Kalamazoo, and Student, and Fisher after him, misquoted parts of it. <!-- L09 -->

A normal reference with the estimated s would have reported p = 0.0000486, 58 times smaller: at n = 10, ignoring the randomness of s overstates the evidence by more than an order of magnitude. What t does not fix is shape. It is exact only for normal data, so on the spend at n = 30 it still rejects 39.8% in the lower tail, and on an exponential population at n = 10 it rejects 13.17%. Student's t corrects for estimating σ, not for skew.

## How fast does the CLT work?

The size of the tail error is predictable. An **Edgeworth expansion** corrects the normal approximation in powers of 1/√n, and its first term for the t statistic is P(T ≤ x) ≈ Φ(x) + γ(2x² + 1)φ(x)/(6√n), with Φ and φ the standard normal CDF and density. <!-- L11 --> At the one-sided 5% point that makes the lower tail about 5% + 0.110 γ/√n and the upper about 5% − 0.110 γ/√n. The error depends on n only through γ/√n.

Figure 7 tests that on eight populations. Part 1 supplies six: the normal and the unit-variance t₅ (skewness 0), Clarke's Poisson (1.04), the exponential (2), Greenwood and Yule's negative binomial (2.37) and the product of 12 effects (4.25). The standard lognormal (6.18), whose simulation by Wilcox and Rousselet appears below, and the spend (21.6) complete the set.

![Lower-tail excess over 5% against skewness over √n for seven populations and the spend, against a dashed first-order line](FIG_07)
*Figure 7. Plotted against γ/√n, populations as different as a Poisson and a lognormal fall close to one line. The spend, with excess kurtosis 600, runs above it.*

| Population | Skewness γ | Lower tail, n = 30 | Upper tail, n = 30 | n for each one-sided test within 10% of 5% |
|---|---|---|---|---|
| normal | 0 | 4.93% | 4.98% | any |
| unit-variance t₅ | 0 | 4.95% | 4.95% | any |
| Poisson, Clarke's rate 0.932 | 1.04 | 7.11% | 3.20% | 521 |
| exponential | 2 | 9.84% | 2.26% | 1,943 |
| negative binomial, Greenwood and Yule | 2.37 | 10.34% | 2.04% | 2,737 |
| product of 12 effects | 4.25 | 14.41% | 1.17% | 8,787 |
| standard lognormal | 6.18 | 15.44% | 0.98% | 18,582 |
| customer spend | 21.58 | 39.82% | 0.05% | 226,264 |

Every rate in the table carries an MCSE of 0.15 points or less. The last column inverts the first-order rule: keeping each one-sided test between 4.5% and 5.5% needs 0.110 γ/√n ≤ 0.005, which is n ≥ 486γ². For n = 30 to pass that bar, γ must be below 0.25. From n = 30 the five skewed populations sit within 20% of the rule, but the spend's errors run 20% to 69% above it, so its 226,264 is a floor.

Others have reached the same verdict. In the long preprint of his 2015 article in *The American Statistician*, Hesterberg applies the same expansion to both tails of a two-sided 5% t-test and finds that an exponential population needs n > 4,578 to keep each tail within 10% of 2.5%, closer to 5,000 by simulation; his summary is that n ≥ 30 is not enough. <!-- L12 --> <!-- L13 --> Fukuda sampled the real distributions of 38 variables from Japanese firms and rejected the normality of the sample mean for 31 of them even at n = 500. <!-- L29 -->

An older skewness rule, from survey sampling, asks much less. **Cochran's rule**, n > 25γ², promises that a two-sided 95% interval for a mean covers the true mean at least 94% of the time, while allowing its misses to fall unequally on the two sides. <!-- L14 --> For the spend it asks for n > 11,644, and the lab agrees: at n = 10,000 the two-sided test rejects 6.06% ± 0.08, a coverage of 93.9%. The rule is right about what it promises. It promises only the two-sided total, which hides the asymmetry: in the expansion the 1/√n term is even in x, so it adds to one tail what it takes from the other. That is why a two-sided test on mildly skewed data can look fine at n = 30 while a one-sided question, such as whether revenue fell, is answered at a different error rate from the one designed.

## What does Berry–Esseen guarantee?

The rule above is an approximation. The **Berry–Esseen inequality** is a guarantee. Measure the gap between two distributions by the **Kolmogorov distance**, the largest vertical gap between their CDFs. For independent draws with a finite third absolute moment, the distance between the standardised mean's CDF and Φ is at most C₀β₃/√n for every n, where β₃ = E|X − μ|³/σ³. <!-- L17 --> Berry and Esseen proved it independently in 1941 and 1942. The best constant proven is Shevtsova's C₀ ≤ 0.469 of 2013, which improved her 0.4748 of 2011, and no constant below 0.4097 can work. <!-- L18 --> <!-- L19 -->

For the spend, β₃ = 21.59, so the bound is 10.1/√n, and it guarantees a distance of 0.01 only from n = 1,025,322. The actual distance can be computed exactly. The **characteristic function** of a random variable, E e^(itX), determines its distribution, <!-- L34 --> and for a mean of draws from a finite population it is a finite sum that can be inverted numerically. Checked against the exponential, whose sample sum has an exact gamma distribution, <!-- L35 --> the inversion agrees to 1.3 × 10⁻¹¹. For the spend it gives 0.2215 at n = 30, 0.0468 at n = 1,000 and 0.0144 at n = 10,000, and the distance falls to 0.01 at n = 20,652, 50 times sooner than the guarantee (Figure 8). The exponential tells the same story: 177 against 12,824.

![Log–log plot of Kolmogorov distance against n: Berry–Esseen bounds far above the exact distances for the spend and the exponential](FIG_08)
*Figure 8. Filled dots: where the exact distance reaches 0.01. Hollow dots: where Berry–Esseen guarantees it, 50 to 72 times later.*

The bound is loose because it must hold for every population with the same β₃, including the worst one. Even the smallest constant that could ever work, 0.4097, would push the guarantee to 782,555. It also bounds the standardised mean with σ known, not the t statistic. Use it for what it says, that the error shrinks like 1/√n with a constant set by β₃; use simulation or exact computation to know when the approximation is good enough.

## When does the CLT never arrive?

The CLT needs a finite variance. Drop that and the normal limit can fail in two ways.

The **Cauchy distribution**, the distribution of the ratio of two independent standard normals, <!-- L33 --> has no mean at all. The average of n Cauchy draws has exactly the same distribution as a single draw, for every n, so averaging gains nothing. <!-- L22 --> The lab measures the interquartile range of the mean of n draws as 2.00, 2.00, 2.03 and 2.00 for n = 1, 10, 100 and 1,000, against 2 for one draw. Running means never settle (Figure 9, left): one of three seeded runs ends at −1,317 after a million draws, dragged there by an enormous value late in the run.

A **Pareto distribution** with **tail index** a has P(X > x) = x^(−a) for x ≥ 1, and its moments of order p are finite only for p below a. <!-- L21 --> With a = 1.5 the mean is 3 and the variance is infinite. (NumPy's `Generator.pareto` draws the shifted version, the Lomax, so the lab adds 1 to each draw.) <!-- L28 --> The law of large numbers still holds and running means do approach 3, slowly and in jumps (Figure 9, middle). The **generalized CLT** says what replaces the normal: the only possible limits of normalised sums are **stable laws**, and with a between 1 and 2 the sum is normalised by n^(1/a) instead of √n. <!-- L20 --> So the spread of the mean shrinks like n^(−1/3), not n^(−1/2): the lab measures its interquartile range shrinking by a factor of 0.485 per tenfold n at the largest sizes, against 0.464 for the stable limit and 0.316 for a finite variance.

![Three panels: Cauchy running means that never settle, Pareto running means creeping to 3, and a Pareto t-test error stuck near 26%](FIG_09)
*Figure 9. Left and middle: three seeded runs each. Right: the spend and the exponential creep toward 5%; the Pareto stops near 26%.*

The t-test never recovers. The t statistic tends to a standard normal if and only if the population lies in the normal law's **domain of attraction**, the set of distributions whose normalised sums tend to it. <!-- L23 --> A Pareto with tail index 1.5 does not, and its lower-tail rejection rate falls from 42.6% at n = 10 to 26.4% at n = 10,000 and then stops: 26.4% ± 1.0 at n = 100,000 (Figure 9, right). If a tail that heavy is plausible for your data, and Part 1's log–log trap shows how hard that is to rule out, the population variance may be infinite, and then s/√n estimates nothing finite.

## How many replications does a simulation need?

Every rate above is an estimate from R replications, with MCSE √(p(1 − p)/R). Turn that around to choose R from a target: R = p(1 − p)/MCSE². <!-- L24 --> Measuring a rate near 5% to ±0.1 points takes R = 47,500; measuring any rate to ±0.1 points, the worst case being p = 50%, takes 250,000. This post uses R = 100,000 per setting: ±0.07 points near 5% and ±0.16 at worst.

Seeds make a simulation repeatable. A **seed** fixes the start of the pseudo-random sequence; set it once, at the start, and give each separate experiment its own **stream** of random numbers rather than reseeding. <!-- L25 --> NumPy builds streams from a list of integers, with the varying identifier first and the root seed last, and warns that arithmetic such as root seed + worker id lets streams overlap. <!-- L27 --> The lab seeds every (stage, setting) pair this way, so any stage reruns alone and repeats to the bit.

The MCSE is what tells a reader which differences are real. Wilcox and Rousselet ran a one-sample t-test at the 0.05 level on lognormal data in two versions of their guide to robust methods. The 2017 version reports an actual type I error rate of about 0.111 at n = 30, from 5,000 replications; the 2023 update reports about 0.116 for the same simulation. <!-- L15 --> <!-- L16 --> Is the change a correction, or noise? The lab's two-sided test on the standard lognormal gives 0.1170 ± 0.0002 (R = 2,000,000). At R = 5,000 the MCSE is 0.0045, so 0.111 sits 1.3 MCSEs from it, and 500 reruns at R = 5,000 spread from 0.102 to 0.136 (Figure 10). Neither version printed an MCSE, and they are in large company: of 100 simulation studies reviewed in *Statistics in Medicine*, 93 did not mention Monte Carlo SEs, and of the 87 that stated their number of replications, 4 justified it. <!-- L26 -->

![Histograms of 500 reruns at R = 5,000 and 125 at R = 20,000 of a lognormal t-test rate, with published 0.111 and 0.116 inside each spread](FIG_10)
*Figure 10. Each published value sits inside the spread of reruns at its own R. Printing the MCSE beside them would have shown the change was within simulation noise.*

## The math

| Symbol | Meaning | Units |
|---|---|---|
| $N$, $n$ | population size (4,317) and sample size | count |
| $\mu$, $\sigma$ | population mean and standard deviation (divisor $N$) | £ |
| $\bar X$, $s$ | sample mean and sample standard deviation (divisor $n - 1$) | £ |
| $\gamma$, $\beta_3$ | skewness $\operatorname{E}(X - \mu)^3/\sigma^3$ and absolute third moment $\operatorname{E}\lvert X - \mu\rvert^3/\sigma^3$ | — |
| $\Phi$, $\varphi$ | standard normal CDF and density | — |
| $R$, $p$ | replications and a simulated rate | count, proportion |

**The standard error.** For independent draws, variances add:

$$
\operatorname{E}\bar X = \mu, \qquad \operatorname{SD}(\bar X) = \sqrt{\frac{n\sigma^2}{n^2}} = \frac{\sigma}{\sqrt n} \tag{1}
$$

The spread of the mean falls with the square root of n, so quadrupling n halves the SE. For the spend at n = 30 it is 8,266.70/√30 = £1,509.29, the line in Figure 3.

**The skewness of the mean.** Third central moments of independent draws add too:

$$
\operatorname{skew}(\bar X) = \frac{n\,\gamma\sigma^3}{(n\sigma^2)^{3/2}} = \frac{\gamma}{\sqrt n} \tag{2}
$$

Skew fades only with √n: at n = 30 the spend's mean still has skewness 21.58/√30 = 3.94, Figure 2's second panel.

**The CLT.** If σ is finite, for every x

$$
\lim_{n \to \infty} P\!\left(\frac{\bar X - \mu}{\sigma/\sqrt n} \le x\right) = \Phi(x) \tag{3}
$$

It is a limit and carries no rate; equations (4) and (5) supply one. <!-- L03 -->

**The t statistic's first correction.** With $T = (\bar X - \mu)/(s/\sqrt n)$:

$$
P(T \le x) = \Phi(x) + \frac{\gamma}{6\sqrt n}\,(2x^2 + 1)\,\varphi(x) + O(1/n) \tag{4}
$$

The correction term is positive for every x when γ > 0, so it lifts the whole CDF: more mass in the lower tail and less in the upper, by the same amount at x and −x. <!-- L11 --> At x = −1.645 the lower tail is about $0.05 + c\gamma/\sqrt n$ with $c = (2 \cdot 1.645^2 + 1)\varphi(1.645)/6 = 0.1102$, so keeping it within ε of 5% needs $n \ge (c\gamma/\varepsilon)^2$, which is 486γ² for ε = 0.005. For the spend at n = 10,000 the rule predicts 5% + 11.02 × 0.216 = 7.38% against the measured 7.86%.

**Berry–Esseen.** For every n, with the best constant proven:

$$
\sup_x \left\lvert P\!\left(\frac{\bar X - \mu}{\sigma/\sqrt n} \le x\right) - \Phi(x)\right\rvert \le \frac{C_0\,\beta_3}{\sqrt n}, \qquad C_0 \le 0.469 \tag{5}
$$

Setting the right side to 0.01 and solving for n gives the guaranteed sample size, (0.469 β₃/0.01)² rounded up: 1,025,322 for the spend, whose β₃ is 21.5902. <!-- L17 --> <!-- L18 -->

<details>
<summary>Computing the exact distance</summary>

The characteristic function of the standardised mean is $\phi_n(t) = \psi(t/\sqrt n)^n$, where $\psi(u) = \frac{1}{N}\sum_{j} e^{iu(x_j - \mu)/\sigma}$ is a finite sum over the 4,317 customers. The Gil-Pelaez formula turns it back into the CDF:

$$
F_n(x) = \frac{1}{2} - \frac{1}{\pi}\int_0^\infty \frac{\operatorname{Im}\!\left[e^{-itx}\,\phi_n(t)\right]}{t}\,dt
$$

The lab evaluates the integral by the midpoint rule with step 0.004, doubling the upper limit until $\lvert\phi_n\rvert \lt 10^{-7}$, then takes the largest gap to Φ over a grid refined around its maximum. On the exponential, where $F_n$ is a gamma CDF, the two agree to $1.3 \times 10^{-11}$.

</details>

**The Cauchy mean.** A standard Cauchy has characteristic function $e^{-\lvert t\rvert}$, so the mean of n independent draws has

$$
\operatorname{E} e^{it\bar X} = \left(e^{-\lvert t\rvert/n}\right)^n = e^{-\lvert t\rvert} \tag{6}
$$

the characteristic function of a single draw: the mean of a million Cauchy draws is exactly as spread out as one. <!-- L22 -->

**Monte Carlo error.** For a rate estimated from R independent replications:

$$
\operatorname{MCSE}(\hat p) = \sqrt{\frac{p(1 - p)}{R}}, \qquad R = \frac{p(1 - p)}{\operatorname{MCSE}^2} \tag{7}
$$

At p = 0.398 and R = 100,000 the MCSE is 0.0015, the ± 0.15 points on the n = 30 lower tail. <!-- L24 -->

## Implementation

The heart of the lab fits in a screen: draw R samples with replacement, compute t for each, count both tails, and attach the MCSE.

```python
import numpy as np
from scipy import stats


def tail_errors(pop, n, R, rng):
    """One-sided 5% t-tests of the true mean on R samples of size n: rejection rates and MCSEs."""
    mu = pop.mean()
    x = pop[rng.integers(0, len(pop), size=(R, n))]       # R samples, drawn with replacement
    t = (x.mean(1) - mu) / (x.std(1, ddof=1) / np.sqrt(n))
    c = stats.t.ppf(0.95, n - 1)                           # the one-sided 5% cutoff, 1.699 at n = 30
    out = {}
    for side, hit in (("lower", t <= -c), ("upper", t >= c)):
        p = float(hit.mean())
        out[side] = (round(p, 5), round((p * (1 - p) / R) ** 0.5, 5))   # estimate, MCSE
    return out


spend = np.loadtxt("data/online_retail_customer_spend.csv", delimiter=",", skiprows=10, usecols=1)
rng = np.random.default_rng(np.random.SeedSequence([1, 1, 20261026]))   # the lab's stream for n = 30
print(len(spend), round(spend.mean(), 2), round(spend.std(), 2))         # 4317 1925.71 8266.7
print(tail_errors(spend, 30, 100_000, rng))   # {'lower': (0.39816, 0.00155), 'upper': (0.00047, 7e-05)}
```

Indexing the population with random integers draws with replacement, which is what makes the draws independent; `x.std(1, ddof=1)` is s with divisor n − 1, the one the t distribution assumes. Seeding with the same stream as the lab reproduces its n = 30 numbers to every digit. The full lab adds the other populations, Student's data, the exact Berry–Esseen distances, the infinite-variance cases and the replication study; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** trusting a normal-based test or interval because n ≥ 30. The error of a one-sided t-test scales with γ/√n. On customer spend with skewness 21.6, a 5% test of the true mean rejects 39.8% of the time at n = 30 and 17.7% at n = 1,000; even an exponential population needs about 2,000 observations, by the first-order rule, to keep each one-sided test within half a point of 5%. Estimate the skewness of the quantity you average, and simulate your own test on data like yours before trusting its error rate.

- **Reading a two-sided error rate as safe.** The first-order skew terms cancel between the two tails, so a two-sided rate close to 5% can come from tails of, say, 4% and 1% instead of 2.5% each. Directional decisions, such as alerting on a drop, inherit the one-sided error.
- **Reporting the SE as the SD, or the reverse.** The SE describes the precision of a mean; the SD describes the data. The SE is smaller by √n, which is exactly why it gets misused to describe a sample. <!-- L04 -->
- **Trusting s/√n because s² is unbiased.** At n = 30 on the spend, s is below σ in 88.1% of samples although s² averages σ². The typical SE estimate is a quarter of the truth.
- **Choosing n from a sample's skewness.** For the same reason that s usually falls short of σ, a sample's skewness usually falls short of γ: the samples that reveal a heavy tail are the rare ones that hit it.
- **Sampling a fixed table without replacement and using σ/√n.** The N draws of a whole population sum to a constant, so any two draws without replacement have covariance −σ²/(N − 1), and the SE of the mean shrinks by √((N − n)/(N − 1)): 12% at n = 1,000 of 4,317. The lab's fault exercise shows the symptom.
- **Capping or transforming to make the test behave.** Capping spend at its 99th percentile cuts the skewness to 4.0, but the capped mean, £1,528.79, is a different estimand from £1,925.71. Decide what you want to estimate first.
- **Fixes, and where they are covered.** Johnson's skewness-corrected statistic adds γ̂(2t² + 1)/(6√n) to t, <!-- L30 --> and further modified t tests exist for skewed populations; <!-- L31 --> resampling methods are the subject of a later part of this series. Dependent observations, such as one customer's daily spend, need time-series methods, which this series does not cover.

## Key takeaways

- A statistic is a random variable; its sampling distribution, with spread SE = σ/√n for a mean, is what tests and intervals describe, and the SD of the data is a different quantity.
- The CLT is a limit with no rate. The one-sided error of a t-test is about 0.110 γ/√n, so the sample size a skewed population needs grows like γ², and no single n, 30 or any other, is safe.
- On real customer spend (skewness 21.6), a 5% t-test for a lower mean rejects the true mean 39.8% of the time at n = 30 and 7.9% at n = 10,000, because sample means and SDs fall together.
- Berry–Esseen guarantees normality far later than it arrives: a distance of 0.01 at n = 1,025,322 for the spend, against 20,652 exactly.
- With infinite variance the normal never arrives: a Cauchy mean is as spread out as one draw, and a Pareto t-test with tail index 1.5 stays near 26% in the lower tail.

## Try it yourself

**E1, reproduce.** The population SD is σ = £8,266.70. Compute the standard error of the mean of 30 customers and of 1,000, and check them against Figure 2's panel titles.

<details><summary>Answer</summary>

8,266.70/√30 = £1,509.29 and 8,266.70/√1,000 = £261.42. The lab's simulated SDs of the means are £1,498.26 and £260.88, ratios of 0.993 ± 0.007 and 0.998 ± 0.003, so both match within their MCSE.

</details>

**E3, predict.** An exponential population's lower-tail rejection rate is 9.84% at n = 30. Using the first-order rule, predict it at n = 300 before looking at the answer.

<details><summary>Answer</summary>

The excess over 5% scales like 1/√n, so it shrinks by √10: 4.84/3.16 = 1.53 points, a prediction of 6.53%. The lab measures 6.36% ± 0.08 at n = 300. The prediction is close because γ/√n = 0.115 there, small enough for the first-order term to dominate.

</details>

The lab carries the full ladder, from reproducing these tables to diagnosing a sampling fault that shrinks the standard error, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E4 exercises with answers, and cleanup.
- [`sampling.py`](LAB_02) — the seven stages: population, sampling, skewness, student, berry, heavy and replications.
- [`derive_spend.py`](LAB_03) — rebuilds the spend file from UCI's archive, checked by SHA-256; standard library only.
- [`requirements.txt`](LAB_04) — the pinned NumPy and SciPy versions.
- [`online_retail_customer_spend.csv`](LAB_05) — net spend of the 4,317 customers, with its source, licence and derivation; put it in a `data` folder.
- [`student1908_sleep.csv`](LAB_06) — Student's ten patients, as printed in 1908; put it in a `data` folder.
- [`captures.json`](LAB_07) — the author's full run, machine-readable, with the R cross-check.
- [`captures-quick.json`](LAB_08) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_09) — the author's full run as printed.
- [`notebook.ipynb`](LAB_10) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-sampling-distribution-central-limit-theorem.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. Student. "The probable error of a mean." *Biometrika* 6(1): 1–25, 1908. https://doi.org/10.1093/biomet/6.1.1 (transcription: https://www.york.ac.uk/depts/maths/histstat/student.pdf)
2. A. R. Cushny and A. R. Peebles. "The action of optical isomers: II. Hyoscines." *Journal of Physiology* 32(5–6): 501–510, 1905. https://doi.org/10.1113/jphysiol.1905.sp001097
3. S. Senn and W. Richardson. "The first t-test." *Statistics in Medicine* 13(8): 785–803, 1994. https://doi.org/10.1002/sim.4780130802
4. R Core Team. `sleep`, R package datasets, R 4.5.2. https://stat.ethz.ch/R-manual/R-patched/library/datasets/html/sleep.html (accessed 2026-10-26)
5. D. Chen. "Online Retail" [dataset]. UCI Machine Learning Repository, 2015. CC BY 4.0. https://doi.org/10.24432/C5BW33 (accessed 2026-10-26)
6. D. Chen, S. L. Sain and K. Guo. "Data mining for the online retail industry: a case study of RFM model-based customer segmentation using data mining." *Journal of Database Marketing and Customer Strategy Management* 19(3): 197–208, 2012. https://doi.org/10.1057/dbm.2012.17
7. C. M. Grinstead and J. L. Snell. *Introduction to Probability*, 2nd ed., American Mathematical Society, 1997, Chapters 8–10. https://math.dartmouth.edu/~prob/prob/prob.pdf
8. D. K. Lee, J. In and S. Lee. "Standard deviation and standard error of the mean." *Korean Journal of Anesthesiology* 68(3): 220–223, 2015. https://doi.org/10.4097/kjae.2015.68.3.220
9. T. Hesterberg. "What teachers should know about the bootstrap: resampling in the undergraduate statistics curriculum." Long preprint version, arXiv:1411.5279, 2014; published in *The American Statistician* 69(4): 371–386, 2015. https://arxiv.org/abs/1411.5279
10. P. S. Kott and B. Levine. "Exploring a skewness conjecture: expanding Cochran's rule to a proportion estimated from a complex sample." *Survey Methodology* 50(2): 543–551, 2024. https://www150.statcan.gc.ca/n1/pub/12-001-x/2024002/article/00001-eng.htm
11. R. A. Sugden, T. M. F. Smith and R. P. Jones. "Cochran's rule for simple random sampling." *Journal of the Royal Statistical Society Series B* 62(4): 787–793, 2000. https://doi.org/10.1111/1467-9868.00264
12. K. Fukuda. "An empirical study on sample size for the central limit theorem using Japanese firm data." *Teaching Statistics* 46(3): 184–191, 2024. https://doi.org/10.1111/test.12378
13. A. C. Berry. "The accuracy of the Gaussian approximation to the sum of independent variates." *Transactions of the American Mathematical Society* 49(1): 122–136, 1941. https://doi.org/10.1090/S0002-9947-1941-0003498-3
14. I. Shevtsova. "On the absolute constants in the Berry–Esseen type inequalities for identically distributed summands." arXiv preprint arXiv:1111.6554, 2011. https://arxiv.org/abs/1111.6554
15. A. Zolotukhin, S. Nagaev and V. Chebotarev. "On a bound of the absolute constant in the Berry–Esseen inequality for i.i.d. Bernoulli random variables." *Modern Stochastics: Theory and Applications* 5(3): 385–410, 2018. https://doi.org/10.15559/18-VMSTA113
16. J. P. Nolan. *Univariate Stable Distributions: Models for Heavy Tailed Data*. Springer, 2020, §1.5 and §1.8. https://doi.org/10.1007/978-3-030-52915-4
17. E. Giné, F. Götze and D. M. Mason. "When is the Student t-statistic asymptotically standard normal?" *The Annals of Probability* 25(3): 1514–1531, 1997. https://doi.org/10.1214/aop/1024404523
18. L. Chen. "Testing the mean of skewed distributions." *Journal of the American Statistical Association* 90(430): 767–772, 1995. https://doi.org/10.1080/01621459.1995.10476571
19. T. P. Morris, I. R. White and M. J. Crowther. "Using simulation studies to evaluate statistical methods." *Statistics in Medicine* 38(11): 2074–2102, 2019. https://doi.org/10.1002/sim.8086
20. R. R. Wilcox and G. A. Rousselet. "A guide to robust statistical methods in neuroscience." bioRxiv preprint 151811, 2017; published in *Current Protocols in Neuroscience* 82(1), 2018. https://doi.org/10.1101/151811
21. R. R. Wilcox and G. A. Rousselet. "An updated guide to robust statistical methods in neuroscience." PsyArXiv preprint, 2023; published in *Current Protocols* 3(3): e719, 2023. https://doi.org/10.31234/osf.io/kcjfe
22. NumPy 2.5 documentation, "Parallel random number generation." https://numpy.org/doc/stable/reference/random/parallel.html (accessed 2026-10-26)
23. NumPy 2.5 documentation, `numpy.random.Generator.pareto`. https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.pareto.html (accessed 2026-10-26)
