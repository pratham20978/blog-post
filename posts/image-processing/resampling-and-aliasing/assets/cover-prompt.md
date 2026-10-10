# Cover prompt — resampling-and-aliasing

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover-resampling-and-aliasing.png`, built
in the diagram-design skin by `_cover.py` (title in Instrument Serif, the row of five pixels
with a fixed-width kernel against the kernel widened to cover one new pixel, one tangerine
element). It is the cover `manifest.md` lists; use this prompt only if an illustrated cover is
wanted instead, and then update the manifest's COVER row to `generated`.

**Alt text for an illustrated cover:** A fine striped panel seen through a coarse lattice, where
the stripes turn into broad false bands except behind one wide lens that smooths them away.

```
1. CONCEPT
A flat panel covered in fine, evenly spaced parallel stripes, seen through a much
coarser lattice laid a little above it. Where the stripes show through the coarse
openings they no longer look fine: they merge into a few broad, slow, false bands
that were never on the panel — the pattern a shrunk image invents. In one part of
the frame a single wide, soft lens sits between panel and lattice; behind it the
fine stripes blur into an even tone before they reach the lattice, and no false
bands appear there. The lens is the focal element and the only coloured object.

2. COMPOSITION
The striped panel fills the lower two thirds, receding gently toward the upper
right. The coarse lattice floats just above it across the left and centre, casting
no shadow. The broad false bands are visible through the lattice on the left. The
wide lens sits slightly right of centre, over the lattice, with the calm, even
tone visible beneath it. The right third is near-empty, holding only white-smoke
ground.

3. TECHNIQUE
Flat editorial technical illustration with isometric line work. Fine consistent
line weight throughout, flat fills with no gradients inside shapes, subtle paper
grain over the whole frame. The lattice is drawn slightly heavier than the stripes;
the lens has a single clean outline.

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
