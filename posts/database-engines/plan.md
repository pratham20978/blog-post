# Series plan — Database Engines Beyond PostgreSQL

**Slug:** database-engines · **Shape:** hybrid · **Parts:** 20 · **Status:** Checkpoint S — awaiting approval (planned 2026-09-29) · **Sibling of:** `postgresql-foundations`

## Why this is its own series, not part of PostgreSQL Foundations

The PostgreSQL series decomposes one codebase on one real server. Its invariant is that every number comes from a real PostgreSQL lab (16.2 for Parts 1–3, 18.x after), and its promise is that a reader can explain any PostgreSQL surprise by naming the layer it lives in. The engines here are built on the opposite decisions:
- updating in place with an undo log (InnoDB, DuckDB);
- log-structured merges instead of an updated B-tree and heap (RocksDB, Cassandra, Lucene, Prometheus);
- column layout instead of heap tuples (ClickHouse, DuckDB);
- memory as the store (Redis) and an in-memory page format unlike disk (WiredTiger);
- pointer adjacency (Neo4j) and approximate graph search (vector databases);
- leaderless quorums or per-range consensus instead of one primary shipping WAL (Cassandra, etcd, CockroachDB, TiDB, Spanner).

Each needs its own server, lab and mental model. Folding them into the PG series would either turn PG parts into comparisons, breaking the shared lab, tables and promise, or reduce the engines to footnotes.

What carries over from PG Parts 1–3 is the baseline each contrast is measured against:
- pages, buffers and usage-count eviction (Part 1) → InnoDB's buffer pool, Redis eviction, the WiredTiger cache;
- WAL-before-data and full-page images (Part 1) → InnoDB redo and doublewrite, the RocksDB WAL, SQLite's journal and WAL, the Elasticsearch translog;
- the process cast, what a commit waits for, and the xmin horizon (Part 2) → SQLite's single writer and checkpoint starvation, Raft's majority commit, MongoDB's history store under a long transaction;
- the heap page, tuple header, xmin/xmax visibility, HOT, the visibility map, TOAST, the B-tree walk and split, LSNs and redo-only recovery (Part 3) → InnoDB's undo MVCC and clustered index, LSM versus B-tree, columnar layout, TSDB bytes per sample, Lucene postings, graph hops, distributed timestamps.

Every part here names one of those as its baseline and links it by anchor instead of re-teaching it.

## Shape

Hybrid. Part 1 is a hub: it holds the design-space map and the only side-by-side measurement. The spokes cut "database engines" into families at their own depth. Each spoke is anchored on one named PostgreSQL mechanism rather than on the hub, so a reader can land on any spoke from search. Short ladders sit inside it only where a family's second question needs the first one's answer: 5→6 (LSM mechanism, then compaction), 11→12 (column layout, then vectorized execution), 15→16 (the ring, then modeling for it), and 17→18 and 17→20 (consensus, then distributed transactions and consistency testing). Ladder rungs re-teach their prerequisite in one paragraph. Spokes assume the PG baseline and link to it by anchor. The plan has 19 committed parts plus 1 optional (20). Difficulty never drops along a ladder: 5 intermediate→6 advanced, 11 intermediate→12 advanced, 15→16 both intermediate, 17→18/20 all advanced. Adjacent option, overrulable in one word: a 14-part cut that merges 3+4, 5+6, 11+12 and 15+16 into single L4 pillars and drops 13 and 20. It is shorter, but each merged pillar would run past 12,000 words and lose one search intent.

## Arcs

| Parts | Arc | Purpose |
|---|---|---|
| 1 | Hub | The five decisions every engine makes (where a changed row goes, where old versions live, row or column layout, what the durability unit is, how many machines agree on a write), measured once across engines. Each later part is one pin on this map. |
| 2-6 | Single-node storage engines | The update strategies that differ from PostgreSQL's append-only heap: an in-place B-tree coordinated by a file lock (SQLite), in-place updates with an undo log (InnoDB, two parts), and log-structured merges (LSM/RocksDB, two parts). These form the base that later spokes and the distributed arc build on. |
| 7-14 | Purpose-built engines | Engines built around one data shape or access pattern, each contrasted with the PG mechanism it replaces: RAM as the store (Redis), documents (MongoDB/WiredTiger), text (Lucene/Elasticsearch/OpenSearch), vectors, columns (ClickHouse storage, DuckDB execution), time series (Prometheus TSDB) and graphs (Neo4j). |
| 15-20 | Distributed engines | What changes when more than one machine must agree: leaderless quorums (Cassandra/Dynamo), modeling data for a partition key, consensus inside the database (Raft, MongoDB replica sets), distributed SQL transactions (CockroachDB, TiDB, YugabyteDB, Spanner), timestamps without one clock, and, as optional part 20, testing the consistency claims yourself. |

## Reading paths

- **From little SQL to engine literacy** (A developer who knows little SQL and wants the map before the internals): the PG spine's from-scratch entry part(s) (planned separately) → 1 → 2 → 7 → 8 → 16 → 9
- **Storage-engine internals** (Engineers who finished PG Parts 1–3 and want the other update strategies): PG Part 3 → 1 → 3 → 4 → 5 → 6 → 11 → 12
- **Choosing and running an application datastore** (Backend engineers picking or operating Redis, MongoDB, Elasticsearch/OpenSearch, Cassandra or DynamoDB): 1 → 7 → 8 → 9 → 15 → 16 → 10
- **Distributed databases** (Engineers and SREs running replicated or geo-distributed systems): PG Part 2 → 17 → 18 → 19 → 15 → 20 (optional)
- **Analytics and observability** (Data and platform engineers): 1 → 11 → 12 → 13, then `data-at-scale`
- **Search and AI retrieval** (Engineers building search, RAG or recommendation): PG Part 3 → 9 → 10 → 14
- **MySQL and PostgreSQL side by side** (DBAs migrating between MySQL and PostgreSQL or running both): PG Part 3 → 3 → 4 → 2

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | place any engine on five decisions: where a changed row goes, where old versions live, row or column layout, the durability unit, and how many machines agree on a write | 1 |
| 2 | count the bytes one update writes in an engine and turn the counts into write, space and read amplification | 1 |
| 3 | explain how SQLite serializes writers with file locks and why WAL mode lets readers run beside one writer | 2 |
| 4 | diagnose SQLITE_BUSY and a WAL file that never shrinks, and fix both | 2 |
| 5 | follow an InnoDB record's hidden transaction id and roll pointer into the undo log | 3 |
| 6 | predict when purge lag (history list length) grows and what it slows | 3 |
| 7 | say which anomaly MySQL REPEATABLE READ allows that PostgreSQL's rejects | 3 |
| 8 | trace one commit through redo, binlog and their two-phase commit, and choose flush settings from what a process crash versus an OS crash loses | 4 |
| 9 | explain why InnoDB needs a doublewrite buffer where PostgreSQL writes full-page images, and compare midpoint-insertion LRU with the clock sweep and rings | 4 |
| 10 | trace a put and a get through WAL, memtable, L0 and levelled SSTs | 5 |
| 11 | size a bloom filter from a target false-positive rate | 5 |
| 12 | choose leveled, tiered or FIFO compaction from a workload's write, read and space budget | 6 |
| 13 | predict and relieve a write stall, and explain why tombstones slow range scans | 6 |
| 14 | estimate Redis memory per key and predict an encoding switch | 7 |
| 15 | choose a Redis eviction policy and sample size from measured hit ratios | 7 |
| 16 | say which acknowledged writes RDB, AOF and async replication can lose | 7 |
| 17 | explain why WiredTiger's cache holds a different format than disk and recognize eviction stalls | 8 |
| 18 | predict the write cost of changing one field of a large document in MongoDB versus PG JSONB with TOAST | 8 |
| 19 | explain how Lucene finds and scores documents for a term through the term dictionary, postings and BM25 | 9 |
| 20 | set refresh interval, translog durability and merge policy from the visibility versus durability trade | 9 |
| 21 | choose HNSW, IVF-PQ or a disk-based index from recall, latency and memory budgets, and compute the footprint before building | 10 |
| 22 | explain why filtered vector search loses recall and how filter-aware engines recover it | 10 |
| 23 | predict the granules a ClickHouse query reads from its ORDER BY key | 11 |
| 24 | explain why an UPDATE in a column store is a mutation that rewrites parts | 11 |
| 25 | distinguish tuple-at-a-time, vectorized and compiled execution and measure the difference | 12 |
| 26 | explain why morsel-driven parallelism scales across cores where a PG gather plan is capped by its workers | 12 |
| 27 | compute bytes per sample for delta-of-delta and XOR encoding versus a PG row | 13 |
| 28 | predict TSDB memory from series cardinality and spot a cardinality explosion | 13 |
| 29 | compare a graph traversal's pointer chases with a recursive CTE's index descents, depth by depth | 14 |
| 30 | say when a graph database is the wrong tool | 14 |
| 31 | predict what a read at ONE, QUORUM and ALL returns with a replica partitioned | 15 |
| 32 | explain hinted handoff, read repair, anti-entropy repair, last-write-wins loss under skew and zombie deletes after gc_grace_seconds | 15 |
| 33 | design Cassandra and DynamoDB tables from a list of access patterns | 16 |
| 34 | detect and fix a hot or oversized partition | 16 |
| 35 | trace a Raft election and commit, and predict commit latency from follower round-trip times | 17 |
| 36 | choose MongoDB write and read concern from which writes may be rolled back | 17 |
| 37 | explain how a distributed SQL database splits, replicates and rebalances ranges | 18 |
| 38 | count the consensus rounds a multi-range transaction pays under parallel commits and under Percolator | 18 |
| 39 | explain TrueTime commit wait, HLC uncertainty restarts and a timestamp oracle's round trip, and the cost of each per commit | 19 |
| 40 | build a history-checked consistency test with real partitions on one machine and read a Jepsen report | 20 |

## Parts

### Part 1 — The Five Decisions Behind Every Database Engine

- **Slug:** five-decisions-behind-every-database-engine · **Arc:** Hub · **Status:** planned
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 4,800 · **Figures:** 8
- **Answers:** What few design decisions separate every database engine from PostgreSQL, and how do you read an engine's trade-offs off them?
- **Assumes:** None. Re-states PostgreSQL's baseline (append-only heap, one WAL, one primary) in one paragraph and links to PG Part 1 #a-two-byte-update-that-cost-7544-bytes, which is live.
- **Hands off:** Every engine's mechanism goes to its spoke. The map names families, not post titles, and links a spoke only once that spoke is live.
- **Worked example:** One row of orders (id 4242, the row PG Part 3 decodes) is updated once, then 1,000,000 random rows are updated, in SQLite (rollback journal and WAL mode), LMDB (copy-on-write B+tree), RocksDB (LSM) and DuckDB (columnar with undo buffers). For each engine the lab counts write syscalls, bytes written and fsyncs with strace -f -c plus file-size deltas, the file size after the run, and the pages or blocks read for one point lookup. The result is one table of write, space and read amplification. PostgreSQL's row in that table is quoted from its own series: 7,544 bytes of WAL for a two-byte change after a checkpoint (PG Part 1), plus 322 B non-HOT versus 111 B HOT once PG Part 3 is live.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E3; access: none. One Python script in the engines-lab uv venv (stdlib sqlite3 3.46.1, plus the lmdb, rocksdict and duckdb wheels), run under strace. It writes captures.md with the amplification table. No server and no PostgreSQL connection. strace counting a child's pwrite64 and fdatasync calls was verified on this machine.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** types of database storage engines; b-tree vs lsm vs column store; read write space amplification; RUM conjecture; how do databases store data differently

### Part 2 — SQLite Without a Server: One File, One Writer

- **Slug:** sqlite-one-file-one-writer · **Arc:** Single-node storage engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** What does a database give up and gain when the library is the server and a file lock is the only coordinator?
- **Assumes:** PG Part 2 (postgresql-foundations-process-layer) #the-postmaster-the-process-that-never-touches-your-data
- **Hands off:** Replication layers built on SQLite (Litestream, LiteFS, rqlite, libSQL) and the experimental BEGIN CONCURRENT/HC-tree branches are named once. The undo-versus-heap MVCC question goes to part 3.
- **Worked example:** The customers table at the PG lab's row count is loaded into one SQLite file. A dbstat page census (4,096-byte pages; a rowid B+tree whose leaves hold the rows) is set against PG's 710 heap pages of 8 KB. One UPDATE is traced in DELETE-journal mode (the original page copied to -journal, fsyncs counted) and in WAL mode (one frame appended). Two writer processes collide: SQLITE_BUSY at busy_timeout 0, serialized at 5,000 ms. One reader holds a snapshot while a writer commits 10,000 transactions; the -wal file grows past the 1,000-page auto-checkpoint and is never reset (checkpoint starvation), the same shape as PG Part 2's idle transaction holding the horizon. Last, fsyncs per commit under synchronous=FULL versus NORMAL.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E4; access: none. Python stdlib sqlite3 (3.46.1 here, compiled with DBSTAT, FTS5 and RTREE: verified), two writer processes and one long reader, and strace for fsync counts. The optional sqlite3 CLI and sqlite3_analyzer can be built from the amalgamation with gcc. The database file sits on the NVMe lab root, not on tmpfs.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** sqlite wal mode explained; sqlite database is locked; sqlite checkpoint starvation wal growing; sqlite vs postgresql architecture; sqlite concurrency

### Part 3 — Where the Old Row Goes: InnoDB Undo Logs vs PostgreSQL

- **Slug:** innodb-undo-log-mvcc-vs-postgresql-heap · **Arc:** Single-node storage engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** How does MySQL's InnoDB keep old row versions for readers while updating rows in place, and what does that cost compared with PostgreSQL's append-only heap and vacuum?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #who-can-see-a-row-xmin-xmax-and-the-hint-bits
- **Hands off:** Redo log, doublewrite, binlog, buffer pool and crash recovery go to part 4. Oracle's undo segments, SQL Server's tempdb version store and OrioleDB (an undo-based table access method for PostgreSQL, owned by the PG spine) are named once.
- **Worked example:** orders is loaded into MySQL with the PG lab's rows. Row 4242 is found in its clustered-index leaf page (16,384-byte page) by a small page reader: FIL header, record header, hidden 6-byte DB_TRX_ID and 7-byte DB_ROLL_PTR. It is updated twice; the lab shows the undo records chained from the roll pointer while the clustered record keeps its place, against PG's new tuple version. A consistent-read transaction is held open while 100,000 updates run; history list length (INNODB_METRICS trx_rseg_history_len) and undo tablespace size are measured, then purge drains after release, set against PG Part 2's idle-transaction horizon. A non-key column update leaves the secondary index untouched, while a secondary lookup needs a second descent through the primary key (contrast HOT and the ctid). Finally, a two-session read-modify-write under REPEATABLE READ: MySQL silently loses one increment, while PG raises 'could not serialize access due to concurrent update' (PG side run in a throwaway database on the PG lab).
- **Lab:** G2 · local service (local-service-in-user-space (MySQL generic glibc 'minimal' tarball plus a libaio.so.1 symlink shim)); ladder E1–E5; access: none. mysqld is initialized with --initialize-insecure under ~/.cache/blog-engines-lab, bound to 127.0.0.1 on a lab port with a socket in the lab directory. LD_LIBRARY_PATH points at a lab lib/ holding libaio.so.1 → the system libaio.so.1t64 (only the t64 name exists here; libnuma is present). A roughly 150-line Python page reader is cross-checked against INFORMATION_SCHEMA and the source's page offsets; innodb_ruby is ruled out because Ruby is absent. The PG comparison runs in a throwaway database.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** innodb mvcc undo log; mysql history list length purge lag; mysql vs postgresql mvcc; innodb clustered index secondary index lookup; mysql repeatable read lost update

### Part 4 — MySQL's Two Logs: Redo, Binlog and the Doublewrite Buffer

- **Slug:** mysql-redo-log-binlog-doublewrite · **Arc:** Single-node storage engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** Why does MySQL write every change to two logs and every page twice when PostgreSQL uses one WAL with full-page images, and what does each setting lose on a crash?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #crash-recovery-archiving-and-replicas-three-readers-of-one-log
- **Hands off:** Group Replication/InnoDB Cluster consensus is taught generically in part 17. Vitess and MySQL sharding are named only. Aurora's 'the log is the database' gets one closing paragraph. Thread-per-connection versus PG's process-per-connection gets one section.
- **Worked example:** One UPDATE of row 4242 is traced through three things: redo bytes (LSN delta from performance_schema.log_status), binlog event size (mysqlbinlog --verbose), and fsyncs per commit under innodb_flush_log_at_trx_commit=1 with sync_binlog=1 versus 0/0 (strace). These are set against PG's 322-byte record and PG Part 1's 7,544-byte full-page image. Next, a checkpoint followed by the first page flush gives doublewrite bytes against FPI bytes. Then kill -9 mysqld mid-load: under flush=0 the lab counts the acknowledged transactions lost; under flush=2 the count should be zero, and the OS-crash row is labelled documented rather than reproduced, because one machine allows no power cut. A second mysqld on another port is fed by the binlog as a replica. Finally, a full orders scan with and without innodb_old_blocks_time, measuring the buffer-pool hit ratio of the hot customers table, set against PG Part 1's 256 KB ring.
- **Lab:** G2 · local service (local-service-in-user-space (same MySQL tarball and shim as part 3)); ladder E1–E5; access: none. The same mysqld as part 3 plus a second instance on another port as a binlog replica. strace counts fsyncs. kill -9 serves as the crash. Captures label both flush settings.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** mysql redo log vs binlog; innodb doublewrite buffer; innodb_flush_log_at_trx_commit explained; mysql binlog two phase commit; innodb buffer pool midpoint insertion

### Part 5 — LSM Trees: How RocksDB Turns Every Write Into an Append

- **Slug:** lsm-tree-rocksdb-write-and-read-path · **Arc:** Single-node storage engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How does a log-structured merge tree accept writes without updating pages in place, and what does a read then have to search?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #the-b-tree-one-lookup-and-one-split
- **Hands off:** Compaction strategies, amplification tuning, write stalls and tombstone build-up go to part 6. LSMs inside Cassandra, CockroachDB (Pebble) and TiKV are named for parts 15 and 18. Bigtable and HBase are named as the lineage.
- **Worked example:** orders rows keyed by order id are inserted into RocksDB with the default 64 MB write buffer. The lab records memtable flushes, L0 file count and sizes, and one SST opened with sst_dump (data, index and filter blocks). The point lookup of order 4242 is traced through memtable, L0 and each level, with block-cache hits and misses and bloom-filter useful/checked counts at 0, 5, 10 and 20 bits per key. That is set against PG Part 3's three-page B-tree walk (290 → 860 → 1068). Then a range scan merges across levels. Finally, sequential versus random key inserts: PG Part 3's rightmost split leaves 90% full and a middle split halves the page, while the LSM never splits a page.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E4; access: none. The rocksdict wheel, which bundles RocksDB, in the engines-lab venv; whether it exposes property strings and statistics is to be verified at research. RocksDB's ldb and sst_dump can be built from source with make (gcc and make are present). Data lives on the NVMe lab root.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** lsm tree explained; how rocksdb works; b-tree vs lsm tree; bloom filter bits per key false positive rate; memtable sstable

### Part 6 — LSM Compaction: Leveled, Tiered and the Write-Stall Cliff

- **Slug:** lsm-compaction-leveled-vs-tiered · **Arc:** Single-node storage engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** Which compaction strategy should an LSM engine run, and how do you predict its write, read and space amplification before it stalls production?
- **Assumes:** Part 5 (lsm-tree-rocksdb-write-and-read-path), its write-path and tombstone sections. Anchors are fixed when part 5 is written.
- **Hands off:** Cassandra's compaction strategies (STCS/LCS/TWCS/UCS) are named for part 15. Key-value separation (BlobDB, WiscKey, Titan) gets one section. Vacuum is PG's in-place counterpart and is linked, not taught.
- **Worked example:** About 10 GB of random-key overwrites in part 5's key shape are run three times: leveled, universal (tiered) and FIFO. For each, rocksdb.stats gives compaction bytes read and written, measured write amplification, steady-state space amplification and p99 put latency. Next, ingest is pushed past compaction throughput until L0 reaches the default slowdown and then stop triggers, and the stall timeline is plotted. Finally, 50% of keys are deleted; tombstones slow a range scan until a manual compaction clears them.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E4; access: none. rocksdict with explicit compaction options. db_bench is optional: it needs gflags, which can be built with a pip-installed cmake inside the venv. The run needs about 25 GB of NVMe space (223 GB free) and stays under a 3 GiB RSS budget.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** rocksdb compaction leveled vs universal; rocksdb write stall; lsm write amplification; tombstones slow range scan; size tiered vs leveled compaction

### Part 7 — How Redis Works: Memory, Eviction and What Survives a Crash

- **Slug:** redis-memory-eviction-persistence · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** What does a single-threaded, in-memory database do with its RAM, which keys does it evict when full, and which acknowledged writes survive a crash or a failover?
- **Assumes:** PG Part 1 (postgresql-foundations-memory-layer) #the-clock-sweep-how-a-page-gets-evicted
- **Hands off:** Redis Cluster's 16,384 hash slots get one section. Failover as a consensus problem goes to part 17. Streams, modules and vector search in Redis are named only. Caching patterns are out of scope.
- **Worked example:** 1,000,000 customers-shaped hashes are loaded. The lab measures bytes per key (MEMORY USAGE, INFO memory) and the listpack→hashtable switch at the documented 128-entry/64-byte thresholds. With maxmemory at half the dataset, it runs allkeys-lru at maxmemory-samples 5 and 10 and allkeys-lfu, and compares their hit ratios on a Zipf workload with an exact-LRU simulation. The link to PG: both designs approximate LRU to save cost (PG Part 1 #why-not-lru). A BGSAVE of a roughly 1.5 GB dataset under continuing writes gives latest_fork_usec and copy-on-write bytes. AOF appendfsync always / everysec / no gives ops/s and fsyncs, set against PG Part 2's 16x synchronous_commit off ratio. Last, kill -9 the primary with one async replica after acknowledged writes, promote the replica, and count the lost keys; then repeat with WAIT 1.
- **Lab:** G2 · local service (local-service-in-user-space (Redis or Valkey built from source with gcc and make; jemalloc is vendored)); ladder E1–E5; access: none. redis-server from a pinned source tarball built in the lab root, a replica on a second port, and redis-py in the venv. strace counts fsyncs. Peak including copy-on-write stays within 3 GiB. Licence note: Redis versus Valkey is chosen at research.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** redis eviction policies lru lfu; redis rdb vs aof; redis fork latency copy on write; redis memory usage per key; redis replication data loss

### Part 8 — MongoDB and WiredTiger: Documents, Cache and In-Memory MVCC

- **Slug:** mongodb-wiredtiger-documents-cache-mvcc · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** How does MongoDB store and update a document in WiredTiger, and why does its cache behave nothing like PostgreSQL's shared buffers?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #toast-when-a-value-will-not-fit
- **Hands off:** Replica sets, the oplog, write concern and rollback go to part 17. Shard-key choice goes to part 16. PG's JSONB operators and indexing belong to the PG spine.
- **Worked example:** One 100 KB orders document (an order with 1,000 line items) has a counter field incremented 1,000 times. MongoDB journal bytes and data-file growth (serverStatus wiredTiger stats, collStats) are set against PG JSONB in a throwaway PG database: WAL bytes from pg_stat_wal, and TOAST chunks rewritten by PG Part 3's ⌈n/1,996⌉ rule. A 2 GB working set runs against a 1 GB WiredTiger cache, showing pages read into cache and application-thread eviction stalls past the dirty trigger. A transaction is held open while 100,000 updates run, showing cache and history-store growth, set against PG Part 2's horizon. Last, an array is pushed until the document nears the 16 MB limit.
- **Lab:** G2 · local service (local-service-in-user-space (MongoDB Community server tarball)); ladder E1–E5; access: none. The mongod Ubuntu 24.04 tarball runs as a single-node replica set, which transactions need. Its runtime libraries libssl3 and libcurl4 are present; running on 26.04 is to be verified. pymongo is in the venv. The PG side runs in a throwaway database on the PG lab.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** wiredtiger cache explained; mongodb vs postgres jsonb; mongodb large document update performance; mongodb embed vs reference; wiredtiger eviction application threads

### Part 9 — Inside Lucene: Segments, Postings and Near-Real-Time Search

- **Slug:** lucene-elasticsearch-segments-postings-refresh · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** How does Lucene, under Elasticsearch and OpenSearch, turn text into immutable segments that answer a query in milliseconds, and why is a just-written document not yet searchable?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #the-b-tree-one-lookup-and-one-split (its posting-list leaf)
- **Hands off:** Lucene's per-segment HNSW goes to part 10. Label postings in a TSDB are linked from part 13. PG full-text search and GIN belong to the PG spine. Relevance tuning is out of scope.
- **Worked example:** 1,000,000 generated orders notes go into a one-shard index, with refresh_interval set explicitly because search-idle shards skip scheduled refreshes. The lab counts segments per refresh at 1 s versus 30 s (_cat/segments) and watches merges over time. For one term it reads the document frequency and a BM25 _explain for one hit. A document written and searched 200 ms later misses until the next refresh, while in PG a committed row is visible to the next statement. 10% of documents are updated, and the deleted-docs ratio and disk use are tracked until the next merge. kill -9 under translog durability async (5 s sync) versus request gives a count of acknowledged documents lost. A closing figure sets PG Part 3's posting-list leaf for customer 92399 beside a Lucene postings block.
- **Lab:** G2 · local service (local-service-in-user-space (OpenSearch or Elasticsearch tarball with its bundled JDK)); ladder E1–E5; access: none. A single node with a 1 GB heap under the lab root. vm.max_map_count is 1,048,576 here, so the bootstrap check passes, and nofile is 524,288. opensearch-py or elasticsearch-py is in the venv. The engine choice follows the licence check at research.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** how lucene inverted index works; elasticsearch refresh vs flush translog; elasticsearch segment merging; bm25 explained; elasticsearch document not searchable immediately

### Part 10 — Vector Databases: HNSW, Quantization and the Filter Problem

- **Slug:** vector-databases-hnsw-quantization-filtering · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** What does a dedicated vector database do differently from an index kept in PostgreSQL pages, and how do you trade recall, latency and memory once a filter is attached?
- **Assumes:** PG Part 1 (postgresql-foundations-memory-layer) #shared-buffers-what-a-buffer-actually-is
- **Hands off:** pgvector tuning belongs to the PG spine and is linked when live. Embedding models and RAG pipelines are out of scope. Lucene's segments are linked back to part 9.
- **Worked example:** 1,000,000 SIFT-128 vectors from the public ANN-benchmarks set are used; synthetic vectors would make recall meaningless. Raw size is 1M × 128 × 4 B = 512 MB. HNSW with M=16 runs at ef_search 16, 64 and 256, measuring recall@10, p50 latency and index size in Qdrant and in faiss/hnswlib. IVF-PQ with nlist 4,096 and m=16 (16 bytes per vector, 32x smaller) gives recall against nprobe. A payload filter then keeps 1% of vectors, comparing post-filter recall with Qdrant's payload-indexed filtering. The same HNSW is built with pgvector in a throwaway PG database, measuring build time, index pages and the shared-buffers hit ratio during queries.
- **Lab:** G1 · runs anywhere (runs-anywhere (faiss-cpu, hnswlib) plus local-service-in-user-space (the Qdrant static binary and the pgvector comparison)); ladder E1–E5; access: none. A dataset download of about 0.5 GB into the lab root, faiss-cpu and hnswlib wheels, and the Qdrant release binary on a lab port. pgvector is compiled with pgxs against the PG lab and created only in a throwaway database; this must be coordinated with the PG spine's pgvector part. The run stays within a 3 GiB budget.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** how hnsw works; vector database vs pgvector; ivf pq explained; filtered vector search recall; vector index memory calculation

### Part 11 — Column Stores: How ClickHouse's MergeTree Skips Your Data

- **Slug:** clickhouse-mergetree-column-store · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** Why does a column store answer an aggregate over a huge table by reading a sliver of it, and why does an UPDATE become a rewrite?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #the-heap-page-byte-by-byte
- **Hands off:** Vectorized execution goes to part 12. Parquet and lakehouse formats belong to `data-at-scale`. ReplicatedMergeTree and Keeper are named, and Keeper's Raft goes to part 17.
- **Worked example:** orders is generated at the PG lab's row count and at 100x. The lab measures per-column bytes on disk and compression ratio (system.parts_columns). One monthly-revenue query shows the granules selected by the sparse index (EXPLAIN indexes = 1) and read_rows/read_bytes from system.query_log, against PG reading the whole 7,693-page heap for the same query (PG Part 1's cold scan). ORDER BY (customer_id, order_date) versus (order_date) is compared by granules read for two query shapes, at 8,192 rows per granule. Last, one ALTER TABLE UPDATE mutation rewrites a part, measured in bytes, against PG Part 3's 111-byte HOT update.
- **Lab:** G2 · local service (local-service-in-user-space (ClickHouse single binary)); ladder E1–E4; access: none. The clickhouse binary under the lab root runs clickhouse-local for loading and a clickhouse server on a lab port for query_log. clickhouse-connect is in the venv. The 100x table needs a few GB of NVMe space.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** how clickhouse mergetree works; clickhouse primary key sparse index granule; column store vs row store; clickhouse update mutation slow; clickhouse order by key choice

### Part 12 — DuckDB Vectorized Execution: 2,048 Rows at a Time

- **Slug:** duckdb-vectorized-execution · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** Why does an analytical engine process a vector of values per operator call instead of one tuple, and how does it use every core where PostgreSQL launches a couple of workers?
- **Assumes:** Part 11 (clickhouse-mergetree-column-store), its column-layout section
- **Hands off:** DuckDB reading Parquet and Iceberg belongs to `data-at-scale`. Planner and optimizer theory belongs to the PG spine. DuckDB's HyPer-style in-place-with-undo MVCC gets one section linking part 3.
- **Worked example:** Part 11's orders at 1x and 100x are loaded into DuckDB. GROUP BY customer_id SUM(amount) runs at threads = 1, 2, 4, 8 and 16 to get a scaling curve (16 CPUs here), with operator timings from EXPLAIN ANALYZE. The same query runs in a throwaway PG database at max_parallel_workers_per_gather 0, 2 (the default) and 8, set against PG Part 2's 'six planned, one launched'. Per-row cost at one thread isolates vectorization from parallelism. Last, memory_limit = 500 MB forces the aggregate to spill, and temp bytes are measured.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E4; access: none. The duckdb wheel, or the DuckDB CLI static binary listed in facts.md, runs the whole DuckDB side. The PG side needs a throwaway database on the PG lab.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** vectorized query execution explained; duckdb internals; morsel driven parallelism; volcano model vs vectorized; duckdb vs postgres analytics

### Part 13 — Time-Series Engines: Inside the Prometheus TSDB

- **Slug:** prometheus-tsdb-time-series-engine · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** How does a time-series engine store a numeric sample in a byte or two where a PostgreSQL row costs dozens, and what breaks when label cardinality explodes?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #rows-per-page
- **Hands off:** TimescaleDB and PG partitioning for time series belong to the PG spine. PromQL and pipeline design are out of scope. Long-term object-store backends (Thanos, Mimir) are named only.
- **Worked example:** 1,000 series with one sample per 15 s for 30 days (172.8M samples) are backfilled with promtool tsdb create-blocks-from openmetrics. promtool tsdb analyze then gives bytes per sample, chunk counts and label postings. The same samples as (ts timestamptz, series_id int, value float8) PG rows cost about 52 B each by PG Part 3's tuple arithmetic: a 24-byte aligned header, 8+4+4 pad+8 data, and a 4-byte line pointer. That figure is optionally measured at 1% scale in a throwaway PG database. Retention is compared as dropping a 2-hour block versus DELETE plus vacuum. Last, a label with 100,000 distinct values is added, and head series count, memory and index size are measured.
- **Lab:** G2 · local service (local-service-in-user-space (Prometheus and promtool static binaries)); ladder E1–E4; access: none. promtool backfill and analysis work on files without a server. A Prometheus server on a lab port handles the cardinality experiment. Both binaries are the user-space downloads listed in facts.md.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** how prometheus tsdb works; gorilla compression explained; prometheus high cardinality memory; time series database vs postgres; prometheus bytes per sample

### Part 14 — Graph Databases: Index-Free Adjacency Versus Joins

- **Slug:** graph-databases-index-free-adjacency-vs-joins · **Arc:** Purpose-built engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** When does storing relationships as pointers beat joining through B-tree indexes, and when does the relational engine win anyway?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #the-b-tree-one-lookup-and-one-split
- **Hands off:** Graph analytics frameworks (Pregel, GraphX) belong to `data-at-scale`. RDF and SPARQL are named only. Apache AGE belongs to the PG spine.
- **Worked example:** A power-law referral graph is built over the customers rows (each customer refers 0 to 20 others, about 1M edges). Friends-of-friends from customer 92399, PG Part 3's lookup key, is run at depths 1 to 4: as a PG recursive CTE with EXPLAIN ANALYZE BUFFERS in a throwaway database, and in Neo4j with PROFILE for db hits and page-cache hits. The comparison covers rows reached and pages or records touched per depth. Then a whole-graph aggregate (triangle count) is run where hash joins or DuckPGQ win. Last, a supernode with 100,000 referrals is added to both engines.
- **Lab:** G2 · local service (local-service-in-user-space (Neo4j Community tarball plus a JDK 21 tarball; no Java on this machine)); ladder E1–E4; access: none. Neo4j with a 1 GB heap and a 1 GB page cache under the lab root. DuckDB with the DuckPGQ community extension is the runs-anywhere comparison path. The PG side runs in a throwaway database. Neo4j's record-versus-block store format is pinned at research.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** index free adjacency explained; graph database vs relational performance; neo4j vs postgres recursive cte; when to use a graph database; sql pgq gql

### Part 15 — Leaderless Replication: How Cassandra Survives a Node Down

- **Slug:** cassandra-dynamo-leaderless-replication · **Arc:** Distributed engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** How does a Dynamo-style store keep accepting writes with replicas down or partitioned, and what does a quorum read actually guarantee?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #replicas
- **Hands off:** Query-first modeling and partition sizing go to part 16. Consensus goes to part 17. History checking goes to part 20. Storage compaction is linked to part 6. ScyllaDB and Riak are named. DynamoDB-the-service (Multi-Paxos leaders per partition) is set apart from Dynamo-the-paper.
- **Worked example:** Three Cassandra nodes on 127.0.0.1-3, all inside one unprivileged network namespace, RF = 3. Node 3 is cut off by an nftables rule; a write at ONE, then a read at ONE from node 3 returns the old value while QUORUM returns the new one. On heal, hints are delivered (nodetool tpstats, hint files). Two clients write the same cell, and the later write, carrying a USING TIMESTAMP 2 s behind, silently loses. A row is deleted with gc_grace_seconds = 60, node 3 is held partitioned past that window, compaction runs, and on heal the deleted row comes back. Last, one IF NOT EXISTS lightweight transaction is compared with a plain write under 5 ms of netem delay.
- **Lab:** G2 · local service (local-service-in-user-space (Cassandra tarball plus a JDK 17 tarball, inside unshare -rn)); ladder E1–E5; access: none. Nodes and client are launched from one unshare -rn shell, so nftables drops and tc netem delays work without root; this was verified on this machine 2026-09-28. Heaps are 512 MB to 1 GB per node, 3 GiB or less in total. ccm and cassandra-driver are in the venv.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** cassandra consistency levels quorum; hinted handoff read repair; cassandra tombstones gc_grace_seconds zombie data; dynamo vs dynamodb; leaderless replication

### Part 16 — Data Modeling Without Joins: Partition Keys That Scale

- **Slug:** data-modeling-partition-keys-cassandra-dynamodb · **Arc:** Distributed engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 10
- **Answers:** How do you design tables for a store that can only find data by its partition key, and what does a bad key cost?
- **Assumes:** Part 15 (cassandra-dynamo-leaderless-replication), its consistent-hashing section
- **Hands off:** Range partitioning in distributed SQL goes to part 18. MongoDB's balancer mechanics are named. Normalized relational schema design belongs to the PG spine.
- **Worked example:** The PG series' three orders access patterns (orders by customer newest first, one order by id, orders by status per day) are modeled three ways: PG (one table plus two indexes), Cassandra (three tables) and DynamoDB single-table design (one table plus one GSI). For each, the lab measures bytes stored per order and partitions touched per query (Cassandra TRACING). One customer is then given 1,000,000 orders, raising a partition-size warning (nodetool tablehistograms) that monthly buckets fix. Key and GSI correctness is checked on DynamoDB Local only.
- **Lab:** G2 · local service (local-service-in-user-space (part 15's Cassandra plus the DynamoDB Local jar on the same JDK)); ladder E1–E4; access: optional: an AWS sandbox DynamoDB table for measured hot-partition throttling (see access_requests). Reuses the part 15 cluster. DynamoDB Local runs on a lab port and boto3 is in the venv. DynamoDB Local models no partitions or throughput, so hot-key throttling is either documented or measured on the optional real table.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** cassandra data modeling partition key; dynamodb single table design; dynamodb hot partition; cassandra large partition; how to choose a shard key

### Part 17 — Consensus Inside the Database: Raft and What a Majority Buys

- **Slug:** raft-consensus-database-replication · **Arc:** Distributed engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 14
- **Answers:** How do replicas agree on one log without an outside referee, and which acknowledged writes survive a leader's death?
- **Assumes:** PG Part 2 (postgresql-foundations-process-layer) #the-wal-writer-and-what-a-commit-waits-for
- **Hands off:** Raft per range and distributed transactions go to part 18. Paxos variants (Multi-Paxos, EPaxos, Accord) are named. History checking goes to part 20. Patroni's use of etcd for PostgreSQL belongs to the PG spine.
- **Worked example:** Three etcd members run inside a user network namespace. etcdctl endpoint status shows term, index and leader. kill -9 the leader and time the new election at the default 100 ms heartbeat and 1,000 ms election timeout. nftables then isolates the leader: the minority side cannot commit, the majority elects, and the old leader steps down on heal. tc netem at 1, 10 and 50 ms RTT shows commit latency tracking the median follower. Then a three-member MongoDB replica set: 1,000 w:1 writes are acknowledged, the primary is cut off, a new primary is elected, and the old primary rejoins; the rollback files count the lost acknowledged writes. The same run with w:'majority' should lose nothing, at higher latency. PG contrast numbers are quoted from PG Part 2's synchronous_commit capture.
- **Lab:** G2 · local service (local-service-in-user-space (etcd static binary plus the MongoDB tarball from part 8, inside unshare -rn)); ladder E1–E5; access: none. All members and clients run in one unprivileged network namespace for partitions and latency. Election timings come from the etcd and mongod logs. pymongo and the etcd client are in the venv.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** raft consensus explained; etcd leader election; mongodb write concern majority rollback; raft vs paxos database; quorum commit latency

### Part 18 — Distributed SQL: Committing Across Ranges in CockroachDB

- **Slug:** distributed-sql-ranges-raft-transactions · **Arc:** Distributed engines · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** How does a distributed SQL database split a table into ranges, replicate each with its own consensus group, and commit a transaction that touches several of them?
- **Assumes:** Part 17 (raft-consensus-database-replication), its commit-and-leases section
- **Hands off:** Timestamps and clock uncertainty go to part 19. Consistency checking goes to part 20. Citus belongs to the PG spine. HTAP learners (TiFlash) are named.
- **Worked example:** Three CockroachDB nodes run in a user network namespace with 10 ms netem RTT between them. orders is loaded and SHOW RANGES tracks the table as it splits. A single-row UPDATE (one range, one consensus round) is compared with a transaction updating an orders row and a customers row on two ranges with different leaseholders; latency and KV round trips come from EXPLAIN ANALYZE and a trace, showing parallel commits. kill -9 a leaseholder and time how long until writes resume. A follower read (AS OF SYSTEM TIME follower_read_timestamp()) is compared with a leaseholder read. The same two-row transaction runs on TiDB via TiUP playground (PD, 3 TiKV, TiDB), with Percolator's prewrite and commit phases and its TSO fetches visible in the trace.
- **Lab:** G2 · local service (local-service-in-user-space (CockroachDB single binary and TiUP playground, inside unshare -rn)); ladder E1–E5; access: none. CockroachDB runs with --cache and --max-sql-memory lowered to about 700 MB per node. TiUP runs with TIUP_HOME inside the lab root. CockroachDB's licence changed in 2024 and must be verified; YugabyteDB (yugabyted) or TiDB, both Apache 2.0, is the fallback lab engine.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** how cockroachdb works; distributed sql architecture; tidb percolator transaction; cockroachdb parallel commits; yugabytedb vs cockroachdb architecture

### Part 19 — Ordering Transactions Across Machines: TrueTime, HLC and TSO

- **Slug:** truetime-hlc-tso-distributed-timestamps · **Arc:** Distributed engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** Without one machine handing out transaction IDs, how does a distributed database decide which transaction came first, and what does each answer cost per commit?
- **Assumes:** PG Part 3 (postgresql-foundations-storage-layer) #who-can-see-a-row-xmin-xmax-and-the-hint-bits
- **Hands off:** History checking goes to part 20. Spanner's SQL layer is named. Clock hardware and NTP/PTP operations are out of scope.
- **Worked example:** CockroachDB, three nodes: a concurrent read/write workload runs at the default --max-offset of 500 ms and at a lowered bound, counting uncertainty restarts from metrics. A write to a GLOBAL table has its commit latency measured as commit wait. On TiDB playground, netem delay of 0, 5 and 20 ms is placed between tidb-server and PD; every transaction pays the TSO round trip for its start and commit timestamps. A TrueTime commit-wait model is computed with the Spanner paper's reported ε range and labelled as a model. The post states plainly that the lab cannot skew one node's wall clock: there is no root, time namespaces do not shift CLOCK_REALTIME, and Go binaries ignore LD_PRELOAD time fakes.
- **Lab:** G2 · local service (local-service-in-user-space (part 18's CockroachDB and TiUP setup); optional needs-access for a Cloud Spanner instance); ladder E1–E4; access: optional: a Cloud Spanner instance for real commit timestamps and latency (see access_requests). Reuses part 18's namespace scripts. Uncertainty-restart and commit-latency captures are labelled with the offset bound. Spanner numbers are either model-only or come from the optional instance.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** spanner truetime explained; hybrid logical clock; cockroachdb uncertainty interval read restart; tidb tso timestamp oracle; spanner commit wait

### Part 20 — Checking a Database's Consistency Claims Yourself

- **Slug:** checking-database-consistency-claims-jepsen-style · **Arc:** Distributed engines · **Status:** planned
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 7,000 · **Figures:** 10
- **Answers:** How do you test whether a database really provides the consistency it advertises, on one machine, with real partitions?
- **Assumes:** Part 17 (raft-consensus-database-replication), its partition experiments
- **Hands off:** Nothing is handed on. This optional part closes the distributed arc.
- **Worked example:** A single-register workload (read, write, CAS; 5 clients; 60 s) runs against etcd with linearizable versus serializable (--consistency=s) reads, and against MongoDB at w:1/readConcern local versus w:majority/linearizable, under nftables partitions every 10 s. Histories are recorded and checked by a small shipped Python WGL linearizability checker, and by Elle on the lab JDK. The result shows which configurations produce non-linearizable histories. The Hermitage lost-update test is re-run on MySQL and PG REPEATABLE READ from part 3.
- **Lab:** G2 · local service (local-service-in-user-space (reuses part 17's etcd and MongoDB; Elle on the lab JDK)); ladder E1–E4; access: none. The fault schedule runs from one unshare -rn shell. The checker and histories ship as lab files. The README states the limit: one kernel, one clock, one disk.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** jepsen testing explained; how to test linearizability; elle consistency checker; database isolation anomalies write skew g2

## Publication order and cadence

Starts after PostgreSQL Foundations' core (Part 32) is live, or interleaves with its later arcs —
the owner's call. Within this series, a part may publish once the one part it names under
**Assumes** is live. Versions are pinned at each part's research time from dated primary sources
(the 2026-09-28 currency check is in the build scratchpad, not here).

## Cross-links

Every part here opens from one named PostgreSQL mechanism, mostly in PostgreSQL Foundations Parts 1–3 (published or drafted), plus: Part 18 (isolation) for InnoDB MVCC in Part 3; Part 36 (pgvector) for Part 10; Part 40 (analytics) for Parts 11–12; Parts 22–23 (replication, failover) for Parts 15 and 17; Part 35 (full-text) for Part 9. Links run only from the later-published part. Published parts are never edited to add forward links.

## Lab policy

Graded per blog-forge `references/labs.md` (G0–G3, ladder E1–E5); the probe and requests are in
`access.md`. Everything installable in user space is self-provisioned and never asked for — JDK
and Hadoop/Kafka/Spark/Trino tarballs, static binaries, source builds into a user prefix, a
disposable local PostgreSQL. The build machine has ~5 GB RAM free at idle and no Docker access.

### Access requests (answer each: `grant`, `decline` or `later`)

| ID | Need | Parts | Smallest arrangement | If declined |
|---|---|---|---|---|
| AR-01 | A Google Cloud Spanner instance for one working session | 19 (and one Spanner paragraph in 18) | A Spanner free-trial instance if the account qualifies, otherwise the smallest paid configuration (100 processing units) for a single sitting. One throwaway database, a budget alert, credentials kept out of every lab file, and no production data. Delete the instance after the run. | Teach TrueTime from the Spanner papers as an explicitly labelled model. Measure commit wait locally on CockroachDB GLOBAL tables (non-blocking transactions), which wait out a clock bound the same way, and label it as an analog, not Spanner. |
| AR-02 | An AWS sandbox account with one DynamoDB on-demand table | 16 | One on-demand table in a sandbox account, an IAM user limited to that table, and a small budget alarm. Run about a million writes against one partition key, then against spread keys, and delete the table after the run. Current prices are pinned at research, not in the plan. | Cite the 2022 DynamoDB paper and AWS documentation for per-partition limits as documented behaviour. Demonstrate the same skew locally as an oversized, hot partition on part 15's Cassandra cluster (nodetool tablehistograms and TRACING). |

## What this series will not cover

- Proprietary or cloud-only engines as full parts: Oracle, SQL Server, DB2, Aurora and AlloyDB storage, Pinecone, and DynamoDB internals beyond its published paper. They are named where they illustrate a variant and never given a lab.
- Installation guides, operations runbooks, managed-service pricing, vendor feature matrices and speed shootouts between engines.
- The big-data and lakehouse stack: Hadoop, Spark, Kafka, Flink, Parquet/ORC internals, Iceberg/Delta/Hudi, Trino, warehouses and streaming databases (Materialize, RisingWave). These belong to `data-at-scale`.
- Anything PostgreSQL-specific beyond the one named baseline anchor per part: PG isolation levels, replication setup, Patroni, and pgvector/JSONB/full-text/TimescaleDB/Citus/AGE/OrioleDB configuration. These belong to the PG spine.
- Query-language tutorials (SQL, CQL, Cypher, GQL, PromQL, MongoDB query language, Elasticsearch DSL), ORMs and application caching patterns.
- Engines without a part: ScyllaDB, FoundationDB, VoltDB, SingleStore, Couchbase, Memgraph, Milvus, Weaviate, InfluxDB, VictoriaMetrics, Riak. HBase and Bigtable appear only as LSM and wide-column lineage (their Hadoop deployment is `data-at-scale`). Each is named once where it illustrates a design choice.
- Embedding models, RAG pipelines and search-relevance tuning.
- Legacy and niche models: hierarchical (IMS), object and XML databases, RDF triple stores beyond a mention, and ledger/blockchain databases.
- Hardware-level storage (persistent memory, zoned or computational SSDs), power-loss testing and clock hardware (NTP/PTP/GPS operations).

## Risks

- Publication dependency: 15 of the 20 parts anchor on PG Parts 2 or 3. Part 2's publish status is unconfirmed and Part 3 is not uploaded. If this series starts first, publish the parts anchored only on the live PG Part 1 (1, 7, 10) first, and renumber series_position before any upload, since positions are publication order.
- facts.md says no real network partitions, but a read-only probe on 2026-09-28 created a netem qdisc, a veth pair and an nftables table inside unshare -rn without root. apparmor_restrict_unprivileged_userns is 1 here yet the probe worked, so a policy or profile update could close it. Re-verify at the first distributed lab (part 15). If it fails, fall back to kill -9, SIGSTOP/SIGCONT and a user-space TCP proxy on client paths, labelled as weaker than a partition.
- Licence churn changes which engine a lab can use: CockroachDB (2024 change to a licence-key/telemetry model), Redis (source-available in 2024, AGPLv3 option from Redis 8), Elasticsearch (AGPL option added in 2024), MongoDB (SSPL), Neo4j Community (GPLv3). The embedded graph engine Kùzu was reportedly archived in 2025; the plan does not use it. Pin and check per part; each lab README names its fallback (YugabyteDB/TiDB, Valkey, OpenSearch).
- Version currency: many defaults changed recently (MySQL 8.4 InnoDB defaults, Redis listpack encodings, Cassandra 5.0 UCS/SAI, Neo4j's block store format, Prometheus 3, RocksDB options). The plan deliberately carries no version numbers. Pin them per part at research against a dated primary source; this is the NVIDIA-series lesson.
- Benchmark trap: cross-engine speed shootouts invite wrong conclusions, and some licences restrict publishing benchmarks. Parts measure mechanisms (bytes, pages, fsyncs, round trips, amplification, recall), label every timing with hardware, version and config, and never headline 'X is faster than PostgreSQL'.
- Memory ceiling: 14 GiB total and about 4 GiB available at probe time. Cassandra x3, OpenSearch, CockroachDB x3 and the Redis fork demo are tight. Each lab budgets a peak of 3 GiB or less, runs alone, and records peak RSS.
- One machine: namespaces give real packet loss and latency, but all nodes share one disk, CPU pool, kernel and clock. That rules out independent disk failure, clock skew and power loss. Every distributed part must state what its lab cannot show, part 19 above all.
- Shared PG lab: research subagents have altered that server before (context and memory record an ALTER SYSTEM and a pg_ctl stop). Parts wanting fresh PG numbers must use throwaway databases, snapshot postgresql.auto.conf and never run concurrently with other agents.
- Tooling gaps: there is no ready InnoDB page tool here (innodb_ruby needs Ruby, which is absent), so part 3's Python page reader must be cross-checked against INFORMATION_SCHEMA and source offsets. rocksdict's statistics surface is unverified. The MongoDB 24.04 tarball on Ubuntu 26.04 is unverified. perf is unavailable (perf_event_paranoid 4).
- Scope overlap: pgvector, JSONB, full-text, time series, isolation, Citus and Patroni belong to the PG spine; Parquet, Trino and lakehouse belong to `data-at-scale`. A part that drifts into PG configuration or file formats duplicates a sibling series; the boundary notes fix ownership.
- Size: 19 committed parts is about 150,000 words. If the owner wants a smaller first commitment, the defensible core is 1, 3, 5, 15, 17 and 18, then 2 and 7. The only in-series dependencies are 6→5, 12→11, 16→15, 18→17 and 20→17, so the remaining spokes can be added later without re-cutting.
- Hub promise: if part 1 lists spokes by title, the list becomes a public promise (the image-processing precedent). Keep the hub's map at family level and link a spoke only once it is live.
