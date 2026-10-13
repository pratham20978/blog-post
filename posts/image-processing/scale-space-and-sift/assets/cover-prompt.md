# Cover prompt — scale-space-and-sift

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at
`assets/cover-scale-space-and-sift.png`, built in the diagram-design skin by `_cover.py`
(title in Instrument Serif, and three DoG levels of the patch enlarged seven times, σ 2.016,
2.540 and 3.200, stacked obliquely along σ, blue below zero and warm grey above, with the one
sample that beats all 26 neighbours ringed in tangerine on the middle level). It is the cover
`manifest.md` lists; use this prompt only if an illustrated cover is wanted instead, and then
update the manifest's COVER row to `generated`.

**Alt text for an illustrated cover:** A grid split by a vertical step with a bright square,
and a stack of blurred copies above it with one point marked on the middle level.

```
1. CONCEPT
A square grid of tiles split by a sharp vertical boundary: dark tiles on the
left, pale tiles on the right, and on the dark side a bright square block of
tiles. Above the grid float three thin translucent sheets, stacked one over
another like panes of frosted glass, each a softer, more blurred copy of the
grid below: the bright square spreads into a soft round pool on each sheet,
and the boundary into a gentle band. On the middle sheet, at the centre of the
pool, one small ring marks a single point, the focal element.

2. COMPOSITION
The grid sits low and slightly left of centre, seen from a gentle oblique
angle, so that the three sheets above it read as a vertical stack climbing
toward the upper left. The middle sheet is the most legible. The right third
of the frame is near-empty, holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines around every tile and every sheet, flat fills with soft tonal steps
standing in for blur, no glossy gradients, subtle paper grain over the whole
frame. Dark tiles in jet-black, pale tiles in silver, the bright square in
white-smoke, the sheets in pale blue-slate tints with jet-black edges, the
single ring in tangerine.

4. PALETTE
Palette, strictly limited to these five colours and their tints:
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0,
white-smoke #f5f5f5, atomic-tangerine #eb6c36.
White-smoke dominates as the background. Jet-black and blue-slate carry
structure. Atomic-tangerine is used once, on the single focal element, and
covers less than five percent of the frame. No other hues anywhere.

5. LIGHT AND MOOD
Even, diffuse light with no dramatic shadows. Calm, precise, and technical
rather than energetic. The mood of a well-made reference book, not a
conference keynote slide.

6. FRAME
16:9 aspect ratio, 1200 by 630 pixels. Keep all meaningful content within a
5 percent margin from every edge. The composition must survive being cropped
to a square and to a 4:1 banner.

7. NEGATIVE
Do not include: any text, letters, numbers, words, labels, or captions.
No logos, watermarks, signatures, or UI chrome. No photorealism, no stock-photo
people, no 3D chrome or glossy renders, no lens flare, no drop shadows.
No colours outside the stated palette. No busy detail — large readable shapes
only, since this is viewed at thumbnail size.

8. HOUSE STYLE
House style: an editorial technical illustration for a computer-science
publication. Flat vector-like shapes with fine line work, generous negative
space, and a single point of emphasis. Restrained and geometric. It should
look hand-designed for this specific article rather than generic tech art,
and it should sit comfortably beside clean black-and-white technical diagrams
without competing with them. Composed to stay legible at 300 pixels wide.
```
