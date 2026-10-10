#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "The 2-D DFT".

Image Processing by Hand, part 5. The shell (lockup, rule, serif title, deck, takeaway,
footer) is copied from part 4's _social.py, with the lockup reading "canery.in". Every
number on a card comes from `_figs.py` — the patch's 2-D DFT, the phase-only and
magnitude-only rebuilds, the swap with the transpose, the notch on the tiled patch and the
operation-count model — so a card cannot disagree with the article. Pixel cells follow the
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
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/the-2d-dft-spectra-phase-filtering"
FOOTER = "THE 2-D DFT · CANERY.IN"

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
LMAX = math.log10(1 + 2815)
ORDER = F.shift_order(5)
OFF_RMS = {"unfiltered": 14.14, "±3 only": 10.78, "±2 and ±3": 13.43, "eight bins": 17.43}
FFT_1080 = F.fft_route(1920, 1080, 11)
assert round(FFT_1080, 1) == 169.8
assert round(F.PH_ONLY[2][1], 2) == 0.84 and round(F.MAG_ONLY[0][0], 1) == 427.7


def fnum(v, nd=1):
    s = f"{v:.{nd}f}"
    if s.lstrip("-").strip("0.") == "":
        s = s.lstrip("-")
    return s.replace("-", "−")


# ------------------------------------------------------------------ shared visuals
def shaded(x, y, w, h, t, stroke="rgba(45,49,66,0.35)", sw=1.5):
    t = max(0.0, min(1.0, t))
    a = 0.85 * (1 - t) + 0.04
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"/>')


def spectrum(x, y, cw, size=26):
    """The patch's centred |F|, log-shaded as in Figure 2; DC outlined in the accent."""
    v = ""
    for i, kr in enumerate(ORDER):
        for j, kc in enumerate(ORDER):
            m = abs(F.FA[kr][kc])
            t = math.log10(1 + m) / LMAX
            v += shaded(x + j * cw, y + i * cw, cw, cw, t)
            shown = f"{round(m)}" if abs(m - round(m)) < 1e-6 else fnum(m)
            v += mono(x + j * cw + cw / 2, y + i * cw + cw / 2 + size * 0.36, shown, size,
                      "#ffffff" if t < 0.52 else INK, "middle", 600)
    v += (f'<rect x="{x + 2 * cw}" y="{y + 2 * cw}" width="{cw}" height="{cw}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="5"/>')
    v += (f'<rect x="{x - 4}" y="{y + 2 * cw - 4}" width="{5 * cw + 8}" height="{cw + 8}" fill="none" '
          f'stroke="{BLUE}" stroke-width="3" stroke-dasharray="10,7"/>')
    return v


def value_grid(x, y, cw, A, lo, hi, fmtv, size=24, mark=None):
    v = ""
    for r, row in enumerate(A):
        for c, val in enumerate(row):
            t = (val - lo) / (hi - lo)
            v += shaded(x + c * cw, y + r * cw, cw, cw, t)
            v += mono(x + c * cw + cw / 2, y + r * cw + cw / 2 + size * 0.36, fmtv(val), size,
                      "#ffffff" if t < 0.52 else INK, "middle", 600)
    if mark:
        r, c = mark
        v += (f'<rect x="{x + c * cw}" y="{y + r * cw}" width="{cw}" height="{cw}" fill="none" '
              f'stroke="{ACCENT}" stroke-width="5"/>')
    return v


def pixel_cell(x, y, w, h, val, size=28, hi=False):
    t = val / 255
    v = shaded(x, y, w, h, t, ACCENT if hi else "rgba(45,49,66,0.35)", 4 if hi else 1.5)
    return v + mono(x + w / 2, y + h / 2 + size * 0.36, f"{val}", size,
                    "#ffffff" if t < 0.52 else INK, "middle", 600)


def arrow(cx, cy, L, d, colour, sw=5):
    a = math.radians(d)
    ux, uy = math.cos(a), -math.sin(a)
    tipx, tipy = cx + L * ux, cy + L * uy
    head, half = 20, 11
    bx, by = tipx - head * ux, tipy - head * uy
    v = (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{L + 6:.1f}" fill="#ffffff" stroke="{RULE_SOLID}" '
         f'stroke-width="2"/>')
    v += (f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{colour}" '
          f'stroke-width="{sw}"/>')
    v += (f'<polygon points="{tipx:.1f},{tipy:.1f} {bx - half * uy:.1f},{by + half * ux:.1f} '
          f'{bx + half * uy:.1f},{by - half * ux:.1f}" fill="{colour}"/>')
    return v


def rms_bars(x0, y, big=False):
    rows = [("no filter", OFF_RMS["unfiltered"], MUTED),
            ("notch ±3 only", OFF_RMS["±3 only"], GREEN),
            ("notch ±2 and ±3", OFF_RMS["±2 and ±3"], INK),
            ("notch eight bins", OFF_RMS["eight bins"], ACCENT)]
    w, bh, gap, size = (420, 50, 80, 26) if not big else (420, 60, 108, 30)
    lab_w = 330 if not big else 360
    v = label(x0, y - 26, "rms error, grey levels · bands at 2.5 cycles", SOFT, "start", 15 if not big else 17)
    for name, val, col in rows:
        v += txt(x0, y + bh * 0.72, name, size, col, SANS, 600)
        bw = val / 18 * w
        v += (f'<rect x="{x0 + lab_w}" y="{y}" width="{bw:.1f}" height="{bh}" rx="3" fill="{col}" '
              f'fill-opacity="{0.9 if col == ACCENT else 0.65}"/>')
        v += mono(x0 + lab_w + bw + 16, y + bh * 0.74, f"{val:.1f}", size, col, "start", 600)
        y += gap
    return v, y


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += spectrum(110, 524, 104, 24)
    v += label(110, 1100, "|F(kr, kc)| centred · kc across, kr down", SOFT, "start", 14)
    v += txt(680, 600, "2,815", 40, ACCENT, SANS, 600)
    v += txt(680, 636, "DC: the pixel sum", 20, MUTED)
    v += txt(680, 730, "1,079 · 709", 34, BLUE, SANS, 600)
    v += txt(680, 766, "the edge's row", 20, MUTED)
    v += txt(680, 860, "215", 40, INK, SANS, 600)
    v += txt(680, 896, "every other bin:", 20, MUTED)
    v += txt(680, 924, "the bright pixel", 20, MUTED)
    emit("feed", 1, "a-spectrum-says-how-much",
         ["A spectrum says how much.", "Phase says where."],
         ["The series' 5×5 patch, transformed by hand: one vertical edge,",
          "one bright pixel, 25 coefficients."],
         v,
         ["The edge prints a horizontal line; the pixel prints a flat floor.",
          "Where anything sits is in the phase, not here."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 540, "the floor's phase along kc, at kr = 1", SOFT, "start", 15)
    for i, kc in enumerate(range(5)):
        d = F.deg(F.FA[1][kc])
        cx = 170 + i * 176
        v += arrow(cx, 640, 52, d, MUTED)
        v += mono(cx, 730, f"{fnum(round(d), 0)}°", 24, INK, "middle", 600)
        v += label(cx, 764, f"kc {kc}", SOFT, "middle", 14)
    v += txt(110, 830, "−72° per step along kc  →  column 1", 28, ACCENT, SANS, 600)
    v += txt(110, 878, "−144° per step along kr  →  row 2", 28, ACCENT, SANS, 600)
    v += hline(110, 970, 930)
    v += mono(110, 990, "every floor bin: 215 at angle −72°·(2kr + kc)", 24, INK)
    v += mono(110, 1036, "shift one column right: each turns −72°·kc", 24, MUTED)
    emit("feed", 2, "position-is-a-phase-ramp",
         ["One bright pixel is", "every wave at once."],
         ["Its magnitude is 215 in every bin. Its position is the",
          "slope of the phase, read straight off the arrows."],
         v,
         ["Moving an image changes no magnitude at all.",
          "Every arrow turns in proportion to its frequency."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    ph = [[x * 100 for x in row] for row in F.PH_ONLY]
    v += label(110, 534, "phase only, × 100", ACCENT, "start", 15)
    v += value_grid(110, 556, 78, ph, -16, 84, lambda x: f"{x:.0f}".replace("-", "−"), 22, mark=(2, 1))
    v += label(590, 534, "magnitude only", INK, "start", 15)
    v += value_grid(590, 556, 78, F.MAG_ONLY, 60, 428, lambda x: f"{x:.0f}", 22, mark=(0, 0))
    v += txt(110, 1000, "impulse stays at (2, 1)", 24, ACCENT, SANS, 600)
    v += txt(110, 1034, "dark left, bright right", 20, MUTED)
    v += txt(590, 1000, "impulse moves to (0, 0)", 24, INK, SANS, 600)
    v += txt(590, 1034, "the step becomes a hump", 20, MUTED)
    emit("feed", 3, "keep-the-phase-keep-the-layout",
         ["Keep the phase,", "keep the layout."],
         ["Rebuild the patch from phase alone, with every magnitude",
          "set to 1, then from magnitude alone, with phase set to 0."],
         v,
         ["Phase holds where things are.",
          "Magnitude alone moves everything to the origin."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 534, "|A| with the phase of B = Aᵀ", SOFT, "start", 15)
    v += value_grid(110, 556, 92, F.SWAP_AB, 0, 400, lambda x: f"{x:.0f}", 24, mark=(1, 2))
    v += (f'<rect x="{110 + 2 * 92 - 5}" y="{556 - 5}" width="{92 + 10}" height="{5 * 92 + 10}" fill="none" '
          f'stroke="{BLUE}" stroke-width="3" stroke-dasharray="10,7"/>')
    v += txt(640, 600, "393 at (1, 2)", 30, ACCENT, SANS, 600)
    v += txt(640, 636, "B's impulse, from B's phase", 20, MUTED)
    v += txt(640, 730, "rows 3–4 brighter", 30, INK, SANS, 600)
    v += txt(640, 766, "B's step, from B's phase", 20, MUTED)
    v += txt(640, 860, "a vertical bar", 30, BLUE, SANS, 600)
    v += txt(640, 896, "A's edge runs that way:", 20, MUTED)
    v += txt(640, 924, "from A's magnitude", 20, MUTED)
    emit("feed", 4, "neither-image-wins",
         ["Swap the halves and", "neither image wins."],
         ["Magnitude from the patch, phase from the patch turned on",
          "its side. The result belongs to neither."],
         v,
         ["Phase decided where; magnitude decided which way.",
          "Photographs share a roughly 1/f magnitude, so there phase wins."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    row = [200, 200, 40, 40, 40, 200, 200, 40, 40]
    v += label(110, 540, "row r0, as the DFT sees it: tiled", SOFT, "start", 15)
    cw = 96
    for i, val in enumerate(row):
        x = 110 + i * cw
        v += pixel_cell(x, 568, cw, 96, val, 28)
        if 2 <= i <= 6:
            pass
    v += (f'<rect x="{110 + 2 * cw}" y="568" width="{5 * cw}" height="96" fill="none" stroke="{INK}" '
          f'stroke-width="4"/>')
    for k in (2, 7):
        x = 110 + k * cw
        v += f'<line x1="{x}" y1="548" x2="{x}" y2="684" stroke="{ACCENT}" stroke-width="6"/>'
    v += label(110 + 4.5 * cw, 716, "the patch's row", INK, "middle", 15)
    v += txt(110, 790, "200 → 40 at every tile border:", 28, ACCENT, SANS, 600)
    v += txt(110, 828, "a step of −160 the patch does not contain", 24, INK)
    v += hline(110, 970, 880)
    v += mono(110, 936, "left ≠ right  →  a line through DC", 24, INK)
    v += mono(110, 978, "top ≠ bottom  →  another: the cross", 24, INK)
    v += mono(110, 1040, "fixes: taper · mirror · periodic + smooth", 24, GREEN, "start", 600)
    emit("feed", 5, "the-dft-sees-a-tile",
         ["Your DFT thinks", "the image is a tile."],
         ["Across the right border, the 200 of the last column runs",
          "straight into the next tile's 40."],
         v,
         ["Before you read a spectrum, taper, mirror or split.",
          "Zero padding to a fast size adds a jump of its own."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += txt(110, 556, "3 cycles in 10 rows", 30, INK, SANS, 600)
    v += mono(110, 596, "two bins, (±3, 0), both empty in the tile", 22, MUTED)
    v += mono(110, 632, "two-bin notch: error 3 × 10⁻¹², exact", 22, GREEN, "start", 600)
    v += hline(110, 970, 676)
    v += txt(110, 730, "2.5 cycles in 10 rows: every bin", 30, INK, SANS, 600)
    bars_svg, _ = rms_bars(110, 790)
    v += bars_svg
    emit("feed", 6, "a-notch-is-exact-only-on-bin",
         ["A notch is exact", "only on-bin."],
         ["Bands that fit the frame land on two empty bins.",
          "Bands that don't leak into the image's own."],
         v,
         ["A notch's width is a bet on what the image doesn't",
          "contain. Crop to whole cycles: at 20 rows it's exact again."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 540, "operations per pixel, 1920 × 1080 · counted, not timed", SOFT, "start", 15)
    ms = [3, 5, 7, 9, 10, 11, 13]
    v += label(110, 588, "m × m", SOFT, "start", 14)
    v += label(430, 588, "direct 2m²", SOFT, "end", 14)
    v += label(700, 588, "fft route", SOFT, "end", 14)
    v += label(740, 588, "cheaper", SOFT, "start", 14)
    y = 636
    for m in ms:
        d, f_ = 2 * m * m, F.fft_route(1920, 1080, m)
        cheaper = "direct" if d < f_ else "fft"
        col = ACCENT if m == 10 else INK
        v += mono(110, y, f"{m} × {m}", 24, col, "start", 600 if m == 10 else 400)
        v += mono(430, y, f"{d}", 24, col, "end", 600 if d < f_ else 400)
        v += mono(700, y, f"{f_:.1f}", 24, col, "end", 600 if f_ <= d else 400)
        v += mono(740, y, cheaper, 22, GREEN if cheaper == "direct" else ACCENT, "start", 600)
        y += 46
    v += hline(110, 970, y - 14)
    v += mono(110, y + 26, "OpenCV filter2D switches at area ≥ 130: 12 × 12", 21, MUSTARD)
    v += mono(110, y + 60, "SciPy's model: 3 × 3 · textbook ratio: 7 × 7", 21, MUTED)
    emit("feed", 7, "the-fft-is-a-fixed-toll",
         ["The FFT round trip", "is a fixed toll."],
         ["About 170 operations per pixel whatever the kernel.",
          "A full m × m kernel costs 2m²."],
         v,
         ["The crossover depends on what you count",
          "and on whose direct loop you race."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("read a spectrum", "fftshift on odd sizes, the cross, log scale", "DC 65% of the energy"),
             ("what phase keeps", "phase-only rebuilds, the swap, phase correlation", "a ridge becomes one peak"),
             ("filter there", "zero-phase gains, padding, notches", "exact on-bin, a bet off it"),
             ("what it costs", "four answers to the crossover", "≈ 10 × 10 by count, 12 × 12 on OpenCV's fast path")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "what phase keeps" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["The 2-D DFT,", "by hand."],
         ["Spectra, phase, notches and the FFT crossover,",
          "all on one 5×5 patch."],
         v,
         ["The full walk-through, with the tooling map for",
          "NumPy, OpenCV, SciPy and scikit-image."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = spectrum(220, 752, 128, 28)
    v += label(540, 1446, "the edge's row · the pixel's floor of 215", SOFT, "middle", 17)
    emit("story", 1, "a-spectrum-says-how-much",
         ["A spectrum says how", "much. Phase says where."],
         ["One edge, one bright pixel,", "25 coefficients, by hand."],
         v,
         ["One bright pixel: 215 in every bin.", "Its position is only in the phase."],
         STORY_TOTAL)


def story_02():
    ph = [[x * 100 for x in row] for row in F.PH_ONLY]
    v = label(150, 760, "phase only, × 100", ACCENT, "start", 18)
    v += value_grid(150, 784, 104, ph, -16, 84, lambda x: f"{x:.0f}".replace("-", "−"), 26, mark=(2, 1))
    v += txt(720, 1000, "impulse", 30, ACCENT, SANS, 600)
    v += txt(720, 1040, "stays at (2, 1)", 26, MUTED)
    v += txt(150, 1372, "Magnitude only: the impulse moves", 28, INK, SANS, 600)
    v += txt(150, 1412, "to (0, 0), with the value 428.", 28, INK, SANS, 600)
    emit("story", 2, "keep-the-phase-keep-the-layout",
         ["Keep the phase,", "keep the layout."],
         ["Every magnitude set to 1;", "only the phase kept."],
         v,
         ["Phase holds where things are.", "Magnitude alone moves them to the corner."],
         STORY_TOTAL)


def story_03():
    v = txt(110, 790, "3 cycles in 10 rows: exact", 34, GREEN, SANS, 600)
    v += txt(110, 836, "two empty bins, a two-bin notch", 26, MUTED)
    bars_svg, _ = rms_bars(110, 950, big=True)
    v += bars_svg
    emit("story", 3, "a-notch-is-exact-only-on-bin",
         ["A notch is exact", "only on-bin."],
         ["At 2.5 cycles the bands leak", "into the image's own bins."],
         v,
         ["Crop to whole cycles first.", "At 20 rows the notch is exact again."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["magnitude: how much, which way",
             "phase: where",
             "notch: only where the image is empty",
             "FFT: a toll of ~170 per pixel at 1080p"]
    y = 900
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 32, INK, SANS, 600 if i == 1 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Four readings of", "every spectrum."],
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
