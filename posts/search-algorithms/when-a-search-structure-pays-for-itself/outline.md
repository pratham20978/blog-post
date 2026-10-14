# Outline — When a Search Structure Pays for Itself

**Title:** Hash Map, Sorted Array or Tree? When Each Pays for Itself (57 chars). The plan's working
title, *Hash Map, Sorted Array or Tree? When a Search Structure Pays for Itself*, is 70 characters;
the front half, which carries the search phrases, is kept unchanged.
**Slug:** `when-a-search-structure-pays-for-itself` (the plan's)
**Series:** `search-algorithms`, part 2 · **Tier:** L2 standard · **Category:** algorithms ·
**Difficulty:** intermediate (big-O, a hash function, and Part 1's prepaid-structure idea; no proof
is assumed) · **Lab grade:** G1 — runs anywhere (one Python file, standard library only)
**Budget:** about 4,600 words as the validator counts them (L2 range 3,000–5,000, references
included) · **Figures:** 6 (L2 range 5–8; the plan estimated 6)
**Assumes:** Part 1, *Every Search Algorithm Is the Same Algorithm* (published): the frame and the
`#intuition` argument that a structure is a fixed cost amortised over queries, which Part 1 states
and never computes. Named in plain text; the owner adds the link.
**Hands off:** per-probe speed inside a sorted array (layout, branches, cache) and probing fewer
than log₂ n times go to "a later part of this series" with no number or title. Hash-table internals
are out of scope: flooding appears only as collision cost; PEP 456 is cited for the fix and SipHash
is named, not explained. B-tree pages and LSM trees are out of scope; the RUM conjecture is named
as the general form of the trade-off.

**Checkpoints.** As with the other series built this autumn, the session ran without a stop at A
and B; what each would have shown is recorded here.
**A:** 17 sources, 6 peer-reviewed with identifiers (floor 4): Stober & Weiß (ALENEX 2023),
Flajolet & Golin (Acta Inf. 1994), Crosby & Wallach (USENIX Security 2003), Tarjan (SIAM J. Alg.
Disc. Meth. 1985), Guibas & Sedgewick (FOCS 1978), Athanassoulis et al. (EDBT 2016); plus PEP 456,
JEP 180, the oCERT advisory, Python and Java docs, and CPython and OpenJDK source at release tags.
Five databases queried (OpenAlex, Crossref, Google Scholar answered; DBLP and Semantic Scholar
blocked), 23 searches, 34 claims. Not read: Ford & Johnson 1959 and Knuth's TAOCP (both cited
through Stober & Weiß). No paper figure is reusable (CC BY-NC-ND; USENIX non-commercial only).
**B:** this file.

**Five findings change what the plan expected.**
1. *The information floor of 45 is unreachable.* Stober & Weiß proved in 2023 that 16 keys need
   46 comparisons in the worst case, disproving Knuth's conjecture of 45; merge insertion reaches
   46. Merge sort's worst case is 49, its exact mean over all 16! orders 2056/45 = 45.69.
2. *The break-even grows only as 2 log₂ n − 2.* Sorting pays back after 9.56 successful lookups at
   16 keys (ahead from the 10th) and 38.00 at 2²⁰; misses pay back after log₂ n − 1 (4.12 at 16,
   19.00 at 2²⁰). The sort costs about log₂ n scans' worth of comparisons and each lookup saves
   half a scan.
3. *Inserting 50 into TreeMap needs no rebalancing at all.* 5 comparisons, one red leaf under a
   black parent, 0 rotations, 0 flips, against the array's 4 comparisons and 8 shifts. The price of
   balance shows over the whole build instead: 60 comparisons, 10 rotations and 9 colour flips for
   16 ascending inserts. The same keys in an unbalanced BST make a 16-deep chain in which finding
   61 costs 10 comparisons: Part 1's linear scan, exactly.
4. *CPython's flood count is 128, not the plan's 120.* The one-list model costs 0 + 1 + … + 15 =
   120; CPython's probe sequence returns to the first key's slot on its fourth step while the table
   is small, so inserts 4–11 pay one extra each. The lab replays the probe sequence from the
   v3.14.0 constants and matches CPython at 16, 64, 256 and 1,024 keys.
5. *"No hash can answer largest ≤ 60" is too strong.* For small integer keys a hash set can probe
   60, 59, …, 53 (8 lookups) or the 31 integers of the range [40, 70]; for strings or floats it
   cannot. The article says exactly that.

---

## The spine

A search structure is a bill paid in three parts: a build, a charge on every write, and a list of
questions it can no longer answer. The scan pays nothing and gets one elimination per comparison.
Sorting buys a better exchange rate with a build of about n log₂ n comparisons and earns it back
after about 2 log₂ n − 2 successful lookups, which is why the break-even is small and grows slowly;
inserts then cost the sorted array n/2 shifts each, so it loses once writes reach half the work. A
balanced tree trades a little lookup speed and memory for writes that touch one path, and loses to
a plain scan only when writes outnumber reads by about n/(2 log₂ n) to one. A hash map skips the
search for exact keys and cannot answer anything else, and keys chosen to collide turn it back into
the list it replaced.

## Verified numbers (all from `lab/pays_for_itself.py`, captures.json)

**Lookups (16 keys):** scan hit mean 8.5, miss 16. Closed-interval binary search (Part 1's prose
procedure) hit mean 3.375 = 54/16, max 5; miss mean 70/17 = 4.118, max 5; 61 probes 47, 74, 61.
**Sort:** merge sort worst 49, order 3 53 28 79 14 68 42 91 9 61 35 85 21 74 47 97; exact mean
2056/45 = 45.69; 20,000 seeded orders mean 45.70, range 37–49; floor ⌈log₂ 16!⌉ = 45 (log₂ 16! =
44.25); best possible 46 (cited).
**Break-even (hits):** 49/(8.5 − 3.375) = 9.56 → 10th lookup; mean sort 8.91 → 9th; 46 → 8.98 →
9th. **(misses):** 49/(16 − 4.118) = 4.12 → 5th; mean 3.85 → 4th.
**Sorted array insert 50:** slot 8, 4 comparisons, 8 shifts (53 … 97); mean shifts over the 17
gaps 8.0; mean lower_bound 4.118.
**TreeMap, ascending inserts:** build 60 comparisons (one is the first put's self-check), 10
rotations, 9 flips; height 6; root 21, find 61 = 4 (21, 47, 74, 61); hit mean 59/16 = 3.69, max 6;
miss mean 75/17 = 4.41; insert 50 = 5 comparisons (21, 47, 74, 61, 53), 0 rotations, 0 flips;
floorKey(60) = 53 in 5; subMap(40, 70) = 42 47 53 61 68 in 11.
**Plain BST, ascending:** build 120, height 16, find 61 = 10.
**Ordered queries on the array:** range [40, 70] = 8 comparisons + 5 reads; scan 16 visits (26
comparisons); integer probing 31. Largest ≤ 60 = 53 in 4; integer probing 8; nearest to 60 = 61.
**Scale (q\* hits / misses):** 16: 9.56/4.12 · 64: 11.73/5.54 · 256: 14.76/7.23 · 1,024:
18.31/9.09 · 4,096: 22.11/11.03 · 16,384: 26.04/13.01 · 65,536: 30.01/15.00 · 2¹⁸: 34.00/17.00 ·
2²⁰: 38.00/19.00. Exercise E3: 2²⁴ → 46.00.
**Writes (writes per read at break-even, write price 1 / 0.1):** array 16: 0.42/1.04 · 64:
0.72/2.97 · 256: 0.89/5.84 · 1,024: 0.96/8.23 · 4,096: 0.99/9.40 · 16,384: 1.00/9.82 · 65,536:
1.00/9.95. TreeMap 16: 0.9/1.1 · 64: 3.3/4.0 · 256: 11.6/13.9 · 1,024: 40.3/47.0 · 4,096:
140.6/160.4 · 16,384: 495.8/556.4 · 65,536: 1,770.5/1,961.2. Rotations and flips per insert → 1.00
each at large n for ascending inserts. Exercise E3: price 0.25 at 65,536 → 3.99.
**Flood (CPython 3.14.4 dict):** colliding inserts 0 1 2 4 5 6 7 8 9 10 11 11 12 13 14 15 = 128;
model 120; spread 0. Lookup of 97: 16 against 1; absent: 16 against 0. 64 → 2,069 (2,016); 256 →
32,885 (32,640); 1,024 → 524,600 (523,776). `hash(61)` = 61; str and bytes use siphash13.

## Sections and budget

| Section | Target | Figures |
|---|---|---|
| Insights + who + series line | 170 | — |
| Why this matters | 110 | — |
| The problem | 260 | — |
| Worked example: lookups, the sort, the break-even | 620 | FIG_01 |
| Intuition: a pass you buy before the rides | 280 | — |
| How many writes can a sorted structure absorb? | 560 | FIG_02, FIG_03 |
| Which questions can a hash map not answer? | 380 | FIG_04 |
| What input breaks a hash map? | 400 | FIG_05 |
| The math | 380 | FIG_06 |
| Implementation | 230 | — |
| Limitations and common mistakes | 250 | — |
| Key takeaways | 110 | — |
| Try it yourself (E1–E3, short) | 200 | — |
| References and lab downloads | ~550 | — |

## Figure plan (route gate run per figure)

| # | Section | One thing it says | Route | Why |
|---|---|---|---|---|
| 01 | Worked example | cumulative comparisons for q lookups: the scan's line starts at 0 and climbs 8.5 a lookup; sort-then-search starts at 49 and climbs 3.375; they cross at 9.56 | chart | Q1 — counted lab data at q = 0…20, with the mean-sort line at 45.69 |
| 02 | Writes | inserting 50: the array moves 8 keys; the red-black tree walks one 5-node path and adds a red leaf; the unbalanced tree is a 16-deep chain | placed | Q4 — real slots and the real TreeMap shape and colours, small multiples |
| 03 | Writes | writes per read at break-even against n: the array stays near 1 (near 10 if a write costs a tenth), the tree climbs past 1,700 | chart | Q1 — lab rows at seven sizes and two write prices, log axes |
| 04 | Hash map | the range [40, 70] and the floor of 60 on the sorted array are two boundary searches over one contiguous run; the same keys in 16 hash buckets are scattered, so a range must visit every bucket | placed | Q4 — real array slots and a labelled model table (bucket = key mod 16) |
| 05 | Flooding | cumulative key comparisons while inserting 16 keys: 0 with spread hashes, 120 for one list, 128 in CPython | chart | Q1 — counted `__eq__` calls from the lab |
| 06 | The math | the break-even lookup count from 16 keys to 2²⁰: hits 9.56 → 38.00 along 2 log₂ n − 2, misses along log₂ n − 1 | chart | Q1 — exact counts per size (direct to 4,096, the verified recursion beyond) with the model line labelled as a model |

## Term map

| Term | First section | What | Why | When |
|---|---|---|---|---|
| comparison (the unit) | The problem | one call to the key-compare function, whatever it returns | one currency for every structure | reading any count here |
| build cost; per-write cost; lookup cost | The problem | the three parts of a structure's price | what the scan avoids | choosing |
| amortised | The problem | cost averaged over a worst-case sequence (Tarjan) | spreading a build over queries | build-once workloads |
| break-even lookup count q\* | Worked example | lookups after which build + lookups beat scanning | the decision number | before sorting or indexing |
| merge sort; information floor ⌈log₂ n!⌉; S(n) | Worked example | a comparison sort; the fewest comparisons any sort can need; the true minimum | the build price and its limit | sorting |
| shift; write share; writes per read | Writes | moving one element; fraction of operations that insert | the array's maintenance price | mixed workloads |
| balanced BST; red-black tree; rotation; colour flip | Writes | a tree kept shallow by colour rules; the two repair steps | writes that touch one path | ordered data with writes |
| `TreeMap`, `HashMap`, `dict`, `bisect`/`insort` | Writes / hash map | the library structures | what readers actually call | code review |
| RUM conjecture | Writes | read, update, memory: bound two and the third pays | the general trade-off | any index design |
| point query; range query; predecessor (floor); nearest; ordered iteration | Hash map | the query types | which need order | workload analysis |
| hash function; bucket; collision; open addressing | Hash map | key to slot; the slot; two keys in one slot; probing other slots | how a hash skips the search | point lookups |
| hash flooding (algorithmic complexity attack) | Breaks | chosen keys that all collide | the input that breaks hashing | untrusted keys |
| keyed hash; hash randomisation; SipHash (named only) | Breaks | a hash with a secret seed | the fix | servers, parsers |
| tree bins (JEP 180) | Breaks | a crowded bucket turned into a red-black tree | Java's other fix | Java maps |

## Not repeated from Part 1

The frame (frontier, probe, eliminate) gets one sentence; the 16-integer trace gets three; the
log₂ n decision-tree bound is referred to, not re-derived; the overflow bug and Eytzinger layouts are
not mentioned; "hashing is the absence of a search" is paraphrased once, as the point this part
prices.
