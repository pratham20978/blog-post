#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important figure (the four stages),
white-smoke paper, a single tangerine element. 1200 x 630.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SERIF, SANS, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    # motif: the four stages, reduced to bars — the first one carries the accent
    bar_y, bar_h, bar_w, gap, x0 = 396, 56, 232, 24, 84
    labels = ["SAMPLE", "FILTER", "TRANSFORM", "DECIDE"]
    for i, lab in enumerate(labels):
        x = x0 + i * (bar_w + gap)
        focal = i == 0
        s += (f'<rect x="{x}" y="{bar_y}" width="{bar_w}" height="{bar_h}" rx="6" '
              f'fill="{ACCENT_TINT if focal else "#ffffff"}" '
              f'stroke="{ACCENT if focal else INK}" stroke-width="1.2"/>')
        s += mono(x + bar_w / 2, bar_y + 34, lab, size=11,
                  fill=ACCENT if focal else INK, track="0.16em", weight="500")
        if i < 3:
            ax = x + bar_w
            s += (f'<line x1="{ax + 4}" y1="{bar_y + bar_h / 2}" x2="{ax + gap - 4}" '
                  f'y2="{bar_y + bar_h / 2}" stroke="{MUTED}" stroke-width="1"/>')

    # a single 3x3 stencil above the motif — the operation three stages share
    cw, gx, gy = 44, 84, 220
    weights = [["-1", "0", "1"], ["-2", "0", "2"], ["-1", "0", "1"]]
    for r in range(3):
        for c in range(3):
            s += (f'<rect x="{gx + c * cw}" y="{gy + r * cw}" width="{cw}" height="{cw}" '
                  f'fill="#ffffff" stroke="rgba(45,49,66,0.28)" stroke-width="0.8"/>')
            s += txt(gx + c * cw + cw / 2, gy + r * cw + cw / 2 + 4, weights[r][c],
                     size=12, fill=INK, family=MONO, weight="500")
    s += mono(gx, gy + 3 * cw + 22, "one weighted sum", size=9, fill=SOFT,
              anchor="start", track="0.14em")

    # title block
    s += mono(300, 236, "algorithms  ·  pillar", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(300, 300, "Image Processing", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(300, 356, "by Hand", size=54, fill=ACCENT, family=SERIF, anchor="start")

    s += (f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>')
    s += mono(84, 562, "sample · filter · transform · decide", size=10, fill=MUTED,
              anchor="start", track="0.14em")
    s += mono(1116, 562, "canery", size=10, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg,
                                    encoding="utf-8")
    (HERE / "cover.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / "cover.svg", HERE / "cover.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
