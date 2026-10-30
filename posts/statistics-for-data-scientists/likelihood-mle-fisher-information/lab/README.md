# Lab — Likelihood: The MLE, Three Tests, and Where χ² Fails

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-28 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `likelihood.py` 786c58fb52d9, root seed 20261028. The notebook was built and executed with the same pins. The author also checked the fits privately against R 4.5.2 with MASS 7.3.65 (`glm`, `glm.nb`, `fitdistr`) and the power-law comparison against the `powerlaw` 2.0.0 package: every estimate, log-likelihood and likelihood ratio agrees to the six significant digits the capture file keeps, and so do `fitdistr`'s standard errors; `glm.nb`'s own standard error for θ differs in the fifth digit (0.1862447 against 0.1862514), because MASS evaluates it at the fitted means of its previous iteration (the `author_crosscheck` key in `captures.json`).

This lab reproduces every number the article calls measured. It works Clarke's 576 squares of V-1 hits by
hand (log-likelihood, score, maximum likelihood estimate, observed and expected information, standard error)
and checks them against SciPy and statsmodels; computes the Wald, score and likelihood-ratio statistics for
the V-1 rate and for one Prussian corps' 20 years of horse-kick deaths, and their exact error rates as the
expected count grows; fits the negative binomial to Greenwood and Yule's 647 women by maximum likelihood,
with profile-likelihood and Wald intervals and the delta method; simulates the likelihood-ratio test of
Poisson against negative binomial with its null on the boundary of the parameter space; shows how the German
tank likelihood breaks the regularity conditions; and settles the first part's power-law question with a
likelihood-ratio comparison. The one entry point is `likelihood.py`; it prints its numbers and writes them to
the file you name with `--out`. Every simulated quantity is printed as estimate ± its Monte Carlo standard
error (MCSE), with the number of replications R.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `likelihood.py` | G1 | yes | the five stages: `poisson`, `nb`, `boundary`, `tank`, `powerlaw` |
| `data/clarke1946_flying_bombs.csv` | — | — | Clarke's 576 squares of south London by number of V-1 hits, with provenance |
| `data/greenwood_yule1920_accidents.csv` | — | — | Greenwood and Yule's 647 women by number of accidents in five weeks, with provenance |
| `data/bortkiewicz1898_horse_kicks.csv` | — | — | deaths by horse kick in 14 Prussian corps, 1875–1894, one row per corps-year, with provenance |
| `requirements.txt` | — | — | the four pinned dependencies: NumPy, SciPy, statsmodels and pandas |
| `captures.json` | — | — | the author's full run, machine-readable, with the private cross-checks; every figure in the article reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; every run peaked at 0.27 GB of RAM |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4, SciPy 1.18.1, statsmodels 0.15.0 and pandas 3.1.0: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python likelihood.py all --quick` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | the virtual environment takes about 260 MB; on the build machine `all --quick` took 16.5 s and `all` 99 s, 79 s of it in the `powerlaw` stage's simulation |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python likelihood.py all --quick --out mine.json     # the reader's budget; keeps the shipped captures
python likelihood.py all --out full.json             # the article's budget
```

If you download the files one by one rather than as the zip, put the three CSV files in a folder named `data`
beside `likelihood.py`. Each stage also runs alone, for example `python likelihood.py nb --quick --out
mine.json`. `--quick` cuts every simulation to a tenth of its replications. Three flags exist for the
exercises: `--corps` picks the corps the `poisson` stage tests (default `XI`), `--boundary-n` sets the number
of counts in each simulated data set of the `boundary` stage (default: the real data's 576 and 647), and
`--fault` swaps in an earlier draft of the boundary simulation (E4).

## What to expect

The first line is the provenance line. Then, stage by stage, for the full budget:

- `poisson`: λ̂ = 537/576 = 0.932292, observed and expected information both 617.8324, SE 0.040231; SciPy and
  statsmodels agree. For H0: λ = 0.85 the Wald, score and likelihood-ratio statistics are 4.1839, 4.5890 and
  4.4477; for λ = 1.0 they are 2.8324, 2.6406 and 2.7023. Corps XI, 25 deaths in 20 years, against the ten
  regular corps' 0.61: Wald 6.5536, score 13.4295, LR 10.2720, and the Wald statistic runs from 3.628 to 27.519
  as the same parameter is rescaled. Exact sizes of the three 5% tests at an expected count of 12.2: 8.84%,
  4.26% and 6.57%; at 537: 5.03%, 4.95% and 4.97%.
- `nb`: Newton's method reaches k̂ = 0.865116 in five steps from the moment estimate 0.954814; SciPy and
  statsmodels agree (α̂ = 1/k̂ = 1.155915). SE(k̂) is 0.186251 from the observed information and 0.183894 from
  the expected. The 95% intervals for k: profile 0.5855 to 1.3827, Wald 0.5001 to 1.2302. The dispersion
  index 1 + μ/k is 1.5378 with delta-method SE 0.1220. Over R = 20,000 data sets from the fitted model, k̂
  has SD 0.2163 and skewness 1.376, and falls above the Wald upper limit in 7.47% ± 0.19 of them, below the
  lower limit in 0.14% ± 0.03.
- `boundary`: V-1, LR 0.4104 with p 0.522 against χ²₁ and 0.261 against the 50:50 mixture; Greenwood and
  Yule, LR 49.834. Under a Poisson null with R = 200,000: LR = 0 in 52.61% ± 0.11 of data sets at the V-1
  settings (52.53% at Greenwood and Yule's), and the test that compares LR with 3.841 rejects 2.17% ± 0.03
  (2.20%). Inside the parameter space the same test rejects 5.01% ± 0.05.
- `tank`: at N = m = 303 the log-likelihood falls by 0.01658 per tank and curves upward; the MLE's error
  N − M has mean 56.167, SD 47.890 and skewness 1.183 for k = 5.
- `powerlaw`: the first part's sample regenerates exactly (threshold 26.140414260414). On its top 1,000
  points the lognormal beats the power law, normalised ratio 2.286, p 0.0223; at CSN's Kolmogorov–Smirnov
  threshold (509 points) the ratio is 1.290, p 0.197. Over R = 1,000 fresh samples the comparison favours the
  lognormal in 98.1% at 1,000 points and 45.9% at 500, and it favours a true power law in 4.4%.

Everything is deterministic. Exact and fitted values match to every printed digit on any machine; a different
statsmodels may move the last digits of its own line. Simulated values repeat exactly with NumPy 2.5.4 and the
default seed; another NumPy version may draw different streams and move each simulated value by a few of its
MCSEs. The `powerlaw` stage stops with a message if your NumPy does not regenerate the first part's sample. A
`--quick` run uses the same streams but fewer draws, so it matches `captures-quick.json` exactly and
`captures.json` within a few MCSEs.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden
below it. This is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: the three statistics and the boundary rates

Run `python likelihood.py all --quick --out mine.json`. Compare the `poisson` lines with the article's worked
example, the `nb` intervals with its table, and the `boundary` rates with `captures-quick.json`.

**Self-check:** every exact and fitted number (λ̂ 0.932292, SE 0.040231, the statistics 4.1839, 4.5890 and
4.4477, k̂ 0.865116, the profile interval 0.5855 to 1.3827) matches to the printed digits; each simulated rate
lies within three of its MCSEs of the article's full-budget value; with NumPy 2.5.4 the quick numbers match
`captures-quick.json` digit for digit; your output starts with the provenance line.

<details><summary>Answer</summary>

The author's quick run: LR = 0 in 52.65% ± 0.35 of Poisson data sets at the V-1 settings and 52.87% ± 0.35 at
Greenwood and Yule's; the χ²₁ test rejects 2.17% ± 0.10 and 2.21% ± 0.10, and the mixture's 2.706 test 4.30%
± 0.14 and 4.35% ± 0.14; inside the parameter space the χ²₁ test rejects 4.61% ± 0.15. k̂ over 2,000 data sets
has SD 0.2187 and skewness 1.260. If an exact number differs, the script or a data file was edited; if only
simulated numbers differ, your NumPy draws different streams, and each should still sit within a few MCSEs of
the full run.

</details>

### E2 — Inspect: which data sets land on the boundary

The article says the likelihood-ratio statistic is exactly zero whenever a data set's variance is at most its
mean, because the score for α = 1/k is then not positive at α = 0. Before you look, write down your guess for
the share of Poisson data sets that end on the boundary, and for whether "LR = 0" and "variance ≤ mean" can
ever disagree. Then read `boundary` → `null_boundary` → `v1` → `p_zero` and `p_boundary_score` in `mine.json`.

**Self-check:** you can say why the two shares must be equal, and why the share is a little above one half
rather than exactly one half.

<details><summary>Answer</summary>

Both shares are 0.5265 in the quick run (0.5261 in the full one): the same data sets. The score for α at
α = 0 is proportional to Σ(y − ȳ)² − Σy, so when the divisor-n variance is at most the mean, the
log-likelihood falls as soon as α leaves zero, the maximum is the Poisson itself, and LR = 0 exactly; when the
variance exceeds the mean, the maximum is inside and LR > 0. The share exceeds one half because the boundary
event is Fisher's dispersion statistic Σ(y − ȳ)²/ȳ at most n, and under a Poisson that statistic is close to
χ² on n − 1 degrees of freedom, whose median sits below its mean, so it lands below n slightly more than half
the time. The lab decides "variance ≤ mean" in exact integer arithmetic: ten of the 20,000 quick data sets
have variance exactly equal to the mean, and floating point would put some of them on the wrong side.

</details>

### E3 — Predict: smaller data sets, or the other side of the null

Pick one or both. Write each prediction down, with its reason, before you run.

1. Data sets of 50 counts instead of 576 and 647: `python likelihood.py boundary --quick --boundary-n 50 --out
   e3.json`. Predict whether the share of data sets with LR = 0 rises or falls from 52.6%, and whether the
   mixture's 5% critical value, 2.706, then rejects more or less than 5%.
2. Corps VIII, 7 deaths in 20 years: `python likelihood.py poisson --quick --corps VIII --out e3.json`.
   Corps XI sat above the null and gave score > LR > Wald. Predict the order for VIII, which sits below it.

**Self-check:** for 1, the share's direction right, within five points, and the size's direction right, for
the reason E2 gives; for 2, the order right, for the reason that each statistic weighs the squared distance by
the information at a different point.

<details><summary>Answer</summary>

1. The share rises to 60.05% ± 0.35 at the V-1 rate and 59.36% ± 0.35 at Greenwood and Yule's, and the 2.706
   test rejects only 3.32% ± 0.13 and 3.36% ± 0.13 (the χ²₁ test 1.57% and 1.62%). With fewer counts the
   dispersion statistic's χ² on 49 degrees of freedom is more skewed, its median sits further below its mean,
   and more data sets fall on the boundary than the asymptotic one half; Lawless (1987) reported the same for
   the negative binomial's α. The mixture is a large-sample result, and here it is conservative.
2. Wald 3.8629 > LR 2.6226 > score 2.2164, the reverse of XI, and only the Wald test rejects at 5%. For a
   Poisson rate the expected information is n/λ, larger at smaller λ. The Wald statistic weighs the squared
   distance by the information at the estimate, the score statistic by the information at the null, so
   whichever of λ̂ and λ₀ is smaller gives its statistic the larger value, and the LR lies between them.
   VIII is one of the ten regular corps, so its own 7 deaths are inside the null rate of 0.61; treat it as
   an illustration of the geometry rather than as a test.

</details>

### E4 — Diagnose: likelihood ratios below zero

Run `python likelihood.py boundary --quick --fault --out fault.json`. The rejection rates look the same as
in a correct run, yet no data set has LR = 0 and the smallest LR is −0.7578. One helper in this stage is an
earlier draft. Name the symptom, the cause, the one printed line that proves it, and the fix, then check that
the fix holds.

**Self-check:** the cause is in the range of parameters the fit may reach, the proof is a printed line that
ties the negative ratios to one property of the data, and after the fix the smallest LR is 0 and the share at
zero is back to about 52.6%.

<details><summary>Answer</summary>

- **Symptom:** LR < 0 in 54.55% of data sets at the V-1 settings (53.82% at Greenwood and Yule's), down to
  −0.7578; no data set has LR = 0. A likelihood ratio between nested models cannot be negative, because the
  larger model contains the smaller one's maximum.
- **Cause:** with `--fault`, the stage fits k with `fit_k_box`, which confines log k to −5 to 5, as a generic
  bounded optimiser call would; k can then be at most e⁵ = 148.4, so α = 1/k is at least 0.0067. The fitted
  family no longer contains the Poisson (α = 0), and for a data set whose likelihood rises all the way to
  α = 0 the best the box allows sits below the Poisson's likelihood.
- **Proof:** the line `LR < 0 in 0.5455 of data sets; of those, 0.9652 have variance <= mean, and 1.0000 of
  the data sets with variance <= mean have LR < 0`. Every data set whose maximum is on the boundary goes
  negative; the remaining 3.5% of negatives are data sets with a variance barely above the mean, whose k̂ lies
  beyond 148.
- **Fix:** let the fit reach the boundary: `fit_k_matrix` returns k = ∞ (the Poisson) whenever the variance
  is at most the mean, and the likelihood ratio is then exactly 0. Run without `--fault`: LR = 0 in 52.65%,
  smallest LR 0. The rates above 2.706 and 3.841 never changed, because the draft only touches ratios near
  zero; a check of the test's size alone would not have caught it.

</details>

### E5 — Extend: zero inflation is another boundary

A zero-inflated Poisson gives each count a probability π of being a structural zero: P(0) = π + (1 − π)e^(−λ)
and P(y) = (1 − π) e^(−λ) λ^y / y! for y ≥ 1. Testing π = 0 puts the null on the boundary again, since π ≥ 0.
Write a function that fits this model to a count table by maximum likelihood with π restricted to 0 ≤ π < 1,
returns the likelihood ratio against the Poisson, and apply it to Clarke's table. Then simulate it under a
Poisson null with Clarke's n and rate, as the `boundary` stage does for the negative binomial, with at least
20,000 data sets.

**Self-check:** your result must pass all four tests.

1. At π = 0 your log-likelihood equals the Poisson's: −732.5946 for Clarke's table, to 10⁻⁹ (with the
   constant Σ log y! included).
2. Your fit never returns π < 0. It returns π̂ = 0, and LR = 0 exactly, when the observed zeros are at most
   n e^(−ȳ), the number the Poisson expects at the fitted mean; derive that condition from the score for π at
   π = 0 before you code it.
3. On Clarke's table, which has 229 empty squares against 226.74 expected, π̂ is about 0.016 and the LR about
   0.094, both to within 0.001.
4. In the simulation, the share with LR = 0 equals the share whose zeros are at most n e^(−ȳ) exactly, lies
   between 0.45 and 0.56, and the 2.706 test rejects between 4% and 6% of data sets.

## Safety and cleanup

- `likelihood.py` reads only `data/`, writes only the file named by `--out`, and opens no network connection.
  It never overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json full.json e3.json fault.json
```
