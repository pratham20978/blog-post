# blog-forge

Authoring pipeline for long-form computer-science education posts written as a single Markdown file.

## Install

```bash
git clone <this-repo> ~/.claude/plugins/blog-forge
```

Also install [`diagram-design`](https://github.com/cathrynlavery/diagram-design), which blog-visuals calls for rendering.

## Use

```
/blog:new consistent hashing
/blog:research B-tree splits
/blog:visuals posts/consistent-hashing
/blog:expand posts/consistent-hashing "The math"
/blog:publish posts/consistent-hashing
```

## Skills

| Skill | Owns |
|---|---|
| `blog-authoring` | structure, depth tiers, drafting, quality gate |
| `blog-research` | source tiers, search protocol, claim ledger |
| `blog-visuals` | figure planning, cover and LinkedIn prompt sequences, handoff |

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
python3 scripts/validate_post.py posts/<slug>/            # gate
python3 scripts/validate_post.py posts/<slug>/ --publish  # gate + no placeholders left
python3 scripts/fill_urls.py posts/<slug>/ urls.txt       # swap placeholders for URLs
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
