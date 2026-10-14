#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif at
the optical centre, a Geist Mono category label above it, one simplified motif taken from the post's
figures, white-smoke paper, the tangerine used once. The motif is Figure 6's equal-hump histogram cut
once in tangerine at Otsu's threshold, beside Figure 4's last step: the patch's 5×5 relief flooded from
two markers into two regions (blue and warm grey; the tangerine is kept for the cut). Values come from
_data.py. 1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, ACCENT, mono,
                    rasterize, svg_doc, txt)
import _data as d

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-thresholding-and-segmentation"


def blend(rgb, a, paper=(245, 245, 245)):
    r, g, b = (round(a * c + (1 - a) * p) for c, p in zip(rgb, paper))
    return f"#{r:02x}{g:02x}{b:02x}"


def build():
    sh = d.SHAPES["equal"]
    assert (sh["otsu"], d.WS_HAND[0]) == (120, [1, 1, 1, 2, 2])
    s = ""
    # the histogram, cut once
    x0, y0, w, h = 70, 112, 420, 160
    hmax = max(sh["h"])
    pts = [(x0 + w * v / 255, y0 + h - h * sh["h"][v] / hmax * 0.92) for v in range(256)]
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in [(x0, y0 + h)] + pts + [(x0 + w, y0 + h)])
    s += f'<polygon points="{poly}" fill="{INK}" fill-opacity="0.78"/>'
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{MUTED}" stroke-width="1.2"/>'
    xc = x0 + w * (sh["otsu"] + 0.5) / 255
    s += f'<line x1="{xc:.1f}" y1="{y0 - 16}" x2="{xc:.1f}" y2="{y0 + h + 8}" stroke="{ACCENT}" stroke-width="4"/>'
    s += mono(x0, y0 + h + 30, "one histogram, one cut", size=11, fill=SOFT, anchor="start", track="0.06em")
    # the flooded grid
    cs, gx, gy = 32, 70, 340
    fills = {1: blend((46, 90, 168), 0.42), 2: blend((122, 131, 153), 0.30)}
    for i in range(5):
        for j in range(5):
            s += (f'<rect x="{gx + j * cs}" y="{gy + i * cs}" width="{cs}" height="{cs}" '
                  f'fill="{fills[d.WS_HAND[i][j]]}" stroke="rgba(45,49,66,0.35)" stroke-width="1"/>')
    for (i, j) in ((0, 0), (2, 4)):
        s += (f'<rect x="{gx + j * cs + 3}" y="{gy + i * cs + 3}" width="{cs - 6}" height="{cs - 6}" fill="none" '
              f'stroke="{INK}" stroke-width="2.4"/>')
    s += mono(gx + 5 * cs + 22, gy + 2.5 * cs - 6, "two markers,", size=11, fill=SOFT, anchor="start", track="0.06em")
    s += mono(gx + 5 * cs + 22, gy + 2.5 * cs + 12, "two regions", size=11, fill=SOFT, anchor="start", track="0.06em")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 11", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Thresholding and Segmentation", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 348, "Otsu, Sauvola, Watershed", size=26, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 396, "when one number can split an image, and what to do", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(560, 422, "when it cannot, worked by hand on a 5×5 patch", size=15, fill=MUTED, family=SANS,
             anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "histogram · otsu · 2-means · local thresholds · watershed · markers",
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
