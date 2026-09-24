#!/usr/bin/env python3
"""Mechanical quality gate for a blog-forge post folder.

Usage:
    python3 validate_post.py posts/<slug>/ [--publish]
    python3 validate_post.py posts/<slug>/ --social

Checks structure, metadata, figures, claim keys, and the public-file boundary.
--publish additionally requires that every placeholder has been replaced with
a public image URL.

Exit codes: 0 pass, 1 failures found, 2 could not read the post.
"""

import argparse
import datetime as dt
import pathlib
import re
import struct
import sys
from urllib.parse import urlsplit

TIERS = {
    "L1": (2000, 3000, 3, 5),
    "L2": (3000, 5000, 5, 8),
    "L3": (5000, 7500, 8, 12),
    "L4": (7500, 10000, 12, 18),
}

# Per-tier research floors: (peer-reviewed or standard sources carrying an
# identifier, distinct scholarly databases queried). The full table this pair
# is taken from lives in blog-research/SKILL.md.
RESEARCH_FLOORS = {
    "L1": (2, 2),
    "L2": (4, 3),
    "L3": (7, 4),
    "L4": (10, 4),
}

REQUIRED_FIELDS = [
    "title", "slug", "date", "summary", "tags", "category",
    "tier", "difficulty", "reading_minutes",
]

REQUIRED_SECTIONS = ["Insights", "Why this matters", "The problem",
                     "Worked example", "Intuition",
                     "Limitations and common mistakes",
                     "Key takeaways", "References"]

CATEGORIES = {
    "algorithms", "data-structures", "networking", "operating-systems",
    "databases", "distributed-systems", "machine-learning",
    "computer-architecture", "compilers", "security", "theory",
    "software-engineering",
}

PLACEHOLDER_RE = re.compile(r"\b(COVER|FIG_\d{2})\b")
# A figure's route is the reasoned choice of how it is drawn, recorded in
# manifest.md and explained in blog-visuals/references/visual-taxonomy.md. Each
# route maps to the source file it must leave behind; an empty tuple means the
# route produces no build source of its own.
FIGURE_ROUTES = {
    "source": (".png", ".svg", ".jpg", ".jpeg", ".webp"),
    "mermaid": (".mmd",),
    "placed": (".html",),
    "chart": (".html",),
    "plot": (".py", ".svg"),
    "capture": (),
    "generated": (),
}
COVER_ROUTES = ("generated", "placed")
RESEARCH_STATUSES = (
    "peer-reviewed", "preprint", "standard", "official-docs", "source",
    "practitioner",
)
MISSING_CELLS = {"", "—", "–", "-", "n/a"}
SEARCH_LOG_HEADING_RE = re.compile(r"^##\s+Search log\s*$", re.M | re.I)
LITERATURE_NOTE_HEADING_RE = re.compile(r"^##\s+Literature note\s*$", re.M | re.I)
SERIES_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SERIES_CONTEXT_HEADINGS = (
    "Series invariants",
    "Part status",
    "Knowledge established",
    "Decisions to preserve",
    "Open threads",
    "Next part brief",
)
CLAIM_KEY_RE = re.compile(r"<!--\s*(L\d{2,3})\s*-->")
IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]*)\)")
MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\((?P<target>[^)\n]+)\)")
REFERENCE_LINK_RE = re.compile(
    r"^\s*\[(?!\^)[^\]]+\]:\s*(?P<target>\S+)", re.MULTILINE
)
HTML_LINK_RE = re.compile(r"\bhref\s*=\s*['\"](?P<target>[^'\"]+)['\"]", re.I)
PRIVATE_DIRECTORY_RE = re.compile(
    r"(?<![\w/-])(?:\.\.?/)*(?P<path>assets?/|research/)",
    re.I,
)
PUBLIC_LAB_DIRECTORY_RE = re.compile(
    r"(?<![\w/-])(?:\.\.?/)*(?P<path>examples?/|lab/)", re.I
)
LAB_PLACEHOLDER_RE = re.compile(r"\bLAB_\d{2}\b")
LAB_DOWNLOAD_HEADING_RE = re.compile(r"^###\s+Lab downloads\s*$", re.M | re.I)
REFERENCES_HEADING_RE = re.compile(r"^##\s+References\s*$", re.M | re.I)
MINIO_DOWNLOAD_HOST = "minio.canery.in"
PRIVATE_FILE_RE = re.compile(
    r"(?<![\w/.-])(?P<path>outline\.md|manifest\.md|linkedin\.md|"
    r"(?:research/)?ledger\.md|cover-prompt\.md|linkedin-prompts\.md|social\.md)\b",
    re.I,
)
FENCE_RE = re.compile(r"^```")
LINKEDIN_FRAME_RE = re.compile(r"^##\s+(\d{2})\s+[—-]\s+.+$", re.M)
SOCIAL_ASSET_HEADING_RE = re.compile(
    r"^###\s+(?P<stem>(?P<kind>feed|story)-(?P<number>\d{2})-[a-z0-9-]+)\s*$",
    re.M,
)
SOCIAL_FIELDS = (
    "File", "Title", "Platforms", "Role", "Dimensions", "Narrative beat",
    "Technical source", "Visual structure", "Visible-text transcript",
    "Alt text", "Long description", "Keywords", "Canonical URL",
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def render(self):
        for m in self.errors:
            print(f"  FAIL  {m}")
        for m in self.warnings:
            print(f"  warn  {m}")
        print()
        print(f"{len(self.errors)} failures, {len(self.warnings)} warnings")
        return 1 if self.errors else 0


def split_frontmatter(text):
    """Return (frontmatter_dict, body). Values stay as raw strings."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end]
    body = text[end + 4:]
    fm = {}
    for line in raw.splitlines():
        line = line.rstrip()
        if not line or line.lstrip().startswith("#") or ":" not in line:
            continue
        if line[0] in " \t-":          # nested value, not a top-level key
            continue
        key, _, value = line.partition(":")
        fm[key.strip()] = value.strip().strip('"').strip("'")
    return fm, body


def parse_list(value):
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    return [v.strip().strip('"').strip("'") for v in value.split(",") if v.strip()]


def table_cells(line):
    """Split one Markdown table row into stripped, unfenced cells."""
    return [cell.strip().strip("`").strip() for cell in line.strip().strip("|").split("|")]


def markdown_table(text, *headers):
    """Return (header cells, body rows) for the first table holding every header.

    Header names match case-insensitively. The separator row is dropped and the
    body stops at the first line that is no longer part of the table.
    """
    if not text:
        return [], []
    wanted = [header.casefold() for header in headers]
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        header = table_cells(line)
        folded = [cell.casefold() for cell in header]
        if any(want not in folded for want in wanted):
            continue
        rows = []
        for following in lines[index + 1:]:
            if not following.strip().startswith("|"):
                break
            cells = table_cells(following)
            if all(re.fullmatch(r":?-+:?", cell or "-") for cell in cells):
                continue
            rows.append(cells)
        return header, rows
    return [], []


def column_index(header, *names):
    """Return the position of the first header cell matching one of `names`."""
    folded = [cell.casefold() for cell in header]
    for name in names:
        if name.casefold() in folded:
            return folded.index(name.casefold())
    return None


def cell_at(cells, index):
    """Return one cell by position, or an empty string when the row is short."""
    if index is None or index >= len(cells):
        return ""
    return cells[index]


def is_missing(value):
    """Return whether a cell is empty or an explicit em-dash placeholder."""
    return value.strip().casefold() in MISSING_CELLS


def find_repo_root(root):
    """Walk up from a post folder to the directory that holds posts/."""
    resolved = root.resolve()
    for candidate in (resolved, *resolved.parents):
        if (candidate / "posts").is_dir():
            return candidate
    return None


def strip_code(body):
    """Remove fenced code blocks so they don't pollute word counts or checks."""
    out, inside = [], False
    for line in body.splitlines():
        if FENCE_RE.match(line.strip()):
            inside = not inside
            continue
        if not inside:
            out.append(line)
    return "\n".join(out)


def markdown_destination(raw):
    """Extract a Markdown destination while discarding an optional title."""
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1:raw.index(">")].strip()
    return raw.split(maxsplit=1)[0] if raw else ""


def is_public_link(target):
    """Return whether a link resolves without an unpublished local file."""
    if not target:
        return False
    if target.startswith(("#", "/", "?")):
        return True
    try:
        parsed = urlsplit(target)
    except ValueError:
        return False
    if parsed.scheme in {"http", "https"}:
        return bool(parsed.netloc)
    if parsed.scheme == "mailto":
        return bool(parsed.path)
    return False


def is_public_image(target):
    """Return whether an image target is an absolute public HTTP(S) URL."""
    try:
        parsed = urlsplit(target)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def is_lab_placeholder(target):
    return bool(LAB_PLACEHOLDER_RE.fullmatch(target))


def is_public_minio_download(target):
    """Return whether a lab target is a public Canery MinIO object URL."""
    if is_lab_placeholder(target):
        return True
    try:
        parsed = urlsplit(target)
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and parsed.netloc.casefold() == MINIO_DOWNLOAD_HOST
        and parsed.path.startswith("/media/")
    )


def check_public_boundary(body, rep):
    """Reject links and prose references to build-only post artifacts."""
    stripped = re.sub(r"<!--.*?-->", " ", strip_code(body), flags=re.S)

    targets = []
    for pattern in (MARKDOWN_LINK_RE, REFERENCE_LINK_RE, HTML_LINK_RE):
        targets.extend(
            markdown_destination(match.group("target"))
            for match in pattern.finditer(stripped)
        )
    has_public_lab = any(is_public_minio_download(target) for target in targets)
    for target in dict.fromkeys(targets):
        if not is_public_link(target) and not is_lab_placeholder(target):
            rep.error(
                f"public boundary: local link '{target}' will not exist after publish"
            )

    # Include fenced code here: a command such as `python examples/demo.py`
    # still depends on an unpublished file even though it is not a Markdown link.
    prose = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    prose = re.sub(r"https?://[^\s)>]+", " ", prose)
    prose = MARKDOWN_LINK_RE.sub(" ", prose)
    prose = REFERENCE_LINK_RE.sub(" ", prose)
    prose = HTML_LINK_RE.sub(" ", prose)
    private_paths = []
    for pattern in (PRIVATE_DIRECTORY_RE, PRIVATE_FILE_RE):
        private_paths.extend(match.group("path") for match in pattern.finditer(prose))
    for path in dict.fromkeys(private_paths):
        rep.error(
            f"public boundary: blog.md refers to unpublished artifact '{path}'"
        )

    public_lab_paths = [
        match.group("path") for match in PUBLIC_LAB_DIRECTORY_RE.finditer(prose)
    ]
    if public_lab_paths and not has_public_lab:
        rep.error(
            "public boundary: lab/example paths require MinIO lab downloads "
            "in the References section"
        )


def manifest_lab_rows(manifest_text):
    """Return LAB_XX rows as (placeholder, local path) in manifest order."""
    rows = []
    if manifest_text is None:
        return rows
    for line in manifest_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) >= 2 and LAB_PLACEHOLDER_RE.fullmatch(cells[0]):
            rows.append((cells[0], cells[1]))
    return rows


def publishable_lab_files(root):
    """List source artifacts intended for upload, excluding generated caches."""
    lab_root = root / "lab"
    if not lab_root.exists():
        legacy = root / "examples"
        lab_root = legacy if legacy.exists() else lab_root
    if not lab_root.exists():
        return []
    files = []
    for path in sorted(lab_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        if "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if any(part.startswith(".") for part in relative.parts):
            continue
        files.append(relative.as_posix())
    return files


def check_lab_downloads(body, manifest_text, root, rep):
    """Validate optional lab structure and its end-of-article MinIO links."""
    visible_body = re.sub(r"<!--.*?-->", " ", body, flags=re.S)
    local_files = publishable_lab_files(root)
    placeholders = sorted(set(LAB_PLACEHOLDER_RE.findall(visible_body)))
    heading = LAB_DOWNLOAD_HEADING_RE.search(visible_body)
    rows = manifest_lab_rows(manifest_text)

    if not (local_files or placeholders or heading or rows):
        return
    if heading is None:
        rep.error("public lab: missing '### Lab downloads' under References")
        return

    references = REFERENCES_HEADING_RE.search(visible_body)
    if references is None or heading.start() < references.end():
        rep.error("public lab: 'Lab downloads' must be inside the final References section")

    next_heading = re.search(r"^#{2,3}\s+", visible_body[heading.end():], re.M)
    end = heading.end() + next_heading.start() if next_heading else len(visible_body)
    section = visible_body[heading.end():end]
    targets = [
        markdown_destination(match.group("target"))
        for match in MARKDOWN_LINK_RE.finditer(section)
    ]
    if not targets:
        rep.error("public lab: 'Lab downloads' has no downloadable files")
    for target in targets:
        if not is_public_minio_download(target):
            rep.error(
                f"public lab: download '{target}' must be LAB_XX in draft or a "
                f"public https://{MINIO_DOWNLOAD_HOST}/media/ URL"
            )

    section_placeholders = set(
        target for target in targets if is_lab_placeholder(target)
    )
    outside = set(placeholders) - section_placeholders
    if outside:
        rep.error(
            "public lab: placeholders must appear only under 'Lab downloads': "
            + ", ".join(sorted(outside))
        )

    row_names = [placeholder for placeholder, _ in rows]
    expected_names = [f"LAB_{number:02d}" for number in range(1, len(rows) + 1)]
    if row_names and row_names != expected_names:
        rep.error("public lab: manifest placeholders must be contiguous from LAB_01")
    if placeholders and manifest_text is None:
        rep.error("public lab: placeholders are used but manifest.md is missing")
    elif set(placeholders) - set(row_names):
        missing = sorted(set(placeholders) - set(row_names))
        rep.error("public lab: placeholders missing from manifest.md: " + ", ".join(missing))

    if rows and len(targets) != len(rows):
        rep.error(
            f"public lab: References has {len(targets)} downloads but manifest.md "
            f"lists {len(rows)} lab files"
        )

    manifest_paths = [path for _, path in rows]
    if len(manifest_paths) != len(set(manifest_paths)):
        rep.error("public lab: manifest lists a lab file more than once")
    for path_text in manifest_paths:
        path = pathlib.Path(path_text)
        candidate = (root / path).resolve()
        try:
            candidate.relative_to(root.resolve())
        except ValueError:
            rep.error(f"public lab: manifest path escapes the post folder: {path_text}")
            continue
        if not candidate.is_file():
            rep.error(f"public lab: manifest file does not exist: {path_text}")

    if set(local_files) != set(manifest_paths):
        missing = sorted(set(local_files) - set(manifest_paths))
        extra = sorted(set(manifest_paths) - set(local_files))
        if missing:
            rep.error("public lab: local files missing from manifest.md: " + ", ".join(missing))
        if extra:
            rep.error("public lab: manifest paths outside the lab: " + ", ".join(extra))

    if len(local_files) > 1 and not any(
        pathlib.Path(path).name.casefold() == "readme.md" for path in local_files
    ):
        rep.error("public lab: a multi-file lab requires README.md")


def word_count(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\|", " ", text)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text))


def check_frontmatter(fm, root, rep):
    for field in REQUIRED_FIELDS:
        if not fm.get(field):
            rep.error(f"frontmatter: missing or empty '{field}'")

    title = fm.get("title", "")
    if title and len(title) > 60:
        rep.warn(f"frontmatter: title is {len(title)} chars, target is under 60")

    summary = fm.get("summary", "")
    if summary and not (120 <= len(summary) <= 200):
        rep.warn(f"frontmatter: summary is {len(summary)} chars, target is 150-160")

    tags = parse_list(fm.get("tags", ""))
    if not 4 <= len(tags) <= 7:
        rep.error(f"frontmatter: {len(tags)} tags, need 4 to 7")
    for tag in tags:
        if tag != tag.lower() or " " in tag:
            rep.error(f"frontmatter: tag '{tag}' must be lowercase and hyphenated")
    if len(set(tags)) != len(tags):
        rep.error("frontmatter: duplicate tags")

    category = fm.get("category", "")
    if category and category not in CATEGORIES:
        rep.warn(f"frontmatter: category '{category}' is not in the standard list")
    if tags and category and tags[0] != category:
        rep.warn(f"frontmatter: first tag '{tags[0]}' should be the category '{category}'")

    tier = fm.get("tier", "")
    if tier not in TIERS:
        rep.error(f"frontmatter: tier '{tier}' must be one of {', '.join(TIERS)}")

    for field in ("date", "updated"):
        value = fm.get(field)
        if value:
            try:
                dt.date.fromisoformat(value)
            except ValueError:
                rep.error(f"frontmatter: '{field}' is not an ISO date: {value}")

    check_series(fm, root, rep)
    return tier, fm.get("slug", "")


def check_series(fm, root, rep):
    """A series member lives below its shared plan and compact context."""
    series = fm.get("series", "").strip()
    position = fm.get("series_position", "").strip()
    if not series and not position:
        return

    if not position:
        rep.error("frontmatter: 'series' is set without 'series_position'")
    if not series:
        rep.error("frontmatter: 'series_position' is set without 'series'")
    if series and not SERIES_SLUG_RE.fullmatch(series):
        rep.error(f"frontmatter: series '{series}' must be lowercase and hyphenated")
    if position and not (position.isdigit() and int(position) >= 1):
        rep.error(
            f"frontmatter: series_position '{position}' must be a positive integer"
        )

    if not series or not SERIES_SLUG_RE.fullmatch(series):
        return
    repo = find_repo_root(root)
    series_path = f"posts/{series}"
    plan = f"{series_path}/plan.md"
    context = f"{series_path}/context.md"
    if repo is None:
        rep.warn(f"series: cannot locate the repository root for {root}")
        return

    series_dir = repo / "posts" / series
    if root.resolve().parent != series_dir.resolve():
        rep.warn(
            f"series: member should live at {series_path}/<post-slug>/, not {root}"
        )
    if not (repo / plan).is_file():
        rep.warn(f"series: no plan at {plan}; the plan sets each part's tier and scope")
    context_path = repo / context
    if not context_path.is_file():
        rep.warn(
            f"series: no context at {context}; it carries completed knowledge and the "
            "next-part brief"
        )
        return

    context_text = context_path.read_text(encoding="utf-8")
    for heading in SERIES_CONTEXT_HEADINGS:
        if not re.search(rf"^##\s+{re.escape(heading)}\s*$", context_text, re.M):
            rep.warn(f"series: context.md is missing '## {heading}'")
    context_words = word_count(context_text)
    if context_words > 2000:
        rep.warn(
            f"series: context.md is {context_words} words; consolidate it below 2000"
        )


def check_structure(body, rep):
    lines = body.splitlines()
    h1 = [line for line in lines if line.startswith("# ")]
    if h1:
        rep.error(
            f"structure: found {len(h1)} body H1 headings; the page shell owns the H1"
        )

    headings = [(len(m.group(1)), m.group(2).strip())
                for line in lines
                if (m := re.match(r"^(#{1,6})\s+(.*)$", line))]

    prev = 0
    for level, text in headings:
        if prev and level > prev + 1:
            rep.error(f"structure: heading level jumps from H{prev} to H{level} at '{text}'")
        prev = level

    names = [t for _, t in headings]
    for section in REQUIRED_SECTIONS:
        if section == "Insights":
            continue
        if not any(section.lower() in n.lower() for n in names):
            rep.error(f"structure: missing section '{section}'")

    if "**Insights**" not in body and "## Insights" not in body:
        rep.error("structure: no Insights block found")
    else:
        idx = body.find("Insights")
        prose = word_count(body[:idx])
        if prose > 60:
            rep.error(f"structure: Insights appears after {prose} words, must be near the top")

    return headings


def check_figures(body, manifest_text, tier, rep):
    stripped = strip_code(body)
    images = list(IMAGE_RE.finditer(stripped))
    if not images:
        rep.error("figures: no images found")

    placeholders = []
    for m in images:
        alt = m.group("alt").strip()
        target = m.group("target").strip()
        if not alt:
            rep.error(f"figures: image with empty alt text -> {target}")
        elif len(alt) < 20:
            rep.warn(f"figures: alt text is short ({len(alt)} chars): '{alt}'")
        if PLACEHOLDER_RE.fullmatch(target):
            placeholders.append(target)

    figs = [p for p in placeholders if p.startswith("FIG_")]
    resolved = [m.group("target") for m in images
                if m.group("target").startswith("http")]
    total_figs = len(figs) + max(0, len(resolved) - (1 if "COVER" not in placeholders else 0))

    if tier in TIERS:
        _, _, lo, hi = TIERS[tier]
        if total_figs and not lo <= total_figs <= hi:
            rep.warn(f"figures: {total_figs} figures, {tier} expects {lo} to {hi}")

    # every figure must be referenced in prose
    for n in range(1, total_figs + 1):
        if not re.search(rf"Figure {n}\b", stripped):
            rep.warn(f"figures: Figure {n} has no caption or prose reference")

    if manifest_text is not None:
        for p in placeholders:
            if p not in manifest_text:
                rep.error(f"figures: placeholder {p} is not listed in manifest.md")
    elif placeholders:
        rep.error("figures: placeholders are used but manifest.md is missing")

    return placeholders


def check_routes(manifest_text, root, rep):
    """Every figure must record the route that was reasoned for it."""
    if manifest_text is None:
        return
    header, rows = markdown_table(manifest_text, "Placeholder")
    if not header:
        return

    route_at = column_index(header, "Route")
    if route_at is None:
        rep.warn(
            "figures: manifest.md records no figure routes, so the route gate in "
            "blog-visuals/references/visual-taxonomy.md was never run"
        )
        return

    why_at = column_index(header, "Why")
    if why_at is None:
        rep.error("figures: manifest.md records routes but has no 'Why' column")
    credit_at = column_index(header, "Source credit", "Credit")
    rights_at = column_index(header, "Rights", "License", "Licence")
    file_at = column_index(header, "Local file", "File")
    assets = root / "assets"

    for cells in rows:
        placeholder = cell_at(cells, 0)
        if not PLACEHOLDER_RE.fullmatch(placeholder):
            continue

        route = cell_at(cells, route_at).casefold()
        if not route:
            rep.error(f"figures: {placeholder} records no route in manifest.md")
            continue
        if route not in FIGURE_ROUTES:
            rep.error(
                f"figures: {placeholder} has unknown route '{route}', use one of "
                + ", ".join(FIGURE_ROUTES)
            )
            continue
        if why_at is not None and is_missing(cell_at(cells, why_at)):
            rep.error(
                f"figures: {placeholder} is routed '{route}' with no reason under 'Why'"
            )
        if route == "source":
            if credit_at is None or is_missing(cell_at(cells, credit_at)):
                rep.error(
                    f"figures: {placeholder} is routed 'source' without paper, original "
                    "figure number, and public source under 'Source credit'"
                )
            if rights_at is None or is_missing(cell_at(cells, rights_at)):
                rep.error(
                    f"figures: {placeholder} is routed 'source' without a verified "
                    "licence or permission under 'Rights'"
                )
        if placeholder == "COVER" and route not in COVER_ROUTES:
            rep.warn(
                f"figures: COVER is routed '{route}', a cover is normally "
                + " or ".join(COVER_ROUTES)
            )

        suffixes = FIGURE_ROUTES[route]
        if not suffixes or not assets.is_dir():
            continue
        stem = pathlib.Path(cell_at(cells, file_at)).stem
        if not stem:
            continue
        if not any((assets / f"{stem}{suffix}").is_file() for suffix in suffixes):
            rep.error(
                f"figures: {placeholder} is routed '{route}' but assets/{stem} has no "
                + " or ".join(suffixes) + " source file"
            )


def check_claims(body, ledger_text, rep):
    keys = set(CLAIM_KEY_RE.findall(body))
    if ledger_text is None:
        if keys:
            rep.error("claims: claim keys used but research/ledger.md is missing")
        else:
            rep.error("claims: research/ledger.md is missing")
        return
    for key in sorted(keys):
        if not re.search(rf"\|\s*{key}\s*\|", ledger_text):
            rep.error(f"claims: key {key} is not in the ledger")
    ledger_keys = set(re.findall(r"\|\s*(L\d{2,3})\s*\|", ledger_text))
    unused = ledger_keys - keys
    if unused:
        rep.warn(f"claims: ledger rows never used: {', '.join(sorted(unused))}")
    if not keys:
        rep.warn("claims: no claim keys in the draft; sourced facts should carry one")


def check_research(ledger_text, tier, rep):
    """Confirm the literature sweep ran and cleared the tier's scholarly floor."""
    if ledger_text is None:
        return

    if SEARCH_LOG_HEADING_RE.search(ledger_text) is None:
        rep.warn(
            "research: the ledger has no search log, so the literature sweep in "
            "blog-research/SKILL.md cannot be confirmed to have run"
        )
        return

    header, sources = markdown_table(ledger_text, "ID", "Tier", "Source")
    status_at = column_index(header, "Status")
    if status_at is None:
        rep.warn(
            "research: the ledger's Sources table has no Status column, so the "
            "scholarly sweep in blog-research/SKILL.md cannot be counted"
        )
        return
    identifier_at = column_index(header, "Identifier")
    if identifier_at is None:
        rep.error("research: the Sources table records a Status but no Identifier")
        return

    log_header, log_rows = markdown_table(ledger_text, "Database", "Query")
    database_at = column_index(log_header, "Database")
    seen = {}
    for cells in log_rows:
        name = cell_at(cells, database_at)
        if not is_missing(name):
            seen.setdefault(name.casefold(), name)
    databases = list(seen.values())

    papers = 0
    for cells in sources:
        source_id = cell_at(cells, 0)
        if not source_id:
            continue
        status = cell_at(cells, status_at).casefold()
        identifier = cell_at(cells, identifier_at)
        if status not in RESEARCH_STATUSES:
            rep.error(
                f"research: source {source_id} has status '{status}', use one of "
                + ", ".join(RESEARCH_STATUSES)
            )
            continue
        if status == "peer-reviewed" and is_missing(identifier):
            rep.error(
                f"research: peer-reviewed source {source_id} carries no identifier, "
                "record its DOI, arXiv id or equivalent"
            )
        if status in {"peer-reviewed", "standard"} and not is_missing(identifier):
            papers += 1

    if tier not in RESEARCH_FLOORS:
        return
    paper_floor, database_floor = RESEARCH_FLOORS[tier]
    if len(databases) < database_floor:
        rep.error(
            f"research: {len(databases)} scholarly databases queried, {tier} needs "
            f"{database_floor}; the search log names "
            + (", ".join(databases) if databases else "none")
        )
    if papers < paper_floor:
        message = (
            f"research: {papers} peer-reviewed or standard sources carry an "
            f"identifier, {tier} needs {paper_floor}"
        )
        if LITERATURE_NOTE_HEADING_RE.search(ledger_text):
            rep.warn(
                message + "; the ledger's literature note downgraded this to a warning"
            )
        else:
            rep.error(message)


def check_math(body, rep):
    if re.search(r"\\\(|\\\[", body):
        rep.error("math: \\( or \\[ delimiters found, use $ or $$")
    if "\\eqref" in body or "\\label" in body:
        rep.error("math: \\label and \\eqref do not render, number equations by hand")

    stripped = strip_code(body)
    for m in re.finditer(r"\$\$(.+?)\$\$", stripped, flags=re.S):
        after = stripped[m.end():m.end() + 400].strip()
        first = after.split("\n\n")[0].strip()
        if not first or first.startswith(("#", "$$", "|")):
            rep.warn("math: a display equation is not followed by a plain-language sentence")


def check_length(body, tier, rep):
    words = word_count(strip_code(body))
    if tier in TIERS:
        lo, hi, _, _ = TIERS[tier]
        if words < lo:
            rep.warn(
                f"length: {words} words, {tier} starts at {lo}. "
                "Drop a tier rather than padding."
            )
        elif words > hi:
            rep.warn(f"length: {words} words, {tier} tops out at {hi}. Consider splitting.")
    print(f"  info  {words} words")


def check_publish(body, rep):
    stripped = re.sub(r"<!--.*?-->", " ", strip_code(body), flags=re.S)
    leftover = sorted(set(PLACEHOLDER_RE.findall(stripped)))
    if leftover:
        rep.error(f"publish: unresolved placeholders: {', '.join(leftover)}")
    lab_leftover = sorted(set(LAB_PLACEHOLDER_RE.findall(stripped)))
    if lab_leftover:
        rep.error(f"publish: unresolved lab downloads: {', '.join(lab_leftover)}")
    for image in IMAGE_RE.finditer(stripped):
        target = markdown_destination(image.group("target"))
        if not PLACEHOLDER_RE.fullmatch(target) and not is_public_image(target):
            rep.error(
                f"publish: image '{target}' must be an absolute public http(s) URL"
            )


def resolved_http_url(url):
    try:
        parsed = urlsplit(url)
        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
            and not re.search(r"[\s<>{}]", url)
        )
    except ValueError:
        return False


def check_linkedin_prompts(prompts_text, rep):
    """Validate the unchanged alternative image-prompt contract."""
    if prompts_text is None:
        rep.error("linkedin: assets/linkedin-prompts.md is missing")
        return []

    matches = list(LINKEDIN_FRAME_RE.finditer(prompts_text))
    if not 4 <= len(matches) <= 10:
        rep.error(f"linkedin: {len(matches)} image prompts found, need 4 to 10")

    numbers = [int(match.group(1)) for match in matches]
    if numbers != list(range(1, len(matches) + 1)):
        rep.error("linkedin: prompt numbers must be contiguous from 01")

    filenames = []
    beats = []
    alts = []
    prompt_bodies = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(prompts_text)
        block = prompts_text[match.end():end]
        number = match.group(1)

        beat = re.search(r"^- Narrative beat:\s*(.+)$", block, re.M)
        filename = re.search(r"^- File:\s*`?([^`\n]+)`?\s*$", block, re.M)
        alt = re.search(r"^- Alt text:\s*(.+)$", block, re.M)
        prompt = re.search(r"^### Prompt\s*\n+```text\s*\n(.+?)\n```", block, re.M | re.S)

        if not beat or not beat.group(1).strip():
            rep.error(f"linkedin: frame {number} has no narrative beat")
        else:
            beats.append(beat.group(1).strip().casefold())
        if not filename:
            rep.error(f"linkedin: frame {number} has no filename")
        else:
            resolved = filename.group(1).strip()
            if not re.fullmatch(rf"linkedin-{number}-[a-z0-9-]+\.png", resolved):
                rep.error(f"linkedin: frame {number} filename is not numbered consistently")
            filenames.append(resolved)
        if not alt or not alt.group(1).strip():
            rep.error(f"linkedin: frame {number} has no alt text")
        elif not 80 <= len(alt.group(1).strip()) <= 140:
            rep.warn(f"linkedin: frame {number} alt text should be 80 to 140 characters")
            alts.append(alt.group(1).strip().casefold())
        else:
            alts.append(alt.group(1).strip().casefold())
        if not prompt or len(prompt.group(1).split()) < 40:
            rep.error(f"linkedin: frame {number} needs a complete self-contained prompt")
        else:
            prompt_body = prompt.group(1).strip()
            prompt_bodies.append(prompt_body)
            required_prompt_parts = (
                "SCENE AND INTENDED USE",
                "SUBJECT",
                "KEY DETAILS",
                "CONSTRAINTS",
                "4:5 portrait frame",
                "Maintain the same visual world",
            )
            missing = [part for part in required_prompt_parts if part not in prompt_body]
            if missing:
                rep.error(
                    f"linkedin: frame {number} prompt is missing: {', '.join(missing)}"
                )

    if len(filenames) != len(set(filenames)):
        rep.error("linkedin: prompt filenames must be unique")
    if len(beats) != len(set(beats)):
        rep.error("linkedin: narrative beats must not be duplicates")
    if len(alts) != len(set(alts)):
        rep.error("linkedin: alt text must not be duplicated")
    if len(prompt_bodies) != len(set(prompt_bodies)):
        rep.error("linkedin: image prompts must not be duplicates")
    return filenames


def check_linkedin_copy(canonical, filenames, linkedin_text, rep):
    if linkedin_text is None:
        rep.error("linkedin: linkedin.md is missing")
        return

    for heading in ("LinkedIn post", "Carousel order", "Accessibility checklist",
                    "First comment"):
        if not re.search(rf"^#+\s+{re.escape(heading)}\s*$", linkedin_text, re.M | re.I):
            rep.error(f"linkedin: linkedin.md is missing '{heading}'")

    comment = re.search(r"^##\s+First comment\s*$([\s\S]*)", linkedin_text, re.M | re.I)
    comment_text = comment.group(1) if comment else ""
    if canonical and canonical not in comment_text:
        rep.error("linkedin: first comment does not contain canonical_url")
    if "Read the full article on Canery:" not in comment_text:
        rep.error("linkedin: first comment is missing the Canery article CTA")
    takeaway = comment_text.partition("Read the full article on Canery:")[0].strip()
    if len(takeaway.split()) < 4:
        rep.error("linkedin: first comment needs a takeaway or short quote before the CTA")

    before_comment = linkedin_text[:comment.start()] if comment else linkedin_text
    if canonical and canonical in before_comment:
        rep.error("linkedin: canonical_url belongs in the first comment, not the main post")
    for filename in filenames:
        if filename not in linkedin_text:
            rep.error(f"linkedin: carousel order is missing {filename}")


def check_linkedin(fm, prompts_text, linkedin_text, rep):
    """Legacy LinkedIn-only contract retained for existing post folders."""
    canonical = fm.get("canonical_url", "").strip()
    if not resolved_http_url(canonical):
        rep.error("linkedin: frontmatter canonical_url must be a resolved http(s) URL")
    filenames = check_linkedin_prompts(prompts_text, rep)
    check_linkedin_copy(canonical, filenames, linkedin_text, rep)


def social_section(text, heading, level=2):
    start = re.search(rf"^{'#' * level}\s+{re.escape(heading)}\s*$", text, re.M | re.I)
    if start is None:
        return None
    following = text[start.end():]
    next_heading = re.search(rf"^#{{1,{level}}}\s+", following, re.M)
    end = start.end() + next_heading.start() if next_heading else len(text)
    return text[start.end():end].strip()


def social_order(text, heading, level, kind):
    section = social_section(text, heading, level)
    if section is None:
        return None
    pattern = re.compile(
        rf"^\d+\.\s+`assets/social/(?P<stem>{kind}-\d{{2}}-[a-z0-9-]+)\.png`\s+—\s+.+$",
        re.M,
    )
    return [match.group("stem") for match in pattern.finditer(section)]


def parse_social_assets(text):
    metadata = social_section(text, "Asset metadata", 2)
    if metadata is None:
        return []
    matches = list(SOCIAL_ASSET_HEADING_RE.finditer(metadata))
    assets = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(metadata)
        block = metadata[match.end():end]
        fields = {}
        for field in SOCIAL_FIELDS:
            value = re.search(rf"^- {re.escape(field)}:\s*(.+)$", block, re.M)
            if value:
                fields[field] = value.group(1).strip().strip("`")
        assets.append(
            {
                "stem": match.group("stem"),
                "kind": match.group("kind"),
                "number": int(match.group("number")),
                "fields": fields,
            }
        )
    return assets


def social_png_dimensions(path):
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError:
        return None
    if len(header) != 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", header[16:24])


def social_logo_marker(text, kind):
    """The lockup must sit at the template's locked position, at a locked width.

    Two widths are accepted per kind. The first is the shipped template's, which
    render_social.py enforces on anything rendered now; the second is the width
    the posts written before that renderer existed carry. Accepting both keeps
    those posts green without letting a new card place the lockup freely.
    """
    marker = re.search(r"<g\b[^>]*data-canery-logo=['\"]lockup['\"][^>]*>", text)
    if marker is None:
        return False
    position, widths = (
        ({"data-logo-x": "72", "data-logo-y": "72"}, ("220", "180"))
        if kind == "feed"
        else ({"data-logo-x": "72", "data-logo-y": "250"}, ("245", "200"))
    )
    for name, value in position.items():
        if not re.search(rf"\b{re.escape(name)}=['\"]{re.escape(value)}['\"]", marker.group(0)):
            return False
    return any(
        re.search(rf"\bdata-logo-width=['\"]{re.escape(width)}['\"]", marker.group(0))
        for width in widths
    )


def check_social(fm, root, social_text, prompts_text, rep):
    """Validate the finished cross-platform social package."""
    canonical = fm.get("canonical_url", "").strip()
    if not resolved_http_url(canonical):
        rep.error("social: frontmatter canonical_url must be a resolved http(s) URL")

    if social_text is None:
        rep.error("social: social.md is missing")
        return

    social_fm, social_body = split_frontmatter(social_text)
    if social_fm.get("social_schema") != "2":
        rep.error("social: social.md frontmatter must set social_schema: 2")
    if social_fm.get("canonical_url", "").strip() != canonical:
        rep.error("social: social.md canonical_url must match blog.md")

    for heading in (
        "LinkedIn post", "LinkedIn first comment", "Instagram caption",
        "Shared feed order", "Instagram Story", "Asset metadata",
    ):
        section = social_section(social_body, heading, 2)
        if section is None:
            rep.error(f"social: social.md is missing '{heading}'")
        elif heading in {"LinkedIn post", "Instagram caption"} and len(section.split()) < 8:
            rep.error(f"social: '{heading}' needs platform-ready copy")

    comment = social_section(social_body, "LinkedIn first comment", 2) or ""
    if canonical and canonical not in comment:
        rep.error("social: LinkedIn first comment must contain canonical_url")
    if "Read the full article on Canery:" not in comment:
        rep.error("social: LinkedIn first comment is missing the Canery article CTA")

    story = social_section(social_body, "Instagram Story", 2) or ""
    if not re.search(r"^- CTA:\s*\S.+$", story, re.M):
        rep.error("social: Instagram Story needs CTA copy")
    if not re.search(r"^- Link sticker label:\s*\S.+$", story, re.M):
        rep.error("social: Instagram Story needs a link sticker label")
    sticker = re.search(r"^- Link sticker URL:\s*(\S+)\s*$", story, re.M)
    if not sticker or sticker.group(1) != canonical:
        rep.error("social: Instagram Story link sticker URL must match canonical_url")

    feed_order = social_order(social_body, "Shared feed order", 2, "feed")
    story_order = social_order(social_body, "Story order", 3, "story")
    if feed_order is None:
        feed_order = []
    if story_order is None:
        story_order = []
        rep.error("social: social.md is missing 'Story order'")
    story_order_section = social_section(social_body, "Story order", 3) or ""
    overlay_lines = re.findall(
        r"^\d+\.\s+`assets/social/story-\d{2}-[a-z0-9-]+\.png`\s+—\s+Overlay:\s+\S.+$",
        story_order_section,
        re.M,
    )
    if len(overlay_lines) != len(story_order):
        rep.error("social: every Story order entry needs explicit overlay copy")

    if not 5 <= len(feed_order) <= 8:
        rep.error(f"social: shared feed has {len(feed_order)} cards, need 5 to 8")
    if not 3 <= len(story_order) <= 5:
        rep.error(f"social: Story has {len(story_order)} frames, need 3 to 5")
    for kind, order in (("feed", feed_order), ("story", story_order)):
        numbers = [int(stem.split("-")[1]) for stem in order]
        if numbers != list(range(1, len(order) + 1)):
            rep.error(f"social: {kind} order must be contiguous from 01")
        if len(order) != len(set(order)):
            rep.error(f"social: {kind} order contains duplicate filenames")

    assets = parse_social_assets(social_body)
    if not assets:
        rep.error("social: Asset metadata has no feed or Story entries")
    stems = [asset["stem"] for asset in assets]
    if len(stems) != len(set(stems)):
        rep.error("social: Asset metadata contains duplicate entries")

    by_kind = {
        kind: [asset for asset in assets if asset["kind"] == kind]
        for kind in ("feed", "story")
    }
    for kind, order in (("feed", feed_order), ("story", story_order)):
        metadata_order = [asset["stem"] for asset in by_kind[kind]]
        if metadata_order != order:
            rep.error(f"social: {kind} order and Asset metadata must match exactly")

    alts = []
    longs = []
    beats = []
    social_dir = root / "assets" / "social"
    for kind, group in by_kind.items():
        expected_dimensions = (1080, 1350) if kind == "feed" else (1080, 1920)
        expected_text = "1080×1350" if kind == "feed" else "1080×1920"
        expected_platforms = "Instagram feed, LinkedIn" if kind == "feed" else "Instagram Story"
        numbers = [asset["number"] for asset in group]
        if numbers != list(range(1, len(group) + 1)):
            rep.error(f"social: {kind} metadata numbers must be contiguous from 01")
        for index, asset in enumerate(group):
            stem = asset["stem"]
            fields = asset["fields"]
            missing = [field for field in SOCIAL_FIELDS if not fields.get(field)]
            if missing:
                rep.error(f"social: {stem} is missing metadata: {', '.join(missing)}")
                continue

            expected_file = f"assets/social/{stem}.png"
            if fields["File"] != expected_file:
                rep.error(f"social: {stem} File must be {expected_file}")
            if fields["Platforms"] != expected_platforms:
                rep.error(f"social: {stem} Platforms must be '{expected_platforms}'")
            if fields["Dimensions"] != expected_text:
                rep.error(f"social: {stem} Dimensions must be {expected_text}")
            if fields["Canonical URL"] != canonical:
                rep.error(f"social: {stem} Canonical URL must match blog.md")

            expected_role = "cover" if index == 0 else ("cta" if index == len(group) - 1 else "technical")
            if fields["Role"].casefold() != expected_role:
                rep.error(f"social: {stem} Role must be {expected_role}")
            if expected_role == "technical" and len(fields["Technical source"].split()) < 2:
                rep.error(f"social: {stem} needs an article-specific Technical source")

            alt = fields["Alt text"]
            if not 80 <= len(alt) <= 160:
                rep.warn(f"social: {stem} alt text should be 80 to 160 characters")
            alts.append(alt.casefold())
            longs.append(fields["Long description"].casefold())
            beats.append(fields["Narrative beat"].casefold())

            for suffix in (".html", ".svg", ".png"):
                path = social_dir / f"{stem}{suffix}"
                if not path.is_file():
                    rep.error(f"social: {stem} is missing {path.name}")
            html = social_dir / f"{stem}.html"
            svg = social_dir / f"{stem}.svg"
            for source in (html, svg):
                if source.is_file() and not social_logo_marker(source.read_text(encoding="utf-8"), kind):
                    rep.error(f"social: {source.name} lacks the locked Canery logo marker")
            png = social_dir / f"{stem}.png"
            if png.is_file() and social_png_dimensions(png) != expected_dimensions:
                got = social_png_dimensions(png)
                label = "invalid PNG" if got is None else f"{got[0]}×{got[1]}"
                rep.error(f"social: {png.name} is {label}, expected {expected_text}")

    for label, values in (
        ("alt text", alts),
        ("long descriptions", longs),
        ("narrative beats", beats),
    ):
        if len(values) != len(set(values)):
            rep.error(f"social: {label} must be unique")

    if social_dir.is_dir():
        source_stems = {
            path.stem for path in social_dir.glob("*.html")
            if re.fullmatch(r"(?:feed|story)-\d{2}-[a-z0-9-]+", path.stem)
        }
        unlisted = sorted(source_stems - set(stems))
        if unlisted:
            rep.error("social: HTML assets missing from metadata: " + ", ".join(unlisted))

    check_linkedin_prompts(prompts_text, rep)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post_dir")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--publish", action="store_true",
                      help="also require every placeholder to be a real URL")
    mode.add_argument("--social", action="store_true",
                      help="validate only the finished social package and prompt pack")
    args = ap.parse_args()

    root = pathlib.Path(args.post_dir)
    post = root / "blog.md"
    if not post.exists():
        print(f"Cannot read {post}", file=sys.stderr)
        return 2

    text = post.read_text(encoding="utf-8")
    fm, body = split_frontmatter(text)

    manifest = root / "manifest.md"
    ledger = root / "research" / "ledger.md"
    manifest_text = manifest.read_text(encoding="utf-8") if manifest.exists() else None
    ledger_text = ledger.read_text(encoding="utf-8") if ledger.exists() else None
    linkedin_prompts = root / "assets" / "linkedin-prompts.md"
    linkedin = root / "linkedin.md"
    social = root / "social.md"
    linkedin_prompts_text = (
        linkedin_prompts.read_text(encoding="utf-8") if linkedin_prompts.exists() else None
    )
    linkedin_text = linkedin.read_text(encoding="utf-8") if linkedin.exists() else None
    social_text = social.read_text(encoding="utf-8") if social.exists() else None

    rep = Report()
    print(f"Validating {root}\n")

    if args.social:
        check_social(fm, root, social_text, linkedin_prompts_text, rep)
        print()
        code = rep.render()
        print("PASS" if code == 0 else "FAIL")
        return code

    tier, _ = check_frontmatter(fm, root, rep)
    check_structure(body, rep)
    check_figures(body, manifest_text, tier, rep)
    check_routes(manifest_text, root, rep)
    check_claims(body, ledger_text, rep)
    check_research(ledger_text, tier, rep)
    check_math(body, rep)
    check_public_boundary(body, rep)
    check_lab_downloads(body, manifest_text, root, rep)
    check_length(body, tier, rep)
    if social_text is not None:
        check_social(fm, root, social_text, linkedin_prompts_text, rep)
    if args.publish:
        check_publish(body, rep)
        if social_text is None:
            check_linkedin(fm, linkedin_prompts_text, linkedin_text, rep)

    print()
    code = rep.render()
    print("PASS" if code == 0 else "FAIL")
    return code


if __name__ == "__main__":
    sys.exit(main())
