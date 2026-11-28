#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 2 reduced to its argument: the posterior of the
trial's vaccine efficacy after 8 of 170 cases under the protocol's beta(0.700102, 1) prior, with its
95% credible interval, 90.3% to 97.6%, in tangerine (the one use). Values come from the lab's capture.
1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import math
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-bayesian-inference-conjugate-priors"
A0, B0 = 0.700102, 1.0


def beta_pdf(x, a, b):
    return math.exp((a - 1) * math.log(x) + (b - 1) * math.log1p(-x) - (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)))


def build():
    row = next(r for r in CAP["pfizer"]["rows"] if r["endpoint"] == "covid19_7d_after_dose2_no_prior_infection")
    yv, yp = row["split"]
    a, b, r = A0 + yv, B0 + yp, row["r"]
    lo, hi = row["lower"], row["upper"]
    assert (round(100 * lo, 1), round(100 * hi, 1)) == (90.3, 97.6) and row["matches_published"]
    dens = lambda v: beta_pdf(r * (1 - v) / (1 + r * (1 - v)), a, b) * r / (1 + r * (1 - v)) ** 2
    v0, v1 = 0.86, 0.995
    x0, x1, base, top = 90, 570, 470, 200
    vs = [v0 + (v1 - v0) * i / 400 for i in range(401)]
    peak = max(dens(v) for v in vs)
    ex = lambda v: x0 + (v - v0) / (v1 - v0) * (x1 - x0)
    ey = lambda d: base - d / peak * (base - top)
    band = [v for v in vs if lo <= v <= hi]
    pts = " ".join(f"{ex(v):.1f},{ey(dens(v)):.1f}" for v in band)
    s = (f'<polygon points="{ex(band[0]):.1f},{base} {pts} {ex(band[-1]):.1f},{base}" fill="{ACCENT}" '
         f'fill-opacity="0.85" stroke="none"/>')
    s += (f'<polyline points="{" ".join(f"{ex(v):.1f},{ey(dens(v)):.1f}" for v in vs)}" fill="none" '
          f'stroke="{INK}" stroke-width="2.2" stroke-linejoin="round"/>')
    s += f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    for v in (0.88, 0.92, 0.96):
        s += mono(ex(v), base + 22, f"{100 * v:.0f}%", size=12, fill=SOFT)
    s += mono(x0 - 10, 150, "prior beta(0.700102, 1), then 8 of 170 cases", size=13, fill=SOFT, anchor="start")
    s += mono(ex(hi) + 10, top + 40, "90.3% to 97.6%", size=13, fill=INK, anchor="start", weight="600")
    s += mono(x0, base + 48, "vaccine efficacy, posterior density", size=13, fill=SOFT, anchor="start")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 11", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "Bayesian Inference", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "by Hand:", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 384, "Conjugacy and Credible Intervals", size=30, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 432, "Laplace's 1.1461 × 10⁻⁴², a vaccine trial's prior,", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 458, "and what a flat prior is flat on", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "beta–binomial · gamma–Poisson · normal–normal · HDI · coverage · posterior predictive · "
              "Jeffreys · Bayes factor · Lindley", size=10, fill=MUTED, anchor="start", track="0.12em")

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
