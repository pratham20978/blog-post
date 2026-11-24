# Lab — Multiple Comparisons: FWER, FDR, and Tests You Didn't Count

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-11-18 · Linux x86_64 container, 2 vCPU Intel Xeon @ 2.10 GHz, 7 GiB RAM
- **Provenance:** Linux 6.18 (glibc 2.39), x86_64, 2 vCPU Intel Xeon @ 2.10 GHz, 7 GiB RAM, no GPU; Python 3.13.18; NumPy 2.5.5, SciPy 1.18.1, statsmodels 0.15.0 and their dependencies pinned in `requirements.txt`; seed 9; the full budget took 86 s and peaked at about 400 MB

This lab reproduces every number in the article. One entry point, `multiplicity.py`, runs five
stages. The first corrects the 3,170 Hedenfalk p-values by hand with Bonferroni, Holm,
Benjamini–Hochberg (BH), Benjamini–Yekutieli (BY) and Storey's q-values, and checks them against
statsmodels, SciPy and the counts Storey and Tibshirani published. The other four measure the
guarantees by simulation: correlated tests, the worst-case dependence for BH, researcher degrees
of freedom and Freedman's screened regressions. The article quotes the full budget in
`captures/full.txt`; `--quick` runs the same code on a tenth of the budget.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `multiplicity.py` | G1 | yes | the entry point; `python multiplicity.py --help` lists the stages |
| `data/hedenfalk.csv` | — | — | the 3,170 tests: observed \|t\|, count of permutation statistics at or above it, p-value; provenance in its header |
| `requirements.txt` | — | — | exact versions of every package the run imported |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |
| `captures/full.txt` | — | — | the run the article quotes (full budget), to compare with yours |
| `captures/quick.txt` | — | — | the same run at the `--quick` budget |
| `captures/results-full.json`, `captures/results-quick.json` | — | — | every number of those runs, machine-readable |

## What you need

| | |
|---|---|
| Hardware | any laptop; about 400 MB of free memory for the full budget, 250 MB for `--quick` |
| Software | Python 3.13 (the version tested; the pins are resolved for it) and the packages in `requirements.txt`; `uv` or `pip`, no root |
| Privileges | none: no root, no Docker, nothing outside this folder |
| Disk, network, time | about 150 MB of packages, fetched once; no network after that (the optional `recompute` stage downloads 2.4 MB); `--quick` runs in about 15 s and the full budget in about 90 s on two cores |

## Run

```bash
uv venv .venv && . .venv/bin/activate     # or: python3 -m venv .venv && . .venv/bin/activate
uv pip install -r requirements.txt         # or: pip install -r requirements.txt
python multiplicity.py --quick             # every stage at the small budget, about 15 s
python multiplicity.py --out mine.json     # the article's budget, about 90 s
```

Run one stage by naming it: `python multiplicity.py procedures`. The exit status is 1 when a
reconciliation check fails, so the run doubles as a test.

## What to expect

The `procedures` stage is exact: on any machine it prints Bonferroni 2, Holm 2, BH 94, BY 0 and
Storey q 162 discoveries at 5%, the three π0 estimates to seven decimals (0.6758154, 0.6699224,
0.6635132) and eight `PASS` lines. A different number there means a changed CSV or a library whose
defaults moved, never noise.

The simulated stages are reproducible to the digit with seed 9, the same budget and the versions
pinned here. With another seed or another budget, each rate should land within three of its
printed MCSEs of the capture. One line is expected to disagree with a paper: Storey and
Tibshirani's BH counts (21, 88, 153) do not come back from these p-values (24, 94, 157). Neither
m = 3,226 nor a step-down variant reproduces all three, so the article reports it as an open
discrepancy.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer
hidden below it. This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: the five discovery counts and the paper's q-values

Run `python multiplicity.py procedures` and compare the `Discoveries at 5%` line and the
`Against Storey & Tibshirani` block with `captures/full.txt`.

**Self-check:** 2, 2, 94, 0 and 162; the paper recipe's q-value counts read `[80, 159, 231]`
against the published `[80, 160, 231]`; all eight checks print `PASS`.

<details><summary>Answer</summary>

The counts are exact, so any difference is a real one. The q-values come back within one gene of
the paper at every cutoff because the package's p-values are the paper's own analysis rerun with
fresh permutations: the gene the paper ranks 8th has the same p-value (5.05 × 10⁻⁵), the 47th
differs in the third digit (4.86 × 10⁻⁴ here, 4.79 × 10⁻⁴ there). If a `PASS` turns into `FAIL`,
read the `max |diff|` it prints: anything above 10⁻¹² is a changed implementation, not rounding.

</details>

### E2 — Inspect: what a q-value is made of

Storey's q-values are π0 times the BH-adjusted p-values, so a q-value cutoff is a BH cutoff in
disguise. Check it, and look at the tie the second-smallest p-value makes with Bonferroni's line:

```python
import numpy as np
import multiplicity as lab

_, null_ge, p = lab.load_hedenfalk()
pi0 = lab.pi0_storey(p)                        # qvalue 2.x defaults
ratio = lab.qvalues(p, pi0) / lab.adjust_bh(p)
print("pi0", round(pi0, 7), "q / BH-adjusted:", ratio.min(), ratio.max())
print("q <= 0.05 is BH at", round(0.05 / pi0, 4))
k = np.argsort(p)[1]
print("p_(2) =", null_ge[k], "/ 317000; m * p_(2) == 0.05:", p.size * p[k] == 0.05)
```

**Self-check:** the ratio is 0.6699224 for every gene, so `q ≤ 0.05` is BH run at 0.0746; the
second-smallest p-value times 3,170 is exactly 0.05.

<details><summary>Answer</summary>

Storey's gain over BH is the factor 1/π0 = 1.49 on the level: 162 genes instead of 94. The tie is
a property of permutation p-values. Each is a count over 317,000, and 5/317,000 = 1/63,400 = 0.05/3,170
to the last bit, so Bonferroni with `≤` rejects two genes and with `<` rejects one. Libraries use
`≤` (R's `p.adjust`, statsmodels and SciPy agree), but a hand-rolled `<` would silently lose a gene.

</details>

### E3 — Predict: BH and Storey at correlation 0.3

Before you run anything, write down what you expect at ρ = 0.3 for BH's FDR, for the chance that
more than 10% of BH's discoveries are false, and for Storey's FDR, using the ρ = 0 and ρ = 0.5
rows of `captures/full.txt` as anchors. Then run `python multiplicity.py dependence --quick` and
read the `rho = 0.3` block.

**Self-check:** BH's FDR stays at or below q·m0/m = 0.0335; P(FDP > 10%) sits far above its
ρ = 0 value; Storey's FDR is well above 5%. The reason in each case is the one the article gives.

<details><summary>Answer</summary>

Full budget, ρ = 0.3: BH's FDR is 0.0277 ± 0.0004, so the expectation holds, because one-sided
tests of positively correlated normal statistics satisfy BH's dependence condition (PRDS). But
P(FDP > 10%) is 0.0868 ± 0.0020 against 0.0018 ± 0.0003 under independence: a shared shift moves
all null p-values together, so a study gets either almost no false discoveries or many. Storey's
FDR is 0.1887 ± 0.0019. Its π0 estimate is read off the same shifted p-values. When the shift pushes
them down, the estimate falls (its 5th percentile is 0.000, the 1/m floor the lab clips it to), the q-values shrink and the list floods
with nulls. The quick budget gives the same picture with MCSEs about three times larger.

</details>

### E4 — Diagnose: a BH that agrees at 5% and is still wrong

Run `python multiplicity.py procedures --fault stepdown`. The `Discoveries at 5%` line still says
BH 94, yet four checks fail and the run exits with status 1. Find the cause before you open the
answer: what changed, which observation proves it, and how you would confirm the fix.

**Self-check:** you can name the symptom (reconciliation fails though the 5% count is unchanged),
the cause (the adjusted p-values use a running maximum, which turns BH into a step-down rule), the
observation (the BH counts at 0.03 and 0.07 drop) and the check (all eight `PASS` without the
flag).

<details><summary>Answer</summary>

`adjust_bh` with `fault="stepdown"` takes the running maximum of m·p₍ᵢ₎/i from the smallest
p-value up, which is Holm's pattern. BH needs the running minimum from the largest p-value down:
it rejects everything up to the last crossing of its line, even below a rank that sits above the
line. At 5% the two agree on these data, because no rank below 94 sits above the line. At 0.03 and
0.07 they do not: 21 and 153 instead of 24 and 157. That is the observation the counts give you.
statsmodels and SciPy disagree by up to 8.7 × 10⁻³ in BH-adjusted p-value and 7.5 × 10⁻² in
BY-adjusted p-value, which is what the checks see. Remove the flag, or restore `np.minimum.accumulate(r[::-1])[::-1]`, and all eight checks pass.
A matching headline count proves nothing about the procedure that produced it.

</details>

## Safety and cleanup

- The lab reads `data/hedenfalk.csv` and writes only the `--out` file you name. It contacts no
  service; the optional `recompute` stage downloads `hedenfalk.RData` from GitHub, checks its
  SHA-256, reads it and deletes it.
- Nothing is installed outside `.venv`.

```bash
deactivate 2>/dev/null; rm -rf .venv mine.json
```
