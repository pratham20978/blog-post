# Lab — Why Your GPU Is Idle at 100% Utilization

This lab comes in two hardware tiers, and each script says which one it needs.

- **Tier A — no GPU.** `queue_model.py` is a model of one CUDA stream in plain Python. It prints
  every number in the article's worked example, its fixes and its exercises, and it runs on any
  machine with Python 3.9 or newer. The transcript in `expected-output.txt` was captured on a
  laptop with no NVIDIA GPU.
- **Tier B — one NVIDIA GPU.** `step_timing.py` runs the same training step for real and times it
  on both clocks. `util_probe.py` reads `nvidia-smi`'s utilization number while the GPU does four
  very different things. **Neither has been run for this article**: the machine it was written on
  has no NVIDIA GPU, so no Tier B result ships with the lab. `results-schema.json` defines exactly
  what a run writes, and it is empty on purpose — no number here is invented.

## Prerequisites

| | Tier A | Tier B |
|---|---|---|
| Hardware | any | one NVIDIA GPU; about 1 GB of free GPU memory |
| Driver | none | the NVIDIA driver, which also provides `libnvidia-ml.so.1` |
| Python | 3.9+, standard library only | 3.9+ with a CUDA build of PyTorch (written against 2.14.0) |
| Time | under a second | about two minutes for both scripts |

Run Tier B on a GPU nothing else is using. `util_probe.py` deliberately holds the GPU busy, and
any other process's kernels would count toward the same utilization number it is reading.

## Run order

```bash
python3 queue_model.py --trace                                  # tier A: the article's numbers
python3 step_timing.py --instance "<where this ran>" --out results.json   # tier B
python3 util_probe.py --out results.json                        # tier B
```

Both Tier B scripts merge into the same `results.json`. `--instance` is free text for the
provenance line — the rented instance type, or "desktop".

## What each script does, and what to expect

### `queue_model.py` (tier A)

Three rules — a launch costs the host time, the GPU starts a kernel when it has arrived and the one
before it has finished, and a sync point moves the host's clock forward to the GPU's — applied to
the article's step. It prints each phase on the host timer and on CUDA events, the GPU time the
kernels actually ran, the step time, and utilization by NVIDIA's definition, for four versions of
the step. The numbers match the article exactly because the article's figures import this file.

The inputs are round numbers chosen to be followed by hand. They are **not** measurements. The
model also assumes one stream, no launch latency and an unbounded launch queue; the real queue is
finite and its depth is not documented.

### `step_timing.py` (tier B)

An MLP with 100 parameter tensors, trained with AdamW, run four ways: as written (with
`loss.item()` between backward and the optimizer and a for-loop optimizer), with the logging sync
removed, with the foreach optimizer, and captured as one CUDA graph. For each phase it prints the
host timer, the CUDA-event time, and the phase's kernels alone — measured by queuing them behind a
one-thread spin kernel (`torch.cuda._sleep`) so the GPU never waits for the host. It also prints
what `torch.cuda.set_sync_debug_mode("warn")` reports for one as-written step, and the step time a
loop reports when it is timed without a final `torch.cuda.synchronize()`.

What the article predicts you will see, whatever your GPU:

- **as-written, `log` phase:** a large host-timer value and a CUDA-event value near zero. That is a
  sync point billed for work that ran earlier.
- **as-written and fix-1, `optimizer` phase:** host timer and events close together and both well
  above the kernels-alone time, if your GPU runs those small kernels faster than Python issues them.
  A very slow GPU may not show it; say so if it does not.
- **fix-2 and graph:** a loop timed without a final sync reports a shorter step than the same loop
  synchronized, whenever the step is GPU-bound.
- **graph:** the host time per step collapses to the copy-in and one replay call; the events stay
  close to the kernels-alone time.

Utilization by definition can read slightly above 100% for a GPU-bound variant: the kernels-alone
pass is a separate measurement from the events, and the two carry independent noise.

### `util_probe.py` (tier B)

Reads NVML's `nvmlDeviceGetUtilizationRates` every 100 ms — the call `nvidia-smi` and most monitoring
agents are built on — across four phases: idle, a one-thread spin kernel, back-to-back large
matmuls, and a Python loop of one-element additions. For the last phase it also estimates the share
of time a kernel was actually executing, from the launch rate and the per-kernel GPU time.

This is the script that settles the one contested point in the article. NVIDIA documents the number
as the share of the sample window in which some kernel was executing: by that definition
`spin_one_thread` reads about 100%, and `tiny_launches` reads about its estimated kernel-busy share.
One published measurement saw the counter read 100% on a GPU executing kernels a few percent of the
time. Record which description fits your GPU.

To see the spatial number next to it, run DCGM's monitor in a second terminal while the probe runs:

```bash
dcgmi dmon -e 203,1002     # device utilization, and SM Activity (DCGM_FI_PROF_SM_UTIL_RATIO)
```

## The provenance line

A Tier B number is publishable only with the line `step_timing.py` prints first, in this form:

```text
Captured <UTC time> on <GPU> (sm_NN, N SMs), KMD <kernel driver>, CUDA UMD <driver ceiling>,
torch <version> (runtime <torch.version.cuda>), <CPU model>, Python <version>, <instance>.
```

The KMD and CUDA UMD versions are read from NVML, not parsed from `nvidia-smi` output — the same
four-number vocabulary as part 2 of this series. If you publish or send results, send
`results.json` whole: it carries the provenance next to every number.

## What was and was not executed

- `queue_model.py` was run; its output is `expected-output.txt`.
- `step_timing.py` and `util_probe.py` were syntax-checked. Every code path in `step_timing.py`
  that does not need CUDA — the model, the four phases, the for-loop and foreach optimizers, the
  bookkeeping and the results file — was exercised against a CPU build of PyTorch 2.14.0 with the
  CUDA timing calls stubbed. The graph capture, the events, the spin kernel and everything in
  `util_probe.py` need a GPU and have not been run.

## Cleanup

Nothing is installed and no environment variable is changed. The Tier B scripts write
`results.json` only when given `--out`, and free their GPU memory when they exit.
