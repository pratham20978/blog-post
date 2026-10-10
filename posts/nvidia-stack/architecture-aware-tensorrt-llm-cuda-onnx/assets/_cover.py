#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important figure (the compatibility
stack), white-smoke paper, a single tangerine element. 1200 x 630.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, PAPER2, RULE,
                    SERIF, SOFT, mono, rasterize, svg_doc, txt, vline)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    # motif: the six-layer compatibility stack, reduced to bands — one carries the accent
    x, w, h, y0 = 84, 232, 30, 208
    layers = [("L6", "model"), ("L5", "runtime"), ("L4", "framework"),
              ("L3", "code images"), ("L2", "toolkit"), ("L1", "host + gpu")]
    focal_i = 3
    s += (f'<rect x="{x}" y="{y0}" width="{w}" height="{h * 6}" rx="4" fill="#ffffff" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    for i, (idx, name) in enumerate(layers):
        y = y0 + i * h
        if i == focal_i:
            s += f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" fill="{ACCENT_TINT}"/>'
            s += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" '
                  f'stroke="{ACCENT}" stroke-width="1.2"/>')
        elif i % 2 == 1:
            s += f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" fill="{PAPER2}" fill-opacity="0.55"/>'
        if i and i != focal_i and i != focal_i + 1:
            s += f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{RULE}" stroke-width="1"/>'
        c = ACCENT if i == focal_i else (INK if i == focal_i else MUTED)
        s += mono(x + 14, y + h / 2 + 3, idx, size=8, fill=ACCENT if i == focal_i else SOFT,
                  anchor="start", track="0.10em")
        s += mono(x + w - 14, y + h / 2 + 3, name, size=9,
                  fill=ACCENT if i == focal_i else MUTED, anchor="end", track="0.06em")
    s += vline(x - 20, y0 + h * 6 - 6, y0 + 6, stroke=MUTED, marker="arrow")
    s += mono(x, y0 + h * 6 + 26, "rebuild the lowest layer that is missing code",
              size=9, fill=SOFT, anchor="start", track="0.08em")

    # title block
    s += mono(396, 236, "machine-learning  ·  L4", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(396, 300, "CUDA Architecture", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(396, 356, "Repairs", size=54, fill=ACCENT, family=SERIF, anchor="start")
    s += mono(396, 396, "pytorch  ·  tensorrt-llm  ·  onnx  ·  cmake", size=11, fill=MUTED,
              anchor="start", track="0.18em")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "audit · replace · rebuild one layer · verify", size=10, fill=MUTED,
              anchor="start", track="0.14em")
    s += mono(1116, 562, "canery", size=10, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg,
                                    encoding="utf-8")
    (HERE / "cover.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / "cover.svg", HERE / "cover.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
