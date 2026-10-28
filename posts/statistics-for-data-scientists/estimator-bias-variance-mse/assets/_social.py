#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Estimators and Their Errors: Why the Best One Can Be
Biased".

Statistics for Data Scientists, part 3. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 2, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks each card's point (the truth, the biased winner, the shrunken
total), blue the unbiased comparison, ink the reference.

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
CANONICAL = "canery.in/blogs/estimator-bias-variance-mse"
FOOTER = "ESTIMATORS AND THEIR ERRORS · CANERY.IN"

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
T, D, BB, S = (CAP[k] for k in ("tanks", "divisors", "baseball", "stein"))
EX, SIM = T["exact"], T["sim"]
W = T["worked"]
RAW, REP = BB["raw"], BB["replay"]
NORMAL, EXPO = D["populations"]["normal"], D["populations"]["exponential"]
assert W["serials"] == [58, 171, 272, 273, 303] and round(W["estimates"]["mvue"], 1) == 362.6
assert round(EX["mle"]["mse"]) == 5448 and round(EX["mvue"]["mse"]) == 3303 and round(EX["minmse"]["mse"]) == 3212
assert round(EX["mle"]["bias"], 1) == -56.2 and round(EX["minmse"]["bias"], 1) == -9.5
assert round(EX["mom"]["var"]) == 7706 and round(T["var_ratio_mom_mvue"]["exact"], 2) == 2.33
assert round(NORMAL["at"]["n-1"]["mse_exact"], 4) == 0.2222 and round(NORMAL["at"]["n+1"]["mse_exact"], 4) == 0.1818
assert round(EXPO["best_d_theory"], 1) == 16.4 and round(1 - EXPO["mse_ratio_best_nm1"]["exact"], 2) == 0.45
assert round(RAW["c"], 3) == 0.212 and round(RAW["tse_y"], 4) == 0.0753 and round(RAW["tse_z"], 4) == 0.0213
assert RAW["closer"] == 16 and round(100 * REP["share_js_wins"], 1) == 96.2
FEED_TOTAL, STORY_TOTAL = 8, 4
NAMES = BB["players"]
CLEM, MUNS = NAMES.index("Clemente"), NAMES.index("Munson")


def n0(v):
    """A whole number with thousands separators and a true minus sign."""
    return f"{v:,.0f}".replace("-", "−")


def avg(v):
    """A batting average as printed in baseball: .346"""
    return f"{v:.3f}".lstrip("0")


def big(x, y, value, sub, colour, size=72, sub_size=19):
    """A large number with its label below, spaced by the number's size so the text boxes never meet."""
    return txt(x, y, value, size, colour, SANS, 600) + mono(x, y + max(40, int(size * 0.6)), sub, sub_size, colour)


def bars(x, y, w, h, parts, scale):
    """A stacked horizontal bar: parts are (value, colour, opacity)."""
    out, cx = "", x
    for value, colour, op in parts:
        out += rect(cx, y, value * scale, h, colour, colour, 1.2, op=op)
        cx += value * scale
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, f"estimating N = {T['N']} tanks from k = {T['k']} serial numbers", 20, MUTED, "start", 600)
    rows = [("MLE: the largest serial", "biased", EX["mle"]["mse"], INK),
            ("MVUE: m(1 + 1/k) − 1", "unbiased", EX["mvue"]["mse"], LINK),
            ("m(k + 2)/(k + 1) − 1", f"biased by {-EX['minmse']['bias']:.1f} tanks", EX["minmse"]["mse"], ACCENT)]
    y = 650
    for name, kind, mse, col in rows:
        v += mono(110, y, name, 23, col, "start", 600)
        v += mono(110, y + 38, kind, 20, MUTED)
        v += txt(970, y + 22, n0(mse), 62, col, SANS, 600, "end")
        y += 130
    v += mono(110, 1046, "mean squared error, tanks²: exact, and matched by", 17, SOFT)
    v += mono(110, 1074, f"{T['R']:,} simulated captures", 17, SOFT)
    emit("feed", 1, "unbiased-is-not-best",
         ["Unbiased is not", "the same as best."],
         ["Three estimates of how many tanks exist,", "scored by mean squared error."],
         v,
         ["The most accurate rule here is biased.", "Unbiasedness was never the yardstick."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    X = lambda s: 110 + s * 860 / 420
    y0 = 700
    v += mono(110, 556, "one capture of five tanks; true N hidden", 20, MUTED, "start", 600)
    v += line(X(0), y0, X(W["max"]), y0, RULE_SOLID, 2)
    v += line(X(W["max"]), y0, X(W["estimates"]["mvue"]), y0, LINK, 3.5, "10,6")
    for s_ in W["serials"]:
        v += f'<circle cx="{X(s_):.1f}" cy="{y0}" r="9" fill="{INK}"/>'
    for s_, lab in ((58, "58"), (171, "171"), (272.5, "272, 273")):
        v += mono(X(s_), y0 - 26, lab, 21, INK, "middle", 600)
    v += mono(X(W["max"]), y0 + 46, str(W["max"]), 21, INK, "middle", 600)    # below: clear of "272, 273"
    v += line(X(T["N"]), y0 - 90, X(T["N"]), y0 + 70, ACCENT, 3, "8,6")
    v += mono(X(T["N"]), y0 - 102, f"true N = {T['N']}", 20, ACCENT, "middle", 600)
    v += mono(110, 830, f"MLE: the largest serial, {W['max']}", 23, INK, "start", 600)
    v += mono(110, 872, "can never be above N, so it is biased low", 19, MUTED)
    v += mono(110, 940, f"MVUE: {W['max']} + {W['estimates']['mvue'] - W['max']:.1f} = {W['estimates']['mvue']:.1f}", 23, LINK, "start", 600)
    v += mono(110, 982, f"{W['max'] - T['k']} unseen serials below {W['max']}, in {T['k']} gaps:", 19, MUTED)
    v += mono(110, 1014, "add one more gap of average size", 19, MUTED)
    emit("feed", 2, "five-serial-numbers",
         ["Five serial numbers.", "How many tanks?"],
         ["The German tank problem: tanks numbered", "1 to N, five captured, N unknown."],
         v,
         ["The largest serial is a floor for N,", "not an estimate of it."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cols = [(110, "month", INK, "start"), (560, "intelligence", MUTED, "end"), (760, "serials", LINK, "end"),
            (970, "records", ACCENT, "end")]
    for x, head, col, anc in cols:
        v += mono(x, 556, head, 20, col, anc, 600)
    v += hline(110, 970, 578)
    y = 640
    for row in T["ruggles_brodie"]:
        v += mono(110, y, row["month"], 23, INK)
        v += mono(560, y, f"{row['intelligence']:,}", 26, MUTED, "end")
        v += mono(760, y, str(row["serial_number"]), 26, LINK, "end", 600)
        v += mono(970, y, str(row["records"]), 26, ACCENT, "end", 600)
        y += 76
    errs = [abs(r["serial_error_pct"]) for r in T["ruggles_brodie"]]
    ratios = [r["intelligence_ratio"] for r in T["ruggles_brodie"]]
    v += hline(110, 970, 846)
    v += mono(110, 900, f"serial numbers: within {min(errs):.1f}% to {max(errs):.1f}%", 21, LINK, "start", 600)
    v += mono(110, 942, f"intelligence: {min(ratios):.1f} to {max(ratios):.1f} times the records", 21, MUTED)
    v += mono(110, 1030, "German tanks per month; Ruggles and Brodie (1947),", 17, SOFT)
    v += mono(110, 1058, "as reproduced by Simon (2024)", 17, SOFT)
    emit("feed", 3, "serials-beat-intelligence",
         ["Serial numbers beat", "the intelligence reports."],
         ["Tank production per month: estimated in the", "war, then read in Germany's own records."],
         v,
         ["An estimator with an error model beat", "confident guesses without one."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "mean squared error in tanks², N = 342, k = 5", 20, MUTED, "start", 600)
    scale = 860 / 5600
    rows = [("MLE", "mle"), ("MVUE", "mvue"), ("m(k + 2)/(k + 1) − 1", "minmse")]
    y = 610
    for name, key in rows:
        e = EX[key]
        b2 = e["bias"] ** 2
        v += mono(110, y, name, 22, INK, "start", 600)
        v += bars(110, y + 20, 0, 50, [(e["var"], LINK, 0.22), (b2, ACCENT, 0.30)], scale)
        v += mono(110, y + 104, f"variance {n0(e['var'])} + bias² {n0(b2)} = {n0(e['mse'])}" if b2 > 1
                  else f"variance {n0(e['var'])}, bias 0", 19, MUTED)
        y += 160
    v += mono(110, 1090, "blue: variance · tangerine: bias²", 17, SOFT)
    emit("feed", 4, "bias-squared-plus-variance",
         ["Error = bias²", "+ variance."],
         ["Each estimator's mean squared error,", "split into its two parts."],
         v,
         [f"{EX['mle']['bias'] ** 2 / EX['mle']['mse']:.0%} of the MLE's error is bias.",
          f"The best rule spends {n0(EX['minmse']['bias'] ** 2)} to save {n0(EX['mvue']['var'] - EX['minmse']['var'])}."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    mom, mvue = EX["mom"]["var"], EX["mvue"]["var"]
    v += mono(110, 556, "start: 2 × mean − 1, unbiased but wasteful", 20, MUTED, "start", 600)
    v += txt(110, 650, f"Var = {n0(mom)}", 52, INK, SANS, 600)
    v += mono(110, 716, f"= {n0(mom - mvue)}   scatter among captures with the same max", 20, MUTED)
    v += mono(110, 750, f"+ {n0(mvue)}   spread of the averages", 20, LINK)
    v += hline(110, 970, 790)
    v += mono(110, 846, "average it over captures sharing the largest serial m:", 20, MUTED)
    v += mono(110, 896, "E(2 × mean − 1 | m) = m(1 + 1/k) − 1", 26, LINK, "start", 600)
    v += txt(110, 990, f"Var = {n0(mvue)}", 52, LINK, SANS, 600)
    v += mono(110, 1050, f"the MVUE: {T['var_ratio_mom_mvue']['exact']:.2f} = (k + 2)/3 times less variance", 20, MUTED)
    emit("feed", 5, "rao-blackwell",
         ["Average away the", "noise you can't use."],
         ["Rao–Blackwell: condition an estimator on", "a statistic that holds all the information."],
         v,
         ["Conditioning on a sufficient statistic", "never makes an estimator worse."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, f"estimating a variance from n = {D['n']}: MSE of SS / d", 20, MUTED, "start", 600)
    v += mono(110, 620, "normal data", 22, INK, "start", 600)
    y = 674
    for key, lab in (("n-1", "n − 1"), ("n", "n"), ("n+1", "n + 1")):
        a = NORMAL["at"][key]
        col = ACCENT if key == "n+1" else INK
        v += mono(150, y, f"divide by {lab}", 21, col, "start", 600 if key == "n+1" else 400)
        v += mono(970, y, f"{a['mse_exact']:.4f}", 26, col, "end", 600)
        y += 46
    v += hline(110, 970, 836)
    v += mono(110, 892, "exponential data", 22, LINK, "start", 600)
    v += mono(150, 946, "divide by n − 1", 21, INK)
    v += mono(970, 946, f"{EXPO['at']['n-1']['mse_exact']:.4f}", 26, INK, "end", 600)
    v += mono(150, 992, f"divide by {EXPO['best_d_theory']:.1f}, the best", 21, ACCENT, "start", 600)
    v += mono(970, 992, f"{EXPO['at']['best']['mse_exact']:.4f}", 26, ACCENT, "end", 600)
    v += mono(110, 1062, "best d = n + 1 + (n − 1)κ/n, κ the excess kurtosis", 18, SOFT)
    emit("feed", 6, "n-minus-1-is-not-best",
         ["n − 1 buys unbiasedness,", "not the smallest error."],
         ["Estimating a variance: the exact mean", "squared error of each divisor."],
         v,
         ["n + 1 is best only for normal tails;", "the best divisor grows with kurtosis."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    y_, p_, z_ = BB["y"], BB["p"], RAW["z"]
    v += mono(110, 556, f"shrinking factor c = {RAW['c']:.3f}: every average moves", 20, MUTED, "start", 600)
    v += mono(110, 588, f"{1 - RAW['c']:.0%} of the way to the grand mean, {RAW['ybar']:.3f}", 20, MUTED, "start", 600)
    for i, (idx, who) in enumerate(((CLEM, "Clemente"), (MUNS, "Munson"))):
        y = 668 + i * 108
        v += mono(110, y, who, 24, INK, "start", 600)
        v += mono(370, y, f"{avg(y_[idx])}  →  {avg(z_[idx])}", 28, LINK, "start", 600)
        v += mono(110, y + 40, f"first 45 at-bats → James–Stein; rest of season {avg(p_[idx])}", 18, MUTED)
    v += hline(110, 970, 888)
    v += mono(110, 940, "total squared error, all 18 players", 20, MUTED, "start", 600)
    v += mono(110, 994, f"own averages {RAW['tse_y']:.4f}", 26, INK, "start", 600)
    v += mono(970, 994, f"James–Stein {RAW['tse_z']:.4f}", 26, ACCENT, "end", 600)
    v += mono(110, 1062, f"James–Stein closer for {RAW['closer']} of 18 players", 18, SOFT)
    emit("feed", 7, "steins-paradox",
         ["Stein's paradox,", "on 18 batters."],
         ["Averages after 45 at-bats in 1970, used", "to predict each player's rest of season."],
         v,
         ["Shrinking all 18 toward their mean", f"cut the total error {RAW['ratio']:.1f}-fold."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("bias² + variance", "unbiasedness removes one term", f"tanks: MLE {n0(EX['mle']['mse'])}, MVUE {n0(EX['mvue']['mse'])}"),
             ("Rao–Blackwell", "condition on a sufficient statistic", f"variance ÷ {T['var_ratio_mom_mvue']['exact']:.2f}"),
             ("n + 1", "beats n − 1 for normal data", f"{1 - 1 / NORMAL['mse_ratio_nm1_np1']['exact']:.0%} lower MSE at n = {D['n']}"),
             ("James–Stein", f"smaller error in {100 * REP['share_js_wins']:.1f}% of replayed seasons",
              f"1970: {RAW['ratio']:.1f} times less total error")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "James–Stein" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Estimators and", "their errors."],
         ["Every number measured by a seeded lab", "you can rerun in about 13 seconds."],
         v,
         ["The full walk-through, with the lab", "and every number's Monte Carlo error."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    rows = [("German tanks, MSE", f"MLE {n0(EX['mle']['mse'])} · MVUE {n0(EX['mvue']['mse'])}",
             f"biased stretch {n0(EX['minmse']['mse'])}", f"N = {T['N']}, k = {T['k']}"),
            (f"a variance, n = {D['n']}", f"n − 1: {NORMAL['at']['n-1']['mse_exact']:.3f}",
             f"n + 1: {NORMAL['at']['n+1']['mse_exact']:.3f}", "normal data"),
            ("18 batters, total error", f"averages {RAW['tse_y']:.4f}", f"James–Stein {RAW['tse_z']:.4f}", "1970 season")]
    y = 880
    for head, a, b, c in rows:
        v += mono(110, y, head, 26, MUTED, "start", 600)
        v += mono(110, y + 50, a, 28, INK)
        v += mono(110, y + 92, b, 28, ACCENT, "start", 600)                      # each row's winner
        v += mono(970, y + 92, c, 22, SOFT, "end")
        y += 180
    emit("story", 1, "the-best-can-be-biased",
         ["The best estimator", "can be biased."],
         ["Unbiasedness removes one term", "of the error, not both."],
         v,
         ["Judge an estimator by its", "mean squared error."],
         STORY_TOTAL)


def story_02():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    y_, p_, z_ = BB["y"], BB["p"], RAW["z"]
    v += mono(110, 870, "first 45 at-bats → James–Stein", 26, MUTED, "start", 600)
    for i, (idx, who) in enumerate(((CLEM, "Clemente"), (MUNS, "Munson"))):
        y = 960 + i * 130
        v += mono(110, y, who, 30, INK, "start", 600)
        v += mono(970, y, f"{avg(y_[idx])} → {avg(z_[idx])}", 34, LINK, "end", 600)
        v += mono(110, y + 46, f"rest of the season: {avg(p_[idx])}", 24, MUTED)
    v += txt(110, 1310, f"{RAW['ratio']:.1f}×", 96, ACCENT, SANS, 600)
    v += mono(330, 1290, "less total squared error", 26, ACCENT)
    v += mono(330, 1326, f"closer for {RAW['closer']} of 18 players", 24, MUTED)
    emit("story", 2, "steins-paradox",
         ["Stein's", "paradox."],
         ["18 batting averages after", "45 at-bats, 1970."],
         v,
         ["Pull every average toward", "the mean: less error in total."],
         STORY_TOTAL)


def story_03():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 870, f"captured: {', '.join(map(str, W['serials']))}", 26, MUTED, "start", 600)
    v += mono(110, 960, "MLE, the largest serial", 28, INK, "start", 600)
    v += mono(970, 960, str(W["max"]), 40, INK, "end", 600)
    v += mono(110, 1004, f"bias {EX['mle']['bias']:.1f}, RMSE {EX['mle']['rmse']:.1f}".replace("-", "−"), 24, MUTED)
    v += mono(110, 1110, "MVUE, plus one average gap", 28, LINK, "start", 600)
    v += mono(970, 1110, f"{W['estimates']['mvue']:.1f}", 40, LINK, "end", 600)
    v += mono(110, 1154, f"unbiased, RMSE {EX['mvue']['rmse']:.1f}", 24, MUTED)
    v += mono(110, 1260, f"true N = {T['N']}", 32, ACCENT, "start", 600)
    v += mono(110, 1306, "Germany's recorded production, August 1942", 22, SOFT)
    emit("story", 3, "five-serial-numbers",
         ["Five tanks.", "How many exist?"],
         ["The German tank problem,", "by hand."],
         v,
         [f"Add one average gap:", f"{W['max']} + {W['estimates']['mvue'] - W['max']:.1f} = {W['estimates']['mvue']:.1f}."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["MSE = bias² + variance",
             "condition on a sufficient statistic",
             "n − 1 is unbiased, not best",
             "shrink many averages to their mean"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 3 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Estimators and", "their errors."],
         ["Bias, variance and Stein's paradox,", "measured, with a lab you can rerun."],
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
