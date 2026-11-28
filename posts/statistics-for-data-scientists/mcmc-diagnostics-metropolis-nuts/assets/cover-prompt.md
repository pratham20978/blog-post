# Cover prompt — mcmc-diagnostics-metropolis-nuts

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-mcmc-diagnostics-metropolis-nuts.png`, built in the
diagram-design skin by `_cover.py` (title in Instrument Serif; Figure 2 reduced to its argument: four Metropolis chains
started far apart settle into the band that holds the central 95% of the trial's exact posterior, the band in tangerine,
the one use). It is the cover `manifest.md` lists; use this prompt only if an illustrated cover is wanted instead, and
then update the manifest's COVER row to `generated`.

The concept is the article's thesis: walkers map a landscape by where they spend their time, and every check that
compares the walkers with one another is blind to a valley none of them entered.

**Alt text for an illustrated cover:** Four walkers' footprint trails criss-cross one valley of a two-valley landscape;
the second valley, beyond a ridge, has no footprints.

```
1. CONCEPT
A gently rolling landscape seen from slightly above, with two broad valleys
separated by a low ridge. Four winding trails of small footprints wander and
cross each other inside the left valley only, densest at its floor. The
right valley is smooth and untouched. One trail of footprints is the focal
element.

2. COMPOSITION
The left valley sits left of centre and fills the lower half; the ridge runs
diagonally across the middle; the empty right valley occupies the right
third. A faint regular grid recedes behind the landscape. The upper third is
near-empty, holding only a soft gradient.

3. TECHNIQUE
Flat editorial technical illustration with fine consistent line weight,
flat fills with no internal gradients, and subtle paper grain over the
whole frame. Valleys drawn as a few flat contour bands; footprints as tiny
plain ovals in rows. No outlines on the background grid.

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
