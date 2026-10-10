#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif from the post's most important idea (three pools, one page on its way
to the log), white-smoke paper, a single tangerine element. 1200 x 630.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SERIF, SANS, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    # motif: three stacked pools, drawn as rows of small page cells
    gx, gy, cw, gap = 96, 176, 22, 6
    rows = [("shared buffers", 12, 3), ("WAL buffers", 5, 1), ("local memory", 7, 2)]
    y = gy
    for i, (name, n, h) in enumerate(rows):
        for r in range(h):
            for c in range(n):
                x = gx + c * (cw + gap)
                yy = y + r * (cw + gap)
                focal = (i == 0 and r == 1 and c == 4)
                s += (f'<rect x="{x}" y="{yy}" width="{cw}" height="{cw}" rx="3" '
                      f'fill="{ACCENT_TINT if focal else "#ffffff"}" '
                      f'stroke="{ACCENT if focal else "rgba(45,49,66,0.30)"}" stroke-width="{1.4 if focal else 0.8}"/>')
        s += mono(gx, y + h * (cw + gap) + 10, name, size=9, fill=SOFT, anchor="start", track="0.16em")
        y += h * (cw + gap) + 34
    # the page's path from the pool to the log
    px = gx + 4 * (cw + gap) + cw / 2
    py = gy + (cw + gap) + cw
    s += (f'<path d="M {px} {py + 4} V {gy + 3 * (cw + gap) + 20}" fill="none" stroke="{ACCENT}" '
          f'stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow-accent)"/>')
    s += mono(px + 12, gy + 3 * (cw + gap) + 14, "log first, then the page", size=8, fill=ACCENT, anchor="start", track="0.12em")

    # title block
    s += mono(560, 236, "databases  ·  postgresql foundations, part 1 of 3", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "How PostgreSQL", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "Uses Memory", size=54, fill=ACCENT, family=SERIF, anchor="start")
    s += txt(560, 400, "three pools, one rule, and the numbers behind them", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "shared buffers · the clock sweep · rings · WAL buffers · work_mem · memory contexts", size=10, fill=MUTED,
              anchor="start", track="0.14em")
    s += mono(1116, 562, "canery", size=10, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    (HERE / "cover.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / "cover.svg", HERE / "cover.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
