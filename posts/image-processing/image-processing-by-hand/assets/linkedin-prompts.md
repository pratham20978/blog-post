# LinkedIn image prompts — image-processing-by-hand

Six frames, one teaching arc: the grid loses something → the window is the whole
operation → the same nine numbers give three answers → one bad pixel wrecks a
derivative → the default magnitude is orientation-biased → the library is not the
math.

**These frames are already built** — see `linkedin-0*.png`, rendered in the
diagram-design skin with real typography and the post's own numbers. The prompts
below are the alternative route if you want the text-free illustration treatment
from an image model instead.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — The grid takes it away

- Narrative beat: a continuous surface becomes discrete posts, and everything between the posts is gone
- File: `linkedin-01-grid-takes-it.png`
- Alt text: **Continuous signal discretization in image processing, showing a smooth undulating ribbon sampled onto a regular grid of square posts with varying heights, where each post captures the ribbon’s value at a discrete sampling point.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the opening image of a six-frame sequence about
image processing. It depicts the moment a continuous thing becomes a discrete
one, before any processing has happened.

SUBJECT
A smooth, gently undulating ribbon descends from the upper area of the frame and
presses down onto a regular grid of square posts of varying height. Where the
ribbon meets a post, the post takes the ribbon's height. Between posts, nothing
remains — the gaps are empty ground.

KEY DETAILS
The post field occupies the lower two thirds, receding slightly to the right.
The ribbon above is drawn as a single fine contour line, thinner than the post
outlines. One post near the left third is the focal element and is the only
coloured object. The upper right area is left near-empty. Isometric line work,
flat fills, subtle paper grain.

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

## 02 — One small window does all of it

- Narrative beat: almost every classical operation is a small square of weights sliding across the field
- File: `linkedin-02-the-window.png`
- Alt text: **Sliding window convolution in image processing, showing a 3×3 convolution kernel moving across a regular grid of image pixels, with ghosted positions behind it illustrating the kernel’s scanning path over the image.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the second image of a six-frame sequence about
image processing. It depicts the single operation that most of the field
reduces to.

SUBJECT
A small square window divided into a three-by-three lattice hovers just above a
regular field of square posts. Faint ghosted outlines behind it show the earlier
positions it occupied as it travelled across the field, forming a broken trail.

KEY DETAILS
The window is the focal element and the only coloured object, sitting slightly
left of centre in the upper middle. The post field runs beneath it across the
lower half. The ghost trail fades toward the left edge. Nothing casts a shadow.
The right third stays near-empty. Isometric line work, flat fills, subtle paper
grain, no outlines on the ground plane.

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

## 03 — Same nine numbers, three answers

- Narrative beat: three operators on one identical neighbourhood return three different values
- File: `linkedin-03-three-answers.png`
- Alt text: **Convolution kernel producing different image-processing responses, showing the same 3×3 pixel neighborhood with one deep-valued cell generating three distinct output values through different operators.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the third image of a six-frame sequence about
image processing. It depicts one neighbourhood producing three different results
depending on which operator is applied.

SUBJECT
A single square window divided into a three-by-three lattice sits at the top.
Eight of its cells are shallow and level; the ninth is a deep well. Three
separate paths lead down from the window to three markers resting at three
plainly different heights on a shared vertical scale.

KEY DETAILS
The lowest marker is the focal element and the only coloured object, sitting well
below the other two. The three paths do not cross each other. The window sits in
the upper third, the markers in the lower half, the right edge near-empty. Fine
consistent line work, flat fills, subtle paper grain.

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

## 04 — One bad post throws the measurement

- Narrative beat: a single corrupted sample throws a derivative measured three positions away
- File: `linkedin-04-one-bad-pixel.png`
- Alt text: A row of even posts with one standing far too tall, and a measuring gauge nearby tilted well off true by its presence

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fourth image of a six-frame sequence about
image processing. It depicts a single corrupted sample distorting a measurement
taken some distance away from it.

SUBJECT
A row of square posts steps cleanly from a low plateau up to a high one. One
post near the low end stands absurdly taller than every other. A slender
measuring gauge, resting across the posts where the step occurs, is tilted well
off true — pulled out of alignment by the tall post several positions away.

KEY DETAILS
The over-tall post is the focal element and the only coloured object, placed in
the left third. The gauge sits across the step in the middle of the frame. A
faint ghosted outline shows where the gauge would rest if the tall post were not
there. The upper area stays near-empty. Isometric line work, flat fills, subtle
paper grain.

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

## 05 — Two paths, two different lengths

- Narrative beat: measuring the same diagonal along the legs instead of straight across overstates it
- File: `linkedin-05-l1-overstates.png`
- Alt text: **Distance metrics in image processing, comparing a straight-line Euclidean distance between two diagonal points with a longer right-angled Manhattan distance along horizontal and vertical paths.**

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the fifth image of a six-frame sequence about
image processing. It depicts two ways of measuring the same distance, and the
fact that they do not agree.

SUBJECT
Two points sit diagonally opposite each other. A straight taut line runs
directly between them. A second, visibly longer route leaves the same starting
point, travels along the horizontal, turns a sharp right angle, and climbs the
vertical to arrive at the same finishing point.

KEY DETAILS
The straight diagonal is the focal element and the only coloured object. The
right-angled route is drawn in a heavier neutral line so its extra length reads
immediately. A small quarter-arc marks the angle at the origin. The pair sits in
the lower left two thirds, with the upper right near-empty. Fine consistent line
work, flat fills, subtle paper grain.

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

## 06 — The library is not the math

- Narrative beat: the documented behaviour and the operation the name implies are not always the same thing
- File: `linkedin-06-library-vs-math.png`
- Alt text: Two mirrored copies of the same asymmetric window facing opposite directions, one overlaid faintly on the other

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame, the closing image of a six-frame sequence about
image processing. It depicts the gap between what an operation is called and
what it actually computes.

SUBJECT
One asymmetric square window, divided into a three-by-three lattice with a
clearly lopsided fill pattern, is shown twice. The second copy is the same shape
rotated a half turn, so its lopsided pattern points the other way. The two are
placed close together and slightly overlapping, so the mismatch is unmistakable.

KEY DETAILS
The rotated copy is the focal element and the only coloured object. The pair sits
slightly above centre. Below them, a faint field of posts recedes toward the
lower edge, tying the frame back to the opening image. The upper left is left
near-empty. Isometric line work, flat fills, subtle paper grain.

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
