#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 3 reduced to its argument: the exact coverage of
the 95% Wald interval at n = 50, jagged and mostly below the nominal line (tangerine, the one use),
against the Clopper–Pearson interval's, which never falls below it. Values come from the lab's capture.
1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-confidence-intervals-coverage"


def build():
    cv = CAP["coverage"]["curves"]
    ps, wald, cp = cv["p"], cv["wald"], cv["clopper_pearson"]
    assert cv["n"] == 50 and min(cp) >= 0.95 and round(CAP["coverage"]["n50"]["wald"]["share_below_093"], 2) == 0.40
    x0, x1, top, base = 90, 570, 190, 470                      # p from 0.03 to 0.97, coverage 0.80 to 1.00
    lo_p, hi_p = 0.03, 0.97
    ex = lambda p: x0 + (p - lo_p) / (hi_p - lo_p) * (x1 - x0)
    ey = lambda c: base - (c - 0.80) / 0.20 * (base - top)
    keep = [i for i, p in enumerate(ps) if lo_p <= p <= hi_p]
    pts = lambda ys: " ".join(f"{ex(ps[i]):.1f},{ey(max(ys[i], 0.80)):.1f}" for i in keep)
    s = f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += f'<line x1="{x0 - 10}" y1="{ey(0.95):.1f}" x2="{x1 + 10}" y2="{ey(0.95):.1f}" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="6,5"/>'
    s += f'<polyline points="{pts(cp)}" fill="none" stroke="{INK}" stroke-width="1.6" stroke-linejoin="round"/>'
    s += f'<polyline points="{pts(wald)}" fill="none" stroke="{ACCENT}" stroke-width="1.8" stroke-linejoin="round"/>'
    s += mono(x1 + 14, ey(0.95) + 4, "95%", size=13, fill=MUTED, anchor="start")
    s += mono(x0 - 10, 132, "exact coverage of two 95% intervals · n = 50 · every p", size=13, fill=SOFT, anchor="start")
    top_cp = min(ey(cp[i]) for i in keep)                        # the curve's highest point, in pixels
    s += mono(ex(0.5), top_cp - 12, "Clopper–Pearson, never below 95%", size=13, fill=INK, weight="600")
    s += mono(ex(0.5), ey(0.835), "Wald, below 93% for 40% of p", size=13, fill=ACCENT, weight="600")
    s += mono(ex(0.5), base + 24, "true proportion p", size=13, fill=SOFT)

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 6", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "Confidence Intervals", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "What 95% Means,", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 382, "Measured", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 430, "the 95% belongs to the procedure, not your interval;", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 456, "exact sums show which intervals keep it", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "coverage · Wald · Wilson · Clopper–Pearson · a vaccine trial · overlapping intervals · the t-interval",
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
