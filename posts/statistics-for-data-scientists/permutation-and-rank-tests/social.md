---
social_schema: 2
canonical_url: "https://canery.in/blogs/permutation-and-rank-tests"
---

# Social publishing package — permutation-and-rank-tests

## LinkedIn post

"Nonparametric" does not mean "assumes nothing". A permutation or rank test is exact for one hypothesis, and it is rarely the one people read into it.

The tenth part of Statistics for Data Scientists measures it:

→ Darwin's 15 pairs of maize plants, the data Fisher used in 1935: all 32,768 sign assignments enumerated give an exact p of 0.0527, beside the t-test's 0.0497. The signed-rank test gives 0.0413 and the sign test 0.0074.
→ SciPy's default permutation test draws 9,999 random flips instead of enumerating; on these pairs 19.4% of its runs report p ≤ 0.05.
→ Report (b + 1)/(m + 1), not b/m: with 999 permutations per test and 1,000 Bonferroni-corrected null tests, b/m gave a 63.2% family-wise error.
→ A permutation test of means is exact for identical distributions, not equal means: with groups of 10 and 40 it rejected 18.31% at an SD ratio of 2. Studentised, 5.73%.
→ Mann–Whitney is not a test of medians: at equal medians it rejected 79.7% of samples of 400 per group, and Brunner–Munzel's test holds its level where Mann–Whitney's does not.

Every test is computed by hand, matched to SciPy and R, and its error rate measured by a seeded lab.

## LinkedIn first comment

Before reaching for a rank test, write down the hypothesis: equal means, equal medians, P(X > Y) = ½, or identical distributions. Each has its own test.

Read the full article on Canery: https://canery.in/blogs/permutation-and-rank-tests

## Instagram caption

What do permutation and rank tests actually test? Swipe through Darwin's maize pairs and Fisher's exact count, why a Monte Carlo p-value is itself random, why you add one, why a permutation test of means is not exact for means, why Mann–Whitney is not a test of medians, and what ranks cost.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #nonparametric #python #permutationtest #mannwhitney

## Shared feed order

1. `assets/social/feed-01-four-tests-four-answers.png` — Darwin's 15 pairs through four tests: t-test p = 0.0497, randomisation test 0.0527, signed-rank 0.0413, sign test 0.0074
2. `assets/social/feed-02-every-sign-assignment.png` — All 32,768 sign patterns of Darwin's differences: 835 total more than 314 eighths, 28 equal it, 863 at least; two-sided p = 1,726/32,768 = 0.0527, beside the t-test's 0.0497
3. `assets/social/feed-03-a-monte-carlo-p-is-random.png` — SciPy's default permutation_test draws 9,999 random sign flips; on Darwin's pairs its p-value is at or below 0.05 in 19.4% of reruns, though the exact p is 0.0527
4. `assets/social/feed-04-add-one.png` — With 999 random permutations per test and Bonferroni over 1,000 true nulls, reporting b/m gives a family-wise error of 63.2%; (b + 1)/(m + 1) gives 0.0%
5. `assets/social/feed-05-exact-for-what.png` — Groups of 10 and 40 with equal means: the raw-difference permutation test rejects 18.31% at an SD ratio of 2 and 29.10% at 4; studentised, 5.73% and 5.81%
6. `assets/social/feed-06-not-a-median-test.png` — With equal medians, Mann–Whitney rejects 16.7%, 50.2% and 79.7% at 50, 200 and 400 per group; with medians 0.18 SD apart and P(X > Y) = ½, 4.7% to 5.7%; with equal centres and SDs 4 to 1, 14.81% against Brunner–Munzel's 5.27%
7. `assets/social/feed-07-the-price-of-ranks.png` — ARE of the rank-sum test to the t-test: 0.955 for normal data, at least 0.864 always; at 20 per group, Mann–Whitney's power is 77.6% against Welch's 79.7% for normal data and 95.0% against 84.0% for t with 3 df
8. `assets/social/feed-08-read-the-article.png` — The article's five results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-four-tests-four-answers

- File: `assets/social/feed-01-four-tests-four-answers.png`
- Title: One data set, four p-values
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Darwin's 15 pairs through four tests: t-test p = 0.0497, randomisation test 0.0527, signed-rank 0.0413, sign test 0.0074
- Technical source: Worked example; Intuition; Figure 3; ledger L01, L04, L05
- Visual structure: lockup and counter; serif title; deck; a panel with the dataset line and four rows, each test's name, what it keeps of the data, and its p-value large on the right; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · One data set, · four p-values. · Darwin's maize pairs through four tests · of one idea: crossing makes no difference. · Darwin's 15 pairs of maize plants (1876) · crossed minus self-fertilised: 13 of 15 positive · t-test · keeps: values, normal model · p = 0.0497 · randomisation test · keeps: values, signs flipped · p = 0.0527 · signed-rank test · keeps: ranks and signs · p = 0.0413 · sign test · keeps: signs only · p = 0.0074 · Each test keeps a different part of the data, · so each answers a different question. · PERMUTATION AND RANK TESTS · CANERY.IN
- Alt text: Card listing four p-values for Darwin's 15 maize pairs: t-test 0.0497, randomisation 0.0527, signed-rank 0.0413, sign test 0.0074.
- Long description: Darwin's 1876 experiment: 15 pairs of crossed and self-fertilised maize plants, crossed taller in 13 pairs. Four tests of the idea that crossing makes no difference give different two-sided p-values: the paired t-test, which uses the values under a normal model, 0.0497; Fisher's randomisation test, which uses the values with their signs flipped, 0.0527; the Wilcoxon signed-rank test, which keeps ranks and signs, 0.0413; and the sign test, which keeps the signs only, 0.0074. Takeaway: each test keeps a different part of the data, so each answers a different question.
- Keywords: permutation test, randomisation test, signed-rank test, sign test, t-test, Darwin
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests

### feed-02-every-sign-assignment

- File: `assets/social/feed-02-every-sign-assignment.png`
- Title: Exact, with no normal model
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: All 32,768 sign patterns of Darwin's differences: 835 total more than 314 eighths, 28 equal it, 863 at least; two-sided p = 1,726/32,768 = 0.0527, beside the t-test's 0.0497
- Technical source: Worked example; Figure 2; The math, equation 1; ledger L05, L07
- Visual structure: lockup and counter; serif title; deck; a panel with the histogram of all 32,768 totals, the tails beyond ±314 in tangerine and dashed lines at ±314, then the three counts, the mirror note and the two-sided p-value large; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Exact, with no · normal model. · If a coin had decided each pair's sides, every · one of the 32,768 sign patterns was equally likely. · totals of all 32,768 sign patterns, eighths of an inch · Darwin: 314 · above 314: 835 · equal: 28 · at least: 863 · and as many in the mirror tail · two-sided p = 1,726 / 32,768 · 0.0527 · t-test on the same pairs: 0.0497 · Fisher counted it by hand in 1935: 863 of 32,768 · sign patterns total at least Darwin's 314. · PERMUTATION AND RANK TESTS · CANERY.IN
- Alt text: Card with the histogram of all 32,768 sign-pattern totals of Darwin's pairs; 863 at least 314; two-sided p 0.0527.
- Long description: If crossing makes no difference and a coin had decided which plant of each pair got which side of the pot, each of the 2 to the 15th = 32,768 ways of signing the 15 differences was equally likely. Their totals, in eighths of an inch, form a symmetric histogram; 835 exceed Darwin's observed 314, 28 equal it, so 863 are at least as large, and as many lie in the mirror tail. The two-sided p-value is 1,726/32,768 = 0.0527; the t-test on the same pairs gives 0.0497. Takeaway: Fisher counted it by hand in 1935.
- Keywords: randomisation test, permutation test, exact test, Fisher, Darwin, sign flip
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests

### feed-03-a-monte-carlo-p-is-random

- File: `assets/social/feed-03-a-monte-carlo-p-is-random.png`
- Title: A Monte Carlo p-value is random
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: SciPy's default permutation_test draws 9,999 random sign flips; on Darwin's pairs its p-value is at or below 0.05 in 19.4% of reruns, though the exact p is 0.0527
- Technical source: When is a permutation test exact?; Figure 4a; ledger L36
- Visual structure: lockup and counter; serif title; deck; a panel with the exact distribution of the default p-value over reruns as bars, those at or below 0.05 in tangerine, dashed 0.05 and blue exact-p lines, then the share large in tangerine and the fix; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · A Monte Carlo · p-value is random. · SciPy's default draws 9,999 random sign flips, · fewer than the 32,768 it could enumerate. · scipy.stats.permutation_test, default settings · the p-value it returns for Darwin's pairs, over reruns · 0.05 · exact 0.0527 · runs at or below 0.05 · 19.4% · 95% of runs between 0.0466 and 0.0592 · 9,999 random flips by default; n_resamples=np.inf enumerates · On Darwin's pairs, 19.4% of default runs report · p ≤ 0.05; the exact p-value is 0.0527. · PERMUTATION AND RANK TESTS · CANERY.IN
- Alt text: Card showing the distribution of SciPy's default Monte Carlo p for Darwin's pairs; 19.4% of runs fall at or below 0.05.
- Long description: SciPy's permutation_test enumerates only when the reference set has at most n_resamples members, 9,999 by default; Darwin's has 32,768, so the default draws 9,999 random sign flips and adds one. Over reruns its two-sided p-value is a binomial random variable centred near the exact 0.0527, with 95% of runs between 0.0466 and 0.0592, and 19.4% of runs at or below 0.05. Passing n_resamples=np.inf enumerates all 32,768. Takeaway: on Darwin's pairs, 19.4% of default runs report p at or below 0.05 although the exact p-value is 0.0527.
- Keywords: Monte Carlo p-value, permutation test, SciPy, reproducibility, exact test, resampling
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests

### feed-04-add-one

- File: `assets/social/feed-04-add-one.png`
- Title: Count the observed labelling: add one
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: With 999 random permutations per test and Bonferroni over 1,000 true nulls, reporting b/m gives a family-wise error of 63.2%; (b + 1)/(m + 1) gives 0.0%
- Technical source: When is a permutation test exact?; Figure 4b; The math, equation 1; ledger L12, L13
- Visual structure: lockup and counter; serif title; deck; a panel with the setting, two rows comparing the family-wise error of b/m (tangerine, 63.2%) and (b + 1)/(m + 1) (blue, 0.0%), and a note on zero p-values; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Count the observed · labelling: add one. · A random-permutation p-value is exact as · (b + 1)/(m + 1), not as b/m. · m random relabellings, b at least as extreme · Bonferroni over 1,000 true nulls, m = 999 each · report b/m · 63.2% · family-wise error: at least one false rejection · report (b + 1)/(m + 1) · 0.0% · no p below 1/1,000, the corrected cut is 0.00005 · b/m is 0 with probability 1/(m + 1) under the null, · and a zero survives any multiple-testing correction · With 999 permutations per test and 1,000 tests, · b/m rejected a true null 63.2% of the time. · PERMUTATION AND RANK TESTS · CANERY.IN
- Alt text: Card comparing family-wise error over 1,000 null tests: 63.2% when permutation p-values are b/m, 0.0% with (b + 1)/(m + 1).
- Long description: A Monte Carlo permutation test draws m random relabellings and counts the b at least as extreme as the data. Reported as b/m, the p-value is zero with probability 1/(m + 1) under the null, and a zero survives any multiple-testing correction: with 999 permutations per test and a Bonferroni correction over 1,000 true null hypotheses, at least one is rejected with probability 63.2%. Reported as (b + 1)/(m + 1), no p-value falls below 1/1,000, above the corrected cut-off of 0.00005, and the family-wise error is 0.0%. Takeaway: count the observed labelling as one of the m + 1.
- Keywords: permutation p-value, Monte Carlo test, multiple testing, Bonferroni, family-wise error, Phipson and Smyth
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests

### feed-05-exact-for-what

- File: `assets/social/feed-05-exact-for-what.png`
- Title: Exact for identical distributions, not means
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Groups of 10 and 40 with equal means: the raw-difference permutation test rejects 18.31% at an SD ratio of 2 and 29.10% at 4; studentised, 5.73% and 5.81%
- Technical source: Does a permutation test compare means?; Figure 5; ledger L16–L18
- Visual structure: lockup and counter; serif title; deck; a panel with a three-column table of SD ratio against the size of the raw (tangerine where liberal) and studentised (blue) permutation tests, and the simulation's budget; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Exact for identical · distributions, not means. · Relabelling mixes the groups, so the reference · spread is pooled, like Student's standard error. · groups of 10 and 40, normal data, equal means · SD of the 10 / SD of the 40 · raw difference · studentised · 1/4 · 0.06% · 3.87% · 1 · 4.89% · 4.92% · 2 · 18.31% · 5.73% · 4 · 29.10% · 5.81% · size of a 5% permutation test of equal means; · 50,000 data sets per row, 999 relabellings each · Permute Welch's t, not the raw difference: 5.73% · instead of 18.31% when the 10 have twice the SD. · PERMUTATION AND RANK TESTS · CANERY.IN
- Alt text: Card tabling the size of raw and studentised permutation tests of equal means, groups of 10 and 40: 29.10% against 5.81% at SD ratio 4.
- Long description: A two-sample permutation test of the difference in means is exact when the two groups come from one distribution, not when only their means are equal. With normal data, equal means and groups of 10 and 40, the size of a 5% test, at SD ratios (group of 10 over group of 40) of 1/4, 1, 2 and 4, is 0.06%, 4.89%, 18.31% and 29.10% for the raw difference, and 3.87%, 4.92%, 5.73% and 5.81% when the statistic is Welch's t. 50,000 simulated data sets per row, 999 relabellings each. Takeaway: permute Welch's t, not the raw difference.
- Keywords: permutation test, studentised statistic, Welch t-test, exchangeability, unequal variances, Romano
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests

### feed-06-not-a-median-test

- File: `assets/social/feed-06-not-a-median-test.png`
- Title: Mann–Whitney is not a test of medians
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: With equal medians, Mann–Whitney rejects 16.7%, 50.2% and 79.7% at 50, 200 and 400 per group; with medians 0.18 SD apart and P(X > Y) = ½, 4.7% to 5.7%; with equal centres and SDs 4 to 1, 14.81% against Brunner–Munzel's 5.27%
- Technical source: What does the Mann–Whitney test test?; Figures 6 and 7; ledger L20–L25
- Visual structure: lockup and counter; serif title; deck; a panel with three blocks: rejection rates at equal medians by sample size, the flat rate at unequal medians with P(X > Y) = ½, and Mann–Whitney against Brunner–Munzel for normal groups with unequal spreads; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Mann–Whitney is not · a test of medians. · It responds to P(X > Y), and it is exact only · when the two distributions are identical. · equal medians, P(X > Y) = 0.443 · 50 per group · 16.7% · 200 per group · 50.2% · 400 per group · 79.7% · medians 0.18 SD apart, P(X > Y) = ½ · every size from 10 to 400 per group · 4.7% to 5.7% · equal centres, SDs 4 to 1, groups of 10 and 40 · Mann–Whitney · 14.81% · Brunner–Munzel · 5.27% · rejection rate of a 5% Mann–Whitney test · Choose by hypothesis: Welch for means, Brunner– · Munzel for P(X > Y), a median method for medians. · PERMUTATION AND RANK TESTS · CANERY.IN
- Alt text: Card showing Mann–Whitney rejecting 79.7% at equal medians, 5% at unequal medians, and 14.81% where Brunner–Munzel gives 5.27%.
- Long description: Three designs separate what Mann–Whitney responds to. A normal and a shifted exponential with equal medians and P(X > Y) = 0.443: Mann–Whitney rejects 16.7% of samples at 50 per group, 50.2% at 200 and 79.7% at 400. The same shapes with medians 0.18 SD apart and P(X > Y) = 1/2: it rejects 4.7% to 5.7% at every size from 10 to 400. Two normal groups of 10 and 40 with a common centre and SDs 4 to 1: Mann–Whitney rejects 14.81%, Brunner–Munzel's studentised rank test 5.27%. Takeaway: choose by hypothesis, Welch for means, Brunner–Munzel for P(X > Y), a median method for medians.
- Keywords: Mann-Whitney test, Wilcoxon rank-sum, medians, stochastic ordering, Brunner-Munzel test, nonparametric
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests

### feed-07-the-price-of-ranks

- File: `assets/social/feed-07-the-price-of-ranks.png`
- Title: Ranks cost little, and pay in the tails
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: ARE of the rank-sum test to the t-test: 0.955 for normal data, at least 0.864 always; at 20 per group, Mann–Whitney's power is 77.6% against Welch's 79.7% for normal data and 95.0% against 84.0% for t with 3 df
- Technical source: What do ranks cost?; Figure 9; The math, equation 6; ledger L29, L30
- Visual structure: lockup and counter; serif title; deck; a panel with a four-column table of shape, ARE (tangerine below 1, blue from 1), Mann–Whitney's power and Welch's power for five shapes, and two notes; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Ranks cost little, · and pay in the tails. · The efficiency of Mann–Whitney against the · t-test, in the limit and in samples of 20. · power at 20 per group, shift giving Student 80% on normal data · shape · ARE · Mann–Whitney · Welch · normal · 0.955 · 77.6% · 79.7% · parabolic · 0.864 · 74.1% · 79.9% · uniform · 1.000 · 73.5% · 79.8% · Laplace · 1.500 · 88.0% · 79.8% · t, 3 df · 1.900 · 95.0% · 84.0% · ARE: large-sample ratio of sample sizes for equal power · 100,000 simulated data sets per shape · The ARE is 3/π = 0.955 for normal data and never · below 0.864; with t, 3 df ranks gain 10.9 points. · PERMUTATION AND RANK TESTS · CANERY.IN
- Alt text: Card tabling ARE and power at 20 per group: normal 0.955, Mann–Whitney 77.6% vs 79.7%; t with 3 df 1.900, 95.0% vs 84.0%.
- Long description: The asymptotic relative efficiency of the rank-sum test to the t-test, the large-sample ratio of sample sizes for equal power, and the power of each at 20 per group for a shift that gives Student's t-test 80% power on normal data, 100,000 simulated data sets per shape: normal, ARE 0.955, Mann–Whitney 77.6% against Welch 79.7%; parabolic, 0.864, 74.1% against 79.9%; uniform, 1.000, 73.5% against 79.8%; Laplace, 1.500, 88.0% against 79.8%; t with 3 degrees of freedom, 1.900, 95.0% against 84.0%. Takeaway: the ARE is 3/pi = 0.955 for normal data and never below 0.864; with t, 3 df ranks gain 10.9 points.
- Keywords: asymptotic relative efficiency, Mann-Whitney, t-test, statistical power, heavy tails, Hodges-Lehmann
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: What does your test actually test?
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's five results in one list, and the call to read it
- Technical source: Insights; Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel with five headed lines, each with its number; takeaway; the canonical URL as the footer call to action
- Visible-text transcript: Canery.in · 08 / 08 · What does your · test actually test? · Every test computed by hand, matched to SciPy · and R, and its error rate measured. · the randomisation test · Darwin: exact p = 0.0527, t-test 0.0497 · Monte Carlo p-values · report (b + 1)/(m + 1); b/m gave 63.2% family-wise error · a permutation test of means · 18.31% raw, 5.73% studentised, 10 and 40 · Mann–Whitney · 79.7% rejections at equal medians, 400 per group · Hodges–Lehmann · Darwin: 3.125 in, exact interval 0.5 to 5.1875 · The full walk-through, with the lab and every · simulated number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/PERMUTATION-AND-RANK-TESTS
- Alt text: Closing card listing five results, from Darwin's exact p of 0.0527 to the Hodges–Lehmann interval, with the article's address.
- Long description: A summary of the article: the randomisation test (Darwin's exact p = 0.0527, t-test 0.0497); Monte Carlo p-values (report (b + 1)/(m + 1); b/m gave a 63.2% family-wise error); a permutation test of means (18.31% raw against 5.73% studentised with groups of 10 and 40); Mann–Whitney (79.7% rejections at equal medians, 400 per group); and Hodges–Lehmann (Darwin: 3.125 inches, exact interval 0.5 to 5.1875). Call to action: read it at canery.in/blogs/permutation-and-rank-tests.
- Keywords: permutation test, rank test, Mann-Whitney, Hodges-Lehmann, nonparametric statistics, statistics for data scientists
- Canonical URL: https://canery.in/blogs/permutation-and-rank-tests
