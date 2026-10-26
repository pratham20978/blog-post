# Lab — Controlling Diffusion Models: Guidance, ControlNet, LoRA

- **Grade:** G1 · runs anywhere (CPU PyTorch and numpy)
- **Executed:** yes · 2026-10-18 · AMD Ryzen 7 5825U laptop, Ubuntu 26.04.1, no GPU
- **Provenance:** Linux 7.0.0-38-generic x86_64, AMD Ryzen 7 5825U (16 logical CPUs; the run used 8 worker processes, one thread each), 14 GB RAM; Python 3.12.15, numpy 2.5.3, torch 2.14.0+cpu; the `census` stage also diffusers 0.40.0

This lab measures every way of controlling a diffusion model in the article against a model whose
answers are exact. The world is part 5's crescent world at 8×8 pixels with a contrast dial: each image
shows one of four crescents (the class), faint (contrast 0.5) or strong (1.0) half and half, with a
brightness offset of standard deviation 0.3 and per-pixel detail of 0.1. Its unconditional and
class-conditional denoisers $E[x_0 \mid x]$ and $E[x_0 \mid x, c]$ have closed forms. `control.py`
is the one entry point. It computes the article's worked example in closed form, runs classifier-free
guidance on the exact model, trains a class-conditional network with label dropout (and a weaker copy)
and runs guidance, autoguidance, guidance intervals, CFG-rescale and APG on them, trains a ControlNet
branch, five personalisation recipes and an inpainting network on top of the trained network, runs
replacement and RePaint-style inpainting and SDEdit and DDIM-inversion editing on the exact model,
and writes every number to `captures.json`. Every measured number and figure in the article comes
from the `captures.json` this script wrote on the machine above; numbers the article quotes from
papers come from the papers.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `control.py` | G1 | yes | the entry point: `worked`, `exact`, `networks`, `controlnet`, `personal`, `inpaint`, `edit`, `samples`, `census`, `all` |
| `requirements.txt` | — | — | the two pinned packages, and the optional third for `census` |
| `captures.json` | — | — | the author's run, machine-readable; every measured figure in the article reads it |
| `expected-output.txt` | — | — | the same run as printed, to compare with yours |
| `notebook.ipynb` | G1 | yes | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | any laptop with about 3 GB of free RAM: `all` ran 9 processes, each under 330 MB at its peak |
| Software | Python 3 with numpy 2.5.3 and the CPU build of torch 2.14.0; diffusers 0.40.0 only for `census`. The author's run used Python 3.12.15 |
| Privileges | none: no root, no Docker, no GPU, nothing outside this folder and its virtual environment |
| Disk, network, time | about 200 MB to download for torch and 800 MB installed, no dataset; `census` builds SD 1.5's U-Net and a ControlNet on PyTorch's meta device, so it downloads no weights. On the machine above `all` took 11 min with 8 workers and `all --quick` 4.4 min; `worked` takes about 35 s and `edit` about 10 s |

## Run

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install numpy==2.5.3
pip install --index-url https://download.pytorch.org/whl/cpu torch==2.14.0+cpu
python control.py worked              # ~35 s: the worked example in closed form
python control.py all --quick         # everything with shorter training, ~4.4 min
python control.py all                 # the article's run, ~11 min with 8 workers
pip install diffusers==0.40.0 && python control.py census   # optional: SD 1.5's parameter counts
```

`all` rewrites `captures.json`; any other stage adds its section to it. Pass `--out mine.json` to keep
the shipped capture for comparison. `--workers N` sets the number of parallel processes (default:
cores − 2, at most 8), `--seeds N` the seeds per trained network (default 2). The stages after
`networks` fine-tune the trained network and train it first if it is not cached. Every trained network
is cached in `.cache/` under a hash of the script, so an interrupted run resumes, and any edit to
`control.py` retrains from scratch.

## What to expect

The first line is the provenance of your run. Then (excerpt from the author's run; its last lines name
`captures.final.json` because that run wrote to a new file, renamed to `captures.json` once it finished,
and yours names the file you passed to `--out`):

```text
  worked: x=40, sigma=80: D_uncond 0.203, D_cond 5.419, guided (w=3) 15.849; one DDIM step to 17.53: 8.92 / 13.00 / 21.14
  worked: faint share of class +1 by weight: w=1.0 0.527 (eps* +0.0675)  w=1.5 0.381 (eps* -0.3038)  w=2.0 0.231 (eps* -0.7363)  w=3.0 0.032 (eps* -1.8568)  w=5.0 0.000 (eps* -5.4962)  w=7.5 0.000 (eps* -11.4438)
  exact cfg w= 3.0: faint 0.095, over 0.0037, strong contrast 1.035, brightness sd 0.293, precision 0.807, recall 0.564, distance 0.2252
  …
  model network seed 1 cfg   w=1: 0.52/0.072/0.000  w=1.5: 0.36/0.079/0.000  w=2: 0.26/0.060/0.001  w=3: 0.13/0.042/0.004  w=4: 0.06/0.016/0.018  w=5: 0.03/0.008/0.077   (faint / blends / over)
  model network seed 1 other auto w=1.5: 0.51/0.052/0.020  auto w=2: 0.50/0.040/0.019  …   (faint / blends / distance)
  controlnet zero     seed 1: 0:0.472/0.050 25:0.470/0.047 50:0.472/0.050 100:0.449/0.056 200:0.196/0.044 400:0.096/0.025 …
  personal full     seed 1: 181056 trained; after 2000 steps subject 1.000 (distance 0.193), drift 1.000, crescent-0 distance 0.366, other classes 0.191
  inpaint replacement     : coherent 0.646, median rms from the posterior mean 0.205  (64 denoiser calls)
  edit inversion: success 1.000, ghost +0.001, contrast kept 0.606, brightness error 0.0021, detail corr 1.000; reconstruction rms 0.00324, …
  census SD 1.5: U-Net 859,520,964; ControlNet 361,279,120 (42.0%); LoRA r=4 on 128 attention projections 797,184; …
```

**Exact:** every `worked`, `exact`, `inpaint` (except the inpainting network) and `edit` line uses only
the closed-form denoisers and fixed seeds; on the machine above they repeat to the digits printed, and
on another machine they can differ by one count in 4,096 where matrix products sum in a different
order. `census` counts parameters and is exact everywhere. **Close:** every trained network and what
is built on it. Training is seeded, but another CPU sums in another order and a trained network
amplifies that: expect shares within about two percentage points of the author's, sample distances
within about 0.005, and the same orderings. The `seed 1` and `seed 2` lines show the spread between
two seeds on one machine, a fair guide to the spread between machines.

The `precision` and `recall` that the `exact` lines print are the k-nearest-neighbour metric of
Kynkäänniemi et al. (2019), kept for reference. The article does not quote them: at `w=7.5` recall
rises again because over-saturated outliers widen their own neighbourhoods, so the faint share is the
cleaner measure of coverage in this world.

## Exercises

Do them in order. Each has a self-check you can mark yourself against, with the answer from the
author's run hidden below it. This is an L4 post, so the lab ships E1 to E5.

### E1 — Reproduce: the guided denoiser and the faint share

Run `python control.py worked --out mine.json`. The article computes, in a one-number world, the
unconditional, conditional and guided denoisers at $x = 40$, $\sigma = 80$, one guided DDIM step, and
the share of samples guidance leaves faint. Find them in the output.

**Self-check:** the first line prints `D_uncond 0.203, D_cond 5.419, guided (w=3) 15.849` and a step
to `21.14`; the second prints faint shares 0.527, 0.381, 0.231 and 0.032 for $w$ = 1, 1.5, 2 and 3;
your provenance line printed first.

<details><summary>Answer</summary>

```text
  worked: x=40, sigma=80: D_uncond 0.203, D_cond 5.419, guided (w=3) 15.849; one DDIM step to 17.53: 8.92 / 13.00 / 21.14
  worked: faint share of class +1 by weight: w=1.0 0.527 (eps* +0.0675)  w=1.5 0.381 (eps* -0.3038)  w=2.0 0.231 (eps* -0.7363)  w=3.0 0.032 (eps* -1.8568)  w=5.0 0.000 (eps* -5.4962)  w=7.5 0.000 (eps* -11.4438)
```

At σ = 80 the four looks (±3.6, ±7.2) are almost equally likely, so the unconditional denoiser is near
their mean, 0, and the conditional one near the requested class's mean, 5.4; the exact weights lean
slightly toward the looks nearer $x = 40$, which gives 0.203 and 5.419. Guidance at $w = 3$ asks for
$0.203 + 3(5.419 - 0.203) = 15.849$, more than twice the strongest real contrast. The `eps*` values
are the starting noises at which the paths split between faint and strong, and each faint share is
the normal distribution's mass below it: $\Phi(0.0675) = 0.527$ unguided, because the sampler's
starting noise is centred on zero rather than on the class's mean, and $\Phi(-1.8568) = 0.032$ at
$w = 3$. Every number here is closed form, so yours match to the digits printed.

</details>

### E2 — Inspect: where guidance decides

In the shipped `captures.json`, `exact → below` lists the faint share when guidance at $w = 3$ is
switched on only at noise levels at or below each listed σ, and `exact → above` when it is on only
above it. Find two noise levels: the largest σ for which guidance confined at or below it still leaves
at least half the samples faint, and the largest σ for which guidance confined above it still comes
within 0.02 of full guidance's faint share. Then read `above` upward from the second one to see where
the damage accumulates.

**Self-check:** two noise levels, the first below the second, and the full-guidance faint share the
second is compared with, from `exact → weights → 3.0`.

<details><summary>Answer</summary>

The two levels are 2.0 and 3.0. Full guidance at $w = 3$ leaves `exact → weights → 3.0 → faint` =
0.095. In `below`, the faint share is 0.53 for every σ up to 1.4, 0.50 at 2.0 and 0.42 at 3.0, so
guidance confined to σ ≤ 2 changes nothing: by then the decision is made. In `above`, it is 0.10 at
2.0 and 0.11 at 3.0, within 0.02 of 0.095, then 0.19 at 5, 0.33 at 10, 0.44 at 20 and 0.50 at 40, so
guidance confined above σ = 3 still does almost all of full guidance's damage, and that damage
accumulates between σ ≈ 3 and 20. The guidance-interval paper reached the same verdict on real models
by sweeping the interval's ends: harmful high, unnecessary low.

</details>

### E3 — Predict: SDEdit at σ₀ = 4

The article derives that SDEdit, editing crescent 0 into crescent 1 from a starting noise σ₀, keeps a
fraction $\tau/\sqrt{\tau^2 + \sigma_0^2}$ of everything crescent 1's denoiser cannot explain, with
τ = 0.1: the old crescent (the ghost) and the fine detail alike. Before running anything, predict the
ghost and the detail correlation at σ₀ = 4. Then run `python control.py edit --out mine.json` and read
the `sigma0=  4.0` line.

**Self-check:** your prediction within 0.01 of both printed values, for the reason that both are the
same off-class coordinate scaled by one factor.

<details><summary>Answer</summary>

The prediction is $0.1/\sqrt{0.01 + 16} = 0.0250$ for both. The run prints:

```text
  edit sdedit sigma0=  4.0: success 1.000, ghost +0.025, contrast kept 0.586, brightness error 0.230, detail corr 0.032
```

The ghost matches the prediction to the digits printed. The detail correlation sits about 0.007 above
it at every σ₀ (0.202 against 0.196 at 0.5, 0.106 against 0.0995 at 1) for a reason that is not
physics: every σ₀ reuses one draw of noise (the stage's seed is fixed), and that draw happens to point
slightly along the sources' detail, with a mean cosine of +0.008 across the 1,024 images, about two
standard errors. In those directions the output is exactly a scaled copy of the noisy start, so the
offset passes straight through. The brightness error, 0.230, shows the cost
the dial does not trade: brightness is part of what crescent 1's denoiser explains, so it is
re-drawn rather than kept, and its error grows with σ₀ toward the 0.32 of an unrelated image.

</details>

### E4 — Diagnose: every "crescent 0" is now the subject

Run `python control.py personal --quick --method full --steps 1000 --out mine.json`. It fine-tunes the
trained network for 1,000 steps on five photos of a new subject, a thinner crescent 0, captioned with a
rare token plus "crescent 0", then samples the subject's prompt and the plain "crescent 0" prompt from
the same 1,024 noises. Treat the result as a model someone else trained: say what went wrong, the one
observation that proves it, and a fix that uses only this stage's flags.

**Self-check:** the cause in one sentence, the observation in the printed lines that proves it, and a
rerun with the same seeds whose `drift` is below 0.05 for both seeds while the subject share stays
above 0.95.

<details><summary>Answer</summary>

**Symptom.** The two `personal full` lines print `subject 1.000` and `drift 1.000`: the subject is
learned, and every sample of the plain prompt "crescent 0" is now the subject too; the crescent-0
distance has grown from the base model's 0.036–0.039 to 0.365 and 0.562.

**Cause.** Fine-tuning every weight on images captioned with the class word teaches the class word what
the subject looks like: DreamBooth's language drift. Nothing in the training batch says what an
ordinary crescent 0 looks like.

**Observation.** The `personal base` lines, which sample the same prompts and noises before
fine-tuning, print `drift 0.000`. The sampler, the noises and the prompt are unchanged, so the change
lives in the weights' meaning of "crescent 0".

**Fix and check.** Add prior preservation: `python control.py personal --quick --method full+ppl --steps
1000 --out mine.json` trains on the five photos and, in the same batches, on 1,000 of the model's own
crescent-0 samples under the plain prompt. Its lines print `drift 0.005` and `drift 0.001`, with the
subject share still `1.000`. Two things it does not fix: the other three classes' distance still
grows (0.107 and 0.223, against the base model's 0.040–0.044), because no image of them was in the
batch, and the subject's brightness spread still follows the five photos'. Delete `mine.json` to put
the folder back.

</details>

### E5 — Extend: RePaint with jumps

The `inpaint` stage's resampling goes back one step at a time. RePaint's own schedule (its Appendix
B) jumps back $j$ steps of noise at once and walks them down again. Write
`replacement_jump(y, n=64, resample=r, jump=j)` beside `replacement` in `control.py`: every $j$ steps
on the way down, add back the noise of those $j$ steps in one draw and redo them, $r - 1$ times. Count
its denoiser calls and measure its coherence with `coherence(x, posterior_mean(y))` for $j$ = 1, 2 and
5 at the same number of calls as `resample 5`.

**Self-check:** three acceptance tests your build must pass: with `resample=1` it returns
`replacement(y, 64, 1)` exactly, from the same seed; a counter wrapped around `denoise` shows $64 + (r -
1) \cdot 64$ calls for every $j$; and with $j = 1$ its calls equal `resample r`'s. The coherence it
reaches at larger $j$ is your result: there is no single answer.

## Safety and cleanup

- The lab touches nothing outside this folder: no network access after installation (the optional
  `census` reads no remote file either), no service, no GPU, no shared lab server.
- It writes `captures.json` (or the file named by `--out`) and `.cache/` here, and nothing else.

```bash
rm -rf .cache            # trained networks, about 6 MB after both runs
deactivate; rm -rf .venv # the environment, if you made one here
```
