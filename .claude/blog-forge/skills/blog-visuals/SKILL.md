---
name: blog-visuals
description: Plan and produce every figure for a technical blog post — diagrams, charts, math figures, a cover prompt, and a coordinated LinkedIn visual-prompt handoff — then prepare files for manual upload. Use whenever a post needs figures, a cover or hero, social image prompts, a LinkedIn carousel, or visual planning before a long technical article.
license: MIT
metadata:
  version: "0.1"
---

# Blog Visuals

Every figure in a post is our own work, produced through one pipeline, named by one convention, and handed off as files plus a manifest. This skill never uploads anything.

---

## 1. The pipeline

```
figure plan  →  Mermaid source (.mmd)  →  diagram-design redraw  →  .html  →  .svg + .png
                                                                              ↓
                                                     manifest.md → user uploads → fill_urls.py
```

Mermaid is the **authoring shorthand**, not the output. It is fast to write, easy to diff, and easy to fix six months later. diagram-design is the **renderer**: it discards Mermaid's layout and theme and redraws the content in its own design system, which is why the output looks like a publication rather than a README.

The published `blog.md` references image URLs, never live Mermaid blocks. Images render everywhere and do not depend on the page having a Mermaid runtime.

**Mermaid grammars diagram-design can import:** `flowchart`/`graph`, `sequenceDiagram`, `stateDiagram-v2`, `erDiagram`. For any other type — timeline, Gantt, class, charts, quadrant, Venn, layers, treemap, Sankey — skip Mermaid and author directly in diagram-design.

Keep the `.mmd`, the `.html`, the `.svg` and the `.png`. The first two are what make a figure editable later.

---

## 2. Style

Use diagram-design with its **shipped default skin**. When its first-run style gate asks, choose "proceed with the default". Do not customise tokens per post; consistency across hundreds of posts matters more than any single post's palette.

Its design rules apply and are good ones: target density around 4 out of 10, at most about nine nodes, one or two focal nodes per diagram. A diagram that needs more than nine nodes is two diagrams.

---

## 3. Figure planning

Plan figures **during the outline phase**, before prose is written. A figure decided afterward gets bolted on; a figure decided first changes how the section is written and usually shortens it.

For each planned figure record: the section it belongs to, the one thing it must communicate, the route, and a draft caption.

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

Full mapping in `references/visual-taxonomy.md`. Summary:

| The figure's job | Route |
|---|---|
| Cover or hero | prompt for external generation, or a template cover |
| Structure, components, topology | diagram-design architecture / nested / layers |
| Process, decision logic, algorithm flow | Mermaid flowchart → diagram-design |
| Protocol, handshake, message order | Mermaid sequenceDiagram → diagram-design |
| Lifecycle, connection state, transitions | Mermaid stateDiagram-v2 → diagram-design |
| Schema, entities, relationships | Mermaid erDiagram → diagram-design |
| Real measured data | diagram-design chart types, numbers from the ledger only |
| Math, geometry, growth curves | matplotlib or hand-authored SVG |
| Memory layout, packet or record format | diagram-design, laid out to scale |
| Algorithm trace | table, or small multiples |
| Screenshot, terminal output, real artefact | capture it ourselves |

Never reproduce a figure from a paper, textbook, or documentation site. Redraw from understanding, and credit the source of the idea in the caption. This is a copyright line.

Charts plot numbers that exist in the ledger. Never plot an asymptotic formula and present it as measurement.

---

## 5. Naming

```
cover.png
fig-01-tcp-handshake.mmd
fig-01-tcp-handshake.html
fig-01-tcp-handshake.svg
fig-01-tcp-handshake.png
```

Numbers match the order of appearance in the post. If a figure is inserted later, renumber everything after it and update the manifest, the placeholders, and the captions together. Half-renumbered figures are worse than badly ordered ones.

Export both SVG and PNG. PNG @2 for the post, SVG kept for future editing and for anyone who wants to zoom.

---

## 6. Cover image

The cover is generated outside this pipeline. This skill writes `assets/cover-prompt.md`, a full prompt the user pastes into an image tool.

Prompt structure and the fixed house-style block are in `references/cover-prompt.md`. Read that file before writing a cover prompt. The house-style block is what makes covers look like one publication rather than 365 unrelated images, and it is identical in every prompt.

A branded template cover, built in diagram-design and exported to PNG, is the fallback when the user does not want to run an external tool. It is deterministic, on-brand, and can carry real typography.

---

## 7. Alt text and captions

Both are required on every figure. They do different jobs.

**Alt text** describes the figure for someone who cannot see it. 80 to 140 characters. Describe content, not existence.

- Bad: "diagram of TCP"
- Bad: "image showing the handshake process"
- Good: "Three-way handshake: client SYN, server SYN-ACK, client ACK, with sequence numbers on each arrow"

**Caption** tells a sighted reader what to notice. It adds something the figure does not already say.

- Weak: "Figure 3. The TCP handshake."
- Strong: "Figure 3. The connection is established after the second message; the third only confirms it to the server."

Captions are numbered and the prose refers to them by number.

---

## 8. Handoff

Details in `references/handoff.md`. Short version:

`blog.md` carries placeholders: `COVER`, `FIG_01`, `FIG_02`.

`manifest.md` lists every placeholder with its file, suggested storage path, and alt text.

The user uploads to object storage and runs:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fill_urls.py" posts/<slug>/ urls.txt
```

Paths use a version suffix — `blog/<slug>/fig-01-v1.png` — so an edited figure gets a new URL and no cache anywhere serves the old one. When a figure changes, bump to `v2`.

---

## 9. LinkedIn sequence

After the article is final, read `references/linkedin-handoff.md`. Produce:

- `assets/linkedin-prompts.md`: 4–10 numbered, self-contained 4:5 prompts that
  form one teaching sequence, each with a narrative beat, filename, and alt text.
- `linkedin.md`: the post copy, carousel order, accessibility checklist, and a
  first comment containing the resolved Canery article URL.

This skill writes prompts and copy only. It does not call an image API, create
the carousel bitmaps, post to LinkedIn, or upload anything.
