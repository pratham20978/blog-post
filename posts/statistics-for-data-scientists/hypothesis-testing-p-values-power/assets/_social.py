#!/usr/bin/env python3
"""Build the finished Canery feed sources for "p-Values and Power: How Wrong Can a Significant Result Be?".

Statistics for Data Scientists, part 5. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 4, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks each card's point (the significant right-sign tail, the
p-equals risk, the TOST result) and blue the wrong sign or the naive reading. Feed cards only: the owner
asked for no Story frames (2026-10-30); the shell keeps its Story layout for parts that want one.

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
CANONICAL = "canery.in/blogs/hypothesis-testing-p-values-power"
FOOTER = "P-VALUES AND POWER · CANERY.IN"

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
P, PW, RD, RP, F, T, ST = (CAP[k] for k in ("pvalues", "power", "retrodesign", "replication", "fpr", "tost", "stopping"))
DU, DC = RD["durante"], RD["cases"]["durante_2"]
EQ03, EQ05 = F["equals"]["0.03"], F["equals"]["0.05"]
OP = PW["observed_power"]["table"]
assert round(DU["critical"], 2) == 15.88 and round(DC["exact"]["power"], 4) == 0.0570 and round(DC["exact"]["typeS"], 3) == 0.240
assert round(DC["exact"]["exaggeration"], 2) == 9.54 and round(DU["min_exaggeration"], 2) == 7.94 and round(DU["p_obs"], 4) == 0.0358
assert (round(EQ03["lr"], 1), round(100 * EQ03["fpr_prior05"], 1), round(100 * EQ03["fpr_prior01"], 1)) == (5.0, 16.7, 64.3)
assert round(100 * F["tree"]["fpr"]) == 36 and round(100 * PW["design"]["power"], 2) == 78.14
assert [round(100 * P["z"][k]["power_exact"], 1) for k in ("null", "durante", "lam1", "lam2", "lam28")] == [5.0, 5.7, 17.0, 51.6, 80.0]
assert P["dance"]["n_sig"] == 19 and round(P["dance"]["p_min"], 5) == 0.00007 and round(P["dance"]["p_max"], 2) == 0.33
assert (round(P["cumming"]["lo"], 5), round(P["cumming"]["hi"], 2)) == (0.00008, 0.44)
assert (RP["sig_orig"], RP["sig_rep"], RP["pairs"]) == (97, 36, 97) and (round(RP["mean_r_orig"], 3), round(RP["mean_r_rep"], 3)) == (0.396, 0.197)
assert RP["nonsig"]["n"] == 63 and (RP["nonsig"]["equivalent_0.1"], RP["nonsig"]["equivalent_0.2"]) == (2, 17) and RP["nonsig"]["n_for_80_0.1"] == 854
assert round(T["bound80"]["16"]["tost_exact"], 2) == 1.06 and round(100 * T["power_bound05"][0]["power"], 1) == 0.8
assert [round(100 * ST["exact"]["at"][k], 2) for k in ("2", "10", "100", "1000")] == [8.31, 19.33, 37.36, 52.99]
assert round(OP["0.05"], 2) == 0.50
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


def bar_curve(x0, y0, w, h):
    """The worked example's curve of replicated estimates, N(2, 8.1²), with its two significant tails."""
    A, s, crit = DC["A"], DC["s"], DU["critical"]
    pdf = lambda e: math.exp(-0.5 * ((e - A) / s) ** 2) / (s * math.sqrt(2 * math.pi))
    X = lambda e: x0 + (e + 36) / 72 * w
    Y = lambda d: y0 + h - d / 0.052 * h
    xs = [-36 + 72 * i / 400 for i in range(401)]
    tail = lambda seg: " ".join(f"{a:.1f},{b:.1f}" for a, b in [(X(seg[0]), Y(0))] + [(X(e), Y(pdf(e))) for e in seg] + [(X(seg[-1]), Y(0))])
    out = f'<polygon points="{tail([e for e in xs if e >= crit])}" fill="{ACCENT}" fill-opacity="0.85"/>'
    out += f'<polygon points="{tail([e for e in xs if e <= -crit])}" fill="{LINK}" fill-opacity="0.6"/>'
    out += polyline([(X(e), Y(pdf(e))) for e in xs], INK, 4)
    out += line(X(-36), Y(0), X(36), Y(0), MUTED, 2)
    for v in (crit, -crit):
        out += line(X(v), y0 + 8, X(v), Y(0), MUTED, 2, "8,6")
    return out, X, Y


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "two groups of 16, power 78%: an observed p = .03", 21, MUTED, "start", 600)
    v += stat_row(110, 650, "what the misreading says", "3%", LINK, "the chance the result is a fluke")
    v += stat_row(110, 780, "false positive risk, even prior odds", pc(EQ03["fpr_prior05"]), ACCENT, f"likelihood ratio {EQ03['lr']:.1f}")
    v += stat_row(110, 910, "false positive risk, prior 0.1", pc(EQ03["fpr_prior01"]), ACCENT, "if one tested effect in ten is real")
    v += mono(110, 1044, "the p-value is computed assuming no effect, so it cannot", 18, SOFT)
    v += mono(110, 1072, "be the probability of no effect", 18, SOFT)
    emit("feed", 1, "p-is-not-a-fluke",
         ["p = 0.03 is not a 3%", "chance of a fluke."],
         ["What a p-value says, and what the chance", "a significant result is false depends on."],
         v,
         ["The chance a result is false needs a prior:", f"{pc(EQ03['fpr_prior01'])} at 1 in 10, for p = .03."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "replications of a 2013 study: SE 8.1 points, plausible effect 2", 21, MUTED, "start", 600)
    curve, X, Y = bar_curve(110, 600, 520, 330)
    v += curve
    v += mono(X(DU["critical"]), 592, f"+{DU['critical']:.1f}", 20, MUTED, "middle")
    v += mono(X(-DU["critical"]), 592, f"−{DU['critical']:.1f}", 20, MUTED, "middle")
    v += mono(670, 640, "significant, right sign", 22, ACCENT, "start", 600)
    v += mono(670, 680, pc(DC["exact"]["p_hi"], 2), 30, ACCENT, "start", 600)
    v += mono(670, 740, "significant, wrong sign", 22, LINK, "start", 600)
    v += mono(670, 780, pc(DC["exact"]["p_lo"], 2), 30, LINK, "start", 600)
    v += mono(670, 840, "average significant size", 22, INK, "start", 600)
    v += mono(670, 880, f"{DC['mean_abs_sig']:.2f} = {DC['exact']['exaggeration']:.2f} × 2", 30, INK, "start", 600)
    v += mono(110, 980, "estimate (points)", 18, SOFT)
    v += mono(110, 1044, f"the study reported 17 points with p = .035; any significant", 18, SOFT)
    v += mono(110, 1072, f"estimate here exceeds 15.9, at least {DU['min_exaggeration']:.1f} times the plausible 2", 18, SOFT)
    emit("feed", 2, "significant-so-big",
         ["Significant, so it", "must be big."],
         ["At 5.7% power only estimates beyond", "the bar count, whatever the truth."],
         v,
         [f"Every significant estimate overstates the effect;", f"{pc(DC['exact']['typeS'], 0)} have the wrong sign."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "a two-sided z-test; λ = true effect / standard error", 21, MUTED, "start", 600)
    rows = [("λ = 0, no effect", "null"), ("λ = 0.25, the 2013 design", "durante"), ("λ = 1", "lam1"), ("λ = 2", "lam2"), ("λ = 2.8", "lam28")]
    v += mono(640, 610, "p ≤ .05", 20, SOFT, "end") + mono(930, 610, "median p", 20, SOFT, "end")
    y = 664
    for name, k in rows:
        d = P["z"][k]
        col = ACCENT if k == "durante" else INK
        v += mono(110, y, name, 24, col, "start", 600)
        v += mono(640, y, pc(d["power_exact"]), 26, col, "end", 600)
        med = d["median_exact"]
        v += mono(930, y, f"{med:.3f}" if med >= 0.01 else f"{med:.4f}", 26, col, "end", 600)
        y += 72
    v += mono(110, 1044, f"{P['z']['null']['R']:,} simulated tests per row agree with these exact values", 18, SOFT)
    v += mono(110, 1072, "a p-value has a distribution, like any statistic", 18, SOFT)
    emit("feed", 3, "p-is-a-random-variable",
         ["Under no effect,", "p is uniform."],
         ["With the design fixed, P(p ≤ a) = a; under", "an effect, p piles up toward zero."],
         v,
         ["At low power p is nearly uniform:", "it says almost nothing about the effect."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    d = P["dance"]
    v += mono(110, 556, f"one experiment, 25 runs: 16 per group, power {pc(PW['design']['power'])}", 21, MUTED, "start", 600)
    ps = sorted(d["p"])
    picks = [ps[0], ps[4], ps[9], ps[14], ps[18], ps[19], ps[21], ps[24]]
    y = 640
    for i, pv in enumerate(picks):
        col = ACCENT if pv <= 0.05 else LINK
        txt_v = f"{pv:.5f}" if pv < 0.001 else f"{pv:.4f}" if pv < 0.01 else f"{pv:.3f}"
        xx = 110 + (i % 4) * 225
        yy = y + (i // 4) * 90
        v += mono(xx, yy, txt_v, 32, col, "start", 600)
    v += mono(110, 840, f"orange: p ≤ .05 ({d['n_sig']} of 25); blue: not; 8 of the 25 shown, sorted", 20, MUTED)
    v += hline(110, 970, 880, RULE_SOLID)
    v += mono(110, 940, "after an original p = .05, a replication's one-tailed p", 22, INK, "start", 600)
    v += mono(110, 978, f"lands between {P['cumming']['lo']:.5f} and {P['cumming']['hi']:.2f} with 80% probability", 22, INK, "start", 600)
    v += mono(110, 1072, f"Cumming's interval, reproduced: {pc(P['cumming']['inside'], 2)} of simulated replications inside", 18, SOFT)
    emit("feed", 4, "same-experiment",
         ["One experiment,", f"p from {d['p_min']:.5f} to {d['p_max']:.2f}."],
         ["Nothing changed between runs but", "the sample."],
         v,
         ["A single p is one draw: report the estimate", "and its interval, not just the verdict."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "observed power, two-sided z-test: power at the estimated effect", 21, MUTED, "start", 600)
    v += mono(110, 612, "p-value", 22, SOFT) + mono(970, 612, "observed power", 22, SOFT, "end")
    y = 680
    for k in ("0.001", "0.01", "0.05", "0.2", "0.5"):
        col = ACCENT if k == "0.05" else INK
        v += mono(110, y, f"p = {k}", 30, col, "start", 600)
        v += txt(970, y + 6, f"{OP[k]:.2f}", 46, col, SANS, 600, "end")
        y += 80
    v += mono(110, 1072, "a fixed function of p: above p = .05 it is always below 0.5", 18, SOFT)
    emit("feed", 5, "observed-power",
         ["Observed power is", "the p-value again."],
         ["Plug the estimated effect into the power", "formula and you only get p back."],
         v,
         ["For a design analysis, take the effect", "from outside the data."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "Reproducibility Project: Psychology, 100 replications (CC0 data)", 21, MUTED, "start", 600)
    v += stat_row(110, 650, "significant, originals → replications", f"{RP['sig_orig']} → {RP['sig_rep']}", INK, "of 100 coded pairs", 50)
    v += stat_row(110, 780, "mean effect size r", f"{RP['mean_r_orig']:.3f} → {RP['mean_r_rep']:.3f}", ACCENT, f"97 pairs; the replication smaller in {pc(RP['share_rep_below_orig'], 1)}", 50)
    b1, b2 = RP["by_original_p"]["p_below_001"], RP["by_original_p"]["p_001_to_05"]
    v += mono(110, 920, f"original p below .001: kept {pc(b1['ratio'], 0)}, {b1['replicated']} of {b1['n']} replicated", 22, INK, "start", 600)
    v += mono(110, 960, f"original p .001 to .05: kept {pc(b2['ratio'], 0)}, {b2['replicated']} of {b2['n']} replicated", 22, INK, "start", 600)
    v += mono(110, 1044, "the significance filter predicts the shrinkage and its split", 18, SOFT)
    v += mono(110, 1072, "by p; other causes cannot be ruled out, and that is disputed", 18, SOFT)
    emit("feed", 6, "replications-halve",
         ["Replications kept half", "the effect."],
         ["Published effects passed the significance", "filter, so they arrive inflated."],
         v,
         ["Don't plan a study's power around", "a published effect: shrink it first."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    ns = RP["nonsig"]
    v += mono(110, 556, f"the {ns['n']} non-significant replications, tested for equivalence", 21, MUTED, "start", 600)
    v += stat_row(110, 650, "ruled out any |r| of 0.1 or more", str(ns["equivalent_0.1"]), ACCENT, f"of {ns['n']}; that needs n = {ns['n_for_80_0.1']} at 80% power", 56)
    v += stat_row(110, 780, "ruled out any |r| of 0.2 or more", str(ns["equivalent_0.2"]), INK, f"the median replication had n = {RP['median_n_rep']:.0f}", 56)
    v += hline(110, 970, 850, RULE_SOLID)
    b16 = T["bound80"]["16"]["tost_exact"]
    v += mono(110, 920, "two one-sided tests, 16 per group, 80% power:", 22, INK, "start", 600)
    v += mono(110, 960, f"rules out only effects larger than {b16:.2f} SD", 22, ACCENT, "start", 600)
    v += mono(110, 1072, "TOST: reject both 'at most −Δ' and 'at least +Δ', a 90% interval inside ±Δ", 18, SOFT)
    emit("feed", 7, "not-significant-is-not-no-effect",
         ["Not significant is", "not no effect."],
         ["To claim no meaningful effect, test", "for equivalence with a bound that matters."],
         v,
         ["Most failed replications mean", "\"not shown\", not \"absent\"."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("a p-value is a random variable", "uniform under no effect, nearly so at low power", INK),
             ("power, by the noncentral t", f"16 per group, d = 1: {pc(PW['design']['power'], 2)}; observed power adds nothing", INK),
             ("type S and M errors", f"at 5.7% power: {pc(DC['exact']['typeS'], 0)} wrong sign, {DC['exact']['exaggeration']:.1f} times too big", ACCENT),
             ("false positive risk, TOST, peeking", f"p = .03 at 1 in 10: {pc(EQ03['fpr_prior01'], 0)}; 16 per group: ±{T['bound80']['16']['tost_exact']:.2f} SD; 100 looks: {pc(ST['exact']['at']['100'], 0)}", INK)]
    y = 556
    for head, a, colour in items:
        v += txt(110, y, head, 30, colour, SANS, 600)
        v += mono(110, y + 42, a, 21, INK if colour == INK else colour)
        y += 136
    emit("feed", 8, "read-the-article",
         ["p-values, power, and", "how wrong significance is."],
         ["Every number measured by a seeded lab", "you can rerun in about 30 seconds."],
         v,
         ["The full walk-through, with the lab", "and every number's Monte Carlo error."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
