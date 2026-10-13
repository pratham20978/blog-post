#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important figure (Figure 2: row r2's tensors),
white-smoke paper, the tangerine used once. The motif is the shared patch, shaded by value
(high = bright), with three of row r2's tensors drawn over it as ellipses along their
eigenvectors, semi-axes proportional to the square roots of the eigenvalues: the step alone at
(r2, c4) as a flat line, the step with two ring pixels at (r2, c3) as a narrow ellipse, and the
window goodFeaturesToTrack returns, (r2, c2), as the rounder ellipse in tangerine.
1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import math
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)
from _figs import L1, L2, PATCH, PTS, TH

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-the-structure-tensor"


def build():
    assert PTS == [(2, 2)]
    s = ""
    cw, gx, gy = 76, 96, 112
    for i in range(5):
        for j in range(5):
            v = PATCH[i][j]
            x, y = gx + j * cw, gy + i * cw
            a = 0.88 * (1 - v / 255) + 0.02
            s += (f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" fill="{PAPER}"/>'
                  f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" fill="rgba(45,49,66,{a:.3f})" '
                  f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
    scale = 34 / math.sqrt(L1[2][4])        # the longest glyph spans 68 of a 76-px cell
    cy = gy + 2 * cw + cw / 2
    for c, colr in ((4, "#ffffff"), (3, "#ffffff"), (2, ACCENT)):
        cx = gx + c * cw + cw / 2
        a, b = scale * math.sqrt(L1[2][c]), scale * math.sqrt(L2[2][c])
        if b < 0.75:
            a -= 5                                  # the round caps add 5 px at each end
            s += (f'<line x1="{cx - a:.1f}" y1="{cy}" x2="{cx + a:.1f}" y2="{cy}" stroke="{INK}" '
                  f'stroke-width="10" stroke-linecap="round"/>'
                  f'<line x1="{cx - a:.1f}" y1="{cy}" x2="{cx + a:.1f}" y2="{cy}" stroke="{colr}" '
                  f'stroke-width="5.5" stroke-linecap="round"/>')
        else:
            fill = ACCENT if colr == ACCENT else "#ffffff"
            s += (f'<ellipse cx="{cx}" cy="{cy}" rx="{a:.1f}" ry="{b:.1f}" transform="rotate({TH[2][c]:.1f} {cx} {cy})" '
                  f'fill="{fill}" fill-opacity="{0.9 if colr == ACCENT else 0.92}" stroke="{INK}" stroke-width="3"/>')
    s += mono(gx + 2.5 * cw, gy - 18, "one matrix per window", size=11, fill=SOFT, track="0.1em")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 9", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "The Structure Tensor", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 348, "Harris, Shi–Tomasi, and optical flow", size=26, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 396, "one 2×2 matrix behind corners, orientation", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(560, 422, "and motion, worked by hand on a 5×5 patch", size=15, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="548" x2="1104" y2="548" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 574, "windows · eigenvalues · harris's k · shi–tomasi · förstner · orientation · lucas–kanade",
              size=10, fill=MUTED, anchor="start", track="0.14em")

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
