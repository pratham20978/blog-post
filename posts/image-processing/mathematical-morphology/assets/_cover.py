#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif at
the optical centre, a Geist Mono category label above it, one simplified motif taken from the post's
figures, white-smoke paper, the tangerine used once. The motif is Figure 2's first step: the patch's
mask opened by the cross, the speck (in tangerine, the one accent) falling through while the bar stays,
with the adjunction law set beneath it. Values come from _data.py. 1200 x 630. The cover carries no
brand lockup; the social cards do.
"""
import pathlib

from _build import (FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, ACCENT, mono,
                    rasterize, svg_doc, txt)
import _data as d

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-mathematical-morphology"
WHITE, DARK = "#ffffff", "#555866"          # DARK = ink at 0.80 over the paper, as in the figures
ELEM2 = "#7a95c5"                           # the figures' element blue


def grid(x0, y0, cs, S, accent=frozenset()):
    s = ""
    for i in range(5):
        for j in range(5):
            f = ACCENT if (i, j) in accent else (WHITE if (i, j) in S else DARK)
            s += (f'<rect x="{x0 + j * cs}" y="{y0 + i * cs}" width="{cs}" height="{cs}" fill="{f}" '
                  f'stroke="rgba(45,49,66,0.35)" stroke-width="1" shape-rendering="crispEdges"/>')
    s += (f'<rect x="{x0}" y="{y0}" width="{5 * cs}" height="{5 * cs}" fill="none" '
          f'stroke="rgba(45,49,66,0.6)" stroke-width="1.2"/>')
    return s


def build():
    assert len(d.X) == 11 and d.O1 == d.BAR and d.SPECK == {(2, 1)}
    s = ""
    cs, gy = 30, 120
    # the mask, its speck in tangerine
    s += grid(70, gy, cs, d.X, accent=d.SPECK)
    # the cross between them, over an arrow
    ax0, ax1, ay = 70 + 5 * cs + 22, 330 - 22, gy + 2.5 * cs
    s += f'<line x1="{ax0}" y1="{ay}" x2="{ax1 - 8}" y2="{ay}" stroke="{MUTED}" stroke-width="1.6"/>'
    s += f'<polygon points="{ax1},{ay} {ax1 - 10},{ay - 5} {ax1 - 10},{ay + 5}" fill="{MUTED}"/>'
    c, ex, ey = 14, (ax0 + ax1) / 2 - 21, ay - 62
    for a, b in d.CROSS:
        s += (f'<rect x="{ex + (b + 1) * c}" y="{ey + (a + 1) * c}" width="{c}" height="{c}" fill="{ELEM2}" '
              f'stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>')
    # the opening: the bar alone
    s += grid(330, gy, cs, d.O1)
    s += mono(70, gy + 5 * cs + 34, "open by the cross: the speck falls through, the bar stays",
              size=11, fill=SOFT, anchor="start", track="0.04em")
    # the law beneath
    s += mono(70, 400, "δ(A) ⊆ Y", size=24, fill=INK, anchor="start", weight="500")
    s += mono(70, 436, "exactly when", size=13, fill=SOFT, anchor="start", track="0.08em")
    s += mono(70, 474, "A ⊆ ε(Y)", size=24, fill=INK, anchor="start", weight="500")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 12", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Mathematical Morphology", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 350, "as Lattice Algebra", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 404, "erosion and dilation are adjoint, and every law of", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(560, 430, "opening, closing and sieving follows, worked by hand", size=15, fill=MUTED, family=SANS,
             anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "erosion · dilation · opening · closing · top-hat · granulometry · reconstruction",
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
