---
social_schema: 2
canonical_url: "https://canery.in/blogs/sampling-distribution-central-limit-theorem"
---

# Social publishing package — sampling-distribution-central-limit-theorem

## LinkedIn post

Run a 5% t-test of a true mean on real revenue data, and at n = 30 it rejects 39.8% of the time. The "n ≥ 30" rule is a rule of thumb, not a theorem.

The second part of Statistics for Data Scientists measures the central limit theorem instead of quoting it, on the net spend of 4,317 customers of a UK online retailer (skewness 21.6):

→ The mean's spread is σ/√n, £1,509 at n = 30. The estimate a t-test divides by is typically £386.
→ One tail of the t-test fires 39.8% of the time at n = 30, the other 0.05%. At n = 1,000 it is still 17.7% against 0.9%.
→ Why: three samples in four miss the 43 biggest customers, so their mean and SD fall together (correlation 0.972).
→ The error is about 11 points × skewness/√n, so the n you need grows like skewness squared: about 2,000 for an exponential to stay within half a point of 5%.
→ Berry–Esseen guarantees the mean's distribution is within 0.01 of normal only from n = 1,025,322; the exact distance gets there at 20,652.
→ With infinite variance it never arrives: a Pareto t-test with tail index 1.5 stalls near 26%.

Every number comes from a seeded lab, with its Monte Carlo standard error, that you can rerun in under four minutes.

## LinkedIn first comment

The pace of the central limit theorem is set by skewness over √n, not by a magic n. Simulate your own test on data like yours, and print every simulated rate with its Monte Carlo error.

Read the full article on Canery: https://canery.in/blogs/sampling-distribution-central-limit-theorem

## Instagram caption

Is n = 30 enough for the CLT? On real customer spend, a 5% t-test of the true mean rejects 39.8% of the time at n = 30. Swipe through the population, the standard error and its estimate, why one tail fires, the skewness rule, Berry–Esseen's slow guarantee, and what infinite variance does.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #centrallimittheorem #ttest #probability #python #abtesting

## Shared feed order

1. `assets/social/feed-01-n-30-is-not-a-theorem.png` — a nominal 5% t-test of the true mean on real customer spend rejects 39.8% of the time in the lower tail and 0.05% in the upper at n = 30, and is still off at n = 1,000 and 10,000
2. `assets/social/feed-02-a-few-whales.png` — the population: median spend £658 against a mean of £1,926, 79.1% of customers below the mean, and the top 1% holding 29.7% of all spend
3. `assets/social/feed-03-sd-is-not-se.png` — σ = £8,267 describes one customer, the standard error σ/√30 = £1,509 describes a mean of 30, and the typical sample estimate s/√30 is only £386
4. `assets/social/feed-04-why-one-tail-fires.png` — 74.1% of samples of 30 miss the 43 biggest customers, have a low mean and a small s, and are rejected 53.7% of the time; the 25.9% that hold one are never rejected; mean and s correlate 0.972
5. `assets/social/feed-05-skewness-sets-the-pace.png` — at n = 30 the one-sided t-test's tails are 4.93/4.98% for the normal, 9.84/2.26% for the exponential, 15.44/0.98% for the standard lognormal and 39.82/0.05% for the spend; the lower tail is about 5% + 11.02 points × γ/√n
6. `assets/social/feed-06-guaranteed-vs-good-enough.png` — the exact distance between the standardised mean of spend and the normal falls to 0.01 at n = 20,652, but Berry–Esseen guarantees it only from n = 1,025,322
7. `assets/social/feed-07-no-n-is-enough.png` — the interquartile range of a Cauchy mean stays at 2.00 from n = 1 to 1,000, and a Pareto (tail index 1.5) t-test's lower tail stalls near 26.4%
8. `assets/social/feed-08-read-the-article.png` — the four ideas of the article in one list, and the call to read it

## Instagram Story

- CTA: n = 30 is a rule of thumb. Measured on real data, the CLT takes far longer — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### Story order

1. `assets/social/story-01-n-30-is-not-a-theorem.png` — Overlay: At n = 30, a 5% test fires 39.8% of the time.
2. `assets/social/story-02-sd-is-not-se.png` — Overlay: σ £8,267, true SE £1,509, typical estimate £386.
3. `assets/social/story-03-skewness-sets-the-pace.png` — Overlay: The error grows with skewness over √n.
4. `assets/social/story-04-read-the-article.png` — Overlay: The sampling distribution. Link below.

## Asset metadata

### feed-01-n-30-is-not-a-theorem

- File: `assets/social/feed-01-n-30-is-not-a-theorem.png`
- Title: n = 30 is a rule of thumb, not a theorem
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: a nominal 5% t-test of the true mean on real customer spend rejects 39.8% of the time in the lower tail and 0.05% in the upper at n = 30, and is still off at n = 1,000 and 10,000
- Technical source: Insights; Worked example, the t-test's two tails; Figure 4
- Visual structure: lockup and counter; serif title; deck; a panel with the two n = 30 rates as large numbers, a rule, the n = 1,000 and n = 10,000 rates in two rows, and a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · n = 30 is a rule of thumb, · not a theorem. · A t-test on real customer spend, with the · true mean as the null it should keep. · a 5% t-test of the true mean, n = 30 customers · 39.8% · lower tail: rejects a true mean · 0.05% · upper tail · each test is built to reject 5% of the time · n = 1,000: · lower 17.7% · upper 0.9% · n = 10,000: · lower 7.9% · upper 3.0% · R = 100,000 samples per n, MCSE at most 0.16 points · 4,317 real customers' net spend, skewness 21.6 · The central limit theorem is a limit. · It never promised a sample size. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: A 5% t-test of the true mean on real customer spend at n = 30: 39.8% false rejections in the lower tail and 0.05% in the upper, still off at n = 10,000.
- Long description: On the net spend of 4,317 customers (skewness 21.6), a one-sided t-test of the true mean, built to reject 5% of the time in each direction, rejects 39.8% of the time in the lower tail and 0.05% in the upper tail at n = 30; 17.7% and 0.9% at n = 1,000; and 7.9% and 3.0% at n = 10,000. Each rate comes from 100,000 simulated samples, with a Monte Carlo standard error of at most 0.16 points. The takeaway: the central limit theorem is a limit and never promised a sample size.
- Keywords: central limit theorem, n = 30 rule, t-test, type I error, skewness, sampling distribution
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### feed-02-a-few-whales

- File: `assets/social/feed-02-a-few-whales.png`
- Title: A few whales, many minnows
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the population: median spend £658 against a mean of £1,926, 79.1% of customers below the mean, and the top 1% holding 29.7% of all spend
- Technical source: Worked example, the population; Figure 1; ledger L01
- Visual structure: lockup and counter; serif title; deck; a panel with the median and mean as large numbers, a bar showing the top 1%'s share of spend, and two lines of facts; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · A few whales, · many minnows. · Revenue per customer is the kind of number · people average and test every day. · net spend of 4,317 customers, Dec 2010 to Dec 2011 · £658 · median customer · £1,926 · mean · share of all spend held by the top 1% (43 customers) · 29.7% · 79.1% of customers spend less than the mean · largest £279,489: 33.6 SDs above the mean · skewness 21.6; UCI Online Retail, CC BY 4.0 · Most customers sit below the mean. · That is where the trouble starts. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: Net spend of 4,317 customers: median £658, mean £1,926, and a bar showing the top 1% holding 29.7% of all spend.
- Long description: The population is the net spend of 4,317 customers of a UK online retailer between December 2010 and December 2011, from the UCI Online Retail dataset (CC BY 4.0). The median customer spent £658 and the mean is £1,926; 79.1% of customers spend less than the mean. The 43 biggest customers, the top 1%, hold 29.7% of all spend, drawn as a bar, and the largest spent £279,489, 33.6 standard deviations above the mean. The skewness is 21.6. The takeaway: most customers sit below the mean, which is where the t-test's trouble starts.
- Keywords: revenue per customer, skewed distribution, median vs mean, Online Retail dataset, skewness
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### feed-03-sd-is-not-se

- File: `assets/social/feed-03-sd-is-not-se.png`
- Title: The SD is not the SE, and its estimate runs small
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: σ = £8,267 describes one customer, the standard error σ/√30 = £1,509 describes a mean of 30, and the typical sample estimate s/√30 is only £386
- Technical source: Worked example, standard deviation or standard error; Figure 3; ledger L04
- Visual structure: lockup and counter; serif title; deck; a panel with three labelled rows (σ, σ/√30, s/√30), each with its value and a bar on a log scale, then two lines on s and s²; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · The SD is not the SE, · and its estimate runs small. · Spread of customers, spread of means, and · what a t-test actually divides by. · σ · one customer's spread · £8,267 · σ/√30 · true standard error of a mean of 30 · £1,509 · s/√30 · what a typical sample estimates · £386 · bar length: log of the amount, £1 to σ · s < σ in 88.1% of samples of 30 · yet s² averages 0.986 × σ²: unbiased, not typical · The typical estimate is a quarter · of the true standard error. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: Three amounts for 30 customers' spend: σ £8,267, true standard error £1,509, and the typical estimate s/√30 of just £386.
- Long description: The standard deviation σ = £8,267 is the spread of one customer's spend. The standard error of a mean of 30 customers is σ/√30 = £1,509. The estimate a t-test divides by, s/√30, is typically only £386, because the sample SD s falls below σ in 88.1% of samples of 30, even though s² averages 0.986 times σ² and is unbiased. Bars show each amount on a log scale from £1 to σ. The takeaway: the typical estimate is a quarter of the true standard error.
- Keywords: standard error, standard deviation, SE vs SD, sample standard deviation, t-test
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### feed-04-why-one-tail-fires

- File: `assets/social/feed-04-why-one-tail-fires.png`
- Title: Why one tail fires and the other almost never
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: 74.1% of samples of 30 miss the 43 biggest customers, have a low mean and a small s, and are rejected 53.7% of the time; the 25.9% that hold one are never rejected; mean and s correlate 0.972
- Technical source: Intuition; Figure 5
- Visual structure: lockup and counter; serif title; deck; a panel in two columns (samples that miss the big customers in tangerine, samples that hold one in blue), each with its share, its mean and s, and its rejection rate, then the correlation and the t formula; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Why one tail fires · and the other almost never. · Count the big customers in each sample · of 30. · 74.1% · of samples of 30 miss the · 43 biggest customers · mean below μ: 92.4% · s small, from the same · small values · rejected: 53.7% · 25.9% · hold one of them · mean lifted, s inflated · far more, so t stays · small · rejected: 0 of 25,855 · correlation of sample mean and SD: 0.972 · t = (mean − μ) / (s/√n): a low mean over a small s · is a very negative t · n = 30, R = 100,000 samples · The mean and the SD fall together, · so the t statistic is skewed too. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: Samples of 30 that miss the 43 biggest customers are rejected 53.7% of the time; those that hold one are never rejected.
- Long description: Of samples of 30 customers, 74.1% miss all 43 of the biggest customers: their mean falls below the true mean 92.4% of the time and their standard deviation is small, because it comes from the same small values, so the t statistic is very negative and the lower-tail test rejects 53.7% of them. The 25.9% that hold one of the big customers have a lifted mean and a far more inflated s, so t stays small: none of 25,855 is rejected. Across 100,000 samples the correlation of sample mean and SD is 0.972. The takeaway: the mean and the SD fall together, so the t statistic is skewed too.
- Keywords: t statistic, skewness, sample mean, sample standard deviation, correlation, t-test failure
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### feed-05-skewness-sets-the-pace

- File: `assets/social/feed-05-skewness-sets-the-pace.png`
- Title: Skewness sets the pace, not n = 30
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: at n = 30 the one-sided t-test's tails are 4.93/4.98% for the normal, 9.84/2.26% for the exponential, 15.44/0.98% for the standard lognormal and 39.82/0.05% for the spend; the lower tail is about 5% + 11.02 points × γ/√n
- Technical source: How fast does the CLT work; Figure 7; ledger L11, L12
- Visual structure: lockup and counter; serif title; deck; a panel with a four-row table of skewness and lower/upper tail rates at n = 30, the first-order rule, and the sample sizes it implies; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Skewness sets the pace, · not n = 30. · The same test on populations of known · skewness, R = 100,000 each. · one-sided 5% t-test at n = 30: lower / upper tail · γ · normal · 0.00 · 4.93% / 4.98% · exponential · 2.00 · 9.84% / 2.26% · standard lognormal · 6.18 · 15.44% / 0.98% · customer spend · 21.58 · 39.82% / 0.05% · lower tail ≈ 5% + 11.02 points × γ/√n · so within 10% of 5% needs n ≥ 486 γ²: · exponential 1,943, spend 226,264 or more · first-order Edgeworth term, checked by simulation · n = 30 keeps a one-sided test within · 10% of 5% only if γ is below 0.25. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: A table of one-sided t-test error rates at n = 30 for four populations of rising skewness, from 4.93% for the normal to 39.82% for spend.
- Long description: The same one-sided 5% t-test at n = 30, with 100,000 simulated samples each: the normal (skewness 0) rejects 4.93% in the lower tail and 4.98% in the upper; the exponential (2.00) 9.84% and 2.26%; the standard lognormal (6.18) 15.44% and 0.98%; customer spend (21.58) 39.82% and 0.05%. The first-order Edgeworth rule puts the lower tail at about 5% + 11.02 points × γ/√n, so keeping it within 10% of 5% needs n ≥ 486γ²: 1,943 for the exponential and at least 226,264 for the spend. The takeaway: n = 30 keeps a one-sided test within 10% of 5% only if the skewness is below 0.25.
- Keywords: skewness, Edgeworth expansion, sample size, t-test robustness, exponential distribution, lognormal
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### feed-06-guaranteed-vs-good-enough

- File: `assets/social/feed-06-guaranteed-vs-good-enough.png`
- Title: A guarantee is too slow to plan with
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the exact distance between the standardised mean of spend and the normal falls to 0.01 at n = 20,652, but Berry–Esseen guarantees it only from n = 1,025,322
- Technical source: What does Berry–Esseen guarantee; Figure 8; ledger L17, L18
- Visual structure: lockup and counter; serif title; deck; a panel with two large sample sizes (exact, guaranteed), the bound's formula and β₃, the exponential's pair, and a method note; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · A guarantee is too slow · to plan with. · The Berry–Esseen bound against the exact · distance for the same spend data. · largest gap to the normal CDF falls to 0.01 at · 20,652 · customers: the exact distance · 1,025,322 · guaranteed by Berry–Esseen · bound = 0.469 × β₃ / √n, β₃ = 21.59 · exponential: 177 exact, 12,824 guaranteed · exact distance by inverting the characteristic function · The guarantee arrives 50 times later · than the normal shape does. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: The largest gap to the normal falls to 0.01 at n = 20,652 for spend; Berry–Esseen guarantees it only from n = 1,025,322.
- Long description: For the customer-spend population, the Kolmogorov distance between the standardised sample mean's distribution and the normal, computed exactly by inverting the characteristic function, falls to 0.01 at n = 20,652. The Berry–Esseen bound, 0.469 × β₃/√n with β₃ = 21.59, guarantees that distance only from n = 1,025,322. For an exponential population the pair is 177 exact against 12,824 guaranteed. The takeaway: the guarantee arrives 50 times later than the normal shape does.
- Keywords: Berry-Esseen theorem, Kolmogorov distance, central limit theorem rate, characteristic function
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### feed-07-no-n-is-enough

- File: `assets/social/feed-07-no-n-is-enough.png`
- Title: Infinite variance: no n is enough
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the interquartile range of a Cauchy mean stays at 2.00 from n = 1 to 1,000, and a Pareto (tail index 1.5) t-test's lower tail stalls near 26.4%
- Technical source: When does the CLT never arrive; Figure 9; ledger L20–L23
- Visual structure: lockup and counter; serif title; deck; a panel with two blocks: Cauchy spreads at four n, and Pareto lower-tail rates at four n; a note and a provenance line; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Infinite variance: · no n is enough. · The CLT needs a finite variance. · Take it away and the normal never comes. · Cauchy · spread (IQR) of the mean of n draws · n = 1 · 2.00 · n = 10 · 2.00 · n = 100 · 2.03 · n = 1,000 · 2.00 · Pareto, tail index 1.5 · one-sided 5% t-test, lower tail · n = 10 · 42.6% · n = 1,000 · 28.6% · n = 10,000 · 26.4% · n = 100,000 · 26.4% · the mean exists; the variance does not · lab simulation; Cauchy R = 20,000, Pareto R = 20,000 (2,000 at n = 100,000) · Averaging a Cauchy gains nothing; a Pareto · t-test stalls near 26%. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: A Cauchy mean's spread stays at 2.00 from n = 1 to 1,000; a Pareto t-test with tail index 1.5 stalls near 26.4% in the lower tail.
- Long description: The central limit theorem needs a finite variance. For the Cauchy distribution, the interquartile range of the mean of n draws is 2.00, 2.00, 2.03 and 2.00 at n = 1, 10, 100 and 1,000: averaging gains nothing. For a Pareto with tail index 1.5, whose mean exists but whose variance does not, a one-sided 5% t-test rejects 42.6% in the lower tail at n = 10, 28.6% at 1,000, 26.4% at 10,000 and 26.4% at 100,000. All values are from the lab's simulations. The takeaway: averaging a Cauchy gains nothing and a Pareto t-test stalls near 26%.
- Keywords: infinite variance, Cauchy distribution, Pareto distribution, stable law, heavy tails, generalized central limit theorem
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: The sampling distribution: read the article
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four ideas of the article in one list, and the call to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel with four short headed entries; takeaway; call to action with the URL
- Visible-text transcript: Canery.in · 08 / 08 · The sampling · distribution. · Every number measured by a seeded lab · you can rerun in under four minutes. · sampling distribution · a statistic is a random variable · SE = σ/√n = £1,509 at n = 30 · Student's t · corrects for estimating σ, not for skew · 1.96 with an estimated σ: 8.16% at n = 10 · the pace · error ≈ 0.110 γ/√n · spend: 39.8% at n = 30 · Monte Carlo error · every simulated rate ± its MCSE · √(p(1 − p)/R) · The full walk-through, with the lab · and every number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/SAMPLING-DISTRIBUTION-CENTRAL-LIMIT-THEOREM
- Alt text: Four ideas from the article: the sampling distribution, Student's t, the skewness rule, and Monte Carlo error, with a link to read it.
- Long description: The closing card lists four ideas: a statistic is a random variable whose spread is SE = σ/√n (£1,509 at n = 30 for the spend); Student's t corrects for estimating σ, not for skew (using 1.96 with an estimated σ rejects 8.16% at n = 10); the pace of the error is about 0.110 γ/√n (39.8% at n = 30 for the spend); and every simulated rate should carry its Monte Carlo standard error, √(p(1 − p)/R). It invites the reader to the full article, whose lab reruns every number in under four minutes.
- Keywords: sampling distribution, central limit theorem, Student's t, Monte Carlo standard error, statistics for data scientists
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### story-01-n-30-is-not-a-theorem

- File: `assets/social/story-01-n-30-is-not-a-theorem.png`
- Title: n = 30 is not a theorem
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: a 5% t-test of the true mean on real spend at n = 30 fires 39.8% of the time in the lower tail and 0.05% in the upper
- Technical source: Insights; Figure 4
- Visual structure: lockup and counter; serif title; deck; a panel with the two rates stacked as large numbers and a source line; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · n = 30 is not · a theorem. · Each tail is built to fire · 5% of the time. · 5% t-test of the true mean, n = 30 · 39.8% · lower tail: false alarms · 0.05% · upper tail · real spend of 4,317 customers · Skewness, not 30, sets · the sample size you need. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: At n = 30, a 5% t-test of the true mean on real spend fires 39.8% of the time in the lower tail and 0.05% in the upper.
- Long description: Each tail of a one-sided t-test at 5% is built to fire 5% of the time. On the real spend of 4,317 customers, at n = 30, the lower tail fires 39.8% of the time when the null is true, false alarms, and the upper tail 0.05%. The takeaway: skewness, not 30, sets the sample size you need.
- Keywords: central limit theorem, n = 30, t-test, false alarm, skewness
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### story-02-sd-is-not-se

- File: `assets/social/story-02-sd-is-not-se.png`
- Title: The SD is not the SE
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: σ = £8,267, the true standard error £1,509 at n = 30, and the typical estimate £386
- Technical source: Worked example, standard deviation or standard error; Figure 3
- Visual structure: lockup and counter; serif title; deck; a panel with three rows (σ, σ/√30, s/√30) and their amounts; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · The SD is not · the SE. · And the SE a sample estimates · is usually far too small. · σ · one customer · £8,267 · σ/√30 · true SE · £1,509 · s/√30 · typical estimate · £386 · s < σ in 88.1% of · samples of 30. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: Three amounts: σ £8,267 for one customer, true standard error £1,509 at n = 30, and a typical estimate of £386.
- Long description: For the spend of 4,317 customers, σ = £8,267 is one customer's spread, σ/√30 = £1,509 is the true standard error of a mean of 30, and s/√30 = £386 is what a typical sample estimates. The takeaway: s falls below σ in 88.1% of samples of 30, so the estimated standard error is usually far too small.
- Keywords: standard error, standard deviation, SE vs SD, t-test
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### story-03-skewness-sets-the-pace

- File: `assets/social/story-03-skewness-sets-the-pace.png`
- Title: Skewness sets the pace
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: lower-tail error at n = 30: normal 4.9%, exponential 9.8%, lognormal 15.4%, spend 39.8%; about 5% + 11.02 points × γ/√n
- Technical source: How fast does the CLT work; Figure 7
- Visual structure: lockup and counter; serif title; deck; a panel with four rows of lower-tail rates and the first-order rule; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Skewness sets · the pace. · The same 5% test on · four populations. · one-sided error at n = 30 · normal · 4.9% · exponential · 9.8% · lognormal · 15.4% · spend · 39.8% · ≈ 5% + 11.02 points × γ/√n · lower tail; nominal 5% in each row · The sample size you need · grows like skewness squared. · THE SAMPLING DISTRIBUTION · CANERY.IN
- Alt text: Lower-tail error of a 5% t-test at n = 30: normal 4.9%, exponential 9.8%, lognormal 15.4%, spend 39.8%.
- Long description: The same one-sided 5% t-test at n = 30 rejects in the lower tail 4.9% of the time for the normal, 9.8% for the exponential, 15.4% for the standard lognormal and 39.8% for customer spend. The first-order rule puts the lower tail at about 5% + 11.02 points × γ/√n. The takeaway: the sample size you need grows like skewness squared.
- Keywords: skewness, sample size, t-test, Edgeworth expansion, central limit theorem
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: The sampling distribution: read the article
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: four steps that sum up the article, and the link sticker
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel with four numbered steps; takeaway; call to action pointing to the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · The sampling · distribution. · The CLT, measured on real data, · with a lab you can rerun. · 1 · a statistic is a random variable · 2 · SE = σ/√n, and s/√n runs small · 3 · the error scales with γ/√n · 4 · print every simulated rate ± MCSE · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Four numbered steps from the article, from a statistic being a random variable to printing every simulated rate with its MCSE.
- Long description: The closing Story frame lists four steps: a statistic is a random variable; SE = σ/√n, and the estimate s/√n runs small; the error scales with γ/√n; print every simulated rate with its Monte Carlo standard error. It points to the link sticker for the full walk-through on Canery.
- Keywords: sampling distribution, standard error, skewness, Monte Carlo standard error, Canery
- Canonical URL: https://canery.in/blogs/sampling-distribution-central-limit-theorem
