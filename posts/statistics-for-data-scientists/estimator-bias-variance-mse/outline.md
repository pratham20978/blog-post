# Outline — estimator-bias-variance-mse

Series `statistics-for-data-scientists`, Part 3 of 18 (Foundations ladder; parent: Part 2). Private build file.

## Brief

- **Title:** Estimators and Their Errors: Why the Best One Can Be Biased (59 characters; the plan's title runs
  to 81, over the 60-character limit).
- **Answers:** what makes an estimator good, and why can a deliberately biased one beat every unbiased
  alternative?
- **Tier:** L3 (plan). Five things to learn: bias, variance and MSE on one problem; how the best unbiased
  estimator is built (sufficiency, Rao–Blackwell); consistency as a separate property; the variance divisor;
  Stein's paradox. The smallest honest worked example (five serial numbers, then a million captures) fills a
  screen. **Adjacent option:** L4 would add the Cramér–Rao bound and the MLE's asymptotics, which Part 4 owns.
- **Difficulty:** intermediate. Assumes Part 2's sampling distribution, standard error and MCSE; expectation
  and variance; NumPy. Proofs are sketched (Rao–Blackwell, the n + 1 divisor) or cited (James–Stein).
  **Adjacent option:** advanced would prove the James–Stein risk identity (Stein's lemma).
- **Lab:** G1 · runs anywhere · E1–E4 · access none (probe 2026-10-28 matches `access.md` except RAM
  available 2 GiB; the lab peaks at 0.13 GB). NumPy 2.5.4 and SciPy 1.18.1 in the series venv; R 4.5.2 as the
  private check of every exact value (agrees to 4 × 10⁻¹¹; 7 × 10⁻⁶ where the lab rounds the batters' spread).
- **Corrects:** "Unbiased estimators are the best ones."
- **Four-point angle:** reconcile (every simulated bias, SD and MSE against its exact value from the
  distribution of the maximum; R as a private check; both Efron–Morris comparisons recomputed from their
  table, with the 1977 article's 0.077 and the 1975 text's −3.275 explained); condition (sampling without
  replacement from 1..N, then broken in E4; n + 1 optimal only at zero excess kurtosis, broken with the uniform
  and the exponential; k ≥ 3 for Stein); measure (every rate and MSE with MCSE and R; 1970 replayed 200,000
  times); read the output (the Efron–Morris tables read column by column).

## Settled at research

- Ruggles and Brodie 1947 was not reachable; its three-month table comes from Simon 2024 and Miller, Sharma
  and Yang 2024, which agree. The article says "as reproduced by".
- The worked population is N = 342, Germany's recorded production in August 1942, with k = 5 tanks captured,
  a textbook simplification: the 1940s analysts worked from gearbox, chassis and wheel numbers.
- The batting table ships as a CSV transcribed from the 1975 Table 1 and cross-checked against Rdatasets'
  `pscl::EfronMorris` (all 18 rows equal).

## Sections and budget

Validator words (decimals count twice). Target about 6,000 prose plus about 900 references.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 260 | state the answer | — | — |
| Why this matters | 200 | see that ranking many small groups by their own averages wastes accuracy | — | L15, L19 |
| The problem | 420 | define bias, variance and MSE; state the German tank problem | — | L05 |
| Worked example | 950 | compute five estimators by hand, read their sampling distributions, decompose MSE, compare with 1940s records | FIG_01–04 | L01–L04, L06 |
| Intuition | 350 | explain why the maximum carries the information and why shrinking pays when variance dominates | — | — |
| How is the best unbiased estimator built? | 400 | build the MVUE from 2 × mean − 1 by conditioning on the maximum | FIG_05 | L06–L09 |
| Is unbiased the same as consistent? | 350 | separate the two properties; read error rates 1/k and 1/√k | FIG_06 | — |
| Why divide by n − 1, and when not to? | 500 | choose a divisor by MSE; see why n + 1 needs normal tails | FIG_07 | L26, L27 |
| Stein's paradox | 800 | apply James–Stein to 18 averages and recompute both published comparisons | FIG_08, FIG_09 | L10–L22, L25, L29 |
| How much does shrinking gain, and when? | 450 | read the replay and the exact risk curve; know the k ≥ 3 condition | FIG_10, FIG_11 | L11, L17, L23 |
| The math | 600 | the formulas, each tied back to the worked numbers | — | L07, L08, L11, L26 |
| Implementation | 300 | run the tank simulation and the James–Stein rule | — | — |
| Limitations and common mistakes | 400 | avoid seven mistakes | — | L23, L24, L22 |
| Key takeaways | 170 | carry five claims | — | — |
| Try it yourself | 220 | E1, E3 from the article | — | — |
| References | ~900 | — | — | — |

## Figure plan (route gate run per figure)

| Fig | Section | One thing it says | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 01 | Worked example | one capture: the MLE stops at the largest serial; the MVUE adds the average gap | plot | Q4: five data points on a scaled number line with constructed estimates | the largest serial is the MLE; the gap rule adds 59.6 |
| 02 | Worked example | over a million captures the MLE piles up below N and never passes it; the MVUE centres on N | plot | Q4: simulated distributions against an exact pmf | the MLE's wall at 342 |
| 03 | Worked example | MSE = bias² + variance for five estimators; the MLE's MSE is 58% bias | chart | Q1: exact decomposition, simulated checks | bias costs the MLE more than variance does |
| 04 | Worked example | serial-number estimates within 4–39% of the records, intelligence 4.5 to 8.2 times too high | chart | Q1: published numbers (L03) on a log axis | statistics against spies |
| 05 | Best unbiased | conditioning 2 × mean − 1 on the maximum collapses its spread onto m(1 + 1/k) − 1 | plot | Q4: a scatter of 3,000 captures and conditional means from a million | Rao–Blackwell, drawn |
| 06 | Consistent | RMSE against k: 1/k for maximum-based, 1/√k for the mean, flat for one tank | plot | Q4: exact curves on log–log axes with simulated points | unbiased is not consistent |
| 07 | Divisors | MSE against the divisor for three populations; the best is n + 1 only for the normal | plot | Q4: exact curves with simulated points | the best divisor moves with the tails |
| 08 | Stein | rest-of-season against first-45 averages; the James–Stein line (0.212) beside the hindsight slope (0.190) and the identity | plot | Q4: published data (L13) with constructed lines | shrinkage as regression toward the mean |
| 09 | Stein | each player's squared error, average against James–Stein; 16 of 18 improve | chart | Q1: per-player errors from the table | where the 3.5 comes from |
| 10 | Gain | 200,000 replayed seasons: James–Stein wins 96%, the observed 3.5 sits in the upper quarter | plot | Q4: a simulated distribution with the published value marked | 1970 was a good draw, not a fluke |
| 11 | Gain | exact total risk against the spread of the true means: 3 to 18, never above 18 | plot | Q4: exact curve with simulated points and the batters' spread | the gain depends on the spread |
| Cover | — | the MLE's sampling distribution walled at N beside the MVUE's, the truth in tangerine | placed | template cover in the series house layout; no external generator | — |

Source-route check: Efron and Morris's 1977 figures are Scientific American's copyright (ledger F1, F2), and
Figure 8 adds a regression line and the truth they do not show; Simon's table is facts drawn as Figure 4 (F3);
Clark et al.'s Figure 2 has unclear provenance (F4). No figure is Mermaid: none is a graph of nodes and edges.

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| estimand, estimator, estimate | The problem | the quantity, the rule as a random variable, its value (series terms) | the object judged | every inference |
| bias | The problem | E(θ̂) − θ: the systematic part of the error | the property in the title | when errors must cancel across uses |
| variance, standard error | The problem | spread of θ̂ over samples (Part 2's SE) | the random part of the error | every estimate |
| mean squared error (MSE), RMSE | The problem | E(θ̂ − θ)² = bias² + variance; RMSE its root, in θ's units | the yardstick | squared-error loss |
| loss function, risk | The problem | how a miss is scored; risk = expected loss | MSE is one choice | choosing a yardstick |
| German tank problem | The problem | estimate N from k serial numbers drawn from 1..N | the worked case | IDs, serials, counts from labels |
| maximum likelihood estimator (MLE) | Worked example | the N that makes the observed capture most probable; named here, built in general in Part 4 | the biased candidate | default estimator |
| minimum-variance unbiased estimator (MVUE) | Worked example | the unbiased estimator with the smallest variance at every N | the unbiased candidate | when unbiasedness is required |
| sufficient statistic | Best unbiased | a summary that keeps all the information the data carry about θ | why the max is enough | compressing data |
| Rao–Blackwell theorem | Best unbiased | conditioning an estimator on a sufficient statistic never increases its MSE | how the MVUE is built | improving any estimator |
| Lehmann–Scheffé | Best unbiased | named only: unbiased + complete sufficient ⇒ unique MVUE | uniqueness | — |
| consistency | Consistent | error → 0 as the sample grows | a separate property | large-sample work |
| divisor, sum of squares | Divisors | SS/d as an estimate of σ² | the n − 1 question | every variance estimate |
| excess kurtosis κ | Divisors | E(X − μ)⁴/σ⁴ − 3: tail weight relative to the normal | sets the best divisor | heavy-tailed data |
| c₄ | Divisors | E(s)/σ for normal data | s stays biased | quality control, small n |
| shrinkage | Intuition | pulling an estimate toward a target to cut variance at the price of bias | the idea of all three cases | many small groups |
| James–Stein estimator | Stein | shrink each of k ≥ 3 means toward the grand mean by a data-chosen factor | Stein's paradox | ranking many groups |
| admissible, inadmissible | Stein | no other estimator is at least as good everywhere and better somewhere | what Stein disproved | comparing estimators |
| total squared error, efficiency | Stein | sum of squared errors over all k; ratio of two such totals | the published comparison | multi-group forecasts |
| variance-stabilising (arcsine) transform | Stein | √n · arcsin(2y − 1): makes a binomial average's variance nearly 1 | the 1975 version | proportions |
| positive-part rule | Gain | never shrink past the grand mean: max(c, 0) | plain James–Stein can overshoot | small spread |
| empirical Bayes, partial pooling | Limitations | named only: the shrinkage's Bayesian reading; later in this series | handoff | grouped data |

## Handoffs (plain text in the post, no numbers or titles)

- Maximum likelihood as a general recipe and its variance: later in this series.
- The bootstrap's failure on the sample maximum: later in this series.
- Shrinkage as partial pooling in grouped data, and unequal variances: later in this series.
- Bias and variance of prediction error: machine-learning practice, outside this series.
- Part 2, *The Sampling Distribution: The CLT and Where n = 30 Fails*, named by title where the standard error,
  MCSE and the n − 1 divisor are used.
