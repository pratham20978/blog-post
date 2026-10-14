# Source ledger — when-a-search-structure-pays-for-itself

Part 2 of *Search Algorithms: The Price of the Skip*. Researched 2026-10-14, inline (no agents).
Every count the article computes comes from `lab/pays_for_itself.py` and its `captures.json`; this
ledger carries the claims that come from sources. Primary copies were read from the session
scratchpad: PDFs as `pdftotext` text, docs and source at the tags named below.

## Sources

| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |
|---|---|---|---|---|---|---|---|---|
| S1 | T1 | Stober & Weiß, "Lower Bounds for Sorting 16, 17, and 18 Elements" | ALENEX 2023 (SIAM), pp. 201–213 | 2023 | 10.1137/1.9781611977561.ch17 (arXiv:2206.05597v2) | peer-reviewed | https://arxiv.org/abs/2206.05597 | 2026-10-14 |
| S2 | T1 | Flajolet & Golin, "Mellin Transforms and Asymptotics: The Mergesort Recurrence" | Acta Informatica 31(7):673–696 | 1994 | 10.1007/BF01177551 | peer-reviewed | https://algo.inria.fr/flajolet/Publications/FlGo94.pdf | 2026-10-14 |
| S3 | T1 | Crosby & Wallach, "Denial of Service via Algorithmic Complexity Attacks" | 12th USENIX Security Symposium, pp. 29–44 | 2003 | dblp:conf/uss/CrosbyW03 | peer-reviewed | https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf | 2026-10-14 |
| S4 | T1 | Tarjan, "Amortized Computational Complexity" | SIAM J. Algebraic and Discrete Methods 6(2):306–318 | 1985 | 10.1137/0606031 | peer-reviewed | https://doi.org/10.1137/0606031 | 2026-10-14 |
| S5 | T1 | Guibas & Sedgewick, "A Dichromatic Framework for Balanced Trees" | 19th IEEE FOCS, pp. 8–21 | 1978 | 10.1109/SFCS.1978.3 | peer-reviewed | https://sedgewick.io/wp-content/themes/sedgewick/papers/1978Dichromatic.pdf | 2026-10-14 |
| S6 | T1 | Athanassoulis, Kester, Maas, Stoica, Idreos, Ailamaki & Callaghan, "Designing Access Methods: The RUM Conjecture" | EDBT 2016, pp. 461–466 | 2016 | 10.5441/002/edbt.2016.42 | peer-reviewed | https://openproceedings.org/2016/conf/edbt/paper-12.pdf | 2026-10-14 |
| S7 | T2 | PEP 456, "Secure and Interchangeable Hash Algorithm" (Heimes; Final; Python 3.4) | Python Enhancement Proposals | 2013 | PEP 456 | official-docs | https://peps.python.org/pep-0456/ | 2026-10-14 |
| S8 | T2 | Python 3 docs, "Command line and environment" (`-R`, `PYTHONHASHSEED`) | docs.python.org | 2026 | — | official-docs | https://docs.python.org/3/using/cmdline.html | 2026-10-14 |
| S9 | T2 | Python 3 docs, "Data model", `object.__hash__` | docs.python.org | 2026 | — | official-docs | https://docs.python.org/3/reference/datamodel.html | 2026-10-14 |
| S10 | T2 | Python docs, "What's New In Python 3.11" (siphash13, bpo-29410) | docs.python.org | 2022 | — | official-docs | https://docs.python.org/3/whatsnew/3.11.html | 2026-10-14 |
| S11 | T2 | Python 3 docs, `bisect` — Array bisection algorithm | docs.python.org | 2026 | — | official-docs | https://docs.python.org/3/library/bisect.html | 2026-10-14 |
| S12 | T3 | CPython `Objects/dictobject.c` at tag v3.14.0 | GitHub python/cpython | 2025 | v3.14.0 | source | https://github.com/python/cpython/blob/v3.14.0/Objects/dictobject.c | 2026-10-14 |
| S13 | T3 | OpenJDK `java/util/TreeMap.java` at tag jdk-25-ga | GitHub openjdk/jdk | 2025 | jdk-25-ga | source | https://github.com/openjdk/jdk/blob/jdk-25-ga/src/java.base/share/classes/java/util/TreeMap.java | 2026-10-14 |
| S14 | T3 | OpenJDK `java/util/HashMap.java` at tag jdk-25-ga | GitHub openjdk/jdk | 2025 | jdk-25-ga | source | https://github.com/openjdk/jdk/blob/jdk-25-ga/src/java.base/share/classes/java/util/HashMap.java | 2026-10-14 |
| S15 | T2 | JEP 180, "Handle Frequent HashMap Collisions with Balanced Trees" (Closed / Delivered, JDK 8) | OpenJDK JEP index | 2013 | JEP 180 | official-docs | https://openjdk.org/jeps/180 | 2026-10-14 |
| S16 | T2 | Java SE 25 API, `java.util.TreeMap` | docs.oracle.com | 2025 | — | official-docs | https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeMap.html | 2026-10-14 |
| S17 | T2 | oCERT-2011-003, "Multiple implementations denial-of-service via hash algorithm collision" | oCERT advisories | 2011 | oCERT-2011-003 | official-docs | https://ocert.org/advisories/ocert-2011-003.html | 2026-10-14 |

## Search log

| # | Rung | Database | Query | Returned |
|---|---|---|---|---|
| 1 | 1 | OpenAlex | full-text `adaptive indexing database cracking survey`, sorted by citations | noise (qualitative-research methods, physics-informed ML); full-text search unusable here, switched to title search |
| 2 | 1 | OpenAlex | `title.search: RUM conjecture` | Athanassoulis et al., EDBT 2016, 70 citations, open access: the general form of this post's trade-off |
| 3 | 1 | OpenAlex | `title.search: lower bounds for sorting 16 17 18` | Stober & Weiß 2023, SIAM ALENEX proceedings, arXiv copy |
| 4 | 1 | OpenAlex | `title.search: amortized computational complexity` | Tarjan 1985, SIAM J. Alg. Disc. Meth. 6(2), no open copy listed |
| 5 | 1 | OpenAlex | `title.search: denial of service via algorithmic complexity attacks` | Crosby & Wallach 2003, 316 citations, no DOI (USENIX legacy proceedings) |
| 6 | 1 | Crossref | bibliographic `Ford Johnson A tournament problem 1959` | AMM 66(5):387–389, DOI 10.1080/00029890.1959.11989306; paywalled, not read; merge insertion is cited through S1 |
| 7 | 1 | Crossref | bibliographic `Guibas Sedgewick dichromatic framework balanced trees` | FOCS 1978, pp. 8–21, DOI 10.1109/SFCS.1978.3 |
| 8 | 1 | Crossref | bibliographic `Flajolet Golin Mellin transforms asymptotics mergesort recurrence` | Acta Informatica 31(7):673–696, DOI 10.1007/BF01177551 |
| 9 | 1 | Crossref | bibliographic `Tarjan Updating a balanced search tree in O(1) rotations` | IPL 16(5):253–257 (1983); not read, and not needed once S4 §3 covered rotations |
| 10 | 1 | Crossref | bibliographic `Carter Wegman Universal classes of hash functions` | STOC 1977 abstract, JCSS 18(2) 1979; not read, so universal hashing is cited only as Crosby & Wallach's proposed fix |
| 11 | 1 | Crossref | DOI `10.1137/1.9781611977561.ch17` | confirms Stober & Weiß in the 2023 ALENEX proceedings, pp. 201–213 |
| 12 | 1 | OpenAlex | `title.search: database cracking` | Halim et al. PVLDB 2012, Schuhknecht et al. PVLDB 2013; adaptive indexing is covered through S6 instead |
| 13 | 1 | Google Scholar | `"amortized computational complexity" tarjan` | other Tarjan papers (pairing heaps, rank-balanced trees); not the 1985 paper |
| 14 | 1 | Google Scholar | `"a dichromatic framework for balanced trees"` | Sedgewick's own PDF of the 1978 paper (read); Andersson 1993; Tarjan 1983 |
| 15 | 1 | Google Scholar | `flajolet golin "mellin transforms and asymptotics" mergesort` | author copies FlGo93 and FlGo94 at algo.inria.fr (FlGo94 read) |
| 16 | 1 | Google Scholar | `allintitle:"amortized computational complexity"`, 1985 only | a course copy of Tarjan 1985 at jflap.org (read, all six pages) |
| 17 | 1 | DBLP | API search `Denial of Service via Algorithmic Complexity Attacks` | blocked by an Anubis bot wall; the key conf/uss/CrosbyW03 follows DBLP's scheme but could not be confirmed live |
| 18 | 1 | Semantic Scholar | API search, same title | HTTP 429, blocked |
| 19 | 4 | OpenAlex | `cites:W1563402047` (forward from Crosby & Wallach), by citations | 316 citing works; the most cited are tangential (RFC 5201, sensor-network ciphers) |
| 20 | 4 | OpenAlex | `cites:W1563402047` with `title.search: hash` | 23 works: Bar-Yosef & Wool 2008 show a randomised table attacked remotely, the same weakness PEP 456 cites; Lemire & Kaser 2013 on fast universal hashing |
| 21 | 4 | OpenAlex | `cites:W4315784878` (forward from Stober & Weiß) | 0 citing works |
| 22 | 4 | Google Scholar | cited-by of Stober & Weiß | 5 citations (Skonieczny 2026 on parallel sorting, Edelkamp 2017, a blog); nothing revises S(16) = 46 |
| 23 | 4 | OpenAlex | `cites:W2259014610` (forward from the RUM paper) | 71 works, mostly LSM trees (WiscKey, Monkey, an LSM survey); LSM is out of scope for this series |

Rungs 2, 3 and 5 ran as direct reads of the primary documents listed above: the two Java classes
and CPython's `dictobject.c` at their release tags, the Python and Java docs, PEP 456, JEP 180 and
the oCERT advisory. The lab's TreeMap port was then checked against the real class (see Open
questions).

## Claims

| Key | Claim (our words) | Source | Condition |
|---|---|---|---|
| L01 | Sorting 16 elements needs 46 comparisons in the worst case; 45 are not enough. Proved by exhaustive computer search | S1 abstract, Theorem 1.1 | worst case, comparison model |
| L02 | The information-theoretic lower bound is the ceiling of log2 n!, and S(n) is at least that | S1 §1 | worst case, comparison model |
| L03 | Knuth had conjectured S(16) = 45 (below the Ford–Johnson count); Stober and Weiß disproved it | S1 abstract and §1 | — |
| L04 | Ford and Johnson's merge insertion (1959) supplies the matching upper bound, 46 comparisons for 16 elements | S1 §1 | worst case |
| L05 | Worst case of top-down mergesort: T(n) = n lg n + nA(lg n) + 1 with A(u) = 1 − frac(u) − 2^(1 − frac(u)); at a power of two this is n lg n − n + 1 | S2 Theorem 1 | top-down, split into halves |
| L06 | Merging runs of p and v keys costs p + v − S comparisons, S being the keys left on the non-empty run; the worst case is S = 1 | S2 §1 | two-way merge |
| L07 | Amortised cost means averaging the running time per operation over a worst-case sequence of operations | S4 §1 | — |
| L08 | A red-black insertion repairs colours with flips that may continue up the tree, then ends with at most one single or one double rotation | S4 §3, Figs. 3–4 | insertion only |
| L09 | m consecutive insertions into an n-node red-black tree take O(n + m) total rebalancing, O(1) amortised per insertion | S4 §3 | consecutive insertions |
| L10 | The red-black (dichromatic) scheme stores one colour bit per node: every path from a node to its external nodes has the same number of black links, and no path has two red links in a row | S5 §1, conditions 1–3 | 2-3-4 variant |
| L11 | Guibas and Sedgewick introduced the red-black framework in 1978 | S5 | — |
| L12 | A hash table whose keys all land in one bucket, and an unbalanced binary tree fed sorted input, both degenerate into a linked list, so inserting n keys costs O(n²) | S3 §1 | chosen input |
| L13 | Programmers pick hash tables for their constant expected time, though one operation can cost O(n) in the worst case | S3 §2 | expected vs worst case |
| L14 | Inserting about 90,000 colliding strings took 6,506 s of CPU in Perl 5.6.1 against under 2 s for strings built for the other Perl version (6,838 s against under 2 s for 5.8.0) | S3 Table 1, §3.3 | 2003 hardware, Perl 5.6.1 and 5.8.0 |
| L15 | Crosby and Wallach proposed universal hashing as the fix, at a cost comparable to common hash functions | S3 abstract, §5 | — |
| L16 | PEP 456 (Final, Python 3.4) made SipHash the default hash for str and bytes, because the earlier randomisation's secret could be recovered by a remote attacker | S7 abstract, rationale | str and bytes |
| L17 | Python 3.11 moved str and bytes hashing to SipHash-1-3 (siphash13), bpo-29410 | S10 | CPython 3.11 and later |
| L18 | Hash randomisation salts the hashes of str and bytes; it guards dict construction against chosen-input O(n²) work; integers are not covered | S8 (`-R`, PYTHONHASHSEED) | CPython |
| L19 | Hash randomisation has been on by default since Python 3.3 | S9 (`object.__hash__`, changed in 3.3) | CPython |
| L20 | The 2011 advisory found predictable hash collisions in Java, PHP, Python, Ruby and others, and called it practically identical to the 2003 Perl report | S17 | 2011 versions |
| L21 | JDK 8 made a crowded HashMap bucket switch from a list to a balanced tree, taking the collision worst case from O(n) to O(log n) for keys that implement Comparable | S15 summary, description | JDK 8 and later |
| L22 | HashMap converts a bucket to a tree at 8 entries, but only once the table has at least 64 buckets (TREEIFY_THRESHOLD 8, MIN_TREEIFY_CAPACITY 64); tree bins order by hash code, then compareTo | S14 lines 160–275 | jdk-25-ga |
| L23 | HashMap promises constant-time get and put only if the hash spreads keys across buckets, and promises no iteration order | S14 class comment | — |
| L24 | TreeMap is a red-black tree implementing NavigableMap, with guaranteed log(n) time for containsKey, get, put and remove, adapted from Cormen, Leiserson and Rivest | S13 class comment; S16 | — |
| L25 | Each TreeMap entry holds key, value, left, right and parent references plus a boolean colour | S13 `Entry` | jdk-25-ga |
| L26 | TreeMap's first put into an empty map compares the key with itself, as a type and null check | S13 `addEntryToEmptyMap` | jdk-25-ga |
| L27 | `new TreeMap(sortedMap)` builds the tree in linear time without comparing keys (`buildFromSorted`) | S13 constructor comment | input already sorted |
| L28 | TreeMap answers floorKey and subMap with root-to-leaf descents (getFloorEntry, getCeilingEntry, getHigherEntry), then walks successor links without comparing | S13 | jdk-25-ga |
| L29 | Python's insort is O(n): its O(log n) search is dominated by the linear insertion step | S11 | list-backed |
| L30 | CPython's dict checks identity, then the stored hash, and calls `__eq__` only when the hashes are equal | S12 `compare_generic` | v3.14.0 |
| L31 | CPython's dict probes with i = 5i + perturb + 1 (perturb shifted right by 5 each step), starts at 8 slots, fills a table to two thirds, grows to the next power of two of at least three times its size in use, and looks a key up before it grows | S12 `do_lookup`, `insertdict`, constants | v3.14.0 |
| L32 | The RUM conjecture: an access method that bounds two of read, update and memory overhead must pay a lower bound on the third | S6 §3 | conjecture, unproved |
| L33 | A sorted column searches in logarithmic time but updates in linear time; a hash index has the fastest point query but must scan for a range; a B+-tree has the fastest range query | S6 §3, Table 1 | I/O model |
| L34 | Adaptive indexing (database cracking) builds an index gradually as queries arrive, spreading its creation cost over them | S6 §3 | — |

## Figure candidates

| Candidate | Source | Original figure | Section / claim served | Why this figure is necessary | Rights | Source URL | Decision |
|---|---|---|---|---|---|---|---|
| F1 | S6 | Figure 1 (data structures placed in the RUM triangle) | the RUM paragraph / L32 | it would show the general trade-off, but our own counted table carries the point for this post's four structures | CC BY-NC-ND 4.0: non-commercial, no derivatives | https://openproceedings.org/2016/conf/edbt/paper-12.pdf | do not reuse |
| F2 | S3 | Figures 1–2 (a hash table in normal use and with every key in one bucket) | the flooding section / L12 | our measured CPython counts say more than a schematic | USENIX: non-commercial educational reproduction only | https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf | do not reuse |

## Open questions

- **Counts are not time.** Every number here counts comparisons and element moves. A comparison in
  a sequential scan is far cheaper than one in a binary search or a tree descent (prefetching,
  predictable branches, vector instructions), so in wall-clock terms each break-even moves later.
  Nothing in this post measures by how much; the series' lab policy leaves timing to Part 4. The
  post says so wherever a count could be read as a speed.
- **Ford & Johnson (1959) and Knuth's TAOCP Vol. 3 were not read in this session.** Merge
  insertion's 46 comparisons for 16 keys and Knuth's conjecture are cited through Stober & Weiß,
  who state both.
- **TreeMap port verified, privately.** The lab's Python transliteration of TreeMap's put, get,
  ceiling, higher, floor and subMap was run beside the real `java.util.TreeMap` from Temurin JDK
  25.0.4.1 with a counting comparator, reading the tree by reflection. Per-insert comparisons, both
  tree shapes and colours, the lookup totals, floorKey(60), subMap(40, 70) and the insert of 50 all
  matched. The Java harness is not shipped.
- **CPython's flood count is 128, not 120.** The one-list model gives 0 + 1 + … + 15 = 120.
  CPython's probe sequence returns to the first key's slot on its fourth step while the table has 8
  or 16 slots, so inserts 4 to 11 each compare that key twice. The lab replays the probe sequence
  from the v3.14.0 constants (L31) and matches CPython exactly at 16, 64, 256 and 1,024 keys. The
  count is specific to CPython's growth policy and may change between versions.
