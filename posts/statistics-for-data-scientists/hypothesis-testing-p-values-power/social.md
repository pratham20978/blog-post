---
social_schema: 2
canonical_url: "https://canery.in/blogs/hypothesis-testing-p-values-power"
---

# Social publishing package — hypothesis-testing-p-values-power

## LinkedIn post

A p-value of 0.03 is not a 3% chance that the result is a fluke. It is computed assuming there is no effect, so it cannot be the probability that there is none.

The fifth part of Statistics for Data Scientists measures what a p-value is, what a test promises, and how wrong a "significant" estimate can be:

→ A 2013 study reported a 17-point shift in voting with p = .035. If the true effect is a plausible 2 points, its design reaches significance only 5.7% of the time; every significant estimate is at least 7.9 times the effect, and 24% have the wrong sign (Gelman and Carlin's design analysis, recomputed in closed form).
→ Under no effect a p-value is uniform. At 5.7% power it is nearly uniform too, so it says almost nothing; one 78%-power experiment run 25 times gave p from 0.00007 to 0.33.
→ The chance a significant result is false needs a prior. For an observed p = .03 with 16 per group it is 16.7% at even odds and 64.3% if one tested effect in ten is real.
→ In the Reproducibility Project's CC0 data, replications kept half the original effect (mean r 0.396 against 0.197), and only 2 of 63 failed replications could rule out an effect of 0.1.
→ Testing after every observation turns a 5% test into a 37% test after 100 looks.

Every number comes from a seeded lab, with its Monte Carlo standard error, that you can rerun in about 30 seconds.

## LinkedIn first comment

Before calling a result a discovery, ask three questions the p-value cannot answer: how plausible the effect was beforehand, how much power the design had for a realistic effect, and whether the sample size was fixed in advance. To claim no effect, run an equivalence test.

Read the full article on Canery: https://canery.in/blogs/hypothesis-testing-p-values-power

## Instagram caption

Does p = 0.03 mean a 3% chance of a fluke? No. Swipe through what a p-value measures, why a significant estimate from a weak design is exaggerated and sometimes points the wrong way, why the p-value itself bounces around, why replications find smaller effects, and how to show there is no effect.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #pvalues #hypothesistesting #python #abtesting

## Shared feed order

1. `assets/social/feed-01-p-is-not-a-fluke.png` — An observed p = .03 in a 16-per-group design with 78% power: the misreading says 3%; the false positive risk is 16.7% at even prior odds and 64.3% at a prior of 0.1
2. `assets/social/feed-02-significant-so-big.png` — The 2013 design with a plausible 2-point effect: significance needs an estimate beyond ±15.9, so 4.34% land significant with the right sign, 1.37% with the wrong one, and the average significant size is 19.08, 9.54 times the effect
3. `assets/social/feed-03-p-is-a-random-variable.png` — For a two-sided z-test the p-value's distribution depends only on λ: P(p ≤ .05) is 5.0%, 5.7%, 17.0%, 51.6% and 80.0%, and the median p 0.500, 0.487, 0.293, 0.045 and 0.0051, for λ = 0, 0.25, 1, 2 and 2.8
4. `assets/social/feed-04-same-experiment.png` — Twenty-five runs of one 78%-power experiment give 19 significant results and p-values from 0.00007 to 0.33; after an original p = .05, a replication's one-tailed p falls between 0.00008 and 0.44 with 80% probability
5. `assets/social/feed-05-observed-power.png` — For a two-sided z-test, observed power is a fixed function of p: 0.91 at p = .001, 0.73 at .01, 0.50 at .05, 0.25 at .2 and 0.10 at .5
6. `assets/social/feed-06-replications-halve.png` — The Reproducibility Project: 97 of 100 originals and 36 replications significant; mean r 0.396 against 0.197 over 97 pairs; originals with p below .001 kept 67% of their effect, those between .001 and .05 kept 38%
7. `assets/social/feed-07-not-significant-is-not-no-effect.png` — Of 63 non-significant replications only 2 ruled out any |r| of 0.1 or more and 17 any |r| of 0.2 or more; two one-sided tests with 16 per group rule out only effects larger than 1.06 SD
8. `assets/social/feed-08-read-the-article.png` — The article's four results in one list, and the call to read it

## Instagram Story

Not produced: this part ships feed cards only, at the owner's request (2026-10-30), so there are no Story frames, Story CTA or link sticker to post.

### Story order

None.

## Asset metadata

### feed-01-p-is-not-a-fluke

- File: `assets/social/feed-01-p-is-not-a-fluke.png`
- Title: p = 0.03 is not a 3% chance of a fluke
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: An observed p = .03 in a 16-per-group design with 78% power: the misreading says 3%; the false positive risk is 16.7% at even prior odds and 64.3% at a prior of 0.1
- Technical source: The problem; What share of significant results are false?; Figure 11; ledger L05, L06, L31
- Visual structure: lockup and counter; serif title; deck; a panel of three labelled numbers, the misreading's 3% in blue and the two false positive risks in tangerine; a note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · p = 0.03 is not a 3% · chance of a fluke. · What a p-value says, and what the chance · a significant result is false depends on. · two groups of 16, power 78%: an observed p = .03 · what the misreading says · 3% · the chance the result is a fluke · false positive risk, even prior odds · 16.7% · likelihood ratio 5.0 · false positive risk, prior 0.1 · 64.3% · if one tested effect in ten is real · the p-value is computed assuming no effect, so it cannot · be the probability of no effect · The chance a result is false needs a prior: · 64.3% at 1 in 10, for p = .03. · P-VALUES AND POWER · CANERY.IN
- Alt text: Card contrasting the misread 3% for p = .03 with false positive risks of 16.7% at even odds and 64.3% at a prior of 0.1.
- Long description: In a two-sample design with 16 per group and 78% power, an observed p of .03 has a likelihood ratio of 5.0 for a real effect against none. Read as the chance of a fluke it would be 3%, but the p-value is computed assuming no effect and cannot be that probability. The chance the effect is not real is 16.7% if a real effect was as likely as not beforehand, and 64.3% if one tested effect in ten is real. Takeaway: the chance a result is false needs a prior.
- Keywords: p-value, false positive risk, likelihood ratio, prior probability, hypothesis testing, misinterpretation
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power

### feed-02-significant-so-big

- File: `assets/social/feed-02-significant-so-big.png`
- Title: Significant, so it must be big
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The 2013 design with a plausible 2-point effect: significance needs an estimate beyond ±15.9, so 4.34% land significant with the right sign, 1.37% with the wrong one, and the average significant size is 19.08, 9.54 times the effect
- Technical source: Worked example; Figure 1; ledger L01, L02, L07
- Visual structure: lockup and counter; serif title; deck; a panel with the normal curve of replicated estimates, its two significant tails shaded tangerine and blue beyond dashed bars at ±15.9, and three labelled numbers beside it; a note; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Significant, so it · must be big. · At 5.7% power only estimates beyond · the bar count, whatever the truth. · replications of a 2013 study: SE 8.1 points, plausible effect 2 · +15.9 · −15.9 · significant, right sign · 4.34% · significant, wrong sign · 1.37% · average significant size · 19.08 = 9.54 × 2 · estimate (points) · the study reported 17 points with p = .035; any significant · estimate here exceeds 15.9, at least 7.9 times the plausible 2 · Every significant estimate overstates the effect; · 24% have the wrong sign. · P-VALUES AND POWER · CANERY.IN
- Alt text: Card showing a normal curve centred at 2 with tails beyond ±15.9 shaded: 4.34% right sign, 1.37% wrong sign, mean size 9.54 times the effect.
- Long description: A 2013 study reported a 17-point difference with p = .035 and a standard error of 8.1 points. If the true effect is the plausible 2 points, replicated estimates are normal around 2 with standard deviation 8.1, and only those beyond ±15.9 reach significance: 4.34% on the right side and 1.37% on the wrong side, a power of 5.7%. The significant estimates average 19.08 points in magnitude, 9.54 times the true effect, and none is smaller than 15.9, 7.9 times it. Takeaway: every significant estimate overstates the effect, and 24% have the wrong sign.
- Keywords: type M error, type S error, exaggeration ratio, statistical power, design analysis, Gelman and Carlin
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power

### feed-03-p-is-a-random-variable

- File: `assets/social/feed-03-p-is-a-random-variable.png`
- Title: Under no effect, p is uniform
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: For a two-sided z-test the p-value's distribution depends only on λ: P(p ≤ .05) is 5.0%, 5.7%, 17.0%, 51.6% and 80.0%, and the median p 0.500, 0.487, 0.293, 0.045 and 0.0051, for λ = 0, 0.25, 1, 2 and 2.8
- Technical source: What is the distribution of a p-value?; Figure 2; ledger L08
- Visual structure: lockup and counter; serif title; deck; a panel with a five-row table of λ, the share of p-values at or below .05, and the median p, the 2013 design's row in tangerine; a note; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Under no effect, · p is uniform. · With the design fixed, P(p ≤ a) = a; under · an effect, p piles up toward zero. · a two-sided z-test; λ = true effect / standard error · p ≤ .05 · median p · λ = 0, no effect · 5.0% · 0.500 · λ = 0.25, the 2013 design · 5.7% · 0.487 · λ = 1 · 17.0% · 0.293 · λ = 2 · 51.6% · 0.045 · λ = 2.8 · 80.0% · 0.0051 · 200,000 simulated tests per row agree with these exact values · a p-value has a distribution, like any statistic · At low power p is nearly uniform: · it says almost nothing about the effect. · P-VALUES AND POWER · CANERY.IN
- Alt text: Card with a table: p ≤ .05 share and median p for λ from 0 to 2.8, uniform at 0 and nearly uniform at the 2013 design's 0.25.
- Long description: When there is no effect and the design is fixed, a p-value is uniform between 0 and 1, so P(p ≤ a) = a. Under an effect its distribution depends, for a z-test, only on λ, the true effect over its standard error: the share at or below .05 is 5.0% at λ = 0, 5.7% at the 2013 design's 0.25, 17.0% at 1, 51.6% at 2 and 80.0% at 2.8, and the median p falls from 0.500 to 0.487, 0.293, 0.045 and 0.0051. 200,000 simulated tests per row agree. Takeaway: at low power the p-value is nearly uniform and says almost nothing about the effect.
- Keywords: p-value distribution, uniform distribution, statistical power, z-test, simulation
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power

### feed-04-same-experiment

- File: `assets/social/feed-04-same-experiment.png`
- Title: One experiment, p from 0.00007 to 0.33
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Twenty-five runs of one 78%-power experiment give 19 significant results and p-values from 0.00007 to 0.33; after an original p = .05, a replication's one-tailed p falls between 0.00008 and 0.44 with 80% probability
- Technical source: What is the distribution of a p-value?; Figure 3; ledger L10
- Visual structure: lockup and counter; serif title; deck; a panel with eight sorted p-values in two rows, significant ones in tangerine and the rest in blue, a key, a rule, and Cumming's interval; a note; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · One experiment, · p from 0.00007 to 0.33. · Nothing changed between runs but · the sample. · one experiment, 25 runs: 16 per group, power 78.1% · 0.00007 · 0.0019 · 0.0082 · 0.017 · 0.047 · 0.052 · 0.168 · 0.334 · orange: p ≤ .05 (19 of 25); blue: not; 8 of the 25 shown, sorted · after an original p = .05, a replication's one-tailed p · lands between 0.00008 and 0.44 with 80% probability · Cumming's interval, reproduced: 80.05% of simulated replications inside · A single p is one draw: report the estimate · and its interval, not just the verdict. · P-VALUES AND POWER · CANERY.IN
- Alt text: Card listing eight of 25 p-values from one experiment, from 0.00007 to 0.334, and Cumming's 80% interval of 0.00008 to 0.44.
- Long description: The same experiment, 16 per group with a true difference of one standard deviation and 78% power, was simulated 25 times. Nineteen runs were significant and the p-values ranged from 0.00007 to 0.33; eight of them are shown, sorted. After an original p of .05, Cumming's interval puts a replication's one-tailed p between 0.00008 and 0.44 with 80% probability, and 80.05% of simulated replications fall inside it. Takeaway: a single p is one draw, so report the estimate and its interval, not just the verdict.
- Keywords: p-value variability, replication, Cumming p interval, dance of the p-values, simulation
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power

### feed-05-observed-power

- File: `assets/social/feed-05-observed-power.png`
- Title: Observed power is the p-value again
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: For a two-sided z-test, observed power is a fixed function of p: 0.91 at p = .001, 0.73 at .01, 0.50 at .05, 0.25 at .2 and 0.10 at .5
- Technical source: How is power computed?; Figure 7; ledger L16, L17
- Visual structure: lockup and counter; serif title; deck; a panel with a five-row table of p-values and their observed power, the p = .05 row in tangerine; a note; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Observed power is · the p-value again. · Plug the estimated effect into the power · formula and you only get p back. · observed power, two-sided z-test: power at the estimated effect · p-value · observed power · p = 0.001 · 0.91 · p = 0.01 · 0.73 · p = 0.05 · 0.50 · p = 0.2 · 0.25 · p = 0.5 · 0.10 · a fixed function of p: above p = .05 it is always below 0.5 · For a design analysis, take the effect · from outside the data. · P-VALUES AND POWER · CANERY.IN
- Alt text: Card with a table of p-values and observed power for a z-test: 0.91 at .001, 0.50 at .05 and 0.10 at .5.
- Long description: Observed power plugs the effect a study estimated back into the power formula. For a two-sided z-test the result depends on the p-value alone: 0.91 at p = .001, 0.73 at .01, 0.50 at .05, 0.25 at .2 and 0.10 at .5, so any result with p above .05 has observed power below 0.5. It adds nothing to the p-value. Takeaway: for a design analysis, take the effect from outside the data.
- Keywords: observed power, post hoc power, statistical power, p-value, design analysis
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power

### feed-06-replications-halve

- File: `assets/social/feed-06-replications-halve.png`
- Title: Replications kept half the effect
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The Reproducibility Project: 97 of 100 originals and 36 replications significant; mean r 0.396 against 0.197 over 97 pairs; originals with p below .001 kept 67% of their effect, those between .001 and .05 kept 38%
- Technical source: Why do replications find smaller effects?; Figure 9; ledger L24, L25, L26
- Visual structure: lockup and counter; serif title; deck; a panel with two labelled pairs of numbers, the effect sizes in tangerine, two lines splitting by the original p-value, and a note; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · Replications kept half · the effect. · Published effects passed the significance · filter, so they arrive inflated. · Reproducibility Project: Psychology, 100 replications (CC0 data) · significant, originals → replications · 97 → 36 · of 100 coded pairs · mean effect size r · 0.396 → 0.197 · 97 pairs; the replication smaller in 83.5% · original p below .001: kept 67%, 19 of 31 replicated · original p .001 to .05: kept 38%, 14 of 59 replicated · the significance filter predicts the shrinkage and its split · by p; other causes cannot be ruled out, and that is disputed · Don't plan a study's power around · a published effect: shrink it first. · P-VALUES AND POWER · CANERY.IN
- Alt text: Card: 97 of 100 originals and 36 replications significant; mean effect r fell from 0.396 to 0.197; weaker originals kept less.
- Long description: The Open Science Collaboration replicated 100 psychology studies; in its CC0 data 97 originals and 36 replications are coded significant. Over the 97 pairs with both effect sizes the mean correlation fell from 0.396 to 0.197, and the replication was smaller in 83.5% of pairs. Originals with p below .001 kept 67% of their effect and replicated 19 times in 31; originals between .001 and .05 kept 38% and replicated 14 times in 59. The significance filter predicts the shrinkage and its split; other causes cannot be ruled out, and the reading is disputed. Takeaway: do not plan a study's power around a published effect without shrinking it.
- Keywords: replication crisis, Reproducibility Project, effect size, significance filter, winner's curse, Open Science Collaboration
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power

### feed-07-not-significant-is-not-no-effect

- File: `assets/social/feed-07-not-significant-is-not-no-effect.png`
- Title: Not significant is not no effect
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Of 63 non-significant replications only 2 ruled out any |r| of 0.1 or more and 17 any |r| of 0.2 or more; two one-sided tests with 16 per group rule out only effects larger than 1.06 SD
- Technical source: How do you show there is no effect?; Figures 12 and 13; ledger L37, L38, L40
- Visual structure: lockup and counter; serif title; deck; a panel with two labelled counts, a rule, and the TOST result for 16 per group in tangerine; a note on the procedure; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Not significant is · not no effect. · To claim no meaningful effect, test · for equivalence with a bound that matters. · the 63 non-significant replications, tested for equivalence · ruled out any |r| of 0.1 or more · 2 · of 63; that needs n = 854 at 80% power · ruled out any |r| of 0.2 or more · 17 · the median replication had n = 71 · two one-sided tests, 16 per group, 80% power: · rules out only effects larger than 1.06 SD · TOST: reject both 'at most −Δ' and 'at least +Δ', a 90% interval inside ±Δ · Most failed replications mean · "not shown", not "absent". · P-VALUES AND POWER · CANERY.IN
- Alt text: Card: of 63 non-significant replications 2 ruled out |r| of 0.1 and 17 of 0.2; TOST with 16 per group rules out only 1.06 SD.
- Long description: A non-significant result does not show that an effect is absent. Testing the Reproducibility Project's 63 non-significant replications for equivalence to zero with 90% Fisher-z intervals, only 2 rule out any correlation of 0.1 or more in magnitude and 17 any of 0.2 or more; showing |r| below 0.1 with 80% power would need n = 854, and the median replication had 71. Two one-sided tests with 16 per group can, with 80% power, rule out only effects larger than 1.06 standard deviations. Takeaway: most failed replications mean not shown, not absent.
- Keywords: equivalence test, TOST, two one-sided tests, non-significant result, replication, smallest effect size of interest
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: p-values, power, and how wrong significance is
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: The article's four results in one list, and the call to read it
- Technical source: Key takeaways; the whole article
- Visual structure: lockup and counter; serif title; deck; a panel with four headed lines, the type S and M line in tangerine; takeaway; the article's address as a tangerine footer
- Visible-text transcript: Canery.in · 08 / 08 · p-values, power, and · how wrong significance is. · Every number measured by a seeded lab · you can rerun in about 30 seconds. · a p-value is a random variable · uniform under no effect, nearly so at low power · power, by the noncentral t · 16 per group, d = 1: 78.14%; observed power adds nothing · type S and M errors · at 5.7% power: 24% wrong sign, 9.5 times too big · false positive risk, TOST, peeking · p = .03 at 1 in 10: 64%; 16 per group: ±1.06 SD; 100 looks: 37% · The full walk-through, with the lab · and every number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/HYPOTHESIS-TESTING-P-VALUES-POWER
- Alt text: Closing card summarising p as a random variable, power, type S and M errors, the false positive risk, TOST and peeking.
- Long description: A summary of the article in four lines: a p-value is a random variable, uniform under no effect and nearly so at low power; power comes from the noncentral t, 78.14% for 16 per group and d = 1, and observed power adds nothing; at 5.7% power 24% of significant estimates have the wrong sign and they are 9.5 times too big; and an observed p of .03 carries a 64% false positive risk at a prior of 1 in 10, 16 per group rules out only ±1.06 SD, and 100 looks raise a 5% test to 37%. Every number is measured by a seeded lab that reruns in about 30 seconds. Call to action: read it at canery.in.
- Keywords: p-values, statistical power, type S error, type M error, false positive risk, equivalence testing
- Canonical URL: https://canery.in/blogs/hypothesis-testing-p-values-power
