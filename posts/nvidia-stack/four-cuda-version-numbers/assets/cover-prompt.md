# Cover prompt — four-cuda-version-numbers

The shipped cover is `assets/cover.png`, built deterministically by `_cover.py`: a branded
template card carrying the post's own four-plate motif with the two decisive numbers in the
accent. It is on-brand, reproducible, and needs no external tool. **Use it unless there is a
reason not to.**

This prompt is the alternative, for when an illustrated hero is wanted instead. It produces a
wordless 1200×630 image in the same visual world as the LinkedIn sequence in
`linkedin-prompts.md`, so a reader who sees both recognises them as one set.

The blog cover stays **unbranded** — no Canery lockup. Only social frames carry the lockup.

```text
SCENE AND INTENDED USE
A 1200x630 blog hero image for a technical article about four separately versioned software
artifacts that all share one name, and the single comparison between two of them that decides
whether a program runs.

SUBJECT
Four thin rectangular plates float in a vertical column above a shallow white-smoke plinth,
separated by clear gaps. Each plate has a visibly different thickness and surface treatment, so
the four read as separately made parts rather than slices of one block. A fine caliper spans
only the middle two plates, its jaws seated precisely on their facing surfaces. A thin
translucent horizontal plane hovers above the column, extending well past it on both sides,
supporting nothing and touching nothing.

KEY DETAILS
The caliper must touch the middle two plates and unmistakably not the topmost or the lowest —
that exclusion is the whole idea. Draw the hovering plane as a single ruled hairline so it reads
as a limit rather than a shelf, with a deliberate empty gap between it and the topmost plate.
The lowest plate is cut from the same darker material as the plinth and remains fused to it with
no seam. Compose the column in the left third of the frame in a three-quarter orthographic view,
leaving the right two thirds as open white-smoke for the title to be set over later.

CONSTRAINTS
1200x630 landscape frame. Editorial technical illustration with flat vector-like shapes, fine
consistent line work, subtle paper grain, and generous negative space. Palette strictly limited
to jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5, and
atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears once, on the caliper,
and covers less than five percent of the frame. No text, letters, numbers, labels, captions,
logos, watermarks, signatures, UI chrome, photorealism, stock-photo people, glossy 3D, lens
flare, or drop shadows. Keep meaningful content inside a five percent safe margin and out of the
right two thirds.
```

**Alt text for whichever cover ships:** Four stacked plates naming each CUDA version number,
with a caliper spanning only the middle two — the pair that decides whether a program runs.
