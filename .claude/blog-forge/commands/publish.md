---
description: Run the quality gate and prepare handoff
---

Prepare a post for publish: $ARGUMENTS

1. `python3 scripts/validate_post.py posts/<slug>/`
2. Work through `blog-authoring/assets/checklist.md`
3. Fix every failure, report every warning with a recommendation
4. Confirm `manifest.md`, `assets/cover-prompt.md`,
   `assets/linkedin-prompts.md`, and `linkedin.md` exist

After the user uploads and provides `urls.txt`:

```bash
python3 scripts/fill_urls.py posts/<slug>/ urls.txt
python3 scripts/validate_post.py posts/<slug>/ --publish
```

Do not mark a post ready with a failing gate.
