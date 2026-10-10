# LinkedIn image prompts — laplacian-by-hand

Six frames, one teaching arc: one operator with five jobs → what it measures →
what one bad pixel does to it → why two library stencils disagree → how σ²
turns it into a ruler → the factor each library call silently applies.

**These frames are already built** — see `linkedin-0*.png`, rendered in the
diagram-design skin with real typography and the post's own numbers. The prompts
below are the alternative route if you want the text-free illustration treatment
from an image model instead.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — One operator, five jobs

- Narrative beat: one cross-shaped stamp is the tool behind five different operations
- File: `linkedin-01-one-operator.png`
- Alt text: **Laplacian operator in image processing, shown as a cross-shaped convolution kernel above a tiled pixel field with five visual outputs representing edge ridges, parallel grooves, circular features, multiscale structures, and enclosed holes.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a six-frame sequence about
the Laplacian operator in image processing. It introduces the one tool the
whole sequence is about and hints that it has several uses.

SUBJECT
A field of small flat square tiles fills the lower half of the frame. Above
it hovers a single cross-shaped stamp: a centre square with four short arms,
drawn slightly heavier than the tiles. From the stamp, five thin lines fan
out to the upper right, each ending at a small, simple, distinct shape — a
raised ridge, a pair of parallel grooves, a circle with a ring, a stack of
three shrinking squares, and a square with a hole cut in it.

KEY DETAILS
The stamp sits one third from the left and is the focal element, the only
coloured object. The five shapes are small and evenly spaced along an arc,
drawn in fine line work with no fill. The tile field recedes slightly toward
the right. Isometric line work, flat fills, subtle paper grain, generous
empty space at the top.

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

## 02 — Neighbour average, minus centre

- Narrative beat: the operator measures how far a tile sits from the average height of its four neighbours
- File: `linkedin-02-mean-minus-centre.png`
- Alt text: **Laplacian operator measuring local intensity difference, showing a central pixel tile above the average height of its four neighboring pixels, with a dashed average line and a vertical arrow indicating the difference.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of six about the Laplacian
operator. It shows what the operator measures, in physical terms: the gap
between one tile and the average of its neighbours.

SUBJECT
Five square tiles seen in isometric view, arranged as a plus sign: one centre
tile and its four side-neighbours. The four neighbours stand at slightly
different heights. A thin horizontal line floats across them at their average
height. The centre tile stands well above that line, and a short vertical
double-ended arrow marks the gap between the line and the tile's top.

KEY DETAILS
The centre tile is the focal element and the only coloured object. The
average-height line is fine and dashed. The four neighbours are drawn with
the same line weight as the tiles in the opening frame. Everything else in
the frame is empty white-smoke ground, with the group placed slightly left of
centre. Isometric line work, flat fills, subtle paper grain.

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

## 03 — One bad pixel

- Narrative beat: a single tile standing far too high dominates the operator's response and distorts its reading of the neighbouring edge
- File: `linkedin-03-one-bad-pixel.png`
- Alt text: **Laplacian response to an impulse outlier near an image edge, showing a single abnormally tall pixel producing a strong local response while a cross-shaped Laplacian kernel overlaps the neighboring step edge.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of six about the Laplacian operator.
It shows the failure mode: one defective sample produces the largest response
in the whole field and corrupts the reading of a real edge nearby.

SUBJECT
A field of flat square tiles with a clean, straight step running across it,
so that the right half stands one level higher than the left. Two tiles to
the left of the step, one single tile stands far above everything else, a
tall thin post among flat ground. The cross-shaped stamp from the opening
frame hovers over the tile at the foot of the step, its left arm touching the
tall post.

KEY DETAILS
The tall tile is the focal element and the only coloured object. The step is
drawn cleanly with a heavier line along its top edge. The stamp is drawn in
fine line work with no fill. The upper third of the frame is near-empty.
Isometric line work, flat fills, subtle paper grain.

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

## 04 — ksize=3 is not ksize=1

- Narrative beat: two stamps that look alike touch the ground on different tiles and press four times as hard
- File: `linkedin-04-ksize-three.png`
- Alt text: **Laplacian convolution stencils compared in image processing, showing a four-neighbor cross-shaped kernel and a diagonal X-shaped kernel with different weights and footprints applied to a square pixel grid.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of six about the Laplacian
operator. It contrasts two stencils that share a name and differ in shape and
weight, which is the gap between what a library call is named and what it
does.

SUBJECT
Two stamps side by side above a flat tile field. The left stamp is the
familiar cross: a centre square with arms to the four sides. The right stamp
is an X: a centre square, visibly larger and heavier, with arms to the four
corners. Below each stamp, its footprint is pressed into the tiles, so the
reader can see that the two touch different tiles, and that the right one
presses deeper.

KEY DETAILS
The right stamp's centre is the focal element and the only coloured object.
Both stamps are drawn in the same fine line weight; the right centre square
is about twice the size of the left. The footprints are drawn as shallow
depressions with the same tile grid running through them. Isometric line
work, flat fills, subtle paper grain.

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

## 05 — Multiply by sigma squared, and sigma is a ruler

- Narrative beat: the size of the stamp that fits a shape best is the size of the shape
- File: `linkedin-05-sigma-is-a-ruler.png`
- Alt text: **Laplacian scale selection in image processing, showing three Mexican-hat Laplacian-of-Gaussian kernels of different sizes tested against a raised circular feature, with the middle-scale kernel aligning precisely with the disc’s edge.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fifth of six about the Laplacian operator.
It shows scale selection as a physical fitting: try stamps of several sizes
on one shape, and the one that fits is the one that measures it.

SUBJECT
A single round raised disc sits on a flat tile field. Above it, three ring-
shaped stamps hover in a row from small to large — each a filled centre disc
with a thin outer ring, the Mexican-hat shape seen from above. The smallest
stamp's ring falls inside the disc, the largest stamp's ring falls far
outside it, and the middle stamp's ring lands exactly on the disc's edge.

KEY DETAILS
The middle stamp is the focal element and the only coloured object. The
three stamps are aligned on one horizontal line with even spacing; the disc
below is drawn with a heavier outline. The tile field recedes slightly to the
right and the upper third is near-empty. Isometric line work, flat fills,
subtle paper grain.

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

## 06 — The library is the math, with a factor

- Narrative beat: each tool produces the same shape of result at a different size, and the sizes are the thing to know
- File: `linkedin-06-the-factor.png`
- Alt text: **Laplacian operator implementations with different response strengths, showing four identical cross-shaped stencils producing the same footprint at progressively increasing depths across a pixel grid, illustrating that response magnitude depends on the operator configuration rather than the image surface.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the closing image of a six-frame sequence
about the Laplacian operator. It shows that the different implementations
of one operator produce the same footprint at different depths, and that
the depth is a property of the tool, not of the ground.

SUBJECT
Four cross-shaped stamps in a row above a flat tile field, all the same
shape and size. Beneath each, the footprint it has pressed into the tiles:
the same cross shape, but at four clearly different depths, from a faint
impression on the left to a deep one on the right. A thin horizontal
reference line runs behind the four footprints at the depth of the
shallowest.

KEY DETAILS
The deepest footprint is the focal element and the only coloured object. The
four stamps are drawn identically, in fine line work, with even spacing. The
reference line is fine and dashed. The tile field recedes slightly toward the
right and the upper third of the frame is near-empty. Isometric line work,
flat fills, subtle paper grain.

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
