#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important figure (the patch's centred
spectrum: one bright row through DC over a flat floor, shaded log10(1 + |F|) exactly as
Figure 2 shades it), white-smoke paper, a single tangerine element on DC. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import math
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)
from _figs import FA, shift_order

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-the-2d-dft-spectra-phase-filtering"


def build():
    s = ""
    cw, gx, gy = 66, 96, 150
    order = shift_order(5)
    lmax = math.log10(1 + 2815)
    for i, kr in enumerate(order):
        for j, kc in enumerate(order):
            m = abs(FA[kr][kc])
            t = math.log10(1 + m) / lmax
            dc = i == 2 and j == 2
            a = 0.88 * (1 - t) + 0.02
            fill = "rgba(235,108,54,0.12)" if dc else f"rgba(45,49,66,{a:.3f})"
            stroke = ACCENT if dc else "rgba(45,49,66,0.30)"
            s += (f'<rect x="{gx + j * cw}" y="{gy + i * cw}" width="{cw}" height="{cw}" fill="{PAPER}"/>'
                  f'<rect x="{gx + j * cw}" y="{gy + i * cw}" width="{cw}" height="{cw}" '
                  f'fill="{fill}" stroke="{stroke}" stroke-width="{2.2 if dc else 0.8}"/>')
    s += mono(gx + 2.5 * cw, gy - 18, "|F|, centred", size=11, fill=SOFT, track="0.1em")
    s += mono(gx + 2.5 * cw, gy + 5 * cw + 30, "the edge's row, the impulse's floor", size=10,
              fill=SOFT, track="0.06em")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 5", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "The 2-D DFT", size=58, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 350, "what a spectrum shows, what phase holds", size=17, fill=MUTED,
             family=SANS, anchor="start")
    s += txt(560, 376, "and when filtering there beats filtering in space", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="96" y1="536" x2="1104" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 562, "fftshift · phase swap · notch filter · fft crossover · phase correlation", size=10,
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
