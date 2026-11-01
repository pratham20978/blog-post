#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 4 reduced to its argument: the exact type I error
of Student's t-test (tangerine, the one use) climbing to 29% as the smaller of two groups (10 against
40) gets the larger SD, against Welch's, flat at 5%. Values come from the lab's capture. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import json
import math
import pathlib

from _build import (ACCENT, FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-choosing-a-statistical-test"


def build():
    ex = CAP["twosample"]["designs"]["10,40"]["exact"]
    ks = [k for k in sorted(ex, key=float) if float(k) >= 1.0]
    assert round(100 * ex["4"]["student"], 2) == 29.37 and abs(ex["4"]["welch"] - 0.05) < 0.002
    x0, x1, top, base = 90, 570, 190, 470                       # SD ratio 1 to 4 (log scale), error 0 to 32%
    ex_ = lambda r: x0 + math.log2(r) / 2 * (x1 - x0)
    ey = lambda v: base - v / 0.32 * (base - top)
    stud = " ".join(f"{ex_(float(k)):.1f},{ey(ex[k]['student']):.1f}" for k in ks)
    wel = " ".join(f"{ex_(float(k)):.1f},{ey(ex[k]['welch']):.1f}" for k in ks)
    s = f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += f'<line x1="{x0}" y1="{ey(0.05):.1f}" x2="{x1}" y2="{ey(0.05):.1f}" stroke="{SOFT}" stroke-width="1.2" stroke-dasharray="6,5"/>'
    s += f'<polyline points="{wel}" fill="none" stroke="{LINK}" stroke-width="2.0" stroke-linejoin="round"/>'
    s += f'<polyline points="{stud}" fill="none" stroke="{ACCENT}" stroke-width="2.4" stroke-linejoin="round"/>'
    s += mono(x0 - 10, 132, "type I error of a 5% test, groups of 10 and 40", size=13, fill=SOFT, anchor="start")
    s += mono(ex_(4) - 4, ey(ex["4"]["student"]) - 16, "Student: 29%", size=13, fill=ACCENT, anchor="end", weight="600")
    s += mono(ex_(4) - 4, ey(0.05) - 12, "Welch: 5%", size=13, fill=LINK, anchor="end", weight="600")
    s += mono(x0, base + 24, "SD of the group of 10, over the 40's: 1 to 4", size=13, fill=SOFT, anchor="start")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 8", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "Which Statistical Test?", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "The Design Decides,", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 382, "Not the Data", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 430, "paired or not, Student or Welch, Fisher or Boschloo:", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 456, "each error rate measured where its condition fails", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "paired t · Student · Welch · pre-testing · tea tasting · Fisher · Boschloo · chi-squared · ANOVA",
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
