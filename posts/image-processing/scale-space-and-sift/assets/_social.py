#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Scale Space and SIFT".

Image Processing by Hand, part 10. The shell (lockup, rule, serif title, deck, takeaway,
footer) is copied from part 9's _social.py, with the lockup reading "canery.in". Every
number on a card comes from `_data.py` — the closed-form octave of the patch enlarged seven
times, the 26-neighbour block, the quadratic fit, the edge test, the fixed-level maps and the
plain-Python replay of OpenCV's rules — so a card cannot disagree with the article. DoG maps
follow the figures: blue below zero, warm grey above. Feed cards only, by the owner's choice
for this post: no Story frames.

Lockup width is 220 (feed), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]                     # a series member sits one level deeper
sys.path.insert(0, str(HERE))
import _data as d  # noqa: E402  — the article's numbers and conventions

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
LINK = "#2e5aa8"                            # the figures' blue, so cards and figures match
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/scale-space-and-sift"
FOOTER = "SCALE SPACE AND SIFT · CANERY.IN"

# ------------------------------------------------------------------ the lockup
LOCKUP_VIEWBOX_W = 671.40
IN_GAP = -10
IN_SIZE = 140
IN_ADVANCE = 171
LOCKUP_FULL_W = LOCKUP_VIEWBOX_W + IN_GAP + IN_ADVANCE


def logo_paths() -> str:
    source = (ROOT / "web/public/brand/canerly-lockup-horizontal.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b[\s\S]*?/>", source)
    if len(paths) != 2:
        raise RuntimeError("Could not read the canonical Canery horizontal lockup")
    suffix = (f'<text x="{LOCKUP_VIEWBOX_W + IN_GAP}" y="122.5" font-size="{IN_SIZE}" '
              f'font-family="{SANS}" font-weight="600" text-anchor="start">.in</text>')
    return "\n".join(paths) + "\n" + suffix


LOGO_PATHS = logo_paths()


# ------------------------------------------------------------------ primitives
def esc(v) -> str:
    return html.escape(str(v), quote=True)


def ascii_upper(v) -> str:
    return "".join(c.upper() if "a" <= c <= "z" else c for c in str(v))


def txt(x, y, value, size=22, fill=INK, family=SANS, weight=400, anchor="start", track=None):
    extra = f' letter-spacing="{track}"' if track else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{esc(value)}</text>')


def mono(x, y, value, size=18, fill=INK, anchor="start", weight=400):
    return txt(x, y, value, size, fill, MONO, weight, anchor)


def label(x, y, value, fill=SOFT, anchor="start", size=14):
    return txt(x, y, ascii_upper(value), size, fill, MONO, 500, anchor, "0.12em")


def lines(x, y, values, size, family=SANS, fill=INK, weight=400, gap=None, anchor="start"):
    gap = gap or int(size * 1.16)
    return "".join(txt(x, y + i * gap, v, size, fill, family, weight, anchor)
                   for i, v in enumerate(values))


def box(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.28)", rx=8, sw=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{dd}/>'


def vline(x, y1, y2, stroke=RULE, sw=1, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{dd}/>'


# ------------------------------------------------------------------ the shell
def shell(number, total, title, deck, visual, takeaway, cta=None):
    height, logo_y, logo_w = 1350, 72, 220
    rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
    deck_y = title_y + len(title) * title_gap + 20
    take_rule, take_y, foot_y = 1168, 1220, 1305
    scale = logo_w / LOCKUP_FULL_W
    defs = f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style></defs>'
    body = f'<rect width="{VW}" height="{height}" fill="{PAPER}"/>'
    body += (f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
             f'data-logo-width="{logo_w}" fill="{INK}" '
             f'transform="translate(72 {logo_y}) scale({scale})">{LOGO_PATHS}</g>')
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", SOFT, "end", 15)
    body += hline(72, 1008, rule_y)
    body += lines(72, title_y, title, title_size, SERIF, gap=title_gap)
    body += lines(72, deck_y, deck, 22, fill=MUTED, gap=30)
    body += visual
    body += hline(72, 1008, take_rule)
    body += lines(72, take_y, takeaway, 22, weight=600, gap=30)
    body += label(72, foot_y, cta or FOOTER, ACCENT if cta else SOFT, "start", 14)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {height}" '
            f'width="{VW}" height="{height}" role="img">\n{defs}\n{body}\n</svg>')


def emit(number, slug, title, deck, visual, takeaway, total, cta=None):
    svg = shell(number, total, title, deck, visual, takeaway, cta)
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(" ".join(title))}</title><link href="{FONTS.replace("&", "&amp;")}" rel="stylesheet">'
            f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style>'
            f'</head><body>{svg}</body></html>')
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"feed-{number:02d}-{slug}.html"
    path.write_text(page, encoding="utf-8")
    print(path.name)


# ------------------------------------------------------------------ the numbers
r = d.r
assert [(c[0], c[1], c[2]) for c in d.CANDS] == [(2, 10, 17), (2, 17, 17)]
assert [r(d.D7[i][d.CY][d.CX], 2) for i in range(5)] == [-21.86, -32.22, -35.38, -31.42, -23.12]
assert r(d.FB["sigma"]) == 2.508 and r(d.S_DOG) == 2.48 and r(d.FB["off"][2], 4) == -0.0554
assert r(d.FB["test"], 2) == 4.0 and r(d.FG["test"], 1) == 23.2 and r(10 / 121, 4) == 0.0826
assert d.MIN14 == [(17, 31), (24, 31), (17, 38), (24, 38)] and r(d.C14, 2) == -9.66
assert abs(d.C14T - d.D7[2][d.CY][d.CX]) < 1e-9
KD, KP = d.KP7D[0], d.KP7P[0]
assert (r(KD["pt"][0], 2), r(KD["pt"][1], 2), r(KD["size"], 2)) == (10.23, 17.25, 5.02)
assert (r(KP["pt"][0], 2), r(KP["pt"][1], 2), r(KP["size"], 2)) == (9.98, 17.0, 5.03)
_b5, _b7 = d.box1d(d.BOXF, 5), d.box1d(d.BOXF, 7)
assert (r(_b5[3], 2), r(_b7[3], 2)) == (4.4, 4.43)


def fv(v, nd=2):
    return f"{v:.{nd}f}".replace("-", "−")


def blend(rgb, a, paper=(255, 255, 255)):
    rr, gg, bb = (round(a * c + (1 - a) * p) for c, p in zip(rgb, paper))
    return f"#{rr:02x}{gg:02x}{bb:02x}"


def dog_fill(v, vmax=36.0):
    t = min(1.0, abs(v) / vmax)
    return blend((46, 90, 168) if v < 0 else (122, 131, 153), 0.04 + 0.86 * t)


def dog_map(x0, y0, side, M):
    """A DoG level as a map, run-length rects with opaque fills so no seams show."""
    n = len(M)
    cs = side / n
    out = ""
    for i, row in enumerate(M):
        j = 0
        while j < n:
            f = dog_fill(row[j])
            k = j + 1
            while k < n and dog_fill(row[k]) == f:
                k += 1
            out += (f'<rect x="{x0 + j * cs:.2f}" y="{y0 + i * cs:.2f}" width="{(k - j) * cs + 0.5:.2f}" '
                    f'height="{cs + 0.5:.2f}" fill="{f}" shape-rendering="crispEdges"/>')
            j = k
    out += (f'<rect x="{x0}" y="{y0}" width="{side}" height="{side}" fill="none" '
            f'stroke="rgba(45,49,66,0.55)" stroke-width="1.5"/>')
    return out


def mark(x0, y0, side, n, u, v, rad=13, sw=4):
    """Ring a continuous point (u, v); pixel centres sit at integers."""
    cs = side / n
    cx, cy = x0 + (u + 0.5) * cs, y0 + (v + 0.5) * cs
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad}" fill="none" stroke="#ffffff" stroke-width="{sw + 3}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rad}" fill="none" stroke="{ACCENT}" stroke-width="{sw}"/>')


def dog_legend(x, y):
    out = ""
    for k, (v, lab) in enumerate(((-30, "below zero"), (12, "above zero"))):
        xx = x + k * 230
        out += (f'<rect x="{xx}" y="{y - 17}" width="22" height="22" fill="{dog_fill(v)}" '
                f'stroke="rgba(45,49,66,0.35)"/>')
        out += mono(xx + 34, y, lab, 18, MUTED)
    return out


# ------------------------------------------------------------------ feed
FEED_TOTAL = 8


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    side, top = 260, 576
    panels = [(110, d.FIX7, "×7, σ 2.540 → 3.200", [(d.CX, d.CY)], ["one well,", "−35.38 at the centre"]),
              (410, d.FIX14, "×14, the same σ", d.MIN14, ["four wells, −20.43;", "the centre −9.66"]),
              (710, d.TWICE14, "×14, σ doubled", [(20.5, 34.5)], ["one well again,", "−35.38 at the centre"])]
    v += mono(110, 532, "one DoG level on the patch at ×7, then at ×14", 17, SOFT, "start", 600)
    for x0, M, head, pts, notes in panels:
        n = len(M)
        v += mono(x0, top - 16, head, 18, INK, "start", 600)
        v += dog_map(x0, top, side, M)
        for u, w in pts:
            v += mark(x0, top, side, n, u, w, *((13, 4) if n == 35 else (10, 4) if len(pts) == 1 else (7, 2.5)))
        v += mono(x0, top + side + 40, notes[0], 19, ACCENT if x0 == 410 else INK, "start", 600)
        v += mono(x0, top + side + 70, notes[1], 19, ACCENT if x0 == 410 else INK, "start", 600)
    v += dog_legend(110, 1000)
    v += mono(110, 1050, "searched, the ×14 square returns: size 10.03 against 5.03", 19, LINK, "start", 600)
    v += mono(110, 1094, "closed form at pixel centres; worked by hand, not run", 17, SOFT)
    emit(1, "sigma-is-a-search-dimension",
         ["σ is a search", "dimension."],
         ["Fix σ and the answer depends on the zoom:",
          "the same square, enlarged twice as much."],
         v,
         ["A fixed σ sees one size. Search σ, and only",
          "the reported size changes."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 532, "the five DoG levels of the ×7 patch", 17, SOFT, "start", 600)
    side, top = 150, 590
    for i in range(5):
        x0 = 110 + i * 172
        hi = i == 2
        v += mono(x0, top - 16, f"D{i}", 20, ACCENT if hi else INK, "start", 600)
        v += dog_map(x0, top, side, d.D7[i])
        if hi:
            v += mark(x0, top, side, 35, d.CX, d.CY, 10)
        v += mono(x0 + side / 2, top + side + 34, f"σ {d.SIG[i]:.2f}→{d.SIG[i + 1]:.2f}", 15, SOFT, "middle")
        v += mono(x0 + side / 2, top + side + 70, fv(d.D7[i][d.CY][d.CX]), 21,
                  ACCENT if hi else INK, "middle", 600)
    yb = top + side + 100
    x1, x3 = 110 + 172, 110 + 3 * 172 + side
    v += (f'<path d="M {x1} {yb} V {yb + 12} H {x3} V {yb}" fill="none" stroke="{MUTED}" stroke-width="2"/>')
    v += mono((x1 + x3) / 2, yb + 42, "searched: D1 to D3, each has a level above and below", 17, MUTED, "middle")
    v += mono(110, 948, "the square's centre, (10, 17), is deepest on D2:", 20, INK, "start", 600)
    v += mono(110, 982, "−35.38, below −32.22 on D1 and −31.42 on D3", 20, INK, "start", 600)
    v += mono(110, 1040, "six blurs at σ = 1.6 × 2^(i/3); three intervals per octave", 18, MUTED)
    v += mono(110, 1094, "closed form at pixel centres; worked by hand, not run", 17, SOFT)
    emit(2, "six-blurs-five-differences",
         ["Six blurs,", "five differences."],
         ["One octave on the 5×5 patch enlarged seven",
          "times: a square of 255 beside a step."],
         v,
         ["Subtract neighbouring blurs and the square",
          "becomes a well, deepest at its own scale."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 532, "the 3×3×3 block around (10, 17) on level 2", 17, SOFT, "start", 600)
    cw, top = 84, 600
    lo, hi_ = -27.5, -35.4
    for g, lev in enumerate((1, 2, 3)):
        x0 = 110 + g * 292
        v += mono(x0, top - 18, f"level {lev} · σ {d.SIG[lev]:.3f}", 17, ACCENT if lev == 2 else INK, "start", 600)
        for yy in range(3):
            for xx in range(3):
                val = d.BLOCK[g][yy][xx]
                t = max(0.0, min(1.0, (lo - val) / (lo - hi_)))
                f = blend((46, 90, 168), 0.06 + 0.40 * t)
                centre = g == 1 and yy == 1 and xx == 1
                v += (f'<rect x="{x0 + xx * cw}" y="{top + yy * cw}" width="{cw}" height="{cw}" fill="{f}" '
                      f'stroke="rgba(45,49,66,0.35)" stroke-width="1.5"/>')
                v += mono(x0 + xx * cw + cw / 2, top + yy * cw + cw / 2 + 6, fv(val, 3), 16,
                          INK, "middle", 600)
        if lev == 2:
            v += (f'<rect x="{x0 + cw}" y="{top + cw}" width="{cw}" height="{cw}" fill="none" '
                  f'stroke="{ACCENT}" stroke-width="5"/>')
        v += mono(x0 + 1.5 * cw, top + 3 * cw + 30, "x = 9 · 10 · 11", 15, SOFT, "middle")
    v += mono(110, 948, "−35.379 is below all 26 others; the closest,", 20, INK, "start", 600)
    v += mono(110, 980, "−33.223, sits one pixel to its left", 20, INK, "start", 600)
    v += mono(110, 1036, "over the whole octave, two samples pass: (10, 17),", 18, MUTED)
    v += mono(110, 1066, "the square, and (17, 17), between square and step", 18, MUTED)
    v += mono(110, 1104, "closed form at pixel centres; worked by hand, not run", 17, SOFT)
    emit(3, "lower-than-all-26-neighbours",
         ["Lower than all", "26 neighbours."],
         ["The candidate test compares a sample with its",
          "neighbours in x, y and the levels either side."],
         v,
         ["Every one of the 26 comparisons goes",
          "the same way: (10, 17) is a candidate."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 532, "the DoG at the square's centre, along scale; filled: the samples fitted", 17, SOFT, "start", 600)
    px0, px1, py0, py1 = 190, 950, 570, 880
    u0, u1, dlo, dhi = -0.25, 4.25, -37.0, -19.0
    X = lambda u: px0 + (u - u0) / (u1 - u0) * (px1 - px0)
    Y = lambda val: py0 + (dhi - val) / (dhi - dlo) * (py1 - py0)
    for val in (-35, -30, -25, -20):
        v += hline(px0, px1, f"{Y(val):.1f}", RULE)
        v += mono(px0 - 14, Y(val) + 6, fv(val, 0), 16, SOFT, "end")
    v += hline(px0, px1, py1, RULE_SOLID, 2)
    for i in range(5):
        v += vline(X(i), py1, py1 + 10, RULE_SOLID, 2)
        v += mono(X(i), py1 + 34, f"level {i}", 15, SOFT, "middle")
        v += mono(X(i), py1 + 58, f"σ {d.SIG[i]:.3f}", 15, SOFT, "middle")
    cont = [(u / 20, d.D_CONT(1.6 * 2 ** (u / 60))) for u in range(0, 81)]
    v += ('<polyline points="' + " ".join(f"{X(u):.1f},{Y(val):.1f}" for u, val in cont) +
          f'" fill="none" stroke="{SOFT}" stroke-width="3"/>')
    D1, D2, D3 = (d.D7[i][d.CY][d.CX] for i in (1, 2, 3))
    g1, h1 = (D3 - D1) / 2, D3 + D1 - 2 * D2
    par = [(1.4 + k / 25, D2 + g1 * (1.4 + k / 25 - 2) + 0.5 * h1 * (1.4 + k / 25 - 2) ** 2) for k in range(31)]
    v += ('<polyline points="' + " ".join(f"{X(u):.1f},{Y(val):.1f}" for u, val in par) +
          f'" fill="none" stroke="{ACCENT}" stroke-width="4" stroke-dasharray="12,7"/>')
    for i in range(5):
        val = d.D7[i][d.CY][d.CX]
        v += (f'<circle cx="{X(i):.1f}" cy="{Y(val):.1f}" r="9" fill="{INK if i in (1, 2, 3) else "#ffffff"}" '
              f'stroke="{INK}" stroke-width="3"/>')
    uf = 2 + d.FB["off"][2]
    v += vline(X(uf), 760, Y(d.FB["contr"]) - 14, ACCENT, 2.5, "5,5")
    v += (f'<circle cx="{X(uf):.1f}" cy="{Y(d.FB["contr"]):.1f}" r="13" fill="none" stroke="{ACCENT}" '
          f'stroke-width="4"/>')
    v += mono(X(uf), 714, f"fit: σ {d.FB['sigma']:.3f}", 19, ACCENT, "middle", 600)
    v += mono(X(uf), 742, "0.055 of a level below 2", 17, ACCENT, "middle")
    v += mono(X(2.55), 600, "closed-form curve (grey):", 17, SOFT, "start", 600)
    v += mono(X(2.55), 626, f"its minimum at σ {d.S_DOG:.3f}", 17, SOFT, "start")
    v += mono(110, 1004, "offset in (x, y, level): (−0.0193, 0, −0.0554)", 20, INK, "start", 600)
    v += mono(110, 1038, "value at the fit −35.391, or 0.139 on 0 to 1", 19, MUTED)
    v += mono(110, 1070, "Lowe's contrast threshold is 0.03: kept", 19, MUTED)
    v += mono(110, 1104, "closed form at pixel centres; worked by hand, not run", 17, SOFT)
    emit(4, "scale-is-refined-like-position",
         ["Scale is refined", "like position."],
         ["A quadratic fit through the 3×3×3 block puts",
          "the extremum between samples, in σ too."],
         v,
         ["The keypoint's σ is 2.508, 1% from the",
          "continuous curve's own minimum."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 532, "Tr²/Det of the DoG's 2×2 Hessian in x and y", 17, SOFT, "start", 600)
    ax0, ax1, ay = 150, 930, 820
    X = lambda q: ax0 + q / 30 * (ax1 - ax0)
    band_top = 640
    v += (f'<rect x="{X(4):.1f}" y="{band_top}" width="{X(12.1) - X(4):.1f}" height="{ay - band_top}" '
          f'fill="{ACCENT_TINT}"/>')
    v += (f'<rect x="{X(12.1):.1f}" y="{band_top}" width="{X(25) - X(12.1):.1f}" height="{ay - band_top}" '
          f'fill="rgba(46,90,168,0.06)"/>')
    v += mono(X(4) + 14, band_top + 32, "SIFT keeps", 18, ACCENT, "start", 600)
    v += mono(X(12.1) + 14, band_top + 32, "Harris, k = 0.04, keeps too", 18, LINK, "start", 600)
    v += hline(ax0, ax1, ay, RULE_SOLID, 3)
    for q in (0, 10, 20, 30):
        v += vline(X(q), ay, ay + 12, RULE_SOLID, 3)
        v += mono(X(q), ay + 40, str(q), 18, SOFT, "middle")
    v += vline(X(12.1), band_top - 20, ay, ACCENT, 4)
    v += vline(X(25), band_top - 20, ay, LINK, 4, "12,8")
    v += mono(X(12.1), ay + 80, "SIFT, r = 10: 12.1", 18, ACCENT, "middle", 600)
    v += mono(X(12.1), ay + 106, "k = 10/121 = 0.0826", 16, ACCENT, "middle")
    v += mono(X(25), ay + 80, "Harris: 25", 18, LINK, "middle", 600)
    v += mono(X(25), ay + 106, "k = 0.04", 16, LINK, "middle")
    for q, who, val in ((d.FB["test"], "the square", "4.00"), (d.FG["test"], "the gap", "23.2")):
        v += (f'<circle cx="{X(q):.1f}" cy="{ay - 46}" r="12" fill="{INK}" stroke="#ffffff" stroke-width="3"/>')
        v += mono(X(q), ay - 104, who, 18, INK, "middle", 600)
        v += mono(X(q), ay - 78, val, 18, INK, "middle", 600)
    v += mono(110, 1004, "the square: Dxx 4.510, Dyy 4.420, a round bowl", 19, INK, "start", 600)
    v += mono(110, 1036, "the gap: Dxx −3.804, Dyy −0.180, a ridge; rejected", 19, ACCENT, "start", 600)
    v += mono(110, 1074, "4 is the floor: two equal curvatures", 17, MUTED)
    v += mono(110, 1104, "closed form at pixel centres; worked by hand, not run", 17, SOFT)
    emit(5, "the-edge-test-is-a-stricter-harris",
         ["The edge test is", "a stricter Harris."],
         ["Lowe's Tr²/Det < 12.1 is Harris's sign test",
          "with k = 0.0826, on the DoG's Hessian."],
         v,
         ["The gap point would pass Harris at 0.04.",
          "SIFT's edge test is what removes it."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 532, "three kernels against the requirements that differ", 17, SOFT, "start", 600)
    cols = [("semi-", "group"), ("rotation-", "invariant"), ("non-enhance-", "ment"), ("separable", "")]
    rows = [("Gaussian", ["yes", "yes", "yes", "yes"]),
            ("Poisson", ["yes", "yes", "no", "no"]),
            ("box", ["no", "no", "no", "yes"])]
    x0, cw0, cw, y0 = 110, 220, 160, 590
    for j, (a, b) in enumerate(cols):
        xc = x0 + cw0 + j * cw + cw / 2
        v += mono(xc, y0, a, 17, INK, "middle", 600)
        if b:
            v += mono(xc, y0 + 24, b, 17, INK, "middle", 600)
    v += hline(x0, x0 + cw0 + 4 * cw - 30, y0 + 46, RULE_SOLID, 2)
    for i, (name, vals) in enumerate(rows):
        y = y0 + 100 + i * 72
        v += txt(x0, y + 8, name, 26, INK, SANS, 600)
        for j, val in enumerate(vals):
            xc = x0 + cw0 + j * cw + cw / 2
            if val == "yes":
                v += f'<circle cx="{xc - 26:.1f}" cy="{y:.1f}" r="8" fill="{INK}"/>'
                v += mono(xc - 10, y + 7, "yes", 19, INK, "start")
            else:
                v += (f'<path d="M {xc - 34:.1f} {y - 8:.1f} L {xc - 18:.1f} {y + 8:.1f} M {xc - 18:.1f} {y - 8:.1f} '
                      f'L {xc - 34:.1f} {y + 8:.1f}" stroke="{ACCENT}" stroke-width="4" stroke-linecap="round"/>')
                v += mono(xc - 10, y + 7, "no", 19, ACCENT, "start", 600)
    xn = x0 + cw0 + 2 * cw
    v += (f'<rect x="{xn + 6}" y="{y0 - 30}" width="{2 * cw - 12}" height="{100 + 2 * 72 + 64}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="2.5" stroke-dasharray="10,6" rx="6"/>')
    v += mono(xn + 2 * cw - 6, y0 + 100 + 2 * 72 + 64, "either one leaves only the Gaussian", 16, ACCENT, "end", 600)
    v += mono(110, 994, "all three are linear, shift- and scale-invariant", 18, MUTED)
    v += mono(110, 1024, "and positive (Felsberg & Sommer, for Poisson)", 18, MUTED)
    v += mono(110, 1064, "box: on 2 9 1 4 1 7 7 7 6, a peak of 4.40", 18, INK, "start", 600)
    v += mono(110, 1094, "rises to 4.43 when the box widens from 5 to 7", 18, INK, "start", 600)
    emit(6, "why-only-the-gaussian",
         ["Why only the", "Gaussian may search."],
         ["Blurring more must never invent structure.",
          "Which requirement rules each kernel out?"],
         v,
         ["Non-enhancement or separability leaves",
          "only the Gaussian. Without both, Poisson fits."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 532, "the 3×3 pixels around the square's centre, ×7 patch", 17, SOFT, "start", 600)
    cell, gx, gy = 112, 150, 600
    P = lambda u, w: (gx + (u - 8.5) * cell, gy + (w - 15.5) * cell)
    for j in range(3):
        for i in range(3):
            v += (f'<rect x="{gx + i * cell}" y="{gy + j * cell}" width="{cell}" height="{cell}" fill="#ffffff" '
                  f'stroke="rgba(45,49,66,0.30)" stroke-width="1.5"/>')
            cx, cy = P(9 + i, 16 + j)
            v += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.5" fill="{RULE_SOLID}"/>'
        v += mono(gx + j * cell + cell / 2, gy - 14, str(9 + j), 16, SOFT, "middle")
        v += mono(gx - 14, gy + j * cell + cell / 2 + 6, str(16 + j), 16, SOFT, "end")
    cx, cy = P(10, 17)
    v += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="22" fill="none" stroke="{INK}" stroke-width="3"/>'
    px_, py_ = P(KP["pt"][0], KP["pt"][1])
    v += f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="9" fill="{LINK}"/>'
    qx, qy = P(KD["pt"][0], KD["pt"][1])
    v += (f'<path d="M {qx - 12:.1f} {qy - 12:.1f} L {qx + 12:.1f} {qy + 12:.1f} M {qx + 12:.1f} {qy - 12:.1f} '
          f'L {qx - 12:.1f} {qy + 12:.1f}" stroke="{ACCENT}" stroke-width="5" stroke-linecap="round"/>')
    tx = 560
    v += mono(tx, 612, "cv2.SIFT_create(), the default", 18, MUTED)
    v += mono(tx, 646, "× (10.23, 17.25), size 5.02", 21, ACCENT, "start", 600)
    v += mono(tx, 718, "enable_precise_upscale=True", 18, MUTED)
    v += mono(tx, 752, "● (9.98, 17.00), size 5.03", 21, LINK, "start", 600)
    v += mono(tx, 824, "○ the square's centre, (10, 17)", 19, INK, "start", 600)
    v += mono(110, 994, "resize maps output pixel j to input j/2 − 0.25;", 19, INK, "start", 600)
    v += mono(110, 1026, "halving keeps the even pixels: +0.25 px in x and y", 19, INK, "start", 600)
    v += mono(110, 1064, "the −0.02 px left after the fix is real: the step's pull", 17, MUTED)
    v += mono(110, 1094, "OpenCV's rules replayed in plain Python; not run", 17, SOFT)
    emit(7, "a-quarter-pixel-by-default",
         ["OpenCV's SIFT is off", "by a quarter pixel."],
         ["By default it doubles the image with resize,",
          "and every keypoint lands +0.25 px out."],
         v,
         ["Pass enable_precise_upscale=True,",
          "added in OpenCV 4.8, and the shift goes."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("why search σ", "a fixed σ sees one size", "the ×14 square splits into four corner wells"),
             ("the octave", "26 neighbours in x, y and σ", "one blob kept, σ = 2.508, offsets fitted"),
             ("the edge test", "Harris's ratio test, k = 0.0826", "the gap point fails, 23.2 against 12.1"),
             ("the Gaussian", "non-enhancement or separability", "without both, the Poisson kernel passes")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "the Gaussian" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit(8, "read-the-article",
         ["Scale space and SIFT,", "by hand."],
         ["Why σ is searched, and why only the",
          "Gaussian may search it."],
         v,
         ["The full walk-through, every number worked",
          "by hand, and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
