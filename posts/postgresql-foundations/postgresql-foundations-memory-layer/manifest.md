# Upload manifest — postgresql-foundations-memory-layer

Every placeholder in `blog.md`, in order of appearance. Upload each file to object
storage, put the resulting public URLs into `urls.txt` **in this row order**, then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/postgresql-foundations/postgresql-foundations-memory-layer/ posts/postgresql-foundations/postgresql-foundations-memory-layer/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/postgresql-foundations/postgresql-foundations-memory-layer/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery
contract rejects a non-URL there, so it must be resolved before upload. Suggested
object keys carry the post slug as a suffix so they cannot collide with the previous
posts' figures in the same flat bucket.

| Placeholder | File | Suggested object key | Alt text |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/postgresql-foundations-memory-layer/README.md` | Lab prerequisites, safe setup, run order, and cleanup |
| LAB_02 | `lab/captures.json` | `labs/postgresql-foundations-memory-layer/captures.json` | Machine-readable measurements |
| LAB_03 | `lab/captures.md` | `labs/postgresql-foundations-memory-layer/captures.md` | Readable captured output |
| LAB_04 | `lab/run_lab.py` | `labs/postgresql-foundations-memory-layer/run_lab.py` | Runnable memory experiments |
| COVER | `assets/cover.png` | `cover-postgresql-foundations-memory-layer.png` | Three stacked memory pools of a PostgreSQL server, with one small tangerine page moving from the shared pool towards the log |
| FIG_01 | `assets/fig-01-three-layers.png` | `fig-01-three-layers-postgresql-foundations-memory-layer.png` | Three horizontal layers labelled memory, process and storage, with the memory layer highlighted and annotated with shared buffers, WAL buffers and per-process memory |
| FIG_02 | `assets/fig-02-three-pools.png` | `fig-02-three-pools-postgresql-foundations-memory-layer.png` | One server box containing a shared memory region with shared buffers, WAL buffers and other structures, several backend boxes each with their own local memory, and beneath them the kernel page cache and the disk |
| FIG_03 | `assets/fig-03-shared-memory-map.png` | `fig-03-shared-memory-map-postgresql-foundations-memory-layer.png` | Horizontal bar of 143 MB with a 128 MB segment for buffer blocks and a 15 MB tail broken into XLOG Ctl, buffer descriptors, transaction-status caches and about fifty smaller pieces |
| FIG_04 | `assets/fig-04-three-levels.png` | `fig-04-three-levels-postgresql-foundations-memory-layer.png` | Four columns, one per lab step, each with three stacked levels labelled disk, kernel cache and shared buffers, showing 7,693 pages on disk only, then 7,693 in the kernel and 32 in shared buffers, then 7,693 in shared buffers after prewarm, then 320 after the forced sweep |
| FIG_05 | `assets/fig-05-the-threshold.png` | `fig-05-the-threshold-postgresql-foundations-memory-layer.png` | A horizontal scale from 0 to 16,384 pages with four marks: customers at 710, the quarter-pool threshold at 4,096, orders at 7,693 and the pool at 16,384 |
| FIG_06 | `assets/fig-06-buffer-anatomy.png` | `fig-06-buffer-anatomy-postgresql-foundations-memory-layer.png` | Byte layout of a 64-byte buffer descriptor: a 20-byte tag of five fields, a buffer id, a 32-bit state word split into 18 bits refcount, 4 bits usage count and 10 flag bits, a waiter field, a free-list link and an embedded content lock; beside it the 8 KB page it describes, and above them a hash table with 128 partitions mapping tags to buffer ids |
| FIG_07 | `assets/fig-07-hit-and-miss.png` | `fig-07-hit-and-miss-postgresql-foundations-memory-layer.png` | Sequence diagram with lanes for a backend, the buffer lookup table, a buffer descriptor, the WAL and the file: on a hit the backend hashes the tag, finds the buffer, pins it and bumps its usage count; on a miss it picks a victim via the clock sweep, flushes WAL and writes the victim if dirty, swaps the tag in the table, reads the page with pread, and marks it valid |
| FIG_08 | `assets/fig-08-clock-sweep-trace.png` | `fig-08-clock-sweep-trace-postgresql-foundations-memory-layer.png` | Three panels of the same eight-slot pool with a clock hand; slots carry usage counts 3, 0 (pinned), 1, 5, 0, 2, 1, 0; the hand starts at slot one, decrements the 3 to 2, skips the pinned slot, decrements the 1 to 0, decrements 5 to 4, and stops at the fifth slot whose count is 0, which becomes the victim |
| FIG_09 | `assets/fig-09-usage-histogram.png` | `fig-09-usage-histogram-postgresql-foundations-memory-layer.png` | Grouped bar chart of buffer counts at usage counts 0 through 5, before and after the forced sweep: before, 14,956 at zero and 883 at five; after, 5,148 at zero, 10,146 at one and 134 at five |
| FIG_10 | `assets/fig-10-replacement-timeline.png` | `fig-10-replacement-timeline-postgresql-foundations-memory-layer.png` | Timeline from 2005 to 2026: PostgreSQL 8.0 in January 2005 adopts ARC, 8.0.2 in April 2005 replaces it with 2Q over a patent, 8.1 in November 2005 adopts the clock sweep, 9.6 in 2016 makes the buffer header lock-free, 16 through 18 tune the rings, and 19 removes the free list |
| FIG_11 | `assets/fig-11-the-ring.png` | `fig-11-the-rin-postgresql-foundations-memory-layer.png` | A ring of 32 buffer slots with pages of a 7,693-page table cycling through it, one slot marked dirty and ejected to the normal pool, and three such rings drawn for a leader and two parallel workers |
| FIG_12 | `assets/fig-12-ring-sizes.png` | `fig-12-ring-sizes-postgresql-foundations-memory-layer.png` | Table graphic with three rows for bulk read, bulk write and vacuum rings: 256 KB / 32 buffers used by large sequential scans; 16 MB / 2,048 buffers used by COPY, CREATE TABLE AS, REFRESH MATERIALIZED VIEW and table rewrites; 256 KB in 16 and 2 MB from 17 used by VACUUM and ANALYZE; footnotes for the quarter-pool threshold, the one-eighth cap, and the 18 change that grows the read ring |
| FIG_13 | `assets/fig-13-wal-insert-path.png` | `fig-13-wal-insert-path-postgresql-foundations-memory-layer.png` | Sequence diagram with lanes for a backend, the WAL insert position, the WAL buffers, the WAL writer and the segment file: the backend reserves bytes under a spinlock, copies the record into the buffers under one of eight insertion locks, sets the page LSN, and at commit calls XLogFlush which writes and fsyncs the buffers to the segment; a side branch shows a full buffer forcing the inserter to write it out itself and count wal_buffers_full |
| FIG_14 | `assets/fig-14-full-page-image.png` | `fig-14-full-page-image-postgresql-foundations-memory-layer.png` | Two bars to scale: the first update's WAL is a 7,473-byte HOT_UPDATE record almost entirely filled by a 7,408-byte page image, with the 784-byte free-space hole shown as omitted, plus a 34-byte commit; the second update's WAL is three small records of 59, 70 and 34 bytes |
| FIG_15 | `assets/fig-15-when-a-page-may-leave.png` | `fig-15-when-a-page-may-leave-postgresql-foundations-memory-layer.png` | Timeline of WAL positions: a page is dirtied and stamped with LSN A; the WAL flush position advances past A at commit; only then may FlushBuffer write the page; at the next checkpoint the page is written and marked clean; a bar underneath shows the page's buffer state going valid, dirty, dirty and flushable, clean |
| FIG_16 | `assets/fig-16-per-process-budgets.png` | `fig-16-per-process-budgets-postgresql-foundations-memory-layer.png` | Plan tree for a parallel aggregate: a Gather Merge over three identical branches, leader and two workers, each annotated with its own hash aggregate at 2,065 kB in nine batches and its own external sort of about 2.5 MB on disk |
| FIG_17 | `assets/fig-17-sort-two-budgets.png` | `fig-17-sort-two-budgets-postgresql-foundations-memory-layer.png` | Two pairs of bars: with work_mem 4 MB the sort used 40,464 kB of temp files and took 662 ms; with 256 MB it used 81,868 kB of memory and took 493 ms |
| FIG_18 | `assets/fig-18-context-tree.png` | `fig-18-context-tree-postgresql-foundations-memory-layer.png` | Tree of memory contexts rooted at TopMemoryContext with children CacheMemoryContext, MessageContext, TopTransactionContext and PortalContext; under the portal, ExecutorState, then TupleSort main at 25,174,064 bytes with a child Caller tuples at 58,720,256 bytes; leaf sizes from the lab annotated, grand total 85,132,832 bytes |
| FIG_19 | `assets/fig-19-where-85-mb-went.png` | `fig-19-where-85-mb-went-postgresql-foundations-memory-layer.png` | Stacked bar of the sort's 85 MB split into the 25 MB SortTuple array and the 58.7 MB of tuples in 17 blocks, beside three bars for the backend's resident size: 12 MB idle, 97 MB with the cursor open, 18 MB after CLOSE |
| FIG_20 | `assets/fig-20-rest-of-shared-memory.png` | `fig-20-rest-of-shared-memory-postgresql-foundations-memory-layer.png` | Treemap of the 15 MB of non-buffer shared memory: XLOG Ctl 4.0 MB, anonymous allocations 4.6 MB, free 1.8 MB, buffer descriptors 1 MB, the CommitTs, Xact, Subtrans, MultiXact, Notify and Serial caches, checkpointer data and buffer ids, shared statistics, backend status arrays, and the lock and proc tables |
| FIG_21 | `assets/fig-21-huge-pages.png` | `fig-21-huge-pages-postgresql-foundations-memory-layer.png` | Two bars of equal length representing 143 MB of shared memory: the upper divided into 36,608 pages of 4 kB drawn as a dense grid, the lower into 72 pages of 2 MB, with a note that each page needs one TLB entry |
| FIG_22 | `assets/fig-22-tooling-map.png` | `fig-22-tooling-map-postgresql-foundations-memory-layer.png` | Grid mapping the three pools and the kernel cache to the tools that observe them: pg_shmem_allocations and pg_buffercache for shared buffers, pg_stat_wal and pg_walinspect for WAL buffers, pg_backend_memory_contexts and EXPLAIN for local memory, pg_stat_io across all three, and fincore for the kernel cache which no PostgreSQL view sees |

## Notes

- Every figure is our own redraw. None is reproduced from a paper, textbook, or
  documentation site; FIG_10 credits its dates to the release notes, FIG_08 draws the
  algorithm from the buffer README, FIG_07 and FIG_13 draw function names from the
  REL_16_2 tree.
- Every number in FIG_03, FIG_04, FIG_05, FIG_09, FIG_11, FIG_14, FIG_16, FIG_17, FIG_18,
  FIG_19, FIG_20 and FIG_21 is from `lab/captures.md` (PostgreSQL 16.2, default
  `postgresql.conf`). FIG_08 is a hand trace on a made-up 8-buffer pool and says so.
  FIG_09 is drawn on a log scale and its caption says so.
- The bucket keys are flat and nginx serves `/media/` as immutable for a year, so a
  corrected figure must be uploaded under a **new** filename, never overwritten.
- The `.html` sources in `assets/` (and `_build.py`, `_figs_a.py`, `_figs_b.py`,
  `_cover.py`, `_linkedin.py`) are what make the figures editable. PNG is exported at
  2× for the post; SVG is kept for zooming and later edits. Re-render everything with
  `python3 _figs_a.py && python3 _figs_b.py && python3 _cover.py && python3 _linkedin.py`
  from inside `assets/` (needs headless Chrome; Playwright is deliberately not used).
- The body keeps its `# How PostgreSQL Uses Memory` H1 so `validate_post.py` passes; the
  previous post dropped the H1 after upload because the platform renders the
  frontmatter title itself. Do the same here if the page shows the title twice.
