# LinkedIn image prompts — estimator-bias-variance-mse

Five frames, one teaching arc: five sightings on a long production line, the German tank problem → one more average gap, the unbiased rule → two heaps of estimates against the gate, bias against spread → sifting the scatter onto one line, Rao–Blackwell → eighteen markers drawn toward the middle, Stein's paradox.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the house template with the post's own numbers. These prompts are the alternative route for a text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — Five sightings on a long line

- Narrative beat: tanks are numbered 1 to N along a production line and five are captured; the largest serial seen, 303, is the maximum likelihood estimate, a floor for N rather than an estimate of it, since the true N is 342
- File: `linkedin-01-estimator-bias-variance-mse.png`
- Alt text: A long line of faint tank hulls with five drawn solid, the last one short of a tangerine gate at the line's true end

### Prompt

```text
SCENE AND INTENDED USE
The opening frame of a five-frame sequence about judging an estimate by its whole error, told through a production line of tank hulls whose length is unknown. It shows the problem: a few sightings, and an end that has not been seen.

SUBJECT
A long straight production line of identical tank hulls runs on a gentle diagonal from the lower left toward the upper right. Most hulls are faint silver outlines. Five of them, at uneven intervals along the first two thirds of the line, are drawn solid in blue-slate as if sighted. Beyond the last solid hull the faint hulls continue for a while, evenly spaced, to a single upright gate that marks where the line truly ends. The gate is atomic-tangerine and the focal element.

KEY DETAILS
The production line, its rails, the hull silhouettes, and the gate are the recurring objects of the sequence. Rails in jet-black, faint hulls in thin silver line, sighted hulls in blue-slate with jet-black line work. The upper third of the frame is empty white-smoke ground. The gap between the last sighted hull and the gate is clearly visible but modest.

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

## 02 — One more average gap

- Narrative beat: the five serials cut the line below the largest into five gaps averaging 59.6 unseen numbers; the unbiased MVUE lays one more gap of that size beyond the largest, 303 + 59.6 = 362.6, close to the true 342
- File: `linkedin-02-estimator-bias-variance-mse.png`
- Alt text: Five measuring rods laid between sighted tank hulls and a sixth rod laid beyond the last hull, reaching near a tangerine gate

### Prompt

```text
SCENE AND INTENDED USE
The second frame of a five-frame sequence about judging an estimate by its whole error, told through a production line of tank hulls whose length is unknown. It shows the rule that estimates the line's end without bias: measure the gaps you saw and add one more.

SUBJECT
The same straight production line of identical tank hulls runs on a gentle diagonal from the lower left toward the upper right, with five hulls drawn solid in blue-slate at uneven intervals and the rest as faint silver outlines. Under the line, five flat measuring rods of different lengths each span one gap between consecutive sighted hulls, the first starting at the line's beginning. A sixth rod, the average length of the five, is laid beyond the last sighted hull and ends a little past a single upright gate that marks the line's true end. The gate is atomic-tangerine and the focal element.

KEY DETAILS
The production line, its rails, the hull silhouettes, and the gate are the recurring objects of the sequence; the measuring rods are new here. Rods in jet-black with fine silver end caps, the sixth rod drawn with a dashed outline to show it is an estimate. The rods sit in a band below the rails with generous space around them. The upper third of the frame is empty white-smoke ground.

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

## 03 — Two heaps at the gate

- Narrative beat: over a million repeated captures the largest serial piles up against the true end and never passes it, a bias of −56.2 tanks; the unbiased rule centres on the end but scatters wider; the MLE's mean squared error is 1.65 times the MVUE's
- File: `linkedin-03-estimator-bias-variance-mse.png`
- Alt text: Two rails of small markers: one heap piled against the near side of a tangerine gate, a wider heap centred on it

### Prompt

```text
SCENE AND INTENDED USE
The third frame of a five-frame sequence about judging an estimate by its whole error, told through a production line of tank hulls whose length is unknown. It shows what happens when the estimate is repeated many times: one rule always falls short, the other is right on average but scattered.

SUBJECT
Across the top fifth of the frame runs a thin strip of the same production line of identical tank hulls, ending at a single upright gate. Below it, two long horizontal rails lie one above the other, both aligned so that the gate's position is marked on each by a short tick directly beneath it. On the upper rail, hundreds of small round markers are heaped like sand: the heap rises steeply toward the gate's tick and stops dead against it, with not a single marker beyond. On the lower rail, a wider, lower heap of the same markers is centred on the tick, with gentle slopes on both sides. The gate above, and the ticks below it, are atomic-tangerine; the gate is the focal element.

KEY DETAILS
The production line, the hull silhouettes, and the gate are the recurring objects of the sequence; the small round markers stand for repeated estimates. Markers in blue-slate, rails in jet-black, the upper strip's hulls in thin silver line. The two rails fill the middle of the frame with generous space between them, and the upper heap's sharp edge against the tick should read at a glance.

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

## 04 — Sifting the scatter

- Narrative beat: the crude unbiased rule, twice the mean minus one, scatters widely; averaging it over all captures that share the same largest serial (Rao–Blackwell) collapses each column of scatter onto one straight guide, the MVUE, with 2.33 times less variance
- File: `linkedin-04-estimator-bias-variance-mse.png`
- Alt text: Columns of scattered markers above a rail, each column funnelled down to one marker on a straight tangerine guide line

### Prompt

```text
SCENE AND INTENDED USE
The fourth frame of a five-frame sequence about judging an estimate by its whole error, told through a production line of tank hulls whose length is unknown. It shows how the best unbiased rule is built: average away the scatter that carries no information.

SUBJECT
Along the bottom of the frame runs a long horizontal rail with evenly spaced ticks. Above each tick rises a tall loose column of small round markers, scattered up and down, the columns growing taller toward the right. Each column narrows through a small funnel into a single larger marker sitting on one straight guide line that climbs gently from the lower left to the upper right through the middle of the frame. The guide line is atomic-tangerine and the focal element. A thin strip of the same production line of tank hulls and its gate runs faintly across the top edge, to keep the setting.

KEY DETAILS
The small round markers, the rail, and the production line are recurring objects of the sequence; the funnels are new here. Scattered markers in pale blue-slate, funnels in thin jet-black line, the single collapsed markers in solid blue-slate sitting exactly on the guide line. The columns are clearly wide above the funnels and reduced to points below them.

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

## 05 — Eighteen markers drawn toward the middle

- Narrative beat: Stein's paradox: pulling each of 18 early-season batting averages 79% of the way toward their common mean (James–Stein) cut the total squared error of the 1970 forecast from 0.0753 to 0.0213, although no single average is guaranteed to improve
- File: `linkedin-05-estimator-bias-variance-mse.png`
- Alt text: Eighteen markers on a rail, each drawn by a thread most of the way toward one tangerine marker at the rail's centre

### Prompt

```text
SCENE AND INTENDED USE
The closing frame of a five-frame sequence about judging an estimate by its whole error, told through a production line of tank hulls and markers on rails. It shows Stein's paradox: many separate estimates become better as a group when each is pulled toward their common centre.

SUBJECT
A long horizontal rail crosses the middle of the frame. Eighteen small round markers hang above it at uneven positions, spread widely to both sides. Each marker is joined by a thin taut thread to one larger marker at the rail's centre, and below each original marker a second, solid marker sits on the rail most of the way along its thread toward the centre, so that the eighteen solid markers form a tight cluster around the middle while the faint originals stay spread out above. The central marker is atomic-tangerine and the focal element. A thin strip of the same production line of tank hulls runs faintly across the top edge, to keep the setting.

KEY DETAILS
The small round markers and the rail are recurring objects of the sequence; the threads are new here. Original markers as faint silver outlines, the pulled markers in solid blue-slate, threads in thin jet-black line. The contrast between the wide faint spread above and the tight solid cluster on the rail should read at a glance.

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
