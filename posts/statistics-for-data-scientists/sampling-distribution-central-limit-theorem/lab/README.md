# Lab — The Sampling Distribution: The CLT and Where n = 30 Fails

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-26 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1; `sampling.py` f73eec698b31, root seed 20261026. The notebook was built and executed with the same pins. The author also checked the population's moments, Student's t-test and every t critical value privately against R 4.5.2: they agree to within 5 × 10⁻¹¹ (the `author_crosscheck_r` key in `captures.json`).

This lab reproduces every number the article calls measured. It treats the net spend of 4,317 customers of
an online retailer as a population, draws samples from it with replacement, and measures how the sample
mean's sampling distribution, its standard error and a 5% t-test behave as n grows from 10 to 10,000. It
then runs the same t-test on seven populations of known skewness, reruns Student's 1908 example, computes the
exact distance to the normal that the Berry–Esseen inequality bounds, breaks the central limit theorem's
finite-variance condition with a Cauchy and a Pareto, and measures Monte Carlo error itself. The one entry
point is `sampling.py`; it prints its numbers and writes them to the file you name with `--out`. Every
simulated rate is printed as estimate ± its Monte Carlo standard error (MCSE), with the number of
replications R.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `sampling.py` | G1 | yes | the seven stages: `population`, `sampling`, `skewness`, `student`, `berry`, `heavy`, `replications` |
| `derive_spend.py` | G1 | yes | rebuilds the spend file from UCI's public archive, checked by SHA-256; standard library only; optional |
| `data/online_retail_customer_spend.csv` | — | — | net spend of the 4,317 customers, with source, licence (CC BY 4.0) and the derivation rule in its header |
| `data/student1908_sleep.csv` | — | — | Student's ten patients, as printed in his 1908 paper; identical to R's `datasets::sleep` |
| `requirements.txt` | — | — | the two pinned dependencies, NumPy and SciPy |
| `captures.json` | — | — | the author's full run, machine-readable; every figure in the article reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.3 GB of RAM, the E4 fault run at 0.5 GB |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4 and SciPy 1.18.1: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python sampling.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 180 MB; `all --quick` took 98 s and `all` 210 s on the build machine, 76 to 79 s of each in the exact Berry–Esseen distances, which `--quick` does not shorten; `derive_spend.py` needs the 23.7 MB UCI archive and takes about 30 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python sampling.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python sampling.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the two CSV files in a folder named `data`
beside `sampling.py`. Each stage also runs alone, for example `python sampling.py sampling --quick --out
mine.json`. `--quick` cuts every simulation to a fifth of its replications or fewer. Two flags exist for the
exercises: `--cap 0.99` caps spend at its 99th percentile (E3), and `--fault` swaps in an earlier draft of
one helper (E4). To rebuild the spend file from the source, download `online+retail.zip` from
https://archive.ics.uci.edu/dataset/352/online+retail and run `python derive_spend.py online+retail.zip --out
check.csv`; it must match `data/online_retail_customer_spend.csv` byte for byte.

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `population`: 4,317 customers, total £8,313,294.95; mean 1,925.71, median 658.26, SD 8,266.70 (divisor
  N); skewness 21.582, E|X − μ|³/σ³ = 21.590, excess kurtosis 599.6; 79.1% of customers below the mean;
  the top 1% (43 customers) hold 29.7% of all spend.
- `sampling`, R = 100,000 per n: the simulated SE matches σ/√n at every n (0.993 ± 0.007 at n = 30); the
  one-sided 5% t-test rejects the true mean 39.82% ± 0.15 (lower) and 0.05% ± 0.01 (upper) at n = 30,
  17.69% ± 0.12 and 0.94% ± 0.03 at n = 1,000, and 7.86% ± 0.09 and 2.99% ± 0.05 at n = 10,000. At n = 30
  the median s is 0.256 σ and corr(mean, s) is 0.972; 25.9% of samples hold one of the 43 biggest customers.
- `skewness`, R = 100,000 per point: lower/upper rates at n = 30 run from 4.93/4.98% (normal) through
  9.84/2.26% (exponential) to 15.44/0.98% (standard lognormal); the lognormal's two-sided rate is 11.71% ±
  0.10 at n = 30.
- `student`: t = 4.0621 for the sleep data (Student's z 1.3540 = t/3), one-sided P 0.001416; with normal
  data at n = 10, the 1.96 cutoff rejects 8.14% ± 0.03 (exact 8.16%) and the t cutoff 4.98% ± 0.02.
- `berry`: the inversion agrees with the exponential's exact gamma CDF to 1.3 × 10⁻¹¹; the exact distance
  reaches 0.01 at n = 20,652 for the spend and 177 for the exponential, against Berry–Esseen guarantees from
  1,025,322 and 12,824.
- `heavy`: the interquartile range of a Cauchy mean stays at 2.00 for n = 1 to 1,000; the Pareto (tail
  index 1.5) lower-tail rate falls from 42.59% at n = 10 to 26.43% at n = 10,000 and is 26.40% ± 0.99 at
  n = 100,000.
- `replications`: R for a target MCSE, and the lognormal's two-sided rate at n = 30 as 11.70% ± 0.02 from
  R = 2,000,000, with 500 reruns at R = 5,000 spread from 0.1018 to 0.1364.

Everything is deterministic. Exact results (the population, Student's numbers, Berry–Esseen, the critical
values) match to every printed digit on any machine. Simulated results repeat exactly with NumPy 2.5.4 and
the default seed; another NumPy version may draw different streams and move each simulated value by a few of
its MCSEs. A `--quick` run uses the same streams but fewer draws, so it matches `captures-quick.json` exactly
and `captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden
below it. This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: the population and the two tails at n = 30

Run `python sampling.py population --out mine.json` and `python sampling.py sampling --quick --out
mine.json`. Compare the population's mean, SD and skewness with the article, and the n = 30 line of the
sampling table with `captures-quick.json` and with the article's full-budget 39.82% and 0.05%.

**Self-check:** the population line reads mean 1,925.71, SD 8,266.70, skewness 21.582 on any machine; the
quick n = 30 rates match `captures-quick.json` digit for digit (with NumPy 2.5.4) and the full-budget rates
within three of the quick run's MCSEs; your output starts with the provenance line.

<details><summary>Answer</summary>

The author's quick run: at n = 30, lower 40.62% ± 0.49, upper 0.07% ± 0.03, two-sided 35.13% ± 0.48, against
the full budget's 39.82%, 0.05% and 34.41%. The differences are 1.6, 0.7 and 1.5 quick MCSEs. If the
population line differs, the CSV was edited or read without its header lines skipped; if only the simulated
rates differ, your NumPy draws different streams, and the rates should still agree within a few MCSEs.

</details>

### E2 — Inspect: why the lower tail fires

The article says samples of 30 that miss the 43 biggest customers have a low mean and a small s together.
Before you look, write down two predictions: is the typical sample SD at n = 30 above or below σ = £8,266.70,
and by roughly how much? Then read `sampling` → `by_n` → `30` in `mine.json`: `s_over_sigma_quantiles`,
`p_s_below_sigma`, `corr_mean_sd` and `top1`.

**Self-check:** the median of s/σ is far below 1, s < σ in most samples, the correlation of mean and s is
above 0.9, and the lower tail rejects about half of the samples without a big customer and none of the rest.

<details><summary>Answer</summary>

The author's quick run: median s/σ 0.253, so the typical estimated SE is a quarter of the true one; s < σ in
88.2% ± 0.3 of samples, although s²/σ² averages 1.033 ± 0.047 (s² is unbiased, s is not typical);
correlation 0.975. 25.2% ± 0.4 of samples hold one of the 43 biggest customers (25.9% exactly); the other
74.8% have a mean below μ 92.4% of the time and are rejected by the lower-tail test 54.3% ± 0.6 of the time,
while none of those holding a big customer is rejected. A low mean over a small SE gives a very negative t.

</details>

### E3 — Predict: cap the biggest customers

`--cap 0.99` replaces every spend above the 99th percentile (£17,506.69) by that value, a common way to tame
revenue metrics. First run `python sampling.py population --cap 0.99 --out capped.json` and read the capped
skewness. Then predict the lower-tail rejection rate at n = 1,000 from the article's first-order rule, 5% +
11.02 points × γ/√n, before you run `python sampling.py sampling --quick --cap 0.99 --out capped.json`.

**Self-check:** your prediction is within one point of the measured rate, for the reason that the error
scales with γ/√n; and you can say what the capped mean estimates.

<details><summary>Answer</summary>

The capped skewness is 4.017, so the rule predicts 5% + 11.02 × 4.017/√1,000 = 6.40%. The author's quick run
measures 6.69% ± 0.25 at n = 1,000 (upper tail 3.65% ± 0.19), against 17.64% ± 0.38 before capping. The
capped population's mean is £1,528.79, not £1,925.71: the test now behaves, but it tests a different
quantity, the mean of capped spend, which is 21% lower. Capping trades a tail error for an estimand you have
to defend.

</details>

### E4 — Diagnose: a standard error that shrinks too fast

Run `python sampling.py sampling --quick --fault --out fault.json`. The SE column, which should read about
1.000 at every n, now falls as n grows: 0.866 at n = 1,000, 0.549 at n = 3,000 and 0.000 at n = 10,000,
where no sample mean differs from μ at all. One helper in this stage is an earlier draft. Name the symptom,
the cause, the one printed number that proves it, and the fix, then check that the fix holds.

**Self-check:** the cause is the sampling design, the proof is a printed ratio that matches a formula in N
and n, and after the fix the ratio is 1 within its MCSE at every n.

<details><summary>Answer</summary>

- **Symptom:** the simulated SE falls below σ/√n, more as n grows, and at n = 10,000 every "sample" has
  mean exactly μ. The t-test turns conservative: the lower tail rejects 2.39% at n = 3,000.
- **Cause:** `draw_customers` with `fault=True` shuffles the 4,317 customers and takes the first n, which is
  sampling without replacement. Draws are then dependent: the N values sum to a constant, so any two draws
  have covariance −σ²/(N − 1), and the variance of the mean shrinks by (N − n)/(N − 1). For n above N the
  slice silently returns the whole population.
- **Proof:** the printed ratios match √((N − n)/(N − 1)): 0.866 ± 0.006 against 0.877 at n = 1,000, and
  0.549 ± 0.004 against 0.552 at n = 3,000.
- **Fix:** draw indices with replacement, as the shipped helper does,
  `pop[rng.integers(0, len(pop), size=shape)]`, or, if sampling without replacement is the real design,
  multiply σ/√n by √((N − n)/(N − 1)). Check it by running without `--fault`: the ratios return to 1.000
  within their MCSEs (0.991 ± 0.008 at n = 1,000 on the quick budget).

</details>

## Safety and cleanup

- `sampling.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection.
  It never overwrites `captures.json` unless you leave out `--out`. `derive_spend.py` reads the archive you
  pass and writes one CSV and a temporary copy of the workbook, which it deletes.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json capped.json fault.json check.csv
```
