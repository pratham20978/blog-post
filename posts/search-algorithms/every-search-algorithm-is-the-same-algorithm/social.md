---
social_schema: 2
canonical_url: "https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm"
---
# Social publishing package — every-search-algorithm-is-the-same-algorithm

## LinkedIn post

Binary search, KMP, A*, and HNSW look like four different subjects. Underneath, they run one loop: hold a frontier, probe one candidate, eliminate what the result ruled out, and repeat.

The useful difference is the elimination rule.

- Binary search prepays for sorted order, so one comparison removes the wrong half.
- KMP prepays for a pattern-overlap table, so a mismatch does not rewind the text pointer.
- A* prepays for a heuristic, so the frontier bends toward the goal.
- HNSW prepays for a proximity graph, then accepts probable rather than certain elimination.

The article’s 16-value example makes the exchange rate visible. A linear scan reaches 61 on its tenth probe. Ordered search probes 47, 74, then 61: three probes, with the frontier collapsing from 16 to 8 to 3 to found.

That speed was not created inside the loop. It was moved into sorting, preprocessing, a heuristic, a graph index, memory layout, update cost, or—in approximate search—recall.

So “which search is faster?” is incomplete. Ask what relation connects the candidates, what it cost to build, and how many queries will repay it.

## LinkedIn first comment

The loop is ordinary. The prepaid elimination rule is the algorithm.

Read the full article on Canery: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

## Instagram caption

Every search algorithm here runs the same loop: frontier → probe → eliminate → repeat.

What changes is the prepaid structure that lets one probe remove candidates it never tested. Sorted order buys binary search. An overlap table buys KMP’s forward-only text scan. A heuristic turns Dijkstra into A*. A proximity graph buys HNSW’s approximate skip.

Swipe through the 16-value binary-search trace, the real KMP mismatch, the A* equations, and the cost checklist.

Before choosing a search structure, count build cost, queries per rebuild, writes, memory, and accuracy—not just query complexity.

Read the full guide from the Story link or at canery.in/blogs/every-search-algorithm-is-the-same-algorithm.

#Algorithms #BinarySearch #KMP #AStar #HNSW

## Shared feed order

1. `assets/social/feed-01-one-loop-different-skip.png` — Binary search, KMP, A*, and HNSW share a frontier–probe–eliminate loop but use different prepaid elimination rules.
2. `assets/social/feed-02-three-probes-vs-ten.png` — Searching the article’s 16 sorted values for 61 takes ten linear probes but only three order-aware probes.
3. `assets/social/feed-03-four-ways-to-buy-the-skip.png` — Ordering, precomputation, heuristics, and geometry buy four different forms of candidate elimination.
4. `assets/social/feed-04-kmp-never-rewinds-text.png` — The KMP overlap table reuses a verified suffix so the text pointer does not move backward after a mismatch.
5. `assets/social/feed-05-dijkstra-is-a-star-zero.png` — Dijkstra and A* share the same frontier rule, with the heuristic and its conditions acting as the adjustable knob.
6. `assets/social/feed-06-the-skip-has-a-price.png` — The closing decision table connects each search structure to its query benefit and prepaid cost.

## Instagram Story

- CTA: Read the full article on Canery
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### Story order

1. `assets/social/story-01-same-loop-different-rule.png` — Overlay: Every search algorithm runs the same loop.
2. `assets/social/story-02-binary-search-three-probes.png` — Overlay: Order turns ten probes into three.
3. `assets/social/story-03-four-prices-for-the-skip.png` — Overlay: Four ways to buy the skip.
4. `assets/social/story-04-read-the-search-guide.png` — Overlay: Ask what the skip cost before using it.

## Asset metadata

### feed-01-one-loop-different-skip

- File: `assets/social/feed-01-one-loop-different-skip.png`
- Title: Every search algorithm runs the same loop
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: Binary search, KMP, A*, and HNSW differ mainly in the prepaid rule used to eliminate candidates after a probe.
- Technical source: The problem and Figure 1 universal search loop; Implementation shared search skeleton
- Visual structure: The Canery lockup and two-line hook lead into four connected loop stages, the article’s Python skeleton, four algorithm-to-structure mappings, and the central takeaway.
- Visible-text transcript: Canery; 01 / 06; Every search algorithm runs the same loop.; Binary search, KMP, A*, and HNSW change one box: how the probe eliminates candidates.; FRONTIER; candidates; PROBE; one choice; ELIMINATE; ruled out; REPEAT; smaller set; while frontier:; candidate = pick(frontier); result = test(candidate); frontier = eliminate(frontier, candidate, result); BINARY; sorted order; KMP; overlap table; A*; heuristic; HNSW; proximity graph; The loop is ordinary. The prepaid elimination rule is the algorithm.; THE PRICE OF THE SKIP · CANERY
- Alt text: Universal search loop connects frontier, probe, eliminate, and repeat, then maps four algorithms to their prepaid structures.
- Long description: Four connected boxes show the universal search cycle: maintain candidates, probe one, eliminate what the result ruled out, and repeat with a smaller frontier. A code block reproduces the article’s parameterized search skeleton, while four labels map binary search to sorted order, KMP to an overlap table, A* to a heuristic, and HNSW to a proximity graph.
- Keywords: search algorithm, frontier, elimination rule, binary search, KMP, A*, HNSW
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### feed-02-three-probes-vs-ten

- File: `assets/social/feed-02-three-probes-vs-ten.png`
- Title: Same target, three probes instead of ten
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Sorted order raises the number of candidates eliminated per probe without making an individual comparison faster.
- Technical source: Worked example; Figures 2 and 3 binary-search frontier and elimination rate
- Visual structure: The complete 16-value array highlights target 61, followed by three probe cards, a dark frontier-collapse strip, the linear-versus-ordered probe count, and the exchange-rate takeaway.
- Visible-text transcript: Canery; 02 / 06; Same target. Three probes vs ten.; Search for 61 in the article’s 16 sorted integers. Order changes eliminations—not comparison speed.; 3, 9, 14, 21, 28, 35, 42, 47, 53, 61, 68, 74, 79, 85, 91, 97; PROBE 1; a[7] = 47; eliminate indices 0–7; 8 gone; PROBE 2; a[11] = 74; eliminate indices 11–15; 5 gone; PROBE 3; a[9] = 61; target found; FOUND; 16 → 8 → 3 → FOUND; LINEAR SCAN: 10 PROBES · ORDERED SEARCH: 3 PROBES; The probes buy 8, then 5, then 2 eliminations. Sorted order raises the exchange rate.; THE PRICE OF THE SKIP · CANERY
- Alt text: Sixteen sorted values shrink to eight, then three, before binary search finds 61 on its third probe instead of the tenth.
- Long description: The target 61 is highlighted at index 9 in the article’s exact 16-value array. The ordered search first probes 47 at index 7 and eliminates indices 0 through 7, then probes 74 at index 11 and eliminates indices 11 through 15, then finds 61 at index 9. The frame compares these three probes with the ten probes needed by the linear scan for this target.
- Keywords: binary search trace, sorted array, target 61, elimination rate, search frontier
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### feed-03-four-ways-to-buy-the-skip

- File: `assets/social/feed-03-four-ways-to-buy-the-skip.png`
- Title: Four structures buy the skip
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Four algorithm families use different structures to connect one observation to candidates that were never directly tested.
- Technical source: Ordering buys the skip; Precomputation buys the skip; A heuristic buys the skip; Geometry buys the skip
- Visual structure: A two-by-two matrix compares ordering, precomputation, a heuristic, and geometry, with HNSW highlighted before a dark strip lists where the cost is prepaid.
- Visible-text transcript: Canery; 03 / 06; Four structures buy the skip.; Each lets one probe say something about candidates that were never tested directly.; 01 · ORDERING; Binary search; wrong half is impossible; exact · ≈ log₂ n probes; 02 · PRECOMPUTATION; KMP; LPS table preserves matches; exact · O(m + n); 03 · HEURISTIC; A*; f(v) = g(v) + h(v); exact with admissible h; 04 · GEOMETRY; HNSW; coarse-to-fine graph walk; approximate · tune recall; BUILD · MAINTAIN · LAY OUT · OR TRADE ACCURACY; Faster queries are never free. The price moves into build time, maintenance, memory, or recall.; THE PRICE OF THE SKIP · CANERY
- Alt text: Four-card comparison shows binary search, KMP, A*, and HNSW buying eliminations with different prepaid structures.
- Long description: Binary search uses sorted order to rule out the wrong half, KMP uses its LPS table to preserve already verified matches, and A* uses the sum of path cost and an admissible heuristic to order its frontier. HNSW instead walks a coarse-to-fine proximity graph and accepts approximate results whose recall must be measured.
- Keywords: sorted order, LPS table, A* heuristic, HNSW proximity graph, approximate search
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### feed-04-kmp-never-rewinds-text

- File: `assets/social/feed-04-kmp-never-rewinds-text.png`
- Title: KMP keeps the text pointer moving forward
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: KMP’s precomputed overlap table preserves verified characters after a mismatch instead of restarting the text scan.
- Technical source: Precomputation buys the skip; Figure 4 KMP shift trace
- Visual structure: The exact pattern and text alignment identifies the mismatch, two response cards contrast a naive rewind with the LPS-based KMP shift, and a forward arrow emphasizes the monotonic text pointer.
- Visible-text transcript: Canery; 04 / 06; KMP keeps the text pointer moving forward.; Pattern AABAAC mismatches after AABAA against text AABAABAABAAC. The overlap table saves work.; MISMATCH AFTER FIVE MATCHES; TEXT A A B A A B A A B A A C; PATTERN A A B A A C; text[5]=B · pattern[5]=C; NAIVE SHIFT; rewind the text; shift 1 · text pointer → 1; KMP SHIFT; keep i at 5; lps[4] = 2 · pattern j → 2; text positions visited: 0 · 1 · 2 · … · 11; TEXT POINTER NEVER MOVES BACKWARD; The LPS table remembers the verified suffix. That buys O(m + n) worst-case matching.; THE PRICE OF THE SKIP · CANERY
- Alt text: KMP trace keeps the text pointer at position 5 after a mismatch by resetting the pattern index with lps[4] equal to 2.
- Long description: Pattern AABAAC matches AABAA in text AABAABAABAAC before text position 5 contains B while the pattern expects C. A naive shift rewinds the text, but KMP uses `lps[4] = 2`, keeps the text pointer at position 5, and resumes from pattern index 2. The text positions advance from 0 through 11 without moving backward.
- Keywords: KMP, longest prefix suffix, string matching, AABAAC, O(m+n)
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### feed-05-dijkstra-is-a-star-zero

- File: `assets/social/feed-05-dijkstra-is-a-star-zero.png`
- Title: Dijkstra is A* with the knob at zero
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: Dijkstra and A* use the same frontier ordering equation, with the heuristic controlling direction and requiring explicit conditions.
- Technical source: A heuristic buys the skip; Figure 5; The math admissibility and consistency equations
- Visual structure: Parallel Dijkstra and A* cards compare their equations and the article’s cell counts, followed by separate cards for admissibility and consistency and a takeaway that sets the heuristic to zero.
- Visible-text transcript: Canery; 05 / 06; Dijkstra is A* with the knob at zero.; The article’s grid keeps the same cost-11 path. A heuristic changes which frontier nodes get probed.; DIJKSTRA; f(v) = g(v) + 0; 58 cells expanded; broad frontier from the start; A*; f(v) = g(v) + h(v); 33 cells expanded; heuristic biases toward the goal; SAME GRID · SAME COST-11 PATH; RESULT GUARANTEE; admissible; h(v) ≤ h*(v) · least-cost path; EXPANSION CLAIM; consistent; h(u) ≤ c(u,v) + h(v); Set h(v)=0 and A* becomes Dijkstra exactly. Do not quote stronger guarantees without conditions.; THE PRICE OF THE SKIP · CANERY
- Alt text: Dijkstra’s f equals g plus zero while A* adds h; the frame separates admissibility from heuristic consistency.
- Long description: On the article’s same cost-11 grid path, Dijkstra expands 58 cells while A* expands 33. The frame writes Dijkstra as `f(v)=g(v)+0` and A* as `f(v)=g(v)+h(v)`. It then distinguishes an admissible heuristic, which guarantees a least-cost returned path, from consistency, which is required for the stronger node-expansion optimality claim.
- Keywords: Dijkstra, A*, admissible heuristic, consistent heuristic, graph search
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### feed-06-the-skip-has-a-price

- File: `assets/social/feed-06-the-skip-has-a-price.png`
- Title: The skip always has a price
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: Choosing a search structure requires comparing its prepaid construction and maintenance cost with its workload-level query benefit.
- Technical source: Intuition; Figure 7 price of the skip; Limitations and common mistakes
- Visual structure: A three-column table maps four prepaid structures to the skip they enable and the condition to watch, followed by a five-part workload checklist and the article CTA.
- Visible-text transcript: Canery; 06 / 06; The skip always has a price.; Query complexity hides where the useful structure was built and what keeps it valid.; PREPAID STRUCTURE; THE SKIP; WHAT TO WATCH; sorted order; discard one side; sort + O(n) inserts; LPS table; reuse matched prefix; pattern preprocessing; heuristic h; bias the frontier; admissible / consistent; proximity graph; probable elimination; recall ↔ throughput; DECISION CHECK; build · queries/rebuild · writes · memory · accuracy; Before choosing a search structure, ask how many queries will repay its build and maintenance cost.; READ THE FULL GUIDE · CANERY.IN/BLOGS/EVERY-SEARCH-ALGORITHM-IS-THE-SAME-ALGORITHM
- Alt text: Decision table links sorted order, LPS, heuristics, and proximity graphs to their benefits and hidden costs.
- Long description: The closing table maps sorted order to discarding one side while paying for sorting and costly middle insertions; the LPS table to reusing a matched prefix after preprocessing; a heuristic to a guided frontier under admissibility and consistency conditions; and a proximity graph to probable elimination measured on a recall-throughput curve. A workload checklist adds build cost, queries per rebuild, writes, memory, and accuracy.
- Keywords: search structure cost, query amortization, updates, memory layout, recall throughput
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### story-01-same-loop-different-rule

- File: `assets/social/story-01-same-loop-different-rule.png`
- Title: Every search algorithm runs the same loop
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: The Story hook reduces four apparently different algorithms to the same candidate-elimination cycle.
- Technical source: The problem; Figure 1 universal search loop
- Visual structure: A large two-line hook leads into four Story-sized loop cards and a dark mapping strip for binary search, KMP, A*, and HNSW before the elimination takeaway.
- Visible-text transcript: Canery; 01 / 04; Every search algorithm runs the same loop.; What changes is how one probe can eliminate candidates it never tested.; FRONTIER; hold candidates; PROBE; test one; ELIMINATE; remove many; REPEAT; smaller frontier; binary · KMP · A* · HNSW; same loop · different prepaid elimination rule; The eliminate step is where the algorithm lives.; THE PRICE OF THE SKIP · CANERY
- Alt text: Story frame shows frontier, probe, eliminate, and repeat as the shared loop behind four search algorithms.
- Long description: The opening Story arranges the universal loop in four large cards: hold the frontier, probe one candidate, eliminate many candidates using the result, and repeat with a smaller frontier. A dark strip names binary search, KMP, A*, and HNSW as algorithms that share the loop while changing the prepaid elimination rule.
- Keywords: universal search loop, frontier, probe, eliminate, search algorithms
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### story-02-binary-search-three-probes

- File: `assets/social/story-02-binary-search-three-probes.png`
- Title: Order turns ten probes into three
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The compact Story trace demonstrates the exact eliminations that sorted order buys for target 61.
- Technical source: Worked example; Figure 2 binary-search trace
- Visual structure: The 16-value array sits above three full-width probe rows, with the target row highlighted and the frontier sequence repeated as the takeaway.
- Visible-text transcript: Canery; 02 / 04; Order turns ten probes into three.; Target 61 in the same 16-value array. Only the elimination rate changes.; 3, 9, 14, 21, 28, 35, 42, 47, 53, 61, 68, 74, 79, 85, 91, 97; 1; a[7] = 47; eliminate 0–7; 16 → 8; 2; a[11] = 74; eliminate 11–15; 8 → 3; 3; a[9] = 61; target at index 9; FOUND; 16 → 8 → 3 → found. One comparison rules out a region.; THE PRICE OF THE SKIP · CANERY
- Alt text: Story trace finds 61 after probes at values 47, 74, and 61 as the candidate frontier shrinks from 16 to eight to three.
- Long description: The Story reproduces the full sorted input and its target, then presents the three ordered probes vertically. Value 47 eliminates indices 0 through 7, value 74 eliminates indices 11 through 15, and value 61 at index 9 ends the search. The candidate sequence is 16, then 8, then 3, then found.
- Keywords: binary search Story, target 61, three probes, sorted order, frontier
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### story-03-four-prices-for-the-skip

- File: `assets/social/story-03-four-prices-for-the-skip.png`
- Title: Four ways to buy the skip
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: The Story comparison identifies the structure, mechanism, and guarantee behind each form of candidate skipping.
- Technical source: Ordering, Precomputation, A heuristic, and Geometry sections
- Visual structure: Four vertically stacked comparison rows move from exact ordering through a table and admissible heuristic to highlighted approximate geometry.
- Visible-text transcript: Canery; 03 / 04; Four ways to buy the skip.; Each structure links one probe to candidates it never touches.; ORDER; Binary search; wrong half is impossible; EXACT; TABLE; KMP; text pointer never rewinds; O(M+N); HEURISTIC; A*; f = g + h guides frontier; ADMISSIBLE; GEOMETRY; HNSW; coarse-to-fine graph; APPROX; Prepay with build, maintenance, memory—or accuracy.; THE PRICE OF THE SKIP · CANERY
- Alt text: Four Story rows compare binary search ordering, KMP tables, A* heuristics, and approximate HNSW geometry.
- Long description: Binary search uses order for exact elimination, KMP’s table keeps the text pointer moving with linear worst-case time, and A* uses an admissible heuristic to preserve a least-cost result. HNSW is highlighted as the different case: its proximity graph enables coarse-to-fine search but returns approximate neighbours that must be evaluated for recall.
- Keywords: binary search, KMP, A*, HNSW, exact versus approximate search
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm

### story-04-read-the-search-guide

- File: `assets/social/story-04-read-the-search-guide.png`
- Title: Ask what the skip cost before using it
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: The final Story converts the article’s unifying idea into a practical workload checklist and reading CTA.
- Technical source: Intuition; Limitations and common mistakes; Key takeaways
- Visual structure: A highlighted decision question leads into five workload checks, a dark article button inside the safe area, and the final comparison rule.
- Visible-text transcript: Canery; 04 / 04; Ask what the skip cost before using it.; Fast queries are a prepaid asset—not a property of the loop itself.; THE DECISION THE ARTICLE TEACHES; What relation lets one probe eliminate many candidates?; BUILD COST; QUERIES / REBUILD; WRITES; MEMORY; ACCURACY; Read the full article on Canery; use the link sticker below; Compare the whole workload, not one asymptotic bound.; LINK STICKER · READ THE ARTICLE
- Alt text: Final Story asks readers to evaluate build cost, query volume, writes, memory, and accuracy before choosing a search structure.
- Long description: The CTA frame asks which relation connects a probe to candidates it can eliminate, then supplies five workload checks: build cost, number of queries per rebuild, write frequency, memory, and accuracy requirements. It directs the reader to the complete Canery article using the Story link sticker.
- Keywords: algorithm selection, workload analysis, build cost, query volume, accuracy
- Canonical URL: https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm
