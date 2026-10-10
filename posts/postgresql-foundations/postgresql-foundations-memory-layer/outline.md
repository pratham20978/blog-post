# Outline — postgresql-foundations-memory-layer

**Series:** PostgreSQL Foundations, part 1 of 3 (memory layer → process layer → storage layer)
**Tier:** L4 pillar · **Budget:** ~9,500 words · **Figures:** 22 + cover (above the 12–18 band on purpose: the post spans seven mechanisms and every figure carries a lab number)
**Working title:** *How PostgreSQL Uses Memory* · slug `postgresql-foundations-memory-layer`
**Audience:** working engineers and CS students who run Postgres and have never looked inside it. Level intermediate. Prereqs: SQL, what a process and a page of memory are, having seen an EXPLAIN plan.

**Thesis.** PostgreSQL treats RAM as three pools, not one: a *shared* buffer pool of 8 KB page copies that every process maps; a small ring of *WAL buffers* whose contents must reach disk before any of those pages may; and *per-process working memory* that each sort or hash allocates and frees on its own. Every memory surprise an operator meets — a 60 MB table that "fits in cache" but leaves 256 KB behind, a 7.5 KB WAL record for a 2-byte update, a backend that balloons by 85 MB and shrinks again — is one of those three pools doing what it was designed to do. The post is built on a reproducible lab (PostgreSQL 16.2, default config) so every number in it was observed, not remembered.

**Series framing (first 100 words).** PostgreSQL's architecture is commonly split into three layers: memory, process, and storage. This post is layer one. It stops at the boundary where processes are scheduled (part 2) and where bytes hit files (part 3), and says so where it stops.

---

| # | Section | Target | Job | Figures |
|---|---|---|---|---|
| 1 | `# Title` + `## Insights` | 100 | the three-pool answer, and that every surprise is a pool doing its job | — |
| 2 | Who this is for + series note + jump list | 120 | level, prereqs, time; three layers, this is layer one | FIG_01 |
| 3 | `## Why this matters` | 350 | the 25% rule applied blindly; a table that fits in cache yet is re-read; a backend OOM-killed at 4× work_mem | — |
| 4 | `## The problem` | 720 | one process per connection, no threads; RAM must be shared without a shared address space; the OS already caches files; state the three pools precisely with sizes; the constraint: WAL before data | FIG_02 |
| 5 | `## Worked example` | 1,250 | the lab: 128 MB pool = 16,384 buffers; orders 7,693 pages vs customers 710; cold scan → 32 pages left, kernel keeps all; rescans; point lookup hit=3; sort on disk vs memory; the 7,544-byte update. All real EXPLAIN/pg_buffercache output | FIG_03, FIG_04, FIG_05 |
| 6 | `## Intuition` | 850 | the pool is a hotel with 16,384 rooms and a night clerk (clock hand) who lowers a "wanted" sign each pass; rings are a side door; WAL is the receipt book. Where each analogy breaks. | — |
| 7 | `## Shared buffers: what a buffer actually is` | 650 | descriptor (64 B) + page (8 KB); tag → hash table with 128 partitions; the 32-bit state word (18/4/10); pin vs content lock; hit path vs miss path at function level | FIG_06, FIG_07 |
| 8 | `## The clock sweep: how a page gets evicted` | 800 | the rule traced by hand on 8 buffers; usage cap 5 → ≤6 passes; free list until the pool fills; dirty victims written by the evicting backend; why not LRU: ARC (8.0) → 2Q (8.0.2, patent) → clock sweep (8.1); lock-free header (9.6); the lab's sweep: usage-5 pages survive, usage-1 pages go | FIG_08, FIG_09, FIG_10 |
| 9 | `## Rings: why a big scan leaves 256 KB behind` | 650 | NBuffers/4 threshold; 32-buffer ring; three processes = three rings; bulk-write 16 MB (CTAS left 2,080 pages); vacuum ring; dirty page ejection; pg_stat_io reuses = 7,661; 17/18 changes | FIG_11, FIG_12 |
| 10 | `## WAL buffers: the memory that must reach disk first` | 850 | write-ahead rule; pd_lsn ties page to log; insertion: reserve (spinlock) + copy (8 insert locks); commit = XLogFlush; wal_buffers = shared/32; wal_buffers_full = 8,919 during the load; full-page writes: 7,473 vs 70 bytes; FlushBuffer → XLogFlush; checkpoint clears dirty; ARIES lineage | FIG_13, FIG_14, FIG_15 |
| 11 | `## Local memory: work_mem and its family` | 700 | per operation × per process; 4 MB sort → 40 MB temp; 256 MB → 82 MB quicksort; parallel: 3 × 2,065 kB; hash_mem_multiplier 2.0 → 4.0 removes the spill; maintenance_work_mem and the old 1 GB vacuum cap; temp_buffers; the multiplication rule | FIG_16, FIG_17 |
| 12 | `## Memory contexts: how a backend allocates` | 650 | palloc + context tree; TopMemoryContext, CacheMemoryContext, MessageContext, TopTransactionContext, ExecutorState; AllocSet doubling 8 KB→8 MB, 8-byte chunk header; the sort's 85 MB = 2^20 × 24 B + 58.7 MB of tuples; RSS 12→97→18 MB; freeing by context | FIG_18, FIG_19 |
| 13 | `## The rest of shared memory` | 600 | the 15 MB that isn't buffers: XLOG Ctl, Xact/CommitTs/Subtrans SLRUs, lock table (64 × MaxBackends), PGPROC, checkpointer arrays; how the segment is created (mmap + tiny SysV); DSM/DSA for parallel query; huge pages: 143 MB = 72 × 2 MB | FIG_20, FIG_21 |
| 14 | `## The math` | 850 | (a) the three-level hit model and what blks_hit does not measure; (b) sizing arithmetic: descriptors, wal_buffers, ring sizes, threshold, lock table, huge pages; (c) clock-sweep cost bound ≤ (BM_MAX_USAGE_COUNT+1)·N; (d) sort memory = 24·2^⌈log₂n⌉ + Σtuples; (e) worst-case working memory = work_mem × ops × processes × sessions | — |
| 15 | `## Implementation` | 650 | the SQL toolkit: pg_shmem_allocations, pg_buffercache by relation, usage histogram, pg_stat_io by context, EXPLAIN (ANALYZE, BUFFERS), pg_backend_memory_contexts, pg_stat_wal; version notes (16 vs 18 column changes); link to lab/run_lab.py | FIG_22 |
| 16 | `## Limitations and common mistakes` | 450 | work_mem set globally high; shared_buffers as "the cache"; effective_cache_size is not an allocation; 25% rule origin; huge_pages=try silently failing; reading blks_hit as disk avoidance; bulk UPDATE defeats the ring; what this post does not cover (processes, storage, replication) | — |
| 17 | `## Key takeaways` | 100 | 5 claims | — |
| 18 | `## Try it yourself` | 200 | 3 exercises with hidden answers, runnable on the lab | — |
| 19 | `## References` | 60 | ledger sources actually used, grouped T1/T2/T3 | — |

**Total target:** ~9,600 words.

---

## Figure plan

| ID | Type | Route | Carries |
|---|---|---|---|
| COVER | template cover | diagram-design skin | three stacked pools, one tangerine page |
| FIG_01 | layer stack | diagram-design layers | memory / process / storage, this post highlighted |
| FIG_02 | containment | diagram-design nested | one server: shared memory (buffers, WAL buffers, other) + N backends' local memory, over the kernel page cache, over disk |
| FIG_03 | part-of-whole bars | diagram-design bar, to scale | pg_shmem_allocations: 128 MB buffer blocks vs 15 MB of 56 other allocations |
| FIG_04 | three-level residency | small multiples | where the 7,693 pages of `orders` are (disk / kernel / shared) after: restart+drop, cold scan, prewarm, sweep |
| FIG_05 | scale bar | diagram-design, to scale | 710 · 4,096 · 7,693 · 16,384 pages: customers, NBuffers/4, orders, the pool |
| FIG_06 | byte layout | diagram-design, to scale | BufferDesc 64 B (tag 20 B, id, state 32-bit split 18/4/10, lock) ↔ 8 KB page; 128-partition hash table |
| FIG_07 | sequence | Mermaid sequenceDiagram → redraw | hit vs miss: lookup, pin, (victim, flush WAL, write, retag, pread), valid |
| FIG_08 | algorithm trace | small multiples | clock sweep on 8 buffers with usage counts, 3 hand positions |
| FIG_09 | timeline | diagram-design timeline | LRU → ARC 8.0 (2005-01) → 2Q 8.0.2 (2005-04) → clock 8.1 (2005-11) → lock-free header 9.6 (2016) → rings tuned 16/17/18 → free list gone 19 |
| FIG_10 | grouped bars | diagram-design bar | usage-count histogram before and after the forced sweep (lab numbers) |
| FIG_11 | process | diagram-design | a 32-slot ring cycling through 7,693 pages; a dirtied slot ejected; three rings for three processes |
| FIG_12 | comparison table graphic | diagram-design | ring sizes, users, threshold and cap; 16.2 vs 17 vs 18 |
| FIG_13 | sequence | Mermaid sequenceDiagram → redraw | WAL insert: reserve → copy under insert lock → commit → XLogFlush → segment; wal_buffers_full path |
| FIG_14 | to-scale bars | diagram-design | the two updates' WAL: 7,473 (FPI 7,408 + hole 784 omitted) + 34 vs 59 + 70 + 34 |
| FIG_15 | timeline | diagram-design | page LSN vs WAL flush LSN: when a dirty page may be written; checkpoint |
| FIG_16 | plan tree with memory | diagram-design | leader + 2 workers each with 2,065 kB hash and own sort |
| FIG_17 | bars | diagram-design bar | 4 MB: 40,464 kB temp, 662 ms; 256 MB: 81,868 kB memory, 493 ms |
| FIG_18 | tree | diagram-design tree | memory context tree of the lab backend with sizes |
| FIG_19 | stacked bars | diagram-design | the sort's 85 MB: 2^20 × 24 B array + 17 Generation blocks; RSS 12 → 97 → 18 MB |
| FIG_20 | map | diagram-design nested | the non-buffer 15 MB: XLOG Ctl, SLRUs, locks, procs, checkpointer, stats (lab sizes) |
| FIG_21 | to-scale comparison | diagram-design | 143 MB as 36,608 × 4 kB pages vs 72 × 2 MB huge pages |
| FIG_22 | tooling map | diagram-design | which view/command sees which pool |

Ratio: 22 figures / 9,600 words ≈ one per 440 words — dense, but every figure carries a distinct lab number or mechanism; none repeats a neighbour at a different zoom.

---

## Padding test

After each section the reader can:

- Problem → name the three pools and say which one the OS page cache is not
- Worked example → predict from a table's page count whether a scan will leave it cached
- Intuition → explain eviction, rings and WAL in one sentence each, and say where the analogies break
- Shared buffers → read a pg_buffercache row and say what pin, usage count and dirty mean
- Clock sweep → trace a victim choice by hand; explain why ARC was dropped
- Rings → explain "shared hit=32 read=7661"
- WAL buffers → explain why the first update after a checkpoint costs 100× the second
- Local memory → compute a query's worst-case working memory
- Contexts → read pg_log_backend_memory_contexts output and know why memory came back
- Rest of shared memory → account for the 15 MB that is not buffers; size huge pages
- Math → do the sizing arithmetic for a different shared_buffers
- Implementation → run the toolkit on their own server

No two answers match. Sections 7–13 each own one pool or one mechanism.
