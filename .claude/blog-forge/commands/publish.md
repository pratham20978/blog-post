---
description: Run the quality gate and prepare handoff
---

Prepare a post for publish: $ARGUMENTS

1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" posts/<slug>/`
2. Work through `blog-authoring/assets/checklist.md`
3. Fix every failure, report every warning with a recommendation
4. Confirm `manifest.md`, `assets/cover-prompt.md`,
   `assets/linkedin-prompts.md`, and `linkedin.md` exist
5. If `lab/` exists, confirm only that lab has been published to a public
   GitHub repository, `LAB_REPO` is in `manifest.md`, and the article introduces
   the lab at its first relevant mention

After the user uploads images, publishes the optional lab, and provides
`urls.txt` with one URL for each still-unresolved placeholder in manifest order:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fill_urls.py" posts/<slug>/ urls.txt
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" posts/<slug>/ --publish
```

Do not mark a post ready with a failing gate.
