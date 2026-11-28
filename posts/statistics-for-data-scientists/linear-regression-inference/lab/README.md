# Lab — Linear Regression by Hand: Every Number in the Summary

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-11-28 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-43-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.16, NumPy 2.5.4 (OpenBLAS 0.3.34), SciPy 1.18.1, statsmodels 0.15.0, pandas 3.1.0; `regression.py` 7bd415f83058, root seed 20261128. The notebook was built and executed with the same pins. The optional `crosscheck.R` ran in R 4.5.2 (2025-10-31) with base R only, and its output `crosscheck-R.csv` is shipped; the lab matched R's `lm`, `summary.lm`, `anova`, `AIC` and `BIC` to between 3.7 × 10⁻¹⁶ and 1.2 × 10⁻¹¹ relative, and R's `predict` gives the VC arm's two intervals at 1.5 mg/day to every digit the lab prints.

This lab reproduces every number the article calls computed or measured. It rebuilds the sleep t-tests and PlantGrowth's
one-way ANOVA from *Which Statistical Test? The Design Decides, Not the Data* as regressions; solves NIST's eleven
linear Statistical Reference Datasets exactly in rational arithmetic and then scores ten floating-point solvers against
the certified values; recomputes every number in statsmodels' and R's summary of Longley's regression; partials out a
coefficient, measures omitted-variable bias and the variance inflation factors; fits an interaction with three origins on
ToothGrowth; computes the two intervals for a new guinea pig; and measures how often the slope's 95% interval covers when
the model's conditions fail. The one entry point is `regression.py`; it prints its numbers and writes them to the file
you name with `--out`.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `regression.py` | G1 | yes | the seven stages: `example`, `nist`, `summary`, `meaning`, `interaction`, `intervals`, `conditions` |
| `crosscheck.R` | G1 | yes | optional: the same models in base R's `lm`; writes `crosscheck-R.csv`, which `regression.py` compares against |
| `crosscheck-R.csv` | — | — | the author's R output (R 4.5.2), 63 values at 17 significant digits |
| `data/student1908_sleep.csv` | — | — | Student's ten patients on two drugs (public domain), with provenance |
| `data/plant_growth.csv` | — | — | Dobson's 30 plants under a control and two treatments, from R, with provenance |
| `data/toothgrowth.csv` | — | — | 60 guinea pigs by vitamin C dose and delivery, from R, with provenance |
| `requirements.txt` | — | — | the pinned dependencies: NumPy, SciPy, statsmodels, pandas |
| `captures.json` | — | — | the author's full run, machine-readable; every figure in the article reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

NIST's data files are not in this folder. The first run of the `nist` stage (or any stage that needs Longley) downloads
the eleven files, about 30 kB, from `https://www.itl.nist.gov/div898/strd/` into a hidden `.nist/` folder here and checks
each against the SHA-256 hash written in `regression.py`. A file that fails its hash is deleted and the run stops.

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.32 GB of RAM, the quick run at 0.26 GB |
| Software | Python 3.12 and the pins in `requirements.txt`, installed into a virtual environment (no root); R 4.x only for the optional cross-check (base R, no packages) |
| Privileges | none: no root, no Docker, nothing outside this folder and the virtual environment |
| Disk, network, time | the install is about 263 MB and needs the network once, and the first `nist` run fetches about 30 kB from NIST; then `all --quick` takes about 5 s and `all` about 20 s on the build machine |

## Run

```bash
python3.12 -m venv .venv && . .venv/bin/activate      # or: uv venv --python 3.12 && . .venv/bin/activate
pip install -r requirements.txt
python regression.py all --quick --out quick.json      # the reader's budget, about 5 s
python regression.py all --out mine.json               # the article's budget, about 20 s
Rscript crosscheck.R                                   # optional: rewrites crosscheck-R.csv from your R
```

One stage at a time: `python regression.py nist --quick --out quick.json`. A run adds or replaces its stages' keys in
the file you name, so stages can be run in any order. Never point `--out` at `captures.json`; that file is the author's
run to compare against. Run `crosscheck.R` after a `nist` run, since it reads the files in `.nist/`.

## What to expect

The quick run's `nist` stage prints, after its provenance line:

```text
Exact rational least squares against NIST's certified values (15 significant digits):
  Longley   n= 16 p= 7: 15/15 certified values reproduced digit for digit
  all datasets: 121/121
Longley: kappa(X) 4.8593e+09, kappa(X'X) 2.3612e+19, column-scaled kappa 4.3275e+04; smallest/largest singular value 2.058e-10
  Householder QR                 digits min  10.92 max  13.22 RSS/certified 1.0000
  normal equations (LU)          digits min   7.38 max   8.56 RSS/certified 1.0000
Filip: kappa(X) 1.7680e+15, kappa(X'X) 3.1257e+30, column-scaled kappa 5.2068e+09; smallest/largest singular value 5.656e-16
  Householder QR                 digits min   8.55 max   9.71 RSS/certified 1.0000
  normal equations (LU)          digits min  -0.03 max   0.01 RSS/certified 1.3285
  statsmodels OLS().fit()        digits min  -0.03 max   0.00 RSS/certified 1.3458 [The design matrix is rank-deficient. ...]
```

What must match where:

- **Exact arithmetic, anywhere:** 121/121 certified values, digit for digit. These use Python's `fractions` and do not
  depend on the machine.
- **Floating-point digits:** with these pins on x86-64 Linux a run repeats `captures-quick.json` and `captures.json`
  digit for digit. With another BLAS build, CPU or even memory layout, the last bits of a solution can change, and with
  them the digits beyond about the eleventh: in the author's runs, passing Norris's response as a strided column instead
  of a contiguous array moved its QR digits from 12.09 to 13.33. Expect agreement within about one digit, and the same
  pattern: QR near 16 − log₁₀ κ, the normal equations near 16 − 2 log₁₀ κ (κ of the column-scaled design), and the three
  library defaults at zero on Filip.
- **Simulated rates:** every random number comes from a seeded stream, `SeedSequence([stage, sub-stream, seed])`, so the
  `intervals`, `conditions` and rounding results repeat exactly with these pins; elsewhere they agree within 3 MCSE
  (0.15 points at 95% on the full budget, 0.49 on `--quick`).
- **statsmodels and R:** each stage prints the largest relative difference from the libraries; anything above 10⁻⁹ means
  something changed.

The stages:

- `example`: the sleep data with a drug dummy (Student's t, 1.8608) and with nine patient dummies added (the paired t,
  4.0621, same coefficient 1.58); PlantGrowth with a three-level factor and the nested F (4.8461 on 2 and 27 df).
- `nist`: exact rational least squares on all eleven datasets; ten solvers on Longley and Filip; R's `lm` from the
  cross-check; Filip without x¹⁰; the fewest correct digits on all eleven against their condition numbers; Longley with GNP
  in thousands; Longley's data perturbed 20,000 times (2,000 on `--quick`) within their printed precision.
- `summary`: statsmodels' summary of Longley printed, then every number in it from the design matrix, with the
  differences from statsmodels and R; three joint F tests; the joint 95% region for GNP and Year.
- `meaning`: each slope by partialling out (Frisch–Waugh–Lovell), with each predictor's R² on the others and its VIF;
  omitted-variable bias with Year left out, as an exact identity; condition numbers raw, centred and standardised.
- `interaction`: ToothGrowth's six cell means; length on supplement times doublings of dose with the origin at 0.5, 1
  and 2 mg/day; lack of fit against the cell means; the interaction with dose as a factor.
- `intervals`: the vitamin-C-as-ascorbic-acid (VC) arm at 1.5 mg/day, the interval for the mean and for a new animal,
  and how often each covers in 20,000 simulated studies at six sizes.
- `conditions`: coverage of the slope's 95% interval under six conditions at n = 5 to 1,000, 20,000 datasets per cell
  (2,000 on `--quick`); the prediction interval's two tails under normal and skewed errors.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden below it. This is
an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: NIST's certified values, and what each solver keeps of them

Run the `nist` stage on the quick budget into your own file and compare it with `captures-quick.json`.

```bash
python regression.py nist --quick --out mine.json
```

**Self-check:** the provenance line prints your versions; all 121 certified values reproduce in exact arithmetic;
Householder QR keeps at least 10.9 digits on every Longley coefficient and 8.5 on every Filip coefficient; the normal
equations keep about 7.4 on Longley and none on Filip; statsmodels' default fit prints its rank warning on Filip.

<details><summary>Answer</summary>

**Answer.** The author's run: 121/121 exact matches across the eleven files (15 for Longley, 23 for Filip). On Longley
the fewest correct digits are 10.92 for Householder QR, 7.38, 7.24 and 7.41 for the normal equations by LU, Cholesky and
explicit inverse, and 10.93 to 11.08 for the SVD and complete-orthogonal solvers. On Filip, QR keeps 8.55; the normal
equations keep none (Cholesky refuses the matrix, the explicit inverse leaves a residual sum of squares 16,269 times the
minimum); NumPy's default `lstsq` and statsmodels' default fit keep none, with a residual sum of squares 1.3458 times the
minimum; `rcond=-1`, SciPy's `gelsd` and `gelsy` keep 5.41, 6.06 and 7.80. If your digits differ by more than about one,
check `--quick` is not the issue (the `nist` digits do not depend on the budget) and that `regression.py`'s SHA-1 prefix
is 7bd415f83058.

</details>

### E2 — Inspect: the singular value two defaults threw away

The article says NumPy's and statsmodels' default solvers return a minimum-norm answer on Filip because each treats a
singular value as zero. In `mine.json`, under `nist` → `datasets` → `Filip`, find `sv_ratio` (the smallest singular
value of X over the largest), `numpy_cutoff` and `statsmodels_cutoff`. Before opening the answer, say which solvers
should keep all eleven columns and why.

**Self-check:** the ratio, both cutoffs, and the rule that a solver keeps a singular value only when the ratio exceeds its
cutoff, applied to NumPy's default, statsmodels' default, `rcond=-1` and SciPy's default.

<details><summary>Answer</summary>

**Answer.** σ_min/σ_max = 5.656 × 10⁻¹⁶. NumPy's default cutoff is machine precision times max(82, 11) = 1.82 × 10⁻¹⁴ and
statsmodels' pseudoinverse uses 10⁻¹⁵; the ratio is below both, so both zero the eleventh singular value and solve a
rank-10 problem, which is why their residual sum of squares is 34.6% above the minimum. `rcond=-1` and SciPy's default
both cut at machine precision, 2.22 × 10⁻¹⁶, below the ratio, so they keep all eleven columns and recover 5.41 and 6.06
digits. statsmodels says so: its `rank` check uses NumPy's `matrix_rank` tolerance and finds 10, hence the warning.

</details>

### E3 — Predict: the year measured from 1954

Longley's `Year` column runs from 1947 to 1962, so the intercept is the predicted employment in the year 0. You will
rerun two stages with the year measured from 1954:

```bash
python regression.py summary --quick --year-origin 1954 --out e3.json
python regression.py nist --quick --year-origin 1954 --out e3.json
```

Write your prediction first: (a) which numbers in the summary table change, and (b) how many digits the normal equations
and QR gain on Longley, given that the column-scaled condition number falls from 4.33 × 10⁴ to 1.15 × 10³. Use the
article's rule for each solver.

**Self-check:** (a) names exactly the numbers that change; (b) the gain for each solver within one digit of what the rule
predicts, with the article's reason.

<details><summary>Answer</summary>

**Answer.** (a) Only the intercept row changes: 91,903 (SE 22,187, t 4.14, p 0.0025) instead of −3,482,259 (SE 890,420,
t −3.91). Every slope, standard error, t and p, σ̂ = 304.854, R² = 0.995479, F = 330.29 and the log-likelihood stay
identical, because shifting a column by a constant moves only where the intercept is read. The new intercept is the
predicted employment in 1954 with the other five predictors at zero, still far outside the data. (b) The rule says QR
loses about log₁₀ κ digits and the normal equations about 2 log₁₀ κ, so a fall of log₁₀(4.33 × 10⁴ / 1.15 × 10³) = 1.58
decades predicts about 1.6 more digits for QR and 3.2 for the normal equations. The author's run: QR from 10.92 to 12.20
(+1.28), the normal equations from 7.38 to 10.25 (+2.87). Rescaling GNP to thousands, by contrast, changes the raw κ
from 4.86 × 10⁹ to 1.38 × 10⁹ but not the column-scaled κ, and the normal equations stay at 7.43 digits.

</details>

### E4 — Diagnose: a better R² from a worse fit

An earlier draft of the `summary` stage produced the table below. Run it:

```bash
python regression.py summary --quick --fault --out e4.json
```

R² is now 1.000 and F is 50,523, so by those two numbers the fit improved enormously; but σ̂ is 475.2, up from 304.9,
so the residuals grew. Find the cause before you read the code, name the one printed number that proves it, and fix it.

**Self-check:** symptom, cause, the proving number, and a fix after which the stage prints R² 0.995479 and σ̂ 304.854.

<details><summary>Answer</summary>

**Answer.** *Symptom:* R² 0.999967, adjusted R² 0.999947 and F 50,523 on 6 and 10 df, while σ̂ rose from 304.854 to
475.166 and the residual degrees of freedom from 9 to 10. *Cause:* the draft built X without the column of ones, which is
what `sm.OLS(y, X)` does when `sm.add_constant` is forgotten; with no intercept, R² is measured against zero instead of
against the mean (statsmodels labels it "R-squared (uncentered)" and adds a note). *Proof:* the printed TSS is
68,445,976,650, which is Σy², not Σ(y − ȳ)² = 185,008,826; against that much larger total, any fit looks perfect. Year's
coefficient also collapses from 1,829 to 48.4, because a column near 1,954 now stands in for the missing constant.
*Fix:* restore the constant in the `--fault` branch (delete the line that drops column 0); the stage then prints
R² 0.995479 and σ̂ 304.854 again. Undo your edit afterwards so `regression.py` matches its SHA-1 again.

</details>

### E5 — Extend: modified Gram–Schmidt, two ways

Wampler's 1969 study ranked the Gram–Schmidt programs with the Householder ones, far ahead of elimination. Add two solvers to
the harness, by importing `read_nist`, `nist_design`, `lre` and `kappa_scaled` from `regression.py`: modified
Gram–Schmidt that forms Qᵀy after factoring X, and Björck's variant that factors the augmented matrix [X | y] and reads
the coefficients from the last column of R. Score both on all eleven datasets, next to Householder QR.

**Self-check (acceptance test):** on a seeded, well-conditioned random 50 × 5 problem both solvers agree with
`np.linalg.lstsq` to 10⁻¹² relative; your table has eleven rows with the fewest correct digits for each solver; and you
explain from the LAPACK bound in the article why the two variants differ most on Filip. The author's implementation is
not shipped, so there is no answer to copy; its numbers are in the answer below for comparison.

<details><summary>Answer</summary>

**Answer.** The author's implementation, for comparison: on Longley, modified Gram–Schmidt with Qᵀy kept 10.55 digits
and the augmented version 14.12 (Householder QR 10.92); on Filip, 4.45 and 7.29 (QR 8.55). Classical Gram–Schmidt, for
contrast, kept 8.82 on Longley and none on Filip. Forming Qᵀy after the factorisation uses a Q whose columns have lost
orthogonality in proportion to κ, which brings a κ² term back; the augmented form carries y through the same
orthogonalisation as X and avoids it.

</details>

## Safety and cleanup

- The lab reads its three CSVs and NIST's eleven files, which it downloads once into `.nist/` from NIST's public site and
  checks against fixed hashes. It contacts nothing else and runs nothing in the background.
- It writes only the files you name with `--out`; `crosscheck.R` rewrites `crosscheck-R.csv` beside itself.

```bash
rm -rf .nist __pycache__ quick.json mine.json e3.json e4.json
deactivate && rm -rf .venv          # if you made the environment here
```
