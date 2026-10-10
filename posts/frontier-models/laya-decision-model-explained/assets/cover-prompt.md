# Cover prompt — laya-decision-model-explained

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-laya-decision-model-explained.png`,
built in the diagram-design skin by `_cover.py`. It has the title in Instrument Serif, a strip
of token tiles whose four `[MASK]` slots each drop to one bar of the route question's
probabilities (billing 0.847), and one tangerine element. It is the cover `manifest.md` lists.
Use this prompt only if an illustrated cover is wanted instead, and then update the manifest's
COVER row to `generated`.

**Alt text for an illustrated cover:** A row of flat tiles with four small open slots, each
slot dropping a thread to a weighing pan, one pan heavier than the others.

```
1. CONCEPT
A long horizontal row of flat, evenly sized tiles, like type set in a printer's
composing stick. Four of the tiles are hollow slots instead of solid tiles. From
each hollow slot a single fine thread hangs straight down to a small flat pan, so
four pans hang side by side beneath the row. One pan hangs much lower than the
other three, as if it holds most of the weight; the other three barely dip. The
heavy pan and its slot are the focal element and the only coloured objects.

2. COMPOSITION
The row of tiles runs across the upper third of the frame, from the left margin to
slightly past the centre. The four threads and pans hang in the left half, the
heavy pan lowest, at about two thirds of the frame's height. Behind everything, a
faint field of evenly spaced horizontal rules recedes, like ruled paper. The right
third of the frame is near-empty, holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight throughout, flat
fills with no gradients inside shapes, subtle paper grain over the whole frame. The
tiles are drawn as flat silver and blue-slate rectangles with thin jet-black
outlines; the threads are single hairlines.

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
