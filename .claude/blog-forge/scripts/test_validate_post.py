"""Boundary tests for the LinkedIn publish gate."""

from __future__ import annotations

import unittest

from .validate_post import Report, check_linkedin

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


if __name__ == "__main__":
    unittest.main()
