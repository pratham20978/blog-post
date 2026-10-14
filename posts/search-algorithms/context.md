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
  - **The 10×8 grid** in (row, col), never (x, y): 8 rows × 10 columns, 4-connected, unit cost, a
    wall in column 5 over rows 0–5, S (4, 1), G (4, 8), 74 open cells, 124 edges; the hub's `astar()`
    gives 58 and 33. The hub shows it only as Figure 5, so **every grid part restates it**.
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
| 2 | when-a-search-structure-pays-for-itself | ready | the break-even: lookups per build, writes per read, query types | per-probe speed and the time a comparison costs: "a later part of this series", unnamed |

Status is `planned`, `researching`, `drafting`, `ready` or `published`; parts 3–18 are `planned`
(see `plan.md`). Add a row when a part starts.

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
- **Binary search's two problems:** correctness (Bloch's 2006 overflow, told in full) and speed
  (Khuong & Morin against Brodal et al., left open: "measure on your machine").
- **Strings:** KMP traced on the shared pair, O(m + n), the text pointer never rewinds; Boyer–Moore
  is sublinear only on average (Cole ~3n, tight; Galil restores linearity). The table is defined,
  never built (Part 6).
- **Graphs, as corrected:** Dijkstra 1959 is single-pair, with no heap and no complexity analysis;
  O(m + n log n) is Fredman–Tarjan 1987; A\* (1968) needs consistency for optimal efficiency (the
  1972 correction, Dechter & Pearl 1985).
- **Geometry:** HNSW preprint 2016, TPAMI 2020; "logarithmic complexity scaling" is a design claim;
  ANN is compared on recall-versus-throughput curves, so the currency becomes correctness.
- **Hashing is outside the frame**: "the absence of a search". No part explains hash tables through
  the frame; hashing appears only as a decision (2), a limit case (5), a cheaper probe (6), a
  bucketing probe (15) and a lookup step (16, 17).

### Part 2 — When a Search Structure Pays for Itself (ready, 2026-10-14)

- **Unit.** A comparison is one call to the compare function, whatever it returns; a shift moves one
  element one slot; binary search is the hub's closed-interval prose procedure. `lab/pays_for_itself.py`
  (G1, stdlib) counts everything; `assets/_data.py` reads its `captures.json` and asserts each number.
- **Settled (16 keys).** Scan 8.5 hit, 16 miss; binary 3.375, 70/17 = 4.12. Merge sort worst 49,
  mean 2056/45 = 45.69; ⌈log₂ 16!⌉ = 45 is unreachable, S(16) = 46 (Stober & Weiß, ALENEX 2023).
  q\* = 9.56 (ahead from the 10th lookup), misses 4.12. At 2²⁰ q\* = 38.00, so ahead from the 39th:
  write "after about 38", never "by the 38th". q\* ≈ 2 log₂ n − 2 for hits, log₂ n − 1 for misses.
- **Writes.** Insert 50: array 4 comparisons and 8 shifts; TreeMap 5 comparisons, no rotation. TreeMap
  fed the 16 keys in ascending order: root 21, height 6, 60 comparisons, 10 rotations, 9 flips,
  checked against the real class (JDK 25). The unbalanced BST of the same order is a 16-deep chain:
  find 61 = 10, the hub's scan. Break-even writes per read: array → 1 (29.7% writes at 16 keys), tree
  1,770.5 at 65,536 (grows like n / (2 log₂ n); say "about 1,770").
- **Hashing.** CPython's dict: spread keys 0 comparisons to insert, 1 to find; 16 keys with one hash
  128, not the one-list 120 (the probe sequence revisits the first slot in 8- and 16-slot tables; the
  lab replays it). Fixes cited: PEP 456, siphash13 (3.11), randomisation for str/bytes only (3.3),
  JEP 180 tree bins. Range 40–70: 8 comparisons + 5 reads (TreeMap 11); floor of 60 = 53 in 4; a hash
  set scans all 16 or, for integers only, probes values.
- **Owns** the break-even and write-share formulas; later parts point here, never re-derive them.

## Decisions to preserve

- **The hub is fixed.** Its graph counts are right for its own code (flipping the tie-break gives
  21: "the count belongs to the tie-break", never a correction). Its prose trace and code differ by
  midpoint convention (3 probes against 4; Part 3 says which it traces). "Same number of comparisons"
  holds for the fixed-trip two-way form (Part 4 words it so).
- **No public promise exists.** The KMP "later L2" line is in the hub's private `outline.md` only.
  Never cite it as something the hub promised.
- **Planned anchors.** Part 4 depends on Part 3's `#the-fixed-trip-boundary-form`. Part 15 depends
  on Part 14's `#measuring-an-ann-index-honestly`. Part 14 also owns "efSearch as a bounded
  frontier". Keep those headings exact.
- **No body H1** (a `# ` line fails the validator). British spelling, as in the hub.
- **Opening furniture:** `> [!NOTE]` **Insights**, the **Level / You need / Time** line, then one
  line placing the part in the series and naming Part 1 by title.
- **Code** for a search fills the hub's `search()` skeleton; a cost model (Part 2) need not.
- **Cross-post links (owner's rule since 2026-10-01).** Name earlier parts in plain text, by title and
  part number, live or not; the owner adds links. List every spot in the manifest's *Series links to
  add* with a suggested anchor. Later parts are "a later part of this series": no number, no title.
  Hub anchors: `#the-problem`, `#worked-example`, `#intuition`, `#ordering-buys-the-skip`,
  `#precomputation-buys-the-skip`, `#a-heuristic-buys-the-skip`, `#geometry-buys-the-skip`,
  `#the-math`, `#implementation`, `#limitations-and-common-mistakes`.
- **Asset keys carry the slug** (`fig-01-…-<slug>.png`). The hub's keys are unsuffixed at the
  bucket root (`cover-image.png`, `fig-01-search-loop.png`). Never reuse those names; the bucket is
  flat and served `immutable`.
- **Toolchain.** Part 2 started it, copied from image-processing part 11: `assets/_build.py`,
  `_figs.py`, `_data.py` (reads the lab capture and asserts), `_cover.py`, `_social.py`
  (`HERE.parents[3]`), `_overlap.py`. Every later part copies forward from the newest member.
- **Product claims** need a primary source; for libraries, read the code at a tag.
- **Category** `algorithms` for every part. Proposed; confirm at Checkpoint S.

## Open threads

- **The hub's `blog.md` lost its claim keys** (0; `blog.md.bak` has 39). Not repaired; live post unaffected.
- **The hub fails the validator on its frontmatter** (no `date`, `category`, `tier`, `difficulty`,
  `reading_minutes`); pre-existing. Its ledger and manifest predate blog-forge 0.4 (warnings only).
- **The hub now sits in `posts/search-algorithms/`**, but its `assets/_social.py` still has
  `ROOT = HERE.parents[2]`; change it to `parents[3]` before re-rendering its cards. It carries no
  `series` / `series_position` (`plan.md` › *Open decisions* 2).
- **Hub ledger L28 says SODA 2003 for Brodal et al.; it is 2002.** No public error; fix if the hub reopens.
- **Every *(planning)* number in `plan.md` is provisional**; each part re-derives its own in its lab.
- **Checkpoint S is not passed for the whole cut.** The owner asked for Part 2 on 2026-10-14 and it
  was built out of the recommended order; the part list, optional wave and cuts still await approval.
- **Part 2 awaits upload and publish** (manifest: 7 images, 5 lab files, one zip). Plan corrections it
  found (flood 128 not 120, integer hash probing, the 45 floor) are in its manifest, not `plan.md`.

## Next part brief

- **Part:** not yet approved. The recommendation is **Part 3, *Why Your Binary Search Is Off by
  One*** (`why-your-binary-search-is-off-by-one`, L2, beginner). It has the highest student demand,
  a counting-only lab, and it unlocks Part 4.
- **Can assume:** the hub's loop, vocabulary and halving rule (`#ordering-buys-the-skip`), and the
  log₂ n bound (`#the-math`).
- **Must teach:** the invariant as what lies outside the half-open frontier, every variant one loop
  with a different `eliminate`; the midpoint convention behind the hub's 3 against 4; the fixed-trip
  lower_bound; a monotone predicate as the prepaid structure (`git bisect`, exponential search).
- **Must not repeat:** the overflow story (link it), the log₂ n derivation (link it), or a catalogue
  of variants. Dasdan's 2026 survey owns that; read it to avoid duplicating it.
- **Evidence still needed:** Bentley's statistic from the 2nd-edition page ("a couple of hours";
  "ninety percent ... found bugs"); Knuth §6.2.1 read directly (Mauchly 1946, Lehmer 1960, Bottenbruch
  1962); Pattis 1988; the `git-bisect` docs on the single-transition assumption; Bentley & Yao 1976.
- **Toolchain and lab:** copy Part 2's `assets/` builders and the shape of its lab (one script,
  `captures.json`, README with the ladder, `lab-cells.py`, notebook, zip).
- **Handoff:** a section headed "The fixed-trip boundary form" (`#the-fixed-trip-boundary-form`).
  It defines the (base, len) loop with no equality test, which Part 4 links.
