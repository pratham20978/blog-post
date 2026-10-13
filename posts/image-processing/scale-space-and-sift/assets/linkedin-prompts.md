# LinkedIn image prompts — scale-space-and-sift

Five frames, one teaching arc: one fixed ring on two sizes of one square → a stack of blurred
copies with the dip deepest in the middle → one bead lower than its twenty-six neighbours → a
bowl kept and a trough turned away → one bell through a gate cut to its shape.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the
house template with the post's own numbers. These prompts are the alternative route for a
text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — One lens two zooms

- Narrative beat: a detector at one fixed scale sees a small square as one blob but the same square enlarged as four separate corners
- File: `linkedin-01-one-lens-two-zooms.png`
- Alt text: Two tiled squares, one small and one twice as large, each under the same fixed ring; the small fills it, the large shows four corners

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a five-frame sequence about why a feature detector must search over scale. It shows one fixed-size lens failing on a bigger version of the same shape.

SUBJECT
Two square blocks of bright tiles sit side by side on a dark tiled ground. The left block is small; the right block is exactly twice as wide. Over each block hovers an identical round ring of the same size. Over the small block the ring frames the whole square neatly. Over the large block the ring sits at one corner only, and three more identical rings sit at the other three corners, showing that the fixed ring can only take in a corner at a time.

KEY DETAILS
The rings share one line weight and one diameter, which is the point of the image. The single ring framing the small block is the focal element, drawn in atomic-tangerine; the four corner rings on the large block are blue-slate. Tiles are jet-black and silver, bright blocks white-smoke. Flat fills, fine outlines, subtle paper grain, generous empty space above.

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

## 02 — A stack of veils

- Narrative beat: one octave is a stack of progressively blurred copies, and the square becomes a soft dip that is deepest on the middle copy
- File: `linkedin-02-a-stack-of-veils.png`
- Alt text: A tiled grid with a bright square, and five thin sheets stacked above it, each softer, the square's dip deepest on the middle sheet

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second of five, about how an image is searched over scale. It shows one octave of blurred copies stacked like panes.

SUBJECT
The same dark tiled ground with its bright square block lies flat at the bottom of the frame, seen from a gentle oblique angle. Above it float five thin translucent sheets, evenly spaced, each a softer copy of the ground: on each sheet the square has become a round soft pool, shallow on the lowest and highest sheets and deepest on the middle one.

KEY DETAILS
The sheets are pale blue-slate tints with fine jet-black edges, stacked with equal gaps. The pool on the middle sheet is the focal element, its outline drawn in atomic-tangerine; the pools on the other sheets are silver. Flat tonal steps stand in for blur, no glossy gradients. Subtle paper grain, calm open space to the right.

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

## 03 — The lowest bead

- Narrative beat: a candidate keypoint must be lower than all twenty-six neighbours in position and scale
- File: `linkedin-03-the-lowest-bead.png`
- Alt text: A cube-shaped lattice of twenty-seven beads in three layers, the centre bead sitting lowest and the only coloured one

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third of five, about how a candidate point is chosen. It shows one point compared with its neighbours in three directions at once.

SUBJECT
A small cube-shaped lattice of beads, three layers of three by three, held in place by fine straight rods, seen from a gentle oblique angle. Every bead sits at the same height in its cell except the one at the very centre of the middle layer, which hangs visibly lower than all twenty-six around it.

KEY DETAILS
The rods are fine blue-slate lines; the twenty-six outer beads are white-smoke with jet-black outlines, all identical. The low centre bead is the focal element, solid atomic-tangerine. A faint strip of the tiled ground runs along the bottom of the frame. Flat fills, fine outlines, subtle paper grain, generous empty space around the lattice.

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

## 04 — A bowl and a trough

- Narrative beat: the edge test keeps a round extremum and rejects a long ridge, because it is a stricter version of the Harris corner test
- File: `linkedin-04-a-bowl-and-a-trough.png`
- Alt text: A round shallow bowl beside a long straight trough; a ball rests in the bowl, and the trough is crossed out by a gate

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth of five, about the test that removes edge responses. It contrasts a point curved equally in every direction with one curved in only one.

SUBJECT
On the left, a round shallow bowl carved into a flat slab, with a single ball resting at its lowest point. On the right, a long straight trough carved into an identical slab, running from front to back, with a ball that could roll along it. In front of the trough stands a narrow closed gate.

KEY DETAILS
The slabs are silver with fine jet-black outlines, the bowl and trough shaded with flat blue-slate tones. The ball in the round bowl is the focal element, solid atomic-tangerine; the ball in the trough is white-smoke. The closed gate is jet-black. Flat fills, fine outlines, subtle paper grain, balanced composition with lots of quiet space above.

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

## 05 — One bell through the gate

- Narrative beat: of the smoothing kernels, only the Gaussian bell meets the requirements a scale search needs, while a box and a sharp-peaked kernel do not
- File: `linkedin-05-one-bell-through-the-gate.png`
- Alt text: Three kernel shapes, a box, a sharp peak and a smooth bell, before a bell-shaped gate that only the smooth bell passes through

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the closing image of five, about why the Gaussian is the only kernel allowed to do the searching. It shows one shape fitting a requirement the others fail.

SUBJECT
Three solid profile shapes stand in a row on a ground line, like cut-out silhouettes: a flat-topped box, a narrow sharp-peaked spike with long thin skirts, and a smooth symmetric bell. In front of the row stands a gate whose opening is cut in exactly the bell's outline. The bell is shown halfway through the opening; the box and the spike stand back, clearly unable to fit.

KEY DETAILS
The box and the spike are silver with fine jet-black outlines. The gate is blue-slate. The bell is the focal element, solid atomic-tangerine. A thin strip of the tiled ground runs along the bottom. Flat fills, fine outlines, subtle paper grain, calm and balanced, with generous empty space.

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
