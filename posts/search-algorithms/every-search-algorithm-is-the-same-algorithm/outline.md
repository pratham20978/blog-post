# Outline — every-search-algorithm-is-the-same-algorithm

**Tier:** L2 · **Budget:** ~4,200 words · **Figures:** 7 + cover (L2 allows 5–8)

**Thesis.** Every search algorithm is one loop: hold a set of candidates, probe one, eliminate the ones the probe ruled out. What separates binary search from KMP from A* from HNSW is not the loop. It is the *structure that lets the probe eliminate more than one candidate*, and every one of those structures is paid for in advance.

**Why this earns four families in one L2 post.** Each family is evidence for the thesis, not its own tutorial. A reader wanting KMP in full detail is served by a later L2 of its own; this post's job is the transfer — that the skip is a purchased asset, and its price is the thing to compare.

---

| # | Section | Target | Job | Figure |
|---|---|---|---|---|
| 1 | `# Title` + `## Insights` | 90 | The answer: the loop is shared, the skip structure is not | — |
| 2 | Who this is for | 40 | level, prereqs, time | — |
| 3 | `## Why this matters` | 170 | You pick search structures constantly and compare them on the wrong axis | — |
| 4 | `## The problem` | 340 | State search precisely: candidate set, probe, elimination. Name the constraint — a probe returns one bit-ish of information | FIG_01 |
| 5 | `## Worked example` | 630 | 16 sorted integers, traced. Linear scan vs binary search, counting *candidates eliminated per probe*. Real numbers, by hand | FIG_02, FIG_03 |
| 6 | `## Intuition` | 420 | The skip budget. Probes buy elimination; structure raises the exchange rate; the structure is prepaid. Analogy + its breaking point | — |
| 7 | `## Ordering buys the skip` | 370 | Binary search. The log lower bound. Then the two ways it bites in practice: the overflow bug (L22–L24) and cache layout (L26–L29) | — |
| 8 | `## Precomputation buys the skip` | 370 | KMP and Boyer–Moore. The failure function *is* the prepaid structure. Naive (n+1)² vs O(m+n). BM's right-to-left scan and its honest worst case | FIG_04 |
| 9 | `## A heuristic buys the skip` | 370 | Dijkstra 1959 as it actually is (three sets, no heap, no complexity, single-pair) → A* as Dijkstra plus a prepaid estimate. Admissibility, and the 1972 correction | FIG_05 |
| 10 | `## Geometry buys the skip` | 370 | HNSW. When exact elimination is impossible you buy *probabilistic* elimination and pay in recall. Log scaling as a design claim, not a theorem | FIG_06 |
| 11 | `## The math` | 420 | The skip identity; ⌈log₂(n+1)⌉ decision-tree bound; A* as f = g + h with h = 0 collapsing to Dijkstra; admissible vs consistent | FIG_07 |
| 12 | `## Implementation` | 340 | One `search()` skeleton in Python; binary search and A* as instantiations of the same loop with different `eliminate` | — |
| 13 | `## Limitations and common mistakes` | 210 | Comparing query time while ignoring build cost; asymptotics vs cache; quoting A*'s uncorrected optimality; treating ANN recall as free | — |
| 14 | `## Key takeaways` | 60 | 4 bullets, each a claim | — |
| 15 | `## References` | 30 | the 13 used sources | — |

**Total target:** ~4,210 words.

---

## Figure plan

| ID | Type | Carries |
|---|---|---|
| COVER | cover image | — |
| FIG_01 | flow diagram | The universal loop: candidates → probe → eliminate → repeat. Every later section refers back to this shape |
| FIG_02 | trace diagram | Binary search on the 16-element array, 4 probes, showing the surviving candidate window shrink 16→8→4→2→1 |
| FIG_03 | bar chart | Candidates eliminated per probe, linear vs binary, on the same array. Makes "exchange rate" visible |
| FIG_04 | before/after alignment | Naive backtracking vs KMP's failure-function shift on one text/pattern pair |
| FIG_05 | grid comparison | Dijkstra's uniform frontier vs A*'s goal-biased frontier on the same grid with the same obstacle |
| FIG_06 | layered graph | HNSW descent: sparse top layer long hops, dense bottom layer short hops |
| FIG_07 | comparison table graphic | The four skip structures: what is prepaid, build cost, query saving, what you give up |

Figure ratio: 7 figures / ~4,200 words = one per 600 words. In the 500–700 band.

---

## Padding test

What can the reader do after each section that they could not before?

- Problem → state any search task in candidate/probe/eliminate terms
- Worked example → count elimination per probe by hand
- Intuition → predict that a structure must be prepaid
- Ordering → explain why sorted order is worth log n, and why the asymptotics can still lose to layout
- Precomputation → explain what the failure function stores and why it removes backtracking
- Heuristic → explain what A* adds to Dijkstra in one sentence, correctly
- Geometry → explain what you buy and what you give up when exact elimination is unavailable
- Math → derive the lower bound and place all four algorithms against it
- Implementation → write the shared loop and swap the elimination rule

No two answers repeat. Sections 7–10 are the same *question* asked of four different structures, which is the thesis, not restatement — each names a different prepaid asset and a different price.
