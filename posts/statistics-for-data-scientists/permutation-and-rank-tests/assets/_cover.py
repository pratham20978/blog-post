#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in Instrument Serif, a
Geist Mono category label above it, one simplified motif taken from the post's figures, white-smoke
paper, the tangerine used once. The motif is Figure 2 reduced to its argument: the totals of all
32,768 sign assignments of Darwin's 15 differences, with the two tails at least as extreme as the
observed 314 eighths in tangerine (the one use). Values come from the lab's capture. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import json
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-permutation-and-rank-tests"


def build():
    perm = CAP["example"]["perm"]
    vals, counts = perm["null_values"], perm["null_counts"]
    assert perm["ge"] == 863 and round(perm["p"], 4) == 0.0527
    x0, x1, base, top = 90, 570, 470, 200                  # totals -544 to 544, counts 0 to the peak
    peak = max(counts)
    ex = lambda v: x0 + (v + 560) / 1120 * (x1 - x0)
    ey = lambda c: base - c / peak * (base - top)
    s = f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    for v, c in zip(vals, counts):
        tail = abs(v) >= 314
        s += (f'<line x1="{ex(v):.1f}" y1="{base}" x2="{ex(v):.1f}" y2="{ey(c):.1f}" '
              f'stroke="{ACCENT if tail else SOFT}" stroke-width="{0.9 if tail else 0.8}"/>')
    for v in (-314, 314):
        s += f'<line x1="{ex(v):.1f}" y1="{top - 10}" x2="{ex(v):.1f}" y2="{base}" stroke="{INK}" stroke-width="1.0" stroke-dasharray="5,4"/>'
    s += mono(x0 - 10, 150, "all 32,768 sign flips of Darwin's 15 pairs", size=13, fill=SOFT, anchor="start")
    s += mono(ex(314) + 8, top + 8, "314: p = 0.0527", size=13, fill=INK, anchor="start", weight="600")
    s += mono(x0, base + 24, "total of the signed differences, eighths of an inch", size=13, fill=SOFT, anchor="start")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 10", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(640, 290, "Permutation and", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 340, "Rank Tests:", size=46, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 384, "What They Actually Test", size=34, fill=INK, family=SERIF, anchor="start")
    s += txt(640, 432, "exact when the labels are exchangeable, and only then;", size=17, fill=MUTED, family=SANS, anchor="start")
    s += txt(640, 458, "what Mann–Whitney rejects when the medians are equal", size=17, fill=MUTED, family=SANS, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "randomisation · exchangeability · the +1 · studentising · Mann–Whitney · Brunner–Munzel · "
              "Hodges–Lehmann · ARE · Spearman · Kendall", size=10, fill=MUTED, anchor="start", track="0.12em")

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
