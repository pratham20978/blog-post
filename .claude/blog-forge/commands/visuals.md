---
description: Plan or build figures for a post
---

Use the **blog-visuals** skill for: $ARGUMENTS

If the post has no figure plan yet, produce one. For each figure record the
section, the one thing it must communicate, a draft caption, and the **route**
decided by the gate in `references/visual-taxonomy.md` together with the one-line
reason it was decided that way. Route every figure before drawing any of them.

Before drawing a paper-backed figure, inspect the original paper's figures.
Use the `source` route when one rights-cleared figure directly explains the
section; extract it unchanged and record its paper, original figure number,
source URL, and rights. Select only relevant figures, never every paper image.
If reuse rights are unclear, do not generate or redraw a lookalike.

A figure you can only hand-place by dropping nodes, dropping edge labels, or
splitting it in two is a `mermaid` figure. Do not simplify an architecture to fit
a hand-placed canvas.

If the plan exists, build the figures on their recorded routes: exact extraction
for `source`, Mermaid source
rendered by `mermaid-cli` for `mermaid`, diagram-design for `placed` and `chart`,
matplotlib or hand SVG for `plot`. Export SVG and PNG either way and keep the
editable source. Write `manifest.md` with the route and reason columns filled in,
then run `lint_visuals.py` and read every rendered PNG before calling it done.

Once the article is final, read `references/social-assets.md`; build the shared
Instagram/LinkedIn feed deck and the separate Instagram Story sequence as HTML,
SVG, and PNG, then write `social.md`. Social frames are always rendered images
and never Mermaid output — the route gate does not apply to them. Run
`render_social.py` and its `--check` mode. Also keep producing
`assets/linkedin-prompts.md` from the unchanged `references/linkedin-handoff.md`
prompt contract. Do not upload or post assets.
