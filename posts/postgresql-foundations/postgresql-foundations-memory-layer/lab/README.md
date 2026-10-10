# Lab — How PostgreSQL Uses Memory

`run_lab.py` produces every server-side number quoted in `../blog.md`. It writes
`captures.md` (psql output, verbatim, in run order) and `captures.json` (the figures'
input). The committed captures are from PostgreSQL 16.2, default `postgresql.conf`,
16 CPUs, 15 GB RAM, Samsung NVMe, Linux 7.0, run 2026-09-18.

## What you need

- PostgreSQL 16.x server binaries you can start yourself. The captures used the
  `pgserver` wheel (`pip install pgserver`), which bundles 16.2 under
  `site-packages/pgserver/pginstall/`, including `pg_config` and `pgxs`.
- The contrib modules `pg_buffercache`, `pg_prewarm`, `pg_walinspect` and
  `pageinspect` installed for that server. With the wheel they are not shipped; fetch
  `contrib/<module>/` from `raw.githubusercontent.com/postgres/postgres/REL_16_2/` and
  run `make USE_PGXS=1 PG_CONFIG=<pginstall>/bin/pg_config install` in each.
- `fincore` from util-linux, `psycopg` 3, and a data directory on a **real disk**
  (not tmpfs — the cold-read step would be meaningless).

## Run

```bash
initdb -D /path/pgdata -U postgres
pg_ctl -D /path/pgdata -w -o '-h ""' -o '-k /path/sock' -l /path/pgdata/server.log start
PGBIN=/path/to/bin PGDATA=/path/pgdata PGSOCK=/path/sock python3 run_lab.py
```

The script restarts the server once (to empty shared buffers), evicts the two table
files from the kernel page cache with `posix_fadvise(DONTNEED)`, and resets the
cumulative statistics views at the start so `pg_stat_io`, `pg_stat_wal` and
`pg_stat_bgwriter` describe this run only. It takes about a minute.

## What changes on 17 and 18

The mechanisms are the same; some constants and column names are not. On 17 the
vacuum ring defaults to 2 MB and `pg_stat_bgwriter`'s checkpoint columns move to
`pg_stat_checkpointer`. On 18 the bulk-read ring is larger than 256 KB (so "32 buffers"
becomes a bigger number), `pg_stat_io` has byte columns instead of `op_bytes`,
`pg_backend_memory_contexts` has `path`/`type` and no `parent`, and `EXPLAIN ANALYZE`
shows buffers without asking. The script's queries against those views will need the
corresponding edits.
