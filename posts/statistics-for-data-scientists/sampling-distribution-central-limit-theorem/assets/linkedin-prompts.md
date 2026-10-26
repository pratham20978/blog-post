# LinkedIn image prompts — sampling-distribution-central-limit-theorem

Seven frames, one teaching arc: thirty soundings that miss the one trench, the n = 30 failure → two rails, single soundings against survey averages, SD and SE → two copies of the lake, precise and wrong → four lakes, four trenches, skewness sets the pace → two flags on a long rail, Berry–Esseen's late guarantee → a trench with no floor, infinite variance → a hundred thousand surveys, simulation as the instrument.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the house template with the post's own numbers. These prompts are the alternative route for a text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — Thirty soundings, none in the trench

- Narrative beat: a sample of 30 customers usually misses the few biggest spenders, the way 30 soundings miss a lake's one trench, so its mean reads low; on real customer spend a 5% t-test of the true mean rejects 39.8% of the time at n = 30, so n ≥ 30 is a rule of thumb, not a theorem
- File: `linkedin-01-sampling-distribution-central-limit-theorem.png`
- Alt text: A lake in cross-section with one deep trench outlined in tangerine; thirty thin sounding lines all stop on the shallow bed

### Prompt

```text
SCENE AND INTENDED USE
The opening frame of a seven-frame sequence about how slowly the average of a skewed population becomes normal, told through a lake surveyed by soundings. It shows one survey that misses the place where most of the water is.

SUBJECT
The subject is a lake seen in cross-section, its bed long and shallow except for one narrow, deep trench that holds much of the water, with the trench slightly right of centre. Thirty thin sounding lines, each with a small weight at its end, hang down from small floats on the water at uneven spacing, and every one stops on the shallow bed: none falls into the trench. The trench's outline is atomic-tangerine; it is the focal element.

KEY DETAILS
The lake cross-section, its trench, and the sounding lines are the recurring objects of the sequence. The waterline runs straight across the upper third of the frame, the bed sits just below the middle, and the trench reaches down toward the lower margin. Water is a pale flat tint of blue-slate, the bed silver with fine hatching, the lines and weights jet-black, the floats small silver circles. The space above the waterline is empty white-smoke ground.

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

## 02 — Single soundings and survey averages

- Narrative beat: the standard deviation describes one customer (σ = £8,267) and the standard error σ/√n describes a mean of n (£1,509 at n = 30); the means of many samples of 30 form the sampling distribution, narrower than the population but still lopsided, with 71.8% of them below the true mean
- File: `linkedin-02-sampling-distribution-central-limit-theorem.png`
- Alt text: Two rails of markers: single soundings spread wide, survey averages heaped tighter but lopsided, left of one tangerine peg

### Prompt

```text
SCENE AND INTENDED USE
The second frame of a seven-frame sequence about how slowly the average of a skewed population becomes normal, told through a lake surveyed by soundings. It contrasts the spread of single soundings with the spread of survey averages.

SUBJECT
Across the top fifth of the frame runs a thin strip of a lake seen in cross-section, its bed long and shallow except for one narrow, deep trench that holds much of the water. Below it lie two long horizontal measuring rails with no markings, one above the other, each running from shallow on the left to deep on the right. On the upper rail, small round markers, one for each single sounding, are scattered along its whole length: most crowd the shallow end and a few lie far out toward the deep end. On the lower rail, one marker for each survey's average over thirty soundings: they stack into a heap far narrower than the scatter above, still lopsided, its peak on the shallow side with a thin trail toward the deep side. A single upright peg on the lower rail marks the lake's true average depth, to the right of the heap's peak; the peg is atomic-tangerine and the focal element.

KEY DETAILS
The lake cross-section, the sounding lines, and the small round markers recur across the sequence; the measuring rails are recurring objects too. The two rails fill the middle of the frame with generous space between them. Markers jet-black, rails blue-slate, water a pale flat tint of blue-slate, the bed silver.

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

## 03 — Precise and wrong

- Narrative beat: a sample that misses the biggest customers has a low mean and a small SD at once (their correlation across samples is 0.972), so it looks precise and is wrong: 74.1% of samples of 30 miss all 43 of the top 1%, a 5% t-test rejects 53.7% of those, and it rejects none of the 25,855 that hold one
- File: `linkedin-03-sampling-distribution-central-limit-theorem.png`
- Alt text: Two copies of a lake: one survey's short, even lines on the shallow bed, the other's one tangerine line deep in the trench

### Prompt

```text
SCENE AND INTENDED USE
The third frame of a seven-frame sequence about how slowly the average of a skewed population becomes normal, told through a lake surveyed by soundings. It shows why a survey that misses the trench looks precise as well as reading shallow.

SUBJECT
Two identical copies of a lake seen in cross-section, its bed long and shallow except for one narrow, deep trench that holds much of the water sit side by side, each surveyed once. In the left copy every sounding line stops on the shallow bed: the lines are short and almost exactly equal in length, a neat, even row. In the right copy most lines stop on the shallow bed too, but one falls into the trench and runs far deeper than all the others, so the row is ragged and uneven. That single deep line is atomic-tangerine; it is the focal element.

KEY DETAILS
The lake cross-section, its trench, and the thin sounding lines with small weights hanging from floats are the recurring objects of the sequence. The two copies share one waterline across the upper third of the frame, with a clear gap between them. Water a pale flat tint of blue-slate, the bed silver with fine hatching, the lines and weights jet-black, the floats small silver circles.

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

## 04 — Four lakes, four trenches

- Narrative beat: skewness, not n = 30, sets the pace: a one-sided 5% t-test's lower-tail error is about 5% + 11.02 points × γ/√n, so the sample size needed grows like the skewness squared, and n = 30 keeps the error within 10% of 5% only if γ is below 0.25
- File: `linkedin-04-sampling-distribution-central-limit-theorem.png`
- Alt text: Four lakes stacked, each trench deeper than the last, beside heaps of survey averages that grow more lopsided

### Prompt

```text
SCENE AND INTENDED USE
The fourth frame of a seven-frame sequence about how slowly the average of a skewed population becomes normal, told through a lake surveyed by soundings. It shows that the more lopsided the lake, the more lopsided the survey averages.

SUBJECT
Four small lakes in cross-section are stacked in a column from the top of the frame to the bottom. The top lake has a flat, even bed with no trench. Each lake below has a narrower, deeper trench than the one above it, so the bottom lake's trench is the deepest. To the right of each lake, a short horizontal measuring rail holds a small heap of round markers, one per survey's average: beside the flat lake the heap is symmetric, and each heap further down is more lopsided, with a longer thin trail toward the deep side. The outline of the deepest trench, in the bottom lake, is atomic-tangerine; it is the focal element.

KEY DETAILS
The lake cross-sections, their trenches, the measuring rails, and the small round markers are the recurring objects of the sequence. The four rows are evenly spaced with generous gaps. Water a pale flat tint of blue-slate, beds silver with fine hatching, markers jet-black, rails blue-slate.

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

## 05 — A guarantee far down the rail

- Narrative beat: the Berry–Esseen bound guarantees that the spend mean's distribution is within 0.01 of normal only from n = 1,025,322; the exact distance gets there at n = 20,652, so the guarantee arrives about 50 times later than the normal shape does
- File: `linkedin-05-sampling-distribution-central-limit-theorem.png`
- Alt text: A long measuring rail running to the horizon, a slate flag near where the heaps turn bell-shaped and a tangerine flag far off

### Prompt

```text
SCENE AND INTENDED USE
The fifth frame of a seven-frame sequence about how slowly the average of a skewed population becomes normal, told through a lake surveyed by soundings. It shows how much later a worst-case guarantee arrives than the shape it guarantees.

SUBJECT
A long horizontal measuring rail with no markings lies on flat open ground, running from the foreground toward a distant horizon. Small heaps of round markers stand on it at intervals: the nearest heaps are lopsided, and heaps further along become more nearly bell-shaped. A small blue-slate flag stands beside the first heap that looks bell-shaped, a short way along the rail. A second flag stands far beyond it, almost at the horizon; that far flag is atomic-tangerine and is the focal element.

KEY DETAILS
The measuring rail and the small round markers are the recurring objects of the sequence. The rail enters at the lower left and recedes toward the upper right, with an empty white-smoke sky above the horizon. Markers jet-black, rail blue-slate, ground a pale silver tint.

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

## 06 — A trench with no floor

- Narrative beat: the CLT needs a finite variance, and without one it never arrives: the mean of n Cauchy draws is as spread as a single draw (an interquartile range of 2.00 from n = 1 to 1,000), and a Pareto t-test with tail index 1.5 stalls near 26.4% in the lower tail
- File: `linkedin-06-sampling-distribution-central-limit-theorem.png`
- Alt text: A lake whose tangerine-outlined trench has no floor and runs off the frame; markers on a rail above it never form a heap

### Prompt

```text
SCENE AND INTENDED USE
The sixth frame of a seven-frame sequence about how slowly the average of a skewed population becomes normal, told through a lake surveyed by soundings. It shows a lake whose trench has no bottom, so no number of soundings settles its average.

SUBJECT
The subject is a lake seen in cross-section with a long shallow bed and one narrow trench that has no floor: the trench runs straight down and out of the bottom edge of the frame. A few sounding lines that fell into it run down out of sight; the rest stop on the shallow bed. Above the waterline, a long horizontal measuring rail with no markings holds small round markers, one per survey's average, strewn unevenly along its whole length with no heap forming. The trench's outline is atomic-tangerine; it is the focal element.

KEY DETAILS
The lake cross-section, its trench, the sounding lines, the measuring rail, and the small round markers are the recurring objects of the sequence. The rail sits in the upper quarter of the frame, the waterline just below it, and the trench runs from the middle of the bed to the bottom edge. Water a pale flat tint of blue-slate, the bed silver with fine hatching, lines, weights and markers jet-black.

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

## 07 — A hundred thousand surveys

- Narrative beat: simulation is the series' instrument: repeat the sampling R times from a fixed seed, count how often the test rejects, and report the rate with its Monte Carlo standard error √(p(1 − p)/R); R = 47,500 holds the error of a 5% rate to 0.1 points
- File: `linkedin-07-sampling-distribution-central-limit-theorem.png`
- Alt text: A grid of many small identical lake drawings, each with its own soundings, and one card set apart and outlined in tangerine

### Prompt

```text
SCENE AND INTENDED USE
The closing frame of a seven-frame sequence about how slowly the average of a skewed population becomes normal, told through a lake surveyed by soundings. It closes the sequence with the method: repeat the survey many times and count.

SUBJECT
A surveyor's worktable seen from above, covered with a tidy grid of many small identical cards. Each card is a tiny drawing of the same lake in cross-section, a long shallow bed with one narrow, deep trench, with its own scatter of thin sounding lines: on most cards the lines miss the trench, and on a few one line falls in. The grid recedes toward the top of the frame, suggesting more cards than can be counted. One card is set slightly apart from the grid, in the lower foreground, and outlined in atomic-tangerine; it is the focal element.

KEY DETAILS
The lake cross-section, its trench, and the sounding lines are the recurring objects of the sequence, here drawn small and repeated. Cards in white-smoke with fine blue-slate borders, the tiny lakes in a pale blue-slate tint with silver beds and jet-black lines. The tabletop is a plain pale silver tint.

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
