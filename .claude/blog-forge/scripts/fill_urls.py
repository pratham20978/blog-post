#!/usr/bin/env python3
"""Replace image and public-lab placeholders in blog.md with public URLs.

Usage:
    python3 fill_urls.py posts/<slug>/ urls.txt [--dry-run]

Reads unresolved placeholders in manifest.md order, pairs them with the URLs
in urls.txt line by line, and rewrites blog.md in place. Refuses to write on
any mismatch, because a half-filled post looks fine and ships broken links.

Exit codes: 0 written, 1 refused, 2 could not read inputs.
"""

import argparse
import pathlib
import re
import shutil
import sys

PLACEHOLDER_RE = re.compile(r"\b(COVER|FIG_\d{2}|LAB_REPO)\b")


def read_manifest_order(text):
    """Placeholders in table order, first column of each row."""
    order = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells:
            continue
        m = PLACEHOLDER_RE.fullmatch(cells[0])
        if m and cells[0] not in order:
            order.append(cells[0])
    return order


def read_urls(text):
    urls = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def unresolved_manifest_order(manifest_text, body):
    """Return manifest placeholders that still occur in blog.md."""
    manifest_order = read_manifest_order(manifest_text)
    present = set(PLACEHOLDER_RE.findall(body))
    return [placeholder for placeholder in manifest_order if placeholder in present]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post_dir")
    ap.add_argument("urls_file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = pathlib.Path(args.post_dir)
    post = root / "blog.md"
    manifest = root / "manifest.md"
    urls_path = pathlib.Path(args.urls_file)

    for path in (post, manifest, urls_path):
        if not path.exists():
            print(f"Cannot read {path}", file=sys.stderr)
            return 2

    body = post.read_text(encoding="utf-8")
    manifest_text = manifest.read_text(encoding="utf-8")
    manifest_order = read_manifest_order(manifest_text)
    present = set(PLACEHOLDER_RE.findall(body))
    unlisted = sorted(present - set(manifest_order))
    if unlisted:
        print("Refusing to write, blog.md has placeholders missing from manifest.md:",
              file=sys.stderr)
        for placeholder in unlisted:
            print(f"  {placeholder}", file=sys.stderr)
        return 1
    order = unresolved_manifest_order(manifest_text, body)
    urls = read_urls(urls_path.read_text(encoding="utf-8"))

    if not order:
        print("No unresolved placeholders found in blog.md", file=sys.stderr)
        return 1

    if len(order) != len(urls):
        print(f"Refusing to write: manifest lists {len(order)} placeholders "
              f"but urls.txt has {len(urls)} URLs.", file=sys.stderr)
        print("\nManifest order:", file=sys.stderr)
        for i, p in enumerate(order, 1):
            got = urls[i - 1] if i <= len(urls) else "(missing)"
            print(f"  {i:>2}. {p:<8} -> {got}", file=sys.stderr)
        return 1

    bad = [u for u in urls if not u.startswith(("http://", "https://"))]
    if bad:
        print("Refusing to write, these are not URLs:", file=sys.stderr)
        for u in bad:
            print(f"  {u}", file=sys.stderr)
        return 1

    mapping = dict(zip(order, urls))
    used = {}
    for placeholder, url in mapping.items():
        pattern = re.compile(rf"\b{re.escape(placeholder)}\b")
        body, n = pattern.subn(url, body)
        used[placeholder] = n

    missing = [p for p, n in used.items() if n == 0]
    if missing:
        print("Refusing to write, these placeholders are in the manifest but "
              "not in blog.md:", file=sys.stderr)
        for p in missing:
            print(f"  {p}", file=sys.stderr)
        return 1

    leftover = sorted(set(PLACEHOLDER_RE.findall(body)))
    if leftover:
        print("Refusing to write, blog.md still contains placeholders that the "
              "manifest does not list:", file=sys.stderr)
        for p in leftover:
            print(f"  {p}", file=sys.stderr)
        return 1

    for placeholder, n in used.items():
        print(f"  {placeholder:<8} -> {mapping[placeholder]}  ({n} occurrence{'s' if n != 1 else ''})")

    if args.dry_run:
        print("\nDry run, nothing written.")
        return 0

    shutil.copy2(post, post.with_suffix(".md.bak"))
    post.write_text(body, encoding="utf-8")
    print(f"\nWrote {post}  (backup at {post.with_suffix('.md.bak')})")
    validator = pathlib.Path(__file__).resolve().with_name("validate_post.py")
    print("Next:", sys.executable, validator, root, "--publish")
    return 0


if __name__ == "__main__":
    sys.exit(main())
