# Visual taxonomy

Pick the route by what the figure has to say, not by what looks impressive.

---

## Selection

Every figure carries a **route**, decided before anything is drawn and recorded in the figure
plan and the manifest. There are seven routes, and the token in the left column is the one that
goes in the manifest:

| Route | What it means | Source file kept |
|---|---|---|
| `source` | one relevant, rights-cleared figure extracted unchanged from a cited paper | extracted `.png`, `.svg`, `.jpg`, or `.webp`, with credit and rights in the manifest |
| `mermaid` | graph-shaped content laid out by Mermaid's engine, rendered by mermaid-cli | `.mmd` |
| `placed` | hand-placed diagram-design HTML | `.html` |
| `chart` | diagram-design chart drawn from ledger numbers | `.html` |
| `plot` | matplotlib or hand-authored SVG for math, geometry, curves | `.py` or `.svg` |
| `capture` | a real artefact we captured ourselves: terminal output, `EXPLAIN`, a UI | the capture itself |
| `generated` | externally generated image; the cover only | the prompt |

Two questions come before the gate, because either can end the figure:

1. What is the one thing this figure must communicate? If answering takes two sentences, it is
   two figures.
2. Could a well-written paragraph do it? If yes, write the paragraph.

Then work the gate in order and **stop at the first question that answers yes**. The gate runs
for every figure, every time. Skipping it is how a post ends up with eight sparse
boxes-and-arrows pictures that each carry a third of an architecture.

**Source check — Does a cited paper already contain the exact relevant figure?** Inspect the
paper's figures and captions before planning a replacement. Route to `source` and stop only when
the figure directly teaches this section's one point, the prose will discuss it, and its reuse
rights are verified. Do not take every image from the paper, a merely related image, or a figure
that repeats the prose. Follow `paper-figures.md` for the relevance, rights, extraction, and
attribution gates. If reuse rights are unclear, do not generate or redraw a lookalike; continue
only if an original figure would contribute our own analysis.

**Q1 — Is this measured data from the ledger?** Counts, latencies, sizes, rates, a curve fitted
to real runs. Route to `chart` when diagram-design draws it, `plot` when it needs matplotlib or
hand-authored SVG. Stop.

**Q2 — Is this a real artefact we can capture ourselves?** Terminal output, a query plan, a
profiler view, a UI we are running. Route to `capture`. Stop.

**Q3 — Is it graph-shaped?** Its content is nodes joined by typed edges — components, stages,
states, entities, messages — and the reader's takeaway is the whole connected path rather than
any single box. Count the nodes and the crossings **honestly, on the real content**, not on the
simplified version you wish you could draw. Route to `mermaid` if any one of these holds:

- more than nine nodes; or
- any edge that must cross another; or
- three or more parallel paths; or
- this is the post's one end-to-end architecture view.

Stop.

**Q4 — Does the figure's value come from something Mermaid cannot draw?** Proportional widths, a
byte layout to scale, geometry, small multiples, a grid of real values, a depiction of the thing
itself rather than a box naming it. Route to `placed` — or to `plot` when the figure is a curve
or a construction that wants matplotlib or hand-authored SVG. Stop.

**Q5 — Otherwise** — route to `placed`. Under nine nodes, no crossings, nothing exotic: hand
placement is denser and on-brand, and it carries a tensor shape or a real number on every edge.

**A figure you can only hand-place by dropping nodes, dropping edge labels, or splitting it in
two is a `mermaid` figure. The simplification is the defect, not the fix.** The moment you catch
yourself deciding which three components to leave out so the boxes fit, the gate has already
answered Q3 for you.

Record the route and the one-clause reason that settled it — "14 nodes, edges cross", "needs
tensor shape on every stage" — in the figure plan, and carry both into `manifest.md`.

### Both routes owe the reader the same data

Routing to `mermaid` buys layout, not licence to say less. A Mermaid diagram of bare unlabelled
boxes is **worse** than a placed one, because it spends the extra nodes on nothing. On both
routes, every node keeps its real name plus its shape, type or range, and every edge keeps its
label. `Encoder` is a box; `Encoder E · 3×512×512 → 4×64×64` is a figure. An unlabelled arrow
says only "related", which the reader already assumed, whoever laid it out.

---

## Routes

| Kind | Shows | Route | Drawn with | Notes |
|---|---|---|---|---|
| **Published paper figure** | the exact method, architecture, or result discussed in this section | `source` when directly relevant and rights-cleared | extract the original; do not redraw or generate | record paper, original figure number, source URL, and rights |
| **Structure, ≤9 nodes** | components and their connections | `placed` | diagram-design architecture | no crossing edges; shapes and per-edge data are the payoff |
| **Whole-system architecture** | the end-to-end path in one view | `mermaid` | Mermaid layout, mermaid-cli render | never split it in two to make it hand-placeable |
| **Containment** | scope, boundaries, nesting | `placed` | diagram-design nested | trust boundaries, address spaces |
| **Layers** | stacked abstraction levels | `placed` | diagram-design layers | protocol stacks, storage tiers |
| **Process** | steps with branches | `placed`, or `mermaid` past Q3 | Mermaid flowchart source → diagram-design redraw | one decision per node |
| **Order in time** | messages between actors | `mermaid` at three or more participants, else `placed` | Mermaid `sequenceDiagram` | handshakes, RPC, syscalls |
| **State** | states, transitions, guards | `mermaid` past Q3, else `placed` | Mermaid `stateDiagram-v2` | connection state, process lifecycle |
| **Entities** | tables, fields, relationships | `mermaid` at four or more entities, else `placed` | Mermaid `erDiagram` | schemas |
| **Quantity across categories** | measured comparison | `chart` | diagram-design bar | ledger numbers only |
| **Trend** | change over a continuous axis | `chart` | diagram-design line | real measurements |
| **Correlation** | two variables | `chart` | diagram-design scatter | |
| **Part of whole** | relative sizes | `chart` | diagram-design treemap | avoid pie |
| **Flow with volume** | quantity splitting and merging | `chart` | diagram-design Sankey | traffic, request breakdown |
| **Trade-off** | two-axis positioning | `placed` | diagram-design quadrant | design space comparisons |
| **Overlap** | set relationships | `placed` | diagram-design Venn | ≤3 sets |
| **Root cause** | causes of one effect | `placed` | diagram-design fishbone | postmortems |
| **Time span** | events in history | `placed` | diagram-design timeline | protocol evolution |
| **Byte layout** | packet, record, memory format | `placed` | diagram-design, to scale | field widths must be proportional — Q4 |
| **Trace** | algorithm step by step | `placed`, or no figure | small multiples, or a Markdown table | often a table beats a diagram |
| **Math** | curves, geometry, growth | `plot` | matplotlib or hand SVG | |
| **Real artefact** | terminal output, query plan, UI | `capture` | our own run | never a stock screenshot |
| **Cover** | the post's one hero image | `generated`, or `placed` for a diagram-design template cover | external image tool, or diagram-design | `generated` is used for the cover and nothing else |

---

## Worked decisions

| Figure | The question that settled it | Route |
|---|---|---|
| A paper's Figure 2, which is the architecture this section walks through | Source check — this exact rights-cleared figure is the object being explained | `source` |
| The whole diffusion system: training loop, sampling loop, and the conditioning chain feeding both | Q3 — 16 nodes, two loops that cross, and it is the post's one end-to-end view | `mermaid` |
| A U-Net with the tensor shape on every down, bottleneck and up stage | Q4 — the shapes on the stages *are* the figure, and they need the room a placed layout gives them | `placed` |
| The TCP three-way handshake | Q3 — messages between actors in order; Mermaid's `sequenceDiagram` places the lifelines correctly and for free | `mermaid` |
| A B-tree node before and after a split | Q4 — the key slots must be drawn to scale, side by side, so the reader sees the half-empty node | `placed` |

Each row's middle column is the shape of the "Why" clause the manifest wants: the question, and
the fact about the real content that answered it.

---

## CS-specific guidance

**Networking.** Sequence diagram for anything with message order. Packet layout to scale, with bit offsets. State machine for connection state. Do not draw the OSI stack again unless the post is actually about layering.

**Operating systems.** Sequence diagram across the syscall boundary, with the user and kernel sides as separate participants. Address space layout as a vertical layer stack. Process lifecycle as a state machine.

**Databases.** B-tree before and after a split is the single most useful database figure. Query plans as trees. Concurrency and isolation as a timeline of two transactions side by side, which makes anomalies visible in a way prose cannot.

**Algorithms.** Trace on a tiny input, usually as a table or small multiples rather than a flowchart. Recursion tree for divide and conquer. Growth charts from measured runtimes, never from plotting the asymptotic form.

**Machine learning.** Architecture diagram with tensor shapes on every edge, because shapes are where the confusion actually lives. A forward pass on 2×2 numbers. Loss curves from real runs. The full system view — data, training, sampling, conditioning — is the case Q3 exists for; route it to `mermaid` rather than shedding components until it fits.

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
- A paper image that is merely related to the topic rather than necessary to the section. Leave it in the paper.
- Decoration to break up text. If the text needs breaking up, the text is too long.
