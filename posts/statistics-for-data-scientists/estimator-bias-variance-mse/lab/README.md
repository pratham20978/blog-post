# Lab — Estimators and Their Errors: Why the Best One Can Be Biased

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-28 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1; `estimators.py` 453f0b844e69, root seed 20261028. The notebook was built and executed with the same pins. The author also checked every exact value privately against R 4.5.2 (the tank moments by summing `choose()`, c₄, the divisor MSEs, both Efron–Morris calculations and the James–Stein risk): they agree to within 4 × 10⁻¹¹, except the risk at the batters' spread, 7 × 10⁻⁶ apart because the lab rounds that spread to four decimals (the `author_crosscheck_r` key in `captures.json`).

This lab reproduces every number the article calls measured. It simulates the German tank problem, five
tanks captured from 342, and sets each estimator's simulated bias, standard deviation and mean squared error
(MSE) beside its exact value; it rebuilds the minimum-variance unbiased estimator from 2 × mean − 1 by
conditioning on the largest serial; it follows the errors as more tanks are captured; it compares the
variance divisors n − 1, n and n + 1 on three populations; it recomputes both of Efron and Morris's published
James–Stein comparisons from their 1970 table and replays that season 200,000 times; and it computes James–
Stein's exact risk for 18 means. The one entry point is `estimators.py`; it prints its numbers and writes
them to the file you name with `--out`. Every simulated quantity is printed as estimate ± its Monte Carlo
standard error (MCSE), with the number of replications R.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `estimators.py` | G1 | yes | the five stages: `tanks`, `consistency`, `divisors`, `baseball`, `stein` |
| `data/efron_morris_1975_batting.csv` | — | — | the 18 players of 1970: hits in their first 45 at-bats, at-bats and average for the rest of the season, transcribed from Efron and Morris's 1975 Table 1 with provenance |
| `data/ruggles_brodie_1947_tanks.csv` | — | — | three months of German tank production: intelligence, serial-number and recorded figures, as reproduced from Ruggles and Brodie (1947) |
| `requirements.txt` | — | — | the two pinned dependencies, NumPy and SciPy |
| `captures.json` | — | — | the author's full run, machine-readable; every figure in the article reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; every run peaked at 0.13 GB of RAM |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4 and SciPy 1.18.1: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python estimators.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 180 MB; on the build machine `all --quick` took 2.7 s and `all` 12.6 s, 5.4 s of it in the `consistency` stage |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python estimators.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python estimators.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the two CSV files in a folder named `data`
beside `estimators.py`. Each stage also runs alone, for example `python estimators.py tanks --quick --out
mine.json`. `--quick` cuts every simulation to a tenth of its replications. Four flags exist for the
exercises: `--k` and `--N` change the tank problem (defaults 5 and 342), `--n` the sample size of the divisor
study (default 10), and `--fault` swaps in an earlier draft of one helper (E4).

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `tanks`, R = 1,000,000: the worked capture is 58, 171, 272, 273 and 303; the MLE's bias is −56.22 ± 0.05
  (exact −56.17), the MVUE's −0.07 ± 0.06 (exact 0); MSEs 5,456 ± 9 and 3,305 ± 6 (exact 5,448.2 and
  3,302.6); MSE ratio MLE/MVUE 1.6508 ± 0.0013 (exact 1.6497); m(k + 2)/(k + 1) − 1 over the MVUE 0.9731 ±
  0.0003 (exact 0.9727); the MVUE is closer than the MLE in 62.06% ± 0.05 of captures; Var(2 × mean − 1) /
  Var(MVUE) = 2.3305 ± 0.0035 (exact 7/3), and the conditional means lie on a line with slope 1.2004 ±
  0.0014 and intercept −1.10 ± 0.40. Then Ruggles and Brodie's three months.
- `consistency`, R = 200,000 per k: exact RMSE for k = 1 to 100 with simulated checks at six values of k;
  from k = 10 to 100 the MVUE's RMSE falls 10.8-fold and that of 2 × mean − 1 3.7-fold, while 2 × one tank
  − 1 stays at 197.5.
- `divisors`, R = 1,000,000 per population, n = 10: MSE 0.2219 ± 0.0004, 0.1899 ± 0.0003 and 0.1818 ±
  0.0002 for divisors 9, 10 and 11 on normal data (exact 0.2222, 0.1900, 0.1818); best divisors 11.00, 9.92
  and 16.40 for normal, uniform and exponential data (simulated 10.99 ± 0.01, 9.92 ± 0.00, 16.41 ± 0.04);
  E(s)/σ for normal data at n = 2 to 100 against c₄.
- `baseball`: raw scale c = 0.2117, total squared errors 0.0753 and 0.0213, ratio 3.535, James–Stein closer
  for 16 of 18; arcsine scale 17.571 and 4.999, efficiency 3.515, closer for 15; the replay, R = 200,000:
  James–Stein smaller in 96.25% ± 0.04 of seasons, efficiency 2.658 ± 0.002 (positive part 2.827 ± 0.002).
- `stein`, R = 100,000 per point: total risk of James–Stein for 18 means from 3.008 ± 0.012 at zero spread
  (exact 3) to 17.151 ± 0.020 at spread 256 (exact 17.164), and 6.811 ± 0.010 at the batters' spread
  (exact 6.812).

Everything is deterministic. Exact values (the tank moments, c₄, the divisor MSEs, the Efron–Morris
recomputations, the James–Stein risk) match to every printed digit on any machine. Simulated values repeat
exactly with NumPy 2.5.4 and the default seed; another NumPy version may draw different streams and move each
simulated value by a few of its MCSEs. A `--quick` run uses the same streams but fewer draws, so it matches
`captures-quick.json` exactly and `captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden
below it. This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: the tank table

Run `python estimators.py tanks --quick --out mine.json`. Compare the table it prints with the article's table
of bias, SD, MSE and RMSE, and with `captures-quick.json`.

**Self-check:** the exact columns read −56.17, 0.00 and −9.53 for the biases and 5448.2, 3302.6 and 3212.4
for the MSEs on any machine; every simulated bias lies within three of its MCSEs of the exact value; the
quick numbers match `captures-quick.json` digit for digit (with NumPy 2.5.4); your output starts with the
provenance line.

<details><summary>Answer</summary>

The author's quick run, R = 100,000: MLE bias −56.18 ± 0.15, MSE 5,449 ± 27; MVUE −0.02 ± 0.18, 3,302 ± 19;
m(k + 2)/(k + 1) − 1, −9.55 ± 0.18, 3,212 ± 20; MSE ratio MLE/MVUE 1.6505 ± 0.0033. If the exact columns
differ, the script was edited; if only the simulated values differ, your NumPy draws different streams, and
they should still sit within a few MCSEs of the exact values.

</details>

### E2 — Inspect: does James–Stein hurt any player on average?

The article says James–Stein lowers the total squared error, not every player's, and in the real 1970 season
it moved two players further from the truth. Before you look, predict: in the replay, where each player's
true average is his rest-of-season average, does any player's own expected squared error go up? If none
does, which player gains least, and why? Then read `baseball` → `replay` → `mse_y`, `mse_z` and
`players_hurt` in `mine.json` (run `python estimators.py baseball --quick --out mine.json` first), with
`players` for the names.

**Self-check:** you can name the player with the largest ratio `mse_z / mse_y` and give the reason from the
article's account of shrinkage; your prediction about `players_hurt` is right or you can say what it missed.

<details><summary>Answer</summary>

`players_hurt` is empty: in expectation James–Stein lowers every player's own squared error here. Clemente
gains least, with ratio 0.909 (Alvis 0.856, Alvarado 0.657); Kessinger gains most, 0.205. Shrinking pulls
every player toward 0.265, which costs most for the player whose true average sits furthest from it, Clemente
at 0.346. None is hurt because the true averages vary less than the noise in 45 at-bats (0.58 noise SDs on
the arcsine scale), so the pull is right for everyone on average. The two players hurt in 1970 were hurt by
that season's luck, not in expectation; a true average far from the others, such as a 0.400 hitter in this
group, would be hurt in expectation.

</details>

### E3 — Predict: more tanks, or another population

Pick one or both. Write each prediction down, with its reason, before you run.

1. Capture 20 tanks instead of 5: `python estimators.py tanks --quick --k 20 --out k20.json`. Predict the
   MLE's bias and whether the MSE ratio MLE/MVUE moves toward 1 or away from it.
2. Samples of 30 instead of 10: `python estimators.py divisors --quick --n 30 --out n30.json`. Predict the
   best divisor for exponential data from the article's formula d = n + 1 + (n − 1)κ/n.

**Self-check:** the bias within 0.2 tanks of your prediction and the ratio's direction right, for the reason
that the MLE's bias shrinks no faster than the MVUE's whole MSE; the divisor within 0.5 of your prediction,
for the reason that heavy tails inflate the variance of s².

<details><summary>Answer</summary>

1. The bias is (k − N)/(k + 1) = −322/21 = −15.33 (simulated −15.40 ± 0.05). The ratio moves away from 1, to
   1.8421 ± 0.0045 (exact 1.8437), toward 2k/(k + 1) = 1.90 for a very large N: the MLE's squared bias and
   the MVUE's variance both shrink like 1/k², so the MLE stays about twice as bad.
2. d = 31 + 29 × 6/30 = 36.8; simulated 36.90 ± 0.08. Dividing by 36.8 gives an MSE 21% below dividing by
   29 (exact ratio 0.788), against 45% at n = 10: the tails matter less as n grows, but n + 1 is still not
   the best divisor.

</details>

### E4 — Diagnose: an unbiased estimator that reports a bias

Run `python estimators.py tanks --quick --fault --out fault.json`. The MVUE, which equation (2) of the article
proves unbiased, now reports a bias of −1.22 ± 0.18 tanks, almost seven MCSEs from zero, and the MSE ratio
reads 1.6841 against an exact 1.6497. One helper in this stage is an earlier draft. Name the symptom, the
cause, the one printed line that proves it, and the fix, then check that the fix holds.

**Self-check:** the cause is in how the serial numbers are drawn, the proof is a printed line about those
numbers plus one estimator that stays unbiased, and after the fix the MVUE's bias is within two MCSEs of zero.

<details><summary>Answer</summary>

- **Symptom:** every estimator built from the maximum or the mean is shifted down: the MLE by −57.18 instead
  of −56.17, the MVUE by −1.22, 2 × mean − 1 by −1.91; and the MLE never equals N (0.00% of captures, against
  an exact 1.46%).
- **Cause:** `capture` with `fault=True` draws each serial with `rng.integers(0, j)`, which gives 0 to j − 1,
  not 1 to j. The simulated tanks are numbered 0 to 341, so N is one too small for every rule that assumes
  numbering from 1, and the MVUE's bias is −(1 + 1/k) = −1.2.
- **Proof:** the line `serial numbers drawn ran from 0 to 341`, and the spread estimator,
  (max − min)(1 + 2/(k − 1)) − 1, which does not depend on where numbering starts, still reports a bias of
  −0.21 ± 0.29.
- **Fix:** draw from 1 to j, `rng.integers(1, j + 1)`, as the shipped helper does; the line then reads 1 to
  342 and the MVUE's bias returns to −0.02 ± 0.18. With real serial numbers whose first value is unknown, the
  fix is the other way round: use the spread estimator, which the article names under Limitations.

</details>

## Safety and cleanup

- `estimators.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection.
  It never overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json k20.json n30.json fault.json
```
