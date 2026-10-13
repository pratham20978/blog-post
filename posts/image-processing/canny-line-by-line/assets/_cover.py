#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important figure (Figure 3: hysteresis on
the smoothed patch), white-smoke paper, the tangerine used once, on a seed. The motif is
the shared patch after the series' 3×3 Gaussian, shaded by value (high = bright), with
the chain that hysteresis keeps at 450 and 180 drawn down column c3 as linked dots — the
top one, a seed, in tangerine; the other seed, at the bottom, larger in ink — and the two
ring pixels that survive suppression but have no seed drawn hollow and unlinked.
1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)
from _figs import COL, SKEEP2, SM, SM2, hysteresis

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-canny-line-by-line"


def build():
    out = hysteresis(SKEEP2, SM2, 180, 450)
    assert out == COL
    dropped = sorted(SKEEP2 - out)
    assert dropped == [(1, 0), (3, 0)]
    s = ""
    cw, gx, gy = 64, 96, 150
    for i in range(5):
        for j in range(5):
            v = SM[i][j]
            x, y = gx + j * cw, gy + i * cw
            a = 0.88 * (1 - v / 255) + 0.02
            s += (f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" fill="{PAPER}"/>'
                  f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" fill="rgba(45,49,66,{a:.3f})" '
                  f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
    cx = gx + 3 * cw + cw / 2
    ys = [gy + i * cw + cw / 2 for i in range(5)]
    s += (f'<line x1="{cx}" y1="{ys[0]}" x2="{cx}" y2="{ys[4]}" stroke="{INK}" stroke-width="5" '
          f'stroke-linecap="round"/>')
    for i, y in enumerate(ys):
        if i == 0:
            s += f'<circle cx="{cx}" cy="{y}" r="15" fill="{ACCENT}" stroke="{PAPER}" stroke-width="3"/>'
        elif SM2[i][3] > 450:
            s += f'<circle cx="{cx}" cy="{y}" r="15" fill="{INK}" stroke="{PAPER}" stroke-width="3"/>'
        else:
            s += f'<circle cx="{cx}" cy="{y}" r="9" fill="{INK}" stroke="{PAPER}" stroke-width="3"/>'
    for (i, j) in dropped:
        x, y = gx + j * cw + cw / 2, gy + i * cw + cw / 2
        s += (f'<circle cx="{x}" cy="{y}" r="9" fill="none" stroke="#ffffff" stroke-width="2" '
              f'stroke-dasharray="3,3"/>')
    s += mono(gx + 2.5 * cw, gy - 18, "chains, not pixels", size=11, fill=SOFT, track="0.1em")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 8", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Canny Edge Detection,", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "Line by Line", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 404, "what the two thresholds actually select,", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(560, 430, "and how to set them from the noise", size=15, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="548" x2="1104" y2="548" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 574, "gradient · suppression · ties · hysteresis · threshold units · thresholds from noise",
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
