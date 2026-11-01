---
title: "Which Statistical Test? The Design Decides, Not the Data"
slug: choosing-a-statistical-test
date: 2026-11-01
updated: 2026-11-01
summary: "Paired, the same ten patients give p = 0.003; as two groups, p = 0.08. Choose the test from the design: Student's t errs 18% where Welch's holds 5%."
tags: [data-science, statistics, hypothesis-testing, welch-t-test, paired-t-test, fisher-exact-test, anova]
category: data-science
series: statistics-for-data-scientists
series_position: 8
tier: L3
difficulty: advanced
prerequisites: ["hypothesis tests, type I error and power", "the t statistic", "Python with NumPy and SciPy"]
reading_minutes: 32
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/choosing-a-statistical-test"
---

![Type I error of Student's and Welch's t-tests against the SD ratio for groups of 10 and 40: Student's climbs to 29%, Welch's stays at 5%](COVER)

> [!NOTE]
> **Insights** — Choose a test from how the data were collected, not from how they look. Student's ten patients each took both sleeping drugs, so the paired t-test, p = 0.0028, is the analysis the design dictates; read as two groups, the same twenty numbers give p = 0.079. For two independent groups, Welch's t-test keeps its 5% error rate where Student's does not: with groups of 10 and 40, Student's test rejects a true null 18.3% of the time when the smaller group has twice the standard deviation. Testing the assumptions first and then choosing does worse than always using Welch, and for a 2 × 2 table the margins the design fixed decide between Fisher's exact test and its alternatives.

**Level:** advanced · **You need:** hypothesis tests, type I error and power; the t statistic; Python with NumPy and SciPy · **Time:** ~32 min

**Jump to:** [worked example](#worked-example) · [Student vs Welch](#when-does-student-s-t-test-keep-its-5) · [pre-testing](#does-checking-the-assumptions-first-help) · [2 × 2 tables](#which-test-fits-a-2-2-table) · [ANOVA](#what-does-anova-s-f-compare) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **computed** or **measured** come from its lab: one NumPy, SciPy and statsmodels script, seeded so every number repeats exactly. Type I error rates and power of the t-tests are computed exactly, by numerical integration, and those of the 2 × 2 tests by summing over every possible table; the rest are simulated and printed as an estimate ± its Monte Carlo standard error (MCSE). Published numbers are **quoted**, and library conventions are read from the libraries' source code.

## Why this matters

R ships Student's 1908 sleep data as twenty rows: the extra hours of sleep a patient gained, the drug that produced them, and the patient. <!-- L01 --> Split the hours by drug, hand the two halves to a two-sample t-test, and it reports p = 0.079: no evidence that one drug beats the other at the 5% level. Hand the same twenty numbers to a paired t-test and it reports p = 0.0028. Nothing about the numbers decides between the two answers. The design does: every patient took both drugs, and R's help page warns that its `group` variable is misleading, because the values are measurements on ten persons, not two groups. The same question comes up whenever an A/B comparison is run on the same users, a model is scored before and after a change on the same test set, or two groups of very different sizes are compared with whatever test the library runs by default.

## The problem

A test promises an error rate: when the null hypothesis is true, a 5% test rejects in 5% of repetitions. The fifth part of this series, *p-Values and Power: How Wrong Can a Significant Result Be?*, defined that promise and power beside it. The repetitions are repetitions of the **design**: how the units were chosen, which conditions each unit received, and which totals were fixed in advance. A test's reference distribution is the distribution of its statistic over those repetitions, so a test built for one design keeps its promise only for that design.

Three designs cover most comparisons of a numerical outcome. In a **paired design** each unit is measured under both conditions, so the comparison is made within units. In a design with **independent groups**, each unit appears once, in one group. With three or more independent groups the comparison is a one-way analysis of variance. For two independent groups there are two standard tests. **Student's two-sample t-test** pools both groups' variances into one estimate, weighting each by its degrees of freedom, and assumes the two population variances are equal. **Welch's t-test** keeps the variances separate and estimates its degrees of freedom from them, the Welch–Satterthwaite approximation. <!-- L05 --> Both assume roughly normal data.

When an assumption is in doubt, a common habit is to test it first: a test of equal variances, a test of normality, and then a choice of test. This part takes the habit as one procedure and measures it. It corrects the claim **"check normality and equal variances first, then choose the test."** It also measures what each condition is worth when it fails, and reads the defaults that choose a test for you when you name none.

## Worked example

The data are Student's Illustration I, which he took from a table published by Cushny and Peebles: the additional hours of sleep ten patients gained on each of two soporific drugs (Figure 1). <!-- L02 --> The second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*, used the same ten patients to build the t statistic; this part asks which analysis their design calls for. The trial behind them was a within-patient trial at Kalamazoo, which Senn and Richardson showed that Student and Fisher both misquoted; what matters here is that each patient received both drugs. <!-- L03 -->

![Ten patients' extra hours of sleep on two drugs, joined by lines, and drug 2 plotted against drug 1; correlation 0.795](FIG_01)
*Figure 1. On either drug the patients spread over more than five hours, and a patient high on one drug is high on the other (r = 0.795). Nine of ten gained more sleep on drug 2; one gained the same.*

**Unpaired.** Treat the columns as two groups of ten. The means are 0.75 and 2.33 hours, a difference of 1.58, and the standard deviations are 1.789 and 2.002. Student's pooled variance is (3.201 + 4.009)/2 = 3.605, so the standard error (SE) of the difference is √(3.605 × (1/10 + 1/10)) = 0.849, t = 1.58/0.849 = 1.861 on 18 degrees of freedom, and p = 0.0792. Welch's test uses the same standard error here, because the groups are the same size, but 17.78 degrees of freedom: p = 0.0794.

**Paired.** Subtract within each patient. The ten differences have mean 1.58, the same number, and standard deviation 1.230. The standard error is 1.230/√10 = 0.389, t = 1.58/0.389 = 4.062 on 9 degrees of freedom, and p = 0.0028, with a 95% interval for the mean difference of 0.70 to 2.46 hours.

The mean difference did not change; its standard error fell by a factor of 2.18. The reason is the correlation between a patient's two results, 0.795 across the ten patients. The variance of a difference is the sum of the two variances minus twice their covariance:

Var(d) = 3.201 + 4.009 − 2 × 2.848 = 1.513.

The unpaired test charges the comparison with the sum of the two variances, 7.210, as if each drug had been given to different patients; pairing subtracts twice the covariance, 5.697, the part of a patient's two results that comes from the patient. A parallel-group trial would need about 48 patients per drug, estimated from these sample variances, to estimate the difference as precisely as these ten patients did. Student saw it in 1908: he analysed the differences as a new series and attributed their small standard deviation to the two drugs acting alike on the same patient. <!-- L02 --> Figure 2 shows what the extra precision does to the test.

![Null distributions of the mean difference as two groups (SE 0.849, p = 0.079) and paired (SE 0.389, p = 0.0028); observed 1.58](FIG_02)
*Figure 2. The same difference of 1.58 hours, divided by two standard errors: 0.849 when the patients' own spread stays in the error, 0.389 when pairing removes it.*

The layout is the trap. R stores `sleep` in long form, one row per measurement with the drug in `group` and the patient in `ID`, which looks like two groups. From R 4.0.0 the formula interface accepted `paired = TRUE`, although a formula such as `extra ~ group` carries no patient identifier, so the only pairing it can make is by row order; R 4.4.0 rejects `paired` there and points to `Pair(x1, x2) ~ 1`, which pairs explicitly. <!-- L04 --> In R 4.5.2, `t.test(extra ~ group, data = sleep, paired = TRUE)` stops with "cannot use 'paired' in formula method".

## Intuition

A test asks how its statistic would vary if the study were repeated with no effect present, and the design says what a repetition is. In the sleep trial a repetition keeps each patient and gives them both drugs again; whatever made patient 7 gain 3.7 and 5.5 hours appears in both numbers and cancels in the difference. With independent groups a repetition draws new patients, so between-patient spread is part of the error, and the test has to say how it treats two groups whose spreads differ. For counts in a 2 × 2 table the question is which totals a repetition would hold fixed, and 2 × 2 tables arise from at least three designs that differ in exactly that (Figure 3). <!-- L18 -->

![Design-to-test map: paired units to the paired t-test, independent groups to Welch's tests, a 2 × 2 table by its fixed margins](FIG_03)
*Figure 3. Each branch is a question about how the data were collected. None asks what the histogram looks like.*

The analogy that misleads is to treat a test as a tool for a kind of data: a t-test for two columns of numbers, a chi-squared test for a table. The same two columns are a paired design or two groups, and the same table is exact under one design and conservative under another.

## When does Student's t-test keep its 5%?

Student's test pools the variances with weights n₁ − 1 and n₂ − 1, so the larger group dominates the pooled estimate. The variance of the difference in means is σ₁²/n₁ + σ₂²/n₂, in which the smaller group's variance carries the larger weight. When the sizes are equal the two weightings agree; when sizes and variances both differ they do not, and the error rate moves in a predictable direction. If the smaller group has the larger variance, the pooled standard error is too small and the test rejects too often, which is called **liberal**; if the larger group has the larger variance, the test is **conservative**. <!-- L08 --> The first case is called **negative pairing** of sizes and variances, the second **positive pairing**.

For normal data the error rate of either test can be computed exactly. Given the two sample variances, the difference in means is normal and independent of them, so the probability of rejecting is a normal tail; averaging it over the two chi-squared distributions of the variances is a two-dimensional integral, evaluated here by quadrature to 10⁻¹². Figure 4 plots the exact **size** (the probability that a 5% test rejects a true null) of both tests against the ratio of the two populations' standard deviations (SDs).

![Exact type I error of Student's and Welch's t-tests against the SD ratio for 10 and 40 and for 25 and 25; Student's reaches 29.4%](FIG_04)
*Figure 4. With groups of 10 and 40, Student's error follows the pairing: 0.07% when the group of 10 has a quarter of the SD, 29.37% when it has four times. Welch's stays between 4.97% and 5.15%. The dots are simulations of 200,000 pairs of samples each.*

With 10 against 40, a smaller group with 1.5 times the standard deviation already gives Student's test a size of 12.17%, twice the SD 18.25%, four times 29.37%. In the other direction its size falls to 0.52% at half the SD, a test that almost never rejects and so has little power. With 25 and 25 the largest size anywhere in the range is 5.44%, at a fourfold ratio: with equal sizes Student's test is robust to unequal variances, as Box showed for the one-way analysis of variance. <!-- L09 --> Welch's test stays within 0.15 points of 5% everywhere. Simulation agrees with the quadrature within 1.8 MCSE at every point checked.

Welch's test is not free. Its degrees of freedom are estimated from the two sample variances, and with 10 against 40 the smaller group's noisier variance dominates them, so when the variances really are equal it spends power that Student's pooled estimate would not. Figure 5 measures the price.

![Power of Student's and Welch's tests with equal SDs, for 25 and 25 and for 10 and 40; Welch loses up to 4.6 points of power](FIG_05)
*Figure 5. With equal SDs, Welch's test gives up 0.08 points of power in the balanced design and up to 4.6 points with 10 against 40, where its degrees of freedom are near 14 rather than 48.*

At the difference Student's test detects with 80.0% power, 0.81 standard deviations for 25 and 25, Welch's power is 79.9%; for 10 against 40, at 1.01 standard deviations, it is 75.6%. Delacre, Lakens and Leys found power very similar in balanced designs across many distributions, with Student's largest advantage in their balanced simulations about 5 points, and they recommend Welch's test by default. <!-- L10 --> Their 2022 correction keeps that recommendation and withdraws two of the paper's generalisations, including one to unequal sample sizes drawn from highly skewed distributions. <!-- L11 --> The numbers in this section are for normal data; skewness with unequal sizes is a further failure that neither test escapes.

## Does checking the assumptions first help?

The habit has two common forms. In the first, **Levene's test** of equal variances, an F-test on each value's absolute distance from its group's centre, decides: Welch's test if it rejects at 5%, Student's otherwise. The version run here centres at the median, Brown and Forsythe's variant and SciPy's default. <!-- L16 --> In the second, a **Shapiro–Wilk test** of normality runs on each group first, and if either rejects, a rank test, Mann–Whitney's, replaces both t-tests. <!-- L35 --> Both are **two-stage procedures**: the final p-value comes from a test chosen by another test on the same data. Figure 6 simulates them with groups of 10 and 40, normal data and no true difference, 100,000 pairs of samples at each SD ratio.

![Type I error of always-Student, always-Welch, Levene-decides and the full pre-testing habit by SD ratio, with Levene's power](FIG_06)
*Figure 6. Letting Levene choose lands between the two tests it chooses from: 9.74% at an SD ratio of 1.5 and 9.13% at 2, where Welch alone gives 5.07% and 5.06%. Below, Levene's test detects a ratio of 1.5 in 27.9% of samples.*

The procedure inherits Student's error wherever Levene's test cannot see the difference, and with ten observations in one group it rarely can. At a ratio of 1.5 Levene rejects in 27.9% of samples, at 2 in 64.6%, and only at 3 or more in over 90%. Delacre and colleagues estimated that about 120 subjects in a balanced design are needed for 80% power to detect a ratio of 1.5. <!-- L36 --> Where the larger group has the larger variance the procedure is conservative instead: 3.85% at half the SD and 2.96% at two thirds. Adding the normality test changes little at small ratios and costs more at large ones, 6.86% against 5.22% at a ratio of 4, because the rank test it switches to does not test equality of means, and on the samples the normality test sends it, it errs 23.1% there; what it does test belongs to a later part of this series.

The deeper problem is selection. Write the procedure's error as P(accept) × P(error | Student, accepted) + P(reject) × P(error | Welch, rejected). The conditional rates are not the unconditional ones: at a ratio of 2, Student's test errs 21.19% on the samples Levene passed, against 18.25% on all samples, because the samples whose variances look alike are those in which the small group's variance came out low, exactly where pooling understates the standard error most. With equal variances, Welch's test errs 9.77% on the 4.3% of samples Levene flags. A p-value reported after the pre-test carries neither test's error rate.

These results reproduce a literature. Zimmerman found that the Levene-then-t procedure fails to protect the significance level and usually makes things worse, more so with small samples and slight variance differences, and recommended the separate-variances test unconditionally whenever sizes differ. <!-- L12 --> Hayes and Cai found unconditional tests, Welch's among them, as good or better across 49 distributions, and Rasch, Kubinger and Moder concluded that pre-testing leaves the final error rates unknown. <!-- L13 --> <!-- L14 --> Rochon, Gondan and Kieser showed that a Shapiro–Wilk pre-test badly distorts the conditional error rates (10.8% to 17.0% for t-tests on exponential samples of 30 that passed), while the whole procedure stayed acceptable with equal sizes. <!-- L15 --> The claim is corrected on that evidence: pre-testing never did better than always using Welch, and with unequal sizes it did worse.

## Which test fits a 2 × 2 table?

**Both margins fixed.** Fisher's tea-tasting experiment, from *The Design of Experiments*, gave a lady eight cups of tea, told her that four had the milk poured first, and asked her to pick those four. <!-- L17 --> If she cannot tell, each of the C(8, 4) = 70 choices of four cups is equally likely, and the number of milk-first cups she picks correctly follows the **hypergeometric distribution**: 1, 16, 36, 16 and 1 ways to get 0 to 4 right (Figure 7). All eight right has probability 1/70 = 0.0143; three of four or better, 17/70 = 0.243. Both margins of her 2 × 2 table, four cups of each kind poured and four named, were fixed by the design, a rare case, so this distribution follows from the design alone and **Fisher's exact test**, which conditions on both margins, is exact here. <!-- L17 -->

![The tea-tasting design's null distribution: 1, 16, 36, 16 and 1 of 70 ways to pick 0 to 4 milk-first cups; P(all right) = 1/70](FIG_07)
*Figure 7. A 5% test can reject only when all eight cups are right, so its size is 1/70 = 1.43%: exact, and below 5% only because the outcomes are discrete.*

Not telling her the split changes the design. She may then name three cups as milk-first, the column total is no longer fixed, and with one doubtful cup her best outcome has probability 4/56 = 0.071 instead of 1/70. <!-- L17 -->

**One margin fixed.** Most 2 × 2 tables fix less. Yates's 1934 paper on small counts used Hellman's data on infants: 4 of 20 breast-fed infants and 1 of 22 bottle-fed ones had normal teeth. <!-- L20 --> If the groups' sizes were set and only the outcomes varied, this is a **comparative trial**, two independent binomial samples, one margin fixed; a **cross-sectional** sample fixes only the grand total. <!-- L18 --> Under independence the expected count of normal-toothed breast-fed infants is 5 × 20/42 = 2.38, below the 5 that the usual rule demands for the **chi-squared test**. Yates called that rule customary practice in 1934; Cochran, to whom it is often attributed, credited Fisher and called the number 5 arbitrary. <!-- L19 --> Figure 8 runs eight tests on this one table.

![The malocclusion table and its eight p-values, from 0.112 (mid-p) and 0.122 (Pearson) to 0.286 (Yates) and 0.287 (doubled Fisher)](FIG_08)
*Figure 8. One table, eight answers, from 0.112 to 0.287. R's and SciPy's default chi-squared test for this table is the Yates-corrected one, near the top.*

Pearson's chi-squared statistic is 2.386, p = 0.122. **Yates's correction** shrinks each deviation by half a unit so that the chi-squared p-value tracks the exact test's: 0.286 here. <!-- L20 --> Fisher's test has two two-sided versions in use: doubling the smaller tail, 0.287, and Irwin's rule, which adds every table no likelier than the one observed, 0.174 and the version R and SciPy compute. <!-- L21 --> The **mid-p** value counts only half of the observed table's probability, 0.112, an idea Lancaster proposed in 1961. <!-- L22 --> An **unconditional test** does not condition on the margin the design left free; it computes the p-value from the two-binomial design itself, taking the largest value over the unknown common success rate π, a **nuisance parameter**. Barnard's test does this with a z statistic, 0.143; Boschloo's uses Fisher's p-value as its statistic, 0.175.

The design that produced the table defines each test's real error rate. Figure 9 sums, for every π, the probability of every table each test rejects at 5%: all 483 tables with these group sizes, and all 451 for groups of 10 and 40.

![Exact size of five 2 × 2 tests against π for groups of 20 and 22 and of 10 and 40; Pearson reaches 9.1% in the second](FIG_09)
*Figure 9. With groups of 20 and 22, Fisher's test never exceeds 3.61% and Yates's corrected chi-squared 2.19%; Boschloo's reaches 4.63% and mid-p 5.14%. With 10 and 40, Pearson's test reaches 9.11% where the small group expects 0.28 successes, and Boschloo's dips below Fisher's at small π.*

Fisher's test is conservative here for two reasons: the outcomes are discrete, as in the tea test, and it conditions on a margin the design did not fix. Boschloo showed in 1970 that its unconditional size is often below half the nominal level in small samples, and that raising its conditional level turns it into an unconditional test with size at most α. <!-- L23 --> In this design Boschloo's test rejects every one of the 254 tables Fisher's rejects, plus 10 more, so it is at least as powerful against every alternative, and its size never passes 4.63%. That containment is guaranteed only against the doubled-tail version of Fisher's test, because SciPy's two-sided Boschloo p doubles the smaller one-sided value. <!-- L29 --> With groups of 10 and 40, Irwin's-rule Fisher rejects 4 tables that Boschloo's test does not, Boschloo's rejects 10 that Fisher's does not, and at π = 0.1 Boschloo's size is the smaller, 1.61% against 2.43%. Lydersen, Fagerland and Laake recommend unconditional tests or the mid-p version and conclude that the traditional Fisher's exact test should practically never be used. <!-- L24 --> Campbell, from each test's exact maximum size over every split of the sample sizes, recommends the chi-squared test with N − 1 in place of N whenever every expected count is at least 1, and Fisher's test by Irwin's rule otherwise. <!-- L25 --> Yates disagreed in 1984: he argued that conditioning on the margins is right even when the design did not fix them, and that the charge of conservatism comes from Neyman–Pearson theory and fixed nominal levels. <!-- L26 --> The disagreement is about inference, not arithmetic. On the arithmetic, the design that fixed both margins makes Fisher's test exact; with one margin fixed, Fisher's test leaves part of its 5% unspent, and an unconditional test or the mid-p value spends more of it.

## What does ANOVA's F compare?

For three or more independent groups, the classical **one-way analysis of variance (ANOVA)** compares two estimates of the common variance σ². R's PlantGrowth data, from Dobson, weigh 30 plants grown under a control and two treatments, ten each (Figure 10). <!-- L32 --> The **within-group mean square** pools the three groups' variances: a sum of squares of 10.492 on 27 degrees of freedom, 0.389, which estimates σ² whatever the means are. The **between-group mean square** measures how far the group means, 5.032, 4.661 and 5.526, sit from the grand mean, 5.073: 10 × Σ(ȳⱼ − ȳ)² = 3.766 on 2 degrees of freedom, 1.883, which estimates σ² only if the means are equal and more than σ² otherwise. Their ratio is **F** = 1.883/0.389 = 4.85 on 2 and 27 degrees of freedom, p = 0.0159.

![PlantGrowth's 30 dried weights in three groups with their means and the grand mean; between mean square 1.883, within 0.389, F 4.85](FIG_10)
*Figure 10. F is the between-group variance estimate divided by the within-group one. A ratio near 1 is what equal means predict.*

The F test pools, as Student's test does, and fails the same way. **Welch's ANOVA**, W, weights each group's mean by nⱼ/sⱼ², so a noisy group counts for less, and estimates its denominator degrees of freedom from the group variances. <!-- L30 --> For PlantGrowth W = 5.18 on 2 and 17.13 degrees of freedom, p = 0.0174: equal sizes and standard deviations within a factor of 1.8 of each other leave the two tests in agreement. With two groups F is exactly Student's t squared and W is Welch's: for the sleep data read as two groups, F = 3.4626 = 1.8608². Figure 11 simulates three groups of normal data with equal means, 100,000 times per design.

![Type I error of F, Welch's W and Brown–Forsythe's F* in four three-group designs; F reaches 16.1% under negative pairing](FIG_11)
*Figure 11. With groups of 10, 20 and 30 whose SDs run 3, 2, 1, the F test rejects 16.13% of the time; reversed, 2.04%. W stays between 4.90% and 5.25% in all four designs.*

Equal sizes no longer rescue the F test with three groups: at 20 each with SDs of 1, 2 and 3 it rejects 6.14%, where W gives 4.98%. Delacre and colleagues found the same pattern and recommend W by default, at a small cost in power when every assumption holds. <!-- L31 --> Brown and Forsythe's F*, a third option, weights each group's variance by 1 − nⱼ/N, and reached 5.96% to 6.01% under both pairings here. <!-- L37 --> The t-test and ANOVA as special cases of a regression with dummy variables come later in this series.

## The math

| Symbol | Meaning |
|---|---|
| nᵢ, x̄ᵢ, sᵢ² | size, mean and variance (divisor nᵢ − 1) of group i |
| σᵢ, τ² | population SD of group i; the variance of x̄₁ − x̄₂, σ₁²/n₁ + σ₂²/n₂ |
| d̄, s_d | mean and SD of the within-pair differences |
| m, n, s, N | the 2 × 2 table's row totals, first-column total and grand total |

**Paired and pooled.** The paired test is a one-sample t-test on the differences, and their variance is reduced by the correlation ρ between a unit's two results: <!-- L02 -->

$$
t_{\mathrm{paired}} = \frac{\bar d}{s_d/\sqrt{n}}, \qquad \operatorname{Var}(d) = \sigma_1^2 + \sigma_2^2 - 2\rho\,\sigma_1\sigma_2 \tag{1}
$$

For the sleep data, 1.58/(1.230/√10) = 4.06 on 9 degrees of freedom, and 3.201 + 4.009 − 2(0.795)(1.789)(2.002) = 1.513.

**Student and Welch.** <!-- L05 -->

$$
t_{S} = \frac{\bar x_1 - \bar x_2}{s_p\sqrt{1/n_1 + 1/n_2}}, \quad s_p^2 = \frac{(n_1 - 1)s_1^2 + (n_2 - 1)s_2^2}{n_1 + n_2 - 2}; \qquad t_{W} = \frac{\bar x_1 - \bar x_2}{\sqrt{s_1^2/n_1 + s_2^2/n_2}}, \quad \nu = \frac{\left(s_1^2/n_1 + s_2^2/n_2\right)^2}{\dfrac{(s_1^2/n_1)^2}{n_1 - 1} + \dfrac{(s_2^2/n_2)^2}{n_2 - 1}} \tag{2}
$$

Student's denominator estimates σ²(1/n₁ + 1/n₂) for a common σ², while the true variance of the numerator is τ². With n = 10 and 40 and the group of 10 at twice the SD, the pooled variance averages (9 × 4 + 39 × 1)/48 = 1.5625, so Student's denominator averages 1.5625 × 0.125 = 0.195 against τ² = 0.425: the statistic is about √2.18 = 1.48 times too spread out. For the sleep data read as two groups, ν = 17.78.

**The exact size, sketched.** For normal data, x̄₁ − x̄₂ ~ N(δ, τ²) independently of (s₁², s₂²), with (nᵢ − 1)sᵢ²/σᵢ² ~ χ²ₙᵢ₋₁. With SE the test's standard error and c its critical value, both functions of the sample variances,

$$
P(\text{reject}) = \mathbb{E}\left[\Phi\!\left(\frac{\delta - c\,\mathrm{SE}}{\tau}\right) + \Phi\!\left(\frac{-\delta - c\,\mathrm{SE}}{\tau}\right)\right] \tag{3}
$$

an expectation over two chi-squared variables, computed by Gauss–Laguerre quadrature. At δ = 0 it is the size; Student's 18.25% at n = 10 and 40 with a twofold SD is this integral.

**Fisher's test and its variants.** With both margins fixed, the top-left count a has the hypergeometric probability

$$
P(a) = \frac{\binom{m}{a}\binom{n}{s - a}}{\binom{N}{s}} \tag{4}
$$

and Irwin's two-sided p sums P over every table with P ≤ P(observed). <!-- L21 --> The mid-p value subtracts half the probability of the tables exactly as likely as the observed one. For the tea design, P(4) = 1/70 and P(3) = 16/70; for the malocclusion table, P(a = 4) = 0.1253 and Fisher's p is 0.1745, its mid-p 0.1745 − 0.1253/2 = 0.112.

**Unconditional tests.** For two binomial samples with common rate π, a table's probability is the product of two binomial probabilities, and Boschloo's p-value is <!-- L23 --> <!-- L29 -->

$$
p_{\mathrm{B}} = \max_{0 < \pi < 1} \; P_\pi\!\left(p_F(T) \le p_F(t_{\mathrm{obs}})\right) \tag{5}
$$

with p_F Fisher's one-sided p-value; SciPy reports twice the smaller of the two one-sided values. The maximum over π is what makes its size at most α.

**ANOVA.** With k groups, F = [Σ nⱼ(ȳⱼ − ȳ)²/(k − 1)] / [Σ(nⱼ − 1)sⱼ²/(N − k)]. Welch's W replaces the weights by wⱼ = nⱼ/sⱼ²: <!-- L30 -->

$$
W = \frac{\sum_j w_j(\bar y_j - \bar y_w)^2/(k - 1)}{1 + \frac{2(k - 2)}{k^2 - 1}\sum_j \frac{(1 - w_j/\sum w)^2}{n_j - 1}}, \qquad \nu_2 = \frac{k^2 - 1}{3\sum_j (1 - w_j/\sum w)^2/(n_j - 1)} \tag{6}
$$

where ȳ_w is the w-weighted mean. For PlantGrowth W = 5.18 with ν₂ = 17.13.

## Implementation

The paired analysis and the 2 × 2 tests in a dozen lines. Run as printed, it gives the worked example's numbers.

```python
import numpy as np
from scipy import stats

drug1 = np.array([0.7, -1.6, -0.2, -1.2, -0.1, 3.4, 3.7, 0.8, 0.0, 2.0])   # Student's ten patients (R's sleep):
drug2 = np.array([1.9, 0.8, 1.1, 0.1, -0.1, 4.4, 5.5, 1.6, 4.6, 3.4])      # extra hours on each drug, patient by patient

d = drug2 - drug1                                    # the design: every patient took both drugs
t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
print(f"paired by hand  t {t:.4f}, p {2 * stats.t.sf(abs(t), len(d) - 1):.6f}")
print(f"ttest_rel       p {stats.ttest_rel(drug2, drug1).pvalue:.6f}")
print(f"ttest_ind       p {stats.ttest_ind(drug2, drug1).pvalue:.6f}")                    # Student's: the default
print(f"ttest_ind Welch p {stats.ttest_ind(drug2, drug1, equal_var=False).pvalue:.6f}")

table = np.array([[4, 16], [1, 21]])     # Hellman: rows breast-fed (20), bottle-fed (22); columns normal teeth, malocclusion
print(f"chi2_contingency          p {stats.chi2_contingency(table).pvalue:.4f}")        # Yates-corrected: the default
print(f"chi2, correction=False    p {stats.chi2_contingency(table, correction=False).pvalue:.4f}")
print(f"fisher_exact              p {stats.fisher_exact(table).pvalue:.4f}")
print(f"boschloo_exact(table.T)   p {stats.boschloo_exact(table.T).pvalue:.4f}")       # columns must be the groups
```

It prints a paired t of 4.0621 with p = 0.002833, matched by `ttest_rel`; 0.079187 from `ttest_ind` and 0.079394 with `equal_var=False`; and 0.2857, 0.1224, 0.1745 and 0.1747 for the four 2 × 2 tests. The line that matters most is the subtraction: it pairs by position, so the two arrays must hold the same patients in the same order.

### Reading the library's output

When you name no test, the library chooses, and the libraries disagree. <!-- L06 --> <!-- L07 --> <!-- L27 --> <!-- L28 --> <!-- L38 -->

| Comparison | SciPy 1.18.1 | statsmodels 0.15.0 | R 4.5.2 |
|---|---|---|---|
| two groups | `ttest_ind`: Student's (`equal_var=True`) | `ttest_ind`: pooled | `t.test`: Welch's |
| k groups | `f_oneway`: classical F; `equal_var=False` gives W | `anova_oneway`: Welch's W | `oneway.test`: W; `anova(lm(...))`: F |
| 2 × 2 chi-squared | `chi2_contingency`: Yates-corrected, no warning | — | `chisq.test`: Yates-corrected; warns if any expected count is below 5 |
| Fisher, two-sided | `fisher_exact`: Irwin's rule | — | `fisher.test`: Irwin's rule |
| equal variances | `levene`: median-centred (Brown–Forsythe) | — | `var.test` (the F ratio); Levene's test is not in base R |

The same `ttest_ind(a, b)` call therefore runs Student's test in SciPy and statsmodels, and the same `t.test(a, b)` runs Welch's in R. Welch's ANOVA arrived in `f_oneway` with SciPy 1.16.0. <!-- L07 --> SciPy's `boschloo_exact` and `barnard_exact` treat each **column** as one binomial sample, so a table with the groups in rows must be transposed: without `.T` the call answers a different design, 0.1503 here. <!-- L29 --> And `barnard_exact` keeps the tables whose |Z| is at least the observed one with no tolerance for rounding, so a table tied with the observed one in exact arithmetic can drop out. In the malocclusion design, 71 of the 481 tables SciPy can test got a p-value different from the lab's, every one of them tied exactly with another table; the worst, 15 of 20 against 12 of 22, gets 0.1791, while its mirror image, 5 of 20 against 10 of 22, gets 0.2172. No 5% decision changed in this design. The lab's `choosing.py` computes every number in this post in five stages; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** testing normality and equal variances and then choosing the test. With groups of 10 and 40, Levene's test missed a 1.5-fold SD ratio 72% of the time, and letting it choose gave a 5% test an error rate of 9.74%. Choose from the design, and use Welch's test for two independent groups and Welch's ANOVA for more.

- **Analysing paired data as two groups.** The sleep data give p = 0.079 instead of 0.0028, because the between-patient spread enters the error. The reverse mistake, pairing rows that are not the same unit, invents a correlation.
- **Pairing by row order.** A long table sorted for display pairs the wrong patients and still returns a confident p-value; pair on an identifier, as R's `Pair()` makes explicit.
- **Trusting the default.** SciPy's `ttest_ind` is Student's test and both `chi2_contingency` and `chisq.test` apply Yates's correction, which in the malocclusion design gave a 5% test a size of at most 2.19%.
- **Switching to Mann–Whitney for unequal variances.** It is not a test of means, and many authors use it as a substitute that it is not; at an SD ratio of 2 with negative pairing, it erred 15.6% on the samples the normality test sent it. <!-- L34 -->
- **Fisher's test when the design fixed only the group sizes.** It conditions on a margin the design left free: with groups of 20 and 22 a 5% test never exceeded 3.61%, and Boschloo's test rejected every table it did and 10 more.
- **The chi-squared test with a tiny expected count in an unbalanced design.** With groups of 10 and 40 its size reached 9.11%. The usual rule of 5 is arbitrary; Campbell's measurements support the 'N − 1' version whenever every expected count is at least 1. <!-- L25 -->
- **Paired binary outcomes.** A 2 × 2 table of the same subjects before and after is a paired design; McNemar's test analyses it, and its mid-p version performed well in comparisons with the asymptotic and exact versions. <!-- L33 -->
- **Normal-theory results applied to skewed data.** Every exact rate here assumes normal data. Skewness combined with unequal sizes affects both t-tests, and the lab's quadrature does not cover it.

## Key takeaways

- The design picks the test: Student's ten patients took both drugs, so the paired t-test (p = 0.0028) is the analysis; the same numbers as two groups give p = 0.079, because pairing subtracts the shared patient part, 5.70, from the two drugs' combined variance of 7.21.
- Student's t-test errs in the direction of the pairing of sizes and variances: 18.25% when a group of 10 has twice the SD of a group of 40, and 0.52% when the larger group has it. Welch's test stays within 0.15 points of 5%, at a power cost of 0.08 points in a balanced design.
- Pre-testing does not help. Letting Levene's test choose gave 9.74% at an SD ratio of 1.5 where Welch's test alone gave 5.07%, the error rates after a pre-test's verdict are worse than either test's own, and the procedure never beat always using Welch.
- In a 2 × 2 table, the fixed margins decide. With both fixed by design, as in the tea test, Fisher's test is exact; with only the group sizes fixed, at 20 and 22, it never exceeded 3.61%, while Boschloo's unconditional test rejected every table Fisher's did and 10 more, at a size of at most 4.63%.
- ANOVA's F is a ratio of two variance estimates and fails like Student's test: 16.13% under negative pairing with three groups, where Welch's W gave 5.25%.

## Try it yourself

**E1, reproduce.** From the worked example's summary numbers alone, the mean difference 1.58, the SD of the differences 1.230 and the two drugs' SDs 1.789 and 2.002, compute the paired t and Welch's degrees of freedom for the unpaired test.

<details><summary>Answer</summary>

Paired: t = 1.58/(1.230/√10) = 1.58/0.3890 = 4.062 on 9 degrees of freedom. Welch: s₁²/n₁ = 3.2006/10 = 0.32006 and s₂²/n₂ = 4.0090/10 = 0.40090, so ν = (0.72096)²/((0.32006² + 0.40090²)/9) = 0.51978/0.029240 = 17.78, the value R and SciPy report.

</details>

**E3, predict.** Swap the design of Figure 4: give the group of **40** twice the SD of the group of 10. Before computing, predict whether Student's test becomes liberal or conservative and roughly how far, using the expected pooled variance, and what happens to Welch's test.

<details><summary>Answer</summary>

Conservative. The pooled variance now averages (39 × 4 + 9 × 1)/48 = 3.4375, so Student's denominator averages 3.4375 × 0.125 = 0.430 against a true variance of 4/40 + 1/10 = 0.200: the statistic is only √(0.200/0.430) = 0.68 times as spread out as it should be, which predicts a size of about 2Φ(−2.01/0.68) = 0.3%. The exact size is 0.52%, the mirror of the 10-against-40 design at half the SD; Welch's is 5.01%. The lab's `twosample` stage with `--n1 40 --n2 10 --ratio 2` prints both.

</details>

The lab carries the full ladder, from reproducing these numbers to diagnosing a paired analysis that returns p = 0.000007 on the same data, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E4 exercises with answers, and cleanup.
- [`choosing.py`](LAB_02) — the five stages: example, twosample, pretest, tables and anova.
- [`student1908_sleep.csv`](LAB_03) — Student's ten patients on two drugs (public domain), with provenance; put it in a `data` folder.
- [`plant_growth.csv`](LAB_04) — R's PlantGrowth weights (part of R, GPL-2 or GPL-3), with provenance; put it in a `data` folder.
- [`requirements.txt`](LAB_05) — the pinned NumPy, SciPy, statsmodels and pandas versions.
- [`captures.json`](LAB_06) — the author's full run, machine-readable, with the private cross-check against R.
- [`captures-quick.json`](LAB_07) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_08) — the author's full run as printed.
- [`notebook.ipynb`](LAB_09) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-choosing-a-statistical-test.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. Student. "The probable error of a mean." *Biometrika* 6(1): 1–25, 1908. https://doi.org/10.1093/biomet/6.1.1
2. A. R. Cushny and A. R. Peebles. "The action of optical isomers: II. Hyoscines." *Journal of Physiology* 32(5–6): 501–510, 1905. https://doi.org/10.1113/jphysiol.1905.sp001097
3. S. Senn and W. Richardson. "The first t-test." *Statistics in Medicine* 13(8): 785–803, 1994. https://doi.org/10.1002/sim.4780130802
4. B. L. Welch. "The generalization of 'Student's' problem when several different population variances are involved." *Biometrika* 34(1–2): 28–35, 1947. https://doi.org/10.1093/biomet/34.1-2.28
5. F. E. Satterthwaite. "An approximate distribution of estimates of variance components." *Biometrics Bulletin* 2(6): 110–114, 1946. https://doi.org/10.2307/3002019
6. B. L. Welch. "On the comparison of several mean values: an alternative approach." *Biometrika* 38(3–4): 330–336, 1951. https://doi.org/10.1093/biomet/38.3-4.330
7. M. Delacre, D. Lakens and C. Leys. "Why psychologists should by default use Welch's t-test instead of Student's t-test." *International Review of Social Psychology* 30(1): 92–101, 2017. https://doi.org/10.5334/irsp.82
8. M. Delacre, D. Lakens and C. Leys. "Correction: Why psychologists should by default use Welch's t-test instead of Student's t-test." *International Review of Social Psychology* 35(1): 21, 2022. https://doi.org/10.5334/irsp.661
9. M. Delacre, C. Leys, Y. L. Mora and D. Lakens. "Taking parametric assumptions seriously: arguments for the use of Welch's F-test instead of the classical F-test in one-way ANOVA." *International Review of Social Psychology* 32(1): 13, 2019. https://doi.org/10.5334/irsp.198
10. G. E. P. Box. "Some theorems on quadratic forms applied in the study of analysis of variance problems, I. Effect of inequality of variance in the one-way classification." *The Annals of Mathematical Statistics* 25(2): 290–302, 1954. https://doi.org/10.1214/aoms/1177728786
11. D. W. Zimmerman. "A note on preliminary tests of equality of variances." *British Journal of Mathematical and Statistical Psychology* 57(1): 173–181, 2004. https://doi.org/10.1348/000711004849222
12. A. F. Hayes and L. Cai. "Further evaluating the conditional decision rule for comparing two independent means." *British Journal of Mathematical and Statistical Psychology* 60(2): 217–244, 2007. https://doi.org/10.1348/000711005X62576
13. D. Rasch, K. D. Kubinger and K. Moder. "The two-sample t test: pre-testing its assumptions does not pay off." *Statistical Papers* 52(1): 219–231, 2011. https://doi.org/10.1007/s00362-009-0224-x
14. J. Rochon, M. Gondan and M. Kieser. "To test or not to test: preliminary assessment of normality when comparing two independent samples." *BMC Medical Research Methodology* 12: 81, 2012. https://doi.org/10.1186/1471-2288-12-81
15. M. B. Brown and A. B. Forsythe. "Robust tests for the equality of variances." *Journal of the American Statistical Association* 69(346): 364–367, 1974. https://doi.org/10.1080/01621459.1974.10482955
16. M. B. Brown and A. B. Forsythe. "The small sample behavior of some statistics which test the equality of several means." *Technometrics* 16(1): 129–132, 1974. https://doi.org/10.1080/00401706.1974.10489158
17. J. L. Gastwirth, Y. R. Gel and W. Miao. "The impact of Levene's test of equality of variances on statistical theory and practice." *Statistical Science* 24(3): 343–360, 2009. https://doi.org/10.1214/09-STS301
18. S. S. Shapiro and M. B. Wilk. "An analysis of variance test for normality (complete samples)." *Biometrika* 52(3–4): 591–611, 1965. https://doi.org/10.1093/biomet/52.3-4.591
19. R. A. Fisher. *The Design of Experiments.* Edinburgh: Oliver and Boyd, 1935.
20. F. Yates. "Tests of significance for 2 × 2 contingency tables." *Journal of the Royal Statistical Society, Series A* 147(3): 426–463, 1984. https://doi.org/10.2307/2981577
21. F. Yates. "Contingency tables involving small numbers and the χ² test." *Supplement to the Journal of the Royal Statistical Society* 1(2): 217–235, 1934. https://doi.org/10.2307/2983604
22. M. Hellman. "A study of some etiological factors of malocclusion." *Dental Cosmos* 56: 1017–1032, 1914 (as printed in source 20).
23. I. Campbell. "Chi-squared and Fisher–Irwin tests of two-by-two tables with small sample recommendations." *Statistics in Medicine* 26(19): 3661–3675, 2007. https://doi.org/10.1002/sim.2832
24. S. Lydersen, M. W. Fagerland and P. Laake. "Recommended tests for association in 2 × 2 tables." *Statistics in Medicine* 28(7): 1159–1175, 2009. https://doi.org/10.1002/sim.3531
25. R. D. Boschloo. "Raised conditional level of significance for the 2 × 2-table when testing the equality of two probabilities." *Statistica Neerlandica* 24(1): 1–9, 1970. https://doi.org/10.1111/j.1467-9574.1970.tb00104.x
26. G. A. Barnard. "Significance tests for 2 × 2 tables." *Biometrika* 34(1–2): 123–138, 1947. https://doi.org/10.1093/biomet/34.1-2.123
27. H. O. Lancaster. "Significance tests in discrete distributions." *Journal of the American Statistical Association* 56(294): 223–234, 1961. https://doi.org/10.1080/01621459.1961.10482105
28. W. G. Cochran. "Some methods for strengthening the common χ² tests." *Biometrics* 10(4): 417–451, 1954. https://doi.org/10.2307/3001616
29. M. W. Fagerland, S. Lydersen and P. Laake. "The McNemar test for binary matched-pairs data: mid-p and asymptotic are better than exact conditional." *BMC Medical Research Methodology* 13: 91, 2013. https://doi.org/10.1186/1471-2288-13-91
30. G. D. Ruxton. "The unequal variance t-test is an underused alternative to Student's t-test and the Mann–Whitney U test." *Behavioral Ecology* 17(4): 688–690, 2006. https://doi.org/10.1093/beheco/ark016
31. A. J. Dobson. *An Introduction to Statistical Modelling.* Chapman and Hall, 1983. https://doi.org/10.1007/978-1-4899-3174-0
32. R Core Team. R 4.5.2 documentation: `sleep`, `PlantGrowth`, `t.test`, `oneway.test`, `chisq.test`, `fisher.test`, and the NEWS for R 4.0.0 and 4.4.0. https://stat.ethz.ch/R-manual/R-patched/library/stats/html/t.test.html (accessed 2026-11-01)
33. SciPy 1.18.1 documentation, `scipy.stats`. https://docs.scipy.org/doc/scipy/reference/stats.html (accessed 2026-11-01)
34. statsmodels 0.15.0 documentation, `statsmodels.stats.oneway.anova_oneway`. https://www.statsmodels.org/stable/generated/statsmodels.stats.oneway.anova_oneway.html (accessed 2026-11-01)
