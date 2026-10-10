#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important idea (every 3x3 derivative is
one stencil whose outer rows carry a single free weight p; Sobel, Scharr and Prewitt
are values of p), white-smoke paper, a single tangerine element. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-kernel-design-separability-borders-derivatives"


def build():
    s = ""
    # motif: the 3x3 x-derivative, outer rows in the accent (the free weight p)
    cw, gx, gy = 78, 96, 150
    cells = [["−p", "0", "p"], ["−(1−2p)", "0", "1−2p"], ["−p", "0", "p"]]
    for r in range(3):
        for c in range(3):
            outer = r != 1 and c != 1
            fill = "rgba(235,108,54,0.10)" if outer else "#ffffff"
            stroke = ACCENT if outer else "rgba(45,49,66,0.30)"
            s += (f'<rect x="{gx + c * cw}" y="{gy + r * cw}" width="{cw}" height="{cw}" '
                  f'fill="{fill}" stroke="{stroke}" stroke-width="{1.4 if outer else 0.8}"/>')
            s += mono(gx + c * cw + cw / 2, gy + r * cw + cw / 2 + 5, cells[r][c],
                      size=14 if len(cells[r][c]) < 5 else 11,
                      fill=ACCENT if outer else INK, weight="500")
    s += mono(gx + 1.5 * cw, gy - 16, "½ ×", size=11, fill=SOFT, track="0.1em")
    # the p line underneath, with three named members
    lx0, lx1, ly = gx, gx + 3 * cw, gy + 3 * cw + 92
    X = lambda p: lx0 + p / 0.36 * (lx1 - lx0)
    s += f'<line x1="{lx0}" y1="{ly}" x2="{lx1}" y2="{ly}" stroke="rgba(45,49,66,0.35)"/>'
    for p, name, col in ((3 / 16, "Scharr 3/16", ACCENT), (0.25, "Sobel 1/4", MUTED),
                         (1 / 3, "Prewitt 1/3", MUTED)):
        s += f'<circle cx="{X(p):.1f}" cy="{ly}" r="5" fill="{col}"/>'
    s += mono(X(3 / 16) - 6, ly - 14, "Scharr 3/16", size=9, fill=ACCENT, anchor="end", track="0.06em")
    s += mono(X(0.25), ly + 22, "Sobel 1/4", size=9, fill=MUTED, track="0.06em")
    s += mono(X(1 / 3), ly - 14, "Prewitt 1/3", size=9, fill=MUTED, track="0.06em")
    s += mono(lx0, ly + 44, "p, the one free number", size=9, fill=SOFT, anchor="start", track="0.12em")

    # title block
    s += mono(560, 236, "algorithms  ·  image processing by hand, part 4", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Kernel Design", size=58, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 350, "where a kernel's numbers come from", size=17, fill=MUTED,
             family=SANS, anchor="start")
    s += txt(560, 376, "separability, borders and optimised derivatives", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="96" y1="536" x2="1104" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 562, "sobel · scharr · farid–simoncelli · truncation · border modes", size=10,
              fill=MUTED, anchor="start", track="0.14em")

    svg = svg_doc(VW, VH, s)
    (HERE / f"{STEM}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg,
                                      encoding="utf-8")
    (HERE / f"{STEM}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / f"{STEM}.svg", HERE / f"{STEM}.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
