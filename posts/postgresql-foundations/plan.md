# Series plan — PostgreSQL Foundations
**Slug:** postgresql-foundations · **Shape:** hybrid · **Parts:** 46 (1 published, 2 drafted, 43 planned) · **Status:** Checkpoint S — awaiting approval (planned 2026-09-29)
**Display title (platform only, key unchanged):** *PostgreSQL Foundations: From First Query to Production at Scale*
## Why this is a series and not one post

The owner's brief (2026-09-28/29) is to train a reader into an industry-grade PostgreSQL and
database engineer: from a first query to an automated, monitored, replicated, sharded fleet, plus
PostgreSQL as a data platform (documents, text, vectors, time series, geo, change streams, the
lake). A curriculum map of 45 capability areas put 29 of them on PostgreSQL. Budgeted at the
tier table, that is about 43 new parts at L2–L4, roughly 360,000 words: nothing like one post.

The seams are prerequisite seams. Nobody can read a plan before they can write the query; nobody
can reason about failover before they know what a standby replays; nobody can tune vacuum before
they know what the horizon is. Each part below names **at most one** earlier part it truly depends
on, and every dependency points to a lower position, so publishing in position order never links
forward.

## Shape

**Hybrid.** Parts 1–3 stay a decomposition (three sibling layers at L4, intermediate), now the
*Internals* arc that most later parts link into by anchor. Parts 4 → 5 → 6 are a short ladder,
the from-scratch SQL on-ramp, beginner to intermediate, each rung assuming the one before. Every
part from 7 on is a spoke cut at a prerequisite seam, ordered the way an engineer meets the
problems on the job: first schema, going live, first slow query, first concurrency bug, first
outage, growth, new workloads, fleet. Spokes **assume** the part they name and link back to it;
only the ladder rungs re-teach, in three sentences at most. Practice spokes (20, 25, 26, 31) sit
at intermediate after advanced neighbours on purpose: they are not ladder rungs.

## Where this series stops, and the two sibling series

Hadoop is **not** part of PostgreSQL: it shares no code, storage format or process with it, and the
two meet only through connectors. So the curriculum is a spine plus two siblings:

- **This series** owns every area where a real PostgreSQL server is the thing being operated,
  changed or measured — including PostgreSQL's end of every integration (publications, slots,
  decoding plugins, FDWs, COPY to Parquet, pgvector).
- **`data-at-scale`** (planned, `posts/data-at-scale/plan.md`) owns what happens once the data has
  left PostgreSQL: HDFS, MapReduce, YARN, Spark, Parquet internals, Iceberg/Delta/Hudi, Trino,
  Kafka, Flink, dbt, Airflow, warehouse vs lakehouse.
- **`database-engines`** (planned, `posts/database-engines/plan.md`) owns other engine designs set
  against this series' baseline: SQLite, InnoDB, LSM trees, Redis, MongoDB, Lucene, vector
  databases, ClickHouse, DuckDB, Prometheus, graph, Cassandra, Raft, distributed SQL.

Bridges: Part 39 (CDC) hands the change stream to *data-at-scale* Part 17; Part 41 (the lake)
hands Iceberg to *data-at-scale* Part 11; Part 40 (analytics) is the baseline for
*database-engines* Parts 11–12; Part 36 (pgvector) for *database-engines* Part 10; Parts 22–23
(replication, failover) for *database-engines* Parts 15 and 17.

## Arcs

| Parts | Arc | Purpose |
|---|---|---|
| 1–3 | Internals: the three layers | What is in RAM, which process does the work, and what is on disk. Fixed, existing parts; most later parts link into them by anchor. |
| 4–10 | Day 0: from zero to a first schema | The from-scratch on-ramp: the relational model, SQL, schema and physical design, loading data, and logic inside the database, all on the shop tables. |
| 11–12 | Day 1: going live | Connections, pooling, prepared statements, authentication, privileges and tenancy. |
| 13–17 | The first slow query | Find the slow query, read its plan, understand estimates and the executor, choose the index that fixes it. |
| 18–20 | The first concurrency bug | Anomalies, locks, and changing a live schema without taking the site down. |
| 21–27 | Staying up | Backup and PITR, replication, failover, logical decoding, upgrades, migrating in from another engine, corruption. |
| 28–32 | Growth | Observe, keep vacuum ahead, partition, find the ceiling, tune from evidence. |
| 33–41 | PostgreSQL as a data platform | Extensions and the workloads they enable: documents, text, vectors, geo, time series, change streams, analytics, the lake. |
| 42–46 | The fleet: scale out and automate | Sharding, managed services, infrastructure as code, Kubernetes operators, and incident response encoded as runbooks. |

## Reading paths

Positions are publication order. Readers enter by path, and the series index shows these paths:

- **From zero (beginner):** 4 → 5 → 6 → 7 → 8 → 9 → 13 → 16 → 18, then 1 → 2 → 3.
- **Application developer:** 4 → 5 → 7 → 11 → 13 → 16 → 18 → 19 → 20 → 34 → 36.
- **DBA / operator:** 1 → 2 → 3 → 21 → 22 → 23 → 28 → 29 → 25 → 32 → 44 → 45 → 46.
- **Performance:** 1 → 13 → 14 → 15 → 16 → 17 → 30 → 31 → 32.
- **Data platform:** 3 → 17 → 34 → 35 → 36 → 38 → 39 → 40 → 41, then *data-at-scale*.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | name PostgreSQL's three memory pools and the kernel page cache it cannot see | 1 |
| 2 | predict whether a page survives in shared buffers from its usage count and the clock sweep | 1 |
| 3 | explain why a big sequential scan leaves only a 256 KB ring behind, and check it in `pg_stat_io` | 1 |
| 4 | say why no dirty page may leave memory before its WAL, and what a full-page image costs | 1 |
| 5 | budget `work_mem` per operation, per process, per parallel worker | 1 |
| 6 | explain why one killed backend restarts the whole server, and why that is the design | 2 |
| 7 | price a connection, and say why only the postmaster forks | 2 |
| 8 | say what the checkpointer, background writer and WAL writer each owe the others | 2 |
| 9 | predict when autovacuum will arrive and how many index passes it will make | 2 |
| 10 | choose `synchronous_commit` from what a commit actually waits for | 2 |
| 11 | read a heap page byte by byte: header, line pointers, tuple headers, `pd_lsn` | 3 |
| 12 | say from `xmin`, `xmax` and the infomask bits whether a row version is visible | 3 |
| 13 | say when an `UPDATE` is HOT, and what it saves the indexes | 3 |
| 14 | explain what the visibility map lets vacuum and index-only scans skip | 3 |
| 15 | say what the free space map records and why an insert lands where it does | 3 |
| 16 | predict when a value is compressed, moved out of line, or both (TOAST) | 3 |
| 17 | walk a B-tree lookup through its pages, and say what a page split does | 3 |
| 18 | name a WAL segment from an LSN, and trace crash recovery replaying it onto a page | 3 |
| 19 | say what a relation, a key and NULL are, and follow one query from text to rows | 4 |
| 20 | read the system-catalog rows that describe a table | 4 |
| 21 | evaluate a SELECT clause by clause and predict its row count | 5 |
| 22 | avoid the NULL and join fan-out traps (NOT IN with NULL, duplicated joins) | 5 |
| 23 | write running totals, rankings, top-N-per-group and gaps-and-islands queries | 6 |
| 24 | walk a hierarchy with WITH RECURSIVE and detect cycles | 6 |
| 25 | normalize a schema and name the anomaly each normal form prevents | 7 |
| 26 | enforce business rules with PK, FK, UNIQUE, CHECK, EXCLUDE and temporal constraints | 7 |
| 27 | price a data-type or key choice in bytes, index pages and WAL | 8 |
| 28 | choose between bigint, uuidv4 and uuidv7 keys from measured split and WAL cost | 8 |
| 29 | load millions of rows at the fastest correct rate and explain the WAL behind each method | 9 |
| 30 | merge incoming data race-free with ON CONFLICT or MERGE | 9 |
| 31 | decide which logic belongs in functions, procedures or triggers, and price it per row | 10 |
| 32 | set function volatility correctly and say what it changes | 10 |
| 33 | size a connection pool from Little's law and choose a PgBouncer mode | 11 |
| 34 | diagnose a generic-plan regression and fix it with plan_cache_mode | 11 |
| 35 | configure authentication, TLS, roles and default privileges for least privilege | 12 |
| 36 | build, then attack, a multi-tenant row-level-security design | 12 |
| 37 | find the worst query with pg_stat_statements and read its EXPLAIN (ANALYZE, BUFFERS) node by node | 13 |
| 38 | apply and measure the six most common query rewrites | 13 |
| 39 | compute a selectivity and a plan cost by hand and match them to EXPLAIN | 14 |
| 40 | fix correlated-column misestimates with extended statistics | 14 |
| 41 | predict which join algorithm wins for given input sizes and memory | 15 |
| 42 | explain spills, Memoize and parallel plans from EXPLAIN output | 15 |
| 43 | design composite, partial, covering and expression indexes and prove each earns its write cost | 16 |
| 44 | choose among GIN, GiST, SP-GiST, BRIN, hash and bloom for a query shape, and say what each stores | 17 |
| 45 | name the anomalies each isolation level allows in PostgreSQL and reproduce them | 18 |
| 46 | write retry loops that make Serializable safe to use | 18 |
| 47 | read pg_locks and the wait graph, and prevent lock-queue outages with lock_timeout | 19 |
| 48 | build a SKIP LOCKED job queue and resolve deadlocks | 19 |
| 49 | run any common schema change under traffic without blocking, using expand/contract | 20 |
| 50 | lint and test migrations in CI | 20 |
| 51 | restore to any second with WAL archiving and pgBackRest, and state RPO/RTO from measurements | 21 |
| 52 | automate restore testing as a scheduled job | 21 |
| 53 | set up streaming replication and choose synchronous_commit from its measured cost | 22 |
| 54 | diagnose replica lag, slot growth and standby conflicts | 22 |
| 55 | run a Patroni cluster, explain leader election and fencing, and rejoin a failed primary with pg_rewind | 23 |
| 56 | set up filtered logical replication, read decoded changes, and resolve apply conflicts | 24 |
| 57 | upgrade a major version with pg_upgrade or a logical blue-green, with a rollback plan | 25 |
| 58 | migrate a schema and data from another engine and prove equality | 26 |
| 59 | detect and triage heap, index, WAL and collation corruption | 27 |
| 60 | find an incident from statistics views and wait events, and write alerts that page only on real trouble | 28 |
| 61 | measure bloat, find whatever holds the xmin horizon, and keep XID age safe | 29 |
| 62 | decide whether and how to partition, and verify pruning and retention | 30 |
| 63 | benchmark honestly with pgbench, locate the first ceiling, and defend a scaling decision with the numbers | 31 |
| 64 | tune memory, checkpoint, WAL and I/O settings from evidence | 32 |
| 65 | explain how extensions load and hook in, and write and test a C extension | 33 |
| 66 | decide JSONB vs columns, and index and query JSONB correctly | 34 |
| 67 | build full-text and fuzzy search with dictionaries, ranking and trigram indexes | 35 |
| 68 | tune pgvector IVFFlat/HNSW to a recall and latency target, with filters and hybrid ranking | 36 |
| 69 | store and query spatial data correctly (SRIDs, geography) and index it | 37 |
| 70 | choose a time-series layout and rollup strategy for stated ingest and retention | 38 |
| 71 | stream changes out reliably with logical decoding and the outbox pattern, and protect the primary from its slot | 39 |
| 72 | judge PostgreSQL's analytics limits and columnar options | 40 |
| 73 | federate queries with FDWs and tier cold data to Parquet/Iceberg | 41 |
| 74 | choose a distribution key, co-locate tables, and reason about distributed queries and 2PC in Citus | 42 |
| 75 | say what a managed service changes, what stays yours, and how Aurora and Neon relocate the WAL | 43 |
| 76 | manage roles and settings as code, and detect drift | 44 |
| 77 | run and fail over PostgreSQL on Kubernetes with an operator | 45 |
| 78 | triage the common incidents with one method and runbooks as code | 46 |

## Parts

*Parts 1–3 are unchanged from the approved three-part plan.*

### Part 1 — How PostgreSQL Uses Memory

- **Slug:** postgresql-foundations-memory-layer · **Status:** published 2026-09-18
- **Tier:** L4 · **Difficulty:** intermediate · **Words:** 11,525 · **Figures:** 21 + cover
- **Answers:** where does PostgreSQL keep things in RAM, and what decides what stays?
- **Assumes:** SQL and reading `EXPLAIN`; what a process and a page of memory are.
- **Hands off:** process scheduling and autovacuum to Part 2; on-disk page format beyond
  `pd_lsn`, TOAST, visibility map, indexes, WAL archiving and replay to Part 3.
- **Worked example:** cold scan of `orders` (7,693 pages) through the ring, `customers` (710 pages)
  staying cached, a forced eviction, one sort under two `work_mem` budgets, and a two-byte update
  that cost 7,544 bytes of WAL.
- **Search intent:** "postgresql shared_buffers explained", "postgresql clock sweep", "work_mem".

### Part 2 — How PostgreSQL Uses Processes

- **Slug:** postgresql-foundations-process-layer · **Status:** drafted 2026-09-19, gate PASS
- **Tier:** L4 · **Difficulty:** intermediate · **Words:** 12,131 · **Figures:** 27 + cover
- **Answers:** who does the work — which process, woken by what, and waiting on whom?
- **Assumes:** Part 1's pools, the clock sweep and the WAL-before-data rule, by anchor.
- **Hands off:** heap page format, visibility map, free space map, TOAST, index internals, WAL
  segment layout/archiving/replay, and replication processes beyond naming them — Part 3.
- **Worked example:** the price of one connection, `orders` crossing the autovacuum threshold,
  the same delete vacuumed twice (1 pass vs 5 index passes), one idle transaction holding the
  horizon, six parallel workers planned and one launched, one killed backend.
- **Search intent:** "postgresql process architecture", "how autovacuum works", "postmaster".

### Part 3 — How PostgreSQL Stores Data

- **Slug:** postgresql-foundations-storage-layer · **Status:** drafted 2026-09-24, gate PASS
- **Tier:** L4 · **Difficulty:** intermediate · **Words:** 12,146 · **Figures:** 22 + cover
- **Answers:** what is actually on disk, byte by byte, and how does a row, its index entry and its
  log record get back to a consistent state after a crash?
- **Assumes:** Part 1's buffer, page and `pd_lsn` — the "full page image" and "when a dirty page
  may leave memory" anchors. Links (does not depend) to Part 2's vacuum sections for who sets the
  visibility-map bits.
- **Owes (promised by Parts 1 and 2):** heap page layout, the visibility map and why vacuum skips
  pages, the free space map, TOAST, index internals, WAL segment layout, archiving and replay, and
  the replication processes named as readers of that segment stream.
- **Hands off:** nothing — this closes the series. Streaming-replication configuration, logical
  decoding, GIN/GiST/BRIN/hash internals, and table access methods are out of scope, named once.
- **Worked example:** one row of `orders` found by its `ctid` and read with `pageinspect` —
  page header, line pointer, tuple header — then updated twice (one HOT, one not), vacuumed
  (visibility-map bits before and after), TOASTed with a wide value, looked up through a B-tree
  index on `orders`, and finally its WAL record located by LSN in a named segment file and
  replayed after an immediate shutdown.
- **Key sources:** PostgreSQL 16 docs ch. 73 (Database Physical Storage) and ch. 30 (WAL);
  `src/include/storage/bufpage.h`, `access/htup_details.h`, `src/backend/access/nbtree/README`;
  Lehman & Yao 1981 (B-link trees); Mohan et al. 1992 (ARIES).
- **Search intent:** "postgresql page layout", "postgresql visibility map", "postgres TOAST",
  "HOT update postgresql", "WAL segment file name from LSN".
- **Scope risk:** this is the heaviest part; seven promised topics. If it budgets past ~12,000
  words, cut index internals to one B-tree walk plus one split, rather than dropping a promise.

### Part 4 — What a Relational Database Actually Does

- **Slug:** what-is-a-relational-database-postgresql · **Arc:** Day 0: from zero to a first schema · **Status:** planned
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** What is a relational database, and what happens between typing a query and getting rows back?
- **Assumes:** Nothing in the series: this is the from-scratch entry point. A terminal and a browser.
- **Hands off:** How each SELECT clause evaluates goes to Part 5, designing tables and constraints to Part 7, and how the planner costs plans to Part 14. What a buffer or a page is stays with Part 1, which is linked but not taught here.
- **Worked example:** The series' own two tables treated as relations: customers (100,000 rows) and orders (1,000,000 rows), created with the exact DDL Parts 1–3 used. One business question, revenue in cents per country for paid orders, is written as SQL, run, and followed through parse → rewrite → plan → execute with EXPLAIN ANALYZE. The tables' own rows in the system catalog (pg_class, pg_attribute) make 'the schema is data' concrete. Then come two surprises on real rows. orders has no primary key, so an INSERT duplicating id 4242 succeeds and WHERE id = 4242 returns two rows. And count(*) and count(amount_cents) diverge once one amount is set to NULL.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E3; no access needed. One script on the 18.x lab creates the compat tables with shopgen, runs the question, and prints the EXPLAIN tree, the catalog rows and both surprises. Graded levels: L1, reproduce the revenue table. L2, break it: insert the duplicate and watch the join double-count revenue. L3, defend: add the constraint that prevents it, and check.py verifies that the duplicate is now rejected.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** what is a relational database; how does postgresql execute a query; sql basics postgresql; relational model explained

### Part 5 — How a SELECT Is Evaluated: Joins, Grouping and NULL

- **Slug:** sql-select-evaluation-joins-group-by-null · **Arc:** Day 0: from zero to a first schema · **Status:** drafted 2026-10-02, gate + `--social` PASS (6,423 words, 10 figures + cover); publish after Part 4
- **Tier:** L3 · **Difficulty:** beginner · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** In what logical order does SQL evaluate a SELECT, and what does each clause do to the rows?
- **Assumes:** Part 4 — its query-lifecycle section (anchor fixed when Part 4 is drafted).
- **Hands off:** Window functions, CTEs, LATERAL and recursion go to Part 6. Why the physical order differs from the logical order goes to Parts 13–15, and join algorithms go to Part 15.
- **Worked example:** One report is built clause by clause on customers and orders, with the row count printed after each step. FROM with INNER vs LEFT JOIN needs 1,000 order-less customers to be added first: the compat generator's multiplier 7,919 is coprime to 100,000, so every existing customer has exactly 10 orders. WHERE vs HAVING is shown on the same predicate, then GROUP BY country and status. Three-valued logic: NOT IN (subquery) returns zero rows once one NULL customer_id appears, while NOT EXISTS gives the right answer. EXISTS vs IN vs JOIN shows fan-out duplicates. Then UNION vs UNION ALL, and ORDER BY … LIMIT 10 with ties. Every step is checked against a hand count on a 20-row sample.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. The script builds the report step by step and diffs each intermediate result against the hand-computed sample. step 1: reproduce each row count. step 2: introduce one NULL and predict which of six queries change. step 3: repair three broken queries (a duplicated join, NOT IN with a NULL, HAVING used as WHERE); check.py compares the results.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** sql order of execution; left join vs inner join; not in null sql; sql group by having; exists vs in

### Part 6 — Window Functions, CTEs, LATERAL and Recursive Queries

- **Slug:** postgresql-window-functions-cte-lateral-recursive · **Arc:** Day 0: from zero to a first schema · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How do you answer ranking, running-total, top-N-per-group and hierarchy questions in one query, and what does each construct cost?
- **Assumes:** Part 5 — its logical evaluation order.
- **Hands off:** The plan-level cost of sorts and hashes goes to Part 15, and the indexes that make top-N cheap go to Part 16. Graph workloads beyond recursive CTEs go to the other-engines sibling.
- **Worked example:** Each customer's running spend and rank within their country, with window frames ROWS vs RANGE vs GROUPS on tied timestamps. The top 3 orders per customer, written with ROW_NUMBER() and with LATERAL … LIMIT 3, both EXPLAINed on 100,000 customers. Gaps-and-islands sessionisation of a 1,000,000-event clickstream with a 30-minute gap rule. A 4-level category tree of about 1,000 nodes walked with WITH RECURSIVE using the SEARCH and CYCLE clauses (14+), with one injected cycle caught. A revenue cube built with GROUPING SETS and ROLLUP. The same CTE run MATERIALIZED vs NOT MATERIALIZED, showing a predicate pushed down.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. shopgen adds the events and categories tables, and each query ships with an expected result hash. step 1: reproduce. step 2: a frame clause that silently changes a running total when timestamps are duplicated. step 3: pick LATERAL or a window function for top-N given an index; check.py runs both and verifies the reader's choice is the faster one on the lab.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgresql window functions; top n per group postgres; recursive cte postgres; lateral join postgres; gaps and islands sql

### Part 7 — Designing the Schema: Keys, Normal Forms and Constraints

- **Slug:** postgresql-schema-design-normalization-constraints · **Arc:** Day 0: from zero to a first schema · **Status:** planned
- **Tier:** L3 · **Difficulty:** beginner · **Est. words:** 7,000 · **Figures:** 10
- **Answers:** How do you turn a business's rules into tables and constraints that the database enforces for you?
- **Assumes:** Part 4 — its tables and the missing-primary-key surprise.
- **Hands off:** The physical cost of types and keys goes to Part 8, audit-history triggers to Part 10, changing this schema under traffic to Part 20, multi-tenant access rules to Part 12, and JSONB as an escape hatch to Part 34.
- **Worked example:** The lab's orders table as built for Parts 1–3 (no primary key, no foreign key, status as free text, one amount, no line items) is redesigned into customers, orders, order_items, products, payments and sellers. Each normal-form violation is shown as a real anomaly on rows, for example a product price copied into 3,000 order rows and then updated in only some of them. Constraints are added one at a time and each is violated once on purpose: PRIMARY KEY; FOREIGN KEY with ON DELETE RESTRICT vs CASCADE, where a 1,000,000-row delete exposes the missing index on the referencing column; UNIQUE NULLS NOT DISTINCT (15+); CHECK; an EXCLUDE constraint preventing overlapping delivery slots (btree_gist); and 18's temporal PRIMARY KEY … WITHOUT OVERLAPS on product price history. Soft delete vs archive table vs hard delete is decided with one measured query each. One deliberate denormalisation (a stored order total) is defended with a count of reads vs writes.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. The lab migrates the compat tables to the v2 shop schema that every later part uses, and each constraint has a 'violate it' step. step 1: reproduce the anomalies. step 2: load rows the new schema must reject; check.py counts the rejections. step 3: model a new rule (one active cart per customer) as a constraint; check.py probes it with 12 adversarial inserts.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** database normalization explained; postgres foreign key index; exclusion constraint postgres; temporal primary key postgres 18; soft delete postgres

### Part 8 — Physical Design: Data Types, Column Order and Key Choice

- **Slug:** postgresql-data-types-column-order-uuid-bigint · **Arc:** Day 0: from zero to a first schema · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** What does each data-type and key choice cost in bytes, in index pages and in planner accuracy?
- **Assumes:** Part 3 — #the-tuple and #the-b-tree-one-lookup-and-one-split.
- **Hands off:** Index design beyond the primary key goes to Part 16, JSONB vs columns to Part 34, collation drift corrupting text indexes to Part 27, and changing a type under traffic to Part 20.
- **Worked example:** The v2 orders table (1,000,000 rows) is stored in several variants and measured. Amount as integer cents vs numeric(12,2) vs float8, including a float sum of 1,000,000 amounts drifting away from the exact total. The same columns in two orders, with alignment padding counted by pg_column_size and in table pages. The primary key as bigint identity vs uuidv4 vs 18's uuidv7(), compared on index size, leaf-page splits, WAL bytes during 1,000,000 inserts, and index pages touched per insert. timestamptz vs timestamp across a DST change in Europe/Berlin. text vs varchar(n) vs char(n). Status as an enum vs a lookup table vs a CHECK, including what adding a value costs. 18's virtual vs stored generated columns.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. Each variant is built in its own table and reported in bytes, pages, WAL and split counts from pgstattuple and pageinspect. step 1: reproduce. step 2: the float drift and the DST gap. step 3: choose types for a 12-column payments table under a size budget; check.py computes the row width and runs correctness tests.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** uuid vs bigint primary key postgres; uuidv7 postgres 18; postgres column order padding; timestamp vs timestamptz; numeric vs integer money postgres

### Part 9 — Getting Data In: COPY, Bulk Loads, Upsert and MERGE

- **Slug:** postgresql-bulk-loading-copy-upsert-merge · **Arc:** Day 0: from zero to a first schema · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** What is the fastest correct way to get rows into PostgreSQL, and how do you merge incoming data without races?
- **Assumes:** Part 1 — #the-full-page-image.
- **Hands off:** Streaming changes out goes to Part 39, loading from other engines to Part 26, the locking behind concurrent upserts to Part 19, and loading partition by partition to Part 30.
- **Worked example:** 1,000,000 orders are loaded into the v2 schema six ways, each timed as the median of 5 runs, with WAL bytes from pg_stat_wal: single-row autocommit INSERTs; the same inside one transaction; 1,000-row multi-VALUES batches; psycopg pipeline mode; COPY FROM STDIN; and COPY into an UNLOGGED staging table followed by INSERT … SELECT. Each is repeated with the two indexes and the foreign key kept vs dropped and rebuilt. Then a 20,000-row nightly product feed is applied with INSERT … ON CONFLICT DO UPDATE and with MERGE (RETURNING and WHEN NOT MATCHED BY SOURCE, 17+). Two concurrent loaders show that SELECT-then-INSERT creates duplicates and ON CONFLICT does not. Finally, a feed with 37 malformed rows is loaded with COPY ON_ERROR ignore (17) and REJECT_LIMIT (18).
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. A loader script with six strategies and a concurrency harness. step 1: reproduce the timing table. step 2: the race; check.py counts the duplicates. step 3: load 10,000,000 rows under a WAL budget; check.py measures the WAL and verifies the constraints were re-validated.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres bulk insert fastest; copy vs insert postgres; on conflict do update; merge vs upsert postgres; unlogged table load

### Part 10 — Logic in the Database: Functions, Procedures and Triggers

- **Slug:** postgresql-functions-procedures-triggers · **Arc:** Day 0: from zero to a first schema · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** What can run inside PostgreSQL, what does it cost per row, and which logic belongs there rather than in the application?
- **Assumes:** Part 7 — the v2 schema and its constraints.
- **Hands off:** SECURITY DEFINER attacks and privileges go to Part 12, C functions and hooks to Part 33, the trigger-based outbox to Part 39, and hot-row lock contention in depth to Part 19.
- **Worked example:** An audit-history trigger on orders, written as a row-level AFTER trigger and as a statement-level trigger with transition tables, timed on a 100,000-row UPDATE. The same lookup function marked VOLATILE vs STABLE vs IMMUTABLE, changing whether an expression index can be built and whether it is evaluated once or 1,000,000 times. A SQL-language function inlined into the plan vs the same logic in PL/pgSQL, with EXPLAIN showing both. A procedure archiving 1,000,000 old orders in 10,000-row batches with COMMIT inside CALL, vs one DELETE. A trigger-maintained per-customer order counter under pgbench at 32 clients, against the hot-row contention it creates. The subtransaction cost of exception blocks.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. Each mechanism is one step with a timing and an EXPLAIN. step 1: reproduce. step 2: a function wrongly marked IMMUTABLE returns stale results through an index. step 3: decide trigger vs application for three rules; check.py runs a concurrency test on the chosen designs.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** plpgsql tutorial; postgres trigger performance; function vs procedure postgres; immutable stable volatile postgres; transition tables trigger

### Part 11 — The Application Tier: Connections, Pooling and Prepared Statements

- **Slug:** postgresql-connection-pooling-pgbouncer-prepared-statements · **Arc:** Day 1: going live · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** How should an application connect to PostgreSQL, how big should its pool be, and why does a prepared statement sometimes get slower on its sixth run?
- **Assumes:** Part 2 — #what-a-connection-actually-costs and #connection-capacity.
- **Hands off:** Authentication and TLS go to Part 12, the selectivity behind generic plans to Part 14, reconnecting after failover to Part 23, and pool-saturation alerts to Part 28.
- **Worked example:** pgbench on the v2 shop at 10, 100 and 500 clients, direct vs through PgBouncer in session and transaction mode, measuring TPS, p99 latency and backend count, plus a connection storm after a restart. A pool size derived from Little's law and the measured mean query time, then checked by sweeping pool sizes from 4 to 64. The extended query protocol traced (Parse/Bind/Execute), and pipeline mode vs round trips. A prepared query on a skewed status column (90% delivered, 1% refunded) switching to a generic plan on its sixth execution and slowing down for 'delivered', fixed with plan_cache_mode. Transaction mode with PgBouncer's protocol-level prepared statements (max_prepared_statements, 1.21+), and the session-state traps it breaks: SET, advisory locks, temp tables and LISTEN. statement_timeout, idle_in_transaction_session_timeout and 17's transaction_timeout, each fired once.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); PgBouncer built against a user-prefix libevent; ladder E1–E5; no access needed (self-provisioned). Builds libevent and PgBouncer into the lab prefix, then runs the pgbench matrix and the plan-cache demo. step 1: reproduce the TPS and latency table. step 2: a session-state bug under transaction pooling. step 3: choose the pool mode and size for a stated workload; check.py runs it and grades p99 against a threshold.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** pgbouncer transaction mode prepared statements; postgres connection pool size; postgres generic plan slow; plan_cache_mode; too many connections postgres

### Part 12 — Securing PostgreSQL: Authentication, Privileges and Row-Level Security

- **Slug:** postgresql-security-roles-rls-authentication · **Arc:** Day 1: going live · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** Who can connect, what can they touch, and how do you prove it for a multi-tenant application?
- **Assumes:** Part 7 — the v2 schema and its sellers (the tenants).
- **Hands off:** Roles and grants as code go to Part 44, managed-cloud IAM authentication to Part 43, replication-connection security to Part 22, and PII in CDC streams to Part 39.
- **Worked example:** The shop becomes a marketplace of 500 sellers, secured from zero. pg_hba.conf gets hostssl rules with scram-sha-256 (MD5 is deprecated in 18). A local CA and server and client certificates are made with openssl. Roles are created for owner, migrator, app, read-only and analyst, with default privileges, and the public schema and search_path are hardened. RLS makes seller 42's session see only its own 2,000 orders. Then five attacks are run as the app role, and each is blocked: a same-named function planted earlier in search_path; a SECURITY DEFINER function without SET search_path; a superuser-owned view bypassing RLS (fixed with security_invoker, 15+); a non-LEAKPROOF function leaking filtered rows through an error; and the table owner bypassing its own policy (fixed with FORCE ROW LEVEL SECURITY). RLS overhead is measured on a 1,000,000-row query, and pgaudit logs each attack. Tenancy models are compared: shared tables with RLS, schema-per-tenant (catalog size at 500 schemas), and database-per-tenant. Column masking is added for the analyst role.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. Generates the CA and certificates, writes pg_hba.conf for a lab cluster, builds pgaudit via pgxs, and runs each attack with an asserted outcome. step 1: reproduce the locked-down cluster. step 2: all five attacks against an unhardened copy. step 3: write policies for a new support-agent role; check.py runs 20 access probes.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgresql row level security multi tenant; pg_hba.conf scram tls; postgres roles and privileges best practices; search_path security postgres; pgaudit

### Part 13 — Diagnosing a Slow Query: From pg_stat_statements to EXPLAIN ANALYZE to the Fix

- **Slug:** postgresql-slow-query-explain-analyze · **Arc:** The first slow query · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** Which query is hurting you, and what in its plan says why?
- **Assumes:** Part 5 — logical evaluation order. Links Part 1 #shared-buffers-what-a-buffer-actually-is for BUFFERS output, without depending on it.
- **Hands off:** Why estimates are wrong goes to Part 14, what nodes do with memory to Part 15, index choice to Part 16, and server-wide monitoring to Part 28.
- **Worked example:** A mixed pgbench workload of 8 query shapes on the v2 shop. pg_stat_statements, ranked by total_exec_time, finds the worst one. Its EXPLAIN (ANALYZE, BUFFERS, SETTINGS) is read node by node: estimated vs actual rows, loops, shared hit vs read, and Rows Removed by Filter. auto_explain catches a query that is slow for only one customer. Then six rewrites are measured before and after: OFFSET 100,000 pagination vs keyset pagination; date_trunc on a column vs a sargable range; an implicit text-to-integer cast blocking an index; NOT IN vs NOT EXISTS; OR across two columns vs UNION ALL or a BitmapOr; and an ORM-style N+1 loop of 1,000 queries vs one join.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. Enables pg_stat_statements and auto_explain (both in the 18.x contrib build), runs the workload, and captures the plans. step 1: reproduce the ranking and the plans. step 2: introduce a regression and find it from pg_stat_statements alone. step 3: fix three unseen slow queries; check.py verifies equal results and a speed threshold.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** how to read explain analyze; postgres slow query; pg_stat_statements top queries; keyset pagination postgres; postgres query not using index

### Part 14 — Where Row Estimates Come From: Statistics, Selectivity and the Cost Model

- **Slug:** postgresql-query-planner-statistics-estimates · **Arc:** The first slow query · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** How does the planner guess how many rows each step returns and what each plan costs, and why is the guess wrong?
- **Assumes:** Part 13 — its node-by-node EXPLAIN reading.
- **Hands off:** Physical join and sort behaviour goes to Part 15, index choice to Part 16, partition pruning to Part 30, and statistics after an upgrade to Part 25.
- **Worked example:** The v2 shop with deliberate skew: Zipf-distributed customer activity, status split 90/9/1, and correlated country and city. pg_stats is read for orders.status (MCV list and frequencies) and for created (histogram bounds and correlation). The selectivity of status = 'refunded' AND country = 'DE' is computed by hand under the independence assumption, matched to EXPLAIN, then corrected with CREATE STATISTICS (dependencies, ndistinct, mcv). default_statistics_target is compared at 100 vs 1,000. A sequential scan's cost is computed by hand (seq_page_cost × pages + cpu_tuple_cost × rows) and matched to EXPLAIN. random_page_cost 4.0 vs 1.1 flips an index scan to a sequential scan at a measured row fraction. Join-order search is shown on a 13-table query crossing geqo_threshold (12), with join_collapse_limit changing the plan.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. Uses shopgen's skew mode and prints the pg_stats rows and the hand calculations beside EXPLAIN. step 1: reproduce hand vs planner estimates. step 2: correlated predicates misestimated 100x. step 3: fix three misestimates with statistics, not hints; check.py requires estimate error below 2x.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres row estimate wrong; how the postgres query planner works; extended statistics postgres; random_page_cost ssd; geqo postgres

### Part 15 — How the Executor Runs a Plan: Joins, Sorts, Hashes and Parallel Workers

- **Slug:** postgresql-executor-joins-sorts-parallel-query · **Arc:** The first slow query · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** What does each plan node physically do with rows and memory, and when does each join algorithm win?
- **Assumes:** Part 1 — #local-memory-work_mem-and-its-family; links Part 2 #parallel-workers-and-the-shared-pool.
- **Hands off:** How the planner chose a node goes to Part 14, server-wide memory tuning to Part 32, and joins across shards to Part 42.
- **Worked example:** orders ⋈ customers is executed three ways by disabling the alternatives: a nested loop with an inner index scan; a hash join, which spills into batches at work_mem 4 MB and fits at 64 MB (temp_blks_written shows the difference); and a merge join over sorted inputs. Time and memory are measured for outer sizes from 10 to 1,000,000 rows to locate each crossover. Sorts are compared: in-memory quicksort, external merge, and top-N heapsort for LIMIT 10. Also HashAggregate vs GroupAggregate under hash_mem_multiplier, Memoize on a repeated inner lookup, and incremental sort. A parallel sequential scan with a partial aggregate and Gather runs at 0, 2, 4 and 6 workers. One node's ExecProcNode pull loop is drawn to show the Volcano iterator model. JIT is measured only if the build has LLVM; otherwise the post says it was not measured.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. enable_* toggles and work_mem sweeps, with timings as the median of 5 runs. step 1: reproduce the crossover chart. step 2: force a hash join to spill 10x. step 3: pick work_mem for a 50-connection reporting pool under a RAM budget; check.py checks peak memory and spill counts.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** hash join vs merge join vs nested loop; postgres parallel query; external merge disk sort postgres; memoize postgres; hash aggregate work_mem

### Part 16 — B-tree Index Design: Column Order, Covering, Partial and Expression Indexes

- **Slug:** postgresql-btree-index-design · **Arc:** The first slow query · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** Which B-tree indexes should a table have, and how do you prove each one earns its write cost?
- **Assumes:** Part 3 — #the-b-tree-one-lookup-and-one-split; links #hot-the-update-that-skips-the-indexes.
- **Hands off:** Non-B-tree index types go to Part 17, CONCURRENTLY builds under traffic in depth to Part 20, and index bloat from vacuum debt to Part 29.
- **Worked example:** Five v2-shop queries each get their best index, with pages read before and after. A customer's latest orders: (customer_id, created DESC) vs (created, customer_id). Unshipped orders by date: a partial index WHERE status = 'pending' at 1% of rows vs the full index, compared by size ratio. Case-insensitive email lookup: an expression index on lower(email). An index-only scan made possible with INCLUDE, then lost when the visibility map is cleared. 18's skip scan letting (status, created) serve a created-only predicate. hypopg tests each index before it is built. Each index's write price is measured as WAL bytes per 100,000 updates, along with the HOT updates it costs. Unused and duplicate indexes are found in pg_stat_user_indexes, and a bloated index is rebuilt with REINDEX CONCURRENTLY.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. hypopg is built via pgxs, and the lab keeps a read/write ledger per index. step 1: reproduce. step 2: an index that kills HOT updates and doubles WAL. step 3: choose at most 4 indexes for a 10-query workload under a write budget; check.py replays the workload and scores reads and WAL.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** composite index column order postgres; partial index postgres; covering index include postgres; unused indexes postgres; skip scan postgres 18

### Part 17 — Beyond the B-tree: GIN, GiST, SP-GiST, BRIN, Hash and Bloom

- **Slug:** postgresql-index-types-gin-gist-spgist-brin · **Arc:** The first slow query · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 17
- **Answers:** What does each non-B-tree index store, which operators can it answer, and what does it cost to maintain?
- **Assumes:** Part 3 — #the-heap-page-byte-by-byte (the page format every index access method shares).
- **Hands off:** Each index in its workload goes to the platform arc: GIN for JSONB (34) and full text (35), GiST for geometry (37), BRIN for time series (38). pgvector's HNSW and IVFFlat go to Part 36, and the index access-method API to Part 33.
- **Worked example:** One index of each kind on shop data, inspected with pageinspect's GIN, GiST and BRIN functions. GIN on products.tags text[]: the entry tree and posting lists, and the fastupdate pending list growing under inserts and being flushed by vacuum (insert throughput with fastupdate on vs off). GiST on a tstzrange of delivery windows, answering overlap queries and backing the exclusion constraint. SP-GiST on inet addresses. BRIN on events.created at pages_per_range 32 and 128, compared in size with a B-tree on the same column, then on a physically shuffled copy. Hash vs B-tree on a 64-character text key. bloom for 6-column equality. A decision table maps query shapes to index types, with each cell backed by one measured query.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. Uses contrib from the 18.x build (pageinspect, btree_gin, btree_gist, bloom). Each index is built, inspected and benchmarked. step 1: reproduce. step 2: BRIN on uncorrelated data. step 3: pick index types for 8 query shapes; check.py verifies each chosen index is used and meets a latency bar.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** gin vs gist; brin index postgresql; postgres index types explained; gin fastupdate pending list; sp-gist

### Part 18 — Transactions, Snapshots and Isolation Levels

- **Slug:** postgresql-transaction-isolation-mvcc · **Arc:** The first concurrency bug · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** What does each isolation level promise in PostgreSQL, which anomalies can each still produce, and how do you write code that survives serialization failures?
- **Assumes:** Part 3 — #who-can-see-a-row-xmin-xmax-and-the-hint-bits.
- **Hands off:** Locks and waits go to Part 19, the horizon at scale to Part 29, and distributed transactions to Part 42. Isolation in other engines goes to the other-engines sibling.
- **Worked example:** Two sessions driven in lockstep (threads with barriers) reproduce each anomaly on shop rows. A lost update on inventory under Read Committed, and its three fixes: an atomic UPDATE, SELECT … FOR UPDATE, and Repeatable Read with a retry. A non-repeatable read and a phantom. Write skew: two warehouses each ship the last unit because each saw the other's stock; this is allowed under Repeatable Read and caught under Serializable, with the SIReadLock rows visible in pg_locks. The snapshot printed with pg_current_snapshot() and matched to Part 3's visibility rules. Read Committed's UPDATE re-check (EvalPlanQual) returning a row the snapshot never saw. Serialization-failure rates at 8, 32 and 64 pgbench clients, with and without a retry loop. A SERIALIZABLE READ ONLY DEFERRABLE report.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. A small harness scripts the interleavings deterministically. step 1: reproduce every anomaly. step 2: construct your own write-skew case. step 3: pick an isolation level and retry policy for three workflows; check.py runs 10,000 interleavings and requires zero invariant violations.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres isolation levels explained; write skew postgres serializable; serialization failure retry postgres; lost update postgres; mvcc postgres

### Part 19 — Locks: Row Locks, Lock Modes, Lock Queues and Deadlocks

- **Slug:** postgresql-locks-deadlocks-lock-queue · **Arc:** The first concurrency bug · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** What locks does each statement take, who waits on whom, and how do you stop one lock from taking the site down?
- **Assumes:** Part 18 — its snapshot and write-conflict sections.
- **Hands off:** Safe DDL recipes go to Part 20, lock monitoring to Part 28, and distributed deadlocks to Part 42.
- **Worked example:** The lock-mode conflict matrix is probed on orders from pg_locks for 8 statements. The lock-queue outage is reproduced: a 60-second report holds ACCESS SHARE, ALTER TABLE orders ADD COLUMN waits for ACCESS EXCLUSIVE, and 200 pgbench clients queue behind the ALTER. The wait graph is drawn from pg_blocking_pids alongside the latency spike, and the outage is fixed with lock_timeout plus a retry. FOR UPDATE vs FOR NO KEY UPDATE, and the FOR KEY SHARE lock a foreign-key check takes, which is why inserting an order does not block a non-key customer update. Multixacts appear when two transactions share a row lock. A deadlock between two transfers taken in opposite order is detected after deadlock_timeout and shows up in the log. A SKIP LOCKED queue drained by 8 workers (100,000 jobs) is compared with a naive FOR UPDATE queue. An advisory lock guards a singleton job.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. Scripted blockers and waiters, with a pg_locks sampler that renders the wait graph. step 1: reproduce the matrix and the outage. step 2: create a deadlock. step 3: build a queue that meets a throughput bar; check.py verifies exactly-once processing of 100,000 jobs.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres lock modes; deadlock detected postgres; alter table lock queue postgres; select for update skip locked queue; pg_locks blocking

### Part 20 — Zero-Downtime Schema Migrations, Tested in CI

- **Slug:** postgresql-zero-downtime-schema-migrations · **Arc:** The first concurrency bug · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** How do you change a live schema under traffic without blocking it or breaking the application version still running?
- **Assumes:** Part 19 — the lock-queue outage and lock_timeout.
- **Hands off:** Major-version moves go to Part 25, migrating from another engine to Part 26, schema changes in a CDC stream to Part 39, and migrations inside fleet automation to Part 44.
- **Worked example:** Twelve migrations run while pgbench holds a steady rate against the v2 shop, and each is measured for maximum lock wait and TPS dip. They are: ADD COLUMN with a constant vs a volatile default; SET NOT NULL via CHECK … NOT VALID + VALIDATE, and 18's NOT VALID NOT NULL; CREATE INDEX vs CREATE INDEX CONCURRENTLY, including the INVALID index a failed concurrent build leaves; a foreign key added NOT VALID and then validated; orders.id from int to bigint done as expand/contract (new column, batched backfill of 10,000,000 rows, sync trigger, swap); a column rename behind a compatibility view across two application versions; and a drop. The same migrations then run through a migration tool in a local CI script against an ephemeral cluster, linted by squawk and asserted by pgTAP tests.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. A traffic generator plus a migration runner that records lock waits; squawk is a prebuilt binary and pgTAP is built via pgxs. step 1: reproduce the twelve-row table. step 2: the naive versions and the outages they cause. step 3: write an expand/contract plan for a new change; check.py runs it under traffic and fails on any lock wait over 1 s or any error in the old application version's queries.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** zero downtime migration postgres; add column without locking postgres; create index concurrently; int to bigint migration postgres; expand and contract migration

### Part 21 — Backup and Point-in-Time Recovery: Proving You Can Restore

- **Slug:** postgresql-backup-point-in-time-recovery · **Arc:** Staying up · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** What does it take to get the database back to the second before a mistake, and how do you know the backups work before you need them?
- **Assumes:** Part 3 — #archiving and #replaying-a-crash.
- **Hands off:** Standbys go to Part 22, corruption that backups copy faithfully to Part 27, operator-managed backups to Part 44, and managed snapshots to Part 43.
- **Worked example:** At a scripted instant T, DELETE FROM orders runs without a WHERE clause under pgbench traffic. The database is recovered to T minus 1 second four ways: pg_dump (everything since the dump is lost); pg_basebackup + WAL archive + recovery_target_time; pgBackRest full + differential + incremental to an S3 repository on a local MinIO; and 17's incremental pg_basebackup with pg_combinebackup. Each is measured for backup size, backup time, restore time and rows lost, giving an RPO/RTO table. The new timeline's history file is read. pg_verifybackup and amcheck check the restore. A delayed standby (recovery_min_apply_delay 15 min) is shown as the faster undo. A nightly restore-test job restores into a scratch cluster and asserts row counts and checksums: the runbook as code.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); pgBackRest built against a user-prefix libyaml, plus core pg_basebackup/pg_combinebackup; ladder E1–E5; no access needed (self-provisioned). Builds pgBackRest, starts MinIO with generated credentials, and runs the disaster and the four recoveries. step 1: reproduce the RPO/RTO table. step 2: a gap in the WAL archive, and a restore that stops there. step 3: design a backup policy for a stated RPO, RTO and retention; check.py triggers a disaster at a random time and grades the restore.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres point in time recovery; pgbackrest tutorial; pg_dump vs pg_basebackup; incremental backup postgres 17; restore postgres to timestamp

### Part 22 — Streaming Replication: Slots, Synchronous Commit, Lag and Conflicts

- **Slug:** postgresql-streaming-replication · **Arc:** Staying up · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** How does a standby stay in step with the primary, what does each synchronous_commit level cost per commit, and what breaks when a standby falls behind?
- **Assumes:** Part 3 — #replicas (walsender, walreceiver and replay).
- **Hands off:** Automatic promotion goes to Part 23, row-level replication to Part 24, lag alerts to Part 28, and hot_standby_feedback bloat at scale to Part 29.
- **Worked example:** A primary and two standbys, one synchronous and one asynchronous, run on the lab machine, built with pg_basebackup -R. Write, flush and replay lag are read from pg_stat_replication under pgbench. Commit latency is measured at synchronous_commit off, local, remote_write, on and remote_apply (linking Part 2's WAL-writer section). Then: quorum commit with ANY 1 (s1, s2); a stopped standby whose slot grows pg_wal until max_slot_wal_keep_size invalidates it (plus 18's idle_replication_slot_timeout); a standby query cancelled by a vacuum conflict, then hot_standby_feedback moving the bloat to the primary; a cascading standby; and a SIGSTOPped synchronous standby blocking every commit on the primary.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. A cluster builder for N nodes on separate ports, with small shared_buffers so the set fits in about 5 GiB of free RAM. step 1: reproduce the latency-per-level table. step 2: the slot that grows pg_wal; the growth is measured, but the disk-full itself is modelled unless a user-space size cap is available. step 3: pick synchronous settings for a stated RPO and latency budget; check.py kills a node and counts lost commits.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres streaming replication setup; replication lag postgres; replication slot wal growing; synchronous_commit remote_apply; hot standby conflict

### Part 23 — High Availability and Failover: Patroni, Consensus, Fencing and pg_rewind

- **Slug:** postgresql-high-availability-patroni-failover · **Arc:** Staying up · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** How does a PostgreSQL cluster pick a new primary when the old one dies, without ever having two?
- **Assumes:** Part 22 — synchronous standbys and replay lag.
- **Hands off:** Operators doing the same job on Kubernetes go to Part 44 and managed failover to Part 43. Multi-primary systems and distributed SQL go to the other-engines sibling.
- **Worked example:** A 3-node etcd and 3 Patroni-managed PostgreSQL 18 nodes run on one machine. The primary is killed with kill -9 under pgbench, and the lab measures detection time against ttl and loop_wait, promotion, and clients reconnecting through libpq multi-host with target_session_attrs=read-write (HAProxy on Patroni's REST health checks is shown as the alternative). A client-side commit log counts transactions lost with asynchronous replication vs synchronous_mode. A SIGSTOPped primary (the zombie) is demoted when its leader key expires, and the post explains why a watchdog needs root. The old primary rejoins with pg_rewind, which needs checksums, and 18 clusters have them on by default; the timeline fork is shown in pg_waldump. Then a planned switchover, etcd quorum loss with failsafe_mode, and a partition between the primary and etcd, modelled at TCP level with toxiproxy.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); Patroni in a uv venv with static etcd, three nodes on one host; ladder E1–E5; optional AR-02 (real network partitions); if declined, one-host failures only (kill -9, SIGSTOP), labelled as such. Brings up etcd x3 and Patroni x3 with a client that logs every acknowledged commit. step 1: reproduce failover timing and loss. step 2: the zombie primary. step 3: tune ttl, loop_wait and synchronous_mode for a stated RTO and RPO; check.py runs 10 randomized failovers and grades loss and downtime.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** patroni tutorial; postgres automatic failover; pg_rewind; split brain postgres; patroni etcd

### Part 24 — Logical Replication and Logical Decoding

- **Slug:** postgresql-logical-replication-decoding · **Arc:** Staying up · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** How does PostgreSQL turn physical WAL into row changes another database can apply, and where does that stop working?
- **Assumes:** Part 3 — #wal-records-lsns-and-segment-files and #one-record-byte-by-byte; links Part 22 for slots.
- **Hands off:** Using it for upgrades goes to Part 25 and non-PostgreSQL consumers to Part 39. Conflict-free multi-primary goes to the other-engines sibling.
- **Worked example:** A publisher and a subscriber, both on 18.x. A publication on orders uses a row filter (country = 'IN') and a column list. The initial sync of 1,000,000 rows is timed, then streaming begins. One UPDATE is decoded through test_decoding and pgoutput via pg_logical_slot_peek_changes, and REPLICA IDENTITY DEFAULT vs FULL changes what the old row carries. A 1,000,000-row transaction spills past logical_decoding_work_mem (spill_bytes in pg_stat_replication_slots); this is the setting Part 1 said belonged to Part 3. Then: streaming = parallel; a duplicate-key conflict that stops the apply worker, 18's conflict counters, and ALTER SUBSCRIPTION … SKIP; what is not replicated (DDL, sequence values); a failover slot synchronised to a standby (17+); and origin = none for bidirectional replication, with why its conflicts are hard.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. Two clusters, with a script for each step and the decoded output captured. step 1: reproduce. step 2: DDL on the publisher halts the subscriber. step 3: design a filtered replica for an analytics team; check.py verifies row counts, filters and lag.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres logical replication; logical decoding postgres; replica identity full; logical_decoding_work_mem; pgoutput

### Part 25 — Major Version Upgrades: pg_upgrade, Blue-Green and the Way Back

- **Slug:** postgresql-major-version-upgrade · **Arc:** Staying up · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 10
- **Answers:** How do you move a production database to a new major version with the least downtime and a way back?
- **Assumes:** Part 24 — publications, subscriptions and initial sync.
- **Hands off:** Operator-driven upgrades go to Part 44, managed upgrade paths to Part 43, and migrations from other engines to Part 26.
- **Worked example:** A fresh 16.2 cluster, built with the series' 16.2 binaries in a new data directory (never the live lab), is loaded with the v2 shop at 10,000,000 orders. It is upgraded to 18.x three ways with downtime measured: pg_upgrade copy, --link, and 18's --swap. pg_upgrade --check catches the checksum mismatch trap: 16's initdb has checksums off, while 18's initdb defaults to on. 18's pg_upgrade carries optimizer statistics over, compared with the old analyze-in-stages gap, and vacuumdb --missing-stats-only fills the rest. An incompatible extension gets flagged. Then a logical blue-green upgrade: a 16.2 publisher feeds an 18.x subscriber, sequences are synced by hand, the write freeze and cutover are measured in seconds, and reverse replication provides the rollback path. Last, minor updates as routine: the lab's 16.2 is 13 minor releases behind 16.15.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. Uses both the 16.2 wheel binaries and the 18.x build in user space. step 1: reproduce the downtime table. step 2: upgrade without --check. step 3: write an upgrade runbook for a stated downtime; check.py executes it and measures the write freeze.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** pg_upgrade; postgres major version upgrade zero downtime; upgrade postgres 16 to 18; pg_upgrade link vs copy; blue green postgres upgrade

### Part 26 — Migrating to PostgreSQL from Another Database

- **Slug:** migrating-to-postgresql-from-another-database · **Arc:** Staying up · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 9
- **Answers:** How do you move a schema and its data into PostgreSQL from another engine, prove nothing was lost or changed, and cut over?
- **Assumes:** Part 8 — its type-by-type costs.
- **Hands off:** Source-engine internals (InnoDB, binlog, Oracle redo) go to the other-engines sibling, and CDC mechanics on the PostgreSQL side to Part 39.
- **Worked example:** The shop is exported to SQLite through Python's standard library, with no server. SQLite's type affinity lets '12.50' sit in an INTEGER column and '0000-00-00' in a date column. The data is migrated to PostgreSQL 18 through a column-by-column type-mapping table. COPY with ON_ERROR ignore and REJECT_LIMIT counts and logs the rows PostgreSQL refuses. Identity sequences are reset with setval. Six semantic differences are tested with the same query on both sides: case-sensitive comparison, empty string vs NULL, integer division, boolean, date arithmetic, and collation order. Validation uses per-table row counts and ordered per-column hashes. Cutover (dump/load with a read-only window, or change capture from the source) is decided against a stated downtime budget. MySQL 8.4 from a generic tarball is an optional second source.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. shopgen writes the SQLite source; the lab ships the migration script, a validator and a semantics test suite. step 1: reproduce. step 2: a silent truncation that the validator must catch. step 3: map a new 20-column source table; check.py validates round-trip equality.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** migrate mysql to postgres; sqlite to postgres migration; oracle to postgresql migration; database migration validation; pgloader

### Part 27 — When Storage Lies: Checksums, amcheck and Corruption Recovery

- **Slug:** postgresql-data-corruption-checksums-amcheck · **Arc:** Staying up · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 10
- **Answers:** How do you detect that PostgreSQL's files no longer mean what it thinks, and what can you still save?
- **Assumes:** Part 3 — #the-header (pd_checksum) and #the-b-tree-one-lookup-and-one-split.
- **Hands off:** Restoring clean data goes to Part 21, and corruption alerts to Part 28.
- **Worked example:** Bytes are flipped with dd in a scratch copy of the shop cluster. A heap page gives a checksum failure and 'invalid page in block'; it is salvaged with zero_damaged_pages and the rows lost are counted. A B-tree leaf is found by pg_amcheck (bt_index_check) and fixed with REINDEX. A damaged heap tuple header is caught by verify_heapam. A missing WAL segment stops recovery, and a damaged pg_xact file is shown too. Then collation drift: a text index built under one collation version is queried after a simulated version change, giving wrong results and a version-mismatch warning, and it is fixed with REINDEX plus ALTER COLLATION … REFRESH VERSION. Finally, checksums are enabled offline with pg_checksums on a 16.2 copy; 18's initdb enables them by default.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. A corruption injector that only ever works on a copied data directory, with a detector run after each injection. step 1: reproduce each detection. step 2: an unseen injected fault. step 3: write a triage runbook; check.py injects 3 random faults and grades detection and the data saved.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres data corruption; invalid page in block postgres; amcheck; pg_checksums; postgres collation glibc upgrade index corruption

### Part 28 — Observing PostgreSQL: Statistics Views, Wait Events, Logs and Alerts

- **Slug:** postgresql-monitoring-observability-wait-events · **Arc:** Growth · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** What should you watch on a PostgreSQL server, what does each signal mean, and which ones deserve a page at 3 a.m.?
- **Assumes:** Part 2 — #the-rest-of-the-cast (every process that can appear waiting).
- **Hands off:** Acting on the evidence goes elsewhere: capacity to Part 31, tuning to Part 32, vacuum to Part 29.
- **Worked example:** The shop runs a scripted day of pgbench traffic with four injected incidents: a lock pile-up, a runaway query, a replica falling behind, and an idle-in-transaction session holding the horizon. Each incident is found first in the raw views: pg_stat_activity wait events sampled every 100 ms as a poor man's active-session history, pg_stat_io, pg_stat_wal, pg_stat_checkpointer, pg_stat_progress_vacuum, pg_stat_replication and age(datfrozenxid). Then it is found again on a Prometheus + postgres_exporter + node_exporter stack in user space. The logging settings (log_min_duration_statement, log_lock_waits, log_autovacuum_min_duration, log_checkpoints) are parsed by a script and by pgBadger. OS-level evidence comes from pidstat and iostat, plus perf only if the kernel allows it. An alert set covers XID age, replication lag, connection saturation, long transactions and archive failures; each threshold is justified, and each incident fires exactly its own alert.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); Prometheus and postgres_exporter static binaries; ladder E1–E5; optional AR-03 (perf sysctl for flame graphs); if declined, wait events and pg_stat_io only. An incident injector plus the exporter stack and alert rules. step 1: reproduce the four incidents in the views and the alerts. step 2: diagnose an unseen incident. step 3: write the alert rules; check.py runs 6 incidents and scores true and false pages.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres monitoring; postgres wait events; prometheus postgres_exporter alerts; pg_stat_activity; pgbadger

### Part 29 — Vacuum at Production Scale: Bloat, Freezing and Wraparound

- **Slug:** postgresql-vacuum-bloat-transaction-wraparound · **Arc:** Growth · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** Why does a busy table grow without bound, how close is the database to refusing writes, and how do you tune vacuum so neither happens?
- **Assumes:** Part 2 — #autovacuum-part-one-how-it-decides and #the-horizon.
- **Hands off:** Partition-level maintenance goes to Part 30 and per-table settings as code to Part 44. XID-age alerts are already built in Part 28.
- **Worked example:** orders at 10,000,000 rows runs a 10:1 update-heavy pgbench script. Bloat is tracked over time with pgstattuple (dead tuples, free space), comparing autovacuum_vacuum_scale_factor 0.2 vs 0.01 per table and a raised cost limit. Four culprits hold the xmin horizon and each is found with one query: an idle-in-transaction session, a hot_standby_feedback standby, an abandoned replication slot, and a forgotten prepared transaction. Freezing follows: age(relfrozenxid) advancing, an aggressive vacuum, and the anti-wraparound autovacuum that cannot be cancelled. A throwaway cluster is pushed near the limit with pg_resetwal (procedure pinned at research time) to show the warnings, vacuum_failsafe_age and the stop. Also covered: 18's eager freezing of all-visible pages, multixact age, pg_repack vs VACUUM FULL lock time, and 17's TidStore removing the index-pass multiplier Part 2 measured on 16.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. pgstattuple and pg_repack are built via pgxs, and the wraparound demo runs only on a throwaway cluster. step 1: reproduce the bloat curves. step 2: find a hidden horizon holder. step 3: per-table settings that keep bloat under 20% at stated write rates; check.py runs 30 simulated minutes.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres table bloat; transaction id wraparound postgres; autovacuum tuning; pg_repack vs vacuum full; postgres freeze

### Part 30 — Partitioning: Pruning, Retention and the Traps

- **Slug:** postgresql-table-partitioning · **Arc:** Growth · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** When does splitting a table into partitions make queries, maintenance and retention cheaper, and when does it make them worse?
- **Assumes:** Part 13 — reading EXPLAIN (Subplans Removed, per-partition nodes).
- **Hands off:** Time-series specifics go to Part 38, spreading partitions across nodes to Part 42, and tiering cold partitions to Part 41.
- **Worked example:** orders at 100,000,000 rows over 24 months is compared as one table, as 24 monthly range partitions, and as 16 hash partitions on customer_id. The lab shows plan-time and run-time pruning in EXPLAIN, and planning time at 24, 365 and 3,000 partitions. Retention by DETACH PARTITION CONCURRENTLY + DROP is compared with DELETE of one month on time, WAL bytes and bloat left behind. Partition-wise join and aggregate are shown on and off. Also covered: the unique-constraint rule (it must include the partition key) and what it does to orders.id; the default-partition trap; indexing a partitioned table with ON ONLY and ATTACH; pg_partman premaking and retention scheduled by pg_cron; and vacuum per partition vs one huge table.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. Uses shopgen's L scale, with pg_partman and pg_cron built via pgxs. step 1: reproduce. step 2: a query that prunes nothing. step 3: pick a scheme for stated queries and retention; check.py scores planning time, pruning and retention cost.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres partitioning; partition pruning postgres; pg_partman; detach partition concurrently; postgres partitioning performance

### Part 31 — Capacity Planning: Benchmarking with pgbench and the Scaling Decision

- **Slug:** postgresql-capacity-planning-pgbench · **Arc:** Growth · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** How much load can this database take, which resource runs out first, and what do you scale when it does?
- **Assumes:** Part 28 — attributing a ceiling with wait events and pg_stat_io.
- **Hands off:** Moving the ceiling with settings goes to Part 32, sharding to Part 42, and buying the ceiling from a vendor to Part 43.
- **Worked example:** The shop's own workload is written as pgbench custom scripts (70% reads, 25% order inserts, 5% reports) with random_zipfian keys. It runs at 1 to 64 clients, 5 repetitions each, reported as throughput and p50/p95/p99 with spread. The knee is located and attributed to CPU, WAL write, lock contention or buffer eviction from wait events and pg_stat_io. Closed-loop runs vs fixed-rate (--rate) runs expose coordinated omission. Headroom at 2x traffic is read off the curve. Then the scaling decision tree (bigger machine, read replicas with read-your-writes, caching, partitioning, functional split, sharding) has each branch defended or rejected with these numbers. The post also explains why a laptop's curve does not transfer to production hardware.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. A benchmark harness with repetitions, spread and a report. step 1: reproduce the curve. step 2: a benchmark that lies (warm cache, no think time). step 3: a capacity plan for 3x growth; check.py re-runs at the claimed load and grades p99.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** pgbench tutorial; postgres benchmark; how to scale postgres; when to shard postgres; postgres capacity planning

### Part 32 — Tuning PostgreSQL from Evidence

- **Slug:** postgresql-performance-tuning-configuration · **Arc:** Growth · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** Which server settings actually move performance on a given workload, by how much, and how do you prove it?
- **Assumes:** Part 31 — the benchmark method and the attributed ceiling.
- **Hands off:** Query-level fixes go to Parts 13 and 16, parameter groups to Part 43, and config as code to Part 44.
- **Worked example:** Starting from the default postgresql.conf and Part 31's workload, one setting group changes at a time, with 5 runs each. shared_buffers goes from 128 MB to 2 GB, sized to the machine's roughly 5 GiB free rather than a rule of thumb (links Part 1). effective_cache_size changes plans. work_mem is set per role vs globally. max_wal_size and checkpoint_timeout change checkpoint frequency and full-page-image volume (links Part 1's full-page image). Also: wal_compression = zstd; random_page_cost for NVMe; 18's io_method sync vs worker with io_combine_limit on a cold scan (io_uring is not built, since liburing is missing); and per-table storage parameters. OS settings that need root (huge pages, swappiness, dirty ratios, THP) are checked read-only and measured only if access is granted. OLTP and reporting profiles are compared, and a tuning log records every change, including the settings that did nothing.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); huge pages and vm.* settings need privileges; ladder E1–E5; optional AR-03 (one sudo session for sysctls); if declined, those settings are documented, not measured. A parameter-sweep harness on Part 31's benchmark. step 1: reproduce the per-setting deltas. step 2: a setting that looks good in a short run and fails in a long one. step 3: a config for a stated workload and RAM; check.py benchmarks it against the default and a reference.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres performance tuning; postgresql.conf tuning; shared_buffers size; max_wal_size checkpoint tuning; io_method postgres 18

### Part 33 — How Extensions Hook into PostgreSQL, and Writing One

- **Slug:** postgresql-extensions-hooks-writing-an-extension · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 8,500 · **Figures:** 13
- **Answers:** What can an extension change inside the server, how is it loaded, and how do you write, test and ship one?
- **Assumes:** Part 2 — #the-postmaster-the-process-that-never-touches-your-data (what shared_preload_libraries loads, and where).
- **Hands off:** The big extensions each get their own part: pgvector (36), PostGIS (37), TimescaleDB (38), Citus (41). Trusted-language extensions on managed services go to Part 43.
- **Worked example:** CREATE EXTENSION pg_stat_statements is traced through its control file, install script, and rows in pg_extension and pg_depend, and then ALTER EXTENSION … UPDATE through a version path. shared_preload_libraries loaded by the postmaster is contrasted with a per-session LOAD. A C extension of about 150 lines is built with pgxs. It has a SQL-callable function (fmgr V1), an ExecutorEnd hook that logs any plan node whose actual rows are 10x its estimate, a custom GUC and a background worker, and it is tested with pg_regress (make installcheck). One figure then maps the extension points the big extensions use: types and operators; index access method (pgvector); custom scan (Citus); table access method (columnar storage, the non-heap AMs Part 3 left out); FDW (Part 41); and planner and executor hooks. The post ends with trusted languages and pg_tle for managed services.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E5; no access needed. gcc and pgxs against the 18.x build, with regression tests shipped alongside the extension. step 1: build it and pass the tests. step 2: a hook that forgets to call the previous hook. step 3: add a GUC threshold feature with tests; check.py runs pg_regress.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** write postgresql extension in c; postgres hooks; shared_preload_libraries; pgxs tutorial; postgres table access method

### Part 34 — JSONB: When a Document Column Earns Its Place

- **Slug:** postgresql-jsonb-semi-structured-data · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** When should data live in JSONB rather than columns, and how do you query, index and update it without surprises?
- **Assumes:** Part 17 — its GIN section.
- **Hands off:** JSON change events go to Part 39. Document-database designs go to the other-engines sibling.
- **Worked example:** Partner-supplied product attributes, which vary by category, are stored for 20,000 products three ways (columns, EAV and JSONB) and compared on size and on five queries. The part covers jsonb operators and jsonpath (@?, @@), and 17's JSON_TABLE shredding a document into rows. GIN jsonb_ops vs jsonb_path_ops is compared on size and on which operators each serves, alongside an expression B-tree on a single key. Updating one key in a 5 KB document rewrites the whole TOASTed value; the WAL bytes are measured (links Part 3's TOAST section). The planner cannot see key frequencies, and extended statistics on an expression fix that. CHECK constraints validate document shape. json vs jsonb is compared on duplicate keys and key order.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. shopgen's attribute documents, with each query shipping a result hash. step 1: reproduce. step 2: a hot key updated 1,000 times a second inside a large document. step 3: pick columns vs JSONB for 10 attributes given query patterns; check.py scores size and latency.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres jsonb performance; jsonb gin index; jsonb vs json; json_table postgres; jsonb vs columns

### Part 35 — Full-Text and Fuzzy Search in PostgreSQL

- **Slug:** postgresql-full-text-search-trigram · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How does PostgreSQL turn text into searchable terms, rank matches and tolerate typos, and when is that not enough?
- **Assumes:** Part 17 — its GIN and GiST sections.
- **Hands off:** Semantic and hybrid search go to Part 36. BM25 and Lucene-style engines go to the other-engines sibling.
- **Worked example:** 20,000 product titles and descriptions come from an openly licensed corpus, chosen and licence-checked at research time. The to_tsvector pipeline (parser, dictionaries, lexemes) is shown for one sentence under the english and simple configurations. The part adds unaccent and a synonym dictionary, a weighted generated tsvector column with a GIN index, and websearch_to_tsquery on user input. ts_rank vs ts_rank_cd order the same 10 hits differently. Also covered: phrase search with <->, ts_headline and its cost, pg_trgm similarity finding 'postgersql', GIN vs GiST trigram indexes, and LIKE '%term%' made fast. Latency is measured at 20,000 and 2,000,000 rows. The post ends where PostgreSQL stops (BM25 relevance, faceting, analyzers) and names pg_search as an extension option.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. A corpus download and loader, with queries that have expected top-10 lists. step 1: reproduce. step 2: a dictionary mismatch between the index and the query. step 3: a search configuration for 20 labelled queries; check.py scores hits@10.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres full text search; pg_trgm fuzzy search; postgres vs elasticsearch; ts_rank postgres; postgres search typo tolerance

### Part 36 — Vector Search with pgvector: Exact, IVFFlat, HNSW and Hybrid

- **Slug:** pgvector-vector-search-hnsw-ivfflat · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** How do you store embeddings and find nearest neighbours in PostgreSQL at a recall and latency you can defend?
- **Assumes:** Part 17 — the index-access-method comparison; links Part 35 for the hybrid section.
- **Hands off:** Dedicated vector databases go to the other-engines sibling. Embedding-model choice and RAG beyond retrieval are out of scope.
- **Worked example:** 100,000 product and review texts are embedded on CPU with a small open 384-dimension model, plus a 1,000,000-vector public ANN benchmark set for scale. Exact k-NN serves as ground truth. IVFFlat (lists 100 and 1,000; probes 1, 10 and 40) is compared with HNSW (m 16 and 32; ef_construction 64 and 200; ef_search 40, 100 and 400) on recall@10, p95 latency, build time, index size and the maintenance_work_mem each build needs, drawn as a recall-latency frontier. Filtered search ('in stock at seller 42') uses pgvector's iterative index scans, compared with post-filtering that returns too few rows. halfvec and binary quantization with re-ranking trade size against recall. Hybrid search combines Part 35's full-text ranking with vector ranking through reciprocal rank fusion in one SQL query. The HNSW memory budget is checked against this machine's roughly 5 GiB free.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); pgvector via pgxs, embeddings from a CPU model in a uv venv; ladder E1–E5; no access needed. An embedding script, an index-sweep harness and a recall evaluator. step 1: reproduce the frontier. step 2: a filter that starves HNSW. step 3: parameters for recall of at least 0.95 under a p95 budget; check.py measures both.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** pgvector hnsw vs ivfflat; pgvector performance tuning; pgvector filtering; hybrid search postgres; pgvector recall

### Part 37 — Geospatial PostgreSQL with PostGIS

- **Slug:** postgis-geospatial-postgresql · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How do you store locations and shapes, answer 'what is near, inside or within 5 km' correctly, and make it fast?
- **Assumes:** Part 17 — its GiST section.
- **Hands off:** Routing (pgRouting) and raster analysis are named but not covered; spatial joins across shards go to Part 42.
- **Worked example:** The data is 200 warehouses, 100,000 customer locations (synthetic points inside real city bounding boxes) and delivery zones as polygons. The nearest warehouse per customer is found with KNN <-> on a GiST index and compared with a full distance sort. ST_DWithin 5 km is run in geometry SRID 4326 (degrees, the wrong answer), in geography, and in a projected metric SRID, with the error quantified. Point-in-polygon with ST_Contains assigns zones. ST_Subdivide on a large zone changes join time. The part also measures index size and build time, and a spatial join of 100,000 points to 50 zones.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); PostGIS with GEOS/PROJ built into a user prefix; ladder E1–E4; no access needed unless the user-space build fails; then raise one request for the -dev packages. Builds PostGIS against the 18.x lab and uses shopgen's geo mode. step 1: reproduce. step 2: the degrees-as-metres bug. step 3: pick types, SRID and index for three queries; check.py scores correctness and latency.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgis tutorial; postgis nearest neighbor; geometry vs geography postgis; st_dwithin; postgis spatial index

### Part 38 — Time Series on PostgreSQL: Partitions, BRIN, TimescaleDB and Rollups

- **Slug:** postgresql-time-series-partitions-brin-timescaledb · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How do you ingest, query, roll up and expire high-volume timestamped data in PostgreSQL, and when do you need an extension for it?
- **Assumes:** Part 30 — range partitioning and retention by partition.
- **Hands off:** Moving old data to object storage goes to Part 41. Dedicated time-series and columnar engines go to the other-engines sibling.
- **Worked example:** 50,000,000 clickstream events (30 days with a daily cycle) are ingested with COPY into four layouts: a plain table with a B-tree; a plain table with BRIN; daily partitions with BRIN managed by pg_partman; and a TimescaleDB hypertable with compression. Each layout is measured for ingest rate, size and three dashboard queries (last hour per product, daily uniques, a 7-day moving average). A materialized view with REFRESH CONCURRENTLY is compared with a continuous aggregate, and compression ratio with query speed. Also covered: retention by dropping partitions or chunks, date_bin vs time_bucket with gap filling, and late-arriving events.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); TimescaleDB built with pip-installed cmake; ladder E1–E4; no access needed. An event generator at scale, the four layouts, and the dashboard queries. step 1: reproduce. step 2: BRIN after out-of-order ingest. step 3: a layout for stated ingest, retention and dashboards; check.py scores ingest, size and latency.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres time series; timescaledb vs postgres partitioning; brin index time series; continuous aggregates postgres; postgres retention policy

### Part 39 — Change Data Capture: Streaming Changes Out of PostgreSQL

- **Slug:** postgresql-change-data-capture-outbox · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** How do you stream every committed change out of PostgreSQL to other systems reliably, and what can the slot that feeds it do to the primary?
- **Assumes:** Part 24 — replication slots and pgoutput.
- **Hands off:** Kafka, Flink and downstream processing go to the big-data sibling; landing changes in a lake goes to Part 41.
- **Worked example:** Changes to orders are consumed three ways: a Python consumer of about 100 lines reading pgoutput over the replication protocol, writing to a file sink and confirming its flush LSN; wal2json output; and, optionally, Debezium into a local Kafka (JDK and Kafka in KRaft mode from tarballs). The transactional outbox table is compared with dual writes by crashing between the database commit and the message send. At-least-once delivery produces a duplicate when a consumer restarts before acknowledging, and an idempotent consumer handles it. A stalled consumer fills pg_wal until max_slot_wal_keep_size invalidates the slot. An initial snapshot is joined to the stream with an exported snapshot, and a schema change happens mid-stream. The post closes on LISTEN/NOTIFY and why it is not CDC.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); Debezium and Kafka 4.x (KRaft) from tarballs with a JDK tarball; ladder E1–E4; no access needed. A consumer, a crash injector and a duplicate detector. step 1: reproduce. step 2: the slot that eats the disk; the growth is measured, and disk-full is modelled unless a user-space size cap exists. step 3: an outbox design with exactly-once effects; check.py kills the consumer 20 times at random and verifies the sink.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres cdc; debezium postgres; outbox pattern postgres; replication slot disk full; wal2json

### Part 40 — Analytics in PostgreSQL: Columnar Storage, DuckDB Inside and Materialized Views

- **Slug:** postgresql-analytics-columnar · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** How far can PostgreSQL go as an analytics engine, and what do columnar storage and vectorized execution change?
- **Assumes:** Part 15 — hash aggregate and parallel workers.
- **Hands off:** Warehouses and lakehouses to `data-at-scale`; DuckDB and ClickHouse internals to `database-engines`.
- **Worked example:** A star schema over Part 30's 24,000,000 orders. A revenue rollup run on heap with 1 and with 8 workers, on a Citus columnar table, through pg_duckdb, and from a materialized view refreshed CONCURRENTLY. Record bytes read, time and compression for each. Draw row and column layout from the actual files, and give the point at which to hand off to a warehouse.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); pg_duckdb and Citus columnar built in user space; ladder E1–E5; no access needed. pg_duckdb is a C++ build with cmake and ninja from pip. Citus columnar comes from Part 42.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres analytics performance; pg_duckdb; postgres columnar storage; refresh materialized view concurrently

### Part 41 — PostgreSQL and the Lake: Foreign Data Wrappers, Parquet and Iceberg

- **Slug:** postgresql-data-lake-fdw-parquet-iceberg · **Arc:** PostgreSQL as a data platform · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** How does PostgreSQL read from and write to other databases and object-storage files, and where should that boundary sit?
- **Assumes:** Part 30 — detaching a cold partition.
- **Hands off:** Parquet encoding, Iceberg metadata internals, Spark and Trino go to the big-data sibling; DuckDB's engine goes to the other-engines sibling.
- **Worked example:** postgres_fdw connects to a second cluster: a join pushed down vs pulled (Remote SQL in EXPLAIN VERBOSE), fetch_size, and async append. file_fdw reads a CSV feed. Orders older than 12 months, held in a detached partition, are exported to Parquet on a local MinIO and compared with their heap size. The same data is queried back from PostgreSQL through an FDW or extension, and from the DuckDB CLI. An Iceberg table is written and read via whichever route supports 18 at research time (DuckDB's Iceberg support or a PostgreSQL lake extension), with licences checked. 'Revenue per month for 2024' is timed on heap vs Parquet. The post ends with the decision of what stays in PostgreSQL.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); local MinIO static binary, pg_lake / FDWs built in user space; ladder E1–E5; no access needed. Two clusters, MinIO and DuckDB, with export and query scripts. step 1: reproduce. step 2: an FDW join that pulls 1,000,000 rows across. step 3: a tiering plan for stated query patterns; check.py measures cost and correctness.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres parquet; postgres iceberg; postgres_fdw pushdown; postgres data lake; export postgres to s3

### Part 42 — Sharding PostgreSQL with Citus

- **Slug:** postgresql-sharding-citus · **Arc:** The fleet: scale out and automate · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** How do you spread one logical database over many nodes, which key do you shard on, and which queries stop being cheap?
- **Assumes:** Part 30 — hash partitioning and partition keys.
- **Hands off:** Consensus-per-range distributed SQL (Spanner, CockroachDB, YugabyteDB) goes to the other-engines sibling; operating the shard fleet goes to Part 44.
- **Worked example:** A coordinator and 3 workers (4 clusters on one machine) hold the shop at 100,000,000 orders, distributed three ways: by customer_id, by order_id, and by seller_id (the tenant). The lab compares orders ⋈ order_items co-located on one shard with a repartition join, sets up products as a reference table, and times router queries against multi-shard fan-out. A cross-shard transaction commits with two-phase commit, a worker is killed mid-commit, and pg_dist_transaction drives the recovery. An online shard rebalance runs under pgbench, one hot seller is isolated to its own shard, and a distributed deadlock is detected. The post lists what stops working: some foreign keys, and global uniqueness off the distribution column. Caveat: all nodes share 16 CPUs and 14 GiB, so the post shows mechanism and relative cost, not scale-out throughput.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); Citus coordinator and two workers on one host; ladder E1–E5; optional AR-04 (four small VMs for one day); if declined, distributed-plan mechanics measured on one host, scale-out throughput documented. A four-node builder with small shared_buffers, plus distribution scripts and fault injection. step 1: reproduce. step 2: a distribution key that turns every query into a fan-out. step 3: choose the key and the reference tables for a workload; check.py scores the single-shard fraction and latency.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** citus sharding; postgres sharding; distribution column citus; citus vs partitioning; distributed postgres

### Part 43 — Managed PostgreSQL: What RDS, Aurora, Cloud SQL and Neon Change

- **Slug:** managed-postgresql-rds-aurora-cloud-sql-neon · **Arc:** The fleet: scale out and automate · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 10
- **Answers:** What does a managed service take off your hands, what does it take away, and which of this series' decisions are still yours?
- **Assumes:** Part 3 — #crash-recovery-archiving-and-replicas-three-readers-of-one-log.
- **Hands off:** Storage-engine comparisons beyond the WAL-into-storage idea go to the other-engines sibling; running your own fleet goes to Part 44.
- **Worked example:** The series' operations checklist (from Parts 11–32) is mapped row by row to what each service does. A local emulation runs the shop as a non-superuser admin holding pg_monitor, pg_maintain (17), pg_read_all_stats and pg_signal_backend. That admin attempts 12 operations a DBA expects, including ALTER SYSTEM, an untrusted extension, COPY FROM PROGRAM, pg_read_server_files, terminating another role's session and changing shared_buffers. The lab records which succeed and which fail, and compares the result with each vendor's documented admin-role model. Aurora's and Neon's architectures are drawn as Part 3's WAL moved into a storage service (quorum writes; pageserver and safekeepers). Failover and replica-lag semantics come from dated vendor documentation, and a cost worksheet prices the shop at 10,000,000 orders from dated public pricing. A Tier B harness is provided for a real instance.
- **Lab:** G2 emulation of the managed patterns; G3 · needs a cloud sandbox for real-service numbers; ladder E1–E4; optional AR-05; if declined, every managed-service number is documented with its source date. A privilege-probe script and the cost worksheet, plus a Tier B harness with an empty results schema. step 1: reproduce the probe table. step 2: a migration that needs superuser. step 3: choose self-managed vs managed for a stated team and budget, graded against a rubric.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** rds vs aurora postgres; aurora postgres architecture; neon serverless postgres architecture; managed postgres limitations; rds_superuser

### Part 44 — PostgreSQL as Code: Roles, Configuration and Drift with OpenTofu and Ansible

- **Slug:** postgresql-infrastructure-as-code · **Arc:** The fleet: scale out and automate · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** How do you manage a fleet's roles, grants, databases and settings declaratively, and catch drift?
- **Assumes:** Part 12 — role design and default privileges.
- **Hands off:** Kubernetes to 32; schema migrations to 28.
- **Worked example:** Part 12's three roles, two databases, extensions and 12 settings declared in OpenTofu (postgresql provider) and in Ansible, planned and applied to two local clusters. A GRANT made by hand, detected as drift and reverted. Password rotation by swapping between two roles with no downtime. Settings that need a reload told apart from those that need a restart, using pg_settings.context.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); OpenTofu static binary and Ansible in a uv venv, two local clusters; ladder E1–E4; no access needed. OpenTofu as a static binary plus a provider download; Ansible in a uv venv.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** terraform postgresql provider; ansible postgresql; manage postgres roles as code

### Part 45 — PostgreSQL on Kubernetes with CloudNativePG

- **Slug:** postgresql-kubernetes-cloudnativepg · **Arc:** The fleet: scale out and automate · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** What does an operator do that Patroni does not, and should your database run on Kubernetes?
- **Assumes:** Part 23 — Patroni's failover decisions, as the baseline the operator is compared with.
- **Hands off:** Managed services to 43.
- **Worked example:** A 3-instance CloudNativePG cluster in kind (shared_buffers 128 MB). Delete the primary pod and measure failover time against Part 23's Patroni numbers. A switchover; continuous backup to local MinIO and a PITR into a new cluster; a rolling minor upgrade; a lost PVC re-cloned. The reconcile loop traced through the operator's events.
- **Lab:** G3 · needs a container runtime for kind; ladder E1–E5; AR-01 (required for measured numbers); if declined, manifests and harness ship unrun with an empty results schema, and a labelled model of the reconcile loop carries the worked example. If access is declined, the manifests and harness ship unrun, labelled, following the NVIDIA-series Tier B pattern.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** cloudnativepg tutorial; postgres on kubernetes; postgres operator

### Part 46 — PostgreSQL Incidents: A Triage Method and Runbooks as Code

- **Slug:** postgresql-incident-triage-runbooks · **Arc:** The fleet: scale out and automate · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** When production PostgreSQL is on fire, what do you look at first, second and third, and how do you encode that so the next person doesn't need you?
- **Assumes:** Part 28 — wait events and alert rules.
- **Hands off:** Each incident links to the part that owns its mechanism.
- **Worked example:** Five incidents injected into the lab one at a time: a connection storm, an idle-in-transaction session holding the horizon, a lock queue behind DDL, an abandoned slot retaining WAL, and a checkpoint storm. Each is triaged with the same five queries. Then encode the method as an executable runbook (gather evidence, propose an action, wait for a human to confirm) and test it against each injection.
- **Lab:** G2 · local service (the PostgreSQL 18 lab); ladder E1–E4; no access needed. The disk is never filled; WAL retention is measured in bytes against thresholds.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** postgres troubleshooting; postgres high cpu; too many connections; postgres wal disk full slot

## Publication order and cadence

1. **Finish the layer trilogy first.** Publish Part 2, then Part 3 (Part 3 links Part 2's vacuum and
   checkpointer anchors). Before Part 3 is uploaded, decide the two sentences under *Published
   promises* below.
2. **Then the on-ramp, 4 → 10,** because every later arc assumes a reader who can write the query.
3. **Then in position order.** The rule that makes skipping safe: a part may publish as soon as the
   one part it names under **Assumes** is live, since its links go to published URLs. So the
   Staying-up arc (21–27) can run in parallel with the slow-query arc (13–17) once Part 3 is live.
4. Cadence: one L4 part every two weeks, or one L2/L3 part a week. At that rate the series takes
   about 18 months; Parts 4–32 (the core engineer) are about 11 months.

## Cross-links

- Every part links back to the one part it assumes, at the anchor named above, by canonical URL
  `https://canery.in/blogs/<slug>#<github-anchor>`. Anchors of Parts 4+ are fixed when each is drafted
  and recorded in `context.md`.
- Earlier published parts are **never** edited to add forward links; the platform's series index and
  the series description carry the reading paths.
- A bridge to a sibling series is added only when the sibling part is live, in the later part.

## Lab policy

Graded per blog-forge `references/labs.md` (grades G0–G3, exercise ladder E1–E5). The probe and all
access requests are in `access.md`.

- **Two labs, never mixed.** Parts 1–3 keep the PostgreSQL **16.2** pgserver lab at
  `~/.cache/blog-pg-lab/` exactly as captured. Every new part runs on **PostgreSQL 18.x** (18.6 on
  2026-09-28, the current major) built from the release tarball into `~/.cache/blog-pg18-lab/` (on
  disk, own ports and socket directory). A source build brings the contrib modules the wheel lacks
  (`pg_stat_statements`, `auto_explain`, `amcheck`, `postgres_fdw`, `pg_trgm`, …). No new lab
  connects to or changes the 16.2 server.
- **Same tables.** The shop tables `customers` and `orders` are regenerated on 18 by the same
  generator, so the numbers line up with Parts 1–3; parts that need scale grow `orders` explicitly
  and say by how much. Page counts are re-captured on 18 (checksums are on by default there).
- **PostgreSQL 19** was at beta 4 on 2026-09-24 with GA planned for October 2026. Pin the version at
  each part's research time with a dated source; do not switch mid-arc; name 19 deltas inline.
  Part 25 (upgrades) upgrades a *copy* of the 16.2 lab to 18 as its worked example.
- **Grades.** Every new part is **G2** (a disposable local PostgreSQL server) unless its Lab line says
  otherwise. Everything a part needs that can be built in user space is self-provisioned (libevent,
  libyaml, GEOS/PROJ, etcd, MinIO, Prometheus, a JDK, Kafka, cmake from pip) and recorded in
  `access.md`, never asked for.
- **Ladder.** L2 ships E1–E3, L3 ships E1–E4, L4 ships E1–E5, each with a self-check and an answer
  from the author's own run. E4 faults are injected only into the disposable environment.
- **Step sketches.** The numbered steps on each part's Lab line are the planners' first sketch; the
  part's outline maps them onto E1–E5 with self-checks.
- **Downloads.** Each part ships per-file `LAB_XX` downloads plus the whole-lab `lab-<slug>.zip`.
- **Safety.** Never `pkill -f`; check `postgresql.auto.conf` before and after every run; no subagent
  touches a lab server.

### Access requests (answer each: `grant`, `decline` or `later`)

| ID | Need | Parts | If declined |
|---|---|---|---|
| AR-01 | a container runtime (docker group membership or rootless podman) so `kind` can run | 45 (also *data-at-scale* 8, 10, 21) | the operator part ships its manifests and harness unrun, with a labelled model of the reconcile loop |
| AR-02 | real network partitions: root for `tc netem`, or three small VMs for a day | 23 (optional) | failover is shown with one-host faults only (kill -9, SIGSTOP), and the post says what that cannot show |
| AR-03 | one sudo session for sysctls (huge pages, `vm.*`, `kernel.perf_event_paranoid`) | 28, 32 (optional) | those settings are documented, not measured |
| AR-04 | four small VMs for one day | 42 (optional) | Citus mechanics measured on one host; scale-out throughput documented |
| AR-05 | a cloud sandbox with a spend cap (one small managed PostgreSQL) | 43 (optional) | managed-service numbers documented with dated sources |

## Published promises, and the two sentences to decide

- **Part 1 (live):** "This is the first of three posts, one per layer" stays true — Parts 1–3 are
  the three layer posts. Not edited.
- **Part 3 (not uploaded):** two sentences contradict an extended series and should change before
  upload (owner's call; not edited by the plan):
  - "This is the third and last post" → "This is the third and last of the three layer posts".
  - Limitations: "What this post, and the series, does not cover … Each is its own series." →
    "What this post does not cover … Later parts of this series take these up." (no forward links).
- **Part 2:** needs no change.

## Open decisions for the owner

1. Approve the 46-part cut (or name parts to drop; 33–46 can be reordered freely).
2. Answer AR-01 … AR-05.
3. The two Part 3 sentences above.
4. The platform display title (optional).
5. Whether `data-at-scale` and `database-engines` start after this series' core (Part 32) or interleave.

## What this series will not cover

Hadoop, Spark, open table formats, streaming platforms and orchestration (→ `data-at-scale`); other
engines' internals (→ `database-engines`); DBMS kernel development and core patches; administering
proprietary engines (Oracle, SQL Server, Db2); ML modelling and BI tooling.
