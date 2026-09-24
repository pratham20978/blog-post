---
description: Run the quality gate and prepare handoff
---

Prepare a post for publish: $ARGUMENTS

1. `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" <post-folder>/`
2. Work through `blog-authoring/assets/checklist.md`
3. Fix every failure, report every warning with a recommendation
   - Three of the gate's warnings are legacy signals, deliberately not failures:
     no figure routes in `manifest.md`, no `## Search log` in the ledger, and a
     missing `posts/<series-slug>/plan.md` or `context.md`. On a **new** post treat any of them as a
     failure — it means the route gate, the literature sweep, or the scope
     decision did not run. On a post predating those rules, say so and move on.
4. Confirm `manifest.md`, `assets/cover-prompt.md`, and
   `assets/linkedin-prompts.md` exist. New posts require `social.md` plus checked
   `assets/social/` triplets; legacy posts may retain `linkedin.md` instead.
5. Run `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" <post-folder>/ --social`
   for a new social package.
6. If `lab/` exists, confirm every publishable file has one `LAB_XX` row in
   `manifest.md` and one link under `### Lab downloads` in the final References
   section. Upload those files individually to the public MinIO `media` bucket.
7. For a series member, analyse the final artifacts and update the shared
   `posts/<series-slug>/context.md`: completed knowledge, decisions to preserve,
   open threads, part status, and the next-part brief. Keep it under 2,000 words
   and never copy article prose, the outline, ledger, or source list into it.

After the user uploads images and optional lab files to MinIO and provides
`urls.txt` with one URL for each still-unresolved placeholder in manifest order:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/fill_urls.py" <post-folder>/ urls.txt
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate_post.py" <post-folder>/ --publish
```

Do not mark a post ready with a failing gate.
