#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figures 1 and 2 in one line: the patch's frame of twelve
known pixels around nine unknowns, and, after the solve, the same frame with the nine pixels back,
255 at the impulse. The tangerine is the solve. Values come from _data.py. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, ACCENT, mono,
                    rasterize, svg_doc, txt)
import _data as d

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-gradient-domain-editing"


def blend(rgb, a, paper=(245, 245, 245)):
    r, g, b = (round(paper[i] * (1 - a) + rgb[i] * a) for i in range(3))
    return f"#{r:02x}{g:02x}{b:02x}"


def grey(v):
    t = max(0.0, min(1.0, v / 255))
    return blend((45, 49, 66), 0.88 * (1 - t) + 0.02)


def grid(x0, y0, cs, solved):
    s = ""
    for i in range(5):
        for j in range(5):
            x, y = x0 + j * cs, y0 + i * cs
            if (i, j) in ((0, 0), (0, 4), (4, 0), (4, 4)):
                s += f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="{blend((45, 49, 66), 0.05)}" stroke="rgba(45,49,66,0.25)" stroke-width="0.8"/>'
                continue
            inner = 1 <= i <= 3 and 1 <= j <= 3
            if inner and not solved:
                s += f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="#ffffff" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>'
                s += mono(x + cs / 2, y + cs / 2 + 5, "?", size=14, fill=SOFT, weight="500")
                continue
            v = d.PATCH[i][j]
            ink = "#ffffff" if v < 133 else INK
            s += (f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="{grey(v)}" '
                  f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
            s += mono(x + cs / 2, y + cs / 2 + 4, str(v), size=11, fill=ink, weight="500")
    s += (f'<rect x="{x0 + cs}" y="{y0 + cs}" width="{3 * cs}" height="{3 * cs}" fill="none" '
          f'stroke="{LINK}" stroke-width="2.4"/>')
    s += (f'<rect x="{x0}" y="{y0}" width="{5 * cs}" height="{5 * cs}" fill="none" '
          f'stroke="rgba(45,49,66,0.55)" stroke-width="1"/>')
    return s


def build():
    assert d.solve_exact(d.A, d.B) == d.XSTAR and d.XSTAR[3] == 255
    cs = 40
    xa, xb, y0 = 96, 404, 150
    s = ""
    s += grid(xa, y0, cs, solved=False)
    s += grid(xb, y0, cs, solved=True)
    ay = y0 + 2.5 * cs
    s += (f'<line x1="{xa + 5 * cs + 16}" y1="{ay}" x2="{xb - 18}" y2="{ay}" stroke="{ACCENT}" '
          f'stroke-width="3" stroke-linecap="round"/>')
    s += (f'<polygon points="{xb - 16},{ay - 7} {xb - 4},{ay} {xb - 16},{ay + 7}" fill="{ACCENT}"/>')
    s += mono((xa + 5 * cs + xb) / 2, ay - 16, "solve", size=12, fill=MUTED, weight="500")
    s += mono(xa, y0 - 16, "12 known · 9 unknown", size=11, fill=SOFT, anchor="start")
    s += mono(xb, y0 - 16, "the 9 pixels, back", size=11, fill=SOFT, anchor="start")
    s += mono(xa, y0 + 5 * cs + 34, "∇²f = div v inside, f fixed on the frame", size=12, fill=MUTED,
              anchor="start", weight="500")

    s += mono(700, 214, "algorithms  ·  image processing by hand, part 14", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(700, 282, "Gradient-Domain", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(700, 336, "Editing", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(700, 384, "Poisson Cloning, HDR and Tiling", size=30, fill=INK, family=SERIF, anchor="start")
    s += txt(700, 432, "keep an image's gradients and its border,", size=17, fill=MUTED, family=SANS,
             anchor="start")
    s += txt(700, 458, "and the pixels come back: worked by hand", size=17, fill=MUTED, family=SANS,
             anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "Poisson equation · seamlessClone · Gauss–Seidel · multigrid · HDR · seamless tiling",
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
