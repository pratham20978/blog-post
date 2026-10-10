# LinkedIn image prompts — resampling-and-aliasing

Five frames, one teaching arc: shrinking and enlarging are different problems → a coarse
grid can skip the one bright tile → a fair shrink weighs every tile equally → a sharp
enlarging kernel rings → the fix is a kernel that widens with the shrink.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in
the house template with the post's own numbers. These prompts are the alternative route for a
text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — Two grids, two jobs

- Narrative beat: shrinking and enlarging are different problems
- File: `linkedin-01-two-grids.png`
- Alt text: A row of five tiles with a fine grid laid over it on one side and a coarse grid on the other, one coarse cell marked

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a five-frame sequence about
resizing images. It shows that making an image larger and making it smaller are
two different problems.

SUBJECT
A single row of five flat square tiles of different greys runs across the
middle of the frame: dark, very light, dark, light, light. Above the left half
floats a fine lattice whose openings are smaller than the tiles. Above the right
half floats a coarse lattice whose openings are wider than the tiles, so each
opening straddles parts of two or three tiles. One coarse opening is outlined as
the focal element.

KEY DETAILS
The row of tiles is the recurring object of the whole sequence and sits at the
same height it will occupy in later frames. The fine lattice reads as calm and
dense; the coarse lattice reads as sparse. The outlined coarse opening sits right
of centre and is the only coloured shape. Isometric line work, flat fills, subtle
paper grain, generous empty space at the top.

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

## 02 — The bright tile that vanishes

- Narrative beat: a coarse sampling grid can skip the one bright tile entirely
- File: `linkedin-02-bright-tile.png`
- Alt text: Five tiles with one bright tile between two sparse sampling pins, so the pins land on dark tiles and miss the bright one

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of five about resizing images. It
shows how sampling a row on a coarse grid can miss a single bright feature
completely.

SUBJECT
The same row of five flat square tiles: dark, very light, dark, light, light.
Three thin vertical pins drop onto the row from above at wide, even spacing. The
first pin lands on the first dark tile, the second on the third tile, the third
on the fifth tile, so no pin touches the very light second tile. A faint ghost
outline shows where a slightly shifted set of pins would have landed squarely on
the bright tile.

KEY DETAILS
The very light second tile is the focal element and the only coloured shape,
glowing softly as the thing the pins miss. The pins are fine and precise; the
ghost pins are drawn in a lighter dashed line. The tiles sit at the same height
and scale as in the previous frame. Isometric line work, flat fills, subtle paper
grain, generous negative space.

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

## 03 — Every tile weighed equally

- Narrative beat: a good shrink gives every input tile the same total weight
- File: `linkedin-03-equal-weights.png`
- Alt text: Five tiles each resting on its own small balance pan, four pans uneven and one row of pans all level at the same height

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of five about resizing images. It
shows the check that reveals whether a shrink treats every input tile fairly.

SUBJECT
Two rows of five small balance pans hang beneath the familiar row of tiles.
In the upper row the pans sit at uneven heights: some sag low, some float high,
one hangs empty. In the lower row all five pans hang level at exactly the same
height, like a perfectly even scale. A single horizontal line runs along the
level pans, marking their shared height.

KEY DETAILS
The level line under the lower row of pans is the focal element and the only
coloured shape. The uneven upper row is drawn in blue-slate and silver so the
contrast reads at a glance. The tile row above keeps its position and scale from
earlier frames. Isometric line work, flat fills, subtle paper grain, generous empty
space at the bottom.

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

## 04 — Ripples beside an edge

- Narrative beat: a sharp enlarging kernel rings beside edges
- File: `linkedin-04-ripples.png`
- Alt text: A smooth ramp between a low and a high plateau, with small ripples overshooting above the high side and dipping below the low side

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of five about resizing images. It
shows the ringing that a sharp enlarging method adds next to a hard edge.

SUBJECT
A long flat low plateau on the left rises steeply to a flat high plateau on the
right, like a cross-section of a step. Just past the top of the rise, the surface
overshoots in one small hump above the high plateau before settling; just before
the bottom of the rise it dips in one small trough below the low plateau. A thin
horizontal ceiling line runs above the high plateau, and the hump just touches it.

KEY DETAILS
The small overshoot hump is the focal element and the only coloured shape. The
ripples are modest, not dramatic, and the plateaus are perfectly flat elsewhere.
The profile is drawn as a clean continuous line over a faint row of the familiar
tiles. Isometric line work, flat fills, subtle paper grain, generous negative
space above.

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

## 05 — The widening lens

- Narrative beat: the fix for shrinking is a kernel that widens with the shrink
- File: `linkedin-05-widening-lens.png`
- Alt text: A wide soft lens spanning three tiles beneath one coarse grid cell, beside a narrow lens that covers only a single tile

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the closing image of a five-frame sequence about
resizing images. It shows the fix: when shrinking, the averaging window must grow
as wide as one new pixel.

SUBJECT
The familiar row of five tiles sits under one outlined coarse lattice opening
that spans parts of three tiles. Below the row, two lenses hang side by side. The
first is narrow and covers only the middle tile. The second is wide and softly
curved, spanning all three tiles under the opening, gathering them evenly.

KEY DETAILS
The wide lens is the focal element and the only coloured shape. The narrow lens
is drawn in blue-slate and silver as the contrast. The coarse opening from the
first frame returns at the same size and position, closing the sequence. Isometric
line work, flat fills, subtle paper grain, generous empty space at the top.

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
