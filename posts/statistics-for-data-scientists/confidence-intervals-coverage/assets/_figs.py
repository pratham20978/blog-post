#!/usr/bin/env python3
"""Figures 01-10 for confidence-intervals-coverage.

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/intervals.py, or from a closed
form evaluated here and checked against it. The asserts below pin each number the article quotes, so a figure cannot
drift from the text. Run:  python3 _figs.py [01 05 ...]
"""
import json
import math
import pathlib
import sys
from statistics import NormalDist

from _build import (ACCENT, INK, LINK, MUTED, PAPER, RULE, RULE_SOLID, SOFT, emit, eyebrow, mono)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
EN, IV, CV, PF, OV, TC = (CAP[k] for k in ("enumerate", "invert", "coverage", "pfizer", "overlap", "tcoverage"))
N01 = NormalDist()
Z = N01.inv_cdf(0.975)
NAMES = {"wald": "Wald", "wilson": "Wilson", "agresti_coull": "Agresti–Coull", "clopper_pearson": "Clopper–Pearson",
         "jeffreys": "Jeffreys"}
ORDER = ("wald", "wilson", "agresti_coull", "clopper_pearson", "jeffreys")
# One style per method, the same in every figure: (colour, stroke width, dash)
STYLE = {"wald": (ACCENT, 1.8, None), "wilson": (INK, 1.8, None), "agresti_coull": (MUTED, 1.4, "5,3"),
         "clopper_pearson": (LINK, 1.8, None), "jeffreys": (SOFT, 1.4, "1.5,2.5")}

# ------------------------------------------------------------------ the numbers the article prints, held to the capture
M = EN["methods"]
assert [round(v, 4) for v in EN["pmf"][:8]] == [0.1216, 0.2702, 0.2852, 0.1901, 0.0898, 0.0319, 0.0089, 0.002]
assert round(sum(EN["pmf"][8:]), 4) == 0.0004
assert (round(M["wald"]["coverage"], 4), round(M["wilson"]["coverage"], 4), round(M["clopper_pearson"]["coverage"], 4)) == (0.876, 0.9568, 0.9887)
assert M["wald"]["covered_x"] == [1, 2, 3, 4, 5, 6] and M["wilson"]["covered_x"] == [0, 1, 2, 3, 4] and M["clopper_pearson"]["covered_x"] == [0, 1, 2, 3, 4, 5]
assert (round(M["wald"]["lower"][1], 3), round(M["wald"]["upper"][1], 3), round(M["wald"]["lower"][6], 3), round(M["wald"]["upper"][6], 3)) == (-0.046, 0.146, 0.099, 0.501)
assert (round(M["wald"]["lower"][7], 3), round(M["wald"]["upper"][7], 3)) == (0.141, 0.559)
assert (round(M["wilson"]["upper"][0], 3), round(M["wilson"]["lower"][5], 3), round(M["clopper_pearson"]["lower"][5], 3), round(M["clopper_pearson"]["lower"][6], 3)) == (0.161, 0.112, 0.087, 0.119)
SIM = EN["simulated"]
assert (round(100 * SIM["wald"]["estimate"], 2), round(100 * SIM["wilson"]["estimate"], 2), round(100 * SIM["clopper_pearson"]["estimate"], 2)) == (87.57, 95.68, 98.89)
assert max(abs(SIM[k]["z"]) for k in ORDER) < 1.3
assert [round(v, 3) for v in IV["roots"]["wald"]] == [-0.031, 0.231] and [round(v, 3) for v in IV["roots"]["score"]] == [0.028, 0.301]
assert [round(v, 3) for v in IV["roots"]["exact"]] == [0.012, 0.317] and IV["gaps"]["score"] < 6.5e-16
N50 = CV["n50"]
assert round(N50["wald"]["share_below_093"], 2) == 0.40 and round(N50["wilson"]["min"], 3) == 0.839 and round(N50["wilson"]["at_p"], 4) == 0.0035
assert round(N50["jeffreys"]["min"], 3) == 0.884 and N50["agresti_coull"]["min"] > 0.934 and round(N50["clopper_pearson"]["min"], 4) == 0.9508
assert round(CV["wilson_dip"]["min"], 4) == 0.8387 and round(N50["clopper_pearson"]["width_vs_wilson"], 3) == 1.083 and round(N50["wald"]["width_vs_wilson"], 3) == 0.992
assert (round(N50["clopper_pearson"]["mean"], 3), round(N50["wilson"]["mean"], 3), round(N50["wald"]["mean"], 4)) == (0.969, 0.952, 0.9006)
W01 = CV["wald_vs_n"]["0.1"]
assert (round(W01["at"]["29"], 3), round(W01["at"]["30"], 3), round(W01["at"]["50"], 3)) == (0.947, 0.809, 0.879)
assert round(W01["share_below_094"], 2) == 0.22 and (round(min(W01["wilson"]), 3), round(max(W01["wilson"]), 3)) == (0.920, 0.981)
assert round(CV["textbook_rule_worst"]["coverage"], 3) == 0.854 and CV["textbook_rule_worst"]["n"] == 12
assert CV["ac_table1"]["means_matching"] == 15
PR = PF["primary"]["methods"]
assert [round(100 * v, 1) for v in PR["clopper_pearson"]["ve"]] == [90.0, 97.9] and [round(v, 4) for v in PR["clopper_pearson"]["share"]] == [0.0205, 0.0906]
assert [round(100 * v, 1) for v in PR["wald"]["ve"]] == [91.4, 98.4] and [round(100 * v, 1) for v in PR["wilson"]["ve"]] == [90.1, 97.5]
assert [round(100 * v, 1) for v in PR["agresti_coull"]["ve"]] == [89.9, 97.7] and [round(100 * v, 1) for v in PR["jeffreys"]["ve"]] == [90.5, 97.7]
S170 = PF["coverage_at_170"]["summary"]
assert (round(S170["wald"]["min"], 3), round(S170["wilson"]["min"], 3), round(S170["clopper_pearson"]["min"], 3)) == (0.796, 0.930, 0.952)
assert all(abs(S170[k]["mean"] - 0.95) < 0.02 for k in ORDER if k != "wald") and abs(S170["wald"]["mean"] - 0.95) > 0.02
assert PF["summary"] == {"confidence_rows": 16, "match_printed": 9, "within_rounding": 16}
SV = PF["severe"]
assert (round(SV["arms"]["vaccine"]["rate"], 2), round(SV["arms"]["vaccine"]["lower"], 3), round(SV["arms"]["vaccine"]["upper"], 2)) == (0.25, 0.006, 1.39)
assert (round(SV["arms"]["placebo"]["rate"], 2), round(SV["arms"]["placebo"]["lower"], 2), round(SV["arms"]["placebo"]["upper"], 2)) == (2.25, 1.03, 4.26)
assert round(SV["p_two_sided"], 3) == 0.021 and round(SV["p_scipy_binomtest"], 4) == 0.0116 and [round(100 * v, 1) for v in SV["ve_ci"]] == [20.1, 99.7]
assert (round(OV["alpha_at"]["1"], 4), round(OV["alpha_at"]["2"], 4)) == (0.0056, 0.0085) and round(OV["arm_overlap_at_5pct"], 2) == 0.59
assert round(OV["power_at_design80"]["overlap95"], 2) == 0.51 and round(100 * OV["level_for_5pct"], 1) == 83.4
assert round(OV["p_half_arm"]["1"], 3) == 0.038 and round(OV["greenland"]["p"], 3) == 0.029
OS = OV["simulation"]
assert (round(100 * OS["null"]["t_test"]["rate"], 2), round(100 * OS["null"]["no_overlap_95"]["rate"], 2), round(100 * OS["null"]["no_overlap_83"]["rate"], 2)) == (4.99, 0.57, 4.97)
assert (round(100 * OS["alt80"]["t_test"]["rate"], 1), round(100 * OS["alt80"]["no_overlap_95"]["rate"], 1), round(100 * OS["alt80"]["no_overlap_83"]["rate"], 2)) == (80.0, 44.9, 79.85)
assert round(OS["d_alt"], 2) == 1.32
TB = TC["by_n"]
assert [round(100 * TB[k]["coverage"], 2) for k in ("10", "30", "100", "1000", "10000")] == [64.42, 65.83, 70.3, 85.65, 93.84]
assert round(100 * TB["30"]["miss_below"], 2) == 34.17 and round(TB["30"]["miss_above"] * TB["30"]["R"]) == 1 and TB["30"]["R"] == 200_000
assert max(TB[k]["miss_above"] for k in TB) < 0.012 and round(TC["population"]["skewness"], 1) == 21.6
DEC = TC["deciles"]["30"]["coverage"]
assert DEC[0] == 0.0 and round(100 * DEC[1], 1) == 1.0 and round(100 * DEC[2], 1) == 14.9 and min(DEC[5:]) >= 0.9895
NDEC = TC["normal"]["exact_deciles"]["30"]
assert (round(100 * NDEC[0], 1), round(100 * NDEC[-1], 1)) == (88.2, 98.7)


# ------------------------------------------------------------------ drawing helpers (Part 5's set)
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


def dot(x, y, rr=3.4, fill=INK, stroke=None, op=None):
    s = f' stroke="{stroke}" stroke-width="1.2"' if stroke else ""
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
        elif part[0] == "dotted":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.4, dash="1.5,2.5")
        elif part[0] == "longdash":
            s += line(x, y + 5, x + 22, y + 5, stroke=part[1], sw=float(part[2]) if len(part) > 2 else 1.4, dash="8,4")
        elif part[0] == "dot":
            s += dot(x + 8, y + 5, float(part[2]), fill=part[1], op=float(part[3]) if len(part) > 3 else None)
        elif part[0] == "ring":
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1])
        elif part[0] == "hinterval":                     # a horizontal interval with its estimate
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=2.0) + dot(x + 9, y + 5, 2.6, fill=part[1])
        elif part[0] == "style":                         # one of the five methods, drawn as in the curves
            col, sw, dash = STYLE[part[1]]
            s += line(x, y + 5, x + 18, y + 5, stroke=col, sw=sw, dash=dash)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 24
    return s


def pct(v, nd=1):
    return f"{100 * v:.{nd}f}%"


def num(v, nd=1):
    """A number with thousands separators and a true minus sign."""
    return f"{v:,.{nd}f}".replace("-", "−")


def curve(ax, xs, ys):
    assert all(v == v for v in ys), "a NaN would make the browser drop the whole polyline"
    return [(ax.X(a), ax.Y(b)) for a, b in zip(xs, ys)]


log10 = math.log10


# ------------------------------------------------------------------ FIG 01
def sci(v):
    """6e-16 as '6 × 10⁻¹⁶', for labels."""
    e = math.floor(math.log10(abs(v)))
    m = round(v / 10**e)
    if m == 10:
        m, e = 1, e + 1
    sup = str(e).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{m} × 10{sup}"


def fig01():
    vw, vh = 1016, 512
    rows = 9                                            # X = 0..8; P(X >= 9) is 6e-5 and is said in a note
    top, rh = 116, 30
    pmf = EN["pmf"]
    s = eyebrow(32, 40, "20 audited predictions, a true error rate of 10%: every possible count, its probability and its 95% intervals")
    s += title(40, top - 22, "errors X", size=9)
    s += title(118, top - 22, "P(X = x)", size=9)
    for i in range(rows):
        y = top + i * rh + rh / 2
        s += mono(70, y + 3, f"X = {i}", size=8.6, fill=INK, anchor="end")
        w = pmf[i] / 0.3 * 120
        s += rect(112, y - 7, w, 14, fill=MUTED, op=0.45, stroke="none", sw=0)
        s += mono(112 + w + 6, y + 3, f"{pmf[i]:.4f}", size=8.2, fill=INK, anchor="start")
    panels = (("wald", "Wald"), ("wilson", "Wilson"), ("clopper_pearson", "Clopper–Pearson"))
    for j, (key, name) in enumerate(panels):
        ax = Axes(318 + j * 232, top, 200, rows * rh, (-0.1, 0.65), (0, 1))
        m = M[key]
        s += title(ax.x0, top - 22, f"{name}: coverage {m['coverage']:.4f}", size=9, fill=INK)
        for v in (0, 0.1, 0.3, 0.5):
            s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE, sw=0.8)
            s += mono(ax.X(v), ax.y0 + ax.h + 15, f"{v:g}", size=8, fill=SOFT)
        s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
        s += line(ax.X(0.1), ax.y0 - 4, ax.X(0.1), ax.y0 + ax.h, stroke=INK, sw=1.1, dash="3,3")
        for i in range(rows):
            y = top + i * rh + rh / 2
            lo, hi, ok = m["lower"][i], m["upper"][i], m["contains"][i]
            col = INK if ok else ACCENT
            if hi - lo < 1e-9:
                s += dot(ax.X(lo), y, 3.2, fill=col)
            else:
                s += line(ax.X(max(lo, -0.1)), y, ax.X(min(hi, 0.65)), y, stroke=col, sw=2.2)
        cov = m["covered_x"]
        s += mono(ax.x0 + ax.w / 2, ax.y0 + ax.h + 32, f"contains 0.1 for X = {cov[0]} to {cov[-1]}", size=8.4, fill=MUTED)
    s += mono(318 + 2 * 232 + 200, top - 36, "true p = 0.1 (dashed)", size=8.2, fill=SOFT, anchor="end")
    tail9 = sum(pmf[9:])
    s += note_lines(40, top + rows * rh + 56, [
        ("Coverage at p = 0.1 is the total probability of the counts whose interval contains 0.1: Wald 0.2702 + ... + 0.0089 = 0.8760, "
         "Wilson 0.9568, Clopper–Pearson 0.9887.", MUTED),
        (f"At X = 0 the Wald interval has zero width (the dot); it misses 0.1, and X = 0 happens {pct(pmf[0])} of the time. "
         f"Counts of 9 or more have probability {tail9:.5f} and are not drawn.", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("interval contains 0.1", "line:" + INK + ":2.2"), ("interval misses 0.1", "line:" + ACCENT + ":2.2"),
                              ("zero-width interval", "dot:" + ACCENT + ":3.2"), ("P(X = x)", "band:" + MUTED + ":0.45")])
    return emit("01", "coverage-by-enumeration", "Coverage is a sum over outcomes",
                "Every count of errors in 20 audits, its binomial probability under a true rate of 10%, and the 95% interval each of three "
                "methods would report for it.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 486
    x, n = IV["x"], IV["n"]
    ph = x / n
    se = math.sqrt(ph * (1 - ph) / n)
    grid = IV["grid"]
    # The Wald curve also runs below zero, which the captured grid does not cover; evaluate it here and check it there.
    wald_p = lambda p0: 2 * (1 - N01.cdf(abs(ph - p0) / se))
    assert all(abs(wald_p(g) - c) <= 1e-5 * abs(c) + 1e-12 for g, c in zip(grid, IV["curves"]["wald"]))   # the capture keeps 6 digits
    s = eyebrow(32, 40, "2 errors in 20 audits: the two-sided p-value of three tests of p = p0, against p0")
    ax = Axes(96, 96, 620, 250, (-0.06, 0.42), (0, 1.0))
    s += ax.clip("c2") + title(ax.x0, ax.y0 - 16, "two-sided p-value")
    s += ax.frame([-0.05, 0, 0.1, 0.2, 0.3, 0.4], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="null value p0",
                  xfmt=lambda v: num(v, 2), yfmt=lambda v: f"{v:.1f}")
    xs = [-0.06 + 0.48 * i / 600 for i in range(601)]
    inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    inner += line(ax.X(0), ax.y0, ax.X(0), ax.y0 + ax.h, stroke=RULE_SOLID, sw=0.8)
    inner += polyline(curve(ax, xs, [wald_p(v) for v in xs]), STYLE["wald"][0], sw=1.8)
    inner += polyline(curve(ax, grid, IV["curves"]["score"]), STYLE["wilson"][0], sw=1.8)
    inner += polyline(curve(ax, grid, IV["curves"]["exact"]), STYLE["clopper_pearson"][0], sw=1.8)
    s += f'<g clip-path="url(#c2)">{inner}</g>'
    s += mono(ax.x0 + ax.w - 4, ax.Y(0.05) - 5, "p = 0.05", size=8.4, fill=SOFT, anchor="end")
    s += mono(ax.X(0.1), ax.y0 - 4, "p-hat = 0.1", size=8.4, fill=INK)
    rows = (("wald", "Wald test → Wald interval", IV["roots"]["wald"]), ("wilson", "score test → Wilson interval", IV["roots"]["score"]),
            ("clopper_pearson", "exact test → Clopper–Pearson", IV["roots"]["exact"]))
    for i, (key, label, (lo, hi)) in enumerate(rows):
        y = ax.y0 + ax.h + 50 + 20 * i
        col = STYLE[key][0]
        s += line(ax.X(lo), y, ax.X(hi), y, stroke=col, sw=2.4)
        s += line(ax.X(lo), y - 5, ax.X(lo), y + 5, stroke=col, sw=1.4) + line(ax.X(hi), y - 5, ax.X(hi), y + 5, stroke=col, sw=1.4)
        s += mono(ax.X(hi) + 8, y + 3, f"{num(lo, 3)} to {hi:.3f}   {label}", size=8.4, fill=col, anchor="start", weight="600")
    s += note_lines(752, ax.y0 + 20, [
        ("each interval is the set", INK), ("of p0 its test keeps:", INK), ("p-value ≥ 0.05", INK), ("", INK),
        ("Wald: SE at p-hat, a curve", ACCENT), ("symmetric about 0.1; its", ACCENT), ("interval runs below zero", ACCENT), ("", INK),
        ("score: SE at p0; its", INK), ("crossings are Wilson's", INK), (f"endpoints, to {sci(IV['gaps']['score'])}", MUTED), ("", INK),
        ("exact: twice the smaller", LINK), ("binomial tail, capped at 1", LINK), ("near p-hat; gives", LINK), ("Clopper–Pearson's", LINK)], gap=15)
    s += legend(vh - 24, vw, [("Wald test", "style:wald"), ("score test", "style:wilson"), ("exact binomial test", "style:clopper_pearson"),
                              ("the 0.05 line", "dash:" + SOFT)])
    return emit("02", "intervals-as-inverted-tests", "An interval is the null values a test keeps",
                "For an observed 2 errors in 20, each curve is one test's p-value for the null p = p0. The 95% interval is where the curve "
                "is at or above 0.05.", "what 95% promises", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 584
    cvs = CV["curves"]
    s = eyebrow(32, 40, "exact coverage of five nominal 95% intervals for a proportion, n = 50, p from 0.001 to 0.999")
    slots = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1)]
    for key, (cx, cy) in zip(ORDER, slots):
        ax = Axes(84 + cx * 312, 92 + cy * 252, 252, 160, (0, 1), (0.80, 1.0))
        cid = f"c3{key}"
        s += ax.clip(cid)
        sm = N50[key]
        s += title(ax.x0, ax.y0 - 14, NAMES[key], size=9.5)
        s += ax.frame([0, 0.25, 0.5, 0.75, 1.0], [0.80, 0.85, 0.90, 0.95, 1.0], xfmt=lambda v: f"{v:g}",
                      yfmt=lambda v: f"{100 * v:.0f}%", ylabels=(cx == 0))
        col = STYLE[key][0]
        # the curve on a 0.001 grid, with the exact minimum found on the finer grid inserted, so the dot sits on the line
        pts = sorted(list(zip(cvs["p"], cvs[key])) + [(sm["at_p"], sm["min"])])
        inner = line(ax.x0, ax.Y(0.95), ax.x0 + ax.w, ax.Y(0.95), stroke=SOFT, sw=1.0, dash="4,3")
        inner += polyline(curve(ax, [a for a, _ in pts], [b for _, b in pts]), col, sw=0.9)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        mn = sm["min"]
        if mn >= 0.80:
            s += dot(ax.X(sm["at_p"]), ax.Y(mn), 3.2, fill=col)
            s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 28, f"min {pct(mn, 2)} at p = {sm['at_p']:.4f}", size=8.2, fill=MUTED, anchor="end")
        else:
            s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 28, "falls toward 0 at the edges (off scale)", size=8.2, fill=MUTED, anchor="end")
        s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 42, f"mean {pct(sm['mean'], 1)}; below 93% for {pct(sm['share_below_093'], 1)} of p",
                  size=8.2, fill=MUTED, anchor="end")
    nx, ny = 84 + 2 * 312, 92 + 252
    s += note_lines(nx, ny + 8, [
        ("each curve sums, at every p,", INK), ("the binomial probabilities of", INK), ("the counts whose interval", INK),
        ("contains p; nothing is simulated", INK), ("", INK),
        ("dashed: nominal 95%; dots:", SOFT), ("the minimum on a finer grid", SOFT), ("", INK),
        (f"Clopper–Pearson never below {pct(N50['clopper_pearson']['min'], 2)}", LINK), ("", INK),
        ("Wilson's edge dip never closes:", MUTED), (f"{CV['wilson_dip']['min']:.4f} at n = {CV['wilson_dip']['n']:,}", MUTED)], gap=15)
    return emit("03", "coverage-curves", "Five intervals, one sample size",
                "Exact actual coverage against the true proportion p at n = 50. The promise is 95% at every p.", "choosing an interval", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 556
    ns, wc, wl = W01["n"], W01["wald"], W01["wilson"]
    s = eyebrow(32, 40, "exact coverage of the 95% Wald and Wilson intervals when the true proportion is 0.1, for every n from 10 to 1,000")
    ax = Axes(96, 96, 620, 250, (10, 1000), (0.6, 1.0), xmap=log10)
    s += ax.clip("c4") + title(ax.x0, ax.y0 - 16, "Wald interval: coverage at p = 0.1")
    s += ax.frame([10, 20, 30, 50, 100, 200, 500, 1000], [0.6, 0.7, 0.8, 0.9, 0.95, 1.0],
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{100 * v:.0f}%")
    inner = rect(ax.X(50), ax.y0, ax.x0 + ax.w - ax.X(50), ax.h, fill=MUTED, op=0.06, stroke="none", sw=0)
    inner += line(ax.x0, ax.Y(0.95), ax.x0 + ax.w, ax.Y(0.95), stroke=SOFT, sw=1.0, dash="4,3")
    inner += polyline(curve(ax, ns, wc), STYLE["wald"][0], sw=1.0)
    s += f'<g clip-path="url(#c4)">{inner}</g>'
    for n_, dx, dy, anc in (("29", -6, -10, "end"), ("30", 8, 14, "start"), ("50", 8, 16, "start")):
        v = W01["at"][n_]
        s += dot(ax.X(int(n_)), ax.Y(v), 3.6, fill=ACCENT)
        s += mono(ax.X(int(n_)) + dx, ax.Y(v) + dy, f"n = {n_}: {pct(v, 1)}", size=8.6, fill=ACCENT, anchor=anc, weight="600")
    s += mono(ax.X(50) + 6, ax.y0 + 14, "np ≥ 5 from n = 50", size=8.4, fill=MUTED, anchor="start")
    s += mono(ax.x0 + 6, ax.Y(0.95) + 14, "nominal 95%", size=8.4, fill=SOFT, anchor="start")
    bx = Axes(96, 392, 620, 80, (10, 1000), (0.9, 1.0), xmap=log10)
    s += bx.clip("c4b") + title(bx.x0, bx.y0 - 12, "Wilson interval, same p and n", size=9)
    s += bx.frame([10, 20, 30, 50, 100, 200, 500, 1000], [0.9, 0.95, 1.0], xlab="n (log scale)", xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: f"{100 * v:.0f}%")
    inner = rect(bx.X(50), bx.y0, bx.x0 + bx.w - bx.X(50), bx.h, fill=MUTED, op=0.06, stroke="none", sw=0)
    inner += line(bx.x0, bx.Y(0.95), bx.x0 + bx.w, bx.Y(0.95), stroke=SOFT, sw=1.0, dash="4,3")
    inner += polyline(curve(bx, ns, wl), STYLE["wilson"][0], sw=1.0)
    s += f'<g clip-path="url(#c4b)">{inner}</g>'
    s += note_lines(752, ax.y0 + 20, [
        ("Wald, n = 10 to 1,000:", ACCENT), (f"from {pct(W01['min'], 1)} to {pct(W01['max'], 1)}", ACCENT),
        (f"below 94% for {pct(W01['share_below_094'], 0)} of n", ACCENT), (f"n = 100: {pct(W01['at']['100'], 1)}", ACCENT),
        (f"n = 1,000: {pct(W01['at']['1000'], 1)}", ACCENT), ("", INK),
        ("Wilson, same range:", INK), (f"{pct(min(wl), 1)} to {pct(max(wl), 1)}", INK), ("", INK),
        ("shaded: n ≥ 50, where the", MUTED), ("rule np ≥ 5 is met", MUTED), ("", INK),
        ("each step changes which", MUTED), ("counts' intervals contain 0.1", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("Wald", "style:wald"), ("Wilson", "style:wilson"), ("the article's three n", "dot:" + ACCENT + ":3.6"),
                              ("nominal 95%", "dash:" + SOFT), ("np ≥ 5", "band:" + MUTED + ":0.06")])
    return emit("04", "wald-oscillation", "More data, not always more coverage",
                "The Wald interval's coverage zigzags as n grows, because the set of counts whose interval contains 0.1 changes one count "
                "at a time; the Wilson interval's, below on a finer scale, stays near 95%.", "choosing an interval", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 500
    bn = CV["by_n"]
    ns = bn["n"]
    s = eyebrow(32, 40, "each interval averaged over a true proportion spread uniformly from 0 to 1, computed exactly")
    axl = Axes(96, 104, 360, 270, (5, 200), (0.6, 1.0), xmap=log10)
    axr = Axes(562, 104, 360, 270, (5, 200), (0.8, 1.25), xmap=log10)
    s += axl.clip("c5l") + axr.clip("c5r")
    s += title(axl.x0, axl.y0 - 16, "mean coverage") + title(axr.x0, axr.y0 - 16, "mean width, relative to Wilson's")
    s += axl.frame([5, 10, 20, 50, 100, 200], [0.6, 0.7, 0.8, 0.9, 0.95, 1.0], xlab="n (log scale)", xfmt=lambda v: f"{v:g}",
                   yfmt=lambda v: f"{100 * v:.0f}%")
    s += axr.frame([5, 10, 20, 50, 100, 200], [0.8, 0.9, 1.0, 1.1, 1.2], xlab="n (log scale)", xfmt=lambda v: f"{v:g}",
                   yfmt=lambda v: f"{v:.1f}×")
    il = line(axl.x0, axl.Y(0.95), axl.x0 + axl.w, axl.Y(0.95), stroke=SOFT, sw=1.0, dash="4,3")
    ir = line(axr.x0, axr.Y(1.0), axr.x0 + axr.w, axr.Y(1.0), stroke=SOFT, sw=1.0, dash="4,3")
    wil = bn["wilson"]["width"]
    for key in ORDER:
        col, sw, dash = STYLE[key]
        il += polyline(curve(axl, ns, bn[key]["mean"]), col, sw=sw, dash=dash)
        ir += polyline(curve(axr, ns, [w / v for w, v in zip(bn[key]["width"], wil)]), col, sw=sw, dash=dash)
    s += f'<g clip-path="url(#c5l)">{il}</g><g clip-path="url(#c5r)">{ir}</g>'
    printed = CV["ac_table1"]["printed"]
    for key in ("wald", "wilson", "clopper_pearson"):
        for n_, (mean, _rmse) in printed[key].items():
            s += dot(axl.X(int(n_)), axl.Y(mean), 4.6, fill="none", stroke=STYLE[key][0])
    jw = list(ns).index(10)
    s += mono(axl.X(10) + 8, axl.Y(bn["wald"]["mean"][jw]) + 16, "Wald", size=8.4, fill=STYLE["wald"][0], anchor="start", weight="600")
    jc = list(ns).index(20)
    s += mono(axl.X(20), axl.Y(bn["clopper_pearson"]["mean"][jc]) - 7, "Clopper–Pearson", size=8.4, fill=STYLE["clopper_pearson"][0],
              anchor="start", weight="600")
    s += mono(axl.X(100) + 4, axl.Y(bn["wilson"]["mean"][list(ns).index(100)]) + 15, "Wilson", size=8.4, fill=STYLE["wilson"][0],
              anchor="start", weight="600")
    j50 = list(ns).index(50)
    rr = {k: bn[k]["width"][j50] / wil[j50] for k in ORDER}
    s += note_lines(axr.X(30), axr.Y(0.95), [("at n = 50, width over Wilson's:", INK),
                                               (f"Clopper–Pearson {rr['clopper_pearson']:.3f}×", LINK),
                                               (f"Agresti–Coull {rr['agresti_coull']:.3f}×", MUTED),
                                               (f"Jeffreys {rr['jeffreys']:.3f}×", MUTED), (f"Wald {rr['wald']:.3f}×", ACCENT)], gap=14)
    s += note_lines(96, 428, [("Rings: Agresti and Coull's Table 1 means for Wald, Wilson and Clopper–Pearson; all 15 reproduce to three decimals.", MUTED),
                              (f"Even at n = 100 the 95% Wald interval's mean coverage is {pct(printed['wald']['100'][0], 1)}.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("Wald", "style:wald"), ("Wilson", "style:wilson"), ("Agresti–Coull", "style:agresti_coull"),
                              ("Clopper–Pearson", "style:clopper_pearson"), ("Jeffreys", "style:jeffreys"), ("published mean", "ring:" + INK + ":4.6")])
    return emit("05", "coverage-and-width", "What coverage costs",
                "Mean coverage over a uniform p, and mean width as a multiple of the Wilson interval's, for five intervals as n grows.",
                "choosing an interval", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 490
    pr = PF["primary"]
    s = eyebrow(32, 40, "the BNT162b2 trial's primary split: 8 of 170 cases in the vaccine group, surveillance times 2.214 and 2.222")
    axl = Axes(140, 104, 360, 250, (86, 100), (0, 7))
    s += title(axl.x0, axl.y0 - 16, "vaccine efficacy and its 95% interval")
    for v in (86, 88, 90, 92, 94, 96, 98, 100):
        s += line(axl.X(v), axl.y0, axl.X(v), axl.y0 + axl.h, stroke=RULE, sw=0.8)
        s += mono(axl.X(v), axl.y0 + axl.h + 15, f"{v}%", size=8, fill=SOFT)
    s += line(axl.x0, axl.y0 + axl.h, axl.x0 + axl.w, axl.y0 + axl.h, stroke=RULE_SOLID)
    ve = 100 * pr["ve"]
    s += line(axl.X(ve), axl.y0, axl.X(ve), axl.y0 + axl.h, stroke=INK, sw=0.9, dash="2,3")
    s += mono(axl.X(ve), axl.y0 - 4, f"estimate {ve:.1f}%", size=8.2, fill=INK)
    rows = [(k, NAMES[k], [100 * v for v in pr["methods"][k]["ve"]]) for k in ORDER]
    cred = [r for r in PF["rows"] if r["interval"] == "credible" and r["endpoint"].endswith("no_prior_infection")][0]
    rows.append(("credible", "credible (published)", [cred["published"][1], cred["published"][2]]))
    for i, (key, name, (lo, hi)) in enumerate(rows):
        y = axl.Y(6.4 - i)
        col, sw, dash = (MUTED, 2.4, "8,4") if key == "credible" else (STYLE[key][0], 2.4, STYLE[key][2])
        s += mono(axl.x0 - 8, y + 3, name, size=8.4, fill=col, anchor="end", weight="600" if key == "clopper_pearson" else "400")
        s += line(axl.X(lo), y, axl.X(hi), y, stroke=col, sw=sw, dash=dash)
        s += mono(axl.X(hi) + 6, y + 3, f"{lo:.1f} to {hi:.1f}" + ("  = Table 3" if key == "clopper_pearson" else "  Table 2" if key == "credible" else ""),
                  size=8.2, fill=col, anchor="start", weight="600" if key == "clopper_pearson" else "400")
    axr = Axes(600, 104, 330, 250, (0.01, 0.12), (0.78, 1.0))
    c170 = PF["coverage_at_170"]
    s += axr.clip("c6") + title(axr.x0, axr.y0 - 16, "exact coverage at n = 170")
    s += axr.frame([0.02, 0.04, 0.06, 0.08, 0.10, 0.12], [0.80, 0.85, 0.90, 0.95, 1.0], xlab="true share of cases in the vaccine group",
                   xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: f"{100 * v:.0f}%")
    inner = line(axr.x0, axr.Y(0.95), axr.x0 + axr.w, axr.Y(0.95), stroke=SOFT, sw=1.0, dash="4,3")
    inner += line(axr.X(8 / 170), axr.y0, axr.X(8 / 170), axr.y0 + axr.h, stroke=INK, sw=0.9, dash="2,3")
    for key in ("wald", "wilson", "clopper_pearson"):
        inner += polyline(curve(axr, c170["share"], c170[key]), STYLE[key][0], sw=1.0)
    s += f'<g clip-path="url(#c6)">{inner}</g>'
    s += mono(axr.X(8 / 170) + 4, axr.y0 + 12, "observed 8/170", size=8.2, fill=INK, anchor="start")
    sm = c170["summary"]
    s += note_lines(600, 402, [("min / mean coverage, true shares 0.01 to 0.12:", MUTED),
                               (f"Wald {pct(sm['wald']['min'])} / {pct(sm['wald']['mean'])}, Wilson {pct(sm['wilson']['min'])} / "
                                f"{pct(sm['wilson']['mean'])}, Agresti–Coull {pct(sm['agresti_coull']['min'])} / {pct(sm['agresti_coull']['mean'])}", MUTED),
                               (f"Clopper–Pearson {pct(sm['clopper_pearson']['min'])} / {pct(sm['clopper_pearson']['mean'])}, "
                                f"Jeffreys {pct(sm['jeffreys']['min'])} / {pct(sm['jeffreys']['mean'])}", MUTED)], gap=14, size=8)
    s += legend(vh - 24, vw, [("Wald", "style:wald"), ("Wilson", "style:wilson"), ("Agresti–Coull", "style:agresti_coull"),
                              ("Clopper–Pearson", "style:clopper_pearson"), ("Jeffreys", "style:jeffreys"), ("credible interval", "longdash:" + MUTED + ":2.4")])
    return emit("06", "vaccine-efficacy-intervals", "One trial, six intervals",
                "Efficacy intervals from the same case split by five confidence methods, beside the trial's published credible interval; "
                "right, how often three of the methods cover at this size.", "a real trial", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "two independent estimates with 95% intervals: what non-overlap says about their difference")
    g = Axes(56, 104, 250, 250, (-0.6, 1.6), (0, 1))
    s += title(g.x0, g.y0 - 16, "equal standard errors s")
    arm, d5, dt = Z, Z * math.sqrt(2), 2 * Z
    sc = lambda v: g.x0 + 20 + (v + arm) / (dt + 2 * arm) * 210
    for i, (d, lab, sub) in enumerate(((d5, "p = 0.05 exactly", f"overlap {OV['arm_overlap_at_5pct']:.0%} of an arm"),
                                       (dt, "just touching", f"p = {OV['p_touching']['1']:.4f}"))):
        y0 = g.y0 + 30 + i * 120
        s += mono(g.x0, y0 - 10, lab, size=8.6, fill=INK, anchor="start", weight="600")
        if i == 0:
            s += rect(sc(d - arm), y0 + 4, sc(arm) - sc(d - arm), 32, fill=ACCENT, op=0.16, stroke="none", sw=0)
        for k, c in enumerate((0.0, d)):
            yy = y0 + 12 + 16 * k
            s += line(sc(c - arm), yy, sc(c + arm), yy, stroke=MUTED, sw=2.2) + dot(sc(c), yy, 2.8, fill=MUTED)
        s += mono(g.x0, y0 + 60, sub, size=8.4, fill=ACCENT if i == 0 else MUTED, anchor="start", weight="600" if i == 0 else "400")
        s += mono(g.x0, y0 + 74, f"difference {d:.2f}s", size=8.2, fill=MUTED, anchor="start")
    ax = Axes(386, 104, 250, 250, (1, 20), (0, 0.055), xmap=log10)
    ac = OV["alpha_curve"]
    s += ax.clip("c7a") + title(ax.x0, ax.y0 - 16, "type I error of \"no overlap\"")
    s += ax.frame([1, 2, 5, 10, 20], [0, 0.01, 0.02, 0.03, 0.04, 0.05], xlab="ratio of standard errors k (log)",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%")
    inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    inner += polyline(curve(ax, ac["k"], ac["alpha"]), ACCENT, sw=1.9)
    s += f'<g clip-path="url(#c7a)">{inner}</g>'
    for k_, dx, dy in (("1", 8, -6), ("2", 8, 15), ("4", 8, 15)):
        v = OV["alpha_at"][k_]
        s += dot(ax.X(int(k_)), ax.Y(v), 3.2, fill=ACCENT)
        s += mono(ax.X(int(k_)) + dx, ax.Y(v) + dy, pct(v, 2), size=8.2, fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.x0 + ax.w - 4, ax.Y(0.05) + 13, "a real 5% test", size=8.2, fill=SOFT, anchor="end")
    bx = Axes(716, 104, 250, 250, (0, 5), (0, 1))
    pc = OV["power_curve"]
    assert max(abs(a - b) for a, b in zip(pc["standard"], pc["overlap83"])) < 1e-9   # at k = 1 the 83.4% rule is the standard test
    s += bx.clip("c7b") + title(bx.x0, bx.y0 - 16, "power, k = 1")
    s += bx.frame([0, 1, 2, 3, 4, 5], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="true difference / its SE", xfmt=lambda v: f"{v:g}",
                  yfmt=lambda v: f"{100 * v:.0f}%")
    inner = polyline(curve(bx, pc["delta"], pc["standard"]), INK, sw=1.9)
    inner += polyline(curve(bx, pc["delta"], pc["overlap83"]), LINK, sw=1.4, dash="5,3")
    inner += polyline(curve(bx, pc["delta"], pc["overlap95"]), ACCENT, sw=1.9)
    d80 = OV["power_at_design80"]["delta"]
    inner += line(bx.X(d80), bx.y0, bx.X(d80), bx.Y(0), stroke=SOFT, sw=0.8, dash="2,3")
    s += f'<g clip-path="url(#c7b)">{inner}</g>'
    s += dot(bx.X(d80), bx.Y(0.8), 3.4, fill=INK) + dot(bx.X(d80), bx.Y(OV["power_at_design80"]["overlap95"]), 3.4, fill=ACCENT)
    s += mono(bx.X(d80) - 6, bx.Y(0.8) - 7, "80%", size=8.4, fill=INK, anchor="end", weight="600")
    s += mono(bx.X(d80) + 6, bx.Y(OV["power_at_design80"]["overlap95"]) + 4, pct(OV["power_at_design80"]["overlap95"], 0), size=8.4,
              fill=ACCENT, anchor="start", weight="600")
    s += note_lines(386, 404, [(f"At k = 1 the {100 * OV['level_for_5pct']:.1f}% rule rejects exactly when the standard test does,", MUTED),
                               ("so its dashed curve lies on the standard test's.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("estimate ± 1.96 s", "hinterval:" + MUTED), ("overlap", "band:" + ACCENT + ":0.16"),
                              ("the standard test", "line:" + INK + ":1.9"), ("rule: 95% intervals apart", "line:" + ACCENT + ":1.9"),
                              (f"rule: {100 * OV['level_for_5pct']:.1f}% intervals apart", "dash:" + LINK)])
    return emit("07", "overlap-rule", "Overlap is a weak test",
                "Left: two estimates with equal standard errors at the edge of significance and at the edge of overlap. Middle and right: "
                "the overlap rule read as a test, from Schenker and Gentleman's formula.", "overlapping intervals", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 410
    arms, ov = SV["arms"], SV["overlap"]
    s = eyebrow(32, 40, "severe Covid-19 after dose 1 in the BNT162b2 trial (FDA Table 12): 1 case against 9")
    ax = Axes(150, 110, 390, 150, (0, 4.6), (0, 2))
    s += ax.clip("c8") + title(ax.x0, ax.y0 - 18, "cases per 1,000 person-years, exact 95% interval for each arm")
    for v in (0, 1, 2, 3, 4):
        s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE, sw=0.8)
        s += mono(ax.X(v), ax.y0 + ax.h + 15, f"{v}", size=8, fill=SOFT)
    s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
    inner = rect(ax.X(ov[0]), ax.y0, ax.X(ov[1]) - ax.X(ov[0]), ax.h, fill=ACCENT, op=0.16, stroke="none", sw=0)
    s += f'<g clip-path="url(#c8)">{inner}</g>'
    for i, (k, lab) in enumerate((("vaccine", "vaccine: 1 case, 4.021"), ("placebo", "placebo: 9 cases, 4.006"))):
        a = arms[k]
        y = ax.Y(1.45 - 0.9 * i)
        col = LINK if k == "vaccine" else INK
        s += mono(ax.x0 - 8, y + 3, lab, size=8.4, fill=col, anchor="end")
        s += line(ax.X(a["lower"]), y, ax.X(a["upper"]), y, stroke=col, sw=2.4) + dot(ax.X(a["rate"]), y, 3.4, fill=col)
        lo_txt = f"{a['lower']:.3f}" if a["lower"] < 0.1 else f"{a['lower']:.2f}"
        s += mono(ax.X(a["upper"]) + 6, y + 3, f"{a['rate']:.2f} ({lo_txt} to {a['upper']:.2f})", size=8.2, fill=col, anchor="start")
    s += mono(ax.X((ov[0] + ov[1]) / 2), ax.y0 + ax.h + 32, f"overlap {ov[0]:.2f} to {ov[1]:.2f}", size=8.4, fill=ACCENT, weight="600")
    bx = Axes(640, 110, 330, 150, (-40, 100), (0, 2))
    s += title(bx.x0, bx.y0 - 18, "vaccine efficacy, 95% interval")
    for v in (-40, -20, 0, 20, 40, 60, 80, 100):
        s += line(bx.X(v), bx.y0, bx.X(v), bx.y0 + bx.h, stroke=RULE, sw=0.8)
        s += mono(bx.X(v), bx.y0 + bx.h + 15, f"{v}%", size=8, fill=SOFT)
    s += line(bx.x0, bx.y0 + bx.h, bx.x0 + bx.w, bx.y0 + bx.h, stroke=RULE_SOLID)
    s += line(bx.X(0), bx.y0, bx.X(0), bx.y0 + bx.h, stroke=INK, sw=1.2, dash="4,3")
    lo, hi = (100 * v for v in SV["ve_ci"])
    y = bx.Y(1.0)
    s += line(bx.X(lo), y, bx.X(hi), y, stroke=INK, sw=2.4) + dot(bx.X(100 * SV["ve"]), y, 3.4, fill=INK)
    s += mono(bx.X(lo), y - 12, f"{lo:.1f}% to {hi:.1f}%, estimate {100 * SV['ve']:.1f}%", size=8.4, fill=INK, anchor="start", weight="600")
    s += mono(bx.X(0) - 6, bx.y0 + 14, "no efficacy", size=8.2, fill=INK, anchor="end")
    s += note_lines(150, 318, [
        (f"Exact test of no efficacy on the 1-to-9 split, the vaccine share {SV['pi0']:.4f} under the null: twice the smaller tail gives "
         f"p = {SV['p_two_sided']:.4f},", MUTED),
        ("the version the Clopper–Pearson interval inverts; scipy.stats.binomtest and R's poisson.test sum the outcomes no likelier", MUTED),
        (f"than the observed one and give {SV['p_scipy_binomtest']:.4f}. Both are below 0.05.", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("vaccine arm", "hinterval:" + LINK), ("placebo arm", "hinterval:" + INK), ("the arms' intervals overlap", "band:" + ACCENT + ":0.16"),
                              ("efficacy 0", "dash:" + INK)])
    return emit("08", "overlap-in-a-trial", "Overlapping arms, a significant difference",
                "Each arm's rate has an exact Poisson interval; the difference has its own interval, the efficacy interval the FDA briefing prints.",
                "overlapping intervals", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 486
    ns = [int(k) for k in TB]
    pop = TC["population"]
    s = eyebrow(32, 40, f"95% t-interval for the mean net spend of {pop['N']:,} customers (skewness {pop['skewness']:.1f}), customers drawn with replacement")
    ax = Axes(96, 96, 400, 280, (8, 12500), (0.6, 1.0), xmap=log10)
    s += ax.clip("c9") + title(ax.x0, ax.y0 - 16, "coverage")
    s += ax.frame([10, 30, 100, 300, 1000, 3000, 10000], [0.6, 0.7, 0.8, 0.9, 0.95, 1.0], xlab="sample size n (log scale)",
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{100 * v:.0f}%")
    inner = line(ax.x0, ax.Y(0.95), ax.x0 + ax.w, ax.Y(0.95), stroke=SOFT, sw=1.0, dash="4,3")
    inner += polyline(curve(ax, ns, [TB[str(n)]["coverage"] for n in ns]), INK, sw=1.6)
    s += f'<g clip-path="url(#c9)">{inner}</g>'
    for n in ns:
        s += dot(ax.X(n), ax.Y(TB[str(n)]["coverage"]), 3.4, fill=INK)
    for n, dx, dy, anc in ((10, 6, 16, "start"), (30, 0, -10, "middle"), (1000, 6, 16, "start"), (10000, -6, 16, "end")):
        v = TB[str(n)]["coverage"]
        s += mono(ax.X(n) + dx, ax.Y(v) + dy, pct(v, 2), size=8.4, fill=INK, anchor=anc, weight="600")
    s += mono(ax.x0 + ax.w - 4, ax.Y(0.95) - 6, "nominal 95%, exact for normal data", size=8.2, fill=SOFT, anchor="end")
    bx = Axes(596, 96, 330, 280, (8, 12500), (1e-6, 1.0), xmap=log10, ymap=log10)
    s += bx.clip("c9b") + title(bx.x0, bx.y0 - 16, "share of intervals that miss, by side (log)")
    s += bx.frame([10, 100, 1000, 10000], [1e-6, 1e-4, 1e-2, 1.0], xlab="sample size n (log scale)", xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: {1e-6: "0.0001%", 1e-4: "0.01%", 1e-2: "1%", 1.0: "100%"}[v])
    below = [TB[str(n)]["miss_below"] for n in ns]
    above = [TB[str(n)]["miss_above"] for n in ns]
    inner = polyline(curve(bx, ns, below), ACCENT, sw=1.6) + polyline(curve(bx, ns, above), LINK, sw=1.6)
    s += f'<g clip-path="url(#c9b)">{inner}</g>'
    for n, b, a in zip(ns, below, above):
        s += dot(bx.X(n), bx.Y(b), 3.0, fill=ACCENT) + dot(bx.X(n), bx.Y(a), 3.0, fill=LINK)
    s += mono(bx.X(30), bx.Y(below[1]) - 9, f"below the mean: {pct(below[1], 2)} at n = 30", size=8.2, fill=ACCENT, anchor="start", weight="600")
    s += mono(bx.X(30) + 6, bx.Y(above[1]) + 4, "above: 1 in 200,000", size=8.2, fill=LINK, anchor="start", weight="600")
    s += mono(bx.X(10000) - 4, bx.Y(above[-1]) - 8, f"{100 * above[-1]:.3f}%", size=8.2, fill=LINK, anchor="end")
    big = max(TB[k]["mcse"] for k in TB)
    s += note_lines(96, 428, [(f"Each coverage has an MCSE of at most {100 * big:.2f} points, so ±2 MCSE lies inside its dot (R = {TB['30']['R']:,} "
                               f"samples up to n = 100, {TB['10000']['R']:,} at n = 10,000).", MUTED),
                              ("Customers are drawn with replacement, so the draws are independent and the target is the population mean.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("coverage", "dot:" + INK + ":3.4"), ("interval wholly below the mean", "line:" + ACCENT + ":1.6"),
                              ("wholly above the mean", "line:" + LINK + ":1.6"), ("nominal 95%", "dash:" + SOFT)])
    return emit("09", "t-interval-coverage", "The t-interval on skewed spend",
                "The fraction of 95% t-intervals that contain the population mean as n grows, and on which side the misses fall.",
                "the t-interval", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "95% t-intervals at n = 30 sorted by their own width into ten equal groups: how often each group contains the mean")
    ax = Axes(96, 104, 620, 270, (0, 10), (0, 1.0))
    s += title(ax.x0, ax.y0 - 16, "coverage within each tenth of interval width")
    s += ax.frame([], [0, 0.2, 0.4, 0.6, 0.8, 0.95, 1.0], yfmt=lambda v: f"{100 * v:.0f}%")
    s += line(ax.x0, ax.Y(0.95), ax.x0 + ax.w, ax.Y(0.95), stroke=SOFT, sw=1.0, dash="4,3")
    for i in range(10):
        x0 = ax.X(i)
        for k, (v, col, op) in enumerate(((DEC[i], ACCENT, 0.85), (NDEC[i], MUTED, 0.45))):
            bx0 = x0 + 8 + k * 24
            s += rect(bx0, ax.Y(v), 22, ax.Y(0) - ax.Y(v), fill=col, op=op, stroke="none", sw=0)
        s += mono(x0 + 31, ax.y0 + ax.h + 15, f"{i + 1}", size=8.2, fill=SOFT)
        s += mono(x0 + 19, ax.Y(DEC[i]) - 5, f"{100 * DEC[i]:.0f}", size=7.8, fill=ACCENT, weight="600")
    s += mono(ax.X(0) + 8, ax.y0 + ax.h + 30, "narrowest", size=8.4, fill=SOFT, anchor="start")
    s += mono(ax.X(10) - 4, ax.y0 + ax.h + 30, "widest", size=8.4, fill=SOFT, anchor="end")
    s += mono(ax.x0 + ax.w / 2, ax.y0 + ax.h + 30, "tenth of interval width", size=8.4, fill=SOFT)
    d100 = TC["deciles"]["100"]["coverage"]
    s += note_lines(752, ax.y0 + 20, [
        ("customer spend, n = 30:", ACCENT), (f"none of the {TB['30']['R'] // 10:,} narrowest", ACCENT), ("intervals contains the mean;", ACCENT),
        (f"the next tenth {pct(DEC[1], 1)}, then {pct(DEC[2], 1)}", ACCENT), ("", INK),
        ("normal data, n = 30 (exact):", MUTED), (f"{pct(NDEC[0], 1)} to {pct(NDEC[-1], 1)}", MUTED), ("a small s makes a narrow", MUTED),
        ("interval whatever the mean", MUTED), ("", INK),
        ("spend at n = 100, narrowest", INK), (f"tenths: {pct(d100[0], 1)}, {pct(d100[1], 1)}, {pct(d100[2], 1)}", INK)], gap=15)
    s += legend(vh - 24, vw, [("customer spend (simulated)", "band:" + ACCENT + ":0.85"), ("normal population (exact)", "band:" + MUTED + ":0.45"),
                              ("nominal 95%", "dash:" + SOFT)])
    return emit("10", "coverage-by-width", "The narrow intervals are the ones that miss",
                "Coverage of the 95% t-interval within each tenth of interval width, for the skewed spend and for a normal population.",
                "the t-interval", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10}

if __name__ == "__main__":
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
