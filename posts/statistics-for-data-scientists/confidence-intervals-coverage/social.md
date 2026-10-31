---
social_schema: 2
canonical_url: "https://canery.in/blogs/confidence-intervals-coverage"
---

# Social publishing package — confidence-intervals-coverage

## LinkedIn post

A 95% confidence interval does not mean a 95% chance that the true value is inside it. The 95% belongs to the procedure: over repeated samples it is supposed to contain the truth 95% of the time, whatever the truth is.

The sixth part of Statistics for Data Scientists measures that promise:

→ The Pfizer–BioNTech trial printed two 95% intervals for the same 95.0% efficacy: 90.0% to 97.9% (a confidence interval, Clopper–Pearson) and 90.3% to 97.6% (a Bayesian credible interval). Only the second supports a probability statement about the efficacy.
→ For a proportion, coverage is an exact sum over outcomes. With 20 audits and a true rate of 10%, the textbook Wald interval covers 87.6%, Wilson's 95.7% and Clopper–Pearson's 98.9%.
→ The Wald interval's coverage zigzags with n: at p = 0.1 it falls from 94.7% at n = 29 to 80.9% at n = 30, and covers 87.9% at n = 50, where np ≥ 5 says it is fine. statsmodels' proportion_confint uses it by default.
→ Two overlapping 95% intervals can hide a significant difference: with equal standard errors, judging by overlap is a 0.56% test.
→ On real customer spend (skewness 21.6) a 95% t-interval covers 65.8% at n = 30, and its narrowest intervals almost never contain the mean.

Every number is computed exactly or measured by a seeded lab you can rerun in about 20 seconds.

## LinkedIn first comment

Before you trust a 95% interval, ask which procedure made it and whether that procedure keeps its 95% at your sample size. For a proportion use Wilson, Jeffreys or Agresti–Coull, or Clopper–Pearson when 95% must be a floor; to compare two groups, put an interval on the difference itself.

Read the full article on Canery: https://canery.in/blogs/confidence-intervals-coverage

## Instagram caption

Does a 95% confidence interval mean a 95% chance the truth is inside? No. Swipe through what the 95% does mean, how to measure whether an interval keeps it, which interval to use for a proportion, how a vaccine trial's interval reproduces, why two overlapping intervals can still differ, and why on skewed data the narrowest intervals are the ones that miss.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #confidenceintervals #python #biostatistics #abtesting

## Shared feed order

1. `assets/social/feed-01-two-intervals.png` — The BNT162b2 trial printed two 95% intervals for one efficacy of 95.0%: a Clopper–Pearson confidence interval of 90.0% to 97.9% and a credible interval of 90.3% to 97.6%; only the second supports a probability statement about the efficacy
2. `assets/social/feed-02-coverage-is-a-sum.png` — With 20 audits and a true error rate of 10%, each count of errors has a binomial probability; an interval's coverage is the sum over the counts whose interval contains 0.1: Wald 87.6%, Wilson 95.7%, Clopper–Pearson 98.9%
3. `assets/social/feed-03-one-more-trial.png` — At a true proportion of 0.1 the Wald interval's exact coverage zigzags as n grows: 94.7% at n = 29, 80.9% at n = 30, and 87.9% at n = 50, where np = 5 meets the rule of thumb
4. `assets/social/feed-04-pick-the-interval.png` — Five 95% intervals for a proportion at n = 50, summed exactly over every p: the lowest coverage, the mean coverage over a uniform p and the mean width relative to Wilson; only Clopper–Pearson never falls below 95%, and statsmodels defaults to the Wald interval
5. `assets/social/feed-05-trial-reproduced.png` — Given 170 cases, the vaccine group's 8 are binomial; the Clopper–Pearson interval for that share, 0.0205 to 0.0906, maps to efficacy 90.0% to 97.9%, the paper's Table 3; 9 of 16 published rows match every digit and 7 lie within the rounding of the surveillance times
6. `assets/social/feed-06-overlap-is-not-a-test.png` — In the trial's severe split, 1 case against 9, the two arms' 95% rate intervals overlap, yet the exact test of the difference gives p = 0.021 and efficacy 20.1% to 99.7%; judging a difference by non-overlap is a 0.56% test with 51% power where the real test has 80%
7. `assets/social/feed-07-t-interval-on-skewed-data.png` — On real customer spend with skewness 21.6, the 95% t-interval for the mean covers 65.8% at n = 30, lies wholly below the mean in 34.2% of samples, and sorted by width its narrowest tenth never contains the mean
8. `assets/social/feed-08-read-the-article.png` — The article's four results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-two-intervals

- File: `assets/social/feed-01-two-intervals.png`
- Title: A 95% interval is not a 95% chance
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: The BNT162b2 trial printed two 95% intervals for one efficacy of 95.0%: a Clopper–Pearson confidence interval of 90.0% to 97.9% and a credible interval of 90.3% to 97.6%; only the second supports a probability statement about the efficacy
- Technical source: Why this matters; What does a real low-count trial give?; Figure 6; ledger L01, L02, L03, L21
- Visual structure: lockup and counter; serif title; deck; a panel with the two intervals as horizontal bars on one efficacy axis, the estimate as a dashed line, and two notes on what each interval says; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · A 95% interval is not · a 95% chance. · One vaccine trial printed two 95% intervals · for the same 95.0% efficacy. · BNT162b2 trial: 8 of 170 cases in the vaccine group · efficacy 95.0% · confidence interval, Table 3 · 90.0 to 97.9 · credible interval, Table 2 · 90.3 to 97.6 · 88% · 90% · 92% · 94% · 96% · 98% · confidence: the procedure contains the true efficacy · in at least 95% of repetitions · credible: given the prior, a 97.5% probability that · efficacy is at least 90.3%, as the FDA read it · The 95% belongs to the procedure; a probability · for your interval needs a prior. · CONFIDENCE INTERVALS · CANERY.IN
- Alt text: Card comparing the trial's confidence interval, 90.0% to 97.9%, with its credible interval, 90.3% to 97.6%, for the same 95.0% efficacy.
- Long description: The Pfizer–BioNTech phase 3 trial had 8 Covid-19 cases in the vaccine group and 162 in the placebo group, an efficacy of 95.0%. Its paper prints a 95% confidence interval of 90.0% to 97.9%, by the Clopper–Pearson method (Table 3), and a 95% credible interval of 90.3% to 97.6%, from a beta-binomial model with a prior (Table 2). The confidence interval's 95% is a property of the procedure: it contains the true efficacy in at least 95% of repetitions. The credible interval, given its prior, carries a 97.5% probability that efficacy is at least 90.3%, as the FDA briefing read it. Takeaway: the 95% belongs to the procedure; a probability for your interval needs a prior.
- Keywords: confidence interval, credible interval, coverage, Clopper-Pearson, vaccine efficacy, Bayesian inference
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage

### feed-02-coverage-is-a-sum

- File: `assets/social/feed-02-coverage-is-a-sum.png`
- Title: Coverage is a sum over outcomes
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: With 20 audits and a true error rate of 10%, each count of errors has a binomial probability; an interval's coverage is the sum over the counts whose interval contains 0.1: Wald 87.6%, Wilson 95.7%, Clopper–Pearson 98.9%
- Technical source: Worked example; Figure 1; The math, equation (1)
- Visual structure: lockup and counter; serif title; deck; a table of the counts 0 to 6 with their probabilities and whether each method's interval contains 0.1, then a coverage row; a note on the counts not shown; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Coverage is a sum · over outcomes. · Add the probabilities of the counts whose · interval contains the truth. Nothing simulated. · 20 audits, true error rate 10%: does the interval contain 0.1? · errors · P(X) · Wald · Wilson · Clopper–P. · X = 0 · 0.1216 · no · yes · yes · X = 1 · 0.2702 · yes · yes · yes · X = 2 · 0.2852 · yes · yes · yes · X = 3 · 0.1901 · yes · yes · yes · X = 4 · 0.0898 · yes · yes · yes · X = 5 · 0.0319 · yes · no · yes · X = 6 · 0.0089 · yes · no · no · coverage · 87.6% · 95.7% · 98.9% · X = 7 or more: probability 0.0024, every interval misses · A 95% Wald interval covers 87.6% here; the · zero-error audit alone costs 12.2 points. · CONFIDENCE INTERVALS · CANERY.IN
- Alt text: Card tabulating which counts of errors in 20 audits give intervals containing 0.1, with coverage 87.6%, 95.7% and 98.9% for three methods.
- Long description: For 20 audited predictions with a true error rate of 10%, the count of errors X has probabilities 0.1216, 0.2702, 0.2852, 0.1901, 0.0898, 0.0319 and 0.0089 for 0 to 6 errors. The Wald interval contains 0.1 for X = 1 to 6 but not for X = 0, where it has zero width; the Wilson interval for X = 0 to 4; the Clopper–Pearson interval for X = 0 to 5. Coverage is the sum of the probabilities of the counts whose interval contains 0.1: 87.6% for Wald, 95.7% for Wilson and 98.9% for Clopper–Pearson. Seven or more errors have probability 0.0024 and every interval misses there. Takeaway: a 95% Wald interval covers 87.6% here, and the zero-error audit alone costs 12.2 points.
- Keywords: coverage probability, binomial proportion, Wald interval, Wilson interval, Clopper-Pearson, exact computation
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage

### feed-03-one-more-trial

- File: `assets/social/feed-03-one-more-trial.png`
- Title: One more trial, 14 points less coverage
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: At a true proportion of 0.1 the Wald interval's exact coverage zigzags as n grows: 94.7% at n = 29, 80.9% at n = 30, and 87.9% at n = 50, where np = 5 meets the rule of thumb
- Technical source: Which interval should you use for a proportion?; Figure 4; ledger L14
- Visual structure: lockup and counter; serif title; deck; a line chart of the Wald interval's coverage for n from 10 to 100 with the nominal 95% dashed and three labelled points; two notes; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · One more trial, · 14 points less coverage. · The Wald interval's coverage zigzags as n · grows, at a true proportion of 0.1. · exact coverage of the 95% Wald interval, true proportion 0.1 · 100% · n = 29: 94.7% · 90% · n = 50: 87.9% · 80% · n = 30: 80.9% · 70% · 60% · 10 · 30 · 50 · 70 · 100 · number of trials n · n = 50 meets the rule of thumb np ≥ 5, and covers 87.9%; · each step in n changes which counts' intervals contain 0.1 · np ≥ 5 is not a guarantee: at n = 50, where · np = 5, the Wald interval covers 87.9%. · CONFIDENCE INTERVALS · CANERY.IN
- Alt text: Card plotting the Wald interval's coverage against n at p = 0.1: 94.7% at n = 29, 80.9% at n = 30 and 87.9% at n = 50.
- Long description: The exact coverage of the 95% Wald interval for a proportion, when the true proportion is 0.1, zigzags as the number of trials n grows from 10 to 100, because each extra trial changes which counts give an interval containing 0.1. Coverage is 94.7% at n = 29 and falls to 80.9% at n = 30, about 14 points for one more trial. At n = 50, where np = 5 and the usual rule of thumb says the normal approximation is adequate, coverage is 87.9%. Takeaway: np ≥ 5 is not a guarantee.
- Keywords: Wald interval, coverage oscillation, rule of thumb, binomial proportion, sample size
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage

### feed-04-pick-the-interval

- File: `assets/social/feed-04-pick-the-interval.png`
- Title: Pick the interval, not the default
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Five 95% intervals for a proportion at n = 50, summed exactly over every p: the lowest coverage, the mean coverage over a uniform p and the mean width relative to Wilson; only Clopper–Pearson never falls below 95%, and statsmodels defaults to the Wald interval
- Technical source: Which interval should you use for a proportion?; Figures 3 and 5; Reading the library's output; ledger L13, L14, L31
- Visual structure: lockup and counter; serif title; deck; a five-row table of method, lowest coverage, mean coverage and width; a note defining the columns and naming the library default; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Pick the interval, · not the default. · Only one of the five never falls below 95%, · and it pays for that in width. · five 95% intervals at n = 50, exact over every p · interval · lowest · mean · width · Wald · near 0 · 90.1% · 0.99× · Wilson · 83.93% · 95.2% · 1.00× · Agresti–Coull · 93.45% · 95.8% · 1.02× · Clopper–Pearson · 95.08% · 96.9% · 1.08× · Jeffreys · 88.39% · 95.0% · 0.99× · lowest: the smallest coverage at any p; mean: over a uniform p; · width: as a multiple of Wilson's. statsmodels' proportion_confint · defaults to the Wald interval · Wilson or Jeffreys for small n, Agresti–Coull · for larger; Clopper–Pearson when 95% is a floor. · CONFIDENCE INTERVALS · CANERY.IN
- Alt text: Card tabulating five 95% intervals at n = 50: lowest coverage, mean coverage and width; only Clopper–Pearson stays above 95%.
- Long description: At n = 50, summing exact coverage over every true proportion: the Wald interval's lowest coverage falls toward zero at the edges, its mean is 90.1% and its width 0.99 times Wilson's; Wilson's lowest is 83.93%, mean 95.2%; Agresti–Coull's lowest 93.45%, mean 95.8%, width 1.02 times; Clopper–Pearson's lowest 95.08%, mean 96.9%, width 1.08 times; Jeffreys' lowest 88.39%, mean 95.0%, width 0.99 times. statsmodels' proportion_confint defaults to the Wald interval. Takeaway: use Wilson or Jeffreys for small n, Agresti–Coull for larger n, and Clopper–Pearson when 95% must be a floor.
- Keywords: Wilson interval, Agresti-Coull, Clopper-Pearson, Jeffreys interval, statsmodels, binomial proportion
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage

### feed-05-trial-reproduced

- File: `assets/social/feed-05-trial-reproduced.png`
- Title: A vaccine trial's interval, reproduced
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Given 170 cases, the vaccine group's 8 are binomial; the Clopper–Pearson interval for that share, 0.0205 to 0.0906, maps to efficacy 90.0% to 97.9%, the paper's Table 3; 9 of 16 published rows match every digit and 7 lie within the rounding of the surveillance times
- Technical source: What does a real low-count trial give?; Figure 6; The math, equation (4); ledger L02, L20, L22
- Visual structure: lockup and counter; serif title; deck; a panel of three steps with their values, a rule, the match to the paper and the count of published rows; a note with the Wald interval; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · A vaccine trial's · interval, reproduced. · Given the total, the vaccine group's cases · are binomial: an exact interval, then a map. · BNT162b2, the primary endpoint, recomputed · cases in the vaccine group · 8 of 170 · Clopper–Pearson for that share · 0.0205 to 0.0906 · mapped to efficacy, 1 − IRR · 90.0% to 97.9% · = the paper's Table 3, to the digit · 16 published rows: 9 match every digit, 7 lie within · the rounding of the surveillance times · the Wald interval on the same split: 91.4% to 98.4% · A published interval should reproduce from · its counts; this one does, to the digit. · CONFIDENCE INTERVALS · CANERY.IN
- Alt text: Card reproducing the trial's efficacy interval: 8 of 170 cases, a Clopper–Pearson share of 0.0205 to 0.0906, efficacy 90.0% to 97.9%.
- Long description: In the BNT162b2 trial's primary analysis, 8 of 170 Covid-19 cases were in the vaccine group. Conditional on the total, that count is binomial, and the Clopper–Pearson interval for the vaccine group's share runs from 0.0205 to 0.0906. Mapped to efficacy through the incidence rate ratio and the ratio of surveillance times, it gives 90.0% to 97.9%, the paper's Table 3 to the digit. Of the 16 Clopper–Pearson rows the trial published, 9 reproduce every digit and the other 7 lie within the rounding of the surveillance times. The Wald interval on the same split gives 91.4% to 98.4%. Takeaway: a published interval should reproduce from its counts, and this one does.
- Keywords: vaccine efficacy, Clopper-Pearson, rate ratio, reproducibility, BNT162b2, surveillance time
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage

### feed-06-overlap-is-not-a-test

- File: `assets/social/feed-06-overlap-is-not-a-test.png`
- Title: Overlapping intervals, a significant difference
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: In the trial's severe split, 1 case against 9, the two arms' 95% rate intervals overlap, yet the exact test of the difference gives p = 0.021 and efficacy 20.1% to 99.7%; judging a difference by non-overlap is a 0.56% test with 51% power where the real test has 80%
- Technical source: Do overlapping intervals mean no difference?; Figures 7 and 8; ledger L22, L23, L24
- Visual structure: lockup and counter; serif title; deck; a panel with the two arms' rate intervals and their overlap shaded on one axis, then two labelled statistics; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Overlapping intervals, · a significant difference. · Two arms' 95% intervals can overlap while · the difference between them is significant. · severe Covid-19 after dose 1: 1 case against 9 · vaccine 0.25 · placebo 2.25 · 0 · 1 · 2 · 3 · 4 · cases per 1,000 person-years, exact 95% intervals; shaded: overlap · difference: exact test · p = 0.021 · efficacy 20.1% to 99.7%, excluding zero · "no overlap" read as a test · 0.56% · equal standard errors; power 51% where the test has 80% · Test the difference itself: overlap of two · 95% intervals is not a 5% test. · CONFIDENCE INTERVALS · CANERY.IN
- Alt text: Card showing two overlapping rate intervals for severe Covid-19, a significant difference at p = 0.021, and the overlap rule's 0.56% error.
- Long description: After the first dose, 10 participants in the BNT162b2 trial had severe Covid-19: 1 in the vaccine group and 9 in the placebo group. Each arm's rate per 1,000 person-years has an exact 95% interval, vaccine 0.25 and placebo 2.25, and the two intervals overlap. The exact test of the difference gives p = 0.021, and the efficacy interval, 20.1% to 99.7%, excludes zero. Read as a test, 'the 95% intervals do not overlap' rejects a true null only 0.56% of the time when the standard errors are equal, and has 51% power where the standard test has 80%. Takeaway: test the difference itself.
- Keywords: overlapping confidence intervals, significance, Schenker and Gentleman, statistical power, vaccine trial
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage

### feed-07-t-interval-on-skewed-data

- File: `assets/social/feed-07-t-interval-on-skewed-data.png`
- Title: A 95% t-interval that covers 66%
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: On real customer spend with skewness 21.6, the 95% t-interval for the mean covers 65.8% at n = 30, lies wholly below the mean in 34.2% of samples, and sorted by width its narrowest tenth never contains the mean
- Technical source: Does the t-interval keep its promise on skewed data?; Figures 9 and 10; ledger L29, L30
- Visual structure: lockup and counter; serif title; deck; a panel with two labelled statistics and ten bars of coverage by tenth of interval width with a dashed 95% line; a note; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · A 95% t-interval · that covers 66%. · Real customer spend is so skewed that · a sample of 30 usually misses the big spenders. · 95% t-interval for mean spend, 4,317 customers, n = 30 · covers the true mean · 65.8% · of 200,000 samples · lies wholly below the mean · 34.2% · above it: 1 in 200,000 · coverage by tenth of interval width, narrowest first · 95% · 100 · 100 · 100 · 100 · 99 · 89 · 55 · 15 · 1 · 0 · skewness 21.6; at n = 1,000 coverage is still 85.65% · On skewed data the narrow intervals are the · ones that miss: none of the narrowest tenth covers. · CONFIDENCE INTERVALS · CANERY.IN
- Alt text: Card on the t-interval for mean customer spend at n = 30: 65.8% coverage, and none of the narrowest tenth of intervals covers.
- Long description: The net spend of 4,317 customers of an online retailer has skewness 21.6. Sampling 30 customers with replacement, the 95% t-interval for the mean contains the true mean in 65.8% of 200,000 samples and lies wholly below it in 34.2%; it lies above it in 1 of 200,000. Sorted into tenths by width, the narrowest tenth never contains the mean, the next covers 1%, the third 15%, and the widest half almost always. At n = 1,000 coverage is still 85.65%. Takeaway: on skewed data the narrow intervals are the ones that miss.
- Keywords: t-interval, coverage, skewness, relevant subsets, customer spend, Monte Carlo
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Confidence intervals: what 95% means
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's four results in one list, and the call to read it
- Technical source: Insights; Key takeaways; the lab
- Visual structure: lockup and counter; serif title; deck; a panel of four headed results; takeaway; the call to action with the article's URL
- Visible-text transcript: Canery.in · 08 / 08 · Confidence intervals: · what 95% means. · Every number computed exactly or measured by · a seeded lab you can rerun in 20 seconds. · coverage, summed exactly · 20 audits at p = 0.1: Wald 87.6%, Wilson 95.7% · which interval for a proportion · Clopper–Pearson never below 95.08% at n = 50 · a vaccine trial and overlapping intervals · 90.0% to 97.9% reproduced; no overlap is a 0.56% test · the t-interval on skewed data · customer spend at n = 30: 65.8% coverage · The full walk-through, with the lab and every · simulated number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/CONFIDENCE-INTERVALS-COVERAGE
- Alt text: Closing card listing the article's four results on coverage, choosing an interval, a vaccine trial and skewed data, with the link.
- Long description: A summary of the article in four results: exact coverage for 20 audits at p = 0.1 is 87.6% for the Wald interval and 95.7% for Wilson's; the Clopper–Pearson interval never falls below 95.08% at n = 50; the trial's 90.0% to 97.9% reproduces, and judging by non-overlap is a 0.56% test; customer spend at n = 30 gives the t-interval 65.8% coverage. Every number is computed exactly or measured by a seeded lab that reruns in about 20 seconds. The call to action points to canery.in/blogs/confidence-intervals-coverage.
- Keywords: confidence intervals, statistics, data science, coverage, Python lab
- Canonical URL: https://canery.in/blogs/confidence-intervals-coverage
