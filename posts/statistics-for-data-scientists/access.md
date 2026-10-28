# Lab access — Statistics for Data Scientists

> Private build artifact. Read with `plan.md` and `context.md` before every part; re-run the probe.

## Probe — 2026-10-23

```
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14G ram_available=3G
disk_free=320G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
groups=prathamv adm cdrom sudo dip plugdev lpadmin sambashare
docker=unusable
gcc=yes make=yes cmake=no meson=no ninja=no bison=no flex=no java=no go=no rustc=no uv=yes psql=yes podman=no kubectl=no
zlib.h=yes readline/readline.h=yes openssl/ssl.h=yes zstd.h=yes lz4.h=no event.h=no yaml.h=no
```

Lines added for what this series' labs need:

```
python 3.14.4 (also /usr/bin/python3.12 = 3.12.15); uv 0.11.26
g++=yes gfortran=yes
R 4.5.2 (2025-10-31)
R present: MASS 7.3.65, boot 1.3.32, nlme 3.1.168, mgcv 1.9.4, survival 3.8.6, Matrix 1.7.4
R absent: lme4, glmmTMB, sandwich, lmtest, car, carData, rstan, brms, coin, qvalue
system python: numpy, scipy, pandas, statsmodels, matplotlib, pymc, arviz all absent
uv resolver (nothing installed), Python 3.14 and 3.12: numpy 2.5.4, scipy 1.18.1, pandas 3.1.0,
  statsmodels 0.15.0, matplotlib 3.11.2, pymc 6.3.2, pytensor 3.3.4, arviz 1.3.0
```

Everything this series needs is present or user-space installable. R 4.5.2 with its recommended
packages gives an independent reference for `lm`, `glm`, `MASS::glm.nb`, `boot.ci` and `nlme::lme`
without installing anything. PyTensor (under PyMC) compiles with the system `g++`. `lme4` is absent;
its `nloptr` dependency may need CMake, which installs from pip inside the lab venv. There is no
NVIDIA GPU and Docker is unusable; neither matters, since no part needs a GPU or a container. The
`sudo` group is membership only and is not used.

Available RAM was about 3 GiB at the probe, because other processes held 12 GiB. Every planned lab
fits well under 1 GiB, including small multi-chain PyMC runs, but re-probe at each part and keep the
Part 12 and 18 runs small.

## Probe — 2026-10-24 (Part 1)

```
ram_total=14G ram_available=6G
disk_free=318G on /
everything else as on 2026-10-23
```

Part 1's full lab run peaked at 0.2 GB of RAM and took 4.6 to 9 s, depending on load.

## Probe — 2026-10-26 (Part 2)

```
ram_total=14G ram_available=4G at the start of the build, 6G at its end
disk_free=319G on /
everything else as on 2026-10-23
```

Part 2's lab, measured with `/usr/bin/time -v` on the frozen `sampling.py` (f73eec698b31): the full
run peaked at 0.28 GB in 212 s, `--quick` at 0.27 GB in 98 s, and the E4 fault run at 0.46 GB in
10 s. The exact Berry–Esseen stage takes 76 to 79 s of the first two, whatever the budget.

## Probe — 2026-10-28 (Part 3)

```
ram_total=14G ram_available=2G
disk_free=319G on /
everything else as on 2026-10-23
```

Part 3's lab, measured with `/usr/bin/time -v` on the frozen `estimators.py` (453f0b844e69): the full run
peaked at 0.13 GB in 12.4 s, `--quick` at 0.10 GB in 2.7 s, and the E4 fault run at 0.10 GB in 1.4 s.
Available RAM was the lowest yet, so later labs should keep checking it before long runs.

## Requests

None. Every part is **G1 — runs anywhere**, self-provisioned. No hardware, privilege, credential or
gated service is load-bearing for any worked example, figure or claim.

| ID | Need | Parts | Raised | Answer | Answered | Grade as built |
|---|---|---|---|---|---|---|
| — | none | — | — | — | — | G1 throughout |

## Self-provisioned

Created as each part's build needs it. On 2026-10-24, Part 1 created
`~/.cache/statistics-for-data-scientists-lab/venv312` (Python 3.12.15, NumPy 2.5.4, SciPy 1.18.1;
183 MB). Its notebook ran in a throwaway `uv run --with` environment from uv's cache, and its R
cross-check used the system R's MASS, so nothing was installed into R. On 2026-10-26, Part 2 reused
the venv unchanged; its notebook ran the same way (nbclient 0.11.0, nbformat 5.11.1, ipykernel
7.4.0), its R cross-check used base R only, and the 23.7 MB UCI archive behind its spend CSV was
downloaded to the session scratchpad, not the repository. On 2026-10-28, Part 3 reused the venv
unchanged; its notebook ran the same way, its private R check used base R only (`choose`, `dpois`,
`lm`), and the papers it read were downloaded to the session scratchpad.

| What | Where | For | Undo |
|---|---|---|---|
| `uv` venv: NumPy, SciPy, pandas, statsmodels, Matplotlib, pinned per part | `~/.cache/statistics-for-data-scientists-lab/` | all parts | delete the directory |
| PyMC and ArviZ in the same venv | same | 12, 18 | same |
| Isolated R library: `lme4` (CMake from pip if `nloptr` needs it), `sandwich` | `~/.cache/statistics-for-data-scientists-lab/R-lib`, via `R_LIBS_USER` | 14, 16, 17 cross-checks | delete the directory |
| Public datasets (NIST StRD, UCI, Gelman–Hill radon, Rdatasets CSVs) | each post's `lab/data/`, or its scratch directory when not redistributable | per part | delete the files |

The user's default R library (`~/R/x86_64-pc-linux-gnu-library/4.5`) is not touched. All of the
above meet the six self-provision conditions in `references/labs.md`: user space only, no root, no
account, one directory to delete, well inside the RAM and disk headroom, and new and disposable.

## Capture backlog

None. Nothing is deferred for want of a resource.
