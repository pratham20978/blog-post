# LinkedIn image prompts — postgresql-foundations-storage-layer

An alternative to the rendered feed cards in `assets/social/`: six self-contained prompts for an
image tool. Every prompt repeats the locked sequence style in full.

## 01 — three kinds

- Narrative beat: Everything PostgreSQL keeps on disk is data, a map of the data, or the log.
- File: `linkedin-01-three-kinds.png`
- Alt text: Three stacked groups: a large block of page tiles, two thin strips beside it, and a line of dots below, with one tile highlighted.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel opening frame that introduces a database's on-disk storage as three kinds of object.

SUBJECT
A large grid of identical small square tiles fills the left and centre, standing for pages of a table. To its right stand two narrow vertical strips, one of small paired marks and one of small single marks, standing for two compact maps of those pages. Along the bottom runs a long, evenly spaced line of small dots, standing for a log.

KEY DETAILS
Exactly one tile in the grid is the single tangerine focal point. The two strips are silver and blue-slate and clearly much smaller than the grid. The dot line is jet-black and continuous. Nothing overlaps. Leave the upper right third near-empty.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

## 02 — no room

- Narrative beat: An update that cannot fit beside the old row goes to another page and must tell every index.
- File: `linkedin-02-no-room.png`
- Alt text: A full page tile with a sliver of space, a new tile far away receiving the row, and two thin lines reaching down from above to it.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing an update that did not fit on its own page.

SUBJECT
On the left, one page tile drawn as a card completely packed with thin horizontal rows, with only a hairline gap at its middle. On the right, a second, half-empty card receives one new row drawn in tangerine. From the top edge of the frame, two separate fine lines descend and both land on that new row.

KEY DETAILS
The new tangerine row is the single focal point. The packed card on the left is visibly full. The two lines from above are parallel and never cross. Leave the lower third calm.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

## 03 — two tiles

- Narrative beat: Vacuum read two pages of 7,693 because a map told it the rest were clean.
- File: `linkedin-03-two-tiles.png`
- Alt text: A very long band of tiles in which only two are open; a small reading lens rests on one of them.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame about a maintenance pass that skips almost all of a table.

SUBJECT
A single long horizontal band of many small identical closed tiles runs across the middle of the frame. Two tiles are drawn open, one near the left end and one at the far right end. A small round lens rests over the left open tile.

KEY DETAILS
The lens and its open tile form the single tangerine focal point. Every other tile is silver and identical. The band is long enough that the two open tiles look rare. Generous negative space above and below.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

## 04 — the cliff

- Narrative beat: A value one byte too big for the row leaves it and is replaced by a small pointer.
- File: `linkedin-04-the-cliff.png`
- Alt text: A row of cards growing in width that stops at an edge; past the edge, the largest card is folded into a small tab tied to a stack of slips.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame about oversized values being moved out of a row.

SUBJECT
Across the upper half, a sequence of horizontal cards each a little wider than the last, left to right, ending at a fine vertical boundary line. Just past the boundary, instead of a wider card, sits a small tab connected by one fine thread to a neat stack of six equal slips lower down, the last slip much shorter than the others.

KEY DETAILS
The small tab is the single tangerine focal point. The growing cards are blue-slate outlines. The slips are silver. The boundary line is jet-black and crisp. Leave the lower left calm.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

## 05 — one log

- Narrative beat: After a crash the page on disk was one change behind, and replaying the log brought it back.
- File: `linkedin-05-one-log.png`
- Alt text: A page tile with a faint outline and a crisp outline slightly offset, and a line of dots feeding into it from the left.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame about recovering a page from a log after a crash.

SUBJECT
In the centre, one page tile drawn twice: a faint, slightly smaller outline behind, and a crisp full outline in front, as if the page has been brought up to date. A long line of small evenly spaced dots enters from the left edge and ends exactly at the page, with the last few dots in tangerine.

KEY DETAILS
The last dots and the point where they meet the page are the single tangerine focal point. The faint outline is silver, the crisp one jet-black. No other objects. Leave the right third near-empty.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

## 06 — three readers

- Narrative beat: The same log is read by crash recovery, by the archiver and by replicas.
- File: `linkedin-06-three-readers.png`
- Alt text: One line of dots splitting into three branches, each ending at a different simple container.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel closing frame showing one log read three ways.

SUBJECT
A single horizontal line of small evenly spaced dots enters from the left and, at one third across, splits into three parallel branches going right. The top branch ends at a page tile, the middle one at a small box, and the bottom one at a second, smaller line of dots that continues off the right edge.

KEY DETAILS
The split point is the single tangerine focal point. The three branches never cross and are evenly spaced. All three containers are drawn in the same line weight. Generous space above and below the branches.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```
