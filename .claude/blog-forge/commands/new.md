---
description: Start a new blog post from a topic
---

Start a new post using the **blog-authoring** skill.

Topic: $ARGUMENTS

Run the pipeline from phase 0. Fix the brief first (subject area, audience), then run the scope decision from `references/series-planning.md`. If the topic is a series, stop at Checkpoint S with the plan instead of starting a single post.

For a new series, create `posts/<series-slug>/plan.md` and the sibling
`context.md`; member posts live at `posts/<series-slug>/<post-slug>/`. When the
request names an approved series part, read both shared files before research
or outlining and update `context.md` only after the completed part passes its
gate.

If it is one post, propose the tier and the difficulty with their reasons and the adjacent option, then research and stop at Checkpoint A. Do not draft prose before the outline is approved at Checkpoint B.
