# Lab — Permutation and Rank Tests: What They Actually Test

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-11-23 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-43-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.16, NumPy 2.5.4, SciPy 1.18.1; `permutation.py` d180435ad219, root seed 20261123. The notebook was built and executed with the same pins. The author also checked the lab privately against base R 4.5.2: `t.test` on Darwin's pairs (t 2.147987, p 0.0497029), `wilcox.test(conf.int = TRUE)` (V 96, exact p 0.0412598, Hodges–Lehmann 3.125, interval 0.5 to 5.1875), `binom.test` (p 0.00738525), `wilcox.test` on the two-sample example (W 63, exact p 0.199529, normal approximation 0.195988, Hodges–Lehmann −0.3525), and `cor.test` on the law-school sample (Pearson p 0.000665102, Spearman ρ 0.796429 with AS 89 p 0.000607857, Kendall τ 0.638095 with exact p 0.000532022) all agree with the lab to the six significant digits the captures keep, except R's Spearman p, which is an Edgeworth approximation at n = 15 (the `author_crosscheck` key in `captures.json`).

This lab reproduces every number the article calls computed or measured. It enumerates all 32,768 sign assignments
of Darwin's 15 pairs of *Zea mays*, the randomisation test Fisher counted by hand, beside the paired t-test, the
Wilcoxon signed-rank test, the sign test and the Hodges–Lehmann estimate with its exact interval, each matched to
SciPy. It computes what SciPy's default Monte Carlo version returns on those pairs, and what a Monte Carlo p-value
without its +1 does to a family of tests. A permutation engine for two independent samples measures the size of the
raw and the studentised permutation tests of equal means when the variances differ. It simulates the Mann–Whitney,
Brunner–Munzel and Welch tests in three designs that separate medians, P(X > Y) and identical distributions,
computes the asymptotic relative efficiency of ranks by quadrature with power at n = 20 by simulation, and computes
Pearson's, Spearman's and Kendall's correlations of the law-school sample with exact and Monte Carlo p-values. The
one entry point is `permutation.py`; it prints its numbers and writes them to the file you name with `--out`.
Every simulated quantity is printed as estimate ± its Monte Carlo standard error (MCSE); exact quantities carry none.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `permutation.py` | G1 | yes | the five stages: `example`, `twosample`, `mannwhitney`, `efficiency`, `correlation` |
| `data/darwin1876_zea_mays.csv` | — | — | Darwin's 15 pairs (1876, public domain), heights in eighths of an inch, with provenance |
| `data/law_school_82.csv` | — | — | the law-school data (CRAN `bootstrap`, BSD 3-clause); Part 7's file with one added line |
| `requirements.txt` | — | — | the two pinned dependencies: NumPy and SciPy |
| `captures.json` | — | — | the author's full run, machine-readable, with the private R cross-check; every figure reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.30 GB of RAM and `--quick` at 0.27 GB |
| Software | Python 3 (run on 3.12.16) with NumPy 2.5.4 and SciPy 1.18.1: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python permutation.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 220 MB; on the build machine `all --quick` took 20 s and `all` 2 min 38 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python permutation.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python permutation.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the two CSV files in a folder named `data` beside
`permutation.py`. Each stage also runs alone, for example `python permutation.py example --out mine.json`. `--quick`
cuts every simulation to a tenth of its replications (the law-school reorderings from 99,999 to 9,999); the exact
computations (the enumeration of Darwin's pairs, the signed-rank and sign tests, the Hodges–Lehmann interval, the
binomial distribution of SciPy's Monte Carlo p-value, the quadrature, Spearman's exact p-value) do not depend on the
budget, so they print the article's numbers on either. Two options exist for the exercises: `--n1`, `--n2` and
`--ratio` run the `twosample` stage on a design of your own (E3), and `--fault` swaps in an earlier draft of the
`example` stage's enumeration (E4).

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `example`: the differences in eighths of an inch are 49, −67, 8, 16, 6, 23, 28, 41, 14, 29, 56, 24, 75, 60, −48,
  summing to 314. The paired t is 2.1480 on 14 df, p = 0.049703. Of the 32,768 sign assignments 835 total more than
  314, 28 exactly 314, so 863 at least 314, and the two-sided p is 1,726/32,768 = 0.052673; the counts by number of
  negative signs reproduce Fisher's Table 4. The signed-rank V+ is 96, p = 0.041260; the sign test p is 0.007385.
  Galton's re-paired columns give t = 5.1714. The Hodges–Lehmann estimate is 3.125 in, its exact interval 0.5 to
  5.1875 in at 95.21% confidence. SciPy's default `permutation_test` gives p ≤ 0.05 in 19.4% of reruns (exact), and
  in 21.3% ± 1.3 of 1,000 actual runs. With 999 permutations per test and Bonferroni over 1,000 true nulls, b/m gives
  a family-wise error of 63.2%, (b + 1)/(m + 1) gives 0.0%.
- `twosample`: the engine matches SciPy's exact enumeration on 4 and 6 values. With groups of 10 and 40, the
  permutation test of the raw difference rejects 18.31% ± 0.17 at an SD ratio of 2 and 29.10% ± 0.20 at 4 (Student's
  t-test on the same data 18.34% and 29.20%), and 0.06% at 1/4; studentised, 5.73% ± 0.10, 5.81% ± 0.10 and 3.87% ±
  0.09. With 25 and 25 the two permutation tests are the same test and reject 5.06% to 5.57%.
- `mannwhitney`: X ~ N(0, 1) against Y = E − ln 2, E ~ Exp(1), has equal medians and SDs and P(X > Y) = 0.443065;
  Mann–Whitney rejects 16.7% ± 0.3 at 50 per group, 50.2% ± 0.4 at 200 and 79.7% ± 0.3 at 400. With Y = E − 0.875798,
  P(X > Y) = ½ and the medians differ by 0.18; Mann–Whitney rejects 4.7% to 5.7% at every size. With normal groups of
  10 and 40 and equal centres it rejects 9.93% ± 0.21 at an SD ratio of 2 and 14.81% ± 0.25 at 4, where
  Brunner–Munzel's test gives 5.55% and 5.27%. The two-sample Hodges–Lehmann estimate in the first design converges
  to −0.1827, not to the difference in medians, 0.
- `efficiency`: the asymptotic relative efficiencies are 0.8640 (parabolic), 0.9549 (normal), 1.0000 (uniform),
  1.0966 (logistic), 1.2412 (t, 5 df), 1.5000 (Laplace), 1.3733 (contaminated normal) and 1.8998 (t, 3 df). At n = 20
  per group with a shift of 0.9091 SD, Welch's power is 79.7% and Mann–Whitney's 77.6% for normal data; for t with 3
  df, 84.0% and 95.0%.
- `correlation`: r = 0.7764, ρ = 0.7964, τ = 0.6381. Kendall's exact p is 0.000532; Spearman's exact p, counted over
  all 15! orderings, is 0.000638, where SciPy's t approximation gives 0.000380; the Monte Carlo p-values with 99,999
  reorderings are 0.00134 (Pearson), 0.00078 (Spearman) and 0.00067 (Kendall).

Everything exact or computed matches to every printed digit on any machine. Simulated values repeat exactly with
NumPy 2.5.4, SciPy 1.18.1 and the default seed; other versions may draw different streams and move each simulated
value by a few of its MCSEs. A `--quick` run uses the same streams with fewer replications, so it matches
`captures-quick.json` exactly and `captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden below it.
This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: the enumeration, three exact tests and one simulated size

Run `python permutation.py all --quick --out mine.json` and compare `mine.json` with `captures-quick.json`. Then find
in your output the number of sign assignments whose total is at least 314 and the two-sided p, the paired t-test's
p, the signed-rank p, the Hodges–Lehmann estimate and interval, and the size of the raw and the studentised
permutation tests with groups of 10 and 40 at an SD ratio of 2.

**Self-check:** your provenance line prints NumPy 2.5.4 and SciPy 1.18.1; the exact values match the article to the
digit; and your simulated values match `captures-quick.json` exactly.

<details><summary>Answer</summary>

The exact values do not depend on the budget: 863 of 32,768 and p = 0.052673; t-test p = 0.049703; signed-rank p =
0.041260; Hodges–Lehmann 3.125 in with the interval 0.5 to 5.1875 in. The quick run's sizes at a ratio of 2 are
18.62% ± 0.55 (raw difference) and 5.98% ± 0.34 (studentised), within a quick MCSE of the full run's 18.31% ± 0.17
and 5.73% ± 0.10. If an exact value differs, check the versions first, then the data: their hashes are in the
`data_sha1` field of the provenance.

</details>

### E2 — Inspect: Fisher's Table 4

The capture lists the enumeration by number of negative signs under `example.table4`, each row as `[negatives,
totals above 314, totals equal to 314, totals below 314, assignments]`. Fisher printed rows only for 2 to 6 negative
signs. Before you look, work out from the 15 differences why every assignment with 0 or 1 negative sign totals more
than 314, and why every assignment with 7 or more totals less. Then read the row for 4 negative signs.

**Self-check:** you found the two boundary totals by arithmetic, and the row for 4 negative signs reads 302, 11,
1,052 and 1,365, as Fisher printed it.

<details><summary>Answer</summary>

The magnitudes sum to 544 eighths, and a minus sign on a magnitude takes twice that magnitude off the total. One
minus sign takes off at most 2 × 75 = 150, leaving at least 394, above 314. Seven minus signs take off at least twice
the seven smallest magnitudes, 2 × (6 + 8 + 14 + 16 + 23 + 24 + 28) = 238, leaving at most 306, below 314. The row
for 4 negative signs is `[4, 302, 11, 1052, 1365]`: C(15, 4) = 1,365 assignments, of which 313 total at least 314.
Summed over the rows, 835 are above, 28 equal and 863 at least 314, Fisher's count.

</details>

### E3 — Predict: equal group sizes

Run `python permutation.py twosample --quick --n1 25 --n2 25 --ratio 4 --out e3.json`: two groups of 25, the first
with four times the SD of the second, equal means. Before you run it, write down whether the permutation test of the
raw difference keeps its 5% here, as it did not with groups of 10 and 40, and how the studentised test's rate
compares with it.

**Self-check:** the raw test's rate near 5%, the two permutation tests' rates identical, and the reason for each.

<details><summary>Answer</summary>

Both permutation tests reject 5.62% ± 0.33 on the quick budget (5.57% ± 0.10 on the full one); Student's t-test 5.54%
and Welch's 5.00%. With equal sizes, the permutation distribution of the difference has the same large-sample
variance as its sampling distribution even when the variances differ, so the raw test is asymptotically valid, as
Romano showed. The rates are identical because, across the relabellings of one data set, the studentised statistic
is an increasing function of the absolute difference: with n per group, (n − 1)(s₁² + s₂²) equals the total sum of
squares about the grand mean minus n D²/2, where D is the difference in means, and the total does not change under
relabelling. The two tests order the relabellings identically and reject the same data sets.

</details>

### E4 — Diagnose: Fisher's count comes out short

Run `python permutation.py example --quick --fault --out fault.json`. The stage's enumeration is an earlier draft,
and the two-sided p comes out 0.051392 instead of 0.052673, while the t-test, the signed-rank test and the sign test
are unchanged. Name the symptom, the cause, the one printed line that proves it, and the fix, then check that the fix
holds.

**Self-check:** the cause is in how the draft compares totals, the proof is a printed line, and after the fix the count
is 863 and p = 0.052673 again.

<details><summary>Answer</summary>

- **Symptom:** 842 assignments counted as at least the observed total, not 863; the p-value is too small by 2 × 21 of
  32,768.
- **Cause:** the draft converts the differences to centimetres (× 2.54/8) and compares floating-point totals exactly.
  2.54/8 is not a binary fraction, so the 28 assignments whose totals equal the observed one in exact arithmetic sum
  their terms with different rounding: the observed total prints as 99.69500000000001 cm, and 21 of the 28 tied totals
  come out a hair smaller and are counted as less extreme. In eighths of an inch every total is an exact integer.
- **Proof:** the line `totals > 314: 835, = 314: 28, at least 314: 842`, whose first two counts come from the exact
  totals: 835 + 28 = 863, not 842.
- **Fix:** compute in integer eighths, as the stage does without `--fault`, or count totals within a relative
  tolerance of the observed one, as SciPy's `permutation_test` does (100 machine epsilons). Rerun without `--fault`:
  863 and p = 0.052673. Nothing on disk changed except `fault.json`.

</details>

## Safety and cleanup

- `permutation.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection. It
  never overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json e3.json fault.json
```
