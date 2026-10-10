# Cover prompt — diffusion-samplers-and-solvers

**The shipped cover is the template build, not an external generation.** `assets/cover.png` is
produced by `python3 assets/_figures.py cover` and follows the series house layout: eyebrow,
Instrument Serif title, mono subtitle, the article's own evidence (measured error against network
calls for DDIM and a third-order solver, reaching one grey level at 100 and 16 calls, beside the
toy's exact sampling paths with DDIM's six-step chords cutting across the bend, ending on the
crescents they reach), a rule, and an italic serif kicker. It is deterministic, on-brand, and
carries real typography, which is what the template-cover fallback in
`blog-visuals/references/cover-prompt.md` is for.

The prompt below is kept so the cover can be regenerated in an external image tool if the
publication ever moves to generated covers. Blocks 4–8 are the locked house-style blocks,
reproduced verbatim; only 1–3 are written for this post.

Alt text (same string as `blog.md` and `manifest.md`): Error against network calls for DDIM and a third-order solver, beside exact sampling paths that bend once and end on crescents

---

```
1. CONCEPT
A smooth curved path runs from a fine haze of scattered dots at the left to
a clear crescent moon at the right. It is straight for most of its length
and bends once, sharply, about two thirds of the way along. A dense row of
tiny evenly spaced ticks follows the curve exactly: the thousand small
steps. Above it, a few long straight strides cover the same distance in
three or four jumps, and the one stride that cuts across the bend instead
of following it is the single tangerine element.

2. COMPOSITION
The dot haze sits at the far left, vertically centred. The path runs to the
right across the lower half of the frame, bending in the right third, and
ends on the crescent near the right edge. The long strides sit just above
the path. The upper-left third is near-empty, holding only a soft flat
ground, so a title overlay has room.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat
fills with no internal gradients, subtle paper grain over the whole frame.
The path drawn as one clean line, the ticks as short crisp strokes of equal
length, the strides as straight thin bars with small round joints; the haze
as evenly sized round dots of varying density, never as a gradient.

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
