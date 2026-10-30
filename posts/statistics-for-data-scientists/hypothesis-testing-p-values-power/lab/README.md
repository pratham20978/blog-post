# Lab — p-Values and Power: How Wrong Can a Significant Result Be?

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-29 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `testing.py` 13b3a5154d33, root seed 20261029. The notebook was built and executed with the same pins. The author also checked the design analysis privately against Gelman and Carlin's own `retrodesign()` in R 4.5.2 (base R only): power and the type S rate agree to every printed digit, and over seeds 1 to 1,000 R's simulated exaggeration ratio for the 2013 design averages 9.5366 with SD 0.0608, against the closed form's 9.5366. R's `power.t.test(n = 16, delta = 1, strict = TRUE)` gives 0.781398, as here; its default, `strict = FALSE`, counts only the upper tail and gives 0.781397 (the `author_crosscheck` key in `captures.json`).

This lab reproduces every number the article calls measured. It treats the p-value as a random variable:
its distribution under the null and under alternatives, for a z statistic and for two-sample t-tests on
simulated data, 25 repeats of one experiment, and Cumming's interval for a replication's p-value. It
computes the power of the two-sample t-test four ways (one integral by hand, SciPy's noncentral t,
statsmodels, simulation), the sample sizes it implies, and "observed power". It ports Gelman and Carlin's
`retrodesign()` line for line and sets it beside the closed form for the two published studies they
analysed. It reads the Reproducibility Project's 100 coded replications from their CC0 data file. It
computes the false positive risk both ways, recomputing Ioannidis's table and Colquhoun's likelihood
ratios. It runs two one-sided tests (TOST) from first principles against statsmodels, with their size and
power. And it measures what testing after every observation does to a 5% test. The one entry point is
`testing.py`; it prints its numbers and writes them to the file you name with `--out`. Every simulated
quantity is printed as estimate ± its Monte Carlo standard error (MCSE), with the number of replications R.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `testing.py` | G1 | yes | the seven stages: `pvalues`, `power`, `retrodesign`, `replication`, `fpr`, `tost`, `stopping` |
| `data/osc2015_rpp_pairs.csv` | — | — | the Reproducibility Project's 100 coded replications (CC0 1.0), with provenance and the extraction rule |
| `requirements.txt` | — | — | the four pinned dependencies: NumPy, SciPy, statsmodels and pandas |
| `captures.json` | — | — | the author's full run, machine-readable, with the private cross-checks; every figure in the article reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.48 GB of RAM, `--quick` at 0.27 GB |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0 and pandas 3.1.0: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python testing.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 300 MB; on the build machine `all --quick` took 7.6 s and `all` 26.5 s |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python testing.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python testing.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the CSV file in a folder named `data`
beside `testing.py`. Each stage also runs alone, for example `python testing.py retrodesign --quick --out
mine.json`. `--quick` cuts every simulation to a tenth of its replications. Three flags exist for the
exercises: `--effect` and `--se` make the `retrodesign` stage analyse one design of your choosing instead of
the published cases, and `--fault` swaps in an earlier draft of the design-analysis simulation (E4).

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `pvalues`: with no effect, 4.98% ± 0.05 of 200,000 z-test p-values fall at or below .05 and the twenty
  bins pass a χ² check of uniformity (p = 0.546). At λ = 0.247, the 2013 design with a 2-point truth,
  5.69% ± 0.05 do (exact 5.70%) and the median p is 0.487. Pooled t-tests with 16 per group and a true
  difference of 1 SD reject 78.40% ± 0.13 of the time (exact 78.14%). Your by-hand t-test matches
  `scipy.stats.ttest_ind` to 4 × 10⁻¹⁷. Twenty-five repeats of that experiment give 19 significant results
  and p from 0.00007 to 0.33. Cumming's 80% interval after an original p = .05 runs from 0.000081 to
  0.4413, and 80.05% ± 0.24 of 28,439 simulated replications land inside it.
- `power`: the integral, SciPy's `nct`, statsmodels and the normal approximation give 0.781398, 0.781398,
  0.781398 and 0.807430 at d = 1 with 16 per group. Thirteen simulated designs sit within 2.3 MCSE of the
  exact curves. The smallest n per group for 80% power is 17, 26, 64 and 394 for d = 1, 0.8, 0.5 and 0.2.
  SciPy's `nct.cdf(-c, df, λ)` first returns NaN at n = 132 per group for d = 1 (λ 8.12), where statsmodels
  returns `nan`; the lab takes the lower tail as `nct.sf(c, df, -λ)` instead. Observed power is 0.500 at
  p = .05 and 0.249 at p = .2.
- `retrodesign`: for the 2013 design (true effect 2, SE 8.1), power 0.0570, type S 0.2396 and exaggeration
  9.5366 in closed form; 2,000 repeats of Gelman and Carlin's 10,000-draw simulation average 9.535 with SD
  0.059, and ten million draws give 9.5404 ± 0.0019. Kanazawa's design gives type S 0.4644, 0.3947 and
  0.1937 and exaggeration 76.69, 25.59 and 7.749 for true differences of 0.1, 0.3 and 1. A significant
  estimate from the 2013 design must exceed 15.876, 7.94 times the plausible effect.
- `replication`: 97 of the 100 originals and 36 of the replications are coded significant. On the 97 pairs
  with both effect sizes the mean r falls from 0.3962 to 0.1970; of the 63 non-significant replications, 2
  are equivalent to zero within |r| below 0.1 and 17 within 0.2.
- `fpr`: Ioannidis's Table 4 recomputes to his printed precision. In the 16-per-group design an observed
  p = .05 has likelihood ratio 2.757, so a false positive risk of 0.2662 at prior 0.5 and 0.7655 at prior
  0.1; p = .03 gives 4.996, 0.1668 and 0.6430. Simulated, 25.90% ± 0.44 of results between .045 and .05
  are false at prior 0.5.
- `tost`: the by-hand TOST matches `ttost_ind` exactly on both examples; with the truth on the bound it
  rejects 5.04% ± 0.07. Its power at ±0.5 SD with no true difference is 0.82% at 16 per group and 79.85% at
  69 (exact), and the narrowest bound it establishes with 80% power at 16 per group is ±1.059 SD.
- `stopping`: testing after every observation rejects a true null 8.31%, 14.17%, 19.33%, 37.36% and 52.99%
  of the time after 2, 5, 10, 100 and 1,000 looks, computed exactly; 100,000 simulated paths agree within
  2.1 MCSE. A t-test checked after every added pair from 10 to 100 per group rejects 28.5% ± 0.3, and
  testing at 20 per group then adding 10 rejects 7.77% ± 0.06.

Everything exact or computed matches to every printed digit on any machine; a different statsmodels or
SciPy may move the last digits of its own lines. Simulated values repeat exactly with NumPy 2.5.4 and the
default seed; another NumPy version may draw different streams and move each simulated value by a few of
its MCSEs. A `--quick` run uses the same streams but fewer draws, so it matches `captures-quick.json`
exactly and `captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden
below it. This is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: the design analysis and the false positive risk

Run `python testing.py all --quick --out mine.json` and compare `mine.json` with `captures-quick.json`. Then
find in your output the 2013 design's power, type S rate and exaggeration ratio, the false positive risk of
an observed p = .03 at priors 0.5 and 0.1, and the number of non-significant replications equivalent to zero
within 0.1 and 0.2.

**Self-check:** your provenance line prints NumPy 2.5.4 and SciPy 1.18.1, and the closed-form values match
the article exactly: 0.0570, 0.2396 and 9.5366; 0.1668 and 0.6430; 2 and 17.

<details><summary>Answer</summary>

The closed forms do not depend on the budget or the seed: power 0.0570 (0.0434 above the bar, 0.0137 below
it), type S 0.2396, exaggeration 9.5366; likelihood ratio 4.996 at p = .03, so risks of 0.1668 and 0.6430;
2 and 17 equivalent replications. The simulated values in the author's quick run are, for example, 7.77% for
"test at 20, add 10" and 28.75% for testing after every added pair, against 7.77% ± 0.06 and 28.5% ± 0.3 in
the full run.

</details>

### E2 — Inspect: what every significant estimate shares

The `retrodesign` stage keeps, for its largest simulation of each design, `min_abs_sig`, the smallest
magnitude among the significant estimates, and `share_sig_negative`, the share of them below zero. Before
you read the two values for `durante_2`, state the bound the first must respect and the value the second
should be near, and why.

**Self-check:** you named 1.96 × 8.1 = 15.876 as a floor that the smallest magnitude cannot go below, and the
closed-form type S rate, 0.2396, as the share's target within about two MCSEs.

<details><summary>Answer</summary>

`min_abs_sig` is 15.8757 in both the quick and the full run: a significant estimate has |estimate| above
1.959964 × 8.1 = 15.8757, and with a million draws one lands just above the bar. So every significant
estimate from this design exceeds the plausible 2-point effect at least 7.94 times, whatever the data.
`share_sig_negative` is 0.2375 in the quick run (one million draws, about 57,000 of them significant, MCSE
0.0018) and 0.2387 in the full run (ten million draws, MCSE 0.0006), against the exact 0.2396.

</details>

### E3 — Predict: twice the data

Rerun the design analysis for the 2013 design with twice the sample size, so the standard error falls to
8.1/√2 = 5.7276, keeping the true effect at 2: `python testing.py retrodesign --quick --se 5.7276 --out
e3.json`. Before you run it, write down whether power, the type S rate and the exaggeration ratio rise or
fall, and roughly how far.

**Self-check:** the direction of all three, and a reason from the article's model: they depend only on
λ = D/SE, and λ grows with the square root of the sample size.

<details><summary>Answer</summary>

λ rises from 0.247 to 0.349. Power rises only to 0.0641, the type S rate falls to 0.1633 and the exaggeration
ratio to 6.785; the bar falls to 1.96 × 5.7276 = 11.226, which is the smallest significant magnitude the run
prints. Doubling the data barely helps because the effect is an eighth of the noise; 80% power needs λ = 2.80,
a standard error of 0.714, about 129 times the original data.

</details>

### E4 — Diagnose: an exaggeration ratio that comes out too small

Run `python testing.py retrodesign --quick --fault --out fault.json`. The power and type S rates are the same
as in a correct run, and the closed-form exaggeration ratios have not moved, but every simulated exaggeration
ratio disagrees with them, some badly and one not at all. One helper in this stage is an earlier draft. Name
the symptom, the cause, the one printed line that proves it, and the fix, then check that the fix holds.

**Self-check:** the cause is in how the simulated estimates are summarised, the proof is a printed number that
equals the faulty ratio times the true effect, and after the fix the simulated ratios agree with the closed
form within a few MCSEs.

<details><summary>Answer</summary>

- **Symptom:** with `--fault`, a million draws give an exaggeration ratio of 5.71 for Kanazawa's 0.1-point
  design against the closed form's 76.69, and 5.10 for the 2013 design against 9.54, while the 80%-power
  design gives 1.125 either way.
- **Cause:** `exaggeration_draft` averages the significant estimates themselves, `estimate[significant].mean()`,
  instead of their magnitudes. Significant estimates with the wrong sign then subtract instead of adding, so
  the damage grows with the type S rate: none at 80% power, where no significant estimate has the wrong sign,
  and most for Kanazawa's design, where 46% do.
- **Proof:** the line `significant estimates: signed mean 10.198, mean magnitude 19.085, ...` for `durante_2`.
  The faulty ratio is the signed mean over the true effect, 10.198/2 = 5.10; the correct one is the mean
  magnitude over it, 19.085/2 = 9.54. Kanazawa's signed mean, 0.571, gives the faulty 5.71.
- **Fix:** take magnitudes, `np.abs(estimate[significant]).mean() / A`, which is `exaggeration_of`, as in
  Gelman and Carlin's R code, `mean(abs(estimate)[significant])`. Without `--fault` the million-draw values
  are 76.79, 9.543 and 1.1249, each within a few MCSEs of the closed form.

</details>

### E5 — Extend: a sequential test that keeps its 5%

Testing after every look inflates the error rate (the `stopping` stage). A group sequential design instead
raises the bar: with K equally spaced looks, reject at the first look where |z| reaches a constant c chosen
so that the overall rate is 5%. Write a function that finds c for a given K, using `stopping_exact()` from
`testing.py` (it takes the bar as `c`) or a simulation of your own, and check your c by simulating a z-test
on accumulating normal data with the null true.

**Self-check:** your result must pass all four tests.

1. For K = 1 your c is 1.960 to three decimals.
2. For K = 2 and K = 5 your c is within 0.005 of 2.178 and 2.413; the author's implementation, with
   `stopping_exact()` on a grid of step 0.0025, gives 2.1779 and 2.4134.
3. A simulation of at least 100,000 null paths with your K = 5 constant rejects within two MCSEs of 5%.
4. The same simulation with c = 1.96 at K = 5 rejects within two MCSEs of the stage's 14.17%.

## Safety and cleanup

- `testing.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection.
  It never overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json e3.json fault.json
```
