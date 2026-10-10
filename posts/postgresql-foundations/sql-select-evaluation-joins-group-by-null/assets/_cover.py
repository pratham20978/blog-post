#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif from the post's most important idea, white-smoke paper, a single
tangerine element. 1200 x 630. Same layout grid as parts 1-4 (title block at x=560,
motif on the left). Part 5's motif: rows of tiles that narrow as each clause hands a smaller
table to the next; in the last row two tiles tie for one place, in tangerine, one solid and one
dashed; eight dots beneath them, the eight clauses of the logical order.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MUTED, PAPER, RULE, SERIF, SANS,
                    SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def row(x0, y, n, t=16, g=5):
    s = ""
    for c in range(n):
        s += (f'<rect x="{x0 + c * (t + g)}" y="{y}" width="{t}" height="{t}" rx="3" '
              f'fill="#ffffff" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
    return s


def build():
    s = ""
    t, g, x0, y0 = 16, 5, 96, 236
    step = t + 18
    s += mono(x0, y0 - 24, "rows, clause by clause", size=9, fill=SOFT, anchor="start", track="0.16em")
    for i, n in enumerate((12, 8, 4)):
        s += row(x0, y0 + i * step, n)
    # the last row: one tile kept, then two tied for the second place
    yl = y0 + 3 * step
    s += row(x0, yl, 1)
    x2 = x0 + (t + g)
    s += (f'<rect x="{x2}" y="{yl}" width="{t}" height="{t}" rx="3" fill="{ACCENT_TINT}" '
          f'stroke="{ACCENT}" stroke-width="1.4"/>')
    x3 = x0 + 2 * (t + g) + 6
    s += (f'<rect x="{x3}" y="{yl}" width="{t}" height="{t}" rx="3" fill="{PAPER}" '
          f'stroke="{ACCENT}" stroke-width="1.4" stroke-dasharray="3,2"/>')
    # eight clauses beneath
    yd = yl + t + 52
    xs = [x0 + 8 + k * 38 for k in range(8)]
    s += (f'<line x1="{xs[0]}" y1="{yd}" x2="{xs[-1]}" y2="{yd}" stroke="rgba(45,49,66,0.35)" '
          f'stroke-width="0.9"/>')
    for x in xs:
        s += f'<circle cx="{x}" cy="{yd}" r="4.5" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>'
    s += mono(x0, yd + 30, "eight clauses", size=9, fill=SOFT, anchor="start", track="0.16em")

    s += mono(560, 236, "databases  ·  postgresql foundations, part 5", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "How a SELECT Is Evaluated:", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "Joins, Grouping and NULL", size=54, fill=ACCENT, family=SERIF, anchor="start")
    s += txt(560, 400, "the logical order of a query, clause by clause, and where NULL breaks it",
             size=15, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "FROM · WHERE · GROUP BY · HAVING · SELECT · ORDER BY · LIMIT · NULL", size=10,
              fill=MUTED, anchor="start", track="0.14em")
    s += mono(1116, 562, "canery", size=10, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    (HERE / "cover.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize((HERE / "cover.svg").resolve(), (HERE / "cover.png").resolve(), VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
