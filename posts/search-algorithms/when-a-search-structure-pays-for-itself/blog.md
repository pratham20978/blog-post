---
title: "Hash Map, Sorted Array or Tree? When Each Pays for Itself"
slug: when-a-search-structure-pays-for-itself
date: 2026-10-14
updated: 2026-10-14
summary: "Sorting 16 keys pays for itself by the 10th lookup, a million keys after about 38. Then writes, query types and colliding keys pick array, tree or hash map."
tags: [algorithms, binary-search, hash-table, red-black-tree, sorting, performance]
category: algorithms
categories: [algorithms]
tier: L2
difficulty: intermediate
series: search-algorithms
series_position: 2
prerequisites: ["big-O notation", "what a hash function does", "part 1 of this series, for the idea that a search structure is paid for in advance"]
reading_minutes: 21
cover_image_url: "COVER"
cover_image_alt: "Title card: a steep scan line and a flatter sort-then-search line cross at one tangerine point, above a row of the 16 sorted keys"
canonical_url: "https://canery.in/blogs/when-a-search-structure-pays-for-itself"
---

> [!NOTE]
> **Insights** — Sorting 16 keys costs at most 49 comparisons and saves about 5 on every successful lookup, so it has paid for itself by the 10th lookup; a million keys pay it back after about 38. Writes decide what comes next: a sorted array shifts half its keys per insert and loses to plain appending once writes reach about half the work, while a red-black tree such as Java's `TreeMap` keeps winning until writes outnumber reads by about 1,770 to one at 65,536 keys. A hash map skips the search for exact keys but cannot answer a range or "largest key below x" query, and keys that all collide turn it back into a list.

**Level:** intermediate · **You need:** big-O notation, what a hash function does, and the idea from part 1 of this series that a search structure is paid for in advance · **Time:** ~21 min

This is part 2 of *Search Algorithms: The Price of the Skip*. Part 1, *Every Search Algorithm Is the Same Algorithm*, argued in its Intuition section that every search structure is a cost paid up front and spread over the queries that use it, and that the complete question is how many queries it takes to pay for itself. It never worked out the number. This part does, on Part 1's own 16 keys.

**Jump to:** [The problem](#the-problem) · [Worked example](#worked-example) · [Intuition](#intuition) · [Writes](#how-many-writes-can-a-sorted-structure-absorb) · [Query types](#which-questions-can-a-hash-map-not-answer) · [Flooding](#what-input-breaks-a-hash-map) · [The math](#the-math) · [Implementation](#implementation) · [Limitations](#limitations-and-common-mistakes)

## Why this matters

You have 2,000 customer IDs in a list and a loop that checks 300 incoming IDs against it. Do you sort the list first, load it into a set, or leave it alone? Or a code review asks why a map is a `HashMap` and not a `TreeMap`. The usual answer quotes O(1), O(log n) and O(n). None of those says how many lookups a sort must serve before it is paid for, what each insert costs afterwards, or which questions the structure can no longer answer. Those three numbers decide the choice.

## The problem

You hold n keys and expect a workload: q lookups, w inserts, and perhaps a few questions about order, such as "which keys lie between 40 and 70?". Four candidates are on the table:

1. Leave the keys unsorted, append new ones at the end, and scan.
2. Sort once, binary-search, and keep the array sorted on every insert.
3. A balanced binary search tree, such as Java's `TreeMap`.
4. A hash table, such as Java's `HashMap` or Python's `dict`.

Each one's price has three parts: a **build cost** paid once, a **cost per write**, and a **cost per lookup**. To compare them, this post counts in one unit. A **comparison** is one call to the function that compares two keys, whatever it returns; Java's `compareTo` and Python's `==` are both one comparison. A **shift** moves one array element one slot. Counts are not timings, and the post returns to that difference under Limitations.

The build is **amortised** over the lookups it serves: its cost is averaged over the whole sequence of operations, as in Tarjan's definition of amortised cost as the average over a worst-case sequence. <!-- L07 --> That is the sense of Part 1's claim, and it is what makes "is sorting worth it?" a question about q, not about big-O.

What makes the choice hard is that the four bills are written in different currencies. The scan pays per lookup. Sorting pays up front and then per insert, in shifts. The tree pays in memory and in a little lookup speed. The hash table pays in questions it cannot answer and in inputs that break it. Big-O shows one line of each bill.

The keys are Part 1's: `3 9 14 21 28 35 42 47 53 61 68 74 79 85 91 97`.

## Worked example

Part 1 searched these 16 sorted keys for 61, which sits at index 9. A linear scan tests index 0, 1, 2 and so on, and finds it on the tenth probe. Binary search on the closed interval tests the middle key, 47, then the middle of what is left, 74, then 61: three probes, 3.375 on average over the 16 keys, and never more than 5.

Now drop the assumption that the keys arrive sorted, and price each step.

**The scan.** A lookup that succeeds tests (16 + 1)/2 = 8.5 keys on average, whatever the order, because the wanted key is equally likely to sit in each of the 16 positions. A lookup that fails tests all 16.

**The sort.** Merge sort splits the keys in halves, sorts each half, and merges them. A merge of two sorted runs costs one comparison per key it places, until one run is empty. <!-- L06 --> For 16 keys the worst case is 49 comparisons, and some orders force it; the lab builds one, `3 53 28 79 14 68 42 91 9 61 35 85 21 74 47 97`. <!-- L05 --> Averaged over all 16! orders, merge sort needs exactly 2056/45 ≈ 45.69.

No comparison sort can do better than ⌈log₂ 16!⌉ = 45 in the worst case. There are 16! possible orders, and each comparison can at best halve the ones still possible. <!-- L02 --> Even 45 is out of reach. Florian Stober and Armin Weiß proved in 2023, by exhaustive computer search, that 16 keys need 46 comparisons. <!-- L01 --> That settled a conjecture of Knuth's that 45 would do. <!-- L03 --> Ford and Johnson's merge insertion, from 1959, reaches 46. <!-- L04 -->

**The break-even.** Sorting costs 49 up front and then saves 8.5 − 3.375 = 5.125 comparisons on every successful lookup.

| Lookups q | Scan: 8.5 q | Sort, then search: 49 + 3.375 q |
|---:|---:|---:|
| 0 | 0 | 49 |
| 5 | 42.5 | 65.9 |
| 9 | 76.5 | 79.4 |
| 10 | 85 | 82.75 |
| 20 | 170 | 116.5 |

The two totals cross at 49 / 5.125 = 9.56 lookups, so sorting is ahead from the 10th lookup on. Figure 1 draws both lines.

![Cumulative comparisons over 20 lookups: the scan line rises 8.5 a lookup, sort-then-search starts at 49 and rises 3.375, crossing at 9.56](FIG_01)

*Figure 1 — Two bills for the same lookups. The sort is a fixed charge of 49; after it, each lookup costs 3.375 instead of 8.5, and the lines cross at 9.56. The dashed line uses merge sort's mean, 45.69, and crosses at 8.91.*

That 10 sets a worst-case sort against average lookups, which is the cautious way round. With merge sort's mean of 45.69, sorting is ahead from the 9th lookup, and so is the best possible sort, at 46. Lookups that miss move the crossing much earlier: a failed scan costs 16 and a failed binary search 4.12 on average, so a worst-case sort is repaid after 49 / 11.88 = 4.12 misses.

## Intuition

Sorting works like a monthly travel pass. You pay once, each ride then costs less than a single ticket, and the pass pays for itself after a fixed number of rides. The analogy breaks on writes. A pass does not cost more each time the network opens a station, but a sorted array charges again on every insert, in shifts, and its charge grows with n.

The break-even is small, and it grows slowly, because of what each side costs in scans. A merge sort of n keys makes about n log₂ n comparisons, which is the price of about log₂ n passes over the data. A lookup on the sorted array saves about half a pass, n/2 comparisons, against scanning. So the number of lookups that repays the sort grows like 2 log₂ n, not like n: 9.56 at 16 keys, 38.00 at a million. The math section derives the exact form.

A hash table does something else. It does not buy a better rate of eliminations per probe. It computes from the key where that key must be, so a lookup tests about one key. Part 1 called that the absence of a search. Its bill is paid in two other currencies. Order is thrown away, so any question about order is refused, and its speed depends on keys spreading evenly over the table, which someone choosing the keys can prevent.

## How many writes can a sorted structure absorb?

### The sorted array pays in shifts

Insert 50. Binary search finds its slot, index 8, in 4 comparisons. Then the eight keys after it, 53 through 97, each move one slot right. An insert at a random position shifts n/2 keys on average. Python's documentation says the same of `bisect.insort`: the O(log n) search is dominated by the O(n) insertion step. <!-- L29 -->

So a sorted array is worth keeping only while the lookups it speeds up outnumber the inserts it slows down. Price a shift like a comparison, and compare it with appending at the end and scanning. At 16 keys, keeping the array sorted wins only while fewer than 29.7% of operations are writes, 0.42 writes per read. As n grows that share rises to 50%: one write per read, because each insert now costs about n/2 shifts and each lookup saves about n/2 comparisons. If moving a key costs a tenth of a comparison, the array can absorb close to 10 writes per read at 65,536 keys.

### The tree pays in nodes

`TreeMap` is a **red-black tree**: a binary search tree that keeps itself shallow with one colour bit per node. <!-- L24 --> Every path from a node down to an empty link passes the same number of black nodes, and no red node has a red child; Leo Guibas and Robert Sedgewick framed these rules in 1978. <!-- L10 --> <!-- L11 --> Together the rules keep the longest path at most twice the shortest, so the height stays within 2 log₂(n + 1).

Insert the 16 keys in ascending order and `TreeMap` builds the tree in Figure 2, of height 6, in 60 comparisons. One of them is its first `put` comparing the key with itself as a type check. <!-- L26 --> Along the way it made 10 **rotations**, which swap a parent and child to shorten a path, and 9 **colour flips**, which recolour three nodes and move a violation two levels up. An insert repairs the tree with flips that may climb, then at most one single or double rotation, <!-- L08 --> and a run of inserts costs O(1) of that repair each, amortised. <!-- L09 --> At 65,536 ascending keys the lab counted one rotation and one flip per insert.

Now insert 50: it is compared with 21, 47, 74, 61 and 53, and becomes a red leaf under black 53. Five comparisons, no rotation, no flip, no shift.

![Inserting 50: eight array keys shift right; the red-black tree adds a red leaf via 21, 47, 74, 61, 53; unbalanced, the keys form a chain](FIG_02)

*Figure 2 — One insert, three structures. The array moves 8 keys. The red-black tree touches one five-node path and moves nothing. The same keys inserted in order with no balancing make a chain 16 deep, in which finding 61 takes 10 comparisons.*

The tree pays elsewhere. A lookup costs a little more than binary search, 3.69 comparisons on average against 3.375, and 15.5 against 15.0 at 65,536 keys. Every entry carries five references and a colour bit. <!-- L25 --> In return, it loses to plain appending only when writes outnumber reads by about 0.9 to one at 16 keys, 40 at 1,024 and 1,770 at 65,536, as Figure 3 shows.

![Writes per read at break-even by key count: the sorted array stays near 1, or 10 with cheap writes; the red-black tree climbs to 1,770](FIG_03)

*Figure 3 — How many writes per read each sorted structure can absorb before plain appending wins. The array's limit stays flat; the tree's grows with n. Solid lines price a write as one comparison, dashed as a tenth of one; every count behind them is the lab's.*

Drop the balancing rules and the price comes back as a list. The same ascending keys, inserted into a plain binary search tree, each become the right child of the one before, a chain 16 deep. Building it costs 0 + 1 + … + 15 = 120 comparisons, and finding 61 costs 10: Part 1's linear scan again. Crosby and Wallach list sorted input as exactly the case that turns an unbalanced tree into a list. <!-- L12 -->

The general form of this trade-off has a name. The **RUM conjecture** says an access method that bounds two of read cost, update cost and memory must pay a lower bound on the third. <!-- L32 --> The sorted array is lean and fast to read, so updates pay. The tree bounds reads and updates, so memory pays. Appending and scanning bounds updates and memory, so reads pay.

## Which questions can a hash map not answer?

A **hash function** turns a key into a slot number, and the table looks only there, plus any slots its collisions spilled into. For exact keys this skips the search entirely. CPython's `dict` inserted the 16 keys without a single key comparison, because it compares the stored hashes first and calls `==` only when two hashes are equal. <!-- L30 --> Looking up 97 took one comparison, the match itself. Java's `HashMap` promises constant time for `get` and `put` only on condition that the hash spreads the keys, and promises no order at all. <!-- L23 -->

Order is what a hash table gives up, and many questions need it:

| Query on the 16 keys | Sorted array | `TreeMap` | Hash table |
|---|---|---|---|
| Is 61 there? | 3 comparisons | 4 | 1, after hashing |
| Every key from 40 to 70 | 8 comparisons, then read 5 | 11, then step through 5 | look at all 16; for integers only, probe all 31 values |
| Largest key ≤ 60 | 4 → 53 | 5, `floorKey` | integers only: probe 60, 59, …, 53, 8 lookups |
| Keys in order | read the array | walk the tree | sort them first |

In the sorted array every key from 40 to 70 sits in one contiguous run. Two boundary searches find its ends: the first key ≥ 40 and the first key greater than 70. `TreeMap` does the same with descents from the root, then walks to each next entry without comparing. <!-- L28 --> The nearest key to 60 is one of the two keys either side of it, 53 or 61, so it falls out of the same search. A hash table scatters the run across its slots, as Figure 4 shows, so a range must visit every key. The RUM paper's comparison makes the same split: hash indexes give the fastest point lookups, and B+-trees the fastest ranges. <!-- L33 -->

![Sorted array: two searches bracket 42 to 68 and the floor of 60 is 53; in 16 hash buckets the same five keys sit in scattered buckets](FIG_04)

*Figure 4 — Order keeps a range in one piece. In the array, [40, 70] is five neighbours found by two searches. In a hash table, here a model with bucket = key mod 16, the same five keys land in five unrelated buckets.*

The decision rule follows. If every query names an exact key, do not search at all: hash. If any query asks about order, keep the order, in a sorted array when writes are rare and in a tree when they are not.

## What input breaks a hash map?

Programmers choose hash tables for constant expected time, but one operation can still cost O(n) in the worst case. <!-- L13 --> The worst case is a **collision** on every key: all keys share one hash value, so each new key must be compared with every key already stored. In a table that keeps one list per bucket, 16 such keys cost 0 + 1 + … + 15 = 120 comparisons, and n keys cost n(n − 1)/2.

The lab measured it in CPython 3.14's own `dict`, with a key type whose hash is one constant. The 16 inserts took 128 comparisons, and the spread keys took none (Figure 5). CPython probes other slots of one array rather than keeping lists, and its probe sequence returns to the first key's slot on its fourth step while the table is small. So inserts 4 to 11 each compared that key twice. <!-- L31 --> Looking up 97 took 16 comparisons instead of 1. At 1,024 keys the inserts took 524,600.

![Cumulative key comparisons for 16 keys sharing one hash: 128 in CPython's dict, 120 for one list, 0 for keys with ordinary hashes](FIG_05)

*Figure 5 — Sixteen keys with one shared hash. Each insert compares the new key with every earlier one: 120 in a one-list model, 128 in CPython 3.14.4, where the probe sequence revisits a slot. Keys with spread hashes compare nothing.*

This is **hash flooding**: choosing keys that collide, to make a server do quadratic work. Scott Crosby and Dan Wallach demonstrated it in 2003. About 90,000 colliding strings took 6,506 seconds of CPU to insert in Perl 5.6.1, against under 2 seconds for strings built to collide in a different Perl version. <!-- L14 --> A 2011 advisory found predictable collisions in Java, PHP, Python and Ruby, and called it practically the same problem. <!-- L20 -->

There are two fixes. The first makes the hash unpredictable. Crosby and Wallach proposed universal hashing, <!-- L15 --> and Python salts the hashes of `str` and `bytes` with a random seed, on by default since Python 3.3. <!-- L19 --> PEP 456 moved those hashes to SipHash in Python 3.4, because the older seed could be recovered remotely, <!-- L16 --> and Python 3.11 switched to its faster SipHash-1-3 variant. <!-- L17 --> Integers are not covered: `hash(61)` is 61 in every run. <!-- L18 --> The second fix is Java's: since JDK 8, a `HashMap` bucket that collects 8 entries, in a table of at least 64 buckets, becomes a red-black tree. <!-- L22 --> The worst case then drops from O(n) to O(log n), for keys that implement `Comparable`. <!-- L21 --> The fallback for a broken hash is a search structure.

## The math

| Symbol | Meaning |
|---|---|
| $n$ | number of keys |
| $S(n)$ | comparisons to sort them (the build) |
| $L_s(n)$, $L_b(n)$ | comparisons per lookup by scan and by binary search |
| $q^*$ | lookups at which sort-then-search catches up with scanning |
| $w$ | share of operations that are writes |

Sorting pays once $S(n) + q L_b(n) \le q L_s(n)$, so

$$
q^* \;=\; \frac{S(n)}{L_s(n) - L_b(n)}.
$$

The build is repaid after the build cost divided by what each lookup saves. With the worked example's numbers that is $49 / (8.5 - 3.375) = 9.56$.

Merge sort's worst case is $S(n) = n\lceil \log_2 n \rceil - 2^{\lceil \log_2 n \rceil} + 1$, which is $n \log_2 n - n + 1$ when $n$ is a power of two. <!-- L05 --> A successful lookup costs $L_s = (n+1)/2$ by scanning and about $\log_2 n - 1$ by binary search. Divide, and for large $n$

$$
q^*_{\text{hits}} \;\approx\; 2\log_2 n - 2, \qquad q^*_{\text{misses}} \;\approx\; \log_2 n - 1.
$$

The sort costs about $\log_2 n$ scans' worth of comparisons, and each successful lookup saves half a scan. A miss saves a whole scan, so it repays the sort twice as fast. At $n = 2^{20}$ the exact count gives $19{,}922{,}945 / 524{,}269.5 = 38.00$, as Figure 6 shows.

![Lookups that repay a merge sort, 16 to 1,048,576 keys: hits climb from 9.56 to 38.00 and misses from 4.12 to 19.00, tracking log models](FIG_06)

*Figure 6 — Lookups needed to repay a worst-case merge sort, by number of keys. Exact counts at each power of two; the thin lines are the models 2 log₂ n − 2 and log₂ n − 1.*

Writes change the comparison. Let $I$ be the cost of one insert, in comparisons plus priced writes. Keeping the keys sorted beats appending while $(1 - w)(L_s - L_b) \gt w\,(I_{\text{sorted}} - I_{\text{append}})$, so the break-even write share is

$$
w^* \;=\; \frac{L_s - L_b}{(L_s - L_b) + (I_{\text{sorted}} - I_{\text{append}})}.
$$

Keeping the order pays up to that share of writes and loses past it. For the array, $I_{\text{sorted}} \approx \log_2 n + n/2$ shifts, so $w^*$ tends to one half. At 16 keys it is $5.125 / (5.125 + 12.12) = 29.7\%$. For a red-black tree, $I \approx \log_2 n$ plus a constant, so the break-even ratio of writes to reads, $w^* / (1 - w^*)$, grows like $n / (2\log_2 n)$.

<details>
<summary>Why a red-black tree's height stays within 2 log₂(n + 1)</summary>

Let $b$ be the number of black nodes on every path from the root to an empty link. A subtree whose paths each pass $b$ black nodes holds at least $2^b - 1$ nodes, by induction on height. No red node has a red child, so at least half the nodes on any path are black, and the height $h$ is at most $2b$. Then $n \ge 2^{h/2} - 1$, so $h \le 2\log_2(n+1)$. For 16 keys that bound is 8.17; the lab's tree has height 6.

</details>

## Implementation

The break-even fits in a few lines. This sketch uses merge sort's exact worst case, and a closed-interval binary search's exact average, counted by recursion over the interval sizes it splits into:

```python
from functools import cache

def merge_sort_worst(n):
    k = (n - 1).bit_length()                       # ceil(log2 n)
    return n * k - (1 << k) + 1

@cache
def binary_total(s):
    """Comparisons summed over all s keys of a closed-interval binary search."""
    return 0 if s == 0 else s + binary_total((s - 1) // 2) + binary_total(s // 2)

def lookups_to_repay_sort(n):
    scan, binary = (n + 1) / 2, binary_total(n) / n
    return merge_sort_worst(n) / (scan - binary)

print(round(lookups_to_repay_sort(16), 2), round(lookups_to_repay_sort(2**20), 2))   # 9.56 38.0
print(round(lookups_to_repay_sort(2000), 2))                                           # 20.14
```

The last line answers the opening question. For 2,000 IDs a worst-case sort is repaid after 20.14 successful lookups, so 300 lookups repay it many times over, and sooner if most incoming IDs are absent. If all you ask is whether an ID is present, though, a set skips the search altogether.

Each library names these structures differently. In Python, `sorted` plus `bisect` gives the sorted array, and `insort` gives its O(n) insert. In Java, `Arrays.sort` with `Arrays.binarySearch` gives the array, `TreeMap` the tree, with `floorKey` and `subMap` for the ordered questions, and `HashMap` the hash table. If the keys already arrive sorted, `new TreeMap<>(sortedMap)` builds the tree in linear time without comparing a single key. <!-- L27 -->

The lab behind every count here is one Python file with no dependencies. It runs the scan, the binary search and merge sort with a counting comparison, carries a line-for-line port of `TreeMap`'s insert and lookup methods, and floods CPython's own `dict`. It is under [Lab downloads](#lab-downloads).

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** reading the break-even as a time. Every count here treats comparisons as equal, but a scan reads memory in order while a binary search or a tree jumps around it, and Part 1 showed that those jumps, not the comparison count, decide speed on large arrays. In wall-clock time the sort pays back later than the counts say; how much later depends on the machine, and a later part of this series measures what one probe costs.

**Assuming lookups are uniform.** If most lookups hit a few hot keys near the front of an unsorted array, the scan's average falls far below n/2 and the sort pays back late or never. Count your real lookup mix before quoting q\*.

**Sorting before you know the workload.** When nobody knows how many queries are coming, adaptive indexing, also called database cracking, reorganises the data a little on each query and spreads the build across the queries that actually arrive. <!-- L34 -->

**Trusting a hash map with keys you do not choose.** Expected O(1) is a promise about spread keys. A parser or server that hashes untrusted strings needs a keyed hash, which Python gives `str` and `bytes` by default. Integer keys get no such protection.

**Feeding sorted keys to an unbalanced tree.** A hand-written binary search tree, or any tree without balancing rules, turns ascending input into a list. Use the library's balanced tree.

**Quoting tree counts without the insert order.** This post's tree counts are for keys inserted in ascending order; another order builds another shape, with other counts.

## Key takeaways

- Sorting n keys pays for itself after about 2 log₂ n − 2 successful lookups, counted in comparisons: 9.56 at 16 keys, 38.00 at a million. Lookups that miss repay it twice as fast.
- A sorted array loses to plain appending once writes reach about half the operations, because each insert shifts n/2 keys. A balanced tree such as `TreeMap` loses only past a ratio of writes to reads that grows like n / (2 log₂ n), about 1,770 to one at 65,536 keys, and pays in memory and slightly slower lookups instead.
- A hash map skips the search for exact keys and refuses range, floor and nearest queries. If any query needs order, keep order.
- Keys chosen to collide turn a hash map into a list: 16 of them cost CPython's `dict` 128 comparisons. A keyed hash or Java's tree bins is the fix; integer hashes are not keyed.

## Try it yourself

The full ladder, with self-checks and answers from the author's run, is in the lab's README under [Lab downloads](#lab-downloads). These three need only the article.

1. **E1, reproduce.** At 16 keys, every lookup a miss, how many lookups repay a worst-case merge sort?

<details><summary>Answer</summary>

A failed scan costs 16 and a failed binary search 70/17 ≈ 4.12, so each miss saves 11.88. 49 / 11.88 = 4.12, so sorting is ahead from the 5th lookup.

</details>

2. **E3, predict.** Before running anything, predict q\* for successful lookups at 2²⁴, about 16.8 million keys.

<details><summary>Answer</summary>

2 log₂ n − 2 = 2 × 24 − 2 = 46. The lab's `scale --max-exp 24` prints 46.00.

</details>

3. **E3, predict.** If a shift cost a quarter of a comparison, about how many writes per read could a sorted array of 65,536 keys absorb before appending wins?

<details><summary>Answer</summary>

Each insert then costs about n/2 × 1/4 while each lookup still saves about n/2, so about 1 / (1/4) = 4 writes per read. The lab's `writes --write-price 0.25` prints 3.99.

</details>

## References

### Lab downloads

- [`README.md`](LAB_01) — the lab's grade, provenance, run order, and the E1–E3 exercise ladder with answers.
- [`pays_for_itself.py`](LAB_02) — counts every number in this post: the scan, binary search, merge sort, a port of `TreeMap`, and CPython's `dict` flooded.
- [`captures.json`](LAB_03) — the author's run, machine-readable; every figure was drawn from it.
- [`expected-output.txt`](LAB_04) — the same run as printed, to compare with yours.
- [`notebook.ipynb`](LAB_05) — the README with a runnable cell under each step and exercise.
- [Complete lab](https://minio.canery.in/media/lab-when-a-search-structure-pays-for-itself.zip) — every file above in one zip.

### Sources

1. Stober, F., Weiß, A. [Lower Bounds for Sorting 16, 17, and 18 Elements](https://doi.org/10.1137/1.9781611977561.ch17). ALENEX 2023, SIAM, pp. 201–213. [arXiv:2206.05597](https://arxiv.org/abs/2206.05597).
2. Flajolet, P., Golin, M. [Mellin Transforms and Asymptotics: The Mergesort Recurrence](https://doi.org/10.1007/BF01177551). *Acta Informatica* 31(7), 1994: 673–696.
3. Crosby, S. A., Wallach, D. S. [Denial of Service via Algorithmic Complexity Attacks](https://www.usenix.org/legacy/events/sec03/tech/full_papers/crosby/crosby.pdf). 12th USENIX Security Symposium, 2003: 29–44.
4. Tarjan, R. E. [Amortized Computational Complexity](https://doi.org/10.1137/0606031). *SIAM Journal on Algebraic and Discrete Methods* 6(2), 1985: 306–318.
5. Guibas, L. J., Sedgewick, R. [A Dichromatic Framework for Balanced Trees](https://doi.org/10.1109/SFCS.1978.3). 19th IEEE Symposium on Foundations of Computer Science, 1978: 8–21.
6. Athanassoulis, M., Kester, M. S., Maas, L. M., Stoica, R., Idreos, S., Ailamaki, A., Callaghan, M. [Designing Access Methods: The RUM Conjecture](https://doi.org/10.5441/002/edbt.2016.42). EDBT 2016: 461–466.
7. Heimes, C. [PEP 456 — Secure and Interchangeable Hash Algorithm](https://peps.python.org/pep-0456/). Python Enhancement Proposals, 2013. Accessed 2026-10-14.
8. Python Software Foundation. [Command line and environment](https://docs.python.org/3/using/cmdline.html) (`-R`, `PYTHONHASHSEED`) and [Data model](https://docs.python.org/3/reference/datamodel.html) (`object.__hash__`). Accessed 2026-10-14.
9. Python Software Foundation. [What's New In Python 3.11](https://docs.python.org/3/whatsnew/3.11.html). Accessed 2026-10-14.
10. Python Software Foundation. [`bisect` — Array bisection algorithm](https://docs.python.org/3/library/bisect.html). Accessed 2026-10-14.
11. CPython. [`Objects/dictobject.c`](https://github.com/python/cpython/blob/v3.14.0/Objects/dictobject.c), tag v3.14.0.
12. OpenJDK. [`java/util/TreeMap.java`](https://github.com/openjdk/jdk/blob/jdk-25-ga/src/java.base/share/classes/java/util/TreeMap.java) and [`java/util/HashMap.java`](https://github.com/openjdk/jdk/blob/jdk-25-ga/src/java.base/share/classes/java/util/HashMap.java), tag jdk-25-ga.
13. OpenJDK. [JEP 180: Handle Frequent HashMap Collisions with Balanced Trees](https://openjdk.org/jeps/180). Accessed 2026-10-14.
14. Oracle. [`java.util.TreeMap`](https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeMap.html), Java SE 25 API. Accessed 2026-10-14.
15. oCERT. [oCERT-2011-003: Multiple implementations denial-of-service via hash algorithm collision](https://ocert.org/advisories/ocert-2011-003.html). 2011. Accessed 2026-10-14.
