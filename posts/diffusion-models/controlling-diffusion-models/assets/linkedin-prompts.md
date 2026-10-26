# LinkedIn image prompts — controlling-diffusion-models

The alternative prompt pack, for when the carousel is generated in an image tool instead of built
from the locked templates in `assets/social/`. Six frames, one teaching arc: guidance overshoots,
the faint look drains away, a weaker model guides better, a branch that starts at zero, five photos
make a mould, and one dial with two losses.

Each prompt is self-contained — paste frame 05 without reading frame 04. The constraints block is
repeated in full every time, because that is what keeps the sequence looking like one sequence.

Recurring objects across the frames, so the arc reads as continuous: **a haze of evenly sized round
dots** for noise, **a square field of discrete cells holding a crescent** for an image, **thin
channels** for sampling paths, and **a single tangerine element** marking what each frame is about.

---

## 01 — Guidance overshoots

- Narrative beat: Guidance extrapolates past the conditional prediction, so at high noise it aims beyond the strongest real image before the path settles.
- File: linkedin-01-guidance-overshoots.png
- Alt text: A path from a haze of dots arcs past the stronger of two crescent targets, overshoots, and bends back to settle on it

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening of a sequence about controlling diffusion models. It depicts guidance aiming beyond anything real before the sample settles.

SUBJECT
A fine haze of evenly sized round dots fills the left third of the frame. On the right, two square fields of small discrete cells hold the same crescent, one faint in pale silver cells and one strong in dark slate cells, stacked one above the other. A thin sampling channel leaves the haze, climbs past the strong crescent's field into the empty space above it, turns in a smooth loop and comes back down to end on the strong crescent.

KEY DETAILS
The overshooting loop of the channel is the single tangerine element; the rest of the channel is slate. Cells are flat fills with crisp edges and no gradients. The empty space the loop reaches into stays white-smoke, larger than either cell field, so the overshoot reads at feed size.

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

## 02 — The faint look drains away

- Narrative beat: Guidance moves samples between looks: the less typical, faint half of a class drains into the strong one.
- File: linkedin-02-the-faint-look-drains-away.png
- Alt text: Many sampling paths from a dot haze bend into the strong crescent's basin; the faint crescent's basin keeps a single path

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about controlling diffusion models. It depicts guidance changing which look of a class gets drawn, not only how it is drawn.

SUBJECT
A fine haze of evenly sized round dots fills the top of the frame. Below it, a dozen thin sampling channels run downward. At the bottom sit two shallow basins, each holding a square field of small discrete cells with a crescent: a faint crescent in pale silver cells on the left and a strong crescent in dark slate cells on the right. Halfway down, nearly every channel bends toward the right basin, so the right basin receives eleven channels and the left basin only one.

KEY DETAILS
The bend where the channels turn is the single tangerine element, a short curved stroke across the bundle. Channels are fine, even slate lines. The left basin is visibly nearly empty, with generous white-smoke around it, so the imbalance is the first thing read.

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

## 03 — A weaker guide

- Narrative beat: Autoguidance steers away from a weaker copy's mistakes instead of away from the other classes, so it removes errors without deleting a look.
- File: linkedin-03-a-weaker-guide.png
- Alt text: A crisp crescent stencil beside a smaller smudged copy; an arrow points from the smudged copy through and past the crisp stencil

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about controlling diffusion models. It depicts guiding a model with a weaker version of itself.

SUBJECT
Two flat stencil plates stand side by side. The larger plate on the right has a clean crescent cut-out with crisp edges. The smaller plate on the left has the same crescent cut-out with smudged, doubled edges, as if cut by an unsteady hand. A single straight arrow starts at the smudged plate, passes through the centre of the crisp cut-out and continues a short way beyond it.

KEY DETAILS
The arrow is the single tangerine element. The plates are silver with slate outlines and fine consistent line work. Both cut-outs show the white-smoke ground through them. The smaller plate is clearly about two thirds the size of the larger one.

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

## 04 — A branch that starts at zero

- Narrative beat: ControlNet's trainable copy joins the frozen network through connections that start at zero, so training begins from the original model, untouched.
- File: linkedin-04-a-branch-that-starts-at-zero.png
- Alt text: A frozen stack of slate blocks with a silver copy beside it, joined by small closed valves; the main flow passes unchanged

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about controlling diffusion models. It depicts a trainable side path attached to a frozen network without disturbing it.

SUBJECT
A vertical stack of four solid slate blocks forms the frozen network, with a smooth flow line running down through all four from top to bottom. To its right stands a parallel stack of four lighter silver blocks, the trainable copy, with a small square field of cells holding an outline sketch at its top as its extra input. Each silver block connects to the matching slate block by a short horizontal pipe with a round valve wheel set fully closed.

KEY DETAILS
The four valve wheels are the single tangerine element, small and identical. The flow line through the slate stack is continuous and undisturbed. Pipes are thin with fine consistent line work. Leave wide white-smoke margins on both sides of the two stacks.

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

## 05 — Five photos make the mould

- Narrative beat: Fine-tuning on a few photos learns the photos, and without prior preservation it reshapes every image of the class into the subject.
- File: linkedin-05-five-photos-make-the-mould.png
- Alt text: Five small cards of a thin crescent feed a mould that presses every crescent behind it into the same thin shape

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about controlling diffusion models. It depicts personalising a model on a handful of images and what that does to the rest of its class.

SUBJECT
Five small square cards, each a field of discrete cells holding the same thin crescent, lie in a neat row across the top of the frame. Below them a simple press mould with a thin crescent-shaped die stamps a stack of cell-field cards. In the background, a fan of earlier cards shows ordinary, fuller crescents, and the cards nearest the press have already been reshaped into the thin crescent.

KEY DETAILS
The crescent-shaped die of the press is the single tangerine element. Cards are silver with slate cells, flat fills and crisp edges. The five source cards look nearly identical to each other, so the narrowness of the set is visible. Generous white-smoke negative space around the press.

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

## 06 — One dial, two losses

- Narrative beat: SDEdit's single noise dial fades the old image's ghost and its fine detail together; inversion keeps the detail without the ghost.
- File: linkedin-06-one-dial-two-losses.png
- Alt text: A dial beside three cell fields: a new crescent with an old ghost and fine grain, both fading together as the dial turns

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the close of a sequence about controlling diffusion models. It depicts editing an existing image by adding noise and denoising it as something new.

SUBJECT
A large round dial with a single pointer sits at the left. To its right, three square fields of small discrete cells are arranged in a row, each showing a crescent that points up. Behind each upward crescent is a faint ghost of an older crescent pointing left, and fine speckled grain covers the cells. From the first field to the third, the ghost and the grain fade together, until the third field shows a clean upward crescent with neither ghost nor grain.

KEY DETAILS
The dial's pointer is the single tangerine element. Cells are slate and silver tints with crisp edges. The ghost and the grain fade at exactly the same rate across the three fields, so they read as one quantity. Keep the dial and the fields on one horizontal line with generous white-smoke above and below.

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
