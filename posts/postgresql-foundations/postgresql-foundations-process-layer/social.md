---
social_schema: 2
canonical_url: "https://canery.in/blogs/postgresql-foundations-process-layer"
---

# Social publishing package — postgresql-foundations-process-layer

## LinkedIn post

PostgreSQL is not one program.

It is one supervisor that deliberately avoids your data, one backend per connection, and a permanent cast of processes for checkpoints, WAL, buffer cleaning, autovacuum, replication, and more.

That process model explains several production surprises that look unrelated:

- A fresh connection took 1.762 ms in the lab; a round trip on an existing connection took 0.0299 ms.
- An autovacuum worker spent 30 seconds arriving, then removed 30,000 dead tuples in 30 milliseconds.
- The same 800,000-row delete required five complete index passes at 1 MB of `maintenance_work_mem` and one pass at 256 MB.
- Three or eight autovacuum workers still share one cluster-wide cost budget.
- `synchronous_commit = off` changed 5,000 single-row commits from 867 to 13,771 transactions per second in this lab, while trading away the newest crash-window commits—not consistency.
- Killing one backend made the postmaster terminate every other child and recover, because it cannot know what the failed child left in shared memory.

The useful debugging move is simple: name the process, identify the one decision it owns, and tune that decision instead of the symptom.

## LinkedIn first comment

The process name turns a vague PostgreSQL symptom into a specific clock, budget, memory store, or recovery rule.

Read the full article on Canery: https://canery.in/blogs/postgresql-foundations-process-layer

## Instagram caption

One PostgreSQL server is a supervisor and a crowd of single-purpose processes.

Swipe through six measured consequences: the process tree, five vacuum index passes versus one, 30 seconds of autovacuum waiting for 30 milliseconds of work, one shared worker budget, the WAL commit trade-off, and the whole-server recovery triggered by one killed backend.

The rule to keep: name the process before changing the setting.

Read the full technical guide through the Story link.

#PostgreSQL #DatabaseInternals #Autovacuum #WAL #DatabasePerformance

## Shared feed order

1. `assets/social/feed-01-one-parent.png` — PostgreSQL is one postmaster supervising per-connection backends and a fixed background-process cast.
2. `assets/social/feed-02-five-index-passes.png` — One megabyte of vacuum tuple memory forces five full index passes where 256 megabytes needs one.
3. `assets/social/feed-03-thirty-seconds.png` — A qualified table waits 30 seconds for an autovacuum worker that finishes in 30 milliseconds.
4. `assets/social/feed-04-one-shared-budget.png` — One, three, and eight workers divide the same 200-unit cost budget instead of multiplying throughput.
5. `assets/social/feed-05-sixteen-times.png` — Synchronous commit changes whether the backend waits for disk, moving the lab from 867 to 13,771 transactions per second with an explicit crash-loss trade-off.
6. `assets/social/feed-06-one-killed-backend.png` — One backend killed by signal 9 makes the postmaster reset every child and run recovery before the article CTA.

## Instagram Story

- CTA: Read the full PostgreSQL process-layer guide on Canery
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/postgresql-foundations-process-layer

### Story order

1. `assets/social/story-01-one-supervisor.png` — Overlay: PostgreSQL is not one program.
2. `assets/social/story-02-thirty-seconds.png` — Overlay: 30 seconds waiting. 30 milliseconds working.
3. `assets/social/story-03-five-index-passes.png` — Overlay: The same delete needs five index passes or one.
4. `assets/social/story-04-name-the-process.png` — Overlay: Name the process. Then tune it.

## Asset metadata

### feed-01-one-parent

- File: `assets/social/feed-01-one-parent.png`
- Title: PostgreSQL is not one program
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: PostgreSQL is a supervised process tree in which only the postmaster forks client and background processes.
- Technical source: The problem; The postmaster: the process that never touches your data; Figure 2; ledger claims L01, L20, and L28
- Visual structure: The Canery lockup and series label lead into a two-line hook, a postmaster-to-children process tree, a three-line architectural explanation, and the practical tuning rule.
- Visible-text transcript: Canery; PostgreSQL foundations · part 2; 01 / 06; PostgreSQL is not one program.; It is a supervisor and a crowd of single-purpose processes: one per connection, plus a fixed background cast.; postmaster · never touches your data; backend; backend; backend; checkpointer; bg writer; WAL writer; av launcher; av worker; parallel wkr; Every process in a PostgreSQL server is a child of one supervisor that never runs a query, never reads a page, and is the only process allowed to fork.; The autovacuum launcher cannot start a worker. A parallel query cannot start its own. Every one of them asks the postmaster.; how postgresql uses processes; canery
- Alt text: A postmaster that never touches data fans out to client backends, checkpointer, WAL writer, autovacuum, and parallel workers.
- Long description: A highlighted postmaster sits above nine child processes: three representative client backends plus the checkpointer, background writer, WAL writer, autovacuum launcher, autovacuum worker, and a parallel worker. The frame states that only the postmaster forks and that it does not run queries or read data pages.
- Keywords: PostgreSQL postmaster, process tree, client backend, background processes, fork
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### feed-02-five-index-passes

- File: `assets/social/feed-02-five-index-passes.png`
- Title: The same delete needs five index passes or one
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Vacuum tuple-memory capacity deterministically changes the number of complete index passes for the same 800,000 dead rows.
- Technical source: Worked example: The same delete, vacuumed twice; The memory arithmetic; Figure 6; ledger claims L72 and L73
- Visual structure: Two stacked experiment bands compare 1 MB and 256 MB of maintenance work memory, followed by the six-byte tuple calculation and the operational takeaway.
- Visible-text transcript: Canery; Vacuum memory; 02 / 06; Same delete. Five index passes.; 800,000 dead tuples, two indexes, one setting changed: the vacuum read its indexes five times instead of once.; maintenance_work_mem = 1 MB; heap: 7,693 pages, read once; both indexes, in full × 5; 5 index passes · 13,015 index pages read; maintenance_work_mem = 256 MB; heap: 7,693 pages, read once; both indexes, in full; 1 index pass · 2,603 index pages read; In 16 a dead tuple costs 6 bytes of memory. When the list fills, vacuum stops, walks every index in full, and resumes. 1 MB holds 174,761 of them; 800,000 dead rows means five complete passes.; passes = ceil(dead tuples × 6 B / maintenance_work_mem).; On a churning table, that one setting decides how long vacuum takes.; how postgresql uses processes; canery
- Alt text: Two vacuum runs show 800,000 dead tuples causing five index passes at 1 MB of work memory but one pass at 256 MB.
- Long description: The upper band shows a 7,693-page heap scan and five complete walks of two indexes with `maintenance_work_mem = 1 MB`, totaling 13,015 index pages read. The lower band keeps the same heap and indexes but uses 256 MB, so all dead tuple identifiers fit and one 2,603-page index pass is sufficient.
- Keywords: PostgreSQL VACUUM, maintenance_work_mem, dead tuples, index passes, PostgreSQL 16
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### feed-03-thirty-seconds

- File: `assets/social/feed-03-thirty-seconds.png`
- Title: Thirty seconds waiting, thirty milliseconds working
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Autovacuum arrival latency comes from the launcher's round-robin clock, not from the duration of the worker's table cleanup.
- Technical source: Worked example: Crossing the autovacuum threshold; The launcher's clock; Figure 5; ledger claims L53, L59, and L61
- Visual structure: A measured 0-to-30-second timeline contrasts the long launcher wait with the tiny worker interval, then separates arrival-time tuning from work-time tuning.
- Visible-text transcript: Canery; Autovacuum clock; 03 / 06; Thirty seconds waiting. Thirty milliseconds working.; The table crossed its threshold the instant the UPDATE committed. Nobody looked for half a minute. Nothing was misconfigured.; UPDATE 30,000 rows; threshold 20,050 crossed at once; 30.0 seconds · the launcher is asleep; 0 s; 5 s; 10 s; 15 s; 20 s; 25 s; 30 s; worker forked; 30,000 removed in 0.03 s; The launcher visits each database once per autovacuum_naptime, 60 s by default, round-robin. It does not watch tables; it keeps time. A table that qualifies waits for the next visit—up to a minute.; Expected arrival: naptime / 2. Worst case: naptime, plus queueing for one of three worker slots. Halving naptime halves the wait, not the work.; how postgresql uses processes; canery
- Alt text: Timeline shows 30,000 updated rows waiting 30 seconds for autovacuum, followed by a worker that removes them in 0.03 seconds.
- Long description: At time zero an update produces 30,000 dead tuples, above the computed 20,050 threshold. The launcher is between database visits, so the table waits 30.0 seconds. A worker then appears and removes the tuples in 0.03 seconds, demonstrating that `autovacuum_naptime` controls discovery latency rather than the cleanup duration.
- Keywords: autovacuum launcher, autovacuum_naptime, vacuum threshold, pg_stat_activity, PostgreSQL
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### feed-04-one-shared-budget

- File: `assets/social/feed-04-one-shared-budget.png`
- Title: More autovacuum workers share the same budget
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Increasing autovacuum worker count improves concurrency across tables but does not raise the cluster's total cost-limited I/O rate.
- Technical source: The budget, and why more workers do not help; Figure 23; ledger claims L66 and L67
- Visual structure: Three equal-width budget bars split 200 cost units among one, three, and eight workers, followed by the distinction between raising throughput and serving more tables concurrently.
- Visible-text transcript: Canery; Autovacuum budget; 04 / 06; More workers. Same speed.; Raising autovacuum_max_workers from 3 to 8 cannot make vacuum keep up, because all of them share one budget.; one worker · 200 cost units per 2 ms each; limit 200; = 200 units / 2 ms · the same total; three workers · 66 cost units per 2 ms each; limit 66; limit 66; limit 66; = 200 units / 2 ms · the same total; eight workers · 25 cost units per 2 ms each; = 200 units / 2 ms · the same total; autovacuum_vacuum_cost_limit is divided among the running workers. The bar's width is the cluster's vacuum I/O ceiling—about 39 MB/s of dirtied pages at the defaults—and it never moves.; To vacuum faster, raise the budget. Add workers only when many tables need vacuuming at the same time.; how postgresql uses processes; canery
- Alt text: Equal-width bars divide a 200-unit autovacuum budget among one, three, and eight workers without increasing total throughput.
- Long description: The first row gives one worker all 200 cost units per two milliseconds. The second divides the same budget into three limits of 66, and the third divides it into eight limits of 25. Every row has identical total width, showing why worker count changes concurrency but not the shared cost ceiling.
- Keywords: autovacuum_max_workers, autovacuum_vacuum_cost_limit, cost delay, I/O budget
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### feed-05-sixteen-times

- File: `assets/social/feed-05-sixteen-times.png`
- Title: Synchronous commit changes what a backend waits for
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The lab's throughput gain from asynchronous commit comes from removing the per-commit disk wait while preserving consistency and accepting bounded recent-transaction loss.
- Technical source: The WAL writer and what a commit waits for; Figure 19; ledger claims L46 and L49
- Visual structure: A paired bar chart compares throughput and fdatasync counts with synchronous commit on and off, followed by the WAL-writer timing and explicit crash-loss qualifier.
- Visible-text transcript: Canery; WAL commit path; 05 / 06; Sixteen times faster. Zero corruption risk.; 5,000 single-row commits on the same disk. The only difference is whether the backend waits for fdatasync before replying.; 867; synchronous_commit = on; transactions per second; 5,000 fdatasync calls; for 5,000 commits; 13,771; synchronous_commit = off; transactions per second; 2 fdatasync calls; for 5,000 commits; With on, the committing backend waits for the disk to confirm its log record. With off, it replies at once and the WAL writer flushes within 3 × wal_writer_delay = 600 ms. Nothing can be corrupted.; off risks the last 600 ms of commits in a crash, never consistency.; It is a per-transaction setting: off for the reload, on for the payment.; how postgresql uses processes; canery
- Alt text: Bar chart compares 867 versus 13,771 transactions per second and 5,000 versus 2 sync calls for synchronous commit on and off.
- Long description: For 5,000 single-row commits on the same PostgreSQL 16.2 system, `synchronous_commit = on` produces 867 transactions per second and 5,000 `fdatasync` calls. With it off, the lab records 13,771 transactions per second and two sync calls. The frame states that recent acknowledged commits may be lost in a crash window, but database consistency is preserved.
- Keywords: synchronous_commit, WAL writer, fdatasync, transactions per second, crash durability
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### feed-06-one-killed-backend

- File: `assets/social/feed-06-one-killed-backend.png`
- Title: One killed backend resets every session
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: A child crash causes the postmaster to terminate all children, reinitialize shared state, and recover because it cannot inspect possible shared-memory damage.
- Technical source: Worked example: One killed backend; The postmaster; Figure 10; ledger claims L03 and L04
- Visual structure: The final frame presents the real crash log in execution order, explains the postmaster's safety rule, and closes with the article and reproducible-lab invitation.
- Visible-text transcript: Canery; Crash recovery · read the article; 06 / 06; One backend killed. Every session dropped.; kill -9 on one connection. An innocent second connection got 'server closed the connection unexpectedly'. Here is why.; LOG: server process (PID 130554) was terminated by signal 9: Killed; LOG: terminating any other active server processes; LOG: all server processes terminated; reinitializing; LOG: database system was not properly shut down; automatic recovery in progress; LOG: redo starts at 3/73592518; LOG: database system is ready to accept connections; The postmaster never reads shared memory, so it cannot know what a killed backend left behind. It does the only safe thing: terminate every child, reset, recover. Two seconds later it was serving again.; That is the design, not a fault. Find the child in the line above.; Eleven processes, what each decides, and a lab you can run: PostgreSQL 16.2, default settings, every number quoted verbatim.; read it on canery; canery
- Alt text: PostgreSQL log sequence shows one backend killed, every child terminated, shared state reinitialized, and automatic recovery completed.
- Long description: The real server log begins with PID 130554 terminated by signal 9, then highlights `terminating any other active server processes`. It continues through reinitialization, automatic recovery, a redo start location, and readiness for new connections. The explanation connects this reset to the postmaster's deliberate refusal to inspect shared memory after a child crash.
- Keywords: PostgreSQL crash recovery, postmaster, SIGKILL, shared memory, redo
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### story-01-one-supervisor

- File: `assets/social/story-01-one-supervisor.png`
- Title: One supervisor and many PostgreSQL processes
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: The Story opens with PostgreSQL's supervisor-and-children architecture and assigns one responsibility to each permanent process.
- Technical source: The problem; Figure 2; ledger claims L01, L20, L25, and L28
- Visual structure: A large two-line hook leads to the highlighted postmaster, six connected process cards, and the instruction to tune the decision owned by the named process.
- Visible-text transcript: Canery; 01 / 04; PostgreSQL is not one program.; One supervisor forks every client and background process. The supervisor itself never runs a query or reads a page.; Only process allowed to fork; postmaster; client backend; one / connection; checkpointer; redo boundary; background writer; free buffers; WAL writer; log flushes; av launcher; keeps time; av worker; cleans tables; Name the process. Then tune the decision it owns.; PostgreSQL process layer · Canery
- Alt text: A highlighted postmaster connects to backend, checkpointer, background writer, WAL writer, launcher, and autovacuum worker cards.
- Long description: The vertical process tree places the postmaster above a client backend and five permanent background roles. Each child card names its responsibility: connection execution, redo boundary, free-buffer preparation, log flushing, autovacuum scheduling, or table cleanup. The postmaster is marked as the only process allowed to fork.
- Keywords: PostgreSQL architecture, postmaster, backend process, checkpointer, autovacuum
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### story-02-thirty-seconds

- File: `assets/social/story-02-thirty-seconds.png`
- Title: Thirty seconds waiting for thirty milliseconds of work
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The Story separates the threshold calculation, launcher delay, and worker execution time in the measured autovacuum run.
- Technical source: Crossing the autovacuum threshold; The launcher's clock; Figure 5; ledger claims L56, L59, and L61
- Visual structure: The threshold equation and computed customers-table value sit above a 30-second launcher timeline and a compact worker-log card, ending with the naptime takeaway.
- Visible-text transcript: Canery; 02 / 04; 30 seconds waiting. 30 ms working.; The table qualified immediately. The launcher was asleep.; Default vacuum threshold; 50 + 0.2 × reltuples; customers: 100,000 rows → 20,050 dead tuples; UPDATE created 30,000 dead tuples → qualified now; Measured timeline · PostgreSQL 16.2; launcher waits for its next database visit; 0 s · UPDATE commits; 30.0 s · worker appears; Worker log; 30,000 removed; elapsed: 0.03 s; Halving naptime halves the wait—not the work.; Autovacuum clock · Canery
- Alt text: Story computes a 20,050-tuple threshold, then contrasts a 30-second launcher wait with a 0.03-second autovacuum run.
- Long description: The default formula `50 + 0.2 × reltuples` gives the 100,000-row customers table a vacuum threshold of 20,050 dead tuples. An update creates 30,000, so the table qualifies immediately. The measured timeline shows the worker arriving 30.0 seconds later and removing the tuples in 0.03 seconds.
- Keywords: autovacuum threshold, reltuples, autovacuum_naptime, launcher delay
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### story-03-five-index-passes

- File: `assets/social/story-03-five-index-passes.png`
- Title: Five vacuum index passes or one
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The same dead-row set creates five index cycles at 1 MB and one at 256 MB because the tuple store fills at different rates.
- Technical source: The same delete, vacuumed twice; The memory arithmetic; Figure 25; ledger claims L71 and L72
- Visual structure: Two large memory-setting panels compare five orange pass blocks with one dark pass block, followed by the exact cycle calculation and cache qualifier.
- Visible-text transcript: Canery; 03 / 04; Same delete. Five passes or one.; 800,000 dead tuples. Two indexes. One memory setting.; maintenance_work_mem = 1 MB; 174,761 tuple slots; pass 1; pass 2; pass 3; pass 4; pass 5; Each fill pauses the heap scan and walks both indexes in full.; maintenance_work_mem = 256 MB; 1 complete index pass; The same 800,000 rows fit in one dead-tuple store.; cycles = ceil(800,000 / (174,761 − 291)) = 5; The pass count is deterministic. Its cost depends on cache.; Vacuum memory · Canery
- Alt text: Story compares five vacuum index-pass blocks at 1 MB with one complete pass at 256 MB for the same 800,000 dead tuples.
- Long description: At 1 MB, PostgreSQL 16.2 exposes 174,761 dead-tuple slots. Subtracting the 291-slot reserve and dividing 800,000 dead tuples produces five index-vacuum cycles. At 256 MB the same tuple identifiers fit at once, so both indexes are walked only once.
- Keywords: vacuum cycles, maintenance_work_mem, max_dead_tuples, index cleanup
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer

### story-04-name-the-process

- File: `assets/social/story-04-name-the-process.png`
- Title: Name the process before tuning PostgreSQL
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: The CTA maps four measured symptoms to the backend, launcher, vacuum worker, WAL writer, and the settings or actions they imply.
- Technical source: Worked example; Key takeaways; Figures 4, 5, 6, and 19
- Visual structure: Four measurement cards pair a symptom with its responsible process, followed by a dark guide-preview panel and a protected link-sticker instruction.
- Visible-text transcript: Canery; 04 / 04; Name the process. Then tune it.; Four symptoms. Four different decisions inside one server.; Connection; 1.762 ms vs 0.0299 ms; fresh backend vs reused connection; backend · pool connections; Autovacuum arrival; 30.0 s wait · 0.03 s work; qualified table waits for a visit; launcher · tune naptime; Vacuum passes; 5 index scans vs 1; 1 MB vs 256 MB work memory; worker · size tuple memory; Commit path; 5,000 syncs vs 2; synchronous_commit on vs off; backend + WAL writer; Full 50-minute technical guide; Postmaster · WAL · checkpoints · autovacuum; parallel workers · runnable PostgreSQL 16.2 lab; Read the full article on Canery; Link sticker · Read the article
- Alt text: Four cards map connection, autovacuum delay, vacuum passes, and commit sync measurements to the PostgreSQL process responsible.
- Long description: The final Story summarizes four lab results: fresh versus reused connection latency, autovacuum arrival versus execution time, five versus one index scan, and 5,000 versus two WAL syncs. Each card identifies the process and tuning direction, then the CTA previews the full process-layer guide and runnable PostgreSQL 16.2 lab.
- Keywords: PostgreSQL tuning, process diagnosis, connection pooling, autovacuum, WAL
- Canonical URL: https://canery.in/blogs/postgresql-foundations-process-layer
