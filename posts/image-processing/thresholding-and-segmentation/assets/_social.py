#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Thresholding and Segmentation".

Image Processing by Hand, part 11. The shell (lockup, rule, serif title, deck, takeaway, footer) is
copied from part 9's _social.py, with the lockup reading "canery.in" as in part 10. Every number on a
card comes from `_data.py` — the patch and OpenCV's 8-bit blur of it, Otsu's criterion, the three
threshold rules, the closed-form mixtures, the two-light tiling and the watershed replays — so a card
cannot disagree with the article. Pixel cells follow the article: high value = bright; regions use the
figures' colours.

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
CANONICAL = "canery.in/blogs/thresholding-and-segmentation"
FOOTER = "THRESHOLDING AND SEGMENTATION · CANERY.IN"

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
r = d.r
assert d.LIB["raw"]["otsu"] == 40 and d.LIB["smooth"] == dict(otsu=105, sk_otsu=105, isodata=[125], tri=160, sk_tri=161)
assert (d.SM_BEST["lo"], d.SM_BEST["hi"], r(d.SM_BEST["sb"], 1), r(d.SM_VAR, 2)) == (105, 162, 2935.8, 3370.47)
assert (d.SHAPES["sizes"]["otsu"], d.SHAPES["sizes"]["best"], r(100 * d.SHAPES["sizes"]["err_otsu"], 0)) == (72, 130, 43.0)
assert r(100 * d.FLIP, 1) == 2.0 and r(d.ETA_5PC[1], 2) == 0.68 and r(d.SHAPES["overlap"]["eta"], 2) == 0.68
assert r(100 * d.SHAPES["overlap"]["err_best"], 1) == 15.9
assert d.OTSU_T2 == 51 and d.errors(d.GLOBAL_T2) == 10 and d.LOCAL_ERR[("sauvola", 7)] == 0
assert d.WS_NONE[2] == [3, 3, 3, 2, 2] and d.WS_HAND[0] == [1, 1, 1, 2, 2]
assert d.OCV_B[3] == [-1, 2, 2, 2, -1]
FIVE = d.mixture([(0.95, 70, 15), (0.05, 170, 15)])


def fv(v, nd=1):
    return f"{v:,.{nd}f}" if abs(v - round(v)) > 1e-9 else f"{round(v):,}"


def xmark(x, y, h, colour, sw=4):
    return line(x - h, y - h, x + h, y + h, colour, sw) + line(x - h, y + h, x + h, y - h, colour, sw)


def bars(x, y, w, h, hist, xr, shade=None, marks=(), bar_w=5, label_size=18, cmax=None):
    """A histogram as bars on [xr], with an optional shaded run and labelled vertical marks."""
    lo, hi = xr
    X = lambda v: x + (v - lo) / (hi - lo) * w
    cmax = cmax or max(hist.values())
    Y = lambda c: y + h - c / cmax * (h - 8)
    s = ""
    if shade:
        s += rect(X(shade[0]), y, X(shade[1]) - X(shade[0]), h, ACCENT, op=0.10)
    for v, c in hist.items():
        s += rect(X(v) - bar_w / 2, Y(c), bar_w, y + h - Y(c), INK)
    s += hline(x, x + w, y + h, MUTED, 1.5)
    for k, (t, lab) in enumerate(marks):
        s += line(X(t), y - 6, X(t), y + h, ACCENT, 3)
        s += mono(X(t), y - 16 - 26 * k, lab, label_size, ACCENT, "middle", 600)
    return s


def curve_panel(x, y, w, h, hist, ch, cut, best, cut_label, best_label, obj=None):
    """A closed-form histogram over 0..255 with its Otsu criterion below and two cut lines."""
    X = lambda v: x + v / 255 * w
    hmax = max(hist)
    pts = [(X(v), y + h - hist[v] / hmax * (h - 6)) for v in range(256)]
    poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in [(x, y + h)] + pts + [(x + w, y + h)])
    s = f'<polygon points="{poly}" fill="{INK}" fill-opacity="0.75"/>'
    s += hline(x, x + w, y + h, MUTED, 1.5)
    cur, _ = d.otsu_curve(hist)
    cmax = max(cur)
    yc = y + h + 30
    cpts = " ".join(f"{X(t):.1f},{yc + ch - c / cmax * (ch - 6):.1f}" for t, c in enumerate(cur))
    s += f'<polyline points="{cpts}" fill="none" stroke="{MUTED}" stroke-width="3"/>'
    s += hline(x, x + w, yc + ch, MUTED, 1.5)
    s += mono(x - 12, yc + 22, "σB²", 18, SOFT, "end")
    s += line(X(best + 0.5), y - 10, X(best + 0.5), yc + ch, LINK, 3, "8,6")
    s += line(X(cut + 0.5), y - 10, X(cut + 0.5), yc + ch, ACCENT, 4)
    s += mono(X(cut + 0.5), y - 22, cut_label, 20, ACCENT, "middle", 600)
    s += mono(X(best + 0.5), y - 22, best_label, 20, LINK, "middle", 600)
    for v in (0, 100, 200):
        s += mono(X(v), yc + ch + 30, str(v), 16, SOFT, "middle")
    if obj is not None:
        s += f'<circle cx="{X(obj):.1f}" cy="{y + h:.1f}" r="7" fill="{INK}"/>'
        s += mono(X(obj) + 14, y + h - 18, "the object, too small to see", 17, SOFT, "start")
    return s


def grid5(x, y, cs, L, size=26, outline=(), values=None, dash=()):
    s = ""
    for i in range(5):
        for j in range(5):
            lab = L[i][j]
            fill = REG[lab] if lab > 0 else "#ffffff"
            s += rect(x + j * cs, y + i * cs, cs, cs, fill, "rgba(45,49,66,0.35)", 1.2)
            if lab < 0:
                s += rect(x + j * cs, y + i * cs, cs, cs, "url(#hatch)")
                s += rect(x + j * cs + cs / 2 - size * 0.95, y + i * cs + cs / 2 - size * 0.80, size * 1.9, size * 1.48, PAPER)
            t = values[i][j] if values is not None else ("−1" if lab < 0 else str(lab))
            s += mono(x + j * cs + cs / 2, y + i * cs + cs / 2 + size * 0.36, t, size, INK if lab >= 0 else MUTED,
                      "middle", 600)
    s += rect(x, y, 5 * cs, 5 * cs, "none", "rgba(45,49,66,0.6)", 2)
    for (i, j), colour in outline:
        s += rect(x + j * cs + 3, y + i * cs + 3, cs - 6, cs - 6, "none", colour, 5)
    for (i, j) in dash:
        s += rect(x + j * cs + 9, y + i * cs + 9, cs - 18, cs - 18, "none", INK, 3, dash="7,5")
    return s


HATCH = ('<defs><pattern id="hatch" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
         '<line x1="2" y1="0" x2="2" y2="14" stroke="rgba(45,49,66,0.30)" stroke-width="2.4"/></pattern></defs>')


def mask_grid(x, y, cs, img, mk, size=22):
    s = ""
    for i in range(5):
        for j in range(5):
            bright = mk[i][j] == 1
            s += rect(x + j * cs, y + i * cs, cs, cs, "#ffffff" if bright else blend((45, 49, 66), 0.82, (245, 245, 245)),
                      "rgba(45,49,66,0.35)", 1.2)
            s += mono(x + j * cs + cs / 2, y + i * cs + cs / 2 + size * 0.36, str(img[i][j]), size,
                      INK if bright else "#ffffff", "middle", 600)
    s += rect(x, y, 5 * cs, 5 * cs, "none", "rgba(45,49,66,0.6)", 2)
    return s


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    raw, sm = d.RAW_BEST, d.SM_BEST
    v += mono(110, 548, "the patch: 40, 200 and 255", 22, INK, "start", 600)
    v += bars(110, 580, 860, 170, d.HR, (0, 258), shade=(raw["lo"] + 0.5, raw["hi"] - 0.5), bar_w=7)
    v += mono(110, 790, f"any t from {raw['lo']} to {raw['hi'] - 1} splits it the same way · returns {d.LIB['raw']['otsu']}",
              19, MUTED)
    v += mono(110, 862, "smoothed, 8-bit: ten levels", 22, INK, "start", 600)
    v += bars(110, 894, 860, 170, d.HS, (0, 258), shade=(sm["lo"] + 0.5, sm["hi"] - 0.5), bar_w=7)
    v += mono(110, 1104, f"any t from {sm['lo']} to {sm['hi'] - 1} · σB² {fv(sm['sb'])} · returns {d.LIB['smooth']['otsu']}",
              19, MUTED)
    emit("feed", 1, "otsu-always-returns-a-number",
         ["Otsu always", "returns a number."],
         ["Whether any number can work is written", "in the histogram, before you call it."],
         v,
         ["A threshold works only when the two classes", "do not share grey levels."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    rows = d.SM
    best = d.SM_BEST
    smax = max(rr["sb"] for rr in rows)
    y = 546
    for row in rows:
        hot = row is best
        v += mono(110, y + 22, f"{row['lo']} | {row['hi']}", 21, ACCENT if hot else INK, "start", 600 if hot else 400)
        wbar = 560 * row["sb"] / smax
        v += rect(300, y, wbar, 30, ACCENT if hot else blend((45, 49, 66), 0.45, (255, 255, 255)))
        v += mono(300 + wbar + 14, y + 22, fv(row["sb"]), 21, ACCENT if hot else MUTED, "start", 600 if hot else 400)
        y += 58
    v += mono(110, y + 26, f"σB² + σW² = {fv(d.SM_VAR, 2)} on every row", 21, INK, "start", 600)
    emit("feed", 2, "nine-cuts-one-winner",
         ["Nine cuts,", "one winner."],
         ["The smoothed 5×5 patch has ten grey levels,", "so nine places to cut. σB² for each:"],
         v,
         ["The cut that pushes the class means apart", "is the cut that makes each class tightest."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    lib = d.LIB["smooth"]
    marks = [(lib["otsu"] + 0.5, f"Otsu {lib['otsu']}"), (lib["isodata"][0] + 0.5, f"isodata {lib['isodata'][0]}"),
             (lib["tri"] + 0.5, f"triangle {lib['tri']}")]
    v += bars(110, 640, 520, 300, d.HS, (30, 210), shade=(d.SM_BEST["lo"] + 0.5, d.SM_BEST["hi"] - 0.5),
              marks=marks, bar_w=6, label_size=18)
    for t in (40, 80, 120, 160, 200):
        v += mono(110 + (t - 30) / 180 * 520, 972, str(t), 16, SOFT, "middle")
    v += mono(700, 600, "the mask, all three", 20, INK, "start", 600)
    v += mask_grid(700, 630, 56, d.G3, d.MASK_SM, 18)
    v += mono(700, 950, "the impulse, 99: dark", 19, MUTED)
    v += mono(110, 1050, "every threshold from 105 to 161 draws this mask", 21, INK, "start", 600)
    emit("feed", 3, "three-numbers-one-mask",
         ["105, 125, 160."],
         ["Otsu, isodata and the triangle method on the", "same smoothed patch print three numbers."],
         v,
         ["One mask. The split is the result;", "the number is only where it landed."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    sh = d.SHAPES["sizes"]
    v += curve_panel(150, 600, 780, 250, sh["h"], 120, sh["otsu"], sh["best"], f"Otsu {sh['otsu']}", f"best {sh['best']}",
                     obj=170)
    v += mono(150, 1100, f"Otsu: {100 * sh['err_otsu']:.0f}% wrong · best cut: {100 * sh['err_best']:.2f}% wrong", 21,
              INK, "start", 600)
    emit("feed", 4, "a-small-object",
         ["A 1% object,", "43% wrong."],
         ["Otsu's criterion has two peaks, and the", "higher one sits inside the background."],
         v,
         [f"Below about a {100 * d.FLIP:.0f}% object, Otsu cuts", "through the background."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    panels = [(FIVE, "a 5% object, cut cleanly", f"η = {d.ETA_5PC[1]:.2f}",
               f"{100 * d.cut_error([(0.95, 70, 15), (0.05, 170, 15)], d.ETA_5PC[0]):.2f}% wrong"),
              (d.SHAPES["overlap"]["h"], "two humps that overlap", f"η = {d.SHAPES['overlap']['eta']:.2f}",
               f"{100 * d.SHAPES['overlap']['err_best']:.1f}% wrong at best")]
    for k, (hist, ttl, eta, err) in enumerate(panels):
        x0 = 110 + k * 460
        v += mono(x0, 560, ttl, 21, INK, "start", 600)
        hmax = max(hist)
        X = lambda vv, x0=x0: x0 + vv / 255 * 400
        pts = [(X(vv), 840 - hist[vv] / hmax * 230) for vv in range(256)]
        poly = " ".join(f"{a:.1f},{b:.1f}" for a, b in [(x0, 840)] + pts + [(x0 + 400, 840)])
        v += f'<polygon points="{poly}" fill="{INK}" fill-opacity="0.75"/>'
        v += hline(x0, x0 + 400, 840, MUTED, 1.5)
        v += mono(x0, 920, eta, 40, ACCENT, "start", 600)
        v += mono(x0, 966, err, 21, MUTED)
    v += mono(110, 1070, "same score, opposite verdicts", 22, INK, "start", 600)
    emit("feed", 5, "eta-twice",
         ["η = 0.68, twice."],
         ["Otsu's separability score for a clean small", "object and for two hopelessly mixed humps."],
         v,
         ["η measures the variance a split explains,", "not whether a clean cut exists."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    row, truth = d.T2[0], d.TRUTH[0]
    mk5, T5 = d.LOCAL[("sauvola", 7)]
    x0, w, y0, h = 130, 820, 600, 330
    slot = w / 10
    Y = lambda val: y0 + h - val / 230 * h
    for j, val in enumerate(row):
        xc = x0 + (j + 0.5) * slot
        v += rect(xc - slot * 0.32, Y(val), slot * 0.64, y0 + h - Y(val),
                  blend((45, 49, 66), 0.30 if truth[j] else 0.78, (255, 255, 255)))
        v += line(xc - slot * 0.42, Y(T5[0][j]), xc + slot * 0.42, Y(T5[0][j]), ACCENT, 5)
        v += mono(xc, y0 + h + 30, "bright" if truth[j] else "dark", 15, SOFT, "middle")
        if d.GLOBAL_T2[0][j] != truth[j]:
            v += xmark(xc, y0 + h + 56, 9, LINK)
    v += line(x0, Y(d.OTSU_T2), x0 + w, Y(d.OTSU_T2), LINK, 3, "10,7")
    v += line(x0 + 5 * slot, y0 - 10, x0 + 5 * slot, y0 + h, RULE_SOLID, 2, "4,5")
    v += mono(x0 + 2.5 * slot, y0 - 20, "lit", 20, SOFT, "middle")
    v += mono(x0 + 7.5 * slot, y0 - 20, "a fifth of the light", 20, SOFT, "middle")
    v += mono(110, 1090, f"global Otsu, {d.OTSU_T2} (blue): {d.errors(d.GLOBAL_T2)} wrong · Sauvola, window 7 (orange): "
              f"{d.LOCAL_ERR[('sauvola', 7)]} wrong", 19, INK, "start", 600)
    emit("feed", 6, "one-value-two-meanings",
         ["40 is dark here", "and bright there."],
         ["The patch beside itself at a fifth of the light,", "one row of it."],
         v,
         ["Threshold locally: a window wider than the", "objects and narrower than the shading."],
         FEED_TOTAL)


def feed_07():
    v = HATCH + box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(130, 560, "no markers", 22, INK, "start", 600)
    v += grid5(130, 590, 72, d.WS_NONE, 26)
    v += mono(130, 1000, "4 regions", 26, ACCENT, "start", 600)
    v += mono(590, 560, "two markers, drawn by hand", 22, INK, "start", 600)
    v += grid5(590, 590, 72, d.WS_HAND, 26, outline=[((0, 0), LINK), ((2, 4), ACCENT)])
    v += mono(590, 1000, "2 regions", 26, INK, "start", 600)
    v += mono(130, 1070, "the impulse's ring cuts the dark side's flat zeros in three", 19, MUTED)
    emit("feed", 7, "one-hot-pixel-four-regions",
         ["One hot pixel,", "four regions."],
         ["Watershed on the patch's gradient floods", "every regional minimum unless you say otherwise."],
         v,
         ["Markers decide which minima", "are the same object."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("Otsu", "2-means on the histogram", "best only for two humps of like size and spread"),
             ("η", "variance explained", f"not separability: {d.ETA_5PC[1]:.2f} twice"),
             ("local", "a threshold per window", "wider than objects, narrower than shading"),
             ("watershed", "a flood from markers", "every unmarked minimum becomes a region")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "watershed" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Thresholding and", "segmentation, by hand."],
         ["Otsu, Sauvola and watershed", "on one 5×5 patch."],
         v,
         ["The full walk-through, every number worked", "by hand, and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    raw = d.RAW_BEST
    v = mono(150, 800, "the patch's histogram: 40, 200, 255", 24, SOFT, "start", 600)
    v += bars(150, 900, 780, 300, d.HR, (0, 258), shade=(raw["lo"] + 0.5, raw["hi"] - 0.5),
              marks=[(d.LIB["raw"]["otsu"] + 0.5, f"returns {d.LIB['raw']['otsu']}")], bar_w=10, label_size=26)
    v += txt(150, 1290, "any t from 40 to 199 splits it the same way", 30, MUTED)
    v += txt(150, 1340, "and Otsu returns the first of them", 30, MUTED)
    emit("story", 1, "otsu-returned-40",
         ["Otsu returned 40."],
         ["The top of the dark spike,", "not the middle of the gap."],
         v,
         ["Reuse that number on a noisy frame", "and a dark pixel at 42 turns bright."],
         STORY_TOTAL)


def story_02():
    sh = d.SHAPES["sizes"]
    v = mono(150, 800, "a histogram with a 1% object at 170", 24, SOFT, "start", 600)
    v += curve_panel(150, 900, 780, 260, sh["h"], 130, sh["otsu"], sh["best"], f"Otsu {sh['otsu']}", f"best {sh['best']}",
                     obj=170)
    emit("story", 2, "a-small-object",
         ["43% wrong."],
         ["Otsu's cut on a small object", "lands inside the background."],
         v,
         [f"The best cut, {sh['best']}, gets", f"{100 * sh['err_best']:.2f}% wrong."],
         STORY_TOTAL)


def story_03():
    v = HATCH + mono(150, 790, "cv2.watershed, markers (r1, c1) and (r2, c3)", 22, SOFT, "start", 600)
    v += grid5(240, 830, 120, d.OCV_B, 34, outline=[((1, 1), LINK), ((2, 3), ACCENT)], dash=[(3, 1), (3, 2)])
    emit("story", 3, "the-label-crossed-the-step",
         ["Label 2 crossed", "the step."],
         ["OpenCV floods neighbour differences:", "the step costs 160, the impulse 215."],
         v,
         ["Two dark pixels come back", "with the bright label."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["the histogram decides first",
             "Otsu: two humps of like size",
             "uneven light: threshold locally",
             "touching objects: watershed"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 3 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Thresholding and", "segmentation."],
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
