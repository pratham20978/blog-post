---
name: seo-daily
description: Run and triage Canery's daily SEO health check. Use when the user asks for a daily SEO routine, recurring audit, SEO report, monitoring pass, or scheduled discoverability check.
license: MIT
metadata:
  version: "0.2"
---

# Daily SEO

From the repository root run:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/canery-seo" daily --config seo.config.json
```

This writes dated Markdown and JSON reports under `reports/seo/`. Summarize new errors first, then warnings, then stable passes. Do not make content changes unless the user explicitly asks for fixes.

For recurring execution, use the host's scheduler or a Claude Desktop scheduled routine. A Claude Code `/loop` is session-scoped and is not durable automation.

If backend history is configured, pass the full private admin endpoint through `--submit-url`; read the bearer token only from `BLOG_ADMIN_ACCESS_TOKEN`. Never print either secret.
