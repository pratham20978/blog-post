# Series context — PostgreSQL Foundations

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** from a reader who has never written SQL (Parts 4–7) to engineers who run a
  PostgreSQL fleet. Parts 1–3 are L4, intermediate; every later part carries its own tier and
  difficulty in `plan.md` (extended 2026-09-29 to 46 parts; Checkpoint S not yet passed).
- **Shape:** hybrid — Parts 1–3 are the sibling layer posts (the *Internals* arc); 4 → 5 → 6 is the
  from-scratch ladder; every later part is a spoke that names at most one earlier part. The three
  layer posts open with the same three-layer paragraph and Figure 1; later parts do not reuse it.
- **Shared promise:** after the series a reader can build, operate, scale and automate a
  PostgreSQL system to industry grade, and explain any surprise by naming the mechanism and the
  number that proves it.
- **Terminology and notation:** "memory layer / process layer / storage layer", always those
  words. "Shared buffers", "WAL buffers", "local memory" for the three pools. Sizes in 8 KB pages
  with the byte figure alongside.
- **Recurring lab:** G2 (`access.md`). Parts 1–3: PostgreSQL 16.2 at `~/.cache/blog-pg-lab`;
  parts 4+: 18.6 built from source at `~/.cache/blog-pg18-lab/`; never mix them. `customers` 710
  pages, `orders` 7,693. Every server number comes from the part's own `lab/captures.md`;
  version deltas are named inline.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | postgresql-foundations-memory-layer | published | what is in RAM and what decides what stays | pools, clock sweep, rings, WAL-before-data, `pd_lsn` |
| 2 | postgresql-foundations-process-layer | published | which process does the work, and who waits on whom | the process cast; vacuum decides and does, but its page-level effects are deferred |
| 3 | postgresql-foundations-storage-layer | ready, **not published** (gate PASS 2026-09-24) | what is on disk, byte by byte, and how it survives a crash | closes the layer trilogy; later parts link its anchors |
| 4 | what-is-a-relational-database-postgresql | ready, **not published** (gate + `--social` PASS 2026-10-01) | the from-scratch entry: relations, the query path, two surprises | query path at `#what-happens-between-the-query-and-the-rows`; the missing key for part 7 |
| 5 | sql-select-evaluation-joins-group-by-null | ready, **not published** (gate + `--social` PASS 2026-10-02) | the logical order of a SELECT; joins, grouping and NULL | order table in *The problem*; NOT IN at `#why-does-not-in-return-nothing-once-a-null-appears` |
| 6–46 | see `plan.md` | planned | one question each, listed in `plan.md` | — |

## Knowledge established

### Part 1 — How PostgreSQL Uses Memory

- Three pools (shared buffers, WAL buffers, local memory) plus the kernel page cache.
- Clock sweep over usage counts 0–5; a big scan uses a 32-buffer ring (`pg_stat_io.reuses`).
- WAL before data, by `pd_lsn`; the first change after a checkpoint logs a full page (a two-byte
  update cost 7,544 bytes).
- `work_mem` is per operation, per process, times parallel workers.

### Part 2 — How PostgreSQL Uses Processes

- Only the postmaster forks, and it never touches data, so it can reset all after a crash.
- Checkpointer makes WAL forgettable; backends still write pages; `synchronous_commit = off`
  made commits 16× faster with no corruption risk.
- Autovacuum workers share one cost budget; index passes = ⌈dead × 6 B / `maintenance_work_mem`⌉
  (1 vs 5 on the same delete).
- An idle transaction holds the xmin horizon; parallel workers come from a shared pool.

### Part 3 — How PostgreSQL Stores Data

- On disk: 8 KB pages of data, maps (VM, FSM) and the log; each page carries its last LSN.
- Row 4242 at ctid `(32,82)` decoded byte by byte (a ctid names a line pointer).
- First update at fillfactor 100 not HOT (5 records, 322 B); the next, with room, HOT (2, 111 B).
- Vacuum read 2 of 7,693 pages via the VM; an index-only scan went 0 → 102,000 heap fetches when
  the VM was cleared.
- TOAST past a 2,032-byte row; B-tree lookup of customer 92399 via pages 290 → 860 → 1068.
- LSN → segment file and byte, CRC-32C recomputed; after an immediate stop, redo from the REDO
  point caught the page up. Recovery is redo-only (no undo) because of the no-overwrite heap.

### Part 4 — What a Relational Database Actually Does

- A table without a key is a bag: a copy of order 4242 moved JP's revenue by 56,954 cents; the
  key is refused while the copy exists, then refuses it.
- Parser (grammar, then names), rewriter, planner (hash join 2.27× cheaper than the next plan),
  executor; System R (1979) had code generation instead of rewrite.
- NULL: `count(*)` 1,000,000 vs `count(amount_cents)` 999,999; `= NULL` matches 0 rows.
- The catalog describes itself (`pg_class` has a row for `pg_class`).

### Part 5 — How a SELECT Is Evaluated: Joins, Grouping and NULL

- Logical order (PG's SELECT reference): FROM, WHERE, GROUP BY/HAVING, SELECT, DISTINCT, set ops,
  ORDER BY, LIMIT. It defines the result, not the work: a HAVING with no aggregate was moved into
  WHERE (identical plans), and PG computes the SELECT list after LIMIT where it can.
- Shop + `--orderless 1000`: 101,000 customers (717 pages). Join 1,000,000 → paid 333,333 → 5
  countries. IN and JP tie at 3,333,366,679 paid cents: LIMIT 2 gave DE, IN by default and DE, JP
  with parallel workers off (the groups reach the top-N sort in another order). WITH TIES: 3 rows.
- LEFT JOIN 1,001,000; with WHERE on orders 333,333 (the planner made it an inner join); the
  condition in ON 334,333.
- GROUP BY gives NULLs one group (20 groups after the left join, 5 NULL); DESC sorts NULL first,
  so `limit 5` returned the five empty groups.
- NOT IN vs NOT EXISTS: 1,000 each; after order 4242's customer_id became NULL, 0 vs 1,000.
  R = {1, NULL}, S = {NULL}: NOT IN ∅, NOT EXISTS {1, NULL}, EXCEPT {1}. Contested: Rubinson 2007
  against Date and Grant 2008; Libkin's certain answers. All four critiques read via sigmodrecord.org.
- NOT IN over 1,000,000 rows is not hashable at default `work_mem` (rows × 32 B > 4 MB × 2):
  117.5 s against 46 ms for NOT EXISTS; hashed at 64 MB, 192 ms. PG 19 (beta) turns NOT IN into an
  anti-join when no NULL is possible. Measuring this belongs to the slow-query part.
- Fan-out: join 333,333 rows (66,667 × 3 + 33,333 × 4) vs EXISTS/IN 100,000 (the plan dedupes
  customer ids first); two joins to orders 1,099,998 rows, totals × 3.3, FILTER repairs it.
  UNION ALL 666,666 vs UNION 100,000; UNION keeps one NULL.

## Decisions to preserve

- **No body H1.** The page shell renders the title; the validator fails one.
- Cover grid fixed by Parts 1–2: title block at x=560, motif on the left. Motifs so far: a band
  of tiles (3); two tile grids, one doubled tangerine row, four dots (4); tile rows narrowing to a
  tangerine tie, eight dots (5).
- Figure toolchain is copied into each part's `assets/` (`_build.py`, figure scripts, `_cover.py`,
  `_social.py`; part 4: `_figs.py` placed, `_fig04.py` + `.mmd` mermaid); object keys suffixed with
  the slug; headless Chrome with absolute paths.
- **`shopgen.py`** (part 4; `--scale S|M|L`, `--indexes`, refuses a database it did not create;
  part 5 added `--orderless N`). Copy the latest part's copy and extend it; scale M stays
  byte-for-byte. **Quirk:** all 10 orders of a customer share one amount (37 × 100,000 ≡ 0 mod
  100,000), so per-customer running totals rise in equal steps.
- **NOT IN at scale M takes ~2 minutes at default settings:** run it at most twice, timed; raise
  `work_mem` per session for the rest (part 5's runner does).
- **One psql call is one session:** a `SET` must travel in the same call as the statement it
  changes. Part 4's `captures.md` step 3 printed the wrong plan because of this.
- **Cross-part links (part 4 on): name the earlier post, never its URL;** the owner adds links
  (2026-10-01). Name published parts, plus the one part a post assumes (part 5 names unpublished
  part 4, so 4 must go live first); list each in the manifest's *Series links to add*. Later parts
  are "later in this series", never a number or title. Never edit a published part.
- **Labs run on a temporary cluster, deleted after capture** (owner, 2026-10-01): `initdb`, run,
  save the captures, stop, delete the data directory. PG 18.6 binaries stay at
  `~/.cache/blog-pg18-lab/pginstall` (40 MB). Provision versions yourself; Docker is unusable
  (AR-01), so ask before planning on it.
- Ledger keys are HTML comments; keep `blog.md.bak` and diff before the gate.
- Intended gate warnings: figure count above the L4 band, words above 10,000; part 4's length.
- Part 3's `run_lab.py` checkpoints before the load and must not scan `orders` between the
  crash-step update and the crash (the clock sweep can write the page out).
- Ledger format from part 3 on: Venue/Year/Identifier/Status columns and a `## Search log`.
  Reachable: Crossref, OpenAlex, arXiv, Google Scholar, vldb.org, sigmodrecord.org, LIPIcs. Blocked:
  DBLP and HAL (bot walls), Semantic Scholar (429), ACM DL and Edinburgh/TU/e repositories (403).

## Open threads

- **Part 1's local `blog.md` lost every claim key** (109 survive in `blog.md.bak`) and its manifest
  names the wrong lab file; restore from the `.bak` before any re-publish.
- **Parts 1 and 2 are live; part 3 is not published** (owner, 2026-10-01). Part 3's links to
  part 2's anchors are therefore safe. Until part 3 is live, no later part may name it as a
  place to read more.
- Part 3: gate-PASS, assets await upload (`urls.txt` pre-filled).
- **Part 4 before upload:** one temporary-cluster run to regenerate `lab/captures.md` (step 3
  printed the chosen plan; the code is fixed) needs the owner's go-ahead; then upload and wrap two
  titles.
- **Pending since 2026-09-29:** Checkpoint S (the 46-part cut); AR-01…AR-05 in `access.md`; part 3's
  "third and last post" and "Each is its own series" contradict the extension — owner's call.
- **Part 5 before upload:** part 4 goes live first. Then upload 10 figures, the cover, 8 lab files
  and `lab-sql-select-evaluation-joins-group-by-null.zip` (`urls.txt` pre-filled) and wrap three
  titles. Checkpoints A and B were not held (owner asked for the whole post); review the outline
  and ledger at Checkpoint C.
- Sibling series `data-at-scale` and `database-engines`: add a bridge only once its part is live.

## Next part brief

- **Part:** 6 — *Window Functions, CTEs, LATERAL and Recursive Queries*
  (`postgresql-window-functions-cte-lateral-recursive`), L3, intermediate.
- **Can assume:** part 5, named by title (*How a SELECT Is Evaluated: Joins, Grouping and NULL*):
  its logical-order table in *The problem*. Window functions run after HAVING and before DISTINCT
  and ORDER BY (SELECT reference); place them in that table rather than re-teaching it.
- **Must teach (plan):** frames ROWS/RANGE/GROUPS on tied timestamps; top-3 per customer with
  ROW_NUMBER vs LATERAL … LIMIT 3; gaps and islands on a 1,000,000-event clickstream; WITH
  RECURSIVE with SEARCH and CYCLE on a ~1,000-node tree with one injected cycle; GROUPING SETS and
  ROLLUP; a CTE MATERIALIZED vs NOT MATERIALIZED.
- **Must not repeat:** the clause order, ties at LIMIT, NULLS FIRST, NOT IN, fan-out — one
  sentence and the part 5 name each.
- **Evidence:** copy part 5's `shopgen.py`; add the events and categories tables as new options.
  Mind the amount quirk above before choosing a running-total example. Temporary cluster, deleted
  after capture.
- **Handoff:** sort and hash costs to the executor part; indexes for top-N to the B-tree part.
