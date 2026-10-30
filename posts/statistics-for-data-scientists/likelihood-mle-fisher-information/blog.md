---
title: "Likelihood: The MLE, Three Tests, and Where χ² Fails"
slug: likelihood-mle-fisher-information
date: 2026-10-28
updated: 2026-10-28
summary: "One log-likelihood gives the MLE, its standard error and three tests. On a boundary, as in Poisson against negative binomial, the χ² p-value is twice too big."
tags: [data-science, statistics, maximum-likelihood, fisher-information, likelihood-ratio-test, wald-test, negative-binomial]
category: data-science
series: statistics-for-data-scientists
series_position: 4
tier: L4
difficulty: advanced
prerequisites: ["bias, variance and consistency of estimators", "derivatives to second order", "Python with NumPy"]
reading_minutes: 37
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/likelihood-mle-fisher-information"
---

![Clarke's V-1 log-likelihood with three distances to a null value: a horizontal gap, a drop in height and a tangent's slope](COVER)

> [!NOTE]
> **Insights** — The likelihood turns a model and data into one curve: its peak is the maximum likelihood estimate (MLE), the curvature at the peak is the Fisher information, and one over the information's square root is the standard error. The Wald, score and likelihood-ratio tests measure how far a null value sits from that peak in three ways; on Clarke's 576 squares of V-1 hits they agree within 10%, and on one Prussian corps' 20 years of horse-kick deaths they differ by a factor of two. The χ² reference all three rely on needs the null inside the parameter space: testing Poisson against negative binomial puts it on the boundary, where 52.6% of likelihood ratios are exactly zero and the χ² p-value is twice the correct one.

**Level:** advanced · **You need:** bias, variance and consistency of estimators; derivatives to second order; Python with NumPy · **Time:** ~37 min

**Jump to:** [worked example](#worked-example) · [when the tests disagree](#when-do-the-wald-score-and-likelihood-ratio-tests-disagree) · [a second parameter](#what-changes-with-a-second-parameter) · [profile intervals](#why-is-the-profile-likelihood-interval-lopsided) · [the boundary](#what-happens-when-the-null-sits-on-a-boundary) · [regularity conditions](#which-conditions-does-the-likelihoods-promise-need) · [power law or lognormal](#power-law-or-lognormal-what-does-the-likelihood-ratio-say) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: one NumPy, SciPy and statsmodels script that runs in about 100 seconds and is seeded, so every number repeats exactly. Each simulated quantity is printed as an estimate ± its Monte Carlo standard error (MCSE) with its number of replications R; the exact error rates are sums over the Poisson distribution, not simulations. Published numbers are **quoted** from their sources.

## Why this matters

You fit a negative binomial because your counts look too variable for a Poisson, and you want a p-value for "no extra variance". The textbook recipe doubles the difference in log-likelihoods and compares it with χ² on one degree of freedom. On Clarke's V-1 counts that returns p = 0.52; the right answer is 0.26, because the null value sits at the edge of what the model allows, where the recipe's reference distribution is wrong. R's `pscl::odTest` makes the correction; <!-- L23 --> a hand-rolled comparison usually does not. The same edge appears whenever a test asks whether a variance, a zero-inflation probability or any other quantity that cannot go negative is zero.

## The problem

The third part of this series, *Estimators and Their Errors: Why the Best One Can Be Biased*, judged estimators by bias, variance and mean squared error, and met one maximum likelihood estimator, for the German tank problem, without saying where such estimators come from. This part supplies the recipe, and the standard errors and tests that come with it.

Write down a model for how the data arise: a density or mass function f(x; θ) with an unknown parameter θ. Read as a function of θ with the data held fixed, the probability of the data actually observed is the **likelihood**, L(θ). Fisher defined it in 1922 as proportional to the probability that, were θ to have that value, the observations would be the ones observed. <!-- L01 --> It is not a probability distribution over θ: it does not integrate to one over θ, and its peak stays put when θ is rewritten on another scale. <!-- L02 --> The **maximum likelihood estimate (MLE)**, θ̂, is the value with the largest likelihood. For independent data the likelihood is a product, so its log, the **log-likelihood** ℓ(θ), is a sum and easier to differentiate.

In a regular model the log-likelihood near its peak looks like a downward parabola, and three large-sample promises follow. The MLE is approximately normal around the true value. Its standard error comes from how sharply the curve falls at the peak, the **Fisher information**. And three statistics, Wald, score and likelihood ratio, measure how far a hypothesised value θ₀ sits from θ̂, each approximately χ² with one degree of freedom when θ₀ is true. Most of what statistical software prints rests on these promises: the standard error beside every fitted coefficient, every Wald z, every likelihood-ratio test of nested models.

Each promise needs conditions, the **regularity conditions**, and this post breaks three of them on real data. The claim it tests is the one most often repeated without its condition: the likelihood-ratio statistic is χ²-distributed.

## Worked example

### The rate, its information and its standard error

Clarke's 1946 note counts the V-1 flying bombs that fell on 576 squares of south London, a quarter square kilometre each: 229 squares took no hit, 211 one, 93 two, 35 three and 7 four, and one square took the remaining 7 of 537 hits. <!-- L34 --> The first part of this series, *Distributions as Generative Stories: Let the Process Pick*, derived a Poisson model from the bombs' story and set its rate to the mean. Here the likelihood fits it.

Each square's count x is Poisson with rate λ, P(x) = e^(−λ) λ^x / x!. The squares are independent, so the log-likelihood of all 576 is a sum, and the counts enter it only through their total, 537:

ℓ(λ) = 537 log λ − 576 λ − 157.95

The constant, minus the sum of log xᵢ!, does not involve λ and drops out of everything below. The slope of ℓ is the **score**, U(λ) = 537/λ − 576. At the peak the slope is zero: 537/λ = 576 gives λ̂ = 537/576 = 0.9323 hits per square, the sample mean. SciPy's bounded optimiser lands on the same value to seven decimals, with ℓ(λ̂) = −732.59.

The second derivative says how fast the curve bends: −ℓ″(λ) = 537/λ², which at λ̂ is 537/0.9323² = 617.8. Minus the second derivative at the MLE is the **observed information**, J(λ̂). Its average over data sets drawn from the model, the **expected information** or Fisher information, is I(λ) = 576/λ, since each count averages λ; at λ̂ it is also 617.8. The standard error is one over the information's square root:

SE(λ̂) = 1/√617.8 = 0.0402

A sharper peak means more information and a smaller standard error. statsmodels fits the same model as a Poisson GLM with a log link and reports log λ̂ = −0.0701 with standard error 1/√537 = 0.0432; multiplying by λ̂ to return to the rate's scale gives 0.0402 again. Figure 1 draws the log-likelihood beside the parabola with the same peak and curvature.

![Clarke's Poisson log-likelihood peaks at 0.9323 with curvature 617.8; below it the score crosses zero at the same point](FIG_01)
*Figure 1. The peak is the estimate and the curvature is the information. Near the peak curve and parabola coincide; far out, the curve falls faster on the left.*

### Three distances from one null value

Now test a value for λ. Take λ₀ = 0.85, a device chosen to sit two standard errors (2.05) below the estimate. There are three natural ways to say how far it sits from 0.9323, and Buse drew all three on one curve: <!-- L10 -->

- **Wald statistic**: the horizontal gap, squared and weighted by the information at the MLE: (0.9323 − 0.85)² × 617.8 = 4.18. It needs only the fitted model.
- **Likelihood-ratio (LR) statistic**: twice the drop in log-likelihood from the peak to λ₀. The drop is 2.224, so LR = 4.45.
- **Score statistic**: the slope at λ₀, squared and divided by the information there. U(0.85) = 537/0.85 − 576 = 55.76 and I(0.85) = 576/0.85 = 677.6, so the statistic is 55.76²/677.6 = 4.59. It needs only the null model.

Wald's 1943 paper built tests from the MLE and its information, <!-- L08 --> Rao's 1948 paper from the score, which the Lagrange multiplier test of Aitchison and Silvey turns out to equal. <!-- L09 --> The likelihood ratio's large-sample law is Wilks's 1938 theorem: when λ₀ is true and sits inside the parameter space, each statistic is approximately **χ²₁**, the distribution of a squared standard normal, whose 95th percentile is 3.84. <!-- L07 -->

Against χ²₁ the three give p-values of 0.041, 0.035 and 0.032: the probability, were λ₀ true, of a statistic at least this large. What a p-value does and does not say is the subject of a later part of this series; here it is a tail area of χ²₁. The three statistics lie within 10% of each other, and their order is not fixed: at λ₀ = 1.0, above the estimate, Wald gives 2.83, LR 2.70 and score 2.64.

![On Clarke's log-likelihood the gap to 0.85 gives Wald 4.18, the drop gives LR 4.45, and the slope there gives score 4.59](FIG_02)
*Figure 2. Three readings of one distance. With 537 hits the curve is almost a parabola, so the three nearly agree.*

## Intuition

The log-likelihood is a hill over the parameter's possible values, built from the data. Its summit is the estimate. How sharply the ground falls away from the summit is the information: a narrow ridge pins the parameter down, a broad dome does not. To say how far a candidate value lies from the summit, you can measure the distance on the map (Wald), the steepness of the ground where you stand (score), or how far you have climbed down (likelihood ratio).

On a perfect dome, a parabola in θ, the three readings convert into one another exactly; Buse showed that they are then the same number, with an exact χ² distribution at every sample size. <!-- L10 --> More data narrow the hill, and close to its summit any smooth hill looks like a dome, which is why the three agree in large samples. The analogy breaks at the edge of the map. A hiker cannot stand beyond the edge, but the data can pull the summit past it, and then the estimate is pinned to the edge, the distance on the map is zero in about half of all samples, and the χ² readings fail.

## When do the Wald, score and likelihood-ratio tests disagree?

When the hill is lopsided, which happens when the counts are small. Bortkiewicz's table of deaths by horse kick holds a clean example. He left four of the 14 Prussian corps out of his famous 200 corps-years because their make-up differed, corps XI among them, with three divisions. Corps XI lost 25 men in the 20 years from 1875 to 1894, against 122 deaths in the 200 corps-years he kept, a rate of 0.61. <!-- L36 --> Take 0.61 as known, since its standard error, 0.055, is a fifth of corps XI's 0.25, and test it (Figure 3).

![Corps XI's lopsided log-likelihood: Wald 6.55, likelihood ratio 10.27 and score 13.43 for the same null rate of 0.61](FIG_03)
*Figure 3. Wald's parabola drops 3.28 at the null; the curve itself drops 5.14. Wald sees the least distance, the score test the most.*

The same data and the same null give Wald 6.55, LR 10.27 and score 13.43, with p-values of 0.010, 0.0014 and 0.00025: all three reject at 5%, but the evidence they report differs 40-fold. Figure 3 shows why. Wald replaces the curve by the parabola with the curvature at the MLE, 20/1.25 = 16. At 0.61 that parabola has dropped 3.28, half the Wald statistic, while the curve has dropped 5.14, half the LR. The score test measures at the other end, where the information, 20/0.61 = 32.8, is twice as large. For a Poisson rate the likelihood ratio always lies between the other two, and which of them is larger depends only on which side of the estimate the null sits. In the linear regression model Berndt and Savin proved a fixed order, Wald ≥ LR ≥ score, but Buse notes that the geometry alone cannot fix an order in general. <!-- L11 -->

### How often does each test err?

Lopsidedness belongs to the count, not to the number of squares or years. For a Poisson rate all three statistics depend on the data only through the total count T, and on the design only through m = nλ₀, the total expected under the null (equation 4). So the actual error rate of each nominal 5% test can be computed exactly, for any m, by summing the Poisson probabilities of every total that rejects (Figure 4).

![Exact rejection rates of 5% Wald, score and likelihood-ratio tests against the expected count: erratic below 20, all near 5% by 537](FIG_04)
*Figure 4. Below an expected count of about 20 the Wald test's error rate swings far from 5%; the score test's stays closest.*

At corps XI's m = 12.2 the Wald test rejects a true null 8.84% of the time, the likelihood-ratio test 6.57% and the score test 4.26%, and their verdicts differ in 8.1% of data sets drawn under the null. At Clarke's m = 537 they reject 5.03%, 4.97% and 4.95%, and differ in 1.0%. Over expected counts from 2 to 20 the largest departure from 5% is 15.5 points for Wald, 10.1 for the likelihood ratio and 2.8 for the score test. Wald fails worst at the bottom: when no event occurs, its estimated standard error is zero and its statistic infinite, so at m = 0.5 it rejects 61% of true nulls. The zigzag is the count's discreteness: each curve jumps where m crosses a value at which one more total starts to reject.

### Does it matter how the parameter is written?

For Wald, yes. The likelihood ratio compares two heights on the curve, and writing λ as log λ or 1/λ moves neither the peak nor the null, only their labels, so the LR statistic cannot change; the score statistic does not change either. The Wald statistic squares a distance on whatever scale the parameter is written in, and the curve is close to a parabola on at most one of them. Figure 5 computes it for one null on the scales λ^c.

![Wald statistics for one null across scales λ^c: corps XI from 3.63 to 27.52, Clarke 3.82 to 5.03; score and LR stay flat](FIG_05)
*Figure 5. One hypothesis, written on many scales. Corps XI's Wald statistic ranges from not significant to overwhelming.*

For corps XI, testing the rate gives 6.55, its log 12.87 and the mean time between deaths, 1/λ, 27.52; testing λ² gives 3.63, which does not reject at 5% (p = 0.057). On the cube-root scale Wald gives 10.18, close to the likelihood ratio's 10.27. Even Clarke's 537 hits are not immune near the threshold: across scales, the Wald statistic for 0.85 runs from 3.82 to 5.03, either side of 3.84. Fears, Bénichou and Gail found the same in a random-effects analysis of variance, where power transformations of one parameter gave Wald p-values anywhere from 0 to 1, <!-- L13 --> and in logistic regression Hauck and Donner found the Wald statistic falling back toward zero as the estimate moves far from the null. <!-- L14 -->

Why is Wald everywhere, then? Convenience. It needs only the fitted model, which the software has just maximised; the score test needs only the null model, and the likelihood ratio needs both. Engle notes that, since the three differ only in finite samples, computational convenience often decides which is used. <!-- L12 --> With small counts, a skewed parameter or a result near your threshold, refit under the null and use the likelihood ratio or the score test.

## What changes with a second parameter?

Greenwood and Yule's 647 munition workers had 447, 132, 42, 21, 3 and 2 accidents for 0 to 5 over five weeks, <!-- L35 --> a variance 1.49 times the mean. The first part explained it as accident proneness: each woman has her own Poisson rate, the rates follow a gamma distribution, and the counts follow a **negative binomial** with mean μ and variance μ + μ²/k. The shape k measures how unequal the rates are: smaller k means more unequal, and k → ∞ is the Poisson. The first part fitted it by moments, k = 0.955; here the likelihood fits μ and k together.

The log-likelihood ℓ(μ, k) (equation 5) has a feature that simplifies the whole fit: its slope in μ is zero at μ = ȳ = 0.4652, whatever k is. The best mean is always the sample mean, so the search runs along one line, and the score equation for k is solved by **Newton's method**, which steps to where the score's tangent crosses zero. From the moment estimate 0.9548 it moves to 0.8485, 0.8646, 0.86512 and 0.8651158, and stops after five steps with the score at 10⁻¹¹. The MLE is k̂ = 0.865, below the moment estimate. SciPy's general optimiser over both parameters lands on the same point. statsmodels' `NegativeBinomial` writes the model with the dispersion α = 1/k, variance μ + αμ², <!-- L32 --> and reports α̂ = 1.155915, the same fit, with log-likelihood −592.27 against −617.18 for the Poisson. SciPy's `nbinom` uses yet another convention, n = k and p = k/(k + μ). <!-- L33 --> The fitted counts for 0 to 4 and 5 or more accidents are 445.9, 134.9, 44.0, 14.7, 5.0 and 2.6, with a chi-square of 3.77 against the moment fit's 4.20.

With two parameters the information is a 2 × 2 matrix. At the MLE its diagonal holds 904.4 for μ and 28.83 for k, and its off-diagonal entry is exactly zero: μ and k are **orthogonal**, so the estimate of one carries no information about the other, and the standard errors are 1/√904.4 = 0.0333 for μ̂ and 1/√28.83 = 0.186 for k̂. Figure 6 draws the likelihood surface.

![Negative binomial likelihood regions in mean and shape: the 95% region reaches k = 1.58, while the Wald ellipse stops at 1.32](FIG_06)
*Figure 6. The likelihood region stretches upward, toward the Poisson; the ellipse built from the information is symmetric.*

The 95% region, every (μ, k) whose log-likelihood lies within 3.00 of the peak (half the 95th percentile of χ² on two degrees of freedom), runs from k = 0.535 to 1.585, while the ellipse the information implies runs from 0.409 to 1.321. The region is upright, because the parameters are orthogonal, but lopsided: the data rule out very unequal rates more firmly than nearly equal ones.

For k, the observed and expected informations also differ: 28.83 against 29.57, standard errors 0.1863 and 0.1839. Efron and Hinkley argued for the observed one, because it approximates the variance conditional on how informative this particular sample turned out to be; <!-- L15 --> a 2013 dissertation, available as a preprint, finds that the expected one estimates the unconditional variance with no larger mean squared error. <!-- L16 --> Here the 1.3% difference is the smaller problem. Neither standard error describes an estimate whose sampling distribution is skewed.

## Why is the profile-likelihood interval lopsided?

Because the curve is. A confidence interval can be built by inverting a test: it collects the values of k the test would not reject. Inverting the Wald test gives k̂ ± 1.96 SE, 0.500 to 1.230, symmetric by construction. Inverting the likelihood ratio gives the **profile-likelihood interval**: for each k, maximise the log-likelihood over the other parameters (here μ = ȳ every time), and keep the values of k whose profile lies within 1.92 = 3.84/2 of the peak. <!-- L38 --> It runs from 0.585 to 1.383, 0.280 below k̂ and 0.518 above (Figure 7). What "95%" promises, and how often each interval actually covers, is measured in a later part of this series.

![Profile log-likelihoods for k and the dispersion index cut at −1.92: the profile intervals are lopsided, the Wald ones symmetric](FIG_07)
*Figure 7. Where each curve crosses −1.92 is its 95% interval. The profile reaches farther toward large k than the Wald parabola.*

The Wald interval on log k, k̂ × exp(±1.96 SE/k̂), is 0.567 to 1.319: a better parabola, still not the curve. Lawless found the same for the negative binomial's dispersion: likelihood-ratio intervals are preferable, and the estimate's sampling distribution has a shorter left tail and a longer right tail than the normal approximation. <!-- L20 --> The lab checks the shape directly: it draws 20,000 data sets of 647 women from the fitted negative binomial and re-estimates k in each (Figure 8).

![Histogram of 20,000 re-estimated k: skewed right, with 7.47% above the upper Wald limit and 0.14% below the lower](FIG_08)
*Figure 8. The normal curve the Wald standard error implies is too narrow on the right and too wide on the left.*

The re-estimates average 0.914 against a true 0.865, with median 0.881, standard deviation 0.216 against Wald's 0.186, and skewness 1.38. A normal distribution would put 2.5% beyond each Wald limit; the simulation puts 7.47% ± 0.19% above 1.230 and 0.14% ± 0.03% below 0.500. The profile interval's long upper arm is that right tail, read off a single data set's curve.

### The delta method

Often the quantity of interest is a function of the parameters. The **delta method** carries the standard errors to it by replacing the function with its tangent plane at the MLE (equation 7); it approximates the moments of the function and is accurate only under conditions on the function and the estimator. <!-- L37 --> Take the dispersion index, variance over mean, D = 1 + μ/k, whose moment value in the first part was 1.49: at the MLE it is 1.538. Its gradient and the inverse information give a standard error of 0.1220, 90% of its variance from k̂, and the simulation agrees: D̂ has a standard deviation of 0.121 over the 20,000 data sets. The delta interval, 1.299 to 1.777, is symmetric. The profile interval for D, which maximises over μ with k = μ/(D − 1), runs from 1.331 to 1.819. The delta method got the spread right and the shape wrong, because D̂ is skewed too (skewness 0.30).

## What happens when the null sits on a boundary?

Ask whether Clarke's squares are overdispersed at all: is the Poisson enough, or do the bombs cluster? Write the negative binomial with α = 1/k, so that α = 0 is the Poisson. A negative binomial cannot have a variance below its mean, so α ≥ 0, and the null value α = 0 sits on the **boundary** of the parameter space. Figure 9 shows what that does to the likelihood.

![Profile log-likelihood in α: Clarke's peaks inside at 0.040 with LR 0.41; a simulated Poisson data set peaks on the edge, α = 0](FIG_09)
*Figure 9. When the curve falls from the edge, the maximum is the edge itself, and the likelihood ratio is exactly zero.*

For Clarke's squares the variance (divisor n) is 0.9694, above the mean of 0.9323, so the curve rises from α = 0 and peaks inside, at α̂ = 0.040 (k̂ = 25), with LR = 0.41. For a simulated Poisson data set whose variance, 0.8725, falls below its mean, 0.9028, the curve falls from α = 0, and the maximum is the Poisson itself: α̂ = 0 and LR = 0 exactly. The score at α = 0 is proportional to Σ(y − ȳ)² − Σy, so which case occurs depends only on whether the variance exceeds the mean, and under a Poisson that is close to a coin flip.

Chernoff worked out the consequence in 1954: with one parameter whose true value sits on the boundary, twice the log-likelihood ratio tends not to χ²₁ but to an equal mixture of a point mass at zero and χ²₁. <!-- L17 --> Self and Liang extended the result to nuisance parameters that stay inside, here μ, and gave the test for a single random effect as the typical case. <!-- L18 --> Lawless gave the negative binomial version, testing α = 0. <!-- L19 --> The lab measures it on 200,000 Poisson data sets shaped like Clarke's and, for contrast, on 200,000 negative binomial data sets shaped like Greenwood and Yule's, testing their true k, which lies inside (Figure 10).

![Simulated shares above each likelihood ratio: inside they follow χ²₁; on the boundary 52.6% sit at 0 and the mixture fits](FIG_10)
*Figure 10. Inside the parameter space the χ²₁ curve and the simulation coincide. On the boundary half the mass sits at zero.*

Inside, the χ²₁ test at 3.84 rejects 5.01% ± 0.05% of true nulls: Wilks's promise holds. On the boundary, LR = 0 in 52.61% ± 0.11% of data sets, the χ²₁ test rejects only 2.17% ± 0.03%, and the mixture's 5% point, 2.71, the 90th percentile of χ²₁, rejects 4.40% ± 0.05%. Comparing the likelihood ratio with χ²₁ on a boundary halves the test's error rate and doubles every p-value: the mixture's p-value is half of P(χ²₁ ≥ LR). For Clarke's LR of 0.41 that is 0.26, not 0.52. R's `pscl::odTest` builds the mixture in, comparing the ratio with 2.7 rather than 3.8. <!-- L23 --> The mixture is a large-sample result, and at Clarke's n the boundary still holds 52.6% of data sets rather than 50%, which leaves even the corrected test slightly conservative; Lawless reported the same direction. <!-- L19 --> For Greenwood and Yule the correction does not matter: LR = 49.8 and the p-value is about 10⁻¹² either way.

The score test needs nothing new on a boundary, only the Poisson fit. With no covariates it is Fisher's dispersion test, Σ(y − ȳ)²/ȳ against χ² on n − 1 degrees of freedom, <!-- L21 --> and score tests of this kind detect arbitrary mixed-Poisson alternatives. <!-- L22 --> For Clarke's squares the statistic is 598.9 on 575 degrees of freedom, one-sided p = 0.24, close to the corrected likelihood ratio's 0.26 and far from the naive 0.52. Molenberghs and Verbeke show that the three tests stay asymptotically equivalent on a boundary once the score and Wald tests are made one-sided, with χ² mixtures as their null distributions. <!-- L24 --> A variance component in a mixed model poses the same problem in a harder shape, where the χ² mixture can be a poor approximation; <!-- L25 --> a later part of this series takes it up.

## Which conditions does the likelihood's promise need?

Fisher published the method in 1922 while saying he was not satisfied with the rigour of his own proof, <!-- L04 --> and the earliest proof of the MLE's consistency generally accepted as correct is Wald's, from 1949. <!-- L06 --> One standard list, from Brazzale and Mameli's review, has five regularity conditions: <!-- L05 -->

1. The parameters are identifiable: different values give different distributions.
2. The support, the set of values the data can take, does not depend on θ.
3. The true value sits inside a parameter space of fixed dimension.
4. The log-likelihood has three derivatives near the true value, the third suitably bounded.
5. The score averages zero and its variance equals the information, which is finite and positive.

Each failure leads to its own reference distribution:

| What breaks | Case in this post | What happens | Reference distribution |
|---|---|---|---|
| nothing | Clarke's rate; k inside | the three statistics agree | χ²₁ |
| the count is small | corps XI | they disagree, and Wald depends on the scale | χ²₁ only as the count grows |
| 3: the null on the boundary | Poisson against negative binomial | half the estimates sit on the edge | ½χ²₀ + ½χ²₁ |
| 2: the support moves with θ | German tanks | no zero score, no information | none; the error is exponential |
| 3: the dimension grows with n | Neyman–Scott pairs | the MLE is inconsistent | none |
| the models are not nested | power law against lognormal | the sign of the ratio carries the evidence | normal after standardising |

The German tank problem breaks condition 2. Serial numbers run from 1 to N, so a capture of five tanks whose largest serial is 303 has likelihood 1/C(N, 5) for N ≥ 303 and zero below: the support moves with N (Figure 11).

![German tank log-likelihood falls from a wall at 303 with no peak; the MLE's error is skewed, and a normal would put 12% below 0](FIG_11)
*Figure 11. Cut off at the largest serial, the likelihood has no peak to measure. Its maximum is the edge, and the error is one-sided.*

The maximum is the edge, N̂ = 303, where the log-likelihood is still falling, by 0.0166 per tank: the score is not zero. The curve bends upward, so minus its second derivative is negative and there is no information to invert. The MLE's error, N minus the largest serial, can never be negative: over all captures of five tanks from 342 it has mean 56.2, standard deviation 47.9 and skewness 1.18, and a normal with that mean and spread would put 12% of its errors below zero. As the population grows, k(N − N̂)/N tends to an exponential distribution: for 20 tanks from 100,000 it lies 0.014 from the exponential in Kolmogorov distance and 0.147 from the normal with the same mean and standard deviation. The third part found these errors shrinking like 1/k rather than 1/√k; no part of the regular theory applies. Le Cam's survey makes the same point with the continuous uniform on 0 to θ, whose MLE, the sample maximum, has a larger mean squared error than a slightly stretched maximum at every sample size. <!-- L26 -->

Condition 3's fixed dimension fails when parameters multiply with the data. In Neyman and Scott's example each pair of measurements has its own mean and all pairs share one variance; the MLE of that variance converges to half its true value, however many pairs arrive. <!-- L27 --> Per-user or per-store intercepts estimated by maximum likelihood from a few observations each put a model in the same position.

## Power law or lognormal: what does the likelihood ratio say?

The first part drew 10,000 values from a lognormal distribution with σ = 2.5, found that its top 10% lay on a straight line on log–log axes, as a power law's would, and left the test to this part. The lab regenerates that sample exactly, from the same seed, and runs the procedure of Clauset, Shalizi and Newman (CSN).

Above a threshold x_min a power law has density proportional to x^(−α), and the MLE of α is 1 + n/Σ log(xᵢ/x_min), the Hill estimator, with standard error (α̂ − 1)/√n; CSN choose the threshold that minimises the Kolmogorov–Smirnov distance between the data and the fitted power law. <!-- L29 --> The competitor is a lognormal cut off at the same threshold, fitted by maximum likelihood over its two parameters. The two families are not **nested**, neither contains the other, so Wilks's theorem says nothing about their likelihood ratio. Vuong showed instead that for non-nested models the log-likelihood ratio, divided by its estimated standard deviation, is approximately standard normal when the two models are equally close to the truth. <!-- L28 --> CSN use that normalised ratio and trust its sign only when its two-sided p is below 0.1. <!-- L30 -->

On the 1,000 points the first part fitted, those above 26.14, the power law's α̂ is 1.837 ± 0.026, and the lognormal's fitted μ and σ are −1.88 and 2.95. The lognormal's log-likelihood is higher by 7.02, the normalised ratio is 2.29 and p = 0.022: the data favour the lognormal, which is the truth (Figure 12). CSN's α is the density's exponent, so the survival curve falls with slope −(α̂ − 1) = −0.84, not the first part's least-squares slope of −0.92.

![The top 1,000 values of the first part's lognormal sample on log–log axes: the lognormal fit follows the bend, the power law overshoots](FIG_12)
*Figure 12. Both fits pass through the bulk of the points. The extreme tail, a few dozen values, carries the lognormal's advantage.*

At CSN's own threshold, 63.65, which leaves 509 points, the comparison cannot decide: normalised ratio 1.29, p = 0.20. The `powerlaw` package, which implements the procedure, <!-- L31 --> reproduces both results and the threshold exactly. Figure 13 shows how the verdict moves with the threshold.

![Vuong's normalised ratio against tail size: 1.10 at 100 points, 2.29 at 1,000 and 12.49 at 5,000; undecided below about 1,000](FIG_13)
*Figure 13. The fewer points the threshold leaves, the less the comparison can say. A true power law is almost never confirmed.*

With 5,000 points the ratio is 12.49; with 100 it is 1.10. Over 1,000 fresh lognormal samples the comparison decides for the lognormal in 98.1% at 1,000 points but in only 45.9% at 500. When the truth is a power law with α = 1.837 and 1,000 points, it decides for the power law in 4.4% of samples, for the lognormal in 0.1%, and stays undecided in 95.5%: a lognormal with a very large σ mimics a power law over any finite range, so the test can rule a power law out but rarely confirm it. The first part's question is settled for its own sample at its own threshold: lognormal. At CSN's threshold the honest answer is "cannot tell".

## The math

| Symbol | Meaning |
|---|---|
| ℓ(θ), U(θ) | log-likelihood and score, U = dℓ/dθ |
| J(θ), I(θ) | observed information −ℓ″(θ), and expected (Fisher) information, its mean over data sets |
| θ₀, T, m | null value; observed total count; total expected under the null, m = nλ₀ |
| μ, k, α | negative binomial mean, shape, and dispersion α = 1/k |

**Likelihood, score and information.** For independent observations with density or mass function f(x; θ),

$$
\ell(\theta) = \sum_{i=1}^{n} \log f(x_i;\theta), \qquad U(\theta) = \ell'(\theta), \qquad J(\theta) = -\ell''(\theta) \tag{1}
$$

The MLE solves U(θ̂) = 0 when the maximum lies inside the parameter space; for Clarke's squares U(λ) = 537/λ − 576 and J(λ) = 537/λ².

$$
\operatorname{E}\,U(\theta) = 0, \qquad I(\theta) = \operatorname{Var}\,U(\theta) = -\operatorname{E}\,\ell''(\theta) \tag{2}
$$

At the true value the score averages zero and its variance is the expected curvature. Fisher's 1925 paper defined this information and gave the MLE's large-sample distribution as normal with variance 1/I(θ). <!-- L03 --> For a Poisson rate I(λ) = n/λ, which at λ̂ equals J(λ̂): both are 617.8 for Clarke.

**The three statistics.** For H₀: θ = θ₀,

$$
W = (\hat\theta - \theta_0)^2\, I(\hat\theta), \qquad S = \frac{U(\theta_0)^2}{I(\theta_0)}, \qquad \mathrm{LR} = 2\big[\ell(\hat\theta) - \ell(\theta_0)\big] \tag{3}
$$

Each is approximately χ²₁ when θ₀ is true and inside the parameter space of a regular model. For a Poisson rate they reduce to

$$
W = \frac{(T - m)^2}{T}, \qquad S = \frac{(T - m)^2}{m}, \qquad \mathrm{LR} = 2\Big[T \log\frac{T}{m} - (T - m)\Big] \tag{4}
$$

The data enter only through T, so the exact error rates in Figure 4 are sums over T distributed as Poisson(m). Wald divides by T and the score statistic by m, so the score statistic is the larger whenever the estimate lies above the null, and the LR always lies between them. For Clarke at λ₀ = 0.85, T = 537 and m = 489.6, so W = 47.4²/537 = 4.18 and S = 47.4²/489.6 = 4.59.

<details>
<summary>Why the likelihood ratio is χ²₁, and where the argument breaks</summary>

Expand ℓ(θ₀) around θ̂, where ℓ′(θ̂) = 0:

$$
\ell(\theta_0) = \ell(\hat\theta) - \tfrac12\, J(\hat\theta)\,(\hat\theta - \theta_0)^2 + O\big((\hat\theta - \theta_0)^3\big)
$$

So LR = J(θ̂)(θ̂ − θ₀)² plus a remainder that vanishes as n grows. Since √I(θ₀) (θ̂ − θ₀) tends to a standard normal Z, and J(θ̂)/I(θ₀) tends to 1, LR tends to Z², which is χ²₁. This expansion is the core of Wilks's theorem, and it uses every regularity condition. <!-- L07 --> On a boundary, θ̂ cannot fall on the far side of θ₀: it equals θ₀ whenever Z would be negative, so LR tends to max(0, Z)², which is zero with probability one half and χ²₁ otherwise. Where the support moves with θ, ℓ′(θ̂) is not zero and the expansion never starts.

</details>

**The negative binomial.** With mean μ and shape k,

$$
\ell(\mu, k) = \sum_{i} \Big[\log\Gamma(y_i + k) - \log\Gamma(k) - \log y_i! + k \log\frac{k}{k + \mu} + y_i \log\frac{\mu}{k + \mu}\Big] \tag{5}
$$

Its slope in μ is k Σ(yᵢ − μ)/(μ(k + μ)), zero at μ = ȳ for every k, and the cross term of the information, Σ(yᵢ − μ)/(k + μ)², is zero there too, which is the orthogonality. The profile score for k is then

$$
\frac{\partial \ell}{\partial k}\bigg|_{\mu = \bar y} = \sum_i \sum_{j=0}^{y_i - 1} \frac{1}{k + j} \;-\; n \log\Big(1 + \frac{\bar y}{k}\Big) \tag{6}
$$

using Γ(y + k)/Γ(k) = k(k + 1)⋯(k + y − 1) for whole-number y. Newton's method solves it, and minus its derivative at k̂, 28.83, is the observed information for k.

**The delta method.** For a function g of the estimates, with gradient ∇g,

$$
\operatorname{Var}\, g(\hat\theta) \approx \nabla g^{\top} J^{-1}\, \nabla g \tag{7}
$$

For D = 1 + μ/k the gradient is (1/k, −μ/k²) = (1.156, −0.622) and J⁻¹ is diagonal with entries 1/904.4 and 1/28.83, so Var D̂ ≈ 0.00148 + 0.01340 and SE(D̂) = 0.122.

**The boundary mixture.** With the null on the boundary and the nuisance parameters inside,

$$
\mathrm{LR} \;\to\; \tfrac12\,\chi^2_0 + \tfrac12\,\chi^2_1, \qquad p = \tfrac12 \Pr\big(\chi^2_1 \ge \mathrm{LR}\big) \quad \text{for } \mathrm{LR} \gt 0 \tag{8}
$$

Here χ²₀ is a point mass at zero, so the 5% critical value is the 90th percentile of χ²₁, 2.71. For Clarke, half of 0.522 is 0.261.

**Vuong's statistic.** With dᵢ the log of the ratio of the two fitted densities at the i-th point, and s_d their standard deviation,

$$
z = \frac{\sum_{i=1}^{n} d_i}{\sqrt{n}\; s_d} \tag{9}
$$

The statistic z is approximately standard normal when the two models are equally close to the truth. For the first part's 1,000 points, Σdᵢ = 7.02 and z = 2.29.

## Implementation

The negative binomial fit by hand takes a screen: Newton's method on the profile score (6), in log k so that k stays positive, then the same fit in statsmodels.

```python
import numpy as np
import statsmodels.api as sm

y, w = np.array([0, 1, 2, 3, 4, 5]), np.array([447, 132, 42, 21, 3, 2])   # Greenwood and Yule's 647 women
n, ybar = w.sum(), (y * w).sum() / w.sum()


def score_k(k):
    """dl/dk at mu = ybar, and its derivative in k; for integer y, psi(y + k) - psi(k) = sum of 1/(k + j)."""
    s = sum(wi * (1 / (k + np.arange(yi))).sum() for yi, wi in zip(y, w)) - n * np.log1p(ybar / k)
    ds = n * ybar / (k * (k + ybar)) - sum(wi * (1 / (k + np.arange(yi)) ** 2).sum() for yi, wi in zip(y, w))
    return s, ds


k = ybar ** 2 / ((w * (y - ybar) ** 2).sum() / (n - 1) - ybar)    # moment estimate, the starting point
for _ in range(6):
    s, ds = score_k(k)
    k *= np.exp(-s / (k * ds))                                     # Newton's step on log k
print(f"k_hat {k:.6f}  alpha_hat {1 / k:.6f}  SE(k_hat) {1 / np.sqrt(-score_k(k)[1]):.4f}")

nb2 = sm.NegativeBinomial(np.repeat(y, w), np.ones((n, 1)), loglike_method="nb2")
fit = nb2.fit(method="newton", tol=1e-12, disp=0)
print(f"statsmodels: alpha {fit.params[1]:.6f}  SE(alpha) {fit.bse[1]:.4f}  log-likelihood {fit.llf:.4f}")
```

It prints:

```text
k_hat 0.865116  alpha_hat 1.155915  SE(k_hat) 0.1863
statsmodels: alpha 1.155915  SE(alpha) 0.2489  log-likelihood -592.2671
```

statsmodels' standard error for α is the observed-information one carried to α's scale, SE(k̂)/k̂² = 0.2489, and with Newton's method and a tight tolerance its α̂ matches the hand fit to six decimals.

Whether a Poisson data set's maximum sits on the boundary needs no fitting at all, only its variance and mean. In whole numbers, so that data sets whose variance equals their mean exactly land on the right side:

```python
import numpy as np

rng = np.random.default_rng(20261028)
counts = rng.poisson(537 / 576, size=(20_000, 576))        # 20,000 Poisson data sets shaped like Clarke's
s1, s2 = counts.sum(axis=1), (counts ** 2).sum(axis=1)
on_edge = 576 * s2 - s1 ** 2 - 576 * s1 <= 0               # variance (divisor n) at most the mean, in integers
print(f"data sets whose MLE is the Poisson itself, LR = 0: {on_edge.mean():.4f}")
```

It prints 0.5267, within its MCSE of 0.0035 of the lab's 0.5261. The lab adds the vectorised fits behind every rate above, the exact error rates, the profile and delta-method intervals, the tank's exact distribution and the power-law comparison; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** comparing a likelihood ratio with χ²₁ when the null value is the edge of what the model allows: no overdispersion (α = 0), no random effect (a variance of zero), no zero inflation. About half the data sets then give LR = 0 exactly, the χ²₁ test rejects about 2.2% of true nulls instead of 5%, and every p-value is twice too large. Halve the p-value, or compare the ratio with 2.71.

- **Wald intervals for skewed parameters.** Dispersions, variances and rates near zero have lopsided likelihoods: for k, 7.47% of the estimates' distribution fell above the Wald interval and 0.14% below it. Use the profile-likelihood interval, or at least build the Wald interval on the log scale.
- **Reading one Wald statistic as the answer.** It depends on how the parameter is written: for corps XI it runs from 3.63 to 27.52 for one hypothesis, while the likelihood ratio stays at 10.27. When a Wald p-value sits near your threshold, refit under the null.
- **Small counts.** The three tests agree only when the expected count is large: from 2 to 20 the Wald test's error rate strayed up to 15.5 points from 5%. Prefer the score test or the likelihood ratio, or an exact test.
- **Standard errors from a likelihood outside the conditions.** The German tank MLE has no information to invert, and parameters that multiply with the data leave the MLE inconsistent. Check that the support does not move with the parameter, as it does for maxima, thresholds and change points, and count your parameters against your data.
- **χ² for models that are not nested.** Power law against lognormal is not a nested comparison; use Vuong's normalised ratio, read its sign, and expect "cannot tell" from short tails.
- **Trusting the boundary mixture in small samples.** It is a large-sample result: with 50 counts per data set the lab finds 60.1% of likelihood ratios at zero, and the corrected 5% test rejects 3.3%. For variance components the approximation can be worse.
- **Observed and expected information unlabelled.** They agree at a Poisson MLE but not in general: 28.83 against 29.57 for k here. When you report a standard error, say which one it is.

## Key takeaways

- The log-likelihood's peak is the MLE, its curvature there is the information, and one over the information's square root is the standard error: 0.9323 ± 0.0402 hits per square for Clarke's 537 hits on 576 squares.
- Wald measures the horizontal gap, the score test the slope at the null, the likelihood ratio the drop. They agree when the curve is nearly a parabola (4.18, 4.59 and 4.45 for Clarke) and differ when counts are small (6.55, 13.43 and 10.27 for 25 deaths).
- Only Wald changes when the parameter is rewritten. With small counts or skewed parameters, use the likelihood ratio and profile-likelihood intervals: 0.585 to 1.383 for the negative binomial's k, against Wald's symmetric 0.500 to 1.230.
- The likelihood ratio is χ²₁ only for a null inside the parameter space. On a boundary half the data sets give LR = 0, the χ²₁ test rejected 2.17% of true nulls, and the right p-value is half the χ²₁ one.
- Each reference distribution belongs to a condition: χ² inside the parameter space, a χ² mixture on its boundary, a standard normal for non-nested families, and none at all when the support moves with the parameter.

## Try it yourself

**E1, reproduce.** From corps XI's 25 deaths in 20 years and the null rate 0.61, compute the Wald, score and likelihood-ratio statistics with equation (4).

<details><summary>Answer</summary>

m = 20 × 0.61 = 12.2 and T − m = 12.8. Wald = 12.8²/25 = 6.55; score = 12.8²/12.2 = 13.43; LR = 2[25 log(25/12.2) − 12.8] = 2(17.936 − 12.8) = 10.27. The lab prints 6.5536, 13.4295 and 10.2720.

</details>

**E2, inspect.** Clarke's likelihood ratio for overdispersion is 0.41, and P(χ²₁ ≥ 0.41) = 0.522. What p-value should you report, and why?

<details><summary>Answer</summary>

0.261, half of 0.522. The null α = 0 is the boundary of the parameter space, so under it about half the data sets give LR = 0 exactly and the other half follow χ²₁; the probability of a ratio at least 0.41 is half the χ²₁ tail. Fisher's dispersion test, which needs only the Poisson fit, gives a similar 0.24.

</details>

**E3, predict.** Simulate Poisson data sets of 50 counts instead of 576. Before reading on, predict whether the share with LR = 0 rises above or falls below 52.6%, and whether the mixture's 2.71 test then rejects more or less than 5% of true nulls.

<details><summary>Answer</summary>

The share rises, to 60.05% ± 0.35% at Clarke's rate, and the 2.71 test rejects only 3.32% ± 0.13%. The boundary event is Fisher's dispersion statistic falling at or below n; that statistic is close to χ² on n − 1 degrees of freedom, whose median sits below its mean, and with fewer counts the gap is wider. The mixture is a large-sample result, and in small samples it is conservative.

</details>

The lab carries the full ladder, from reproducing these numbers to diagnosing a simulation whose likelihood ratios go negative and building a test for zero inflation, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E5 exercises with answers, and cleanup.
- [`likelihood.py`](LAB_02) — the five stages: poisson, nb, boundary, tank and powerlaw.
- [`requirements.txt`](LAB_03) — the pinned NumPy, SciPy, statsmodels and pandas versions.
- [`clarke1946_flying_bombs.csv`](LAB_04) — Clarke's 576 squares by number of hits, with provenance; put it in a `data` folder.
- [`greenwood_yule1920_accidents.csv`](LAB_05) — Greenwood and Yule's 647 women by number of accidents, with provenance; put it in a `data` folder.
- [`bortkiewicz1898_horse_kicks.csv`](LAB_06) — deaths by horse kick in 14 Prussian corps, one row per corps and year, with provenance; put it in a `data` folder.
- [`captures.json`](LAB_07) — the author's full run, machine-readable, with the private cross-checks against R and the `powerlaw` package.
- [`captures-quick.json`](LAB_08) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_09) — the author's full run as printed.
- [`notebook.ipynb`](LAB_10) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-likelihood-mle-fisher-information.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. R. A. Fisher. "On the mathematical foundations of theoretical statistics." *Philosophical Transactions of the Royal Society A* 222: 309–368, 1922. https://doi.org/10.1098/rsta.1922.0009
2. S. M. Stigler. "The epic story of maximum likelihood." *Statistical Science* 22(4): 598–620, 2007. https://doi.org/10.1214/07-STS249
3. S. S. Wilks. "The large-sample distribution of the likelihood ratio for testing composite hypotheses." *The Annals of Mathematical Statistics* 9(1): 60–62, 1938. https://doi.org/10.1214/aoms/1177732360
4. A. Wald. "Tests of statistical hypotheses concerning several parameters when the number of observations is large." *Transactions of the American Mathematical Society* 54(3): 426–482, 1943. https://doi.org/10.1090/S0002-9947-1943-0012401-3
5. C. R. Rao. "Large sample tests of statistical hypotheses concerning several parameters with applications to problems of estimation." *Mathematical Proceedings of the Cambridge Philosophical Society* 44(1): 50–57, 1948. https://doi.org/10.1017/S0305004100023987
6. A. Buse. "The likelihood ratio, Wald, and Lagrange multiplier tests: an expository note." *The American Statistician* 36(3a): 153–157, 1982. https://doi.org/10.1080/00031305.1982.10482817
7. R. F. Engle. "Wald, likelihood ratio, and Lagrange multiplier tests in econometrics." *Handbook of Econometrics* 2: 775–826, 1984. https://doi.org/10.1016/S1573-4412(84)02005-5
8. A. R. Brazzale and V. Mameli. "Likelihood asymptotics in nonregular settings: a review with emphasis on the likelihood ratio." *Statistical Science* 39(2): 322–345, 2024. https://doi.org/10.1214/23-STS910
9. S. G. Self and K.-Y. Liang. "Asymptotic properties of maximum likelihood estimators and likelihood ratio tests under nonstandard conditions." *Journal of the American Statistical Association* 82(398): 605–610, 1987. https://doi.org/10.1080/01621459.1987.10478472
10. H. Chernoff. "On the distribution of the likelihood ratio." *The Annals of Mathematical Statistics* 25(3): 573–578, 1954. https://doi.org/10.1214/aoms/1177728725
11. J. F. Lawless. "Negative binomial and mixed Poisson regression." *Canadian Journal of Statistics* 15(3): 209–225, 1987. https://doi.org/10.2307/3314912
12. B. Efron and D. V. Hinkley. "Assessing the accuracy of the maximum likelihood estimator: observed versus expected Fisher information." *Biometrika* 65(3): 457–483, 1978. https://doi.org/10.1093/biomet/65.3.457
13. X. Cao. "Relative performance of expected and observed Fisher information in covariance estimation for maximum likelihood estimates." PhD dissertation, arXiv preprint arXiv:1305.1056, 2013. https://arxiv.org/abs/1305.1056
14. L. Le Cam. "Maximum likelihood: an introduction." *International Statistical Review* 58(2): 153–171, 1990. https://doi.org/10.2307/1403464
15. T. R. Fears, J. Bénichou and M. H. Gail. "A reminder of the fallibility of the Wald statistic." *The American Statistician* 50(3): 226–227, 1996. https://doi.org/10.1080/00031305.1996.10474384
16. W. W. Hauck and A. Donner. "Wald's test as applied to hypotheses in logit analysis." *Journal of the American Statistical Association* 72(360a): 851–853, 1977. https://doi.org/10.1080/01621459.1977.10479969
17. G. Molenberghs and G. Verbeke. "Likelihood ratio, score, and Wald tests in a constrained parameter space." *The American Statistician* 61(1): 22–27, 2007. https://doi.org/10.1198/000313007X171322
18. Q. H. Vuong. "Likelihood ratio tests for model selection and non-nested hypotheses." *Econometrica* 57(2): 307–333, 1989. https://doi.org/10.2307/1912557
19. A. Clauset, C. R. Shalizi and M. E. J. Newman. "Power-law distributions in empirical data." *SIAM Review* 51(4): 661–703, 2009. https://doi.org/10.1137/070710111
20. J. Alstott, E. Bullmore and D. Plenz. "powerlaw: a Python package for analysis of heavy-tailed distributions." *PLoS ONE* 9(1): e85777, 2014. https://doi.org/10.1371/journal.pone.0085777
21. R. D. Clarke. "An application of the Poisson distribution." *Journal of the Institute of Actuaries* 72(3): 481, 1946. https://doi.org/10.1017/S0020268100035435
22. M. Greenwood and G. U. Yule. "An inquiry into the nature of frequency distributions representative of multiple happenings with particular reference to the occurrence of multiple attacks of disease or of repeated accidents." *Journal of the Royal Statistical Society* 83(2): 255–279, 1920. https://doi.org/10.2307/2341080
23. L. von Bortkiewicz. *Das Gesetz der kleinen Zahlen*. B. G. Teubner, Leipzig, 1898. https://archive.org/details/dasgesetzderklei00bortrich
24. C. M. Crainiceanu and D. Ruppert. "Likelihood ratio tests in linear mixed models with one variance component." *Journal of the Royal Statistical Society B* 66(1): 165–185, 2004. https://doi.org/10.1111/j.1467-9868.2004.00438.x
25. C. Dean and J. F. Lawless. "Tests for detecting overdispersion in Poisson regression models." *Journal of the American Statistical Association* 84(406): 467–472, 1989. https://doi.org/10.1080/01621459.1989.10478792
26. G. W. Oehlert. "A note on the delta method." *The American Statistician* 46(1): 27–29, 1992. https://doi.org/10.1080/00031305.1992.10475842
27. statsmodels 0.15.0 documentation, `statsmodels.discrete.discrete_model.NegativeBinomial`. https://www.statsmodels.org/stable/generated/statsmodels.discrete.discrete_model.NegativeBinomial.html (accessed 2026-10-28)
28. SciPy 1.18.0 documentation, `scipy.stats.nbinom`. https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html (accessed 2026-10-28)
29. pscl 1.5.9 documentation, `odTest`. https://search.r-project.org/CRAN/refmans/pscl/html/odTest.html (accessed 2026-10-28)
