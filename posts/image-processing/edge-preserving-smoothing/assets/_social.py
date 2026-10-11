#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Edge-Preserving Smoothing".

Image Processing by Hand, part 7. The shell (lockup, rule, serif title, deck, takeaway,
footer) is copied from part 6's _social.py, with the lockup reading "canery.in". Every
number on a card comes from `_figs.py` — the bilateral filter, NL-means under both
self-weight rules and the Perona-Malik iterations on the shared patch — so a card cannot
disagree with the article. Pixel cells follow the article: high value = bright.

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
CANONICAL = "canery.in/blogs/edge-preserving-smoothing"
FOOTER = "EDGE-PRESERVING SMOOTHING · CANERY.IN"

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
BIL = F.BIL80
PM = F.PM
NLM_MAX_IMP, NLM_ONE_IMP = F.NLM_MAX[2][1], F.NLM_ONE[2][1]
assert round(BIL[2][1], 1) == 240.5 and round(BIL[0][2], 1) == 46.5 and round(BIL[0][3], 1) == 193.5
assert round(NLM_MAX_IMP, 1) == 83.0 and round(NLM_ONE_IMP) == 255
assert [round(PM[k][2][1], 2) for k in range(4)] == [255, 228.85, 199.19, 165.25]
assert [(round(PM[k][0][2], 2), round(PM[k][0][3], 2)) for k in range(4)] == [
    (40, 200), (48, 192), (54.51, 185.49), (61.54, 179.65)]
assert round(F.rw(160, 80), 3) == 0.135 and round(F.rw(215, 80), 3) == 0.027
assert round(F.g_rat(215), 3) == 0.122 and F.g_rat(160) == 0.2


def fv(v, nd=1):
    s = f"{int(round(v))}" if abs(v - round(v)) < 1e-9 else f"{v:.{nd}f}"
    return s.replace("-", "−")


def cellv(v):
    """Scorecard display: integers when the value is within 0.005 of one, else one decimal."""
    return f"{int(round(v))}" if abs(v - round(v)) < 0.005 else f"{v:.1f}"


def shaded(x, y, w, h, t, stroke="rgba(45,49,66,0.35)", sw=1.5):
    t = max(0.0, min(1.0, t))
    a = 0.85 * (1 - t) + 0.04
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"/>')


def vcell(x, y, w, h, val, size=24, ring=False, nd=1):
    t = val / 255.0
    v = shaded(x, y, w, h, t, ACCENT if ring else "rgba(45,49,66,0.35)", 4 if ring else 1.5)
    return v + mono(x + w / 2, y + h / 2 + size * 0.36, fv(val, nd), size,
                    "#ffffff" if t < 0.52 else INK, "middle", 600)


def grid5(x, y, cw, M, size=18, ring=(2, 1)):
    return "".join(vcell(x + j * cw, y + i * cw, cw, cw, M[i][j], size, (i, j) == ring)
                   for i in range(5) for j in range(5))


def grid3(x, y, cw, vals, size=22, ring=None):
    return "".join(vcell(x + b * cw, y + a * cw, cw, cw, vals[3 * a + b], size, ring == (a, b))
                   for a in range(3) for b in range(3))


def bar(x, y, w, h, frac, col, op=0.85):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="rgba(45,49,66,0.25)" stroke-width="1.2"/>'
            f'<rect x="{x}" y="{y}" width="{max(frac * w, 2):.1f}" height="{h}" fill="{col}" fill-opacity="{op}"/>')


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "the patch", 17, SOFT, "start", 600)
    v += grid5(110, 562, 70, F.PATCH)
    v += mono(600, 540, "bilateral filter, σr = 80", 17, ACCENT, "start", 600)
    v += grid5(600, 562, 70, BIL)
    v += mono(110, 970, "edge 40 | 200 → 46.5 | 193.5: 92% kept", 22, LINK, "start", 600)
    v += mono(110, 1010, "bright pixel 255 → 240.5: 93% kept", 22, ACCENT, "start", 600)
    v += mono(110, 1050, "the Gaussian would give 78.2 | 161.8 and 98.6", 20, MUTED)
    emit("feed", 1, "a-bright-pixel-is-a-strong-edge",
         ["A bright pixel is", "a strong edge."],
         ["One 5×5 patch: an edge of 160 and one pixel 215",
          "above its neighbours. Then a bilateral filter."],
         v,
         ["Contrast cannot tell noise from an edge",
          "when the noise is the bigger jump."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 544, "weight kept for a difference Δ, σr = 80", 17, SOFT, "start", 600)
    rows = [("Δ = 0, alike", 1.0, INK), ("Δ = 20, a small bump", F.rw(20, 80), MUTED),
            ("Δ = 160, across the edge", F.rw(160, 80), LINK), ("Δ = 215, the bright pixel", F.rw(215, 80), ACCENT)]
    for k, (lab, w, col) in enumerate(rows):
        y = 580 + k * 88
        v += txt(110, y + 30, lab, 22, col, SANS, 600 if k >= 2 else 400)
        v += bar(470, y + 6, 400, 36, w, col)
        v += mono(890, y + 33, f"{w:.3f}", 22, col, "start", 600)
    v += mono(110, 970, "bright pixel: 255 → 240.5", 22, ACCENT, "start", 600)
    v += mono(110, 1010, "edge: 40 | 200 → 46.5 | 193.5", 22, LINK, "start", 600)
    v += mono(110, 1050, "a 60 among 40s → 45.6, as the Gaussian's 45.45", 20, MUTED)
    emit("feed", 2, "weight-by-value",
         ["Weight by value,", "and the bright pixel wins."],
         ["A neighbour keeps e^(−Δ²/2σr²) of its weight.",
          "The bright pixel is the bigger difference."],
         v,
         ["Any σr that keeps the 160 edge keeps",
          "the 215 pixel harder."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    step = F.patch3(F.PATCH, 0, 2)
    copy = F.patch3(F.PATCH, 4, 2)
    imp = F.patch3(F.PATCH, 2, 1)
    flat = F.patch3(F.PATCH, 0, 0)
    v += mono(110, 540, "the edge pixel and its copy at (r4, c2)", 17, LINK, "start", 600)
    v += grid3(110, 558, 62, step, 20)
    v += mono(340, 662, "=", 40, LINK, "middle", 600)
    v += grid3(392, 558, 62, copy, 20)
    v += mono(620, 652, "d² = 0", 24, LINK, "start", 600)
    v += mono(620, 686, "weight 1", 20, MUTED)
    v += mono(110, 806, "the bright pixel and its best match", 17, ACCENT, "start", 600)
    v += grid3(110, 824, 62, imp, 20, ring=(1, 1))
    v += mono(340, 928, "≠", 40, ACCENT, "middle", 600)
    v += grid3(392, 824, 62, flat, 20)
    v += mono(620, 918, "d² = 215² / 9", 24, ACCENT, "start", 600)
    v += mono(620, 952, "= 5,136", 24, ACCENT, "start", 600)
    v += mono(620, 986, "weight 0.000003 at h = 20", 20, MUTED)
    emit("feed", 3, "nl-means-asks-who-looks-like-me",
         ["NL-means asks", "who looks like me."],
         ["It compares whole 3×3 patches, not single values,",
          "with every pixel of the patch."],
         v,
         ["The edge repeats down its column.",
          "The bright pixel repeats nowhere."],
         FEED_TOTAL)


def votes(x, y, w, h, weights, values, size=26):
    out = ""
    for k, (wt, val) in enumerate(zip(weights, values)):
        xx = x + k * (w + 14)
        out += vcell(xx, y, w, h, val, size, ring=(k == 0))
        out += mono(xx + w / 2, y + h + 34, wt, 19, ACCENT if k == 0 else MUTED, "middle", 600)
    return out


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "own weight 1: OpenCV, scikit-image", 18, INK, "start", 600)
    v += votes(110, 560, 100, 90, ["1", "3e−6", "3e−6", "3e−6", "3e−6"], [255, 40, 40, 40, 40])
    v += mono(700, 618, f"→ {fv(NLM_ONE_IMP, 0)}", 40, INK, "start", 600)
    v += mono(110, 800, "own weight = largest other: IPOL", 18, INK, "start", 600)
    v += votes(110, 820, 100, 90, ["equal", "equal", "equal", "equal", "equal"], [255, 40, 40, 40, 40])
    v += mono(700, 878, f"→ {fv(NLM_MAX_IMP, 1)}", 40, ACCENT, "start", 600)
    v += mono(110, 1050, "(255 + 4 × 40) / 5 = 83.0; the edge stays exact either way", 20, MUTED)
    emit("feed", 4, "the-pixels-own-vote",
         ["255 or 83:", "the pixel's own vote."],
         ["Its four best matches are flat 40s. What decides",
          "the outcome is how much it trusts itself."],
         v,
         ["Same algorithm, one rule apart: the bright",
          "pixel survives, or loses 80% of its height."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "each face conducts g(s) = 1 / (1 + (s/80)²)", 18, SOFT, "start", 600)
    v += mono(110, 590, "a step face: g(160) = 0.2", 22, LINK, "start", 600)
    v += mono(110, 628, "a bright-pixel face: g(215) = 0.122, but four of them", 22, ACCENT, "start", 600)
    v += label(110, 700, "iteration", SOFT, "start", 15)
    v += label(330, 700, "bright pixel", ACCENT, "start", 15)
    v += label(620, 700, "edge, top row", LINK, "start", 15)
    for k in range(4):
        y = 750 + k * 74
        v += hline(110, 970, y - 40, RULE)
        v += mono(150, y, str(k), 28, INK, "middle", 600)
        v += mono(330, y, fv(PM[k][2][1], 2), 28, ACCENT, "start", 600)
        v += mono(620, y, f"{fv(PM[k][0][2], 2)} | {fv(PM[k][0][3], 2)}", 28, LINK, "start", 600)
    v += mono(110, 1070, "λ = 1/4, K = 80, no flow through the border", 19, MUTED)
    emit("feed", 5, "four-faces-against-one",
         ["Perona–Malik:", "four faces against one."],
         ["The heat equation, with a conductance on every face",
          "that falls as the difference across it grows."],
         v,
         ["Each bright-pixel face conducts less,",
          "but it has four. It drains first."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 540, "contrast over iterations, K = 80", 18, SOFT, "start", 600)
    x0, y0, w, h = 150, 580, 760, 380
    lx = lambda t: math.log(1 + t) / math.log(101)
    X = lambda t: x0 + lx(t) * w
    Y = lambda c: y0 + h - (c + 10) / 230 * h
    v += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1.5"/>'
    v += f'<line x1="{x0}" y1="{Y(0):.1f}" x2="{x0 + w}" y2="{Y(0):.1f}" stroke="{RULE}" stroke-width="1.2"/>'
    for t in (0, 1, 3, 10, 30, 100):
        v += mono(X(t), y0 + h + 32, str(t), 17, SOFT, "middle")
    imp = [F.contrasts(PM[k])[0] for k in range(101)]
    stp = [F.contrasts(PM[k])[1] for k in range(101)]
    for series, col in ((imp, ACCENT), (stp, LINK)):
        pts = " ".join(f"{X(k):.1f},{Y(c):.1f}" for k, c in enumerate(series))
        v += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="5" stroke-linejoin="round"/>'
    v += mono(X(1) + 16, Y(imp[1]) - 20, "bright pixel", 20, ACCENT, "start", 600)
    for c, lab, col in ((215, "215", ACCENT), (160, "160", LINK), (0, "0", SOFT)):
        v += mono(x0 - 14, Y(c) + 7, lab, 18, col, "end", 600)
    v += mono(X(10) + 16, Y(stp[10]) - 14, "edge", 20, LINK, "start", 600)
    v += mono(110, 1070, "both reach 0: every pixel ends at 2,815 / 25 = 112.6", 20, MUTED)
    emit("feed", 6, "diffusion-ends-at-the-mean",
         ["Diffusion ends", "at the mean."],
         ["The scheme conserves brightness, so the patch",
          "can only flatten to its average, 112.6."],
         v,
         ["The iteration count is a parameter:",
          "where you stop is the result."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 540, "method", SOFT, "start", 14)
    v += label(600, 540, "bright pixel", ACCENT, "start", 14)
    v += label(800, 540, "edge, top row", LINK, "start", 14)
    rows = [("input", F.PATCH, False), ("Gaussian, σ = 0.8", F.GAUSS, False), ("median 3×3", F.MED, True),
            ("bilateral, σr = 80", BIL, False), ("NL-means, own weight 1", F.NLM_ONE, False),
            ("NL-means, IPOL's rule", F.NLM_MAX, True), ("Perona–Malik, 3 iterations", PM[3], False)]
    for k, (lab, M, win) in enumerate(rows):
        y = 590 + k * 70
        if win:
            v += f'<rect x="90" y="{y - 40}" width="900" height="58" fill="{GREEN}" fill-opacity="0.12"/>'
        v += txt(110, y, lab, 23, INK, SANS, 600 if win else 400)
        imp = "83.0" if lab == "NL-means, IPOL's rule" else cellv(M[2][1])
        v += mono(600, y, imp, 24, ACCENT, "start", 600)
        v += mono(800, y, f"{cellv(M[0][2])} | {cellv(M[0][3])}", 24, LINK, "start", 600)
    emit("feed", 7, "only-rank-and-repetition-win",
         ["Only rank and", "repetition win here."],
         ["Six ways to smooth the patch, and what each",
          "does to the bright pixel and the edge."],
         v,
         ["The median and IPOL's NL-means keep",
          "the edge and lower the bright pixel."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("the bilateral filter", "weight by value", "keeps the bright pixel: 240.5"),
             ("non-local means", "weight by repetition", "83 or 255: the own-weight rule"),
             ("Perona–Malik", "heat with a brake on every face", "ends at the mean, 112.6"),
             ("the tooling map", "OpenCV, scikit-image, ITK, MedPy", "d = 3 is five taps, not nine")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "non-local means" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Edge-preserving", "smoothing, by hand."],
         ["Bilateral, non-local means and Perona–Malik,",
          "all on one 5×5 patch."],
         v,
         ["The full walk-through, with every number",
          "worked by hand and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = mono(150, 790, "row r2 of the patch", 20, SOFT, "start", 600)
    v += "".join(vcell(150 + j * 156, 812, 156, 140, F.PATCH[2][j], 34, j == 1) for j in range(5))
    v += mono(150, 1050, "after a bilateral filter, σr = 80", 22, ACCENT, "start", 600)
    v += "".join(vcell(150 + j * 156, 1072, 156, 140, BIL[2][j], 30, j == 1) for j in range(5))
    v += txt(150, 1300, "the edge kept, and the bright pixel too", 30, MUTED)
    emit("story", 1, "a-bright-pixel-is-a-strong-edge",
         ["A bright pixel is", "a strong edge."],
         ["One 5×5 patch,", "one bilateral filter, by hand."],
         v,
         ["Contrast cannot tell noise from an edge",
          "when the noise is the bigger jump."],
         STORY_TOTAL)


def story_02():
    v = mono(150, 800, "weight a neighbour keeps, σr = 80", 22, SOFT, "start", 600)
    v += txt(150, 900, "across the edge (160)", 34, LINK, SANS, 600)
    v += bar(150, 930, 780, 70, F.rw(160, 80), LINK)
    v += mono(150, 1070, "0.135", 64, LINK, "start", 600)
    v += txt(150, 1190, "beside the bright pixel (215)", 34, ACCENT, SANS, 600)
    v += bar(150, 1220, 780, 70, F.rw(215, 80), ACCENT)
    v += mono(150, 1360, "0.027", 64, ACCENT, "start", 600)
    emit("story", 2, "0-135-against-0-027",
         ["0.135 against", "0.027."],
         ["What a neighbour keeps of its weight,", "across the edge and beside the pixel."],
         v,
         ["The bright pixel is the bigger jump,", "so it is the better protected."],
         STORY_TOTAL)


def story_03():
    v = mono(150, 800, "own weight 1 (OpenCV, scikit-image)", 22, INK, "start", 600)
    v += votes(150, 830, 140, 120, ["1", "3e−6", "3e−6", "3e−6", "3e−6"], [255, 40, 40, 40, 40], 32)
    v += mono(150, 1070, f"→ {fv(NLM_ONE_IMP, 0)}", 52, INK, "start", 600)
    v += mono(150, 1170, "own weight = largest other (IPOL)", 22, INK, "start", 600)
    v += votes(150, 1200, 140, 120, ["equal"] * 5, [255, 40, 40, 40, 40], 32)
    v += mono(150, 1440, f"→ {fv(NLM_MAX_IMP, 1)}", 52, ACCENT, "start", 600)
    emit("story", 3, "the-pixels-own-vote",
         ["One rule:", "255 or 83."],
         ["Non-local means, and how much", "a pixel trusts itself."],
         v,
         ["IPOL caps the pixel's own weight.", "OpenCV and scikit-image do not."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["bilateral: weight by value",
             "NL-means: weight by repetition",
             "Perona–Malik: heat with a brake",
             "the bright pixel: who keeps it"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 1 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Three ways to smooth", "without blurring."],
         ["Worked by hand on one", "5×5 patch."],
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
