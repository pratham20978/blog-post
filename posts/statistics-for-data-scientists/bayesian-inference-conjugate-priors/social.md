---
social_schema: 2
canonical_url: "https://canery.in/blogs/bayesian-inference-conjugate-priors"
---

# Social publishing package — bayesian-inference-conjugate-priors

## LinkedIn post

A flat prior is not a neutral one. Flat on one scale is a hill on another, and with few events the prior writes part of the answer.

The eleventh part of Statistics for Data Scientists computes Bayesian inference by hand:

→ Laplace's 1781 question: 251,527 boys and 241,945 girls baptised in Paris, a uniform prior, and a probability of 1.1461 × 10⁻⁴² that boys are not the likelier birth. His own series gave 1.1521 × 10⁻⁴².
→ The Pfizer–BioNTech trial's 95% credible interval, 90.3% to 97.6%, rebuilt from its protocol: beta(0.700102, 1) plus 8 of 170 cases, mapped with the ratio of surveillance times.
→ The protocol's success and futility boundaries follow from the same posterior and its predictive distribution, entry for entry.
→ With 170 cases five common priors move the lower limit by 0.8 points; with the 4 severe cases, by 38.
→ Lindley's paradox in Laplace's own table: Paris in 1782 rejects a boy probability of ½ at p = 0.024, while the Bayes factor favours ½ by 8.6 to 1.

Every number is computed exactly, matched to SciPy and R, and reproduced by a lab you can rerun.

## LinkedIn first comment

Before trusting a posterior, ask which scale its prior is flat on, and rerun it with two other priors.

Read the full article on Canery: https://canery.in/blogs/bayesian-inference-conjugate-priors

## Instagram caption

How does a prior become a posterior, and how much of the answer did it write? Swipe through Laplace's 1781 calculation on Paris births, a vaccine trial's credible interval rebuilt from its protocol, where the prior's 0.700102 comes from, what 95% promises, and Lindley's paradox in a single year of baptisms.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #bayesian #python #bayesianinference #credibleinterval

## Shared feed order

1. `assets/social/feed-01-laplaces-question.png` — Laplace's Paris baptisms, 251,527 boys and 241,945 girls from 1745 to 1770, under a uniform prior: P(x ≤ ½) = 1.1461 × 10⁻⁴², against his own first-term estimate of 1.1521 × 10⁻⁴²
2. `assets/social/feed-02-the-trials-interval-by-hand.png` — The trial's prior beta(0.700102, 1) plus 8 vaccine and 162 placebo cases is beta(8.700102, 163); mapped to efficacy with the surveillance-time ratio it gives the published 90.3% to 97.6%
3. `assets/social/feed-03-where-0700102-comes-from.png` — The prior's constant is 0.4118/0.5882, the beta(p/(1 − p), 1) with its mean at VE 30%; that 'minimally informative' prior puts 38.4% on harm, a median VE of 40.9% and a 95% VE interval of −2,616% to 99.5%
4. `assets/social/feed-04-170-cases-against-4.png` — Five priors move the primary endpoint's lower VE limit only from 90.1% to 90.9%, but the 4 severe cases' lower limit from −154.6% to −116.6%; the prior keeps 1.0% of the weight at 170 cases and 29.8% at 4
5. `assets/social/feed-05-equal-tails-or-highest-density.png` — The equal-tailed intervals reproduce the published 90.3% to 97.6% and −124.8% to 96.3%; the highest-density intervals are 90.9% to 97.9% and −69.7% to 99.9%
6. `assets/social/feed-06-what-95-percent-promises.png` — Averaged over its prior the trial's credible interval covers exactly 95.000%; at a fixed true efficacy it covers 92.9% to 96.5% with 170 cases and as little as 86.6% with 4, where Clopper–Pearson holds 95.1% to 98.0%
7. `assets/social/feed-07-lindleys-paradox-1782.png` — Paris 1782, 9,851 boys of 19,387: the exact test rejects ½ at p = 0.0241 while the Bayes factor under a uniform alternative favours ½ by 8.60; with the 1745–1770 posterior as the alternative's prior it is 11.54 against
8. `assets/social/feed-08-read-the-article.png` — The article's five results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-laplaces-question

- File: `assets/social/feed-01-laplaces-question.png`
- Title: How sure was Laplace?
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Laplace's Paris baptisms, 251,527 boys and 241,945 girls from 1745 to 1770, under a uniform prior: P(x ≤ ½) = 1.1461 × 10⁻⁴², against his own first-term estimate of 1.1521 × 10⁻⁴²
- Technical source: Worked example; Figure 1; ledger L01, L02
- Visual structure: lockup and counter; serif title; deck; a panel with the dataset line, the two counts large, the posterior, the exact tail in tangerine and Laplace's printed value; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · How sure was · Laplace? · x is the chance that a Paris birth is a boy. · A uniform prior, 26 years of baptisms. · Paris baptisms, 1745 to 1770 (Laplace, 1781) · boys · 251,527 · girls · 241,945 · uniform prior → posterior beta(251,528, 241,946) · P(x ≤ ½), exact · 1.1461 × 10⁻⁴² · Laplace's first term · 1.1521 × 10⁻⁴² · his own series, “a little too great” · ½ lies 13.6 posterior SDs below the mean: · the boys' excess is no accident. · BAYESIAN INFERENCE BY HAND · CANERY.IN
- Alt text: Card: Paris baptisms 1745–1770, 251,527 boys and 241,945 girls; under a uniform prior P(x ≤ ½) = 1.1461 × 10⁻⁴², Laplace's 1.1521.
- Long description: Laplace's question about the Paris baptisms of 1745 to 1770: 251,527 boys and 241,945 girls. With a uniform prior on x, the chance that a birth is a boy, the posterior is beta(251,528, 241,946), and the probability that x is at most one half is 1.1461 × 10^-42 exactly. Laplace's own series, whose first term he printed as 1.1521 × 10^-42 and called a little too great, came within 0.53%. Takeaway: one half lies 13.6 posterior standard deviations below the mean, so the boys' excess is no accident.
- Keywords: Laplace, Bayesian inference, uniform prior, beta posterior, sex ratio, inverse probability
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors

### feed-02-the-trials-interval-by-hand

- File: `assets/social/feed-02-the-trials-interval-by-hand.png`
- Title: A vaccine trial's interval, by hand
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The trial's prior beta(0.700102, 1) plus 8 vaccine and 162 placebo cases is beta(8.700102, 163); mapped to efficacy with the surveillance-time ratio it gives the published 90.3% to 97.6%
- Technical source: Worked example; Figure 2; The math, equation 1; ledger L08, L09, L12
- Visual structure: lockup and counter; serif title; deck; a panel with the update as three rows (prior, cases, posterior), the efficacy map, the credible interval large in tangerine with the published values, and P(VE ≤ 30%); takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · A vaccine trial's · interval, by hand. · θ is the vaccine group's share of cases. · The protocol's prior, then the data. · Pfizer–BioNTech phase 3, primary endpoint · prior on θ · beta(0.700102, 1) · + cases · 8 vaccine, 162 placebo · = posterior · beta(8.700102, 163) · VE = 1 − θ / ((1 − θ) r), r = 2.214 / 2.222 · 95% credible interval · 90.3% to 97.6% · published: 90.3 to 97.6 · P(VE ≤ 30%) · 2.46 × 10⁻²⁸ · Conjugacy turns the trial's Bayesian analysis · into two additions and two quantiles. · BAYESIAN INFERENCE BY HAND · CANERY.IN
- Alt text: Card: the trial's prior beta(0.700102, 1) plus 8 vaccine and 162 placebo cases gives beta(8.700102, 163) and VE 90.3% to 97.6%.
- Long description: The Pfizer-BioNTech phase 3 primary analysis rebuilt from its protocol. theta is the vaccine group's share of cases. The prior beta(0.700102, 1) plus 8 vaccine and 162 placebo cases gives the posterior beta(8.700102, 163). Mapped to vaccine efficacy by VE = 1 − theta/((1 − theta) r), with r = 2.214/2.222 the ratio of surveillance times, its quantiles give a 95% credible interval of 90.3% to 97.6%, the published values, and P(VE ≤ 30%) = 2.46 × 10^-28. Takeaway: conjugacy turns the analysis into two additions and two quantiles.
- Keywords: credible interval, beta-binomial, conjugate prior, vaccine efficacy, Pfizer BioNTech, Bayesian trial
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors

### feed-03-where-0700102-comes-from

- File: `assets/social/feed-03-where-0700102-comes-from.png`
- Title: Where does 0.700102 come from?
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The prior's constant is 0.4118/0.5882, the beta(p/(1 − p), 1) with its mean at VE 30%; that 'minimally informative' prior puts 38.4% on harm, a median VE of 40.9% and a 95% VE interval of −2,616% to 99.5%
- Technical source: Worked example; How much does the prior matter?; Figure 9; ledger L12, L18, L19
- Visual structure: lockup and counter; serif title; deck; a panel with the target and the rounding, 0.700102 large in tangerine, a rule, then three rows of what the prior says; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Where does · 0.700102 come from? · The prior's first parameter has six figures · and its second has one. The reason is a rounding. · the target: θ at VE 30% = 0.7 / 1.7 = 0.411765 · rounded to 0.4118; beta(p/(1 − p), 1) has mean p · 0.4118 / 0.5882 · 0.700102 · what the 'minimally informative' prior says · P(VE < 0), harm · 38.4% · median VE · 40.9% · its mean of θ maps to 30%, its median to 40.9% · 95% interval for VE · −2,616% to 99.5% · A 'minimally informative' prior still says · something: 38.4% that the vaccine does harm. · BAYESIAN INFERENCE BY HAND · CANERY.IN
- Alt text: Card: 0.700102 = 0.4118/0.5882; the prior puts 38.4% on harm, a median VE of 40.9% and a 95% interval of −2,616% to 99.5%.
- Long description: Why the protocol's prior is beta(0.700102, 1): the share of cases at VE 30% is 0.7/1.7 = 0.411765, rounded to 0.4118, and beta(p/(1 − p), 1) has mean p, so the first parameter is 0.4118/0.5882 = 0.700102. What this minimally informative prior says: a 38.4% probability that the vaccine does harm, a median efficacy of 40.9% while its mean of theta maps to 30%, and a 95% prior interval for efficacy from −2,616% to 99.5%. Takeaway: a minimally informative prior still says something.
- Keywords: prior distribution, minimally informative prior, beta prior, vaccine efficacy, Senn, prior elicitation
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors

### feed-04-170-cases-against-4

- File: `assets/social/feed-04-170-cases-against-4.png`
- Title: 170 cases outvote the prior. 4 do not.
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Five priors move the primary endpoint's lower VE limit only from 90.1% to 90.9%, but the 4 severe cases' lower limit from −154.6% to −116.6%; the prior keeps 1.0% of the weight at 170 cases and 29.8% at 4
- Technical source: Intuition; How much does the prior matter?; Figures 3 and 8; ledger L16, L18
- Visual structure: lockup and counter; serif title; deck; a panel with a three-column table of five priors and the lower limits for 8:162 (blue) and 1:3 (tangerine), and two lines on the prior's weight; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · 170 cases outvote · the prior. 4 do not. · Five common priors, two endpoints from the · same trial, one lower limit each. · lower limit of the 95% credible interval for VE · prior · 8 : 162 · 1 : 3 · beta(0.700102, 1) · 90.3% · −124.8% · beta(1, 1.428363) · 90.1% · −116.6% · beta(1, 1) · 90.1% · −154.6% · beta(½, ½) · 90.5% · −154.4% · beta(0, 0) · 90.9% · −143.9% · the prior's weight: 1.0% of the posterior mean at 170 cases, · 29.8% at 4 (the trial's severe-case endpoint) · With few events every default prior shows in · the answer: report the prior and vary it. · BAYESIAN INFERENCE BY HAND · CANERY.IN
- Alt text: Card tabling five priors' lower VE limits: 90.1% to 90.9% for 8:162 cases, −154.6% to −116.6% for the 4 severe cases.
- Long description: The lower limit of the 95% credible interval for vaccine efficacy under five priors: the trial's beta(0.700102, 1), Senn's beta(1, 1.428363), the uniform beta(1, 1), Jeffreys' beta(1/2, 1/2) and Haldane's beta(0, 0). With 8 vaccine and 162 placebo cases the limits are 90.3%, 90.1%, 90.1%, 90.5% and 90.9%; with the 1 against 3 severe cases, −124.8%, −116.6%, −154.6%, −154.4% and −143.9%. The prior keeps 1.0% of the weight on the posterior mean at 170 cases and 29.8% at 4. Takeaway: with few events, report the prior and vary it.
- Keywords: prior sensitivity, Jeffreys prior, Haldane prior, uniform prior, small samples, credible interval
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors

### feed-05-equal-tails-or-highest-density

- File: `assets/social/feed-05-equal-tails-or-highest-density.png`
- Title: Equal tails or highest density?
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The equal-tailed intervals reproduce the published 90.3% to 97.6% and −124.8% to 96.3%; the highest-density intervals are 90.9% to 97.9% and −69.7% to 99.9%
- Technical source: Credible intervals: equal tails or highest density?; Figure 5; ledger L21, L22
- Visual structure: lockup and counter; serif title; deck; a panel with four interval rows, equal tails in tangerine with the published values beneath and highest density in blue, and a note on the one-sided probabilities; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Equal tails or · highest density? · Only one of them reproduces the trial's · published intervals. · two 95% intervals from one posterior · 8 : 162, equal tails · 90.3% to 97.6% · published 90.3 to 97.6 · 8 : 162, highest density · 90.9% to 97.9% · 1 : 3, equal tails · −124.8% to 96.3% · published −124.8 to 96.3 · 1 : 3, highest density · −69.7% to 99.9% · P(VE ≥ lower end), 8 : 162: 97.5% with equal tails, 96.1% with the HDI · Quantiles survive a change of scale; the · shortest interval does not. · BAYESIAN INFERENCE BY HAND · CANERY.IN
- Alt text: Card: equal-tailed 90.3% to 97.6% against highest-density 90.9% to 97.9% for 8:162; −124.8% to 96.3% against −69.7% to 99.9% for 1:3.
- Long description: Two 95% intervals from one posterior. For the primary endpoint, 8 against 162 cases, the equal-tailed interval is 90.3% to 97.6%, the published one, and the highest-density interval of efficacy is 90.9% to 97.9%. For the severe endpoint, 1 against 3, they are −124.8% to 96.3%, published, and −69.7% to 99.9%. The probability that efficacy is at least the lower end is 97.5% for equal tails and 96.1% for the highest-density interval. Takeaway: quantiles survive a change of scale; the shortest interval does not.
- Keywords: highest density interval, HDI, equal-tailed interval, credible interval, posterior summary, skewed posterior
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors

### feed-06-what-95-percent-promises

- File: `assets/social/feed-06-what-95-percent-promises.png`
- Title: What does 95% promise?
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Averaged over its prior the trial's credible interval covers exactly 95.000%; at a fixed true efficacy it covers 92.9% to 96.5% with 170 cases and as little as 86.6% with 4, where Clopper–Pearson holds 95.1% to 98.0%
- Technical source: What does a credible interval promise?; Figure 6; ledger L32, L34
- Visual structure: lockup and counter; serif title; deck; a panel with four rows: the prior-averaged coverage large in tangerine, the range at 170 cases, the lowest value at 4 cases, and the Clopper–Pearson range in blue; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · What does 95% · promise? · The credible interval held to a fixed true · efficacy, and averaged over its prior. · exact coverage of the trial's 95% credible interval · averaged over the prior · 95.000% · for any number of cases: it holds 95% of each posterior · 170 cases, VE 0 to 95% · 92.9% to 96.5% · 4 cases, lowest · 86.6% · at a true VE of 96.3% · Clopper–Pearson, 170 cases · 95.1% to 98.0% · A credible interval's 95% is an average over · its prior, not a guarantee at each true value. · BAYESIAN INFERENCE BY HAND · CANERY.IN
- Alt text: Card: the credible interval covers 95.000% averaged over its prior, 92.9% to 96.5% at fixed VE with 170 cases, 86.6% at worst with 4.
- Long description: The exact frequentist coverage of the trial's 95% credible interval. Averaged over its prior it is exactly 95.000% for any number of cases, because the interval holds 95% of each posterior. At a fixed true efficacy between 0% and 95% it covers 92.9% to 96.5% with 170 cases; with 4 cases it falls as low as 86.6%, at a true efficacy of 96.3%. The Clopper-Pearson interval holds 95.1% to 98.0% with 170 cases. Takeaway: a credible interval's 95% is an average over its prior, not a guarantee at each true value.
- Keywords: coverage, credible interval, confidence interval, Clopper-Pearson, frequentist properties, calibration
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors

### feed-07-lindleys-paradox-1782

- File: `assets/social/feed-07-lindleys-paradox-1782.png`
- Title: Rejected at 5%, favoured 8.6 to 1
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Paris 1782, 9,851 boys of 19,387: the exact test rejects ½ at p = 0.0241 while the Bayes factor under a uniform alternative favours ½ by 8.60; with the 1745–1770 posterior as the alternative's prior it is 11.54 against
- Technical source: Bayes factors and Lindley's paradox; Figures 10 and 11; ledger L35, L37, L38
- Visual structure: lockup and counter; serif title; deck; a panel with the 1782 counts and the hypothesis, then three rows: the p-value, the uniform-alternative Bayes factor in tangerine and the informed Bayes factor in blue, and a note on the other years; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Rejected at 5%, · favoured 8.6 to 1. · Lindley's paradox in one year of Laplace's · own table of Paris baptisms. · Paris, 1782: 9,851 boys of 19,387 births · H0: a birth is a boy with probability ½ · exact binomial test · p = 0.0241 · rejects ½ at the 5% level · Bayes factor, uniform H1 · BF01 = 8.60 · favours ½, P(H0 | data) = 0.896 · H1's prior: 1745–1770 · BF10 = 11.54 · the earlier years' posterior: against ½ · 4 of the 14 years 1771–1784 reject at 5% while BF01 exceeds 1 · A Bayes factor inherits its alternative's · prior, and at a fixed z it grows like √n. · BAYESIAN INFERENCE BY HAND · CANERY.IN
- Alt text: Card: Paris 1782, 9,851 boys of 19,387; exact p = 0.0241 rejects ½, but BF01 = 8.60 favours it; the earlier years' prior gives BF10 = 11.54.
- Long description: Lindley's paradox in one year of Laplace's table of Paris baptisms: in 1782, 9,851 of 19,387 births were boys. The exact binomial test of a boy probability of one half gives p = 0.0241, a rejection at the 5% level. The Bayes factor for one half against a uniform alternative is 8.60, a posterior probability of 0.896 for the null at even prior odds. With the 1745-1770 posterior as the alternative's prior the Bayes factor is 11.54 against one half. Four of the fourteen years from 1771 to 1784 reject at 5% while the Bayes factor exceeds 1. Takeaway: a Bayes factor inherits its alternative's prior and grows like the square root of n.
- Keywords: Lindley's paradox, Bayes factor, p-value, point null hypothesis, Jeffreys, Laplace
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Bayesian inference, by hand
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's five results in one list, and the call to read it
- Technical source: Insights; Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel with five headed lines, each with its number; takeaway; the canonical URL as the footer call to action
- Visible-text transcript: Canery.in · 08 / 08 · Bayesian inference, · by hand. · Every posterior in closed form, matched to · SciPy and R, and every prior checked. · Laplace, 1781 · P(x ≤ ½) = 1.1461e-42; his own 1.1521e-42 · the trial's interval · beta(8.700102, 163) → VE 90.3% to 97.6% · the prior's weight · 1.0% at 170 cases, 29.8% at 4 · flat is a choice of scale · uniform on θ: P(VE ≤ 0) = ½ · Lindley's paradox · 1782: p = 0.0241, BF01 = 8.60 · The full walk-through, with the lab, the · protocol's boundaries and every check. · READ IT AT CANERY.IN/BLOGS/BAYESIAN-INFERENCE-CONJUGATE-PRIORS
- Alt text: Closing card listing five results, from Laplace's 1.1461e-42 to Lindley's paradox in 1782, with the article's address.
- Long description: A summary of the article: Laplace in 1781 (P(x ≤ 1/2) = 1.1461e-42, his own estimate 1.1521e-42); the trial's interval (beta(8.700102, 163) gives VE 90.3% to 97.6%); the prior's weight (1.0% at 170 cases, 29.8% at 4); flatness as a choice of scale (uniform on theta gives P(VE ≤ 0) = 1/2); and Lindley's paradox (1782: p = 0.0241, BF01 = 8.60). Call to action: read it at canery.in/blogs/bayesian-inference-conjugate-priors.
- Keywords: Bayesian inference, conjugate prior, credible interval, Bayes factor, statistics for data scientists, Laplace
- Canonical URL: https://canery.in/blogs/bayesian-inference-conjugate-priors
