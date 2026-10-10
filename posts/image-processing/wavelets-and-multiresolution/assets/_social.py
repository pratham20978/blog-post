#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Wavelets and Multiresolution".

Image Processing by Hand, part 6. The shell (lockup, rule, serif title, deck, takeaway,
footer) is copied from part 5's _social.py, with the lockup reading "canery.in". Every
number on a card comes from `_figs.py` — the Haar and 5/3 lifting of the patch's rows, the
2-D Haar level, the coefficient counts, the shift cases and the thresholded patch — so a
card cannot disagree with the article. Pixel cells follow the article: high value = bright.

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
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/wavelets-and-multiresolution"
FOOTER = "WAVELETS AND MULTIRESOLUTION · CANERY.IN"

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
H0S, H0D = F.H0[0], F.H0[1]                        # Haar on r0: [40, 120, 200], [0, 160]
L0S, L0D = F.L0[0], F.L0[1]                        # 5/3 on r0: [40, 60, 240], [0, 80]
L2S, L2D, L2U = F.L2                               # integer 5/3 on r2
SOFT50 = F.threshold_patch(50, "soft")
assert H0D == [0, 160] and L0D == [0, 80] and L0S == [40, 60, 240]
assert L2S == [148, 114, 240] and L2D == [215, 80] and L2U == [108, 74, 40]
assert F.inv53(L2S, L2D) == F.ROW2
assert SOFT50[2][:2] == [65, 180] and SOFT50[0][2:4] == [65, 175]
COUNTS = [("lifting (JPEG 2000)", 25, ACCENT), ("PyWavelets haar", 36, BLUE),
          ("PyWavelets bior2.2", 100, BLUE), ("PyWavelets bior4.4", 196, BLUE),
          ("Laplacian pyramid", 39, MUSTARD)]
assert [round(b[3] * 25) for b in F.BUDGET] == [25, 36, 100, 196, 39]


def fv(v):
    s = f"{int(round(v))}" if abs(v - round(v)) < 1e-9 else f"{v:g}"
    return s.replace("-", "−")


# ------------------------------------------------------------------ shared visuals
def shaded(x, y, w, h, t, stroke="rgba(45,49,66,0.35)", sw=1.5):
    t = max(0.0, min(1.0, t))
    a = 0.85 * (1 - t) + 0.04
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"/>')


def vcell(x, y, w, h, val, size=26, hi=255.0, ring=False):
    t = val / hi
    v = shaded(x, y, w, h, t, ACCENT if ring else "rgba(45,49,66,0.35)", 4 if ring else 1.5)
    return v + mono(x + w / 2, y + h / 2 + size * 0.36, fv(val), size,
                    "#ffffff" if t < 0.52 else INK, "middle", 600)


def dcell(x, y, w, h, val, size=26, ring=False, faint=False):
    v = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#ffffff" '
         f'stroke="{ACCENT if ring else "rgba(45,49,66,0.35)"}" stroke-width="{4 if ring else 1.5}"/>')
    return v + mono(x + w / 2, y + h / 2 + size * 0.36, fv(val), size,
                    RULE_SOLID if faint else INK, "middle", 600)


def cells(x, y, cw, ch, vals, size=26, ring=None, detail=False, hi=255.0):
    out = ""
    for i, v in enumerate(vals):
        r = ring is not None and i in ring
        out += dcell(x + i * cw, y, cw, ch, v, size, r) if detail else vcell(x + i * cw, y, cw, ch, v, size, hi, r)
    return out


def pair_cells(x, y, cw, ch, vals, size=26, ring=None, detail=False):
    """Cells aligned with the Haar pairs of a 5-sample row: (c0, c1), (c2, c3), then c4 alone."""
    out, xx = "", x
    for i, v in enumerate(vals):
        w = 2 * cw if i < 2 else cw
        r = ring is not None and i in ring
        out += dcell(xx, y, w, ch, v, size, r) if detail else vcell(xx, y, w, ch, v, size, 255.0, r)
        xx += w
    return out


def dft_floor(x, y, cw, size=20):
    out = ""
    for r in range(5):
        for c in range(5):
            out += shaded(x + c * cw, y + r * cw, cw, cw, 0.62)
            out += mono(x + c * cw + cw / 2, y + r * cw + cw / 2 + size * 0.36, "215", size, INK, "middle", 600)
    return out


def subbands(x, y, cw, gap, size=18):
    """The impulse's own contribution to one Haar level: one coefficient of 107.5 per subband."""
    out = ""
    names = ["LL", "HL", "LH", "HH"]
    for q, (qx, qy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):
        ox, oy = x + qx * (3 * cw + gap), y + qy * (3 * cw + gap + 26)
        out += label(ox, oy - 10, names[q], SOFT, "start", 14)
        for i in range(3):
            for j in range(3):
                hit = (i, j) == (1, 0)
                out += dcell(ox + j * cw, oy + i * cw, cw, cw, 107.5 if hit else 0, size, hit, not hit)
    return out


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 540, "the pixel in fourier · 25 bins of 215", SOFT, "start", 15)
    v += dft_floor(110, 566, 64, 19)
    v += txt(110, 948, "each bin: 4% of the pixel's energy", 22, MUTED)
    v += label(600, 540, "in one haar level · 4 coefficients", ACCENT, "start", 15)
    v += subbands(598, 590, 62, 14, 15)
    v += txt(600, 1052, "each: 25% of its energy", 22, ACCENT, SANS, 600)
    emit("feed", 1, "four-numbers-not-twenty-five",
         ["One bright pixel:", "25 numbers, or 4."],
         ["The series' 5×5 patch has one pixel of 255 among 40s.",
          "Fourier spreads it everywhere; a wavelet does not."],
         v,
         ["A wavelet coefficient knows where it is:",
          "the pixel lands in one coefficient per subband."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 544, "row r0 of the patch", SOFT, "start", 15)
    v += cells(110, 562, 112, 96, F.ROW0, 30)
    v += label(110, 718, "detail · odd sample − its left neighbour", ACCENT, "start", 15)
    v += pair_cells(110, 736, 112, 96, H0D, 30, ring=[1], detail=True)
    v += txt(600, 794, "pair across the step: 160", 24, INK, SANS, 600)
    v += label(110, 892, "coarse · each pair's average", SOFT, "start", 15)
    v += pair_cells(110, 910, 112, 96, H0S, 30)
    v += txt(110, 1056, "c4 has no partner: it passes through", 22, MUTED)
    emit("feed", 2, "a-haar-level-is-a-prediction-error",
         ["A Haar level is a", "prediction error."],
         ["Predict each odd sample from its left neighbour,",
          "keep the error, then average the pair."],
         v,
         ["Smooth data costs nothing; an edge inside a pair",
          "costs its height. Five samples in, five numbers out."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 544, "the same row through the 5/3", SOFT, "start", 15)
    v += cells(110, 562, 112, 96, F.ROW0, 30)
    v += label(110, 718, "detail · odd − ⌊(left + right) / 2⌋", ACCENT, "start", 15)
    v += pair_cells(110, 736, 112, 96, L0D, 30, ring=[1], detail=True)
    v += txt(600, 794, "the step costs half: 80", 24, INK, SANS, 600)
    v += label(110, 892, "coarse · even + ⌊(dL + dR + 2) / 4⌋", SOFT, "start", 15)
    v += pair_cells(110, 910, 112, 96, L0S, 30)
    v += mono(110, 1056, "240 = (−40 + 400 + 1200 + 400 − 40) / 8", 20, MUTED)
    emit("feed", 3, "the-5-3-pays-half-for-an-edge",
         ["The 5/3 pays half", "for an edge."],
         ["JPEG 2000's reversible wavelet predicts from both",
          "neighbours, so a straight line costs nothing."],
         v,
         ["Its coarse row is no block average: the low-pass",
          "overshoots to 240 beside the mirrored step."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 540, "row r2 · forward, rounding inside the steps", SOFT, "start", 15)
    v += cells(110, 558, 104, 86, F.ROW2, 28)
    v += mono(110, 700, "update: ⌊432/4⌋ = 108 · ⌊297/4⌋ = 74 · ⌊162/4⌋ = 40", 21, ACCENT, "start", 600)
    v += label(110, 748, "coarse", SOFT, "start", 14)
    v += cells(110, 762, 104, 86, L2S, 28)
    v += label(470, 748, "detail", SOFT, "start", 14)
    v += cells(470, 762, 104, 86, L2D, 28, detail=True)
    v += mono(110, 900, "exact arithmetic: 147.5, 113.75, 240", 21, MUTED)
    v += label(110, 950, "inverse · subtract the same 108, 74, 40", SOFT, "start", 15)
    v += cells(110, 968, 104, 86, F.inv53(L2S, L2D), 28, ring=[1])
    emit("feed", 4, "integers-in-integers-out",
         ["Integers in,", "integers out."],
         ["Lifting rounds inside each step; the inverse",
          "recomputes the same rounded numbers."],
         v,
         ["That is how JPEG 2000 codes losslessly",
          "with its 5/3 wavelet."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 540, "coefficients for the 5×5 patch (25 pixels)", SOFT, "start", 15)
    x0, w, xmax = 430, 470, 200.0
    for k, (lab, n, col) in enumerate(COUNTS):
        y = 576 + k * 78
        v += txt(110, y + 32, lab, 22, INK, SANS, 600 if k == 0 else 400)
        v += f'<rect x="{x0}" y="{y + 6}" width="{n / xmax * w:.1f}" height="40" fill="{col}" fill-opacity="0.85"/>'
        v += mono(x0 + n / xmax * w + 12, y + 35, f"{n}", 24, INK, "start", 600)
    v += mono(110, 1000, "1920×1080, five levels: haar +0.01% · bior2.2 +1.2%", 19, MUTED)
    v += mono(110, 1030, "bior4.4 +2.3% · Laplacian pyramid +33% (4/3)", 19, MUTED)
    v += mono(110, 1064, "the patch's pyramid: 39 for 25, +56%", 19, MUSTARD, "start", 600)
    emit("feed", 5, "the-coefficient-budget",
         ["N pixels,", "N coefficients."],
         ["Lifting keeps exactly one number per pixel.",
          "Library padding and the pyramid keep more."],
         v,
         ["The padding fades on large images;",
          "the pyramid's extra third never does."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    rows = [("step at c2 | c3", F.SHIFTS[0][1], H0D, L0D, False, False),
            ("step one pixel left", F.SHIFTS[1][1], F.haar_lift(F.SHIFTS[1][1])[1],
             F.lift53(F.SHIFTS[1][1], False)[1], True, False),
            ("impulse at odd c1", F.SHIFTS[3][1], F.haar_lift(F.SHIFTS[3][1])[1],
             F.lift53(F.SHIFTS[3][1], False)[1], False, False),
            ("impulse at even c2", F.SHIFTS[4][1], F.haar_lift(F.SHIFTS[4][1])[1],
             F.lift53(F.SHIFTS[4][1], False)[1], False, True)]
    v += label(520, 534, "haar d", SOFT, "start", 14)
    v += label(760, 534, "5/3 d", SOFT, "start", 14)
    for k, (lab, row, hd, fd, hlost, fsplit) in enumerate(rows):
        y = 556 + k * 132
        v += label(110, y - 6 + 0, lab, MUTED, "start", 13)
        v += cells(110, y + 6, 76, 70, row, 20)
        v += cells(520, y + 6, 100, 70, hd, 22, ring=[0, 1] if hlost else None, detail=True)
        v += cells(760, y + 6, 106, 70, fd, 20, ring=[0, 1] if fsplit else None, detail=True)
    emit("feed", 6, "one-pixel-empties-a-subband",
         ["Move the edge", "one pixel."],
         ["Decimated wavelets are not shift-invariant,",
          "and each filter fails on a different feature."],
         v,
         ["Haar loses the step at level 1; the 5/3 keeps it",
          "but halves the impulse's detail energy."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 540, "the patch", SOFT, "start", 15)
    for r in range(5):
        for c in range(5):
            v += vcell(110 + c * 74, 560 + r * 74, 74, 74, F.PATCH[r][c], 20, ring=(r, c) == (2, 1))
    v += label(560, 540, "soft threshold, λ = 50", ACCENT, "start", 15)
    for r in range(5):
        for c in range(5):
            v += vcell(560 + c * 74, 560 + r * 74, 74, 74, SOFT50[r][c], 20, ring=(r, c) == (2, 1))
    v += mono(110, 978, "edge across c2 | c3: 160 → 110 in every row", 21, INK, "start", 600)
    v += mono(110, 1012, "impulse 255 → 180; hard thresholding: unchanged", 21, MUTED)
    v += mono(110, 1046, "λ = σ√(2 ln N) = 4.995σ at 512×512: 50 for σ = 10", 21, MUTED)
    emit("feed", 7, "soft-thresholding-taxes-every-edge",
         ["Soft thresholding", "taxes every edge."],
         ["Noise stays σ in every orthonormal coefficient;",
          "the image gathers in a few large ones."],
         v,
         ["Soft takes λ off every survivor; hard keeps it",
          "whole or kills it."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("one level by hand", "Haar and the 5/3 on one row", "an edge costs 160, or 80"),
             ("the budget", "N numbers, not 4/3 N", "PyWavelets pads: 25 → 36 or 100"),
             ("lifting", "integers in, integers out", "JPEG 2000's lossless path"),
             ("the price", "shift variance, thresholds", "one pixel empties a subband")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "lifting" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Wavelets and", "multiresolution, by hand."],
         ["Haar, lifting, JPEG 2000 and denoising,",
          "all on one 5×5 patch."],
         v,
         ["The full walk-through, with the tooling map for",
          "PyWavelets, scikit-image and Pillow."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = label(150, 790, "the pixel in fourier · 215 × 25", SOFT, "start", 17)
    v += dft_floor(150, 812, 64, 18)
    v += label(560, 790, "haar · 4 coefficients", ACCENT, "start", 17)
    v += subbands(560, 840, 60, 14, 15)
    v += txt(150, 1310, "4% each, everywhere", 30, MUTED)
    v += txt(560, 1310, "25% each, one place", 30, ACCENT, SANS, 600)
    emit("story", 1, "four-numbers-not-twenty-five",
         ["One bright pixel:", "25 numbers, or 4."],
         ["The series' 5×5 patch,", "one wavelet level, by hand."],
         v,
         ["A wavelet coefficient knows where it is.",
          "Fourier spreads the pixel everywhere."],
         STORY_TOTAL)


def story_02():
    v = label(150, 790, "row r0", SOFT, "start", 18)
    v += cells(150, 812, 156, 120, F.ROW0, 34)
    v += label(150, 1010, "haar detail", SOFT, "start", 18)
    v += pair_cells(150, 1032, 156, 120, H0D, 34, ring=[1], detail=True)
    v += label(150, 1230, "5/3 detail", ACCENT, "start", 18)
    v += pair_cells(150, 1252, 156, 120, L0D, 34, ring=[1], detail=True)
    v += txt(800, 1104, "whole step", 30, MUTED)
    v += txt(800, 1324, "half step", 30, ACCENT, SANS, 600)
    emit("story", 2, "an-edge-costs-its-height",
         ["An edge costs", "its height, or half."],
         ["Predict each odd sample;", "keep only the error."],
         v,
         ["Smooth data costs nothing.", "Five samples in, five numbers out."],
         STORY_TOTAL)


def story_03():
    v = label(150, 790, "haar · step inside a pair", SOFT, "start", 18)
    v += cells(150, 812, 156, 120, F.ROW0, 34)
    v += pair_cells(150, 952, 156, 110, H0D, 32, detail=True)
    v += label(150, 1140, "haar · step one pixel left", ACCENT, "start", 18)
    v += cells(150, 1162, 156, 120, F.SHIFTS[1][1], 34)
    v += pair_cells(150, 1302, 156, 110, F.haar_lift(F.SHIFTS[1][1])[1], 32, ring=[0, 1], detail=True)
    emit("story", 3, "one-pixel-empties-a-subband",
         ["Move the edge", "one pixel."],
         ["Decimated wavelets are", "not shift-invariant."],
         v,
         ["The level-1 detail drops from 160 to 0.",
          "The step reappears a level down."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["a coefficient: local, at one scale",
             "lifting: N numbers, exact integers",
             "JPEG 2000: the 5/3 and the 9/7",
             "the price: shift variance"]
    y = 900
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 32, INK, SANS, 600 if i == 1 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Four things a", "wavelet level does."],
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
