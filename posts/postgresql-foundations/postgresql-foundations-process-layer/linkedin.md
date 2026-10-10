# LinkedIn post

Same table. Same 800,000 deleted rows. One `VACUUM` walked both indexes five times;
the other walked them once. The only difference was a memory setting.

That is not a bug either. It is PostgreSQL's vacuum doing exactly what its source says
it does when the list of dead rows fills up, and it is the second in a series of things
I could not have told you a month ago.

PostgreSQL is not one program. It is a supervisor that never touches your data and a
crowd of single-purpose processes that do: one forked per connection, plus a fixed cast
of background workers that exist because their work must not run inside your query.
Almost every process-layer surprise an operator meets is one of those processes working
as intended.

Same lab as part 1 — a stock PostgreSQL 16.2, two tables, one `postgresql.conf`, every
capture quoted verbatim. What it showed:

- the autovacuum launcher visits each database once per minute and does not watch
  tables; a table that crossed its threshold waited 30.0 s for a worker that then
  finished in 30 ms
- in 16 a dead tuple costs 6 bytes of `maintenance_work_mem`, so 1 MB remembers
  174,761 of them and 800,000 means five complete index passes
- three autovacuum workers share one I/O budget, divided evenly — eight workers do
  not vacuum faster, they each get a smaller slice
- `synchronous_commit = off` was 16× faster on the same disk, and cannot corrupt
  anything; it turned 5,000 commits into 2 `fdatasync` calls
- `kill -9` on one backend dropped every other session, because the postmaster never
  reads shared memory and so cannot know what the dead child left in it

Swipe through for the one parent, the five passes, the thirty seconds, the shared
budget, the sixteen times, and the log line everyone misreads.

---

## Carousel order

1. `linkedin-01-one-parent.png` — every process is a child of one supervisor that never runs a query and is the only one allowed to fork
2. `linkedin-02-five-passes.png` — the same delete vacuumed at 1 MB and 256 MB of `maintenance_work_mem`: five index passes against one
3. `linkedin-03-thirty-seconds.png` — the launcher's clock: a table qualified instantly and waited half a naptime for 30 ms of work
4. `linkedin-04-one-budget.png` — one, three and eight workers under the same cost limit: the same total width every time
5. `linkedin-05-sixteen-times.png` — 5,000 commits with `synchronous_commit` on and off: 867 vs 13,771 tps, 5,000 vs 2 syncs
6. `linkedin-06-one-killed-backend.png` — the crash log, line by line, and why an innocent connection was dropped

---

## Accessibility checklist

- [ ] Upload frames in the numbered order.
- [ ] Apply each frame's supplied alt text from `assets/linkedin-prompts.md`.
- [ ] Check every frame is legible at mobile-feed size before posting.
- [ ] Confirm no frame rendered text, if the prompt route was used instead of the built frames.

---

## First comment

The postmaster never reads shared memory. That one restraint is why it can survive a
child that corrupts it — and why, when one does, the only safe move is to start
everyone over.

Part 1 (the memory layer): https://canery.in/blogs/postgresql-foundations-memory-layer

Read part 2 on Canery: https://canery.in/blogs/postgresql-foundations-process-layer
