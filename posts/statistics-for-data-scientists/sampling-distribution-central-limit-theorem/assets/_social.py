#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "The Sampling Distribution: The CLT and Where n = 30
Fails".

Statistics for Data Scientists, part 2. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 1, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks the failure each card is about (the lower tail, the spend), blue
the comparison, ink the reference.

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
CANONICAL = "canery.in/blogs/sampling-distribution-central-limit-theorem"
FOOTER = "THE SAMPLING DISTRIBUTION · CANERY.IN"

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
P, SA, SK, ST, BE, HV = (CAP[k] for k in ("population", "sampling", "skewness", "student", "berry", "heavy"))
B = SA["by_n"]
MU, SD, G = P["mean"], P["sd"], P["skewness"]
TP = B["30"]["top1"]
EXP = SK["populations"]["exponential"]["by_n"]
LOGN = SK["populations"]["lognormal_sigma1"]["by_n"]
NORM = SK["populations"]["normal"]["by_n"]
SP, EB = BE["spend"], BE["exponential"]
PT = HV["pareto15_ttest"]
assert round(100 * B["30"]["lower"]["p"], 1) == 39.8 and round(100 * B["30"]["upper"]["p"], 2) == 0.05
assert round(100 * B["1000"]["lower"]["p"], 1) == 17.7 and round(100 * B["10000"]["lower"]["p"], 1) == 7.9
assert round(MU, 2) == 1925.71 and round(P["median"], 2) == 658.26 and round(G, 1) == 21.6
assert round(100 * P["share_below_mean"], 1) == 79.1 and round(100 * P["top1"]["share_of_spend"], 1) == 29.7
assert round(B["30"]["s_over_sigma_quantiles"]["q50"], 3) == 0.256 and round(B["30"]["corr_mean_sd"], 3) == 0.972
assert SP["n_good"] == 20652 and SP["n_guaranteed"] == 1025322 and EB["n_good"] == 177
assert round(100 * PT["10000"]["lower"]["p"], 1) == 26.4
FEED_TOTAL, STORY_TOTAL = 8, 4


def pc(p, d=1):
    return f"{100 * p:.{d}f}%"


def gbp(v):
    return f"£{v:,.0f}"


def big(x, y, value, sub, colour, size=72, sub_size=19):
    """A large number with its label below, spaced by the number's size so the text boxes never meet."""
    return txt(x, y, value, size, colour, SANS, 600) + mono(x, y + max(40, int(size * 0.6)), sub, sub_size, colour)


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "a 5% t-test of the true mean, n = 30 customers", 20, MUTED, "start", 600)
    v += big(110, 660, pc(B["30"]["lower"]["p"]), "lower tail: rejects a true mean", ACCENT, 84)
    v += big(560, 660, pc(B["30"]["upper"]["p"], 2), "upper tail", LINK, 84)
    v += hline(110, 970, 760)
    v += mono(110, 812, "each test is built to reject 5% of the time", 20, INK, "start", 600)
    for i, n in enumerate(("1000", "10000")):
        y = 870 + 52 * i
        v += mono(110, y, f"n = {int(n):,}:", 21, SOFT)
        v += mono(330, y, f"lower {pc(B[n]['lower']['p'])}", 22, ACCENT, "start", 600)
        v += mono(640, y, f"upper {pc(B[n]['upper']['p'])}", 22, LINK, "start", 600)
    v += mono(110, 1010, f"R = {B['30']['R']:,} samples per n, MCSE at most 0.16 points", 17, SOFT)
    v += mono(110, 1046, f"4,317 real customers' net spend, skewness {G:.1f}", 17, SOFT)
    emit("feed", 1, "n-30-is-not-a-theorem",
         ["n = 30 is a rule of thumb,", "not a theorem."],
         ["A t-test on real customer spend, with the", "true mean as the null it should keep."],
         v,
         ["The central limit theorem is a limit.", "It never promised a sample size."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "net spend of 4,317 customers, Dec 2010 to Dec 2011", 20, MUTED, "start", 600)
    v += big(110, 664, gbp(P["median"]), "median customer", INK)
    v += big(560, 664, gbp(MU), "mean", INK)
    v += hline(110, 970, 760)
    w = 860
    top = P["top1"]["share_of_spend"]
    v += mono(110, 812, "share of all spend held by the top 1% (43 customers)", 19, MUTED)
    v += rect(110, 836, w, 44, LINK, LINK, 1, op=0.18)
    v += rect(110, 836, w * top, 44, ACCENT, ACCENT, 1, op=0.85)
    v += mono(110 + w * top + 14, 866, pc(top), 24, ACCENT, "start", 600)
    v += mono(110, 940, f"{pc(P['share_below_mean'])} of customers spend less than the mean", 20, INK, "start", 600)
    v += mono(110, 984, f"largest {gbp(P['max'])}: {P['max_in_sds']:.1f} SDs above the mean", 19, MUTED)
    v += mono(110, 1046, f"skewness {G:.1f}; UCI Online Retail, CC BY 4.0", 17, SOFT)
    emit("feed", 2, "a-few-whales",
         ["A few whales,", "many minnows."],
         ["Revenue per customer is the kind of number", "people average and test every day."],
         v,
         ["Most customers sit below the mean.", "That is where the trouble starts."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    r = B["30"]
    est = r["s_over_sigma_quantiles"]["q50"] * SD / math.sqrt(30)
    rows = [("σ", "one customer's spread", SD, INK), ("σ/√30", "true standard error of a mean of 30", r["se_theory"], LINK),
            ("s/√30", "what a typical sample estimates", est, ACCENT)]
    y = 566
    for sym, what, val, col in rows:
        v += mono(110, y, sym, 26, col, "start", 600)
        v += mono(280, y, what, 19, MUTED)
        v += mono(970, y, gbp(val), 30, col, "end", 600)
        v += rect(110, y + 18, 860 * math.log10(val) / math.log10(SD), 14, col, op=0.35 if col != ACCENT else 0.85)
        y += 118
    v += mono(110, 950, "bar length: log of the amount, £1 to σ", 16, SOFT)
    v += mono(110, 1000, f"s < σ in {pc(r['p_s_below_sigma']['p'])} of samples of 30", 20, INK, "start", 600)
    v += mono(110, 1040, f"yet s² averages {r['mean_s2_over_sigma2']:.3f} × σ²: unbiased, not typical", 18, MUTED)
    emit("feed", 3, "sd-is-not-se",
         ["The SD is not the SE,", "and its estimate runs small."],
         ["Spread of customers, spread of means, and", "what a t-test actually divides by."],
         v,
         ["The typical estimate is a quarter", "of the true standard error."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    none = 1 - TP["p_sample_has_one"]["p"]
    v += txt(110, 566, pc(none), 56, ACCENT, SANS, 600)
    v += mono(110, 604, "of samples of 30 miss the", 18, ACCENT)
    v += mono(110, 630, "43 biggest customers", 18, ACCENT)
    v += mono(110, 690, f"mean below μ: {pc(TP['p_below_mu_given_none']['p'])}", 20, INK, "start", 600)
    v += mono(110, 726, "s small, from the same", 18, MUTED)
    v += mono(110, 752, "small values", 18, MUTED)
    v += mono(110, 810, f"rejected: {pc(TP['lower_given_none']['p'])}", 24, ACCENT, "start", 600)
    v += txt(560, 566, pc(TP["p_sample_has_one"]["p"]), 56, LINK, SANS, 600)
    v += mono(560, 604, "hold one of them", 18, LINK)
    v += mono(560, 690, "mean lifted, s inflated", 20, INK, "start", 600)
    v += mono(560, 726, "far more, so t stays", 18, MUTED)
    v += mono(560, 752, "small", 18, MUTED)
    v += mono(560, 810, f"rejected: {int(TP['lower_given_one']['p'] * TP['lower_given_one']['R'])} of "
                        f"{TP['lower_given_one']['R']:,}", 24, LINK, "start", 600)
    v += hline(110, 970, 860)
    v += mono(110, 916, f"correlation of sample mean and SD: {B['30']['corr_mean_sd']:.3f}", 22, INK, "start", 600)
    v += mono(110, 960, "t = (mean − μ) / (s/√n): a low mean over a small s", 18, MUTED)
    v += mono(110, 990, "is a very negative t", 18, MUTED)
    v += mono(110, 1046, f"n = 30, R = {B['30']['R']:,} samples", 17, SOFT)
    emit("feed", 4, "why-one-tail-fires",
         ["Why one tail fires", "and the other almost never."],
         ["Count the big customers in each sample", "of 30."],
         v,
         ["The mean and the SD fall together,", "so the t statistic is skewed too."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "one-sided 5% t-test at n = 30: lower / upper tail", 20, MUTED, "start", 600)
    rows = [("normal", 0.0, NORM["30"], INK), ("exponential", 2.0, EXP["30"], INK),
            ("standard lognormal", SK["populations"]["lognormal_sigma1"]["skewness"], LOGN["30"], INK),
            ("customer spend", G, B["30"], ACCENT)]
    y = 620
    v += mono(560, y - 40 + 8, "γ", 18, SOFT, "end")
    for name, g, r, col in rows:
        v += mono(110, y, name, 22, col, "start", 600 if col == ACCENT else 400)
        v += mono(560, y, f"{g:.2f}", 22, col, "end")
        v += mono(970, y, f"{pc(r['lower']['p'], 2)} / {pc(r['upper']['p'], 2)}", 22, col, "end", 600)
        y += 52
    v += hline(110, 970, 846)
    c = SK["edgeworth_coefficient"]
    v += mono(110, 900, f"lower tail ≈ 5% + {100 * c:.2f} points × γ/√n", 24, INK, "start", 600)
    v += mono(110, 944, "so within 10% of 5% needs n ≥ 486 γ²:", 19, MUTED)
    v += mono(110, 976, f"exponential {SK['populations']['exponential']['n_needed']['one_sided_within_10pct']:,.0f}, "
                        f"spend {SA['population']['n_needed']['one_sided_within_10pct']:,.0f} or more", 19, MUTED)
    v += mono(110, 1046, "first-order Edgeworth term, checked by simulation", 17, SOFT)
    emit("feed", 5, "skewness-sets-the-pace",
         ["Skewness sets the pace,", "not n = 30."],
         ["The same test on populations of known", "skewness, R = 100,000 each."],
         v,
         ["n = 30 keeps a one-sided test within", "10% of 5% only if γ is below 0.25."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "largest gap to the normal CDF falls to 0.01 at", 20, MUTED, "start", 600)
    v += big(110, 664, f"{SP['n_good']:,}", "customers: the exact distance", ACCENT, 64)
    v += big(110, 800, f"{SP['n_guaranteed']:,}", "guaranteed by Berry–Esseen", INK, 64)
    v += hline(110, 970, 880)
    v += mono(110, 934, f"bound = {BE['C0_upper']} × β₃ / √n, β₃ = {SP['beta3']:.2f}", 21, INK, "start", 600)
    v += mono(110, 976, f"exponential: {EB['n_good']} exact, {EB['n_guaranteed']:,} guaranteed", 19, MUTED)
    v += mono(110, 1046, "exact distance by inverting the characteristic function", 17, SOFT)
    emit("feed", 6, "guaranteed-vs-good-enough",
         ["A guarantee is too slow", "to plan with."],
         ["The Berry–Esseen bound against the exact", "distance for the same spend data."],
         v,
         [f"The guarantee arrives {SP['n_guaranteed'] / SP['n_good']:.0f} times later", "than the normal shape does."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    iq = HV["cauchy_mean_iqr"]
    v += txt(110, 566, "Cauchy", 30, INK, SANS, 600)
    v += mono(110, 604, "spread (IQR) of the mean of n draws", 18, MUTED)
    for i, n in enumerate(("1", "10", "100", "1000")):
        v += mono(110 + 215 * i, 660, f"n = {int(n):,}", 18, SOFT)
        v += mono(110 + 215 * i, 700, f"{iq[n]['iqr']:.2f}", 30, INK, "start", 600)
    v += hline(110, 970, 750)
    v += txt(110, 806, "Pareto, tail index 1.5", 30, ACCENT, SANS, 600)
    v += mono(110, 844, "one-sided 5% t-test, lower tail", 18, MUTED)
    for i, n in enumerate(("10", "1000", "10000", "100000")):
        v += mono(110 + 215 * i, 900, f"n = {int(n):,}", 18, SOFT)
        v += mono(110 + 215 * i, 940, pc(PT[n]["lower"]["p"]), 30, ACCENT, "start", 600)
    v += mono(110, 1010, "the mean exists; the variance does not", 19, INK, "start", 600)
    v += mono(110, 1046, "lab simulation; Cauchy R = 20,000, Pareto R = 20,000 (2,000 at n = 100,000)", 16, SOFT)
    emit("feed", 7, "no-n-is-enough",
         ["Infinite variance:", "no n is enough."],
         ["The CLT needs a finite variance.", "Take it away and the normal never comes."],
         v,
         ["Averaging a Cauchy gains nothing; a Pareto", "t-test stalls near 26%."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("sampling distribution", "a statistic is a random variable", f"SE = σ/√n = {gbp(B['30']['se_theory'])} at n = 30"),
             ("Student's t", "corrects for estimating σ, not for skew", f"1.96 with an estimated σ: {pc(ST['p_abs_t9_beyond_z975'], 2)} at n = 10"),
             ("the pace", "error ≈ 0.110 γ/√n", f"spend: {pc(B['30']['lower']['p'])} at n = 30"),
             ("Monte Carlo error", "every simulated rate ± its MCSE", "√(p(1 − p)/R)")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "the pace" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["The sampling", "distribution."],
         ["Every number measured by a seeded lab", "you can rerun in under four minutes."],
         v,
         ["The full walk-through, with the lab", "and every number's Monte Carlo error."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 870, "5% t-test of the true mean, n = 30", 24, MUTED, "start", 600)
    v += txt(110, 1010, pc(B["30"]["lower"]["p"]), 120, ACCENT, SANS, 600)
    v += mono(110, 1074, "lower tail: false alarms", 26, ACCENT)
    v += txt(110, 1230, pc(B["30"]["upper"]["p"], 2), 96, LINK, SANS, 600)
    v += mono(110, 1290, "upper tail", 26, LINK)
    v += mono(110, 1372, "real spend of 4,317 customers", 22, SOFT)
    emit("story", 1, "n-30-is-not-a-theorem",
         ["n = 30 is not", "a theorem."],
         ["Each tail is built to fire", "5% of the time."],
         v,
         ["Skewness, not 30, sets", "the sample size you need."],
         STORY_TOTAL)


def story_02():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    r = B["30"]
    est = r["s_over_sigma_quantiles"]["q50"] * SD / math.sqrt(30)
    rows = [("σ", "one customer", SD, INK), ("σ/√30", "true SE", r["se_theory"], LINK), ("s/√30", "typical estimate", est, ACCENT)]
    y = 900
    for sym, what, val, col in rows:
        v += mono(110, y, sym, 34, col, "start", 600)
        v += mono(110, y + 44, what, 24, MUTED)
        v += mono(970, y + 20, gbp(val), 52, col, "end", 600)
        y += 170
    emit("story", 2, "sd-is-not-se",
         ["The SD is not", "the SE."],
         ["And the SE a sample estimates", "is usually far too small."],
         v,
         [f"s < σ in {pc(r['p_s_below_sigma']['p'])} of", "samples of 30."],
         STORY_TOTAL)


def story_03():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    c = SK["edgeworth_coefficient"]
    v += mono(110, 880, "one-sided error at n = 30", 26, MUTED, "start", 600)
    rows = [("normal", NORM["30"], INK), ("exponential", EXP["30"], INK), ("lognormal", LOGN["30"], INK),
            ("spend", B["30"], ACCENT)]
    y = 960
    for name, r, col in rows:
        v += mono(110, y, name, 30, col, "start", 600 if col == ACCENT else 400)
        v += mono(970, y, pc(r["lower"]["p"], 1), 34, col, "end", 600)
        y += 72
    v += mono(110, 1300, f"≈ 5% + {100 * c:.2f} points × γ/√n", 30, INK, "start", 600)
    v += mono(110, 1350, "lower tail; nominal 5% in each row", 22, SOFT)
    emit("story", 3, "skewness-sets-the-pace",
         ["Skewness sets", "the pace."],
         ["The same 5% test on", "four populations."],
         v,
         ["The sample size you need", "grows like skewness squared."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["a statistic is a random variable",
             "SE = σ/√n, and s/√n runs small",
             "the error scales with γ/√n",
             "print every simulated rate ± MCSE"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 2 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["The sampling", "distribution."],
         ["The CLT, measured on real data,", "with a lab you can rerun."],
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
