#!/usr/bin/env python3
"""Catch the figure defects the other gates are blind to.

`validate_post.py` checks frontmatter, headings, placeholders and links.
`render_social.py --check` checks canvas size and the logo. Neither looks at
what the picture does, so this pass reads the rendered SVGs and asserts:

  1. every arrow terminates on a node edge, and enters it head-on
  2. no text runs off the canvas

Usage:
    python3 lint_visuals.py posts/<slug>/assets/
    python3 lint_visuals.py posts/<slug>/assets/ --strict   # exit 1 on findings

Free vectors and plot axes legitimately touch no node, so arrow findings are
advisory by default: read them, then decide. Text overflow is always a defect.
"""

from __future__ import annotations

import argparse
import html
import pathlib
import re
import sys

# Rough advance width per em, measured against the shipped faces.
EM = {"mono": 0.605, "serif": 0.42, "sans": 0.545}
ATTR = re.compile(r'([\w:-]+)="([^"]*)"')
TEXT = re.compile(r"<text\b([^>]*)>([\s\S]*?)</text>")
RECT = re.compile(r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" '
                  r'height="([\d.]+)"[^>]*?stroke="(?!none)([^"]+)"')
LINE = re.compile(r'<line x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" '
                  r'y2="([-\d.]+)"[^>]*marker-end="url\(#([^)]+)\)"')
PATH = re.compile(r'<path d="([^"]+)"[^>]*marker-end="url\(#([^)]+)\)"')
EDGE_TOL = 10.0


def family(attrs: dict[str, str]) -> str:
    f = attrs.get("font-family", "")
    return "mono" if "Mono" in f else ("serif" if "Serif" in f else "sans")


def strip_chrome(svg: str) -> str:
    svg = re.sub(r"<defs>[\s\S]*?</defs>", "", svg)
    # Rotated labels cannot be box-tested with a horizontal advance estimate.
    return re.sub(r'<g transform="rotate\([^"]*\)">[\s\S]*?</g>', "", svg)


def overflowing(svg: str) -> list[str]:
    box = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg)
    if not box:
        return []
    width, height = float(box.group(1)), float(box.group(2))
    out = []
    for match in TEXT.finditer(strip_chrome(svg)):
        attrs = dict(ATTR.findall(match.group(1)))
        body = html.unescape(re.sub(r"<[^>]+>", "", match.group(2))).strip()
        if not body or "x" not in attrs:
            continue
        size = float(attrs.get("font-size", 12))
        spacing = attrs.get("letter-spacing", "0")
        extra = float(spacing.rstrip("em")) * size if spacing.endswith("em") else 0.0
        run = len(body) * (EM[family(attrs)] * size + extra)
        x, y = float(attrs["x"]), float(attrs.get("y", 0))
        anchor = attrs.get("text-anchor", "start")
        left = x if anchor == "start" else (x - run / 2 if anchor == "middle" else x - run)
        why = []
        if left < -2:
            why.append(f"left by {-left:.0f}px")
        if left + run > width + 2:
            why.append(f"right by {left + run - width:.0f}px")
        if y > height:
            why.append(f"below the canvas by {y - height:.0f}px")
        if why:
            out.append(f"text {' / '.join(why)}: {body[:70]!r}")
    return out


def path_end(d: str) -> tuple[float, float, str]:
    x = y = px = py = 0.0
    for cmd, arg in re.findall(r"([MHVQ])([-\d., ]*)", d):
        nums = [float(v) for v in re.findall(r"-?[\d.]+", arg)]
        px, py = x, y
        if cmd == "M":
            x, y = nums[0], nums[1]
        elif cmd == "H":
            x = nums[-1]
        elif cmd == "V":
            y = nums[-1]
        elif cmd == "Q":
            x, y = nums[-2], nums[-1]
    return x, y, ("h" if abs(x - px) > abs(y - py) else "v")


def bad_arrows(svg: str) -> list[str]:
    body = strip_chrome(svg)
    nodes = [tuple(map(float, m.groups()[:4])) for m in RECT.finditer(body)
             if float(m.group(3)) >= 60 and float(m.group(4)) >= 40]
    ends = [(float(m.group(3)), float(m.group(4)),
             "h" if abs(float(m.group(3)) - float(m.group(1)))
             > abs(float(m.group(4)) - float(m.group(2))) else "v")
            for m in LINE.finditer(body)]
    ends += [path_end(m.group(1)) for m in PATH.finditer(body)]
    out = []
    for ex, ey, travel in ends:
        hit = None
        for x, y, w, h in nodes:
            if (-EDGE_TOL <= ey - y <= h + EDGE_TOL
                    and (abs(ex - x) <= EDGE_TOL or abs(ex - (x + w)) <= EDGE_TOL)):
                hit = "vertical"
                break
            if (-EDGE_TOL <= ex - x <= w + EDGE_TOL
                    and (abs(ey - y) <= EDGE_TOL or abs(ey - (y + h)) <= EDGE_TOL)):
                hit = "horizontal"
                break
        if hit is None:
            out.append(f"arrow at ({ex:.0f},{ey:.0f}) travelling {travel} touches no node")
        elif (travel == "h") != (hit == "vertical"):
            out.append(f"arrow at ({ex:.0f},{ey:.0f}) meets a {hit} edge side-on")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero when anything is reported")
    args = ap.parse_args(argv)

    root = pathlib.Path(args.directory)
    files = sorted(root.rglob("*.svg"))
    if not files:
        print(f"no SVGs under {root}")
        return 1

    overflow = arrows = 0
    for svg_path in files:
        svg = svg_path.read_text(encoding="utf-8")
        over, arrow = overflowing(svg), bad_arrows(svg)
        if over or arrow:
            print(f"\n{svg_path.relative_to(root)}")
        for line in over:
            overflow += 1
            print(f"  OVERFLOW  {line}")
        for line in arrow:
            arrows += 1
            print(f"  arrow     {line}")

    print(f"\n{len(files)} files · {overflow} text overflows · {arrows} arrow reports")
    print("arrow reports are advisory: free vectors and plot axes touch no node by design")
    return 1 if args.strict and (overflow or arrows) else 0


if __name__ == "__main__":
    sys.exit(main())
