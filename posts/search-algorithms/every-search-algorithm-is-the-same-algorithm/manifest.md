# Asset manifest — every-search-algorithm-is-the-same-algorithm

**Status: uploaded.** All eight objects are live in the public `media` bucket and
byte-identical to the local files (verified by ETag against local MD5, 2026-09-08).

Public base URL: `https://minio.canery.in/media/`

| Placeholder | File | Object key (live) | Alt text |
|---|---|---|---|
| COVER | cover-image.png | cover-image.png | A dense grid of small marks narrowing in stages to a single highlighted mark, with the discarded ones left as faint ghosts |
| FIG_01 | fig-01-search-loop.png | fig-01-search-loop.png | Flow diagram of the universal search loop: a frontier set feeds a probe step, whose result feeds an eliminate step that shrinks the frontier and loops back |
| FIG_02 | fig-02-binary-search-trace.png | fig-02-binary-search-trace.png | Four-row trace of binary search over 16 sorted integers, the live window shrinking from all 16 to indices 8-15, then 8-10, then the found index 9 |
| FIG_03 | fig-03-elimination-rate.png | fig-03-elimination-rate.png | Grouped bar chart of candidates eliminated per probe: one each for the unordered scan, versus eight, five and two for the ordered search |
| FIG_04 | fig-04-kmp-shift.png | fig-04-kmp-shift.png | Two aligned traces of pattern AABAAC against text AABAABAABAAC, the upper rewinding the text pointer four places, the lower holding it while the pattern slides three |
| FIG_05 | fig-05-dijkstra-vs-astar.png | fig-05-dijkstra-vs-astar.png | Two identical 10 by 8 grids with the same wall, start and goal: Dijkstra shades 58 expanded cells spreading in all directions, A-star shades 33 biased toward the goal |
| FIG_06 | fig-06-hnsw-layers.png | fig-06-hnsw-layers.png | Three stacked proximity-graph layers, sparse with long edges at the top and dense with short edges at the bottom, with a greedy descent path threading down through them |
| FIG_07 | fig-07-price-of-the-skip.png | fig-07-price-of-the-skip.png | Positioning map of prepaid cost against candidates eliminated per probe, plotting linear scan at the origin and HNSW highest with a dashed marker for approximate elimination |

URLs were written into `urls.txt` in the row order above and applied with:

    python3 .claude/blog-forge/scripts/fill_urls.py posts/every-search-algorithm-is-the-same-algorithm/ urls.txt

`fill_urls.py` refuses to write if the line count does not match this manifest, or
if any listed placeholder is absent from `blog.md`.

---

## Source files kept per figure

Every figure keeps four files in `assets/`, so a correction six months from now is
an edit and a re-export rather than a redraw:

| Extension | What it is |
|---|---|
| `.mmd` | Mermaid authoring shorthand — FIG_01 only; the other six are types Mermaid cannot express |
| `.html` | The diagram-design source of truth, re-editable |
| `.svg` | Vector export, for zooming and future editing |
| `.png` | What ships, exported at @2 |

The cover was generated externally from `assets/cover-prompt.md` and is present as
`assets/cover-image.png`.

## Version suffixes — not currently used

The keys in this bucket are flat and unsuffixed (`fig-01-search-loop.png`, not
`fig-01-v1.png`), and nginx serves `/media/` with
`Cache-Control: public, max-age=31536000, immutable`.

Those two facts together are a trap. A corrected figure re-uploaded to the same key
will keep serving the old bytes from browser and CDN caches for up to a year, with
no way to flush them. So when a figure changes, **upload it under a new key** —
`fig-05-dijkstra-vs-astar-v2.png` — and update the URL in `blog.md`. Do not
overwrite in place.
