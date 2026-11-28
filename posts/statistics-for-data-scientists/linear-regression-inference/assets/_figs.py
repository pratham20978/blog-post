#!/usr/bin/env python3
"""Figures 01-04 and 06-14 for linear-regression-inference (Statistics for Data Scientists, part 13).

Figure 05 is a Mermaid figure (fig-05-*.mmd, written and rendered by _fig05.py). Every value drawn here comes from the
lab's capture, ../lab/captures.json, written by lab/regression.py. The asserts pin each number the article quotes, so a
figure cannot drift from the text. Run:  python3 _figs.py [01 ...]
"""
import json
import math
import pathlib
import sys
from decimal import ROUND_HALF_UP, Decimal

from _build import ACCENT, INK, LINK, MUTED, PAPER, RULE, RULE_SOLID, SOFT, emit, eyebrow, mono, txt

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE.parent / "lab"
CAP = json.loads((LAB / "captures.json").read_text(encoding="utf-8"))
EXA, NIS, SUM, MEA, INT, ITV, CON = (CAP[k] for k in ("example", "nist", "summary", "meaning", "interaction",
                                                      "intervals", "conditions"))
EPS = 2.0 ** -52
LIGHT = "#7d9ccf"


def hp(share, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return float((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def hv(x, nd=4):
    """A number rounded half up from its stored decimal."""
    return float(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


# ------------------------------------------------------------------ the numbers the article quotes
SL = EXA["sleep"]
assert (hv(SL["unpaired"]["b"][1], 2), hv(SL["unpaired"]["se"][1], 3), hv(SL["unpaired"]["t"][1], 3)) == (1.58, 0.849, 1.861)
assert (hv(SL["paired"]["se"], 3), hv(SL["paired"]["t"], 3), hv(SL["paired"]["p"], 6)) == (0.389, 4.062, 0.002833)
LO, FI = NIS["datasets"]["Longley"], NIS["datasets"]["Filip"]
assert NIS["exact"]["matched"] == NIS["exact"]["total"] == 121
assert hv(min(LO["solvers"]["Householder QR"]["lre"]), 2) == 10.92 and hv(min(LO["solvers"]["normal equations (LU)"]["lre"]), 2) == 7.38
assert hv(min(FI["solvers"]["Householder QR"]["lre"]), 2) == 8.55
assert f"{LO['kappa_XtX']:.4e}" == "2.3612e+19"
assert (hv(SUM["r2"], 6), hv(SUM["sigma"], 3), hv(SUM["F"], 2)) == (0.995479, 304.854, 330.29)
assert (hv(SUM["aic_statsmodels"], 1), hv(SUM["aic_R"], 1)) == (233.2, 235.2)


# ------------------------------------------------------------------ drawing helpers (Part 12's set)
def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, op=None, marker=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}{o}{m}/>')


def polyline(pts, stroke, sw=1.6, dash=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}{o}/>')


def area(pts, fill, op, stroke="none", sw=0):
    return (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}" '
            f'fill-opacity="{op}" stroke="{stroke}" stroke-width="{sw}"/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None, op=None, sw=1.2):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{o}{s}/>'


def ring(x, y, rr=3.6, stroke=LINK, sw=1.5):
    return dot(x, y, rr, fill=PAPER, stroke=stroke, sw=sw)


def note_lines(x, y, items, size=8.5, gap=15, anchor="start"):
    out = ""
    for k, (t, c) in enumerate(items):
        if t:
            out += mono(x, y + k * gap, t, size=size, fill=c, anchor=anchor,
                        weight="600" if c in (INK, LINK, ACCENT) else "400")
    return out


def title(x, y, s, fill=INK, anchor="start", size=9.5):
    return mono(x, y, s, size=size, fill=fill, anchor=anchor, weight="600")


def plate(x, y, s, size=8, fill=MUTED, anchor="start", weight="400"):
    """Monospace text on an opaque plate, for labels that sit near marks."""
    w = 0.6 * size * len(str(s)) + 8
    x0 = {"start": x - 4, "middle": x - w / 2, "end": x - w + 4}[anchor]
    return (rect(x0, y - size - 2, w, size + 7, fill=PAPER, stroke="none", sw=0)
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
            s += mono(self.x0 + 4, self.y0 - 3, ylab, size=8, fill=SOFT, anchor="start")
        return s


def legend(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like this post's marks."""
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
            s += dot(x + 8, y + 5, float(part[2]), fill=part[1])
        elif part[0] == "ring":
            s += ring(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.6, stroke=part[1])
        elif part[0] == "bar":
            s += rect(x, y + 1, 18, 8, fill=part[1], op=float(part[2]), stroke=part[1], sw=0.8)
        elif part[0] == "cross":
            s += line(x + 4, y + 1, x + 12, y + 9, stroke=part[1], sw=1.4) + line(x + 12, y + 1, x + 4, y + 9, stroke=part[1], sw=1.4)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 24
    return s


def num(v, nd=1):
    return f"{v:,.{nd}f}".replace("-", "−")


def curve(ax, xs, ys):
    assert all(v == v for v in ys), "a NaN would make the browser drop the whole polyline"
    return [(ax.X(a), ax.Y(b)) for a, b in zip(xs, ys)]


def cross_mark(x, y, r=3.6, stroke=SOFT, sw=1.4):
    return line(x - r, y - r, x + r, y + r, stroke=stroke, sw=sw) + line(x + r, y - r, x - r, y + r, stroke=stroke, sw=sw)


def tq(df, p=0.975):
    """Student's t quantile by bisection on the regularised incomplete beta (stdlib only)."""
    def cdf(t):
        x = df / (df + t * t)
        ib = betainc(df / 2, 0.5, x)
        return 1 - 0.5 * ib if t > 0 else 0.5 * ib
    lo, hi = 0.0, 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) < p else (lo, mid)
    return (lo + hi) / 2


def betainc(a, b, x):
    """Regularised incomplete beta by Lentz's continued fraction (Numerical Recipes form)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x))
    if x < (a + 1) / (a + b + 2):
        return bt * _cf(a, b, x) / a
    return 1 - bt * _cf(b, a, 1 - x) / b


def _cf(a, b, x):
    tiny = 1e-300
    c, d = 1.0, 1 - (a + b) * x / (a + 1)
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((a + m2 - 1) * (a + m2))
        d = 1 + aa * d
        c = 1 + aa / c
        d = 1 / (d if abs(d) > tiny else tiny)
        h *= d * c
        aa = -(a + m) * (a + b + m) * x / ((a + m2) * (a + m2 + 1))
        d = 1 + aa * d
        c = 1 + aa / c
        d = 1 / (d if abs(d) > tiny else tiny)
        de = d * c
        h *= de
        if abs(de - 1) < 1e-15:
            break
    return h


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 520
    y, drug = SL["y"], SL["drug"]
    within = SL["within"]
    up, pr = SL["unpaired"], SL["paired"]
    s = eyebrow(32, 40, "student's ten patients, each on both drugs: the same twenty numbers in two regressions")
    axL = Axes(96, 96, 360, 300, (-0.45, 1.45), (-2.5, 6.0))
    axR = Axes(588, 96, 360, 300, (-0.45, 1.45), (-2.5, 6.0))
    for ax, head, sub in ((axL, "extra ~ drug", "a drug-2 dummy, nothing else"),
                          (axR, "extra ~ drug + patient", "nine patient dummies added; shown as each value minus its patient's mean")):
        s += title(ax.x0, ax.y0 - 32, head) + mono(ax.x0, ax.y0 - 18, sub, size=8, fill=SOFT, anchor="start")
        s += ax.frame([0, 1], [-2, 0, 2, 4, 6], xfmt=lambda v: "drug 1" if v == 0 else "drug 2", yfmt=lambda v: f"{v:g}",
                      ylab="extra hours of sleep" if ax is axL else "extra hours, within patient")
    # left: pairs as faint lines, points, group means, fitted line, +-1 sigma around each mean
    for i in range(10):
        s += line(axL.X(0), axL.Y(y[i]), axL.X(1), axL.Y(y[10 + i]), stroke=SOFT, sw=0.6, op=0.45)
    for k in range(20):
        s += dot(axL.X(drug[k]), axL.Y(y[k]), 3.6, fill=INK if drug[k] == 0 else LINK)
    m0, m1 = SL["means"]
    for xv, m in ((0, m0), (1, m1)):
        s += rect(axL.X(xv) - 22, axL.Y(m + up["sigma"]), 44, axL.Y(m - up["sigma"]) - axL.Y(m + up["sigma"]),
                  fill=SOFT, op=0.10, stroke="none", sw=0)
    s += line(axL.X(0), axL.Y(m0), axL.X(1), axL.Y(m1), stroke=ACCENT, sw=2.0)
    s += mono(axL.X(1) + 30, axL.Y(m1) + 3, f"slope {hv(up['b'][1], 2):.2f}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += note_lines(axL.x0 + 8, axL.y0 + 16, [(f"residual SD {hv(up['sigma'], 2):.2f} on {up['df']} df", INK),
                                             (f"SE {hv(up['se'][1], 3):.3f}, t = {hv(up['t'][1], 3):.3f}", INK),
                                             (f"p = {hv(up['p'][1], 4):.4f}: Student's t-test", MUTED)])
    # right: within-patient deviations
    for i in range(10):
        s += line(axR.X(0), axR.Y(within[i]), axR.X(1), axR.Y(within[10 + i]), stroke=SOFT, sw=0.6, op=0.45)
    for k in range(20):
        s += dot(axR.X(drug[k]), axR.Y(within[k]), 3.6, fill=INK if drug[k] == 0 else LINK)
    h = up["b"][1] / 2
    for xv, m in ((0, -h), (1, h)):
        s += rect(axR.X(xv) - 22, axR.Y(m + pr["sigma"]), 44, axR.Y(m - pr["sigma"]) - axR.Y(m + pr["sigma"]),
                  fill=SOFT, op=0.10, stroke="none", sw=0)
    s += line(axR.X(0), axR.Y(-h), axR.X(1), axR.Y(h), stroke=ACCENT, sw=2.0)
    s += mono(axR.X(1) + 30, axR.Y(h) + 3, f"slope {hv(pr['b'], 2):.2f}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += note_lines(axR.x0 + 8, axR.y0 + 16, [(f"residual SD {hv(pr['sigma'], 2):.2f} on {pr['df']} df", INK),
                                             (f"SE {hv(pr['se'], 3):.3f}, t = {hv(pr['t'], 3):.3f}", INK),
                                             (f"p = {hv(pr['p'], 6):.6f}: the paired t-test", MUTED)])
    s += legend(vh - 24, vw, [("drug 1", "dot:" + INK + ":3.6"), ("drug 2", "dot:" + LINK + ":3.6"),
                              ("one patient's pair", "line:" + SOFT + ":0.8"), ("fitted difference", "line:" + ACCENT + ":2"),
                              ("group mean ± residual SD", "band:" + SOFT + ":0.18")])
    return emit("01", "two-regressions-one-coefficient", "Same coefficient, different standard error",
                "The sleep data as a regression on a drug dummy and with patient dummies added: the coefficient is the "
                "same, the residual spread is not.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 510
    up = SL["unpaired"]
    tss, ess, rss = up["tss"], up["ess"], up["rss"]
    assert abs(tss - ess - rss) < 1e-9 and (hv(tss, 2), hv(ess, 2), hv(rss, 2)) == (77.37, 12.48, 64.89)
    s = eyebrow(32, 40, "least squares as a projection, drawn for the sleep regression (n = 20, p = 2), centred at the mean")
    # the column space: a parallelogram in an oblique view
    P = [(150, 360), (560, 410), (760, 300), (350, 250)]
    s += area(P, LINK, 0.06, stroke=LINK, sw=1.0)
    s += mono(150, 440, "the column space of X: every vector Xb", size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(150, 454, "(spanned by the column of ones and the drug dummy: p = 2)", size=8, fill=SOFT, anchor="start")
    O = (330, 330)            # ȳ, the origin after centring
    F = (590, 318)            # ŷ − ȳ, inside the plane
    Y = (590, 108)            # y − ȳ, above the plane
    s += line(*O, *F, stroke=INK, sw=2.0, marker="arrow")
    s += line(*O, *Y, stroke=ACCENT, sw=2.0, marker="arrow-accent")
    s += line(*F, *Y, stroke=LINK, sw=2.0, dash="6,4")
    # right-angle mark at F
    s += polyline([(F[0], F[1] - 14), (F[0] - 14, F[1] - 14 + 1), (F[0] - 14, F[1] + 1)], MUTED, sw=1.0)
    s += dot(*O, 3.6, fill=INK) + mono(O[0] - 10, O[1] + 18, "ȳ", size=10, fill=INK, anchor="end", weight="600")
    s += plate(464, 206, f"y − ȳ: squared length {num(tss, 2)} = TSS", size=9, fill=ACCENT, anchor="end", weight="600")
    s += plate(420, 344, f"ŷ − ȳ: {num(ess, 2)} = ESS", size=9, fill=INK, anchor="start", weight="600")
    s += plate(604, 214, f"e = y − ŷ: {num(rss, 2)} = RSS", size=9, fill=LINK, anchor="start", weight="600")
    s += mono(604, 230, "perpendicular to every column: Xᵀe = 0", size=8, fill=SOFT, anchor="start")
    s += mono(604, 244, f"so e has n − p = {up['df']} free directions", size=8, fill=SOFT, anchor="start")
    s += note_lines(806, 330, [("Pythagoras:", INK), (f"{num(tss, 2)} = {num(ess, 2)} + {num(rss, 2)}", INK),
                               (f"R² = {num(ess, 2)} / {num(tss, 2)}", MUTED), (f"   = {hv(up['r2'], 4):.4f}", MUTED),
                               (f"s² = {num(rss, 2)} / {up['df']} = {hv(up['s2'], 4):.4f}", MUTED), ("s: the residual SD", SOFT)], gap=16)
    s += legend(vh - 24, vw, [("y − ȳ, the data", "line:" + ACCENT + ":2"), ("ŷ − ȳ, the fit", "line:" + INK + ":2"),
                              ("e, the residual", "dash:" + LINK + ":2"), ("column space of X", "band:" + LINK + ":0.15")])
    return emit("02", "least-squares-as-projection", "The fit is a shadow; the residual is perpendicular",
                "Least squares projects the centred data vector onto the space spanned by X's columns. The residual is "
                "perpendicular to that space, so the three squared lengths add up.", "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
SOLVER_ROWS = [("Householder QR", "Householder QR"), ("SciPy lstsq (gelsy)", "SciPy lstsq, gelsy"),
               ("SciPy lstsq (gelsd)", "SciPy lstsq, gelsd (default)"), ("NumPy lstsq, rcond=-1", "NumPy lstsq, rcond=−1"),
               ("NumPy lstsq, default rcond", "NumPy lstsq (default)"), ("statsmodels OLS().fit()", "statsmodels OLS().fit()"),
               ("R lm", "R lm (default tol)"), ("normal equations (LU)", "normal equations, LU"),
               ("normal equations (Cholesky)", "normal equations, Cholesky")]


def fig03():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "correct significant digits (lre) of every coefficient against nist's certified values, by solver")
    labx = 214
    panels = ((LO, "Longley: 7 coefficients", 236), (FI, "Filip: 11 coefficients", 636))
    top, rowh = 112, 38
    for d, head, x0 in panels:
        ax = Axes(x0, top, 340, rowh * len(SOLVER_ROWS), (0, 15), (0, len(SOLVER_ROWS)))
        s += title(x0, top - 30, head)
        s += mono(x0, top - 16, "each dot is one coefficient; the number is the fewest digits", size=8, fill=SOFT, anchor="start")
        for v in (0, 5, 10, 15):
            s += line(ax.X(v), top, ax.X(v), top + ax.h, stroke=RULE, sw=0.8)
            s += mono(ax.X(v), top + ax.h + 15, f"{v}", size=8, fill=SOFT)
        s += mono(ax.X(15), top + ax.h + 32, "correct digits", size=8.5, fill=SOFT, anchor="end")
        for i, (key, label) in enumerate(SOLVER_ROWS):
            yy = top + rowh * i + rowh / 2
            if x0 == panels[0][2]:
                s += mono(labx, yy + 3, label, size=8.5, fill=INK if "normal" not in key else LINK, anchor="end")
            s += line(ax.X(0), yy, ax.X(15), yy, stroke=RULE, sw=0.6)
            if key == "R lm":
                lres = d["r_lm"]["default"]["lre"]
            else:
                lres = d["solvers"][key]["lre"]
            vals = [v for v in lres if v == v]
            col = LINK if "normal" in key else INK
            if not vals:
                s += plate(ax.X(0) + 8, yy + 3, "refused: XᵀX not positive definite in floating point", size=8, fill=LINK)
                continue
            for v in vals:
                s += dot(ax.X(max(v, 0)), yy, 3.0, fill=col, op=0.75)
            lo = min(vals)
            lab = f"{max(lo, 0):.2f}"
            if key == "R lm" and len(vals) < len(lres):
                lab += f"  (x¹⁰ dropped: rank {d['r_lm']['default']['rank']:.0f} of 11)"
            if key == "statsmodels OLS().fit()" and d is FI:
                lab += "  (warns: rank-deficient)"
            xl = ax.X(max(lo, 0))
            if xl > ax.X(9.5):
                s += plate(ax.X(15) + 6, yy + 3, f"{max(lo, 0):.2f}", size=8, fill=col, weight="600")
            else:
                s += plate(max(xl, ax.X(max(vals))) + 10, yy + 3, lab, size=8, fill=col, weight="600")
    s += legend(vh - 24, vw, [("orthogonal (QR or SVD) solver", "dot:" + INK + ":3"), ("normal equations", "dot:" + LINK + ":3")])
    return emit("03", "digits-kept-by-each-solver", "What each solver keeps of fifteen certified digits",
                "Correct significant digits of every coefficient for Longley's and Filip's regressions, by solver, against "
                "NIST's values certified with 500-digit arithmetic.", "does the solver matter?", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 520
    rows = NIS["all"]
    s = eyebrow(32, 40, "nist's eleven linear datasets: fewest correct digits against the condition number of the column-scaled design")
    ax = Axes(96, 92, 640, 330, (0, 10.4), (0, 16))
    s += ax.clip("c4") + title(ax.x0, ax.y0 - 16, "a solver loses about log₁₀ κ digits (QR) or 2 log₁₀ κ (normal equations), κ of X with unit-length columns")
    s += ax.frame([0, 2, 4, 6, 8, 10], [0, 4, 8, 12, 16], xfmt=lambda v: f"10^{v}" if v else "1", yfmt=lambda v: f"{v}",
                  xlab="κ of the column-scaled design (log scale)", ylab="fewest correct digits over the coefficients")
    top = -math.log10(EPS)
    inner = line(ax.X(0), ax.Y(top), ax.X(10.4), ax.Y(top - 10.4), stroke=INK, sw=1.0, dash="5,3")
    inner += line(ax.X(0), ax.Y(top), ax.X(top / 2), ax.Y(0), stroke=LINK, sw=1.0, dash="5,3")
    s += f'<g clip-path="url(#c4)">{inner}</g>'
    s += plate(ax.X(6.9), ax.Y(top - 6.9) - 10, "15.65 − log₁₀ κ", size=8, fill=INK, anchor="start")
    s += plate(ax.X(3.9), ax.Y(1.9), "15.65 − 2 log₁₀ κ", size=8, fill=LINK, anchor="start")
    pos = {}
    for r in rows:
        lk = math.log10(r["kappa_scaled"])
        pos[r["name"]] = lk
        s += dot(ax.X(lk), ax.Y(max(r["qr_min"], 0)), 4.0, fill=INK)
        s += ring(ax.X(lk), ax.Y(max(r["ne_min"], 0)), 4.0, stroke=LINK)
    lab = {r["name"]: r for r in rows}
    s += plate(ax.X(0) + 12, ax.Y(15.0) + 4, "NoInt1, NoInt2: 14.7 and 15.0 by both", size=8, fill=MUTED)
    s += plate(ax.X(pos["Norris"]) + 10, ax.Y(lab["Norris"]["qr_min"]) + 18, "Norris", size=8, fill=MUTED)
    s += plate(ax.X(pos["Pontius"]) + 10, ax.Y(lab["Pontius"]["qr_min"]) - 6, "Pontius", size=8, fill=MUTED)
    s += plate(ax.X(pos["Longley"]) - 8, ax.Y(lab["Longley"]["qr_min"]) + 14, "Longley", size=8, fill=INK, anchor="end", weight="600")
    s += plate(ax.X(pos["Longley"]) + 10, ax.Y(lab["Longley"]["ne_min"]) + 3, f"normal {lab['Longley']['ne_min']:.2f}", size=8, fill=LINK, weight="600")
    s += plate(ax.X(pos["Filip"]) - 10, ax.Y(lab["Filip"]["qr_min"]) - 10, f"Filip: QR {lab['Filip']['qr_min']:.2f}", size=8, fill=INK, anchor="end", weight="600")
    s += plate(ax.X(pos["Filip"]) - 10, ax.Y(0.0) - 8, "normal equations: 0", size=8, fill=LINK, anchor="end", weight="600")
    wx = ax.X(pos["Wampler1"])
    w = [lab[f"Wampler{k}"] for k in range(1, 6)]
    s += mono(wx, ax.Y(w[4]["qr_min"]) + 22, "Wampler 1 to 5", size=8, fill=MUTED, anchor="middle")
    s += note_lines(760, 120, [("Wampler 1 to 5 share one X;", INK), ("only the noise in y differs.", INK),
                               ("QR keeps " + ", ".join(f"{v['qr_min']:.2f}" for v in w), MUTED),
                               ("digits; the normal equations", MUTED), (", ".join(f"{v['ne_min']:.2f}" for v in w) + ".", MUTED), ("", MUTED),
                               ("When the residual is large", INK), ("next to the fit (tan θ), QR", INK),
                               ("pays LAPACK's κ² tan θ term:", INK), (f"Wampler 5 (tan θ = {w[4]['tan_theta']:.1f}) keeps", MUTED),
                               (f"{w[4]['qr_min']:.2f} digits by QR, {w[4]['ne_min']:.2f} by", MUTED), ("the normal equations.", MUTED), ("", MUTED),
                               (f"Longley: QR {lab['Longley']['qr_min']:.2f}, normal", INK), (f"equations {lab['Longley']['ne_min']:.2f}.", INK)], gap=15)
    s += legend(vh - 24, vw, [("Householder QR", "dot:" + INK + ":4"), ("normal equations (LU)", "ring:" + LINK + ":4"),
                              ("rule of thumb, QR", "dash:" + INK + ":1"), ("rule of thumb, normal equations", "dash:" + LINK + ":1")])
    return emit("04", "digits-against-condition-number", "The condition number predicts the digits",
                "Fewest correct digits over the coefficients, for QR and for the normal equations, on NIST's eleven "
                "linear datasets, against the condition number of the column-scaled design.", "does the solver matter?", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 520
    rows = SUM["rows"]
    dg = SUM["diagnostics"]
    s = eyebrow(32, 40, "statsmodels 0.15.0's summary of longley's regression, each number traced to its formula")
    x0, y0, lh = 40, 78, 15.2
    w_txt = 560

    def pre(x, y, t, fill):
        """Monospace text that keeps its runs of spaces (SVG collapses them otherwise)."""
        t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return (f'<text x="{x}" y="{y:.1f}" fill="{fill}" font-size="10.2" font-family="\'Geist Mono\', ui-monospace, monospace" '
                f'text-anchor="start" xml:space="preserve" style="white-space:pre">{t}</text>')
    lines = []
    lines.append(("Dep. Variable:   Employed      R-squared:           " + f"{SUM['r2']:.3f}", "top"))
    lines.append(("No. Observations: 16           Adj. R-squared:      " + f"{SUM['adj_r2']:.3f}", "top"))
    lines.append(("Df Residuals:      9           F-statistic:         " + f"{SUM['F']:.1f}", "top"))
    lines.append(("Df Model:          6           Prob (F-statistic):  " + f"{SUM['F_p']:.2e}", "top"))
    lines.append(("Covariance Type:   nonrobust   Log-Likelihood:      " + f"{SUM['llf']:.2f}", "top"))
    lines.append(("                               AIC:                 " + f"{SUM['aic_statsmodels']:.1f}", "top"))
    lines.append(("                               BIC:                 " + f"{SUM['bic_statsmodels']:.1f}", "top"))
    lines.append(("", "gap"))
    lines.append(("             coef    std err        t    P>|t|   [0.025   0.975]", "head"))
    show = {"const": ("-3.482e+06", "8.9e+05", "-3.911", "0.004", "-5.5e+06", "-1.47e+06"),
            "Deflator": ("15.0619", "84.915", "0.177", "0.863", "-177.029", "207.153"),
            "GNP": ("-0.0358", "0.033", "-1.070", "0.313", "-0.112", "0.040"),
            "Unemployed": ("-2.0202", "0.488", "-4.136", "0.003", "-3.125", "-0.915"),
            "Armed": ("-1.0332", "0.214", "-4.822", "0.001", "-1.518", "-0.549"),
            "Population": ("-0.0511", "0.226", "-0.226", "0.826", "-0.563", "0.460"),
            "Year": ("1829.1515", "455.478", "4.016", "0.003", "798.788", "2859.515")}
    for r in rows:
        v = show[r["name"]]
        assert abs(float(v[0]) - r["b"]) <= abs(r["b"]) * 2e-3 and abs(float(v[2]) - r["t"]) < 1e-3, r["name"]
        lines.append((f"{r['name']:<11s}{v[0]:>11s}{v[1]:>10s}{v[2]:>9s}{v[3]:>8s}{v[4]:>10s}{v[5]:>10s}", "coef"))
    lines.append(("", "gap"))
    lines.append((f"Omnibus:        {dg['omnibus']:.3f}     Durbin-Watson:      {dg['durbin_watson']:.3f}", "diag"))
    lines.append((f"Prob(Omnibus):  {dg['omnibus_p']:.3f}     Jarque-Bera (JB):   {dg['jb']:.3f}", "diag"))
    lines.append((f"Skew:           {dg['skew']:.3f}     Prob(JB):           {dg['jb_p']:.3f}", "diag"))
    lines.append((f"Kurtosis:       {dg['kurtosis']:.3f}     Cond. No.           {dg['condition_number']:.2e}", "diag"))
    ys = {}
    s += rect(x0 - 10, y0 - 18, w_txt + 20, lh * len(lines) + 26, fill="#ffffff", stroke=RULE_SOLID, rx=6)
    for k, (t, kind) in enumerate(lines):
        yy = y0 + k * lh
        ys.setdefault(kind, []).append(yy)
        if t:
            s += pre(x0, yy, t.replace("-", "−") if kind != "head" else t, INK if kind != "head" else MUTED)
    cx = 628
    notes = [
        (ys["top"][0], f"R² = 1 − RSS/TSS = 1 − {float(SUM['rss_full']):,.0f} / {float(SUM['tss_full']):,.0f}", INK),
        (ys["top"][1], "adjusted: 1 − (1 − R²)(n − 1)/(n − p) = 1 − (1 − R²)·15/9", INK),
        (ys["top"][2], f"F = [(TSS − RSS)/6] / s², s² = RSS/9 = {num(SUM['sigma'] ** 2, 1)}", INK),
        (ys["top"][3], "P(F₆,₉ > 330.3)", MUTED),
        (ys["top"][4], "ℓ = −(n/2)[log(2π·RSS/n) + 1]: the Gaussian MLE", INK),
        (ys["top"][5], f"−2ℓ + 2·7 (R counts σ too: 2·8 → {SUM['aic_R']:.1f})", ACCENT),
        (ys["top"][6], "−2ℓ + 7·log 16 (R: 8·log 16)", ACCENT),
        (ys["coef"][0] - lh, "coef = R⁻¹Qᵀy from X = QR (never (XᵀX)⁻¹Xᵀy)", INK),
        (ys["coef"][1] - lh * 0.15, f"std err = s √[(XᵀX)⁻¹]ⱼⱼ, residual SD s = {SUM['sigma']:.3f}, 9 df", INK),
        (ys["coef"][2] + lh * 0.55, "t = coef / std err", INK),
        (ys["coef"][3] + lh * 0.9, "P>|t| = 2 P(T₉ > |t|)", INK),
        (ys["coef"][4] + lh * 1.25, f"[0.025, 0.975] = coef ± {SUM['t_quantile']:.3f} × std err", INK),
        (ys["diag"][0], "residual normality tests (Omnibus, JB, skew,", MUTED),
        (ys["diag"][1], "kurtosis): checked in a later part", MUTED),
        (ys["diag"][2], "Durbin–Watson: residual autocorrelation (time order)", MUTED),
        (ys["diag"][3], "σ_max / σ_min of X: numerical, not statistical", ACCENT),
    ]
    for yy, t, c in notes:
        s += line(x0 + w_txt + 12, yy - 3.5, cx - 8, yy - 3.5, stroke=RULE_SOLID, sw=0.8)
        s += mono(cx, yy, t, size=8.3, fill=c, anchor="start", weight="600" if c == ACCENT else "400")
    s += note_lines(40, y0 + lh * len(lines) + 30, [
        ("Every number above is recomputed in the lab from the design matrix; the 39 compared with statsmodels agree to 5.6e-12.", MUTED),
        ("Notes printed under the table: [1] standard errors assume the error covariance is correctly specified; [2] the condition number is large.", SOFT)],
        size=8.2, gap=14)
    s += legend(vh - 24, vw, [("a formula", "line:" + INK + ":1"), ("where statsmodels and R count differently", "line:" + ACCENT + ":1"),
                              ("read later or elsewhere", "line:" + MUTED + ":1")])
    return emit("06", "the-summary-table-annotated", "Every number in the summary, traced",
                "statsmodels' summary of Longley's employment regression, with each block mapped to the formula that "
                "produces it from the design matrix.", "every number in the summary", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 560
    el = SUM["ellipse"]
    bx, byr = el["center"]
    C = el["cov"]
    fq = el["f_quantile"]
    ovb = MEA["ovb"]
    short_gnp = ovb["short"][ovb["names"].index("GNP")]
    # the RSS contour through the Year-omitted estimate: same shape, r^2 = t_Year^2
    t_year = byr / math.sqrt(C[1][1])
    r2_95 = 2 * fq
    det = C[0][0] * C[1][1] - C[0][1] ** 2
    inv = [[C[1][1] / det, -C[0][1] / det], [-C[0][1] / det, C[0][0] / det]]
    d0 = (short_gnp - bx, 0 - byr)
    r2_short = d0[0] * (inv[0][0] * d0[0] + inv[0][1] * d0[1]) + d0[1] * (inv[1][0] * d0[0] + inv[1][1] * d0[1])
    assert abs(r2_short - t_year ** 2) < 1e-3 * t_year ** 2, (r2_short, t_year ** 2)
    k = math.sqrt(r2_short / r2_95)
    s = eyebrow(32, 40, "longley: the joint 95% confidence region for the gnp and year coefficients, and its two shadows")
    ax = Axes(110, 86, 560, 340, (-0.19, 0.17), (-1200, 4000))
    s += ax.clip("c7") + title(ax.x0, ax.y0 - 16, f"the estimates correlate {el['corr']:.2f}: the data fix a mix of the two better than either")
    s += ax.frame([-0.15, -0.10, -0.05, 0, 0.05, 0.10, 0.15], [-1000, 0, 1000, 2000, 3000, 4000],
                  xfmt=lambda v: f"{v:.2f}".replace("-", "−"), yfmt=lambda v: f"{v:,.0f}",
                  xlab="GNP coefficient", ylab="Year coefficient")
    pts = el["points"]
    inner = line(ax.X(0), ax.Y(-1200), ax.X(0), ax.Y(4000), stroke=SOFT, sw=0.8, dash="3,3")
    inner += line(ax.X(-0.19), ax.Y(0), ax.X(0.17), ax.Y(0), stroke=SOFT, sw=0.8, dash="3,3")
    big = [(bx + k * (p[0] - bx), byr + k * (p[1] - byr)) for p in pts]
    inner += polyline(curve(ax, [p[0] for p in big], [p[1] for p in big]), MUTED, sw=1.0, dash="5,3")
    inner += area(curve(ax, [p[0] for p in pts], [p[1] for p in pts]), ACCENT, 0.14, stroke=ACCENT, sw=1.6)
    s += f'<g clip-path="url(#c7)">{inner}</g>'
    # shadows: the individual 95% intervals on the axes
    g0, g1 = el["ci_gnp"]
    y0_, y1_ = el["ci_year"]
    s += line(ax.X(g0), ax.Y(-1200) - 10, ax.X(g1), ax.Y(-1200) - 10, stroke=INK, sw=3.0)
    s += plate(ax.X(g1) + 8, ax.Y(-1200) - 7, f"GNP alone: {g0:.3f} to {g1:.3f}".replace("-", "−"), size=8, fill=INK)
    s += line(ax.X(-0.19) + 10, ax.Y(y0_), ax.X(-0.19) + 10, ax.Y(y1_), stroke=INK, sw=3.0)
    s += plate(ax.X(-0.19) + 18, ax.Y(y0_) + 14, f"Year alone: {y0_:,.0f} to {y1_:,.0f}", size=8, fill=INK)
    s += dot(ax.X(bx), ax.Y(byr), 4.2, fill=INK)
    s += plate(ax.X(bx) + 10, ax.Y(byr) + 4, f"estimate ({bx:.4f}, {byr:,.0f})".replace("-", "−"), size=8, fill=INK, weight="600")
    s += ring(ax.X(short_gnp), ax.Y(0), 4.6, stroke=LINK, sw=1.8)
    s += plate(ax.X(short_gnp) + 8, ax.Y(0) + 20, f"Year left out: GNP {short_gnp:+.4f}", size=8, fill=LINK, anchor="start", weight="600")
    s += note_lines(700, 112, [("Shaded: the 95% joint region,", INK), (f"F(2, 9) quantile {fq:.3f}.", MUTED), ("", MUTED),
                               ("The bars are its shadows: each", INK), ("coefficient's own 95% interval.", INK), ("", MUTED),
                               ("Dashed: the residual-sum-of-", MUTED), ("squares contour that touches", MUTED),
                               ("Year = 0. Forcing Year to 0", MUTED), ("slides GNP along the tilt to", MUTED),
                               (f"{short_gnp:+.4f}: the omitted-", LINK), ("variable bias described below.", LINK), ("", MUTED),
                               (f"Joint test of both: F {SUM['joint']['GNP+Year']['F']:.2f}, p {SUM['joint']['GNP+Year']['p']:.4f}", INK)], gap=15)
    s += legend(vh - 24, vw, [("joint 95% region", "band:" + ACCENT + ":0.3"), ("individual 95% intervals", "line:" + INK + ":3"),
                              ("RSS contour through Year = 0", "dash:" + MUTED + ":1"), ("estimate with Year omitted", "ring:" + LINK + ":4")])
    return emit("07", "joint-region-gnp-year", "Two coefficients, one tilted region",
                "The joint 95% confidence region for Longley's GNP and Year coefficients, their individual intervals as its "
                "shadows, and where the estimate moves when Year is left out.", "every number in the summary", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 500
    P = MEA["fwl_points"]
    fw = MEA["fwl"]["GNP"]
    xr_, yr_ = P["x_raw"], P["y_raw"]
    xp, yp = P["x_partial"], P["y_partial"]
    s = eyebrow(32, 40, "longley: employment against gnp, as recorded and with the other five predictors partialled out")
    axL = Axes(96, 96, 360, 290, (220000, 570000), (59000, 72000))
    axR = Axes(588, 96, 360, 290, (-5600, 5600), (-700, 700))
    s += title(axL.x0, axL.y0 - 32, "as recorded") + mono(axL.x0, axL.y0 - 18, "GNP and employment rise together over 16 years", size=8, fill=SOFT, anchor="start")
    s += title(axR.x0, axR.y0 - 32, "partialled out") + mono(axR.x0, axR.y0 - 18, "residuals of each on the other five predictors and the constant", size=8, fill=SOFT, anchor="start")
    s += axL.frame([250000, 350000, 450000, 550000], [60000, 64000, 68000, 72000], xfmt=lambda v: f"{v / 1000:.0f}k",
                   yfmt=lambda v: f"{v / 1000:.0f}k", xlab="GNP (NIST's file)", ylab="employment (NIST's file)")
    s += axR.frame([-4000, -2000, 0, 2000, 4000], [-600, -300, 0, 300, 600], xfmt=lambda v: f"{v:,.0f}".replace("-", "−"),
                   yfmt=lambda v: f"{v:,.0f}".replace("-", "−"), xlab="GNP, partialled out", ylab="employment, partialled out")
    # raw simple-regression line
    n = len(xr_)
    mx, my = sum(xr_) / n, sum(yr_) / n
    bs = P["simple_slope"]
    assert abs(bs - sum((a - mx) * (b - my) for a, b in zip(xr_, yr_)) / sum((a - mx) ** 2 for a in xr_)) < 1e-6 * abs(bs)
    s += line(axL.X(225000), axL.Y(my + bs * (225000 - mx)), axL.X(565000), axL.Y(my + bs * (565000 - mx)), stroke=SOFT, sw=1.4)
    for a, b in zip(xr_, yr_):
        s += dot(axL.X(a), axL.Y(b), 3.6, fill=INK)
    s += plate(axL.X(230000), axL.Y(71000), f"slope alone {bs:.4f}", size=8.5, fill=MUTED, weight="600")
    slope = fw["slope"]
    s += line(axR.X(-5400), axR.Y(slope * -5400), axR.X(5400), axR.Y(slope * 5400), stroke=ACCENT, sw=2.0)
    for a, b in zip(xp, yp):
        s += dot(axR.X(a), axR.Y(b), 3.6, fill=INK)
    s += plate(axR.X(-5300), axR.Y(640), f"slope {slope:.4f} = GNP's coefficient".replace("-", "−"), size=8.5, fill=ACCENT, weight="600")
    s += note_lines(axR.x0 + 10, axR.y0 + axR.h - 44, [(f"spread of GNP here: SD {fw['sd_partial']:,.0f}", INK),
                                                       (f"as recorded: SD {fw['sd_raw']:,.0f}, {fw['sd_raw'] / fw['sd_partial']:.1f} times more", MUTED),
                                                       (f"= √VIF = √{fw['vif']:,.1f}", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("year (one point each)", "dot:" + INK + ":3.6"), ("simple regression on GNP alone", "line:" + SOFT + ":1.4"),
                              ("partial slope = multiple-regression coefficient", "line:" + ACCENT + ":2")])
    return emit("08", "holding-the-others-fixed", "What holding the others fixed leaves to compare",
                "Longley's employment against GNP: alone, the slope is positive; with the other predictors partialled out "
                "(Frisch-Waugh-Lovell), the slope is the multiple-regression coefficient and the remaining spread of GNP "
                "is a 42nd of the original.", "what a coefficient measures", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 460
    o = MEA["ovb"]
    names = o["names"][1:]
    long_, short_, bias, lse = o["long"][1:], o["short"][1:], o["bias"][1:], o["long_se"][1:]
    zs = [(l / se, sh / se, b / se) for l, sh, b, se in zip(long_, short_, bias, lse)]
    s = eyebrow(32, 40, "longley: each coefficient with year in the model and with year left out, in units of its full-model se")
    ax = Axes(200, 92, 560, 260, (-6, 4), (0, len(names)))
    s += ax.clip("c9") + title(ax.x0, ax.y0 - 16, "short = long + Year's coefficient (1,829.15) × the predictor's slope when Year is regressed on the rest")
    for v in (-6, -4, -2, 0, 2, 4):
        s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=RULE if v else RULE_SOLID, sw=0.8)
        s += mono(ax.X(v), ax.y0 + ax.h + 15, f"{v:+d}".replace("+0", "0").replace("-", "−"), size=8, fill=SOFT)
    s += mono(ax.X(4), ax.y0 + ax.h + 32, "coefficient ÷ its SE with Year in the model", size=8.5, fill=SOFT, anchor="end")
    for i, (nm, (zl, zsh, zb), l, sh, aux) in enumerate(zip(names, zs, long_, short_, o["aux"][1:])):
        yy = ax.y0 + (i + 0.5) * ax.h / len(names)
        s += mono(ax.x0 - 12, yy + 3, nm, size=9, fill=INK, anchor="end", weight="600")
        gap = 7 if ax.X(zsh) > ax.X(zl) else -7
        s += line(ax.X(zl), yy, ax.X(zsh) - gap, yy, stroke=LINK, sw=1.6, marker="arrow-link")
        s += dot(ax.X(zl), yy, 4.4, fill=INK)
        s += ring(ax.X(zsh), yy, 4.4, stroke=LINK, sw=1.8)
        lab = f"{l:#.4g} → {sh:#.4g}".replace("-", "−")
        s += mono(ax.X(4) + 12, yy - 2, lab, size=8, fill=INK, anchor="start")
        s += mono(ax.X(4) + 12, yy + 10, f"= {l:.4g} + 1,829.15 × {aux:.3g}".replace("-", "−"), size=7.6, fill=SOFT, anchor="start")
    s += note_lines(200, ax.y0 + ax.h + 54, [(f"The identity is exact in the sample (it holds to {o['identity_maxrel']:.0e} here); "
                                               f"R² falls only from {SUM['r2']:.4f} to {o['short_r2']:.4f}.", MUTED)], size=8.2)
    s += legend(vh - 24, vw, [("Year in the model", "dot:" + INK + ":4.4"), ("Year left out", "ring:" + LINK + ":4.4")])
    return emit("09", "omitted-variable-bias", "Leave Year out and every coefficient moves",
                "Each of Longley's coefficients with and without Year in the model, scaled by its standard error; the "
                "move equals Year's coefficient times the predictor's slope in the regression of Year on the others.",
                "what a coefficient measures", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 470
    names = ["Deflator", "GNP", "Unemployed", "Armed", "Population", "Year"]
    vifs = [MEA["fwl"][n]["vif"] for n in names]
    kp = MEA["kappa"]
    assert [round(v, 2) for v in vifs] == [135.53, 1788.51, 33.62, 3.59, 399.15, 758.98]
    s = eyebrow(32, 40, "longley: what collinearity costs (left) and what the condition number measures (right)")
    axL = Axes(190, 96, 330, 260, (0, 4), (0, 6))
    s += title(axL.x0 - 90, axL.y0 - 30, "variance inflation factor, VIF = 1 / (1 − R²ⱼ)")
    s += mono(axL.x0 - 90, axL.y0 - 16, "R²ⱼ: predictor j regressed on the other five; √VIF multiplies its SE", size=8, fill=SOFT, anchor="start")
    for v in range(0, 5):
        s += line(axL.X(v), axL.y0, axL.X(v), axL.y0 + axL.h, stroke=RULE, sw=0.8)
        s += mono(axL.X(v), axL.y0 + axL.h + 15, f"{10 ** v:,}", size=8, fill=SOFT)
    s += mono(axL.X(4), axL.y0 + axL.h + 32, "VIF (log scale)", size=8.5, fill=SOFT, anchor="end")
    for i, (n, v) in enumerate(zip(names, vifs)):
        yy = axL.y0 + (i + 0.5) * axL.h / 6
        s += mono(axL.x0 - 10, yy + 3, n, size=9, fill=INK, anchor="end", weight="600")
        s += rect(axL.X(0), yy - 9, axL.X(math.log10(v)) - axL.X(0), 18, fill=INK if v > 10 else SOFT, op=0.8, stroke="none", sw=0)
        s += plate(axL.X(math.log10(v)) + 8, yy + 3, f"{v:,.1f}  (SE × {math.sqrt(v):.1f})", size=8, fill=INK)
    axR = Axes(700, 96, 260, 260, (0, 4), (0, 10.5))
    s += title(axR.x0 - 30, axR.y0 - 30, "condition number of X, κ = σ_max / σ_min")
    s += mono(axR.x0 - 30, axR.y0 - 16, "the same six columns, re-expressed", size=8, fill=SOFT, anchor="start")
    for v in (0, 2, 4, 6, 8, 10):
        s += line(axR.x0, axR.Y(v), axR.x0 + axR.w, axR.Y(v), stroke=RULE, sw=0.8)
        s += mono(axR.x0 - 8, axR.Y(v) + 3, "1" if v == 0 else f"10^{v}", size=8, fill=SOFT, anchor="end")
    for j, (lab, v) in enumerate((("as recorded", kp["raw"]), ("centred", kp["centred"]), ("standardised", kp["standardised"]))):
        xx = axR.x0 + (j + 0.5) * axR.w / 3
        s += rect(xx - 22, axR.Y(math.log10(v)), 44, axR.Y(0) - axR.Y(math.log10(v)), fill=LINK, op=0.75, stroke="none", sw=0)
        s += plate(xx, axR.Y(math.log10(v)) - 8, f"{v:.4g}".replace("e+0", "e").replace("e+", "e"), size=8, fill=LINK, anchor="middle", weight="600")
        s += mono(xx, axR.y0 + axR.h + 15, lab, size=8, fill=INK)
    s += note_lines(axR.x0 - 30, axR.y0 + axR.h + 44, [("The VIFs are identical in all three", INK),
                                                       (f"(they move by {kp['vif_unchanged_maxrel']:.0e}): κ is numerical,", MUTED),
                                                       ("VIF is statistical.", MUTED)], gap=14)
    s += legend(vh - 24, vw, [("VIF above 10", "bar:" + INK + ":0.8"), ("VIF below 10", "bar:" + SOFT + ":0.8"),
                              ("condition number", "bar:" + LINK + ":0.75")])
    return emit("10", "vif-and-condition-number", "Collinearity costs precision; centring cannot buy it back",
                "Variance inflation factors of Longley's six predictors, and the condition number of the design matrix as "
                "recorded, centred and standardised.", "how much collinearity costs", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 520
    cells = INT["cells"]
    fits = INT["fits"]
    f1 = fits["1"]
    a, oj, sl, it = f1["b"]
    assert (hv(oj, 2), hv(it, 3), hv(fits["0.5"]["b"][1], 3), hv(fits["2"]["b"][1], 3)) == (3.70, -2.665, 6.365, 1.035)
    s = eyebrow(32, 40, "toothgrowth: odontoblast length by vitamin c dose and delivery, 10 guinea pigs per cell")
    ax = Axes(96, 96, 560, 320, (-1.25, 1.25), (0, 34))
    s += ax.clip("c11") + title(ax.x0, ax.y0 - 16, "length ~ OJ × doublings of dose: the OJ coefficient is the gap where 'doublings' is zero")
    s += ax.frame([-1, 0, 1], [0, 10, 20, 30], xfmt=lambda v: {-1: "0.5 mg", 0: "1 mg", 1: "2 mg"}[v], yfmt=lambda v: f"{v}",
                  xlab="dose per day (log scale)", ylab="odontoblast length (as recorded)")
    t9 = tq(9)
    inner = ""
    for supp, col, dx in (("OJ", INK, -0.035), ("VC", LINK, 0.035)):
        b0 = a + (oj if supp == "OJ" else 0)
        b1 = sl + (it if supp == "OJ" else 0)
        inner += line(ax.X(-1.2), ax.Y(b0 + b1 * -1.2), ax.X(1.2), ax.Y(b0 + b1 * 1.2), stroke=col, sw=1.6)
        for d, zz in (("0.5", -1), ("1", 0), ("2", 1)):
            c = cells[f"{supp}_{d}"]
            hw = t9 * c["sd"] / math.sqrt(c["n"])
            xx = ax.X(zz + dx)
            inner += line(xx, ax.Y(c["mean"] - hw), xx, ax.Y(c["mean"] + hw), stroke=col, sw=1.2)
            inner += dot(xx, ax.Y(c["mean"]), 4.2, fill=col) if supp == "OJ" else ring(xx, ax.Y(c["mean"]), 4.2, stroke=col)
    s += f'<g clip-path="url(#c11)">{inner}</g>'
    # brackets: the OJ - VC gap of the fitted lines at each origin, with only the number beside them
    spots = {"0.5": (26, 11.6, "start"), "1": (-26, 17.4, "end"), "2": (20, 24.6, "start")}
    for key, zz in (("0.5", -1), ("1", 0), ("2", 1)):
        f = fits[key]
        top_ = a + oj + (sl + it) * zz
        bot = a + sl * zz
        dx, ylab, anc = spots[key]
        xx = ax.X(zz) + dx
        s += line(xx, ax.Y(top_), xx, ax.Y(bot), stroke=ACCENT, sw=2.0)
        s += line(xx - 4, ax.Y(top_), xx + 4, ax.Y(top_), stroke=ACCENT, sw=2.0) + line(xx - 4, ax.Y(bot), xx + 4, ax.Y(bot), stroke=ACCENT, sw=2.0)
        s += plate(xx + (6 if anc == "start" else -6), ax.Y(ylab), f"{hv(f['b'][1], 2):.2f}", size=8.5, fill=ACCENT, anchor=anc, weight="600")
    s += note_lines(690, 112, [("The OJ coefficient, by origin:", INK)], gap=15)
    keep = lambda t: t.replace('text-anchor="start"', 'text-anchor="start" xml:space="preserve" style="white-space:pre"')
    s += keep(mono(690, 136, f"{'origin':<9s} {'OJ coef':>7s}  {'SE':>5s}  {'p':>6s}", size=8.5, fill=SOFT, anchor="start"))
    for k, key in enumerate(("0.5", "1", "2")):
        f = fits[key]
        pv = f["p"][1]
        ptxt = f"{hv(pv, 4):.4f}"
        s += keep(mono(690, 152 + 15 * k, f"{key + ' mg':<9s} {hv(f['b'][1], 2):>7.2f}  {hv(f['se'][1], 2):>5.2f}  {ptxt:>6s}", size=8.5,
                       fill=ACCENT if key == "1" else INK, anchor="start"))
    s += note_lines(690, 214, [("The interaction is the same in all", INK), (f"three: {it:.3f} (SE {f1['se'][3]:.3f}), the change", INK),
                               ("in the OJ gap per doubling of dose.", MUTED), ("Moving the origin changes only", MUTED),
                               ("which gap the OJ coefficient reports.", MUTED), ("", MUTED),
                               (f"Lines against the six cell means:", MUTED), (f"lack of fit F {INT['lack_of_fit']['F']:.2f}, p {INT['lack_of_fit']['p']:.2f}.", MUTED),
                               (f"Dose as a factor: interaction", MUTED), (f"F {INT['factor_interaction']['F']:.2f}, p {INT['factor_interaction']['p']:.3f}.", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("orange juice (OJ): mean ± 95% CI", "dot:" + INK + ":4.2"), ("ascorbic acid (VC)", "ring:" + LINK + ":4.2"),
                              ("fitted lines", "line:" + MUTED + ":1.6"), ("the OJ coefficient at each origin", "line:" + ACCENT + ":2")])
    return emit("11", "interaction-and-centring", "Where the predictor is zero decides what the coefficient means",
                "ToothGrowth's cell means with the fitted interaction model; the supplement coefficient is the gap between "
                "the lines at the dose chosen as the origin.", "interactions and centring", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 500
    g, m, ch, ph = ITV["grid"], ITV["band_mean"], ITV["ci_half"], ITV["pi_half"]
    z, yv = ITV["z"], ITV["y"]
    s = eyebrow(32, 40, "the ascorbic-acid (vc) arm: a band for the mean length and a band for one new guinea pig")
    ax = Axes(96, 96, 470, 300, (-1.2, 1.2), (0, 36))
    s += ax.clip("c12") + title(ax.x0, ax.y0 - 16, "95% intervals from one fit: half-widths t·s·√h for the mean, t·s·√(1 + h) for one animal")
    s += ax.frame([-1, 0, 1], [0, 10, 20, 30], xfmt=lambda v: {-1: "0.5 mg", 0: "1 mg", 1: "2 mg"}[v], yfmt=lambda v: f"{v}",
                  xlab="dose per day (log scale)", ylab="odontoblast length")
    inner = area(curve(ax, g, [a + b for a, b in zip(m, ph)]) + curve(ax, g[::-1], [a - b for a, b in zip(m[::-1], ph[::-1])]), LINK, 0.12)
    inner += area(curve(ax, g, [a + b for a, b in zip(m, ch)]) + curve(ax, g[::-1], [a - b for a, b in zip(m[::-1], ch[::-1])]), LINK, 0.38)
    inner += polyline(curve(ax, g, m), INK, sw=1.6)
    jit = {}
    for zz, yy in zip(z, yv):
        k = jit.get(zz, 0)
        jit[zz] = k + 1
        inner += dot(ax.X(zz + (k % 5 - 2) * 0.018), ax.Y(yy), 2.6, fill=INK, op=0.55)
    s += f'<g clip-path="url(#c12)">{inner}</g>'
    z0 = math.log2(ITV["x0_dose"])
    ci, pi = ITV["ci"], ITV["pi"]
    xx = ax.X(z0)
    s += line(xx + 10, ax.Y(pi[0]), xx + 10, ax.Y(pi[1]), stroke=LINK, sw=1.6) + line(xx + 4, ax.Y(ci[0]), xx + 4, ax.Y(ci[1]), stroke=INK, sw=3.0)
    s += note_lines(ax.x0 + 10, ax.y0 + 18, [(f"at 1.5 mg (bars): mean {ITV['mean0']:.2f}", INK),
                                             (f"for the mean: {ci[0]:.2f} to {ci[1]:.2f}", INK),
                                             (f"for one new animal: {pi[0]:.2f} to {pi[1]:.2f}", LINK),
                                             (f"s = {ITV['sigma']:.3f} on {ITV['df']} df; h = {ITV['leverage0']:.4f}", MUTED)], gap=15)
    rows = ITV["coverage"]["rows"]
    axR = Axes(640, 96, 320, 300, (5, 700), (0, 1.0), xmap=math.log10)
    s += title(axR.x0, axR.y0 - 16, "how often each covers, 20,000 simulated studies per n")
    s += axR.frame([6, 15, 30, 60, 150, 600], [0, 0.25, 0.5, 0.75, 0.95, 1.0], xfmt=lambda v: f"{v}", yfmt=lambda v: f"{100 * v:.0f}%",
                   xlab="animals in the arm (log scale)", ylab="coverage")
    s += line(axR.X(5), axR.Y(0.95), axR.X(700), axR.Y(0.95), stroke=ACCENT, sw=1.0, dash="5,3")
    for key, col, lab in (("pi_covers_new", LINK, "PI covers a new animal"), ("ci_covers_mean", INK, "CI covers the mean"),
                          ("ci_covers_new", SOFT, "CI used as a PI")):
        pts = [(r["n"], r[key]) for r in rows]
        s += polyline(curve(axR, [p[0] for p in pts], [p[1] for p in pts]), col, sw=1.6)
        for a, b in pts:
            s += dot(axR.X(a), axR.Y(b), 3.2, fill=col)
    last = rows[-1]
    s += mono(axR.X(600) - 4, axR.Y(last["ci_covers_new"]) + 18, f"{hp(last['ci_covers_new']):.1f}% at 600", size=8, fill=MUTED, anchor="end", weight="600")
    s += mono(axR.X(6) + 10, axR.Y(rows[0]["ci_covers_new"]) - 10, f"{hp(rows[0]['ci_covers_new']):.1f}% at 6", size=8, fill=MUTED, anchor="start", weight="600")
    lo95 = min(min(r["pi_covers_new"], r["ci_covers_mean"]) for r in rows)
    hi95 = max(max(r["pi_covers_new"], r["ci_covers_mean"]) for r in rows)
    s += mono(axR.X(6) + 4, axR.Y(0.95) + 18, f"the other two: {hp(lo95):.1f}% to {hp(hi95):.1f}%", size=8, fill=INK, anchor="start", weight="600")
    s += legend(vh - 24, vw, [("CI for the mean", "band:" + LINK + ":0.45"), ("prediction interval", "band:" + LINK + ":0.15"),
                              ("PI, new animal", "line:" + LINK + ":1.6"), ("CI, the mean", "line:" + INK + ":1.6"),
                              ("CI as a PI", "line:" + SOFT + ":1.6")], x=96)
    return emit("12", "confidence-vs-prediction", "An interval for the mean is not an interval for the next animal",
                "The VC arm's fitted line with its 95% confidence band for the mean and its 95% prediction band, and how "
                "often each covers a new animal as the arm grows.", "confidence or prediction interval", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
COND = [("normal", INK, "normal"), ("skewed predictor", LIGHT, "skewed x"),
        ("skewed errors", ACCENT, "skewed errors and x"), ("heavy-tailed errors", MUTED, "t errors, 3 df"),
        ("non-constant variance", LINK, "SD rising with x"), ("dependent errors", SOFT, "AR(1) errors")]


def fig13():
    vw, vh = 1016, 520
    sl = CON["slope"]
    reps = CON["reps"]
    sizes = CON["sizes"]
    s = eyebrow(32, 40, f"coverage of the slope's 95% t-interval, y = 1 + 2x + error, {reps:,} simulated datasets per point")
    axL = Axes(96, 96, 400, 300, (4, 1300), (0.92, 0.97), xmap=math.log10)
    axR = Axes(588, 96, 380, 300, (4, 1300), (0.5, 1.0), xmap=math.log10)
    s += title(axL.x0, axL.y0 - 16, "conditions on the distributions (zoomed)")
    s += title(axR.x0, axR.y0 - 16, "conditions on variance and independence")
    s += axL.frame(sizes, [0.92, 0.93, 0.94, 0.95, 0.96, 0.97], xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{100 * v:.0f}%",
                   xlab="n (log scale)", ylab="coverage")
    s += axR.frame(sizes, [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 1.0], xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{100 * v:.0f}%",
                   xlab="n (log scale)", ylab="coverage")
    for ax in (axL, axR):
        s += line(ax.X(4), ax.Y(0.95), ax.X(1300), ax.Y(0.95), stroke=ACCENT, sw=0.8, dash="5,3")
    for key, col, lab in COND:
        ax = axR if key in ("non-constant variance", "dependent errors") else axL
        pts = [(r["n"], r["cover"], r["mcse"]) for r in sl[key]]
        s += polyline(curve(ax, [p[0] for p in pts], [p[1] for p in pts]), col, sw=1.6, dash="5,3" if key == "heavy-tailed errors" else None)
        for a, b, e in pts:
            s += line(ax.X(a), ax.Y(b - 1.96 * e), ax.X(a), ax.Y(b + 1.96 * e), stroke=col, sw=1.0)
            s += dot(ax.X(a), ax.Y(b), 3.0, fill=col)
    nc, de = sl["non-constant variance"], sl["dependent errors"]
    s += mono(axR.X(1000) - 6, axR.Y(nc[-1]["cover"]) + 16, f"{hp(nc[-1]['cover']):.1f}% at n = 1,000", size=8, fill=LINK, anchor="end", weight="600")
    s += mono(axR.X(1000) - 6, axR.Y(de[-1]["cover"]) - 9, f"{hp(de[-1]['cover']):.1f}% at n = 1,000", size=8, fill=MUTED, anchor="end", weight="600")
    sk = sl["skewed errors"]
    s += mono(axL.X(5) + 8, axL.Y(sk[0]["cover"]) + 18, f"{hp(sk[0]['cover']):.1f}% at n = 5", size=8, fill=ACCENT, anchor="start", weight="600")
    s += legend(vh - 24, vw, [(lab, ("dash:" if k == "heavy-tailed errors" else "line:") + col + ":1.6") for k, col, lab in COND], x=96)
    return emit("13", "which-conditions-matter", "Normality barely matters; variance and independence do",
                "Measured coverage of the slope's nominal 95% interval as n grows, under four distributional conditions "
                "and two conditions on the errors' variance and independence.", "which conditions carry the weight", vw, vh, s)


# ------------------------------------------------------------------ FIG 14
def fig14():
    vw, vh = 1016, 460
    pi = CON["pi"]
    reps = pi["reps"]
    s = eyebrow(32, 40, f"a 95% prediction interval's misses below and above, {reps:,} simulated datasets per n")
    lim = pi["exact_exponential_upper"]
    panels = (("normal", "normal errors", 96), ("skewed", "skewed errors: exponential, centred", 560))
    for key, head, x0 in panels:
        ax = Axes(x0, 96, 380, 260, (0, 4), (0, 0.07))
        s += title(ax.x0, ax.y0 - 16, head)
        s += ax.frame([], [0, 0.01, 0.025, 0.05, 0.07], yfmt=lambda v: f"{100 * v:g}%", ylab="share of new observations missed")
        s += line(ax.x0, ax.Y(0.025), ax.x0 + ax.w, ax.Y(0.025), stroke=ACCENT, sw=0.8, dash="5,3")
        if key == "skewed":
            s += line(ax.x0, ax.Y(lim), ax.x0 + ax.w, ax.Y(lim), stroke=LINK, sw=0.8, dash="5,3")
        for i, r in enumerate(pi[key]):
            cx = ax.X(i + 0.5)
            for j, (v, col) in enumerate(((r["below"], MUTED), (r["above"], LINK))):
                xx = cx - 16 + 18 * j
                s += rect(xx, ax.Y(v), 14, ax.Y(0) - ax.Y(v), fill=col, op=0.75, stroke="none", sw=0)
                ly = ax.Y(v) - 4
                for ref in ([0.025, lim] if key == "skewed" else [0.025]):
                    if abs(ax.Y(v) - ax.Y(ref)) < 12:
                        ly = min(ly, ax.Y(ref) - 7)
                s += mono(xx + 7, ly, f"{hp(v, 1):.1f}", size=7.5, fill=col)
            s += mono(cx, ax.y0 + ax.h + 15, f"n = {r['n']:,}", size=8, fill=SOFT)
    s += legend(vh - 24, vw, [("missed below", "bar:" + MUTED + ":0.75"), ("missed above", "bar:" + LINK + ":0.75"),
                              ("2.5%: what each tail should miss", "dash:" + ACCENT + ":0.8"),
                              (f"large-n limit above, {hp(lim, 2):.2f}%", "dash:" + LINK + ":0.8")])
    return emit("14", "prediction-interval-tails", "A prediction interval needs the error's shape at any n",
                "Share of new observations falling below and above a 95% prediction interval, for normal and for skewed "
                "errors, as the sample grows.", "which conditions carry the weight", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "06": fig06, "07": fig07, "08": fig08, "09": fig09,
        "10": fig10, "11": fig11, "12": fig12, "13": fig13, "14": fig14}

if __name__ == "__main__":
    for k in (sys.argv[1:] or sorted(FIGS)):
        FIGS[k]()
