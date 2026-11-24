---
title: "Permutation and Rank Tests: What They Actually Test"
slug: permutation-and-rank-tests
date: 2026-11-23
updated: 2026-11-23
summary: "Darwin's 15 pairs: all 32,768 sign flips give an exact p of 0.0527. Mann–Whitney tests P(X > Y), not medians: at equal medians it rejected 80% at n = 400."
tags: [data-science, statistics, permutation-test, mann-whitney-test, wilcoxon-test, nonparametric-statistics, hypothesis-testing]
category: data-science
series: statistics-for-data-scientists
series_position: 10
tier: L3
difficulty: advanced
prerequisites: ["two-sample tests and their error rates", "p-values and type I error", "Python with NumPy and SciPy"]
reading_minutes: 33
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/permutation-and-rank-tests"
---

![Totals of all 32,768 sign assignments of Darwin's 15 differences, the tails beyond the observed 314 eighths in orange; p = 0.0527](COVER)

> [!NOTE]
> **Insights** — A permutation test is exact when its relabellings leave the data's distribution unchanged under the null hypothesis, and only then. Enumerating all 32,768 sign assignments of Darwin's 15 pairs of maize plants, as Fisher did by hand in 1935, gives p = 0.0527 with no normal model, beside the t-test's 0.0497. That exactness covers "the labels do not matter", not "the means are equal": with groups of 10 and 40 and the small group twice as spread, a permutation test of the mean difference rejected a true null 18.3% of the time, and studentising the statistic brought that to 5.7%. Mann–Whitney's test responds to P(X > Y), not to medians: with equal medians and different shapes it rejected 79.7% of samples of 400 per group.

**Level:** advanced · **You need:** two-sample tests and their error rates; p-values and type I error; Python with NumPy and SciPy · **Time:** ~33 min

**Jump to:** [worked example](#worked-example) · [exactness](#when-is-a-permutation-test-exact) · [means](#does-a-permutation-test-compare-means) · [Mann–Whitney](#what-does-the-mannwhitney-test-test) · [Hodges–Lehmann](#how-large-is-the-effect-the-hodgeslehmann-estimate) · [efficiency](#what-do-ranks-cost) · [correlation](#rank-correlations-spearman-and-kendall) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **computed** or **measured** come from its lab: one NumPy and SciPy script, seeded so every number repeats exactly. Darwin's randomisation, signed-rank and sign tests are computed exactly by enumerating all 32,768 sign assignments, Spearman's p-value by counting all 15! orderings, and efficiencies by numerical integration; error rates and power are simulated and printed as an estimate ± its Monte Carlo standard error (MCSE). Published numbers are **quoted**, and library conventions are read from SciPy's and R's source code.

## Why this matters

Nonparametric tests are sold as the option that assumes nothing. When a histogram looks skewed, swap the t-test for Mann–Whitney; when the distribution is in doubt, permute the labels. Both moves change the question the p-value answers. A permutation test is exact for one hypothesis, that the labels could be exchanged without changing the distribution of the data, and Mann–Whitney's p-value responds to whether one group tends to produce larger values, not to whether the medians differ. The cost shows up as a "significant change in median session time" that is really a change in shape, or as a permutation test of means that rejects a true null three times as often as promised because the smaller arm of an experiment is the noisier one.

## The problem

A test promises an error rate: when its null hypothesis is true, a 5% test rejects in 5% of repetitions. The eighth part of this series, *Which Statistical Test? The Design Decides, Not the Data*, measured how far Student's and Welch's t-tests keep that promise when their conditions fail. A **permutation test** keeps it without any model of the data's distribution. It takes a set of transformations of the data, such as swapping the labels of two groups or flipping the sign of a paired difference, computes the statistic on every transformed copy, and reports the share of copies at least as extreme as the observed statistic. That set of copies is the test's **reference set**. When the transformations are a physically performed random assignment, the test is called a **randomisation test**; the arithmetic is the same. <!-- L11 -->

The condition that makes it exact is **exchangeability**: under the null hypothesis, the transformations leave the joint distribution of the data unchanged, so the observed data are just one equally likely member of the reference set. A **rank test** applies the same idea to the ranks of the data instead of their values, so its reference distribution can be tabulated once for every data set of a given size. Wilcoxon's signed-rank and rank-sum tests and Mann and Whitney's U are the standard examples. <!-- L20 -->

This part asks three questions of these tests: which null hypothesis each is exact for, which alternatives it responds to, and what replacing values by ranks costs. It corrects the claim **"Mann–Whitney compares medians, so use it when the data are not normal."**

## Worked example

Darwin raised maize, *Zea mays*, from two kinds of seed: crossed, from flowers fertilised with pollen from another plant, and self-fertilised, from a single plant left to fertilise itself. Seeds that germinated together were planted in pairs on opposite sides of four large pots and measured to the tips of their leaves, in inches and eighths, while 1 to 2 feet tall (Figure 1). <!-- L01 --> The online transcription of his table misreads two fractions; the printed page and its column totals settle them. <!-- L10 --> Darwin asked Francis Galton how far the averages could be trusted, and Galton took this table as his example. <!-- L02 --> In 1935 Fisher used the same 15 pairs to introduce the randomisation test in *The Design of Experiments*. <!-- L03 -->

![Darwin's 15 pairs of crossed and self-fertilised maize heights by pot, and the 15 differences; two negatives, −67 and −48 eighths](FIG_01)
*Figure 1. Thirteen of the 15 crossed plants are taller. The two exceptions, pairs 2 and 15, are among the largest differences in either direction.*

Crossed minus self-fertilised, in eighths of an inch, the differences are 49, −67, 8, 16, 6, 23, 28, 41, 14, 29, 56, 24, 75, 60 and −48. They sum to 314 eighths, a mean of 2.617 inches. The paired t-test treats them as a normal sample: their standard deviation (SD) is 4.718 inches, the standard error 4.718/√15 = 1.218, and t = 2.617/1.218 = 2.148 on 14 degrees of freedom, p = 0.0497. Fisher computed the same t and noted that it barely exceeds the 5% point, 2.145. <!-- L04 -->

The randomisation test needs no normal model. Suppose crossing makes no difference, and suppose a coin had decided which plant of each pair got which side of the pot. Then each difference was as likely to come out −d as +d, and each of the 2¹⁵ = 32,768 ways of attaching signs to the 15 magnitudes was equally likely to be the one Darwin recorded. The test counts the assignments whose total is at least the observed 314: 835 exceed it and 28 equal it, so 863 of 32,768, a one-sided p of 2.634%. The totals are symmetric about zero, so the two-sided p-value is 1,726/32,768 = 0.0527 (Figure 2). Fisher counted this by hand, sorting the assignments by how many minus signs they carry; the lab's enumeration reproduces his table row by row. <!-- L05 --> He put part of the small gap between 0.0527 and the t-test's 0.0497 down to the t distribution's continuity, which in effect counts only half of the 28 tied totals. <!-- L06 -->

![Histogram of the totals of all 32,768 sign assignments; 863 at or above 314 and 863 at or below −314 shaded; two-sided p 0.0527](FIG_02)
*Figure 2. The reference set of the randomisation test. Darwin's total sits where 2.634% of the equally likely totals are at least as large.*

The same enumeration gives two more exact tests. The **Wilcoxon signed-rank test** replaces each magnitude by its rank, from 1 for the smallest difference (6 eighths) to 15 for the largest (75), and sums the ranks of the positive differences, a statistic called V⁺. The two negatives hold ranks 14 and 10, so V⁺ = 120 − 24 = 96; 676 of the 32,768 sign assignments reach 96 or more, and the two-sided p-value is 0.0413. The **sign test** keeps only the signs: if each is a fair coin, 13 or more plus signs out of 15 has probability 121/32,768, and the two-sided p-value is 242/32,768 = 0.0074. Four tests on one data set, each formalising "crossing makes no difference" in its own way, give 0.0497, 0.0527, 0.0413 and 0.0074.

## Intuition

Each test keeps a different part of the data, so each answers a different question (Figure 3). The t-test and the randomisation test both use the values; the randomisation test holds the 15 magnitudes fixed and asks only whether their signs look like coin flips. The signed-rank test keeps the order of the magnitudes and their signs. The sign test keeps the signs alone.

![The 15 differences as values, as signed ranks and as signs, with the t, randomisation, signed-rank and sign-test p-values](FIG_03)
*Figure 3. The order of the p-values follows what each test keeps: the two large negatives weigh most in the tests on values, less as ranks 14 and 10, and only as 2 of 15 in the sign test.*

The reference set has to come from the design. Galton, judging Darwin's table, ranked the crossed and the self-fertilised plants separately and compared the tallest with the tallest, the second with the second, and so on. The new differences have the same mean, 2.617 inches, but an SD of 1.960 instead of 4.718; Fisher computed t = 5.171 from them, a value chance would exceed once or twice in 10,000 trials, and called the rearrangement a falsification. <!-- L09 --> The plants that shared a pot shared its soil and light; a reference set that re-pairs them discards the variation the test has to measure.

## When is a permutation test exact?

The argument is a symmetry. If the null hypothesis makes every member of the reference set equally likely to be the observed data, the observed statistic is equally likely to fall at any rank among the statistics of the reference set, and the share at least as extreme is an exact p-value: the test rejects with probability at most α for every α and every sample size. For paired differences the condition is that each difference is independent and symmetric about zero; for two independent samples, that all n₁ + n₂ observations come from one distribution.

Randomisation guarantees the condition by design. Fisher's argument was that if a coin assigns the two sites in each pair, each pair's error enters the average with a plus or minus sign at equal and independent chances, whatever the soil and light did. <!-- L07 --> He framed the test as one of the wider hypothesis that the two series come from one population, normal or not, made available by the physical act of randomisation. <!-- L08 --> Darwin used no coin, and Fisher named the absence of randomisation as the one flaw in Darwin's procedure. <!-- L07 --> For these pairs, then, the exact p-value of 0.0527 rests on an assumption, that each difference was symmetric about zero under the null, rather than on the design.

When the reference set is too large to enumerate, a **Monte Carlo permutation test** draws m relabellings at random, counts the b whose statistic is at least as extreme as the observed one, and reports p = (b + 1)/(m + 1). The +1 counts the observed labelling as one of m + 1 equally likely members, and that p-value is exact. <!-- L12 --> <!-- L15 --> The tempting b/m is not: under the null, b/m is uniform on 0, 1/m, …, 1, so a 5% test with m = 1,000 rejects 51/1,001 = 5.09% of the time, and b/m is zero with probability 1/(m + 1). <!-- L12 --> A zero survives any multiple-testing correction. With 999 relabellings per test and a Bonferroni correction over 1,000 true null hypotheses, b/m rejects at least one of them with probability 63.2%; (b + 1)/(m + 1) cannot fall below 1/1,000, above the corrected threshold 0.05/1,000, so it rejects none (Figure 4b). Phipson and Smyth found genomic permutation p-values understated by about 1/m in practice: 1,000 permutations for each of 30,000 null genes leave about 30 exact zeros. <!-- L13 --> When the relabellings are drawn with replacement, as libraries do, the exact p-value is slightly below (b + 1)/(m + 1), so the +1 errs on the safe side. <!-- L14 -->

![Distribution over reruns of SciPy's default Monte Carlo p on Darwin's pairs, 19.4% at or below 0.05; family-wise error of b/m and (b + 1)/(m + 1)](FIG_04)
*Figure 4. Left: SciPy's default p-value for Darwin's pairs is a random variable centred near the exact 0.0527. Right: counting b/m sends the family-wise error towards 1 as the number of tests grows.*

The library default makes the point concrete. SciPy's `permutation_test` enumerates only when the reference set has at most `n_resamples` members, 9,999 by default; Darwin's has 32,768, so the default draws 9,999 random sign assignments and applies the +1. <!-- L36 --> Each run returns 2(B + 1)/10,000, where B, the count of draws at least as extreme, is binomial with probability 863/32,768. In 95% of runs the p-value lands between 0.0466 and 0.0592, and in 19.4% of runs it is 0.05 or less although the exact p-value is 0.0527 (Figure 4a); 1,000 actual runs with different seeds gave 21.3% ± 1.3. Near a threshold, pass `n_resamples=np.inf` to enumerate.

## Does a permutation test compare means?

A permutation test of the difference in means is exact for the hypothesis that both groups come from one distribution. As a test of equal means it is something else. Romano showed that it is asymptotically valid for equal means only when the sample sizes are equal or the variances are, <!-- L16 --> because only then does the reference set's spread match the true sampling variance of the difference. <!-- L17 --> Relabelling mixes the two groups, so the reference distribution reflects a pooled variance, as Student's pooled standard error does, and it fails in the same direction.

![Size of raw and studentised two-sample permutation tests and of Student's and Welch's t against the SD ratio, groups of 10 and 40 and of 25 and 25](FIG_05)
*Figure 5. With groups of 10 and 40, the permutation test of the raw difference tracks Student's t-test, to 29.1% when the small group has four times the SD. Studentised, it stays between 3.9% and 5.9%.*

Figure 5 measures it with normal data and equal means, 50,000 simulated data sets per point and 999 random relabellings each. With 10 and 40, the raw difference rejects 18.31% ± 0.17 when the group of 10 has twice the SD and 29.10% at four times, where Student's t-test on the same data rejects 18.34% and 29.20%. When the larger group has the larger SD the test almost never rejects: 0.06% at a quarter.

The repair is to permute a **studentised statistic**, one divided by its own estimated standard error. Welch's t, recomputed on every relabelling, keeps the exactness when the distributions are identical and is asymptotically valid for equal means when they are not; Janssen proved this for the difference in means, and Chung and Romano extended it to general parameters. <!-- L18 --> With 10 and 40 it rejects 5.73% at an SD ratio of 2, 5.81% at 4 and 3.87% at a quarter. That is not Welch's parametric test, which holds 4.95% to 5.19% on the same normal data; asymptotic validity means the rate approaches 5% as both groups grow. With 25 and 25 the raw and the studentised test are the same test, and they reject 5.06% to 5.57%. Medians are harder still: Romano found the permutation test of medians invalid even with equal sizes, <!-- L16 --> and in Chung and Romano's simulation it rejected 23.1% one-sided for two normal populations with one median and different spreads, 101 observations each, against 6.2% studentised. <!-- L19 -->

## What does the Mann–Whitney test test?

Wilcoxon's rank-sum test and Mann and Whitney's U test are one test. U counts the pairs (x, y), one value from each group, in which x is larger, ties counting a half; Mann and Whitney proposed it to test whether the two distributions are identical, and showed it consistent against alternatives in which one variable is **stochastically larger**, tending to produce larger values. <!-- L20 --> U/(n₁n₂) estimates θ = P(X > Y) + ½P(X = Y), the **Mann–Whitney functional**. <!-- L21 --> When the distributions are identical, every arrangement of the ranks is equally likely, so Mann–Whitney is a permutation test on ranks, and exact.

Three designs separate what it responds to. In the first, X is normal and Y an exponential distribution shifted left until its median is 0: equal medians, equal SDs, different shapes, and P(X > Y) = 0.4431 (Figure 6a). In the second, the exponential is shifted further, until P(X > Y) = ½ exactly, which puts its median at −0.183 (Figure 6b). In the third, both groups are normal with a common centre and unequal spreads, 10 and 40 observations, so P(X > Y) = ½ and the medians are equal.

![Normal and shifted exponential densities: equal medians with P(X > Y) = 0.443, and medians 0 and −0.183 with P(X > Y) = 0.5](FIG_06)
*Figure 6. Equal medians do not make P(X > Y) = ½, and P(X > Y) = ½ does not make the medians equal.*

With equal medians, Mann–Whitney rejects 16.7% ± 0.3 of samples at 50 per group, 50.2% at 200 and 79.7% at 400 (Figure 7a). It is detecting P(X > Y) ≠ ½, as it should; read as a test of medians, every one of those rejections is wrong. With P(X > Y) = ½ and medians 0.18 SD apart, it rejects 4.7% to 5.7% at every size: it has no power against that median difference. From 25 per group on, Welch's t-test rejects more often than either in both designs, because the means differ, by 0.307 and 0.124. Divine and colleagues document the same failure with real and constructed examples and conclude that the procedure is not a test of medians. <!-- L22 -->

![Rejection rates of Mann–Whitney, Brunner–Munzel and Welch: by n per group in both designs of Figure 6, and by SD ratio for normal groups of 10 and 40](FIG_07)
*Figure 7. Mann–Whitney follows P(X > Y) in (a) and (b). In (c), where P(X > Y) = ½ exactly, it errs like Student's t-test: 14.81% at an SD ratio of 4.*

The third design shows that Mann–Whitney is not even an exact test of P(X > Y) = ½. Its null distribution assumes identical distributions, so unequal spreads with unequal sizes move its error rate: 9.93% ± 0.21 when the group of 10 has twice the SD, 14.81% at four times, 0.71% at a quarter (Figure 7c). This is the rank version of Student's failure, which Brunner and Munzel found conservative or liberal depending on the ratio of sizes and variances. <!-- L23 --> <!-- L24 --> Their **Brunner–Munzel test** studentises the rank statistic, estimating its variance from each group's ranks and referring it to a t distribution with Welch–Satterthwaite degrees of freedom; <!-- L23 --> it is asymptotically valid for P(X > Y) = ½ when the distributions differ, <!-- L21 --> and here it rejected 4.94% to 5.67%. Karch recommends it as the default rank test for that reason. <!-- L25 --> The eighth part of this series found Mann–Whitney erring on the samples a normality pre-test sent to it; this is why.

So the choice follows the hypothesis. For means, use Welch's t-test. For P(X > Y), use Brunner–Munzel, or Mann–Whitney when identical distributions are the null you mean. For medians, use a method built for medians, such as a bootstrap interval for the difference in medians from the seventh part, *The Bootstrap: From Percentile to BCa, and Where It Breaks*. The one-sample signed-rank test has the same limit: it tests that the differences are symmetric about zero, and its target is the median of the differences only when they are symmetric. <!-- L27 -->

## How large is the effect? The Hodges–Lehmann estimate

A rank test gives a p-value; the **Hodges–Lehmann estimate** gives the matching effect size, by inverting the test. <!-- L26 --> For one sample it is the median of the **Walsh averages**, (dᵢ + dⱼ)/2 for every pair i ≤ j, each difference paired with itself included. Darwin's 15 differences have 120 Walsh averages, and their median is 3.125 inches (Figure 8), against a mean of 2.617 and a median difference of 3.0.

![Darwin's 120 Walsh averages in order; median 3.125; the 26th smallest, 0.5, and the 26th largest, 5.1875, bound the interval](FIG_08)
*Figure 8. The estimate and its interval are order statistics of the Walsh averages, so the two large negatives move them less than they move the mean.*

The confidence interval collects the shifts the signed-rank test would not reject. The exact signed-rank distribution for 15 differences gives P(V⁺ ≤ 25) = 2.4%, so the interval runs from the 26th smallest to the 26th largest Walsh average: 0.5 to 5.1875 inches, with exact confidence 95.21%, not 95%, because V⁺ takes whole-number values. R's `wilcox.test(conf.int = TRUE)` prints the same estimate and interval, computed by Bauer's algorithm. <!-- L27 --> The t-interval is 0.004 to 5.229.

The estimate's target is the **pseudomedian**, the median of (u + v)/2 for two independent draws u and v, which equals the median when the distribution is symmetric. <!-- L27 --> The two-sample version is the median of the n₁n₂ differences xᵢ − yⱼ. Under a pure shift it estimates the shift; otherwise it estimates the median of X − Y, which R's documentation warns is not the difference in medians. <!-- L27 --> In the equal-medians design of Figure 6a that target is −0.18, and 200 simulated samples of 400 per group gave −0.186 ± 0.005, while the medians differ by nothing.

## What do ranks cost?

The **asymptotic relative efficiency** (ARE) of one test to another is the limiting ratio of the sample sizes they need for equal power against a small shift. For the rank-sum test against the t-test it is 12σ²(∫f²)², with f the density of the data: 3/π = 0.955 for normal data, so ranks waste about 5% of the sample. <!-- L30 --> Hodges and Lehmann proved that it never falls below 0.864 for a shift of any continuous distribution, <!-- L29 --> and a parabolic density attains that minimum; with heavy tails it grows without bound, and for t distributions the rank test is the more efficient one at 18 degrees of freedom or fewer. <!-- L30 --> The same bounds hold for the signed-rank test against the one-sample t-test on symmetric data, and for Kruskal–Wallis against the F test. <!-- L29 -->

![Power of Welch's t and Mann–Whitney at n = 20 per group for eight distributions, with each one's ARE, from 0.864 to 1.900](FIG_09)
*Figure 9. In samples of 20, the rank test loses up to 6.3 points of power in light-tailed shapes and gains up to 10.9 in heavy-tailed ones.*

ARE is a limit, so Figure 9 measures power at 20 per group, for a shift that gives Student's test 80% power on normal data, 0.91 SD. For normal data Mann–Whitney has 77.6% against Welch's 79.7%; for the parabolic, 74.1% against 79.9%. The uniform distribution, whose ARE is exactly 1, still costs the rank test 6.3 points at this size: 73.5% against 79.8%. In the tails the trade reverses: 88.0% against 79.8% for the Laplace distribution, 89.2% against 80.5% for a normal with 10% contamination at three times the SD, and 95.0% against 84.0% for t with 3 degrees of freedom.

## Rank correlations: Spearman and Kendall

The same ideas give two rank correlations. **Spearman's ρ** is Pearson's correlation computed on the ranks; **Kendall's τ** is the share of concordant pairs minus the share of discordant ones, a pair being concordant when the two variables order it the same way. <!-- L31 --> Both measure monotone association, not linear association. On the law-school sample the seventh part bootstrapped, the average LSAT score and undergraduate grade-point average (GPA) of 15 schools' classes, <!-- L40 --> Pearson's r is 0.776, Spearman's ρ is 0.796 (the squared rank differences sum to 114) and Kendall's τ is (86 − 19)/105 = 0.638 (Figure 10).

![Law-school GPA against LSAT for 15 schools, as values and as ranks, with r 0.776, ρ 0.796, τ 0.638 and their p-values](FIG_10)
*Figure 10. One sample, three coefficients. Spearman's p-value depends on how it is computed: 0.00064 exactly, 0.00038 by SciPy's t approximation.*

Their null hypothesis is independence, under which all 15! orderings of one variable against the other are equally likely, so each has an exact permutation test. Kendall's exact p-value is 0.00053, and SciPy and R agree. Spearman's, counted over all 15! = 1.3 × 10¹² orderings by dynamic programming, is 0.00064; SciPy's `spearmanr` reports 0.00038 from a t approximation, and R's `cor.test` 0.00061 from an Edgeworth series, which it uses above n = 9. <!-- L34 --> <!-- L39 --> With 99,999 random reorderings the Monte Carlo p-values are 0.00078 for Spearman, 0.00067 for Kendall and 0.00134 for Pearson's r, whose normal-theory t-test gives 0.00067. As with means, a permutation test of a correlation is exact for independence but not for zero correlation; DiCiccio and Romano studentise it for that hypothesis. <!-- L33 --> The **Kruskal–Wallis test** extends the rank-sum test to three or more groups, comparing their rank sums against a chi-squared reference, and like Mann–Whitney its null hypothesis is that all groups come from one distribution. <!-- L32 --> <!-- L35 -->

## The math

| Symbol | Meaning |
|---|---|
| G, g | the reference set of transformations (sign changes, relabellings) and one of them |
| T(X), m, b | the statistic on data X; random relabellings drawn; how many are at least as extreme |
| dᵢ, Rᵢ, V⁺ | paired differences; the rank of the absolute difference; the sum of the positive ranks |
| U, θ | the Mann–Whitney count of pairs won by X; P(X > Y) + ½P(X = Y) |
| D, SS | the difference in group means; the total sum of squares about the grand mean |

**The exact p-value** is the share of the reference set at least as extreme as the data: <!-- L12 -->

$$
p = \frac{1}{|G|}\,\#\{g \in G : |T(gX)| \ge |T(X)|\}, \qquad p_{\mathrm{MC}} = \frac{1 + b}{1 + m} \tag{1}
$$

For Darwin's pairs G holds the 32,768 sign changes and p = 1,726/32,768; with m random draws, b/m would be zero in a share 1/(m + 1) of null data sets, which (1 + b)/(1 + m) rules out.

**The signed-rank statistic** sums the ranks of the positive differences; with no ties, under the null each rank joins the sum with probability ½:

$$
V^{+} = \sum_{i=1}^{n} R_i \,\mathbf{1}[d_i \gt 0], \qquad \mathbb{E}\,V^{+} = \frac{n(n+1)}{4}, \qquad \operatorname{Var} V^{+} = \frac{n(n+1)(2n+1)}{24} \tag{2}
$$

For n = 15 the mean is 60 and the SD √310 = 17.6, so Darwin's 96 sits 2.04 SDs above it: a normal-approximation p of 0.041, beside the exact 0.0413.

**Mann–Whitney's U** estimates the functional θ; under identical distributions its variance is fixed by the sample sizes alone: <!-- L21 -->

$$
U = \sum_{i=1}^{n_1}\sum_{j=1}^{n_2}\left(\mathbf{1}[x_i \gt y_j] + \tfrac12\,\mathbf{1}[x_i = y_j]\right), \qquad \mathbb{E}\,\frac{U}{n_1 n_2} = \theta, \qquad \operatorname{Var}_{F=G} U = \frac{n_1 n_2 (n_1 + n_2 + 1)}{12} \tag{3}
$$

The last formula is the one that unequal shapes break: in Figure 7c θ = ½ but U's true variance differs from it, and Brunner–Munzel's test replaces it with an estimate from each group's ranks.

**Equal sizes make raw and studentised the same test.** With n per group, the within-group sums of squares are the total minus the between-group part, and the total does not change under relabelling:

$$
(n - 1)\left(s_1^2 + s_2^2\right) = \mathrm{SS} - \frac{n D^2}{2}, \qquad t_W^2 = \frac{D^2}{(s_1^2 + s_2^2)/n} = \frac{n(n-1)D^2}{\mathrm{SS} - nD^2/2} \tag{4}
$$

Welch's t² increases with D² across the relabellings of one data set, so both tests rank them identically, which is why the 25-and-25 curves of Figure 5 coincide.

**The Hodges–Lehmann interval** takes order statistics of the N = n(n + 1)/2 Walsh averages W, with k the smallest value at which the exact null distribution function of V⁺ reaches α/2: <!-- L26 --> <!-- L27 -->

$$
\hat\Delta = \operatorname{median}\left\{\frac{d_i + d_j}{2} : i \le j\right\}, \qquad \left[\,W_{(k)},\; W_{(N - k + 1)}\,\right] \tag{5}
$$

For Darwin's pairs N = 120, k = 26, and the interval is W₍₂₆₎ = 0.5 to W₍₉₅₎ = 5.1875 inches around Δ̂ = 3.125.

**The efficiency of ranks** for a density f with variance σ²: <!-- L30 -->

$$
\mathrm{ARE}(U, t) = 12\,\sigma^2 \left(\int f^2(x)\,dx\right)^2 \tag{6}
$$

For the normal, ∫f² = 1/(2√π), so the ARE is 12/(4π) = 3/π = 0.955; heavier tails make ∫f² larger relative to σ², and the rank test more efficient.

## Implementation

Darwin's exact tests, the Hodges–Lehmann interval and a studentised two-sample permutation test, in SciPy. Run as printed, the first part gives the worked example's numbers.

```python
import numpy as np
from scipy import stats

d8 = np.array([49, -67, 8, 16, 6, 23, 28, 41, 14, 29, 56, 24, 75, 60, -48])     # Darwin's differences, eighths
signs = 1 - 2 * ((np.arange(2**15)[:, None] >> np.arange(15)) & 1)             # all 32,768 sign assignments
totals = signs @ np.abs(d8)                                                     # exact integers: no tie is lost
print("at least 314:", (totals >= 314).sum(), "| two-sided p:", (np.abs(totals) >= 314).mean())

res = stats.permutation_test((d8,), lambda x, axis: x.sum(axis=axis), permutation_type="samples",
                             vectorized=True, n_resamples=np.inf)              # np.inf enumerates; default draws 9,999
print("SciPy exact:", res.pvalue, "| t:", stats.ttest_1samp(d8, 0).pvalue,
      "| signed-rank:", stats.wilcoxon(d8).pvalue, "| sign:", stats.binomtest(13, 15).pvalue)

v_null = np.bincount((signs > 0) @ np.arange(1, 16), minlength=121)            # V+ over the same enumeration
k = int(np.searchsorted(np.cumsum(v_null) / 2**15, 0.025))                      # 26: R's qsignrank(0.025, 15)
i, j = np.triu_indices(15)
walsh = np.sort(d8[i] + d8[j]) / 16                                             # 120 Walsh averages, inches
print("Hodges-Lehmann:", np.median(walsh), "| interval:", walsh[k - 1], "to", walsh[120 - k])

def welch_t(x, y, axis):                                                        # the studentised statistic
    return (x.mean(axis=axis) - y.mean(axis=axis)) / np.sqrt(
        x.var(axis=axis, ddof=1) / x.shape[axis] + y.var(axis=axis, ddof=1) / y.shape[axis])

rng = np.random.default_rng(10)
x, y = rng.normal(0, 2, 10), rng.normal(0, 1, 40)                               # equal means, unequal spreads
print("studentised permutation:", stats.permutation_test((x, y), welch_t, vectorized=True, rng=rng).pvalue,
      "| Brunner-Munzel:", stats.brunnermunzel(x, y).pvalue, "| Mann-Whitney:", stats.mannwhitneyu(x, y).pvalue)
```

It prints 863 and 0.052673 for the enumeration, matched by `permutation_test`; 0.049703, 0.041260 and 0.007385 for the t, signed-rank and sign tests; and 3.125 with the interval 0.5 to 5.1875. The last line is one simulated data set, so its three p-values are illustrations, not measurements. The line that matters most is the first `print`: the totals are integers, so the 28 assignments that tie with Darwin's 314 are all counted.

### Reading the library's output

SciPy and R differ in which test they run by default and in what they report. <!-- L28 --> <!-- L34 --> <!-- L35 --> <!-- L36 --> <!-- L37 --> <!-- L38 --> <!-- L39 -->

| Task | SciPy 1.18.1 | R 4.5.2 |
|---|---|---|
| permutation test | `permutation_test`: exact if the reference set has at most `n_resamples` members (default 9,999), else random draws with the +1; two-sided p doubles the smaller tail | none in base R |
| signed-rank | `wilcoxon`: exact up to 50 differences without zeros or ties; reports the smaller rank sum, 24 for Darwin | `wilcox.test`: exact below 50 without ties; reports V⁺, 96; `conf.int = TRUE` adds Hodges–Lehmann |
| rank-sum | `mannwhitneyu`: exact only if a group has 8 or fewer values and there are no ties, else a normal approximation with continuity correction | `wilcox.test(x, y)`: exact while both groups are under 50, without ties |
| Brunner–Munzel | `brunnermunzel`: t reference, Welch–Satterthwaite degrees of freedom | not in base R |
| Spearman | `spearmanr`: t approximation | `cor.test`: AS 89, exact below n = 10, Edgeworth series above |
| Kendall | `kendalltau`: exact without ties up to n = 33 | `cor.test`: exact below n = 50 without ties |
| Kruskal–Wallis | `kruskal`: chi-squared | `kruskal.test`: chi-squared |

Two of these change answers. SciPy doubles the smaller one-sided p for a two-sided permutation test, which equals the share of |T| at least |t| only when the reference distribution is symmetric, as Darwin's is: on one data set of 4 and 6 values the doubled p was 0.676 and the |T| share 0.738. And the same two-sample data give different p-values in the two libraries once a group passes 8 values: on 12 and 15 values, SciPy's normal approximation gave 0.1960 where R's exact test gave 0.1995. The lab's `permutation.py` computes every number in this post in five stages; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** choosing Mann–Whitney because the data look skewed and reading its p-value as a comparison of medians. With equal medians and equal SDs it rejected 79.7% of samples of 400 per group; with medians 0.18 SD apart and P(X > Y) = ½ it rejected about 5%. Choose the test from the hypothesis: Welch for means, Brunner–Munzel for P(X > Y), a median method for medians.

- **"Assumption-free."** Permutation and rank tests are exact only under exchangeability. Darwin's pairs were never randomised, so their exact 0.0527 rests on symmetry of each difference under the null.
- **A raw permutation test of means in an unbalanced design.** With groups of 10 and 40 it erred 18.3% when the small group had twice the SD. Permute Welch's t instead, or balance the design.
- **Reporting b/m, or p = 0.** Use (b + 1)/(m + 1), and draw enough relabellings for the smallest p you need: under a Bonferroni correction over k tests, m + 1 must reach k/α before any test can reject.
- **Trusting a library default near the line.** SciPy's 9,999 random sign flips put Darwin's pairs at or below 0.05 in 19.4% of runs. Enumerate when the reference set is small enough.
- **Spearman's p from the t approximation in a small sample.** For the law-school sample it gave 0.00038 against the exact 0.00064.
- **Ties and floating point.** The exact null distributions above assume no ties; with ties, use midranks and the conditional permutation distribution. Totals that tie in exact arithmetic can differ in floating point, so compare in exact units or within a tolerance, as SciPy does.
- **The two-sample Hodges–Lehmann estimate as a difference in medians.** In the equal-medians design it estimates −0.18.
- **Dependent data.** Every test here assumes independent pairs or units. Clustered or time-ordered data break exchangeability, and the reference set must respect the dependence. Randomisation inference built on an experiment's actual assignment belongs with experiment design, outside this series.

## Key takeaways

- A permutation test is exact when its relabellings are exchangeable under the null: all 32,768 sign assignments of Darwin's pairs give p = 0.0527 beside the t-test's 0.0497, and because Darwin used no coin, that exactness rests on symmetry, not on the design.
- Report (b + 1)/(m + 1) for random relabellings, and enumerate when you can: b/m gave a 63.2% family-wise error over 1,000 null tests with 999 relabellings each, and SciPy's default draws put Darwin's p at or below 0.05 in 19.4% of runs.
- Exact for identical distributions is not exact for equal means: with groups of 10 and 40 the raw permutation test erred 18.3% at an SD ratio of 2, and studentising the statistic brought it to 5.7%.
- Mann–Whitney responds to P(X > Y) and is exact only for identical distributions: 79.7% rejections at equal medians, about 5% at unequal medians with P(X > Y) = ½, and 14.8% for equal-centre normal groups with unequal spreads, where Brunner–Munzel's test held 4.9% to 5.7%.
- Ranks cost little: an ARE of 3/π = 0.955 for normal data and never below 0.864, with up to 10.9 points of power gained in heavy tails at 20 per group; the Hodges–Lehmann estimate, 3.125 inches with an interval of 0.5 to 5.1875 for Darwin, is the effect size that goes with them.

## Try it yourself

**E1, reproduce.** From the 15 differences alone, compute V⁺ for the signed-rank test and the two-sided p-value of the sign test.

<details><summary>Answer</summary>

**Answer.** The absolute differences in order are 6, 8, 14, 16, 23, 24, 28, 29, 41, 48, 49, 56, 60, 67, 75, so the negatives, 48 and 67, hold ranks 10 and 14. The ranks sum to 15 × 16/2 = 120, so V⁺ = 120 − 24 = 96. Thirteen of 15 signs are positive; the probability of 13 or more is (1 + 15 + 105)/32,768 = 121/32,768, and the two-sided p-value is 242/32,768 = 0.0074.

</details>

**E2, inspect.** Figure 2's totals run from −544 to 544 eighths. Without enumerating, show that every sign assignment with at most one minus sign totals more than 314, and every one with seven or more totals less.

<details><summary>Answer</summary>

**Answer.** The magnitudes sum to 544, and a minus sign on a magnitude takes twice it off the total. One minus sign takes off at most 2 × 75 = 150, leaving at least 394. Seven minus signs take off at least twice the seven smallest magnitudes, 2 × (6 + 8 + 14 + 16 + 23 + 24 + 28) = 238, leaving at most 306. So only assignments with 2 to 6 minus signs can tie or straddle 314, and those are the rows Fisher tabulated.

</details>

**E3, predict.** Keep SciPy's random sign flips for Darwin's pairs but raise `n_resamples` tenfold, to 99,999. Before reading the answer, use the binomial model behind Figure 4a to predict roughly how often a run would then report p ≤ 0.05.

<details><summary>Answer</summary>

**Answer.** Rarely: in 0.38% of runs. The count B is now binomial with 99,999 trials and probability 863/32,768, so its mean is 2,633.6 and its SD 50.6. A run reports p ≤ 0.05 when 2(B + 1)/100,000 ≤ 0.05, that is when B ≤ 2,499, which is 2.65 SDs below the mean. Ten times the draws shrink the SD of the reported p by √10, from 0.0032 to 0.0010, while the gap between the exact 0.0527 and 0.05 stays 0.0027. Enumerating removes the randomness altogether.

</details>

The lab carries the full ladder, from reproducing these numbers to diagnosing a randomisation test that counts 842 assignments where Fisher counted 863, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E4 exercises with answers, and cleanup.
- [`permutation.py`](LAB_02) — the five stages: example, twosample, mannwhitney, efficiency and correlation.
- [`darwin1876_zea_mays.csv`](LAB_03) — Darwin's 15 pairs (1876, public domain) in eighths of an inch, with provenance; put it in a `data` folder.
- [`law_school_82.csv`](LAB_04) — the law-school data (CRAN `bootstrap`, BSD 3-clause), with provenance; put it in a `data` folder.
- [`requirements.txt`](LAB_05) — the pinned NumPy and SciPy versions.
- [`captures.json`](LAB_06) — the author's full run, machine-readable, with the private cross-check against R.
- [`captures-quick.json`](LAB_07) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_08) — the author's full run as printed.
- [`notebook.ipynb`](LAB_09) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-permutation-and-rank-tests.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. C. Darwin. *The Effects of Cross and Self Fertilisation in the Vegetable Kingdom.* London: John Murray, 1876. Text and page scans in J. van Wyhe (ed.), *The Complete Work of Charles Darwin Online*. https://darwin-online.org.uk/content/frameset?itemID=F1249&viewtype=text&pageseq=1 (accessed 2026-11-23)
2. R. A. Fisher. *The Design of Experiments.* Edinburgh: Oliver and Boyd, 1935; second edition 1937, chapter III, read for this post.
3. H. A. David. "The beginnings of randomization tests." *The American Statistician* 62(1): 70–72, 2008. https://doi.org/10.1198/000313008X269576
4. M. D. Ernst. "Permutation methods: a basis for exact inference." *Statistical Science* 19(4): 676–685, 2004. https://doi.org/10.1214/088342304000000396
5. B. Phipson and G. K. Smyth. "Permutation p-values should never be zero: calculating exact p-values when permutations are randomly drawn." *Statistical Applications in Genetics and Molecular Biology* 9(1): Article 39, 2010. https://doi.org/10.2202/1544-6115.1585
6. J. Hemerik and J. J. Goeman. "Exact testing with random permutations." *TEST* 27(4): 811–825, 2018. https://doi.org/10.1007/s11749-017-0571-1
7. J. P. Romano. "On the behavior of randomization tests without a group invariance assumption." *Journal of the American Statistical Association* 85(411): 686–692, 1990. https://doi.org/10.1080/01621459.1990.10474928
8. E. Chung and J. P. Romano. "Exact and asymptotically robust permutation tests." *The Annals of Statistics* 41(2): 484–507, 2013. https://doi.org/10.1214/13-AOS1090
9. A. Janssen. "Studentized permutation tests for non-i.i.d. hypotheses and the generalized Behrens–Fisher problem." *Statistics & Probability Letters* 36(1): 9–21, 1997. https://doi.org/10.1016/S0167-7152(97)00043-6
10. F. Wilcoxon. "Individual comparisons by ranking methods." *Biometrics Bulletin* 1(6): 80–83, 1945. https://doi.org/10.2307/3001968
11. H. B. Mann and D. R. Whitney. "On a test of whether one of two random variables is stochastically larger than the other." *The Annals of Mathematical Statistics* 18(1): 50–60, 1947. https://doi.org/10.1214/aoms/1177730491
12. M. P. Fay and M. A. Proschan. "Wilcoxon–Mann–Whitney or t-test? On assumptions for hypothesis tests and multiple interpretations of decision rules." *Statistics Surveys* 4: 1–39, 2010. https://doi.org/10.1214/09-SS051
13. G. W. Divine, H. J. Norton, A. E. Barón and E. Juarez-Colunga. "The Wilcoxon–Mann–Whitney procedure fails as a test of medians." *The American Statistician* 72(3): 278–286, 2018. https://doi.org/10.1080/00031305.2017.1305291
14. E. Brunner and U. Munzel. "The nonparametric Behrens–Fisher problem: asymptotic theory and a small-sample approximation." *Biometrical Journal* 42(1): 17–25, 2000. https://doi.org/10.1002/(SICI)1521-4036(200001)42:1%3C17::AID-BIMJ17%3E3.0.CO;2-U
15. M. W. Fagerland and L. Sandvik. "The Wilcoxon–Mann–Whitney test under scrutiny." *Statistics in Medicine* 28(10): 1487–1497, 2009. https://doi.org/10.1002/sim.3561
16. J. D. Karch. "Psychologists should use Brunner–Munzel's instead of Mann–Whitney's U test as the default nonparametric procedure." *Advances in Methods and Practices in Psychological Science* 4(2), 2021. https://doi.org/10.1177/2515245921999602
17. J. L. Hodges and E. L. Lehmann. "Estimates of location based on rank tests." *The Annals of Mathematical Statistics* 34(2): 598–611, 1963. https://doi.org/10.1214/aoms/1177704172
18. D. F. Bauer. "Constructing confidence sets using rank statistics." *Journal of the American Statistical Association* 67(339): 687–690, 1972. https://doi.org/10.1080/01621459.1972.10481279
19. J. L. Hodges and E. L. Lehmann. "The efficiency of some nonparametric competitors of the t-test." *The Annals of Mathematical Statistics* 27(2): 324–335, 1956. https://doi.org/10.1214/aoms/1177728261
20. C. Spearman. "The proof and measurement of association between two things." *The American Journal of Psychology* 15(1): 72–101, 1904. https://doi.org/10.2307/1412159
21. M. G. Kendall. "A new measure of rank correlation." *Biometrika* 30(1–2): 81–93, 1938. https://doi.org/10.1093/biomet/30.1-2.81
22. D. J. Best and D. E. Roberts. "Algorithm AS 89: the upper tail probabilities of Spearman's rho." *Applied Statistics* 24(3): 377–379, 1975. https://doi.org/10.2307/2347111
23. W. H. Kruskal and W. A. Wallis. "Use of ranks in one-criterion variance analysis." *Journal of the American Statistical Association* 47(260): 583–621, 1952. https://doi.org/10.1080/01621459.1952.10483441
24. C. J. DiCiccio and J. P. Romano. "Robust permutation tests for correlation and regression coefficients." *Journal of the American Statistical Association* 112(519): 1211–1220, 2017. https://doi.org/10.1080/01621459.2016.1202117
25. B. Efron and R. J. Tibshirani. *An Introduction to the Bootstrap.* Chapman & Hall, 1993; the law-school data as distributed in the CRAN package `bootstrap`. https://cran.r-project.org/package=bootstrap
26. R Core Team. R 4.5.2 documentation: `wilcox.test`, `cor.test`, `kruskal.test`. https://stat.ethz.ch/R-manual/R-patched/library/stats/html/wilcox.test.html (accessed 2026-11-23)
27. SciPy 1.18.1 documentation, `scipy.stats`. https://docs.scipy.org/doc/scipy/reference/stats.html (accessed 2026-11-23)
