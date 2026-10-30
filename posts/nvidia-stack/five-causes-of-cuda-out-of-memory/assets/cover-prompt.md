# Cover prompt — five-causes-of-cuda-out-of-memory

The shipped cover is `assets/cover-five-causes-of-cuda-out-of-memory.png`, built deterministically by
`_cover.py`: a template card in Part 3's layout carrying the post's own motif — run 1's 256 MiB request
above the 37 segments whose 128 MiB tails held 4.63 GiB free, none large enough. It is on-brand,
reproducible, and needs no external tool. **Use it unless there is a reason not to.**

This prompt is the alternative, for when an illustrated hero is wanted instead. It produces a
wordless 1200×630 image in the same visual world as the LinkedIn sequence in `linkedin-prompts.md`.

The blog cover stays **unbranded** — no Canery lockup. Only social frames carry the lockup.

```text
1. CONCEPT
A long storage shelf whose free space adds up to plenty but is useless. Every bay of the shelf holds
a wide dark crate pushed against one side, leaving a narrow empty gap at the other end of the bay.
In front of the shelf waits one large crate, wider than any gap, although the gaps together are far
wider than it. Nothing is broken; the space is simply in the wrong shape.

2. COMPOSITION
The shelf runs from the left edge to about two thirds across the frame, three tiers high, seen almost
straight on with a slight downward angle. Each tier has six or seven identical bays, each bay a wide
dark crate and a narrow gap. The waiting crate sits on the floor in front of the shelf's right end,
slightly below centre. The right third of the frame is near-empty white-smoke, holding only a soft
paper texture.

3. TECHNIQUE
Flat editorial technical illustration. Fine consistent line weight, flat fills with no internal
gradients, subtle paper grain over the whole frame. Crates drawn as simple rectangles with a single
inner line for depth; the gaps left as clean white-smoke.

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

The atomic-tangerine accent goes on the single waiting crate.

**Alt text for the shipped template cover:** A 256 MiB request above 37 memory segments, each a live block beside a free tail too small to hold it.
For an illustrated cover from this prompt: A long shelf of crates with a narrow gap in every bay, and one
large crate that fits none of the gaps.
