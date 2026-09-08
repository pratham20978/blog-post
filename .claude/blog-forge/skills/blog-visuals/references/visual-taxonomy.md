# Visual taxonomy

Pick the route by what the figure has to say, not by what looks impressive.

---

## Selection

Ask, in order:

1. What is the one thing this figure must communicate?
2. Could a well-written paragraph do it? If yes, write the paragraph.
3. What kind of thing is it: structure, order, state, quantity, layout, or trace?
4. Route from the table below.

If step 1 needs two sentences to answer, it is two figures.

---

## Routes

| Kind | Shows | Route | Notes |
|---|---|---|---|
| **Structure** | components and their connections | diagram-design architecture | ≤9 nodes; split if more |
| **Containment** | scope, boundaries, nesting | diagram-design nested | trust boundaries, address spaces |
| **Layers** | stacked abstraction levels | diagram-design layers | protocol stacks, storage tiers |
| **Process** | steps with branches | Mermaid flowchart → redraw | one decision per node |
| **Order in time** | messages between actors | Mermaid sequenceDiagram → redraw | handshakes, RPC, syscalls |
| **State** | states, transitions, guards | Mermaid stateDiagram-v2 → redraw | connection state, process lifecycle |
| **Entities** | tables, fields, relationships | Mermaid erDiagram → redraw | schemas |
| **Quantity across categories** | measured comparison | diagram-design bar | ledger numbers only |
| **Trend** | change over a continuous axis | diagram-design line | real measurements |
| **Correlation** | two variables | diagram-design scatter | |
| **Part of whole** | relative sizes | diagram-design treemap | avoid pie |
| **Flow with volume** | quantity splitting and merging | diagram-design Sankey | traffic, request breakdown |
| **Trade-off** | two-axis positioning | diagram-design quadrant | design space comparisons |
| **Overlap** | set relationships | diagram-design Venn | ≤3 sets |
| **Root cause** | causes of one effect | diagram-design fishbone | postmortems |
| **Time span** | events in history | diagram-design timeline | protocol evolution |
| **Byte layout** | packet, record, memory format | diagram-design, to scale | field widths must be proportional |
| **Trace** | algorithm step by step | table, or small multiples | often a table beats a diagram |
| **Math** | curves, geometry, growth | matplotlib or hand SVG | |
| **Real artefact** | terminal output, query plan, UI | capture ourselves | never a stock screenshot |

---

## CS-specific guidance

**Networking.** Sequence diagram for anything with message order. Packet layout to scale, with bit offsets. State machine for connection state. Do not draw the OSI stack again unless the post is actually about layering.

**Operating systems.** Sequence diagram across the syscall boundary, with the user and kernel sides as separate participants. Address space layout as a vertical layer stack. Process lifecycle as a state machine.

**Databases.** B-tree before and after a split is the single most useful database figure. Query plans as trees. Concurrency and isolation as a timeline of two transactions side by side, which makes anomalies visible in a way prose cannot.

**Algorithms.** Trace on a tiny input, usually as a table or small multiples rather than a flowchart. Recursion tree for divide and conquer. Growth charts from measured runtimes, never from plotting the asymptotic form.

**Machine learning.** Architecture diagram with tensor shapes on every edge, because shapes are where the confusion actually lives. A forward pass on 2×2 numbers. Loss curves from real runs.

**Distributed systems.** Sequence diagram with three or more nodes and an injected failure. The failure case is the figure that matters; the happy path is usually obvious.

**Security.** Trust boundaries as containment. Attack as a sequence. Never draw an operational attack procedure; draw the mechanism and the defence.

**Compilers.** AST for a short expression. IR before and after one pass, side by side.

---

## Data figure rules

- Numbers come from the ledger. If a number has no ledger row, the chart cannot be drawn.
- The caption states the setup: hardware, dataset size, version.
- Axes are labelled with units.
- Log scale is labelled as log scale.
- Zero baseline on bar charts, always.
- Never plot a formula and present it as data. If it is a model, say it is a model in the caption.

---

## When not to draw

- Two boxes and an arrow. Write the sentence.
- A list rendered as shapes. Use a list.
- A diagram the prose never refers to. Cut it.
- A diagram that repeats the previous one at a different zoom, with nothing new.
- Decoration to break up text. If the text needs breaking up, the text is too long.
