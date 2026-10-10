# Cover prompt — diffusion-backbones-unet-to-dit

**The shipped cover is the template build, not an external generation.** `assets/cover.png` is
produced by `python3 assets/_figures.py cover` and follows the series house layout: eyebrow,
Instrument Serif title, mono subtitle, the article's motif (a U-Net drawn to scale with its skips,
beside the series' noisy crescent patch cut into 2×2 patches and laid out as a strip of tokens), a
rule, and an italic serif kicker. It is deterministic, on-brand, and carries real typography, which
is what the template-cover fallback in `blog-visuals/references/cover-prompt.md` is for.

The prompt below is kept so the cover can be regenerated in an external image tool if the
publication ever moves to generated covers. Blocks 4–8 are the locked house-style blocks,
reproduced verbatim; only 1–3 are written for this post.

Alt text (same string as `blog.md` and `manifest.md`): A U-shaped stack of shrinking and growing
feature maps beside the noisy crescent patch cut into 2×2 patches and laid out as a strip of tokens

---

```
1. CONCEPT
Two ways of making a large tiled floor manageable. On the left, a staircase
of stacked slabs descends into a valley and climbs back out: tall narrow
slabs at the top, short wide slabs at the bottom, joined across the valley
by thin bridges at every level. On the right, a square field of small tiles
holding a simple lighter crescent is being lifted apart into a neat row of
identical tiles, laid end to end like a train. The single tangerine element
is the lattice that cuts the field into tiles: the decision of how big each
tile is.

2. COMPOSITION
The valley of slabs occupies the left third, its lowest point slightly left
of centre. The tiled crescent field sits just right of centre, at the same
height as the valley's rim. The row of separated tiles leaves the field and
runs toward the right edge along the upper-middle band. The lower third is
near-empty, holding only a faint ground line, so a title overlay has room.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat
fills with no internal gradients, subtle paper grain over the whole frame.
Slabs and tiles drawn as clean rectangles with crisp edges; bridges as thin
single lines.

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
