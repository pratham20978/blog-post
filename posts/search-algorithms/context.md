# Series context — Search Algorithms: The Price of the Skip

> Private build memory. Read before starting a member post; update only after a member passes its gate. Keep under 2,000 words.

## Series invariants

- **Audience:** CS students and working engineers who compare search algorithms on query complexity
  alone. Mostly intermediate; Part 3 is the beginner on-ramp; Parts 4, 8, 10, 12, 15, 17 advanced.
- **Shape:** hybrid. One published L2 hub (Part 1). Spokes grouped under its four families plus
  one cross-cutting part (2), each depending on the hub alone, except two ladders: 3 → 4 and
  14 → 15. Parts 16–18 are optional and await user approval.
- **Shared promise:** after the series a reader can price any search structure. They can say what
  it prepays, what that costs in build time, layout, write maintenance or accuracy, after how many
  queries it pays back, and which input breaks it.
- **The four questions.** Every part answers them for its own domain, and ends on the input that
  breaks its structure. A part that only explains a mechanism has failed the series.
- **Terminology** (fixed by the hub; never swap in synonyms):
  - **frontier**, **probe**, **eliminate**, **prepaid structure**, **exchange rate**
    (eliminations per probe), **the skip**, **buys the skip**.
  - The four prices are **build time, memory layout, maintenance under writes, accuracy**.
  - The skeleton is `search(frontier, pick, test, eliminate)`.
  - Identity: Σ Eᵢ = n. Bound: p ≥ log₂ n. A\*: f = g + h, and h = 0 is Dijkstra.
  - Admissible: h ≤ h\*. Consistent: h(u) ≤ c(u,v) + h(v).
- **Bound-based elimination, provisional wording** (Part 13 owns and may refine it; Parts 16 and 17
  restate it verbatim and must publish after 13): *a set of candidates is eliminated when a bound
  proves that none of them can beat the best answer already held.*
- **Recurring examples.** Reuse these; never invent a second instance of the same kind:
  - **16 sorted integers** `3 9 14 21 28 35 42 47 53 61 68 74 79 85 91 97`, target 61 at index 9.
    Linear scan 10 probes. The hub's prose trace is a closed-interval search, midpoint
    ⌊(lo + hi)/2⌋: 3 probes (47, 74, 61), eliminating 8, 5, 2. Its half-open `binary_search()` code
    probes 53, 79, 68, 61, which is 4. Both average 3.375, worst case 5.
  - **The KMP pair:** pattern `AABAAC`, text `AABAABAABAAC`, one match at 6. Failure table
    [0, 1, 0, 1, 2, 0].
  - **The 10×8 grid,** in (row, col) coordinates: 8 rows × 10 columns, 4-connected, unit cost.
    - A wall fills column 5 over rows 0–5. S is (4, 1) and G is (4, 8).
    - That leaves 74 open cells and 124 undirected edges.
    - Reconstructed at planning time; two independent runs of the hub's `astar()` reproduce its 58
      and 33. The hub shows the grid only as a picture in Figure 5, so **every grid part restates
      it** in two sentences and one small figure. Always (row, col), never (x, y).
  - Where a part needs more scale (Part 4's cache effects, Parts 13–15's vectors), it adds a larger
    measured instance *beside* the shared one and says why.
- **Counting conventions** (the hub's code). The goal is tested on pop. Heap entries are
  `(f, g, node)`, so ties go to **low g**. An expansion is a pop of a non-stale entry. Character
  comparisons are counted once, with the result reused; the textbook while/if KMP re-tests matches
  and costs more. Any count that depends on a convention is printed with it. A part that changes a
  convention reports the hub-convention count too.
- **Lab contract:** `plan.md` › *The lab policy*.

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | every-search-algorithm-is-the-same-algorithm | published | the frame: one loop, a prepaid structure, compare by price | none by name — no child post is promised in the published text |

Status is `planned`, `researching`, `drafting`, `ready`, or `published`. Parts 2–18 are `planned`.
Their slugs, questions and dependencies live in `plan.md` and are not duplicated here. Add a row
when work on a part begins, and update its status as it moves through the gate.

## Knowledge established

### Part 1 — Every Search Algorithm Is the Same Algorithm (published)

- **The loop and its one interesting box.** Search is frontier → probe → eliminate. The hub's
  subject is `eliminate`. It never explores `pick` (FIFO, LIFO, priority) or what the frontier costs
  in memory. Those are free ground for Parts 9 and 18.
- **The thesis sentence**, reusable verbatim: *a probe eliminates more than one candidate only when
  a prepaid structure connects the probed candidate to the others.* The structure is a fixed cost
  amortised over queries. The hub states the break-even question but never computes it; Part 2 does.
- **The math it settled.** It derived Σ Eᵢ = n, the decision-tree bound p ≥ log₂ n, binary search's
  ⌊log₂ n⌋ + 1 worst case, and f = g + h with h = 0 collapsing to Dijkstra. Link `#the-math`; do not
  re-derive.
- **Binary search has two unrelated problems.**
  - Correctness: Bloch's 2006 overflow bug and its fix, told in full.
  - Speed: Khuong & Morin found Eytzinger usually fastest at large n, contradicting Brodal,
    Fagerberg & Jacob. The hub left this deliberately unresolved: "Treat layout choice as something
    to measure on your machine, not something to look up."
- **Strings.** It traced KMP on the shared pair; the text pointer never rewinds and the bound is
  O(m + n). Boyer–Moore is sublinear only on average, Cole's ~3n worst case is tight, and Galil's
  rule restores linearity. The two are "two prices for the same commodity". KMP's table is
  *defined* but never *built*, which is left to Part 6.
- **Graph history, as corrected.**
  - Dijkstra 1959 is single-pair, uses three sets, and has no heap and no complexity analysis; its
    stated justification is storage.
  - O(m + n log n) is Fredman–Tarjan 1987.
  - A\* dates from 1968. Admissibility guarantees a least-cost path. Optimal efficiency needs
    consistency: the 1972 correction, then Dechter & Pearl 1985.
  - The grid gives 58 vs 33 expansions for the hub's code.
- **Geometry.** HNSW's preprint dates from 2016 and TPAMI from 2020. The paper's "logarithmic
  complexity scaling" is a design claim, not a theorem, and ANN is compared on recall-versus-
  throughput curves. The currency changes from build time to correctness.
- **Hashing is outside the frame.** It is "the absence of a search", and the first question is
  whether you need to search at all. No part explains hash tables *through* the frame. Hashing
  appears only as:
  - a decision (Part 2);
  - a limit case (Part 5);
  - a cheaper probe (Part 6's Rabin–Karp paragraph);
  - a bucketing probe (Part 15's LSH section);
  - a lookup step (Parts 16 and 17).

## Decisions to preserve

- **The hub is fixed.**
  - **Its graph counts are correct for its own code.** Planning found that flipping only the
    tie-break takes A\* from 33 to 21 on the same grid. Present that as "the count belongs to the
    tie-break", an extension, never a correction. The hub's Figure 5 caption already says the shape
    matters, not the count.
  - **Its binary-search prose trace and its code use different midpoints** (3 probes against 4 for
    target 61). Part 3 says which one it traces and presents the gap as a midpoint convention, never
    as a hub error.
  - **Its claim that Eytzinger and binary search "perform the same number of comparisons"** holds
    for the fixed-trip two-way form. Part 4 words it that way.
- **No public promise exists.** The KMP "later L2" line is in the hub's private `outline.md` only.
  Never cite it as something the hub promised.
- **Planned anchors.** Part 4 depends on Part 3's `#the-fixed-trip-boundary-form`. Part 15 depends
  on Part 14's `#measuring-an-ann-index-honestly`. Part 14 also owns "efSearch as a bounded
  frontier". Keep those headings exact.
- **No body H1.** `validate_post.py` fails on a `# ` line. British spelling throughout
  (neighbours, amortised, optimisation), matching the hub.
- **Opening furniture:** `> [!NOTE]` **Insights**, then the **Level / You need / Time** line, then
  one line placing the part in the series with a link to the hub.
- **Code** fills the hub's `search()` skeleton, so every snippet reads as the same loop.
- **Cross-post links.** Use the canonical URL plus a GitHub-style anchor, added in the later post:
  `https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm#ordering-buys-the-skip`.
  The hub anchors are `#the-problem`, `#worked-example`, `#intuition`, `#ordering-buys-the-skip`,
  `#precomputation-buys-the-skip`, `#a-heuristic-buys-the-skip`, `#geometry-buys-the-skip`,
  `#the-math`, `#implementation` and `#limitations-and-common-mistakes`. Never link forward to an
  unpublished part; restate the one fact instead.
- **Asset keys carry the slug** (`fig-01-…-<slug>.png`). The hub's keys are unsuffixed at the
  bucket root (`cover-image.png`, `fig-01-search-loop.png`). Never reuse those names; the bucket is
  flat and served `immutable`.
- **Toolchain.** The hub has no per-post figure toolchain; its figures are diagram-design HTML on
  the default skin, plus `_social.py`. The first member written (Part 3 under the recommended order)
  starts a `_build.py`/`_figs.py` copy from the newest post in the repo and keeps the diagram-design
  default skin. Every later part copies forward. A member one level deeper than `posts/` needs
  `HERE.parents[3]`.
- **Product claims.** Never say what a named product or library runs without a primary source; for
  libraries, read the code.
- **Category** `algorithms` for every part. Proposed; confirm at Checkpoint S.

## Open threads

- **The hub's `blog.md` has 0 claim keys; `blog.md.bak` has 39** (the key-stripping seen in
  PostgreSQL Foundations). The live post is unaffected; the local repair has not been done.
- **The hub fails the validator on its frontmatter:** missing `date`, `category`, `tier`,
  `difficulty` and `reading_minutes`; it uses `categories:`. This is pre-existing. The ledger has
  no `## Search log` and the manifest no Route column (it predates blog-forge 0.4); both are
  warnings by design.
- **The hub is not moved** into `posts/search-algorithms/` and carries no `series` /
  `series_position`. Both decisions are open in `plan.md` › *Open decisions*.
- **Hub ledger L28 dates Brodal, Fagerberg & Jacob to SODA 2003; the paper is SODA 2002**
  (confirmed in review). The published body gives no year, so there is no public error. Fix the
  ledger row only if the hub is reopened.
- **Every `(planning)` number in `plan.md` is provisional,** though a second, independent run
  re-checked most of them. The scripts lived in the session scratchpad and were not kept. Each part
  re-derives its numbers in its own lab.
- **Checkpoint S is not yet passed.** The part list, the optional wave and the adjacent cuts await
  the user.

## Next part brief

- **Part:** not yet approved. The recommendation is **Part 3, *Why Your Binary Search Is Off by
  One*** (`why-your-binary-search-is-off-by-one`, L2, beginner). It has the highest student demand,
  a counting-only lab, and it unlocks Part 4.
- **Can assume:** the hub's loop, vocabulary and halving rule (`#ordering-buys-the-skip`), and the
  log₂ n bound (`#the-math`).
- **Must teach:**
  - The invariant, stated as what lies *outside* the half-open frontier, with every variant derived
    from it as one loop with a different `eliminate`.
  - The midpoint convention that separates the hub's prose trace from its code.
  - The fixed-trip lower_bound.
  - The monotone predicate as the prepaid structure: `git bisect` and exponential search.
- **Must not repeat:** the overflow story (link it), the log₂ n derivation (link it), or a catalogue
  of variants. Dasdan's 2026 survey owns that; read it to avoid duplicating it.
- **Evidence still needed:**
  - Bentley's statistic, from the 2nd-edition page. Programmers had "a couple of hours", and
    "ninety percent of the programmers found bugs in their programs".
  - Knuth §6.2.1, read directly: Mauchly 1946, Lehmer 1960 (first correct for all n), Bottenbruch
    1962. "1946 and 1962" is Bentley's paraphrase.
  - Pattis 1988.
  - The `git-bisect` documentation on its single-transition assumption.
  - Bentley & Yao 1976.
- **Handoff:** a section headed "The fixed-trip boundary form" (`#the-fixed-trip-boundary-form`).
  It defines the (base, len) loop with no equality test, which Part 4 links.
