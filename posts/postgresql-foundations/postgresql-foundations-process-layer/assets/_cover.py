#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback: title in
Instrument Serif at the optical centre, a Geist Mono category label above it, one
simplified motif from the post's most important idea (one supervisor, a row of workers
it forked, one of them sweeping, one gone), white-smoke paper, a single tangerine
element. 1200 x 630. Same layout grid as part 1's cover so the series reads as a set.
"""
import pathlib

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SERIF, SANS, SOFT, mono, rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1200, 630


def build():
    s = ""
    # motif: the postmaster above a row of children, fan lines from one point
    cw = 22
    px, py = 240, 176                      # the lone square
    s += (f'<rect x="{px}" y="{py}" width="{cw}" height="{cw}" rx="3" fill="#ffffff" '
          f'stroke="{INK}" stroke-width="1.2"/>')
    s += mono(px + cw / 2, py - 12, "postmaster", size=9, fill=SOFT, track="0.16em")
    n, gap = 10, 12
    rx0 = 96
    ry = 356
    focal_i, gone_i = 6, 4
    for i in range(n):
        x = rx0 + i * (cw + gap)
        cx = x + cw / 2
        # fan line from the lone square to each child (or to nothing for the gap)
        end_y = ry if i != gone_i else ry - 14
        s += (f'<line x1="{px + cw / 2}" y1="{py + cw}" x2="{cx}" y2="{end_y}" '
              f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>')
        if i == gone_i:
            continue
        focal = i == focal_i
        s += (f'<rect x="{x}" y="{ry}" width="{cw}" height="{cw}" rx="3" '
              f'fill="{ACCENT_TINT if focal else "#ffffff"}" '
              f'stroke="{ACCENT if focal else "rgba(45,49,66,0.30)"}" stroke-width="{1.4 if focal else 0.8}"/>')
    # the trail behind the sweeping worker
    fx = rx0 + focal_i * (cw + gap)
    for k in range(4):
        s += f'<circle cx="{fx - 8 - k * 9}" cy="{ry + cw + 14}" r="{2.2 - k * 0.35}" fill="{ACCENT}" fill-opacity="{0.9 - k * 0.2}"/>'
    s += mono(rx0, ry + cw + 40, "backends · checkpointer · WAL writer · autovacuum", size=9, fill=SOFT, anchor="start", track="0.16em")
    s += mono(rx0 + gone_i * (cw + gap) + cw / 2, ry + 14, "×", size=9, fill=SOFT)

    # title block (same grid as part 1)
    s += mono(560, 236, "databases  ·  postgresql foundations, part 2", size=11, fill=SOFT,
              anchor="start", track="0.24em", weight="500")
    s += txt(560, 300, "How PostgreSQL", size=54, fill=INK, family=SERIF, anchor="start")
    s += txt(560, 356, "Uses Processes", size=54, fill=ACCENT, family=SERIF, anchor="start")
    s += txt(560, 400, "one supervisor, a crowd of workers, and what each decides", size=15, fill=MUTED,
             family=SANS, anchor="start")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(84, 562, "the postmaster · backends · checkpointer · background writer · WAL writer · autovacuum · parallel workers", size=10, fill=MUTED,
              anchor="start", track="0.14em")
    s += mono(1116, 562, "canery", size=10, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    (HERE / "cover.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / "cover.svg", HERE / "cover.png", VW, VH, svg_markup=svg)
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
