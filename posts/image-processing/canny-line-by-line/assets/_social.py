#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Canny Edge Detection, Line by Line".

Image Processing by Hand, part 8. The shell (lockup, rule, serif title, deck, takeaway,
footer) is copied from part 7's _social.py, with the lockup reading "canery.in". Every
number on a card comes from `_figs.py` — the Sobel gradient, OpenCV's suppression rule
with each norm, the tie rules, hysteresis before and after the shared Gaussian, and the
noise model — so a card cannot disagree with the article. Pixel cells follow the
article: high value = bright.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
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
import _figs as F  # noqa: E402  — the article's numbers and conventions

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
GREEN, BLUE, MUSTARD, BROWN, VIOLET = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50", "#8e7aa6"
LINK = "#2e5aa8"                            # the figures' blue, so cards and figures match
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/canny-line-by-line"
FOOTER = "CANNY, LINE BY LINE · CANERY.IN"

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
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def pixel(x, y, w, h, v, size=30, hi=False):
    """One pixel cell, high value = bright, as in the article."""
    shade = 0.85 * (1 - (v - 40) / 215) + 0.04
    out = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
           f'fill="rgba(45,49,66,{shade:.3f})" stroke="{ACCENT if hi else "rgba(45,49,66,0.35)"}" '
           f'stroke-width="{4 if hi else 1.5}"/>')
    shown = f"{int(round(v))}" if abs(v - round(v)) < 1e-9 else f"{v:.2f}"
    out += mono(x + w / 2, y + h / 2 + size * 0.36, shown,
                size, "#ffffff" if v < 120 else INK, "middle", 600)
    return out


def pixel_row(x, y, cw, ch, values, size=30, hi=None, labels=True):
    out = ""
    for i, v in enumerate(values):
        out += pixel(x + i * cw, y, cw, ch, v, size, hi is not None and i in hi)
        if labels:
            out += label(x + i * cw + cw / 2, y + ch + 30, f"c{i}", SOFT, "middle", 15)
    return out


# ------------------------------------------------------------------ the shell
def shell(kind, number, total, title, deck, visual, takeaway, cta=None):
    if kind == "feed":
        height, logo_y, logo_w = 1350, 72, 220
        rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
        deck_y = title_y + len(title) * title_gap + 20
        take_rule, take_y, foot_y = 1168, 1220, 1305
    else:
        height, logo_y, logo_w = 1920, 250, 245
        rule_y, title_y, title_size, title_gap = 340, 470, 70, 80
        deck_y = title_y + len(title) * title_gap + 28
        take_rule, take_y, foot_y = 1505, 1570, 1665
    scale = logo_w / LOCKUP_FULL_W
    defs = f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style></defs>'
    body = f'<rect width="{VW}" height="{height}" fill="{PAPER}"/>'
    body += (f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
             f'data-logo-width="{logo_w}" fill="{INK}" '
             f'transform="translate(72 {logo_y}) scale({scale})">{LOGO_PATHS}</g>')
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", SOFT, "end", 15)
    body += hline(72, 1008, rule_y)
    body += lines(72, title_y, title, title_size, SERIF, gap=title_gap)
    body += lines(72, deck_y, deck, 22 if kind == "feed" else 26, fill=MUTED,
                  gap=30 if kind == "feed" else 36)
    body += visual
    body += hline(72, 1008, take_rule)
    body += lines(72, take_y, takeaway, 22 if kind == "feed" else 27, weight=600,
                  gap=30 if kind == "feed" else 36)
    body += label(72, foot_y, cta or FOOTER, ACCENT if cta else SOFT, "start",
                  14 if kind == "feed" else 16)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {height}" '
            f'width="{VW}" height="{height}" role="img">\n{defs}\n{body}\n</svg>')


def emit(kind, number, slug, title, deck, visual, takeaway, total, cta=None):
    svg = shell(kind, number, total, title, deck, visual, takeaway, cta)
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(" ".join(title))}</title><link href="{FONTS.replace("&", "&amp;")}" rel="stylesheet">'
            f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style>'
            f'</head><body>{svg}</body></html>')
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{kind}-{number:02d}-{slug}.html"
    path.write_text(page, encoding="utf-8")
    print(path.name)





# ------------------------------------------------------------------ the numbers
M2, M1 = F.M2, F.M1
KEEP1, KEEP2 = F.KEEP1, F.KEEP2
LINE2, LINE1, RING = F.LINE2, F.LINE1, F.RING
RAW_OUT = F.hysteresis(KEEP2, M2, 180, 450)
SM_OUT = F.hysteresis(F.SKEEP2, F.SM2, 180, 450)
SM_DROPPED = F.SKEEP2 - SM_OUT
assert RAW_OUT == KEEP2 and len(RAW_OUT) == 10 and SM_OUT == F.COL and SM_DROPPED == {(1, 0), (3, 0)}
assert F.hysteresis(KEEP1, M1, 450, 600) == LINE1 and len(F.hysteresis(KEEP1, M1, 200, 600)) == 8
assert (F.GX[1][2], F.GY[1][2], M1[1][2], round(M2[1][2], 1)) == (425, 215, 640, 476.3)
assert (round(F.S_NOISE, 2), round(F.TH, 1), round(F.TL, 1), round(F.TH / 4, 1)) == (6.93, 29.7, 14.9, 7.4)
assert [round(v, 1) for v in F.SM2[1]][:2] == [219.7, 222.2] and round(F.SM2[2][3], 1) == 408.8


def fv(v, nd=1):
    s = f"{int(round(v))}" if abs(v - round(v)) < 1e-9 else f"{v:.{nd}f}"
    return s.replace("-", "−")


def shaded(x, y, w, h, t, stroke="rgba(45,49,66,0.35)", sw=1.5):
    t = max(0.0, min(1.0, t))
    a = 0.85 * (1 - t) + 0.04
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"/>')


def vcell(x, y, w, h, val, size=24, ring=False, hi=255.0):
    t = val / hi
    v = shaded(x, y, w, h, t, ACCENT if ring else "rgba(45,49,66,0.35)", 4 if ring else 1.5)
    return v + mono(x + w / 2, y + h / 2 + size * 0.36, fv(val), size,
                    "#ffffff" if t < 0.52 else INK, "middle", 600)


def patch5(x, y, cw, size=20):
    return "".join(vcell(x + j * cw, y + i * cw, cw, cw, F.PATCH[i][j], size, (i, j) == (2, 1))
                   for i in range(5) for j in range(5))


def result5(x, y, cw, keep, M, line, size=18, hollow=(), show=True):
    """Edge pixels: the step's line in blue, impulse pixels in orange, the rest blank."""
    out = ""
    for i in range(5):
        for j in range(5):
            xx, yy = x + j * cw, y + i * cw
            p = (i, j)
            if p in keep:
                col = LINK if p in line else ACCENT
                out += (f'<rect x="{xx}" y="{yy}" width="{cw}" height="{cw}" fill="{col}" fill-opacity="0.88" '
                        f'stroke="{col}" stroke-width="1.5"/>')
                if show:
                    out += mono(xx + cw / 2, yy + cw / 2 + size * 0.36, fv(M[i][j]), size, "#ffffff", "middle", 600)
            elif p in hollow:
                out += (f'<rect x="{xx + 1.5}" y="{yy + 1.5}" width="{cw - 3}" height="{cw - 3}" fill="#ffffff" '
                        f'stroke="{SOFT}" stroke-width="2.4" stroke-dasharray="6,4"/>')
                if show:
                    out += mono(xx + cw / 2, yy + cw / 2 + size * 0.36, fv(M[i][j]), size, SOFT, "middle", 600)
            else:
                out += (f'<rect x="{xx}" y="{yy}" width="{cw}" height="{cw}" fill="#ffffff" '
                        f'stroke="rgba(45,49,66,0.22)" stroke-width="1.2"/>')
    return out


def tie_row(x, y, cw, kept, size=22):
    out = ""
    for c, v in enumerate([0, 0, 640, 640, 0]):
        xx = x + c * cw
        if c in kept:
            out += (f'<rect x="{xx}" y="{y}" width="{cw}" height="{cw}" fill="{LINK}" fill-opacity="0.88" '
                    f'stroke="{LINK}" stroke-width="1.5"/>')
            out += mono(xx + cw / 2, y + cw / 2 + size * 0.36, str(v), size, "#ffffff", "middle", 600)
        else:
            dash = ' stroke-dasharray="6,4"' if v else ""
            out += (f'<rect x="{xx}" y="{y}" width="{cw}" height="{cw}" fill="#ffffff" '
                    f'stroke="{SOFT if v else "rgba(45,49,66,0.22)"}" stroke-width="{2 if v else 1.2}"{dash}/>')
            out += mono(xx + cw / 2, y + cw / 2 + size * 0.36, str(v), size, SOFT, "middle", 500)
    return out


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "the patch", 17, SOFT, "start", 600)
    v += patch5(110, 562, 70)
    v += mono(600, 540, "cv2.Canny, defaults: L1", 17, ACCENT, "start", 600)
    v += result5(600, 562, 70, KEEP1, M1, LINE1, 18)
    v += mono(110, 970, "low 430 or more: three separate dots", 22, LINK, "start", 600)
    v += mono(110, 1010, "low below 430: the dots and a ring of five", 22, ACCENT, "start", 600)
    v += mono(110, 1050, "high at 640 or more: nothing at all", 20, MUTED)
    emit("feed", 1, "every-threshold-pair-fails",
         ["Every threshold pair", "fails this edge."],
         ["cv2.Canny, defaults, on one 5×5 patch:",
          "a clean step of 160 and one bright pixel."],
         v,
         ["The thresholds were not the problem.",
          "What they were compared with was."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "Sobel magnitude, L2, replicate border", 17, SOFT, "start", 600)
    cw = 84
    for i in range(5):
        for j in range(5):
            v += vcell(110 + j * cw, 562 + i * cw, cw, cw, M2[i][j], 18, (i, j) == (2, 1), hi=640.0)
    nx = 590
    v += mono(nx, 600, "the step: 4 × 160 = 640", 22, LINK, "start", 600)
    v += mono(nx, 636, "on c2 and c3 at once", 20, MUTED)
    v += mono(nx, 700, "the 255 itself: 0", 22, ACCENT, "start", 600)
    v += mono(nx, 736, "left and right cancel,", 20, MUTED)
    v += mono(nx, 768, "so do above and below", 20, MUTED)
    v += mono(nx, 832, "around it: 210 to 476.3", 22, INK, "start", 600)
    v += mono(110, 1050, "magnitude cells shaded high = bright, 640 the brightest", 18, SOFT)
    emit("feed", 2, "the-bright-pixel-has-no-gradient",
         ["The bright pixel", "has no gradient."],
         ["Sobel on the raw patch, as cv2.Canny",
          "computes it: no smoothing first."],
         v,
         ["A bright pixel becomes a ring of",
          "edge candidates around a zero."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "row r1, columns c0 to c4", 17, SOFT, "start", 600)
    cw = 120
    v += mono(110, 596, "L2", 22, LINK, "start", 600)
    for row_y, M, keep in ((568, M2, KEEP2), (708, M1, KEEP1)):
        for j in range(5):
            x = 170 + j * cw
            p = (1, j)
            if p in keep:
                col = LINK if p in LINE2 else ACCENT
                v += (f'<rect x="{x}" y="{row_y}" width="{cw}" height="90" fill="{col}" fill-opacity="0.88" '
                      f'stroke="{col}"/>')
                v += mono(x + cw / 2, row_y + 54, fv(M[1][j]), 24, "#ffffff", "middle", 600)
            elif M is M1 and j in (2, 3):
                v += (f'<rect x="{x + 1.5}" y="{row_y + 1.5}" width="{cw - 3}" height="87" fill="#ffffff" '
                      f'stroke="{ACCENT}" stroke-width="3" stroke-dasharray="8,5"/>')
                v += mono(x + cw / 2, row_y + 54, fv(M[1][j]), 24, ACCENT, "middle", 600)
            else:
                v += (f'<rect x="{x}" y="{row_y}" width="{cw}" height="90" fill="#ffffff" '
                      f'stroke="rgba(45,49,66,0.28)"/>')
                v += mono(x + cw / 2, row_y + 54, fv(M[1][j]), 24, INK if j == 2 else SOFT, "middle", 600)
    v += mono(110, 736, "L1", 22, ACCENT, "start", 600)
    v += mono(110, 840, "orange: the bright pixel's ring, kept either way", 18, SOFT)
    v += mono(110, 900, "(r1, c2): Gx 425, Gy 215", 22, INK, "start", 600)
    v += mono(110, 940, "L2 √(425² + 215²) = 476.3 → (r1, c3) wins", 22, LINK, "start", 600)
    v += mono(110, 980, "L1 425 + 215 = 640: a tie, and both lose", 22, ACCENT, "start", 600)
    v += mono(110, 1050, "the same happens on row r3", 20, MUTED)
    emit("feed", 3, "one-tie-two-lost-rows",
         ["One tie,", "two lost rows."],
         ["OpenCV's default magnitude is L1, |Gx| + |Gy|.",
          "On an oblique gradient it reads high."],
         v,
         ["L2gradient=True keeps the edge",
          "on every row of the patch."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    rules = [("strict on both sides", [], "no pixel: the edge vanishes", ACCENT),
             ("OpenCV: > before, ≥ after", [2], "one pixel, the left of the pair", LINK),
             ("scikit-image: ≥ on both sides", [2, 3], "two pixels: a double-width edge", LINK)]
    y = 540
    for head, kept, verdict, col in rules:
        v += mono(110, y, head, 20, INK, "start", 600)
        v += tie_row(110, y + 18, 80, kept, 20)
        v += mono(540, y + 66, verdict, 20, col, "start", 600)
        y += 178
    emit("feed", 4, "zero-one-or-two-pixels",
         ["Zero, one or", "two pixels."],
         ["The step falls between c2 and c3, so Sobel reads",
          "640 on both. Three tie rules, three answers."],
         v,
         ["On an edge between pixels,",
          "the tie rule decides what you get."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "raw patch, L2", 17, ACCENT, "start", 600)
    v += result5(110, 562, 70, RAW_OUT, M2, LINE2, 17)
    v += mono(600, 540, "after the 3×3 Gaussian", 17, LINK, "start", 600)
    v += result5(600, 562, 70, SM_OUT, F.SM2, F.COL, 15, hollow=SM_DROPPED)
    v += mono(110, 970, "raw: the ring touches the line at a corner,", 22, ACCENT, "start", 600)
    v += mono(110, 1004, "so all 10 pixels come out", 22, ACCENT, "start", 600)
    v += mono(110, 1050, "smoothed: two lone 219.7s have no seed: 5 out", 22, LINK, "start", 600)
    emit("feed", 5, "chains-not-pixels",
         ["Hysteresis grades", "chains, not pixels."],
         ["High 450, low 180, a ratio of 2.5,",
          "before and after smoothing."],
         v,
         ["High decides which chains exist.",
          "Low decides where each one ends."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 544, "to get the step alone", SOFT, "start", 14)
    rows = [("cv2.Canny defaults, raw (L1)", "no pair works", ACCENT),
            ("raw, L2gradient=True", "high ÷ low under 1.49", ACCENT),
            ("3×3 Gaussian first, L2", "high 219.7 to 474.9,", LINK),
            ("", "low under 408.8", LINK)]
    y = 610
    for k, (a, b, col) in enumerate(rows):
        if a:
            v += hline(110, 970, y - 42, RULE)
            v += txt(110, y, a, 24, INK, SANS, 600)
        v += mono(600, y if a else y - 56, b, 22, col, "start", 600)
        y += 92 if a else 0
    v += hline(110, 970, 900, RULE)
    v += txt(110, 952, "Canny's own ratio: 2 to 3", 24, INK, SANS, 600)
    v += mono(600, 952, "fits only the last", 22, LINK, "start", 600)
    v += mono(110, 1050, "smoothing detaches the ring from the step", 20, MUTED)
    emit("feed", 6, "smooth-first",
         ["Smooth first, and", "the ratio works."],
         ["What it takes to get the step's line",
          "alone, on each version of the patch."],
         v,
         ["cv2.Canny does not smooth.",
          "The Gaussian is yours to add."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "high = s √(2 ln(1/α)),  s = √12 σ", 26, INK, "start", 600)
    v += mono(110, 604, "flat-region magnitude is Rayleigh with scale s", 19, SOFT)
    pts = []
    x0, y0, w, h = 130, 650, 520, 200
    s_ = F.S_NOISE
    f = lambda m: m / s_ ** 2 * math.exp(-m * m / (2 * s_ * s_))
    for k in range(201):
        m = 60 * k / 200
        pts.append(f"{x0 + m / 60 * w:.1f},{y0 + h - f(m) / 0.09 * h:.1f}")
    v += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1.5"/>'
    v += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="4"/>'
    for m, col, lab in ((F.TL, BLUE, "low 14.9"), (F.TH, LINK, "high 29.7")):
        xx = x0 + m / 60 * w
        v += f'<line x1="{xx:.1f}" y1="{y0}" x2="{xx:.1f}" y2="{y0 + h}" stroke="{col}" stroke-width="3" stroke-dasharray="8,6"/>'
        v += mono(xx + 10, y0 + 24, lab, 19, col, "start", 600)
    v += mono(x0 + w, y0 + h + 30, "gradient magnitude, σ = 2", 17, SOFT, "end")
    v += mono(700, 700, "α = 1 in 10,000", 22, LINK, "start", 600)
    v += mono(700, 740, "→ high 29.7", 22, LINK, "start", 600)
    v += mono(700, 800, "low = high ÷ 2", 22, BLUE, "start", 600)
    v += mono(700, 840, "→ 1 flat pixel", 20, MUTED)
    v += mono(700, 870, "   in 10 above it", 20, MUTED)
    v += mono(110, 990, "weakest step that can seed: 29.7 / 4 = 7.4 grey levels", 21, INK, "start", 600)
    v += mono(110, 1050, "model: Gaussian pixel noise, Sobel aperture 3, L2", 18, SOFT)
    emit("feed", 7, "set-them-from-the-noise",
         ["Set them from", "the noise."],
         ["Pick how many false seeds a flat region",
          "may produce, and derive the number."],
         v,
         ["A ratio of 2 to 3 is what chains of 4 to 9",
          "pixels can afford under that model."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("suppression", "four bins, or interpolation", "and a tie rule: 0, 1 or 2 pixels a row"),
             ("hysteresis", "chains, not pixels", "450 and 180: 10 pixels raw, 5 smoothed"),
             ("units", "raw Sobel: 4h at aperture 3, 48h at 5", "L1 reads diagonals up to 41% high"),
             ("thresholds", "from the noise, not by trial", "high = s √(2 ln(1/α)), low a half to a third")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "hysteresis" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Canny edge detection,", "line by line."],
         ["Every step worked by hand",
          "on one 5×5 patch."],
         v,
         ["The full walk-through, with every number",
          "worked by hand and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = mono(150, 790, "cv2.Canny, defaults, on the patch", 22, SOFT, "start", 600)
    v += result5(150, 815, 104, KEEP1, M1, LINE1, 24)
    v += txt(150, 1400, "three dots, or the dots and a ring", 30, MUTED)
    emit("story", 1, "every-threshold-pair-fails",
         ["Every threshold", "pair fails."],
         ["One clean step of 160,", "one bright pixel."],
         v,
         ["Smoothing first", "is what fixes it."],
         STORY_TOTAL)


def story_02():
    v = mono(150, 800, "at (r1, c2), Gx 425 and Gy 215", 24, SOFT, "start", 600)
    v += mono(150, 920, "L1: 425 + 215", 44, ACCENT, "start", 600)
    v += mono(150, 1000, "= 640", 64, ACCENT, "start", 600)
    v += mono(150, 1090, "ties (r1, c3) = 640: both lost", 26, ACCENT, "start", 600)
    v += mono(150, 1220, "L2: 476.3", 44, LINK, "start", 600)
    v += mono(150, 1290, "(r1, c3) wins with 640", 26, LINK, "start", 600)
    emit("story", 2, "640-equals-640",
         ["640 = 640."],
         ["OpenCV's default L1 magnitude", "on row r1 of the patch."],
         v,
         ["The default norm deletes", "two rows of the edge."],
         STORY_TOTAL)


def story_03():
    v = mono(150, 790, "raw patch", 22, ACCENT, "start", 600)
    v += result5(150, 815, 76, RAW_OUT, M2, LINE2, 17)
    v += mono(560, 790, "after the Gaussian", 22, LINK, "start", 600)
    v += result5(560, 815, 76, SM_OUT, F.SM2, F.COL, 15, hollow=SM_DROPPED)
    v += txt(150, 1290, "10 pixels out", 34, ACCENT, SANS, 600)
    v += txt(560, 1290, "5 pixels out", 34, LINK, SANS, 600)
    v += txt(150, 1370, "same thresholds: high 450, low 180", 28, MUTED)
    emit("story", 3, "chains-not-pixels",
         ["Chains,", "not pixels."],
         ["Hysteresis keeps a chain", "if it holds a seed."],
         v,
         ["The ratio works", "only after smoothing."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["gradient: cv2.Canny does not smooth",
             "suppression: bins, ties, the norm",
             "hysteresis: chains, not pixels",
             "thresholds: from the noise"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 2 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Canny, line by line,", "by hand."],
         ["Worked on one", "5×5 patch."],
         v,
         ["The full walk-through is on Canery."],
         STORY_TOTAL, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08,
            story_01, story_02, story_03, story_04]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
