# Lab — Distributions as Generative Stories: Let the Process Pick

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-24 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1; `stories.py` 31277f0c5888. The notebook was built and executed with the same Python and pins. The author also checked every pmf and the tail ratio privately against R 4.5.2 (MASS 7.3.65): they agree to within 1.5 × 10⁻¹¹ (the `author_crosscheck_r` key in `captures.json`).

This lab reproduces every number the article calls measured, and recomputes every published table it
quotes. Each generative story is written as code: bombs falling into squares, events arriving at a
constant rate, effects that add or multiply, women whose accident rates differ, a normal whose
variance varies, and growth with and without a floor. Each story is then checked against a historical
table or an exact formula. The one entry point is `stories.py`; it prints its numbers and writes them
to `captures.json` (or the file you name with `--out`). Published counts come from the papers, as the
data files' headers record; everything simulated is labelled simulated and printed with its Monte
Carlo standard error (MCSE) and its number of replications R.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `stories.py` | G1 | yes | the six stages: `worked`, `waiting`, `sums`, `accidents`, `tails`, `loglog`; NumPy pmfs by recurrence, checked against SciPy |
| `data/clarke1946_flying_bombs.csv` | — | — | Clarke's 576 squares of south London, with its source and the imputed 7 explained |
| `data/bortkiewicz1898_horse_kicks.csv` | — | — | the 280 corps-years of horse-kick deaths, transcribed from the 1898 scan; `in_200` marks the corps Bortkiewicz kept |
| `data/greenwood_yule1920_accidents.csv` | — | — | Greenwood and Yule's 647 women, as two independent reproductions print them |
| `data/coal_disasters_1851_1962.csv` | — | — | dates of 191 coal-mine explosions, from R's boot package |
| `requirements.txt` | — | — | the two pinned dependencies, NumPy and SciPy |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.2 GB of RAM |
| Software | Python 3 (run on 3.12.15) with NumPy 2.5.4 and SciPy 1.18.1: `pip install -r requirements.txt` into a virtual environment, or `uv run --with-requirements requirements.txt python stories.py all` |
| Privileges | none: no root, no Docker, no network access after the install, nothing outside this folder |
| Disk, network, time | NumPy and SciPy take about 180 MB once installed; `all` takes 5 to 10 seconds (the capture took 4.6 s, most of it the two accident simulations), `all --quick` 1 to 2 seconds |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python stories.py all --out mine.json          # keeps the shipped captures.json for comparison
```

If you download the files one by one rather than as the zip, put the four CSV files in a folder named
`data` beside `stories.py`. Each stage also runs alone: `python stories.py worked`, `waiting`, `sums`,
`accidents`, `tails` or `loglog`. `--quick` cuts every simulation to a quarter or less of its replications, for a faster and
noisier run. Three flags exist for the exercises: `sums --dominant` widens one of the twelve effects,
`tails --df 3` swaps in a t with 3 degrees of freedom, and `accidents --fault` swaps in an earlier
draft of one helper.

## What to expect

The first line is the provenance line. Then, stage by stage:

- `worked`: Clarke's 576 squares and 537 bombs give λ = 0.932292, mean 0.9323 and variance 0.9711
  (divisor n − 1). The Poisson row 226.743, 211.390, 98.539, 30.622, 7.137, 1.569 is Clarke's printed
  table; the binomial row 226.559, 211.586, 98.618, 30.586, 7.101, 1.550 is the story before its rare-event
  limit. Chi-square 1.1692 on 4 df, P = 0.8832. Binomial and Poisson differ by 0.550 squares in total
  (total variation 4.776 × 10⁻⁴; Le Cam's bound 1.619 × 10⁻³). Bortkiewicz's 200 corps-years: mean
  0.6100, variance 0.6110; all 280: mean 0.7000, variance 0.7627.
- `waiting`: a Poisson process built from exponential gaps gives Poisson(3) counts (total variation
  0.0036 at R = 100,000) and a gamma third arrival (mean 0.9999 ± 0.0018). The coal gaps: CV 1.469
  pooled, which no record of 190 exponential gaps reached in R = 10,000 (largest 1.361); 1.064 for
  1851–1889, reached by 18.77% ± 0.39% of exponential records.
- `sums`: twelve effects from 0.5 to 1.5, R = 200,000: the sum has skewness 0.0027 and excess
  kurtosis −0.1008; the product has skewness 4.1611, median 0.5919 against mean 0.9952, and 68.79% of
  products below their mean; its log has skewness −0.1062.
- `accidents`: mean 0.4652, variance 0.6919, ratio 1.4872. Poisson chi-square 103.14; the moment fit
  k = 0.9548 (statsmodels α = 1.0473, R size and MASS θ = 0.9548, SciPy `nbinom(0.9548, 0.6724)`) gives
  chi-square 4.20. Under the fitted gamma the top 20% of women carry 53.0% of expected accidents.
  Simulated proneness (R = 20,000 factories): sample variance 0.6918 ± 0.0006; second five weeks
  0.4653 ± 0.0002. Simulated contagion (R = 10,000): period-one counts 442.77, 138.48, 44.48, 14.37,
  4.65, 2.25 against the negative binomial's 442.91, 138.55, 44.36, 14.32, 4.64, 2.23; second five weeks
  0.6913 ± 0.0004 (exact 0.6919).
- `tails`: beyond 4 standard deviations the unit-variance t₅ has 3.5728 × 10⁻³ against the normal's
  6.3342 × 10⁻⁵, a ratio of 56.405; its density at 0 is 0.4901 against 0.3989. In R = 20,000 samples of
  1,000, 97.19% ± 0.12% of t samples have a point beyond 4 (exact 97.21%), and of the first 100 points
  none is beyond 4 in 69.35% ± 0.33% (exact 69.91%).
- `loglog`: the top 10% of 10,000 lognormal(0, 2.5) draws spans 2.52 decades with slope −0.9180 and
  R² 0.9905; over R = 1,000 samples R² ≥ 0.98 in 91.40% ± 0.89%. Champernowne's walk with a floor
  matches P(X ≥ 2ʲ) = 2⁻ʲ to 0.0014; without one, P(X ≥ 2²⁰) after 20 steps is 2.87 × 10⁻¹⁰.

Every number is deterministic: the exact computations match to every printed digit on any machine, and
the simulated ones repeat exactly with NumPy 2.5.4 and the default seed. Another NumPy version may draw
different random streams, which moves each simulated value by a few of its MCSEs and changes the Q–Q
sample. `--quick` draws different streams too; compare a quick run with this list, not digit by digit.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer
hidden below it. This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: Clarke's table and Greenwood and Yule's fit

Run `python stories.py worked --out mine.json` and `python stories.py accidents --out mine.json`.
Compare the Poisson row of Clarke's table with the values he printed in 1946 (226.74, 211.39, 98.54,
30.62, 7.14, 1.57) and his chi-square of 1.17 with P = 0.88. Then read the negative binomial fit to
Greenwood and Yule's accidents.

**Self-check:** the Poisson row rounds to Clarke's printed values, the chi-square is 1.1692, the moment
fit gives k = 0.9548 with chi-square 4.20, and your output starts with the provenance line.

<details><summary>Answer</summary>

The author's run: Poisson 226.743, 211.390, 98.539, 30.622, 7.137, 1.569; chi-square 1.1692 on 4 df,
P = 0.8832; k = 0.9548 and negative binomial 442.91, 138.55, 44.36, 14.32, 4.64, 2.23, chi-square
4.20. These lines involve no randomness, so they match on any machine. A mismatch means a data file
was edited: Clarke's file must total 537 hits over 576 squares, Greenwood and Yule's 301 accidents
over 647 women.

</details>

### E2 — Inspect: the two halves of the overdispersion

The article splits Greenwood and Yule's variance of 0.6919 into 0.4652 of Poisson noise and 0.2267
from rates that differ between women. The `accidents` stage builds 20,000 factories of 647 women from
the proneness story and measures both halves. Before you look, write down what each should be from
μ = 0.4652 and k = 0.9548. Then read `accidents` → `proneness_simulation` → `within_part` and
`between_part` in `mine.json`.

**Self-check:** the within part is close to μ and the between part close to μ²/k, each within three
of its printed MCSEs.

<details><summary>Answer</summary>

Within 0.4650 ± 0.0001 and between 0.2264 ± 0.0002, against μ = 0.4652 and μ²/k = 0.2267. The within
part is the average Poisson variance, which equals the average rate; the between part is the variance
of the rates themselves. Their sum is the law of total variance, and it is the negative binomial's
μ + μ²/k.

</details>

### E3 — Predict: one effect that dominates the sum

Now `python stories.py sums --dominant --out dominant.json` makes one of the twelve effects twelve
times wider (0.5 to 12.5) and leaves the other eleven alone. Write down your prediction for the sum's
skewness and excess kurtosis (now 0.0027 and −0.1008) before you run it, with the reason.

**Self-check:** the sign and rough size of the excess kurtosis, for the reason the article gives for
when the central limit theorem works.

<details><summary>Answer</summary>

Skewness stays near zero (0.0017), because the wide effect is symmetric. Excess kurtosis falls to
−1.0344: the sum turns flat-topped, close to the uniform's −1.2. The wide effect carries 12 of the
sum's 12.92 units of variance, 93%, so the condition that no single effect dominates fails and the
sum looks like that one effect, not like a normal. The exact value is −1.036, from the uniforms'
fourth cumulants.

</details>

### E3 — Predict: heavier tails with 3 degrees of freedom

Run `python stories.py tails --df 3 --out t3.json`, which scales a t with 3 degrees of freedom to
variance 1. Before you run it, predict its ratio to the normal beyond 4 standard deviations (56.4 for
the t₅), in direction and rough size.

**Self-check:** a ratio between 80 and 120, for the reason that fewer degrees of freedom mean a
variance that varies more.

<details><summary>Answer</summary>

97.334: the unit-variance t₃ puts 6.1654 × 10⁻³ beyond 4 against the normal's 6.3342 × 10⁻⁵, so a
sample of 1,000 has 6.2 such points on average. Its peak is higher still (0.6366 against 0.4901 for
t₅), so the body looks even more like a slightly pointy normal while the tail grows. With 100 points,
53.88% of samples still show nothing beyond 4.

</details>

### E4 — Diagnose: a negative binomial that fits worse than the Poisson

Run `python stories.py accidents --fault --out fault.json`. The negative binomial row now expects 223
women with no accident where 447 had none, and its chi-square is 397, worse than the Poisson's 103 on
data the article fits with chi-square 4.2. One helper in this stage is an earlier draft. Find the
fault: name the symptom, the cause, the one printed number that proves it, and the fix, then check
that the fix holds.

**Self-check:** the cause is a parameter mapping, the proof is a number the run prints, and after the
fix the fitted distribution has mean 0.4652, variance 0.6919 and chi-square 4.20.

<details><summary>Answer</summary>

- **Symptom:** a moment fit that misses the zeros by half and fits worse than the model it replaces.
- **Cause:** `scipy_nbinom_args` passes SciPy p = μ/(k + μ) = 0.3276. SciPy's `nbinom(n, p)` counts
  failures before n successes, and p is the success probability, k/(k + μ) = 0.6724.
- **Proof:** the run prints the "fitted" distribution's mean as 1.9596 and variance as 5.9815. A
  moment fit must return the sample's own 0.4652 and 0.6919. The recurrence also disagrees with SciPy
  by 0.34, where a correct mapping agrees to 10⁻¹⁶.
- **Fix:** p = k/(k + μ), which is SciPy's documented p = μ/σ² with n = μ²/(σ² − μ). Check it:

```python
from scipy import stats
x, f = [0, 1, 2, 3, 4, 5], [447, 132, 42, 21, 3, 2]
mu = sum(a * b for a, b in zip(x, f)) / 647
s2 = sum(b * (a - mu) ** 2 for a, b in zip(x, f)) / 646
k = mu * mu / (s2 - mu)
fit = stats.nbinom(k, k / (k + mu))
print(round(fit.mean(), 4), round(fit.var(), 4))   # 0.4652 0.6919
```

Then run `python stories.py accidents --out mine.json` without `--fault`: chi-square 4.20.

</details>

## Safety and cleanup

- `stories.py` reads only `data/`, writes only the file named by `--out`, and opens no network
  connection. It never overwrites `captures.json` unless you leave out `--out`.
- Nothing runs in the background and nothing is installed outside the virtual environment.

```bash
deactivate
rm -rf .venv mine.json dominant.json t3.json fault.json
```
