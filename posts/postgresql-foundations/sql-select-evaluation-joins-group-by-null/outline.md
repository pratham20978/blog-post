# Outline — How a SELECT Is Evaluated: Joins, Grouping and NULL

- **Slug:** `sql-select-evaluation-joins-group-by-null` · **Series:** postgresql-foundations, part 5
- **Tier:** L3 · **Difficulty:** beginner · **Budget:** 6,800 words · **Figures:** 10 + cover
- **Lab:** G2, built and executed on a temporary PostgreSQL 18.6 cluster (deleted after capture), rungs E1–E4
- **Answers:** In what logical order does SQL evaluate a SELECT, and what does each clause do to the rows?
- **Assumes:** part 4, *What a Relational Database Actually Does* — its section *What happens
  between the query and the rows?* (the four stages, EXPLAIN, NULL in counts and comparisons).
- **Hands off:** window functions, CTEs, LATERAL and recursion → part 6. Why the physical order
  differs from the logical one, and what NOT IN costs → the slow-query, estimate and executor
  parts. Join algorithms → the executor part. All as "later in this series", never a number.
- **Checkpoints A and B:** the owner asked for the whole post in one request ("build this one
  blog"), so the source list and this outline were not held for approval. Both are recorded
  here and in `research/ledger.md` for review at Checkpoint C.

## What research changed (Checkpoint A, in brief)

- 27 sources: 9 peer-reviewed (all read in full, including the four NULL critiques part 4 could
  not reach: SIGMOD Record's own archive serves them), 12 PostgreSQL documentation pages, 3
  source files at `REL_18_6`, the 19 beta release notes, the lab. The 2020 survey was located
  and could not be fetched; Libkin 2015 carries its job (ledger, Open questions).
- What the post can honestly claim: the processing order is PostgreSQL's documented definition
  of the result (L01), not an execution order (L03, L26); every row count is measured and the
  sample's are also worked by hand (L43–L64); NOT IN's empty answer is defined behaviour (L18,
  L34), and whether it is the *right* answer is genuinely contested (L31–L35), so the post
  names the disagreement rather than settling it.
- Changes from the plan's sketch: the tie lives at LIMIT 2 of the country report (and 5/6 of the
  status report), not LIMIT 10; the plan flips which tied row comes back (L47); NOT IN is also a
  two-minute query at default settings, stated once and handed off (L58).

## Series links

| Earlier post | Status | Where it is named | Why |
|---|---|---|---|
| Part 4 — *What a Relational Database Actually Does* | **ready, not yet published** — must go live before this part | the opening series line; Intuition (the planner, EXPLAIN); NOT IN section (`= NULL` and the three truth values) | part 5 assumes it |
| Part 1 — *How PostgreSQL Uses Memory* | live | NOT IN section, the sentence on work_mem | work_mem is taught there |
| Part 2 — *How PostgreSQL Uses Processes* | live | Worked example, the clause on parallel workers in the tie | parallel workers are taught there |

Part 3 is not published and is not mentioned. This table moves into `manifest.md` as *Series
links to add*.

## Word budget

| Section | Target | Carries |
|---|---|---|
| Insights + who + series line + jump list | 170 | the order, the counts, the tie, the NULL |
| Why this matters | 200 | a report that changed with no data change (L47); a count that went to 0 (L59) |
| The problem | 420 | written order vs logical order (L01, L02, L03) |
| Worked example | 1,050 | the 20-row sample by hand and the full shop measured (L43–L49, L12, L14, L15) |
| Intuition | 430 | each clause takes a table and returns one; the order defines the answer, not the work (L03, L26) |
| Body 1 — What does FROM build? | 600 | inner vs left join, ON vs WHERE (L05, L06, L50) |
| Body 2 — WHERE or HAVING, and where NULL lands in GROUP BY and ORDER BY | 750 | L07–L09, L13, L26, L29, L30, L40, L51–L54 |
| Body 3 — Why does NOT IN return nothing once a NULL appears? | 850 | L18, L27, L28, L34–L36, L31–L33, L58–L62, L23, L24 |
| Body 4 — Where do duplicate rows come from? | 650 | L17, L37, L11, L10, L42, L55–L57, L20 |
| The math | 450 | bag multiplicities, NOT IN as a conjunction, certain answers (L35–L38) |
| Implementation | 280 | the lab, provenance, run time, the warning |
| Limitations and common mistakes | 330 | the traps as mistakes, with symptoms (L42) |
| Key takeaways | 130 | five claims |
| Try it yourself | 250 | E1–E4 from the README, answers hidden |
| References | 400 | lab downloads + sources |

Total about 7,000 including references, inside the L3 band (5,000–7,500). A fifth body section
on ORDER BY and LIMIT was cut: the tie is the worked example's ending, NULL ordering sits in
Body 2, and logical-versus-physical sits in Intuition. On its own it would restate all three.

## Sections

### `## Insights`
SQL evaluates a SELECT in a fixed logical order — FROM, WHERE, GROUP BY, HAVING, SELECT,
DISTINCT, ORDER BY, LIMIT — and each clause takes a table and hands on a smaller or bigger one.
Know the order and you can predict every row count: 1,000,000 joined rows, 333,333 paid, 5
countries, 2 shown. Two results surprise people: the second of those two rows changed between
plans, because two countries tie; and one NULL turned NOT IN's 1,000 customers without orders
into 0, while NOT EXISTS still found all 1,000. Primary keywords: *SQL order of execution*,
*NOT IN NULL*, *LEFT JOIN vs INNER JOIN*.

### Who this is for + series line
`**Level:** beginner · **You need:** part 4's tables and EXPLAIN, or any first SQL course · **Time:** ~32 min`.
Series line names part 4 by title.

### `## Why this matters`
Two real symptoms from the lab, no theory: the "top two countries" report printed IN second
under one plan and JP under another, with the same data (L47); the "customers who never
ordered" count fell from 1,000 to 0 when one order lost its customer (L59). Neither is a bug.

### `## The problem`
The written order (SELECT first) vs the logical order (SELECT fifth) from the SELECT reference
(L01), as a two-column table. Three consequences stated precisely: an alias does not exist in
WHERE (L02, L53); an aggregate cannot be tested in WHERE (L52); nothing has an order until ORDER
BY, and only as far as its keys (L12). The reader's task: predict the rows after each clause.
State the boundary: this order defines the result, not the work (L03), and the rest is later in
this series.

### `## Worked example`
The 20-row sample (FIG_01): 6 customers, 14 orders, built by hand so every effect appears once.
The report — paid revenue per country, top two — built clause by clause: count after each on
the sample by hand and on the full shop measured (L46, L49), FIG_02. Explain the generator's
arithmetic in two sentences (L44): why every customer has exactly 10 orders and 333,333 are paid.
The ending: ORDER BY revenue with IN and JP tied; LIMIT 2 keeps whichever reached the sort
first; the measured flip (L47, FIG_03); WITH TIES (L15, L16) and a tiebreaker as the fixes.
Name part 2 for parallel workers in one clause.

### `## Intuition`
Each clause is a function from table to table; the pipeline picture, and where it breaks: the
server may do the work in any order that gives the same rows (L03; HAVING moved to WHERE, L26;
19's aggregation before joins, L24). Three rules carry the rest: FROM builds and can multiply
rows; WHERE and HAVING keep only *true* (L04); order exists only from ORDER BY on. Part 4 named
for the four stages and EXPLAIN.

### `## What does FROM build?` (Body 1)
INNER vs LEFT on the sample (FIG_04) and at scale: 1,000,000 vs 1,001,000, the 1,000 padded rows
(L05, L50). A LEFT JOIN plus a WHERE on the right table is an inner join again: 333,333; the same
condition in ON keeps the 1,000: 334,333 (L06, FIG_05). The plan agrees: no left join node (L50).
RIGHT and FULL in one sentence.

*Terms:* join, join condition, inner join, left (outer) join, padded row, ON vs WHERE.

### `## WHERE or HAVING, and where does NULL land?` (Body 2)
WHERE filters rows before grouping, HAVING filters groups after (L07). The same predicate both
ways: same 5 rows; 333,333 vs 1,000,000 rows reach grouping, 5 vs 15 groups form — logically;
physically the plans are identical because the planner moved it (L26, L51, FIG_06). A condition
on an aggregate can only be HAVING (L52), the puzzle Date named in 1984 (L30). Grouping by
country and status after the LEFT JOIN: 20 groups, five with a NULL status (L54): GROUP BY puts
NULLs in one group (L40), unlike `=`; in 1983's SQL it did not (L29). ORDER BY revenue DESC then
puts those NULL groups first, because NULLs sort as larger (L13): the report's top five is five
empty groups (FIG_07). NULLS LAST, and the tie again at 5/6.

*Terms:* group, HAVING, aggregate (reminder), NULLS FIRST/LAST.

### `## Why does NOT IN return nothing once a NULL appears?` (Body 3)
Customers who never ordered: NOT IN, NOT EXISTS, LEFT JOIN … IS NULL and EXCEPT all say 1,000
(L58). Set order 4242's customer_id to NULL: NOT IN says 0, the other three 1,000 (L59). Why:
NOT IN is `<> ALL`, a chain of ANDs, and one `<> NULL` makes it unknown (L18, L60, FIG_08); WHERE
drops unknown (L04); Libkin's one-line statement of it (L34). NOT EXISTS asks whether a matching
row exists, and a NULL never matches. Then the three-way difference table, R = {1, NULL},
S = {NULL} (L36, L62) — markdown table, not a figure. Which answer is right is argued: Rubinson
vs Date and Grant (L31–L33); certain answers in one sentence (L35). The practical rule: NOT
EXISTS, and NOT NULL where a value is required. Physical aside, two sentences: the planner can't
turn NOT IN into an anti-join for the same reason (L27); at default settings it took about two
minutes against 50 ms (L58, L28, L23, part 1 named for work_mem); 19 converts it when NULLs are
impossible (L24).

*Terms:* subquery, IN/NOT IN, EXISTS/NOT EXISTS, anti-join, certain answer.

### `## Where do duplicate rows come from?` (Body 4)
Customers with a paid order: JOIN 333,333, EXISTS and IN 100,000 (L55, L17): a join repeats a
row once per match (L37), a semi-join keeps it once, and the plan shows how (dedupe first). DISTINCT
repairs it at a cost (L42). The duplicated join: two joins to orders multiply — 1,099,998 rows,
revenue 3.3× (L56, FIG_09); FILTER as the repair (L20). UNION vs UNION ALL: 666,666 vs 100,000;
UNION dedupes inside each input too (L11, L57, FIG_10); NULLs count as equal here (L10, L38),
so after the NULL, UNION has 100,001 rows (L61). One sentence of history: 1983's UNION had no
ALL (L29).

*Terms:* fan-out, semi-join, bag, DISTINCT, UNION/UNION ALL, FILTER.

### `## The math`
Bag semantics in three lines: multiplicity of a joined pair is the product (L37), so the join
counts are sums of products: 333,333 = Σ paid orders; 1,099,998 = Σ p×r; UNION ALL adds, UNION
caps at 1. NOT IN as a conjunction under Kleene logic, worked on customer 100,001 (L18, L35).
Certain answers in a `<details>` block (L35).

### `## Implementation`
The lab: shopgen (with `--orderless 1000`), `sample.sql`, `run_lab.py`, `check.py`,
`broken.sql`, captures. Provenance (L43). Run time about four and a half minutes, nearly all of
it two NOT IN queries (L58). Warning: it drops a NOT NULL and blanks a value. `[Lab downloads](#lab-downloads)`.

### `## Limitations and common mistakes`
`> [!WARNING]` NOT IN over a nullable column. Then: WHERE on the right table of a LEFT JOIN;
wrapping a column in max() to silence the GROUP BY error (query C, L63); DISTINCT to hide
fan-out (L42); LIMIT without a unique ORDER BY (L14); treating the logical order as the
execution order. One machine, one plan: the tie can go either way on another machine.

### `## Key takeaways`
Five claims: the order; FROM multiplies and WHERE/HAVING keep only true; outer-join conditions
belong in ON; NOT IN breaks on one NULL, NOT EXISTS doesn't; top-N needs a unique order.

### `## Try it yourself`
E1–E4 from `lab/README.md`, each with a self-check, answers in `<details>`.

### `## References`
`### Lab downloads` (LAB_01–LAB_08 + the zip), then `### Sources` S1–S26 as used.

## Figures

All ten are `placed`: each one's value is a grid of real rows or a real count on every step, which
Mermaid cannot carry (Q4), and FIG_02 is eight stages in one line with no crossings (Q5). No paper
figure is reused (ledger, Figure candidates).

| ID | Name | Section | Carries what the prose cannot | Route · why | Numbers from |
|---|---|---|---|---|---|
| FIG_01 | `sample-rows` | Worked example | the 20 rows themselves, with customer 6's missing orders, customer 1's two paid orders and the IN/JP tie marked | placed · Q4, a grid of real values | `sample.sql` |
| FIG_02 | `logical-order` | Worked example | written order beside evaluation order, with the row count after each clause, sample and full | placed · Q5, eight stages, no crossings, a count on every edge | L46, L49 |
| FIG_03 | `limit-tie` | Worked example | the five sorted groups, the tie at the LIMIT boundary, which plan kept which | placed · Q4, ranked real values | L46, L47 |
| FIG_04 | `inner-vs-left-join` | Body 1 | the sample's joined rows both ways, customer 6's padded row | placed · Q4 | L49, L50 |
| FIG_05 | `on-versus-where` | Body 1 | the padded row surviving ON and dying at WHERE, unknown on its status | placed · Q4 | L49, L50 |
| FIG_06 | `where-versus-having` | Body 2 | two logical paths with their counts, and the one physical plan | placed · Q5, two paths of three steps | L51 |
| FIG_07 | `null-group-sorts-first` | Body 2 | the 20 groups ranked by revenue DESC, five NULL groups on top, the 5/6 tie | placed · Q4 | L54 |
| FIG_08 | `not-in-unknown` | Body 3 | NOT IN unrolled for customer 100,001 into ANDed comparisons ending in unknown, beside NOT EXISTS's single question | placed · Q4, truth values on real values | L58–L60 |
| FIG_09 | `fan-out` | Body 4 | customer 1 repeated by the join and kept once by EXISTS; the double join multiplying 2 × 1 | placed · Q4 | L55, L56 |
| FIG_10 | `union-versus-union-all` | Body 4 | the sample's 6 + 4 ids, 10 kept by UNION ALL, 5 by UNION | placed · Q4 | L57 |

Figure budget: 10 over about 7,000 words, one per 700 words, inside the L3 band of 8–12.

## Term map

| Term | First section | What it is | Why it is used here | When it matters |
|---|---|---|---|---|
| logical (evaluation) order | The problem | the order in which SQL defines each clause's effect | predicts counts and which names exist | whenever a clause does not see what you expect |
| clause | The problem | one keyword-led part of a SELECT | the unit of that order | always |
| alias | The problem | a name given to an output column in SELECT | exists only from SELECT on | ORDER BY yes, WHERE no |
| intermediate table | Worked example | what one clause hands the next | what you count | debugging a report |
| join, join condition | Worked example | pairing rows of two tables where a condition is true | builds the report's rows | every multi-table query |
| inner / left (outer) join | Body 1 | matched pairs only / plus unmatched left rows padded with NULLs | customers with no orders | "including those with none" |
| padded row | Body 1 | the row a left join adds for an unmatched left row | where NULLs appear with none stored | a WHERE on the right table |
| group, HAVING | Worked example / Body 2 | rows collapsed by equal values / a filter on groups | per-country totals; conditions on totals | reports |
| NULLS FIRST / LAST | Body 2 | where NULLs go in a sort | DESC puts them first | top-N |
| tie, WITH TIES, tiebreaker | Worked example | rows equal on every sort key; the clause that keeps all of them; an extra key | LIMIT's boundary | top-N, pagination |
| subquery | Body 3 | a SELECT inside another | IN, EXISTS | membership tests |
| IN / NOT IN; EXISTS / NOT EXISTS | Body 3 | value-membership tests; row-existence tests | the NULL trap | "customers who never …" |
| semi-join / anti-join | Body 3–4 | joins that keep each left row once if it has a match / has none | what the planner turns EXISTS into | reading EXPLAIN |
| certain answer | Body 3 | a row that is in the result however the NULLs are filled in | frames the disagreement | deciding what NULL means |
| fan-out | Body 4 | a join repeating a row once per matching row | duplicated totals | joins before aggregates |
| bag | Body 4 | a collection that may hold duplicates | what a table and UNION ALL are | counting |
| FILTER | Body 4 | a per-aggregate row condition | repairs the double join | conditional totals |
| hashed subplan, work_mem | Body 3 | an in-memory set of a subquery's values; the per-operation memory budget | why NOT IN is slow here | large subqueries |

## Padding test

*The problem* — say why the written order misleads. *Worked example* — compute a report's row
count after every clause, by hand and at scale. *Intuition* — model a clause as table-to-table and
separate logical from physical order. *Body 1* — choose INNER or LEFT and place a condition in ON
or WHERE. *Body 2* — choose WHERE or HAVING and predict where NULL groups land. *Body 3* —
predict NOT IN under a NULL and choose NOT EXISTS. *Body 4* — predict duplicates from a join or a
UNION and remove them correctly. *The math* — compute those counts from multiplicities. No two
answers match.
