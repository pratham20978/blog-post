#!/usr/bin/env python3
"""Read-only SEO audit runner for Canery Markdown posts and web routes.

The audit never edits content and never claims to predict rankings. It emits a
deterministic report that Claude Code, the IDE extension, cron, or a human can
run in exactly the same way.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urljoin

USER_AGENT = "CanerySeoAudit/0.2 (+https://canery.in)"
IMAGE_RE = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<target>[^)]*)\)")
H1_RE = re.compile(r"^#\s+", re.MULTILINE)
LEGACY_ROUTE_RE = re.compile(r"https?://[^\s)\]>]+/p/|(?<!\w)/p/")


@dataclass(frozen=True)
class Finding:
    rule_code: str
    severity: str
    message: str
    page_url: str | None = None
    evidence: dict[str, Any] | None = None

    def wire(self) -> dict[str, Any]:
        result = asdict(self)
        result["evidence"] = self.evidence or {}
        return result


@dataclass(frozen=True)
class Page:
    url: str
    canonical_url: str | None
    page_type: str
    indexable: bool
    content_sha256: str

    def wire(self) -> dict[str, Any]:
        return asdict(self)


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Parse the flat top-level values this audit needs without a YAML dependency."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith(("#", "-")):
            continue
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields, text[end + 4 :]


def _words(text: str) -> int:
    return len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'-]*", text))


def _add(
    findings: list[Finding],
    rule: str,
    severity: str,
    message: str,
    *,
    page_url: str | None = None,
    **evidence: Any,
) -> None:
    findings.append(Finding(rule, severity, message, page_url, evidence))


def audit_post(
    blog_file: pathlib.Path,
    *,
    site_url: str,
    article_path: str,
) -> tuple[Page, list[Finding]]:
    text = blog_file.read_text(encoding="utf-8")
    fields, body = split_frontmatter(text)
    folder_slug = blog_file.parent.name
    slug = fields.get("slug") or folder_slug
    page_url = site_url + article_path.format(slug=slug)
    canonical = fields.get("canonical_url") or None
    findings: list[Finding] = []

    if slug != folder_slug:
        _add(
            findings,
            "SLUG_FOLDER_MISMATCH",
            "error",
            f"Frontmatter slug '{slug}' differs from folder '{folder_slug}'.",
            page_url=page_url,
        )
    if canonical != page_url:
        _add(
            findings,
            "CANONICAL_MISMATCH",
            "error",
            f"Canonical must be {page_url}.",
            page_url=page_url,
            actual=canonical,
            expected=page_url,
        )

    h1_count = len(H1_RE.findall(body))
    if h1_count:
        _add(
            findings,
            "BODY_H1_DUPLICATES_PAGE_TITLE",
            "error",
            "Article body must start at H2 because the page shell owns the H1.",
            page_url=page_url,
            count=h1_count,
        )

    title = fields.get("title", "")
    if not title:
        _add(findings, "TITLE_MISSING", "error", "Title is missing.", page_url=page_url)
    elif len(title) > 60:
        _add(
            findings,
            "TITLE_TOO_LONG",
            "warning",
            "Title is longer than 60 characters and may truncate in results.",
            page_url=page_url,
            characters=len(title),
        )

    summary = fields.get("summary", "")
    if not summary:
        _add(
            findings,
            "META_DESCRIPTION_MISSING",
            "error",
            "Summary/meta description is missing.",
            page_url=page_url,
        )
    elif not 120 <= len(summary) <= 170:
        _add(
            findings,
            "META_DESCRIPTION_LENGTH",
            "warning",
            "Summary should usually be 120–170 characters.",
            page_url=page_url,
            characters=len(summary),
        )

    for image in IMAGE_RE.finditer(body):
        if not image.group("alt").strip():
            _add(
                findings,
                "IMAGE_ALT_MISSING",
                "error",
                "An article image has empty alt text.",
                page_url=page_url,
                target=image.group("target"),
            )

    if LEGACY_ROUTE_RE.search(text):
        _add(
            findings,
            "LEGACY_ARTICLE_ROUTE",
            "error",
            "Replace /p/ article URLs with the canonical /blogs/ route.",
            page_url=page_url,
        )

    insight_at = body.find("Insights")
    if insight_at == -1:
        _add(
            findings,
            "ANSWER_BLOCK_MISSING",
            "warning",
            "The early Insights answer block is missing.",
            page_url=page_url,
        )
    elif _words(body[:insight_at]) > 100:
        _add(
            findings,
            "ANSWER_BLOCK_LATE",
            "warning",
            "Move the direct answer into the first 100 words.",
            page_url=page_url,
        )

    return (
        Page(
            url=page_url,
            canonical_url=canonical,
            page_type="article",
            indexable=True,
            content_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        ),
        findings,
    )


def audit_web(web_dir: pathlib.Path) -> list[Finding]:
    findings: list[Finding] = []
    required = {
        "SITEMAP_ROUTE_MISSING": web_dir / "src" / "app" / "sitemap.ts",
        "ROBOTS_ROUTE_MISSING": web_dir / "src" / "app" / "robots.ts",
    }
    for rule, path in required.items():
        if not path.is_file():
            _add(findings, rule, "error", f"Required route is missing: {path}")

    article_page = web_dir / "src" / "app" / "(reader)" / "blogs" / "[slug]" / "page.tsx"
    if not article_page.is_file():
        _add(findings, "ARTICLE_ROUTE_MISSING", "error", f"Article route is missing: {article_page}")
    else:
        source = article_page.read_text(encoding="utf-8")
        if "JsonLd" not in source and "application/ld+json" not in source:
            _add(
                findings,
                "ARTICLE_STRUCTURED_DATA_MISSING",
                "error",
                "Article route has no JSON-LD structured data.",
            )
    return findings


def _fetch(url: str) -> tuple[int, str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=12) as response:
        return response.status, response.read(2_000_000).decode("utf-8", "replace")


def audit_live(site_url: str) -> list[Finding]:
    findings: list[Finding] = []
    for path, rule, expected in (
        ("/robots.txt", "LIVE_ROBOTS_UNAVAILABLE", "Sitemap:"),
        ("/sitemap.xml", "LIVE_SITEMAP_UNAVAILABLE", "/blogs/"),
    ):
        url = urljoin(site_url + "/", path.lstrip("/"))
        try:
            status, body = _fetch(url)
        except (OSError, urllib.error.URLError, ValueError) as exc:
            _add(
                findings,
                rule,
                "warning",
                f"Could not verify {url}: {type(exc).__name__}.",
                url=url,
            )
            continue
        if status != 200 or expected not in body:
            _add(
                findings,
                rule,
                "error",
                f"{url} did not return the expected SEO content.",
                url=url,
                status=status,
                expected=expected,
            )
    return findings


def audit(config_path: pathlib.Path, *, live: bool) -> dict[str, Any]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    root = config_path.parent
    site_url = str(config["site_url"]).rstrip("/")
    article_path = str(config.get("article_path", "/blogs/{slug}"))
    if "{slug}" not in article_path:
        raise ValueError("article_path must include {slug}")

    posts_dir = root / str(config.get("posts_dir", "posts"))
    pages: list[Page] = []
    findings: list[Finding] = []
    for blog_file in sorted(posts_dir.glob("*/blog.md")):
        page, post_findings = audit_post(
            blog_file, site_url=site_url, article_path=article_path
        )
        pages.append(page)
        findings.extend(post_findings)

    findings.extend(audit_web(root / str(config.get("web_dir", "web"))))
    if live:
        findings.extend(audit_live(site_url))

    counts = {
        severity: sum(item.severity == severity for item in findings)
        for severity in ("error", "warning", "info")
    }
    return {
        "site_url": site_url,
        "brand_name": str(config.get("brand_name", "Canery")),
        "timezone": str(config.get("timezone", "UTC")),
        "kind": "full" if live else "local",
        "pages": [page.wire() for page in pages],
        "findings": [finding.wire() for finding in findings],
        "summary": {"counts": counts, "pages_scanned": len(pages)},
        "config": config,
    }


def markdown_report(result: dict[str, Any], completed: dt.datetime) -> str:
    counts = result["summary"]["counts"]
    lines = [
        "# Canery SEO audit",
        "",
        f"- Completed: {completed.isoformat()}",
        f"- Site: {result['site_url']}",
        f"- Pages scanned: {result['summary']['pages_scanned']}",
        f"- Findings: {counts['error']} errors, {counts['warning']} warnings, {counts['info']} info",
        "",
    ]
    if not result["findings"]:
        lines.extend(["No findings.", ""])
    else:
        lines.extend(["## Findings", ""])
        for item in result["findings"]:
            page = f" — {item['page_url']}" if item["page_url"] else ""
            lines.append(
                f"- **{item['severity'].upper()} · {item['rule_code']}**: "
                f"{item['message']}{page}"
            )
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "This audit checks discoverability prerequisites. It cannot guarantee a ranking or an AI-search citation.",
            "",
        ]
    )
    return "\n".join(lines)


def submit_result(
    result: dict[str, Any],
    *,
    endpoint: str,
    token: str,
    started: dt.datetime,
    completed: dt.datetime,
) -> None:
    payload = {
        "site_url": result["site_url"],
        "brand_name": result["brand_name"],
        "timezone": result["timezone"],
        "kind": result["kind"],
        "trigger": "plugin",
        "started_at": started.isoformat(),
        "completed_at": completed.isoformat(),
        "pages": result["pages"],
        "findings": result["findings"],
        "summary": result["summary"],
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if not 200 <= response.status < 300:
            raise RuntimeError(f"audit submission returned HTTP {response.status}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("audit", "daily"), default="audit")
    parser.add_argument("--config", default="seo.config.json")
    parser.add_argument("--live", action="store_true", help="also check the deployed robots and sitemap")
    parser.add_argument("--output", help="write the Markdown report to this path")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    parser.add_argument("--strict-warnings", action="store_true")
    parser.add_argument("--submit-url", help="full secret-admin audit endpoint")
    parser.add_argument("--token-env", default="BLOG_ADMIN_ACCESS_TOKEN")
    args = parser.parse_args(argv)

    started = dt.datetime.now(dt.timezone.utc)
    config_path = pathlib.Path(args.config).resolve()
    try:
        result = audit(config_path, live=args.live or args.command == "daily")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"SEO audit could not start: {exc}", file=sys.stderr)
        return 2
    completed = dt.datetime.now(dt.timezone.utc)
    report = markdown_report(result, completed)

    output = args.output
    if args.command == "daily" and not output:
        report_dir = config_path.parent / result["config"].get("report_dir", "reports/seo")
        output = str(report_dir / f"{completed.date().isoformat()}.md")
    if output:
        output_path = pathlib.Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding="utf-8")
        output_path.with_suffix(".json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )

    if args.submit_url:
        token = os.environ.get(args.token_env)
        if not token:
            print(f"{args.token_env} is not set; audit was not submitted", file=sys.stderr)
            return 2
        try:
            submit_result(
                result,
                endpoint=args.submit_url,
                token=token,
                started=started,
                completed=completed,
            )
        except (OSError, urllib.error.URLError, RuntimeError) as exc:
            print(f"Audit submission failed: {type(exc).__name__}", file=sys.stderr)
            return 2

    print(json.dumps(result, indent=2) if args.json else report)
    counts = result["summary"]["counts"]
    return int(bool(counts["error"] or (args.strict_warnings and counts["warning"])))


if __name__ == "__main__":
    raise SystemExit(main())
