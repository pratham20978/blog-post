#!/usr/bin/env python3
"""Figures 01-10 for permutation-and-rank-tests (Statistics for Data Scientists, part 10).

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/permutation.py, or from a closed
form evaluated here (normal and exponential densities, the t density) and checked against the capture. The asserts
below pin each number the article quotes, so a figure cannot drift from the text. Run:  python3 _figs.py [01 05 ...]
"""
import json
import math
import pathlib
import sys
from decimal import ROUND_HALF_UP, Decimal

from _build import ACCENT, INK, LINK, MUTED, PAPER, RULE, RULE_SOLID, SOFT, emit, eyebrow, mono

HERE = pathlib.Path(__file__).resolve().parent
LAB = HERE.parent / "lab"
CAP = json.loads((LAB / "captures.json").read_text(encoding="utf-8"))
EX, TS, MW, EF, CO = (CAP[k] for k in ("example", "twosample", "mannwhitney", "efficiency", "correlation"))
XC = CAP["author_crosscheck"]

# One style per test, the same in every figure: (colour, stroke width, dash). The test read as answering a question
# it does not answer is tangerine; the test that answers it is blue; the parametric reference is grey or thin.
STYLE = {"perm_diff": (ACCENT, 1.9, None), "perm_stud": (LINK, 1.9, None),
         "student": (ACCENT, 1.2, "5,3"), "welch": (LINK, 1.2, "5,3"),
         "mw": (ACCENT, 1.9, None), "bm": (LINK, 1.9, None), "welch_t": (MUTED, 1.5, "2,2.5"),
         "naive": (ACCENT, 1.9, None), "naive10k": (ACCENT, 1.4, "5,3"),
         "plus1": (LINK, 1.9, None), "plus1_10k": (LINK, 1.4, "5,3")}


def hp(share, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return float((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def hv(x, nd=4):
    """A number rounded half up from its stored decimal."""
    return float(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


# ------------------------------------------------------------------ the numbers the article prints, held to the capture
D8 = EX["d8"]
assert D8 == [49, -67, 8, 16, 6, 23, 28, 41, 14, 29, 56, 24, 75, 60, -48] and EX["sum8"] == 314
assert sum(1 for v in D8 if v > 0) == 13 and sum(abs(v) for v in D8) == 544
assert (hv(EX["t"], 3), hv(EX["p_t"], 4), hv(EX["mean"], 3), hv(EX["sd"], 3), hv(EX["se"], 3)) == (2.148, 0.0497, 2.617, 4.718, 1.218)
assert [hv(v, 3) for v in EX["ci_t"]] == [0.004, 5.229] and hv(EX["crit"], 3) == 2.145
PERM = EX["perm"]
assert (PERM["gt"], PERM["eq"], PERM["ge"], PERM["n_assign"]) == (835, 28, 863, 32768) and hv(PERM["p"], 4) == 0.0527
assert hp(PERM["one_sided"], 3) == 2.634 and hp(EX["one_sided_t"], 3) == 2.485
assert [r for r in EX["table4"] if r[0] == 4] == [[4, 302, 11, 1052, 1365]]
SR = EX["signed_rank"]
assert (SR["v"], SR["v_minus"], SR["ge"], hv(SR["p"], 4)) == (96, 24, 676, 0.0413)
assert hv(EX["sign"]["p"], 4) == 0.0074 and EX["sign"]["k"] == 13
assert hv(EX["galton"]["t"], 2) == 5.17 and hv(EX["galton"]["mean"], 3) == 2.617
HL = EX["hodges_lehmann"]
assert (HL["estimate"], HL["lower"], HL["upper"], HL["qu"], HL["n_walsh"]) == (3.125, 0.5, 5.1875, 26, 120)
assert hp(HL["confidence"], 1) == 95.2
assert (XC["darwin_pseudomedian"], XC["darwin_hl_ci"]) == (3.125, [0.5, 5.1875]) and XC["darwin_signed_rank_V"] == 96
MC = EX["monte_carlo"]
assert hp(MC["p_below"], 1) == 19.4 and (hv(MC["q_lo"], 4), hv(MC["q_hi"], 4)) == (0.0466, 0.0592)
assert (hp(MC["runs_share"], 1), hp(MC["runs_mcse"], 1), MC["runs"]) == (21.3, 1.3, 1000)
FW = EX["fwer"]
_k = FW["999"]["tests"].index(1000)
assert (hp(FW["999"]["naive"][_k], 1), hp(FW["999"]["plus_one"][_k], 1)) == (63.2, 0.0)
D40, D25 = TS["designs"]["10,40"], TS["designs"]["25,25"]
assert [hp(D40[k]["perm_diff"], 2) for k in ("0.25", "2", "4")] == [0.06, 18.31, 29.10]
assert [hp(D40[k]["perm_studentised"], 2) for k in ("0.25", "2", "4")] == [3.87, 5.73, 5.81]
assert [hp(D40[k]["student"], 2) for k in ("2", "4")] == [18.34, 29.20] and hp(D40["2"]["welch"], 2) == 5.02
assert all(v["perm_diff"] == v["perm_studentised"] for v in D25.values())
assert (min(hp(v["perm_diff"], 2) for v in D25.values()), max(hp(v["perm_diff"], 2) for v in D25.values())) == (5.06, 5.57)
assert TS["engine_check"]["max_abs_diff"] < 1e-12 and D40["2"]["R"] == 50000
assert hv(MW["theta1"], 4) == 0.4431 and hv(MW["c2"], 4) == 0.8758 and hv(MW["hl_target1"], 4) == -0.1827
assert hv(MW["mean_y1"], 3) == 0.307 and hv(MW["median_y2"], 3) == -0.183
S1, S2, S3 = MW["S1"], MW["S2"], MW["S3"]
assert [hp(S1[k]["mw"], 1) for k in ("10", "50", "200", "400")] == [6.1, 16.7, 50.2, 79.7]
assert (min(hp(v["mw"], 1) for v in S2.values()), max(hp(v["mw"], 1) for v in S2.values())) == (4.7, 5.7)
assert [hp(S3[k]["mw"], 2) for k in ("0.25", "2", "4")] == [0.71, 9.93, 14.81]
assert (min(hp(v["bm"], 2) for v in S3.values()), max(hp(v["bm"], 2) for v in S3.values())) == (4.94, 5.67)
assert hv(MW["hl_sim"]["mean"], 3) == -0.186
SH = EF["shapes"]
assert hv(EF["delta"], 2) == 0.91
assert [hv(SH[k]["are"], 3) for k in ("parabolic", "normal", "uniform", "Laplace", "t, 3 df")] == [0.864, 0.955, 1.0, 1.5, 1.9]
assert [(hp(SH[k]["welch"], 1), hp(SH[k]["mw"], 1)) for k in ("normal", "uniform", "t, 3 df")] == [(79.7, 77.6), (79.8, 73.5), (84.0, 95.0)]
assert (hv(CO["r"], 3), hv(CO["rho"], 3), hv(CO["tau"], 3), CO["concordant"], CO["discordant"]) == (0.776, 0.796, 0.638, 86, 19)
assert (hv(CO["spearman_exact"]["p"], 5), hv(CO["library"]["spearmanr_p"], 5), hv(XC["law_spearman_p_as89"], 5)) == (0.00064, 0.00038, 0.00061)
assert hv(CO["library"]["kendalltau_p"], 5) == 0.00053 and hv(CO["library"]["pearsonr_p"], 5) == 0.00067
assert [hv(CO["perm_p"][k], 5) for k in ("pearson", "spearman", "kendall")] == [0.00134, 0.00078, 0.00067]


# ------------------------------------------------------------------ drawing helpers (Part 8's set)
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


def log2(v):
    return math.log(v, 2)


def log10(v):
    return math.log10(v)


RATIO_TICKS = [0.25, 0.5, 1, 2, 4]


def ratio_fmt(v):
    return {0.25: "1/4", 0.5: "1/2", 1: "1", 2: "2", 4: "4"}[v]


def frac8(v):
    """Eighths of an inch as Darwin wrote them: 49 -> '6 1/8', -67 -> '−8 3/8'."""
    sign = "−" if v < 0 else ""
    whole, rest = divmod(abs(int(v)), 8)
    return f"{sign}{whole}" + (f" {rest}/8" if rest else "")


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 510
    c8, s8, pots = EX["crossed8"], EX["self8"], EX["pot"]
    s = eyebrow(32, 40, "the worked example: Darwin's 15 pairs of Zea mays (1876), measured in eighths of an inch")
    ax = Axes(96, 96, 470, 340, (0.4, 15.6), (11, 24.5))
    s += title(ax.x0, ax.y0 - 16, "height of each plant, inches, pair by pair")
    s += ax.frame([], [12, 14, 16, 18, 20, 22, 24], yfmt=lambda v: f"{v:.0f}")
    bounds = [i for i in range(1, 15) if pots[i] != pots[i - 1]]
    for b in bounds:
        xb = ax.X(b + 0.5)
        s += line(xb, ax.y0, xb, ax.y0 + ax.h, stroke=RULE_SOLID, sw=0.8, dash="2,3")
    starts = [0] + bounds + [15]
    for k in range(4):
        mid = (starts[k] + starts[k + 1] - 1) / 2 + 1
        s += mono(ax.X(mid), ax.y0 + ax.h + 16, f"pot {['I', 'II', 'III', 'IV'][k]}", size=8.4, fill=SOFT)
    for i, (c, sf) in enumerate(zip(c8, s8)):
        x = ax.X(i + 1)
        col = ACCENT if c < sf else MUTED
        s += line(x, ax.Y(c / 8), x, ax.Y(sf / 8), stroke=col, sw=1.6 if c < sf else 1.1)
        s += dot(x, ax.Y(c / 8), 4.0, fill=INK) + dot(x, ax.Y(sf / 8), 4.0, fill=PAPER, stroke=INK, sw=1.4)
    s += mono(ax.X(2), ax.Y(96 / 8) + 16, "pair 2", size=8, fill=ACCENT, weight="600")
    s += mono(ax.X(15) - 4, ax.Y(96 / 8) + 16, "pair 15", size=8, fill=ACCENT, anchor="end", weight="600")
    # panel B: the 15 differences on one line, in eighths
    bx = Axes(640, 150, 330, 60, (-80, 80), (0, 1))
    s += title(bx.x0, ax.y0 - 16, "crossed minus self-fertilised, eighths of an inch")
    s += line(bx.x0, bx.y0 + bx.h, bx.x0 + bx.w, bx.y0 + bx.h, stroke=RULE_SOLID)
    for v in (-80, -40, 0, 40, 80):
        s += mono(bx.X(v), bx.y0 + bx.h + 15, num(v, 0), size=8, fill=SOFT)
    s += line(bx.X(0), bx.y0 - 6, bx.X(0), bx.y0 + bx.h, stroke=SOFT, sw=0.9, dash="3,3")
    srt = sorted(D8)
    for k, v in enumerate(srt):
        lift = 12 + 12 * (k % 3)
        s += line(bx.X(v), bx.y0 + bx.h, bx.X(v), bx.y0 + bx.h - lift, stroke=ACCENT if v < 0 else MUTED, sw=1.0)
        s += dot(bx.X(v), bx.y0 + bx.h - lift, 3.6, fill=ACCENT if v < 0 else INK)
    s += note_lines(640, 268, [
        (f"13 of 15 positive; sum {EX['sum8']} eighths", INK),
        (f"mean {EX['mean']:.3f} in, SD {EX['sd']:.3f} in", MUTED),
        ("", INK),
        ("the two negatives are large:", ACCENT),
        (f"pair 2: {frac8(-67)} in (−67 eighths)", ACCENT),
        (f"pair 15: {frac8(-48)} in (−48 eighths)", ACCENT),
        ("", INK),
        ("each pair germinated together and", MUTED),
        ("grew on opposite sides of one pot", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("crossed", "dot:" + INK + ":4.0"), ("self-fertilised", "ring:" + INK + ":4.0"),
                              ("self-fertilised taller", "line:" + ACCENT + ":1.6")])
    return emit("01", "darwins-pairs", "Thirteen of 15 crossed plants are taller; the two exceptions are large",
                "Darwin's 15 pairs of cross- and self-fertilised maize seedlings, grown in four pots, and the 15 differences "
                "Fisher analysed in 1935.", "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 480
    vals, counts = PERM["null_values"], PERM["null_counts"]
    assert sum(counts) == 32768 and sum(c for v, c in zip(vals, counts) if v >= 314) == 863
    assert sum(c for v, c in zip(vals, counts) if v <= -314) == 863
    s = eyebrow(32, 40, "all 2^15 = 32,768 ways to give the 15 differences a sign, each equally likely if crossing does nothing")
    ax = Axes(96, 96, 820, 300, (-560, 560), (0, max(counts) * 1.34))
    s += title(ax.x0, ax.y0 - 16, "number of sign assignments with each total (eighths of an inch)")
    yt = [0, 50, 100, 150]
    s += ax.frame([-544, -314, 0, 314, 544], [v for v in yt if v <= ax.yr[1]], xfmt=lambda v: num(v, 0),
                  xlab="total of the 15 signed differences, eighths of an inch")
    for v, c in zip(vals, counts):
        tail = abs(v) >= 314
        s += line(ax.X(v), ax.Y(0), ax.X(v), ax.Y(c), stroke=ACCENT if tail else MUTED, sw=1.0 if tail else 0.9,
                  op=None if tail else 0.75)
    s += line(ax.X(314), ax.y0 + 8, ax.X(314), ax.Y(0), stroke=INK, sw=1.2, dash="4,3")
    s += line(ax.X(-314), ax.y0 + 8, ax.X(-314), ax.Y(0), stroke=INK, sw=1.0, dash="4,3")
    s += mono(ax.X(314) + 8, ax.y0 + 20, f"observed 314: {PERM['ge']} of 32,768 at or above", size=8.6, fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.X(314) + 8, ax.y0 + 36, f"({PERM['gt']} above, {PERM['eq']} equal)", size=8.4, fill=ACCENT, anchor="start")
    s += mono(ax.X(-314) - 8, ax.y0 + 20, f"its mirror: {PERM['ge']} at or below −314", size=8.6, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(0), ax.y0 + 20, f"two-sided p = 1,726/32,768 = {PERM['p']:.4f}", size=9.2, fill=INK, weight="600")
    s += mono(ax.X(0), ax.y0 + 36, f"(t-test: {EX['p_t']:.4f})", size=8.4, fill=MUTED)
    s += mono(ax.X(-544), ax.Y(0) - 10, "all 15 negative", size=7.8, fill=SOFT, anchor="start")
    s += mono(ax.X(544), ax.Y(0) - 10, "all 15 positive", size=7.8, fill=SOFT, anchor="end")
    s += legend(vh - 24, vw, [("totals at least as far from 0 as Darwin's", "line:" + ACCENT + ":1.4"),
                              ("the other totals", "line:" + MUTED + ":1.4")])
    return emit("02", "every-sign-assignment", "Fisher's randomisation test, enumerated",
                "If crossing makes no difference and the coin decided which plant of a pair got which site, every one of the "
                "32,768 sign patterns was equally likely; the p-value is the share of totals at least as extreme as 314.",
                "the worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 540
    ranks = SR["ranks"]
    s = eyebrow(32, 40, "one data set, three views of it, four tests: what each test keeps of the 15 differences")
    rows = [("values", "t-test and randomisation test", 120), ("signed ranks", "Wilcoxon signed-rank test", 236),
            ("signs", "sign test", 352)]
    x0, x1 = 210, 640
    for lab, sub, y in rows:
        s += mono(x0 - 24, y - 2, lab, size=9.2, fill=INK, anchor="end", weight="600")
        s += mono(x0 - 24, y + 13, sub, size=8, fill=SOFT, anchor="end")
        s += line(x0, y + 28, x1, y + 28, stroke=RULE, sw=0.8)
    # row 1: values on a number line, eighths
    vx = lambda v: x0 + (v + 80) / 160 * (x1 - x0)
    y = rows[0][2]
    s += line(vx(0), y - 22, vx(0), y + 24, stroke=SOFT, sw=0.8, dash="3,3")
    for k, v in enumerate(sorted(D8)):
        s += dot(vx(v), y + 4 - 9 * (k % 2), 4.0, fill=ACCENT if v < 0 else INK)
    for v in (-80, 0, 80):
        s += mono(vx(v), y + 42, num(v, 0), size=7.8, fill=SOFT)
    # row 2: ranks 1..15 with signs
    order = sorted(range(15), key=lambda i: ranks[i])
    y = rows[1][2]
    w = (x1 - x0) / 15
    for j, i in enumerate(order):
        neg = D8[i] < 0
        s += rect(x0 + j * w + 2, y - 14, w - 4, 26, fill=PAPER if not neg else "rgba(235,108,54,0.10)",
                  stroke=ACCENT if neg else "rgba(45,49,66,0.35)", sw=1.0)
        s += mono(x0 + j * w + w / 2, y + 4, f"{'−' if neg else '+'}{int(ranks[i])}", size=8.6,
                  fill=ACCENT if neg else INK, weight="600")
    s += mono(x0, y + 44, f"V+ = sum of positive ranks = {int(SR['v'])} of 120", size=8.2, fill=MUTED, anchor="start")
    # row 3: signs only
    y = rows[2][2]
    for j, i in enumerate(order):
        neg = D8[i] < 0
        s += mono(x0 + j * w + w / 2, y + 6, "−" if neg else "+", size=14, fill=ACCENT if neg else INK, weight="600")
    s += mono(x0, y + 44, "13 plus, 2 minus", size=8.2, fill=MUTED, anchor="start")
    # the p-values, on one axis
    px = Axes(720, 96, 240, 290, (0, 0.06), (0, 1))
    s += title(px.x0, 80, "two-sided p-value")
    s += line(px.x0, px.y0 + px.h, px.x0 + px.w, px.y0 + px.h, stroke=RULE_SOLID)
    for v in (0, 0.02, 0.04, 0.06):
        s += mono(px.X(v), px.y0 + px.h + 15, f"{v:.2f}", size=8, fill=SOFT)
    s += line(px.X(0.05), px.y0, px.X(0.05), px.y0 + px.h, stroke=SOFT, sw=1.0, dash="4,3")
    s += mono(px.X(0.05), px.y0 + px.h + 28, "0.05", size=7.8, fill=SOFT)
    items = [("t-test", EX["p_t"], 112, INK), ("randomisation", PERM["p"], 144, INK),
             ("signed-rank", SR["p"], 240, MUTED), ("sign test", EX["sign"]["p"], 356, MUTED)]
    for lab, p, yy, col in items:
        s += line(px.x0, yy, px.X(p), yy, stroke=col, sw=1.0, op=0.5)
        s += dot(px.X(p), yy, 4.2, fill=col)
        s += mono(px.x0 + 4, yy - 9, f"{lab}  {p:.4f}", size=8.6, fill=col, anchor="start", weight="600")
    s += note_lines(32, 444, [
        ("the two tests on values feel the two large negatives (−67 and −48 eighths) and land on either side of 0.05;", MUTED),
        ("ranks shrink them to 14 and 10 of 15; signs count them as 2 of 15 and ignore how large they are", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("a negative difference", "dot:" + ACCENT + ":4.0"), ("a positive difference", "dot:" + INK + ":4.0")])
    return emit("03", "four-tests-one-dataset", "Four tests, four questions, four p-values",
                "The same 15 differences seen as values, as signed ranks and as signs, and the exact two-sided p-value each "
                "view gives.", "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "a monte carlo permutation p-value is itself random; exact distributions, no simulation")
    pv, pmf = MC["pvalues"], MC["pmf"]
    ax = Axes(96, 96, 380, 320, (0.040, 0.068), (0, max(pmf) * 1.15))
    s += title(ax.x0, ax.y0 - 16, "(a) Darwin's pairs, SciPy's default: 9,999 random sign flips")
    s += ax.frame([0.04, 0.045, 0.05, 0.055, 0.06, 0.065], [], xfmt=lambda v: f"{v:.3f}", grid_y=False,
                  xlab="two-sided p-value of one run")
    s += ax.clip("c4a") + '<g clip-path="url(#c4a)">'
    for p, w_ in zip(pv, pmf):
        if 0.040 <= p <= 0.068:
            s += line(ax.X(p), ax.Y(0), ax.X(p), ax.Y(w_), stroke=ACCENT if p <= 0.05 + 1e-12 else MUTED, sw=1.6,
                      op=None if p <= 0.05 + 1e-12 else 0.8)
    s += "</g>"
    s += line(ax.X(0.05), ax.y0 + 30, ax.X(0.05), ax.Y(0), stroke=INK, sw=1.0, dash="4,3")
    s += line(ax.X(PERM["p"]), ax.y0 + 8, ax.X(PERM["p"]), ax.Y(0), stroke=LINK, sw=1.6)
    s += mono(ax.X(PERM["p"]) + 6, ax.y0 + 18, f"exact p {PERM['p']:.4f}", size=8.4, fill=LINK, anchor="start", weight="600")
    s += mono(ax.X(0.05) - 6, ax.y0 + 42, f"{pct(MC['p_below'], 1)} of runs", size=8.4, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(0.05) - 6, ax.y0 + 56, "give p ≤ 0.05", size=8.4, fill=ACCENT, anchor="end")
    # (b) family-wise error with and without the +1
    bx = Axes(590, 96, 380, 320, (1, 100000), (0, 1), xmap=log10)
    s += title(bx.x0, bx.y0 - 16, "(b) Bonferroni over k true nulls, m permutations each")
    s += bx.frame([1, 10, 100, 1000, 10000, 100000], [0, 0.25, 0.5, 0.75, 1.0], xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: f"{100 * v:.0f}%", xlab="number of tests k (log scale)")
    s += line(bx.x0, bx.Y(0.05), bx.x0 + bx.w, bx.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    ks = FW["999"]["tests"]
    for m, sfx in (("999", ""), ("9999", "10k")):
        s += styled(bx, ks, FW[m]["naive"], "naive" + sfx)
        s += styled(bx, ks, FW[m]["plus_one"], "plus1" + ("_10k" if sfx else ""))
    k1 = ks.index(1000)
    s += dot(bx.X(1000), bx.Y(FW["999"]["naive"][k1]), 3.6, fill=ACCENT)
    s += mono(bx.X(1000) - 8, bx.Y(FW["999"]["naive"][k1]) - 8, f"b/m, m = 999: {pct(FW['999']['naive'][k1], 1)} at k = 1,000",
              size=8.2, fill=ACCENT, anchor="end", weight="600")
    s += mono(bx.X(1.4), bx.Y(0.16), "(b + 1)/(m + 1): never above 5%,", size=8.2, fill=LINK, anchor="start", weight="600")
    s += mono(bx.X(1.4), bx.Y(0.16) + 14, "and 0 once α/k < 1/(m + 1)", size=8.2, fill=LINK, anchor="start")
    s += mono(bx.x0 + bx.w, bx.y0 + bx.h + 46, "independent tests, continuous statistic (Phipson and Smyth's formulas)",
              size=7.8, fill=SOFT, anchor="end")
    s += legend(vh - 24, vw, [("b/m, m = 999", "style:naive"), ("b/m, m = 9,999", "style:naive10k"),
                              ("(b + 1)/(m + 1), m = 999", "style:plus1"), ("(b + 1)/(m + 1), m = 9,999", "style:plus1_10k")])
    return emit("04", "monte-carlo-p-values", "A Monte Carlo p-value is a random variable; add one",
                "Left: the distribution of the p-value SciPy's default permutation test returns on Darwin's pairs, over "
                "reruns. Right: the family-wise error of Bonferroni when permutation p-values are counted as b/m.",
                "when is a permutation test exact?", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "normal data, equal means, 999 random relabellings per data set, 50,000 data sets per point")
    ks = sorted(D40, key=float)
    xs = [float(k) for k in ks]
    ax = Axes(96, 96, 470, 320, (0.25, 4.0), (0, 0.32), xmap=log2)
    s += ax.clip("c5a") + title(ax.x0, ax.y0 - 16, "(a) groups of 10 and 40: size of a 5% test")
    s += ax.frame(RATIO_TICKS, [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], xfmt=ratio_fmt, yfmt=lambda v: f"{100 * v:.0f}%",
                  xlab="SD of the group of 10 / SD of the group of 40 (log scale)")
    inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    for key_, st in (("student", "student"), ("welch", "welch"), ("perm_diff", "perm_diff"), ("perm_studentised", "perm_stud")):
        inner += styled(ax, xs, [D40[k][key_] for k in ks], st)
    s += f'<g clip-path="url(#c5a)">{inner}</g>'
    for k in ks:
        s += dot(ax.X(float(k)), ax.Y(D40[k]["perm_diff"]), 3.2, fill=ACCENT)
        s += dot(ax.X(float(k)), ax.Y(D40[k]["perm_studentised"]), 3.2, fill=LINK)
    s += mono(ax.X(4) - 6, ax.Y(D40["4"]["perm_diff"]) - 10, f"raw difference {pct(D40['4']['perm_diff'], 2)}", size=8.4, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(2) - 8, ax.Y(D40["2"]["perm_diff"]) - 10, pct(D40["2"]["perm_diff"], 2), size=8.4, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(0.25) + 8, ax.Y(0.24), f"Student's t on the same data: {pct(D40['2']['student'], 2)} at 2;", size=8.0, fill=ACCENT, anchor="start")
    s += mono(ax.X(0.25) + 8, ax.Y(0.24) + 14, "its dashed curve lies under the raw one", size=8.0, fill=ACCENT, anchor="start")
    s += mono(ax.X(4) - 6, ax.Y(D40["4"]["perm_studentised"]) - 12, f"studentised {pct(D40['4']['perm_studentised'], 2)}", size=8.4, fill=LINK, anchor="end", weight="600")
    s += mono(ax.X(0.25) + 6, ax.Y(D40["0.25"]["perm_studentised"]) + 20, f"studentised {pct(D40['0.25']['perm_studentised'], 2)}", size=8.2, fill=LINK, anchor="start")
    s += mono(ax.X(0.25) + 6, ax.Y(0) - 8, f"raw {pct(D40['0.25']['perm_diff'], 2)}", size=8.2, fill=ACCENT, anchor="start")
    # (b) equal sizes
    bx = Axes(640, 96, 330, 320, (0.25, 4.0), (0, 0.32), xmap=log2)
    s += bx.clip("c5b") + title(bx.x0, bx.y0 - 16, "(b) groups of 25 and 25")
    s += bx.frame(RATIO_TICKS, [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], xfmt=ratio_fmt, yfmt=lambda v: f"{100 * v:.0f}%",
                  xlab="SD of group 1 / SD of group 2")
    kb = sorted(D25, key=float)
    inner = line(bx.x0, bx.Y(0.05), bx.x0 + bx.w, bx.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    inner += styled(bx, [float(k) for k in kb], [D25[k]["perm_diff"] for k in kb], "perm_diff")
    s += f'<g clip-path="url(#c5b)">{inner}</g>'
    for k in kb:
        s += dot(bx.X(float(k)), bx.Y(D25[k]["perm_diff"]), 3.2, fill=ACCENT)
        s += dot(bx.X(float(k)), bx.Y(D25[k]["perm_diff"]), 1.6, fill=LINK)
    lo, hi = min(v["perm_diff"] for v in D25.values()), max(v["perm_diff"] for v in D25.values())
    s += note_lines(bx.x0 + 14, bx.y0 + 40, [
        ("raw and studentised are the", INK), ("same test here: every data set", MUTED),
        ("gets the same verdict from both", MUTED), (f"{pct(lo, 2)} to {pct(hi, 2)} across ratios", INK)], gap=15)
    s += legend(vh - 24, vw, [("permutation, raw difference", "styledot:perm_diff"), ("permutation, studentised", "styledot:perm_stud"),
                              ("Student's t", "style:student"), ("Welch's t", "style:welch")])
    return emit("05", "permutation-test-of-means", "Exact for identical distributions, not for equal means",
                "The simulated size of two-sample permutation tests of equal means when the SDs differ: the raw difference in "
                "means against the studentised (Welch) statistic, beside Student's and Welch's t-tests on the same data.",
                "does a permutation test compare means?", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def norm_pdf(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def sexp_pdf(x, c):
    """Density of E - c, E ~ Exp(1)."""
    return math.exp(-(x + c)) if x > -c else 0.0


def fig06():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "two populations with sd 1: a normal, and an exponential with mean 1 shifted to the left")
    xs = [i / 100 for i in range(-350, 451)]
    for p, (c, lab, sub) in enumerate(((MW["c1"], "(a) equal medians", f"c = ln 2 = {MW['c1']:.4f}"),
                                         (MW["c2"], "(b) P(X > Y) = 1/2", f"c = {MW['c2']:.4f}"))):
        ax = Axes(96 + p * 470, 96, 400, 300, (-3.5, 4.5), (0, 1.02))
        cid = f"c6{p}"
        s += ax.clip(cid) + title(ax.x0, ax.y0 - 16, f"{lab}, {sub}")
        s += ax.frame([-3, -2, -1, 0, 1, 2, 3, 4], [0, 0.25, 0.5, 0.75, 1.0], yfmt=lambda v: f"{v:.2f}")
        inner = polyline(curve(ax, xs, [norm_pdf(x) for x in xs]), INK, sw=1.8)
        inner += polyline(curve(ax, xs, [sexp_pdf(x, c) for x in xs]), ACCENT, sw=1.8)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        med_y = math.log(2) - c
        s += line(ax.X(0), ax.y0 + 6, ax.X(0), ax.Y(0), stroke=INK, sw=1.0, dash="4,3")
        if abs(med_y) > 1e-4:
            s += line(ax.X(med_y), ax.y0 + 6, ax.X(med_y), ax.Y(0), stroke=ACCENT, sw=1.0, dash="4,3")
        theta = MW["theta1"] if p == 0 else 0.5
        lines = [(f"P(X > Y) = {theta:.4f}" if p == 0 else "P(X > Y) = 0.5000", INK),
                 ("medians 0 and 0" if p == 0 else f"medians 0 and {num(med_y, 3)}", ACCENT if p == 1 else MUTED),
                 (f"means 0 and {num(1 - c, 3)}", MUTED)]
        s += note_lines(ax.X(1.25), ax.y0 + 26, lines, gap=15)
    s += legend(vh - 24, vw, [("X: normal", "line:" + INK + ":1.8"), ("Y: shifted exponential", "line:" + ACCENT + ":1.8"),
                              ("median of X", "dash:" + INK + ":1.0"), ("median of Y, where it differs", "dash:" + ACCENT + ":1.0")])
    return emit("06", "equal-medians-different-shapes", "Equal medians do not make P(X > Y) = ½, and the reverse",
                "Two pairs of populations: equal medians with P(X > Y) = 0.443, and different medians with P(X > Y) = 0.5. "
                "Mann–Whitney's U estimates P(X > Y).", "what does the mann-whitney test test?", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 530
    s = eyebrow(32, 40, "rejection rate of 5% tests, 20,000 simulated data sets per point")
    sizes = sorted(S1, key=int)
    ns = [int(k) for k in sizes]
    for p, (S, lab) in enumerate(((S1, "(a) equal medians, P(X > Y) = 0.443"), (S2, "(b) medians differ, P(X > Y) = ½"))):
        ax = Axes(96 + p * 300, 96, 240, 300, (10, 400), (0, 1.0), xmap=log10)
        s += title(ax.x0, ax.y0 - 16, lab, size=9)
        s += ax.frame([10, 25, 50, 100, 200, 400], [0, 0.25, 0.5, 0.75, 1.0], yfmt=lambda v: f"{100 * v:.0f}%",
                      ylabels=(p == 0), xlab="n per group (log)")
        s += line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
        for key_, st in (("welch", "welch_t"), ("bm", "bm"), ("mw", "mw")):
            s += styled(ax, ns, [S[k][key_] for k in sizes], st)
            for k in sizes:
                s += dot(ax.X(int(k)), ax.Y(S[k][key_]), 2.6, fill=STYLE[st][0])
        if p == 0:
            s += mono(ax.X(10) + 6, ax.Y(0.72), "Mann–Whitney: " + pct(S1["400"]["mw"], 1), size=8.2, fill=ACCENT, anchor="start", weight="600")
            s += mono(ax.X(10) + 6, ax.Y(0.72) + 14, "at 400 per group", size=8.2, fill=ACCENT, anchor="start")
            s += mono(ax.X(100), ax.Y(S1["100"]["welch"]) - 12, "Welch", size=8.2, fill=MUTED, anchor="end")
        else:
            s += mono(ax.X(400) - 4, ax.Y(S2["400"]["welch"]) - 10, "Welch", size=8.2, fill=MUTED, anchor="end")
            s += mono(ax.X(10) + 6, ax.Y(0.24), "Mann–Whitney 4.7% to 5.7%,", size=8.2, fill=ACCENT, anchor="start", weight="600")
            s += mono(ax.X(10) + 6, ax.Y(0.24) + 14, "on the 5% line at every n", size=8.2, fill=ACCENT, anchor="start")
    ks = sorted(S3, key=float)
    cx = Axes(720, 96, 250, 300, (0.25, 4.0), (0, 0.16), xmap=log2)
    s += title(cx.x0, cx.y0 - 16, "(c) normal, equal centres, 10 and 40", size=9)
    s += cx.frame(RATIO_TICKS, [0, 0.04, 0.08, 0.12, 0.16], xfmt=ratio_fmt, yfmt=lambda v: f"{100 * v:.0f}%",
                  xlab="SD of the 10 / SD of the 40")
    s += line(cx.x0, cx.Y(0.05), cx.x0 + cx.w, cx.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    for key_, st in (("welch", "welch_t"), ("bm", "bm"), ("mw", "mw")):
        s += styled(cx, [float(k) for k in ks], [S3[k][key_] for k in ks], st)
        for k in ks:
            s += dot(cx.X(float(k)), cx.Y(S3[k][key_]), 2.6, fill=STYLE[st][0])
    s += mono(cx.X(4) - 4, cx.Y(S3["4"]["mw"]) - 9, pct(S3["4"]["mw"], 2), size=8.2, fill=ACCENT, anchor="end", weight="600")
    s += mono(cx.X(2) - 4, cx.Y(S3["2"]["mw"]) - 9, pct(S3["2"]["mw"], 2), size=8.2, fill=ACCENT, anchor="end", weight="600")
    s += mono(cx.X(0.25) + 4, cx.Y(0.05) - 9, "Brunner–Munzel", size=8.2, fill=LINK, anchor="start", weight="600")
    s += note_lines(96, 452, [
        ("(a) and (b): X normal, Y a shifted exponential, both SD 1, as in Figure 6; (c): P(X > Y) = ½ exactly,", MUTED),
        ("so every rejection is an error for a test of P(X > Y) = ½, and Mann–Whitney's are errors of its variance", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("Mann–Whitney", "styledot:mw"), ("Brunner–Munzel", "styledot:bm"), ("Welch's t (means)", "styledot:welch_t")])
    return emit("07", "what-mann-whitney-rejects", "Mann–Whitney follows P(X > Y), and keeps its level only for identical shapes",
                "How often three 5% tests reject in the two designs of Figure 6, by sample size, and for two normal groups with "
                "equal centres and unequal spreads.", "what does the mann-whitney test test?", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 515
    walsh = sorted((D8[i] + D8[j]) / 16 for i in range(15) for j in range(i, 15))
    assert len(walsh) == 120 and (walsh[59] + walsh[60]) / 2 == HL["estimate"]
    assert walsh[HL["qu"] - 1] == HL["lower"] and walsh[120 - HL["qu"]] == HL["upper"]
    s = eyebrow(32, 40, "darwin's pairs: the 120 walsh averages, the mean of every pair of differences, each with itself included")
    ax = Axes(96, 96, 560, 330, (-9, 10), (0, 121))
    s += title(ax.x0, ax.y0 - 16, "Walsh averages, inches, smallest to largest")
    s += ax.frame([-8, -6, -4, -2, 0, 2, 4, 6, 8, 10], [1, 26, 60, 95, 120], xfmt=lambda v: num(v, 0),
                  yfmt=lambda v: f"{v:.0f}", xlab="Walsh average, inches", grid_y=False)
    s += mono(ax.x0 - 34, ax.y0 - 14, "rank", size=8, fill=SOFT, anchor="start")
    s += rect(ax.X(HL["lower"]), ax.y0, ax.X(HL["upper"]) - ax.X(HL["lower"]), ax.h, fill=LINK, op=0.07, stroke="none", sw=0)
    for k, v in enumerate(walsh, start=1):
        inside = HL["lower"] <= v <= HL["upper"]
        s += dot(ax.X(v), ax.Y(k), 2.3, fill=INK if inside else SOFT)
    for v, lab, anchor, yy in ((HL["lower"], f"26th: {HL['lower']}", "end", ax.y0 + 14),
                               (HL["upper"], f"26th from the top: {HL['upper']}", "start", ax.Y(12))):
        s += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=LINK, sw=1.2, dash="4,3")
        s += mono(ax.X(v) + (-6 if anchor == "end" else 6), yy, lab, size=8.4, fill=LINK, anchor=anchor, weight="600")
    s += line(ax.X(HL["estimate"]), ax.y0 + 24, ax.X(HL["estimate"]), ax.y0 + ax.h, stroke=ACCENT, sw=1.4)
    s += mono(ax.X(HL["estimate"]) - 6, ax.Y(76), f"median {HL['estimate']}", size=8.6, fill=ACCENT, anchor="end", weight="600")
    # comparison: the t interval and the mean
    bx = Axes(700, 150, 270, 120, (-1, 7), (0, 1))
    s += title(bx.x0, 120, "the same pairs, two summaries", size=9)
    s += line(bx.x0, bx.y0 + bx.h, bx.x0 + bx.w, bx.y0 + bx.h, stroke=RULE_SOLID)
    for v in (0, 2, 4, 6):
        s += mono(bx.X(v), bx.y0 + bx.h + 15, f"{v}", size=8, fill=SOFT)
    yy = bx.y0 + 30
    s += line(bx.X(HL["lower"]), yy, bx.X(HL["upper"]), yy, stroke=LINK, sw=2.2) + dot(bx.X(HL["estimate"]), yy, 4.0, fill=ACCENT)
    s += mono(bx.x0, yy - 10, f"Hodges–Lehmann {HL['estimate']}, {HL['lower']} to {HL['upper']}", size=8.2, fill=INK, anchor="start", weight="600")
    yy = bx.y0 + 84
    lo, hi = EX["ci_t"]
    s += line(bx.X(lo), yy, bx.X(hi), yy, stroke=MUTED, sw=2.2) + dot(bx.X(EX["mean"]), yy, 4.0, fill=MUTED)
    s += mono(bx.x0, yy - 10, f"mean {EX['mean']:.3f}, t interval {lo:.3f} to {hi:.3f}", size=8.2, fill=MUTED, anchor="start", weight="600")
    s += note_lines(700, 330, [("the interval is exact by counting:", INK), (f"confidence {pct(HL['confidence'], 2)}, not 95.00%,", MUTED),
                               ("because the signed-rank statistic", MUTED), ("takes whole-number values", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("Walsh average inside the interval", "dot:" + INK + ":2.3"), ("outside", "dot:" + SOFT + ":2.3"),
                              ("Hodges–Lehmann estimate", "line:" + ACCENT + ":1.4"), ("interval ends", "dash:" + LINK + ":1.2")])
    return emit("08", "hodges-lehmann", "The estimate and its interval are order statistics",
                "Darwin's 120 Walsh averages in order. Their median is the Hodges–Lehmann estimate; the 26th from each end "
                "bound the exact interval that inverting the signed-rank test gives.", "how large is the effect?", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 535
    names = sorted(SH, key=lambda k: SH[k]["are"])
    s = eyebrow(32, 40, f"20 per group, a shift of {EF['delta']:.2f} sd (80% power for student's t on normal data), 100,000 data sets")
    ax = Axes(330, 96, 470, 344, (0.70, 1.0), (0, len(names)))
    s += title(ax.x0, ax.y0 - 16, "power of a 5% test, by shape of the distribution (each scaled to SD 1)")
    s += ax.frame([0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.0], [], xfmt=lambda v: f"{100 * v:.0f}%", grid_y=False,
                  xlab="power", grid_x=True)
    s += mono(150, ax.y0 - 16, "ARE", size=9.5, fill=INK, anchor="end", weight="600")
    s += mono(ax.x0 + ax.w + 2, ax.y0 + ax.h + 46, "labels: Mann–Whitney vs Welch", size=8, fill=MUTED, anchor="end")
    for i, k in enumerate(names):
        v = SH[k]
        yy = ax.y0 + (i + 0.5) / len(names) * ax.h
        s += mono(320, yy + 3, k, size=8.8, fill=INK, anchor="end", weight="600")
        s += mono(150, yy + 3, f"{v['are']:.3f}", size=8.8, fill=ACCENT if v["are"] < 1 else LINK, anchor="end", weight="600")
        s += line(ax.X(v["welch"]), yy, ax.X(v["mw"]), yy, stroke=RULE_SOLID, sw=2.2)
        s += dot(ax.X(v["welch"]), yy, 4.4, fill=INK) + dot(ax.X(v["mw"]), yy, 4.4, fill=ACCENT)
        right = max(v["welch"], v["mw"])
        s += mono(ax.X(right) + 10, yy + 3, f"{pct(v['mw'], 1)} vs {pct(v['welch'], 1)}", size=8, fill=MUTED, anchor="start")
    s += note_lines(32, 470, [
        ("ARE: the large-sample ratio of sample sizes for equal power against a small shift, 12σ²(∫f²)²; 3/π = 0.955 for the normal,", MUTED),
        ("never below 108/125 = 0.864. At n = 20 the uniform (ARE 1) still costs Mann–Whitney 6 points: ARE is a limit", MUTED)], gap=15.5)
    s += legend(vh - 24, vw, [("Welch's t", "dot:" + INK + ":4.4"), ("Mann–Whitney", "dot:" + ACCENT + ":4.4")])
    return emit("09", "price-of-ranks", "Ranks cost little in the body and pay in the tails",
                "The asymptotic relative efficiency of the rank-sum test to the t-test, and the power of each at n = 20 per "
                "group, for eight shapes of distribution.", "what do ranks cost?", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 470
    lsat, gpa, rl, rg = CO["lsat"], CO["gpa"], CO["ranks_lsat"], CO["ranks_gpa"]
    s = eyebrow(32, 40, "the law-school sample: average LSAT and undergraduate GPA of 15 schools' classes")
    ax = Axes(96, 96, 280, 300, (540, 670), (2.7, 3.5))
    s += title(ax.x0, ax.y0 - 16, "(a) values: GPA against LSAT")
    s += ax.frame([550, 600, 650], [2.8, 3.0, 3.2, 3.4], xfmt=lambda v: f"{v:.0f}", yfmt=lambda v: f"{v:.1f}",
                  xlab="LSAT", grid_x=True)
    for x, y in zip(lsat, gpa):
        s += dot(ax.X(x), ax.Y(y), 4.0, fill=INK)
    bx = Axes(450, 96, 280, 300, (0.5, 15.5), (0.5, 15.5))
    s += title(bx.x0, bx.y0 - 16, "(b) ranks: GPA's against LSAT's")
    s += bx.frame([1, 5, 10, 15], [1, 5, 10, 15], xfmt=lambda v: f"{v:.0f}", yfmt=lambda v: f"{v:.0f}",
                  xlab="rank of LSAT", grid_x=True)
    s += line(bx.X(0.5), bx.Y(0.5), bx.X(15.5), bx.Y(15.5), stroke=SOFT, sw=0.9, dash="4,3")
    for x, y in zip(rl, rg):
        s += dot(bx.X(x), bx.Y(y), 4.0, fill=INK)
    rows = [("Pearson r", f"{CO['r']:.3f}", [("t-test", CO["library"]["pearsonr_p"]), ("permutation, 99,999", CO["perm_p"]["pearson"])]),
            ("Spearman ρ", f"{CO['rho']:.3f}", [("exact, all 15!", CO["spearman_exact"]["p"]), ("SciPy t approx.", CO["library"]["spearmanr_p"]),
                                                  ("R AS 89", XC["law_spearman_p_as89"])]),
            ("Kendall τ", f"{CO['tau']:.3f}", [("exact (SciPy, R)", CO["library"]["kendalltau_p"])])]
    y = 112
    s += title(780, 96, "coefficient and p-values")
    for lab, est, ps in rows:
        s += mono(780, y + 8, f"{lab} = {est}", size=9, fill=INK, anchor="start", weight="600")
        y += 24
        for pl, pv in ps:
            s += mono(792, y, f"{pl}: {pv:.5f}", size=8.2, fill=ACCENT if pl.startswith("SciPy t") else MUTED, anchor="start")
            y += 16
        y += 12
    s += note_lines(780, y + 6, [(f"τ = ({CO['concordant']} − {CO['discordant']})/105:", MUTED), ("concordant minus", MUTED),
                                 ("discordant pairs", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("one school", "dot:" + INK + ":4.0"), ("ranks in perfect agreement", "dash:" + SOFT + ":0.9")])
    return emit("10", "rank-correlation", "Three correlations of one sample, and five p-values for them",
                "The law-school sample as values and as ranks, with Pearson's, Spearman's and Kendall's coefficients and "
                "their exact, approximate and Monte Carlo p-values.", "rank correlations", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10}

if __name__ == "__main__":
    for k in (sys.argv[1:] or sorted(FIGS)):
        FIGS[k]()
