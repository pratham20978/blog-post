#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Distributions as Generative Stories: Let the
Process Pick".

Statistics for Data Scientists, part 1. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Image Processing by Hand, part 14, so the new series starts from the
house layout. Every number on a card comes from the lab's capture, ../lab/captures.json, and the asserts
below hold each one to the article. Colours follow the figures: blue marks observed counts and the
Poisson part of the variance, tangerine the one departure each card is about.

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
CANONICAL = "canery.in/blogs/distributions-as-generative-stories"
FOOTER = "DISTRIBUTIONS AS GENERATIVE STORIES · CANERY.IN"

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
W, A, T, L = CAP["worked"], CAP["accidents"], CAP["tails"], CAP["loglog"]
CL = W["clarke"]
OBS_C, POIS_C = CL["observed"], CL["expected_poisson"]
OBS_G, POIS_G, NB_G = A["data"]["observed"], A["poisson"]["expected"], A["negative_binomial"]["expected"]
CONT_G = A["contagion_simulation"]["expected_counts"]
MU, K = A["data"]["mean"], A["negative_binomial"]["k"]
R4 = T["two_sided_tail"]["4"]
assert OBS_C == [229, 211, 93, 35, 7, 1] and [round(v, 1) for v in POIS_C] == [226.7, 211.4, 98.5, 30.6, 7.1, 1.6]
assert round(CL["dispersion_index"], 2) == 1.04 and round(CL["chi2"], 2) == 1.17 and round(CL["chi2_p"], 2) == 0.88
assert OBS_G == [447, 132, 42, 21, 3, 2] and round(K, 3) == 0.955 and round(A["data"]["dispersion_index"], 2) == 1.49
assert [round(v, 1) for v in NB_G] == [442.9, 138.5, 44.4, 14.3, 4.6, 2.2]
assert [round(v, 1) for v in CONT_G] == [442.8, 138.5, 44.5, 14.4, 4.7, 2.2]
assert round(R4["ratio"], 1) == 56.4 and round(T["simulation"]["t"]["n100_exact_none"] * 100) == 70
assert round(L["lognormal"]["r2"], 3) == 0.991
FEED_TOTAL, STORY_TOTAL = 8, 4
CLASSES = ["0", "1", "2", "3", "4", "5+"]


def f1(v):
    return f"{v:,.1f}"


def row(x, y, head, values, size, fill=INK, head_fill=SOFT, step=118, weight=600, fmt=str):
    s = mono(x, y, head, size - 2, head_fill, "start", 500)
    for i, v in enumerate(values):
        s += mono(x + 250 + i * step, y, fmt(v), size, fill, "end", weight)
    return s


def variance_bar(x, y, w, h, scale_max):
    """The negative binomial's variance as two stacked blocks: Poisson noise and the spread of rates."""
    pois, spread = MU, MU * MU / K
    hp, hs = h * pois / scale_max, h * spread / scale_max
    s = rect(x, y + h - hp, w, hp, LINK, LINK, 2, op=0.22)
    s += rect(x, y + h - hp - hs, w, hs, ACCENT, ACCENT, 2, op=0.22)
    return s, (pois, spread)


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    steps = [("each bomb: one square of 576, independently", MUTED),
             ("→ a square's count: Binomial(537, 1/576)", INK),
             (f"→ many rare chances: Poisson, λ = 537/576 = {CL['lambda']:.3f}", INK)]
    y = 562
    for s_, c in steps:
        v += mono(110, y, s_, 22, c, "start", 600 if c == INK else 400)
        y += 46
    v += hline(110, 970, 718)
    v += row(110, 780, "hits per square", CLASSES, 22, SOFT, weight=500)
    v += row(110, 836, "observed", OBS_C, 26, LINK)
    v += row(110, 892, "Poisson", POIS_C, 26, INK, fmt=f1)
    v += mono(110, 978, f"variance {CL['variance']:.3f} · mean {CL['mean']:.3f} · "
                        f"chi-square {CL['chi2']:.2f}, P = {CL['chi2_p']:.2f}", 20, MUTED)
    v += mono(110, 1030, "R. D. Clarke, 1946: 576 squares of a quarter square kilometre", 17, SOFT)
    v += mono(110, 1062, "in south London; the 5+ square held the remaining 7 bombs", 17, SOFT)
    emit("feed", 1, "let-the-process-pick",
         ["Let the process pick", "the distribution."],
         ["537 flying bombs on 576 squares: the story", "predicts the table before you see it."],
         v,
         ["A histogram can test a story.", "It cannot choose one."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "hanging rootogram: √observed hung from √expected", 20, MUTED, "start", 600)
    base, unit, x0, step = 900, 18.0, 160, 140
    v += hline(120, 960, base, MUTED, 2)
    for d in (-1, 1):
        v += hline(120, 960, base - d * unit * 1, SOFT, 2, "10,7")
    v += mono(966, base - unit + 6, "+1", 17, SOFT)
    v += mono(966, base + unit + 6, "−1", 17, SOFT)
    pts = []
    for j, (o, e) in enumerate(zip(OBS_C, POIS_C)):
        top = base - math.sqrt(e) * unit
        bot = top + math.sqrt(o) * unit
        v += rect(x0 + j * step - 46, top, 92, bot - top, LINK, LINK, 2, op=0.22)
        v += mono(x0 + j * step, base + 66, CLASSES[j], 20, SOFT, "middle")
        pts.append((x0 + j * step, top))
    v += polyline(pts, INK, 3)
    for x, y in pts:
        v += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{INK}"/>'
    v += mono(110, 1050, f"variance / mean = {CL['dispersion_index']:.2f}; clustering would push it above 1", 20,
              INK, "start", 600)
    v += mono(110, 1090, "every bar ends inside Tukey's ±1 lines", 18, SOFT)
    emit("feed", 2, "variance-equals-mean",
         ["Variance = mean:", "the Poisson's signature."],
         ["Clarke tested whether the flying bombs", "clustered. His squares gave it no support."],
         v,
         ["The story made a prediction,", "and the data had a chance to break it."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    b2, b8 = W["bortkiewicz_200"], W["bortkiewicz_280"]
    cols = [(110, "the well-known 200 corps-years", "10 corps, 1875–1894", b2, LINK),
            (560, "all 280 corps-years", "14 corps, 1875–1894", b8, ACCENT)]
    for x, head, sub, d, c in cols:
        v += txt(x, 570, head, 26, INK, SANS, 600)
        v += mono(x, 606, sub, 18, SOFT)
        v += mono(x, 676, f"mean      {d['mean']:.2f}", 26, INK, "start", 600)
        v += mono(x, 726, f"variance  {d['variance']:.3f}", 26, INK, "start", 600)
        v += mono(x, 776, f"ratio     {d['dispersion_index']:.2f}", 26, c, "start", 600)
    v += hline(110, 970, 830)
    v += mono(110, 884, "left out of the 200: the Guard, with 40 cavalry", 19, MUTED)
    v += mono(110, 918, "squadrons; XI, with three divisions; I and VI, with", 19, MUTED)
    v += mono(110, 952, "30 and 25 squadrons, against a norm of 20", 19, MUTED)
    v += mono(110, 1030, "Clarke, too, chose an area of nearly constant density", 19, INK, "start", 600)
    v += mono(110, 1066, "Bortkiewicz 1898, §12; Clarke 1946", 16, SOFT)
    emit("feed", 3, "read-the-footnote",
         ["Read the", "footnote."],
         ["Bortkiewicz's horse kicks fit the Poisson", "after four corps were set aside."],
         v,
         ["The Poisson needs one common rate. Both", "classic fits met it partly by selection."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += row(110, 560, "accidents", CLASSES, 22, SOFT, weight=500)
    v += row(110, 614, "observed", OBS_G, 25, LINK)
    v += row(110, 664, "Poisson", POIS_G, 25, MUTED, fmt=f1)
    v += row(110, 714, f"neg. binom.", NB_G, 25, ACCENT, fmt=f1)
    v += mono(110, 760, f"k = {K:.3f} by moments; chi-square {A['poisson']['chi2']:.1f} → "
                        f"{A['negative_binomial']['chi2']:.2f}", 19, MUTED)
    bar, (p, s_) = variance_bar(140, 800, 120, 260, 0.75)
    v += bar
    v += mono(300, 826, f"{MU + MU * MU / K:.3f}  variance of a woman's count", 22, INK, "start", 600)
    v += mono(300, 868, f"{s_:.3f}  μ²/k: rates that differ", 22, ACCENT, "start", 600)
    v += mono(300, 988, f"{p:.3f}  μ: each woman's Poisson noise", 22, LINK, "start", 600)
    v += mono(300, 1060, "647 women on high-explosive shells, five weeks", 17, SOFT)
    emit("feed", 4, "rates-that-differ",
         ["Rates that differ make", "a negative binomial."],
         ["Give each worker her own accident rate,", "drawn from a gamma, and recount."],
         v,
         ["Under that story, the extra variance", "is the spread of the women's rates."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    pr, co = A["proneness_simulation"], A["contagion_simulation"]
    v += txt(110, 566, "proneness", 28, LINK, SANS, 600)
    v += mono(110, 600, "each woman her own rate", 18, SOFT)
    v += txt(560, 566, "contagion", 28, ACCENT, SANS, 600)
    v += mono(560, 600, f"start at {co['start_rate']:.3f}, +{co['rate_step']:.3f} an accident", 18, SOFT)
    v += hline(110, 970, 636)
    v += mono(110, 680, "first five weeks: women with 0 to 5+ accidents", 19, MUTED)
    v += mono(110, 724, "  ".join(f1(x) for x in NB_G[:4]) + " …", 22, LINK, "start", 600)
    v += mono(560, 724, "  ".join(f1(x) for x in CONT_G[:4]) + " …", 22, ACCENT, "start", 600)
    v += mono(110, 770, "proneness exact, contagion simulated: the same distribution", 18, SOFT)
    v += hline(110, 970, 812)
    v += mono(110, 860, "second five weeks: mean count", 19, MUTED)
    v += txt(110, 950, f"{pr['period2_mean']:.3f}", 72, LINK, SANS, 600)
    v += txt(560, 950, f"{co['period2_mean']:.3f}", 72, ACCENT, SANS, 600)
    v += mono(110, 1000, "rates unchanged", 18, SOFT)
    v += mono(560, 1000, "accidents have accumulated", 18, SOFT)
    v += mono(110, 1066, f"lab simulation: R = {pr['R']:,} and {co['R']:,} factories of 647", 16, SOFT)
    emit("feed", 5, "same-counts-two-stories",
         ["Same counts,", "two stories."],
         ["A rate per person, or accidents that raise", "the chance of the next one."],
         v,
         ["One period cannot tell them apart.", "A second period can."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "beyond 4 standard deviations", 20, MUTED, "start", 600)
    v += txt(110, 650, f"{R4['t'] * 100:.3f}%", 64, ACCENT, SANS, 600)
    v += mono(110, 690, "unit-variance t₅", 19, ACCENT)
    v += txt(560, 650, f"{R4['normal'] * 100:.4f}%", 64, INK, SANS, 600)
    v += mono(560, 690, "normal", 19, INK)
    v += hline(110, 970, 730)
    y = 790
    for x in ("3", "4", "5"):
        r = T["two_sided_tail"][x]["ratio"]
        w = 120 * math.log10(r)
        v += mono(110, y + 8, f"beyond {x}", 20, SOFT)
        v += rect(270, y - 22, w, 36, ACCENT if x == "4" else LINK, op=0.85 if x == "4" else 0.35)
        lab = f"×{r:,.1f}" if r < 100 else f"×{r:,.0f}"
        v += mono(270 + w + 16, y + 8, lab, 22, ACCENT if x == "4" else INK, "start", 600)
        y += 60
    v += mono(110, 1010, "bar length: log of the ratio of tail probabilities", 16, SOFT)
    v += mono(110, 1060, f"peaks: t₅ {T['peak_t']:.3f}, normal {T['peak_normal']:.3f} · samples of 100: "
                         f"{T['simulation']['t']['n100_exact_none']:.0%} show nothing beyond 4", 17, MUTED)
    emit("feed", 6, "56-times-the-tail",
         ["Same variance.", "56 times the tail."],
         ["A t with 5 degrees of freedom, scaled", "to variance 1, against the normal."],
         v,
         ["The tail that sets your risk is the", "part a small sample usually misses."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    ln = L["lognormal"]
    x0, y0, w, h = 130, 540, 520, 380
    lx = lambda x: x0 + (math.log10(x) + 4) / 9 * w
    ly = lambda y: y0 + h - (math.log10(y) + 4) / 4 * h
    v += line(x0, y0 + h, x0 + w, y0 + h, RULE_SOLID, 2) + line(x0, y0, x0, y0 + h, RULE_SOLID, 2)
    v += rect(lx(ln["threshold"]), y0, x0 + w - lx(ln["threshold"]), h, "rgba(45,49,66,0.05)")
    pts = [(lx(x), ly(y)) for x, y in zip(ln["ccdf_x"], ln["ccdf_y"]) if 1e-4 <= x <= 1e5 and y >= 1e-4]
    v += polyline(pts, INK, 3)
    xa, xb = ln["threshold"], max(ln["ccdf_x"])
    fit = [(lx(x), ly(10 ** (ln["intercept"] + ln["slope"] * math.log10(x)))) for x in (xa, xb)]
    v += polyline(fit, ACCENT, 5)
    v += mono(x0, y0 + h + 34, "x, log scale →", 17, SOFT)
    v += mono(x0, y0 - 14, "P(X ≥ x), log scale", 17, SOFT)
    v += mono(690, 590, "top 10% of 10,000", 19, MUTED)
    v += mono(690, 622, "lognormal draws, σ = 2.5", 19, MUTED)
    v += mono(690, 676, f"R² = {ln['r2']:.3f}", 28, ACCENT, "start", 600)
    v += mono(690, 716, f"slope {ln['slope']:.3f}".replace("-", "−"), 22, INK, "start", 600)
    v += mono(690, 776, "read as a power law:", 18, MUTED)
    v += mono(690, 806, "an infinite mean", 18, MUTED)
    v += mono(690, 856, "true mean:", 18, MUTED)
    v += mono(690, 886, f"e^(σ²/2) = {math.exp(ln['sigma'] ** 2 / 2):.1f}", 22, INK, "start", 600)
    v += mono(110, 1066, "add a floor to the same growth and the tail becomes a true power law", 17, SOFT)
    emit("feed", 7, "straight-is-not-a-power-law",
         ["A straight log–log", "line is not a power law."],
         ["A lognormal sample draws a straight tail,", "with a mean the line says cannot exist."],
         v,
         ["The mechanism, such as a floor under growth,", "decides. The plot cannot."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("Poisson", "537 bombs, 576 squares", f"variance / mean = {CL['dispersion_index']:.2f}"),
             ("negative binomial", "647 women, rates that differ",
              f"{MU + MU * MU / K:.3f} = {MU:.3f} + {MU * MU / K:.3f}"),
             ("Student t₅", "a normal whose variance varies", f"×{R4['ratio']:.0f} beyond 4 sd"),
             ("power law or lognormal", "the mechanism decides", f"R² {L['lognormal']['r2']:.3f} proves nothing")]
    y = 556
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "negative binomial" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 136
    emit("feed", 8, "read-the-article",
         ["Distributions as", "generative stories."],
         ["Each family derived from a process, then", "tested on real tables or by simulation."],
         v,
         ["The full walk-through, every computed", "number rerun by a script you can download."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 870, "squares with 0 to 5+ hits", 24, MUTED, "start", 600)
    y = 950
    for i, (o, e) in enumerate(zip(OBS_C, POIS_C)):
        v += mono(130, y, CLASSES[i], 28, SOFT, "start", 500)
        v += mono(450, y, f"{o}", 34, LINK, "end", 600)
        v += mono(760, y, f1(e), 34, INK, "end", 600)
        y += 66
    v += mono(450, 1390, "observed", 22, LINK, "end")
    v += mono(760, 1390, "Poisson", 22, INK, "end")
    emit("story", 1, "let-the-process-pick",
         ["Let the process", "pick."],
         ["537 flying bombs, 576 squares,", "chance 1/576 each."],
         v,
         ["The story predicts every class", "of the table."],
         STORY_TOTAL)


def story_02():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    bar, (p, s_) = variance_bar(170, 860, 200, 500, 0.75)
    v += bar
    v += mono(430, 940, f"{s_:.3f}", 44, ACCENT, "start", 600)
    v += mono(430, 984, "rates that differ", 26, ACCENT)
    v += mono(430, 1180, f"{p:.3f}", 44, LINK, "start", 600)
    v += mono(430, 1224, "Poisson noise", 26, LINK)
    v += mono(430, 1330, f"= {MU + MU * MU / K:.3f} variance", 28, INK, "start", 600)
    emit("story", 2, "rates-that-differ",
         ["1.49 times", "the mean."],
         ["Greenwood and Yule's 647 women:", "their accident counts' variance."],
         v,
         ["Rates drawn from a gamma:", "the counts go negative binomial."],
         STORY_TOTAL)


def story_03():
    v = box(72, 790, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 870, "beyond 4 standard deviations", 26, MUTED, "start", 600)
    v += txt(110, 1010, f"{R4['t'] * 100:.3f}%", 96, ACCENT, SANS, 600)
    v += mono(110, 1074, "unit-variance t₅", 26, ACCENT)
    v += txt(110, 1220, f"{R4['normal'] * 100:.4f}%", 96, INK, SANS, 600)
    v += mono(110, 1284, "normal", 26, INK)
    v += mono(110, 1370, "a t with 5 degrees of freedom, scaled to variance 1", 22, SOFT)
    emit("story", 3, "56-times",
         [f"{R4['ratio']:.0f} times", "the tail."],
         ["Same variance, same mean,", "different tails."],
         v,
         [f"{T['simulation']['t']['n100_exact_none']:.0%} of t₅ samples of 100", "show nothing beyond 4."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["write how each number was made",
             "derive the family from the story",
             "test what the story predicts",
             "a straight log–log line is not a test"]
    y = 900
    for i, s_ in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s_, 32, INK, SANS, 600 if i == 1 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["Distributions as", "generative stories."],
         ["Poisson, negative binomial, t and", "power law, each from its process."],
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
