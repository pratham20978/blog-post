# Cover prompt — gradient-domain-editing

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-gradient-domain-editing.png`, built in the
diagram-design skin by `_cover.py` (title in Instrument Serif; Figures 1 and 2 in one line: the
patch's frame of twelve known pixels around nine unknowns, a tangerine arrow labelled solve, and the
frame with the nine pixels back, 255 at the impulse). It is the cover `manifest.md` lists; use this
prompt only if an illustrated cover is wanted instead, and then update the manifest's COVER row to
`generated`.

**Alt text for an illustrated cover:** A square wooden frame with a thin sheet stretched across it,
tilting smoothly to meet a lower side, carrying a few ridges and one small tangerine peak.

```
1. CONCEPT
A square wooden frame, like an empty picture frame laid flat, with a thin
elastic sheet stretched across it like a drumhead. One side of the frame
sits lower than the other three, and the sheet tilts smoothly down to meet
it without any crease: the smooth correction that hides a seam. The sheet
carries its own raised pattern, a straight ridge running across it and one
small sharp peak, and these keep their shape while the whole sheet tilts:
the kept gradients riding on the membrane. The peak is the focal element.

2. COMPOSITION
The frame sits in the left two thirds of the image, seen from a high
three-quarter angle so the tilt of the sheet is visible. The ridge runs
diagonally across the sheet; the peak stands slightly left of the frame's
centre. The right third of the image is near-empty white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with fine line work. Thin consistent
outlines, flat fills with no gradients inside shapes, subtle paper grain
over the whole frame. The wooden frame in blue-slate with a jet-black
outline, the sheet in silver with fine jet-black contour lines showing its
gentle tilt, the ridge in a slightly darker silver, the small peak filled
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
