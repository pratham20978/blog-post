# Upload manifest — what-is-a-relational-database-postgresql

Every placeholder in `blog.md`, in upload order. Upload each file to the public MinIO `media`
bucket under its suggested object key; the public URL is then
`https://minio.canery.in/media/<key>`. `urls.txt` is pre-filled **in this row order** from those
keys. Edit it if an upload lands under a different key, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/postgresql-foundations/what-is-a-relational-database-postgresql/ posts/postgresql-foundations/what-is-a-relational-database-postgresql/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/postgresql-foundations/what-is-a-relational-database-postgresql/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body, and the Canery contract
rejects a non-URL there, so resolve it before upload. Object keys carry the post slug as a suffix
so they cannot collide with earlier parts in the same flat bucket. Set
`Content-Disposition: attachment` on the six lab files if the upload tool allows it.

## Build status (2026-10-01)

- **Gate: PASS** (`validate_post.py`, and `--social` with 0 warnings). The two default warnings are the length, 5,126 words of which 466 are references, and two ledger rows the post does not cite.
- **Figures, cover and social: built 2026-10-01** and every PNG opened and checked. The six
  placed figures come from `assets/_figs.py`, FIG_04 from `assets/_fig04.py` and its `.mmd`, the
  cover from `assets/_cover.py`, and the ten social frames and `social.md` from `assets/_social.py`.
  Every number in them is read from `lab/captures.json`. The slug-suffixed PNGs beside each figure
  are the upload copies named in the object keys. `lint_visuals.py`: 0 text overflows; its 16
  arrow reports all land on table cells, a bracket or Mermaid nodes, which it cannot see.
- **`lab/captures.md` needs one regeneration before upload.** Its step "the planner's second
  choice" printed the chosen plan again: the old `run_lab.py` sent the `SET` and the `EXPLAIN` in
  two psql sessions. The code is fixed. The post uses only the runner-up's cost, which
  `captures.json` recorded correctly. Regenerating needs one run on a temporary cluster, deleted
  afterwards, and the owner's go-ahead (owner, 2026-10-01: no PostgreSQL to be touched while the
  article is written).
- **`lab/check.py` gained a guard** that refuses E4 when an amount is still null from E3. It is
  untested for the same reason, and the next lab run should exercise it.

## Series links to add

The post names earlier parts by title, with no URL. Wrap each title in its link:

| Earlier post | Status | Where it is named in `blog.md` |
|---|---|---|
| Part 1 — *How PostgreSQL Uses Memory* | live | *What is a relation, really?* → *The schema is stored as data*, the sentence defining a page |
| Part 2 — *How PostgreSQL Uses Processes* | live | *What happens between the query and the rows?* → *Stage 4*, the sentence on the two helper processes |

Part 3 is not published, so the post does not mention it. Later parts appear only as "later in
this series", with no number, title or link.

## Placeholders

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| LAB_01 | `lab/README.md` | — | lab file | — | — | `labs/what-is-a-relational-database-postgresql/README.md` | grade, setup, run order, the four exercises, cleanup |
| LAB_02 | `lab/shopgen.py` | — | lab file | — | — | `labs/what-is-a-relational-database-postgresql/shopgen.py` | builds the database and loads the series' two tables |
| LAB_03 | `lab/run_lab.py` | — | lab file | — | — | `labs/what-is-a-relational-database-postgresql/run_lab.py` | the entry point: every number in the post |
| LAB_04 | `lab/check.py` | — | lab file | — | — | `labs/what-is-a-relational-database-postgresql/check.py` | marks a reader's run, one exercise at a time |
| LAB_05 | `lab/captures.md` | — | lab file | — | — | `labs/what-is-a-relational-database-postgresql/captures.md` | readable captures of the run the post quotes |
| LAB_06 | `lab/captures.json` | — | lab file | — | — | `labs/what-is-a-relational-database-postgresql/captures.json` | machine-readable captures; check.py and the figures read them |
| COVER | `assets/cover.png` | placed | template cover in the series grid (title block at x=560, motif on the left) | — | — | `cover-what-is-a-relational-database-postgresql.png` | Two grids of square tiles joined by a thin line, one row of the right grid shown twice in tangerine, four dots in a row beneath |
| FIG_01 | `assets/fig-01-plan-as-a-tree.png` | placed | Q2 declined: the plan text is already in the post verbatim; the figure's job is the tree, rows flowing up, with real estimated and actual rows on all 9 nodes (Q4) | — | — | `fig-01-plan-as-a-tree-what-is-a-relational-database-postgresql.png` | The revenue query's plan drawn as a tree: scans of orders and customers at the bottom feed a hash join, then a partial aggregate and a sort in each of three processes, then a gather merge, a final aggregate and a sort at the top, with estimated and actual row counts beside each step |
| FIG_02 | `assets/fig-02-declared-keys.png` | placed | Q4 — the two real tables drawn as grids, with the declared key and the undeclared link marked on them | — | — | `fig-02-declared-keys-what-is-a-relational-database-postgresql.png` | The customers and orders tables drawn as grids of rows: customers.id marked as its declared primary key, orders with no key at all, and an arrow from orders.customer_id to customers.id marked as a foreign key that nothing declares or checks |
| FIG_03 | `assets/fig-03-schema-is-data.png` | placed | Q4 — a grid of real catalog rows, with pg_class pointing at its own row | — | — | `fig-03-schema-is-data-what-is-a-relational-database-postgresql.png` | The customers and orders tables each pointing to their own row in pg_class and to one row per column in pg_attribute, with the pg_class table pointing to its own row in pg_class |
| FIG_04 | `assets/fig-04-path-of-a-query.png` | mermaid | Q3 — the post's one end-to-end view: text in, four stages, catalog lookups, rows out | — | — | `fig-04-path-of-a-query-what-is-a-relational-database-postgresql.png` | Four stages left to right, parser, rewriter, planner and executor, with SQL text going in, a query tree passed from the parser to the rewriter, a rewritten query tree passed to the planner, a plan tree passed to the executor and rows coming out, and the system catalog consulted by the parser and the rewriter |
| FIG_05 | `assets/fig-05-system-r-vs-postgresql.png` | placed | Q4 — two four-step lists aligned, with the one unmatched step in each offset; Mermaid cannot hold the alignment | — | — | `fig-05-system-r-vs-postgresql-what-is-a-relational-database-postgresql.png` | System R's four phases from 1979, parsing, optimization, code generation and execution, aligned above PostgreSQL's four stages, parser, rewriter, planner and executor, with parsing, optimization and execution matched, code generation unmatched after optimization, and the rewriter unmatched before the planner |
| FIG_06 | `assets/fig-06-duplicate-row.png` | placed | Q4 — the real duplicated rows, the join and the sum, with the 56,954 cents on every edge | — | — | `fig-06-duplicate-row-what-is-a-relational-database-postgresql.png` | Two identical rows for order 4242 in orders, both joined to customer 92399 in JP, so the sum for JP adds 56,954 cents twice and the country's total rises from 3,333,366,679 to 3,333,423,633 |
| FIG_07 | `assets/fig-07-three-valued-logic.png` | placed | Q1 declined: two counts that differ by one are not a chart; Q4 — truth values on real rows beside the two counts | — | — | `fig-07-three-valued-logic-what-is-a-relational-database-postgresql.png` | On the left, the comparison amount_cents = NULL evaluating to unknown for every row so that WHERE keeps none, while IS NULL evaluates to true for the one blanked row; on the right, count(*) counting 1,000,000 rows and count(amount_cents) counting 999,999 non-null values |
