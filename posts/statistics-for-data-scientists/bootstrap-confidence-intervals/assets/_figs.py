#!/usr/bin/env python3
"""Figures 01-13 for bootstrap-confidence-intervals.

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/bootstrap.py, from the lab's
data file (Figure 1's scatter), or from a closed form evaluated here and checked against the capture. The asserts
below pin each number the article quotes, so a figure cannot drift from the text. Run:  python3 _figs.py [01 05 ...]
"""
import csv
import json
import math
import pathlib
import sys
from decimal import ROUND_HALF_UP, Decimal
from statistics import NormalDist

from _build import (ACCENT, INK, LINK, MUTED, PAPER, PAPER2, RULE, RULE_SOLID, SOFT, elbow, emit, eyebrow, mono, node,
                    alabel, hline, vline)

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE.parent / "lab"
CAP = json.loads((LAB / "captures.json").read_text(encoding="utf-8"))
EX, RC, CO, SP, MX, HV, DP = (CAP[k] for k in ("example", "reconcile", "coverage", "spend", "maximum", "heavy", "dependent"))
N01 = NormalDist()
Z = N01.inv_cdf(0.975)
NAMES = {"normal": "normal, bootstrap SE", "percentile": "percentile", "basic": "basic", "studentized": "studentized",
         "studentized_z": "studentized, Fisher scale", "bca": "BCa", "fisher_z": "Fisher z, normal theory", "t": "t-interval"}
LAW_ORDER = ("percentile", "bca", "basic", "normal", "studentized", "studentized_z", "fisher_z")
SPEND_ORDER = ("t", "normal", "percentile", "basic", "studentized", "bca")
# One style per interval method, the same in every figure: (colour, stroke width, dash)
STYLE = {"percentile": (INK, 1.8, None), "bca": (LINK, 1.8, None), "basic": (ACCENT, 1.8, None),
         "normal": (SOFT, 1.6, "5,3"), "studentized": (MUTED, 1.6, "5,3"), "studentized_z": (MUTED, 1.8, None),
         "fisher_z": (INK, 1.6, "1.5,2.5"), "t": (SOFT, 1.8, None)}

def hp(share, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it. Shares are counts over R,
    so exact ties like 78.65% occur; scaling by 100 in binary first would turn some of them into 78.6499..."""
    return float((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


# ------------------------------------------------------------------ the numbers the article prints, held to the capture
IV = EX["intervals"]
assert (round(EX["r"], 3), round(EX["rho"], 3), round(EX["se_boot"], 3), round(EX["se_normal_theory"], 3)) == (0.776, 0.76, 0.135, 0.115)
assert round(EX["true"]["se"], 3) == 0.130 and round(EX["se_delta"], 3) == 0.124 and EX["below"] == 4630 and EX["B"] == 10_000
assert (round(EX["z0"], 4), round(EX["a"], 5)) == (-0.0929, -0.07567) and [hp(v, 2) for v in EX["bca_levels"]] == [0.58, 93.86]
assert [round(v, 3) for v in IV["percentile"]] == [0.452, 0.962] and [round(v, 3) for v in IV["basic"]] == [0.590, 1.100]
assert [round(v, 3) for v in IV["normal"]] == [0.511, 1.042] and [round(v, 3) for v in IV["studentized"]] == [-0.462, 0.997]
assert [round(v, 3) for v in IV["studentized_z"]] == [-0.142, 0.946] and [round(v, 3) for v in IV["bca"]] == [0.327, 0.942]
assert [round(v, 3) for v in IV["fisher_z"]] == [0.439, 0.922] and [round(v, 2) for v in EX["t_quantiles"]] == [-1.78, 9.97]
assert round(EX["first_resample"]["r"], 3) == 0.720 and EX["first_resample"]["distinct"] == 11
JACK = dict(zip(EX["schools"], EX["jackknife"]))
assert round(JACK[6], 3) == 0.893 and EX["schools"][0] == 6
_d = [EX["jack_mean"] - j for j in EX["jackknife"]]
S2, S3 = sum(v * v for v in _d), sum(v**3 for v in _d)
D6 = _d[0]
assert abs(S3 / (6 * S2**1.5) - EX["a"]) < 1e-5 and round(100 * D6**3 / S3) == 110 and round(100 * D6**2 / S2) == 63
ESD = EX["endpoint_sd"]["by_B"]
assert (round(ESD["2000"]["percentile"][0], 3), round(ESD["2000"]["bca"][0], 3), round(ESD["10000"]["bca"][0], 3)) == (0.012, 0.026, 0.012)
assert round(ESD["2000"]["se"], 3) == 0.003 and ESD["10000"]["bca"][0] < ESD["2000"]["percentile"][0]
CM = CO["methods"]
assert [hp(CM[k]["coverage"], 1) for k in LAW_ORDER] == [91.0, 92.0, 80.7, 89.0, 95.7, 93.8, 93.6]
assert [hp(CM[k]["rho_below"], 1) for k in LAW_ORDER] == [6.9, 5.0, 18.7, 10.2, 2.6, 2.9, 4.5]
assert [hp(CM[k]["rho_above"], 1) for k in LAW_ORDER] == [2.2, 3.0, 0.7, 0.9, 1.7, 3.3, 2.0]
assert (hp(CM["studentized"]["upper_above_1"], 1), hp(CM["basic"]["upper_above_1"], 1)) == (23.5, 69.6)
S30, S100 = SP["by_n"]["30"]["methods"], SP["by_n"]["100"]["methods"]
assert [hp(S30[k]["coverage"], 1) for k in SPEND_ORDER] == [66.0, 64.3, 66.8, 60.3, 80.3, 73.3]
assert [hp(S100[k]["coverage"], 1) for k in SPEND_ORDER] == [70.1, 69.6, 72.0, 66.2, 80.3, 77.0]
assert (hp(S30["bca"]["by_flag"]["1"], 1), hp(S30["bca"]["by_flag"]["0"], 1)) == (97.0, 64.8)
assert (hp(S30["studentized"]["by_flag"]["1"], 1), hp(S30["studentized"]["by_flag"]["0"], 1)) == (99.4, 73.5)
assert hp(S100["bca"]["by_flag"]["0"], 1) == 40.4 and SP["top1_count"] == 44 and round(SP["top1_threshold"]) == 17507
TK = MX["tanks"]
assert TK["boot_pmf"] == [0.00032, 0.00992, 0.06752, 0.24992, 0.67232] and round(TK["true_pmf_at_m"], 3) == 0.009
assert TK["percentile"] == [272, 303] and TK["basic"] == [303, 334] and TK["bca"] == {"strict": [171, 303], "midrank": [273, 303]}
assert TK["exact_one_sided"] == [303, 549] and TK["exact"] == [303, 631] and hp(TK["coverage"]["basic"], 2) == 75.73
assert hp(TK["coverage"]["percentile"], 2) == 1.46 and TK["scipy_bca"] == [273.0, 303.0]
UN = MX["uniform"]["by_n"]
assert round(UN["100"]["point_mass"], 3) == 0.634 and all(abs(UN[k]["basic_coverage"] - 0.875) < 3 * UN[k]["mcse"] for k in UN)
HB = HV["by_n"]
assert [hp(HB[k]["methods"]["bca"]["coverage"], 1) for k in ("30", "100", "300", "1000")] == [73.2, 78.2, 80.9, 83.6]
assert (hp(HB["30"]["methods"]["t"]["coverage"], 1), hp(HB["1000"]["methods"]["t"]["coverage"], 1)) == (65.9, 77.2)
assert (hp(HB["30"]["methods"]["studentized"]["coverage"], 1), hp(HB["1000"]["methods"]["studentized"]["coverage"], 1)) == (80.8, 84.8)
SH = HV["shapes"]
assert round(SH[0]["max"], 1) == 22.2 and hp(SH[0]["max_share"], 1) == 8.5 and (round(SH[0]["spacing"], 2), round(SH[0]["sd_rest"], 2)) == (0.22, 0.19)
assert (round(SH[2]["spacing"], 2), round(SH[2]["sd_rest"], 2)) == (0.17, 0.29)
assert (round(SH[0]["boot_sd"], 3), round(SH[0]["sd_rest"], 3)) == (0.271, 0.188)
assert round(1 - (SH[0]["sd_rest"] / SH[0]["boot_sd"]) ** 2, 2) == 0.52 and round(1 - (SH[2]["sd_rest"] / SH[2]["boot_sd"]) ** 2, 2) == 0.21
assert (round(DP["sd_mean_exact"], 3), round(DP["se_ratio_mean"], 3), round(DP["se_ratio_theory"], 3)) == (0.141, 0.574, 0.577)
assert (round(DP["lag1_orig"], 3), round(DP["lag1_resample"], 3), hp(DP["coverage"], 1)) == (0.487, -0.005, 73.5)


# ------------------------------------------------------------------ drawing helpers (Part 6's set)
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
        elif part[0] == "dotted":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.4, dash="1.5,2.5")
        elif part[0] == "dot":
            s += dot(x + 8, y + 5, float(part[2]), fill=part[1], op=float(part[3]) if len(part) > 3 else None)
        elif part[0] == "ring":
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1], sw=1.6)
        elif part[0] == "style":                         # one of the interval methods, drawn as in every figure
            col, sw, dash = STYLE[part[1]]
            s += line(x, y + 5, x + 18, y + 5, stroke=col, sw=sw, dash=dash)
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


def read_law():
    with (LAB / "data" / "law_school_82.csv").open(encoding="utf-8") as f:
        rows = list(csv.DictReader(line_ for line_ in f if not line_.startswith("#")))
    return [(int(r["school"]), float(r["lsat"]), float(r["gpa"]), r["in_sample"] == "1") for r in rows]


def corr(pairs):
    n = len(pairs)
    mx = sum(p[0] for p in pairs) / n
    my = sum(p[1] for p in pairs) / n
    sxy = sum((p[0] - mx) * (p[1] - my) for p in pairs)
    sxx = sum((p[0] - mx) ** 2 for p in pairs)
    syy = sum((p[1] - my) ** 2 for p in pairs)
    return sxy / math.sqrt(sxx * syy)


def hinterval(ax, lo, hi, y, key, clip_lo=None, clip_hi=None, est=None):
    """A horizontal interval in its method's style, with end ticks, clipped to the axis."""
    col, sw, dash = STYLE[key]
    a, b = max(lo, clip_lo if clip_lo is not None else lo), min(hi, clip_hi if clip_hi is not None else hi)
    s = line(ax.X(a), y, ax.X(b), y, stroke=col, sw=sw + 0.6, dash=dash)
    if clip_lo is None or lo >= clip_lo:
        s += line(ax.X(lo), y - 6, ax.X(lo), y + 6, stroke=col, sw=1.4)
    if clip_hi is None or hi <= clip_hi:
        s += line(ax.X(hi), y - 6, ax.X(hi), y + 6, stroke=col, sw=1.4)
    if est is not None:
        s += dot(ax.X(est), y, 3.0, fill=col)
    return s


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 520
    law = read_law()
    pop = [(l_, g) for _, l_, g, _ in law]
    smp = [(l_, g) for _, l_, g, ins in law if ins]
    assert abs(corr(pop) - EX["rho"]) < 1e-5 and abs(corr(smp) - EX["r"]) < 1e-5 and len(smp) == 15
    s = eyebrow(32, 40, "the law-school data: 82 American law schools, and the random sample of 15 that Efron and Tibshirani bootstrap")
    ax = Axes(96, 96, 560, 320, (460, 720), (2.5, 3.6))
    s += ax.frame([480, 520, 560, 600, 640, 680, 720], [2.6, 2.8, 3.0, 3.2, 3.4, 3.6], xlab="average LSAT score",
                  ylab="average undergraduate GPA", yfmt=lambda v: f"{v:.1f}")
    for sch, l_, g, ins in law:
        if not ins:
            s += dot(ax.X(l_), ax.Y(g), 3.0, fill=SOFT, op=0.55)
    for sch, l_, g, ins in law:
        if ins:
            s += dot(ax.X(l_), ax.Y(g), 4.6, fill=INK)
    six = next((l_, g) for sch, l_, g, _ in law if sch == 6)
    s += dot(ax.X(six[0]), ax.Y(six[1]), 8.5, fill="none", stroke=ACCENT, sw=1.8)
    s += mono(ax.X(six[0]) - 14, ax.Y(six[1]) + 3, "school 6 (576, 3.39)", size=8.6, fill=ACCENT, anchor="end", weight="600")
    s += note_lines(700, 120, [
        ("all 82 schools", MUTED), (f"ρ = {EX['rho']:.4f}", MUTED), ("", INK),
        ("the 15 sampled", INK), (f"r = {EX['r']:.4f}", INK), ("", INK),
        ("the 15 without school 6", ACCENT), (f"r = {JACK[6]:.4f}", ACCENT), ("", INK),
        ("school 6 has a high GPA for", MUTED), ("its LSAT; leaving it out moves", MUTED), ("r further than leaving out", MUTED),
        ("any other school", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("one of the 82 schools", "dot:" + SOFT + ":3.0:0.55"), ("one of the 15 sampled", "dot:" + INK + ":4.6"),
                              ("school 6", "ring:" + ACCENT + ":6")])
    return emit("01", "law-school-sample", "Fifteen schools from a published population of 82",
                "Average LSAT score against average undergraduate GPA for the 82 law schools, with the 15 the bootstrap is run on. "
                "Schools keep their numbers among the 82.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 520
    edges = EX["hist_edges"]
    width = edges[1] - edges[0]
    boot = [c / (EX["B"] * width) for c in EX["hist"]]
    true = [c / (EX["true"]["R"] * width) for c in EX["true"]["hist"]]
    assert abs(sum(EX["hist"]) - EX["B"]) <= 2 and abs(sum(EX["true"]["hist"]) - EX["true"]["R"]) <= 100
    s = eyebrow(32, 40, "the correlation of 15 schools: 10,000 bootstrap replicates against a million fresh samples from the 82")
    ax = Axes(96, 96, 600, 290, (-0.1, 1.0), (0, 4.6))
    s += ax.clip("c2") + title(ax.x0, ax.y0 - 16, "density")
    s += ax.frame([-0.1, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 1, 2, 3, 4], xfmt=lambda v: num(v, 1), yfmt=lambda v: f"{v:g}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 50, "correlation", size=8.5, fill=SOFT, anchor="end")
    inner = ""
    for i, h in enumerate(boot):
        x0 = edges[i]
        if x0 + width <= -0.1:
            continue
        inner += rect(ax.X(x0) + 0.6, ax.Y(h), ax.X(x0 + width) - ax.X(x0) - 1.2, ax.Y(0) - ax.Y(h), fill=MUTED, op=0.40,
                      stroke="none", sw=0)
    pts = []
    for i, h in enumerate(true):
        pts += [(ax.X(edges[i]), ax.Y(h)), (ax.X(edges[i + 1]), ax.Y(h))]
    inner += polyline(pts, INK, sw=1.6)
    inner += line(ax.X(EX["r"]), ax.y0, ax.X(EX["r"]), ax.y0 + ax.h, stroke=INK, sw=1.2)
    inner += line(ax.X(EX["rho"]), ax.y0, ax.X(EX["rho"]), ax.y0 + ax.h, stroke=SOFT, sw=1.2, dash="4,3")
    s += f'<g clip-path="url(#c2)">{inner}</g>'
    s += mono(ax.X(EX["r"]) + 6, ax.y0 + 12, f"r = {EX['r']:.3f}", size=8.4, fill=INK, anchor="start", weight="600")
    s += mono(ax.X(EX["rho"]) - 6, ax.y0 + 12, f"ρ = {EX['rho']:.3f}", size=8.4, fill=SOFT, anchor="end")
    lo, hi = IV["percentile"]
    for v, lab, anc in ((lo, f"2.5% point of r*: {lo:.3f}", "start"), (hi, f"97.5% point of r*: {hi:.3f}", "end")):
        s += line(ax.X(v), ax.Y(0) + 2, ax.X(v), ax.Y(0) + 10, stroke=MUTED, sw=1.6)
        s += mono(ax.X(v) + (-4 if anc == "start" else 4), ax.Y(0) + 32, lab, size=8.2, fill=MUTED, anchor=anc)
    t = EX["true"]
    s += note_lines(728, 112, [
        ("bootstrap, 10,000 replicates", MUTED), (f"SD {EX['se_boot']:.4f}, mean {EX['mean_boot']:.4f}", MUTED),
        (f"{EX['below']:,} below r ({pct(EX['p0'])}): z0 = {num(EX['z0'], 3)}", MUTED), ("", INK),
        ("true, 1,000,000 samples of 15", INK), (f"SD {t['se']:.4f}, mean {t['mean']:.4f}", INK),
        (f"{pct(t['p_below_rho'])} below ρ", INK), ("", INK),
        ("normal theory, (1 − r²)/√(n − 3)", SOFT), (f"SD {EX['se_normal_theory']:.4f}", SOFT), ("", INK),
        ("both skewed left: a correlation", MUTED), ("near 0.8 has more room below", MUTED), ("than above", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("bootstrap replicates r*", "band:" + MUTED + ":0.40"), ("true sampling distribution of r", "line:" + INK + ":1.6"),
                              ("ρ, all 82 (r is the solid line)", "dash:" + SOFT + ":1.2")])
    return emit("02", "bootstrap-against-truth", "The bootstrap copies the sampling distribution's shape",
                "Bootstrap replicates of the 15 schools' correlation against the true sampling distribution of r, measured by drawing "
                "fresh samples of 15 from the 82.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 500
    rows = sorted(zip(EX["schools"], EX["jackknife"]), key=lambda t: -t[1])
    s = eyebrow(32, 40, "the jackknife: the 15 schools' correlation recomputed with each school left out in turn")
    top, rh = 100, 21
    ax = Axes(170, top, 470, rh * len(rows), (0.70, 0.92), (0, 1))
    for v in (0.72, 0.76, 0.80, 0.84, 0.88, 0.92):
        s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE, sw=0.8)
        s += mono(ax.X(v), ax.y0 + ax.h + 15, f"{v:.2f}", size=8, fill=SOFT)
    s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "correlation with that school left out", size=8.5, fill=SOFT, anchor="end")
    jm = EX["jack_mean"]
    s += line(ax.X(jm), ax.y0 - 8, ax.X(jm), ax.y0 + ax.h, stroke=INK, sw=1.1, dash="3,3")
    s += mono(ax.X(jm), ax.y0 - 12, f"jackknife mean {jm:.4f}", size=8.4, fill=INK)
    for i, (sch, v) in enumerate(rows):
        y = top + i * rh + rh / 2
        col = ACCENT if sch == 6 else INK
        s += mono(ax.x0 - 14, y + 3, f"school {sch}", size=8.6, fill=col, anchor="end", weight="600" if sch == 6 else "400")
        s += line(ax.X(jm), y, ax.X(v), y, stroke=MUTED, sw=1.4)
        s += dot(ax.X(v), y, 3.6, fill=col)
        if sch == 6:
            s += mono(ax.X(v) - 2, y - 9, f"{v:.4f}", size=8.6, fill=ACCENT, anchor="middle", weight="600")
    sig = lambda v: num(float(f"{v:.4g}"), max(0, 3 - math.floor(math.log10(abs(v)))))   # four significant figures
    s += note_lines(686, 120, [
        ("d = jackknife mean − each value", MUTED), ("", INK),
        (f"Σd² = {sig(S2)}", INK), (f"Σd³ = {sig(S3)}", INK), ("", INK),
        ("a = Σd³ / (6 (Σd²)^1.5)", LINK), (f"  = {num(EX['a'], 5)}", LINK), ("", INK),
        (f"school 6: d = {num(D6, 4)}", ACCENT), (f"d³ = {sig(D6 ** 3)}", ACCENT),
        (f"{round(100 * D6 ** 3 / S3)}% of Σd³, {round(100 * D6 ** 2 / S2)}% of Σd²", ACCENT), ("", INK),
        ("the other 14 partly cancel:", MUTED), ("one school sets the sign", MUTED), ("and the size of a", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("leave-one-out correlation", "dot:" + INK + ":3.6"), ("school 6", "dot:" + ACCENT + ":3.6"),
                              ("distance d from the jackknife mean", "line:" + MUTED + ":1.4")])
    return emit("03", "jackknife-acceleration", "One school sets the acceleration",
                "Each school's leave-one-out correlation, sorted. BCa's acceleration a is the skewness of these values, "
                "and school 6 supplies all of it.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "seven 95% intervals for the correlation of the same 15 schools, from the same 10,000 replicates")
    top, rh = 104, 38
    ax = Axes(250, top, 560, rh * len(LAW_ORDER), (-0.55, 1.15), (0, 1))
    s += rect(ax.X(1.0), ax.y0 - 6, ax.X(1.15) - ax.X(1.0), ax.h + 6, fill=PAPER2, stroke="none", sw=0)
    s += mono(ax.X(1.075), ax.y0 - 23, "above 1:", size=8, fill=SOFT)
    s += mono(ax.X(1.075), ax.y0 - 12, "impossible", size=8, fill=SOFT)
    for v in (-0.5, -0.25, 0, 0.25, 0.5, 0.75, 1.0):
        s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE, sw=0.8)
        s += mono(ax.X(v), ax.y0 + ax.h + 15, num(v, 2), size=8, fill=SOFT)
    s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
    s += line(ax.X(EX["r"]), ax.y0 - 4, ax.X(EX["r"]), ax.y0 + ax.h, stroke=INK, sw=1.1)
    s += line(ax.X(EX["rho"]), ax.y0 - 4, ax.X(EX["rho"]), ax.y0 + ax.h, stroke=SOFT, sw=1.1, dash="4,3")
    s += mono(ax.X(EX["r"]) + 4, ax.y0 + ax.h + 32, f"r = {EX['r']:.3f}; ρ = {EX['rho']:.3f} (dashed)", size=8.4, fill=INK, anchor="start")
    for i, key in enumerate(LAW_ORDER):
        y = top + i * rh + rh / 2
        lo, hi = IV[key]
        s += mono(ax.x0 - 16, y + 3, NAMES[key], size=8.8, fill=STYLE[key][0], anchor="end", weight="600")
        s += hinterval(ax, lo, hi, y, key, clip_lo=-0.55, clip_hi=1.15, est=EX["r"])
        s += mono(836, y + 3, f"{num(lo, 3)} to {hi:.3f}", size=8.8, fill=STYLE[key][0], anchor="start", weight="600")
    s += legend(vh - 24, vw, [("r, the estimate (each row's dot)", "line:" + INK + ":1.1"), ("ρ, the 82 schools", "dash:" + SOFT + ":1.1")])
    return emit("04", "seven-intervals", "One sample, seven answers",
                "The percentile, BCa, basic, normal, studentized (raw and on Fisher's scale) and Fisher z intervals for the law-school "
                "correlation. The dot is r.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 440
    s = eyebrow(32, 40, "the real world and the bootstrap world, with the law-school numbers on every edge")
    w, h = 204, 60
    xs = (40, 406, 772)
    yt, yb = 96, 300
    s += eyebrow(xs[0], yt - 14, "real world", fill=SOFT)
    s += eyebrow(xs[0], yb - 14, "bootstrap world", fill=SOFT)
    s += mono(xs[1] + w / 2, yt - 14, "happens once", size=8, fill=SOFT)
    s += mono(xs[1] + w / 2, yb - 14, "repeat as often as you like", size=8, fill=SOFT)
    s += node(xs[0], yt, w, h, "82 law schools", f"population F · ρ = {EX['rho']:.3f}", kind="store")
    s += node(xs[1], yt, w, h, "the sample of 15", f"r = {EX['r']:.3f}", kind="backend")
    s += node(xs[2], yt, w, h, "sampling distribution of r", f"SD {EX['true']['se']:.3f} around ρ", kind="store")
    s += node(xs[0], yb, w, h, "the 15 as the population", "mass 1/15 on each school", kind="input")
    s += node(xs[1], yb, w, h, "a resample of 15", f"first draw: r* = {EX['first_resample']['r']:.3f}", kind="backend")
    s += node(xs[2], yb, w, h, "bootstrap distribution of r*", f"SD {EX['se_boot']:.3f} around r", kind="focal")
    for y in (yt + h / 2, yb + h / 2):
        s += hline(xs[0] + w, xs[1] - 2, y)
        s += hline(xs[1] + w, xs[2] - 2, y)
    s += alabel((xs[0] + w + xs[1]) / 2, yt + h / 2, "draw 15 with replacement", w=156)
    s += alabel((xs[1] + w + xs[2]) / 2, yt + h / 2, "over all samples", w=110)
    s += alabel((xs[0] + w + xs[1]) / 2, yb + h / 2, "draw 15 with replacement", w=156)
    s += alabel((xs[1] + w + xs[2]) / 2, yb + h / 2, f"repeat B = {EX['B']:,}", w=110)
    # Down from the sample, across a clear band, down onto the bootstrap population's top edge: no box border is ridden.
    x1, x2, ym, r = xs[1] + w / 2, xs[0] + w * 0.62, yt + h + 50, 8
    s += (f'<path d="M {x1} {yt + h} V {ym - r} Q {x1} {ym} {x1 - r} {ym} H {x2 + r} Q {x2} {ym} {x2} {ym + r} V {yb - 2}" '
          f'fill="none" stroke="{ACCENT}" stroke-width="1" marker-end="url(#arrow-accent)"/>')
    s += mono((x1 + x2) / 2, ym - 8, "the sample plays the population", size=8.6, fill=ACCENT, weight="600")
    s += vline(xs[2] + w / 2, yb - 2, yt + h + 2, stroke=LINK, dash="4,3", marker="arrow-link")
    s += mono(xs[2] + w / 2 - 10, (yt + h + yb) / 2 - 4, "the bet: r* − r", size=8.6, fill=LINK, anchor="end", weight="600")
    s += mono(xs[2] + w / 2 - 10, (yt + h + yb) / 2 + 10, "behaves like r − ρ", size=8.6, fill=LINK, anchor="end", weight="600")
    s += note_lines(40, vh - 50, [
        ("Where the bet fails: the bootstrap population holds only the sample's 15 schools, so nothing outside them can ever be drawn.",
         MUTED)], gap=15)
    return emit("05", "bootstrap-world", "The bootstrap swaps the population for the sample",
                "Top: the process an interval needs to know about, which happens once. Bottom: the same process with the sample "
                "in the population's place, which can be repeated.", "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 500
    z0, a = EX["z0"], EX["a"]
    bca = lambda z: z0 + (z0 + z) / (1 - a * (z0 + z))
    bc = lambda z: 2 * z0 + z
    zl, zh = -2.9, 2.9
    assert all(1 - a * (z0 + z) > 0.5 for z in (zl, zh))
    s = eyebrow(32, 40, "how BCa moves the percentile levels, for the law schools' bias correction and acceleration, on a probit scale")
    ax = Axes(110, 90, 440, 330, (zl, zh), (-3.2, 3.2))
    levels = (0.005, 0.025, 0.1, 0.5, 0.9, 0.975, 0.995)
    zt = [N01.inv_cdf(p) for p in levels]
    fl = lambda z: f"{100 * N01.cdf(z):g}%"
    s += ax.clip("c6") + title(ax.x0, ax.y0 - 16, "adjusted level read from the replicates")
    s += ax.frame(zt, zt, xlab="nominal level", xfmt=fl, yfmt=fl, grid_x=True)
    xs = [zl + (zh - zl) * i / 300 for i in range(301)]
    inner = polyline(curve(ax, xs, xs), SOFT, sw=1.4, dash="5,3")
    inner += polyline(curve(ax, xs, [bc(z) for z in xs]), MUTED, sw=1.6)
    inner += polyline(curve(ax, xs, [bca(z) for z in xs]), LINK, sw=2.0)
    s += f'<g clip-path="url(#c6)">{inner}</g>'
    # Short labels placed inside gridline-free cells (below the 0.5% line; between the 97.5% and 99.5% verticals).
    for p, dy in ((0.025, 15), (0.975, 6)):
        z = N01.inv_cdf(p)
        lv = EX["bca_levels"][0 if p < 0.5 else 1]
        assert abs(N01.cdf(bca(z)) - lv) < 1e-5
        s += line(ax.X(z), ax.Y(z), ax.X(z), ax.Y(bca(z)), stroke=LINK, sw=1.0, dash="2,2")
        s += dot(ax.X(z), ax.Y(bca(z)), 3.6, fill=LINK)
        s += mono(ax.X(z) + 6, ax.Y(bca(z)) + dy, f"{100 * lv:.2f}%", size=8.6, fill=LINK, anchor="start", weight="600")
    blo, bhi = N01.cdf(bc(-Z)), N01.cdf(bc(Z))
    s += note_lines(600, 112, [
        ("percentile: the diagonal, levels unchanged", SOFT), ("", INK),
        (f"BC (a = 0): every level shifted by 2z0", MUTED), (f"  2.5% → {100 * blo:.2f}%, 97.5% → {100 * bhi:.2f}%", MUTED), ("", INK),
        ("BCa: shifted by z0 and bent by a", LINK), (f"  2.5% → {100 * EX['bca_levels'][0]:.2f}%, 97.5% → {100 * EX['bca_levels'][1]:.2f}%", LINK),
        ("", INK),
        ("a < 0: the standard error shrinks as ρ", MUTED), ("grows, so the lower tail is stretched", MUTED),
        ("more than the upper one is pulled in", MUTED), ("", INK),
        (f"BCa interval: the replicates' {100 * EX['bca_levels'][0]:.2f}% and", INK),
        (f"{100 * EX['bca_levels'][1]:.2f}% points, {IV['bca'][0]:.3f} to {IV['bca'][1]:.3f}", INK)], gap=16)
    s += legend(vh - 24, vw, [("percentile (no change)", "dash:" + SOFT), ("BC, z0 only", "line:" + MUTED + ":1.6"),
                              ("BCa, z0 and a", "line:" + LINK + ":2.0")])
    return emit("06", "bca-levels", "z0 shifts the levels, a bends them",
                "The percentile level each method reads from the bootstrap replicates, against the nominal level, for the law-school "
                "values of z0 and a.", "how each interval works", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 470
    R = CO["R"]
    s = eyebrow(32, 40, f"{R:,} samples of 15 from the 82 schools, {CO['B']:,} replicates each: how often each 95% interval contains ρ = 0.760")
    top, rh = 104, 36
    ax = Axes(250, top, 300, rh * len(LAW_ORDER), (0.78, 0.98), (0, 1))
    for v in (0.80, 0.85, 0.90, 0.95):
        s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE, sw=0.8)
        s += mono(ax.X(v), ax.y0 + ax.h + 15, pct(v, 0), size=8, fill=SOFT)
    s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
    s += line(ax.X(0.95), ax.y0 - 6, ax.X(0.95), ax.y0 + ax.h, stroke=INK, sw=1.1, dash="4,3")
    s += title(ax.x0, ax.y0 - 16, "coverage (bar: ±2 MCSE)")
    bx = Axes(606, top, 260, rh * len(LAW_ORDER), (-0.2, 0.2), (0, 1))
    s += rect(bx.X(-0.025), bx.y0 - 6, bx.X(0.025) - bx.X(-0.025), bx.h + 6, fill=PAPER2, stroke="none", sw=0)
    for v, lab in ((-0.2, "20%"), (-0.1, "10%"), (0, "0"), (0.1, "10%"), (0.2, "20%")):
        s += line(bx.X(v), bx.y0, bx.X(v), bx.y0 + bx.h, stroke=RULE, sw=0.8)
        s += mono(bx.X(v), bx.y0 + bx.h + 15, lab, size=8, fill=SOFT)
    s += line(bx.x0, bx.y0 + bx.h, bx.x0 + bx.w, bx.y0 + bx.h, stroke=RULE_SOLID)
    s += line(bx.X(0), bx.y0 - 6, bx.X(0), bx.y0 + bx.h, stroke=RULE_SOLID, sw=1.0)
    s += title(bx.X(-0.2), bx.y0 - 16, "misses: interval below ρ | above ρ")
    s += mono(bx.X(0.2), bx.y0 + bx.h + 32, "shaded: the 2.5% each side a 95% interval allows", size=8.2, fill=SOFT, anchor="end")
    for i, key in enumerate(LAW_ORDER):
        m = CM[key]
        y = top + i * rh + rh / 2
        col = STYLE[key][0]
        s += mono(ax.x0 - 16, y + 3, NAMES[key], size=8.8, fill=col, anchor="end", weight="600")
        c, e = m["coverage"], 2 * m["mcse"]
        s += line(ax.X(c - e), y, ax.X(c + e), y, stroke=col, sw=2.4)
        s += dot(ax.X(c), y, 4.0, fill=col)
        near = 0.925 < c < 0.95                          # keep the label off the 95% line
        s += mono(ax.X(c) + (-10 if near else 10), y - 6, pct(c), size=8.4, fill=col, anchor="end" if near else "start", weight="600")
        lo_w, hi_w = m["rho_above"], m["rho_below"]       # interval below rho (too low) | interval above rho (too high)
        s += rect(bx.X(-lo_w), y - 7, bx.X(0) - bx.X(-lo_w), 14, fill=col, op=0.55, stroke="none", sw=0)
        s += rect(bx.X(0), y - 7, bx.X(hi_w) - bx.X(0), 14, fill=col, op=0.55, stroke="none", sw=0)
        s += mono(bx.X(-lo_w) - 6, y + 3, pct(lo_w), size=8, fill=MUTED, anchor="end")
        s += mono(bx.X(hi_w) + 6, y + 3, pct(hi_w), size=8, fill=MUTED, anchor="start")
        s += mono(996, y + 3, (pct(m["upper_above_1"]) if m["upper_above_1"] > 0 else "never"), size=8, fill=SOFT, anchor="end")
    s += mono(996, top - 16, "upper limit above 1", size=8.2, fill=SOFT, anchor="end")
    s += legend(vh - 24, vw, [("coverage, ±2 MCSE", "dot:" + INK + ":4.0"), ("share of samples missed", "band:" + INK + ":0.55"),
                              ("95% nominal", "dash:" + INK + ":1.1"), ("2.5% per side allowed", "band:" + PAPER2 + ":1.0")])
    return emit("07", "law-school-coverage", "Only the widest intervals reach 95%",
                "Actual coverage of seven 95% intervals for the correlation, measured by drawing fresh samples of 15 from the 82-school "
                "population, with the misses split by side.", "coverage, measured", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 500
    Bs = (1000, 2000, 10000)
    s = eyebrow(32, 40, "the same 15 schools bootstrapped 200 times at each B: how far each endpoint moves from run to run")
    ax = Axes(110, 96, 520, 290, (900, 11000), (0.0008, 0.05), xmap=math.log10, ymap=math.log10)
    s += ax.clip("c8") + title(ax.x0, ax.y0 - 16, "standard deviation over 200 reruns (log scale)")
    s += ax.frame(Bs, [0.001, 0.002, 0.005, 0.01, 0.02, 0.05], xlab="replicates B (log scale)",
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{v:g}", grid_x=True)
    series = (("BCa lower limit", [ESD[str(b)]["bca"][0] for b in Bs], LINK, None),
              ("percentile lower limit", [ESD[str(b)]["percentile"][0] for b in Bs], INK, None),
              ("BCa upper limit", [ESD[str(b)]["bca"][1] for b in Bs], LINK, "5,3"),
              ("bootstrap SE", [ESD[str(b)]["se"] for b in Bs], SOFT, "1.5,2.5"),
              ("percentile upper limit", [ESD[str(b)]["percentile"][1] for b in Bs], INK, "5,3"))
    inner = ""
    for lab, ys, col, dash in series:
        inner += polyline(curve(ax, Bs, ys), col, sw=1.8, dash=dash)
        for b, v in zip(Bs, ys):
            inner += dot(ax.X(b), ax.Y(v), 3.2, fill=col)
    guide = ESD["10000"]["bca"][0]
    inner += line(ax.X(2000), ax.Y(guide), ax.X(10000), ax.Y(guide), stroke=ACCENT, sw=1.0, dash="2,2")
    s += f'<g clip-path="url(#c8)">{inner}</g>'
    labels = sorted(((ys[-1], lab, col) for lab, ys, col, _ in series), reverse=True)
    yl = []
    for v, lab, col in labels:
        y = ax.Y(v) + 3
        if yl and y - yl[-1] < 13:
            y = yl[-1] + 13
        yl.append(y)
        s += mono(ax.X(10000) + 14, y, f"{lab} {v:.4f}", size=8.2, fill=col, anchor="start", weight="600")
        if lab == "BCa lower limit":
            s += mono(ax.X(10000) + 14, y + 13, f"≈ percentile lower at 2,000, {ESD['2000']['percentile'][0]:.4f} (dotted)", size=8.2,
                      fill=ACCENT, anchor="start")
            yl.append(y + 13)
    s += note_lines(40, vh - 58, [
        (f"BCa's lower limit is the {100 * EX['bca_levels'][0]:.2f}% point: at B = 2,000 about {round(EX['bca_levels'][0] * 2000)} replicates lie below it. "
         "Every SD falls roughly like 1/√B.", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("BCa limit", "line:" + LINK + ":1.8"), ("percentile limit", "line:" + INK + ":1.8"),
                              ("upper limits (dashed)", "dash:" + INK + ":1.8"), ("bootstrap SE", "dotted:" + SOFT)])
    return emit("08", "monte-carlo-error-by-b", "BCa's lower limit needs five times the replicates",
                "Monte Carlo standard deviation of each endpoint, and of the bootstrap standard error, over 200 reruns on the same data, "
                "against the number of replicates.", "how many resamples", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 440
    s = eyebrow(32, 40, f"mean customer spend: coverage of six 95% intervals, {SP['by_n']['30']['R']:,} samples at n = 30 and "
                        f"{SP['by_n']['100']['R']:,} at n = 100")
    top, rh = 110, 34
    panels = (("30", 210), ("100", 640))
    for nn, x0 in panels:
        mm = SP["by_n"][nn]["methods"]
        frac = SP["by_n"][nn]["with_top"] / SP["by_n"][nn]["R"]
        ax = Axes(x0, top, 300, rh * len(SPEND_ORDER), (0.15, 1.0), (0, 1))
        s += title(ax.x0, ax.y0 - 30, f"n = {nn}: {pct(frac)} of samples hold a top-1% customer")
        for v in (0.2, 0.4, 0.6, 0.8, 1.0):
            s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE, sw=0.8)
            s += mono(ax.X(v), ax.y0 + ax.h + 15, pct(v, 0), size=8, fill=SOFT)
        s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
        s += line(ax.X(0.95), ax.y0 - 8, ax.X(0.95), ax.y0 + ax.h, stroke=INK, sw=1.1, dash="4,3")
        s += mono(ax.X(0.95), ax.y0 - 12, "95%", size=8, fill=INK)
        for i, key in enumerate(SPEND_ORDER):
            y = top + i * rh + rh / 2
            m = mm[key]
            if nn == "30":
                s += mono(ax.x0 - 16, y + 3, NAMES[key], size=8.8, fill=INK, anchor="end", weight="600")
            lo, hi, al = m["by_flag"]["0"], m["by_flag"]["1"], m["coverage"]
            s += line(ax.X(lo), y, ax.X(hi), y, stroke=RULE_SOLID, sw=1.2)
            s += dot(ax.X(lo), y, 4.2, fill=PAPER, stroke=ACCENT, sw=1.8)
            s += dot(ax.X(hi), y, 3.6, fill=MUTED)
            s += dot(ax.X(al), y, 4.2, fill=INK)
            s += mono(ax.X(al), y - 9, pct(al), size=8.2, fill=INK, weight="600")
    flag = lambda nn, g: [SP["by_n"][nn]["methods"][k]["by_flag"][g] for k in SPEND_ORDER]
    lo30, lo100, hi_all = flag("30", "0"), flag("100", "0"), flag("30", "1") + flag("100", "1")
    s += note_lines(40, vh - 72, [
        (f"Top 1%: the {SP['top1_count']} customers who spent £{SP['top1_threshold']:,.0f} or more. Without one, a sample's bootstrap world "
         f"has no large customer to resample: its intervals cover", MUTED),
        (f"{pct(min(lo30), 0)} to {pct(max(lo30), 0)} at n = 30 and {pct(min(lo100), 0)} to {pct(max(lo100), 0)} at n = 100. With one, "
         f"{pct(min(hi_all), 0)} to {pct(max(hi_all), 0)}. Overall coverage is the mix of the two.", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("all samples", "dot:" + INK + ":4.2"), ("samples without a top-1% customer", "ring:" + ACCENT + ":4.2"),
                              ("samples with one", "dot:" + MUTED + ":3.6"), ("95%", "dash:" + INK + ":1.1")])
    return emit("09", "skewed-mean-coverage", "The bootstrap cannot resample what the sample lacks",
                "Coverage of the t-interval and five bootstrap intervals for mean customer spend, overall and split by whether the "
                "sample contains one of the 44 largest customers.", "the skewed mean", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "five tank serial numbers, 58, 171, 272, 273, 303, from N = 342: the cdf of the maximum, true and bootstrapped")
    ax = Axes(96, 96, 560, 290, (0, 360), (0, 1.0))
    s += ax.clip("c10") + title(ax.x0, ax.y0 - 16, "P(maximum ≤ m)")
    s += ax.frame([0, 50, 100, 150, 200, 250, 300, 350], [0, 0.25, 0.5, 0.75, 1.0], xlab="serial number m",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:.2f}")
    sup, pmf = TK["true_support"], TK["true_pmf"]
    acc, pts = 0.0, [(ax.X(0), ax.Y(0)), (ax.X(sup[0]), ax.Y(0))]
    for m, p in zip(sup, pmf):
        acc += p
        pts.append((ax.X(m), ax.Y(acc)))
    assert abs(acc - 1) < 1e-4 and abs(sum(p for m, p in zip(sup, pmf) if m <= 303) - TK["true_p_le_m"]) < 1e-5
    pts.append((ax.X(360), ax.Y(1)))
    inner = polyline(pts, INK, sw=1.8)
    cdf, serials = 0.0, TK["serials"]
    bpts = [(ax.X(0), ax.Y(0))]
    for v, p in zip(serials, TK["boot_pmf"]):
        bpts += [(ax.X(v), ax.Y(cdf)), (ax.X(v), ax.Y(cdf + p))]
        cdf += p
    bpts.append((ax.X(360), ax.Y(1)))
    inner += polyline(bpts, ACCENT, sw=2.0)
    inner += line(ax.X(342), ax.y0, ax.X(342), ax.y0 + ax.h, stroke=INK, sw=1.1, dash="4,3")
    s += f'<g clip-path="url(#c10)">{inner}</g>'
    s += mono(ax.X(342) - 4, ax.y0 + ax.h - 8, "N = 342", size=8.4, fill=INK, anchor="end", weight="600")
    yj = ax.Y(0.85)                                              # inside the jump, well above the true curve
    s += line(ax.X(303) - 112, yj, ax.X(303) - 3, yj, stroke=ACCENT, sw=1.0, marker="arrow-accent")
    s += mono(ax.X(303) - 116, yj + 3, f"jump of {TK['point_mass']:.3f} at 303", size=8.4, fill=ACCENT, anchor="end", weight="600")
    s += dot(ax.X(303), ax.Y(TK["true_p_le_m"]), 3.2, fill=INK)
    s += mono(ax.X(303) - 10, ax.Y(TK["true_p_le_m"]) - 8, f"true: {TK['true_p_le_m']:.3f} at 303", size=8.4, fill=INK, anchor="end")
    s += note_lines(700, 112, [
        ("bootstrap: every resample of the", ACCENT), ("five serials, 5^5 = 3,125 of them", ACCENT),
        ("P*(max = 303) = 1 − (4/5)^5 = 0.672", ACCENT), ("nothing above 303, ever", ACCENT), ("", INK),
        (f"true: P(max = 303) = {TK['true_pmf_at_m']:.4f}", INK), ("smooth, and runs to 342", INK), ("", INK),
        ("the bootstrap's mass at the maximum", MUTED), (f"n = 5: {TK['point_mass']:.3f}", MUTED),
        (f"n = 100: {UN['100']['point_mass']:.3f}", MUTED), (f"limit 1 − 1/e = {MX['uniform']['limit_point_mass']:.3f}", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("bootstrap cdf of the maximum", "line:" + ACCENT + ":2.0"),
                              ("true cdf of the maximum, N = 342", "line:" + INK + ":1.8"), ("N", "dash:" + INK + ":1.1")])
    return emit("10", "tank-maximum", "Two thirds of the bootstrap mass sits on 303",
                "The cumulative distribution of the largest of five serial numbers: exactly, over every capture from 342 tanks, and "
                "over every bootstrap resample of the five serials observed.", "where the bootstrap fails", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 430
    s = eyebrow(32, 40, "95% intervals for the number of tanks N from the serials 58, 171, 272, 273 and 303, beside the truth, N = 342")
    rows = (("percentile", TK["percentile"], STYLE["percentile"], TK["coverage"]["percentile"], "pct"),
            ("BCa, z0 from the strict share", TK["bca"]["strict"], STYLE["bca"], TK["coverage"]["bca"], "pct"),
            ("BCa, mid-rank z0 (SciPy)", TK["bca"]["midrank"], (LINK, 1.6, "5,3"), TK["coverage"]["bca"], "pct"),
            ("basic", TK["basic"], STYLE["basic"], TK["coverage"]["basic"], "pct"),
            ("exact, one-sided 95%", TK["exact_one_sided"], (MUTED, 1.8, None), 0.95, "ge"),
            ("exact, 2.5% each side", TK["exact"], (MUTED, 1.6, "5,3"), 0.975, "ge"))
    top, rh = 100, 40
    ax = Axes(250, top, 500, rh * len(rows), (150, 660), (0, 1))
    for v in (200, 300, 400, 500, 600):
        s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE, sw=0.8)
        s += mono(ax.X(v), ax.y0 + ax.h + 15, f"{v}", size=8, fill=SOFT)
    s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
    s += line(ax.X(303), ax.y0 - 4, ax.X(303), ax.y0 + ax.h, stroke=SOFT, sw=1.1)
    s += line(ax.X(342), ax.y0 - 4, ax.X(342), ax.y0 + ax.h, stroke=INK, sw=1.1, dash="4,3")
    s += mono(ax.X(303) - 4, ax.y0 + ax.h + 32, "largest serial 303", size=8.4, fill=SOFT, anchor="end")
    s += mono(ax.X(342) + 4, ax.y0 + ax.h + 32, "N = 342 (dashed)", size=8.4, fill=INK, anchor="start", weight="600")
    s += mono(990, top - 14, "coverage of N over all captures", size=8.2, fill=SOFT, anchor="end")
    s += mono(772, top - 14, "interval", size=8.2, fill=SOFT, anchor="start")
    for i, (lab, (lo, hi), (col, sw, dash), cov, kind) in enumerate(rows):
        y = top + i * rh + rh / 2
        s += mono(ax.x0 - 16, y + 3, lab, size=8.8, fill=col, anchor="end", weight="600")
        s += line(ax.X(lo), y, ax.X(hi), y, stroke=col, sw=sw + 0.8, dash=dash)
        s += line(ax.X(lo), y - 6, ax.X(lo), y + 6, stroke=col, sw=1.4) + line(ax.X(hi), y - 6, ax.X(hi), y + 6, stroke=col, sw=1.4)
        s += mono(772, y + 3, f"{lo} to {hi}", size=8.4, fill=col, anchor="start")
        s += mono(990, y + 3, (f"{100 * cov:.2f}%" if kind == "pct" else f"at least {100 * cov:g}%"), size=8.8, fill=col, anchor="end", weight="600")
    s += legend(vh - 24, vw, [("percentile", "style:percentile"), ("BCa", "style:bca"), ("basic", "style:basic"),
                              ("exact, from the distribution of the maximum", "line:" + MUTED + ":1.8")])
    return emit("11", "tank-intervals", "Every percentile-type interval stops at the largest serial",
                "Bootstrap and exact 95% intervals for N from five captured serials, and how often each method contains N over every "
                "possible capture of five tanks from 342.", "where the bootstrap fails", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
COPY_COL = (SOFT, MUTED, INK, LINK)


def fig12():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "a Pareto population with tail index 1.5: mean 3, infinite variance")
    s += title(40, 84, "bootstrap distributions of the mean, three samples of 100, by copies of the largest value")
    ph, gap = 100, 34
    for j, sh in enumerate(SH):
        y0 = 104 + j * (ph + gap)
        edges = sh["edges"]
        hist = sh["hist_by_copies"]
        tot = [sum(col[i] for col in hist) for i in range(len(edges) - 1)]
        ax = Axes(40, y0, 420, ph, (edges[0], edges[-1]), (0, max(tot) * 1.08))
        s += line(ax.x0, ax.y0 + ax.h, ax.x0 + ax.w, ax.y0 + ax.h, stroke=RULE_SOLID)
        for i in range(len(edges) - 1):
            base = 0
            for c in range(4):
                h = hist[c][i]
                if h:
                    s += rect(ax.X(edges[i]) + 0.4, ax.Y(base + h), ax.X(edges[i + 1]) - ax.X(edges[i]) - 0.8, ax.Y(base) - ax.Y(base + h),
                              fill=COPY_COL[c], op=0.75, stroke="none", sw=0)
                base += h
        ticks = [round(edges[0] + (edges[-1] - edges[0]) * k / 4, 1) for k in range(5)]
        for v in ticks:
            if edges[0] <= v <= edges[-1]:
                s += mono(ax.X(v), ax.y0 + ax.h + 13, f"{v:.1f}", size=7.6, fill=SOFT)
        share_var = 1 - (sh["sd_rest"] / sh["boot_sd"]) ** 2
        s += mono(ax.x0 + ax.w + 12, y0 + 16, f"sample {j + 1}: largest {sh['max']:.1f}", size=8.4, fill=INK, anchor="start", weight="600")
        s += mono(ax.x0 + ax.w + 12, y0 + 31, f"{pct(sh['max_share'])} of the sum", size=8.2, fill=MUTED, anchor="start")
        s += mono(ax.x0 + ax.w + 12, y0 + 46, f"bootstrap SD {sh['boot_sd']:.3f};", size=8.2, fill=MUTED, anchor="start")
        s += mono(ax.x0 + ax.w + 12, y0 + 61, f"{sh['sd_rest']:.3f} from the other 99", size=8.2, fill=MUTED, anchor="start")
        s += mono(ax.x0 + ax.w + 12, y0 + 76, f"one value: {pct(share_var, 0)} of the variance", size=8.2, fill=MUTED, anchor="start")
    rest = 1 - sum(v["share"] for v in SH[0]["lumps"].values())
    s += mono(40, 104 + 3 * (ph + gap) - 8, f"Resamples with 4 or more copies ({pct(rest)} in sample 1) are not drawn.", size=8.2, fill=SOFT, anchor="start")
    cx = Axes(700, 104, 270, 300, (22, 1400), (0.6, 1.0), xmap=math.log10)
    s += title(cx.x0, cx.y0 - 20, "coverage of the mean (bar: ±2 MCSE)")
    s += cx.frame([30, 100, 300, 1000], [0.6, 0.7, 0.8, 0.9, 1.0], xlab="n (log scale)", xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: pct(v, 0), grid_x=True)
    s += line(cx.x0, cx.Y(0.95), cx.x0 + cx.w, cx.Y(0.95), stroke=INK, sw=1.1, dash="4,3")
    s += mono(cx.x0 + cx.w - 2, cx.Y(0.95) - 5, "95%", size=8, fill=INK, anchor="end")
    ns = ("30", "100", "300", "1000")
    for key in ("studentized", "bca", "percentile", "t"):
        col, sw, dash = STYLE[key]
        ys = [HB[k]["methods"][key]["coverage"] for k in ns]
        s += polyline(curve(cx, [int(k) for k in ns], ys), col, sw=sw, dash=dash)
        for k, v in zip(ns, ys):
            e = 2 * HB[k]["methods"][key]["mcse"]
            s += line(cx.X(int(k)), cx.Y(v - e), cx.X(int(k)), cx.Y(v + e), stroke=col, sw=1.2)
            s += dot(cx.X(int(k)), cx.Y(v), 2.8, fill=col)
        s += mono(cx.X(1000) + 8, cx.Y(ys[-1]) + 3, f"{pct(ys[-1])}", size=8, fill=col, anchor="start", weight="600")
    s += legend(vh - 24, vw, [("0 copies", "band:" + SOFT + ":0.75"), ("1", "band:" + MUTED + ":0.75"), ("2", "band:" + INK + ":0.75"),
                              ("3", "band:" + LINK + ":0.75"), ("studentized", "style:studentized"), ("BCa", "style:bca"),
                              ("percentile", "style:percentile"), ("t", "style:t")])
    return emit("12", "infinite-variance", "With infinite variance, a few values decide the shape",
                "Left: each sample's bootstrap distribution of the mean, coloured by how many copies of the sample's largest value a "
                "resample drew. Right: coverage of four intervals for the mean as n grows.", "where the bootstrap fails", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 470
    ex = DP["example"]
    s = eyebrow(32, 40, f"an AR(1) series with φ = {DP['phi']}, n = {DP['n']}: the first 100 values, and the first 100 of one resample")
    lo_, hi_ = -3.6, 3.6
    for j, (lab, series, col, r1, rbar) in enumerate((("the series", ex["series"], INK, ex["lag1"], DP["lag1_orig"]),
                                                     ("one resample of it", ex["resample"], ACCENT, ex["lag1_resample"], DP["lag1_resample"]))):
        y0 = 100 + j * 160
        ax = Axes(96, y0, 520, 110, (0, 99), (lo_, hi_))
        assert all(lo_ < v < hi_ for v in series)
        s += line(ax.x0, ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=RULE_SOLID, sw=0.8)
        s += polyline(curve(ax, range(len(series)), series), col, sw=1.4)
        s += title(ax.x0, y0 - 10, f"{lab}: lag-1 autocorrelation {num(r1, 2)} here, {num(rbar, 3)} on average", fill=col)
        for v in (-3, 0, 3):
            s += mono(ax.x0 - 8, ax.Y(v) + 3, num(v, 0), size=8, fill=SOFT, anchor="end")
        if j == 1:
            for t in (0, 24, 49, 74, 99):
                s += mono(ax.X(t), ax.y0 + ax.h + 15, f"{t + 1}", size=8, fill=SOFT)
            s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "position in the series", size=8.5, fill=SOFT, anchor="end")
    bx = Axes(700, 110, 260, 140, (0, 1), (0, 0.16))
    s += title(bx.x0, bx.y0 - 14, "SD of the mean")
    s += line(bx.x0, bx.y0 + bx.h, bx.x0 + bx.w, bx.y0 + bx.h, stroke=RULE_SOLID)
    vals = (("true", DP["sd_mean_exact"], INK), ("resampled", DP["se_ratio_mean"] * DP["sd_mean_exact"], ACCENT))
    for k, (lab, v, col) in enumerate(vals):
        x = bx.x0 + 30 + k * 120
        s += rect(x, bx.Y(v), 70, bx.Y(0) - bx.Y(v), fill=col, op=0.6, stroke="none", sw=0)
        s += mono(x + 35, bx.Y(v) - 6, f"{v:.4f}", size=8.6, fill=col, weight="600")
        s += mono(x + 35, bx.y0 + bx.h + 14, lab, size=8.4, fill=MUTED)
    s += note_lines(700, 300, [
        (f"resampling single values estimates", ACCENT), (f"{DP['se_ratio_mean']:.3f} of the true SD", ACCENT),
        (f"(large n: √((1 − φ)/(1 + φ)) = {DP['se_ratio_theory']:.3f})", MUTED), ("", INK),
        (f"percentile interval for the mean", INK), (f"covers {pct(DP['coverage'])} (R = {DP['R']:,})", INK)], gap=16)
    s += legend(vh - 24, vw, [("the series", "line:" + INK + ":1.4"), ("a resample", "line:" + ACCENT + ":1.4")])
    return emit("13", "dependent-data", "Resampling single values shuffles time away",
                "An autocorrelated series and one bootstrap resample of it, and the standard error of the mean that independent "
                "resampling reports.", "where the bootstrap fails", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08, "09": fig09,
        "10": fig10, "11": fig11, "12": fig12, "13": fig13}

if __name__ == "__main__":
    for k in (sys.argv[1:] or sorted(FIGS)):
        FIGS[k]()
