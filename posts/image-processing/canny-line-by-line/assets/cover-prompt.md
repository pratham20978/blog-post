# Cover prompt — canny-line-by-line

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at
`assets/cover-canny-line-by-line.png`, built in the diagram-design skin by `_cover.py`
(title in Instrument Serif, the shared patch after the series' 3×3 Gaussian shaded high =
bright, the chain hysteresis keeps at 450 and 180 drawn down column c3 as linked dots from one
tangerine seed, and the two isolated ring pixels drawn hollow and unlinked). It is the cover
`manifest.md` lists; use this prompt only if an illustrated cover is wanted instead, and then
update the manifest's COVER row to `generated`.

**Alt text for an illustrated cover:** A mosaic split by a sharp boundary, with a chain of beads
along the boundary hanging from one bright bead, and two loose beads off to one side.

```
1. CONCEPT
A square mosaic of tiles split down the middle by a sharp vertical boundary:
dark tiles on the left, pale tiles on the right. Along the boundary runs a
single chain of round beads threaded on a fine line, top to bottom, hanging
from one bright bead at the very top. Off to the left, on the dark side, two
small loose beads lie on their own, with no thread and nothing to hang from.
The bright top bead, the one the whole chain hangs from, is the focal element.

2. COMPOSITION
The mosaic sits slightly left of centre, about one third across, occupying
about half the frame's height, seen straight on with a faint isometric lift.
The chain runs down the boundary through the mosaic's middle; the two loose
beads sit low on the dark side. The right third of the frame is near-empty,
holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines around every tile, flat fills with no gradients inside shapes, subtle
paper grain over the whole frame. Dark tiles in jet-black, pale tiles in
silver, chain beads and thread in blue-slate, the loose beads drawn as open
outlines.

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
