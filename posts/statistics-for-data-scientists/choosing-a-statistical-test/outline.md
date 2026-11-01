# Outline — choosing-a-statistical-test

Series `statistics-for-data-scientists`, Part 8 of 18 (Choosing a method arc; parent: Part 5). Private build file.

## Brief

- **Title:** Which Statistical Test? The Design Decides, Not the Data (56 characters). The plan's title, *Choosing a
  Statistical Test: The Design Decides, Not the Data*, is 61 characters, over the 60 the validator allows; the
  question form keeps "statistical test" near the front and matches the first search intent.
- **Answers:** which test answers my question, given how the data were collected, and what happens to its error rate
  when its conditions fail?
- **Tier:** L3 (plan). Six things to learn: the design fixes the test (paired against unpaired on one dataset);
  Student's against Welch's test, measured exactly; why pre-testing assumptions fails, measured as a procedure; how
  a 2 × 2 table's design decides between Fisher's, the chi-squared and the unconditional tests; one-way ANOVA's F as
  a ratio of two variance estimates, and Welch's ANOVA; the library defaults that pick a test for you. The worked
  example (ten patients, two drugs) fits on one screen. **Adjacent option:** L4 would add the rank-based branch of
  the pre-testing habit in full and a cross-sectional 2 × 2 design; both belong to Part 10 and DS-2.
- **Difficulty:** advanced. Assumes Part 5's α, power and type I error, and Part 2's t statistic. **Adjacent
  option:** intermediate would drop the exact quadrature and the unconditional-test construction.
- **Lab:** G1 · runs anywhere · E1–E4 · access none. Probe 2026-11-01 matches `access.md` (RAM available 5–6 GiB; the
  lab peaks at 0.21 GB). The series venv (NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0) is reused
  unchanged. R 4.5.2 is the author's private check, recorded under `author_crosscheck` in `captures.json`; no R
  file ships (the plan names R lab files for Parts 7, 13, 15, 16 and 17 only).
- **Corrects:** "Check normality and equal variances first, then choose the test."
- **Four-point angle:** reconcile (every test by hand, matched to SciPy and statsmodels to 1e-13 or better, and to R
  4.5.2; SciPy's `barnard_exact` found to drop exactly tied tables); condition (normal data with unequal variances,
  unequal sizes, a pre-test on the same data, a margin the design did not fix; each broken on purpose); measure
  (Student's and Welch's type I error and power exactly, by quadrature; the two-stage procedures by simulation
  with MCSE; every 2 × 2 test's exact size over all 483 tables; F and W by simulation); read the output (each
  library's default test, and which one R and SciPy run when you name none).

## Settled at research and in the lab

- The `sleep` premise holds: paired p = 0.002833 (t 4.0621, 9 df), Student unpaired 0.079187, Welch 0.079394 (17.776
  df). The drugs' correlation across patients is 0.795, so Var(d) = 3.2006 + 4.0090 − 5.6967 = 1.5129. A
  parallel-group trial would need about 48 patients per arm for the same standard error (from these sample
  variances, so labelled an estimate).
- Student's test at n = 10 against 40: exact type I error 18.25% at SD ratio 2 and 29.37% at 4 when the group of 10
  has the larger SD; 0.52% and 0.07% when it has the smaller. Welch's stays between 4.97% and 5.15% everywhere. At
  25 and 25, Student's error is at most 5.44%.
- Welch's price: with equal SDs at 10 against 40, Student's 80.0% power is Welch's 75.6% (largest gap 4.58 points);
  at 25 and 25 the gap is 0.08 points. The article states the cost, not "no cost".
- Pre-testing at 10 against 40: Levene decides 9.74% at SD ratio 1.5 and 9.13% at 2, against Welch's 5.07% and
  5.06%; Levene detects a ratio of 1.5 in 27.9% of samples. Student's conditional error when Levene accepts is
  21.19% at ratio 2, above its unconditional 18.25%; Welch's when Levene rejects at ratio 1 is 9.77%. Rochon et al.
  found the overall Shapiro–Wilk procedure acceptable with equal sizes, so the article puts the damage where it is:
  unequal sizes, conditional error rates, and never better than always using Welch.
- 2 × 2: the tea design fixes both margins (Yates 1984 §8); 1/70 and 17/70 are exact. On the malocclusion table the
  eight tests give p from 0.1118 (mid-p) to 0.2871 (doubled Fisher); its smallest expected count is 2.381. Exact
  sizes at 20 and 22: Fisher 3.61%, Yates and doubled Fisher 2.19%, Pearson 4.94%, mid-p 5.14%, Boschloo 4.63%.
  At 10 and 40 Pearson reaches 9.11% at π = 0.028. Boschloo's region contains Fisher's plus 10 tables, so it is at
  least as powerful at every alternative; single-alternative power depends on direction and is left to the lab.
  The containment holds at 20 and 22 only: SciPy's two-sided Boschloo doubles the smaller one-sided p, so it is
  guaranteed to contain the doubled-tail Fisher test, and at 10 and 40 Irwin's-rule Fisher rejects 4 tables it does
  not (found when Figure 9 showed Boschloo's size below Fisher's at small π).
- SciPy 1.18.1's `barnard_exact` differs from the lab on 71 of 481 tables, every one tied exactly with another
  table's abs(Z); worst, (15 of 20, 12 of 22): 0.1791 against 0.2172 for its mirror image. Decisions at 5% agree.
- PlantGrowth: F = 1.8832/0.3886 = 4.846 (p 0.0159); W = 5.181 on 2 and 17.13 df (p 0.0174), R to the digit.
  Simulated at k = 3: negative pairing F 16.13%, W 5.25%; positive pairing F 2.04%, W 4.90%; equal sizes with SDs
  1, 2, 3, F 6.14%, W 4.98%.

## Sections and budget

Validator words (decimals count twice; References add about 1,100). Target about 7,200 in all.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 280 | state the answer | — | — |
| Why this matters | 180 | see one dataset give p = 0.003 and p = 0.08 | — | L01 |
| The problem | 380 | state what a test's guarantee needs; name the design's role; state the claim | — | L05, L08 |
| Worked example | 700 | analyse the sleep data paired and unpaired by hand; read Var(d) | FIG_01, FIG_02 | L01–L04 |
| Intuition | 250 | map a design to a test | FIG_03 | L18 |
| When does Student's t-test keep its 5%? | 650 | predict Student's error from the pairing of size and variance; price Welch | FIG_04, FIG_05 | L08–L11 |
| Does checking the assumptions first help? | 550 | measure a two-stage procedure; explain conditional error | FIG_06 | L12–L16, L36 |
| Which test fits a 2 × 2 table? | 850 | match the test to the margins the design fixed; compare exact sizes | FIG_07–FIG_09 | L17–L26 |
| What does ANOVA's F compare? | 450 | compute F and W by hand; predict F's error under pairing | FIG_10, FIG_11 | L30–L32 |
| The math | 550 | the formulas, each with the worked numbers | — | L05, L30 |
| Implementation | 450 | run each test; read each library's default | — | L06, L07, L27–L29 |
| Limitations and common mistakes | 380 | avoid seven mistakes | — | L33, L34 |
| Key takeaways | 180 | carry five claims | — | — |
| Try it yourself | 280 | E1 and E3 from the article | — | — |
| References | ~1,100 | — | — | — |

## Figure plan

| # | Section | One thing it communicates | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | ten patients, each a line from drug 1 to drug 2; the lines are parallel-ish, and the differences are tight | plot | Q1: real paired data | The between-patient spread dwarfs the drug effect |
| 2 | Worked example | one mean difference, two standard errors: t 1.86 on 18 df against t 4.06 on 9 df, with their tail areas | plot | Q4: two computed t densities with observed values | Pairing removes the patients from the error |
| 3 | Intuition | how the design picks the test: paired, two groups, k groups, a 2 × 2 table by its fixed margins | mermaid | Q2: 12 nodes, three parallel branches | Ask how the data were collected, not how they look |
| 4 | Student vs Welch | exact type I error of both tests against the SD ratio at 10 vs 40 and 25 vs 25, with simulated checks | plot | Q1: computed curves with measured points | Student's error follows the pairing of size and variance |
| 5 | Student vs Welch | power with equal SDs, both tests, both designs | plot | Q4: computed curves | Welch's price is small when the design is balanced |
| 6 | Pre-testing | overall error of four procedures against the SD ratio, and Levene's rejection rate | plot | Q1: simulated rates with MCSE | Letting Levene choose lands between Student and Welch |
| 7 | 2 × 2 | the tea design's hypergeometric distribution, 1, 16, 36, 16, 1 of 70 | plot | Q4: an exact distribution | Both margins fixed by design: the test is exact |
| 8 | 2 × 2 | the malocclusion table and eight p-values on one axis | plot | Q4: values to scale | One table, p from 0.11 to 0.29 |
| 9 | 2 × 2 | exact size against π for five tests, in the 20 vs 22 and 10 vs 40 designs | plot | Q1: exact sums over all tables | Conditioning on a margin the design did not fix costs size |
| 10 | ANOVA | PlantGrowth's 30 weights by group, the means, and the two mean squares whose ratio is F | plot | Q1: real data | F compares two estimates of the same variance |
| 11 | ANOVA | type I error of F, W and F* in four designs | plot | Q1: simulated rates with MCSE | F's error follows the pairing; W's stays near 5% |
| cover | — | Student's and Welch's error curves at 10 vs 40, reduced to the argument | placed | template cover in the series house layout | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| design, paired (within-subject) design, independent groups | The problem | how the data were collected: the same units measured twice, or separate units per condition | fixes the null distribution a test must use | before choosing any test |
| paired t-test | Worked example | the one-sample t-test on the within-unit differences | removes between-unit variation from the error | matched or repeated measurements |
| pooled variance, Student's two-sample t-test | The problem | one variance estimate from both groups, weighted by n − 1 | Student's test assumes equal variances | the classical default |
| Welch's t-test, Welch–Satterthwaite degrees of freedom | The problem | separate variances, df estimated from them | keeps its error rate when variances differ | the default for two independent groups |
| type I error rate, exact size, liberal, conservative | When does Student's… | the probability a 5% test rejects a true null, computed exactly; above or below 5% | the guarantee being measured | every test |
| negative and positive pairing | When does Student's… | the larger variance in the smaller or the larger group | predicts the direction of Student's (and F's) error | unequal sizes |
| pre-test, Levene's test (Brown–Forsythe), Shapiro–Wilk test | Does checking… | tests of equal variances and of normality, run on the same data first | the habit under test | never as a gate |
| two-stage procedure, conditional error rate | Does checking… | the whole pipeline as one test; the error rate given the pre-test's verdict | what the reader actually runs | reporting a pre-tested p |
| 2 × 2 table, margins, fixed margin | Which test fits… | a table of counts; its row and column totals; a total the design set in advance | decides the sampling distribution | any binary outcome by group |
| hypergeometric distribution, Fisher's exact test, Irwin's rule | Which test fits… | the distribution of a cell given both margins; the test built on it; its two-sided rule | exact when both margins are fixed | small counts |
| expected count, Pearson's chi-squared, Yates's correction, 'N − 1' chi-squared | Which test fits… | counts implied by independence; the large-sample test; its continuity adjustment and variant | the asymptotic tests and their condition | large tables |
| mid-p, conditional and unconditional tests, nuisance parameter, Boschloo's and Barnard's tests | Which test fits… | half-counting the observed table; tests that do or do not condition on a margin; the unknown common π; maximising over it | the alternatives that keep size closer to α | one margin fixed |
| one-way ANOVA, between- and within-group mean squares, F ratio | What does ANOVA's F compare? | two estimates of σ² and their ratio | the k-group test | three or more groups |
| Welch's ANOVA (W), Brown–Forsythe F* | What does ANOVA's F compare? | weighted between-group comparison without pooling | keeps error near 5% under unequal variances | the default for k groups |
