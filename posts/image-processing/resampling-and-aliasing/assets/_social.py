#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Resampling and Aliasing".

Image Processing by Hand, part 3. The shell (lockup, rule, serif title, deck, takeaway,
footer) is the construction the NVIDIA Stack and Diffusion series settled on, with the
lockup reading "canery.in". Every number on a card is recomputed here from the same
kernels `_figs.py` uses, on row r2 of the shared patch, so a card cannot disagree with
the article. Pixel cells follow the article's convention: high value = bright.

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
GREEN, BLUE, MUSTARD = "#7c8f6f", "#5e7a9b", "#b8915a"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/resampling-and-aliasing"
FOOTER = "RESAMPLING AND ALIASING · CANERY.IN"

# ------------------------------------------------------------------ the numbers
ROW = F.ROW
XS_DN, XS_UP = F.XS_DN, F.XS_UP
DOWN = {n: [F.value(x, n) for x in XS_DN] for n in ("nearest", "linear", "cubic", "lanczos3")}
AREA_W = F.matrix("area")
AREA = [sum(AREA_W[j][i] * ROW[i] for i in range(5)) for j in range(3)]
COLS = {n: [sum(F.matrix(n)[j][i] for j in range(3)) for i in range(5)]
        for n in ("nearest", "linear", "area")}
UP_L3 = [F.value(x, "lanczos3") for x in XS_UP]
CV_NN = [ROW[min(int(j / 0.6), 4)] for j in range(3)]          # OpenCV floor index
assert [round(v, 2) for v in DOWN["linear"]] == [111.67, 40.0, 200.0]
assert [round(v) for v in AREA] == [126, 115, 200] and CV_NN == [40, 255, 200]


def mean(v):
    return sum(v) / len(v)


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
def shrink_compare(y0, big=False):
    """Row r2 and two 0.6x shrinks of it: the default and area averaging."""
    cw, ch = (160, 120) if big else (150, 104)
    x = (VW - 5 * cw) / 2
    v = label(x, y0 - 18, "row r2 · mean 147", SOFT, "start", 15 if not big else 17)
    v += pixel_row(x, y0, cw, ch, ROW, 34 if big else 30, hi={1})
    y = y0 + ch + (96 if big else 80)
    ow = 5 * cw / 3
    for name, vals, col, note in (("INTER_LINEAR, the default", DOWN["linear"], MUTED, "2 taps"),
                                  ("INTER_AREA", AREA, ACCENT, "width 1/s")):
        v += label(x, y - 16, f"0.6× · {name} · {note}", col, "start", 15 if not big else 17)
        for j, val in enumerate(vals):
            v += pixel(x + j * ow, y, ow, ch * 0.8, round(val, 2), 28 if big else 26,
                       hi=col == ACCENT)
        v += mono(x + 5 * cw, y + ch * 0.8 + 36, f"mean {mean(vals):.1f}", 22 if not big else 26,
                  col, "end", 600)
        y += ch * 0.8 + (110 if big else 92)
    return v


def impulse_compare(y0, big=False):
    cw, ch = (160, 120) if big else (150, 104)
    x = (VW - 5 * cw) / 2
    v = pixel_row(x, y0, cw, ch, ROW, 34 if big else 30, hi={1})
    y = y0 + ch + (100 if big else 84)
    ow = 5 * cw / 3
    for name, picks, vals, col in (("pixel centres · reads c0 c2 c4", [0, 2, 4], [40, 40, 200], MUTED),
                                   ("OpenCV INTER_NEAREST · reads c0 c1 c3", [0, 1, 3], CV_NN, ACCENT)):
        v += label(x, y - 16, name, col, "start", 15 if not big else 17)
        for j, val in enumerate(vals):
            v += pixel(x + j * ow, y, ow, ch * 0.8, val, 28 if big else 26, hi=(val == 255))
        y += ch * 0.8 + (110 if big else 96)
    return v


def column_sums(y0, big=False):
    rows = [("nearest", COLS["nearest"], MUTED), ("linear", COLS["linear"], BLUE),
            ("area", COLS["area"], ACCENT)]
    x0, cw = 250, 150
    bh = 150 if big else 120
    v = ""
    for i in range(5):
        v += label(x0 + i * cw + cw / 2, y0, f"c{i}", ACCENT if i == 1 else SOFT, "middle", 16)
    y = y0 + 30
    for name, cs, col in rows:
        v += txt(x0 - 24, y + bh * 0.62, name, 30 if big else 28, col, SANS, 600, "end")
        v += hline(x0, x0 + 5 * cw, y + bh, RULE_SOLID, 1.5)
        for i, c in enumerate(cs):
            hgt = c * (bh - 36)
            v += (f'<rect x="{x0 + i * cw + 28}" y="{y + bh - hgt:.1f}" width="{cw - 56}" '
                  f'height="{max(hgt, 0):.1f}" fill="{col}" fill-opacity="{0.9 if col == ACCENT else 0.55}"/>')
            v += mono(x0 + i * cw + cw / 2, y + bh - hgt - 10, f"{c:.3g}" if c else "0", 22 if not big else 24,
                      col, "middle", 600)
        y += bh + (44 if big else 34)
    return v


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 7, 4


def feed_01():
    emit("feed", 1, "shrinking-is-not-enlarging-backwards",
         ["Shrinking is not", "enlarging backwards."],
         ["Enlarging fills in between samples. Shrinking also has to",
          "remove the detail the coarser grid cannot hold."],
         shrink_compare(540),
         ["A shrink by s needs a kernel 1/s times wider. The default",
          "reads the same two pixels however far you shrink."],
         FEED_TOTAL)


def feed_02():
    emit("feed", 2, "the-impulse-is-there-or-not",
         ["The impulse is there,", "or it isn't."],
         ["Row r2 shrunk to 0.6× by nearest-neighbour, twice. Same kernel,",
          "same factor, grids laid half a cell apart."],
         impulse_compare(540),
         ["Output that depends on where the grid happens to fall,",
          "not on the image, is what aliasing looks like in space."],
         FEED_TOTAL)


def feed_03():
    v = column_sums(540)
    emit("feed", 3, "audit-a-resize-by-its-column-sums",
         ["Audit a resize by", "its column sums."],
         ["A column sum is the total weight one input pixel gets across",
          "every output. For a 0.6× shrink they should all be 0.6."],
         v,
         ["Equal columns count every pixel equally, and keep the",
          "mean: 147 in, 147 out. Only area averaging manages it."],
         FEED_TOTAL)


def feed_04():
    rows = [("Rifman", "a = −1", "14.8%", MUTED),
            ("OpenCV INTER_CUBIC", "a = −3/4", "11.1%", ACCENT),
            ("Keys · Pillow BICUBIC", "a = −1/2", "7.4%", INK),
            ("Mitchell (B, C) = (1/3, 1/3)", "off the axis", "3.6%", MUTED)]
    v = box(72, 510, 936, 560, "#ffffff", RULE_SOLID)
    v += label(110, 566, "cubic kernel", SOFT, "start", 14)
    v += label(700, 566, "parameter", SOFT, "end", 14)
    v += label(970, 566, "overshoot on an edge", SOFT, "end", 14)
    y = 650
    for name, a, ov, col in rows:
        v += txt(110, y, name, 28, col, SANS, 600)
        v += mono(700, y, a, 26, INK, "end")
        v += mono(970, y, ov, 30, col, "end", 600)
        y += 92
    v += hline(110, 970, y - 50)
    v += mono(540, y + 12, "Keys family: overshoot = −4a/27 of the step height", 24, INK, "middle", 600)
    emit("feed", 4, "bicubic-is-a-family",
         ["“Bicubic” is not", "one kernel."],
         ["Keys' cubic has a free parameter a. Each library picks its own,",
          "and the edge overshoot changes with it."],
         v,
         ["Only a = −1/2 is third-order accurate: it reproduces",
          "every quadratic exactly. OpenCV uses −3/4."],
         FEED_TOTAL)


def feed_05():
    x0, y0, w, h = 150, 480, 820, 460
    xr, yr = (-0.5, 4.5), (0, 280)
    X = lambda u: x0 + (u - xr[0]) / (xr[1] - xr[0]) * w
    Y = lambda u: y0 + h - (u - yr[0]) / (yr[1] - yr[0]) * h
    v = hline(x0, x0 + w, Y(0), RULE_SOLID, 1.5)
    for lvl, lab in ((40, "40"), (200, "200"), (255, "255 · 8-bit ceiling")):
        v += hline(x0, x0 + w, Y(lvl), RULE_SOLID, 1.5, "8,8")
        v += mono(x0 - 12, Y(lvl) + 7, lab.split(" ")[0], 18, SOFT, "end")
    v += mono(x0 + w, Y(255) - 12, "8-bit ceiling", 16, SOFT, "end")
    pts = " ".join(f"{X(-0.5 + 5 * i / 400):.1f},{Y(F.recon(-0.5 + 5 * i / 400, 'lanczos3')):.1f}"
                   for i in range(401))
    v += f'<polyline points="{pts}" fill="none" stroke="{MUSTARD}" stroke-width="5"/>'
    for i, r in enumerate(ROW):
        v += f'<circle cx="{X(i):.1f}" cy="{Y(r):.1f}" r="7" fill="{MUTED}"/>'
    for j, (x, val) in enumerate(zip(XS_UP, UP_L3)):
        hot = F.ringing(x, val)
        v += f'<circle cx="{X(x):.1f}" cy="{Y(val):.1f}" r="{10 if hot else 7}" fill="{ACCENT if hot else INK}"/>'
        if j in (0, 2, 6):
            dy = 40 if val < 100 else -22
            v += mono(X(x) + (26 if val < 100 else 0), Y(val) + dy, f"{val:.1f}", 26, ACCENT,
                      "start" if val < 100 else "middle", 600)
    v += label(x0, y0 + h + 50, "row r2 enlarged 1.7× by Lanczos-3 · eight samples", SOFT, "start", 15)
    emit("feed", 5, "enlarging-rings",
         ["Enlarging rings."],
         ["Lanczos-3 keeps the impulse sharp at 1.7× and pays for it:",
          "14.1 in a region that is flat 40, 225.0 over a flat 200."],
         v,
         ["Negative lobes buy sharpness. Near an edge they push",
          "values past the input's range, and 8-bit output clips."],
         FEED_TOTAL)


def feed_06():
    rows = [("Lanczos-3", F.H("lanczos3", 0.4), MUSTARD), ("Keys, a = −1/2", F.H("cubic", 0.4), BLUE),
            ("linear", F.H("linear", 0.4), GREEN),
            ("triangle widened by 1/0.6", F.sinc(0.4 / 0.6) ** 2, ACCENT)]
    x0, w = 460, 460
    v = box(72, 510, 936, 590, "#ffffff", RULE_SOLID)
    v += label(110, 566, "kernel", SOFT, "start", 14)
    v += label(x0, 566, "gain at 0.4 cycles/px — above the 0.6× Nyquist", SOFT, "start", 14)
    y = 640
    for name, g, col in rows:
        v += txt(110, y + 28, name, 26, col if col != ACCENT else ACCENT, SANS, 600)
        v += box(x0, y, g * w, 44, col, col, 4, 1)
        v += mono(x0 + g * w + 14, y + 32, f"{g:.3f}", 26, col, "start", 600)
        y += 96
    v += mono(540, y + 20, "whatever passes folds to a period-5 stripe", 22, MUTED, "middle")
    emit("feed", 6, "better-interpolator-worse-downscaler",
         ["The better interpolator", "is the worse downscaler."],
         ["A 0.6× shrink must remove everything between 0.3 and 0.5",
          "cycles per pixel. Sharper kernels let more of it through."],
         v,
         ["A flat band up to 0.5 is exactly what leaks 0.3 to 0.5.",
          "Widening the kernel by 1/s moves its cutoff to 0.3."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 520, 936, 560, "#ffffff", RULE_SOLID)
    items = [("shrink", "INTER_AREA · Pillow resize · skimage resize", "a kernel that widens with 1/s"),
             ("enlarge", "INTER_CUBIC (a = −3/4) · Pillow BICUBIC (a = −1/2)", "pick the ringing you can live with"),
             ("halve", "pyrDown · INTER_LINEAR at exactly 0.5×", "the one factor the default gets right"),
             ("never", "blur after the shrink", "the folded detail is already there")]
    y = 594
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "shrink" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 124
    emit("feed", 7, "read-the-article",
         ["Resampling and", "aliasing, by hand."],
         ["Nearest, bilinear, bicubic, Lanczos and area averaging on one",
          "five-pixel row: every tap and every output value."],
         v,
         ["The full walk-through, with the tooling map for",
          "OpenCV, Pillow, scikit-image and SciPy."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    emit("story", 1, "shrinking-is-not-enlarging-backwards",
         ["Shrinking is not", "enlarging backwards."],
         ["The default resize reads two pixels", "per output, however far you shrink."],
         shrink_compare(830, big=True),
         ["Area averaging keeps the mean at 147.", "The default drops it to 117.2."],
         STORY_TOTAL)


def story_02():
    emit("story", 2, "the-impulse-is-there-or-not",
         ["The impulse is there,", "or it isn't."],
         ["Two nearest-neighbour grids,", "half a cell apart."],
         impulse_compare(830, big=True),
         ["Same kernel, same factor.", "The grid decided, not the image."],
         STORY_TOTAL)


def story_03():
    emit("story", 3, "audit-a-resize-by-its-column-sums",
         ["Audit a resize by", "its column sums."],
         ["The total weight each input pixel", "gets, for a 0.6× shrink."],
         column_sums(820, big=True),
         ["All equal to 0.6: every pixel counted.", "Only area averaging does it."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["enlarging: choose the kernel",
             "shrinking: widen it by 1/s",
             "bicubic: check which a",
             "audit: resize an impulse, sum it",
             "never blur after the shrink"]
    y = 880
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 32, INK, SANS, 600 if i == 1 else 400)
        y += 108
    emit("story", 4, "read-the-article",
         ["Five rules for", "every resize."],
         ["Worked by hand on one", "five-pixel row."],
         v,
         ["The full walk-through is on Canery."],
         STORY_TOTAL, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07,
            story_01, story_02, story_03, story_04]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
