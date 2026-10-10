# Outline — postgresql-foundations-process-layer

**Series:** PostgreSQL Foundations, part 2 of 3 (memory layer → **process layer** → storage layer)
**Part 1:** *How PostgreSQL Uses Memory* — https://canery.in/blogs/postgresql-foundations-memory-layer
**Tier:** L4 pillar · **Budget:** ~10,500 words · **Figures:** 24 + cover (above the 12–18 band on
purpose, as in part 1: the post spans eleven processes and every figure carries a lab number)
**Working title:** *How PostgreSQL Uses Processes* · slug `postgresql-foundations-process-layer`
**Audience:** working engineers and CS students who run Postgres and have never looked inside it.
Level intermediate. Prereqs: SQL, what a process and a signal are, having seen an EXPLAIN plan.
Part 1 is recommended but not required — every reference to it is a link, not a dependency.

**Thesis.** PostgreSQL is not one program. It is a supervisor that never touches your data and a
crowd of single-purpose processes that do — one forked per connection, plus a fixed cast of
background workers that exist because the work they do must not happen inside your query. Every
process-layer surprise an operator meets — a `VACUUM` that scans the same two indexes eleven
times, an autovacuum worker that appears 39 seconds after the threshold is crossed and then
throttles itself to 2 ms of sleep per 200 cost units, a table that cannot be cleaned because
somebody left a `BEGIN` open in another session, a query that plans six workers and launches one,
a whole server restarting because one backend was killed — is one of those processes doing
exactly what it was designed to do.

**Series framing (first 100 words).** PostgreSQL's architecture is commonly split into three
layers: memory, process, and storage. Part 1 was the memory layer. This is layer two. It stops at
the boundary where bytes hit files (part 3) and says so where it stops. Where it needs a memory
fact — what a dirty buffer is, what the write-ahead rule means — it links to the relevant section
of part 1 rather than re-teaching it.

**What this post must NOT re-teach** (link to part 1 instead):
shared buffers and the clock sweep → `#shared-buffers-what-a-buffer-actually-is`,
`#the-clock-sweep-how-a-page-gets-evicted`; the WAL buffer ring and the write-ahead rule →
`#wal-buffers-the-memory-that-must-reach-disk-first`; `work_mem` per operation per process →
`#local-memory-work_mem-and-its-family`; memory contexts →
`#memory-contexts-how-a-backend-allocates`; the non-buffer shared memory →
`#the-rest-of-shared-memory`.

**Deferred to part 3 (storage layer):** heap page layout, the visibility map and why it makes
vacuum skippable, TOAST, index internals, WAL segment files, archiving and replay, replication.

---

| # | Section | Target | Job | Figures |
|---|---|---|---|---|
| 1 | `# Title` + `## Insights` | 110 | one supervisor, N workers; every surprise is a process doing its job | — |
| 2 | Who this is for + series note + jump list | 130 | level, prereqs, time; three layers, this is layer two, part 1 linked | FIG_01 |
| 3 | `## Why this matters` | 380 | three real incidents: vacuum "running" for hours on a table it cannot clean; more autovacuum workers making nothing faster; one killed backend restarting the server | — |
| 4 | `## The problem` | 780 | a database must do work that belongs to no single query (cleanup, checkpoints, log flushes) while serving queries that must not pay for it; processes not threads; who is allowed to fork; name the whole cast with lab counts | FIG_02, FIG_03 |
| 5 | `## Worked example` | 1,350 | the lab, start to finish: 11 processes at rest; 200 connections vs 200 round trips; cross the autovacuum threshold and watch a worker appear; the same DELETE vacuumed with 1 MB vs 256 MB of `maintenance_work_mem`; one open transaction and nothing is removable; six workers planned, one launched | FIG_04, FIG_05, FIG_06, FIG_07 |
| 6 | `## Intuition` | 820 | the kitchen: one maître d' who only seats people, a cook per table, and a cleaning crew that works between orders. Where each analogy breaks (the maître d' can't cook; the crew can be starved by one customer who never leaves) | FIG_08 |
| 7 | `## The postmaster: the process that never touches your data` | 700 | PostmasterMain → shmem → listen → ServerLoop → fork; why it holds no critical state; HandleChildCrash and the lab's SIGKILL capture; the death pipe; SIGHUP reload; `restart_after_crash` | FIG_09, FIG_10 |
| 8 | `## What a connection actually costs` | 700 | fork + auth + InitPostgres; the lab's per-connection milliseconds; relcache/catcache/plancache are per-process and never shared; sinval; why poolers exist; what `max_connections` sizes | FIG_11, FIG_12 |
| 9 | `## How one process interrupts another` | 650 | no preemption inside a query; CHECK_FOR_INTERRUPTS; ProcSignal multiplexed over SIGUSR1; cancel vs terminate, with the lab's two error messages; latches and WaitEventSet; wait events as the observable surface | FIG_13, FIG_14 |
| 10 | `## The checkpointer: making the WAL forgettable` | 800 | what a checkpoint is for (bounding recovery, freeing WAL); redo point vs checkpoint record; `checkpoint_timeout` / `max_wal_size` / `checkpoint_completion_target` and the spread; the fsync request queue backends forward to it; the lab's log line and timings; restartpoints; the 17 column move | FIG_15, FIG_16 |
| 11 | `## The background writer, and why your backend still writes pages` | 600 | BgBufferSync walking ahead of the clock hand; the smoothed allocation estimate; the three defaults; the lab's `pg_stat_io` split showing who actually wrote; hibernation; the honest verdict on its usefulness | FIG_17 |
| 12 | `## The WAL writer and what a commit waits for` | 700 | XLogFlush on the committing backend vs the WAL writer's background flush; `synchronous_commit` levels; the lab's on-vs-off throughput; the documented loss window; group commit | FIG_18, FIG_19 |
| 13 | `## Autovacuum, part one: how it decides` | 900 | launcher naptime/N_databases; it asks the postmaster to fork; the three threshold formulas with the lab's computed numbers; n_dead_tup is an estimate; anti-wraparound ages; the cost-balance that makes more workers useless | FIG_20, FIG_21, FIG_22 |
| 14 | `## Autovacuum, part two: what the worker actually does` | 900 | the phase state machine from `pg_stat_progress_vacuum`; the index-pass multiplier and the lab's 1 MB vs 256 MB run; dead-TID memory arithmetic and 17's TidStore; the xmin horizon and the lab's blocked vacuum; failsafe; VACUUM FULL is a different thing | FIG_23, FIG_24 |
| 15 | `## Parallel workers and the shared pool` | 600 | bgworker framework; only the postmaster forks; the three pool settings; Workers Planned vs Launched from the lab; leader participation; what cannot be parallelised | FIG_25 |
| 16 | `## The rest of the cast` | 450 | startup, archiver, walsender/walreceiver, logical replication launcher, slot sync; the stats collector that no longer exists; 18's io_workers | FIG_26 |
| 17 | `## The math` | 800 | (a) autovacuum arrival time = naptime/N_db + queue; (b) index passes = ⌈dead_tids / (mwm/bytes_per_tid)⌉ with the lab's numbers; (c) cost-delay throughput = cost_limit/cost_delay pages per second, divided among workers; (d) recovery bound from checkpoint_timeout and max_wal_size; (e) connection capacity | — |
| 18 | `## Implementation` | 700 | the toolkit as runnable SQL: process census, who-wrote-what, autovacuum debt query, xmin-horizon query, progress watcher, wait-event sampler; version notes 16 vs 17 vs 18; link to `lab/run_lab.py` | FIG_27 |
| 19 | `## Limitations and common mistakes` | 500 | autovacuum off; more workers; long transactions and stale slots; `maintenance_work_mem` left at 64 MB; VACUUM FULL as routine maintenance; reading `last_autovacuum` as proof of cleanliness; connection sprawl; what this post does not cover | — |
| 20 | `## Key takeaways` | 110 | 5 claims | — |
| 21 | `## Try it yourself` | 220 | 3 exercises with hidden answers, runnable on the lab | — |
| 22 | `## References` | 70 | ledger sources actually used, grouped T1/T2/T3 | — |

**Total target:** ~10,500 words. Figure ratio ≈ one per 400 words.

---

## Figure plan

| ID | Type | Route | Carries |
|---|---|---|---|
| COVER | template cover | diagram-design skin | one supervisor node above a row of worker nodes, one tangerine |
| FIG_01 | layer stack | diagram-design layers | memory / **process** / storage, this post highlighted, part 1 greyed |
| FIG_02 | process tree | diagram-design tree | the postmaster and its eleven children at rest, from the lab's `ps` output |
| FIG_03 | responsibility map | diagram-design nested | which process owns which job, and which pool from part 1 it touches |
| FIG_04 | bars | diagram-design bar | 200 fresh connections vs 200 round trips (lab ms) |
| FIG_05 | timeline | diagram-design timeline | threshold crossed → launcher wakes → postmaster forks → worker runs (lab seconds) |
| FIG_06 | grouped bars | diagram-design bar | 1 MB vs 256 MB `maintenance_work_mem`: index passes and seconds |
| FIG_07 | before/after | small multiples | vacuum with a snapshot held vs released: removed vs non-removable |
| FIG_08 | analogy | diagram-design | the kitchen, with the break points annotated |
| FIG_09 | sequence | Mermaid sequenceDiagram → redraw | client connect → ServerLoop → fork → auth → InitPostgres → query loop |
| FIG_10 | state/flow | Mermaid flowchart → redraw | child exits: clean vs SIGKILL → HandleChildCrash → terminate all → recovery |
| FIG_11 | to-scale bars | diagram-design | per-backend private memory vs the shared segment (bridges to part 1) |
| FIG_12 | containment | diagram-design nested | relcache/catcache/plancache per backend, and sinval as the only link |
| FIG_13 | sequence | Mermaid sequenceDiagram → redraw | pg_cancel_backend: SIGUSR1 → ProcSignal slot → latch → CHECK_FOR_INTERRUPTS |
| FIG_14 | horizontal bars | diagram-design bar | the lab's sampled wait events by process type |
| FIG_15 | timeline | diagram-design timeline | a checkpoint's phases against `checkpoint_timeout` and `completion_target` |
| FIG_16 | process | diagram-design | backend fsync request → CheckpointerShmem queue → checkpointer; queue-full fallback |
| FIG_17 | stacked bars | diagram-design bar | lab `pg_stat_io`: writes by checkpointer / bgwriter / client backend |
| FIG_18 | sequence | Mermaid sequenceDiagram → redraw | commit with `synchronous_commit` on vs off, showing who waits |
| FIG_19 | bars | diagram-design bar | 5,000 commits: on vs off (lab tps) |
| FIG_20 | formula figure | diagram-design | the three thresholds drawn against `customers`' real row count |
| FIG_21 | timeline | diagram-design timeline | launcher naptime → database pick → postmaster fork → worker |
| FIG_22 | comparison | diagram-design | one worker vs three workers under a shared cost limit: same total I/O |
| FIG_23 | state machine | Mermaid stateDiagram-v2 → redraw | the vacuum phases from `pg_stat_progress_vacuum` |
| FIG_24 | algorithm trace | small multiples | heap scan fills the TID store → full index pass → resume; ×N |
| FIG_25 | plan tree | diagram-design tree | Gather with planned vs launched workers and the shared pool |
| FIG_26 | map | diagram-design | the optional processes and the condition that makes each exist |
| FIG_27 | tooling map | diagram-design | which view sees which process, and in which version |

Ratio: 27 figures + cover / ~10,500 words ≈ one per 390 words. Every figure carries a lab number
or a mechanism; none repeats a neighbour at a different zoom.

---

## Padding test

After each section the reader can:

- Problem → name every process in a running server and say which one is allowed to fork
- Worked example → predict whether a given table will be autovacuumed, and roughly when
- Intuition → explain the supervisor/worker split and say where the analogy breaks
- Postmaster → explain why one killed backend restarts the whole server
- Connection cost → justify a pooler with a number instead of a feeling
- Interrupts → explain why `pg_cancel_backend` sometimes appears to do nothing
- Checkpointer → read a `log_checkpoints` line and say what triggered it
- Background writer → say which process wrote a given dirty page, from `pg_stat_io`
- WAL writer → state exactly what `synchronous_commit = off` risks, and what it does not
- Autovacuum decide → compute a table's threshold and its arrival time
- Autovacuum do → explain an eleven-pass vacuum and fix it with one setting
- Parallel workers → explain `Workers Planned: 6, Workers Launched: 1`
- Rest of the cast → say why a given process is or is not present on their server
- Math → size `maintenance_work_mem` and `autovacuum_vacuum_cost_limit` for a real table
- Implementation → run the census and debt queries on their own server

No two answers match. Sections 7–16 each own one process or one decision.
