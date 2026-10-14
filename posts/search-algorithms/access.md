# Lab access — Search Algorithms: The Price of the Skip

Created 2026-10-14 at the start of Part 2, because the series was planned (2026-09-23) before the
graded-lab rules and had no `access.md`. The series' lab contract is `plan.md` › *The lab policy*:
counts over timings, Python everywhere except Part 4 (C), timings only in Parts 4, 7, 14 and 15.
Under that contract every remaining part's lab is **G1 — runs anywhere**.

## Probe — 2026-10-14

```text
Linux 7.0.0-38-generic x86_64
Ubuntu 26.04.1 LTS
cpus=16
ram_total=14G ram_available=4G
disk_free=217G on /
gpu: VGA compatible controller: Advanced Micro Devices, Inc. [AMD/ATI] Barcelo (rev c1)
nvidia_gpu=none
groups=prathamv adm cdrom sudo dip plugdev lpadmin sambashare
docker=unusable
gcc=yes make=yes cmake=no meson=no ninja=no bison=no flex=no java=no go=no rustc=no uv=yes psql=yes podman=no kubectl=no
zlib.h=yes readline/readline.h=yes openssl/ssl.h=yes zstd.h=yes lz4.h=no event.h=no yaml.h=no
```

CPU: AMD Ryzen 7 5825U. Python 3.14.4 (the repo's `.venv`).

## Requests

None. Checked against every remaining part's planned lab:

| Parts | Lab needs | Grade | Why no request |
|---|---|---|---|
| 2, 3, 5, 6, 8, 9, 10, 11, 12, 16–18 | Python standard library, counts only | G1 | present |
| 4 | C, a compiler, timings across cache sizes | G1 | `gcc=yes`; a quiet CPU, not access |
| 7 | Python `re` timings | G1 | present |
| 13 | numpy | G1 | CPU wheel in a `uv` environment, self-providable |
| 14, 15 | numpy, hnswlib, faiss-cpu; a small public vector dataset | G1 | CPU wheels via `uv`; the dataset is a public download whose size and licence the part's README states |

No part needs a GPU (the plan excludes GPU search), root, Docker or a paid service. A part that
changes this must raise its request at its own brief.

## Self-provisioned

| What | Where | For | Undo |
|---|---|---|---|
| Temurin JDK 25.0.4.1 (tarball from api.adoptium.net, 141 MB) | the session scratchpad, `jdk/` | Part 2: a private cross-check that the lab's Python port of `java.util.TreeMap` matches the real class (comparisons per insert, tree shape and colours, lookups, `floorKey`, `subMap`); not shipped, the lab stays Python | delete the scratchpad's `jdk/` directory; removed when Part 2 passed its gate |

## Capture backlog

| Part | Files | Waiting on | Then |
|---|---|---|---|
