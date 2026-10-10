#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important idea (the stencil and its five
jobs), white-smoke paper, a single tangerine element. 1200 x 630.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SERIF, SANS, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    # motif: the five-point stencil, centre in accent, five spokes to five jobs
    cw, gx, gy = 56, 96, 224
    weights = [["0", "1", "0"], ["1", "−4", "1"], ["0", "1", "0"]]
    for r in range(3):
        for c in range(3):
            focal = (r, c) == (1, 1)
            s += (f'<rect x="{gx + c * cw}" y="{gy + r * cw}" width="{cw}" height="{cw}" '
                  f'fill="{ACCENT_TINT if focal else "#ffffff"}" '
                  f'stroke="{ACCENT if focal else "rgba(45,49,66,0.28)"}" stroke-width="{1.2 if focal else 0.8}"/>')
            s += txt(gx + c * cw + cw / 2, gy + r * cw + cw / 2 + 5, weights[r][c],
                     size=16, fill=ACCENT if focal else (SOFT if weights[r][c] == "0" else INK),
                     family=MONO, weight="600" if focal else "500")
    s += mono(gx, gy + 3 * cw + 36, "neighbour average minus centre, × 4", size=9, fill=SOFT,
              anchor="start", track="0.14em")
    # spokes
    jobs = ["sharpen", "find the edge", "pick the scale", "split the octaves", "keep it, not the pixels"]
    x1 = gx + 3 * cw + 16
    ys = [gy - 8, gy + 40, gy + 88, gy + 136, gy + 184]
    for y, job in zip(ys, jobs):
        s += (f'<path d="M {x1} {gy + 84} H {x1 + 24} Q {x1 + 32} {gy + 84} {x1 + 32} {gy + 84 + (8 if y > gy + 84 else -8)} '
              f'V {y + (-8 if y > gy + 84 else 8)} Q {x1 + 32} {y} {x1 + 40} {y} H {x1 + 56}" '
              f'fill="none" stroke="{MUTED}" stroke-width="1"/>')
        s += mono(x1 + 64, y + 3, job, size=10, fill=INK, anchor="start", track="0.12em", weight="500")

    # title block
    s += mono(560, 236, "algorithms  ·  child of image processing by hand", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "The Laplacian", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "by Hand", size=54, fill=ACCENT, family=SERIF, anchor="start")
    s += txt(560, 400, "what Gaussian blur removes, per unit of scale", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += (f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>')
    s += mono(84, 562, "edges · blobs · pyramids · sharpening", size=10, fill=MUTED,
              anchor="start", track="0.14em")
    s += mono(1116, 562, "canery", size=10, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg,
                                    encoding="utf-8")
    (HERE / "cover.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / "cover.svg", HERE / "cover.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
