# LinkedIn image prompts — distributions-as-generative-stories

Six frames, one teaching arc: pebbles landing by chance on a grid, the Poisson → cups of different widths, rates that differ → two shelves that match until a second fall, proneness against contagion → two hills alike in the middle, one with a far boulder, the tail → a curved rail that looks straight through a window, the log–log trap → a workbench with a blank notebook, write the story first.

**The finished social cards are already built** — see `social/` and `social.md`, rendered in the house template with the post's own numbers. These prompts are the alternative route for a text-free illustration treatment from an image model.

Every prompt is self-contained. Paste any single one without carrying context.

---

## 01 — Pebbles on the grid

- Narrative beat: each event lands in one square of many by chance and independently, so each square's count is binomial and, with many rare chances, Poisson; the story predicts how many squares hold 0, 1, 2 events before any are counted
- File: `linkedin-01-distributions-as-generative-stories.png`
- Alt text: A flat grid of square tiles scattered with small pebbles, most tiles holding none or one, one tangerine pebble falling toward the grid

### Prompt

```text
SCENE AND INTENDED USE
The opening frame of a six-frame sequence about choosing a probability distribution from the process that made the data. It shows events landing by chance on a grid of squares.

SUBJECT
A flat grid of square paving tiles, eight by ten, seen from a high three-quarter angle. Small round pebbles lie scattered across it, each dropped from above and landing on a tile by chance: most tiles hold no pebble or one, a few hold two, one holds three, with no clustering. One more pebble hangs in the air above the grid, about to land, with a faint dotted line below it marking its path. That falling pebble is atomic-tangerine; it is the focal element.

KEY DETAILS
The tiled grid and the small round pebbles are the recurring objects of the sequence. The grid fills the lower two thirds of the frame; the falling pebble sits in the upper middle, above the grid's centre. Tiles in silver with blue-slate joints, resting pebbles in jet-black.

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

## 02 — Cups of different widths

- Narrative beat: give each unit its own rate, drawn from a gamma, and the counts spread wider than a Poisson: the variance is the Poisson noise plus the spread of the rates, and the counts become negative binomial
- File: `linkedin-02-distributions-as-generative-stories.png`
- Alt text: A row of cups with mouths of different widths under falling pebbles, wide cups holding many, narrow ones few, the widest rim tangerine

### Prompt

```text
SCENE AND INTENDED USE
The second frame of a six-frame sequence about choosing a probability distribution from the process that made the data. It shows units that catch events at different rates.

SUBJECT
A single row of twelve small open cups standing on a shelf under an even fall of small round pebbles. The cups have mouths of different widths, a few wide, most narrow, so after the fall the wide cups hold many pebbles and the narrow cups hold few or none. The widest cup has an atomic-tangerine rim; it is the focal element.

KEY DETAILS
The small round pebbles are the same as in the earlier frames of the sequence; the shelf of cups is a new recurring object that returns in later frames. The shelf runs across the middle of the frame; the falling pebbles fill the space above it. Cups in silver with blue-slate outlines, pebbles in jet-black.

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

## 03 — Two shelves, a second fall

- Narrative beat: proneness, a fixed rate per unit, and contagion, where each event raises the chance of the next, give the same counts in one period; only a second period tells them apart
- File: `linkedin-03-distributions-as-generative-stories.png`
- Alt text: Two shelves of cups that match after a first fall of pebbles; in a second fall one lower cup has grown a wide tangerine funnel

### Prompt

```text
SCENE AND INTENDED USE
The third frame of a six-frame sequence about choosing a probability distribution from the process that made the data. It shows two different processes that produce the same first count.

SUBJECT
Two shelves of cups, one above the other. On the upper shelf the cups have fixed mouths of different widths. On the lower shelf every cup starts with the same narrow mouth, but each cup that has caught a pebble has grown a slightly wider funnel on top, so cups that caught early catch more later. After a first fall both shelves hold the same pattern of pebble counts. A second fall of pebbles is beginning above both shelves. One cup on the lower shelf, whose funnel has grown widest, has an atomic-tangerine funnel; it is the focal element.

KEY DETAILS
The cups and the small round pebbles are the same as in the earlier frames of the sequence. The two shelves sit in the middle of the frame with even space between them; the second fall of pebbles starts near the top. Cups and funnels in silver with blue-slate outlines, pebbles in jet-black.

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

## 04 — Two hills, one far boulder

- Narrative beat: a t distribution scaled to the normal's variance looks alike in the middle but puts 56 times as much probability beyond four standard deviations, and a small sample usually shows none of it
- File: `linkedin-04-distributions-as-generative-stories.png`
- Alt text: Two hills of equal size side by side, one smooth, the other with low ridges running far out to one far tangerine boulder near the edge

### Prompt

```text
SCENE AND INTENDED USE
The fourth frame of a six-frame sequence about choosing a probability distribution from the process that made the data. It shows two shapes that agree in the middle and disagree far out.

SUBJECT
Two smooth hills drawn as simple profiles on a long, flat plain, side by side and of the same overall size. The left hill falls quickly to the flat ground on both sides. The right hill has a slightly sharper top and long, very low ridges that run far out across the plain on both sides. Far out on one of these low ridges, near the edge of the frame, sits a single small boulder; nothing sits that far out beside the left hill. The boulder is atomic-tangerine; it is the focal element.

KEY DETAILS
The small round pebbles from the earlier frames lie in a light scatter at the foot of both hills, so the hills read as heaps of the same pebbles. The two hills fill the lower half of the frame; the upper half is near-empty. Hills in silver with jet-black profiles, the plain a fine blue-slate line.

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

## 05 — The straight window on a curved rail

- Narrative beat: the tail of a lognormal sample looks straight on log–log axes over the window people fit, with R² near 0.99, so a straight line on a log–log plot is not a test for a power law
- File: `linkedin-05-distributions-as-generative-stories.png`
- Alt text: A rail curving gently downward, with a window frame over one section where it looks straight and a tangerine ruler laid along it

### Prompt

```text
SCENE AND INTENDED USE
The fifth frame of a six-frame sequence about choosing a probability distribution from the process that made the data. It shows how a curved shape can look straight through a narrow window.

SUBJECT
A long, thin rail running from the upper left to the lower right of the frame and bending gently downward along its whole length. A plain rectangular window frame stands over one short section of the rail, so that only that section shows through it, and inside the window the rail looks almost straight. A straight ruler is laid along the rail inside the window and matches it closely there. Outside the window the rail visibly bends away from the ruler's line. The ruler is atomic-tangerine; it is the focal element.

KEY DETAILS
Faint grid lines behind the rail are evenly spaced in both directions, like log-scaled graph paper drawn with no numbers. The window sits slightly right of centre. Rail in jet-black, window frame in blue-slate, grid in pale silver.

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

## 06 — Write the story first

- Narrative beat: the method in one picture: write down how each number was made, derive the family from that story, then test what it predicts against the data
- File: `linkedin-06-distributions-as-generative-stories.png`
- Alt text: A workbench with the tiled grid, a shelf of cups and a hill of pebbles, a blank notebook and a tangerine pencil laid across its open pages

### Prompt

```text
SCENE AND INTENDED USE
The closing frame of a six-frame sequence about choosing a probability distribution from the process that made the data. It shows the method: write the process down first, then test it.

SUBJECT
A wide wooden workbench seen from a high angle. On it, small and neatly arranged, sit the objects from the earlier frames: a little tiled grid with scattered pebbles, a short shelf of cups of different widths, and a small heap of pebbles shaped like a hill. In the front centre lies an open notebook with blank pages showing only a few simple line sketches of these same objects, no writing. A pencil lies across the open pages. The pencil is atomic-tangerine; it is the focal element.

KEY DETAILS
The grid, the cups, the pebbles and the hill are the recurring objects of the sequence, drawn at the same scale and in the same style as before. The notebook sits in the lower middle; the objects are arranged in an arc behind it. Workbench in silver with blue-slate grain lines, objects in their earlier colours.

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
