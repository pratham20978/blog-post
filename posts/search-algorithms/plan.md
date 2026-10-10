# Series plan — Search Algorithms: The Price of the Skip

**Slug:** search-algorithms · **Shape:** hybrid (hub and spokes, two short ladders) · **Parts:** 18 (1 published, 14 committed, 3 optional)

## Why this is a series and not one post

The hub, *Every Search Algorithm Is the Same Algorithm*, is already live and fixes the frame: one
loop (frontier, probe, eliminate), and a **prepaid structure** that decides how many candidates one
probe can eliminate. It spends about 400 to 625 words on each of its four families and stops at the
conclusion. It tells the reader to measure layout on their own machine, but never measures it. It
states that the complete question is "how many queries before this pays for itself", but never
works one out. It asserts that high-dimensional geometry is too weak for exact elimination, but
never shows it. It names the admissible-but-inconsistent failure without demonstrating it, and it
says ANN indexes belong on a recall curve without drawing one. Each of those answers needs the
hub's vocabulary to start. Beyond that, each needs a prerequisite the others do not share: the
cache hierarchy, string periodicity, heap amortisation, consistency, or high-dimensional geometry.
That makes a seam for each family. The fourteen committed spokes come to roughly 75,000 words and
117 figures, far past L4.

**The cut is ours to make.** The hub's published body names no child post. The only deferral
("a reader wanting KMP in full detail is served by a later L2 of its own") is in its private
`outline.md`, not in `blog.md`. No part below may claim that the hub promised it.

This is a **hybrid**. Most spokes are disjoint siblings that depend on the hub alone and link back
to one hub anchor. They are grouped under the hub's own four families (ordering, precomputation,
heuristic, geometry), plus one cross-cutting part that computes the hub's central claim. Two
seams are real ladders. Part 4 needs Part 3's fixed-trip boundary form, because only that form
can be made branch-free. Part 15 needs Part 14's evaluation method, because comparing currencies
means nothing without a fair curve. Difficulty is set per spoke. It rises inside each ladder
(beginner → advanced; intermediate → advanced) and varies freely everywhere else.

## The angle, and why it is not another set of algorithm tutorials

The scoping sweep found introductory material on this subject about as saturated as ground gets.
The owners: cp-algorithms, GeeksforGeeks and Wikipedia for binary search, KMP and Dijkstra. Russell
& Norvig and Red Blob Games for "BFS, DFS and A\* are one loop with a different queue". Slotin's
*Algorithms for Modern Hardware* for Eytzinger and S-trees. Pinecone's Faiss series and vendor docs
for HNSW. Russ Cox for regex backtracking. A post that restates any of them is worthless.

What nobody owns is the **price and the condition**. Every part answers the same four questions
for its own domain, on the hub's own three examples:

1. **What is prepaid?** Order, a table, an estimate, a graph, a model.
2. **What does it cost?** Build time, memory or layout, maintenance under writes, or accuracy.
3. **After how many queries does it pay back?**
4. **Which concrete input breaks it?**

Each part also corrects one claim that usually circulates without its condition. The sweep found
all of these stated unconditionally in top results:

- "Eytzinger is faster". The truth: batched throughput on arrays far larger than L3.
- "Interpolation search is O(log log n)". The truth: uniform keys only; the worst case is O(n).
- "Libraries use KMP or Boyer–Moore". The truth: glibc's `strstr` runs a hashed-pair Horspool for
  needles up to 256 bytes and Crochemore–Perrin Two-Way above that, and CPython added Two-Way for
  long needles in 3.10.
- "Boyer–Moore is sublinear". The truth: on average only.
- "A\* with h = 0 on unit costs is BFS". Holte lists it as a misconception.
- "Dijkstra was beaten in 2025". The truth: for distances, not for distance *order*.
- "A\* is optimally efficient". The truth: only with consistency and a stated tie-break.
- "Google Maps uses A\*". The truth: routers use preprocessing, and Google's method is not public.
- "In high dimensions all points are equidistant". The truth: only under Beyer et al.'s conditions.
- "HNSW recall is set by M and ef". The truth: insertion order and data move it too.
- "Alpha-beta is b^(d/2)". The truth: only under perfect move ordering.
- "WAND beats MaxScore". The truth: it depends on k and the number of terms.

## Reader objectives

| # | After this the reader can ... | Part |
|---|---|---|
| 1 | state any search task as frontier, probe and eliminate, and name the prepaid structure that raises the exchange rate | 1 |
| 2 | count eliminations per probe on a real trace and derive the log₂ n decision-tree bound | 1 |
| 3 | compute the query count at which building a search structure beats scanning, from counted operations | 2 |
| 4 | find the write-to-read ratio past which keeping keys sorted, in an array or a balanced tree, is a net loss | 2 |
| 5 | decide from the query types a workload needs (membership, range, predecessor, nearest) whether it needs a search at all | 2 |
| 6 | derive every binary-search variant — find, lower_bound, upper_bound, first-true — from one invariant instead of memorised update rules | 3 |
| 7 | binary-search a monotone predicate that is not an array: an answer space, a commit history, a list of unknown length | 3 |
| 8 | say which layout changes lower the price of a probe and which raise the exchange rate, and predict cache lines touched per query | 4 |
| 9 | benchmark search layouts across cache boundaries and report the result without over-generalising it | 4 |
| 10 | explain how a probe can return more than one bit, and why that does not contradict the comparison bound | 5 |
| 11 | name the key distributions that make interpolation search and learned indexes collapse | 5 |
| 12 | build the KMP failure function by hand and predict every Boyer–Moore and Horspool shift | 6 |
| 13 | say which substring algorithm a standard library actually runs for a given needle length, and why | 6 |
| 14 | recognise a catastrophically backtracking regex before it ships, and name the engine property that prevents it | 7 |
| 15 | decide when to prepay the text instead of the pattern, and price the index against re-scanning | 8 |
| 16 | follow an FM-index backward search as a shrinking interval of suffix-array rows | 8 |
| 17 | pick BFS, DFS, 0-1 BFS, Dijkstra, Bellman–Ford or A\* from the edge weights and the guarantee needed | 9 |
| 18 | state the real bound of a lazy-deletion binary-heap Dijkstra (the heap can hold up to m entries) and count its stale pops | 9 |
| 19 | explain why Dijkstra is universally optimal for distance order yet beatable for distances alone | 10 |
| 20 | diagnose a slow or wrong A\* from its heuristic, its tie-break and where its goal test runs | 11 |
| 21 | trade optimality for speed with weighted A\* and state the cost bound it keeps | 11 |
| 22 | price landmarks and contraction hierarchies in preprocessing time, space and settled nodes per query | 12 |
| 23 | say why a routing speedup measured on a continental graph does not transfer to a small one | 12 |
| 24 | measure the dimension at which bound-based pruning stops eliminating, and say which data escapes it | 13 |
| 25 | tune HNSW's M, efConstruction and efSearch against a measured recall-versus-throughput curve | 14 |
| 26 | account for an HNSW index's memory, build time and behaviour under deletes | 14 |
| 27 | choose between graph, quantised and disk-resident vector indexes from a memory, disk and recall budget | 15 |
| 28 | explain alpha-beta's best and worst cases from move ordering, and what engines prepay to approach the best | 16 |
| 29 | explain how MaxScore and WAND skip documents by upper bounds, and when the bounds stop pruning | 17 |
| 30 | say what a bounded frontier throws away, and tell a search error from a model error | 18 |

## Parts

**About the numbers below.** Some worked-example numbers are marked *(planning)*. They were
computed during scoping by throwaway scripts that first reproduced the hub's 58 and 33 with its own
`astar()`, and an independent review run re-checked them. They are still provisional. Each part
re-derives them in its own lab before citing them, and prints the counting convention next to any
count that depends on one.

**The grid, restated.** Every grid part (9, 10, 11, 12, 13, 18) restates the grid in two sentences
and one small figure, because the hub shows it only as a picture in Figure 5: 8 rows × 10 columns
in (row, col), 4-connected, unit cost, a wall in column 5 over rows 0–5, S (4, 1), G (4, 8),
74 open cells, 124 edges.

### Part 1 — Every Search Algorithm Is the Same Algorithm

- **Slug:** every-search-algorithm-is-the-same-algorithm
- **Tier:** L2 · **Difficulty:** intermediate · **Words:** 4,721 · **Figures:** 7
- **Answers:** why are binary search, KMP, A\* and HNSW one loop, and what actually separates them?
- **Assumes:** big-O notation, arrays and graphs, basic logarithms.
- **Hands off:** nothing by name. The open questions it leaves are listed under *Why this is a
  series* and are what the spokes own.
- **Worked example:** 16 sorted integers `3 9 14 21 28 35 42 47 53 61 68 74 79 85 91 97`, target 61
  at index 9. Linear scan: 10 probes. The prose trace (closed interval, midpoint ⌊(lo + hi)/2⌋)
  takes 3 probes, eliminating 8, 5 and 2 (worst case 5). Also `AABAAC` against `AABAABAABAAC`, and
  the 10×8 grid where Dijkstra expands 58 cells and A\* 33 on a cost-11 path.
- **Key sources:** the hub's 13 references, chiefly Dijkstra 1959, Hart, Nilsson & Raphael 1968
  and the 1972 correction, Knuth, Morris & Pratt 1977, Khuong & Morin 2017, and Malkov & Yashunin
  2020 (hub refs 1, 2, 3, 5, 9, 10).
- **Search intent:** "what do search algorithms have in common", "binary search vs A\* vs KMP",
  "search algorithms explained"
- **Status:** **published** at https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm.
  Lives at `posts/every-search-algorithm-is-the-same-algorithm/`, not under this folder (see *Open
  decisions*).

### Part 2 — Hash Map, Sorted Array or Tree? When a Search Structure Pays for Itself

- **Slug:** when-a-search-structure-pays-for-itself
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,000 · **Figures:** 6
- **Answers:** how many queries per build, and how few writes, does sorting, a tree or a hash
  table need before it beats a plain scan? And when should you not search at all?
- **Assumes:** Part 1's amortisation argument, the `#intuition` anchor. Big-O, and what a hash
  function is. Re-teaches the 16-integer trace in three sentences.
- **Hands off:** per-probe speed inside a sorted array goes to Part 4, and probing fewer than
  log₂ n times to Part 5. Hash-table internals are out of scope; hash flooding is covered only as
  collision cost, with PEP 456 cited for the fix and SipHash not explained. B-tree page splits
  belong to PostgreSQL Foundations Part 3 (planned; link it only once it is published). LSM trees
  and compaction are out of scope for both series. Part 2 may name the RUM conjecture (Athanassoulis
  et al., EDBT 2016) as the general form of its own trade-off.
- **Worked example:** the hub's 16 integers.
  - A successful linear lookup averages 8.5 probes. A three-way closed-interval binary search (the
    hub's prose procedure) averages 3.375, worst case 5.
  - Merge sort costs at most 49 comparisons here, against an information floor of
    ⌈log₂ 16!⌉ = 45. So sorting pays back after about 10 lookups. That figure sets a worst-case sort
    against average lookups, and the part says so.
  - Inserting 50 shifts 8 elements.
  - The same 16 keys in a balanced BST (the red-black tree behind `TreeMap`). Count the
    comparisons to find 61, and what inserting 50 costs: one root-to-leaf path plus rotations and no
    shifts, all counted in the lab, against the sorted array's 8 shifts.
  - The range query [40, 70] costs two binary searches plus 5 reads; a hash set must scan all 16.
  - "Largest value ≤ 60" returns 53, which no hash can answer.
  - Sixteen keys forced into one bucket cost 0 + 1 + … + 15 = 120 comparisons to insert. That is
    hash flooding, the price of hashing.
  - Every small-n number is generalised by formula, so "sort after 10 queries" does not become a
    rule of thumb.
- **Key sources:** Knuth, *TAOCP* Vol. 3, 2nd ed. (1998), §5.3.1, §6.2.1, §6.4; Crosby & Wallach,
  "Denial of Service via Algorithmic Complexity Attacks", 12th USENIX Security Symposium, 2003;
  Tarjan, "Amortized Computational Complexity", *SIAM J. Algebraic Discrete Methods* 6(2):306–318,
  1985; PEP 456 (SipHash-2-4 from Python 3.4; SipHash-1-3 from 3.11).
- **Search intent:** "hash map vs sorted array", "is it worth sorting before binary search",
  "hashmap vs treemap performance", "should I sort an array before searching it"

### Part 3 — Why Your Binary Search Is Off by One

- **Slug:** why-your-binary-search-is-off-by-one
- **Tier:** L2 · **Difficulty:** beginner · **Est. words:** 3,500 · **Figures:** 6
- **Answers:** why does a binary search loop forever or return the wrong index? And what one
  invariant writes every variant correctly, including searches over things that are not arrays?
- **Assumes:** Part 1's halving rule, the `#ordering-buys-the-skip` anchor. The overflow bug is
  linked there, not re-told. Loops and integer division, nothing more. Restates frontier, probe and
  eliminate in three sentences, which is why this spoke can be beginner.
- **Hands off:** layout and branch-free speed go to Part 4. Part 4 starts from this part's
  fixed-trip boundary form, so the section that defines it is headed "The fixed-trip boundary
  form" (anchor `#the-fixed-trip-boundary-form`). Probing fewer than log₂ n times goes to Part 5.
- **Worked example:** the hub's 16 integers.
  - Boundary queries: lower_bound(61) = 9, upper_bound(61) = 10, lower_bound(60) = 9 (an absent
    value's insertion point), lower_bound(100) = 16, lower_bound(2) = 0.
  - **The midpoint convention.** The hub's prose trace probes 47, 74, 61 (3 probes, closed
    interval). The hub's own half-open `binary_search()` code probes 53, 79, 68, 61 (4 probes) for
    the same target. Both average 3.375 probes, worst case 5. This is a midpoint convention, not a
    hub error, and the part says which one it traces.
  - The classic bug: "last index with a[i] ≤ t", written with `while lo < hi` on a closed interval
    with `lo = mid`. For t = 61 it traces (lo, hi, mid) = (0,15,7), (7,15,11), (7,10,8), (8,10,9),
    then sticks at (9,10,9) forever. *(planning)* 10 of the 16 stored values hang it, and t = 60 is
    one of the few targets that pass, which is why a one-target test passes. The loop condition is
    printed, because `while lo <= hi` hangs on 60 too.
  - **The fixed-trip lower_bound.** A (base, len) loop halves len every trip and has no equality
    test. It makes the same number of comparisons for every target (count it in the lab), unlike the
    (lo, hi) loop above. It gets its own heading, which is Part 4's anchor.
  - The array read as 16 commits with the first bad one at 9: `git bisect` needs 4 builds.
  - Exponential search without knowing n brackets 61 by doubling, then bisects the bracket.
  - The last section: what one flaky "bad" verdict does to a bisection.
- **Angle:** the half-open interval *is* the frontier. The invariant is "everything outside the
  frontier was eliminated soundly", and every variant is the same loop with a different
  `eliminate`. The prepaid structure need not be a sorted array; a monotone predicate is enough. Not
  a variant catalogue: Dasdan's 2026 arXiv survey owns that exhaustively.
- **Key sources:**
  - Pattis, "Textbook Errors in Binary Searching", SIGCSE 1988.
  - Bentley, *Programming Pearls*, Column 4. Professional programmers had "a couple of hours", and
    "ninety percent of the programmers found bugs in their programs". The fetched quote is from the
    1st edition; check the 2nd-edition page.
  - Knuth, *TAOCP* Vol. 3 §6.2.1 for the history: Mauchly 1946, Lehmer 1960 (first correct for all
    n), Bottenbruch 1962. "1946 and 1962" is Bentley's paraphrase; read §6.2.1 before quoting.
  - Bentley & Yao, "An Almost Optimal Algorithm for Unbounded Searching", *IPL* 5(3), 1976.
  - The `git-bisect` documentation.
- **Search intent:** "binary search off by one", "binary search infinite loop", "lower_bound vs
  upper_bound", "binary search on answer", "how does git bisect work"

### Part 4 — Is Eytzinger Faster Than Binary Search? Measuring Memory Layouts

- **Slug:** eytzinger-vs-binary-search-memory-layouts
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** with the comparison count fixed near log₂ n, what makes one binary search several
  times faster than another? And how do you measure which layout wins on your own machine?
- **Assumes:** **Part 3**, not Part 1. It needs Part 3's fixed-trip lower_bound with no equality
  test, the only form that can be made branch-free. Planned anchor: `#the-fixed-trip-boundary-form`.
  Also reading C, cache lines, and branch misprediction. Re-teaches the boundary form in one
  paragraph for readers arriving from search.
- **Hands off:** whether to keep a sorted array at all goes to Part 2, and using key values to
  probe fewer times to Part 5. Write costs of static layouts are out of scope.
- **Worked example:** the hub's 16 integers in Eytzinger order (1-indexed):
  `53 28 79 14 42 68 91 9 21 35 47 61 74 85 97 3`.
  - `k = 2k + (b[k] < x)` walks 1, 3, 6, 12 (values 53, 79, 68, 61) for target 61. That is 4 steps
    for most targets and 5 for targets ≤ 9, whose path reaches node 16, because n = 16 is not
    2ᵏ − 1. There is no data-dependent branch inside the loop. The hub's prose trace found 61 in 3
    and its half-open code in 4.
  - All 16 keys fit one 64-byte line, so the shared example shows only the index arithmetic.
  - The speed claim comes from a C lab timing four variants: branchy sorted, branch-free sorted,
    Eytzinger with prefetch, and 16-key B-tree nodes.
  - Sizes run from n = 2¹⁰ past last-level cache. Every variant is first checked against a
    reference lower_bound on all n + 1 gaps, and the CPU model and compiler are stated.
  - The hub says the two layouts "perform the *same number* of comparisons". The part words that as
    true of the fixed-trip two-way form, not of the three-way early-exit loop.
- **Angle:** separate two things the popular posts blur. Eytzinger order, branch-free code and
  prefetching keep the elimination schedule and **lower the price per probe**. B-tree and S-tree
  nodes **raise the exchange rate**: one SIMD probe of 16 keys eliminates about 16/17 of the
  frontier. Headline multipliers are quoted with their conditions, or not at all.
- **Key sources:** Khuong & Morin, "Array Layouts for Comparison-Based Searching", *ACM JEA* 22,
  Article 1.3, 2017 (arXiv:1509.05053); Brodal, Fagerberg & Jacob, "Cache Oblivious Search Trees
  via Binary Trees of Small Height", SODA 2002, pp. 39–48 (the hub's ledger wrongly says 2003);
  Frigo, Leiserson, Prokop & Ramachandran, "Cache-Oblivious Algorithms", FOCS 1999; Slotin,
  *Algorithms for Modern Hardware* (S-trees), as the practitioner reference this part must beat.
- **Search intent:** "eytzinger layout binary search", "branchless binary search", "cache friendly
  binary search", "why is binary search slow on large arrays"

### Part 5 — Beating log n: Interpolation Search and Learned Indexes

- **Slug:** beating-log-n-interpolation-search-learned-indexes
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 5,500 · **Figures:** 9
- **Answers:** how can a search of sorted keys take fewer than log₂ n probes without contradicting
  the comparison bound? What is prepaid instead of order, and which key distributions make it
  collapse?
- **Assumes:** Part 1's decision-tree bound, the `#the-math` anchor: p ≥ log₂ n because each
  comparison yields at most one bit. Cumulative distribution functions and a least-squares line.
- **Hands off:** cache-level speedups at the same probe count go to Part 4. The general
  write-to-read break-even for keeping keys sorted goes to Part 2. The model's own write price stays
  here as this part's breaking input: an insert that breaks the error bound forces a refit. Hashing
  stays outside the frame, as the hub ruled. It appears only as the limit where the model is exact
  and order is thrown away.
- **Worked example:** the hub's 16 integers.
  - Interpolation probes position 0 + (61 − 3)·15/(97 − 3) = 9.26, so index 9, and finds 61 in
    **1** probe.
  - Replace 97 with 10,000 and the same search takes **10** probes: exactly the hub's linear scan.
  - A least-squares line, position ≈ 0.157·key − 0.416, predicts 9.16 for 61, with a maximum error
    of 0.26 across all 16 keys. So a learned index checks one slot.
  - Its entire prepaid structure is two floats and an error bound, and one skewed key invalidates
    it.
- **Key sources:** Perl, Itai & Avni, "Interpolation Search — A Log Log N Search", *CACM* 21(7),
  1978; Kraska et al., "The Case for Learned Index Structures", SIGMOD 2018; Ferragina &
  Vinciguerra, "The PGM-index", *PVLDB* 13(8):1162–1175, 2020; Marcus et al., "Benchmarking Learned
  Indexes", *PVLDB* 14(1), 2021.
- **Search intent:** "interpolation search vs binary search", "learned index structures explained",
  "search sorted keys in fewer than log n probes", "is O(log n) search optimal"

### Part 6 — KMP, Boyer–Moore or Two-Way: Which Substring Search Actually Runs

- **Slug:** kmp-boyer-moore-or-two-way
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** what exactly do KMP, Boyer–Moore, Horspool and Two-Way precompute from the pattern?
  What does each table cost, and which one does your standard library actually run, at which
  needle length?
- **Assumes:** Part 1's `AABAAC` trace and the text pointer that never rewinds, the
  `#precomputation-buys-the-skip` anchor. Strings, arrays, O(m + n). Re-traces the mismatch in one
  paragraph.
- **Hands off:** regex engines go to Part 7, and indexing the text instead of the pattern to
  Part 8. Many patterns at once (Aho–Corasick, where the failure function becomes an automaton) is
  owned here as a closing section. Rabin–Karp gets one paragraph, as a hash used for a *cheaper
  probe* rather than to avoid a search.
- **Worked example:** `AABAAC` in `AABAABAABAAC`, match at 6. Every count uses one convention: each
  character comparison is counted once and its result reused. The textbook while/if KMP loop
  re-tests successful pairs and costs 25, 81 and 199 on the three cases below, so the part prints
  the loop it counted.
  - The failure table is [0, 1, 0, 1, 2, 0], built in 8 comparisons. Building it is itself a KMP
    run of the pattern against itself.
  - Character comparisons: naive 24, KMP 14, Horspool 8 (shift table A:1, B:3, other:6).
  - Two adversaries *(planning)*. First, the KMP paper's own case at n = 16: naive 289 = (n + 1)²,
    KMP 49, Horspool 33. Second, a¹⁰ in a¹⁰⁰ with 91 matches: naive 910, KMP 100, and both
    unmodified Boyer–Moore and Horspool 910. That is why Galil's rule exists.
  - The close: what glibc and CPython actually run, read from their source. glibc's generic
    `strstr` uses a linear scan for needles ≤ 3, a hashed-pair Horspool up to 256, and Two-Way
    above that; CPython 3.10 added Two-Way for long needles.
- **Key sources:** Knuth, Morris & Pratt 1977 and Boyer & Moore 1977 (hub refs 5, 6); Horspool,
  "Practical Fast Searching in Strings", *SP&E* 10(6), 1980; Galil, *CACM* 22(9), 1979; Crochemore
  & Perrin, "Two-Way String-Matching", *JACM* 38(3), 1991; Aho & Corasick, *CACM* 18(6), 1975;
  glibc `string/strstr.c` and `string/str-two-way.h`, CPython `Objects/stringlib/fastsearch.h`, and
  the Python 3.10 *What's New* (bpo-41972), as primary evidence.
- **Search intent:** "kmp vs boyer moore", "boyer moore worst case", "how is the KMP failure
  function built", "what algorithm does strstr use", "Aho-Corasick explained"

### Part 7 — Why Your Regex Hangs: Backtracking Is a Search That Never Eliminates

- **Slug:** why-your-regex-hangs-catastrophic-backtracking
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,300 · **Figures:** 6
- **Answers:** why does one regex take milliseconds on 16 characters and minutes on 30, and what
  makes a regex engine linear-time?
- **Assumes:** Part 1's guarantee that the text pointer never moves back, the
  `#precomputation-buys-the-skip` anchor. The reader writes regexes; no automata theory is assumed.
- **Hands off:** substring algorithms go to Part 6. Regex syntax tutorials and DFA minimisation are
  out of scope.
- **Worked example:** `(A+)+B` against 16 A's and no B.
  - The backtracker must reject at least 2¹⁵ = 32,768 ways of splitting the A's before it can fail.
    From one start position a naive backtracker makes 2¹⁶ − 1 attempts, more across start
    positions.
  - *(planning, Python 3.14 on this machine)* 4.35 ms at 16 A's, 17.4 ms at 18, 68.9 ms at 20 and
    278 ms at 22: about ×4 for every two characters.
  - A Thompson simulation of the same NFA keeps at most one copy of each state per text position.
    Its frontier is a state set, duplicates are eliminated, and its text pointer never moves back.
    That is KMP's guarantee, generalised.
  - The lab re-measures on the reader's machine.
- **Key sources:** Thompson, "Regular Expression Search Algorithm", *CACM* 11(6):419–422, 1968;
  Cox, "Regular Expression Matching Can Be Simple and Fast", 2007; Davis, Coghlan, Servant & Lee,
  "The Impact of Regular Expression Denial of Service (ReDoS) in Practice: An Empirical Study at the
  Ecosystem Scale", ESEC/FSE 2018; Cloudflare's report on its 2 July 2019 outage. That was a WAF
  regex that backtracked catastrophically, and a removed CPU guard contributed.
- **Search intent:** "regex catastrophic backtracking", "why is my regex so slow", "ReDoS
  explained", "RE2 vs PCRE"

### Part 8 — Prepaying the Text: Suffix Arrays and the FM-Index

- **Slug:** suffix-arrays-and-the-fm-index
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** when the text is fixed and the queries keep coming, how do suffix arrays and the
  FM-index turn string search back into binary search? And after how many queries do they beat
  re-scanning?
- **Assumes:** Part 1's `#precomputation-buys-the-skip`: KMP's O(m + n) pattern-side guarantee is
  the baseline this part prices against. Also sorting, binary search, and lexicographic order.
  Links Part 6 for the full pattern-side tables but does not depend on it.
- **Hands off:** pattern-side tables go to Part 6. Word-level inverted indexes get one paragraph
  here, as the word-level text index that cannot answer arbitrary substrings. They are otherwise out
  of scope; Part 17, if written, assumes one exists and does not teach it. Compression beyond the
  BWT is out of scope.
- **Worked example:**
  - The suffix array of the hub's text `AABAABAABAAC` is [0, 3, 6, 9, 1, 4, 7, 10, 2, 5, 8, 11].
    A half-open lower_bound (Part 3's boundary form) finds `AABAAC` at suffix 6 in 4 probes.
    *(planning)* Those probes cost 17 character comparisons against KMP's 14 in Part 6's unit.
  - So at n = 12 the index loses even before its build cost. It wins because its query cost grows
    with m·log n rather than n. The lab computes the crossover n.
  - The BWT of `AABAABAABAAC$`, with `$` sorted first, is `C$BBBAAAAAAAA`. An FM-index backward
    search for `AABAAC` narrows [sp, ep) as C:[12,13), A:[8,9), A:[4,5), B:[11,12), A:[7,8),
    A:[3,4). Row 3 maps to suffix 6: the frontier as an interval.
  - Scale-up: a 3.1-billion-base genome needs a 12.4 GB 32-bit suffix array against about 3.1 GB of
    text. BWA's manual gives about 5 GB of memory to index the human genome, and about 3.2 GB for
    `aln`. That is why read aligners use the FM-index.
- **Key sources:** Manber & Myers, "Suffix Arrays", *SIAM J. Comput.* 22(5), 1993; Burrows &
  Wheeler, SRC Research Report 124, Digital Systems Research Center, 1994; Ferragina & Manzini,
  "Opportunistic Data Structures with Applications", FOCS 2000; Li & Durbin, *Bioinformatics*
  25(14):1754–1760, 2009.
- **Search intent:** "suffix array explained", "suffix array vs suffix tree", "FM index explained",
  "burrows wheeler transform search"

### Part 9 — BFS, DFS, Dijkstra or A\*? The Frontier Decides

- **Slug:** bfs-dfs-dijkstra-or-a-star
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** given my graph's edge weights and the guarantee I need, which of BFS, DFS, 0-1 BFS,
  Dijkstra, Bellman–Ford or A\* should run, and with which frontier data structure?
- **Assumes:** Part 1's `search(frontier, pick, test, eliminate)` skeleton and its `astar()` code,
  the `#implementation` anchor. Graphs, and what a queue, a stack and a heap are. Restates the grid.
- **Hands off:** A\* failure modes, including tie-breaks and goal-test placement, go to Part 11.
  Decrease-key, Fibonacci and working-set heaps and their amortised bounds go to Part 10; this part
  states O(m + n log n) in one sentence, with a link to the hub's `#a-heuristic-buys-the-skip`.
  Preprocessing speedups go to Part 12. Iterative deepening and memory-bounded frontiers go to
  Part 18 if it is written, and are otherwise out of scope.
- **Worked example:** the hub's grid (74 open cells, 124 edges). *(planning)*
  - The hub's conventions (goal tested on pop, (f, g, node) ties) are stated in one sentence and not
    varied here.
  - BFS expands 58 at cost 11, and Dijkstra also expands 58 on this grid. The equal count is not an
    identity, which is Holte's point: the two pop in different orders, and BFS may test the goal when
    a node is generated.
  - DFS returns a path costing anywhere from 17 to 55, depending only on neighbour order.
  - Greedy best-first expands 15–16 cells and happens to find cost 11, with no guarantee.
  - A\* expands 33.
  - The hub's lazy-deletion heap Dijkstra, with pushes, pops and stale entries counted.
  - A hand-built graph with one negative edge, where Dijkstra is wrong and Bellman–Ford is right.
- **Angle:** the hub's frame is *not* new here; it is the textbook framing. So the part stands out
  on measured counts and on guarantee conditions. Holte's misconceptions go here: A\* with h = 0 on
  unit costs is not BFS, and swapping the queue for a stack while marking nodes visited on push is
  not true DFS.
- **Key sources:** Moore, "The Shortest Path Through a Maze", Proc. International Symposium on the
  Theory of Switching (Harvard University Press, 1959; symposium held 1957); Bellman, "On a Routing
  Problem", *Q. Appl. Math.* 16(1):87–90, 1958; Holte, "Common Misconceptions Concerning Heuristic
  Search", SoCS 2010; Chen, Chowdhury, Ramachandran, Roche & Tong, "Priority Queues and Dijkstra's
  Algorithm", UTCS TR-07-54, 2007.
- **Search intent:** "bfs vs dfs vs dijkstra", "when to use dijkstra vs bfs", "dijkstra negative
  weights", "0-1 bfs", "dijkstra priority queue lazy deletion"

### Part 10 — Is Dijkstra Optimal? Universal Optimality and the Sorting Barrier

- **Slug:** is-dijkstra-optimal-sorting-barrier
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 5,500 · **Figures:** 9
- **Answers:** in 2024 Dijkstra's algorithm was proved universally optimal, and in 2025 it was
  beaten. How are both true, and what does each say about the price of keeping the frontier in
  sorted order?
- **Assumes:** Part 1's `#a-heuristic-buys-the-skip`: the 1959 paper had no heap, and
  O(m + n log n) is Fredman–Tarjan's. Also heaps and amortised analysis. Restates the grid. Links
  Part 9 for the frontier container, if it is published, but does not depend on it.
- **Hands off:** the practical choice of heap goes to Part 9. This part owns decrease-key,
  Fibonacci and working-set heaps. It is theory, with one measured illustration.
- **Worked example:** the hub's grid with edge weights drawn by `random.Random(1959).randint(1, 9)`
  over the 124 edges in sorted order. *(planning)*
  - With h = 0, the hub's `astar()` returns cost 47 after 74 heap pushes and 68 pops. Nine of the
    pops are stale, which leaves 59 expansions.
  - Print the vertices in the order Dijkstra settles them: the sort you did not ask for.
  - Then compare a working-set heap's delete-min cost with a binary heap's on the same run.
- **The reconciliation this part owns:** universal optimality is for the **distance-order**
  problem, using a heap with the working-set property. Duan et al. give a deterministic
  O(m log^(2/3) n) algorithm for single-source shortest paths on directed graphs with real
  non-negative weights, in the comparison-addition model. They compute the **distances alone** and
  never produce the order, which is how they get under the sorting bound on sparse graphs.
- **Key sources:** Haeupler, Hladík, Rozhoň, Tarjan & Tětek, "Universal Optimality of Dijkstra via
  Beyond-Worst-Case Heaps", FOCS 2024; Duan, Mao, Mao, Shu & Yin, "Breaking the Sorting Barrier for
  Directed Single-Source Shortest Paths", STOC 2025 (arXiv:2504.17033); Fredman & Tarjan 1987 and
  Dijkstra 1959 (hub refs 11, 1).
- **Search intent:** "is dijkstra optimal", "dijkstra universally optimal", "faster than dijkstra
  2025", "breaking the sorting barrier shortest path"

### Part 11 — Why Your A\* Is Slow or Wrong

- **Slug:** why-your-a-star-is-slow-or-wrong
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** my A\* returns a longer path than it should, or expands far too many nodes. Which of
  the common causes is it, and when should I give up optimality on purpose with weighted A\*?
- **Assumes:** Part 1's `#the-math`: f = g + h, and the admissible and consistent definitions,
  together with the `astar()` code in `#implementation`. Restates the grid.
- **Hands off:** frontier choice beyond A\* goes to Part 9, and heuristics bought by preprocessing
  to Part 12. IDA\* goes to Part 18 if it is written, and is otherwise out of scope. Jump point
  search gets one section, as a skip bought from grid symmetry for zero memory. This part owns
  tie-breaking and goal-test placement as failure modes.
- **Worked example:** the hub's grid. *(planning)*
  - The hub's A\* expands 33 with its (f, g, node) tuples, which break ties toward *low* g. Flip
    only the tie-break and the same heuristic expands **21** at the same cost 11.
  - A Euclidean h on the 4-connected grid expands 41.
  - Weighted A\* at w = 2 expands 21 and at w = 5 expands 16. Both still return cost 11 here,
    under the cost ≤ w·optimal bound.
  - A five-node graph with an admissible but inconsistent h. Textbook closed-set A\* returns cost
    6; the hub's reopen-on-better-g code returns 5 at the price of one re-expansion; testing the
    goal on push returns 11.
- **Key sources:** Hart, Nilsson & Raphael 1968, the 1972 correction, and Dechter & Pearl 1985
  (hub refs 2–4); Martelli, "On the Complexity of Admissible Search Algorithms", *AI* 8(1), 1977;
  Pohl, "Heuristic Search Viewed as Path Finding in a Graph", *AI* 1(3–4):193–204, 1970; Holte,
  SoCS 2010 (as Part 9); Harabor & Grastien, "Online Graph Pruning for Pathfinding on Grid Maps",
  AAAI 2011.
- **Search intent:** "a\* not finding shortest path", "a\* too slow", "admissible vs consistent
  heuristic", "a\* tie breaking", "weighted a\*"

### Part 12 — Contraction Hierarchies and Landmarks: What Road Routers Prepay

- **Slug:** road-routing-landmarks-contraction-hierarchies
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** how do road routers answer shortest-path queries on continental graphs in well under
  a millisecond, and what do they prepay to do it?
- **Assumes:** Part 1's A\* as Dijkstra plus a prepaid estimate, the `#a-heuristic-buys-the-skip`
  anchor. The triangle inequality. Restates the grid.
- **Hands off:** A\* debugging goes to Part 11. Time-dependent, multimodal, transit and
  live-traffic routing are out of scope. No sentence says what a named product runs without a
  primary source.
- **Worked example:** the hub's grid as a 74-node, 124-edge graph. *(planning)* Counts are
  reported under both tie-breaks, the hub's (low g) and Part 11's flipped one (high g).
  - ALT with four corner landmarks costs 4 BFS runs (296 stored distances). It expands 22 cells
    against Manhattan A\*'s 33 with low-g ties, and 12 against 21 with high-g ties, because the
    landmarks know about the wall.
  - A single badly placed landmark at (7, 0) expands 48, worse than the free Manhattan heuristic.
  - Bidirectional Dijkstra settles 63, worse than one-directional Dijkstra's 58 at this scale.
  - So at 74 nodes the landmarks repay their 296 settlements only after about 27 to 33 queries,
    depending on the tie-break. The speedups belong to continental graphs, not to the algorithms.
  - A small subgraph contracted by hand, then continental preprocessing and query figures quoted
    from Bast et al. (read them from the survey before quoting).
  - Pattern databases get one section: the same purchase in puzzle space.
- **Key sources:** Goldberg & Harrelson, "Computing the Shortest Path: A\* Search Meets Graph
  Theory", SODA 2005; Geisberger, Sanders, Schultes & Delling, "Contraction Hierarchies", WEA 2008;
  Bast et al., "Route Planning in Transportation Networks", LNCS 9220, 2016; Culberson & Schaeffer,
  "Pattern Databases", *Computational Intelligence* 14(3), 1998.
- **Search intent:** "contraction hierarchies explained", "how does google maps find the shortest
  route so fast", "ALT landmarks A\*", "route planning algorithms road network"

### Part 13 — k-d Trees and the Dimension Where Pruning Dies

- **Slug:** kd-trees-and-where-pruning-dies
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** how does a k-d tree eliminate a whole region with one bound test, and at what
  dimension does that test stop eliminating anything?
- **Assumes:** Part 1's claim that high-dimensional geometry is too weak for exact elimination, the
  `#geometry-buys-the-skip` anchor. The hub asserts it; this part measures it. Euclidean distance,
  binary trees, recursion. Restates the grid.
- **Owns:** the series' canonical wording of **bound-based elimination** (branch and bound). Parts
  16 and 17 restate it from `context.md` rather than re-deriving it.
- **Hands off:** approximate indexes go to Parts 14 and 15.
- **Worked example:** *(planning)*
  - The grid's 74 open cells as 2-D points. A nearest open cell to wall cell (3, 5) is (3, 6), at
    distance 1. It ties with (3, 4), so the part states its tie rule. A median-split tree
    that splits on the column first finds it after about 7 distance tests out of 74; the count
    depends on the build.
  - Then 4,000 uniform random points with 20 queries per dimension. The share of points that must be
    distance-tested is 0.4% at d = 2, 1.4% at d = 4, 17% at d = 8, 99% at d = 16, and 100% at
    d = 32 and 64.
  - Then the same measurement on data with low intrinsic dimension in a high ambient space, where
    pruning survives. Beyer et al.'s conditions are stated, not "all points are equidistant".
- **Key sources:** Bentley, "Multidimensional Binary Search Trees Used for Associative Searching",
  *CACM* 18(9):509–517, 1975; Friedman, Bentley & Finkel, "An Algorithm for Finding Best Matches in
  Logarithmic Expected Time", *ACM TOMS* 3(3):209–226, 1977; Weber, Schek & Blott, VLDB 1998;
  Beyer, Goldstein, Ramakrishnan & Shaft, "When Is 'Nearest Neighbor' Meaningful?", ICDT 1999.
- **Search intent:** "kd tree nearest neighbor", "why kd trees fail in high dimensions", "curse of
  dimensionality nearest neighbor", "kd tree vs brute force"

### Part 14 — Tuning HNSW: Recall, Throughput and What the Index Costs

- **Slug:** tuning-hnsw-recall-throughput-cost
- **Tier:** L3 · **Difficulty:** intermediate · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** how do HNSW's M, efConstruction and efSearch move you along a recall-versus-
  throughput curve, and what does the index cost in memory, build time and updates?
- **Assumes:** Part 1's `#geometry-buys-the-skip`: the layered descent, "logarithmic complexity
  scaling" as a design claim, and comparison on a curve. Vectors, cosine and Euclidean distance,
  Python with numpy. It takes the hub's assertion that exact search fails as given, and does not
  measure it: that is Part 13's subject. A see-also to Part 13 is added only if Part 13 is already
  published.
- **Owns:**
  - **The series' method for honest ANN evaluation.** Brute-force ground truth, recall@k against
    QPS, and build time and memory drawn *on* the chart, because by the hub's thesis they are the
    price of the skip. Its section is headed "Measuring an ANN index honestly" (anchor
    `#measuring-an-ann-index-honestly`), and Part 15 reuses the method.
  - **efSearch as a bounded frontier.** It gets its own heading, and Parts 15 and 18 link back to
    it.
- **Hands off:** other ANN families go to Part 15. Filtered search gets section depth only. GPU
  indexes and vector-database operations are out of scope.
- **Worked example:** 10,000 SIFT-128 vectors (verify the subset's format and licence), hnswlib at
  M = 16.
  - The level rule P(level ≥ l) = 16⁻ˡ puts about 625 nodes on layer 1, 39 on layer 2 and 2.4 on
    layer 3. That is the hub's three-layer picture, derived rather than drawn.
  - efSearch is the size of a bounded frontier. The layer-0 best-first search keeps only the ef
    closest candidates and forgets the rest, so ef is a beam width.
  - Sweep ef over {10, 20, 40, 80, 160, 320} and measure recall@10 against brute force, alongside
    QPS.
  - Repeat the sweep at n = 1k, 10k and 100k from the same dataset, and plot distance computations
    per query at fixed recall@10 against log n. That measures the hub's design claim.
  - Memory: hnswlib allows maxM0 = 2M = 32 layer-0 links, stored as 4-byte ids plus a 4-byte count.
    That is 132 bytes per vector (confirmed in source; re-check before quoting), against 512 bytes
    of vector data.
  - Mark 10% of the points deleted and re-measure recall.
  - Show the insertion-order effect: Elliott & Clark report shifts of up to 12 percentage points.
- **Key sources:** Malkov & Yashunin, *TPAMI* 2020, and Aumüller et al., ANN-Benchmarks, 2020 (hub
  refs 10, 12); Malkov, Ponomarenko, Logvinov & Krylov, the NSW predecessor, *Information Systems*
  45:61–68, 2014; Elliott & Clark, "The Impacts of Data, Ordering, and Intrinsic Dimensionality on
  Recall in Hierarchical Navigable Small Worlds", ICTIR 2024; hnswlib source and documentation.
- **Search intent:** "HNSW parameters M ef_construction ef_search", "HNSW recall vs latency", "how
  to measure ANN recall", "HNSW explained"

### Part 15 — HNSW, IVF-PQ or DiskANN? Three Currencies for Approximate Search

- **Slug:** hnsw-ivf-pq-or-diskann
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,500 · **Figures:** 10
- **Answers:** once exact pruning is dead, what does each approximate-index family prepay (graph
  edges, cluster centroids, compressed codes, SSD layout)? And which one fits a given memory, disk
  and recall budget?
- **Assumes:** **Part 14**'s evaluation method and its recall-versus-QPS curve. Planned anchor:
  `#measuring-an-ann-index-honestly`. k-means at the level of "assign to the nearest centroid".
- **Hands off:** learned rerankers, embedding models and RAG are out of scope; the exact-distance
  re-scoring of PQ candidates is in scope. Lexical top-k goes to Part 17 if it is written.
- **Worked example:** a budget for 1M × 768-dimensional float32 vectors, 3.07 GB raw.
  - HNSW at M = 16 adds about 132 MB of layer-0 links, plus about 1/M more for the upper layers.
  - IVF-PQ with 96 one-byte codes stores 96 MB of codes (plus ids and codebooks). That is a 32×
    compression, paid for in recall and usually bought back with an exact re-rank against full
    vectors.
  - IVF with nlist = 1024 and nprobe = 8 scans about 7,800 vectors per query if the lists are
    balanced. nprobe is a frontier-size knob, like Part 14's efSearch.
  - Then a faiss-cpu and hnswlib lab plots flat, IVF-PQ and HNSW on Part 14's curve.
  - LSH gets one section, with hash buckets as a prepaid candidate set: the currency with a
    guarantee and the weakest practical numbers.
- **Key sources:** Jégou, Douze & Schmid, "Product Quantization for Nearest Neighbor Search",
  *TPAMI* 33(1), 2011; Subramanya et al., "DiskANN", NeurIPS 2019; Guo et al., "Accelerating
  Large-Scale Inference with Anisotropic Vector Quantization", ICML 2020; Indyk & Motwani,
  "Approximate Nearest Neighbors: Towards Removing the Curse of Dimensionality", STOC 1998,
  pp. 604–613; Simhadri et al., NeurIPS'21 big-ann-benchmarks results.
- **Search intent:** "hnsw vs ivf", "product quantization explained", "which faiss index to
  choose", "DiskANN explained"

### Part 16 (optional) — Alpha-Beta Pruning Is Only as Good as Its Move Ordering

- **Slug:** alpha-beta-pruning-move-ordering
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** why does alpha-beta save nothing under bad move ordering, yet cut the tree to roughly
  its square root under perfect ordering? And how do game engines prepay that ordering?
- **Assumes:** Part 1's sentence that a probe eliminates many candidates only when a prepaid
  structure connects them, the `#intuition` anchor. Restates the bound-elimination wording owned by
  Part 13. Trees and recursion; teaches minimax itself.
- **Hands off:** Monte Carlo tree search appears only as the contrast, the place where the frame
  breaks: it allocates probes by statistics and never eliminates anything. Transposition tables
  appear as a lookup step, not as hashing explained.
- **Worked example:** a depth-3, branching-3 tree with 27 concrete leaf values.
  - Minimax evaluates 27.
  - Alpha-beta under the worst ordering still evaluates 27. Under perfect ordering it evaluates
    11 = 3² + 3¹ − 1, the Knuth–Moore minimal tree, with the same root value.
  - At Shannon's "of the order of 30" legal moves and depth 8, that is 30⁸ ≈ 6.56 × 10¹¹ leaves
    against 2·30⁴ − 1 ≈ 1.62 × 10⁶. The often-quoted b ≈ 35 is not Shannon's figure; cite a later
    source if it is used.
- **Key sources:** Knuth & Moore, "An Analysis of Alpha-Beta Pruning", *AI* 6(4), 1975; Shannon,
  "Programming a Computer for Playing Chess", *Phil. Mag.* Ser. 7, 41(314), 1950; Schaeffer, "The
  History Heuristic and Alpha-Beta Search Enhancements in Practice", *TPAMI* 11(11):1203–1212, 1989;
  Kocsis & Szepesvári, ECML 2006 (contrast only).
- **Search intent:** "alpha beta pruning explained", "move ordering alpha beta", "alpha beta best
  case complexity", "transposition table"

### Part 17 (optional) — How a Search Engine Skips Documents: MaxScore and WAND

- **Slug:** maxscore-and-wand-top-k-retrieval
- **Tier:** L3 · **Difficulty:** advanced · **Est. words:** 6,000 · **Figures:** 9
- **Answers:** after the term lookup, which the hub calls the absence of a search, how does a search
  engine avoid scoring every matching document? And when do the bounds stop pruning?
- **Assumes:** Part 1's `#limitations-and-common-mistakes`: hashing is the absence of a search, and
  here the real search starts after the lookup. Assumes an inverted index exists and does not teach
  its construction. BM25 at the level of "a sum of per-term scores". Restates Part 13's
  bound-elimination wording.
- **Hands off:** dense retrieval goes to Parts 14–15. Learned sparse retrieval, reranking and hybrid
  ranking are out of scope.
- **Worked example:** the hub's 16 integers as the posting list for *search* (score 1.0 each).
  *binary* appears in {9, 61, 97} (max 3.0) and *tree* in {14, 42, 61, 85} (max 2.5).
  - Exhaustive OR evaluation scores all 16 documents to find the top-1, document 61 at 6.5.
  - MaxScore fully scores only 3 (documents 3, 9 and 61). As the threshold rises to 1.0, 4.0 and
    6.5, whole lists lose the ability to lift a document above it.
  - Galloping intersection, restated in two sentences: double the stride from the current posting
    until it overshoots, then binary-search the bracket. A see-also goes to Part 3's exponential
    search.
  - Why WAND does not always beat MaxScore.
- **Key sources:** Turtle & Flood, "Query Evaluation: Strategies and Optimizations", *IP&M* 31(6),
  1995; Broder et al., "Efficient Query Evaluation Using a Two-Level Retrieval Process", CIKM 2003;
  Ding & Suel, "Faster Top-k Document Retrieval Using Block-Max Indexes", SIGIR 2011; Grand, Muir,
  Ferenczi & Lin, "From MAXSCORE to Block-Max Wand: The Story of How Lucene Significantly Improved
  Query Evaluation Performance", ECIR 2020.
- **Search intent:** "WAND algorithm explained", "MaxScore top-k retrieval", "block-max WAND", "how
  do search engines find top results fast"

### Part 18 (optional) — When Eliminate Is a Guess: Beam Search, IDA\* and Bounded Frontiers

- **Slug:** beam-search-ida-star-bounded-frontiers
- **Tier:** L2 · **Difficulty:** intermediate · **Est. words:** 4,500 · **Figures:** 7
- **Answers:** what happens when you cannot afford to store the frontier? How do IDA\* and beam
  search choose what to forget, what does each pay, and why can a wider beam give a worse answer?
- **Assumes:** Part 1's `pick` parameter and `astar()` code, the `#implementation` anchor. The hub
  never explores what the frontier costs in memory. Recursion, priority queues. Restates the grid.
- **Hands off:** efSearch as a beam width inside vector indexes is owned by Part 14; this part adds
  a cross-link if Part 14 is published. Optimisation metaheuristics are out of scope; hill climbing
  appears as beam width 1 in one paragraph. This part owns iterative deepening.
- **Worked example:** the hub's grid. *(planning)*
  - A\* expands 33 cells with a frontier that may hold every open cell.
  - IDA\* finds the cost-11 path in 3 iterations (f-bounds 7, 9, 11) and 62 expansions. That is 88%
    more work, for memory proportional to path depth.
  - A beam of width 1 walks into the wall and fails. Width 2 finds cost 11 in 22 expansions, and
    width 8 in 54.
  - Then a small decoding lattice where widening the beam returns a worse output.
- **Key sources:** Korf, "Depth-First Iterative-Deepening: An Optimal Admissible Tree Search",
  *AI* 27(1), 1985; Holtzman et al., "The Curious Case of Neural Text Degeneration", ICLR 2020;
  Meister, Cotterell & Vieira, "If Beam Search Is the Answer, What Was the Question?", EMNLP 2020;
  Stahlberg & Byrne, "On NMT Search Errors and Model Errors: Cat Got Your Tongue?", EMNLP-IJCNLP
  2019.
- **Search intent:** "beam search explained", "IDA\* explained", "beam width tradeoff", "why does
  larger beam give worse results"

## Publication order and cadence

`series_position` follows the numbering above, and that is also the reading order in the series
index. It is grouped by the hub's own section order: ordering (3–5), precomputation (6–8),
heuristic (9–12), geometry (13–15). Part 2 sits first because it computes the hub's central claim.
The optional wave comes last, and every handoff into it has a stated fallback, so dropping it leaves
no gaps.

Publication order is free, apart from three hard constraints:

- **4 after 3.**
- **15 after 14.**
- **16 and 17 after 13**, because they restate its final bound-elimination wording.

Recommended order, alternating search demand with how directly the hub points at each topic:

1. **Part 3.** Highest student demand, beginner, a counting-only lab.
2. **Part 14.** Strongest working-engineer demand.
3. **Part 6.** The spoke the hub's own outline planned.
4. **Parts 9, 11 and 2**, in that order.
5. **The advanced, lab-heavy parts:** 4, 13, 15, 7, 8, 12, 10, 5.
6. **The optional wave**, if approved, after Part 13.

Cadence: one L2 a week and one L3 every two weeks. These are 6,000-word posts with ten figures, and
a weekly L3 cadence will not survive the figure budget.

## Cross-links

Every spoke links back to exactly one prior part as its dependency, using that part's canonical URL
plus a GitHub-style heading anchor and never a local path:

- **Parts 4 and 15 excepted, every spoke** links to the hub:
  `https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm#<anchor>`.
- **Part 4** links to
  `https://canery.in/blogs/why-your-binary-search-is-off-by-one#the-fixed-trip-boundary-form`.
- **Part 15** links to
  `https://canery.in/blogs/tuning-hnsw-recall-throughput-cost#measuring-an-ann-index-honestly`.

A spoke may add "see also" links, but only to parts that are already published, and never forward
to an unpublished one. Where a part would like a see-also to a sibling that the recommended order
publishes later (Part 14 to 13, Part 10 to 9, Part 18 to 14), it restates the one fact it needs
instead.

The hub is **not reopened** to add forward links. It names no spokes, so readers find them through
the series index.

## The lab policy

Unlike the image-processing series, this series **executes code**. The hub already measured its
Figure 5 counts.

- **Counts over timings.** The series' currency is probes, eliminations, character comparisons,
  expansions and distance checks. Those are deterministic and reproducible from a lab script, and
  they carry most parts. Any count that depends on a convention (tie-break, goal test, midpoint,
  whether a comparison result is reused) is printed with its convention.
- **Timings only where the machine is the subject:** Parts 4, 7, 14 and 15. Every timing ships with
  the CPU model, compiler or interpreter version, and an invitation to rerun.
- **Language:** Part 4's lab is C, because Python's interpreter overhead hides every cache effect
  (gcc is on this machine). Everything else is Python.
- **Dependencies:** numpy, hnswlib and faiss-cpu are not installed. Parts 13–15 install them into a
  venv, CPU only.
- **Data:** ANN parts use a small real dataset with a verified licence, because random Gaussian
  vectors are a worst case that misstates recall.
- **Format:** each lab follows blog-forge's `references/labs.md` format and needs no GPU.

## Open decisions for the user

1. **Move the hub into this folder?** The image-processing and NVIDIA series moved their published
   members in; the diffusion series left one out until asked. Moving it means `assets/_social.py`
   must change `ROOT = HERE.parents[2]` to `parents[3]`, and the `fill_urls.py` path in its
   `manifest.md` changes. `posts/` is gitignored, so copy, verify, then delete. Not done.
2. **Add `series: search-algorithms` / `series_position: 1` to the hub?** That is a re-publish of a
   live post. The hub also fails the current validator on five missing frontmatter fields (date,
   category, tier, difficulty, reading_minutes), which that re-publish would have to fix. Not done.
3. **Commit the optional wave (16–18)?** It is new ground beyond the hub's four families and strong
   in search demand. Dropping it costs nothing in public, and every handoff into it has a fallback.
4. **Adjacent cuts**, each a one-word overrule:
   - **tight (7 parts):** 1, 2, 4 (absorbing 3's correctness harness), 6, 9, 11 and 14 (absorbing
     13's opening). Strictly what the hub touched.
   - **merge 9 + 11:** into one L3 graph-search part of about 7,500 words.
   - **merge 14 + 15:** into one L4 vector-index part of about 8,500 words.
5. **Category:** the hub uses `algorithms`. Proposed for every part; settle once.

## What this series will not cover

- **Hash-table internals and hash-function design.** This is the hub's own boundary ("the absence
  of a search"). Hashing appears only in six places:
  - Part 2's decision, and its breaking input (hash flooding, as collision cost only);
  - Part 5's limit case;
  - Part 6's one Rabin–Karp paragraph (a fingerprint as a cheaper probe);
  - Part 15's LSH section (hash buckets as a prepaid candidate set, the one sanctioned use of
    hashing inside the frame);
  - Part 16's transposition tables, as a lookup step;
  - Part 17's term lookup.
- **Disk-resident, write-optimised storage structures:** B-tree page splits and page layout, LSM
  trees, compaction, and the RUM trade-off as applied to storage engines. Part 4's static, read-only
  in-memory B-tree and S-tree nodes are in scope, and Part 2 owns what inserts cost an in-memory
  balanced tree.
- **Optimisation metaheuristics** (simulated annealing, genetic algorithms), beyond one paragraph in
  Part 18.
- **SAT, SMT and constraint solving.**
- **Monte Carlo tree search and RL planning**, beyond Part 16's contrast.
- **GPU-accelerated search** (there is no local GPU) and distributed or sharded search.
- **Retrieval pipelines:** learned rerankers (cross-encoders), embedding models, RAG, hybrid
  lexical-plus-vector ranking, learned sparse retrieval, and vector-database operations. Part 15's
  exact-distance re-scoring of PQ candidates is in scope.
- **Routing variants:** time-dependent, multimodal, transit and live-traffic routing.
- **Regex syntax and DFA minimisation; compression beyond the BWT; word-level inverted index
  construction.**
- **Quantum search.**
- **Introductory tutorials** for binary search, BFS/DFS or KMP on their own.
- **If the optional wave is dropped:** memory-bounded frontiers (iterative deepening, IDA\*, beam
  search), game-tree search, and top-k document retrieval.
