# LinkedIn image prompts — diffusion-samplers-and-solvers

The alternative prompt pack, for when the carousel is generated in an image tool instead of built
from the locked templates in `assets/social/`. Six frames, one teaching arc: the path a trained
model already defines, where few long steps go wrong, order as the slope of error, reusing the
last network call, putting the steps where the path bends, and noise that buys forgetting.

Each prompt is self-contained — paste frame 05 without reading frame 04. The constraints block is
repeated in full every time, because that is what keeps the sequence looking like one sequence.

Recurring objects across the frames, so the arc reads as continuous: **a haze of evenly sized round
dots** for noise, **a square field of discrete cells holding a crescent** for an image, **one smooth
path that bends once** for the sampling trajectory, **thin bars with small round joints** for solver
steps, and **a single tangerine element** marking what each frame is about.

---

## 01 — The path already exists

- Narrative beat: A trained diffusion model already defines one smooth path from every noise sample to an image; a sampler only decides how to walk it.
- File: linkedin-01-a-path-from-noise-to-image.png
- Alt text: A smooth path from a haze of dots to a crescent, traced by a dense row of tiny equal ticks, with one long stride beside it

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening of a sequence about diffusion samplers as numerical solvers. It depicts the fixed path that a trained model defines from noise to an image.

SUBJECT
A smooth curved path runs from a fine haze of evenly sized round dots at the lower left to a square field of small discrete cells holding a clear lighter crescent at the upper right. The path is straight for most of its length and bends once, about two thirds of the way along. A dense row of tiny evenly spaced ticks follows the path exactly.

KEY DETAILS
Beside the path, a single long straight stride, a thin bar with small round joints at each end, spans the first straight stretch from the haze toward the bend; it is the single tangerine element. The ticks, the path and the dots are slate and silver. Flat fills, crisp edges, no gradients inside any cell.

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

## 02 — Error is made at the bend

- Narrative beat: A few long steps follow the straight parts of the path almost perfectly and lose their accuracy where the path bends.
- File: linkedin-02-error-is-made-at-the-bend.png
- Alt text: Four long straight strides along a curved path: three lie on its straight stretches, and the one crossing the bend misses it

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about diffusion samplers as numerical solvers. It depicts where a sampler that takes few, long steps goes wrong.

SUBJECT
The same smooth curved path runs from a haze of evenly sized round dots at the lower left to a square field of cells holding a crescent at the upper right, straight for most of its length and bending once. Four long straight strides, thin bars joined by small round joints, walk the path from the haze to the crescent.

KEY DETAILS
Three strides lie almost exactly on the straight stretches. The one stride that crosses the bend cuts the corner and lands visibly off the path; that stride and the small gap it leaves are the single tangerine element. Everything else is slate and silver, with flat fills and crisp edges.

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

## 03 — Order is a slope

- Narrative beat: A higher-order method checks how the path turns within each step, so each halving of its step size cuts its error four or eight times instead of two.
- File: linkedin-03-order-is-a-slope.png
- Alt text: Three staircases descending at different slopes on a plain grid, the steepest one in orange reaching the bottom first

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about diffusion samplers as numerical solvers. It depicts the order of a solver as how steeply its error falls when more steps are taken.

SUBJECT
A plain square grid of fine silver lines fills the frame. Three staircases of thin flat slabs descend from the upper left toward the lower right, each step one doubling of the number of steps. The first descends gently, the second twice as steeply, the third steeper still.

KEY DETAILS
The steepest staircase is the single tangerine element and reaches the bottom edge first. The other two are slate and blue-slate. At the far upper left, all three start from the same slab, and for their first two steps they overlap, before order has room to show. Flat fills, crisp edges, generous space.

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

## 04 — Reuse the last call

- Narrative beat: A multistep solver gets a second-order step for the price of one network call by reusing the answer it computed on the previous step.
- File: linkedin-04-reuse-the-last-call.png
- Alt text: A row of strides along a curved path, each joint casting a thin line forward that steers the next stride, one joint in orange

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about diffusion samplers as numerical solvers. It depicts a multistep method, which reuses information from the previous step instead of making extra network calls.

SUBJECT
The same smooth curved path runs from a haze of evenly sized round dots to a square field of cells holding a crescent. Six medium strides, thin bars with small round joints, follow it closely. From each joint a thin straight guide line extends forward, past the next joint, steering the stride that follows.

KEY DETAILS
One joint near the bend, with its forward guide line, is the single tangerine element; it shows the earlier answer carried forward into the next step. Every other stride, joint and guide line is slate or silver. Flat fills, crisp edges, no gradients.

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

## 05 — Put the steps where it bends

- Narrative beat: Where the steps go matters as much as the solver: short steps where the path bends, long ones where it is straight.
- File: linkedin-05-put-the-steps-where-it-bends.png
- Alt text: Strides along a curved path, long on its straight stretches and short and dense around its single bend, where one stride is orange

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about diffusion samplers as numerical solvers. It depicts a step schedule that places short steps where the sampling path bends.

SUBJECT
The same smooth curved path runs from a haze of evenly sized round dots to a square field of cells holding a crescent. Strides, thin bars with small round joints, follow it: two long strides on the first straight stretch, then many short strides crowded around the single bend, then two long strides on the final straight stretch.

KEY DETAILS
Every stride lies on the path, including those through the bend. One short stride at the sharpest point of the bend is the single tangerine element. The others are slate and blue-slate. Flat fills, crisp edges, generous negative space around the long strides.

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

## 06 — Noise buys forgetting

- Narrative beat: A stochastic sampler adds fresh noise as it goes, which erases errors made earlier at the price of a larger error on every step.
- File: linkedin-06-noise-buys-forgetting.png
- Alt text: A path that wanders off course, then a small burst of fresh dots after which it returns to the crescent, the burst in orange

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the close of a sequence about diffusion samplers as numerical solvers. It depicts a stochastic sampler, which injects fresh noise that lets the path forget its earlier errors.

SUBJECT
A path of short strides, thin bars with small round joints, leaves a haze of evenly sized round dots at the lower left and drifts slightly off a faint silver guide curve. Midway, a small burst of fresh dots is scattered onto the path. After the burst the strides rejoin the guide curve and end on a square field of cells holding a clear crescent at the upper right.

KEY DETAILS
The burst of fresh dots is the single tangerine element. The drifting strides before it are blue-slate, the corrected strides after it jet-black, the guide curve silver. Flat fills, crisp edges, no gradients inside any cell.

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
