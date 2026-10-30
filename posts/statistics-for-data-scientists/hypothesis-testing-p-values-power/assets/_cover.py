#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 1 reduced to its argument: the distribution of
replicated estimates from the 2013 design if the true effect is the plausible 2 points, cut by the
significance bar at ±15.88; only its far tails are significant, the right-sign tail in tangerine (the one
use) and the wrong-sign tail in slate. Values come from the lab's capture. 1200 x 630. The cover carries
no brand lockup; the social cards do.
"""
import json
import math
import pathlib

from _build import (ACCENT, FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize,
                    svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-hypothesis-testing-p-values-power"


def build():
    rd = CAP["retrodesign"]
    du, dc = rd["durante"], rd["cases"]["durante_2"]
    A, se, crit = dc["A"], dc["s"], du["critical"]
    assert (A, se) == (2.0, 8.1) and round(crit, 2) == 15.88 and round(dc["exact"]["exaggeration"], 2) == 9.54
    pdf = lambda x: math.exp(-0.5 * ((x - A) / se) ** 2) / (se * math.sqrt(2 * math.pi))
    x0, x1, top, base = 90, 570, 190, 470                        # estimate from -36 to 36 points, density 0 to 0.052
    ex = lambda v: x0 + (v + 36) / 72 * (x1 - x0)
    ey = lambda v: base - v / 0.052 * (base - top)
    xs = [-36 + 72 * i / 720 for i in range(721)]
    right = [x for x in xs if x >= crit]
    left = [x for x in xs if x <= -crit]
    poly = lambda seg, a, b: " ".join(f"{p:.1f},{q:.1f}" for p, q in [(ex(a), ey(0))] + [(ex(x), ey(pdf(x))) for x in seg] + [(ex(b), ey(0))])
    s = f'<polygon points="{poly(right, crit, right[-1])}" fill="{ACCENT}" fill-opacity="0.85" stroke="none"/>'
    s += f'<polygon points="{poly(left, left[0], -crit)}" fill="{LINK}" fill-opacity="0.55" stroke="none"/>'
    s += (f'<polyline points="{" ".join(f"{ex(x):.1f},{ey(pdf(x)):.1f}" for x in xs)}" fill="none" stroke="{INK}" '
          f'stroke-width="3" stroke-linejoin="round"/>')
    s += f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    for v in (crit, -crit):
        s += (f'<line x1="{ex(v):.1f}" y1="{top + 20}" x2="{ex(v):.1f}" y2="{base}" stroke="{MUTED}" stroke-width="1.4" '
              f'stroke-dasharray="6,5"/>')
    s += mono(ex(crit), top + 8, f"+{crit:.1f}", size=13, fill=MUTED)
    s += mono(ex(-crit), top + 8, f"−{crit:.1f}", size=13, fill=MUTED)
    s += mono(ex(A), base + 24, "true effect 2", size=13, fill=SOFT)
    s += mono(x0 - 10, 132, "replications of a 2013 design · SE 8.1 points", size=13, fill=SOFT, anchor="start")
    s += mono(ex(27), ey(0.012), f"{dc['exact']['exaggeration']:.1f}× too big", size=13, fill=ACCENT, weight="600")
    s += mono(ex(-26), ey(0.012), f"{100 * dc['exact']['typeS']:.0f}% wrong sign", size=13, fill=LINK, weight="600")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 5", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "p-Values and Power", size=56, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "How Wrong Can a", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 382, "Significant Result Be?", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 430, "a p-value assumes no effect; in a low-powered study", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 456, "only exaggerated estimates clear the bar", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "p as a random variable · power · type S and M errors · replication · false positive risk · TOST · peeking",
              size=10, fill=MUTED, anchor="start", track="0.12em")

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
