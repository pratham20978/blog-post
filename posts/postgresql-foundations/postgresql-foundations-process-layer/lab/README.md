# Lab — How PostgreSQL Uses Processes

`run_lab.py` produces every server-side number quoted in `../blog.md`. It writes
`captures.md` (psql output, verbatim, in run order) and `captures.json` (the figures'
input). The committed captures are from PostgreSQL 16.2, default `postgresql.conf`,
16 CPUs, 15 GB RAM, Samsung NVMe, Linux 7.0, run 2026-09-19.

It is the same lab as part 1 ([How PostgreSQL Uses
Memory](https://canery.in/blogs/postgresql-foundations-memory-layer)) and builds the same
two tables — `customers` at 710 pages and `orders` at 7,693 pages — so the two posts'
numbers line up. Part 2 adds two indexes on `orders` and a scratch copy of it, because
vacuum's interesting behaviour is in the index passes.

## What you need

- PostgreSQL 16.x server binaries you can start yourself. The captures used the
  `pgserver` wheel (`pip install pgserver`), which bundles 16.2 under
  `site-packages/pgserver/pginstall/`.
- The contrib modules `pg_buffercache` and `pg_prewarm` installed for that server.
  With the wheel they are not shipped; fetch `contrib/<module>/` from
  `raw.githubusercontent.com/postgres/postgres/REL_16_2/` and run
  `make USE_PGXS=1 PG_CONFIG=<pginstall>/bin/pg_config install` in each.
- `psycopg` 3, `ps` from procps, and a data directory on a **real disk**. Step 8's cold
  runs evict files from the kernel page cache with `posix_fadvise(DONTNEED)`; on tmpfs
  that would be meaningless.

## Run

```bash
initdb -D /path/pgdata -U postgres
pg_ctl -D /path/pgdata -w -o '-h ""' -o '-k /path/sock' -l /path/pgdata/server.log start
PGBIN=/path/to/bin PGDATA=/path/pgdata PGSOCK=/path/sock python3 run_lab.py
```

Takes about three minutes, most of it waiting for a real autovacuum cycle rather than
forcing one.

> [!WARNING]
> Two steps deliberately break things. Step 9 holds a snapshot open so vacuum cannot
> remove anything, and **step 15 kills a backend with `SIGKILL`**, which makes the
> postmaster terminate every other session and run crash recovery. Point this at a
> throwaway cluster, never at anything you care about.

## What each step captures

| Step | Produces |
|---|---|
| 1 | the process census: `ps --ppid <postmaster>` and one `pg_stat_activity` row per process |
| 2 | 200 fresh connections against 200 round trips on one connection; a backend's RSS |
| 3 | the two tables and their indexes, in pages |
| 4 | a timed `CHECKPOINT` over a dirtied pool, with the `log_checkpoints` line |
| 5 | `pg_stat_io` split by `backend_type`: who actually wrote each page |
| 6 | 5,000 commits with `synchronous_commit` on and off, with the `pg_stat_wal` deltas |
| 7 | the three autovacuum thresholds computed in SQL, then a real launcher cycle caught in the act |
| 8 | the same 800,000-dead-tuple vacuum at 1 MB and 256 MB of `maintenance_work_mem`, warm and cold |
| 9 | a vacuum blocked by one open `REPEATABLE READ` transaction, and the same vacuum after it commits |
| 10 | `pg_stat_progress_vacuum` sampled through every phase |
| 11 | `Workers Planned` vs `Workers Launched`, and the workers caught in `pg_stat_activity` |
| 12 | `pg_cancel_backend` vs `pg_terminate_backend`, with both error messages |
| 13 | sampled `wait_event_type` / `wait_event` by process type |
| 14 | `age(relfrozenxid)` against `autovacuum_freeze_max_age` |
| 15 | a `SIGKILL`ed backend and the postmaster's crash-recovery log |
| 16 | the cumulative counters for the whole run |

## What changes on 17 and 18

The mechanisms are the same; some names and constants are not.

- **17** moves `pg_stat_bgwriter`'s checkpoint columns to `pg_stat_checkpointer`, and
  replaces vacuum's dead-TID array with `TidStore`, which removes the 1 GB
  `maintenance_work_mem` ceiling step 8 is built on. Step 8's index-pass counts will be
  lower on 17 for the same memory setting.
- **18** adds asynchronous I/O (`io_method`, `io_workers`), so step 1's process census
  gains rows, and `pg_stat_io` gains byte columns.

The script's queries against those views need the corresponding edits.
