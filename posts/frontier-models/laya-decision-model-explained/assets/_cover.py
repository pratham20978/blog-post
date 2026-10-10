#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important idea (a token strip with one
[MASK] in front of every option, each [MASK] feeding one bar of a per-question
softmax), white-smoke paper, a single tangerine element (the billing marker and its
bar). 1200 x 630. The cover carries no brand lockup; the social cards do.
"""
import json
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
EN = json.loads((HERE.parent / "lab" / "trace.json").read_text(encoding="utf-8"))["english"]
VW, VH = 1200, 630
STEM = "cover-laya-decision-model-explained"


def build():
    route = next(q for q in EN["questions"] if q["id"] == "route")
    probs = route["p_returned"]
    s = ""
    # motif: a strip of tiles — question, then [MASK] + option pairs, then the ticket
    x0, y0, tw, th, gap = 96, 170, 22, 34, 4
    tiles = (["q"] * 3 + ["m", "o", "o"] + ["m", "o", "o"] + ["m", "o", "o"] + ["m", "o", "o"]
             + ["s"] * 3)
    fills = {"q": "rgba(94,122,155,0.20)", "o": "rgba(184,145,90,0.22)", "s": "rgba(124,143,111,0.22)"}
    strokes = {"q": "#5e7a9b", "o": "#b8915a", "s": "#7c8f6f"}
    mask_x = []
    for i, t in enumerate(tiles):
        x = x0 + i * (tw + gap)
        if t == "m":
            focal = len(mask_x) == 0
            mask_x.append(x + tw / 2)
            s += (f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="3" '
                  f'fill="{ACCENT if focal else "#ffffff"}" stroke="{ACCENT if focal else INK}" '
                  f'stroke-width="{1.4 if focal else 1}"/>')
        else:
            s += (f'<rect x="{x}" y="{y0}" width="{tw}" height="{th}" rx="3" '
                  f'fill="{fills[t]}" stroke="{strokes[t]}" stroke-width="0.8"/>')
    # each marker drops to its own bar
    base, hmax = y0 + 290, 190
    for i, (mx, p) in enumerate(zip(mask_x, probs)):
        top = base - p * hmax
        col = ACCENT if i == 0 else MUTED
        s += (f'<line x1="{mx:.1f}" y1="{y0 + th + 2}" x2="{mx:.1f}" y2="{top - 6:.1f}" '
              f'stroke="{col}" stroke-width="1" stroke-dasharray="{"" if i == 0 else "3,3"}"/>')
        s += (f'<rect x="{mx - 16:.1f}" y="{top:.1f}" width="32" height="{base - top:.1f}" '
              f'fill="{col}" fill-opacity="{0.85 if i == 0 else 0.35}"/>')
        s += mono(mx, base + 20, ["billing", "technical", "account", "sales"][i], size=9,
                  fill=ACCENT if i == 0 else SOFT, track="0.04em")
    s += (f'<line x1="{x0}" y1="{base}" x2="{x0 + len(tiles) * (tw + gap) - gap}" y2="{base}" '
          f'stroke="rgba(45,49,66,0.35)"/>')
    s += mono(mask_x[0] + 22, base - probs[0] * hmax + 14, f"{probs[0]:.3f}", size=11, fill=ACCENT,
              anchor="start", weight="600")

    # title block
    tx = 640
    s += mono(tx, 226, "machine learning  ·  frontier models  ·  laya, part 1", size=11, fill=SOFT,
              anchor="start", track="0.2em", weight="500")
    s += txt(tx, 290, "What a Decision", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(tx, 346, "Model Is", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(tx, 392, "traced through Laya, number by number", size=17, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="96" y1="536" x2="1104" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 562, "option markers · one softmax per question · 421,293,827 parameters · zero output tokens",
              size=10, fill=MUTED, anchor="start", track="0.12em")

    svg = svg_doc(VW, VH, s)
    (HERE / f"{STEM}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg,
                                      encoding="utf-8")
    (HERE / f"{STEM}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / f"{STEM}.svg", HERE / f"{STEM}.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
