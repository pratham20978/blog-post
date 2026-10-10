# Cover prompt — training-a-diffusion-model

**The shipped cover is the template build, not an external generation.** `assets/cover.png` is
produced by `python3 assets/_figures.py cover` and follows the series house layout: eyebrow,
Instrument Serif title, mono subtitle, the article's own evidence (Stable Diffusion's log-SNR
schedule stopping at −5.4 beside its zero-SNR rescale, and the lab's crescent samples from the
same starting noise: varied in brightness when the last step is pure noise, uniform grey through
Stable Diffusion's endpoint), a rule, and an italic serif kicker. It is deterministic, on-brand, and carries real typography, which is what the
template-cover fallback in `blog-visuals/references/cover-prompt.md` is for.

The prompt below is kept so the cover can be regenerated in an external image tool if the
publication ever moves to generated covers. Blocks 4–8 are the locked house-style blocks,
reproduced verbatim; only 1–3 are written for this post.

Alt text (same string as `blog.md` and `manifest.md`): Stable Diffusion's schedule ending at log-SNR −5.4, not minus infinity, beside crescents sampled with and without a pure-noise last step

---

```
1. CONCEPT
A long staircase of thin slabs descends from a clear crescent moon at the
top left into a fine haze of scattered dots at the bottom right: each step
down holds less of the crescent and more of the haze. The staircase should
reach the haze completely, but its last step stops short, and a faint ghost
of the crescent still shows through it. That last, unfinished step is the
single tangerine element.

2. COMPOSITION
The crescent sits in the upper-left third. The staircase runs diagonally
down to the right, ending at about two thirds across and two thirds down.
The dot haze fills the lower right corner and fades toward the centre. The
upper-right third is near-empty, holding only a soft flat ground, so a
title overlay has room.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat
fills with no internal gradients, subtle paper grain over the whole frame.
Steps drawn as clean thin slabs with crisp edges; the haze as evenly sized
round dots of varying density, never as a gradient.

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
