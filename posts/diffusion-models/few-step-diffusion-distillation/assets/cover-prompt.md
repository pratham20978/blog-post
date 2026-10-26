# Cover prompt — few-step-diffusion-distillation

**The shipped cover is the template build, not an external generation.** `assets/cover.png` is
produced by `python3 assets/_figures.py cover` and follows the series house layout: eyebrow,
Instrument Serif title, mono subtitle, the article's own evidence (the exact endpoint of the path as
a step against a fitted student's ramp, from the worked example, beside crescent samples from the
exact path, one DDIM call and a one-call student), a rule, and an italic serif kicker. It is
deterministic, on-brand, and carries real typography, which is what the template-cover fallback in
`blog-visuals/references/cover-prompt.md` is for.

The prompt below is kept so the cover can be regenerated in an external image tool if the
publication ever moves to generated covers. Blocks 4–8 are the locked house-style blocks,
reproduced verbatim; only 1–3 are written for this post.

Alt text (same string as `blog.md` and `manifest.md`): The exact endpoint of the path as a step against a student's ramp, beside crescent samples from the exact path, DDIM and a student

---

```
1. CONCEPT
A low ridge divides two shallow valleys, each holding a crescent built from
square cells. A fine haze of evenly sized round dots drifts above the ridge,
and from it thin channels run down either slope, each ending on one of the
two crescents. A single long straight jump, a thin bar with small round
joints, leaps from the haze directly onto one crescent without following any
channel: the one-call student, and the single tangerine element. Right on the
crest of the ridge, two dots that sit almost touching have channels that part
toward opposite valleys.

2. COMPOSITION
The ridge runs diagonally from lower left to centre right. The dot haze sits
above its middle. One valley and its crescent lie in the lower right, the
other in the lower centre-left. The tangerine jump spans from the haze to the
lower-right crescent. The upper-left third is near-empty, holding only a soft
flat ground, so a title overlay has room.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat
fills with no internal gradients, subtle paper grain over the whole frame.
Channels drawn as clean single lines of equal weight, the ridge as one
contour line, the crescents as grids of flat square cells, the haze as evenly
sized round dots of varying density, never as a gradient.

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
