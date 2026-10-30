#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography.

Per blog-visuals/references/cover-prompt.md § Template cover fallback, laid out like Part 3's cover so
the series reads as one publication: a motif on the left taken from the post's figures, a Geist Mono
category label, the title in Instrument Serif with its second line in tangerine, a topic strip, and the
series footer. The motif is Figure 5 reduced to its argument: run 1's request beside the segments that
held 4.63 GiB free in 128 MiB tails, none large enough. Values come from the lab's capture. 1200 x 630.
The cover carries no brand lockup; the social cards do.
"""
import json
import pathlib

from _build import ACCENT, FONTS, INK, MUTED, PAPER, RULE, SERIF, SOFT, mono, rasterize, svg_doc, txt

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-five-causes-of-cuda-out-of-memory"
MiB, GiB = 2**20, 2**30


def build():
    oom = CAP["runs"]["fragmentation"]["oom"]
    snap, stats = oom["snapshot"], oom["stats"]
    tails = [sg for sg in snap["segments"] if sg["total"] == 384 * MiB and sg["largest_free"] == 128 * MiB]
    free = stats["inactive_split_bytes.all.current"]
    assert len(tails) == 37 and f"{free / GiB:.2f}" == "4.63" and "Tried to allocate 256.00 MiB" in oom["message"]

    # The request, as the box Part 3 used for nvidia-smi's reading.
    s = (f'<rect x="84" y="170" width="248" height="86" rx="6" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>'
         + mono(100, 192, "Tried to allocate", size=11, fill=SOFT, anchor="start")
         + txt(316, 242, "256 MiB", size=42, fill=ACCENT, family=SERIF, anchor="end"))
    # The segments, to scale: a live 256 MiB head and a free 128 MiB tail each, five to a row, no wider
    # than the request's box, so the motif stays clear of the title column.
    sc, rh, rg, per = 0.113, 11, 6, 5
    assert per * (384 * sc + 6) <= 248
    for k in range(len(tails)):
        x, y = 84 + (k % per) * (384 * sc + 6), 282 + (k // per) * (rh + rg)
        s += f'<rect x="{x:.1f}" y="{y}" width="{256 * sc:.1f}" height="{rh}" fill="{INK}" fill-opacity="0.85"/>'
        s += (f'<rect x="{x + 256 * sc:.1f}" y="{y}" width="{128 * sc:.1f}" height="{rh}" fill="{ACCENT}" '
              f'fill-opacity="0.35" stroke="{ACCENT}" stroke-width="0.8"/>')
    s += mono(84, 446, f"{free / GiB:.2f} GiB free · no piece fits 256 MiB", size=11, fill=SOFT, anchor="start",
              track="0.06em")

    s += mono(470, 222, "machine-learning  ·  L3", size=12, fill=SOFT, anchor="start", track="0.2em", weight="500")
    s += txt(470, 292, "Five Causes of One", size=50, fill=INK, family=SERIF, anchor="start")
    s += txt(470, 350, "“CUDA Out of Memory”", size=50, fill=ACCENT, family=SERIF, anchor="start")
    s += mono(470, 400, "caching allocator  ·  fragmentation  ·  retained graphs", size=12, fill=MUTED, anchor="start",
              track="0.12em")
    s += mono(470, 424, "other processes  ·  memory outside PyTorch", size=12, fill=MUTED, anchor="start", track="0.12em")

    s += f'<line x1="84" y1="536" x2="1116" y2="536" stroke="{RULE}" stroke-width="1"/>'
    s += mono(84, 566, "the nvidia stack  ·  part 4", size=11, fill=MUTED, anchor="start", track="0.16em")
    s += mono(1116, 566, "canery", size=11, fill=SOFT, anchor="end", track="0.3em")

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
