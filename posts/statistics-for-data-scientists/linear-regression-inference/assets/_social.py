#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Linear Regression by Hand: Every Number in the Summary".

Statistics for Data Scientists, part 13. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 12, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: blue marks the normal equations and failures of the classical guarantee, ink QR
and what holds, tangerine the certified target. Geist Mono has no superscript digits or combining hat, so mono
text says "R-squared" and "s", and values with exponents are set in Geist. Feed cards only: the owner asked for
no Story frames (2026-10-30); the shell keeps its Story layout.

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
CANONICAL = "canery.in/blogs/linear-regression-inference"
FOOTER = "LINEAR REGRESSION BY HAND · CANERY.IN"

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


# ------------------------------------------------------------------ the numbers
from decimal import ROUND_HALF_UP, Decimal

EXA, NIS, SUM, MEA, INT, ITV, CON = (CAP[k] for k in ("example", "nist", "summary", "meaning", "interaction",
                                                      "intervals", "conditions"))
FEED_TOTAL = 8


def pc(v, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it; true minus sign."""
    return f"{(Decimal(repr(float(v))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}%".replace("-", "−")


def hv(v, nd=4):
    return f"{Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}".replace("-", "−")


SL = EXA["sleep"]
UP, PR = SL["unpaired"], SL["paired"]
LO, FI = NIS["datasets"]["Longley"], NIS["datasets"]["Filip"]
LQ = lambda d, k: min(v for v in d["solvers"][k]["lre"] if v == v)
assert (hv(UP["b"][1], 2), hv(UP["se"][1], 3), hv(UP["t"][1], 3), hv(UP["p"][1], 4)) == ("1.58", "0.849", "1.861", "0.0792")
assert (hv(PR["se"], 3), hv(PR["t"], 3), hv(PR["p"], 6)) == ("0.389", "4.062", "0.002833")
assert NIS["exact"]["matched"] == NIS["exact"]["total"] == 121
assert (hv(LQ(LO, "Householder QR"), 2), hv(LQ(LO, "normal equations (LU)"), 2), hv(LQ(FI, "Householder QR"), 2)) == \
    ("10.92", "7.38", "8.55")
assert LQ(FI, "normal equations (LU)") < 1 and LQ(FI, "NumPy lstsq, default rcond") < 1 and LQ(FI, "statsmodels OLS().fit()") < 1
assert (hv(LQ(FI, "NumPy lstsq, rcond=-1"), 2), hv(LQ(FI, "statsmodels fit(method='qr')"), 2)) == ("5.41", "8.55")
assert hv(min(FI["r_lm"]["tol1e10"]["lre"]), 2) == "8.42" and FI["r_lm"]["default"]["rank"] == 10
assert hv(FI["degree9"]["F"], 1) == "20.2"
assert (hv(SUM["r2"], 6), hv(SUM["adj_r2"], 6), hv(SUM["F"], 2), hv(SUM["sigma"], 3)) == ("0.995479", "0.992465", "330.29", "304.854")
assert (hv(SUM["aic_statsmodels"], 1), hv(SUM["aic_R"], 1)) == ("233.2", "235.2")
FW = MEA["fwl"]["GNP"]
assert (hv(MEA["fwl_points"]["simple_slope"], 4), hv(FW["slope"], 4), round(FW["sd_partial"]), round(FW["sd_raw"])) == \
    ("0.0348", "−0.0358", 2350, 99395)
OV = MEA["ovb"]
assert hv(OV["short"][OV["names"].index("GNP")], 4) == "0.0720" and hv(FW["vif"], 1) == "1788.5"
SC = CON["slope"]
cov = lambda k: [r["cover"] for r in SC[k]]
assert (pc(min(cov("skewed predictor"))), pc(max(cov("skewed predictor")))) == ("94.7%", "95.3%")
assert (pc(cov("skewed errors")[0]), pc(cov("skewed errors")[-1])) == ("93.4%", "95.4%")
assert (pc(min(cov("heavy-tailed errors"))), pc(max(cov("heavy-tailed errors")))) == ("94.9%", "95.2%")
assert (pc(cov("non-constant variance")[-1]), pc(cov("dependent errors")[-1])) == ("82.9%", "59.0%")
CV = ITV["coverage"]["rows"]
assert (pc(CV[0]["ci_covers_new"]), pc(CV[2]["ci_covers_new"]), pc(CV[-1]["ci_covers_new"])) == ("71.8%", "34.1%", "7.8%")


def stat_row(x, y, name, value, colour, note=None, size=48):
    """A labelled statistic: its name in mono on the left, the value large on the right."""
    out = mono(x, y, name, 23, colour, "start", 600)
    out += txt(970, y + 8, value, size, colour, SANS, 600, "end")
    if note:
        out += mono(x, y + 34, note, 19, MUTED)
    return out


def bar_row(x, y, name, digits, colour, label_text=None):
    """Correct digits as a bar on a 0-15 scale, 640 px wide."""
    w = max(digits, 0) / 15 * 640
    out = mono(x, y, name, 21, MUTED, "start", 600)
    out += rect(x, y + 14, max(w, 4), 34, colour, op=0.85)
    out += txt(x + max(w, 4) + 16, y + 42, label_text or ("0" if digits < 1 else hv(digits, 2)), 34, colour, SANS, 600)
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "extra sleep ~ drug-2 dummy, 20 values", 21, MUTED, "start", 600)
    v += stat_row(110, 622, "coefficient", hv(UP["b"][1], 2), INK, "the difference in the two drugs' means", size=44)
    v += stat_row(110, 722, "standard error", hv(UP["se"][1], 3), INK, "residual SD × √0.2: Student's pooled SE", size=44)
    v += stat_row(110, 822, "t on 18 df", hv(UP["t"][1], 3), INK, f"p = {hv(UP['p'][1], 4)}: Student's two-sample t-test", size=44)
    v += hline(110, 970, 900)
    v += mono(110, 950, "add nine patient dummies:", 21, MUTED, "start", 600)
    v += stat_row(110, 1020, "same 1.58, SE", hv(PR["se"], 3), LINK, f"t = {hv(PR['t'], 3)} on 9 df: the paired t-test", size=44)
    emit("feed", 1, "regression-is-the-t-test",
         ["Regression is", "the t-test."],
         ["Student's sleep data on a drug dummy, every", "number of the summary built by hand."],
         v,
         ["Not an approximation: the regression on a", "dummy is Student's test to the last digit."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "NIST's Statistical Reference Datasets", 21, MUTED, "start", 600)
    v += mono(110, 592, "certified in 500-digit arithmetic, printed to 15", 20, MUTED)
    v += stat_row(110, 672, "exact rational arithmetic", f"{NIS['exact']['matched']} / {NIS['exact']['total']}", ACCENT,
                  "coefficients, standard errors and residual SDs", size=44)
    v += hline(110, 970, 750)
    v += mono(110, 800, "Longley: 16 years, 6 nearly collinear predictors", 20, MUTED, "start", 600)
    v += mono(110, 860, "condition number of X", 22, INK, "start", 600)
    v += txt(970, 866, "4.86 × 10⁹", 40, INK, SANS, 600, "end")
    v += mono(110, 930, "condition number of XᵀX", 22, LINK, "start", 600)
    v += txt(970, 936, "2.361 × 10¹⁹", 40, LINK, SANS, 600, "end")
    v += mono(110, 990, "the value Wampler printed in 1969", 19, MUTED)
    v += mono(110, 1050, "every one of the 15 digits reproduced", 21, INK, "start", 600)
    emit("feed", 2, "fifteen-certified-digits",
         ["Fifteen digits,", "certified."],
         ["Before testing any solver, check the certificate:", "least squares on decimals has an exact answer."],
         v,
         ["All 121 certified values reproduce digit for", "digit, with nothing but Python's fractions."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 548, "correct digits of the worst coefficient (of 15)", 20, MUTED, "start", 600)
    v += bar_row(110, 610, "Longley, Householder QR", LQ(LO, "Householder QR"), INK)
    v += bar_row(110, 710, "Longley, normal equations", LQ(LO, "normal equations (LU)"), LINK)
    v += bar_row(110, 830, "Filip, Householder QR", LQ(FI, "Householder QR"), INK)
    v += bar_row(110, 930, "Filip, normal equations", LQ(FI, "normal equations (LU)"), LINK)
    v += line(110 + 640, 590, 110 + 640, 1000, ACCENT, 3)
    v += mono(110 + 640, 1050, "15 certified", 19, ACCENT, "end", 600)
    emit("feed", 3, "qr-not-normal-equations",
         ["QR, not the", "normal equations."],
         ["Forming XᵀX squares the condition number,", "so it doubles the digits the solver loses."],
         v,
         ["Longley loses 3.5 digits to the textbook route;", "Filip loses all of them."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "NIST's Filip polynomial, 10th degree, 82 points", 20, MUTED, "start", 600)
    rows = [("NumPy lstsq, default", "0 digits", LINK, "cutoff 1.8e-14 drops a singular value"),
            ("statsmodels OLS().fit()", "0 digits", LINK, "pseudoinverse; warns rank-deficient"),
            ("R lm, default tol", "drops x¹⁰", LINK, f"F = {hv(FI['degree9']['F'], 1)} says it mattered")]
    y = 620
    for name, value, colour, note in rows:
        v += stat_row(110, y, name, value, colour, note, size=36)
        y += 100
    v += hline(110, 970, 912)
    fixes = [("rcond=-1", hv(LQ(FI, "NumPy lstsq, rcond=-1"), 2)), ("method='qr'", hv(LQ(FI, "statsmodels fit(method='qr')"), 2)),
             ("tol = 1e-10", hv(min(FI["r_lm"]["tol1e10"]["lre"]), 2))]
    v += mono(110, 962, "the same calls, fixed (correct digits):", 20, MUTED, "start", 600)
    for k, (name, val) in enumerate(fixes):
        v += mono(110 + k * 300, 1020, name, 21, INK, "start", 600)
        v += txt(110 + k * 300, 1066, val, 34, INK, SANS, 600)
    emit("feed", 4, "defaults-that-fail",
         ["Three defaults,", "zero digits."],
         ["Near rank deficiency the library defaults", "truncate or drop, with one warning at most."],
         v,
         ["Read the warning and the NA: each default", "has a one-argument fix."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "Longley's summary, recomputed from X", 21, MUTED, "start", 600)
    items = [("R-squared = 1 − RSS/TSS", hv(SUM["r2"], 6), INK),
             ("adjusted: (n − 1)/(n − p)", hv(SUM["adj_r2"], 6), INK),
             ("F, nested in intercept-only", hv(SUM["F"], 2), INK),
             ("s = √(RSS/(n − p)), 9 df", hv(SUM["sigma"], 3), INK),
             ("AIC, statsmodels (k = 7)", hv(SUM["aic_statsmodels"], 1), ACCENT),
             ("AIC, R (k = 8, counts σ)", hv(SUM["aic_R"], 1), ACCENT)]
    y = 622
    for name, value, colour in items:
        v += mono(110, y, name, 22, colour, "start", 600)
        v += txt(970, y + 6, value, 36, colour, SANS, 600, "end")
        y += 76
    emit("feed", 5, "every-number-traced",
         ["Every number,", "traced."],
         ["39 numbers of statsmodels' summary, matched", "to 5.6e-12; R's summary to 1.2e-11."],
         v,
         ["The two libraries agree on every formula", "and count AIC's parameters differently."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "Longley: employment on GNP", 21, MUTED, "start", 600)
    v += stat_row(110, 622, "GNP alone", f"+{hv(MEA['fwl_points']['simple_slope'], 4)}", INK, size=44)
    v += stat_row(110, 712, "others held fixed", hv(FW["slope"], 4), LINK, "the multiple-regression coefficient", size=44)
    v += stat_row(110, 812, "Year left out", f"+{hv(OV['short'][OV['names'].index('GNP')], 4)}", LINK,
                  "omitted-variable bias, exact in the sample", size=44)
    v += hline(110, 970, 892)
    v += mono(110, 942, "spread of GNP the comparison can use", 21, MUTED, "start", 600)
    v += stat_row(110, 1012, "2,350 of 99,395", f"1/{hv(FW['sd_raw'] / FW['sd_partial'], 1)}", INK,
                  f"= 1/√VIF, VIF {hv(FW['vif'], 1)}", size=44)
    emit("feed", 6, "holding-the-others-fixed",
         ["What holding", "fixed leaves."],
         ["A coefficient compares units that agree on", "every other predictor; the data hold few."],
         v,
         ["Same data, three answers for GNP: the", "comparison, not the arithmetic, changed."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "coverage of the slope's 95% interval, n = 5 to 1,000", 20, MUTED, "start", 600)
    rows = [("skewed predictor", f"{pc(min(cov('skewed predictor')))} to {pc(max(cov('skewed predictor')))}", INK),
            ("heavy-tailed errors", f"{pc(min(cov('heavy-tailed errors')))} to {pc(max(cov('heavy-tailed errors')))}", INK),
            ("skewed errors and x", f"{pc(cov('skewed errors')[0])} to {pc(cov('skewed errors')[-1])}", INK),
            ("SD rising with x", f"down to {pc(cov('non-constant variance')[-1])}", LINK),
            ("autocorrelated errors", f"down to {pc(cov('dependent errors')[-1])}", LINK)]
    y = 626
    for name, value, colour in rows:
        v += mono(110, y, name, 23, colour, "start", 600)
        v += txt(970, y + 6, value, 36, colour, SANS, 600, "end")
        y += 82
    v += mono(110, y + 4, "20,000 simulated datasets per point; MCSE 0.15 points", 18, MUTED)
    emit("feed", 7, "normality-is-not-the-condition",
         ["Normal variables?", "Not needed."],
         ["Normality is about the errors, and it barely", "moved coverage even at n = 5."],
         v,
         ["Unequal variance and dependence break the", "interval, and more data make it worse."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("by hand", "the t-test, the paired t and ANOVA are regressions", INK),
             ("arithmetic", f"QR {hv(LQ(LO, 'Householder QR'), 2)} digits, normal equations {hv(LQ(LO, 'normal equations (LU)'), 2)}", INK),
             ("coefficients", "comparisons between units, not interventions", INK),
             ("two intervals", f"a CI used as a PI covers {pc(CV[-1]['ci_covers_new'])} at n = 600", LINK),
             ("conditions", "linearity, independence, constant variance", LINK)]
    y = 552
    for head, a, colour in items:
        v += txt(110, y, head, 28, colour, SANS, 600)
        v += mono(110, y + 40, a, 21, INK if colour == INK else colour)
        y += 112
    emit("feed", 8, "read-the-article",
         ["Linear regression,", "by hand."],
         ["Every number in the summary rebuilt from", "the design matrix, and every guarantee measured."],
         v,
         ["The full walk-through, with the lab, the", "notebook and NIST's certified test data."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
