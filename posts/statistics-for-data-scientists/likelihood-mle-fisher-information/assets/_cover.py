#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 2 reduced to its argument: Clarke's log-likelihood
for the V-1 rate, with the three distances from the MLE to the null value 0.85 — the horizontal gap
(Wald), the drop in height (likelihood ratio) and the slope at the null (score, the one tangerine
line). Values come from the lab's capture. 1200 x 630. The cover carries no brand lockup; the social
cards do.
"""
import json
import math
import pathlib

from _build import (ACCENT, FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize,
                    svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-likelihood-mle-fisher-information"


def build():
    v1 = CAP["poisson"]["v1"]
    total, n, lam = v1["total"], v1["n"], v1["lam_hat"]
    lam0 = 0.85
    st = v1["nulls"]["0.85"]
    assert (total, n) == (537, 576) and (round(st["wald"], 2), round(st["lr"], 2), round(st["score"], 2)) == (4.18, 4.45, 4.59)
    ll = lambda l: total * math.log(l / lam) - n * (l - lam)
    x0, x1, top, base = 110, 560, 200, 470                         # plot box: λ from 0.82 to 0.97, l from -3 to 0.4
    ex = lambda v: x0 + (v - 0.82) / 0.15 * (x1 - x0)
    ey = lambda v: base - (v + 3.0) / 3.4 * (base - top)
    pts = [(ex(0.82 + 0.15 * i / 300), ey(ll(0.82 + 0.15 * i / 300))) for i in range(301)]
    pts = [(a, b) for a, b in pts if b <= base]
    s = (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" stroke="{INK}" '
         f'stroke-width="3" stroke-linejoin="round"/>')
    drop, slope = ll(lam0), total / lam0 - n
    s += f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += (f'<line x1="{ex(lam0):.1f}" y1="{ey(0.28):.1f}" x2="{ex(lam):.1f}" y2="{ey(0.28):.1f}" stroke="{LINK}" '
          f'stroke-width="2.6"/>')                                 # Wald: the gap
    for xx in (ex(lam0), ex(lam)):
        s += f'<line x1="{xx:.1f}" y1="{ey(0.28) - 8:.1f}" x2="{xx:.1f}" y2="{ey(0.28) + 8:.1f}" stroke="{LINK}" stroke-width="2.6"/>'
    xl = ex(lam0) - 26                                             # likelihood ratio: the drop
    s += f'<line x1="{xl:.1f}" y1="{ey(0):.1f}" x2="{xl:.1f}" y2="{ey(drop):.1f}" stroke="{INK}" stroke-width="2.6"/>'
    for yv in (0, drop):
        s += f'<line x1="{xl - 8:.1f}" y1="{ey(yv):.1f}" x2="{xl + 8:.1f}" y2="{ey(yv):.1f}" stroke="{INK}" stroke-width="2.6"/>'
    t0, t1 = lam0 - 0.012, lam0 + 0.036                            # score: the slope at the null, the one tangerine line
    s += (f'<line x1="{ex(t0):.1f}" y1="{ey(drop + slope * (t0 - lam0)):.1f}" x2="{ex(t1):.1f}" '
          f'y2="{ey(drop + slope * (t1 - lam0)):.1f}" stroke="{ACCENT}" stroke-width="3"/>')
    s += f'<circle cx="{ex(lam):.1f}" cy="{ey(0):.1f}" r="6" fill="{INK}"/>'
    s += f'<circle cx="{ex(lam0):.1f}" cy="{ey(drop):.1f}" r="6" fill="{ACCENT}"/>'
    s += mono(x0 - 10, 132, "Clarke's 576 squares · log-likelihood of the V-1 rate", size=13, fill=SOFT, anchor="start")
    s += mono((ex(lam0) + ex(lam)) / 2, ey(0.28) - 16, f"Wald {st['wald']:.2f}", size=13, fill=LINK, weight="600")
    s += mono(xl - 14, ey(drop / 2) + 5, f"LR {st['lr']:.2f}", size=13, fill=INK, anchor="end", weight="600")
    s += mono(ex(t1) - 12, ey(drop + slope * (t1 - lam0)) + 6, f"score {st['score']:.2f}", size=13, fill=ACCENT,
              anchor="end", weight="600")
    s += mono(ex(lam0), base + 24, "null 0.85", size=13, fill=SOFT)
    s += mono(ex(lam), base + 24, f"MLE {lam:.4f}", size=13, fill=SOFT)

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 4", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "Likelihood", size=60, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "The MLE, Three Tests,", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 382, "and Where χ² Fails", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 430, "one curve gives the estimate, its standard error", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 456, "and three tests; on a boundary, χ² is the wrong reference", size=17, fill=MUTED, family=SANS,
             anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "Fisher information · Wald, score, LR · profile likelihood · delta method · boundaries · power law or lognormal",
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
