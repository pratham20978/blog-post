#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Confidence Intervals: What 95% Means, Measured".

Statistics for Data Scientists, part 6. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 5, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, or the trial's published table in ../lab/data, and the
asserts below hold each one to the article. Colours follow the figures: tangerine marks the Wald interval and
each card's warning, blue the Clopper-Pearson interval, ink the rest. Feed cards only: the owner asked for no
Story frames (2026-10-30); the shell keeps its Story layout for parts that want one.

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
CANONICAL = "canery.in/blogs/confidence-intervals-coverage"
FOOTER = "CONFIDENCE INTERVALS · CANERY.IN"

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
EN, CV, PF, OV, TC = (CAP[k] for k in ("enumerate", "coverage", "pfizer", "overlap", "tcoverage"))
M = EN["methods"]
N50, W01 = CV["n50"], CV["wald_vs_n"]["0.1"]
PR, SV = PF["primary"]["methods"], PF["severe"]
TB, DEC = TC["by_n"], TC["deciles"]["30"]["coverage"]
CRED = [r for r in PF["rows"] if r["interval"] == "credible" and r["endpoint"].endswith("no_prior_infection")][0]
assert (round(M["wald"]["coverage"], 4), round(M["wilson"]["coverage"], 4), round(M["clopper_pearson"]["coverage"], 4)) == (0.876, 0.9568, 0.9887)
assert [round(v, 4) for v in EN["pmf"][:7]] == [0.1216, 0.2702, 0.2852, 0.1901, 0.0898, 0.0319, 0.0089]
assert (round(W01["at"]["29"], 3), round(W01["at"]["30"], 3), round(W01["at"]["50"], 3)) == (0.947, 0.809, 0.879)
assert [round(100 * v, 1) for v in PR["clopper_pearson"]["ve"]] == [90.0, 97.9] and [round(100 * v, 1) for v in PR["wald"]["ve"]] == [91.4, 98.4]
assert CRED["published"][1:] == [90.3, 97.6] and PF["summary"] == {"confidence_rows": 16, "match_printed": 9, "within_rounding": 16}
assert [round(v, 4) for v in PR["clopper_pearson"]["share"]] == [0.0205, 0.0906]
assert round(SV["p_two_sided"], 3) == 0.021 and [round(100 * v, 1) for v in SV["ve_ci"]] == [20.1, 99.7]
assert round(OV["alpha_at"]["1"], 4) == 0.0056 and round(OV["power_at_design80"]["overlap95"], 2) == 0.51
assert (round(100 * TB["30"]["coverage"], 1), round(100 * TB["30"]["miss_below"], 1), round(TC["population"]["skewness"], 1)) == (65.8, 34.2, 21.6)
assert DEC[0] == 0.0 and round(100 * TB["1000"]["coverage"], 2) == 85.65 and round(100 * TB["10000"]["coverage"], 1) == 93.8
assert round(N50["clopper_pearson"]["min"], 4) == 0.9508 and round(N50["wilson"]["min"], 3) == 0.839 and round(N50["wald"]["mean"], 3) == 0.901
FEED_TOTAL = 8


def pc(v, nd=1):
    return f"{100 * v:.{nd}f}%"


def stat_row(x, y, name, value, colour, note=None, size=56):
    """A labelled statistic: its name in mono on the left, the value large on the right."""
    out = mono(x, y, name, 24, colour, "start", 600)
    out += txt(970, y + 10, value, size, colour, SANS, 600, "end")
    if note:
        out += mono(x, y + 36, note, 19, MUTED)
    return out


def ve_axis(x0, w, lo=88.0, hi=99.0):
    return lambda v: x0 + (v - lo) / (hi - lo) * w


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "BNT162b2 trial: 8 of 170 cases in the vaccine group", 21, MUTED, "start", 600)
    X = ve_axis(150, 640)
    v += line(X(88), 868, X(98), 868, RULE_SOLID, 1)
    for t in (88, 90, 92, 94, 96, 98):
        v += line(X(t), 862, X(t), 874, RULE_SOLID, 1)
        v += mono(X(t), 900, f"{t}%", 18, SOFT, "middle")
    v += line(X(95.0), 600, X(95.0), 870, INK, 2, "4,5")
    v += mono(X(95.0), 594, "efficacy 95.0%", 18, INK, "middle")
    ci = [100 * x for x in PR["clopper_pearson"]["ve"]]
    v += mono(110, 668, "confidence interval, Table 3", 21, LINK, "start", 600)
    v += line(X(ci[0]), 700, X(ci[1]), 700, LINK, 8)
    v += mono(X(ci[1]) + 12, 707, f"{ci[0]:.1f} to {ci[1]:.1f}", 20, LINK, "start", 600)
    v += mono(110, 788, "credible interval, Table 2", 21, MUTED, "start", 600)
    v += line(X(CRED["published"][1]), 820, X(CRED["published"][2]), 820, MUTED, 8, "14,8")
    v += mono(X(CRED["published"][2]) + 12, 827, f"{CRED['published'][1]:.1f} to {CRED['published'][2]:.1f}", 20, MUTED, "start", 600)
    v += mono(110, 960, "confidence: the procedure contains the true efficacy", 19, LINK)
    v += mono(110, 988, "in at least 95% of repetitions", 19, LINK)
    v += mono(110, 1036, "credible: given the prior, a 97.5% probability that", 19, MUTED)
    v += mono(110, 1064, "efficacy is at least 90.3%, as the FDA read it", 19, MUTED)
    emit("feed", 1, "two-intervals",
         ["A 95% interval is not", "a 95% chance."],
         ["One vaccine trial printed two 95% intervals", "for the same 95.0% efficacy."],
         v,
         ["The 95% belongs to the procedure; a probability", "for your interval needs a prior."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "20 audits, true error rate 10%: does the interval contain 0.1?", 21, MUTED, "start", 600)
    cols = (("Wald", "wald", 560), ("Wilson", "wilson", 700), ("Clopper–P.", "clopper_pearson", 860))
    v += mono(110, 612, "errors", 19, SOFT) + mono(330, 612, "P(X)", 19, SOFT, "end")
    for name, _key, x in cols:
        v += mono(x, 612, name, 19, SOFT, "middle")
    for i in range(7):
        y = 656 + i * 46
        v += mono(110, y, f"X = {i}", 22, INK, "start", 600)
        v += mono(330, y, f"{EN['pmf'][i]:.4f}", 22, INK, "end")
        for _name, key, x in cols:
            ok = M[key]["contains"][i]
            v += mono(x, y, "yes" if ok else "no", 22, INK if ok else ACCENT, "middle", 600 if not ok else 400)
    y = 656 + 7 * 46 + 18
    v += hline(110, 970, y - 30, RULE_SOLID)
    v += mono(110, y, "coverage", 22, INK, "start", 600)
    for _name, key, x in cols:
        col = ACCENT if key == "wald" else LINK if key == "clopper_pearson" else INK
        v += mono(x, y, pc(M[key]["coverage"]), 24, col, "middle", 600)
    v += mono(110, 1086, "X = 7 or more: probability 0.0024, every interval misses", 18, SOFT)
    emit("feed", 2, "coverage-is-a-sum",
         ["Coverage is a sum", "over outcomes."],
         ["Add the probabilities of the counts whose", "interval contains the truth. Nothing simulated."],
         v,
         ["A 95% Wald interval covers 87.6% here; the", "zero-error audit alone costs 12.2 points."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "exact coverage of the 95% Wald interval, true proportion 0.1", 21, MUTED, "start", 600)
    ns, wc = W01["n"], W01["wald"]
    x0, x1, y0, y1 = 130, 950, 600, 900
    X = lambda n: x0 + (n - 10) / 90 * (x1 - x0)
    Y = lambda c: y1 - (c - 0.60) / 0.40 * (y1 - y0)
    for c in (0.6, 0.7, 0.8, 0.9, 1.0):
        v += line(x0, Y(c), x1, Y(c), RULE, 1)
        v += mono(x0 - 10, Y(c) + 6, f"{100 * c:.0f}%", 17, SOFT, "end")
    v += line(x0, Y(0.95), x1, Y(0.95), SOFT, 2, "6,6")
    pts = [(X(n), Y(c)) for n, c in zip(ns, wc) if n <= 100]
    v += polyline(pts, ACCENT, 3)
    for n_, dx, dy, anc in (("29", 14, -16, "start"), ("30", 14, 26, "start"), ("50", 14, 30, "start")):
        c = W01["at"][n_]
        v += dot(X(int(n_)), Y(c), 7, ACCENT)
        v += mono(X(int(n_)) + dx, Y(c) + dy, f"n = {n_}: {pc(c)}", 22, ACCENT, anc, 600)
    for n_ in (10, 30, 50, 70, 100):
        v += mono(X(n_), 934, str(n_), 17, SOFT, "middle")
    v += mono(x1, 962, "number of trials n", 17, SOFT, "end")
    v += mono(110, 1044, "n = 50 meets the rule of thumb np ≥ 5, and covers 87.9%;", 18, SOFT)
    v += mono(110, 1072, "each step in n changes which counts' intervals contain 0.1", 18, SOFT)
    emit("feed", 3, "one-more-trial",
         ["One more trial,", "14 points less coverage."],
         ["The Wald interval's coverage zigzags as n", "grows, at a true proportion of 0.1."],
         v,
         ["np ≥ 5 is not a guarantee: at n = 50, where", "np = 5, the Wald interval covers 87.9%."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "five 95% intervals at n = 50, exact over every p", 21, MUTED, "start", 600)
    v += mono(110, 616, "interval", 19, SOFT) + mono(640, 616, "lowest", 19, SOFT, "end")
    v += mono(800, 616, "mean", 19, SOFT, "end") + mono(970, 616, "width", 19, SOFT, "end")
    rows = (("Wald", "wald", ACCENT), ("Wilson", "wilson", INK), ("Agresti–Coull", "agresti_coull", INK),
            ("Clopper–Pearson", "clopper_pearson", LINK), ("Jeffreys", "jeffreys", INK))
    for i, (name, key, col) in enumerate(rows):
        y = 676 + i * 64
        s = N50[key]
        low = "near 0" if s["min"] < 0.5 else pc(s["min"], 2)
        v += mono(110, y, name, 26, col, "start", 600)
        v += mono(640, y, low, 26, col, "end", 600)
        v += mono(800, y, pc(s["mean"]), 26, col, "end")
        v += mono(970, y, f"{s['width_vs_wilson']:.2f}×", 26, col, "end")
    v += mono(110, 1016, "lowest: the smallest coverage at any p; mean: over a uniform p;", 18, SOFT)
    v += mono(110, 1044, "width: as a multiple of Wilson's. statsmodels' proportion_confint", 18, SOFT)
    v += mono(110, 1072, "defaults to the Wald interval", 18, ACCENT)
    emit("feed", 4, "pick-the-interval",
         ["Pick the interval,", "not the default."],
         ["Only one of the five never falls below 95%,", "and it pays for that in width."],
         v,
         ["Wilson or Jeffreys for small n, Agresti–Coull", "for larger; Clopper–Pearson when 95% is a floor."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "BNT162b2, the primary endpoint, recomputed", 21, MUTED, "start", 600)
    sh = PR["clopper_pearson"]["share"]
    ci = [100 * x for x in PR["clopper_pearson"]["ve"]]
    steps = (("cases in the vaccine group", "8 of 170", INK),
             ("Clopper–Pearson for that share", f"{sh[0]:.4f} to {sh[1]:.4f}", LINK),
             ("mapped to efficacy, 1 − IRR", f"{ci[0]:.1f}% to {ci[1]:.1f}%", LINK))
    y = 640
    for name, val, col in steps:
        v += mono(110, y, name, 22, MUTED)
        v += txt(970, y + 4, val, 34, col, SANS, 600, "end")
        y += 78
    v += hline(110, 970, y - 34, RULE_SOLID)
    v += mono(110, y + 10, "= the paper's Table 3, to the digit", 22, LINK, "start", 600)
    v += mono(110, y + 52, "16 published rows: 9 match every digit, 7 lie within", 20, INK)
    v += mono(110, y + 80, "the rounding of the surveillance times", 20, INK)
    w = [100 * x for x in PR["wald"]["ve"]]
    v += mono(110, 1072, f"the Wald interval on the same split: {w[0]:.1f}% to {w[1]:.1f}%", 18, ACCENT)
    emit("feed", 5, "trial-reproduced",
         ["A vaccine trial's", "interval, reproduced."],
         ["Given the total, the vaccine group's cases", "are binomial: an exact interval, then a map."],
         v,
         ["A published interval should reproduce from", "its counts; this one does, to the digit."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "severe Covid-19 after dose 1: 1 case against 9", 21, MUTED, "start", 600)
    arms = SV["arms"]
    X = lambda r: 150 + r / 4.6 * 660
    v += rect(X(SV["overlap"][0]), 600, X(SV["overlap"][1]) - X(SV["overlap"][0]), 150, ACCENT, op=0.16)
    for i, (k, col) in enumerate((("vaccine", LINK), ("placebo", INK))):
        a = arms[k]
        y = 640 + i * 74
        v += line(X(a["lower"]), y, X(a["upper"]), y, col, 8)
        v += dot(X(a["rate"]), y, 9, col)
        v += mono(X(a["upper"]) + 14, y + 7, f"{k} {a['rate']:.2f}", 20, col, "start", 600)
    for t in (0, 1, 2, 3, 4):
        v += mono(X(t), 784, str(t), 17, SOFT, "middle")
    v += mono(110, 812, "cases per 1,000 person-years, exact 95% intervals; shaded: overlap", 17, SOFT)
    v += stat_row(110, 880, "difference: exact test", f"p = {SV['p_two_sided']:.3f}", ACCENT,
                  f"efficacy {100 * SV['ve_ci'][0]:.1f}% to {100 * SV['ve_ci'][1]:.1f}%, excluding zero", 44)
    v += stat_row(110, 994, "\"no overlap\" read as a test", pc(OV["alpha_at"]["1"], 2), INK,
                  f"equal standard errors; power {pc(OV['power_at_design80']['overlap95'], 0)} where the test has 80%", 44)
    emit("feed", 6, "overlap-is-not-a-test",
         ["Overlapping intervals,", "a significant difference."],
         ["Two arms' 95% intervals can overlap while", "the difference between them is significant."],
         v,
         ["Test the difference itself: overlap of two", "95% intervals is not a 5% test."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "95% t-interval for mean spend, 4,317 customers, n = 30", 21, MUTED, "start", 600)
    v += stat_row(110, 640, "covers the true mean", pc(TB["30"]["coverage"]), ACCENT, f"of {TB['30']['R']:,} samples", 50)
    v += stat_row(110, 750, "lies wholly below the mean", pc(TB["30"]["miss_below"]), ACCENT, "above it: 1 in 200,000", 50)
    x0, base, bw = 130, 1010, 72
    v += mono(110, 856, "coverage by tenth of interval width, narrowest first", 19, INK, "start", 600)
    for i, c in enumerate(DEC):
        h = c * 110
        v += rect(x0 + i * (bw + 12), base - h, bw, h, ACCENT, op=0.85)
        inside = c >= 0.5                                     # tall bars carry their value inside, clear of the 95% line
        v += mono(x0 + i * (bw + 12) + bw / 2, base - h + 26 if inside else base - h - 8, f"{100 * c:.0f}", 17,
                  "#ffffff" if inside else ACCENT, "middle", 600)
    v += line(x0 - 6, base, x0 + 10 * (bw + 12) - 6, base, MUTED, 2)
    v += line(x0 - 6, base - 0.95 * 110, x0 + 10 * (bw + 12) - 6, base - 0.95 * 110, INK, 2, "8,6")
    v += mono(x0 - 12, base - 0.95 * 110 + 6, "95%", 17, INK, "end", 600)
    v += mono(110, 1072, f"skewness {TC['population']['skewness']:.1f}; at n = 1,000 coverage is still {pc(TB['1000']['coverage'], 2)}", 18, SOFT)
    emit("feed", 7, "t-interval-on-skewed-data",
         ["A 95% t-interval", "that covers 66%."],
         ["Real customer spend is so skewed that", "a sample of 30 usually misses the big spenders."],
         v,
         ["On skewed data the narrow intervals are the", "ones that miss: none of the narrowest tenth covers."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("coverage, summed exactly", f"20 audits at p = 0.1: Wald {pc(M['wald']['coverage'])}, Wilson {pc(M['wilson']['coverage'])}", INK),
             ("which interval for a proportion", f"Clopper–Pearson never below {pc(N50['clopper_pearson']['min'], 2)} at n = 50", LINK),
             ("a vaccine trial and overlapping intervals", f"90.0% to 97.9% reproduced; no overlap is a {pc(OV['alpha_at']['1'], 2)} test", INK),
             ("the t-interval on skewed data", f"customer spend at n = 30: {pc(TB['30']['coverage'])} coverage", ACCENT)]
    y = 556
    for head, a, colour in items:
        v += txt(110, y, head, 30, colour, SANS, 600)
        v += mono(110, y + 42, a, 21, INK if colour == INK else colour)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Confidence intervals:", "what 95% means."],
         ["Every number computed exactly or measured by", "a seeded lab you can rerun in 20 seconds."],
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
