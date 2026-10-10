# Cover image prompt — what-the-nvidia-stack-actually-is

The shipped cover is the deterministic template build in `_cover.py` (`cover.html` → `cover.svg`
→ `cover.png`, 1200×630). This prompt is the alternative handoff if the cover is ever
regenerated with an image tool instead. Either way the constraint is the same: the cover must
carry the post's argument, not a GPU photograph.

## 1. CONCEPT

A layered stack of seven thin horizontal bands, read as a diagram rather than an illustration.
The five upper bands are quiet and neutral. The two lowest bands are held in a single warm
accent and enclosed together, because they are the only layers that must come from the machine
itself. The idea being drawn is a boundary, not a product.

## 2. COMPOSITION

Landscape 1200×630. The stack occupies the left third, vertically centred, roughly 230 px wide.
The right two thirds carry the title block: a small monospace eyebrow, a two-line serif title
with the second line in the accent, and a monospace keyword row beneath. A hairline rule sits
near the bottom with a caption line under it. Generous margins; nothing touches an edge.

## 3. TECHNIQUE

Flat vector. Hairline strokes at 1–1.2 px. No gradients, no glow, no bevel, no drop shadow, no
3D. Corner radius 4 px on the stack container, none elsewhere. The image should read as a
technical figure lifted from an engineering document.

## 4. PALETTE

- paper `#f5f5f5`
- ink `#2d3142` — title, stack outline
- muted `#4f5d75` — secondary labels
- soft `#7a8399` — eyebrow, caption
- accent `#eb6c36` — the two host layers and the second title line, nothing else
- accent tint `rgba(235,108,54,0.08)` — the fill behind those two bands
- rule `rgba(45,49,66,0.12)`

Exactly one accent hue. If more than two elements carry it, the signal is gone.

## 5. LIGHT AND MOOD

Even, flat, no light source. Calm and declarative. The mood is a well-drawn schematic on good
paper, not a product launch. Nothing should feel energetic or futuristic.

## 6. FRAME

1200×630, safe margins of 84 px on every side. The title must remain legible at 600 px wide,
which is the width it is most often seen at in a feed or a link preview.

## 7. NEGATIVE

No GPU photographs or renders. No circuit-board textures, silicon dies, heatsinks or fans. No
green NVIDIA branding, no logos, no trademarks. No dark mode, no neon, no cyan-and-purple
"technical" palette. No isometric 3D, no glossy surfaces, no lens flare. No stock imagery of
servers or data centres. No human figures. No decorative code rain. No arrows that do not carry
a meaning.

## 8. HOUSE STYLE

Instrument Serif for the title, Geist for any sans label, Geist Mono for technical strings and
the eyebrow. Sentence case in prose, lowercase in monospace labels. The canery wordmark sits
bottom-right in muted monospace at small size. The cover must sit beside the other parts of the
NVIDIA Stack series without looking like a different publication.
