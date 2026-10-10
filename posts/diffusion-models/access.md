# Lab access — Diffusion Models

Private build artifact: never linked, never uploaded. Created 2026-10-03 at the start of part 4,
because the series was planned before blog-forge's graded-lab rules and had no access file.

## Probe — 2026-10-03

```text
Linux 7.0.0-31-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14G ram_available=8G
disk_free=221G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
groups=prathamv adm cdrom sudo dip plugdev lpadmin sambashare
docker=unusable
gcc=yes make=yes cmake=no meson=no ninja=no bison=no flex=no java=no go=no rustc=no uv=yes psql=yes podman=no kubectl=no
zlib.h=yes readline/readline.h=yes openssl/ssl.h=yes zstd.h=yes lz4.h=no event.h=no yaml.h=no
```

The only display controller is an integrated AMD APU; there is no NVIDIA GPU. Docker is unusable
(not in the docker group), as recorded for the PostgreSQL Foundations series.

## Probe — 2026-10-09 (part 6)

```text
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14Gi ram_available=4.8Gi
disk_free=218G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
docker=unusable
```

Unchanged except the kernel (7.0.0-31 → 7.0.0-38). Part 6's full lab run peaked at about 1.7 GB
across 9 processes, well inside what is free.

## Requests

None raised. Every remaining part was checked against the three conditions in
`blog-authoring/references/labs.md` (load-bearing, no honest substitute, not self-providable):

| Part | What its lab needs | Grade as planned | Why no request |
|---|---|---|---|
| 4 Backbones | shapes, parameter and FLOP counts of real architectures; one attention timing | G1 (built) | the meta device gives exact counts with no weights; CPU timings are labelled as CPU timings and no claim depends on GPU speed |
| 5 Training | schedule, endpoint, target, weighting and EMA effects | G1 (built) | a Gaussian-mixture toy ("crescent world") has an exact denoiser, so every error is measured against the best possible; 50 small MLPs train on 12 CPU cores in about 30 min; published scaling results are cited, not reproduced |
| 6 Samplers | measured error at matched NFE | G1 (built) | a Gaussian-mixture target has an exact score and exact ODE, so solver error can be measured exactly on CPU — a better instrument than a GPU model, whose "true" trajectory is unknown |
| 7 Distillation | few-step students against a teacher | G1 | distil the same exact-score toy teacher; large-model numbers are documented |
| 8 Control | CFG and conditioning mechanics | G1 | a toy conditional model shows the mechanics; ControlNet/LoRA results are documented |
| 9–12 | evaluation, other modalities, discrete diffusion, memorisation | G0–G1 | closed-form or CPU-scale demonstrations; benchmark numbers are documented with their setups |

If a later part's plan changes so that a claim needs a real GPU run (for example, timing a
production checkpoint), raise AR-01 then, in the form `labs.md` gives; do not absorb it as a silent
downgrade.

## Self-provisioned

| What | Where | For | Undo |
|---|---|---|---|
| Python 3.12 venv with torch 2.14.0+cpu and diffusers 0.40.0 (945 MB) | `~/.cache/diffusion-models-lab/.venv`, with `freeze.txt` beside it | part 4's `census.py`, part 5's `training_decisions.py` and part 6's `samplers.py` (numpy 2.5.3 is in it); reusable for parts 7–8 | `rm -rf ~/.cache/diffusion-models-lab` |

Nothing in this environment runs as a service; it holds no data and no weights.

## Capture backlog

None. Part 4's lab ran in full on 2026-10-03, part 5's on 2026-10-07 and part 6's on 2026-10-09
in 15 min (each part's `lab/captures.json`, provenance line in its lab README).
