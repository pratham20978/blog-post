# Lab — Few-Step Diffusion and Distillation: 20 Steps Into 1

- **Grade:** G1 · runs anywhere (CPU PyTorch and numpy)
- **Executed:** yes · 2026-10-16 · AMD Ryzen 7 5825U laptop, Ubuntu 26.04.1, no GPU
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs; the run used 8 worker processes, one thread each), 14 GB RAM; Python 3.12.15, numpy 2.5.3, torch 2.14.0+cpu

This lab trains few-step students against a teacher whose answers are exact. The teacher is the
exact denoiser $E[x_0 \mid x]$ of part 5's "crescent world" at 8×8 pixels (four bright crescents, a
brightness offset shared by every pixel with standard deviation 0.3, and per-pixel detail of 0.1),
and the exact probability-flow ODE it defines, solved by RK4 to about $10^{-10}$. Every student is a
small network trained on the CPU, warm-started from a network copy of that denoiser, so every error
measured here is the student's. `distill.py` is the one entry point. It computes the article's worked
example in closed form, measures DDIM and DPM-Solver++(2M) with the exact denoiser, trains direct
regression, progressive distillation, consistency distillation, three distribution-matching variants
and a shortcut model with two seeds each, and writes every number to `captures.json`. Every measured
number and figure in the article comes from the `captures.json` this script wrote on the machine
above; numbers the article quotes from papers come from the papers.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `distill.py` | G1 | yes | the entry point: `worked`, `reference`, `teacher`, `students`, `samples`, `all`, and the `dmd` probe |
| `requirements.txt` | — | — | the two pinned packages |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop with about 4 GB of free RAM: `all --quick` peaked at about 3.3 GB across the main process and its 8 workers, and the full run trains the same networks with the same batch sizes, only for longer |
| Software | Python 3 with numpy 2.5.3 and the CPU build of torch 2.14.0. The author's run used Python 3.12.15; the notebook's cells (`all --quick` and every exercise) also ran on Python 3.14.4 with the same two packages |
| Privileges | none: no root, no Docker, no GPU, nothing outside this folder and its virtual environment |
| Disk, network, time | about 200 MB to download for torch and 800 MB installed, no dataset; the full `all` run took about 20 min on the machine above with 8 workers, `all --quick` about 4.5 |

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install numpy==2.5.3
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.0+cpu
python distill.py worked              # ~25 s: the worked example in closed form, and a 1-D student
python distill.py all --quick         # everything with shorter training, ~4.5 min
python distill.py all                 # the article's run, ~20 min with 8 workers
python distill.py dmd --quick --ratio 1 --warm 0 --steps 300    # one distribution-matching run: the one E4 diagnoses
```

`all` rewrites `captures.json`; any other stage adds its section to it. Pass `--out mine.json` to
keep the shipped capture for comparison. `--workers N` sets the number of parallel processes
(default: cores − 2, at most 8), `--seeds N` the seeds per student (default 2). Every trained network
and the reference solutions are cached in `.cache/` under a hash of the script, so an interrupted
run resumes, and any edit to `distill.py` retrains from scratch.

## What to expect

The first line is the provenance of your run. Then (excerpt from the author's run; its last line
names `captures.new.json` because that run wrote to a new file, renamed to `captures.json` once it
finished, and yours names the file you passed to `--out`):

```text
  worked: a=5.1788; at x=40 (eps 0.5) D(x;80)=0.1676, DDIM 1/2/4 steps 0.1676/4.2485/5.0207, exact 5.1489
  worked: halving 4->2 at x=40: teacher 8.8948 -> 1.9367; student target 0.7012 against D 0.1676; cliff +4.8632 / -4.8632
  worked: flow-map check D-bar by jump 3.26999, by path average 3.26999; 1-D student ramp -0.0104..+0.0148, between crescents 0.0099
  reference: RK4 self-check rms 2.99e-10; data-to-data sample distance 0.0336; exact endpoints 0.0453
  reference ddim     1:0.714/0.707/1.00 2:0.334/0.243/0.76 4:0.172/0.128/0.23 8:0.120/0.083/0.02 16:0.084/0.059/0.00 32:0.057/0.051/0.00 128:0.020/0.046/0.00   (calls: error / sample distance / blends)
  reference dpmpp2m  1:0.714/0.707/1.00 2:0.334/0.243/0.76 4:0.130/0.055/0.15 8:0.115/0.063/0.00 16:0.068/0.046/0.00 32:0.037/0.045/0.00 128:0.000/0.045/0.00   (calls: error / sample distance / blends)
  teacher network: 20000 steps; error against the exact denoiser at sigma 1 / 2 / 80: 0.0409 / 0.0468 / 0.0111; its DDIM at 128 calls: error 0.1219, flips 0.0178
  student progressive distillation       seed 1: 1 call: flips 0.0376, blends 0.1658, error 0.1564, sample distance 0.0462, cover [0.2537, 0.2468, 0.2415, 0.2581] (767 s)
  student progressive distillation       seed 2: 1 call: flips 0.0366, blends 0.1621, error 0.1557, sample distance 0.0467, cover [0.2542, 0.2454, 0.2424, 0.2581] (766 s)
  …
  student DMD + regression loss          seed 1: 1 call: flips 0.0984, blends 0.3171, error 0.2648, sample distance 0.0556, cover [0.251, 0.2495, 0.2515, 0.248] (227 s)
  student DMD + regression loss          seed 2: 1 call: flips 0.0967, blends 0.3105, error 0.2647, sample distance 0.0553, cover [0.2415, 0.252, 0.2502, 0.2563] (227 s)
  …
  student progressive distillation       seed 1: 1:0.038/0.046 2:0.030/0.042 4:0.029/0.040 8:0.026/0.039 16:0.020/0.041 32:0.018/0.042   (calls: flips / sample distance)
  student consistency distillation       seed 1: 1:0.031/0.049 2:0.163/0.042 3:0.575/0.057 4:0.667/0.053 8:0.747/0.045   (calls: flips / sample distance)
  …
wrote captures.new.json in 1213 s
```

**Exact:** every `worked` line, and the `reference` lines, which use only the closed-form denoiser
and fixed seeds; they match on any machine to the digits printed. **Close:** the teacher network and
every student. Training is seeded, but matrix products sum in a different order on another CPU, and a
trained network amplifies that: expect flip and blend shares within a few tenths of a percentage
point of the author's, sample distances within about 0.003, and the same orderings. The `seed 1` and
`seed 2` lines show the spread between two seeds on one machine, which is a fair guide to the spread
between machines. **Statistical:** the share of noises in each margin bin, from 4,096 samples.

The `reference` line for the exact endpoints matters: `RK4 self-check rms` must be far below 0.001,
or the "exact path" every student is measured against is not exact.

## Exercises

Do them in order. Each has a self-check you can mark yourself against, with the answer from the
author's run hidden below it. This is an L3 post, so the lab ships E1 to E4.

### E1 — Reproduce: the distillation target at x = 40

Run `python distill.py worked --out mine.json`. The article's worked example computes, by hand, the
target that a two-step progressive-distillation student must output at $x = 40$, $\sigma = 80$,
when its teacher is DDIM on four steps. Find it in the output, with the true denoiser's answer at the
same point and the exact endpoint of the path from $x = 40$.

**Self-check:** the `student target` line prints 0.7012 against `D` 0.1676, the row for $\varepsilon = 0.5$
ends at the exact endpoint 5.1489, and the cliff line prints ±4.8632; your provenance line printed first.

<details><summary>Answer</summary>

Two lines of the `worked` output carry it:

```text
  worked: a=5.1788; at x=40 (eps 0.5) D(x;80)=0.1676, DDIM 1/2/4 steps 0.1676/4.2485/5.0207, exact 5.1489
  worked: halving 4->2 at x=40: teacher 8.8948 -> 1.9367; student target 0.7012 against D 0.1676; cliff +4.8632 / -4.8632
```

The teacher's two DDIM steps on the four-step grid take $x = 40$ at $\sigma = 80$ to 8.8948 and then to
1.9367 at $\sigma'' = 2.5152$. Inverting one DDIM step from $\sigma = 80$ straight to $\sigma''$ gives the
student's target, $(1.9367 - (2.5152/80)\cdot 40)/(1 - 2.5152/80) = 0.7012$, against the true
denoiser's 0.1676 at the same point: the student is told to commit about four times further toward
the crescent at +5.18. A two-step student that hits both of its targets lands where four DDIM steps
land, 5.0207, not where two land, 4.2485; the exact path ends at 5.1489. Two noises 0.002 apart,
$\varepsilon = \pm 0.001$, end at +4.8632 and −4.8632. Every number in these lines is closed-form, so
yours match to the digits printed.

</details>

### E2 — Inspect: where the flips come from

In the shipped `captures.json`, `students → regression → 1 → steps → 1 → flip_by_margin` lists the
share of starting noises that the one-call regression student sends to a different crescent than the
exact path, in each margin bin of `margin_bins`, and `margin_share` lists the share of all 4,096
noises in each bin. Compute what share of all of that student's flips come from noises with margin
below 0.1, and what share of all noises those bins hold.

**Self-check:** two percentages, the first several times the second.

<details><summary>Answer</summary>

`margin_bins` is `[0, 0.025, 0.05, 0.1, 0.2, 0.4, 0.8, 10]`, so a margin below 0.1 is the first three
bins, and `margin_share` gives them $0.0327 + 0.0378 + 0.0625 = 0.133$ of all noises. Each
`flip_by_margin` entry is the flip rate within its bin, so a bin contributes its rate times its share.
For seed 1, $(0.2612 \cdot 0.0327 + 0.2000 \cdot 0.0378 + 0.1094 \cdot 0.0625) = 0.02294$ out of
0.03074 summed over all seven bins: **74.6%** of the flips. Seed 2 gives **77.5%**. The sum over all bins
is the student's overall flip rate, which matches its `flip` field (0.0308 and 0.0293). So the 13.3%
of noises nearest a decision boundary produce three quarters of the student's wrong decisions, and the
two bins from 0.4 up, 53% of the noises, produce none.

</details>

### E3 — Predict: the same halving at x = 1.6

At $x = 1.6$ ($\varepsilon = 0.02$) the true denoiser at $\sigma = 80$ answers 0.0067, and two DDIM calls
land at 0.240, almost on the midpoint between the crescents. Before running anything, predict the
ratio of the two-step student's target to the denoiser's answer at this point, and say why. Then run
`python distill.py worked --x 1.6 --out mine.json`.

**Self-check:** your ratio within 10% of the printed one, for the reason that near the midpoint
every step of the teacher is linear in $x$.

<details><summary>Answer</summary>

The run prints:

```text
  worked: halving 4->2 at x=1.6: teacher 0.3558 -> 0.0777; student target 0.0283 against D 0.0067; cliff +4.8632 / -4.8632
```

The ratio is $0.0283 / 0.0067 = 4.22$, against $0.7012 / 0.1676 = 4.18$ at $x = 40$, and the prediction
is that it barely moves. Near the midpoint the posterior over the two crescents is close to even, so
the denoiser is close to linear in $x$ at every noise level the teacher visits, $D(x;\sigma) \approx
k(\sigma)\,x$. Each DDIM step $x' = D + (\sigma'/\sigma)(x - D)$ is then a linear map, two of them compose
into one, and the target $(x'' - (\sigma''/\sigma)x)/(1 - \sigma''/\sigma)$ is linear in $x$ too. The ratio
of two linear functions through zero is a constant, so the target is about 4.2 times the denoiser's
answer wherever the path starts near the midpoint. What separates 4.18 from 4.22 is the slight bend
the second teacher step meets at $x = 40$, where it starts from 8.89 at $\sigma \approx 17.5$, plus the
rounding of the printed digits.

</details>

### E4 — Diagnose: every sample shows one crescent

Run `python distill.py dmd --quick --ratio 1 --warm 0 --steps 300 --out mine.json`. It trains one
distribution-matching student for 300 generator updates, with one fake-denoiser update per generator
update and no warm-up, prints the share of the samples of 1,024 fixed noises on each crescent at
update 0, every 250 updates and at the end, then evaluates the student on the 4,096 evaluation noises.
Every final sample lands on the same crescent, and the sample distance is worse than one DDIM call's
blur. Treat it as a run someone else stopped: find the cause, the one observation that proves it, and
a fix that uses only the stage's flags.

**Self-check:** the cause in one sentence, the observation in a printed trace that proves it, and a
rerun with the same seed whose final coverage puts every crescent between 0.15 and 0.35.

<details><summary>Answer</summary>

**Symptom.** The last lines read:

```text
  dmd probe ratio 1:1, warm-up 0: step     0 cover [0.187, 0.263, 0.33, 0.221]
  dmd probe ratio 1:1, warm-up 0: step   250 cover [0.0, 0.0, 1.0, 0.0]
  dmd probe ratio 1:1, warm-up 0: step   299 cover [0.0, 0.0, 1.0, 0.0]
  dmd probe final: flips 0.7522, blends 0.8179, sample distance 0.8063, cover [0.0, 0.0, 1.0, 0.0]
```

Every sample is on the third crescent, 82% of them are blends, and the sample distance, 0.806, is
worse than one DDIM call's 0.707.

**Cause.** The run stopped inside a phase every distribution-matching run in this lab goes through:
the generator starts as the teacher's answer at $\sigma = 80$, the blur, so its samples move together
and land on one crescent, and only once the fake denoiser has learned where they are does the
difference between the two denoisers push them apart again.

**Observation.** The trace's first row covers all four crescents, so the generator's start and the
sampler are sound and the modes were lost during training. A longer run with the same seed proves it
is a phase, not the end state: it prints the same rows at updates 0 and 250, and then

```text
  dmd probe ratio 1:1, warm-up 0: step   500 cover [0.326, 0.234, 0.299, 0.141]
  dmd probe ratio 1:1, warm-up 0: step   750 cover [0.293, 0.247, 0.235, 0.225]
```

**Fix and check.** Train for longer: `python distill.py dmd --quick --ratio 1 --warm 0 --steps 3000
--out mine.json`, under a minute on the machine above. Its final line ends `cover [0.2354, 0.2432,
0.26, 0.2615]`, every crescent between 0.15 and 0.35, with flips 0.124, blends 0.394 and sample
distance 0.075. The stage's other flags do not remove the phase. In the author's probes with the same
seed, `--ratio 5`, `--warm 2000` and both together still put every sample on one crescent at update
250, and with the warm-up the collapse lasted longer: 97% and 99.6% of the samples on one crescent at
update 500, where the runs without it already had 14–34% on each. The article's full runs show the
same phase at their own scale (Figure 7). Delete `mine.json` to put the folder back.

</details>

## Safety and cleanup

- The lab touches nothing outside this folder: no network access after installation, no service, no
  GPU, no shared lab server.
- It writes `captures.json` (or the file named by `--out`) and `.cache/` here, and nothing else.

```bash
rm -rf .cache            # cached reference solutions and trained networks
deactivate; rm -rf .venv # the environment, if you made one here
```
