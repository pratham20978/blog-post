# LinkedIn image prompts — postgresql-foundations-memory-layer

Six frames, one teaching arc: three pools → a table that fits but is not cached → the clock
sweep → the full-page image → one budget per process → memory freed all at once.

**These frames are already built** — see `linkedin-0*.png`, rendered in the
diagram-design skin with real typography and the lab's own numbers. The prompts
below are the alternative route if you want the text-free illustration treatment
from an image model instead.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — Three pools

- Narrative beat: RAM inside a PostgreSQL server is three separate pools, not one cache
- File: `linkedin-01-three-pools.png`
- Alt text: **Flat vector technical illustration explaining PostgreSQL memory architecture on a light grey background. Three horizontal shelves of silver, rounded-square tiles representing memory pages are left-aligned, creating a clean data pool layout. In the top shelf, a single focal tile is highlighted in atomic tangerine orange and slightly raised, symbolizing a specific memory page block. The minimal, clean design uses a strict palette of jet-black, blue-slate, and orange with fine line work and generous negative space, optimized for a professional engineering presentation.**Three shelves of small square tiles stacked vertically, wide, short and medium, with one tile on the top shelf raised and coloured

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a six-frame sequence about how PostgreSQL uses memory. It establishes the recurring object of the whole sequence: a tile is a page of memory, and a shelf of tiles is a pool.

SUBJECT
Three horizontal shelves of identical small rounded-square tiles, stacked vertically with clear gaps between them. The top shelf is the widest and fully populated, three rows deep. The middle shelf is a single short row of five tiles. The bottom shelf is medium width, two rows deep, with a few empty slots. One tile in the second row of the top shelf sits slightly raised above its neighbours.

KEY DETAILS
The shelves are left-aligned at about one sixth across and fill the middle vertical third of the frame. The raised tile is the focal element and the only coloured object. A faint regular grid recedes behind the shelves. The lower quarter of the frame is empty white-smoke ground. Fine hairline outlines on every tile; no boxes drawn around the shelves — alignment implies them.

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

---

## 02 — It fits and is not cached

- Narrative beat: a table can be smaller than the pool and still be read through a tiny ring instead of being cached
- File: `linkedin-02-fits-but-not-cached.png`
- Alt text:

**Minimal technical illustration showing PostgreSQL memory limit logic on a light grey background. A long horizontal shelf of silver tiles representing a page pool spans the frame, divided by a thin, atomic tangerine orange dashed vertical gate at the one-quarter mark. Above the shelf, a short blue-slate bar sits comfortably before the gate, while a much longer jet-black bar extends past the orange gate, hovering over an empty shelf with only four tiles. The flat vector graphic uses clean hairline paths and negative space to visually contrast a table size comparison within a database memory pool.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of six about how PostgreSQL uses memory. It shows the one comparison that decides whether a table is allowed into the page pool: its size against a quarter of the pool.

SUBJECT
A single very long horizontal shelf of small rounded-square tiles runs across the middle of the frame, mostly empty. A thin dashed vertical gate stands one quarter of the way along it. Two horizontal bars float above the shelf: a short bar that ends before the gate, resting comfortably on the shelf, and a long bar that reaches well past the gate, hovering above the shelf and not touching it, with only a tiny cluster of tiles beneath its far end.

KEY DETAILS
The shelf spans the frame with a five percent margin. The gate is the focal element and the only coloured object. The short bar sits low and left; the long bar sits higher and spans two thirds of the width. The tiny cluster under the long bar is exactly four tiles. Empty ground above and below; hairline outlines; no gradients.

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

---

## 03 — The clock sweep

- Narrative beat: eviction is a clock hand lowering a small counter on each tile, and the first unpinned zero is taken
- File: `linkedin-03-the-clock-sweep.png`
- Alt text: Technical vector diagram illustrating the PostgreSQL clock sweep buffer replacement algorithm on a light grey background. Eight silver, rounded-square memory tiles are arranged in a circle around a central pivot, with a blue-slate pointer radiating outward like a clock hand. Each tile displays a stack of tiny dots representing usage counters, and one tile is held down by a jet-black peg. The focal tile, highlighted in vibrant atomic tangerine orange, has zero dots and is slightly lifted from the ring, visually demonstrating how the database selects a page block for eviction from the buffer cache.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of six about how PostgreSQL uses memory. It depicts the buffer replacement policy: a circular sweep over tiles that each carry a small tally.

SUBJECT
Eight rounded-square tiles arranged in a circle around a central pivot. Each tile carries a short vertical stack of small filled dots, between zero and five, representing a counter. A slim pointer radiates from the pivot toward one tile. One tile is held down by a small cylindrical peg pressed into its centre. The tile the pointer aims at has no dots and is slightly lifted from the ring.

KEY DETAILS
The circle fills the middle of the frame with generous margin. The lifted tile is the focal element and the only coloured object; the pointer is drawn in blue-slate. The pinned tile's peg is jet-black. Dots are tiny and evenly spaced; hairline outlines; flat fills; a faint receding grid behind.

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

---

## 04 — The whole page or the change

- Narrative beat: the first change to a page after a checkpoint logs the whole page; the second logs only the change
- File: `linkedin-04-7544-bytes-vs-176.png`
- Alt text: Technical vector illustration comparing PostgreSQL Write-Ahead Logging (WAL) before and after a checkpoint on a light grey background. Two identical silver memory tiles with notched corners are placed side by side, separated by a thin horizontal line. The left tile drops down an exceptionally long, vibrant atomic tangerine orange receipt strip containing a faint tile outline, representing a full-page write (FPW). The right tile drops down a tiny, short jet-black stub with three lines, representing a standard delta log entry. The clean flat graphic uses extreme scale to visualize database logging overhead variations.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of six about how PostgreSQL uses memory. It contrasts the size of two log entries for the same tiny change, before and after a checkpoint.

SUBJECT
Two identical small rounded-square tiles sit side by side in the upper middle of the frame, each with the same tiny notch cut from one corner to mark the same small change. Beneath each tile hangs a receipt strip. The left strip is very long, as tall as the whole frame allows, and carries a faint copy of the tile's outline inside it. The right strip is a short stub, one twentieth of the left one's length, with three thin horizontal lines.

KEY DETAILS
The two tiles are aligned at the same height, one third and two thirds across. The long strip is the focal element and the only coloured object. The short strip is jet-black outline on white-smoke. A thin horizontal rule between the tiles marks the checkpoint moment. Hairline line work; flat fills; no text on the strips.

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

---

## 05 — One budget per process

- Narrative beat: a working-memory limit applies to every operation in every process, so one query can spend it many times over
- File: `linkedin-05-work-mem-multiplies.png`
- Alt text: Flat vector technical illustration explaining PostgreSQL query memory allocation (work_mem) on a light grey background. Three identical vertical columns stand side by side, each housing two silver measuring cups filled to the same level to represent isolated memory budgets for individual query operations. In the middle column, the top cup's fill is highlighted in vibrant atomic tangerine orange as the focal point. Faint blue-slate ghosted columns recede in the background, visually demonstrating how database memory multiplies rapidly across parallel workers and multiple execution nodes.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fifth of six about how PostgreSQL uses memory. It shows one query's memory budget being copied for each operation and each parallel worker.

SUBJECT
Three identical vertical columns stand side by side, each a tall rounded rectangle drawn in hairline. Inside each column, two identical small measuring cups sit one above the other, each filled to exactly the same level. Behind the three columns, faint ghosted outlines of three more identical columns recede, suggesting more copies waiting.

KEY DETAILS
The three columns occupy the middle of the frame with equal spacing. The filled portion of the top cup in the middle column is the focal element and the only coloured object; all other cup fills are silver. The ghosted columns behind are drawn at half opacity in blue-slate. Generous margin; flat fills; a faint grid behind.

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

---

## 06 — Freed all at once

- Narrative beat: a backend releases a sort's memory by dropping the whole context that holds it, not by freeing each piece
- File: `linkedin-06-where-85-mb-went.png`
- Alt text: Flat vector technical illustration demonstrating PostgreSQL memory deallocation and context cleanup on a light grey background. A simple hierarchy tree structure of jet-black outlines features a root box at the top connecting to child nodes. At the lower right, a large branch—represented as a dense rectangular block of tiny memory tiles—is highlighted in vibrant atomic tangerine orange and shown lifting away along a dashed hairline stem. This clean, minimal graphic uses generous negative space to visually contrast clearing an entire memory context branch at once versus releasing data piece by piece.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the closing image of a six-frame sequence about how PostgreSQL uses memory. It shows memory being returned as a whole branch of a tree rather than piece by piece.

SUBJECT
A simple tree of rounded rectangles connected by thin lines: a root box at the top, four child boxes below it, and beneath one of the children a large branch that is a rectangle packed densely with tiny square tiles. That whole packed branch is lifted slightly away from the tree along its connecting stem, as if being removed in one motion, leaving the rest of the tree intact and mostly empty.

KEY DETAILS
The root sits at one quarter height, centred. The packed branch hangs at the lower right and is the focal element, the only coloured object; the tiny tiles inside it are drawn as a fine regular pattern, not individually. The stem being pulled is a dashed hairline. The remaining boxes are jet-black hairline outlines on white-smoke. Large shapes; wide margin.

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

---
