#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif from the post's most important idea, white-smoke paper, a single
tangerine element. 1200 x 630. Same layout grid as parts 1 and 2 (title block at x=560,
motif on the left). Part 3's motif: a single wide band of page tiles, one of them the
page that changed, with the log running beneath it as a line of dots.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SERIF, SANS, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    cw, gap, n = 22, 7, 14
    x0, y = 96, 286
    focal = 10
    s += mono(x0, y - 22, "heap pages", size=9, fill=SOFT, anchor="start", track="0.16em")
    for i in range(n):
        x = x0 + i * (cw + gap)
        f = i == focal
        s += (f'<rect x="{x}" y="{y}" width="{cw}" height="{cw}" rx="3" '
              f'fill="{ACCENT_TINT if f else "#ffffff"}" '
              f'stroke="{ACCENT if f else "rgba(45,49,66,0.30)"}" stroke-width="{1.4 if f else 0.8}"/>')
        # the line pointer stripe at the top of every page tile
        s += (f'<line x1="{x + 4}" y1="{y + 5}" x2="{x + cw - 4}" y2="{y + 5}" '
              f'stroke="{ACCENT if f else "rgba(45,49,66,0.25)"}" stroke-width="0.8"/>')
    # the log beneath the band: a line of dots, the dots under the changed page in tangerine
    yl = y + cw + 36
    fx = x0 + focal * (cw + gap) + cw / 2
    for k in range(0, 67):
        cx = x0 + 2 + k * 6
        near = abs(cx - fx) < 12
        s += (f'<circle cx="{cx}" cy="{yl}" r="{1.9 if near else 1.3}" '
              f'fill="{ACCENT if near else "rgba(45,49,66,0.35)"}"/>')
    s += f'<line x1="{fx}" y1="{y + cw + 4}" x2="{fx}" y2="{yl - 5}" stroke="{ACCENT}" stroke-width="0.9" stroke-dasharray="2,2"/>'
    s += mono(x0, yl + 26, "the log", size=9, fill=SOFT, anchor="start", track="0.16em")

    s += mono(560, 236, "databases  ·  postgresql foundations, part 3 of 3", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "How PostgreSQL", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "Stores Data", size=54, fill=ACCENT, family=SERIF, anchor="start")
    s += txt(560, 400, "pages, two maps and a log, and how a row survives a crash", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "heap pages · line pointers · visibility map · free space map · TOAST · B-tree · WAL", size=10, fill=MUTED,
              anchor="start", track="0.14em")
    s += mono(1116, 562, "canery", size=10, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    (HERE / "cover.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize((HERE / "cover.svg").resolve(), (HERE / "cover.png").resolve(), VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
