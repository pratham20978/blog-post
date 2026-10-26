# Lab — Evaluating Generative Models: What FID Measures and Hides

- **Grade:** G1 · runs anywhere
- **Executed:** yes · 2026-10-21 · the build machine (laptop CPU, one thread)
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs, run on one thread), 14 GB RAM; Python 3.12.15, numpy 2.5.3; `evaluate.py` 03f15086ec25. The notebook was built and executed with Python 3.14.4 and the same numpy pin.

This lab reproduces every number the article calls measured. Crescent world is a toy whose true
distribution is known exactly: every 8×8 image shows one of four crescents, faint or strong, with a
random brightness and a little pixel noise. Because the truth is known, every generator below has a
known defect, and every metric can be graded against it. The one entry point is `evaluate.py`; it
writes `captures.json` (or the file you name with `--out`) and prints the same numbers. Every metric
runs on the 64 pixel values, or on five "detector" features; the real FID runs the same arithmetic on
2,048 Inception-v3 features, and nothing here downloads a network.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `evaluate.py` | G1 | yes | crescent world, part 8's exact guided sampler, the five generators, and FD, KID, precision, recall, density and coverage in numpy |
| `requirements.txt` | — | — | the one pinned dependency, numpy |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at 0.31 GB of RAM |
| Software | Python 3 (run on 3.12.15 and 3.14.4) and numpy 2.5.3: `pip install -r requirements.txt` into a virtual environment, or `uv run --with numpy==2.5.3` |
| Privileges | none: no root, no Docker, no network access, nothing outside this folder |
| Disk, network, time | no downloads beyond numpy; `all` takes about 45 s on one core (worked 0 s, failures 11 s, bias 10 s, guidance 24 s) |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python evaluate.py all --out mine.json          # keeps the shipped captures.json for comparison
```

Each stage also runs alone: `python evaluate.py worked`, `failures`, `bias` or `guidance`. `--quick`
halves the sample sizes and cuts the repeats, for a faster and noisier run. `failures --grain G` runs
the grainy generator at a grain you choose instead of the tuned one.

## What to expect

The first line is the provenance line. Then, stage by stage:

- `worked`: the article's eight real contrasts (mean 0.7500, spread 0.2525) and three generators with
  FD 0.1096, 0.0100 and 0.0000; then precision, recall, density and coverage of 1.000, 0.500, 1.500,
  0.500 for the strong-only set, and 0.833, 1.000, 1.250, 0.500 with one stray sample added.
- `failures`: the grain is tuned to 0.3319 so that the grainy generator's FD equals the faint-dropper's,
  3.6221. The perfect generator scores FD 0.0143, the copier 0.0133 and the Gaussian blob 0.0158.
- `bias`: the perfect generator's FD falls from 0.0736 at N = 1,000 to 0.0011 at 64,000, fitted as
  0.0007 + 59.9/N; the grainy one (grain 0.07) from 0.0923 to 0.0300, fitted as 0.0291 + 63.7/N.
- `guidance`: FD from 0.0298 at w = 1 to 9.1318 at 7.5; recall 0.666, down to 0.544 at w = 5, back up
  to 0.725 at 7.5; coverage from 0.984 to 0.266.

Every value is deterministic: two runs on the build machine agreed in every digit. On numpy 2.5.3
with one thread, expect FD to four decimals and the k-NN metrics to three; a different BLAS or numpy
may move FD in the fifth decimal, because matrix products add numbers in a different order.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer
hidden below it. This is an L2 post, so the lab ships E1 to E3.

### E1 — Reproduce: the tied pair

Run the failures stage into your own file and find the faint-dropper's and the grainy generator's FD,
precision, recall and coverage.

```bash
python evaluate.py failures --out mine.json
```

**Self-check:** both FDs read 3.6221 with the grain tuned to 0.3319; the faint-dropper reads precision
0.817, recall 0.394, coverage 0.504; the grainy generator 0.000, 1.000, 0.000; and the provenance line
printed first.

<details><summary>Answer</summary>

The author's run printed `drops faint: FD 3.6221 ... precision 0.817, recall 0.394, density 1.018,
coverage 0.504` and `grainy: FD 3.6221 ... precision 0.000, recall 1.000, density 0.000, coverage
0.000`, with `grain tuned to 0.3319`. The precision of 0.000 is 2 samples in 4,096 (0.000488 in
`captures.json`). If your FDs differ in the fourth decimal, compare numpy versions first; if they
differ more, check that you ran `failures` without `--grain` and without `--quick`.

</details>

### E2 — Inspect: what recall counted at w = 7.5

The article says recall rebounds at w = 7.5 because a few stray faint samples have huge balls. Find
the evidence in the capture: under `guidance` → `weights` → `"7.5"`, read `faint` (the share of
generated samples that are faint), `faint_holders` (how many generated samples have at least one real
faint image inside their ball), `faint_holder_radius_median`, `fake_radius_median`, `recall_faint` and
`coverage_faint`.

**Self-check:** name the number of holders, their median ball radius against the typical one, and the
share of real faint images that recall and coverage each credit.

<details><summary>Answer</summary>

`faint` is 0.000977, 4 samples in 4,096, and `faint_holders` is 4: the last four faint samples are the
only generated samples whose balls hold real faint images. Their median radius is 2.921 against 0.925
for all generated samples, because their nearest generated neighbours are strong crescents far away.
`recall_faint` is 0.996, so recall counts 99.6% of the real faint images as covered, while
`coverage_faint` is 0.003: only 0.3% of the real faint images have a generated sample inside their own
ball. Compare w = 5: 52 holders with median radius 1.145, `recall_faint` 0.619, `coverage_faint` 0.078.

</details>

### E3 — Predict: a little grain

Before running, predict the FD, and the direction of precision and recall, for the grainy generator at
grain 0.05 instead of the tuned 0.3319. Use the article's model: FD adds a spread term per direction.
Here 59 of the 64 pixel directions carry only the pixel detail, with standard deviation 0.1, and grain
g raises it to √(0.1² + g²); add that cost to the perfect generator's 0.0143, which is the sampling
floor. Then run:

```bash
python evaluate.py failures --grain 0.05 --out mine.json
```

**Self-check:** your FD within ±0.006 of the run's, precision falling well below the perfect
generator's 0.807, recall staying above 0.9, for the reason that FD charges the squared change in
spread while every grainy sample leaves its real neighbours' balls.

<details><summary>Answer</summary>

The model gives 0.0143 + 59 × (√0.0125 − 0.1)² = 0.0143 + 59 × 0.000139 = 0.0225. The run printed
FD 0.0185, precision 0.482, recall 0.962, density 0.386 and coverage 0.776. FD barely moves because a
12% wider spread costs its square, about 0.00014 per direction; precision halves because in 64
dimensions the extra noise pushes about half the samples outside every real sample's ball. A small
grain is nearly invisible to FD and obvious to precision.

</details>

### E3 — Predict: the sample count

From the bias stage's fit for the perfect generator, FD ≈ 0.0007 + 59.9/N, predict its FD at
N = 2,000, then check it against the run.

```bash
python evaluate.py bias --out mine.json
```

**Self-check:** within ±0.003 of the run's value at N = 2,000, for the reason that the bias falls like
1/N, so halving N from 4,000 roughly doubles it.

<details><summary>Answer</summary>

0.0007 + 59.9/2,000 = 0.0307. The run printed 0.0299 at N = 2,000 (and 0.0174 at 4,000). At N = 1,000
the measured 0.0736 sits above the line's 0.0606: below a few thousand samples in 64 dimensions the
next-order terms of the bias are no longer small, which is why the fit starts at 2,000.

</details>

## Safety and cleanup

- The lab reads and writes only files in this folder. It contacts no service, downloads nothing and
  needs no network.
- It writes `captures.json`, or the file named with `--out`; the exercises write `mine.json`, so the
  shipped capture stays as it is.

```bash
rm -f mine.json && rm -rf .venv __pycache__
```
