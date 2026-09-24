---
name: blog-authoring
description: Plan a multi-part technical series with persistent compact context, or write a long-form computer-science education blog post with researched sources, figures, and a pre-publish quality gate. Use whenever the user asks to build a series or write, draft, plan, outline, expand, or review a technical blog post, article, tutorial, explainer, or deep dive.
license: MIT
metadata:
  version: "0.6"
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
- **Its explanation is self-contained.** The article and images teach the concept; optional MinIO lab downloads carry runnable files, not missing definitions or reasoning.
- **It introduces terms before relying on them.** The first meaningful use gives the exact name, what the term means here, why it is used, and when it matters.

If a section cannot meet these, the section is cut. Never pad to hit a word count.

---

## 2. Pipeline

Run these in order. Stop at the checkpoints and wait for the user.

| Phase | Does | Output |
|---|---|---|
| 0 Brief and scope | Fix topic, subject area, audience; run the scope decision — one post or a series, and the tier and difficulty of each part | in conversation, plus `posts/<series-slug>/plan.md` and `context.md` when it is a series |
| **CHECKPOINT S** | Only when the topic is a series: user approves the part list and each part's level before anything is researched | |
| 1 Research | Find and tier sources, build the claim ledger | `research/ledger.md` |
| **CHECKPOINT A** | Show source list and what the post can honestly claim | |
| 2 Outline | Section skeleton, word budget, figure plan, term map | `outline.md` |
| **CHECKPOINT B** | User approves before any long prose is written | |
| 3 Draft | Write section by section against the budget | `blog.md` |
| 4 Assets | Build figures, an optional runnable lab, and finished social handoff | `assets/`, optional `lab/`, `manifest.md`, `social.md` |
| 5 Assemble | Frontmatter, figure placeholders, captions | `blog.md` |
| 6 Gate | Run the checklist and the validator; for a series member, analyse the finished part and update the shared `context.md` | pass/fail report plus current series memory |
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

**Proposing the level.** Never open with a bare default. The brief states the level in three lines:

- the proposed **tier**, with a one-line reason — how many distinct things the reader must learn, and whether the smallest honest worked example fits on one screen
- the proposed **difficulty** (`beginner`, `intermediate`, `advanced`), with the prerequisite claim that justifies it
- the **adjacent option** the user can take instead, so overruling costs one word

Tier and difficulty are separate axes. Tier is how much ground the post covers; difficulty is who can read it. A short L1 post can be advanced, and a long L4 post can be beginner-friendly.

When the topic needs more than one post, read `references/series-planning.md` and run the scope decision before writing the brief.

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
| `references/series-planning.md` | at brief time, for any topic that may be more than one post |
| `references/writing-craft.md` | drafting prose |
| `references/labs.md` | the post needs runnable or downloadable lab files |
| `references/math.md` | the post has equations |
| `references/frontmatter.md` | assembling the file |
| `references/subject-playbooks.md` | at brief time, to learn the subject's conventions |
| `assets/post-template.md` | starting a new post |
| `assets/series-context-template.md` | creating the compact memory file for a new series |
| `assets/checklist.md` | phase 6 |

---

## 7. Output contract

One folder per standalone post, slug-named:

```
posts/<slug>/
├── blog.md              the deliverable, with figure placeholders
├── outline.md           section skeleton and budget
├── manifest.md          upload checklist: placeholder → file → alt text
├── social.md            LinkedIn/Instagram copy, order, alt text, and metadata
├── research/ledger.md   claim → source → URL → access date
├── lab/                 optional runnable files uploaded individually to MinIO
└── assets/
    ├── cover-prompt.md
    ├── linkedin-prompts.md
    ├── social/              editable HTML/SVG and rendered PNG social cards
    ├── fig-01-<name>.mmd     Mermaid source, when used
    ├── fig-01-<name>.html    diagram-design source, re-editable
    ├── fig-01-<name>.svg
    └── fig-01-<name>.png
```

A series is one folder under `posts/`. It owns the approved plan, a compact living context, and
one normal post folder per member:

```
posts/<series-slug>/
├── plan.md                    approved shape, objectives, scope, and level of every part
├── context.md                 compact memory of completed work and instructions for the next part
├── <part-1-slug>/             normal post folder with blog.md, outline.md, research/, assets/, ...
└── <part-2-slug>/             normal post folder
```

Each member post carries `series: <series-slug>` and `series_position: <n>` in frontmatter; both
appear together or neither does. Before starting a member, read both `plan.md` and `context.md`.
After the member passes the gate, analyse the completed artifacts and update `context.md` before
starting another part. The plan and context are private build artifacts like the outline — never
link them from a published post.

Images and labs are **not** uploaded by this skill. `blog.md` carries image placeholders like `FIG_03` and one placeholder per lab file: `LAB_01`, `LAB_02`, and so on. The user uploads the listed files to the public MinIO `media` bucket, places the resulting URLs in `urls.txt` in manifest order, and runs `scripts/fill_urls.py` to swap them in.

Only `blog.md`, uploaded images, and the explicitly listed lab objects become public. Every other post file is a private build artifact. Keep definitions, reasoning, expected results, and the core example in the article. Use `lab/` for complete runnable code, setup, small input data, captured output, or exercises. Put every public lab link under `### Lab downloads` inside the final `## References` section, with a one-line purpose for each file. Body text may point readers to `[Lab downloads](#lab-downloads)`, but it must never link a local path. Never expose the outline, manifest, `social.md`, social assets, research ledger, editable image sources, caches, secrets, or another private artifact.

Language is English only.

---

## 8. Hard rules

These exist because breaking them produces an article that looks finished and is not.

**Never pad.** If a section has 300 words of substance and a 600-word budget, write 300 and reduce the tier. Restating an earlier section in new words is the most common failure and the gate checks for it.

**Never state an unsourced fact.** Complexity bounds, benchmark numbers, dates, version numbers, standard names, and named results all need a ledger entry. If research did not find it, write around it or say the number is disputed.

**Prefer the paper's original figure when it is directly relevant and rights-cleared.** Use the
Blog Visuals `source` route, reproduce it unchanged, and record the paper, original figure
number, source URL, and licence or permission. Do not take every image, and do not generate or
redraw a cheaper lookalike. If rights are unclear, omit it; make an original figure only when it
adds our own analysis rather than imitating the source.

**Never quote at length.** Paraphrase. If an exact phrase is genuinely load-bearing, keep it under fifteen words and cite it.

**Never ship an unreferenced figure.** If the prose does not point at a figure, the figure is decoration. Delete it or write the sentence.

**Never leave a placeholder unresolved** in a post marked ready to publish. The validator fails on this.

**Never link a private file.** If a runnable lab exists, keep its source artifacts under `lab/`, include every publishable file in `manifest.md`, and give every file a `LAB_XX` download link in the final References section. Upload only those listed files to MinIO. A post cannot pass `--publish` while a `LAB_XX` placeholder, missing local file, relative link, or non-MinIO lab URL remains.

**Never start a series member from the plan alone.** Read the shared `context.md` first so the new
post preserves established terminology and does not repeat completed work. After the post passes
the gate, update that context from the final artifacts. Keep it compact: no copied prose, outline,
ledger, or source dump, and no planned claim recorded as already established.

**Keep labs minimal and intentional.** Use one file when one file is genuinely runnable and understandable. Split into multiple files only for distinct responsibilities such as schema, runner, dependencies, input, and expected output. A multi-file lab requires `README.md` with prerequisites, run order, expected result, and safety notes. Never include credentials, `.env`, caches, virtual environments, compiled output, or unrelated files. Read `references/labs.md` before creating or reviewing a lab.

**Never use a technical term before introducing it.** At its first meaningful use, give its canonical name (and expand an acronym), say what kind of thing it is, explain the job it does or why it is used here, and state when the reader should use, inspect, or care about it. Add a concrete example or distinguish a nearby concept when confusion is likely. Build a term map in the outline with `term | first section | what | why | when`, then fold those explanations into `blog.md`; never send the reader to the term map.

---

## 9. Quality gate

Phase 6 runs two things.

1. `${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py <post-folder>/` — mechanical checks: frontmatter fields, series plan/context placement, tag count, no body H1, Insights position, heading order, figure references, lab file/manifest/download parity, local links, public MinIO lab URLs, public image URLs at publish time, placeholder resolution, and word count against tier.
2. `assets/checklist.md` — judgment checks the script cannot make: is the worked example actually concrete, is each technical term correctly introduced where it first matters, does every equation have a plain sentence after it, and does any section restate another.

Report failures plainly and fix them. Do not mark a post ready with a failing gate.

---

## 10. Expanding an existing post

The user will want to deepen posts over time. Do not rewrite.

Read the existing `blog.md` and `outline.md`, pick the named section, deepen only that section, then re-run the gate and update the tier in frontmatter. `references/depth-tiers.md` has the protocol.
