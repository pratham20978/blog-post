# Cover prompt — discrete-diffusion-language-models

The published cover is the template build (`assets/cover.png`, from `_figures.py cover`): one crescent
image written in random order, shown with 16, 32, 48 and all 64 of its tokens in place. This prompt is the
alternative for an external image tool; the house-style blocks 4–8 are copied verbatim from blog-visuals'
`references/cover-prompt.md`.

```text
1. CONCEPT
A long row of small square tiles laid in a wooden tray, most of them face down and blank, a few turned
face up to show plain shades of grey. A single hand-held tile is being placed into the one empty slot of
the row, its face shading matching the tiles beside it. The face-down tiles are the hidden tokens; the
row fills one tile at a time. The tile being placed is the focal element.

2. COMPOSITION
The tray runs diagonally from lower left to upper right across the middle of the frame. The tile being
placed hovers just above its slot, one third from the right. Face-up tiles are scattered irregularly
along the row, more of them toward the left. The upper and right areas of the frame are near-empty,
holding only a soft gradient.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat fills with no internal
gradients, face-down tiles drawn with a light diagonal hatching, subtle paper grain over the whole frame.

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

Alt text: A diagonal row of tiles in a tray, most face down and hatched, with one grey tile being placed
into the last empty slot
