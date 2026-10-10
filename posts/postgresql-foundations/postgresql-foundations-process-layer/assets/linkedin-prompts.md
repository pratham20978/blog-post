# LinkedIn image prompts — postgresql-foundations-process-layer

## 01 — one parent

- Narrative beat: PostgreSQL is a supervisor and a crowd of children; only the postmaster is allowed to fork.
- File: `linkedin-01-one-parent.png`
- Alt text: One highlighted postmaster square fans lines to backend and background-process squares arranged in one row below.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel opening frame that introduces PostgreSQL as a supervised process tree rather than one monolithic program.

SUBJECT
Place one small highlighted square near the upper centre. Fan nine fine straight lines from it to nine identical squares across the lower third, representing client backends and permanent background processes.

KEY DETAILS
The parent square is the single focal point. Child squares share equal size and spacing. Lines never cross. Leave generous negative space so the hierarchy reads instantly at mobile size. The physical idea is one robust parent and many specialised children; use no labels or text inside the image.

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

## 02 — five passes

- Narrative beat: The same dead-row set makes vacuum walk both indexes five times at 1 MB but once at 256 MB.
- File: `linkedin-02-five-passes.png`
- Alt text: Two horizontal bands compare five repeated index blocks above with one full-width index block below.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame that visualises five complete PostgreSQL index-vacuum cycles versus one for the same table cleanup.

SUBJECT
Build two stacked experiment bands. Each begins with one long thin heap bar. Beneath the upper heap, place five equal index blocks with narrow gaps. Beneath the lower heap, place one wide index block spanning the identical total width.

KEY DETAILS
Highlight only the upper five-pass experiment. Both heap bars must be exactly equal because the heap is scanned once in either run. The repeated lower blocks represent full walks of the same two indexes, not five different indexes. Keep the comparison symmetrical, sparse, and readable without numbers or labels.

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

## 03 — thirty seconds

- Narrative beat: A qualified table waits for the autovacuum launcher’s next visit, then the worker finishes almost immediately.
- File: `linkedin-03-thirty-seconds.png`
- Alt text: A long wait band runs from a dark start dot to an orange launcher dot followed by a tiny burst of work.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame contrasting autovacuum discovery latency with the much shorter cleanup interval.

SUBJECT
Draw one long horizontal timeline across the middle. Put a small dark dot at the left edge for the qualifying update and one highlighted dot near the right edge for the launcher visit. Immediately after the highlighted dot, add a tiny cluster of short marks for the worker’s brief run.

KEY DETAILS
A faint band must fill almost the entire distance between the two dots, making the wait visually dominant. The work burst should be visibly tiny but not disappear at mobile size. Use empty space above and below to preserve the contrast. Do not add clocks, labels, digits, or interface chrome.

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

## 04 — one budget

- Narrative beat: More autovacuum workers divide one I/O cost budget instead of multiplying the cluster’s throughput.
- File: `linkedin-04-one-budget.png`
- Alt text: Three equal-width budget bars are divided into one, three, and eight worker segments without changing total width.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame showing that one, three, and eight autovacuum workers share one fixed total budget.

SUBJECT
Stack three horizontal bars with identical outer width. Make the top bar one solid segment, the middle bar three equal segments with narrow gaps, and the bottom bar eight equal segments with narrow gaps.

KEY DETAILS
Highlight only the single-segment top bar. The outer width of all three rows must remain visually identical even after the gaps are introduced; that invariant is the teaching point. Align every row to the same left and right bounds. Avoid worker icons, speed gauges, labels, numbers, or decorative arrows.

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

## 05 — sixteen times

- Narrative beat: Removing the per-commit disk wait greatly increases throughput while accepting bounded recent-commit loss after a crash.
- File: `linkedin-05-sixteen-times.png`
- Alt text: A short dark throughput bar stands beside a much taller highlighted bar on the same baseline.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel frame comparing the measured throughput of synchronous and asynchronous PostgreSQL commit paths.

SUBJECT
Place two vertical bars on one shared baseline with a wide gap. The left bar is short and dark. The right bar is highlighted and approximately sixteen times taller, reaching toward the upper third.

KEY DETAILS
Keep bar widths equal and make height the only changing variable. Add a subtle sequence of many tiny marks beneath the short bar and only two marks beneath the tall bar to suggest many disk syncs versus two, without using digits. Preserve large negative space and avoid implying that the faster path has stronger durability.

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

## 06 — one killed backend

- Narrative beat: One child dies abnormally, so the postmaster clears every child and rebuilds safe shared state.
- File: `linkedin-06-one-killed-backend.png`
- Alt text: One missing child square causes every line from the parent square to stop, leaving the entire process row disconnected.

### Prompt

```text
SCENE AND INTENDED USE
A 4:5 LinkedIn carousel closing frame that explains why one killed PostgreSQL backend causes every session to disconnect before recovery.

SUBJECT
Place one parent square above a row of identical child squares. Leave one child position empty and mark that gap with a small highlighted cross. Draw lines from the parent toward every child position, but stop every line at the same horizontal break before it reaches the row.

KEY DETAILS
Reuse the exact square scale and hierarchy from frame one so the sequence closes visually. The empty child is the initiating failure; the uniformly severed lines represent the deliberate whole-cluster reset. Keep the parent intact, because the postmaster survives to recover. Use no flames, explosions, text, labels, or warning symbols beyond the small cross.

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
