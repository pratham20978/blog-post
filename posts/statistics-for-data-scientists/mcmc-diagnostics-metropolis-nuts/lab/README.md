# Lab — MCMC You Can Trust: Metropolis by Hand, R-hat and ESS

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-11-27 · the build machine (a laptop CPU)
- **Provenance:** Linux 7.0.0-43-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs), 14 GB RAM; Python 3.12.16, NumPy 2.5.4, SciPy 1.18.1, PyMC 6.4.0, PyTensor 3.3.8, ArviZ 1.3.0 (arviz-stats 1.3.3, arviz-base 1.3.1), xarray 2026.9.0; `mcmc.py` e8731e385f0c, root seed 20261127. The notebook was built and executed with the same pins. The author also checked the lab privately against R 4.5.2: the `posterior` package 1.8.1, installed into a separate library, computed R-hat (rank-normalised and the basic split and unsplit forms), bulk and tail ESS, the ESS for the mean and the MCSEs of the mean and of the 2.5% and 97.5% quantiles on the full run's trial and accidents chains, and matched the lab to 5.0 × 10⁻¹² relative; base R's `qbeta`, `integrate` and `dnbinom` reproduced the trial's exact quantiles and mean and the accidents grid's summaries to 1.6 × 10⁻¹² (the `author_crosscheck` key in `captures.json`).

This lab reproduces every number the article calls computed or measured. It writes random-walk Metropolis from
scratch, runs it on the trial posterior beta(8.700102, 163) from *Bayesian Inference by Hand: Conjugacy and Credible
Intervals* and checks the draws against the closed form; tunes the proposal step; samples Greenwood and Yule's negative
binomial posterior and checks it against an 801 × 801 grid; computes autocorrelation, ESS, MCSE and the four R-hats by
hand and matches them to ArviZ; measures how often the standard errors cover the truth and what the thresholds 1.1 and
1.01 let through; shows a bimodal posterior that fools every diagnostic; and fits the accidents model with NUTS in PyMC.
The one entry point is `mcmc.py`; it prints its numbers and writes them to the file you name with `--out`.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `mcmc.py` | G1 | yes | the eight stages: `pfizer`, `tuning`, `nb`, `diagnostics`, `mcse`, `rhat`, `bimodal`, `nuts` |
| `data/greenwood_yule1920_accidents.csv` | — | — | Greenwood and Yule's 647 women by number of accidents, with provenance |
| `data/clarke1946_flying_bombs.csv` | — | — | Clarke's 576 squares of south London by flying-bomb hits, for E5, with provenance |
| `requirements.txt` | — | — | the pinned dependencies: NumPy, SciPy, PyMC, PyTensor, ArviZ and what ArviZ reads |
| `captures.json` | — | — | the author's full run, machine-readable, with the private R cross-check; every figure reads it |
| `captures-quick.json` | — | — | the author's `--quick` run, to compare with yours digit for digit |
| `expected-output.txt` | — | — | the full run as printed |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.48 GB of RAM, the quick run at 0.43 GB |
| Software | Python 3.12 and the pins in `requirements.txt`, installed into a virtual environment (no root) |
| Privileges | none: no root, no Docker, nothing outside this folder and the virtual environment |
| Disk, network, time | the install is about 440 MB and needs the network once; then `all --quick` takes about 23 s and `all` about 2 min 25 s on the build machine; the first `nuts` run spends several seconds compiling the model |

## Run

```bash
python3.12 -m venv .venv && . .venv/bin/activate      # or: uv venv --python 3.12 && . .venv/bin/activate
pip install -r requirements.txt
python mcmc.py all --quick --out quick.json            # the reader's budget, about 23 s
python mcmc.py all --out mine.json                     # the article's budget, about 2.5 min
```

One stage at a time: `python mcmc.py pfizer --quick --out quick.json`. A run adds or replaces its stages' keys in the
file you name, so stages can be run in any order. Never point `--out` at `captures.json`; that file is the author's run
to compare against.

## What to expect

The quick run's `pfizer` stage prints, after its provenance line:

```text
  4 chains from theta = 0.005, 0.03, 0.15, 0.4; warmup 500 discarded, 1000 kept each; step 0.04; acceptance 43.5%, 44.2%, 42.1%, 41.5%
  R-hat 1.0011; bulk ESS 811; tail ESS 822 (of S = 4000)
  VE   q025: chain 90.072% +- 0.442 (MCSE); exact 90.317%; z = -0.55
  VE   q975: chain 97.619% +- 0.104 (MCSE); exact 97.617%; z = +0.02
  check: PASS: every estimate within 3 MCSE of the closed form
```

Every random number comes from a seeded stream, `SeedSequence([stage, sub-stream, seed])`, so with these pins on
x86-64 Linux a run repeats `captures-quick.json` and `captures.json` digit for digit. On another platform or with other
versions, expect the Metropolis stages to agree to the digits printed and the `nuts` stage to differ in later digits
(PyTensor's compiled code can add in a different order). What must hold anywhere: every `check:` line prints PASS, and
R-hat is below 1.01 in the `pfizer`, `nb` and `nuts` stages. The other stages show slow or failing chains on purpose and
their R-hats say so: the bad steps in `tuning` and `mcse`, the cases in `rhat`, and the dispersed run in `bimodal`, whose
one-mode run passes every diagnostic and is wrong. On the quick budget the long-jump `bimodal` run is also above 1.01
(1.0161), from too few draws.

The stages:

- `pfizer`: the first eight iterations step by step, four chains on the trial posterior, estimates against the closed form.
- `tuning`: traces at steps 0.002, 0.04 and 1.0; ESS per draw against acceptance over 25 scales, in one and two dimensions.
- `nb`: Greenwood and Yule's negative binomial with priors log μ, log k ~ N(0, 2²); adaptive warmup; the grid check.
- `diagnostics`: every diagnostic by hand against arviz-stats, and the pieces of the hand computation (W, B, autocorrelations, Geyer's truncation, the quantile MCSE).
- `mcse`: 2,000 replicates per step (200 on `--quick`) of how often estimate ± 1.96 standard errors covers the exact value.
- `rhat`: a shared trend; Vehtari et al.'s constructed shifted and narrow chains; R-hat against the real error over 3,200 short runs (320 on `--quick`).
- `bimodal`: 0.7 N(0, 1) + 0.3 N(16, 1) from one mode, from both, and with long proposals; how often chains cross at four separations.
- `nuts`: the accidents model in PyMC with NUTS, read through its diagnostics and checked against the grid.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer hidden below it. This
is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: the trial's interval from your own chains

Run the `pfizer` stage on the quick budget into your own file and compare it with `captures-quick.json`.

```bash
python mcmc.py pfizer --quick --out mine.json
```

**Self-check:** the provenance line prints your versions; the four VE estimates, R-hat 1.0011 and bulk ESS 811 match
`captures-quick.json` (digit for digit with these pins), and the check prints PASS.

<details><summary>Answer</summary>

**Answer.** The author's quick run gives the interval as 90.072% ± 0.442 to 97.619% ± 0.104 against the exact 90.317%
to 97.617% (z = −0.55 and +0.02), R-hat 1.0011, bulk ESS 811 and tail ESS 822 of 4,000 draws, and acceptance 41.5% to
44.2%. If your digits differ with the same pins, check that you ran `--quick` (the full run keeps 5,000 draws per chain
and gives 90.474% to 97.519%) and that `mcmc.py` is unmodified: its SHA-1 prefix, e8731e385f0c, is in the provenance
line.

</details>

### E2 — Inspect: the tail ESS that ArviZ prints by default

The article says ArviZ's tail ESS on xarray input defaults to the 11% and 89% quantiles, not the 5% and 95% of Vehtari
et al. Run the `diagnostics` stage and find, in `mine.json`, both tail ESS values for the accidents model's μ: under
`diagnostics` → `nb_mu`, the `mine` entry's `ess_tail` (5% and 95%) and `ess_tail_11_89`, and the `arviz` entry's
`ess_tail_default_xarray`.

```bash
python mcmc.py diagnostics --quick --out mine.json
```

**Self-check:** state which two of the three numbers are equal, and why, before you open the answer.

<details><summary>Answer</summary>

**Answer.** On the quick budget the 5%/95% tail ESS is 1,336.5, and the hand-computed 11%/89% value and ArviZ's default
are both 1,298.7: they agree to the last bit because ArviZ fills the missing `prob` with `rcParams["stats.ci_prob"]`,
0.89, and its `_ess_tail` turns 0.89 into the pair 0.11 and 0.89. For the trial's VE the same three numbers are 822.4,
748.6 and 748.6. Pass `prob=(0.05, 0.95)` to get Vehtari et al.'s definition, which R's `posterior` uses.

</details>

### E3 — Predict: a quarter of the step

At step 0.04 the quick run accepts about 43% of proposals with a bulk ESS of 811. You will rerun it at step 0.01.
Write down your prediction first: the acceptance rate, the bulk ESS and whether R-hat stays below 1.01, with the reason.

```bash
python mcmc.py pfizer --quick --step 0.01 --out e3.json
```

**Self-check:** acceptance up, to roughly 75–85%; bulk ESS down by about a factor of two to four; your reason must be
the article's: smaller proposals are accepted more often but move less, so the autocorrelation time grows.

<details><summary>Answer</summary>

**Answer.** The author's run accepts about 81% of proposals (79.6% to 81.5% by chain), gives a bulk ESS of 294 and a
tail ESS of 353, and an R-hat of 1.021, above 1.01. Every estimate still lands within 3 MCSEs of the closed form (the
largest z is −2.72), which is the point: the chains are not wrong, they are slow, and the diagnostics say so through the
ESS and R-hat rather than through the answer.

</details>

### E4 — Diagnose: a faster sampler that is wrong

An earlier draft of the `pfizer` stage sampled η = logit θ, so that no proposal falls outside 0 to 1. Run it:

```bash
python mcmc.py pfizer --quick --fault --out e4.json
```

The acceptance rates and R-hat look healthy, and the check fails. Find the cause in `mcmc.py`, name the one observation
that proves it, and fix it.

**Self-check:** symptom, cause, the proving observation, and a fix that makes the check pass.

<details><summary>Answer</summary>

**Answer.** *Symptom:* R-hat 1.0035, bulk ESS 944 and tail ESS 815, acceptance 45% to 51%, yet the mean of VE is
95.309% ± 0.052 against the exact 94.610% (z = +13.5), and the 2.5% point 91.535% against 90.317% (z = +7.0). *Cause:*
the draft calls `logp_beta_logit(x, jacobian=False)`. A chain on η must target p(θ(η)) |dθ/dη|, and for the logit
dθ/dη = θ(1 − θ); without that factor it samples p(θ)/(θ(1 − θ)), which is beta(7.700102, 162). *Proof:* that wrong
posterior has VE mean 95.200%, 2.5% point 91.119%, median 95.425% and 97.5% point 98.002%, and the faulty chains sit
within 2.4 MCSEs of all four (z = 2.11, 2.38, 0.45, 0.64), while they miss the true posterior by up to 13.5. *Fix:* call
`logp_beta_logit(x, jacobian=True)` in the `--fault` branch; the check then passes, as the same chains do on θ itself.
The convergence diagnostics could not have found this: the four chains agree perfectly, on the wrong distribution. Undo
your edit afterwards so `mcmc.py` matches its SHA-1 again.

</details>

### E5 — Extend: Clarke's flying bombs, where k is barely identified

Clarke's 576 squares (in `data/`) had 229, 211, 93, 35, 7 and 1 squares with 0, 1, 2, 3, 4 and 7 hits. *Likelihood:
The MLE, Three Tests, and Where χ² Fails* found no evidence of extra variance in them. Fit the same negative binomial
with the same priors, log μ and log k ~ N(0, 2²), by importing `metropolis`, `summarize`, `mcse_mean` and
`mcse_quantile` from `mcmc.py`, writing your own log posterior and your own grid. Expect k's posterior to be long and
mostly prior: the data say little more than "k is large".

**Self-check (acceptance test):** for μ and for k, R-hat below 1.01 and bulk and tail ESS above 400; your chains' mean
of μ and median of k within 3 MCSEs of your grid's; your grid's mass on its edge rows and columns below 10⁻⁶, which
needs log k to run far past where k's posterior looks finished; and P(k > 50) reported from both chain and grid. Explain
which diagnostic you would watch most closely when the posterior of a parameter is mostly prior.

## Safety and cleanup

- The lab reads only its two CSVs and contacts no service. It writes only the files you name with `--out` and, on the
  first `nuts` run, PyTensor's compile cache in `.pytensor/` inside this folder.
- Nothing runs in the background, and nothing outside this folder and your virtual environment changes.

```bash
rm -rf .pytensor __pycache__ quick.json mine.json e1.json e2.json e3.json e4.json
deactivate && rm -rf .venv          # if you made the environment here
```
