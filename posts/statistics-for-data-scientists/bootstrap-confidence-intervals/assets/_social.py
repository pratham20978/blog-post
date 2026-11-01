#!/usr/bin/env python3
"""Build the finished Canery feed sources for "The Bootstrap: From Percentile to BCa, and Where It Breaks".

Statistics for Data Scientists, part 7. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 6, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks the basic interval and each card's failure, blue BCa, ink the
rest. Feed cards only: the owner asked for no Story frames (2026-10-30); the shell keeps its Story layout.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))

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
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/bootstrap-confidence-intervals"
FOOTER = "THE BOOTSTRAP · CANERY.IN"

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


def polyline(pts, stroke, sw=3, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}/>')


def dot(x, y, r, fill):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'


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
from decimal import ROUND_HALF_UP, Decimal

EX, CO, SP, MX, HV, DP = (CAP[k] for k in ("example", "coverage", "spend", "maximum", "heavy", "dependent"))
IV, CM = EX["intervals"], CO["methods"]
S30 = SP["by_n"]["30"]["methods"]
TK = MX["tanks"]
FEED_TOTAL = 8


def pc(v, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return f"{(Decimal(repr(float(v))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}%"


def r3(v):
    return f"{v:.3f}".replace("-", "−")


assert (r3(EX["r"]), r3(EX["rho"]), r3(EX["se_boot"]), r3(EX["true"]["se"]), r3(EX["se_normal_theory"])) == ("0.776", "0.760", "0.135", "0.130", "0.115")
assert EX["first_resample"]["distinct"] == 11 and r3(EX["first_resample"]["r"]) == "0.720" and EX["below"] == 4630
assert [r3(v) for v in IV["bca"]] == ["0.327", "0.942"] and [r3(v) for v in IV["basic"]] == ["0.590", "1.100"]
assert (f"{EX['z0']:.3f}", f"{EX['a']:.4f}") == ("-0.093", "-0.0757") and [pc(v, 2) for v in EX["bca_levels"]] == ["0.58%", "93.86%"]
assert [pc(CM[k]["coverage"]) for k in ("percentile", "bca", "basic", "fisher_z", "studentized")] == ["91.0%", "92.0%", "80.7%", "93.6%", "95.7%"]
assert [pc(S30[k]["coverage"]) for k in ("t", "percentile", "bca", "studentized")] == ["66.0%", "66.8%", "73.3%", "80.3%"]
assert (pc(S30["bca"]["by_flag"]["0"]), pc(S30["bca"]["by_flag"]["1"]), SP["top1_count"]) == ("64.8%", "97.0%", 44)
assert TK["boot_pmf"][-1] == 0.67232 and pc(TK["coverage"]["percentile"], 2) == "1.46%" and pc(TK["coverage"]["basic"], 2) == "75.73%"
assert (pc(DP["coverage"]), f"{DP['se_ratio_mean']:.3f}") == ("73.5%", "0.574") and pc(MX["uniform"]["by_n"]["100"]["point_mass"]) == "63.4%"
JACK6 = EX["jackknife"][EX["schools"].index(6)]
_d = [EX["jack_mean"] - j for j in EX["jackknife"]]
SHARE6 = (EX["jack_mean"] - JACK6) ** 3 / sum(v**3 for v in _d)
assert round(100 * SHARE6) == 110 and r3(JACK6) == "0.893"

STYLE = {"percentile": INK, "bca": LINK, "basic": ACCENT, "normal": SOFT, "studentized": MUTED, "studentized_z": MUTED,
         "fisher_z": INK}
NAMES = {"percentile": "percentile", "bca": "BCa", "basic": "basic", "normal": "normal, bootstrap SE",
         "studentized": "studentized", "studentized_z": "studentized, Fisher scale", "fisher_z": "Fisher z, normal theory"}


def stat_row(x, y, name, value, colour, note=None, size=56):
    """A labelled statistic: its name in mono on the left, the value large on the right."""
    out = mono(x, y, name, 24, colour, "start", 600)
    out += txt(970, y + 10, value, size, colour, SANS, 600, "end")
    if note:
        out += mono(x, y + 36, note, 19, MUTED)
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "what each condition broken did to a 95% interval", 21, MUTED, "start", 600)
    rows = (("the sample is drawn independently,", "and resampled the way it was drawn", "an AR(1) series, φ = 0.5",
             f"SE {DP['se_ratio_mean']:.3f} of the truth; covers {pc(DP['coverage'])}"),
            ("the sample stands in", "for the population", "spend at n = 30, no top-1% customer",
             f"BCa covers {pc(S30['bca']['by_flag']['0'])}"),
            ("the statistic changes smoothly", "with the distribution", "a uniform maximum",
             "percentile and BCa cover 0%"))
    y = 620
    for a, b, case, result in rows:
        v += txt(110, y, a, 26, INK, SANS, 600) + txt(110, y + 35, b, 26, INK, SANS, 600)
        v += mono(110, y + 75, case, 20, MUTED)
        v += mono(110, y + 105, result, 22, ACCENT, "start", 600)
        y += 164
    emit("feed", 1, "not-assumption-free",
         ["The bootstrap is not", "assumption-free."],
         ["It treats the sample as the population.", "Three conditions, each broken on purpose."],
         v,
         ["Break one condition and a nominal 95% interval", f"covered {pc(DP['coverage'])}, {pc(S30['bca']['by_flag']['0'])} or 0%."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "the correlation of LSAT and GPA in 15 law schools", 21, MUTED, "start", 600)
    v += mono(110, 616, "one resample: 15 rows drawn with replacement", 21, INK, "start", 600)
    rows = EX["first_resample"]["rows_lsat"]
    v += mono(110, 656, " ".join(str(r) for r in rows[:8]), 24, INK)
    v += mono(110, 692, " ".join(str(r) for r in rows[8:]), 24, INK)
    v += mono(110, 736, f"{EX['first_resample']['distinct']} distinct schools; r* = {r3(EX['first_resample']['r'])}", 21, MUTED)
    v += hline(110, 970, 770, RULE_SOLID)
    v += stat_row(110, 830, "bootstrap SE, 10,000 resamples", r3(EX["se_boot"]), LINK, None, 50)
    v += stat_row(110, 914, "true SE, 1,000,000 fresh samples", r3(EX["true"]["se"]), INK, "of 15 from all 82 schools", 50)
    v += stat_row(110, 1022, "normal-theory formula", r3(EX["se_normal_theory"]), ACCENT, "(1 − r²)/√(n − 3)", 50)
    emit("feed", 2, "one-sample-many-resamples",
         ["One sample,", "10,000 resamples."],
         ["Resample the 15 schools with replacement;", "the spread of the replicates is the SE."],
         v,
         [f"The bootstrap SE was {r3(EX['se_boot'])} against a true {r3(EX['true']['se'])};", f"the textbook formula gave {r3(EX['se_normal_theory'])}."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "95% intervals from the same 10,000 replicates", 21, MUTED, "start", 600)
    lo_, hi_ = -0.55, 1.15
    X = lambda t: 390 + (t - lo_) / (hi_ - lo_) * 400                 # names 110-375, bars 390-790, values to 970
    v += rect(X(1.0), 600, X(1.15) - X(1.0), 436, "#ececec")
    v += mono(X(1.075), 592, "above 1", 15, SOFT, "middle")
    v += line(X(EX["r"]), 600, X(EX["r"]), 1036, INK, 2)
    order = ("percentile", "bca", "basic", "normal", "studentized", "studentized_z", "fisher_z")
    for i, k in enumerate(order):
        y = 632 + i * 60
        lo, hi = IV[k]
        col = STYLE[k]
        v += mono(110, y + 6, NAMES[k], 17, col, "start", 600)
        v += line(X(max(lo, lo_)), y, X(min(hi, hi_)), y, col, 7)
        v += mono(970, y + 6, f"{r3(lo)} to {r3(hi)}", 17, col, "end", 600)
    for t in (-0.5, 0, 0.5, 1.0):
        v += mono(X(t), 1066, f"{t:g}".replace("-", "−"), 16, SOFT, "middle")
    v += mono(X(EX["r"]) + 8, 1092, f"r = {r3(EX['r'])}", 16, INK, "start", 600)
    emit("feed", 3, "seven-answers",
         ["One correlation,", "seven 95% intervals."],
         ["The same 15 schools and the same replicates,", "read seven ways."],
         v,
         ["Two of the seven reach above 1, which", "no correlation can."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "BCa: the percentile interval, re-aimed by two numbers", 21, MUTED, "start", 600)
    v += stat_row(110, 640, "bias correction z0", f"{EX['z0']:.3f}".replace("-", "−"), LINK,
                  f"{EX['below']:,} of 10,000 replicates below r", 50)
    v += stat_row(110, 760, "acceleration a", f"{EX['a']:.4f}".replace("-", "−"), LINK,
                  f"from the jackknife; school 6 is {round(100 * SHARE6)}% of Σd³", 50)
    v += hline(110, 970, 830, RULE_SOLID)
    v += mono(110, 884, "percentile levels read", 22, INK, "start", 600)
    v += mono(110, 930, f"2.5% → {pc(EX['bca_levels'][0], 2)}", 30, LINK, "start", 600)
    v += mono(560, 930, f"97.5% → {pc(EX['bca_levels'][1], 2)}", 30, LINK, "start", 600)
    v += mono(110, 1000, f"BCa: {r3(IV['bca'][0])} to {r3(IV['bca'][1])}", 28, LINK, "start", 600)
    v += mono(110, 1046, f"percentile: {r3(IV['percentile'][0])} to {r3(IV['percentile'][1])}", 24, INK)
    emit("feed", 4, "bca-in-two-numbers",
         ["BCa in", "two numbers."],
         ["A bias correction from the replicates and", "an acceleration from the jackknife."],
         v,
         ["One school of 15 set the acceleration, and", "BCa's lower limit is the replicates' 0.58% point."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, f"{CO['R']:,} fresh samples of 15 from the 82 schools", 21, MUTED, "start", 600)
    order = ("studentized", "studentized_z", "fisher_z", "bca", "percentile", "normal", "basic")
    X = lambda c: 470 + (c - 0.78) / 0.20 * 470
    v += line(X(0.78), 1036, X(0.98), 1036, RULE_SOLID, 1)               # an axis with ticks; no gridlines under the labels
    for t in (0.80, 0.85, 0.90):
        v += line(X(t), 1030, X(t), 1042, RULE_SOLID, 1)
    v += line(X(0.95), 600, X(0.95), 1036, INK, 2, "8,6")
    for t, lab in ((0.80, "80%"), (0.85, "85%"), (0.90, "90%")):
        v += mono(X(t), 1066, lab, 16, SOFT, "middle")
    v += mono(X(0.95), 1066, "95%", 17, INK, "middle", 600)
    for i, k in enumerate(order):
        y = 626 + i * 62
        c = CM[k]["coverage"]
        col = STYLE[k]
        v += mono(110, y + 7, NAMES[k], 19, col, "start", 600)
        v += dot(X(c), y, 10, col)
        right = c > 0.95                                   # labels stay on the dot's far side from the 95% line
        v += mono(X(c) + (18 if right else -18), y + 7, pc(c), 20, col, "start" if right else "end", 600)
    emit("feed", 5, "coverage-measured",
         ["95% intervals that", "covered 81% to 96%."],
         ["The 82 schools are published, so each", "interval's real coverage can be measured."],
         v,
         [f"BCa {pc(CM['bca']['coverage'])}, percentile {pc(CM['percentile']['coverage'])}, basic {pc(CM['basic']['coverage'])}; the studentized", f"{pc(CM['studentized']['coverage'])} only by reaching past 1 in {pc(CM['studentized']['upper_above_1'])} of samples."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "95% intervals for mean customer spend, n = 30", 21, MUTED, "start", 600)
    v += mono(110, 616, "interval", 19, SOFT) + mono(650, 616, "all", 19, SOFT, "end")
    v += mono(820, 616, "no top-1%", 19, SOFT, "end") + mono(970, 616, "with top-1%", 19, SOFT, "end")
    for i, (k, name, col) in enumerate((("t", "t-interval", INK), ("percentile", "percentile", INK),
                                        ("bca", "BCa", LINK), ("studentized", "bootstrap-t", MUTED))):
        y = 676 + i * 62
        m = S30[k]
        v += mono(110, y, name, 26, col, "start", 600)
        v += mono(650, y, pc(m["coverage"]), 26, col, "end", 600)
        v += mono(820, y, pc(m["by_flag"]["0"]), 26, ACCENT, "end", 600)
        v += mono(970, y, pc(m["by_flag"]["1"]), 26, col, "end")
    v += hline(110, 970, 940, RULE_SOLID)
    v += mono(110, 990, f"top 1%: the {SP['top1_count']} customers who spent £{SP['top1_threshold']:,.0f} or more,", 19, SOFT)
    v += mono(110, 1018, "29.9% of all spending; 73.5% of samples of 30 hold none", 19, SOFT)
    emit("feed", 6, "missing-tail",
         ["The bootstrap cannot", "resample what is missing."],
         ["Skewed spend: most samples of 30 hold none", "of the few customers who set the mean."],
         v,
         [f"BCa lifts coverage from {pc(S30['t']['coverage'])} to {pc(S30['bca']['coverage'])}; no interval adds", "customers the sample never caught."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "the largest of five tank serials, bootstrapped exactly", 21, MUTED, "start", 600)
    for i, (sv, p) in enumerate(zip(TK["serials"], TK["boot_pmf"])):
        y = 620 + i * 52
        col = ACCENT if sv == 303 else INK
        v += mono(110, y + 7, str(sv), 24, col, "start", 600)
        v += rect(210, y - 14, max(p, 0.004) * 600, 28, col, op=0.8)
        v += mono(220 + max(p, 0.004) * 600, y + 7, f"{p:.4f}", 20, col, "start", 600)
    v += hline(110, 970, 896, RULE_SOLID)
    for i, (name, iv, cov, col) in enumerate((("percentile", TK["percentile"], pc(TK["coverage"]["percentile"], 2), INK),
                                               ("basic", TK["basic"], pc(TK["coverage"]["basic"], 2), ACCENT),
                                               ("exact", TK["exact_one_sided"], "at least 95%", LINK))):
        y = 944 + i * 48
        v += mono(110, y, name, 22, col, "start", 600)
        v += mono(420, y, f"{iv[0]} to {iv[1]}", 22, col)
        v += mono(970, y, cov, 22, col, "end", 600)
    v += mono(970, 914, "covers N = 342", 17, SOFT, "end")
    emit("feed", 7, "the-maximum",
         ["Bootstrap a maximum", "and 67% sits on one value."],
         ["Five serials, the largest 303, the truth 342.", "No resample can exceed 303."],
         v,
         ["Percentile and BCa intervals cover N only if", "tank 342 itself was caught: 1.46% of captures."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("seven intervals, by hand", f"BCa: z0 {EX['z0']:.3f}, a {EX['a']:.4f} → {r3(IV['bca'][0])} to {r3(IV['bca'][1])}".replace("-", "−"), LINK),
             ("coverage, measured on the 82 schools", f"percentile {pc(CM['percentile']['coverage'])}, BCa {pc(CM['bca']['coverage'])}, basic {pc(CM['basic']['coverage'])}", INK),
             ("the skewed mean of part 6", f"t {pc(S30['t']['coverage'])} → BCa {pc(S30['bca']['coverage'])} → bootstrap-t {pc(S30['studentized']['coverage'])}", INK),
             ("where it breaks", "the maximum, infinite variance, dependence", ACCENT)]
    y = 556
    for head, a, colour in items:
        v += txt(110, y, head, 30, colour, SANS, 600)
        v += mono(110, y + 42, a, 21, INK if colour == INK else colour)
        y += 136
    emit("feed", 8, "read-the-article",
         ["The bootstrap:", "what it assumes."],
         ["Every interval computed by hand, matched to", "SciPy and R, and measured by a seeded lab."],
         v,
         ["The full walk-through, with the lab and every", "simulated number's Monte Carlo error."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
