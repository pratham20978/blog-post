# Lab — What a Relational Database Actually Does

- **Grade:** G2 · local service (a PostgreSQL server you start yourself)
- **Executed:** yes · 2026-10-01 · the build machine
- **Provenance:** Ubuntu 26.04.1 LTS, Linux 7.0.0-31-generic x86_64, 16 CPUs, 14 GB RAM, data directory on an NVMe disk (never tmpfs). PostgreSQL 18.6 built from the official source release (sha256 `555610c2…81d9f`), `initdb --encoding=UTF8 --locale=C.UTF-8`, default `postgresql.conf` — the only non-default settings are the connection ones the start command passes, `listen_addresses = ''` and `unix_socket_directories = <sock>`. Python 3.14.4, no third-party packages.

`run_lab.py` produces every server-side number quoted in the article. It asks one business
question of the series' two tables — revenue per country for paid orders — follows it through the
four stages the server puts it through, and then breaks the answer twice. It writes two files next
to itself: `captures.md`, with the psql output of every step verbatim and in run order, and
`captures.json`, with the numbers the article and the figures are drawn from. Nothing in the
article is modelled or estimated; every figure in it came from this run.

The tables are the ones the series has used since part 1 — `customers` at 710 pages and `orders`
at 7,693 pages — created by `shopgen.py` from the DDL parts 1–3 used, byte for byte. Parts 1–3
captured them on PostgreSQL 16.2; this lab is the first on 18.6, and both page counts came out
identical.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `shopgen.py` | G2 | yes | builds the database and loads the two tables; shared with later parts |
| `run_lab.py` | G2 | yes | the entry point: every number in the article |
| `check.py` | G2 | yes | marks your own run, one rung at a time |
| `captures.md` | — | — | the run the article quotes, verbatim, to compare with yours |
| `captures.json` | — | — | the same run as numbers, which `check.py` marks you against |

## What you need

| | |
|---|---|
| Hardware | any laptop; about 400 MB of disk for the data directory |
| Software | PostgreSQL 16, 17 or 18 server binaries you can start yourself, and Python 3.9+. No third-party Python packages. The captures are from 18.6; see *What to expect* for what differs on 16 and 17. |
| Privileges | none: no root, no Docker, no service manager, nothing outside your own data directory |
| Disk, network, time | no network after the server is installed; the whole run takes about 20 seconds, most of it loading 1,000,000 orders |

## Run

```bash
initdb -D /path/pgdata -U postgres --encoding=UTF8 --locale=C.UTF-8
pg_ctl -D /path/pgdata -o "-k /path/sock -h ''" -l /path/server.log -w start

export PGBIN=/path/to/postgres/bin PGSOCK=/path/sock
python3 run_lab.py
```

`run_lab.py` calls `shopgen.py` for you and drops any existing `shoplab` database first. To load
the data once and keep it, run `shopgen.py` yourself and pass `--keep`.

> [!WARNING]
> This lab inserts a duplicate row, drops a `NOT NULL` constraint and adds a primary key to
> `orders`, and leaves the database changed. The exercises start from fresh data, so run
> `shopgen.py --scale M --db shoplab --drop` before E1. It never contacts a server it was not handed a socket for, and `shopgen.py`
> refuses a database it did not create unless you pass `--drop`. Point it at a throwaway cluster,
> never at anything you care about.

## What to expect

A correct run prints the six step headings and writes the two capture files. The values that must
match exactly on any machine:

| Value | This run |
|---|---|
| `customers` / `orders` pages | 710 / 7,693 |
| paid orders | 333,333 |
| total paid revenue | 16,666,533,321 cents |
| revenue after the duplicate | 16,666,590,275 cents (+56,954, the duplicated order's own amount) |
| `count(*)` vs `count(amount_cents)` after one NULL | 1,000,000 vs 999,999 |

Costs and timings will differ. The plan's shape should not: a hash join under a partial aggregate
under a gather, on any machine with at least three usable CPUs. Across three runs on this
machine the total cost read 18,258.22, 18,251.19 and 18,285.79, because `ANALYZE` samples the
table, so treat cost figures as accurate to about 0.2% rather than exact.

**On PostgreSQL 16 and 17** three things in the captures look different, and none of them changes
what the lab teaches:

- `EXPLAIN ANALYZE` prints no `Buffers` lines unless you ask: `EXPLAIN (ANALYZE, BUFFERS)`.
  PostgreSQL 18 includes them by default.
- Actual row counts print as whole numbers (`rows=5`), not with two decimal places (`rows=5.00`).
- `pg_constraint` has no rows for `NOT NULL` constraints. They became full catalog entries in 18.

## Exercises

Do them in order. Each has a self-check `check.py` will mark for you, and the answer is hidden
below it. This is an L2 post, so the lab ships E1 to E3; E4 is here because this topic has an
unusually good fault to diagnose.

### E1 — Reproduce: the revenue table

`run_lab.py` leaves the data changed, so load fresh data first:
`python3 shopgen.py --scale M --db shoplab --drop`. Then run `python3 check.py e1`. It compares your
five rows with the author's, to the cent.

**Self-check:** all three checks pass; five countries in the same order, every revenue figure
identical.

<details><summary>Answer</summary>

DE 3,333,366,716 · IN 3,333,366,679 · JP 3,333,366,679 · BR 3,333,266,642 · US 3,333,166,605,
and 333,333 paid orders in total. A mismatch almost always means `shopgen` ran at a scale other
than `M`, or that a later exercise has already changed the data. `shopgen.py --scale M --db
shoplab --drop` puts it back.

</details>

### E2 — Inspect: what the executor actually read

The article shows the plan but does not print every `Buffers` line in it. Find the one on the
scan of `orders`, with the tool the article taught, and compare it with `relpages` in `pg_class`.

**Self-check:** the two numbers are equal, and `check.py e2` passes both checks.

<details><summary>Answer</summary>

7,693 buffers, 7,693 pages: the scan read the table exactly once, one buffer per page, and no
page twice. `relpages` is the planner's estimate and the buffer count is what the executor did,
so this is the estimate and the reality agreeing — which they do not always do, and part 14 is
about when they do not. On 16 and 17, ask for `EXPLAIN (ANALYZE, BUFFERS)`.

</details>

### E3 — Predict: what one NULL does to two counts

Write down, before running anything: what will `count(*)` and `count(amount_cents)` return after
one order's amount is set to NULL, and will `sum(amount_cents)` change? Then run

```sql
alter table orders alter column amount_cents drop not null;
update orders set amount_cents = null where id = 4242;
```

and mark yourself with `python3 check.py e3`.

**Self-check:** both numbers right, and the reason right: a right number for the wrong reason
fails this rung.

<details><summary>Answer</summary>

1,000,000 and 999,999. `count(*)` counts rows; `count(amount_cents)` counts rows where that
column is not null, so it is one lower. `sum` drops by that order's 56,954 cents, because every
aggregate except `count(*)` skips nulls rather than returning null. And the row you changed
cannot be found with `where amount_cents = null`, which matches nothing: the comparison is
unknown, not true, and `WHERE` keeps only what is true. `is null` is the operator for the
question.

</details>

### E4 — Diagnose: revenue moved overnight

Start from fresh data again: E3 left one amount null, which would hide the fault.

```bash
python3 shopgen.py --scale M --db shoplab --drop
python3 check.py e4 --break
```

That injects one fault. Revenue for one country is now wrong. Find which country, by how much,
and why; then make the server refuse the cause, and mark your fix with
`python3 check.py e4 --verify`.

**Self-check:** symptom (which country, how much), cause, the one observation that proves it, and
a fix the server enforces. All three checks must pass — the third one does not pass if you only
repaired the data.

<details><summary>Answer</summary>

**Symptom:** JP revenue rose by 56,954 cents, from 3,333,366,679 to 3,333,423,633, and its paid
order count rose by one. **Cause:** `orders` has no primary key, so an identical copy of order
4242 was accepted. **The observation that proves it:**
`select count(*) from orders where id = 4242` returns 2. **The fix:** delete the extra copy, then
`alter table orders add primary key (id)`. The constraint cannot be added while the duplicate is
still there, which is the usual order of events in a real system. Deleting the row alone passes
the first two checks and fails the third, on purpose: that repairs this incident and prevents
nothing.

</details>

## Safety and cleanup

- The lab talks only to the server whose socket you pass in `PGSOCK`. It never contacts the
  shared series lab server, any live service, or object storage, and it writes nothing outside
  its own folder and the data directory you created.
- It writes `captures.md` and `captures.json` next to itself, overwriting them each run.

```bash
pg_ctl -D /path/pgdata -m fast stop
rm -rf /path/pgdata /path/sock
```
