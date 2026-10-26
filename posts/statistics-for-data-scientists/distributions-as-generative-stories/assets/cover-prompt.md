# Cover prompt — distributions-as-generative-stories

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-distributions-as-generative-stories.png`,
built in the diagram-design skin by `_cover.py` (title in Instrument Serif; Greenwood and Yule's
accident counts as bars on a square-root scale, the Poisson as a dashed line and the negative
binomial as the one tangerine line). It is the cover `manifest.md` lists; use this prompt only if an
illustrated cover is wanted instead, and then update the manifest's COVER row to `generated`.

**Alt text for an illustrated cover:** A grid of square tiles seen from above at an angle, a few
small pebbles scattered across it, and one tangerine pebble falling toward the grid.

```
1. CONCEPT
A flat grid of square paving tiles, seen from above, onto which small
round pebbles have been dropped one at a time, each landing on a tile by
chance and independently of the others. Most tiles hold no pebble or one,
a few hold two, and one holds three: the counts come from the dropping, not
from any pattern in the tiles. A single pebble is still in the air above
the grid, about to land; it stands for the process that makes the data.
That falling pebble is the focal element.

2. COMPOSITION
The grid fills the left two thirds of the image, seen from a high
three-quarter angle so that its rows recede gently toward the top. The
pebbles sit scattered across the tiles with no clustering. The falling
pebble hangs above the grid, slightly right of its centre, with a faint
dotted line below it marking its path down. The right third of the image
is near-empty white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines, flat fills with no gradients inside shapes, subtle paper grain
over the whole frame. Tiles in silver with fine blue-slate joints, the
resting pebbles in jet-black, the falling pebble filled atomic-tangerine.

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
