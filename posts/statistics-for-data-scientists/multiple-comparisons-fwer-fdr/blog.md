---
title: "Multiple Comparisons: FWER, FDR, and Tests You Didn't Count"
slug: multiple-comparisons-fwer-fdr
date: 2026-11-18
updated: 2026-11-18
summary: "Bonferroni and Holm cap the chance of any false finding; Benjamini-Hochberg caps the expected false share of a list, and only when tests depend nicely."
tags: [data-science, multiple-comparisons, false-discovery-rate, hypothesis-testing, p-hacking, statistics]
category: data-science
series: statistics-for-data-scientists
series_position: 9
tier: L3
difficulty: advanced
prerequisites: ["type I error and p-values", "statistical power", "Monte Carlo standard error"]
reading_minutes: 26
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/multiple-comparisons-fwer-fdr"
---

![The 200 smallest of 3,170 gene p-values on a log scale against two 5% rules: Benjamini–Hochberg's rising line keeps 94 of them, Bonferroni's flat line keeps 2](COVER)

> [!NOTE]
> **Insights** — Bonferroni and Holm control the family-wise error rate, the chance of even one false finding; Benjamini–Hochberg controls the false discovery rate, the expected false share of a list, and only under a condition on how the tests depend on each other. <!-- L01 --> On 3,170 breast-cancer genes the same 5% buys 2, 94 or 162 discoveries, depending on which promise you pick. <!-- L28 --> The false discovery rate is an average over repeated studies: with every pair of tests correlated at 0.5, about one non-empty Benjamini–Hochberg list in five was more than 10% false in our simulation. <!-- L29 --> And the tests nobody counted, the forks inside a single "planned" analysis, can push a 5% test to a 61% false-positive rate. <!-- L31 -->

**Level:** advanced · **You need:** type I error, p-values and power (*p-Values and Power: How Wrong Can a Significant Result Be?*), Monte Carlo standard errors (*The Sampling Distribution*) · **Time:** ~26 min

**On this page:** [the worked example](#worked-example) · [correlated tests](#does-benjaminihochberg-keep-5-when-the-tests-are-correlated) · [what FDR promises](#what-does-fdr-5-promise-about-the-one-list-you-have) · [uncounted tests](#how-many-tests-did-a-one-analysis-study-run) · [the code](#implementation) · [mistakes](#limitations-and-common-mistakes)

## Why this matters

Hedenfalk and colleagues compared breast tumours from carriers of BRCA1 and BRCA2 mutations, gene by gene. <!-- L27 --> Storey and Tibshirani reanalysed 3,170 of those genes with one two-sample test each, seven BRCA1 arrays against eight BRCA2 arrays. <!-- L10 --> At p ≤ 0.05, 606 genes pass. About two-thirds of all genes look null, and null p-values are uniform, so roughly 107 of the 606 should be there by chance. <!-- L33 -->

Figure 1 shows where that estimate comes from: the flat floor of the histogram is what null genes produce, and the spike next to zero is the signal sitting on top of it.

![Histogram of 3,170 p-values in bins of 0.05: 606 in the first bin, the rest near a flat floor of about 107 per bin](FIG_01)
*Figure 1. The flat floor is what null p-values produce; its height, about 107 genes per bin, is π0 × 3,170 × 0.05 with π0 = 0.676.*

So a follow-up lab handed the 606 genes would spend roughly a sixth of its effort on noise, and nothing in the list says which sixth. The corrections that follow exist to change that number. They do it by promising different things, and the difference decides whether you report 2 genes, 94 or 162.

## The problem

Run m tests. An unknown m0 of the null hypotheses are true and m1 = m − m0 are false. A procedure rejects R of them, and V of those rejections are false discoveries:

| | not rejected | rejected | total |
|---|---|---|---|
| true null | U | V | m0 |
| false null | T | S | m1 |
| total | m − R | R | m |

You observe m and R. You never observe V, which is the whole difficulty. Two summaries of V matter.

The **family-wise error rate** (FWER) is the probability of at least one false discovery, P(V ≥ 1). It is the error a claim needs when every rejection stands on its own: a trial endpoint, a published "this gene is involved". With one test it is the type I error rate from Part 5, *p-Values and Power: How Wrong Can a Significant Result Be?*. With many tests it grows fast. Fourteen independent tests at α = 0.05 with every null true give 1 − 0.95¹⁴ = 0.512; 3,170 give a number indistinguishable from 1.

The **false discovery proportion** (FDP) is V divided by R in one study, set to 0 when nothing is rejected. The **false discovery rate** (FDR) is its expectation over repeated studies, E[V / max(R, 1)]. It is the error a list needs when the list feeds more work and a few wrong entries cost only a wasted follow-up. Benjamini and Hochberg defined it, and showed that it equals the FWER when every null is true and is smaller otherwise. <!-- L02 -->

The constraint that makes this hard is the trade-off. The obvious FWER fix, testing each hypothesis at α/m, puts the Hedenfalk threshold at 0.05/3,170 = 1.58 × 10⁻⁵, and only two genes clear it. The question the rest of the post answers is which error your claim needs, which rule controls it under which condition, and how many tests you actually ran.

## Worked example

Sort the 3,170 p-values from smallest to largest and call them p₍₁₎ ≤ … ≤ p₍ₘ₎. Every rule below compares p₍ᵢ₎ with a threshold that depends on its rank i. These are the first eight ranks with α = 0.05:

| rank i | p₍ᵢ₎ | Holm: α/(m − i + 1) | BH: iα/m | BY: iα/(m·H_m) |
|---|---|---|---|---|
| 1 | 3.1546 × 10⁻⁶ | 1.5773 × 10⁻⁵ | 1.5773 × 10⁻⁵ | 1.8258 × 10⁻⁶ |
| 2 | 1.5773 × 10⁻⁵ | 1.5778 × 10⁻⁵ | 3.1546 × 10⁻⁵ | 3.6516 × 10⁻⁶ |
| 3 | 2.2082 × 10⁻⁵ | 1.5783 × 10⁻⁵ | 4.7319 × 10⁻⁵ | 5.4774 × 10⁻⁶ |
| 4 | 3.4700 × 10⁻⁵ | 1.5788 × 10⁻⁵ | 6.3091 × 10⁻⁵ | 7.3032 × 10⁻⁶ |
| 8 | 5.0473 × 10⁻⁵ | 1.5808 × 10⁻⁵ | 1.2618 × 10⁻⁴ | 1.4606 × 10⁻⁵ |

**Bonferroni** rejects every p-value at or below α/m = 1.5773 × 10⁻⁵: ranks 1 and 2. Rank 2 is a tie to the last bit. These p-values come from 317,000 pooled permutation statistics, so each is a count over 317,000, and p₍₂₎ = 5/317,000 = 1/63,400 = 0.05/3,170 exactly. A rule written with a strict inequality would reject one gene.

**Holm** walks up from the smallest and compares p₍ᵢ₎ with α/(m − i + 1), stopping at the first failure. Rank 1 passes, rank 2 passes (1.5773 × 10⁻⁵ ≤ 1.5778 × 10⁻⁵) and rank 3 fails (2.2082 × 10⁻⁵ > 1.5783 × 10⁻⁵). Two genes. Holm is a **step-down procedure**: it starts with the strictest threshold and stops at the first p-value that misses its own.

**Benjamini–Hochberg** (BH) is a **step-up procedure**. It finds the largest k with p₍ₖ₎ ≤ kα/m and rejects ranks 1 to k, including any rank below k that missed its own line. Here k = 94: p₍₉₄₎ = 1.4700 × 10⁻³ ≤ 94 × 0.05/3,170 = 1.4826 × 10⁻³, and no larger rank gets back under its line. Ninety-four genes. Figure 2 draws every rule as a line through the sorted p-values.

![Sorted p-values for ranks 1 to 300 on a log axis, with the Bonferroni, Holm, BH, BY and Storey boundary lines and their crossings at 2, 94 and 162](FIG_02)
*Figure 2. Each rule is a line. BH rejects up to the last p-value under its line (rank 94); Storey's line sits higher by 1/π0 and reaches rank 162; Bonferroni and Holm stop at rank 2; BY never catches the smallest p-value.*

**Benjamini–Yekutieli** (BY) runs BH at α/H_m, where H_m = 1 + 1/2 + … + 1/m is the harmonic number. For m = 3,170, H_m = 8.638860, so the level falls to 0.005788. The smallest p-value, 3.1546 × 10⁻⁶, misses its BY threshold of 1.8258 × 10⁻⁶. Zero genes.

**Storey's q-values** first estimate **π0**, the share of true nulls, then run BH as if only π0·m tests were null. The estimate counts how many p-values sit above a threshold λ, where nulls dominate: a share at or above λ, divided by 1 − λ, estimates π0. <!-- L09 --> Figure 3 shows that ratio across λ for the Hedenfalk data and the smoothing spline every recipe uses to read off one value.

![π0(λ) against λ from 0 to 1 for the Hedenfalk p-values, with three smoothing-spline recipes ending at 0.6758, 0.6699 and 0.6635](FIG_03)
*Figure 3. The same p-values give π0 = 0.6758 with the paper's recipe, 0.6699 with qvalue's current defaults and 0.6635 with its 1.x defaults; the third decimal depends on the tuning grid.*

With qvalue's current defaults π0 = 0.6699, and the **q-value** of a gene, the smallest FDR level at which it would be called significant, is π0 times its BH-adjusted p-value. <!-- L14 --> An **adjusted p-value** is the smallest level at which the procedure would reject that test, which is what software returns. So q ≤ 0.05 is BH run at 0.05/0.6699 = 0.0746, and it finds 162 genes. The counts side by side:

| Rule | Error it controls | Condition | Genes at 5% |
|---|---|---|---|
| Bonferroni | FWER | none | 2 |
| Holm | FWER | none | 2 |
| Benjamini–Hochberg | FDR | independence or positive dependence | 94 |
| Benjamini–Yekutieli | FDR | none | 0 |
| Storey q-value | FDR (estimated π0) | many tests, weak dependence | 162 |

**Reconciling the counts.** The by-hand adjusted p-values match statsmodels 0.15.0 (`multipletests` with `bonferroni`, `holm`, `fdr_bh`, `fdr_by`) and SciPy 1.18.1 (`false_discovery_control` with `bh`, `by`) to within 2.2 × 10⁻¹⁶. <!-- L28 --> Against the paper, the q-values reproduce. With Storey and Tibshirani's own recipe the lab counts 80, 159 and 231 genes at q ≤ 0.03, 0.05 and 0.07, against their published 80, 160 and 231. <!-- L11 --> The genes they name land where they put them: the 8th has p = 5.05 × 10⁻⁵ and q = 0.013 in both. <!-- L12 --> Their BH counts do not reproduce: they report 21, 88 and 153 at the same cutoffs, and these p-values give 24, 94 and 157. The package ships the p-values with the statistics and permutation draws behind them, but they come from a fresh permutation run and are not byte-identical to the paper's (the 47th gene has p = 4.86 × 10⁻⁴ here and 4.79 × 10⁻⁴ there), and neither m = 3,226 nor a step-down variant recovers all three numbers, so this stays an open discrepancy. <!-- L16 -->

## Intuition

The two error rates answer different questions about the same list. The FWER asks how likely the list is to contain any wrong entry at all. The FDR asks what share of the list will be wrong on average, over every study you might run.

A factory makes the distinction concrete. FWER control is a promise that a shipment contains no defective part, with probability 0.95. FDR control is a promise about the average defect rate across shipments. The analogy breaks in one place, and that place is the rest of this post: a factory can open the box and count defects, while a statistician never sees V. The average is all the promise covers, and nothing guarantees that this shipment looks like the average.

BH's line has a simple reading. At a threshold t, about m0·t null p-values fall below it, and at most m·t. R(t) is the number that actually fall below it. So m·t/R(t) is a conservative estimate of the false share at that threshold. BH picks the largest p-value threshold where that estimate is at most q. Storey's version replaces m by π0·m, which is why its line sits higher by 1/π0.

The step-up direction matters. Holm compares each p-value with its own threshold and stops at the first miss. BH asks only where the sorted p-values last cross the line. A run of slightly-too-large p-values in the middle cannot stop BH if a later rank gets back under its threshold. Holm buys strong control of the FWER under any dependence, and it rejects everything Bonferroni rejects. <!-- L01 --> Hochberg's step-up version of Holm needs independence or non-negative association, the same kind of condition BH needs. <!-- L18 -->

Figure 4 turns this into a decision. Start from the claim you will make, then pick the rule from what you know about the dependence.

![Decision flowchart: claims that stand alone lead to Holm; lists lead to BH, BY or Storey by dependence; post-hoc analyses lead to counting forks](FIG_04)
*Figure 4. Choose the error rate from the claim, then the rule from the dependence; a data-dependent analysis needs its forks counted before any rule applies.*

## Does Benjamini–Hochberg keep 5% when the tests are correlated?

Genes in a pathway move together, so their test statistics are correlated, and BH's proof under independence no longer covers them. Benjamini and Yekutieli extended it to **positive regression dependence on the subset of true nulls** (PRDS): roughly, when a null test statistic gets larger, the others tend to get larger too. PRDS covers one-sided tests of normal statistics with non-negative correlations, and it does not cover two-sided tests. <!-- L04 --> Storey and Tibshirani's q-values carry a different condition: many tests, and dependence whose effect fades as the number of tests grows. <!-- L13 -->

The lab measures what each rule delivers as correlation rises. Each simulated study has 3,170 one-sided z-tests, two-thirds of them null, and the 1,046 non-nulls shifted by 1.6 standard deviations. That shift makes BH average 91 discoveries at q = 0.05 under independence, close to the 94 on the real data. <!-- L29 --> Every pair of tests shares a correlation ρ, and each point is 20,000 studies. Figure 5 has the result.

![Line chart of false discovery rate against correlation 0 to 0.5: Storey rises from 0.050 to 0.272, BH falls from 0.0335 to 0.026, BY stays near 0.003](FIG_05)
*Figure 5. BH stays under its promise q·m0/m as correlation rises. Storey's FDR nearly doubles at ρ = 0.1, to 0.092, and reaches 0.272 at ρ = 0.5. Bars are ±2 MCSE.*

BH holds. Its FDR is 0.0335 ± 0.0001 under independence, exactly q·m0/m, the value the theory gives for continuous independent tests. <!-- L03 --> It drifts down to 0.0260 ± 0.0005 at ρ = 0.5, inside the guarantee, as PRDS says it should. <!-- L29 -->

Storey's adaptive rule does not. An **adaptive procedure** estimates π0 from the data and spends the gain on discoveries, and its FDR is 0.0500 ± 0.0001 at independence, right on target. At ρ = 0.1 it is 0.0923 ± 0.0009, and at ρ = 0.5 it is 0.2723 ± 0.0022, more than five times the target. <!-- L29 --> Blanchard and Roquain found the same failure for Storey's estimator with λ = ½, sometimes by a large factor. <!-- L08 --> The mechanism is in the estimate. A shared shift moves every null p-value in the same direction. When it moves them down, few p-values sit above λ, π0 collapses (its 5th percentile is 0.167 already at ρ = 0.1), the q-values shrink, and the list fills with nulls.

One more column in the lab output deserves a look: BH's FWER under independence is 0.9335 ± 0.0018. <!-- L29 --> Controlling the false share at 0.05 still means a false gene in almost every list.

## What does "FDR 5%" promise about the one list you have?

The most common reading of an FDR result is that about one in twenty of the discoveries in hand are false. That is the claim this post corrects. The FDR is an expectation over studies you did not run. Your list has one realised FDP, and the guarantee says nothing directly about it.

Under independence the two are close, because the FDP concentrates around its mean. In 20,000 independent studies BH's FDP exceeded 10% in only 0.18% of them. <!-- L29 --> Correlation breaks that. At ρ = 0.5 the FDR is still 2.60%, yet 8.20% of studies have an FDP above 10%. <!-- L29 --> BH also finds nothing at all in 58.7% of those studies, and those empty lists count as FDP = 0. <!-- L29 --> Among studies that produced a list, 19.8% of the lists were more than 10% false. <!-- L29 --> Figure 6 shows both distributions on the same axis.

![Two histograms of BH's false discovery proportion: tightly spread below 0.1 at correlation 0, a spike at 0 and a long tail past 0.3 at correlation 0.5](FIG_06)
*Figure 6. Same FDR, different promise. With correlated tests most studies are clean or empty and a few are very dirty, and the average hides which kind you have.*

Roquain's survey states the general fact: controlling the FDR does not stop the FDP from varying widely, and the FDR is a meaningful summary only when the FDP concentrates near its mean, which fails under equicorrelated Gaussian dependence. <!-- L07 --> For the 94 Hedenfalk genes, then, "FDR 5%" says the procedure keeps the false share at about 3.4% on average across repetitions, if PRDS holds. <!-- L03 --> It does not say that four or five of these 94 genes are false. If you need a statement about this list, control the tail of the FDP instead, a bound on P(FDP > γ); procedures for that exist, at a cost in power. <!-- L07 -->

## When does Benjamini–Hochberg fail, and what does Benjamini–Yekutieli cost?

BY's correction holds under any dependence at all: run BH at q/H_m and the FDR stays at or below q. <!-- L05 --> The correction is not slack. A specific joint law of the null p-values makes BH's FDR exactly q times H_m, so no smaller factor works in general. <!-- L06 --> Figure 7 shows that law for m = 5.

![Five rows of events: in event Ek, exactly k null p-values fall in the k-th slot of width α/m, which happens with probability α/k and makes BH reject k](FIG_07)
*Figure 7. Each slot catches BH once. The events are disjoint and their probabilities α/k add up to α·H_m, while every p-value stays exactly uniform.*

All m hypotheses are null. With probability α/k, exactly k p-values land in the k-th slot of width α/m and the rest land above α. Each event triggers BH to reject k tests, all false, so the FDR is α(1 + 1/2 + … + 1/m). At m = 3,170 that is 0.4319, and the lab's 20,000-study check gives 0.4300 ± 0.0035. <!-- L30 --> A Kolmogorov–Smirnov test on one test's p-value across the 20,000 studies gives p = 0.865, so each p-value really is uniform. <!-- L30 --> Under the same law Bonferroni and Holm hold at 0.0499 ± 0.0015 and BY at 0.0058 ± 0.0005. Even at m = 10 the worst case is 14.6%. <!-- L30 -->

Guo and Rao call the construction artificial, and Roquain calls its dependence unrealistic: it exists to show the bound is tight, not to describe data. <!-- L06 --> The price of insuring against it is real, though. On the Hedenfalk genes BY's factor of 8.64 takes the discoveries from 94 to zero. <!-- L28 --> Use BY when you cannot rule out dependence you have no model for, such as statistics built from overlapping, reused samples, or signs that can go either way. For one-sided tests with positive correlation, PRDS covers BH and the factor is wasted.

## How many tests did a one-analysis study run?

Every rule so far needs m, the number of tests, and assumes you know it. Simmons, Nelson and Simonsohn showed how a researcher who runs one analysis per study can still run dozens. Their simulation gave four ordinary choices to a study with no effect anywhere: test either of two correlated outcomes or their mean, test at 20 per cell and again after 10 more, add gender as a covariate or an interaction, and drop one of three conditions or test a trend across all three. <!-- L22 --> Each choice alone took a nominal 5% to between 7.7% and 12.6%, and all four together reached 60.7%. <!-- L21 -->

Count the forks, as Figure 8 does: three outcomes, two stopping points, four condition comparisons and four model tests make 96 p-values behind the one that gets reported.

![Four stacked layers of choices with their counts: outcome times 3, stopping time times 2, conditions times 4, model times 4, giving 96 tests](FIG_08)
*Figure 8. One reported result, 96 tests underneath. A sample is a false positive if any of the 96 reaches p below .05.*

The lab reruns their design with 100,000 null samples and two readings of one detail they did not specify: whether the interaction model codes the condition as 0/1 or as ±½. Figure 9 sets both against their table.

![Dot plot of seven scenarios comparing the paper's false-positive rates with ours: close on every row, 61.4% against 60.7% for all four choices](FIG_09)
*Figure 9. Our dummy-coded rerun lands within about one point of every row of their Table 1; effect coding gives 58.4% on the last row, too low to match.*

With 0/1 coding the four-way rate is 61.4% ± 0.15%, and every single choice lands within half a point of the paper. <!-- L31 --> With ±½ coding it is 58.4%, 2.3 points below their 60.7%. <!-- L31 --> Their 15,000 samples and our 100,000 put the standard error of that gap at 0.43 points, so ±½ coding misses by about five standard errors while 0/1 coding sits 1.7 above. <!-- L31 --> So the published numbers are consistent with 0/1 coding and not with ±½. The reproduction had a fork of its own, invisible in the paper's text and worth three points of false-positive rate.

Gelman and Loken pushed the point further: the forks matter even when a researcher never tries a second analysis, because the one analysis chosen depends on the data that came in. <!-- L25 --> No correction can fix this after the fact, because a correction needs m and the forks hide m. The fixes come before the data: write the analysis down, report every test that was run, or correct for the full set of forks you could have taken.

## Why does a screened regression look significant?

Screening variables is a fork with a known size. Freedman showed that with regressors unrelated to the outcome, dropping the ones with small t statistics and refitting keeps R² high and makes the overall F test look highly significant. <!-- L23 --> The setting usually reproduced is 100 observations and 50 pure-noise regressors. <!-- L24 --> The lab runs it 20,000 times: fit all 50, keep those with p below 0.25, refit. The regression is used only as a fitting routine here; later in this series it gets its own post.

![Two histograms of the overall F test's p-value on a log axis: spread near 1 for the full fit, concentrated between 10^-5 and 10^-2 after screening](FIG_10)
*Figure 10. Screening at 0.25 moves the F test's p-value from near-uniform to mostly below 0.01; the refitted regression calls noise significant in 94.8% of datasets.*

In the first pass everything behaves. The mean R² is 0.505, the value 50/99 that noise produces, and the F test rejects in 5.14% ± 0.16% of datasets. <!-- L32 --> The screen keeps 12.5 regressors on average. After refitting on those, the F test rejects in 94.8% ± 0.16% of datasets and in 51.6% at p below 0.001. <!-- L32 --> The number of individually significant slopes rises from 2.5 to 5.6. <!-- L32 --> Figure 10 shows the shift. The screen chose the regressors that happen to line up with y in this sample, and the second F test treats them as if they had been chosen in advance. The fix is the same as for the forks: select on one half of the data and test on the other, or count the screen as part of the test.

## The math

Write $\mathcal{H}_0$ for the set of true nulls, $m_0 = |\mathcal{H}_0|$, and $p_i$ for test $i$'s p-value, uniform on $(0,1)$ when its null is true. $R$ is the number of rejections and $V$ the number of false ones.

**Bonferroni.** A false discovery needs some true null to clear $\alpha/m$, so by the union bound

$$
\Pr(V \ge 1) \le \sum_{i \in \mathcal{H}_0} \Pr(p_i \le \alpha/m) = \frac{m_0\,\alpha}{m} \le \alpha. \tag{1}
$$

The chance of any false discovery is at most the sum of the individual chances, whatever the dependence.

**Holm (sketch).** Order the p-values and let $j$ be the rank of the smallest true-null p-value. At most $m - m_0$ false nulls sit below it, so $j \le m - m_0 + 1$, and Holm reaches it with threshold $\alpha/(m - j + 1) \le \alpha/m_0$. So a false rejection needs $\min_{i \in \mathcal{H}_0} p_i \le \alpha/m_0$, which has probability at most $\alpha$ by equation (1) applied to the $m_0$ nulls.

**Benjamini–Hochberg (sketch, independence).** Write the FDR as a sum over true nulls:

$$
\mathrm{FDR} = \sum_{i \in \mathcal{H}_0} \mathbb{E}\!\left[\frac{\mathbf{1}\{i \text{ rejected}\}}{\max(R, 1)}\right]. \tag{2}
$$

Let $R_i$ be the number of rejections BH would make if $p_i$ were set to 0; it depends only on the other p-values. Test $i$ is rejected exactly when $p_i \le qR_i/m$, and then $R = R_i$. Conditioning on the other p-values, which are independent of the uniform $p_i$, each term is $\mathbb{E}[(qR_i/m)/R_i] = q/m$. Summing over the $m_0$ true nulls gives

$$
\mathrm{FDR} = \frac{m_0}{m}\, q. \tag{3}
$$

Equation (3) is the 0.0335 the lab measured, with $m_0/m = 2{,}124/3{,}170$. Under PRDS the conditional step becomes an inequality and the FDR is at most $q\,m_0/m$; under arbitrary dependence the best general bound is $q\,(m_0/m)\,H_m$, which is why BY divides $q$ by $H_m = \sum_{i=1}^m 1/i \approx \ln m + 0.577$.

**Storey's estimator.** For a threshold $\lambda$,

$$
\hat\pi_0(\lambda) = \frac{\#\{p_i \ge \lambda\}}{m\,(1-\lambda)}, \qquad q_{(i)} = \min_{j \ge i} \frac{\hat\pi_0\, m\, p_{(j)}}{j}. \tag{4}
$$

The first part counts p-values above $\lambda$, where nulls dominate, and scales by the width $1-\lambda$ of that region. Non-nulls that land above $\lambda$ bias it upward, which is safe. Few p-values near $\lambda \to 1$ make it noisy, which is why every recipe smooths it before reading off one value. The second part is the BH-adjusted p-value times $\hat\pi_0$: the running minimum from the largest p-value down is the step-up rule, written per test.

## Implementation

The functions return adjusted p-values; reject test $i$ at level $a$ when its adjusted value is at most $a$. The full lab adds qvalue's spline for $\hat\pi_0$; this version uses a single $\lambda = 0.5$, the simplest form of Storey's estimator.

```python
import numpy as np

def bonferroni(p):
    return np.minimum(1.0, p.size * p)

def holm(p):                       # step-down: running max from the smallest p-value up
    m, o = p.size, np.argsort(p, kind="stable")
    adj = np.maximum.accumulate((m - np.arange(m)) * p[o])
    out = np.empty(m); out[o] = np.minimum(1.0, adj)
    return out

def bh(p, c=1.0):                  # step-up: running min from the largest p-value down
    m, o = p.size, np.argsort(p, kind="stable")
    r = c * m * p[o] / np.arange(1, m + 1)
    adj = np.minimum.accumulate(r[::-1])[::-1]
    out = np.empty(m); out[o] = np.minimum(1.0, adj)
    return out

def by(p):                         # BH at q / H_m, valid under any dependence
    return bh(p, c=np.sum(1.0 / np.arange(1, p.size + 1)))

def storey_q(p, lam=0.5):          # q-values: pi0 times the BH-adjusted p-values
    pi0 = min(1.0, np.mean(p >= lam) / (1 - lam))
    return pi0 * bh(p), pi0

p = np.loadtxt("data/hedenfalk.csv", delimiter=",", comments="#", skiprows=9, usecols=3)
print([int((f(p) <= 0.05).sum()) for f in (bonferroni, holm, bh, by)])  # [2, 2, 94, 0]
```

With $\lambda = 0.5$ the estimate is 0.6763 and $q \le 0.05$ gives 159 genes; the lab's spline recipe gives 0.6699 and 162. The full program, with the reconciliation checks and every simulation, is in the [Lab downloads](#lab-downloads).

The libraries agree on the numbers and disagree on defaults, which is where code reviews miss things:

| Library | Call | Default | Watch for |
|---|---|---|---|
| R 4.5 | `p.adjust(p, method)` | `"holm"` | `"fdr"` is an alias for `"BH"`; Hochberg and Hommel need independence or non-negative association |
| statsmodels 0.15 | `multipletests(p, alpha, method)` | `'hs'` (Holm–Šidák) | returns `(reject, adjusted, …)`; `fdr_by` is labelled for negative dependence |
| SciPy 1.18 | `false_discovery_control(ps, method)` | `'bh'` | returns adjusted p-values only; no FWER methods |
| qvalue (R) | `qvalue(p)` | π0 by spline on λ = 0.05–0.95 | version 1.x used λ = 0–0.90 and a different π0 |

R's `p.adjust` defaults to Holm and treats `"fdr"` as BH. <!-- L18 --> statsmodels' `multipletests` defaults to Holm–Šidák. <!-- L19 --> SciPy's `false_discovery_control` returns adjusted p-values, not decisions. <!-- L20 --> The qvalue defaults moved between versions, which is why the third decimal of $\hat\pi_0$ depends on which version produced it. <!-- L15 -->

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading an FDR of 0.05 as "one in twenty of my discoveries are false". The FDR is an average over studies you did not run. With correlated tests one list can be far dirtier than the average: at ρ = 0.5, 19.8% of the BH lists that were not empty had a false share above 10%. <!-- L29 -->

- **Using q-values when the tests are correlated.** Storey's gain comes from estimating π0 out of the same p-values. Correlation biases that estimate in both directions, and the downward misses flood the list: an FDR of 0.27 at a nominal 0.05 when every pair is correlated at 0.5. <!-- L29 --> If the tests are strongly correlated, use plain BH.
- **Correcting only the tests in the table.** A correction is only as good as its m. Outcome swaps, optional stopping, covariate choice and subgroups all add tests that never reach the table. <!-- L31 --> Count them or pre-specify them.
- **Assuming PRDS for two-sided tests.** The positive-dependence theorem covers one-sided tests of positively correlated normal statistics; two-sided tests are outside it. <!-- L04 --> BH usually behaves anyway, but that is an observation, not the guarantee.
- **Reaching for BY by default.** It holds under any dependence and costs a factor of $H_m$, 8.64 for 3,170 tests: on the Hedenfalk genes, every discovery. <!-- L28 --> Use it when the dependence is truly unknown, not as a safe default.
- **Ignoring ties in discrete p-values.** Permutation p-values are counts. Here the second-smallest sits exactly on Bonferroni's threshold, so `≤` and a strict inequality disagree by a gene.
- **Correcting when the question is single.** Rothman argued that adjustment rests on a universal null and trades type I errors for type II errors, so exploratory work should report unadjusted results with the number of tests. <!-- L26 --> The answer depends on the claim: a list that will be followed up needs FDR control; a set of separately reported findings needs FWER control, or every test reported in full.

## Key takeaways

- The family-wise error rate bounds the chance of any false finding; Holm controls it under any dependence and never rejects less than Bonferroni.
- The false discovery rate bounds the expected false share of a list; Benjamini–Hochberg holds it under independence or positive dependence, and Benjamini–Yekutieli under any dependence at a factor of H_m.
- An FDR is an average, not a property of your list: with correlated tests most lists are clean or empty and a few are badly wrong.
- Storey's q-values gain power by estimating π0 from the same p-values, and correlation can push their FDR to five times the target.
- A correction needs m, and forks in a single analysis, such as outcome, stopping, covariates, subgroups or screened variables, hide m; pre-specify them or count them.

## Try it yourself

1. BH at 5% finds 94 Hedenfalk genes. How many does BH find at 7.46%, and which other rule returns the same list?

<details><summary>Answer</summary>

162. Storey's q-values are π0 times the BH-adjusted p-values, so q ≤ 0.05 is the same cut as BH-adjusted ≤ 0.05/0.6699 = 0.0746. Running BH at 7.46% and calling q ≤ 0.05 with π0 = 0.6699 select the same 162 genes.

</details>

2. Under the worst-case law of Figure 7, what false discovery rate does BH at 5% have with m = 20 tests, and what level would BY use?

<details><summary>Answer</summary>

H₂₀ = 1 + 1/2 + … + 1/20 = 3.5977, so BH's FDR is 0.05 × 3.5977 = 0.1799, and BY would run BH at 0.05/3.5977 = 0.0139.

</details>

3. A colleague tests four outcomes in each of two subgroups, finds p = 0.02 for one of the eight, and reports it alone. If the eight tests were independent and every null true, how likely was at least one p below 0.05, and does p = 0.02 survive Holm?

<details><summary>Answer</summary>

1 − 0.95⁸ = 0.3366, about a one-in-three chance. Holm's first threshold is 0.05/8 = 0.00625, and 0.02 is the smallest p-value of the eight, so it fails at the first step: nothing is rejected.

</details>

## References

### Lab downloads

- [multiplicity.py](LAB_01) — the entry point: the five rules by hand, the reconciliation checks and all four simulations
- [data/hedenfalk.csv](LAB_02) — the 3,170 Hedenfalk tests with their permutation counts and provenance header
- [README.md](LAB_03) — setup, run order, the four exercises and cleanup
- [requirements.txt](LAB_04) — the pinned package versions the captures were made with
- [notebook.ipynb](LAB_05) — the README as a notebook with a runnable cell under each step
- [captures/full.txt](LAB_06) — the full-budget run that every simulated and Hedenfalk number above comes from
- [captures/quick.txt](LAB_07) — the same run at the `--quick` budget, to compare with yours
- [captures/results-full.json](LAB_08) — every number of the full run, machine-readable
- [captures/results-quick.json](LAB_09) — every number of the quick run, machine-readable

### Sources

- Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society B*, 57(1), 289–300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x
- Benjamini, Y., Krieger, A. M., & Yekutieli, D. (2006). Adaptive linear step-up procedures that control the false discovery rate. *Biometrika*, 93(3), 491–507. https://doi.org/10.1093/biomet/93.3.491
- Benjamini, Y., & Yekutieli, D. (2001). The control of the false discovery rate in multiple testing under dependency. *Annals of Statistics*, 29(4), 1165–1188. https://doi.org/10.1214/aos/1013699998
- Blanchard, G., & Roquain, E. (2009). Adaptive false discovery rate control under independence and dependence. *Journal of Machine Learning Research*, 10, 2837–2871. https://jmlr.org/papers/v10/blanchard09a.html
- Ding, P. (2024). *Linear Model and Extensions* (book manuscript, preprint). arXiv:2401.00649. https://arxiv.org/abs/2401.00649
- Freedman, D. A. (1983). A note on screening regression equations. *The American Statistician*, 37(2), 152–155 (abstract consulted). https://doi.org/10.1080/00031305.1983.10482729
- Gelman, A., & Loken, E. (2014). The statistical crisis in science. *American Scientist*, 102(6), 460. https://doi.org/10.1511/2014.111.460
- Guo, W., & Rao, M. B. (2008). On control of the false discovery rate under no assumption of dependency. *Journal of Statistical Planning and Inference*, 138, 3176–3188. https://doi.org/10.1016/j.jspi.2008.01.003
- Hedenfalk, I., et al. (2001). Gene-expression profiles in hereditary breast cancer. *New England Journal of Medicine*, 344(8), 539–548. https://doi.org/10.1056/NEJM200102223440801
- Holm, S. (1979). A simple sequentially rejective multiple test procedure. *Scandinavian Journal of Statistics*, 6(2), 65–70. https://www.jstor.org/stable/4615733
- Lehmann, E. L., & Romano, J. P. (2005). Generalizations of the familywise error rate. *Annals of Statistics*, 33(3), 1138–1154. https://doi.org/10.1214/009053605000000084
- Pawitan, Y., & Sjölander, A. (2020). Dealing with multiple testing: to adjust or not to adjust (preprint). arXiv:2010.02205. https://arxiv.org/abs/2010.02205
- R Core Team. `p.adjust` reference (R 4.5), accessed 2026-11-18. https://search.r-project.org/R/refmans/stats/html/p.adjust.html
- Roquain, E. (2011). Type I error rate control for testing many hypotheses: a survey with proofs. *Journal de la Société Française de Statistique*, 152(2), 3–38. https://arxiv.org/abs/1012.4078
- Rothman, K. J. (1990). No adjustments are needed for multiple comparisons. *Epidemiology*, 1(1), 43–46. https://doi.org/10.1097/00001648-199001000-00010
- SciPy developers. `scipy.stats.false_discovery_control` (SciPy 1.18), accessed 2026-11-18. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.false_discovery_control.html
- Simmons, J. P., Nelson, L. D., & Simonsohn, U. (2011). False-positive psychology: undisclosed flexibility in data collection and analysis allows presenting anything as significant. *Psychological Science*, 22(11), 1359–1366. https://doi.org/10.1177/0956797611417632
- statsmodels developers. `statsmodels.stats.multitest.multipletests` (statsmodels 0.15), accessed 2026-11-18. https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html
- Storey, J. D., & Tibshirani, R. (2003). Statistical significance for genomewide studies. *PNAS*, 100(16), 9440–9445. https://doi.org/10.1073/pnas.1530509100
- Storey, J. D., et al. `qvalue` R package, source 2.15.0 and the `hedenfalk` data (LGPL), accessed 2026-11-18. https://github.com/StoreyLab/qvalue
- Storey, J. D., et al. `qvalue` 1.30.0 reference manual (Bioconductor 2.10, 2012), accessed 2026-11-18. https://bioconductor.statistik.tu-dortmund.de/packages/2.10/bioc/manuals/qvalue/man/qvalue.pdf
