#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif taken from the post's most important idea (a fixed-width kernel
reading two pixels of a shrink, against the kernel widened by 1/s that covers the
whole new pixel), white-smoke paper, a single tangerine element. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import pathlib

from _build import (ACCENT, FONTS, INK, MUTED, PAPER, RULE, SANS, SERIF, SOFT, mono,
                    rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630
STEM = "cover-resampling-and-aliasing"
ROW = [40, 255, 40, 200, 200]


def build():
    s = ""
    # motif: row r2 as five cells, the new 0.6x output cell above, two kernels below
    cw, gx, gy = 72, 84, 196
    for i, v in enumerate(ROW):
        # pixel convention: high value = bright, so 255 is near white and 40 near ink
        shade = 0.85 * (1 - (v - 40) / 215) + 0.04
        s += (f'<rect x="{gx + i * cw}" y="{gy}" width="{cw}" height="{cw}" '
              f'fill="rgba(45,49,66,{shade:.3f})" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
        s += mono(gx + i * cw + cw / 2, gy + cw / 2 + 4, str(v), size=12,
                  fill="#ffffff" if v < 120 else INK, weight="500")
    # the middle output of the 0.6x shrink covers input 5/3 .. 10/3 (centre x = 2)
    def px(x):
        return gx + (x + 0.5) * cw
    a, b = 7 / 6, 17 / 6
    s += (f'<rect x="{px(a):.1f}" y="{gy - 34}" width="{px(b) - px(a):.1f}" height="22" rx="3" '
          f'fill="none" stroke="{INK}" stroke-width="1"/>')
    s += mono((px(a) + px(b)) / 2, gy - 42, "one new pixel", size=9, fill=SOFT, track="0.14em")
    # kernels, drawn under the row
    base = gy + cw + 118
    s += f'<line x1="{gx}" y1="{base}" x2="{gx + 5 * cw}" y2="{base}" stroke="rgba(45,49,66,0.25)"/>'
    h = 96
    # fixed-width triangle at x = 2: reads c2 only
    s += (f'<polyline points="{px(1):.1f},{base} {px(2):.1f},{base - h * 0.62:.1f} {px(3):.1f},{base}" '
          f'fill="none" stroke="{MUTED}" stroke-width="1.6"/>')
    # stretched triangle: half-width 5/3, reads c1, c2, c3 (the single accent)
    s += (f'<polyline points="{px(2 - 5 / 3):.1f},{base} {px(2):.1f},{base - h:.1f} {px(2 + 5 / 3):.1f},{base}" '
          f'fill="rgba(235,108,54,0.08)" stroke="{ACCENT}" stroke-width="2"/>')
    for i in range(5):
        s += (f'<line x1="{px(i):.1f}" y1="{gy + cw}" x2="{px(i):.1f}" y2="{base}" '
              f'stroke="rgba(45,49,66,0.14)" stroke-width="0.8" stroke-dasharray="2,3"/>')
    s += mono(gx, base + 26, "fixed width: 1 of 3 pixels under it", size=9, fill=MUTED,
              anchor="start", track="0.08em")
    s += mono(gx, base + 42, "widened by 1/s: all of them", size=9, fill=ACCENT,
              anchor="start", track="0.08em")

    # title block
    s += mono(560, 236, "algorithms  ·  image processing by hand, part 3", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "Resampling", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "and Aliasing", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 400, "shrinking needs a kernel that widens with the scale", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "nearest · bilinear · bicubic · lanczos · area", size=10, fill=MUTED,
              anchor="start", track="0.14em")

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
