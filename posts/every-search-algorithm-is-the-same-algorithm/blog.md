---
title: Every Search Algorithm Is the Same Algorithm
summary: "Binary search, KMP, A* and HNSW run one loop. What differs is the structure that lets a single probe eliminate many candidates, and what it cost to build."
slug: every-search-algorithm-is-the-same-algorithm
categories: [algorithms]
tags: [algorithms, binary-search, string-matching, graph-search, nearest-neighbor, performance]
---

# Every Search Algorithm Is the Same Algorithm

![A dense grid of small marks narrowing in stages to a single highlighted mark, with the discarded ones left as faint ghosts](https://minio.canery.in/media/cover-image.png)

> [!NOTE]
> **Insights** — Every search algorithm runs the same loop: hold a set of candidates, probe one, throw away everything the probe ruled out. Binary search, KMP, A\* and HNSW differ in exactly one place — the structure that lets a single probe eliminate more than one candidate. That structure is always prepaid, and comparing search algorithms means comparing what you paid for it, not how fast the loop spins.

**Level:** intermediate · **You need:** big-O notation, arrays and graphs, basic logarithms · **Time:** ~21 min

## Why this matters

You choose a search structure more often than you notice. Picking a sorted array over a hash map, adding a heuristic to a path-finder, reaching for a vector index instead of a scan — these are all the same decision wearing four costumes, and they are usually argued about on the wrong axis.

The usual argument is about query time: this one is $O(\log n)$, that one is $O(n)$. That comparison hides the part that decides the outcome. A structure that makes queries fast has to be built, kept correct under writes, and laid out in memory somewhere. Once you can see all four algorithms as one loop with a different prepaid asset bolted on, the real question becomes obvious: what did the skip cost, and are you running enough queries to earn it back?

## The problem

Searching means this: you have a set of candidates, one or more of which is the answer, and a way to test candidates one at a time. You want to spend as few tests as possible.

Call the untested set the **frontier**. Every step picks one candidate from the frontier, tests it, and uses the result to shrink the frontier. When the frontier is empty or the answer is found, you stop. That is the whole shape, and it is shown in Figure 1.

![Flow diagram of the universal search loop: a frontier set feeds into a probe step, the probe result feeds an eliminate step, which shrinks the frontier and loops back, with an exit arrow when the answer is found](https://minio.canery.in/media/fig-01-search-loop.png)

*Figure 1 — The loop every search algorithm runs. The only interesting box is `eliminate`.*

The constraint that makes this hard lives in that `eliminate` box. A test on one candidate tells you about that candidate. By default it tells you nothing about any other candidate, so it removes exactly one from the frontier. Search a set of 16 that way and you spend up to 16 tests.

To do better, a test has to say something about candidates you did not test. That is only possible if the candidates are related to each other in some way you know about in advance. Sorted order is such a relation. So is a precomputed table of pattern self-overlaps, a distance estimate to a goal, and a graph of near-neighbours. None of them come free, and none of them appear from nowhere at query time.

So the real problem is not "how do I search fast". It is: **what relation between candidates can I establish ahead of time, and how many candidates does one probe eliminate once I have it?**

## Worked example

Take 16 sorted integers:

| index | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| value | 3 | 9 | 14 | 21 | 28 | 35 | 42 | 47 | 53 | 61 | 68 | 74 | 79 | 85 | 91 | 97 |

Look for **61**, which sits at index 9. Do it twice.

**Ignoring the order.** Probe index 0, get 3, not 61, eliminate index 0. Probe index 1, get 9, eliminate index 1. Keep going. You reach 61 on the tenth probe. Ten probes, and each one removed exactly one candidate from a frontier of 16. The fact that the array was sorted did nothing, because nothing in the procedure used it.

**Using the order.** The frontier starts as all 16 indices.

1. Probe the middle, index 7, value **47**. Since $47 < 61$ and the array ascends, every index from 0 to 7 is too small. Eliminate all eight at once. Frontier: indices 8–15, eight candidates.
2. Probe the middle of what is left, index 11, value **74**. Since $74 > 61$, indices 11 through 15 are all too large. Eliminate five. Frontier: indices 8, 9, 10 — three candidates.
3. Probe index 9, value **61**. Found.

Three probes instead of ten. Figure 2 shows the frontier collapsing across those three steps.

![Three-stage trace of binary search over a 16-element sorted array, showing the surviving candidate window shrinking from all 16 indices to indices 8-15, then to 8-10, then to the single found index 9](https://minio.canery.in/media/fig-02-binary-search-trace.png)

*Figure 2 — The frontier after each probe: 16 candidates, then 8, then 3, then found. The shaded region is what each probe eliminated.*

The interesting number is not "3 probes". It is the per-probe elimination count, which is what Figure 3 plots.

![Bar chart comparing candidates eliminated per probe: the linear scan shows ten bars of height one, while binary search shows three bars of heights eight, five and two](https://minio.canery.in/media/fig-03-elimination-rate.png)

*Figure 3 — Candidates eliminated per probe. Same array, same target. The linear scan gets one per probe; the ordered search gets 8, then 5, then 2.*

Both runs eliminate all 16 candidates in the end — that is what finishing means. The linear scan pays 10 probes for 16 eliminations. The ordered search pays 3. Sorted order did not make any single comparison faster. It raised the **exchange rate** between probes and eliminations, and that is the only thing that changed.

One honest note on the numbers: 3 probes is what this particular target cost. Searching 16 elements this way takes at most 5 probes, because the window shrinks $16 \to 8 \to 4 \to 2 \to 1$ in the worst case. The point stands either way — 5 is still far below 16.

## Intuition

Think of every probe as buying eliminations, and the structure as setting the price.

With no structure, the price is fixed: one probe, one elimination. Sorted order changes the deal — a probe in the middle eliminates half the frontier, whatever the frontier currently is. That is why the cost goes from "count the candidates" to "count the halvings", and counting halvings is what a logarithm does.

The part that gets skipped in most explanations is that **the exchange rate is prepaid**. Sorting 16 integers is not free. If you search that array once, sorting it costs more than the linear scan you avoided. Sort it once and search it a million times and the sort disappears into rounding error. The structure is a fixed cost amortised over queries, which is why "which search is faster" is an incomplete question and "how many queries before this pays for itself" is the complete one.

An analogy, with its breaking point attached. A prepaid search structure works like an index in the back of a book: someone spent hours building it so that you spend seconds using it, and it only makes sense because many readers use it. **The analogy breaks on updates.** Add a paragraph to a book and the index is stale but the book is still readable; add an element to a sorted array or a vector index and the structure can be wrong in a way that makes queries silently return the wrong answer. Search structures are not passive addenda — they are invariants, and invariants can be violated.

Hold on to one sentence for the rest of the post: *a probe eliminates more than one candidate only when a prepaid structure connects the probed candidate to the others.* The next four sections are the same sentence, with four different structures in the blank.

## Ordering buys the skip

The prepaid structure is sorted order. The probe is a comparison. The elimination rule is "everything on the wrong side of the probe is out."

Sorted order buys roughly $\log_2 n$ probes instead of $n$, and no comparison-based method can do better — that bound comes back in the math section. The part that gets less attention is that binary search, the most-taught algorithm in computer science, is hard to write correctly and hard to make fast, for two completely unrelated reasons.

**It is hard to write correctly.** In 2006 Joshua Bloch reported that the standard midpoint calculation `(low + high) / 2` overflows once the sum exceeds $2^{31} - 1$, wrapping to a negative number and producing a negative array index. <!-- L22 --> The same defect sat undetected in the JDK's `java.util.Arrays.binarySearch` for about nine years, and before that in the implementation published in Jon Bentley's *Programming Pearls*. <!-- L23 --> The fix is to never form the large sum: compute `low + ((high - low) / 2)`, or use the unsigned shift `(low + high) >>> 1`. <!-- L24 --> The bug is a good reminder that a proof of correctness is a proof about the algorithm, not about the arithmetic the machine actually performs.

**It is hard to make fast.** The asymptotics say binary search on a sorted array is optimal. The hardware disagrees. Each probe in a binary search jumps to an unpredictable location, so the early probes miss cache and the branch on the comparison result is close to unpredictable. Khuong and Morin tested the alternatives and found that for large $n$, storing the same elements in **Eytzinger order** — the breadth-first layout normally used for binary heaps, where the root sits at index 1 and the children of node $i$ live at $2i$ and $2i+1$ — is usually the fastest layout, beating sorted order with binary search. <!-- L26 --> For small $n$, plain sorted order with a good implementation still wins. <!-- L27 --> Their fast versions use conditional moves to dodge branch mispredictions and explicit prefetching to hide memory latency. <!-- L29 -->

This is not a settled result, and pretending otherwise would be dishonest. Khuong and Morin note that their conclusion runs counter to earlier experimental work by Brodal, Fagerberg and Jacob, which had found B-tree and van Emde Boas layouts faster at large $n$. <!-- L28 --> Two careful experimental papers, different answers, different hardware eras. Treat layout choice as something to measure on your machine, not something to look up.

The transferable lesson: the elimination rule and the memory layout are independent choices. Binary search fixes the first and says nothing about the second, and the second is often what decides the wall-clock time.

## Precomputation buys the skip

Now the candidates are not values in an array but *alignments* of a pattern against a text. If the text has length $n$ and the pattern length $m$, there are about $n - m + 1$ places the pattern could start, and each one is a candidate.

Test an alignment by comparing characters. The naive method tests one alignment, and on a mismatch shifts the pattern one position and starts over — one probe, one elimination, exactly the linear scan from the worked example. Knuth, Morris and Pratt open their 1977 paper with how bad this gets: matching the pattern $a^n b$ against the text $a^{2n} b$ costs about $(n+1)^2$ character comparisons. <!-- L15 --> Almost every comparison re-examines a character that was already read.

Their fix — published in *SIAM Journal on Computing* in June 1977, and received by the editors nearly three years before that <!-- L13 --> — is a table computed from the pattern alone, before the text is ever touched. For each prefix of the pattern, it records the longest proper prefix of the pattern that is also a suffix of that prefix. The consequence is the interesting part, and the paper states the reason plainly: your current position in the pattern already carries enough information to recreate the text characters just scanned. <!-- L16 --> You do not need to look at them again, so the text pointer never moves backwards.

Trace it. Pattern `AABAAC`, text `AABAABAABAAC`.

- Match `AABAA` against text positions 0–4. At text position 5 the text has `B`, the pattern wants `C`. Mismatch after 5 matched characters.
- The naive move: shift the pattern by one, send the text pointer back to position 1. The KMP move: the table says the 5-character match `AABAA` ends with `AA`, which is also how the pattern starts. Those two characters are already verified. Resume comparing at pattern index 2, **leaving the text pointer at position 5**.
- Pattern index 2 is `B`, text position 5 is `B`. Match. Continue through positions 6 and 7, mismatch again at position 8, apply the table again, and the pattern completes at position 11.

The text pointer visited 0,1,2,3,4,5,6,7,8,9,10,11 and never went back. That is the whole guarantee: $O(m + n)$ time in the worst case, with constants that do not depend on the alphabet size. <!-- L14 --> <!-- L17 --> Figure 4 puts the naive backtrack and the table-driven shift side by side on this example.

![Two aligned traces of pattern AABAAC against text AABAABAABAAC: the upper shows naive matching sending the text pointer backwards after a mismatch, the lower shows the KMP shift keeping the text pointer stationary while the pattern slides forward two positions](https://minio.canery.in/media/fig-04-kmp-shift.png)

*Figure 4 — Same mismatch, two responses. The naive scan rewinds the text pointer; KMP slides the pattern and leaves the pointer where it is.*

Boyer and Moore, publishing in the same year, bought a different skip. <!-- L18 --> They scan the pattern **right to left**, so a mismatch at the far end can prove that many alignments are impossible at once, and they precompute how far to jump. The result is unusual: the algorithm usually reads only a fraction of the characters it moves past, and gets *faster* as the pattern gets longer. <!-- L19 -->

"Usually" is doing real work in that sentence and should not be dropped. That is average behaviour, not a worst-case bound. Cole later established that the search performs roughly $3n$ character comparisons in the worst case and that the bound is tight. <!-- L20 --> The unmodified algorithm is also not linear when the pattern occurs many times in the text; Galil's variant restores a linear worst case. <!-- L21 -->

So: two algorithms, one year, same problem. KMP prepays a table about the pattern's self-overlap and gets a hard linear guarantee. Boyer–Moore prepays a table about character positions and gets better typical behaviour with a messier worst case. Neither is strictly better, which is exactly what you would expect once you see them as two prices for the same commodity.

## A heuristic buys the skip

Graph search is where the loop from Figure 1 is most literally visible, because the frontier is an explicit set of nodes.

Go and read Dijkstra's 1959 paper. It is three pages long, and it is not quite the algorithm people describe. <!-- L07 --> He states two problems; the second is finding the minimum-length path between **two given nodes** $P$ and $Q$, and the procedure stops once $Q$ joins the set of nodes with known minimum paths. <!-- L01 --> <!-- L02 --> It is a single-pair algorithm in the original, not a single-source-to-everywhere one.

The mechanism rests on optimal substructure: if $R$ lies on the minimal path from $P$ to $Q$, then the minimal path from $P$ to $R$ is known as part of it. <!-- L03 --> Nodes are kept in three sets — those with a known minimum path, those adjacent to that set, and the rest — and each step moves the frontier node of minimum distance into the known set. <!-- L04 -->

Two things are *not* in the paper. There is no priority queue and no heap, and there is no asymptotic analysis anywhere in it. <!-- L05 --> The justification Dijkstra actually gives is about storage: his method holds fewer than $n$ branches at a time, where the alternatives he compares against needed all of them. <!-- L06 --> The familiar $O(m + n \log n)$ bound is not his; it is the amortised bound from Fredman and Tarjan's Fibonacci heaps, published in the 1980s. <!-- L08 --> The algorithm and its complexity are separated by nearly three decades, and conflating them is the most common thing said wrongly about Dijkstra's algorithm.

In the vocabulary of this post, Dijkstra's elimination rule is: *once a node enters the known set, no shorter path to it exists, so every other route to it is eliminated.* That is a strong rule, and it is bought entirely by non-negative edge weights. The frontier grows outward from $P$ in all directions at once, because nothing tells the algorithm which direction $Q$ is in.

A\* buys that missing information. Published in 1968 by Hart, Nilsson and Raphael, it orders the frontier not by distance travelled but by distance travelled plus an estimate of distance remaining. <!-- L09 --> If the estimate never overstates the true remaining cost — the property called **admissibility** — A\* still returns a least-cost path. <!-- L10 --> The estimate is the prepaid structure. On a map it might be straight-line distance, computable in advance because you know the coordinates.

The effect is visible in Figure 5: the same graph, the same obstacle, two very different frontier shapes.

![Side-by-side grid search comparison with identical start, goal and wall obstacle: Dijkstra's expanded nodes form a roughly circular region around the start, while A-star's expanded nodes form a narrow corridor biased toward the goal](https://minio.canery.in/media/fig-05-dijkstra-vs-astar.png)

*Figure 5 — Same grid, same wall, same cost-11 path. Running both on this grid, Dijkstra expands 58 cells and A\* expands 33. The shape of the shaded region, not the count, is the thing to notice.*

The A\* story has a correction in it that most write-ups omit. The 1968 paper also claimed a stronger property: that A\* expands no more nodes than any other algorithm with the same information. That claim needed the **consistency** assumption, and the authors published a correction in 1972. <!-- L11 --> Dechter and Pearl later pinned down the precise situation: with merely admissible estimates A\* is not optimal in that sense, and with consistent ones it is. <!-- L12 --> If you have ever read "A\* is optimally efficient" with no conditions attached, that is the uncorrected 1968 claim still in circulation.

The relationship is cleaner than it looks: A\* with a heuristic of zero *is* Dijkstra's algorithm. They are one algorithm with a knob, and the knob is how much you prepaid for knowing where the goal is.

## Geometry buys the skip

The last case is the one where the previous three tricks all fail.

Given a query vector and a few million stored vectors, find the nearest. There is no total order to bisect — sorting by one coordinate tells you almost nothing in 700 dimensions. There is no self-overlap table, because there is no pattern. A heuristic exists, but the geometry is too weak for exact elimination to prune much.

So the deal changes. Instead of buying *certain* elimination, you buy *probable* elimination and accept that the answer is sometimes wrong. HNSW — posted as a preprint in 2016 and published in *IEEE TPAMI* in 2020, so the version most people cite predates peer review by four years <!-- L32 --> — builds a multi-layer proximity graph: each element appears in layers up to a maximum drawn from an exponentially decaying distribution, so the top layer is sparse with long-range links and the bottom layer is dense with short-range ones. <!-- L30 --> A search enters at the top, greedily walks toward the query using the long hops, drops a layer, and repeats with finer steps. Figure 6 shows the descent.

![Three stacked layers of a proximity graph with a query point: the sparse top layer has few nodes and long edges, the middle layer more nodes and medium edges, the dense bottom layer many nodes and short edges, with a path descending through the layers toward the query](https://minio.canery.in/media/fig-06-hnsw-layers.png)

*Figure 6 — Descending an HNSW index. Coarse hops at the top cover distance; fine hops at the bottom refine the answer.*

The elimination rule here is a soft one: *nodes far from the greedy path are assumed to be far from the query, and are never examined.* That assumption is usually right and occasionally wrong, and when it is wrong you silently miss the true nearest neighbour.

Be careful with how this method's cost is described. The paper's abstract says the scale separation "allows a logarithmic complexity scaling" — that is a design and empirical claim about how the structure behaves, not a proven worst-case bound of the kind binary search has. <!-- L31 --> The honest way to compare these systems is the one the ANN-Benchmarks work established: not a single speed number, but a recall-versus-throughput curve, because every implementation can be tuned to trade one for the other. <!-- L33 --> A vector index that answers in 2 ms tells you nothing until you know what recall it hit while doing it.

That trade is the real news. The first three sections bought elimination with certainty intact. This one shows what happens when the geometry will not support that: you can still buy the skip, but the currency changes from build time to correctness.

## The math

Three symbols, defined on use. Let $n$ be the number of candidates, $p$ the number of probes, and $E_i$ the number of candidates eliminated by probe $i$.

Finishing a search means eliminating every candidate except the answer, so for any search algorithm at all:

$$\sum_{i=1}^{p} E_i \;=\; n$$

Every search spends exactly $n$ eliminations; the algorithms differ only in how many probes they need to buy them. In the worked example, the linear scan bought 16 eliminations at one per probe, and the ordered search bought the same 16 in three probes as $8 + 5 + 2 + 1$.

Now the lower bound. If a probe has two useful outcomes, then after $p$ probes an algorithm can distinguish at most $2^p$ different cases. To identify which one of $n$ candidates is the answer, you need $2^p \ge n$, which gives:

$$p \;\ge\; \log_2 n$$

No comparison-based search of a sorted array can beat about $\log_2 n$ probes in the worst case, because each comparison yields at most one bit and you need $\log_2 n$ bits to name the answer. <!-- L25 --> Binary search achieves $\lfloor \log_2 n \rfloor + 1$ probes in the worst case, which is why nothing has replaced it in the comparison model — and why Eytzinger layouts win on speed without contradicting the bound. They perform the *same number* of comparisons; they just perform them against memory that is already in cache.

For graph search, define $g(v)$ as the cost of the best path found so far from the start to $v$, and $h(v)$ as an estimate of the remaining cost from $v$ to the goal. A\* orders the frontier by:

$$f(v) \;=\; g(v) + h(v)$$

The algorithm always expands the frontier node with the smallest $f$. Setting $h(v) = 0$ everywhere makes $f(v) = g(v)$, which orders the frontier purely by distance from the start — that is Dijkstra's algorithm exactly, which is the sense in which it is a special case of A\*.

The two conditions that keep coming up differ like this. Writing $h^*(v)$ for the true remaining cost, and $c(u,v)$ for the cost of the edge from $u$ to $v$:

$$\text{admissible:}\quad h(v) \le h^*(v) \qquad\qquad \text{consistent:}\quad h(u) \le c(u,v) + h(v)$$

Admissibility says the estimate never overstates what is left, and it is what guarantees the path A\* returns is a least-cost path. Consistency is the stronger, more local condition — the estimate may not drop by more than the cost of the edge you crossed — and it is what the 1972 correction and Dechter and Pearl's later analysis identified as the requirement for the node-expansion optimality claim. <!-- L11 --> <!-- L12 --> Every consistent heuristic is admissible; the reverse does not hold.

Figure 7 collects all four structures against these terms.

![Scatter positioning map with prepaid cost on the horizontal axis and candidates eliminated per probe on the vertical axis, plotting linear scan low on both, KMP, Boyer-Moore and binary search high on elimination for modest cost, Dijkstra and A-star further right, and HNSW highest cost with elimination marked as approximate](https://minio.canery.in/media/fig-07-price-of-the-skip.png)

*Figure 7 — Every algorithm in this post on two axes. Linear scan sits at the origin because it prepays nothing. HNSW is drawn with a dashed marker because its vertical position is bought with recall, not certainty.*

## Implementation

Here is the loop from Figure 1, written once, with the elimination rule left as a parameter.

```python
def search(frontier, pick, test, eliminate):
    """The shared skeleton. Every classical search is this with different parts."""
    while frontier:
        candidate = pick(frontier)          # which candidate to probe
        result = test(candidate)            # the probe itself
        if result == "found":
            return candidate
        frontier = eliminate(frontier, candidate, result)   # the whole game
    return None
```

Binary search fills in the blanks by representing the frontier as a half-open index range, which is what makes one probe able to discard half of it:

```python
def binary_search(a, target):
    lo, hi = 0, len(a)                      # frontier = indices [lo, hi)
    while lo < hi:
        mid = lo + (hi - lo) // 2           # never form lo + hi; see the overflow bug
        if a[mid] == target:
            return mid
        elif a[mid] < target:
            lo = mid + 1                    # eliminate [lo, mid]
        else:
            hi = mid                        # eliminate [mid, hi)
    return None
```

A\* fills in the same blanks with a priority queue as the frontier and a heuristic setting the order:

```python
import heapq

def astar(start, goal, neighbours, cost, h):
    frontier = [(h(start), 0, start)]       # (f = g + h, g, node)
    best_g = {start: 0}
    while frontier:
        _, g, node = heapq.heappop(frontier)    # pick: smallest f
        if node == goal:
            return g
        if g > best_g.get(node, float("inf")):
            continue                        # eliminate: a better route here already won
        for nxt in neighbours(node):
            g2 = g + cost(node, nxt)
            if g2 < best_g.get(nxt, float("inf")):
                best_g[nxt] = g2
                heapq.heappush(frontier, (g2 + h(nxt), g2, nxt))
    return None
```

Pass `h=lambda v: 0` and this function is Dijkstra's algorithm. The `continue` line is the elimination rule doing its work: it is where the algorithm discards a candidate route because a probe already proved a better one exists.

## Limitations and common mistakes

> [!WARNING]
> **Common mistake:** comparing query complexity while ignoring build cost. A sorted array supports $O(\log n)$ lookups, but sorting is $O(n \log n)$ and every insertion into the middle is $O(n)$. On a workload with more writes than reads, the linear scan you rejected wins outright. Count the queries per rebuild before choosing.

Three more that bite in practice.

**Reading an asymptotic bound as a speed prediction.** Binary search and an Eytzinger-layout search perform the same number of comparisons and can differ substantially in wall-clock time on large arrays, because one of them is fighting the cache and the other is not. <!-- L26 --> Asymptotics rank algorithms by comparison count. They do not rank implementations, and above a few thousand elements the layout can matter more than the bound.

**Quoting A\*'s optimality without its condition.** "A\* expands the fewest nodes of any algorithm with the same heuristic" is the 1968 claim that the authors corrected in 1972; it needs consistency, not just admissibility. <!-- L11 --> <!-- L12 --> If you are debugging a search that re-expands nodes it has already closed, an admissible-but-inconsistent heuristic is a strong first suspect, and it is not a bug in your implementation.

**Treating approximate results as exact ones.** An ANN index returns a neighbour, not necessarily *the* neighbour. Reporting its latency without its recall describes half the system, since the same index tuned differently gives a different point on the same curve. <!-- L33 --> If a retrieval system quietly degrades in quality, an index that was tuned for throughput and measured only for latency is the usual cause.

The unifying frame has a limit of its own. It explains algorithms that *eliminate* candidates, and it says nothing useful about hashing, which does not narrow a frontier at all — it computes the answer's location directly. A hash lookup is not a fast search; it is the absence of a search. When it fits your access pattern, it beats everything in this post, which is why the first question to ask is not which search to use but whether you need to search at all.

## Key takeaways

- Every search algorithm here is one loop — probe a candidate, eliminate what the probe ruled out — and they differ only in the prepaid structure that lets one probe eliminate many candidates.
- The structure is always paid for in advance, in build time, memory layout, maintenance under writes, or accuracy. "Which is faster" is incomplete until you say how many queries amortise that cost.
- Dijkstra's 1959 paper contains no priority queue and no complexity analysis, and solves the two-node problem; the amortised $O(m + n \log n)$ bound is Fredman and Tarjan's, decades later. A\* is the same algorithm with a prepaid estimate, and reduces to Dijkstra when that estimate is zero.
- When geometry is too weak for exact elimination, as in high-dimensional nearest-neighbour search, you can still buy the skip — but you pay in recall, which is why these systems are compared on a curve rather than a number.

## References

1. Dijkstra, E. W. "A Note on Two Problems in Connexion with Graphs." *Numerische Mathematik* 1 (1959): 269–271. [PDF](https://ir.cwi.nl/pub/9256/9256D.pdf). Accessed 2026-09-08.
2. Hart, P. E., Nilsson, N. J., Raphael, B. "A Formal Basis for the Heuristic Determination of Minimum Cost Paths." *IEEE Transactions on Systems Science and Cybernetics* 4, no. 2 (1968): 100–107.
3. Hart, P. E., Nilsson, N. J., Raphael, B. "Correction to 'A Formal Basis for the Heuristic Determination of Minimum Cost Paths'." *SIGART Newsletter* 37 (1972): 28–29. [ACM](https://dl.acm.org/doi/10.1145/1056777.1056779).
4. Dechter, R., Pearl, J. "Generalized Best-First Search Strategies and the Optimality of A\*." *Journal of the ACM* 32, no. 3 (1985): 505–536. [ACM](https://dl.acm.org/doi/10.1145/3828.3830).
5. Knuth, D. E., Morris, J. H., Pratt, V. R. "Fast Pattern Matching in Strings." *SIAM Journal on Computing* 6, no. 2 (1977): 323–350. [PDF](https://www.cs.jhu.edu/~misha/ReadingSeminar/Papers/Knuth77.pdf). Accessed 2026-09-08.
6. Boyer, R. S., Moore, J S. "A Fast String Searching Algorithm." *Communications of the ACM* 20, no. 10 (1977): 762–772. [PDF](https://www.cs.utexas.edu/~moore/publications/fstrpos.pdf).
7. Cole, R. "Tight Bounds on the Complexity of the Boyer–Moore String Matching Algorithm." *SIAM Journal on Computing* 23, no. 5 (1994): 1075–1091. [SIAM](https://epubs.siam.org/doi/10.1137/S0097539791195543).
8. Bloch, J. "Extra, Extra — Read All About It: Nearly All Binary Searches and Mergesorts are Broken." Google Research blog, June 2006. [Link](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/). Accessed 2026-09-08.
9. Khuong, P.-V., Morin, P. "Array Layouts for Comparison-Based Searching." *ACM Journal of Experimental Algorithmics* 22 (2017). [arXiv:1509.05053](https://arxiv.org/abs/1509.05053). Accessed 2026-09-08.
10. Malkov, Y. A., Yashunin, D. A. "Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs." *IEEE Transactions on Pattern Analysis and Machine Intelligence* 42, no. 4 (2020): 824–836. [arXiv:1603.09320](https://arxiv.org/abs/1603.09320). Accessed 2026-09-08.
11. Fredman, M. L., Tarjan, R. E. "Fibonacci Heaps and Their Uses in Improved Network Optimization Algorithms." *Journal of the ACM* 34, no. 3 (1987): 596–615. [ACM](https://dl.acm.org/doi/10.1145/28869.28874).
12. Aumüller, M., Bernhardsson, E., Faithfull, A. "ANN-Benchmarks: A Benchmarking Tool for Approximate Nearest Neighbor Algorithms." *Information Systems* 87 (2020). [arXiv:1807.05614](https://arxiv.org/abs/1807.05614). Accessed 2026-09-08.
13. Knuth, D. E. *The Art of Computer Programming, Volume 3: Sorting and Searching*, 2nd ed. Addison-Wesley, 1998, §6.2.1.
