# LinkedIn image prompts — five-causes-of-cuda-out-of-memory

Eight alternative image prompts, one per shared feed card, for the abstract editorial-illustration
route. These are not descriptions of the rendered cards in `assets/social/`; those are the shipped
assets and carry their own text. These prompts produce wordless illustrations in one visual world, for
use when a carousel needs imagery rather than typography.

The recurring objects make the article's ledger physical: a long storage shelf divided into bays (the
card), dark crates (tensors), a single tangerine crate that never fits (the request), a closed gate at
the end of the aisle (the error), and a ledger book on a stand that lists only some of the crates
(PyTorch's books). Keeping them constant is what makes the eight read as one sequence.

## 01 — One gate, five reasons

- Narrative beat: The same error stops five different situations; the reason is in what fills the shelf.
- File: linkedin-01-one-gate.png
- Alt text: A closed gate at the end of a storage aisle, a crate waiting before it, the shelf behind it full in five different ways.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel opening frame showing one closed gate that stops a delivery for reasons that differ along the shelf behind it.

SUBJECT
A long storage aisle seen in gentle perspective. On its right runs a shelf divided into five sections of bays; each section is full in its own way: crates with narrow gaps between them, a stack that climbs higher toward the back, a crate tied with a different-coloured strap, crates standing just outside the shelf's marked edge, and one section packed tight with nothing wrong at all. At the aisle's near end a single crate waits in front of a closed gate.

KEY DETAILS
Establish the recurring objects for the whole sequence: the storage shelf of bays, dark crates, the waiting crate, the closed gate, and a small ledger book on a stand beside the gate. Put the single atomic-tangerine accent on the waiting crate. The gate and crate sit in the lower third, the shelf fills the middle, and the top quarter is open white-smoke.

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

## 02 — Gaps that do not add up

- Narrative beat: Fragmentation — plenty of free space in total, none of it in one piece large enough.
- File: linkedin-02-gaps.png
- Alt text: A shelf where every bay holds a wide crate and a narrow gap; a larger crate in front fits none of the gaps.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing free space that exists but is in the wrong shape.

SUBJECT
The storage shelf seen straight on, three tiers of identical bays. Every bay holds one wide dark crate pushed to its left side and leaves a narrow empty gap on its right. In front of the shelf, on the floor, sits a single crate that is wider than any one gap, although all the gaps together are many times wider than it.

KEY DETAILS
Keep the recurring objects from the sequence: the bay shelf, dark crates, the waiting crate, the closed gate at the edge of the frame, the ledger book on its stand. Put the single atomic-tangerine accent on the waiting crate. Draw the gaps as clean white-smoke so their number reads at a glance. The shelf fills the upper two thirds; the waiting crate sits in the lower third, left of centre.

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

## 03 — A stack that only grows

- Narrative beat: A retained graph — every iteration leaves something behind, so memory climbs step by step.
- File: linkedin-03-growing-stack.png
- Alt text: Two stacks of crates side by side: one rising a crate higher at every step toward a ceiling line, one staying level.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing memory that grows a little every iteration until it reaches the ceiling.

SUBJECT
Inside one wide bay of the storage shelf, two stacks of dark crates stand side by side. The left stack rises like a staircase, one crate higher at each of eight evenly spaced positions, its top crate just touching a thin horizontal ceiling line. The right stack stays one crate high at every position, a flat line of crates.

KEY DETAILS
Keep the recurring objects: the bay shelf, dark crates, the waiting crate, the closed gate, the ledger book. Put the single atomic-tangerine accent on the topmost crate of the rising stack, where it meets the ceiling line. The staircase rises from lower left toward upper right; the open white-smoke sits above the level stack.

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

## 04 — The empty spot and the abandoned crate

- Narrative beat: A process that exited gives its memory back; a live orphan keeps holding it.
- File: linkedin-04-orphan.png
- Alt text: One bay holds only the faint outline where a crate used to be; the next still holds a crate whose strap has been cut.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame contrasting space that was released with space still held by something nobody owns.

SUBJECT
Two neighbouring bays of the storage shelf seen up close. The left bay is empty except for the faint dashed outline on its floor where a crate used to stand. The right bay still holds a dark crate whose carrying strap has been cut, the cut ends hanging loose, with no handler anywhere near it.

KEY DETAILS
Keep the recurring objects: the bay shelf, dark crates, the waiting crate partly visible at the frame's lower edge, the closed gate, the ledger book. Put the single atomic-tangerine accent on the cut strap ends. The two bays fill the middle of the frame side by side; the upper third is open white-smoke.

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

## 05 — Crates the ledger does not list

- Narrative beat: Memory outside PyTorch — the process holds it, but PyTorch's books never see it.
- File: linkedin-05-off-the-books.png
- Alt text: An open ledger book beside a shelf; lines in the book match some crates, while other crates sit beside them unrecorded.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing space that is used but missing from the record everyone checks.

SUBJECT
An open ledger book on its stand in the foreground, its pages ruled with plain lines and no writing. Behind it, a section of the storage shelf holds dark crates; thin connector threads run from some of the crates to lines in the open book. Several other crates, larger and grouped together, stand on the same shelf with no thread running to the book at all.

KEY DETAILS
Keep the recurring objects: the bay shelf, dark crates, the waiting crate, the closed gate at the frame's edge, the ledger book. Put the single atomic-tangerine accent on the largest unrecorded crate. The book sits lower left; the shelf fills the upper right; leave the top quarter as open white-smoke.

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

## 06 — Emptying a bin that is already empty

- Narrative beat: empty_cache() cannot rescue the crashed process; everything it could release is already gone.
- File: linkedin-06-empty-bin.png
- Alt text: A small bin tipped upside down with nothing falling out, in front of a shelf that stays exactly as full.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing a cleanup action that frees nothing because the cleanup already happened.

SUBJECT
In front of the storage shelf, a small open bin is tipped upside down in mid-air, and nothing falls out of it. The shelf behind stays packed exactly as before, with the waiting crate still standing in front of the closed gate.

KEY DETAILS
Keep the recurring objects: the bay shelf, dark crates, the waiting crate, the closed gate, the ledger book. Put the single atomic-tangerine accent on the waiting crate. The tipped bin is the central shape, slightly above centre; the shelf forms a quiet band behind it; the lower third is open white-smoke.

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

## 07 — Five checkpoints in order

- Narrative beat: Read the evidence in a fixed order; the first check that holds names the cause.
- File: linkedin-07-checkpoints.png
- Alt text: A path through five small checkpoints in a row, the waiting crate stopped at one of them, the rest ahead open.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing a diagnosis as an ordered series of checks along one path.

SUBJECT
A narrow path winds from the bottom of the frame toward the top through five small identical checkpoint arches spaced evenly along it. The waiting crate has stopped beneath the second arch; the arches beyond it stand open and unused. Beside the path, at a distance, stands the storage shelf.

KEY DETAILS
Keep the recurring objects: the bay shelf, dark crates, the waiting crate, the closed gate at the far end of the path, the ledger book on a stand near the first arch. Put the single atomic-tangerine accent on the waiting crate. The path runs up the centre; the right third is open white-smoke.

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

## 08 — One gap where it is needed

- Narrative beat: Once the cause is named, the fix is specific; here the gaps merge and the crate fits.
- File: linkedin-08-one-gap.png
- Alt text: The shelf rearranged so its crates sit together and one wide gap remains at the end, the waiting crate sliding into it.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel closing frame showing the problem solved by putting free space in one piece.

SUBJECT
The same storage shelf, but its dark crates now stand shoulder to shoulder along one tier, and the free space that was scattered in narrow gaps has gathered into one wide gap at the end. The waiting crate is sliding into that gap. The gate at the end of the aisle stands open.

KEY DETAILS
Keep the recurring objects: the bay shelf, dark crates, the waiting crate, the gate (now open), the ledger book. Put the single atomic-tangerine accent on the waiting crate. The shelf runs across the middle of the frame; the open gate sits at the right edge; the top third is open white-smoke.

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
