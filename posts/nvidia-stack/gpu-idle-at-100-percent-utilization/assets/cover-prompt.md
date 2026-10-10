# Cover prompt — gpu-idle-at-100-percent-utilization

The shipped cover is `assets/cover.png`, built deterministically by `_cover.py`: a branded template
card carrying the post's own motif — a utilization readout of 100% above a grid of SMs with exactly
one lit. It is on-brand, reproducible, and needs no external tool. **Use it unless there is a reason
not to.**

This prompt is the alternative, for when an illustrated hero is wanted instead. It produces a
wordless 1200×630 image in the same visual world as the LinkedIn sequence in `linkedin-prompts.md`.

The blog cover stays **unbranded** — no Canery lockup. Only social frames carry the lockup.

```text
1. CONCEPT
A measuring instrument that reads full above a machine that is almost entirely idle. A round dial
gauge with its needle pinned at the maximum stop presides over a wide grid of cold burners, and
exactly one burner carries a small flame. The gauge is not wrong; it is answering a narrower
question than the viewer assumes.

2. COMPOSITION
The burner grid, about forty identical burners in a shallow three-quarter view, occupies the left
half of the frame and slightly below centre. The single lit burner sits in the grid's top-left
corner. The dial gauge floats above the grid, aligned with its left edge. A long empty ticket rail
runs faintly along the back of the cooktop. The right third of the frame is near-empty
white-smoke, holding only a soft paper texture.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat fills with no internal
gradients, subtle paper grain over the whole frame. Burners drawn as simple concentric rings.

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

The atomic-tangerine accent goes on the single flame.

**Alt text for whichever cover ships:** A GPU utilization readout of 100% above a grid of streaming
multiprocessors in which a single cell is lit.
