# Series plan — Data at Scale: From Hadoop to the Lakehouse

**Slug:** data-at-scale · **Shape:** hybrid · **Parts:** 22 · **Status:** Checkpoint S — awaiting approval (planned 2026-09-29) · **Sibling of:** `postgresql-foundations`

## Why this is its own series, not part of PostgreSQL Foundations

No: Hadoop is not part of PostgreSQL, and no part of it runs inside PostgreSQL. It is a separate Apache project written in Java. It started in 2006 out of the Nutch web crawler and was modelled on Google's GFS (SOSP 2003) and MapReduce (OSDI 2004) papers. The precise differences:

1. Unit of scale. PostgreSQL is one server process tree owning one data directory (Part 2's postmaster and its children). Hadoop is many machines running DataNode and NodeManager daemons, coordinated by a NameNode and a ResourceManager.
2. Storage. PostgreSQL keeps rows in 8 KB heap pages, and an UPDATE writes a new row version under MVCC (Part 3). HDFS files are write-once or append-only, cut into 128 MiB blocks and replicated 3x across machines, and HDFS has no notion of a row.
3. Transactions. PostgreSQL gives ACID across arbitrary rows through WAL and snapshots. HDFS offers atomic file create and rename and nothing about records, and MapReduce offers only task-level retry. Table-level atomicity arrived later, through table formats (Iceberg, Delta, Hudi) layered on top.
4. Access paths. PostgreSQL has a cost-based planner, B-tree and other indexes, and millisecond point lookups. Hadoop has no indexes and no SQL of its own (Hive added SQL; Spark and Trino replaced its compute). It is built to scan everything, moving the computation to where the blocks are.
5. Schema. Schema-on-write versus schema-on-read.
6. Workload. OLTP (many small, low-latency transactions) versus batch analytics (few huge scans, measured in throughput).

The modern stack is a set of separate systems joined by files and protocols: storage, file format, table format, catalog, compute engines, a log and an orchestrator. It therefore needs its own lab (JVM daemons on loopback nodes, object storage, Python lake tools), its own unit of reasoning (bytes scanned, files, shuffles, snapshots) and its own reader objectives. Teaching it inside postgresql-foundations would break that series' one-lab, one-server decomposition and its public 'one per layer' framing.

What does carry over from PG Parts 1-3. Sibling parts link back to these anchors rather than re-teaching:
- The log comes before the state, and checkpoints make the log forgettable. The NameNode's edit log plus fsimage is WAL plus checkpoint (PG3 #wal-records-lsns-and-segment-files, PG2 #the-checkpointer-making-the-wal-forgettable). The NameNode replays its log at startup the way PostgreSQL does (PG3 #replaying-a-crash). Kafka is a replicated WAL that readers subscribe to (PG3 #crash-recovery-archiving-and-replicas-three-readers-of-one-log).
- Pages and blocks are the same trade-off at different sizes, a unit of I/O and of placement: 8 KB versus 128 MiB, then Parquet pages and row groups (PG3 #the-heap-page-byte-by-byte). Checksums per unit carry over too: CRC-32C per WAL record, CRC32C per 512 bytes in HDFS (PG3 #one-record-byte-by-byte).
- Scan resistance. PostgreSQL defends its cache against exactly the big sequential scan Hadoop is built for (PG1 #rings-why-a-big-scan-leaves-256-kb-behind).
- Sort memory and spill. work_mem per operation corresponds to MapReduce's map-side spill and Spark's execution memory (PG1 #one-sort-two-budgets, #local-memory-work_mem-and-its-family).
- Process roles. A coordinator that never touches data bytes (PG2 #the-postmaster-the-process-that-never-touches-your-data). Workers requested versus granted (PG2 #parallel-workers-and-the-shared-pool). Reset-everyone recovery versus task retry and lineage (PG2 #one-killed-backend).
- Snapshots and visibility. Row-level xmin/xmax becomes table-level snapshots in Iceberg and Delta (PG3 #who-can-see-a-row-xmin-xmax-and-the-hint-bits). A long reader holding old data (PG2 #the-horizon) becomes time travel holding old files.
- Skipping by summary. The visibility map (PG3 #the-visibility-map-and-why-vacuum-skips-pages) becomes Parquet statistics and Iceberg manifest pruning.
- Garbage collection. Vacuum (PG2 #autovacuum-part-two-what-the-worker-actually-does) becomes compaction, expire_snapshots and orphan removal. HOT (PG3 #hot-the-update-that-skips-the-indexes) becomes files that are never updated in place.
- Compression and out-of-line values. TOAST (PG3 #toast-when-a-value-will-not-fit) becomes Parquet encodings and codecs.

## Shape

The ground covered here is neither one system seen at rising depth (a pure ladder) nor one system's sibling subsystems at the same depth (the decomposition PostgreSQL Foundations uses). It is a stack of separate projects, and each has its own lab, its own unit of reasoning and its own search audience. So: Part 1 is a hub, the layer map every other part links to. Eight arcs are cut at prerequisite seams. Inside the Spark, table-format and streaming arcs there are short ladders (8 to 9, 11 to 12, 16 to 17 and 18). An upper rung re-teaches its lower rung in one paragraph, and only where a reader arriving from search needs it. Every other member is a spoke: it assumes one rung and re-teaches nothing. Each part has at most one parent, and every parent sits at a lower position, so publication order 1 to 22 never links backward to an unpublished part: 2<-1, 3<-2, 4<-2, 5<-2, 6<-1, 7<-6, 8<-3, 9<-8, 10<-8, 11<-4, 12<-11, 13<-11, 14<-11, 15<-7, 16 (none), 17<-16, 18<-16, 19 (none), 20<-19, 21<-20, 22<-15. Why a series and not one post: the budget is about 176,000 words over 22 prerequisite-separated groups, far past one L4. Adjacent options the owner can overrule in one word: (a) a 15-part core (1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 15, 16, 17, 19, 20) that defers the seven leaf spokes 5, 10, 13, 14, 18, 21 and 22, none of which any other part depends on; (b) split the streaming arc (16-18) into its own series; (c) fold the Hadoop arc (2-4) into one L4 post on what Hadoop got right. Option (c) saves two parts but loses the HDFS internals and the small-files mechanism that Part 11 starts from.

## Arcs

| Parts | Arc | Purpose |
|---|---|---|
| 1 | Orientation (hub) | The way in from scratch: when one server stops being enough, the honest Hadoop-versus-PostgreSQL answer, and the layer map every other part hangs on. |
| 2-4 | The Hadoop foundation | Storage, batch compute and resource scheduling as Hadoop built them, plus the directory-as-table design whose failure motivates everything after. Each part is taught for what carried forward. |
| 5-7 | Storage for analytics | Object-store semantics in place of a filesystem, the columnar file byte by byte, and arranging rows so that queries skip data. |
| 8-10 | Spark | A ladder from execution model to optimizer (depth), plus a practice spoke on measured tuning. |
| 11-14 | Open table formats | A ladder from Iceberg's commit model to row-level change and maintenance (depth), plus comparison (Delta/Hudi) and catalog/governance spokes. |
| 15, 22 | Query engines and architecture | Distributed SQL over storage the engine does not own, then the capstone choice between warehouse, lake and lakehouse. |
| 16-18 | Streaming | The log itself, then two depth spokes: CDC from PostgreSQL into the lake, and stateful stream processing. |
| 19-21 | Pipelines and modeling | A ladder from analytics modeling to transformation (dbt) to orchestration (Airflow). This is the second, beginner-friendly way into the series. |

## Reading paths

- **Analytics from scratch** (Readers who know little SQL, or analysts moving into data engineering.): The PostgreSQL spine's SQL-from-scratch part -> 1 -> 19 -> 20 -> 21 -> 6 -> 7 -> 15 -> 22
- **PostgreSQL engineer crossing over** (Readers of postgresql-foundations who want the analytics side, taught against what they already know.): PG Parts 1-3 -> 1 -> 6 -> 16 -> 17 (after the PG spine's logical-decoding part) -> 2 -> 4 -> 11 -> 12
- **Hadoop platform** (Engineers running, securing or migrating an on-premises Hadoop estate.): 1 -> 2 -> 3 -> 4 -> 5 -> 8
- **Spark engineer** (Batch data engineers who write and tune Spark jobs.): 1 -> 2 -> 3 -> 8 -> 9 -> 10 -> 6 -> 7
- **Lakehouse platform** (Engineers building an open lakehouse on object storage.): 1 -> 2 -> 4 -> 5 -> 6 -> 7 -> 11 -> 12 -> 13 -> 14 -> 15 -> 22
- **Streaming** (Engineers building event pipelines and CDC.): 1 -> 16 -> 17 (with the PG spine's logical-decoding part first) -> 18
- **Full industry-grade path** (The reader the owner wants to train: someone who should know every layer of data handling.): The PostgreSQL spine's core, then Parts 1 -> 22 in publication order

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | decide from dataset size, a measured scan rate and query shape whether one PostgreSQL server still fits the job | 1 |
| 2 | name each layer of the distributed data stack and the project that fills it, and say precisely why Hadoop is not a database | 1 |
| 3 | trace a file into blocks and replica placements, and read the NameNode's edit log and fsimage offline | 2 |
| 4 | predict when a DataNode is declared dead, and what re-replication and checksum repair then do | 2 |
| 5 | follow a MapReduce job from submission through containers, spills, shuffle and reduce, and compute its spill count and shuffle bytes | 3 |
| 6 | size YARN containers per node and explain queue capacity and elasticity | 3 |
| 7 | explain how a Hive table maps to directories and metastore rows, and price the small-files problem in NameNode heap and scan time | 4 |
| 8 | show why a directory-based INSERT OVERWRITE is not atomic for concurrent readers | 4 |
| 9 | name the filesystem operations object stores lack, and choose a job committer that does not depend on rename | 5 |
| 10 | compare the storage overhead and failure tolerance of replication and erasure coding | 5 |
| 11 | decode a Parquet footer and a column chunk by hand, and predict each column's encoding | 6 |
| 12 | explain repetition and definition levels, and choose between Parquet, ORC, Avro and Arrow for a job | 6 |
| 13 | choose partition columns, sort order and target file size, and predict how many row groups a query skips | 7 |
| 14 | say when Z-order or Hilbert ordering helps and when only a bloom filter will | 7 |
| 15 | explain how an action becomes jobs, stages and tasks, and find every shuffle boundary in a program | 8 |
| 16 | explain how Spark rebuilds a lost partition from lineage, and why it outruns MapReduce | 8 |
| 17 | read a Spark plan at every Catalyst phase and predict which join strategy it will choose | 9 |
| 18 | explain the three things adaptive query execution changes at runtime | 9 |
| 19 | compute an executor's memory regions and size shuffle partitions from input size | 10 |
| 20 | diagnose skew, spill and small-file output from metrics, and prove each fix with a measurement | 10 |
| 21 | read every Iceberg metadata file, and explain how a commit is made atomic and how a conflict retries | 11 |
| 22 | evolve a schema and a partition spec without rewriting data, time-travel, and gate a batch with write-audit-publish | 11 |
| 23 | choose copy-on-write or merge-on-read for a workload, and run table maintenance in the right order | 12 |
| 24 | prove that a GDPR deletion is physically complete in a lake | 12 |
| 25 | read a Delta transaction log and a Hudi timeline, and choose a table format by workload | 13 |
| 26 | explain what a lakehouse catalog guarantees, give two engines safe access to one table, and contrast credential vending with Kerberos delegation tokens | 14 |
| 27 | read a distributed query plan, choose broadcast or partitioned joins, and explain dynamic filtering and connector pushdown | 15 |
| 28 | read a Kafka partition's segment files, and predict what is committed and what can be lost under each acks and ISR setting | 16 |
| 29 | explain idempotent producers, transactions and leader-epoch fencing | 16 |
| 30 | build a PostgreSQL-to-Iceberg CDC pipeline with an idempotent sink, and spot replication-slot WAL retention before it fills a disk | 17 |
| 31 | choose a watermark from measured lateness, handle late events, and explain barrier checkpoints and end-to-end exactly-once | 18 |
| 32 | declare a fact table's grain, model slowly changing history as Type 2, and avoid fan-out double counting | 19 |
| 33 | explain what dbt compiles and runs, pick a materialization, and write an incremental model that survives late data | 20 |
| 34 | explain Airflow's data intervals, and make tasks safe to retry and backfill | 21 |
| 35 | explain storage-compute separation in three warehouses, cost a workload under three pricing models, and choose warehouse, lake or lakehouse | 22 |

## Parts

### Part 1 — Hadoop Is Not a Database: What Changes When Data Outgrows One Server

- **Slug:** hadoop-is-not-a-database · **Arc:** Orientation (hub) · **Status:** planned
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** When does one PostgreSQL server stop being the right tool for a dataset, and what does the distributed data stack put in its place, layer by layer?
- **Assumes:** No prior part. SELECT, WHERE and GROUP BY. Readers with no SQL start at the PostgreSQL spine's SQL-from-scratch part, which is a cross-series link, not a dependency.
- **Hands off:** Each layer goes to its arc: HDFS to 2, batch compute to 3 and 8, tables as directories to 4, object storage to 5, file formats to 6, table formats to 11, engines to 15, the log to 16, modeling to 19, the architecture choice to 22. HBase and the other engines are named once and handed to `database-engines`.
- **Worked example:** One query, 'revenue per customer for 2025', over the series' seeded orders data at three sizes: 1 GB, 100 GB and 10 TB. Measured on the build machine: one NVMe's sequential read rate R using dd iflag=direct, which bypasses the page cache and needs no root; and the 1 GB case run in DuckDB over CSV and over Parquet, with bytes read captured for each run. Modelled, labelled and with inputs stated: 10 TB / R on one disk against the same bytes spread over 100 disks, and the bytes a query touching 2 of 12 columns needs in row versus column layout. The post closes with a PostgreSQL-versus-Hadoop table in which every row names its mechanism: 8 KB page vs 128 MiB block, MVCC row versions vs write-once files, WAL vs edit log, B-tree vs no index, postmaster vs ResourceManager, schema-on-write vs schema-on-read.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E3; access: none. A uv venv with duckdb and the series generator (gen_data.py, seeded), plus a 4 GiB scratch file read with dd iflag=direct. About 2 GB of disk and under 1 GiB of RAM. No JVM, no services.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "is hadoop a database", "hadoop vs postgresql", "when do you need big data tools", "oltp vs olap"

### Part 2 — How HDFS Stores a File: Blocks, Replicas and the NameNode's Log

- **Slug:** how-hdfs-stores-a-file · **Arc:** The Hadoop foundation · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** When a client writes a 1 GiB file into HDFS, where do its bytes and its metadata end up, and how does the cluster notice and heal a dead or corrupt replica?
- **Assumes:** Part 1's layer map and scan arithmetic (the anchor is fixed when Part 1 is written).
- **Hands off:** Input splits and data locality for computation go to Part 3, the NameNode heap cost of small files to Part 4, rename semantics and erasure coding to Part 5, and Kerberos to Part 14. NameNode HA (quorum journal, ZKFC, fencing) is one body section of mechanism here; the live fencing demonstration is Part 16's leader-epoch experiment.
- **Worked example:** A 1 GiB file written with dfs.blocksize 128 MiB and replication 3 to a four-DataNode pseudo-cluster. The DataNodes sit on 127.0.0.2-.5, split into two simulated racks by a topology script. That gives 8 blocks and 24 replicas. Placement is read from hdfs fsck -files -blocks -locations -racks and checked against the default policy: the writer's node, then a node on a remote rack, then a second node on that rack. The write pipeline in numbers: 64 KB packets and a 4-byte CRC32C per 512 bytes, a 0.78% checksum overhead that shows up as a .meta file beside each blk_ file. The NameNode's edit log is read with hdfs oev (OP_ADD, OP_ADD_BLOCK and OP_CLOSE records with their txids), and its fsimage with hdfs oiv after a saveNamespace checkpoint. Then kill -9 one DataNode: it is declared dead after 2 x 300 s recheck + 10 x 3 s heartbeat = 630 s, and the under-replicated count falls to 0 (count and duration captured). Finally, one byte flipped in a blk_ file on disk: the client read fails over to another replica, and the bad replica is reported and replaced.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E5; access: None required. The optional 'multi-machine cluster' request covers placement across real hosts and network-bound pipeline throughput.. A JDK 17/21 tarball and the Hadoop 3.4.3 or 3.5.0 binary tarball under ~/.cache/data-at-scale-lab. One NameNode (512 MB heap), one Secondary NameNode (256 MB) and four DataNodes (256 MB each) on loopback aliases. Each daemon starts with hdfs --daemon start, because no sshd is listening and start-dfs.sh cannot be used. About 2 GiB of RAM and 4 GB of disk. Failures are injected with kill -9 and by editing a block file.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "how hdfs works", "hdfs block replication explained", "namenode edit log fsimage", "hdfs replica placement policy"

### Part 3 — From hadoop jar to _SUCCESS: How MapReduce Runs on YARN

- **Slug:** how-mapreduce-runs-on-yarn · **Arc:** The Hadoop foundation · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** How does a group-by run across machines: who asks for containers, where does map output spill, and exactly what crosses the network in the shuffle?
- **Assumes:** Part 2's block layout and read path, because input splits are blocks and locality is block placement.
- **Hands off:** Spark's removal of per-stage materialisation goes to Part 8, SQL over these jobs to Part 4, and Spark resource management to Parts 8 and 10. The Fair Scheduler, node labels and YARN federation are named only.
- **Worked example:** Revenue per customer over a 1.25 GiB (10-block) orders file gives 10 input splits and 10 map tasks. The ApplicationMaster's container requests and grants are read from the ResourceManager log and REST API. Map side: mapreduce.task.io.sort.mb = 100 MB with a spill at 80%, so the spill files per map are predicted from map output bytes and checked against the Spilled Records and Map output bytes counters. The same job is then run with a combiner, and shuffle bytes before and after are captured. Reduce side: 2 vs 8 reducers, and a Zipf-skewed customer that turns one reducer into the straggler (task durations captured). YARN arithmetic: containers per NodeManager from yarn.nodemanager.resource.memory-mb and a 512 MB container size after rounding to yarn.scheduler.minimum-allocation-mb. Two Capacity Scheduler queues at 70/30 with elasticity, and one job borrowing the idle queue's capacity. A Hadoop Streaming version with a Python mapper and reducer means no Java is required.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E5; access: None required. The optional 'multi-machine cluster' request covers real network shuffle bytes and locality ratios.. Part 2's cluster trimmed to three DataNodes, plus a ResourceManager (512 MB), two NodeManagers offering 1.5 GB each and the JobHistory server. Containers are 512 MB, at most 4 at once. About 4 GiB of RAM in total, so the README checks free memory before starting. Python 3 for the Streaming variant.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "how mapreduce works", "mapreduce shuffle and sort explained", "yarn architecture explained", "yarn container memory calculation"

### Part 4 — Tables Made of Directories: Hive, the Metastore and the Small-Files Problem

- **Slug:** hive-metastore-small-files-problem · **Arc:** The Hadoop foundation · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How does a directory of files become a SQL table, and why does that design break under many partitions, many small files and concurrent writers?
- **Assumes:** Part 2's NameNode, which holds all metadata in one heap.
- **Hands off:** The fix, snapshot metadata over immutable files, goes to Part 11, object-store listing cost to Part 5, and file layout for skipping to Part 7. Hive ACID, LLAP and Tez are named once.
- **Worked example:** orders becomes an external table partitioned first by order_date (365 directories), then by (order_date, region) (365 x 20 = 7,300 directories), in Spark SQL with Hive support and an embedded Derby metastore. The metastore's own tables (DBS, TBLS, SDS, PARTITIONS, PARTITION_KEY_VALS) are queried to show what a table actually is. One query runs with a partition predicate and one without, capturing partitions fetched from the metastore and files listed. The same 10 GB is then written as 40 files of 256 MB and as 100,000 files of 100 KB. For each, the post counts NameNode objects (files plus blocks) and heap at the ~150 bytes/object rule of thumb, labelled as a rule of thumb, and measures scan time on the pseudo-cluster. MSCK REPAIR TABLE is timed. Finally, an INSERT OVERWRITE writer is killed half-way while a second session reads: the reader sees a partial partition. That is the correctness failure that motivates table formats.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E4; access: none. Part 2's HDFS pseudo-cluster plus a Spark 4.x tarball in local mode with enableHiveSupport and Spark's embedded Derby metastore. No PostgreSQL is needed, so the shared PG lab is never touched. About 3 GiB of RAM, and about 25 GB of disk for the two 10 GB layouts.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "hive metastore explained", "small files problem hadoop", "hive partitioning how it works", "msck repair table"

### Part 5 — Object Storage Is Not a Filesystem: What Changes When HDFS Becomes S3

- **Slug:** object-storage-vs-hdfs · **Arc:** Storage for analytics · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** When the storage under your tables is an object store instead of HDFS, what breaks (rename, append, listing, job commit), and what gets cheaper (erasure coding, compute that scales separately from storage)?
- **Assumes:** Part 2's rename-as-metadata-operation and replication.
- **Hands off:** Why table formats never rename or list goes to Part 11, credential scoping to Part 14, and warehouse storage-compute separation to Part 22. Keeping images, logs and documents in a lake gets one section (an object plus a metadata table); multimodal formats are out of scope.
- **Worked example:** One Spark job's 200 output files are committed two ways: to HDFS, and through S3A to a local MinIO with four drive directories in one erasure set at EC:2. Request counts from mc admin trace show FileOutputCommitter's rename phase as a COPY plus a DELETE per file, where HDFS does one NameNode metadata rename. The S3A magic committer replaces that phase with multipart-upload completion (requests and time captured). A 1,000-object 'directory rename' is timed on both stores. Storage overhead is worked as arithmetic, then checked with du: HDFS 3x replication is 3.0x, HDFS RS-6-3 is 1.5x, and MinIO EC:2 over 4 drives is 2.0x. One MinIO drive directory is removed and reads still succeed. AWS facts are quoted with dates and labelled documented, not measured: strong read-after-write consistency since December 2020, and 3,500 PUT/COPY/POST/DELETE plus 5,500 GET/HEAD requests per second per prefix.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E4; access: None required. The optional 'AWS S3 sandbox bucket' request covers throttling, real latency and per-request cost.. The MinIO and mc static binaries bound to 127.0.0.1 only, never minio.canery.in. hadoop-aws and the AWS SDK bundle from the Hadoop tarball's share/hadoop/tools/lib, Part 2's HDFS, and Spark 4.x in local mode. About 3 GiB of RAM and 5 GB of disk.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "hdfs vs s3", "s3a committer explained", "why is rename slow on s3", "object storage erasure coding"

### Part 6 — Parquet from the Bytes Up: Row Groups, Pages, Encodings and the Footer

- **Slug:** parquet-file-format-internals · **Arc:** Storage for analytics · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 16
- **Answers:** What is inside a Parquet file, byte by byte, and why does a query over two of twelve columns read only a small fraction of it?
- **Assumes:** Part 1's row-versus-column argument.
- **Hands off:** Using statistics to skip across many files goes to Part 7, field IDs and schema evolution at table level to Part 11, and access control to Part 14. Parquet modular encryption is named only. ORC, Avro and Arrow get one comparison section each, not depth.
- **Worked example:** 1,000,000 rows of the series' orders are written with pyarrow using zstd and explicit per-column encodings. The last 8 bytes are read by hand: a 4-byte little-endian footer length followed by 'PAR1'. A ~100-line script decodes the Thrift-compact FileMetaData into row groups, column chunks, offsets and min/max/null_count statistics, cross-checked with DuckDB's parquet_metadata(). One column chunk is shown per encoding: status (5 distinct values) as a dictionary page plus RLE/bit-packed 3-bit indices, order_id as DELTA_BINARY_PACKED, and note as plain plus zstd, each with bytes before and after encoding. A nested items list is decoded for three rows into repetition and definition levels. The same rows are then written as CSV, Parquet, ORC, Avro and Arrow IPC, capturing file size and the time to read 2 columns. The PostgreSQL heap size for the same row count is computed from PG Part 3's rows-per-page arithmetic, not measured.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E5; access: none. A uv venv with pyarrow, fastavro, duckdb and the series generator, plus a small pure-Python Thrift-compact decoder. Under 2 GiB of RAM and about 2 GB of disk. No JVM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "parquet file format explained", "parquet row group size", "parquet dictionary encoding rle", "parquet vs orc vs avro"

### Part 7 — Reading Less: Partitioning, Sorting, Z-Order and File Size

- **Slug:** data-layout-partitioning-sorting-zorder · **Arc:** Storage for analytics · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How should a large table's rows be arranged across files and row groups so that a selective query skips most of them?
- **Assumes:** Part 6's row-group statistics.
- **Hands off:** Manifest-level pruning and hidden partitioning go to Part 11, bucketed joins to Part 9, and engine-side pushdown to Part 15.
- **Worked example:** 100,000,000 orders rows are laid out five ways: unsorted, partitioned by month, sorted by customer_id, Z-ordered on (customer_id, order_date) and Hilbert-ordered. Three queries run against each layout: customer_id = 92399 (the PG series' customer), a one-week order_date range, and both together. For every layout-and-query pair the post captures files opened, row groups read and skipped, bytes read and wall time, from DuckDB EXPLAIN ANALYZE and parquet_metadata(). A sweep of target file sizes (8 MB, 128 MB, 1 GB) follows. A UUID column shows min/max skipping nothing, then a Parquet bloom filter skipping row groups. The Z-order bit interleave is computed by hand for two 4-bit keys so the curve is visible.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E4; access: none. DuckDB (memory_limit 2 GB) and pyarrow in a uv venv; the generator writes the 100M rows in chunks. About 30 GB of disk across the five layouts and about 2 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "z-order clustering explained", "parquet predicate pushdown", "partitioning vs bucketing", "optimal parquet file size"

### Part 8 — How Spark Runs a Job: Lineage, Stages, Shuffles and Executors

- **Slug:** how-spark-runs-a-job · **Arc:** Spark · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** What does Spark do between an action and its result: how is a program cut into stages and tasks, where does data move, and how is a lost partition rebuilt without a log?
- **Assumes:** Part 3's shuffle.
- **Hands off:** Catalyst, joins and AQE go to Part 9, and memory regions, skew and spill tuning to Part 10. Structured Streaming appears in Part 18's contrast section. Spark on Kubernetes is named, with the optional container access request.
- **Worked example:** Part 3's revenue per customer is rewritten as RDD code and as a DataFrame over the same 1.25 GiB input. The result is one job, two stages, 10 map-side tasks and 200 planned shuffle partitions (the spark.sql.shuffle.partitions default), which AQE coalesces. The coalesced count is captured and the reason left to Part 9. Lineage comes from toDebugString, shuffle write and read bytes from the event log and REST API, and cache() is shown with the storage memory it takes. On a standalone master with two workers on loopback aliases, one executor is killed with kill -9 mid-stage and only its tasks re-run (count captured). The job's wall time is compared with Part 3's MapReduce run, and each reason is named and measured where possible: no HDFS materialisation between stages, long-lived executor JVMs, and pipelined narrow transformations.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E5; access: None required. Optional requests: 'multi-machine cluster' for a real network shuffle, and 'container access' for Spark on Kubernetes.. The Spark 4.2.0 tarball on JDK 17/21, first in local[*], then as a standalone master with 2 workers (1.5 GB each) on loopback aliases, optionally submitted to Part 3's YARN. About 3.5 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "how spark works internally", "spark stages vs tasks", "spark vs mapreduce", "spark lineage fault tolerance"

### Part 9 — Inside Spark SQL: Catalyst, Join Strategies and Adaptive Query Execution

- **Slug:** spark-sql-catalyst-joins-aqe · **Arc:** Spark · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** How does Spark turn a SQL query into a physical plan, how does it pick a join strategy, and what does adaptive execution change while the query is running?
- **Assumes:** Part 8's stages and exchanges.
- **Hands off:** Executor memory and spill go to Part 10, and Trino's pipelined alternative to stage-at-a-time execution to Part 15.
- **Worked example:** One query (orders joined to customers and regions, filtered to one year, grouped by region) is walked through EXPLAIN EXTENDED/FORMATTED: parsed, analyzed, optimized and physical. The optimized plan shows the predicate pushed into the Parquet scan, columns pruned and constants folded. The join is forced three ways on the same data, capturing shuffle bytes and time for each: broadcast hash (spark.sql.autoBroadcastJoinThreshold, default 10 MB), sort-merge and shuffle-hash. Then AQE off vs on: the 200 shuffle partitions are coalesced, a sort-merge join is demoted to broadcast once the filter has shrunk customers, and skew-join handling splits the partition of the Zipf-hot customer. Cost-based join reordering is compared on and off, with ANALYZE TABLE statistics. The generated Java for one whole-stage-codegen stage is shown as an excerpt.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E5; access: none. Spark 4.2.0 in local[*] with a 4 GB driver heap, over 10M-row orders and 1M-row customers from the generator. About 5 GB of disk. No cluster needed.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "spark catalyst optimizer explained", "spark broadcast join threshold", "adaptive query execution spark", "sort merge join vs broadcast hash join"

### Part 10 — Tuning Spark: Memory, Partitions, Skew and Spill, Measured

- **Slug:** spark-performance-tuning-measured · **Arc:** Spark · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 12
- **Answers:** Why is this Spark job slow or out of memory, and which change fixes it, proven by a measurement rather than a folklore setting?
- **Assumes:** Part 8's executors, tasks and shuffle.
- **Hands off:** Table-level small-file compaction goes to Part 12. Cluster sizing on real hosts and Kubernetes dynamic allocation are named, with the optional access requests.
- **Worked example:** One deliberately bad job is fixed in five steps: a skewed join, 200 shuffle partitions over 2 GB, an executor sized to fail and 100,000 tiny output files. Each step is a before/after row of wall time, shuffle bytes, spill (memory and disk), peak executor memory, GC time and files written, all captured. The memory arithmetic for a 4 GB executor at Spark defaults, to be re-checked for 4.2: (4096 - 300 reserved) x 0.6 = 2,277.6 MB of unified memory, half of it storage-protected (1,138.8 MB), plus overhead of max(384 MB, 10%) = 409.6 MB, so the container asks for about 4,506 MB. The partition count comes from input size / 128 MB. Skew is fixed by AQE and, separately, by salting. The output file count is fixed with a repartition before the write.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E4; access: None required. Optional requests: 'multi-machine cluster' for network-bound shuffle numbers, and 'container access' for Kubernetes executors.. Spark standalone with two 2 GB workers on loopback aliases. Every run's event log is kept and summarised by a script into captures.md. About 4 GiB of RAM, so the README checks free memory before starting.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "spark performance tuning", "spark executor out of memory", "how many shuffle partitions spark", "spark data skew fix"

### Part 11 — How Apache Iceberg Works: Snapshots, Manifests and the Atomic Commit

- **Slug:** how-apache-iceberg-works · **Arc:** Open table formats · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** How does a pile of immutable Parquet files become a table with atomic commits, snapshot isolation, schema and partition evolution, and time travel?
- **Assumes:** Part 4's directory tables and their partial-overwrite failure.
- **Hands off:** UPDATE, DELETE, MERGE and table maintenance go to Part 12, Delta and Hudi to Part 13, and REST catalogs and access control to Part 14. Spec v3 features go to Part 12 (deletion vectors, row lineage) and Part 6 (variant).
- **Worked example:** An Iceberg orders table (PyIceberg, a SQL catalog on SQLite and a local warehouse directory) goes through five commits: create; append 1M rows; append 1M more; add a column; evolve the partitioning from month to day. After each commit every new file is listed and read: vN.metadata.json, the snap-*.avro manifest list, each manifest decoded with fastavro, and the data files they point to. A one-day query is planned with and without its predicate, capturing manifests and data files read vs skipped. Time travel goes back to snapshot 2. Two writers load the same metadata and both append: the second commit fails its assert-ref-snapshot-id requirement and retries, which makes the compare-and-swap visible. Write-audit-publish: a batch is written to branch audit, a check fails, and main never sees it; a passing batch fast-forwards main. That step uses Spark if PyIceberg's branch writes are missing at the pinned version.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E5; access: none. A uv venv with pyiceberg[sql-sqlite,pyarrow] and fastavro, over a local-filesystem warehouse. Optional cross-check in Spark 4.x with the matching iceberg-spark-runtime jar (version matrix verified at research). Under 2 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "how iceberg works", "iceberg metadata manifest list explained", "iceberg snapshot isolation", "iceberg hidden partitioning"

### Part 12 — Updating an Immutable Lake: Copy-on-Write, Merge-on-Read and Table Maintenance

- **Slug:** copy-on-write-merge-on-read-table-maintenance · **Arc:** Open table formats · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** How does a table built from files that are never modified support UPDATE, DELETE and MERGE, and what must run afterwards so that reads and storage do not degrade?
- **Assumes:** Part 11's snapshots and manifests.
- **Hands off:** Delta's and Hudi's versions of the same trade-off go to Part 13. Streaming upserts with equality deletes go to Parts 17 and 18.
- **Worked example:** Customer 92399 is erased from twelve monthly partitions of orders, as a GDPR request would require. Copy-on-write rewrites every data file that holds a matching row (files and MB rewritten, captured). Merge-on-read writes position-delete files instead (count and KB) and, where the pinned engine supports spec v3, a deletion vector in a Puffin file. Read cost is measured after 1, 10 and 100 merge-on-read deletes (delete files applied per scan, and time). A MERGE INTO updating 1% of rows runs under both modes. Then maintenance, in its required order: rewrite_data_files, rewrite_manifests, expire_snapshots, remove_orphan_files, with file counts and bytes before and after. The GDPR trap is proved on disk. Before expiry, time travel still returns 92399's rows and grep still finds the bytes. After expiry and orphan removal, both are gone. One equality-delete example shows how streaming writers delete by key.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E5; access: none. Spark 4.x in local[*] with the iceberg-spark-runtime jar and the Iceberg SQL extensions, over a local warehouse. The engine/format version matrix is pinned at research and may mean Spark 4.0/4.1 if 4.2 support lags. About 3 GiB of RAM and 10 GB of disk.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "copy on write vs merge on read", "iceberg delete files explained", "gdpr delete data lake", "iceberg compaction expire snapshots"

### Part 13 — Iceberg, Delta Lake and Hudi: Three Answers to the Same Commit Problem

- **Slug:** iceberg-vs-delta-lake-vs-hudi · **Arc:** Open table formats · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** How do Delta Lake and Apache Hudi record a commit differently from Iceberg, and which design suits which workload?
- **Assumes:** Part 11's metadata tree as the baseline.
- **Hands off:** Catalog interoperability goes to Part 14. Vendor platform features (Databricks, Onehouse, managed Iceberg services) are named only.
- **Worked example:** The same three operations are applied to the same data as Iceberg, Delta and Hudi tables: insert 1M rows, update 1% of them, delete customer 92399. The three file trees are shown side by side. Delta: _delta_log/00000000000000000000.json onward, with its add, remove, metaData and protocol actions; a Parquet checkpoint at the checkpoint interval (default 10 commits, re-checked for the pinned release); table features and deletion vectors. Hudi: the .hoodie timeline's requested, inflight and completed instants; the record-key index; a merge-on-read table's log files and the compaction that folds them back in; and an incremental query for 'what changed since instant T'. For each format the post captures metadata bytes written per operation and data files rewritten. Metadata translation (Delta UniForm or Apache XTable) is shown once, if it runs on the pinned versions.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E4; access: none. Delta via the deltalake (delta-rs) Python package, which runs anywhere. Hudi via Spark with the hudi-spark bundle; this may need Spark 3.5.9 if Hudi lags Spark 4, so the lab can carry two Spark versions. Iceberg via Part 12's setup. About 3 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "iceberg vs delta vs hudi", "delta lake transaction log explained", "apache hudi merge on read", "open table formats comparison"

### Part 14 — The Catalog Decides: Commits, Access Control and Credentials in a Lakehouse

- **Slug:** lakehouse-catalog-access-control · **Arc:** Open table formats · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** Who decides what a table is and who may read it? How a lakehouse catalog serves commits, many engines and access control, and how Hadoop answered the same question with Kerberos.
- **Assumes:** Part 11's catalog pointer swap.
- **Hands off:** Warehouse-native governance (Snowflake, Unity Catalog inside Databricks) is named and compared in Part 22. Encryption at rest and key management are named only. Lineage beyond one OpenLineage event is out of scope.
- **Worked example:** One Iceberg table sits in a REST catalog running in user space (Apache Polaris with in-memory persistence is the candidate, confirmed at research) over a local MinIO. Spark and PyIceberg both write to it, and a stale writer's commit is rejected with the failed requirement shown in the REST response. A principal holding SELECT on one table but not on its namespace reads that table and is refused the other. Credential vending: the reader receives a scoped, expiring credential and cannot read another table's prefix with it (feasibility on MinIO's STS is verified at research). The Hadoop answer is shown as a sequence: a Kerberos ticket to the NameNode, a delegation token carried by a YARN job, HDFS POSIX ACLs, and Ranger-style row filters and column masks. The Spark job's OpenLineage run event is shown as JSON.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E4; access: none. A JDK, the REST catalog server (Polaris is the candidate), MinIO on 127.0.0.1, and Spark local mode plus PyIceberg. Kerberos is described, not run, unless Hadoop's MiniKdc test KDC runs in user space (checked at research). About 3 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "iceberg rest catalog explained", "what is a data catalog in a lakehouse", "apache polaris vs unity catalog", "hadoop kerberos delegation token"

### Part 15 — How Trino Runs One SQL Query Across Many Machines

- **Slug:** how-trino-executes-a-query · **Arc:** Query engines and architecture · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,000 · **Figures:** 15
- **Answers:** How does a distributed SQL engine that owns no storage cut one query into stages, splits and exchanges across workers, and where does the time go?
- **Assumes:** Part 7's pruning and pushdown.
- **Hands off:** The choice between warehouse, lake and lakehouse goes to Part 22. The internals of ClickHouse and DuckDB as engines go to `database-engines`.
- **Worked example:** A coordinator and two heap-capped workers on loopback aliases, with the Iceberg connector over the orders and customers tables from Parts 11-12 and the PostgreSQL connector pointed at a throwaway PostgreSQL cluster. One join-plus-aggregate is run through EXPLAIN (TYPE DISTRIBUTED) and EXPLAIN ANALYZE, capturing fragments, split counts, rows and bytes across each exchange, and CPU vs wall time per stage. The same query runs with join_distribution_type BROADCAST and then PARTITIONED. Dynamic filtering is turned on and off, capturing probe-side rows read from orders. A federated join pushes its filter down, and the exact SQL the connector sent is read from the throwaway cluster's log. Fault-tolerant execution (retry-policy=TASK with local exchange spooling) is tested by killing one worker mid-query: the query still finishes, and the retried task count is captured.
- **Lab:** G2 · local service (Local-service-in-user-space. The federated leg needs-access: a throwaway PostgreSQL cluster.); ladder E1–E5; access: Optional: 'multi-machine cluster' for network-bound exchange numbers.. The Trino server tarball with whatever JDK its release requires (verified at research; possibly newer than the series' JDK 17/21). Coordinator plus 2 workers at about 1.5 GB of heap each. Iceberg is reached through Part 14's REST catalog or a file-based metastore. About 4.5 GiB of RAM, so it is captured in the RAM window.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "how trino works", "trino explain analyze distributed", "trino dynamic filtering", "trino vs spark"

### Part 16 — Kafka Is a Log: Partitions, Replication and Exactly-Once

- **Slug:** how-kafka-works-log-replication · **Arc:** Streaming · **Status:** planned
- **Tier:** L4 · **Difficulty:** intermediate · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** What is a Kafka topic on disk, how does replication decide what is committed, and what exactly does 'exactly once' guarantee?
- **Assumes:** No in-series prerequisite; Part 1 is optional.
- **Hands off:** Kafka Connect, Debezium and schema registries go to Part 17, and stateful processing to Part 18. Tiered storage and multi-cluster replication (MirrorMaker 2) are named only.
- **Worked example:** Three combined broker/controller KRaft nodes run on 127.0.0.2-.4, a topology suitable only for a lab. Topic order_events has 6 partitions and replication factor 3. Produce 1M records, then read one partition's segment with kafka-dump-log: base-offset file names, batches, and sparse .index/.timeindex entries roughly every log.index.interval.bytes = 4,096 bytes. Latency and throughput are captured for acks=0, 1 and all. With min.insync.replicas=2, kill -9 one broker: the ISR shrinks and producing still succeeds. Kill a second: NotEnoughReplicas. SIGSTOP a partition leader: a new leader is elected with a higher leader epoch, and the stale state of the old leader is fenced when it resumes. With unclean leader election and acks=1, acknowledged records are lost, and the loss is counted. The post also shows idempotent-producer sequence numbers; a transactional read-process-write in which read_committed consumers never see the aborted batch; a cooperative rebalance with consumer lag before and after; and a compacted keyed topic keeping only the latest value per key.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E5; access: none. The Kafka 4.x tarball on JDK 17/21: three KRaft processes at 512 MB of heap each, with log directories on disk. About 2.5 GiB of RAM. Failures are injected with kill -9 and SIGSTOP/SIGCONT.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "how kafka works internally", "kafka isr high watermark", "kafka exactly once semantics", "kafka log compaction"

### Part 17 — From PostgreSQL to the Lake: Change Data Capture with Debezium, Kafka and Iceberg

- **Slug:** cdc-postgresql-debezium-kafka-iceberg · **Arc:** Streaming · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 15
- **Answers:** How do row changes committed in PostgreSQL arrive in the lake as an up-to-date table, in order, with exactly-once effect?
- **Assumes:** Part 16's offsets, compaction and transactions.
- **Hands off:** Stateful stream joins and windows go to Part 18. Slot management and slot failover go to the PostgreSQL spine.
- **Worked example:** A throwaway PostgreSQL cluster (wal_level=logical, with its own port and data directory) holds orders. The Debezium PostgreSQL connector runs on a one-worker Kafka Connect cluster and takes an initial snapshot of 100,000 rows, then streams 10,000 updates and deletes. One change event is shown whole (before, after, op, ts_ms, source.lsn, txId), and its LSN is tied back to PG Part 3's LSN arithmetic. Events are Avro through an Apache-2.0 schema registry (Apicurio is the candidate): one backward-compatible column add is accepted and one incompatible type change is rejected. The sink writes into Iceberg, using the Iceberg Kafka Connect sink, or Spark Structured Streaming with foreachBatch MERGE if the sink lacks upsert support at the pinned version. Source and lake row counts match. Kafka Connect is killed with kill -9 mid-stream; on restart the re-delivered duplicates are counted, and the keyed MERGE leaves the counts equal. The connector is then stopped through an hour of writes, and the slot's retained WAL grows, measured with pg_replication_slots on the throwaway cluster. That is the production outage pattern. The outbox pattern is shown with one table.
- **Lab:** G3 · needs access (Needs-access (approval to run a throwaway PostgreSQL cluster), plus local-service-in-user-space for Kafka, Connect and the sink.); ladder E1–E5; access: none (a disposable PostgreSQL is self-provisioned). A throwaway PostgreSQL 16/18 on 127.0.0.1:55433, from the pgserver binaries or a PG 18 source build, never the shared ~/.cache/blog-pg-lab server. Part 16's Kafka reduced to one broker, Kafka Connect with the Debezium 3.x jars, a schema registry JAR, and Spark or the Iceberg sink. About 5 GiB of RAM, so it is captured in the RAM window; the legs can also run one after another.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "debezium postgres kafka tutorial", "cdc to data lake iceberg", "replication slot wal retention debezium", "outbox pattern debezium"

### Part 18 — Stream Processing with Flink: Event Time, Watermarks, State and Checkpoints

- **Slug:** flink-event-time-watermarks-checkpoints · **Arc:** Streaming · **Status:** planned
- **Tier:** L4 · **Difficulty:** advanced · **Est. words:** 9,500 · **Figures:** 16
- **Answers:** How does a stream processor compute correct windowed results from late, out-of-order events, and survive a crash without counting anything twice?
- **Assumes:** Part 16's offsets and transactions.
- **Hands off:** The LSM internals of the RocksDB state backend go to `database-engines`. Streaming writes into Iceberg with equality deletes are linked to Part 12. Flink SQL and CEP are named only.
- **Worked example:** order_events come from a fixed-seed generator that injects known lateness (for example, 5% of events arrive 0-3 minutes late), and are counted in 5-minute tumbling revenue windows. Watermarks at max event time minus 30 s and minus 2 min are compared against the generator's ground truth per window, with late events either dropped or routed to a side output (counts captured). Keyed state per customer is compared on the heap backend and on RocksDB, by state size and checkpoint size. Aligned checkpoints run every 10 s with alignment time captured, then unaligned checkpoints run under backpressure from a slowed sink. The TaskManager is killed with kill -9 and restored from the last checkpoint with Kafka offsets rewound. With the two-phase-commit Kafka sink and read_committed consumers the output has zero duplicates; without it, the duplicates are counted. The same window in Spark Structured Streaming gives a micro-batch contrast (latency per trigger). Lambda vs Kappa gets one section.
- **Lab:** G2 · local service (local-service-in-user-space); ladder E1–E5; access: none. The Flink 2.x tarball on JDK 17 (verified at research): a JobManager and one TaskManager (1.5 GB), with Part 16's Kafka reduced to one broker, and Spark local mode for the contrast run. About 3.5 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "flink watermarks explained", "flink checkpoint exactly once", "event time vs processing time", "flink vs spark structured streaming"

### Part 19 — Modeling Data for Analytics: Grain, Facts, Dimensions and Slowly Changing History

- **Slug:** dimensional-modeling-star-schema-scd · **Arc:** Pipelines and modeling · **Status:** planned
- **Tier:** L3 · **Difficulty:** beginner · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** How do you reshape an application's normalized tables into a model that answers business questions correctly, including questions about the past?
- **Assumes:** No in-series prerequisite; Part 1 is optional.
- **Hands off:** Building and testing the model with dbt goes to Part 20. Where the model lives (warehouse or lakehouse) goes to Part 22.
- **Worked example:** The PG series' customers and orders, plus order_items, products and regions in third normal form, are reshaped into fact_order_lines (grain: one row per order line), dim_customer, dim_product and dim_date. A customer moves from Pune to Bengaluru on 1 June. Type 1 overwrites the city; Type 2 adds a row with valid_from, valid_to and is_current, and the rows are shown. 'Revenue by customer city at time of order' runs in DuckDB under both and gives different totals, with the Type 1 answer wrong for the first five months. A fan-out trap follows: joining two facts at different grains double-counts revenue, shown and then fixed. The same data is sketched as One Big Table and as Data Vault hubs, links and satellites, and mapped onto bronze, silver and gold layers.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E4; access: none. The DuckDB CLI or Python duckdb with the seeded generator. SQL files only. Under 1 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "dimensional modeling star schema", "slowly changing dimension type 2", "fact table grain", "kimball vs data vault", "medallion architecture"

### Part 20 — How dbt Works: Models, the ref Graph, Incremental Loads and Tests

- **Slug:** how-dbt-works-incremental-models · **Arc:** Pipelines and modeling · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** What does dbt actually do with a folder of SELECT statements, and why do incremental models and snapshots go wrong without an error?
- **Assumes:** Part 19's star schema.
- **Hands off:** Scheduling, retries and backfills go to Part 21. Quality gates at the table level (write-audit-publish) are linked to Part 11.
- **Worked example:** Part 19's star schema becomes a dbt project on DuckDB: 3 sources, 3 staging, 2 intermediate and 4 mart models, 12 in all. dbt compile shows the Jinja-rendered SQL and the manifest.json DAG. The actual DDL for each materialization (view, table, incremental, ephemeral) is read from the logs. An incremental fact built with the naive updated_at > max(updated_at) filter misses late-arriving rows, and the row count is off by exactly the late rows; a lookback window plus a unique_key merge fixes it. dbt snapshot builds dim_customer as Type 2 (dbt_valid_from, dbt_valid_to) from the Pune-to-Bengaluru change. unique, not_null and relationships tests run, and one failing test stops a build. A model contract rejects a type change. In slim CI, state:modified+ selects 3 of the 12 models.
- **Lab:** G1 · runs anywhere (runs-anywhere); ladder E1–E4; access: none. A uv venv with dbt-core and dbt-duckdb (versions pinned at research) and one DuckDB file. Under 1 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "how dbt works", "dbt incremental models explained", "dbt snapshot scd type 2", "dbt tests and contracts"

### Part 21 — Airflow Without Surprises: Data Intervals, Backfills and Idempotent Tasks

- **Slug:** airflow-data-intervals-backfills-idempotency · **Arc:** Pipelines and modeling · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,000 · **Figures:** 11
- **Answers:** How does Airflow decide when a task runs and for which slice of data, and how do you make a pipeline safe to retry and backfill?
- **Assumes:** Part 20's dbt project, which the DAG runs.
- **Hands off:** Celery and Kubernetes executors are named, with the optional container access request. Dagster and Prefect are named as alternatives in one section.
- **Worked example:** A daily DAG extracts one day of orders from the generator, loads it into a date-partitioned table and runs dbt build. With start_date seven days back, the seven DAG runs are printed with their data_interval_start and data_interval_end. Catchup runs, then a three-day backfill. The load is first written as an append: a simulated failure after the write triggers an automatic retry, and one day's rows double (counts shown). Rewritten as a partition overwrite (or MERGE), the same retry and a repeated backfill leave the counts identical. A sensor is compared with a deferrable operator running on the triggerer process. Asset-based scheduling starts the dbt DAG when the load's asset updates. A heavy top-level import slows the scheduler's DAG parse, timed before and after the fix.
- **Lab:** G2 · local service (Local-service-in-user-space. Needs-access only if the pinned Airflow release requires PostgreSQL for its metadata database.); ladder E1–E4; access: None if SQLite suffices; otherwise approval for a throwaway PostgreSQL cluster. Optional: container access for the Kubernetes executor.. Airflow 3.x in a uv venv with its constraints file, run with airflow standalone. The metadata DB is SQLite if the release supports it for the executor used; otherwise a throwaway PostgreSQL cluster, never the shared lab. About 2 GiB of RAM.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "airflow data interval explained", "airflow backfill", "idempotent airflow tasks", "airflow catchup"

### Part 22 — Warehouse, Lake or Lakehouse: Where Analytics Data Should Live

- **Slug:** warehouse-vs-lake-vs-lakehouse · **Arc:** Query engines and architecture · **Status:** planned
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 7,500 · **Figures:** 12
- **Answers:** How do cloud warehouses, data lakes and lakehouses separate storage from compute, and which one fits a given workload, team and budget?
- **Assumes:** Part 15's distributed query engine.
- **Hands off:** Nothing; this part closes the series. The internals of warehouse engines as database engines (ClickHouse, DuckDB) go to `database-engines`.
- **Worked example:** One workload: 5 TB of order history, 50 GB of new data a day, 40 analysts, and 20 dashboards refreshing hourly that scan about 200 GB a day. It is costed under three published pricing models from the providers' price pages, each dated: per-TB scanned on demand, per-credit-second virtual warehouses, and provisioned cluster hours. The result is a break-even table and its sensitivity to pruning, using the byte reduction measured in Part 7 as a model input. The architectures come from the papers: Snowflake (SIGMOD 2016: micro-partitions, metadata pruning, virtual warehouses), BigQuery/Dremel (VLDB 2010 and 2020: disaggregated shuffle) and Redshift (SIGMOD 2022: RA3 managed storage). The open stack built in this series (MinIO + Iceberg + Trino) is measured at small scale on the dashboard query. A decision table closes the post: latency, concurrency, openness, governance, operations cost, lock-in.
- **Lab:** G1 · runs anywhere (Runs-anywhere for the cost model; local-service-in-user-space for the open-stack measurement. Optional needs-access (BigQuery sandbox) for one measured managed-warehouse query.); ladder E1–E4; access: None required. Optional: 'managed warehouse accounts' (a BigQuery sandbox, optionally a Snowflake trial).. A Python cost model in which every price is a dated input, plus the Part 15 stack for the local measurement. About 4 GiB of RAM during that step.
- **Key sources:** chosen in this part's research phase (Checkpoint A), not before.
- **Search intent:** "data warehouse vs data lake vs lakehouse", "snowflake architecture explained", "lakehouse architecture", "bigquery vs snowflake cost"

## Publication order and cadence

Starts after PostgreSQL Foundations' core (Part 32) is live, or interleaves with its later arcs —
the owner's call. Within this series, a part may publish once the one part it names under
**Assumes** is live. Versions are pinned at each part's research time from dated primary sources
(the 2026-09-28 currency check is in the build scratchpad, not here).

## Cross-links

PostgreSQL Foundations Part 39 (CDC: queues, the outbox and CDC out of PostgreSQL) hands the change stream to Part 17 here; Part 41 (FDWs, Parquet and Iceberg from PostgreSQL) hands the table format to Part 11; Part 40 (analytics in PostgreSQL) is the single-node baseline Part 1 argues past; Part 7 of the PostgreSQL series (schema design) is the normalized model Part 19 reshapes. Links run only from the later-published part. Published parts are never edited to add forward links.

## Lab policy

Graded per blog-forge `references/labs.md` (G0–G3, ladder E1–E5); the probe and requests are in
`access.md`. Everything installable in user space is self-provisioned and never asked for — JDK
and Hadoop/Kafka/Spark/Trino tarballs, static binaries, source builds into a user prefix, a
disposable local PostgreSQL. The build machine has ~5 GB RAM free at idle and no Docker access.

### Access requests (answer each: `grant`, `decline` or `later`)

| ID | Need | Parts | Smallest arrangement | If declined |
|---|---|---|---|---|
| AR-02 | A capture window with about 8 GiB of RAM free | 15, 17, 18 (and 3 and 10 if free memory is below their budgets) | A scheduled two-hour window per heavy part, with other heavy sessions closed and the shared PostgreSQL lab idle (not stopped). | Run each leg separately with smaller heaps at the 1M-row scale, and state the scale and heap in the provenance line. |
| AR-03 | Multi-machine cluster time | 2, 3, 8, 10, 15 (optional legs) | Four cloud VMs (4 vCPU, 16 GB, local SSD) in one zone for one afternoon per thread (Hadoop, Spark, Trino), torn down afterwards, with a budget alarm. | Every mechanism is still demonstrated for real on the loopback pseudo-cluster. Network-bound numbers become labelled models with stated inputs and an unrun harness, the NVIDIA series' pattern. |
| AR-04 | An AWS S3 sandbox bucket | 5 (optionally 14, for credential vending on real STS) | One bucket in a sandbox account, one IAM user scoped to it, and a $5 budget alarm; everything deleted after capture. | MinIO is measured locally for API and committer behavior. AWS limits and prices are quoted from dated AWS documentation and labelled documented, not measured. |
| AR-05 | Managed warehouse accounts | 22 (optional) | A BigQuery sandbox project (no billing account) with one table of the generator's data loaded; optionally one Snowflake trial. | A cost model built from dated price pages and the vendor papers, with the open stack measured locally. Every managed-warehouse number is labelled documented. |
| AR-01 (shared with postgresql-foundations) | Container access (docker group or rootless podman) | 8, 10, 21 (optional) | Add the user to the docker group once, or enable rootless podman, so kind can run one control-plane node and two workers. | The standalone and YARN deployments are shown, and each part's Limitations says the Kubernetes deployment is not demonstrated. |

## What this series will not cover

- Machine-learning platforms: feature stores, MLOps, model training on Spark (MLlib is named only). The ML series pair covers models.
- BI and visualization tools (Superset, Tableau, Power BI, Looker), and semantic layers beyond one mention in Part 22.
- Data mesh, team topology and the design of data organizations.
- Operating data systems on Kubernetes (Spark, Flink and Strimzi operators, Helm) beyond naming the deployment mode.
- Retired Hadoop-era tools (Pig, Oozie, Sqoop, Flume, Mahout, Giraph) beyond one line of history in Part 1.
- HBase and Bigtable-style wide-column stores, which go to `database-engines` with LSM trees and Cassandra.
- Hive LLAP, Tez and Impala internals; Hive ACID tables are named once in Part 4.
- Real-time OLAP stores (Druid, Pinot) and ClickHouse/DuckDB engine internals, which go to `database-engines`.
- Console walkthroughs of managed services (EMR, Dataproc, Databricks, Glue, Synapse, Fabric); concepts only.
- Geospatial and graph processing at scale (Iceberg geometry types, GraphX).
- Multimodal lake formats such as Lance, and vector search over lakes. Vector search goes to the PG spine (pgvector) and `database-engines`.
- Multi-region replication and disaster recovery for Kafka and lakes (MirrorMaker 2, cross-region table replication) beyond naming them.
- PostgreSQL's own logical decoding, replication slots, FDWs and lake extensions, which the PG spine owns.
- Vendor certification paths, and current prices beyond Part 22's dated snapshots.

## Risks

- Size. 22 parts, eleven of them L4, about 176,000 words in all. Mitigation: build the 15-part core first; the seven leaf spokes (5, 10, 13, 14, 18, 21, 22) can be deferred without breaking any dependency. Fan out research early, as the research-fan-out lessons say.
- Memory. About 4-5 GiB is free at idle, and multi-JVM labs can swap and falsify timings. Every lab caps its heaps and checks free memory before starting, and the three heaviest (15, 17, 18) need the capture window.
- Version-matrix churn. Spark 4.2.0 is about ten weeks old and Hadoop 3.5.0 about six months. The Iceberg Spark runtime, Hudi and Debezium may not yet support the newest Spark or Java, and spec v3 features (deletion vectors, row lineage, variant) are unevenly supported across engines. Each lab pins its matrix at research and may carry Spark 3.5.9 alongside 4.x.
- No containers. Nearly every upstream quickstart (Iceberg, Trino, Kafka Connect, Polaris, Airflow) assumes Docker, and tarball setups for Polaris, the Hudi bundle, Debezium and the Iceberg Kafka Connect sink are fiddly. A one-day lab spike should come before Parts 13, 14 and 17 are committed.
- Single-machine distortion. Loopback networking and one NVMe overstate throughput and hide network cost. Any number that depends on the network is labelled 'single machine' or 'modelled', never presented as cluster behavior.
- Shared PostgreSQL lab. Parts 15, 17 and possibly 21 need PostgreSQL. A slip that pointed them at ~/.cache/blog-pg-lab could restart or fill the live server (a wal_level change, WAL retained by a slot). Only a throwaway cluster on its own port may be used, and each run script enforces that.
- Hadoop relevance. Some readers treat Hadoop as legacy. Each Hadoop-arc part must say what carried forward (HDFS to object-store semantics, the shuffle to Spark and Trino exchanges, YARN to Kubernetes scheduling, the metastore to Iceberg's catalogs) so the posts read and rank as current.
- Vendor bias. Table-format and warehouse comparisons are dominated by vendor marketing. Parts 13 and 22 must rest on specs, papers and the same-data lab, never on vendor benchmark posts alone.
- Licensing. Confluent Schema Registry and some connectors are under the Confluent Community License, which is not OSI-approved. Prefer Apache-2.0 components (Apicurio) and state the licence of everything used.
- Cross-series link timing. PG Parts 2 and 3 are not confirmed live, and posts may link only to published URLs. Links to Part 2 and 3 anchors are added only once those parts are live.
- Boundary drift with `database-engines` and with the PG spine (CDC, FDW and lake integration, partitioning). The boundary must be recorded in context.md at Checkpoint S.
- Kerberos feasibility. A KDC may not run in user space. If Hadoop's MiniKdc does not run, Part 14 shows Kerberos as a sequence without a lab, and says so.
