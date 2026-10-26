#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Few-Step Diffusion and Distillation:
20 Steps Into 1".

Diffusion Models, part 7. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every measured or
computed artefact on a card is read from the lab capture the article ships (../lab/captures.json),
so a card cannot disagree with the post.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import json
import math
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("P7_SOCIAL_OUT", HERE / "social"))
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads(pathlib.Path(os.environ.get("P7_CAPTURES", HERE.parent / "lab" / "captures.json"))
                 .read_text(encoding="utf-8"))
W, REF, ST, SM = CAP["worked"], CAP["reference"], CAP["students"], CAP["samples"]

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
BLUE = "#5e7a9b"
MUSTARD = "#b8915a"
PURPLE = "#8a5a9e"
SAGE = "#7c8f6f"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/few-step-diffusion-distillation"
FOOTER = "FEW-STEP DIFFUSION AND DISTILLATION · CANERY.IN"

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


def txt(x, y, value, size=22, fill=INK, family=SANS, weight=400, anchor="start", track=None,
        italic=False):
    extra = f' letter-spacing="{track}"' if track else ""
    extra += ' font-style="italic"' if italic else ""
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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def grey(v, lo=-1.6, hi=3.2):
    """High value = bright, the series' display convention."""
    u = min(1.0, max(0.0, (v - lo) / (hi - lo)))
    return round(26 + u * (250 - 26))


def polyline(pts, colour, width=5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return ('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
            + f'" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" '
            f'stroke-linecap="round"{d}/>')


class Plot:
    """Data to pixels; logx/logy put an axis on log10, and a reversed range runs right to left."""

    def __init__(self, x, y, w, h, xr, yr, logx=False, logy=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr, self.logx, self.logy = xr, yr, logx, logy

    def X(self, v):
        v = math.log10(v) if self.logx else v
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        v = math.log10(max(v, 1e-12)) if self.logy else v
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h


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
    defs = (f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style>'
            f'<marker id="arrow-a" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="11" '
            f'refX="15" refY="5.5" orient="auto"><polygon points="0 0,16 5.5,0 11" fill="{ACCENT}"/></marker>'
            f'</defs>')
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


FEED_TOTAL, STORY_TOTAL = 7, 4
WORDS = {0: "no", 1: "one", 2: "two", 3: "three"}


# ------------------------------------------------------------------ shared artefacts
def png_gray(rows):
    """A greyscale PNG from rows of 0..255 ints, stdlib only."""
    import base64
    import struct
    import zlib
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()


def tile(x, y, size, flat, side=8, stroke=RULE_SOLID, sw=1.5):
    rows = [[grey(flat[r * side + c]) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>'
            + box(x, y, size, size, "none", stroke, 0, sw))


def mean2(name, key, field):
    vals = [run["steps"][key][field] for run in ST[name].values()]
    return sum(vals) / len(vals)


def flips_near(name):
    """Share of a one-call student's flips that come from noises with margin below 0.1 (mean of seeds)."""
    share = CAP["margin_share"]
    out = []
    for run in ST[name].values():
        fb = run["steps"]["1"]["flip_by_margin"]
        out.append(sum(f * s for f, s in zip(fb[:3], share[:3])) / sum(f * s for f, s in zip(fb, share)))
    return sum(out) / len(out)


def far_flips():
    """Flips among noises with margin 0.4 or more, counted over the four path-following students and both seeds."""
    share = CAP["margin_share"]
    n_far = [round(s * REF["n_eval"]) for s in share[5:]]
    flips, total = 0, 0
    for name in ("regression", "pd", "cd", "shortcut"):
        for run in ST[name].values():
            fb = run["steps"]["1"]["flip_by_margin"][5:]
            flips += sum(round(f * n) for f, n in zip(fb, n_far))
            total += sum(n_far)
    return flips, total


def tiles_rows(x, y, size, gap, rows, cols, label_w=250, label_size=18):
    """Rows of 8x8 samples: (label, images) each, the label in mono caps at the left."""
    out = ""
    for i, (lab, imgs) in enumerate(rows):
        yy = y + i * (size + gap)
        out += label(x, yy + size / 2 + 7, lab, MUTED, "start", label_size)
        for k, j in enumerate(cols):
            out += tile(x + label_w + k * (size + gap), yy, size, imgs[j])
    return out


def cliff(x, y, w, h, size=18, lw=5):
    """The worked example's zoomed map: the exact step and the least-squares student's ramp."""
    M, st, a = W["map"], W["student_1d"], W["a"]
    pl = Plot(x, y, w, h, (-0.05, 0.05), (-6.0, 6.0))
    out = box(x, pl.Y(a / 2), w, pl.Y(-a / 2) - pl.Y(a / 2), ACCENT_TINT, "none", 0, 0)
    out += label(x + w - 12, pl.Y(-a / 2) - 14, "between the crescents", ACCENT, "end", size - 2)
    for v in (a, -a):
        out += hline(x, x + w, pl.Y(v), RULE_SOLID, 1.5, "8,6")
    eps = M["eps"]
    neg = [(e, v) for e, v in zip(eps, M["exact"]) if -0.05 <= e < 0]
    pos = [(e, v) for e, v in zip(eps, M["exact"]) if 0 < e <= 0.05]
    out += polyline([(pl.X(e), pl.Y(v)) for e, v in neg], INK, lw)
    out += polyline([(pl.X(e), pl.Y(v)) for e, v in pos], INK, lw)
    out += polyline([(pl.X(0), pl.Y(neg[-1][1])), (pl.X(0), pl.Y(pos[0][1]))], INK, 2, "3,7")
    out += polyline([(pl.X(e), pl.Y(v)) for e, v in st["curve"] if abs(e) <= 0.05], ACCENT, lw)
    out += hline(x, x + w, y + h, RULE_SOLID, 1.5)
    for e in (-0.04, -0.02, 0, 0.02, 0.04):
        out += mono(pl.X(e), y + h + 34, f"{e:+.2f}".replace("+0.00", "0").replace("-", "−"), size, SOFT, "middle")
    out += mono(x + 8, pl.Y(a) - 12, f"crescent +{a:.2f}", size - 2, SOFT)
    out += mono(x + w - 8, pl.Y(-a) - 12, f"crescent −{a:.2f}", size - 2, SOFT, "end")
    return out, pl


# ------------------------------------------------------------------ feed
def feed_01():
    rows = [("exact path", SM["exact"]), ("DDIM, 1 call", SM["methods"]["ddim_1"]),
            ("student, 1 call", SM["methods"]["pd_1"])]
    v = tiles_rows(96, 520, 172, 30, rows, [3, 4, 5], 270, 18)
    emit("feed", 1, "twenty-steps-into-one",
         ["Twenty steps", "into one."],
         ["A sampler walks from noise to image one network call at a time.",
          "A few-step student is trained to jump to where the walk ends."],
         v,
         ["One DDIM call returns the average of every crescent, a ring.",
          "A distilled student returns a crescent."],
         FEED_TOTAL)


def feed_02():
    h = W["halving"]
    rows = [("true denoiser at x = 40, σ = 80", f"{h['D_first']:.3f}", MUTED, False),
            (f"teacher: two DDIM steps to σ = {h['sigma_next']:.3f}", f"{h['x_two']:.3f}", MUTED, False),
            ("the student's target for one step", f"{h['target']:.3f}", ACCENT, True),
            ("after two calls: DDIM", f"{h['ddim2_end']:.3f}", MUTED, False),
            ("after two calls: a perfectly distilled student", f"{h['student_end']:.3f}", INK, True),
            ("the exact path", f"{W['rows'][1]['exact']:.3f}", INK, False)]
    v = label(96, 540, "one number between two crescents at ±" + f"{W['a']:.2f}", SOFT, "start", 16)
    y = 610
    for i, (name, val, colour, bold) in enumerate(rows):
        if i == 3:
            v += hline(96, 984, y - 44, RULE, 1)
        v += txt(96, y, name, 27, INK if bold else MUTED, SANS, 600 if bold else 400)
        v += mono(984, y, val, 30, colour, "end", 600)
        y += 84 if i != 2 else 104
    emit("feed", 2, "told-where-the-path-goes",
         ["The student is told", "where the path goes."],
         ["Progressive distillation: one student step must land where two",
          "teacher steps land. Inverting that step gives its target."],
         v,
         [f"Trained to say {h['target']:.3f} where the denoiser says {h['D_first']:.3f}, the student",
          "commits four times sooner. It is not a better denoiser."],
         FEED_TOTAL)


def feed_03():
    v, pl = cliff(110, 560, 860, 420)
    st = W["student_1d"]
    v += polyline([(110, 1076), (170, 1076)], INK, 5) + mono(184, 1083, "exact path", 21, INK)
    v += polyline([(420, 1076), (480, 1076)], ACCENT, 5) + mono(494, 1083, "a network fitted to it", 21, ACCENT)
    v += label(110, 1120, "starting noise ε, zoomed to ±0.05", SOFT, "start", 15)
    emit("feed", 3, "a-cliff-in-the-map",
         ["Where each noise ends", "is a cliff."],
         [f"Two noises 0.002 apart end on opposite crescents, ±{W['exact_pm'][0]:.2f}.",
          "A one-call student must draw that step with a smooth function."],
         v,
         [f"Fitted by least squares, it ramps from ε {st['ramp'][0]:+.3f} to {st['ramp'][1]:+.3f}".replace("-", "−"),
          f"and leaves {100 * st['share_between']:.1f}% of all noises between the crescents."],
         FEED_TOTAL)


def bars_near(x, y, w, row_h, size=26, value_size=28):
    names = [("direct regression", "regression"), ("progressive distillation", "pd"),
             ("consistency distillation", "cd"), ("shortcut model", "shortcut")]
    near_share = sum(CAP["margin_share"][:3])
    out = label(x, y, "share of each student's flips from noises near a boundary", SOFT, "start", 16)
    yy = y + 60
    for lab, key in names:
        s = flips_near(key)
        out += txt(x, yy, lab, size, INK, SANS, 400)
        out += box(x, yy + 16, w, 32, "rgba(45,49,66,0.06)", "none", 4, 0)
        out += box(x, yy + 16, w * s, 32, ACCENT, "none", 4, 0)
        out += mono(x + w + 20, yy + 42, f"{100 * s:.0f}%", value_size, ACCENT, "start", 600)
        yy += row_h
    out += txt(x, yy, "the noises themselves", size, MUTED, SANS, 400)
    out += box(x, yy + 16, w, 32, "rgba(45,49,66,0.06)", "none", 4, 0)
    out += box(x, yy + 16, w * near_share, 32, SOFT, "none", 4, 0)
    out += mono(x + w + 20, yy + 42, f"{100 * near_share:.0f}%", value_size, MUTED, "start", 600)
    return out


def feed_04():
    v = bars_near(96, 540, 700, 104)
    f, n = far_flips()
    emit("feed", 4, "errors-live-at-decisions",
         ["Errors live at", "the decisions."],
         ["4,096 noises through four one-call students. A noise is near a",
          "boundary when it leans almost equally toward two crescents."],
         v,
         [f"For the {round(100 * sum(CAP['margin_share'][5:]))}% of noises farthest from a boundary, the four",
          f"students, two seeds each, flipped {WORDS.get(f, f)} decision{'s' if f != 1 else ''} in {n:,}."],
         FEED_TOTAL)


def feed_05():
    calls = ["1", "2", "4"]
    series = [("DDIM, exact denoiser", [REF["solvers"]["ddim"][c]["swd"] for c in calls], INK),
              ("DPM-Solver++(2M), exact", [REF["solvers"]["dpmpp2m"][c]["swd"] for c in calls], MUTED),
              ("distilled student", [mean2("pd", c, "swd") for c in calls], ACCENT)]
    v = label(96, 540, "sample distance to the data · lower is better", SOFT, "start", 16)
    top = max(max(s[1]) for s in series)
    x0, base, hmax, bw, gap = 150, 1010, 380, 70, 14
    for g, c in enumerate(calls):
        gx = x0 + g * 290
        for k, (name, vals, colour) in enumerate(series):
            bh = hmax * vals[g] / top
            bx = gx + k * (bw + gap)
            v += box(bx, base - bh, bw, bh, colour, "none", 3, 0)
            v += mono(bx + bw / 2, base - bh - 14, f"{vals[g]:.3f}", 19, colour, "middle", 600)
        v += mono(gx + 1.5 * bw + gap, base + 40, f"{c} call" + ("s" if c != "1" else ""), 22, INK, "middle", 600)
    v += hline(130, 1000, base, RULE_SOLID, 1.5)
    ly = 1110
    lx = 96
    for name, vals, colour in series:
        v += box(lx, ly - 18, 22, 22, colour, "none", 3, 0) + mono(lx + 34, ly, name, 19, MUTED)
        lx += 60 + len(name) * 11.5
    emit("feed", 5, "students-beat-solvers",
         ["Below eight calls,", "a student wins."],
         ["Progressive distillation's students against two solvers at the",
          "same number of network calls. The solvers use the exact denoiser."],
         v,
         [f"At two calls: {mean2('pd', '2', 'swd'):.3f} for the student, {REF['solvers']['ddim']['2']['swd']:.3f} for DDIM.",
          f"Two independent sets of real images differ by {REF['swd_floor']:.3f}."],
         FEED_TOTAL)


def coverage_chart(x, y, w, h, run, until=4000, size=18, lw=5):
    tr = [r for r in run["trace"] if r["step"] <= until]
    pl = Plot(x, y, w, h, (0, until), (0, 1.0))
    cols = [INK, ACCENT, BLUE, SAGE]
    out = ""
    for f in (0, 0.25, 0.5, 0.75, 1.0):
        out += hline(x, x + w, pl.Y(f), RULE if f else RULE_SOLID, 1.5 if f == 0 else 1, "8,6" if f == 0.25 else None)
        out += mono(x - 14, pl.Y(f) + 7, f"{round(100 * f)}%", size, SOFT, "end")
    for k in range(4):
        out += polyline([(pl.X(r["step"]), pl.Y(r["cover"][k])) for r in tr], cols[k], lw)
    for s in range(0, until + 1, 1000):
        out += mono(pl.X(s), y + h + 34, f"{s:,}", size, SOFT, "middle")
    return out


def feed_06():
    run = ST["dmd_5to1"]["1"]
    v = coverage_chart(170, 560, 790, 400, run)
    v += label(170, 1046, "generator updates · share of samples on each of the four crescents", SOFT, "start", 15)
    v += label(170, 1074, "DMD with five fake-denoiser updates per generator update, seed 1", SOFT, "start", 15)
    emit("feed", 6, "matching-the-set-drops-a-mode",
         ["Matching the set", "can drop a mode."],
         ["Distribution matching never asks where each noise should end.",
          "In the lab, every run first put all its samples on one crescent."],
         v,
         ["With the teacher's noise-image pairs, every crescent was back above",
          "15% of the samples within 400 updates; without, after 800 to 3,100."],
         FEED_TOTAL)


def feed_07():
    items = [("Progressive distillation", "halve the steps round by round; one student per count"),
             ("Consistency models", "jump to the end; extra calls re-decide"),
             ("Distribution matching", "no pairing to keep; watch every mode"),
             ("Shortcut models, flow maps", "one network for any number of steps"),
             ("Measure both", "fidelity and coverage, not one FID")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 7, "read-the-article",
         ["Twenty steps", "into one."],
         ["Distillation, consistency models, DMD and flow maps, measured",
          "against an exact teacher in a lab you can run on a laptop."],
         v,
         ["Every few-step method learns the jump, and pays for it:",
          "in fidelity, in coverage, or in both."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    rows = [("exact path", SM["exact"]), ("DDIM, 1 call", SM["methods"]["ddim_1"]),
            ("student, 1 call", SM["methods"]["pd_1"])]
    v = tiles_rows(96, 820, 180, 36, rows, [3, 4, 5], 260, 20)
    emit("story", 1, "twenty-steps-into-one",
         ["Twenty steps", "into one."],
         ["One DDIM call returns a blur.", "A distilled student returns an image."],
         v,
         ["The student learns where the path", "from each noise ends."],
         STORY_TOTAL)


def story_02():
    v, pl = cliff(110, 840, 860, 480, 22, 6)
    st = W["student_1d"]
    v += polyline([(110, 1430), (170, 1430)], INK, 6) + mono(184, 1438, "exact path", 24, INK)
    v += polyline([(420, 1430), (480, 1430)], ACCENT, 6) + mono(494, 1438, "fitted student", 24, ACCENT)
    emit("story", 2, "a-cliff-in-the-map",
         ["Where each noise ends", "is a cliff."],
         ["Noises 0.002 apart end on", "opposite crescents."],
         v,
         [f"A smooth student strands {100 * st['share_between']:.1f}%", "of noises between the crescents."],
         STORY_TOTAL)


def story_03():
    v = bars_near(96, 860, 640, 120, 28, 30)
    emit("story", 3, "errors-live-at-decisions",
         ["Errors live at", "the decisions."],
         ["Noises near a decision boundary,", "against the students' flips."],
         v,
         [f"{100 * sum(CAP['margin_share'][:3]):.0f}% of the noises carry most", "of every student's mistakes."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["why one solver call returns a blur",
             "how progressive distillation halves steps",
             "what a consistency model learns",
             "how distribution matching drops modes",
             "one network for any step count"]
    y = 880
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 30, INK, SANS, 400)
        y += 108
    emit("story", 4, "read-the-article",
         ["Twenty steps", "into one."],
         ["Few-step diffusion, measured", "against an exact teacher."],
         v,
         ["The full article is on Canery."],
         STORY_TOTAL, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07,
            story_01, story_02, story_03, story_04]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
