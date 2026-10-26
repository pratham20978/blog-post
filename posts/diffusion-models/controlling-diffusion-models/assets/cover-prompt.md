# Cover prompt — controlling-diffusion-models

The published cover is the template build (`assets/cover.png`, from `_figures.py cover`): the worked
example's guided paths beside one exact-model sample at four guidance weights. This prompt is the
alternative for an external image tool; the house-style blocks 4–8 are copied verbatim from
blog-visuals' `references/cover-prompt.md`.

```text
1. CONCEPT
A wide, gentle stream of fine particles flows down a shallow channel toward two basins carved side by
side in the ground: a small, shallow basin and a large, deep one. A single thin guide vane stands in
the stream just before the fork, angled so that it bends almost all of the flow toward the deep basin;
a few particles overshoot and pile up past its far rim, and the shallow basin is left nearly dry. The
guide vane is the focal element: control that helps the flow choose, at the price of the basin it
starves.

2. COMPOSITION
The fork and the guide vane sit one third from the left, slightly above centre. The stream enters
from the upper left edge as a broad, soft band and narrows toward the vane. The deep basin sits lower
centre, full, with a small heap of overshooting particles beyond its rim; the shallow basin sits just
left of it, nearly empty. A faint regular grid recedes behind everything. The right third of the frame
is near-empty, holding only a soft gradient.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat fills with no internal
gradients, particles drawn as small uniform dots, subtle paper grain over the whole frame. No outlines
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

Alt text: A stream of particles bent by one guide vane into a deep basin, overshooting its rim, while a
shallow basin beside it stays nearly dry
