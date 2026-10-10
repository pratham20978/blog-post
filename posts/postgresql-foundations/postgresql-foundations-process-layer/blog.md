---
title: "How PostgreSQL Uses Processes"
slug: postgresql-foundations-process-layer
date: 2026-09-19
updated: 2026-09-19
summary: "PostgreSQL is one supervisor and a crowd of single-purpose processes. Real lab numbers show what the postmaster, checkpointer, WAL writer and autovacuum each do, and why."
tags: [databases, postgresql, autovacuum, checkpointer, process-architecture, performance, internals]
category: databases
categories: [databases]
series: postgresql-foundations
series_position: 2
tier: L4
difficulty: intermediate
prerequisites: ["SQL and reading an EXPLAIN plan", "what a process and a signal are", "having run PostgreSQL at least once"]
reading_minutes: 50
cover_image_url: "https://minio.canery.in/media/cover-postgresql-foundations-process-layer.png"
cover_image_alt: "One small square set above a row of identical squares, each joined to it by a thin line, with one square in the row highlighted and carrying a short trail of dots behind it"
canonical_url: "https://canery.in/blogs/postgresql-foundations-process-layer"
---
> [!NOTE]
> **Insights** — PostgreSQL is not one program. It is a *supervisor* that never reads or writes your data, and a crowd of single-purpose processes that do: one forked for every connection, plus a fixed cast of background workers that exist because the work they do — flushing the log, writing dirty pages, cleaning up dead rows — must not happen inside your query. Almost every process-layer surprise you will meet — a `VACUUM` that walks the same two indexes five times, an autovacuum worker that arrives a full minute after the table crossed its threshold, a table that cannot be cleaned because somebody left a transaction open in another session, a whole server restarting because one backend was killed — is one of those processes doing exactly what it was designed to do.

**Level:** intermediate · **You need:** SQL and the habit of reading `EXPLAIN`, a working idea of what a process and a signal are, and a PostgreSQL you are allowed to break · **Time:** ~50 min

PostgreSQL's architecture is usually described as three layers: a **memory layer** that caches pages and log records, a **process layer** of the postmaster and the workers it forks, and a **storage layer** of heap files, indexes and WAL segments on disk. [Part 1](https://canery.in/blogs/postgresql-foundations-memory-layer) was the memory layer. This is the second post, and it stays inside the process layer: who the processes are, who is allowed to create them, how they talk to each other, and what each one decides. Where it needs a memory fact — what a dirty buffer is, why the log must reach disk before the page — it links to the section of part 1 that established it rather than teaching it again. Where a mechanism crosses into file formats, it says so and stops. Figure 1 shows the three layers and where this post sits. 

![Three horizontal layers labelled memory, process and storage, with the process layer highlighted and annotated with postmaster, backends, checkpointer, background writer, WAL writer and autovacuum, and the memory layer greyed as part 1](https://minio.canery.in/media/fig-01-three-layers-postgresql-foundations-process-layer.png)

*Figure 1 — The three layers of a PostgreSQL server. Part 1 was the top one; this post is the middle one.*

> [!TIP]
> **Runnable lab:** The server setup, runner, machine-readable captures, and readable results are listed under [Lab downloads](#lab-downloads) at the end. Use them when you want to reproduce the process, checkpoint, WAL, and vacuum experiments; the concepts and relevant results remain in this article.

Every number in this post that came from a running server came from that reproducible lab and the same setup as part 1: PostgreSQL 16.2 with its default `postgresql.conf`, the same 1,000,000-row `orders` table (7,693 pages) and 100,000-row `customers` table (710 pages), on a laptop with 16 CPUs, 15 GB of RAM and an NVMe disk. Part 2 adds two indexes on `orders`, because vacuum's interesting behaviour is in the index passes. The captured output is quoted verbatim. Where 17 or 18 changed a number, a name or a process, the change is named in the sentence. 

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [The postmaster](#the-postmaster-the-process-that-never-touches-your-data) · [What a connection costs](#what-a-connection-actually-costs) · [Interrupts](#how-one-process-interrupts-another) · [The checkpointer](#the-checkpointer-making-the-wal-forgettable) · [The background writer](#the-background-writer-and-why-your-backend-still-writes-pages) · [The WAL writer](#the-wal-writer-and-what-a-commit-waits-for) · [Autovacuum: deciding](#autovacuum-part-one-how-it-decides) · [Autovacuum: doing](#autovacuum-part-two-what-the-worker-actually-does) · [Parallel workers](#parallel-workers-and-the-shared-pool) · [The rest of the cast](#the-rest-of-the-cast) · [The math](#the-math) · [Implementation](#implementation) · [Limitations](#limitations-and-common-mistakes)

## Why this matters

A reporting table churns: a nightly job deletes and reloads 80% of it. Autovacuum is on, `pg_stat_all_tables` says it vacuumed the table this morning, and yet the table keeps growing and every scan gets slower. You look at `pg_stat_progress_vacuum` during the next run and see the phase flip between `vacuuming indexes` and `scanning heap` five times before it finishes. Nothing is broken. `maintenance_work_mem` is at its 64 MB default, the table produces more dead rows than 64 MB can remember, and vacuum is doing exactly what the docs say it does when that happens: a complete pass over every index, each time the list fills.  

Or: autovacuum is "not keeping up", so you raise `autovacuum_max_workers` from 3 to 8, restart, and nothing gets faster. It cannot. The three workers were sharing one I/O budget, `autovacuum_vacuum_cost_limit`, and the eight workers share the same budget, each getting a smaller slice. The setting you needed was the budget, not the headcount. 

Or: a data-loading script hits a segfault in an extension, and every connection on the server drops at once — the web app, the report, the migration that was half done. You find `terminating any other active server processes` in the log and assume the server crashed. It did not. One backend died badly, and the postmaster, which cannot know what that backend left behind in shared memory, did the only safe thing and started everyone over. 

Each of these is a different process. Once you can name the process and the one decision it makes, the fix is usually one line, and the log message stops looking like a failure.

## The problem

A database has work that belongs to no query. Somebody has to write dirty pages out of the shared buffer pool before it fills; somebody has to flush the write-ahead log so committed transactions survive a crash; somebody has to remove the row versions that `UPDATE` and `DELETE` leave behind under MVCC; somebody has to periodically make the log forgettable, so recovery after a crash takes seconds and not the age of the database. None of that work should run inside the query that happens to be executing when it becomes due, because that query's user did not ask for it and should not pay for it.

PostgreSQL runs one operating-system process per connection. Part 1 covered [why](https://canery.in/blogs/postgresql-foundations-memory-layer#the-problem): the 1986 Berkeley design chose a process per user over a threaded server "after much soul searching", citing limited programming resources, and forty years later that is still the architecture.  The consequence for this post is that the background work above cannot be a thread inside the server, because there is no single server to put a thread in. Each job is a process of its own, and the processes need a parent.

That parent is the **postmaster**. It is the process you start, the one that owns the listening socket, and the one that creates the shared memory segment part 1 described. It is also, deliberately, the process that does the least. Its source header says it creates shared memory at startup and then, as a rule, does not touch it: it is not in the array of backends, it cannot take a lock, and it never runs a query. The reason given is robustness. A process that does not read shared memory cannot be corrupted by a child that scribbled on shared memory, so it can survive that child's crash, reset everything, and carry on. 

Two rules follow from this and shape everything else in the post:

1. **Only the postmaster forks.** A backend cannot start a helper. The autovacuum launcher cannot start a worker. A parallel query cannot start its own workers. Every one of them asks the postmaster, through a signal and a flag in shared memory, and the postmaster forks a child that then reads the flag to find out what it is supposed to be. The autovacuum source gives the reason in one sentence: a process that is attached to shared memory is not as robust as the postmaster, so it must not be a parent.  
2. **A crash is a crash for everyone.** When any child exits abnormally, the postmaster assumes shared memory may be inconsistent, terminates every other child, and reinitialises. It cannot be more surgical than that, because it does not look inside shared memory to find out what was damaged. 

Figure 2 is the process tree of the lab server the moment after it started, from `ps`. Every process has the postmaster as its parent, and five of them exist before any client has connected. 

![Process tree with the postmaster at the top and five children under it labelled checkpointer, background writer, walwriter, autovacuum launcher and logical replication launcher, each with its resident memory in kilobytes](https://minio.canery.in/media/fig-02-process-tree-postgresql-foundations-process-layer.png)

*Figure 2 — A 16.2 server at rest. The postmaster and five children, none of them serving a client. `ps --ppid` confirms the parent of every one is the postmaster.*

```text
    pid    ppid    rss  command
 128882    3166  18176  postgres -D pgdata
 129064  128882  90240  postgres: checkpointer
 129065  128882   5404  postgres: background writer
 129144  128882   8204  postgres: walwriter
 129145  128882   6768  postgres: autovacuum launcher
 129146  128882   5856  postgres: logical replication launcher
```

One number in that block is a memory-layer fact wearing a process-layer costume: the checkpointer's 90 MB of resident memory is not private. RSS counts every page of the shared segment a process has touched, and the checkpointer, having just written most of the buffer pool, has touched most of it. The other four have touched almost none.

Stated with the defaults of a fresh 16.2 install, the cast is:  

- **The postmaster.** Listens, authenticates by forking, supervises, resets. Never touches data.
- **Client backends.** One per connection, forked on demand. Each parses, plans and executes every query on its connection, and each owns the private caches — relation cache, catalog cache, plan cache — that make a fresh connection expensive. 
- **The checkpointer.** Periodically writes every dirty page in shared buffers to its file and records a point from which recovery can start, so old WAL can be discarded. Also the process every backend hands its fsync requests to.  
- **The background writer.** Writes some dirty pages a little ahead of where backends will need a free buffer, so a backend evicting a page rarely has to write it first. 
- **The WAL writer.** Flushes log records that no backend has flushed yet, so that a transaction committed without waiting for the disk is still on disk within a knowable time. 
- **The autovacuum launcher and its workers.** The launcher decides which database to visit and when; a worker, forked by the postmaster at the launcher's request, decides which tables in that database have crossed their thresholds and vacuums them. 
- **The logical replication launcher.** Present by default; idle unless there is a subscription.
- **On demand:** parallel query workers, walsenders for each streaming replica, a walreceiver and a startup process on a standby, an archiver when `archive_mode` is on, and — from 18 — three I/O worker processes that perform reads on behalf of backends. 

Figure 3 puts each of these next to the pool from part 1 that it touches, because that is the fastest way to remember what each one is for.

![Grid with the processes down the side and the three memory pools from part 1 across the top; marks show the checkpointer and background writer on shared buffers, the WAL writer on WAL buffers, autovacuum workers on shared buffers through their own ring, backends on all three, and the postmaster on none](https://minio.canery.in/media/fig-03-who-touches-what-postgresql-foundations-process-layer.png)

*Figure 3 — Who touches what. The postmaster's row is empty on purpose.*

The constraint that ties the cast together is the one part 1 ended on: [a dirty page may not be written until the WAL describing its change is on disk](https://canery.in/blogs/postgresql-foundations-memory-layer#when-a-dirty-page-may-leave-memory). That rule is why the WAL writer and the checkpointer are separate processes with separate clocks, why the background writer has to flush WAL before it can write a page, and why the checkpointer's job is not "write pages" but "write pages *and then* declare which WAL is no longer needed". 

## Worked example

The lab creates the two tables from part 1, adds two indexes to `orders` (1,157 and 1,086 pages), and then does six things to the server that each expose one process. Everything below is quoted from the downloadable `captures.md`.

### What a connection costs

Two hundred fresh connections, each doing one `select 1` and closing, against two hundred round trips on a connection that is already open: 

```text
{
  "fresh_200_s": 0.3525,  "fresh_each_ms": 1.762,
  "reuse_200_s": 0.0060,  "reuse_each_ms": 0.0299,
  "ratio": 59.0
}
```

1.8 milliseconds to fork a process, authenticate it, attach it to shared memory and build its caches, against 30 microseconds to send a query to a process that already exists. This is over a Unix socket with `trust` authentication; a TCP connection with TLS and a password check is slower still. The fresh backend was 13.0 MB resident; one query against `pg_class` grew it to 14.5 MB, all of it private cache that no other backend can use.  Figure 4 draws the ratio.

![Two bars on a log scale: one fresh connection at 1.8 ms against one round trip on an open connection at 0.03 ms, a 59-to-1 ratio, with the fork, authenticate, InitPostgres and query stages marked on the tall bar](https://minio.canery.in/media/fig-04-connection-cost-postgresql-foundations-process-layer.png)

*Figure 4 — A connection costs about sixty queries. That number is the case for connection poolers, stated once.*

### Crossing the autovacuum threshold

`customers` has 100,000 rows. The vacuum threshold is `autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor × reltuples`, which with the defaults 50 and 0.2 is 20,050 dead tuples.  The lab computes the three thresholds in SQL, straight from `pg_settings` and `pg_class`: 

```text
  relname  | reltuples | vacuum_threshold | insert_threshold | analyze_threshold | n_dead_tup
-----------+-----------+------------------+------------------+-------------------+------------
 orders    |   1000000 |           200050 |           201000 |            100050 |          0
 customers |    100000 |            20050 |            21000 |             10050 |          0
```

Then it updates 30,000 rows of `customers` and waits, with nothing tuned — `autovacuum_naptime` is the default 60 seconds. A worker appeared **30.0 seconds** after the update. While it ran, `pg_stat_activity` showed it: 

```text
  pid  |   backend_type    |                    query
-------+-------------------+----------------------------------------------
130208 | autovacuum worker | autovacuum: VACUUM ANALYZE public.customers
```

and, with `log_autovacuum_min_duration` set to 0 for this one step, the worker wrote its own report:

```text
LOG:  automatic vacuum of table "proclab.public.customers": index scans: 1
	pages: 0 removed, 984 remain, 566 scanned (57.52% of total)
	tuples: 30000 removed, 95913 remain, 0 are dead but not yet removable
	removable cutoff: 71161, which was 0 XIDs old when operation ended
	index scan needed: 296 pages from table (30.08% of total) had 25164 dead item identifiers removed
	index "customers_pkey": pages: 551 in total, 0 newly deleted, 0 currently deleted, 0 reusable
	buffer usage: 2019 hits, 0 misses, 0 dirtied
	WAL usage: 1322 records, 0 full page images, 249396 bytes
	system usage: CPU: user: 0.01 s, system: 0.00 s, elapsed: 0.03 s
```

The work took 30 milliseconds. The wait took a thousand times longer. Figure 5 lays the two on the same timeline, because the gap between them is the whole point of the launcher section below.

![Timeline from the UPDATE at zero seconds: threshold crossed immediately, launcher asleep until its next visit to this database at 30 seconds, postmaster forks a worker, worker scans 566 pages and finishes 30 milliseconds later](https://minio.canery.in/media/fig-05-arrival-time-postgresql-foundations-process-layer.png)

*Figure 5 — Thirty seconds of waiting for thirty milliseconds of work. The launcher visits each database once per naptime; with two databases a visit comes every 30 s, and the wait for this one can be anything from nothing to a full minute.*

### The same delete, vacuumed twice

The lab copies `orders` into a scratch table with two indexes, deletes 80% of it — 800,000 dead tuples — and vacuums with `maintenance_work_mem` at 1 MB. Then it rebuilds the table, deletes the same rows, and vacuums with 256 MB.  

```text
INFO:  finished vacuuming "proclab.public.vac_demo": index scans: 5
pages: 0 removed, 7693 remain, 7693 scanned (100.00% of total)
tuples: 800000 removed, 200000 remain, 0 are dead but not yet removable
index "vac_demo_customer_idx": pages: 1178 in total ...
index "vac_demo_created_idx": pages: 1425 in total ...
buffer usage: 29051 hits, 0 misses, 1 dirtied
WAL usage: 36022 records, 0 full page images, 10357894 bytes
system usage: CPU: user: 0.24 s, system: 0.01 s, elapsed: 0.25 s
```

```text
INFO:  finished vacuuming "proclab.public.vac_demo": index scans: 1
...
buffer usage: 24323 hits, 0 misses, 1050 dirtied
WAL usage: 25670 records, 0 full page images, 5086568 bytes
system usage: CPU: user: 0.21 s, system: 0.01 s, elapsed: 0.22 s
```

Five complete passes over both indexes against one. And the elapsed time barely moved — 0.25 s against 0.22 s — because 2,603 index pages fit comfortably in the 128 MB buffer pool, so passes two to five were reads from memory. The lab then repeats both runs cold: server restarted to empty shared buffers, and the heap and index files evicted from the kernel page cache. Now the 5-pass vacuum takes 1.10 s and the 1-pass one 0.87 s, with 21,283 against 16,575 buffer misses.  Figure 6 shows all four.

![Grouped bars for warm and cold runs: index passes 5 versus 1 in both; elapsed 0.26 s versus 0.23 s warm and 1.10 s versus 0.87 s cold; buffer misses 0 versus 0 warm and 21,283 versus 16,575 cold](https://minio.canery.in/media/fig-06-index-passes-postgresql-foundations-process-layer.png)

*Figure 6 — The pass count is decided by arithmetic and does not care about the cache. What each pass costs does. On a table whose indexes do not fit in shared buffers, each extra pass is a full re-read from disk.*

That arithmetic is worth doing once by hand, because it is exact. In 16 a dead tuple is remembered as a 6-byte tuple identifier in an array; the array is sized as `(maintenance_work_mem − 8) / 6` entries; at 1 MB that is (1,048,576 − 8) / 6 = **174,761**.  The lab's `pg_stat_progress_vacuum` reported `max_dead_tuples = 174761`.  A new index pass starts when fewer than 291 slots are left — 291 being the most tuples an 8 KB page can hold — so each pass clears about 174,470 tuples, and 800,000 / 174,470 rounds up to 5. 

### One idle transaction

A second session runs `begin isolation level repeatable read; select count(*) from vac_demo;` and then does nothing. The first session deletes 800,000 rows and vacuums: 

```text
INFO:  finished vacuuming "proclab.public.vac_demo": index scans: 0
pages: 0 removed, 7693 remain, 7693 scanned (100.00% of total)
tuples: 0 removed, 1000000 remain, 800000 are dead but not yet removable
removable cutoff: 71185, which was 1 XIDs old when operation ended
```

Every page scanned, nothing removed — and note that the 800,000 dead rows still count as "remain". `pg_stat_activity` names the culprit: a backend in state `idle in transaction` — one of six states the view reports, and the one that holds a snapshot while doing nothing — whose `backend_xmin` is 71185.  The second session commits, the vacuum runs again, and it removes all 800,000 in one index pass. Figure 7 shows the two runs side by side.

![Two panels of the same vacuum: with a snapshot held, 7,693 pages scanned, 0 index passes, 0 removed and 800,000 not yet removable; after the snapshot is released, 1 index pass and 800,000 removed](https://minio.canery.in/media/fig-07-held-snapshot-postgresql-foundations-process-layer.png)

*Figure 7 — The oldest open snapshot anywhere in the cluster decides what every vacuum may remove. One idle `BEGIN` holds it.*

### Six workers planned, one launched

A parallel count over `orders` plans two workers and gets two. Raising `max_parallel_workers_per_gather` to 6 changes nothing: the planner still asks for two, because that setting is a ceiling and the number of workers is derived from the table's size. Setting the table's `parallel_workers` storage parameter to 6 makes the plan ask for six and the executor deliver six. Then, with `max_parallel_workers = 1`: 

```text
 Finalize Aggregate (actual rows=1 loops=1)
   ->  Gather (actual rows=2 loops=1)
         Workers Planned: 6
         Workers Launched: 1
         ->  Partial Aggregate (actual rows=1 loops=2)
               ->  Parallel Seq Scan on orders (actual rows=499995 loops=2)
                     Filter: (amount_cents > 0)
                     Rows Removed by Filter: 5
```

The plan was made against a ceiling; the workers were requested from a pool. The planner cannot see the pool.

### One killed backend

The last step opens two connections and sends `SIGKILL` to one of them. The server log: 

```text
LOG:  server process (PID 130554) was terminated by signal 9: Killed
DETAIL:  Failed process was running: select pg_backend_pid()
LOG:  terminating any other active server processes
LOG:  all server processes terminated; reinitializing
LOG:  database system was interrupted; last known up at 2026-09-19 16:36:26 IST
LOG:  database system was not properly shut down; automatic recovery in progress
LOG:  redo starts at 3/73592518
```

The second connection, which had done nothing wrong, got `server closed the connection unexpectedly`. Two seconds later the server was accepting connections again with a fresh set of children.

## Intuition

Picture a restaurant with one maître d' and no manager. The maître d' stands at the door. They seat every party at its own table and assign it its own cook — one cook per table, hired on the spot, who does everything for that table from taking the order to plating it. The maître d' never enters the kitchen. If a cook drops a pan and sets a fire, the maître d' does not investigate: they clear the whole restaurant, let it air out, and reopen. That is the postmaster, the backends, and `HandleChildCrash`.

Behind the tables is a small permanent crew that no customer ever ordered. One person walks the room writing down every order in a ledger the instant it is placed, so that if the power fails nothing is lost — that is the WAL writer, and the rule that the ledger entry must exist before the plate leaves the kitchen is the write-ahead rule. One person tidies plates from tables a little before they are needed, so a cook reaching for a clean plate rarely has to wash one — the background writer. Every few minutes one person does a full sweep and then tears the old pages out of the ledger, because everything on them has been served — the checkpointer. And one person walks the tables on a fixed round, noting which have accumulated enough dirty dishes to be worth clearing, and calls the maître d' to hire a temporary busser for each — the autovacuum launcher and its workers.

The analogy carries three real properties. The maître d' does not cook, so the maître d' cannot poison anyone. The cleanup crew has a fixed size and a fixed rhythm, so a busy night does not automatically get more cleaners. And one guest who refuses to leave keeps their table from being cleared no matter how many bussers are on shift.

It breaks in three places. First, the cooks are not independent: they share one pantry — shared memory — and a cook who corrupts the pantry has corrupted every other cook's ingredients, which is why the whole room is cleared and not just the one table. A restaurant would just replace the cook. Second, the maître d' cannot hire on their own judgement; every hire is requested by someone else and the maître d' only ever says yes. Third, the guest who will not leave does not just block their own table. Because every table in the building shares one timeline of what is "old enough to clear", one lingering guest anywhere blocks the clearing of every table in the building. Figure 8 draws the crew and marks where the analogy stops.

![Restaurant floor plan with a maître d' at the door, cooks at tables, and a crew of four along the back wall labelled ledger, plates, sweep and rounds; three callouts mark where the analogy breaks: shared pantry, hires only on request, one guest blocks every table](https://minio.canery.in/media/fig-08-the-kitchen-postgresql-foundations-process-layer.png)

*Figure 8 — The crew, and the three places the picture stops being true.*

## The postmaster: the process that never touches your data

`PostmasterMain` reads `postgresql.conf`, creates the shared memory segment and semaphores, opens the listening sockets, starts the auxiliary processes in a fixed order, and then enters `ServerLoop`, where it waits for one of three things: a connection request, a signal from a child, or a child exiting. Everything else it does is a reaction to one of those. 

On a connection request it forks *immediately* — `fork_process()` is a thin wrapper over `fork()` — before reading a byte of the client's startup message.  The child does the authentication — reads the startup packet, checks `pg_hba.conf`, negotiates TLS or GSS, verifies the password — and only then becomes a backend. The source gives two reasons for forking first: the auth code can be written in a simple single-threaded style, and a client that stalls inside a non-reentrant library like SSL or PAM stalls only its own child, never the postmaster and never anyone else.  Figure 9 is the sequence from `connect()` to the first query.

![Sequence diagram with lanes for client, postmaster and new backend: connect, ServerLoop accepts, fork_process, child reads startup packet, ClientAuthentication against pg_hba, InitPostgres takes a PGPROC slot and builds caches, then the read-parse-plan-execute loop; the postmaster returns to ServerLoop right after the fork](https://minio.canery.in/media/fig-09-connection-sequence-postgresql-foundations-process-layer.png)

*Figure 9 — The postmaster's involvement ends at the fork. Authentication, initialisation and every query happen in the child.*

The postmaster keeps a table of its children and nothing else of consequence. It is not in the `PGPROC` array, so it cannot hold or wait for a lock; it does not read the buffer pool; it does not read the WAL. When a child exits, `ServerLoop` collects the exit status. A clean exit — the client disconnected, an autovacuum worker finished — releases the slot. An abnormal one enters `HandleChildCrash`.  

`HandleChildCrash` logs which process died and what it was running, logs `terminating any other active server processes`, and sends `SIGQUIT` to every remaining child, including the checkpointer and the WAL writer. When the last one is gone it reinitialises shared memory, starts a startup process to run crash recovery from the last checkpoint's redo point, and only then accepts connections again.  The checkpointer's own source header adds a second reason this cannot be avoided even when shared memory is fine: if the checkpointer dies, the list of files that still need an fsync dies with it, and the only way to be sure everything is durable is to recover.  Figure 10 is the decision.

![Flowchart: child exits; if exit status is clean, release slot; otherwise log, send SIGQUIT to all children, wait for them, reinitialise shared memory, run crash recovery from the redo point, accept connections; restart_after_crash off leads to shutdown instead](https://minio.canery.in/media/fig-10-child-crash-postgresql-foundations-process-layer.png)

*Figure 10 — There is no branch that inspects shared memory to decide how bad it is. The postmaster does not look; it resets.*

Two more reactions are worth knowing. `SIGHUP` — from `pg_reload_conf()` or `pg_ctl reload` — makes the postmaster re-read the configuration files and forward the signal to every child, which is how a setting marked reloadable takes effect in running backends. And every child holds the read end of a pipe whose write end only the postmaster owns; if the postmaster dies, the pipe reports end-of-file, and children that notice it exit rather than run as orphans against a shared memory segment nobody supervises. 

What the postmaster does not do is as important as what it does. It does not fork on its own initiative. When the lab's autovacuum launcher decided `customers` needed a worker, the launcher did not fork one; it set a flag in shared memory and sent the postmaster `PMSIGNAL_START_AUTOVAC_WORKER`. The postmaster forked a child that knew nothing except that it should become an autovacuum worker; the child attached to shared memory and read the flag to learn which database. The autovacuum source explains the design: a process attached to shared memory is subject to corruption there and cannot reliably shut down its children on exceptional conditions, so it must not be a parent.   The same path serves parallel query workers and every extension's background worker. There is exactly one parent, and it is the process that reads nothing.

## What a connection actually costs

The 1.8 ms in the worked example is `fork()`, authentication, and `InitPostgres`. The fork is cheap on Linux. Authentication depends on the method. `InitPostgres` is where the time and the memory go, and it is the same for every connection, because everything it builds is private to the new process. 

In order: the backend takes a slot in the `PGPROC` array, which is how every other process will find it; registers with the shared-invalidation queue so it will hear about catalog changes; initialises the relation cache, the catalog cache and the plan cache, all empty; and registers with the statistics subsystem so it appears in `pg_stat_activity`.  Figure 11 puts the private part next to the shared part from part 1, to scale.

![To-scale comparison of one backend's private memory, 13.0 MB fresh and 14.5 MB after one catalog query, against the 143 MB shared segment from part 1; the private bar is labelled relcache, catcache, plancache, memory contexts](https://minio.canery.in/media/fig-11-private-vs-shared-postgresql-foundations-process-layer.png)

*Figure 11 — What a connection owns and nobody else can use. Multiply by the connection count; this is why 500 idle connections is a memory problem and not just a socket count.*

The caches are the reason a warm connection is fast and a cold one is not. The first query that touches a table pulls its `pg_class` row, its attributes, its indexes and its constraints into the relation cache; the second query finds them there. Prepared statements live in the plan cache. None of this is shared, because sharing it would need a shared allocator and shared locking on every lookup, which is a cost every query would pay. So PostgreSQL pays it once per connection instead, and the trade-off is that a connection pooler is not an optimisation but the design's intended shape. [Part 1&#39;s memory-contexts section](https://canery.in/blogs/postgresql-foundations-memory-layer#memory-contexts-how-a-backend-allocates) shows what these caches look like from inside the backend. 

Private caches raise a question: when one backend runs `ALTER TABLE`, how do the other backends' relation caches learn that their copy is stale? Through the shared-invalidation queue, a fixed-size circular buffer in shared memory. The backend that made the change appends an invalidation message at commit; every other backend reads the queue at the start of its next transaction and discards the cached entries the messages name. A backend that falls far behind gets a "catchup" interrupt telling it to read now; one that falls off the end of the ring is told to throw away its caches entirely.  Figure 12 draws it.

![Several backends, each with its own relcache, catcache and plancache, connected only through a ring buffer in shared memory labelled sinval; one backend appends an ALTER TABLE message, the others read it at their next transaction start](https://minio.canery.in/media/fig-12-sinval-postgresql-foundations-process-layer.png)

*Figure 12 — The only link between private caches. Backends do not talk to each other about schema; they all read the same ring.*

What `max_connections` actually sizes is the `PGPROC` array and everything keyed by it. `MaxBackends` is `max_connections + autovacuum_max_workers + 1 + max_worker_processes + max_wal_senders`, which with defaults is 100 + 3 + 1 + 8 + 10 = 122 slots, and it can only be set at server start.   Part 1 already showed the [lock table](https://canery.in/blogs/postgresql-foundations-memory-layer#the-rest-of-shared-memory) scaling with it. Since 14, taking a snapshot no longer scans that whole array to find the oldest running transaction, which is the change that made many idle connections cheap enough to tolerate; before it, every snapshot cost time proportional to the number of slots. 

Is any of this going to change? In June 2023 Heikki Linnakangas proposed on pgsql-hackers that PostgreSQL move to a single process with one thread per connection, over several releases and behind a switch. The obstacles he listed are the obstacles you would expect from this section: about 1,666 global variables that would have to become thread-local, extensions that assume a process, exposed process IDs in `pg_stat_activity`, the signal-based interrupts described below, and crash recovery — restarting after one thread corrupts memory is, in his words, hard and possibly impossible in one process. He named crash isolation as the current design's real advantage. As of September 2026 no such change has shipped, and 19 is still one process per connection. 

## How one process interrupts another

A backend in the middle of a sort cannot be stopped at an arbitrary instruction. It may hold a lightweight lock; it may be halfway through modifying a page in shared memory; it may be inside a critical section where an error would have to become a crash. So PostgreSQL never acts on a signal inside the signal handler. The handler sets a flag — `QueryCancelPending`, `ProcDiePending` — and sets `InterruptPending`, and returns. The backend checks that flag at points of its own choosing, by calling `CHECK_FOR_INTERRUPTS()`, and only there does it act. Long loops call it once per iteration; that is why a cancel usually lands within a millisecond and occasionally does not land for as long as a single uninterruptible step takes. 

`pg_cancel_backend(pid)` sends `SIGINT`; `pg_terminate_backend(pid)` sends `SIGTERM`.  The lab did both to a backend sleeping in `pg_sleep(30)`: 

```text
after cancel:     canceling statement due to user request        (connection still usable)
after terminate:  terminating connection due to administrator command   (process gone)
```

Figure 13 traces the cancel from the calling session to the point where the sleeping backend acts on it.

![Sequence diagram: session A calls pg_cancel_backend; kernel delivers SIGINT to backend B; B's handler sets QueryCancelPending and InterruptPending and returns; B's pg_sleep wakes from its latch; B calls CHECK_FOR_INTERRUPTS, sees the flag, raises the cancel error and returns to its read loop](https://minio.canery.in/media/fig-13-cancel-sequence-postgresql-foundations-process-layer.png)

*Figure 13 — Nothing happens in the signal handler except a flag. The backend interrupts itself, at a moment it chose.*

That covers two signals. PostgreSQL needs many more kinds of message between processes — "a catalog changed, re-read the queue", "a `NOTIFY` arrived", "a parallel worker has an error for you", "log your memory contexts", "a recovery conflict needs you to abort" — and Unix does not have that many signals to spare. So all of them ride on `SIGUSR1`. The sender sets a bit in the target's slot of a shared `ProcSignal` array naming the reason, then sends `SIGUSR1`; the handler reads its own slot to find out which reasons are set. Sixteen reasons are defined in 16, including seven flavours of recovery conflict.  The `pg_log_backend_memory_contexts(pid)` call part 1 used to look inside another backend is one of them: it sets `PROCSIG_LOG_MEMORY_CONTEXT`, and the target backend writes its own tree to the log at its next interrupt check.

Signals wake a process; they do not let it *wait* efficiently. A process that wants to sleep until either a timeout passes or another process pokes it uses a **latch**. `WaitLatch` sleeps in `epoll_wait` on Linux; `SetLatch` from another process makes that return. The historical difficulty was a race — a signal that arrives just before the sleep call does not wake the sleep — and the source describes the two fixes: the self-pipe trick on `poll()` platforms, where the handler writes a byte into a pipe the sleep is also watching, and on Linux a `signalfd` that turns the signal into a readable descriptor with no handler at all.  Every "wait" in this post — the checkpointer pacing its writes, the WAL writer between flushes, the launcher between rounds, a parallel leader waiting for tuples — is a latch wait.

The observable surface of all this is `pg_stat_activity.wait_event_type` and `wait_event`. When a process is inside a latch wait, those columns say what it is waiting *for*. There are nine types; "Activity" means idle in the main loop, "IO" a read or write, "Lock" a heavyweight lock, "LWLock" a lightweight one, "IPC" another process, "Timeout" a timer, "Client" the socket.  The lab sampled the columns 200 times a second while a join ran: 

```text
 backend_type                 | wait_event_type | wait_event           | samples
------------------------------+-----------------+----------------------+--------
 client backend               | (running)       | (cpu)                |      34
 parallel worker              | (running)       | (cpu)                |      31
 autovacuum launcher          | Activity        | AutoVacuumMain       |      19
 background writer            | Activity        | BgWriterMain         |      19
 walwriter                    | Activity        | WalWriterMain        |      19
 logical replication launcher | Activity        | LogicalLauncherMain  |      19
 checkpointer                 | Timeout         | CheckpointWriteDelay |      19
```

Every background process was asleep on its own latch the whole time, named by its main loop, and the checkpointer was asleep between paced writes. Figure 14 draws the sample. It is a sample of instants and not a profile, but it is the cheapest way there is to see where a server's time goes.

![Horizontal bars of sampled wait events by process type: client backend and parallel worker on CPU, four auxiliary processes on their Activity main-loop events, the checkpointer on CheckpointWriteDelay](https://minio.canery.in/media/fig-14-wait-events-postgresql-foundations-process-layer.png)

*Figure 14 — A server's background processes, seen through their latches. Each idle process names the loop it is sleeping in.*

## The checkpointer: making the WAL forgettable

Recovery after a crash replays the write-ahead log from some starting point forward. If that starting point were the beginning of the database, recovery would take as long as the database's life. A **checkpoint** is the mechanism that moves the starting point forward: it is a moment at which every heap and index page dirtied before it is guaranteed to be in its file, so recovery never needs to look at WAL older than it.  Once a checkpoint is complete, the WAL before its redo point can be removed or reused, which is the second thing checkpoints are for: bounding disk space. 

The checkpointer process performs them. A checkpoint is triggered when `checkpoint_timeout` elapses (5 minutes), when the WAL written since the last one approaches `max_wal_size` (1 GB), by the `CHECKPOINT` command, and at shutdown; a timed one is skipped if nothing was written.  The checkpointer does not itself watch WAL volume — backends signal it when they fill a segment. 

What it does, in order: note the current WAL position as the **redo point**; write every buffer that is dirty at that moment to the operating system, paced so the writes spread across the interval; fsync every file it wrote to, plus every file a backend asked it to fsync; write a checkpoint record to the WAL naming the redo point; update `pg_control`; and remove or recycle WAL segments before the redo point.   The redo point is earlier than the checkpoint record, and recovery starts from the redo point, because pages dirtied *during* the checkpoint may or may not have been included. Figure 15 lays a checkpoint against its interval.

![Timeline of one checkpoint interval: redo point at the start, dirty-buffer writes spread across 90% of the interval under checkpoint_completion_target, an fsync phase, the checkpoint record, then old WAL segments recycled; the lab's 0.055 s write and 0.210 s sync shown to scale for the forced case](https://minio.canery.in/media/fig-15-checkpoint-timeline-postgresql-foundations-process-layer.png)

*Figure 15 — A scheduled checkpoint spreads its writes over 90% of the interval. A forced one, like the lab's, does them all at once, which is why its sync phase dominates.*

The pacing is `checkpoint_completion_target`, 0.9 since 14 and 0.5 before that. The checkpointer adjusts its write rate so it finishes at 90% of `checkpoint_timeout`, or of the WAL budget, whichever is nearer, sleeping on `CheckpointWriteDelay` between batches — the wait event the lab caught it in. The docs recommend against reducing it, because a faster checkpoint is a spikier one.  The lab's manual `CHECKPOINT` is the unpaced case: 

```text
LOG:  checkpoint starting: immediate force wait
LOG:  checkpoint complete: wrote 10138 buffers (61.9%); 0 WAL file(s) added, 0 removed, 8 recycled;
      write=0.055 s, sync=0.210 s, total=0.321 s; sync files=313, longest=0.005 s, average=0.001 s;
      distance=131882 kB, estimate=539953 kB; lsn=3/236669F8, redo lsn=3/236669C0
```

Ten thousand pages written in 55 ms, then 210 ms fsyncing 313 files. The `redo lsn` is 56 bytes before the `lsn` of the record itself; eight WAL segments were recycled for reuse. Since 15 every checkpoint logs a line like this by default. 

A checkpoint too soon after the last one is the classic symptom of `max_wal_size` set too small for the write rate. `checkpoint_warning` (30 s) logs it, and the lab tripped it during its bulk load: 

```text
LOG:  checkpoints are occurring too frequently (8 seconds apart)
HINT:  Consider increasing the configuration parameter "max_wal_size".
```

Frequent checkpoints cost more than the writes. Part 1 showed that [the first change to a page after a checkpoint logs the whole page](https://canery.in/blogs/postgresql-foundations-memory-layer#the-full-page-image); more checkpoints mean more full-page images, so a smaller interval partly defeats itself. 

The checkpointer has a second job that is easy to miss: it is the process that fsyncs data files on behalf of everyone. When a backend or the background writer writes a dirty page, it does not fsync the file; it appends a request to a queue in shared memory — `CheckpointerShmem`, sized to one slot per shared buffer — and the checkpointer fsyncs every requested file at its next checkpoint. If the queue is full, the backend first tries to compact it by removing duplicates; if that fails, or the checkpointer is not running, the backend does its own fsync and `buffers_backend_fsync` counts it. A queue more than half full sets the checkpointer's latch to hurry it along.  Figure 16 draws the queue.

![A backend writes a page and appends an fsync request to a shared queue of NBuffers slots; the checkpointer drains the queue at its next checkpoint; a full queue is compacted, and if still full the backend fsyncs itself and buffers_backend_fsync increments](https://minio.canery.in/media/fig-16-fsync-queue-postgresql-foundations-process-layer.png)

*Figure 16 — Backends write pages; the checkpointer fsyncs files. The queue between them is the reason `buffers_backend_fsync` should be zero.*

`pg_stat_bgwriter` is where 16 reports all of this — `checkpoints_timed`, `checkpoints_req`, `checkpoint_write_time`, `checkpoint_sync_time`, `buffers_checkpoint` — under a name that stopped being accurate when the checkpointer was split out of the background writer in 9.2. 17 fixes the name: those columns move to a new `pg_stat_checkpointer` view.  

## The background writer, and why your backend still writes pages

When a backend needs a buffer and the pool is full, [the clock sweep](https://canery.in/blogs/postgresql-foundations-memory-layer#the-clock-sweep-how-a-page-gets-evicted) picks a victim. If the victim is dirty, the backend must write it — after flushing the WAL that describes it — before it can reuse the slot, and that write happens inside the backend's query. The background writer exists to make that rare. It issues writes of dirty buffers a little ahead of where the sweep hand is going, so that when a backend arrives at a buffer it is usually already clean. 

Its algorithm, in `BgBufferSync`, is a prediction. Every `bgwriter_delay` (200 ms) it reads how many buffers backends allocated since the last round, keeps a moving average over 16 rounds, multiplies that by `bgwriter_lru_multiplier` (2.0) to estimate the next round's demand, and scans ahead of the hand until it has found that many reusable buffers, writing the dirty ones it passes, up to `bgwriter_lru_maxpages` (100) per round. If it laps the hand with nothing being allocated — or if `lru_maxpages` is 0, which disables it — it hibernates, sleeping fifty times its normal delay until a backend wakes it.   The settings are in `postgresql.conf` only; they cannot be changed per session.

The background writer does not fsync, does not checkpoint, and does not decide which pages are important; it cleans whatever the sweep is about to reach. It also does not write very much on many workloads. The lab's is one of them. After dirtying 10,137 pages and checkpointing, `pg_stat_io` says: 

```text
  backend_type  | context | writes | fsyncs | extends | evictions
----------------+---------+--------+--------+---------+-----------
 checkpointer   | normal  |  10137 |    312 |         |
 client backend | normal  |      0 |      0 |    9238 |         0
```

The checkpointer wrote every dirty page. The backends wrote none and evicted none — the two tables fit in the pool — and merely extended files by 9,238 pages. The background writer has no row at all. Figure 17 is that table as a picture.

![Stacked bar of page writes by process type from the lab: checkpointer 10,137, client backends 0 writes and 9,238 extends, background writer 0; a second bar shows the checkpointer's 312 fsyncs against the backends' 0](https://minio.canery.in/media/fig-17-who-wrote-postgresql-foundations-process-layer.png)

*Figure 17 — Who wrote the lab's dirty pages. On a pool that never filled, the answer is "the checkpointer, at the checkpoint", and the background writer had nothing to do.*

One detail in that step is worth pausing on. During the same step, `pg_stat_bgwriter.buffers_backend` rose by 1,351 — while `pg_stat_io` says backends wrote nothing. The old column counts relation extensions as backend writes. That is one reason 17 removes `buffers_backend` and `buffers_backend_fsync` from `pg_stat_bgwriter` as redundant with `pg_stat_io`, and it is a reason to read `pg_stat_io` on 16 and later rather than the older view.  

The honest summary is that the background writer matters when the pool is full, the workload dirties pages faster than checkpoints clean them, and backends would otherwise pay write latency inside queries. On a server where the working set fits, or where the checkpointer keeps up, it hibernates, and `buffers_clean` stays near zero. That is not a fault.

## The WAL writer and what a commit waits for

Part 1 described [how a WAL record gets into the buffer ring](https://canery.in/blogs/postgresql-foundations-memory-layer#wal-buffers-the-memory-that-must-reach-disk-first) and that a committing backend calls `XLogFlush` to write and fsync the ring up to its commit record before it reports success. That is `synchronous_commit = on`, the default, and under it the committing backend does the flush itself. So what is the WAL writer for?

Two things, per its source header. It writes out WAL pages that have filled but that no backend has flushed yet, so backends less often find themselves writing pages they did not dirty. And it guarantees that a transaction committed *without* waiting — `synchronous_commit = off` — reaches disk within a knowable time: at most three times `wal_writer_delay`, 600 ms with the default 200 ms. Backends can still write WAL when it falls behind, so it is not an essential process and shuts down quickly.   Figure 18 contrasts the two commit paths.

![Sequence diagram of two commits: with synchronous_commit on, the backend writes its commit record, calls XLogFlush, waits for fdatasync and then replies to the client; with off, the backend writes the record and replies immediately, and the WAL writer flushes it within three delay cycles](https://minio.canery.in/media/fig-18-commit-paths-postgresql-foundations-process-layer.png)

*Figure 18 — What a commit waits for. With `off`, the client hears "committed" before the disk does; the WAL writer closes the gap within 600 ms.*

The lab measured the difference with 5,000 single-row transactions from one client: 

```text
 synchronous_commit | seconds | tps    | wal_write | wal_sync
--------------------+---------+--------+-----------+---------
 on                 |  5.76   |    867 |     5000  |    5000
 off                |  0.36   | 13,771 |      105  |       2
```

Sixteen times the throughput, and the second row explains the first: five thousand commits became two `fdatasync` calls — the default `wal_sync_method` on Linux — because the WAL writer batched them.  Figure 19 draws it.

![Two pairs of bars: transactions per second 867 versus 13,771, and fdatasync calls 5,000 versus 2, for synchronous_commit on versus off over 5,000 single-row commits](https://minio.canery.in/media/fig-19-sync-commit-postgresql-foundations-process-layer.png)

*Figure 19 — The commit is not slow because of the write. It is slow because of the wait for the disk to confirm it.*

What `off` risks is precisely stated in the docs and worth stating precisely here, because it is often overstated. A crash inside the window loses the transactions committed in it — up to 600 ms of them. It cannot corrupt the database: recovery replays WAL to the last flushed record and stops, and because transactions replay in commit order, a transaction cannot survive one it depended on. The database comes back as if those last transactions had been cleanly rolled back.  Certain commands — `DROP TABLE`, `PREPARE TRANSACTION` — commit synchronously regardless, so the file system and the catalog cannot disagree. 

The setting has five values, and the four that wait differ only in *what* they wait for: `local` waits for the local flush; `remote_write` for a synchronous standby to have written the record; `on` for the standby to have flushed it; `remote_apply` for the standby to have applied it. Without a synchronous standby, all four are the same as `on`.  It is a per-session, even per-transaction setting, which is the right way to use it: `off` for the bulk load that can be rerun, `on` for the payment.

`commit_delay` is not asynchronous commit and is ignored under it. It is a synchronous trick: a committing backend that sees at least `commit_siblings` (5) other active transactions waits `commit_delay` microseconds (0 by default) before flushing, in the hope that the others reach their commit in that window and one flush serves them all.  The lab's `wal_sync` of 2 for 5,000 commits is that same batching, obtained for free by not waiting at all.

## Autovacuum, part one: how it decides

The part 1 lab showed that an `UPDATE` [writes a new row version and leaves the old one in place](https://canery.in/blogs/postgresql-foundations-memory-layer#a-two-byte-update-that-cost-7544-bytes). A `DELETE` does the same without the new version. Both leave a **dead tuple**: a row version no transaction that starts from now will ever see, still occupying its bytes in the page and its entry in every index. Somebody has to remove them. That somebody is a vacuum, and *deciding* when to run one is a different job from *running* one. This section is the decision; the next is the work.

Two kinds of process do the deciding. The **launcher** is always running, started by the postmaster when `autovacuum = on`. It does not connect to any database and does not look at any table. Its job is to pick a database and a moment, and ask the postmaster for a worker. The **worker**, once forked and connected to that database, does the rest: it reads the statistics for every table and decides which have crossed their thresholds.  Figure 20 is the handshake.

![Sequence: launcher wakes, picks a database, sets a flag in autovacuum shared memory, sends PMSIGNAL_START_AUTOVAC_WORKER to the postmaster; postmaster forks; child attaches, reads the flag, connects to the database, evaluates every table against its thresholds, vacuums the ones that qualify, sends SIGUSR2 to the launcher on exit](https://minio.canery.in/media/fig-20-autovacuum-handshake-postgresql-foundations-process-layer.png)

*Figure 20 — The launcher never forks and never sees a table. It asks; the postmaster forks; the worker decides.*

### The launcher's clock

The launcher tries to start one worker in each database every `autovacuum_naptime` (60 s). With N databases that means a launch every naptime/N seconds, round-robin, so each database is visited about once a minute. The sleep is floored at 100 ms and capped at 300 s.  The lab has two databases, so the launcher woke every 30 s, alternating between them; the `UPDATE` landed just after a visit to the other database, and the worker came at the next visit to this one, 30 s later. Had it landed just after a visit to *this* database, the wait would have been 60 s. A table that crosses its threshold waits, on average, half a naptime, and in the worst case a whole one, before anyone looks. 

At most `autovacuum_max_workers` (3) workers exist at once. If a worker finishes early it signals the launcher, which may start another immediately; if all three are busy, the next database waits. In 16 the worker count needs a restart to change; 18 adds `autovacuum_worker_slots` so the ceiling is fixed at start and the count can move at runtime beneath it.   Figure 21 draws the rhythm.

![Timeline of the launcher over three minutes with two databases: a wake every 30 s alternating between them, a worker forked at each wake that finds work, three worker slots shown filling and emptying, and the lab's UPDATE placed just after a visit so its worker comes 60 s later](https://minio.canery.in/media/fig-21-launcher-round-postgresql-foundations-process-layer.png)

*Figure 21 — The launcher's round. Arrival time is naptime divided by database count, plus however long the three slots are busy.*

### The worker's arithmetic

Inside a database, the worker evaluates every table with one function, `relation_needs_vacanalyze`, against three thresholds. Each is a base count plus a fraction of the table's row count as `pg_class.reltuples` last recorded it:   

```text
vacuum   when n_dead_tup         > autovacuum_vacuum_threshold        (50)   + 0.2 × reltuples
vacuum   when n_ins_since_vacuum > autovacuum_vacuum_insert_threshold (1000) + 0.2 × reltuples
analyze  when n_mod_since_analyze > autovacuum_analyze_threshold      (50)   + 0.1 × reltuples
```

The insert rule is from 13 and exists so that append-only tables — which never produce dead tuples — still get vacuumed for freezing and for the visibility map.  For the lab's tables the thresholds come out to 20,050 / 21,000 / 10,050 on `customers` and 200,050 / 201,000 / 100,050 on `orders`.  Figure 22 draws the rule.

![The vacuum threshold as a line, 50 plus 0.2 times row count, plotted against table size with the lab's two tables marked at 100,000 rows and 20,050 tuples and at 1,000,000 rows and 200,050 tuples, and a note that on a billion-row table the threshold is 200 million dead tuples](https://minio.canery.in/media/fig-22-threshold-line-postgresql-foundations-process-layer.png)

*Figure 22 — The default threshold is 20% of the table. On a million-row table that is 200,000 dead rows before anything happens; on a billion-row table, 200 million. This is the setting large tables override per table.*

The counts the rule compares against — `n_dead_tup`, `n_ins_since_vacuum`, `n_mod_since_analyze` in `pg_stat_all_tables` — are estimates. Each `INSERT`, `UPDATE` and `DELETE` reports to the cumulative statistics system, and the docs call the result semi-accurate, because under heavy load some reports can be lost.  A table that "should have been vacuumed by now" and was not is sometimes a table whose dead-tuple estimate ran low. Every threshold and scale factor can be set per table as a storage parameter, and on large tables that is the normal thing to do: `autovacuum_vacuum_scale_factor = 0.01` and a fixed threshold, or, in 18, `autovacuum_vacuum_max_threshold` to cap the count regardless of scale factor.  

There is a fourth rule that overrides the other three. Every table records the oldest transaction ID any of its rows still carries, `relfrozenxid`, and transaction IDs are 32-bit counters that wrap. A table whose `relfrozenxid` is more than `autovacuum_freeze_max_age` (200 million) transactions old is vacuumed whether or not it has dead tuples, and — the docs are explicit — whether or not autovacuum is enabled.  If that vacuum does not happen, the server begins warning at 40 million transactions before wraparound, and at 3 million it stops accepting commands.  The lab's tables were about 10,000 transactions old, so 199,990,000 short. 

### The budget, and why more workers do not help

A running vacuum is throttled. Every page it touches adds to a cost balance — 1 for a buffer hit, 2 for a miss, 20 for dirtying a page — and when the balance reaches the cost limit the process sleeps `cost_delay × balance / limit` milliseconds, capped at four times the delay, and resets. For autovacuum the delay is `autovacuum_vacuum_cost_delay`, 2 ms since 12 (20 ms before), and the limit is `autovacuum_vacuum_cost_limit`, which at its default of −1 falls back to `vacuum_cost_limit`, 200. A manual `VACUUM` has `vacuum_cost_delay = 0` and is not throttled at all. 

The consequence most people miss is in `AutoVacuumUpdateCostLimit`: the limit is *divided* among the running workers. Each worker's limit is `vacuum_cost_limit / nworkers_for_balance`, minimum 1, so that — as the docs put it — the total I/O impact is the same however many workers are running. A table with its own cost storage parameters is left out of the balance.  Figure 23 is the picture that makes the "add workers" mistake impossible to make.

![Two panels with the same total bandwidth: one worker with a cost limit of 200 units per 2 ms, and three workers each with 66 units per 2 ms; the sum is the same width in both panels](https://minio.canery.in/media/fig-23-cost-balance-postgresql-foundations-process-layer.png)

*Figure 23 — Three workers do not vacuum three times as fast. They share one budget. To vacuum faster, raise the budget.*

That budget is small. 200 units every 2 ms is 100,000 units a second: 50,000 page misses a second, or 5,000 dirtied pages a second, which is about 39 MB/s of dirtying on an NVMe drive that could do far more. A table producing dead rows faster than that will fall behind no matter how many workers are assigned to it. The section on math turns this into a formula.

## Autovacuum, part two: what the worker actually does

Once a worker has picked a table, it runs the same code a manual `VACUUM` does. That code has a state machine, visible in `pg_stat_progress_vacuum`, and understanding the machine explains every vacuum performance question that matters.  Figure 24 is the machine; the lab sampled it every 10 ms.

![State machine of vacuum phases: initializing, scanning heap, vacuuming indexes, vacuuming heap, back to scanning heap if the heap is not finished, then cleaning up indexes, truncating heap, performing final cleanup; the loop through vacuuming indexes and vacuuming heap is marked as repeating once per fill of the dead-tuple memory](https://minio.canery.in/media/fig-24-vacuum-phases-postgresql-foundations-process-layer.png)

*Figure 24 — The loop in the middle is the whole story. Each time the dead-tuple memory fills, vacuum leaves the heap, walks every index in full, comes back, and resumes where it stopped.*

The phases are: 

1. **Scanning heap.** Walk the table page by page, skipping pages the visibility map says have nothing to do. On each page, prune dead row versions to stubs and record each stub's tuple identifier in memory. Freeze old tuples where required.
2. **Vacuuming indexes.** For every index on the table, scan the *entire index* and remove every entry whose tuple identifier is in the remembered list.
3. **Vacuuming heap.** Revisit the heap pages that had dead tuples and turn the stubs into free space, now that no index points at them.
4. If the heap scan is not finished — because step 1 stopped when memory filled — go back to step 1 and resume where it left off. Otherwise:
5. **Cleaning up indexes.** A per-index cleanup pass that may update index statistics.
6. **Truncating heap.** If the trailing pages are entirely empty, take a brief `ACCESS EXCLUSIVE` lock and give them back to the file system. This is the only case in which a plain vacuum shrinks a file. 
7. **Final cleanup.** Update `pg_class`, report to the statistics system.

Step 2 is the expensive one and step 4 is the multiplier. Index vacuuming is a full scan of each index regardless of how many entries it will remove, because an index has no way to find entries by heap location except by reading everything. So the number of times step 2 runs is the number of times the dead-tuple memory filled, and *that* is the number `maintenance_work_mem` controls.  

The lab's `pg_stat_progress_vacuum` sample, at 1 MB: 

```text
 phase             | heap_total | heap_scanned | heap_vacuumed | index_vac_count | max_dead | num_dead
-------------------+------------+--------------+---------------+-----------------+----------+---------
 initializing      |          0 |            0 |             0 |               0 |        0 |        0
 scanning heap     |       7693 |            0 |             0 |               0 |   174761 |        0
 scanning heap     |       7693 |          249 |             0 |               0 |   174761 |    25896
 ...
 scanning heap     |       7693 |         1677 |             0 |               0 |   174761 |   174408
 vacuuming indexes |       7693 |         1678 |             0 |               0 |   174761 |   174512
 vacuuming heap    |       7693 |         1678 |            61 |               1 |   174761 |   174512
 vacuuming heap    |       7693 |         1678 |          1663 |               1 |   174761 |   174512
 scanning heap     |       7693 |         1728 |          1677 |               1 |   174761 |     5200
 ...
 vacuuming indexes |       7693 |         3356 |          1677 |               1 |   174761 |   174512
 vacuuming heap    |       7693 |         3356 |          3342 |               2 |   174761 |   174512
 scanning heap     |       7693 |         3359 |          3355 |               2 |   174761 |      312
 ...
```

`max_dead_tuples` is 174,761. `num_dead_tuples` climbs to 174,512 — the store stops accepting when fewer than 291 slots remain — the phase flips to `vacuuming indexes`, `index_vacuum_count` becomes 1, the heap is vacuumed through page 1,677, and the scan resumes at 1,678 with the counter reset. The second cycle fills at page 3,356. Five times in all, 1,375 distinct samples.

### The memory arithmetic

In 16 the remembered list is a plain sorted array of 6-byte tuple identifiers, and the number of slots is `(maintenance_work_mem − 8) / 6`, capped at 1 GB regardless of the setting — 178,956,970 identifiers — and at the table's page count times 291.   So the number of index passes for a vacuum is, to within one:

```text
passes ≈ ⌈ dead_tuples × 6 bytes / maintenance_work_mem ⌉
```

At the 64 MB default that is one pass per 11.2 million dead tuples. A table that accumulates 50 million dead rows between vacuums — a day of churn on a large table — gets five passes at the default and one at 320 MB. Figure 25 draws the trace on the lab's numbers.

![Small multiples: a heap of 7,693 pages being scanned left to right; each time the dead-tuple store fills at 174,761 the scan pauses, both indexes are walked in full, the heap pages so far are vacuumed, and the scan resumes; five such cycles at 1 MB against one at 256 MB](https://minio.canery.in/media/fig-25-index-pass-trace-postgresql-foundations-process-layer.png)

*Figure 25 — Five index passes at 1 MB, one at 256 MB, on the same 800,000 dead tuples. The store's size is the only variable.*

Two version notes. Autovacuum uses `autovacuum_work_mem` if it is set and `maintenance_work_mem` otherwise, and raising either above 1 GB does nothing for the dead-tuple list in 16.  17 replaces the array with a radix tree, `TidStore`, keyed by block number with a bitmap of offsets per block: far more compact, and no longer capped at 1 GB. The same 800,000 dead tuples would need a fraction of the memory on 17, and the progress view's columns change to `max_dead_tuple_bytes` and `num_dead_item_ids` to match.  

### The horizon

A dead tuple can be removed only when no transaction can still see it. "No transaction" means no transaction *anywhere in the cluster*, because every snapshot records the oldest transaction it must respect and vacuum takes the minimum over all of them. The lab's idle `REPEATABLE READ` session held a snapshot from before the delete; its `backend_xmin` was 71185; the vacuum's removable cutoff was 71185; and 800,000 tuples were "dead but not yet removable". The vacuum still scanned all 7,693 pages to discover that. When the session committed, the cutoff moved, and the same vacuum removed everything in one pass. 

Four things hold the horizon back: a long-running transaction, a session left `idle in transaction`, a replication slot whose consumer has gone away, and a prepared transaction nobody committed. All four are visible — `pg_stat_activity.backend_xmin`, `pg_replication_slots.xmin`, `pg_prepared_xacts` — and all four are invisible to autovacuum's thresholds, which is why a table can be vacuumed on schedule every hour and still bloat. 14 added `idle_session_timeout` beside `idle_in_transaction_session_timeout` for the second cause; 18 adds `idle_replication_slot_timeout` for the third.  

### What vacuum does not do

Plain `VACUUM` takes a `SHARE UPDATE EXCLUSIVE` lock, runs beside reads and writes, and makes space reusable *within the table*. It returns space to the operating system only in step 6, by truncating wholly-empty trailing pages. A table that bloated to ten times its size and then had its rows deleted stays ten times its size until something rewrites it. `VACUUM FULL` is that something: a complete rewrite under `ACCESS EXCLUSIVE`, needing the extra disk space while it runs. It is a different operation with a similar name, not a stronger vacuum.  Plain vacuum's own options are narrower than they look: `INDEX_CLEANUP` defaults to `AUTO`, which skips the index passes when there are very few dead tuples; `TRUNCATE` defaults to on and can be turned off per table to avoid the brief exclusive lock; `FREEZE` just zeroes the two freeze ages. 

Manual `VACUUM` can use parallel workers — one per index larger than `min_parallel_index_scan_size`, at most `max_parallel_maintenance_workers` (2), and only for the index phases; the heap scan is never parallel. The lab's manual vacuums did this unasked: "launched 1 parallel vacuum worker for index vacuuming (planned: 1)". Autovacuum in 16 does not.   And near wraparound, the failsafe added in 14 (`vacuum_failsafe_age`, 1.6 billion) makes a vacuum abandon its cost delay and skip index vacuuming altogether, so the freeze that prevents shutdown happens as fast as the disk allows. 

## Parallel workers and the shared pool

A parallel query is one more case of "only the postmaster forks", and the general framework beneath it explains the `Workers Planned: 6, Workers Launched: 1` line.

PostgreSQL has a **background worker** framework. An extension loaded at startup can register a worker with `RegisterBackgroundWorker`, and any backend can request one at runtime with `RegisterDynamicBackgroundWorker`; either way the request goes into a slot array in shared memory sized to `max_worker_processes` (8), the postmaster is signalled, and the postmaster forks.   Parallel query workers, logical replication apply workers and extension workers all come out of those eight slots. `max_parallel_workers` (8) is the share of them parallel queries may use; `max_parallel_workers_per_gather` (2) and `max_parallel_maintenance_workers` (2) are per-operation ceilings within that share. 

The planner decides how many workers a scan *should* have from the table's size — one at `min_parallel_table_scan_size` and roughly one more each time the table triples — capped by `max_parallel_workers_per_gather`, or fixed by the table's `parallel_workers` storage parameter. That decision becomes `Workers Planned`. At execution the `Gather` node asks for that many dynamic background workers, and it gets however many slots are free at that instant, bounded by both pool settings. That becomes `Workers Launched`. The leader runs the parallel portion of the plan too, unless `parallel_leader_participation` is off, which is why a plan with zero launched workers still completes.   Figure 26 draws the two numbers and where each comes from.

![A Gather node above a Parallel Seq Scan, with Workers Planned fed from the planner's size rule and the per-gather ceiling, and Workers Launched fed from the shared pool of max_parallel_workers slots, some already occupied; the lab's 6 planned and 1 launched shown](https://minio.canery.in/media/fig-26-planned-vs-launched-postgresql-foundations-process-layer.png)

*Figure 26 — Planned is a decision made against a ceiling. Launched is a request made against a pool. The planner cannot see the pool, so the two can disagree.*

The lab caught a leader and its four workers in `pg_stat_activity`: one `client backend` with `leader_pid` null, four `parallel worker` rows carrying its pid, all `active`.   Each of them had its own `work_mem`, which is the point part 1 made about [per-process budgets](https://canery.in/blogs/postgresql-foundations-memory-layer#local-memory-work_mem-and-its-family) and is not repeated here.

What cannot be parallel is a shorter list than it used to be but still matters: a query that writes or locks rows (except the `SELECT` under `CREATE TABLE AS`, `SELECT INTO` and materialized views), a query that might be suspended — a cursor, a PL/pgSQL `FOR ... IN query` loop — a query using a function marked `PARALLEL UNSAFE`, which is every user-defined function until it is marked otherwise, and any query already running inside a parallel worker. 

## The rest of the cast

Six more process kinds exist on some servers and not others. Each is a one-line answer to "why is that in my process list", and the condition that makes it appear.

- **The startup process** runs crash recovery after an unclean shutdown — the lab saw it after the `SIGKILL` — and, on a standby, stays alive as the process that replays WAL from the primary. 
- **The archiver** exists when `archive_mode = on`, and copies each finished WAL segment by running `archive_command` or, since 15, calling an `archive_library` module. 
- **Walsenders** exist one per streaming replica or logical subscriber, up to `max_wal_senders` (10). A **walreceiver** is their counterpart on a standby.
- **The logical replication launcher** is present by default and starts **apply workers** for subscriptions, up to `max_logical_replication_workers`; 16 added parallel apply workers for large transactions.
- **The statistics collector** no longer exists. Until 14 it was a process that received per-table counters over UDP and wrote them to temporary files for backends to read. 15 moved the cumulative statistics into shared memory and deleted the process, the UDP traffic and `stats_temp_directory`. If a tuning guide tells you to put the stats temp directory on a RAM disk, it predates 15. 
- **I/O workers** are new in 18. `io_method` defaults to `worker`: backends push read requests onto a shared submission queue and `io_workers` (3) separate processes perform them with ordinary synchronous system calls, so the backend can issue several reads and wait for all of them. `io_method = io_uring` does the same from within the backend on Linux 5.1+, and `sync` is the pre-18 behaviour.  Figure 27 is the whole cast, with the condition that summons each optional member.

![Map of every process kind: the always-present five and the postmaster in the centre; around them the conditional ones each with its trigger — client backend per connection, parallel worker per Gather, autovacuum worker per launcher request, archiver when archive_mode on, walsender per replica, walreceiver and startup on a standby, apply worker per subscription, I/O workers from 18; the statistics collector shown crossed out as removed in 15](https://minio.canery.in/media/fig-27-the-cast-postgresql-foundations-process-layer.png)

*Figure 27 — Every process a PostgreSQL server can run in 16, and one it no longer runs. The condition beside each optional process is the one-line answer to "why is that here".*

Every one of them appears in `pg_stat_activity` with its `backend_type`, since 10 for most and 14 for the archiver, and every one of them is a child of the postmaster.  

## The math

Five formulas cover the process layer's numbers. Each is stated, then checked against a lab number.

### Autovacuum arrival time

With N databases and a naptime of T, the launcher visits each database every T seconds, so a table that crosses its threshold at a uniformly random moment waits an expected T/2 and at most T before a worker looks, plus any queueing for one of the `autovacuum_max_workers` slots:

$$
t_{\text{arrive}} \in \left[\,0,\; T\,\right] + t_{\text{queue}}, \qquad \mathbb{E}[t_{\text{arrive}}] = \tfrac{T}{2} + t_{\text{queue}}
$$

With T = 60 s and no queueing, the expected delay is 30 s and the worst case 60 s. The lab drew 30.   Halving `autovacuum_naptime` halves both; it does not make vacuum itself faster.

### Index passes per vacuum

In 16, with D dead tuples, M bytes of `maintenance_work_mem` (or `autovacuum_work_mem`), 6 bytes per identifier, and a 1 GB ceiling:

$$
\text{passes} = \left\lceil \frac{D}{\min\!\left(\dfrac{M - 8}{6},\; 178{,}956{,}970\right) - 291} \right\rceil
$$

D = 800,000, M = 1 MB: (1,048,576 − 8) / 6 = 174,761; minus 291 is 174,470; 800,000 / 174,470 = 4.59; five passes. M = 256 MB: 44.7 million slots; one pass.    Each pass reads every index page once, so the index I/O of a vacuum is passes × (sum of index sizes); the heap is read once regardless. On 17 the denominator is no longer a constant 6 bytes and the ceiling is gone. 

### Autovacuum throughput ceiling

With cost limit L units, delay d seconds, and per-page costs of 1 (hit), 2 (miss), 20 (dirty), the throttle allows L/d units per second, divided among the running workers:

$$
\text{pages/s} = \frac{L}{d \cdot c_{\text{page}}}\quad\text{per cluster, not per worker}
$$

Defaults L = 200, d = 0.002 s: 100,000 units/s; at 2 units per miss, 50,000 misses/s (390 MB/s of reads); at 20 units per dirtied page, 5,000 dirty pages/s (39 MB/s).   A workload dirtying more than 39 MB/s of pages that need vacuuming will outrun autovacuum at the defaults whatever the worker count. Raising `autovacuum_vacuum_cost_limit` raises the ceiling linearly; adding workers does not move it.

### Recovery time bound

Crash recovery replays WAL from the last redo point. With a checkpoint every T seconds at completion target c, the redo point is at most about (1 + c) × T old when a crash happens, and the WAL to replay is at most `max_wal_size` plus what accumulated during the current checkpoint:

$$
\text{WAL to replay} \lesssim \max\!\big(\text{rate} \times (1 + c)\,T,\; \texttt{max\_wal\_size}\big)
$$

With T = 300 s, c = 0.9, and a server writing 5 MB/s of WAL, that is up to about 2.8 GB — more than the 1 GB `max_wal_size`, which is why on that server the WAL trigger fires first and checkpoints come every 200 s.   Recovery replays that at whatever rate the disk and the startup process allow. This is the trade `checkpoint_timeout` makes: longer intervals mean fewer full-page images and less write amplification, and longer recovery.

### Connection capacity

Process slots are fixed at start:

$$
\text{MaxBackends} = \texttt{max\_connections} + \texttt{autovacuum\_max\_workers} + 1 + \texttt{max\_worker\_processes} + \texttt{max\_wal\_senders}
$$

Defaults: 100 + 3 + 1 + 8 + 10 = 122.  Every one of those slots has a `PGPROC` entry, a share of the lock table, and a place in the shared-invalidation array; every one that is *used* has 13–15 MB of private memory on top, from the lab's measurement, and more once its caches warm.  Multiply, and compare to RAM.

## Implementation

The process-layer toolkit is a dozen queries. All of them run on 16; version notes follow the block. The downloadable `run_lab.py` produced this post’s numbers.

```sql
-- 1. The census: every process, its type, and what it is waiting on.
select pid, backend_type, state, wait_event_type, wait_event,
       leader_pid, backend_xmin, now() - xact_start as xact_age
from pg_stat_activity
order by backend_type, pid;

-- 2. Who wrote pages, and who fsynced. (16+)
select backend_type, context, writes, fsyncs, extends, evictions, reuses
from pg_stat_io
where object = 'relation' and coalesce(writes, 0) + coalesce(evictions, 0) + coalesce(extends, 0) > 0
order by writes desc nulls last;

-- 3. Checkpoint accounting. (16: pg_stat_bgwriter; 17+: pg_stat_checkpointer)
select checkpoints_timed, checkpoints_req,
       checkpoint_write_time, checkpoint_sync_time,
       buffers_checkpoint, buffers_clean, buffers_backend, buffers_backend_fsync
from pg_stat_bgwriter;

-- 4. Autovacuum debt: how far each table is past, or short of, its threshold.
select c.relname,
       s.n_dead_tup,
       (coalesce((select option_value::int from pg_options_to_table(c.reloptions)
                  where option_name = 'autovacuum_vacuum_threshold'),
                 current_setting('autovacuum_vacuum_threshold')::int)
        + coalesce((select option_value::float from pg_options_to_table(c.reloptions)
                    where option_name = 'autovacuum_vacuum_scale_factor'),
                   current_setting('autovacuum_vacuum_scale_factor')::float)
          * c.reltuples)::bigint as threshold,
       s.last_autovacuum, s.autovacuum_count
from pg_class c join pg_stat_all_tables s on s.relid = c.oid
where c.relkind = 'r' and c.reltuples > 0
order by s.n_dead_tup desc limit 20;

-- 5. What is holding the xmin horizon back.
select 'backend' as kind, pid::text as who, backend_xmin::text::bigint as xmin,
       state, now() - xact_start as open_for
from pg_stat_activity where backend_xmin is not null
union all
select 'slot', slot_name, xmin::text::bigint, active::text, null
from pg_replication_slots where xmin is not null
union all
select 'prepared', gid, transaction::text::bigint, null, now() - prepared
from pg_prepared_xacts
order by xmin nulls last;

-- 6. Distance to a forced anti-wraparound vacuum, per table.
select relname, age(relfrozenxid) as xid_age,
       current_setting('autovacuum_freeze_max_age')::bigint - age(relfrozenxid) as until_forced
from pg_class where relkind = 'r' order by xid_age desc limit 10;

-- 7. Watch a running vacuum.
select p.pid, c.relname, p.phase,
       p.heap_blks_scanned, p.heap_blks_total,
       p.index_vacuum_count, p.num_dead_tuples, p.max_dead_tuples
from pg_stat_progress_vacuum p join pg_class c on c.oid = p.relid;

-- 8. WAL writer and commit accounting: all eight counters of pg_stat_wal on 16.
select wal_records, wal_fpi, wal_bytes, wal_buffers_full, wal_write, wal_sync,
       wal_write_time, wal_sync_time
from pg_stat_wal;

-- 9. Compute the index-pass count before you run the vacuum.
select ceil(n_dead_tup::numeric /
            (least((pg_size_bytes(current_setting('maintenance_work_mem')) - 8) / 6,
                   178956970) - 291)) as index_passes_at_current_mwm
from pg_stat_all_tables where relname = 'orders';

-- 10. Ask the postmaster to start a fresh set of children: the polite way to
--     apply a reloadable setting to every process.
select pg_reload_conf();
```

Two habits make the counters mean something. Reset the shared views at the start of an experiment — `pg_stat_reset_shared('bgwriter')`, `('wal')`, `('io')`, `('archiver')` and `('recovery_prefetch')` are the five accepted arguments on 16 — so cumulative numbers describe one run.   And remember that `pg_stat_progress_vacuum` is one of six progress views; `_analyze`, `_cluster`, `_create_index`, `_copy` and `_basebackup` show the same kind of phase machine for their operations. 

Version notes, because the views moved under the toolkit:      

| Item                                               | 16                                       | 17                                                                                                              | 18                                                                        |
| -------------------------------------------------- | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Checkpoint counters                                | `pg_stat_bgwriter`                     | `pg_stat_checkpointer`; `buffers_backend*` removed                                                          | same                                                                      |
| Vacuum progress memory columns                     | `max_dead_tuples`, `num_dead_tuples` | `max_dead_tuple_bytes`, `num_dead_item_ids`, `dead_tuple_bytes`, `indexes_total`, `indexes_processed` | same                                                                      |
| Dead-tuple storage                                 | 6-byte array, 1 GB cap                   | `TidStore`, no cap                                                                                            | same                                                                      |
| Vacuum buffer ring (`vacuum_buffer_usage_limit`) | 256 kB                                   | 2 MB                                                                                                            | 2 MB                                                                      |
| `pg_stat_io`                                     | counts,`op_bytes`                      | same                                                                                                            | `read_bytes` / `write_bytes` / `extend_bytes`, `op_bytes` removed |
| `autovacuum_max_workers`                         | restart                                  | restart                                                                                                         | reloadable under`autovacuum_worker_slots`                               |
| Statistics collector                               | gone since 15                            | —                                                                                                              | —                                                                        |
| Asynchronous I/O                                   | —                                       | —                                                                                                              | `io_method`, `io_workers` processes                                   |
| `EXPLAIN ANALYZE`                                | `BUFFERS` opt-in                       | opt-in                                                                                                          | on by default                                                             |

Figure 28 maps which view sees which process.

![Grid of processes against views and log settings: pg_stat_activity covers all; pg_stat_io covers checkpointer, bgwriter, backends, autovacuum workers; pg_stat_bgwriter or pg_stat_checkpointer covers checkpointer and bgwriter; pg_stat_wal covers WAL writer and backends; pg_stat_progress_vacuum covers vacuum workers; log_checkpoints and log_autovacuum_min_duration cover their processes; version markers where a view moved](https://minio.canery.in/media/fig-28-tooling-map-postgresql-foundations-process-layer.png)

*Figure 28 — Which view watches which process, and where the view moved between 16 and 18.*

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** raising `autovacuum_max_workers` to make autovacuum keep up. The workers share one cost budget, divided among them, so eight workers each get a quarter of what two had. Raise `autovacuum_vacuum_cost_limit` — or set it per table on the tables that churn — and only add workers when many tables need vacuuming *at once*. 

**Turning autovacuum off to save I/O.** The anti-wraparound vacuum runs anyway once a table's `relfrozenxid` reaches 200 million transactions of age, and it runs then, at whatever moment that is, with whatever else the server is doing. Meanwhile every table bloats and every index accumulates dead entries. The I/O is not saved; it is deferred with interest. 

**Leaving `maintenance_work_mem` at 64 MB on a large, churning table.** On 16 that is one index pass per 11 million dead tuples. A table that produces 100 million between vacuums walks every index nine times. Set `autovacuum_work_mem` higher, or on 17 stop worrying about this one.  

**Reading `last_autovacuum` as proof of health.** A vacuum that ran and removed nothing — because a snapshot, slot or prepared transaction held the horizon — updates `last_autovacuum` just the same. Check `n_dead_tup` after the vacuum, and check the horizon query. 

**Treating `VACUUM FULL` as a stronger vacuum.** It is a table rewrite under an exclusive lock that needs the table's size again in free space. Use it to recover space once, after the cause of the bloat is fixed. Do not schedule it. 

**Reading `synchronous_commit = off` as "unsafe".** It cannot corrupt the database; it can lose up to 600 ms of committed transactions in a crash. For a load that can be rerun that is a 16× speed-up for free. For a payment it is the wrong setting, and it is a per-transaction setting, so use both.  

**Connection sprawl.** Every connection is a process with 13 MB or more of private memory, a `PGPROC` slot, and a share of every scan of the process array. The design intends a pooler between the application and the server. If `max_connections` is over a few hundred and the server is not enormous, the question is why.  

**Blaming the server for a crash it survived.** `terminating any other active server processes` means one child died and the postmaster reset. The process that died is named in the line above it. The server did what it was built to do; find the child. 

What this post does not cover, by design: the on-disk format of the heap page and the visibility map that lets vacuum skip pages, how the free space map is maintained, TOAST, index internals, how WAL segments are laid out, archived and replayed, and the replication processes beyond naming them — that is part 3. The memory that every process in this post allocates was part 1.

## Key takeaways

- The postmaster never touches your data, and that is precisely why it can survive a child that corrupts shared memory: it does not look, it resets everyone. One killed backend restarting the whole server is the design, not a bug.  
- Only the postmaster forks. The autovacuum launcher, a parallel `Gather`, an extension — every one of them asks and waits. There is one parent, and it is the process that reads nothing.  
- Autovacuum arrives on the launcher's clock, up to a whole `autovacuum_naptime` after a table qualifies, and every running worker shares one cost budget. To vacuum faster, raise the budget, not the headcount.  
- The number of index passes a vacuum makes is `⌈dead tuples × 6 B / maintenance_work_mem⌉` on 16, and each pass reads every index in full. That one setting turns a one-pass vacuum into a five-pass one on the same table.  
- A commit with `synchronous_commit = on` waits for `fdatasync`; with `off` it waits for nothing and the WAL writer flushes within 600 ms. The lab measured 16× between them, and `off` cannot corrupt anything.   

## Try it yourself

All three run on the lab's `proclab` database, or on any 16 server you may restart.

**1.** Set `maintenance_work_mem = '2MB'`, delete 500,000 rows from a copy of `orders` with two indexes, and predict the index-pass count before running `VACUUM (VERBOSE)`. Then check `index scans:` in the output.

<details><summary>Answer</summary>

Slots at 2 MB: (2,097,152 − 8) / 6 = 349,524; minus 291 is 349,233. 500,000 / 349,233 = 1.43, so 2 passes. Query 9 in the Implementation section computes this from `pg_stat_all_tables` before you run it.

</details>

**2.** Open a second `psql`, run `begin; select 1;` and leave it. In the first, delete rows and vacuum. Why does the vacuum *still* remove them, when the worked example's held snapshot did not?

<details><summary>Answer</summary>

`begin; select 1;` in `READ COMMITTED` takes a snapshot per statement and releases it when the statement ends, so between statements the session holds no snapshot and its `backend_xmin` is null. The worked example used `REPEATABLE READ`, whose snapshot lasts the whole transaction. Try `begin isolation level repeatable read; select 1;` and the vacuum is blocked. The horizon is held by snapshots, not by open transactions as such — though a `READ COMMITTED` session in the *middle* of a long statement holds one too.

</details>

**3.** With `max_parallel_workers_per_gather = 4`, run a parallel scan of `orders` in one session while a second session runs `alter table orders set (parallel_workers = 4)` and starts its own scan. Watch `Workers Launched` in the second plan. What ceiling did it hit?

<details><summary>Answer</summary>

`max_parallel_workers` (8) is the pool for the whole server. The first query holds 4; the second is planned for 4 and gets whatever is left — 4 if the first finished, fewer if it is still running. Neither the per-gather setting nor the table option can see the pool.

</details>

## References

Grouped by tier. Access date 2026-09-19 except where noted. The lab captures are available in the download list below.

### Lab downloads

- [`README.md` in the complete lab archive](https://minio.canery.in/media/lab-postgresql-foundations-process-layer.zip) — prerequisites, safe setup, run order, expected measurements, and cleanup.
- [`captures.json` in the complete lab archive](https://minio.canery.in/media/lab-postgresql-foundations-process-layer.zip) — machine-readable process, checkpoint, WAL, vacuum, and parallel-worker measurements.
- [`captures.md` in the complete lab archive](https://minio.canery.in/media/lab-postgresql-foundations-process-layer.zip) — readable captured output quoted throughout the article.
- [`run_lab.py` in the complete lab archive](https://minio.canery.in/media/lab-postgresql-foundations-process-layer.zip) — creates the disposable PostgreSQL setup and runs the process-layer experiments.
- [Lab Downloads](https://minio.canery.in/media/lab-postgresql-foundations-process-layer.zip)

### Sources

**T1 — papers**

- Stonebraker, M., Rowe, L. A. *The Design of POSTGRES.* SIGMOD 1986; UCB/ERL M85/95. https://dsf.berkeley.edu/papers/ERL-M85-95.pdf (accessed 2026-09-17)
- Stonebraker, M., Rowe, L. A., Hirohama, M. *The Implementation of POSTGRES.* IEEE TKDE 2(1), 1990. https://dsf.berkeley.edu/papers/ERL-M90-34.pdf (accessed 2026-09-17)

**T2 — PostgreSQL documentation and release notes**

- PostgreSQL 16 docs, §20.10 Automatic Vacuuming. https://www.postgresql.org/docs/16/runtime-config-autovacuum.html
- PostgreSQL 16 docs, §25.1 Routine Vacuuming. https://www.postgresql.org/docs/16/routine-vacuuming.html
- PostgreSQL 16 docs, §20.4 Resource Consumption. https://www.postgresql.org/docs/16/runtime-config-resource.html
- PostgreSQL 16 docs, VACUUM. https://www.postgresql.org/docs/16/sql-vacuum.html
- PostgreSQL 16 docs, §20.5 Write Ahead Log. https://www.postgresql.org/docs/16/runtime-config-wal.html
- PostgreSQL 16 docs, §30.4 Asynchronous Commit. https://www.postgresql.org/docs/16/wal-async-commit.html
- PostgreSQL 16 docs, §30.5 WAL Configuration. https://www.postgresql.org/docs/16/wal-configuration.html
- PostgreSQL 16 docs, §28.2 The Cumulative Statistics System. https://www.postgresql.org/docs/16/monitoring-stats.html
- PostgreSQL 16 docs, §28.4 Progress Reporting. https://www.postgresql.org/docs/16/progress-reporting.html
- PostgreSQL 16 docs, §15 Parallel Query (15.1–15.3). https://www.postgresql.org/docs/16/how-parallel-query-works.html
- PostgreSQL 16 docs, §48 Background Worker Processes. https://www.postgresql.org/docs/16/bgworker.html
- PostgreSQL 16 docs, §20.3 Connections and Authentication. https://www.postgresql.org/docs/16/runtime-config-connection.html
- PostgreSQL 18 docs, §19.4 Resource Consumption. https://www.postgresql.org/docs/18/runtime-config-resource.html
- PostgreSQL release notes: 10.0, 14.0, 15.0, 17.0, 18.0. https://www.postgresql.org/docs/release/

**T3 — source code (release tags) and mailing list**

- `src/backend/postmaster/postmaster.c`, `autovacuum.c`, `checkpointer.c`, `bgwriter.c`, `walwriter.c`, `bgworker.c`, `fork_process.c`, REL_16_2. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/postmaster
- `src/backend/access/heap/vacuumlazy.c`, `src/backend/commands/vacuum.c`, `src/include/commands/vacuum.h`, `src/include/access/htup_details.h`, REL_16_2.
- `src/backend/access/transam/varsup.c`, REL_16_2 (wraparound limits).
- `src/backend/storage/buffer/bufmgr.c` (`BgBufferSync`), REL_16_2.
- `src/backend/storage/ipc/procsignal.c`, `signalfuncs.c`, `latch.c`, `sinvaladt.c`; `src/include/storage/procsignal.h`, `pmsignal.h`; `src/include/miscadmin.h`, REL_16_2.
- `src/backend/utils/init/postinit.c`, REL_16_2 (`InitializeMaxBackends`, `InitPostgres`).
- `src/backend/access/common/tidstore.c`, REL_17_0.
- `src/backend/storage/aio/method_worker.c` and `src/backend/storage/aio/README.md`, REL_18_0.
- Linnakangas, H. *Let's make PostgreSQL multi-threaded.* pgsql-hackers, 2023-06-05. https://www.postgresql.org/message-id/31cc6df9-53fe-3cd9-af5b-ac0d801163f4@iki.fi

**This series**

- Part 1 — *How PostgreSQL Uses Memory.* https://canery.in/blogs/postgresql-foundations-memory-layer
