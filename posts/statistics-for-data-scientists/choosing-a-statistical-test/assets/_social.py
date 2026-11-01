#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Which Statistical Test? The Design Decides, Not the Data".

Statistics for Data Scientists, part 8. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 7, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks the pooled or conditional classic and each card's failure, blue
the test the article recommends, ink the rest. Feed cards only: the owner asked for no Story frames
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
CANONICAL = "canery.in/blogs/choosing-a-statistical-test"
FOOTER = "CHOOSING A TEST · CANERY.IN"

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

EX, TS, PR, TB, AN = (CAP[k] for k in ("example", "twosample", "pretest", "tables", "anova"))
E40 = TS["designs"]["10,40"]["exact"]
PB = PR["by_ratio"]
A80 = TS["power_at_80"]
MP = TB["malocclusion"]["pvalues"]
SZ = TB["designs"]["malocclusion"]["size"]
SIM = AN["simulation"]
FEED_TOTAL = 8


def pc(v, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return f"{(Decimal(repr(float(v))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}%"


def r3(v):
    return f"{v:.3f}".replace("-", "−")


assert (f"{EX['paired']['p']:.4f}", f"{EX['student']['p']:.3f}", f"{EX['welch']['p']:.3f}") == ("0.0028", "0.079", "0.079")
assert [r3(v) for v in EX["var_identity"]] == ["3.201", "4.009", "5.697", "1.513"] and r3(EX["r"]) == "0.795"
assert (r3(EX["student"]["se"]), r3(EX["paired"]["se"]), f"{EX['se_ratio']:.2f}", round(EX["n_equivalent_per_arm"])) == ("0.849", "0.389", "2.18", 48)
assert [pc(E40[k]["student"], 2) for k in ("0.25", "0.5", "1", "1.5", "2", "4")] == ["0.07%", "0.52%", "5.00%", "12.17%", "18.25%", "29.37%"]
assert (pc(min(v["welch"] for v in E40.values()), 2), pc(max(v["welch"] for v in E40.values()), 2)) == ("4.97%", "5.15%")
assert (pc(A80["25,25"]["welch"]), pc(A80["10,40"]["welch"]), pc(A80["10,40"]["student"])) == ("79.9%", "75.6%", "80.0%")
assert [pc(PB[k]["levene_rule"]["rate"], 2) for k in ("1.5", "2")] == ["9.74%", "9.13%"] and [pc(PB[k]["welch"]["rate"], 2) for k in ("1.5", "2")] == ["5.07%", "5.06%"]
assert [pc(PB[k]["lev_reject"]["rate"]) for k in ("1.5", "2")] == ["27.9%", "64.6%"] and pc(PB["2"]["student_given_accept"]["rate"], 2) == "21.19%"
assert [f"{MP[k]:.3f}" for k in ("mid_p", "pearson", "n_minus_1", "barnard", "fisher", "boschloo", "yates", "fisher_doubled")] == \
    ["0.112", "0.122", "0.127", "0.143", "0.174", "0.175", "0.286", "0.287"]
assert [pc(SZ[k]["max"], 2) for k in ("fisher", "yates", "pearson", "mid_p", "boschloo")] == ["3.61%", "2.19%", "4.94%", "5.14%", "4.63%"]
assert TB["tea"]["ways"] == [1, 16, 36, 16, 1] and SZ["boschloo"]["n_rejected"] - SZ["fisher"]["n_rejected"] == 10
assert (pc(SIM["negative pairing"]["F"], 2), pc(SIM["negative pairing"]["W"], 2)) == ("16.13%", "5.25%")


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
    v += mono(110, 556, "Student's 1908 sleep data: ten patients, two drugs", 21, MUTED, "start", 600)
    v += mono(110, 596, "the same twenty numbers, the same 1.58-hour difference", 21, MUTED)
    v += stat_row(110, 700, "paired: each patient took both", f"p = {EX['paired']['p']:.4f}", LINK,
                  f"t = {EX['paired']['t']:.2f} on 9 df, SE {r3(EX['paired']['se'])}", 60)
    v += hline(110, 970, 800, RULE_SOLID)
    v += stat_row(110, 880, "as two groups, as the layout suggests", f"p = {EX['student']['p']:.3f}", ACCENT,
                  f"t = {EX['student']['t']:.2f} on 18 df, SE {r3(EX['student']['se'])}", 60)
    v += mono(110, 1030, "R's help page: the 20 values are measurements", 20, INK)
    v += mono(110, 1062, "on 10 persons, not two groups", 20, INK)
    emit("feed", 1, "the-design-decides",
         ["The design decides,", "not the data."],
         ["Same numbers, two tests. How the data were", "collected says which one answers the question."],
         v,
         ["Paired, the drugs differ at p = 0.0028; read as", "two groups, the same numbers give p = 0.079."],
         FEED_TOTAL)


def feed_02():
    vi = EX["var_identity"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "why pairing shrinks the standard error", 21, MUTED, "start", 600)
    rows = (("Var(drug 1)", r3(vi[0]), INK), ("+ Var(drug 2)", r3(vi[1]), INK),
            (f"− 2 Cov (correlation {r3(EX['r'])})", r3(vi[2]), ACCENT), ("= Var(difference)", r3(vi[3]), LINK))
    y = 626
    for name, val, col in rows:
        v += mono(110, y, name, 24, col, "start", 600)
        v += mono(970, y, val, 30, col, "end", 600)
        y += 58
    v += hline(110, 970, 866, RULE_SOLID)
    v += stat_row(110, 930, "SE as two groups", r3(EX["student"]["se"]), ACCENT, None, 44)
    v += stat_row(110, 1000, "SE paired", r3(EX["paired"]["se"]), LINK, None, 44)
    v += mono(110, 1068, f"a parallel trial: about {round(EX['n_equivalent_per_arm'])} patients per drug", 20, MUTED)
    v += mono(110, 1096, "for the same precision (from these variances)", 20, MUTED)
    emit("feed", 2, "pairing-removes-the-patients",
         ["Pairing removes", "the patients."],
         ["A patient high on one drug is high on the", "other, so that spread cancels in the difference."],
         v,
         [f"Pairing removed {r3(EX['var_identity'][2])} of a variance of {EX['var_identity'][0] + EX['var_identity'][1]:.2f},", f"and the standard error fell {EX['se_ratio']:.2f} times."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "exact type I error of a 5% test, groups of 10 and 40", 21, MUTED, "start", 600)
    v += mono(110, 606, "SD of the 10 / SD of the 40", 19, SOFT)
    v += mono(700, 606, "Student", 19, ACCENT, "end", 600)
    v += mono(970, 606, "Welch", 19, LINK, "end", 600)
    y = 662
    for k, lab in (("0.25", "1/4"), ("0.5", "1/2"), ("1", "1"), ("1.5", "1.5"), ("2", "2"), ("4", "4")):
        bad = float(k) > 1
        v += mono(110, y, lab, 26, INK, "start", 600)
        v += mono(700, y, pc(E40[k]["student"], 2), 28, ACCENT if bad else INK, "end", 600)
        v += mono(970, y, pc(E40[k]["welch"], 2), 28, LINK, "end", 600)
        y += 64
    v += mono(110, 1062, "normal data; computed by quadrature, checked by simulation", 19, MUTED)
    emit("feed", 3, "student-follows-the-pairing",
         ["Student's t-test fails", "when sizes and SDs differ."],
         ["It pools the variances, so a small group's", "large variance is understated."],
         v,
         ["When the group of 10 has 4 times the SD, Student's", "5% test rejects 29.37% of the time; Welch's 5.04%."],
         FEED_TOTAL)


def feed_04():
    a25, a40 = A80["25,25"], A80["10,40"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "power with equal SDs, where Student's test has 80.0%", 21, MUTED, "start", 600)
    v += txt(110, 646, "groups of 25 and 25", 30, INK, SANS, 600)
    v += mono(110, 690, f"true difference {a25['delta']:.2f} SD", 20, MUTED)
    v += stat_row(110, 750, "Welch's power", pc(a25["welch"]), LINK, f"{100 * a25['max_gap']:.2f} points below Student's at most", 54)
    v += hline(110, 970, 846, RULE_SOLID)
    v += txt(110, 916, "groups of 10 and 40", 30, INK, SANS, 600)
    v += mono(110, 960, f"true difference {a40['delta']:.2f} SD", 20, MUTED)
    v += stat_row(110, 1020, "Welch's power", pc(a40["welch"]), LINK, "its degrees of freedom are near 14, not 48", 54)
    emit("feed", 4, "the-price-of-welch",
         ["Welch's test", "has a price."],
         ["When the variances really are equal, it", "spends a little power that pooling would not."],
         v,
         ["Under 0.1 points in a balanced design, 4.4 at", "10 against 40: small beside Student's failure."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "Levene's test first: Welch if it rejects, else Student", 21, MUTED, "start", 600)
    v += mono(110, 596, "groups of 10 and 40, normal data, no true difference", 20, MUTED)
    v += mono(110, 652, "SD ratio (10 / 40)", 19, SOFT)
    v += mono(540, 652, "Levene detects", 19, SOFT, "end")
    v += mono(760, 652, "procedure", 19, INK, "end", 600)
    v += mono(970, 652, "Welch alone", 19, LINK, "end", 600)
    y = 712
    for k in ("1.5", "2"):
        v += mono(110, y, k, 28, INK, "start", 600)
        v += mono(540, y, pc(PB[k]["lev_reject"]["rate"]), 28, MUTED, "end")
        v += mono(760, y, pc(PB[k]["levene_rule"]["rate"], 2), 28, ACCENT, "end", 600)
        v += mono(970, y, pc(PB[k]["welch"]["rate"], 2), 28, LINK, "end", 600)
        y += 62
    v += hline(110, 970, 846, RULE_SOLID)
    v += mono(110, 908, "on the samples Levene passed, at a ratio of 2:", 21, INK)
    v += stat_row(110, 976, "Student's error", pc(PB["2"]["student_given_accept"]["rate"], 2), ACCENT,
                  f"against {pc(PB['2']['student']['rate'], 2)} on all samples", 54)
    emit("feed", 5, "pre-testing-does-not-help",
         ["Testing assumptions", "first does not help."],
         ["The pre-test misses the differences that", "matter, and selects the worst samples."],
         v,
         ["Letting Levene choose left a 5% test at 9.74%;", "always using Welch gave 5.07%."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "normal teeth: breast-fed 4 of 20, bottle-fed 1 of 22", 21, MUTED, "start", 600)
    v += mono(110, 590, "smallest expected count 2.38 (Hellman, via Yates 1934)", 19, MUTED)
    rows = (("Fisher's mid-p", "mid_p", INK), ("Pearson chi-squared", "pearson", MUTED), ("'N − 1' chi-squared", "n_minus_1", MUTED),
            ("Barnard (unconditional)", "barnard", LINK), ("Fisher exact, Irwin's rule", "fisher", ACCENT),
            ("Boschloo (unconditional)", "boschloo", LINK), ("Yates-corrected: the default", "yates", MUTED),
            ("Fisher exact, doubled tail", "fisher_doubled", ACCENT))
    y = 650
    for name, k, col in rows:
        v += mono(110, y, name, 23, col, "start", 600)
        v += mono(970, y, f"{MP[k]:.3f}", 26, col, "end", 600)
        y += 54
    emit("feed", 6, "one-table-eight-answers",
         ["One 2 × 2 table,", "eight p-values."],
         ["The same counts through eight tests in use,", "from the mid-p value to doubled Fisher."],
         v,
         ["R's and SciPy's default chi-squared test gives", "0.286 here; the mid-p value gives 0.112."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += txt(110, 566, "both margins fixed: the tea test", 28, INK, SANS, 600)
    v += mono(110, 608, "eight cups, she is told four have milk first", 20, MUTED)
    v += mono(110, 644, "all eight right: 1/70 = 0.0143, exactly", 22, LINK, "start", 600)
    v += hline(110, 970, 684, RULE_SOLID)
    v += txt(110, 744, "only the group sizes fixed: 20 and 22", 28, INK, SANS, 600)
    v += mono(110, 786, "largest size of a 5% test, every table summed", 20, MUTED)
    y = 842
    for name, k, col in (("Fisher's exact", "fisher", ACCENT), ("Yates-corrected", "yates", MUTED), ("Boschloo", "boschloo", LINK),
                         ("Pearson", "pearson", MUTED), ("mid-p", "mid_p", INK)):
        v += mono(110, y, name, 23, col, "start", 600)
        v += mono(970, y, pc(SZ[k]["max"], 2), 26, col, "end", 600)
        y += 50
    emit("feed", 7, "the-margins-decide",
         ["In a 2 × 2 table,", "the margins decide."],
         ["Which totals the design fixed in advance", "decides whether Fisher's test is exact."],
         v,
         ["At 20 and 22, Boschloo's test rejected every table", "Fisher's did and 10 more, at a size of at most 4.63%."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("the design picks the test", f"paired p = {EX['paired']['p']:.4f}; as two groups p = {EX['student']['p']:.3f}", LINK),
             ("Student against Welch, 10 and 40", f"{pc(E40['4']['student'], 2)} against {pc(E40['4']['welch'], 2)} at 4 times the SD", INK),
             ("pre-testing the assumptions", f"{pc(PB['1.5']['levene_rule']['rate'], 2)} where Welch alone gives {pc(PB['1.5']['welch']['rate'], 2)}", ACCENT),
             ("2 × 2 tables", f"Fisher's 5% test at most {pc(SZ['fisher']['max'], 2)} with groups of 20 and 22", INK),
             ("ANOVA, three groups", f"F {pc(SIM['negative pairing']['F'], 2)} against W {pc(SIM['negative pairing']['W'], 2)} under negative pairing", INK)]
    y = 552
    for head, a, colour in items:
        v += txt(110, y, head, 28, colour, SANS, 600)
        v += mono(110, y + 40, a, 21, INK if colour == INK else colour)
        y += 112
    emit("feed", 8, "read-the-article",
         ["Which test?", "Ask the design."],
         ["Every test computed by hand, matched to SciPy", "and R, and its error rate measured."],
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
