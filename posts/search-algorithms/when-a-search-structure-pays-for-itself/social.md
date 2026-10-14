---
social_schema: 2
canonical_url: "https://canery.in/blogs/when-a-search-structure-pays-for-itself"
---

# Social publishing package — when-a-search-structure-pays-for-itself

## LinkedIn post

Is it worth sorting a list before you search it? Counted in comparisons on 16 keys: yes, from the 10th lookup.

A merge sort of the 16 keys costs at most 49 comparisons. After it, a successful lookup costs 3.375 instead of the scan's 8.5, so the sort is repaid after 49 / 5.125 = 9.56 lookups.

→ That number grows only like 2 log₂ n − 2. A worst-case sort of 1,048,576 keys is repaid after 38.00 lookups: the sort costs about log₂ n scans, and each lookup saves half a scan.
→ The floor of 45 comparisons for 16 keys can't be reached. A 2023 computer proof shows the worst case needs 46.
→ Writes change the answer. Inserting 50 shifts 8 keys of the sorted array, so keeping it sorted loses to plain appending once writes reach about half the work. Java's TreeMap compares 5 keys on one path and adds a red leaf; it keeps winning until writes outnumber reads by about n / (2 log₂ n), about 1,770 to one at 65,536 keys.
→ A hash map skips the search for exact keys. A range query has to look at every key, and "largest key ≤ 60" works only for integer keys, by probing 60, 59, 58 and so on.
→ 16 keys that share one hash cost CPython's dict 128 comparisons to insert. The hash map has become a list again.

Part 2 of Search Algorithms: The Price of the Skip. Every count comes from a lab you can rerun.

## LinkedIn first comment

Sort when the lookups will repay it, keep order when any query needs it, and give a hash map a keyed hash when someone else chooses the keys.

Read the full article on Canery: https://canery.in/blogs/when-a-search-structure-pays-for-itself

## Instagram caption

Is it worth sorting before you search? Swipe through the break-even, counted on 16 keys: a sort of 49 comparisons repaid by the 10th lookup, a floor of 45 that no sort can reach, a million keys repaid after about 38 lookups, an insert that shifts eight keys against one that walks a single tree path, the questions a hash map cannot answer, and 16 colliding keys that cost a hash map 128 comparisons.

Every number comes from the article's own lab.

Link in bio.

#algorithms #datastructures #computerscience #programming #java #python #softwareengineering

## Shared feed order

1. `assets/social/feed-01-sorting-pays-from-the-10th-lookup.png` — sorting 16 keys costs at most 49 comparisons and then saves 5.125 per lookup, so the lines cross at 9.56 lookups
2. `assets/social/feed-02-the-floor-is-45-the-best-is-46.png` — the information floor for sorting 16 keys is 45 comparisons, but a 2023 proof shows the worst case needs 46; merge sort's worst is 49
3. `assets/social/feed-03-the-break-even-grows-like-log-n.png` — the lookups needed to repay a worst-case merge sort grow like 2 log2 n − 2: 9.56 at 16 keys, 38.00 at 1,048,576
4. `assets/social/feed-04-insert-50.png` — inserting 50 shifts eight keys of the sorted array, while TreeMap's red-black tree compares five keys and adds one red leaf
5. `assets/social/feed-05-the-tree-absorbs-writes.png` — against plain appending and scanning, a sorted array stops paying at about one write per read; the red-black tree at about 1,770 at 65,536 keys
6. `assets/social/feed-06-what-a-hash-map-cannot-answer.png` — a hash map finds an exact key in one comparison but must scan for a range, and finds the largest key below 60 only for integers, by probing
7. `assets/social/feed-07-sixteen-collisions.png` — sixteen keys sharing one hash cost CPython's dict 128 key comparisons to insert, against 120 in a one-list model and 0 with ordinary hashes
8. `assets/social/feed-08-read-the-article.png` — the four answers of the post, and where to read it

## Instagram Story

- CTA: When does sorting pay for itself? Counted on 16 keys — tap the link.
- Link sticker label: Read the article
- Link sticker URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### Story order

1. `assets/social/story-01-repaid-by-the-10th-lookup.png` — Overlay: Sorting 16 keys is repaid by lookup 10.
2. `assets/social/story-02-eight-shifts-or-one-path.png` — Overlay: Insert 50: 8 shifts, or one tree path.
3. `assets/social/story-03-sixteen-keys-one-hash.png` — Overlay: 16 keys, one shared hash: 128 comparisons.
4. `assets/social/story-04-read-the-article.png` — Overlay: Hash map, sorted array or tree? Link below.

## Asset metadata

### feed-01-sorting-pays-from-the-10th-lookup

- File: `assets/social/feed-01-sorting-pays-from-the-10th-lookup.png`
- Title: Sorting pays for itself by the 10th lookup
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: sorting 16 keys costs at most 49 comparisons and then saves 5.125 per lookup, so the lines cross at 9.56 lookups
- Technical source: Worked example, the break-even; Figure 1
- Visual structure: lockup and counter; serif title; deck; a panel with the scan line and the sort-then-search line crossing at a tangerine point; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 08 · Sorting pays for itself by the 10th lookup. · 16 keys: sorting costs at most 49 comparisons, then every lookup costs 3.375 instead of 8.5. · scan · sort, then search · cross at 9.56 lookups · 49 · 0 to 20 lookups · Counted in comparisons. A million keys take about 38 lookups to repay it. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: Two cost lines over 20 lookups: the scan rises faster than sort-then-search, which starts at 49, and they cross at 9.56 lookups.
- Long description: Cumulative comparisons for successful lookups on part 1's 16 keys. Scanning costs 8.5 per lookup from zero. Sorting first costs at most 49 comparisons, after which each binary search costs 3.375. The lines cross at 49 / 5.125 = 9.56 lookups, so sorting is ahead from the 10th lookup. Counted in comparisons; at about a million keys the same break-even is 38.00 lookups.
- Keywords: break-even, merge sort, binary search, linear scan, amortised cost
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### feed-02-the-floor-is-45-the-best-is-46

- File: `assets/social/feed-02-the-floor-is-45-the-best-is-46.png`
- Title: No sort of 16 keys can promise fewer than 46
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the information floor for sorting 16 keys is 45 comparisons, but a 2023 proof shows the worst case needs 46; merge sort's worst is 49
- Technical source: Worked example, the sort; ledger L01–L05
- Visual structure: lockup and counter; serif title; deck; four labelled rows with their values, and a number line marking 45, 45.69, 46 and 49; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 08 · No sort of 16 keys can promise fewer than 46. · In the worst case the information floor says 45. A computer proof from 2023 says 45 is not enough. · 40 · 42 · 44 · 46 · 48 · 50 · 52 · information floor · ceil(log2 16!), cannot be reached · 45 · least possible · worst case, proved in 2023; merge insertion · 46 · merge sort, mean · over all 16! orders · 45.69 · merge sort, worst · the cautious break-even uses this · 49 · The break-even barely moves: at 46 the sort is ahead by lookup 9. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: Four sorting costs for 16 keys on a number line: the floor 45, merge sort's mean 45.69, the proven least 46, merge sort's worst 49.
- Long description: Sorting 16 keys by comparisons: the information floor, ceil(log2 16!) = 45, cannot be reached in the worst case; Stober and Weiß proved in 2023 that 46 comparisons are needed, which Ford and Johnson's merge insertion achieves. Merge sort needs 45.69 on average over all 16! orders and 49 in its worst case. With 46, sorting is still ahead from the 9th lookup.
- Keywords: comparison sorting, information-theoretic lower bound, merge insertion, Ford–Johnson, merge sort
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### feed-03-the-break-even-grows-like-log-n

- File: `assets/social/feed-03-the-break-even-grows-like-log-n.png`
- Title: A million keys repay the sort in about 38 lookups
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: the lookups needed to repay a worst-case merge sort grow like 2 log2 n − 2: 9.56 at 16 keys, 38.00 at 1,048,576
- Technical source: The math; Figure 6
- Visual structure: lockup and counter; serif title; deck; five rows of key counts with tangerine bars and values; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 08 · A million keys repay the sort in about 38 lookups. · Lookups that repay a worst-case merge sort, exact at every power of two. · keys n · lookups to repay the sort · 16 · 9.56 · 256 · 14.76 · 4,096 · 22.11 · 65,536 · 30.01 · 1,048,576 · 38.00 · The sort costs about log2 n scans, and each lookup saves half a scan. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: Bars for lookups that repay a worst-case merge sort: 9.56 at 16 keys, 14.76 at 256, 22.11 at 4,096, 30.01 at 65,536, 38.00 at a million.
- Long description: The break-even lookup count for successful lookups against a worst-case merge sort, exact at every power of two: 9.56 at 16 keys, 14.76 at 256, 22.11 at 4,096, 30.01 at 65,536 and 38.00 at 1,048,576. It grows like 2 log2 n − 2 because the sort costs about log2 n scans and each lookup saves about half a scan.
- Keywords: break-even, logarithmic growth, merge sort, binary search, linear scan
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### feed-04-insert-50

- File: `assets/social/feed-04-insert-50.png`
- Title: Insert 50: eight shifts, or one path
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: inserting 50 shifts eight keys of the sorted array, while TreeMap's red-black tree compares five keys and adds one red leaf
- Technical source: How many writes can a sorted structure absorb?; Figure 2
- Visual structure: lockup and counter; serif title; deck; the 17-slot array after the insert with the moved keys tinted; the red-black tree with the five-node path to the new leaf in blue; takeaway; footer
- Visible-text transcript: Canery.in · 04 / 08 · Insert 50: eight shifts, or one path. · The array moves every key after the slot. The red-black tree adds one red leaf. · sorted array: 4 comparisons, then 8 shifts · 3 · 9 · 14 · 21 · 28 · 35 · 42 · 47 · 50 · 53 · 61 · 68 · 74 · 79 · 85 · 91 · 97 · TreeMap: 5 comparisons, 0 rotations, 0 shifts · 3 · 9 · 14 · 21 · 28 · 35 · 42 · 47 · 50 · 53 · 61 · 68 · 74 · 79 · 85 · 91 · 97 · A sorted array loses to plain appending once writes reach about half the work. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: The sorted array after inserting 50, eight keys shifted, above TreeMap's red-black tree with the path 21, 47, 74, 61, 53 to a new red leaf 50.
- Long description: Inserting 50 into the sorted array takes 4 comparisons to find slot 8, then shifts the eight keys 53 to 97 one slot right. Inserting 50 into the red-black tree that Java's TreeMap builds from the same 16 keys compares it with 21, 47, 74, 61 and 53 and adds a red leaf under the black 53: 5 comparisons, no rotation, no colour flip, no shift.
- Keywords: sorted array, insertion, red-black tree, TreeMap, rotation
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### feed-05-the-tree-absorbs-writes

- File: `assets/social/feed-05-the-tree-absorbs-writes.png`
- Title: The tree absorbs about 1,770 writes per read
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: against plain appending and scanning, a sorted array stops paying at about one write per read; the red-black tree at about 1,770 at 65,536 keys
- Technical source: How many writes can a sorted structure absorb?; Figure 3
- Visual structure: lockup and counter; serif title; deck; three blocks of writes per read for the array and the tree at 16, 1,024 and 65,536 keys; a pricing note; takeaway; footer
- Visible-text transcript: Canery.in · 05 / 08 · The tree absorbs 1,770 writes per read. · At 65,536 keys, before plain appending wins. The sorted array absorbs 1. · writes per read at break-even, against appending · 16 keys · array · 0.42 · tree · 0.9 · 1,024 keys · array · 0.96 · tree · 40.3 · 65,536 keys · array · 1.00 · tree · 1,770.5 · a write = a shift, a store, a rotation or a flip, · priced like one comparison; lookups hit · It pays in memory instead: five references and a colour bit in every entry. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: Writes per read at break-even: array 0.42, 0.96 and 1.00, tree 0.9, 40.3 and 1,770.5, at 16, 1,024 and 65,536 keys.
- Long description: The writes a sorted structure can absorb per read before plain appending and scanning wins, with a write (shift, store, rotation or colour flip) priced like one comparison and lookups that hit: the sorted array 0.42 at 16 keys, 0.96 at 1,024 and 1.00 at 65,536; TreeMap's red-black tree with keys inserted in ascending order 0.9, 40.3 and 1,770.5. The tree pays in memory instead: five references and a colour bit per entry.
- Keywords: write amplification, sorted array, red-black tree, append-only log, RUM conjecture
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### feed-06-what-a-hash-map-cannot-answer

- File: `assets/social/feed-06-what-a-hash-map-cannot-answer.png`
- Title: What a hash map cannot answer
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: a hash map finds an exact key in one comparison but must scan for a range, and finds the largest key below 60 only for integers, by probing
- Technical source: Which questions can a hash map not answer?; Figure 4
- Visual structure: lockup and counter; serif title; deck; a three-column table of four queries for the sorted array and the hash map; takeaway; footer
- Visible-text transcript: Canery.in · 06 / 08 · What a hash map cannot answer. · It finds an exact key at once. Anything about order, it has to scan for. · query · sorted array · hash map · is 61 there? · 3 comparisons · 1 comparison, after · hashing the key · every key from 40 to 70 · 8 comparisons, · then read 5 · look at all 16 keys · largest key ≤ 60 · 4 comparisons: 53 · integers only: · probe 60 down to 53 · keys in order · read the array · sort them first · If any query needs order, keep order: an array for reads, a tree for writes. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: A table of four queries: 61's lookup, the keys from 40 to 70, the largest key up to 60 and sorted order, for a sorted array against a hash map.
- Long description: Four queries on the 16 keys. Is 61 there: 3 comparisons in the sorted array, 1 in a hash map after hashing. Every key from 40 to 70: 8 comparisons then 5 reads in the array; the hash map must look at all 16 keys. The largest key up to 60: 4 comparisons to 53 in the array; a hash map can only probe 60 down to 53, and only for integer keys. Keys in order: read the array, or sort the hash map's keys first.
- Keywords: hash map, range query, predecessor query, floor, sorted array
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### feed-07-sixteen-collisions

- File: `assets/social/feed-07-sixteen-collisions.png`
- Title: 16 colliding keys, 128 comparisons
- Platforms: Instagram feed, LinkedIn
- Role: technical
- Dimensions: 1080×1350
- Narrative beat: sixteen keys sharing one hash cost CPython's dict 128 key comparisons to insert, against 120 in a one-list model and 0 with ordinary hashes
- Technical source: What input breaks a hash map?; Figure 5
- Visual structure: lockup and counter; serif title; deck; sixteen bars of comparisons per insert, eight in tangerine; totals line; a key for the tangerine bars; takeaway; footer
- Visible-text transcript: Canery.in · 07 / 08 · 16 colliding keys, 128 comparisons. · Every new key is compared with every key before it. CPython's dict, counted. · key comparisons per insert, all 16 keys sharing one hash · 0 · 1 · 2 · 4 · 5 · 6 · 7 · 8 · 9 · 10 · 11 · 11 · 12 · 13 · 14 · 15 · total 128; one list would be 120; ordinary hashes: 0 · compared the first key twice: the probe sequence revisits it · Keyed hashes (Python's str) and tree bins (Java 8+) are the two fixes. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: Sixteen bars of key comparisons per insert, rising from 0 to 15, eight in tangerine where CPython compared the first key twice; total 128.
- Long description: Inserting 16 keys that share one hash into CPython 3.14's dict, counted by __eq__ calls: 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 11, 12, 13, 14, 15, total 128. A one-list model would cost 0 + 1 + … + 15 = 120; inserts 4 to 11 pay one extra because CPython's probe sequence returns to the first key's slot while the table is small. Keys with ordinary hashes cost 0. Keyed hashes (Python's str) and tree bins (Java 8 and later) are the fixes.
- Keywords: hash flooding, hash collision, CPython dict, open addressing, SipHash
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### feed-08-read-the-article

- File: `assets/social/feed-08-read-the-article.png`
- Title: Hash map, sorted array or tree?
- Platforms: Instagram feed, LinkedIn
- Role: cta
- Dimensions: 1080×1350
- Narrative beat: the four answers of the post, and where to read it
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; four headed items with a line and a figure each; takeaway; tangerine call to action
- Visible-text transcript: Canery.in · 08 / 08 · Hash map, sorted array or tree? · Every number counted, from part 1's 16 keys to a million, with the lab to rerun it. · sort · repaid by lookup 10 at 16 keys · after about 38 at a million · sorted array · an insert shifts half the keys · loses at about one write per read · red-black tree · an insert walks one path · about 1,770 writes per read at 65,536 · hash map · exact keys only, and keys that spread · 128 comparisons for 16 colliding · The full article: the break-even, the write share and the queries a hash refuses. · READ IT AT CANERY.IN/BLOGS/WHEN-A-SEARCH-STRUCTURE-PAYS-FOR-ITSELF
- Alt text: Four summary items: the sort's break-even, the sorted array's write limit, the red-black tree's, and the hash map's collision cost.
- Long description: A summary of the article: sorting is repaid by lookup 10 at 16 keys and after about 38 at a million; a sorted array's insert shifts half the keys and loses at about one write per read; a red-black tree's insert walks one path and absorbs about 1,770 writes per read at 65,536 keys; a hash map serves exact keys that spread, and 16 colliding keys cost it 128 comparisons. The call to action gives the article's address.
- Keywords: search structures, break-even, sorted array, red-black tree, hash map
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### story-01-repaid-by-the-10th-lookup

- File: `assets/social/story-01-repaid-by-the-10th-lookup.png`
- Title: Sorting is repaid by lookup 10
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
- Narrative beat: the 9:16 version of the break-even: 49 comparisons to sort, then 5.125 saved per lookup, crossing at 9.56
- Technical source: Worked example, the break-even; Figure 1
- Visual structure: lockup and counter; serif title; deck; the two cost lines crossing at a tangerine point; takeaway; footer
- Visible-text transcript: Canery.in · 01 / 04 · Sorting is repaid by lookup 10. · 16 keys: 49 comparisons to sort, then 5.125 saved per lookup. · scan · sort, then search · cross at 9.56 lookups · 49 · 0 to 20 lookups · Counted in comparisons, on part 1's own 16 keys. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: The scan line and the sort-then-search line, which starts at 49, crossing at 9.56 lookups on 16 keys.
- Long description: On part 1's 16 keys, sorting costs at most 49 comparisons and then saves 5.125 comparisons on every successful lookup. The scan's line and the sort-then-search line cross at 9.56 lookups, so sorting is repaid by lookup 10. Counted in comparisons.
- Keywords: break-even, sorting, binary search, linear scan
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### story-02-eight-shifts-or-one-path

- File: `assets/social/story-02-eight-shifts-or-one-path.png`
- Title: Eight shifts, or one path
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: inserting 50 shifts eight array keys, while TreeMap compares five keys on one path and rotates nothing
- Technical source: How many writes can a sorted structure absorb?; Figure 2
- Visual structure: lockup and counter; serif title; deck; part of the array after the insert; the red-black tree with the path to 50 in blue; takeaway; footer
- Visible-text transcript: Canery.in · 02 / 04 · Eight shifts, or one path. · Inserting 50 into a sorted array, and into Java's red-black TreeMap. · sorted array: 8 shifts · 28 · 35 · 42 · 47 · 50 · 53 · 61 · 68 · 74 · 79 · 85 · 91 · 97 · TreeMap: 5 comparisons, 0 rotations · 3 · 9 · 14 · 21 · 28 · 35 · 42 · 47 · 50 · 53 · 61 · 68 · 74 · 79 · 85 · 91 · 97 · The array loses once writes reach about half the work. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: Part of the sorted array after inserting 50 with eight shifted keys, above TreeMap's red-black tree with the five-node path to the new leaf.
- Long description: Inserting 50 into the sorted array shifts eight keys; inserting it into Java's TreeMap compares it with 21, 47, 74, 61 and 53 and adds a red leaf: 5 comparisons and 0 rotations. The array loses to plain appending once writes reach about half the work.
- Keywords: sorted array, red-black tree, TreeMap, insertion
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### story-03-sixteen-keys-one-hash

- File: `assets/social/story-03-sixteen-keys-one-hash.png`
- Title: 128 comparisons for 16 keys
- Platforms: Instagram Story
- Role: technical
- Dimensions: 1080×1920
- Narrative beat: sixteen keys sharing one hash make CPython's dict compare every new key with every earlier one: 128 comparisons
- Technical source: What input breaks a hash map?; Figure 5
- Visual structure: lockup and counter; serif title; deck; sixteen bars of comparisons per insert; totals line; a key for the tangerine bars; takeaway; footer
- Visible-text transcript: Canery.in · 03 / 04 · 128 comparisons for 16 keys. · When every key shares one hash, a hash map is a list again. · comparisons per insert, one shared hash · 16 inserts, 128 comparisons in CPython's dict · compared the first key twice · Fix: a keyed hash, or a tree inside the bucket. · SEARCH ALGORITHMS, PART 2 · CANERY.IN
- Alt text: Sixteen bars of comparisons per insert for keys sharing one hash, eight in tangerine, totalling 128 in CPython's dict.
- Long description: When every key shares one hash, each insert into CPython's dict compares the new key with every key already stored, and inserts 4 to 11 compare the first key twice: 128 comparisons for 16 inserts. A keyed hash or a tree inside the bucket is the fix.
- Keywords: hash flooding, hash collision, CPython dict
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself

### story-04-read-the-article

- File: `assets/social/story-04-read-the-article.png`
- Title: Hash map, sorted array or tree?
- Platforms: Instagram Story
- Role: cta
- Dimensions: 1080×1920
- Narrative beat: four takeaways and the call to action
- Technical source: Key takeaways
- Visual structure: lockup and counter; serif title; deck; a tinted panel of four numbered takeaways; takeaway; call to action
- Visible-text transcript: Canery.in · 04 / 04 · Hash map, sorted array or tree? · When each one pays for itself. · 1 · sorting is repaid by lookup 10 · 2 · writes favour the tree · 3 · order questions need order · 4 · colliding keys break hashing · The full article is on Canery. · LINK IN THE STICKER ABOVE
- Alt text: Four numbered takeaways: sorting repaid by lookup 10, writes favour the tree, order questions need order, colliding keys break hashing.
- Long description: Four takeaways from the article, numbered: sorting is repaid by lookup 10 at 16 keys; writes favour the red-black tree; questions about order need a structure that keeps order; keys that collide break a hash map. The call to action points to the link sticker.
- Keywords: search structures, sorting, red-black tree, hash map
- Canonical URL: https://canery.in/blogs/when-a-search-structure-pays-for-itself
