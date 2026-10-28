---
social_schema: 2
canonical_url: "https://canery.in/blogs/estimator-bias-variance-mse"
---

# Social publishing package — estimator-bias-variance-mse

## LinkedIn post

Unbiased is not the same as best. An estimator's mean squared error is bias² plus variance, and unbiasedness only removes the first term.

The third part of Statistics for Data Scientists measures it on three classic cases:

→ German tanks: from five captured serial numbers, the largest one (the MLE) has a mean squared error of 5,448 squared tanks; the unbiased MVUE, 3,303. A slightly biased stretch of the maximum beats both: 3,212.
→ In the war, serial-number estimates of German tank production landed within 4.4% to 38.5% of the records; conventional intelligence ran 4.5 to 8.2 times too high.
→ Rao–Blackwell: averaging the crude unbiased rule 2 × mean − 1 over captures that share the same maximum gives the MVUE, with 2.33 times less variance.
→ Dividing a sum of squares by n − 1 is unbiased, but for normal data n + 1 has 18% lower MSE at n = 10, and for exponential data the best divisor is 16.4.
→ Stein's paradox: pulling 18 batting averages toward their mean cut the total squared error of a 1970 forecast from 0.0753 to 0.0213. Replayed 200,000 times, James–Stein wins in 96.2% of seasons.

Every number comes from a seeded lab, with its Monte Carlo standard error, that you can rerun in about 13 seconds.

## LinkedIn first comment

Pick the loss first, then the estimator that minimises it. Unbiasedness is one property of an estimator, not a measure of its accuracy.

Read the full article on Canery: https://canery.in/blogs/estimator-bias-variance-mse

## Instagram caption

Is an unbiased estimator always the best? No: on German tank serial numbers, variance divisors and 18 batting averages, a deliberately biased estimator has the lower mean squared error. Swipe through the tank problem by hand, the error split into bias² and variance, Rao–Blackwell, why n − 1 is not the most accurate divisor, and Stein's paradox.

Every number comes from a lab you can rerun.

Link in bio.

#statistics #datascience #estimation #germantankproblem #steinsparadox #python #machinelearning

## Shared feed order

1. `assets/social/feed-01-unbiased-is-not-best.png` — three estimators of the number of tanks from five serial numbers: the biased MLE has MSE 5,448, the unbiased MVUE 3,303, and a biased stretch of the maximum 3,212, the lowest
2. `assets/social/feed-02-five-serial-numbers.png` — one capture by hand: serials 58, 171, 272, 273 and 303; the MLE is 303 and can never exceed N; the MVUE adds one average gap, 303 + 59.6 = 362.6; the true N is 342
3. `assets/social/feed-03-serials-beat-intelligence.png` — Ruggles and Brodie's comparison as reproduced: serial-number estimates within 4.4% to 38.5% of Germany's records, intelligence estimates 4.5 to 8.2 times too high
4. `assets/social/feed-04-bias-squared-plus-variance.png` — each MSE split into variance and bias²: the MLE's 5,448 is 58% bias; the best rule spends 91 squared tanks of bias to save 181 of variance
5. `assets/social/feed-05-rao-blackwell.png` — conditioning 2 × mean − 1 on the largest serial removes 4,403 of its 7,706 variance and leaves the MVUE, 2.33 times less variable
6. `assets/social/feed-06-n-minus-1-is-not-best.png` — exact MSEs of a variance estimate at n = 10: 0.2222, 0.1900 and 0.1818 for divisors n − 1, n and n + 1 on normal data; 0.8222 against 0.4512 at the best divisor, 16.4, on exponential data
7. `assets/social/feed-07-steins-paradox.png` — Efron and Morris's 18 batters: c = 0.212 moves every average 79% of the way to 0.265; Clemente .400 → .294, Munson .178 → .247; total squared error 0.0753 against 0.0213
8. `assets/social/feed-08-read-the-article.png` — the four results of the article in one list, and the call to read it

## Instagram Story

- CTA: Unbiased is not best. Three cases where a biased estimator wins, measured — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/estimator-bias-variance-mse

### Story order

1. `assets/social/story-01-the-best-can-be-biased.png` — Overlay: Three cases where a biased estimator wins.
2. `assets/social/story-02-steins-paradox.png` — Overlay: Shrink 18 averages, cut the total error 3.5-fold.
3. `assets/social/story-03-five-serial-numbers.png` — Overlay: Five serial numbers: how many tanks exist?
4. `assets/social/story-04-read-the-article.png` — Overlay: Estimators and their errors. Link below.

## Asset metadata

### feed-01-unbiased-is-not-best

- File: `assets/social/feed-01-unbiased-is-not-best.png`
- Title: Unbiased is not the same as best
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: three estimators of the number of tanks from five serial numbers: the biased MLE has MSE 5,448, the unbiased MVUE 3,303, and a biased stretch of the maximum 3,212, the lowest
- Technical source: Insights; Worked example, bias and variance added up; Figure 3
- Visual structure: lockup and counter; serif title; deck; a panel with three rows, each an estimator, its bias status and its MSE as a large number, and a provenance note; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Unbiased is not · the same as best. · Three estimates of how many tanks exist, · scored by mean squared error. · estimating N = 342 tanks from k = 5 serial numbers · MLE: the largest serial · biased · 5,448 · MVUE: m(1 + 1/k) − 1 · unbiased · 3,303 · m(k + 2)/(k + 1) − 1 · biased by 9.5 tanks · 3,212 · mean squared error, tanks²: exact, and matched by · 1,000,000 simulated captures · The most accurate rule here is biased. · Unbiasedness was never the yardstick. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Card comparing three tank-count estimators by mean squared error: biased MLE 5,448, unbiased MVUE 3,303, biased stretch 3,212.
- Long description: Estimating N = 342 tanks from k = 5 captured serial numbers, scored by mean squared error in squared tanks. The maximum likelihood estimator, the largest serial, is biased and has MSE 5,448. The minimum-variance unbiased estimator m(1 + 1/k) − 1 has MSE 3,303. The stretch m(k + 2)/(k + 1) − 1 is biased by 9.5 tanks and has the lowest MSE, 3,212. The values are exact and are matched by 1,000,000 simulated captures. Takeaway: the most accurate rule is biased; unbiasedness was never the yardstick.
- Keywords: German tank problem, mean squared error, bias, unbiased estimator, MVUE, maximum likelihood
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### feed-02-five-serial-numbers

- File: `assets/social/feed-02-five-serial-numbers.png`
- Title: Five serial numbers: how many tanks?
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: one capture by hand: serials 58, 171, 272, 273 and 303; the MLE is 303 and can never exceed N; the MVUE adds one average gap, 303 + 59.6 = 362.6; the true N is 342
- Technical source: Worked example, one capture by hand; Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with the five serials as dots on a number line, a dashed blue extension of one average gap past the largest and a dashed tangerine line at the true N, then the MLE and MVUE explained in two blocks; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · Five serial numbers. · How many tanks? · The German tank problem: tanks numbered · 1 to N, five captured, N unknown. · one capture of five tanks; true N hidden · 58 · 171 · 272, 273 · 303 · true N = 342 · MLE: the largest serial, 303 · can never be above N, so it is biased low · MVUE: 303 + 59.6 = 362.6 · 298 unseen serials below 303, in 5 gaps: · add one more gap of average size · The largest serial is a floor for N, · not an estimate of it. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Five captured serial numbers on a line, with the largest, 303, extended by one average gap to 362.6 beside the true 342.
- Long description: One capture of five tanks with serial numbers 58, 171, 272, 273 and 303, drawn as dots on a number line; the true number of tanks, 342, is a dashed tangerine line. The maximum likelihood estimate is the largest serial, 303, which can never be above N and so is biased low. The minimum-variance unbiased estimate adds one average gap: 298 unseen serials below 303 in 5 gaps make 59.6 per gap, so the estimate is 303 + 59.6 = 362.6. Takeaway: the largest serial is a floor for N, not an estimate of it.
- Keywords: German tank problem, serial number analysis, maximum likelihood, MVUE, estimation
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### feed-03-serials-beat-intelligence

- File: `assets/social/feed-03-serials-beat-intelligence.png`
- Title: Serial numbers beat the intelligence reports
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Ruggles and Brodie's comparison as reproduced: serial-number estimates within 4.4% to 38.5% of Germany's records, intelligence estimates 4.5 to 8.2 times too high
- Technical source: Worked example, against the records; Figure 4; ledger L03
- Visual structure: lockup and counter; serif title; deck; a panel with a four-column table (month, intelligence, serials, records) for three months, two summary lines and a source note; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · Serial numbers beat · the intelligence reports. · Tank production per month: estimated in the · war, then read in Germany's own records. · month · intelligence · serials · records · June 1940 · 1,000 · 169 · 122 · June 1941 · 1,550 · 244 · 271 · August 1942 · 1,550 · 327 · 342 · serial numbers: within 4.4% to 38.5% · intelligence: 4.5 to 8.2 times the records · German tanks per month; Ruggles and Brodie (1947), · as reproduced by Simon (2024) · An estimator with an error model beat · confident guesses without one. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Table of German monthly tank production for three months: intelligence 1,000 to 1,550, serial numbers 169 to 327, records 122 to 342.
- Long description: German tank production per month in June 1940, June 1941 and August 1942. Intelligence estimates: 1,000, 1,550 and 1,550. Serial-number estimates: 169, 244 and 327. Germany's records: 122, 271 and 342. The serial-number estimates were within 4.4% to 38.5% of the records; the intelligence estimates were 4.5 to 8.2 times the records. Source: Ruggles and Brodie (1947), as reproduced by Simon (2024). Takeaway: an estimator with an error model beat confident guesses without one.
- Keywords: German tank problem, World War II, economic intelligence, serial number analysis, statistics history
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### feed-04-bias-squared-plus-variance

- File: `assets/social/feed-04-bias-squared-plus-variance.png`
- Title: Error = bias² + variance
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: each MSE split into variance and bias²: the MLE's 5,448 is 58% bias; the best rule spends 91 squared tanks of bias to save 181 of variance
- Technical source: Worked example, bias and variance added up; Figure 3; The math, equation (1)
- Visual structure: lockup and counter; serif title; deck; a panel with three stacked horizontal bars (blue variance, tangerine bias²), each labelled with its sum; a colour key; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Error = bias² · + variance. · Each estimator's mean squared error, · split into its two parts. · mean squared error in tanks², N = 342, k = 5 · MLE · variance 2,293 + bias² 3,155 = 5,448 · MVUE · variance 3,303, bias 0 · m(k + 2)/(k + 1) − 1 · variance 3,122 + bias² 91 = 3,212 · blue: variance · tangerine: bias² · 58% of the MLE's error is bias. · The best rule spends 91 to save 181. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Stacked bars splitting three tank estimators' MSE into variance and bias²: MLE 2,293 plus 3,155, MVUE 3,303, stretch 3,122 plus 91.
- Long description: Mean squared error in squared tanks for N = 342 and k = 5, each split into variance (blue) and bias squared (tangerine). MLE: variance 2,293 plus bias² 3,155 equals 5,448. MVUE: variance 3,303, bias 0. The stretch m(k + 2)/(k + 1) − 1: variance 3,122 plus bias² 91 equals 3,212. Takeaway: 58% of the MLE's error is bias; the best rule spends 91 squared tanks of bias to save 181 of variance.
- Keywords: bias-variance decomposition, mean squared error, German tank problem, estimator, bias
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### feed-05-rao-blackwell

- File: `assets/social/feed-05-rao-blackwell.png`
- Title: Rao–Blackwell: average away the noise you can't use
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: conditioning 2 × mean − 1 on the largest serial removes 4,403 of its 7,706 variance and leaves the MVUE, 2.33 times less variable
- Technical source: How is the best unbiased estimator built?; Figure 5; The math, equation (4)
- Visual structure: lockup and counter; serif title; deck; a panel with the crude estimator's variance split into two terms, a rule, the conditional expectation formula and the MVUE's variance; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · Average away the · noise you can't use. · Rao–Blackwell: condition an estimator on · a statistic that holds all the information. · start: 2 × mean − 1, unbiased but wasteful · Var = 7,706 · = 4,403   scatter among captures with the same max · + 3,303   spread of the averages · average it over captures sharing the largest serial m: · E(2 × mean − 1 | m) = m(1 + 1/k) − 1 · Var = 3,303 · the MVUE: 2.33 = (k + 2)/3 times less variance · Conditioning on a sufficient statistic · never makes an estimator worse. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Card showing Rao–Blackwell on tank serials: variance 7,706 of 2 × mean − 1 splits into 4,403 removed and 3,303 kept by the MVUE.
- Long description: The crude unbiased estimator 2 × mean − 1 has variance 7,706, which splits into 4,403, the scatter among captures with the same largest serial, plus 3,303, the spread of the averages. Averaging it over captures sharing the largest serial m gives E(2 × mean − 1 given m) = m(1 + 1/k) − 1, the MVUE, with variance 3,303: 2.33 = (k + 2)/3 times less. Takeaway: conditioning on a sufficient statistic never makes an estimator worse.
- Keywords: Rao-Blackwell theorem, sufficient statistic, MVUE, conditional expectation, German tank problem
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### feed-06-n-minus-1-is-not-best

- File: `assets/social/feed-06-n-minus-1-is-not-best.png`
- Title: n − 1 buys unbiasedness, not the smallest error
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: exact MSEs of a variance estimate at n = 10: 0.2222, 0.1900 and 0.1818 for divisors n − 1, n and n + 1 on normal data; 0.8222 against 0.4512 at the best divisor, 16.4, on exponential data
- Technical source: Why divide by n − 1, and when not to?; Figure 7; The math, equations (5) and (6)
- Visual structure: lockup and counter; serif title; deck; a panel with two blocks, normal data (three divisors) and exponential data (two divisors), the best in tangerine, and the formula for the best divisor; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · n − 1 buys unbiasedness, · not the smallest error. · Estimating a variance: the exact mean · squared error of each divisor. · estimating a variance from n = 10: MSE of SS / d · normal data · divide by n − 1 · 0.2222 · divide by n · 0.1900 · divide by n + 1 · 0.1818 · exponential data · divide by n − 1 · 0.8222 · divide by 16.4, the best · 0.4512 · best d = n + 1 + (n − 1)κ/n, κ the excess kurtosis · n + 1 is best only for normal tails; · the best divisor grows with kurtosis. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Exact MSE of a variance estimate at n = 10: normal 0.2222, 0.1900, 0.1818 for n − 1, n, n + 1; exponential 0.8222 against 0.4512 at 16.4.
- Long description: The exact mean squared error of the sum of squares divided by d, estimating a variance of 1 from n = 10 observations. Normal data: dividing by n − 1 gives 0.2222, by n 0.1900, by n + 1 0.1818, the best. Exponential data: dividing by n − 1 gives 0.8222 and by the best divisor, 16.4, 0.4512. The best divisor is n + 1 + (n − 1)κ/n, where κ is the excess kurtosis. Takeaway: n + 1 is best only for normal tails; the best divisor grows with kurtosis.
- Keywords: sample variance, Bessel's correction, n-1, mean squared error, kurtosis
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### feed-07-steins-paradox

- File: `assets/social/feed-07-steins-paradox.png`
- Title: Stein's paradox, on 18 batters
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Efron and Morris's 18 batters: c = 0.212 moves every average 79% of the way to 0.265; Clemente .400 → .294, Munson .178 → .247; total squared error 0.0753 against 0.0213
- Technical source: What is Stein's paradox?; Figures 8 and 9; ledger L18, L19
- Visual structure: lockup and counter; serif title; deck; a panel with the shrinking factor, two players' averages before and after shrinkage with their rest-of-season averages, and the two total squared errors; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · Stein's paradox, · on 18 batters. · Averages after 45 at-bats in 1970, used · to predict each player's rest of season. · shrinking factor c = 0.212: every average moves · 79% of the way to the grand mean, 0.265 · Clemente · .400  →  .294 · first 45 at-bats → James–Stein; rest of season .346 · Munson · .178  →  .247 · first 45 at-bats → James–Stein; rest of season .316 · total squared error, all 18 players · own averages 0.0753 · James–Stein 0.0213 · James–Stein closer for 16 of 18 players · Shrinking all 18 toward their mean · cut the total error 3.5-fold. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: James–Stein on 18 batters of 1970: Clemente .400 to .294, Munson .178 to .247; total squared error 0.0753 against 0.0213.
- Long description: Efron and Morris's 18 major-league players after 45 at-bats in 1970, used to predict each player's average over the rest of the season. The James–Stein shrinking factor c = 0.212 moves every average 79% of the way to the grand mean, 0.265. Clemente's .400 becomes .294 (rest of season .346); Munson's .178 becomes .247 (rest of season .316). Total squared error over all 18 players: own averages 0.0753, James–Stein 0.0213, with James–Stein closer for 16 of 18 players. Takeaway: shrinking all 18 toward their mean cut the total error 3.5-fold.
- Keywords: Stein's paradox, James-Stein estimator, shrinkage, Efron and Morris, batting averages
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Estimators and their errors: read the article
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four results of the article in one list, and the call to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a panel listing four results, each a heading, a line and a number; takeaway; call to action with the URL
- Visible-text transcript: Canery.in · 08 / 08 · Estimators and · their errors. · Every number measured by a seeded lab · you can rerun in about 13 seconds. · bias² + variance · unbiasedness removes one term · tanks: MLE 5,448, MVUE 3,303 · Rao–Blackwell · condition on a sufficient statistic · variance ÷ 2.33 · n + 1 · beats n − 1 for normal data · 18% lower MSE at n = 10 · James–Stein · smaller error in 96.2% of replayed seasons · 1970: 3.5 times less total error · The full walk-through, with the lab · and every number's Monte Carlo error. · READ IT AT CANERY.IN/BLOGS/ESTIMATOR-BIAS-VARIANCE-MSE
- Alt text: Closing card listing the article's four results: bias² plus variance, Rao–Blackwell, the n + 1 divisor and James–Stein.
- Long description: A summary of the article. Bias² + variance: unbiasedness removes one term; for the tanks, MLE 5,448 against MVUE 3,303. Rao–Blackwell: condition on a sufficient statistic; the variance falls 2.33-fold. n + 1: beats n − 1 for normal data, with 18% lower MSE at n = 10. James–Stein: smaller error in 96.2% of replayed seasons, and 3.5 times less total error in 1970. Every number is measured by a seeded lab you can rerun in about 13 seconds. Call to action: read it at canery.in/blogs/estimator-bias-variance-mse.
- Keywords: estimators, bias-variance, Rao-Blackwell, James-Stein estimator, statistics for data scientists
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### story-01-the-best-can-be-biased

- File: `assets/social/story-01-the-best-can-be-biased.png`
- Title: The best estimator can be biased
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: three cases where a biased estimator has the lowest mean squared error: the tank stretch, the n + 1 divisor and James–Stein
- Technical source: Insights; Figures 3, 7 and 9
- Visual structure: lockup and counter; serif title; deck; a panel with three cases, each a heading, the comparison and the biased winner in tangerine, with a note at the right; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · The best estimator · can be biased. · Unbiasedness removes one term · of the error, not both. · German tanks, MSE · MLE 5,448 · MVUE 3,303 · biased stretch 3,212 · N = 342, k = 5 · a variance, n = 10 · n − 1: 0.222 · n + 1: 0.182 · normal data · 18 batters, total error · averages 0.0753 · James–Stein 0.0213 · 1970 season · Judge an estimator by its · mean squared error. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Story card with three cases where a biased estimator wins: tank stretch 3,212, divisor n + 1 0.182, James–Stein 0.0213.
- Long description: Three cases where a biased estimator has the lower mean squared error. German tanks, N = 342 and k = 5: MLE 5,448, MVUE 3,303, biased stretch 3,212. A variance from n = 10 normal observations: divisor n − 1 gives 0.222, n + 1 gives 0.182. 18 batters in the 1970 season: total squared error 0.0753 for the averages, 0.0213 for James–Stein. Takeaway: judge an estimator by its mean squared error.
- Keywords: biased estimator, mean squared error, German tank problem, Bessel's correction, James-Stein estimator
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### story-02-steins-paradox

- File: `assets/social/story-02-steins-paradox.png`
- Title: Stein's paradox
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: James–Stein moves Clemente's .400 to .294 and Munson's .178 to .247, cutting the total squared error 3.5-fold, closer for 16 of 18 players
- Technical source: What is Stein's paradox?; Figure 9; ledger L18, L19
- Visual structure: lockup and counter; serif title; deck; a panel with two players' averages before and after shrinkage and their rest-of-season averages, then a large 3.5× with two lines; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · Stein's · paradox. · 18 batting averages after · 45 at-bats, 1970. · first 45 at-bats → James–Stein · Clemente · .400 → .294 · rest of the season: .346 · Munson · .178 → .247 · rest of the season: .316 · 3.5× · less total squared error · closer for 16 of 18 players · Pull every average toward · the mean: less error in total. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Story card on Stein's paradox: Clemente .400 to .294, Munson .178 to .247, and 3.5 times less total squared error for 18 batters.
- Long description: Efron and Morris's 18 batting averages after 45 at-bats in 1970, shrunk by the James–Stein estimator. Clemente: .400 becomes .294; his rest-of-season average was .346. Munson: .178 becomes .247; his rest-of-season average was .316. Over all 18 players the total squared error is 3.5 times smaller, with James–Stein closer for 16 of 18 players. Takeaway: pull every average toward the mean for less error in total.
- Keywords: Stein's paradox, James-Stein estimator, shrinkage, batting averages, empirical Bayes
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### story-03-five-serial-numbers

- File: `assets/social/story-03-five-serial-numbers.png`
- Title: Five tanks: how many exist?
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: the German tank problem by hand: the MLE 303 (bias −56.2, RMSE 73.8) against the MVUE 362.6 (unbiased, RMSE 57.5), with the true N 342
- Technical source: Worked example, one capture by hand; the table of bias and RMSE; Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with the five serials, then the MLE and the MVUE each with its value at the right and its bias and RMSE below, then the true N in tangerine; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · Five tanks. · How many exist? · The German tank problem, · by hand. · captured: 58, 171, 272, 273, 303 · MLE, the largest serial · 303 · bias −56.2, RMSE 73.8 · MVUE, plus one average gap · 362.6 · unbiased, RMSE 57.5 · true N = 342 · Germany's recorded production, August 1942 · Add one average gap: · 303 + 59.6 = 362.6. · ESTIMATORS AND THEIR ERRORS · CANERY.IN
- Alt text: Story card on the German tank problem: serials up to 303, MLE 303 with bias −56.2, MVUE 362.6 unbiased, true N 342.
- Long description: The German tank problem by hand. Captured serial numbers: 58, 171, 272, 273 and 303. The MLE, the largest serial, is 303, with bias −56.2 tanks and RMSE 73.8. The MVUE adds one average gap and is 362.6, unbiased, with RMSE 57.5. The true N is 342, Germany's recorded production in August 1942. Takeaway: add one average gap, 303 + 59.6 = 362.6.
- Keywords: German tank problem, MVUE, maximum likelihood, serial numbers, estimation
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Estimators and their errors
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: the four ideas of the article as numbered steps, and the link sticker
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel with four numbered steps; takeaway; call to action pointing at the link sticker
- Visible-text transcript: Canery.in · 04 / 04 · Estimators and · their errors. · Bias, variance and Stein's paradox, · measured, with a lab you can rerun. · 1 · MSE = bias² + variance · 2 · condition on a sufficient statistic · 3 · n − 1 is unbiased, not best · 4 · shrink many averages to their mean · The full walk-through is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Closing story card with four steps: MSE is bias² plus variance, condition on a sufficient statistic, n − 1 is not best, shrink.
- Long description: The four ideas of the article as numbered steps: MSE = bias² + variance; condition on a sufficient statistic; n − 1 is unbiased, not best; shrink many averages to their mean. The full walk-through, measured with a lab you can rerun, is on Canery; the link is in the sticker above.
- Keywords: estimators, bias-variance, Rao-Blackwell, sample variance, James-Stein estimator
- Canonical URL: https://canery.in/blogs/estimator-bias-variance-mse
