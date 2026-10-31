# Cover prompt — confidence-intervals-coverage

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-confidence-intervals-coverage.png`, built in the
diagram-design skin by `_cover.py` (title in Instrument Serif; Figure 3 reduced to its argument: the exact
coverage of the 95% Wald interval at n = 50, jagged and mostly below the nominal line, the one tangerine
element, against the Clopper–Pearson interval's, which never falls below it). It is the cover `manifest.md`
lists; use this prompt only if an illustrated cover is wanted instead, and then update the manifest's COVER
row to `generated`.

The concept is the article's intuition: a confidence procedure is a thrower whose record is 95%, and the
interval you computed is one ring still in the air. The record describes the thrower; the ring lands on
the peg or it does not.

**Alt text for an illustrated cover:** A ring-toss peg with most rings stacked around its base, two lying
beside it, and one tangerine ring still in the air above it.

```
1. CONCEPT
A ring-toss game seen from the side, like a page from an engineer's field
notebook. A single upright peg stands on a flat board. Around its base lie
many identical rings that have already landed: almost all of them have
dropped neatly over the peg and stack around it, and two lie flat on the
board beside it, having missed. One more ring hangs in mid-air above the
peg, caught in flight, and nothing about it shows whether it will land on
the peg or beside it. That airborne ring is the focal element.

2. COMPOSITION
The board runs across the lower third of the left two thirds of the frame,
the peg near its centre. The landed rings sit around the peg's base, the
two misses a little to its right. The airborne ring floats above the peg,
slightly tilted. The right third holds only the board's edge and empty
white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration in the manner of a field notebook
diagram. Fine consistent line weight, flat fills with no gradients inside
shapes, subtle paper grain over the whole frame. The board and peg in
jet-black line, the landed rings as blue-slate outlines, the board's
surface as a pale silver tint. Only the airborne ring is atomic-tangerine.

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
