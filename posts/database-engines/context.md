# Series context — Database Engines Beyond PostgreSQL

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** engineers who know PostgreSQL at the level of PostgreSQL Foundations' core and now meet engines built on different decisions.
- **Shape:** hybrid — see `plan.md`.
- **Shared promise:** the reader can read any engine’s trade-offs off a few design decisions, each measured against a named PostgreSQL mechanism.
- **Terminology and notation:** PostgreSQL terms keep the meanings PostgreSQL Foundations gave them; every contrast names the PostgreSQL part and anchor it is measured against.
- **Recurring example or lab:** the PostgreSQL series' shop data, exported or regenerated at the scale each part states; lab grades G1–G2 on the build machine, G3 legs listed in `access.md`.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1–20 | see `plan.md` | planned | one question each | — |

## Knowledge established

None yet.

## Decisions to preserve

- Hadoop and every other system here are not PostgreSQL; each part says which PostgreSQL mechanism it contrasts with, by anchor.
- Versions are pinned per part at research time, never from this plan.

## Open threads

- Checkpoint S not passed: the part list, and every access request in `access.md`, await the owner.

## Next part brief

- **Part:** 1 — The Five Decisions Behind Every Database Engine (`five-decisions-behind-every-database-engine`); build only after Checkpoint S.
- **Can assume:** None. Re-states PostgreSQL's baseline (append-only heap, one WAL, one primary) in one paragraph and links to PG Part 1 #a-two-byte-update-that-cost-7544-bytes, which is live.
- **Must teach:** What few design decisions separate every database engine from PostgreSQL, and how do you read an engine's trade-offs off them?
- **Must not repeat:** PostgreSQL internals beyond a one-sentence recap and a link.
- **Evidence still needed:** everything — no research has run.
- **Handoff:** Every engine's mechanism goes to its spoke. The map names families, not post titles, and links a spoke only once that spoke is live.
