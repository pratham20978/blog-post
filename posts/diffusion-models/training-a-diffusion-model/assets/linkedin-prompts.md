# LinkedIn image prompts — training-a-diffusion-model

The alternative prompt pack, for when the carousel is generated in an image tool instead of built
from the locked templates in `assets/social/`. Six frames, one teaching arc: the last step that is
not noise, why the leak hides in small averages, why more steps cannot fix it, the repair, what
each prediction target does to a small mistake, and a loss weighting as one fixed budget.

Each prompt is self-contained — paste frame 05 without reading frame 04. The constraints block is
repeated in full every time, because that is what keeps the sequence looking like one sequence.

Recurring objects across the frames, so the arc reads as continuous: **a square field of discrete
cells holding a faint crescent** for an image, **a staircase or row of thin slabs** for the noise
levels, **evenly sized round dots** for noise, and **a single tangerine element** marking what each
frame is about.

---

## 01 — The last step that isn't noise

- Narrative beat: a diffusion model trains on a staircase of noise levels, and the bottom step, meant to be pure noise, still holds a ghost of the image.
- File: linkedin-01-training-a-diffusion-model.png
- Alt text: A staircase of slabs fading from a clear crescent to scattered dots, its lowest slab still holding a faint crescent outline

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening of a sequence about the decisions made before training a diffusion model. It depicts a training schedule whose final step was meant to be pure noise but is not.

SUBJECT
A staircase of thin flat slabs descends from the upper left to the lower right. On the top slab sits a square field of small discrete cells holding a clear lighter crescent. On each slab further down, the same square field holds less of the crescent and more evenly scattered dots, until the bottom slab's field is almost all dots.

KEY DETAILS
The bottom slab's field still shows a faint ghost of the crescent through its dots, and that ghost outline is the single tangerine element. Every other field is drawn in slate and silver. The slabs are evenly spaced, with crisp edges and fine line work. Flat fills, no gradients inside any cell.

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

## 02 — Hidden in small averages

- Narrative beat: averaging many values shrinks the noise in their mean but not a tint they all share, so a leak invisible in a small patch becomes readable in a large latent.
- File: linkedin-02-training-a-diffusion-model.png
- Alt text: A small grid of noisy cells beside a much larger grid whose many cells share a faint common tint that only shows at scale

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, second in a sequence about training diffusion models. It depicts why a faint signal hidden in a few values becomes visible across many.

SUBJECT
On the left, a small square field of sixteen discrete cells, each a random shade of grey, with no visible pattern. On the right, a much larger square field of several hundred small cells, also randomly shaded. Beside each field stands a simple level gauge with a needle.

KEY DETAILS
Across the large field the random shades average out, and a faint common tint shows evenly over the whole field. Its gauge needle, drawn in tangerine, points clearly away from the centre line, while the small field's gauge needle rests on the centre. Both fields share the same cell style. Flat fills, crisp edges.

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

## 03 — More steps, the same wrong answer

- Narrative beat: adding sampling steps makes the flawed schedule converge more precisely on the wrong brightness instead of escaping it.
- File: linkedin-03-training-a-diffusion-model.png
- Alt text: Two paths of dots approaching a high line: one levels off on a ledge well short of it, the other keeps climbing toward it

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, third in a sequence about training diffusion models. It depicts a process that converges, but to the wrong place.

SUBJECT
Two paths of evenly sized round dots start together at the left and travel right, the dots growing denser toward the right as more steps are taken. A thin horizontal line near the top marks the goal. The upper path keeps rising toward that line. The lower path flattens onto a low ledge and runs along it.

KEY DETAILS
The low ledge where the lower path settles is the single tangerine element. The dots on both paths are slate; the goal line is silver. The denser the dots, the more exactly the lower path sits on its ledge. Flat fills, crisp edges, generous empty space above the paths.

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

## 04 — Completing the last step

- Narrative beat: rescaling the schedule barely moves its middle and turns the final step into pure noise.
- File: linkedin-04-training-a-diffusion-model.png
- Alt text: The same staircase of noise levels with its middle slabs barely shifted and its lowest slab now holding only even dots

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, fourth in a sequence about training diffusion models. It depicts a small repair that completes a schedule's final step.

SUBJECT
The staircase of thin flat slabs from the first frame descends from upper left to lower right, each slab carrying a square field of small discrete cells that fades from a clear crescent to scattered dots. Faint silver outlines show where each slab sat before the repair; the middle slabs have moved by a hair.

KEY DETAILS
The bottom slab's field now holds only evenly scattered dots, with no ghost of the crescent, and a thin tangerine outline around that completed bottom slab is the single focal element. The other slabs stay slate and silver. Flat fills, crisp edges, fine line work.

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

## 05 — Three answer formats

- Narrative beat: predicting the noise, the clean image or a blend of both gives the same answer in principle but magnifies small mistakes very differently.
- File: linkedin-05-training-a-diffusion-model.png
- Alt text: Three lenses over the same small mark: one magnifies it hugely, one leaves it the same size, and one shrinks it slightly

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, fifth in a sequence about training diffusion models. It depicts three ways of writing down the same answer that treat a small mistake differently.

SUBJECT
Three identical round lenses on thin stands sit in a row across the frame. Under each lens lies the same tiny mark on a square field of small discrete cells holding a faint crescent. Above each lens, the mark's projected image is shown at the size that lens produces.

KEY DETAILS
The left lens projects the mark enormously enlarged, and that oversized projection is the single tangerine element. The middle lens projects it at the same size. The right lens projects it slightly smaller. Lenses and stands are slate with silver glass. Flat fills, crisp edges, no reflections.

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

## 06 — One budget across noise levels

- Narrative beat: a loss weighting splits one network's limited capacity across noise levels, so favouring some levels starves others.
- File: linkedin-06-training-a-diffusion-model.png
- Alt text: One pile of tokens divided along a row of slabs from clear to noisy, heaped at the clear end and nearly empty at the noisy end

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, sixth in a sequence about training diffusion models. It depicts a fixed budget spread unevenly across tasks.

SUBJECT
A row of thin flat slabs runs across the frame, each carrying a square field of small discrete cells that goes from a clear crescent on the left to scattered dots on the right. Small round tokens are heaped on the slabs: a tall pile on the clear left slabs, smaller piles toward the middle, almost none on the right.

KEY DETAILS
The empty space on the noisiest slab at the far right, outlined by a thin tangerine ring, is the single focal element. All tokens are slate and identical in size. The total number of tokens reads as fixed. Flat fills, crisp edges, generous negative space above the row.

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
