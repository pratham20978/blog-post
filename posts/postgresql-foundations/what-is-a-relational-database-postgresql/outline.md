# Outline — What a Relational Database Actually Does

- **Slug:** `what-is-a-relational-database-postgresql` · **Series:** postgresql-foundations, part 4
- **Tier:** L2 · **Difficulty:** beginner · **Budget:** 4,500 words · **Figures:** 7
- **Lab:** G2, built and executed (`lab/`), rungs E1–E4
- **Answers:** What is a relational database, and what happens between typing a query and getting rows back?
- **Assumes:** nothing from the series. A terminal and a browser.
- **Hands off:** clause-by-clause SELECT evaluation → part 5. Schema design, keys and normal forms → part 7. How the planner costs plans → part 14. How the executor runs each node → part 15. Buffers and pages → part 1, never taught here.
- **How hand-offs read in the post:** later parts are "later in this series" — no number, no title, no link; they are not a public promise. Earlier parts are named by title, with no URL; the owner adds the links. See *Series links*.

## Series links

Part 4 depends on none of parts 1–3: it is the from-scratch entry point, and a reader who has read
nothing else in the series loses nothing. It names two published parts once each, as further
reading. The post carries the title as plain text; the owner wraps it in the link.

| Earlier post | Status | Where it is named | Why |
|---|---|---|---|
| Part 1 — *How PostgreSQL Uses Memory* | live | Body 2, the sentence on the 7,693 buffers | pages and buffers are taught there, not here |
| Part 2 — *How PostgreSQL Uses Processes* | live | Body 2, the clause on `Workers Launched: 2` | the parallel workers are introduced there |

Part 3, *How PostgreSQL Stores Data*, is not published, so part 4 does not mention it. This table
moves into `manifest.md` as *Series links to add* at assembly.

## Word budget

| Section | Target | Carries |
|---|---|---|
| Insights + who this is for | 135 | the answer, before any setup |
| Why this matters | 180 | the model is 55 years old and still the default (L30) |
| The problem | 360 | data independence, stated with the two tables' real sizes (L05, L31) |
| Worked example | 675 | the revenue question, run, with its real answer (L33) |
| Intuition | 450 | a relation is a set; the server is a four-stage machine |
| Body 1 — What is a relation, really? | 525 | Codd's definition and the catalog (L01–L04, L32) |
| Body 2 — What happens between the query and the rows? | 525 | the four stages, each made visible (L08–L18, L34–L37) |
| Body 3 — Two surprises | 525 | the duplicate and the NULL (L19–L25, L38–L40) |
| The math | 450 | Cartesian product, and three-valued logic |
| Implementation | 360 | the SQL, and how to run the lab |
| Limitations and common mistakes | 225 | what this post does not settle |
| Key takeaways + references | 90 | 5 bullets |

## Sections

### `## Insights`
Two to four sentences, the answer first. A relational database keeps data as relations — sets of
rows over named columns — and lets you state *what* you want rather than *how* to fetch it. Between
your `SELECT` and the rows, the server parses it, rewrites it, plans it and executes it, and you
can watch all four. It also does exactly what you declared and no more: our 1,000,000-row table
accepted a duplicate order and quietly moved one country's revenue, because nobody had declared a
key. Primary keyword: *relational database*.

### Who this is for
`**Level:** beginner · **You need:** a terminal; no SQL assumed · **Time:** ~20 min`

### `## Why this matters`
The relational model is from 1970 and SQL from 1974, and in 2024 two of the field's most-cited
systems people argued it is still the dominant model and that SQL keeps absorbing its challengers'
best ideas (L30). So this is not a legacy skill. The concrete hook: a revenue number that moved
overnight with no deploy and no error — the surprise this post ends on.

### `## The problem`
State it as Codd did, and with our numbers. You have 100,000 customers and 1,000,000 orders
(L31) and a question that spans both. You could write a program that opens both files and loops.
Then the file format changes, or someone adds an index, or the rows get reordered — and your
program breaks. Codd named these three dependencies — ordering, indexing, access path — and called
their removal *data independence* (L05). Name the constraint that makes it hard: the machine still
has to pick an order, an index and a path; somebody has to decide, and it will not be you (L11).

### `## Worked example`
One business question — revenue in cents per country for paid orders — written as SQL and run on
the lab, with the real five-row answer (L33). Show the SQL, show the output table, name every
clause in one line each without teaching evaluation order (that is later in this series). Then the same query's
`EXPLAIN ANALYZE`, as the thing the rest of the post explains. **FIG_04** anchors here.

### `## Intuition`
Two ideas, in plain words. First: a table is a set of rows, and a set has no order and no
duplicates — which is Codd's definition, not a convention (L01, L02). Second: the server is not
reading your query, it is compiling it; four stages, each with an input and an output.
Analogy: ordering at a restaurant rather than walking into the kitchen. **Where it breaks:** the
kitchen can refuse your order for being ungrammatical before it checks whether the dish exists,
which is exactly the difference between the post's two error messages (L34).

### `## Body 1 — What is a relation, really?`
Codd's definition, in his words and then in ours: a relation on n sets is a set of n-tuples, one
element from each (L01); rows are distinct and unordered, columns are ordered and named (L02, L03);
a primary key is the column or columns whose values identify a row uniquely (L04); a foreign key
points at another relation's primary key. Map each term onto what SQL calls it and what psql shows:
relation→table, tuple→row, attribute→column, domain→type. Then make "the schema is data" concrete:
`customers` and `orders` are themselves rows in `pg_class`, their columns rows in `pg_attribute`,
and `pg_class` has a row for `pg_class` (L21, L22, L32). **FIG_01**, **FIG_05**.

*Term map obligations in this section:* relation, tuple, attribute, domain, degree, primary key,
foreign key, catalog, system catalog, type.

### `## Body 2 — What happens between the query and the rows?`
The four stages, in PostgreSQL's own names (L12), each one made to show itself from the captures:
1. **Parse** — `selec` fails on syntax with a caret; `c.nosuchcolumn` fails by name, after the
   catalog was consulted. Two halves of one stage (L34).
2. **Rewrite** — define a view, `EXPLAIN` it, and find no view in the plan: the rewriter replaced
   it with its definition first (L13, L35).
3. **Plan** — the planner builds candidate paths, costs them, keeps the cheapest (L14). Read the
   two cost numbers and say what the units are (L16, L17). Then take the hash join away and show
   what the runner-up costs: 18,251 against 41,076, 2.25× (L36). *How* those numbers are computed
   is later in this series; say so, with no part number, and move on.
4. **Execute** — `EXPLAIN ANALYZE` puts actual rows beside estimates (L18). Name the two
   PostgreSQL 18 deltas the reader will see or not see: BUFFERS by default, and `rows=5.00`
   (L27, L28). **One sentence only** on the 7,693 buffers being one per page, naming part 1,
   *How PostgreSQL Uses Memory*, as the place pages and buffers are taught. When the plan shows
   `Workers Launched: 2`, one clause naming part 2, *How PostgreSQL Uses Processes*, for who those
   workers are.

Then the historical note that earns its place: System R ran four phases in 1979 — parsing,
optimization, code generation, execution (L08) — and PostgreSQL's four are not the same four. The
rewrite stage is where code generation was. **FIG_02**, **FIG_03**.

*Term map obligations:* parser, parse/query tree, rewriter, view, planner/optimizer, plan tree,
node, cost, estimate, executor, `EXPLAIN`, `EXPLAIN ANALYZE`.

### `## Body 3 — Two surprises on real rows`
**One: `orders` has no primary key.** Insert an identical copy of order 4242; it is accepted. The
row is now there twice, and JP's revenue rises by exactly that order's 56,954 cents (L38). Nothing
errored. Codd said all rows are distinct (L02); SQL does not say that unless you do. Then the fix,
in the order it really happens: the constraint is refused while the duplicate is there, accepted
once it is gone, and afterwards the server refuses the insert itself (L39). Quote the documentation's
own position on tables without primary keys (L24). Point forward to "later in this series", no number: the schema-design part opens here. **FIG_06**.

**Two: NULL is not a value.** Drop the `NOT NULL`, set one amount to NULL, and the counts diverge:
1,000,000 and 999,999 (L40). `count(*)` counts rows; `count(amount_cents)` counts non-null values
(L19). `sum` skips it too (L20). And the row cannot be found with `= null`, only with `is null`,
because the comparison is unknown rather than false (L40). Note the related trap: a unique
constraint does not stop two nulls (L25). **FIG_07**.

### `## The math`
Short and genuinely formal, two pieces. (1) The relation as a subset of a Cartesian product,
R ⊆ S₁ × … × Sₙ, with our `customers` as the worked instance and degree 3 (L01); why "set" is the
load-bearing word for surprise one. (2) Three-valued logic: the truth table for `=` with an unknown
operand, and the rule that `WHERE` keeps only rows where the condition is *true*, which is why
`= null` returns nothing and `is null` is a different operator (L40). Every symbol defined on first
use; a plain sentence after each line. Collapse the longer truth table into `<details>`.

### `## Implementation`
The lab, and only what the reader needs to run it: `shopgen.py` builds the two tables from the DDL
parts 1–3 used, `run_lab.py` reproduces every number in this post, `check.py` marks each exercise.
State the provenance line (18.6, default config, 16 CPUs). Point at `[Lab downloads](#lab-downloads)`;
never a local path. Note that the page counts came out identical on 16.2 and 18.6 (L31).

### `## Limitations and common mistakes`
- `> [!WARNING]` **Common mistake:** believing a table is a set. It is a bag until you declare a key.
- The costs here are not milliseconds and do not predict them; comparing two plans' costs is
  meaningful, comparing a cost to a clock is not (L17).
- One lab machine, one data distribution: the plan shape is ours, not a law. A later part of the
  series is where the estimates are allowed to be wrong.
- What this post does not settle: whether SQL's three-valued logic was the right choice. The
  argument is real and published; this post states what PostgreSQL does, not who is right.

### `## Key takeaways`
Five bullets, each a claim: the model is a set of relations and the database enforces only what you
declare; `what` is separated from `how` by four stages you can watch; the catalog is itself
relations; a missing key is a silent data bug, not an error; NULL is unknown, and that changes what
counting means.

### `## Try it yourself`
The four rungs from `lab/README.md`, each with its self-check and a `<details>` answer: E1
reproduce the revenue table; E2 inspect what the executor read; E3 predict the two counts; E4
diagnose the moved revenue and make the server refuse its cause.

### `## References`
`### Lab downloads` first — `shopgen.py`, `run_lab.py`, `check.py`, `README.md`, `captures.md` —
then `### Sources` from the ledger: S1–S4 (papers), S5–S11 (PostgreSQL 18 documentation),
S12 (release notes).

## Figures

| ID | Name | Carries what the prose cannot | Source of its numbers |
|---|---|---|---|
| FIG_01 | `relation-vocabulary` | Codd's words and SQL's words on the same two tables, with degree and a marked key | L01–L04, L31 |
| FIG_02 | `path-of-a-query` | the four stages, each with its input, output, and the one place the catalog is read | L12–L15 |
| FIG_03 | `system-r-vs-postgresql` | the 1979 four phases beside the modern four, aligned, with code generation opposite rewrite | L08, L12 |
| FIG_04 | `plan-as-a-tree` | the EXPLAIN text redrawn as a tree, rows flowing upward, estimate beside actual at each node | L36, L37 |
| FIG_05 | `schema-is-data` | the two tables pointing at their own rows in pg_class and pg_attribute, and pg_class pointing at itself | L21, L22, L32 |
| FIG_06 | `duplicate-row` | one order inserted twice, both matching one customer, 56,954 added twice | L38 |
| FIG_07 | `three-valued-logic` | the truth table and the two counts' split, side by side | L19, L20, L40 |

Figure budget check: 7 figures over 4,500 words is one per 640 words, inside the L2 band.

## Term map

| Term | First section | What it is | Why it is used here | When it matters |
|---|---|---|---|---|
| relation | Body 1 | a set of tuples over named domains | it is the thing the model is named for | whenever "table" behaves unlike a set |
| tuple / row | Body 1 | one element of a relation | the unit everything else counts | counting, duplicates |
| attribute / column | Body 1 | a named position in every tuple | what SQL selects | schema design |
| domain / type | Body 1 | the set a column's values are drawn from | it bounds what can be stored | choosing types (part 8) |
| degree | Body 1 | the number of columns in a relation | makes "n-ary" concrete | reading Codd |
| primary key | Body 1 | the column(s) uniquely identifying a row | the declaration that makes a table a set | surprise one, part 7 |
| foreign key | Body 1 | a column holding another relation's primary key | how the two tables connect | joins, part 7 |
| system catalog | Body 1 | the tables that describe the tables | shows the model is self-describing | inspecting a database |
| parser | Body 2 | the stage that checks the text's shape | it explains the first error message | reading syntax errors |
| rewriter | Body 2 | the stage that expands views and rules | it explains why views are free | views, part 5 |
| planner | Body 2 | the stage that picks the cheapest path | it is who decides *how* | slow queries, part 14 |
| executor | Body 2 | the stage that runs the plan tree | it produces the rows | part 15 |
| plan node / tree | Body 2 | one step of the plan; its tree | how to read EXPLAIN at all | every performance question |
| cost | Body 2 | an arbitrary unit anchored at seq_page_cost=1 | stops cost being read as time | comparing plans |
| EXPLAIN / ANALYZE | Body 2 | shows the plan; runs it and measures | the post's main instrument | always |
| constraint | Body 3 | a rule the server enforces on every writer | the fix for surprise one | part 7 |
| NULL | Body 3 | the marker for unknown, not a value | the cause of surprise two | every aggregate |
| three-valued logic | The math | true, false, unknown | why `= null` matches nothing | writing WHERE clauses |
| aggregate | Body 3 | a function over many rows returning one | `count`, `sum` behave differently on NULL | reporting |

## Padding test

Each section's "what can the reader do after this" is distinct: *Problem* — say why a program over
files is the wrong tool. *Worked example* — write and run one real query. *Body 1* — read a schema,
and find it in the catalog. *Body 2* — read an EXPLAIN plan and say which stage produced what.
*Body 3* — recognise two silent data bugs. *The math* — justify both surprises from the definitions.
No section restates another. The History note sits inside Body 2 rather than becoming its own
section, because on its own it would restate Body 2's stage list.
