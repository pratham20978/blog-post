#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "The Structure Tensor".

Image Processing by Hand, part 9. The shell (lockup, rule, serif title, deck, takeaway,
footer) is copied from part 8's _social.py, with the lockup reading "canery.in". Every
number on a card comes from `_figs.py` — the Sobel gradient under reflect-101, the box-window
tensors, their eigenvalues and scores, goodFeaturesToTrack's rule, and the one-step
Lucas-Kanade solves — so a card cannot disagree with the article. Pixel cells follow the
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
CANONICAL = "canery.in/blogs/the-structure-tensor"
FOOTER = "THE STRUCTURE TENSOR · CANERY.IN"

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
assert F.PTS == [(2, 2)] and round(F.MX, 1) == 616155.8
assert (F.A[2][2], F.C[2][2], F.A[2][4], F.C[2][4]) == (1634150, 462250, 2457600, 0)
assert (round(F.H04[2][3] / 1e9, 1), round(F.H06[2][3] / 1e9, 1)) == (31.8, -27.8)
assert (round(F.tstar(0.04), 4), round(F.tstar(0.06), 4)) == (0.0436, 0.0685)
D2, _ = F.lk_one_step(2, 2)
D1, _ = F.lk_one_step(2, 1)
assert (round(D2[0], 2), round(D1[0], 2)) == (1.28, -0.89)
T3 = F.L2[2][3] / F.L1[2][3]
assert round(T3, 3) == 0.057


def fv(v, nd=1):
    s = f"{v:,.0f}" if abs(v - round(v)) < 1e-9 else f"{v:,.{nd}f}"
    return s.replace("-", "−")


def shaded(x, y, w, h, t, stroke="rgba(45,49,66,0.35)", sw=1.5):
    t = max(0.0, min(1.0, t))
    a = 0.85 * (1 - t) + 0.04
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"/>')


def patch5(x, y, cw, size=20, values=True, pick=True, impulse=True):
    out = ""
    for i in range(5):
        for j in range(5):
            v = F.PATCH[i][j]
            out += shaded(x + j * cw, y + i * cw, cw, cw, v / 255)
            if values:
                out += mono(x + j * cw + cw / 2, y + i * cw + cw / 2 + size * 0.36, str(v), size,
                            "#ffffff" if v < 130 else INK, "middle", 600)
    if impulse:
        out += (f'<rect x="{x + cw + 4}" y="{y + 2 * cw + 4}" width="{cw - 8}" height="{cw - 8}" fill="none" '
                f'stroke="{LINK}" stroke-width="4" stroke-dasharray="10,7"/>')
    if pick:
        out += (f'<rect x="{x + 2 * cw}" y="{y + 2 * cw}" width="{cw}" height="{cw}" fill="none" '
                f'stroke="{ACCENT}" stroke-width="6"/>')
    return out


def arrows5(x, y, cw):
    out = ""
    for i in range(5):
        for j in range(5):
            gx, gy = F.GX[i][j], F.GY[i][j]
            m = math.hypot(gx, gy)
            if not m:
                continue
            cx, cy = x + j * cw + cw / 2, y + i * cw + cw / 2
            L = 0.7 * cw * math.sqrt(m / 640)
            col = "#ffffff" if F.PATCH[i][j] < 130 else INK
            ux, uy = gx / m, gy / m
            x1, y1, x2, y2 = cx - ux * L / 2, cy - uy * L / 2, cx + ux * L / 2, cy + uy * L / 2
            hx, hy = x2 - ux * 13, y2 - uy * 13
            px_, py_ = -uy * 7, ux * 7
            out += (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{col}" '
                    f'stroke-width="4" stroke-linecap="round"/>'
                    f'<polygon points="{x2:.1f},{y2:.1f} {hx + px_:.1f},{hy + py_:.1f} {hx - px_:.1f},{hy - py_:.1f}" '
                    f'fill="{col}"/>')
    return out


def glyph(cx, cy, l1, l2, ang, scale, colr=INK, fill=None, op=0.16, sw=4):
    a, b = scale * math.sqrt(max(l1, 0)), scale * math.sqrt(max(l2, 0))
    if b < 1:
        dx, dy = a * math.cos(math.radians(ang)), a * math.sin(math.radians(ang))
        return (f'<line x1="{cx - dx:.1f}" y1="{cy - dy:.1f}" x2="{cx + dx:.1f}" y2="{cy + dy:.1f}" '
                f'stroke="{colr}" stroke-width="7" stroke-linecap="round"/>')
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{a:.1f}" ry="{b:.1f}" '
            f'transform="rotate({ang:.1f} {cx:.1f} {cy:.1f})" fill="{fill or colr}" fill-opacity="{op}" '
            f'stroke="{colr}" stroke-width="{sw}"/>')


def ratio_axis(x0, y0, w, size=18, big=False):
    """0 to 0.08: Harris's two sign boundaries and (r2, c3)'s ratio."""
    X = lambda t: x0 + t / 0.08 * w
    out = f'<line x1="{x0}" y1="{y0}" x2="{x0 + w}" y2="{y0}" stroke="{RULE_SOLID}" stroke-width="3"/>'
    for t in (0, 0.02, 0.04, 0.06, 0.08):
        out += f'<line x1="{X(t):.1f}" y1="{y0}" x2="{X(t):.1f}" y2="{y0 + 12}" stroke="{RULE_SOLID}" stroke-width="3"/>'
        out += mono(X(t), y0 + 40, f"{t:g}", size, SOFT, "middle")
    hgt = 150 if big else 120
    for k, dash, lab, anchor, dx in ((0.04, None, "k = 0.04", "end", -10), (0.06, "12,8", "k = 0.06", "start", 10)):
        xk = X(F.tstar(k))
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out += f'<line x1="{xk:.1f}" y1="{y0 - hgt}" x2="{xk:.1f}" y2="{y0}" stroke="{ACCENT}" stroke-width="4"{d}/>'
        out += mono(xk + dx, y0 - hgt + 8, lab, size, ACCENT, anchor, 600)
        out += mono(xk + dx, y0 - hgt + 8 + size * 1.3, f"{F.tstar(k):.4f}", size - 2, ACCENT, anchor)
    xc = X(T3)
    out += f'<circle cx="{xc:.1f}" cy="{y0 - 52}" r="11" fill="{INK}" stroke="#ffffff" stroke-width="3"/>'
    if big:
        out += mono(xc, y0 - 108, "(r2, c3)", size, INK, "middle", 600)
        out += mono(xc, y0 - 76, "0.057", size, INK, "middle", 600)
    else:
        out += mono(xc, y0 - 74, "(r2, c3): 0.057", size, INK, "middle", 600)
    return out


def matrix(x, y, rows, vec, size=26, colw=None, gap=None, fill=INK):
    """A 2x2 matrix times a vector, with drawn brackets and right-aligned columns."""
    gap = gap or int(size * 1.75)
    cw = colw or [size * 6.4, size * 1.6]
    out = ""
    h = gap * (len(rows) - 1) + size * 1.1
    top = y - size * 0.95
    right = x + 18 + sum(cw) + 20
    for bx, flip in ((x, 1), (right, -1)):
        out += (f'<path d="M {bx + 10 * flip} {top} H {bx} V {top + h} H {bx + 10 * flip}" fill="none" '
                f'stroke="{fill}" stroke-width="3"/>')
    for i, row in enumerate(rows):
        cx = x + 18
        for j, val in enumerate(row):
            cx += cw[j]
            out += mono(cx, y + i * gap, val, size, fill, "end", 600)
    vx = right + 30
    for bx, flip in ((vx, 1), (vx + size * 1.9, -1)):
        out += (f'<path d="M {bx + 10 * flip} {top} H {bx} V {top + h} H {bx + 10 * flip}" fill="none" '
                f'stroke="{fill}" stroke-width="3"/>')
    for i, val in enumerate(vec):
        out += mono(vx + size * 0.95, y + i * gap, val, size, fill, "middle", 600)
    return out


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "the patch", 17, SOFT, "start", 600)
    v += patch5(110, 562, 78, 19)
    nx = 560
    v += mono(nx, 600, "goodFeaturesToTrack(p, 10, 0.01, 1)", 18, INK, "start", 600)
    v += mono(nx, 650, "→ one point: x = 2, y = 2", 22, ACCENT, "start", 600)
    v += mono(nx, 720, "the bright pixel, x = 1:", 20, LINK, "start", 600)
    v += mono(nx, 752, "not returned", 20, LINK, "start", 600)
    v += mono(nx, 822, "the step runs between", 20, MUTED)
    v += mono(nx, 854, "x = 2 and x = 3", 20, MUTED)
    v += mono(110, 1010, "(2, 2): smaller eigenvalue 462,250, the largest", 20, INK, "start", 600)
    v += mono(110, 1046, "inside the patch; the border's 616,156 is never returned", 20, INK, "start", 600)
    v += mono(110, 1094, "worked by hand from OpenCV's source; not run", 17, SOFT)
    emit("feed", 1, "the-best-feature-is-not-the-bright-pixel",
         ["The best feature", "is not the bright pixel."],
         ["OpenCV's goodFeaturesToTrack on one 5×5 patch:",
          "a step of 160 and one pixel of 255."],
         v,
         ["It returns a window whose gradients point",
          "two ways: the step's and the pixel's."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "Sobel gradient, reflect-101 border", 17, SOFT, "start", 600)
    cw = 84
    v += patch5(110, 562, cw, values=False, pick=False, impulse=False)
    v += arrows5(110, 562, cw)
    v += mono(110 + cw * 1.5, 562 + cw * 2.5 + 10, "0", 30, ACCENT, "middle", 600)
    nx = 580
    v += mono(nx, 600, "each pixel: one gradient,", 21, INK, "start", 600)
    v += mono(nx, 634, "one direction", 21, INK, "start", 600)
    v += mono(nx, 690, "its outer product has", 20, MUTED)
    v += mono(nx, 722, "rank 1 at most", 20, MUTED)
    v += mono(nx, 798, "the 255 itself: gradient 0,", 21, ACCENT, "start", 600)
    v += mono(nx, 832, "the same zero matrix", 20, MUTED)
    v += mono(nx, 864, "as a flat pixel", 20, MUTED)
    v += mono(110, 1046, "the step reads 640 = 4 × 160 on c2 and c3", 20, LINK, "start", 600)
    emit("feed", 2, "no-pixel-is-a-corner",
         ["No single pixel", "can be a corner."],
         ["Sobel on the patch, with the border",
          "rule cv2.cornerHarris uses."],
         v,
         ["A corner needs a window: a sum of",
          "gradients from different directions."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "row r2: each 3×3 window's tensor", 17, SOFT, "start", 600)
    scale = 92 / math.sqrt(F.L1[2][4])
    for k, c in enumerate((4, 3, 2, 1)):
        cx = 190 + k * 222
        cy = 720
        v += glyph(cx, cy, F.L1[2][c], F.L2[2][c], F.TH[2][c], scale, ACCENT if c == 2 else INK)
        v += mono(cx, 870, f"(r2, c{c})", 20, INK, "middle", 600)
        v += mono(cx, 906, f"λ1 {fv(F.L1[2][c])}", 17, MUTED, "middle")
        v += mono(cx, 934, f"λ2 {fv(F.L2[2][c])}", 17, MUTED, "middle")
        v += mono(cx, 974, {4: "rank 1", 3: "rank 2, barely", 2: "rank 2", 1: "rank 2"}[c], 18,
                  ACCENT if c == 2 else INK, "middle", 600)
    v += mono(110, 1046, "c4: the step alone · c1: the bright pixel", 18, SOFT)
    v += mono(110, 1080, "semi-axes ∝ √λ, along the eigenvectors", 18, SOFT)
    emit("feed", 3, "zero-one-or-two-directions",
         ["Zero, one or", "two directions."],
         ["Sum each pixel's outer product over a",
          "3×3 window: a 2×2 matrix, drawn as an ellipse."],
         v,
         ["The two eigenvalues count the",
          "directions a window varies in."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 560, "R = λ1² [t − k(1 + t)²],  t = λ2 / λ1", 24, INK, "start", 600)
    v += mono(110, 600, "R > 0, a corner, exactly when t / (1 + t)² > k", 19, SOFT)
    v += ratio_axis(150, 860, 780, 18)
    v += mono(110, 966, "k = 0.04:  R = +31.8 × 10⁹ → corner", 22, ACCENT, "start", 600)
    v += mono(110, 1006, "k = 0.06:  R = −27.8 × 10⁹ → edge", 22, ACCENT, "start", 600)
    v += mono(110, 1066, "(r2, c3) is a pixel on the step itself", 19, MUTED)
    emit("feed", 4, "k-is-a-ratio",
         ["Harris's k is", "a ratio threshold."],
         ["R changes sign at one eigenvalue ratio:",
          "1 to 23 at k = 0.04, 1 to 14.6 at 0.06."],
         v,
         ["Choose how elongated a corner may be.",
          "That choice is k."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "why (2, 2) wins", 17, SOFT, "start", 600)
    scale = 100 / math.sqrt(F.A[2][2])
    cy = 720
    parts = [(F.A[2][2], 0, 0, LINK, "the step's Gx²", f"A = {fv(F.A[2][2])}"),
             (F.C[2][2], 0, 90, ACCENT, "the pixel's ring, Gy²", f"C = {fv(F.C[2][2])}"),
             (F.A[2][2], F.C[2][2], 0, INK, "(2, 2)'s tensor", f"λ2 = {fv(F.L2[2][2])}")]
    for k, (l1, l2, ang, col, lab, val) in enumerate(parts):
        cx = 220 + k * 320
        v += glyph(cx, cy, l1, l2, ang, scale, col)
        v += mono(cx, 880, lab, 19, col, "middle", 600)
        v += mono(cx, 912, val, 19, col, "middle", 600)
        if k < 2:
            v += mono(cx + 160, cy + 14, "+" if k == 0 else "=", 46, MUTED, "middle", 600)
    v += mono(110, 1000, "the bright pixel's own window, (1, 2): λ2 = 405,350", 19, MUTED)
    v += mono(110, 1032, "its ring cuts the step's 640 at c2 to 425, 210, 425", 19, MUTED)
    emit("feed", 5, "two-edges-in-one-window",
         ["Two edges in", "one window."],
         ["The step varies across x, the pixel's ring",
          "across y. Summed, they look like a corner."],
         v,
         ["Detectors find two directions,",
          "not geometric corners."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "Lucas–Kanade:  M d = −Σ g It", 26, INK, "start", 600)
    v += mono(110, 600, "at (r2, c4), the step's own window:", 19, SOFT)
    v += matrix(150, 690, [("2,457,600", "0"), ("0", "0")], ("u", "v"), 26)
    v += mono(150, 846, "0 · v = 0", 54, ACCENT, "start", 600)
    v += mono(150, 900, "for any pair of frames", 21, ACCENT, "start", 600)
    ax, ay, aw, ah = 690, 650, 260, 240
    v += f'<line x1="{ax}" y1="{ay + ah / 2}" x2="{ax + aw}" y2="{ay + ah / 2}" stroke="{RULE_SOLID}" stroke-width="2"/>'
    v += f'<line x1="{ax + aw * 0.3}" y1="{ay}" x2="{ax + aw * 0.3}" y2="{ay + ah}" stroke="{RULE_SOLID}" stroke-width="2"/>'
    xu = ax + aw * 0.3 + 2.0 * aw * 0.3
    v += f'<line x1="{xu:.1f}" y1="{ay}" x2="{xu:.1f}" y2="{ay + ah}" stroke="{ACCENT}" stroke-width="7"/>'
    v += mono(ax + aw, ay + ah / 2 + 30, "u", 19, SOFT, "end")
    v += mono(ax + aw * 0.3 + 10, ay + 22, "v", 19, SOFT, "start")
    v += mono(xu - 12, ay + ah - 12, "every v fits", 18, ACCENT, "end", 600)
    v += mono(xu - 8, ay + ah / 2 + 28, "u = 2", 17, SOFT, "end")
    v += mono(110, 1010, "slide the step down by any amount:", 20, MUTED)
    v += mono(110, 1044, "nothing in this window changes", 20, MUTED)
    emit("feed", 6, "the-aperture-problem-is-a-zero-eigenvalue",
         ["The aperture problem", "is a zero eigenvalue."],
         ["Optical flow solves with the same matrix",
          "the corner detectors score."],
         v,
         ["An edge's window cannot see",
          "motion along the edge."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "the patch moved one pixel right; one step", 17, SOFT, "start", 600)
    rows = [("(2, 2)", f"u = {D2[0]:.2f}", "right way, 28% long", LINK),
            ("(1, 2), the bright pixel", f"u = {D1[0]:.2f}".replace("-", "−"), "the wrong way", ACCENT)]
    y = 610
    for who, val, verdict, col in rows:
        v += txt(110, y, who, 26, INK, SANS, 600)
        v += mono(560, y, val, 28, col, "start", 600)
        v += mono(560, y + 36, verdict, 20, col)
        y += 120
    v += hline(110, 970, 836, RULE)
    v += mono(110, 886, "at c2 the step's slope predicts −26.25;", 21, INK, "start", 600)
    v += mono(110, 922, "the bright pixel arrives: +215", 21, ACCENT, "start", 600)
    v += mono(110, 990, "the linear model holds only for motions small", 19, MUTED)
    v += mono(110, 1022, "against the structure; this one is 1 pixel on 1", 19, MUTED)
    emit("feed", 7, "one-linear-step-can-point-backwards",
         ["One linear step", "can point backwards."],
         ["Lucas–Kanade, one step, on two windows",
          "that both pass a corner test."],
         v,
         ["Smooth, iterate, or go coarse to fine:",
          "the remedies Lucas and Kanade gave."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("eigenvalues", "zero, one or two directions", "rank 1 on the step, rank 2 at (2, 2)"),
             ("Harris's k", "a threshold on λ2 / λ1", "1 to 23 at 0.04, 1 to 14.6 at 0.06"),
             ("Shi–Tomasi", "the tracker's own test", "goodFeaturesToTrack returns (2, 2)"),
             ("Lucas–Kanade", "the same matrix, solved", "a zero eigenvalue is the aperture problem")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "Lucas–Kanade" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["The structure tensor,", "by hand."],
         ["Corners, orientation and optical flow",
          "from one 2×2 matrix."],
         v,
         ["The full walk-through, every number worked",
          "by hand, and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = mono(150, 790, "goodFeaturesToTrack on the patch", 22, SOFT, "start", 600)
    v += patch5(150, 815, 104, 24)
    v += txt(150, 1400, "returned: (2, 2), not the bright pixel", 30, MUTED)
    emit("story", 1, "the-best-feature-is-not-the-bright-pixel",
         ["The best feature is", "not the bright pixel."],
         ["One step of 160,", "one pixel of 255."],
         v,
         ["Two edges in one window", "count as a corner."],
         STORY_TOTAL)


def story_02():
    v = mono(150, 800, "Harris on (r2, c3), a pixel on the step", 24, SOFT, "start", 600)
    v += ratio_axis(150, 1130, 780, 24, big=True)
    v += mono(150, 1260, "k = 0.04: R > 0, a corner", 30, ACCENT, "start", 600)
    v += mono(150, 1320, "k = 0.06: R < 0, an edge", 30, ACCENT, "start", 600)
    emit("story", 2, "k-is-a-ratio",
         ["k = 0.04 says corner.", "k = 0.06 says edge."],
         ["One pixel on the step, two", "common settings of Harris's k."],
         v,
         ["k is a threshold on", "the eigenvalue ratio."],
         STORY_TOTAL)


def story_03():
    v = mono(150, 800, "Lucas–Kanade at the step's window", 24, SOFT, "start", 600)
    v += matrix(150, 930, [("2,457,600", "0"), ("0", "0")], ("u", "v"), 34)
    v += mono(150, 1130, "0 · v = 0", 76, ACCENT, "start", 600)
    v += mono(150, 1210, "whatever the frames hold", 28, ACCENT, "start", 600)
    v += txt(150, 1350, "u is measured, v is not", 32, MUTED)
    emit("story", 3, "zero-eigenvalue",
         ["0 · v = 0"],
         ["The same matrix the corner", "detectors score."],
         v,
         ["Any vertical motion fits.", "That is the aperture problem."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["eigenvalues: how many directions",
             "Harris's k: a ratio threshold",
             "Shi–Tomasi: the tracker's test",
             "Lucas–Kanade: the same matrix"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 3 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["The structure tensor,", "by hand."],
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
