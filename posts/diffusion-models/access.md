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

## Probe — 2026-10-16 (part 7)

```text
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14Gi ram_available=2.5Gi
disk_free=207G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
docker=unusable
```

Unchanged since part 6. The low `ram_available` was read while part 7's notebook build was
training; part 7's `all --quick` peaked at about 3.3 GB across 9 processes.

## Probe — 2026-10-19 (part 8)

```text
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14Gi ram_available=8.0Gi
disk_free=187G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
docker=unusable
```

Unchanged since part 7 except free disk. Part 8's `all` ran 9 processes, each under 330 MB at its
peak.

## Probe — 2026-10-21 (part 9)

```text
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14G ram_available=4G
disk_free=320G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
docker=unusable
```

Unchanged since part 8 except free disk and RAM. Part 9's `all` ran on one thread in 45 s and peaked at
0.31 GB.

## Probe — 2026-10-21 (part 10)

```text
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14G ram_available=8G
disk_free=320G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
docker=unusable
```

Unchanged since part 9 except available RAM. Part 10's `all` ran on one thread in 63 s and peaked at
0.32 GB.

## Probe — 2026-10-23 (part 11)

```text
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14Gi ram_available=2.4Gi
disk_free=320G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
docker=unusable
```

Unchanged since part 10 except available RAM. Part 11's `all` ran on one thread on 2026-10-22 in
118 s and peaked at 0.29 GB.

## Requests

None raised. Every remaining part was checked against the three conditions in
`blog-authoring/references/labs.md` (load-bearing, no honest substitute, not self-providable):

| Part | What its lab needs | Grade as planned | Why no request |
|---|---|---|---|
| 4 Backbones | shapes, parameter and FLOP counts of real architectures; one attention timing | G1 (built) | the meta device gives exact counts with no weights; CPU timings are labelled as CPU timings and no claim depends on GPU speed |
| 5 Training | schedule, endpoint, target, weighting and EMA effects | G1 (built) | a Gaussian-mixture toy ("crescent world") has an exact denoiser, so every error is measured against the best possible; 50 small MLPs train on 12 CPU cores in about 30 min; published scaling results are cited, not reproduced |
| 6 Samplers | measured error at matched NFE | G1 (built) | a Gaussian-mixture target has an exact score and exact ODE, so solver error can be measured exactly on CPU — a better instrument than a GPU model, whose "true" trajectory is unknown |
| 7 Distillation | few-step students against a teacher | G1 (built) | part 6's exact crescent-world teacher (closed-form denoiser, RK4 ODE) makes every student's error the student's; seven students, two seeds each, train on 8 CPU workers in 20 min; large-model results are quoted with their setups |
| 8 Control | guidance, ControlNet, personalisation, inpainting and editing mechanics | G1 (built) | crescent world's exact class-conditional denoisers make guidance's mode loss and over-saturation measurable; a ControlNet branch, five personalisation recipes and an inpainting network train on the lab's model on 8 CPU workers in 11 min; SD 1.5's parameter counts come from the meta device; large-model results are quoted with their setups |
| 9 Evaluation | FID, KID, precision/recall and density/coverage graded against known defects; guidance re-scored | G1 (built) | crescent world's generators have exactly known defects, so every metric is graded against the truth on CPU in 45 s with numpy alone; Inception-space and human-study results are quoted with their setups |
| 10 Beyond images | per-frame vs joint video sampling, noise priors, forecasting by replacement, score distillation | G1 (built) | crescent world in motion has exact frame and clip denoisers, so every failure belongs to the sampler or the conditioning; numpy alone, about a minute on one core, 0.32 GB; video, audio, molecule and 3-D results are quoted with their setups |
| 11 Discrete diffusion | parallel decoding, ancestral and threshold samplers, decoders that do not sample, the float32 race | G1 (built) | crescent world as tokens has an exact lookup denoiser, so every failure belongs to the sampler; numpy alone, two minutes on one core, 0.29 GB; LLaDA-scale results are quoted with their setups |
| 12 Memorisation | when a sample stops being new | G0–G1 | closed-form or CPU-scale demonstrations; benchmark numbers are documented with their setups |

If a later part's plan changes so that a claim needs a real GPU run (for example, timing a
production checkpoint), raise AR-01 then, in the form `labs.md` gives; do not absorb it as a silent
downgrade.

## Self-provisioned

| What | Where | For | Undo |
|---|---|---|---|
| Python 3.12 venv with torch 2.14.0+cpu and diffusers 0.40.0 (945 MB) | `~/.cache/diffusion-models-lab/.venv`, with `freeze.txt` beside it | part 4's `census.py`, part 5's `training_decisions.py`, part 6's `samplers.py`, part 7's `distill.py`, part 8's `control.py`, part 9's `evaluate.py`, part 10's `beyond.py` and part 11's `tokens.py` (all three numpy 2.5.3 only) | `rm -rf ~/.cache/diffusion-models-lab` |

Nothing in this environment runs as a service; it holds no data and no weights. Parts 7–11
built their notebooks in throwaway `uv run --no-project` environments (nbclient, nbformat, ipykernel
and the lab's pins; part 8's adds PyTorch's CPU index for its torch pin, parts 9–11 pin numpy alone),
which live only in uv's cache.

## Capture backlog

None. Part 4's lab ran in full on 2026-10-03, part 5's on 2026-10-07, part 6's on 2026-10-09
in 15 min, part 7's on 2026-10-16 in 20 min, part 8's on 2026-10-18 in 11 min, part 9's on
2026-10-21 in 45 s, part 10's on 2026-10-21 in 63 s and part 11's on 2026-10-22 in 118 s (each part's `lab/captures.json`, provenance line in its lab README).
