# LinkedIn image prompts — what-a-diffusion-model-actually-does

The alternative prompt pack, for when the carousel is generated in an image tool instead of built
from the locked templates in `assets/social/`. Six frames, one teaching arc: the corruption, the
free target, the averaging, the amplification, the seed, the four parts.

Each prompt is self-contained — paste frame 05 without reading frame 04. The constraints block is
repeated in full every time, because that is what keeps the sequence looking like one sequence.

Recurring objects across all six frames, so the arc reads as continuous: **a square field of
discrete cells**, **a crescent shape** inside it, and **a single tangerine element** marking
whatever the frame is about.

---

## 01 — The corruption

- Narrative beat: a known recipe destroys the image, one small step at a time.
- File: linkedin-01-what-a-diffusion-model-actually-does.png
- Alt text: A crescent in a cell field dissolving into even grain across five stacked stages, the clearest stage marked

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening of a sequence about how diffusion
models work. It depicts the moment a clean shape is progressively destroyed by
a fixed, known procedure.

SUBJECT
A square field built from small discrete cells. A simple crescent shape sits
inside it, formed only by the cells being lighter than their surroundings. The
same field is repeated five times down the frame; from top to bottom the cells
become more irregular and the crescent dissolves into even grain until, in the
last repetition, no shape remains.

KEY DETAILS
The five fields are stacked vertically, evenly spaced, each the same size,
occupying the middle two-thirds of the frame. The topmost field — the one where
the crescent is clearest — is the single focal point and carries a thin
tangerine outline. A fine vertical rule runs down the left side, suggesting a
measured scale. Generous empty space at the top and bottom. Flat fills, no
gradients inside any cell.

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

## 02 — The free target

- Narrative beat: the noise that was added is kept, and it is the answer the network is graded against.
- File: linkedin-02-what-a-diffusion-model-actually-does.png
- Alt text: Two cell fields, one holding a crescent and one holding pure grain, combining into a third, with the grain field marked

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame from a sequence about how diffusion models work.
It depicts the moment two known quantities are combined, one of which is kept
aside as the answer.

SUBJECT
Two square fields of discrete cells sit side by side in the upper half. The left
field holds a faint crescent shape; the right field holds pure irregular grain
and no shape. Below them, a third field of the same size shows the two
overlaid — the crescent barely visible through the grain. A small closed
container sits beside the right-hand field, holding an exact copy of that grain,
set apart and preserved.

KEY DETAILS
The two upper fields are equal in size and separated by a narrow gap. The lower
field is centred beneath them. The preserved copy of the grain is the single
focal point and is the only tangerine element in the frame. Thin connector lines
run from the two upper fields down to the lower one. Flat fills, fine consistent
line weight, no gradients.

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

## 03 — The average

- Narrative beat: many clean images explain the same noisy one, so one guess returns their mean.
- File: linkedin-03-what-a-diffusion-model-actually-does.png
- Alt text: One grainy field fanning out to four distinct shapes, which converge into a single smeared field marked in tangerine

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame from a sequence about how diffusion models work.
It depicts the moment a single guess has to stand in for many possibilities.

SUBJECT
At the top, one square field of discrete cells filled with heavy grain. Fine
lines fan out from it to four smaller square fields arranged in a row, each
holding a different simple shape: a vertical divide, a horizontal divide, a
diagonal, and a crescent. Lines from all four converge below into one final
square field whose cells are a soft, indeterminate smear — recognisably the
average of the four, with none of their edges.

KEY DETAILS
The fan opens downward and the convergence closes downward, forming a narrow
hourglass. The four possibility fields are equal in size and evenly spaced. The
final smeared field at the bottom is the single focal point and carries a thin
tangerine outline. Generous space at the left and right margins. Flat fills, no
gradients inside cells.

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

## 04 — The amplifier

- Narrative beat: the same small error arrives enormous when the noise is heavy, so the steps stay small.
- File: linkedin-04-what-a-diffusion-model-actually-does.png
- Alt text: A small wedge entering four funnels of increasing width and leaving as four bars, the widest marked in tangerine

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame from a sequence about how diffusion models work.
It depicts the moment a small deviation is magnified by an amount that depends
on how much signal is left.

SUBJECT
Four horizontal lanes stacked down the frame. Each lane begins on the left with
an identical small wedge of the same size. Each wedge passes through a funnel
shape, and the funnels widen from lane to lane going down. On the right of each
lane the wedge emerges as a horizontal bar; the bars grow dramatically longer
from top to bottom, the bottom one running nearly the full width.

KEY DETAILS
The four input wedges are strictly identical — that equality is the point. The
lanes are evenly spaced with a thin rule between them. The bottom lane, with the
widest funnel and longest bar, is the single focal point and is rendered in
tangerine. A faint square field of discrete cells sits behind everything at low
contrast, tying this frame to the rest of the sequence. Flat fills, fine
consistent line weight.

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

## 05 — The seed

- Narrative beat: the new image is decided by where the walk started, not by anything remembered.
- File: linkedin-05-what-a-diffusion-model-actually-does.png
- Alt text: Three paths from three different grain fields to three different crescents, the middle path marked in tangerine

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame from a sequence about how diffusion models work.
It depicts the moment three identical procedures produce three different
results because they began in three different places.

SUBJECT
Three square fields of discrete grain sit in a row across the top, visibly
different from one another. From each, a stepped path descends — the same shape
of path in all three cases, the same number of steps, the same turns. At the
bottom of each path sits a square field holding a crescent, and the three
crescents differ from each other in orientation and thickness.

KEY DETAILS
The three paths are drawn identically in line weight and step count so the
reader sees the procedure is shared. The middle path and its two endpoints are
the single focal element and carry the tangerine. The starting fields are at the
top edge margin, the finished fields at the bottom. Flat fills, generous space
between the three columns, no gradients.

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

## 06 — The four parts

- Narrative beat: four components, and only one of them was ever trained.
- File: linkedin-06-what-a-diffusion-model-actually-does.png
- Alt text: Four stacked panels, three drawn as rigid fixed mechanisms and the third as a dense adaptive mesh marked in tangerine

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame closing a sequence about how diffusion models
work. It depicts four components of one system, exactly one of which is
adaptive.

SUBJECT
Four panels stacked down the frame, equal in width. The first shows a fixed
ruled scale, rigid and regular. The second shows a closed loop of arrows around
a small square field of cells. The third shows a dense irregular mesh of
connected nodes, visibly different in character from everything else — organic
where the others are rigid. The fourth shows a stepped staircase descending from
a grain field to a crescent.

KEY DETAILS
Panels one, two and four are drawn with strict geometric regularity, in
jet-black and blue-slate. The third panel — the mesh — is the single focal point
and is the only tangerine element, and its irregularity against the other three
is the whole composition. Thin rules separate the panels. Equal margins left and
right. Flat fills, no gradients.

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
