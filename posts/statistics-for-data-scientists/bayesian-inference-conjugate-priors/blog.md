---
title: "Bayesian Inference by Hand: Conjugacy and Credible Intervals"
slug: bayesian-inference-conjugate-priors
date: 2026-11-25
updated: 2026-11-25
summary: "Laplace's 1.1461 × 10⁻⁴² for Paris births, a vaccine trial's 90.3–97.6 interval rebuilt from its prior, why flat priors are not neutral, and Lindley's paradox."
tags: [data-science, statistics, bayesian-inference, conjugate-prior, credible-interval, bayes-factor, vaccine-efficacy]
category: data-science
series: statistics-for-data-scientists
series_position: 11
tier: L3
difficulty: advanced
prerequisites: ["the likelihood function", "p-values and confidence intervals", "Python with NumPy and SciPy"]
reading_minutes: 33
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/bayesian-inference-conjugate-priors"
---

![Posterior density of the vaccine trial's efficacy after 8 of 170 cases, its 95% credible interval from 90.3% to 97.6% shaded in orange](COVER)

> [!NOTE]
> **Insights** — A posterior is the prior times the likelihood, normalised, and for the binomial, Poisson and normal models it has a closed form. Laplace's uniform prior on the chance that a Paris birth is a boy, updated by 251,527 boys and 241,945 girls, leaves 1.1461 × 10⁻⁴² of probability at or below ½. The Pfizer–BioNTech trial's prior, beta(0.700102, 1), updated by 8 of 170 cases and mapped to efficacy, gives its published 95% credible interval of 90.3% to 97.6% to the decimal. With 170 cases the prior barely matters; with the 4 severe cases, common "uninformative" priors move the lower limit from −155% to −117%. "Flat" always means flat on some scale: uniform on the vaccine group's share of cases puts half the prior probability on a vaccine that does harm. And a single year of Paris births rejects ½ at p = 0.024 while its Bayes factor favours ½ by 8.6 to 1.

**Level:** advanced · **You need:** the likelihood function; p-values and confidence intervals; Python with NumPy and SciPy · **Time:** ~33 min

**Jump to:** [worked example](#worked-example) · [conjugacy](#conjugate-priors-from-the-likelihood-kernel) · [intervals](#credible-intervals-equal-tails-or-highest-density) · [coverage](#what-does-a-credible-interval-promise) · [predictive](#the-posterior-predictive-distribution) · [priors](#how-much-does-the-prior-matter) · [Lindley](#bayes-factors-and-lindley-s-paradox) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **computed** come from its lab: one NumPy and SciPy script whose beta, gamma and binomial calculations are exact, checked against exact integer arithmetic and against R. Two simulated checks print an estimate ± its Monte Carlo standard error (MCSE). Published numbers are **quoted**: Laplace's from his memoirs, the trial's from its paper, protocol and FDA briefing.

## Why this matters

The FDA's briefing on the Pfizer–BioNTech vaccine read the trial's interval of 90.3% to 97.6% as a 97.5% probability that the true efficacy is at least 90.3%. <!-- L16 --> No confidence interval supports that sentence; a credible interval does, but only given a prior. Bayesian answers are often defended as objective once the prior is "flat", which hides the one input a reader should check. A flat prior on one scale is informative on another, and with few events it can decide the answer. This part rebuilds a famous posterior and a regulatory one by hand, then measures what each prior and each summary contributes.

## The problem

Bayesian inference treats an unknown parameter θ as uncertain and describes that uncertainty with a probability distribution. The **prior** p(θ) states it before the data. The **likelihood** p(y | θ), the probability of the observed data as a function of θ, is the object the fourth part of this series, *Likelihood: The MLE, Three Tests, and Where χ² Fails*, built. **Bayes' theorem** combines them into the **posterior**, p(θ | y) ∝ p(y | θ) p(θ), normalised to integrate to 1. Bayes's 1763 essay solved this for a binomial probability under a uniform prior, and Laplace's 1774 memoir gave the first widely read account of it, applied to binomial and location problems. <!-- L07 --> <!-- L06 -->

Three questions follow. How does a prior and a likelihood become a posterior, and when is the answer a formula? What does a 95% interval from the posterior, a **credible interval**, say that a confidence interval cannot? And how much of the answer did the prior supply? This part corrects one claim: **"With a flat prior the Bayesian answer is objective."**

## Worked example

Laplace's question was whether the excess of boys among Paris baptisms could be chance. From 1745 to 1770, 251,527 boys and 241,945 girls were baptised in Paris, about 105 boys to 101 girls. <!-- L01 --> Let x be the probability that a birth is a boy. Laplace took every value of x from 0 to 1 as equally possible beforehand, a uniform prior, so the probability that x is at most ½ is the integral of x^p(1 − x)^q from 0 to ½, divided by the same integral from 0 to 1, with p and q the counts. <!-- L02 --> That ratio is a beta distribution's cumulative distribution function. The **beta distribution** beta(a, b) is the distribution on 0 to 1 with density proportional to x^(a−1)(1 − x)^(b−1). Here the posterior is beta(251,528, 241,946): mean 0.509709, standard deviation (SD) 0.000712, so x = ½ lies 13.64 SDs below the mean (Figure 1).

![Posterior density of the chance that a Paris birth is a boy, beta(251,528, 241,946), on a linear and a log scale; at one half the log10 density is −37.66](FIG_01)
*Figure 1. Laplace's posterior. Its mass at or below ½ is 1.1461 × 10⁻⁴², too small to see on a linear scale.*

The mass at or below ½ is 1.1461 × 10⁻⁴²; exact integer arithmetic, SciPy's beta function and R's agree to nine digits. Laplace had no such integral tables. He expanded the integrand around its maximum and kept the first term of a series, printing a numerator of 1.1521 over the seventh power of a million, 1.1521 × 10⁻⁴². He called that "a little too great" and put the next term at about 1/200 of the first. <!-- L02 --> His first term recomputes to 1.15215 × 10⁻⁴², 0.53% above the exact value, and the second term is 1/186 of it. BDA3 retells the calculation in its chapter on single-parameter models. <!-- L05 --> In his *Théorie analytique* Laplace extended the count to 393,386 boys and 377,555 girls for 1745 to 1784. <!-- L04 --> A 1783 memoir lists the years between, and its yearly rows sum exactly to the difference, 141,859 and 135,610, although the table's printed total row says 151,859 and 145,159. <!-- L03 --> The yearly rows return in the section on Lindley's paradox.

The same machinery carries a modern trial. In the phase 3 trial of the Pfizer–BioNTech vaccine BNT162b2, participants without prior infection had 8 cases of Covid-19 from 7 days after the second dose in the vaccine group and 162 in the placebo group. They were followed for 2.214 and 2.222 thousand person-years, the **surveillance time**. <!-- L08 --> **Vaccine efficacy** is VE = 1 − IRR, where the **incidence rate ratio** IRR is the vaccine group's case rate per 1,000 person-years over the placebo group's. <!-- L09 --> Given the 170 cases, the vaccine group's share θ is binomial, and θ = r · IRR/(1 + r · IRR), with r = 2.214/2.222 = 0.9964 the ratio of surveillance times. At r = 1 this is the protocol's θ = (1 − VE)/(2 − VE).

The protocol put a beta(0.700102, 1) prior on θ, called it minimally informative, and centred it at θ = 0.4118, the share at VE = 30%, which it called pessimistic. <!-- L12 --> The odd constant has a source. Senn notes that the first parameter is quoted to six figures and the second to one; a referee's rule he reports gives the least informative unimodal beta with a given mean p of at most ½ as beta(p/(1 − p), 1). <!-- L18 --> <!-- L19 --> With p rounded to 0.4118, 0.4118/0.5882 = 0.700102 to six figures.

Conjugacy does the update: the posterior is beta(0.700102 + 8, 1 + 162) = beta(8.700102, 163) (Figure 2). Its 2.5% and 97.5% quantiles map through VE = 1 − θ/((1 − θ)r) to 90.317% and 97.617%, the published 90.3% to 97.6%. The paper reports a posterior probability above 0.9999 that VE exceeds 30%, with the final analysis's success boundary at 98.6%. <!-- L08 --> <!-- L10 --> The computed shortfall is P(VE ≤ 30%) = 2.46 × 10⁻²⁸. The headline efficacy, 95.0%, is not a posterior summary but the rate-ratio estimate 1 − (8/2.214)/(162/2.222); the posterior median is 94.8%.

![Left: the trial's beta(0.700102, 1) prior on the vaccine group's share of cases. Right: the posterior density of vaccine efficacy with its 95% credible interval, 90.3% to 97.6%](FIG_02)
*Figure 2. Prior to posterior. The prior puts 38% of its probability on a vaccine that does harm; 170 cases leave little of it.*

## Intuition

A beta prior behaves like data already seen. Beta(a, b) contributes a + b **pseudo-counts**: the trial's prior is worth 1.700102 cases, of which 0.700102 fell in the vaccine group. The posterior mean of θ is then a weighted average of the prior mean and the observed share, with the prior's weight (a + b)/(a + b + n). For the primary endpoint that weight is 1.7/171.7 = 0.0099, so the posterior mean, 0.050670, is 0.0099 × 0.4118 + 0.9901 × 0.047059: the data's share, nudged.

The FDA's briefing also reports a 4-case endpoint: first severe Covid-19 from 7 days after the second dose, 1 case in the vaccine group and 3 in the placebo group, with a credible interval of −124.8% to 96.3% from the same prior. <!-- L16 --> The lab reproduces it to the decimal. Here the prior keeps 1.7/5.7 = 29.8% of the weight, and the posterior sits visibly between prior and likelihood (Figure 3). A posterior is a compromise weighted by counts, so the same prior is negligible in one analysis and decisive in the next.

![Prior, scaled likelihood and posterior for the vaccine group's share of cases, with 1 against 3 cases and with 8 against 162](FIG_03)
*Figure 3. With 4 cases the prior keeps 30% of the weight on the posterior mean; with 170 it keeps 1%.*

## Conjugate priors from the likelihood kernel

A prior family is **conjugate** to a likelihood when every posterior stays in the family. <!-- L23 --> The test is the **kernel**, the part of a density that depends on the parameter. A binomial likelihood has kernel θ^y(1 − θ)^(n−y), and a beta(a, b) prior has kernel θ^(a−1)(1 − θ)^(b−1); their product is the beta(a + y, b + n − y) kernel. The normalising constant, the **marginal likelihood** p(y), is the integral of likelihood times prior. For 8 of 170 under the trial's prior it is 0.0101302, by quadrature and by the closed form C(n, y) B(a + y, b + n − y)/B(a, b) alike.

Counts with exposure work the same way. If y cases occur in t thousand person-years at a rate λ, the Poisson kernel is λ^y e^(−λt), and a gamma prior with shape α and rate β, kernel λ^(α−1) e^(−βλ), gives a gamma(α + y, β + t) posterior. <!-- L25 --> With Jeffreys' prior for a rate, proportional to λ^(−1/2), the vaccine arm's posterior is gamma(8.5, 2.214), mean 3.84 cases per 1,000 person-years (95% interval 1.71 to 6.82), and the placebo arm's is gamma(162.5, 2.222), mean 73.13 (62.32 to 84.80) (Figure 4a). The two arms reconnect to the trial's model by conditioning on the total. Two independent gamma variables with a common rate parameter have a beta-distributed share, so gamma priors on the two arms' expected counts with shapes 0.700102 and 1 and any common rate give exactly the trial's beta(8.700102, 163); the lab confirms it by simulation. Under the Jeffreys rate priors the share is beta(8.5, 162.5), and VE runs from 90.46% to 97.69%. "Adjusted for surveillance time" is the exposure, entering through r.

For a normal mean with known variance and a normal prior, the posterior is normal, its precision (the reciprocal of its variance) is the sum of the two precisions, and its mean is the precision-weighted average of the prior mean and the data. <!-- L24 --> Laplace's years give a check. The 1745–1770 posterior is close to normal, with mean 0.509709 and SD 0.000712. The 1782 baptisms alone, 9,851 boys of 19,387, give 0.50812 with standard error 0.00359. The prior carries 96.2% of the precision, and the posterior is 0.509649 ± 0.000698: the exact beta update on the pooled counts, to six decimals (Figure 4b). Updating year by year and updating once on the pooled data give the same posterior.

![Posteriors of the two trial arms' case rates per 1,000 person-years, and a normal prior from 1745-1770 combined with the 1782 baptisms by precision weights](FIG_04)
*Figure 4. Gamma–Poisson for rates and normal–normal for means. Yesterday's posterior is today's prior.*

All three are instances of one result: for an exponential family, conjugate priors are exactly those under which the posterior mean is linear in the data. <!-- L26 --> Conjugacy is a convenience, not a requirement; posteriors with no closed form are sampled, the subject of the next part of this series.

## Credible intervals: equal tails or highest density?

A 95% posterior interval can be chosen two ways. The **equal-tailed** interval runs between the 2.5% and 97.5% posterior quantiles. The **highest-density interval** (HDI) is the shortest interval holding 95%, with every point inside denser than any point outside. <!-- L21 --> <!-- L22 --> They coincide for a symmetric unimodal posterior and part company under skew.

For the trial's primary endpoint the equal-tailed interval is 90.3% to 97.6% and the HDI of VE is 90.9% to 97.9%. Only the first reproduces the published interval, so the trial reported equal tails. The choice matters more than it looks, because the HDI depends on the scale it is computed on. Mapping the shortest interval for θ to the VE scale gives 90.8% to 97.9%, not the HDI of VE: shortness is not preserved by a nonlinear map, while quantiles are. For the 4 severe cases the three answers diverge (Figure 5): −124.8% to 96.3% with equal tails, −69.7% to 99.9% as the HDI of VE, and −73.5% to 99.1% as the HDI of θ, mapped.

![Posterior densities of efficacy for 1 against 3 and 8 against 162 cases, with the equal-tailed interval and two highest-density intervals drawn as bars under each](FIG_05)
*Figure 5. The published intervals are the equal-tailed ones. The shortest interval on one scale is not the shortest on another.*

The FDA's sentence depends on the choice. Equal tails leave exactly 2.5% of the posterior below the lower limit, so "at least 90.3% with probability 97.5%" is true of the published interval. Below the lower limit of the HDI of VE lies 3.9% of the posterior, so the same sentence about the HDI would claim 97.5% where the posterior gives 96.1%.

## What does a credible interval promise?

A 95% credible interval contains θ with posterior probability 0.95 given this data set, this model and this prior. It says nothing about what happens when the trial is repeated at a fixed true efficacy. A confidence interval promises the reverse: it contains the true value at least 95% of the time at every true value, and says nothing about this data set. <!-- L32 --> The sixth part of this series, *Confidence Intervals: What 95% Means, Measured*, measured that promise for binomial intervals. The same calculation applies to the trial's credible interval: fix the true VE, sum the binomial probabilities of every split whose credible interval contains it.

With 170 cases the credible interval's exact coverage stays between 92.9% and 96.5% for true efficacies from 0% to 95%, where the Clopper–Pearson interval, the exact binomial confidence interval, holds 95.1% to 98.0% (Figure 6a). In large samples a central posterior interval covers at about its nominal rate at every fixed value. <!-- L32 --> With 4 cases the coverage ranges from 91.7% to 100% over the same efficacies and falls to 86.6% at VE 96.3% (Figure 6b), where the Clopper–Pearson interval never drops below 97.5%.

![Exact coverage of the trial's 95% credible interval and of the Clopper-Pearson interval against the true efficacy, for 170 cases and for 4](FIG_06)
*Figure 6. 95% on average over the prior, not at every true value.*

The credible interval's own guarantee is an average. Draw θ from the prior, data from θ, and the interval contains θ with probability exactly 0.95, because for each data set it holds 95% of that data set's posterior. The lab's quadrature gives 95.000000% for both case counts, and simulation gives 95.01% ± 0.03 and 95.03% ± 0.03 (S = 400,000 draws each). This identity is how Bayesian software is tested: Cook, Gelman and Rubin simulate parameters from the prior and check that the true values' posterior quantiles are uniform. <!-- L34 --> The guarantee holds for a reader whose beliefs match the prior; a regulator who wants error rates at a fixed truth needs the frequentist calculation, which is why Brown, Cai and DasGupta recommend the equal-tailed Jeffreys interval for small binomial samples on coverage grounds. <!-- L33 -->

The trial needed both. Its protocol calibrated the 99.5% and 98.6% thresholds so that a vaccine with VE exactly 30% would be declared a success with overall probability at most 2.5%. <!-- L15 --> The lab reproduces the protocol's **operating characteristics**, the frequentist probabilities of success and failure at each analysis for a given true VE, in 44 of their 45 printed entries, 0.021 overall at VE 30%. The exception, an overall probability of success above 0.999 at VE 70%, is 0.994, the sum of the table's own columns.

## The posterior predictive distribution

The **posterior predictive distribution** describes future data: the probability of a new observation, averaged over the posterior. For one more birth under Laplace's posterior it is the posterior mean, (y + 1)/(n + 2) = 251,528/493,474 = 0.509709, the rule BDA3 calls Laplace's law of succession. <!-- L05 --> For m future binomial trials it is the **beta-binomial distribution**, a binomial whose probability is itself beta-distributed, wider than any binomial with a fixed probability.

The trial's protocol used it as a stopping rule. It planned **interim analyses**, looks at the accumulating cases before the planned end, after 32, 62, 92 and 120 cases, and a final analysis at 164. At each it declared success if P(VE > 30%) exceeded 0.995 (0.986 at the final). It would stop for **futility**, for lack of benefit, if the predicted probability of success at the final analysis, a beta-binomial posterior predictive probability, fell below 5%. <!-- L13 --> <!-- L14 --> Recomputed from the prior, the success boundaries are at most 6, 15, 25, 35 and 53 vaccine cases. At 164 cases the posterior probability is 0.9904 with 53 vaccine cases and 0.9853 with 54, either side of 0.986. These are the protocol's Table 6, entry for entry. <!-- L13 -->

The futility boundaries come from the predictive. With 15 of the first 32 cases in the vaccine group, success at 164 needs at most 38 of the next 132. Under beta(15.700102, 18) the predictive probability of that is 3.11%, so the trial would stop; with 14, at most 39 are needed, with probability 7.19% (Figure 7a). The same calculation gives the protocol's boundaries of 26 at 62 cases and 35 at 92 (Figure 7b). The first interim analysis was never run. <!-- L13 -->

![Beta-binomial predictive distributions of future vaccine cases after 14 and 15 of 32, and the predictive probability of final success against the cases so far](FIG_07)
*Figure 7. The futility rule is a posterior predictive probability, and it reproduces the protocol's boundaries.*

## How much does the prior matter?

**Prior sensitivity** is the change in the answer as the prior changes, and it is measured, not assumed. Five priors on θ, the trial's, Senn's beta(1, 1.428363) with the same mean, the uniform beta(1, 1), Jeffreys' beta(½, ½) and Haldane's beta(0, 0), move the primary endpoint's lower limit only from 90.1% to 90.9%. <!-- L18 --> For the 4 severe cases the same five move it from −154.6% to −116.6%. A **sceptical prior**, one centred on no effect, shows the other side of the trade (Figure 8). Centred at VE 0% and worth 170 cases, as many as the data, it puts the primary interval at 52.3% to 70.4%.

![Credible interval of efficacy against the prior's weight in cases, for priors centred at VE 30% and at VE 0%, for the primary and the severe endpoints](FIG_08)
*Figure 8. 170 cases outvote a light prior; 4 cases do not.*

"Flat" does not settle the choice, because flatness belongs to a scale. Uniform on θ becomes the logistic density on the log-odds of θ, which at r = 1 is the log of the incidence rate ratio: a hill centred on no effect (Figure 9). On the VE scale the same prior gives P(VE ≤ 0) = ½ and P(VE > 90%) = 1/11. The trial's "minimally informative" prior puts 38.4% of its probability on harm and spreads its 95% prior interval for VE from −2,616% to 99.5%, as the protocol's −26.2 to 0.995 says in fractions. <!-- L12 --> Its mean of θ maps to VE 30% while its median maps to VE 40.9%. As Senn points out, a mean does not survive a nonlinear transformation, though a median does, and a prior centred on the efficacy bar describes the bar, not a belief. <!-- L18 --> <!-- L20 -->

![Uniform, Jeffreys and the trial's priors as densities of the vaccine group's share and of its log-odds, with Haldane's improper flat prior on the log-odds](FIG_09)
*Figure 9. Flat on θ is a hill on the log-odds.*

Jeffreys proposed a rule that does not depend on the scale: take the prior proportional to the square root of the Fisher information, so that applying the rule after a reparameterisation gives the prior transformed from the original. <!-- L28 --> <!-- L27 --> For the binomial that is beta(½, ½), and the lab confirms the invariance on the log-odds to machine precision. Invariance is not neutrality. Haldane's beta(0, 0), flat on the log-odds, is improper and yields an improper posterior when there are no events in one group. <!-- L27 --> With zero events, beta parameters below 1, Jeffreys' ½ and the trial's 0.700102 among them, concentrate mass near 0 and pull the posterior there. <!-- L30 --> Kass and Wasserman's review concludes that no default prior can be trusted when the sample is small relative to the parameters, and Gelman, Simpson and Betancourt argue that a prior can often only be read in the context of its likelihood. <!-- L29 --> <!-- L31 --> The claim this part corrects fails twice: flatness depends on the parameterisation, and the prior's effect has to be checked, as Figure 8 does.

## Bayes factors and Lindley's paradox

Estimation asks where θ is. Testing a **point null hypothesis**, here H0: x = ½ exactly, asks whether a special value holds, and the Bayesian tool is the **Bayes factor**, BF01 = p(y | H0)/p(y | H1), the ratio of the two hypotheses' marginal likelihoods. It equals the posterior odds of H0 when H0 has prior probability ½. <!-- L38 --> Under a uniform alternative it is exact: BF01 = (n + 1) C(n, y)/2ⁿ.

Take the 1782 Paris baptisms alone: 9,851 boys of 19,387 births, a share of 0.5081. The standardised excess is z = (9,851 − 9,536)/√19,387 = 2.262, and the exact two-sided binomial test of ½ gives p = 0.0241, a rejection at 5%. The Bayes factor is 8.60 in favour of ½, a posterior probability of H0 of 0.896 at even prior odds. In four of the fourteen years from 1771 to 1784, 1772, 1778, 1779 and 1782, the test rejects ½ at the 5% level while the data favour ½ (Figure 10). This is **Lindley's paradox**. In 1957 Lindley gave an example in which a result is significant at 5% while the posterior probability of the null, even from a small prior probability, is as high as 95%, and concluded that 5% in a small sample does not mean what 5% means in a large one. <!-- L35 --> Bartlett corrected a missing factor in his formula the same year. <!-- L36 --> Jeffreys had derived the conflict from 1935 on: the evidence for a point null grows like √n, so no fixed multiple of the standard error can serve as an evidence threshold. <!-- L37 --> For even evidence he gave t² = ln(2n/π). <!-- L37 --> At 19,387 births that is z = 3.069, where the 5% test uses 1.96.

![Exact p-value against the Bayes factor for one half, for each year of Paris baptisms 1771 to 1784; four years reject at 5% while the Bayes factor exceeds 1](FIG_10)
*Figure 10. Four years reject ½ at the 5% level while the data favour ½.*

The paradox lives in the alternative's prior. A uniform x spreads H1's prediction across every share from 0 to 1, so data near 0.508 are more probable under exactly ½ than under "anything". Edwards, Lindman and Savage put it as a sharp null against a diffuse alternative. <!-- L39 --> Change H1's prior and the factor changes (Figure 11a). Symmetric beta(κ/2, κ/2) priors around ½ take BF01 from 8.60 at κ = 2 down to 0.289 near κ = 5,000 and back toward 1. The 1745–1770 posterior as H1's prior gives BF01 = 1/11.54, evidence against ½. No prior can push it below 1/12.93, the likelihood ratio at the observed share. Berger and Sellke show the same gap for a normal mean: p = 0.05 leaves the null a posterior probability of at least 0.30 under any objective prior. <!-- L40 --> At a fixed z the uniform-alternative factor grows like √n (Figure 11b): at z = 2.262 it passes 1 at n = 260 and 19, a posterior probability of 0.95, at n = 94,708.

![Bayes factor for the 1782 baptisms against the concentration of a symmetric beta prior, and against the number of births at a fixed z](FIG_11)
*Figure 11. The Bayes factor depends on the alternative's prior and, at a fixed z, on n.*

The posterior for estimation is far less fragile. Under the uniform prior the 1782 posterior gives P(x ≤ ½) = 0.0118 and a 95% credible interval of 0.5011 to 0.5152; any continuous prior gives the single value ½ probability zero, so estimation never asks the paradox's question. The two schools agree on the pooled years: from 1771 to 1784 the boys' excess gives z = 11.86 and log10 BF01 = −27.9. A Bayes factor answers a different question from a posterior, and it inherits the alternative's prior in full. Robert reads the paradox also as a warning about improper priors in tests. <!-- L41 -->

## The math

| Symbol | Meaning |
|---|---|
| θ, x | the vaccine group's share of cases; the probability that a birth is a boy |
| a, b | beta shapes; a + b is the prior's weight in pseudo-counts |
| y, n | events and trials (vaccine cases and all cases; boys and births) |
| t, r | surveillance time in 1,000 person-years; its vaccine-to-placebo ratio |
| I(θ), m | Fisher information; future trials in a predictive |

**Beta–binomial updating** and the trial's map from share to efficacy:

$$
\theta \mid y \sim \mathrm{Beta}(a + y,\ b + n - y), \qquad \mathrm{VE} = 1 - \frac{\theta}{(1 - \theta)\,r} \tag{1}
$$

With a = 0.700102, b = 1, y = 8 and n = 170, the quantiles of beta(8.700102, 163) map to 90.317% and 97.617%; because the map is decreasing, the upper quantile of θ gives the lower limit of VE.

**Gamma–Poisson with exposure**, for y events in exposure t: <!-- L25 -->

$$
\lambda \sim \mathrm{Gamma}(\alpha, \beta) \ \Rightarrow\ \lambda \mid y \sim \mathrm{Gamma}(\alpha + y,\ \beta + t) \tag{2}
$$

With α = ½ and β = 0, the vaccine arm's posterior is gamma(8.5, 2.214), mean 8.5/2.214 = 3.84 cases per 1,000 person-years.

**Normal–normal**, with prior N(μ₀, τ₀²) and an observed mean ȳ with standard error σ:

$$
\mu \mid \bar y \sim \mathrm{N}\!\left(\frac{\mu_0/\tau_0^2 + \bar y/\sigma^2}{1/\tau_0^2 + 1/\sigma^2},\ \frac{1}{1/\tau_0^2 + 1/\sigma^2}\right) \tag{3}
$$

For 1782 after 1745–1770 the prior's share of the precision is 0.962, and the posterior is 0.509649 ± 0.000698.

**The posterior predictive** for m future trials is beta-binomial:

$$
P(\tilde y = k \mid y) = \binom{m}{k} \frac{B(a + y + k,\ b + n - y + m - k)}{B(a + y,\ b + n - y)} \tag{4}
$$

The protocol's futility check at 32 cases is the sum of (4) over k from 0 to 53 − y with m = 132: 3.11% at y = 15.

**Jeffreys' prior** for a binomial share, from the Fisher information n/(θ(1 − θ)): <!-- L27 -->

$$
p_J(\theta) \propto \sqrt{I(\theta)} \propto \theta^{-1/2}(1 - \theta)^{-1/2} \tag{5}
$$

That is beta(½, ½); for a Poisson rate, with I(λ) = 1/λ, the same rule gives λ^(−1/2).

**The Bayes factor** against a point null at ½ with a uniform alternative:

$$
\mathrm{BF}_{01} = \frac{\binom{n}{y} 2^{-n}}{\int_0^1 \binom{n}{y} x^{y}(1 - x)^{n-y}\,dx} = \frac{(n + 1)\binom{n}{y}}{2^{n}} \tag{6}
$$

For 1782, n = 19,387 and y = 9,851 give 8.60; by Stirling's formula BF01 ≈ √(2n/π) e^(−z²/2), the √n growth of Figure 11b.

## Implementation

The worked example's numbers in SciPy. Run as printed, it gives Laplace's tail, the trial's interval and boundaries, and the 1782 Bayes factor.

```python
import numpy as np
from scipy import special, stats

post = stats.beta(251527 + 1, 241945 + 1)                    # Laplace: uniform prior, Paris 1745-1770
print("P(x <= 1/2):", post.cdf(0.5))                         # 1.146e-42

a0, b0 = 0.700102, 1.0                                       # the protocol's prior on theta = (1 - VE)/(2 - VE)
yv, yp, tv, tp = 8, 162, 2.214, 2.222                        # cases and thousand person-years
r = tv / tp
ve = lambda t: 1 - t / ((1 - t) * r)                         # share -> efficacy, adjusted for surveillance time
theta = stats.beta(a0 + yv, b0 + yp)
print("VE 95% credible interval:", ve(theta.ppf([0.975, 0.025])))
print("P(VE <= 30%):", theta.sf(0.7 * r / (1 + 0.7 * r)))

print("final boundary:", [stats.beta(a0 + x, b0 + 164 - x).cdf(0.7 / 1.7) for x in (53, 54)])
print("POS with 15 of 32:", stats.betabinom(164 - 32, a0 + 15, b0 + 32 - 15).cdf(53 - 15))

n, y = 19387, 9851                                           # Paris 1782
log_bf01 = np.log(n + 1) + special.gammaln(n + 1) - special.gammaln(y + 1) - special.gammaln(n - y + 1) - n * np.log(2)
print("BF01:", np.exp(log_bf01), "| p:", stats.binomtest(y, n, 0.5).pvalue)
```

It prints 1.146e-42; 0.90317 and 0.97617; 2.46e-28; 0.9904 and 0.9853, either side of the 0.986 threshold; a POS of 0.0311; and a Bayes factor of 8.597 beside p = 0.0241. The line that most often goes wrong is the efficacy map. Without r the lower limit prints 90.352, which rounds to 90.4, not the published 90.3.

### Reading the library's output

SciPy and R parameterise these distributions differently, and the defaults decide answers. <!-- L42 --> <!-- L43 -->

| Task | SciPy 1.18.1 | R 4.5.2 |
|---|---|---|
| beta posterior | `stats.beta(a, b)`, computed by Boost | `pbeta`, `qbeta`: TOMS 708, inverted after AS 109 |
| gamma posterior for a rate | `stats.gamma(shape, scale=1/rate)`: the second argument is a scale | `qgamma(p, shape, rate)`: rate, 1 by default |
| beta-binomial predictive | `stats.betabinom(m, a, b)` | none in base R: `lchoose` plus `lbeta` |
| equal-tailed interval | `.interval(0.95)` or `.ppf([0.025, 0.975])` | `qbeta(c(0.025, 0.975), a, b)` |
| exact binomial test | `stats.binomtest(y, n, 0.5)` | `binom.test(y, n, 0.5)` |

The gamma row is the trap. Passing the posterior rate 2.214 as SciPy's `scale` multiplies the vaccine arm's rate by 2.214² instead of dividing; check any gamma posterior's mean against shape/rate. R agrees with SciPy on the intervals, tail probabilities, trial boundaries and Bayes factors here to the digits it prints. The lab's `bayes.py` computes all of it in six stages; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** calling a flat prior objective. Uniform on the vaccine group's share is a hill on the log-odds and gives a harmful vaccine prior probability ½; the trial's "minimally informative" prior gives it 38.4%. With 170 cases it does not matter; with 4 cases, five common priors moved the lower limit by 38 points. Report the prior, and show how the answer moves when it changes.

- **A highest-density interval carried across scales.** The HDI of θ, mapped to VE, is not the HDI of VE, and neither carries the one-sided 97.5% reading the equal-tailed interval allows.
- **A credible interval read as a confidence interval.** Its 95% is an average over the prior. At a fixed true efficacy, 4 cases gave coverage as low as 86.6%. The trial's own paper calls the credible interval a "95% confidence interval" once, in its efficacy results, which Senn reads as a typographical error. <!-- L11 -->
- **A Bayes factor from a vague alternative.** It favours the null more the vaguer the alternative's prior, so state that prior and vary it. Improper priors cannot be used.
- **Ignoring exposure.** The efficacy map needs the surveillance-time ratio: dropped, it moves the severe-case interval from −124.8% to −123.1%.
- **Trusting one printed threshold.** The FDA briefing gives the final-analysis criterion as 99.5% in its text and as 98.6% in one table; the protocol and the paper say 98.6%. <!-- L17 -->
- **A conjugate prior chosen for convenience.** Conjugacy buys a closed form, not a justified prior; when the prior matters, choose it for its content and check it.

## Key takeaways

- A posterior is prior × likelihood, normalised; with a conjugate prior it is a formula. Laplace's uniform prior and 493,472 Paris births give 1.1461 × 10⁻⁴² at or below ½, within 0.53% of his 1781 first-term estimate of 1.1521 × 10⁻⁴².
- The trial's published interval rebuilds by hand: beta(0.700102, 1) plus 8 of 170 cases is beta(8.700102, 163), mapped with the surveillance ratio to 90.3% to 97.6%; the protocol's success and futility boundaries follow from the same posterior and its predictive.
- A credible interval is a probability statement given a prior. Its 95% holds exactly on average over the prior and only approximately at a fixed truth: 92.9% to 96.5% with 170 cases, down to 86.6% with 4.
- Flatness depends on the scale. Uniform on θ gives P(VE ≤ 0) = ½; Jeffreys' rule is invariant but not neutral, and with few or no events every default prior shows in the answer.
- A Bayes factor tests a point null and depends on the alternative's prior: Paris in 1782 rejects ½ at p = 0.024, while BF01 is 8.60 under a uniform alternative and 1/11.54 under the earlier years' posterior.

## Try it yourself

**E1, reproduce.** From the protocol's prior and the primary split, 8 vaccine cases and 162 placebo cases, write the posterior of θ and compute its mean. Show that it is the weighted average of the prior mean and the observed share, with the prior weight (a + b)/(a + b + n).

<details><summary>Answer</summary>

**Answer.** The posterior is beta(8.700102, 163), with mean 8.700102/171.700102 = 0.050670. The prior mean is 0.700102/1.700102 = 0.4118 and the observed share 8/170 = 0.047059; the prior weight is 1.700102/171.700102 = 0.009902. Then 0.009902 × 0.4118 + 0.990098 × 0.047059 = 0.050670.

</details>

**E2, inspect.** Show that beta(p/(1 − p), 1) has mean p, and use it to explain the constant 0.700102.

<details><summary>Answer</summary>

**Answer.** A beta(a, 1) has mean a/(a + 1). With a = p/(1 − p), a + 1 = 1/(1 − p), so the mean is p. The protocol targets θ at VE = 30%, which is 0.7/1.7 = 0.411765; rounded to 0.4118, a = 0.4118/0.5882 = 0.700102006, printed to six figures as 0.700102. Unrounded, a would be exactly 0.7.

</details>

**E3, predict.** In the trial's subgroup aged 75 or over, 0 vaccine and 5 placebo cases occurred over 0.102 and 0.106 thousand person-years. Before running the lab's `priors` stage on this split, predict which of the five priors (trial, Senn's, uniform, Jeffreys, Haldane) gives the highest lower limit for VE, and which gives no answer at all.

<details><summary>Answer</summary>

**Answer.** Haldane's beta(0, 0) gives no answer: with no vaccine cases the posterior beta(0, 5) is improper. Jeffreys' beta(½, ½) gives the highest lower limit, 36.5%, because its first parameter below 1 piles prior mass near θ = 0, which is VE near 100%. The trial's prior gives 29.9% to 99.9%, Senn's 19.5% to 99.6% and the uniform 11.7% to 99.6%. The ordering follows the first beta parameter, ½, 0.700102 and 1, then the second. The lab prints them with `python bayes.py priors --split 0 5 --times 0.102 0.106`.

</details>

The lab's README has these and a fourth exercise, which diagnoses an efficacy map that drops the surveillance time.

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E4 exercises with answers, and cleanup.
- [`bayes.py`](LAB_02) — the six stages: laplace, pfizer, conjugate, intervals, priors and lindley.
- [`paris_baptisms_1745_1784.csv`](LAB_03) — Laplace's Paris baptisms by sex, 1745–1770, each year 1771–1784, and 1745–1784, with provenance; put it in a `data` folder.
- [`bnt162b2_bayesian_rows.csv`](LAB_04) — the trial's case splits and surveillance times behind its published credible intervals, with sources; put it in a `data` folder.
- [`requirements.txt`](LAB_05) — the pinned NumPy and SciPy versions.
- [`captures.json`](LAB_06) — the author's full run, machine-readable, with the private cross-check against R.
- [`captures-quick.json`](LAB_07) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_08) — the author's full run as printed.
- [`notebook.ipynb`](LAB_09) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-bayesian-inference-conjugate-priors.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. P.-S. Laplace. "Mémoire sur les probabilités." *Mémoires de l'Académie royale des sciences de Paris*, année 1778 (1781). English translation by R. J. Pulskamp, 2010. https://gtfp.cs.rhul.ac.uk/pulskamp/Laplace/memoir_probabilities.pdf (accessed 2026-11-25)
2. P.-S. Laplace. "Sur les naissances, les mariages et les morts à Paris, depuis 1771 jusqu'en 1784." *Mémoires de l'Académie royale des sciences de Paris* 1783: 693–702. Translation by R. J. Pulskamp. https://gtfp.cs.rhul.ac.uk/pulskamp/Laplace/naissances.pdf (accessed 2026-11-25)
3. P.-S. Laplace. *Théorie analytique des probabilités*, 3rd edition, Book II, chapter VI. Paris: Courcier, 1820 (first edition 1812). Translation by R. J. Pulskamp. https://gtfp.cs.rhul.ac.uk/pulskamp/Laplace/TAP/TAP_book2_chap6.pdf (accessed 2026-11-25)
4. S. M. Stigler. "Laplace's 1774 memoir on inverse probability." *Statistical Science* 1(3): 359–363, 1986. https://doi.org/10.1214/ss/1177013620
5. T. Bayes. "An essay towards solving a problem in the doctrine of chances." *Philosophical Transactions of the Royal Society* 53: 370–418, 1763. https://doi.org/10.1098/rstl.1763.0053
6. F. P. Polack et al. "Safety and efficacy of the BNT162b2 mRNA Covid-19 vaccine." *New England Journal of Medicine* 383(27): 2603–2615, 2020. https://doi.org/10.1056/NEJMoa2034577
7. Pfizer and BioNTech. Protocol C4591001, Amendment 9, 29 October 2020, §9.5; supplementary appendix to source 6. https://www.ebi.ac.uk/europepmc/webservices/rest/PMC7745181/supplementaryFiles (accessed 2026-11-25)
8. U.S. Food and Drug Administration. *FDA Briefing Document: Pfizer-BioNTech COVID-19 Vaccine.* Vaccines and Related Biological Products Advisory Committee, 10 December 2020. https://www.fda.gov/media/144245/download (accessed 2026-11-25)
9. S. Senn. "The design and analysis of vaccine trials for COVID-19 for the purpose of estimating efficacy." *Pharmaceutical Statistics* 21(4): 790–807, 2022. https://doi.org/10.1002/pst.2226
10. A. Gelman, J. B. Carlin, H. S. Stern, D. B. Dunson, A. Vehtari and D. B. Rubin. *Bayesian Data Analysis*, 3rd edition. CRC Press, 2013. https://doi.org/10.1201/b16018
11. H. Jeffreys. "An invariant form for the prior probability in estimation problems." *Proceedings of the Royal Society of London A* 186(1007): 453–461, 1946. https://doi.org/10.1098/rspa.1946.0056
12. R. E. Kass and L. Wasserman. "The selection of prior distributions by formal rules." *Journal of the American Statistical Association* 91(435): 1343–1370, 1996. https://doi.org/10.1080/01621459.1996.10477003
13. F. Tuyl, R. Gerlach and K. Mengersen. "A comparison of Bayes–Laplace, Jeffreys, and other priors: the case of zero events." *The American Statistician* 62(1): 40–44, 2008. https://doi.org/10.1198/000313008X267839
14. A. Gelman, D. Simpson and M. Betancourt. "The prior can often only be understood in the context of the likelihood." *Entropy* 19(10): 555, 2017. https://doi.org/10.3390/e19100555
15. P. Diaconis and D. Ylvisaker. "Conjugate priors for exponential families." *The Annals of Statistics* 7(2): 269–281, 1979. https://doi.org/10.1214/aos/1176344611
16. R. J. Hyndman. "Computing and graphing highest density regions." *The American Statistician* 50(2): 120–126, 1996. https://doi.org/10.1080/00031305.1996.10474359
17. L. D. Brown, T. T. Cai and A. DasGupta. "Interval estimation for a binomial proportion." *Statistical Science* 16(2): 101–133, 2001. https://doi.org/10.1214/ss/1009213286
18. S. R. Cook, A. Gelman and D. B. Rubin. "Validation of software for Bayesian models using posterior quantiles." *Journal of Computational and Graphical Statistics* 15(3): 675–692, 2006. https://doi.org/10.1198/106186006X136976
19. D. V. Lindley. "A statistical paradox." *Biometrika* 44(1–2): 187–192, 1957. https://doi.org/10.1093/biomet/44.1-2.187
20. M. S. Bartlett. "A comment on D. V. Lindley's statistical paradox." *Biometrika* 44(3–4): 533–534, 1957. https://doi.org/10.1093/biomet/44.3-4.533
21. E.-J. Wagenmakers and A. Ly. "History and nature of the Jeffreys–Lindley paradox." *Archive for History of Exact Sciences* 77(1): 25–72, 2023. https://doi.org/10.1007/s00407-022-00298-3
22. R. E. Kass and A. E. Raftery. "Bayes factors." *Journal of the American Statistical Association* 90(430): 773–795, 1995. https://doi.org/10.1080/01621459.1995.10476572
23. W. Edwards, H. Lindman and L. J. Savage. "Bayesian statistical inference for psychological research." *Psychological Review* 70(3): 193–242, 1963. https://doi.org/10.1037/h0044139
24. J. O. Berger and T. Sellke. "Testing a point null hypothesis: the irreconcilability of P values and evidence." *Journal of the American Statistical Association* 82(397): 112–122, 1987. https://doi.org/10.1080/01621459.1987.10478397
25. C. P. Robert. "On the Jeffreys–Lindley paradox." *Philosophy of Science* 81(2): 216–232, 2014. https://doi.org/10.1086/675729
26. SciPy 1.18.1 source, `scipy.stats` distributions `gamma`, `beta` and `betabinom`. https://github.com/scipy/scipy/blob/main/scipy/stats/_continuous_distns.py (accessed 2026-11-25)
27. R Core Team. R 4.5.2 documentation: `Beta` and `GammaDist`. https://stat.ethz.ch/R-manual/R-patched/library/stats/html/Beta.html (accessed 2026-11-25)
