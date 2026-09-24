---
name: blog-visuals
description: Select relevant reusable figures from cited papers, and plan and produce every original figure and finished social asset for a technical blog post — diagrams, charts, math figures, a cover prompt, a shared Instagram/LinkedIn carousel, an Instagram Story sequence, and an alternative image-prompt handoff. Use whenever a post needs figures, a cover or hero, social cards, social image prompts, or visual planning before a long technical article.
license: MIT
metadata:
  version: "0.4"
---

# Blog Visuals

Every figure in a post is either the one relevant, rights-cleared figure from a cited paper or our own work. Both travel through one pipeline, use one naming convention, and are handed off as files plus a manifest. This skill never uploads anything.

---

## 1. The pipeline

```
                  ┌─ mermaid ─→ .mmd ─→ mermaid-cli ─────────┐
figure plan       │                                          │
     ↓            │                                          ↓
 route gate ──────┤                                   .svg + .png → manifest.md → user uploads → fill_urls.py
                  │                                          ↑
                  ├─ placed / chart ─→ diagram-design ─→ .html
                  └─ source ─→ extract the rights-cleared paper figure
```

Every figure leaves the plan on one of **seven routes**, and the **route gate** picks it. The gate
is the ordered procedure in `references/visual-taxonomy.md`; it runs once per figure, at plan
time, and produces one token. The sketch above draws only the two routes that reach a drawing
tool. `source` keeps a relevant paper figure as published rather than generating or drawing an
inferior substitute. `mermaid` means Mermaid's **layout engine** places the graph and its
render is what ships. `placed`, `chart` and `plot` mean we position the figure ourselves.
`capture` and `generated` skip the drawing tools entirely.

On the `placed` route, Mermaid is still the **authoring shorthand** for a small diagram, not the
output. It is fast to write, easy to diff, and easy to fix six months later. diagram-design is
then the **renderer**: it discards Mermaid's layout and theme and redraws the content in its own
design system, which is why the output looks like a publication rather than a README.

The published `blog.md` references image URLs, never live Mermaid blocks — on either route. Images render everywhere and do not depend on the page having a Mermaid runtime.

**Mermaid grammars diagram-design can import:** `flowchart`/`graph`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`. For any other type — timeline, Gantt, class, charts, quadrant, Venn, layers, treemap, Sankey — skip Mermaid and author directly in diagram-design.

Keep the editable source its route produces — `.mmd` on `mermaid`, `.html` on `placed` and `chart`, `.py` or hand-authored `.svg` on `plot` — alongside the exported `.svg` and `.png`. That source is what makes an original figure editable later. A `source` figure instead keeps the exact extracted image plus its citation and rights record; do not redraw or restyle it.

---

## 2. Style

Use diagram-design with its **shipped default skin**. When its first-run style gate asks, choose "proceed with the default". Do not customise tokens per post; consistency across hundreds of posts matters more than any single post's palette.

Its design rules apply and are good ones: target density around 4 out of 10, at most about nine nodes, one or two focal nodes per diagram. That ceiling is a limit on **hand placement**, not on the figure: a diagram whose real content needs more than nine nodes routes to `mermaid` (section 4), it is not split into two poorer diagrams.

---

## 3. Figure planning

Plan figures **during the outline phase**, before prose is written. A figure decided afterward gets bolted on; a figure decided first changes how the section is written and usually shortens it.

**The route is decided here**, with the rest of the figure plan, not when someone opens a drawing
tool. Run the gate in `references/visual-taxonomy.md` against the real content of the figure and
write the answer down. A route chosen at drawing time is chosen by whichever tool is already open,
which is how an architecture ends up as four boxes that carry a quarter of it.

For each planned figure record:

- the section it belongs to;
- the one thing it must communicate;
- the **route** — one of `source`, `mermaid`, `placed`, `chart`, `plot`, `capture`, `generated`;
- the **why** — the one clause that settled the route, such as "14 nodes, edges cross";
- a draft caption.

The route and the why travel with the figure into `manifest.md` (section 10).

Budget is roughly one figure per 500–700 words:

| Tier | Figures |
|---|---|
| L1 | 3–5 |
| L2 | 5–8 |
| L3 | 8–12 |
| L4 | 12–18 |

**The test before drawing anything:** would the reader learn more from this than from a well-written paragraph? If no, write the paragraph. A diagram of two boxes and an arrow is a sentence wearing a costume.

---

## 4. Routing

Seven routes, seven tokens. **The gate that picks one — the source-figure check followed by the ordered Q1–Q5 procedure, and the rule
about figures that only fit once you delete half of them — lives in
`references/visual-taxonomy.md`.** Read it before planning figures; do not route from this table
alone.

| Route | For | Produced by | Source kept |
|---|---|---|---|
| `source` | the paper's own figure, only when it directly explains this section and reuse rights are verified | exact extraction from the official paper or author-hosted copy | extracted `.png`, `.svg`, `.jpg`, or `.webp`, plus credit and rights record |
| `mermaid` | graph-shaped content: more than nine nodes, crossing edges, three or more parallel paths, or the post's one end-to-end architecture | Mermaid's layout engine, rendered by mermaid-cli — section 5 | `.mmd` |
| `placed` | everything else that is drawn: structure under nine nodes, containment, layers, byte layouts to scale, small multiples | diagram-design, hand-placed | `.html` |
| `chart` | measured comparison, trend, correlation, part of whole, flow with volume | diagram-design chart types | `.html` |
| `plot` | math, geometry, growth curves | matplotlib or hand-authored SVG | `.py` or `.svg` |
| `capture` | terminal output, query plans, a UI we are running | our own run | the capture |
| `generated` | the cover or hero, and nothing else | external image tool, or a template cover | the prompt |

Before drawing anything based on a paper, inspect that paper's figures. If one figure directly
communicates the exact point the section teaches, prefer the published figure on the `source`
route instead of generating or redrawing a cheaper substitute. This is a relevance rule, not a
request to copy every image: one selected figure must earn its place under the same
"would removing it lose information?" test as every other figure.

Read `references/paper-figures.md` before selecting or extracting one. Reuse requires a verified
licence, permission, or public-domain basis; citation alone is not permission. If rights are
unclear, do not paste the image and do not generate a lookalike. Continue through the route gate
only when an original teaching figure would add our own analysis rather than imitate the paper.

Charts plot numbers that exist in the ledger. Never plot an asymptotic formula and present it as measurement.

---

## 5. Shipping a mermaid-routed figure

The decision is already made: section 4 and `references/visual-taxonomy.md` own it. This
section is only about getting a `mermaid` figure onto the page.

**Do not put a fenced ` ```mermaid ` block in `blog.md`.** The renderer is `react-markdown`
with `remark-gfm`, `remark-math`, `rehype-sanitize` and `rehype-katex` — there is no Mermaid
plugin and the sanitiser strips injected SVG, so the fence reaches the reader as visible
source code. Render it to an image instead:

```bash
npx -y @mermaid-js/mermaid-cli -i assets/fig-NN-<name>.mmd \
    -o assets/fig-NN-<name>.svg -b transparent
```

Keep the `.mmd` as the editable source, export `.svg` and `.png`, and list the PNG in
`manifest.md` exactly like any other figure, with `mermaid` in its Route column. The reader
gets an image that renders anywhere; you keep Mermaid's layout and a source you can re-edit in
one line.

Choosing this route buys layout, nothing else. The node names, the shapes and types, and the
edge labels are still owed — section 6 applies here in full.

Revisit this section if the renderer ever gains a Mermaid plugin — a live fence becomes
available at that point, and only at that point.

---

## 6. Every original diagram answers what, why and how

**This section applies to both routes.** A `mermaid` figure that answers only "what" is as
weak as a placed one, and it is the easier mistake to make, because Mermaid will happily lay
out fifteen bare boxes and look tidy doing it.

A `source` figure is judged by the relevance gate and explained by the surrounding prose; do
not modify the published image to force it into this house format.

A figure that only names its parts is a labelled picture, not an explanation. Before
drawing, write the three sentences the figure has to make recoverable **without** the
surrounding prose:

- **What** — every box carries its real name, and its shape, type or range where one
  exists. "Encoder" is a label; "Encoder E · 3×512×512 → 4×64×64" is information.
- **Why** — what breaks, or what the reader gets wrong, if this component is absent or
  swapped. Put it on the figure as a short verdict, a contrast, or a highlighted path.
- **How** — what actually travels along each edge. A tensor shape, a formula, a count, a
  direction. An unlabelled arrow between two boxes says only "related", which the reader
  already assumed.

If a figure cannot answer all three, it is decoration. Cut it or rewrite the plan.

### Arrows are a correctness surface

Connector bugs are the most common way a redrawn figure becomes *wrong* rather than merely
plain, and they survive every mechanical check the pipeline runs. Routing to `mermaid`
removes the arrow-**geometry** class of bug — the engine lands every edge on a node edge — but
not the wrong-**source-box** class, which is the one that misinforms the reader. Check the
semantics on both routes; check the geometry on placed figures. Hold every connector to
these rules:

- It terminates **on a node edge**, not in open space and not inside the node.
- It enters that edge **head-on**: a horizontal arrow meets a left or right edge, a
  vertical arrow meets a top or bottom edge. An arrow that arrives parallel to the edge it
  lands on reads as a near miss.
- It leaves the box that actually **owns** the thing it represents. Cross-attention leaves
  the text encoder, not the timestep embedding.
- A loop returns to the node it loops over.

Orthogonal routing helpers bend one way only, so check which. A horizontal-then-vertical
elbow always arrives travelling vertically and will stab a side edge; use a
vertical-then-horizontal connector when the target sits beside the source.

Lint it rather than trusting your eye:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint_visuals.py" posts/<slug>/assets/
```

It reports every `marker-end` endpoint that lands on no node or meets an edge side-on, and
every `<text>` whose estimated box leaves the canvas. Text overflow is always a defect. Arrow
reports are advisory — free vectors and plot axes touch no node by design — so read them and
decide, rather than driving the count to zero.

---

## 7. Naming

```
cover.png
fig-01-tcp-handshake.mmd
fig-01-tcp-handshake.html
fig-01-tcp-handshake.svg
fig-01-tcp-handshake.png
```

Numbers match the order of appearance in the post. If a figure is inserted later, renumber everything after it and update the manifest, the placeholders, and the captions together. Half-renumbered figures are worse than badly ordered ones.

For original figures, export both SVG and PNG. PNG @2 for the post, SVG kept for future editing and for anyone who wants to zoom. For a `source` figure, preserve the extracted original; make only a non-altering format conversion when the publishing platform requires one.

---

## 8. Cover image

The cover is generated outside this pipeline. This skill writes `assets/cover-prompt.md`, a full prompt the user pastes into an image tool.

Prompt structure and the fixed house-style block are in `references/cover-prompt.md`. Read that file before writing a cover prompt. The house-style block is what makes covers look like one publication rather than 365 unrelated images, and it is identical in every prompt.

A branded template cover, built in diagram-design and exported to PNG, is the fallback when the user does not want to run an external tool. It is deterministic, on-brand, and can carry real typography.

---

## 9. Alt text and captions

Both are required on every figure. They do different jobs.

**Alt text** describes the figure for someone who cannot see it. 80 to 140 characters. Describe content, not existence.

- Bad: "diagram of TCP"
- Bad: "image showing the handshake process"
- Good: "Three-way handshake: client SYN, server SYN-ACK, client ACK, with sequence numbers on each arrow"

**Caption** tells a sighted reader what to notice. It adds something the figure does not already say.

- Weak: "Figure 3. The TCP handshake."
- Strong: "Figure 3. The connection is established after the second message; the third only confirms it to the server."

Captions are numbered and the prose refers to them by number.

For a `source` figure, the caption also says “Reproduced from,” names the paper and original
figure number, links the source, and states the licence or permission. Do not say “adapted from”
when the image was copied unchanged.

---

## 10. Handoff

Details in `references/handoff.md`. Short version:

`blog.md` carries placeholders: `COVER`, `FIG_01`, `FIG_02`.

`manifest.md` lists every placeholder with its local file, its route, the clause that settled
the route, source credit and rights when applicable, the suggested object key, and its alt text:

```markdown
| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| FIG_01 | fig-01-paper-architecture.png | source | original Figure 2 directly explains this section | Author et al., Paper, Figure 2, source URL | CC BY 4.0 | blog/<slug>/fig-01-v1.png | ... |
| FIG_02 | fig-02-handshake.png | mermaid | 3 participants, message order | — | — | blog/<slug>/fig-02-v1.png | ... |
| FIG_03 | fig-03-record.png | placed | field widths must be to scale | — | — | blog/<slug>/fig-03-v1.png | ... |
```

Route and Why are not bookkeeping for its own sake: they are the record that the gate was
actually run, and they tell the next editor which source file to open.

The user uploads to object storage and runs:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fill_urls.py" posts/<slug>/ urls.txt
```

Paths use a version suffix — `blog/<slug>/fig-01-v1.png` — so an edited figure gets a new URL and no cache anywhere serves the old one. When a figure changes, bump to `v2`.

---

## 11. Social package

After the article is final, read `references/social-assets.md` and produce:

- `assets/social/`: 5–8 shared 1080×1350 feed-card triplets and 3–5 separately
  composed 1080×1920 Story triplets, each as editable HTML, SVG, and PNG.
- `social.md`: LinkedIn and Instagram copy, feed and Story order, link-sticker
  details, and complete per-image accessibility and publishing metadata.

Every social frame carries the full Canery lockup in the template's locked
top-left position. The blog cover stays unbranded. Each technical social card
must use a real article-specific artefact rather than generic metaphor art.

**Social assets are always rendered images, never Mermaid. The route gate in section 4 does
not apply to them.** Three reasons, and they are not negotiable by figure content:

- They are uploaded to Instagram and LinkedIn as image files. There is no Markdown renderer
  of any kind on the other side, so there is nothing for a `.mmd` to become.
- They must carry the Canery lockup, the brand typography, and a fixed 1080×1350 or
  1080×1920 canvas. Mermaid produces none of those, and cannot be made to.
- Their job is to stop a scroll. That is a design job, not a layout job.

Mermaid may still be used upstream — lay a diagram out with it, then restyle it into a card
in the template. Nothing in `assets/social/` ships as a mermaid-cli render.

Then read `references/linkedin-handoff.md` and continue producing the existing
`assets/linkedin-prompts.md` alternative prompt pack. Its prompt structure and
locked illustration style are unchanged in this phase.

This skill renders local social files but does not call an image API, post to a
social platform, or upload anything.
