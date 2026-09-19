#!/usr/bin/env python3
"""Mechanical quality gate for a blog-forge post folder.

Usage:
    python3 validate_post.py posts/<slug>/ [--publish]

Checks structure, metadata, figures, claim keys, and the public-file boundary.
--publish additionally requires that every placeholder has been replaced with
a public image URL.

Exit codes: 0 pass, 1 failures found, 2 could not read the post.
"""

import argparse
import datetime as dt
import pathlib
import re
import sys
from urllib.parse import urlsplit

TIERS = {
    "L1": (2000, 3000, 3, 5),
    "L2": (3000, 5000, 5, 8),
    "L3": (5000, 7500, 8, 12),
    "L4": (7500, 10000, 12, 18),
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
LAB_REPO_RE = re.compile(r"\bLAB_REPO\b")
PRIVATE_FILE_RE = re.compile(
    r"(?<![\w/.-])(?P<path>outline\.md|manifest\.md|linkedin\.md|"
    r"(?:research/)?ledger\.md|cover-prompt\.md|linkedin-prompts\.md)\b",
    re.I,
)
FENCE_RE = re.compile(r"^```")
LINKEDIN_FRAME_RE = re.compile(r"^##\s+(\d{2})\s+[—-]\s+.+$", re.M)


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


def is_public_github_link(target):
    """Return whether a link points to a public GitHub host."""
    if target == "LAB_REPO" or target.startswith(("LAB_REPO/", "LAB_REPO#")):
        return True
    try:
        parsed = urlsplit(target)
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and parsed.netloc.casefold() in {
            "github.com", "www.github.com", "raw.githubusercontent.com"
        }
    )


def check_public_boundary(body, rep):
    """Reject links and prose references to build-only post artifacts."""
    stripped = strip_code(body)

    targets = []
    for pattern in (MARKDOWN_LINK_RE, REFERENCE_LINK_RE, HTML_LINK_RE):
        targets.extend(
            markdown_destination(match.group("target"))
            for match in pattern.finditer(stripped)
        )
    has_public_lab = any(is_public_github_link(target) for target in targets)
    for target in dict.fromkeys(targets):
        if not is_public_link(target) and not is_public_github_link(target):
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
            "public boundary: lab/example paths require a public GitHub lab link "
            "at their first relevant mention"
        )


def word_count(text):
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\|", " ", text)
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text))


def check_frontmatter(fm, rep):
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
    return tier, fm.get("slug", "")


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
        if LAB_REPO_RE.search(body) and "LAB_REPO" not in manifest_text:
            rep.error("public lab: LAB_REPO is not listed in manifest.md")
    elif placeholders:
        rep.error("figures: placeholders are used but manifest.md is missing")
    elif LAB_REPO_RE.search(body):
        rep.error("public lab: LAB_REPO is used but manifest.md is missing")

    return placeholders


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
    stripped = strip_code(body)
    leftover = sorted(set(PLACEHOLDER_RE.findall(stripped)))
    if leftover:
        rep.error(f"publish: unresolved placeholders: {', '.join(leftover)}")
    if LAB_REPO_RE.search(stripped):
        rep.error("publish: unresolved public lab placeholder: LAB_REPO")
    for image in IMAGE_RE.finditer(stripped):
        target = markdown_destination(image.group("target"))
        if not PLACEHOLDER_RE.fullmatch(target) and not is_public_image(target):
            rep.error(
                f"publish: image '{target}' must be an absolute public http(s) URL"
            )


def check_linkedin(fm, prompts_text, linkedin_text, rep):
    canonical = fm.get("canonical_url", "").strip()
    try:
        parsed_canonical = urlsplit(canonical)
        canonical_resolved = (
            parsed_canonical.scheme in {"http", "https"}
            and bool(parsed_canonical.netloc)
            and not re.search(r"[\s<>{}]", canonical)
        )
    except ValueError:
        canonical_resolved = False
    if not canonical_resolved:
        rep.error("linkedin: frontmatter canonical_url must be a resolved http(s) URL")

    if prompts_text is None:
        rep.error("linkedin: assets/linkedin-prompts.md is missing")
        return
    if linkedin_text is None:
        rep.error("linkedin: linkedin.md is missing")
        return

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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("post_dir")
    ap.add_argument("--publish", action="store_true",
                    help="also require every placeholder to be a real URL")
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
    linkedin_prompts_text = (
        linkedin_prompts.read_text(encoding="utf-8") if linkedin_prompts.exists() else None
    )
    linkedin_text = linkedin.read_text(encoding="utf-8") if linkedin.exists() else None

    rep = Report()
    print(f"Validating {root}\n")

    tier, _ = check_frontmatter(fm, rep)
    check_structure(body, rep)
    check_figures(body, manifest_text, tier, rep)
    check_claims(body, ledger_text, rep)
    check_math(body, rep)
    check_public_boundary(body, rep)
    check_length(body, tier, rep)
    if args.publish:
        check_publish(body, rep)
        check_linkedin(fm, linkedin_prompts_text, linkedin_text, rep)

    print()
    code = rep.render()
    print("PASS" if code == 0 else "FAIL")
    return code


if __name__ == "__main__":
    sys.exit(main())
