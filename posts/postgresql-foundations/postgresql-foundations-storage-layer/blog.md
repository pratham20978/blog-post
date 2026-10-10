---
title: "How PostgreSQL Stores Data"
slug: postgresql-foundations-storage-layer
date: 2026-09-24
updated: 2026-09-24
summary: "PostgreSQL stores rows in 8 KB pages, maps them with a visibility map and a free space map, and logs every change to WAL. One real row, followed byte by byte."
tags: [databases, postgresql, write-ahead-log, mvcc, b-tree, storage-engine, internals]
category: databases
categories: [databases]
series: postgresql-foundations
series_position: 3
tier: L4
difficulty: intermediate
prerequisites: ["SQL and reading an EXPLAIN plan", "reading hexadecimal", "what a transaction is"]
reading_minutes: 55
cover_image_url: "COVER"
cover_image_alt: "A single wide band of small square tiles, one of them highlighted in tangerine, with a thin line of dots running beneath the band"
canonical_url: "https://canery.in/blogs/postgresql-foundations-storage-layer"
---

> [!NOTE]
> **Insights** — Everything PostgreSQL keeps on disk is one of three things. There is the *data*: heap pages, index pages and TOAST chunks, all in the same 8 KB page format. There are two *maps* of that data, the visibility map and the free space map, small enough to be checked before a page is touched. And there is a *log*, the write-ahead log, whose byte position is stamped into every page it changes. Almost every storage-layer surprise you will meet — an update that writes to both indexes although no indexed column changed, a vacuum that reads 2 pages of 7,693, an index-only scan that still visits the table 102,000 times, a crash that loses nothing although the table file never saw the change — is one of those three structures doing exactly what it was designed to do.

**Level:** intermediate · **You need:** SQL and the habit of reading `EXPLAIN`, enough hexadecimal to read `0x2C` as 44, and a PostgreSQL you are allowed to break · **Time:** ~55 min

PostgreSQL's architecture is usually described as three layers: a **memory layer** that caches pages and log records, a **process layer** of the postmaster and the workers it forks, and a **storage layer** of heap files, indexes and WAL segments on disk. [Part 1](https://canery.in/blogs/postgresql-foundations-memory-layer) was the memory layer and [part 2](https://canery.in/blogs/postgresql-foundations-process-layer) the process layer. This is the third and last post, and it stays on disk. It covers what a page holds, byte by byte; how a row finds its way back after it moves; what the two maps record; how a value bigger than a page is stored; and how a row, its index entry and its log record get back to a consistent state after a crash. Where it needs a memory fact, such as the full-page image or the rule that WAL reaches disk before the page it describes, it links to part 1. Where it needs to know who runs vacuum, it links to part 2. Figure 1 shows the three layers and where this post sits.

![Three horizontal layers labelled memory, process and storage, with the storage layer highlighted and annotated with heap pages, visibility map, free space map, TOAST, B-tree and WAL segments, and the upper two layers greyed as parts 1 and 2](FIG_01)

*Figure 1 — The three layers of a PostgreSQL server. Parts 1 and 2 covered the top two; this post is the bottom one.*

> [!TIP]
> **Runnable lab:** The runner, a README, the readable captures and the machine-readable captures are listed under [Lab downloads](#lab-downloads) at the end. Every concept and result is explained here; the lab is for reproducing them.

Every number in this post that came from a running server came from that lab, with the same setup as parts 1 and 2. That means PostgreSQL 16.2 with its default `postgresql.conf`, the same 1,000,000-row `orders` table (7,693 pages), the same 100,000-row `customers` table (710 pages) and part 2's two indexes on `orders`, on a laptop with 16 CPUs, 15 GB of RAM and an NVMe disk. <!-- L01 --> The lab follows one row of `orders` from insert to crash recovery. Transaction ids, log positions and file numbers are the ones that run produced; yours will differ, and nothing else should. Where 17 or 18 changed a constant or a default, the sentence says so.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [The heap page](#the-heap-page-byte-by-byte) · [Visibility](#who-can-see-a-row-xmin-xmax-and-the-hint-bits) · [HOT](#hot-the-update-that-skips-the-indexes) · [The visibility map](#the-visibility-map-and-why-vacuum-skips-pages) · [The free space map](#the-free-space-map-where-a-new-row-lands) · [TOAST](#toast-when-a-value-will-not-fit) · [The B-tree](#the-b-tree-one-lookup-and-one-split) · [WAL](#wal-records-lsns-and-segment-files) · [Recovery and its readers](#crash-recovery-archiving-and-replicas-three-readers-of-one-log) · [The math](#the-math) · [Implementation](#implementation) · [Limitations](#limitations-and-common-mistakes)

## Why this matters

A table of orders has a `status` column that changes three times in each order's life. Nothing on it is indexed except `customer_id` and `created`, yet the first status change of every row writes a new entry into both indexes, and `n_tup_hot_upd` in `pg_stat_user_tables` lags far behind `n_tup_upd`. The table was loaded with the default fill factor, which packs each page until no further row fits; the page holding the row in this post had 24 bytes left. The new version of the row cannot fit beside the old one, so it goes to another page, and an entry on another page needs new index entries to find it. <!-- L03 --> <!-- L07 -->

Or: a report counts rows with an index-only scan, meant to read only the index. Run just after a vacuum, it touches 118 buffers. Run after a batch job has updated one row in fifty, it touches 102,118, and `EXPLAIN` says `Heap Fetches: 102000`. The query did not change; a map of which pages are safe to skip did, and only vacuum puts it back. <!-- L34 -->

Or: the server is killed, and the next start prints `database system was not properly shut down; automatic recovery in progress`. The last committed update was never written to its table file, and it is there after the restart anyway. <!-- L30 --> <!-- L31 -->

Each of these is one on-disk structure doing its job. Once you can name the structure and read its bytes, the fix is usually one setting, and the log message stops being alarming.

## The problem

A database has to keep rows in files that the operating system reads and writes in fixed blocks. PostgreSQL's block, the **page**, is 8 KB by default. Every table and every index is an array of pages, and a row may be stored in any page of its table. <!-- L35 --> Six requirements make that harder than it sounds:

1. **Rows have variable length, pages do not.** A page must hold as many rows as fit, of any size, and pack new ones into whatever space is left.
2. **An index needs a stable address for each row**, even though the row may move within its page when the page is compacted.
3. **Old versions must stay.** PostgreSQL implements **multiversion concurrency control (MVCC)**: an `UPDATE` writes a new version of the row and leaves the old one, so that a transaction that started earlier still reads a consistent snapshot. Something must remember which version each transaction may see, and something must eventually remove the versions nobody can see.
4. **Some values are bigger than a page.** A row may not span pages, so a 10,000-byte value has to live somewhere else.
5. **New rows need somewhere to go**, found without reading the whole table to look for free space.
6. **A crash can happen between any two writes.** The disk does not promise to write 8 KB atomically, a committed transaction must survive, and forcing every changed page to disk at commit would turn every commit into scattered random writes. [Part 1](https://canery.in/blogs/postgresql-foundations-memory-layer#when-a-dirty-page-may-leave-memory) covered the memory side of this, the rule that no dirty page leaves memory before its log records.

PostgreSQL's answer is a small set of files per table, and Figure 2 draws the set that `orders` owns in the lab. The table itself is one file named after its **relfilenode**, the number in `pg_class.relfilenode`: `base/90977/91057`, where 90977 is the database's OID. The file is 63,021,056 bytes, or 7,693 pages. Beside it sit two **forks**, extra files that share the name with a suffix. `91057_fsm` is the free space map, 32,768 bytes. `91057_vm` is the visibility map, 8,192 bytes. <!-- L02 --> Each index is a file of its own. The table also has an empty **TOAST table** for oversized values, with a one-page index. A table or index larger than 1 GB is split into segment files named `.1`, `.2` and so on. The relfilenode usually matches the table's OID but need not: `TRUNCATE`, `REINDEX`, `CLUSTER` and some forms of `ALTER TABLE` give a table a new file while it keeps its OID. <!-- L43 --> Then there is the log. It is a directory, `pg_wal`, of 16 MB **WAL segment** files; in the lab it held 16 of them, 256 MiB. It is shared by every table in the cluster. <!-- L02 --> <!-- L84 -->

![Proportional bars for every file behind the orders table: the 63 MB heap file of 7,693 pages, its 32 KB free space map fork and 8 KB visibility map fork, a 9.5 MB and an 8.9 MB index, an empty TOAST table with a one-page index, and the pg_wal directory of 16 MB segments shared by the cluster](FIG_02)

*Figure 2 — What `orders` is on disk. The table is one 63 MB file. Its two maps together are 40 KB, 0.06% of it, which is why they can be read before any page is.*

Two different things are called a segment here, and they are easy to confuse. A relation's 1 GB segments are pieces of one table. A WAL segment is a 16 MB piece of the one log. The rest of this post means the second whenever it says "segment" alone.

## Worked example

The lab creates the two tables exactly as parts 1 and 2 did, then follows one row of `orders`, `id = 4242`, through eight steps. The server numbers below are captured output; the byte decodes are computed from the raw page. Figure 3 is the whole story on one strip, and each step below fills in one cell.

![Timeline strip of eight steps for row 4242: at (32,82) after the load; moved to (7692,41) by a non-HOT update that added two index entries; old version pruned to a dead line pointer; HOT update to (7692,42); vacuum turns 41 into a redirect; a 10,000-byte note adds version (7692,43) and six TOAST chunks; an index lookup walks pages 290, 860 and 1068 to TID (7692,41); a crash after update (7692,44) is replayed from WAL](FIG_03)

*Figure 3 — One row's physical life. Its logical identity never changes; its address changes four times, and the indexes learn about only the first move.*

### The row, and the page it lives on

Every row version has an address called its **ctid**: a page number and a slot number within that page. Row 4242 is at `(32,82)`, slot 82 of page 32. <!-- L03 -->

```sql
select ctid, * from orders where id = 4242;
```

```text
  ctid   |  id  | customer_id | amount_cents |        created         | status
---------+------+-------------+--------------+------------------------+--------
 (32,82) | 4242 |       92399 |        56954 | 2026-01-01 01:10:42+00 | paid
```

**`pageinspect`** is a contrib extension that copies a page out of the buffer pool as raw bytes and decodes it. It is how this post reads pages at all. <!-- L109 --> Its `page_header` function reads page 32's first 24 bytes: the log position of the last change to the page, 3/EB723BC0; a checksum of 0, because this cluster was created without data checksums; flag 4, meaning every row on the page is visible to everyone; and two offsets, 544 and 568, between which lie the page's only free bytes. <!-- L03 --> That is 24 bytes free. The page holds 130 rows, and there is no room for a 131st. The row itself is 53 bytes: a header that ends at byte 24, then the five column values, with four bytes of padding in the middle that belong to no column. <!-- L04 --> The heap-page section below decodes every one of those bytes.

### Two updates, one of them HOT

The first update changes `status` from `paid` to `shipped`. No index covers `status`, so this is exactly the update **HOT (heap-only tuple)** exists for: the optimisation that puts a new version on the same page as the old one and adds no index entries. It did not happen. <!-- L07 -->

```sql
update orders set status = 'shipped' where id = 4242;
```

Reading page 32 raw right afterwards shows the old version still in slot 82. Its `xmax` now names the updating transaction, 71484, and its `t_ctid`, the pointer to the newer version, says `(7692,41)`. <!-- L07 --> The new version went to page 7692, the last page of the table. That was the only page the free space map said had room: 5,632 bytes. <!-- L06 --> Because the new version is on another page, both indexes needed an entry for its new address. The update wrote five log records: 54 bytes to lock the old version, 106 bytes for the update itself, 64 bytes for a new entry in each index, and 34 bytes for the commit. That is 322 bytes, touching four pages: both heap pages and one leaf in each index. <!-- L07 -->

A second update, `shipped` to `refunded`, finds the row on page 7692, which has room. This time the update is HOT. The old version at slot 41 is marked *HOT-updated*, the new one at slot 42 is marked *heap-only*, and neither index is touched. The log records a 77-byte `HOT_UPDATE` and the 34-byte commit, 111 bytes in all. <!-- L10 --> `pg_stat_user_tables` now counts two updates and one HOT update. The two updates changed the same column in the same way. The only difference was 24 bytes of free space.

In between, an ordinary `SELECT` on the table did something that looks like it should not: it wrote. Scanning all 7,693 pages to find `id = 4242`, it passed page 32 and found the old version dead to every transaction. It shrank that version to a 4-byte stub marked dead, freeing 56 bytes, and logged a 57-byte `PRUNE` record. <!-- L09 --> That is page-local cleanup, called **pruning**, and any reader may do it.

### Vacuum reads two pages

**Vacuum** is the maintenance pass that removes dead row versions and the index entries pointing at them; [part 2](https://canery.in/blogs/postgresql-foundations-process-layer#autovacuum-part-two-what-the-worker-actually-does) covered who runs it and when. Here it was run by hand, and its first line of output is the point:

```text
pages: 0 removed, 7693 remain, 2 scanned (0.03% of total)
index scan bypassed: 1 pages from table (0.01% of total) have 1 dead item identifiers
```

Vacuum read 2 of 7,693 pages. <!-- L14 --> The **visibility map** told it the other 7,691 were all-visible, meaning every row on them is visible to every transaction, and so had nothing to clean. It also skipped both indexes, because one dead line pointer was not worth two full index scans. So page 32 stayed marked not-all-visible, holding a dead stub that two index entries still pointed at. A second vacuum with `INDEX_CLEANUP ON` removed the stub and set the last bit. <!-- L14 --> <!-- L15 --> On page 7692, vacuum turned slot 41 into a **redirect**, a 4-byte pointer to slot 42 with no row attached. Indexes point at 41, and 41 now says "look at 42". <!-- L14 -->

### A 10,000-byte note

The lab adds a nullable `note` column, which changes only the catalog: the table keeps its file and all 7,693 pages, and old rows still record five columns. <!-- L20 --> A column with no default, or with a constant one since 11, never needs a table rewrite. <!-- L107 --> It then gives row 4242 a 10,000-byte note of hexadecimal text. That value is far too big for a row, which may not exceed about 2 KB before PostgreSQL steps in, and hex does not compress well. **TOAST (The Oversized-Attribute Storage Technique)** is PostgreSQL's mechanism for such values: it cut the note into six chunks of at most 1,996 bytes and stored them as rows of the table's TOAST table. The row itself grew by only 18 bytes, a pointer to those chunks, and it went to slot 43 as another HOT update. <!-- L21 --> <!-- L22 -->

### Back through the index

Looking the row up by `customer_id` goes through `orders_customer_idx`, a **B-tree**, the index structure that keeps keys sorted in a tree of pages. The lookup reads three index pages, from the root at page 290 to page 860 to the leaf at page 1068, and the leaf entry for customer 92399 says `(7692,41)`. <!-- L24 --> <!-- L25 --> That is the address the index was given by the first update, and it is still right. Slot 41 redirects to 42, 42 says HOT-updated and points at 43, and 43 is the current version. The whole query read 13 buffers: three index pages and one heap page for each of the customer's ten orders. <!-- L23 --> <!-- L25 -->

### The log record, and a crash

Every change above was written to the **write-ahead log (WAL)** first. WAL is the append-only record of changes that PostgreSQL writes before it changes any data page, so that it can redo the changes after a crash. A position in it is a **log sequence number (LSN)**, a byte offset written as two hexadecimal halves. The second update's record starts at LSN 3/F6D261D0, and that number alone names the file and the byte where it sits: `pg_wal/0000000100000003000000F6`, offset 13,787,600. Reading 77 bytes there gives the record, and its checksum matches one computed by hand. <!-- L11 -->

Finally, the lab takes a checkpoint, updates the row once more (`amount_cents = 60000`), commits, and kills the server with `pg_ctl stop -m immediate`, which gives no process time to write anything. At that moment page 7692 in memory said its last change was at LSN 3/F6D69D50. The same page in the table file said 3/F6D42F28, from before the update, and had one line pointer fewer. <!-- L30 --> On restart the server replayed the log from the checkpoint's starting point, stopped where the log ran out, and the row read `60000`. <!-- L31 --> The committed change had existed only in the log, and the log was enough.

## Intuition

Every structure in that story is one of three kinds, and Figure 4 sorts them.

- **Data**: heap pages, index pages and TOAST chunks. Same 8 KB format, same header, same slot array.
- **Maps**: the visibility map and the free space map. Each is a few bits or one byte per heap page, small enough to consult before any page is read. Each is allowed to be wrong in one direction only.
- **The log**: WAL. Every change to data goes there first. Every data page carries the log position of its last change, and that position is what makes recovery safe to repeat.

![Map of the on-disk structures grouped as data, maps and log: an index entry points at a heap page's line pointer, the line pointer at a tuple, a tuple's TOAST pointer at chunks in the TOAST table; the visibility map and free space map each hold per-page entries for the heap; every WAL record names a relation and block, and every page's header points back at a WAL position](FIG_04)

*Figure 4 — Data, maps and log. Every arrow is a real pointer: a ctid, a line-pointer offset, a TOAST value id, a block number, or an LSN.*

An accountant's ledger is a fair picture of the data. Nothing is erased: a correction is a new entry, and the old entry is annotated to point at it, as `xmax` and `t_ctid` annotate an old row version. A journal kept in strict order, the log, lets the books be rebuilt after a fire. The numbered tabs at the front of each ledger page never move even when the entries are recopied; those are the line pointers.

The analogy breaks in two places. PostgreSQL does erase: pruning and vacuum reclaim dead versions, and a checkpoint lets old WAL be recycled, so both the ledger and the journal are finite. And the journal records physical changes to pages, not business events: a WAL record says "on block 7692 of relation 91057, build a new version at slot 42 from the old one and these 17 bytes". It can be replayed onto that page and no other.

## The heap page, byte by byte

A **heap page** is one 8 KB page of a table; "heap" is PostgreSQL's name for the table storage itself, rows in no particular order. Every heap page has five parts, in this order: a 24-byte **page header**, an array of 4-byte **line pointers**, free space, the rows themselves (called **tuples**, one per row version), and a *special space* that indexes use and tables leave empty. <!-- L35 --> <!-- L36 --> Line pointers grow forward from the header and tuples grow backward from the end, so the free space is always the hole between them. Figure 5 draws page 32 to scale.

![Page 32 of orders drawn to scale as an 8,192-byte bar: the 24-byte header, 130 line pointers ending at byte 544, a 24-byte gap of free space from 544 to 568, and tuples filling bytes 568 to 8,192, with row 4242's 53-byte tuple marked at offset 3,384](FIG_05)

*Figure 5 — Page 32 is full. The free space is the 24-byte hole between the last line pointer and the lowest tuple, which is too small for another row.*

### The header

Figure 6 decodes the header's 24 bytes as they sit on disk, in little-endian order.

![The first 24 bytes of page 32 in hex, 03 00 00 00 c0 3b 72 eb 00 00 04 00 20 02 38 02 00 20 04 20 00 00 00 00, split into fields: pd_lsn 3/EB723BC0, pd_checksum 0, pd_flags 4 all-visible, pd_lower 544, pd_upper 568, pd_special 8192, page size 8192 with layout version 4, pd_prune_xid 0; below, line pointer 82 decoded from 38 8d 6a 00 into offset 3384, flags 1, length 53](FIG_06)

*Figure 6 — Every field of the page header, and one line pointer, from raw hex. Nothing here needs a catalog lookup to read.*

`pd_lsn` is the LSN just past the last WAL record that changed this page. It is stored as two 32-bit halves, `03 00 00 00` then `c0 3b 72 eb`, which read as 3/EB723BC0. <!-- L36 --> <!-- L03 --> That field is how the page and the log stay in step, and the recovery section below depends on it. `pd_checksum` is 0 because this cluster was created without data checksums. They are off unless chosen at `initdb`, arrived in 9.3, and `initdb` turns them on by default from 18. <!-- L104 --> `pd_flags` is `0x0004`, `PD_ALL_VISIBLE`: a hint that every tuple here is visible to every transaction. <!-- L37 --> `pd_lower` (544) and `pd_upper` (568) bound the hole. `pd_special` is 8192 because a heap page has no special space. `pd_pagesize_version` packs the page size and a layout version, 4, which has not changed since PostgreSQL 8.3. <!-- L37 -->

### Line pointers, and why they exist

A **line pointer** (the docs also say *item identifier*) is 4 bytes, split 15 / 2 / 15 bits into an offset, a state and a length. The four states are unused, normal, redirect and dead. <!-- L38 --> Line pointer 82 is `38 8d 6a 00`, which read as a little-endian 32-bit word is `0x006a8d38`. The low 15 bits are 3,384, the tuple's byte offset. The next 2 bits are 1, meaning normal. The top 15 bits are 53, its length. With 544 − 24 = 520 bytes of line pointers, the page has 130 of them. <!-- L03 -->

The ctid `(32,82)` names the line pointer, not the tuple. That indirection is the point: when PostgreSQL compacts a page, it moves tuples and rewrites their line pointers' offsets, but a line pointer never moves until it is freed. So every index entry that says `(32,82)` stays correct however the page is rearranged. <!-- L39 --> The idea dates from the original design. The 1987 paper that designed the POSTGRES storage system pointed index entries at a slot in a page's "line table" for exactly this reason. <!-- L97 -->

### The tuple

A heap tuple starts with a 23-byte header, then an optional bitmap of null columns, then padding up to `t_hoff`, which is always a multiple of 8, the alignment on this machine. <!-- L40 --> Figure 7 lays out all 53 bytes of row 4242.

![Row 4242's 53 bytes drawn to scale: t_xmin 71477, t_xmax 0, t_cid 0, t_ctid (32,82), t_infomask2 5, t_infomask 0x0902, t_hoff 24 and one pad byte, then id 4242, customer_id 92399, amount_cents 56954, four padding bytes, created as microseconds since 2000, and status as a one-byte length header 0x0b followed by paid](FIG_07)

*Figure 7 — The four zero bytes after `amount_cents` belong to no column. They are there because `created` is 8 bytes wide and must start on an 8-byte boundary.*

The header's fields, in order:

- `t_xmin` = 71477, the transaction that inserted this version, which here is the load. `t_xmax` = 0: nobody has deleted or updated it. `t_cid` = 0, the command within that transaction.
- `t_ctid` = `(32,82)`, which points at the tuple itself. That is how a tuple says "I am the newest version".
- `t_infomask2` = 5: the low 11 bits count the tuple's attributes. `t_infomask` = `0x0902`, three flags: the tuple has a variable-width column (`0x0002`), its inserting transaction is known to have committed (`0x0100`), and its `xmax` is invalid (`0x0800`). <!-- L41 --> <!-- L04 -->
- `t_hoff` = 24. The header proper ends at byte 23, so one byte of padding follows. There is no null bitmap, because no column is null.

The data follows at byte 24 and needs no catalog to read once you know the column types. `92 10 00 00` is 4242, `ef 68 01 00` is 92399 and `7a de 00 00` is 56954. Then come four zero bytes, because the `timestamptz` that follows must start on an 8-byte boundary. It is `80 28 c0 07 48 ea 02 00`: 820,545,042,000,000 microseconds after midnight on 1 January 2000, which is 2026-01-01 01:10:42 UTC. <!-- L04 --> Last is `status`. Its first byte, `0x0b`, has its low bit set, which marks a **varlena** (variable-length value) with a 1-byte header. The remaining seven bits give the total length, 5, so 4 bytes of text follow: `paid`. Values under 127 bytes get this short header and no alignment padding. <!-- L42 -->

Two numbers fall out of this. Tuples are stored on 8-byte boundaries, so a 53-byte `paid` row and a 56-byte `shipped` row each take 56 bytes, and a 57-byte `refunded` row takes 64; each also needs its 4-byte line pointer. That averages about 62.7 bytes per row, and 8,168 usable bytes hold 130 of them. <!-- L05 --> And the padding is a cost of column order. The same million rows, copied with `created` first so nothing needs padding, fill 7,353 pages at 136 rows each, 4.4% fewer. <!-- L05 --> The copy's file is 7,360 pages, because PostgreSQL 16 extends a table several pages at a time during a bulk load and 7 of them were never used. <!-- L111 -->

## Who can see a row: xmin, xmax and the hint bits

Under MVCC, whether a transaction can see a row version is a question about the version's two transaction ids, and nothing else. Every query runs with a snapshot: a record of which transactions had committed when the snapshot was taken. A version is visible if its `xmin` committed before the snapshot, and its `xmax` is empty, aborted, or had not committed by then. Figure 8 draws row 4242's five versions on one axis of transaction ids.

![Five horizontal bars on a transaction-id axis, one per version of row 4242: (32,82) from xid 71477 to 71484, (7692,41) from 71484 to 71485, (7692,42) from 71485 to 71490, (7692,43) from 71490 to 71539, and (7692,44) from 71539 onward; a vertical snapshot line crosses exactly one bar](FIG_08)

*Figure 8 — Each version is alive from its `xmin` to its `xmax`. Any snapshot, drawn as a vertical line, crosses exactly one bar, and that is the version it reads.*

"Committed" has to be looked up. The **commit log**, `pg_xact`, stores 2 bits per transaction: in progress, committed, aborted or sub-committed. <!-- L46 --> It was called `pg_clog` until PostgreSQL 10, when it was renamed so that nobody would mistake it for a disposable log and delete it. <!-- L47 --> The 1987 design already had this: a 2-bit status per transaction, and `xmin`/`xmax` stamps on every record. <!-- L96 -->

Looking up `pg_xact` for every row of every scan would be slow, so the first reader to learn a transaction's fate writes it into the tuple as **hint bits**: `HEAP_XMIN_COMMITTED` (`0x0100`), `HEAP_XMIN_INVALID`, `HEAP_XMAX_COMMITTED` and `HEAP_XMAX_INVALID`. <!-- L44 --> <!-- L41 --> The lab caught this happening. Right after update 1 committed, the new version's infomask was `0x2802`, without the committed hint. After one `SELECT` had read it, it was `0x2902`. <!-- L08 --> Setting a hint bit marks the buffer dirty, so a read can cause a write. That is why the first scan after a big load can generate I/O that a second, identical scan does not. <!-- L44 -->

Two consequences matter later. First, a version whose `xmin` neither committed nor is still running is treated as aborted, whatever happened to its transaction. The code's comment is "it must have aborted or crashed". <!-- L45 --> So after a crash nothing needs undoing: the in-progress transactions' versions are simply never visible, and vacuum removes them. Second, transaction ids are 32 bits and eventually wrap, so vacuum must mark old versions **frozen**, visible to everyone forever. [Part 2](https://canery.in/blogs/postgresql-foundations-process-layer#autovacuum-part-two-what-the-worker-actually-does) covered when that happens. The storage-layer part is one bit in the visibility map, which the next-but-one section describes.

## HOT: the update that skips the indexes

An update writes a new version. Where that version goes decides what else must be written, and HOT is the special case where nothing else is.

An update is HOT when two conditions hold. <!-- L48 --> The first is that no column referenced by any index changes. That includes columns an index only uses in a partial-index `WHERE` clause, and the test compares binary representations, not the type's own equality. <!-- L52 --> The second is that the old version's page has room for the new one. Then the new version goes on the same page, marked *heap-only* (`HEAP_ONLY_TUPLE`, `0x8000` in `t_infomask2`). The old version is marked *HOT-updated* (`0x4000`) and its `t_ctid` points forward. No index entry is added: every index keeps pointing at the first line pointer of the chain, and a lookup follows `t_ctid` along the page until it finds the version it can see. <!-- L41 --> <!-- L51 --> The chain never leaves the page. That keeps the chain short to follow, and it lets cleanup work one page at a time.

Update 1 failed the second condition. The new version needed 56 bytes of tuple and 4 of line pointer, and page 32 had 24. Before giving up the page to find another, `heap_update` logs a temporary lock on the old version, which is the 54-byte `LOCK` record. <!-- L55 --> <!-- L07 --> Figure 9 follows the line pointers on both pages through each step.

![Small multiples of line pointers: after update 1, page 32 slot 82 is normal with xmax set and points to (7692,41), and both indexes gain an entry for (7692,41); after a reader, slot 82 is dead; after update 2, slot 41 is HOT-updated and points to slot 42, a heap-only tuple; after the first vacuum slot 41 is a redirect to 42 and slot 82 is still dead; after the forced index cleanup slot 82 is unused](FIG_09)

*Figure 9 — The two indexes point at `(32,82)` and later at `(7692,41)`, and never at slot 42. The redirect is what lets them stay put.*

Figure 10 prices the two updates. The one that could not stay on its page wrote five records, 322 bytes, to four pages: two heap pages and one leaf in each index. The HOT one wrote two records, 111 bytes, to one page. <!-- L07 --> <!-- L10 --> Even the `HOT_UPDATE` record is trimmed. When old and new versions share a page, PostgreSQL leaves out the bytes at the start and end of the new tuple that match the old one. So the record's 17 bytes of tuple data are a 2-byte count saying the first 24 bytes are unchanged, the 5-byte header, 1 pad byte, and the 9 bytes of `refunded`. <!-- L12 --> <!-- L56 -->

![Stacked horizontal bars of WAL bytes per update: the non-HOT update's 322 bytes split into LOCK 54, UPDATE 106, two INSERT_LEAF records of 64 each and COMMIT 34, touching four pages; the HOT update's 111 bytes split into HOT_UPDATE 77 and COMMIT 34, touching one page](FIG_10)

*Figure 10 — Same column, same kind of change, three times the log and four times the pages. PostgreSQL 16.2, the lab's `orders` table, no checkpoint between the two updates.*

**Pruning** is the other half of HOT. When a backend reads a page that has a prune hint set (`pd_prune_xid`), and the page has less than the larger of its fill-factor reserve or a tenth of the page free (819 bytes at the default), it tries to clean the page on the spot. <!-- L53 --> Old versions that nobody can see lose their storage. A dead root keeps a 4-byte stub, marked dead or redirected, because indexes still point at it. That is what the lab's `SELECT` did to page 32: slot 82 became dead with length 0, and `pd_upper` moved from 568 to 624. <!-- L09 --> The stub stays until vacuum has removed the index entries that name it. <!-- L51 --> Pruning frees the storage of any dead version this way, deletes and cross-page updates included, as page 32 shows. What HOT adds is that a heap-only version needs no stub at all, since no index names it, so a chain of HOT updates can be cleaned up during ordinary reads without waiting for vacuum. <!-- L49 -->

The practical lever is **fillfactor**, a per-table setting for how full inserts may pack a page. Lowering it from the default 100 leaves room for HOT updates. The docs also note that without it HOT still happens once updated rows migrate to pages with space, and that is exactly the lab's second update. <!-- L50 --> HOT arrived in PostgreSQL 8.3. <!-- L54 -->

It is also PostgreSQL's answer to a real criticism. A 2017 VLDB study of MVCC designs classifies Postgres as storing each version in the table and pointing indexes at physical versions. It found that this design must insert into every secondary index for every new version, and that indexes pointing at a stable logical id did better on update-heavy workloads. <!-- L100 --> <!-- L101 --> The study ran on its own in-memory research engine, not on PostgreSQL. Uber's 2016 migration post made the same complaint from production. <!-- L103 --> HOT is the exception that removes the index writes, and the lab shows both sides: one update paid for both indexes, the next paid for neither. The 1987 design had proposed skipping index maintenance when no indexed field changed, too. <!-- L97 -->

## The visibility map, and why vacuum skips pages

The **visibility map (VM)** is the table's `_vm` fork, and it holds two bits per heap page. The first, *all-visible*, means no tuple on the page needs vacuuming: every version on it is visible to every transaction. The second, *all-frozen*, means every tuple on the page is frozen, so even an anti-wraparound vacuum need not visit it. <!-- L57 --> The map is conservative by construction. Only vacuum sets a bit, any change to a page clears it, and a set bit is always true while a clear bit merely might be. Indexes have no VM. <!-- L57 --> The page header's `PD_ALL_VISIBLE` flag mirrors the first bit on the page itself. <!-- L37 --> At two bits per page, one 8 KB map page covers 32,672 heap pages, 255 MB of table, so `orders` needs one. <!-- L116 --> <!-- L02 -->

Figure 11 shows the lab's map before and after the two vacuums.

![Three bands of 7,693 tiles, one per heap page of orders: before vacuum, pages 32 and 7692 are clear and all others all-visible; after the first vacuum only page 32 is clear; after the forced index cleanup all are set; a zoomed inset shows pages 0 to 31 as a run of 32 skippable pages and marks the two pages vacuum actually read](FIG_11)

*Figure 11 — Two clear bits in 7,693 made vacuum read two pages. Page 32 stayed clear after the first vacuum, because vacuum chose to skip the index work that would have freed its last dead stub.*

The map buys two things. The first is vacuum skipping pages. The lab's vacuum read 2 of 7,693 pages. <!-- L14 --> It does not skip every all-visible page, though: it skips only runs of at least 32. For shorter runs it reads the pages anyway, because the operating system's read-ahead makes that cheap and skipping would defeat it. <!-- L60 --> Page 32 happens to follow exactly 32 all-visible pages. Had the row been on page 20, vacuum would have read pages 0 to 20 too. The VM itself arrived in 8.4, and the all-frozen bit in 9.6, when anti-wraparound vacuum stopped having to read every page of a table. <!-- L58 -->

The lab also caught vacuum declining work. When fewer than 2% of a table's pages hold dead line pointers, vacuum skips index vacuuming altogether (14 made this the default, as `INDEX_CLEANUP auto`). One dead stub is not worth reading 2,243 index pages to remove two entries. <!-- L61 --> <!-- L14 --> The price is that page 32 stayed not-all-visible until a vacuum with `INDEX_CLEANUP ON` removed the entries, turned the stub into an unused slot and set the bit. <!-- L15 --> On a real table the stubs wait for the next vacuum that crosses the threshold.

The second thing is **index-only scans**, which answer a query from the index alone. That would be impossible without the VM, because an index entry says nothing about which transactions may see its row. A 2017 study of MVCC designs notes that without version information in the index, a system must always check the tuple. <!-- L102 --> PostgreSQL's way out, since 9.2, is to check the VM: if the page is all-visible, the row is visible, and the heap is skipped. <!-- L59 --> Figure 12 shows what that is worth. The lab counted 100,000 rows of a copy of `orders` through an index-only scan three times: all-visible, after updating one row in fifty, and after vacuum.

![Two panels of bars for the same index-only count of 100,000 rows: heap fetches on a linear scale, 0, 102,000 and 0, and shared buffers on a log scale, 118, 102,118 and 118, for the all-visible table, after touching one row in fifty, and after vacuum](FIG_12)

*Figure 12 — The plan never changed; the map did. PostgreSQL 16.2, a 7,847-page copy of `orders`, forced index-only plan; execution time 10.6, 113.1 and 9.5 ms in this run.*

The one-in-fifty update cleared the bit on every page, since every page had a row that changed. So the scan fetched each heap tuple to check it: 102,000 fetches for 100,000 counted rows, the extra 2,000 being old versions whose index entries were still there. <!-- L34 --> One vacuum put every bit back. For an index-only scan, `Heap Fetches` in `EXPLAIN ANALYZE` is the visibility map's report card.

## The free space map: where a new row lands

The **free space map (FSM)**, the `_fsm` fork, answers one question fast: which page has room for a row this size? It keeps one byte per heap page, the free space divided by 32 and rounded down, so it records space in 32-byte steps. <!-- L62 --> Every heap and index relation has one except hash indexes. <!-- L113 --> The bytes are arranged as a tree. Within each FSM page, a binary tree stored as an array keeps each page's value at a leaf and, at every node above it, the larger of its two children. Across FSM pages the same idea repeats, with three levels and the root always at block 0. <!-- L62 --> One FSM page holds 4,069 leaves, and three levels cover any table at 8 KB. <!-- L63 --> Figure 13 draws the four FSM pages of `orders` and the path to the one page with room.

![The four FSM pages of orders as a tree: block 0 at level 2 holding the maximum 174, block 1 at level 1 with two children holding 2 and 174, and two leaf pages at level 0 covering heap pages 0 to 4,068 and 4,069 onward; inside the second leaf, the path from node 0 to node 7718 carries 174 at every step, and inside the first, node 4127 for heap page 32 holds 2](FIG_13)

*Figure 13 — To find room, PostgreSQL follows the larger child from the root. One look at block 0's root, 174, says the roomiest page in the table has between 5,568 and 5,599 bytes free.*

That is why update 1's new version went to page 7692. Before the update the FSM listed exactly one page with room, 7692 with 5,632 bytes, and the updater asked the FSM because page 32 was full. <!-- L06 --> After both vacuums the map read 174 at the leaf for page 7692 (node 7718) and all the way up. 174 × 32 = 5,568. The page's actual hole was 5,592 bytes, less the 4 bytes a new row's line pointer would take, which is 5,588 rounded down to a multiple of 32. Page 32, whose hole had grown to 80 bytes when its dead version was pruned and whose freed slot could be reused, showed category 2: 64 bytes. <!-- L16 --> <!-- L15 --> <!-- L09 -->

The FSM is allowed to be wrong because nothing's correctness depends on it. It is not WAL-logged; its pages are written as hints. <!-- L64 --> If the page it offers turns out not to have room, the inserter records that page's real free space and asks again, and vacuum rewrites the bottom level as it scans. <!-- L115 --> A crash can at worst leave it stale, and staleness costs a retry, never a wrong answer. Per-table FSM forks date from 8.4; before that, the map was a fixed-size region of shared memory that had to be sized by hand. <!-- L64 -->

## TOAST: when a value will not fit

A tuple may not span pages, so a value bigger than a page must be shrunk or moved. **TOAST** does both. <!-- L65 --> It works through the varlena header. That is the same length word `status` used, whose low bits distinguish a plain value, a 1-byte short header, a compressed value and a pointer to data stored elsewhere. <!-- L42 -->

The toaster runs when a row would be wider than `TOAST_TUPLE_THRESHOLD`. It compresses or moves the widest eligible values until the row fits under `TOAST_TUPLE_TARGET`, or nothing more can be gained. <!-- L65 --> Both are 2,032 bytes on 8 KB pages, the largest tuple size that lets four tuples share a page. The target can be changed per table with `toast_tuple_target`. <!-- L66 --> Each column has a **storage strategy**:

- `EXTENDED` (the default for most types): compress, then move out of line if still too big.
- `EXTERNAL`: move out of line but never compress. Substrings of an uncompressed value can be read without fetching all of it.
- `MAIN`: compress, and move out of line only as a last resort.
- `PLAIN`: neither, for types that cannot be TOASTed. <!-- L69 -->

Compression is **pglz**, PostgreSQL's own compressor from the Lempel–Ziv family that began with a 1977 paper by Ziv and Lempel. <!-- L74 --> Its default settings skip inputs under 32 bytes, keep the result only if it saves at least 25%, and give up if the first 1 KB does not compress. <!-- L70 --> `lz4` is an option from 14; the default is still `pglz`. <!-- L72 -->

The lab measured where the lines fall, using a two-column `(int, text)` table so that the arithmetic is exact. The row is a 24-byte header, a 4-byte integer, and the value with its 4-byte length word: 32 bytes plus the value. Figure 14 plots what happened.

![Line chart, log-scale y axis, of bytes stored in the row against raw value size from 500 to 10,000 bytes: both compressible and incompressible text stay inline and grow one-for-one up to 2,000 bytes; at 2,001 compressible text drops to 51 bytes of pglz output, rising to 142 at 10,000, and incompressible text drops to an 18-byte pointer, with a vertical line at the 2,032-byte tuple threshold](FIG_14)

*Figure 14 — The cliff is exact: a 2,000-byte value makes a 2,032-byte row and stays; 2,001 bytes tips it over. What happens next depends only on whether the text compresses by a quarter.*

At 2,000 bytes both kinds of text stay inline, making a 2,032-byte row. At 2,001 bytes the toaster runs. Text that repeats a phrase compresses to 51 bytes and stays in the row. Hex text cannot be shrunk by a quarter, so it leaves the row: the tuple drops to 46 bytes, 18 of them a pointer. <!-- L17 --> Out-of-line values are cut into chunks of at most `TOAST_MAX_CHUNK_SIZE`, 1,996 bytes, chosen so four chunks fit on a TOAST page. A value of n bytes needs ⌈n / 1,996⌉ chunks: 2 for anything from 2,001 to 3,000 bytes, 6 for 10,000. <!-- L67 --> <!-- L18 --> A compressible 10,000-byte value never leaves the row at all; it becomes 142 bytes. <!-- L18 -->

Row 4242's note took the out-of-line path, and Figure 15 decodes the pointer it left behind.

![The 18-byte TOAST pointer at the end of row 4242's tuple, 01 12 14 27 00 00 10 27 00 00 cb 63 01 00 b4 63 01 00, decoded as header 0x01, tag 18 on-disk, raw size 10,004, stored size 10,000 with no compression, value id 91083 and TOAST table 91060; beside it the six chunk rows for value 91083, five of 1,996 bytes and one of 20, four on TOAST page 0 and two on page 1](FIG_15)

*Figure 15 — Eighteen bytes stand in for ten thousand. The pointer carries both sizes, so PostgreSQL knows the value's length without fetching a single chunk.*

An on-disk TOAST pointer is always 18 bytes, whatever it points to. <!-- L68 --> Its first byte, `0x01`, is a 1-byte varlena header whose length bits are all zero, which would be impossible for a real value; that is what marks a pointer. Tag 18 says "on disk". Then come four 32-bit fields: the raw size including its own 4-byte header (10,004), the stored size and compression method (10,000, none), the value's id (91083), and the TOAST table's OID (91060). <!-- L21 --> The six chunks are rows of `pg_toast.pg_toast_91057`, keyed by value id and sequence number through a unique index. <!-- L21 --> The log shows the toaster's work in order. First a `LOCK` on the old version, because `heap_update` must release the page while the toaster runs. <!-- L55 --> Then four chunk inserts on TOAST page 0, the fifth opening page 1, an entry in the TOAST index for each, and finally an 86-byte `HOT_UPDATE` for the row itself. <!-- L22 -->

Two properties make TOAST cheap in practice. An update that does not change the out-of-line value copies the 18-byte pointer and nothing else. The lab updated the integer column of a row holding a 10,000-byte out-of-line value: no chunk moved, and the update wrote 168 bytes of WAL. <!-- L71 --> <!-- L19 --> And an out-of-line value is fetched only if the query asks for that column, when the result is sent. So the main table stays small and cacheable, however large the values it points at. <!-- L114 --> TOAST arrived in 7.1, in 2001, the same release as WAL. Until then a row had a compiled-in limit of 8 to 32 KB. <!-- L73 -->

## The B-tree: one lookup and one split

The **B-tree** comes from Bayer and McCreight's 1970 report, published in 1972. It kept an index in fixed-size pages on disk, so that a search, an insert or a delete costs time proportional to log_k of the index size, with every page at least half full. <!-- L81 --> By 1979 it was, in Comer's survey's words, the de facto standard for file organisation. The variant most systems use is the **B+-tree**, in which every key lives in a leaf and the upper levels only guide the search. <!-- L82 --> PostgreSQL's B-tree, `nbtree`, is a B+-tree built on Lehman and Yao's 1981 design for concurrent access. <!-- L75 -->

An `nbtree` index is pages of the same 8 KB format, with a special space that holds each page's left and right neighbours and its level. Block 0 is a **metapage**, which records where the root is. Above the leaves every entry is a **pivot tuple**, a separator key plus a *downlink* to the child page that holds keys from there up to the next separator. The first downlink on a page has no key at all, standing for minus infinity. <!-- L77 --> Lehman and Yao added two things to each page. A **right-link** points at the next page on the same level. A **high key** is an upper bound on the keys the page may hold. A search that lands on a page and finds its key above the high key knows the page was split while it was on the way down, and follows the right-link. In the paper this removes read locks entirely. PostgreSQL still takes a short read lock on each page, because unlike Lehman and Yao's model its backends share one copy of each page in memory. <!-- L75 --> <!-- L76 -->

Figure 16 is the lab's lookup of customer 92399 in `orders_customer_idx`.

![The lookup of customer 92399: metapage block 0 names root 290 at level 2; root 290 holds five pivots, minus infinity, 24709, 49417, 74125 and 98833, and the search takes the downlink for 74125 to block 860; block 860 at level 1 holds 285 items with high key 98833 and sends it to leaf 1068 via key 92395; leaf 1068 holds 89 items with high key 92482 and has two entries for 92399, a posting list of nine heap TIDs and a plain entry for (7692,41), which leads to heap page 7692, slot 41 redirecting to 42 and on to 43](FIG_16)

*Figure 16 — Three index pages and a chain on one heap page. The index entry still says slot 41, two HOT updates and one redirect later.*

The metapage says the root is block 290, at level 2. The root holds five pivots: minus infinity, 24709, 49417, 74125 and 98833. 92399 falls between the last two, so the search takes 74125's downlink to block 860. Block 860, at level 1, has 285 items and a high key of 98833. Its downlink for 92395 leads to leaf 1068, which holds keys 92395 to 92481 and has a high key of 92482. <!-- L24 --> The whole index is that shape: one root, 5 pages at level 1, and 1,150 leaves. <!-- L26 --> The query's plan reported 13 buffer hits: the three index pages, and ten heap pages for the customer's ten orders. The metapage is not re-read, because each backend caches it after first use. <!-- L23 --> <!-- L80 -->

The leaf has two entries for 92399, and they show **deduplication**, added in PostgreSQL 13. A non-unique index stores many rows with the same key, and deduplication merges them into one **posting-list tuple**: the key once, then a sorted array of heap TIDs. <!-- L78 --> Nine of the customer's ten orders share one 72-byte tuple. The tenth, row 4242's new version from update 1, sits in a separate 16-byte entry, because deduplication runs lazily, only when a page would otherwise have to split. <!-- L25 --> <!-- L78 --> Across the whole index, 100,000 of the 100,001 leaf tuples are posting lists, and between them the leaf tuples hold 1,000,000 heap TIDs, one per row. <!-- L26 --> Keys still have to be unique for Lehman and Yao's invariants to hold, so every entry is ordered by key and then by heap TID. And pivots keep only as many key columns as they need to separate their neighbours, a trick called suffix truncation. <!-- L77 -->

A page split is the one structural change an ordinary insert can cause. The lab watched one on a fresh single-column index. 407 ascending integers fill its one leaf, leaving 8 bytes free, and the 408th does not fit. <!-- L27 --> Figure 17 is before and after.

![Before and after a leaf split, key slots to scale: before, one leaf page holding keys 1 to 407 with 8 bytes free is also the root; after, the left leaf holds keys 1 to 366 plus a high key of 367 and has 808 bytes free, the right leaf holds 367 to 408 with 7,308 bytes free, and a new root at block 3 holds a minus-infinity downlink to the left leaf and key 367 to the right; a second panel shows a split in the middle of a tree dividing 367 items into 204 and 205](FIG_17)

*Figure 17 — A split at the right edge leaves the left page 90% full, betting that ascending keys will keep arriving on the right. A split in the middle divides the page evenly.*

The insert logged a 752-byte `SPLIT_R` record and a 122-byte `NEWROOT`. The left page kept keys 1 to 366 and gained a high key of 367, with 808 bytes free. The right page took 367 to 408 and has 7,308 bytes free. A new root at block 3 holds two downlinks: minus infinity to the left page, 367 to the right. <!-- L27 --> The split is uneven on purpose. When the page being split is the rightmost on its level, PostgreSQL leaves the left half at the leaf fill factor, 90% by default. Keys that keep ascending, such as sequence numbers or timestamps, then build a tree of 90%-full pages instead of half-full ones. <!-- L79 --> <!-- L110 --> Elsewhere a split equalises free space. After 41 more keys were fed into the middle of a second index, its left leaf split into 204 and 205 items. <!-- L28 --> A root split is an ordinary split followed by a new root, installed by updating the metapage. <!-- L80 -->

## WAL: records, LSNs and segment files

WAL's contract is that no change reaches a data file before the log records describing it have been flushed. After a crash, the log is replayed forward, **redo**, to reapply whatever the data files missed. One flush of the log can make many commits durable at once. <!-- L83 --> [Part 1](https://canery.in/blogs/postgresql-foundations-memory-layer#when-a-dirty-page-may-leave-memory) covered the memory side of that rule; this section is the file side.

### From an LSN to a file

An LSN is a byte offset into one conceptually endless log, 64 bits wide and written as two 32-bit hexadecimal halves. The log is stored as **segment files** of 16 MB each, and each segment is divided into 8 KB WAL pages. File names start at `000000010000000000000001` and only ever increase. <!-- L84 --> The segment size has been an `initdb` option since 11. <!-- L88 --> Figure 18 decomposes the second update's LSN.

![The LSN 3/F6D261D0 as 64 bits: the high 32 bits, 3, and the low 32 bits split into the top byte F6 and a 24-bit offset D261D0; these give the file name 00000001 for the timeline, 00000003 and 000000F6, and the offset 13,787,600, which is WAL page 1683 of the segment at byte 464](FIG_18)

*Figure 18 — An LSN is a file name and an offset. With 16 MB segments, the low 24 bits are the offset and the next 8 are the last two hex digits of the name.*

A segment is 16 MiB, 2^24 bytes, so the segment number is the LSN shifted right by 24 bits. For 3/F6D261D0 that is 0x3F6. The name is three 8-digit hex fields. The first is the **timeline**, a counter of recovery histories: a new one begins whenever an archive recovery, such as a point-in-time restore, completes, so that WAL written afterwards cannot overwrite the old history's files. It is 1 here. <!-- L119 --> Then come the segment number's high part and its low part, 256 segments to each 4 GiB. So the record lives in `0000000100000003000000F6`, at byte 0xD261D0 = 13,787,600. That is WAL page 1683 of the file, 464 bytes in. <!-- L85 --> <!-- L11 --> `pg_walfile_name_offset()` does this arithmetic for you; doing it once by hand is how you learn to read LSNs in log messages. The directory was `pg_xlog` until 10. <!-- L47 -->

Every WAL page begins with a small header, and the first page of each segment with a long one. The segment's first 40 bytes carry the magic number `0xD113` (the WAL format version for 16), the timeline, the page's own LSN (3/F6000000), the segment size, the WAL page size, and the cluster's **system identifier**. That identifier is the same 64-bit number `pg_controldata` reports. <!-- L13 --> <!-- L86 --> PostgreSQL refuses a segment whose identifier or sizes do not match its own, so a WAL file from another cluster cannot be replayed by mistake. <!-- L117 -->

### One record, byte by byte

The lab read the second update's 77 bytes straight out of the segment file, and Figure 19 lays them out.

![The 77-byte HOT_UPDATE record drawn to scale: a 24-byte header with total length 77, xid 71485, previous-record pointer 3/F6D26190, info 0x40, resource manager 10 (Heap) and CRC cf8032b2; a 20-byte block reference naming tablespace 1663, database 90977, relation 91057, block 7692 and 17 bytes of data; a 2-byte main-data header; the 17 bytes of block data, a prefix count of 24, the new tuple header, one pad byte and refunded; and 14 bytes of main data with old offset 41 and new offset 42](FIG_19)

*Figure 19 — Everything recovery needs to redo the update is in these 77 bytes: which page, what to change on it, and a checksum to prove the bytes are the ones that were written.*

The 24-byte header is common to every record. It holds the total length (77), the transaction (71485), the LSN of the previous record (3/F6D26190), an info byte (`0x40`, meaning HOT update), the **resource manager** that knows how to replay it (10, the heap), and a CRC. <!-- L86 --> <!-- L121 --> <!-- L11 --> The block reference says which page the record changes: tablespace 1663, database 90977, relation 91057, block 7692, with 17 bytes of data for it. The 14 bytes of main data say which slot is old (41) and which is new (42). <!-- L11 --> <!-- L12 --> `pg_waldump`, which reads segment files offline, prints the same record in one line:

```text
rmgr: Heap        len (rec/tot):     77/    77, tx:      71485, lsn: 3/F6D261D0, prev 3/F6D26190, desc: HOT_UPDATE old_xmax: 71485, old_off: 41, old_infobits: [], flags: 0x20, new_xmax: 0, new_off: 42, blkref #0: rel 1663/90977/91057 blk 7692
```

The CRC is **CRC-32C**, with the Castagnoli polynomial that iSCSI also standardised. <!-- L87 --> The lab computed it over the record's bytes and got `cf8032b2`, the value in the header. <!-- L11 --> Not every record is this small. The first change to a page after a checkpoint carries a copy of the whole page, [the full-page image part 1 measured](https://canery.in/blogs/postgresql-foundations-memory-layer#the-full-page-image). The crash step's first record carried one: 2,684 bytes of page, the page's 5,508-byte hole left out. <!-- L29 -->

## Crash recovery, archiving and replicas: three readers of one log

Three different processes read the same segment files, and Figure 21 shows all three. The first is the one that recovers from a crash.

### Replaying a crash

A **checkpoint** makes the log before it forgettable. It notes the current WAL position as its **REDO location**, writes every page that was dirty at that moment, and then saves the REDO location in `pg_control`, the small control file that recovery reads first. <!-- L89 --> [Part 2](https://canery.in/blogs/postgresql-foundations-process-layer#the-checkpointer-making-the-wal-forgettable) covered the checkpointer. The lab's checkpoint left REDO at 3/F6D691A0, in segment `…00F6`. It then updated row 4242 and committed. The update wrote a `LOCK` record carrying the full-page image, a 72-byte `HOT_UPDATE` and a commit. <!-- L29 --> Just before the crash, the buffer holding page 7692 was dirty with a usage count of 5, and its header said 3/F6D69D50. The table file's copy said 3/F6D42F28 and had one line pointer fewer: the committed change was only in memory and in the log. `pg_ctl stop -m immediate` killed everything, and `pg_control` was left saying `in production`, the mark of an unclean stop. <!-- L30 --> Figure 20 is what happened next.

![Sequence diagram with participants backend, shared buffers, pg_wal, table file, pg_control and startup process: a checkpoint records REDO 3/F6D691A0; the update's LOCK with page image, HOT_UPDATE and COMMIT are flushed to pg_wal while the page stays dirty in buffers and the file keeps 3/F6D42F28; after an immediate stop the startup process reads pg_control, fsyncs the data directory, replays from REDO, applies each record because the page LSN is lower, stops at a zero-length record at 3/F6D69D78, and an end-of-recovery checkpoint writes the page with LSN 3/F6D69D50](FIG_20)

*Figure 20 — Recovery is redo only. Nothing is undone, because a version whose transaction never committed is invisible anyway.*

The restart's log reads like a checklist (timestamps and process ids removed): <!-- L31 -->

```text
LOG:  database system was interrupted; last known up at 2026-09-24 12:21:50 IST
LOG:  database system was not properly shut down; automatic recovery in progress
LOG:  redo starts at 3/F6D691A0
LOG:  invalid record length at 3/F6D69D78: expected at least 24, got 0
LOG:  redo done at 3/F6D69D50 system usage: CPU: user: 0.00 s, system: 0.00 s, elapsed: 0.00 s
LOG:  checkpoint starting: end-of-recovery immediate wait
LOG:  checkpoint complete: wrote 4 buffers (0.0%); ...
LOG:  database system is ready to accept connections
```

The **startup process**, the process that runs recovery, reads `pg_control`, then the checkpoint record, then replays from the REDO location. <!-- L89 --> Before replaying, it fsyncs the whole data directory, since writes made before the crash may not have been durable yet. The fsync runs between the first two lines, which is where their 1.5-second gap goes. <!-- L91 --> <!-- L31 --> For each record it reads the target page and compares LSNs. If the page's `pd_lsn` is already at or past the record, the change is on the page, and the record is skipped. <!-- L90 --> That comparison is what makes replay safe to repeat: a second crash during recovery just replays the same records again. Here the `LOCK` record's page image put page 7692 back as it was at that moment, and the `HOT_UPDATE` added slot 44. Replay ends at the first record that fails validation. At 3/F6D69D78 the next record's length was zero, where the log simply stops. <!-- L118 --> An end-of-recovery checkpoint then wrote four pages, and the table file's copy of page 7692 finally read 3/F6D69D50. <!-- L31 -->

That recovery has no undo pass, and that is not the textbook design. **ARIES**, the recovery method IBM researchers published in 1992, recovers in three passes. It analyses the log, redoes everything ("repeating history", including the work of transactions that never committed), then undoes the losers, logging each undo as it goes. <!-- L92 --> It needs the undo pass because of its buffer policy. In ARIES's terms, a *steal* policy lets a dirty page of an uncommitted transaction be written, and *no-force* means commit does not wait for data pages. <!-- L93 --> PostgreSQL is both. Part 2's background writer and checkpointer write any dirty page, and a commit waits only for WAL. So uncommitted changes can be on disk after a crash. PostgreSQL does not need to remove them: their versions carry an `xmin` that never committed, so readers treat them as aborted, and vacuum clears them later. <!-- L45 -->

That is a legacy of the original design, and of its retreat. The 1987 storage paper had no conventional log and no code to run at recovery time. It never overwrote a record; updates became insertions; a "vacuum cleaner" process moved old records to an optical-disk archive. <!-- L96 --> By 1990 its designers wrote that without stable main memory, such a system must force every page a transaction wrote to disk at commit. That is random I/O, where a log needs only sequential writes, and so it is guaranteed to be slower. <!-- L98 --> They still counted one advantage: aborting is instant, because the old records are still there. <!-- L99 --> PostgreSQL 7.1 added WAL in 2001; until then every commit had forced its data pages to disk. <!-- L73 --> What runs today is ARIES-style redo on top of the 1987 no-overwrite heap. The no-overwrite heap is why there is nothing to undo, and why vacuum exists at all.

### Archiving

Without archiving, a checkpoint lets old segments be recycled, renamed for reuse as future segments. With `archive_mode = on`, a finished segment is first handed to `archive_command`. That is any shell command, with `%p` replaced by the file's path and `%f` by its name, which must exit 0 only if the copy succeeded. <!-- L94 --> The lab turned it on with `cp` into a scratch directory and restarted, and an `archiver` process appeared among the postmaster's children. `pg_switch_wal()` closed the current segment early. Moments later `0000000100000003000000F6` was in the archive, `pg_stat_archiver` counted one success, and `pg_wal/archive_status` held a `.done` marker for it. <!-- L32 --> That file held the second update's record, the checkpoint's REDO point and every record the crash replay had applied. <!-- L112 --> Point-in-time recovery is a base backup plus those archived segments, replayed as far as the chosen moment, by the same startup process running the same redo. <!-- L120 -->

### Replicas

The third reader is a **walsender**. That is a process the postmaster forks for each client connected with the replication protocol, which streams WAL as it is written rather than a whole segment at a time. On a standby, a **walreceiver** writes what arrives into its own `pg_wal`, and the standby's startup process replays it continuously, with the same code that ran after the crash. <!-- L95 --> The lab attached `pg_receivewal`, a client that speaks the replication protocol and saves segments, and the postmaster forked a `walsender` in state `streaming`. It wrote the next segment, `…00F7`, under the same name the primary uses. <!-- L33 --> That is the replication part 2 left for this post: two more processes reading the log that recovery reads. Configuring a standby, and failing over to it, are out of scope.

![WAL written by backends into pg_wal segment 0000000100000003000000F6, read three ways: by the startup process during crash recovery from the REDO location into the table files; by the archiver, which runs archive_command to copy the finished segment into an archive directory and marks it done; and by a walsender, which streams records to pg_receivewal or a standby's walreceiver, whose startup process replays them](FIG_21)

*Figure 21 — One log, three readers. Crash recovery, point-in-time recovery and a standby all run the same redo; they differ in where the WAL comes from.*

All three rest on one assumption below PostgreSQL: that when `fsync()` returns, the file's data has been transferred to the storage device, which is what POSIX asks of it. <!-- L105 --> The docs warn that a drive which reports a write as done while holding it in a volatile cache can corrupt the database on power loss, and no amount of WAL can prevent that. <!-- L106 -->

## The math

Five formulas cover the storage layer's numbers. Each is stated, then checked against the lab.

### Rows per page

A heap page holds the largest number of tuples n for which the header, n line pointers and n aligned tuples fit in 8,192 bytes:

$$
24 + 4n + \sum_{i=1}^{n} \mathrm{MAXALIGN}(t_i) \le 8192
$$

In words: every row costs its tuple length rounded up to 8 bytes, plus 4 bytes of line pointer, and the page has 8,168 bytes to spend. For `orders` the three statuses give tuples of 53, 56 and 57 bytes, stored as 56, 56 and 64, for an average of 62.7 bytes per row with its pointer. 8,168 / 62.7 = 130.3, so 130 rows per page and ⌈1,000,000 / 130⌉ = 7,693 pages. With `created` moved first, every tuple is 49 to 53 bytes, stored as 56, so each row costs 60 bytes: 136 rows per page, 7,353 pages. <!-- L05 --> <!-- L01 -->

### The TOAST threshold and chunk count

With 8 KB pages, a 24-byte header and 4 tuples per page as the design target:

$$
T = \mathrm{MAXALIGN\_DOWN}\!\left(\frac{8192 - \mathrm{MAXALIGN}(24 + 4 \times 4)}{4}\right) = \mathrm{MAXALIGN\_DOWN}(2038) = 2032
$$

That is the row width above which the toaster runs. The chunk size comes from the same budget, less a chunk row's own header and fields, and the chunk count follows from it:

$$
C = 2032 - 24 - 4 - 4 - 4 = 1996, \qquad \text{chunks}(n) = \left\lceil \frac{n}{C} \right\rceil
$$

The chunk budget spends 24 bytes on the chunk row's header, then 4 each on the value id, the sequence number and the chunk's own length word. For the note, n = 10,000 gives ⌈5.01⌉ = 6 chunks, five full and one of 20 bytes. In the lab's two-column table, a row is 32 bytes plus its value, so the first value to be TOASTed is 2,032 − 32 + 1 = 2,001 bytes. <!-- L66 --> <!-- L67 --> <!-- L17 --> <!-- L21 -->

### B-tree height

With L leaf pages and an average of f downlinks per internal page, a lookup reads one page per level:

$$
h = 1 + \left\lceil \log_{f} L \right\rceil
$$

Each level multiplies the number of reachable leaves by the fanout. The lab's index has L = 1,150 leaves, reached by 1,150 downlinks on its 5 level-1 pages (their 1,154 items include four high keys), so f = 230 and h = 1 + ⌈log₂₃₀ 1,150⌉ = 1 + 2 = 3: root, one internal page, one leaf. <!-- L26 --> <!-- L24 --> A hundred times more rows, 115,000 leaves, gives 1 + ⌈2.14⌉ = 4. A B-tree grows a level only when its data grows by a factor of the fanout.

### From an LSN to a file

With 16 MiB segments and timeline 1:

$$
s = \left\lfloor \frac{\mathrm{LSN}}{2^{24}} \right\rfloor, \qquad
\text{file} = \texttt{%08X}(1)\;\texttt{%08X}\!\left(\left\lfloor s/256 \right\rfloor\right)\;\texttt{%08X}(s \bmod 256), \qquad
\text{offset} = \mathrm{LSN} \bmod 2^{24}
$$

The high 32 bits of the LSN and the next 8 bits name the file, and the low 24 bits are the byte within it. For 3/F6D261D0: s = 0x3F6, the file is `0000000100000003000000F6`, and the offset is 0xD261D0 = 13,787,600, which is 1,683 WAL pages of 8,192 bytes plus 464. <!-- L85 --> <!-- L11 -->

### What the maps cost

The FSM stores ⌊free / 32⌋ per heap page, and the VM 2 bits per heap page:

$$
\text{FSM leaf pages} = \left\lceil \frac{P}{4069} \right\rceil, \qquad \text{VM pages} = \left\lceil \frac{P}{(8192 - 24) \times 4} \right\rceil = \left\lceil \frac{P}{32672} \right\rceil
$$

For P = 7,693 heap pages that is 2 FSM leaf pages, plus one level-1 page and the root, which makes the 4 pages (32,768 bytes) in the lab, and 1 VM page (8,192 bytes). <!-- L63 --> <!-- L116 --> <!-- L02 --> Past the first few pages, the FSM costs one page per 4,069 heap pages and the VM one per 32,672: about 0.025% and 0.003% of the table. That is why vacuum and the planner can afford to read them before touching a heap page.

## Implementation

The storage toolkit is a dozen queries. They need the contrib extensions `pageinspect`, `pg_visibility`, `pg_freespacemap` and `pg_walinspect` (15+), and most need superuser, because they read raw pages. <!-- L109 --> <!-- L124 --> Run them on a copy, never on a busy production table, since several read every page. The downloadable runner produced this post's numbers.

```sql
create extension if not exists pageinspect;
create extension if not exists pg_visibility;
create extension if not exists pg_freespacemap;
create extension if not exists pg_walinspect;

-- 1. Where a row lives, and the page around it.
select ctid from orders where id = 4242;                       -- (32,82)
select * from page_header(get_raw_page('orders', 32));
select lp, lp_off, lp_flags, lp_len, t_xmin, t_xmax, t_ctid,
       (select raw_flags from heap_tuple_infomask_flags(t_infomask, t_infomask2))
from heap_page_items(get_raw_page('orders', 32)) where lp = 82;

-- 2. Which files a table is, and how big each fork is.
select pg_relation_filepath('orders'),
       pg_relation_size('orders', 'main') as main, pg_relation_size('orders', 'fsm') as fsm,
       pg_relation_size('orders', 'vm') as vm,
       pg_relation_size(reltoastrelid) as toast
from pg_class where relname = 'orders';

-- 3. How often updates are HOT. A low ratio on a table with unindexed updates
--    means pages are too full: consider fillfactor.
select relname, n_tup_upd, n_tup_hot_upd,
       round(100.0 * n_tup_hot_upd / nullif(n_tup_upd, 0), 1) as hot_pct
from pg_stat_user_tables order by n_tup_upd desc limit 10;

-- 4. How much of a table vacuum and index-only scans can skip.
select * from pg_visibility_map_summary('orders');
select relname, relpages, relallvisible,
       round(100.0 * relallvisible / nullif(relpages, 0), 1) as pct_all_visible
from pg_class where relname = 'orders';

-- 5. Where a new row would go.
select * from pg_freespace('orders') where avail > 0 order by avail desc limit 5;

-- 6. What TOAST is holding, per column.
select pg_column_compression(note) as method, count(*),
       sum(octet_length(note)) as raw_bytes, sum(pg_column_size(note)) as stored_bytes
from orders where note is not null group by 1;

-- 7. The shape of a B-tree: levels, pages and fill. (bt_multi_page_stats is 16+.)
select * from bt_metap('orders_customer_idx');
select btpo_level, count(*) as pages, round(avg(free_size)) as avg_free
from bt_multi_page_stats('orders_customer_idx', 1, -1) group by 1 order by 1 desc;

-- 8. Where the log is, and what one statement wrote to it (psql: \gset keeps the LSN).
select pg_current_wal_lsn(), * from pg_walfile_name_offset(pg_current_wal_lsn());
select pg_current_wal_insert_lsn() as before \gset
update orders set status = status where id = 4242;     -- a no-op change, still a new version
select start_lsn, xid, resource_manager, record_type, record_length, fpi_length, block_ref
from pg_get_wal_records_info(:'before', pg_current_wal_insert_lsn());
```

Three more tools work from the shell, with the server's files:

```bash
pg_waldump -p "$PGDATA/pg_wal" -s 3/F6D261D0 -e 3/F6D26248   # records from segment files; use your own LSNs
pg_controldata "$PGDATA"                                     # REDO location, cluster state, system id
ls -l "$PGDATA/$(psql -Atc "select pg_relation_filepath('orders')")"*   # the table's files
```

Figure 22 maps each tool to the structure it reads.

![Grid of tools against on-disk structures: pageinspect reads heap pages, tuples, B-tree pages and FSM pages; pg_visibility reads the visibility map; pg_freespacemap reads the free space map; pg_walinspect and pg_waldump read WAL records; pg_controldata reads pg_control; pg_relation_filepath names the files; version markers show bt_multi_page_stats from 16 and pg_walinspect from 15](FIG_22)

*Figure 22 — Which tool reads which structure. Every one of them reads bytes that already exist; none changes anything on disk.*

Version notes for the queries above. `bt_multi_page_stats` arrived with pageinspect 1.12 in 16. On older servers, loop `bt_page_stats` over the blocks. <!-- L123 --> `pg_walinspect` needs 15 or later; before that, `pg_waldump` is the only way in. <!-- L124 --> On 18, `pd_checksum` in query 1 will usually be non-zero, because `initdb` enables data checksums by default. <!-- L104 --> The page, tuple, TOAST, FSM, VM and B-tree formats in this post are the same on 17 and 18. Two newer features read the same structures in new ways. 17 adds WAL summaries, which record the blocks changed in an LSN range so that `pg_basebackup` can take incremental backups. 18 adds skip scans of multicolumn B-trees. <!-- L108 -->

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** leaving `fillfactor` at 100 on a table whose rows are updated. A freshly loaded page is packed until no row fits, so the first update of each row cannot be HOT. It writes a new entry into every index, and it leaves a dead line pointer that only vacuum can clear. On the lab's `orders` that first update cost five log records and four pages, against two records and one page once the row sat on a page with room. `alter table orders set (fillfactor = 90)` leaves about 800 bytes on each page for new versions. The setting does not change existing pages by itself, so rewrite the table once if they matter. <!-- L07 --> <!-- L10 --> <!-- L50 --> <!-- L125 -->

**Indexing a column that every update changes.** An index on `status`, `updated_at` or a counter makes every update of that column non-HOT, whatever the fill factor, because HOT requires that no indexed column change. That includes columns that appear only in a partial index's `WHERE` clause. <!-- L48 --> <!-- L52 --> Before adding such an index, check `n_tup_hot_upd` against `n_tup_upd`.

**Reading `Heap Fetches` as an index problem.** A slow index-only scan with many heap fetches has a visibility-map problem, not an index problem: the pages it needs are not all-visible, and only vacuum sets the bits. <!-- L34 --> <!-- L57 --> On a table with frequent small changes, vacuum it more often, or accept that the scan is really an index scan.

**`SELECT *` on a table with large values.** An out-of-line value is fetched only if the query asks for the column. Selecting it anyway reads every chunk, and decompresses them if they were compressed: a 10,000-byte note is six extra chunk fetches per row. <!-- L114 --> <!-- L21 -->

**An `archive_command` that fails quietly, or that succeeds quietly without copying.** PostgreSQL trusts the exit status. A nonzero status makes it retry, while `pg_wal` keeps filling until its file system is full and the server shuts down with a PANIC, losing no committed transaction but staying down until space is freed. A zero status for a copy that did not happen means the segment is recycled and the archive has a hole in it. <!-- L94 --> <!-- L122 --> Test the command's failure path before relying on it.

**Treating `pg_wal` or `pg_xact` as logs you can delete.** They were renamed in 10 because people did exactly that and lost data. <!-- L47 --> A full disk is solved by fixing whatever is holding the segments, never by deleting them.

**Running without data checksums on 16 and earlier.** With checksums off, `pd_checksum` is 0 and a page corrupted on disk is read back without complaint. Checksums are chosen at `initdb`, or switched on offline with `pg_checksums`; 18 turns them on by default. <!-- L104 --> WAL protects against a crash, not against a drive that returns the wrong bytes, and not against one that reports writes it never made. <!-- L106 -->

**Assuming the relfilenode is the OID.** It usually is, until a `TRUNCATE`, `REINDEX`, `CLUSTER` or table-rewriting `ALTER TABLE`. Use `pg_relation_filepath()`, never a remembered number. <!-- L43 -->

**Ignoring column order on very large tables.** Padding before 8-byte columns is real space: 4.4% of `orders`. It is worth ordering columns widest-first when a table is created. It is rarely worth rewriting an existing table for. <!-- L05 -->

What this post, and the series, does not cover, by design: configuring streaming replication and failing over to a standby, logical decoding, the internals of GIN, GiST, BRIN and hash indexes, and table access methods other than the heap. Each is its own series. Part 1 covered memory and part 2 the processes that do the work.

## Key takeaways

- A ctid names a line pointer, not a tuple, and indexes point at line pointers. An update is HOT, touching no index, only if no indexed column changes and the page has room. At the default fill factor a row's first update usually is not. <!-- L39 --> <!-- L48 --> <!-- L07 -->
- The visibility map's two bits per page decide how much work vacuum does and whether an index-only scan reads the table. The lab saw 2 pages of 7,693 read, and 0 against 102,000 heap fetches. <!-- L14 --> <!-- L34 -->
- TOAST starts when a row passes 2,032 bytes. Compressible text stays in the row, compressed; incompressible text leaves an 18-byte pointer to ⌈n / 1,996⌉ chunks, and later updates of other columns copy only the pointer. <!-- L66 --> <!-- L17 --> <!-- L71 -->
- An LSN is a file name and a byte offset. Every WAL record carries a CRC-32C, and every page carries the LSN of its last change, which is what lets recovery replay the same record twice safely. <!-- L85 --> <!-- L87 --> <!-- L90 -->
- PostgreSQL's recovery is redo-only. Its buffer policy is steal and no-force, like ARIES, but uncommitted versions are simply invisible, a legacy of the 1987 no-overwrite design. That same choice is why vacuum has to exist. <!-- L93 --> <!-- L45 --> <!-- L96 -->

## Try it yourself

All three use the lab's `storelab` database, or any PostgreSQL 16 with `pageinspect`.

**1.** Without running anything, name the segment file and byte offset for the LSN 3/F6D69D50, the end of the crash step's `HOT_UPDATE`. Then check with `pg_walfile_name_offset`.

<details><summary>Answer</summary>

s = 0x3F6D69D50 ÷ 2²⁴ = 0x3F6, so the file is `0000000100000003000000F6`, the same segment as the second update. The offset is 0xD69D50 = 14,064,976, which is WAL page 1,716 (14,057,472) plus 7,504 bytes. `pg_walfile_name_offset('3/F6D69D50')` returns the same pair.

</details>

**2.** A table has columns `(id int, body text)`. Predict what happens to a 1,900-byte `body` and to a 5,000-byte `body` of random base64 text, then insert both and check with `pg_column_size` and the TOAST table.

<details><summary>Answer</summary>

The row is 24 + 4 + 4 + n bytes. At 1,900 bytes it is 1,932, under the 2,032-byte threshold, so it stays inline and uncompressed. At 5,000 bytes it is 5,032, so the toaster runs. Random base64 cannot shrink by 25%, so the value goes out of line: the tuple becomes 46 bytes, and the value is split into ⌈5,000 / 1,996⌉ = 3 chunks, of 1,996, 1,996 and 1,008 bytes.

</details>

**3.** After the lab's vacuums, page 32 of `orders` has an 80-byte hole and one unused line pointer (slot 82). Row 4243, `(32,83)`, has status `shipped`. Will `update orders set status = 'paid' where id = 4243` be HOT, and at what ctid will the new version land?

<details><summary>Answer</summary>

Yes. The new tuple is 53 bytes, stored as 56. Slot 82 is unused and can be reused, so no new line pointer is needed, and 56 ≤ 80. No indexed column changes. The new version lands at `(32,82)`, the slot row 4242 vacated, and `n_tup_hot_upd` goes up by one. Try it inside `begin; ... rollback;` to leave the lab as it was.

</details>

## References

Grouped by tier. Accessed 2026-09-24 except where noted. The lab files are listed first.

### Lab downloads

- [`README.md`](LAB_01) — prerequisites, safe setup, run order, what each step captures, and cleanup.
- [`run_lab.py`](LAB_02) — builds the tables and runs every experiment in this post, from the page decode to the crash and replay.
- [`captures.md`](LAB_03) — the readable output of the run this post quotes, psql transcripts in order.
- [`captures.json`](LAB_04) — the same run's numbers in machine-readable form, the input to every figure.

### Sources

**T1 — papers and standards**

- Stonebraker, M. *The Design of the POSTGRES Storage System.* Proc. 13th VLDB, Brighton, 1987, pp. 289–300. https://www.vldb.org/conf/1987/P289.PDF
- Stonebraker, M., Rowe, L. A., Hirohama, M. *The Implementation of POSTGRES.* IEEE TKDE 2(1), 1990. doi:10.1109/69.50912. https://dsf.berkeley.edu/papers/ERL-M90-34.pdf
- Mohan, C., Haderle, D., Lindsay, B., Pirahesh, H., Schwarz, P. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging.* ACM TODS 17(1), 1992. doi:10.1145/128765.128770
- Lehman, P. L., Yao, S. B. *Efficient Locking for Concurrent Operations on B-Trees.* ACM TODS 6(4), 1981. doi:10.1145/319628.319663
- Bayer, R., McCreight, E. *Organization and Maintenance of Large Ordered Indexes.* Acta Informatica 1(3), 1972. doi:10.1007/BF00288683
- Comer, D. *The Ubiquitous B-Tree.* ACM Computing Surveys 11(2), 1979. doi:10.1145/356770.356776
- Wu, Y., Arulraj, J., Lin, J., Xian, R., Pavlo, A. *An Empirical Evaluation of In-Memory Multi-Version Concurrency Control.* PVLDB 10(7), 2017. doi:10.14778/3067421.3067427. https://www.vldb.org/pvldb/vol10/p781-Wu.pdf
- Ziv, J., Lempel, A. *A Universal Algorithm for Sequential Data Compression.* IEEE Trans. Information Theory 23(3), 1977. doi:10.1109/TIT.1977.1055714
- RFC 3720, *Internet Small Computer Systems Interface (iSCSI)*, 2004, §12.1 and Appendix B.4 (CRC32C). https://www.rfc-editor.org/rfc/rfc3720
- IEEE Std 1003.1-2017 (POSIX), `fsync()`. https://pubs.opengroup.org/onlinepubs/9699919799/functions/fsync.html

**T2 — PostgreSQL documentation and release notes**

- PostgreSQL 16 docs, ch. 73 Database Physical Storage: §73.1 File Layout, §73.2 TOAST, §73.3 Free Space Map, §73.4 Visibility Map, §73.6 Page Layout, §73.7 HOT. https://www.postgresql.org/docs/16/storage.html
- PostgreSQL 16 docs, ch. 30 Reliability and the Write-Ahead Log (§30.2 Data Checksums, §30.3 WAL, §30.6 WAL Internals). https://www.postgresql.org/docs/16/wal.html
- PostgreSQL 16 docs, §26.3 Continuous Archiving and Point-in-Time Recovery. https://www.postgresql.org/docs/16/continuous-archiving.html
- PostgreSQL 16 docs, §27.2 Log-Shipping Standby Servers. https://www.postgresql.org/docs/16/warm-standby.html
- PostgreSQL 16 docs, §67.4 B-Tree Implementation. https://www.postgresql.org/docs/16/btree-implementation.html
- PostgreSQL 16 docs, ALTER TABLE. https://www.postgresql.org/docs/16/sql-altertable.html
- PostgreSQL 16 docs, pageinspect, pg_visibility, pg_freespacemap, pg_walinspect. https://www.postgresql.org/docs/16/pageinspect.html
- PostgreSQL release notes: 7.1, 8.3, 8.4, 9.2, 9.3, 9.6, 10, 11, 13, 14, 15, 17, 18. https://www.postgresql.org/docs/release/

**T3 — source code (tag REL_16_2)**

- `src/include/storage/bufpage.h`, `itemid.h`; `src/include/access/htup_details.h`, `heaptoast.h`, `xlog_internal.h`, `xlogrecord.h`, `rmgrlist.h`, `nbtree.h`; `src/include/varatt.h`. https://github.com/postgres/postgres/tree/REL_16_2/src/include
- `src/backend/access/heap/README.HOT`, `heapam.c`, `heapam_visibility.c`, `hio.c`, `pruneheap.c`, `vacuumlazy.c`, `visibilitymap.c`. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/access/heap
- `src/backend/access/nbtree/README`, `nbtsplitloc.c`. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/access/nbtree
- `src/backend/storage/freespace/README`, `freespace.c`; `src/include/storage/fsm_internals.h`. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/storage/freespace
- `src/backend/access/transam/xlog.c`, `xlogreader.c`, `xlogutils.c`, `clog.c`. https://github.com/postgres/postgres/tree/REL_16_2/src/backend/access/transam
- `src/common/pg_lzcompress.c`; `src/port/pg_crc32c_sb8.c`; `contrib/pageinspect/pageinspect--1.11--1.12.sql`. https://github.com/postgres/postgres/tree/REL_16_2

**T4 — practitioner writing (framing only)**

- Klitzke, E. *Why Uber Engineering Switched from Postgres to MySQL.* Uber blog, 2016. https://www.uber.com/blog/postgres-to-mysql-migration/

**This series**

- Part 1 — *How PostgreSQL Uses Memory.* https://canery.in/blogs/postgresql-foundations-memory-layer
- Part 2 — *How PostgreSQL Uses Processes.* https://canery.in/blogs/postgresql-foundations-process-layer
