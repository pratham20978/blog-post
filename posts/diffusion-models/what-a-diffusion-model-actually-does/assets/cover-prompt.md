# Cover prompt — what-a-diffusion-model-actually-does

**The shipped cover is the template build, not an external generation.** `assets/cover.png` is
produced by `python3 assets/_figures.py cover` and follows the series house layout: eyebrow,
Instrument Serif title, mono subtitle, the motif band, a rule, and an italic serif kicker. It is
deterministic, on-brand, and carries real typography, which is what the template-cover fallback in
`blog-visuals/references/cover-prompt.md` is for.

The prompt below is kept so the cover can be regenerated in an external image tool if the
publication ever moves to generated covers. Blocks 4–8 are the locked house-style blocks,
reproduced verbatim; only 1–3 are written for this post.

---

## 1 — CONCEPT

A field of fine, irregular grain resolving from left to right into one simple bright shape — a
crescent — on a dark ground. On the left the grain is total and no shape is present. Across five
or six stages the grain thins and the crescent emerges from it, never drawn but progressively
uncovered. The rightmost stage is the focal element: the shape is now clean and the grain is gone.
Nothing in the frame suggests a brush or a hand; the shape appears to have been there all along
and is being subtracted toward, not added.

## 2 — COMPOSITION

The stages sit in a single horizontal band across the middle third of the frame, evenly spaced,
each one a square panel of equal size. The band starts at the left edge margin and ends about
four-fifths of the way across. The rightmost panel is the focal element and carries the single
accent. A thin horizontal rule runs under the band. The upper third and the lower third are
near-empty, holding only flat background — the upper third is where a title overlay goes. The
right-hand fifth of the frame is empty.

## 3 — TECHNIQUE

Flat editorial technical illustration built from discrete square cells rather than continuous
tone, so the grain reads as quantised samples rather than photographic noise. Fine consistent
line weight on the panel outlines only. Flat fills with no internal gradients. Subtle paper grain
over the whole frame. No outlines on the individual cells.

## 4 — PALETTE

```
Palette, strictly limited to these five colours and their tints:
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0,
white-smoke #f5f5f5, atomic-tangerine #eb6c36.
White-smoke dominates as the background. Jet-black and blue-slate carry
structure. Atomic-tangerine is used once, on the single focal element, and
covers less than five percent of the frame. No other hues anywhere.
```

## 5 — LIGHT AND MOOD

```
Even, diffuse light with no dramatic shadows. Calm, precise, and technical
rather than energetic. The mood of a well-made reference book, not a
conference keynote slide.
```

## 6 — FRAME

```
16:9 aspect ratio, 1200 by 630 pixels. Keep all meaningful content within a
5 percent margin from every edge. The composition must survive being cropped
to a square and to a 4:1 banner.
```

## 7 — NEGATIVE

```
Do not include: any text, letters, numbers, words, labels, or captions.
No logos, watermarks, signatures, or UI chrome. No photorealism, no stock-photo
people, no 3D chrome or glossy renders, no lens flare, no drop shadows.
No colours outside the stated palette. No busy detail — large readable shapes
only, since this is viewed at thumbnail size.
```

## 8 — HOUSE STYLE

```
House style: an editorial technical illustration for a computer-science
publication. Flat vector-like shapes with fine line work, generous negative
space, and a single point of emphasis. Restrained and geometric. It should
look hand-designed for this specific article rather than generic tech art,
and it should sit comfortably beside clean black-and-white technical diagrams
without competing with them. Composed to stay legible at 300 pixels wide.
```

---

## Alt text

> A twelve-by-twelve patch of pure noise resolving through six stages into a bright crescent,
> under the line 'Trained only to undo noise'

## Note on block 7 and the shipped cover

The locked negative block forbids text, because image generators mangle typography and the site
overlays its own title. The template cover breaks that rule deliberately and safely: its type is
real SVG text set in the house faces, not generated, and part 2 of this series uses the same
layout. If this post ever switches to a generated cover, drop the title and kicker and let the
page shell supply them.
