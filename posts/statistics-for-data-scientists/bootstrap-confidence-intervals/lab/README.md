# Lab — The Bootstrap: From Percentile to BCa, and Where It Breaks

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-11-01 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1; `bootstrap.py` e3a939a03bc4, root seed 20261101. `crosscheck.R` ran under R 4.5.2 with boot 1.3.32 (R seed 20261101, 2,000 replicates) and wrote `crosscheck-r.csv`, which ships, so the R comparison runs without R. The notebook was built and executed with the same Python pins.

This lab reproduces every number the article calls computed or measured. It bootstraps the correlation of LSAT and
GPA in 15 law schools by hand, printing each intermediate of seven 95% intervals (percentile, basic, studentized
on two scales, BCa with its bias correction z0 and acceleration a, the normal interval with a bootstrap standard
error, and Fisher's normal-theory z interval), and matches them to `scipy.stats.bootstrap` on the same resamples
and to R's `boot.ci` on R's own replicates. Because the 82 schools the sample came from are published, it measures
each interval's actual coverage by drawing fresh samples of 15 from them. It then measures the same intervals for
mean customer spend, the skewed case of part 6, and demonstrates three failures: the sample maximum, the mean of
infinite-variance data, and an autocorrelated series. The one entry point is `bootstrap.py`; it prints its numbers
and writes them to the file you name with `--out`. Every simulated quantity is printed as estimate ± its Monte Carlo
standard error (MCSE).

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `bootstrap.py` | G1 | yes | the seven stages: `example`, `reconcile`, `coverage`, `spend`, `maximum`, `heavy`, `dependent` |
| `crosscheck.R` | G1 | yes | optional: the same bootstrap in R's `boot` package; writes `crosscheck-r.csv` |
| `crosscheck-r.csv` | — | — | R's output: its seven intervals, z0, two accelerations, influence values and all 2,000 replicates |
| `data/law_school_82.csv` | — | — | the 82 law schools and the 15-school sample (package `bootstrap` 2019.6, BSD 3-clause, notice inside) |
| `data/online_retail_customer_spend.csv` | — | — | net spend of 4,317 customers (UCI Online Retail, CC BY 4.0), with provenance |
| `requirements.txt` | — | — | the two pinned dependencies: NumPy and SciPy |
| `captures.json` | — | — | the author's full run, machine-readable; every figure in the article reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.46 GB of RAM, `--quick` at 0.42 GB |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4 and SciPy 1.18.1: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python bootstrap.py all --quick`. Optional: R with its recommended package `boot` for `crosscheck.R` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 170 MB; on the build machine `all --quick` took 23 s and `all` 3.5 minutes |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python bootstrap.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python bootstrap.py all --out full.json             # the article's budget
Rscript crosscheck.R                                # optional; rewrites crosscheck-r.csv with the same numbers
```

If you download the files one by one rather than as the zip, put the two CSV files in a folder named `data` beside
`bootstrap.py`. Each stage also runs alone, for example `python bootstrap.py maximum --out mine.json`. `--quick`
cuts every simulation to a tenth of its samples but keeps the worked example's 10,000 replicates, so the `example`
and `reconcile` stages print the article's numbers on either budget. Three flags exist for the exercises: `--drop`
leaves one school out of the worked example (E3), `--fault` swaps in an earlier draft of its resampler (E4), and
`--n` sets the sample size the `coverage` stage draws from the 82 schools.

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `example`: r = 0.776374 for the 15 schools, against 0.759998 for all 82. The first resample draws 11 distinct
  schools and gives r* = 0.7195. Over 10,000 replicates the bootstrap standard error is 0.1353, against 0.1147 from
  normal theory and 0.1296 for the true sampling distribution (a million samples of 15 from the 82); 4,630
  replicates lie below r, so z0 = −0.0929; the jackknife gives a = −0.07567, and BCa reads the 0.581% and 93.859%
  points. The seven intervals: normal 0.5112 to 1.0416, percentile 0.4523 to 0.9624, basic 0.5904 to 1.1004,
  studentized −0.4624 to 0.9971, studentized on Fisher's scale −0.1421 to 0.9455, BCa 0.3273 to 0.9421, Fisher z
  0.4385 to 0.9220. Rerun 200 times, the BCa lower limit moves with SD 0.0261 at B = 2,000 and 0.0115 at 10,000.
- `reconcile`: on SciPy's own resamples the from-scratch percentile, basic and BCa limits equal
  `scipy.stats.bootstrap`'s to 2.2 × 10⁻¹⁶. From R's 2,000 replicates the lab recomputes all seven of `boot.ci`'s
  limits to 3.9 × 10⁻¹⁵, including its BCa with the acceleration from regression (−0.08655) and from the jackknife
  (−0.07409). On one set of replicates the four BCa conventions in circulation give lower limits from 0.3493 to
  0.3551.
- `coverage`: 20,000 samples of 15 from the 82 schools, 2,000 replicates each: normal 89.0%, percentile 91.0%,
  basic 80.7%, studentized 95.7% (with an upper limit above 1 in 23.5% of samples), studentized on Fisher's scale
  93.8%, BCa 92.0% and Fisher z 93.6%, each ± 0.1 to 0.3.
- `spend`: at n = 30 the t-interval for mean spend covers 66.0%, the percentile interval 66.8%, BCa 73.3% and the
  studentized (bootstrap-t) 80.3%, ± 0.3; 26.4% of samples contain one of the 44 customers spending £17,507 or more,
  and BCa covers 97.0% of those and 64.8% of the rest. At n = 100: 70.1%, 72.0%, 77.0% and 80.3%.
- `maximum`: for the five tank serials 58, 171, 272, 273 and 303, the bootstrap maximum equals 303 with probability
  0.67232 exactly; the percentile interval for N is 272 to 303 and BCa's 171 to 303 or 273 to 303, depending on
  how z0 counts ties, while the exact bound from the distribution of the maximum is 549. Over all captures of five
  tanks the percentile and BCa intervals cover N = 342 only when tank 342 is caught (1.46%), the basic interval
  75.73%. For uniform samples the point mass is 0.6340 at n = 100, and the basic interval covers 87.5% ± 0.1.
- `heavy`: for Pareto data with tail index 1.5, BCa covers the mean 73.2% at n = 30 and 83.6% at n = 1,000; the
  studentized interval 80.8% and 84.8%. Three samples of 100 give bootstrap distributions made of lumps, one per
  number of copies of the largest value drawn.
- `dependent`: for an AR(1) series with φ = 0.5 and n = 200, resampling single observations gives a standard error
  0.574 times the true 0.1409, the lag-1 autocorrelation falls from 0.487 to −0.005, and the percentile interval
  covers 73.5% ± 0.7.

Everything exact or computed matches to every printed digit on any machine. Simulated values repeat exactly with
NumPy 2.5.4 and the default seed; another NumPy may draw different streams and move each simulated value by a few of
its MCSEs. A `--quick` run uses the same streams with fewer samples, so it matches `captures-quick.json` exactly and
`captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden below it.
This is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: the worked example, both reconciliations and one coverage

Run `python bootstrap.py all --quick --out mine.json` and compare `mine.json` with `captures-quick.json`. Then find
in your output the bootstrap standard error, z0, a and the BCa interval of the worked example, the two largest
differences printed by `reconcile`, and BCa's coverage on the 82 schools.

**Self-check:** your provenance line prints NumPy 2.5.4 and SciPy 1.18.1; the worked example matches the article to
the digit (0.1353, −0.0929, −0.07567, 0.3273 to 0.9421); both reconciliation differences are below 10⁻¹²; and BCa's
coverage lies within two of its MCSEs of the article's 92.0%.

<details><summary>Answer</summary>

The worked example does not depend on the budget: SE 0.1353, z0 −0.0929, a −0.07567, BCa 0.3273 to 0.9421. The
reconciliation differences are 2.2 × 10⁻¹⁶ (SciPy) and 3.9 × 10⁻¹⁵ (R). The author's quick run gives BCa coverage
91.0% ± 0.6 on 2,000 samples, against 92.0% ± 0.2 on 20,000: within two quick MCSEs. If the worked example differs,
check the versions first, then the data: their hashes are in the `data_sha1` field of the provenance.

</details>

### E2 — Inspect: which school sets the acceleration

The acceleration a = −0.07567 comes from the 15 leave-one-out correlations, which `captures.json` holds under
`example.jackknife`, in the order of `example.schools`. Before you look, use the article's scatter of the 15 schools
to name the school you expect to move r most when it is left out, and say which way. Then compute a by hand from the
15 values, and the share of the numerator Σd³ that comes from that one school.

**Self-check:** you named the school and the direction; your a equals −0.0757; you found one school's share of Σd³.

<details><summary>Answer</summary>

School 6 (LSAT 576, GPA 3.39), with the third-highest GPA and the sixth-lowest LSAT: a high GPA for its LSAT puts it
far above the line the other 14 follow, so leaving it out raises r from 0.7764 to 0.8929. With d = (jackknife mean) − (leave-one-out
value) and the jackknife mean 0.7759, Σd² = 0.02176 and Σd³ = −0.001458, so a = −0.001458 / (6 × 0.02176^1.5) =
−0.0757 (−0.07567 from the unrounded sums). School 6 alone has d = −0.1170 and d³ = −0.001603: 110% of Σd³, because the
other schools' terms partly cancel, and 63% of Σd². One observation out of 15 sets both the sign and the size of the acceleration.

</details>

### E3 — Predict: the sample without school 6

Run `python bootstrap.py example --quick --drop 6 --out e3.json`. Before you run it, write down what happens to r, to
the bootstrap standard error (larger or smaller, and roughly by how much), to the acceleration, and to the gap
between the BCa and percentile intervals.

**Self-check:** r, the direction and rough size of the standard error's change, a moving toward zero, and the BCa
interval closer to the percentile one, for the reason E2 gives.

<details><summary>Answer</summary>

r rises to 0.8929, the leave-one-out value E2 printed. The bootstrap standard error falls from 0.1353 to 0.0611, less
than half: the remaining 14 schools lie close to a line, and a correlation near 1 has little room to vary. The
acceleration shrinks from −0.07567 to −0.02629, because the school that supplied 110% of Σd³ is gone, and z0 stays
near −0.1 (−0.0954). BCa now reads the 1.166% and 95.372% points instead of 0.581% and 93.859%, and its interval,
0.7140 to 0.9704, sits much closer to the percentile interval, 0.7492 to 0.9768, than the full sample's 0.3273 to
0.9421 sat to 0.4523 to 0.9624.

</details>

### E4 — Diagnose: an interval that excludes its own estimate

Run `python bootstrap.py example --quick --fault --out fault.json`. The worked example's numbers change completely:
the 95% percentile interval no longer contains r = 0.776, and BCa returns an interval of width 0.001. The stage's
resampler is an earlier draft. Name the symptom, the cause, the one printed line that proves it, and the fix, then
check that the fix holds.

**Self-check:** the cause is in how the draft forms each resample, the proof is a printed line from the first
resample, and after the fix the percentile interval is 0.4523 to 0.9624 again.

<details><summary>Answer</summary>

- **Symptom:** the replicates average −0.0005 instead of about 0.77, the bootstrap standard error is 0.2666, and the
  percentile interval runs from −0.5198 to 0.5172, excluding the estimate it was built around. 9,994 of 10,000
  replicates lie below r, so z0 = +3.2389 and BCa reads the 99.999% and 100.000% points, an interval from 0.8331 to
  0.8342.
- **Cause:** the draft draws the rows for LSAT and the rows for GPA independently, so each resample pairs one
  school's LSAT with another school's GPA. That samples from the product of the two marginal distributions, in which
  the correlation is 0: the resampling destroyed the dependence the statistic measures. It is the same failure as
  resampling single observations of a time series, in one dimension instead of over time.
- **Proof:** the two lines `first resample, rows drawn for LSAT: [...]` and `rows drawn for GPA: [...]` print
  different row numbers. In a correct bootstrap they are the same list.
- **Fix:** draw one index array per resample and use it for both columns, as the stage does without `--fault`
  (`idx_y = idx`). Edit the draft that way and rerun the same command: the two lines match and the percentile interval
  is 0.4523 to 0.9624. Nothing on disk changed except `fault.json`, so a run without `--fault` is the original lab.

</details>

### E5 — Extend: the m-out-of-n bootstrap for an upper endpoint

The `maximum` stage shows that every interval built from percentiles of the ordinary bootstrap stops at the sample
maximum, so for a uniform population on 0 to θ it never covers θ. Resampling m < n observations repairs this when m
grows more slowly than n. Write a function that, for one sample of size n, draws B resamples of size m with
replacement, takes q as the 95% point of m(M − M*)/M over them, where M is the sample maximum and M* a resample's,
and returns the one-sided 95% upper bound M(1 + q/n) for θ. Then measure its coverage on fresh uniform samples.

**Self-check:** for n = 1,000, m = 50 and B = 2,000, over at least 1,000 samples: the share of resample maxima equal
to M is within 0.01 of 1 − (1 − 1/n)^m = 0.049, and the bound covers θ in 92% to 97% of samples; with m = n the same
code covers far less, near the 82% the author found.

<details><summary>Answer</summary>

The author's run of such a function, over 2,000 samples with B = 2,000: m = 50 covers 94.3% ± 0.5 with a point mass of
0.049; m = 31, about √n, covers 93.9%; m = 100 covers 93.2%; and m = n = 1,000 covers 81.8% with the familiar point
mass of 0.632. At n = 100 the repair is weaker: m = 10 covers 91.2%. The choice of m is the method's tuning problem;
Bickel, Götze and van Zwet (1997) discuss it.

</details>

## Safety and cleanup

- `bootstrap.py` reads only `data/` and `crosscheck-r.csv`, writes only the file named by `--out`, and opens no network
  connection. It never overwrites `captures.json` unless you leave out `--out`. `crosscheck.R` reads `data/` and
  writes only `crosscheck-r.csv`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json e3.json fault.json
```
