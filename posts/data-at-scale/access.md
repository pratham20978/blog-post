# Lab access — Data at Scale: From Hadoop to the Lakehouse

> Private build artifact. Read with `plan.md` and `context.md` before every part; re-run the probe.

## Probe — 2026-09-28

Same machine as `posts/postgresql-foundations/access.md` (16 CPUs, 14 GB RAM with ~5 GB free, 223 GB
free disk, no NVIDIA GPU, Docker unusable, no java/cmake/go/rust; gcc, make and uv present).

## Requests

| ID | Need | Parts | Raised | Answer | Answered | Grade as built |
|---|---|---|---|---|---|---|
| AR-02 | A capture window with about 8 GiB of RAM free | 15, 17, 18 (and 3 and 10 if free memory is below their budgets) | Checkpoint S, 2026-09-29 | pending | | — |
| AR-03 | Multi-machine cluster time | 2, 3, 8, 10, 15 (optional legs) | Checkpoint S, 2026-09-29 | pending | | — |
| AR-04 | An AWS S3 sandbox bucket | 5 (optionally 14, for credential vending on real STS) | Checkpoint S, 2026-09-29 | pending | | — |
| AR-05 | Managed warehouse accounts | 22 (optional) | Checkpoint S, 2026-09-29 | pending | | — |
| AR-01 | Container access (docker group or rootless podman) | 8, 10, 21 (optional) | Checkpoint S, 2026-09-29 | pending | | — |

## Self-provisioned

None yet.

## Capture backlog

None yet.
