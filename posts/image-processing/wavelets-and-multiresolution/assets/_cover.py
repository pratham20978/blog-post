#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important figure (Figure 4: the padded patch's
one Haar level as four 3x3 subbands, the impulse's four coefficients lit, set against
Part 5's 25 equal DFT bins), white-smoke paper, the tangerine used once, on the impulse.
1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-wavelets-and-multiresolution"


def build():
    s = ""
    cw, gx, gy, gap = 44, 96, 132, 14
    tints = ["rgba(45,49,66,0.62)", "rgba(45,49,66,0.10)", "rgba(45,49,66,0.10)", "rgba(45,49,66,0.10)"]
    for q, (qx, qy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
        ox = gx + qx * (3 * cw + gap)
        oy = gy + qy * (3 * cw + gap)
        for i in range(3):
            for j in range(3):
                hit = (i, j) == (1, 0)
                fill = "rgba(235,108,54,0.85)" if hit else tints[q]
                stroke = ACCENT if hit else "rgba(45,49,66,0.30)"
                s += (f'<rect x="{ox + j * cw}" y="{oy + i * cw}" width="{cw}" height="{cw}" fill="{PAPER}"/>'
                      f'<rect x="{ox + j * cw}" y="{oy + i * cw}" width="{cw}" height="{cw}" '
                      f'fill="{fill}" stroke="{stroke}" stroke-width="{1.8 if hit else 0.8}"/>')
    s += mono(gx + 3 * cw + gap / 2, gy - 18, "one level, four subbands", size=11, fill=SOFT,
              track="0.1em")
    by = gy + 6 * cw + 2 * gap + 34
    bw = (6 * cw + gap) / 25
    for k in range(25):
        s += (f'<rect x="{gx + k * bw:.1f}" y="{by}" width="{bw:.1f}" height="16" '
              f'fill="rgba(45,49,66,0.28)" stroke="{PAPER}" stroke-width="1"/>')
    s += mono(gx + 3 * cw + gap / 2, by + 36, "vs. 25 equal fourier bins", size=10, fill=SOFT,
              track="0.06em")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 6", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Wavelets and", size=56, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 358, "Multiresolution", size=56, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 404, "how much of a wave, and where", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(560, 430, "one level by hand, by lifting, in integers", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="96" y1="548" x2="1104" y2="548" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 574, "haar · 5/3 lifting · jpeg 2000 · shift variance · thresholding", size=10,
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
