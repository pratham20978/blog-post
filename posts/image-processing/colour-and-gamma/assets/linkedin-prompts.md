# LinkedIn image prompts — colour-and-gamma

Five frames, one teaching arc: a staircase whose evenly looking steps are uneven in light → a rod
resting under a curved ramp, the shortfall of a straight average → one tile becoming two different
greys → two triangles of lamps around a white, where the grey weights come from → a sample tile
between two white cards, why Lab needs its white.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the
house template with the post's own numbers. These prompts are the alternative route for a
text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — The staircase of greys

- Narrative beat: a stored pixel value is a position on a perceptual scale, not an amount of light: the grey that looks halfway sends less than a fifth of white's light
- File: `linkedin-01-the-staircase-of-greys.png`
- Alt text: A staircase of grey tiles from black to white, risers short at the bottom and tall at the top, its middle step outlined in tangerine

### Prompt

```text
SCENE AND INTENDED USE
The opening frame of a five-frame sequence about how images store light. It shows that steps which look evenly spaced are not evenly spaced in light.

SUBJECT
A staircase of square tiles climbing from left to right, the tiles stepping evenly from jet-black through blue-slate and silver to white-smoke, so each looks a little lighter than the last. The risers are very short at the bottom and grow taller toward the top, so the middle tile sits only about a fifth of the way up the total height. The middle tile has an atomic-tangerine outline; it is the focal element.

KEY DETAILS
The tiles and the staircase are the recurring objects of the sequence. The staircase is seen side-on, filling the lower two thirds of the frame, with open space above.

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

## 02 — The rod under the ramp

- Narrative beat: averaging stored values is not averaging light: a straight average falls below the curve, so blurs and resizes on stored values come out darker
- File: `linkedin-02-the-rod-under-the-ramp.png`
- Alt text: A curved ramp with a straight rod resting across two of its points and a tangerine peg filling the gap between the rod's middle and the ramp

### Prompt

```text
SCENE AND INTENDED USE
The second frame of a five-frame sequence about how images store light. It shows that a straight average of two points on a curve falls short of the curve.

SUBJECT
A long curved ramp rising steeply at the lower left and flattening toward the upper right. A thin straight rod rests across the ramp, touching it at one point on the steep part and one point on the flatter part, so that between them the rod runs below the ramp's surface. At the rod's midpoint a small upright peg fills the gap between rod and ramp; the peg is the focal element.

KEY DETAILS
A row of tiles graded from dark to light lies along the base of the ramp, the same tiles as in the earlier staircase. Ramp in blue-slate with a jet-black outline, rod in silver, peg in atomic-tangerine. The right third of the frame is near-empty.

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

## 03 — One tile, two greys

- Narrative beat: a colour can be turned to grey two ways, by weighing the stored values or by weighing the light; the first comes out darker on saturated colours
- File: `linkedin-03-one-tile-two-greys.png`
- Alt text: One light tile splitting into two grey tiles, the left one darker with a tangerine outline, the right one matching the original's lightness

### Prompt

```text
SCENE AND INTENDED USE
The third frame of a five-frame sequence about how images store light. It shows one colour becoming two different greys.

SUBJECT
One large square tile at the top centre, filled with a light silver tint and slightly raised. Below it two arrows lead down to two grey tiles side by side: the left tile noticeably darker, in blue-slate, with an atomic-tangerine outline, the focal element; the right tile the same lightness as the tile above, in silver.

KEY DETAILS
The tiles keep the size and line weight of the earlier frames. Generous white-smoke space surrounds the three tiles.

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

## 04 — Three lamps and a white

- Narrative beat: the weights that make a grey are fixed by a display's three primary lights and its white; the 0.299, 0.587, 0.114 weights come from an older, larger set of lamps
- File: `linkedin-04-three-lamps-and-a-white.png`
- Alt text: Two triangles of three lamps around a white disc, a faint older wide triangle behind a smaller modern one, with one old lamp in tangerine

### Prompt

```text
SCENE AND INTENDED USE
The fourth frame of a five-frame sequence about how images store light. It shows that the weights for grey come from the three lamps a display uses and the white they make.

SUBJECT
A white-smoke disc at the centre, lit from three small lamps arranged in a triangle around it on a flat ground plane. Behind them, fainter and wider, a second, older triangle of three lamps, one of which, the top lamp, is filled atomic-tangerine as the focal element. Thin silver lines join each triangle's lamps.

KEY DETAILS
The disc and the lamps sit in the middle of the frame, seen from a gentle angle above, with open space at the top and bottom.

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

## 05 — A sample and two white cards

- Narrative beat: a Lab colour value only means something relative to its reference white; the same pixel gets different numbers under different whites
- File: `linkedin-05-a-sample-and-two-white-cards.png`
- Alt text: A tangerine-edged sample tile between two white cards under two lamps, its outline falling at a different place on each

### Prompt

```text
SCENE AND INTENDED USE
The closing frame of a five-frame sequence about how images store light. It shows that a colour is described relative to a chosen white.

SUBJECT
Two upright white-smoke cards side by side, each lit by its own small lamp from above, one lamp slightly warmer in shape and one cooler, drawn as simple discs. A single small square sample tile stands between the cards, outlined in atomic-tangerine as the focal element, with a thin silver outline of it projected onto each card at slightly different positions.

KEY DETAILS
The cards and the tile sit in the centre third of the frame with generous space around them, matching the line weight of the earlier frames.

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
