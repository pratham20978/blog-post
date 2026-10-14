#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif,
a Geist Mono category label above it, one simplified motif taken from the post's main figure, on
white-smoke paper with the tangerine used once. The motif is Figure 1: the scan's cumulative line
and the sort-then-search line crossing, the crossing point in tangerine, above the 16 sorted keys.
Values come from _data.py. 1200 x 630. The cover carries no brand lockup; the social cards do.
Structure copied from image-processing part 11's _cover.py.
"""
import pathlib

from _build import (FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, ACCENT, mono,
                    rasterize, svg_doc, txt)
import _data as d

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-when-a-search-structure-pays-for-itself"


def build():
    assert (d.SORT_WORST, round(d.Q_WORST, 2)) == (49, 9.56)
    s = ""
    # the two bills: scan against sort-then-search, q = 0..20 lookups
    x0, y0, w, h = 80, 96, 400, 260
    X = lambda q: x0 + w * q / 20
    Y = lambda v: y0 + h - h * v / 180
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += (f'<line x1="{X(0)}" y1="{Y(0)}" x2="{X(20)}" y2="{Y(20 * d.SCAN_HIT):.1f}" stroke="{INK}" '
          f'stroke-width="3"/>')
    s += (f'<line x1="{X(0)}" y1="{Y(d.SORT_WORST):.1f}" x2="{X(20)}" y2="{Y(d.SORT_WORST + 20 * d.BIN_HIT):.1f}" '
          f'stroke="{MUTED}" stroke-width="3"/>')
    xq, yq = X(d.Q_WORST), Y(d.SCAN_HIT * d.Q_WORST)
    s += f'<circle cx="{xq:.1f}" cy="{yq:.1f}" r="8" fill="{ACCENT}" stroke="{PAPER}" stroke-width="2"/>'
    s += mono(X(15) - 10, Y(15 * d.SCAN_HIT) - 14, "scan", size=12, fill=INK, anchor="end", weight="500")
    s += mono(X(20), Y(d.SORT_WORST + 20 * d.BIN_HIT) + 52, "sort, then search", size=12, fill=MUTED,
              anchor="end", weight="500")
    s += mono(x0, y0 + h + 30, "repaid after 9.56 lookups", size=11, fill=SOFT, anchor="start", track="0.06em")
    # the 16 keys, sorted
    cw, ch, ax0, ay0 = 25, 30, 80, 430
    for i, k in enumerate(d.KEYS):
        s += (f'<rect x="{ax0 + i * cw}" y="{ay0}" width="{cw}" height="{ch}" fill="#ffffff" '
              f'stroke="rgba(45,49,66,0.35)" stroke-width="1"/>')
        s += mono(ax0 + i * cw + cw / 2, ay0 + 19, str(k), size=10, fill=INK, weight="500")
    s += mono(ax0, ay0 + ch + 26, "16 keys, sorted once", size=11, fill=SOFT, anchor="start", track="0.06em")

    s += mono(560, 228, "algorithms  ·  search algorithms, part 2", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 290, "Hash Map, Sorted Array or Tree?", size=40, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 336, "When Each Pays for Itself", size=28, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 386, "how many lookups repay a sort, how many writes a", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(560, 412, "sorted structure absorbs, and what a hash cannot answer", size=17, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "break-even · binary search · red-black tree · hash map · hash flooding",
              size=10, fill=MUTED, anchor="start", track="0.14em")

    svg = svg_doc(VW, VH, s)
    (HERE / f"{STEM}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    (HERE / f"{STEM}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / f"{STEM}.svg", HERE / f"{STEM}.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
