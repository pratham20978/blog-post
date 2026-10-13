# Cover prompt — the-structure-tensor

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at
`assets/cover-the-structure-tensor.png`, built in the diagram-design skin by `_cover.py`
(title in Instrument Serif, the shared patch shaded high = bright, and three of row r2's tensors
drawn over it as ellipses: the step alone at (r2, c4) as a flat line, the step with two ring
pixels at (r2, c3) as a narrow ellipse, and the window `goodFeaturesToTrack` returns, (r2, c2), as
the rounder ellipse in tangerine). It is the cover `manifest.md` lists; use this prompt only if an
illustrated cover is wanted instead, and then update the manifest's COVER row to `generated`.

**Alt text for an illustrated cover:** A mosaic split by a sharp boundary with one bright tile,
and three lens shapes across its middle row, from a flat bar to one round tangerine lens.

```
1. CONCEPT
A square mosaic of tiles split down the middle by a sharp vertical boundary:
dark tiles on the left, pale tiles on the right, and one bright tile alone on
the dark side, in the middle row. Across that middle row sit three lens shapes,
each centred on a tile: on the pale side, far right, a thin flat bar; beside it,
on the boundary's pale edge, a narrow lens; and between the bright tile and the
boundary, a rounder lens, the focal element. The three read as one shape
growing rounder as it moves toward the bright tile.

2. COMPOSITION
The mosaic sits slightly left of centre, about one third across, occupying
about half the frame's height, seen straight on with a faint isometric lift.
The three lenses run left to right along the mosaic's middle row. The right
third of the frame is near-empty, holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines around every tile, flat fills with no gradients inside shapes, subtle
paper grain over the whole frame. Dark tiles in jet-black, pale tiles in
silver, the bright tile in white-smoke, the bar and the narrow lens in
white-smoke with jet-black outlines, the round lens filled tangerine.

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
