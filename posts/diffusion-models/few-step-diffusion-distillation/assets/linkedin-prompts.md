# LinkedIn image prompts — few-step-diffusion-distillation

The alternative prompt pack, for when the carousel is generated in an image tool instead of built
from the locked templates in `assets/social/`. Six frames, one teaching arc: one call returns the
blur, a student learns where paths end, the cliff at a decision, halving the steps round by round,
matching the set and losing a mode, and one network for every step count.

Each prompt is self-contained — paste frame 05 without reading frame 04. The constraints block is
repeated in full every time, because that is what keeps the sequence looking like one sequence.

Recurring objects across the frames, so the arc reads as continuous: **a haze of evenly sized round
dots** for noise, **a square field of discrete cells holding a crescent** for an image, **thin
channels running down a slope** for sampling paths, **thin bars with small round joints** for jumps,
and **a single tangerine element** marking what each frame is about.

---

## 01 — One call returns the blur

- Narrative beat: A single step of a sampler can only use the denoiser's first answer, and from pure noise that answer is the average of every image, a blur.
- File: linkedin-01-one-call-returns-the-blur.png
- Alt text: One short stride from a haze of dots ends on a grey cell field where four faint crescents overlap into a blur

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening of a sequence about few-step diffusion models. It depicts why one sampler step from pure noise cannot produce an image.

SUBJECT
A fine haze of evenly sized round dots fills the upper half of the frame. A single short stride, a thin bar with small round joints, leaves the haze and ends on a square field of small discrete cells in the lower half. In that field four crescents in four rotations overlap faintly, so no single crescent can be seen: a soft even blur of mid-grey cells.

KEY DETAILS
The stride is the single tangerine element. The cells are slate and silver tints, flat fills, crisp edges, no gradients inside any cell. Generous empty white-smoke ground around both shapes.

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

## 02 — The student learns where paths end

- Narrative beat: A distilled student does not walk the path; it learns where each starting point ends and jumps there in one call.
- File: linkedin-02-learn-where-paths-end.png
- Alt text: Thin winding channels run from a dot haze to crescents, and one long straight jump goes directly to where its channel ends

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about few-step diffusion models. It depicts a network that jumps straight to the end of a sampling path instead of walking it.

SUBJECT
From a haze of evenly sized round dots at the top, several thin channels wind down the frame, each ending on a square field of discrete cells holding one clear crescent. Beside one winding channel, a single long straight jump, a thin bar with small round joints, leaves the same starting dot and lands exactly where that channel ends.

KEY DETAILS
The long jump is the single tangerine element; the channels are slate lines of equal weight. The crescent fields are flat cells in slate and silver with crisp edges. The winding of the channels is visible, so the shortcut of the jump reads at a glance.

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

## 03 — The cliff at a decision

- Narrative beat: Two starting points a hair apart end on different images, so the map from noise to image has a cliff, and a smooth student strands some points between the two.
- File: linkedin-03-the-cliff-at-a-decision.png
- Alt text: Two nearly touching dots on a ridge send channels to opposite crescents; one dot stranded on the crest between them

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about few-step diffusion models. It depicts the decision point where nearby starting noises end on different images.

SUBJECT
A low ridge drawn as a single contour line crosses the frame. On each side a shallow valley holds a square field of discrete cells with a crescent, the two crescents pointing in opposite directions. Two round dots sit almost touching on the crest; from each, a thin channel runs down a different slope into a different crescent. A third dot rests exactly on the crest between them, connected to neither valley.

KEY DETAILS
The stranded dot on the crest is the single tangerine element. Channels and contour are slate lines of equal weight; crescent cells are flat slate and silver. The two near dots are drawn very close so the split reads as sudden.

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

## 04 — Halving the steps, round by round

- Narrative beat: Progressive distillation trains a student whose one step matches two of its teacher's, then makes the student the next teacher.
- File: linkedin-04-halving-round-by-round.png
- Alt text: Stacked rows of jointed bars spanning one path, each row with half as many bars, twice as long, as the row above

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about few-step diffusion models. It depicts progressive distillation halving the number of sampling steps in rounds.

SUBJECT
Five horizontal rows stacked from top to bottom, each spanning the same width from a small haze of dots on the left to a small field of cells with a crescent on the right. The top row is made of many short jointed bars end to end; each row below has half as many bars, each twice as long, until the bottom row is a single long bar spanning the whole width.

KEY DETAILS
The single long bar in the bottom row is the single tangerine element; every other bar is slate. The joints line up vertically across rows where a long bar replaces two short ones. Flat shapes, crisp joints, no gradients.

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

## 05 — Matching the set can lose a mode

- Narrative beat: Distribution matching pushes samples toward where the data is and away from where the generator already is, and can leave a whole mode empty.
- File: linkedin-05-matching-the-set.png
- Alt text: Dots gathered on three of four crescent fields arranged in a ring, the fourth field an empty outline

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame in a sequence about few-step diffusion models. It depicts a generator that matches the set of images but leaves one kind of image out.

SUBJECT
Four square fields of discrete cells sit in a ring, each holding a crescent in a different rotation. Small round dots cluster thickly on three of the fields. The fourth field holds no dots at all, and its crescent is drawn only as an outline of cells.

KEY DETAILS
The empty outlined crescent is the single tangerine element. The dot clusters and the filled crescents are slate and silver. A few short slate arrows in the centre point outward toward the three occupied fields only.

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

## 06 — One network, any step count

- Narrative beat: A shortcut model or flow map is one network that can jump any distance along the path, so the same model takes one, two or four steps.
- File: linkedin-06-one-network-any-step-count.png
- Alt text: One winding path from a dot haze to a crescent, crossed by one long jump, two medium jumps and four short jumps of one style

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the close of a sequence about few-step diffusion models. It depicts one model that can take any number of steps along the same path.

SUBJECT
One thin channel winds from a haze of evenly sized round dots at the top to a square field of discrete cells holding a crescent at the bottom. Three chains of jointed bars follow it side by side: one single long bar, a chain of two medium bars, and a chain of four short bars, all landing on the same crescent.

KEY DETAILS
The single long bar is the single tangerine element; the two- and four-bar chains are slate in exactly the same bar style, so they read as one tool used at three sizes. Flat fills, crisp joints, generous space around the path.

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
