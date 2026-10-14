# Asset manifest — when-a-search-structure-pays-for-itself

Series `search-algorithms`, part 2. **Status: local draft assets ready for upload.** Upload each PNG
below to the public `media` bucket under the object key shown (the store is flat, so every key
carries the post slug and none reuses the hub's unsuffixed names), upload the lab files under their
keys, write the resulting URLs to `urls.txt` in table order (figures first, then `LAB_01`–`LAB_05`),
then run:

```bash
python3 .claude/blog-forge/scripts/fill_urls.py posts/search-algorithms/when-a-search-structure-pays-for-itself/ posts/search-algorithms/when-a-search-structure-pays-for-itself/urls.txt
python3 .claude/blog-forge/scripts/validate_post.py posts/search-algorithms/when-a-search-structure-pays-for-itself/ --publish
```

`COVER` sits in the frontmatter key `cover_image_url`, not in the body. The canery contract rejects a
non-URL there, so it must be resolved before upload.

**Lab grade:** G1 · runs anywhere — one Python file, standard library only, executed on this machine
(CPython 3.14.4; 3.10.20 and 3.12.15 reproduce every count). Nothing in the post is documented rather
than measured except what the ledger cites. Nothing needs checking before publish.

Every figure is our own work, built by `assets/_figs.py` (figures) and `assets/_cover.py` (cover) on
top of `assets/_build.py`, the toolchain copied forward from image-processing part 11 as the series
context directs; each exports `.html`, `.svg` and a 2× `.png`. Every value drawn comes from the lab's
shipped `lab/captures.json` through `assets/_data.py`, whose asserts hold each number to the one the
article prints, so a figure that disagrees with the text fails to build. The asserts caught one slip
in drafting: merge sort's mean break-even is 8.9149, which rounds to 8.91, not the 8.92 first written
in Figure 1's caption. The route gate was run per figure against its real content. The `source` route
was considered and rejected: the two candidate paper figures in `research/ledger.md` (the RUM paper's
Figure 1, CC BY-NC-ND; Crosby & Wallach's Figures 1–2, USENIX non-commercial only) have no verified
reuse basis, and our counted figures carry more. No figure is a `mermaid` route.

Every PNG was opened and checked by eye after its last render, and every `<text>` was measured in
headless Chrome with the webfonts loaded (`_overlap.py`: 0 issues on the six figures and the cover).
`lint_visuals.py`: 0 text overflows; 4 advisory arrow reports, all expected — Figure 2's "move right"
arrow is a free vector, and Figure 4's three arrows land on array cells of 50 × 32, below the lint's
60 × 40 node size. Review by eye caught and fixed: label plates cutting gaps in plotted lines (Figures
1, 3 and 6) and in a gridline (Figure 1), pale plate boxes inside shaded bands (Figures 1 and 5), step
numbers sitting on the tree's incoming edges (Figure 2), legend swatches white where the marks are
tinted (Figures 2 and 4), a missing legend entry for the new key's ring (Figure 2), a single grey
"model" swatch for two coloured model lines (Figure 6), a label clipped by a line (Figure 6), arrows
stopping short of their cells and a dead band above the legend (Figure 4), and the cover's line labels
sitting on the scan line.

Re-render: `cd assets && python3 _figs.py && python3 _cover.py && python3 _social.py && python3
../../../../.claude/blog-forge/scripts/render_social.py social/` (paths resolve from the script
directory, so the absolute-path rule for `rasterize` is already satisfied). Text check:
`python3 _overlap.py . social`.

| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover-when-a-search-structure-pays-for-itself.png | placed | template cover in the house layout, built by `_cover.py` from Figure 1 — a diagram-design build, not an external generator | — | — | cover-when-a-search-structure-pays-for-itself.png | Title card: a steep scan line and a flatter sort-then-search line cross at one tangerine point, above a row of the 16 sorted keys |
| FIG_01 | assets/fig-01-break-even-when-a-search-structure-pays-for-itself.png | chart | Q1 — cumulative comparisons counted by the lab at q = 0…20, three series on one scale | — | — | fig-01-break-even-when-a-search-structure-pays-for-itself.png | Cumulative comparisons over 20 lookups: the scan line rises 8.5 a lookup, sort-then-search starts at 49 and rises 3.375, crossing at 9.56 |
| FIG_02 | assets/fig-02-insert-50-when-a-search-structure-pays-for-itself.png | placed | Q4 — real array slots, the real TreeMap shape and colours, and the unbalanced chain as small multiples | — | — | fig-02-insert-50-when-a-search-structure-pays-for-itself.png | Inserting 50: eight array keys shift right; the red-black tree adds a red leaf via 21, 47, 74, 61, 53; unbalanced, the keys form a chain |
| FIG_03 | assets/fig-03-write-share-when-a-search-structure-pays-for-itself.png | chart | Q1 — the lab's break-even rows at seven sizes and two write prices, log axes | — | — | fig-03-write-share-when-a-search-structure-pays-for-itself.png | Writes per read at break-even by key count: the sorted array stays near 1, or 10 with cheap writes; the red-black tree climbs to 1,770 |
| FIG_04 | assets/fig-04-ordered-queries-when-a-search-structure-pays-for-itself.png | placed | Q4 — real array slots for two queries, beside a labelled 16-bucket model table | — | — | fig-04-ordered-queries-when-a-search-structure-pays-for-itself.png | Sorted array: two searches bracket 42 to 68 and the floor of 60 is 53; in 16 hash buckets the same five keys sit in scattered buckets |
| FIG_05 | assets/fig-05-hash-flooding-when-a-search-structure-pays-for-itself.png | chart | Q1 — `__eq__` calls counted in CPython's dict, against the one-list model | — | — | fig-05-hash-flooding-when-a-search-structure-pays-for-itself.png | Cumulative key comparisons for 16 keys sharing one hash: 128 in CPython's dict, 120 for one list, 0 for keys with ordinary hashes |
| FIG_06 | assets/fig-06-break-even-by-n-when-a-search-structure-pays-for-itself.png | chart | Q1 — exact counts at 17 sizes, the models drawn as labelled dotted lines, not data | — | — | fig-06-break-even-by-n-when-a-search-structure-pays-for-itself.png | Lookups that repay a merge sort, 16 to 1,048,576 keys: hits climb from 9.56 to 38.00 and misses from 4.12 to 19.00, tracking log models |

## Lab files

**Lab grade:** G1 · runs anywhere (one Python file, standard library only).

| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/when-a-search-structure-pays-for-itself/README-v1.md` | grade, provenance, run order, the E1–E3 exercise ladder, cleanup |
| LAB_02 | `lab/pays_for_itself.py` | `labs/when-a-search-structure-pays-for-itself/pays_for_itself-v1.py` | the entry point: scan, binary search, merge sort, the TreeMap port, the flooded dict, scale and writes |
| LAB_03 | `lab/captures.json` | `labs/when-a-search-structure-pays-for-itself/captures-v1.json` | the author's run, machine-readable; every figure reads it |
| LAB_04 | `lab/expected-output.txt` | `labs/when-a-search-structure-pays-for-itself/expected-output-v1.txt` | the author's run as printed |
| LAB_05 | `lab/notebook.ipynb` | `labs/when-a-search-structure-pays-for-itself/notebook-v1.ipynb` | the README with a runnable cell under each step and exercise |
| ARCHIVE | `lab-when-a-search-structure-pays-for-itself.zip` | `lab-when-a-search-structure-pays-for-itself.zip` (bucket root) | every lab file in one zip; its final URL is already written in `blog.md` |

Upload with accurate `Content-Type` (`text/markdown`, `text/x-python`, `application/json`,
`text/plain`, `application/x-ipynb+json`) and, where the upload path supports object metadata,
`Content-Disposition: attachment; filename="<name>"`.

## Series links to add

Earlier parts are named in plain text; the owner adds the links (convention since 2026-10-01; since
2026-10-09 earlier parts are named whether or not they are live). Later parts of this series are
"a later part of this series", with no number, title or link, because the hub promises none.

| Post | Status | Where it is named | Suggested target |
|---|---|---|---|
| Part 1 — *Every Search Algorithm Is the Same Algorithm* | **live** at https://canery.in/blogs/every-search-algorithm-is-the-same-algorithm | the **Level** line: "the idea from part 1 of this series that a search structure is paid for in advance" | the post root |
| Part 1 | live | series line: "Part 1, *Every Search Algorithm Is the Same Algorithm*, argued in its Intuition section" | `#intuition` |
| Part 1 | live | Worked example: "Part 1 searched these 16 sorted keys for 61" | `#worked-example` |
| Part 1 | live | Intuition: "Part 1 called that the absence of a search" | `#limitations-and-common-mistakes` |
| Part 1 | live | writes section: "finding 61 costs 10: Part 1's linear scan again" | `#worked-example` |
| Part 1 | live | Limitations: "Part 1 showed that those jumps, not the comparison count, decide speed on large arrays" | `#ordering-buys-the-skip` |

## Findings outside this post

- **The series plan's flood count of 120 is the one-list model; CPython's own dict pays 128** for the
  16 keys (its probe sequence revisits the first key's slot in the 8- and 16-slot tables). The post
  states both and why. `plan.md` is not edited.
- **The plan's "no hash can answer largest ≤ 60" is too strong for integer keys**: a hash set can probe
  60, 59, …, 53 (8 lookups), or the 31 integers of a range. The post says exactly when that works.
- **The information floor of 45 for sorting 16 keys is unreachable**: Stober & Weiß (ALENEX 2023)
  proved 46, disproving Knuth's conjecture. Any later part that quotes ⌈log₂ n!⌉ as achievable for
  small n should check this.
- **The plan's title was 70 characters**; the post's is "Hash Map, Sorted Array or Tree? When Each
  Pays for Itself" (57). The slug is the plan's.
