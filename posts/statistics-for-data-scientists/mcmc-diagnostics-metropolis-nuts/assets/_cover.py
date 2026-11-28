#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 2 reduced to its argument: four Metropolis chains
started far apart (θ = 0.005, 0.03, 0.15, 0.4) settle within a few dozen iterations into the band that
holds the central 95% of the trial's exact posterior, shaded in tangerine (the one use). Values come
from the lab's capture. 1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import math
import pathlib

from _build import (FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, ACCENT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-mcmc-diagnostics-metropolis-nuts"
CH = (INK, LINK, "#7d9ccf", MUTED)


def build():
    pf = CAP["pfizer"]
    lo, hi = pf["exact"]["theta_q025"], pf["exact"]["theta_q975"]
    assert (round(lo, 4), round(hi, 4)) == (0.0232, 0.088)
    x0, x1, top, base = 90, 570, 150, 480
    n = 160
    ex = lambda t: x0 + t / n * (x1 - x0)
    ly = lambda v: base - (math.log10(v) - math.log10(0.003)) / (math.log10(0.6) - math.log10(0.003)) * (base - top)
    s = (f'<rect x="{x0}" y="{ly(hi):.1f}" width="{x1 - x0}" height="{ly(lo) - ly(hi):.1f}" fill="{ACCENT}" '
         f'fill-opacity="0.85" stroke="none"/>')
    for c, tr in enumerate(pf["trace_head"]):
        pts = [pf["starts"][c]] + tr[:n]
        s += (f'<polyline points="{" ".join(f"{ex(t):.1f},{ly(v):.1f}" for t, v in enumerate(pts))}" fill="none" '
              f'stroke="{CH[c]}" stroke-width="1.6" stroke-linejoin="round"/>')
        s += f'<circle cx="{ex(0):.1f}" cy="{ly(pts[0]):.1f}" r="4.5" fill="{CH[c]}"/>'
    s += f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += mono(x0, base + 26, "iteration 0", size=12, fill=SOFT, anchor="start")
    s += mono(x1, base + 26, f"{n}", size=12, fill=SOFT, anchor="end")
    s += mono(x0 - 10, 126, "four chains from dispersed starts, log scale", size=13, fill=SOFT, anchor="start")
    s += mono(x1, ly(lo) + 24, "the exact central 95%", size=13, fill=INK, anchor="end", weight="600")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 12", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "MCMC You Can Trust:", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "Metropolis by Hand,", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 384, "R-hat and ESS", size=30, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 432, "a vaccine trial's posterior sampled by hand, why", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 458, "1.1 is not converged, and the mode no chain visits", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "random-walk Metropolis · acceptance · autocorrelation · ESS · MCSE · split R-hat · "
              "rank normalisation · NUTS", size=10, fill=MUTED, anchor="start", track="0.12em")

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
