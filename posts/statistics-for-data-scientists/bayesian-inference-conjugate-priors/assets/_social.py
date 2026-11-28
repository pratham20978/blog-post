#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Bayesian Inference by Hand: Conjugacy and Credible Intervals".

Statistics for Data Scientists, part 11. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 8, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks the posterior and the published answer, blue the data or the
alternative reading, ink the rest. Feed cards only: the owner asked for no Story frames
(2026-10-30); the shell keeps its Story layout.

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
CANONICAL = "canery.in/blogs/bayesian-inference-conjugate-priors"
FOOTER = "BAYESIAN INFERENCE BY HAND · CANERY.IN"

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


TEXTS: list[str] = []


def txt(x, y, value, size=22, fill=INK, family=SANS, weight=400, anchor="start", track=None):
    TEXTS.append(str(value))
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
    print(json.dumps({"card": path.stem, "texts": TEXTS[:]}, ensure_ascii=False))
    TEXTS.clear()


# ------------------------------------------------------------------ the numbers
from decimal import ROUND_HALF_UP, Decimal

LA, PF, IV, PR, LI = (CAP[k] for k in ("laplace", "pfizer", "intervals", "priors", "lindley"))
ROWS = {r["endpoint"]: r for r in PF["rows"]}
PRIM = ROWS["covid19_7d_after_dose2_no_prior_infection"]
SEV = ROWS["first_severe_covid19_7d_after_dose2_no_prior_infection"]
CON = PF["constants"]
NM = PR["named"]
Y82 = LI["years"]["1782"]
FO = LI["focus"]
FEED_TOTAL = 8


def pc(v, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it; true minus sign."""
    return f"{(Decimal(repr(float(v))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}%".replace("-", "−")


def hv(v, nd=4):
    return f"{Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}"


def sci(x, nd=4, sup=True):
    import math
    e = math.floor(math.log10(abs(x)))
    m = (Decimal(repr(float(x))) / Decimal(10) ** e).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    s = "".join("⁰¹²³⁴⁵⁶⁷⁸⁹"[int(c)] if c.isdigit() else "⁻" for c in str(e))
    return f"{m} × 10{s}"


PRIORS = (("trial", "beta(0.700102, 1)"), ("senn_alternative", "beta(1, 1.428363)"), ("uniform", "beta(1, 1)"),
          ("jeffreys", "beta(½, ½)"), ("haldane", "beta(0, 0)"))
assert sci(LA["tail_exact"]) == "1.1461 × 10⁻⁴²" and hv(LA["sds_below_mean"], 1) == "13.6"
assert (pc(PRIM["lower"]), pc(PRIM["upper"]), pc(SEV["lower"]), pc(SEV["upper"])) == ("90.3%", "97.6%", "−124.8%", "96.3%")
assert sci(PRIM["p_ve_le_30"], 2) == "2.46 × 10⁻²⁸" and all(r["matches_published"] for r in PF["rows"])
assert (hv(CON["a_from_rounded_mean"], 6), pc(CON["prior_p_ve_lt_0"]), pc(CON["ve_at_prior_median"])) == ("0.700102", "38.4%", "40.9%")
assert (pc(CON["prior95_ve"][0], 0), pc(CON["prior95_ve"][1])) == ("−2616%", "99.5%")
assert [pc(NM["primary"][k]["lower"]) for k, _ in PRIORS] == ["90.3%", "90.1%", "90.1%", "90.5%", "90.9%"]
assert [pc(NM["severe"][k]["lower"]) for k, _ in PRIORS] == ["−124.8%", "−116.6%", "−154.6%", "−154.4%", "−143.9%"]
assert (pc(PRIM["prior_weight"]), pc(SEV["prior_weight"])) == ("1.0%", "29.8%")
IP, IS = IV["primary"], IV["severe"]
assert [pc(v) for v in IP["equal_tailed"] + IP["hdi_ve"]] == ["90.3%", "97.6%", "90.9%", "97.9%"]
assert [pc(v) for v in IS["equal_tailed"] + IS["hdi_ve"]] == ["−124.8%", "96.3%", "−69.7%", "99.9%"]
assert (pc(IP["p_ve_at_least_lower"]["equal_tailed"]), pc(IP["p_ve_at_least_lower"]["hdi_ve"])) == ("97.5%", "96.1%")
CP_, CS_ = IP["coverage"], IS["coverage"]
assert pc(CP_["prior_average_quadrature"], 3) == "95.000%" and [pc(v) for v in CP_["credible_range_ve_0_95"]] == ["92.9%", "96.5%"]
assert (pc(CS_["credible_min_ve_0_99"]), pc(CS_["credible_min_at_ve"])) == ("86.6%", "96.3%")
assert [pc(v) for v in CP_["cp_range_ve_0_95"]] == ["95.1%", "98.0%"]
assert (Y82["boys"], Y82["n"], hv(Y82["p_exact"]), hv(Y82["bf01"], 2), hv(FO["bf10_informed"], 2)) == (9851, 19387, "0.0241", "8.60", "11.54")
assert LI["lindley_years"] == ["1772", "1778", "1779", "1782"] and len(LI["years"]) == 14


def stat_row(x, y, name, value, colour, note=None, size=48):
    """A labelled statistic: its name in mono on the left, the value large on the right."""
    out = mono(x, y, name, 23, colour, "start", 600)
    out += txt(970, y + 8, value, size, colour, SANS, 600, "end")
    if note:
        out += mono(x, y + 34, note, 19, MUTED)
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    a, b = LA["posterior"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "Paris baptisms, 1745 to 1770 (Laplace, 1781)", 21, MUTED, "start", 600)
    v += stat_row(110, 636, "boys", f"{LA['boys']:,}", INK, size=44)
    v += stat_row(110, 716, "girls", f"{LA['girls']:,}", INK, size=44)
    v += mono(110, 790, f"uniform prior → posterior beta({a:,}, {b:,})", 20, MUTED)
    v += stat_row(110, 880, "P(x ≤ ½), exact", sci(LA["tail_exact"]), ACCENT, size=46)
    v += stat_row(110, 990, "Laplace's first term", "1.1521 × 10⁻⁴²", INK, "his own series, “a little too great”", size=40)
    emit("feed", 1, "laplaces-question",
         ["How sure was", "Laplace?"],
         ["x is the chance that a Paris birth is a boy.", "A uniform prior, 26 years of baptisms."],
         v,
         [f"½ lies {hv(LA['sds_below_mean'], 1)} posterior SDs below the mean:", "the boys' excess is no accident."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "Pfizer–BioNTech phase 3, primary endpoint", 21, MUTED, "start", 600)
    v += stat_row(110, 630, "prior on θ", "beta(0.700102, 1)", MUTED, size=36)
    v += stat_row(110, 700, "+ cases", "8 vaccine, 162 placebo", LINK, size=36)
    v += stat_row(110, 770, "= posterior", "beta(8.700102, 163)", ACCENT, size=36)
    v += mono(110, 840, "VE = 1 − θ / ((1 − θ) r), r = 2.214 / 2.222", 20, MUTED)
    v += stat_row(110, 930, "95% credible interval", f"{pc(PRIM['lower'])} to {pc(PRIM['upper'])}", ACCENT, "published: 90.3 to 97.6", size=44)
    v += stat_row(110, 1044, "P(VE ≤ 30%)", sci(PRIM["p_ve_le_30"], 2), INK, size=36)
    emit("feed", 2, "the-trials-interval-by-hand",
         ["A vaccine trial's", "interval, by hand."],
         ["θ is the vaccine group's share of cases.", "The protocol's prior, then the data."],
         v,
         ["Conjugacy turns the trial's Bayesian analysis", "into two additions and two quantiles."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "the target: θ at VE 30% = 0.7 / 1.7 = 0.411765", 21, MUTED, "start", 600)
    v += mono(110, 596, "rounded to 0.4118; beta(p/(1 − p), 1) has mean p", 20, MUTED)
    v += stat_row(110, 680, "0.4118 / 0.5882", hv(CON["a_from_rounded_mean"], 6), ACCENT, size=48)
    v += hline(110, 970, 740)
    v += mono(110, 790, "what the 'minimally informative' prior says", 21, MUTED, "start", 600)
    v += stat_row(110, 870, "P(VE < 0), harm", pc(CON["prior_p_ve_lt_0"]), INK, size=44)
    v += stat_row(110, 960, "median VE", pc(CON["ve_at_prior_median"]), INK, "its mean of θ maps to 30%, its median to 40.9%", size=44)
    v += stat_row(110, 1070, "95% interval for VE", "−2,616% to 99.5%", INK, size=36)
    emit("feed", 3, "where-0700102-comes-from",
         ["Where does", "0.700102 come from?"],
         ["The prior's first parameter has six figures", "and its second has one. The reason is a rounding."],
         v,
         ["A 'minimally informative' prior still says", "something: 38.4% that the vaccine does harm."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "lower limit of the 95% credible interval for VE", 21, MUTED, "start", 600)
    v += mono(110, 610, "prior", 19, SOFT)
    v += mono(760, 610, "8 : 162", 19, LINK, "end", 600)
    v += mono(970, 610, "1 : 3", 19, ACCENT, "end", 600)
    y = 672
    for key, name in PRIORS:
        v += mono(110, y, name, 24, INK, "start", 600)
        v += mono(760, y, pc(NM["primary"][key]["lower"]), 26, LINK, "end", 600)
        v += mono(970, y, pc(NM["severe"][key]["lower"]), 26, ACCENT, "end", 600)
        y += 64
    v += mono(110, 1012, f"the prior's weight: {pc(PRIM['prior_weight'])} of the posterior mean at 170 cases,", 19, MUTED)
    v += mono(110, 1044, f"{pc(SEV['prior_weight'])} at 4 (the trial's severe-case endpoint)", 19, MUTED)
    emit("feed", 4, "170-cases-against-4",
         ["170 cases outvote", "the prior. 4 do not."],
         ["Five common priors, two endpoints from the", "same trial, one lower limit each."],
         v,
         ["With few events every default prior shows in", "the answer: report the prior and vary it."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "two 95% intervals from one posterior", 21, MUTED, "start", 600)
    rows = (("8 : 162, equal tails", IP["equal_tailed"], ACCENT, "published 90.3 to 97.6"),
            ("8 : 162, highest density", IP["hdi_ve"], LINK, None),
            ("1 : 3, equal tails", IS["equal_tailed"], ACCENT, "published −124.8 to 96.3"),
            ("1 : 3, highest density", IS["hdi_ve"], LINK, None))
    y = 640
    for name, (lo, hi), col, note in rows:
        v += stat_row(110, y, name, f"{pc(lo)} to {pc(hi)}", col, note, size=36)
        y += 106 if note else 84
    v += mono(110, 1072, f"P(VE ≥ lower end), 8 : 162: {pc(IP['p_ve_at_least_lower']['equal_tailed'])} with equal tails, "
              f"{pc(IP['p_ve_at_least_lower']['hdi_ve'])} with the HDI", 19, MUTED)
    emit("feed", 5, "equal-tails-or-highest-density",
         ["Equal tails or", "highest density?"],
         ["Only one of them reproduces the trial's", "published intervals."],
         v,
         ["Quantiles survive a change of scale; the", "shortest interval does not."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "exact coverage of the trial's 95% credible interval", 21, MUTED, "start", 600)
    v += stat_row(110, 650, "averaged over the prior", pc(CP_["prior_average_quadrature"], 3), ACCENT, "for any number of cases: it holds 95% of each posterior", size=44)
    v += stat_row(110, 790, "170 cases, VE 0 to 95%", f"{pc(CP_['credible_range_ve_0_95'][0])} to {pc(CP_['credible_range_ve_0_95'][1])}", INK, size=40)
    v += stat_row(110, 890, "4 cases, lowest", pc(CS_["credible_min_ve_0_99"]), INK, f"at a true VE of {pc(CS_['credible_min_at_ve'])}", size=40)
    v += stat_row(110, 1020, "Clopper–Pearson, 170 cases", f"{pc(CP_['cp_range_ve_0_95'][0])} to {pc(CP_['cp_range_ve_0_95'][1])}", LINK, size=40)
    emit("feed", 6, "what-95-percent-promises",
         ["What does 95%", "promise?"],
         ["The credible interval held to a fixed true", "efficacy, and averaged over its prior."],
         v,
         ["A credible interval's 95% is an average over", "its prior, not a guarantee at each true value."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, f"Paris, 1782: {Y82['boys']:,} boys of {Y82['n']:,} births", 21, MUTED, "start", 600)
    v += mono(110, 596, "H0: a birth is a boy with probability ½", 20, MUTED)
    v += stat_row(110, 680, "exact binomial test", f"p = {hv(Y82['p_exact'])}", INK, "rejects ½ at the 5% level", size=44)
    v += stat_row(110, 810, "Bayes factor, uniform H1", f"BF01 = {hv(Y82['bf01'], 2)}", ACCENT, "favours ½, P(H0 | data) = 0.896", size=44)
    v += stat_row(110, 940, "H1's prior: 1745–1770", f"BF10 = {hv(FO['bf10_informed'], 2)}", LINK, "the earlier years' posterior: against ½", size=44)
    v += mono(110, 1068, "4 of the 14 years 1771–1784 reject at 5% while BF01 exceeds 1", 19, MUTED)
    emit("feed", 7, "lindleys-paradox-1782",
         ["Rejected at 5%,", "favoured 8.6 to 1."],
         ["Lindley's paradox in one year of Laplace's", "own table of Paris baptisms."],
         v,
         ["A Bayes factor inherits its alternative's", "prior, and at a fixed z it grows like √n."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    assert f"{LA['tail_exact']:.4e}" == "1.1461e-42"
    items = [("Laplace, 1781", f"P(x ≤ ½) = {LA['tail_exact']:.4e}; his own 1.1521e-42", INK),
             ("the trial's interval", f"beta(8.700102, 163) → VE {pc(PRIM['lower'])} to {pc(PRIM['upper'])}", ACCENT),
             ("the prior's weight", f"{pc(PRIM['prior_weight'])} at 170 cases, {pc(SEV['prior_weight'])} at 4", INK),
             ("flat is a choice of scale", "uniform on θ: P(VE ≤ 0) = ½", LINK),
             ("Lindley's paradox", f"1782: p = {hv(Y82['p_exact'])}, BF01 = {hv(Y82['bf01'], 2)}", ACCENT)]
    y = 552
    for head, a, colour in items:
        v += txt(110, y, head, 28, colour, SANS, 600)
        v += mono(110, y + 40, a, 21, INK if colour == INK else colour)
        y += 112
    emit("feed", 8, "read-the-article",
         ["Bayesian inference,", "by hand."],
         ["Every posterior in closed form, matched to", "SciPy and R, and every prior checked."],
         v,
         ["The full walk-through, with the lab, the", "protocol's boundaries and every check."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
