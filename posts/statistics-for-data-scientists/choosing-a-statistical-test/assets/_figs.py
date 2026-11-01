#!/usr/bin/env python3
"""Figures 01, 02 and 04-11 for choosing-a-statistical-test (Figure 03 is Mermaid: _mermaid.py).

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/choosing.py, from the lab's data
files (Figures 1 and 10), or from a closed form evaluated here and checked against the capture. The asserts below pin
each number the article quotes, so a figure cannot drift from the text. Run:  python3 _figs.py [01 05 ...]
"""
import csv
import json
import math
import pathlib
import sys
from decimal import ROUND_HALF_UP, Decimal

from _build import ACCENT, INK, LINK, MUTED, PAPER, RULE, RULE_SOLID, SOFT, emit, eyebrow, mono

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE.parent / "lab"
CAP = json.loads((LAB / "captures.json").read_text(encoding="utf-8"))
EX, TS, PR, TB, AN = (CAP[k] for k in ("example", "twosample", "pretest", "tables", "anova"))

# One style per test, the same in every figure: (colour, stroke width, dash). The pooled or conditional classic is
# tangerine, the test this post recommends is blue.
STYLE = {"student": (ACCENT, 1.9, None), "welch": (LINK, 1.9, None),
         "student_bal": (ACCENT, 1.5, "5,3"), "welch_bal": (LINK, 1.5, "5,3"),
         "levene_rule": (INK, 1.8, None), "habit": (MUTED, 1.6, "2,2.5"),
         "pearson": (MUTED, 1.5, None), "yates": (SOFT, 1.5, "5,3"), "fisher": (ACCENT, 1.9, None),
         "mid_p": (INK, 1.4, "2,2.5"), "boschloo": (LINK, 1.9, None),
         "F": (ACCENT, 1.8, None), "W": (LINK, 1.8, None), "Fstar": (MUTED, 1.6, None)}


def hp(share, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return float((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


# ------------------------------------------------------------------ the numbers the article prints, held to the capture
assert EX["means"] == [0.75, 2.33, 1.58] and [round(v, 3) for v in EX["sd"]] == [1.789, 2.002, 1.230]
assert round(EX["r"], 3) == 0.795 and [round(v, 3) for v in EX["var_identity"]] == [3.201, 4.009, 5.697, 1.513]
P, S_, W_ = EX["paired"], EX["student"], EX["welch"]
assert (round(P["se"], 3), round(P["t"], 3), round(P["p"], 4)) == (0.389, 4.062, 0.0028)
assert (round(S_["se"], 3), round(S_["t"], 3), round(S_["p"], 4), round(W_["p"], 4), round(W_["df"], 2)) == (0.849, 1.861, 0.0792, 0.0794, 17.78)
assert round(EX["se_ratio"], 2) == 2.18 and round(EX["n_equivalent_per_arm"]) == 48
D40, D25 = TS["designs"]["10,40"], TS["designs"]["25,25"]
E40 = D40["exact"]
assert [hp(E40[k]["student"], 2) for k in ("0.25", "0.5", "1.5", "2", "4")] == [0.07, 0.52, 12.17, 18.25, 29.37]
assert min(hp(v["welch"], 2) for v in E40.values()) == 4.97 and max(hp(v["welch"], 2) for v in E40.values()) == 5.15
assert max(hp(v["student"], 2) for v in D25["exact"].values()) == 5.44
assert max(abs(z) for v in list(D40["simulated"].values()) + list(D25["simulated"].values()) for z in v["z"]) < 1.85
A80 = TS["power_at_80"]
assert (hp(A80["25,25"]["welch"], 1), hp(A80["10,40"]["welch"], 1), round(A80["10,40"]["delta"], 2), round(A80["25,25"]["delta"], 2)) == (79.9, 75.6, 1.01, 0.81)
assert round(100 * A80["25,25"]["max_gap"], 2) == 0.08 and round(100 * A80["10,40"]["max_gap"], 1) == 4.6
PB = PR["by_ratio"]
assert [hp(PB[k]["levene_rule"]["rate"], 2) for k in ("1.5", "2", "0.5", "0.6667", "4")] == [9.74, 9.13, 3.85, 2.96, 5.22]
assert [hp(PB[k]["welch"]["rate"], 2) for k in ("1.5", "2")] == [5.07, 5.06] and hp(PB["4"]["habit"]["rate"], 2) == 6.86
assert [hp(PB[k]["lev_reject"]["rate"], 1) for k in ("1.5", "2", "1")] == [27.9, 64.6, 4.3]
assert hp(PB["2"]["student_given_accept"]["rate"], 2) == 21.19 and hp(PB["1"]["welch_given_reject"]["rate"], 2) == 9.77
assert hp(PB["4"]["mw_given_sw"]["rate"], 1) == 23.1 and hp(PB["2"]["mw_given_sw"]["rate"], 1) == 15.6
TEA, MAL = TB["tea"], TB["malocclusion"]
assert TEA["ways"] == [1, 16, 36, 16, 1] and TEA["total"] == 70 and round(TEA["p_not_told_one_doubt"], 3) == 0.071
MP = MAL["pvalues"]
assert [round(MP[k], 3) for k in ("mid_p", "pearson", "n_minus_1", "barnard", "fisher", "boschloo", "yates", "fisher_doubled")] == \
    [0.112, 0.122, 0.127, 0.143, 0.174, 0.175, 0.286, 0.287]
assert round(MAL["min_expected"], 2) == 2.38 and round(MAL["chi2"], 3) == 2.386
SZ, SZU = TB["designs"]["malocclusion"]["size"], TB["designs"]["unbalanced"]["size"]
assert [hp(SZ[k]["max"], 2) for k in ("fisher", "yates", "pearson", "mid_p", "boschloo")] == [3.61, 2.19, 4.94, 5.14, 4.63]
assert hp(SZU["pearson"]["max"], 2) == 9.11 and round(TB["pearson_unbalanced_expected"], 2) == 0.28
assert SZ["fisher"]["n_rejected"] == 254 and SZ["boschloo"]["n_rejected"] == 264 and TB["nested"]["fisher_in_boschloo"]
assert TB["nested"]["fisher_doubled_in_boschloo"] and TB["unbalanced_nested"]["fisher_doubled_in_boschloo"]
assert not TB["unbalanced_nested"]["fisher_in_boschloo"] and len(TB["unbalanced_fisher_not_boschloo"]) == 4 and TB["unbalanced_boschloo_not_fisher"] == 10
assert (hp(SZU["fisher"]["at"]["0.1"], 2), hp(SZU["boschloo"]["at"]["0.1"], 2)) == (2.43, 1.61)
BT = MAL["barnard_ties"]
assert BT["n_differ"] == 71 and BT["n_explained_by_ties"] == 71 and BT["decision_flips_at_5pc"] == 0
assert (round(BT["scipy"], 4), round(BT["scipy_mirror"], 4)) == (0.1791, 0.2172)
assert (round(AN["msb"], 3), round(AN["msw"], 3), round(AN["F"], 2), round(AN["pF"], 4)) == (1.883, 0.389, 4.85, 0.0159)
assert (round(AN["W"], 2), round(AN["df2W"], 2), round(AN["pW"], 4)) == (5.18, 17.13, 0.0174)
SIM = AN["simulation"]
assert [hp(SIM[k]["F"], 2) for k in ("negative pairing", "positive pairing", "equal sizes")] == [16.13, 2.04, 6.14]
assert [hp(SIM[k]["W"], 2) for k in ("negative pairing", "positive pairing", "equal sizes")] == [5.25, 4.90, 4.98]


# ------------------------------------------------------------------ drawing helpers (Part 7's set)
def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, marker=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}{m}{o}/>')


def polyline(pts, stroke, sw=1.6, dash=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}{o}/>')


def area(pts, fill, op):
    return (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}" '
            f'fill-opacity="{op}" stroke="none"/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None, op=None, sw=1.2):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{o}{s}/>'


def note_lines(x, y, items, size=8.5, gap=15, anchor="start"):
    out = ""
    for k, (t, c) in enumerate(items):
        if t:
            out += mono(x, y + k * gap, t, size=size, fill=c, anchor=anchor,
                        weight="600" if c in (INK, LINK, ACCENT) else "400")
    return out


def title(x, y, s, fill=INK, anchor="start", size=9.5):
    """A panel title in mono, not uppercased, so symbols keep their case."""
    return mono(x, y, s, size=size, fill=fill, anchor=anchor, weight="600")


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr, xmap=None, ymap=None):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr
        self.xmap = xmap or (lambda v: v)
        self.ymap = ymap or (lambda v: v)

    def X(self, x):
        a, b = self.xmap(self.xr[0]), self.xmap(self.xr[1])
        return self.x0 + (self.xmap(x) - a) / (b - a) * self.w

    def Y(self, y):
        a, b = self.ymap(self.yr[0]), self.ymap(self.yr[1])
        return self.y0 + self.h - (self.ymap(y) - a) / (b - a) * self.h

    def clip(self, cid):
        return (f'<clipPath id="{cid}"><rect x="{self.x0}" y="{self.y0}" width="{self.w}" '
                f'height="{self.h}"/></clipPath>')

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid_y=True, grid_x=False, ylabels=True):
        s = ""
        for v in yt:
            yy = self.Y(v)
            if grid_y:
                s += line(self.x0, yy, self.x0 + self.w, yy, stroke=RULE, sw=0.8)
            if ylabels:
                s += mono(self.x0 - 8, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            xx = self.X(v)
            if grid_x:
                s += line(xx, self.y0, xx, self.y0 + self.h, stroke=RULE, sw=0.8)
            s += mono(xx, self.y0 + self.h + 15, xfmt(v), size=8, fill=SOFT)
        s += line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, stroke=RULE_SOLID)
        s += line(self.x0, self.y0, self.x0, self.y0 + self.h, stroke=RULE_SOLID)
        if xlab:
            s += mono(self.x0 + self.w, self.y0 + self.h + 32, xlab, size=8.5, fill=SOFT, anchor="end")
        if ylab:
            s += mono(self.x0, self.y0 - 12, ylab, size=8.5, fill=SOFT, anchor="start")
        return s


def legend(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like this post's marks (colour, size, opacity, stroke)."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, kind in items:
        part = kind.split(":")
        if part[0] == "band":
            s += rect(x, y - 1, 16, 12, fill=part[1], op=float(part[2]), stroke="none", sw=0)
        elif part[0] == "line":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=float(part[2]) if len(part) > 2 else 2.0)
        elif part[0] == "dash":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=float(part[2]) if len(part) > 2 else 1.4, dash="5,3")
        elif part[0] == "dot":
            s += dot(x + 8, y + 5, float(part[2]), fill=part[1], op=float(part[3]) if len(part) > 3 else None)
        elif part[0] == "ring":
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1], sw=1.6)
        elif part[0] == "style":
            col, sw, dash = STYLE[part[1]]
            s += line(x, y + 5, x + 18, y + 5, stroke=col, sw=sw, dash=dash)
        elif part[0] == "styledot":
            col, sw, dash = STYLE[part[1]]
            s += line(x, y + 5, x + 18, y + 5, stroke=col, sw=sw, dash=dash) + dot(x + 9, y + 5, 3.0, fill=col)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 24
    return s


def pct(v, nd=1):
    return f"{hp(v, nd):.{nd}f}%"


def num(v, nd=1):
    """A number with thousands separators and a true minus sign."""
    return f"{v:,.{nd}f}".replace("-", "−")


def curve(ax, xs, ys):
    assert all(v == v for v in ys), "a NaN would make the browser drop the whole polyline"
    return [(ax.X(a), ax.Y(b)) for a, b in zip(xs, ys)]


def styled(ax, xs, ys, key, op=None):
    col, sw, dash = STYLE[key]
    return polyline(curve(ax, xs, ys), col, sw=sw, dash=dash, op=op)


def t_pdf(t, df):
    c = math.lgamma((df + 1) / 2) - math.lgamma(df / 2) - 0.5 * math.log(df * math.pi)
    return math.exp(c - (df + 1) / 2 * math.log1p(t * t / df))


def read_sleep():
    with (LAB / "data" / "student1908_sleep.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line_ for line_ in f if not line_.startswith("#")))
    return [(int(r["patient"]), float(r["drug_1"]), float(r["drug_2"])) for r in rows]


def log2(v):
    return math.log(v, 2)


RATIO_TICKS = [0.25, 0.5, 1, 2, 4]


def ratio_fmt(v):
    return {0.25: "1/4", 0.5: "1/2", 1: "1", 2: "2", 4: "4"}[v]


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 520
    rows = read_sleep()
    assert [(round(a, 1), round(b, 1)) for _, a, b in rows] == list(zip(EX["x"], EX["y"]))
    s = eyebrow(32, 40, "the worked example: Student's ten patients, each given both drugs (R's sleep data)")
    ax = Axes(96, 96, 300, 330, (0, 1), (-2.5, 6.0))
    s += title(ax.x0, ax.y0 - 16, "extra hours of sleep, patient by patient")
    s += ax.frame([], [-2, 0, 2, 4, 6], yfmt=lambda v: num(v, 0))
    s += mono(ax.X(0.12), ax.y0 + ax.h + 18, "drug 1", size=9, fill=MUTED)
    s += mono(ax.X(0.88), ax.y0 + ax.h + 18, "drug 2", size=9, fill=MUTED)
    for pid, a, b in rows:
        s += line(ax.X(0.12), ax.Y(a), ax.X(0.88), ax.Y(b), stroke=MUTED, sw=1.1, op=0.75)
        s += dot(ax.X(0.12), ax.Y(a), 3.6, fill=INK) + dot(ax.X(0.88), ax.Y(b), 3.6, fill=INK)
    s += line(ax.x0, ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=SOFT, sw=0.8, dash="3,3")
    # panel B: drug 2 against drug 1 for each patient
    bx = Axes(520, 96, 300, 330, (-2.5, 6.0), (-2.5, 6.0))
    s += title(bx.x0, bx.y0 - 16, "drug 2 against drug 1, one dot per patient")
    s += bx.frame([-2, 0, 2, 4, 6], [-2, 0, 2, 4, 6], xlab="drug 1, hours", xfmt=lambda v: num(v, 0), yfmt=lambda v: num(v, 0))
    s += line(bx.X(-2.5), bx.Y(-2.5), bx.X(6.0), bx.Y(6.0), stroke=SOFT, sw=1.0, dash="4,3")
    s += line(bx.X(-2.5), bx.Y(-2.5 + 1.58), bx.X(6.0 - 1.58), bx.Y(6.0), stroke=LINK, sw=1.2, op=0.8)
    for pid, a, b in rows:
        s += dot(bx.X(a), bx.Y(b), 4.2, fill=INK)
    s += mono(bx.X(4.15), bx.Y(3.65), "no difference", size=8, fill=SOFT, anchor="start")
    s += note_lines(846, 120, [
        ("SD on drug 1", MUTED), (f"{EX['sd'][0]:.3f}", INK), ("SD on drug 2", MUTED), (f"{EX['sd'][1]:.3f}", INK),
        ("SD of the differences", MUTED), (f"{EX['sd'][2]:.3f}", LINK), ("", INK),
        ("correlation between", MUTED), ("a patient's two results", MUTED), (f"r = {EX['r']:.3f}", INK), ("", INK),
        ("patients high on one drug", MUTED), ("are high on the other, so", MUTED), ("the differences vary less", MUTED),
        ("than either drug alone", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("one patient", "dot:" + INK + ":3.6"), ("equal sleep on both drugs", "dash:" + SOFT + ":1.0"),
                              ("drug 2 = drug 1 + 1.58", "line:" + LINK + ":1.2")])
    return emit("01", "ten-patients", "Ten patients, two drugs each",
                "The extra hours of sleep each patient gained on drug 1 and on drug 2, as Student printed them in 1908 and as R "
                "ships them in its sleep data.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "one mean difference, 1.58 hours, measured against two null distributions")
    ax = Axes(96, 96, 620, 300, (-3.6, 3.6), (0, 1.12))
    s += ax.clip("c2") + title(ax.x0, ax.y0 - 16, "density of the mean difference if the drugs were equal")
    s += ax.frame([-3, -2, -1, 0, 1, 2, 3], [0, 0.5, 1.0], xlab="mean difference, hours (drug 2 − drug 1)",
                  xfmt=lambda v: num(v, 0), yfmt=lambda v: f"{v:g}")
    inner = ""
    obs = EX["means"][2]
    for key, se, df, col, op in (("unpaired", S_["se"], S_["df"], ACCENT, 0.16), ("paired", P["se"], P["df"], LINK, 0.22)):
        xs = [-3.6 + 7.2 * i / 720 for i in range(721)]
        ys = [t_pdf(x / se, df) / se for x in xs]
        tail = [(x, y) for x, y in zip(xs, ys) if x >= obs]
        tail_l = [(x, y) for x, y in zip(xs, ys) if x <= -obs]
        for seg in (tail, tail_l):
            pts = [(ax.X(seg[0][0]), ax.Y(0))] + [(ax.X(x), ax.Y(y)) for x, y in seg] + [(ax.X(seg[-1][0]), ax.Y(0))]
            inner += area(pts, col, op)
        inner += polyline(curve(ax, xs, ys), col, sw=1.9)
    inner += line(ax.X(obs), ax.y0, ax.X(obs), ax.y0 + ax.h, stroke=INK, sw=1.2)
    inner += line(ax.X(-obs), ax.y0 + 150, ax.X(-obs), ax.y0 + ax.h, stroke=SOFT, sw=0.9, dash="3,3")
    s += f'<g clip-path="url(#c2)">{inner}</g>'
    s += mono(ax.X(obs) + 6, ax.y0 + 12, "observed: +1.58", size=8.4, fill=INK, anchor="start", weight="600")
    s += mono(ax.X(-obs) - 6, ax.y0 + 162, "−1.58", size=8.2, fill=SOFT, anchor="end")
    s += mono(ax.X(0.62), ax.Y(0.84), "paired", size=8.6, fill=LINK, anchor="start", weight="600")
    s += mono(ax.X(-1.72), ax.Y(0.20), "as two groups", size=8.6, fill=ACCENT, anchor="end", weight="600")
    s += note_lines(742, 112, [
        ("as two groups", ACCENT), (f"SE {S_['se']:.3f}", MUTED), (f"t = 1.58/{S_['se']:.3f} = {S_['t']:.2f}", MUTED),
        (f"{S_['df']:.0f} df: p = {S_['p']:.3f}", MUTED), (f"(Welch, {W_['df']:.2f} df: p = {W_['p']:.3f})", SOFT), ("", INK),
        ("paired", LINK), (f"SE {P['se']:.3f}", MUTED), (f"t = 1.58/{P['se']:.3f} = {P['t']:.2f}", MUTED),
        (f"{P['df']} df: p = {P['p']:.4f}", MUTED), ("", INK),
        ("shaded: the two-sided p-value,", MUTED), ("the area beyond ±1.58", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("as two groups (t, 18 df, scaled by its SE)", "line:" + ACCENT + ":1.9"),
                              ("paired (t, 9 df, scaled by its SE)", "line:" + LINK + ":1.9")])
    return emit("02", "two-standard-errors", "The same difference against two standard errors",
                "Each curve is the null distribution of the mean difference under one analysis: a t distribution scaled by "
                "that analysis's standard error.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 540
    s = eyebrow(32, 40, "exact type I error of a 5% two-sided test, normal data, by quadrature; dots are simulations")
    ax = Axes(96, 96, 600, 320, (0.25, 4.0), (0, 0.32), xmap=log2)
    s += ax.clip("c4") + title(ax.x0, ax.y0 - 16, "type I error")
    s += ax.frame(RATIO_TICKS, [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], xlab="SD of group 1 / SD of group 2 (log scale)",
                  xfmt=ratio_fmt, yfmt=lambda v: f"{100 * v:.0f}%")
    ratios = [float(k) for k in sorted(E40, key=float)]
    inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    for design, sfx in ((D25, "_bal"), (D40, "")):
        ex = design["exact"]
        ks = sorted(ex, key=float)
        inner += styled(ax, [float(k) for k in ks], [ex[k]["student"] for k in ks], "student" + sfx)
        inner += styled(ax, [float(k) for k in ks], [ex[k]["welch"] for k in ks], "welch" + sfx)
    s += f'<g clip-path="url(#c4)">{inner}</g>'
    for design in (D25, D40):
        for k, v in design["simulated"].items():
            for t in ("student", "welch"):
                s += dot(ax.X(float(k)), ax.Y(v[t]), 3.2, fill=PAPER, stroke=STYLE[t][0], sw=1.3)
    s += dot(ax.X(1.5), ax.Y(E40["1.5"]["student"]), 2.6, fill=ACCENT)
    assert ratios[0] == 0.25
    s += mono(ax.X(4.0) - 4, ax.Y(E40["4"]["student"]) - 9, f"{pct(E40['4']['student'], 2)}", size=8.4, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(2.0) - 6, ax.Y(E40["2"]["student"]) - 9, f"{pct(E40['2']['student'], 2)}", size=8.4, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(1.5) - 6, ax.Y(E40["1.5"]["student"]) - 9, f"{pct(E40['1.5']['student'], 2)}", size=8.4, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(0.5), ax.Y(0.05) + 30, f"Student at 1/2: {pct(E40['0.5']['student'], 2)}", size=8.2, fill=ACCENT, anchor="middle")
    s += mono(ax.X(2.6), ax.Y(0.05) + 18, "Welch, both designs", size=8.2, fill=LINK, anchor="middle", weight="600")
    s += note_lines(722, 112, [
        ("n = 10 (group 1) and 40", INK), ("SD ratio > 1: the small group", MUTED), ("has the larger SD, and Student's", MUTED),
        ("pooled SE is too small", MUTED), ("SD ratio < 1: the reverse, and", MUTED), ("Student's test rarely rejects", MUTED), ("", INK),
        ("Welch's test, anywhere here", LINK), (f"{pct(min(v['welch'] for v in E40.values()), 2)} to {pct(max(v['welch'] for v in E40.values()), 2)}", LINK), ("", INK),
        ("n = 25 and 25 (dashed)", INK), (f"Student's at most {pct(max(v['student'] for v in D25['exact'].values()), 2)}", MUTED), ("", INK),
        ("dots: 200,000 simulated pairs", MUTED), ("of samples; within 1.8 MCSE", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("Student, 10 and 40", "style:student"), ("Welch, 10 and 40", "style:welch"),
                              ("Student, 25 and 25", "style:student_bal"), ("Welch, 25 and 25", "style:welch_bal"),
                              ("simulated", "ring:" + MUTED + ":3.2")])
    return emit("04", "student-against-welch", "Student's error follows the pairing of size and variance",
                "The exact probability that a 5% test rejects when the means are equal, for normal samples, as the ratio of the two "
                "population SDs moves from 1/4 to 4.", "when does student's t-test keep its 5%?", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "exact power of 5% two-sided tests with equal SDs, normal data, by quadrature")
    ax = Axes(96, 96, 600, 300, (0, 2.0), (0, 1.0))
    s += ax.clip("c5") + title(ax.x0, ax.y0 - 16, "power")
    s += ax.frame([0, 0.5, 1.0, 1.5, 2.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="true difference in means, in SDs",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%")
    inner = line(ax.x0, ax.Y(0.8), ax.x0 + ax.w, ax.Y(0.8), stroke=SOFT, sw=0.9, dash="4,3")
    for dkey, sfx in (("25,25", "_bal"), ("10,40", "")):
        pw = TS["power"][f"{dkey},1"]
        inner += styled(ax, pw["delta"], pw["student"], "student" + sfx)
        inner += styled(ax, pw["delta"], pw["welch"], "welch" + sfx)
        a = A80[dkey]
        inner += line(ax.X(a["delta"]), ax.Y(a["welch"]), ax.X(a["delta"]), ax.Y(0.8), stroke=INK, sw=1.0)
        inner += dot(ax.X(a["delta"]), ax.Y(0.8), 3.0, fill=ACCENT) + dot(ax.X(a["delta"]), ax.Y(a["welch"]), 3.0, fill=LINK)
    s += f'<g clip-path="url(#c5)">{inner}</g>'
    a40, a25 = A80["10,40"], A80["25,25"]
    s += mono(ax.X(a40["delta"]) + 8, ax.Y(a40["welch"]) + 14, f"10 and 40 at {a40['delta']:.2f} SD: Welch {pct(a40['welch'])}", size=8.2, fill=LINK, anchor="start", weight="600")
    s += mono(ax.X(a25["delta"]) - 8, ax.Y(0.8) - 10, f"25 and 25 at {a25['delta']:.2f} SD: Welch {pct(a25['welch'])}", size=8.2, fill=LINK, anchor="end", weight="600")
    s += mono(ax.X(1.95), ax.Y(0.30), "25 and 25: the dashed Student and", size=8, fill=MUTED, anchor="end")
    s += mono(ax.X(1.95), ax.Y(0.30) + 13, "Welch curves coincide", size=8, fill=MUTED, anchor="end")
    s += note_lines(722, 112, [
        ("Student's power is 80.0% at", MUTED), (f"{a25['delta']:.2f} SD with 25 and 25,", MUTED), (f"and at {a40['delta']:.2f} SD with 10 and 40", MUTED), ("", INK),
        ("Welch's power there", LINK), (f"25 and 25: {pct(a25['welch'])}", LINK), (f"10 and 40: {pct(a40['welch'])}", LINK), ("", INK),
        ("largest gap, 0 to 2 SD", INK), (f"25 and 25: {100 * a25['max_gap']:.2f} points", MUTED), (f"10 and 40: {100 * a40['max_gap']:.1f} points", MUTED), ("", INK),
        ("with 10 against 40, Welch's df", MUTED), ("are near 14 rather than 48", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("Student, 10 and 40", "style:student"), ("Welch, 10 and 40", "style:welch"),
                              ("Student, 25 and 25", "style:student_bal"), ("Welch, 25 and 25", "style:welch_bal")])
    return emit("05", "the-price-of-welch", "Welch's price, when the variances really are equal",
                "Power of Student's and Welch's tests against the true difference in means, with both population SDs equal, in a "
                "balanced and an unbalanced design.", "when does student's t-test keep its 5%?", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 600
    s = eyebrow(32, 40, "n = 10 (group 1) and 40, normal data, equal means; 100,000 simulated pairs of samples per SD ratio")
    ax = Axes(96, 92, 600, 250, (0.25, 4.0), (0, 0.32), xmap=log2)
    s += ax.clip("c6a") + title(ax.x0, ax.y0 - 14, "type I error of the whole procedure")
    s += ax.frame(RATIO_TICKS, [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], xfmt=ratio_fmt, yfmt=lambda v: f"{100 * v:.0f}%")
    ks = sorted(PB, key=float)
    xs = [float(k) for k in ks]
    ex = D40["exact"]
    eks = sorted(ex, key=float)
    inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    inner += styled(ax, [float(k) for k in eks], [ex[k]["student"] for k in eks], "student")
    inner += styled(ax, [float(k) for k in eks], [ex[k]["welch"] for k in eks], "welch")
    for key in ("habit", "levene_rule"):
        ys = [PB[k][key]["rate"] for k in ks]
        inner += styled(ax, xs, ys, key)
        col = STYLE[key][0]
        for x, y in zip(xs, ys):
            inner += dot(ax.X(x), ax.Y(y), 3.0, fill=col)
    s += f'<g clip-path="url(#c6a)">{inner}</g>'
    s += mono(ax.X(1.5) + 10, ax.Y(PB["1.5"]["levene_rule"]["rate"]) - 12, pct(PB["1.5"]["levene_rule"]["rate"], 2), size=8.4, fill=INK, anchor="start", weight="600")
    s += mono(ax.X(2.0) + 6, ax.Y(PB["2"]["levene_rule"]["rate"]) + 14, pct(PB["2"]["levene_rule"]["rate"], 2), size=8.4, fill=INK, anchor="start", weight="600")
    s += mono(ax.X(3.4), ax.Y(ex["4"]["student"]) + 2, "Student", size=8.2, fill=ACCENT, anchor="end", weight="600")
    bx = Axes(96, 400, 600, 110, (0.25, 4.0), (0, 1.0), xmap=log2)
    s += title(bx.x0, bx.y0 - 12, "how often Levene's test rejects equal variances")
    s += bx.frame(RATIO_TICKS, [0, 0.5, 1.0], xlab="SD of group 1 / SD of group 2 (log scale)", xfmt=ratio_fmt, yfmt=lambda v: f"{100 * v:.0f}%")
    lev = [PB[k]["lev_reject"]["rate"] for k in ks]
    s += polyline(curve(bx, xs, lev), INK, sw=1.6)
    for x, y in zip(xs, lev):
        s += dot(bx.X(x), bx.Y(y), 3.0, fill=INK)
    s += mono(bx.X(1.5) - 6, bx.Y(PB["1.5"]["lev_reject"]["rate"]) - 8, pct(PB["1.5"]["lev_reject"]["rate"]), size=8.2, fill=INK, anchor="end", weight="600")
    s += note_lines(722, 108, [
        ("Levene decides:", INK), ("Welch if it rejects at 5%,", MUTED), ("Student otherwise", MUTED), ("", INK),
        ("the full habit adds a Shapiro-", MUTED), ("Wilk test of each group first,", MUTED), ("and a rank test if either fails", MUTED), ("", INK),
        ("at an SD ratio of 2", INK), (f"Levene decides {pct(PB['2']['levene_rule']['rate'], 2)}", INK),
        (f"Welch alone {pct(PB['2']['welch']['rate'], 2)}", LINK),
        (f"Student on the samples Levene", ACCENT), (f"passed: {pct(PB['2']['student_given_accept']['rate'], 2)}", ACCENT), ("", INK),
        ("at 1/2 the procedure is", MUTED), (f"conservative: {pct(PB['0.5']['levene_rule']['rate'], 2)}", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("always Student", "style:student"), ("always Welch", "style:welch"),
                              ("Levene decides", "styledot:levene_rule"), ("the full habit", "styledot:habit")])
    return emit("06", "pre-testing", "Testing the assumptions first does not rescue Student's test",
                "The type I error of four procedures for two groups of 10 and 40, and how often the variance pre-test rejects, as "
                "the ratio of the population SDs moves from 1/4 to 4.", "does checking the assumptions first help?", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "Fisher's tea-tasting design: eight cups, four with milk first, and the lady is told so")
    ax = Axes(96, 96, 470, 290, (-0.6, 4.6), (0, 40))
    s += title(ax.x0, ax.y0 - 16, "ways to pick the four milk-first cups, out of 70 equally likely choices")
    s += ax.frame([0, 1, 2, 3, 4], [0, 10, 20, 30, 40], xlab="milk-first cups picked correctly",
                  xfmt=lambda v: f"{v}", yfmt=lambda v: f"{v}")
    for k, w in enumerate(TEA["ways"]):
        col = ACCENT if k == 4 else (INK if k == 3 else MUTED)
        op = 0.85 if k >= 3 else 0.45
        s += rect(ax.X(k) - 30, ax.Y(w), 60, ax.Y(0) - ax.Y(w), fill=col, op=op, stroke="none", sw=0)
        s += mono(ax.X(k), ax.Y(w) - 8, f"{w}", size=9, fill=col if k >= 3 else MUTED, weight="600" if k >= 3 else "400")
    s += mono(ax.X(4), ax.Y(1) - 24, "1/70 = 0.0143", size=8.4, fill=ACCENT, anchor="middle", weight="600")
    s += mono(ax.X(3.0), ax.Y(16) - 36, "3 or 4 right:", size=8.2, fill=INK, anchor="middle")
    s += mono(ax.X(3.0), ax.Y(16) - 24, "17/70 = 0.243", size=8.4, fill=INK, anchor="middle", weight="600")
    # the table for all eight right
    tx, ty = 620, 110
    s += title(tx, ty, "all eight right, as a 2 × 2 table")
    cells = [["", "named milk first", "named tea first", "total"], ["milk first", "4", "0", "4"], ["tea first", "0", "4", "4"],
             ["total", "4", "4", "8"]]
    widths = [92, 104, 100, 52]
    for r_, row in enumerate(cells):
        x = tx
        for c_, val in enumerate(row):
            fill = "#ffffff" if (r_ in (1, 2) and c_ in (1, 2)) else PAPER
            s += rect(x, ty + 14 + 24 * r_, widths[c_], 24, fill=fill, stroke="rgba(45,49,66,0.25)")
            s += mono(x + widths[c_] / 2, ty + 14 + 24 * r_ + 16, val, size=8.4,
                      fill=ACCENT if (r_ == 3 or c_ == 3) and val not in ("", "total") else INK,
                      weight="600" if (r_ == 3 or c_ == 3) else "400")
            x += widths[c_]
    s += note_lines(tx, ty + 136, [
        ("both margins (tangerine) were fixed", ACCENT), ("by the design: four cups of each kind", MUTED),
        ("poured, and four named", MUTED), ("", INK),
        ("a 5% test can reject only at all", MUTED), ("eight right: its size is 1/70 = 1.43%", INK), ("", INK),
        ("not told the split, she may name three;", MUTED), ("one doubtful cup then gives P = 4/56", MUTED),
        ("= 0.071 at best (Yates 1984)", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("4 right: the only outcome a 5% test rejects", "band:" + ACCENT + ":0.85"),
                              ("3 right: with 4, the 17/70 tail", "band:" + INK + ":0.85"), ("other outcomes", "band:" + MUTED + ":0.45")])
    return emit("07", "tea-tasting", "When the design fixes both margins, Fisher's test is exact",
                "The hypergeometric distribution of correct picks if the lady cannot tell the difference: every choice of four of "
                "the eight cups equally likely.", "which test fits a 2 × 2 table?", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
ORDER8 = ("mid_p", "pearson", "n_minus_1", "barnard", "fisher", "boschloo", "yates", "fisher_doubled")
LABEL8 = {"mid_p": "Fisher's mid-p", "pearson": "Pearson chi-squared", "n_minus_1": "'N − 1' chi-squared",
          "barnard": "Barnard (unconditional)", "fisher": "Fisher exact, Irwin's rule", "boschloo": "Boschloo (unconditional)",
          "yates": "Yates-corrected chi-squared", "fisher_doubled": "Fisher exact, doubled tail"}


def fig08():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "Hellman's malocclusion counts, as Yates printed them in 1934: one 2 × 2 table, eight tests")
    tx, ty = 40, 96
    s += title(tx, ty, "observed (expected under independence)")
    exp = MAL["expected"]
    cells = [["", "normal teeth", "malocclusion", "total"],
             ["breast-fed", f"4 ({exp[0][0]:.2f})", f"16 ({exp[0][1]:.2f})", "20"],
             ["bottle-fed", f"1 ({exp[1][0]:.2f})", f"21 ({exp[1][1]:.2f})", "22"],
             ["total", "5", "37", "42"]]
    widths = [78, 92, 100, 42]
    for r_, row in enumerate(cells):
        x = tx
        for c_, val in enumerate(row):
            hot = (r_, c_) == (1, 1)
            s += rect(x, ty + 14 + 26 * r_, widths[c_], 26, fill="#ffffff" if r_ in (1, 2) and c_ in (1, 2) else PAPER,
                      stroke=ACCENT if hot else "rgba(45,49,66,0.25)", sw=1.4 if hot else 0.8)
            s += mono(x + widths[c_] / 2, ty + 14 + 26 * r_ + 17, val, size=8.4, fill=ACCENT if hot else INK,
                      weight="600" if hot else "400")
            x += widths[c_]
    s += note_lines(tx, ty + 150, [
        (f"smallest expected count {MAL['min_expected']:.2f},", ACCENT), ("below the customary 5", MUTED), ("", INK),
        (f"Pearson's chi-squared {MAL['chi2']:.3f}", MUTED), ("on 1 df", MUTED), ("", INK),
        ("R's chisq.test and SciPy's", MUTED), ("chi2_contingency default to", MUTED), ("the Yates-corrected test", MUTED)], gap=15.5)
    ax = Axes(560, 96, 380, 300, (0, 0.32), (0, 8))
    s += title(400, ax.y0 - 16, "two-sided p-value for this table")
    s += ax.frame([0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3], [], xfmt=lambda v: f"{v:g}", ylabels=False, grid_y=False)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "p", size=8.5, fill=SOFT, anchor="end")
    s += line(ax.X(0.05), ax.y0, ax.X(0.05), ax.y0 + ax.h, stroke=SOFT, sw=1.0, dash="4,3")
    s += mono(ax.X(0.05) + 4, ax.y0 + ax.h - 6, "0.05", size=8, fill=SOFT, anchor="start")
    cols = {"mid_p": INK, "pearson": MUTED, "n_minus_1": MUTED, "barnard": LINK, "fisher": ACCENT, "boschloo": LINK,
            "yates": MUTED, "fisher_doubled": ACCENT}
    for i, k in enumerate(ORDER8):
        y = ax.y0 + 22 + i * 36
        s += line(ax.x0, y, ax.x0 + ax.w, y, stroke=RULE, sw=0.6)
        s += dot(ax.X(MP[k]), y, 4.4, fill=cols[k])
        s += mono(ax.x0 - 10, y + 3, LABEL8[k], size=8.4, fill=INK, anchor="end")
        s += mono(ax.X(MP[k]) + 9, y + 3, f"{MP[k]:.3f}", size=8.4, fill=cols[k], anchor="start", weight="600")
    s += legend(vh - 24, vw, [("conditional on both margins", "dot:" + ACCENT + ":4.4"), ("unconditional", "dot:" + LINK + ":4.4"),
                              ("chi-squared family", "dot:" + MUTED + ":4.4"), ("mid-p", "dot:" + INK + ":4.4")])
    return emit("08", "eight-tests-one-table", "One table, eight p-values",
                "Breast-fed and bottle-fed infants with normal teeth or malocclusion (Hellman's data, via Yates 1934), and the "
                "two-sided p-value each test gives.", "which test fits a 2 × 2 table?", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "exact size of 5% tests: two independent binomial samples with a common rate π, every possible table summed")
    grid = TB["pi_grid"]
    keys = ("pearson", "yates", "fisher", "mid_p", "boschloo")
    for j, (sz, lab, m, n) in enumerate(((SZ, "groups of 20 and 22 (the malocclusion design)", 20, 22),
                                          (SZU, "groups of 10 and 40", 10, 40))):
        ax = Axes(96 + j * 470, 96, 400, 330, (0, 1), (0, 0.10))
        s += ax.clip(f"c9{j}") + title(ax.x0, ax.y0 - 16, lab)
        s += ax.frame([0, 0.25, 0.5, 0.75, 1.0], [0, 0.02, 0.04, 0.06, 0.08, 0.10], xlab="common success rate π",
                      xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%", ylabels=True)
        inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
        for k in keys:
            inner += styled(ax, grid, sz[k]["curve"], k)
        s += f'<g clip-path="url(#c9{j})">{inner}</g>'
        s += mono(ax.X(0.12), ax.Y(0.05) - 6, "5%", size=8, fill=SOFT, anchor="start")
        lines = [(f"largest size", INK)] + [(f"{LABEL9[k]} {pct(sz[k]['max'], 2)}", STYLE[k][0] if k != "yates" else MUTED) for k in
                                           ("pearson", "mid_p", "boschloo", "fisher", "yates")]
        s += note_lines(ax.X(0.86), ax.y0 + 14, lines, size=8.2, gap=14, anchor="end")
    s += mono(96 + 470 + 8, 96 + 330 - (330 * 0.0911 / 0.10) - 10, f"Pearson {pct(SZU['pearson']['max'], 2)} at π = {SZU['pearson']['argmax']:.3f}",
              size=8.2, fill=MUTED, anchor="start", weight="600")
    s += legend(vh - 24, vw, [("Pearson", "style:pearson"), ("Yates-corrected", "style:yates"), ("Fisher, Irwin's rule", "style:fisher"),
                              ("mid-p", "style:mid_p"), ("Boschloo", "style:boschloo")])
    return emit("09", "exact-size-of-2x2-tests", "Conditioning on a margin the design did not fix costs size",
                "For every common success rate π, the probability that each 5% test rejects, summed exactly over all 483 (left) and "
                "451 (right) possible tables.", "which test fits a 2 × 2 table?", vw, vh, s)


LABEL9 = {"pearson": "Pearson", "mid_p": "mid-p", "boschloo": "Boschloo", "fisher": "Fisher", "yates": "Yates"}


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 520
    groups = AN["groups"]
    names = list(groups)
    s = eyebrow(32, 40, "R's PlantGrowth data: dried weight of 30 plants, a control and two treatments, ten plants each")
    ax = Axes(96, 96, 470, 320, (-0.5, 2.5), (3.4, 6.6))
    s += title(ax.x0, ax.y0 - 16, "dried weight")
    s += ax.frame([], [3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5], yfmt=lambda v: f"{v:.1f}")
    s += line(ax.x0, ax.Y(AN["grand"]), ax.x0 + ax.w, ax.Y(AN["grand"]), stroke=SOFT, sw=1.1, dash="5,3")
    s += mono(ax.X(0) + 56, ax.Y(AN["grand"]) - 6, f"grand mean {AN['grand']:.3f}", size=8.2, fill=SOFT, anchor="start")
    for i, g in enumerate(names):
        vals = sorted(groups[g]["values"])
        for j, v in enumerate(vals):
            s += dot(ax.X(i) - 36 + 8 * j, ax.Y(v), 3.4, fill=MUTED, op=0.85)
        mu = groups[g]["mean"]
        s += line(ax.X(i) - 52, ax.Y(mu), ax.X(i) + 52, ax.Y(mu), stroke=LINK, sw=2.0)
        s += line(ax.X(i) + 52, ax.Y(mu), ax.X(i) + 52, ax.Y(AN["grand"]), stroke=ACCENT, sw=1.6)
        s += mono(ax.X(i), ax.y0 + ax.h + 18, g, size=9, fill=MUTED)
        s += mono(ax.X(i), ax.y0 + ax.h + 32, f"mean {mu:.3f}, SD {groups[g]['sd']:.3f}", size=8, fill=SOFT)
    s += note_lines(612, 108, [
        ("within groups", MUTED), (f"SS {AN['ssw']:.3f} on {AN['df'][1]} df", MUTED), (f"mean square {AN['msw']:.3f}", INK),
        ("estimates σ² whatever the means", MUTED), ("", INK),
        ("between groups (tangerine gaps)", ACCENT), (f"10 × Σ(group mean − grand)² = {AN['ssb']:.3f}", MUTED),
        (f"on {AN['df'][0]} df: mean square {AN['msb']:.3f}", INK), ("estimates σ² only if the means are equal", MUTED), ("", INK),
        (f"F = {AN['msb']:.3f} / {AN['msw']:.3f} = {AN['F']:.2f}", INK), (f"on 2 and 27 df: p = {AN['pF']:.4f}", MUTED), ("", INK),
        (f"Welch's W = {AN['W']:.2f}", LINK), (f"on 2 and {AN['df2W']:.2f} df: p = {AN['pW']:.4f}", LINK)], gap=15.5)
    s += legend(vh - 24, vw, [("one plant", "dot:" + MUTED + ":3.4:0.85"), ("group mean", "line:" + LINK + ":2.0"),
                              ("distance to the grand mean", "line:" + ACCENT + ":1.6"), ("grand mean", "dash:" + SOFT + ":1.1")])
    return emit("10", "anova-as-a-ratio", "F compares two estimates of the same variance",
                "PlantGrowth's 30 weights by group: the spread within the groups and the spread of the group means about the grand "
                "mean, and the ratio of their mean squares.", "what does anova's f compare?", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "three normal groups with equal means; 100,000 simulated data sets per design; bars are ±2 MCSE")
    ax = Axes(330, 96, 470, 300, (0, 0.18), (0, 4))
    s += title(ax.x0, ax.y0 - 16, "type I error of a 5% test")
    s += ax.frame([0, 0.03, 0.06, 0.09, 0.12, 0.15, 0.18], [], xfmt=lambda v: f"{100 * v:.0f}%", ylabels=False, grid_y=False)
    s += line(ax.X(0.05), ax.y0, ax.X(0.05), ax.y0 + ax.h, stroke=SOFT, sw=1.0, dash="4,3")
    s += mono(ax.X(0.05) + 4, ax.y0 + ax.h - 6, "5%", size=8, fill=SOFT, anchor="start")
    rows = (("negative pairing", "n 10, 20, 30; SD 3, 2, 1"), ("positive pairing", "n 10, 20, 30; SD 1, 2, 3"),
            ("equal sizes", "n 20, 20, 20; SD 1, 2, 3"), ("equal variances", "n 10, 20, 30; SD 1, 1, 1"))
    for i, (k, sub) in enumerate(rows):
        y0 = ax.y0 + 18 + i * 74
        s += line(ax.x0, y0 + 42, ax.x0 + ax.w, y0 + 42, stroke=RULE, sw=0.6)
        s += mono(ax.x0 - 14, y0 + 14, k, size=8.8, fill=INK, anchor="end", weight="600")
        s += mono(ax.x0 - 14, y0 + 28, sub, size=8, fill=SOFT, anchor="end")
        v = SIM[k]
        for j, (t, lab) in enumerate((("F", "F"), ("W", "W"), ("Fstar", "F*"))):
            yy = y0 + 6 + 14 * j
            col = STYLE[t][0]
            rate, m = v[t], v["mcse"][j]
            s += line(ax.X(rate - 2 * m), yy, ax.X(rate + 2 * m), yy, stroke=col, sw=1.4)
            s += dot(ax.X(rate), yy, 3.6, fill=col)
            s += mono(ax.X(rate) + 9, yy + 3, f"{lab} {pct(rate, 2)}", size=8, fill=col, anchor="start", weight="600")
    s += note_lines(822, 112, [
        ("negative pairing: the", MUTED), ("smallest group has the", MUTED), ("largest SD, and the pooled", MUTED),
        ("within-group mean square", MUTED), ("understates its noise", MUTED), ("", INK),
        ("W stays within 0.3 points", LINK), ("of 5% in all four designs", LINK)], gap=15.5)
    s += legend(vh - 24, vw, [("classical F", "dot:" + ACCENT + ":3.6"), ("Welch's W", "dot:" + LINK + ":3.6"),
                              ("Brown–Forsythe F*", "dot:" + MUTED + ":3.6")])
    return emit("11", "anova-type-i-error", "F's error follows the pairing; W's stays near 5%",
                "The simulated type I error of the classical F test, Welch's W and Brown–Forsythe's F* for three groups, in four "
                "designs.", "what does anova's f compare?", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08, "09": fig09, "10": fig10,
        "11": fig11}

if __name__ == "__main__":
    for k in (sys.argv[1:] or sorted(FIGS)):
        FIGS[k]()
