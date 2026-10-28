---
title: "Estimators and Their Errors: Why the Best One Can Be Biased"
slug: estimator-bias-variance-mse
date: 2026-10-28
updated: 2026-10-28
summary: "Unbiased is not best: on German tank serial numbers, variance divisors and 18 batting averages, a deliberately biased estimator has lower mean squared error."
tags: [data-science, statistics, point-estimation, bias-variance, mean-squared-error, german-tank-problem, james-stein-estimator]
category: data-science
series: statistics-for-data-scientists
series_position: 3
tier: L3
difficulty: intermediate
prerequisites: ["sampling distributions and standard errors", "expectation and variance", "Python with NumPy"]
reading_minutes: 30
cover_image: "COVER"
canonical_url: "https://canery.in/blogs/estimator-bias-variance-mse"
---

![Sampling distributions of two tank-count estimators: the MLE piled against a wall at the true 342, the MVUE centred on it](COVER)

> [!NOTE]
> **Insights** — An estimator is judged by its mean squared error (MSE), the expected squared miss, which splits into bias² plus variance. Unbiasedness removes only the first term, so the best estimator can be biased. Counting German tanks from five serial numbers, the unbiased estimator beats the biased maximum (3,303 against 5,448 squared tanks), yet a slightly biased stretch of the maximum beats both. For normal data, dividing a sum of squares by n + 1 beats the unbiased n − 1. And pulling 18 batting averages toward their grand mean, the James–Stein estimator, cut the total squared error of Efron and Morris's 1970 forecast 3.5-fold.

**Level:** intermediate · **You need:** sampling distributions and standard errors, expectation and variance, Python with NumPy · **Time:** ~30 min

**Jump to:** [worked example](#worked-example) · [the best unbiased estimator](#how-is-the-best-unbiased-estimator-built) · [consistency](#is-unbiased-the-same-as-consistent) · [n − 1](#why-divide-by-n--1-and-when-not-to) · [Stein's paradox](#what-is-steins-paradox) · [how much shrinking gains](#how-much-does-shrinking-gain) · [math](#the-math) · [mistakes](#limitations-and-common-mistakes)

> [!IMPORTANT]
> Numbers this post calls **measured** come from its lab: one NumPy and SciPy script that runs in about 13 seconds and is seeded, so every number repeats exactly. Each simulated quantity is printed as an estimate ± its Monte Carlo standard error (MCSE) with its number of replications R, and set beside its exact value wherever one exists. Published numbers are **quoted** from their sources.

## Why this matters

Suppose you rank 18 stores, campaigns or sales reps by an early rate and plan the quarter on those rates. Each one's own rate is an unbiased estimate of its true rate, and together they forecast badly. Efron and Morris ran this test on 18 baseball players in 1970: the averages after 45 at-bats predicted the rest of the season with a total squared error 3.5 times that of an estimate that pulled every average toward the group's mean. <!-- L15 --> <!-- L19 --> At the 1972 meeting of the American Statistical Association, John Tukey had said such estimators would save no more than ten percent in practice. <!-- L17 --> The instinct behind that forecast, that an unbiased estimator is the safe default, is what this post measures.

## The problem

You want a population quantity, the **estimand** θ. You compute it from a sample with a rule, the **estimator** θ̂, a random variable before the sample is drawn; its realised value is the **estimate**. These terms, with the sampling distribution and the standard error, come from the second part of this series, *The Sampling Distribution: The CLT and Where n = 30 Fails*. That part asked how an estimator varies. This one asks which estimator to use.

Choosing needs a yardstick. A **loss function** scores one miss, and the usual one is squared error, (θ̂ − θ)². Its expectation over samples, the **risk**, is then the **mean squared error (MSE)**, and it splits into two parts: MSE = bias² + variance. The **bias**, E(θ̂) − θ, is how far the estimator's average sits from the truth; the **variance** is how much it scatters around its own average. The square root of the MSE, the **RMSE**, is in θ's units.

An **unbiased** estimator has zero bias. That removes one term of the MSE and says nothing about the other. Unbiasedness earns its keep when many estimates are added or averaged, because their errors then cancel. When one estimate must land close, the MSE is the yardstick.

One more property of the yardstick matters later. An estimator's MSE depends on the true value: the rule "always answer 342" has MSE zero if N is 342 and grows without limit as N moves away. So estimators are compared by their **risk function**, the MSE at every possible θ, and one estimator **dominates** another if its risk is no higher anywhere and lower somewhere. Stein's paradox, below, is a statement about domination.

The test case is the **German tank problem**: tanks carry serial numbers 1 to N, you capture k of them with every tank equally likely to be caught, and you estimate N from their serials. <!-- L05 --> From 1943, Allied economic intelligence did this with serial numbers read on captured tanks' chassis, engines, gearboxes and road wheels, because estimates from prewar capacity, agents' reports and prisoner interrogation were unreliable or contradicted each other. <!-- L01 --> <!-- L02 --> The real numbering was messier than the textbook's: gearbox numbers ran in one unbroken sequence, while chassis numbers came in blocks by model. <!-- L04 -->

The claim this post tests is the one most of us absorbed with our first estimator: unbiased estimators are the best ones.

## Worked example

### One capture, by hand

Take N = 342, Germany's recorded tank production in August 1942, quoted below, and capture k = 5 tanks. One seeded capture from the lab gives serial numbers 58, 171, 272, 273 and 303 (Figure 1).

![Five captured serial numbers on a line from 0 to 560, with the MLE at 303, the MVUE at 362.6 and the true N = 342 marked](FIG_01)
*Figure 1. The largest serial is a floor for N, not an estimate of it. The MVUE adds one average gap, 59.6, beyond it.*

Four estimators read this capture four ways:

- **The largest serial, m = 303.** Every set of five serials has the same probability, 1/C(N, 5), which falls as N grows, so the N that makes this capture most probable is the smallest one allowed: 303. That makes m the **maximum likelihood estimator (MLE)** here; likelihood in general is the subject of a later part of this series. It can never exceed N, so it is biased low. <!-- L05 -->
- **m(1 + 1/k) − 1 = 362.6**, the **minimum-variance unbiased estimator (MVUE)**, the unbiased estimator with the smallest variance at every N. Below 303 sit 303 − 5 = 298 unseen serials in five gaps, 59.6 per gap; assume one more gap of that size above the largest. Leo Goodman derived it in 1952. <!-- L06 -->
- **2 × mean − 1 = 429.8.** The serials are uniform on 1 to N, whose mean is (N + 1)/2, so twice the sample mean minus 1 is unbiased. Here the mean is 215.4.
- **2 × (one tank's serial) − 1 = 543**, using one captured tank, here serial 272. Unbiased for the same reason.

### A million captures

One capture cannot say which rule is better; their sampling distributions can. The lab repeats the capture R = 1,000,000 times and applies every rule to each (Figure 2).

![Three histograms of a million estimates of N = 342: the MLE stops at 342, the MVUE centres on it, 2 × mean − 1 spreads widest](FIG_02)
*Figure 2. The MLE piles up against a wall at the true N. Stretching it by (1 + 1/k) moves the pile onto N at the price of a wider spread.*

The MLE never exceeds 342 and equals it only when tank 342 is among the five: in 1.47% ± 0.01 of captures, against exactly 5/342 = 1.46%. Its average is k(N + 1)/(k + 1) = 285.8, a bias of −56.2 tanks; simulated, −56.22 ± 0.05. The MVUE centres on 342 (simulated bias −0.07 ± 0.06) and scatters more, with SD 57.5 against the MLE's 47.9. The thin lines in Figure 2 are the exact distributions, computed from the probability of each maximum, C(m − 1, k − 1)/C(N, k); the simulation sits on them.

### Bias and variance, added up

| Estimator | Bias | SD | MSE (tanks²) | RMSE |
|---|---|---|---|---|
| MLE, m | −56.2 | 47.9 | 5,448 | 73.8 |
| MVUE, m(1 + 1/k) − 1 | 0 | 57.5 | 3,303 | 57.5 |
| m(k + 2)/(k + 1) − 1 | −9.5 | 55.9 | 3,212 | 56.7 |
| 2 × mean − 1 | 0 | 87.8 | 7,706 | 87.8 |
| 2 × one tank − 1 | 0 | 197.5 | 38,988 | 197.5 |

The table is exact, computed from the distribution of the maximum, and every simulated bias and MSE lies within one and a half MCSEs of it. Figure 3 splits each MSE into its two parts.

![Stacked bars of MSE as variance plus bias² for four estimators: MLE 5,448 with bias² 3,155; MVUE 3,303; m(k+2)/(k+1) − 1 3,212](FIG_03)
*Figure 3. Bias costs the MLE more than its variance does. The third bar spends 91 squared tanks of bias to save 181 of variance.*

Read it in three steps. First, the unbiased MVUE beats the biased MLE: the MLE's MSE is 1.65 times larger (simulated 1.6508 ± 0.0013), 58% of it is bias², and the MVUE lands closer to N in 62.1% of captures. Second, unbiasedness does not rank estimators: three unbiased rules have MSEs of 3,303, 7,706 and 38,988. Third, the best rule in the table is biased. Stretching the maximum a little less, by (k + 2)/(k + 1) instead of (k + 1)/k, adds a bias of −9.5 tanks and cuts the MSE by 2.7% (simulated ratio 0.9731 ± 0.0003, exact 0.9727). That stretch minimises the MSE for a continuous uniform (derived under The math); the best stretch for this N is 1.1672 against 1.1667, but finding it needs N.

### Against the records

After the war, Ruggles and Brodie set the serial-number estimates beside the intelligence estimates and Germany's own production records. As reproduced, identically, in two recent papers, monthly tank production in June 1940 was estimated at 1,000 by intelligence and 169 from serial numbers, against 122 in the records; in June 1941, 1,550 and 244 against 271; in August 1942, 1,550 and 327 against 342 (Figure 4). <!-- L03 -->

![Log-scale dots for June 1940, June 1941 and August 1942: intelligence 1,000 to 1,550 tanks, serial numbers 169 to 327, records 122 to 342](FIG_04)
*Figure 4. The statistical estimates missed by 4.4% to 38.5%. Conventional intelligence ran 4.5 to 8.2 times the records.*

The 1940s analysts worked from several serial sequences, some of them broken into blocks by model, so their numbers are not one formula applied to five tanks. <!-- L01 --> <!-- L04 --> The lesson survives the simplification: an estimator chosen for its error beat confident guesses that had no error model at all.

## Intuition

Two ideas carry every result in this post.

The first is that the maximum holds all the information. Given the largest serial m, the other four are scattered uniformly below it, whatever N is. <!-- L07 --> Once you know m, the rest of the capture tells you nothing more about N, only about how the serials happened to fall. The k serials cut 1 to m into k gaps, and the MVUE assumes one more gap of average size above m.

The second is that shrinking pays when noise dominates. Take an unbiased estimate with variance σ² and report c times it instead. Its MSE becomes c²σ² + (1 − c)²θ²: a smaller c cuts variance by c² and adds bias in proportion to θ. The best c is θ²/(θ² + σ²), always below 1, and smaller the noisier the estimate is relative to what it estimates. Every win for a biased estimator below is this trade: stretching the maximum a little less, dividing by n + 1 instead of n − 1, and pulling 18 averages toward their mean.

The best c depends on θ, which is unknown; the estimators below estimate it from the data. Think of a weather forecaster who blends a noisy local reading with the seasonal norm, leaning on the norm more when the reading is noisier. The analogy breaks at Stein's paradox: the forecaster's norm is relevant to the reading, while James–Stein pulls each estimate toward the mean of whatever was estimated alongside it, related or not, and still lowers the total error.

## How is the best unbiased estimator built?

Start from the crude unbiased rule 2 × mean − 1, which uses every serial but wastes information. Average it over all captures that share the same maximum m. Given m, the other k − 1 serials are uniform on 1 to m − 1 with mean m/2 each, so the average of 2 × mean − 1 is exactly m(1 + 1/k) − 1: the MVUE (Figure 5).

![Scatter of 2 × mean − 1 against the largest serial for 3,000 captures, with conditional means lying on the line m(1 + 1/k) − 1](FIG_05)
*Figure 5. Each vertical slice is the noise that conditioning on m removes: at m = 300 its SD is 69 tanks.*

That conditioning step is the **Rao–Blackwell theorem** (Rao 1945, Blackwell 1947): replacing an estimator by its conditional expectation given a sufficient statistic never makes it worse under squared-error loss, or any convex loss. <!-- L09 --> A **sufficient statistic** is a summary that keeps all the information the data carry about θ; here it is m. Measured over a million captures, the average of 2 × mean − 1 at each m lies on a line with slope 1.2004 ± 0.0014 and intercept −1.10 ± 0.40, against the MVUE's 1.2 and −1. The variance falls from 7,706 to 3,303, a factor of (k + 2)/3 = 2.33; simulated, 2.3305 ± 0.0035.

Why the variance must fall: the variance of any rule T splits into the average spread within each value of m plus the spread of the averages, Var(T) = E[Var(T | m)] + Var(E[T | m]). Conditioning keeps the second term and deletes the first. Here 7,706 = 4,403 + 3,303, and the 4,403 squared tanks are the vertical scatter in Figure 5: noise about how the serials fell below m, which says nothing about N.

Because m is also complete, meaning no function of m other than zero averages to zero at every N, the Lehmann–Scheffé theorem makes m(1 + 1/k) − 1 the unique MVUE: every unbiased estimator, conditioned on m, lands on it. <!-- L07 --> "Best unbiased" therefore means best among unbiased rules only, and Figure 3 already showed a biased rule that beats it.

## Is unbiased the same as consistent?

No. An estimator is **consistent** if its error shrinks to zero as the sample grows. Unbiasedness is a statement about one sample size; consistency is a statement about all of them (Figure 6).

![Log–log RMSE against tanks captured: one-tank estimator flat at 197.5, mean-based falling like 1/√k, maximum-based like 1/k](FIG_06)
*Figure 6. The one-tank rule is unbiased at every k and never improves. The MLE is biased at every k below N and still converges.*

The one-tank rule, 2 × (one serial) − 1, is unbiased with any capture, and its RMSE stays at 197.5 tanks however many tanks you catch: unbiased, not consistent. The MLE is biased at every k below N, by −56.2 at k = 5 and −2.40 at k = 100, and its error goes to zero: biased, consistent. From k = 10 to k = 100 the MVUE's RMSE falls 10.8-fold, while that of 2 × mean − 1 falls only 3.7-fold. Errors of maximum-based rules shrink like 1/k, errors of mean-based rules like 1/√k, the rate the second part of this series found for every mean.

The faster rate comes from the maximum's edge. The expected gap between the largest serial and N is (N − k)/(k + 1), roughly N/(k + 1): ten times as many tanks leave a top gap ten times smaller, and every rule built on the maximum inherits that. A mean of k serials instead carries the spread of one serial, N/√12 for a uniform, divided by √k. In a finite population the sample cannot outgrow N, and at k = N every rule built from the whole capture is exact; read Figure 6 for k well below N.

## Why divide by n − 1, and when not to?

For a sample x₁, …, xₙ the sum of squares is SS = Σ(xᵢ − x̄)². Dividing it by n − 1 makes SS/(n − 1) unbiased for σ² in any population with a finite variance: at n = 10 the lab measures its average as 0.9992, 0.9998 and 1.0000 times σ² for normal, uniform and exponential data. Unbiasedness then fails twice over.

First, the square root does not keep it: the sample SD s = √(SS/(n − 1)) is biased low, its average below σ, because a square root bends averages downward. For normal data E(s) = c₄σ, where c₄ is 0.7979 at n = 2 and 0.9727 at n = 10 (simulated 0.9725 ± 0.0005); Student found the distribution of s for normal samples in 1908. <!-- L27 -->

Second, it is not the most accurate divisor. Two observations show why by hand. With x₁ and x₂, SS = (x₁ − x₂)²/2, and for normal data SS/σ² has a chi-squared distribution with one degree of freedom, mean 1 and variance 2. <!-- L27 --> Dividing by n − 1 = 1 is unbiased, with MSE 2σ⁴. Dividing by n + 1 = 3 gives a bias of −2σ²/3 and a variance of 2σ⁴/9, an MSE of 4/9 + 2/9 = 2/3 of σ⁴: three times smaller. In general, for normal data Var(s²) = 2σ⁴/(n − 1), <!-- L26 --> and the MSE of SS/d is smallest at d = n + 1. At n = 10 the MSE is 0.2222 σ⁴ with n − 1, 0.1900 with n and 0.1818 with n + 1, 18% below n − 1's.

| n | E(s)/σ, normal data | MSE with n − 1 ÷ MSE with n + 1 |
|---|---|---|
| 2 | 0.798 | 3.00 |
| 5 | 0.940 | 1.50 |
| 10 | 0.973 | 1.22 |
| 30 | 0.991 | 1.07 |
| 100 | 0.997 | 1.02 |

The table bounds the debate. From n = 30 the divisor moves the MSE by 7% or less and the SD's bias is under 1%; below n = 10 both matter.

![MSE of the sum of squares divided by d at n = 10: minimum at 11 for normal, 9.92 for uniform and 16.4 for exponential data](FIG_07)
*Figure 7. The best divisor moves with the tails: n + 1 is optimal only for the normal.*

That n + 1 needs normal tails. For any population with a finite fourth moment the best divisor is d = n + 1 + (n − 1)κ/n, where κ is the **excess kurtosis**, E(X − μ)⁴/σ⁴ − 3, a measure of tail weight that is 0 for the normal (derived under The math). For a uniform population, κ = −1.2, the best divisor at n = 10 is 9.92, and n − 1 and n + 1 are within 0.7% of each other. For an exponential, κ = 6, it is 16.4 (simulated optimum 16.41 ± 0.04), and dividing by it gives an MSE 45% below n − 1's (Figure 7).

So keep n − 1 where unbiasedness is used: in a t statistic, whose distribution assumes it, and in variances pooled or averaged across groups. For a single variance estimate judged by squared error, n − 1 is never the most accurate divisor, and the best one depends on the tails.

## What is Stein's paradox?

### Eighteen batting averages

Efron and Morris took the 18 major-league players that the *New York Times* of 26 April or 3 May 1970 listed with exactly 45 at-bats, so that every average had the same variance, and made sure the sample held an unusually good hitter, Roberto Clemente. The task: predict each player's average over the rest of the season. <!-- L13 -->

Each player's own average y is unbiased for his ability, with binomial variance σ² = ȳ(1 − ȳ)/45 at the grand average ȳ. The **James–Stein estimator**, in the raw-scale form of their 1977 article, is z = ȳ + c(y − ȳ), with shrinking factor c = 1 − (k − 3)σ²/Σ(y − ȳ)². <!-- L20 --> For these players ȳ = 0.265, σ² = 0.00433 and c = 0.212, so every average moves 79% of the way to 0.265: Clemente's 0.400 becomes 0.294 and Thurman Munson's 0.178 becomes 0.247. <!-- L18 --> Over the rest of the season they hit 0.346 and 0.316.

### The comparison, recomputed

Against the rest-of-season averages, the 18 own averages have a total squared error of 0.0753 and the James–Stein estimates 0.0213, a ratio of 3.53; James–Stein is closer for 16 players and further for Ron Swoboda and Ellie Rodriguez (Figure 9). The 1977 article prints 0.077 and 0.022, a ratio of 3.5, and the same 16 of 18. <!-- L19 --> No variant the lab tried reproduces 0.077 (the table's printed averages give 0.0754; full-season averages give 0.0591), but the ratio agrees.

The 1975 paper worked on a transformed scale. Its **arcsine transform**, √45 · arcsin(2y − 1), gives each average a variance close to 1 across the range of batting abilities, and its rule shrinks the transformed averages toward their mean with constant k − 3; the paper's estimate of the shrinkage, (k − 3)/V, is 0.791. <!-- L14 --> The total squared error was 17.56 for the averages and 5.01 for Stein's rule, an efficiency of 3.50, with Stein closer for 15 players and worse for Clemente, Swoboda and Rodriguez. <!-- L15 --> The lab gets 17.571, 4.999 and 3.515, and the same three exceptions. One line of the paper does not reconcile: its text gives the mean of the transformed averages as −3.275 and the rule as 0.209X − 2.59, but the column it averages has mean −3.317, and the paper's own back-transformed estimates match −3.317. <!-- L16 --> The slip is in the text, not in the analysis.

![Rest-of-season against first-45 batting averages for 18 players, with slope-1, James–Stein (0.212) and hindsight (0.190) lines](FIG_08)
*Figure 8. Using each player's own average assumes slope 1. With hindsight the best line has slope 0.190; James–Stein found 0.212 from the first 45 at-bats alone.*

Figure 8 shows why it works. Regressing the rest-of-season averages on the first-45 averages across the 18 players gives a slope of 0.190; predicting each player by his own average assumes a slope of 1. James–Stein estimates the slope from the first 45 at-bats alone, and its 0.212 lands near the hindsight value: the total squared error with the hindsight slope is 0.0213, the same to four decimals. Stigler showed that, seen as Galton's regression toward the mean, Stein's paradox is transparent. <!-- L25 -->

### Where the shrinking factor comes from

The factor c has a reading that removes most of the mystery. Suppose the players' true abilities are themselves spread around the grand mean with variance τ², and each observed average adds binomial noise with variance σ². Then the best estimate of a player's ability shrinks his average toward the mean by the share of the observed variance that is noise, σ²/(σ² + τ²), and the spread of the averages themselves estimates σ² + τ². <!-- L32 --> For 1970, Σ(y − ȳ)²/(k − 3) = 0.00550, of which σ² = 0.00433 is noise. That leaves τ² of about 0.00116, a true-ability SD near 0.034 against a noise SD of 0.066 in 45 at-bats. So 79% of what separated the players after 45 at-bats was luck, and James–Stein removes 79% of every player's distance from the mean. This is the **empirical Bayes** reading: the data estimate the prior that the estimator shrinks toward, the idea the Intuition section needed when the best c depended on the unknown θ.

![Per-player squared errors for 18 batters: James–Stein closer for 16, further for Swoboda and Rodriguez; totals 0.0753 and 0.0213](FIG_09)
*Figure 9. Most of the 3.5 comes from the extremes: Munson's squared error falls from 0.0191 to 0.0048.*

### Why it is a paradox

For one or two normal means with known variance, estimating each by its own observation is **admissible**: no other estimator is at least as good at every θ and strictly better at some. For a single mean that had been proved in 1950. <!-- L21 --> From three means on, it is **inadmissible**: Stein proved in 1956 that some estimator has lower total squared error whatever the true means are. <!-- L10 --> James and Stein wrote one down in 1961, and among unbiased estimators the separate observations are still the best. <!-- L11 --> <!-- L12 --> The paradox is in what the estimator does: Clemente's estimate depends on Max Alvis's average, although nothing connects the two players but the arithmetic.

## How much does shrinking gain?

### Was 1970 a lucky season?

The 1977 article states that 3.5 is close to the expected ratio for these data. <!-- L30 --> The lab replays the season instead: it sets each player's true ability to his rest-of-season average, draws his 45 at-bats again, and repeats this R = 200,000 times (Figure 10).

![Histogram of 200,000 replayed seasons' error ratios: 96.2% above break-even, median 3.05, the real 1970 ratio 3.53 in the top quarter](FIG_10)
*Figure 10. James–Stein wins in almost every replayed season, and 1970's 3.53 sits in the top quarter.*

James–Stein has the smaller total in 96.2% ± 0.04 of replayed seasons. The ratio of the two totals has median 3.05, and 90% of seasons fall between 1.15 and 4.17; 1970's 3.53 is reached in 25.1%. The ratio of the mean totals, the efficiency, is 2.658 ± 0.002. So the win is no fluke, and its size in 1970 was a good draw rather than a typical one. The replay understates James–Stein, though: the rest-of-season averages carry their own sampling noise, which spreads the true abilities wider than they are, and narrower true abilities favour Stein's rule. <!-- L29 -->

Plain James–Stein can also overshoot. In 14.8% of replayed seasons the 18 averages happened to be so close together that c fell below zero, flipping every player to the far side of the grand mean. The **positive-part rule**, max(c, 0), never shrinks past the mean, and it raises the efficiency to 2.827 ± 0.002.

### The exact risk

Figure 11 shows the whole picture for 18 normal means with variance 1. The separate observations have total risk 18 everywhere. James–Stein's risk depends only on the spread of the true means, Σ(θ − θ̄)²: it is 3 when all true means are equal, six times better; 6.81 at the batters' spread on the arcsine scale, 2.64 times better; and 17.16 at a spread of 256, almost no better. <!-- L11 --> It never exceeds 18.

![James–Stein risk against the spread of 18 true means: 3 when equal, 6.81 at the batters' spread, rising toward the flat 18](FIG_11)
*Figure 11. Shrinking gains most when the true means are close together relative to the noise, and in total it never loses.*

The exact efficiency at the batters' spread, 2.64, agrees with the binomial replay's 2.66: two independent routes to the same expected gain. A saving of ten percent, Tukey's ceiling, needs a spread of about 112, true means that vary 2.6 times as much as the noise in one estimate. <!-- L17 --> The batters' true averages varied 0.58 times as much: the players differed from each other by less than 45 at-bats could measure.

## The math

| Symbol | Meaning |
|---|---|
| θ, θ̂ | estimand and estimator |
| N, k, m | number of tanks, tanks captured, largest serial captured |
| n, SS, d | sample size, sum of squares Σ(xᵢ − x̄)², divisor |
| σ², κ | population variance and excess kurtosis |
| k, X, θ (Stein) | number of means, observations with variance 1, their true means |

**Bias and variance.** Add and subtract E(θ̂):

$$
\operatorname{E}(\hat\theta - \theta)^2 = \big(\operatorname{E}\hat\theta - \theta\big)^2 + \operatorname{E}\big(\hat\theta - \operatorname{E}\hat\theta\big)^2 \tag{1}
$$

The cross term vanishes because E(θ̂ − Eθ̂) = 0, so MSE = bias² + variance. For the MLE in the worked example: 56.17² + 2,293.5 = 5,448.2.

**The maximum.** With every set of k serials equally likely,

$$
P(M = m) = \frac{\binom{m-1}{k-1}}{\binom{N}{k}}, \qquad \operatorname{E}M = \frac{k(N + 1)}{k + 1} \tag{2}
$$

The maximum is m when one serial is m and the other k − 1 come from 1 to m − 1. So the MLE's bias is (k − N)/(k + 1), which is −56.17 at N = 342 and k = 5, and m(1 + 1/k) − 1 is unbiased. Its variance is <!-- L08 -->

$$
\operatorname{Var}\!\left(M\Big(1 + \frac{1}{k}\Big) - 1\right) = \frac{(N + 1)(N - k)}{k(k + 2)} \tag{3}
$$

which is 343 × 337/35 = 3,302.6 tanks², the MVUE's MSE in the table.

**Rao–Blackwell.** Given M = m, the other k − 1 serials are a random subset of 1 to m − 1, each with mean m/2: <!-- L07 -->

$$
\operatorname{E}\!\left(2\bar X - 1 \,\middle|\, M = m\right) = \frac{2}{k}\left(m + (k - 1)\frac{m}{2}\right) - 1 = m\Big(1 + \frac{1}{k}\Big) - 1 \tag{4}
$$

Conditioning turned the wasteful unbiased rule into the best unbiased one, the line in Figure 5.

<details>
<summary>The best stretch of the maximum</summary>

For a continuous uniform on 0 to θ, the sample maximum M of k draws has E M = kθ/(k + 1) and E M² = kθ²/(k + 2). The MSE of cM is c² E M² − 2cθ E M + θ², which is smallest at c = θ E M / E M² = (k + 2)/(k + 1), with MSE θ²/(k + 1)². The unbiased stretch (k + 1)/k has MSE θ²/(k(k + 2)), so the biased stretch wins by a factor k(k + 2)/(k + 1)², which is 35/36 = 0.972 at k = 5. The discrete problem gives 0.9727.

</details>

**The variance divisor.** For i.i.d. data with finite fourth moment μ₄, <!-- L26 -->

$$
\operatorname{Var}\!\left(\frac{SS}{n - 1}\right) = \frac{\mu_4}{n} - \frac{(n - 3)\sigma^4}{n(n - 1)} = \sigma^4\left(\frac{2}{n - 1} + \frac{\kappa}{n}\right) \tag{5}
$$

With E SS = (n − 1)σ², the MSE of SS/d is

$$
\operatorname{MSE}(d) = \frac{\sigma^4}{d^2}\left[(n - 1)^2\Big(\frac{2}{n - 1} + \frac{\kappa}{n}\Big) + (n - 1 - d)^2\right], \qquad d^* = n + 1 + \frac{(n - 1)\kappa}{n} \tag{6}
$$

Setting the derivative in 1/d to zero gives d*. For normal data, κ = 0 and d* = n + 1; at n = 10 the MSE is 2/9 = 0.2222 at d = 9 and 2/11 = 0.1818 at d = 11, as measured.

**James–Stein.** For k ≥ 4 observations Xᵢ with variance 1, shrinking toward their mean X̄:

$$
\hat\theta_i = \bar X + \left(1 - \frac{k - 3}{V}\right)(X_i - \bar X), \qquad V = \sum_{j}(X_j - \bar X)^2 \tag{7}
$$

The factor (k − 3)/V estimates how much of the observed spread is noise: when V is small the averages agree, and the rule shrinks hard. Its total risk is exact: <!-- L11 -->

$$
\operatorname{E}\sum_i (\hat\theta_i - \theta_i)^2 = k - (k - 3)^2\, \operatorname{E}\frac{1}{k - 3 + 2K}, \qquad K \sim \operatorname{Poisson}\!\left(\tfrac{1}{2}\textstyle\sum_i (\theta_i - \bar\theta)^2\right) \tag{8}
$$

The subtracted term is positive for every θ, so the risk is below k everywhere. At zero spread K = 0, and the risk is k − (k − 3) = 3, Figure 11's left end. This is James and Stein's 1961 formula applied in the k − 1 directions orthogonal to the grand mean; the grand mean itself is estimated without shrinkage and costs 1.

## Implementation

The tank simulation fits in a screen. A random subset of k serials is the k smallest of N random keys:

```python
import numpy as np


def captures(n_tanks, k, reps, rng):
    """reps captures of k distinct serial numbers from 1..N: the k smallest of N random keys."""
    keys = rng.random((reps, n_tanks))
    return np.argpartition(keys, k - 1, axis=1)[:, :k] + 1


rng = np.random.default_rng(20261028)
N, k = 342, 5
s = captures(N, k, 20_000, rng)
m = s.max(axis=1)
for name, est in (("MLE", m), ("MVUE", m * (1 + 1 / k) - 1), ("2 x mean - 1", 2 * s.mean(axis=1) - 1)):
    err = est - N
    print(f"{name:13s} bias {err.mean():7.2f}   SD {err.std():6.2f}   RMSE {np.sqrt((err ** 2).mean()):6.2f}")
```

It prints:

```text
MLE           bias  -56.14   SD  47.69   RMSE  73.66
MVUE          bias    0.03   SD  57.23   RMSE  57.23
2 x mean - 1  bias   -0.50   SD  87.45   RMSE  87.45
```

With R = 20,000 the MCSE of each bias is about SD/√R, 0.3 to 0.6 tanks, so these agree with the exact −56.17, 0 and 0. The lab draws its captures with Floyd's algorithm instead, which needs memory for k serials per capture rather than N keys, and gives every stage its own random stream through NumPy's `SeedSequence`, so any stage reruns alone and repeats to the bit. <!-- L28 -->

James–Stein on the 1970 table is five lines:

```python
import numpy as np

hits, rest = np.loadtxt("data/efron_morris_1975_batting.csv", delimiter=",", skiprows=9, usecols=(3, 5), unpack=True)
y = hits / 45                                       # each player's average over his first 45 at-bats
ybar, k = y.mean(), len(y)
c = 1 - (k - 3) * (ybar * (1 - ybar) / 45) / ((y - ybar) ** 2).sum()
z = ybar + c * (y - ybar)                           # James-Stein: every average pulled toward ybar
print(round(ybar, 4), round(c, 4))                   # 0.2654 0.2117
print(round(((y - rest) ** 2).sum(), 4), round(((z - rest) ** 2).sum(), 4))   # 0.0753 0.0213
```

The CSV ships with the lab, with its provenance in nine header lines. The full lab adds the exact distributions, the Rao–Blackwell check, the consistency curves, the divisor study, the replayed seasons and the exact risk; see [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** choosing an estimator because it is unbiased. Unbiasedness removes the bias term of the MSE and leaves the variance free: the one-tank rule is unbiased with an MSE nearly twelve times the MVUE's. Under squared error the most accurate estimator is often biased: dividing by n + 1, stretching the maximum by (k + 2)/(k + 1), shrinking many averages toward their mean. Decide on the loss first, then pick the estimator that minimises it.

- **Reading James–Stein as better for every group.** It lowers the total, not each component. In 1970 it moved Swoboda and Rodriguez further from their rest-of-season averages. If one group's error matters more than the rest, a flagship store or a key account, do not shrink it with the others, or cap the move: Efron and Morris's limited-translation rule limits how far any one estimate may shift, and for 18 means it cuts the worst-case risk of a single estimate from 4.60 to 1.52 times that of its own average, while keeping 80% of Stein's saving. <!-- L33 -->
- **Shrinking toward the wrong target.** In Brown's field test on the 2005 season, the naive current averages were the worst predictor in every setting, and separating pitchers from other players mattered, because the two groups have different means. <!-- L23 --> The theorem allows any target, and shrinking toward any fixed point still dominates; <!-- L24 --> the gain comes only when the true values sit near it. Efron and Morris made the point with a car-import share of 0.200 lumped in with the 18 batters: its James–Stein estimate becomes 0.251. <!-- L22 -->
- **Using the equal-variance rule with unequal samples.** The rule above needs every estimate to have the same variance. With different sample sizes the right shrinkage differs per group, and unequal variances complicate the theory; <!-- L24 --> shrinkage with group-specific weights, as partial pooling, comes later in this series.
- **Shrinking one or two estimates.** With one or two means the separate estimates are admissible, and shrinking toward the grand mean needs at least four. <!-- L10 -->
- **Trusting the German-tank formula off its assumptions.** It needs serials numbered from 1, consecutively, with every tank equally likely to be caught. If the first serial is unknown, (max − min)(1 + 2/(k − 1)) − 1 is unbiased instead. <!-- L31 --> The bootstrap also fails for the sample maximum, a failure a later part of this series examines.
- **Carrying n + 1 into a test.** The t distribution assumes the n − 1 divisor; the n + 1 result is about a single variance estimate under squared error, and it holds only for normal tails.
- **Confusing this decomposition with the one in machine learning.** Bias and variance of a prediction error are a related decomposition with a different object, the prediction, and they belong to machine-learning practice, outside this series.

## Key takeaways

- An estimator's MSE is bias² plus variance. Unbiasedness sets the first term to zero and leaves the second unchecked, so it does not rank estimators: three unbiased tank estimators have MSEs from 3,303 to 38,988.
- The best unbiased estimator is built by conditioning a crude unbiased one on a sufficient statistic (Rao–Blackwell): 2 × mean − 1 becomes m(1 + 1/k) − 1, with 2.33 times less variance.
- Unbiased and consistent are different properties: one tank's serial is unbiased and never improves; the biased maximum converges like 1/k.
- Dividing by n − 1 makes s² unbiased but s biased, and for normal data dividing by n + 1 has 18% lower MSE at n = 10; with heavier tails the best divisor grows, to 16.4 for exponential data.
- Shrinking 18 batting averages toward their mean cut the 1970 forecast's total squared error 3.5-fold and wins in 96% of replayed seasons, but it guarantees only the total, and its gain depends on how close the true values are.

## Try it yourself

**E1, reproduce.** Using equation (2), compute the MLE's bias at N = 342 and k = 5, and the MVUE's variance from equation (3).

<details><summary>Answer</summary>

E M = 5 × 343/6 = 285.83, so the bias is 285.83 − 342 = −56.17 tanks. The variance is 343 × 337/(5 × 7) = 3,302.6 tanks², an SD of 57.5. The lab measures −56.22 ± 0.05 and an SD of 57.49 over a million captures.

</details>

**E3, predict.** Capture k = 20 tanks instead of 5. Before computing, predict the MLE's bias and whether the MLE's MSE moves closer to the MVUE's or further from it.

<details><summary>Answer</summary>

The bias is (k − N)/(k + 1) = −322/21 = −15.33 tanks. The ratio moves further from 1, from 1.65 toward 2: the MLE's bias² shrinks like 1/k², but so does the MVUE's whole MSE, and for large N the ratio approaches 2k/(k + 1). The exact ratio at k = 20 is 1.844; the lab's `--quick` run gives 1.8421 ± 0.0045.

</details>

The lab carries the full ladder, from reproducing these tables to diagnosing a simulation that reports a bias in an unbiased estimator, with self-checks and answers; see [Lab downloads](#lab-downloads).

## References

### Lab downloads

- [`README.md`](LAB_01) — grade, provenance, setup, run order, the E1–E4 exercises with answers, and cleanup.
- [`estimators.py`](LAB_02) — the five stages: tanks, consistency, divisors, baseball and stein.
- [`requirements.txt`](LAB_03) — the pinned NumPy and SciPy versions.
- [`efron_morris_1975_batting.csv`](LAB_04) — the 18 players of 1970, transcribed from Efron and Morris's table with provenance; put it in a `data` folder.
- [`ruggles_brodie_1947_tanks.csv`](LAB_05) — the three months of tank estimates and records, as reproduced from Ruggles and Brodie; put it in a `data` folder.
- [`captures.json`](LAB_06) — the author's full run, machine-readable, with the R cross-check.
- [`captures-quick.json`](LAB_07) — the author's `--quick` run, to compare with yours digit for digit.
- [`expected-output.txt`](LAB_08) — the author's full run as printed.
- [`notebook.ipynb`](LAB_09) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-estimator-bias-variance-mse.zip) — every file above in one zip, with the `data` folder in place.

### Sources

1. B. Efron and C. Morris. "Data analysis using Stein's estimator and its generalizations." *Journal of the American Statistical Association* 70(350): 311–319, 1975. https://doi.org/10.1080/01621459.1975.10479864
2. B. Efron and C. Morris. "Stein's paradox in statistics." *Scientific American* 236(5): 119–127, 1977. https://doi.org/10.1038/scientificamerican0577-119
3. W. James and C. Stein. "Estimation with quadratic loss." *Proceedings of the Fourth Berkeley Symposium on Mathematical Statistics and Probability* 1: 361–379, 1961. https://digitalassets.lib.berkeley.edu/math/ucb/text/math_s4_v1_article-19.pdf
4. C. Stein. "Inadmissibility of the usual estimator for the mean of a multivariate normal distribution." *Proceedings of the Third Berkeley Symposium on Mathematical Statistics and Probability* 1: 197–206, 1956. https://digitalassets.lib.berkeley.edu/math/ucb/text/math_s3_v1_article-15.pdf
5. R. Ruggles and H. Brodie. "An empirical approach to economic intelligence in World War II." *Journal of the American Statistical Association* 42(237): 72–91, 1947. https://doi.org/10.1080/01621459.1947.10501915
6. C. M. Simon. "A Bayesian treatment of the German tank problem." *The Mathematical Intelligencer* 46(2): 117–127, 2024. https://doi.org/10.1007/s00283-023-10274-6
7. S. J. Miller, K. Sharma and A. Yang. "The German tank problem with multiple factories." *The PUMP Journal of Undergraduate Research* 7: 231–257, 2024. https://doi.org/10.46787/pump.v7i0.4249
8. G. Clark, A. Gonye and S. J. Miller. "Lessons from the German tank problem." *The Mathematical Intelligencer* 43(4): 19–28, 2021. https://doi.org/10.1007/s00283-021-10082-w
9. L. A. Goodman. "Serial number analysis." *Journal of the American Statistical Association* 47(260): 622–634, 1952. https://doi.org/10.1080/01621459.1952.10483442
10. C. P. Robert and G. O. Roberts. "Rao–Blackwellisation in the Markov chain Monte Carlo era." *International Statistical Review* 89(2): 237–249, 2021. https://doi.org/10.1111/insr.12463
11. D. Blackwell. "Conditional expectation and unbiased sequential estimation." *The Annals of Mathematical Statistics* 18(1): 105–110, 1947. https://doi.org/10.1214/aoms/1177730497
12. L. D. Brown. "In-season prediction of batting averages: a field test of empirical Bayes and Bayes methodologies." *The Annals of Applied Statistics* 2(1): 113–152, 2008. https://doi.org/10.1214/07-AOAS138
13. C. N. Morris and M. Lysy. "Shrinkage estimation in multilevel normal models." *Statistical Science* 27(1): 115–134, 2012. https://doi.org/10.1214/11-STS363
14. S. M. Stigler. "The 1988 Neyman Memorial Lecture: a Galtonian perspective on shrinkage estimators." *Statistical Science* 5(1): 147–155, 1990. https://doi.org/10.1214/ss/1177012274
15. E. Benhamou. "A few properties of sample variance." arXiv preprint arXiv:1809.03774, 2018. https://arxiv.org/abs/1809.03774
16. Student. "The probable error of a mean." *Biometrika* 6(1): 1–25, 1908. https://doi.org/10.1093/biomet/6.1.1
17. V. Arel-Bundock. Rdatasets, `pscl::EfronMorris`. https://vincentarelbundock.github.io/Rdatasets/doc/pscl/EfronMorris.html (accessed 2026-10-28)
18. NumPy 2.5 documentation, "Parallel random number generation." https://numpy.org/doc/stable/reference/random/parallel.html (accessed 2026-10-28)
