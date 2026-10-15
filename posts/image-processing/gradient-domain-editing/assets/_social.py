#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Gradient-Domain Editing: Poisson Cloning, HDR
and Tiling".

Image Processing by Hand, part 14. The shell (lockup, rule, serif title, deck, takeaway, footer) is
copied from part 13's _social.py (itself from parts 12, 9 and 11, with the lockup reading "canery.in"
as in part 10). Every number on a card comes from `_data.py` — the nine equations, the Gauss-Seidel
errors, the V-cycle, the shadow clone in codes and in log, Fattal's factor and the attenuated square —
so a card cannot disagree with the article. Colours follow the figures: blue marks the region solved,
tangerine a departure, an overshoot or the coarse step, and pixel cells are high value = bright.

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
CANONICAL = "canery.in/blogs/gradient-domain-editing"
FOOTER = "GRADIENT-DOMAIN EDITING · CANERY.IN"

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
assert d.XSTAR[3] == 255 and round(d.SWEEP_ERR[3], 1) == 31.1 and round(d.V1_ERR, 1) == 15.4
assert round(float(d.FILL_SHADOW[4]), 1) == -40.0 and round(d.CIRC, 3) == -0.337
WHITE = "#ffffff"
LINE = "rgba(45,49,66,0.40)"
INK_RGB = (45, 49, 66)


def grey(v):
    """High value = bright, the series rule; clamped to 0..255 for the fill."""
    t = max(0.0, min(1.0, float(v) / 255))
    return blend(INK_RGB, 0.88 * (1 - t) + 0.02, (245, 245, 245))


def on(v):
    return WHITE if float(v) < 133 else INK


def fmt1(v):
    v = float(v)
    return f"{v:,.1f}".replace("-", "−") if abs(v - round(v)) > 1e-9 else f"{round(v):,}".replace("-", "−")


def cellv(x, y, cs, v, size, stroke="rgba(45,49,66,0.30)", sw=1, txt_override=None):
    s = rect(x, y, cs, cs, grey(v), stroke, sw)
    s += mono(x + cs / 2, y + cs / 2 + size * 0.36, txt_override or fmt1(v), size, on(v), "middle", 600)
    return s


def grid5(x0, y0, cs, frame, inner, size, unknown=False, neg=False, laps=None):
    """The patch's 5x5: ring from `frame`, interior from `inner` (row-major 9); corners pale."""
    s = ""
    for i in range(5):
        for j in range(5):
            x, y = x0 + j * cs, y0 + i * cs
            if (i, j) in ((0, 0), (0, 4), (4, 0), (4, 4)):
                s += rect(x, y, cs, cs, blend(INK_RGB, 0.05, (245, 245, 245)), "rgba(45,49,66,0.25)", 1)
            elif 1 <= i <= 3 and 1 <= j <= 3:
                if unknown and laps is not None:
                    s += rect(x, y, cs, cs, WHITE, "rgba(45,49,66,0.30)", 1)
                    s += mono(x + cs / 2, y + 26, "?", 18, SOFT, "middle", 500)
                    s += mono(x + cs / 2, y + cs - 16, fmt1(laps[3 * (i - 1) + (j - 1)]), size - 2, ACCENT, "middle", 600)
                elif unknown:
                    s += rect(x, y, cs, cs, WHITE, "rgba(45,49,66,0.30)", 1)
                    s += mono(x + cs / 2, y + cs / 2 + size * 0.4, "?", size + 4, SOFT, "middle", 500)
                else:
                    v = float(inner[3 * (i - 1) + (j - 1)])
                    s += cellv(x, y, cs, v, size)
                    if neg and v < 0:
                        s += rect(x + 3, y + 3, cs - 6, cs - 6, "none", ACCENT, 4)
            else:
                s += cellv(x, y, cs, frame[i][j], size)
    s += rect(x0 + cs, y0 + cs, 3 * cs, 3 * cs, "none", LINK, 4)
    s += rect(x0, y0, 5 * cs, 5 * cs, "none", "rgba(45,49,66,0.6)", 1.5)
    return s


def arrow_r(x1, x2, y, col=ACCENT, sw=4):
    return (line(x1, y, x2 - 14, y, col, sw)
            + f'<polygon points="{x2 - 18},{y - 10} {x2},{y} {x2 - 18},{y + 10}" fill="{col}"/>')


FEED_TOTAL, STORY_TOTAL = 8, 4
SHADOW = [[float(v) for v in row] for row in d.SHADOW]


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cs = 62
    xa, xb, y0 = 110, 660, 600
    v += mono(xa, 570, "12 known · 9 unknown", 20, MUTED, "start", 600)
    v += mono(xb, 570, "the 9 pixels, back", 20, MUTED, "start", 600)
    v += grid5(xa, y0, cs, d.PATCH, None, 20, unknown=True)
    v += grid5(xb, y0, cs, d.PATCH, d.XSTAR, 20)
    v += arrow_r(xa + 5 * cs + 26, xb - 22, y0 + 2.5 * cs)
    v += mono((xa + 5 * cs + xb) / 2, y0 + 2.5 * cs - 24, "solve", 22, ACCENT, "middle", 600)
    v += mono(xa, 1000, "kept inside: the Laplacian, 215 · 160 · −160 / −860 · 375 · −160 / …", 19, MUTED)
    v += mono(xa, 1040, "solved: ∇²f = div v inside, f fixed on the frame", 20, INK, "start", 600)
    v += mono(xa, 1090, "the series' 5×5 patch · Ω, outlined in blue, is rows r1–r3 × columns c1–c3", 16, SOFT)
    emit("feed", 1, "keep-the-gradients",
         ["Keep the gradients.", "Get the pixels back."],
         ["Throw away the 3×3 interior of a 5×5 patch;", "keep its Laplacian and the 12 pixels around it."],
         v,
         ["Gradients plus a border fix every pixel:", "the one solution of a Poisson equation."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "the equation at the impulse, (r2, c1):", 20, MUTED, "start", 600)
    v += mono(110, 610, "4f(r2,c1) − f(r1,c1) − f(r3,c1) − f(r2,c2)", 26, INK, "start", 600)
    v += mono(110, 656, "= 40", 26, INK, "start", 600)
    v += mono(320, 656, "+ 860", 26, INK, "start", 600)
    v += mono(142, 690, "known left pixel", 17, SOFT)
    v += mono(350, 690, "minus its Laplacian, −860", 17, SOFT)
    v += mono(110, 736, "= 900", 26, LINK, "start", 600)
    v += hline(110, 970, 780)
    v += mono(110, 830, "check with the patch:  4 × 255 − 40 − 40 − 40 = 900", 21, INK, "start", 600)
    v += mono(110, 900, "all nine right-hand sides, row by row:", 19, MUTED)
    bs = [fmt1(x) for x in d.B]
    v += mono(110, 940, "  ".join(bs[:3]) + "   ·   " + "  ".join(bs[3:6]), 21, INK, "start", 600)
    v += mono(110, 976, "  ".join(bs[6:]), 21, INK, "start", 600)
    v += mono(110, 1050, "A: 4 on the diagonal, −1 between neighbours; symmetric, positive definite", 17, SOFT)
    emit("feed", 2, "nine-equations",
         ["Nine pixels,", "nine equations."],
         ["One five-point stencil per unknown, with", "the known frame moved to the right-hand side."],
         v,
         ["A is symmetric and positive definite,", "so the patch is the only solution."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "largest error after each sweep, from all zeros", 20, MUTED, "start", 600)
    vals = d.SWEEP_ERR[:9]
    base, top, x0, bw = 960, 600, 120, 88
    for k, e in enumerate(vals):
        h = (base - top) * e / 255
        col = ACCENT if k == 3 else LINK
        v += rect(x0 + k * 96, base - h, bw, h, blend((46, 90, 168), 0.25 + 0.5 * min(1, e / 255)) if k != 3 else ACCENT)
        lab = fmt1(round(e, 1)) if e >= 1 else f"{e:.2f}"
        v += mono(x0 + k * 96 + bw / 2, base - h - 12, lab, 18, col if k == 3 else INK, "middle", 600)
        v += mono(x0 + k * 96 + bw / 2, base + 30, "start" if k == 0 else f"{k}", 16, SOFT, "middle")
    v += hline(110, 970, base, MUTED, 1.5)
    v += mono(110, 1030, "sweep 3 leaves 31.1; from then on the error halves each sweep.", 19, INK, "start", 600)
    v += mono(110, 1064, "cos²(π/4) = 0.5 is the slowest pattern's factor on nine unknowns", 18, MUTED)
    emit("feed", 3, "three-sweeps",
         ["Three sweeps leave", "31 levels of error."],
         ["Gauss–Seidel on the nine equations:", "each unknown from its neighbours, in turn."],
         v,
         ["Sweeps strip the jumps fast and the", "smooth bowl slowly, here halving per sweep."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    steps = [("1", "one sweep", f"largest error {fmt1(round(d.SWEEP_ERR[1], 1))}", INK),
             ("2", "residual, full weighting onto one point", f"r = {fmt1(round(float(d.V_RC), 1))}", INK),
             ("3", "coarse equation: (3/4) · e = r", f"e = {fmt1(round(float(d.V_EC), 1))}", ACCENT),
             ("4", "interpolate back: centre, edges, corners", "106.8 · 53.4 · 26.7", ACCENT),
             ("5", "add it, one more sweep", f"largest error {fmt1(round(d.V1_ERR, 1))}", LINK)]
    y = 566
    for n, what, val, col in steps:
        v += mono(110, y, n, 26, col, "start", 600)
        v += mono(160, y, what, 21, INK)
        v += mono(970, y, val, 22, col, "end", 600)
        y += 82
    v += hline(110, 970, y - 34)
    v += mono(110, y + 14, f"three plain sweeps: {fmt1(round(d.SWEEP_ERR[3], 1))}  ·  one V-cycle: "
                           f"{fmt1(round(d.V1_ERR, 1))}  ·  two: {d.maxabs(d.err(d.V2)):.2f}", 20, INK, "start", 600)
    v += mono(110, y + 64, "3/4 = restriction × A × interpolation, on the one coarse point", 18, MUTED)
    emit("feed", 4, "one-v-cycle",
         ["One V-cycle halves what", "three sweeps leave."],
         ["Multigrid removes the smooth error on a", "coarser grid, where it is no longer smooth."],
         v,
         ["At 1,023 pixels wide, plain sweeps need", "244,633 per digit; multigrid's work is O(n)."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cs = 60
    xa, xb, y0 = 110, 660, 600
    v += mono(xa, 570, "in codes", 21, INK, "start", 600)
    v += mono(xb, 570, "in log", 21, INK, "start", 600)
    v += grid5(xa, y0, cs, SHADOW, [float(x) for x in d.FILL_SHADOW], 17, neg=True)
    v += grid5(xb, y0, cs, SHADOW, d.FILL_LOG, 18)
    v += mono(xa, 940, "−40 at (r2, c2): below black", 20, ACCENT, "start", 600)
    v += mono(xb, 940, "the shadowed patch, exactly", 19, LINK, "start", 600)
    v += hline(110, 970, 980)
    v += mono(110, 1030, "frame: the patch at a fifth of the light (8 for 40, 40 for 200)", 18, MUTED)
    v += mono(110, 1064, "in log a fifth of the light is −ln 5 all round the frame: a flat membrane", 18, MUTED)
    emit("feed", 5, "differences-not-ratios",
         ["A clone keeps", "differences, not ratios."],
         ["The patch's gradients cloned into a copy of", "itself at a fifth of the light."],
         v,
         ["In codes the dark side goes below black.", "Clone a change of light in log."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("bounding box, sine transform", "solves the mask's whole box exactly, no iteration", LINK),
             ("mask eroded 3 px", "a mask under 7 px wide clones nothing (#17450, open)", ACCENT),
             ("MIXED_CLONE: abs(gx − gy)", "the spike's own (−215, −215) gives 0: it never wins", ACCENT),
             ("truncation", "a value that should be 40 can be stored as 39", ACCENT),
             ("from 4.11.0", "a 1-channel mask is eroded and inverted in place", ACCENT)]
    y = 562
    for head, detail, col in items:
        v += mono(110, y, head, 23, col, "start", 600)
        v += mono(110, y + 34, detail, 19, INK)
        y += 104
    emit("feed", 6, "seamlessclone-is-not-the-paper",
         ["seamlessClone is", "not the paper."],
         ["OpenCV's photo module, read from source at", "802cf95 and 4.10.0 to 5.0.0, not run."],
         v,
         ["The 5×5 patch with a full mask", "clones nothing at all."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 560, "φ = (|∇H| / α)^(β − 1)", 28, INK, "start", 600)
    v += mono(110, 596, "H = log luminance · α = 0.1 × mean gradient · β 0.8 to 0.9", 18, MUTED)
    v += hline(110, 970, 630)
    v += mono(110, 678, "the step row, at β = 0.85:", 20, MUTED, "start", 600)
    v += mono(110, 716, "ln 5 = 1.609 at 25α  →  × 0.617  →  0.993", 22, INK, "start", 600)
    v += mono(110, 754, "a 5:1 step becomes 2.70:1", 22, ACCENT, "start", 600)
    v += hline(110, 970, 790)
    v += mono(110, 838, "one square of the patch, attenuated:", 20, MUTED, "start", 600)
    sx, sy, side = 130, 870, 150
    v += line(sx, sy, sx + side, sy, INK, 4) + line(sx + side, sy, sx + side, sy + side, MUTED, 2)
    v += line(sx + side, sy + side, sx, sy + side, ACCENT, 4) + line(sx, sy + side, sx, sy, MUTED, 2)
    for px, py in ((sx, sy), (sx + side, sy), (sx + side, sy + side), (sx, sy + side)):
        v += f'<circle cx="{px}" cy="{py}" r="8" fill="#ffffff" stroke="{INK}" stroke-width="2.5"/>'
    v += mono(330, 892, f"row r1, left to right: +{d.GX_R1:.3f}", 21, INK, "start", 600)
    v += mono(330, 930, f"row r2, left to right: +{d.GX_R2:.3f}", 21, ACCENT, "start", 600)
    v += mono(330, 968, "down both columns: 0", 21, MUTED)
    v += mono(330, 1012, f"round the loop: {d.GX_R1:.3f} − {d.GX_R2:.3f} = {d.CIRC:.3f}".replace("= -", "= −"), 22, INK,
              "start", 600)
    v += mono(330, 1050, "an image's loops sum to zero", 18, SOFT)
    emit("feed", 7, "hdr-shrink-and-solve",
         ["HDR: shrink the big", "gradients, solve again."],
         ["Fattal's attenuation on the log of the", "patch, with one pyramid level."],
         v,
         ["The shrunken field is no image's gradient,", "so least squares picks the nearest image."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("kept", "12 frame values and 9 Laplacians", "the 9 pixels come back exactly"),
             ("solved", "3 sweeps: 31.1 · one V-cycle: 15.4", "OpenCV uses a sine transform: exact"),
             ("cloned", "at (r2, c2): −40 in codes, 8 in log", "clone a change of light in log"),
             ("tiled", "40 40 40 200 200 → 120 80 40 160 120", "the seam's 160 becomes a slope")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "cloned" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Gradient-domain", "editing, by hand."],
         ["Poisson cloning, HDR compression and", "seamless tiling on one 5×5 patch."],
         v,
         ["The full walk-through, every number worked", "by hand, and the tooling map."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    cs = 80
    xa, xb, y0 = 110, 570, 840
    v = mono(xa, 806, "kept: frame + Laplacians", 26, MUTED, "start", 600)
    v += mono(xb, 806, "solved", 28, MUTED, "start", 600)
    v += grid5(xa, y0, cs, d.PATCH, None, 24, unknown=True, laps=d.LAP)
    v += grid5(xb, y0, cs, d.PATCH, d.XSTAR, 24)
    v += mono(xa, y0 + 5 * cs + 70, "∇²f = div v inside,", 30, INK, "start", 600)
    v += mono(xa, y0 + 5 * cs + 112, "f fixed on the frame", 30, INK, "start", 600)
    emit("story", 1, "keep-the-gradients",
         ["Keep the gradients.", "Lose the pixels."],
         ["Twelve values and nine Laplacians", "are all that is kept."],
         v,
         ["Nine equations bring", "the pixels back."],
         STORY_TOTAL)


def story_02():
    v = ""
    vals = d.SWEEP_ERR[:9]
    y = 830
    for k, e in enumerate(vals):
        w = 600 * e / 255
        col = ACCENT if k == 3 else blend((46, 90, 168), 0.3 + 0.5 * min(1, e / 255))
        v += mono(110, y + 34, "start" if k == 0 else f"sweep {k}", 24, SOFT)
        v += rect(300, y + 4, max(w, 3), 40, col)
        lab = fmt1(round(e, 1)) if e >= 1 else f"{e:.2f}"
        v += mono(300 + max(w, 3) + 16, y + 34, lab, 28, ACCENT if k == 3 else INK, "start", 600)
        y += 64
    emit("story", 2, "31-after-three-sweeps",
         ["31 levels after", "three sweeps."],
         ["Gauss–Seidel on nine unknowns,", "from all zeros."],
         v,
         ["One multigrid V-cycle", "leaves 15.4."],
         STORY_TOTAL)


def story_03():
    v = rect(110, 820, 400, 400, grey(0), "rgba(45,49,66,0.4)", 2)
    v += rect(122, 832, 376, 376, "none", ACCENT, 8)
    v += mono(310, 1050, "−40", 96, WHITE, "middle", 600)
    v += rect(570, 820, 400, 400, grey(8), "rgba(45,49,66,0.4)", 2)
    v += rect(582, 832, 376, 376, "none", LINK, 8)
    v += mono(770, 1050, "8", 96, WHITE, "middle", 600)
    v += mono(110, 1290, "in codes", 30, ACCENT, "start", 600)
    v += mono(570, 1290, "in log", 30, LINK, "start", 600)
    v += mono(110, 1360, "pixel (r2, c2) of the patch, cloned", 26, MUTED)
    v += mono(110, 1400, "into its fifth-light copy", 26, MUTED)
    emit("story", 3, "minus-40-or-8",
         ["−40 or 8?"],
         ["One pixel, cloned into", "a fifth of the light, two ways."],
         v,
         ["Clone a change of light", "in log."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["gradients + a border = the image",
             "sweeps kill jumps fast, bowls slowly",
             "clone a change of light in log",
             "seamlessClone is not the paper"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 2 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Gradient-domain", "editing."],
         ["Worked on nine pixels", "of one 5×5 patch."],
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
