# LinkedIn image prompts — edge-preserving-smoothing

Five frames, one teaching arc: a boundary and one bright tile both survive smoothing → each
neighbour weighed by likeness → neighbourhoods matched with their twins → the bright tile's own
vote against four plain ones → value leaking through every face until everything is grey.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the
house template with the post's own numbers. These prompts are the alternative route for a
text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — Kept, both of them

- Narrative beat: a bilateral filter keeps a bright outlier for the same reason it keeps an edge
- File: `linkedin-01-kept-both-of-them.png`
- Alt text: A mosaic split by a sharp boundary, with one bright tile on the dark side left as bright as before

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a five-frame sequence about smoothing an image without blurring its edges. It shows a mosaic after smoothing in which both a sharp boundary and one bright tile survive.

SUBJECT
A square mosaic of tiles split down the middle by a sharp vertical boundary, dark tiles on the left and pale tiles on the right. Soft haze has evened out the small differences inside each side, but the boundary stays crisp, and one single tile on the dark side still glows bright, as untouched as the boundary.

KEY DETAILS
The mosaic is the recurring object of the whole sequence. Dark tiles are jet-black, pale tiles silver, outlines fine and even. The one bright tile is the focal element and the only coloured shape. Flat fills, fine outlines, subtle paper grain, generous empty space in the upper area.

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

## 02 — Weighed by likeness

- Narrative beat: each neighbour counts in proportion to how alike its value is, so the bright tile's neighbours barely count
- File: `linkedin-02-weighed-by-likeness.png`
- Alt text: Tiles carrying discs of different sizes: large discs on like tiles, tiny ones across the boundary and beside the bright tile

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of five, about weighing neighbouring tiles by how alike they are. It shows the weights as discs of different sizes sitting on the tiles.

SUBJECT
The same mosaic, close up on a small block of tiles that straddles the boundary and includes the bright tile. Each tile carries a round disc: tiles alike in shade carry large discs, tiles across the boundary carry small discs, and the tiles around the bright tile carry discs no bigger than specks.

KEY DETAILS
The mosaic and its boundary continue from the previous frame. Discs are white-smoke on dark tiles and blue-slate on pale ones. The bright tile is the single focal element. Flat fills, fine line work, subtle paper grain, generous negative space.

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

## 03 — Looking for a twin

- Narrative beat: non-local means compares whole neighbourhoods: the boundary's repeats down its length, the bright tile's repeats nowhere
- File: `linkedin-03-looking-for-a-twin.png`
- Alt text: Small square windows of tiles matched in pairs along a boundary, and one window around the bright tile with no match

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of five, about finding similar neighbourhoods anywhere in an image. It shows small windows of tiles being matched with identical windows elsewhere.

SUBJECT
The same mosaic, seen whole. Several small square windows of nine tiles, each drawn as a thin frame, sit along the boundary, and each is joined by a faint line to an identical window further along the same boundary. One window frames the bright tile and its plain neighbours, and no line leaves it: it has no twin anywhere.

KEY DETAILS
Window frames are blue-slate, the connecting lines fine and faint. The bright tile is the single focal element. The mosaic keeps its boundary and palette from the earlier frames. Flat fills, fine line work, subtle paper grain.

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

## 04 — Its own vote

- Narrative beat: whether the bright tile survives depends on how much its own vote counts against four plain look-alikes
- File: `linkedin-04-its-own-vote.png`
- Alt text: Five tiles in a row on a balance beam, one bright and four plain, the beam tipping toward the plain ones

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of five, about a single rule deciding whether an outlier is kept or averaged away. It shows a vote between one bright tile and four plain tiles.

SUBJECT
Five square tiles from the mosaic stand on a long, thin balance beam: one bright tile at one end and four plain dark tiles spread along the rest. The beam tips gently toward the four plain tiles, which together outweigh the bright one; a faint second outline of the beam, level and still, hints at the other rule in which the bright tile's own vote holds everything in place.

KEY DETAILS
The tiles keep the mosaic's palette and line weight. The beam is jet-black, its faint ghost outline silver. The bright tile is the single focal element. Generous empty space around the beam, subtle paper grain.

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

## 05 — Warmth leaking through faces

- Narrative beat: diffusion lets value leak through every face; the bright tile drains through four sides and everything ends grey
- File: `linkedin-05-warmth-leaking-through-faces.png`
- Alt text: The mosaic with soft warmth seeping out of the bright tile through all four sides and slowly across the boundary

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the last of five, about smoothing as heat flow that slows at large differences. It shows value leaking out of tiles through their edges.

SUBJECT
The same mosaic. From the bright tile, soft warmth seeps out through all four of its sides into its plain neighbours, while along the boundary only a thin trickle crosses from one side to the other. Towards the bottom of the frame the mosaic fades into a single even grey, as if the flow had been left running too long.

KEY DETAILS
The seeping warmth is drawn as fine, flat bands just outside the bright tile's sides. The bright tile is the single focal element. Same palette, line weight and mosaic as the earlier frames. Flat fills, subtle paper grain, generous negative space.

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
