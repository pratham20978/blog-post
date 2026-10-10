# LinkedIn image prompts — sql-select-evaluation-joins-group-by-null

An alternative to the rendered feed cards in `assets/social/`: six self-contained prompts for an
image tool, one per feed beat. Every prompt repeats the locked sequence style in full.

## 01 — the order

- Narrative beat: A query's clauses take effect in a fixed order, and the part written first takes effect fifth.
- File: `linkedin-01-logical-order.png`
- Alt text: Eight stations stacked down one vertical line, rows of small tiles shrinking as they pass down, the fifth station highlighted

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel opening frame that introduces the fixed order in which a database query takes effect.

SUBJECT
Eight identical rounded stations are stacked one above another down a single vertical line, joined by short connectors. A wide band of small square tiles enters the top station and leaves each station narrower than it arrived, until only two tiles leave the last one.

KEY DETAILS
The fifth station is the single tangerine focal point, drawn slightly wider than the rest; the other stations are jet-black outlines on white-smoke, the connectors blue-slate and the tiles silver. The stack is centred with wide margins on both sides.

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

## 02 — the tie

- Narrative beat: Two equal results compete for the last place in a top-two list, and the route taken decides which one stays.
- File: `linkedin-02-tie.png`
- Alt text: A ranked column of five bars where the second and third are exactly equal, a dashed cut line running between them

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing a short ranked list whose cut-off falls between two exactly equal entries.

SUBJECT
Five horizontal bars are ranked from longest at the top to shortest at the bottom, left-aligned. The second and third bars are exactly the same length. A single dashed horizontal cut line runs across the column between them, so one equal bar falls above the cut and its twin below.

KEY DETAILS
The dashed cut line is the single tangerine focal point; the bars are blue-slate and silver, the two equal bars drawn with identical outlines so their sameness reads at a glance. Generous white-smoke space surrounds the column.

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

## 03 — the outer join undone

- Narrative beat: A filter applied after an outer join removes exactly the rows the join added for unmatched entries.
- File: `linkedin-03-left-join.png`
- Alt text: Paired cards joined side by side, one card whose right half is empty passing toward a narrow gate that stops it

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing an outer join's added rows being removed by a later filter.

SUBJECT
On the left, several pairs of cards are joined edge to edge, each pair a full card beside a full card. One pair is different: its right-hand card is an empty dashed outline. All the pairs travel right toward a narrow upright gate; the complete pairs pass through, the pair with the empty half is stopped in front of it.

KEY DETAILS
The pair with the empty dashed half is the single tangerine focal point; the complete pairs are jet-black outlines, the gate blue-slate. The motion reads left to right across the frame's middle third.

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

## 04 — empty groups on top

- Narrative beat: Groups with no total sort to the top of a largest-first ranking unless the sort says otherwise.
- File: `linkedin-04-nulls-first.png`
- Alt text: A largest-first column of bars topped by a few hollow dashed outlines with no length, sitting above the longest bar

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing empty groups rising to the top of a descending ranking.

SUBJECT
A column of horizontal bars is sorted from longest to shortest, top to bottom. Above the longest bar, at the very top of the column, sit a few hollow rectangles drawn only as dashed outlines with nothing inside them, as if their length were unknown. They occupy the first places in the ranking.

KEY DETAILS
The small group of hollow dashed outlines is the single tangerine focal point; the measured bars below are blue-slate and silver, decreasing in steady steps. The column sits slightly left of centre with open space to its right.

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

## 05 — one unknown in the list

- Narrative beat: One unknown value in a comparison list makes every not-in test unknown, so nothing passes.
- File: `linkedin-05-not-in.png`
- Alt text: A long row of small gates, all open except one hollow dashed gate, with a single marker unable to pass the row

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing how one unknown value in a list blocks a not-in test for everything.

SUBJECT
A long horizontal row of small identical gates stands across the frame, all of them open. One gate in the row is different: drawn only as a hollow dashed outline, neither open nor shut. A single round marker waits at the start of the row, unable to clear it, while the open gates beyond it lead nowhere.

KEY DETAILS
The hollow dashed gate is the single tangerine focal point; the open gates are jet-black outlines, the waiting marker blue-slate. The row runs across the middle of the frame with even spacing.

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

## 06 — one row per match

- Narrative beat: A join repeats a row once for every match, while an existence test keeps it once.
- File: `linkedin-06-fan-out.png`
- Alt text: One card on the left fanning out into three identical copies, beside a second card that stays a single card

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel closing frame contrasting a join that repeats a row with a test that keeps it once.

SUBJECT
On the left half, a single card splits along three short lines into three identical copies, one for each matching partner drawn as a small square beside it. On the right half, an identical card faces the same three partners but stays a single card, joined to them by one short line.

KEY DETAILS
The three repeated copies on the left are the single tangerine focal point; the cards on the right and the partner squares are jet-black and silver outlines. The two halves mirror each other across a quiet vertical gap.

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
