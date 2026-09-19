"""Tests for public URL placeholder handling."""

from __future__ import annotations

import unittest

from .fill_urls import read_manifest_order, unresolved_manifest_order


class TestManifestOrder(unittest.TestCase):
    def test_reads_images_and_optional_public_lab_in_table_order(self) -> None:
        manifest = """| Placeholder | File |
|---|---|
| COVER | assets/cover.png |
| LAB_REPO | lab/ |
| FIG_01 | assets/figure.png |
"""
        self.assertEqual(
            read_manifest_order(manifest),
            ["COVER", "LAB_REPO", "FIG_01"],
        )

    def test_returns_only_placeholders_still_present_in_the_article(self) -> None:
        manifest = """| Placeholder | File |
|---|---|
| COVER | assets/cover.png |
| LAB_REPO | lab/ |
| FIG_01 | assets/figure.png |
"""
        body = "[Public GitHub lab](LAB_REPO)\n\n![Figure](FIG_01)"
        self.assertEqual(
            unresolved_manifest_order(manifest, body),
            ["LAB_REPO", "FIG_01"],
        )


if __name__ == "__main__":
    unittest.main()
