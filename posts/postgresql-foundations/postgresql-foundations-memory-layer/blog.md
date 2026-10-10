---
title: "How PostgreSQL Uses Memory"
slug: postgresql-foundations-memory-layer
date: 2026-09-18
updated: 2026-09-18
summary: "PostgreSQL keeps RAM in three pools: shared buffers, WAL buffers and per-process working memory. Real lab numbers show what each pool does, and why."
tags: [databases, postgresql, shared-buffers, write-ahead-log, memory-management, performance, internals]
category: databases
categories: [databases]
series: postgresql-foundations
series_position: 1
tier: L4
difficulty: intermediate
prerequisites: ["SQL and reading an EXPLAIN plan", "what a process and a page of memory are", "having run PostgreSQL at least once"]
reading_minutes: 52
cover_image_url: "https://minio.canery.in/media/cover-postgresql-foundations-memory-layer.png"
cover_image_alt: "Three stacked memory pools of a PostgreSQL server, with one small tangerine page moving from the shared pool towards the log"
canonical_url: "https://canery.in/blogs/postgresql-foundations-memory-layer"
---
> [!NOTE]
> **Insights** — PostgreSQL treats RAM as three pools, not one. A *shared buffer pool* holds 8 KB copies of table and index pages that every server process maps. A small ring of *WAL buffers* holds the log records that must reach disk before any of those pages may. And each process owns *local working memory* that a sort or hash allocates and frees on its own. Almost every memory surprise you will meet — a 60 MB table that fits in cache but leaves 256 KB behind, a 7,544-byte log entry for a two-byte update, a backend that grows by 85 MB and shrinks again — is one of those three pools doing exactly what it was designed to do.

**Level:** intermediate · **You need:** SQL and the habit of reading `EXPLAIN`, a working idea of processes and memory pages, and a PostgreSQL you are allowed to restart · **Time:** ~52 min

PostgreSQL's architecture is usually described as three layers: a **memory layer** that caches pages and log records, a **process layer** of the postmaster and the workers it forks, and a **storage layer** of heap files, indexes and WAL segments on disk. This is the first of three posts, one per layer, and it stays inside the memory layer. Where a mechanism crosses into scheduling or file formats, the text says so and stops. Figure 1 shows the three layers and where this post sits.

![Three horizontal layers labelled memory, process and storage, with the memory layer highlighted and annotated with shared buffers, WAL buffers and per-process memory](https://minio.canery.in/media/fig-01-three-layers-postgresql-foundations-memory-layer.png)

*Figure 1 — The three layers of a PostgreSQL server. This post is the top one; parts 2 and 3 cover the other two.*

> [!TIP]
> **Runnable lab:** The server setup, runner, machine-readable captures, and readable results are listed under [Lab downloads](#lab-downloads) at the end. Use them when you want to reproduce the experiments; the concepts and results needed to follow them remain in this article.

Every number in this post that came from a running server came from that reproducible lab: PostgreSQL 16.2 with its default `postgresql.conf`, a 1,000,000-row table and a 100,000-row table, on a laptop with 16 CPUs, 15 GB of RAM and an NVMe disk. The captured output is quoted verbatim. 16.2 dates from February 2024; as this is written the current releases are 18.6, 17.11 and 16.15, and 19 is in beta. Where 17 or 18 changed a number or a name, the change is named in the sentence.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Shared buffers](#shared-buffers-what-a-buffer-actually-is) · [The clock sweep](#the-clock-sweep-how-a-page-gets-evicted) · [Rings](#rings-why-a-big-scan-leaves-256-kb-behind) · [WAL buffers](#wal-buffers-the-memory-that-must-reach-disk-first) · [Local memory](#local-memory-work_mem-and-its-family) · [Memory contexts](#memory-contexts-how-a-backend-allocates) · [The rest of shared memory](#the-rest-of-shared-memory) · [The math](#the-math) · [Implementation](#implementation) · [Limitations](#limitations-and-common-mistakes)

## Why this matters

You inherit a server with 64 GB of RAM and `shared_buffers = 128MB`, the default. You have read that the number should be 25% of memory, so you set it to 16 GB, restart, and the first thing that happens is that checkpoints get slower and the write latency graph grows teeth.   Nothing in the documentation was wrong. The 25% figure is a starting point for a dedicated server, and the same paragraph says a bigger pool needs a bigger `max_wal_size` to spread its checkpoints out. You just could not see the connection, because you did not know what a checkpoint does to the pool.

Or: a 60 MB reporting table is queried every minute. The server has 128 MB of shared buffers, so the table fits with room to spare, yet every scan reads the whole thing again. `pg_stat_database` reports a 93% hit ratio and everything looks healthy.  The table is not being cached, and the hit ratio cannot tell you, because the table is read through a 32-buffer ring that was designed to *stop* it from being cached.

Or: `work_mem` goes from 4 MB to 256 MB to make one report faster, the report does get faster, and two weeks later the kernel kills a backend at 3 a.m. The setting is a per-operation limit, not a per-connection one, and one parallel query in the lab below runs three sorts and three hash tables at once, each with its own copy.

Each of these is a different pool. Once you can name the pool, the fix is usually one line.

## The problem

PostgreSQL runs one operating-system process per connection.  The postmaster accepts a connection and forks a backend for it; that backend parses, plans and executes every query on that connection until it disconnects. The 1986 design paper chose this over a single multi-threaded server "after much soul searching", giving the team's limited programming resources as the reason, and the 1990 follow-up calls the choice an expedient.  Implementation began at Berkeley in 1986; forty years later it is still the architecture, and it sets the memory problem up precisely.

Processes do not share an address space. If backend A reads block 17 of a table into its own memory and backend B reads the same block, the server holds two copies, and when A updates the block, B's copy is stale. A database cannot work that way. So the copies of pages that backends read and modify must live in memory every process can see, which on Unix means a region of shared memory mapped into each process at startup.  That region is fixed at server start, it can never be freed, and its size is decided by a handful of settings before the first client connects.

Two more facts make the region hard to size. The operating system already caches files: when PostgreSQL reads an 8 KB page from a data file, the kernel keeps a copy in its page cache, so the same bytes may sit in RAM twice.  And durability imposes an order. Before any modified page may be written back to its file, the log records describing the modification must already be on disk.  Those records have to be assembled in memory too, and that memory has to be shared as well, because every backend appends to the same log.

Meanwhile a query needs memory of its own. A sort of a million rows, a hash table of a hundred thousand groups, the parse tree, the catalog cache — none of that belongs in the shared region, and all of it must be freed when the query ends without a leak. So PostgreSQL ends up with three pools, drawn in Figure 2.

![One server box containing a shared memory region with shared buffers, WAL buffers and other structures, several backend boxes each with their own local memory, and beneath them the kernel page cache and the disk](https://minio.canery.in/media/fig-02-three-pools-postgresql-foundations-memory-layer.png)

*Figure 2 — The three pools, and the two layers under them that PostgreSQL does not control. The kernel page cache is not part of PostgreSQL, but it holds copies of the same pages.*

Stated with the defaults of a fresh 16.2 install:

1. **Shared buffers.** `shared_buffers = 128MB`, which is 16,384 slots of 8 KB, each able to hold exactly one page of one table or index.   Every process maps the same slots. A page is copied in from a file at most once, is modified in place, and is written back later by whoever is responsible at the time. The pool has an eviction policy, a locking scheme and a special path for bulk scans; those are the first three body sections below.
2. **WAL buffers.** `wal_buffers = -1`, which means one thirty-second of shared buffers, so 4 MB here.  Every change to a page is described by a record appended to this ring before the change is considered done. The ring is written to its file at every commit.  This is the fourth body section.
3. **Local memory.** `work_mem = 4MB` per sort or hash, `maintenance_work_mem = 64MB` per VACUUM or index build, `temp_buffers = 8MB` for temporary tables, and an allocator that carves everything a backend needs out of a tree of *memory contexts*.    None of this is shared, all of it is per process, and most of it is freed by dropping a whole context at once. Sections five and six.

Around the buffer pool sit about 15 MB of other shared structures: the lock table, the process array, transaction-status caches, the checkpointer's bookkeeping.  They are the seventh section. Below all of it, the kernel page cache is a fourth pool that PostgreSQL neither sizes nor controls, and the whole question of "how much memory does PostgreSQL use" turns on remembering that it exists.

The constraint that ties the pools together is the write-ahead rule. A page copy in shared buffers may be dirtied freely, but it may not be written to its file until the WAL describing the change is safely on disk.   That one rule decides who writes pages, when, and why the first update after a checkpoint costs forty times more than the second.

## Worked example

The lab creates two tables. `customers` has 100,000 rows in 710 pages, about 5.5 MB. `orders` has 1,000,000 rows in 7,693 pages, about 60 MB, with 130 rows on each page.  The pool has 16,384 buffers, so either table would fit with room for the other. That is the setup for the first surprise.

### The pool, before any query

`pg_shmem_allocations` lists what the postmaster carved out of shared memory at startup. The lab server has 57 named allocations totalling 143 MB.

```text
             name              |    off    |   size    | allocated_size
-------------------------------+-----------+-----------+----------------
 Buffer Blocks                 |   6843392 | 134221824 |      134221824
 <anonymous>                   |           |   4777344 |        4777344
 XLOG Ctl                      |     54016 |   4208200 |        4208256
                               | 147620352 |   1875456 |        1875456
 Buffer Descriptors            |   5794816 |   1048576 |        1048576
 CommitTs                      |   4792064 |    533920 |         534016
 Xact                          |   4262912 |    529152 |         529152
 Checkpointer Data             | 146817408 |    393280 |         393344
 Checkpoint BufferIds          | 141327360 |    327680 |         327680
```

Three lines carry the whole story. `Buffer Blocks` is 134,221,824 bytes: 16,384 buffers of 8,192 bytes, plus 4 KB of alignment. `Buffer Descriptors` is 1,048,576 bytes, which is exactly 16,384 × 64, one 64-byte descriptor per buffer.  `XLOG Ctl` is 4,208,256 bytes, which is the 4 MB of WAL buffers plus its control structure. Figure 3 draws the split.

![Horizontal bar of 143 MB with a 128 MB segment for buffer blocks and a 15 MB tail broken into XLOG Ctl, buffer descriptors, transaction-status caches and about fifty smaller pieces](https://minio.canery.in/media/fig-03-shared-memory-map-postgresql-foundations-memory-layer.png)

*Figure 3 — 128 MB of the 143 MB is page storage. The other 15 MB is 56 allocations, and the largest of them is the WAL buffer ring.*

### A cold scan of the big table

The lab restarts the server, which empties shared buffers, and then evicts both table files from the kernel page cache with `posix_fadvise(DONTNEED)`; `fincore` confirms zero resident pages. That makes the first read a real disk read. Parallel query is off for this one step so a single process does the work.

```text
explain (analyze, buffers, costs off)
select count(*) from orders;

 Aggregate (actual time=198.336..198.338 rows=1 loops=1)
   Buffers: shared read=7693
   ->  Seq Scan on orders (actual time=0.288..128.115 rows=1000000 loops=1)
         Buffers: shared read=7693
 Execution Time: 198.433 ms
```

Every one of the 7,693 pages was a `read`: it was not in shared buffers, so the backend asked the kernel for it. 198 ms for 60 MB from an NVMe drive. After the scan, `fincore` reports all 7,693 pages resident in the kernel cache. And shared buffers?

```text
 relname | buffers_in_shared_buffers
---------+---------------------------
 orders  |                        32
```

Thirty-two. The pool has 16,384 free slots, the table needs 7,693, and the scan kept 32 of them. `pg_stat_io` explains it in one row:

```text
  backend_type  |  object  | context  | reads | hits | evictions | reuses
----------------+----------+----------+-------+------+-----------+--------
 client backend | relation | bulkread |  7693 |    0 |         0 |   7661
```

The read happened in the `bulkread` context, and 7,661 of the 7,693 pages were placed into a buffer the scan had just finished using: 7,693 − 32 = 7,661. The scan ran through a ring of 32 buffers, 256 KB, because the table is larger than a quarter of the pool.   The pool was empty, and PostgreSQL still refused to fill it with this table. Section three explains why that is the right call; the point here is that "it fits" is not the question the buffer manager asks.

Run the same query again and the kernel has the pages, but shared buffers still do not:

```text
   Buffers: shared hit=32 read=7661
 Execution Time: 181.992 ms
```

Thirty-two hits, the ring's leftovers, and 7,661 reads served from the kernel's cache in 182 ms. Now allow the default parallel plan, which uses the leader and two workers:

```text
 Finalize Aggregate (actual time=62.498..63.777 rows=1 loops=1)
   Buffers: shared hit=64 read=7629
   ->  Gather (actual time=62.399..63.771 rows=3 loops=1)
         Workers Planned: 2
         Workers Launched: 2
         ->  Partial Aggregate (actual time=59.039..59.040 rows=1 loops=3)
               ->  Parallel Seq Scan on orders (actual time=0.039..36.529 rows=333333 loops=3)
                     Buffers: shared hit=64 read=7629
 Execution Time: 63.900 ms
```

Three processes, three rings, and the table's footprint in shared buffers is now 160 pages: the 32 + 32 left by the two earlier scans plus 3 × 32 from this one. Figure 4 tracks where the 7,693 pages are after each step.

![Four columns, one per lab step, each with three stacked levels labelled disk, kernel cache and shared buffers, showing 7,693 pages on disk only, then 7,693 in the kernel and 32 in shared buffers, then 7,693 in shared buffers after prewarm, then 320 after the forced sweep](https://minio.canery.in/media/fig-04-three-levels-postgresql-foundations-memory-layer.png)

*Figure 4 — The same 60 MB after four steps. Only a deliberate `pg_prewarm` puts the whole table into the pool, and only a bigger table pushes it out again.*

### The small table stays

`customers` is 710 pages, under the 4,096-page threshold (16,384 ÷ 4), so it is read with the normal strategy. Cold, it reads all 710 pages in 31 ms. Warm, every page is a hit and the scan takes 17 ms.  The threshold is drawn to scale in Figure 5.

![A horizontal scale from 0 to 16,384 pages with four marks: customers at 710, the quarter-pool threshold at 4,096, orders at 7,693 and the pool at 16,384](https://minio.canery.in/media/fig-05-the-threshold-postgresql-foundations-memory-layer.png)

*Figure 5 — The scan strategy is decided by one comparison: table pages against NBuffers ÷ 4. Both tables fit in the pool; only one is allowed to use it.*

A point lookup shows what a hit is at the finest grain. `select * from customers where id = 4242` walks two index pages and one heap page. The first time, the heap page is already in shared buffers from the scan but the index pages are not: `shared hit=1 read=2`. The second time: `shared hit=3`.

### Usage counts, and a forced eviction

After three more scans of `customers`, a thousand point lookups and one more scan of `orders`, `pg_buffercache` shows every `customers` page at usage count 5, the maximum, the index pages at 2–5, and every `orders` ring page at 1.   Pool-wide, 14,956 of the 16,384 buffers are still at usage count 0: the pool is mostly empty and untouched.

To see eviction, the lab calls `pg_prewarm('orders')`, which reads a whole relation into shared buffers with the normal strategy and no ring.  All 7,693 pages become resident. Then it prewarms `orders_archive`, a 15,424-page copy that cannot fit alongside. The pool must evict 10,048 buffers to make room, and afterwards:

```text
    relname     | buffers
----------------+---------
 orders_archive |   14861
 customers      |     710
 orders         |     320
 customers_pkey |     275
```

Every page of `customers`, at usage count 5, survived. Every index page survived. Of the 7,693 pages of `orders`, prewarmed at usage count 1, only 320 remain. That is the clock sweep choosing victims exactly as section two describes, and it is why "the table that was read most recently" is the wrong mental model: the pool kept the pages that were *used most often*.

### One sort, two budgets

`select * from orders order by amount_cents` sorts a million rows. With the default `work_mem = 4MB` the sort does not fit and spills:

```text
 Sort (actual time=489.431..599.267 rows=1000000 loops=1)
   Sort Key: amount_cents
   Sort Method: external merge  Disk: 40464kB
   Buffers: shared hit=323 read=7373, temp read=10115 written=10135
   ->  Seq Scan on orders (actual time=0.036..108.576 rows=1000000 loops=1)
         Buffers: shared hit=320 read=7373
 Execution Time: 662.195 ms
```

With `set work_mem = '256MB'`:

```text
 Sort (actual time=363.688..430.101 rows=1000000 loops=1)
   Sort Key: amount_cents
   Sort Method: quicksort  Memory: 81868kB
   Buffers: shared hit=355 read=7341
   ->  Seq Scan on orders (actual time=0.045..112.425 rows=1000000 loops=1)
         Buffers: shared hit=352 read=7341
 Execution Time: 493.234 ms
```

The sort needed 81,868 kB to stay in memory, twenty times the default budget. In the first run it wrote 10,135 temp blocks, about 79 MB, and read them back. That memory was private to the one backend, and it was gone the moment the query finished; section six shows the backend's resident size go from 12 MB to 97 MB and back to 18 MB.

### A two-byte update that cost 7,544 bytes

The last experiment updates one column of one `customers` row twice, immediately after a `CHECKPOINT`, and asks `pg_walinspect` what was written:

```text
 start_lsn  |    rmgr     | record_type | record_length | fpi_length
------------+-------------+-------------+---------------+------------
 0/4E576D78 | Heap        | HOT_UPDATE  |          7473 |       7408
 0/4E578AC8 | Transaction | COMMIT      |            34 |          0
 0/4E578AF0 | Heap2       | PRUNE       |            59 |          0
 0/4E578B30 | Heap        | HOT_UPDATE  |            70 |          0
 0/4E578B78 | Transaction | COMMIT      |            34 |          0
```

The first update wrote 7,544 bytes of WAL, of which 7,408 are a copy of the entire page minus its 784-byte free-space hole. The second, identical update wrote 176 bytes. Same row, same page, same column; the only difference is that a checkpoint happened before the first one.  Section four explains the rule that produces this, and why the WAL buffer ring is the memory that must reach disk before anything else.

## Intuition

Picture the buffer pool as a hotel with 16,384 identical rooms. A guest is a page of a table or index. Guests do not check out; they are evicted when someone else needs the room. The night clerk walks the corridor in a loop, and every door has a counter on it from 0 to 5. When a guest is visited, the counter on their door goes up by one, to a maximum of 5. When the clerk passes a door with a counter above 0, he lowers it by one and moves on. When he finds a door at 0 with nobody inside, he gives that room to the next arrival.   A page that is used often keeps getting its counter topped up and survives many laps. A page that was read once starts at 1 and is gone the second time the clerk passes. That is why `customers` survived the prewarm of a bigger table and `orders` did not.

The analogy breaks in two places. First, the clerk never moves a guest; a real LRU list would reorder entries on every access, and PostgreSQL deliberately avoids that because every backend would contend for the list. The counters are the whole policy. Second, a room can be *pinned*: a backend that is reading a page holds it, and the clerk skips pinned rooms entirely without touching their counters.   Pins are short, but they are what stop a page from vanishing under a running scan.

The ring is a side door. A large sequential scan is told: you may use these 32 rooms and no others, and when you need a 33rd, reuse the first.  The hotel stays full of long-term guests while a tour group of 7,693 passes through 32 rooms. The analogy breaks if the group makes a mess: a page that the scan *modifies* has to be written to disk before its room can be reused, which needs a WAL flush, so the buffer manager throws that room out of the ring and takes another from the clerk. A scan that dirties every page stops being a ring at all.

The WAL buffer is the receipt book. Before any room is changed, the change is written into the book, and before any changed room is copied out to the archive on disk, the book up to that entry must already be in the archive.   The book is small, 4 MB, because it is copied to the archive at every commit anyway.   Where the analogy breaks: a receipt normally describes the change; PostgreSQL's receipt, the first time a page is touched after a checkpoint, *is the whole page*, because the archive is not assumed to be able to write a page atomically.  That is the 7,408-byte image.

Local memory has no analogy because it is just memory: each backend calls an allocator that hands out chunks from a tree of contexts freed together. What is worth holding on to is the multiplication. A budget like `work_mem` applies to *one operation in one process*. A query with three sorts uses it three times; a parallel query with two workers uses it three times per operation; twenty such connections use it sixty times.

## Shared buffers: what a buffer actually is

A buffer is two things in two places. The page itself, 8,192 bytes, lives in the `Buffer Blocks` array. Its bookkeeping lives in a 64-byte *buffer descriptor* in a parallel array, one per buffer, padded to a cache line so that two processes touching neighbouring descriptors do not fight over the same line.  The lab's 1,048,576-byte `Buffer Descriptors` allocation is that second array. Figure 6 lays both out.

![Byte layout of a 64-byte buffer descriptor: a 20-byte tag of five fields, a buffer id, a 32-bit state word split into 18 bits refcount, 4 bits usage count and 10 flag bits, a waiter field, a free-list link and an embedded content lock; beside it the 8 KB page it describes, and above them a hash table with 128 partitions mapping tags to buffer ids](https://minio.canery.in/media/fig-06-buffer-anatomy-postgresql-foundations-memory-layer.png)

*Figure 6 — What one buffer costs: 8,192 bytes of page and 64 bytes of descriptor. The state word is the interesting part; three different facts share 32 bits so that one atomic instruction can update them together.*

The descriptor starts with a **tag**: tablespace OID, database OID, relation file number, fork number and block number.  That is enough to find the block on disk without consulting any catalog, which matters because the process writing a page out may know nothing about the table it belongs to. To find whether a block is already in the pool, a backend hashes its tag and looks it up in a shared hash table guarded by 128 partition locks; the lookup takes a shared lock on one partition, and only assigning a buffer to a different page takes it exclusively.

Next comes the **state word**, a single 32-bit atomic integer that packs three things: an 18-bit reference count, a 4-bit usage count, and 10 flag bits.  The flags say whether the page is valid, dirty, being read or written right now, needed by the next checkpoint, and whether the descriptor is locked. That last flag *is* the descriptor's spinlock: there is no separate lock field. Setting the bit with an atomic OR and observing that it was previously clear is what "taking the buffer header lock" means.  This design shipped in PostgreSQL 9.6, and the commit that introduced it reported up to an eightfold improvement in a read-only benchmark at high client counts, because pinning a buffer no longer took a lock at all: it became a compare-and-swap loop that bumps the refcount and the usage count in one step.   The same change is why PostgreSQL cannot have more than 262,143 backends: the refcount has 18 bits, and every backend might pin the same buffer.

The **reference count** is the pin. A pinned buffer will not be evicted; an unpinned one may be reused for another page at any instant. Pins are held for the duration of an operation on the page, may be held across a whole scan of that page, and may never be held across a transaction boundary.  A pin does not protect the *contents* of the page. That is the job of the third piece, an LWLock embedded in the descriptor called the content lock, taken shared to read the page and exclusive to change it.  A pin says "keep this page here"; the content lock says "nobody else writes it while I look".

Figure 7 follows one request through those pieces, on the hit path and the miss path.

![Sequence diagram with lanes for a backend, the buffer lookup table, a buffer descriptor, the WAL and the file: on a hit the backend hashes the tag, finds the buffer, pins it and bumps its usage count; on a miss it picks a victim via the clock sweep, flushes WAL and writes the victim if dirty, swaps the tag in the table, reads the page with pread, and marks it valid](https://minio.canery.in/media/fig-07-hit-and-miss-postgresql-foundations-memory-layer.png)

*Figure 7 — A hit costs a hash lookup and one atomic update. A miss costs a victim search, possibly a WAL flush and a page write, and a read. The write-ahead rule is enforced inside the miss path, in `FlushBuffer`.*

On a **hit**, `ReadBuffer` finds the tag, pins the buffer, raises its usage count by one unless it is already 5, and returns.   On a **miss**, the backend needs a victim. It first pops the free list; on a freshly started server every buffer is on that list, which is why the lab's cold scans evicted nothing.  Once the list is empty it runs the clock sweep of the next section. If the victim is dirty, *the backend that needs the buffer writes it out itself*, and before it does, `FlushBuffer` forces WAL out to the victim page's LSN.   Then the backend takes the partition lock exclusively, swaps the new tag in, sets the usage count to 1, and reads the page. In 16.x the read is a direct `pread()` on the segment file; the flag `BM_VALID` is set only when the bytes have arrived.   PostgreSQL 18 routes that read through a new asynchronous I/O subsystem instead, which is why its descriptor gained one extra field, but the protocol around it is the same.

One consequence of the miss path explains a whole class of latency spikes: on a busy server with a full pool, an ordinary `SELECT` can end up writing somebody else's dirty page to disk, and flushing WAL to do it, before it can read its own.   The background writer exists to make that rare. It walks ahead of the clock hand writing dirty, unpinned, usage-count-0 buffers so that victims are already clean when a backend reaches them.

## The clock sweep: how a page gets evicted

The replacement policy is small enough to state in full. The clock hand, `nextVictimBuffer`, is an integer that walks the descriptor array in a loop. To get a victim, advance the hand one step and look at that buffer:

- if it is pinned, skip it;
- if its usage count is above 0, subtract one and skip it;
- otherwise it is the victim.

That is all. The hand is an atomic counter advanced without any lock; the only synchronised moment is when it wraps around, so that the number of complete passes can be counted.  Because the usage count saturates at 5, the source notes that finding a victim can take up to six full passes over the pool in the worst case, though in practice the hand stops at the first zero it finds.  If it examines every buffer and all of them are pinned, it gives up with "no unpinned buffers available".

Figure 8 traces the rule on a pool of eight buffers, which is small enough to follow with a finger.

![Three panels of the same eight-slot pool with a clock hand; slots carry usage counts 3, 0 (pinned), 1, 5, 0, 2, 1, 0; the hand starts at slot one, decrements the 3 to 2, skips the pinned slot, decrements the 1 to 0, decrements 5 to 4, and stops at the fifth slot whose count is 0, which becomes the victim](https://minio.canery.in/media/fig-08-clock-sweep-trace-postgresql-foundations-memory-layer.png)

*Figure 8 — Eight buffers, one pass. The hand lowers every count it passes and stops at the first unpinned zero. Buffer 2 is pinned and is not even decremented; buffer 4 at count 5 will survive four more passes.*

Read the lab's forced eviction against that rule. Before `pg_prewarm('orders_archive')`, `orders` had 7,693 pages at usage count 1, `customers` had 710 at usage count 5, and the free list was nearly exhausted.  The prewarm needed 10,048 victims. On the hand's first pass, every `orders` page dropped from 1 to 0; on the second pass they were taken. Every `customers` page dropped from 5 to 4, then to 3, and was still standing when the prewarm ran out of pages to load. Afterwards the usage-count histogram had 134 buffers at 5 instead of 883, and `orders` kept 320 of its 7,693 pages.  Figure 9 shows the two histograms side by side.

![Grouped bar chart of buffer counts at usage counts 0 through 5, before and after the forced sweep: before, 14,956 at zero and 883 at five; after, 5,148 at zero, 10,146 at one and 134 at five](https://minio.canery.in/media/fig-09-usage-histogram-postgresql-foundations-memory-layer.png)

*Figure 9 — The sweep's fingerprint. The prewarmed pages arrive at count 1, the survivors from before were lowered from 5 towards 3, and the pool has almost no zeros left.*

### Why not LRU?

A least-recently-used list is the textbook answer, and PostgreSQL used one until 8.0. It has two problems in a database. The first is that a single large scan pushes out every page that was useful before it; LRU has no notion of frequency, only of recency.  The second is that every access has to move an entry to the head of a shared list, and on a multi-processor server that list becomes the thing every backend waits on.

The history of the fix is short and worth knowing, because it explains the shape of what runs today, and Figure 10 puts it on a line.

![Timeline from 2005 to 2026: PostgreSQL 8.0 in January 2005 adopts ARC, 8.0.2 in April 2005 replaces it with 2Q over a patent, 8.1 in November 2005 adopts the clock sweep, 9.6 in 2016 makes the buffer header lock-free, 16 through 18 tune the rings, and 19 removes the free list](https://minio.canery.in/media/fig-10-replacement-timeline-postgresql-foundations-memory-layer.png)

*Figure 10 — Twenty years of one data structure. The policy has been the clock sweep since 8.1; everything after that is about locks and rings.*

PostgreSQL 8.0, released in January 2005, replaced LRU with ARC, the Adaptive Replacement Cache of Megiddo and Modha: four lists that track recently and frequently used pages and shift the balance between them as the workload changes.   ARC is scan-resistant and, on the authors' SPC1-like trace with a 4 GB cache, reached a 20% hit ratio against LRU's 9.19%.  Then IBM's patent application on ARC surfaced. In February 2005 Tom Lane argued that the patent turned on the word "adaptively", and that the 2Q algorithm of Johnson and Shasha — two queues with *fixed* sizes, a FIFO for first-touched pages and an LRU for pages touched again — gave the same scan resistance without it, and could be implemented mostly by deleting code.   Release 8.0.2 in April 2005 shipped 2Q, with a note that it might be a few percent slower than ARC and that a better algorithm was coming in 8.1.

The better algorithm was older than either. Corbató's 1968 paging experiment on Multics describes a pointer cycling a circular list of pages, a usage bit on each page that the hardware sets on reference and the sweep clears, and replacement of the first page whose bit is clear.  PostgreSQL 8.1 adopted it in November 2005, with a 4-bit counter in place of the single bit, as part of an overhaul aimed at multi-CPU scalability; the release notes name the shared buffer cache as "a significant scalability problem".  The appeal is that the sweep never reorders anything. An access touches one counter in one descriptor. The only shared state is the hand.

> [!NOTE]
> The free list still exists through PostgreSQL 18 as a fast path for a pool that has never filled. It is removed on the development branch that will become 19, where the sweep is the only path.  On any server that has been up for a while the difference is invisible: the list is empty within minutes.

## Rings: why a big scan leaves 256 KB behind

The clock sweep protects hot pages from *other* hot pages. It cannot protect them from a sequential scan of a table larger than the pool, because such a scan touches every page once, each arriving with usage count 1, and by the time the hand comes round again the whole pool has been replaced. The 8.0 release notes describe exactly this failure of LRU; the clock sweep on its own only slows it down.  The fix, added in 8.3, is to stop such scans from using the pool at all.

A **buffer access strategy**, or ring, is a small private list of buffers that a scan reuses in a circle. When the scan needs a buffer it takes the next one in the ring, provided that buffer is unpinned and has a usage count of at most 1; otherwise something else has found that page useful, so the ring gives it up and takes a fresh victim from the normal sweep.  For a sequential scan the ring is 256 KB, 32 buffers, and the README's reasoning is that 256 KB fits in an L2 cache, so copying pages from the kernel into it stays cheap, while still leaving a small trail behind for a second scan of the same table to synchronise with.   Figure 11 draws the ring, and what happens to a slot the scan dirties.

![A ring of 32 buffer slots with pages of a 7,693-page table cycling through it, one slot marked dirty and ejected to the normal pool, and three such rings drawn for a leader and two parallel workers](https://minio.canery.in/media/fig-11-the-rin-postgresql-foundations-memory-layer.png)

*Figure 11 — The ring is per process. A parallel scan with two workers leaves three rings' worth of pages behind, which is the 96 the lab measured.*

Whether a scan uses a ring is decided by one comparison in `initscan`: a heap scan gets the bulk-read strategy, and synchronised scanning, only when the table has more pages than a quarter of the pool.  On the lab server that is 4,096 pages. `orders` at 7,693 uses the ring; `customers` at 710 does not, and that single comparison is why one table stayed cached and the other did not, in Figure 5.

Three rings exist, drawn in Figure 12 with their sizes.

![Table graphic with three rows for bulk read, bulk write and vacuum rings: 256 KB / 32 buffers used by large sequential scans; 16 MB / 2,048 buffers used by COPY, CREATE TABLE AS, REFRESH MATERIALIZED VIEW and table rewrites; 256 KB in 16 and 2 MB from 17 used by VACUUM and ANALYZE; footnotes for the quarter-pool threshold, the one-eighth cap, and the 18 change that grows the read ring](https://minio.canery.in/media/fig-12-ring-sizes-postgresql-foundations-memory-layer.png)

*Figure 12 — Ring sizes on PostgreSQL 16.2, with the 17 and 18 changes noted. Every ring is capped at one eighth of the pool.*

The **bulk-read** ring is what the scans above used. If the scan dirties one of its buffers, writing that buffer back would require a WAL flush, so instead the buffer is thrown out of the ring and a replacement is taken from the sweep; a scan that modifies every page, a bulk `UPDATE` or `DELETE`, therefore degrades to the normal strategy and does fill the pool.

The **bulk-write** ring is 16 MB, 2,048 buffers, and is used by `COPY`, `CREATE TABLE AS`, `REFRESH MATERIALIZED VIEW` and table rewrites. Dirty pages are not ejected from it; WAL is flushed as needed so the buffer can be reused. The README explains the size: smaller rings made `COPY` block too often on those flushes, and a foreground load is allowed to take more of the pool than a background vacuum.   The lab saw the ring directly: after `CREATE TABLE orders_archive AS ...` wrote 15,424 pages, 2,080 of them were still in shared buffers, the ring's footprint plus a few pages of catalog work.

The **vacuum** ring is sized by `vacuum_buffer_usage_limit`: 256 KB in 16, raised to 2 MB in 17, and settable per `VACUUM` call since 16 with the `BUFFER_USAGE_LIMIT` option.   Before rings existed, VACUUM's buffers went straight to the free list, which the README describes as a ring of one buffer that flushed WAL constantly.

Two version notes. Every ring, whatever its nominal size, is capped at one eighth of the pool, so on a 128 kB `shared_buffers` a "16 MB" ring is two buffers.  And in PostgreSQL 18 the bulk-read ring is no longer fixed: it grows by `io_combine_limit × effective_io_concurrency` blocks so that the new asynchronous reads can have enough I/O in flight, which with the defaults makes it 2,304 KB before the cap.  The number 32 in the worked example is a 16.x number.

`pg_stat_io` is the instrument for all of this. It reports one row per backend type, object and *context*, where context is `normal`, `bulkread`, `bulkwrite` or `vacuum`, and its `reuses` column counts ring slots reused while `evictions` counts pages pushed out of the shared pool.  The lab's 7,661 reuses for a 7,693-page scan is the cleanest statement of what a ring is.

## WAL buffers: the memory that must reach disk first

The buffer pool would be enough for a database that never crashed. The write-ahead log exists because it does. The rule, in the project's own words, is that changes to data files may be written only after the log records describing them have been flushed to permanent storage; recovery then rolls forward from the last checkpoint, redoing whatever the log says and the files do not yet show.  The pay-off is that a commit needs only the *log* on disk, and the log is written sequentially, which is far cheaper than forcing out every page the transaction touched.

The rule needs memory of its own, and it needs to be shared, because every backend appends to one log. That is the WAL buffer ring, 4 MB on the lab server: `wal_buffers = -1` means one thirty-second of `shared_buffers`, floored at 64 kB and capped at one WAL segment, normally 16 MB.  It is small on purpose. The buffers are written to the current segment file at every transaction commit, so a much larger ring rarely helps; the documentation's own advice is that a few megabytes matter on a busy server where many clients commit at once, and that a bigger ring smooths response times right after a checkpoint.

### How a record gets in

Figure 13 follows one update from the heap page to the segment file.

![Sequence diagram with lanes for a backend, the WAL insert position, the WAL buffers, the WAL writer and the segment file: the backend reserves bytes under a spinlock, copies the record into the buffers under one of eight insertion locks, sets the page LSN, and at commit calls XLogFlush which writes and fsyncs the buffers to the segment; a side branch shows a full buffer forcing the inserter to write it out itself and count wal_buffers_full](https://minio.canery.in/media/fig-13-wal-insert-path-postgresql-foundations-memory-layer.png)

*Figure 13 — Insertion is two steps: a tiny serialised reservation, then a parallel copy. The flush happens at commit, and it is the commit that waits.*

Inside `XLogInsertRecord`, insertion is a two-step process. First the backend reserves space by advancing a byte position under a spinlock; the operation is kept to a bare increment because it is the one moment that serialises every backend on the server. Then it copies the record into the reserved bytes of the ring while holding one of eight *insertion locks*, so up to eight backends copy at once.  The function returns the position just past the record, and that number is written into the page header as `pd_lsn`.  The source describes the returned LSN as the point up to which the log must be flushed before the page can be written, and calls it the basic rule: write the log before the data.

The canonical sequence for any logged change is fixed and short: pin and exclusive-lock the buffer, enter a critical section, modify the page, mark the buffer dirty, insert the WAL record, stamp the page with the returned LSN, leave the critical section, unlock.  The critical section is why a failure in the middle is a PANIC rather than an ERROR: a page that has been modified in shared memory without its log record is a page that recovery could never reproduce.

At commit, `RecordTransactionCommit` calls `XLogFlush` up to the commit record, and the client is told "COMMIT" only when that returns.  `XLogFlush` writes and fsyncs not just the bytes it was asked for but any further WAL already sitting in the ring, to piggyback as much as it can on one expensive fsync.  With `synchronous_commit = off` the backend skips the wait and leaves the flush to the WAL writer process, which runs every `wal_writer_delay`, 200 ms by default; the transaction is then safe within at most three of those intervals.

When the ring is full, the inserter must free space itself: it writes an older, unwritten buffer to the file before it can copy its record in, and counts the event in `pg_stat_wal.wal_buffers_full`.  The lab's load of 1.1 million rows produced 1,208,928 WAL records and 101 MB of WAL, and the 4 MB ring overflowed 8,919 times.  That counter is the signal the documentation says to watch when deciding whether `wal_buffers` is too small.

### The full page image

Now the 7,544-byte update. With `full_page_writes` on, the default, the first time a page is modified after a checkpoint the WAL record carries a copy of the whole page.  Recovery does not redo the change on whatever is in the file; it lays the copy down whole. The reason is that PostgreSQL does not assume a disk writes 8 KB atomically: a crash halfway through a page write leaves a torn page, half old and half new, which no incremental redo could repair.  Figure 14 draws the two updates to scale.

![Two bars to scale: the first update's WAL is a 7,473-byte HOT_UPDATE record almost entirely filled by a 7,408-byte page image, with the 784-byte free-space hole shown as omitted, plus a 34-byte commit; the second update's WAL is three small records of 59, 70 and 34 bytes](https://minio.canery.in/media/fig-14-full-page-image-postgresql-foundations-memory-layer.png)

*Figure 14 — The same change, logged twice. The first record after a checkpoint is the page; the second is the change. The hole between the line pointers and the tuples is not copied.*

`pg_walinspect` shows the image is 7,408 bytes, not 8,192: the 784 bytes of free space between the page's line-pointer array and its tuples are omitted, because recovery can reconstruct a hole of zeros.  The second update logs three records totalling 163 bytes plus alignment: a prune of the dead tuple version, the update itself, and the commit. Between them lies only one fact — no checkpoint intervened.

This is also the connection to `shared_buffers` sizing that opened the post. A checkpoint writes every dirty page in the pool and then starts the clock again, so that every page's next modification is a full image.   Checkpoints run every `checkpoint_timeout`, five minutes, or when `max_wal_size`, 1 GB, is about to be exceeded, and since PostgreSQL 14 their writes are spread over 90% of the interval.   A bigger pool holds more dirty pages, which makes each checkpoint write more, which is why the documentation pairs a bigger `shared_buffers` with a bigger `max_wal_size`.  Since 9.6 the checkpointer sorts its dirty pages by file and block before writing them, so that the burst is sequential rather than random.

### When a dirty page may leave memory

Figure 15 puts the three numbers that govern a dirty page on one line: the page's own LSN, how far the WAL has been flushed, and the checkpoint.

![Timeline of WAL positions: a page is dirtied and stamped with LSN A; the WAL flush position advances past A at commit; only then may FlushBuffer write the page; at the next checkpoint the page is written and marked clean; a bar underneath shows the page's buffer state going valid, dirty, dirty and flushable, clean](https://minio.canery.in/media/fig-15-when-a-page-may-leave-postgresql-foundations-memory-layer.png)

*Figure 15 — A dirty buffer is writable only once the flush position has passed its LSN. Whoever writes it — checkpointer, background writer, or a backend that needs the buffer — calls the same function and obeys the same rule.*

Every buffer write, whoever performs it, goes through `FlushBuffer`, and `FlushBuffer` begins by calling `XLogFlush` up to the page's LSN.   That single call is the write-ahead rule in code. It is the reason a backend evicting a dirty victim may end up waiting on an fsync of the log, and it is the reason a bulk-read ring ejects dirty pages instead of writing them: the ring would otherwise stall on that flush every 32 pages.

After the lab's two updates, the page's `pd_lsn` was `0/4E578B78`, the end of the last record that touched it; the buffer showed `isdirty = t` in `pg_buffercache`; and a `CHECKPOINT` left it resident and clean.  Nothing about it was evicted. Clean and cached is the normal state of a hot page.

The design is ARIES, published by Mohan and colleagues in 1992: log records on stable storage before the data they describe, an LSN on every page, and a buffer manager that forces the log up to a dirty page's LSN before writing it.  What PostgreSQL leaves out is as telling as what it takes. ARIES undoes loser transactions after a crash with compensation records; PostgreSQL has no undo pass at all, because a transaction without a flushed commit record is simply presumed aborted, its tuples are invisible under MVCC, and VACUUM removes them later.   That is why there is no abort log to flush, and why the memory layer never has to keep "before images" of anything.

## Local memory: work_mem and its family

Everything so far was shared. The third pool is not. Each backend allocates its own working memory from the operating system as it needs it, and the settings that govern it are limits per *operation*, not per connection.

`work_mem` is the one that matters most. It defaults to 4 MB and caps a single sort or hash table before it starts spilling to temporary files.  The documentation is explicit about the multiplication: a complex query may run several sorts and hashes at the same time, each allowed its own `work_mem`, and several sessions may do so concurrently, so the total can be many times the setting.  Parallel query adds a factor: resource limits are applied to each worker individually.  Figure 16 shows the lab's grouping query with `work_mem` lowered to 1 MB, where the leader and two workers each got their own 2,065 kB hash table and each spilled it into nine batches, and then each ran its own external sort as well.

![Plan tree for a parallel aggregate: a Gather Merge over three identical branches, leader and two workers, each annotated with its own hash aggregate at 2,065 kB in nine batches and its own external sort of about 2.5 MB on disk](https://minio.canery.in/media/fig-16-per-process-budgets-postgresql-foundations-memory-layer.png)

*Figure 16 — Six operations, six budgets, one query. `work_mem` was 1 MB; the hash budget is twice that; every process got its own copy of both.*

The hash budget is not `work_mem` itself but `work_mem × hash_mem_multiplier`, 2.0 by default, so 8 MB.  The multiplier arrived in PostgreSQL 13 with a default of 1.0, alongside the change that let hash aggregates spill at all — before 13 a hash aggregate that outgrew its estimate simply kept growing — and the default was raised to 2.0 in 15.   In the lab, grouping a million rows into 100,000 groups spilled at the defaults: five batches, 8,241 kB in memory, 7,248 kB on disk. Raising the multiplier to 4.0, without touching `work_mem`, gave the hash 16 MB and it finished in one batch at 12,561 kB.  That is what the multiplier is for: hash tables are usually the operation that benefits from memory, and this raises their budget without raising every sort's.

Figure 17 puts the two sort runs from the worked example next to each other.

![Two pairs of bars: with work_mem 4 MB the sort used 40,464 kB of temp files and took 662 ms; with 256 MB it used 81,868 kB of memory and took 493 ms](https://minio.canery.in/media/fig-17-sort-two-budgets-postgresql-foundations-memory-layer.png)

*Figure 17 — The in-memory sort needed twenty times the default budget. It was 26% faster, not ten times faster; the spill path is a merge, not a disaster.*

A sort's actual budget is `Max(work_mem, 64) × 1024` bytes, and `EXPLAIN ANALYZE` reports the outcome as `Sort Method: quicksort Memory: NkB` or `external merge Disk: NkB`.  The lab's million-row sort needed 81,868 kB, and the next section shows where every byte of that went.

The rest of the family:

- **`maintenance_work_mem`**, 64 MB, bounds `VACUUM`, `CREATE INDEX` and `ALTER TABLE ADD FOREIGN KEY`. It can be larger than `work_mem` because a session runs one such operation at a time — but autovacuum can run `autovacuum_max_workers` of them at once, each with its own copy, and `autovacuum_work_mem` exists to cap that separately.  Through PostgreSQL 16, VACUUM could use at most 1 GB of this budget for dead-tuple identifiers whatever the setting said, because it kept them in one array and a single allocation is limited to 1 GB minus one byte; 17 replaced the array with a radix tree and the limit disappeared.
- **`temp_buffers`**, 8 MB, is a third buffer pool, private to the session and used only for temporary tables.  `EXPLAIN` reports it as `local` rather than `shared`. In the lab a temporary copy of `orders` was read as `local read=7744` and a rescan still read from disk, because the table is 60 MB and the pool is 8 MB.  The setting can be changed only before the session first touches a temporary table.
- **`logical_decoding_work_mem`**, 64 MB, caps what a replication connection buffers before spilling, and belongs to part 3.

> [!WARNING]
> **Common mistake:** setting `work_mem` globally to make one report fast. The report has three sorts and runs with two workers, so it uses nine budgets; twenty connections run it at once. The symptom is not a slow query. It is the kernel's out-of-memory killer taking down a backend, which takes down the postmaster's whole set of children with it. Set it per session, per role, or per query with `SET LOCAL`.

## Memory contexts: how a backend allocates

A backend never calls `malloc` directly for its working data. It calls `palloc`, and `palloc` allocates from the *current memory context*, a global that `MemoryContextSwitchTo` changes and restores.  Contexts form a tree, and the point of the tree is one operation: deleting or resetting a context frees everything in it and everything below it, at once, without walking the individual chunks.  That is how PostgreSQL reclaims all of a query's memory at query end, all of a transaction's at transaction end, and all of a per-tuple scratch area between rows, with no leak tracking and no reference counting.

Figure 18 is the tree of the lab's backend while it held the 256 MB sort open in a cursor, taken with `pg_log_backend_memory_contexts`.

![Tree of memory contexts rooted at TopMemoryContext with children CacheMemoryContext, MessageContext, TopTransactionContext and PortalContext; under the portal, ExecutorState, then TupleSort main at 25,174,064 bytes with a child Caller tuples at 58,720,256 bytes; leaf sizes from the lab annotated, grand total 85,132,832 bytes](https://minio.canery.in/media/fig-18-context-tree-postgresql-foundations-memory-layer.png)

*Figure 18 — The tree of one backend mid-sort. Deleting `ExecutorState` when the cursor closes frees 84 MB in one call.*

The roots are the same in every backend.  `TopMemoryContext` is never reset; allocating there is effectively `malloc`. `CacheMemoryContext` holds the relation and catalog caches for the life of the session, which is why a backend that has touched many tables is bigger than one that has not. `MessageContext` holds the current command and is reset at the top of every command cycle. `TopTransactionContext` is reset at the end of each top-level transaction. Below those, each query gets an executor context, and each node in the plan that needs scratch space gets a child of that.

The lab's numbers tie the tree to the earlier sort. An idle backend held 118 contexts totalling 1,298 kB.  With the sort held open, `TupleSort main` was 25,174,064 bytes and its child `Caller tuples` was 58,720,256 bytes in 17 blocks holding 1,000,000 chunks, for a grand total of 85,132,832 bytes.  Both numbers decompose exactly. A `SortTuple` — a pointer to the tuple, the first sort key, a null flag and a tape number — is 24 bytes, and the array of them grows by doubling, so a million rows need 2²⁰ = 1,048,576 slots × 24 bytes = 25,165,824 bytes, which is the `TupleSort main` figure less one 8 KB block of overhead.  The tuples themselves, one chunk each, average 58.7 bytes and live in a Generation context, an allocator for chunks that are freed in roughly the order they were allocated; 17 moved them to a still leaner "bump" context with no per-chunk header at all.  Figure 19 puts the two halves next to the process's resident size.

![Stacked bar of the sort's 85 MB split into the 25 MB SortTuple array and the 58.7 MB of tuples in 17 blocks, beside three bars for the backend's resident size: 12 MB idle, 97 MB with the cursor open, 18 MB after CLOSE](https://minio.canery.in/media/fig-19-where-85-mb-went-postgresql-foundations-memory-layer.png)

*Figure 19 — Where 85 MB went, and that it came back. The 6 MB the backend kept after CLOSE is cache, not leak.*

The process's resident set told the same story from outside: 12 MB idle, 97 MB with the cursor open, 18 MB after `CLOSE` and `COMMIT`.  The memory went back to the operating system because the executor context was deleted, not because a million tuples were freed one by one.

Under the tree sits the allocator. The default kind, an *AllocSet*, requests blocks from `malloc` starting at 8 KB and doubling up to 8 MB, carves chunks out of them, and keeps eleven free lists for power-of-two chunk sizes from 8 bytes up; any request over 8 KB gets a block of its own.  Each chunk carries an 8-byte header, cut from 16 bytes in PostgreSQL 16, whose low bits identify which kind of context owns it, so `pfree` can find the owner without being told.  A normal `palloc` is limited to one byte under 1 GB; only a separate "huge" allocation path goes beyond, and that limit is the same one that capped the old vacuum array.

Two tools expose all of this from SQL. `pg_backend_memory_contexts` shows the calling session's own tree, and `pg_log_backend_memory_contexts(pid)` writes any other process's tree to the server log; both arrived in PostgreSQL 14.   The view's shape changed in 18: it gained `type` and `path` columns, lost `parent`, and its `level` became 1-based instead of 0-based, so a query written against 16 will need adjusting.

## The rest of shared memory

Of the lab's 143 MB, 128 MB is page storage. The other 15 MB is 56 allocations, and Figure 20 maps the ones that matter.

![Treemap of the 15 MB of non-buffer shared memory: XLOG Ctl 4.0 MB, anonymous allocations 4.6 MB, free 1.8 MB, buffer descriptors 1 MB, the CommitTs, Xact, Subtrans, MultiXact, Notify and Serial caches, checkpointer data and buffer ids, shared statistics, backend status arrays, and the lock and proc tables](https://minio.canery.in/media/fig-20-rest-of-shared-memory-postgresql-foundations-memory-layer.png)

*Figure 20 — Everything in shared memory that is not a page. The WAL ring is the largest piece; the rest is bookkeeping whose size follows `max_connections` and `shared_buffers`.*

- **`XLOG Ctl`**, 4.0 MB, is the 4 MB WAL buffer ring plus its control structure.
- **`Buffer Descriptors`** and **`Buffer IO Condition Variables`** are the per-buffer bookkeeping: 64 bytes and 16 bytes per buffer (1,048,576 and 262,144 bytes over 16,384 buffers). The condition variables replaced a per-buffer lock in 14; a backend waiting for someone else's read of the same page sleeps on one.
- **`Xact`, `CommitTs`, `Subtrans`, `MultiXactOffset`, `MultiXactMember`, `Notify`, `Serial`** are *SLRU* caches, simple LRU pools that front the small on-disk status files: which transactions committed, their parent transactions, their commit times, row-lock groups, `NOTIFY` queues, serializable-isolation state.  In 16.2 their sizes are compile-time: the commit-status cache gets `shared_buffers / 512` pages, between 4 and 128, which is 32 pages here.  PostgreSQL 17 made them configurable and split each into 16-page banks with their own locks.
- **The lock table** is sized for `max_locks_per_transaction` (64) × (`MaxBackends` + `max_prepared_transactions`) entries, and `MaxBackends` is more than `max_connections`: it adds autovacuum workers, background workers and WAL senders.  This is the allocation that runs out when one transaction touches thousands of partitions.
- **The process array** holds one `PGPROC` per backend slot, with the hot fields mirrored into dense arrays so that taking a snapshot can scan them in a tight loop.
- **`Checkpointer Data`** and **`Checkpoint BufferIds`** are the checkpointer's request queue and the array it sorts dirty buffers into.

Two questions remain about the region itself: how it is created, and whether it uses huge pages.

On Linux the region is an anonymous `mmap`, plus a System V segment of a few dozen bytes whose only job is to be attached by every process, because a System V segment can report how many processes are attached and an anonymous mapping cannot; that count is the interlock that stops a second postmaster from starting on the same data directory.  Structures register themselves by name in a shared hash table, and nothing is ever freed.  Parallel query needs memory that did not exist at startup, so it uses *dynamic* shared memory: segments created at run time with `shm_open`, torn down when the query ends, with an allocator on top that hands out size-class chunks by relative pointer, since each process maps a segment at its own address.

Huge pages are the other question, and Figure 21 shows the arithmetic.

![Two bars of equal length representing 143 MB of shared memory: the upper divided into 36,608 pages of 4 kB drawn as a dense grid, the lower into 72 pages of 2 MB, with a note that each page needs one TLB entry](https://minio.canery.in/media/fig-21-huge-pages-postgresql-foundations-memory-layer.png)

*Figure 21 — The same 143 MB as 36,608 small pages or 72 huge ones. Every backend maps the whole region, so every backend pays the page-table cost.*

`huge_pages = try` is the default: the server rounds the region up to a multiple of the huge page size, asks for it with `MAP_HUGETLB`, and falls back to ordinary pages if the kernel refuses.  The lab server reports `shared_memory_size = 143MB` and `shared_memory_size_in_huge_pages = 72`, but the machine has no huge pages reserved, so `try` silently fell back.  The documented procedure is to run `postgres -C shared_memory_size_in_huge_pages` against the stopped server and set `vm.nr_hugepages` to at least that number; both read-only parameters arrived in 15, and 17 added `huge_pages_status` so a running server can say which way `try` went.

## The math

There are five pieces of arithmetic in this post. None needs more than a calculator, and each answers a question the lab raised.

| Symbol                                                         | Meaning                                    | Units |
| -------------------------------------------------------------- | ------------------------------------------ | ----- |
| $N$                                                          | `shared_buffers` in pages (`NBuffers`) | pages |
| $B$                                                          | page size (`BLCKSZ`)                     | bytes |
| $P$                                                          | pages in a relation                        | pages |
| $h$  | hits,$r$ reads, as `pg_stat_database` counts them | blocks                                     |       |
| $w$                                                          | `work_mem`                               | bytes |
| $n$                                                          | rows in a sort                             | rows  |

**1. The threshold and the rings.** A sequential scan uses a ring when $P > N/4$; the bulk-read ring holds $256\,\text{kB}/B$ buffers, the bulk-write ring $16\,\text{MB}/B$, and every ring is capped at $N/8$.   With $N = 16{,}384$ and $B = 8{,}192$:

$$
N/4 = 4{,}096 \text{ pages}, \qquad 256\,\text{kB}/B = 32, \qquad 16\,\text{MB}/B = 2{,}048, \qquad N/8 = 2{,}048.
$$

A 7,693-page table is over the threshold and leaves 32 pages behind per process; a 710-page table is under it and is cached whole. The bulk-write ring and the cap coincide at 128 MB of `shared_buffers`: any smaller pool shrinks the `COPY` ring below 16 MB.

**2. Fixed overheads.** Descriptors cost $64N$ bytes, WAL buffers $\max(64\,\text{kB}, \min(NB/32, 16\,\text{MB}))$, and the region is rounded up to whole huge pages when they are used.   For the lab:

$$
64 \times 16{,}384 = 1{,}048{,}576 \text{ bytes}, \qquad \frac{16{,}384 \times 8{,}192}{32} = 4\,\text{MB}, \qquad \left\lceil \frac{143\,\text{MB}}{2\,\text{MB}} \right\rceil = 72.
$$

Descriptor overhead is 0.8% of the pool at any size, which is why nobody tunes it. Scale `shared_buffers` to 8 GB and the WAL ring hits its 16 MB cap at 512 MB of buffers and stays there.

**3. What the hit ratio measures.** `pg_stat_database` gives

$$
\text{hit ratio} = \frac{h}{h + r},
$$

and the lab's whole run scored $2{,}102{,}354 / (2{,}102{,}354 + 146{,}867) = 93.5\%$.  The number is honest about one thing only: how often a page was already in *shared buffers*. A read counted in $r$ may have come from the kernel page cache in microseconds or from the disk in milliseconds, and the view cannot tell them apart.  In the lab, the 7,661 "reads" of the warm rescan came from the kernel; the 7,693 of the cold scan came from the disk; the ratio treats them identically. Two servers with the same 93.5% can differ a hundredfold in I/O time, which is what `track_io_timing` is for.

**4. The cost of a victim search.** Each step of the clock sweep either decrements a usage count or ends the search, and no count exceeds $5$. Starting from a pool in which every buffer is at the maximum, the hand can decrement at most $5N$ times before it must find a zero, so a single search touches at most

$$
(\text{BM\_MAX\_USAGE\_COUNT} + 1)\,N = 6N
$$

descriptors, which is the bound the source comment states.  Amortised over the searches that follow it is far less, because every decrement is work the next search does not repeat: after one full pass the pool is full of zeros. The lab's 10,048 evictions of usage-1 pages took two passes over 16,384 descriptors, about $3.3$ descriptor visits per victim.

**5. Working memory.** A sort keeps an array of $24$-byte entries that doubles as it grows, plus the tuples themselves, so an in-memory sort of $n$ rows of average tuple size $t$ needs about

$$
24 \cdot 2^{\lceil \log_2 n \rceil} + n\,t \text{ bytes},
$$

which for the lab's $n = 10^6$, $t \approx 58.7$ gives $25.2\,\text{MB} + 58.7\,\text{MB} = 83.9\,\text{MB}$, against the $85.1\,\text{MB}$ the backend actually reported once block headers are counted.   And the number an operator should compute before raising any budget is the worst case,

$$
M_{\max} = w \times (\text{operations per query}) \times (\text{leader} + \text{workers}) \times (\text{concurrent sessions}),
$$

with hash operations counted at $w \times \texttt{hash\_mem\_multiplier}$.    A query with three sorts and three hashes, two workers, and twenty sessions at $w = 256\,\text{MB}$ can ask for $256 \times (3 + 6) \times 3 \times 20 = 138\,\text{GB}$. It usually will not; the point is that nothing in PostgreSQL stops it.

## Implementation

The memory layer is fully observable from SQL. Figure 22 maps each pool to the view that sees it, and the queries below are the ones the lab ran; the complete runner and captured output are available under [Lab downloads](#lab-downloads).

![Grid mapping the three pools and the kernel cache to the tools that observe them: pg_shmem_allocations and pg_buffercache for shared buffers, pg_stat_wal and pg_walinspect for WAL buffers, pg_backend_memory_contexts and EXPLAIN for local memory, pg_stat_io across all three, and fincore for the kernel cache which no PostgreSQL view sees](https://minio.canery.in/media/fig-22-tooling-map-postgresql-foundations-memory-layer.png)

*Figure 22 — One view per pool, and one pool no view can see. `pg_stat_io` is the only tool that shows the rings.*

**The shared region.** How big it is and what is in it:

```sql
select name, pg_size_pretty(allocated_size) as size
from pg_shmem_allocations
order by allocated_size desc
limit 10;
```

**What is in the pool, by relation.** Needs the `pg_buffercache` extension. Filter on the main fork, or the free-space-map and visibility-map forks inflate the count:

```sql
select c.relname,
       count(*)                              as buffers,
       count(*) filter (where b.isdirty)     as dirty,
       round(avg(b.usagecount), 2)           as avg_usage
from pg_buffercache b
join pg_class c on b.relfilenode = pg_relation_filenode(c.oid)
where b.reldatabase = (select oid from pg_database where datname = current_database())
  and b.relforknumber = 0
group by c.relname
order by buffers desc
limit 15;

select * from pg_buffercache_usage_counts();   -- 16+: the histogram in one row per count
```

**Who is reading through a ring, and who is writing dirty pages.**

```sql
select backend_type, context, reads, hits, evictions, reuses, writes, fsyncs
from pg_stat_io
where object = 'relation' and (reads > 0 or writes > 0)
order by backend_type, context;
```

Large `writes` or `fsyncs` on `client backend` in the `normal` context are backends evicting dirty pages themselves; `reuses` in `bulkread` is a scan being kept out of the pool by design. On 18 the byte columns replace `op_bytes` and WAL gets its own rows.

**One query's footprint.** `BUFFERS` is off by default through 17 and on by default with `ANALYZE` from 18.

```sql
explain (analyze, buffers) select ... ;
-- shared hit/read: the pool;  local: temp_buffers;  temp read/written: work_mem spills
```

**The WAL ring.** `wal_buffers_full` is the count that says the ring was too small:

```sql
select wal_records, wal_fpi, pg_size_pretty(wal_bytes) as wal, wal_buffers_full
from pg_stat_wal;
```

**A backend's own memory.**

```sql
select name, parent, level, pg_size_pretty(total_bytes) as total
from pg_backend_memory_contexts
order by total_bytes desc limit 10;            -- this session (18: no parent column, use path)

select pg_log_backend_memory_contexts(12345);  -- another backend, to the server log
```

**The kernel cache.** No PostgreSQL view sees it. `fincore <path>` from util-linux reports how much of a relation file is resident, and `pg_relation_filepath('orders')` gives the path.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** treating `shared_buffers` as "the cache" and `pg_stat_database` as its hit rate. The kernel page cache is a second, larger cache that PostgreSQL relies on and cannot see. A 93% hit ratio with every miss served from the kernel and a 93% hit ratio with every miss served from disk look identical in that view; only `track_io_timing` separates them.

- **The 25% rule is a starting point, not a derivation.** The documentation offers it for a dedicated server with at least 1 GB, says more than 40% is unlikely to help because the kernel caches too, and pairs any increase with a larger `max_wal_size`.   The ceiling exists because of double buffering: pages held in both caches are RAM spent twice, and the project's own asynchronous-I/O notes list removing that duplication as a motivation for direct I/O.  The `debug_io_direct` option that exists since 16 is a developer setting that the documentation says currently reduces performance; do not turn it on in production.
- **`effective_cache_size` allocates nothing.** It is a hint to the planner about how much of a table is likely to be in *either* cache, and the documentation says to count both shared buffers and the kernel cache, "though some data might exist in both places".  Raising it makes index scans look cheaper; it does not make anything cached.
- **A bulk `UPDATE` or `DELETE` defeats the ring.** The bulk-read ring ejects any page it dirties, so a statement that dirties every page fills the pool exactly as an unringed scan would, and evicts your working set.  Batch it, or accept the eviction.
- **`huge_pages = try` fails silently.** The lab server asked for 72 huge pages and got none, and nothing in the log said so on 16. Check `huge_pages_status` on 17+, or `/proc/meminfo`, after every restart.
- **`work_mem` is per operation, per process.** See the math above. The failure is not a slow query but a killed backend.
- **`temp_buffers` cannot be raised mid-session** once a temporary table has been used; set it in the connection's first statement.
- **Version drift.** The numbers here are PostgreSQL 16.2. Since then: the vacuum ring default is 2 MB (17), the bulk-read ring grows with `effective_io_concurrency` (18), `pg_stat_io` gained byte columns and WAL rows (18), `pg_backend_memory_contexts` changed shape (18), `EXPLAIN ANALYZE` shows buffers by default (18), and the free list is gone (19).      The mechanisms are the same; the constants moved.

What this post does not cover, by design: how the postmaster forks and supervises processes, how the checkpointer, background writer and WAL writer are scheduled, and how autovacuum decides what to do — that is part 2. The on-disk page format beyond `pd_lsn`, TOAST, the visibility map, indexes, and how WAL segments are archived and replayed — that is part 3. Replication, which reuses the WAL buffers for a different purpose, belongs to neither and is not here.

## Key takeaways

- PostgreSQL has three memory pools: shared buffers for pages, WAL buffers for log records, and per-process local memory for everything a query computes. The kernel page cache is a fourth pool it neither sizes nor sees.
- A page's fate in the pool is decided by a usage counter from 0 to 5 and a clock hand that lowers it; pages used often survive, pages read once do not, and a table that "fits" is cached only if it is read through the normal path rather than a ring.
- A scan of a table larger than a quarter of the pool runs through a 32-buffer ring on 16.x and leaves nothing else behind, which is why big tables re-read from the kernel every time and why `pg_stat_io.reuses` is the number to check.
- No dirty page may be written before the WAL up to its LSN is flushed; the first change to a page after a checkpoint logs the whole page, so checkpoint frequency, `wal_buffers` and `shared_buffers` are one decision, not three.
- `work_mem` and its relatives are per operation per process and are multiplied by parallel workers and sessions; the memory is freed by dropping a whole context, which is why a backend that grew by 85 MB gives it back the moment the query ends.

## Try it yourself

All three run against the lab's `memlab` database, or any table of your own with more pages than `shared_buffers / 4`.

1. Set `shared_buffers = 256MB`, restart, and predict from the arithmetic in the math section how many pages of `orders` a cold single-process scan will leave in shared buffers, and whether `customers` will now use a ring. Then measure with `pg_buffercache`.

<details><summary>Answer</summary>

`NBuffers` is now 32,768, the threshold `NBuffers/4` is 8,192 pages, and `orders` at 7,693 pages is *under* it. The scan uses the normal strategy, no ring, and all 7,693 pages stay resident; `customers` at 710 pages never used a ring. The bulk-read ring size did not change — it is 256 kB regardless of the pool — but the table no longer qualifies for it.

</details>

2. Run the two-update experiment from the worked example, but put `CHECKPOINT` between the two updates instead of before the first. Predict the two WAL byte counts from `pg_wal_lsn_diff` before running it.

<details><summary>Answer</summary>

Both updates now carry a full page image, because each is the first modification of the page after a checkpoint: roughly 7.5 kB each rather than 7.5 kB and 176 bytes. The second image will be a few bytes different from the first because the page's free-space hole shrank by one dead tuple version.

</details>

3. With `work_mem = '4MB'`, the lab's sort spilled 40,464 kB to disk and used `temp written=10135` blocks. Using the formula in the math section, estimate the smallest `work_mem` that keeps the sort in memory, then bisect with `SET work_mem` and `EXPLAIN ANALYZE`.

<details><summary>Answer</summary>

The in-memory run reported 81,868 kB, so any `work_mem` at or above about 82 MB should avoid the spill; the array of 2²⁰ × 24-byte entries alone is 24 MB and cannot shrink for a million rows. In practice the first value that stays in memory is a little above 81,868 kB because the sort also needs headroom for its own bookkeeping.

</details>

## References

### Lab downloads



- [`README.md`](LAB_01) — prerequisites, safe setup, run order, expected measurements, and cleanup.
- [`captures.json`](LAB_02) — machine-readable measurements collected by the lab runner.
- [`captures.md`](LAB_03) — readable captured output quoted throughout the article.
- [`run_lab.py`](LAB_04) — creates the disposable PostgreSQL setup and runs the memory experiments.
- [Lab Downloads](https://minio.canery.in/media/lab-postgresql-foundations-memory-layer.zip)

### Sources

**Papers (T1)**

1. Megiddo, N. and Modha, D. S. *ARC: A Self-Tuning, Low Overhead Replacement Cache.* USENIX FAST, 2003. https://www.usenix.org/conference/fast-03/arc-self-tuning-low-overhead-replacement-cache (accessed 2026-09-18)
2. Johnson, T. and Shasha, D. *2Q: A Low Overhead High Performance Buffer Management Replacement Algorithm.* VLDB, 1994, pp. 439–450. https://www.vldb.org/conf/1994/P439.PDF (accessed 2026-09-18)
3. Corbató, F. J. *A Paging Experiment with the Multics System.* MIT Project MAC, 1968; in *In Honor of P. M. Morse*, MIT Press, 1969, pp. 217–228. https://www.multicians.org/paging-experiment.pdf (accessed 2026-09-18)
4. Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H. and Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS 17(1), 1992, pp. 94–162. DOI 10.1145/128765.128770 (accessed 2026-09-17)
5. Stonebraker, M. and Rowe, L. A. *The Design of POSTGRES.* SIGMOD, 1986. https://dsf.berkeley.edu/papers/ERL-M85-95.pdf (accessed 2026-09-17)
6. Stonebraker, M., Rowe, L. A. and Hirohama, M. *The Implementation of POSTGRES.* IEEE TKDE 2(1), 1990. https://dsf.berkeley.edu/papers/ERL-M90-34.pdf (accessed 2026-09-17)

**PostgreSQL documentation and release notes (T2)**

7. PostgreSQL 16 documentation, *Resource Consumption* (§20.4) and *Write Ahead Log* (§20.5). https://www.postgresql.org/docs/16/runtime-config-resource.html · https://www.postgresql.org/docs/16/runtime-config-wal.html (accessed 2026-09-18)
8. PostgreSQL 18 documentation: *Resource Consumption*, *WAL Configuration* (§28.5), *Write-Ahead Logging* (§28.3), *Database Page Layout* (§66.6), *Database File Layout* (§66.1), *Query Planning* (§19.7), *Managing Kernel Resources* (§18.4), *Preset Options* (§19.15), *Lock Management* (§19.12), *Version and Platform Compatibility* (§19.13), *Developer Options* (§19.17), *The Cumulative Statistics System* (§27.2), `EXPLAIN`, `pg_shmem_allocations`, `pg_backend_memory_contexts`, `pg_log_backend_memory_contexts`, `pg_buffercache`, `pg_prewarm`, *A Brief History of PostgreSQL*. https://www.postgresql.org/docs/current/ (accessed 2026-09-17)
9. PostgreSQL 16 documentation, `pg_backend_memory_contexts`, `EXPLAIN`, *The Cumulative Statistics System* (§28.2). https://www.postgresql.org/docs/16/ (accessed 2026-09-17)
10. PostgreSQL release notes 8.0 (2005-01-19), 8.0.2 (2005-04-07), 8.1 (2005-11-08), 9.6, 13, 14, 15, 16, 17 and 18. https://www.postgresql.org/docs/release/ (accessed 2026-09-17 and 2026-09-18)
11. PostgreSQL versioning policy and the 2026-08-13 release announcement. https://www.postgresql.org/support/versioning/ (accessed 2026-09-17)

**Source code, commits and mailing list (T3)** — all at tag `REL_16_2` unless noted; identical text verified at `REL_18_6` where the post says so.

12. `src/backend/storage/buffer/README`; `src/include/storage/buf_internals.h`; `src/backend/storage/buffer/freelist.c`; `src/backend/storage/buffer/bufmgr.c`; `src/include/storage/lwlock.h`. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/storage/buffer (accessed 2026-09-18)
13. `src/backend/access/heap/heapam.c` (`initscan`, `heap_update`); `src/backend/access/transam/README`, `xlog.c`, `xact.c`; `src/backend/storage/smgr/md.c`; `src/backend/storage/file/fd.c`. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/access (accessed 2026-09-18)
14. `src/backend/utils/mmgr/README`, `aset.c`; `src/include/utils/memutils.h`; `src/backend/utils/sort/tuplesort.c`; `src/include/utils/tuplesort.h`; `src/backend/executor/nodeHash.c`; `src/backend/utils/adt/mcxtfuncs.c`; `src/backend/access/heap/vacuumlazy.c`; `src/backend/utils/misc/guc_tables.c`. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/utils (accessed 2026-09-17)
15. At `REL_18_6`: `src/backend/port/sysv_shmem.c`; `src/include/storage/pg_shmem.h`; `src/backend/storage/ipc/dsm.c`, `dsm_impl.c`, `ipci.c`, `shmem.c`; `src/backend/utils/mmgr/dsa.c`; `src/backend/access/transam/slru.c`, `clog.c`; `src/backend/storage/lmgr/lock.c`; `src/include/storage/proc.h`; `src/backend/storage/aio/README.md`. https://github.com/postgres/postgres/tree/REL_18_6 (accessed 2026-09-17)
16. Commits: 48354581a49c (lock-free buffer header, 2016-04-10); 9cd00c457e6a (checkpoint sorting, 2016-02-19); d6c08e29e7bc (`hash_mem_multiplier`, 2020-07-29); 667e65aac354 (TidStore for vacuum, 2024-04-02); c6e0fe1f2a08 (8-byte chunk header, 2022-08-29); 29f6a959cfd8 and 6ed83d5fa55c (bump allocator, 2024-04-07); 15f0cb26b530 (bulk-read ring growth, 2025-04-08). https://github.com/postgres/postgres/commits (accessed 2026-09-17)
17. Lane, T. *Escaping the ARC patent.* pgsql-hackers, 2005-02-03. https://www.postgresql.org/message-id/5609.1107469649@sss.pgh.pa.us (accessed 2026-09-18)
18. This post's reproducible lab used `run_lab.py` and `captures.md`, downloadable below: PostgreSQL 16.2 with default `postgresql.conf`, 16 CPUs, 15 GB RAM, Samsung NVMe, Linux 7.0, run 2026-09-17 and 2026-09-18.
