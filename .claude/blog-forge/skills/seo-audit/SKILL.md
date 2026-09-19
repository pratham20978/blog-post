---
name: seo-audit
description: Audit Canery articles and web routes for technical and on-page SEO problems. Use when the user asks to check SEO, indexing prerequisites, canonicals, titles, descriptions, headings, image alt text, robots.txt, sitemap.xml, structured data, or why a blog may not be discoverable.
license: MIT
metadata:
  version: "0.2"
---

# SEO Audit

Run the deterministic local audit first:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/canery-seo" audit --config seo.config.json
```

Add `--live` only when the user wants the deployed site checked. Read the report, verify each affected file before suggesting changes, and separate errors from recommendations.

Never promise a rank. The tool checks indexability and content prerequisites, not search-engine outcomes. Never edit or publish during an audit-only request.

For the meaning and remediation of a rule, read `references/technical-seo.md`.
