#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 2's n = 30 panel reduced to its argument: means of
30 customers' spend in standard errors as bars, the normal curve the CLT promises dashed in slate, and the
true mean as the one tangerine line, with most of the bars to its left. Values come from the lab's capture.
1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import math
import pathlib

from _build import (ACCENT, FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize,
                    svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-sampling-distribution-central-limit-theorem"


def build():
    r = CAP["sampling"]["by_n"]["30"]
    edges, counts, reps = r["hist_z_edges"], r["hist_z_counts"], r["R"]
    below = r["p_mean_below_mu"]["p"]
    assert round(100 * below, 1) == 71.8 and round(100 * r["lower"]["p"], 1) == 39.8
    x0, x1, base, top = 110, 560, 470, 170                       # plot box: z from -2 to 5
    zx = lambda z: x0 + (z + 2) / 7 * (x1 - x0)
    dens = [c / (reps * (edges[i + 1] - edges[i])) for i, c in enumerate(counts)]
    lo, hi = edges.index(-2.0), edges.index(5.0)
    ymax = max(dens[lo:hi]) * 1.08
    yy = lambda d: base - d / ymax * (base - top)
    s = ""
    for i in range(lo, hi):
        if dens[i] > 0:
            s += (f'<rect x="{zx(edges[i]):.1f}" y="{yy(dens[i]):.1f}" width="{zx(edges[i + 1]) - zx(edges[i]):.1f}" '
                  f'height="{base - yy(dens[i]):.1f}" fill="{LINK}" fill-opacity="0.22" stroke="{LINK}" stroke-width="0.6"/>')
    pts = " ".join(f"{zx(z):.1f},{yy(math.exp(-z * z / 2) / math.sqrt(2 * math.pi)):.1f}"
                   for z in [-2 + 7 * k / 200 for k in range(201)])
    s += f'<polyline points="{pts}" fill="none" stroke="{MUTED}" stroke-width="2.4" stroke-dasharray="7,5"/>'
    s += f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += f'<line x1="{zx(0):.1f}" y1="{top - 30}" x2="{zx(0):.1f}" y2="{base}" stroke="{ACCENT}" stroke-width="3"/>'
    for z in (-2, 0, 2, 4):
        s += mono(zx(z), base + 24, f"{z:+d}".replace("+0", "0").replace("-", "−"), size=13, fill=SOFT)
    s += mono(x0 - 10, 124, "means of 30 customers' spend · in standard errors", size=13, fill=SOFT, anchor="start")
    s += mono(zx(0) + 12, top - 14, "true mean", size=13, fill=ACCENT, anchor="start", weight="600")
    s += mono(zx(0) + 12, top + 6, f"{below:.1%} of means fall below it", size=13, fill=MUTED, anchor="start")
    lx, ly = zx(1.45), yy(0.30)                 # beside the curve's right flank, above the bars
    s += mono(lx, ly, "the normal curve", size=13, fill=MUTED, anchor="start")
    s += mono(lx, ly + 20, "the CLT promises", size=13, fill=MUTED, anchor="start")
    s += f'<line x1="{lx - 4:.1f}" y1="{ly + 26:.1f}" x2="{zx(1.12):.1f}" y2="{yy(0.215):.1f}" stroke="{MUTED}" stroke-width="1"/>'

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 2", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 282, "The Sampling", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 336, "Distribution", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 384, "The CLT and Where n = 30 Fails", size=30, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 432, "how fast a mean turns normal depends on skew,", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 458, "and on real spend n = 30 is nowhere near", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "standard error · Student's t · skewness · Berry–Esseen · Cauchy · Pareto · Monte Carlo error",
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
