#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 3 reduced to its argument: the fewest correct
digits that Householder QR and the normal equations keep on NIST's Longley and Filip regressions,
against the 15 digits NIST certifies (the tangerine line, its one use). Values come from the lab's
capture. 1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import pathlib

from _build import (ACCENT, FONTS, INK, LINK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-linear-regression-inference"


def build():
    ds = CAP["nist"]["datasets"]
    rows = [("Longley", "QR", min(ds["Longley"]["solvers"]["Householder QR"]["lre"]), INK),
            ("Longley", "normal equations", min(ds["Longley"]["solvers"]["normal equations (LU)"]["lre"]), LINK),
            ("Filip", "QR", min(ds["Filip"]["solvers"]["Householder QR"]["lre"]), INK),
            ("Filip", "normal equations", max(0.0, min(ds["Filip"]["solvers"]["normal equations (LU)"]["lre"])), LINK)]
    assert [round(r[2], 2) for r in rows] == [10.92, 7.38, 8.55, 0.0]
    x0, x1 = 120, 560
    X = lambda v: x0 + v / 15 * (x1 - x0)
    s = mono(x0, 132, "correct digits of the worst coefficient", size=13, fill=SOFT, anchor="start")
    s += f'<line x1="{X(15):.1f}" y1="156" x2="{X(15):.1f}" y2="470" stroke="{ACCENT}" stroke-width="2.4"/>'
    s += mono(X(15), 492, "15 certified", size=12, fill=ACCENT, anchor="end", weight="600")
    y = 186
    for k, (name, method, v, col) in enumerate(rows):
        if k == 2:
            y += 30
        s += mono(x0 + 8, y - 8, f"{name}, {method}", size=12, fill=MUTED, anchor="start")
        s += f'<rect x="{x0}" y="{y}" width="{max(X(v) - x0, 2):.1f}" height="26" fill="{col}" fill-opacity="0.85"/>'
        s += mono(max(X(v), x0 + 2) + 10, y + 18, "0" if v == 0 else f"{v:.2f}", size=13, fill=col, anchor="start", weight="600")
        y += 62
    s += f'<line x1="{x0}" y1="156" x2="{x0}" y2="470" stroke="{MUTED}" stroke-width="1.2"/>'
    s += mono(x0, 492, "0", size=12, fill=SOFT, anchor="start")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 13", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "Linear Regression", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "by Hand: Every Number", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 384, "in the Summary", size=30, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 432, "NIST's certified digits reproduced, every number", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 458, "recomputed, and which conditions really matter", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "QR · normal equations · log relative error · n − p · standard errors · t and F · R² · VIF · "
              "omitted variables · prediction intervals", size=10, fill=MUTED, anchor="start", track="0.12em")

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
