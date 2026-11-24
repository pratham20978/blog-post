# Outline — permutation-and-rank-tests

Series `statistics-for-data-scientists`, Part 10 of 18 (Choosing a method arc; parent: Part 8). Private build file.

## Brief

- **Title:** Permutation and Rank Tests: What They Actually Test (51 characters). The plan's title, *Permutation and
  Rank Tests: What Nonparametric Methods Actually Test*, is 67 characters, over the 60 the validator allows; this one
  keeps both keywords at the front and the claim.
- **Answers:** how can a test be exact without assuming a distribution, and what hypothesis does each rank test test?
- **Tier:** L3 (plan). Six things to learn: the randomisation test by enumeration and what makes it exact
  (exchangeability, randomisation); exact against Monte Carlo p-values and the +1; why a permutation test of means is
  not exact for means, and studentising; what Mann–Whitney tests (P(X > Y), identical distributions), with
  Brunner–Munzel beside it; the Hodges–Lehmann estimate and its exact interval; what ranks cost (ARE), with rank
  correlations and Kruskal–Wallis named. The worked example (15 pairs, one enumeration, four p-values) fits on one
  screen. **Adjacent option:** L4 would add the studentised median test and the k-sample studentised permutation test
  (Chung and Romano) in full; neither is in the plan.
- **Difficulty:** advanced. Assumes Part 8's two-sample tests and their measured error rates, Part 5's p-values. **Adjacent
  option:** intermediate would drop the Monte Carlo p-value theory and the efficiency integral.
- **Lab:** G1 · runs anywhere · E1–E4 · access none. Probe 2026-11-23 matches `access.md` except Python 3.12.16 (was
  3.12.15) and the kernel; RAM available 5 GiB; the lab peaks at 0.30 GB. The series venv is reused unchanged; the lab
  needs only NumPy 2.5.4 and SciPy 1.18.1. R 4.5.2 is the private check (`author_crosscheck` in `captures.json`); no
  R file ships.
- **Corrects:** "Mann–Whitney compares medians, so use it when the data are not normal."
- **Four-point angle:** reconcile (Fisher's Table 4 to the count; t, signed-rank, sign test, Hodges–Lehmann and its
  interval to SciPy and R; the permutation engine to SciPy's exact enumeration; Spearman's exact p by dynamic
  programming against SciPy's t approximation and R's Edgeworth series); condition (exchangeability: randomisation
  for Darwin's pairs, identical distributions for two samples, broken on purpose by unequal variances and shapes);
  measure (sizes of four permutation tests and three rank tests by simulation with MCSE, power under eight shapes, the
  exact distribution of SciPy's Monte Carlo p); read the output (SciPy's and R's defaults, statistic conventions and
  exact/approximate switches).

## Settled at research and in the lab

- Darwin's pairs: the 1876 scans settle two fractions the Darwin Online transcription misreads (18 5/8, 21 5/8);
  totals 302.875 and 263.625 inches reproduce the printed 302.88 and 263.63. Differences in eighths: 49, −67, 8, 16,
  6, 23, 28, 41, 14, 29, 56, 24, 75, 60, −48; sum 314.
- Paired t 2.1480 (p 0.049703), 95% CI 0.0039 to 5.2294 in. Enumeration reproduces Fisher's Table 4 row by row:
  835 above, 28 at, 863 at least 314; two-sided p 1,726/32,768 = 0.052673. Signed-rank V+ 96 (ranks 14 and 10
  negative), p 0.041260; sign test 242/32,768 = 0.007385. Galton's re-paired columns: t 5.1714, p 1.42e-4.
  Hodges–Lehmann 3.125 in, exact interval 0.5 to 5.1875 (26th smallest and largest of 120 Walsh averages), confidence
  95.21%. R and SciPy agree to the capture's six digits.
- SciPy's default `permutation_test` on Darwin (9,999 random flips): p over reruns has 95% range 0.0466 to 0.0592;
  P(p ≤ 0.05) = 19.4% exactly (binomial); 1,000 actual runs 21.3% ± 1.3. `n_resamples=np.inf` gives 0.052673.
- The +1: m = 999 and Bonferroni over 1,000 true nulls: family-wise error 63.2% with b/m, 0.0% with (b + 1)/(m + 1);
  Phipson–Smyth's 30,000 genes at m = 1,000: 29.97 zero p-values on average.
- Two-sample permutation tests at 10 and 40 (R 50,000, 999 relabellings each): raw difference 18.31% at SD ratio 2,
  29.10% at 4, 0.06% at 1/4 (Student's on the same data 18.34%, 29.20%, 0.06%); studentised 5.73%, 5.81%, 3.87%;
  Welch's t 5.02%, 5.11%, 5.01%. At 25 and 25 raw and studentised coincide (a monotone function of each other) and
  hold 5.06% to 5.57%. The engine matches SciPy's exact enumeration on 4 and 6 values; SciPy's default two-sided p
  doubles the smaller tail (0.676 against 0.738 for |T|).
- Mann–Whitney: S1 (N(0, 1) against Exp(1) − ln 2; equal medians and SDs) P(X > Y) = 0.4431; MW rejects 6.1%, 10.2%,
  16.7%, 28.8%, 50.2%, 79.7% at 10 to 400 per group; S2 (c = 0.8758, medians 0 and −0.18, P(X > Y) = ½) 4.7% to 5.7%;
  S3 (normal, 10 and 40, equal centres) MW 0.71% at 1/4, 9.93% at 2, 14.81% at 4; Brunner–Munzel 4.94% to 5.67%.
  Two-sample HL target in S1: median of X − Y = −0.1827 (simulated −0.1858 ± 0.0048 at 400 per group).
- Efficiency at n = 20 per group, shift 0.9091 SD (Student's 80% for normal data), R 100,000: normal Welch 79.7% vs MW
  77.6%; parabolic (ARE 0.864) 79.9 vs 74.1; uniform (ARE 1) 79.8 vs 73.5; logistic 79.8 vs 82.0; t5 80.7 vs 86.1;
  Laplace 79.8 vs 88.0; contaminated normal 80.5 vs 89.2; t3 84.0 vs 95.0.
- Law school: r 0.7764, ρ 0.7964 (Σd² 114), τ 0.6381 (86 − 19 of 105). Kendall exact 0.000532 (SciPy = R); Spearman
  exact 0.000638 (833,742,534 of 15! orderings, by dynamic programming) against SciPy's t approximation 0.000380 and
  R's AS 89 Edgeworth 0.000608; Monte Carlo (99,999) 0.00078, 0.00067, Pearson 0.00134 (t-test 0.000665).

## Sections and budget

Validator words (decimals count twice; References add about 1,100). Target about 7,300 in all, under the 7,500 cap.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 260 | state the answer | — | — |
| Why this matters | 160 | see the two habits this corrects | — | — |
| The problem | 330 | name the null a permutation or rank test is exact for; state the claim | — | L11, L20 |
| Worked example | 700 | enumerate Darwin's sign assignments; read four p-values | FIG_01, FIG_02 | L01–L05, L09 |
| Intuition | 300 | say what each test keeps of the data; see a reference set broken | FIG_03 | L06–L09 |
| When is a permutation test exact? | 520 | state exchangeability; use (b + 1)/(m + 1); size a Monte Carlo run | FIG_04 | L07, L12–L15, L36 |
| Does a permutation test compare means? | 480 | predict when a permutation test of means fails; studentise | FIG_05 | L16–L19 |
| What does the Mann–Whitney test test? | 680 | read U as P(X > Y); pick MW, Brunner–Munzel or a median method by hypothesis | FIG_06, FIG_07 | L20–L25 |
| How large is the effect? | 380 | compute the Hodges–Lehmann estimate and interval; know its target | FIG_08 | L26–L27 |
| What do ranks cost? | 400 | read ARE; expect the power trade by tail weight | FIG_09 | L29, L30 |
| Rank correlations | 330 | compute ρ and τ; choose an exact p | FIG_10 | L31–L34 |
| The math | 480 | the formulas, each with the worked numbers | — | L12, L21, L30 |
| Implementation | 420 | run each test; read each library's default | — | L28, L34–L39 |
| Limitations and common mistakes | 330 | avoid seven mistakes | — | L22, L24 |
| Key takeaways | 200 | carry five claims | — | — |
| Try it yourself | 230 | E1 and E3 from the article | — | — |
| References | ~1,100 | — | — | — |

## Figure plan

| # | Section | One thing it communicates | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | Darwin's 15 pairs, crossed against self-fertilised, by pot, and their differences: 13 positive, 2 large negatives | plot | Q1: real paired data | Thirteen of 15 crossed plants are taller; the two exceptions are large |
| 2 | Worked example | all 32,768 sign-assignment totals, the observed 314 and both tails (863 each) | plot | Q4: an exact distribution | The randomisation test's reference set |
| 3 | Intuition | what each test keeps: values (t, permutation), signed ranks, signs, with their p-values | plot | Q4: values to scale | Four tests, four questions, four p-values |
| 4 | When exact? | (a) SciPy's default p over reruns, exact binomial, against 0.05 and the exact p; (b) family-wise error of b/m and (b + 1)/(m + 1) against the number of tests | plot | Q1: computed distributions | A Monte Carlo p is a random variable; add one |
| 5 | Means? | size of the raw and studentised permutation tests, Student's and Welch's, against the SD ratio, 10/40 and 25/25 | plot | Q1: simulated rates with MCSE | Exact for identical distributions, not for equal means |
| 6 | Mann–Whitney | the S1 and S2 densities with medians, means and P(X > Y) | plot | Q4: densities | Equal medians, P(X > Y) = 0.443; different medians, P(X > Y) = ½ |
| 7 | Mann–Whitney | rejection rates: S1 and S2 against n, S3 against the SD ratio | plot | Q1: simulated rates with MCSE | Mann–Whitney follows P(X > Y), and only for identical shapes |
| 8 | Hodges–Lehmann | Darwin's 120 Walsh averages sorted; the median and the 26th from each end | plot | Q4: values to scale | The estimate and interval are order statistics |
| 9 | Efficiency | ARE and the power of Welch and Mann–Whitney at n = 20 for eight shapes | plot | Q1: computed and simulated values | Ranks cost little in the body and pay in the tails |
| 10 | Rank correlation | law-school values and their ranks, with r, ρ, τ and their p-values | plot | Q1: real data | Three correlations of one sample |
| cover | — | the 32,768 totals with Darwin's tail, reduced to the argument | placed | template cover in the series house layout | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| permutation test, reference set | The problem | a test whose null distribution is the statistic over relabellings of the data | needs no distributional model | a null under which labels are interchangeable |
| randomisation test | The problem | the same computation justified by the random assignment actually made | exact by design | randomised experiments |
| exchangeability | The problem | the joint distribution unchanged by the relabellings | the condition that makes the test exact | check before trusting exactness |
| rank test, rank, midrank | The problem | a test computed from ranks; the average rank for ties | a null distribution free of the data's values | skew, outliers, ordinal data |
| sign-flip test, sign test, Wilcoxon signed-rank test | Worked example | one-sample tests on signs and magnitudes, signs only, signed ranks | Darwin's pairs | paired designs |
| Monte Carlo p-value, the +1 | When exact? | p from m random relabellings, (b + 1)/(m + 1) | exact where b/m is not | too many relabellings to enumerate |
| studentised statistic | Means? | a statistic divided by its estimated standard error (Welch's t) | asymptotically valid for means without identical distributions | unequal variances or sizes |
| Mann–Whitney U, Wilcoxon rank-sum, P(X > Y), stochastic ordering | Mann–Whitney | pairs won by X; its estimand; one variable tending to be larger | what the test responds to | two independent groups |
| Brunner–Munzel test | Mann–Whitney | a studentised rank test of P(X > Y) + ½P(X = Y) = ½ | valid without identical shapes | the hypothesis is P(X > Y) |
| Hodges–Lehmann estimate, Walsh averages, pseudomedian | How large? | the median of pairwise averages or differences; its target | the estimate that matches the rank test | report a size with a rank test |
| asymptotic relative efficiency (ARE) | What do ranks cost? | the large-sample ratio of sample sizes for equal power | the price of ranks | choosing between t and rank tests |
| Spearman's ρ, Kendall's τ, concordant pairs | Rank correlations | Pearson on ranks; concordant minus discordant over pairs | monotone association | ordinal or skewed pairs |
| Kruskal–Wallis test | Rank correlations | the k-group rank test | the rank analogue of ANOVA | three or more groups |
