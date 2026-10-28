#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 2 reduced to its argument: the exact distribution of
the MLE (the largest of five serial numbers) piled against a wall at the true N, beside the unbiased MVUE's
distribution centred on N, and the true N as the one tangerine line. Values come from the lab's capture.
1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import pathlib

from _build import (ACCENT, FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize,
                    svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-estimator-bias-variance-mse"


def build():
    t = CAP["tanks"]
    n_tanks, k, pmf = t["N"], t["k"], t["pmf_max"]
    assert (n_tanks, k) == (342, 5) and round(t["exact"]["mle"]["bias"], 1) == -56.2
    x0, x1, base, top = 110, 560, 470, 190                       # plot box: estimates from 150 to 430
    ex = lambda v: x0 + (v - 150) / 280 * (x1 - x0)
    ymax = max(pmf) * 1.08
    yy = lambda d: base - d / ymax * (base - top)
    ms = [k + j for j in range(len(pmf))]
    mle = [(ex(m), yy(p)) for m, p in zip(ms, pmf) if m >= 150]
    s = (f'<polygon points="{ex(150):.1f},{base} ' + " ".join(f"{a:.1f},{b:.1f}" for a, b in mle)
         + f' {ex(n_tanks):.1f},{base}" fill="{LINK}" fill-opacity="0.22" stroke="{LINK}" stroke-width="1.4"/>')
    mvue = " ".join(f"{ex(m * (1 + 1 / k) - 1):.1f},{yy(p / (1 + 1 / k)):.1f}" for m, p in zip(ms, pmf)
                    if m * (1 + 1 / k) - 1 >= 150)
    end = ex(n_tanks * (1 + 1 / k) - 1)
    s += f'<polyline points="{mvue} {end:.1f},{base}" fill="none" stroke="{MUTED}" stroke-width="2.4" stroke-dasharray="7,5"/>'
    s += f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += f'<line x1="{ex(n_tanks):.1f}" y1="{top - 40}" x2="{ex(n_tanks):.1f}" y2="{base}" stroke="{ACCENT}" stroke-width="3"/>'
    for v in (200, 300, 400):
        s += mono(ex(v), base + 24, str(v), size=13, fill=SOFT)
    s += mono(x0 - 10, 124, "a million captures of five tanks · estimates of N", size=13, fill=SOFT, anchor="start")
    s += mono(ex(n_tanks) + 12, top - 24, f"true N = {n_tanks}", size=13, fill=ACCENT, anchor="start", weight="600")
    s += mono(ex(232), yy(0.0102), "MLE: biased,", size=13, fill=LINK, anchor="start", weight="600")
    s += mono(ex(232), yy(0.0102) + 20, "never above N", size=13, fill=LINK, anchor="start")
    s += mono(ex(n_tanks) + 12, top + 34, "MVUE: unbiased,", size=13, fill=MUTED, anchor="start")
    s += mono(ex(n_tanks) + 12, top + 54, "wider", size=13, fill=MUTED, anchor="start")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 3", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 282, "Estimators and", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 336, "Their Errors", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 384, "Why the Best One Can Be Biased", size=30, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 432, "unbiasedness removes one term of the error,", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 458, "so the most accurate estimator can be biased", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "German tanks · bias² + variance · Rao–Blackwell · n − 1 or n + 1 · James–Stein · Stein's paradox",
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
