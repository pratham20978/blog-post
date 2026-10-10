#!/usr/bin/env python3
"""Template cover — deterministic, on-brand, real typography. 1200 x 630.

Same construction as part 1's cover so the series reads as one thing; the motif
is this post's own figure 1 reduced to four stacked plates, one per version
number, with the two that decide a launch carried in the accent.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, PAPER2, RULE,
                    SERIF, SOFT, mono, rasterize, svg_doc, txt, vline)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    x, w, h, y0 = 84, 232, 46, 210
    # Four plates, top to bottom in the order the post numbers them.
    plates = [
        ("1", "nvidia.ko", "580.65.06", False),
        ("2", "libcuda.so.1", "13.0", True),
        ("3", "libcudart.so.13", "13.0", True),
        ("4", "nvcc", "13.4", False),
    ]
    s += (f'<rect x="{x}" y="{y0}" width="{w}" height="{h * 4}" rx="4" fill="#ffffff" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    for i, (idx, name, value, decisive) in enumerate(plates):
        y = y0 + i * h
        if decisive:
            s += f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" fill="#ffffff"/>'
            s += f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" fill="{ACCENT_TINT}"/>'
        elif i % 2 == 1:
            s += (f'<rect x="{x + 1}" y="{y}" width="{w - 2}" height="{h}" '
                  f'fill="{PAPER2}" fill-opacity="0.55"/>')
        if i:
            s += (f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{RULE}" '
                  f'stroke-width="1"/>')
        s += mono(x + 14, y + h / 2 - 2, idx, size=8,
                  fill=ACCENT if decisive else SOFT, anchor="start", track="0.10em")
        s += mono(x + 32, y + h / 2 - 2, name, size=9.5,
                  fill=ACCENT if decisive else MUTED, anchor="start", track="0.04em")
        s += mono(x + w - 14, y + h / 2 + 14, value, size=9,
                  fill=ACCENT if decisive else SOFT, anchor="end", track="0.06em")
    # The two that are compared against each other.
    s += (f'<rect x="{x}" y="{y0 + h}" width="{w}" height="{h * 2}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="1.2"/>')
    s += vline(x - 20, y0 + h * 3 + 10, y0 + h + 6, stroke=MUTED, marker="arrow")
    s += mono(x, y0 + h * 4 + 26, "only these two decide whether your code runs",
              size=9, fill=SOFT, anchor="start", track="0.08em")

    s += mono(396, 236, "machine-learning  ·  L2", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(396, 300, "The Four CUDA", size=48, fill=INK, family=SERIF, anchor="start")
    s += txt(396, 356, "Version Numbers", size=48, fill=ACCENT, family=SERIF, anchor="start")
    s += mono(396, 396, "kmd  ·  umd  ·  runtime  ·  nvcc  ·  compatibility",
              size=11, fill=MUTED, anchor="start", track="0.18em")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "the nvidia stack  ·  part 2", size=10, fill=MUTED,
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
