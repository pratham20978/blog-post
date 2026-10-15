#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Colour and Gamma: Luma, Luminance and the
Spaces in Between".

Image Processing by Hand, part 13. The shell (lockup, rule, serif title, deck, takeaway, footer) is
copied from part 12's _social.py (itself from parts 9 and 11, with the lockup reading "canery.in" as in
part 10). Every number on a card comes from `_data.py` — the decoded codes, the azure's luma and
luminance greys, the blurred step, the codes per lightness band, the weights from primaries and the
all-colour luma range — so a card cannot disagree with the article. Colours follow the figures:
tangerine is a computation on codes, blue a computation on light, and swatches carry their true sRGB
values.

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
CANONICAL = "canery.in/blogs/colour-and-gamma"
FOOTER = "COLOUR AND GAMMA · CANERY.IN"

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
assert round(d.AZ_LUMA) == 158 and round(d.AZ_LUMGREY) == 186 and d.MID_CODES == 120
assert f"{d.enc8(d.MID_LIGHT):.1f}" == "148.7" and d.BANDS_LIN[0] == 3 and d.BANDS_LIN[-1] == 61
WHITE = "#ffffff"
LINE = "rgba(45,49,66,0.40)"


def rgb(t):
    return f"rgb({t[0]},{t[1]},{t[2]})"


def grey(v):
    g = max(0, min(255, round(v)))
    return f"rgb({g},{g},{g})"


def on(v):
    """White text on darker greys, ink on lighter ones; the switch at code 135 keeps both above 3:1."""
    return WHITE if v < 135 else INK


def sw(x, y, w, h, fill, stroke=LINE, width=1.2):
    return rect(x, y, w, h, fill, stroke, width)


def fmt1(v):
    return f"{v:,.1f}".replace("-", "−") if abs(v - round(v)) > 1e-9 else f"{round(v):,}"


def pct(L):
    return f"{100 * L:.1f}%"


FEED_TOTAL, STORY_TOTAL = 8, 4


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 548, "two codes from the patch", 20, MUTED, "start", 600)
    for k, c in enumerate((40, 200)):
        x = 110 + k * 230
        v += sw(x, 570, 190, 130, grey(c))
        v += mono(x + 95, 645, str(c), 34, on(c), "middle", 600)
        v += mono(x, 736, f"sends {pct(d.LIN[c])} of white", 18, MUTED)
    v += mono(600, 548, "averaged", 20, MUTED, "start", 600)
    v += txt(560, 650, "→", 44, MUTED, SANS, 500, "middle")
    v += sw(610, 570, 170, 130, grey(d.MID_CODES), ACCENT, 4)
    v += mono(695, 645, "120", 34, on(120), "middle", 600)
    v += sw(800, 570, 170, 130, grey(d.enc8(d.MID_LIGHT)), LINK, 4)
    v += mono(885, 645, fmt1(d.enc8(d.MID_LIGHT)), 34, on(149), "middle", 600)
    v += mono(610, 736, "as codes", 19, ACCENT, "start", 600)
    v += mono(800, 736, "as light", 19, LINK, "start", 600)
    v += hline(110, 970, 790)
    v += mono(110, 846, f"code 120 sends {pct(d.dec8(120))} of white's light;", 21, INK, "start", 600)
    v += mono(110, 882, f"the average of the two lights is {pct(d.MID_LIGHT)}, code {fmt1(d.enc8(d.MID_LIGHT))}.", 21, INK, "start", 600)
    v += mono(110, 950, "one-pixel black and white stripes, halved:", 19, MUTED)
    v += mono(110, 984, f"codes give 127.5 ({pct(d.STRIPE_CODES_LIGHT)} of white); light gives 187.5 (50%)", 19, MUTED)
    v += mono(110, 1060, "average = a blur, a resize, a composite", 19, SOFT)
    emit("feed", 1, "averaging-codes-darkens",
         ["Averaging codes", "darkens the image."],
         ["Code 40 and code 200, averaged two ways:", "as numbers, and as the light they send."],
         v,
         ["An 8-bit value is a code on the sRGB curve,", "not an amount of light. Decode first."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += sw(110, 560, 200, 200, rgb(d.AZURE))
    v += mono(110, 800, "the azure", 21, INK, "start", 600)
    v += mono(110, 832, "(40, 200, 255)", 19, MUTED)
    v += sw(400, 580, 160, 160, grey(d.AZ_LUMA), ACCENT, 5)
    v += mono(480, 676, "158", 38, on(158), "middle", 600)
    v += sw(700, 580, 160, 160, grey(d.AZ_LUMGREY), LINK, 5)
    v += mono(780, 676, "186", 38, on(186), "middle", 600)
    v += mono(400, 800, "luma: BGR2GRAY", 20, ACCENT, "start", 600)
    v += mono(400, 832, "weights on codes", 18, MUTED)
    v += mono(700, 800, "luminance grey", 20, LINK, "start", 600)
    v += mono(700, 832, "weights on light", 18, MUTED)
    v += hline(110, 970, 880)
    v += mono(110, 934, "0.299·40 + 0.587·200 + 0.114·255 = 158.4", 20, ACCENT, "start", 600)
    v += mono(110, 972, f"decode → Y = {d.AZ_Y:.4f} → encode → {fmt1(d.AZ_LUMGREY)}", 20, LINK, "start", 600)
    v += mono(110, 1046, f"L*: azure {fmt1(d.AZ_LAB[0])} · luma grey {fmt1(d.lstar(d.AZ_LUMA_Y))} · "
                         f"luminance grey {fmt1(d.lstar(d.AZ_Y))}", 19, MUTED)
    emit("feed", 2, "bgr2gray-is-luma",
         ["BGR2GRAY returns luma,", "not luminance."],
         ["One pixel, two greys: weights on the codes,", "or weights on the light they encode."],
         v,
         ["The luma grey is 10.2 units of L* darker", "than the colour it came from."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    x0, y0, sc = 120, 1060, 560          # an xy plot, x 0..0.75, y 0..0.85
    X = lambda x: x0 + x * sc
    Y = lambda y: y0 - y * sc
    pts = " ".join(f"{X(x):.1f},{Y(y):.1f}" for _, x, y in d.LOCUS)
    v += f'<polygon points="{pts}" fill="rgba(45,49,66,0.04)" stroke="{INK}" stroke-width="2"/>'
    for P, col in ((d.P_NTSC, ACCENT), (d.P709, LINK)):
        tri = " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in P)
        v += f'<polygon points="{tri}" fill="none" stroke="{col}" stroke-width="3.5" stroke-linejoin="round"/>'
    v += f'<circle cx="{X(d.WP_D65[0]):.1f}" cy="{Y(d.WP_D65[1]):.1f}" r="6" fill="{LINK}"/>'
    v += f'<circle cx="{X(d.WP_C_CIE[0]):.1f}" cy="{Y(d.WP_C_CIE[1]):.1f}" r="6" fill="{ACCENT}"/>'
    rx = 590
    v += mono(rx, 580, "NTSC 1953, white C", 21, ACCENT, "start", 600)
    v += mono(rx, 616, " · ".join(f"{x:.3f}" for x in d.ROW_NTSC), 22, INK, "start", 600)
    v += mono(rx, 648, "= BT.601's luma weights", 18, MUTED)
    v += mono(rx, 730, "BT.709 and sRGB, D65", 21, LINK, "start", 600)
    v += mono(rx, 766, " · ".join(f"{x:.4f}" for x in d.ROW_709), 22, INK, "start", 600)
    v += mono(rx, 798, "= sRGB's luminance weights", 18, MUTED)
    v += mono(rx, 880, "BT.601's own primaries", 21, MUTED, "start", 600)
    v += mono(rx, 916, " · ".join(f"{x:.3f}" for x in d.ROW_625), 22, INK, "start", 600)
    v += mono(rx, 948, "625-line, with D65", 18, MUTED)
    v += mono(rx, 1040, "CIE 1931 xy; horseshoe from", 16, SOFT)
    v += mono(rx, 1064, "the CIE's table (CC BY-SA 4.0)", 16, SOFT)
    emit("feed", 3, "where-0-299-comes-from",
         ["Where 0.299, 0.587", "and 0.114 come from."],
         ["Luminance weights are fixed by a display's", "primaries and its white point."],
         v,
         ["BT.601 still codes with the 1953 NTSC", "weights, not those of its own primaries."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    base, top, x0 = 990, 600, 152
    k = (base - top) / 65
    v += mono(110, 556, "codes per tenth of lightness L*", 20, INK, "start", 600)
    for i in range(10):
        xc = x0 + i * 84
        for val, col, dx in ((d.BANDS_SRGB[i], ACCENT, -19), (d.BANDS_LIN[i], LINK, 19)):
            h = val * k
            v += rect(xc + dx - 17, base - h, 34, h, col)
            if h > 34:
                v += mono(xc + dx, base - h + 26, str(val), 18, WHITE, "middle", 600)
            else:
                v += mono(xc + dx, base - h - 10, str(val), 18, col, "middle", 600)
        v += mono(xc, base + 30, f"{10 * i}–{10 * i + 10}", 14, SOFT, "middle")
    v += hline(110, 970, base, MUTED, 1.5)
    v += mono(110, 1074, "sRGB", 19, ACCENT, "start", 600)
    v += mono(185, 1074, "21 to 29 per tenth", 19, MUTED)
    v += mono(520, 1074, "linear 8-bit", 19, LINK, "start", 600)
    v += mono(680, 1074, "3 to 61", 19, MUTED)
    emit("feed", 4, "why-8-bits-need-a-curve",
         ["Why 8 bits need", "a curve."],
         ["256 codes spread over lightness: along the", "sRGB curve, or evenly in light."],
         v,
         ["Linear 8-bit coding spends 3 codes on the", "darkest tenth and 61 on the brightest."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    rows = [("row r0 of the patch", d.STEP_ROW, INK), ("blurred as codes", d.BLUR_CODES, ACCENT),
            ("blurred as light", d.BLUR_LIGHT_AS_CODES, LINK)]
    cs, y = 150, 560
    for name, vals, col in rows:
        v += mono(110, y, name, 21, col, "start", 600)
        for j, val in enumerate(vals):
            v += rect(165 + j * cs, y + 18, cs, 110, grey(val), "rgba(45,49,66,0.30)", 1)
            v += mono(165 + j * cs + cs / 2, y + 84, fmt1(val), 24, on(val), "middle", 600)
        v += rect(165, y + 18, 5 * cs, 110, "none", "rgba(45,49,66,0.6)", 2)
        y += 172
    v += mono(110, 1092, "weights 0.239 · 0.522 · 0.239: the series' Gaussian", 18, SOFT)
    emit("feed", 5, "the-same-blur-two-answers",
         ["The same blur,", "two answers."],
         ["Row r0 of the patch blurred with the series'", "Gaussian: on codes, and on decoded light."],
         v,
         ["On codes the edge comes out darker:", "78.2 against 109.4 on the dark side."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cw, x0 = 95, 98
    for k, (name, t) in enumerate(d.SWATCHES):
        cx = x0 + k * cw + cw / 2
        luma, lg = d.GREYS[name]
        v += sw(cx - 38, 540, 76, 70, rgb(t))
        v += mono(cx, 640, name, 16, INK, "middle", 600)
        v += sw(cx - 38, 660, 36, 60, grey(luma), ACCENT, 3)
        v += sw(cx + 2, 660, 36, 60, grey(lg), LINK, 3)
        v += mono(cx - 20, 752, str(round(luma)), 17, ACCENT, "middle", 600)
        v += mono(cx + 20, 752, str(round(lg)), 17, LINK, "middle", 600)
    v += hline(110, 970, 800)
    v += sw(110, 834, 22, 30, grey(150), ACCENT, 3) + mono(146, 856, "luma (BGR2GRAY)", 20, ACCENT, "start", 600)
    v += sw(420, 834, 22, 30, grey(150), LINK, 3) + mono(456, 856, "luminance grey", 20, LINK, "start", 600)
    lo, hi = d.SWEEP["luma601_minus_lumgrey_min"], d.SWEEP["luma601_minus_lumgrey_max"]
    v += mono(110, 930, f"over all {d.SWEEP['colours']:,} 8-bit colours:", 20, INK, "start", 600)
    v += mono(110, 968, f"luma − luminance grey runs from {fmt1(lo[0])}", 20, INK)
    v += mono(110, 1004, f"(pure green) to +{hi[0]:.1f} (255, 172, 255)", 20, INK)
    v += mono(110, 1068, "exactly 0 on every grey", 19, MUTED)
    emit("feed", 6, "luma-is-off-by-70",
         ["Luma is off by up", "to 70 grey levels."],
         ["BGR2GRAY against the grey of equal", "luminance, for every 8-bit colour."],
         v,
         ["Equal on greys, darker on saturated", "colours, a little brighter on pale pinks."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    rows = [("OpenCV", "COLOR_BGR2GRAY", "158", "luma of the codes", ACCENT),
            ("OpenCV", "COLOR_BGR2XYZ, Y", "170", "the matrix on codes, no decode", ACCENT),
            ("OpenCV", "COLOR_BGR2Lab, L*", fmt1(d.AZ_LAB[0]), "decodes first, undocumented", LINK),
            ("scikit-image", "rgb2gray", f"{d.AZ_SK_GRAY:.4f}", "documented as luminance", ACCENT),
            ("scikit-image", "rgb2xyz, Y", f"{d.AZ_SK_Y:.4f}", "decodes first: luminance", LINK)]
    y = 566
    for lib, call, val, note, col in rows:
        v += mono(110, y, lib, 17, SOFT)
        v += mono(110, y + 32, call, 22, INK, "start", 600)
        v += mono(620, y + 32, val, 30, col, "end", 600)
        v += mono(650, y + 32, note, 18, col if col == ACCENT else LINK)
        y += 106
    emit("feed", 7, "five-calls-two-decode",
         ["Five calls on one pixel.", "Two decode it."],
         ["The azure (40, 200, 255) through OpenCV and", "scikit-image, read from source, not run."],
         v,
         ["Only the calls that decode sRGB first", "work on light: Lab, and rgb2xyz."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("codes", "code 128 sends 21.6% of white's light", "decode before you blur, resize or blend"),
             ("luma", "BGR2GRAY: 158; luminance grey: 186", "weights on codes, or on light"),
             ("weights", "0.299 · 0.587 · 0.114 date from 1953", "sRGB's own: 0.2126 · 0.7152 · 0.0722"),
             ("Lab", f"D65 or D50: {d.DE_65_50:.1f} ΔE apart", "a Lab number needs its white")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "luma" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Colour and gamma,", "by hand."],
         ["Luma, luminance and the spaces in between,", "on one pixel and one 5×5 patch."],
         v,
         ["The full walk-through, every number worked", "by hand, and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    x0, x1 = 110, 970
    W = x1 - x0
    v = mono(x0, 806, "sRGB code", 24, INK, "start", 600)
    n = 64
    for k in range(n):
        v += rect(x0 + k * W / n, 820, W / n + 0.5, 70, grey((k + 0.5) / n * 255))
    v += rect(x0, 820, W, 70, "none", "rgba(45,49,66,0.6)", 2)
    v += mono(x1, 1180, "light it sends", 24, INK, "end", 600)
    v += line(x0, 1210, x1, 1210, INK, 3)
    for c, L, col in ((128, d.LIN[128], ACCENT), (187.5, 0.5, LINK)):
        xc, xl = x0 + c / 255 * W, x0 + L * W
        v += line(xc, 890, xl, 1210, col, 4)
        v += f'<circle cx="{xl:.1f}" cy="1210" r="9" fill="{col}"/>'
        v += mono(xc, 806, fmt1(c), 30, col, "middle", 600)
        v += mono(xl, 1262, "21.6%" if c == 128 else "50%", 30, col, "middle", 600)
    v += mono(x0, 1340, "0", 22, SOFT)
    v += mono(x1, 1340, "100%", 22, SOFT, "end")
    emit("story", 1, "code-128-is-not-half",
         ["Code 128 is not", "half of white."],
         ["It sends 21.6% of white's light."],
         v,
         ["Half of the light", "needs code 187.5."],
         STORY_TOTAL)


def story_02():
    v = sw(110, 800, 400, 300, rgb(d.AZURE))
    v += mono(110, 1150, "the azure (40, 200, 255)", 28, INK, "start", 600)
    v += sw(570, 800, 190, 190, grey(d.AZ_LUMA), ACCENT, 6)
    v += mono(665, 910, "158", 44, on(158), "middle", 600)
    v += sw(780, 800, 190, 190, grey(d.AZ_LUMGREY), LINK, 6)
    v += mono(875, 910, "186", 44, on(186), "middle", 600)
    v += mono(570, 1040, "luma", 28, ACCENT, "start", 600)
    v += mono(780, 1040, "luminance", 28, LINK, "start", 600)
    v += mono(110, 1260, "BGR2GRAY weighs the codes;", 28, MUTED)
    v += mono(110, 1302, "luminance weighs the light.", 28, MUTED)
    emit("story", 2, "158-or-186",
         ["158 or 186?"],
         ["One azure pixel,", "two ways to make it grey."],
         v,
         ["BGR2GRAY gives luma, 158.", "The grey of equal light is 186."],
         STORY_TOTAL)


def story_03():
    v = sw(110, 800, 190, 190, grey(40))
    v += mono(205, 910, "40", 44, on(40), "middle", 600)
    v += sw(330, 800, 190, 190, grey(200))
    v += mono(425, 910, "200", 44, on(200), "middle", 600)
    v += sw(110, 1060, 400, 190, grey(120), ACCENT, 6)
    v += mono(310, 1172, "120", 52, on(120), "middle", 600)
    v += sw(570, 1060, 400, 190, grey(d.enc8(d.MID_LIGHT)), LINK, 6)
    v += mono(770, 1172, fmt1(d.enc8(d.MID_LIGHT)), 52, on(149), "middle", 600)
    v += mono(110, 1300, "average of the codes", 26, ACCENT, "start", 600)
    v += mono(570, 1300, "average of the light", 26, LINK, "start", 600)
    v += mono(110, 1040, "averaged:", 26, MUTED)
    emit("story", 3, "averaging-codes-darkens",
         ["Averaging codes", "darkens."],
         ["Code 40 and code 200,", "averaged two ways."],
         v,
         ["Decode, average, encode:", "148.7, not 120."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["a pixel value is a code, not light",
             "decode, average, then encode",
             "BGR2GRAY is luma, not luminance",
             "Lab needs its white"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 2 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Colour and", "gamma."],
         ["Worked on one pixel", "and one 5×5 patch."],
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
