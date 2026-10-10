# Source ledger — postgresql-foundations-storage-layer

Research ran 2026-09-24. Every server-side number comes from one run of `lab/run_lab.py`
(PostgreSQL 16.2, default `postgresql.conf`, captured in `lab/captures.md` and
`lab/captures.json`, run 2026-09-24T06:51:39Z). Documentation claims were checked against the
PostgreSQL 16 documentation, using the `REL_16_2` SGML sources in the release tarball (the same
text as the web pages cited). Source-code claims were checked against the `postgresql-16.2`
release tarball and name the file and symbol. Paper claims were checked against the full text,
except where the Condition column says the abstract was all that could be read.

Three findings from the lab corrected the plan's own assumptions. They are recorded as claims,
not hidden:
- The first `status` update was **not** HOT. Page 32 had 24 bytes free.
- The first vacuum **bypassed** index cleanup, and left page 32 not-all-visible.
- In an early run the dirty page was written out *before* the simulated crash. The cause was a
  sequential scan the lab ran after the update, which drove the clock sweep. The final lab
  removes that scan and proves the page is still dirty with `pg_buffercache`.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Stonebraker, M. "The Design of the POSTGRES Storage System" | Proc. 13th VLDB, Brighton | 1987 | VLDB '87 pp. 289–300 | peer-reviewed | https://www.vldb.org/conf/1987/P289.PDF | 2026-09-24 |
| S2 | T1 | Stonebraker, M., Rowe, L. A., Hirohama, M. "The Implementation of POSTGRES" (read in its UCB/ERL M90/34 report form) | IEEE TKDE 2(1) | 1990 | 10.1109/69.50912 | peer-reviewed | https://dsf.berkeley.edu/papers/ERL-M90-34.pdf | 2026-09-24 |
| S3 | T1 | Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H., Schwarz, P. "ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging" | ACM TODS 17(1) | 1992 | 10.1145/128765.128770 | peer-reviewed | https://cs.stanford.edu/people/chrismre/cs345/rl/aries.pdf | 2026-09-24 |
| S4 | T1 | Lehman, P. L., Yao, S. B. "Efficient Locking for Concurrent Operations on B-Trees" | ACM TODS 6(4) | 1981 | 10.1145/319628.319663 | peer-reviewed | https://www.csd.uoc.gr/~hy460/pdf/p650-lehman.pdf | 2026-09-24 |
| S5 | T1 | Comer, D. "The Ubiquitous B-Tree" | ACM Computing Surveys 11(2) | 1979 | 10.1145/356770.356776 | peer-reviewed | https://carlosproal.com/ir/papers/p121-comer.pdf | 2026-09-24 |
| S6 | T1 | Bayer, R., McCreight, E. "Organization and Maintenance of Large Ordered Indexes" (read in its 1970 Boeing report form) | Acta Informatica 1(3) | 1972 | 10.1007/BF00288683 | peer-reviewed | https://infolab.usc.edu/csci585/Spring2010/den_ar/indexing.pdf | 2026-09-24 |
| S7 | T1 | Wu, Y., Arulraj, J., Lin, J., Xian, R., Pavlo, A. "An Empirical Evaluation of In-Memory Multi-Version Concurrency Control" | PVLDB 10(7) | 2017 | 10.14778/3067421.3067427 | peer-reviewed | https://www.vldb.org/pvldb/vol10/p781-Wu.pdf | 2026-09-24 |
| S8 | T1 | Ziv, J., Lempel, A. "A Universal Algorithm for Sequential Data Compression" | IEEE Trans. Information Theory 23(3) | 1977 | 10.1109/TIT.1977.1055714 | peer-reviewed | https://courses.cs.duke.edu/spring03/cps296.5/papers/ziv_lempel_1977_universal_algorithm.pdf | 2026-09-24 |
| S9 | T1 | RFC 3720, Internet Small Computer Systems Interface (iSCSI), §12.1 and Appendix B.4 (CRC32C) | IETF | 2004 | RFC 3720 | standard | https://www.rfc-editor.org/rfc/rfc3720.txt | 2026-09-24 |
| S10 | T1 | IEEE Std 1003.1-2017 (POSIX), `fsync()` | IEEE / The Open Group | 2017 | IEEE Std 1003.1-2017 | standard | https://pubs.opengroup.org/onlinepubs/9699919799/functions/fsync.html | 2026-09-24 |
| S11 | T2 | PostgreSQL 16 docs, §73.1 Database File Layout | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/storage-file-layout.html | 2026-09-24 |
| S12 | T2 | PostgreSQL 16 docs, §73.2 TOAST | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/storage-toast.html | 2026-09-24 |
| S13 | T2 | PostgreSQL 16 docs, §73.3 Free Space Map | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/storage-fsm.html | 2026-09-24 |
| S14 | T2 | PostgreSQL 16 docs, §73.4 Visibility Map | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/storage-vm.html | 2026-09-24 |
| S15 | T2 | PostgreSQL 16 docs, §73.6 Database Page Layout (PageHeaderData, HeapTupleHeaderData) | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/storage-page-layout.html | 2026-09-24 |
| S16 | T2 | PostgreSQL 16 docs, §73.7 Heap-Only Tuples (HOT) | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/storage-hot.html | 2026-09-24 |
| S17 | T2 | PostgreSQL 16 docs, ch. 30 Reliability and the Write-Ahead Log (§30.2 Data Checksums, §30.3 WAL, §30.6 WAL Internals) | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/wal-internals.html | 2026-09-24 |
| S18 | T2 | PostgreSQL 16 docs, §26.3 Continuous Archiving and Point-in-Time Recovery | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/continuous-archiving.html | 2026-09-24 |
| S19 | T2 | PostgreSQL 16 docs, §27.2 Log-Shipping Standby Servers (streaming replication; walsender/walreceiver; startup process) | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/warm-standby.html | 2026-09-24 |
| S20 | T2 | PostgreSQL 16 docs, §67.4 B-Tree Implementation (deduplication) | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/btree-implementation.html | 2026-09-24 |
| S21 | T2 | PostgreSQL 16 docs, ALTER TABLE (Notes: ADD COLUMN and table rewrites) | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/sql-altertable.html | 2026-09-24 |
| S22 | T2 | PostgreSQL 16 docs, F.25 pageinspect; F.29 pg_freespacemap; F.33 pg_visibility; F.35 pg_walinspect | — | 2024 | — | official-docs | https://www.postgresql.org/docs/16/pageinspect.html | 2026-09-24 |
| S23 | T2 | PostgreSQL release notes: 7.1 (2001-04-13), 8.3, 8.4, 9.2 (2012-09-10), 9.3, 9.6, 10, 11, 13 (2020-09-24), 14, 15 (2022-10-13), 17, 18 (2025-09-25) | — | 2025 | — | official-docs | https://www.postgresql.org/docs/release/ | 2026-09-24 |
| S24 | T3 | `src/include/storage/bufpage.h`, REL_16_2 (`PageHeaderData`, `PD_ALL_VISIBLE`, `PG_PAGE_LAYOUT_VERSION`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/include/storage/bufpage.h | 2026-09-24 |
| S25 | T3 | `src/include/storage/itemid.h`, REL_16_2 (`ItemIdData`, `LP_*`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/include/storage/itemid.h | 2026-09-24 |
| S26 | T3 | `src/include/access/htup_details.h`, REL_16_2 (infomask bits, `HEAP_NATTS_MASK`, `HEAP_HOT_UPDATED`, `HEAP_ONLY_TUPLE`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/include/access/htup_details.h | 2026-09-24 |
| S27 | T3 | `src/backend/access/heap/README.HOT`, REL_16_2 | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/README.HOT | 2026-09-24 |
| S28 | T3 | `src/backend/access/heap/pruneheap.c`, REL_16_2 (`heap_page_prune_opt`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/pruneheap.c | 2026-09-24 |
| S29 | T3 | `src/backend/access/heap/heapam.c`, REL_16_2 (`heap_update`, `log_heap_update`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/heapam.c | 2026-09-24 |
| S30 | T3 | `src/backend/access/heap/vacuumlazy.c`, REL_16_2 (`SKIP_PAGES_THRESHOLD`, `BYPASS_THRESHOLD_PAGES`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/vacuumlazy.c | 2026-09-24 |
| S31 | T3 | `src/backend/access/heap/heapam_visibility.c`, REL_16_2 (file header; `HeapTupleSatisfiesMVCC`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/heapam_visibility.c | 2026-09-24 |
| S32 | T3 | `src/backend/access/transam/clog.c`, REL_16_2 (`CLOG_BITS_PER_XACT`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/transam/clog.c | 2026-09-24 |
| S33 | T3 | `src/backend/storage/freespace/README`, `freespace.c`, `src/include/storage/fsm_internals.h`, REL_16_2 | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/storage/freespace/README | 2026-09-24 |
| S34 | T3 | `src/include/access/heaptoast.h`, `src/include/varatt.h`, `src/common/pg_lzcompress.c`, REL_16_2 | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/include/access/heaptoast.h | 2026-09-24 |
| S35 | T3 | `src/backend/access/nbtree/README`, `nbtsplitloc.c`, `src/include/access/nbtree.h`, REL_16_2 | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/nbtree/README | 2026-09-24 |
| S36 | T3 | `src/include/access/xlog_internal.h`, `src/include/access/xlogrecord.h`, REL_16_2 (`XLogFileName`, `XLogPageHeaderData`, `XLogRecord`, `XLOG_PAGE_MAGIC`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/include/access/xlog_internal.h | 2026-09-24 |
| S37 | T3 | `src/backend/access/transam/xlogutils.c` (`XLogReadBufferForRedoExtended`) and `xlog.c` (`StartupXLOG`, `SyncDataDirectory`), REL_16_2 | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/transam/xlogutils.c | 2026-09-24 |
| S38 | T3 | `src/port/pg_crc32c_sb8.c`, REL_16_2 (Castagnoli polynomial) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/port/pg_crc32c_sb8.c | 2026-09-24 |
| S29b | T3 | `src/backend/access/heap/hio.c`, REL_16_2 (`RelationAddBlocks`, `MAX_BUFFERS_TO_EXTEND_BY`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/hio.c | 2026-09-24 |
| S41 | T3 | `src/backend/access/heap/visibilitymap.c`, REL_16_2 (`MAPSIZE`, `HEAPBLOCKS_PER_PAGE`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/heap/visibilitymap.c | 2026-09-24 |
| S42 | T3 | `src/backend/access/transam/xlogreader.c`, REL_16_2 (`XLogReaderValidatePageHeader`, `ValidXLogRecordHeader`, `ValidXLogRecord`) | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/backend/access/transam/xlogreader.c | 2026-09-24 |
| S43 | T3 | `src/include/access/rmgrlist.h`, REL_16_2 | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/src/include/access/rmgrlist.h | 2026-09-24 |
| S44 | T3 | `contrib/pageinspect/pageinspect--1.11--1.12.sql` and `pageinspect.control`, REL_16_2 | — | 2024 | — | source | https://github.com/postgres/postgres/blob/REL_16_2/contrib/pageinspect/pageinspect--1.11--1.12.sql | 2026-09-24 |
| S39 | T3 | This post's lab: `lab/run_lab.py`, captures of 2026-09-24 | — | 2026 | lab/captures.md | source | (downloadable lab) | 2026-09-24 |
| S40 | T4 | Klitzke, E. "Why Uber Engineering Switched from Postgres to MySQL", Uber blog | — | 2016 | — | practitioner | https://www.uber.com/blog/postgres-to-mysql-migration/ | 2026-09-24 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | Semantic Scholar | API search "b-tree survey", "database recovery principles survey", "multiversion concurrency control evaluation version storage", "design of the POSTGRES storage system" | HTTP 429 on every attempt, by curl and by WebFetch, including retries 20–60 s apart; no records. Not counted toward the sweep |
| 2 | 1 | DBLP | publ API: "Ubiquitous B-Tree Comer", "Efficient Locking for Concurrent Operations on B-Trees", eight more titles | An anti-bot challenge page (Anubis) for curl and WebFetch alike; no records. Venues were confirmed at Crossref and on the papers' own title pages instead. Not counted |
| 3 | 1 | Crossref | "Lehman Yao Efficient locking for concurrent operations on B-trees 1981" | TODS 1981, 10.1145/319628.319663, 378 citing works |
| 4 | 1 | Crossref | "Comer The Ubiquitous B-Tree Computing Surveys 1979" | ACM Computing Surveys 1979, 10.1145/356770.356776; the survey to read first on B-tree variants |
| 5 | 1 | Crossref | "Graefe Modern B-Tree Techniques" | FnT Databases 2011, 10.1561/1900000028, and its 2024 sequel; neither open access, so neither is read or cited |
| 6 | 1 | Crossref | "Mohan ARIES ... write-ahead logging" | TODS 1992, 10.1145/128765.128770; also ARIES/IM (SIGMOD Record 1992), which is not needed for a heap-only claim |
| 7 | 1 | Crossref | "Haerder Reuter Principles of transaction-oriented database recovery" | CSUR 1983, 10.1145/289.291; full text is blocked (ACM 403). ARIES's own definitions of steal/force, which credit it, are used instead |
| 8 | 1 | Crossref | "Stonebraker The design of the POSTGRES storage system" | DTIC report 10.21236/ADA187244. The VLDB '87 version was read from the VLDB Endowment's site (row 14) |
| 9 | 1 | Crossref | Wu et al. MVCC evaluation; Bernstein & Goodman 1983; Bayer & McCreight 1972; Lanin & Shasha 1986; Castagnoli 1993; Ziv & Lempel 1977; Stonebraker & Rowe 1986; Stonebraker et al. 1990; Graefe 2012 | DOIs for every one except Lanin & Shasha (FJCC 1986, not in Crossref; the nbtree README is cited for its use instead) |
| 10 | 1 | OpenAlex | title.search:b-tree + title.search:survey, sorted by citations | Graefe, *A survey of B-tree locking techniques* (TODS 2010, 10.1145/1806907.1806908) and *A survey of B-tree logging and recovery techniques* (TODS 2012, 10.1145/2109196.2109197). Neither could be fetched, so they are recorded here but not cited |
| 11 | 1 | OpenAlex | title.search:POSTGRES storage system | Stonebraker 1987 (255 citations) plus a 1992 ICDE follow-up on index recovery for the same storage system |
| 12 | 1 | OpenAlex | cites:W2108179552 (forward from Lehman & Yao), sorted by citations | 535 citing works, led by linearizability (TOPLAS 1990) and GiST (1995); nothing overturns the B-link invariant. Graefe's 2010 survey (row 10) is the modern restatement |
| 13 | 1 | OpenAlex | cites:W2104954161 (forward from ARIES), sorted by citations | 1,046 citing works, mostly persistent-memory logging (2009–2011) and "The End of an Architectural Era" (VLDB 2007); none describes PostgreSQL's redo-only recovery |
| 14 | 1 | VLDB Endowment proceedings | vldb.org/conf/1987 P289; pvldb vol. 10 p781 | Full text of Stonebraker 1987 and Wu et al. 2017; Wu's Table 1 classifies Postgres |
| 15 | 1 | arXiv | abs:"write-ahead log", by relevance | Eight preprints on WAL for NVM, LSM trees and Rust (2017–2025); none on PostgreSQL's WAL format; none cited |
| 16 | 1 | OpenAlex | OA locations for ten DOIs | Open copies listed only on dl.acm.org, which refuses curl and WebFetch; author or course copies were used for S3–S6 and S8 |
| 17 | 2 | PostgreSQL docs (local SGML, REL_16_2) | storage.sgml, wal.sgml, backup.sgml, btree.sgml, high-availability.sgml, ref/alter_table.sgml | Page, tuple, TOAST, FSM, VM, HOT, WAL internals, archiving, streaming, ADD COLUMN rules |
| 18 | 2 | PostgreSQL source (REL_16_2 tarball) | grep bufpage.h, itemid.h, htup_details.h, heaptoast.h, varatt.h, README.HOT, nbtree README, freespace README, xlog_internal.h, xlogrecord.h | Every constant in the post, with its definition |
| 19 | 3 | Our lab | run_lab.py on PostgreSQL 16.2 | Every server number; three runs (the second fixed the crash step, the third added the packed-page breakdown); every number in the post is from the third |
| 20 | 4 | Our reading | Stonebraker et al. 1990, §4.1–4.2 | The designers' own case against no-overwrite without stable memory; the vacuum "meltdown" |
| 21 | 4 | PostgreSQL release notes | 7.1, 8.3, 8.4, 9.2, 9.3, 9.6, 10, 11, 13, 14, 17, 18 | When WAL, TOAST, HOT, the VM, index-only scans, checksums, the all-frozen bit, dedup and the index-vacuum bypass arrived |
| 22 | 4 | Web search | Uber "postgres to mysql" write amplification | The 2016 practitioner report Wu et al. cite as industry evidence; framing only |
| 23 | 5 | PostgreSQL source | heapam.c `heap_update`, `log_heap_update`; xlogutils.c; xlog.c; heapam_visibility.c; vacuumlazy.c; pruneheap.c; nbtsplitloc.c | Why the lab saw LOCK records, prefix-compressed HOT records, the 2% bypass, 32-page skips and the 90% split |
| 24 | 6 | Web search | "Principles of transaction-oriented database recovery" pdf | ResearchGate and ACM only; nothing readable. Not cited |

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Lab: PostgreSQL 16.2, default config, 16 CPUs, 15 GB RAM, NVMe; `customers` 710 pages, `orders` 7,693 pages (1,000,000 rows), `orders_customer_idx` 1,157 pages, `orders_created_idx` 1,086 pages | S39 §0–1 | run 2026-09-24 |
| L02 | `orders` is `base/90977/91057`: main fork 63,021,056 bytes, `_fsm` 32,768 bytes, `_vm` 8,192 bytes; its TOAST table (91060) is 0 bytes and its TOAST index (91061) 1 page; `pg_wal` held 16 segments (256 MiB) | S39 §1 | OIDs are this run's |
| L03 | Row 4242 is at ctid (32,82). Page 32: pd_lsn 3/EB723BC0, checksum 0, flags 4, pd_lower 544, pd_upper 568, pd_special 8192, layout version 4; 130 line pointers and a 24-byte hole | S39 §2 | before any update |
| L04 | Row 4242's tuple is 53 bytes. Header: xmin 71477, xmax 0, ctid (32,82), infomask2 5, infomask 0x0902, t_hoff 24. Data: 4242, 92399, 56954, then 4 zero bytes, then created (820,545,042,000,000 µs after 2000-01-01), then 0x0b and `paid` | S39 §2 | decoded by run_lab.py |
| L05 | `orders` holds 130.0 rows per page and `customers` 140.8. With `created` moved first, the same rows fill 7,353 pages at up to 136 rows each; the copy is 7,360 pages because 7 bulk-extended pages at the end were never initialised | S39 §2 | CREATE TABLE AS |
| L06 | Before update 1, the FSM said only page 7692 had room (5,632 bytes). That page held 40 tuples (pd_lower 184, pd_upper 5848) | S39 §3 | — |
| L07 | Update 1 (xid 71484) was not HOT. The new version went to (7692,41). Its own WAL: LOCK 54 B on block 32, UPDATE 106 B on blocks 7692 and 32, INSERT_LEAF 64 B in each index, COMMIT 34 B; 322 bytes of records | S39 §3 | a catalog PRUNE with a page image in the same LSN window belongs to xid 0 and is excluded |
| L08 | Right after update 1, the new version's infomask lacked HEAP_XMIN_COMMITTED. After one reader it had it | S39 §3 | raw page reads do not set hint bits |
| L09 | A sequential scan pruned page 32: line pointer 82 became LP_DEAD with length 0; pd_upper went 568→624; PD_ALL_VISIBLE cleared; one 57-byte PRUNE record | S39 §3 | — |
| L10 | Update 2 (xid 71485) was HOT: HOT_UPDATE 77 B + COMMIT 34 B = 111 bytes of records. lp 41 got HEAP_HOT_UPDATED and ctid (7692,42); lp 42 got HEAP_ONLY_TUPLE; n_tup_upd 2, n_tup_hot_upd 1 | S39 §4 | no checkpoint between the updates |
| L11 | The HOT_UPDATE record starts at 3/F6D261D0, in `0000000100000003000000F6` at offset 13,787,600 (WAL page 1683, byte 464). Header: tot_len 77, xid 71485, prev 3/F6D26190, info 0x40, rmid 10, CRC cf8032b2, which our own CRC-32C reproduces. Layout: 24 header + 20 block header + 2 data header + 17 block data + 14 main data | S39 §4 | read straight from the file |
| L12 | The 17 bytes of block data are a 2-byte prefix length (24, reused from the old tuple), the 5-byte tuple header, 1 pad byte and the 9-byte `refunded` | S39 §4; S29 `log_heap_update` | flags 0x20 = prefix from old |
| L13 | The segment starts with a long page header: magic 0xD113, timeline 1, pageaddr 3/F6000000, segment size 16,777,216, WAL block size 8,192, and the system identifier that pg_controldata reports | S39 §4 | — |
| L14 | Vacuum 1 scanned 2 of 7,693 pages (0.03%) and bypassed index cleanup (1 page, 1 dead item). The VM went from 7,691 to 7,692 all-visible pages; page 32 stayed not all-visible; lp 41 became LP_REDIRECT to 42; FSM for page 7692 went 5,632→5,568 | S39 §5 | — |
| L15 | VACUUM (INDEX_CLEANUP ON) made one index pass, with one parallel worker for index vacuuming, over both indexes (1,157 and 1,086 pages). lp 82 became LP_UNUSED; all 7,693 pages were all-visible; page 32's FSM entry became 64 | S39 §5 | — |
| L16 | The FSM of `orders` is 4 pages. The root and level-1 pages carry 174 down their leftmost path. Leaf page 0 holds category 2 at node 4127 (heap page 32); leaf page 1 holds 174 at node 7718 (heap page 7692). Page 7692's hole of 5,592 bytes is recorded as 5,568 | S39 §6 | after vacuum 2 |
| L17 | In an (int, text) row, 2,000-byte values stay inline (tuple 2,032 bytes). At 2,001 bytes, compressible text becomes 51 bytes of pglz inline, and incompressible text leaves the row: 46-byte tuple, 18-byte pointer | S39 §7 | md5-hex text for the incompressible kind |
| L18 | Compressible text of 10,000 bytes stores in 142 bytes. Out-of-line values take ⌈n/1,996⌉ chunks: 2 for 2,001–3,000, 3 for 4,000, 4 for 6,000, 5 for 8,000, 6 for 10,000 | S39 §7 | — |
| L19 | Updating only the int column of a row with an out-of-line value left every TOAST chunk in place and wrote 168 bytes of WAL | S39 §7 | — |
| L20 | `ALTER TABLE orders ADD COLUMN note text` kept relfilenode 82853 and 7,693 pages; untouched tuples still record 5 attributes | S39 §8 | — |
| L21 | Row 4242's 10,000-byte note was stored uncompressed, out of line, in 6 chunks (5 × 1,996 + 20). The tuple became 75 bytes, ending in the 18-byte pointer: rawsize 10,004, extsize 10,000, value 91083, TOAST relation 91060 | S39 §8 | — |
| L22 | The wide update logged a LOCK on block 7692, six TOAST inserts (four per TOAST page, then INSERT+INIT for page 1), a NEWROOT and six INSERT_LEAF records for the TOAST index, then a HOT_UPDATE of 86 B | S39 §8 | first TOAST value in this table |
| L23 | `customer_id = 92399` used an Index Scan: 10 rows, 13 shared buffer hits | S39 §9 | bitmap scans and parallelism turned off for clarity |
| L24 | The walk: metapage root 290, level 2. Root has 5 items (−∞, 24709, 49417, 74125, 98833) → block 860 (level 1, 285 items, high key 98833, downlink 92395) → leaf 1068 (89 items, 808 bytes free, high key 92482) | S39 §9 | — |
| L25 | The leaf holds two entries for 92399: a 72-byte posting-list tuple of 9 TIDs, and a 16-byte plain tuple for (7692,41). The heap end is lp 41 (redirect) → 42 → 43 | S39 §9 | — |
| L26 | The index has 1 root, 5 internal pages (1,154 items) and 1,150 leaves (101,150 items). 100,000 of the 100,001 leaf tuples are posting lists, holding 1,000,000 TIDs | S39 §9 | — |
| L27 | 407 ascending ints fill one leaf, leaving 8 bytes free. The 408th insert logged SPLIT_R (752 B) and NEWROOT (122 B). Left page: 366 keys + high key 367, 808 bytes free. Right page: 42 keys, 7,308 bytes free. New root at block 3 with 2 items | S39 §10 | — |
| L28 | A non-rightmost leaf of 367 items split after 41 more inserts into 204 and 205 items (4,068 and 4,048 bytes free) | S39 §10 | — |
| L29 | After the checkpoint, REDO was 3/F6D691A0 in `…00F6`. The update (xid 71539) logged LOCK 2,743 B, including a 2,684-byte page image with a 5,508-byte hole, then HOT_UPDATE 72 B and COMMIT 34 B | S39 §11 | — |
| L30 | Before the crash the buffer was dirty (usage count 5): pd_lsn 3/F6D69D50 in memory with pd_lower 200, against 3/F6D42F28 with pd_lower 196 in the table file. The file was unchanged while the server was down, and pg_control said "in production" | S39 §11 | stop -m immediate |
| L31 | Recovery logged: interrupted; not properly shut down; redo starts at 3/F6D691A0; invalid record length at 3/F6D69D78; redo done at 3/F6D69D50; an end-of-recovery checkpoint wrote 4 buffers; ready. The file then matched memory and amount_cents read 60000 | S39 §11 | ~1.5 s between the first two messages |
| L32 | With archiving on, an `archiver` process appeared. After pg_switch_wal, `0000000100000003000000F6` was archived (archived_count 1, a `.done` marker) | S39 §12 | reset afterwards |
| L33 | pg_receivewal made the postmaster fork a `walsender` in state `streaming`, and it wrote `0000000100000003000000F7` | S39 §13 | — |
| L34 | Index-only count of 100,000 rows: all-visible → 0 heap fetches, 118 buffers, 10.6 ms. After 20,000 updates (0 of 7,847 pages all-visible) → 102,000 heap fetches, 102,118 buffers, 113.1 ms. After vacuum → 0 fetches, 118 buffers, 9.5 ms | S39 §14 | forced index-only plan; times vary run to run |
| L35 | Tables and indexes are arrays of fixed-size pages, normally 8 kB; every page has five parts: header, item identifiers, free space, items, special space | S15 | default build |
| L36 | The page header is 24 bytes: pd_lsn (8, next byte after the last WAL record for this page), pd_checksum, pd_flags, pd_lower, pd_upper, pd_special, pd_pagesize_version, pd_prune_xid | S15; S24 | — |
| L37 | Page layout version 4 dates from PostgreSQL 8.3; PD_ALL_VISIBLE is flag 0x0004 | S15; S24 | — |
| L38 | An item identifier is 4 bytes: 15-bit offset, 2-bit flags (UNUSED, NORMAL, REDIRECT, DEAD), 15-bit length | S25 | — |
| L39 | A ctid is a block number plus an item-identifier index; identifiers never move until freed, so tuples can move within the page | S15 | — |
| L40 | A heap tuple header is 23 bytes, followed by an optional null bitmap; user data starts at t_hoff, a MAXALIGN multiple | S15; S26 | most machines |
| L41 | Infomask bits: HASVARWIDTH 0x0002, HASEXTERNAL 0x0004, XMIN_COMMITTED 0x0100, XMAX_COMMITTED 0x0400, XMAX_INVALID 0x0800, UPDATED 0x2000. Infomask2: natts mask 0x07FF, HOT_UPDATED 0x4000, HEAP_ONLY_TUPLE 0x8000 | S26 | — |
| L42 | Values with a 1-byte varlena header (under 127 bytes) are not aligned; 4-byte headers are; the low bits of the header mark short, compressed or external | S12 | little-endian |
| L43 | Relation files are named by relfilenode, with `_fsm` and `_vm` forks, split into 1 GB segments named `.1`, `.2`; TRUNCATE, REINDEX, CLUSTER and some ALTER TABLE forms change the filenode but keep the OID | S11 | default segment size |
| L44 | Readers set hint bits once they learn a transaction committed or aborted, and mark the buffer dirty as a hint | S31 | — |
| L45 | A version whose xmin is not committed and not running is treated as aborted or crashed and hinted invalid | S31 | — |
| L46 | The commit log (`pg_xact`) keeps 2 bits per transaction, for four states: in progress, committed, aborted, sub-committed | S32 (`clog.c`, `clog.h`) | — |
| L47 | `pg_clog` was renamed `pg_xact` and `pg_xlog` became `pg_wal` in PostgreSQL 10, because users had deleted them as inessential logs and lost data | S23 | 10.0 |
| L48 | HOT requires that no column referenced by any index changes, and that the old version's page has room for the new one | S16 | — |
| L49 | HOT needs no new index entries, and its old versions can be removed during normal operation, including SELECTs | S16 | — |
| L50 | Lowering fillfactor makes HOT likelier; without it HOT still happens as new versions migrate to pages with room | S16 | — |
| L51 | A HOT chain stays within one page. The index points at the root line pointer; once dead, the root becomes a redirect | S27 | — |
| L52 | "Indexed column" includes partial-index predicate columns, and the check compares binary representations | S27 | non-summarizing indexes |
| L53 | Pruning runs when a page is read, has a prune hint, and has less than max(fillfactor target, BLCKSZ/10) free — for 8 kB pages, under 819 bytes free at the default fillfactor | S27; S28 | — |
| L54 | HOT arrived in PostgreSQL 8.3 | S23 | 8.3.0 |
| L55 | heap_update logs a temporary LOCK on the old version whenever it must toast or the new version will not fit on the page | S29 | — |
| L56 | When old and new versions share a page, only the changed middle of the new tuple is logged; this is skipped when the page gets an image or wal_level is logical | S29 | — |
| L57 | The VM holds two bits per heap page (all-visible, all-frozen). It is conservative, set only by vacuum, cleared by any modification; indexes have none | S14 | — |
| L58 | The VM arrived in 8.4 so vacuum could skip pages; the all-frozen bit arrived in 9.6 so anti-wraparound vacuum could skip frozen pages | S23 | 8.4.0, 9.6.0 |
| L59 | Index-only scans arrived in 9.2 and skip the heap only for pages the VM marks all-visible | S23 | 9.2.0 |
| L60 | Vacuum skips all-visible pages only in runs of at least 32 | S30 | 16.x |
| L61 | Vacuum bypasses index vacuuming when under 2% of pages hold LP_DEAD items; introduced in 14 as INDEX_CLEANUP auto | S30; S23 | 14.0+ |
| L62 | The FSM stores one byte per page (1/256 of a page, so 32-byte steps at 8 kB) in a max-tree within and across pages; the root is block 0; three levels cover any table at 8 kB | S13; S33 | — |
| L63 | One FSM page holds 4,069 leaf slots: 8,192 − 24 − 4 = 8,164 nodes, of which 4,095 are non-leaf | S33 | derived from fsm_internals.h |
| L64 | The FSM is not WAL-logged; it corrects itself. Per-relation FSM forks date from 8.4, replacing a fixed-size shared-memory map sized by max_fsm_pages and max_fsm_relations | S33; S23 | — |
| L65 | A tuple cannot span pages; TOAST compresses and/or moves out of line any value that would make a row wider than TOAST_TUPLE_THRESHOLD, until the row fits under TOAST_TUPLE_TARGET | S12 | — |
| L66 | TOAST_TUPLE_THRESHOLD is MaximumBytesPerTuple(4): 2,032 bytes on 8 kB pages; TOAST_TUPLE_TARGET defaults to the same and is per-table adjustable | S34; S12 | 8 kB pages |
| L67 | Out-of-line chunks are at most TOAST_MAX_CHUNK_SIZE bytes, chosen so four fit on a page: 1,996 at 8 kB | S12; S34 | — |
| L68 | An on-disk TOAST pointer is always 18 bytes: header, tag, raw size, stored size plus method, value OID, TOAST table OID | S12; S34 | — |
| L69 | Storage strategies PLAIN, EXTENDED, EXTERNAL, MAIN; EXTENDED (compress, then move) is the default for most types | S12 | — |
| L70 | pglz skips inputs under 32 bytes, requires 25% savings, and gives up if the first 1 KB does not compress | S34 | default strategy |
| L71 | An UPDATE that leaves out-of-line values unchanged incurs no TOAST cost | S12 | — |
| L72 | LZ4 for TOAST arrived in 14; the default stays pglz | S23 | 14.0 |
| L73 | WAL and TOAST both arrived in 7.1 (2001-04-13); before, commits forced all data to disk and rows had an 8–32 KB limit | S23 | 7.1.0 |
| L74 | pglz is an LZ-family compressor; the family begins with Ziv and Lempel's 1977 universal sequential algorithm | S34; S8 | abstract only for S8 |
| L75 | nbtree implements Lehman & Yao: a right-link and a high key per page, so a search that finds its key above the high key moves right | S35; S4 | — |
| L76 | Lehman & Yao's link pointer removes read locks; PostgreSQL still takes page-level read locks because backends share buffers | S4; S35 | — |
| L77 | Non-leaf tuples and leaf high keys are pivot tuples; heap TID breaks ties so every key is unique; suffix truncation (Bayer & Unterauer) trims pivots | S35 | — |
| L78 | Deduplication merges duplicates into posting-list tuples, lazily, when a page would otherwise split; it arrived in 13 | S35; S20; S23 | 13.0 |
| L79 | A rightmost split leaves the left page leaf-fillfactor full (90% default); other splits equalize free space | S35 | — |
| L80 | A new root is installed by updating the metapage; the metapage is cached in the relcache | S35 | — |
| L81 | The B-tree was introduced by Bayer and McCreight (1970 report, 1972 paper), with log_k(I) search and at least 50% page utilization | S6 | — |
| L82 | By 1979 B-trees were the de facto standard index; in a B+-tree all keys live in the leaves | S5 | — |
| L83 | WAL: changes are logged before data files change; recovery rolls forward (REDO); one WAL flush can commit many transactions | S17 | — |
| L84 | An LSN is a byte offset into the WAL. Segments are 16 MB, divided into 8 kB pages; names start at 000000010000000000000001 and never wrap | S17 | default build |
| L85 | A segment file is named from timeline, segno / segments-per-4-GiB and segno mod segments-per-4-GiB, in hex | S36 | — |
| L86 | XLOG_PAGE_MAGIC is 0xD113 in 16; a record header holds total length, xid, prev pointer, info, resource manager id and CRC | S36 | 16.x |
| L87 | WAL records are protected by CRC-32C, the Castagnoli polynomial 0x1EDC6F41 that iSCSI also uses | S38; S9 | — |
| L88 | The WAL segment size became an initdb option in 11 | S23 | 11.0 |
| L89 | Recovery reads pg_control, then the checkpoint record, then redoes from its REDO location | S17 | — |
| L90 | Redo skips a block whose page LSN is at or past the record's LSN | S37 | — |
| L91 | After a crash, startup fsyncs the whole data directory before replaying; the fsync sits between the "interrupted" message and the "not properly shut down" message | S37 (`xlog.c` StartupXLOG, `xlogrecovery.c` InitWalRecovery) | — |
| L92 | ARIES recovers in three passes (analysis, redo that repeats history, undo of losers), redoing a record only if the page-LSN is lower, and logs compensation records during undo | S3 | — |
| L93 | Steal: dirty pages of uncommitted transactions may be written. No-force: commit does not wait for data pages | S3 | ARIES's definitions |
| L94 | archive_command runs with %p and %f and must exit 0 only on success; without archiving, old segments are recycled | S18 | — |
| L95 | On a standby, a walreceiver connects to a walsender on the primary, WAL streams as it is generated, and the startup process replays it | S19 | — |
| L96 | The 1987 design had no conventional WAL and no recovery code; it overwrote nothing; a vacuum cleaner daemon moved old records to archival storage; the log was 2 bits per transaction | S1 | — |
| L97 | The same paper pointed index entries at a line-table slot so records could move within a page, and skipped index maintenance when no indexed field changed | S1 | design, not a shipped feature |
| L98 | By 1990 its designers wrote that without stable memory, no-overwrite forces random writes at commit where a WAL writes sequentially, so it is guaranteed slower | S2 | their opinion |
| L99 | The 1990 paper praised no-overwrite for instant abort, since old records remain, and warned the vacuum cleaner could starve under load | S2 | — |
| L100 | Wu et al. classify Postgres MVCC as append-only (oldest-to-newest), vacuum GC, physical pointers | S7 | 2017 survey table |
| L101 | Physical pointers must insert into every secondary index on each new version; logical pointers had higher throughput on update-heavy workloads | S7 | in-memory testbed (Peloton), not PostgreSQL |
| L102 | Index-only scans need version information in the index or equivalent; PostgreSQL's substitute is the VM | S7; S14 | — |
| L103 | A 2016 Uber post blamed updates that rewrite every index for its move off Postgres | S40 | practitioner; framing only |
| L104 | Data checksums are off unless chosen at initdb (or enabled offline with pg_checksums); they arrived in 9.3; initdb enables them by default from 18 | S17; S23 | — |
| L105 | POSIX fsync() transfers all of a file's data to its storage device | S10 | device honesty is assumed |
| L106 | The docs warn that drives which falsely report writes defeat WAL | S17 | — |
| L107 | ADD COLUMN with no default, or a non-volatile default, needs no table rewrite; constant defaults stopped rewriting in 11 | S21; S23 | — |
| L108 | 17 adds WAL summarization and incremental backup; 18 adds B-tree skip scan | S23 | — |
| L109 | pageinspect, pg_visibility, pg_freespacemap and pg_walinspect are contrib modules that read pages and WAL directly | S22 | superuser |
| L110 | B-tree default leaf fillfactor 90, internal 70 | S35 | — |
| L111 | For bulk inserts, 16 extends a relation by several pages at once (up to 64) | S29b | `hio.c` `RelationAddBlocks` |
| L112 | In this run, update 2's record, the crash step's REDO point and replayed records, and the archived file are all in segment `0000000100000003000000F6` | S39 §4, §11, §12 | this run |
| L113 | Every heap and index relation except hash indexes has a free space map fork | S13 | — |
| L114 | TOASTed values are fetched only if the column is selected, when the result is sent to the client; the main table stays small enough to cache | S12 | — |
| L115 | If the page the FSM offers lacks room, the inserter records that page's real free space and asks for another; vacuum rewrites the FSM's bottom level as it scans | S33; S29b | — |
| L116 | One VM page maps (8,192 − 24) × 4 = 32,672 heap pages | S41 | 8 kB pages |
| L117 | Reading a segment, PostgreSQL rejects a long page header whose system identifier, segment size or WAL block size differs from the cluster's | S42 | — |
| L118 | A record is accepted only if its length is plausible, its prev-link matches the record before it and its CRC matches; the first failure is taken as the end of WAL | S42 | crash recovery |
| L119 | A new timeline begins whenever an archive recovery completes; the timeline id is part of every segment name so later WAL cannot overwrite the earlier history's files | S18 | — |
| L120 | Point-in-time recovery restores a physical backup and replays archived WAL up to the chosen moment | S17 (§30.3); S18 | — |
| L121 | Resource manager id 10 is Heap (0 XLOG, 1 Transaction, … 9 Heap2, 10 Heap, 11 Btree) | S43 | 16.x |
| L122 | While archive_command keeps failing, pg_wal keeps filling; if its file system fills, the server does a PANIC shutdown, losing no committed transaction but staying down | S18 | — |
| L123 | `bt_multi_page_stats` is new in pageinspect 1.12, which ships with 16 | S44 | — |
| L124 | pg_walinspect arrived in 15, giving SQL output similar to pg_waldump | S23 (15.0, 2022-10-13) | — |
| L125 | ALTER TABLE ... SET (storage parameter) does not modify existing table contents; a rewrite (VACUUM FULL, CLUSTER, a rewriting ALTER TABLE) applies it to old pages | S21 | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S4 | Fig. 3 (B*-tree node with high key) | B-tree / L75 | shows the high key | ACM copyright, no reuse licence found | https://doi.org/10.1145/319628.319663 | do not reuse; our FIG_16 draws the lab's real pages instead |
| F2 | S7 | Fig. 5 (logical vs physical pointers) | HOT / L101 | contrasts index schemes | PVLDB CC BY-NC-ND 4.0; site's non-commercial status not verified | https://www.vldb.org/pvldb/vol10/p781-Wu.pdf | do not reuse |
| F3 | S1 | none relevant | — | — | — | — | — |

## Open questions

- Whether the 1987 delta-record design was ever implemented in POSTGRES. The 1990 paper
  discusses the no-overwrite manager and the vacuum cleaner but not delta records. The post
  calls it a design proposal only.
- Recovery time for large WAL volumes. The lab replayed 2 kB. The post does not generalise
  replay speed.
- Whether pg_receivewal's walsender and a real standby's differ in anything but the client. The
  docs describe the standby case; the post says only that both read the same stream.
