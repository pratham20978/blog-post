#!/usr/bin/env python3
"""Build the finished Canery feed sources for "MCMC You Can Trust: Metropolis by Hand, R-hat and ESS".

Statistics for Data Scientists, part 12. The shell (lockup reading "canery.in", rule, serif title, deck,
takeaway, footer) is copied from Part 11, so the series renders as one publication. Every number on a card
comes from the lab's capture, ../lab/captures.json, and the asserts below hold each one to the article.
Colours follow the figures: tangerine marks the exact answer and the thresholds, blue the chain's estimate,
ink the rest. Geist Mono has no superscript digits or combining hat, so mono text says "R-hat" and values
with exponents are set in Geist. Feed cards only: the owner asked for no Story frames (2026-10-30); the
shell keeps its Story layout.

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
CANONICAL = "canery.in/blogs/mcmc-diagnostics-metropolis-nuts"
FOOTER = "MCMC YOU CAN TRUST · CANERY.IN"

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

PF, TU, NB, DG, MC, RH, BM, NU = (CAP[k] for k in ("pfizer", "tuning", "nb", "diagnostics", "mcse", "rhat", "bimodal",
                                                   "nuts"))
FEED_TOTAL = 8


def pc(v, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it; true minus sign."""
    return f"{(Decimal(repr(float(v))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}%".replace("-", "−")


def hv(v, nd=4):
    return f"{Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)}".replace("-", "−")


EX, ES, PD = PF["exact"], PF["estimates"], PF["diagnostics"]
TR, SW = TU["traces"], TU["sweep"]
ST = MC["steps"]
C1000 = RH["constructed"]["1000"]
CR, RU = C1000["crossings"], RH["threshold"]["rules"]
OM, DI, LJ = BM["one_mode"], BM["dispersed"], BM["long_jumps"]
PIECES = DG["pieces"]
assert (pc(EX["ve_q025"], 2), pc(EX["ve_q975"], 2), pc(ES["q025"]["value"], 2), pc(ES["q975"]["value"], 2)) == \
    ("90.32%", "97.62%", "90.47%", "97.52%")
assert (hv(ES["q025"]["z"], 2), hv(ES["q975"]["z"], 2)) == ("1.20", "−2.61")
assert [r["accept"] for r in PF["first_iterations"]].count(True) == 2
assert [pc(TR[k]["acceptance"]) for k in ("0.002", "0.04", "1.0")] == ["95.5%", "42.8%", "2.2%"]
assert [round(TR[k]["ess_mean"]) for k in ("0.002", "0.04", "1.0")] == [46, 3638, 296]
assert (pc(SW["1d"]["best_acceptance"]), hv(SW["1d"]["best_efficiency"], 3)) == ("42.1%", "0.207")
assert (round(PIECES["tau"], 3), round(PIECES["ess_mean"])) == (4.961, 4032)
assert [pc(ST[k]["naive"]) for k in ("0.008", "0.04")] == ["29.8%", "65.1%"]
assert [pc(ST[k]["ess_based"]) for k in ("0.008", "0.04")] == ["93.2%", "94.9%"]
assert (hv(CR["shift_split_1.01"], 2), hv(CR["shift_split_1.1"], 2), hv(CR["scale_folded_1.01"], 2),
        hv(CR["scale_folded_1.1"], 2)) == ("0.31", "0.99", "0.76", "0.36")
assert (pc(RU["rank<1.1"]["share_off_1pt"]), RU["rank<1.01 & ESS>400"]["share_off_1pt"]) == ("10.6%", 0.0)
assert (hv(OM["diagnostics"]["rank"]), round(OM["diagnostics"]["ess_bulk"]), hv(OM["mean"], 3), OM["p_right"]) == \
    ("1.0006", 4295, "0.006", 0.0)
assert (hv(DI["diagnostics"]["rank"], 2), hv(LJ["p_right"], 3)) == ("1.60", "0.301")
NUM, NUK = NU["params"]["mu"], NU["params"]["k"]
# The capture keeps six significant digits, so k's R-hat is stored as 1.00145; the lab printed 1.0014 from full
# precision, and the article quotes the lab's print, so these two are formatted as the lab formats them.
RH_NUTS = (f"{NUM['mine']['rank']:.4f}", f"{NUK['mine']['rank']:.4f}")
assert RH_NUTS == ("1.0005", "1.0014")
assert (round(NUM["mine"]["ess_bulk"]), round(NUK["mine"]["ess_bulk"]), NU["divergences"]) == (3769, 3943, 0)
assert (int(NUM["arviz"]["ess_tail_default_xarray"]), round(NUM["mine"]["ess_tail"])) == (2637, 2945)


def stat_row(x, y, name, value, colour, note=None, size=48):
    """A labelled statistic: its name in mono on the left, the value large on the right."""
    out = mono(x, y, name, 23, colour, "start", 600)
    out += txt(970, y + 8, value, size, colour, SANS, 600, "end")
    if note:
        out += mono(x, y + 34, note, 19, MUTED)
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "random-walk Metropolis, one step:", 21, MUTED, "start", 600)
    steps = ["1  propose θ* = θ + s·z,  z ~ N(0, 1)", "2  r = p(θ*) / p(θ): the constant cancels",
             "3  accept if u < r,  u ~ Uniform(0, 1)", "4  record the state, moved or not"]
    for i, t in enumerate(steps):
        v += mono(110, 600 + i * 40, t, 21, INK)
    v += hline(110, 970, 780)
    v += mono(110, 830, "Part 11's trial posterior, beta(8.700102, 163)", 20, MUTED, "start", 600)
    v += stat_row(110, 900, "exact 95% interval", f"{pc(EX['ve_q025'], 2)} – {pc(EX['ve_q975'], 2)}", ACCENT, size=40)
    v += stat_row(110, 1000, "20,000 draws", f"{pc(ES['q025']['value'], 2)} – {pc(ES['q975']['value'], 2)}", LINK,
                  f"z = +{hv(ES['q025']['z'], 2)} and {hv(ES['q975']['z'], 2)} Monte Carlo standard errors", size=40)
    emit("feed", 1, "metropolis-by-hand",
         ["Metropolis,", "by hand."],
         ["Twenty lines of NumPy, run on a vaccine", "trial's posterior whose answer is known."],
         v,
         ["Both ends land within 3 Monte Carlo", "standard errors of the closed form."],
         FEED_TOTAL)


def feed_02():
    rows = PF["first_iterations"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    cols = (110, 170, 320, 470, 620, 760)          # SVG collapses repeated spaces: every column has its own x
    for x, head in zip(cols, ("t", "θ", "θ*", "r", "u", "decision")):
        v += mono(x, 548, head, 20, MUTED, "start", 600)
    v += hline(110, 970, 566)
    for i, r in enumerate(rows):
        rr = f"{r['r']:.3g}" if r["r"] >= 0.001 else "4.2e-6"
        dec = "accept" if r["accept"] else "stay at θ"
        col = LINK if r["accept"] else INK
        for x, val in zip(cols, (f"{r['t']}", f"{r['theta']:.4f}", f"{r['proposal']:.4f}", rr, f"{r['u']:.3f}", dec)):
            v += mono(x, 612 + i * 58, val, 21, col)
    emit("feed", 2, "a-rejection-is-a-draw",
         ["A rejection", "is a draw."],
         ["Eight iterations from θ = 0.10 with step 0.04:", "two proposals accepted, six rejected."],
         v,
         ["Five rejections leave five copies of 0.0533", "in the record, and they belong there."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "four chains × 5,000 draws, the trial's posterior", 21, MUTED, "start", 600)
    y = 640
    top = max(TR[k]["ess_mean"] for k in TR)
    for k, name in (("0.002", "step 0.002: crawls"), ("0.04", "step 0.04: mixes"), ("1.0", "step 1.0: sticks")):
        t = TR[k]
        col = ACCENT if k == "0.04" else INK
        v += mono(110, y, name, 23, col, "start", 600)
        v += mono(110, y + 36, f"accepts {pc(t['acceptance'])}", 20, MUTED)
        w = max(4, 330 * t["ess_mean"] / top)       # leaves room for the label at the longest bar
        v += rect(440, y + 6, w, 30, col, op=0.8)
        v += txt(440 + w + 14, y + 30, f"ESS {t['ess_mean']:,.0f}", 30, col, SANS, 600)
        y += 140
    emit("feed", 3, "tune-the-step",
         ["Tune the step,", "not the answer."],
         ["Too small and almost every move is accepted", "but goes nowhere; too large and almost every", "move is refused."],
         v,
         [f"Efficiency peaked at {pc(SW['1d']['best_acceptance'], 0)} acceptance and stayed", "within 20% of it from 27% to 51%."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, f"τ = 1 + 2 Σ ρ_t = {PIECES['tau']:.3f};  ESS = 20,000 / {PIECES['tau']:.3f} = {PIECES['ess_mean']:,.0f}", 21, INK, "start", 600)
    v += hline(110, 970, 580)
    v += mono(110, 632, f"{MC['reps']:,} runs: how often estimate ± 1.96 SE covers the truth", 20, MUTED, "start", 600)
    for i, (k, lab) in enumerate((("0.04", "step 0.04"), ("0.008", "step 0.008, slow"))):
        y = 720 + i * 190
        st = ST[k]
        v += mono(110, y, lab, 23, INK, "start", 600)
        v += stat_row(110, y + 60, "naive SE = SD/√S", pc(st["naive"]), INK, size=42)
        v += stat_row(110, y + 120, "MCSE = SD/√ESS", pc(st["ess_based"]), ACCENT, size=42)
    emit("feed", 4, "20000-draws-worth-4032",
         ["20,000 draws,", "worth 4,032."],
         ["Consecutive draws are correlated, so they carry", "less information than independent ones."],
         v,
         ["The naive standard error was 2.2 times too", "small. Report SD/√ESS beside every estimate."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "4 chains of normal draws, one altered; median of 400 runs", 20, MUTED, "start", 600)
    v += stat_row(110, 634, "one chain shifted: split R-hat", f"{hv(CR['shift_split_1.1'], 2)} SD", INK,
                  f"needed to reach 1.1; 1.01 is reached at {hv(CR['shift_split_1.01'], 2)} SD", size=42)
    v += stat_row(110, 766, "one chain narrow: folded R-hat", f"{hv(CR['scale_folded_1.1'], 2)} × SD", INK,
                  f"needed to reach 1.1; 1.01 is reached at {hv(CR['scale_folded_1.01'], 2)}", size=42)
    v += hline(110, 970, 846)
    v += mono(110, 898, "3,200 short runs on the trial's posterior:", 20, MUTED, "start", 600)
    v += stat_row(110, 960, "R-hat < 1.1: lower limit off > 1 point", pc(RU["rank<1.1"]["share_off_1pt"]), INK, size=40)
    v += stat_row(110, 1050, "R-hat < 1.01, ESS > 400", pc(RU["rank<1.01 & ESS>400"]["share_off_1pt"]), ACCENT, size=40)
    emit("feed", 5, "what-1-1-lets-through",
         ["What R-hat 1.1", "lets through."],
         ["The old cutoff passes a chain shifted by", "almost a whole posterior standard deviation."],
         v,
         ["Use R-hat below 1.01, with bulk and", "tail ESS above 400."],
         FEED_TOTAL)


def feed_06():
    d = OM["diagnostics"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "0.7 N(0, 1) + 0.3 N(16, 1); four chains started near 0", 20, MUTED, "start", 600)
    v += stat_row(110, 636, "R-hat", hv(d["rank"]), INK, "below 1.01: passes", size=44)
    v += stat_row(110, 746, "bulk ESS", f"{d['ess_bulk']:,.0f}", INK, "above 400: passes", size=44)
    v += hline(110, 970, 806)
    v += stat_row(110, 870, "mean", f"{hv(OM['mean'], 3)}", LINK, f"exact {BM['exact']['mean']:g}", size=44)
    v += stat_row(110, 980, "P(θ > 8)", f"{OM['p_right']:.1f}", LINK, f"exact {BM['exact']['p_right']:g}", size=44)
    emit("feed", 6, "the-mode-no-chain-visited",
         ["Perfect diagnostics,", "30% missing."],
         ["A posterior with two modes; none of 24,000", "iterations crossed the valley."],
         v,
         ["No within- or between-chain statistic can", "see a mode that no chain visited."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 552, "PyMC, NUTS: Greenwood and Yule's accidents, 4 × 1,000 draws", 20, MUTED, "start", 600)
    v += stat_row(110, 636, "R-hat, mu and k", f"{RH_NUTS[0]} / {RH_NUTS[1]}", INK, size=40)
    v += stat_row(110, 716, "bulk ESS of 4,000", f"{NUM['mine']['ess_bulk']:,.0f} / {NUK['mine']['ess_bulk']:,.0f}", INK, size=40)
    v += stat_row(110, 796, "divergences", f"{NU['divergences']}", INK, f"{NU['mean_n_steps']:.2f} leapfrog steps per draw", size=40)
    v += hline(110, 970, 870)
    v += mono(110, 920, "tail ESS of mu, two definitions:", 20, MUTED, "start", 600)
    v += stat_row(110, 990, "ArviZ summary: 11% / 89%", f"{int(NUM['arviz']['ess_tail_default_xarray']):,}", INK, size=40)
    v += stat_row(110, 1070, "Vehtari et al.: 5% / 95%", f"{NUM['mine']['ess_tail']:,.0f}", ACCENT, size=40)
    emit("feed", 7, "reading-nuts-in-pymc",
         ["Reading NUTS", "in PyMC."],
         ["The production sampler, read through its", "diagnostics and checked against a grid."],
         v,
         ["ArviZ's summary defaults to an 89% interval", "and an 11%/89% tail ESS. Know the defaults."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("by hand", f"20,000 draws: VE {pc(ES['q025']['value'], 2)} to {pc(ES['q975']['value'], 2)}", INK),
             ("dependence", f"τ = {PIECES['tau']:.3f}: 20,000 draws worth {PIECES['ess_mean']:,.0f}", INK),
             ("standard errors", f"naive covers {pc(ST['0.04']['naive'])}, SD/√ESS {pc(ST['0.04']['ess_based'])}", LINK),
             ("thresholds", f"1.1 passes shifts up to {hv(CR['shift_split_1.1'], 2)} SD; use 1.01, ESS > 400", ACCENT),
             ("blind spot", f"one mode: R-hat {hv(OM['diagnostics']['rank'])}, 30% of the posterior missing", ACCENT)]
    y = 552
    for head, a, colour in items:
        v += txt(110, y, head, 28, colour, SANS, 600)
        v += mono(110, y + 40, a, 21, INK if colour == INK else colour)
        y += 112
    emit("feed", 8, "read-the-article",
         ["MCMC you", "can trust."],
         ["A sampler by hand, every diagnostic by hand,", "matched to ArviZ, and every guarantee measured."],
         v,
         ["The full walk-through, with the lab, the", "notebook and PyMC's output read line by line."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
