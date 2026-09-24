"""Tests for deterministic social-card rendering and contract checks."""

from __future__ import annotations

import pathlib
import struct
import tempfile
import unittest
import zlib

from .render_social import (
    SocialRenderError,
    extract_svg,
    png_dimensions,
    png_has_logo_ink,
    render_source,
    validate_svg,
)


def svg(kind: str = "feed", *, logo: bool = True) -> str:
    width, height = (1080, 1350) if kind == "feed" else (1080, 1920)
    logo_y, logo_width = (72, 220) if kind == "feed" else (250, 245)
    marker = (
        f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
        f'data-logo-width="{logo_width}"><path d="M0 0h10v10z"/></g>'
        if logo
        else ""
    )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">{marker}</svg>'
    )


def write_png(path: pathlib.Path, width: int, height: int, *, color: bytes = b"\x00\x00\x00") -> None:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    raw = b"".join(b"\x00" + color * width for _ in range(height))
    payload = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(payload)


class TestSocialRenderer(unittest.TestCase):
    def test_extracts_one_inline_svg(self) -> None:
        source = pathlib.Path("feed-01-test.html")
        self.assertEqual(extract_svg(f"<html>{svg()}</html>", source), svg())
        with self.assertRaises(SocialRenderError):
            extract_svg("<html></html>", source)

    def test_validates_locked_dimensions_and_logo_position(self) -> None:
        self.assertEqual(validate_svg(svg(), "feed", pathlib.Path("feed-01-test.html")), (1080, 1350))
        self.assertEqual(
            validate_svg('<?xml version="1.0"?>\n' + svg(), "feed", pathlib.Path("feed-01-test.svg")),
            (1080, 1350),
        )
        self.assertEqual(
            validate_svg(svg("story"), "story", pathlib.Path("story-01-test.html")),
            (1080, 1920),
        )
        with self.assertRaises(SocialRenderError):
            validate_svg(svg(logo=False), "feed", pathlib.Path("feed-01-test.html"))

    def test_png_dimensions_reads_ihdr(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "frame.png"
            write_png(path, 1080, 1350)
            self.assertEqual(png_dimensions(path), (1080, 1350))

    def test_png_branding_region_must_be_painted(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            painted = root / "painted.png"
            blank = root / "blank.png"
            write_png(painted, 1080, 1350)
            write_png(blank, 1080, 1350, color=b"\xff\xff\xff")
            self.assertTrue(png_has_logo_ink(painted, "feed"))
            self.assertFalse(png_has_logo_ink(blank, "feed"))

    def test_check_mode_requires_complete_triplet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            html = root / "feed-01-test.html"
            html.write_text(f"<html>{svg()}</html>", encoding="utf-8")
            with self.assertRaises(SocialRenderError):
                render_source(html, check_only=True)
            html.with_suffix(".svg").write_text(svg(), encoding="utf-8")
            write_png(html.with_suffix(".png"), 1080, 1350)
            render_source(html, check_only=True)


if __name__ == "__main__":
    unittest.main()
