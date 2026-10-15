#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 8's first chord: the sRGB encode curve, the chord
between codes 40 and 200, and the gap between the chord's 120 and the curve's 148.7, which is the cost
of averaging codes instead of light. The cover keeps the locked five-colour palette, so the post's
colour swatches stay in the figures and on the social cards. Values come from _data.py. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (FONTS, INK, MUTED, PAPER, RULE, RULE_SOLID, SANS, SERIF, SOFT, ACCENT, mono,
                    rasterize, svg_doc, txt)
import _data as d

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-colour-and-gamma"


def build():
    assert d.MID_CODES == 120 and f"{d.enc8(d.MID_LIGHT):.1f}" == "148.7"
    x0, y0, w, h = 96, 96, 400, 352            # the plot: light 0..1 across, code 0..255 up
    X = lambda L: x0 + L * w
    Y = lambda c: y0 + h - c / 255 * h
    s = ""
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1.2"/>'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1.2"/>'
    pts = " ".join(f"{X(i / 300):.1f},{Y(d.enc8(i / 300)):.1f}" for i in range(301))
    s += f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="2.6" stroke-linejoin="round"/>'
    La, Lb, xm = d.LIN[40], d.LIN[200], d.MID_LIGHT
    s += (f'<line x1="{X(La):.1f}" y1="{Y(40):.1f}" x2="{X(Lb):.1f}" y2="{Y(200):.1f}" stroke="{MUTED}" '
          f'stroke-width="1.8"/>')
    for L, c in ((La, 40), (Lb, 200)):
        s += f'<circle cx="{X(L):.1f}" cy="{Y(c):.1f}" r="4.5" fill="{MUTED}"/>'
    # the one accent: the gap between the chord's midpoint and the curve
    s += (f'<line x1="{X(xm):.1f}" y1="{Y(d.MID_CODES):.1f}" x2="{X(xm):.1f}" y2="{Y(d.enc8(xm)):.1f}" '
          f'stroke="{ACCENT}" stroke-width="4" stroke-linecap="round"/>')
    s += f'<circle cx="{X(xm):.1f}" cy="{Y(d.MID_CODES):.1f}" r="5.5" fill="{ACCENT}"/>'
    s += f'<circle cx="{X(xm):.1f}" cy="{Y(d.enc8(xm)):.1f}" r="5.5" fill="{ACCENT}"/>'
    s += mono(X(xm) + 12, Y(d.MID_CODES) + 18, "120", size=13, fill=MUTED, anchor="start", weight="600")
    s += mono(X(xm) - 12, Y(d.enc8(xm)) - 10, "148.7", size=13, fill=INK, anchor="end", weight="600")
    s += mono(X(La) + 10, Y(40) + 18, "code 40", size=11, fill=SOFT, anchor="start")
    s += mono(X(Lb) + 10, Y(200) + 18, "code 200", size=11, fill=SOFT, anchor="start")
    s += mono(x0 + w, y0 + h + 22, "linear light", size=11, fill=SOFT, anchor="end", track="0.06em")
    s += mono(x0, y0 - 12, "sRGB code", size=11, fill=SOFT, anchor="start", track="0.06em")
    s += mono(x0, y0 + h + 50, "average the codes: 120 · average the light: 148.7", size=11, fill=SOFT,
              anchor="start", track="0.04em")

    s += mono(580, 214, "algorithms  ·  image processing by hand, part 13", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(580, 282, "Colour and Gamma", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(580, 330, "Luma, Luminance and", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(580, 368, "the Spaces in Between", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(580, 420, "an 8-bit pixel is a code, not light, and BGR2GRAY", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(580, 446, "returns luma, not luminance: worked by hand", size=17, fill=MUTED, family=SANS,
             anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "sRGB · linear light · luma · luminance · CIE XYZ · CIELAB · BT.601 · BT.709",
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
