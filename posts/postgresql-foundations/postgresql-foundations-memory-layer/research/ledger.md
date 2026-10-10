# Source ledger — postgresql-foundations-memory-layer

Research ran 2026-09-17 (nine parallel sweeps over primary sources, one per sub-topic) and
2026-09-18 (buffer-replacement history, read/write path, and constant-by-constant
spot-checks against the REL_16_2 tree). Source-code citations use release tags, never
branches. The post's live examples were captured on PostgreSQL 16.2, so every
version-dependent claim names the version it holds for; "current" means the 18.x docs
as fetched on the access date.

## Sources

| ID | Tier | Source | URL | Accessed |
|---|---|---|---|---|
| S1 | T2 | PostgreSQL 16 docs, §20.4 Resource Consumption (shared_buffers, work_mem, hash_mem_multiplier, maintenance_work_mem, temp_buffers, vacuum_buffer_usage_limit, max_parallel_workers_per_gather) | https://www.postgresql.org/docs/16/runtime-config-resource.html | 2026-09-18 |
| S2 | T2 | PostgreSQL 18 docs, §19.4 Resource Consumption (same entries; io_method, io_workers, io_combine_limit, effective_io_concurrency, SLRU buffer GUCs) | https://www.postgresql.org/docs/current/runtime-config-resource.html | 2026-09-17 |
| S3 | T2 | PostgreSQL 16 docs, §20.5 Write Ahead Log (wal_buffers, wal_writer_delay, synchronous_commit, full_page_writes, checkpoint_* , max_wal_size) | https://www.postgresql.org/docs/16/runtime-config-wal.html | 2026-09-18 |
| S4 | T2 | PostgreSQL 18 docs, §28.5 WAL Configuration (checkpoints, XLogInsertRecord/XLogFlush, wal_buffers advice) | https://www.postgresql.org/docs/current/wal-configuration.html | 2026-09-17 |
| S5 | T2 | PostgreSQL 18 docs, §28.3 Write-Ahead Logging (WAL) | https://www.postgresql.org/docs/current/wal-intro.html | 2026-09-17 |
| S6 | T2 | PostgreSQL 18 docs, §66.6 Database Page Layout | https://www.postgresql.org/docs/current/storage-page-layout.html | 2026-09-17 |
| S7 | T2 | PostgreSQL 18 docs, §66.1 Database File Layout | https://www.postgresql.org/docs/current/storage-file-layout.html | 2026-09-17 |
| S8 | T2 | PostgreSQL 18 docs, §19.7 Query Planning (effective_cache_size) | https://www.postgresql.org/docs/current/runtime-config-query.html | 2026-09-17 |
| S9 | T2 | PostgreSQL 18 docs, §18.4 Managing Kernel Resources (shared memory, huge pages) | https://www.postgresql.org/docs/current/kernel-resources.html | 2026-09-17 |
| S10 | T2 | PostgreSQL 18 docs, §19.15 Preset Options (shared_memory_size, shared_memory_size_in_huge_pages, block_size, wal_segment_size) | https://www.postgresql.org/docs/current/runtime-config-preset.html | 2026-09-17 |
| S11 | T2 | PostgreSQL 18 docs, §19.12 Lock Management (max_locks_per_transaction) | https://www.postgresql.org/docs/current/runtime-config-locks.html | 2026-09-17 |
| S12 | T2 | PostgreSQL 18 docs, pg_shmem_allocations view | https://www.postgresql.org/docs/current/view-pg-shmem-allocations.html | 2026-09-17 |
| S13 | T2 | PostgreSQL 16 docs, pg_backend_memory_contexts view | https://www.postgresql.org/docs/16/view-pg-backend-memory-contexts.html | 2026-09-17 |
| S14 | T2 | PostgreSQL 18 docs, pg_backend_memory_contexts view | https://www.postgresql.org/docs/current/view-pg-backend-memory-contexts.html | 2026-09-17 |
| S15 | T2 | PostgreSQL 18 docs, §9.28 System Administration Functions (pg_log_backend_memory_contexts) | https://www.postgresql.org/docs/current/functions-admin.html | 2026-09-17 |
| S16 | T2 | PostgreSQL 18 docs, F.25 pg_buffercache | https://www.postgresql.org/docs/current/pgbuffercache.html | 2026-09-17 |
| S17 | T2 | PostgreSQL 18 docs, F.30 pg_prewarm | https://www.postgresql.org/docs/current/pgprewarm.html | 2026-09-17 |
| S18 | T2 | PostgreSQL 18 docs, §27.2 Cumulative Statistics (pg_stat_io, pg_stat_wal, pg_stat_bgwriter, pg_stat_checkpointer, pg_stat_database) | https://www.postgresql.org/docs/current/monitoring-stats.html | 2026-09-17 |
| S19 | T2 | PostgreSQL 16 docs, §28.2 Cumulative Statistics (pg_stat_io with op_bytes, pg_stat_bgwriter with checkpoint columns, pg_stat_wal eight columns) | https://www.postgresql.org/docs/16/monitoring-stats.html | 2026-09-17 |
| S20 | T2 | PostgreSQL 18 docs, EXPLAIN reference (BUFFERS) | https://www.postgresql.org/docs/current/sql-explain.html | 2026-09-17 |
| S21 | T2 | PostgreSQL 16 docs, EXPLAIN reference (BUFFERS defaults to FALSE) | https://www.postgresql.org/docs/16/sql-explain.html | 2026-09-17 |
| S22 | T2 | PostgreSQL 18 docs, §19.17 Developer Options (debug_io_direct) | https://www.postgresql.org/docs/current/runtime-config-developer.html | 2026-09-17 |
| S23 | T2 | PostgreSQL 18 docs, §2 A Brief History of PostgreSQL | https://www.postgresql.org/docs/current/history.html | 2026-09-17 |
| S24 | T2 | PostgreSQL release notes, 8.0 (2005-01-19) | https://www.postgresql.org/docs/release/8.0.0/ | 2026-09-18 |
| S25 | T2 | PostgreSQL release notes, 8.0.2 (2005-04-07) | https://www.postgresql.org/docs/release/8.0.2/ | 2026-09-18 |
| S26 | T2 | PostgreSQL release notes, 8.1 (2005-11-08) | https://www.postgresql.org/docs/release/8.1.0/ | 2026-09-18 |
| S27 | T2 | PostgreSQL release notes, 9.6 (2016-09-29) | https://www.postgresql.org/docs/release/9.6.0/ | 2026-09-17 |
| S28 | T2 | PostgreSQL release notes, 13 (2020-09-24) | https://www.postgresql.org/docs/release/13.0/ | 2026-09-17 |
| S29 | T2 | PostgreSQL release notes, 14 (2021-09-30) | https://www.postgresql.org/docs/release/14.0/ | 2026-09-17 |
| S30 | T2 | PostgreSQL release notes, 15 (2022-10-13) | https://www.postgresql.org/docs/release/15.0/ | 2026-09-17 |
| S31 | T2 | PostgreSQL release notes, 16 (2023-09-14) | https://www.postgresql.org/docs/release/16.0/ | 2026-09-17 |
| S32 | T2 | PostgreSQL release notes, 17 (2024-09-26) | https://www.postgresql.org/docs/release/17.0/ | 2026-09-17 |
| S33 | T2 | PostgreSQL release notes, 18 (2025-09-25) | https://www.postgresql.org/docs/release/18.0/ | 2026-09-17 |
| S34 | T2 | PostgreSQL versioning policy and the 2026-08-13 release announcement (18.6, 17.11, 16.15, 19 Beta 3) | https://www.postgresql.org/support/versioning/ · https://www.postgresql.org/about/news/postgresql-186-1711-1615-1519-1424-and-19-beta-3-released-3365/ | 2026-09-17 |
| S35 | T3 | PostgreSQL source, src/backend/storage/buffer/README, tag REL_16_2 (text identical at REL_18_6 except the BM_IO_IN_PROGRESS paragraph) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/storage/buffer/README | 2026-09-18 |
| S36 | T3 | PostgreSQL source, src/include/storage/buf_internals.h, tag REL_16_2 (state word, flags, BufferTag, BufferDesc, BM_MAX_USAGE_COUNT, BUFFERDESC_PAD_TO_SIZE) | https://github.com/postgres/postgres/blob/REL_16_2/src/include/storage/buf_internals.h | 2026-09-18 |
| S37 | T3 | PostgreSQL source, src/backend/storage/buffer/freelist.c, tag REL_16_2 (ClockSweepTick, StrategyGetBuffer, GetAccessStrategy, GetAccessStrategyWithSize, GetBufferFromRing) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/storage/buffer/freelist.c | 2026-09-18 |
| S38 | T3 | PostgreSQL source, src/backend/storage/buffer/bufmgr.c, tag REL_16_2 (ReadBuffer_common, BufferAlloc, GetVictimBuffer, PinBuffer, FlushBuffer, BufferSync, BgBufferSync) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/storage/buffer/bufmgr.c | 2026-09-18 |
| S39 | T3 | PostgreSQL source, src/include/storage/lwlock.h, tag REL_16_2 (NUM_BUFFER_PARTITIONS) | https://github.com/postgres/postgres/blob/REL_16_2/src/include/storage/lwlock.h | 2026-09-18 |
| S40 | T3 | PostgreSQL source, src/backend/access/heap/heapam.c, tag REL_16_2 (initscan NBuffers/4 rule; heap_update critical section) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/heapam.c | 2026-09-18 |
| S41 | T3 | PostgreSQL source, src/backend/access/transam/xlog.c, tag REL_16_2 (NUM_XLOGINSERT_LOCKS, XLogInsertRecord, ReserveXLogInsertLocation, AdvanceXLInsertBuffer, XLogFlush, XLOGChooseNumBuffers, check_wal_buffers) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/transam/xlog.c | 2026-09-18 |
| S42 | T3 | PostgreSQL source, src/backend/access/transam/README, tag REL_16_2 ("Write-Ahead Log Coding", "Asynchronous Commit") | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/transam/README | 2026-09-18 |
| S43 | T3 | PostgreSQL source, src/backend/access/transam/xact.c, tag REL_16_2 (RecordTransactionCommit) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/transam/xact.c | 2026-09-18 |
| S44 | T3 | PostgreSQL source, src/backend/storage/smgr/md.c and src/backend/storage/file/fd.c, tag REL_16_2 (mdread → FileRead → pg_pread; mdwrite) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/storage/smgr/md.c | 2026-09-18 |
| S45 | T3 | PostgreSQL source, src/backend/utils/mmgr/README, tag REL_16_2 (memory context design) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/utils/mmgr/README | 2026-09-17 |
| S46 | T3 | PostgreSQL source, src/backend/utils/mmgr/aset.c and src/include/utils/memutils.h, tag REL_16_2 (ALLOCSET_* sizes, chunk limit, MaxAllocSize) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/utils/mmgr/aset.c | 2026-09-17 |
| S47 | T3 | PostgreSQL source, src/backend/utils/sort/tuplesort.c and src/include/utils/tuplesort.h, tag REL_16_2 (allowedMem, "TupleSort main", "Caller tuples" Generation context, SortTuple) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/utils/sort/tuplesort.c | 2026-09-18 |
| S48 | T3 | PostgreSQL source, src/backend/executor/nodeHash.c, tag REL_16_2 (get_hash_memory_limit) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/executor/nodeHash.c | 2026-09-17 |
| S49 | T3 | PostgreSQL source, src/backend/port/sysv_shmem.c and src/include/storage/pg_shmem.h, tag REL_18_6 (anonymous mmap, MAP_HUGETLB, SysV interlock, PGShmemHeader) | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/port/sysv_shmem.c | 2026-09-17 |
| S50 | T3 | PostgreSQL source, src/backend/storage/ipc/dsm.c, dsm_impl.c and src/backend/utils/mmgr/dsa.c, tag REL_18_6 | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/storage/ipc/dsm.c | 2026-09-17 |
| S51 | T3 | PostgreSQL source, src/backend/access/transam/slru.c and clog.c, tags REL_16_2 and REL_18_6 (SLRU pools, CLOGShmemBuffers, banks) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/transam/clog.c | 2026-09-17 |
| S52 | T3 | PostgreSQL source, src/backend/storage/lmgr/lock.c and src/include/storage/proc.h, tag REL_18_6 (NLOCKENTS, PGPROC) | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/storage/lmgr/lock.c | 2026-09-17 |
| S53 | T3 | Commit 48354581a49c "Allow Pin/UnpinBuffer to operate in a lockfree manner" (Andres Freund, Alexander Korotkov), 2016-04-10 | https://github.com/postgres/postgres/commit/48354581a49c30f5757c203415aa8412d85b0f70 | 2026-09-17 |
| S54 | T3 | Commit 9cd00c457e6a "Checkpoint sorting and balancing" (Fabien Coelho, Andres Freund), 2016-02-19 | https://github.com/postgres/postgres/commit/9cd00c457e6a1ebb984167ac556a9961812a683c | 2026-09-17 |
| S55 | T3 | Commit d6c08e29e7bc "Add hash_mem_multiplier GUC" (Peter Geoghegan), 2020-07-29 | https://github.com/postgres/postgres/commit/d6c08e29e7bc8bc3bf49764192c4a9c71fc0b097 | 2026-09-17 |
| S56 | T3 | Commit 667e65aac354 "Use TidStore for dead tuple TIDs storage during lazy vacuum" (Masahiko Sawada), 2024-04-02 | https://github.com/postgres/postgres/commit/667e65aac354975c6f8090c6146fceb8d7b762d6 | 2026-09-17 |
| S57 | T3 | Commit c6e0fe1f2a08 "Improve performance of and reduce overheads of memory management" (David Rowley), 2022-08-29 | https://github.com/postgres/postgres/commit/c6e0fe1f2a08505544c410f613839664eea9eb21 | 2026-09-17 |
| S58 | T3 | Commit 29f6a959cfd8 "Introduce a bump memory allocator" and 6ed83d5fa55c "Use bump memory context for tuplesorts" (David Rowley), 2024-04-07 | https://github.com/postgres/postgres/commit/29f6a959cfd8ffa7d6db2c0629439c5329e2853e | 2026-09-17 |
| S59 | T3 | Commit 15f0cb26b530 "Increase BAS_BULKREAD based on effective_io_concurrency" (Andres Freund), 2025-04-08 | https://github.com/postgres/postgres/commit/15f0cb26b530b6725a37391738cfc62d4745c49b | 2026-09-17 |
| S60 | T3 | Tom Lane, "Escaping the ARC patent", pgsql-hackers, 2005-02-03 | https://www.postgresql.org/message-id/5609.1107469649@sss.pgh.pa.us | 2026-09-18 |
| S61 | T1 | Megiddo & Modha, "ARC: A Self-Tuning, Low Overhead Replacement Cache", USENIX FAST 2003 | https://www.usenix.org/conference/fast-03/arc-self-tuning-low-overhead-replacement-cache | 2026-09-18 |
| S62 | T1 | Johnson & Shasha, "2Q: A Low Overhead High Performance Buffer Management Replacement Algorithm", VLDB 1994, pp. 439–450 | https://www.vldb.org/conf/1994/P439.PDF | 2026-09-18 |
| S63 | T1 | Corbató, "A Paging Experiment with the Multics System", MIT Project MAC, 1968 (in *In Honor of P. M. Morse*, MIT Press 1969, pp. 217–228) | https://www.multicians.org/paging-experiment.pdf | 2026-09-18 |
| S64 | T1 | Mohan, Haderle, Lindsay, Pirahesh, Schwarz, "ARIES: A Transaction Recovery Method…", ACM TODS 17(1), 1992, pp. 94–162 | https://cs.stanford.edu/people/chrismre/cs345/rl/aries.pdf (DOI 10.1145/128765.128770) | 2026-09-17 |
| S65 | T1 | Stonebraker & Rowe, "The Design of POSTGRES", SIGMOD 1986 (UCB/ERL M85/95) | https://dsf.berkeley.edu/papers/ERL-M85-95.pdf | 2026-09-17 |
| S66 | T1 | Stonebraker, Rowe & Hirohama, "The Implementation of POSTGRES", IEEE TKDE 2(1), 1990 (ERL-M90-34) | https://dsf.berkeley.edu/papers/ERL-M90-34.pdf | 2026-09-17 |
| S67 | T3 | PostgreSQL source, src/backend/storage/aio/README.md, tag REL_18_6 ("double buffering" rationale) | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/storage/aio/README.md | 2026-09-17 |
| S68 | T3 | Lab captures on PostgreSQL 16.2, default postgresql.conf, this post's `lab/run_lab.py` (numbers reproduced on 2026-09-17/18) | lab/captures.md | 2026-09-18 |
| S69 | T3 | PostgreSQL source, src/backend/utils/misc/guc_tables.c, tags REL_16_2 and REL_18_6 (boot values) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/utils/misc/guc_tables.c | 2026-09-17 |
| S70 | T3 | PostgreSQL source, src/backend/utils/adt/mcxtfuncs.c and src/backend/utils/mmgr/mcxt.c, tag REL_16_2 (0-based level; MemoryContextStatsDetail 100/100) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/utils/adt/mcxtfuncs.c | 2026-09-17 |
| S71 | T3 | PostgreSQL source, src/backend/access/heap/vacuumlazy.c, tag REL_16_2 (dead_items_max_items, MaxAllocSize cap) | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/vacuumlazy.c | 2026-09-17 |
| S72 | T3 | PostgreSQL source, src/backend/storage/ipc/ipci.c and shmem.c, tag REL_18_6 (CalculateShmemSize, ShmemIndex, no free) | https://github.com/postgres/postgres/blob/REL_18_6/src/backend/storage/ipc/ipci.c | 2026-09-17 |
| S73 | T2 | PostgreSQL 18 docs, Appendix K Limits; §19.4 (huge_pages); initdb reference | https://www.postgresql.org/docs/current/limits.html | 2026-09-17 |
| S74 | T2 | PostgreSQL 18 docs, §19.13 Version and Platform Compatibility (synchronize_seqscans) | https://www.postgresql.org/docs/current/runtime-config-compatible.html | 2026-09-17 |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | shared_buffers defaults to 128 MB (16,384 blocks of 8 kB), must be at least 128 kB, and can only be set at server start | S1 §20.4.1; S69 | default build, BLCKSZ 8192 |
| L02 | The docs' starting point for a dedicated server with ≥1 GB RAM is shared_buffers = 25% of memory, and they say more than 40% is unlikely to beat a smaller value because PostgreSQL also relies on the OS cache | S1 §20.4.1 | guidance, not a measured law |
| L03 | The docs note that a larger shared_buffers usually needs a larger max_wal_size so checkpoint writes are spread over a longer period | S1 §20.4.1 | — |
| L04 | A database page is 8 kB by default and consists of a 24-byte header, 4-byte line pointers growing from the front, free space, and items growing from the end | S6 Table 66.2/66.3 | default BLCKSZ; layout version 4 |
| L05 | The first field of every page header, pd_lsn, holds the position just past the last WAL record that changed the page | S6 Table 66.3 | — |
| L06 | A relation larger than 1 GB is split into 1 GB segment files, and each table also has FSM and visibility-map forks | S7 §66.1 | default --with-segsize |
| L07 | Each buffer descriptor packs refcount (18 bits), usage count (4 bits) and 10 flag bits into one 32-bit atomic state word | S36 header comment | REL_16_2; same in 18 |
| L08 | BM_MAX_USAGE_COUNT is 5, so usage counts saturate at 5 and the source comment warns it can take up to 6 full clock passes to find a victim | S36 #define BM_MAX_USAGE_COUNT | REL_16_2 and REL_18_6 |
| L09 | On 64-bit builds every BufferDesc is padded to a 64-byte stride so descriptors are cache-line aligned | S36 BUFFERDESC_PAD_TO_SIZE | SIZEOF_VOID_P == 8 |
| L10 | A BufferTag identifies a block by tablespace OID, database OID, relation file number, fork number and block number | S36 struct buftag | — |
| L11 | The buffer lookup table is a shared hash table keyed by BufferTag and guarded by 128 partition locks (NUM_BUFFER_PARTITIONS) | S39; S35 "Buffer Manager's Internal Locking" | REL_16_2 and REL_18_6 |
| L12 | A lookup takes only a shared lock on one partition; the buffer must be pinned before the lock is released; re-assigning a buffer to another page needs the partition lock exclusively | S35 locking section; S38 BufferAlloc | — |
| L13 | A pin is a per-buffer reference count; an unpinned buffer may be reused for another page at any instant, and pins may not be held across transaction boundaries | S35 "Pins" paragraph | — |
| L14 | PinBuffer is a compare-and-swap loop that increments the refcount and, for the normal strategy, the usage count up to the maximum; a ring strategy only raises usage from 0 to 1 | S38 PinBuffer | REL_16_2 |
| L15 | The header spinlock is the BM_LOCKED bit inside the state word; the lock-free header design shipped in 9.6 via commit 48354581a49c, which reported up to 8× read-only pgbench gains at high client counts | S53; S27 | 9.6.0, 2016-09-29 |
| L16 | Because the refcount field has 18 bits, MAX_BACKENDS is 2^18 − 1 = 262,143 | S36/S53 commit message | since 9.6 |
| L17 | The clock hand nextVictimBuffer is an atomic counter advanced without a lock; only the backend that wraps it takes the strategy lock to bump completePasses | S37 ClockSweepTick | REL_16_2 |
| L18 | The sweep rule: a pinned buffer is skipped; an unpinned buffer with usage > 0 has its count decremented and is skipped; an unpinned buffer with usage 0 is the victim | S35 steps 3–5; S37 StrategyGetBuffer | — |
| L19 | Before sweeping, StrategyGetBuffer pops the free list; at startup every buffer is on that list, which is why a fresh server evicts nothing until the pool fills | S37; S38 buf_init | REL_16_2 through 18.x (free list removed on master after 18) |
| L20 | If the sweep sees NBuffers pinned buffers in a row it errors with "no unpinned buffers available" | S37 | — |
| L21 | The evicting backend writes a dirty victim itself: GetVictimBuffer takes a conditional shared content lock and calls FlushBuffer, or gives up and picks another victim | S38 GetVictimBuffer | REL_16_2 |
| L22 | On a miss, BufferAlloc inserts the new tag under the exclusive partition lock, sets BM_TAG_VALID and usage count 1, and BM_VALID only after the read completes | S38 BufferAlloc | REL_16_2 |
| L23 | In 16.x the requesting backend reads the page itself: ReadBuffer_common calls smgrread, which reaches mdread and a pread() on the segment file | S38 ReadBuffer_common; S44 mdread/FileRead | REL_16_2 (18 routes misses through the AIO subsystem) |
| L24 | The BM_IO_IN_PROGRESS flag plus a per-buffer condition variable replaced the per-buffer I/O LWLock in PostgreSQL 14 | S35 | 14+ |
| L25 | MarkBufferDirty requires a pin and an exclusive content lock and sets BM_DIRTY and BM_JUST_DIRTIED; page contents are protected by the embedded content LWLock, not the header spinlock | S38 MarkBufferDirty; S35 | — |
| L26 | PostgreSQL 8.0 (2005-01-19) replaced LRU with ARC, a four-list policy tracking recency and frequency, because LRU let large scans push out useful pages | S24 | 8.0 |
| L27 | PostgreSQL 8.0.2 (2005-04-07) replaced ARC with 2Q to avoid a pending US patent on ARC, noting 2Q might be a few percent slower | S25 | 8.0.2 |
| L28 | Tom Lane's 2005-02-03 proposal argued the ARC patent hinged on the word "adaptively", that 2Q with fixed list sizes gives the same scan resistance, and that it could be done mostly by deletions from freelist.c | S60 | — |
| L29 | PostgreSQL 8.1 (2005-11-08) overhauled buffer-manager locking for multi-CPU scalability and switched to the clock-sweep replacement policy | S26 | 8.1 |
| L30 | ARC (Megiddo & Modha, FAST 2003) adaptively balances recency and frequency with constant per-request overhead and is scan-resistant; on an SPC1-like trace with a 4 GB cache it reached a 20% hit ratio against LRU's 9.19% | S61 abstract | the benchmark figure is the paper's own |
| L31 | 2Q (Johnson & Shasha, VLDB 1994) puts first-touched pages in a FIFO A1in queue, remembers evicted identifiers in A1out, and promotes to the main LRU queue Am only on a re-reference; recommended sizes are Kin ≈ 25% of the buffer and Kout identifiers for ≈ 50% | S62 §2–3 | — |
| L32 | Corbató's 1968 Multics experiment describes the clock algorithm: a pointer cycling a circular list, a per-page usage bit set on reference and cleared by the sweep, and replacement of the first page whose bit is clear | S63 pp. 219–220 | k = 1 shift register case |
| L33 | Bulk-access rings: a sequential scan uses a 256 kB ring (32 buffers), COPY/CTAS use a 16 MB ring, VACUUM's ring is vacuum_buffer_usage_limit (256 kB in 16.2), and any ring is capped at NBuffers/8 | S37 GetAccessStrategy, GetAccessStrategyWithSize; S1 | REL_16_2 |
| L34 | A heap scan uses the bulk-read ring (and synchronized scanning) only when the table has more than NBuffers/4 blocks; smaller tables are read with the normal strategy | S40 initscan | REL_16_2 and 18 |
| L35 | The README's rationale: 256 kB fits in L2 cache so OS-cache-to-shared-buffer copies stay cheap, and leaves a trail for synchronized scans to join | S35 "Buffer Ring Replacement Strategy" | — |
| L36 | If a bulk-read ring buffer is dirtied and would need a WAL flush, it is dropped from the ring and replaced via the normal sweep; a scan that dirties every page degrades to the normal strategy | S35; S37 StrategyRejectBuffer | BAS_BULKREAD only |
| L37 | VACUUM and bulk-write rings keep dirty pages and flush WAL as needed; before rings arrived in 8.3, VACUUM's buffers went to the free list, effectively a 1-buffer ring that flushed WAL excessively | S35 | — |
| L38 | The 16 MB bulk-write ring exists because smaller rings made COPY block too often on WAL flushes | S35 | — |
| L39 | A ring slot is reused only if its buffer has refcount 0 and usage count ≤ 1; otherwise the ring takes a fresh victim from the normal sweep | S37 GetBufferFromRing | — |
| L40 | In pg_stat_io, context is normal, vacuum, bulkread or bulkwrite; "reuses" counts ring slots reused and "evictions" counts blocks evicted from shared buffers | S18 pg_stat_io; S31 | 16+ |
| L41 | In PostgreSQL 17 the vacuum ring default rose to 2 MB, and in 18 the bulk-read ring grows by io_combine_limit × effective_io_concurrency blocks (2,304 kB with defaults) | S32; S59; S2 | 17+ / 18+ |
| L42 | Resource limits such as work_mem apply to each parallel worker individually, so total use can be far higher than for one process | S1 max_parallel_workers_per_gather | — |
| L43 | The write-ahead rule in the project's words: data-file changes may be written only after the WAL records describing them are flushed to permanent storage; recovery is roll-forward (REDO) only | S5 §28.3 | — |
| L44 | Syncing the sequential WAL at commit is far cheaper than flushing every data page the transaction touched | S5 §28.3 | — |
| L45 | wal_buffers defaults to −1, meaning 1/32 of shared_buffers, not less than 64 kB and not more than one WAL segment (typically 16 MB); a manual value under 32 kB is treated as 32 kB | S3 wal_buffers; S41 XLOGChooseNumBuffers | set at server start |
| L46 | The WAL buffers are written out at every transaction commit, so very large values rarely help | S3 wal_buffers | — |
| L47 | XLogInsertRecord reserves space with a single spinlock-protected byte-position increment, then copies the record into the buffers under one of NUM_XLOGINSERT_LOCKS = 8 insertion locks so inserts proceed in parallel | S41 | REL_16_2 |
| L48 | When an inserter needs a WAL buffer that still holds unwritten data it must write that buffer itself and increments wal_buffers_full, which pg_stat_wal reports | S41 AdvanceXLInsertBuffer; S18/S19 pg_stat_wal | 14+ for the column |
| L49 | XLogFlush writes and fsyncs any additional WAL already in the buffers to piggyback as much as possible on each expensive fsync | S41 XLogFlush | — |
| L50 | With synchronous_commit on (the default), RecordTransactionCommit calls XLogFlush up to the commit record before returning success; with off it only records the LSN for the WAL writer, and the maximum delay is three times wal_writer_delay | S43; S3 synchronous_commit | — |
| L51 | wal_writer_delay defaults to 200 ms | S3 | — |
| L52 | full_page_writes is on by default: the first modification of a page after a checkpoint writes the whole page into WAL, guarding against torn pages | S3 full_page_writes; S42 | — |
| L53 | The canonical WAL-logged change is: pin and exclusive-lock the buffer, START_CRIT_SECTION, modify the page, MarkBufferDirty, XLogInsert, PageSetLSN with the returned pointer, END_CRIT_SECTION, unlock | S42 "Write-Ahead Log Coding"; S40 heap_update | — |
| L54 | FlushBuffer calls XLogFlush up to the page's LSN before smgrwrite for permanent buffers; the code calls this the basic rule that log updates hit disk before the data changes they describe | S38 FlushBuffer | BM_PERMANENT buffers |
| L55 | After a crash a transaction without a flushed commit record is simply presumed aborted; there is no undo pass | S42 "Asynchronous Commit" | — |
| L56 | ARIES defines the WAL protocol (log records on stable storage before the data they describe), prescribes an LSN on every page, and has the buffer manager force the log up to a dirty page's LSN before writing it | S64 §1.1, §2 | ARIES 1992 |
| L57 | PostgreSQL takes page LSNs and redo-first recovery from ARIES but has no undo pass or compensation records: aborted tuples are left for MVCC and VACUUM | S64; S42 | — |
| L58 | A checkpoint flushes every dirty page in shared buffers and writes a checkpoint record; checkpoints run every checkpoint_timeout (5 min) or when max_wal_size (1 GB) is about to be exceeded | S4; S3 | defaults |
| L59 | Checkpoints are expensive for two reasons: writing all dirty buffers, and the extra WAL from full-page writes afterwards | S4 | full_page_writes on |
| L60 | checkpoint_completion_target defaults to 0.9 (raised from 0.5 in PostgreSQL 14) | S3; S29 | 14+ |
| L61 | Since 9.6 the checkpointer sorts dirty buffers by tablespace, relation, fork and block before writing them | S54; S27 | 9.6+ |
| L62 | The background writer runs every bgwriter_delay (200 ms), writes at most bgwriter_lru_maxpages (100) per round, and only writes buffers that are dirty, unpinned and have usage count 0, scanning ahead of the clock hand without moving it | S1 bgwriter; S35 "Background Writer's Processing"; S38 SyncOneBuffer | defaults |
| L63 | Every buffer write, whoever performs it, goes through FlushBuffer; pg_stat_io splits writes by backend type (checkpointer, background writer, client backend, autovacuum worker) | S38; S18 | 16+ |
| L64 | work_mem defaults to 4 MB and caps one sort or hash operation before it spills; a query may run several such operations at once and sessions run concurrently, so total memory can be many times work_mem | S1 work_mem | — |
| L65 | hash_mem_multiplier defaults to 2.0 and the hash budget is work_mem × hash_mem_multiplier; it was introduced in 13 with default 1.0 and raised to 2.0 in 15 | S1; S55; S30; S48 | — |
| L66 | Since PostgreSQL 13 a hash aggregate spills to disk when its table exceeds the hash budget; before 13 it stayed in memory however large it grew | S28 | 13+ |
| L67 | maintenance_work_mem defaults to 64 MB and bounds VACUUM, CREATE INDEX and ALTER TABLE ADD FOREIGN KEY; with autovacuum, up to autovacuum_max_workers times that may be in use | S1 maintenance_work_mem | — |
| L68 | In 16 VACUUM could use at most 1 GB for dead-tuple identifiers whatever maintenance_work_mem said (MaxAllocSize cap on one array); 17 replaced the array with a radix-tree TidStore and removed the limit | S1; S71; S56; S32 | 16 vs 17+ |
| L69 | temp_buffers defaults to 8 MB of session-local buffers for temporary tables and can be changed only before the session first uses a temp table | S1 temp_buffers | — |
| L70 | A tuplesort's budget is Max(work_mem, 64) × 1024 bytes; EXPLAIN reports "Sort Method: quicksort Memory: NkB" or "external merge Disk: NkB" | S47 tuplesort_begin_common; S68 | — |
| L71 | A SortTuple is 24 bytes (pointer, first-key Datum, null flag, tape number), held in an array that grows by doubling | S47 tuplesort.h; S47 tuplesort.c | REL_16_2, 64-bit |
| L72 | In 16.2 tuplesort keeps the tuples themselves in a Generation context named "Caller tuples" and the SortTuple array in "TupleSort main"; 17 switched the tuples to a bump context | S47; S58 | — |
| L73 | palloc allocates from CurrentMemoryContext; MemoryContextSwitchTo changes it and returns the previous one | S45 "Background" | — |
| L74 | Freeing a context releases every chunk in it at once, which is how PostgreSQL reclaims all transient memory at transaction end, query end or per tuple without per-chunk bookkeeping; deleting a context deletes its children | S45 | — |
| L75 | TopMemoryContext is the root and is never reset; CacheMemoryContext holds the relcache and catcache permanently; MessageContext is reset at the top of each command cycle; TopTransactionContext is reset at end of each top-level transaction | S45 "Globally Known Contexts" | — |
| L76 | An AllocSet allocates blocks starting at 8 kB and doubling up to 8 MB (ALLOCSET_DEFAULT_SIZES), keeps 11 power-of-two freelists from 8 bytes, and gives any request over 8 kB its own malloc'd block | S46 | REL_16_2 and 18 |
| L77 | A normal palloc is limited to MaxAllocSize = 0x3fffffff bytes (1 GB − 1); only MemoryContextAllocHuge may exceed it | S46 memutils.h | — |
| L78 | PostgreSQL 16 cut the per-chunk header from 16 to 8 bytes; the low bits of the header identify the context type (3 bits in 16, widened to 4 in 17) | S57; S45 | 16 / 17+ |
| L79 | pg_backend_memory_contexts and pg_log_backend_memory_contexts() were added in 14; in 16 the view has nine columns with a 0-based level; 18 added type and path, removed parent, and made level 1-based | S29; S13; S14; S33; S70 | version-dependent |
| L80 | pg_log_backend_memory_contexts(pid) writes the target process's context tree to the server log and, for a parent with more than 100 children, logs the first 100 plus a summary | S15; S70 | — |
| L81 | Most of PostgreSQL's shared memory is an anonymous mmap region plus a tiny System V segment kept only as an interlock against a second postmaster on the same data directory | S9 §18.4.1; S49 | shared_memory_type = mmap (default on Linux) |
| L82 | huge_pages has values try (default), on and off; with try the server falls back to normal pages if MAP_HUGETLB fails; huge pages need shared_memory_type = mmap | S2 huge_pages; S49 | Linux |
| L83 | Since 15 the read-only shared_memory_size and shared_memory_size_in_huge_pages report the main area's size and the huge-page count, and 17 added the read-only huge_pages_status; the documented procedure is `postgres -C shared_memory_size_in_huge_pages` then vm.nr_hugepages | S10; S9 §18.4.5; S30; S32 | 15+ / 17+, Linux |
| L84 | pg_shmem_allocations (added in 13) lists every named allocation in the main segment with size and allocated_size; NULL name is unused memory and <anonymous> is untracked allocation; DSM is excluded | S12; S28 | 13+ |
| L85 | Shared structures are registered by name in the ShmemIndex hash table and shared memory is never freed once allocated | S72 shmem.c | main segment |
| L86 | Dynamic shared memory segments (posix shm_open by default on Linux) are created at run time, mainly for parallel query, and are removed when unmapped or at the next postmaster start; a DSA hands out size-class chunks and superblocks on top of them | S50; S2 dynamic_shared_memory_type | 9.4+ for DSM |
| L87 | The heavyweight lock table is sized for max_locks_per_transaction (default 64) × (MaxBackends + max_prepared_transactions) entries, where MaxBackends exceeds max_connections | S52 NLOCKENTS; S11 | — |
| L88 | Every backend has a PGPROC struct in shared memory, sized by MaxBackends plus auxiliary processes and prepared transactions | S52 proc.h | — |
| L89 | SLRU pools buffer transaction status (pg_xact), subtransactions, multixacts, commit timestamps, NOTIFY and serializable state; in 16.2 their sizes were compile-time (CLOG = Min(128, Max(4, NBuffers/512)) buffers, 32 subtrans, 8/16 multixact, 8 notify, 16 serial) | S51 | REL_16_2 |
| L90 | PostgreSQL 17 made SLRU sizes configurable (transaction_buffers etc., default 0 = shared_buffers/512 capped at 1024) and split each pool into 16-buffer banks with their own locks | S32; S2; S51 | 17+ |
| L91 | effective_cache_size defaults to 4 GB, is a planner estimate only, allocates nothing, and the docs say to count both shared_buffers and the kernel cache "though some data might exist in both places" | S8 | — |
| L92 | pg_stat_database.blks_hit counts only hits in PostgreSQL's own cache, so a "read" may still have come from the kernel page cache rather than disk | S18 pg_stat_database | — |
| L93 | The AIO README lists avoiding double buffering between the OS cache and shared_buffers as a motivation for direct I/O; debug_io_direct (16+) is a developer-only option that the docs say currently reduces performance | S67; S22; S31 | 16+/18 |
| L94 | PostgreSQL 18 added an asynchronous I/O subsystem (io_method worker/io_uring/sync, default worker; io_workers 3) used for relation reads, and raised effective_io_concurrency's default to 16 | S33; S2 | 18+ |
| L95 | pg_buffercache exposes one row per buffer (relfilenode, fork, block, isdirty, usagecount, pinning_backends); 16 added pg_buffercache_summary() and pg_buffercache_usage_counts(); 17 added pg_buffercache_evict(); 18 added evict_relation/evict_all and pg_buffercache_numa | S16; S31; S32; S33 | version-dependent |
| L96 | pg_prewarm in the default 'buffer' mode reads a relation's blocks into shared buffers (normal strategy); 'read' mode fills only the OS cache | S17 | — |
| L97 | EXPLAIN (BUFFERS) reports shared/local/temp blocks hit, read, dirtied and written; in 16 BUFFERS is off by default, and from 18 it is on automatically with ANALYZE | S20; S21; S33 | — |
| L98 | pg_stat_io was added in 16 with one row per backend type, object and context; 18 replaced op_bytes with byte columns and added WAL rows; 17 moved checkpoint counters from pg_stat_bgwriter to pg_stat_checkpointer | S31; S33; S32; S19 | — |
| L99 | The 1986 Design paper chose a process-per-user model over a server model "after much soul searching", citing limited programming resources; the 1990 paper calls it an expedient and describes an 8 K-page buffer manager with a modified LRU policy | S65 §5.1; S66 §5.2, §5.3 | Berkeley POSTGRES |
| L100 | Implementation of Berkeley POSTGRES began in 1986; Postgres95 followed the 1994 SQL work; PostgreSQL 6.0 was released 1997-01-29 | S23; S34 | — |
| L101 | As of 2026-09-17 the current minors are 18.6, 17.11 and 16.15 (2026-08-13); 18.0 was released 2025-09-25, 17.0 on 2024-09-26, 16.0 on 2023-09-14; 19 is at Beta 3 and planned for September 2026; 16.2 was released 2024-02-08 | S34 | as of the access date |
| L103 | On the lab server (16.2, defaults) the main shared memory area is 57 named allocations totalling 143 MB: Buffer Blocks 128 MB, Buffer Descriptors 1,048,576 bytes (16,384 × 64), XLOG Ctl 4,208,256 bytes, and 15 MB of everything else | S68 §2 | PostgreSQL 16.2, default postgresql.conf |
| L104 | In the lab, `orders` has 7,693 pages (60 MB, 130 rows/page) and `customers` 710 pages (5,680 kB, 141 rows/page, fillfactor 90); NBuffers/4 is 4,096 pages (32 MB) | S68 §3 | lab schema |
| L105 | A cold single-process scan of `orders` read all 7,693 pages from disk in 198 ms, left the whole file resident in the kernel cache and only 32 pages in shared buffers; a rescan hit 32 and read 7,661 in 182 ms; the default parallel plan (leader + 2 workers) hit 64, read 7,629 in 64 ms, and left 3 × 32 more ring buffers behind (160 in total) | S68 §4 | lab machine, NVMe, kernel cache dropped with fadvise |
| L106 | pg_stat_io for the cold scan showed bulkread reads 7,693 and reuses 7,661 = 7,693 − 32 | S68 §4 | — |
| L107 | `customers` (710 pages) read cold in 31 ms and rescanned entirely from shared buffers (hit=710) in 17 ms; a point lookup by primary key was hit=1 read=2 the first time and hit=3 the second | S68 §5 | — |
| L108 | After five scans every `customers` page sat at usage count 5, the index pages at 2–5, and every `orders` ring page at 1; pool-wide, 14,956 of 16,384 buffers were still at usage count 0 | S68 §6 | — |
| L109 | Prewarming `orders` (7,693 pages) fit entirely; prewarming a 15,424-page copy on top forced 10,048 evictions, after which 320 pages of `orders` survived, all 710 of `customers` and all 275 index pages survived, and 14,861 pages of the copy were resident; the usage-count histogram went from 883 buffers at 5 to 134 | S68 §7 | — |
| L110 | CREATE TABLE AS left about 2,080 pages of the new 15,424-page table in shared buffers, the footprint of its 16 MB bulk-write ring | S68 §7 | — |
| L111 | Sorting 1,000,000 rows with work_mem 4 MB ran as an external merge using 40,464 kB of temp files (temp written=10,135 blocks) in 662 ms; with 256 MB it was an in-memory quicksort using 81,868 kB in 493 ms | S68 §8 | one process |
| L112 | With work_mem 1 MB the parallel aggregate gave the leader and each of two workers their own 2,065 kB hash table (9 batches each) and their own external sort | S68 §8 | — |
| L113 | Grouping 1,000,000 rows into 100,000 groups spilled at the defaults (4 MB × 2.0: 5 batches, 8,241 kB memory, 7,248 kB disk) and fit in one batch at 12,561 kB with hash_mem_multiplier 4.0 | S68 §9 | — |
| L114 | A temp copy of `orders` was read through the 8 MB local buffer pool (local read=7,744) and a rescan still showed local reads because the table is larger than temp_buffers | S68 §10 | — |
| L115 | Right after a checkpoint, a one-column update of one row wrote 7,544 bytes of WAL: a HOT_UPDATE record of 7,473 bytes carrying a 7,408-byte full-page image (the 784-byte free-space hole omitted) plus a 34-byte COMMIT; the identical second update wrote 176 bytes (PRUNE 59, HOT_UPDATE 70, COMMIT 34) | S68 §11 | customers block 30, fillfactor 90 |
| L116 | After the updates the page's pd_lsn (0/4E578B78) equalled the start of the final COMMIT record, i.e. the end of the last record that touched the page; its buffer was dirty in pg_buffercache with usage count 5, and a CHECKPOINT left it resident but clean | S68 §11 | — |
| L117 | An idle backend held 118 contexts totalling 1,298 kB; with a 256 MB sort held open in a cursor, "TupleSort main" was 25,174,064 bytes and "Caller tuples" 58,720,256 bytes in 17 blocks (1,000,000 chunks), grand total 85,132,832 bytes; the process RSS went 12 MB → 97 MB → 18 MB after CLOSE | S68 §12 | — |
| L118 | shared_memory_size was 143 MB and shared_memory_size_in_huge_pages 72; the machine had HugePages_Total 0 so huge_pages = try fell back to 4 kB pages | S68 §13 | lab machine |
| L119 | Loading the two tables (1,100,000 rows) generated 1,208,928 WAL records and 101,178,572 WAL bytes, and the default 4 MB of WAL buffers overflowed 8,919 times (wal_buffers_full), each time forcing the loading backend to write WAL itself | S68 §3 | pg_stat_wal reset before the load |
| L120 | Over the whole lab run pg_stat_database reported a 93.5% buffer hit ratio (2,102,354 hits, 146,867 reads) | S68 §15 | — |
| L121 | 1 GB minus 1 byte (MaxAllocSize) is also the single-allocation ceiling that capped the pre-17 dead-tuple array | S46; S71 | — |
| L122 | Synchronized sequential scans (8.3+, synchronize_seqscans on by default) let a scan of a large table start where another scan is, which can change row order without ORDER BY | S74; S35 | 8.3+ |

## Open questions

- Effelsberg & Härder, "Principles of Database Buffer Management" (TODS 1984), the classic statement of why a DBMS buffer manager differs from OS paging, could not be fetched (ACM and ResearchGate return 403). It is not cited; the post makes the point from the PostgreSQL README instead.
- The exact `sizeof(BufferDesc)` before padding was not measured by compiling; the post states only the padded 64-byte stride, which the lab confirms (1,048,576 / 16,384).
- Whether the 96-vs-64 shared-buffer count after the parallel scan includes buffers left by earlier scans depends on free-list state; the post explains the 160 total as 32 + 32 + 96 and labels it as observed, not derived.
- The docs' "typically 48 bytes" for the System V segment does not match a hand count of PGShmemHeader on x86-64 (56); the post says "a few dozen bytes".
- PG 19 will remove the free list (commit 2c789405 on master); the post says "through 18" wherever the free list matters.
