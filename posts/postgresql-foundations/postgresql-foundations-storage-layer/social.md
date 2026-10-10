---
social_schema: 2
canonical_url: "https://canery.in/blogs/postgresql-foundations-storage-layer"
---

# Social publishing package — postgresql-foundations-storage-layer

## LinkedIn post

I followed one row of a PostgreSQL table from its first byte to crash recovery, on a real server.

Two updates changed the same unindexed column. The first could not stay on its page (24 bytes free), so it wrote 322 bytes of WAL and a new entry in both indexes. The second was HOT: 111 bytes, no index touched.

Vacuum then read 2 of the table's 7,693 pages, because the visibility map said the rest were clean. The same map turned an index-only count into 102,000 heap fetches until vacuum set it again.

A 2,000-byte value stayed in its row; 2,001 bytes did not. And after an immediate shutdown, the committed change existed only in the write-ahead log, which was enough.

Part 3 of PostgreSQL Foundations, the storage layer. Swipe through the six cards; the link is in the first comment.

## LinkedIn first comment

Everything PostgreSQL keeps on disk is data, a map of the data, or the log, and every one of the surprises above is one of those three doing its job.

Read the full article on Canery: https://canery.in/blogs/postgresql-foundations-storage-layer

## Instagram caption

One PostgreSQL row, followed byte by byte: a non-HOT update that paid for both indexes, a vacuum that read 2 pages of 7,693, a 2,001-byte value that left its row, and a crash that lost nothing because the log had it. Part 3 of PostgreSQL Foundations, the storage layer. Full article on canery.in, link in bio.

## Shared feed order

1. `assets/social/feed-01-data-maps-log.png` — Everything on disk is data, a map of the data, or the log.
2. `assets/social/feed-02-not-hot.png` — The first update was not HOT because its page was full; the second was.
3. `assets/social/feed-03-two-pages.png` — The visibility map lets vacuum skip every all-visible page.
4. `assets/social/feed-04-heap-fetches.png` — An index-only scan visits the heap for every page the visibility map does not mark all-visible.
5. `assets/social/feed-05-toast-cliff.png` — TOAST compresses or moves values once a row passes 2,032 bytes.
6. `assets/social/feed-06-only-in-the-log.png` — Crash recovery replays WAL from the checkpoint's REDO point onto pages that missed it.

## Instagram Story

- CTA: Read how PostgreSQL stores a row, and gets it back after a crash
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### Story order

1. `assets/social/story-01-data-maps-log.png` — Overlay: Everything on disk is data, a map, or the log
2. `assets/social/story-02-not-hot.png` — Overlay: Why the first update wrote to both indexes
3. `assets/social/story-03-two-pages.png` — Overlay: 2 of 7,693 pages: the visibility map at work
4. `assets/social/story-04-only-in-the-log.png` — Overlay: Nothing committed was lost. Read how →

## Asset metadata

### feed-01-data-maps-log

- File: `assets/social/feed-01-data-maps-log.png`
- Title: What PostgreSQL keeps on disk
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Everything on disk is data, a map of the data, or the log.
- Technical source: Intuition section; Figure 2 and Figure 4; ledger L02
- Visual structure: Headline and setup at top; a panel with three labelled rows (data tiles, two map strips, a dotted log line) with sizes; takeaway and footer below.
- Visible-text transcript: What PostgreSQL keeps on disk · Data, two maps of the data, and one log. One real row shows all three. · DATA · heap: 7,693 pages, 63,021,056 bytes · indexes and TOAST chunks: the same 8 KB page format · MAPS · visibility map: 2 bits per page, 8,192 bytes · free space map: 1 byte per page, 32,768 bytes · LOG · WAL: 16 MiB segment files, every change in order · Every storage surprise is one of these three doing its job. · POSTGRESQL FOUNDATIONS · PART 3 · CANERY.IN
- Alt text: PostgreSQL's on-disk storage as three kinds: a 7,693-page heap, two small map forks of 8 and 32 KB, and a log of 16 MiB segments.
- Long description: Cover card for the storage-layer article. A grid of page tiles stands for the orders heap, 7,693 pages or 63,021,056 bytes, with one tile highlighted as the page that changes. Two small squares stand for the visibility map (2 bits per heap page, 8,192 bytes) and the free space map (1 byte per heap page, 32,768 bytes). A dotted line stands for the write-ahead log, stored as 16 MiB segment files. The takeaway: every storage-layer surprise is one of these three structures doing its job.
- Keywords: PostgreSQL, storage layer, heap, visibility map, free space map, WAL
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### feed-02-not-hot

- File: `assets/social/feed-02-not-hot.png`
- Title: Same change, three times the log
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The first update was not HOT because its page was full; the second was.
- Technical source: HOT section; Figure 10; ledger L07, L10
- Visual structure: Headline and setup; two stacked horizontal bars split into WAL records, to scale; a line naming the free space on page 32; takeaway.
- Visible-text transcript: Same change, three times the log · Two status updates to one row of orders. The first could not stay on its page. · update 1 · not HOT · LOCK 54 B · UPDATE 106 B · INSERT_LEAF 64 B · INSERT_LEAF 64 B · 322 bytes · 5 records · 4 pages: both heap pages, one leaf in each index · update 2 · HOT · HOT_UPDATE 77 B · 111 bytes · 2 records · 1 page: heap page 7692 · page 32 had 24 bytes free; the new version needed 60 · HOT needs an unindexed change and room on the same page.
- Alt text: Two WAL bars for the same status update: 322 bytes in five records across four pages when not HOT, 111 bytes in two records when HOT.
- Long description: Two updates changed the unindexed status column of row 4242. The first found only 24 bytes free on page 32, so its new version went to page 7692 and needed a new entry in both indexes: LOCK 54 B, UPDATE 106 B, two INSERT_LEAF records of 64 B, and COMMIT 34 B, 322 bytes in five records touching four pages. The second update found room on page 7692 and was HOT: HOT_UPDATE 77 B and COMMIT 34 B, 111 bytes on one page. PostgreSQL 16.2, lab measurement.
- Keywords: PostgreSQL, HOT update, heap-only tuple, WAL, fillfactor, indexes
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### feed-03-two-pages

- File: `assets/social/feed-03-two-pages.png`
- Title: Vacuum read 2 of 7,693 pages
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: The visibility map lets vacuum skip every all-visible page.
- Technical source: The visibility map section; Figure 11; ledger L14, L60
- Visual structure: Headline and setup; a long band for the table's pages with two tangerine ticks; a monospace box quoting VACUUM VERBOSE; takeaway.
- Visible-text transcript: Vacuum read 2 of 7,693 pages · The visibility map told it the other 7,691 pages had nothing to clean. · the all-visible bit of each of 7,693 pages · page 32 · page 7692 · only these two pages had anything to clean · VACUUM (VERBOSE) orders · pages: 0 removed, 7693 remain, 2 scanned (0.03% of total) · Two bits per page decide how much vacuum has to read.
- Alt text: A band of 7,693 visibility-map bits with only pages 32 and 7692 clear, and VACUUM VERBOSE reporting 2 pages scanned.
- Long description: After two updates, only heap pages 32 and 7692 of the orders table had their visibility-map all-visible bit cleared. VACUUM (VERBOSE) reported: pages: 0 removed, 7693 remain, 2 scanned (0.03% of total). The visibility map keeps two bits per heap page, all-visible and all-frozen, set only by vacuum and cleared by any change. Vacuum skips runs of 32 or more all-visible pages.
- Keywords: PostgreSQL, vacuum, visibility map, all-visible, VACUUM VERBOSE
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### feed-04-heap-fetches

- File: `assets/social/feed-04-heap-fetches.png`
- Title: 102,000 visits to the heap
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: An index-only scan visits the heap for every page the visibility map does not mark all-visible.
- Technical source: The visibility map section; Figure 12; ledger L34
- Visual structure: Headline and setup; three vertical bars of heap fetches with buffer counts beneath; takeaway.
- Visible-text transcript: 102,000 visits to the heap · The same index-only count, before and after one row in fifty was updated. · heap fetches in EXPLAIN (ANALYZE, BUFFERS) · 0 · all-visible · 118 buffers · 102,000 · 1 row in 50 updated · 102,118 buffers · 0 · after vacuum · 118 buffers · Heap Fetches in EXPLAIN is the visibility map's report card.
- Alt text: Heap fetches for one index-only count: 0 when all-visible, 102,000 after updating one row in fifty, and 0 again after vacuum.
- Long description: An index-only count of 100,000 rows on a 7,847-page copy of orders, run three times with the plan forced to an index-only scan. With every page all-visible it fetched 0 heap tuples and touched 118 buffers. After updating one row in fifty, which cleared the visibility bit on every page, it made 102,000 heap fetches and touched 102,118 buffers. After vacuum it was back to 0 fetches and 118 buffers. PostgreSQL 16.2.
- Keywords: PostgreSQL, index-only scan, Heap Fetches, visibility map, EXPLAIN
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### feed-05-toast-cliff

- File: `assets/social/feed-05-toast-cliff.png`
- Title: 2,000 bytes stays. 2,001 leaves.
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: TOAST compresses or moves values once a row passes 2,032 bytes.
- Technical source: TOAST section; Figure 14 and Figure 15; ledger L17, L18
- Visual structure: Headline and setup; a three-row table of value size against what compressible and incompressible text become; takeaway.
- Visible-text transcript: 2,000 bytes stays. 2,001 leaves. · A row wider than 2,032 bytes wakes the toaster. Then it depends on the text. · value size · compressible text · hex text (won't compress) · 2,000 B · inline · 2,004 B · inline · 2,004 B · 2,001 B · 51 B · pglz · 18 B pointer · 2 chunks · 10,000 B · 142 B · pglz · 18 B pointer · 6 chunks · the toaster wakes when the row passes 2,032 bytes · Compress by a quarter and stay; otherwise leave an 18-byte pointer.
- Alt text: What a text value becomes in its row: 2,000 bytes stays inline; at 2,001 it compresses to 51 bytes or leaves an 18-byte pointer.
- Long description: Measured on an (int, text) table in PostgreSQL 16.2. A 2,000-byte value makes a 2,032-byte row and stays inline. At 2,001 bytes the toaster runs: compressible text becomes 51 bytes of pglz output inline, and hex text, which pglz cannot shrink by the required 25%, moves out of line behind an 18-byte pointer in two chunks. At 10,000 bytes compressible text is 142 bytes inline; hex text is six chunks of at most 1,996 bytes.
- Keywords: PostgreSQL, TOAST, pglz, TOAST pointer, chunks, varlena
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### feed-06-only-in-the-log

- File: `assets/social/feed-06-only-in-the-log.png`
- Title: The change was only in the log
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: Crash recovery replays WAL from the checkpoint's REDO point onto pages that missed it.
- Technical source: Crash recovery section; Figure 20; ledger L29–L31
- Visual structure: Headline and setup; five stacked monospace facts joined by arrows from before the crash to after replay; call to action.
- Visible-text transcript: The change was only in the log · A commit, then a crash. The table file was still one change behind. · before the crash, in memory · pd_lsn 3/F6D69D50 · the same page in the table file · pd_lsn 3/F6D42F28 · restart: redo starts at · 3/F6D691A0 · end of WAL · zero-length record at 3/F6D69D78 · after replay, the table file · pd_lsn 3/F6D69D50 · amount 60000 · Read the whole walk-through, byte by byte, on canery.in
- Alt text: Crash replay in five lines: page LSN in memory ahead of the file, redo from the REDO point, end of WAL, file caught up.
- Long description: After a committed update and an immediate shutdown, page 7692 in memory carried pd_lsn 3/F6D69D50, while the same page in the table file still said 3/F6D42F28 and had one line pointer fewer. On restart the startup process replayed WAL from the checkpoint's REDO location 3/F6D691A0, stopped at a zero-length record at 3/F6D69D78, and the end-of-recovery checkpoint wrote the page: its file copy then read 3/F6D69D50 and the row's amount was 60000. Call to action to read the article.
- Keywords: PostgreSQL, crash recovery, WAL, REDO, pd_lsn, LSN
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### story-01-data-maps-log

- File: `assets/social/story-01-data-maps-log.png`
- Title: What PostgreSQL keeps on disk
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: Story opener: the three kinds of on-disk structure, each with its real size.
- Technical source: Intuition section; Figure 2 and Figure 4; ledger L02
- Visual structure: Hook headline, setup line, a tall panel with the three labelled groups and their sizes, takeaway, footer.
- Visible-text transcript: What PostgreSQL keeps on disk · Data, two maps, and a log. · DATA · heap: 7,693 pages, 63,021,056 bytes · indexes and TOAST chunks: the same 8 KB page format · MAPS · visibility map: 2 bits per page, 8,192 bytes · free space map: 1 byte per page, 32,768 bytes · LOG · WAL: 16 MiB segment files, every change in order · One real row, followed byte by byte. · POSTGRESQL FOUNDATIONS · PART 3 · CANERY.IN
- Alt text: Story cover: PostgreSQL's on-disk storage as heap pages, two small map forks of 8 and 32 KB, and a log of 16 MiB segment files.
- Long description: Story cover, recomposed for 9:16. Three labelled groups fill a tall panel: page tiles for the 7,693-page orders heap (63,021,056 bytes) with one highlighted, two small squares for the visibility map (8,192 bytes, 2 bits per page) and the free space map (32,768 bytes, 1 byte per page), and a dotted line for the write-ahead log in 16 MiB segments. The frame promises one real row followed byte by byte.
- Keywords: PostgreSQL, storage layer, heap, visibility map, free space map, WAL
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### story-02-not-hot

- File: `assets/social/story-02-not-hot.png`
- Title: Same change, three times the log
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story beat: a full page forced the first update off its page and into both indexes.
- Technical source: HOT section; Figure 10; ledger L07, L10
- Visual structure: Headline and setup; two stacked horizontal bars split into WAL records, to scale; a line naming the free space on page 32; takeaway.
- Visible-text transcript: Same change, three times the log · The first update could not stay on its page. · update 1 · not HOT · LOCK 54 B · UPDATE 106 B · INSERT_LEAF 64 B · INSERT_LEAF 64 B · 322 bytes · 5 records · 4 pages: both heap pages, one leaf in each index · update 2 · HOT · HOT_UPDATE 77 B · 111 bytes · 2 records · 1 page: heap page 7692 · page 32 had 24 bytes free; the new version needed 60 · HOT needs room on the same page.
- Alt text: Story frame: the first status update cost 322 bytes of WAL on four pages, the HOT one 111 bytes on one page.
- Long description: Story version of the update comparison. The non-HOT update of row 4242 wrote LOCK, UPDATE, two INSERT_LEAF records and COMMIT, 322 bytes on two heap pages and one leaf of each index, because page 32 had only 24 bytes free. The HOT update wrote HOT_UPDATE and COMMIT, 111 bytes on heap page 7692 alone. Lab measurement on PostgreSQL 16.2.
- Keywords: PostgreSQL, HOT update, heap-only tuple, WAL, fillfactor, indexes
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### story-03-two-pages

- File: `assets/social/story-03-two-pages.png`
- Title: Vacuum read 2 of 7,693 pages
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: Story beat: two clear visibility bits, two pages read by vacuum.
- Technical source: The visibility map section; Figure 11; ledger L14, L60
- Visual structure: Headline and setup; a long band for the table's pages with two tangerine ticks; a monospace box quoting VACUUM VERBOSE; takeaway.
- Visible-text transcript: Vacuum read 2 of 7,693 pages · The visibility map skipped the rest. · the all-visible bit of each of 7,693 pages · page 32 · page 7692 · only these two pages had anything to clean · VACUUM (VERBOSE) orders · pages: 0 removed, 7693 remain, 2 scanned (0.03% of total) · Two bits per page decide what vacuum reads.
- Alt text: Story frame: the table's 7,693 visibility bits drawn as a band with two clear, and vacuum reporting 2 pages scanned.
- Long description: Story version of the vacuum result. A band stands for all 7,693 visibility-map bits of orders; only the bits for pages 32 and 7692 are clear, because only those pages changed. A monospace box quotes VACUUM (VERBOSE): 0 pages removed, 7693 remain, 2 scanned, 0.03% of the table. The takeaway: the map's two bits per page decide what vacuum reads.
- Keywords: PostgreSQL, vacuum, visibility map, all-visible, VACUUM VERBOSE
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer

### story-04-only-in-the-log

- File: `assets/social/story-04-only-in-the-log.png`
- Title: The change was only in the log
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: Story close: nothing committed was lost, and the link to the article.
- Technical source: Crash recovery section; Figure 20; ledger L29–L31
- Visual structure: Headline and setup; five stacked monospace facts joined by arrows from before the crash to after replay; call to action and a link sticker area.
- Visible-text transcript: The change was only in the log · And the log was enough. · before the crash, in memory · pd_lsn 3/F6D69D50 · the same page in the table file · pd_lsn 3/F6D42F28 · restart: redo starts at · 3/F6D691A0 · end of WAL · zero-length record at 3/F6D69D78 · after replay, the table file · pd_lsn 3/F6D69D50 · amount 60000 · Read the article: link sticker below. · POSTGRESQL FOUNDATIONS · PART 3 · CANERY.IN
- Alt text: Story close: crash replay in five lines, page LSN in memory ahead of the file, then replayed from the REDO point until caught up.
- Long description: Story close, recomposed for 9:16. Five stacked facts from the lab's crash: the page's LSN in memory (3/F6D69D50) ahead of its file copy (3/F6D42F28); replay starting at the REDO point 3/F6D691A0; the log ending at a zero-length record at 3/F6D69D78; and the file caught up at 3/F6D69D50 with the committed amount of 60000. The frame leaves room for the link sticker to the article.
- Keywords: PostgreSQL, crash recovery, WAL, REDO, pd_lsn, LSN
- Canonical URL: https://canery.in/blogs/postgresql-foundations-storage-layer
