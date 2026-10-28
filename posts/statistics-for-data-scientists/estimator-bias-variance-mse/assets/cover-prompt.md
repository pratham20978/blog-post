# Cover prompt — estimator-bias-variance-mse

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-estimator-bias-variance-mse.png`, built in the
diagram-design skin by `_cover.py` (title in Instrument Serif; Figure 2 reduced to its argument: the exact
distribution of the largest of five serial numbers piled against a wall at the true N = 342, the unbiased
MVUE's wider distribution dashed in slate beside it, and the true N as the one tangerine line). It is the
cover `manifest.md` lists; use this prompt only if an illustrated cover is wanted instead, and then update
the manifest's COVER row to `generated`.

The concept is the article's worked example: from five sightings scattered along a production line, judge
where the line ends. The last sighting is a floor for the end, not the end itself.

**Alt text for an illustrated cover:** A long line of identical tank hulls fading into haze; five hulls
picked out, the last short of a tangerine gate at the line's true end.

```
1. CONCEPT
A long, straight production line of identical tank hulls seen from a low
three-quarter angle, receding toward a pale haze. Most hulls are drawn as
faint outlines; five of them, at uneven intervals, are drawn solid, as if
sighted. The last solid hull sits some way before the end of the line.
Beyond it the faint hulls continue, evenly spaced, to a single gate that
marks where the line truly ends. That gate is the focal element.

2. COMPOSITION
The line runs from the lower left toward the upper right on a gentle
diagonal, so the whole length fits inside a 4:1 banner crop. The five solid
hulls are spread across the left two thirds at irregular gaps. The gate
stands right of centre, a little beyond the last solid hull. The far right
third holds only haze and the last faint outlines, and the upper band is
empty white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration in the manner of an engineering
survey drawing. Fine consistent line weight, flat fills with no gradients
inside shapes, subtle paper grain over the whole frame. Faint hulls as thin
silver outlines, the five sighted hulls in blue-slate with jet-black line
work, the line's rails in jet-black. Only the gate is atomic-tangerine.

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
