#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif from the post's most important idea, white-smoke paper, a single
tangerine element. 1200 x 630. Same layout grid as parts 1-3 (title block at x=560,
motif on the left). Part 4's motif: two small grids of tiles, the two relations, joined by
a thin line; one row of the right grid appears twice, in tangerine, the duplicate; four dots
beneath them, the four stages a query passes through.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MUTED, PAPER, RULE, SERIF, SANS,
                    SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def grid(x0, y0, cols, rows, t=16, g=5, hot_rows=()):
    s = ""
    for r in range(rows):
        hot = r in hot_rows
        for c in range(cols):
            x, y = x0 + c * (t + g), y0 + r * (t + g)
            s += (f'<rect x="{x}" y="{y}" width="{t}" height="{t}" rx="3" '
                  f'fill="{ACCENT_TINT if hot else "#ffffff"}" '
                  f'stroke="{ACCENT if hot else "rgba(45,49,66,0.30)"}" '
                  f'stroke-width="{1.4 if hot else 0.8}"/>')
    return s


def build():
    s = ""
    t, g = 16, 5
    y0 = 250
    cx0 = 96                       # customers: degree 3
    ox0 = cx0 + 3 * t + 2 * g + 92  # orders: degree 5
    s += mono(cx0, y0 - 24, "two relations", size=9, fill=SOFT, anchor="start", track="0.16em")
    s += grid(cx0, y0, 3, 6)
    s += grid(ox0, y0, 5, 6, hot_rows=(2, 3))
    # the join: orders.customer_id (column 1 of the doubled row) to customers.id (column 0)
    jy = y0 + 2 * (t + g) + t / 2
    ty = y0 + 4 * (t + g) + t / 2
    sx = ox0 - 6
    ex = cx0 + 3 * t + 2 * g + 6
    mx = (sx + ex) / 2
    s += (f'<path d="M {sx} {jy} H {mx + 6} Q {mx} {jy} {mx} {jy + 6} V {ty - 6} '
          f'Q {mx} {ty} {mx - 6} {ty} H {ex}" fill="none" stroke="{MUTED}" stroke-width="0.9"/>')
    s += f'<circle cx="{sx}" cy="{jy}" r="2" fill="{MUTED}"/><circle cx="{ex}" cy="{ty}" r="2" fill="{MUTED}"/>'
    # four stages beneath
    yl = y0 + 6 * (t + g) + 44
    xs = [cx0 + 8 + k * 86 for k in range(4)]
    s += f'<line x1="{xs[0]}" y1="{yl}" x2="{xs[-1]}" y2="{yl}" stroke="rgba(45,49,66,0.35)" stroke-width="0.9"/>'
    for x in xs:
        s += f'<circle cx="{x}" cy="{yl}" r="4.5" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>'
    s += mono(cx0, yl + 30, "four stages", size=9, fill=SOFT, anchor="start", track="0.16em")

    s += mono(560, 236, "databases  ·  postgresql foundations, part 4", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "What a Relational", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "Database Actually Does", size=54, fill=ACCENT, family=SERIF, anchor="start")
    s += txt(560, 400, "relations, the four stages of a query, and two silent bugs", size=15,
             fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "relations · keys · system catalog · parser · planner · executor · NULL", size=10,
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
