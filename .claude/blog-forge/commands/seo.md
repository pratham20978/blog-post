---
description: Audit local Canery SEO and explain every finding
---

Run the read-only SEO audit from the repository root:

```bash
"${CLAUDE_PLUGIN_ROOT}/bin/canery-seo" audit --config seo.config.json
```

If `$ARGUMENTS` contains `live`, add `--live`. Inspect the file behind every finding and report errors before warnings. Do not edit or publish unless the user separately asks for fixes, and do not promise a ranking.
