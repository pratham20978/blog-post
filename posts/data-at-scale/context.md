# Series context — Data at Scale: From Hadoop to the Lakehouse

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** engineers who know PostgreSQL at the level of PostgreSQL Foundations' core and now meet data that has left one server.
- **Shape:** hybrid — see `plan.md`.
- **Shared promise:** the reader can design, run and debug a pipeline from PostgreSQL to a lakehouse, and say what each layer costs.
- **Terminology and notation:** PostgreSQL terms keep the meanings PostgreSQL Foundations gave them; every contrast names the PostgreSQL part and anchor it is measured against.
- **Recurring example or lab:** the PostgreSQL series' shop data, exported or regenerated at the scale each part states; lab grades G1–G2 on the build machine, G3 legs listed in `access.md`.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1–22 | see `plan.md` | planned | one question each | — |

## Knowledge established

None yet.

## Decisions to preserve

- Hadoop and every other system here are not PostgreSQL; each part says which PostgreSQL mechanism it contrasts with, by anchor.
- Versions are pinned per part at research time, never from this plan.

## Open threads

- Checkpoint S not passed: the part list, and every access request in `access.md`, await the owner.

## Next part brief

- **Part:** 1 — Hadoop Is Not a Database: What Changes When Data Outgrows One Server (`hadoop-is-not-a-database`); build only after Checkpoint S.
- **Can assume:** No prior part. SELECT, WHERE and GROUP BY. Readers with no SQL start at the PostgreSQL spine's SQL-from-scratch part, which is a cross-series link, not a dependency.
- **Must teach:** When does one PostgreSQL server stop being the right tool for a dataset, and what does the distributed data stack put in its place, layer by layer?
- **Must not repeat:** PostgreSQL internals beyond a one-sentence recap and a link.
- **Evidence still needed:** everything — no research has run.
- **Handoff:** Each layer goes to its arc: HDFS to 2, batch compute to 3 and 8, tables as directories to 4, object storage to 5, file formats to 6, table formats to 11, engines to 15, the log to 16, modeling to 19, the architecture choice to 22. HBase and the other engines are named once and handed to sibling B.
