# Lab — Bayesian Inference by Hand: Conjugacy and Credible Intervals

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-11-25 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-43-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.16, NumPy 2.5.4, SciPy 1.18.1; `bayes.py` f3b096d9fc45, root seed 20261125. The notebook was built and executed with the same pins. The author also checked the lab privately against base R 4.5.2, whose `pbeta` (TOMS 708) and `qbeta` are independent of SciPy's Boost: the three credible intervals (90.317129 to 97.616944, 89.894519 to 97.317223, −124.80786 to 96.299247), P(VE ≤ 30%) for each, Laplace's tails (1.14605849e-42 and 5.592801428e-73), the protocol's success and futility boundaries (6, 15, 25, 35, 53; 15, 26, 35, with the beta-binomial written from `lchoose` and `lbeta`), and for 1782 `binom.test` (p 0.0241218) and both Bayes factors (8.59676 and 1/11.5441) all agree with the lab to the digits R printed (the `author_crosscheck` key in `captures.json`).

This lab reproduces every number the article calls computed. It answers Laplace's question for the Paris baptisms of
1745 to 1770, the probability that a birth is a boy with probability at most ½, by exact integer arithmetic, by SciPy
and by Laplace's own 1781 series. It reconciles his 1783 table of yearly baptisms with the totals of 1812. It rebuilds
the Pfizer–BioNTech trial's Bayesian analysis from its protocol: the prior's constants, the posterior, the three
published credible intervals, the protocol's success and futility boundaries, and the operating characteristics of
its sequential design. It checks the three conjugate pairs against brute-force normalisation, compares equal-tailed
with highest-density intervals on two scales, computes the exact frequentist coverage of the trial's credible
interval, sweeps the prior, and computes the Bayes factor against the p-value for each year of Paris baptisms from
1771 to 1784. The one entry point is `bayes.py`; it prints its numbers and writes them to the file you name with
`--out`. Two Monte Carlo checks print an estimate ± its Monte Carlo standard error (MCSE); everything else is exact.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `bayes.py` | G1 | yes | the six stages: `laplace`, `pfizer`, `conjugate`, `intervals`, `priors`, `lindley` |
| `data/paris_baptisms_1745_1784.csv` | — | — | Laplace's Paris baptisms by sex: 1745–1770, each year 1771–1784, and 1745–1784 (public-domain works), with provenance |
| `data/bnt162b2_bayesian_rows.csv` | — | — | the trial's case splits and surveillance times behind its credible intervals, and one subgroup for E3, with sources |
| `requirements.txt` | — | — | the two pinned dependencies: NumPy and SciPy |
| `captures.json` | — | — | the author's full run, machine-readable, with the private R cross-check; every figure reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.14 GB of RAM and `--quick` at 0.13 GB |
| Software | Python 3 (run on 3.12.16) with NumPy 2.5.4 and SciPy 1.18.1: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python bayes.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 220 MB; on the build machine `all --quick` took 7 s and `all` 10 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python bayes.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python bayes.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the two CSV files in a folder named `data` beside
`bayes.py`. Each stage also runs alone, for example `python bayes.py pfizer --out mine.json`. `--quick` cuts the two
Monte Carlo checks from 400,000 draws to 40,000; every other number is exact and identical on either budget. Two
options exist for the exercises: `--split` and `--times` run the `priors` stage on a case split of your own (E3), and
`--fault` swaps in an earlier draft of the `pfizer` stage's efficacy map (E4).

## What to expect

The first line is the provenance line. Then, stage by stage:

- `laplace`: 251,527 boys and 241,945 girls give the posterior beta(251,528, 241,946), mean 0.509709, SD 0.000712.
  P(x ≤ ½) is 1.1460584901553381e-42 in exact integers and 1.146058490156627e-42 from SciPy. Laplace's first term
  recomputes to 1.1522e-42 (he printed 1.1521e-42), 0.53% above the exact value; his second term is 1/186. The 1783
  table's years sum to 141,859 boys and 135,610 girls, against its printed total row of 151,859 and 145,159, and
  reproduce the 1812 totals 393,386 and 377,555.
- `pfizer`: 0.4118/0.5882 = 0.700102006; the prior's 95% interval for VE runs from −26.16 to 0.9948 (as fractions).
  The posterior beta(8.700102, 163) gives VE from 90.317% to 97.617% (published 90.3 to 97.6) and P(VE ≤ 30%) =
  2.456e-28; 9:169 gives 89.9 to 97.3 and the severe 1:3 gives −124.8 to 96.3, all matching. The protocol's Table 6
  success boundaries (6, 15, 25, 35, 53) and futility boundaries (15, 26, 35) match every entry, and its Tables 7 and
  8 match in 44 of 45 printed values; overall success at VE 30% is 0.0210.
- `conjugate`: the beta-binomial marginal likelihood is 1.013023e-2 by quadrature and in closed form; the two arms'
  case rates are gamma(8.5, rate 2.214), mean 3.839, and gamma(162.5, 2.222), mean 73.132 per 1,000 person-years; the
  normal–normal update of 1782 after 1745–1770 gives 0.509649, SD 0.000698, as the exact beta update does.
- `intervals`: for 8:162 the equal-tailed interval is 90.32% to 97.62% and the HDI of VE 90.86% to 97.94%; for 1:3,
  −124.81% to 96.30% against −69.71% to 99.95%. The credible interval's exact coverage with 170 cases is 92.9% to 96.5%
  for true efficacies from 0% to 95%; averaged over the prior it is 95.000000% by quadrature, 95.01% ± 0.03 by
  simulation.
- `priors`: five priors put the 8:162 lower limit between 90.1% and 90.9%, the 1:3 lower limit between −154.6% and
  −116.6%; a prior centred at VE 0% and worth 170 cases gives 52.3% to 70.4%.
- `lindley`: 1782 has z 2.262, exact p 0.0241 and BF01 8.597 under a uniform alternative; the years 1772, 1778, 1779
  and 1782 have p below 0.05 and BF01 above 1. With the 1745–1770 posterior as H1's prior, BF10 is 11.544.

Everything exact matches to every printed digit on any machine with these pins. The simulated values repeat exactly
with NumPy 2.5.4 and the default seed; other versions may draw different streams and move them by a few MCSEs. A
`--quick` run uses the same streams with fewer draws, so it matches `captures-quick.json` exactly.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden below it.
This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: Laplace's tail, the trial's interval and the 1782 Bayes factor

Run `python bayes.py all --quick --out mine.json` and compare `mine.json` with `captures-quick.json`. Then find in your
output P(x ≤ ½) for 1745–1770, the trial's 95% credible interval for VE and P(VE ≤ 30%), the final-analysis boundary
with the posterior probabilities either side of it, and the 1782 p-value and Bayes factor.

**Self-check:** your provenance line prints NumPy 2.5.4 and SciPy 1.18.1; the exact values match the article to the
digit; your two simulated coverage averages match `captures-quick.json` exactly.

<details><summary>Answer</summary>

The exact values do not depend on the budget: P(x ≤ ½) = 1.146058490156627e-42; VE from 90.317% to 97.617%; P(VE ≤
30%) = 2.456e-28; at 164 cases success needs at most 53 vaccine cases, with posterior probabilities 0.9904 at 53 and
0.9853 at 54 against the threshold 0.986; 1782 gives p = 0.0241 and BF01 = 8.597. The quick run's prior-averaged
coverages are 95.07% ± 0.11 and 95.01% ± 0.11 (S 40,000), within a quick MCSE of 95%. If an exact value differs, check
the versions first, then the data: their hashes are in the `data_sha1` field of the provenance.

</details>

### E2 — Inspect: where the protocol's boundaries come from

The capture lists, under `pfizer.success_curves`, P(VE > 30% | x vaccine cases) for every x at each analysis, and under
`pfizer.pos_curves` the predictive probability of final success at the three interim analyses. Before you look,
write down which x the 0.995 threshold makes the success boundary at 62 cases, and which x makes the 5% futility rule
stop the trial at 62 cases. Then read the two curves at 62.

**Self-check:** your two numbers are 15 and 26, each with the probabilities either side of its threshold.

<details><summary>Answer</summary>

At 62 cases P(VE > 30%) is 0.9975 with 15 vaccine cases and 0.9943 with 16, so success needs at most 15, the
protocol's 15:47. The predictive probability of final success is 5.23% with 25 vaccine cases and 2.49% with 26, so
futility starts at 26, the protocol's 26:36. Both come from one posterior, beta(0.700102 + x, 1 + 62 − x): the first
is its tail below θ = 0.7/1.7, the second the beta-binomial sum over the remaining 102 cases.

</details>

### E3 — Predict: a subgroup with no vaccine cases

Among participants aged 75 or over the trial had 0 vaccine and 5 placebo cases, over 0.102 and 0.106 thousand
person-years. Run `python bayes.py priors --quick --split 0 5 --times 0.102 0.106 --out e3.json`. Before you run it,
write down which of the five priors (trial, Senn's alternative, uniform, Jeffreys, Haldane) gives the highest lower
limit for VE, and which gives no interval.

**Self-check:** the order of the four lower limits, and the reason one prior fails.

<details><summary>Answer</summary>

The row `yours 0:5` reads: trial 29.9 to 99.9; Senn's alternative 19.5 to 99.6; uniform 11.7 to 99.6; Jeffreys 36.5 to
100.0; Haldane improper. Haldane's beta(0, 0) with no vaccine cases gives beta(0, 5), whose integral diverges at θ = 0.
Jeffreys' first parameter, ½, puts the most prior mass near θ = 0, which is VE near 100%, so its lower limit is
highest; the trial's 0.700102 comes next. Senn's beta(1, 1.428363) and the uniform share a first parameter of 1, and
Senn's larger second parameter tilts the prior towards small θ, so its lower limit is the higher of the two. With zero
events the prior decides the interval.

</details>

### E4 — Diagnose: one decimal off the published interval

Run `python bayes.py pfizer --quick --fault --out fault.json`. The stage's efficacy map is an earlier draft, and all
three published credible intervals now mismatch: the primary endpoint's lower limit prints 90.4 instead of 90.3, and
the severe-case interval −123.1 to 96.3 instead of −124.8 to 96.3. The posteriors are unchanged. Name the symptom, the
cause, the one printed line that proves it, and the fix, then check that the fix holds.

**Self-check:** the cause is in how the draft maps θ to VE, the proof is a printed line, and after the fix all three
intervals match again.

<details><summary>Answer</summary>

- **Symptom:** every interval shifts slightly, most at the low end of the severe-case interval, where the map is
  steepest.
- **Cause:** the draft maps θ to VE as if both groups had been followed for the same time, VE = 1 − θ/(1 − θ), with r
  set to 1 rather than the ratio of surveillance times. The trial's intervals are "adjusted for the surveillance time".
- **Proof:** the line `theta at VE 30% under the efficacy map 0.411765` for every endpoint. That is 0.7/1.7, the
  value at r = 1, while each endpoint prints its own ratio on the same line (0.996400, 0.994456, 0.992384), which
  should give 0.410891, 0.410419 and 0.409914.
- **Fix:** use VE = 1 − θ/((1 − θ) r) with r = vaccine surveillance time over placebo, as the stage does without
  `--fault`. Rerun without `--fault`: 90.3 to 97.6, 89.9 to 97.3 and −124.8 to 96.3, all matching. Nothing on disk
  changed except `fault.json`.

</details>

## Safety and cleanup

- `bayes.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection. It never
  overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json e3.json fault.json
```
