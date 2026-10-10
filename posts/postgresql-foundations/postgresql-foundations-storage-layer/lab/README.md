# Lab — How PostgreSQL Stores Data

`run_lab.py` produces every server-side number quoted in the article. It writes two files next
to itself: `captures.md`, with the psql output of every step verbatim and in run order, and
`captures.json`, with the numbers the figures are drawn from. The committed captures come from
PostgreSQL 16.2 with the default `postgresql.conf`, on 16 CPUs, 15 GB RAM, a Samsung NVMe disk
and Linux 7.0, run 2026-09-24.

It is the same lab as parts 1 and 2 of the series, [How PostgreSQL Uses
Memory](https://canery.in/blogs/postgresql-foundations-memory-layer) and [How PostgreSQL Uses
Processes](https://canery.in/blogs/postgresql-foundations-process-layer). It builds the same two
tables, `customers` at 710 pages and `orders` at 7,693 pages, with part 2's two indexes on
`orders`, in a fresh database called `storelab`. It then follows one row, `id = 4242`, from its
first byte to crash recovery.

## What you need

- PostgreSQL 16.x server binaries you can start yourself. The captures used the `pgserver` wheel
  (`pip install pgserver`), which bundles 16.2 under `site-packages/pgserver/pginstall/`.
- The contrib modules `pageinspect`, `pg_visibility`, `pg_freespacemap`, `pg_walinspect` and
  `pg_buffercache`, installed for that server. The wheel does not ship them. Fetch
  `contrib/<module>/` from the 16.2 source release and run
  `make USE_PGXS=1 PG_CONFIG=<pginstall>/bin/pg_config install` in each.
- Python 3 with `psycopg` 3, and `ps` from procps.
- A data directory on a real disk, not tmpfs. Step 11 compares a page in memory with the same
  page read from its file.
- A clean `postgresql.auto.conf`. The script refuses to start if it finds `archive_mode` there.

## Run

```bash
initdb -D /path/pgdata -U postgres
pg_ctl -D /path/pgdata -w -o '-h ""' -o '-k /path/sock' -l /path/pgdata/server.log start
PGBIN=/path/to/bin PGDATA=/path/pgdata PGSOCK=/path/sock python3 run_lab.py
```

It takes about a minute, most of it loading two copies of `orders` and restarting the server
three times.

> [!WARNING]
> Three steps change the server and put it back. **Step 11 stops the server with
> `pg_ctl stop -m immediate`**, a simulated crash, then restarts it into crash recovery. Step 12
> turns on WAL archiving with `ALTER SYSTEM`, restarts, and then resets both settings and restarts
> again. Step 13 attaches `pg_receivewal` for three seconds. Point this at a throwaway cluster,
> never at anything you care about.

## What each step captures

| Step | Produces |
|---|---|
| 0 | the storage settings, and a checkpoint before the load so the first updates carry no full-page image |
| 1 | the tables, their files and forks, and their sizes on disk |
| 2 | row 4242's ctid, its page header and line pointer decoded from raw bytes, its tuple decoded byte by byte, rows per page, and the same rows with a better column order |
| 3 | update 1 (not HOT): the old and new versions, the WAL it wrote, a reader pruning the old version, hint bits being set |
| 4 | update 2 (HOT): the chain on page 7692, its WAL, the record read by LSN from its segment file with its CRC recomputed, `pg_waldump`, and the segment's header |
| 5 | two vacuums, with the visibility map and free space map before and after each |
| 6 | the four free space map pages, as the tree stored in each |
| 7 | TOAST: where the thresholds fall for compressible and incompressible text, and chunk counts |
| 8 | row 4242 given a 10,000-byte note: its chunks, its 18-byte pointer decoded, the WAL |
| 9 | the B-tree lookup of the row's customer, page by page, and the tree's shape |
| 10 | one leaf split at the right edge and one in the middle, with their WAL |
| 11 | a checkpoint, an update, a crash, and the replay, with the page compared in memory and on disk |
| 12 | WAL archiving turned on, one segment archived, and archiving turned off again |
| 13 | a walsender forked for `pg_receivewal` |
| 14 | an index-only scan before and after the visibility map is cleared, and after vacuum |

## What changes on 17 and 18

The formats are the same. Transaction ids, LSNs and file numbers will differ from the captures,
and nothing else should. On 18, `initdb` enables data checksums by default, so the page header's
checksum field will be non-zero. The `checkpoints_so_far()` helper reads
`pg_stat_bgwriter`'s checkpoint counters, which moved to `pg_stat_checkpointer` in 17 under new
names; that one function needs the edit.

## Cleanup

```bash
psql -h /path/sock -U postgres -d postgres -c 'drop database storelab'
```

The script removes its archive directory and resets `postgresql.auto.conf` itself. Check that
`postgresql.auto.conf` holds no settings afterwards.
