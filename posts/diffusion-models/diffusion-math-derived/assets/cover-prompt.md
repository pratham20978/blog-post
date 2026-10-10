# Cover prompt — diffusion-math-derived

**The shipped cover is the template build, not an external generation.** `assets/cover.png` is
produced by `python3 assets/_figures.py cover` and follows the series house layout: eyebrow,
Instrument Serif title, mono subtitle, the article's motif (the teacher and student curves from
Figure 1, plus the crescent patch clean and at the worked noise level), a rule, and an italic serif
kicker. It is deterministic, on-brand, and carries real typography, which is what the
template-cover fallback in `blog-visuals/references/cover-prompt.md` is for.

The prompt below is kept so the cover can be regenerated in an external image tool if the
publication ever moves to generated covers. Blocks 4–8 are the locked house-style blocks,
reproduced verbatim; only 1–3 are written for this post.

Alt text (same string as `blog.md` and `manifest.md`): Two overlapping bell curves, the teacher's
solid and the network's dashed, with the gap between their centres marked, beside the crescent
patch clean and noised

---

```
1. CONCEPT
Two smooth, symmetric hills of exactly the same width and height, drawn as
single continuous lines, standing almost on top of each other on a flat
ground line. One is a solid line; the other is a dashed line shifted slightly
to one side. The only difference between them is where each one stands. A
short horizontal bracket spans the narrow gap between their two summits: the
gap is the subject. The idea is a measurement that can see nothing but
position, because shape has been made identical.

2. COMPOSITION
The two hills sit left of centre, their summits at about one third across and
slightly above the vertical middle, the ground line running under them across
the left two-thirds of the frame. The bracket between the summits is the focal
element and carries the single accent. Behind the hills, very faint, two wider
and lower hills overlap in the background, as if the pair had been formed from
them. The right third and the upper band are near-empty, holding only flat
background for a title overlay.

3. TECHNIQUE
Flat editorial technical illustration in the manner of a precise instrument
plate. Fine, consistent line weight for the hills and ground line, flat fills
with no internal gradients, subtle paper grain over the whole frame. The dashed
hill uses even, regular dashes. No axes, ticks or scales.

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
