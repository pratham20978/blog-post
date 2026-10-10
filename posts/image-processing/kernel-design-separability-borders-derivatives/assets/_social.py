#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Kernel Design".

Image Processing by Hand, part 4. The shell (lockup, rule, serif title, deck, takeaway,
footer) is copied from part 3's _social.py, with the lockup reading "canery.in". Every
number on a card is recomputed here from the same functions `_figs.py` uses — the
derivative family on the shared patch, closed-form angular errors, truncated sigma = 2
Gaussians, OpenCV's sigma <= 0 table and the border extensions of row r2 — so a card
cannot disagree with the article. Pixel cells follow the article: high value = bright.

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
import _figs as F  # noqa: E402  — the article's kernels and conventions

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
CANONICAL = "canery.in/blogs/kernel-design-separability-borders-derivatives"
FOOTER = "KERNEL DESIGN · CANERY.IN"

# ------------------------------------------------------------------ the numbers
PATCH, ROW = F.PATCH, F.ROW
W4 = 2 * math.pi / 4
P = {"central difference": 0.0, "[1 4 1]/6": 1 / 6, "Scharr": 3 / 16, "Sobel": 0.25, "Prewitt": 1 / 3}
DIR4 = {k: abs(F.worst(F.pair_of_family(p), W4)) for k, p in P.items()}
DIR4["Farid–Simoncelli 5"] = abs(F.worst(F.FS5, W4))
IMP = {k: F.gx_family(PATCH, 2, 2, p)[0] for k, p in P.items()}
TRUNC = {t: F.trunc_stats(t) for t in (3, 5, 7, 13)}
BORDER = {m: F.gx_family(PATCH, 2, 0, 0.25, lambda im, r, c, m=m: F.ext(im[r], c, m))[0]
          for m in ("constant", "replicate", "reflect", "reflect-101", "wrap")}
assert round(DIR4["Sobel"], 2) == 3.24 and round(DIR4["Scharr"], 2) == 0.29
assert round(IMP["Sobel"], 2) == 26.25 and round(IMP["Scharr"], 2) == 12.81
assert round(math.sqrt(TRUNC[3][1]), 2) == 0.80 and BORDER["reflect-101"] == 0
assert BORDER["reflect"] * 8 == 430

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




# ------------------------------------------------------------------ shared visuals
def stencil(x, y, cw, size=24):
    """The generic 3x3 x-derivative; outer rows carry p, in the accent."""
    cells = [["−p", "0", "p"], ["−(1−2p)", "0", "1−2p"], ["−p", "0", "p"]]
    v = ""
    for r in range(3):
        for c in range(3):
            outer = r != 1 and c != 1
            v += (f'<rect x="{x + c * cw}" y="{y + r * cw}" width="{cw}" height="{cw}" '
                  f'fill="{"rgba(235,108,54,0.10)" if outer else "#ffffff"}" '
                  f'stroke="{ACCENT if outer else "rgba(45,49,66,0.35)"}" stroke-width="{2.5 if outer else 1.5}"/>')
            s = cells[r][c]
            v += mono(x + c * cw + cw / 2, y + r * cw + cw / 2 + size * 0.36, s,
                      size if len(s) < 5 else int(size * 0.72), ACCENT if outer else INK, "middle", 600)
    return v


def family_table(x0, x1, y, rows, gap, size, head=True):
    v = ""
    if head:
        v += label(x0, y - gap * 0.75, "filter", SOFT, "start", 14)
        v += label(x0 + 470, y - gap * 0.75, "p", SOFT, "start", 14)
        v += label(x1, y - gap * 0.75, "direction error, 4-px pattern", SOFT, "end", 14)
    for name in rows:
        col = ACCENT if name == "Scharr" else INK
        v += txt(x0, y, name, size, col, SANS, 600)
        pv = {"central difference": "0", "[1 4 1]/6": "1/6", "Scharr": "3/16", "Sobel": "1/4",
              "Prewitt": "1/3"}[name]
        v += mono(x0 + 470, y, pv, size - 2, col)
        v += mono(x1, y, f"{DIR4[name]:.2f}°", size, col, "end", 600)
        y += gap
    return v


def bars(x0, y, rows, w, bh, gap, maxv, fmtv, lab_w=330, size=26, pad=14):
    """rows: (name, value, colour); horizontal bars with the value at the end."""
    v = ""
    for name, val, col in rows:
        v += txt(x0, y + bh * 0.72, name, size, col, SANS, 600)
        bw = max(val / maxv * w, 3)
        v += (f'<rect x="{x0 + lab_w}" y="{y}" width="{bw:.1f}" height="{bh}" rx="3" fill="{col}" '
              f'fill-opacity="{0.9 if col == ACCENT else 0.6}"/>')
        v += mono(x0 + lab_w + bw + pad, y + bh * 0.74, fmtv(val), size, col, "start", 600)
        y += gap
    return v


def trunc_bars(x0, y, big=False):
    rows = [(f"{t} taps", math.sqrt(TRUNC[t][1]), ACCENT if t == 3 else INK) for t in (3, 5, 7, 13)]
    v = label(x0, y - 24, "effective σ after renormalising · target 2.0", SOFT, "start", 15 if not big else 17)
    w, bh, gap = (520, 52, 92) if not big else (560, 62, 112)
    v += bars(x0, y, rows, w, bh, gap, 2.0, lambda s: f"{s:.2f}", lab_w=180, size=28 if not big else 32, pad=30)
    xt = x0 + 180 + w
    v += (f'<line x1="{xt}" y1="{y + 3 * gap - 14}" x2="{xt}" y2="{y + 3 * gap + bh + 8}" '
          f'stroke="{MUTED}" stroke-width="2" stroke-dasharray="8,6"/>')
    v += mono(xt, y + 4 * gap - gap + bh + 40, "σ = 2", 20 if not big else 24, MUTED, "middle", 600)
    kept = "  ·  ".join(f"{t}: {TRUNC[t][0] * 100:.1f}%" for t in (3, 5, 7, 13))
    v += label(x0, y + 4 * gap + (60 if not big else 80), "mass kept before renormalising", SOFT, "start",
               15 if not big else 17)
    v += mono(x0, y + 4 * gap + (96 if not big else 124), kept, 22 if not big else 25, MUTED)
    return v


def gauss_rows(x, y, cw, ch, big=False):
    v = ""
    items = [("documented: sampled at σ = 0.8", [0.239, 0.522, 0.239], "variance 0.478", MUTED),
             ("what runs with sigma 0: fixed table", [0.25, 0.5, 0.25], "variance 0.500", ACCENT)]
    for name, ws, var, col in items:
        v += label(x, y - 18, name, col, "start", 15 if not big else 18)
        for i, w_ in enumerate(ws):
            v += box(x + i * cw, y, cw, ch, "#ffffff" if col != ACCENT else ACCENT_TINT,
                     col if col == ACCENT else "rgba(45,49,66,0.35)", 0, 2 if col == ACCENT else 1.5)
            v += mono(x + i * cw + cw / 2, y + ch / 2 + 12, f"{w_:g}", 32 if big else 30, col, "middle", 600)
        v += mono(x + 3 * cw + 30, y + ch / 2 + 10, var, 24 if big else 22, col, "start", 600)
        y += ch + (96 if big else 80)
    return v, y


def border_rows(x, y, cw, ch, big=False):
    modes = [("reflect-101 · OpenCV default", "reflect-101", ACCENT),
             ("reflect · SciPy default", "reflect", INK),
             ("constant 0", "constant", MUTED),
             ("wrap", "wrap", MUTED)]
    v = label(x, y - 26, "invented", SOFT, "start", 14 if not big else 16)
    v += label(x + 3 * cw + 16, y - 26, "c0  c1  c2 of row r2", SOFT, "start", 14 if not big else 16)
    v += label(x + 6 * cw + 60, y - 26, "Sobel at (r2, c0)", SOFT, "start", 14 if not big else 16)
    for name, m, col in modes:
        v += label(x, y + ch + 24, name, col, "start", 14 if not big else 16)
        for i in range(-3, 3):
            val = F.ext(ROW, i, m)
            xx = x + (i + 3) * cw + (16 if i >= 0 else 0)
            v += pixel(xx, y, cw, ch, val, 24 if not big else 28)
            if i < 0:
                v += (f'<rect x="{xx}" y="{y}" width="{cw}" height="{ch}" fill="none" stroke="{PAPER}" '
                      f'stroke-width="3" stroke-dasharray="6,5"/>')
        g = BORDER[m]
        v += mono(x + 6 * cw + 60, y + ch * 0.66, f"{g:.2f}".replace("-", "−"), 34 if not big else 38, col,
                  "start", 600)
        y += ch + (66 if not big else 84)
    return v


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 8, 4


def feed_01():
    v = box(72, 500, 936, 610, "#ffffff", RULE_SOLID)
    v += stencil(110, 540, 86, 24)
    v += txt(420, 590, "½ × the column p, 1 − 2p, p", 26, INK, SANS, 600)
    v += txt(420, 626, "times the central difference −1, 0, 1", 22, MUTED)
    v += txt(420, 690, "one free number: p", 28, ACCENT, SANS, 600)
    v += txt(420, 730, "the weight on each neighbouring row", 20, MUTED)
    v += hline(110, 970, 846)
    v += family_table(110, 970, 906, ["central difference", "Scharr", "Sobel", "Prewitt"], 52, 24)
    emit("feed", 1, "sobel-and-scharr-are-one-stencil",
         ["Sobel and Scharr are", "one stencil."],
         ["Every 3×3 x-derivative that treats up and down alike is the same",
          "product. Only the weight on the neighbouring rows differs."],
         v,
         ["Choosing a derivative filter is choosing one number.",
          "Scharr's p = 3/16 keeps direction within 0.3°; Sobel's 1/4 does not."],
         FEED_TOTAL)


def feed_02():
    rows = [("cv2.Sobel(img, CV_32F, 1, 0, ksize=3)", "640", "× 8", INK),
            ("cv2.Scharr(img, CV_32F, 1, 0)", "2,560", "× 32", ACCENT),
            ("scipy.ndimage.sobel(img, axis=1)", "640", "× 8", INK),
            ("skimage.filters.sobel, one axis", "160", "× 2", INK),
            ("skimage.filters.sobel, magnitude", "113.1", "× 2 ÷ √2", INK),
            ("normalised to slope 1", "80", "× 1", GREEN)]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    v += label(110, 552, "call", SOFT, "start", 14)
    v += label(820, 552, "output at (r2, c3)", SOFT, "end", 14)
    v += label(970, 552, "scale", SOFT, "end", 14)
    y = 626
    for call, out, sc, col in rows:
        v += mono(110, y, call, 20, col, "start", 500)
        v += mono(820, y, out, 30, col, "end", 600)
        v += mono(970, y, sc, 20, col, "end")
        y += 80
    emit("feed", 2, "scharr-returns-four-times-sobel",
         ["Scharr returns four", "times Sobel."],
         ["The patch's clean step rises 160 grey levels, a slope of 80 per",
          "pixel. Each call reports it at its own scale."],
         v,
         ["All six mean a slope of 80. Normalise once, and",
          "threshold in grey levels per pixel."],
         FEED_TOTAL)


def feed_03():
    rows = [("Prewitt", DIR4["Prewitt"], BROWN), ("central difference", DIR4["central difference"], VIOLET),
            ("Sobel", DIR4["Sobel"], BLUE), ("[1 4 1]/6", DIR4["[1 4 1]/6"], GREEN),
            ("Scharr", DIR4["Scharr"], ACCENT), ("Farid–Simoncelli 5-tap", DIR4["Farid–Simoncelli 5"], INK)]
    v = label(72, 480, "worst direction error over orientation · 4-px wavelength · closed form", SOFT, "start", 14)
    v += bars(72, 526, rows, 420, 52, 100, 8.0, lambda d: f"{d:.2f}°", lab_w=330, size=26)
    emit("feed", 3, "the-gradient-turns",
         ["The gradient turns."],
         ["A central difference blurs along its own axis, so on stripes at",
          "an angle it shrinks one component more and the vector turns."],
         v,
         ["Scharr's cross-weight matches that blur down to 3.45 px.",
          "Sobel's matches it only at the 2-pixel Nyquist pattern."],
         FEED_TOTAL)


def feed_04():
    x, cs = 110, 92
    v = box(72, 500, 936, 610, "#ffffff", RULE_SOLID)
    for r in range(3):
        for c in range(3):
            val = PATCH[1 + r][1 + c]
            v += pixel(x + c * cs, 540 + r * cs, cs, cs, val, 26, hi=(val == 255))
    diffs = F.gx_family(PATCH, 2, 2, 0.25)[1]
    for r, d in enumerate(diffs):
        v += mono(x + 3 * cs + 26, 540 + r * cs + cs * 0.62, f"row {d:.1f}".replace("-", "−"), 24,
                  ACCENT if d < 0 else INK, "start", 600)
    v += mono(650, 612, "80 − 107.5 (1 − 2p)", 24, INK, "start", 600)
    v += txt(650, 652, "output at (r2, c2), p on", 20, MUTED)
    v += txt(650, 680, "each neighbouring row", 20, MUTED)
    rows = [("Prewitt", IMP["Prewitt"]), ("Sobel", IMP["Sobel"]), ("Scharr", IMP["Scharr"]),
            ("central difference", IMP["central difference"])]
    y = 906
    v += label(110, y - 40, "filter", SOFT, "start", 14)
    v += label(760, y - 40, "output", SOFT, "end", 14)
    v += label(970, y - 40, "error against 80", SOFT, "end", 14)
    for name, g in rows:
        col = ACCENT if name == "Scharr" else INK
        v += txt(110, y, name, 26, col, SANS, 600)
        v += mono(760, y, f"{g:.2f}".replace("-", "−"), 26, col, "end", 600)
        v += mono(970, y, f"{(80 - g) / 80 * 100:.0f}%", 26, col, "end", 600)
        y += 52
    emit("feed", 4, "robust-or-isotropic",
         ["Robust or isotropic:", "pick one."],
         ["Beside the patch's one bad pixel, the output is a straight line",
          "in p. The clean value is 80."],
         v,
         ["A direction-tuned filter weights the centre row,",
          "and the centre row is where the bad pixel sits."],
         FEED_TOTAL)


def feed_05():
    v = trunc_bars(110, 560)
    emit("feed", 5, "three-taps-at-sigma-2",
         ["(3, 3) at σ = 2 is", "a σ = 0.8 blur."],
         ["Truncating a Gaussian keeps its brightness, because the weights",
          "are renormalised. What it takes is the spread."],
         v,
         ["Use at least 2⌈3σ⌉ + 1 taps — 13 at σ = 2 — or pass",
          "ksize (0, 0) and let the library size the kernel."],
         FEED_TOTAL)


def feed_06():
    g, y = gauss_rows(110, 560, 150, 96)
    g += hline(110, 970, y - 30)
    g += txt(110, y + 20, "on the patch's bad pixel, a 3×3 blur gives", 24, MUTED)
    g += mono(110, y + 72, "98.6 at σ = 0.8", 30, MUTED, "start", 600)
    g += mono(560, y + 72, "93.75 with sigma 0", 30, ACCENT, "start", 600)
    g += txt(110, y + 124, "the same kind of table covers ksize 5, 7 and 9", 22, SOFT)
    emit("feed", 6, "sigma-zero-is-not-sigma-point-eight",
         ["σ = 0 is not", "σ = 0.8."],
         ["For a 3×3 kernel with sigma 0, OpenCV documents σ = 0.8.",
          "The source returns a hard-coded binomial instead."],
         g,
         ["Pass σ explicitly when the number matters. The table is",
          "already in OpenCV's 2.4 branch, and still undocumented."],
         FEED_TOTAL)


def feed_07():
    v = border_rows(110, 560, 80, 72)
    emit("feed", 7, "the-border-is-part-of-the-kernel",
         ["The border is part", "of the kernel."],
         ["Row r2 extended past its left edge four ways, and the",
          "normalised Sobel on the edge pixel (r2, c0)."],
         v,
         ["OpenCV's default gives exactly 0 on the edge column for",
          "any image. SciPy's gives 430 here, raw — same stencil."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    items = [("direction", "Scharr, or Farid–Simoncelli's 5-tap pair", "0.29° and 0.17° at a 4-px wavelength"),
             ("a bad pixel nearby", "a larger p — Sobel over Scharr", "67% error against 84%"),
             ("a Gaussian", "2⌈3σ⌉ + 1 taps, σ passed explicitly", "no fixed table, no hidden truncation"),
             ("the border", "crop by the kernel radius before measuring", "reflect-101 zeroes the edge column")]
    y = 574
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "direction" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 128
    emit("feed", 8, "read-the-article",
         ["Kernel design,", "by hand."],
         ["Sobel, Scharr, Farid–Simoncelli, truncated and discrete Gaussians",
          "and five border rules, all on one 5×5 patch."],
         v,
         ["The full walk-through, with the tooling map for",
          "OpenCV, SciPy, NumPy and scikit-image."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = stencil(285, 760, 170, 42)
    v += label(72, 1330, "direction error, 4-px pattern", SOFT, "start", 16)
    rows = [("Scharr", "p = 3/16", f"{DIR4['Scharr']:.2f}°", ACCENT),
            ("Sobel", "p = 1/4", f"{DIR4['Sobel']:.2f}°", INK)]
    y = 1386
    for name, pv, d, col in rows:
        v += txt(72, y, name, 36, col, SANS, 600)
        v += mono(560, y, pv, 32, col, "middle")
        v += mono(1008, y, d, 36, col, "end", 600)
        y += 56
    emit("story", 1, "sobel-and-scharr-are-one-stencil",
         ["Sobel and Scharr are", "one stencil."],
         ["Only p, the weight on the", "neighbouring rows, differs."],
         v,
         ["Scharr's 3/16 keeps direction within 0.3°", "on a 4-pixel pattern. Sobel's 1/4: 3.2°."],
         STORY_TOTAL)


def story_02():
    rows = [("cv2.Sobel", "640", INK), ("cv2.Scharr", "2,560", ACCENT),
            ("skimage sobel, one axis", "160", INK), ("normalised", "80", GREEN)]
    v = box(72, 800, 936, 600, "#ffffff", RULE_SOLID)
    v += label(120, 870, "call", SOFT, "start", 16)
    v += label(960, 870, "output on the clean step", SOFT, "end", 16)
    y = 980
    for call, out, col in rows:
        v += mono(120, y, call, 30, col, "start", 600)
        v += mono(960, y, out, 44, col, "end", 600)
        y += 118
    emit("story", 2, "scharr-returns-four-times-sobel",
         ["Scharr returns four", "times Sobel."],
         ["Same step, same slope of 80.", "Four scales."],
         v,
         ["Normalise once, then threshold", "in grey levels per pixel."],
         STORY_TOTAL)


def story_03():
    emit("story", 3, "three-taps-at-sigma-2",
         ["(3, 3) at σ = 2 is", "a σ = 0.8 blur."],
         ["Renormalising keeps the brightness.", "Truncation takes the spread."],
         trunc_bars(110, 860, big=True),
         ["13 taps at σ = 2 reach 1.99.", "3 taps reach 0.80."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["direction: Scharr, not a bigger Sobel",
             "bad pixels: a larger p",
             "Gaussian: 2⌈3σ⌉ + 1 taps, σ explicit",
             "border: crop before you measure"]
    y = 900
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 32, INK, SANS, 600 if i == 0 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Four rules for", "every kernel."],
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
