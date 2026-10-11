# Canery Series Roadmap — The Specialization Map

**Status:** publication-level plan · rebuilt 2026-10-11 · decisions closed (see *Decisions*) ·
nothing new is built until a series' own Checkpoint S.
**What this is:** the single map of what Canery publishes — every category (a whole subject), every
series inside it, what each series covers, how the series connect, and the order they are built in.
Private build artifact, like `plan.md`: never linked, never published.

---

## How the map works

1. **A category is a whole subject.** Databases, Networking, Deep Learning — each is a discipline a
   reader can specialise in. The category set is what the site registers.
2. **A category holds many series.** No single series can make a reader an expert in a subject, so
   each subject is divided at the seams where an expert's *job* changes — modelling a schema is not
   operating a cluster, routing is not wireless — and each piece becomes its own standalone series
   with its own lab, search audience and hub part.
3. **Series sizes follow the subject, not a template.** A series is as long as its facet needs:
   8 parts for a tight facet, 20+ for a deep one. Part counts below are estimates, fixed at that
   series' Checkpoint S.
4. **Existing series come first.** The nine series that already exist keep their plans; the 15 posts
   already built but not yet published are the top of the queue; new series are designed around them
   and say which existing parts they assume.
5. **Every series says what it assumes and what it feeds.** That is how a reader moves from one series
   to the next, and how two series avoid teaching the same mechanism twice.
6. **One standard: expert.** The reader is a working engineer or specialist. Every part reconciles
   on real numbers, derives the condition, measures what can be measured, and corrects one claim that
   circulates without its condition. No beginner layer, in prose or in labs.
7. **Already-built blogs are not touched.** Any fix to a built post is listed for the owner, never
   applied silently.

---

## Decisions (closed)

Closed on the owner's instruction to decide them; each is the call this map is built on.

1. **Twelve categories.** `databases`, `data-engineering`, `data-science`, `machine-learning`,
   `deep-learning`, `computer-vision`, `nlp`, `agentic-ai`, `networking`, `security`, `system-design`,
   `algorithms`. The live `engineering` category is left as it is and unused by these series.
2. **Big Data and Data Warehousing are series families inside `data-engineering`**, not categories:
   readers navigate by role (data engineer), and two extra categories would split the same reader
   across three pages. Their posts carry the tags `big-data` and `data-warehousing`, so both still
   get a tag page.
3. **The ML / DL boundary.** Neural networks — mechanics, architectures, training, generative models,
   LLMs — are `deep-learning`. Classical algorithms, theory, probabilistic ML, reinforcement learning,
   recommender systems and ML systems are `machine-learning`. Statistics, experiments, causality and
   analytics are `data-science`.
4. **Re-filing existing series:** foundational-architectures and frontier-models → `deep-learning`;
   image-processing and diffusion-models → `computer-vision`; data-at-scale → `data-engineering`.
   nvidia-stack stays `machine-learning` (settled in its own plan). postgresql-foundations and
   database-engines stay `databases`; search-algorithms stays `algorithms`.
5. **Checkpoint S for the existing planned series is approved as planned**, with three updates:
   postgresql-foundations' unbuilt Day-0 parts (6–10) are written at the expert standard and its
   Part 7 narrows to PostgreSQL's key/constraint mechanics, pointing to DB-3 for modelling theory;
   data-at-scale's Parts 1 and 19 are re-levelled from beginner and its "analytics from scratch"
   path is dropped; foundational-architectures assumes DL-1 for the general mechanics and promotes
   BERT (its optional Part 18) to committed. search-algorithms commits Parts 1–15 and keeps 16–18 as
   a later wave.
6. **nvidia-stack Part 4 is built now** as a G1 labelled model plus an unrun G3 harness, captured
   later if a GPU is granted — the series' own no-GPU rule. frontier-models applies the Laya Part 2
   correction recorded in its `context.md` before Part 2 is researched.
7. **Labs.** G1 by default and self-provisioned. One container/network-namespace capability request
   covers every Docker-dependent series; it is raised once, when the first of them (NET-1) starts, and
   until it is granted those series ship documented topologies plus captures from a single granted run.
   Agent labs default to a local model; an API key is requested only if a specific part needs one.
8. **Security stays exactly as it is** (section 10, unchanged text). Expanding it into more series is
   deferred to a session on Opus 4.8, per the owner.
9. **The thirteen non-security draft `plan.md` files written earlier on 2026-10-11 are superseded** by
   this map and removed from `posts/` (copy kept in the session scratchpad). Each series gets its real
   `plan.md` at its own Checkpoint S. The four security plans are untouched.
10. **blog-forge's category list** (`frontmatter.md` and `CATEGORIES` in `validate_post.py`) gains the
    new keys when the first post in a new category is built; today the validator only warns.

---

## Owner actions (the only things that need your hands)

These are uploads, production writes or edits to built posts — everything the rule "don't touch built
blogs" and the production-write rule reserve for you.

- **Publish the built queue (Wave 0 below):** upload images and labs to MinIO, fill `urls.txt`, run
  `fill_urls.py`, publish. Before upload, four built posts need an owner edit or go-ahead:
  postgresql-foundations Part 3 ("third and last post" wording); Part 4 (one temporary-cluster run to
  regenerate `lab/captures.md`); diffusion-models Part 2 (`series` keys and the cover); nvidia-stack
  Part 6 (cover, figure and lab placeholders). Say *go* on any of them and it is done.
- **Category rows** (production write), ready to insert — `PUT {prefix}/admin/categories`:

  | key | label | description |
  |---|---|---|
  | `databases` | Databases | Data modelling, SQL, internals and operations — PostgreSQL and every other engine. |
  | `data-engineering` | Data Engineering | Pipelines, big data, streaming, warehousing and the lakehouse. |
  | `data-science` | Data Science | Statistics, experimentation, causal inference, forecasting and analytics. |
  | `machine-learning` | Machine Learning | ML algorithms and theory, reinforcement learning, recommender systems and ML systems. |
  | `deep-learning` | Deep Learning | Neural networks: how they learn, the architectures, training at scale and LLMs. |
  | `computer-vision` | Computer Vision | Image processing, recognition, 3-D geometry, video and generative vision. |
  | `nlp` | Natural Language Processing | Text, language structure, retrieval, LLM applications, translation and speech. |
  | `agentic-ai` | Agentic AI | Building, connecting, evaluating and securing AI agents. |
  | `networking` | Networking | Every layer of the network, from the wire to the data centre and the cloud. |
  | `security` | Security | Cryptography, defensive security and secure engineering. |
  | `system-design` | System Design | Large-scale system design: building blocks, guarantees, reliability and case studies. |
  | `algorithms` | Algorithms | Algorithms and data structures — the price, the condition and the measurement. |

  (`databases` exists with the label "DataBase"; `machine-learning` and `databases` have no description.)
- **Re-file the eight live posts** to their new categories (decision 4) and fix the live series titles
  ("Nvidia", "Postgresql") and empty descriptions — one admin session.
- **The container capability** when NET-1 starts (docker group, rootless podman, or confirmed `unshare -rn`).

---

## The category map

106 series across 12 categories: 9 existing, 4 security plans (unchanged), 93 new. Status:
**live** (has published parts), **built** (parts built, unpublished), **planned** (has a `plan.md`),
**mapped** (in this map only; `plan.md` written at its Checkpoint S).

| Category | Series | Count |
|---|---|---|
| `databases` | DB-1 postgresql-foundations *(live)* · DB-2 database-engines *(planned)* · DB-3 Relational Data Modeling: ERD to Normal Forms · DB-4 Data Modeling Patterns & Beyond Relational · DB-5 Advanced SQL Patterns · DB-6 Transactions, Isolation & Concurrency Control · DB-7 Build a Database From Scratch | 7 |
| `data-engineering` | DE-1 data-at-scale *(planned, hub)* · DE-2 Apache Spark in Depth · DE-3 Streaming Systems in Depth · DE-4 Data Warehousing & Dimensional Modeling · DE-5 The Lakehouse in Depth · DE-6 Pipelines, Orchestration & DataOps · DE-7 Data Quality, Observability & Governance | 7 |
| `data-science` | DS-1 Statistics for Data Scientists · DS-2 Experimentation & A/B Testing · DS-3 Causal Inference · DS-4 Time Series & Forecasting · DS-5 Data Wrangling at Expert Level · DS-6 Visualization & Communicating Results · DS-7 Product Analytics & Metrics | 7 |
| `machine-learning` | ML-1 nvidia-stack *(live)* · ML-2 Classical ML Algorithms · ML-3 Learning Theory · ML-4 Probabilistic ML · ML-5 RL Foundations · ML-6 Deep RL · ML-7 Recommender Systems & Ranking · ML-8 ML Systems & MLOps | 8 |
| `deep-learning` | DL-1 Deep Learning Foundations · DL-2 foundational-architectures *(planned)* · DL-3 frontier-models *(built)* · DL-4 Optimization for DL · DL-5 Generative Models · DL-6 Self-Supervised Learning · DL-7 Training & Scaling · DL-8 Efficient DL · DL-9 LLM Engineering · DL-10 Graph Neural Networks · DL-11 Interpretability | 11 |
| `computer-vision` | CV-1 image-processing *(live)* · CV-2 diffusion-models *(live)* · CV-3 Object Detection · CV-4 Segmentation · CV-5 Multiple View Geometry · CV-6 3D Vision & Neural Rendering · CV-7 Visual SLAM · CV-8 Video Understanding · CV-9 OCR & Document AI · CV-10 Human-Centric Vision | 10 |
| `nlp` | NLP-1 Text Processing & Tokenization · NLP-2 Statistical NLP · NLP-3 Syntax, Semantics & Structure · NLP-4 Embeddings · NLP-5 Information Retrieval & Search · NLP-6 RAG · NLP-7 LLM Applications · NLP-8 Machine Translation & Multilingual · NLP-9 Speech & Audio · NLP-10 Evaluating Language Systems | 10 |
| `agentic-ai` | AG-1 Building Agentic Systems · AG-2 Agentic AI Security *(planned, unchanged)* · AG-3 Memory & Context Engineering · AG-4 Multi-Agent Systems · AG-5 Agent Protocols & Infrastructure · AG-6 Agent Evaluation & Reliability · AG-7 Coding & Computer-Use Agents · AG-8 Reasoning & Planning Foundations | 8 |
| `networking` | NET-1 TCP/IP Internals · NET-2 Ethernet, Switching & the LAN · NET-3 Routing Protocols · NET-4 Internet Architecture · NET-5 DNS in Depth · NET-6 HTTP, TLS & QUIC · NET-7 Linux Networking Internals · NET-8 Data Center Networking · NET-9 Network Virtualization & SDN · NET-10 Cloud & Kubernetes Networking · NET-11 Wireless & Mobile · NET-12 Performance & Troubleshooting · NET-13 Network Automation | 13 |
| `security` | SEC-1 Applied Cryptography *(planned)* · SEC-2 Defensive Security *(planned)* · SEC-3 Secure Engineering *(planned)* — unchanged | 3 |
| `system-design` | SD-1 Foundations: Estimation & Trade-offs · SD-2 Scalability Building Blocks · SD-3 Distributed Systems for Designers · SD-4 API & Interface Design · SD-5 Event-Driven Architecture · SD-6 Microservices · SD-7 Reliability Engineering (SRE) · SD-8 Observability Engineering · SD-9 Designing Data-Intensive Systems · SD-10 Case Studies | 10 |
| `algorithms` | ALG-1 search-algorithms *(live)* · ALG-2 Algorithm Design & Analysis · ALG-3 Sorting & Selection · ALG-4 Data Structures in Depth · ALG-5 Graph Algorithms · ALG-6 Dynamic Programming · ALG-7 Advanced String Algorithms · ALG-8 Randomized & Streaming · ALG-9 Computational Geometry · ALG-10 Optimization Algorithms · ALG-11 Parallel & Concurrent · ALG-12 Performance Engineering | 12 |

---

## Build order, category by category

**Wave 0 — finish what is built (top priority, before any new series).** 15 posts are built and
unpublished; they are the cheapest value in the whole map.

| Category | Built, waiting to publish | Then continue with |
|---|---|---|
| `databases` | DB-1 Parts 3, 4, 5 (in that order) | DB-1 Part 6 onward |
| `computer-vision` | CV-2 Parts 2→6 (2 first); CV-1 Parts 3–6 | CV-2 Part 7; CV-1 Part 8 (Canny) |
| `machine-learning` | ML-1 Parts 3 and 6 | ML-1 Part 4 (G1 model + harness), then 5 |
| `deep-learning` | DL-3 Part 1 (Laya) | DL-3 Part 2 |
| `algorithms` | (hub live) | ALG-1 Part 3 |

**Then, inside each category** (existing series continue in parallel; the order is for new series):

| Category | Order |
|---|---|
| `databases` | DB-1 (continue) → **DB-3 ERD** → DB-5 → DB-2 → DB-4 → DB-6 → DB-7 |
| `data-engineering` | DE-1 → DE-4 → DE-2 → DE-3 → DE-6 → DE-5 → DE-7 |
| `data-science` | DS-1 → DS-2 → DS-3 → DS-5 → DS-4 → DS-7 → DS-6 |
| `machine-learning` | ML-1 (continue) → ML-2 → ML-8 → ML-7 → ML-5 → ML-6 → ML-4 → ML-3 |
| `deep-learning` | DL-3 (continue) → DL-1 → DL-2 → DL-7 → DL-8 → DL-9 → DL-5 → DL-6 → DL-4 → DL-11 → DL-10 |
| `computer-vision` | CV-1, CV-2 (continue) → CV-3 → CV-4 → CV-5 → CV-8 → CV-6 → CV-7 → CV-9 → CV-10 |
| `nlp` | NLP-1 → NLP-4 → NLP-5 → NLP-6 → NLP-7 → NLP-2 → NLP-3 → NLP-8 → NLP-9 → NLP-10 |
| `agentic-ai` | AG-1 → AG-3 → AG-5 → AG-6 → AG-4 → AG-7 → AG-8 → AG-2 (on Opus 4.8, after the container grant) |
| `networking` | NET-1 → NET-7 → NET-5 → NET-6 → NET-3 → NET-2 → NET-12 → NET-9 → NET-10 → NET-8 → NET-4 → NET-13 → NET-11 |
| `security` | SEC-1 → SEC-2 → SEC-3 (unchanged; SEC-2/3 after the container grant) |
| `system-design` | SD-1 → SD-2 → SD-3 → SD-10 → SD-4 → SD-7 → SD-5 → SD-6 → SD-9 → SD-8 |
| `algorithms` | ALG-1 (continue) → ALG-2 → ALG-4 → ALG-5 → ALG-6 → ALG-3 → ALG-8 → ALG-12 → ALG-11 → ALG-10 → ALG-7 → ALG-9 |

**The first new series per category** (what starts right after Wave 0): DB-3, DE-4, DS-1, ML-2, DL-1,
CV-3, NLP-1, AG-1, SD-1, ALG-2 — all G1, no access needed — then NET-1 once the container capability
is granted. Across categories, the recommended single next start is **DB-3 (the ERD series)**: it is
the most-requested gap and it feeds DB-1, DE-1 and DE-4.

---

## How the series connect

**Bridges between categories** — the links that make the map one publication:

| From | To | What carries over |
|---|---|---|
| DB-1 postgresql-foundations | DE-1 data-at-scale | every data-at-scale layer is contrasted with a PostgreSQL mechanism (pages, WAL, MVCC, vacuum) |
| DB-3 ERD | DE-4 warehousing, DB-1 Part 7 | 3NF modelling is what dimensional modelling reshapes; PG Part 7 applies DB-3 in PostgreSQL |
| DB-6 transactions | SD-3 distributed systems | isolation anomalies become cross-service consistency problems |
| DB-2 engines, DE-3 streaming | SD-9, SD-5 | engine and log internals underpin the system-level designs |
| DS-1 statistics | ML-2, DS-2…DS-7 | estimation, testing and regression are assumed everywhere downstream |
| ML-2 classical ML | DL-1, ML-7, ML-8 | bias–variance, validation and calibration carry into nets, recsys and production |
| ML-4 probabilistic ML | DL-5 generative models → CV-2 diffusion | ELBO and score matching lead into diffusion |
| DL-1 foundations | DL-2 architectures → CV-3/4, NLP-8 | backbones and the Transformer feed recognition and translation |
| DL-3 frontier models | DL-9 LLM engineering → NLP-7 → AG-1 | model internals → training pipeline → applications → agents |
| NLP-5 retrieval | ALG-1 (HNSW, WAND), DB-2 (Lucene, vector DBs) | the index structures behind search |
| ML-1 nvidia-stack | DL-7, DL-8, ML-8, NET-8 | the hardware view of training, inference and AI-cluster fabrics |
| CV-1 image-processing | CV-5, NLP-9 | the DFT and gradients reappear as multi-view features and audio spectra |
| NET-6 web protocols, NET-7 Linux networking | SEC-1, SEC-2 | TLS on the wire; firewalls in the kernel |
| ALG-1 search, ALG-5 graphs | AG-8 planning, DL-10 GNNs | A\* and graph structure under agents and graph learning |
| ALG-4 data structures, ALG-8 sketches | DB-7, DE-7 | hashing, B-trees and sketches inside engines and data-quality checks |

**Reading paths by role** — one route through the map for each specialist the site serves:

| Role | Path |
|---|---|
| Database engineer | DB-3 → DB-1 → DB-5 → DB-6 → DB-2 → DB-4 → DB-7 |
| Data engineer | DB-1 (core) → DB-3 → DE-1 → DE-4 → DE-2 → DE-3 → DE-5 → DE-6 → DE-7 → SD-5 |
| Data scientist | DS-1 → DS-5 → DB-5 → DS-2 → DS-3 → DS-4 → ML-2 → DS-7 → DS-6 |
| ML engineer | DS-1 → ML-2 → DL-1 → DL-2 → DL-7 → DL-8 → ML-8 → ML-1 → ML-7 |
| Deep learning / LLM engineer | DL-1 → DL-2 → DL-3 → DL-4 → DL-7 → DL-9 → DL-8 → DL-11 → NLP-7 |
| Computer vision engineer | CV-1 → DL-1 → DL-2 → CV-3 → CV-4 → CV-5 → CV-6 → CV-8 → CV-2 |
| NLP engineer | NLP-1 → NLP-4 → DL-2 → NLP-5 → NLP-6 → NLP-7 → NLP-10 → NLP-2 → NLP-3 |
| Agentic AI engineer | NLP-7 → AG-1 → AG-3 → AG-5 → AG-6 → AG-4 → AG-7 → AG-2 |
| Network engineer | NET-1 → NET-2 → NET-3 → NET-5 → NET-6 → NET-7 → NET-12 → NET-8 → NET-9 → NET-10 → NET-13 |
| Backend / platform engineer | SD-1 → SD-2 → SD-3 → DB-6 → SD-4 → SD-7 → SD-5 → SD-6 → SD-10 |
| Security engineer | SEC-1 → SEC-2 → SEC-3 → AG-2 |
| Algorithms specialist | ALG-2 → ALG-4 → ALG-1 → ALG-5 → ALG-6 → ALG-3 → ALG-8 → ALG-12 |

---

## Cross-cutting policy (every new series)

1. **Expert standard, no beginner layer.** Labs stay executable-or-precise, never dumbed down.
2. **Lab grades and the ladder** per `references/labs.md`. Self-provision anything user-space (uv,
   CPU wheels, source builds into `$HOME`, static binaries); raise an access request only when a
   load-bearing claim needs a capability the probe shows missing.
3. **The Docker-network lab (networking + security).** You confirmed "Docker network experimenting
   is enough" — so these build **isolated local Docker networks / network namespaces**, never
   against a real or remote host. But the probe shows **Docker unusable (no docker group)**, so
   those labs are **G2/G3 needing a capability**: one access request per series (docker group /
   rootless podman / `unshare -rn`). If declined, the topology ships as a documented diagram plus
   captured output from one granted run, or an unrun harness — never an invented number.
4. **Security framing.** The security category is **educational and defence-oriented**: how a
   weakness *class* works and **how it is detected and fixed**, lab-only against intentionally-
   vulnerable throwaway targets. No working exploit code, no operational how-tos (blog-forge's
   security subject-playbook). Detailed attack-class scoping happens at each security series'
   Checkpoint S, not in this broad doc.
5. **Explicit seams.** Each series names what it hands to a sibling so two series never teach the
   same mechanism. The boundary goes in `context.md` at Checkpoint S.
6. **Name earlier posts in plain text; you add the links.** No placeholder URLs.
7. **No production writes without go-ahead** — category rows, titles/descriptions, re-filing, uploads.

---

## 1 · Databases (`databases`) — 7 series

How data is modelled, queried, stored, kept consistent and operated: the whole database engineer's
craft. PostgreSQL is the spine (DB-1); database-engines covers every other engine (DB-2); the five new
series give the engine-agnostic depth an expert needs — and the ERD/data-modelling track the map was
missing.

### DB-1 · PostgreSQL Foundations — `postgresql-foundations` · 46 parts · G2 · **2 live, 3 built**
- **Covers:** internals in three layers (memory, processes, storage); the relational model, SQL
  evaluation, window functions/CTEs, schema and physical design, loading data, logic in the database;
  connections, pooling and security; the slow query (pg_stat_statements → EXPLAIN → statistics →
  executor → index design, B-tree and beyond); transactions, locks, zero-downtime migrations; backup
  and PITR, streaming and logical replication, failover, upgrades, migrations, corruption; observing,
  vacuum at scale, partitioning, capacity, tuning; extensions, JSONB, full-text, pgvector, PostGIS,
  time series, CDC, analytics, the lake; Citus, managed PostgreSQL, IaC, Kubernetes, incident runbooks.
- **Next:** publish Parts 3 → 4 → 5, then Part 6.
- **Update (decision 5):** unbuilt Day-0 parts written at the expert standard; Part 7 narrows to
  PostgreSQL's key/constraint mechanics and points to DB-3. Built parts untouched.

### DB-2 · Database Engines Beyond PostgreSQL — `database-engines` · 20 parts · G1–G2 · planned
- **Covers:** the five decisions every engine makes (hub); SQLite; InnoDB (undo, redo and binlog,
  doublewrite); LSM trees and compaction (RocksDB); Redis; MongoDB/WiredTiger; Lucene; vector databases
  (HNSW, quantisation, filtering); ClickHouse MergeTree; DuckDB vectorised execution; the Prometheus
  TSDB; graph databases; Cassandra and leaderless quorums; partition-key modelling; Raft inside the
  database; distributed SQL (CockroachDB); TrueTime, HLC and TSO; checking consistency claims.
- **Assumes:** DB-1 Parts 1–3 (each part contrasts with a PostgreSQL mechanism). **Feeds:** SD-3, SD-9.

### DB-3 · Relational Data Modeling: From ERD to Normal Forms — `relational-data-modeling-erd` · ~16 · G1 · mapped
**The ERD series.**
- **Covers:** conceptual → logical → physical modelling; ER constructs (entities; simple, composite,
  multivalued and derived attributes; relationships with cardinality and participation; weak entities;
  ternary relationships; ISA hierarchies with disjoint/overlapping and total/partial constraints) in
  Chen, Crow's Foot and UML notation; the mapping rules from each ER construct to relations; keys
  (candidate, natural vs surrogate, composite); functional dependencies, Armstrong's axioms, attribute
  closure and the minimal cover; 1NF → 2NF → 3NF → BCNF, 4NF (multivalued dependencies) and 5NF (join
  dependencies); lossless-join and dependency-preserving decomposition, 3NF synthesis vs BCNF
  decomposition; when and how to denormalise; reverse-engineering an ERD from a live schema. One
  domain is modelled end to end and reconciled against its own constraints.
- **Assumes:** DB-1 Part 4 (the relational model). **Feeds:** DB-1 Part 7, DB-4, DE-4.

### DB-4 · Data Modeling Patterns and Beyond Relational — `data-modeling-patterns` · ~12 · G1 · mapped
- **Covers:** hierarchies (adjacency list, nested sets, materialised path, closure table, `ltree`) with
  the query cost of each; polymorphic associations and their alternatives; EAV and why it fails;
  JSON columns vs columns; multi-tenant designs (shared table, schema per tenant, database per tenant);
  soft delete, audit and history tables; temporal and bitemporal modelling (valid vs transaction time,
  SQL:2011 periods); modelling money, time zones and identifiers; document modelling (embed vs
  reference, access-pattern first); single-table key-value design (DynamoDB); property graph vs RDF;
  schema evolution with expand/contract.
- **Assumes:** DB-3. **Feeds:** DB-2 Part 16 (partition keys), SD-9.

### DB-5 · Advanced SQL Patterns — `advanced-sql-patterns` · ~14 · G1 · mapped
- **Covers:** relational algebra as the mental model of a query; three-valued logic and NULL traps;
  set-based thinking; every join shape (semi, anti, lateral, self, non-equi, as-of); window-function
  patterns (running totals, ranking, top-N per group, sessionisation, gaps and islands); recursive
  CTEs (hierarchies, graph walks, series generation); GROUPING SETS, ROLLUP, CUBE; pivot and unpivot;
  deduplication and latest-row-per-key; MERGE and upsert semantics; writing SQL the optimiser can use
  (sargability, decorrelation); anti-patterns and their rewrites — verified on PostgreSQL and DuckDB.
- **Assumes:** DB-1 Parts 5–6. **Feeds:** DE-4, DS-7.

### DB-6 · Transactions, Isolation and Concurrency Control — `transactions-concurrency-control` · ~12 · G1–G2 · mapped
- **Covers:** serialisability and conflict graphs; two-phase locking and deadlock handling; timestamp
  ordering and OCC; MVCC designs compared (append-only, undo/delta, time travel); the anomaly catalogue
  (dirty read, non-repeatable read, phantom, lost update, write skew, read-only anomaly) with Adya's
  definitions; snapshot isolation vs serialisable SI; what each isolation name means in PostgreSQL,
  MySQL, Oracle and SQL Server; isolation in distributed databases; testing isolation claims (the
  Jepsen/Elle method). Every anomaly reproduced in two sessions.
- **Assumes:** DB-1 Part 18. **Feeds:** DB-2 Part 20, DB-7, SD-3.

### DB-7 · Build a Database From Scratch — `build-a-database-from-scratch` · ~22 · G1 · mapped
- **Covers:** a small relational engine built layer by layer in code: slotted pages and heap files; the
  buffer pool and replacement (LRU-K, clock); a B+tree with splits, merges and latch crabbing; hash
  indexes; WAL and ARIES recovery (analysis, redo, undo, CLRs); a lock manager and MVCC; the
  Volcano iterator vs vectorised execution; join algorithms (nested loop, sort-merge, hash, Grace hash);
  external sort; the optimiser (rewrite rules, histogram cardinality estimation, a cost model,
  Selinger dynamic programming, Cascades); a SQL front end. Each layer tested and benchmarked.
- **Assumes:** DB-1 Parts 1–3, DB-6. **Feeds:** DB-2, SD-9.

---

## 2 · Data Engineering (`data-engineering`) — 7 series

Building the systems that move, store and serve data at scale. data-at-scale (DE-1) is the hub: one
rung per layer of the modern stack. The six new series are the mastery tracks for each layer. Big
Data (DE-1, DE-2, DE-3) and Data Warehousing (DE-4) live here, tagged `big-data` and `data-warehousing`.

### DE-1 · Data at Scale: From Hadoop to the Lakehouse — `data-at-scale` · 22 parts · G1–G2 · planned · **hub**
- **Covers:** HDFS; MapReduce on YARN; Hive and the small-files problem; object storage vs HDFS;
  Parquet byte by byte; data layout (partitioning, sorting, Z-order); Spark execution, Catalyst/AQE and
  tuning; Iceberg's atomic commit; copy-on-write vs merge-on-read; Iceberg vs Delta vs Hudi; the
  lakehouse catalog; Trino; Kafka; CDC from PostgreSQL into Iceberg; Flink; dimensional modelling;
  dbt; Airflow; warehouse vs lake vs lakehouse.
- **Update (decision 5):** re-filed here; Parts 1 and 19 re-levelled; it is the part each deeper DE
  series assumes. **Assumes:** DB-1 core. **Feeds:** DE-2 … DE-7.

### DE-2 · Apache Spark in Depth — `apache-spark-in-depth` · ~16 · G2 · mapped
- **Covers:** DAGScheduler and TaskScheduler; shuffle internals (sort-based shuffle, the external
  shuffle service, push-based shuffle); Tungsten and the unified memory manager, on and off heap;
  Catalyst internals and writing an optimiser extension; whole-stage code generation; AQE internals;
  Data Source V2 and pushdown; PySpark internals (Py4J, Arrow, pandas UDFs) and Spark Connect;
  Structured Streaming's micro-batch and state store; Spark on Kubernetes; diagnosing any job from the
  UI and event logs.
- **Assumes:** DE-1 Parts 8–10. **Feeds:** DE-5, ML-8.

### DE-3 · Streaming Systems in Depth — `streaming-systems-in-depth` · ~18 · G2 · mapped
- **Covers:** the Dataflow model (event vs processing time, windows, watermarks, triggers, accumulation);
  what exactly-once guarantees and how (idempotence, transactions, two-phase-commit sinks); Kafka in
  depth (segments, ISR, KRaft, idempotent producers, transactions, the consumer-group protocol, tiered
  storage); Kafka Streams and stream–table duality; Flink internals (checkpoint barriers, state
  backends, savepoints, rescaling); stream joins, deduplication and enrichment; CDC in depth (Debezium,
  snapshots, the outbox); streaming databases (Materialize, RisingWave); real-time OLAP serving.
- **Assumes:** DE-1 Parts 16–18. **Feeds:** SD-5, ML-8.

### DE-4 · Data Warehousing and Dimensional Modeling — `data-warehousing-dimensional-modeling` · ~18 · G1–G2 · mapped
**The Data Warehousing series.**
- **Covers:** Inmon vs Kimball vs Data Vault; the bus matrix and conformed dimensions; fact-table
  types (transaction, periodic snapshot, accumulating snapshot, factless) and grain; SCD types 0–7 and
  when each fits; junk, degenerate, role-playing, outrigger and bridge dimensions; Data Vault 2.0 (hubs,
  links, satellites, PIT and bridge tables); ELT inside the warehouse; warehouse engine architecture
  (Snowflake micro-partitions and pruning, BigQuery/Dremel and Capacitor, Redshift RA3, ClickHouse as a
  warehouse); MPP execution and data distribution; materialised views and aggregate navigation; OLAP
  and the semantic layer; performance and cost governance.
- **Assumes:** DE-1 Part 19, DB-3. **Feeds:** DS-7.

### DE-5 · The Lakehouse in Depth — `lakehouse-in-depth` · ~14 · G1–G2 · mapped
- **Covers:** Parquet and ORC beyond the basics (page index, bloom filters, encodings, nested data);
  the Iceberg spec in depth (delete files, deletion vectors, row lineage, Puffin, branches and tags,
  variant); the Delta protocol (log, checkpoints, table features, deletion vectors, liquid clustering);
  Hudi (timeline, indexes, MoR compaction); catalogs (REST, Polaris, Unity, Nessie); multi-engine
  interoperability (XTable, UniForm); table maintenance at scale; lake performance engineering;
  multimodal and vector table formats (Lance).
- **Assumes:** DE-1 Parts 6–7, 11–14.

### DE-6 · Data Pipelines, Orchestration and DataOps — `data-pipelines-orchestration` · ~14 · G1–G2 · mapped
- **Covers:** pipeline design (idempotent, incremental, late data, backfills, reprocessing); ingestion
  patterns (files, APIs, CDC, events); orchestration internals (Airflow scheduler and executors,
  Dagster assets, Prefect) and when each fits; dbt in depth (materialisations, incremental strategies,
  macros, tests, contracts, slim CI); data contracts; CI/CD and environments for data; testing
  pipelines; reverse ETL; cost engineering for data.
- **Assumes:** DE-1 Parts 20–21. **Feeds:** DE-7, ML-8.

### DE-7 · Data Quality, Observability and Governance — `data-quality-governance` · ~12 · G1 · mapped
- **Covers:** quality dimensions and their measurement; testing data (assertions, expectations,
  contracts); anomaly detection on volume, freshness and distribution; data observability; lineage
  (OpenLineage, column level); catalogs and metadata; access control, PII classification, masking and
  tokenisation; retention and right-to-erasure in a lake; privacy-enhancing techniques (k-anonymity,
  differential privacy basics); ownership and data mesh.
- **Assumes:** DE-1 Part 14, ALG-8 (sketches).

---

## 3 · Data Science (`data-science`) — 7 series

Turning data into decisions: statistics, experiments, causality, forecasting, analysis and
communication. The algorithms of ML live in `machine-learning`; neural networks in `deep-learning`.

### DS-1 · Statistics for Data Scientists — `statistics-for-data-scientists` · ~16 · G1 · mapped
- **Covers:** distributions as generative stories; estimation, the bias and variance of estimators,
  MLE; sampling distributions and the CLT by simulation; confidence intervals and the bootstrap
  (percentile, BCa); hypothesis testing done right (power, effect size, what a p-value is not);
  choosing a test and its assumptions; multiple comparisons (FWER, FDR); Bayesian inference
  (conjugacy, MCMC, credible intervals); regression as an inferential model and its diagnostics; GLMs
  (logistic, Poisson, negative binomial); mixed-effects and hierarchical models; nonparametric methods.
- **Feeds:** every DS series, ML-2, ML-4.

### DS-2 · Experimentation and A/B Testing — `experimentation-ab-testing` · ~14 · G1 · mapped
- **Covers:** design and randomisation units; power, sample size and MDE; variance reduction (CUPED,
  stratification, regression adjustment); ratio metrics and the delta method; peeking and always-valid
  sequential tests; multiple metrics and guardrails; novelty and primacy effects; interference and
  network effects (cluster and switchback designs); heterogeneous treatment effects; interleaving for
  ranking; bandits vs fixed experiments; experimentation platforms; trustworthiness checks (SRM, A/A).
- **Assumes:** DS-1. **Feeds:** DS-3, ML-7.

### DS-3 · Causal Inference — `causal-inference` · ~14 · G1 · mapped
- **Covers:** potential outcomes; DAGs, d-separation, backdoor and front-door criteria; confounders,
  colliders and mediators (simulated); matching, propensity scores, IPW and doubly robust estimators;
  difference-in-differences including staggered adoption; regression discontinuity; synthetic control;
  instrumental variables and LATE; causal ML (meta-learners, double/debiased ML, uplift); sensitivity
  analysis.
- **Assumes:** DS-1, DS-2.

### DS-4 · Time Series Analysis and Forecasting — `time-series-forecasting` · ~14 · G1 · mapped
- **Covers:** decomposition and seasonality; stationarity, differencing, ACF/PACF; ARIMA and SARIMA;
  exponential smoothing; state-space models and the Kalman filter; hierarchical forecasting and
  reconciliation; intermittent demand; probabilistic forecasts and their scoring (pinball loss, CRPS);
  backtesting without leakage; gradient-boosted and neural forecasters; time-series anomaly detection;
  forecasting at scale.
- **Assumes:** DS-1. **Links:** DL-1 for neural forecasters.

### DS-5 · Data Wrangling at Expert Level — `data-wrangling-expert` · ~12 · G1 · mapped
- **Covers:** pandas internals (block manager, copy-on-write, Arrow-backed dtypes); Polars' lazy engine
  and query plans; the Arrow memory model; vectorisation and where it fails; joins and reshapes at
  scale; missing-data mechanisms (MCAR, MAR, MNAR) and principled imputation; outliers; sampling and
  selection bias; exploratory analysis as a method; out-of-core analysis with DuckDB; reproducible
  environments.
- **Feeds:** every DS and ML lab.

### DS-6 · Data Visualization and Communicating Results — `data-visualization-communication` · ~10 · G1 · mapped
- **Covers:** perception and encoding effectiveness (Cleveland–McGill); choosing a chart from the
  question; the grammar of graphics; honest uncertainty; dashboards that drive decisions;
  misleading-chart patterns; colour and accessibility; the decision memo; presenting to executives vs
  engineers.
- **Assumes:** DS-1.

### DS-7 · Product Analytics and Metrics — `product-analytics-metrics` · ~12 · G1 · mapped
- **Covers:** metric design and metric trees (north star, inputs, guardrails); funnels, cohorts and
  retention curves; LTV and unit economics; attribution (last touch to Shapley); segmentation;
  root-causing a metric move (decomposition, mix shift, Simpson's paradox); churn as survival analysis;
  the semantic layer and metric consistency.
- **Assumes:** DS-1, DB-5. **Links:** DS-2, DE-4.

---

## 4 · Machine Learning (`machine-learning`) — 8 series

ML as a discipline: algorithms, theory, probabilistic and reinforcement learning, recommender systems,
and the systems and GPU platform that run ML.

### ML-1 · The NVIDIA Stack — `nvidia-stack` · 16 parts · G1 + G3 (GPU) · **2 live, 2 built**
- **Covers:** what the stack is; the four CUDA version numbers; a GPU idle at 100% utilisation; five
  causes of one OOM; reading a GPU profile; architecture repairs (PyTorch, TensorRT-LLM, ONNX); what
  changes between generations; the memory hierarchy after TMA; one kernel four ways; what tensor cores
  execute; sizing VRAM for LLM serving; choosing an inference engine; Triton, Dynamo and NIM; why a
  multi-GPU job hangs; the parallelism decision; (opt) Jetson.
- **Next:** publish Part 3; Part 6 after its placeholders; Part 4 as G1 model + harness (decision 6).
- **Feeds:** DL-7, DL-8, ML-8, NET-8.

### ML-2 · Classical Machine Learning Algorithms — `classical-ml-algorithms` · ~18 · G1 · mapped
- **Covers:** the supervised setup and bias–variance; feature engineering and leakage; regularised
  linear and logistic models; decision trees; bagging and random forests; gradient boosting derived
  (XGBoost, LightGBM and CatBoost internals); SVMs and kernels; k-NN and the curse of dimensionality;
  naive Bayes, generative vs discriminative; clustering (k-means, GMM/EM, DBSCAN, hierarchical);
  dimensionality reduction (PCA, t-SNE, UMAP — and what they cannot show); cross-validation done right;
  metrics, thresholds and calibration; class imbalance; interpretability (SHAP, permutation, PD/ICE).
- **Assumes:** DS-1. **Feeds:** ML-3, ML-7, ML-8, DL-1.

### ML-3 · Learning Theory — `learning-theory` · ~10 · G0–G1 · mapped
- **Covers:** PAC learning; VC dimension and its bounds; Rademacher complexity; uniform convergence;
  approximation vs estimation error; regularisation as capacity control; algorithmic stability; online
  learning and regret (experts, multiplicative weights); no free lunch; why over-parameterised networks
  strain classical bounds (handed to DL-4).
- **Assumes:** ML-2.

### ML-4 · Probabilistic Machine Learning — `probabilistic-machine-learning` · ~14 · G1 · mapped
- **Covers:** Bayesian modelling; directed and undirected graphical models; exact inference (variable
  elimination, junction tree, belief propagation); approximate inference (Gibbs, HMC, variational
  inference and the ELBO); EM; mixture models; hidden Markov models; Gaussian processes; Bayesian
  optimisation; probabilistic programming.
- **Assumes:** DS-1. **Feeds:** DL-5.

### ML-5 · Reinforcement Learning Foundations — `reinforcement-learning-foundations` · ~12 · G1 · mapped
- **Covers:** MDPs and the Bellman equations; dynamic programming (policy and value iteration); Monte
  Carlo methods; TD learning; SARSA and Q-learning; eligibility traces; function approximation and the
  deadly triad; exploration (ε-greedy, UCB, Thompson sampling); multi-armed and contextual bandits.
- **Assumes:** DS-1. **Feeds:** ML-6.

### ML-6 · Deep Reinforcement Learning — `deep-reinforcement-learning` · ~14 · G1 · mapped
- **Covers:** DQN and its fixes (target networks, replay, double, dueling, distributional, Rainbow);
  policy gradients (REINFORCE, baselines, GAE); actor–critic; TRPO and PPO derived; SAC, DDPG and TD3
  for continuous control; model-based RL (Dyna, world models, MuZero); offline RL; multi-agent RL;
  RL from human feedback and GRPO in practice (derivations in DL-3); reward design and reproducibility.
- **Assumes:** ML-5, DL-1. **Links:** DL-3, DL-9.

### ML-7 · Recommender Systems and Ranking — `recommender-systems` · ~14 · G1 · mapped
- **Covers:** collaborative filtering; matrix factorisation (SVD, ALS, implicit feedback); content-based
  and hybrid models; two-tower retrieval and ANN serving; learning to rank (pointwise, pairwise,
  listwise, LambdaMART); sequential recommenders; the candidate generation → ranking → re-ranking
  architecture; offline (NDCG, recall@k) and counterfactual/off-policy evaluation; feedback loops,
  popularity bias and cold start; industrial architecture.
- **Assumes:** ML-2. **Links:** NLP-5, ALG-1 (ANN indexes), DS-2.

### ML-8 · ML Systems and MLOps — `ml-systems-mlops` · ~16 · G1–G2 · mapped
- **Covers:** the production ML lifecycle; feature stores and point-in-time correctness; training
  pipelines and experiment tracking; versioning data, code and models; serving patterns (batch, online,
  streaming) and their latency and cost; inference optimisation; monitoring (data drift, concept drift,
  decay); retraining strategies; CI/CD/CT for ML; testing ML systems; hidden technical debt in ML;
  designing an ML platform.
- **Assumes:** ML-2. **Links:** ML-1, DL-8, DE-3, DE-6.

---

## 5 · Deep Learning (`deep-learning`) — 11 series

Neural networks end to end: how they learn, the architectures, optimisation, training at scale,
generative and self-supervised learning, LLM engineering, efficiency, graphs and interpretability.
foundational-architectures and frontier-models move here (decision 4).

### DL-1 · Deep Learning Foundations — `deep-learning-foundations` · ~16 · G1 · mapped · **entry series**
- **Covers:** what an MLP computes; backpropagation by hand and a built-from-scratch autograd; losses
  as likelihoods; SGD and momentum; Adam and AdamW; initialisation (Xavier, He) from variance
  propagation; activations (ReLU → GELU → SwiGLU); normalisation (batch, layer, RMS, group) with the
  backward passes; regularisation (dropout, weight decay, label smoothing, augmentation); vanishing and
  exploding gradients; learning-rate schedules and warmup; generalisation and double descent;
  embeddings; the training loop and how to debug it.
- **Assumes:** ML-2 (bias–variance, validation). **Feeds:** every DL series.

### DL-2 · Foundational Architectures — `foundational-architectures` · 18 parts · G1 · planned
- **Covers:** LeNet-5 (shapes and FLOPs by hand; backprop through a CNN), AlexNet, VGG, Inception
  (1×1 bottlenecks; BatchNorm in context), ResNet (degradation; why residuals train), MobileNet, LSTM,
  seq2seq with Bahdanau attention, the Transformer (shape by shape; √d_k, positions, LayerNorm
  placement), ViT; optional ResNeXt/DenseNet/SE, EfficientNet, ConvNeXt; BERT (now committed).
- **Update (decision 5):** re-filed; assumes DL-1 for the general mechanics. **Feeds:** CV-3, CV-4,
  NLP-8, DL-3, DL-6.

### DL-3 · Frontier Models — `frontier-models` · 24 parts · G1 (+API) · **1 built**
- **Covers:** decision models (Laya ×3, Jev ×2); GPT (decoder-only, scaling laws, RLHF/PPO/DPO
  derived, gpt-oss); Llama (RMSNorm, SwiGLU, RoPE, GQA; context extension); mixture of experts;
  DeepSeek (MLA and MTP, sparse attention, R1 and GRPO); Mamba; Gated DeltaNet; JEPA ×4; CLIP; optional
  VLMs and DeepSeek mHC/Muon.
- **Next:** publish Laya Part 1; correct, then build Laya Part 2. **Feeds:** DL-9, NLP-7, AG-1.

### DL-4 · Optimization for Deep Learning — `deep-learning-optimization` · ~12 · G1 · mapped
- **Covers:** the loss-landscape geometry that matters (curvature, sharpness, saddles); SGD as noisy
  dynamics and the role of batch size; momentum theory; why Adam works and when it fails; second-order
  and preconditioned methods (K-FAC, Shampoo, Muon); sharpness-aware minimisation; schedules and warmup
  in theory; the critical batch size; μP and hyperparameter transfer; edge of stability and grokking.
- **Assumes:** DL-1, ML-3.

### DL-5 · Generative Models — `generative-models` · ~16 · G1 · mapped
- **Covers:** what modelling a distribution means; autoregressive models (PixelCNN, WaveNet, the LM
  view); VAEs (the ELBO derived, posterior collapse, β-VAE, VQ-VAE); GANs (the minimax game, mode
  collapse, WGAN, StyleGAN); normalising flows (change of variables, coupling layers, Glow);
  energy-based models and score matching (handed to CV-2 diffusion); flow matching and rectified flow;
  evaluation (likelihood vs FID and precision/recall).
- **Assumes:** DL-1, ML-4. **Feeds:** CV-2, DL-9.

### DL-6 · Self-Supervised and Representation Learning — `self-supervised-learning` · ~12 · G1 · mapped
- **Covers:** why labels are the bottleneck; contrastive learning and InfoNCE (SimCLR, MoCo);
  non-contrastive methods (BYOL, SimSiam, Barlow Twins, VICReg) and collapse; self-distillation (DINO,
  DINOv2); masked modelling (MAE, BEiT, data2vec); multimodal contrastive learning (CLIP's derivation is
  in DL-3); evaluation (linear probe, k-NN, fine-tune); dimensional collapse.
- **Assumes:** DL-1, DL-2 (ViT). **Links:** DL-3 (JEPA, CLIP). **Feeds:** CV-3, CV-4.

### DL-7 · Training and Scaling Deep Networks — `training-and-scaling-deep-networks` · ~14 · G1 core + documented multi-GPU · mapped
- **Covers:** where memory and FLOPs go in a training step; mixed precision (fp16, bf16, FP8, loss
  scaling); gradient accumulation and activation checkpointing; data parallelism and the all-reduce;
  ZeRO and FSDP; tensor, pipeline, sequence and expert parallelism; large-batch training;
  parameter-efficient fine-tuning (LoRA, QLoRA, adapters); hyperparameter search at scale;
  reproducibility; profiling; checkpointing and fault tolerance; sizing a run from a compute budget.
- **Assumes:** DL-1. **Links:** ML-1 (the hardware view).

### DL-8 · Efficient Deep Learning — `efficient-deep-learning` · ~12 · G1 · mapped
- **Covers:** where inference cost goes; quantisation in depth (PTQ, QAT, GPTQ, AWQ, SmoothQuant,
  FP8/MXFP4); pruning (unstructured, structured, lottery tickets); knowledge distillation; low-rank
  factorisation; efficient attention (FlashAttention's algorithm, KV-cache compression, linear
  attention); speculative decoding; MoE efficiency; on-device inference.
- **Assumes:** DL-1, DL-2. **Links:** ML-1, ML-8.

### DL-9 · LLM Engineering: From Data to Deployed Model — `llm-engineering` · ~16 · G1 (+documented GPU) · mapped
- **Covers:** the LLM pipeline stage by stage: pretraining data (extraction, quality filtering,
  deduplication, PII, mixtures); tokenizer training; the pretraining recipe and stability; mid-training
  and long-context extension; SFT data; preference optimisation in practice; RL for reasoning
  (verifiers, reward hacking); evaluation harnesses and contamination; distillation into small models;
  safety tuning; the serving handoff. Per stage — where DL-3 is per model family.
- **Assumes:** DL-1, DL-3. **Feeds:** NLP-7, AG-1.

### DL-10 · Graph Neural Networks — `graph-neural-networks` · ~12 · G1 · mapped
- **Covers:** graphs as data; spectral vs spatial convolution; GCN, GraphSAGE, GAT; the message-passing
  framework; expressivity and the WL test; over-smoothing and over-squashing; graph transformers; link
  prediction and knowledge-graph embeddings; heterogeneous and temporal graphs; GNNs at scale; molecules,
  recommendation and fraud as worked domains.
- **Assumes:** DL-1, ALG-5. **Links:** ML-7.

### DL-11 · Interpretability — `interpretability` · ~12 · G1 · mapped
- **Covers:** what explanation means for a network; attribution (saliency, integrated gradients, SHAP
  for networks) and its failure modes; probing; mechanistic interpretability (features, circuits,
  superposition); sparse autoencoders and dictionary learning; activation patching and causal tracing;
  steering vectors; evaluating explanations; interpretability for debugging.
- **Assumes:** DL-1, DL-2 (Transformer).

---

## 6 · Computer Vision (`computer-vision`) — 10 series

Machines that see: pixels, recognition, geometry, 3-D, video, documents, people and generation.
image-processing and diffusion-models move here (decision 4).

### CV-1 · Image Processing by Hand — `image-processing` · 14 parts · G0 · **2 live, 4 built**
- **Covers:** the hub (sample, filter, transform, decide); the Laplacian; resampling and aliasing;
  kernel design; the 2-D DFT; wavelets; next edge-preserving smoothing, Canny, the structure tensor
  (Harris, optical flow), scale space and SIFT, thresholding and segmentation, morphology, colour and
  gamma, gradient-domain editing.
- **Next:** publish Parts 3–6; then Part 8 (Canny). **Feeds:** CV-5, CV-8, NLP-9.

### CV-2 · Diffusion Models — `diffusion-models` · 12 parts · G1 · **1 live, 5 built**
- **Covers:** what a diffusion model does; the architecture; the loss derived; backbones (U-Net → DiT);
  training; samplers and solvers; next few-step and distillation, control, evaluation, beyond images,
  discrete diffusion LMs, (opt) memorisation.
- **Next:** Part 2 (series keys, cover — owner action), then publish 2 → 6 in order.
- **Assumes:** DL-5 for readers arriving from deep learning.

### CV-3 · Object Detection — `object-detection` · ~14 · G1 · mapped
- **Covers:** IoU, AP and the COCO protocol computed by hand; the R-CNN lineage (RoI pooling/align,
  RPN); anchors, assignment and NMS; feature pyramids; single-stage detectors and focal loss; the YOLO
  family traced (anchor-based → anchor-free, label assignment); DETR and its descendants (bipartite
  matching, deformable attention, RT-DETR); open-vocabulary detection and grounding; small and dense
  objects; the deployment trade.
- **Assumes:** DL-2. **Feeds:** CV-4, CV-8, CV-9, CV-10.

### CV-4 · Segmentation — `image-segmentation` · ~12 · G1 · mapped
- **Covers:** semantic segmentation (FCN, U-Net, DeepLab and atrous convolution); instance segmentation
  (Mask R-CNN); panoptic segmentation and PQ; mask classification (MaskFormer, Mask2Former); promptable
  segmentation (SAM, SAM 2) and its limits; video segmentation; medical segmentation (Dice and its
  losses); evaluation.
- **Assumes:** CV-3.

### CV-5 · Multiple View Geometry — `multiple-view-geometry` · ~14 · G0–G1 · mapped
- **Covers:** projective geometry and homogeneous coordinates; the pinhole camera and calibration;
  distortion; feature matching (SIFT from CV-1; SuperPoint, LightGlue); homographies; epipolar geometry
  and the fundamental and essential matrices (8-point, 5-point); triangulation; PnP; RANSAC; stereo
  rectification and disparity; structure from motion; bundle adjustment and the Schur complement.
- **Assumes:** CV-1. **Feeds:** CV-6, CV-7.

### CV-6 · 3D Vision and Neural Rendering — `3d-vision-neural-rendering` · ~12 · G1 (heavy fits documented) · mapped
- **Covers:** 3-D representations (point clouds, voxels, meshes, SDFs, implicit fields); point-cloud
  learning (PointNet++) and registration (ICP); monocular and multi-view depth; multi-view stereo; NeRF
  (volume rendering, encodings, Instant-NGP); 3D Gaussian Splatting; surface reconstruction; 3-D
  generation; 3-D detection from LiDAR.
- **Assumes:** CV-5. **Links:** CV-2.

### CV-7 · Visual SLAM and Robot Perception — `visual-slam` · ~10 · G1 · mapped
- **Covers:** visual odometry (feature-based vs direct); keyframes, local mapping and loop closure;
  pose-graph optimisation; ORB-SLAM and DSO dissected; visual-inertial odometry (IMU pre-integration,
  filtering vs optimisation); LiDAR SLAM; sensor fusion and calibration; ATE/RPE evaluation.
- **Assumes:** CV-5.

### CV-8 · Video Understanding — `video-understanding` · ~10 · G1 · mapped
- **Covers:** optical flow (Lucas–Kanade, Horn–Schunck, RAFT); single- and multi-object tracking
  (Kalman + Hungarian, SORT, ByteTrack, re-ID embeddings); action recognition (two-stream, 3-D
  convolutions, video transformers); temporal action localisation; video–language models; efficient
  video processing.
- **Assumes:** CV-3, CV-1.

### CV-9 · OCR and Document AI — `ocr-document-ai` · ~10 · G1 · mapped
- **Covers:** text detection (EAST, DBNet) and recognition (CRNN + CTC, attention decoders, TrOCR);
  layout analysis; table extraction; document understanding (the LayoutLM family, Donut and OCR-free
  models); handwriting; evaluation (CER/WER, layout metrics); a document-extraction pipeline end to end.
- **Assumes:** CV-3. **Links:** NLP-7.

### CV-10 · Human-Centric Vision — `human-centric-vision` · ~10 · G1 · mapped
- **Covers:** face detection and alignment; face recognition (ArcFace/CosFace embeddings) and its
  evaluation; 2-D and 3-D human pose; body and hand mesh recovery (SMPL); person re-identification;
  privacy and demographic bias measured, not asserted.
- **Assumes:** CV-3.

---

## 7 · Natural Language Processing (`nlp`) — 10 series

Computation over human language: text, structure, meaning, retrieval, generation, translation and
speech. frontier-models (DL-3) owns LLM internals; these series own everything from raw text to the
model boundary, and from the model to the application.

### NLP-1 · Text Processing and Tokenization — `text-processing-tokenization` · ~10 · G1 · mapped
- **Covers:** Unicode, normalisation forms and the bugs they cause; segmentation across scripts;
  tokenisation algorithms derived (BPE, WordPiece, Unigram LM, byte-level BPE, SentencePiece); training
  a tokenizer; vocabulary-size trade-offs; the cost of tokenisation across languages; pathologies
  (glitch tokens, number splitting); regex and finite-state transducers for normalisation.
- **Feeds:** every NLP series, DL-9.

### NLP-2 · Statistical NLP — `statistical-nlp` · ~12 · G1 · mapped
- **Covers:** n-gram language models and Kneser–Ney smoothing, perplexity; naive Bayes and logistic
  regression for text; HMMs and Viterbi; POS tagging; CRFs and BIO-tagged NER; EM; topic models (LDA by
  Gibbs sampling); edit distance and the noisy channel; the statistical lessons LLMs still obey.
- **Assumes:** NLP-1. **Feeds:** NLP-3, NLP-9.

### NLP-3 · Syntax, Semantics and Linguistic Structure — `syntax-semantics-parsing` · ~12 · G1 · mapped
- **Covers:** morphology; constituency grammars, CKY and PCFGs; dependency parsing (transition- and
  graph-based); Universal Dependencies; semantic role labelling; coreference; word sense; discourse
  structure; semantic parsing and meaning representations (AMR, text-to-SQL); what probing shows LLMs
  have learned of syntax.
- **Assumes:** NLP-2.

### NLP-4 · Embeddings and Semantic Representation — `embeddings-semantic-representation` · ~10 · G1 · mapped
- **Covers:** distributional semantics; word2vec (skip-gram, negative sampling) and GloVe derived;
  subword embeddings; contextual embeddings; sentence embeddings (SBERT, contrastive training, hard
  negatives); anisotropy and whitening; evaluation (MTEB) and its pitfalls; multilingual embeddings;
  compression (Matryoshka, quantisation).
- **Assumes:** NLP-1, DL-1. **Feeds:** NLP-5, NLP-6.

### NLP-5 · Information Retrieval and Search — `information-retrieval-search` · ~14 · G1 · mapped
- **Covers:** the inverted index; the probabilistic model and BM25 derived; query processing; evaluation
  (test collections, MAP, nDCG, MRR, significance); learning to rank; neural retrieval (DPR, ColBERT late
  interaction, SPLADE); hybrid retrieval and fusion; cross-encoder re-ranking; query understanding;
  search-quality operations.
- **Assumes:** NLP-4. **Links:** ALG-1 (WAND, HNSW), DB-2 (Lucene, vector DBs), ML-7.

### NLP-6 · Retrieval-Augmented Generation — `retrieval-augmented-generation` · ~12 · G1 · mapped
- **Covers:** RAG vs fine-tuning; document processing and chunking; indexing strategies; retrieval and
  re-ranking tuning; query rewriting and decomposition; context construction and lost-in-the-middle;
  GraphRAG and structured retrieval; multi-hop retrieval; evaluating retrieval, generation and
  faithfulness separately; failure modes; production RAG.
- **Assumes:** NLP-5. **Feeds:** AG-3.

### NLP-7 · LLM Applications in Practice — `llm-applications` · ~14 · G1 (API optional) · mapped
- **Covers:** a model as a component; prompting and its measured limits; structured output and
  constrained decoding; decoding strategies; task fine-tuning (PEFT from DL-7); classification,
  extraction and summarisation with LLMs; generation metrics (BLEU, ROUGE, BERTScore) and LLM-as-judge
  with its biases; hallucination and groundedness; latency, cost and caching; guardrails by
  construction; LLM application architecture and LLMOps.
- **Assumes:** DL-3 or DL-9. **Feeds:** AG-1, NLP-10.

### NLP-8 · Machine Translation and Multilingual NLP — `machine-translation-multilingual` · ~10 · G1 · mapped
- **Covers:** rules → SMT (IBM models, phrase-based) → NMT; Transformer MT; evaluation (BLEU, chrF,
  COMET, MQM); low-resource MT (back-translation, transfer); multilingual models and cross-lingual
  transfer; the tokenisation tax; LLMs as translators.
- **Assumes:** NLP-1, DL-2.

### NLP-9 · Speech and Audio Processing — `speech-audio-processing` · ~12 · G1 · mapped
- **Covers:** sampling, the STFT and mel scale (the DFT from CV-1); audio features; classical ASR
  (HMM-GMM, WFSTs); CTC and attention-based ASR; Whisper-class models; TTS (Tacotron → VITS →
  neural-codec LMs); speaker recognition and diarisation; speech LLMs; evaluation (WER, MOS);
  streaming speech.
- **Assumes:** DL-1, NLP-2.

### NLP-10 · Evaluating Language Systems — `evaluating-language-systems` · ~8 · G1 · mapped
- **Covers:** metric validity; benchmark and construct design; contamination detection; human
  evaluation and agreement; calibrating LLM-as-judge; variance across seeds and prompts and significance;
  building an evaluation suite for a product.
- **Assumes:** NLP-7. **Links:** AG-6.

---

## 8 · Agentic AI (`agentic-ai`) — 8 series

AI systems that plan and act: how they are built, given memory, coordinated, connected, evaluated,
grounded in classical planning, and secured. AG-2 is part of the security work and stays unchanged.

### AG-1 · Building Agentic Systems — `building-agentic-systems` · ~12 · G1 · mapped · **entry series**
- **Covers:** the agent loop vs a single call, and when a fixed workflow is the better design; tool use
  and function calling from a bare model; designing tools a model can use; ReAct; planning,
  reflection and self-correction; the spectrum from workflow to autonomous agent; guardrails by
  construction; a real agent end to end. Built on Claude conventions (the `claude-api` skill), portable.
- **Assumes:** NLP-7 or DL-3. **Feeds:** every AG series.

### AG-2 · Agentic AI Security *(planned; cross-filed agentic-ai + security)*
- `agentic-ai` (secondary `security`) · hybrid (threat-model ladder + a spoke per architecture layer) · ~16 parts · L3–L4 · advanced
- **Lab:** **G2/G3 — isolated local agent + local tools in Docker**; any injection/misuse demo runs
  **only against a local agent and local throwaway tools** (frontier-models' rule). Container-capability request.
- **Covers (from the Radware guide's scaffold + primary sources):** why autonomy expands blast radius;
  the agentic threat model; prompt injection and **indirect/cross-domain prompt injection** (the named
  real cases EchoLeak and ShadowLeak, as worked examples of why perimeter controls miss them); tool
  misuse and **excessive agency**; **memory/context poisoning**; **rogue and supply-chain agents**
  (malicious plugins / MCP servers); convergence with classic threats (API abuse, ATO, automation
  surges); the **six-layer reference architecture** and the control at each layer — input/output
  guarding, intent/plan validation, budget/timeboxing, **semantic authorization for sensitive actions**,
  least-privilege scoped credentials, decision forensics; the **risk graph**; detection by behavioural
  drift; **incident response for agents** (pause/revoke, quarantine memory, roll back); **red-teaming
  agents**; GRC (NIST AI RMF + GenAI profile, EU AI Act, OWASP for LLM/agentic apps).
- **Sources:** OWASP Top 10 for LLM Apps + agentic work; NIST AI RMF + GenAI profile; MITRE ATLAS;
  EchoLeak/ShadowLeak write-ups; the Radware CISO guide (secondary).

### AG-3 · Agent Memory and Context Engineering — `agent-memory-context` · ~10 · G1 · mapped
- **Covers:** the context window as working memory; constructing and budgeting context; compaction and
  summarisation; episodic vs semantic memory; vector memory and staleness; memory write policies;
  long-horizon tasks; retrieval inside the loop; measuring memory's effect on task success.
- **Assumes:** AG-1, NLP-6.

### AG-4 · Multi-Agent Systems — `multi-agent-systems` · ~10 · G1 · mapped
- **Covers:** when several agents beat one and when they compound errors; topologies (supervisor/worker,
  pipeline, debate, market); role design and handoffs; communication and shared state; agent-to-agent
  protocols (A2A); coordination failures and how to measure them; cost; evaluation; classical
  multi-agent ideas that still apply (contract net, negotiation).
- **Assumes:** AG-1.

### AG-5 · Agent Protocols and Infrastructure — `agent-protocols-infrastructure` · ~10 · G1–G2 · mapped
- **Covers:** the Model Context Protocol in depth (primitives, transports, capability negotiation,
  authorisation); building and testing MCP servers; A2A; tool registries; agent runtimes; sandboxed code
  execution; durable execution for long-running agents; state persistence; tracing and observability
  (OpenTelemetry for agents).
- **Assumes:** AG-1. **Links:** AG-2 (securing these components).

### AG-6 · Agent Evaluation and Reliability — `agent-evaluation-reliability` · ~10 · G1 · mapped
- **Covers:** task success vs trajectory evaluation; building offline evaluation sets; what agent
  benchmarks measure (SWE-bench and others); regression suites; determinism, record/replay and mocking;
  failure taxonomies; reliability engineering for agents (budgets, retries, fallbacks); cost and
  latency accounting; human review loops.
- **Assumes:** AG-1. **Links:** NLP-10.

### AG-7 · Coding and Computer-Use Agents — `coding-computer-use-agents` · ~10 · G1–G2 · mapped
- **Covers:** how coding agents work (repository understanding, edit–test loops, patch application,
  test-driven repair); evaluating them on real repositories; computer-use and browser agents (screen
  grounding, DOM vs pixels, action spaces); recovery from errors; sandboxing; where they fail.
- **Assumes:** AG-1, AG-5.

### AG-8 · Reasoning and Planning Foundations — `reasoning-planning-foundations` · ~10 · G1 · mapped
- **Covers:** classical planning (STRIPS/PDDL, heuristic search, HTN); constraint satisfaction; Monte
  Carlo tree search; knowledge representation and knowledge graphs; logic and neuro-symbolic methods;
  LLM reasoning (chain of thought, self-consistency, search over thoughts, verifiers, process vs outcome
  rewards); what reasoning models change for agents.
- **Assumes:** ALG-1 (A\*), DL-3. **Feeds:** AG-1, AG-4.

---

## 9 · Networking (`networking`) — 13 series

How data moves between machines, in every place a network engineer works: the host stack, the LAN,
routing inside and between networks, the internet core, DNS and the web protocols, the Linux kernel,
the data centre, virtual and cloud networks, wireless, performance and automation. Labs build each
topology as isolated network namespaces on one host and read real captures (decision 7).

### NET-1 · TCP/IP Internals — `tcp-ip-internals` · ~16 · G2 · mapped · **entry series**
- **Covers:** one request through the stack and how to read a capture; IP (header, fragmentation, TTL,
  ICMP); addressing and subnetting by hand; UDP; the TCP state machine (handshake, teardown,
  TIME_WAIT); reliability (sequence and acknowledgement numbers, SACK, RTO estimation); flow control and
  window scaling; congestion control (slow start, Reno, CUBIC, BBR) on paths with controlled delay and
  loss; Nagle and delayed ACK; MTU and path-MTU discovery; IPv6 and what actually changed.
- **Feeds:** every networking series.

### NET-2 · Ethernet, Switching and the LAN — `ethernet-switching-lan` · ~12 · G2 · mapped
- **Covers:** Ethernet framing and the MAC sublayer; how a switch learns and forwards (MAC tables,
  flooding); VLANs and 802.1Q trunks; spanning tree (STP, RSTP, MSTP) and loop prevention; link
  aggregation (LACP); ARP and IPv6 neighbour discovery; broadcast domains and L2 design; inter-VLAN
  routing; first-hop redundancy (VRRP); L2 design that stays stable under change.
- **Assumes:** NET-1.

### NET-3 · Routing Protocols: OSPF, IS-IS, BGP and MPLS — `routing-protocols` · ~16 · G2 · mapped
- **Covers:** the routing table and longest-prefix match; static and default routes; distance vector
  (RIP) and count-to-infinity; link state (OSPF areas, LSAs and SPF; IS-IS); BGP in depth (sessions,
  path attributes, the best-path algorithm, iBGP and route reflectors, communities, policy); MPLS
  (labels, LDP, L3VPN, traffic engineering); redistribution; convergence and fast reroute; origin
  validation with RPKI.
- **Assumes:** NET-1. **Feeds:** NET-4, NET-8, NET-13.

### NET-4 · Internet Architecture: ASes, Peering, IXPs, CDNs and Anycast — `internet-architecture` · ~10 · G2 · mapped
- **Covers:** the AS-level internet; transit vs peering and its economics; IXPs and route servers; the
  valley-free model; anycast; how CDNs route and cache; measuring the internet (traceroute, looking
  glasses, RIPE Atlas); outages and route leaks as case studies of BGP policy; IPv4 exhaustion and CGNAT.
- **Assumes:** NET-3.

### NET-5 · DNS in Depth — `dns-in-depth` · ~10 · G2 · mapped
- **Covers:** the namespace and delegation; recursive and authoritative resolution traced; record types
  including SVCB and HTTPS; caching, TTLs and negative caching; zone transfers; DNSSEC (keys,
  signatures, the chain of trust, validation); DNS over TLS and HTTPS; anycast DNS; operating resolvers
  and authoritative servers; DNS for service discovery.
- **Assumes:** NET-1.

### NET-6 · Web Protocols: HTTP, TLS and QUIC — `web-protocols-http-tls-quic` · ~14 · G2 · mapped
- **Covers:** HTTP/1.1 semantics, keep-alive and head-of-line blocking; HTTP caching semantics; HTTP/2
  framing, streams and HPACK; QUIC (connection IDs, streams, loss recovery, congestion control in user
  space, connection migration); HTTP/3 and QPACK; TLS 1.3 on the wire (the cryptography is SEC-1);
  WebSockets; gRPC over HTTP/2; L7 proxies.
- **Assumes:** NET-1. **Links:** SEC-1.

### NET-7 · Linux Networking Internals — `linux-networking-internals` · ~14 · G2 · mapped
- **Covers:** a packet's path through the kernel (NIC rings, NAPI, softirq, `sk_buff`); sockets and
  their buffers; epoll and io_uring; netfilter hooks, nftables and connection tracking; routing and
  policy routing in the kernel; `tc` and queuing disciplines; network namespaces, veth and bridges (the
  substrate of every lab here); eBPF and XDP; offloads (GRO, GSO, TSO, RSS, RPS); tuning by measurement.
- **Assumes:** NET-1. **Feeds:** NET-9, NET-10, NET-12. **Links:** SEC-2.

### NET-8 · Data Center Networking — `data-center-networking` · ~12 · G2 (+documented fabrics) · mapped
- **Covers:** Clos and leaf–spine topologies; ECMP and flow hashing; BGP as the data-centre routing
  protocol; VXLAN with EVPN; data-centre congestion control (ECN, DCTCP); RDMA and RoCE (PFC and its
  pitfalls); load balancing at scale (Maglev, consistent hashing); SmartNICs and DPUs; AI-cluster
  fabrics (InfiniBand, NVLink and NVSwitch); handling failures in the fabric.
- **Assumes:** NET-3. **Links:** ML-1, SD-2.

### NET-9 · Network Virtualization and SDN — `network-virtualization-sdn` · ~12 · G2 · mapped
- **Covers:** overlays and encapsulation (GRE, VXLAN, Geneve); tunnelling protocols (IPsec and WireGuard
  as protocols); the SDN split of control and data plane, OpenFlow and controllers; programmable data
  planes (P4); network function virtualisation; virtual switches (Open vSwitch); service-mesh data
  planes (Envoy).
- **Assumes:** NET-7.

### NET-10 · Cloud and Kubernetes Networking — `cloud-kubernetes-networking` · ~12 · G2–G3 (cluster) · mapped
- **Covers:** VPC design (subnets, route tables, NAT and internet gateways); cloud load balancers;
  private connectivity and peering; the Kubernetes network model; CNI plugins (bridge, Calico,
  Cilium/eBPF); Services and kube-proxy (iptables, IPVS, eBPF); Ingress and the Gateway API;
  NetworkPolicy; service mesh; multi-cluster networking; debugging pod-to-pod paths.
- **Assumes:** NET-7, NET-9.

### NET-11 · Wireless and Mobile Networking — `wireless-mobile-networking` · ~10 · G0–G1 · mapped
- **Covers:** radio basics for engineers (SNR, modulation and MCS, channel width); the 802.11 MAC
  (CSMA/CA, ACKs, aggregation); Wi-Fi 6/6E/7 (OFDMA, MU-MIMO, multi-link operation); Wi-Fi design and
  roaming; cellular architecture (the LTE EPC, the 5G core and RAN); mobility; Bluetooth LE basics;
  measuring wireless performance.
- **Assumes:** NET-1.

### NET-12 · Network Performance, Measurement and Troubleshooting — `network-performance-troubleshooting` · ~10 · G2 · mapped
- **Covers:** bandwidth, latency and the bandwidth-delay product; queueing and bufferbloat (CoDel,
  FQ-CoDel); diagnosing loss; measurement tools (ping, traceroute/mtr, iperf, ss, tcpdump) and their
  traps; flow telemetry (NetFlow, IPFIX, sFlow); a layered troubleshooting method on planted faults;
  tuning that is measured, not folklore.
- **Assumes:** NET-1, NET-7.

### NET-13 · Network Automation and Programmability — `network-automation` · ~10 · G2 · mapped
- **Covers:** why automate and what goes wrong without it; configuration management for network devices
  (Ansible); model-driven management (YANG, NETCONF, RESTCONF, gNMI); streaming telemetry; a source of
  truth (NetBox); intent-based approaches; CI/CD and pre-deployment verification for network changes
  (Batfish); network as code in a lab.
- **Assumes:** NET-3.

---

## 10 · Cyber Security (new category, three series)

**Framing (firm).** Educational and defence-oriented: how a class of weakness works **and how it is
detected and fixed**, lab-only against intentionally-vulnerable throwaway targets in isolated
networks — mechanism and mitigation, never a working exploit or operational how-to. Detailed per-part
attack-class scoping is deferred to each series' Checkpoint S (the point to switch to 4.8 if 5.5 flags).

### SEC-1 · Applied Cryptography *(planned — full Checkpoint S)*
- `security` · hybrid · ~16 committed + 2 optional · L3–L4 · intermediate→advanced · **Lab: G1, no access.**
- The benign, foundational half of the category — your encryption/decryption/hashing ask. Full plan
  is being written to `posts/applied-cryptography/plan.md`. **Covers:** security goals and threat
  model; randomness/CSPRNGs; AES internals; modes of operation; authenticated encryption (GCM,
  ChaCha20-Poly1305); cryptographic hashing (SHA-2, SHA-3); MACs; KDFs and password hashing; RSA;
  Diffie–Hellman and forward secrecy; elliptic-curve cryptography; digital signatures; certificates
  and PKI; the TLS 1.3 handshake; post-quantum cryptography; encryption in practice (envelope, KMS,
  rotation). Optional: side channels; the double ratchet.

### SEC-2 · Defensive Security / Blue Team *(planned)*
- `security` · hybrid (controls ladder + detection/response spokes) · ~18 parts · L2–L4 · intermediate→advanced
- **Lab:** **G2/G3 — isolated Docker networks** (container-capability access request).
- **Covers:** threat modelling; the firewall (stateless vs stateful, nftables, connection tracking —
  the Docker-network lab); network segmentation and zero-trust; intrusion detection/prevention
  (signatures and anomaly, mapped to MITRE ATT&CK); host hardening (least privilege, sandboxing,
  mandatory access control); identity and authentication (MFA, OAuth/OIDC, SAML, Kerberos);
  authorization (RBAC/ABAC); secrets management; logging, SIEM and detection engineering; the
  incident-response lifecycle and basic forensics; vulnerability and patch management; container and
  cloud posture; GRC mapping (NIST CSF and frameworks).
- **Sources:** NIST CSF and 800-series; MITRE ATT&CK; CIS Benchmarks; netfilter/Suricata/Zeek docs; Sigma.

### SEC-3 · Secure Engineering: Vulnerability Classes & Defenses *(planned)*
- `security` · hybrid (the web/app surface, each part a class + its defence) · ~16 parts · L2–L4 · intermediate→advanced
- **Lab:** **G2/G3 — isolated Docker**, against a tiny intentionally-flawed app the author writes then
  **fixes in the post** (container-capability access request).
- **Covers (altitude only — class list set at its Checkpoint S):** the common web/app weakness classes
  catalogued by **OWASP** (Top 10 / ASVS) and **CWE**, each as *how it arises in code, how it is
  detected, and the concrete fix*; secure defaults and defensive patterns; the secure-development
  lifecycle (NIST SSDF); threat frameworks (ATT&CK, the kill chain) for reasoning about defence;
  responsible disclosure. Every part ends at the fix.
- **Sources:** OWASP (Top 10, ASVS, Cheat Sheets); CWE; NIST SSDF (SP 800-218).
- *(Splits into Web and Network/Host security if one series proves too large — decided at Checkpoint S.)*

**Note on section 10.** It is left exactly as written, on the owner's instruction; growing it into more
series is deferred to a session on Opus 4.8. The four security `plan.md` files predate this map and use
earlier codes: their "NET-1/NET-2" now correspond to NET-1, NET-3, NET-6 and NET-7 here; "SD-1 (API
design)" to SD-4; "NLP-2" to NLP-7; and AG-2's references to AG-1's parts to AG-1, AG-4 and AG-5. Each is
re-mapped when that security series is built.

---

## 11 · System Design (`system-design`) — 10 series

Designing large-scale software systems: the reasoning, the components, the guarantees, the
architectural styles, reliability, observability, and worked designs. Engine internals stay in
`databases` and `data-engineering`; these series compose them.

### SD-1 · System Design Foundations: Estimation and Trade-offs — `system-design-foundations` · ~10 · G1 · mapped · **entry series**
- **Covers:** functional and non-functional requirements; back-of-envelope estimation that holds up;
  the latency numbers; Little's law and queueing; the trade-off vocabulary (consistency, availability,
  latency, durability, cost); the design method (requirements → API → data model → high level → deep
  dive → bottlenecks); cost-aware design.
- **Feeds:** every SD series.

### SD-2 · Scalability Building Blocks — `scalability-building-blocks` · ~14 · G1–G2 · mapped
- **Covers:** load balancing (L4/L7, power of two choices); caching in depth (patterns, eviction,
  invalidation, stampedes, hit-rate arithmetic); CDNs; queues and logs as components; choosing a data
  store; replication for read scale; partitioning and sharding (hot keys, rebalancing); consistent
  hashing (virtual nodes, bounded load, rendezvous, jump); rate limiting and backpressure; search and
  blob storage as components.
- **Assumes:** SD-1. **Links:** NET-8, DB-2.

### SD-3 · Distributed Systems for System Designers — `distributed-systems-for-designers` · ~14 · G1 · mapped
- **Covers:** failure models; consistency models (linearisable → eventual, client-centric guarantees);
  CAP and PACELC stated precisely; replication topologies; quorums; consensus as a tool (leader
  election, replicated logs — internals in DB-2); distributed locks and fencing tokens; time and order
  (Lamport, vector and hybrid logical clocks); idempotency and exactly-once effects; distributed
  transactions (2PC, sagas, the outbox); CRDTs and collaborative state.
- **Assumes:** SD-1, DB-6. **Feeds:** SD-5, SD-6, SD-10.

### SD-4 · API and Interface Design — `api-interface-design` · ~10 · G1 · mapped
- **Covers:** REST resource modelling, gRPC and protobuf, GraphQL, and when each fits; pagination,
  filtering and long-running operations; idempotency keys; versioning and compatibility rules;
  asynchronous APIs (webhooks, events); API gateways; error models; rate limits as part of the contract;
  contract testing; SDK design.
- **Assumes:** SD-1.

### SD-5 · Event-Driven Architecture — `event-driven-architecture` · ~10 · G1–G2 · mapped
- **Covers:** events vs commands vs messages; pub/sub and log-based integration; event sourcing; CQRS;
  the outbox and CDC; event schemas and their evolution; choreography vs orchestration; workflow engines
  and durable execution; exactly-once effects end to end; debugging an event-driven system.
- **Assumes:** SD-3. **Links:** DE-3.

### SD-6 · Microservices and Service Architecture — `microservices-architecture` · ~12 · G1–G2 · mapped
- **Covers:** monolith, modular monolith and microservices, with the honest trade-offs; service
  boundaries from domain-driven design (bounded contexts); synchronous vs asynchronous communication;
  data ownership and database per service; transactions across services; service discovery and the
  service mesh; deployment strategies (blue-green, canary); testing a service architecture; migrating a
  monolith (strangler fig).
- **Assumes:** SD-3, SD-4.

### SD-7 · Reliability Engineering (SRE) — `reliability-engineering-sre` · ~12 · G1–G2 · mapped
- **Covers:** SLIs, SLOs, SLAs and error budgets; availability arithmetic (series and parallel, nines to
  minutes); failure modes and blast radius; timeouts, retries with backoff and jitter, circuit
  breakers, bulkheads, load shedding; graceful degradation; overload and metastable failures; capacity
  planning and autoscaling; chaos engineering; incident management and blameless postmortems; disaster
  recovery (RPO, RTO, multi-region).
- **Assumes:** SD-2. **Feeds:** SD-8.

### SD-8 · Observability Engineering — `observability-engineering` · ~8 · G1–G2 · mapped
- **Covers:** metrics, logs, traces and profiles and what each answers; OpenTelemetry; cardinality and
  cost; the RED and USE methods; SLO-based alerting with burn rates; distributed tracing and context
  propagation; continuous profiling; debugging production through observability.
- **Assumes:** SD-7.

### SD-9 · Designing Data-Intensive Systems — `designing-data-intensive-systems` · ~10 · G1 · mapped
- **Covers:** designing a key-value store, an object store, a time-series store, a search service and a
  distributed cache as *systems* (engine internals linked to DB-2 and DE); read, write and space
  amplification as design inputs; tiered storage; secondary indexes across partitions; batch vs stream
  for derived data; composing data systems (the unbundled database).
- **Assumes:** SD-2, SD-3. **Links:** DB-2, DB-7, DE-3.

### SD-10 · System Design Case Studies — `system-design-case-studies` · ~20 · G1 · mapped
- **Covers:** each a full design against stated numbers, naming the parts it composes: a rate limiter;
  a URL shortener; a news feed; chat; notifications; typeahead; a web crawler; a distributed cache; a
  payment ledger; ride-sharing with geo-indexing; video streaming; file sync; collaborative editing
  (OT and CRDTs); ticketing under flash-sale load; ad-click aggregation; a distributed job scheduler; a
  metrics system; a search engine; an LLM serving platform; a feature store.
- **Assumes:** SD-2, SD-3.

---

## 12 · Algorithms (`algorithms`) — 12 series

Algorithms and data structures across every major family, in the house style search-algorithms set:
what is prepaid, what it costs, when it pays back, and which input breaks it — measured. search-algorithms
stays search-only; the other families are their own series.

### ALG-1 · Search Algorithms: The Price of the Skip — `search-algorithms` · 18 parts · G1 · **hub live**
- **Covers:** one loop with a different prepaid structure: when a search structure pays for itself;
  binary search off by one; Eytzinger layouts; interpolation search and learned indexes; KMP,
  Boyer–Moore and Two-Way; regex backtracking; suffix arrays and the FM-index; BFS, DFS, Dijkstra and
  A\*; universal optimality; A\* pitfalls; contraction hierarchies and landmarks; k-d trees; HNSW tuning;
  HNSW vs IVF-PQ vs DiskANN; later wave: alpha-beta, MaxScore and WAND, beam search and IDA\*.
- **Next:** Part 3 (decision 5). **Feeds:** NLP-5, AG-8, ALG-7.

### ALG-2 · Algorithm Design and Analysis — `algorithm-design-analysis` · ~12 · G0–G1 · mapped · **entry series**
- **Covers:** asymptotic analysis done right (tight vs upper bounds, which case); recurrences (master
  theorem, Akra–Bazzi, recursion trees); amortised analysis (aggregate, accounting, potential); divide
  and conquer; greedy algorithms and exchange arguments, with matroids; backtracking and
  branch-and-bound; lower bounds (decision trees, adversaries); reductions and NP-completeness for
  engineers.
- **Feeds:** every ALG series.

### ALG-3 · Sorting and Selection — `sorting-and-selection` · ~10 · G1 · mapped
- **Covers:** the comparison lower bound; merge sort and its variants; quicksort (partition schemes,
  pivots, introsort, pdqsort); heapsort; Timsort and the sorts real libraries ship; counting and radix
  sort; external sorting; selection (quickselect, median of medians); stability; parallel and SIMD
  sorting — each measured.
- **Assumes:** ALG-2.

### ALG-4 · Data Structures in Depth — `data-structures-in-depth` · ~16 · G1 · mapped
- **Covers:** dynamic arrays and amortisation; hash tables in depth (chaining vs open addressing; linear
  and quadratic probing; Robin Hood, Swiss tables, cuckoo; hash functions and load factors — the ground
  search-algorithms leaves out); heaps (binary, d-ary, pairing, Fibonacci); balanced trees (AVL,
  red–black, treaps, skip lists); in-memory B-trees; tries (radix, ART); union–find; segment and
  Fenwick trees; persistent structures; cache-oblivious layouts; Bloom and cuckoo filters.
- **Assumes:** ALG-2. **Feeds:** ALG-1, ALG-8, DB-7.

### ALG-5 · Graph Algorithms — `graph-algorithms` · ~16 · G1 · mapped
- **Covers:** representations and their costs; DFS applications (topological order, strongly connected
  components with Tarjan and Kosaraju, bridges and articulation points); minimum spanning trees
  (Kruskal, Prim, Borůvka); shortest paths beyond Dijkstra (Bellman–Ford and negative cycles,
  Floyd–Warshall, Johnson); network flow (Ford–Fulkerson, Edmonds–Karp, Dinic, push–relabel) and
  min-cut; matching (Hopcroft–Karp, Hungarian, blossom); colouring; graph processing at scale.
- **Assumes:** ALG-2. **Links:** ALG-1, DL-10.

### ALG-6 · Dynamic Programming — `dynamic-programming` · ~12 · G1 · mapped
- **Covers:** optimal substructure and overlapping subproblems; top-down vs bottom-up and memory;
  knapsack, LCS, edit distance, LIS, matrix chain, coin change; DP on trees, DAGs and intervals;
  bitmask and digit DP; DP optimisations (Knuth, divide and conquer, convex-hull trick, SOS); DP in
  practice (sequence alignment, Viterbi, shortest paths as DP).
- **Assumes:** ALG-2. **Links:** NLP-2.

### ALG-7 · Advanced String Algorithms — `advanced-string-algorithms` · ~10 · G1 · mapped
- **Covers (beyond ALG-1's substring search and suffix arrays):** rolling hashes; the Z-algorithm and
  prefix function as tools; Aho–Corasick multi-pattern matching; suffix trees (Ukkonen) and suffix
  automata; LCP arrays and their uses; palindromes (Manacher); compression (LZ77, LZ78, the BWT link);
  approximate matching (bitap, edit-distance automata).
- **Assumes:** ALG-1 Parts 6–8.

### ALG-8 · Randomized and Streaming Algorithms — `randomized-streaming-algorithms` · ~10 · G1 · mapped
- **Covers:** Las Vegas vs Monte Carlo; the analysis tools (Chernoff, union bound); universal and
  k-independent hashing; Bloom filters and variants; sketches (Count-Min, Count Sketch, HyperLogLog,
  t-digest); MinHash and LSH; reservoir sampling; streaming lower bounds; randomised algorithms inside
  production systems.
- **Assumes:** ALG-2, ALG-4. **Feeds:** DE-7.

### ALG-9 · Computational Geometry — `computational-geometry` · ~10 · G1 · mapped
- **Covers:** robust predicates (orientation, exact arithmetic); convex hulls (Graham, Andrew, Chan);
  line sweep (segment intersection, Bentley–Ottmann); closest pair; polygon triangulation; Voronoi
  diagrams and Delaunay triangulation; range searching and k-d trees; spatial indexes (R-trees,
  quadtrees, geohash, S2, H3).
- **Assumes:** ALG-2. **Links:** SD-10 (geo case study).

### ALG-10 · Optimization Algorithms: LP, IP and Approximation — `optimization-algorithms` · ~12 · G1 · mapped
- **Covers:** linear programming and the simplex method; duality; interior-point methods; integer
  programming (branch and bound, cutting planes); approximation algorithms (vertex cover, set cover,
  TSP, LP rounding); local search and metaheuristics (simulated annealing, genetic algorithms); SAT, SMT
  and constraint programming basics — the ground search-algorithms leaves out.
- **Assumes:** ALG-2.

### ALG-11 · Parallel and Concurrent Algorithms — `parallel-concurrent-algorithms` · ~12 · G1 · mapped
- **Covers:** work and span; parallel prefix (scan); parallel sorting and merging; fork–join and work
  stealing; memory models and ordering (acquire/release); lock-based vs lock-free structures (CAS, ABA,
  hazard pointers, epoch reclamation); concurrent hash maps and queues; GPU algorithm patterns;
  measuring scalability.
- **Assumes:** ALG-2, ALG-4. **Links:** ML-1.

### ALG-12 · Performance Engineering of Algorithms — `algorithm-performance-engineering` · ~10 · G1 · mapped
- **Covers:** why asymptotics mislead on real hardware; the memory hierarchy and cache misses; branch
  prediction and branchless code; SIMD vectorisation; data layout (array of structs vs struct of
  arrays); benchmarking methodology (noise, warm-up, statistics); profiling (perf, flame graphs); case
  studies of algorithm rewrites measured end to end.
- **Assumes:** ALG-2. **Links:** ALG-1 Part 4.
