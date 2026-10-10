# Lab — Diffusion Samplers and Solvers: 1,000 Steps Into 20

- **Grade:** G1 · runs anywhere (numpy only, on a CPU)
- **Executed:** yes · 2026-10-09 · AMD Ryzen 7 5825U laptop, Ubuntu 26.04.1, no GPU
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs; the run used 8 worker processes, one BLAS thread each), 14 GB RAM; Python 3.12.15, numpy 2.5.3

This lab measures samplers, not networks. Its denoiser is never trained: it is the exact posterior
mean $E[x_0 \mid x]$ of part 5's "crescent world" (square images of one of four bright crescents,
a brightness offset shared by every pixel with standard deviation 0.3, and per-pixel detail of
0.1), which has a closed form because the data is a Gaussian mixture. The probability-flow ODE that
a sampler solves is therefore known exactly, and every error below belongs to the sampler alone.
`samplers.py` is the one entry point. It computes the article's worked example in closed form,
measures the global error of DDIM, Heun, DPM-Solver-2, DPM-Solver-3 and DPM-Solver++(2M) against an
RK4 reference solution on five step schedules, measures the error one step makes at each noise
level, and compares deterministic with stochastic samplers. Every measured and computed number and
figure in the article comes from the `captures.json` this script wrote on the machine above;
numbers the article quotes from papers come from the papers.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `samplers.py` | G1 | yes | the entry point: `worked`, `ode`, `local`, `sde`, `samples` or `all` |
| `requirements.txt` | — | — | the one pinned package |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |

## What you need

| | |
|---|---|
| Hardware | any laptop; the full run peaked at about 1.7 GB in total across the main process and its 8 workers (625 MB for the main process alone) in total across its 8 worker processes |
| Software | Python 3 with numpy 2.5.3. The author's run used Python 3.12.15, the only version tried |
| Privileges | none: no root, no Docker, no GPU, nothing outside this folder and its virtual environment |
| Disk, network, time | about 80 MB for the environment, no dataset download; the full `all` run took 15 min on the machine above, `all --quick` 64 s |

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install numpy==2.5.3
python samplers.py worked            # ~4.5 min: the worked example in closed form, then a 16,384-pixel check
python samplers.py ode               # ~6 min: error against the exact path, five solvers x five schedules
python samplers.py local             # ~45 s: the error of one step at each noise level
python samplers.py sde               # ~4 min: deterministic against stochastic samplers
python samplers.py samples           # ~1 s: images and paths for the figures
python samplers.py all --quick       # everything, smaller and noisier, ~1 min
```

Each command adds its section to `captures.json`, and `all` rewrites the file. Pass `--out mine.json`
to keep the shipped capture for comparison. `--workers N` sets the number of parallel processes
(default: cores − 2, at most 8). The `ode` stage first computes its reference solution, the exact
ODE endpoint for 256 shared starting noises, and caches it in `.cache/` under a hash of the script:
any edit to `samplers.py` recomputes it.

## What to expect

The first line is the provenance of your run. Then (excerpt from the author's run):

```text
  worked: sqrt(V0)=38.40; first DDIM step keeps 0.9422; 50 trailing DDIM steps keep 0.8554
  worked ddim/trailing      1% at NFE  778 | 10:0.4117 13:0.5122 ... 50:0.8554 ... 1000:0.9923
  worked dpmpp2m/logsnr     1% at NFE   30 | 10:1.0411 13:1.0384 ... 50:1.0035 ... 1000:1.0000
  worked measured: zero_snr  ddim      steps= 50 kept=0.8540 +- 0.0135 (N=2000)
  ode: reference RK4 self-check rms 4.72e-12
  ode ddim     edm7     below one grey level from NFE 100; 1:6.4e-01 5:1.8e-01 12:8.0e-02 30:2.2e-02 80:8.1e-03 200:3.3e-03 512:1.3e-03
  ode dpm3     edm7     below one grey level from NFE 16; 1:6.4e-01 13:9.0e-03 31:5.9e-04 79:3.2e-05 199:2.9e-06 511:2.1e-07
  ode dpmpp2m  vp_time  below one grey level from NFE 320; 1:6.4e-01 5:2.5e-01 12:1.1e-02 30:3.8e-02 80:3.2e-02 200:1.1e-02 512:2.7e-03
  sde ancestral detail 3:0.002 6:0.253 12:0.352 25:0.573 50:0.748 128:0.889 400:0.961
  samples: decision entropy 100:1.97 60:1.91 40:1.81 30:1.68 20:1.35 10:0.43 5:0.01 2:0.00 1:0.00
wrote captures.json in 901 s
```

**Exact:** every `worked` line except `worked measured`. They are float64 arithmetic on closed forms
and match on any machine. **Close:** the `ode`, `local` and `samples` numbers. numpy's seeded
generator gives the same draws everywhere, but matrix products can sum in a different order on
another CPU; errors agree to about two significant figures, and a "below one grey level from NFE"
threshold can move by one grid point where a curve crosses the line close to a grid point.
**Statistical:** `worked measured` and `sde`, which estimate spreads and sample statistics from
finite samples. The ± after `kept` is one standard error; expect your value within two of it.

The reference check line matters: if `reference RK4 self-check rms` is not far below the grey
level 0.0078, every `ode` number is measured against a reference no better than the samplers.

## Exercises

Do them in order. Each has a self-check you can mark yourself against. E1 to E4 hide the answer
from the author's run below it; E5 is an open extension, so its self-check is an acceptance test.
This is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: part 5's 0.851, from first principles

Run `python samplers.py worked`. Part 5 measured that 50 DDIM steps on its fixed schedule keep 0.851
of the data's brightness spread. Find the closed form's value and the 16,384-pixel measurement.

**Self-check:** the closed-form line prints 0.8554 exactly; the `zero_snr ddim steps= 50` measurement
lies within two standard errors of it; your provenance line printed first.

<details><summary>Answer</summary>

`50 trailing DDIM steps keep 0.8554` is the brightness direction as one Gaussian number, stepped
exactly. `worked measured: zero_snr ddim steps= 50 kept=0.8540 +- 0.0135 (N=2000)` is the same
sampler run on 2,000 full 128×128 crescent images, 0.1 standard errors away. Part 5's 0.851 is the
same quantity from a different draw. The shortfall is DDIM's own error, not the schedule's: the
same line for DPM-Solver++(2M) prints 0.9011 ± 0.0142. A closed-form number that differs means the
schedule or the world constants were edited.

</details>

### E2 — Inspect: which steps lose the spread

In `captures.json`, `worked → first_steps` lists DDIM's factor and the exact path's factor for steps
2 to 7 of part 5's 50-step grid, and `worked → first_step_kept` the first step. Compute what fraction
each step loses relative to the exact path, and find the range of σ where the loss per step exceeds 1%.

**Self-check:** seven per-step losses, the largest first, and a σ range you can state relative to
$\sqrt{V_0}$ = 38.40.

<details><summary>Answer</summary>

Divide each step's DDIM factor by the exact factor. The first step, ∞ → 107.96, keeps 0.9422 of
the exact path, a loss of 5.78%. Then:

| Step | σ → σ′ | DDIM ÷ exact | Loss |
|---:|---|---:|---:|
| 2 | 107.96 → 51.62 | 0.9560 | 4.40% |
| 3 | 51.62 → 32.93 | 0.9754 | 2.46% |
| 4 | 32.93 → 23.65 | 0.9877 | 1.23% |
| 5 | 23.65 → 18.13 | 0.9939 | 0.61% |
| 6 | 18.13 → 14.49 | 0.9968 | 0.32% |
| 7 | 14.49 → 11.92 | 0.9982 | 0.18% |

The four steps that lose more than 1% all end between σ = 108 and 23.6, within a factor of three of
$\sqrt{V_0}$ = 38.4 (12.8 to 115), where the exact path bends from slope 1 to flat. After step 7 the
sampler keeps 0.8581, and the remaining 43 steps lose only 0.3% more, to 0.8554. Part 5's grid has no
step above 108 other than the first, so the largest single loss is the jump from pure noise.

</details>

### E3 — Predict: DDIM steps for 2% error

DDIM on part 5's grid misses the brightness spread by 14.5% at 50 steps and 7.5% at 100. Predict
how many steps bring the error to 2%, then check with this, run from this folder:

```python
import samplers as S
sl, zs = S.sd_schedules()
v0 = 128 * 128 * S.S_B ** 2 + S.TAU ** 2                   # the brightness direction's variance
for steps in (300, 375, 400):
    sig = [S.sigma_of(zs[t]) for t in S.trailing(steps)] + [0.0]
    print(steps, 1 - S.gaussian_1d("ddim", sig, v0, 1.0)[0])
```

**Self-check:** within 15% of the step count that gives 2.0%, for the reason that a first-order
method's error falls in proportion to its step size.

<details><summary>Answer</summary>

Error times steps is roughly constant for a first-order method: $0.145 \times 50 = 7.2$ and
$0.075 \times 100 = 7.5$, so 2% needs about $7.5 / 0.02 = 375$ steps. The snippet prints 2.60% at
300, 2.11% at 375 and 1.99% at 400. The product creeps up, from 7.2 to 8.0, because part 5's grid
does not shrink every step by the same factor as steps are added; first order is the asymptote,
not an exact law.

</details>

### E4 — Diagnose: Heun's samples are twelve times too wide

The `worked` line `heun/trailing4096` runs EDM's Heun method on part 5's trailing spacing at 10 to
1,000 steps, with the infinite first noise level replaced by σ = 4096, the patch diffusers applies
to a zero-SNR schedule. At 49 calls, 25 steps, it keeps 12.2 times the data's brightness spread;
DDIM on the same 25 steps keeps 0.72. Find the step responsible, explain it, and fix it without
leaving part 5's spacing.

**Self-check:** the step and its two factors (Heun's and the exact path's), the reason, and a fix
whose `kept` at 48 or 49 calls lies between 0.8 and 1.1.

<details><summary>Answer</summary>

**Symptom:** the error falls with more calls (39.6 at 19, 12.2 at 49, 1.26 at 199) but from far
above 1, the opposite side from DDIM, so samples come out too wide, not too narrow.

**Cause:** the first step, from σ = 4096 to 51.62. On this direction the ODE's slope is
$(x - D)/\sigma$, and along the exact path the step must cancel 98.4% of the state: the exact
factor is 0.0157. Euler's predictor applies the slope at σ = 4096, where the denoiser returns
almost nothing, and cancels 98.7%, a factor of 0.0127. Heun averages that slope with the one at
the predicted end point, where σ is near $\sqrt{V_0}$ = 38.4 and the denoiser already returns part
of the signal, so the end slope is only 0.64 of the start slope. The true slope stays near its
start value for almost the whole step and drops only near its end, so the trapezoid's half weight
on the end slope is far too much: the average is 18% short, the step
cancels 81% instead of 98.4%, and the state keeps 0.1863: 11.9 times the exact factor. An 18% error
in the slope becomes a twelvefold error in the result because the result is the small difference
left after a near-total cancellation. Every later step is short and accurate.

**Proof:** in `gaussian_1d`'s `heun` branch, print `fe` (0.0127) and the corrected factor (0.1863)
for the first step, against `math.sqrt((v0 + s2**2) / (v0 + s**2))` (0.0157). Only the first step's
corrected factor is far from the exact one.

**Fix:** take the first step with Euler, which is DDIM, and Heun after it. In `gaussian_1d`, change

```python
            if s2 == 0:
                a *= fe
```

in the `heun` branch to

```python
            if s2 == 0 or s == sig[i0]:       # Euler on the last step, and on the first
                a *= fe
```

`heun/trailing4096` then prints 0.8309 at 48 calls, 0.9842 at 98 and 1.0098 at 198. The other fix
is the article's: keep Heun but put its steps on log-SNR, where the first step is short;
`heun/logsnr` already prints 1.0347 at 49. Put the line back afterwards, since the article's
Figure 2 reads the unpatched curve.

</details>

### E5 — Extend: a step-ratio guard for DPM-Solver++(2M)

On the variance-preserving time grid (`vp_time`), DPM-Solver++(2M) needs 320 calls to stay within
one grey level, more than DDIM's 200, and its error does not fall steadily with more calls. Its
multistep correction weights the last two denoiser answers by $1 + 1/(2r)$ and $-1/(2r)$, where
$r = h_{i-1}/h_i$ is the ratio of the previous step to the current one in log σ. On `vp_time` the
steps lengthen sharply toward low noise, so $r$ gets small and those weights large. Add a guard
to `dpmpp2m` that takes a first-order step whenever $r < 0.5$, and measure it.

**Self-check:** your guarded solver passes all of these:

- on `edm7`, every error from 4 calls up matches the unguarded solver's to the printed digits, so
  the guard leaves a well-graded grid alone (at 3 calls the two log-SNR steps differ enough to trip it);
- on `vp_time`, its error falls at every step count from 8 to 512 calls;
- you report its NFE to one grey level on `vp_time` beside the unguarded solver's 320 there and 25
  on `edm7`, and say in one sentence what the guard can repair and what only a better grid can.

The guard is a heuristic of this exercise, not a published method; diffusers instead falls back to
first order on its final steps below 15 steps. A ratio threshold other than 0.5 is worth trying.

<details><summary>Answer</summary>

On `vp_time` the guard fires on exactly one step at every step count: the last before σ_min, which
is 5.4 to 6.7 times longer in log σ than the step before it (r between 0.15 and 0.19). The author's
guarded solver, measured against the lab's cached reference:

```text
vp_time guarded    8:9.79e-02 12:6.56e-02 20:4.84e-02 30:3.43e-02 50:1.91e-02 80:9.62e-03 128:4.33e-03 200:1.96e-03 320:9.00e-04 512:4.52e-04
vp_time unguarded  8:7.13e-02 12:1.13e-02 20:2.12e-02 30:3.79e-02 50:4.12e-02 80:3.18e-02 128:1.99e-02 200:1.12e-02 320:5.61e-03 512:2.72e-03
edm7    guarded    8:8.16e-02 12:2.22e-02 20:8.98e-03 30:3.89e-03 50:1.30e-03 80:4.82e-04 128:1.83e-04 200:7.36e-05 320:2.84e-05 512:1.10e-05
```

The guarded error falls at every step count and stays within one grey level from 100 calls, against
320 unguarded and DDIM's 200 on the same grid. The guard removes the extrapolation's blow-up, but the
last step is still a first-order step five to seven times longer than the one before it, so the solver
needs four times the 25 calls it needs on ρ = 7: only a better grid recovers that. Up to 20 calls the
unguarded solver's error is lower, but it then grows with the budget, from 0.011 at 12 calls to 0.041
at 50; an error that rises with more calls cannot be trusted at any budget, which is why the self-check
asks for a steady fall rather than a smaller number everywhere.

</details>

## Safety and cleanup

- The lab touches nothing outside this folder: no network access after installation, no service, no
  GPU, no shared lab server.
- It writes `captures.json` (or the file named by `--out`) and `.cache/` here, and nothing else.

```bash
rm -rf .cache            # the cached reference solution
deactivate; rm -rf .venv # the environment, if you made one here
```
