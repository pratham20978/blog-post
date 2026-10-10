# Lab access — PostgreSQL Foundations

> Private build artifact. Read with `plan.md` and `context.md` before every part; re-run the probe
> from blog-forge `references/labs.md` and compare.

## Probe — 2026-10-02 (re-run for part 5)

Identical to 2026-10-01 below (RAM available 9G, free disk 221G, same tools and headers). No deltas,
no access request: part 5's lab is G2 on the 18.6 binaries.

## Probe — 2026-10-01 (re-run for part 4)

```text
Linux 7.0.0-31-generic x86_64 · Ubuntu 26.04.1 LTS
cpus=16 ram_total=14G ram_available=9G disk_free=221G on /
gpu: AMD Barcelo integrated (no NVIDIA GPU) · nvidia_gpu=none
groups: prathamv adm cdrom sudo dip plugdev lpadmin sambashare (sudo is not usable non-interactively)
docker=unusable (socket permission denied; not in the docker group)
gcc=yes make=yes uv=yes psql=yes (client 18.6) cmake=no meson=no ninja=no bison=no flex=no java=no go=no rustc=no podman=no kubectl=no
zlib.h=yes readline.h=yes openssl/ssl.h=yes zstd.h=yes curl.h=yes libxml2=yes icu-uc=78.2 krb5=yes lz4.h=no event.h=no yaml.h=no
m4=1.4.21 perl=5.40.1 python=3.14.4
```

**Deltas from 2026-09-28:** available RAM 5G → 9G, free disk 223G → 221G. Nothing a plan depended
on changed. Still no bison or flex, which part 4 had to work around (see Self-provisioned).

## Probe — 2026-09-28

```text
Linux 7.0.0-31-generic x86_64 · Ubuntu 26.04
cpus=16 ram_total=14G ram_available≈5G disk_free=223G on /
gpu: AMD Barcelo integrated (no NVIDIA GPU) · nvidia_gpu=none
groups: prathamv adm cdrom sudo dip plugdev lpadmin sambashare (sudo is not usable non-interactively)
docker=unusable (socket permission denied; not in the docker group)
gcc=yes make=yes uv=yes psql=yes (client 18.6) cmake=no meson=no ninja=no bison=no flex=no java=no go=no rustc=no
zlib.h=yes readline.h=yes openssl/ssl.h=yes zstd.h=yes curl.h=yes libxml2=yes icu=yes krb5=yes lz4.h=no event.h=no yaml.h=no
```

## Requests

| ID | Need | Parts | Raised | Answer | Answered | Grade as built |
|---|---|---|---|---|---|---|
| AR-01 | container runtime for `kind` (docker group or rootless podman) | 45 | Checkpoint S, 2026-09-29 | pending | | — |
| AR-02 | real network partitions (root for `tc netem`, or 3 small VMs) | 23 (optional) | Checkpoint S, 2026-09-29 | pending | | — |
| AR-03 | one sudo session for sysctls (huge pages, `vm.*`, perf) | 28, 32 (optional) | Checkpoint S, 2026-09-29 | pending | | — |
| AR-04 | four small VMs for one day | 42 (optional) | Checkpoint S, 2026-09-29 | pending | | — |
| AR-05 | cloud sandbox with a spend cap | 43 (optional) | Checkpoint S, 2026-09-29 | pending | | — |

**Smallest arrangements.** AR-01: `sudo usermod -aG docker prathamv`, then log out and in (or enable
rootless podman). AR-02: three small VMs on one private network for one day, or permission for one
`sudo tc qdisc` session. AR-03: one supervised `sudo sysctl` session, reverted after capture. AR-04:
four 2 vCPU / 8 GB VMs for one day with a budget alarm. AR-05: one sandbox account with a spend cap
and the smallest managed PostgreSQL instance, deleted after capture.

## Self-provisioned

| What | Where | For | Undo |
|---|---|---|---|
| PostgreSQL 16.2 (pgserver wheel) + contrib via pgxs | `~/.cache/blog-pg-lab/` | Parts 1–3 | shared and live: remove only when the series closes |
| PostgreSQL 18.6 binaries, built from the official source release | `~/.cache/blog-pg18-lab/pginstall` (40 MB) | Parts 4–46 | binaries only, nothing running. Each part `initdb`s a temporary cluster and deletes it after capture (owner, 2026-10-01). Part 4's cluster and the 253 MB build tree were deleted 2026-10-01; part 5's 235 MB cluster on 2026-10-02. Remove the binaries with `rm -rf ~/.cache/blog-pg18-lab` |
| bison 3.8.2 and flex 2.6.4, from Ubuntu `.deb`s unpacked with `dpkg-deb -x` | `~/.cache/blog-pg18-lab/tools/prefix` | building PostgreSQL 18.x | delete the directory; nothing was installed system-wide |

## Capture backlog

None yet.

## Build notes

**The 18.x tarball needs bison and flex; this machine has neither and sudo is not usable.**
Unlike the 16.x releases, the PostgreSQL 18.6 source tarball ships no pre-generated parser
(`src/backend/parser/gram.c` and `scan.c` are absent), so both tools are required. They were
staged under `$HOME` without root by `apt-get download bison flex` (which needs no privileges)
and `dpkg-deb -x` into a private prefix, with `BISON_PKGDATADIR` pointed at its skeleton
directory. No access request was needed: this meets all six self-provisioning conditions in
blog-forge `references/labs.md`. Any later part that rebuilds the server needs the same two lines
on `PATH`.

Configured as:

```bash
./configure --prefix=~/.cache/blog-pg18-lab/pginstall --with-openssl --with-zstd --with-libxml
```

`--with-lz4` was left off because `lz4.h` is absent. `pageinspect`, `pg_buffercache`,
`pg_prewarm`, `pg_walinspect`, `pg_stat_statements` and the rest of contrib are built and
installed. Cluster: `initdb --encoding=UTF8 --locale=C.UTF-8`, default `postgresql.conf`, started
with `-k <sock> -h ''` so it listens on a unix socket only.

**Carried forward from part 4:** `customers` is 710 pages and `orders` 7,693 pages on 18.6 —
identical to the 16.2 figures parts 1–3 published. The series' page counts survive the version
change; 17.x remains untested and is asserted nowhere.
