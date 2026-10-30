#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Likelihood: The MLE, Three Tests, and Where χ² Fails".

Statistics for Data Scientists, part 4. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 3, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: Wald is blue, the score tangerine and the likelihood ratio ink wherever the three
appear together; elsewhere tangerine marks each card's point (the corrected p-value, the profile interval, the
boundary's point mass) and blue the Wald or naive comparison. Feed cards only: the owner asked for no Story
frames (2026-10-30); the shell keeps its Story layout for parts that want one.

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
CANONICAL = "canery.in/blogs/likelihood-mle-fisher-information"
FOOTER = "LIKELIHOOD AND WHERE χ² FAILS · CANERY.IN"

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
P, NB, B, PL = (CAP[k] for k in ("poisson", "nb", "boundary", "powerlaw"))
V1 = P["v1"]
ST = V1["nulls"]["0.85"]
XI = P["corps"]["all"]["XI"]
WS = P["wald_scale"]
NBV, NIN, BV1 = B["null_boundary"]["v1"], B["null_interior"], B["v1"]
TOP10, KS = PL["by_threshold"][2], PL["ks"]
assert (V1["total"], V1["n"]) == (537, 576) and round(V1["lam_hat"], 4) == 0.9323 and round(V1["se"], 4) == 0.0402
assert round(V1["obs_info"], 1) == 617.8
assert (round(ST["wald"], 2), round(ST["lr"], 2), round(ST["score"], 2)) == (4.18, 4.45, 4.59)
assert (round(XI["wald"], 2), round(XI["lr"], 2), round(XI["score"], 2)) == (6.55, 10.27, 13.43)
assert round(min(WS["corps"]), 2) == 3.63 and round(max(WS["corps"]), 2) == 27.52
assert [round(v, 3) for v in NB["intervals_k"]["profile"]] == [0.585, 1.383]
assert [round(v, 3) for v in NB["intervals_k"]["wald_obs"]] == [0.500, 1.230]
assert round(100 * NB["k_sampling"]["above_wald"], 2) == 7.47 and round(100 * NB["k_sampling"]["below_wald"], 2) == 0.14
assert round(BV1["lr"], 2) == 0.41 and round(BV1["p_naive"], 2) == 0.52 and round(BV1["p_mixture"], 2) == 0.26
assert round(BV1["p_dispersion"], 2) == 0.24
assert round(100 * NBV["p_zero"], 1) == 52.6 and round(100 * NBV["p_gt_3841"], 2) == 2.17
assert round(100 * NBV["p_gt_2706"], 2) == 4.40 and round(100 * NIN["p_gt_3841"], 2) == 5.01
assert round(TOP10["z"], 2) == 2.29 and round(TOP10["p"], 3) == 0.022 and KS["n_tail"] == 509 and round(KS["z"], 2) == 1.29
assert round(PL["power"]["powerlaw_1000"]["favours_power_law"], 3) == 0.044
FEED_TOTAL = 8


def p3(v):
    return f"{v:.3f}".replace("-", "−")


def stat_row(x, y, name, value, colour, note=None, size=56):
    """A labelled statistic: its name in mono on the left, the value large on the right."""
    out = mono(x, y, name, 24, colour, "start", 600)
    out += txt(970, y + 10, value, size, colour, SANS, 600, "end")
    if note:
        out += mono(x, y + 36, note, 19, MUTED)
    return out


def mini_curve(x0, y0, w, h, lam_lo, lam_hi, ll_lo):
    """Clarke's log-likelihood over lam_lo..lam_hi, scaled into a w x h box, peak at the top."""
    total, n, lam = V1["total"], V1["n"], V1["lam_hat"]
    xs = [lam_lo + (lam_hi - lam_lo) * i / 200 for i in range(201)]
    pts = []
    for v in xs:
        ll = total * math.log(v / lam) - n * (v - lam)
        pts.append((x0 + (v - lam_lo) / (lam_hi - lam_lo) * w, y0 + (ll / ll_lo) * h))
    X = lambda v: x0 + (v - lam_lo) / (lam_hi - lam_lo) * w
    Y = lambda ll: y0 + (ll / ll_lo) * h
    return polyline([(a, b) for a, b in pts if b <= y0 + h], INK, 4), X, Y


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, f"Clarke's {V1['n']} squares of V-1 hits: clustered?", 21, MUTED, "start", 600)
    v += stat_row(110, 650, "likelihood ratio, NB against Poisson", f"{BV1['lr']:.2f}", INK)
    v += stat_row(110, 780, "p against χ²₁", f"{BV1['p_naive']:.2f}", LINK, "the textbook reference")
    v += stat_row(110, 910, "p against ½ χ²₀ + ½ χ²₁", f"{BV1['p_mixture']:.2f}", ACCENT, "the right one: the null α = 0 is the edge")
    v += mono(110, 1044, f"{NBV['R']:,} simulated Poisson data sets: LR = 0 in {100 * NBV['p_zero']:.1f}%,", 18, SOFT)
    v += mono(110, 1072, f"and the χ²₁ test rejects {100 * NBV['p_gt_3841']:.2f}% of true nulls, not 5%", 18, SOFT)
    emit("feed", 1, "boundary-p-value",
         ["On a boundary, the", "χ² p-value doubles."],
         ["Testing Poisson against negative binomial", "puts the null at the edge of the model."],
         v,
         ["When the null sits on a boundary,", "halve the χ² p-value."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, f"l(λ) = {V1['total']} log λ − {V1['n']} λ + const", 26, INK, "start", 600)
    curve, X, Y = mini_curve(110, 600, 400, 300, 0.80, 1.07, -5.5)
    v += curve
    v += line(X(V1["lam_hat"]), Y(0) - 12, X(V1["lam_hat"]), 900, ACCENT, 2, "6,5")
    v += f'<circle cx="{X(V1["lam_hat"]):.1f}" cy="{Y(0):.1f}" r="8" fill="{ACCENT}"/>'
    v += mono(560, 640, "peak: the MLE", 22, MUTED)
    v += mono(560, 684, f"{V1['total']}/{V1['n']} = {V1['lam_hat']:.4f}", 30, ACCENT, "start", 600)
    v += mono(560, 764, "curvature: the information", 22, MUTED)
    v += mono(560, 808, f"{V1['total']}/0.9323² = {V1['obs_info']:.1f}", 30, INK, "start", 600)
    v += mono(560, 888, "standard error", 22, MUTED)
    v += mono(560, 932, f"1/√{V1['obs_info']:.1f} = {V1['se']:.4f}", 30, INK, "start", 600)
    v += mono(110, 950, "rate λ, hits per square", 18, SOFT)
    v += mono(110, 1044, f"Clarke's {V1['n']} squares of south London, {V1['total']} V-1 hits;", 18, SOFT)
    v += mono(110, 1072, "SciPy and statsmodels give the same estimate and standard error", 18, SOFT)
    emit("feed", 2, "one-curve",
         ["One curve gives the", "estimate and its error."],
         ["The log-likelihood of a Poisson rate,", "from Clarke's 1946 count of V-1 hits."],
         v,
         ["The peak is the estimate; how sharply", "it falls is the information."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "the same three tests on two data sets", 21, MUTED, "start", 600)
    v += mono(110, 632, "Clarke: 537 hits, null 0.85", 24, INK, "start", 600)
    v += mono(110, 682, f"Wald {ST['wald']:.2f}", 30, LINK, "start", 600)
    v += mono(410, 682, f"LR {ST['lr']:.2f}", 30, INK, "start", 600)
    v += mono(700, 682, f"score {ST['score']:.2f}", 30, ACCENT, "start", 600)
    v += mono(110, 722, "within 10% of each other", 20, MUTED)
    v += hline(110, 970, 790, RULE_SOLID)
    v += mono(110, 858, "corps XI: 25 deaths in 20 years, null 0.61", 24, INK, "start", 600)
    v += mono(110, 908, f"Wald {XI['wald']:.2f}", 30, LINK, "start", 600)
    v += mono(410, 908, f"LR {XI['lr']:.2f}", 30, INK, "start", 600)
    v += mono(700, 908, f"score {XI['score']:.2f}", 30, ACCENT, "start", 600)
    v += mono(110, 948, "p = 0.010, 0.0014 and 0.00025", 20, MUTED)
    v += mono(110, 1044, "horse-kick deaths from Bortkiewicz's 1898 table; the null is", 18, SOFT)
    v += mono(110, 1072, "the rate of the ten corps he kept, taken as known", 18, SOFT)
    emit("feed", 3, "few-events",
         ["Few events, three", "different answers."],
         ["Wald, likelihood ratio and score measure", "how far a null value sits from the estimate."],
         v,
         ["With small counts the curve is lopsided:", "prefer the likelihood ratio or the score."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "corps XI, one hypothesis, written four ways", 21, MUTED, "start", 600)
    cs = WS["power"]
    val = {c: WS["corps"][min(range(len(cs)), key=lambda q: abs(cs[q] - c))] for c in (-1, 0, 1, 2)}
    rows = [("Wald on the rate λ", val[1]), ("Wald on log λ", val[0]),
            ("Wald on 1/λ, years between deaths", val[-1]), ("Wald on λ²: not significant", val[2])]
    y = 632
    for name, value in rows:
        v += mono(110, y, name, 23, LINK, "start", 600)
        v += txt(970, y + 6, f"{value:.2f}", 44, LINK, SANS, 600, "end")
        y += 84
    v += hline(110, 970, y - 30, RULE_SOLID)
    v += mono(110, y + 20, "likelihood ratio, on any scale", 23, ACCENT, "start", 600)
    v += txt(970, y + 26, f"{XI['lr']:.2f}", 44, ACCENT, SANS, 600, "end")
    v += mono(110, 1072, "5% critical value: 3.84", 18, SOFT)
    emit("feed", 4, "wald-and-scale",
         ["Rewrite the parameter,", "change the Wald test."],
         ["Wald squares a distance on whatever scale", "the parameter happens to be written in."],
         v,
         ["The likelihood ratio does not change.", f"Wald runs from {val[2]:.2f} to {val[-1]:.2f}."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "95% intervals for the negative binomial shape k", 21, MUTED, "start", 600)
    X = lambda k: 110 + (k - 0.4) / 1.1 * 860
    k = NB["k_hat"]
    v += line(X(0.4), 820, X(1.5), 820, RULE_SOLID, 2)
    for t in (0.4, 0.6, 0.8, 1.0, 1.2, 1.4):
        v += line(X(t), 812, X(t), 828, RULE_SOLID, 2) + mono(X(t), 858, f"{t:.1f}", 18, SOFT, "middle")
    lo, hi = NB["intervals_k"]["profile"]
    v += line(X(lo), 660, X(hi), 660, ACCENT, 10) + f'<circle cx="{X(k):.1f}" cy="660" r="9" fill="{PAPER}" stroke="{ACCENT}" stroke-width="4"/>'
    v += mono(X(lo), 628, f"profile likelihood: {lo:.3f} to {hi:.3f}", 22, ACCENT, "start", 600)
    wlo, whi = NB["intervals_k"]["wald_obs"]
    v += line(X(wlo), 750, X(whi), 750, LINK, 10) + f'<circle cx="{X(k):.1f}" cy="750" r="9" fill="{PAPER}" stroke="{LINK}" stroke-width="4"/>'
    v += mono(X(wlo), 718, f"Wald, k̂ ± 1.96 SE: {wlo:.3f} to {whi:.3f}", 22, LINK, "start", 600)
    ks = NB["k_sampling"]
    v += mono(110, 940, f"refitted on {ks['R']:,} simulated data sets, k̂ falls", 22, INK)
    v += mono(110, 976, f"above the Wald interval in {100 * ks['above_wald']:.2f}%, below it in {100 * ks['below_wald']:.2f}%", 22, INK)
    v += mono(110, 1072, "Greenwood and Yule's 647 munition workers, k̂ = 0.865", 18, SOFT)
    emit("feed", 5, "lopsided-interval",
         ["Skewed estimate,", "lopsided interval."],
         ["The likelihood falls slowly toward large k,", "so the honest interval reaches farther there."],
         v,
         ["Use profile-likelihood intervals", "for dispersions and variances."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, f"{NBV['R']:,} Poisson data sets shaped like Clarke's", 21, MUTED, "start", 600)
    rows = [(f"{100 * NBV['p_zero']:.1f}%", "have a likelihood ratio of exactly 0", ACCENT),
            (f"{100 * NBV['p_gt_3841']:.2f}%", "rejected by the χ²₁ test at 3.84", LINK),
            (f"{100 * NBV['p_gt_2706']:.2f}%", "rejected by the mixture's test at 2.71", INK)]
    y = 670
    for value, what, colour in rows:
        v += txt(110, y, value, 64, colour, SANS, 600)
        v += mono(400, y - 8, what, 22, colour, "start", 600)
        y += 116
    v += mono(110, 1044, f"inside the parameter space the χ²₁ test rejects {100 * NIN['p_gt_3841']:.2f}%,", 18, SOFT)
    v += mono(110, 1072, "as Wilks's theorem promises: the boundary is the difference", 18, SOFT)
    emit("feed", 6, "half-are-zero",
         ["Half the likelihood", "ratios are zero."],
         ["Under a Poisson the fitted dispersion lands", "on its boundary, α = 0, about half the time."],
         v,
         ["On a boundary the reference is", "½ χ²₀ + ½ χ²₁, not χ²₁."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "Vuong's normalised likelihood ratio, lognormal over power law", 21, MUTED, "start", 600)
    rows = [(f"top 1,000 values", f"{TOP10['z']:.2f}", f"p = {TOP10['p']:.3f}: lognormal", ACCENT),
            (f"CSN's threshold, {KS['n_tail']} values", f"{KS['z']:.2f}", f"p = {KS['p']:.2f}: cannot tell", INK)]
    y = 650
    for name, value, note, colour in rows:
        v += mono(110, y, name, 24, colour, "start", 600)
        v += txt(970, y + 10, value, 56, colour, SANS, 600, "end")
        v += mono(110, y + 38, note, 21, MUTED)
        y += 140
    pw = PL["power"]
    v += mono(110, 950, f"a true power law, 1,000 values: decided for it", 21, INK)
    v += mono(110, 984, f"in only {100 * pw['powerlaw_1000']['favours_power_law']:.1f}% of {pw['powerlaw_1000']['R']:,} samples", 21, INK)
    v += mono(110, 1072, "the first part's lognormal sample, regenerated exactly", 18, SOFT)
    emit("feed", 7, "power-law-or-lognormal",
         ["Power law or lognormal?", "Ask the likelihood."],
         ["A lognormal's tail can look straight", "on log–log axes; the likelihood can tell."],
         v,
         ["The test can rule a power law out,", "but it rarely confirms one."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("MLE ± 1/√information", f"Clarke: {V1['lam_hat']:.4f} ± {V1['se']:.4f} hits per square", INK),
             ("Wald · score · likelihood ratio", "agree with 537 hits, not with 25", INK),
             ("profile-likelihood intervals", f"k: {p3(NB['intervals_k']['profile'][0])} to {p3(NB['intervals_k']['profile'][1])}, not Wald's symmetric one", INK),
             ("the boundary", f"χ²₁ rejects {100 * NBV['p_gt_3841']:.2f}%: halve its p-value", ACCENT)]
    y = 556
    for head, a, colour in items:
        v += txt(110, y, head, 30, colour, SANS, 600)
        v += mono(110, y + 42, a, 21, INK if colour == INK else colour)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Likelihood, and", "where χ² fails."],
         ["Every number measured by a seeded lab", "you can rerun in about 100 seconds."],
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
