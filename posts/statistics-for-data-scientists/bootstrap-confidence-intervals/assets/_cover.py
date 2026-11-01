#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 10 reduced to its argument: the cdf of the largest
of five tank serial numbers, the true one smooth and running to N = 342, the bootstrap's (tangerine,
the one use) jumping by 0.672 at the observed maximum, 303, and never passing it. Values come from the
lab's capture. 1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-bootstrap-confidence-intervals"


def build():
    tk = CAP["maximum"]["tanks"]
    sup, pmf, serials, boot = tk["true_support"], tk["true_pmf"], tk["serials"], tk["boot_pmf"]
    assert tk["N"] == 342 and serials[-1] == 303 and round(tk["point_mass"], 3) == 0.672
    x0, x1, top, base = 90, 570, 190, 470                      # serial number 150 to 360, cdf 0 to 1
    lo, hi = 150, 360
    ex = lambda m: x0 + (m - lo) / (hi - lo) * (x1 - x0)
    ey = lambda c: base - c * (base - top)
    acc, pts = 0.0, []
    for m, p in zip(sup, pmf):
        acc += p
        if m >= lo:
            pts.append(f"{ex(m):.1f},{ey(acc):.1f}")
    pts.append(f"{ex(hi):.1f},{ey(1):.1f}")
    cdf, bpts = 0.0, [f"{ex(lo):.1f},{ey(0):.1f}"]
    for v, p in zip(serials, boot):
        if v >= lo:
            bpts += [f"{ex(v):.1f},{ey(cdf):.1f}", f"{ex(v):.1f},{ey(cdf + p):.1f}"]
        cdf += p
    bpts.append(f"{ex(hi):.1f},{ey(1):.1f}")
    s = f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += f'<line x1="{ex(342):.1f}" y1="{top - 6}" x2="{ex(342):.1f}" y2="{base}" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="6,5"/>'
    s += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="1.8" stroke-linejoin="round"/>'
    s += f'<polyline points="{" ".join(bpts)}" fill="none" stroke="{ACCENT}" stroke-width="2.2" stroke-linejoin="round"/>'
    s += mono(ex(342) + 10, ey(0.88), "N = 342", size=13, fill=MUTED, anchor="start")
    s += mono(x0 - 10, 132, "the largest of five tank serials: true cdf against the bootstrap's", size=13, fill=SOFT, anchor="start")
    s += mono(ex(303) - 14, ey(0.80), "bootstrap: 67% of its", size=13, fill=ACCENT, anchor="end", weight="600")
    s += mono(ex(303) - 14, ey(0.80) + 18, "mass on 303, none above", size=13, fill=ACCENT, anchor="end", weight="600")
    s += mono(ex(240), ey(0.32), "true: smooth, runs to 342", size=13, fill=INK, anchor="end", weight="600")
    s += mono(ex(255), base + 24, "serial number", size=13, fill=SOFT)

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 7", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "The Bootstrap", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "From Percentile to BCa,", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 382, "and Where It Breaks", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 430, "it treats the sample as the population;", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 456, "coverage measured where that holds, and where it fails", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "percentile · basic · studentized · BCa · law schools · skewed spend · the maximum · heavy tails · dependence",
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
