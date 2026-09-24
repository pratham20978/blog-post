# blog-forge

Local authoring, technical SEO, daily monitoring, and AI-search discoverability tools for Canery.

## Install

The repository declares `canery-local` in `.claude/settings.json`, so Claude Code
and the Claude VS Code extension load the same plugin after the workspace is
trusted and restarted. To test without installing it:

```bash
claude --plugin-dir ./.claude/blog-forge
```

No GitHub checkout is required. `blog-visuals` optionally uses an installed
`diagram-design` skill for rendering.

## Use

```
/blog-forge:series diffusion models
/blog-forge:new consistent hashing
/blog-forge:research B-tree splits
/blog-forge:visuals posts/consistent-hashing
/blog-forge:expand posts/consistent-hashing "The math"
/blog-forge:publish posts/consistent-hashing
/blog-forge:seo
/blog-forge:seo-daily
```

## Skills

| Skill | Owns |
|---|---|
| `blog-authoring` | scope and level, series plans, structure, depth tiers, drafting, quality gate |
| `blog-research` | literature sweep, source tiers, search protocol, claim ledger |
| `blog-visuals` | figure route gate, figures, cover, finished Instagram/LinkedIn assets, prompts, handoff |
| `seo-audit` | deterministic local and live technical SEO checks |
| `seo-daily` | dated daily reports and optional backend ingestion |
| `seo-content` | reader-intent briefs and useful on-page improvements |
| `ai-discoverability` | evidence-based AI-search citation observations |

## Pipeline

```
brief + scope → CHECKPOINT S → research → CHECKPOINT A → outline → CHECKPOINT B
              → draft → figures → assemble → gate → CHECKPOINT C
```

Checkpoint S fires only when the topic is more than one post. The scope decision
answers how many posts a topic is and at what level each one sits, and writes
`posts/<series-slug>/plan.md` plus a compact living `context.md` before any
research runs. Member posts live under that series folder; the context is read
before each part and updated after each completed part.

## Post folder

```
posts/<slug>/
├── blog.md              deliverable, with figure placeholders
├── outline.md           section skeleton and word budget
├── manifest.md          placeholder → file → route → why → path → alt text
├── social.md            LinkedIn/Instagram copy, asset order, alt text, metadata
├── research/ledger.md   claim → source → URL → access date
└── assets/              cover/prompts, figures, and editable/rendered social cards
```

Series use a nested form:

```text
posts/<series-slug>/
├── plan.md
├── context.md
└── <post-slug>/          the normal post folder shown above
```

## Scripts

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" <post-folder>/
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" <post-folder>/ --social
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" <post-folder>/ --publish
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/lint_visuals.py" <post-folder>/assets/
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/render_social.py" <post-folder>/assets/social/
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fill_urls.py" <post-folder>/ urls.txt
"${CLAUDE_PLUGIN_ROOT}/bin/canery-seo" audit --config seo.config.json
"${CLAUDE_PLUGIN_ROOT}/bin/canery-seo" daily --config seo.config.json
```

Images are uploaded manually. Nothing here touches object storage.

## Tiers

| Tier | Words | Figures |
|---|---|---|
| L1 | 2,000–3,000 | 3–5 |
| L2 | 3,000–5,000 | 5–8 |
| L3 | 5,000–7,500 | 8–12 |
| L4 | 7,500–10,000 | 12–18 |

L1 and L2 are the daily default. Word count is an output of the section budget, never a target.

Tier and difficulty are separate axes. Tier is how much ground a post covers;
difficulty is who can read it. A short L1 post can be advanced, and a long L4
post can be beginner-friendly. Every brief states both.
