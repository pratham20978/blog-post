# LinkedIn image prompts — diffusion-backbones-unet-to-dit

The alternative prompt pack, for when the carousel is generated in an image tool instead of built
from the locked templates in `assets/social/`. Six frames, one teaching arc: the denoiser's contract,
two ways to shrink a grid, where a U-Net keeps its weight and spends its effort, the patch-size
dial, MM-DiT's two streams, and the quadratic wall of comparisons.

Each prompt is self-contained — paste frame 05 without reading frame 04. The constraints block is
repeated in full every time, because that is what keeps the sequence looking like one sequence.

Recurring objects across the frames, so the arc reads as continuous: **a square field of discrete
cells holding a faint crescent** for the latent, **square tiles** for tokens, **rectangular slabs** for
U-Net levels, and **a single tangerine element** marking what each frame is about.

---

## 01 — The contract

- Narrative beat: every backbone takes a noisy grid in and hands back a grid of exactly the same size; only the inside differs.
- File: linkedin-01-diffusion-backbones-unet-to-dit.png
- Alt text: A tiled crescent field entering a closed box and an identical-size field leaving it on the other side

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening of a sequence about the networks inside diffusion models. It depicts the contract every such network keeps: the same shape in and out.

SUBJECT
A square field of small discrete cells holding a faint lighter crescent, dimmed by even grain, slides into a plain closed box from the left. An identical square field, the same size, slides out of the box on the right. The box's interior is not shown.

KEY DETAILS
The box sits at the centre of the frame, the two fields at matching heights on either side, joined to the box by short straight tracks. The single focal point is the outline of the outgoing field, drawn in tangerine, matching the incoming field's size exactly. Flat fills, no gradients inside any cell.

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

## 02 — Two ways to shrink

- Narrative beat: a U-Net pools a grid down and keeps a copy to restore detail; a DiT cuts the grid into tiles and keeps every value.
- File: linkedin-02-diffusion-backbones-unet-to-dit.png
- Alt text: One tiled field pooled into a smaller coarse field with a bridge carrying a copy, and cut into a row of tiles

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, second in a sequence about diffusion model backbones. It depicts two ways to make a grid smaller before comparing all its parts.

SUBJECT
A small square field of sixteen cells at the top centre. Below it the path splits. On the left branch the field becomes a smaller field of four larger, blander cells, and a thin bridge arcs from the original field down past it, carrying a copy. On the right branch the same field is cut into four square tiles that sit side by side in a neat row, each still showing its four small cells.

KEY DETAILS
The original field is centred in the upper third; the two branches fill the lower two thirds, left and right, with negative space between them. The single focal point is the thin lattice that cuts the right branch into tiles, drawn in tangerine. All other lines are jet-black or silver.

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

## 03 — Weight at the bottom, work at the top

- Narrative beat: a U-Net stores most of its weight in its narrow, coarse levels but spends most of its effort at the finest level.
- File: linkedin-03-diffusion-backbones-unet-to-dit.png
- Alt text: A U-shaped staircase of slabs, tall and thin at the rims, short and wide at the bottom, the top-left slab highlighted

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about diffusion model backbones. It depicts a U-shaped network where size and effort sit at opposite ends.

SUBJECT
A U-shaped staircase of rectangular slabs descending into a valley and climbing back out: tall thin slabs at both rims, progressively shorter and wider slabs toward the bottom. Thin bridges join each slab on the left to its mirror on the right. The wide slabs at the bottom look heavy and solid; the tall thin slab at the top left is busy with a dense pattern of fine lines.

KEY DETAILS
The U is centred and fills the middle of the frame, rims near the top, valley floor near the bottom third. The single focal point is the dense line pattern inside the top-left slab, drawn in tangerine. Bridges are fine silver lines; slabs are jet-black outlines with blue-slate fills.

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

## 04 — The patch-size dial

- Narrative beat: the same transformer processes four times as many tiles when the tiles are halved, so its effort quadruples while its size stays fixed.
- File: linkedin-04-diffusion-backbones-unet-to-dit.png
- Alt text: Two identical machines, one fed a short strip of large tiles, the other a strip of small tiles four times as long

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about diffusion model backbones. It depicts the same machine doing four times the work because its input was cut finer.

SUBJECT
Two identical boxy machines stand side by side, the same size and shape. The left machine is fed a short strip of a few large square tiles. The right machine is fed a strip of many small square tiles, four times as long, folding back and forth on the floor before it enters the machine.

KEY DETAILS
The two machines sit in the upper half at equal heights, their strips running down and across the lower half. The single focal point is the long strip of small tiles feeding the right machine, outlined in tangerine. Everything else is jet-black, blue-slate and silver.

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

## 05 — Two streams, one meeting

- Narrative beat: an MM-DiT runs image tiles and text tokens through separate machinery that meets only in one shared chamber.
- File: linkedin-05-diffusion-backbones-unet-to-dit.png
- Alt text: Two conveyor belts, one long with tiles and one short with cards, merging into one shared chamber and splitting again

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about diffusion model backbones. It depicts two separate streams that meet only once, in a shared room.

SUBJECT
Two parallel conveyor belts run from the top of the frame toward the bottom. The left belt is long and crowded with square tiles; the right belt is short and carries a few small rectangular cards. Midway down, both belts enter a single shared chamber from opposite sides, then leave it again on their own sides and continue separately.

KEY DETAILS
The belts run vertically, left and right of centre; the shared chamber spans the middle of the frame. The single focal point is the shared chamber's outline, drawn in tangerine. Each belt has its own identical machinery before and after the chamber, drawn in jet-black and blue-slate.

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

## 06 — The wall of comparisons

- Narrative beat: comparing every tile with every other grows with the square of the tile count, until it outweighs everything else the network does.
- File: linkedin-06-diffusion-backbones-unet-to-dit.png
- Alt text: Three square grids of comparison cells growing from small to towering as the tile rows beside them lengthen

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the close of a sequence about diffusion model backbones. It depicts the cost of comparing everything with everything as the number of tiles grows.

SUBJECT
Three square grids of tiny cells, left to right, each paired with a row of tiles along its edge. The first row has a few tiles and its grid is small; the second has twice as many tiles and its grid is four times the area; the third row is long and its grid towers over the others, filling most of the right half of the frame.

KEY DETAILS
The three grids sit on a common ground line along the lower third, growing from left to right. The single focal point is the largest grid's outline, drawn in tangerine. Smaller grids and the tile rows are jet-black and silver.

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
