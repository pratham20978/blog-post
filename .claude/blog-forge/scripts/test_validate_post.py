"""Boundary tests for the LinkedIn publish gate."""

from __future__ import annotations

import unittest

from .validate_post import (
    Report,
    check_linkedin,
    check_public_boundary,
    check_publish,
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
        self.assertTrue(any("public GitHub lab link" in item for item in report.errors))

    def test_accepts_lab_paths_when_a_public_github_lab_is_declared(self) -> None:
        for target in (
            "LAB_REPO",
            "https://github.com/example/public-lab",
        ):
            with self.subTest(target=target):
                body = f"""[Public GitHub lab]({target})

```bash
python examples/demo.py
```
"""
                report = Report()
                check_public_boundary(body, report)
                self.assertEqual(report.errors, [])

    def test_publish_rejects_an_unresolved_lab_repository(self) -> None:
        report = Report()
        check_publish("[Public GitHub lab](LAB_REPO)", report)
        self.assertTrue(any("LAB_REPO" in item for item in report.errors))

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


if __name__ == "__main__":
    unittest.main()
