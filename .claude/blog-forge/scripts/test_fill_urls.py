"""Tests for public URL placeholder handling."""

from __future__ import annotations

import unittest

from .fill_urls import (
    is_public_minio_download,
    read_manifest_order,
    unresolved_manifest_order,
)


class TestManifestOrder(unittest.TestCase):
    def test_reads_images_and_optional_public_lab_in_table_order(self) -> None:
        manifest = """| Placeholder | File |
|---|---|
| COVER | assets/cover.png |
| LAB_01 | lab/run.py |
| FIG_01 | assets/figure.png |
"""
        self.assertEqual(
            read_manifest_order(manifest),
            ["COVER", "LAB_01", "FIG_01"],
        )

    def test_returns_only_placeholders_still_present_in_the_article(self) -> None:
        manifest = """| Placeholder | File |
|---|---|
| COVER | assets/cover.png |
| LAB_01 | lab/run.py |
| FIG_01 | assets/figure.png |
"""
        body = "[Download `run.py`](LAB_01)\n\n![Figure](FIG_01)"
        self.assertEqual(
            unresolved_manifest_order(manifest, body),
            ["LAB_01", "FIG_01"],
        )

    def test_lab_downloads_must_use_public_minio_media_urls(self) -> None:
        self.assertTrue(
            is_public_minio_download(
                "https://minio.canery.in/media/labs/example/run.py"
            )
        )
        self.assertFalse(
            is_public_minio_download("https://github.com/example/lab/run.py")
        )


if __name__ == "__main__":
    unittest.main()
