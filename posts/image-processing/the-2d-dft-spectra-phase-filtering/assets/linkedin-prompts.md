# LinkedIn image prompts — the-2d-dft-spectra-phase-filtering

Five frames, one teaching arc: an image is a stack of striped sheets → sliding a sheet moves
the picture without changing the sheet → the frame is treated as a repeating tile, and the seam
shows → one unwanted sheet is lifted out of the stack → lifting is cheap only once the job is
big enough.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the
house template with the post's own numbers. These prompts are the alternative route for a
text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — A stack of striped sheets

- Narrative beat: an image's spectrum is a list of waves, each with a strength and a position
- File: `linkedin-01-a-stack-of-striped-sheets.png`
- Alt text: A fanned stack of transparent sheets printed with stripes at different spacings and angles, adding up to a simple picture

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a five-frame sequence about reading an image's frequency spectrum. It shows that a picture can be built by stacking transparent sheets of stripes.

SUBJECT
A stack of thin transparent sheets, each printed with evenly spaced parallel stripes at its own spacing and its own angle. The sheets are fanned slightly so each one is visible, and seen straight through, the stack adds up to a simple picture of one bright square beside a dark one. The top sheet's corner is the focal element.

KEY DETAILS
The stack sits slightly left of centre at a gentle three-quarter angle and is the recurring object of the whole sequence. Stripes are jet-black and blue-slate on pale silver sheets; overlapping sheets darken slightly where they cross. The top sheet's corner is the only coloured shape. Isometric line work, flat fills, subtle paper grain, generous empty space in the upper right.

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

## 02 — Slide a sheet, move the picture

- Narrative beat: shifting an image changes only the phase; the strength of every wave stays the same
- File: `linkedin-02-slide-a-sheet.png`
- Alt text: The same stack of striped sheets with every sheet slid sideways by its own amount, the picture moved while the stripes keep their darkness

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of five about image spectra. It shows that moving a picture means sliding each of its stripe sheets, while no sheet gets lighter or darker.

SUBJECT
A stack of thin transparent sheets printed with parallel stripes at different spacings and angles, fanned slightly. Every sheet has been slid sideways by a small amount — sheets with finer stripes slid by proportionally more of a stripe — and seen through the stack, the simple picture of a bright square beside a dark one now sits further to the right. A faint outline shows where the picture sat before. A small sliding rail along the stack's lower edge is the focal element.

KEY DETAILS
The stack sits slightly left of centre at a gentle three-quarter angle. Stripes keep exactly the same darkness as before; only their positions change. The sliding rail is the only coloured shape. Isometric line work, flat fills, subtle paper grain, generous empty space in the upper right.

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

## 03 — The seam between tiles

- Narrative beat: the transform treats the picture as one tile of a repeating wallpaper, so mismatched edges become a seam
- File: `linkedin-03-the-seam-between-tiles.png`
- Alt text: A three-by-three wallpaper of identical square tiles whose edges do not match, with one vertical seam between tiles marked

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of five about image spectra. It shows that the transform assumes the picture repeats like wallpaper, so its left and right edges meet in a seam that was never in the picture.

SUBJECT
A wall covered with a three-by-three grid of identical square tiles. Each tile shows the same simple picture: dark on its left two-thirds and bright on its right third. Where the bright right edge of one tile meets the dark left edge of the next, a hard vertical seam runs down the whole wall. The centre tile is drawn crisply and the eight around it are fainter. One seam beside the centre tile is the focal element.

KEY DETAILS
The wall faces the viewer almost flat, with a slight three-quarter tilt, filling the lower two-thirds of the frame. Horizontal joins between tiles show no seam, because the top and bottom edges match. The marked seam is the only coloured line. Flat fills, fine consistent line work, subtle paper grain, generous empty space above.

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

## 04 — Lift out the unwanted sheet

- Narrative beat: periodic interference occupies one or two coefficients, so a notch filter removes it by deleting exactly those
- File: `linkedin-04-lift-out-the-unwanted-sheet.png`
- Alt text: A stack of striped sheets with one sheet of fine horizontal bands being lifted clear, the picture beneath now clean

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of five about image spectra. It shows that a regular interference pattern is one extra sheet in the stack, and removing it means lifting out that sheet alone.

SUBJECT
A stack of thin transparent sheets printed with stripes at different spacings and angles, as in the earlier frames. One sheet, printed with fine evenly spaced horizontal bands that do not belong to the picture, is being lifted straight up and out of the stack by a small tab. Through the remaining sheets, the simple picture of a bright square beside a dark one shows cleanly with no bands across it. The lifting tab is the focal element.

KEY DETAILS
The stack sits slightly left of centre at a gentle three-quarter angle; the lifted sheet hovers just above it, offset upward. Every other sheet stays exactly where it was. The tab is the only coloured shape. Isometric line work, flat fills, subtle paper grain, generous empty space in the upper right.

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

## 05 — A fixed toll against a growing pile

- Narrative beat: the transform route costs about the same whatever the kernel, the direct sum grows with it, and they cross near one size
- File: `linkedin-05-a-fixed-toll.png`
- Alt text: A row of block towers growing taller left to right beside a level bar, the towers passing the bar at one marked point

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the last of five about image spectra. It shows that going through the frequency domain costs a fixed toll, while working directly costs more for every larger job, so the cheaper route switches at one point.

SUBJECT
A row of small towers of stacked square blocks standing on a ground line, growing taller from left to right, the height growing faster with each step. A single long level bar runs horizontally across the row at a fixed height. The first towers stay below the bar; one tower in the middle is the first to rise past it, and every tower after it stands above. A small marker at the crossing point is the focal element.

KEY DETAILS
The row runs across the middle of the frame, seen almost flat with a slight three-quarter tilt. Blocks are flat silver squares with jet-black outlines; the bar is blue-slate. The crossing marker is the only coloured shape. Flat fills, fine consistent line work, subtle paper grain, generous empty space above the row.

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
