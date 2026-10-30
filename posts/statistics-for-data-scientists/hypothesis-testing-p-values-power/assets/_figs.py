#!/usr/bin/env python3
"""Figures 01-13 for hypothesis-testing-p-values-power.

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/testing.py.
The asserts below pin each number the article quotes, so a figure cannot drift from the text.
Run:  python3 _figs.py [01 05 ...]
"""
import json
import math
import pathlib
import sys
from statistics import NormalDist

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SANS, SOFT,
                    emit, eyebrow, mono, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
P, PW, RD, RP, F, T, ST = (CAP[k] for k in ("pvalues", "power", "retrodesign", "replication", "fpr", "tost", "stopping"))
DU, DC = RD["durante"], RD["cases"]["durante_2"]
N01 = NormalDist()
SIG_C, WRONG_C = ACCENT, LINK             # significant with the right sign; significant with the wrong sign

# The numbers the article prints, held to the capture.
assert round(DU["critical"], 2) == 15.88 and round(DU["z_obs"], 3) == 2.099 and round(DU["p_obs"], 4) == 0.0358
assert (round(DC["exact"]["p_hi"], 4), round(DC["exact"]["p_lo"], 4), round(DC["exact"]["power"], 4)) == (0.0434, 0.0137, 0.0570)
assert round(DC["exact"]["typeS"], 3) == 0.240 and round(DC["exact"]["exaggeration"], 2) == 9.54 and round(DU["min_exaggeration"], 2) == 7.94
assert round(DC["mean_abs_sig"], 2) == 19.08 and round(DU["mean_sig_pos"], 2) == 19.19 and round(DU["mean_sig_neg"], 2) == -18.72
assert round(100 * P["z"]["durante"]["power_exact"], 1) == 5.7 and round(P["z"]["durante"]["median_exact"], 3) == 0.487
assert round(P["z"]["lam2"]["median_exact"], 3) == 0.045 and round(P["z"]["lam28"]["median_exact"], 4) == 0.0051
assert P["dance"]["n_sig"] == 19 and round(P["dance"]["p_max"], 2) == 0.33 and round(P["dance"]["p_min"], 5) == 0.00007
assert [round(100 * ST["exact"]["at"][k], 2) for k in ("2", "5", "10", "100", "1000")] == [8.31, 14.17, 19.33, 37.36, 52.99]
assert round(PW["design"]["crit"], 3) == 2.042 and round(PW["design"]["t_at_p03"], 2) == 2.28 and round(100 * PW["design"]["power"], 2) == 78.14
assert round(100 * PW["design"]["beta"], 1) == 21.9
assert [PW["sample_sizes"][f"d{d}_p80"]["n"] for d in ("1", "0.8", "0.5", "0.2")] == [17, 26, 64, 394]
assert round(PW["observed_power"]["table"]["0.05"], 2) == 0.50 and round(PW["observed_power"]["table"]["0.2"], 2) == 0.25
assert round(RD["at_power"]["0.5"]["exaggeration"], 2) == 1.41 and round(RD["at_power"]["0.1"]["exaggeration"], 2) == 3.71
assert round(RP["mean_r_orig"], 3) == 0.396 and round(RP["mean_r_rep"], 3) == 0.197 and RP["pairs"] == 97
assert RP["nonsig"]["n"] == 63 and RP["nonsig"]["equivalent_0.1"] == 2 and RP["nonsig"]["equivalent_0.2"] == 17
assert round(F["tree"]["fpr"], 2) == 0.36 and round(F["benjamin"]["at_power1_05"], 4) == 0.3333
assert (round(100 * F["equals"]["0.03"]["fpr_prior05"], 1), round(100 * F["equals"]["0.03"]["fpr_prior01"], 1)) == (16.7, 64.3)
assert (round(100 * F["equals"]["0.05"]["fpr_prior05"], 1), round(100 * F["equals"]["0.05"]["fpr_prior01"], 1)) == (26.6, 76.6)
assert T["sample_sizes"]["0.5"]["tost"] == 69 and T["sample_sizes"]["0.5"]["nhst"] == 64 and T["sample_sizes"]["0.1"]["tost"] == 1713
assert round(100 * T["power_bound05"][0]["power"], 1) == 0.8
assert round(T["bound80"]["16"]["tost_exact"], 2) == 1.06 and round(T["bound80"]["69"]["tost_exact"], 2) == 0.50
assert round(T["bound80"]["1713"]["tost_exact"], 2) == 0.10 and round(T["bound80"]["16"]["detectable"], 2) == 1.02


# ------------------------------------------------------------------ drawing helpers (Part 4's set)
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


def plate(x, y, s, size=8.5, fill=MUTED, anchor="middle", weight="400"):
    """Text on an opaque plate, for labels that sit beside lines in a plot."""
    w = 0.62 * size * len(str(s)) + 10
    x0 = {"middle": x - w / 2, "start": x - 5, "end": x - w + 5}[anchor]
    return (f'<rect x="{x0:.1f}" y="{y - size - 2:.1f}" width="{w:.1f}" height="{size + 7}" rx="2" fill="{PAPER}"/>'
            + mono(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight))


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
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1])
        elif part[0] == "interval":
            s += line(x + 8, y - 1, x + 8, y + 11, stroke=part[1], sw=float(part[2]) if len(part) > 2 else 1.6)
        elif part[0] == "hinterval":                     # a horizontal interval with its estimate
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.6) + dot(x + 9, y + 5, 3.0, fill=part[1])
        elif part[0] == "cross":
            s += line(x + 3, y + 5, x + 15, y + 5, stroke=part[1], sw=2.2) + line(x + 9, y - 1, x + 9, y + 11, stroke=part[1], sw=2.2)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 26
    return s


def pct(v, nd=1):
    return f"{100 * v:.{nd}f}%"


def num(v, nd=1):
    """A number with thousands separators and a true minus sign."""
    return f"{v:,.{nd}f}".replace("-", "−")


def curve(ax, xs, ys):
    return [(ax.X(a), ax.Y(b)) for a, b in zip(xs, ys)]


def npdf(x, mu, sd):
    return N01.pdf((x - mu) / sd) / sd


log10 = math.log10


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 470
    A, s_ = DC["A"], DC["s"]
    crit = DU["critical"]
    s = eyebrow(32, 40, "replications of the 2013 design: standard error 8.1 points, a plausible true effect of 2 points")
    ax = Axes(96, 96, 620, 280, (-42, 42), (0, 0.056))
    s += ax.clip("c1") + title(ax.x0, ax.y0 - 16, "density of the replicated estimate, percentage points")
    s += ax.frame([-40, -30, -20, -10, 0, 10, 20, 30, 40], [0, 0.01, 0.02, 0.03, 0.04, 0.05],
                  xlab="estimated difference in voting preference (points)", xfmt=lambda v: num(v, 0), yfmt=lambda v: f"{v:.2f}")
    xs = [-42 + 84 * i / 840 for i in range(841)]
    right = [x for x in xs if x >= crit]
    left = [x for x in xs if x <= -crit]
    inner = area([(ax.X(crit), ax.Y(0))] + [(ax.X(x), ax.Y(npdf(x, A, s_))) for x in right] + [(ax.X(right[-1]), ax.Y(0))], SIG_C, 0.55)
    inner += area([(ax.X(left[0]), ax.Y(0))] + [(ax.X(x), ax.Y(npdf(x, A, s_))) for x in left] + [(ax.X(-crit), ax.Y(0))], WRONG_C, 0.55)
    inner += polyline([(ax.X(x), ax.Y(npdf(x, 0, s_))) for x in xs], SOFT, sw=1.2, dash="5,3")
    inner += polyline([(ax.X(x), ax.Y(npdf(x, A, s_))) for x in xs], INK, sw=1.8)
    for v in (crit, -crit):
        inner += line(ax.X(v), ax.y0 + 16, ax.X(v), ax.Y(0), stroke=MUTED, sw=1.0, dash="4,3")
    inner += line(ax.X(A), ax.Y(npdf(A, A, s_)), ax.X(A), ax.Y(0), stroke=INK, sw=0.8, dash="2,3")
    inner += line(ax.X(17), ax.Y(0), ax.X(17), ax.Y(0.0172), stroke=INK, sw=1.2)
    s += f'<g clip-path="url(#c1)">{inner}</g>'
    s += mono(ax.X(crit) + 6, ax.y0 + 26, f"+{crit:.2f} = 1.96 × 8.1", size=8.5, fill=MUTED, anchor="start")
    s += mono(ax.X(-crit) - 6, ax.y0 + 26, f"−{crit:.2f}", size=8.5, fill=MUTED, anchor="end")
    s += mono(ax.X(A), ax.Y(0.0522), "true effect 2", size=8.5, fill=INK)
    s += mono(ax.X(17) + 4, ax.Y(0.0182), "published 17", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(ax.X(24), ax.Y(0.0062), pct(DC["exact"]["p_hi"], 2), size=9, fill=SIG_C, anchor="start", weight="600")
    s += mono(ax.X(-24), ax.Y(0.0062), pct(DC["exact"]["p_lo"], 2), size=9, fill=WRONG_C, anchor="end", weight="600")
    s += note_lines(752, ax.y0 + 14, [
        ("if the true effect is 2", INK), (f"signal / noise λ = 2 / 8.1 = {DC['lam']:.3f}", MUTED), ("", INK),
        (f"significant, right sign {pct(DC['exact']['p_hi'], 2)}", SIG_C), (f"significant, wrong sign {pct(DC['exact']['p_lo'], 2)}", WRONG_C),
        (f"power {pct(DC['exact']['power'], 2)}", INK), (f"type S {pct(DC['exact']['typeS'], 1)} of the significant", INK), ("", INK),
        ("mean significant estimate", MUTED), (f"+{DU['mean_sig_pos']:.2f} or {num(DU['mean_sig_neg'], 2)}", MUTED),
        (f"mean magnitude {DC['mean_abs_sig']:.2f}", INK), (f"exaggeration {DC['mean_abs_sig']:.2f} / 2 = {DC['exact']['exaggeration']:.2f}", INK), ("", INK),
        (f"never below {crit:.2f} / 2 = {DU['min_exaggeration']:.2f}", MUTED), ("", INK),
        ("dashed: no effect; under it", SOFT), (f"p for 17 is {DU['p_obs']:.4f}", SOFT)], gap=15)
    s += legend(vh - 24, vw, [("if the true effect is 2", "line:" + INK), ("if there is no effect", "dash:" + SOFT),
                              ("significant, right sign", "band:" + SIG_C + ":0.55"), ("significant, wrong sign", "band:" + WRONG_C + ":0.55")])
    return emit("01", "significance-bar", "What a significant result from this design looks like",
                "The 2013 study's estimate of 17 points had a standard error of 8.1. If the true effect were the plausible 2 "
                "points, only the two shaded tails would be significant.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 438
    keys = [("null", "λ = 0 (no effect)"), ("durante", "λ = 0.247 (the example)"), ("lam1", "λ = 1"), ("lam2", "λ = 2"), ("lam28", "λ = 2.8")]
    s = eyebrow(32, 40, f"p-values of a two-sided z-test, {P['z']['null']['R']:,} simulated tests per panel, in 20 bins of width 0.05")
    pw, gap = 166, 22
    for i, (k, name) in enumerate(keys):
        d = P["z"][k]
        ax = Axes(72 + i * (pw + gap), 104, pw, 210, (0, 1), (0, 0.85))
        s += title(ax.x0, ax.y0 - 16, name, size=8.6)
        s += ax.frame([0, 0.5, 1], [0, 0.2, 0.4, 0.6, 0.8], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:.1f}", ylabels=(i == 0))
        for j, (h, ex) in enumerate(zip(d["hist"], d["exact_bins"])):
            x0, x1 = ax.X(j * 0.05) + 0.6, ax.X((j + 1) * 0.05) - 0.6
            col, op = (SIG_C, 0.85) if j == 0 else (MUTED, 0.45)
            s += rect(x0, ax.Y(h), x1 - x0, ax.Y(0) - ax.Y(h), fill=col, op=op, stroke="none", sw=0)
            s += line(x0 - 0.4, ax.Y(ex), x1 + 0.4, ax.Y(ex), stroke=INK, sw=1.2)
        med = d["median_exact"]
        s += mono(ax.x0 + ax.w, ax.y0 + 40, f"p ≤ .05: {pct(d['power_exact'], 1)}", size=8.3, fill=SIG_C, anchor="end", weight="600")
        s += mono(ax.x0 + ax.w, ax.y0 + 54, f"median p {med:.3f}" if med >= 0.01 else f"median p {med:.4f}", size=8.3, fill=INK, anchor="end")
    s += mono(72, 104 + 210 + 34, "p-value in each panel; bars: share of the simulated tests in each bin", size=8.5, fill=SOFT, anchor="start")
    s += note_lines(72, 374, [("Under no effect every bin holds 5%: the p-value is uniform, and P(p ≤ .05) = 5% is the test's whole promise. "
                               "At the example's λ the bins still hold about 5%,", MUTED),
                              ("so its p-value says almost nothing about the effect. The first bar is the power at 5%.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("simulated share, p ≤ .05", "band:" + SIG_C + ":0.85"), ("simulated share, other bins", "band:" + MUTED + ":0.45"),
                              ("exact probability", "line:" + INK + ":1.2")])
    return emit("02", "p-value-distributions", "The distribution of a p-value",
                "For a z-test the p-value's distribution depends only on λ, the true effect over its standard error.",
                "the distribution of p", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 500
    d = P["dance"]
    n = len(d["p"])
    s = eyebrow(32, 40, f"one experiment run {n} times: 16 per group, true difference 1 SD, power {pct(PW['design']['power'], 1)}")
    ax = Axes(130, 96, 560, 14 * n, (-0.6, 2.6), (n + 0.5, 0.5))
    s += title(ax.x0, ax.y0 - 16, "estimated difference (SD units) with its 95% interval")
    s += ax.frame([-0.5, 0, 0.5, 1.0, 1.5, 2.0, 2.5], [], xfmt=lambda v: num(v, 1), grid_y=False, ylabels=False)
    s += line(ax.X(0), ax.y0, ax.X(0), ax.y0 + ax.h, stroke=SOFT, sw=1.0, dash="4,3")
    s += line(ax.X(1), ax.y0, ax.X(1), ax.y0 + ax.h, stroke=INK, sw=1.0, dash="2,3")
    s += mono(ax.X(1), ax.y0 - 4, "true 1", size=8, fill=INK)
    s += mono(ax.X(0), ax.y0 - 4, "0", size=8, fill=SOFT)
    s += mono(ax.x0 + ax.w + 28, ax.y0 - 4, "p", size=8.5, fill=SOFT, anchor="start", weight="600")
    s += mono(ax.x0 - 14, ax.y0 - 4, "run", size=8.5, fill=SOFT, anchor="end", weight="600")
    for i in range(n):
        y = ax.Y(i + 1)
        sig = d["p"][i] <= 0.05
        col = SIG_C if sig else MUTED
        s += line(ax.X(d["lo"][i]), y, ax.X(d["hi"][i]), y, stroke=col, sw=1.6)
        s += dot(ax.X(d["diff"][i]), y, 3.0, fill=col)
        pv = d["p"][i]
        ptxt = f"{pv:.5f}" if pv < 0.001 else f"{pv:.4f}" if pv < 0.01 else f"{pv:.3f}"
        s += mono(ax.x0 + ax.w + 28, y + 3, ptxt, size=8.2, fill=INK if sig else MUTED, anchor="start", weight="600" if sig else "400")
        s += mono(ax.x0 - 14, y + 3, str(i + 1), size=8, fill=SOFT, anchor="end")
    s += note_lines(812, ax.y0 + 20, [
        (f"{d['n_sig']} of {n} significant", INK), (f"p from {d['p_min']:.5f}", INK), (f"to {d['p_max']:.2f}", INK), ("", INK),
        ("same design, same truth;", MUTED), ("only the sample differs", MUTED), ("", INK),
        ("Cumming's 80% interval", MUTED), ("for a replication's", MUTED), ("one-tailed p after", MUTED), ("an original p = .05:", MUTED),
        (f"{P['cumming']['lo']:.5f} to {P['cumming']['hi']:.2f}", INK),
        (f"simulated: {pct(P['cumming']['inside'], 2)} inside", MUTED), (f"(± {100 * P['cumming']['inside_mcse']:.2f})", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("significant at 5%", "hinterval:" + SIG_C), ("not significant", "hinterval:" + MUTED),
                              ("true difference", "dotted:" + INK), ("no difference", "dash:" + SOFT)])
    return emit("03", "dance-of-p-values", "Twenty-five runs of one experiment",
                "Each row is a fresh simulated experiment from the same design: the estimate, its 95% confidence interval and its p-value.",
                "the distribution of p", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 470
    ex, sim = ST["exact"], ST["simulated"]
    looks = [1, 2, 3, 5, 10, 20, 50, 100, 200, 500, 1000]
    s = eyebrow(32, 40, "a 5% two-sided z-test (known variance) repeated after every new observation, stopping at the first rejection")
    ax = Axes(96, 96, 620, 280, (1, 1000), (0, 0.6), xmap=log10)
    s += ax.clip("c4") + title(ax.x0, ax.y0 - 16, "probability of rejecting a true null at some look")
    s += ax.frame(looks, [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], xlab="number of looks (log scale)", xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: f"{100 * v:.0f}%")
    inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    inner += polyline([(ax.X(k), ax.Y(a)) for k, a in zip(ex["looks"], ex["alpha"])], INK, sw=1.8)
    s += f'<g clip-path="url(#c4)">{inner}</g>'
    for k in looks:
        s += dot(ax.X(k), ax.Y(sim["at"][str(k)]), 3.2, fill=PAPER, stroke=ACCENT)
    for k, dy in (("2", -14), ("5", -14), ("10", -14), ("100", -16), ("1000", 22)):
        s += mono(ax.X(int(k)), ax.Y(ex["at"][k]) + dy, pct(ex["at"][k], 2), size=8.5, fill=INK, weight="600")
    s += mono(ax.x0 + ax.w - 4, ax.Y(0.05) + 14, "nominal 5%", size=8.5, fill=SOFT, anchor="end")
    tp, sm = ST["t_peeking"], ST["simmons"]
    s += note_lines(752, ax.y0 + 20, [
        ("exact: the running sum's", INK), ("distribution carried forward", INK), ("on a grid, look by look", INK), ("", INK),
        (f"circles: {sim['R']:,} simulated paths;", ACCENT), (f"largest gap {sim['max_z']:.1f} MCSE", ACCENT), ("", INK),
        ("two t-test versions, simulated:", MUTED), ("look after every added pair,", MUTED),
        (f"{tp['n_from']} to {tp['n_to']} per group: {pct(tp['alpha'], 1)}", INK),
        ("test at 20 per group, add 10", MUTED), (f"if p > .05, test again: {pct(sm['alpha'], 2)}", INK), ("", INK),
        ("with unlimited looks the rate", MUTED), ("goes to 100%", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("exact", "line:" + INK), (f"simulated ({sim['R']:,} paths)", "ring:" + ACCENT), ("nominal 5%", "dash:" + SOFT)])
    return emit("04", "optional-stopping", "What peeking does to a 5% test",
                "The test is repeated after each new observation and stopped at the first p ≤ .05; the null is true throughout.",
                "the distribution of p", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 470
    dz = PW["design"]
    tg, h0, h1 = dz["t_grid"], dz["h0"], dz["h1"]
    c, t03 = dz["crit"], dz["t_at_p03"]
    s = eyebrow(32, 40, "the pooled t statistic for 16 per group (30 degrees of freedom): no difference, or a true difference of 1 SD")
    ax = Axes(96, 96, 620, 280, (-4.5, 8.0), (0, 0.42))
    s += ax.clip("c5") + title(ax.x0, ax.y0 - 16, "density of the t statistic")
    s += ax.frame([-4, -2, 0, 2, 4, 6, 8], [0, 0.1, 0.2, 0.3, 0.4], xlab="t", xfmt=lambda v: num(v, 0), yfmt=lambda v: f"{v:.1f}")
    pts = list(zip(tg, h0, h1))
    inner = area([(ax.X(c), ax.Y(0))] + [(ax.X(t), ax.Y(b)) for t, a, b in pts if t >= c] + [(ax.X(8.0), ax.Y(0))], LINK, 0.16)
    inner += area([(ax.X(t03), ax.Y(0))] + [(ax.X(t), ax.Y(a)) for t, a, b in pts if t >= t03] + [(ax.X(8.0), ax.Y(0))], ACCENT, 0.75)
    inner += area([(ax.X(-4.5), ax.Y(0))] + [(ax.X(t), ax.Y(a)) for t, a, b in pts if t <= -t03] + [(ax.X(-t03), ax.Y(0))], ACCENT, 0.75)
    inner += polyline([(ax.X(t), ax.Y(a)) for t, a, b in pts], MUTED, sw=1.8)
    inner += polyline([(ax.X(t), ax.Y(b)) for t, a, b in pts], LINK, sw=1.8)
    for v in (c, -c):
        inner += line(ax.X(v), ax.y0 + 34, ax.X(v), ax.Y(0), stroke=INK, sw=1.0, dash="4,3")
    inner += line(ax.X(t03), ax.Y(0.07), ax.X(t03), ax.Y(0), stroke=ACCENT, sw=1.4)
    s += f'<g clip-path="url(#c5)">{inner}</g>'
    s += mono(ax.X(c), ax.y0 + 26, f"+{c:.3f}", size=8.5, fill=INK)
    s += mono(ax.X(-c), ax.y0 + 26, f"−{c:.3f}", size=8.5, fill=INK)
    s += mono(ax.X(t03) + 5, ax.Y(0.078), f"observed t = {t03:.2f}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.X(0), ax.Y(0.41), "no difference (H₀)", size=8.5, fill=MUTED)
    s += mono(ax.X(dz["ncp"]) + 10, ax.Y(0.385), f"true difference 1 SD (noncentral, λ = {dz['ncp']:.2f})", size=8.5, fill=LINK, anchor="start")
    s += mono(ax.X(5.6), ax.Y(0.12), f"power {pct(dz['power'], 2)}", size=9, fill=LINK, weight="600")
    s += note_lines(752, ax.y0 + 20, [
        ("Neyman and Pearson, before", INK), ("the data:", INK), (f"reject when |t| ≥ {c:.3f}", INK),
        ("α = 5% (null beyond the bars)", MUTED), (f"power {pct(dz['power'], 2)}, β {pct(dz['beta'], 1)}", LINK), ("", INK),
        ("Fisher, after the data:", INK), (f"p = P(|T| ≥ {t03:.2f} under H₀)", ACCENT), ("= 3%, the orange tails", ACCENT), ("", INK),
        ("neither is P(H₀ is true)", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("null density", "line:" + MUTED), ("alternative density", "line:" + LINK), ("power", "band:" + LINK + ":0.16"),
                              ("p for t = 2.28", "band:" + ACCENT + ":0.75"), ("5% bars", "dash:" + INK)])
    return emit("05", "fisher-and-neyman-pearson", "Two readings of one test",
                "Colquhoun's design: two groups of 16, a 5% two-sided pooled t-test, and a true difference of one standard deviation.",
                "power", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 470
    cv = PW["curves"]
    ns = cv["n"]
    s = eyebrow(32, 40, "power of a 5% two-sided pooled two-sample t-test against the sample size per group")
    ax = Axes(96, 96, 620, 280, (2, 400), (0, 1.0), xmap=log10)
    s += ax.clip("c6") + title(ax.x0, ax.y0 - 16, "power")
    s += ax.frame([2, 5, 10, 20, 50, 100, 200, 400], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="n per group (log scale)",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%")
    styles = {"1": LINK, "0.8": MUTED, "0.5": INK, "0.2": SOFT}
    inner = line(ax.x0, ax.Y(0.8), ax.x0 + ax.w, ax.Y(0.8), stroke=SOFT, sw=1.0, dash="4,3")
    for dk, col in styles.items():
        assert all(v == v for v in cv[f"d{dk}"]), f"NaN in the exact curve for d = {dk}"
        inner += polyline(curve(ax, ns, cv[f"normal_d{dk}"]), col, sw=1.1, dash="5,3")
        inner += polyline(curve(ax, ns, cv[f"d{dk}"]), col, sw=1.9)
        n80 = PW["sample_sizes"][f"d{dk}_p80"]["n"]
        inner += line(ax.X(n80), ax.Y(0.8), ax.X(n80), ax.Y(0), stroke=col, sw=0.8, dash="1.5,2.5")
    s += f'<g clip-path="url(#c6)">{inner}</g>'
    for sm in PW["sims"]:
        s += dot(ax.X(sm["n"]), ax.Y(sm["sim"]), 3.0, fill=PAPER, stroke=styles["1" if sm["d"] == 1.0 else f"{sm['d']:g}"])
    s += dot(ax.X(16), ax.Y(PW["design"]["power"]), 4.2, fill=ACCENT)
    s += mono(ax.X(16) - 6, ax.Y(0.875), f"16 per group: {pct(PW['design']['power'], 2)}", size=8.5, fill=ACCENT,
              anchor="end", weight="600")
    s += mono(ax.x0 + ax.w - 4, ax.Y(0.8) - 6, "80%", size=8.5, fill=SOFT, anchor="end")
    rows = [("n per group for 80% power,", INK), ("curves left to right:", INK)]
    rows += [(f"d = {dk}: {PW['sample_sizes'][f'd{dk}_p80']['n']}", styles[dk]) for dk in ("1", "0.8", "0.5", "0.2")]
    rows += [("(the dotted verticals)", MUTED), ("", INK), ("dashed: normal approximation,", MUTED),
             (f"{PW['checks'][0]['normal']:.4f} at 16 per group", MUTED), (f"against the exact {PW['checks'][0]['by_hand']:.4f}", MUTED), ("", INK),
             (f"circles: simulated, R = {CAP['provenance']['replications']['power_sim']:,}", MUTED), (f"largest gap {PW['sims_max_z']:.1f} MCSE", MUTED)]
    s += note_lines(752, ax.y0 + 20, rows, gap=15)
    s += legend(vh - 24, vw, [("exact (noncentral t)", "line:" + INK), ("normal approximation", "dash:" + INK), ("simulated", "ring:" + INK),
                              ("the running design", "dot:" + ACCENT + ":4.2")])
    return emit("06", "power-curves", "Power against sample size",
                "Exact power from the noncentral t, its normal approximation, and simulated checks, for four standardised effect sizes.",
                "power", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 430
    op = PW["observed_power"]
    s = eyebrow(32, 40, "observed power: the power computed at the effect the data estimated, for the same data's p-value")
    ax = Axes(96, 96, 620, 250, (1e-4, 1.0), (0, 1.0), xmap=log10)
    s += ax.clip("c7") + title(ax.x0, ax.y0 - 16, "observed power")
    s += ax.frame([1e-4, 1e-3, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="p-value of the test (log scale)",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%")
    inner = line(ax.X(0.05), ax.y0, ax.X(0.05), ax.Y(0), stroke=SOFT, sw=1.0, dash="4,3")
    inner += line(ax.x0, ax.Y(0.5), ax.x0 + ax.w, ax.Y(0.5), stroke=SOFT, sw=0.8, dash="2,3")
    inner += polyline(curve(ax, op["p"], op["t30"]), LINK, sw=1.4, dash="5,3")
    inner += polyline(curve(ax, op["p"], op["z"]), INK, sw=1.9)
    s += f'<g clip-path="url(#c7)">{inner}</g>'
    for k, dx, dy, anc in (("0.001", -8, 18, "end"), ("0.05", 8, -8, "start"), ("0.2", 8, -8, "start"), ("0.5", -10, 18, "end")):
        v = op["table"][k]
        s += dot(ax.X(float(k)), ax.Y(v), 3.6, fill=INK)
        s += mono(ax.X(float(k)) + dx, ax.Y(v) + dy, f"p = {k}: {v:.2f}", size=8.5, fill=INK, anchor=anc, weight="600")
    s += mono(ax.X(0.05) + 4, ax.y0 + 12, "p = .05", size=8.5, fill=SOFT, anchor="start")
    s += note_lines(752, ax.y0 + 20, [
        ("one number, re-expressed:", INK), ("the observed effect sets λ,", MUTED), ("and λ is a function of p", MUTED), ("", INK),
        ("p above .05 means observed", MUTED), ("power below 50%, always", MUTED), ("", INK),
        ("dashed: the 16-per-group", LINK), ("t-test, almost the same", LINK)], gap=15)
    s += legend(vh - 24, vw, [("z-test", "line:" + INK), ("t-test, 30 degrees of freedom", "dash:" + LINK)])
    return emit("07", "observed-power", "Observed power is the p-value",
                "Plugging the estimated effect into the power formula gives a number fixed by the p-value alone.",
                "power", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 490
    cv = RD["curves"]
    lam, pw_, ts, ex = cv["lam"], cv["power"], cv["typeS"], cv["exaggeration"]
    cases = RD["cases"]
    s = eyebrow(32, 40, "type S rate and exaggeration ratio for an unbiased normal estimate, as functions of λ = true effect / SE")
    labels = {"kanazawa_0.1": "Kanazawa, D = 0.1", "kanazawa_0.3": "Kanazawa, D = 0.3", "kanazawa_1.0": "Kanazawa, D = 1",
              "durante_2": "2013 study, D = 2", "power80_2.8": "80% power"}
    xt = [0.03, 0.1, 0.3, 1, 3]
    panels = (("exaggeration", "exaggeration ratio (log scale)", (1, 100), [1, 2, 5, 10, 20, 50, 100], lambda v: f"{v:g}", log10,
               {"kanazawa_0.1": (9, 4, "start"), "kanazawa_0.3": (9, 4, "start"), "kanazawa_1.0": (9, 6, "start"),
                "durante_2": (-9, 15, "end"), "power80_2.8": (6, -9, "start")}),
              ("typeS", "type S rate", (0, 0.5), [0, 0.1, 0.2, 0.3, 0.4, 0.5], lambda v: f"{100 * v:.0f}%", None,
               {"kanazawa_0.1": (9, -7, "start"), "kanazawa_0.3": (9, -12, "start"), "kanazawa_1.0": (9, 12, "start"),
                "durante_2": (9, -4, "start"), "power80_2.8": (0, -10, "middle")}))
    for i, (key, name, yr, yt, yf, ymap, offsets) in enumerate(panels):
        ax = Axes(96 + i * 470, 104, 380, 270, (0.02, 6.0), yr, xmap=log10, ymap=ymap)
        s += ax.clip(f"c8{i}") + title(ax.x0, ax.y0 - 16, name)
        s += ax.frame(xt, yt, xfmt=lambda v: f"{v:g}", yfmt=yf)
        for v in xt:     # the power each λ gives, under the λ labels
            j = min(range(len(lam)), key=lambda q: abs(lam[q] - v))
            s += mono(ax.X(v), ax.y0 + ax.h + 28, f"({pct(pw_[j], 0) if pw_[j] >= 0.1 else pct(pw_[j], 1)})", size=7.6, fill=SOFT)
        s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 44, "λ (log scale), with the power it gives", size=8.5, fill=SOFT, anchor="end")
        ys = ex if key == "exaggeration" else ts
        inner = polyline([(ax.X(a), ax.Y(b)) for a, b in zip(lam, ys) if yr[0] <= b <= yr[1] * 1.05], INK, sw=1.9)
        if key == "exaggeration":
            inner += line(ax.x0, ax.Y(1), ax.x0 + ax.w, ax.Y(1), stroke=SOFT, sw=0.8, dash="2,3")
        s += f'<g clip-path="url(#c8{i})">{inner}</g>'
        for ck, nm in labels.items():
            cs = cases[ck]
            xv, yv = cs["lam"], cs["exact"][key]
            col = ACCENT if ck == "durante_2" else INK
            s += dot(ax.X(xv), ax.Y(yv), 3.6, fill=col)
            pub = cs["published"].get(key)
            if pub is not None:
                s += dot(ax.X(xv), ax.Y(pub), 5.4, fill="none", stroke=LINK)
            dx, dy, anc = offsets[ck]
            val = f"{yv:.3g}" if key == "exaggeration" else ("1.2 × 10⁻⁶" if yv < 0.001 else pct(yv, 1))
            s += mono(ax.X(xv) + dx, ax.Y(yv) + dy, f"{nm}: {val}", size=8, fill=col, anchor=anc, weight="600" if ck == "durante_2" else "400")
    s += note_lines(96, 446, [("Rings: the values Gelman and Carlin print. Their prose gives 77, 25 and 8 for the closed form's 76.7, 25.6 and 7.75, "
                               "and their simulation gave 9.7 for 9.537.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("closed form", "line:" + INK), ("published design, closed form", "dot:" + INK + ":3.6"),
                              ("the worked example", "dot:" + ACCENT + ":3.6"), ("as printed by Gelman and Carlin", "ring:" + LINK + ":5.4")])
    return emit("08", "type-s-and-m", "Type S and M errors against power",
                "Both curves follow from λ alone; the five designs are Gelman and Carlin's examples.",
                "type S and M errors", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 590
    sc = RP["scatter"]
    s = eyebrow(32, 40, f"Reproducibility Project: Psychology, {RP['pairs']} replications with both effect sizes, as correlations r (CC0 data)")
    ax = Axes(96, 96, 420, 380, (-0.03, 1.0), (-0.6, 1.0))
    s += ax.clip("c9") + title(ax.x0, ax.y0 - 16, "replication r against original r")
    s += ax.frame([0, 0.2, 0.4, 0.6, 0.8, 1.0], [-0.6, -0.4, -0.2, 0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="original r",
                  xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: num(v, 1))
    inner = line(ax.X(0), ax.Y(0), ax.X(1), ax.Y(1), stroke=SOFT, sw=1.0, dash="4,3")
    inner += line(ax.X(-0.03), ax.Y(0), ax.X(1), ax.Y(0), stroke=MUTED, sw=0.9)
    for ro, rr, sg in zip(sc["r_orig"], sc["r_rep"], sc["sig_rep"]):
        inner += dot(ax.X(ro), ax.Y(rr), 3.4, fill=ACCENT if sg else MUTED, op=0.85 if sg else 0.55)
    s += f'<g clip-path="url(#c9)">{inner}</g>'
    s += mono(ax.X(0.93), ax.Y(0.93) - 10, "same size", size=8, fill=SOFT, anchor="end")
    xm, ym = RP["mean_r_orig"], RP["mean_r_rep"]
    s += line(ax.X(xm) - 6, ax.Y(ym), ax.X(xm) + 6, ax.Y(ym), stroke=INK, sw=2.2) + line(ax.X(xm), ax.Y(ym) - 6, ax.X(xm), ax.Y(ym) + 6, stroke=INK, sw=2.2)
    bands = RP["by_original_p"]
    bx = Axes(640, 96, 300, 300, (0, 1), (0, 0.6))
    s += title(bx.x0, bx.y0 - 16, "mean r by original p-value")
    s += bx.frame([], [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6], yfmt=lambda v: f"{v:.1f}", grid_y=True)
    for j, (k, name) in enumerate((("p_below_001", "p below .001"), ("p_001_to_05", ".001 to .05"))):
        b = bands[k]
        xc = 0.27 + 0.46 * j
        for off, val, col, op in ((-0.09, b["mean_r_orig"], MUTED, 0.45), (0.09, b["mean_r_rep"], INK, 0.85)):
            x0 = bx.X(xc + off - 0.075)
            s += rect(x0, bx.Y(val), bx.X(xc + off + 0.075) - x0, bx.Y(0) - bx.Y(val), fill=col, op=op, stroke="none", sw=0)
            s += mono(bx.X(xc + off), bx.Y(val) - 6, f"{val:.2f}", size=8.5, fill=INK, weight="600")
        s += mono(bx.X(xc), bx.y0 + bx.h + 16, name, size=8.5, fill=INK, weight="600")
        s += mono(bx.X(xc), bx.y0 + bx.h + 31, f"{b['n']} pairs, {b['replicated']} replicated", size=8, fill=MUTED)
        s += mono(bx.X(xc), bx.y0 + bx.h + 45, f"kept {pct(b['ratio'], 0)}", size=8, fill=MUTED)
    s += note_lines(96, 540, [(f"Replication smaller in {pct(RP['share_rep_below_orig'], 1)} of pairs; {RP['rep_negative']} replications changed sign. "
                               "Seven originals with p above .05 are left out of the split.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("replication significant", "dot:" + ACCENT + ":3.4:0.85"), ("not significant", "dot:" + MUTED + ":3.4:0.55"),
                              ("mean of all 97", "cross:" + INK), ("original mean", "band:" + MUTED + ":0.45"), ("replication mean", "band:" + INK + ":0.85")])
    return emit("09", "replication-effect-sizes", "Replications kept half the effect",
                "Original and replication effect sizes from the Open Science Collaboration's 2015 project, read from its CC0 data file.",
                "replications", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 460
    lt = F["less_than"]
    pri = lt["prior"]
    s = eyebrow(32, 40, "share of p ≤ .05 results that are false, against the share of tested effects that are real")
    ax = Axes(96, 96, 620, 280, (0, 1.0), (0, 1.0))
    s += ax.clip("c10") + title(ax.x0, ax.y0 - 16, "false positive risk, p ≤ .05 (p-less-than)")
    s += ax.frame([0, 0.1, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="prior probability that the effect is real",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%")
    floor = [0.05 * (1 - p) / (0.05 * (1 - p) + p) for p in pri]
    assert abs(0.05 * (10 / 11) / (0.05 * (10 / 11) + 1 / 11) - F["benjamin"]["at_power1_05"]) < 1e-5
    inner = area([(ax.X(pri[0]), ax.Y(0))] + curve(ax, pri, floor) + [(ax.X(pri[-1]), ax.Y(0))], LINK, 0.12)
    inner += polyline(curve(ax, pri, lt["power20"]), SOFT, sw=1.9)
    inner += polyline(curve(ax, pri, lt["power80"]), INK, sw=1.9)
    for v in (0.1, 0.5):
        inner += line(ax.X(v), ax.y0, ax.X(v), ax.Y(0), stroke=SOFT, sw=0.8, dash="2,3")
    s += f'<g clip-path="url(#c10)">{inner}</g>'
    j10, j50 = pri.index(0.1), pri.index(0.5)
    s += dot(ax.X(0.1), ax.Y(lt["power80"][j10]), 4.0, fill=ACCENT)
    s += dot(ax.X(0.1), ax.Y(lt["power20"][j10]), 3.4, fill=SOFT)
    s += dot(ax.X(0.5), ax.Y(lt["power80"][j50]), 3.4, fill=INK)
    s += mono(ax.X(0.1) + 8, ax.Y(lt["power20"][j10]) + 4, f"{pct(lt['power20'][j10], 0)} at 20% power", size=8.5, fill=MUTED, anchor="start", weight="600")
    s += mono(ax.X(0.16), ax.Y(0.30), f"Colquhoun's tree: {pct(lt['power80'][j10], 0)}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += line(ax.X(0.158), ax.Y(0.31), ax.X(0.1) + 4, ax.Y(lt["power80"][j10]) - 2, stroke=ACCENT, sw=0.8)
    s += mono(ax.X(0.5) + 6, ax.Y(0.09), f"even odds: {pct(lt['power80'][j50], 1)}", size=8.5, fill=INK, anchor="start")
    s += mono(ax.X(0.62), ax.Y(0.205), "power 20%", size=8.5, fill=SOFT, anchor="start", weight="600")
    s += mono(ax.X(0.2), ax.Y(0.02), "no power reaches this band", size=8, fill=LINK, anchor="start")
    s += note_lines(752, ax.y0 + 20, [
        ("shaded: below the risk at", LINK), ("power 1, which no study beats", LINK), ("", INK),
        (f"50% power at prior 0.1: {pct(lt['power50'][j10], 0)}", MUTED), ("", INK),
        ("prior odds 1:10 (Benjamin", MUTED), ("et al., for psychology):", MUTED), (f"{pct(F['benjamin']['at_power1_05'], 1)} at power 1,", INK),
        (f"{pct(F['benjamin']['at_power08_05'], 1)} at 80%;", INK), (f"{pct(F['benjamin']['at_power1_005'], 1)} if α = .005", INK), ("", INK),
        ("dotted verticals: priors", MUTED), ("0.1 and 0.5", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("power 80%", "line:" + INK), ("power 20%", "line:" + SOFT), ("below the power-1 floor", "band:" + LINK + ":0.12")])
    return emit("10", "false-positive-risk", "How many significant results are false",
                "α(1 − π) / (α(1 − π) + (1 − β)π) at α = 0.05, the complement of Ioannidis's positive predictive value.",
                "false positives", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 470
    ec = F["equals_curve"]
    ps = ec["p"]
    s = eyebrow(32, 40, "false positive risk of one observed p in the 16-per-group design (power 78.14%), two ways, two priors")
    ax = Axes(96, 96, 620, 280, (1e-4, 0.2), (0, 1.0), xmap=log10)
    s += ax.clip("c11") + title(ax.x0, ax.y0 - 16, "false positive risk")
    s += ax.frame([1e-4, 1e-3, 0.005, 0.01, 0.03, 0.05, 0.1, 0.2], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="observed p (log scale)",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%")
    inner = ""
    for v in (0.03, 0.05):
        inner += line(ax.X(v), ax.y0, ax.X(v), ax.Y(0), stroke=SOFT, sw=0.8, dash="2,3")
    inner += polyline(curve(ax, ps, ec["less_prior01"]), MUTED, sw=1.3, dash="5,3")
    inner += polyline(curve(ax, ps, ec["less_prior05"]), MUTED, sw=1.6)
    inner += polyline(curve(ax, ps, ec["prior01"]), ACCENT, sw=1.6, dash="5,3")
    inner += polyline(curve(ax, ps, ec["prior05"]), ACCENT, sw=2.0)
    s += f'<g clip-path="url(#c11)">{inner}</g>'
    eq = F["equals"]
    spots = {("0.05", "fpr_prior01"): (-7, -8, "end"), ("0.03", "fpr_prior01"): (-7, -8, "end"), ("0.001", "fpr_prior01"): (-7, -8, "end"),
             ("0.05", "fpr_prior05"): (7, 16, "start"), ("0.03", "fpr_prior05"): (7, 16, "start")}
    for (k, prk), (dx, dy, anc) in spots.items():
        v = eq[k][prk]
        s += dot(ax.X(float(k)), ax.Y(v), 3.4, fill=ACCENT)
        s += mono(ax.X(float(k)) + dx, ax.Y(v) + dy, pct(v, 1), size=8.5, fill=ACCENT, anchor=anc, weight="600")
    s += dot(ax.X(0.001), ax.Y(eq["0.001"]["fpr_prior05"]), 3.4, fill=ACCENT)
    s += mono(ax.X(0.03) - 4, ax.y0 + 12, "p = .03", size=8, fill=SOFT, anchor="end")
    s += mono(ax.X(0.05) + 4, ax.y0 + 12, ".05", size=8, fill=SOFT, anchor="start")
    s += note_lines(752, ax.y0 + 20, [
        ("p-equals (orange): the density", ACCENT), ("of the observed t under each", ACCENT), ("hypothesis, a likelihood ratio", ACCENT),
        (f"p = .05: ratio {eq['0.05']['lr']:.2f}", INK), (f"p = .03: ratio {eq['0.03']['lr']:.2f}", INK),
        (f"p = .001: ratio {eq['0.001']['lr']:.1f}, risk", INK), (f"{pct(eq['0.001']['fpr_prior05'], 1)} and {pct(eq['0.001']['fpr_prior01'], 1)}", INK), ("", INK),
        ("p-less-than (grey): every", MUTED), ("result at or below p, with", MUTED), ("the power at that threshold", MUTED), ("", INK),
        ("solid: prior 0.5; dashed: 0.1", INK)], gap=15)
    s += legend(vh - 24, vw, [("p-equals, prior 0.5", "line:" + ACCENT), ("p-equals, prior 0.1", "dash:" + ACCENT),
                              ("p-less-than, prior 0.5", "line:" + MUTED + ":1.6"), ("p-less-than, prior 0.1", "dash:" + MUTED + ":1.3")])
    return emit("11", "p-equals-and-p-less-than", "The risk behind one observed p",
                "The p-equals risk uses the likelihood ratio of the t actually observed; the p-less-than risk treats every result at or below p alike.",
                "false positives", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 470
    b80 = T["bound80"]
    ns = [int(k) for k in b80]
    s = eyebrow(32, 40, "two one-sided tests at 5% each (TOST) when the true difference is 0, beside what an ordinary 5% test detects; 80% power")
    ax = Axes(96, 104, 420, 270, (6, 2000), (0.08, 2.0), xmap=log10, ymap=log10)
    s += ax.clip("c12a") + title(ax.x0, ax.y0 - 16, "narrowest bound ±Δ that TOST establishes (SD units)")
    s += ax.frame([8, 16, 32, 69, 100, 200, 500, 1000, 2000], [0.1, 0.2, 0.5, 1.0, 2.0], xlab="n per group (log scale)",
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{v:g}")
    inner = line(ax.x0, ax.Y(1.0), ax.x0 + ax.w, ax.Y(1.0), stroke=LINK, sw=1.0, dash="4,3")
    inner += polyline([(ax.X(n), ax.Y(b80[str(n)]["detectable"])) for n in ns], INK, sw=1.4, dash="5,3")
    inner += polyline([(ax.X(n), ax.Y(b80[str(n)]["tost_exact"])) for n in ns], ACCENT, sw=2.0)
    s += f'<g clip-path="url(#c12a)">{inner}</g>'
    for n in ns:
        s += dot(ax.X(n), ax.Y(b80[str(n)]["tost_exact"]), 3.2, fill=ACCENT)
    for n, dx, dy, anc in ((16, 8, -10, "start"), (69, 8, -10, "start")):
        v = b80[str(n)]["tost_exact"]
        s += mono(ax.X(n) + dx, ax.Y(v) + dy, f"{n:,} per group: ±{v:.2f}", size=8.3, fill=ACCENT, anchor=anc, weight="600")
    v = b80["1713"]["tost_exact"]
    s += mono(ax.X(330), ax.Y(0.118), f"1,713 per group: ±{v:.2f}", size=8.3, fill=ACCENT, anchor="end", weight="600")
    s += line(ax.X(330) + 4, ax.Y(0.121), ax.X(1713) - 5, ax.Y(v) + 1, stroke=ACCENT, sw=0.8)
    s += mono(ax.x0 + ax.w - 4, ax.Y(1.0) + 14, "the design's true effect, 1 SD", size=8, fill=LINK, anchor="end")
    bx = Axes(600, 104, 330, 270, (0, 160), (0, 1.0))
    s += bx.clip("c12b") + title(bx.x0, bx.y0 - 16, "TOST power at Δ = ±0.5 SD, true difference 0")
    s += bx.frame([0, 16, 32, 50, 69, 100, 150], [0, 0.2, 0.4, 0.6, 0.8, 1.0], xlab="n per group", xfmt=lambda v: f"{v:g}",
                  yfmt=lambda v: f"{100 * v:.0f}%")
    pc, rows = T["power_curve_bound05"], T["power_bound05"]
    inner = line(bx.x0, bx.Y(0.8), bx.x0 + bx.w, bx.Y(0.8), stroke=SOFT, sw=0.8, dash="4,3")
    inner += polyline([(bx.X(n), bx.Y(v)) for n, v in zip(pc["n"], pc["exact"])], ACCENT, sw=1.8)
    s += f'<g clip-path="url(#c12b)">{inner}</g>'
    for r in rows:
        s += dot(bx.X(r["n"]), bx.Y(r["power"]), 3.2, fill=PAPER, stroke=INK)
    s += mono(bx.X(24), bx.Y(0.035), f"16 per group: {pct(rows[0]['power'], 1)}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(bx.X(69) + 6, bx.Y(rows[3]["power"]) + 16, f"69: {pct(rows[3]['power'], 1)}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(bx.x0 + bx.w - 4, bx.Y(0.8) - 6, "80%", size=8, fill=SOFT, anchor="end")
    s += note_lines(96, 428, [(f"Both panels exact (one integral over the SD estimate); circles: simulated, R = {T['size_at_bound']['R']:,}. "
                               f"With the truth on the bound, TOST rejects {pct(T['size_at_bound']['rate'], 2)}: its size is 5%.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("TOST, exact", "line:" + ACCENT), ("smallest effect an ordinary test detects", "dash:" + INK),
                              ("simulated", "ring:" + INK), ("1 SD", "dash:" + LINK + ":1.0")])
    return emit("12", "equivalence-sample-size", "What a sample size can rule out",
                "The narrowest equivalence bound each sample size establishes with 80% power, and TOST's power at ±0.5 SD, computed and simulated by the lab.",
                "no effect", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 470
    ns = RP["nonsig"]
    n = ns["n"]
    lo_all, hi_all = min(ns["lo"]), max(ns["hi"])
    ylo, yhi = math.floor(lo_all * 10) / 10, math.ceil(hi_all * 10) / 10
    s = eyebrow(32, 40, f"the {n} Reproducibility Project replications that were not significant: 90% Fisher-z intervals for r, sorted")
    ax = Axes(96, 96, 630, 290, (0.5, n + 0.5), (ylo, yhi))
    s += ax.clip("c13") + title(ax.x0, ax.y0 - 16, "replication r with its 90% interval")
    yt = [v / 10 for v in range(-8, 9, 2) if ylo <= v / 10 <= yhi]
    s += ax.frame([1, 10, 20, 30, 40, 50, 60], yt, xlab="replications, sorted by r", xfmt=lambda v: f"{v:g}", yfmt=lambda v: num(v, 1))
    inner = rect(ax.x0, ax.Y(0.2), ax.w, ax.Y(-0.2) - ax.Y(0.2), fill=ACCENT, op=0.08, stroke="none", sw=0)
    inner += rect(ax.x0, ax.Y(0.1), ax.w, ax.Y(-0.1) - ax.Y(0.1), fill=ACCENT, op=0.16, stroke="none", sw=0)
    inner += line(ax.x0, ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=MUTED, sw=0.8)
    c1 = c2 = 0
    for i, (r, lo, hi) in enumerate(zip(ns["r"], ns["lo"], ns["hi"])):
        x = ax.X(i + 1)
        if lo > -0.1 and hi < 0.1:
            col, sw = ACCENT, 2.4
            c1 += 1
        elif lo > -0.2 and hi < 0.2:
            col, sw = INK, 1.9
            c2 += 1
        else:
            col, sw = SOFT, 1.4
        inner += line(x, ax.Y(lo), x, ax.Y(hi), stroke=col, sw=sw)
        inner += dot(x, ax.Y(r), 1.9, fill=col)
    assert c1 == ns["equivalent_0.1"] and c1 + c2 == ns["equivalent_0.2"]
    s += f'<g clip-path="url(#c13)">{inner}</g>'
    s += note_lines(762, ax.y0 + 20, [
        (f"inside ±0.1: {c1}", ACCENT), (f"inside ±0.2: {c1 + c2}", INK), (f"neither: {n - c1 - c2}", SOFT), ("", INK),
        ("showing |r| below 0.1 with", MUTED), (f"80% power needs n = {ns['n_for_80_0.1']}", MUTED),
        (f"(0.2: n = {ns['n_for_80_0.2']}); the median", MUTED), (f"replication had n = {RP['median_n_rep']:.0f}", MUTED)], gap=15)
    band01 = 1 - (1 - 0.08) * (1 - 0.16)
    s += legend(vh - 24, vw, [(f"within ±0.1 ({c1})", "interval:" + ACCENT + ":2.4"), (f"within ±0.2, not ±0.1 ({c2})", "interval:" + INK + ":1.9"),
                              (f"neither ({n - c1 - c2})", "interval:" + SOFT + ":1.4"), ("±0.1 band", "band:" + ACCENT + f":{band01:.3f}"),
                              ("±0.2 band", "band:" + ACCENT + ":0.08")])
    return emit("13", "failed-replications-equivalence", "What the failed replications ruled out",
                "Each interval is a Fisher-z 90% interval for the replication's r; inside a band means equivalent to zero within that bound.",
                "no effect", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10, "11": fig11, "12": fig12, "13": fig13}

if __name__ == "__main__":
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
