# Lab — Five Causes of One “CUDA Out of Memory”

- **Grade:** G3 · needs one NVIDIA GPU (this series' Tier B); `diagnose.py` alone is G1 and runs anywhere
- **Executed:** yes · 2026-10-30 · an NVIDIA GB10 (Dell Pro Max with GB10, FCM1253) reached over SSH
- **Provenance:** Ubuntu 24.04.4 LTS, kernel 6.17.0-1021-nvidia, aarch64; Cortex-X925 + Cortex-A725 (20 cores); 121.63 GiB of memory shared by CPU and GPU; NVIDIA GB10 (sm_121, 48 SMs), KMD 595.71.05, CUDA UMD 13.2; Python 3.12.3; torch 2.15.0+cu132 (runtime 13.2), cuda-bindings 13.4.4, numpy 2.3.4, installed with uv 0.12.5

`oom_lab.py` trains one stand-in model — 16 × `Linear(8192, 8192)` + GELU in fp32 with Adam, a 20.00 GiB
peak — on an emulated 24 GiB card and makes it fail five ways: fragmentation, capacity, a retained
autograd graph, another process, and memory outside PyTorch. Each failure prints PyTorch's real
out-of-memory message, and each fix, run in a fresh process, gets past the failure it targets. The lab also measures what one
process holds outside PyTorch, what a unified-memory GPU reports, and what a zombie holds. Every
number the article calls measured comes from `captures.json`, written by this script on the machine
above; `diagnose.py` turns any message into a cause.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `oom_lab.py` | G3 | yes | the entry point: every case, the mystery faults for E4, and the helper processes |
| `diagnose.py` | G1 | yes | the article's decision tree, standard library only |
| `captures.json` | — | — | the run the article quotes, written as `captures-new.json` and renamed: messages, ledgers, snapshot summaries, traces |
| `expected-output.txt` | — | — | that run's console output, to compare with yours |
| `requirements.txt` | — | — | the pinned versions |
| `notebook.ipynb` | G1, with G3 cells | yes, G1 cells | this README with a runnable cell under each step and exercise; built from it, never edited |

## What you need

| | |
|---|---|
| Hardware | for `diagnose.py`, anything with Python 3.10 or newer. For `oom_lab.py`, one NVIDIA GPU with about 31 GiB free at the default `--layers 16`; `--layers 8` halves every size (card, model, holders), `--layers 4` quarters them |
| Software | Python 3.10+, and on Linux `pip install -r requirements.txt` (PyPI's torch 2.15.0 wheel brings its own CUDA 13.2 libraries); an NVIDIA driver new enough for CUDA 13.2, which also provides `libnvidia-ml.so.1` |
| Privileges | none: no root, no Docker; the lab writes only the `--out` file and a temporary folder inside this one |
| Disk, network, time | about 3 GB of wheels on first install; a full run takes about 2.5 minutes on the GB10 |

## Run

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python oom_lab.py run --out mine.json        # every case, about 2.5 minutes
python diagnose.py mine.json                  # the five verdicts from your own run
```

`run --case <name>` runs one case: `baseline`, `fragmentation`, `capacity`, `capacity-fix`, `retained`,
`retained-fix`, `other-process`, `other-process-fix`, `non-pytorch`, `non-pytorch-fix`, `inventory`,
`inventory-eager`, `unified`, `zombie`, `precedence-a`, `precedence-b`. The default `--out` is
`mine.json`, so the shipped `captures.json` is never overwritten.

> [!WARNING]
> The lab drives the GPU to its out-of-memory limit on purpose and, for the other-process case, starts
> a process that holds 6 GiB (at `--layers 16`) until it is stopped or 240 seconds pass. Run it on a GPU
> nothing else needs. The emulated card caps only this lab's PyTorch; the lab never fills the real
> device.

**The emulated card.** The default card is 24 GiB. If your GPU has more memory, `oom_lab.py` caps its
own allocator with `torch.cuda.set_per_process_memory_fraction` before every phase of every step, to
24 GiB minus what NVML says other compute processes and this process's non-PyTorch memory hold. That
is why each message prints an "allowed" clause and your GPU's real total and free. If your GPU has 24
GiB or less, use `--layers 8` or `--layers 4`, and the driver itself refuses the allocations.

## What to expect

The run prints the provenance line, then one block per case. On the GB10:

```text
== fragmentation
   OOM at optimizer of step 0 (batch 12288)
   ... 23.67 GiB allowed; Of the allocated memory 19.00 GiB is allocated by PyTorch, and 4.63 GiB is reserved by PyTorch but unallocated. ...
   fragmentation: FRAGMENTATION
     discriminating number: reserved_but_unallocated = 4.63 GiB
```

What must match on any GPU: each failing case's verdict; `capacity-fix`, `retained-fix`,
`other-process-fix` and `non-pytorch-fix` completing, and the `capacity` case getting past step 0, which
is the fragmentation fix at work; `empty_cache()` failing
to rescue the fragmentation and capacity cases, the legacy variable winning in both precedence cases,
and a zombie disappearing from NVML before it is reaped. What varies: the CUDA context and kernel
memory (173 MiB lazy and 943 MiB eager here), and with it the allowance and every number derived from
it, by a few hundred MiB. The `unified` case shows a CPU tensor shrinking CUDA's free memory only on an
integrated GPU; on a discrete card it reports the start values and stops. Batch timings are the GB10's.

## The provenance line

A number from this lab is publishable only with the line `oom_lab.py run` prints first:

```text
Captured 2026-10-30T11:44:17+00:00 on NVIDIA GB10 (sm_121, 48 SMs, 121.63 GiB unified), KMD 595.71.05, CUDA UMD 13.2, torch 2.15.0+cu132 (runtime 13.2), Cortex-X925 + Cortex-A725, Python 3.12.3, Ubuntu 24.04.4 LTS, Dell Inc. Dell Pro Max with GB10 FCM1253.
```

The KMD and CUDA UMD versions are read from NVML, not parsed from `nvidia-smi`, with the same
vocabulary as part 2 of this series. `captures.json` carries the same fields under `provenance`.

## Exercises

Do them in order. Each exercise has a self-check you can mark yourself against, with the answer
hidden below it. This is an L3 post, so the lab ships E1 to E4. E1 and E2 need no GPU.

### E1 — Reproduce: the five verdicts

Run `python diagnose.py captures.json`. It reads the five failing runs' messages from the shipped capture,
applies the decision tree, and prints the cause and the number that decided it.

**Self-check:** the five causes are fragmentation, capacity, retained graph, other process and
non-PyTorch, with discriminating numbers 4.63 GiB, 23.25 GiB, 1.55 GiB, 6.17 GiB and 4.33 GiB.

<details><summary>Answer</summary>

fragmentation 4.63 GiB reserved but unallocated against a 256 MiB request; capacity 23.25 GiB allocated
by PyTorch with nothing else holding memory; retained graph 1.55 GiB of growth per evaluation batch;
other process 6.17 GiB held by PID 189145; non-PyTorch 4.33 GiB held outside the allocator. If you ran
the GPU lab too, `python diagnose.py mine.json` must give the same five causes; on a different GPU the
numbers move by the difference in context size.

</details>

### E2 — Inspect: the slivers

The fragmentation run's allocator snapshot is summarized in `captures.json`. Read the sizes of its free
blocks and where they sit:

```python
import json

run = json.load(open("captures.json"))["runs"]["fragmentation"]["oom"]
snap = run["snapshot"]
for size, count in sorted(snap["free_block_sizes"].items(), key=lambda kv: -int(kv[0]) * kv[1]):
    print(f"{count:3d} free blocks of {int(size) / 2**20:7.1f} MiB")
print("free inside partly used segments (GiB):", snap["free_in_partly_used_segments"] / 2**30)
print("free in entirely free segments (GiB):  ", snap["free_in_empty_segments"] / 2**30)
```

Before you look at the answer, say which free blocks make up the message's 4.63 GiB, and why the
request did not use the twelve free 256 MiB blocks the snapshot also lists.

**Self-check:** 37 blocks of 128 MiB, all inside segments that still hold a live tensor, sum to the
message's 4.63 GiB; the 256 MiB blocks were still live tensors when the request failed.

<details><summary>Answer</summary>

37 × 128 MiB = 4,736 MiB = 4.625 GiB, printed as 4.63 GiB: the tails of 384 MiB segments whose 256 MiB
heads are gradients and Adam state. The twelve 256 MiB blocks sit in entirely free segments, 3.00 GiB in
all: they were the first twelve of the optimizer's sixteen temporary tensors, live when the thirteenth
failed and freed while the error unwound, before the snapshot was taken. They are also exactly what the
retry's `empty_cache()` released (`retry_after_empty_cache.released` = 3,221,225,472 bytes), and the
retried step failed anyway, because it needed them again.

</details>

### E3 — Predict: half the evaluation batch (needs G3: one NVIDIA GPU)

The retained-graph case evaluates batches of 1,536 rows without `torch.no_grad()` and fails in the
eighth. Halve the batch with `python oom_lab.py run --case retained --val-batch 768 --out e3.json`.
Before you run it, write down the growth per batch, and whether it survives all twelve batches on the
23.67 GiB allowance.

**Self-check:** the growth within 0.02 GiB, and the outcome, for the article's reason: 33 saved tensors
per batch, each 768 × 8,192 × 4 bytes.

<details><summary>Answer</summary>

Each batch keeps 33 tensors of 24 MiB, 792 MiB or 0.77 GiB. The twelfth batch starts at 12.00 + 11 ×
0.77 = 20.51 GiB and peaks below the 23.67 GiB allowance, so all twelve complete. The author's run:
`validation: 12 batches, allocated 12.00 -> 20.51 GiB`. The leak is still there; it is just slower than
the loop, which is how a halved batch hides a retained graph.

</details>

### E4 — Diagnose: an unnamed fault (needs G3: one NVIDIA GPU)

`python oom_lab.py mystery --seed 5` runs one of the five faults without naming it, and prints the
message, the allocated memory at the start of each iteration, and the other compute processes. Name the
cause and the number that proves it, apply that cause's fix with `--fix <cause>` (one of
`fragmentation`, `capacity`, `retained`, `other-process`, `non-pytorch`), and check that the run completes.
Then do the same with `--seed 7`. `--reveal` prints the answer.

**Self-check:** for each seed, the cause, the one number that proves it, a `--fix` run that ends
`completed without running out of memory`, and `--reveal` agreeing.

<details><summary>Answer</summary>

Seed 5 is **non-PyTorch memory**: this process has 23.83 GiB in use, PyTorch reserves 19.50 GiB (19.50
allocated plus 2 MiB unallocated), so 4.33 GiB is held outside the allocator; no other process is listed
and 2 MiB unallocated rules out fragmentation. `--fix non-pytorch` frees the pool and completes.

Seed 7 is a **retained graph**: allocated memory at the start of each iteration climbs 12.00, 13.55,
15.09 … 22.83 GiB, 1.55 GiB per batch. Its message shows 514 MiB unallocated against a 48 MiB request,
which alone reads as fragmentation; the growth comes first. `--fix retained` evaluates under
`torch.no_grad()` and completes. A wrong fix, `--fix capacity`, fails with the same message, which is the
point of naming the cause before fixing it.

</details>

## Safety and cleanup

- The lab touches one GPU, and only through PyTorch and NVML. It contacts no service and needs no
  network after installation.
- It writes the `--out` file and a temporary folder named `oom-lab-*` inside this folder, which it
  deletes when it finishes. Each helper process stops itself after 240 seconds, and the lab stops any
  that are left before it exits.

```bash
rm -f mine.json e3.json                # your runs; captures.json is the shipped one
pgrep -af "oom_lab.py hold" || true    # should print nothing; a leftover holder stops itself within 240 s
```
