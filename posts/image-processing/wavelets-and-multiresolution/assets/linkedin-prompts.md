# LinkedIn image prompts — wavelets-and-multiresolution

Five frames, one teaching arc: one bright spot spread everywhere or kept in one place per
quarter → each tile asked how far it is from its neighbour → split, adjusted and put back
exactly → one step to the side and the pairs no longer see the edge → keep the large, shrink
the small.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the
house template with the post's own numbers. These prompts are the alternative route for a
text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — A spot spread thin, or kept in place

- Narrative beat: the Fourier transform spreads one bright pixel over every coefficient; a wavelet level keeps it in one tile per quarter
- File: `linkedin-01-a-spot-spread-thin-or-kept-in-place.png`
- Alt text: A long strip of identical grey tiles beside a square split into quarters with one tile lit in each

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a five-frame sequence about wavelet transforms of images. It contrasts a bright spot spread evenly everywhere with the same spot kept in one place per quarter.

SUBJECT
On the left, a long vertical strip of identical small grey tiles, all exactly the same shade. On the right, a square mosaic split into four quarters, with one small tile lit in each quarter at the same relative position, and every other tile plain.

KEY DETAILS
The square of quarters is the recurring object of the whole sequence. The strip tiles are an even blue-slate tint; the square's tiles are pale silver outlined in jet-black. The four lit tiles are the focal element and the only coloured shapes. Flat fills, fine outlines, subtle paper grain, generous empty space in the upper area.

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

## 02 — A row asked a question

- Narrative beat: a wavelet coefficient is the error of predicting a sample from its neighbours: flat ground costs nothing, a step costs its height
- File: `linkedin-02-a-row-asked-a-question.png`
- Alt text: A row of five tiles stepping from dark to light, with a small marker over the one pair that straddles the step

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of a five-frame sequence about wavelet transforms. It shows that predicting each tile from its neighbour costs nothing on flat ground and costs the height of a step at an edge.

SUBJECT
A horizontal row of five square tiles: three dark jet-black tiles then two pale silver tiles, a single step between the third and fourth. Beneath the row, small brackets group the tiles in pairs. Above the pair that straddles the step, a small raised block stands as tall as the step; above the flat pair, nothing.

KEY DETAILS
The row of tiles comes from the square of quarters in the previous frame, drawn at the same tile size and line weight. The raised block over the step pair is the focal element and the only coloured shape. Flat fills, fine outlines, subtle paper grain, plenty of empty space above and below.

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

## 03 — Taken apart and put back exactly

- Narrative beat: integer lifting splits a row, adjusts each half from the other, and reverses exactly with nothing lost
- File: `linkedin-03-taken-apart-and-put-back-exactly.png`
- Alt text: Two rows of tiles joined by a ladder of small steps, the same pieces reassembled exactly on the far side

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of a five-frame sequence about wavelet transforms. It shows a row of tiles being split into two halves, adjusted in small exact steps, and reassembled with nothing lost.

SUBJECT
A row of tiles at the top splits into two parallel lanes, each lane passing through two small ladder rungs that nudge it by a whole tile height, and at the bottom the lanes merge back into a row identical to the one at the top, tile for tile.

KEY DETAILS
The tiles are the same pale silver and jet-black tiles as before. The ladder rungs are thin blue-slate bars. The single tile that carried the brightest value, shown whole at the top and whole again at the bottom, is the focal element and the only coloured shape. Flat fills, fine outlines, subtle paper grain.

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

## 04 — One step to the side

- Narrative beat: moving an edge by one tile changes which pairs see it, so the decimated coefficients change
- File: `linkedin-04-one-step-to-the-side.png`
- Alt text: Two copies of a stepped row, the second shifted by one tile, with the pair markers catching the step only in the first

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of a five-frame sequence about wavelet transforms. It shows that sliding a pattern by one tile changes which pairs of tiles see its edge.

SUBJECT
Two rows of tiles stacked one above the other, each with a step from dark to light. In the lower row the step has moved one tile to the left. Fixed brackets beneath both rows group the tiles in the same pairs. In the upper row one bracket straddles the step; in the lower row the step falls between brackets and no bracket straddles it.

KEY DETAILS
The brackets are drawn in fine jet-black line and stay in exactly the same positions under both rows. The bracket that straddles the step in the upper row is the focal element and the only coloured shape. Same tiles and line weight as the earlier frames, subtle paper grain, generous empty space.

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

## 05 — Keeping the large, shrinking the small

- Narrative beat: denoising keeps the few large coefficients and shrinks the many small ones toward zero
- File: `linkedin-05-keeping-the-large-shrinking-the-small.png`
- Alt text: A field of many tiny marks and a few tall bars, with a level line below which the tiny marks flatten away

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the closing image of a five-frame sequence about wavelet transforms. It shows many small marks being flattened while a few large ones stand.

SUBJECT
A wide shallow tray holding many tiny raised marks of slightly different heights and a few tall bars. A horizontal level line crosses the tray just above the tiny marks; below it the marks are pressed flat, and the tall bars stand through it, each slightly shortened by the same small amount.

KEY DETAILS
The tray and marks are pale silver and blue-slate. The tallest bar is the focal element and the only coloured shape. Same visual world and line weight as the earlier frames: the square of quarters appears small and faint in the background corner. Flat fills, fine outlines, subtle paper grain.

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
