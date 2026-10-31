# Lab — Confidence Intervals: What 95% Means, Measured

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-31 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `intervals.py` 4cde398084f1, root seed 20261031. The notebook was built and executed with the same pins. The author also checked the lab privately against base R 4.5.2: `binom.test(2, 20)` and `prop.test(2, 20, correct = FALSE)` return the Clopper–Pearson and Wilson limits to six decimals; `poisson.test(c(8, 162), c(2.214, 2.222))` gives efficacy 90.00% to 97.90%; the Wald interval's exact coverage at n = 20 and p = 0.1 is 0.876037; and R's mean coverages over a uniform p, from `pbeta` sums, match the lab's to four decimals. For the severe split R's `poisson.test` reports p = 0.011574, as SciPy does (the `author_crosscheck` key in `captures.json`).

This lab reproduces every number the article calls computed or measured. It computes the exact coverage of five
95% intervals for a binomial proportion (Wald, Wilson, Agresti–Coull, Clopper–Pearson and Jeffreys) by summing
binomial probabilities over every outcome, with nothing simulated, then measures the same coverage by simulation to
show the two agree. It reads each interval as an inverted test and matches all five to statsmodels and SciPy. It
recomputes Agresti and Coull's 1998 table of mean coverages and every Clopper–Pearson efficacy interval the
BNT162b2 trial published, from the case splits in `data/`. It computes the error rate and power of judging a
difference by whether two intervals overlap, and simulates it. And it measures the coverage of the one-sample
t-interval on a real, heavily skewed population of customer spend, by sample size and by interval width. The one
entry point is `intervals.py`; it prints its numbers and writes them to the file you name with `--out`. Every
simulated quantity is printed as estimate ± its Monte Carlo standard error (MCSE).

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `intervals.py` | G1 | yes | the six stages: `enumerate`, `invert`, `coverage`, `pfizer`, `overlap`, `tcoverage` |
| `data/online_retail_customer_spend.csv` | — | — | net spend of 4,317 customers (UCI Online Retail, CC BY 4.0), with provenance |
| `data/bnt162b2_case_splits.csv` | — | — | the trial's 18 published case splits, surveillance times and intervals, with sources |
| `requirements.txt` | — | — | the four pinned dependencies: NumPy, SciPy, statsmodels and pandas |
| `captures.json` | — | — | the author's full run, machine-readable, with the private cross-checks against R; every figure in the article reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.28 GB of RAM, `--quick` at 0.19 GB |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0 and pandas 3.1.0: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python intervals.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 260 MB; on the build machine `all --quick` took 11 s and `all` 17 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python intervals.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python intervals.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the two CSV files in a folder named `data` beside
`intervals.py`. Each stage also runs alone, for example `python intervals.py pfizer --out mine.json`. `--quick`
cuts every simulation to a tenth of its replications; the exact stages take the same time on either budget, which is
why `--quick` saves less than you might expect. Four flags exist for the exercises: `--n` and `--p` set the worked
example's trials and true proportion in the `enumerate` stage, `--split` makes the `pfizer` stage analyse a case
split of your choosing, and `--fault` swaps in an earlier draft of one interval (E4).

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `enumerate`: with 20 trials and p = 0.1, the Wald interval contains 0.1 for X = 1 to 6 and its exact coverage is
  0.8760; Wilson, Agresti–Coull and Jeffreys contain it for X = 0 to 4 (0.9568), Clopper–Pearson for X = 0 to 5
  (0.9887). A million simulated audits give 87.57% ± 0.03, 95.68% ± 0.02 and 98.89% ± 0.01.
- `invert`: for 2 successes in 20 the 0.05 crossings of the Wald, score and exact tests' p-value functions are
  (−0.031478, 0.231478), (0.027866, 0.301034) and (0.012349, 0.316983); the last two equal the Wilson and
  Clopper–Pearson formulas to 6 × 10⁻¹⁶ and 5 × 10⁻¹⁸. All five intervals match statsmodels' `proportion_confint`
  to 4.4 × 10⁻¹⁶ for every x and n up to 100 (Jeffreys for 0 < x < n, where the two conventions agree), and SciPy's
  `proportion_ci` to 2.2 × 10⁻¹⁵ for every x at n = 1, 2, 5, 10, 20, 50 and 170. statsmodels defaults to
  `method="normal"`, the Wald interval; SciPy defaults to `"exact"`.
- `coverage`: at n = 50 the Wald interval's coverage is below 93% for 40.0% of p; the minima are 0.8393 for Wilson,
  0.9345 for Agresti–Coull, 0.9508 for Clopper–Pearson and 0.8839 for Jeffreys. At p = 0.1 the Wald interval's
  coverage falls from 0.9467 at n = 29 to 0.8085 at n = 30 and is 0.8789 at n = 50. All 15 mean coverages in Agresti
  and Coull's Table 1 reproduce to three decimals; 9 of their 15 root mean square errors do, the largest gap 0.0021.
  The add-two interval's minimum is 0.9168 at n = 10, and Wilson's coverage still dips to 0.8387 at n = 10,000.
- `pfizer`: the primary split, 8 of 170, gives efficacy 95.0% with a Clopper–Pearson interval of 90.0% to 97.9%,
  as the paper prints; 9 of the 16 published Clopper–Pearson rows match every digit and all 16 lie within what
  three-decimal surveillance times allow. The severe split, 1 against 9, gives 88.9% (20.1% to 99.7%); the two
  arms' rate intervals overlap from 1.027 to 1.386 per 1,000 person-years, and the exact test gives p = 0.0212
  (SciPy's two-sided rule: 0.0116).
- `overlap`: judging a difference by non-overlap of 95% intervals has a type I error of 0.00557 at equal standard
  errors, 83.4% intervals make it a 5% test, and at an 80%-power design it has 51.2% power. Simulated with 10 per
  group: the t-test rejects 4.99% ± 0.05, the 95% intervals fail to overlap 0.57% ± 0.02, the 83.4% intervals
  4.97% ± 0.05.
- `tcoverage`: on the customer spend (skewness 21.58) the 95% t-interval covers 64.42% ± 0.11 at n = 10, 65.83% ±
  0.11 at 30, 70.30% ± 0.10 at 100, 85.65% ± 0.14 at 1,000 and 93.84% ± 0.17 at 10,000; at n = 30 it lies wholly
  below the mean in 34.17% of samples. Sorted into tenths by width, the narrowest tenth at n = 30 covers 0.0%; a
  normal population's narrowest tenth covers 88.2%.

Everything exact or computed matches to every printed digit on any machine; another SciPy or statsmodels may move the
last digits of their own lines. Simulated values repeat exactly with NumPy 2.5.4 and the default seed; another NumPy
may draw different streams and move each simulated value by a few of its MCSEs. A `--quick` run uses the same streams
with fewer draws, so it matches `captures-quick.json` exactly and `captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden below it.
This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: exact coverage, the trial's interval and the t-interval

Run `python intervals.py all --quick --out mine.json` and compare `mine.json` with `captures-quick.json`. Then find in
your output the exact coverage of the Wald, Wilson and Clopper–Pearson intervals in the worked example, the trial's
Clopper–Pearson efficacy interval, the overlap rule's type I error at equal standard errors, and the t-interval's
coverage on the spend at n = 30.

**Self-check:** your provenance line prints NumPy 2.5.4 and SciPy 1.18.1; the exact values match the article to the
digit (0.8760, 0.9568, 0.9887; 90.0% to 97.9%; 0.00557), and the simulated coverage at n = 30 lies within two of its
MCSEs of the article's 65.83%.

<details><summary>Answer</summary>

The exact values do not depend on the budget or the seed: 0.8760, 0.9568 and 0.9887; efficacy 95.0% from 90.0% to
97.9%; 0.00557. The author's quick run gives 65.98% ± 0.34 at n = 30, against 65.83% ± 0.11 in the full run: well
within two quick MCSEs. If your exact values differ, check the versions first; if your simulated ones differ by more
than a few MCSEs with the same versions, check that the CSV files are the shipped ones (their hashes are in the
`data_sha1` field of the provenance).

</details>

### E2 — Inspect: the published rows that do not match to the digit

The `pfizer` stage recomputes the 16 Clopper–Pearson rows the trial published, and the article says 9 match every
printed digit while the other 7 lie within what three-decimal surveillance times allow. In your capture, `pfizer.rows`
holds each row's recomputed interval and the flags `matches_printed` and `within_rounding`. Before you look, state
which kind of row you expect to be most sensitive to the rounding, and why. Then list the 7, and for the row with the
largest gap compute by hand the lower efficacy limit at the two extremes of its surveillance-time ratio.

**Self-check:** you named the 7 rows; for the largest gap you showed that the printed lower limit lies between the two
extremes you computed.

<details><summary>Answer</summary>

The rows with the smallest surveillance times are the most sensitive, because a rounding error of 0.0005 thousand
person-years is a larger share of a small time. The 7 rows are age over 55, age 75 or over, male, Black or African
American, all others, Argentina and Brazil. The largest gap is the 75-or-over row, 0 vaccine against 5 placebo cases:
the lab gives a lower limit of −13.4% against the printed −13.1%. With 0 of 5 cases the Clopper–Pearson upper limit
for the vaccine share is 1 − 0.025^(1/5) = 0.5218, so IRR = 0.5218/(0.4782 r). The printed times 0.102 and 0.106 can
be anything from 0.1015 to 0.1025 and 0.1055 to 0.1065, so r runs from 0.1015/0.1065 = 0.9531 to 0.1025/0.1055 =
0.9716, and the lower efficacy limit from −14.5% to −12.3%. The printed −13.1% lies inside.

</details>

### E3 — Predict: half the trial

Suppose the trial had stopped at half the cases with the same split: 4 in the vaccine group and 81 in the placebo
group, with the same ratio of surveillance times. Run `python intervals.py pfizer --quick --split 4 81 --out e3.json`.
Before you run it, write down the efficacy estimate and how the 95% interval changes: which end moves more, and
roughly how far.

**Self-check:** the estimate, the direction of each end, and the size of the lower end's move within two points, for
the reason the article gives: the binomial for a share near zero is skewed.

<details><summary>Answer</summary>

The estimate stays at 95.0%, because the split and the surveillance ratio are unchanged. The interval widens from
90.0%–97.9% to 86.8%–98.7%: the lower end falls 3.2 points and the upper end rises 0.8. A share near zero has a
binomial skewed toward larger values, so the share's upper limit, which sets efficacy's lower limit, moves most. On
the log rate ratio scale the interval is 1.48 times as wide, a little more than the √2 that halving the counts would
give in large samples. Doubling the trial instead (`--split 16 324`) gives 91.8% to 97.2%.

</details>

### E4 — Diagnose: a guaranteed interval that does not cover

Run `python intervals.py coverage --quick --fault --out fault.json`. The Clopper–Pearson interval is constructed to
cover at least 95% at every p, yet the guarantee check fails and other numbers in the stage turn strange. One interval
in this stage is an earlier draft. Name the symptom, the cause, the one printed line that proves it, and the fix, then
check that the fix holds.

**Self-check:** the cause is in how the draft handles one or two particular counts, the proof is a printed interval,
and after the fix the guarantee check prints yes with a minimum coverage of 0.9508 at n = 50.

<details><summary>Answer</summary>

- **Symptom:** with `--fault` the stage prints `guarantee check: ... : NO`; Clopper–Pearson's minimum coverage is
  0.0000 at p = 0.0005, and its mean coverage and width are `nan`, as are its five mean coverages in the Table 1 rows.
- **Cause:** `clopper_pearson_draft` evaluates `stats.beta.ppf(0.025, x, n - x + 1)` at x = 0, where the beta
  distribution's first parameter is 0. That is outside its parameter space, so SciPy returns `nan` without a warning,
  and the same happens to the upper limit at x = n. Every comparison with `nan` is false, so the outcomes X = 0 and
  X = n never count as covering anything. Near p = 0, where X = 0 is the likeliest outcome, the coverage collapses.
- **Proof:** the line `Clopper-Pearson interval printed for x = 0 of 50: (nan, 0.0711)`.
- **Fix:** apply the conventions the method defines, a lower limit of 0 at x = 0 and an upper limit of 1 at x = n,
  as `clopper_pearson()` does. Edit the draft that way and rerun the same command: the check prints yes, with a minimum of 0.9508 at p = 0.9283. Nothing on disk changed except
  `fault.json`, so a run without `--fault` is the original lab.

</details>

## Safety and cleanup

- `intervals.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection. It never
  overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json e3.json fault.json
```
