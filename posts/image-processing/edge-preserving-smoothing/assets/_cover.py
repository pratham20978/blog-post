#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important figure (Figure 1: the bilateral
filter's weights), white-smoke paper, the tangerine used once, on the impulse. The motif
is the shared patch with a dot in each cell of the 3×3 window around (r2, c2), its area
proportional to the bilateral weight that cell gets (σr = 80): large on the dark side,
nearly nothing across the edge and on the bright pixel. 1200 x 630. The cover carries no
brand lockup; the social cards do.
"""
import math
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)
from _figs import PATCH, W2, at, rw

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-edge-preserving-smoothing"


def build():
    s = ""
    cw, gx, gy = 64, 96, 150
    for i in range(5):
        for j in range(5):
            v = PATCH[i][j]
            x, y = gx + j * cw, gy + i * cw
            if (i, j) == (2, 1):
                s += (f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" fill="{ACCENT}" fill-opacity="0.88" '
                      f'stroke="{ACCENT}" stroke-width="1.8"/>')
                continue
            a = 0.88 * (1 - v / 255) + 0.02
            s += (f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" fill="{PAPER}"/>'
                  f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" fill="rgba(45,49,66,{a:.3f})" '
                  f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
    # the bilateral weights around (r2, c2): dot area proportional to weight
    ci, cj = 2, 2
    for (di, dj), ws in W2.items():
        w = ws * rw(at(PATCH, ci + di, cj + dj) - PATCH[ci][cj], 80)
        r = 26 * math.sqrt(w / W2[(0, 0)])
        cx, cy = gx + (cj + dj) * cw + cw / 2, gy + (ci + di) * cw + cw / 2
        bright = at(PATCH, ci + di, cj + dj) > 120
        col = INK if bright else "#ffffff"
        if (di, dj) == (0, -1):
            col = "#ffffff"
        s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{max(r, 1.6):.1f}" fill="{col}" fill-opacity="0.92"/>'
    s += (f'<rect x="{gx + cw}" y="{gy + cw}" width="{3 * cw}" height="{3 * cw}" fill="none" '
          f'stroke="{INK}" stroke-width="1.6" stroke-dasharray="6,4"/>')
    s += mono(gx + 2.5 * cw, gy - 18, "who counts as alike", size=11, fill=SOFT, track="0.1em")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 7", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Edge-Preserving", size=56, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 358, "Smoothing", size=56, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 404, "average only the neighbours that are alike", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(560, 430, "and find out what “alike” lets through", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="96" y1="548" x2="1104" y2="548" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 574, "bilateral · non-local means · perona–malik · the impulse problem · tooling map", size=10,
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
