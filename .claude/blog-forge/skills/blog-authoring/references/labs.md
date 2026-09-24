# Runnable labs

Load this only when a post needs downloadable code, commands, data, or captured output.

## Choose one file or several

Prefer one file when it can run by itself and remain readable. Split only when files have genuinely different responsibilities or tools require the split.

Use multiple files for combinations such as:

- `README.md` — prerequisites, safe environment, run order, expected result, cleanup
- `run.py`, `run.sh`, or equivalent — the single obvious entry point
- `schema.sql` or `setup.sql` — disposable database setup
- `requirements.txt`, `pyproject.toml`, or package manifest — dependencies
- a small input fixture — only when the experiment needs it
- `expected-output.txt`, `.json`, or `.md` — stable captured output worth comparing

A multi-file lab requires `README.md`. Keep the directory shallow unless the language or build tool requires nesting.

## Quality rules

- Make the lab reproduce one teaching outcome from the article. Do not turn it into a second product.
- Use deterministic inputs or document unavoidable variation.
- Give one obvious run path and include cleanup when the lab creates resources.
- Default to a disposable/local environment. Never target production services or destructive operations by default.
- Keep credentials out. Do not include `.env`, tokens, keys, cookies, database dumps with private data, or machine-specific absolute paths.
- Exclude caches, virtual environments, compiled objects, build directories, dependency vendor trees, logs, and unrelated files.
- Add comments for non-obvious decisions, not line-by-line narration.
- Syntax-check every source file. Run the safe path when the required runtime is available; otherwise state exactly what could not be executed.

## Publication contract

Every publishable file receives its own manifest row and download link:

```markdown
| Placeholder | File | Suggested object key | Purpose |
|---|---|---|---|
| LAB_01 | `lab/README.md` | `labs/<slug>/README.md` | setup and run order |
| LAB_02 | `lab/run.py` | `labs/<slug>/run.py` | runnable experiment |
```

Use versioned object keys when changing an already published file. Upload to the public MinIO `media` bucket, producing URLs under `https://minio.canery.in/media/`.

Set an accurate `Content-Type`. When the upload workflow supports object metadata, set `Content-Disposition: attachment; filename="<name>"` so clicking the article link downloads the file instead of rendering it in the browser.

Put all download links at the end of `blog.md`, inside the final References section:

```markdown
## References

### Lab downloads

- [`README.md`](LAB_01) — prerequisites, run order, expected output, and cleanup.
- [`run.py`](LAB_02) — runs the experiment described in the Implementation section.

### Sources
```

The body may link to `#lab-downloads`. It must not link to `lab/run.py` or another local path. Keep the explanation and core example in the article; downloads are for execution and reproduction.
