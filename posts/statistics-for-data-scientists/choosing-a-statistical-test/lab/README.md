# Lab — Which Statistical Test? The Design Decides, Not the Data

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-11-01 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `choosing.py` f97524b7029d, root seed 20261101. The notebook was built and executed with the same pins. The author also checked the lab privately against base R 4.5.2: `t.test` on the sleep data (paired p = 0.002833, Welch 0.07939 on 17.776 df, Student 0.07919), `chisq.test` with and without its correction and `fisher.test` on the malocclusion table (0.2857, 0.1224, 0.1745), `fisher.test` on the tea design (1/70 and 17/70), and `anova(lm())` and `oneway.test` on PlantGrowth (F 4.846, p 0.01591; W 5.181 on 2 and 17.128 df, p 0.01739) all agree with the lab to the six significant digits the captures keep, and R 4.5.2 refuses `paired = TRUE` in the formula method (the `author_crosscheck` key in `captures.json`).

This lab reproduces every number the article calls computed or measured. It analyses Student's ten patients, each
given both sleeping drugs, paired and as two groups, with every intermediate printed and matched to SciPy and
statsmodels. It computes the exact type I error and power of Student's and Welch's two-sample t-tests for normal
data, by quadrature over the two sample variances, and checks them by simulation. It simulates the habit of testing
equal variances and normality first and then choosing a test, as one procedure. For 2 × 2 tables it enumerates
Fisher's tea-tasting design, runs eight tests on Hellman's malocclusion table, and sums the exact size of each test
over every possible table. It computes one-way ANOVA's F and Welch's W by hand on R's PlantGrowth data and measures
their type I error when variances differ. The one entry point is `choosing.py`; it prints its numbers and writes them
to the file you name with `--out`. Every simulated quantity is printed as estimate ± its Monte Carlo standard error
(MCSE); exact quantities carry none.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `choosing.py` | G1 | yes | the five stages: `example`, `twosample`, `pretest`, `tables`, `anova` |
| `data/student1908_sleep.csv` | — | — | Student's ten patients on two drugs (public domain), with provenance; Part 2's file with one added line |
| `data/plant_growth.csv` | — | — | R's PlantGrowth: 30 plants, a control and two treatments (part of R, GPL-2 or GPL-3), with provenance |
| `requirements.txt` | — | — | the four pinned dependencies: NumPy, SciPy, statsmodels, pandas |
| `captures.json` | — | — | the author's full run, machine-readable, with the private R cross-check; every figure reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run and `--quick` each peaked at 0.21 GB of RAM |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0 and pandas 3.1.0: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python choosing.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 260 MB; on the build machine `all --quick` took 30 s and `all` 61 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python choosing.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python choosing.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the two CSV files in a folder named `data` beside
`choosing.py`. Each stage also runs alone, for example `python choosing.py tables --out mine.json`. `--quick` cuts
every simulation to a tenth of its replications; the exact computations (the worked example, the quadrature, the
2 × 2 sums, the ANOVA by hand) do not depend on the budget, so they print the article's numbers on either. Two
options exist for the exercises: `--n1`, `--n2` and `--ratio` run the `twosample` stage on a design of your own (E3),
and `--fault` swaps in an earlier draft of the `example` stage (E4).

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `example`: the drugs' means are 0.75 and 2.33 hours, the mean difference 1.58; the SDs are 1.7890, 2.0022 and, for
  the differences, 1.2300, and the correlation between a patient's two results is 0.7952, so Var(d) = 3.2006 +
  4.0090 − 2 × 2.8483 = 1.5129. Paired: SE 0.3890, t = 4.0621 on 9 df, p = 0.002833. As two groups: SE 0.8491,
  t = 1.8608, Student's p = 0.079187 on 18 df and Welch's p = 0.079394 on 17.776 df. SciPy's `ttest_rel` and
  `ttest_ind` and statsmodels' `ttest_ind` match to 1.4 × 10⁻¹⁶.
- `twosample`: with groups of 10 and 40, Student's exact type I error is 0.07%, 0.52%, 5.00%, 12.17%, 18.25% and
  29.37% at SD ratios 1/4, 1/2, 1, 1.5, 2 and 4 (the group of 10's SD over the 40's), Welch's between 4.97% and
  5.15%; with 25 and 25, Student's is at most 5.44%. 200,000 simulated pairs of samples at each checked ratio agree
  within 1.8 MCSE. With equal SDs, Student's 80.0% power is Welch's 75.6% at 10 and 40, and 79.9% at 25 and 25.
- `pretest`: at 10 and 40, letting Levene's test choose rejects 9.74% at an SD ratio of 1.5 and 9.13% at 2, against
  Welch's 5.07% and 5.06%; Levene's test rejects in 27.9% and 64.6% of samples there. Student's error on the samples
  Levene passes is 21.19% at a ratio of 2. Adding a Shapiro–Wilk test first gives 9.53% at 2 and 6.86% at 4.
- `tables`: the tea design's 70 choices split 1, 16, 36, 16, 1; P(all right) = 1/70, P(three or more) = 17/70. On
  the malocclusion table (smallest expected count 2.381) the eight p-values run from 0.1118 (mid-p) to 0.2871
  (doubled Fisher). Over all 483 tables with groups of 20 and 22, the largest exact sizes are Fisher 3.61%, Yates
  2.19%, Pearson 4.94%, mid-p 5.14% and Boschloo 4.63%; with 10 and 40, Pearson reaches 9.11%. SciPy's `barnard_exact`
  differs from the lab on 71 of 481 tables, each tied exactly with another table's |Z|.
- `anova`: PlantGrowth's F = 1.8832/0.3886 = 4.8461 (p = 0.015910) and Welch's W = 5.1810 on 2 and 17.128 df
  (p = 0.017393). Over 100,000 simulated data sets with three groups, F rejects 16.13% under negative pairing and
  2.04% under positive pairing, where W gives 5.25% and 4.90%.

Everything exact or computed matches to every printed digit on any machine. Simulated values repeat exactly with
NumPy 2.5.4 and the default seed; another NumPy may draw different streams and move each simulated value by a few of
its MCSEs. A `--quick` run uses the same streams with fewer replications, so it matches `captures-quick.json` exactly
and `captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden below it.
This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: the worked example, one exact error rate and one 2 × 2 size

Run `python choosing.py all --quick --out mine.json` and compare `mine.json` with `captures-quick.json`. Then find in
your output the paired and unpaired p-values of the worked example, Student's exact type I error with groups of 10
and 40 at an SD ratio of 2, the largest size of Fisher's test with groups of 20 and 22, and PlantGrowth's F and W.

**Self-check:** your provenance line prints NumPy 2.5.4, SciPy 1.18.1 and statsmodels 0.15.0; the five exact values
match the article to the digit; and your simulated values match `captures-quick.json` exactly.

<details><summary>Answer</summary>

The exact values do not depend on the budget: paired p = 0.002833, unpaired 0.079187 (Student) and 0.079394 (Welch),
Student's exact error 18.25%, Fisher's largest size 3.61%, F = 4.8461 and W = 5.1810. The quick run's simulated
values sit within about two quick MCSEs of the full run's: Levene-decides at a ratio of 2 is 9.74% ± 0.30 against
9.13% ± 0.09, and the simulated check of Fisher's size at π = 0.12 is 2.70% ± 0.11 against the exact 2.95%, the
largest gap at 2.2 MCSE. If an exact value differs, check the versions first, then the data: their hashes are in the
`data_sha1` field of the provenance.

</details>

### E2 — Inspect: the tables Boschloo's test adds

With groups of 20 and 22, Boschloo's test rejects every table Fisher's test rejects at 5%, plus 10 more. The capture
lists those 10 under `tables.boschloo_not_fisher`, as `[normal teeth among 20, among 22, Fisher's p, Boschloo's p]`.
Before you look, predict what Fisher's p-value for such a table must be, and why Boschloo's can be lower. Then read
the list and pick one table.

**Self-check:** you predicted Fisher's p just above 0.05; you named one table with both p-values; and you can say why
Boschloo's region contains Fisher's in this design but not in every design.

<details><summary>Answer</summary>

Every one of the 10 has Fisher's p between 0.055 and 0.063, just above the line, and Boschloo's between 0.038 and
0.048: for example 4 of 20 against 11 of 22, Fisher 0.0577, Boschloo 0.0467. Fisher's test spends its 5% table by
table within each margin, and the discreteness leaves part of it unused; Boschloo's test takes Fisher's p as a
statistic and computes its p-value from the two-binomial design, which lets these near-misses in while keeping the
size at most 4.63%. The containment is guaranteed only against the doubled-tail Fisher test, because SciPy's
two-sided Boschloo p doubles the smaller one-sided p. With groups of 10 and 40 (`tables.unbalanced_fisher_not_boschloo`),
Irwin's-rule Fisher rejects 4 tables Boschloo does not, such as 3 of 10 against 2 of 40: Fisher 0.0483, Boschloo
0.0518.

</details>

### E3 — Predict: swap which group has the larger SD

Run `python choosing.py twosample --quick --n1 40 --n2 10 --ratio 2 --out e3.json`: the group of **40** now has twice
the SD of the group of 10. Before you run it, write down whether Student's test becomes liberal or conservative,
roughly how far from 5% it moves, and what happens to Welch's test.

**Self-check:** the direction of Student's error and its rough size, Welch's near 5%, and the reason in terms of how
the pooled variance weights the two groups.

<details><summary>Answer</summary>

Conservative: the exact size is 0.52%, the mirror image of the 10-and-40 design at half the SD, and the simulated
value is 0.56% ± 0.05; Welch's is 5.01% exact and 5.27% ± 0.16 simulated. The pooled variance weights each group by
its degrees of freedom, so the larger group's larger variance dominates it, averaging (39 × 4 + 9 × 1)/48 = 3.44,
while the variance of the difference in means weights the smaller group's variance more: Student's standard error
is too large, its t too small, and it rarely rejects. Welch's test estimates the two variances separately and is
unaffected.

</details>

### E4 — Diagnose: a paired test that is too sure of itself

Run `python choosing.py example --quick --fault --out fault.json`. The paired p-value drops from 0.0028 to about
0.000007, yet the mean difference is still 1.58 hours and both unpaired tests are unchanged. The stage's pairing is
an earlier draft. Name the symptom, the cause, the one printed line that proves it, and the fix, then check that the
fix holds.

**Self-check:** the cause is in how the draft pairs the two drugs' values, the proof is a printed line, and after the
fix the paired p is 0.002833 again.

<details><summary>Answer</summary>

- **Symptom:** t = 9.2674 and p = 0.000007; the SD of the differences is 0.5391 instead of 1.2300, and the drugs'
  correlation 0.9658 instead of 0.7952. The mean difference cannot change, because it is the difference of the two
  means however the values are paired, and the unpaired tests ignore pairing altogether.
- **Cause:** the draft reshapes the table to long form, sorts it by hours to print it neatly, and pairs the i-th row
  of drug 1 with the i-th row of drug 2. Sorting both columns pairs the smallest with the smallest, which makes the
  two columns as correlated as they can be and the differences as uniform as they can be. Any order other than the
  patients' own makes the p-value wrong; this one makes it too small.
- **Proof:** the line `pairs (patient on drug 1, patient on drug 2): (2, 5), (4, 4), (3, 2), ...` shows patient 2's
  drug 1 value paired with patient 5's drug 2 value. In a correct analysis every pair reads (k, k).
- **Fix:** pair on the patient column, not on row position, as the stage does without `--fault` and as R's
  `Pair(x, y) ~ 1` makes you do. Rerun without `--fault`: every pair reads (k, k) and p = 0.002833. Nothing on disk
  changed except `fault.json`.

</details>

## Safety and cleanup

- `choosing.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection. It never
  overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json e3.json fault.json
```
