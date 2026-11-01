# Cover prompt — bootstrap-confidence-intervals

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-bootstrap-confidence-intervals.png`, built in the
diagram-design skin by `_cover.py` (title in Instrument Serif; Figure 10 reduced to its argument: the cdf of
the largest of five tank serial numbers, the bootstrap's jumping by 0.672 at 303 and stopping there, the one
tangerine element, against the true cdf running smoothly to 342). It is the cover `manifest.md` lists; use this
prompt only if an illustrated cover is wanted instead, and then update the manifest's COVER row to `generated`.

The concept is the article's thesis: the bootstrap treats the sample as the population. A scoop drawing again and
again from a tray can only bring up what the tray holds; the large stone left in the bin is the value no resample
will ever contain.

**Alt text for an illustrated cover:** A large bin of stones, a small tray holding a handful drawn from it, a
scoop dipping into the tray, and one large tangerine stone left behind in the bin.

```
1. CONCEPT
A large open bin full of rounded stones of many sizes stands at the left,
the population. A small shallow tray beside it holds a handful of stones
taken from the bin, the sample, and a small scoop is dipping into the tray
to draw from it again, leaving a few little heaps of scooped stones in a
row in front of the tray. Every stone in the tray and in the heaps is small
or middling. In the bin, half buried among the others, sits one stone far
larger than any in the tray: it was never drawn, so no scoop can bring it
up. That large stone is the focal element.

2. COMPOSITION
The bin sits in the left third, its front edge cut away so its stones are
visible, the large stone near its upper edge. The tray sits just right of
centre at a lower level, with the scoop entering it from above at an angle.
The little heaps run in a short row along the bottom edge to the right of
the tray, each the same scale as the tray's stones. A faint regular grid
recedes behind everything. The upper right third is near-empty, holding
only a soft gradient.

3. TECHNIQUE
Flat editorial technical illustration with fine consistent line weight,
flat fills with no internal gradients, and subtle paper grain over the
whole frame. Stones drawn as simple rounded outlines with flat fills; no
texture on individual stones. No outlines on the background grid.

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
