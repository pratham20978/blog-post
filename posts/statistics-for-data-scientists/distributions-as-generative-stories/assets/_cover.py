#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 5 reduced to its argument: Greenwood and Yule's
647 women as bars on a square-root scale, the Poisson's expected counts dashed in slate, and the
negative binomial's in tangerine. Values come from the lab's capture. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import json
import math
import pathlib

from _build import (ACCENT, FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize,
                    svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-distributions-as-generative-stories"


def build():
    a = CAP["accidents"]
    obs, po, nb = a["data"]["observed"], a["poisson"]["expected"], a["negative_binomial"]["expected"]
    assert obs == [447, 132, 42, 21, 3, 2] and round(a["negative_binomial"]["chi2"], 2) == 4.20
    x0, base, step, top = 110, 470, 82, 21.5
    scale = 300 / top                                   # pixels per unit of sqrt(count)
    s = ""
    for j, o in enumerate(obs):
        h = math.sqrt(o) * scale
        s += (f'<rect x="{x0 + j * step - 27}" y="{base - h:.1f}" width="54" height="{h:.1f}" rx="2" '
              f'fill="{LINK}" fill-opacity="0.22" stroke="{LINK}" stroke-width="1.2"/>')
        s += mono(x0 + j * step, base + 24, ["0", "1", "2", "3", "4", "5+"][j], size=13, fill=SOFT)
    s += f'<line x1="{x0 - 44}" y1="{base}" x2="{x0 + 5 * step + 44}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    pts_p = " ".join(f"{x0 + j * step},{base - math.sqrt(e) * scale:.1f}" for j, e in enumerate(po))
    pts_n = " ".join(f"{x0 + j * step},{base - math.sqrt(e) * scale:.1f}" for j, e in enumerate(nb))
    s += f'<polyline points="{pts_p}" fill="none" stroke="{MUTED}" stroke-width="2.4" stroke-dasharray="7,5"/>'
    s += f'<polyline points="{pts_n}" fill="none" stroke="{ACCENT}" stroke-width="3"/>'
    for j, e in enumerate(nb):
        s += f'<circle cx="{x0 + j * step}" cy="{base - math.sqrt(e) * scale:.1f}" r="5" fill="{ACCENT}"/>'
    s += mono(x0 - 44, 134, "647 women · accidents in five weeks · √ count", size=13, fill=SOFT, anchor="start")
    right = x0 + 5 * step + 44
    for y, label, colour, dash, weight in ((210, "same rate for all: Poisson", MUTED, ' stroke-dasharray="7,5"', "400"),
                                           (232, "rates that differ: negative binomial", ACCENT, "", "600")):
        start = right - 7.8 * len(label)                # Geist Mono at 13 px advances about 7.8 px
        s += (f'<line x1="{start - 40:.0f}" y1="{y - 4}" x2="{start - 12:.0f}" y2="{y - 4}" stroke="{colour}" '
              f'stroke-width="{2.4 if dash else 3}"{dash}/>')
        s += mono(right, y, label, size=13, fill=colour, anchor="end", weight=weight)

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 1", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 282, "Distributions as", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 336, "Generative Stories", size=52, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 384, "Let the Process Pick", size=30, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 432, "write down how each number was made,", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 458, "derive the family, then let the data test it", size=17, fill=MUTED, family=SANS,
             anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "binomial · Poisson · gamma · negative binomial · lognormal · Student t · power law",
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
