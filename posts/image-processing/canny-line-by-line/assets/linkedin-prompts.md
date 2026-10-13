# LinkedIn image prompts — canny-line-by-line

Five frames, one teaching arc: a straight boundary traced only in broken pieces with a ring stuck
to it → two equal pillars, only one kept → chains kept by their anchor, loose ones dropped → the
same mosaic smoothed first, its boundary whole → flags set by how far the noise reaches.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the
house template with the post's own numbers. These prompts are the alternative route for a
text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — A clean edge, broken

- Narrative beat: the default settings return a perfectly straight edge as three separate pieces with a ring of extra pieces stuck to it
- File: `linkedin-01-a-clean-edge-broken.png`
- Alt text: A mosaic split by a straight boundary, traced by only three separate beads, with a ring of beads hugging one bright tile

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a five-frame sequence about how an edge detector decides what a line is. It shows a perfectly straight boundary that the detector traces only in broken pieces.

SUBJECT
A square mosaic of tiles split down the middle by a straight vertical boundary, dark tiles on the left and pale tiles on the right. Along the boundary sit only three round beads, at the top, the middle and the bottom, with gaps between them. On the dark side, one bright tile is surrounded by a tight ring of small beads, and the ring touches the boundary beads at two corners.

KEY DETAILS
The mosaic is the recurring object of the whole sequence. Dark tiles are jet-black, pale tiles silver, beads blue-slate, outlines fine and even. The one bright tile inside the ring is the focal element and the only coloured shape. Flat fills, fine outlines, subtle paper grain, generous empty space in the upper area.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

---

## 02 — Two at a tie

- Narrative beat: when two neighbouring pixels are exactly equal, the tie rule decides whether the edge keeps zero, one or two of them
- File: `linkedin-02-two-at-a-tie.png`
- Alt text: Two equal pillars standing side by side at a boundary, one kept upright and solid, the other drawn as an empty outline

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of five, about a tie between two equal neighbours. It shows two pillars of exactly the same height at the boundary of the mosaic, only one of which is kept.

SUBJECT
Two tall square pillars of exactly equal height stand side by side on the line where dark tiles meet pale tiles, each rising from one tile of the boundary. The left pillar is solid and kept. The right pillar is drawn only as an empty outline, as if it had been set aside, although it is just as tall.

KEY DETAILS
The same mosaic and the same tile sizes as the rest of the sequence, seen from a low angle so the two pillars read clearly. The solid left pillar is the focal element and the only coloured shape. The equal heights must be obvious at a glance. Flat fills, fine outlines, subtle paper grain.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

---

## 03 — Chains, not beads

- Narrative beat: hysteresis keeps whole connected chains that hang from at least one strong bead and drops loose pieces with no anchor
- File: `linkedin-03-chains-not-beads.png`
- Alt text: A long chain of beads hanging from one bright hook, while two short loose chains with no hook fall away below

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of five, about keeping connected chains rather than single points. It shows chains of beads, and only the chain with an anchor stays up.

SUBJECT
Above the mosaic, a long chain of beads threaded on a fine line hangs from one strong hook and stays up, running straight down along the boundary between dark and pale tiles. Two short chains of beads, each with no hook of its own, slip away and drop below the mosaic, falling apart as they go.

KEY DETAILS
The mosaic is the same as in the other frames, now seen from slightly above. Beads are blue-slate, threads fine and dark. The single hook that holds the long chain is the focal element and the only coloured shape. Generous empty space around the falling chains. Flat fills, fine outlines, subtle paper grain.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

---

## 04 — Smooth first

- Narrative beat: blurring the image first detaches the bright tile's ring from the boundary, so the edge comes out whole and the ring falls away
- File: `linkedin-04-smooth-first.png`
- Alt text: The same mosaic under a soft haze, its boundary traced by one continuous chain, and the ring around the bright tile shrunk and detached

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of five, about smoothing an image before looking for edges. It shows the same mosaic after a gentle blur, where the boundary is now traced as one continuous chain.

SUBJECT
The same square mosaic, now under a soft even haze that rounds every tile's corners. Along the boundary runs one unbroken chain of beads from top to bottom. The bright tile has dimmed into a soft glow, and the ring of beads that used to hug it has shrunk to two small loose beads that no longer touch the chain.

KEY DETAILS
The haze is drawn as a light translucent veil, not a gradient smear; tiles keep fine outlines. The continuous chain along the boundary is the focal element; its top bead is the only coloured shape. Flat fills, fine outlines, subtle paper grain, generous empty space.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```

---

## 05 — Set from the noise

- Narrative beat: set the thresholds from how high flat ground's random bumps reach, not by trying numbers until the picture looks right
- File: `linkedin-05-set-from-the-noise.png`
- Alt text: A low mound of pebbles thinning into a long tail, with a tall flag far out past the tail and a shorter flag at half its distance

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the final frame of five, about choosing thresholds from the noise. It shows flat ground covered in random pebbles and two flags placed by how far the pebbles reach.

SUBJECT
A wide flat ground stretching to the right, covered in small pebbles piled into a low mound near the left that thins into a long sparse tail. A tall flag stands far out to the right, past almost every pebble. A shorter flag stands at half the tall flag's distance, among the last scattered pebbles. Beyond the tall flag, on the far right, sits the edge of the same mosaic as in the earlier frames.

KEY DETAILS
Pebbles are blue-slate and silver, the ground white-smoke, flags fine-lined. The tall flag is the focal element and the only coloured shape. The mound and its long thinning tail must read as one shape at a glance. Flat fills, fine outlines, subtle paper grain, generous empty space.

CONSTRAINTS
4:5 portrait frame, designed for a LinkedIn carousel. Editorial technical
illustration with flat vector-like shapes, fine consistent line work, subtle
paper grain, and generous negative space. Palette strictly limited to
jet-black #2d3142, blue-slate #4f5d75, silver #bfc0c0, white-smoke #f5f5f5,
and atomic-tangerine #eb6c36. White-smoke dominates; atomic-tangerine appears
once on the focal element and covers less than five percent of the frame.
Maintain the same visual world, scale language, line weight, palette, and
recurring objects across every frame in the sequence. One idea per frame.
No text, letters, numbers, labels, captions, logos, watermarks, signatures, UI
chrome, photorealism, stock-photo people, glossy 3D, lens flare, or drop
shadows. Keep meaningful content inside a five percent safe margin and use
large shapes that remain legible at mobile-feed size.
```
