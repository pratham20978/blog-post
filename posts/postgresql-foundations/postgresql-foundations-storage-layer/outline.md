# Outline — postgresql-foundations-storage-layer

**Series:** PostgreSQL Foundations, part 3 of 3 (memory layer → process layer → **storage layer**)
**Part 1:** *How PostgreSQL Uses Memory* — https://canery.in/blogs/postgresql-foundations-memory-layer
**Part 2:** *How PostgreSQL Uses Processes* — https://canery.in/blogs/postgresql-foundations-process-layer
**Tier:** L4 pillar · **Difficulty:** intermediate · **Budget:** ~11,200 words · **Figures:** 22 + cover
(above the 12–18 band on purpose, as in parts 1 and 2: seven promised topics, and every figure
carries a lab number or a byte offset)
**Title:** *How PostgreSQL Stores Data* · slug `postgresql-foundations-storage-layer`
**Audience:** engineers who run PostgreSQL and read `EXPLAIN`. Prereqs: SQL, reading `EXPLAIN`,
hexadecimal, and part 1's buffer/`pd_lsn`/full-page-image ideas (linked, not required).

**Thesis.** Everything PostgreSQL keeps on disk is one of three things: the data (heap pages,
index pages, TOAST chunks — all the same 8 KB page format), maps of the data (the visibility map
and the free space map, small enough to be wrong in only one safe direction), and a log of every
change to the data (WAL, whose byte position is stamped into each page it touches). Every
storage-layer surprise — an update that rewrites both indexes when no indexed column changed, a
vacuum that reads 2 of 7,693 pages, an index-only scan that still visits the heap, a 2,016-byte
value that leaves the row, a crash that loses nothing although the table file was never written
— is one of those three structures doing exactly what it was designed to do.

**Series framing (first 100 words after Insights).** Three layers: memory, process, storage.
Parts 1 and 2 are linked by URL; this part closes the series and names what it leaves out once.

**Must not re-teach** (link instead): the clock sweep and rings (part 1); the full-page image
(part 1 `#the-full-page-image`); WAL-before-data (part 1 `#when-a-dirty-page-may-leave-memory`);
vacuum's decide/do split and index passes (part 2 `#autovacuum-part-two-what-the-worker-actually-does`);
the checkpointer (part 2 `#the-checkpointer-making-the-wal-forgettable`); process roles.

**Out of scope, named once in Limitations:** streaming-replication configuration and failover,
logical decoding, GIN/GiST/BRIN/hash internals, table access methods other than heap.

---

| # | Section | Target | Job | Figures |
|---|---|---|---|---|
| 1 | `## Insights` (alert) | 120 | data + maps + log; each surprise is one of them doing its job | — |
| 2 | Who this is for + series paragraph + lab note + jump list | 200 | level, prereqs, time; three layers, this is layer three; lab setup | FIG_01 |
| 3 | `## Why this matters` | 350 | three incidents: every `status` update grows both indexes; index-only scan with 400k heap fetches; a crash, "automatic recovery in progress", and nothing lost | — |
| 4 | `## The problem` | 650 | fixed 8 KB pages the OS can tear; rows addressed stably while they move; old versions kept for MVCC; values bigger than a page; crash mid-write. The on-disk inventory of `orders` with real sizes | FIG_02 |
| 5 | `## Worked example` | 1,500 | row `id = 4242`: `ctid (32,82)` → header and tuple bytes → update 1 (not HOT, page full) → update 2 (HOT) → vacuum (2 of 7,693 pages) → a wide note (TOAST) → B-tree lookup (4 index pages) → WAL record by LSN in a named segment → immediate shutdown → replay | FIG_03 |
| 6 | `## Intuition` | 500 | data / maps / log; the ledger analogy (never erase, post a correcting entry) and where it breaks (vacuum erases; WAL is physical, not logical) | FIG_04 |
| 7 | `## The heap page, byte by byte` | 950 | page header fields decoded from hex; line pointers (15/2/15 bits); why the indirection exists; the tuple header, `t_hoff`, alignment padding, varlena headers; 130 tuples per page | FIG_05, FIG_06, FIG_07 |
| 8 | `## Who can see a row: xmin, xmax and the hint bits` | 550 | the three versions of row 4242 and their xids; infomask bits; hint bits set by readers; pg_xact; freezing in one paragraph, link to part 2 | FIG_08 |
| 9 | `## HOT: the update that skips the indexes` | 750 | two conditions; the chain; redirect and dead line pointers; pruning on read at <10% free; fillfactor; the lab's cost of each update in WAL records and index pages | FIG_09, FIG_10 |
| 10 | `## The visibility map, and why vacuum skips pages` | 650 | two bits per page; set only by vacuum, cleared by any change; the 32-page skip rule; index-only scans and Heap Fetches; the 2% index-cleanup bypass seen in the lab; all-frozen | FIG_11, FIG_12 |
| 11 | `## The free space map: where a new row lands` | 450 | one byte per page, 32-byte steps; three-level tree of max-heaps; why update 1 went to page 7692; not WAL-logged, self-correcting | FIG_13 |
| 12 | `## TOAST: when a value will not fit` | 750 | 2,032-byte threshold derived; four strategies; pglz's 25% rule; out-of-line chunks of 1,996 bytes; the 18-byte pointer decoded; lab bisection | FIG_14, FIG_15 |
| 13 | `## The B-tree: one lookup and one split` | 850 | metapage, root, internal, leaf; pivot tuples, high keys and right-links (Lehman & Yao); deduplication; the lookup's four pages; the split of a 407-key leaf and the 90% rightmost rule | FIG_16, FIG_17 |
| 14 | `## WAL: records, LSNs and segment files` | 800 | LSN as a byte address; segment name from an LSN; 8 KB WAL pages and their headers; the record header and CRC-32C; the update's records; `pg_waldump` | FIG_18, FIG_19 |
| 15 | `## Crash recovery, archiving and replicas: three readers of one log` | 850 | pg_control → redo point → replay; the page on disk before and after; `pd_lsn` makes redo idempotent; no undo, and how that differs from ARIES; archiving with `archive_command` and `pg_stat_archiver`; walsender, and the standby's startup process running the same redo | FIG_20, FIG_21 |
| 16 | `## The math` | 550 | tuples per page; TOAST threshold and chunk count; B-tree height from fanout; segment from LSN; FSM category and map coverage | — |
| 17 | `## Implementation` | 450 | the storage toolkit as SQL; which tool inspects which structure; 16 vs 17 vs 18 | FIG_22 |
| 18 | `## Limitations and common mistakes` | 450 | fillfactor 100 on update-heavy tables; indexing a status column; `VACUUM FULL` for bloat; `SELECT *` on TOASTed columns; archive_command that returns 0 on failure; checksums off; column order; what the series does not cover | — |
| 19 | `## Key takeaways` | 130 | 5 claims | — |
| 20 | `## Try it yourself` | 250 | 3 exercises with hidden answers | — |
| 21 | `## References` | 80 | lab downloads + sources | — |

**Total target:** ~11,200 words. If the draft passes ~12,000, section 13 shrinks to the one
walk and one split, per the plan's scope rule; no promised topic is dropped.

---

## Figure plan (route gate run per figure)

| ID | Section | Must communicate | Route | Why (the clause that settled it) |
|---|---|---|---|---|
| COVER | — | a single wide band of page tiles, one highlighted | placed | template cover in the series grid; title block at x=560 |
| FIG_01 | 2 | three layers, storage highlighted, parts 1–2 greyed | placed | Q5 — three stacked layers, the series' fixed opener |
| FIG_02 | 4 | every file `orders` owns, with its real size | placed | Q4 — containment with sizes to scale; not graph-shaped |
| FIG_03 | 5 | where row 4242 physically lives after each of eight steps | placed | Q4 — small multiples of one row's address over time |
| FIG_04 | 6 | data, maps, log: what points at what | placed | Q5 — seven nodes, no crossings, every edge a real pointer |
| FIG_05 | 7 | page 32 drawn to scale: header, 130 line pointers, 24-byte hole, tuples | placed | Q4 — byte layout to scale |
| FIG_06 | 7 | the 24 header bytes, hex decoded field by field | placed | Q4 — byte layout; field widths proportional |
| FIG_07 | 7 | row 4242's 53 bytes: header, padding, columns | placed | Q4 — byte layout; the padding is the lesson |
| FIG_08 | 8 | three versions' lifetimes in xid time; one visible per snapshot | placed | Q4 — spans on a shared time axis |
| FIG_09 | 9 | line pointers on pages 32 and 7692 across update, prune, vacuum | placed | Q4 — small multiples of real line-pointer states |
| FIG_10 | 9 | WAL records and bytes: non-HOT vs HOT update | chart | Q1 — measured pg_walinspect numbers |
| FIG_11 | 10 | VM bits for 7,693 pages before/after, and pages vacuum read | placed | Q4 — a grid of real values, not a chart of a quantity |
| FIG_12 | 10 | Heap Fetches of one index-only scan: dirty VM vs after vacuum | chart | Q1 — measured EXPLAIN numbers |
| FIG_13 | 11 | the four FSM pages of orders and the in-page max-heap path to 7692 | placed | Q5 — tree under nine nodes with real byte values |
| FIG_14 | 12 | value size → stored size, compressible vs not, threshold line | chart | Q1 — measured pg_column_size bisection |
| FIG_15 | 12 | the 18-byte TOAST pointer decoded and its chunk rows | placed | Q4 — byte layout plus a small table of real chunks |
| FIG_16 | 13 | the lookup: metapage → root → internal → leaf → heap, block numbers and key ranges | placed | Q5 — five pages in a line, every edge a real downlink |
| FIG_17 | 13 | a 407-key leaf before, 366+42 after, and the new root | placed | Q4 — key slots to scale, side by side (the taxonomy's worked decision) |
| FIG_18 | 14 | from LSN to file name, WAL page and byte offset | placed | Q4 — address decomposition drawn as a byte layout |
| FIG_19 | 14 | one WAL record's layout with the update's real lengths | placed | Q4 — byte layout to scale |
| FIG_20 | 15 | crash and replay in order: backend, WAL, data file, pg_control, startup process | mermaid | Q3 — five participants exchanging ordered messages |
| FIG_21 | 15 | three readers of one WAL stream: startup, archiver, walsender | placed | Q5 — eight nodes, no crossings, each edge labelled with what travels |
| FIG_22 | 17 | which tool inspects which structure | placed | Q4 — a grid of real tool × structure marks |

---

## Term map

| Term | First section | What | Why here | When it matters |
|---|---|---|---|---|
| page / block | Problem | the fixed 8 KB unit of every relation file | all storage is arrays of pages | sizing, I/O counting |
| relfilenode, fork, segment | Problem | a relation's file name; its main/_fsm/_vm files; 1 GB pieces | finding the bytes on disk | backups, disk forensics |
| WAL segment (vs 1 GB segment) | Problem | a 16 MB file in `pg_wal` | same word, different thing | reading `pg_wal`, archiving |
| TID / ctid | Worked example | (block, line pointer) address of a row version | how indexes point at rows | debugging, HOT |
| line pointer (item identifier) | Heap page | 4-byte slot: offset, flags, length | indirection lets tuples move | pruning, bloat |
| `pd_lsn` | Heap page | LSN of the last WAL record that changed the page | ties page to log | recovery (link to part 1) |
| LSN | Worked example | byte position in the WAL stream | addresses records and files | replication lag, recovery |
| tuple header, `t_hoff`, infomask | Heap page | 23-byte per-version header and its flag words | visibility and layout | any page inspection |
| MVCC, xmin, xmax | Visibility | versions stamped with creating/deleting xids | why updates make new rows | bloat, visibility |
| hint bits, pg_xact | Visibility | cached commit status in the tuple; the commit log | why reads dirty pages | write surprises after bulk load |
| freezing | Visibility | marking xmin as always-visible | wraparound (link part 2) | anti-wraparound vacuum |
| HOT, heap-only tuple, redirect | HOT | same-page update with no new index entries | cheap updates | update-heavy tables |
| pruning, LP_DEAD | HOT | page-local cleanup by any reader | space reclaimed without vacuum | bloat |
| fillfactor | HOT | fraction of a page filled on insert | leaves room for HOT | table design |
| visibility map, all-visible, all-frozen | VM | 2 bits per heap page | vacuum skipping, index-only scans | vacuum speed, IOS |
| index-only scan, Heap Fetches | VM | scan answered from the index alone | depends on VM bits | read performance |
| free space map | FSM | one byte per page in a max-tree | choosing where rows go | insert placement |
| TOAST, varlena, pglz, TOAST pointer, chunk | TOAST | oversized-attribute storage | values over ~2 KB | wide columns |
| B-tree, metapage, pivot tuple, high key, right-link | B-tree | Lehman & Yao B+tree pages | index lookups | index size, splits |
| deduplication, posting list | B-tree | one key with many TIDs in a tuple (13+) | smaller indexes | non-unique indexes |
| page split | B-tree | a full page divided in two | index growth | bloat, insert patterns |
| WAL record, resource manager, block reference | WAL | one logged change and its target pages | what recovery replays | pg_waldump |
| CRC-32C | WAL | record checksum | detects torn/garbage records | end of WAL |
| timeline | WAL | history id in the file name | file naming | PITR, failover |
| checkpoint, REDO point, pg_control | Recovery | where replay starts, stored in a control file | bounding recovery | crash recovery |
| startup process | Recovery | the process that replays WAL | crash recovery and standbys | recovery time |
| archiving, archive_command | Recovery | copying finished segments out | PITR | backups |
| walsender / walreceiver | Recovery | stream WAL to a standby | replicas read the same log | replication |
| pageinspect, pg_visibility, pg_freespacemap, pg_walinspect, pg_waldump | Worked example / Implementation | inspection tools | every capture | diagnosis |

---

## Padding test

After each section the reader can:

- Problem → list every file that makes up one table and say what each is for
- Worked example → follow one row through update, vacuum, TOAST, index lookup and crash
- Intuition → sort any on-disk structure into data, map or log, and say where the analogy breaks
- Heap page → decode a raw page header and a tuple from hex
- Visibility → say from xmin, xmax and infomask whether a version is visible
- HOT → predict whether an update will be HOT and what it costs if not
- VM → explain `2 scanned (0.03% of total)` and `Heap Fetches`
- FSM → say why a new version landed on the page it did
- TOAST → predict whether a value is inline, compressed, or out of line, and how many chunks
- B-tree → count the pages of a lookup and describe a split
- WAL → name the segment file from an LSN and read a pg_waldump line
- Recovery → say where replay starts, why it cannot double-apply, and who else reads the log
- Math → compute tuples per page, chunks, tree height, file name, FSM coverage
- Implementation → run the inspection toolkit on their own table

No two answers match. Sections 7–15 each own one structure or one reader of the log.
