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
| `blog-authoring` | structure, depth tiers, drafting, quality gate |
| `blog-research` | source tiers, search protocol, claim ledger |
| `blog-visuals` | figure planning, cover and LinkedIn prompt sequences, handoff |
| `seo-audit` | deterministic local and live technical SEO checks |
| `seo-daily` | dated daily reports and optional backend ingestion |
| `seo-content` | reader-intent briefs and useful on-page improvements |
| `ai-discoverability` | evidence-based AI-search citation observations |

## Pipeline

```
brief → research → CHECKPOINT A → outline → CHECKPOINT B
      → draft → figures → assemble → gate → CHECKPOINT C
```

## Post folder

```
posts/<slug>/
├── blog.md              deliverable, with figure placeholders
├── outline.md           section skeleton and word budget
├── manifest.md          placeholder → file → path → alt text
├── linkedin.md          LinkedIn copy, carousel order, first comment
├── research/ledger.md   claim → source → URL → access date
└── assets/              cover/LinkedIn prompts, .mmd, .html, .svg, .png per figure
```

## Scripts

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" posts/<slug>/
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" posts/<slug>/ --publish
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fill_urls.py" posts/<slug>/ urls.txt
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
