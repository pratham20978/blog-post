#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif at
the optical centre, a Geist Mono category label above it, one simplified motif taken from the
post's most important figure (Figure 1: the octave), white-smoke paper, the tangerine used once.
The motif is three DoG levels of the patch enlarged seven times (σ 2.016, 2.540, 3.200), stacked
along σ, with the one sample that beats all 26 neighbours ringed in tangerine on the middle level.
Values are the closed form from _data.py, blue below zero, warm grey above (the tangerine is kept
for the point). 1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)
import _data as d

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-scale-space-and-sift"


def blend(rgb, a, paper=(245, 245, 245)):
    r, g, b = (round(a * c + (1 - a) * p) for c, p in zip(rgb, paper))
    return f"#{r:02x}{g:02x}{b:02x}"


def fill(v, vmax=36.0):
    t = min(1.0, abs(v) / vmax)
    return blend((46, 90, 168) if v < 0 else (122, 131, 153), 0.04 + 0.86 * t)


def level(x0, y0, cs, M):
    s = f'<rect x="{x0}" y="{y0}" width="{cs * 35}" height="{cs * 35}" fill="{PAPER}"/>'
    for i, row in enumerate(M):
        j = 0
        while j < 35:
            f = fill(row[j])
            k = j + 1
            while k < 35 and fill(row[k]) == f:
                k += 1
            s += (f'<rect x="{x0 + j * cs:.1f}" y="{y0 + i * cs:.1f}" width="{(k - j) * cs + 0.4:.1f}" '
                  f'height="{cs + 0.4:.1f}" fill="{f}" shape-rendering="crispEdges"/>')
            j = k
    s += (f'<rect x="{x0}" y="{y0}" width="{cs * 35}" height="{cs * 35}" fill="none" '
          f'stroke="rgba(45,49,66,0.55)" stroke-width="1.2"/>')
    return s


def build():
    assert [(c[0], c[1], c[2]) for c in d.CANDS] == [(2, 10, 17), (2, 17, 17)]
    s = ""
    cs = 6.4
    shear, flat = 0.62, 0.40                    # oblique view: each level a flattened plane
    tx, gap = 70, 116
    top = 150
    planes = [(3, top), (2, top + gap), (1, top + 2 * gap)]          # coarsest at the top
    for lv, ty in planes:
        g = f'<g transform="matrix(1 0 {shear} {flat} {tx} {ty})">' + level(0, 0, cs, d.D7[lv]) + "</g>"
        s += g
        xr = tx + 35 * cs + shear * 35 * cs * flat / flat * 0 + 35 * cs * shear
        s += mono(tx + 35 * cs * (1 + shear) + 14, ty + 35 * cs * flat / 2 + 4, f"σ {d.SIG[lv]:.3f}", size=11,
                  fill=SOFT, anchor="start")
    # the sample that beats its 26 neighbours, on the middle plane
    xm, ym = (d.CX + 0.5) * cs, (d.CY + 0.5) * cs
    mx, my = tx + xm + shear * ym, planes[1][1] + flat * ym
    s += (f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="13" ry="7.5" fill="none" stroke="{INK}" stroke-width="6"/>'
          f'<ellipse cx="{mx:.1f}" cy="{my:.1f}" rx="13" ry="7.5" fill="none" stroke="{ACCENT}" stroke-width="3.5"/>')
    ax = tx - 26
    s += (f'<line x1="{ax}" y1="{top + 2 * gap + 60}" x2="{ax}" y2="{top - 6}" stroke="{MUTED}" stroke-width="1.2" '
          f'marker-end="url(#arrow)"/>')
    s += mono(ax, top - 16, "σ", size=13, fill=MUTED)
    s += mono(tx, top + 2 * gap + 35 * cs * flat + 40, "three levels of one octave, searched in x, y and σ", size=11,
              fill=SOFT, anchor="start", track="0.06em")

    s += mono(560, 236, "algorithms  ·  image processing by hand, part 10", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Scale Space and SIFT", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 348, "Why σ is a search dimension", size=26, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 396, "one octave of differences of Gaussians,", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(560, 422, "worked by hand on a 5×5 patch enlarged seven times", size=15, fill=MUTED, family=SANS,
             anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "scale space · normalised laplacian · 26 neighbours · the fit · the edge test · why the gaussian",
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
