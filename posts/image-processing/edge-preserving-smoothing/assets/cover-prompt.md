# Cover prompt — edge-preserving-smoothing

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at
`assets/cover-edge-preserving-smoothing.png`, built in the diagram-design skin by
`_cover.py` (title in Instrument Serif, the shared patch with a dot in each cell of one 3×3
window sized by the bilateral weight it gets: large on the dark side, nearly nothing across the
edge, and the bright pixel as the one tangerine element). It is the cover `manifest.md` lists; use
this prompt only if an illustrated cover is wanted instead, and then update the manifest's COVER
row to `generated`.

**Alt text for an illustrated cover:** A grid of tiles split by a sharp boundary, with large
discs on one side, tiny ones across the boundary, and one bright tile left untouched.

```
1. CONCEPT
A square mosaic of tiles split down the middle by a sharp vertical boundary:
dark tiles on the left, pale tiles on the right. Over a small block of tiles that
straddles the boundary sit round discs of different sizes, as if each tile were
being weighed: the discs on the dark tiles are large and full, the discs that
cross onto the pale side shrink almost to points. One single tile on the dark
side glows bright, and its disc is a mere speck. That bright tile is the focal
element.

2. COMPOSITION
The mosaic sits slightly left of centre, about one third across, occupying about
half the frame's height, seen straight on with a faint isometric lift. The block
of weighed tiles is at the mosaic's centre, straddling the boundary. The right
third of the frame is near-empty, holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines around every tile, flat fills with no gradients inside shapes, subtle
paper grain over the whole frame. Dark tiles in jet-black, pale tiles in silver,
discs in white-smoke on the dark side and blue-slate on the pale side.

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
