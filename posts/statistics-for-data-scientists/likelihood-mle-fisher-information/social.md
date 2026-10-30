---
social_schema: 2
canonical_url: "https://canery.in/blogs/likelihood-mle-fisher-information"
---

# Social publishing package — likelihood-mle-fisher-information

## LinkedIn post

The likelihood-ratio statistic is χ²-distributed, but only when the null sits inside the parameter space.

The fourth part of Statistics for Data Scientists builds an estimate, its standard error and three tests from one curve, then breaks the promise on real data:

→ Clarke's 1946 count of 537 V-1 hits on 576 squares of south London: the log-likelihood peaks at 537/576 = 0.9323 hits per square, its curvature there is the information, 617.8, and the standard error is 1/√617.8 = 0.0402.
→ Wald, score and likelihood ratio measure how far a null value sits from that peak. With 537 hits they agree within 10% (4.18, 4.59, 4.45); with one Prussian corps' 25 horse-kick deaths they differ twofold (6.55, 13.43, 10.27).
→ Only Wald changes when the parameter is rewritten: one hypothesis gives Wald statistics from 3.63 to 27.52.
→ For a negative binomial's shape, the profile-likelihood interval runs from 0.585 to 1.383. Re-estimated on 20,000 simulated data sets, the shape lands above Wald's symmetric 0.500 to 1.230 in 7.47% of them, where a normal puts 2.5%.
→ Testing Poisson against negative binomial puts the null on the boundary: in 200,000 simulated data sets 52.6% of likelihood ratios are exactly zero, the χ² test rejects 2.17% of true nulls instead of 5%, and the right p-value is half the χ² one.

Every number comes from a seeded lab, with its Monte Carlo standard error, that you can rerun in about 100 seconds.

## LinkedIn first comment

Before comparing a likelihood ratio with χ², check where the null sits. Inside the parameter space χ²₁ holds; on its boundary (no overdispersion, no random effect, no zero inflation) halve the p-value.

Read the full article on Canery: https://canery.in/blogs/likelihood-mle-fisher-information

## Instagram caption

Is the likelihood-ratio statistic χ²? Only when the null sits inside the parameter space. Swipe through one curve that gives the estimate, its standard error and three tests; where the three disagree; why Wald depends on how the parameter is written; profile-likelihood intervals; the boundary, where half the likelihood ratios are exactly zero; and a power law tested against a lognormal.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #maximumlikelihood #hypothesistesting #python #machinelearning

## Shared feed order

1. `assets/social/feed-01-boundary-p-value.png` — Clarke's V-1 counts tested for clustering: the likelihood ratio of 0.41 gives p = 0.52 against χ²₁ but 0.26 against the 50:50 mixture that the boundary null α = 0 requires
2. `assets/social/feed-02-one-curve.png` — Clarke's Poisson log-likelihood: its peak is the MLE, 537/576 = 0.9323; its curvature there is the information, 617.8; the standard error is 1/√617.8 = 0.0402
3. `assets/social/feed-03-few-events.png` — the Wald, likelihood-ratio and score statistics agree within 10% on Clarke's 537 hits (4.18, 4.45, 4.59) and differ twofold on corps XI's 25 horse-kick deaths (6.55, 10.27, 13.43)
4. `assets/social/feed-04-wald-and-scale.png` — one hypothesis for corps XI written on four scales: Wald gives 6.55 on the rate, 12.87 on its log, 27.52 on the mean time between deaths and 3.63 on its square, while the likelihood ratio stays 10.27
5. `assets/social/feed-05-lopsided-interval.png` — for the negative binomial's shape k on Greenwood and Yule's 647 women, the profile-likelihood interval is 0.585 to 1.383 and Wald's symmetric one 0.500 to 1.230; refitted on 20,000 simulated data sets, k̂ falls above the Wald interval in 7.47% and below it in 0.14%
6. `assets/social/feed-06-half-are-zero.png` — over 200,000 Poisson data sets shaped like Clarke's, the likelihood ratio against the negative binomial is exactly zero in 52.6%; the χ²₁ test at 3.84 rejects 2.17% and the mixture's test at 2.71 rejects 4.40%, against 5.01% for a null inside the parameter space
7. `assets/social/feed-07-power-law-or-lognormal.png` — on the first part's lognormal sample, Vuong's normalised likelihood ratio is 2.29 (p = 0.022, lognormal) on the top 1,000 values and 1.29 (p = 0.20, cannot tell) at CSN's threshold of 509 values; a true power law is decided for in only 4.4% of samples
8. `assets/social/feed-08-read-the-article.png` — the article's four results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-boundary-p-value

- File: `assets/social/feed-01-boundary-p-value.png`
- Title: On a boundary, the χ² p-value doubles
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Clarke's V-1 counts tested for clustering: the likelihood ratio of 0.41 gives p = 0.52 against χ²₁ but 0.26 against the 50:50 mixture that the boundary null α = 0 requires
- Technical source: Why this matters; What happens when the null sits on a boundary?; Figure 10; ledger L17–L19, L23
- Visual structure: lockup and counter; serif title; deck; a panel with the likelihood ratio and two p-values as large numbers, the naive one in blue and the correct one in tangerine, and a simulation note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · On a boundary, the · χ² p-value doubles. · Testing Poisson against negative binomial · puts the null at the edge of the model. · Clarke's 576 squares of V-1 hits: clustered? · likelihood ratio, NB against Poisson · 0.41 · p against χ²₁ · 0.52 · the textbook reference · p against ½ χ²₀ + ½ χ²₁ · 0.26 · the right one: the null α = 0 is the edge · 200,000 simulated Poisson data sets: LR = 0 in 52.6%, · and the χ²₁ test rejects 2.17% of true nulls, not 5% · When the null sits on a boundary, · halve the χ² p-value. · LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN
- Alt text: Card showing Clarke's clustering test: likelihood ratio 0.41, p 0.52 against χ²₁ and 0.26 against the boundary mixture.
- Long description: Testing whether Clarke's 576 squares of V-1 hits are overdispersed compares the negative binomial with the Poisson; the null α = 0 is the boundary of the parameter space. The likelihood ratio is 0.41. Compared with χ² on one degree of freedom its p-value is 0.52; compared with the equal mixture of a point mass at zero and χ²₁, the correct reference on a boundary, it is 0.26. Over 200,000 simulated Poisson data sets the likelihood ratio is exactly zero in 52.6% of them, and the χ²₁ test rejects 2.17% of true nulls instead of 5%. Takeaway: when the null sits on a boundary, halve the χ² p-value.
- Keywords: likelihood ratio test, boundary, chi-square mixture, negative binomial, overdispersion, Clarke V-1
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information

### feed-02-one-curve

- File: `assets/social/feed-02-one-curve.png`
- Title: One curve gives the estimate and its error
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Clarke's Poisson log-likelihood: its peak is the MLE, 537/576 = 0.9323; its curvature there is the information, 617.8; the standard error is 1/√617.8 = 0.0402
- Technical source: Worked example, the rate, its information and its standard error; Figure 1; ledger L34
- Visual structure: lockup and counter; serif title; deck; a panel with the log-likelihood formula, a small drawn curve with its peak marked in tangerine, and three labelled computations on the right; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · One curve gives the · estimate and its error. · The log-likelihood of a Poisson rate, · from Clarke's 1946 count of V-1 hits. · l(λ) = 537 log λ − 576 λ + const · peak: the MLE · 537/576 = 0.9323 · curvature: the information · 537/0.9323² = 617.8 · standard error · 1/√617.8 = 0.0402 · rate λ, hits per square · Clarke's 576 squares of south London, 537 V-1 hits; · SciPy and statsmodels give the same estimate and standard error · The peak is the estimate; how sharply · it falls is the information. · LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN
- Alt text: Card with Clarke's log-likelihood curve: peak 537/576 = 0.9323, curvature 617.8, standard error 0.0402.
- Long description: The log-likelihood of a Poisson rate for Clarke's 1946 count, 537 V-1 hits on 576 squares of south London, is 537 log λ − 576 λ plus a constant. Its peak is the maximum likelihood estimate, 537/576 = 0.9323 hits per square. Its curvature at the peak, 537/0.9323² = 617.8, is the information, and the standard error is 1/√617.8 = 0.0402. SciPy and statsmodels give the same estimate and standard error. Takeaway: the peak is the estimate; how sharply it falls is the information.
- Keywords: maximum likelihood, log-likelihood, Fisher information, standard error, Poisson, Clarke V-1
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information

### feed-03-few-events

- File: `assets/social/feed-03-few-events.png`
- Title: Few events, three different answers
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the Wald, likelihood-ratio and score statistics agree within 10% on Clarke's 537 hits (4.18, 4.45, 4.59) and differ twofold on corps XI's 25 horse-kick deaths (6.55, 10.27, 13.43)
- Technical source: Worked example, three distances from one null value; When do the Wald, score and likelihood-ratio tests disagree?; Figures 2 and 3; ledger L10, L11, L36
- Visual structure: lockup and counter; serif title; deck; a panel with two blocks, each a data set with its three statistics in a row coloured blue, ink and tangerine; p-values under the second; a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Few events, three · different answers. · Wald, likelihood ratio and score measure · how far a null value sits from the estimate. · the same three tests on two data sets · Clarke: 537 hits, null 0.85 · Wald 4.18 · LR 4.45 · score 4.59 · within 10% of each other · corps XI: 25 deaths in 20 years, null 0.61 · Wald 6.55 · LR 10.27 · score 13.43 · p = 0.010, 0.0014 and 0.00025 · horse-kick deaths from Bortkiewicz's 1898 table; the null is · the rate of the ten corps he kept, taken as known · With small counts the curve is lopsided: · prefer the likelihood ratio or the score. · LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN
- Alt text: Card comparing three test statistics: Clarke's 537 hits give 4.18, 4.45, 4.59; corps XI's 25 deaths give 6.55, 10.27, 13.43.
- Long description: The Wald, likelihood-ratio and score statistics measure how far a null value sits from the estimate in three ways. On Clarke's 537 V-1 hits, testing a rate of 0.85, they are 4.18, 4.45 and 4.59, within 10% of each other. On corps XI of Bortkiewicz's 1898 table, 25 deaths by horse kick in 20 years, tested against the 0.61 rate of the ten corps he kept, taken as known, they are 6.55, 10.27 and 13.43, with p-values of 0.010, 0.0014 and 0.00025. Takeaway: with small counts the log-likelihood is lopsided, so prefer the likelihood ratio or the score test.
- Keywords: Wald test, score test, likelihood ratio test, small samples, Bortkiewicz horse kicks
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information

### feed-04-wald-and-scale

- File: `assets/social/feed-04-wald-and-scale.png`
- Title: Rewrite the parameter, change the Wald test
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one hypothesis for corps XI written on four scales: Wald gives 6.55 on the rate, 12.87 on its log, 27.52 on the mean time between deaths and 3.63 on its square, while the likelihood ratio stays 10.27
- Technical source: When do the Wald, score and likelihood-ratio tests disagree?, does it matter how the parameter is written?; Figure 5; ledger L13, L14
- Visual structure: lockup and counter; serif title; deck; a panel listing four Wald statistics in blue, then the likelihood ratio in tangerine below a rule, and the 5% critical value; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Rewrite the parameter, · change the Wald test. · Wald squares a distance on whatever scale · the parameter happens to be written in. · corps XI, one hypothesis, written four ways · Wald on the rate λ · 6.55 · Wald on log λ · 12.87 · Wald on 1/λ, years between deaths · 27.52 · Wald on λ²: not significant · 3.63 · likelihood ratio, on any scale · 10.27 · 5% critical value: 3.84 · The likelihood ratio does not change. · Wald runs from 3.63 to 27.52. · LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN
- Alt text: Card listing Wald statistics for one hypothesis on four scales, 3.63 to 27.52, against an unchanging likelihood ratio of 10.27.
- Long description: Corps XI's 25 deaths in 20 years are tested against a rate of 0.61. The hypothesis is the same whichever way the rate is written, but the Wald statistic is not: 6.55 on the rate λ, 12.87 on log λ, 27.52 on 1/λ, the mean years between deaths, and 3.63 on λ², which does not reach the 5% critical value of 3.84. The likelihood ratio is 10.27 on every scale. Takeaway: the likelihood ratio does not change with the parameterisation; Wald runs from 3.63 to 27.52.
- Keywords: Wald test, parameterization, invariance, likelihood ratio test, reparameterisation
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information

### feed-05-lopsided-interval

- File: `assets/social/feed-05-lopsided-interval.png`
- Title: Skewed estimate, lopsided interval
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: for the negative binomial's shape k on Greenwood and Yule's 647 women, the profile-likelihood interval is 0.585 to 1.383 and Wald's symmetric one 0.500 to 1.230; refitted on 20,000 simulated data sets, k̂ falls above the Wald interval in 7.47% and below it in 0.14%
- Technical source: Why is the profile-likelihood interval lopsided?; Figures 7 and 8; ledger L20, L38
- Visual structure: lockup and counter; serif title; deck; a panel with two horizontal interval bars on a shared axis from 0.4 to 1.4, the profile bar in tangerine above the Wald bar in blue, each marking k̂ = 0.865, and a simulation note; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Skewed estimate, · lopsided interval. · The likelihood falls slowly toward large k, · so the honest interval reaches farther there. · 95% intervals for the negative binomial shape k · 0.4 · 0.6 · 0.8 · 1.0 · 1.2 · 1.4 · profile likelihood: 0.585 to 1.383 · Wald, k̂ ± 1.96 SE: 0.500 to 1.230 · refitted on 20,000 simulated data sets, k̂ falls · above the Wald interval in 7.47%, below it in 0.14% · Greenwood and Yule's 647 munition workers, k̂ = 0.865 · Use profile-likelihood intervals · for dispersions and variances. · LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN
- Alt text: Card with two 95% intervals for a negative binomial shape: profile 0.585 to 1.383, Wald 0.500 to 1.230, on one axis.
- Long description: The negative binomial fitted to Greenwood and Yule's 647 munition workers has shape k̂ = 0.865. Its likelihood falls slowly toward large k, so the profile-likelihood 95% interval reaches farther there: 0.585 to 1.383, against the Wald interval k̂ ± 1.96 SE, 0.500 to 1.230. Refitted on 20,000 data sets simulated from the fitted model, k̂ falls above the Wald interval in 7.47% of them and below it in 0.14%, where a normal would put 2.5% on each side. Takeaway: use profile-likelihood intervals for dispersions and variances.
- Keywords: profile likelihood, confidence interval, Wald interval, negative binomial, dispersion, Greenwood Yule
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information

### feed-06-half-are-zero

- File: `assets/social/feed-06-half-are-zero.png`
- Title: Half the likelihood ratios are zero
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: over 200,000 Poisson data sets shaped like Clarke's, the likelihood ratio against the negative binomial is exactly zero in 52.6%; the χ²₁ test at 3.84 rejects 2.17% and the mixture's test at 2.71 rejects 4.40%, against 5.01% for a null inside the parameter space
- Technical source: What happens when the null sits on a boundary?; Figures 9 and 10; ledger L17–L19
- Visual structure: lockup and counter; serif title; deck; a panel with three large percentages, each followed by what it measures; a note on the interior comparison; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Half the likelihood · ratios are zero. · Under a Poisson the fitted dispersion lands · on its boundary, α = 0, about half the time. · 200,000 Poisson data sets shaped like Clarke's · 52.6% · have a likelihood ratio of exactly 0 · 2.17% · rejected by the χ²₁ test at 3.84 · 4.40% · rejected by the mixture's test at 2.71 · inside the parameter space the χ²₁ test rejects 5.01%, · as Wilks's theorem promises: the boundary is the difference · On a boundary the reference is · ½ χ²₀ + ½ χ²₁, not χ²₁. · LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN
- Alt text: Card with three simulated rates: 52.6% of likelihood ratios exactly zero, 2.17% rejected by χ²₁, 4.40% by the mixture's test.
- Long description: Under a Poisson null the negative binomial's fitted dispersion lands on its boundary, α = 0, about half the time, and then the likelihood ratio is exactly zero. Over 200,000 Poisson data sets shaped like Clarke's this happens in 52.6% of them. The χ²₁ test at 3.84 rejects 2.17% of these true nulls, and the 50:50 mixture's test at 2.71 rejects 4.40%. With the null inside the parameter space the χ²₁ test rejects 5.01%, as Wilks's theorem promises. Takeaway: on a boundary the reference distribution is half χ²₀ plus half χ²₁, not χ²₁.
- Keywords: boundary, chi-square mixture, Chernoff, Self and Liang, likelihood ratio test, simulation
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information

### feed-07-power-law-or-lognormal

- File: `assets/social/feed-07-power-law-or-lognormal.png`
- Title: Power law or lognormal? Ask the likelihood
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: on the first part's lognormal sample, Vuong's normalised likelihood ratio is 2.29 (p = 0.022, lognormal) on the top 1,000 values and 1.29 (p = 0.20, cannot tell) at CSN's threshold of 509 values; a true power law is decided for in only 4.4% of samples
- Technical source: Power law or lognormal: what does the likelihood ratio say?; Figures 12 and 13; ledger L28–L31
- Visual structure: lockup and counter; serif title; deck; a panel with two rows, each a tail size with its normalised ratio as a large number and its p-value and verdict, then a note on a true power law; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Power law or lognormal? · Ask the likelihood. · A lognormal's tail can look straight · on log–log axes; the likelihood can tell. · Vuong's normalised likelihood ratio, lognormal over power law · top 1,000 values · 2.29 · p = 0.022: lognormal · CSN's threshold, 509 values · 1.29 · p = 0.20: cannot tell · a true power law, 1,000 values: decided for it · in only 4.4% of 1,000 samples · the first part's lognormal sample, regenerated exactly · The test can rule a power law out, · but it rarely confirms one. · LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN
- Alt text: Card comparing power law and lognormal fits: normalised ratio 2.29 on 1,000 values, 1.29 at CSN's threshold of 509.
- Long description: The first part's 10,000 lognormal values have a tail that looks straight on log–log axes. Fitting a power law and a lognormal above a threshold by maximum likelihood and comparing them with Vuong's normalised likelihood ratio gives 2.29, p = 0.022, in favour of the lognormal on the top 1,000 values, and 1.29, p = 0.20, which cannot decide, at the 509 values above Clauset, Shalizi and Newman's chosen threshold. When the truth is a power law with 1,000 values, the comparison decides for it in only 4.4% of 1,000 samples. Takeaway: the likelihood ratio can rule a power law out, but it rarely confirms one.
- Keywords: power law, lognormal, Vuong test, likelihood ratio, Clauset Shalizi Newman, heavy tails
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Likelihood, and where χ² fails
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the article's four results in one list, and the call to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel with four headed items, the last in tangerine; takeaway; the call to action in tangerine
- Visible-text transcript: Canery.in · 08 / 08 · Likelihood, and · where χ² fails. · Every number measured by a seeded lab · you can rerun in about 100 seconds. · MLE ± 1/√information · Clarke: 0.9323 ± 0.0402 hits per square · Wald · score · likelihood ratio · agree with 537 hits, not with 25 · profile-likelihood intervals · k: 0.585 to 1.383, not Wald's symmetric one · the boundary · χ²₁ rejects 2.17%: halve its p-value · The full walk-through, with the lab · and every number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/LIKELIHOOD-MLE-FISHER-INFORMATION
- Alt text: Closing card listing the article's results: MLE ± 1/√information, three tests, profile intervals and the boundary's halved p-value.
- Long description: A summary of the article: the MLE with its standard error, one over the square root of the information (Clarke: 0.9323 ± 0.0402 hits per square); the Wald, score and likelihood-ratio statistics, which agree with 537 hits but not with 25; profile-likelihood intervals (k: 0.585 to 1.383, not Wald's symmetric interval); and the boundary, where the χ²₁ test rejects 2.17% of true nulls, so its p-value should be halved. Every number is measured by a seeded lab that reruns in about 100 seconds. Call to action: read it at canery.in/blogs/likelihood-mle-fisher-information.
- Keywords: maximum likelihood, Fisher information, Wald test, profile likelihood, likelihood ratio test, data science
- Canonical URL: https://canery.in/blogs/likelihood-mle-fisher-information
