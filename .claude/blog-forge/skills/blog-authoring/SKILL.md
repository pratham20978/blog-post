---
name: blog-authoring
description: Write a long-form computer-science education blog post as a single Markdown file, with researched sources, figures, and a pre-publish quality gate. Use this whenever the user asks to write, draft, plan, outline, expand, or review a blog post, article, tutorial, explainer, or deep dive on any CS or engineering topic — networking, operating systems, databases, algorithms, machine learning, compilers, security, distributed systems, computer architecture, or theory. Also use it when the user names a topic and says "post", "article", "write this up", or refers to a slug or an existing post folder. Trigger even if the user does not say the word "blog".
license: MIT
metadata:
  version: "0.2"
---

# Blog Authoring

Produce one publishable `blog.md` per topic: a computer-science education article for students and working engineers, 2,000 to 10,000 words, with real sources and real figures.

This skill owns **structure, depth, drafting, and the quality gate**. It does not search and it does not draw. It decides what is needed and delegates.

---

## 1. What good looks like

The reader is a CS student or a working engineer. They arrived from a search or a tag page. They will decide in eight seconds whether to stay.

A post earns its length or it loses it. Four things separate a real article from generated filler:

- **It answers early.** The core answer sits in the first 100 words, before any setup.
- **It shows before it formalises.** A concrete instance with real numbers comes before the general form. Novices need the worked case; experts skip it in two seconds.
- **Every claim traces to a source.** No remembered benchmarks, no invented complexity bounds, no approximate dates.
- **Every figure carries information** the prose could not carry alone, and the prose points at it.
- **Its explanation is self-contained.** The article and images teach the concept; an optional public GitHub lab carries runnable code, not missing definitions or reasoning.
- **It introduces terms before relying on them.** The first meaningful use gives the exact name, what the term means here, why it is used, and when it matters.

If a section cannot meet these, the section is cut. Never pad to hit a word count.

---

## 2. Pipeline

Run these in order. Stop at the checkpoints and wait for the user.

| Phase | Does | Output |
|---|---|---|
| 0 Brief | Fix topic, subject area, depth tier, audience | in conversation |
| 1 Research | Find and tier sources, build the claim ledger | `research/ledger.md` |
| **CHECKPOINT A** | Show source list and what the post can honestly claim | |
| 2 Outline | Section skeleton, word budget, figure plan, term map | `outline.md` |
| **CHECKPOINT B** | User approves before any long prose is written | |
| 3 Draft | Write section by section against the budget | `blog.md` |
| 4 Assets | Build figures, an optional runnable lab, and social handoff | `assets/`, optional `lab/`, `manifest.md`, `linkedin.md` |
| 5 Assemble | Frontmatter, figure placeholders, captions | `blog.md` |
| 6 Gate | Run the checklist and the validator | pass/fail report |
| **CHECKPOINT C** | Hand off for upload and publish | |

Checkpoint B matters most. Approving an outline costs the user one minute. Rewriting 5,000 words costs an hour.

Skip phases only when the user asks for one part (`/blog-forge:research`, `/blog-forge:visuals`).

---

## 3. Depth tiers

| Tier | Words | Figures | Use |
|---|---|---|---|
| **L1** Primer | 2,000–3,000 | 3–5 | one concept, daily |
| **L2** Standard | 3,000–5,000 | 5–8 | daily default |
| **L3** Deep dive | 5,000–7,500 | 8–12 | algorithm plus proof plus implementation |
| **L4** Pillar | 7,500–10,000 | 12–18 | subject cornerstone, monthly |

Default to **L1 or L2**. Pick L2 unless the topic is narrow enough for L1 or the user asks for depth.

Word count is an **output of the section budget, not a target**. Read `references/depth-tiers.md` for the per-section allocation and the expand protocol before writing the outline.

---

## 4. Section order

Load `references/structure.md` for the full definition of each section. The order is fixed:

```
frontmatter
page shell renders the title as the only H1
## Insights              ← the answer, first 100 words
Who this is for          ← difficulty, prerequisites, time
## Why this matters
## The problem
## Worked example
## Intuition
## <topic sections>      ← 1–6, the body, tier-dependent
## The math              ← when the topic has math
## Implementation        ← when the topic has code
## Limitations and common mistakes
## Key takeaways
## Try it yourself       ← optional
## References
```

`Insights` is this blog's name for the lead summary. Two to four sentences, most important takeaway first, written so a reader who stops there still gained something.

---

## 5. Delegation

| Need | Load |
|---|---|
| Sources, papers, docs, any factual claim | **blog-research** skill |
| Any figure, diagram, chart, cover image | **blog-visuals** skill |
| Actual diagram rendering | blog-visuals calls **diagram-design** |

Do not search the web directly from this skill. Do not hand-write SVG. The specialist skills carry rules this one does not.

---

## 6. Reference files

Load only what the current phase needs.

| File | Load when |
|---|---|
| `references/structure.md` | writing the outline or any section |
| `references/depth-tiers.md` | setting the budget, or expanding a post |
| `references/writing-craft.md` | drafting prose |
| `references/math.md` | the post has equations |
| `references/frontmatter.md` | assembling the file |
| `references/subject-playbooks.md` | at brief time, to learn the subject's conventions |
| `assets/post-template.md` | starting a new post |
| `assets/checklist.md` | phase 6 |

---

## 7. Output contract

One folder per post, slug-named:

```
posts/<slug>/
├── blog.md              the deliverable, with figure placeholders
├── outline.md           section skeleton and budget
├── manifest.md          upload checklist: placeholder → file → alt text
├── linkedin.md          LinkedIn post, carousel order, and first comment
├── research/ledger.md   claim → source → URL → access date
├── lab/                 optional runnable code published separately to GitHub
└── assets/
    ├── cover-prompt.md
    ├── linkedin-prompts.md
    ├── fig-01-<name>.mmd     Mermaid source, when used
    ├── fig-01-<name>.html    diagram-design source, re-editable
    ├── fig-01-<name>.svg
    └── fig-01-<name>.png
```

Images and labs are **not** uploaded by this skill. `blog.md` carries image placeholders like `FIG_03` and, when a lab exists, the base placeholder `LAB_REPO`. The user uploads images to object storage, publishes only the lab to a public GitHub repository, adds both public URLs to `manifest.md` order, and runs `scripts/fill_urls.py` to swap them in.

Only `blog.md` and the uploaded images are public on the website. A runnable `lab/` may be published separately in a public GitHub repository. Every other post file is a private build artifact. Keep definitions, reasoning, and the core example in the article; use the public lab for complete runnable code, setup, captured output, or exercises. At the first relevant mention, add a clear “Public GitHub lab” link and state what the lab contains and when the reader needs it. Treat `LAB_REPO` as the repository root; later file links on a `main` branch use `LAB_REPO/blob/main/<path>`, never a relative local path. If the public branch differs, use its real full URL. Never expose the outline, manifest, social files, research ledger, editable image sources, or another private artifact.

Language is English only.

---

## 8. Hard rules

These exist because breaking them produces an article that looks finished and is not.

**Never pad.** If a section has 300 words of substance and a 600-word budget, write 300 and reduce the tier. Restating an earlier section in new words is the most common failure and the gate checks for it.

**Never state an unsourced fact.** Complexity bounds, benchmark numbers, dates, version numbers, standard names, and named results all need a ledger entry. If research did not find it, write around it or say the number is disputed.

**Never reproduce a figure from a paper, textbook, or documentation site.** Every diagram is our own redraw from our own understanding. This is a copyright line, not a style preference.

**Never quote at length.** Paraphrase. If an exact phrase is genuinely load-bearing, keep it under fifteen words and cite it.

**Never ship an unreferenced figure.** If the prose does not point at a figure, the figure is decoration. Delete it or write the sentence.

**Never leave a placeholder unresolved** in a post marked ready to publish. The validator fails on this.

**Never link a private file.** If a runnable lab exists, keep it under `lab/`, publish only that lab to a public GitHub repository, and link the resolved GitHub URL. The article must still explain the mechanism and show the core example. Put the public lab link at the first relevant mention, describe what it contains, and use `LAB_REPO` only as a draft placeholder. A post cannot pass `--publish` while `LAB_REPO` or a local relative link remains.

**Never use a technical term before introducing it.** At its first meaningful use, give its canonical name (and expand an acronym), say what kind of thing it is, explain the job it does or why it is used here, and state when the reader should use, inspect, or care about it. Add a concrete example or distinguish a nearby concept when confusion is likely. Build a term map in the outline with `term | first section | what | why | when`, then fold those explanations into `blog.md`; never send the reader to the term map.

---

## 9. Quality gate

Phase 6 runs two things.

1. `${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py posts/<slug>/` — mechanical checks: frontmatter fields, tag count, no body H1, Insights position, heading order, figure references, local/unpublished links, public image URLs at publish time, placeholder resolution, and word count against tier.
2. `assets/checklist.md` — judgment checks the script cannot make: is the worked example actually concrete, is each technical term correctly introduced where it first matters, does every equation have a plain sentence after it, and does any section restate another.

Report failures plainly and fix them. Do not mark a post ready with a failing gate.

---

## 10. Expanding an existing post

The user will want to deepen posts over time. Do not rewrite.

Read the existing `blog.md` and `outline.md`, pick the named section, deepen only that section, then re-run the gate and update the tier in frontmatter. `references/depth-tiers.md` has the protocol.
