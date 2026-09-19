"""Tests for the dependency-free SEO audit runner."""

from __future__ import annotations

import json
import io
import pathlib
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from .seo_audit import audit, audit_post, main


class TestSeoAudit(unittest.TestCase):
    def test_post_requires_canonical_route_and_no_body_h1(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            blog = pathlib.Path(directory) / "example" / "blog.md"
            blog.parent.mkdir()
            blog.write_text(
                """---
title: Example
slug: example
summary: A useful summary that is deliberately long enough to describe the article for a search result without wasting the reader's time.
canonical_url: https://canery.in/p/example
---
# Example

**Insights** — The direct answer.
""",
                encoding="utf-8",
            )

            _, findings = audit_post(
                blog,
                site_url="https://canery.in",
                article_path="/blogs/{slug}",
            )

        rules = {finding.rule_code for finding in findings}
        self.assertIn("CANONICAL_MISMATCH", rules)
        self.assertIn("BODY_H1_DUPLICATES_PAGE_TITLE", rules)
        self.assertIn("LEGACY_ARTICLE_ROUTE", rules)

    def test_clean_project_has_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            post = root / "posts" / "example" / "blog.md"
            post.parent.mkdir(parents=True)
            post.write_text(
                """---
title: Example
slug: example
summary: A useful summary that is deliberately long enough to describe the article for a search result without wasting the reader's time.
canonical_url: https://canery.in/blogs/example
---
**Insights** — The direct answer appears immediately and clearly.

## Why this matters
""",
                encoding="utf-8",
            )
            app = root / "web" / "src" / "app"
            article = app / "(reader)" / "blogs" / "[slug]" / "page.tsx"
            article.parent.mkdir(parents=True)
            article.write_text("export const JsonLd = true", encoding="utf-8")
            (app / "sitemap.ts").write_text("export default function sitemap() {}", encoding="utf-8")
            (app / "robots.ts").write_text("export default function robots() {}", encoding="utf-8")
            config = root / "seo.config.json"
            config.write_text(
                json.dumps(
                    {
                        "site_url": "https://canery.in",
                        "posts_dir": "posts",
                        "web_dir": "web",
                        "article_path": "/blogs/{slug}",
                    }
                ),
                encoding="utf-8",
            )

            result = audit(config, live=False)

        self.assertEqual(result["findings"], [])
        self.assertEqual(result["summary"]["pages_scanned"], 1)

    def test_daily_writes_dated_markdown_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            app = root / "web" / "src" / "app"
            article = app / "(reader)" / "blogs" / "[slug]" / "page.tsx"
            article.parent.mkdir(parents=True)
            article.write_text("export const JsonLd = true", encoding="utf-8")
            (app / "sitemap.ts").write_text("export default function sitemap() {}", encoding="utf-8")
            (app / "robots.ts").write_text("export default function robots() {}", encoding="utf-8")
            config = root / "seo.config.json"
            config.write_text(
                json.dumps(
                    {
                        "site_url": "https://canery.in",
                        "posts_dir": "posts",
                        "web_dir": "web",
                        "report_dir": "reports/seo",
                    }
                ),
                encoding="utf-8",
            )

            with patch("scripts.seo_audit.audit_live", return_value=[]):
                with redirect_stdout(io.StringIO()):
                    code = main(["daily", "--config", str(config)])

            reports = list((root / "reports" / "seo").glob("*.md"))
            machine_reports = list((root / "reports" / "seo").glob("*.json"))

        self.assertEqual(code, 0)
        self.assertEqual(len(reports), 1)
        self.assertEqual(len(machine_reports), 1)


if __name__ == "__main__":
    unittest.main()
