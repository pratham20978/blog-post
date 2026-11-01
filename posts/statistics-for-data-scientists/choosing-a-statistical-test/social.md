---
social_schema: 2
canonical_url: "https://canery.in/blogs/choosing-a-statistical-test"
---

# Social publishing package — choosing-a-statistical-test

## LinkedIn post

Which statistical test? Not the one the data's layout suggests. The design that collected the data decides, and the wrong choice changes the answer.

The eighth part of Statistics for Data Scientists measures it:

→ Student's 1908 sleep data: ten patients, each given both drugs. Paired, the drugs differ at p = 0.0028. Read as two groups, the same twenty numbers give p = 0.079.
→ Student's t-test pools the variances. With groups of 10 and 40, its exact type I error is 18.25% when the smaller group has twice the SD, and 29.37% at four times. Welch's stays between 4.97% and 5.15%.
→ Testing equal variances first and then choosing does not fix it: letting Levene's test decide gave 9.74% where Welch alone gave 5.07%.
→ Welch's price is small: 0.08 points of power in a balanced design, 4.4 points at 10 against 40.
→ In a 2 × 2 table the design's fixed margins decide. Fisher's tea test is exact; with groups of 20 and 22, Fisher's 5% test never exceeds 3.61%, and Boschloo's unconditional test keeps the size while rejecting more.

Every test is computed by hand, matched to SciPy and R, and its error rate computed exactly or measured by a seeded lab.

## LinkedIn first comment

Before choosing a test, write down how the data were collected: which units were measured twice, which groups were separate, and which totals were fixed in advance. That answer names the test.

Read the full article on Canery: https://canery.in/blogs/choosing-a-statistical-test

## Instagram caption

Which statistical test? Ask the design, not the data. Swipe through one dataset that gives p = 0.0028 or p = 0.079, why Student's t-test errs when sizes and SDs differ, Welch's small price, why testing the assumptions first does not help, and how a 2 × 2 table's fixed margins decide between Fisher and the alternatives.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #hypothesistesting #python #ttest #welch

## Shared feed order

1. `assets/social/feed-01-the-design-decides.png` — Student's ten patients took both drugs: paired, the drugs differ at p = 0.0028; read as two groups, the same twenty numbers give p = 0.079
2. `assets/social/feed-02-pairing-removes-the-patients.png` — The variance of a difference is Var(1) + Var(2) − 2 Cov: 3.201 + 4.009 − 5.697 = 1.513, so pairing cut the standard error from 0.849 to 0.389
3. `assets/social/feed-03-student-follows-the-pairing.png` — Exact type I error of a 5% test with groups of 10 and 40: Student's runs from 0.07% to 29.37% as the SD ratio moves from 1/4 to 4; Welch's stays between 4.97% and 5.15%
4. `assets/social/feed-04-the-price-of-welch.png` — With equal SDs, at the difference where Student's test has 80.0% power, Welch's has 79.9% with groups of 25 and 25 and 75.6% with groups of 10 and 40
5. `assets/social/feed-05-pre-testing-does-not-help.png` — Letting Levene's test choose between Student and Welch rejected a true null 9.74% of the time at an SD ratio of 1.5, against Welch's 5.07%; Student's error was 21.19% on the samples Levene passed at a ratio of 2
6. `assets/social/feed-06-one-table-eight-answers.png` — Hellman's malocclusion counts, 4 of 20 against 1 of 22, through eight tests: p from 0.112 (mid-p) to 0.287 (doubled Fisher); R's and SciPy's default gives 0.286
7. `assets/social/feed-07-the-margins-decide.png` — With both margins fixed, as in Fisher's tea test, Fisher's test is exact (1/70); with only group sizes of 20 and 22 fixed, its largest size is 3.61% and Boschloo's 4.63%
8. `assets/social/feed-08-read-the-article.png` — The article's five results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-the-design-decides

- File: `assets/social/feed-01-the-design-decides.png`
- Title: The design decides, not the data
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Student's ten patients took both drugs: paired, the drugs differ at p = 0.0028; read as two groups, the same twenty numbers give p = 0.079
- Technical source: Why this matters; Worked example; Figure 2; ledger L01
- Visual structure: lockup and counter; serif title; deck; a panel with the dataset line, the paired p-value large in blue with its t and SE, the unpaired p-value large in tangerine with its t and SE, and R's help-page note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · The design decides, · not the data. · Same numbers, two tests. How the data were · collected says which one answers the question. · Student's 1908 sleep data: ten patients, two drugs · the same twenty numbers, the same 1.58-hour difference · paired: each patient took both · p = 0.0028 · t = 4.06 on 9 df, SE 0.389 · as two groups, as the layout suggests · p = 0.079 · t = 1.86 on 18 df, SE 0.849 · R's help page: the 20 values are measurements · on 10 persons, not two groups · Paired, the drugs differ at p = 0.0028; read as · two groups, the same numbers give p = 0.079. · CHOOSING A TEST · CANERY.IN
- Alt text: Card contrasting the paired t-test's p = 0.0028 with the two-group test's p = 0.079 on the same ten patients' sleep data.
- Long description: R's sleep data are Student's 1908 example: ten patients, each given both of two sleeping drugs, with a mean difference of 1.58 hours. Analysed as the design dictates, paired, the t statistic is 4.06 on 9 degrees of freedom with a standard error of 0.389, and p = 0.0028. Analysed as two independent groups, as the data's two-column layout suggests, t = 1.86 on 18 degrees of freedom with a standard error of 0.849, and p = 0.079. R's help page notes that the 20 values are measurements on 10 persons, not two groups. Takeaway: paired, the drugs differ at p = 0.0028; read as two groups, the same numbers give p = 0.079.
- Keywords: paired t-test, unpaired t-test, study design, sleep data, Student, p-value
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test

### feed-02-pairing-removes-the-patients

- File: `assets/social/feed-02-pairing-removes-the-patients.png`
- Title: Pairing removes the patients
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The variance of a difference is Var(1) + Var(2) − 2 Cov: 3.201 + 4.009 − 5.697 = 1.513, so pairing cut the standard error from 0.849 to 0.389
- Technical source: Worked example (the variance identity); Figure 1; The math, equation 1
- Visual structure: lockup and counter; serif title; deck; a panel with the variance identity as four rows, the covariance term in tangerine and the result in blue, then the two standard errors as large numbers and the equivalent parallel-trial size; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Pairing removes · the patients. · A patient high on one drug is high on the · other, so that spread cancels in the difference. · why pairing shrinks the standard error · Var(drug 1) · 3.201 · + Var(drug 2) · 4.009 · − 2 Cov (correlation 0.795) · 5.697 · = Var(difference) · 1.513 · SE as two groups · 0.849 · SE paired · 0.389 · a parallel trial: about 48 patients per drug · for the same precision (from these variances) · Pairing removed 5.697 of a variance of 7.21, · and the standard error fell 2.18 times. · CHOOSING A TEST · CANERY.IN
- Alt text: Card showing the variance of the paired differences, 3.201 + 4.009 − 5.697 = 1.513, and the standard error falling from 0.849 to 0.389.
- Long description: A patient's results on the two drugs are correlated, r = 0.795. The variance of a difference is the sum of the two variances minus twice their covariance: 3.201 + 4.009 − 5.697 = 1.513. As two groups, the standard error of the mean difference is 0.849; paired, it is 0.389. A parallel-group trial would need about 48 patients per drug for the same precision, estimated from these sample variances. Takeaway: pairing removed 5.697 of a variance of 7.21, and the standard error fell 2.18 times.
- Keywords: paired design, variance of a difference, covariance, standard error, correlation, sample size
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test

### feed-03-student-follows-the-pairing

- File: `assets/social/feed-03-student-follows-the-pairing.png`
- Title: Student's t-test fails when sizes and SDs differ
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Exact type I error of a 5% test with groups of 10 and 40: Student's runs from 0.07% to 29.37% as the SD ratio moves from 1/4 to 4; Welch's stays between 4.97% and 5.15%
- Technical source: When does Student's t-test keep its 5%?; Figure 4
- Visual structure: lockup and counter; serif title; deck; a panel with a three-column table of SD ratio against the exact type I error of Student's (tangerine where liberal) and Welch's (blue) tests; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Student's t-test fails · when sizes and SDs differ. · It pools the variances, so a small group's · large variance is understated. · exact type I error of a 5% test, groups of 10 and 40 · SD of the 10 / SD of the 40 · Student · Welch · 1/4 · 0.07% · 4.98% · 1/2 · 0.52% · 5.01% · 1 · 5.00% · 5.15% · 1.5 · 12.17% · 5.14% · 2 · 18.25% · 5.11% · 4 · 29.37% · 5.04% · normal data; computed by quadrature, checked by simulation · When the group of 10 has 4 times the SD, Student's · 5% test rejects 29.37% of the time; Welch's 5.04%. · CHOOSING A TEST · CANERY.IN
- Alt text: Card tabling the exact type I error of Student's and Welch's t-tests for groups of 10 and 40, from 0.07% to 29.37% against about 5%.
- Long description: For normal data with groups of 10 and 40, the exact type I error of a 5% two-sided test, computed by quadrature and checked by simulation, at ratios of the group of 10's SD to the group of 40's: 1/4, Student 0.07% and Welch 4.98%; 1/2, 0.52% and 5.01%; 1, 5.00% and 5.15%; 1.5, 12.17% and 5.14%; 2, 18.25% and 5.11%; 4, 29.37% and 5.04%. Student's test pools the variances, so a small group's large variance is understated. Takeaway: when the group of 10 has 4 times the SD, Student's 5% test rejects 29.37% of the time and Welch's 5.04%.
- Keywords: Welch t-test, Student t-test, type I error, unequal variances, unequal sample sizes, robustness
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test

### feed-04-the-price-of-welch

- File: `assets/social/feed-04-the-price-of-welch.png`
- Title: Welch's test has a price
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: With equal SDs, at the difference where Student's test has 80.0% power, Welch's has 79.9% with groups of 25 and 25 and 75.6% with groups of 10 and 40
- Technical source: When does Student's t-test keep its 5%? (Welch's price); Figure 5
- Visual structure: lockup and counter; serif title; deck; a panel with two blocks, one per design, each giving the true difference and Welch's power as a large blue number with a note; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Welch's test · has a price. · When the variances really are equal, it · spends a little power that pooling would not. · power with equal SDs, where Student's test has 80.0% · groups of 25 and 25 · true difference 0.81 SD · Welch's power · 79.9% · 0.08 points below Student's at most · groups of 10 and 40 · true difference 1.01 SD · Welch's power · 75.6% · its degrees of freedom are near 14, not 48 · Under 0.1 points in a balanced design, 4.4 at · 10 against 40: small beside Student's failure. · CHOOSING A TEST · CANERY.IN
- Alt text: Card showing Welch's power with equal SDs where Student's test has 80.0%: 79.9% for 25 and 25, and 75.6% for 10 and 40.
- Long description: When the two population SDs really are equal, Welch's test spends some power that pooling would not. At the true difference where Student's test has 80.0% power, 0.81 SDs for groups of 25 and 25, Welch's has 79.9%, at most 0.08 points below Student's anywhere; at 1.01 SDs for groups of 10 and 40, Welch's has 75.6%, because its degrees of freedom are near 14 rather than 48. Takeaway: under 0.1 points in a balanced design, 4.4 at 10 against 40: small beside Student's failure.
- Keywords: Welch t-test, statistical power, equal variances, degrees of freedom, unbalanced design
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test

### feed-05-pre-testing-does-not-help

- File: `assets/social/feed-05-pre-testing-does-not-help.png`
- Title: Testing assumptions first does not help
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Letting Levene's test choose between Student and Welch rejected a true null 9.74% of the time at an SD ratio of 1.5, against Welch's 5.07%; Student's error was 21.19% on the samples Levene passed at a ratio of 2
- Technical source: Does checking the assumptions first help?; Figure 6; ledger L12–L15
- Visual structure: lockup and counter; serif title; deck; a panel with the rule, a four-column table of SD ratio, Levene's detection rate, the procedure's error (tangerine) and Welch's (blue), then Student's conditional error as a large tangerine number; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Testing assumptions · first does not help. · The pre-test misses the differences that · matter, and selects the worst samples. · Levene's test first: Welch if it rejects, else Student · groups of 10 and 40, normal data, no true difference · SD ratio (10 / 40) · Levene detects · procedure · Welch alone · 1.5 · 27.9% · 9.74% · 5.07% · 2 · 64.6% · 9.13% · 5.06% · on the samples Levene passed, at a ratio of 2: · Student's error · 21.19% · against 18.25% on all samples · Letting Levene choose left a 5% test at 9.74%; · always using Welch gave 5.07%. · CHOOSING A TEST · CANERY.IN
- Alt text: Card tabling the Levene-then-t procedure's error, 9.74% and 9.13%, against Welch's 5.07% and 5.06%, and a 21.19% conditional error.
- Long description: The two-stage habit, simulated with groups of 10 and 40, normal data and no true difference: Levene's test first, then Welch's test if it rejects and Student's otherwise. At an SD ratio (group of 10 over group of 40) of 1.5, Levene detects the difference in 27.9% of samples and the procedure rejects 9.74% of the time, against 5.07% for Welch's test alone; at 2, 64.6%, 9.13% and 5.06%. On the samples Levene passed at a ratio of 2, Student's test errs 21.19%, against 18.25% on all samples. Takeaway: letting Levene choose left a 5% test at 9.74%; always using Welch gave 5.07%.
- Keywords: pre-testing, Levene test, two-stage procedure, Welch t-test, type I error, conditional error
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test

### feed-06-one-table-eight-answers

- File: `assets/social/feed-06-one-table-eight-answers.png`
- Title: One 2 × 2 table, eight p-values
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Hellman's malocclusion counts, 4 of 20 against 1 of 22, through eight tests: p from 0.112 (mid-p) to 0.287 (doubled Fisher); R's and SciPy's default gives 0.286
- Technical source: Which test fits a 2 × 2 table?; Figure 8; ledger L20, L21, L27
- Visual structure: lockup and counter; serif title; deck; a panel with the data line and the smallest expected count, then eight rows of test name and p-value, coloured by family; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · One 2 × 2 table, · eight p-values. · The same counts through eight tests in use, · from the mid-p value to doubled Fisher. · normal teeth: breast-fed 4 of 20, bottle-fed 1 of 22 · smallest expected count 2.38 (Hellman, via Yates 1934) · Fisher's mid-p · 0.112 · Pearson chi-squared · 0.122 · 'N − 1' chi-squared · 0.127 · Barnard (unconditional) · 0.143 · Fisher exact, Irwin's rule · 0.174 · Boschloo (unconditional) · 0.175 · Yates-corrected: the default · 0.286 · Fisher exact, doubled tail · 0.287 · R's and SciPy's default chi-squared test gives · 0.286 here; the mid-p value gives 0.112. · CHOOSING A TEST · CANERY.IN
- Alt text: Card listing eight p-values for one 2 × 2 table, 4 of 20 against 1 of 22, from 0.112 for mid-p to 0.287 for doubled Fisher.
- Long description: Hellman's data, as Yates printed them in 1934: 4 of 20 breast-fed and 1 of 22 bottle-fed infants had normal teeth; the smallest expected count is 2.38. Eight tests give two-sided p-values of 0.112 (Fisher's mid-p), 0.122 (Pearson chi-squared), 0.127 ('N − 1' chi-squared), 0.143 (Barnard's unconditional test), 0.174 (Fisher's exact test by Irwin's rule), 0.175 (Boschloo's unconditional test), 0.286 (the Yates-corrected chi-squared, R's and SciPy's default) and 0.287 (Fisher's exact test, doubled tail). Takeaway: R's and SciPy's default chi-squared test gives 0.286 here; the mid-p value gives 0.112.
- Keywords: 2x2 table, Fisher exact test, chi-squared test, Yates correction, mid-p, Boschloo test
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test

### feed-07-the-margins-decide

- File: `assets/social/feed-07-the-margins-decide.png`
- Title: In a 2 × 2 table, the margins decide
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: With both margins fixed, as in Fisher's tea test, Fisher's test is exact (1/70); with only group sizes of 20 and 22 fixed, its largest size is 3.61% and Boschloo's 4.63%
- Technical source: Which test fits a 2 × 2 table?; Figures 7 and 9; ledger L17, L23
- Visual structure: lockup and counter; serif title; deck; a panel with two blocks: the tea test and its exact 1/70, then the largest exact sizes of five tests for groups of 20 and 22; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · In a 2 × 2 table, · the margins decide. · Which totals the design fixed in advance · decides whether Fisher's test is exact. · both margins fixed: the tea test · eight cups, she is told four have milk first · all eight right: 1/70 = 0.0143, exactly · only the group sizes fixed: 20 and 22 · largest size of a 5% test, every table summed · Fisher's exact · 3.61% · Yates-corrected · 2.19% · Boschloo · 4.63% · Pearson · 4.94% · mid-p · 5.14% · At 20 and 22, Boschloo's test rejected every table · Fisher's did and 10 more, at a size of at most 4.63%. · CHOOSING A TEST · CANERY.IN
- Alt text: Card contrasting the tea test, where Fisher's test is exact, with groups of 20 and 22, where its size never exceeds 3.61%.
- Long description: Fisher's tea-tasting design fixes both margins of its 2 × 2 table: eight cups, and the lady is told that four have milk first, so all eight right has probability exactly 1/70 = 0.0143. When only the group sizes are fixed, 20 and 22, the largest exact size of each 5% test, summed over every possible table, is Fisher's exact 3.61%, Yates-corrected 2.19%, Boschloo 4.63%, Pearson 4.94% and mid-p 5.14%. Takeaway: at 20 and 22, Boschloo's test rejected every table Fisher's did and 10 more, at a size of at most 4.63%.
- Keywords: Fisher exact test, lady tasting tea, Boschloo test, unconditional test, fixed margins, test size
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Which test? Ask the design
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's five results in one list, and the call to read it
- Technical source: Insights; Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel with five headed lines, each with its number; takeaway; the canonical URL as the footer call to action
- Visible-text transcript: Canery.in · 08 / 08 · Which test? · Ask the design. · Every test computed by hand, matched to SciPy · and R, and its error rate measured. · the design picks the test · paired p = 0.0028; as two groups p = 0.079 · Student against Welch, 10 and 40 · 29.37% against 5.04% at 4 times the SD · pre-testing the assumptions · 9.74% where Welch alone gives 5.07% · 2 × 2 tables · Fisher's 5% test at most 3.61% with groups of 20 and 22 · ANOVA, three groups · F 16.13% against W 5.25% under negative pairing · The full walk-through, with the lab and every · simulated number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/CHOOSING-A-STATISTICAL-TEST
- Alt text: Closing card listing five results, from the paired p of 0.0028 to F's 16.13% against W's 5.25%, with the article's address.
- Long description: A summary of the article: the design picks the test (paired p = 0.0028, as two groups p = 0.079); Student against Welch with groups of 10 and 40 (29.37% against 5.04% at four times the SD); pre-testing the assumptions (9.74% where Welch alone gives 5.07%); 2 × 2 tables (Fisher's 5% test at most 3.61% with groups of 20 and 22); and ANOVA with three groups (F 16.13% against W 5.25% under negative pairing). Call to action: read it at canery.in/blogs/choosing-a-statistical-test.
- Keywords: statistical test, study design, Welch t-test, Fisher exact test, ANOVA, statistics for data scientists
- Canonical URL: https://canery.in/blogs/choosing-a-statistical-test
