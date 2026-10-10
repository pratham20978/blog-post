# Cover prompt — image-processing-by-hand

Paste blocks 1–8 into an image tool. Blocks 4–8 are the locked house style and are
copied verbatim from `blog-visuals/references/cover-prompt.md` — do not edit them.

A deterministic fallback already exists at `assets/cover.png`, built in the
diagram-design skin (title in Instrument Serif, the four-stage motif, one tangerine
element). Use it on any day when the post matters more than the cover.

**Alt text for the cover:** Isometric flat vector technical illustration explaining data sampling and spatial analysis concepts on a light grey background. A smooth terrain is mapped into a discrete field of silver grid columns that fills the lower two-thirds of the frame, with one exceptionally tall column rising on the left. A small three-by-three square frame window hovers slightly left of centre as the sole focal element, highlighted in vibrant atomic tangerine orange. A thin blue-slate continuous contour line passes cleanly over the column tops to trace the original surface, using minimal geometric lines and generous negative space optimized for high legibility at thumbnail sizesFour connected panels in a row with the first one
highlighted, above a small three-by-three grid of weigh

---

```
1. CONCEPT
A single continuous surface of gently varying height is pressed onto a regular
grid of square posts, so that a smooth landscape becomes a field of discrete
columns. One column stands far taller than its neighbours. A small square
window, three posts by three posts, hovers just above the field — it is the
focal element, and it is the only thing carrying colour.

2. COMPOSITION
The grid of columns fills the lower two thirds, running from the left edge and
receding slightly toward the right. The single tall column sits one third from
the left. The small square window hovers above and slightly left of centre,
casting no shadow. Behind everything, the original smooth surface is implied by
a faint continuous contour line that passes over the tops of the columns. The
upper right third is near-empty, holding only white-smoke ground.

3. TECHNIQUE
Flat editorial technical illustration with isometric line work. Fine consistent
line weight throughout, flat fills with no gradients inside shapes, subtle paper
grain over the whole frame. The contour line behind is thinner than the column
outlines. No outlines on the ground plane.

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

---

## Why this metaphor

The post's argument is that a continuous signal is forced onto a grid — losing
everything between the posts — and that almost everything done afterwards is a small
window of weights sliding over what survived. The columns are the samples, the tall
one is the impulse the worked example uses, the hovering square is the kernel, and
the faint contour is the signal the operators are actually defined against but which
nobody ever gets back.
