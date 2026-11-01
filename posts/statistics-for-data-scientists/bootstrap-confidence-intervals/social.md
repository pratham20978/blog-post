---
social_schema: 2
canonical_url: "https://canery.in/blogs/bootstrap-confidence-intervals"
---

# Social publishing package — bootstrap-confidence-intervals

## LinkedIn post

The bootstrap gives a standard error and a confidence interval for statistics with no formula: a correlation, a median, a ratio. It is often called assumption-free. It is not: it treats the sample as the population.

The seventh part of Statistics for Data Scientists measures what that costs:

→ Efron and Tibshirani's 15 law schools are a sample from a published population of 82, so every interval's real coverage can be measured. For the LSAT–GPA correlation at n = 15: percentile 91.0%, BCa 92.0%, the basic interval 80.7%, Fisher's normal-theory interval 93.6%.
→ One sample, seven 95% intervals, from −0.46 to 1.10. Two of them reach above 1, which no correlation can.
→ BCa in two numbers: a bias correction from the share of replicates below the estimate, and an acceleration from the jackknife. Here one school of 15 supplies all of the acceleration.
→ On skewed customer spend at n = 30, the t-interval covers 66.0%, BCa 73.3% and the bootstrap-t 80.3%. Most samples hold none of the 44 customers who set the mean, and no resample can add them.
→ It fails outright for a maximum: bootstrapping five tank serial numbers puts 67% of the mass on the largest one, and percentile intervals cover the true count only when the last tank happens to be captured.

Every interval is computed by hand, matched to SciPy and R to 14 decimal places, and measured by a seeded lab.

## LinkedIn first comment

Before you trust a bootstrap interval, ask whether your sample could plausibly contain what the statistic depends on: its tail, its extremes, its time order. If it cannot, no rule for reading the replicates will fix it.

Read the full article on Canery: https://canery.in/blogs/bootstrap-confidence-intervals

## Instagram caption

Is the bootstrap assumption-free? No. Swipe through what it assumes, how one sample gives seven different 95% intervals, what BCa's two numbers do, how often each interval really covers when the population is known, why skewed data defeat it, and why a maximum breaks it outright.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #bootstrap #python #confidenceintervals #resampling

## Shared feed order

1. `assets/social/feed-01-not-assumption-free.png` — The bootstrap rests on three conditions; breaking each on purpose turned a nominal 95% interval into 73.5% (an AR(1) series), 64.8% (spend samples without a large customer) or 0% (a uniform maximum)
2. `assets/social/feed-02-one-sample-many-resamples.png` — One resample of the 15 law schools, then 10,000: the bootstrap SE of the correlation is 0.135 against a true 0.130 measured from the 82 schools, and the normal-theory formula's 0.115
3. `assets/social/feed-03-seven-answers.png` — Seven 95% intervals for the same correlation from the same replicates, from the percentile's 0.452 to 0.962 to the studentized −0.462 to 0.997; the basic and normal intervals reach above 1
4. `assets/social/feed-04-bca-in-two-numbers.png` — BCa's bias correction, z0 = −0.093, and its jackknife acceleration, a = −0.0757, move the percentile levels to 0.58% and 93.86%, giving 0.327 to 0.942; one school supplies 110% of the acceleration's numerator
5. `assets/social/feed-05-coverage-measured.png` — Coverage of seven 95% intervals over 20,000 fresh samples of 15 from the 82 schools: from 80.7% (basic) to 95.7% (studentized, by reaching past 1 in 23.5% of samples)
6. `assets/social/feed-06-missing-tail.png` — For mean customer spend at n = 30, four intervals' coverage overall and split by whether the sample holds a top-1% customer: BCa 73.3% overall, 64.8% without one, 97.0% with one
7. `assets/social/feed-07-the-maximum.png` — The exact bootstrap distribution of the largest of five tank serials puts 0.6723 on 303; percentile intervals cover N = 342 in 1.46% of captures, the basic interval in 75.73%, the exact bound at least 95%
8. `assets/social/feed-08-read-the-article.png` — The article's four results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-not-assumption-free

- File: `assets/social/feed-01-not-assumption-free.png`
- Title: The bootstrap is not assumption-free
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: The bootstrap rests on three conditions; breaking each on purpose turned a nominal 95% interval into 73.5% (an AR(1) series), 64.8% (spend samples without a large customer) or 0% (a uniform maximum)
- Technical source: The problem (the three conditions); Does the bootstrap rescue the skewed mean?; When does the bootstrap fail?; Figures 9, 11 and 13
- Visual structure: lockup and counter; serif title; deck; a panel listing the three conditions, each with the case that breaks it and the measured coverage in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · The bootstrap is not · assumption-free. · It treats the sample as the population. · Three conditions, each broken on purpose. · what each condition broken did to a 95% interval · the sample is drawn independently, · and resampled the way it was drawn · an AR(1) series, φ = 0.5 · SE 0.574 of the truth; covers 73.5% · the sample stands in · for the population · spend at n = 30, no top-1% customer · BCa covers 64.8% · the statistic changes smoothly · with the distribution · a uniform maximum · percentile and BCa cover 0% · Break one condition and a nominal 95% interval · covered 73.5%, 64.8% or 0%. · THE BOOTSTRAP · CANERY.IN
- Alt text: Card listing the bootstrap's three conditions and what breaking each did to a 95% interval: 73.5%, 64.8% and 0% coverage.
- Long description: The bootstrap assumes that the data are an independent sample resampled the way it was drawn, that the sample stands in for the population, and that the statistic changes smoothly with the distribution. Resampling single points of an autocorrelated AR(1) series with φ = 0.5 estimated 0.574 of the true standard error of the mean, and the percentile interval covered 73.5%. For mean customer spend at n = 30, samples holding none of the top 1% of customers were covered by BCa 64.8% of the time. For the maximum of a uniform sample, percentile and BCa intervals for the upper endpoint cover 0%. Takeaway: break one condition and a nominal 95% interval covered 73.5%, 64.8% or 0%.
- Keywords: bootstrap, confidence interval, coverage, BCa, assumptions, dependent data, sample maximum
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals

### feed-02-one-sample-many-resamples

- File: `assets/social/feed-02-one-sample-many-resamples.png`
- Title: One sample, 10,000 resamples
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: One resample of the 15 law schools, then 10,000: the bootstrap SE of the correlation is 0.135 against a true 0.130 measured from the 82 schools, and the normal-theory formula's 0.115
- Technical source: Worked example (one resample; the bootstrap standard error); Figure 2; ledger L04, L07
- Visual structure: lockup and counter; serif title; deck; a panel with the first resample's 15 row numbers, its distinct count and correlation, then three standard errors as large numbers: bootstrap (blue), true (ink), normal theory (tangerine); takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · One sample, · 10,000 resamples. · Resample the 15 schools with replacement; · the spread of the replicates is the SE. · the correlation of LSAT and GPA in 15 law schools · one resample: 15 rows drawn with replacement · 10 13 15 11 11 6 15 5 · 6 12 8 3 12 2 1 · 11 distinct schools; r* = 0.720 · bootstrap SE, 10,000 resamples · 0.135 · true SE, 1,000,000 fresh samples · 0.130 · of 15 from all 82 schools · normal-theory formula · 0.115 · (1 − r²)/√(n − 3) · The bootstrap SE was 0.135 against a true 0.130; · the textbook formula gave 0.115. · THE BOOTSTRAP · CANERY.IN
- Alt text: Card showing one bootstrap resample of 15 law schools and three standard errors for their correlation: 0.135, 0.130 and 0.115.
- Long description: The correlation between average LSAT score and average GPA in 15 law schools is 0.776. One bootstrap resample draws 15 rows with replacement, here rows 10, 13, 15, 11, 11, 6, 15, 5, 6, 12, 8, 3, 12, 2 and 1: 11 distinct schools, with correlation 0.720. Over 10,000 resamples the replicates' standard deviation, the bootstrap standard error, is 0.135. The true standard error, measured from a million fresh samples of 15 from all 82 schools, is 0.130; the normal-theory formula (1 − r²)/√(n − 3) gives 0.115. Takeaway: the bootstrap standard error was 0.135 against a true 0.130; the textbook formula gave 0.115.
- Keywords: bootstrap, standard error, resampling, correlation, law school data, normal theory
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals

### feed-03-seven-answers

- File: `assets/social/feed-03-seven-answers.png`
- Title: One correlation, seven 95% intervals
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Seven 95% intervals for the same correlation from the same replicates, from the percentile's 0.452 to 0.962 to the studentized −0.462 to 0.997; the basic and normal intervals reach above 1
- Technical source: Worked example (the seven intervals); Figure 4
- Visual structure: lockup and counter; serif title; deck; a panel with seven horizontal intervals on one axis from −0.55 to 1.15, a shaded band above 1, a line at r = 0.776, and each interval's limits in a right-hand column; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · One correlation, · seven 95% intervals. · The same 15 schools and the same replicates, · read seven ways. · 95% intervals from the same 10,000 replicates · above 1 · percentile · 0.452 to 0.962 · BCa · 0.327 to 0.942 · basic · 0.590 to 1.100 · normal, bootstrap SE · 0.511 to 1.042 · studentized · −0.462 to 0.997 · studentized, Fisher scale · −0.142 to 0.946 · Fisher z, normal theory · 0.439 to 0.922 · −0.5 · 0 · 0.5 · 1 · r = 0.776 · Two of the seven reach above 1, which · no correlation can. · THE BOOTSTRAP · CANERY.IN
- Alt text: Card with seven 95% intervals for one correlation of 0.776, from 0.452–0.962 to −0.462–0.997; two run past 1.
- Long description: From the same 10,000 bootstrap replicates of the 15 law schools' correlation, seven 95% intervals: percentile 0.452 to 0.962; BCa 0.327 to 0.942; basic 0.590 to 1.100; normal with the bootstrap standard error 0.511 to 1.042; studentized −0.462 to 0.997; studentized on Fisher's scale −0.142 to 0.946; Fisher's normal-theory z interval 0.439 to 0.922. The basic and normal intervals reach above 1, in a shaded band no correlation can enter. Takeaway: two of the seven reach above 1, which no correlation can.
- Keywords: bootstrap confidence interval, percentile interval, BCa, basic interval, studentized interval, Fisher z
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals

### feed-04-bca-in-two-numbers

- File: `assets/social/feed-04-bca-in-two-numbers.png`
- Title: BCa in two numbers
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: BCa's bias correction, z0 = −0.093, and its jackknife acceleration, a = −0.0757, move the percentile levels to 0.58% and 93.86%, giving 0.327 to 0.942; one school supplies 110% of the acceleration's numerator
- Technical source: Worked example (BCa); How does each interval turn replicates into limits?; Figures 3 and 6; ledger L08
- Visual structure: lockup and counter; serif title; deck; a panel with z0 and a as large blue numbers with their sources, then the adjusted percentile levels and the resulting BCa and percentile intervals; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · BCa in · two numbers. · A bias correction from the replicates and · an acceleration from the jackknife. · BCa: the percentile interval, re-aimed by two numbers · bias correction z0 · −0.093 · 4,630 of 10,000 replicates below r · acceleration a · −0.0757 · from the jackknife; school 6 is 110% of Σd³ · percentile levels read · 2.5% → 0.58% · 97.5% → 93.86% · BCa: 0.327 to 0.942 · percentile: 0.452 to 0.962 · One school of 15 set the acceleration, and · BCa's lower limit is the replicates' 0.58% point. · THE BOOTSTRAP · CANERY.IN
- Alt text: Card showing BCa's two inputs, z0 of −0.093 and a of −0.0757, moving the percentile levels to 0.58% and 93.86%.
- Long description: BCa starts from the percentile interval. Its bias correction z0 is the standard normal quantile of the share of replicates below the estimate: 4,630 of 10,000, so z0 = −0.093. Its acceleration a comes from the jackknife, the 15 leave-one-out correlations: a = −0.0757, and school 6 alone supplies 110% of the numerator Σd³. Together they move the nominal 2.5% and 97.5% levels to 0.58% and 93.86%, so BCa reads the replicates' 0.58% and 93.86% points: 0.327 to 0.942, against the percentile interval's 0.452 to 0.962. Takeaway: one school of 15 set the acceleration, and BCa's lower limit is the replicates' 0.58% point.
- Keywords: BCa, bias correction, acceleration, jackknife, bootstrap, confidence interval
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals

### feed-05-coverage-measured

- File: `assets/social/feed-05-coverage-measured.png`
- Title: 95% intervals that covered 81% to 96%
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Coverage of seven 95% intervals over 20,000 fresh samples of 15 from the 82 schools: from 80.7% (basic) to 95.7% (studentized, by reaching past 1 in 23.5% of samples)
- Technical source: Which interval keeps its promise for the law schools?; Figure 7
- Visual structure: lockup and counter; serif title; deck; a panel with one dot per interval on a coverage axis from 78% to 98%, a dashed line at 95%, and each coverage printed beside its dot; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · 95% intervals that · covered 81% to 96%. · The 82 schools are published, so each · interval's real coverage can be measured. · 20,000 fresh samples of 15 from the 82 schools · 80% · 85% · 90% · 95% · studentized · 95.7% · studentized, Fisher scale · 93.8% · Fisher z, normal theory · 93.6% · BCa · 92.0% · percentile · 91.0% · normal, bootstrap SE · 89.0% · basic · 80.7% · BCa 92.0%, percentile 91.0%, basic 80.7%; the studentized · 95.7% only by reaching past 1 in 23.5% of samples. · THE BOOTSTRAP · CANERY.IN
- Alt text: Card plotting measured coverage of seven 95% intervals for the law-school correlation, from 80.7% for basic to 95.7%.
- Long description: Because the 82 law schools are published, fresh samples of 15 can be drawn from them and each interval checked against the true correlation, 0.760. Over 20,000 samples with 2,000 replicates each: studentized 95.7%, studentized on Fisher's scale 93.8%, Fisher's normal-theory z interval 93.6%, BCa 92.0%, percentile 91.0%, normal with the bootstrap standard error 89.0%, basic 80.7%. The studentized interval reaches 95% only by producing upper limits above 1 in 23.5% of samples. Takeaway: BCa 92.0%, percentile 91.0%, basic 80.7%; the studentized interval's 95.7% comes from width.
- Keywords: coverage probability, bootstrap confidence interval, BCa, percentile interval, simulation, law school data
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals

### feed-06-missing-tail

- File: `assets/social/feed-06-missing-tail.png`
- Title: The bootstrap cannot resample what is missing
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: For mean customer spend at n = 30, four intervals' coverage overall and split by whether the sample holds a top-1% customer: BCa 73.3% overall, 64.8% without one, 97.0% with one
- Technical source: Does the bootstrap rescue the skewed mean?; Figure 9; ledger L35
- Visual structure: lockup and counter; serif title; deck; a table of four intervals by three columns (all samples, samples without a top-1% customer in tangerine, samples with one), and a note defining the top 1%; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · The bootstrap cannot · resample what is missing. · Skewed spend: most samples of 30 hold none · of the few customers who set the mean. · 95% intervals for mean customer spend, n = 30 · interval · all · no top-1% · with top-1% · t-interval · 66.0% · 53.8% · 100.0% · percentile · 66.8% · 55.0% · 99.8% · BCa · 73.3% · 64.8% · 97.0% · bootstrap-t · 80.3% · 73.5% · 99.4% · top 1%: the 44 customers who spent £17,507 or more, · 29.9% of all spending; 73.5% of samples of 30 hold none · BCa lifts coverage from 66.0% to 73.3%; no interval adds · customers the sample never caught. · THE BOOTSTRAP · CANERY.IN
- Alt text: Card tabling coverage for mean spend at n = 30: BCa 73.3% overall, 64.8% without a top-1% customer, 97.0% with one.
- Long description: Net spend of 4,317 customers is heavily skewed: the top 1%, 44 customers who spent £17,507 or more, account for 29.9% of all spending, and 73.5% of samples of 30 contain none of them. Coverage of 95% intervals for the mean at n = 30 over 20,000 samples: t-interval 66.0% (53.8% without a top-1% customer, 100.0% with one); percentile 66.8% (55.0%, 99.8%); BCa 73.3% (64.8%, 97.0%); bootstrap-t 80.3% (73.5%, 99.4%). Takeaway: BCa lifts coverage from 66.0% to 73.3%; no interval adds customers the sample never caught.
- Keywords: bootstrap, skewed data, coverage, BCa, bootstrap-t, customer spend
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals

### feed-07-the-maximum

- File: `assets/social/feed-07-the-maximum.png`
- Title: Bootstrap a maximum and 67% sits on one value
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The exact bootstrap distribution of the largest of five tank serials puts 0.6723 on 303; percentile intervals cover N = 342 in 1.46% of captures, the basic interval in 75.73%, the exact bound at least 95%
- Technical source: When does the bootstrap fail? (The maximum); Figures 10 and 11; ledger L21
- Visual structure: lockup and counter; serif title; deck; a panel with bars for the five serials' bootstrap probabilities, 303 in tangerine, then three intervals for N with their coverage over all captures; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Bootstrap a maximum · and 67% sits on one value. · Five serials, the largest 303, the truth 342. · No resample can exceed 303. · the largest of five tank serials, bootstrapped exactly · 58 · 0.0003 · 171 · 0.0099 · 272 · 0.0675 · 273 · 0.2499 · 303 · 0.6723 · percentile · 272 to 303 · 1.46% · basic · 303 to 334 · 75.73% · exact · 303 to 549 · at least 95% · covers N = 342 · Percentile and BCa intervals cover N only if · tank 342 itself was caught: 1.46% of captures. · THE BOOTSTRAP · CANERY.IN
- Alt text: Card showing the bootstrap distribution of five tank serials' maximum, 0.6723 on 303, and intervals for N = 342.
- Long description: Five captured tank serial numbers, 58, 171, 272, 273 and 303, from N = 342 tanks. Over all 3,125 equally likely resamples, the bootstrap maximum is 58 with probability 0.0003, 171 with 0.0099, 272 with 0.0675, 273 with 0.2499 and 303 with 0.6723, and never above 303. The 95% percentile interval for N is 272 to 303, the basic interval 303 to 334, and the exact one-sided bound from the distribution of the maximum 303 to 549. Over every capture of five tanks, the percentile interval covers N in 1.46% of captures, the basic in 75.73%, the exact bound at least 95%. Takeaway: percentile and BCa intervals cover N only if tank 342 itself was caught.
- Keywords: bootstrap failure, sample maximum, German tank problem, percentile interval, point mass, coverage
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: The bootstrap: what it assumes
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's four results in one list, and the call to read it
- Technical source: Insights; Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel with four headed lines, each with its number; takeaway; the canonical URL as the footer call to action
- Visible-text transcript: Canery.in · 08 / 08 · The bootstrap: · what it assumes. · Every interval computed by hand, matched to · SciPy and R, and measured by a seeded lab. · seven intervals, by hand · BCa: z0 −0.093, a −0.0757 → 0.327 to 0.942 · coverage, measured on the 82 schools · percentile 91.0%, BCa 92.0%, basic 80.7% · the skewed mean of part 6 · t 66.0% → BCa 73.3% → bootstrap-t 80.3% · where it breaks · the maximum, infinite variance, dependence · The full walk-through, with the lab and every · simulated number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/BOOTSTRAP-CONFIDENCE-INTERVALS
- Alt text: Closing card listing four results, from BCa's 0.327 to 0.942 to where the bootstrap breaks, with the article's address.
- Long description: A summary of the article: seven bootstrap intervals computed by hand, with BCa's z0 of −0.093 and a of −0.0757 giving 0.327 to 0.942; coverage measured on the 82-school population, percentile 91.0%, BCa 92.0% and basic 80.7%; the skewed mean from part 6, where coverage at n = 30 rises from the t-interval's 66.0% to BCa's 73.3% and the bootstrap-t's 80.3%; and the three failures, the maximum, infinite variance and dependence. Call to action: read it at canery.in/blogs/bootstrap-confidence-intervals.
- Keywords: bootstrap, confidence interval, BCa, coverage, statistics for data scientists
- Canonical URL: https://canery.in/blogs/bootstrap-confidence-intervals
