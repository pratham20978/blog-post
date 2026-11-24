#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Permutation and Rank Tests: What They Actually Test".

Statistics for Data Scientists, part 10. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 8, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks the test read as answering a question it does not answer, blue
the test that answers it, ink the rest. Feed cards only: the owner asked for no Story frames
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
CANONICAL = "canery.in/blogs/permutation-and-rank-tests"
FOOTER = "PERMUTATION AND RANK TESTS · CANERY.IN"

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

EX, TS, MW, EF = (CAP[k] for k in ("example", "twosample", "mannwhitney", "efficiency"))
PERM, SR, MC, FW, HL = EX["perm"], EX["signed_rank"], EX["monte_carlo"], EX["fwer"], EX["hodges_lehmann"]
D40 = TS["designs"]["10,40"]
S1, S2, S3 = MW["S1"], MW["S2"], MW["S3"]
SH = EF["shapes"]
FEED_TOTAL = 8


def pc(v, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return f"{(Decimal(repr(float(v))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}%"


def p4(v):
    return f"{Decimal(repr(float(v))).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)}"


K1000 = FW["999"]["tests"].index(1000)
assert (p4(EX["p_t"]), p4(PERM["p"]), p4(SR["p"]), p4(EX["sign"]["p"])) == ("0.0497", "0.0527", "0.0413", "0.0074")
assert (PERM["gt"], PERM["eq"], PERM["ge"], PERM["n_assign"], EX["sum8"]) == (835, 28, 863, 32768, 314)
assert (pc(MC["p_below"]), p4(MC["q_lo"]), p4(MC["q_hi"])) == ("19.4%", "0.0466", "0.0592")
assert (pc(FW["999"]["naive"][K1000]), pc(FW["999"]["plus_one"][K1000])) == ("63.2%", "0.0%")
assert [pc(D40[k]["perm_diff"], 2) for k in ("0.25", "1", "2", "4")] == ["0.06%", "4.89%", "18.31%", "29.10%"]
assert [pc(D40[k]["perm_studentised"], 2) for k in ("0.25", "1", "2", "4")] == ["3.87%", "4.92%", "5.73%", "5.81%"]
assert [pc(S1[k]["mw"]) for k in ("50", "200", "400")] == ["16.7%", "50.2%", "79.7%"] and f"{MW['theta1']:.3f}" == "0.443"
assert (min(pc(v["mw"]) for v in S2.values()), max(pc(v["mw"]) for v in S2.values())) == ("4.7%", "5.7%")
assert (pc(S3["4"]["mw"], 2), pc(S3["4"]["bm"], 2), pc(S3["2"]["mw"], 2), pc(S3["2"]["bm"], 2)) == ("14.81%", "5.27%", "9.93%", "5.55%")
assert [(f"{SH[k]['are']:.3f}", pc(SH[k]["mw"]), pc(SH[k]["welch"])) for k in ("normal", "parabolic", "uniform", "Laplace", "t, 3 df")] == \
    [("0.955", "77.6%", "79.7%"), ("0.864", "74.1%", "79.9%"), ("1.000", "73.5%", "79.8%"), ("1.500", "88.0%", "79.8%"), ("1.900", "95.0%", "84.0%")]
assert f"{100 * (SH['t, 3 df']['mw'] - SH['t, 3 df']['welch']):.1f}" == "10.9"
assert (HL["estimate"], HL["lower"], HL["upper"]) == (3.125, 0.5, 5.1875)


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
    v += mono(110, 556, "Darwin's 15 pairs of maize plants (1876)", 21, MUTED, "start", 600)
    v += mono(110, 590, "crossed minus self-fertilised: 13 of 15 positive", 20, MUTED)
    rows = (("t-test", "values, normal model", EX["p_t"], INK), ("randomisation test", "values, signs flipped", PERM["p"], INK),
            ("signed-rank test", "ranks and signs", SR["p"], MUTED), ("sign test", "signs only", EX["sign"]["p"], MUTED))
    y = 668
    for name, keeps, p, col in rows:
        v += mono(110, y, name, 25, col, "start", 600)
        v += mono(110, y + 32, f"keeps: {keeps}", 19, SOFT)
        v += txt(970, y + 14, f"p = {p4(p)}", 44, col, SANS, 600, "end")
        y += 102
    emit("feed", 1, "four-tests-four-answers",
         ["One data set,", "four p-values."],
         ["Darwin's maize pairs through four tests", "of one idea: crossing makes no difference."],
         v,
         ["Each test keeps a different part of the data,", "so each answers a different question."],
         FEED_TOTAL)


def feed_02():
    vals, counts = PERM["null_values"], PERM["null_counts"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "totals of all 32,768 sign patterns, eighths of an inch", 21, MUTED, "start", 600)
    x0, x1, base, top = 110, 970, 860, 610
    peak = max(counts)
    for val, c in zip(vals, counts):
        x = x0 + (val + 560) / 1120 * (x1 - x0)
        v += line(x, base, x, base - c / peak * (base - top), ACCENT if abs(val) >= 314 else SOFT, 1.4 if abs(val) >= 314 else 1.2)
    for val in (-314, 314):
        x = x0 + (val + 560) / 1120 * (x1 - x0)
        v += line(x, top - 6, x, base, INK, 1.6, "6,5")
    v += hline(x0, x1, base, RULE_SOLID, 1.5)
    v += mono(x0 + (314 + 560) / 1120 * (x1 - x0) + 10, top + 14, "Darwin: 314", 20, INK, "start", 600)
    for x, lab in ((110, f"above 314: {PERM['gt']}"), (420, f"equal: {PERM['eq']}"), (680, f"at least: {PERM['ge']}")):
        v += mono(x, 920, lab, 22, ACCENT, "start", 600)
    v += mono(110, 966, "and as many in the mirror tail", 20, MUTED)
    v += stat_row(110, 1040, "two-sided p = 1,726 / 32,768", p4(PERM["p"]), INK, f"t-test on the same pairs: {p4(EX['p_t'])}", 52)
    emit("feed", 2, "every-sign-assignment",
         ["Exact, with no", "normal model."],
         ["If a coin had decided each pair's sides, every", "one of the 32,768 sign patterns was equally likely."],
         v,
         ["Fisher counted it by hand in 1935: 863 of 32,768", "sign patterns total at least Darwin's 314."],
         FEED_TOTAL)


def feed_03():
    pv, pmf = MC["pvalues"], MC["pmf"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "scipy.stats.permutation_test, default settings", 21, MUTED, "start", 600)
    v += mono(110, 590, "the p-value it returns for Darwin's pairs, over reruns", 20, MUTED)
    x0, x1, base, top = 110, 970, 860, 640
    lo, hi = 0.040, 0.068
    peak = max(pmf)
    for p, w in zip(pv, pmf):
        if lo <= p <= hi:
            x = x0 + (p - lo) / (hi - lo) * (x1 - x0)
            v += line(x, base, x, base - w / peak * (base - top), ACCENT if p <= 0.05 + 1e-12 else SOFT, 2.6)
    for p, col, lab in ((0.05, INK, "0.05"), (PERM["p"], LINK, f"exact {p4(PERM['p'])}")):
        x = x0 + (p - lo) / (hi - lo) * (x1 - x0)
        v += line(x, top - 14, x, base, col, 2, "6,5" if col == INK else None)
        v += mono(x + (8 if col == LINK else -8), top - 22, lab, 19, col, "start" if col == LINK else "end", 600)
    v += hline(x0, x1, base, RULE_SOLID, 1.5)
    v += stat_row(110, 930, "runs at or below 0.05", pc(MC["p_below"]), ACCENT, f"95% of runs between {p4(MC['q_lo'])} and {p4(MC['q_hi'])}", 52)
    v += mono(110, 1058, "9,999 random flips by default; n_resamples=np.inf enumerates", 20, INK)
    emit("feed", 3, "a-monte-carlo-p-is-random",
         ["A Monte Carlo", "p-value is random."],
         ["SciPy's default draws 9,999 random sign flips,", "fewer than the 32,768 it could enumerate."],
         v,
         ["On Darwin's pairs, 19.4% of default runs report", "p ≤ 0.05; the exact p-value is 0.0527."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "m random relabellings, b at least as extreme", 21, MUTED, "start", 600)
    v += mono(110, 590, "Bonferroni over 1,000 true nulls, m = 999 each", 20, MUTED)
    v += stat_row(110, 690, "report b/m", pc(FW["999"]["naive"][K1000]), ACCENT, "family-wise error: at least one false rejection", 60)
    v += hline(110, 970, 790, RULE_SOLID)
    v += stat_row(110, 870, "report (b + 1)/(m + 1)", pc(FW["999"]["plus_one"][K1000]), LINK, "no p below 1/1,000, the corrected cut is 0.00005", 60)
    v += hline(110, 970, 970, RULE_SOLID)
    v += mono(110, 1030, "b/m is 0 with probability 1/(m + 1) under the null,", 20, INK)
    v += mono(110, 1062, "and a zero survives any multiple-testing correction", 20, INK)
    emit("feed", 4, "add-one",
         ["Count the observed", "labelling: add one."],
         ["A random-permutation p-value is exact as", "(b + 1)/(m + 1), not as b/m."],
         v,
         ["With 999 permutations per test and 1,000 tests,", "b/m rejected a true null 63.2% of the time."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "groups of 10 and 40, normal data, equal means", 21, MUTED, "start", 600)
    v += mono(110, 606, "SD of the 10 / SD of the 40", 19, SOFT)
    v += mono(700, 606, "raw difference", 19, ACCENT, "end", 600)
    v += mono(970, 606, "studentised", 19, LINK, "end", 600)
    y = 672
    for k, lab in (("0.25", "1/4"), ("1", "1"), ("2", "2"), ("4", "4")):
        bad = float(k) > 1
        v += mono(110, y, lab, 28, INK, "start", 600)
        v += mono(700, y, pc(D40[k]["perm_diff"], 2), 30, ACCENT if bad else INK, "end", 600)
        v += mono(970, y, pc(D40[k]["perm_studentised"], 2), 30, LINK, "end", 600)
        y += 70
    v += mono(110, 1000, "size of a 5% permutation test of equal means;", 20, MUTED)
    v += mono(110, 1032, "50,000 data sets per row, 999 relabellings each", 20, MUTED)
    emit("feed", 5, "exact-for-what",
         ["Exact for identical", "distributions, not means."],
         ["Relabelling mixes the groups, so the reference", "spread is pooled, like Student's standard error."],
         v,
         ["Permute Welch's t, not the raw difference: 5.73%", "instead of 18.31% when the 10 have twice the SD."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += txt(110, 556, f"equal medians, P(X > Y) = {MW['theta1']:.3f}", 27, INK, SANS, 600)
    y = 610
    for k in ("50", "200", "400"):
        v += mono(110, y, f"{k} per group", 23, MUTED)
        v += mono(970, y, pc(S1[k]["mw"]), 28, ACCENT, "end", 600)
        y += 44
    v += hline(110, 970, 760, RULE_SOLID)
    v += txt(110, 810, "medians 0.18 SD apart, P(X > Y) = ½", 27, INK, SANS, 600)
    v += mono(110, 856, "every size from 10 to 400 per group", 23, MUTED)
    v += mono(970, 856, f"{min(pc(v_['mw']) for v_ in S2.values())} to {max(pc(v_['mw']) for v_ in S2.values())}", 28, ACCENT, "end", 600)
    v += hline(110, 970, 900, RULE_SOLID)
    v += txt(110, 950, "equal centres, SDs 4 to 1, groups of 10 and 40", 25, INK, SANS, 600)
    v += mono(110, 996, "Mann–Whitney", 23, ACCENT, "start", 600)
    v += mono(970, 996, pc(S3["4"]["mw"], 2), 28, ACCENT, "end", 600)
    v += mono(110, 1040, "Brunner–Munzel", 23, LINK, "start", 600)
    v += mono(970, 1040, pc(S3["4"]["bm"], 2), 28, LINK, "end", 600)
    v += mono(110, 1090, "rejection rate of a 5% Mann–Whitney test", 19, SOFT)
    emit("feed", 6, "not-a-median-test",
         ["Mann–Whitney is not", "a test of medians."],
         ["It responds to P(X > Y), and it is exact only", "when the two distributions are identical."],
         v,
         ["Choose by hypothesis: Welch for means, Brunner–", "Munzel for P(X > Y), a median method for medians."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "power at 20 per group, shift giving Student 80% on normal data", 20, MUTED, "start", 600)
    v += mono(110, 606, "shape", 19, SOFT)
    v += mono(560, 606, "ARE", 19, SOFT, "end")
    v += mono(780, 606, "Mann–Whitney", 19, ACCENT, "end", 600)
    v += mono(970, 606, "Welch", 19, INK, "end", 600)
    y = 670
    for k in ("normal", "parabolic", "uniform", "Laplace", "t, 3 df"):
        sv = SH[k]
        v += mono(110, y, k, 26, INK, "start", 600)
        v += mono(560, y, f"{sv['are']:.3f}", 26, LINK if sv["are"] >= 1 else ACCENT, "end", 600)
        v += mono(780, y, pc(sv["mw"]), 26, ACCENT, "end", 600)
        v += mono(970, y, pc(sv["welch"]), 26, INK, "end", 600)
        y += 66
    v += mono(110, 1030, "ARE: large-sample ratio of sample sizes for equal power", 19, MUTED)
    v += mono(110, 1062, "100,000 simulated data sets per shape", 19, MUTED)
    emit("feed", 7, "the-price-of-ranks",
         ["Ranks cost little,", "and pay in the tails."],
         ["The efficiency of Mann–Whitney against the", "t-test, in the limit and in samples of 20."],
         v,
         ["The ARE is 3/π = 0.955 for normal data and never", "below 0.864; with t, 3 df ranks gain 10.9 points."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("the randomisation test", f"Darwin: exact p = {p4(PERM['p'])}, t-test {p4(EX['p_t'])}", INK),
             ("Monte Carlo p-values", f"report (b + 1)/(m + 1); b/m gave {pc(FW['999']['naive'][K1000])} family-wise error", LINK),
             ("a permutation test of means", f"{pc(D40['2']['perm_diff'], 2)} raw, {pc(D40['2']['perm_studentised'], 2)} studentised, 10 and 40", ACCENT),
             ("Mann–Whitney", f"{pc(S1['400']['mw'])} rejections at equal medians, 400 per group", ACCENT),
             ("Hodges–Lehmann", f"Darwin: {HL['estimate']} in, exact interval {HL['lower']} to {HL['upper']}", INK)]
    y = 552
    for head, a, colour in items:
        v += txt(110, y, head, 28, colour, SANS, 600)
        v += mono(110, y + 40, a, 21, INK if colour == INK else colour)
        y += 112
    emit("feed", 8, "read-the-article",
         ["What does your", "test actually test?"],
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
