# Source ledger — what-is-a-relational-database-postgresql

Research ran 2026-10-01. Every server-side number comes from one run of `lab/run_lab.py`
(PostgreSQL 18.6 built from the official source release, default `postgresql.conf`, captured in
`lab/captures.md` and `lab/captures.json`, run 2026-10-01T09:50:49Z). Documentation claims were
checked against the PostgreSQL 18 documentation at the URLs below; version-delta claims were
checked against `doc/src/sgml/release-18.sgml` in the 18.6 release tarball, whose sha256 was
verified against the published checksum. Every paper claim was checked against the full text of a
copy we fetched and read, not against an abstract or a search snippet.

Three things research changed about the plan:

- The plan's lab line assumed the PostgreSQL 18 lab existed. It did not. It was built for this
  part (source build, because the 18.x tarball ships no pre-generated parser and needed bison and
  flex staged under `$HOME`), and `customers` and `orders` came out at **710 and 7,693 pages**,
  identical to the 16.2 figures parts 1–3 published. The series' numbers survive the version
  change, and the post can say so as a measured fact.
- The four-stage lifecycle is not a PostgreSQL invention to be presented as such. Selinger et al.
  stated it for System R in 1979 (L08), and their four phases are *not* PostgreSQL's four: System R
  had code generation where PostgreSQL has a rewrite stage. That difference is worth the post's
  time and was not in the plan.
- The plan framed duplicate rows as a SQL-versus-Codd disagreement. The 1974 SEQUEL paper shows it
  was a live design question at the start, and that SEQUEL's own default was the *opposite* of
  SQL's today (L06). The post uses the primary source rather than the later critiques.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Codd, E. F. "A Relational Model of Data for Large Shared Data Banks" | Communications of the ACM 13(6), pp. 377–387 | 1970 | 10.1145/362384.362685 | peer-reviewed | https://www.engineering.upenn.edu/~zives/03f/cis550/codd.pdf | 2026-10-01 |
| S2 | T1 | Chamberlin, D. D., Boyce, R. F. "SEQUEL: A Structured English Query Language" | Proc. 1974 ACM SIGFIDET (now SIGMOD) Workshop, pp. 249–264 | 1974 | 10.1145/800296.811515 | peer-reviewed | https://rebelsky.cs.grinnell.edu/Courses/CS302/2006S/Readings/sequel.pdf | 2026-10-01 |
| S3 | T1 | Selinger, P. G., Astrahan, M. M., Chamberlin, D. D., Lorie, R. A., Price, T. G. "Access Path Selection in a Relational Database Management System" | Proc. 1979 ACM SIGMOD, pp. 23–34 | 1979 | 10.1145/582095.582099 | peer-reviewed | https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf | 2026-10-01 |
| S4 | T1 | Stonebraker, M., Pavlo, A. "What Goes Around Comes Around... And Around..." | ACM SIGMOD Record 53(2), pp. 21–37 | 2024 | 10.1145/3685980.3685984 | peer-reviewed | https://db.cs.cmu.edu/papers/2024/whatgoesaround-sigmodrec2024.pdf | 2026-10-01 |
| S5 | T2 | PostgreSQL 18 docs, ch. 51 Overview of PostgreSQL Internals (§51.1 The Path of a Query, §51.3 Parser Stage, §51.4 Rule System, §51.5 Planner/Optimizer, §51.6 Executor) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/query-path.html | 2026-10-01 |
| S6 | T2 | PostgreSQL 18 docs, §14.1 Using EXPLAIN | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/using-explain.html | 2026-10-01 |
| S7 | T2 | PostgreSQL 18 docs, §9.21 Aggregate Functions | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/functions-aggregate.html | 2026-10-01 |
| S8 | T2 | PostgreSQL 18 docs, §52.11 pg_class | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/catalog-pg-class.html | 2026-10-01 |
| S9 | T2 | PostgreSQL 18 docs, §52.7 pg_attribute | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/catalog-pg-attribute.html | 2026-10-01 |
| S10 | T2 | PostgreSQL 18 docs, §5.5 Constraints (§5.5.3 Unique, §5.5.4 Primary Keys) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/ddl-constraints.html | 2026-10-01 |
| S11 | T2 | PostgreSQL 18 docs, Appendix D SQL Conformance | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/features.html | 2026-10-01 |
| S12 | T2 | PostgreSQL 18 docs, Appendix E.6 Release 18 (released 2025-09-25): §E.6.3.2.1 Constraints, §E.6.3.2.3 EXPLAIN. First read in `doc/src/sgml/release-18.sgml` of the verified 18.6 tarball, then confirmed on the public page | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/release-18.html | 2026-10-01 |
| S13 | T3 | This post's lab: `lab/run_lab.py` and `lab/shopgen.py`, captures of 2026-10-01 | — | 2026 | lab/captures.json | source | (downloadable lab) | 2026-10-01 |
| S14 | T2 | PostgreSQL 18 docs, §51.5 Planner/Optimizer (§51.5.1 Generating Possible Plans) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/planner-optimizer.html | 2026-10-01 |
| S15 | T2 | PostgreSQL 18 docs, §9.1 Logical Operators | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/functions-logical.html | 2026-10-01 |
| S16 | T2 | PostgreSQL 18 docs, §9.2 Comparison Functions and Operators | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/functions-comparison.html | 2026-10-01 |
| S17 | T2 | PostgreSQL 18 docs, §7.2.2 The WHERE Clause | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/queries-table-expressions.html | 2026-10-01 |
| S18 | T2 | PostgreSQL 18 docs, §51.3 The Parser Stage (§51.3.1 Parser, §51.3.2 Transformation Process) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/18/parser-stage.html | 2026-10-01 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Crossref | bibliographic: "A Relational Model of Data for Large Shared Data Banks" | only the 2002/2001 book-chapter reprints; the CACM original needed a direct DOI lookup |
| 2 | 1 | Crossref | DOI 10.1145/362384.362685 | confirmed CACM 13(6):377–387, June 1970, Codd — the citation the post uses |
| 3 | 1 | OpenAlex | works/doi:10.1145/362384.362685 | 5,338 citations; OA copy only at dl.acm.org, which refuses automated fetches (403) |
| 4 | 1 | Crossref | bibliographic: "Architecture of a Database System Hellerstein" | 10.1561/1900000002 (FnT in Databases, 2007); every open mirror we tried was unreachable, so it is not cited |
| 5 | 1 | Crossref | bibliographic: "Access Path Selection in a Relational Database Management System" | 10.1145/582095.582099, SIGMOD '79 — the planner source |
| 6 | 1 | Crossref | bibliographic + DOI: "SEQUEL: A Structured English Query Language" | 10.1145/800296.811515; Crossref labels the proceedings 1976, which is wrong |
| 7 | 1 | Google Scholar (web) | Chamberlin Boyce "SEQUEL" SIGFIDET 1974 proceedings pages | settled the venue as SIGFIDET '74, pp. 249–264, against Crossref's 1976 label; also surfaced Chamberlin's CACM 2024 retrospective |
| 8 | 1 | Crossref | DOI 10.1145/320455.320457 | System R (Astrahan et al.), TODS 1(2):97–137, 1976 — located, but every copy found is a scan with no text layer, so no claim rests on it |
| 9 | 1 | Crossref | bibliographic: "What Goes Around Comes Around And Around Pavlo Stonebraker" | 10.1145/3685980.3685984, SIGMOD Record 53(2):21–37, 2024 |
| 10 | 1 | Crossref | bibliographic: "Codd Relational Completeness of Data Base Sublanguages" | not indexed (it is a 1972 Courant symposium chapter); dropped rather than cited unread |
| 11 | 4 | Crossref | bibliographic: "A critique of the SQL database language Date" | Date 1984, SIGMOD Record 14(3):8–54, 10.1145/984549.984551 — located, full text only behind ACM; see Open questions |
| 12 | 4 | Crossref | bibliographic: "Nulls three-valued logic and ambiguity in SQL" | Rubinson 2007 (SIGMOD Record 36(4)) and Date's 2008 reply (37(3)) — the disagreement is real and documented; neither full text was reachable |
| 13 | 4 | Crossref | bibliographic: "On formal semantics of SQL nulls" | Guagliardo & Libkin 2019 (Information Systems 86:46–60); Libkin & Peterfreund 2023 (SIGMOD) |
| 14 | 1 | OpenAlex | OA status for nine candidate DOIs | told us which full texts were worth chasing; four of nine were reachable outside ACM |
| 15 | 2 | PostgreSQL 18 docs | ch. 51 Overview of PostgreSQL Internals, §51.1 The Path of a Query | the four stages, their exact names, and the view-rewriting sentence |
| 16 | 2 | PostgreSQL 18 docs | §14.1 Using EXPLAIN; §9.21 Aggregate Functions; §52.11 pg_class; §52.7 pg_attribute; §5.5 Constraints; App. D | the cost-number definitions, the two count() rows, relpages/reltuples caveats, attnum, the primary-key sentence, the conformance figure |
| 17 | 5 | PostgreSQL 18.6 source | grep EXPLAIN, pg_constraint, "not-null constraints" in release-18.sgml | three 18-specific deltas the post names inline (L27–L29) |
| 18 | 3 | Our lab | run_lab.py on PostgreSQL 18.6 | every server number; three runs (the second fixed a wrong explanatory note and a no-op SET; the third was the final end-to-end check and overwrote the captures). Every number in the post is from the third, the shipped captures. Data-derived values were identical in all three; planner costs moved by under 0.2% |
| 19 | 2 | PostgreSQL 18 docs | §51.5 Planner/Optimizer | the docs' own one-sentence descriptions of nested loop, merge and hash joins; the hash join sentence carries L48 |
| 20 | 2 | PostgreSQL 18 docs | §9.1 Logical Operators; §9.2 Comparison; §7.2.2 The WHERE Clause | the truth tables, the rule that `7 = NULL` is null, and the rule that WHERE discards false *and* null — the mechanism behind L40 |
| 21 | 2 | PostgreSQL 18 docs | §51.3 The Parser Stage | the raw parser makes no catalog lookups, and why: lookups need a transaction, and the server must first recognise BEGIN/ROLLBACK. Opposite to System R, where the optimizer did the name lookups (L09) |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | A relation on n sets is a set of n-tuples whose jth element comes from the jth set; equivalently, a subset of the Cartesian product. Codd calls the jth set the jth domain and n the degree | S1 §1.3 | Codd's own wording, including his footnote 1 |
| L02 | In Codd's array picture of a relation, the ordering of rows is immaterial and all rows are distinct | S1 §1.3, properties (2) and (3) | the array is "not an essential part of the relational view" — it is the picture, not the definition |
| L03 | Column order *is* significant in that array, and Codd proposes users instead deal with domain-unordered relationships, with role names where two domains are identical | S1 §1.3–1.4 | — |
| L04 | A primary key is a domain, or combination of domains, whose values uniquely identify each tuple of the relation | S1 §1.4 | Codd allows several candidate keys, one of which is "arbitrarily selected" as the primary key |
| L05 | Codd's opening problem is data independence: that application programs should survive changes in data representation. He names three dependencies to remove — ordering, indexing and access path | S1 §1.1–1.2 | — |
| L06 | SEQUEL's 1974 default was that duplicates are eliminated by a mapping, and preserved only when a mathematical function is applied to its result; the defaults could be overridden explicitly | S2 §(duplicates) | this is SEQUEL as proposed in 1974, not SQL as standardised |
| L07 | SEQUEL was presented as a sublanguage for both professional programmers and infrequent users, with power equivalent to first-order predicate calculus and without bound variables or quantifiers | S2 abstract | the equivalence is the authors' claim for SEQUEL as specified |
| L08 | System R subjected a SQL statement to four phases: parsing, optimization, code generation, and execution | S3 §2 | System R, 1979 — code generation is the phase PostgreSQL does not have |
| L09 | System R's optimizer looked the query's table and column names up in the catalogs, to verify they exist and to retrieve information about them | S3 §2 | — |
| L10 | Among the many possible choices, the System R optimizer chooses the one that minimises total access cost for the whole statement | S3 §1 | "total access cost" is the paper's term; how the cost is computed is part 14's subject |
| L11 | A user of System R did not have to state the access path or the join order; the optimizer chose both. System R was an experimental relational DBMS under development at IBM's San Jose laboratory since 1975 | S3 §1 | the non-procedural promise the post opens on |
| L12 | PostgreSQL's own description of a query's path has four stages: parser, rewrite system, planner/optimizer, executor | S5 §51.1 | PostgreSQL 18; the stage names are the documentation's |
| L13 | The rewrite system realises views: a query against a view is rewritten into one against the base tables in the view definition | S5 §51.1, §51.4 | — |
| L14 | The planner creates the possible paths to the same result, estimates each one's cost, and expands the cheapest into a plan for the executor | S5 §51.1, §51.5 | — |
| L15 | The executor recursively steps through the plan tree, retrieving rows in the way the plan represents | S5 §51.1, §51.6 | — |
| L16 | EXPLAIN's two cost figures per node are the estimated start-up cost (before the first row) and the estimated total cost (running the node to completion) | S6 §14.1 | — |
| L17 | The cost units are arbitrary, set by the planner's cost parameters; by convention `seq_page_cost` is 1.0 and the rest are relative to it | S6 §14.1 | — |
| L18 | EXPLAIN ANALYZE runs the query and reports actual time, actual rows and loops beside the estimates | S6 §14.1 | — |
| L19 | `count(*)` computes the number of input rows; `count(expression)` computes the number of input rows in which the expression is not null | S7 §9.21 | the documentation's own two table rows |
| L20 | Every aggregate except `count(*)` ignores null inputs rather than returning null | S7 §9.21 | `sum` over no non-null rows returns null, not zero |
| L21 | `pg_class` holds a row for every table and everything else that has columns; `relpages` and `reltuples` are planner estimates refreshed by VACUUM, ANALYZE and some DDL | S8 §52.11 | `reltuples` is −1 when the table has never been vacuumed or analyzed |
| L22 | `pg_attribute` holds one row per column of every table; ordinary columns are numbered from 1 up, and system columns such as `ctid` have negative `attnum` | S9 §52.7 | — |
| L23 | A primary key requires its columns to be unique and not null; a table may have at most one, and `UNIQUE NOT NULL` accepts the same data | S10 §5.5.4 | — |
| L24 | PostgreSQL's documentation states that relational theory requires every table to have a primary key, that PostgreSQL does not enforce this, and that it is usually best to follow it | S10 §5.5.4 | paraphrased; the post quotes at most the middle clause |
| L25 | In a unique constraint two nulls are not considered equal by default, so duplicate rows containing a null in a constrained column remain possible | S10 §5.5.3 | — |
| L26 | PostgreSQL aims at ISO/IEC 9075 and conforms to at least 170 of the 177 mandatory features of Core SQL:2023; no DBMS claims full Core conformance | S11 App. D | as documented for 18 |
| L27 | PostgreSQL 18 includes BUFFERS in EXPLAIN ANALYZE output by default | S12 §E.6.3.2.3 | on 16 and 17 you must ask for it |
| L28 | PostgreSQL 18 prints fractional row counts in EXPLAIN, to two decimal places | S12 §E.6.3.2.3 | hence `rows=5.00` in our captures |
| L29 | PostgreSQL 18 stores column NOT NULL specifications in `pg_constraint`, which lets them be named | S12 §E.6.3.2.1 | why five `contype = 'n'` rows appear in our catalog capture |
| L30 | The relational model remains the dominant data model and SQL has absorbed the good ideas of the approaches proposed to replace it; the authors expect that to continue | S4 abstract, §1, Conclusion | the authors' argument, stated as theirs |
| L31 | Lab: PostgreSQL 18.6, default `postgresql.conf` (`block_size` 8,192 bytes), 16 CPUs, 14 GB RAM, NVMe, locale C.UTF-8. `customers` 710 pages / 100,000 rows, `orders` 7,693 pages / 1,000,000 rows — the same page counts parts 1–3 captured on 16.2 | S13 §1 | run 2026-10-01; shopgen scale M |
| L32 | Lab: `customers` has 3 columns and `orders` 5 in `pg_class.relnatts`; `pg_class` itself has 34 and `pg_attribute` 25 | S13 §1 | PostgreSQL 18.6 catalog shape |
| L33 | Lab: revenue per country for paid orders is DE 3,333,366,716 · IN 3,333,366,679 · JP 3,333,366,679 · BR 3,333,266,642 · US 3,333,166,605 cents, over 333,333 paid orders, 16,666,533,321 cents in total | S13 §2 | the clean run, before any fault |
| L34 | Lab: a wrong word (`selec`) is rejected with a syntax error and a position; a wrong column name is rejected by name, after the catalog lookup | S13 §3 | the two halves of the parser stage made visible |
| L35 | Lab: EXPLAIN of a query against a view and EXPLAIN of the underlying query produce byte-identical plans, with no view node | S13 §3 | the rewriter ran before the planner |
| L36 | Lab: the chosen plan is a hash join under a partial aggregate under a gather of two workers, total cost 18,285.79; with `enable_hashjoin = off` the cheapest remaining plan costs 41,515.08, 2.27× more | S13 §3, `captures.json` `cost_plan_chosen` / `cost_plan_runner_up` | costs moved by under 0.2% across three runs because ANALYZE samples. Only the runner-up's **cost** was captured; its plan text was not (see Open questions), so the post must not name its join method |
| L37 | Lab: the parallel scan of `orders` reported `Buffers: shared hit=7693`, exactly the table's page count | S13 §3 | leader plus two workers, one buffer per page |
| L38 | Lab: inserting an identical copy of order 4242 succeeds; the row then appears twice, and JP's revenue rises by exactly that order's 56,954 cents, to 3,333,423,633 | S13 §4 | `orders` has no primary key until step 5 |
| L39 | Lab: `alter table orders add primary key (id)` fails while the duplicate is present ("could not create unique index \"orders_pkey\"", "Key (id)=(4242) is duplicated"), succeeds once one copy is deleted, and then rejects the same insert ("duplicate key value violates unique constraint \"orders_pkey\""). The key then appears in `pg_constraint` as `orders_pkey`, contype `p`, backed by the unique index of the same name | S13 §5 | — |
| L40 | Lab: after one amount is set to null, `count(*)` is 1,000,000 and `count(amount_cents)` is 999,999; `where amount_cents = null` matches 0 rows and `is null` matches 1 | S13 §6 | the column's NOT NULL constraint had to be dropped first |
| L41 | Lab: the parallel scan of `orders` was estimated at 140,514 rows per process and returned 111,111 per process over 3 loops, 333,333 in total | S13 §3 (shipped captures) | estimates differ between runs; actuals do not |
| L42 | Lab: the plan ran in 3 processes (Workers Planned 2, Launched 2, plus the leader). Each produced 5 partial per-country rows; Gather Merge passed 15 rows up and Finalize GroupAggregate combined them into 5 | S13 §3 | — |
| L43 | Codd's paper appeared in Communications of the ACM in June 1970, written at IBM's research laboratory in San Jose | S1 masthead | — |
| L44 | SEQUEL was presented in 1974 by Chamberlin and Boyce, also of IBM's San Jose research laboratory | S2 masthead | venue settled against Crossref's 1976 label (search log 6–7) |
| L45 | Codd's foreign key: a domain (or combination) of R that is not R's primary key but whose values are values of the primary key of some relation S, which may be R itself | S1 §1.4 | — |
| L46 | Lab: psql's `\d` shows `customers` with a primary key (`customers_pkey`, a B-tree on `id`) and `orders` with five NOT NULL columns, no primary key and no index | S13 §1 | shopgen without `--indexes`: the base DDL, without the two indexes part 2 added |
| L47 | Lab: order 4242 belongs to customer 92399, is `paid`, and is for 56,954 cents; customer 92399's country is JP and, by shopgen's definition (`'customer ' \|\| id`), its name is 'customer 92399' | S13 §4, `shopgen.py` | — |
| L48 | A hash join first scans one input and loads it into a hash table keyed on the join columns, then scans the other input and looks up each row's matches in that table | S14 §51.5 | the docs call the hashed input the right relation; EXPLAIN shows it under a `Hash` node |
| L49 | Ordinary comparison operators return null, meaning unknown, when either input is null: `7 = NULL` is null. Test for null with `IS NULL` / `IS NOT NULL`, never `= NULL` | S16 §9.2 | — |
| L50 | WHERE keeps a row only when its condition is true; a false or a null result discards it | S17 §7.2.2 | — |
| L51 | SQL logic has three values — true, false and null for unknown — with FALSE AND NULL = FALSE, TRUE OR NULL = TRUE, NOT NULL = NULL, and NULL on both sides giving NULL | S15 §9.1 | — |
| L52 | PostgreSQL's raw parser checks syntax with fixed grammar rules and makes no catalog lookups; the transformation process that follows does the semantic interpretation that identifies the tables, functions and operators referenced | S18 §51.3.1–51.3.2 | — |
| L53 | The two are separate because catalog lookups can only be done inside a transaction, and the server does not want to start one on receiving a query string: it must first recognise transaction-control commands such as BEGIN and ROLLBACK | S18 §51.3.2 | — |

## Figure candidates

No figure from any source is reused. Codd 1970's Figure 1 (the `supply` relation) is the obvious
candidate for the "what a relation is" section, but the post's own two tables carry that job with
data the reader can query, and the 1970 CACM paper's rights are not clearly cleared for
reproduction. Every figure in this post is original and drawn from `lab/captures.json`.

## Open questions

- **The NULL critique literature was located but not read.** Date 1984 (10.1145/984549.984551),
  Rubinson 2007 (10.1145/1361348.1361350), Date's 2008 reply (10.1145/1462571.1462574) and
  Guagliardo & Libkin 2019 (10.1016/j.is.2018.08.001) all bear directly on the post's second
  surprise, and all are behind ACM or Elsevier for an automated fetch. **No claim in the post rests
  on them.** The post says what PostgreSQL does and what the SQL standard requires, and does not
  characterise the academic argument about whether three-valued logic was a mistake. Part 5, which
  owns NULL in joins and grouping, should get these full texts first.
- **System R (Astrahan et al. 1976) was located but not read**: every open copy is a scan with no
  text layer. The post's System R claims come from Selinger et al. 1979 (S3), which we did read.
- **Chamberlin's "50 Years of Queries"** (CACM 67(8):110–121, 2024, 10.1145/3649887) is SQL's
  co-author's own history and would be the right source for how SEQUEL became SQL. Not open
  access. The post therefore says what the 1974 paper says and does not narrate the path from
  SEQUEL to the standard.
- **Whether `customers`/`orders` page counts hold on 17.x** is untested. We measured 16.2 (parts
  1–3) and 18.6 (this part) and they agree; 17 is asserted nowhere.
- **`captures.md` step 3 shows the wrong plan for "the planner's second choice".** `run_lab.py`
  sent `set enable_hashjoin = off` and the `EXPLAIN` in two separate psql calls, and each call is
  its own session, so the setting was gone before the `EXPLAIN` ran and the chosen plan was
  printed again. The runner-up's cost in `captures.json` is correct (that capture sent both in one
  call). The code is fixed; the shipped `captures.md` still carries the old output and **must be
  regenerated by one lab run before publish**. That run needs the owner's go-ahead: on 2026-10-01
  the owner said not to touch any PostgreSQL while the article is written.
