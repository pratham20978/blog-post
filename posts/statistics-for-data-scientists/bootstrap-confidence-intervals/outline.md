# Outline — bootstrap-confidence-intervals

Series `statistics-for-data-scientists`, Part 7 of 18 (Tests and intervals arc; parent: Part 6). Private build file.

## Brief

- **Title:** The Bootstrap: From Percentile to BCa, and Where It Breaks (58 characters; the plan's title).
- **Answers:** how do I get a standard error or an interval for a statistic that has no formula, which bootstrap
  interval should I trust, and when does the bootstrap fail?
- **Tier:** L4 (plan). Seven things to learn: the plug-in principle and the bootstrap standard error; five interval
  constructions from one set of replicates (percentile, basic, studentized, BCa with z0 and a, plus Fisher's z as
  the normal-theory benchmark); what second-order accuracy promises; their measured coverage against a real
  population; the number of resamples an interval needs; the skewed-mean case Part 6 left open; three failures
  stated as conditions (extremes, infinite variance, dependence). The worked example (15 schools, 10,000
  replicates) needs a page. **Adjacent option:** L3 would drop the skewed-mean section and the resampling-count
  section and keep one failure in full.
- **Difficulty:** advanced. Assumes Part 6's coverage and Part 2's standard error and t statistic; uses the jackknife
  and influence values, introduced here. **Adjacent option:** intermediate would drop the influence-function
  acceleration and the BCa convention comparison.
- **Lab:** G1 · runs anywhere · E1–E5 · access none. Probe 2026-11-01 matches `access.md` (RAM available 7 GiB; the
  lab peaks at 0.46 GB). The series venv (NumPy 2.5.4, SciPy 1.18.1) is reused unchanged; the lab needs neither
  pandas nor statsmodels. R 4.5.2 with boot 1.3.32 ships as the optional `crosscheck.R` (the plan's one R lab file
  for this part); its output, `crosscheck-r.csv`, ships too, so the R comparison runs without R.
- **Corrects:** "The bootstrap is assumption-free."
- **Four-point angle:** reconcile (every interval matched to `scipy.stats.bootstrap` on the same resamples, 2.2e-16,
  and to `boot.ci` on R's own replicates, 3.9e-15; three BCa conventions compared); condition (iid sampling, the
  sample standing in for the population, a smooth statistic; each broken on purpose); measure (coverage of seven
  intervals on the 82-school population and of six on customer spend, with MCSE; the endpoints' Monte Carlo
  error by B); read the output (SciPy's mid-rank z0, R's regression acceleration and normal-scale interpolation,
  R's "basic" as Hall's percentile, `bcanon`'s type 1 quantiles).

## Settled at research and in the lab

- The law data ship from the book's companion package `bootstrap` 2019.6 (BSD 3-clause, notice carried in the CSV).
  The 15 are schools 4, 6, 13, 15, 31, 35, 36, 45, 47, 50, 52, 53, 70, 79, 82 (13 and 66 share values). r = 0.776374,
  rho = 0.759998. The book itself was not read; nothing is quoted from it beyond the package's documentation.
- Percentile and BCa both fall short at n = 15: 91.0% and 92.0% ± 0.2; Fisher's normal-theory z 93.6%; the
  z-scale bootstrap-t 93.8% and the most balanced; the raw bootstrap-t 95.7% only through width (upper limit above
  1 in 23.5%); basic 80.7%. The article says plainly that second-order accuracy did not deliver at this n.
- Spend at n = 30 keeps Part 6's promise: t 66.0%, BCa 73.3%, bootstrap-t 80.3%; samples without a top-1% customer
  (73.6%) are where every interval fails. Part 6's t-interval figure, 65.83% ± 0.11, agrees with this run's 66.0% ±
  0.3.
- The basic interval for a uniform maximum covers exactly 7/8 for every n from 10 up: it reflects at the
  fourth-largest value, and uniform spacings are exchangeable. Derived here, checked by simulation (87.4–87.6% ±
  0.1). Bickel and Freedman's counterexample is cited through Horowitz 2019, who states it with the 1 − 1/e limit.
- Hall 1990 and Athreya 1987 carry the heavy-tail mechanism (a few extreme values decide the bootstrap
  distribution's shape); the measured coverage still rises at n = 1,000, so the article does not claim a limit.
- The n = 3,000 heavy-tail point was dropped: 400 samples left a 2-point MCSE and a non-monotone reading.

## Sections and budget

Validator words (decimals count twice; References add about 1,200). Target about 7,700 prose.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 300 | state the answer | — | — |
| Why this matters | 200 | see seven intervals for one correlation disagree | — | L01, L02 |
| The problem | 450 | define the plug-in principle, the replicate, B and the bootstrap SE; state the conditions and the claim | — | L03–L06 |
| Worked example | 950 | bootstrap the law-school correlation by hand: SE, percentile, basic, studentized, BCa with z0 and a, Fisher z | FIG_01–FIG_04 | L07–L09 |
| Intuition | 300 | picture the bootstrap world and where the analogy breaks | FIG_05 | — |
| How does each interval turn replicates into limits? | 800 | say what each construction assumes; read z0 and a; first vs second order | FIG_06 | L10–L15 |
| Which interval keeps its promise for the law schools? | 650 | measure coverage against a real population; read misses by side | FIG_07 | L16 |
| How many resamples does an interval need? | 350 | choose B from the endpoints' Monte Carlo error | FIG_08 | L17, L18 |
| Does the bootstrap rescue the skewed mean? | 600 | see why no interval recovers a tail the sample lacks | FIG_09 | L19, L20 |
| When does the bootstrap fail? | 1,150 | state three failure conditions and recognise each | FIG_10–FIG_13 | L21–L30 |
| The math | 650 | the formulas, each with the worked numbers | — | L10, L13 |
| Implementation | 550 | write BCa from scratch; read SciPy's and R's conventions | — | L31–L34 |
| Limitations and common mistakes | 450 | avoid eight mistakes | — | L35 |
| Key takeaways | 200 | carry five claims | — | — |
| Try it yourself | 350 | E1 and E3 from the article | — | — |
| References | ~1,200 | — | — | — |

## Figure plan

| # | Section | One thing it communicates | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | the 15 sampled schools inside the 82, with r = 0.776 and rho = 0.760 | plot | Q1: a scatter of real data | The sample and the population it came from |
| 2 | Worked example | the bootstrap distribution of r* beside the true sampling distribution from the 82 | plot | Q1: two computed distributions on one axis | Same shape, same spread, centred on r instead of rho |
| 3 | Worked example | the 15 leave-one-out correlations; school 6 moves r most; a = −0.076 | plot | Q4: one dot per school with its deviation | One school sets the acceleration |
| 4 | Worked example | seven 95% intervals for the same 15 schools | plot | Q4: intervals drawn to scale on one axis | One sample, seven answers |
| 5 | Intuition | the real world and the bootstrap world side by side, with the law numbers on every edge | placed | Q5: six nodes in two parallel rows, no crossings | The bootstrap replaces F by the sample |
| 6 | How each interval works | BCa's map from nominal to adjusted percentile levels for the law values, beside BC and percentile | plot | Q4: a computed curve | z0 shifts, a bends |
| 7 | Law coverage | coverage of the seven intervals, with misses split by side | plot | Q1: simulated rates with MCSE | Only the wide intervals reach 95% |
| 8 | How many resamples | the endpoints' Monte Carlo SD against B, percentile and BCa | plot | Q1: measured SDs on a log axis | BCa's lower limit needs five times the replicates |
| 9 | Skewed mean | coverage at n = 30 and 100 for six intervals, split by whether the sample holds a top-1% customer | plot | Q1: simulated rates | The bootstrap cannot resample what the sample lacks |
| 10 | Failures | the bootstrap distribution of the tank maximum against its true distribution | plot | Q1: exact distributions | 67% of the bootstrap mass sits on 303 |
| 11 | Failures | intervals for N from five serials, with their exact coverage | plot | Q4: intervals to scale with N marked | Every percentile-type interval stops at the largest serial |
| 12 | Failures | three lumpy bootstrap distributions of a heavy-tailed mean, and coverage against n | plot | Q1: computed histograms and rates | A few values decide the shape |
| 13 | Failures | an AR(1) series and one resample; the SE the resample gives | plot | Q1: simulated series and rates | Resampling single points erases the dependence |
| cover | — | the bootstrap's point mass on the maximum against a smooth sampling distribution, reduced to its argument | placed | template cover in the series house layout | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| bootstrap, plug-in principle, empirical distribution F̂ | The problem | estimate a sampling distribution by sampling from F̂ | gives an SE and an interval with no formula | any statistic of iid data |
| bootstrap sample, replicate θ̂*, B | The problem | a resample of n with replacement; the statistic on it; how many | the Monte Carlo approximation | every bootstrap |
| bootstrap standard error | The problem | SD of the replicates | the simplest output | SE of any statistic |
| percentile interval | Worked example | the 2.5% and 97.5% points of the replicates | transformation-invariant default | smooth, roughly unbiased statistics |
| basic interval | Worked example | 2θ̂ minus the percentiles, reflected | inverts θ̂* − θ̂ as a pivot (Hall's "percentile") | rarely; wrong way for skew |
| studentized (bootstrap-t) interval | Worked example | quantiles of (θ̂* − θ̂)/SE* | estimated pivot, second-order | when a stable SE formula exists |
| bias correction z0, acceleration a, BCa | Worked example | share of replicates below θ̂, mapped to a z; rate at which the SE changes with θ | BCa's two corrections | the default for smooth statistics |
| jackknife, leave-one-out estimate, influence value | Worked example | θ̂ with one observation removed; each point's pull on θ̂ | estimates a | any BCa |
| first- and second-order accuracy | How each works | one-sided coverage error O(n^-1/2) vs O(n^-1) | why BCa and bootstrap-t are preferred | choosing an interval |
| Monte Carlo error of an endpoint | How many resamples | an endpoint's SD over reruns at fixed data | sets B | before reporting a limit |
| point mass at the maximum | Failures | P*(M* = M) = 1 − (1 − 1/n)^n | why the bootstrap fails for extremes | max, min, endpoints |
| infinite variance, tail index | Failures | Pareto with α = 1.5 | the bootstrap of the mean needs finite variance | heavy-tailed data |
| autocorrelation, AR(1) | Failures | correlation between neighbours in time | independent resampling erases it | time series, clustered data |
| m-out-of-n bootstrap, block bootstrap | Failures | resample m ≪ n; resample runs of neighbours | the standard repairs | extremes; dependence |
