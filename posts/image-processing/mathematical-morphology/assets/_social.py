#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Mathematical Morphology as Lattice Algebra".

Image Processing by Hand, part 12. The shell (lockup, rule, serif title, deck, takeaway, footer) is
copied from part 11's _social.py (itself from part 9, with the lockup reading "canery.in" as in part
10). Every number on a card comes from `_data.py` — the mask and its erosion, dilation, opening and
closing, the adjunction checks, the granulometry, the threshold decomposition, the gradient and Sobel,
the two border rules and OpenCV's 2×2 replay — so a card cannot disagree with the article. Mask cells
follow the article: in the set = bright; added pixels tinted, removed ones crossed, as in the figures.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
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
GREEN, MUSTARD = "#7c8f6f", "#b8915a"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/mathematical-morphology"
FOOTER = "MATHEMATICAL MORPHOLOGY · CANERY.IN"

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


def rect(x, y, w, h, fill, stroke="none", sw=0, op=None, dash=None):
    o = f' fill-opacity="{op}"' if op is not None else ""
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{o} stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=2, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{dd}/>'


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    return line(x1, y, x2, y, stroke, sw, dash)


def blend(rgb, a, paper=(255, 255, 255)):
    rr, gg, bb = (round(a * c + (1 - a) * p) for c, p in zip(rgb, paper))
    return f"#{rr:02x}{gg:02x}{bb:02x}"


REG = {1: blend((46, 90, 168), 0.32), 2: blend((235, 108, 54), 0.30), 3: blend((124, 143, 111), 0.34),
       4: blend((184, 145, 90), 0.34)}


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
X, CROSS = d.X, d.CROSS
assert len(X) == 11 and len(d.E1) == 5 and len(d.D1) == 19 and len(d.O1) == 10 and len(d.C1) == 14
assert len(d.CV_CLOSE22) == 7 and len(d.CV_CLOSE22_LOST) == 5 and len(d.TRUE_CLOSE22) == 13
assert d.AREA == [11, 10, 0, 0] and d.SPECTRUM_AREA[:2] == [1, 10] and d.ADJ_FAIL["zero"] == 616
assert len(d.C0) == 7 and len(d.C0_LOST) == 7 and len(d.E0) == 0
ITER2 = d.dil(d.dil(d.ero(d.ero(X, CROSS), CROSS), CROSS), CROSS)
assert ITER2 == frozenset() and d.opening(d.O1, CROSS) == d.O1

WHITE = "#ffffff"
DARKC = blend((45, 49, 66), 0.80, (245, 245, 245))            # the figures' "not in the set"
ADDC = blend((235, 108, 54), 0.32, (245, 245, 245))           # the figures' "added, not in X"
ELEMC = blend((46, 90, 168), 0.62, (245, 245, 245))           # the figures' element blue


def xmark(x, y, h, colour, sw=4):
    return line(x - h, y - h, x + h, y + h, colour, sw) + line(x - h, y + h, x + h, y - h, colour, sw)


def sgrid(x, y, cs, S, ref=None, n=5, m=5):
    """A mask as in the figures: in the set white, out dark; against ref, added tinted, removed crossed."""
    s = ""
    for i in range(n):
        for j in range(m):
            inside = (i, j) in S
            f = WHITE if inside else DARKC
            if inside and ref is not None and (i, j) not in ref:
                f = ADDC
            s += rect(x + j * cs, y + i * cs, cs, cs, f, "rgba(45,49,66,0.35)", 1.2)
            if not inside and ref is not None and (i, j) in ref:
                s += xmark(x + j * cs + cs / 2, y + i * cs + cs / 2, cs * 0.22, ACCENT, max(3, cs / 14))
    s += rect(x, y, m * cs, n * cs, "none", "rgba(45,49,66,0.6)", 2)
    return s


def heat(vmax):
    return lambda v: WHITE if v <= 0 else blend((235, 108, 54), 0.12 + 0.55 * min(1.0, v / vmax), (255, 255, 255))


def grey(v):
    a = 0.88 * (1 - v / 255) + 0.02
    return blend((45, 49, 66), a, (245, 245, 245))


def vgrid(x, y, cs, M, fill_fn, fmt_fn=lambda v: f"{v:g}", size=20, text_fn=None):
    s = ""
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            s += rect(x + j * cs, y + i * cs, cs, cs, fill_fn(v), "rgba(45,49,66,0.35)", 1.2)
            s += mono(x + j * cs + cs / 2, y + i * cs + cs / 2 + size * 0.36, fmt_fn(v), size,
                      text_fn(v) if text_fn else INK, "middle", 600)
    s += rect(x, y, len(M[0]) * cs, len(M) * cs, "none", "rgba(45,49,66,0.6)", 2)
    return s


def legend_row(x, y, items, size=17):
    """Swatches drawn exactly like the cells they name."""
    s = ""
    for lab, kind in items:
        if kind == "in":
            s += rect(x, y - 16, 22, 22, WHITE, "rgba(45,49,66,0.45)", 1.2)
        elif kind == "out":
            s += rect(x, y - 16, 22, 22, DARKC, "rgba(45,49,66,0.45)", 1.2)
        elif kind == "added":
            s += rect(x, y - 16, 22, 22, ADDC, "rgba(45,49,66,0.45)", 1.2)
        elif kind == "removed":
            s += rect(x, y - 16, 22, 22, DARKC, "rgba(45,49,66,0.45)", 1.2) + xmark(x + 11, y - 5, 5, ACCENT, 3)
        s += mono(x + 32, y, lab, size, MUTED)
        x += 32 + 0.6 * size * len(lab) + 34
    return s


def fmt1(v):
    return f"{v:,.1f}" if abs(v - round(v)) > 1e-9 else f"{round(v):,}"


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cs, y0 = 52, 590
    xs = [110, 410, 710]
    panels = [(X, None, "the mask", f"{len(X)} px"),
              (d.CV_CLOSE22, X, "MORPH_CLOSE, 2×2", f"{len(d.CV_CLOSE22)} px, {len(d.CV_CLOSE22_LOST)} lost"),
              (d.TRUE_CLOSE22, X, "a true closing", f"{len(d.TRUE_CLOSE22)} px, none lost")]
    for x0, (S, ref, head, foot) in zip(xs, panels):
        v += mono(x0, y0 - 24, head, 21, ACCENT if "MORPH" in head else INK, "start", 600)
        v += sgrid(x0, y0, cs, S, ref)
        v += mono(x0, y0 + 5 * cs + 38, foot, 20, ACCENT if "lost" in foot and "none" not in foot else MUTED,
                  "start", 600 if "none" not in foot else 400)
    v += legend_row(110, 1000, [("in the set", "in"), ("not in it", "out"), ("added", "added"), ("removed", "removed")])
    v += mono(110, 1068, "fix: cv2.dilate(mask, k, anchor=(0, 0)), then cv2.erode", 20, INK, "start", 600)
    emit("feed", 1, "a-closing-that-deletes-pixels",
         ["OpenCV's closing", "deleted five pixels."],
         ["A 2×2 kernel, the series' 5×5 mask, and", "cv2.MORPH_CLOSE, which may only add pixels."],
         v,
         ["OpenCV's dilate does not reflect the kernel,", "so the pair is no longer adjoint."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 560, "δ(A) ⊆ Y   exactly when   A ⊆ ε(Y)", 30, INK, "start", 600)
    cs = 22
    rows = [("A = the speck, Y = X", d.SPECK, X), ("A = column c4, Y = X", d.E1, X)]
    y = 640
    for lab, A, Y in rows:
        dA, eY = d.dil(A, CROSS), d.ero(Y, CROSS)
        left, right = dA <= Y, A <= eY
        v += mono(110, y - 14, lab, 19, MUTED, "start", 600)
        v += sgrid(110, y, cs, dA)
        v += txt(110 + 5 * cs + 26, y + 70, "⊆", 34, MUTED, SANS, 500, "middle")
        v += sgrid(110 + 5 * cs + 52, y, cs, Y)
        v += mono(110 + 10 * cs + 74, y + 66, "yes" if left else "no", 30, INK if left else ACCENT, "start", 600)
        v += sgrid(580, y, cs, A)
        v += txt(580 + 5 * cs + 26, y + 70, "⊆", 34, MUTED, SANS, 500, "middle")
        v += sgrid(580 + 5 * cs + 52, y, cs, eY)
        v += mono(580 + 10 * cs + 74, y + 66, "yes" if right else "no", 30, INK if right else ACCENT, "start", 600)
        y += 200
    v += mono(110, 1046, "left: is δ(A) inside Y?    right: is A inside ε(Y)?", 18, SOFT)
    v += mono(110, 1078, "the same answer every time, on all 64 pairs of the post's sets", 18, SOFT)
    emit("feed", 2, "one-law",
         ["Erosion and dilation", "are one law."],
         ["Stamping A inside Y is the same question", "as A fitting inside the erosion of Y."],
         v,
         ["Put Y = δ(A): closing never removes a pixel.", "Put A = ε(Y): opening never adds one."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cs, y0 = 46, 600
    v += mono(110, y0 - 26, "opened once", 20, INK, "start", 600)
    v += sgrid(110, y0, cs, d.O1, X)
    v += txt(110 + 5 * cs + 45, y0 + 125, "=", 44, INK, SANS, 500, "middle")
    v += mono(410, y0 - 26, "opened twice", 20, INK, "start", 600)
    v += sgrid(410, y0, cs, d.opening(d.O1, CROSS), X)
    v += mono(710, y0 - 26, "iterations=2", 20, ACCENT, "start", 600)
    v += sgrid(710, y0, cs, ITER2, X)
    v += mono(110, y0 + 5 * cs + 36, f"{len(d.O1)} px", 21, INK, "start", 600)
    v += mono(410, y0 + 5 * cs + 36, f"{len(d.opening(d.O1, CROSS))} px", 21, INK, "start", 600)
    v += mono(710, y0 + 5 * cs + 36, f"{len(ITER2)} px", 21, ACCENT, "start", 600)
    v += mono(110, 1004, "iterations=2: erode, erode, dilate, dilate", 20, MUTED)
    v += mono(110, 1046, "an opening by the 13-pixel diamond, not a second pass", 20, MUTED)
    emit("feed", 3, "twice-is-once",
         ["Opening twice", "changes nothing."],
         ["So iterations=2 cannot mean 'open twice'.", "OpenCV's documentation says what it does."],
         v,
         ["An opening is idempotent; iterations=n is", "an opening by an element n times the size."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cs = 42
    v += mono(110, 560, "f, the patch", 20, INK, "start", 600)
    v += vgrid(110, 584, cs, d.P, grey, size=15, text_fn=lambda t: WHITE if t < 130 else INK)
    v += mono(410, 560, "X_41, eroded", 20, INK, "start", 600)
    v += sgrid(410, 584, cs, d.STACK[41], d.thr(d.P, 41))
    v += mono(710, 560, "ε(f), stacked", 20, INK, "start", 600)
    v += vgrid(710, 584, cs, d.GE, grey, size=15, text_fn=lambda t: WHITE if t < 130 else INK)
    v += txt(110 + 5 * cs + 34, 584 + 2.5 * cs + 12, "→", 34, MUTED, SANS, 500, "middle")
    v += txt(410 + 5 * cs + 34, 584 + 2.5 * cs + 12, "→", 34, MUTED, SANS, 500, "middle")
    v += mono(110, 864, "t from 41 to 200: the threshold set is the mask", 19, MUTED)
    v += mono(110, 900, "t from 201 to 255: the impulse alone, which erodes to nothing", 19, MUTED)
    v += mono(110, 936, "t up to 40: the whole grid, which stays whole", 19, MUTED)
    v += mono(110, 1000, "each pixel takes the highest t that survives:", 20, INK, "start", 600)
    v += mono(110, 1036, "200 on c4, 40 elsewhere", 20, INK, "start", 600)
    emit("feed", 4, "grey-is-binary-stacked",
         ["Grey erosion is", "binary, stacked."],
         ["Cut the patch at every level, erode each", "set, and stack the results back up."],
         v,
         ["Flat operators commute with thresholds,", "so every binary law holds in grey."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cs = 70
    sob = [[round(x, 1) for x in row] for row in d.SOBEL]
    v += mono(110, 560, "dilation − erosion", 21, INK, "start", 600)
    v += vgrid(110, 584, cs, d.GRAD, heat(215), size=19)
    v += mono(580, 560, "Sobel, Part 8's table", 21, INK, "start", 600)
    v += vgrid(580, 584, cs, sob, heat(640), fmt_fn=fmt1, size=15)
    v += mono(110, 584 + 5 * cs + 40, "160: the step's height", 19, MUTED)
    v += mono(110, 584 + 5 * cs + 70, "215: the impulse", 19, MUTED)
    v += mono(580, 584 + 5 * cs + 40, "640 = 4 × 160 on the step", 19, MUTED)
    v += mono(580, 584 + 5 * cs + 70, "0 on the impulse itself", 19, MUTED)
    emit("feed", 5, "heights-not-slopes",
         ["Gradient: 160.", "Sobel: 640."],
         ["The patch's step is 160 grey levels high.", "Dilation minus erosion reads it as it is."],
         v,
         ["A range never cancels: the impulse reads 215", "where Sobel's two halves give 0."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    x0, yb, h = 150, 900, 280
    amax = 13
    for k, (n, a) in enumerate(zip(d.SIZES, d.AREA)):
        xc = x0 + k * 120
        if a:
            v += rect(xc - 30, yb - a / amax * h, 60, a / amax * h, INK)
        v += mono(xc, yb - a / amax * h - 14, str(a), 24, INK, "middle", 600)
        v += mono(xc, yb + 34, f"n = {n}", 18, SOFT, "middle")
        el = d.nB(n)
        span = max(1, n)
        c = 9 if n < 3 else 7
        kk = 2 * span + 1
        for i in range(kk):
            for j in range(kk):
                if (i - span, j - span) in el:
                    v += rect(xc - kk * c / 2 + j * c, yb + 50 + i * c, c, c, ELEMC, "rgba(45,49,66,0.35)", 1)
    v += hline(x0 - 50, x0 + 3 * 120 + 50, yb, MUTED, 1.5)
    v += mono(x0 - 40, 600, "mask area kept by the opening by nB", 19, INK, "start", 600)
    v += mono(700, 640, "what each size removes", 19, INK, "start", 600)
    v += mono(700, 700, "size 0", 20, SOFT)
    v += mono(700, 734, f"{d.SPECTRUM_AREA[0]} px: the speck", 24, ACCENT, "start", 600)
    v += mono(700, 800, "size 1", 20, SOFT)
    v += mono(700, 834, f"{d.SPECTRUM_AREA[1]} px: the bar", 24, INK, "start", 600)
    v += mono(700, 900, "size 2 and up", 20, SOFT)
    v += mono(700, 934, "nothing left", 24, SOFT, "start", 600)
    emit("feed", 6, "a-sieve-with-four-meshes",
         ["The speck is size 0.", "The bar is size 1."],
         ["Open by growing elements and count what", "each size removes: a pattern spectrum."],
         v,
         ["The bar is 2 pixels wide yet survives the", "3-wide cross, because it touches the edge."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cs = 34
    v += mono(330, 560, "erosion", 20, INK, "start", 600)
    v += mono(630, 560, "closing", 20, INK, "start", 600)
    rows = [("outside ignored", "OpenCV, MATLAB", d.E1, d.C1, 584), ("outside = 0", "SciPy's default", d.E0, d.C0, 806)]
    for name, who, E, C, y in rows:
        v += mono(110, y + 70, name, 21, INK, "start", 600)
        v += mono(110, y + 102, who, 18, SOFT)
        v += sgrid(330, y, cs, E, X)
        v += sgrid(630, y, cs, C, X)
        lost = len(X - C)
        v += mono(330 + 5 * cs + 18, y + 96, f"{len(E)} px", 19, MUTED)
        v += mono(630 + 5 * cs + 18, y + 80, f"{len(C)} px", 19, ACCENT if lost else MUTED, "start", 600 if lost else 400)
        v += mono(630 + 5 * cs + 18, y + 108, f"loses {lost}" if lost else "keeps X", 19, ACCENT if lost else MUTED,
                  "start", 600 if lost else 400)
    v += mono(110, 1070, f"outside = 0: the adjunction fails on {d.ADJ_FAIL['zero']:,} of 20,000 random pairs", 19, INK,
              "start", 600)
    emit("feed", 7, "the-border-decides",
         ["SciPy's closing", "lost seven pixels."],
         ["Its binary functions assume 0 outside the", "image; OpenCV and MATLAB ignore the outside."],
         v,
         ["Ignore the outside and the laws hold;", "pad it with 0 and they fail at the edge."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("adjunction", "δ(A) ⊆ Y exactly when A ⊆ ε(Y)", "opening never adds, closing never removes"),
             ("idempotence", "twice is once", "iterations=n is a bigger element"),
             ("grey levels", "binary at every threshold", "gradient 160 at the step, top-hat 215"),
             ("libraries", "border and reflection decide", f"OpenCV's 2×2 closing loses {len(d.CV_CLOSE22_LOST)}")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "libraries" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Mathematical", "morphology, by hand."],
         ["Erosion, dilation and the laws behind them,", "on one 5×5 patch."],
         v,
         ["The full walk-through, every number worked", "by hand, and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    cs = 64
    v = mono(110, 790, "the mask", 26, INK, "start", 600)
    v += sgrid(110, 820, cs, X)
    v += mono(110 + 5 * cs + 80, 790, "MORPH_CLOSE, 2×2", 26, ACCENT, "start", 600)
    v += sgrid(110 + 5 * cs + 80, 820, cs, d.CV_CLOSE22, X)
    v += mono(110, 820 + 5 * cs + 50, f"{len(X)} px", 28, INK, "start", 600)
    v += mono(110 + 5 * cs + 80, 820 + 5 * cs + 50, f"{len(d.CV_CLOSE22)} px, {len(d.CV_CLOSE22_LOST)} lost", 28,
              ACCENT, "start", 600)
    v += legend_row(110, 1300, [("in the set", "in"), ("not in it", "out"), ("added", "added"), ("removed", "removed")],
                    size=21)
    emit("story", 1, "the-closing-deleted-five-pixels",
         ["The closing deleted", "five pixels."],
         ["OpenCV, a 2×2 kernel,", "the 5×5 patch's mask."],
         v,
         ["Dilate with anchor=(0, 0)", "and the closing keeps all 11."],
         STORY_TOTAL)


def story_02():
    cs = 54
    v = mono(110, 790, "opened twice", 26, INK, "start", 600)
    v += sgrid(110, 820, cs, d.opening(d.O1, CROSS), X)
    v += mono(110 + 5 * cs + 120, 790, "iterations=2", 26, ACCENT, "start", 600)
    v += sgrid(110 + 5 * cs + 120, 820, cs, ITER2, X)
    v += mono(110, 820 + 5 * cs + 50, f"{len(d.O1)} px, as once", 28, INK, "start", 600)
    v += mono(110 + 5 * cs + 120, 820 + 5 * cs + 50, f"{len(ITER2)} px", 28, ACCENT, "start", 600)
    v += mono(110, 1260, "erode, erode, dilate, dilate:", 26, MUTED)
    v += mono(110, 1302, "an opening by a 13-pixel diamond", 26, MUTED)
    emit("story", 2, "twice-is-once",
         ["Opening twice", "is opening once."],
         ["So iterations=2 must be", "something else."],
         v,
         ["On the patch: the same 10 pixels,", "against none."],
         STORY_TOTAL)


def story_03():
    cs, gx = 80, 340
    v = mono(gx, 790, "dilation − erosion, by the cross", 24, INK, "start", 600)
    v += vgrid(gx, 820, cs, d.GRAD, heat(215), size=24)
    v += mono(540, 820 + 5 * cs + 56, "Sobel reads 640 on the step, 0 on the impulse", 24, MUTED, "middle")
    emit("story", 3, "160-not-640",
         ["160, not 640."],
         ["The morphological gradient reads", "the step's height, not its slope."],
         v,
         ["And it marks the impulse with 215,", "where Sobel reads 0."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["erosion and dilation are adjoint",
             "so twice is once, by law",
             "grey inherits it, level by level",
             "libraries keep it, or break it"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 3 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Mathematical", "morphology."],
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
