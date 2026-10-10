# Lab — Training a Diffusion Model: The Decisions Before Step One

- **Grade:** G1 · runs anywhere (numpy and CPU PyTorch in a pinned environment; this series' "stdlib and CPU" lab letter)
- **Executed:** yes · 2026-10-07 · AMD Ryzen 7 5825U laptop, Ubuntu 26.04.1, no GPU
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs; training runs single-threaded, 12 in parallel), 14 GB RAM; Python 3.12.15, numpy 2.5.3, torch 2.14.0+cpu

This lab measures what each pre-training decision does, on a toy whose ideal denoiser is known
exactly. The toy is "crescent world": square images of one of four bright crescents on a dark
field, plus a brightness offset shared by every pixel (standard deviation 0.3) and a little
per-pixel detail (0.1). It is a Gaussian mixture, so the best possible denoiser, $E[x_0 \mid x_t]$,
has a closed form, and every error below is measured against it. `training_decisions.py` is the one
entry point. It computes the schedules, measures the terminal-SNR leak with the exact denoiser at
16 to 16,384 pixels, and trains 50 small MLP denoisers on 8×8 crescents to compare weightings,
targets, EMA averages and widths. Every measured number and figure in the article comes from the
`captures.json` this script wrote on the machine above.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `training_decisions.py` | G1 | yes | the entry point: `schedules`, `leak`, `train` or `all` |
| `requirements.txt` | — | — | the two pinned packages and where to get the CPU build of PyTorch |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |

## What you need

| | |
|---|---|
| Hardware | any laptop; the leak experiment peaks at about 1 GB of RAM, each training worker at about 300 MB |
| Software | Python 3.10 or newer; CPU PyTorch 2.14.0 (about 200 MB) and numpy 2.5.3 |
| Privileges | none: no root, no Docker, no GPU, nothing outside this folder and its virtual environment |
| Disk, network, time | about 1 GB for the environment, no dataset download; `schedules` takes 2 s, `leak` about 12 min, `train` about 30 min on 12 cores (about 6 h on one), `all --quick` about 6 min |

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.0+cpu
pip install numpy==2.5.3
python training_decisions.py schedules        # 2 s: terminal SNR, first sampling step, the rescale
python training_decisions.py leak             # ~12 min: the brightness leak with the exact denoiser
python training_decisions.py train            # ~30 min on 12 cores: 50 small training runs
python training_decisions.py all --quick      # everything, smaller and noisier, ~6 min
```

Each command adds its section to `captures.json`; `all` rewrites it. Copy the shipped one aside
first if you want to diff against it. Finished runs are kept in `.cache/`, so an interrupted
`train` resumes where it stopped; delete `.cache/` to start over. The leak result is cached under
a hash of the script, so any edit to it re-runs `leak`; training runs are cached by their
configuration, so if you change code that existing runs use, delete `.cache/` first. `--workers N`
sets the number of parallel training processes (default: cores − 2, at most 12).

## What to expect

The first line is the provenance of your run. Then (excerpt from the author's run):

```text
  schedule scaled_linear            sqrt(abar_T)=0.068265 SNR_T=4.681917e-03 leading first step sqrt(abar)=0.075997
  leak r=128 n=16384 data_std=0.2997 sd_leading_noise=0.3218(pred 0.3243) sd_trailing_noise=0.3536(pred 0.3565) sd_trailing_oracle=0.9929(pred 1.0000) zero_snr_trailing_noise=0.8513(pred 1.0000)
  leak steps=200 n=16384 sd_trailing_noise=0.3568 zero_snr_trailing_noise=0.9637
  train: 50 runs, 0 from cache, 50 to run
  train  4/50 weighting x0  const   w=128 seed=0 swd=0.11179952841628665 (495.7s)
  train  7/50 weighting x0  snr     w=128 seed=0 swd=8.177296925958067e+22 (500.3s)
  train 12/50 weighting x0  minsnr5 w=128 seed=0 swd=0.10493937044821108 (515.6s)
  train 36/50 target    eps minsnr5 w= 32 seed=0 swd=63.42282951397772 (123.7s)
  train 39/50 target    x0  minsnr5 w= 32 seed=0 swd=0.10569373027676847 (116.3s)
wrote captures.json
```

Training lines appear in the order runs finish, so your numbering will differ. Each line's `swd` is
the raw weights' sample distance at the run's last checkpoint; `captures.json` holds every
checkpoint and every weight average.

**Exact:** every schedule number. They are closed-form arithmetic in float64 and match Lin et al.'s
Table 1 to the digits it prints. **Close:** the leak ratios. numpy's seeded generator gives the same
draws everywhere, but matrix products can sum in a different order on another CPU, so expect
agreement to about three decimals. **Statistical:** the training runs. CPU PyTorch is deterministic
for one thread on one machine, but another CPU or library build can change the last bits, and the
50-step sampling trajectory amplifies them; compare medians and blow-up counts, not single seeds.

A sample-quality number above 10 means the sampler left the data's scale entirely ("blew up"); the
article counts those separately instead of averaging them in.

## Exercises

Do them in order. Each has a self-check you can mark yourself against. E1 to E4 hide the answer
from the author's run below it; E5 is an open extension, so its self-check is an acceptance test
rather than one answer. This is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: the leak at 16,384 pixels

Run `python training_decisions.py leak` and find the `r=128` line.

**Self-check:** `sd_trailing_noise` within 0.003 of 0.3536, its closed-form prediction printed as
0.3565, and your provenance line printed first.

<details><summary>Answer</summary>

`sd_trailing_noise=0.3536(pred 0.3565)`: samples from Stable Diffusion's schedule keep 35.4% of
the data's brightness spread. `sd_trailing_oracle=0.9929` shows the mismatch is the whole cause, and
`zero_snr_trailing_noise=0.8513` is the rescaled schedule with the sampler's own 50-step error. A
schedule number that disagrees means you edited the schedule functions; a leak ratio that differs in
the third decimal is a different CPU's summation order.

</details>

### E2 — Inspect: where the rescale moves the series' noise level

The article says the zero-terminal-SNR rescale moves the series' running noise level, $\bar\alpha = 0.64$,
to about 0.617. Find the entry in `captures.json` that records it, and the index it uses.

**Self-check:** an index, an $\bar\alpha$ before within 0.001 of 0.64, and an $\bar\alpha$ after within 0.001 of 0.617.

<details><summary>Answer</summary>

`schedules → rescale_at_abar_064`: index 270 of 0–999, $\bar\alpha$ 0.64074 before and 0.61759 after.
Index 270 is the step whose $\bar\alpha$ is closest to 0.64 under Stable Diffusion's schedule; the
article's 0.617 is the same rescale applied to exactly 0.64.

</details>

### E3 — Predict: a wider brightness spread

Change `S_B` at the top of `training_decisions.py` from 0.3 to 0.5. Before running anything, use the
article's closed form to predict the fraction of brightness spread that samples from Stable
Diffusion's schedule keep at 16,384 pixels. Then run `python training_decisions.py leak` and compare.

**Self-check:** your prediction within 0.01 of the run, with the reason coming from
$1/\sqrt{1-\bar\alpha_T+\bar\alpha_T\,(n s_b^2+\tau^2)}$.

<details><summary>Answer</summary>

With $s_b = 0.5$: $V_0 = 16{,}384 \times 0.25 + 0.01 = 4{,}096.01$, so
$V_T = 0.0046601 \times 4{,}096.01 + 0.99534 = 20.083$ and $\rho = 1/\sqrt{20.083} = 0.2231$. The
author's run printed `sd_trailing_noise=0.2218(pred 0.2231)` at `r=128`. A wider brightness spread
leaks more, because the mean's signal grows with $n s_b^2$, so samples keep a smaller share of it:
22% instead of 35%. `zero_snr_trailing_noise` falls too, to 0.7748, but that is the sampler's own
error, not a leak: in the step sweep it climbs from 0.589 at 25 steps to 0.942 at 200, while
`sd_trailing_noise` stays at 0.223. Put `S_B` back to 0.3 when you are done.

</details>

### E4 — Diagnose: NaN on the first step

Make the exact-denoiser sampler go through ε, the way many sampler implementations convert a
network's output. In `ddim`, replace

```python
        x0 = denoise(x, t)
```

with

```python
        eps_hat = (x - a * denoise(x, t)) / s        # what an epsilon-network would output
        x0 = (x - s * eps_hat) / a                   # converting it back, the epsilon way
```

and run `python training_decisions.py leak --quick`. Some lines print `nan`. Find which variants,
why, and fix it without undoing the change for the other variants.

**Self-check:** the symptom (which variants), the cause, the one observation that proves it, and a
fix that leaves the other variants' numbers unchanged.

<details><summary>Answer</summary>

**Symptom:** only `zero_snr_trailing_noise` prints `nan`, at every size and every step count; the
three Stable Diffusion variants print the same numbers as an unpatched run. numpy also warns
`invalid value encountered in divide` on the line `x0 = (x - s * eps_hat) / a`.

**Cause:** that variant samples the rescaled schedule from its last step, where $\sqrt{\bar\alpha}$ is
exactly zero (`schedules` prints `sqrt(abar_T)=0.000000` for `scaled_linear_zero_snr`). There
`a = 0` and `s = 1`, so `eps_hat` equals `x` and the conversion computes 0/0. Every later step
inherits the NaN.

**Proof:** the warning names the division by `a`, and the one variant that fails is the one whose
first step has `a = 0`. The Stable Diffusion variants start at $\sqrt{\bar\alpha}$ = 0.068 or 0.076
and are untouched.

**Fix:** keep the ε route wherever `a > 0`, and take $x_0$ from the denoiser where it is zero:

```python
        x0 = (x - s * eps_hat) / a if a > 0 else denoise(x, t)   # at zero SNR, take x0 directly
```

In the author's check, every line of `leak --quick` then matched an unpatched run to the printed
digits, and the warning was gone. This is the article's rule from Lin et al.: sample through
$x_0$, and never divide by $\sqrt{\bar\alpha_T}$.

</details>

### E5 — Extend: resample instead of reweight

Hang and colleagues found that drawing noise levels more often near log-SNR 0 beat raising their
loss weight. Add a sixth training configuration that keeps Min-SNR-5's expected objective but draws
log-SNR from a Laplace distribution centred at 0 (try a scale of 1) instead of drawing $t$
uniformly, dividing each sample's weight by its sampling density so the objective is unchanged. Run
three seeds at width 128 for 40,000 steps.

**Self-check:** your configuration passes all of these:

- the importance weights average to 1, within 0.02, over 100,000 draws;
- on the untrained network, your importance-weighted loss over 100,000 draws matches the
  uniform-timestep Min-SNR-5 loss to within 5%, so the objective really is unchanged;
- you report per-level excess error against Min-SNR-5's curve and the median sample distance of
  both, and say in one sentence whether resampling helped in this toy.

Over a full run, the rare draws far from λ = 0 carry importance weights in the thousands. If that
makes training unstable, widen the scale and report both runs.

## Safety and cleanup

- The lab touches nothing outside this folder: no network access after installation, no service, no
  GPU, no shared lab server.
- It writes `captures.json` and `.cache/` here, and nothing else.

```bash
rm -rf .cache            # the per-run cache
deactivate; rm -rf .venv # the environment, if you made one here
```
