#!/usr/bin/env python3
"""Render Blog Forge social-card HTML into standalone SVG and exact-size PNG.

Usage:
    python3 render_social.py posts/<slug>/assets/social/
    python3 render_social.py posts/<slug>/assets/social/ --check

Each source must contain one inline SVG and a marked Canery lockup. Feed cards
are 1080x1350; Story cards are 1080x1920. Rendering is intentionally local and
deterministic: this script never uploads or posts an asset.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

FRAME_RE = re.compile(r"^(feed|story)-(?P<number>\d{2})-[a-z0-9-]+$")
SVG_RE = re.compile(r"<svg\b[^>]*>[\s\S]*?</svg>", re.I)
ATTRIBUTE_RE = re.compile(r"(?P<name>[\w:-]+)=(?P<quote>['\"])(?P<value>.*?)\2", re.S)
EXPECTED = {
    "feed": (1080, 1350, {"x": "72", "y": "72", "width": "220"}),
    "story": (1080, 1920, {"x": "72", "y": "250", "width": "245"}),
}
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class SocialRenderError(ValueError):
    """A social source or rendered output violates the locked contract."""


def frame_kind(path: pathlib.Path) -> str:
    match = FRAME_RE.fullmatch(path.stem)
    if not match:
        raise SocialRenderError(
            f"{path.name}: expected feed-NN-name.html or story-NN-name.html"
        )
    return match.group(1)


def opening_attributes(svg: str) -> dict[str, str]:
    match = re.search(r"<svg\b[^>]*>", svg, re.I)
    if match is None:
        raise SocialRenderError("source has no SVG opening tag")
    opening = match.group(0)
    return {
        match.group("name"): match.group("value")
        for match in ATTRIBUTE_RE.finditer(opening)
    }


def extract_svg(html: str, source: pathlib.Path) -> str:
    matches = SVG_RE.findall(html)
    if len(matches) != 1:
        raise SocialRenderError(
            f"{source.name}: expected exactly one inline SVG, found {len(matches)}"
        )
    svg = matches[0]
    if 'xmlns="http://www.w3.org/2000/svg"' not in svg.split(">", 1)[0]:
        svg = svg.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return svg


def validate_svg(svg: str, kind: str, source: pathlib.Path) -> tuple[int, int]:
    width, height, logo = EXPECTED[kind]
    attrs = opening_attributes(svg)
    expected_viewbox = f"0 0 {width} {height}"
    if attrs.get("width") != str(width) or attrs.get("height") != str(height):
        raise SocialRenderError(
            f"{source.name}: SVG must declare width={width} and height={height}"
        )
    if attrs.get("viewBox") != expected_viewbox:
        raise SocialRenderError(
            f"{source.name}: SVG viewBox must be '{expected_viewbox}'"
        )

    marker = re.search(r"<g\b[^>]*data-canery-logo=['\"]lockup['\"][^>]*>", svg)
    if marker is None:
        raise SocialRenderError(
            f"{source.name}: missing <g data-canery-logo=\"lockup\">"
        )
    marker_attrs = {
        match.group("name"): match.group("value")
        for match in ATTRIBUTE_RE.finditer(marker.group(0))
    }
    for key, expected in logo.items():
        attr = f"data-logo-{key}"
        if marker_attrs.get(attr) != expected:
            raise SocialRenderError(
                f"{source.name}: {attr} must be {expected} for {kind} cards"
            )
    return width, height


def png_dimensions(path: pathlib.Path) -> tuple[int, int]:
    try:
        with path.open("rb") as handle:
            header = handle.read(24)
    except OSError as exc:
        raise SocialRenderError(f"cannot read {path}: {exc}") from exc
    if len(header) != 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise SocialRenderError(f"{path.name}: not a valid PNG header")
    return struct.unpack(">II", header[16:24])


def png_has_logo_ink(path: pathlib.Path, kind: str) -> bool:
    """Confirm the branded area was painted, not merely present in the SVG."""
    payload = path.read_bytes()
    if payload[:8] != PNG_SIGNATURE:
        raise SocialRenderError(f"{path.name}: not a PNG")

    offset = 8
    idat = bytearray()
    header: tuple[int, int, int, int, int, int, int] | None = None
    while offset + 12 <= len(payload):
        length = struct.unpack(">I", payload[offset:offset + 4])[0]
        chunk_type = payload[offset + 4:offset + 8]
        chunk_data = payload[offset + 8:offset + 8 + length]
        if chunk_type == b"IHDR":
            header = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            idat.extend(chunk_data)
        elif chunk_type == b"IEND":
            break
        offset += length + 12

    if header is None:
        raise SocialRenderError(f"{path.name}: missing PNG IHDR")
    width, height, depth, color_type, compression, filtering, interlace = header
    channels = {2: 3, 6: 4}.get(color_type)
    if depth != 8 or channels is None or compression or filtering or interlace:
        raise SocialRenderError(
            f"{path.name}: logo verification requires a non-interlaced 8-bit RGB/RGBA PNG"
        )

    try:
        raw = zlib.decompress(idat)
    except zlib.error as exc:
        raise SocialRenderError(f"{path.name}: invalid PNG image data") from exc
    stride = width * channels
    if len(raw) != (stride + 1) * height:
        raise SocialRenderError(f"{path.name}: unexpected PNG scanline length")

    expected_width, expected_height, logo = EXPECTED[kind]
    if (width, height) != (expected_width, expected_height):
        return False
    x0 = max(0, int(logo["x"]) - 12)
    x1 = min(width, int(logo["x"]) + int(logo["width"]) + 12)
    y0 = int(logo["y"])
    y1 = min(height, y0 + 64)
    previous = bytearray(stride)
    dark_pixels = 0
    cursor = 0

    for y in range(y1):
        filter_type = raw[cursor]
        scanline = bytearray(raw[cursor + 1:cursor + 1 + stride])
        cursor += stride + 1
        for index in range(stride):
            left = scanline[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                scanline[index] = (scanline[index] + left) & 255
            elif filter_type == 2:
                scanline[index] = (scanline[index] + above) & 255
            elif filter_type == 3:
                scanline[index] = (scanline[index] + ((left + above) // 2)) & 255
            elif filter_type == 4:
                estimate = left + above - upper_left
                distances = (abs(estimate - left), abs(estimate - above), abs(estimate - upper_left))
                predictor = (left, above, upper_left)[distances.index(min(distances))]
                scanline[index] = (scanline[index] + predictor) & 255
            elif filter_type != 0:
                raise SocialRenderError(f"{path.name}: unsupported PNG filter {filter_type}")

        if y0 <= y < y1:
            for x in range(x0, x1):
                pixel = x * channels
                if max(scanline[pixel:pixel + 3]) < 170:
                    dark_pixels += 1
        previous = scanline

    return dark_pixels >= 250


def chrome_binary() -> str:
    for candidate in ("google-chrome", "chromium", "chromium-browser"):
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise SocialRenderError(
        "Chrome/Chromium is required. Install google-chrome or chromium, then rerun."
    )


def render_png(svg: str, output: pathlib.Path, width: int, height: int) -> None:
    shim = (
        "<!doctype html><meta charset=\"utf-8\">"
        "<link href=\"https://fonts.googleapis.com/css2?family=Instrument+Serif"
        ":ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600"
        "&display=swap\" rel=\"stylesheet\">"
        f"<style>html,body{{margin:0;width:{width}px;height:{height}px;overflow:hidden;"
        "background:#f5f5f5}svg{display:block}</style>"
        + svg
    )
    with tempfile.TemporaryDirectory(prefix="blog-forge-social-") as directory:
        temp = pathlib.Path(directory)
        shim_path = temp / "frame.html"
        shim_path.write_text(shim, encoding="utf-8")
        profile = temp / "chrome-profile"
        command = [
            chrome_binary(),
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--run-all-compositor-stages-before-draw",
            "--virtual-time-budget=6000",
            f"--user-data-dir={profile}",
            "--force-device-scale-factor=1",
            f"--window-size={width},{height}",
            f"--screenshot={output.resolve()}",
            f"file://{shim_path}",
        ]
        kind = "feed" if height == EXPECTED["feed"][1] else "story"
        for attempt in range(1, 4):
            try:
                subprocess.run(command, check=True, capture_output=True, timeout=120)
            except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise SocialRenderError(f"Chrome failed while rendering {output.name}: {exc}") from exc
            if png_has_logo_ink(output, kind):
                return
        raise SocialRenderError(
            f"{output.name}: Chrome did not paint the Canery lockup after {attempt} attempts"
        )


def sources_in(directory: pathlib.Path) -> list[pathlib.Path]:
    if not directory.is_dir():
        raise SocialRenderError(f"not a directory: {directory}")
    sources = sorted(directory.glob("feed-*.html")) + sorted(directory.glob("story-*.html"))
    if not sources:
        raise SocialRenderError(f"no feed-*.html or story-*.html sources in {directory}")
    return sources


def render_source(source: pathlib.Path, *, check_only: bool = False) -> None:
    kind = frame_kind(source)
    svg = extract_svg(source.read_text(encoding="utf-8"), source)
    width, height = validate_svg(svg, kind, source)
    svg_path = source.with_suffix(".svg")
    png_path = source.with_suffix(".png")

    if check_only:
        for output in (svg_path, png_path):
            if not output.is_file():
                raise SocialRenderError(f"{source.name}: missing {output.name}")
        exported = svg_path.read_text(encoding="utf-8")
        validate_svg(exported, kind, svg_path)
        if png_dimensions(png_path) != (width, height):
            raise SocialRenderError(
                f"{png_path.name}: expected {width}x{height}, got {png_dimensions(png_path)}"
            )
        if not png_has_logo_ink(png_path, kind):
            raise SocialRenderError(f"{png_path.name}: Canery lockup was not painted")
        return

    svg_path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    render_png(svg, png_path, width, height)
    dimensions = png_dimensions(png_path)
    if dimensions != (width, height):
        raise SocialRenderError(
            f"{png_path.name}: Chrome produced {dimensions[0]}x{dimensions[1]}, "
            f"expected {width}x{height}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("social_dir", type=pathlib.Path)
    parser.add_argument(
        "--check", action="store_true", help="validate existing HTML/SVG/PNG triplets"
    )
    args = parser.parse_args(argv)

    try:
        sources = sources_in(args.social_dir)
        for source in sources:
            render_source(source, check_only=args.check)
            action = "checked" if args.check else "rendered"
            print(f"{action}: {source.stem}")
    except (OSError, UnicodeError, SocialRenderError) as exc:
        print(f"social render failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
