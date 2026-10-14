# PostgreSQL practice setups

## Binaries

- **PostgreSQL Foundations parts 1–3 (16.2).** These come from the `pgserver` Python package, installed in the virtual environment at `~/.cache/blog-pg-lab/pgvenv`:
  `BIN=$(cat ~/.cache/blog-pg-lab/pginstall.path)/bin`.
  - Add-ons compiled into it: `pg_buffercache`, `pg_prewarm`, `pg_walinspect`, `pageinspect`, `pg_visibility`, `pg_freespacemap`, `pgstattuple`.
  - Before promising one, check `$BIN/../share/postgresql/extension/<name>.control` exists.
- **Part 4 onwards (18.6, built from source).**
  `BIN=$HOME/.cache/blog-pg18-lab/pginstall/bin`.
- **Pick the version the post's lab used.** The machine itself has only the psql 18 client. It has no server, no sudo, and Docker can't be used.
- **If they ask where `$BIN` comes from:** it is a user-local install, a Python package that carries compiled PostgreSQL programs. To rebuild it:
  ```bash
  uv venv pgvenv --python 3.12
  uv pip install --python pgvenv/bin/python pgserver
  ```
  then write the package's `pginstall` path into `pginstall.path`.

## Setup template

This form of the start command has been run successfully.

```bash
BIN=$(cat ~/.cache/blog-pg-lab/pginstall.path)/bin
export PGHOST=$HOME/pg-<name>/sock PGUSER=postgres PGDATABASE=<labdb>

mkdir -p $HOME/pg-<name>/sock
$BIN/initdb -D $HOME/pg-<name>/pgdata -U postgres
$BIN/pg_ctl -D $HOME/pg-<name>/pgdata -l $HOME/pg-<name>/server.log -o '-h ""' -o "-k $HOME/pg-<name>/sock" start
$BIN/createdb <labdb>
$BIN/psql
```

- **The first two lines go in every terminal.** The rest runs once.
- **Restart:** the same `pg_ctl` line, with `restart` instead of `start`. A restart empties shared buffers.
- **Clean-up:**
  ```bash
  $BIN/pg_ctl -D $HOME/pg-<name>/pgdata -m fast stop
  rm -rf $HOME/pg-<name>
  ```
- **Folder and database names used so far:**
  - `pg-memlab` / `memlab` (part 1)
  - `pg-exercise` / `proclab` (part 2)
  - `pg-storelab` / `storelab` (part 3)
- **Keep the data directory under `$HOME`, never `/tmp`.** `/tmp` lives in RAM on this machine, so a "cold read" there would be a memory read.
- **What the start flags mean:** `-h ""` stops the server listening on the network, so nothing else can reach it or clash with it. `-k` sets the folder for the connection file.
- **The `trust` warning from `initdb` is fine.** It means no passwords, which is acceptable on a private test server.
- **Never suggest `pkill -f postgres`:** it kills the shell. To check a server stopped, use `pg_ctl status -D …`, not `pgrep`, which also matches the canery container's postgres.

## The data load

Copy the tables from the post's lab runner exactly as written. That means the same:
- column order,
- `fillfactor`,
- `generate_series` formulas,
- index creation,
- final `vacuum analyze`.

That copy is what gives `customers` 710 pages and `orders` 7,693 pages, and puts row 4242 at `(32,82)`. Load only the tables the exercises need, plus a scratch copy for anything destructive. Turn autovacuum off on that copy.

## Known traps, by post

### Part 1, memory layer
- **`shared_buffers` needs a restart.** Change it with `ALTER SYSTEM` plus a restart, and set it back the same way afterwards.
- **Turn parallel query off** (`set max_parallel_workers_per_gather = 0`) when counting one scan's ring buffers or one sort's `work_mem`.
- **`pg_buffercache` counts need `relforknumber = 0`.** Without it, the free space map and visibility map pages are counted too.
- **Exercise 2 (checkpoint between two updates).** The post's answer says both updates carry a full-page image. That is only true if a checkpoint happened after the page's previous change. Timed checkpoints come every 5 minutes. Run straight after the worked example, the expected result is first small, second large. **Not yet confirmed.**

### Part 2, process layer
- **Autovacuum got there first.** It vacuumed a copy with 500,000 dead rows about 50 seconds after the delete, so the reader's `VACUUM` then showed `index scans: 0`. Fix: `alter table … set (autovacuum_enabled = off)` on the scratch copy.
- **Query 9 checks the wrong table.** The Implementation section's Query 9 filters on `orders`, but the exercise uses a copy, so it returns 0.
- **`n_dead_tup` lags about 1 second** after a delete.
- **Exercise 2 (held snapshot).** The `REPEATABLE READ` session must run its `select` before the other window's delete.
- **Exercise 3 (worker pool) can't be done as written.** Session A gets only 2 workers, because of the table-size rule, and finishes in about 25 ms.
  - Fix: set the table's `parallel_workers = 4` first, and use a deliberately slow query, for example a `pg_sleep(0.0001)` filter. `pg_sleep` is parallel safe.
  - The logical replication launcher holds one of the 8 `max_worker_processes` slots. So while A holds 4 workers, B should get 3, and the limit hit is `max_worker_processes`, not the `max_parallel_workers` the post names. **Not yet confirmed.**

### Part 3, storage layer
- **Exercise 3 needs the worked example replayed first,** in this order, with nothing else touching `orders`:
  1. update the row to `shipped`,
  2. a reading sequential scan,
  3. update it to `refunded`,
  4. `vacuum`,
  5. `vacuum (index_cleanup on)`.

  Test the exercise's update inside `begin … rollback`.
- **`pg_column_size` doesn't show the 18-byte TOAST pointer.** For a value moved out of line, it reports the value's stored size. Use `heap_page_items(get_raw_page(…)).lp_len` to see the row's real length.
- **Counts inside an open transaction:** `pg_stat_xact_user_tables` shows them; `pg_stat_user_tables` doesn't until the transaction ends.
- **Exercise 1 works on any server.** `pg_walfile_name_offset` needs only the LSN. Have them repeat it on their own server's `pg_current_wal_lsn()` and find the file in `pg_wal`.

## psql things to teach once
- `;` ends a statement, and you can paste several lines at once.
- `\q` quits; `\dt` lists tables; `\d <table>` describes one.
- `\gset` saves a query's result as a variable, used later as `:'var'` (quoted) or `:var` (bare).
- `explain (analyze, buffers, costs off, timing off)` runs the query and keeps the output short.
- Ctrl+C cancels the running query.
- `select x'D69D50'::int;` converts hex to decimal.
