# Finished social assets

Use this workflow only after the article, its figures, claim ledger, and
canonical URL are final. The social package promotes the article; it must not
introduce a technical claim, number, command, or recommendation that the
article and ledger do not support.

The existing `references/linkedin-handoff.md` still owns the alternative image
prompt pack. Do not change that prompt style in this phase.

## Deliverables

**Every social frame is a rendered image, and no social frame is ever a mermaid-cli output.**
The figure route gate in `references/visual-taxonomy.md` governs article
figures only; it does not apply here. These files are uploaded to Instagram and LinkedIn as
images on a fixed branded canvas, so they come from the locked templates below — Mermaid may lay
out a diagram upstream, but what ships is the restyled card.

Create `assets/social/` with editable and rendered triplets:

```text
feed-01-<beat>.html  feed-01-<beat>.svg  feed-01-<beat>.png
story-01-<beat>.html story-01-<beat>.svg story-01-<beat>.png
```

- Shared Instagram/LinkedIn feed: 5–8 contiguous 4:5 cards, 1080×1350.
- Instagram Story: 3–5 contiguous 9:16 frames, 1080×1920.
- Start from the locked templates in `assets/social-feed-template.html` and
  `assets/social-story-template.html`.
- Render and check them with:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_social.py" posts/<slug>/assets/social/
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_social.py" posts/<slug>/assets/social/ --check
```

The first feed card is a purpose-built social cover. The first Story frame is a
9:16 recomposition, not a stretched feed card. The final card/frame is the CTA.
Every social frame carries the full Canery lockup at the locked top-left safe
position. The 1200×630 blog cover remains unbranded.

## Content standard

Every technical card has four parts: a short headline, one setup sentence, one
article-specific technical artefact, and one takeaway. The artefact must be a
real value, equation, command, code fragment, architecture, trace, or sourced
comparison. Prefer the article's own worked example and figures. Do not replace
available technical evidence with generic metaphor art.

Keep one teaching beat per frame. A card may simplify layout, but it must retain
the qualifiers that make the claim accurate. Do not invent benchmark values or
turn observed execution into a vendor-support claim.

## Publishing sheet

Write `social.md` beside `blog.md` using this exact structure. Keep metadata
values on one line so the mechanical gate can validate them.

````markdown
---
social_schema: 2
canonical_url: "<resolved canonical URL>"
---

# Social publishing package — <slug>

## LinkedIn post

<platform-ready post copy>

## LinkedIn first comment

<takeaway>

Read the full article on Canery: <canonical URL>

## Instagram caption

<platform-ready caption and CTA>

## Shared feed order

1. `assets/social/feed-01-<beat>.png` — <narrative beat>
...

## Instagram Story

- CTA: <platform-ready call to action>
- Link sticker label: Read the article
- Link sticker URL: <canonical URL>

### Story order

1. `assets/social/story-01-<beat>.png` — Overlay: <platform overlay copy>
...

## Asset metadata

### feed-01-<beat>

- File: `assets/social/feed-01-<beat>.png`
- Title: <human-readable image title>
- Platforms: Instagram feed, LinkedIn
- Role: cover
- Dimensions: 1080×1350
- Narrative beat: <what the frame teaches>
- Technical source: <article heading, figure, ledger claim, or exact combination>
- Visual structure: <reading order and spatial organization>
- Visible-text transcript: <all meaningful text in reading order>
- Alt text: <concise description of purpose and essential technical content>
- Long description: <complete technical description, values, relationships, and takeaway>
- Keywords: <short, accurate comma-separated technical entities>
- Canonical URL: <canonical URL>

### story-01-<beat>

- File: `assets/social/story-01-<beat>.png`
- Title: <human-readable image title>
- Platforms: Instagram Story
- Role: cover
- Dimensions: 1080×1920
<same remaining fields>
````

Use `cover`, `technical`, or `cta` for Role. The first frame is `cover`, the
last is `cta`, and intermediate frames are `technical`. Alt text is a concise
description, not a keyword container. Put the extra detail and exact visible
wording in Long description and Visible-text transcript.

Social assets are private publishing handoff files. Do not add them to the blog
image manifest, upload them to MinIO, or reference them from `blog.md`.
