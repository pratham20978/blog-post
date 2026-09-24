"""Boundary tests for the LinkedIn publish gate and the post quality gates."""

from __future__ import annotations

import unittest
import struct
from pathlib import Path
from tempfile import TemporaryDirectory

from .validate_post import (
    Report,
    check_frontmatter,
    check_lab_downloads,
    check_linkedin,
    check_public_boundary,
    check_publish,
    check_research,
    check_routes,
    check_social,
    check_structure,
)

CANONICAL = "https://canery.in/blogs/typed-metadata"
PROMPT = (
    "SCENE AND INTENDED USE\nA quiet editorial studio with one precise technical concept "
    "in view.\n\nSUBJECT\nAn engineer teaching the concept through a single physical "
    "metaphor.\n\nKEY DETAILS\nClear hierarchy, consistent character, restrained black, "
    "cream, and one amber accent, subtle paper texture, deliberate negative space.\n\n"
    "CONSTRAINTS\n4:5 portrait frame for a LinkedIn carousel, text-light, no logos, no "
    "watermark, no UI screenshot, no dense labels. Maintain the same visual world, scale "
    "language, line weight, palette, and recurring objects across every frame."
)


def prompts(count: int, *, duplicate: bool = False) -> str:
    blocks = []
    for number in range(1, count + 1):
        prompt = PROMPT if duplicate else f"{PROMPT} Distinct frame concept number {number}."
        alt = (
            "An engineer advances the coherent technical lesson through "
            f"teaching beat {number}, using one clear visual metaphor."
        )
        blocks.append(
            f"""## {number:02d} — Teaching beat {number}

- Narrative beat: The sequence advances through teaching beat {number}.
- File: `linkedin-{number:02d}-teaching-beat.png`
- Alt text: {alt}

### Prompt

```text
{prompt}
```
"""
        )
    return "\n".join(blocks)


def linkedin(count: int, canonical: str = CANONICAL) -> str:
    order = "\n".join(
        f"{number}. `linkedin-{number:02d}-teaching-beat.png`"
        for number in range(1, count + 1)
    )
    return f"""# LinkedIn post

A concise lesson for engineers.

## Carousel order

{order}

## Accessibility checklist

- Add every supplied alt text.
- Check reading order and contrast.

## First comment

The durable takeaway: make the invisible mechanism visible.

Read the full article on Canery: {canonical}
"""


class TestLinkedInGate(unittest.TestCase):
    def report(self, count: int, *, canonical: str = CANONICAL, duplicate: bool = False) -> Report:
        report = Report()
        check_linkedin(
            {"canonical_url": canonical},
            prompts(count, duplicate=duplicate),
            linkedin(count, canonical),
            report,
        )
        return report

    def test_accepts_4_7_and_10_frame_sequences(self) -> None:
        for count in (4, 7, 10):
            with self.subTest(count=count):
                self.assertEqual(self.report(count).errors, [])

    def test_rejects_counts_outside_the_boundary(self) -> None:
        for count in (3, 11):
            with self.subTest(count=count):
                errors = self.report(count).errors
                self.assertTrue(any("need 4 to 10" in error for error in errors))

    def test_rejects_an_unresolved_canonical_url(self) -> None:
        for canonical in ("<canonical_url>", "https://<site>/blogs/article"):
            with self.subTest(canonical=canonical):
                errors = self.report(4, canonical=canonical).errors
                self.assertTrue(any("resolved http(s) URL" in error for error in errors))

    def test_rejects_duplicate_prompts(self) -> None:
        errors = self.report(4, duplicate=True).errors
        self.assertIn("linkedin: image prompts must not be duplicates", errors)

    def test_body_h1_is_rejected_but_page_shell_title_is_not_required(self) -> None:
        body = """**Insights** — Direct answer.

## Why this matters
## The problem
## Worked example
## Intuition
## Limitations and common mistakes
## Key takeaways
## References
"""
        clean = Report()
        check_structure(body, clean)
        self.assertEqual(clean.errors, [])

        duplicated = Report()
        check_structure("# Duplicate page title\n\n" + body, duplicated)
        self.assertTrue(any("page shell owns the H1" in item for item in duplicated.errors))


def social_document(feed_count: int = 5, story_count: int = 3, *, duplicate_alt: bool = False) -> str:
    def order(kind: str, count: int) -> str:
        return "\n".join(
            f"{number}. `assets/social/{kind}-{number:02d}-teaching-beat.png` — "
            + (f"Overlay: Technical beat {number}." if kind == "story" else f"Teaching beat {number}.")
            for number in range(1, count + 1)
        )

    def metadata(kind: str, count: int) -> str:
        blocks = []
        for number in range(1, count + 1):
            role = "cover" if number == 1 else ("cta" if number == count else "technical")
            dimensions = "1080×1350" if kind == "feed" else "1080×1920"
            platforms = "Instagram feed, LinkedIn" if kind == "feed" else "Instagram Story"
            alt_number = 1 if duplicate_alt else number
            blocks.append(f"""### {kind}-{number:02d}-teaching-beat

- File: `assets/social/{kind}-{number:02d}-teaching-beat.png`
- Title: {kind.title()} technical beat {number}
- Platforms: {platforms}
- Role: {role}
- Dimensions: {dimensions}
- Narrative beat: The {kind} sequence advances through distinct technical beat {number}.
- Technical source: Figure {number} and the worked example
- Visual structure: Headline, technical diagram, evidence annotation, and takeaway in reading order.
- Visible-text transcript: Technical beat {number}; evidence; one precise takeaway.
- Alt text: Compatibility evidence advances through {kind} technical beat {alt_number}, with a concrete diagnostic artifact and result.
- Long description: This {kind} frame explains technical beat {number} with a concrete artifact, its evidence, and the conclusion an engineer should draw.
- Keywords: CUDA, compatibility, diagnostic beat {number}
- Canonical URL: {CANONICAL}
""")
        return "\n".join(blocks)

    return f"""---
social_schema: 2
canonical_url: "{CANONICAL}"
---

# Social publishing package — typed-metadata

## LinkedIn post

A concise technical lesson for engineers, grounded in one reproducible diagnostic sequence.

## LinkedIn first comment

Audit the executable artifact before rebuilding the stack.

Read the full article on Canery: {CANONICAL}

## Instagram caption

Swipe through a concrete compatibility audit, then use the evidence to repair only the broken layer.

## Shared feed order

{order("feed", feed_count)}

## Instagram Story

- CTA: Read the full article on Canery
- Link sticker label: Read the article
- Link sticker URL: {CANONICAL}

### Story order

{order("story", story_count)}

## Asset metadata

{metadata("feed", feed_count)}
{metadata("story", story_count)}
"""


def write_social_assets(root: Path, feed_count: int = 5, story_count: int = 3) -> None:
    social_dir = root / "assets" / "social"
    social_dir.mkdir(parents=True)
    for kind, count, height, logo_y, logo_width in (
        ("feed", feed_count, 1350, 72, 220),
        ("story", story_count, 1920, 250, 245),
    ):
        marker = (
            f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
            f'data-logo-width="{logo_width}"><path d="M0 0h10v10z"/></g>'
        )
        svg = (
            f'<svg viewBox="0 0 1080 {height}" width="1080" height="{height}">'
            f"{marker}</svg>"
        )
        png_header = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 1080, height)
        for number in range(1, count + 1):
            stem = f"{kind}-{number:02d}-teaching-beat"
            (social_dir / f"{stem}.html").write_text(svg, encoding="utf-8")
            (social_dir / f"{stem}.svg").write_text(svg, encoding="utf-8")
            (social_dir / f"{stem}.png").write_bytes(png_header)


class TestSocialGate(unittest.TestCase):
    def validate(self, *, duplicate_alt: bool = False) -> tuple[Report, Path, TemporaryDirectory]:
        directory = TemporaryDirectory()
        root = Path(directory.name)
        write_social_assets(root)
        report = Report()
        check_social(
            {"canonical_url": CANONICAL},
            root,
            social_document(duplicate_alt=duplicate_alt),
            prompts(5),
            report,
        )
        return report, root, directory

    def test_accepts_finished_feed_story_and_unchanged_prompts(self) -> None:
        report, _, directory = self.validate()
        self.addCleanup(directory.cleanup)
        self.assertEqual(report.errors, [])

    def test_rejects_duplicate_descriptions(self) -> None:
        report, _, directory = self.validate(duplicate_alt=True)
        self.addCleanup(directory.cleanup)
        self.assertIn("social: alt text must be unique", report.errors)

    def test_rejects_a_broken_asset_triplet(self) -> None:
        report, root, directory = self.validate()
        self.addCleanup(directory.cleanup)
        (root / "assets" / "social" / "feed-03-teaching-beat.svg").unlink()
        report = Report()
        check_social(
            {"canonical_url": CANONICAL}, root, social_document(), prompts(5), report
        )
        self.assertTrue(any("missing feed-03-teaching-beat.svg" in item for item in report.errors))

    def test_rejects_incomplete_metadata_and_story_copy(self) -> None:
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        write_social_assets(root)
        document = social_document().replace("- Title: Feed technical beat 2\n", "", 1)
        document = document.replace("- CTA: Read the full article on Canery\n", "", 1)
        document = document.replace("Overlay: Technical beat 2.", "Technical beat 2.", 1)
        report = Report()
        check_social({"canonical_url": CANONICAL}, root, document, prompts(5), report)
        self.assertTrue(any("missing metadata: Title" in item for item in report.errors))
        self.assertIn("social: Instagram Story needs CTA copy", report.errors)
        self.assertIn(
            "social: every Story order entry needs explicit overlay copy", report.errors
        )

    def test_rejects_wrong_dimensions_and_missing_logo(self) -> None:
        report, root, directory = self.validate()
        self.addCleanup(directory.cleanup)
        social_dir = root / "assets" / "social"
        wrong = b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\rIHDR" + struct.pack(">II", 1000, 1000)
        (social_dir / "story-02-teaching-beat.png").write_bytes(wrong)
        source = social_dir / "feed-02-teaching-beat.html"
        source.write_text(source.read_text(encoding="utf-8").replace("data-canery-logo", "data-logo"), encoding="utf-8")
        report = Report()
        check_social(
            {"canonical_url": CANONICAL}, root, social_document(), prompts(5), report
        )
        self.assertTrue(any("expected 1080×1920" in item for item in report.errors))
        self.assertTrue(any("lacks the locked Canery logo" in item for item in report.errors))


class TestPublicBoundary(unittest.TestCase):
    def test_accepts_public_links_fragments_and_site_routes(self) -> None:
        body = """Read [the docs](https://example.com/docs), [this section](#details),
[another article](/blogs/another-article), or <a href="mailto:editor@example.com">email us</a>.
"""
        report = Report()
        check_public_boundary(body, report)
        self.assertEqual(report.errors, [])

    def test_rejects_relative_markdown_and_reference_links(self) -> None:
        body = """Run [the full example](examples/demo.py).

The measurements are in [the lab notes][lab-notes].

[lab-notes]: ../lab/results.md
"""
        report = Report()
        check_public_boundary(body, report)
        self.assertTrue(any("examples/demo.py" in item for item in report.errors))
        self.assertTrue(any("../lab/results.md" in item for item in report.errors))

    def test_rejects_plain_references_to_private_build_artifacts(self) -> None:
        body = "See `outline.md` and the research/ folder for the missing explanation."
        report = Report()
        check_public_boundary(body, report)
        self.assertTrue(any("outline.md" in item for item in report.errors))
        self.assertTrue(any("research/" in item for item in report.errors))

    def test_rejects_private_artifacts_inside_fenced_commands(self) -> None:
        body = """```bash
python examples/demo.py
```
"""
        report = Report()
        check_public_boundary(body, report)
        self.assertTrue(any("MinIO lab downloads" in item for item in report.errors))

    def test_accepts_lab_paths_when_minio_downloads_are_declared(self) -> None:
        for target in (
            "LAB_01",
            "https://minio.canery.in/media/labs/example/demo.py",
        ):
            with self.subTest(target=target):
                body = f"""## References

### Lab downloads

[Download `demo.py`]({target})

```bash
python examples/demo.py
```
"""
                report = Report()
                check_public_boundary(body, report)
                self.assertEqual(report.errors, [])

    def test_publish_rejects_unresolved_lab_downloads(self) -> None:
        report = Report()
        check_publish("[Download `demo.py`](LAB_01)", report)
        self.assertTrue(any("LAB_01" in item for item in report.errors))

    def test_lab_examples_inside_html_comments_are_ignored(self) -> None:
        report = Report()
        check_publish("<!-- [`run.py`](LAB_01) -->", report)
        self.assertEqual(report.errors, [])

    def test_lab_gate_matches_local_files_manifest_and_reference_links(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lab").mkdir()
            (root / "lab" / "README.md").write_text("Run the lab.", encoding="utf-8")
            (root / "lab" / "run.py").write_text("print('ok')\n", encoding="utf-8")
            manifest = """| Placeholder | File |
|---|---|
| LAB_01 | `lab/README.md` |
| LAB_02 | `lab/run.py` |
"""
            body = """## References

### Lab downloads

- [`README.md`](LAB_01) — setup and run order.
- [`run.py`](LAB_02) — runnable experiment.

### Sources
"""
            report = Report()
            check_lab_downloads(body, manifest, root, report)
            self.assertEqual(report.errors, [])

    def test_lab_gate_rejects_non_minio_downloads(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "lab").mkdir()
            (root / "lab" / "run.py").write_text("print('ok')\n", encoding="utf-8")
            manifest = """| Placeholder | File |
|---|---|
| LAB_01 | `lab/run.py` |
"""
            body = """## References

### Lab downloads

- [`run.py`](https://github.com/example/lab/run.py) — runnable experiment.
"""
            report = Report()
            check_lab_downloads(body, manifest, root, report)
            self.assertTrue(any("minio.canery.in" in item for item in report.errors))

    def test_does_not_treat_image_syntax_as_a_normal_link(self) -> None:
        report = Report()
        check_public_boundary("![A useful diagram](FIG_01)", report)
        self.assertEqual(report.errors, [])

    def test_publish_requires_public_image_urls(self) -> None:
        local = Report()
        check_publish("![Diagram](assets/diagram.png)", local)
        self.assertTrue(any("absolute public http(s) URL" in item for item in local.errors))

        public = Report()
        check_publish("![Diagram](https://cdn.example.com/diagram.png)", public)
        self.assertEqual(public.errors, [])


def manifest_document(
    *,
    routes: bool = True,
    route: str = "mermaid",
    why: str = "14 nodes, edges cross",
    cover_route: str = "generated",
    source_credit: str = "—",
    rights: str = "—",
) -> str:
    if not routes:
        return """| Placeholder | Local file | Suggested object key | Alt text |
|---|---|---|---|
| COVER | assets/cover.png | blog/post/cover-v1.png | The cover image |
| FIG_01 | assets/fig-01-system.png | blog/post/fig-01-system-v1.png | The whole system |
"""
    return f"""| Placeholder | Local file | Route | Why | Source credit | Rights | Suggested object key | Alt text |
|---|---|---|---|---|---|---|---|
| COVER | assets/cover.png | {cover_route} | one atmospheric image | — | — | blog/post/cover-v1.png | The cover image |
| FIG_01 | assets/fig-01-system.png | {route} | {why} | {source_credit} | {rights} | blog/post/fig-01-system-v1.png | The whole system |
"""


def write_figure_sources(root: Path, *suffixes: str) -> None:
    assets = root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "cover.png").write_bytes(b"")
    for suffix in suffixes:
        (assets / f"fig-01-system{suffix}").write_text("source", encoding="utf-8")


class TestFigureRoutes(unittest.TestCase):
    def test_a_manifest_without_routes_warns_and_does_not_fail(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_routes(manifest_document(routes=False), Path(directory), report)
            self.assertEqual(report.errors, [])
            self.assertTrue(
                any("records no figure routes" in item for item in report.warnings)
            )

    def test_accepts_a_route_whose_source_file_is_on_disk(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_figure_sources(root, ".mmd", ".png")
            report = Report()
            check_routes(manifest_document(), root, report)
            self.assertEqual(report.errors, [])
            self.assertEqual(report.warnings, [])

    def test_rejects_an_unknown_route_token(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_routes(manifest_document(route="diagram"), Path(directory), report)
            self.assertTrue(
                any("FIG_01 has unknown route 'diagram'" in item for item in report.errors)
            )

    def test_accepts_a_relevant_rights_cleared_source_figure(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_figure_sources(root, ".png")
            report = Report()
            check_routes(
                manifest_document(
                    route="source",
                    why="original Figure 2 directly explains this section",
                    source_credit="Author et al., Paper, Figure 2, https://example.org/paper",
                    rights="CC BY 4.0",
                ),
                root,
                report,
            )
            self.assertEqual(report.errors, [])

    def test_rejects_a_source_figure_without_credit_or_rights(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_figure_sources(root, ".png")
            report = Report()
            check_routes(manifest_document(route="source"), root, report)
            self.assertTrue(any("without paper" in item for item in report.errors))
            self.assertTrue(any("without a verified licence" in item for item in report.errors))

    def test_rejects_a_route_with_no_reason(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_routes(manifest_document(why=""), Path(directory), report)
            self.assertTrue(
                any("no reason under 'Why'" in item for item in report.errors)
            )

    def test_rejects_a_mermaid_route_with_no_mmd_on_disk(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_figure_sources(root, ".png")
            report = Report()
            check_routes(manifest_document(), root, report)
            self.assertTrue(
                any(
                    "FIG_01 is routed 'mermaid' but assets/fig-01-system has no .mmd" in item
                    for item in report.errors
                )
            )

    def test_skips_the_source_check_before_any_asset_exists(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_routes(manifest_document(), Path(directory), report)
            self.assertEqual(report.errors, [])

    def test_warns_when_the_cover_takes_a_diagram_route(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_routes(
                manifest_document(cover_route="capture"), Path(directory), report
            )
            self.assertTrue(any("COVER is routed 'capture'" in item for item in report.warnings))


def ledger_document(
    *,
    search_log: bool = True,
    status: bool = True,
    databases: tuple = ("Google Scholar", "arXiv", "ACM Digital Library", "IEEE Xplore"),
    papers: int = 10,
    literature_note: bool = False,
    missing_identifier: bool = False,
    unknown_status: bool = False,
) -> str:
    rows = []
    if status:
        head = (
            "| ID | Tier | Source | Venue | Year | Identifier | Status | URL | Accessed |\n"
            "|---|---|---|---|---|---|---|---|---|"
        )
        for number in range(1, papers + 1):
            identifier = "—" if missing_identifier and number == 1 else f"10.1000/p{number}"
            state = "journal-article" if unknown_status and number == 1 else "peer-reviewed"
            rows.append(
                f"| S{number:02d} | T1 | Paper {number} | NeurIPS | 2020 | {identifier} | "
                f"{state} | https://example.com/{number} | 2026-09-20 |"
            )
    else:
        head = "| ID | Tier | Source | URL | Accessed |\n|---|---|---|---|---|"
        for number in range(1, papers + 1):
            rows.append(
                f"| S{number:02d} | T1 | Paper {number} | "
                f"https://example.com/{number} | 2026-09-20 |"
            )

    document = "# Source ledger\n\n## Sources\n\n" + head + "\n" + "\n".join(rows) + "\n"
    if search_log:
        log = "\n".join(
            f'| {number} | 1 | {database} | "query {number}" | one paper |'
            for number, database in enumerate(databases, start=1)
        )
        document += (
            "\n## Search log\n\n| # | Rung | Database | Query | Returned |\n"
            "|---|---|---|---|---|\n" + log + "\n"
        )
    if literature_note:
        document += (
            "\n## Literature note\n\nThis topic is a vendor-specific behaviour with no "
            "research literature, so the sweep rests on official docs and the source tree.\n"
        )
    return document


class TestResearchSweep(unittest.TestCase):
    def test_accepts_a_complete_sweep(self) -> None:
        report = Report()
        check_research(ledger_document(), "L4", report)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_a_legacy_ledger_warns_and_does_not_fail(self) -> None:
        report = Report()
        check_research(ledger_document(search_log=False, status=False), "L4", report)
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)
        self.assertIn("no search log", report.warnings[0])

    def test_a_legacy_sources_table_warns_once(self) -> None:
        report = Report()
        check_research(ledger_document(status=False), "L4", report)
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)
        self.assertIn("no Status column", report.warnings[0])

    def test_rejects_too_few_scholarly_databases(self) -> None:
        report = Report()
        check_research(
            ledger_document(databases=("Google Scholar", "arXiv")), "L4", report
        )
        self.assertTrue(
            any("2 scholarly databases queried, L4 needs 4" in item for item in report.errors)
        )

    def test_rejects_too_few_peer_reviewed_sources(self) -> None:
        report = Report()
        check_research(ledger_document(papers=2), "L4", report)
        self.assertTrue(
            any("2 peer-reviewed or standard sources" in item for item in report.errors)
        )

    def test_a_literature_note_downgrades_the_paper_floor(self) -> None:
        report = Report()
        check_research(ledger_document(papers=2, literature_note=True), "L4", report)
        self.assertEqual(report.errors, [])
        self.assertTrue(
            any("literature note downgraded" in item for item in report.warnings)
        )

    def test_rejects_a_peer_reviewed_source_with_no_identifier(self) -> None:
        report = Report()
        check_research(ledger_document(papers=4, missing_identifier=True), "L1", report)
        self.assertTrue(
            any("peer-reviewed source S01 carries no identifier" in item
                for item in report.errors)
        )

    def test_rejects_a_status_outside_the_allowed_tokens(self) -> None:
        report = Report()
        check_research(ledger_document(papers=4, unknown_status=True), "L1", report)
        self.assertTrue(
            any("source S01 has status 'journal-article'" in item for item in report.errors)
        )


def frontmatter(**overrides) -> dict:
    fields = {
        "title": "How PostgreSQL uses processes",
        "slug": "postgresql-foundations-process-layer",
        "date": "2026-09-19",
        "summary": "A" * 150,
        "tags": "[databases, postgresql, autovacuum, checkpointer]",
        "category": "databases",
        "tier": "L4",
        "difficulty": "intermediate",
        "reading_minutes": "50",
    }
    fields.update(overrides)
    return fields


def series_context(extra: str = "") -> str:
    return f"""# Series context — PostgreSQL Foundations

## Series invariants

- Audience: database engineers

## Part status

| # | Slug | Status | Owns | Actual handoff |
|---|---|---|---|---|
| 1 | memory-layer | ready | memory | process layer |

## Knowledge established

- Shared buffers and private memory have different lifetimes.

## Decisions to preserve

- Use PostgreSQL's own process names.

## Open threads

- Process ownership belongs to part 2.

## Next part brief

- Must teach the process layer without repeating memory sizing.

{extra}
"""


class TestSeriesFrontmatter(unittest.TestCase):
    def post_root(self, directory: str, *, series_member: bool = False) -> Path:
        root = Path(directory) / "posts"
        if series_member:
            root = root / "postgresql-foundations"
        root = root / "postgresql-foundations-process-layer"
        root.mkdir(parents=True)
        return root

    def test_a_post_outside_a_series_is_unaffected(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_frontmatter(frontmatter(), self.post_root(directory), report)
            self.assertEqual(report.errors, [])
            self.assertEqual(report.warnings, [])

    def test_rejects_series_without_series_position(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_frontmatter(
                frontmatter(series="postgresql-foundations"),
                self.post_root(directory, series_member=True),
                report,
            )
            self.assertIn(
                "frontmatter: 'series' is set without 'series_position'", report.errors
            )

    def test_rejects_series_position_without_series(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_frontmatter(
                frontmatter(series_position="2"),
                self.post_root(directory, series_member=True),
                report,
            )
            self.assertIn(
                "frontmatter: 'series_position' is set without 'series'", report.errors
            )

    def test_rejects_a_malformed_slug_or_position(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_frontmatter(
                frontmatter(series="PostgreSQL Foundations", series_position="first"),
                self.post_root(directory, series_member=True),
                report,
            )
            self.assertTrue(
                any("must be lowercase and hyphenated" in item for item in report.errors)
            )
            self.assertTrue(
                any("must be a positive integer" in item for item in report.errors)
            )

    def test_warns_when_the_series_plan_is_not_committed(self) -> None:
        with TemporaryDirectory() as directory:
            report = Report()
            check_frontmatter(
                frontmatter(series="postgresql-foundations", series_position="2"),
                self.post_root(directory, series_member=True),
                report,
            )
            self.assertEqual(report.errors, [])
            self.assertIn(
                "series: no plan at posts/postgresql-foundations/plan.md; "
                "the plan sets each part's tier and scope",
                report.warnings,
            )
            self.assertTrue(
                any("no context at posts/postgresql-foundations/context.md" in item
                    for item in report.warnings)
            )

    def test_accepts_a_committed_series_plan_and_context(self) -> None:
        with TemporaryDirectory() as directory:
            root = self.post_root(directory, series_member=True)
            plan = Path(directory) / "posts" / "postgresql-foundations"
            plan.mkdir(parents=True, exist_ok=True)
            (plan / "plan.md").write_text("# Series plan", encoding="utf-8")
            (plan / "context.md").write_text(series_context(), encoding="utf-8")
            report = Report()
            check_frontmatter(
                frontmatter(series="postgresql-foundations", series_position="2"),
                root,
                report,
            )
            self.assertEqual(report.errors, [])
            self.assertEqual(report.warnings, [])

    def test_warns_when_series_context_is_incomplete(self) -> None:
        with TemporaryDirectory() as directory:
            root = self.post_root(directory, series_member=True)
            series_root = Path(directory) / "posts" / "postgresql-foundations"
            (series_root / "plan.md").write_text("# Series plan", encoding="utf-8")
            (series_root / "context.md").write_text(
                "# Series context", encoding="utf-8"
            )
            report = Report()
            check_frontmatter(
                frontmatter(series="postgresql-foundations", series_position="2"),
                root,
                report,
            )
            self.assertTrue(
                any("context.md is missing '## Next part brief'" in item
                    for item in report.warnings)
            )

    def test_warns_when_series_context_becomes_a_content_dump(self) -> None:
        with TemporaryDirectory() as directory:
            root = self.post_root(directory, series_member=True)
            series_root = Path(directory) / "posts" / "postgresql-foundations"
            (series_root / "plan.md").write_text("# Series plan", encoding="utf-8")
            (series_root / "context.md").write_text(
                series_context("knowledge " * 2100), encoding="utf-8"
            )
            report = Report()
            check_frontmatter(
                frontmatter(series="postgresql-foundations", series_position="2"),
                root,
                report,
            )
            self.assertTrue(
                any("consolidate it below 2000" in item for item in report.warnings)
            )

    def test_warns_when_a_series_member_uses_the_legacy_flat_layout(self) -> None:
        with TemporaryDirectory() as directory:
            root = self.post_root(directory)
            series_root = Path(directory) / "posts" / "postgresql-foundations"
            series_root.mkdir(parents=True)
            (series_root / "plan.md").write_text("# Series plan", encoding="utf-8")
            (series_root / "context.md").write_text(series_context(), encoding="utf-8")
            report = Report()
            check_frontmatter(
                frontmatter(series="postgresql-foundations", series_position="2"),
                root,
                report,
            )
            self.assertTrue(
                any("member should live at posts/postgresql-foundations/<post-slug>/" in item
                    for item in report.warnings)
            )


if __name__ == "__main__":
    unittest.main()
