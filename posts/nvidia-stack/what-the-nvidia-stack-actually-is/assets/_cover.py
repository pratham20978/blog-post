#!/usr/bin/env python3
"""Template cover — deterministic, on-brand, real typography. 1200 x 630.

Motif is the post's first figure reduced to bands: the seven layers, with the two
the host must supply carried in the accent. Same construction as part 6's cover so
the series reads as one thing.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, PAPER2, RULE,
                    SERIF, SOFT, mono, rasterize, svg_doc, txt, vline)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    x, w, h, y0 = 84, 232, 30, 196
    layers = [("L7", "serving"), ("L6", "framework"), ("L5", "libraries"),
              ("L4", "compiler"), ("L3", "runtime"),
              ("L2", "libcuda.so.1"), ("L1", "nvidia.ko")]
    host_from = 5
    s += (f'<rect x="{x}" y="{y0}" width="{w}" height="{h * 7}" rx="4" fill="#ffffff" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    for i, (idx, name) in enumerate(layers):
        y = y0 + i * h
        host = i >= host_from
        if host:
            s += f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" fill="#ffffff"/>'
            s += f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" fill="{ACCENT_TINT}"/>'
        elif i % 2 == 1:
            s += (f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" '
                  f'fill="{PAPER2}" fill-opacity="0.55"/>')
        if i and not (host and i > host_from):
            s += (f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{RULE}" '
                  f'stroke-width="1"/>')
        s += mono(x + 14, y + h / 2 + 3, idx, size=8,
                  fill=ACCENT if host else SOFT, anchor="start", track="0.10em")
        s += mono(x + w - 14, y + h / 2 + 3, name, size=9,
                  fill=ACCENT if host else MUTED, anchor="end", track="0.06em")
    s += (f'<rect x="{x}" y="{y0 + host_from * h}" width="{w}" height="{h * 2}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="1.2"/>')
    s += vline(x - 20, y0 + h * 7 - 6, y0 + 6, stroke=MUTED, marker="arrow")
    s += mono(x, y0 + h * 7 + 26, "only the bottom two must come from the host",
              size=9, fill=SOFT, anchor="start", track="0.08em")

    s += mono(396, 236, "machine-learning  ·  L2", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(396, 300, "What the NVIDIA Stack", size=48, fill=INK, family=SERIF, anchor="start")
    s += txt(396, 356, "Actually Is", size=48, fill=ACCENT, family=SERIF, anchor="start")
    s += mono(396, 396, "driver  ·  runtime  ·  toolkit  ·  cuda-x  ·  wheels",
              size=11, fill=MUTED, anchor="start", track="0.18em")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "the nvidia stack  ·  part 1", size=10, fill=MUTED,
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
