# Outline — hypothesis-testing-p-values-power

Series `statistics-for-data-scientists`, Part 5 of 18 (Tests and intervals arc; parent: Part 2). Private build file.

## Brief

- **Title:** p-Values and Power: How Wrong Can a Significant Result Be? (58 characters; the plan's title runs to 70).
- **Answers:** what does a p-value measure, what does a test promise, and how wrong can a "significant"
  estimate be?
- **Tier:** L4 (plan). Six things to learn: the p-value as a random variable (uniform under the null, and what
  breaks that); Fisher's evidence reading against Neyman–Pearson's decision rule; power for the two-sample
  t-test and why "observed power" adds nothing; type S and type M errors; the false positive risk as a
  function of prior and power; equivalence testing. The worked example (one published estimate, one standard
  error, one plausible effect) fits a screen and is worked by hand. **Adjacent option:** L3 would drop the
  replication data and the optional-stopping simulation, and with them the plan's two links to the
  literature.
- **Difficulty:** advanced. Assumes Part 2's sampling distribution, standard error and t statistic, and
  names Part 4 for the three test statistics. **Adjacent option:** intermediate would drop the noncentral t,
  the closed forms and the likelihood ratio behind the "p-equals" risk.
- **Lab:** G1 · runs anywhere · E1–E5 · access none. Probe 2026-10-29 matches `access.md` (RAM available
  7 GiB; the lab peaks at 0.48 GB). The series venv (NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0,
  pandas 3.1.0) is reused unchanged. R 4.5.2, base only, is the private check (Gelman and Carlin's own
  `retrodesign()`, `power.t.test`).
- **Corrects:** "p = 0.03 means a 3% chance the result is a fluke."
- **Four-point angle:** reconcile (power by an integral against SciPy's noncentral t, statsmodels and R; TOST
  against statsmodels; every published number recomputed); condition (uniformity needs a fixed design, and
  peeking breaks it; significance as a filter breaks unbiasedness); measure (p-value distributions, power,
  type S and M, the false positive risk, TOST size and optional stopping, each with MCSE); read the output
  (statsmodels' `ttost_ind` triple and what each of its numbers is).

## Settled at research

- Gelman and Carlin's published values reproduce from the closed form to their printed precision except their
  simulated exaggeration ratios: 9.7 for Durante et al. against 9.537 (R's own function reaches 9.65 or more
  in 3.2% of seeds). Kanazawa's 77, 25 and 8 are rounded from 76.7, 25.6 and 7.75.
- The worked example is Durante et al. as Gelman and Carlin report it (17 points, p = .035, SE 8.1, plausible
  effect 2). No data are shipped for it: two published numbers are used.
- The replication section uses the Reproducibility Project's CC0 file (sha256 4d87a263…), 100 coded rows.
  The paper's descriptive means could not be read; only its abstract is quoted, and the team's significance
  codes reproduce the abstract's 97 and 36.
- "False positive risk" (Colquhoun 2017), not "false discovery rate", because a later part owns FDR in the
  Benjamini–Hochberg sense.
- Sellke et al.'s calibration is not quoted (its class of alternatives could not be checked).
- One running design for power, the false positive risk and TOST: 16 per group, a true difference of 1 SD
  (Colquhoun's), power 78.14%.

## Sections and budget

Validator words (decimals count twice; References add about 1,400). Target about 7,300 prose.

| Section | Words | Reader can now | Figures | Keys |
|---|---|---|---|---|
| Insights, level line, jump list, lab notice | 260 | state the answer | — | — |
| Why this matters | 170 | see a published p = .035 that a design analysis turns into a coin toss on sign | — | L13, L14 |
| The problem | 350 | define the p-value, α, power, Fisher's and Neyman–Pearson's readings; state the claim tested | — | L01–L05 |
| Worked example | 850 | compute z, p, the significance bar, power, type S and exaggeration for Durante et al. by hand | FIG_01 | L13, L14, L16 |
| Intuition | 250 | picture significance as a net that measures its own mesh; know where that breaks | — | — |
| What is the distribution of a p-value? | 850 | describe p under the null and under alternatives; see 25 repeats; see what peeking does | FIG_02–FIG_04 | L06–L09, L30–L32 |
| How is power computed? | 650 | derive power for the two-sample t, check it four ways, size a study; distrust observed power | FIG_05–FIG_07 | L10, L11 |
| How wrong can a significant estimate be? | 650 | read type S and M against power; reproduce Gelman and Carlin; know the critique | FIG_08 | L15–L20 |
| Why do replications find smaller effects? | 550 | read the Reproducibility Project's 97 pairs against the significance filter | FIG_09 | L21–L24 |
| What share of significant results are false? | 600 | compute the false positive risk both ways; know what it assumes and who disputes it | FIG_10, FIG_11 | L25–L29 |
| How do you show there is no effect? | 600 | run TOST, size it, and read the failed replications for equivalence | FIG_12, FIG_13 | L33–L36 |
| The math | 450 | the formulas, each with the worked numbers | — | L16 |
| Implementation | 300 | retrodesign and TOST in a screen of Python, matched to R and statsmodels | — | — |
| Limitations and common mistakes | 380 | avoid seven mistakes | — | — |
| Key takeaways | 170 | carry five claims | — | — |
| Try it yourself | 200 | E1 and E3 from the article | — | — |
| References | ~1,400 | — | — | — |

## Figure plan

| # | Section | One thing it communicates | Route | Why (the clause that settled it) | Draft caption |
|---|---|---|---|---|---|
| 1 | Worked example | under the plausible 2 points, significance needs ±15.9: 4.34% land right, 1.37% wrong, and every one overstates by 7.9× or more | plot | Q4: a distribution cut by a threshold, computed from two published numbers | A significant estimate from this design is at least 7.9 times the plausible effect, and one in four points the wrong way |
| 2 | Distribution of p | p is uniform under the null and piles up near 0 as λ grows; at Durante's λ it is almost uniform | plot | Q1: simulated histograms against exact bin probabilities, five small multiples | The same test's p-value under five true effects |
| 3 | Distribution of p | 25 repeats of one 78%-power experiment: estimates and intervals with their p, from 0.00007 to 0.33 | plot | Q1: 25 simulated experiments, intervals on a common axis | Nothing changed between rows but the sample |
| 4 | Distribution of p | the error rate of a 5% test repeated after every observation, exact and simulated, up to 1,000 looks | plot | Q1: an exact curve on a log axis with simulated points | Each look is a new chance to be wrong |
| 5 | Power | null and alternative t densities for 16 per group: α in the tails, power under the alternative, the t of p = .03 | plot | Q4: two densities and areas cut by thresholds | Fisher reads the tail beyond the observed t; Neyman and Pearson read the areas fixed before the data |
| 6 | Power | power against n per group for d = 0.2, 0.5, 0.8, 1: exact, normal approximation, simulated points | plot | Q1: computed curves with simulated checks, log x axis | 64 per group for d = 0.5 |
| 7 | Power | observed power as a function of p alone: 0.50 at p = .05 | plot | Q1: one computed curve, two designs | Observed power is the p-value on another scale |
| 8 | Type S and M | exaggeration ratio and type S rate against power, with both published studies and Gelman and Carlin's printed values | plot | Q1: closed-form curves on log axes, published and simulated points | Below 50% power significant estimates exaggerate; below 10% they also flip |
| 9 | Replication | original against replication r for 97 pairs, coloured by replication significance, with the means by original p | plot | Q1: a scatter of real data with summary marks | Replications kept half the original effect, and less when the original p was above .001 |
| 10 | False positive risk | share of p ≤ .05 results that are false against the prior, for power 0.2, 0.5, 0.8 | plot | Q1: computed curves with two marked points | At prior 0.1 and 80% power, 36% |
| 11 | False positive risk | p-equals against p-less-than risk as the observed p falls, priors 0.5 and 0.1 | plot | Q1: computed curves on a log axis with marked points | p = .03 is a 17% risk at even odds and 64% at 1 in 10 |
| 12 | Equivalence | n per group for 80% power to show equivalence within ±Δ, against n to detect Δ; TOST power at n = 16 | plot | Q1: computed curves | Showing absence costs more than showing presence |
| 13 | Equivalence | the 63 non-significant replications' 90% intervals against ±0.1 and ±0.2 | plot | Q1: 63 intervals from real data on one axis | Only 2 of 63 failed replications show the effect is under 0.1 |
| cover | — | the worked example's distribution cut by its significance bar | placed | template cover, the series house layout | — |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| null hypothesis, test statistic | The problem | the model a test assumes; the number it computes from the data | the p-value is defined under the null | every test |
| p-value | The problem | the probability, computed with the null true, of a statistic at least as extreme as the one observed | the quantity this part is about | reading any test |
| significance level α, statistically significant | The problem | the rejection threshold fixed in advance; a p at or below it | Neyman–Pearson's error rate | designing and reporting |
| type I error, type II error, power | The problem | rejecting a true null; missing a real effect; 1 − β | the two errors a decision rule controls | planning a study |
| Fisher's and Neyman–Pearson's readings | The problem | graded evidence against the null; a decision with fixed error rates | they answer different questions | reporting p against reporting a decision |
| signal-to-noise λ | Worked example | true effect over standard error | the only thing p's distribution depends on | design analysis |
| type S error, type M error, exaggeration ratio | Worked example | a significant estimate's wrong sign; its expected magnitude over the true one | what significance does to estimates | interpreting a significant result |
| design analysis (retrodesign) | Worked example | power, type S and M computed from an externally plausible effect | Gelman and Carlin's method | before and after a study |
| uniform distribution of p | Distribution of p | under a true null and a continuous statistic, P(p ≤ a) = a | the test's whole promise | checking a test's calibration |
| optional stopping | Distribution of p | testing repeatedly as data arrive and stopping at significance | breaks uniformity | any monitored experiment |
| noncentral t, effect size d | Power | the t statistic's distribution when the null is false; the difference in SD units | exact power | sample size |
| observed (post hoc) power | Power | power at the estimated effect | a function of p, adds nothing | never for interpretation |
| critical effect size | Type S and M | the smallest estimate that reaches significance | every significant estimate exceeds it | reading significant results |
| significance filter, winner's curse | Replication | selecting estimates because they are significant | why published effects shrink | using published effects to plan |
| prior probability, false positive risk | False positive risk | share of tested effects that are real; share of significant results that are false | what a fluke probability would be | reading one significant result |
| p-less-than, p-equals, likelihood ratio | False positive risk | conditioning on p ≤ α against on the observed p; the density ratio of the data under the two hypotheses | the two ways to compute the risk | single results |
| equivalence test, TOST, equivalence bounds | Showing no effect | two one-sided tests against the smallest effect of interest | the honest "no meaningful effect" | null results |
| Monte Carlo standard error (MCSE) | (Part 2) | the standard error of a simulated rate | every simulated number | always |
