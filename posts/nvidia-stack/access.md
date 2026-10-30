# Lab access — The NVIDIA Stack

> Private build artifact. Read with `plan.md` and `context.md` before every part; re-run the probe
> from blog-forge `references/labs.md` and compare. Created 2026-09-29: this series was planned
> before access requests existed, so its GPU needs were never raised. They are raised here.

## Probe — 2026-09-29

```text
Linux 7.0.0-31-generic x86_64 · Ubuntu 26.04.1 LTS
cpus=16 ram_total=14G ram_available=2G disk_free=222G on /
gpu: AMD Barcelo integrated graphics — not an NVIDIA GPU
nvidia_gpu=none   nvcc=no
docker=unusable (not in the docker group)
gcc=yes make=yes uv=yes; cmake/java/go/rustc=no
```

## Probe — the GB10 host, 2026-10-30

```text
Dell Pro Max with GB10 (FCM1253) · Ubuntu 24.04.4 LTS · kernel 6.17.0-1021-nvidia · aarch64
cpu: Cortex-X925 + Cortex-A725, 20 cores · memory: 121.63 GiB, shared by CPU and GPU
gpu: NVIDIA GB10 (sm_121, 48 SMs, integrated) · KMD 595.71.05 · CUDA UMD 13.2
nvidia-smi Memory-Usage: Not Supported (unified memory); NVML per-process memory: yes
python3.12 (3.12.3) from the system; uv 0.12.5 is the owner's own; sudo: not used
a live desktop: Xorg, gnome-shell, Firefox, nautilus and VS Code hold 792 MiB of graphics memory
```

The machine is the owner's workstation: never fill its memory (Part 4 emulated a 24 GiB card
instead), keep every file under one folder in the home directory, and delete it after the capture.

## Requests

**Access request AR-01: one NVIDIA GPU** (parts 3, 4, 5, 6, 8, 9, 10)

- **Need:** one NVIDIA GPU with its driver and a CUDA build of PyTorch, for one capture session per
  part (Part 3's two scripts take about two minutes). About 24 GB of VRAM lets Part 4 use its planned
  20 GiB model as written; a smaller card works if that example is scaled down. **Part 8 measures a
  TMA layout on the same GPU, so the card must have TMA (Hopper-class or newer)**; any recent
  consumer card covers parts 3, 4, 5 and 9. Part 10's number formats depend on the generation, so
  pin the card at that part's research time.
- **Why quality needs it:** these parts' worked examples are measurements: Part 3 settles whether
  `nvidia-smi` reads 100% on a mostly idle GPU; Part 4 reproduces five real OOMs with the allocator
  summary after each; Part 5 profiles a real slow model; Part 8 measures bandwidth for four layouts;
  Part 9 times four implementations. Without a GPU each becomes a labelled model plus documented
  numbers, and the E4 "diagnose" exercises run on the model instead of the hardware.
- **Probe found:** `nvidia_gpu=none` (the only display controller is an integrated AMD APU).
- **Smallest arrangement:** SSH access to one rented single-GPU cloud instance per capture session,
  as a host alias in your `~/.ssh/config`. Nothing on this machine changes, and credentials stay in
  your SSH config, never in a lab file. Tear the instance down after each capture.
- **If declined:** each part ships a G1 labelled model for its worked example, plus its G3 harness
  syntax-checked and unrun with an empty `results-schema.json`. Measured claims become documented
  ones, and the README says `**Executed:** partly`.
- **Answer:** `grant`, 2026-10-30, as a machine rather than a rented instance: an NVIDIA GB10
  workstation (Dell Pro Max with GB10) on the owner's network, reached over SSH from this machine.
  The owner gives the address and password in chat; neither is stored in any file. A first host
  offered on 2026-10-26 refused SSH from here, and Part 4 waited for this one. Whether the GB10 has
  the TMA Part 8 needs is still to be checked at that part's research time.

**Access request AR-02: a multi-GPU node, and several GPU generations** (parts 7, 12, 14, 15)

- **Need:** one node with at least two NVIDIA GPUs (NVLink preferred) for parts 14 and 15, rented by
  the hour and captured once per part. Part 12 runs four engines on identical hardware. Part 7
  needs short sessions on three GPU generations for the same GEMM inner loop.
- **Why quality needs it:** Part 14 reads a real multi-GPU hang transcript down to the rank that
  hung, and Part 15 places one too-large model four ways and measures each. Neither exists on one
  GPU, and a single-GPU run would teach something false about collectives.
- **Probe found:** `nvidia_gpu=none`.
- **Smallest arrangement:** a 2–4 GPU instance by the hour for each of parts 14 and 15, and three
  short single-GPU sessions on different generations for Part 7, each with a budget alarm.
- **If declined:** documented numbers from dated primary sources, harnesses unrun with empty
  schemas, and each part's Limitations says what was not measured.
- **Answer:** `grant`, `decline` or `later`

| ID | Need | Parts | Raised | Answer | Answered | Grade as built |
|---|---|---|---|---|---|---|
| AR-01 | one NVIDIA GPU (TMA-capable for Part 8) | 3, 4, 5, 6, 8, 9, 10 | before Part 4, 2026-09-29 | grant: a GB10 on the owner's network | 2026-10-30 | Part 4: G3 |
| AR-02 | a multi-GPU node, and three GPU generations | 7, 12, 14, 15 | before Part 4, 2026-09-29 | pending | | — |

## Self-provisioned

| What | Where | For | Undo |
|---|---|---|---|
| not yet needed: a toolkit-only CUDA install (no driver, no root) is self-providable if a part needs `nvcc` | under `~/.cache/` | Tier A compilation | delete the directory |
| a uv virtualenv (torch 2.15.0+cu132, numpy 2.3.4), its own uv cache, the lab and probes: 5.4 GB | `~/canery-lab` on the GB10 | Part 4's capture | deleted 2026-10-30 after the capture |

## Capture backlog

| Part | Files | Waiting on | Then |
|---|---|---|---|
| 3 | `lab/step_timing.py`, `lab/util_probe.py` | a session on the GB10 (AR-01 granted; not run in Part 4's) | run, fill `results.json`, and add the measured result before upload (the part is not published yet) |
| 6 | `examples/benchmark.sh` (AIperf harness) | a session on the GB10; check its engine runs on aarch64 | run on one GPU and fill `examples/benchmark-report.md` |
