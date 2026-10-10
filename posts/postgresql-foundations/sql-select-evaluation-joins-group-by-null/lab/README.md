# Lab — How a SELECT Is Evaluated: Joins, Grouping and NULL

- **Grade:** G2 · local service (a PostgreSQL server you start yourself)
- **Executed:** yes · 2026-10-02 · the build machine
- **Provenance:** Ubuntu 26.04.1 LTS, Linux 7.0.0-31-generic x86_64, 16 CPUs, 14 GB RAM, data directory on an NVMe disk (never tmpfs). PostgreSQL 18.6 built from the official source release, `initdb --encoding=UTF8 --locale=C.UTF-8`, default `postgresql.conf` — the only non-default settings are the connection ones the start command passes, `listen_addresses = ''` and `unix_socket_directories = <sock>`, plus the session-level `SET`s that `run_lab.py` prints beside the queries they change. Python 3.14.4, no third-party packages. The cluster was temporary and was deleted after the capture.

`run_lab.py` produces every server-side number quoted in the article. It builds one report — paid
revenue per country, top two — one clause at a time, and counts the rows after each clause twice:
on the 20-row sample in `sample.sql`, where every count is compared with the count worked by hand
in the article (the script stops if one disagrees), and on the full shop. Then it walks the traps
the clauses set: the outer join a WHERE undoes, WHERE against HAVING, NULL as a group and as a
sort key, the duplicates a join adds and EXISTS does not, UNION against UNION ALL, and NOT IN
against NOT EXISTS once one NULL appears. It writes `captures.md`, every statement and its psql
output verbatim, and `captures.json`, the numbers the article and its figures are drawn from.

The full shop is the series' two tables, built by `shopgen.py` at scale M (100,000 customers,
1,000,000 orders) with `--orderless 1000`: 1,000 more customers who have never ordered. Without
them every customer has exactly 10 orders, and a LEFT JOIN would have nothing to add.

## Files

| File | Grade | Executed | What it is |
|---|---|---|---|
| `README.md` | — | — | this file: grade, setup, run order, exercises, cleanup |
| `shopgen.py` | G2 | yes | builds the database and loads the two tables; part 5 added `--orderless` |
| `sample.sql` | G2 | yes | the 20-row sample: 6 customers and 14 orders, built by hand |
| `run_lab.py` | G2 | yes | the entry point: every number in the article |
| `check.py` | G2 | yes | marks your own run, one rung at a time |
| `broken.sql` | G2 | yes | three queries that run and return wrong answers, for exercise E4 |
| `captures.md` | — | — | the run the article quotes, verbatim, to compare with yours |
| `captures.json` | — | — | the same run as numbers, which `check.py` marks you against |

## What you need

| | |
|---|---|
| Hardware | any laptop; about 300 MB of disk for the data directory |
| Software | PostgreSQL 16, 17 or 18 server binaries you can start yourself, and Python 3.9+. No third-party Python packages. The captures are from 18.6; see *What to expect* for what differs on 16 and 17. |
| Privileges | none: no root, no Docker, no service manager, nothing outside your own data directory |
| Disk, network, time | no network once the server is installed. The whole run takes about four and a half minutes, and almost all of it is two NOT IN queries; that is section 8's lesson, not a fault |

## Run

```bash
initdb -D /path/pgdata -U postgres --encoding=UTF8 --locale=C.UTF-8
pg_ctl -D /path/pgdata -o "-k /path/sock -h ''" -l /path/server.log -w start

export PGBIN=/path/to/postgres/bin PGSOCK=/path/sock
python3 run_lab.py
```

`run_lab.py` calls `shopgen.py` for you and replaces any `shoplab` database that `shopgen`
created; it builds the sample in its own database, `shopsample`. Pass `--keep` to reuse an
existing `shoplab`.

> [!WARNING]
> This lab drops the `NOT NULL` rule on `orders.customer_id` and sets one order's customer to
> NULL, and leaves both databases changed. The exercises start from fresh data, so run
> `shopgen.py --scale M --orderless 1000 --db shoplab --drop` before each one. It never contacts
> a server it was not handed a socket for, and `shopgen.py` refuses a database it did not create
> unless you pass `--drop`. Point it at a throwaway cluster, never at anything you care about.

## What to expect

A correct run prints nine section headings and writes the two capture files. These values must
match exactly on any machine:

| Value | This run |
|---|---|
| customers / orders | 101,000 / 1,000,000 (717 and 7,693 pages) |
| rows after FROM … JOIN, WHERE paid, GROUP BY country | 1,000,000 → 333,333 → 5 |
| LEFT JOIN; with WHERE on orders; with the condition in ON | 1,001,000; 333,333; 334,333 |
| customers with a paid order: JOIN, EXISTS | 333,333 rows; 100,000 |
| UNION ALL; UNION of paid and refunded customer ids | 666,666; 100,000 |
| customers with no order, by NOT IN and NOT EXISTS | 1,000 and 1,000; after one NULL, 0 and 1,000 |
| R minus S for R = {1, NULL}, S = {NULL} | NOT IN: none; NOT EXISTS: 1 and NULL; EXCEPT: 1 |

Timings will differ: on the build machine the NOT IN queries took about 118 seconds each and NOT
EXISTS about 50 ms. Which country comes second in `LIMIT 2` may differ too. IN and JP tie, so
either answer is correct, and the run records the second row under five planner settings to
show it changing.

**On PostgreSQL 16 and 17** every row count is the same. The plans' text can differ, and on 16
the NOT IN filter is printed in an older form, because EXPLAIN's display of subplans changed in
17. `FETCH FIRST … WITH TIES` needs 13 or later.

## Exercises

Do them in order. Each has a self-check `check.py` marks for you, with the answer hidden below it.
This is an L3 post, so the lab ships E1 to E4. Start each one from fresh data:

```bash
python3 shopgen.py --scale M --orderless 1000 --db shoplab --drop
```

### E1 — Reproduce: the report, clause by clause

Run `python3 check.py e1`. It counts the rows after FROM, the join, WHERE and GROUP BY, and
compares the five paid-revenue rows with the article's, to the cent.

**Self-check:** all seven checks pass, and the provenance of your server is the one you started.

<details><summary>Answer</summary>

101,000 customers; 1,000,000 rows after the join (1,001,000 with a LEFT JOIN); 333,333 paid; 5
groups. DE 66,667 orders and 3,333,366,716 cents, IN 66,667 and 3,333,366,679, JP 66,666 and
3,333,366,679, BR 66,667 and 3,333,266,642, US 66,666 and 3,333,166,605. A mismatch almost always
means `shopgen` ran without `--orderless 1000`, or that an earlier exercise changed the data.

</details>

### E2 — Inspect: where did PostgreSQL apply the HAVING condition?

The article says a HAVING condition that uses no aggregate is applied before grouping, as if it
were in WHERE. Check it with the tool the article taught:

```sql
explain (costs off)
select c.country, o.status, count(*)
from customers c join orders o on o.customer_id = c.id
group by c.country, o.status
having o.status = 'paid';
```

Find the line `Filter: (status = 'paid'::text)` and the node it sits under. Then run
`python3 check.py e2`.

**Self-check:** the filter sits on the scan of `orders`, no aggregate node carries it, and the
plan is identical to the WHERE version's.

<details><summary>Answer</summary>

It sits under `Parallel Seq Scan on orders o`, at the bottom of the plan, and the plan is the same
line for line as the one for `where o.status = 'paid'`. The group key even shrinks to
`c.country` alone, because the filter fixes the status. The planner moved the condition into
WHERE so that 333,333 rows are grouped instead of 1,000,000; the answer is the same either way,
which is why it is allowed to.

</details>

### E3 — Predict: which queries change when one order loses its customer?

`python3 check.py e3` prints six queries. Before you run anything else, write down which of them
will return a different number after these two statements:

```sql
alter table orders alter column customer_id drop not null;
update orders set customer_id = null where id = 4242;
```

Then run `python3 check.py e3 --predict <numbers>`, for example `--predict 2,5`. It runs the six,
makes the change, runs them again and marks your prediction.

**Self-check:** you named exactly the queries that changed, and for each one you can say why.
A right set for the wrong reason fails this rung.

<details><summary>Answer</summary>

1, 3 and 6 change. **1**, the join count, falls from 1,000,000 to 999,999: a NULL equals nothing,
so that order joins no customer. **3**, NOT IN, falls from 1,000 to 0: for a customer with no
orders, `id NOT IN (…)` is a chain of `<>` tests joined by AND, and `id <> NULL` is unknown, so
the whole test is unknown and WHERE drops the row. **6**, the number of groups, rises from 100,000
to 100,001: GROUP BY puts the NULL in a group of its own. **2** (IN) stays at 100,000, **4** (NOT
EXISTS) at 1,000, and **5**, `count(DISTINCT customer_id)`, at 100,000, because the order's old
customer still has nine other orders and count skips the NULL.

</details>

### E4 — Diagnose: three queries that run and lie

```bash
python3 shopgen.py --scale M --orderless 1000 --db shoplab --drop
python3 check.py e4 --break
cp broken.sql fixed.sql
```

`--break` sets one order's customer to NULL, as happens in real data. `broken.sql` holds three
queries that run without an error and return a wrong answer. For each one, find the symptom, the
cause and the one observation that proves it; repair it in `fixed.sql`, keeping the three marker
lines, and mark your repairs with `python3 check.py e4 --verify`.

**Self-check:** all three repaired queries return the author's answers, and for each you can name
the symptom, the cause, and the observation that proves it.

<details><summary>Answer</summary>

**A.** *Symptom:* paid and refunded revenue are each about 3.3 times too large, and equal to each
other. *Cause:* two joins to `orders` multiply: a customer with 3 paid and 4 refunded orders
produces 12 rows, so each paid amount is added 4 times. *Proof:* count the rows the two joins
produce before grouping: about 1,100,000, more than there are orders (1,099,998 exactly on fresh
data). *Fix:* one join and two filtered sums,
`sum(o.amount_cents) filter (where o.status = 'paid')` and the same for `'refunded'`. (The two
broken columns come out equal because shopgen gives all 10 orders of a customer the same amount.)

**B.** *Symptom:* 0 customers have never ordered. *Cause:* `NOT IN` over a column that now holds a
NULL is never true. *Proof:* `select count(*) from orders where customer_id is null` returns 1,
and `100001 not in (1, 2, null)` is NULL. *Fix:* `NOT EXISTS (select 1 from orders o where
o.customer_id = c.id)`, which returns 1,000. Filtering the NULL out of the subquery also works,
but the next nullable column brings the bug back.

**C.** *Symptom:* every country received 200,000 big orders, which is every order it has.
*Cause:* the condition was meant for rows but was written for groups. The first draft,
`having o.amount_cents >= 90000`, was rightly rejected; wrapping the column in `max()` silenced
the error and changed the question to "countries that have at least one big order", and the
count still counts all of them. *Proof:* `count(*)` equals the country's whole order count.
*Fix:* move the condition to `where o.amount_cents >= 90000`: 20,000 per country.

</details>

## Safety and cleanup

- The lab talks only to the server whose socket you pass in `PGSOCK`. It never contacts the shared
  series lab server, a live service or object storage, and it writes nothing outside its own
  folder and the data directory you created.
- It writes `captures.md` and `captures.json` next to itself, overwriting them each run.

```bash
pg_ctl -D /path/pgdata -m fast stop
rm -rf /path/pgdata /path/sock
```
