#!/usr/bin/env python3
"""Template cover — deterministic, on-brand, real typography. 1200 x 630.

Same construction as parts 1 and 2 so the series reads as one thing. The motif is
this post's figure 1 reduced to its point: a utilization readout of 100% above a
grid of SMs in which exactly one is doing anything.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MUTED, PAPER, PAPER2, RULE, SERIF,
                    SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    x, y = 84, 170
    # the readout
    s += (f'<rect x="{x}" y="{y}" width="248" height="86" rx="4" fill="#ffffff" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    s += mono(x + 16, y + 26, "utilization.gpu", size=9.5, fill=SOFT, anchor="start", track="0.06em")
    s += txt(x + 232, y + 70, "100%", size=44, fill=ACCENT, family=SERIF, anchor="end")
    # the SMs underneath it: 8 x 12, one of them busy
    gx, gy, cw, ch, rows, cols = x, y + 108, 20.5, 20.5, 8, 12
    for r in range(rows):
        for c in range(cols):
            busy = (r, c) == (0, 0)
            s += (f'<rect x="{gx + c * cw:.1f}" y="{gy + r * ch:.1f}" width="{cw - 4:.1f}" '
                  f'height="{ch - 4:.1f}" rx="2" fill="{ACCENT if busy else PAPER2}" '
                  f'stroke="{ACCENT if busy else "none"}"/>')
    s += mono(x, gy + rows * ch + 20, "one kernel resident · one SM busy", size=9,
              fill=SOFT, anchor="start", track="0.08em")

    s += mono(396, 236, "machine-learning  ·  L3", size=11, fill=SOFT, anchor="start",
              track="0.24em", weight="500")
    s += txt(396, 300, "Why Your GPU Is Idle", size=48, fill=INK, family=SERIF, anchor="start")
    s += txt(396, 356, "at 100% Utilization", size=48, fill=ACCENT, family=SERIF, anchor="start")
    s += mono(396, 396, "launch queues  ·  streams  ·  events  ·  sync points  ·  cuda graphs",
              size=11, fill=MUTED, anchor="start", track="0.14em")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "the nvidia stack  ·  part 3", size=10, fill=MUTED,
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
