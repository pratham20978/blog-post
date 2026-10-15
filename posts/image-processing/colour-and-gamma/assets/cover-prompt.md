# Cover prompt — colour-and-gamma

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-colour-and-gamma.png`, built in the
diagram-design skin by `_cover.py` (title in Instrument Serif; Figure 8's first chord, the sRGB curve
with the chord from code 40 to code 200 and the tangerine gap between the chord's 120 and the curve's
148.7). It is the cover `manifest.md` lists; use this prompt only if an illustrated cover is wanted
instead, and then update the manifest's COVER row to `generated`.

Both covers keep the locked five-colour palette, so the post's colour swatches stay in the figures and
on the social cards.

**Alt text for an illustrated cover:** A curved wooden ramp with a straight rod resting across two
points of it, and a small tangerine peg filling the gap between rod and ramp at the middle.

```
1. CONCEPT
A long curved ramp, like a smooth wooden slide that rises steeply at first
and then flattens toward the top: the curve that turns light into stored
values. A straight thin rod rests across the ramp, touching it at two points,
one low on the steep part and one high on the flatter part, so that between
those points the rod runs below the ramp's surface. At the middle of the rod
a small peg stands upright, filling the gap between the rod and the ramp
above it: the amount by which a straight average falls short of the curve.
The peg is the focal element.

2. COMPOSITION
The ramp sweeps from the lower left to the upper right, occupying the left
two thirds of the frame, seen side-on with a slight downward angle. The rod
crosses the steep lower part of the ramp to the flatter middle. The peg sits
slightly left of centre at the rod's midpoint. A faint row of square tiles,
graded from dark to light, lies along the base like a ruler. The right third
of the frame is near-empty, holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines, flat fills with no gradients inside shapes, subtle paper grain
over the whole frame. Ramp in blue-slate with a jet-black outline, the rod
in silver with a jet-black outline, the tiles stepping from jet-black
through blue-slate and silver to white-smoke, the peg filled
atomic-tangerine.

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
