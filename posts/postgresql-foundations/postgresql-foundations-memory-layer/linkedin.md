# LinkedIn post

A 60 MB table. A 128 MB cache. After every scan, exactly 32 of its 7,693 pages are
in that cache — 256 KB — while 16,000 empty slots look on.

That is not a bug. It is PostgreSQL's buffer manager doing what it was designed to
do, and it is the first of several things I could not have told you a month ago.

PostgreSQL keeps RAM in three pools: a shared page pool every process maps, a 4 MB
ring of log records that must reach disk before any page may, and private working
memory that each sort or hash allocates and frees on its own. Almost every memory
surprise an operator meets is one of those three pools working as intended.

I built a small lab on a stock PostgreSQL 16.2 to see each of them: two tables, one
`postgresql.conf`, every `EXPLAIN` quoted verbatim. What it showed:

- eviction is a clock hand and a counter from 0 to 5 — pages read once vanish,
  pages read five times survive a table twice the pool's size
- the same two-byte UPDATE cost 7,544 bytes of WAL right after a checkpoint and
  176 bytes a moment later
- `work_mem` is per sort, per hash, per process: one query with two workers took
  six budgets at once
- a 256 MB sort made one backend grow from 12 MB to 97 MB and shrink to 18 MB, with
  the sort's memory decomposing exactly into 2²⁰ × 24-byte slots plus one chunk per row

Swipe through for the three pools, the clock sweep, the full-page image, and where
85 MB went.

---

## Carousel order

1. `linkedin-01-three-pools.png` — RAM inside a PostgreSQL server is three pools, plus the kernel cache it cannot see
2. `linkedin-02-fits-but-not-cached.png` — a 60 MB table in a 128 MB pool leaves 32 pages behind, because of one comparison
3. `linkedin-03-the-clock-sweep.png` — eviction is a clock hand lowering a counter from 0 to 5; the first unpinned zero goes
4. `linkedin-04-7544-bytes-vs-176.png` — the first change after a checkpoint logs the whole page; the second logs the change
5. `linkedin-05-work-mem-multiplies.png` — one budget per operation per process: six budgets for one query
6. `linkedin-06-where-85-mb-went.png` — a sort's 85 MB, decomposed, and returned by dropping one context

---

## Accessibility checklist

- [ ] Upload frames in the numbered order.
- [ ] Apply each frame's supplied alt text from `assets/linkedin-prompts.md`.
- [ ] Check every frame is legible at mobile-feed size before posting.
- [ ] Confirm no frame rendered text, if the prompt route was used instead of the built frames.

---

## First comment

The buffer manager never asks "does this table fit?". It asks "is this table bigger
than a quarter of the pool?", and if it is, the whole scan runs through 32 buffers.

Read the full article on Canery: https://canery.in/blogs/postgresql-foundations-memory-layer
