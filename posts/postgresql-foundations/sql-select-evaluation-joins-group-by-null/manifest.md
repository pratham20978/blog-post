# Upload manifest — sql-select-evaluation-joins-group-by-null

Every placeholder in `blog.md`, in upload order. Upload each file to the public MinIO `media`
bucket under its suggested object key; the public URL is then
`https://minio.canery.in/media/<key>`. `urls.txt` is pre-filled **in this row order** from those
keys. Edit it if an upload lands under a different key, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/postgresql-foundations/sql-select-evaluation-joins-group-by-null/ posts/postgresql-foundations/sql-select-evaluation-joins-group-by-null/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/postgresql-foundations/sql-select-evaluation-joins-group-by-null/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body, and the Canery contract
rejects a non-URL there, so resolve it before upload. Object keys carry the post slug as a suffix
so they cannot collide with earlier parts in the same flat bucket. Set
`Content-Disposition: attachment` on the eight lab files and the zip if the upload tool allows it.
The zip goes to the bucket root, `https://minio.canery.in/media/lab-sql-select-evaluation-joins-group-by-null.zip`, the URL
`blog.md` already carries; `urls.txt` does not list it.

## Build status (2026-10-02)

- **Lab: executed** on a temporary PostgreSQL 18.6 cluster (`initdb`, run, capture, `pg_ctl -m fast
  stop`, data directory deleted; only the 18.6 binaries remain). The shipped captures are the
  fourth run's, 2026-10-02T08:41:05Z. Every one of the sample's counts matched the hand count, and
  `check.py` was exercised on every rung, passing and failing paths both. `postgresql.auto.conf`
  was empty before and after.
- **Figures and cover: built 2026-10-02**, every PNG opened and checked by eye: arithmetic against
  the captures, each arrow's source and target, overlaps. Six collisions found by eye and fixed
  (figures 2, 3, 5, 6, 7, 10). `lint_visuals.py`: 0 text overflows; its 4 arrow reports land on
  table cells, which it cannot see. The slug-suffixed PNGs beside each figure are the upload copies.
- **Checkpoints A and B were not held for approval**: the owner asked for the whole post in one
  request. The source list and the outline are in `research/ledger.md` and `outline.md` for review
  here, at Checkpoint C.

## Series links to add

The post names earlier parts by title, with no URL. Wrap each title in its link:

| Earlier post | Status | Where it is named in `blog.md` |
|---|---|---|
| Part 4 — *What a Relational Database Actually Does* | **not yet published** — publish it before this part, which assumes it | the series line under *Who this is for*; *Intuition* ("Part 4 followed a query through PostgreSQL's planner") and the `= NULL` bullet; *Worked example* ("the one part 4 asked") |
| Part 2 — *How PostgreSQL Uses Processes* | live | *Worked example*, the sentence on the helper processes in the tie |
| Part 1 — *How PostgreSQL Uses Memory* | live | *Why does NOT IN return nothing…*, the sentence defining `work_mem` |

Part 3 is not published, so the post does not mention it. Later parts appear only as "later in
this series", with no number, title or link.

## Placeholders

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| LAB_01 | `lab/README.md` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/README.md` | grade, setup, run order, the four exercises, cleanup |
| LAB_02 | `lab/shopgen.py` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/shopgen.py` | builds the database and loads the series' two tables; --orderless adds the customers who never ordered |
| LAB_03 | `lab/sample.sql` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/sample.sql` | the 20-row sample from the worked example |
| LAB_04 | `lab/run_lab.py` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/run_lab.py` | the entry point: every number in the post |
| LAB_05 | `lab/check.py` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/check.py` | marks a reader's run, one exercise at a time |
| LAB_06 | `lab/broken.sql` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/broken.sql` | the three broken queries of exercise E4 |
| LAB_07 | `lab/captures.md` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/captures.md` | readable captures of the run the post quotes |
| LAB_08 | `lab/captures.json` | — | lab file | — | — | `labs/sql-select-evaluation-joins-group-by-null/captures.json` | machine-readable captures; check.py and the figures read them |
| ARCHIVE | `lab-sql-select-evaluation-joins-group-by-null.zip` | — | whole-lab zip, linked by its final URL, not a placeholder | — | — | `lab-sql-select-evaluation-joins-group-by-null.zip` | every lab file above in one zip; rebuild after any change to `lab/` |
| COVER | `assets/cover.png` | placed | template cover in the series grid (title block at x=560, motif on the left) | — | — | `cover-sql-select-evaluation-joins-group-by-null.png` | Rows of tiles narrowing from twelve to two; in the last row a tangerine tile and a dashed one tie for one place; eight dots beneath |
| FIG_01 | `assets/fig-01-sample-rows.png` | placed | Q4 — a grid of the 20 real rows, with the three effects marked on them | — | — | `fig-01-sample-rows-sql-select-evaluation-joins-group-by-null.png` | The 20-row sample: six customers, customer 6 marked as having no orders, and fourteen orders, customer 1's two paid orders marked |
| FIG_02 | `assets/fig-02-logical-order.png` | placed | Q5 — eight stages in one line, no crossings; the payoff is a written position and two real counts on every step | — | — | `fig-02-logical-order-sql-select-evaluation-joins-group-by-null.png` | The eight clauses in evaluation order, FROM to LIMIT, each with its written position and the row count after it, sample and full |
| FIG_03 | `assets/fig-03-limit-tie.png` | placed | Q4 — the five ranked totals with the LIMIT line cutting the tie, beside what each plan kept | — | — | `fig-03-limit-tie-sql-select-evaluation-joins-group-by-null.png` | Five country totals by paid revenue, IN and JP tied on the LIMIT 2 line; the default plan keeps IN, the plan without parallel workers JP |
| FIG_04 | `assets/fig-04-inner-vs-left-join.png` | placed | Q4 — the sample's 15 joined rows themselves, the padded one marked | — | — | `fig-04-inner-vs-left-join-sql-select-evaluation-joins-group-by-null.png` | The sample's left join: the inner join's 14 rows plus customer 6's row padded with NULLs, 15 in all |
| FIG_05 | `assets/fig-05-on-versus-where.png` | placed | Q4 — the same padded row through two placements of one condition, with real counts | — | — | `fig-05-on-versus-where-sql-select-evaluation-joins-group-by-null.png` | Customer 6's padded row: kept when status = 'paid' is in ON, dropped when it is in WHERE because NULL = 'paid' is unknown |
| FIG_06 | `assets/fig-06-where-versus-having.png` | placed | Q5 — two paths of four steps and the one plan; no crossings | — | — | `fig-06-where-versus-having-sql-select-evaluation-joins-group-by-null.png` | Two logical paths for one condition: WHERE filters 1,000,000 rows to 333,333 before grouping, HAVING groups first; one identical plan |
| FIG_07 | `assets/fig-07-null-group-sorts-first.png` | placed | Q4 — the 20 real groups in the order PostgreSQL sorted them | — | — | `fig-07-null-group-sorts-first-sql-select-evaluation-joins-group-by-null.png` | Twenty groups ranked by revenue descending: the five NULL groups on top, then the real ones, with JP paid and IN paid tied |
| FIG_08 | `assets/fig-08-not-in-unknown.png` | placed | Q4 — truth values on real comparisons for one customer, beside NOT EXISTS's single question | — | — | `fig-08-not-in-unknown-sql-select-evaluation-joins-group-by-null.png` | NOT IN for customer 100,001 unrolled into ANDed comparisons, one against NULL and unknown; beside it NOT EXISTS finds no match |
| FIG_09 | `assets/fig-09-fan-out.png` | placed | Q4 — the sample's real rows repeated by a join, kept once by EXISTS, multiplied by two joins | — | — | `fig-09-fan-out-sql-select-evaluation-joins-group-by-null.png` | A join repeats customer 1 once per paid order while EXISTS keeps it once; two joins to orders count its refunded amount twice |
| FIG_10 | `assets/fig-10-union-versus-union-all.png` | placed | Q4 — the sample's ten real ids as tiles, and what each operator keeps | — | — | `fig-10-union-versus-union-all-sql-select-evaluation-joins-group-by-null.png` | Paid-order ids 1, 1, 2, 3, 4, 5 and refunded-order ids 1, 2, 5, 3: UNION ALL keeps all ten, UNION keeps five |
