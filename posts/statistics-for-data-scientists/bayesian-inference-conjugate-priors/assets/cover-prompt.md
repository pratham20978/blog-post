# Cover prompt — bayesian-inference-conjugate-priors

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-bayesian-inference-conjugate-priors.png`, built in the
diagram-design skin by `_cover.py` (title in Instrument Serif; Figure 2 reduced to its argument: the trial's posterior
for vaccine efficacy after 8 of 170 cases, its 95% credible interval from 90.3% to 97.6% in tangerine, the one use). It
is the cover `manifest.md` lists; use this prompt only if an illustrated cover is wanted instead, and then update the
manifest's COVER row to `generated`.

The concept is the article's thesis: a posterior is a balance between prior weight and data. A long balance beam with a
row of small weights spread along it and a heap of marbles poured near one end.

**Alt text for an illustrated cover:** A long balance beam with small weights spread along it and a heap of marbles near
one end, one marble tangerine.

```
1. CONCEPT
A long, thin balance beam rests on a slim pivot. A row of small identical
cube weights is spread evenly along its whole length, and a heap of small
round marbles has been poured onto it near one end, so the beam tilts gently
towards the heap. One marble at the top of the heap is the focal element.

2. COMPOSITION
The beam runs across the lower middle of the frame, slightly off centre,
with the pivot below its middle and the heap to the left. The table edge
runs low across the frame. A faint regular grid recedes behind everything.
The upper third is near-empty, holding only a soft gradient.

3. TECHNIQUE
Flat editorial technical illustration with fine consistent line weight,
flat fills with no internal gradients, and subtle paper grain over the
whole frame. Weights drawn as plain cubes and marbles as plain circles with
flat pale fills; the beam and pivot as simple geometric shapes. No outlines
on the background grid.

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
