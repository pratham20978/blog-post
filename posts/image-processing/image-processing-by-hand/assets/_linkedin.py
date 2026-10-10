#!/usr/bin/env python3
"""LinkedIn carousel frames — 4:5, built in the diagram-design skin.

blog-visuals stops at prompts because image models mangle typography. Built here
instead, the frames get real Instrument Serif headlines and the post's actual
numbers, and they match the 17 figures exactly. The illustration prompts in
linkedin-prompts.md remain the alternative route.

Run:  python3 _linkedin.py           # all frames
      python3 _linkedin.py 03 05     # only those
"""
import math
import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, box, cell, masked, mono,
                    rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1080, 1350
M = 80                      # side margin
MID = VW / 2


def frame(num, total, kicker, headline, deck, visual, takeaway, cta=None):
    """Shared chrome: eyebrow, serif headline, deck, visual band, takeaway."""
    s = ""
    # eyebrow row
    s += mono(M, 120, kicker, size=15, fill=SOFT, anchor="start", track="0.24em", weight="500")
    s += mono(VW - M, 120, f"{num} / {total}", size=15, fill=ACCENT if num == total else SOFT,
              anchor="end", track="0.24em", weight="500")
    s += (f'<line x1="{M}" y1="148" x2="{VW - M}" y2="148" stroke="{RULE}" stroke-width="1"/>')

    # headline
    y = 232
    for line in headline:
        s += txt(M, y, line, size=58, fill=INK, family=SERIF, anchor="start")
        y += 68
    # deck
    y += 6
    for line in deck:
        s += txt(M, y, line, size=21, fill=MUTED, family=SANS, anchor="start")
        y += 30

    s += visual

    # takeaway strip
    s += (f'<line x1="{M}" y1="1176" x2="{VW - M}" y2="1176" stroke="{RULE}" stroke-width="1"/>')
    ty = 1216
    for line in takeaway:
        s += txt(M, ty, line, size=22, fill=INK, family=SANS, anchor="start", weight="500")
        ty += 30
    if cta:
        s += mono(M, 1300, cta, size=14, fill=ACCENT, anchor="start", track="0.16em")
    else:
        s += mono(M, 1300, "image processing by hand", size=14, fill=SOFT,
                  anchor="start", track="0.16em")
    s += mono(VW - M, 1300, "canery", size=14, fill=SOFT, anchor="end", track="0.24em")

    svg = svg_doc(VW, VH, s)
    stem = f"linkedin-{num:02d}-{SLUGS[num]}"
    (HERE / f"{stem}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg,
                                      encoding="utf-8")
    (HERE / f"{stem}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>{stem}</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / f"{stem}.svg", HERE / f"{stem}.png", VW, VH, svg_markup=svg)
    print(f"  {stem}.png  ({VW}x{VH} @2x)")


SLUGS = {1: "grid-takes-it", 2: "the-window", 3: "three-answers",
         4: "one-bad-pixel", 5: "l1-overstates", 6: "library-vs-math"}


# ------------------------------------------------------------------ 01
def f01():
    v = ""
    bx, bw, n = M, VW - 2 * M, 9
    step = bw / n

    def sig(u):
        return 0.5 + 0.34 * math.sin(u * 7.2) + 0.16 * math.sin(u * 19.0)

    # band A — the continuous signal
    v += mono(bx, 484, "the continuous signal", size=15, fill=SOFT, anchor="start", track="0.14em")
    pts = []
    for i in range(241):
        u = i / 240
        pts.append(f"{bx + u * bw:.1f},{600 - 96 * sig(u):.1f}")
    v += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{MUTED}" stroke-width="2.5"/>'

    heights = []
    for kk in range(n):
        u = (kk + 0.5) / n
        y = 600 - 96 * sig(u)
        heights.append(sig(u))
        x = bx + u * bw
        v += (f'<line x1="{x:.1f}" y1="{y + 10:.1f}" x2="{x:.1f}" y2="700" stroke="{RULE_SOLID}" '
              f'stroke-width="1" stroke-dasharray="4,5"/>')
        v += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{INK}"/>'
    v += masked(MID, 744, "only these nine points are kept — the rest is gone",
                size=16, fill=ACCENT)

    # band B — what survives
    v += f'<line x1="{bx}" y1="1096" x2="{bx + bw}" y2="1096" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for kk, hv in enumerate(heights):
        h = 110 + 190 * hv
        x = bx + kk * step + 10
        focal = kk == 4
        v += (f'<rect x="{x:.1f}" y="{1096 - h:.1f}" width="{step - 20:.1f}" height="{h:.1f}" '
              f'rx="4" fill="{ACCENT if focal else INK}" fill-opacity="{0.14 if focal else 0.07}" '
              f'stroke="{ACCENT if focal else INK}" stroke-width="1.5"/>')
    v += mono(bx, 1136, "what the grid keeps — nine numbers", size=15, fill=SOFT,
              anchor="start", track="0.14em")
    frame(1, 6,
          "sample · filter · transform · decide",
          ["The grid already", "took something."],
          ["Sampling runs before your code does, and it is the only",
           "stage in the pipeline that destroys information outright."],
          v,
          ["A prefilter has to run before the resample.",
           "Applied afterwards it removes nothing."])


# ------------------------------------------------------------------ 02
def f02():
    v = ""
    cw, cols, rows = 96, 9, 5
    gx, gy = (VW - cols * cw) / 2, 540
    v += mono(gx, 512, "the image", size=15, fill=SOFT, anchor="start", track="0.14em")
    for r in range(rows):
        for c in range(cols):
            inwin = 2 <= c <= 4 and 1 <= r <= 3
            v += (f'<rect x="{gx + c * cw}" y="{gy + r * cw}" width="{cw}" height="{cw}" '
                  f'fill="{ACCENT_TINT if inwin else "#ffffff"}" '
                  f'stroke="rgba(45,49,66,0.22)" stroke-width="1"/>')
    for off, op in ((-2, 0.18), (-1, 0.34)):
        v += (f'<rect x="{gx + (2 + off) * cw}" y="{gy + cw}" width="{3 * cw}" height="{3 * cw}" '
              f'rx="4" fill="none" stroke="{ACCENT}" stroke-width="2.5" stroke-opacity="{op}"/>')
    v += (f'<rect x="{gx + 2 * cw}" y="{gy + cw}" width="{3 * cw}" height="{3 * cw}" rx="4" '
          f'fill="none" stroke="{ACCENT}" stroke-width="3.5"/>')
    v += masked(gx + 3.5 * cw, gy + cw - 26, "one 3 × 3 window of weights", size=16, fill=ACCENT)
    v += mono(MID, gy + rows * cw + 52, "multiply · add · move one pixel · repeat",
              size=16, fill=SOFT, track="0.16em")
    frame(2, 6,
          "the operation almost everything reduces to",
          ["One small window", "does most of it."],
          ["Lay a grid of weights over a neighbourhood, multiply,",
           "add. Slide it one pixel and do it again."],
          v,
          ["Gaussian blur, Sobel, sharpening, the Laplacian —",
           "that same sum with different weights."])


# ------------------------------------------------------------------ 03
def f03():
    v = ""
    win = [[40, 40, 40], [40, 255, 40], [40, 40, 40]]
    cw, gx, gy = 110, 100, 600
    v += mono(gx, 572, "the identical nine numbers", size=15, fill=SOFT,
              anchor="start", track="0.14em")
    for r in range(3):
        for c in range(3):
            val = win[r][c]
            spike = val == 255
            v += cell(gx + c * cw, gy + r * cw, cw, cw, val,
                      fill=ACCENT_TINT if spike else "#ffffff",
                      stroke=ACCENT if spike else "rgba(45,49,66,0.26)",
                      tcolor=ACCENT if spike else INK, size=30,
                      weight="600" if spike else "500")

    results = [("BOX MEAN", "64", "smears it across nine pixels", MUTED),
               ("GAUSSIAN", "99", "27% of the weight on the bad pixel", MUTED),
               ("MEDIAN", "40", "removes it exactly", ACCENT)]
    rx, rw = 500, 500
    for i, (name, val, note, colour) in enumerate(results):
        y = 596 + i * 128
        focal = colour == ACCENT
        v += box(rx, y, rw, 112, fill=ACCENT_TINT if focal else "#ffffff", stroke=colour)
        v += mono(rx + 28, y + 44, name, size=16, fill=colour, anchor="start", track="0.18em")
        v += mono(rx + 28, y + 80, note, size=14, fill=SOFT, anchor="start", track="0.02em")
        v += txt(rx + rw - 28, y + 74, val, size=48, weight="600", family=MONO,
                 fill=colour, anchor="end")
    v += masked(MID, 1040, "only one of the three actually removed anything",
                size=17, fill=ACCENT)
    frame(3, 6,
          "worked by hand, on real integers",
          ["Same nine numbers.", "Three answers."],
          ["A 3 × 3 neighbourhood: eight pixels at 40, one bad",
           "pixel at 255. Three operators that all claim to denoise."],
          v,
          ["The Gaussian does worse than the box, because it",
           "puts 27% of its weight on the one wrong pixel."])


# ------------------------------------------------------------------ 04
def f04():
    v = ""
    grids = [([[40, 40, 200], [255, 40, 200], [40, 40, 200]], "210", "with one bad pixel", ACCENT),
             ([[40, 40, 200], [40, 40, 200], [40, 40, 200]], "640", "without it", MUTED)]
    cw = 100
    for gi, (g, out, note, colour) in enumerate(grids):
        gx, gy = 100 + gi * 580, 560
        v += mono(gx, 532, note, size=15, fill=colour, anchor="start", track="0.14em")
        for r in range(3):
            for c in range(3):
                val = g[r][c]
                spike = val == 255
                v += cell(gx + c * cw, gy + r * cw, cw, cw, val,
                          fill=ACCENT_TINT if spike else "#ffffff",
                          stroke=ACCENT if spike else "rgba(45,49,66,0.26)",
                          tcolor=ACCENT if spike else INK, size=26,
                          weight="600" if spike else "500")
        v += mono(gx + 1.5 * cw, 918, "sobel Gx", size=15, fill=SOFT, track="0.18em")
        v += txt(gx + 1.5 * cw, 1010, out, size=76, weight="600", family=MONO, fill=colour)
    v += (f'<line x1="{100 + 3 * cw + 40}" y1="710" x2="{680 - 40}" y2="710" '
          f'stroke="{RULE_SOLID}" stroke-width="1" stroke-dasharray="6,6"/>')
    v += masked(MID, 1090, "a 67% error, from a pixel three columns away", size=17, fill=ACCENT)
    frame(4, 6,
          "why the stage order is not negotiable",
          ["One bad pixel.", "A 67% error."],
          ["The Sobel gradient at the same position, computed twice —",
           "once with a single hot pixel nearby, once without it."],
          v,
          ["A derivative amplifies high frequencies. Noise is high",
           "frequency. So you filter before you differentiate."])


# ------------------------------------------------------------------ 05
def f05():
    v = ""
    ox, oy, k = 170, 1060, 0.62
    px, py = ox + 480 * k, oy - 480 * k
    v += mono(ox - 20, 660, "the gradient at a 45° edge", size=15, fill=SOFT,
              anchor="start", track="0.14em")
    v += f'<line x1="{ox}" y1="{oy}" x2="{ox + 370}" y2="{oy}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    v += f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - 370}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    v += mono(ox + 384, oy + 6, "Gx", size=14, fill=SOFT, anchor="start")
    v += mono(ox - 12, oy - 384, "Gy", size=14, fill=SOFT, anchor="end")
    v += (f'<polyline points="{ox},{oy} {px:.1f},{oy} {px:.1f},{py:.1f}" fill="none" '
          f'stroke="{MUTED}" stroke-width="3.5"/>')
    v += masked((ox + px) / 2, oy + 38, "480", size=15, fill=MUTED)
    v += masked(px + 48, (oy + py) / 2, "480", size=15, fill=MUTED)
    v += (f'<line x1="{ox}" y1="{oy}" x2="{px:.1f}" y2="{py:.1f}" stroke="{ACCENT}" '
          f'stroke-width="4"/>')
    v += f'<circle cx="{px:.1f}" cy="{py:.1f}" r="8" fill="{ACCENT}"/>'
    v += mono(ox + 112, oy - 32, "45°", size=15, fill=SOFT)

    rows = [("L1  |480| + |480|", "960", "OpenCV's Canny default", MUTED),
            ("L2  √(480² + 480²)", "678.8", "the true magnitude", ACCENT)]
    rx, rw = 580, 420
    for i, (expr, val, note, colour) in enumerate(rows):
        y = 620 + i * 152
        focal = colour == ACCENT
        v += box(rx, y, rw, 126, fill=ACCENT_TINT if focal else "#ffffff", stroke=colour)
        v += mono(rx + 26, y + 44, expr, size=17, fill=colour, anchor="start", track="0.02em")
        v += mono(rx + 26, y + 76, note, size=14, fill=SOFT, anchor="start", track="0.02em")
        v += txt(rx + rw - 26, y + 112, val, size=40, weight="600", family=MONO,
                 fill=colour, anchor="end")
    v += masked(rx + rw / 2, 966, "larger by exactly √2", size=18, fill=ACCENT)
    frame(5, 6,
          "the default nobody checks",
          ["Your edge threshold", "is orientation-biased."],
          ["cv2.Canny defaults to L2gradient=False, so it measures",
           "magnitude as |Gx| + |Gy| rather than the hypotenuse."],
          v,
          ["At 45° the reported magnitude is 41% too large.",
           "Where either component is zero, the two agree."])


# ------------------------------------------------------------------ 06
def f06():
    v = ""
    kern = [["-1", "0", "1"], ["-2", "0", "2"], ["-1", "0", "1"]]
    flip = [["1", "0", "-1"], ["2", "0", "-2"], ["1", "0", "-1"]]
    cw = 104
    for gi, (g, label, colour) in enumerate(((kern, "the kernel you passed in", MUTED),
                                             (flip, "the kernel it applied", ACCENT))):
        gx, gy = 110 + gi * 548, 560
        v += mono(gx, 532, label, size=15, fill=colour, anchor="start", track="0.14em")
        for r in range(3):
            for c in range(3):
                v += cell(gx + c * cw, gy + r * cw, cw, cw, g[r][c],
                          fill=ACCENT_TINT if colour == ACCENT else "#ffffff",
                          stroke=colour if colour == ACCENT else "rgba(45,49,66,0.26)",
                          tcolor=colour, size=28, weight="600")
    for dy in (-12, 12):
        v += (f'<line x1="512" y1="{716 + dy}" x2="568" y2="{716 + dy}" stroke="{INK}" '
              f'stroke-width="4" stroke-linecap="round"/>')
    v += (f'<line x1="556" y1="686" x2="524" y2="746" stroke="{INK}" stroke-width="4" '
          f'stroke-linecap="round"/>')
    v += (f'<rect x="{M}" y="930" width="{VW - 2 * M}" height="150" rx="8" fill="none" '
          f'stroke="{RULE}" stroke-width="1" stroke-dasharray="6,5"/>')
    v += mono(MID, 986, "cv2.filter2D — \"Convolves an image with the kernel\"",
              size=17, fill=MUTED, track="0.02em")
    v += mono(MID, 1032, "…then the docs state it computes correlation,", size=17,
              fill=ACCENT, track="0.02em")
    v += mono(MID, 1060, "not the convolution", size=17, fill=ACCENT, track="0.02em")
    frame(6, 6,
          "the gap this whole post is about",
          ["The library is", "not the math."],
          ["Every symmetric kernel you test with agrees under both",
           "conventions. The bug waits for the first asymmetric one."],
          v,
          ["Four stages, one operator, and the places where the",
           "API and the math quietly disagree."],
          cta="read it on canery →")


FRAMES = {"01": f01, "02": f02, "03": f03, "04": f04, "05": f05, "06": f06}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FRAMES)
    for kk in want:
        if kk in FRAMES:
            FRAMES[kk]()
