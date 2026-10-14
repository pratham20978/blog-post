# Cover prompt — thresholding-and-segmentation

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at
`assets/cover-thresholding-and-segmentation.png`, built in the diagram-design skin by `_cover.py`
(title in Instrument Serif; Figure 6's equal-hump histogram cut once in tangerine at Otsu's
threshold, above Figure 4's last step, the patch flooded from two markers into two regions). It is
the cover `manifest.md` lists; use this prompt only if an illustrated cover is wanted instead, and
then update the manifest's COVER row to `generated`.

**Alt text for an illustrated cover:** Two soft hills of sand divided by one thin tangerine stake,
beside a small tiled pool filled from two springs into two pools of water.

```
1. CONCEPT
Two soft, rounded hills of fine sand rising from a flat plain, side by side,
with a narrow empty valley between them. One thin upright stake stands in
the bottom of the valley, the focal element, as if marking where one hill
ends and the other begins. In front of the hills lies a small square pool
laid out as a five-by-five grid of tiles, filled from two small springs, one
in a corner and one on the opposite side, so that the water settles into two
separate pools meeting along one straight line of tiles.

2. COMPOSITION
The two hills sit in the upper half of the frame, slightly left of centre,
the stake exactly between them. The tiled pool sits below and to the left of
the hills, small, seen from a gentle three-quarter angle. The right third of
the frame is near-empty, holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines, flat fills with no gradients inside shapes, subtle paper grain
over the whole frame. Hills in blue-slate with jet-black outlines, the plain
and the pool's dry tiles in silver, the two pools of water in two tints of
blue-slate, the stake filled atomic-tangerine.

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
