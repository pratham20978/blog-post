#!/usr/bin/env python3
"""Figures 01-11 for bayesian-inference-conjugate-priors (Statistics for Data Scientists, part 11).

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/bayes.py, or from a closed form
evaluated here (beta, gamma and normal densities through math.lgamma) whose parameters come from the capture. The
asserts below pin each number the article quotes, so a figure cannot drift from the text. Run:  python3 _figs.py [01 ...]
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
LA, PF, CJ, IV, PR, LI = (CAP[k] for k in ("laplace", "pfizer", "conjugate", "intervals", "priors", "lindley"))
XC = CAP["author_crosscheck"]
A0, B0 = 0.700102, 1.0


def hp(share, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return float((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def hv(x, nd=4):
    """A number rounded half up from its stored decimal."""
    return float(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def sci(x, nd=4):
    e = math.floor(math.log10(abs(x)))
    m = (Decimal(repr(float(x))) / Decimal(10) ** e).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    return f"{m} × 10^{e}"


ROWS = {r["endpoint"]: r for r in PF["rows"]}
PRIM = ROWS["covid19_7d_after_dose2_no_prior_infection"]
SEC = ROWS["covid19_7d_after_dose2_with_or_without_prior_infection"]
SEV = ROWS["first_severe_covid19_7d_after_dose2_no_prior_infection"]
CON = PF["constants"]

# ------------------------------------------------------------------ the numbers the article prints, held to the capture
assert (LA["boys"], LA["girls"], LA["posterior"]) == (251527, 241945, [251528, 241946])
assert (hv(LA["mean"], 6), hv(LA["sd"], 6), hv(LA["sds_below_mean"], 2)) == (0.509709, 0.000712, 13.64)
assert sci(LA["tail_exact"]) == "1.1461 × 10^-42" and sci(LA["tail_beta_cdf"]) == "1.1461 × 10^-42"
assert sci(XC["laplace_1745_1770_tail"]) == "1.1461 × 10^-42" and hp(LA["first_over_exact"] - 1, 2) == 0.53
assert hv(LA["laplace_first_term"] * 1e42, 5) == 1.15215 and hv(LA["log10_density_at_half"], 2) == -37.66
assert round(1 / LA["laplace_series"]["second_term"]) == 186 and hv(LA["succession"], 6) == 0.509709
T83 = LA["table1783"]
assert (T83["sum_boys"], T83["sum_girls"], T83["printed_total"], T83["reconciles_with_1812"]) == (141859, 135610, [151859, 145159], True)
assert (LA["tap"]["boys"], LA["tap"]["girls"]) == (393386, 377555)
assert sci(LA["tap"]["tail_exact"]) == "5.5928 × 10^-73" and sci(LA["tap"]["laplace_printed_value"]) == "5.5909 × 10^-73"
assert hv(CON["a_from_rounded_mean"], 6) == 0.700102 and hv(CON["theta_at_ve30"], 6) == 0.411765
assert (hp(CON["ve_at_prior_median"], 1), hv(CON["prior95_ve"][0], 2), hp(CON["prior95_ve"][1], 1)) == (40.9, -26.16, 99.5)
assert (hv(CON["prior_p_ve_lt_0"], 4), hv(CON["prior_p_ve_gt_30"], 4)) == (0.3845, 0.5373)
assert (hp(PRIM["lower"], 1), hp(PRIM["upper"], 1), hp(PRIM["median"], 1), hp(PRIM["mle"], 1)) == (90.3, 97.6, 94.8, 95.0)
assert (hp(SEC["lower"], 1), hp(SEC["upper"], 1)) == (89.9, 97.3) and all(r["matches_published"] for r in PF["rows"])
assert (hp(SEV["lower"], 1), hp(SEV["upper"], 1), hv(SEV["p_ve_gt_30"], 3)) == (-124.8, 96.3, 0.743)
assert sci(PRIM["p_ve_le_30"], 2) == "2.46 × 10^-28" and hv(PRIM["prior_weight"], 4) == 0.0099 and hv(SEV["prior_weight"], 3) == 0.298
assert PF["table6"] == {"success": {"32": 6, "62": 15, "92": 25, "120": 35, "164": 53}, "futility": {"32": 15, "62": 26, "92": 35}}
assert (hp(PF["predictive_32"]["14"]["pos"], 2), hp(PF["predictive_32"]["15"]["pos"], 2)) == (7.19, 3.11)
assert (hv(PF["operating"]["30"]["values"][-1], 3), hv(PF["operating"]["70"]["values"][-1], 3)) == (0.021, 0.994)
assert sum(v["n_match"] for v in PF["operating"].values()) == 44
ARMS = CJ["gamma_poisson"]["arms"]
assert (hv(ARMS["vaccine"]["mean"], 2), [hv(v, 2) for v in ARMS["vaccine"]["interval95"]]) == (3.84, [1.71, 6.82])
assert (hv(ARMS["placebo"]["mean"], 2), [hv(v, 2) for v in ARMS["placebo"]["interval95"]]) == (73.13, [62.32, 84.8])
assert [hp(v, 2) for v in CJ["gamma_poisson"]["ve_interval_jeffreys_rates"]] == [90.46, 97.69]
NN = CJ["normal_normal"]
assert (hv(NN["weight_prior"], 4), hv(NN["posterior"][0], 6), hv(NN["posterior"][1], 6)) == (0.9622, 0.509649, 0.000698)
assert (hv(NN["exact_beta"][0], 6), hv(NN["exact_beta"][1], 6)) == (0.509649, 0.000698)
IP, IS = IV["primary"], IV["severe"]
assert [hp(v, 2) for v in IP["equal_tailed"]] == [90.32, 97.62] and [hp(v, 2) for v in IP["hdi_ve"]] == [90.86, 97.94]
assert [hp(v, 2) for v in IP["hdi_theta_mapped"]] == [90.81, 97.89]
assert [hp(v, 2) for v in IS["equal_tailed"]] == [-124.81, 96.3] and [hp(v, 2) for v in IS["hdi_ve"]] == [-69.71, 99.95]
assert [hp(v, 2) for v in IS["hdi_theta_mapped"]] == [-73.55, 99.08]
assert (hp(IP["p_ve_at_least_lower"]["equal_tailed"], 1), hp(IP["p_ve_at_least_lower"]["hdi_ve"], 1)) == (97.5, 96.1)
CP_, CS_ = IP["coverage"], IS["coverage"]
assert [hp(v, 1) for v in CP_["credible_range_ve_0_95"]] == [92.9, 96.5] and [hp(v, 1) for v in CP_["cp_range_ve_0_95"]] == [95.1, 98.0]
assert [hp(v, 1) for v in CS_["credible_range_ve_0_95"]] == [91.7, 100.0] and hp(CS_["credible_min_ve_0_99"], 1) == 86.6
assert hp(CS_["credible_min_at_ve"], 1) == 96.3 and hp(CS_["cp_min_ve_0_99"], 1) == 97.5
assert hp(CP_["prior_average_quadrature"], 4) == 95.0 and hp(CS_["prior_average_quadrature"], 4) == 95.0
assert (hp(CP_["prior_average_mc"], 2), hp(CP_["prior_average_mcse"], 2), CP_["draws"]) == (95.01, 0.03, 400000)
assert (hp(CS_["prior_average_mc"], 2), hp(CS_["prior_average_mcse"], 2)) == (95.03, 0.03)
NM = PR["named"]
assert sorted(hp(NM["primary"][k]["lower"], 1) for k in ("trial", "senn_alternative", "uniform", "jeffreys", "haldane")) == [90.1, 90.1, 90.3, 90.5, 90.9]
assert (min(hp(NM["severe"][k]["lower"], 1) for k in ("trial", "senn_alternative", "uniform", "jeffreys", "haldane")),
        max(hp(NM["severe"][k]["lower"], 1) for k in ("trial", "senn_alternative", "uniform", "jeffreys", "haldane"))) == (-154.6, -116.6)
MK = PR["sweep"]["ve0_primary"]["marker"]
assert (MK["kappa"], hp(MK["lower"], 1), hp(MK["upper"], 1)) == (170, 52.3, 70.4)
PP = PR["prior_probabilities"]
assert (hv(PP["uniform"]["p_ve_lt_0"], 2), hv(PP["uniform"]["p_ve_gt_90"], 4), hv(PP["uniform"]["p_ve_gt_30"], 4)) == (0.5, 0.0909, 0.4118)
Y82 = LI["years"]["1782"]
assert (Y82["boys"], Y82["n"], hv(Y82["z"], 3), hv(Y82["p_exact"], 4), hv(Y82["bf01"], 2), hv(Y82["post_h0"], 3)) == (9851, 19387, 2.262, 0.0241, 8.6, 0.896)
FO = LI["focus"]
assert (hv(FO["bf10_informed"], 2), hv(FO["bf10_maximum"], 2), hv(FO["estimation"]["p_theta_le_half"], 4)) == (11.54, 12.93, 0.0118)
assert LI["lindley_years"] == ["1772", "1778", "1779", "1782"]
assert (round(LI["crossings"]["z_1782"]["bf_1"]), round(LI["crossings"]["z_1782"]["bf_19"])) == (260, 94708)
assert hv(LI["jeffreys_even_z"], 3) == 3.069 and hv(XC["paris_1782_bf10_informed"], 2) == 11.54


# ------------------------------------------------------------------ drawing helpers (Part 10's set)
def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}{o}/>')


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
        if ylab:   # just above the frame, below the panel title at y0 - 16
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
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1], sw=1.6)
        elif part[0] == "bar":
            s += rect(x, y + 1, 18, 8, fill=part[1], op=float(part[2]), stroke=part[1], sw=0.8)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 24
    return s


def pct(v, nd=1):
    return f"{hp(v, nd):.{nd}f}%".replace("-", "−")


def num(v, nd=1):
    return f"{v:,.{nd}f}".replace("-", "−")


def curve(ax, xs, ys):
    assert all(v == v for v in ys), "a NaN would make the browser drop the whole polyline"
    return [(ax.X(a), ax.Y(b)) for a, b in zip(xs, ys)]


def log10(v):
    return math.log10(v)


def beta_logpdf(x, a, b):
    if x <= 0 or x >= 1:
        return -math.inf
    return (a - 1) * math.log(x) + (b - 1) * math.log1p(-x) - (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b))


def beta_pdf(x, a, b):
    return math.exp(beta_logpdf(x, a, b))


def gamma_pdf(x, k, rate):
    return math.exp(k * math.log(rate) + (k - 1) * math.log(x) - rate * x - math.lgamma(k))


def norm_pdf(x, m, s):
    return math.exp(-0.5 * ((x - m) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def post_ab(row):
    """The posterior's beta shapes from the prior and the split: the capture keeps only six significant digits."""
    yv, yp = row["split"]
    return A0 + yv, B0 + yp


def theta_of(ve, r):
    return r * (1 - ve) / (1 + r * (1 - ve))


def ve_pdf(v, a, b, r):
    """Density of VE = 1 - theta/((1 - theta) r) when theta ~ beta(a, b)."""
    return beta_pdf(theta_of(v, r), a, b) * r / (1 + r * (1 - v)) ** 2


def lin(a, b, m):
    return [a + (b - a) * i / (m - 1) for i in range(m)]


def geom(a, b, m):
    return [a * (b / a) ** (i / (m - 1)) for i in range(m)]


def interval_bar(ax, y, lo, hi, colour, label, value_text, h=9, op=0.22, value_side="right"):
    xa, xb = ax.X(max(lo, ax.xr[0])), ax.X(min(hi, ax.xr[1]))
    s = rect(xa, y - h / 2, xb - xa, h, fill=colour, op=op, stroke=colour, sw=1.0)
    if label:
        s += mono(ax.x0 - 10, y + 3, label, size=8, fill=colour, anchor="end", weight="600")
    if value_side == "right":
        s += mono(xb + 8, y + 3, value_text, size=8, fill=colour, anchor="start")
    else:
        s += mono(xa - 8, y + 3, value_text, size=8, fill=colour, anchor="end")
    return s


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 500
    a, b = LA["posterior"]
    s = eyebrow(32, 40, "Laplace's question: Paris baptisms 1745-1770, a uniform prior on x, the chance that a birth is a boy")
    xs = lin(0.4985, 0.5135, 601)
    ax = Axes(96, 96, 380, 300, (0.4985, 0.5135), (0, 600))
    s += ax.clip("c1a") + title(ax.x0, ax.y0 - 16, f"(a) posterior density of x: beta({a:,}, {b:,})")
    s += ax.frame([0.50, 0.505, 0.51], [0, 200, 400, 600], xfmt=lambda v: f"{v:.3f}", yfmt=lambda v: f"{v:.0f}",
                  xlab="x, probability that a birth is a boy")
    inner = polyline(curve(ax, xs, [beta_pdf(x, a, b) for x in xs]), ACCENT, sw=1.9)
    s += f'<g clip-path="url(#c1a)">{inner}</g>'
    s += line(ax.X(0.5), ax.y0 + 4, ax.X(0.5), ax.Y(0), stroke=INK, sw=1.2, dash="4,3")
    s += mono(ax.X(0.5) + 6, ax.y0 + 20, "x = 1/2", size=8.5, fill=INK, anchor="start", weight="600")
    s += note_lines(ax.X(0.5) + 6, ax.y0 + 40, [(f"mean {LA['mean']:.6f}, SD {LA['sd']:.6f}", MUTED),
                                                 (f"1/2 lies {hv(LA['sds_below_mean'], 2):.2f} SDs below the mean", MUTED)])
    bx = Axes(596, 96, 380, 300, (0.4985, 0.5135), (-45, 5))
    s += bx.clip("c1b") + title(bx.x0, bx.y0 - 16, "(b) the same density on a log scale")
    s += bx.frame([0.50, 0.505, 0.51], [-40, -30, -20, -10, 0], xfmt=lambda v: f"{v:.3f}", yfmt=lambda v: f"{v:.0f}",
                  xlab="x", ylab="log10 density")
    ld = [beta_logpdf(x, a, b) / math.log(10) for x in xs]
    left = [(x, v) for x, v in zip(xs, ld) if x <= 0.5]
    inner = area([(bx.X(xs[0]), bx.Y(-45))] + curve(bx, [p[0] for p in left], [p[1] for p in left]) + [(bx.X(0.5), bx.Y(-45))], ACCENT, 0.22)
    inner += polyline(curve(bx, xs, ld), ACCENT, sw=1.9)
    s += f'<g clip-path="url(#c1b)">{inner}</g>'
    s += line(bx.X(0.5), bx.y0 + 4, bx.X(0.5), bx.Y(-45), stroke=INK, sw=1.2, dash="4,3")
    s += dot(bx.X(0.5), bx.Y(LA["log10_density_at_half"]), 3.2, fill=INK)
    s += mono(bx.X(0.5) + 8, bx.Y(LA["log10_density_at_half"]) + 4, f"{num(hv(LA['log10_density_at_half'], 2), 2)} at x = 1/2",
              size=8, fill=INK, anchor="start")
    s += note_lines(bx.X(0.5025), bx.y0 + 160, [("shaded: P(x ≤ 1/2)", ACCENT), (f"exact {sci(LA['tail_exact'])}", INK),
                                                ("Laplace's first term, 1781:", MUTED), ("1.1521 × 10^-42", MUTED)])
    s += legend(vh - 24, vw, [("posterior of x under a uniform prior", "line:" + ACCENT + ":1.9"),
                              ("tail at or below 1/2 (shaded)", "band:" + ACCENT + ":0.22"), ("x = 1/2", "dash:" + INK + ":1.2")])
    return emit("01", "laplace-paris-baptisms", "Half lies 13.6 standard deviations into the tail",
                "Laplace's posterior for the probability that a birth is a boy, from 251,527 boys and 241,945 girls baptised in "
                "Paris, 1745 to 1770, under a uniform prior. Its mass at or below ½ is 1.1461 × 10⁻⁴².",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "the trial's primary analysis: prior beta(0.700102, 1) on θ, 8 of 170 cases, efficacy VE = 1 - θ/((1 - θ) r)")
    ax = Axes(96, 96, 380, 300, (0, 1), (0, 3))
    s += ax.clip("c2a") + title(ax.x0, ax.y0 - 16, "(a) the prior on θ, the vaccine group's share of cases")
    s += ax.frame([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 1, 2, 3], xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: f"{v:.0f}",
                  xlab="θ (top: the efficacy it implies, r = 1)")
    xs = lin(0.004, 0.999, 400)
    inner = polyline(curve(ax, xs, [beta_pdf(x, A0, B0) for x in xs]), MUTED, sw=1.8)
    s += f'<g clip-path="url(#c2a)">{inner}</g>'
    th30 = CON["theta_at_ve30"]
    s += line(ax.X(th30), ax.y0, ax.X(th30), ax.Y(0), stroke=ACCENT, sw=1.1, dash="4,3")
    s += line(ax.X(0.5), ax.y0, ax.X(0.5), ax.Y(0), stroke=SOFT, sw=0.9, dash="2,3")
    for t, lab in ((1 / 21, "95%"), (th30, "30%"), (0.5, "0%"), (0.75, "−200%"), (0.9, "−800%")):
        s += mono(ax.X(t), ax.y0 - 2, lab, size=7.5, fill=SOFT)
    s += note_lines(ax.X(0.535), ax.y0 + 60, [("VE = 30% at θ = 0.4118,", ACCENT), ("the prior's mean", ACCENT), ("", MUTED),
                                               (f"prior P(VE < 0) = {hv(CON['prior_p_ve_lt_0'], 3):.3f}", MUTED),
                                               (f"prior median VE {pct(CON['ve_at_prior_median'], 1)}", MUTED),
                                               ("prior 95%: VE −2,616%", MUTED), ("to 99.5%", MUTED)])
    a, b = post_ab(PRIM)
    r = PRIM["r"]
    bx = Axes(596, 96, 380, 300, (0.86, 1.0), (0, 0.45))
    s += bx.clip("c2b") + title(bx.x0, bx.y0 - 16, f"(b) posterior of VE: θ ~ beta({a:.6f}, {b:g}), r = {r:.4f}")
    s += bx.frame([0.86, 0.90, 0.94, 0.98], [0, 0.1, 0.2, 0.3, 0.4], xfmt=lambda v: f"{100 * v:.0f}%", yfmt=lambda v: f"{v:.1f}",
                  xlab="vaccine efficacy", ylab="density per point of VE")
    vs = lin(0.86, 0.9995, 500)
    dens = [ve_pdf(v, a, b, r) / 100 for v in vs]
    band = [(v, d) for v, d in zip(vs, dens) if PRIM["lower"] <= v <= PRIM["upper"]]
    inner = area([(bx.X(band[0][0]), bx.Y(0))] + curve(bx, [p[0] for p in band], [p[1] for p in band]) + [(bx.X(band[-1][0]), bx.Y(0))], ACCENT, 0.20)
    inner += polyline(curve(bx, vs, dens), ACCENT, sw=1.9)
    s += f'<g clip-path="url(#c2b)">{inner}</g>'
    for v, lab, col, dy in ((PRIM["median"], f"median {pct(PRIM['median'], 1)}", ACCENT, 0), (PRIM["mle"], f"point estimate {pct(PRIM['mle'], 1)}", INK, 14)):
        s += line(bx.X(v), bx.Y(0), bx.X(v), bx.y0 + 30 + dy, stroke=col, sw=1.0, dash="3,3")
    s += mono(bx.X(PRIM["median"]) - 6, bx.y0 + 26, f"median {pct(PRIM['median'], 1)}", size=8, fill=ACCENT, anchor="end", weight="600")
    s += mono(bx.X(PRIM["mle"]) + 6, bx.y0 + 40, f"MLE {pct(PRIM['mle'], 1)}", size=8, fill=INK, anchor="start")
    s += note_lines(bx.x0 + 8, bx.y0 + 200, [("95% credible interval", ACCENT),
                                              (f"{pct(PRIM['lower'], 1)} to {pct(PRIM['upper'], 1)}", ACCENT),
                                              ("published: 90.3 to 97.6", MUTED)])
    s += legend(vh - 24, vw, [("prior on θ", "line:" + MUTED + ":1.8"), ("posterior of VE", "line:" + ACCENT + ":1.9"),
                              ("95% credible interval", "band:" + ACCENT + ":0.20"), ("VE = 30%, the efficacy bar", "dash:" + ACCENT + ":1.1")])
    return emit("02", "trial-prior-to-posterior", "From the protocol's prior to the published interval",
                "The prior on the vaccine group's share of cases, with the efficacy each share implies, and the posterior of "
                "vaccine efficacy after 8 of 170 cases, adjusted for surveillance time.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "prior × likelihood = posterior: the same prior with 4 cases and with 170")
    panels = ((SEV, "(a) severe Covid-19: 1 vaccine, 3 placebo cases", (0, 1), (0, 3.2), [0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 1, 2, 3]),
              (PRIM, "(b) primary endpoint: 8 vaccine, 162 placebo", (0, 0.15), (0, 32), [0, 0.05, 0.10, 0.15], [0, 10, 20, 30]))
    for p, (row, lab, xr, yr, xt, yt) in enumerate(panels):
        yv, yp = row["split"]
        a, b = post_ab(row)
        ax = Axes(96 + p * 500, 96, 380, 300, xr, yr)
        cid = f"c3{p}"
        s += ax.clip(cid) + title(ax.x0, ax.y0 - 16, lab)
        s += ax.frame(xt, yt, xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: f"{v:.0f}", xlab="θ, the vaccine group's share")
        xs = lin(xr[0] + 0.0005, xr[1] - 0.0005, 400)
        inner = polyline(curve(ax, xs, [beta_pdf(x, A0, B0) for x in xs]), MUTED, sw=1.5, dash="5,3")
        inner += polyline(curve(ax, xs, [beta_pdf(x, yv + 1, yp + 1) for x in xs]), LINK, sw=1.6)
        inner += polyline(curve(ax, xs, [beta_pdf(x, a, b) for x in xs]), ACCENT, sw=2.0)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        share = yv / (yv + yp)
        w = row["prior_weight"]
        items = [(f"prior mean 0.4118, worth {A0 + B0:.2f} cases", MUTED), (f"observed share {share:.4f}", LINK),
                 (f"posterior mean {row['posterior_mean_theta']:.4f}", ACCENT),
                 (f"= {w:.4f} × 0.4118 + {1 - w:.4f} × {share:.4f}", INK)]
        s += note_lines(ax.X(xr[0] + 0.42 * (xr[1] - xr[0])), ax.y0 + 24, items, gap=15)
    s += legend(vh - 24, vw, [("prior, beta(0.700102, 1)", "dash:" + MUTED + ":1.5"), ("likelihood, scaled to a density", "line:" + LINK + ":1.6"),
                              ("posterior", "line:" + ACCENT + ":2.0")])
    return emit("03", "posterior-as-compromise", "The posterior is a compromise weighted by counts",
                "With 4 cases the prior keeps 30% of the weight on the posterior mean; with 170 it keeps 1%.", "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "two more conjugate pairs: Poisson counts with exposure and a gamma prior; a normal mean and a normal prior")
    ax = Axes(96, 96, 380, 300, (1, 120), (0, 5.6), xmap=log10)
    s += ax.clip("c4a") + title(ax.x0, ax.y0 - 16, "(a) each arm's case rate, Jeffreys' prior λ^(−1/2)")
    s += ax.frame([1, 2, 5, 10, 20, 50, 100], [0, 1, 2, 3, 4, 5], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:.0f}",
                  xlab="cases per 1,000 person-years (log)", ylab="density of log λ")
    peaks = {}
    for arm, col in (("vaccine", LINK), ("placebo", INK)):
        k, rate = ARMS[arm]["posterior"]
        xs = geom(1, 120, 600)
        ys = [x * gamma_pdf(x, k, rate) for x in xs]
        peaks[arm] = max(ys)
        s += f'<g clip-path="url(#c4a)">{polyline(curve(ax, xs, ys), col, sw=1.9)}</g>'
        lo, hi = ARMS[arm]["interval95"]
        yb = ax.Y(peaks[arm] + 0.3)
        s += rect(ax.X(lo), yb - 3, ax.X(hi) - ax.X(lo), 6, fill=col, op=0.25, stroke=col, sw=0.8)
    assert peaks["placebo"] + 0.3 < 5.6 and peaks["vaccine"] < 1.6
    v, pl = ARMS["vaccine"], ARMS["placebo"]
    s += note_lines(ax.X(1.1), ax.Y(4.9), [(f"vaccine: {v['cases']} cases in {v['thousand_person_years']}", LINK),
                                            (f"gamma({v['posterior'][0]}, rate {v['posterior'][1]})", LINK),
                                            (f"mean {v['mean']:.2f}", LINK), (f"95% {v['interval95'][0]:.2f} to {v['interval95'][1]:.2f}", LINK)], gap=14)
    s += note_lines(ax.X(9.5), ax.Y(2.9), [(f"placebo: {pl['cases']} in {pl['thousand_person_years']}", INK),
                                            (f"gamma({pl['posterior'][0]}, {pl['posterior'][1]})", INK),
                                            (f"mean {pl['mean']:.2f}", INK), (f"95% {pl['interval95'][0]:.2f} to {pl['interval95'][1]:.2f}", INK)], gap=14)
    m0, s0 = NN["prior"]
    phat, se, n = NN["data"]
    mp, sp = NN["posterior"]
    bx = Axes(596, 96, 380, 300, (0.496, 0.520), (0, 620))
    s += bx.clip("c4b") + title(bx.x0, bx.y0 - 16, "(b) Paris 1782 after 1745-1770, normal approximations")
    s += bx.frame([0.50, 0.505, 0.51, 0.515, 0.52], [0, 200, 400, 600], xfmt=lambda v: f"{v:.3f}", yfmt=lambda v: f"{v:.0f}",
                  xlab="x, probability that a birth is a boy")
    xs = lin(0.496, 0.520, 600)
    inner = polyline(curve(bx, xs, [norm_pdf(x, m0, s0) for x in xs]), MUTED, sw=1.5, dash="5,3")
    inner += polyline(curve(bx, xs, [norm_pdf(x, phat, se) for x in xs]), LINK, sw=1.6)
    inner += polyline(curve(bx, xs, [norm_pdf(x, mp, sp) for x in xs]), ACCENT, sw=2.0)
    s += f'<g clip-path="url(#c4b)">{inner}</g>'
    w = NN["weight_prior"]
    s += note_lines(bx.X(0.4965), bx.y0 + 22, [("prior: 1745-1770", MUTED), (f"{m0:.6f} ± {s0:.6f}", MUTED), (f"weight {w:.3f}", MUTED), ("", MUTED),
                                                ("1782 alone", LINK), (f"{phat:.5f} ± {se:.5f}", LINK), (f"weight {1 - w:.3f}", LINK)], gap=14)
    s += note_lines(bx.X(0.5118), bx.y0 + 22, [("posterior", ACCENT), (f"{mp:.6f} ± {sp:.6f}", ACCENT), ("", MUTED),
                                                ("exact beta update", INK), (f"{NN['exact_beta'][0]:.6f} ± {NN['exact_beta'][1]:.6f}", INK)], gap=14)
    s += legend(vh - 24, vw, [("vaccine arm", "line:" + LINK + ":1.9"), ("placebo arm", "line:" + INK + ":1.9"),
                              ("95% interval (bar)", "bar:" + LINK + ":0.25"), ("prior", "dash:" + MUTED + ":1.5"),
                              ("posterior", "line:" + ACCENT + ":2.0")])
    return emit("04", "gamma-poisson-normal-normal", "Gamma–Poisson for rates, normal–normal for means",
                "Left: posteriors of the two arms' case rates per 1,000 person-years. Right: one year of Paris baptisms added to "
                "26 years, by precision weights, against the exact beta update.", "conjugate priors from the likelihood kernel", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 540
    s = eyebrow(32, 40, "three 95% intervals from one posterior: equal tails, highest density of VE, highest density of θ mapped to VE")
    panels = ((IS, SEV, "(a) severe Covid-19, 1:3", (-3.0, 1.0), [-3, -2, -1, 0, 1], "left", "published: −124.8 to 96.3 (FDA Table 11)"),
              (IP, PRIM, "(b) primary endpoint, 8:162", (0.88, 1.0), [0.88, 0.92, 0.96, 1.0], "right", "published: 90.3 to 97.6 (NEJM Table 2)"))
    for p, (iv, row, lab, xr, xt, side, pub) in enumerate(panels):
        a, b = post_ab(row)
        r = row["r"]
        vs = lin(xr[0], min(xr[1], 0.99995), 900)
        dens = [ve_pdf(v, a, b, r) / 100 for v in vs]
        ax = Axes(150 + p * 470, 96, 320, 200, xr, (0, 1.12 * max(dens)))
        cid = f"c5{p}"
        s += ax.clip(cid) + title(ax.x0, ax.y0 - 16, lab)
        s += ax.frame(xt, [], xfmt=lambda v: f"{100 * v:.0f}%", grid_y=False)
        inner = area([(ax.X(vs[0]), ax.Y(0))] + curve(ax, vs, dens) + [(ax.X(vs[-1]), ax.Y(0))], ACCENT, 0.10)
        inner += polyline(curve(ax, vs, dens), ACCENT, sw=1.8)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "vaccine efficacy", size=8.5, fill=SOFT, anchor="end")
        y0 = ax.y0 + ax.h + 66
        bars = (("equal-tailed", iv["equal_tailed"], INK), ("HDI of VE", iv["hdi_ve"], ACCENT), ("HDI of θ, mapped", iv["hdi_theta_mapped"], LINK))
        for k, (name, (lo, hi), col) in enumerate(bars):
            s += interval_bar(ax, y0 + 26 * k, lo, hi, col, name if p == 0 else None, f"{pct(lo, 1)} to {pct(hi, 1)}", value_side=side)
        pl = iv["p_ve_at_least_lower"]
        s += note_lines(ax.x0, y0 + 84, [(pub, SOFT), (f"P(VE ≥ lower end): {pct(pl['equal_tailed'], 1)}, {pct(pl['hdi_ve'], 1)}, {pct(pl['hdi_theta'], 1)}", MUTED)])
    s += legend(vh - 24, vw, [("posterior density of VE", "line:" + ACCENT + ":1.8"), ("equal-tailed", "bar:" + INK + ":0.22"),
                              ("highest density, VE scale", "bar:" + ACCENT + ":0.22"), ("highest density, θ scale", "bar:" + LINK + ":0.22")])
    return emit("05", "equal-tailed-and-highest-density", "The published intervals are the equal-tailed ones",
                "For a skewed posterior the shortest interval differs from the quantile interval, and the shortest interval on "
                "one scale is not the shortest on another.", "credible intervals: equal tails or highest density?", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "exact coverage: the chance the trial's 95% credible interval contains the true efficacy, at each true efficacy")
    panels = ((CP_, "(a) 170 cases, as in the primary analysis", (0.0, 1.0), [0, 0.25, 0.5, 0.75, 1.0]),
              (CS_, "(b) 4 cases, as in the severe-case analysis", (-1.0, 1.0), [-1, -0.5, 0, 0.5, 1.0]))
    for p, (cv, lab, xr, xt) in enumerate(panels):
        ax = Axes(96 + p * 470, 96, 400, 300, xr, (0.84, 1.0))
        cid = f"c6{p}"
        s += ax.clip(cid) + title(ax.x0, ax.y0 - 16, lab)
        s += ax.frame(xt, [0.85, 0.90, 0.95, 1.0], xfmt=lambda v: f"{100 * v:.0f}%", yfmt=lambda v: f"{100 * v:.0f}%",
                      xlab="true vaccine efficacy", ylabels=(p == 0))
        pts = [(v, c, q) for v, c, q in zip(cv["ve_grid"], cv["credible"], cv["clopper_pearson"]) if xr[0] <= v <= xr[1]]
        inner = polyline(curve(ax, [t[0] for t in pts], [t[2] for t in pts]), LINK, sw=1.1)
        inner += polyline(curve(ax, [t[0] for t in pts], [t[1] for t in pts]), ACCENT, sw=1.4)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        s += line(ax.x0, ax.Y(0.95), ax.x0 + ax.w, ax.Y(0.95), stroke=INK, sw=1.0, dash="4,3")
        lo, hi = cv["credible_range_ve_0_95"]
        qlo, qhi = cv["cp_range_ve_0_95"]
        s += note_lines(ax.x0 + 10, ax.Y(0.84) - 50, [(f"credible: {pct(lo, 1)} to {pct(hi, 1)} for VE 0 to 95%", ACCENT),
                                                       (f"Clopper–Pearson: {pct(qlo, 1)} to {pct(qhi, 1)}", LINK),
                                                       (f"averaged over the prior: {pct(cv['prior_average_quadrature'], 3)}", INK)], gap=14)
    s += legend(vh - 24, vw, [("95% credible interval, trial's prior", "line:" + ACCENT + ":1.4"),
                              ("95% Clopper–Pearson interval", "line:" + LINK + ":1.1"), ("95%", "dash:" + INK + ":1.0")])
    return emit("06", "credible-interval-coverage", "95% on average over the prior, not at every true value",
                "Exact frequentist coverage of the trial's credible interval against the true efficacy, beside the "
                "Clopper–Pearson interval, for 170 and for 4 cases.", "what does a credible interval promise?", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "the protocol's futility rule: the posterior predictive probability that the final analysis (164 cases) succeeds")
    pr = PF["predictive_32"]
    ax = Axes(96, 96, 400, 300, (25, 95), (0, 0.035))
    s += ax.clip("c7a") + title(ax.x0, ax.y0 - 16, "(a) at 32 cases: vaccine cases among the next 132")
    s += ax.frame([30, 40, 50, 60, 70, 80, 90], [0, 0.01, 0.02, 0.03], yfmt=lambda v: f"{v:.2f}", xlab="vaccine cases among the remaining 132")
    for x_, col in (("14", LINK), ("15", ACCENT)):
        pmf = pr[x_]["pmf"]
        need = pr[x_]["need_at_most"]
        pts = [(k, pmf[k]) for k in range(len(pmf)) if 25 <= k <= 95]
        inner = ""
        if x_ == "15":
            sh = [(k, v) for k, v in pts if k <= need]
            inner += area([(ax.X(sh[0][0]), ax.Y(0))] + curve(ax, [q[0] for q in sh], [q[1] for q in sh]) + [(ax.X(sh[-1][0]), ax.Y(0))], col, 0.22)
        inner += polyline(curve(ax, [q[0] for q in pts], [q[1] for q in pts]), col, sw=1.7)
        s += f'<g clip-path="url(#c7a)">{inner}</g>'
        s += line(ax.X(need + 0.5), ax.y0 + 8, ax.X(need + 0.5), ax.Y(0), stroke=col, sw=1.0, dash="3,3")
    s += mono(ax.X(39.5) + 4, ax.y0 + 16, "≤ 39", size=8, fill=LINK, anchor="start", weight="600")
    s += mono(ax.X(38.5) - 4, ax.y0 + 16, "≤ 38", size=8, fill=ACCENT, anchor="end", weight="600")
    bx = Axes(606, 96, 370, 300, (0, 50), (0, 1.0))
    s += title(bx.x0, bx.y0 - 16, "(b) POS against the vaccine cases so far")
    s += bx.frame([0, 10, 20, 30, 40, 50], [0, 0.25, 0.5, 0.75, 1.0], yfmt=lambda v: f"{100 * v:.0f}%", xlab="vaccine cases at the interim analysis")
    s += line(bx.x0, bx.Y(0.05), bx.x0 + bx.w, bx.Y(0.05), stroke=INK, sw=1.0, dash="4,3")
    for n, col in (("32", ACCENT), ("62", LINK), ("92", INK)):
        pos = PF["pos_curves"][n]
        xs = list(range(min(len(pos), 51)))
        s += polyline(curve(bx, xs, pos[: len(xs)]), col, sw=1.6)
        f = PF["table6"]["futility"][n]
        s += dot(bx.X(f), bx.Y(pos[f]), 3.4, fill=col)
        s += mono(bx.X(f) + 6, bx.Y(0.05) - 8, f"≥ {f}", size=8, fill=col, anchor="start", weight="600")
        half = min(range(len(xs)), key=lambda k: abs(pos[k] - 0.5))
        s += mono(bx.X(half) + 6, bx.Y(0.5), f"{n} cases", size=8, fill=col, anchor="start", weight="600")
    s += note_lines(96, 452, [(f"(a) with 14 of the first 32 cases in the vaccine group, the final success region (≤ 53 of 164) needs ≤ 39 of the next 132: "
                               f"POS {pct(pr['14']['pos'], 2)}; with 15, ≤ 38: POS {pct(pr['15']['pos'], 2)}, below 5%.", MUTED),
                              ("(b) the protocol stops for futility at the first count whose POS is under 5%: 15 at 32 cases, 26 at 62, 35 at 92.", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("14 vaccine cases of 32", "line:" + LINK + ":1.7"), ("15 of 32", "line:" + ACCENT + ":1.7"),
                              ("success region, 15 of 32", "band:" + ACCENT + ":0.22"), ("5% line", "dash:" + INK + ":1.0")])
    return emit("07", "predictive-futility-rule", "The futility rule is a posterior predictive probability",
                "The beta-binomial predictive distribution of future vaccine cases, and the predictive probability of final "
                "success that sets the protocol's futility boundaries at 15, 26 and 35 cases.", "the posterior predictive distribution", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "95% credible interval of VE against the prior's weight in cases, for priors centred at VE 30% and at VE 0%")
    panels = (("primary", "(a) primary endpoint, 8:162", (-0.4, 1.0), [-0.4, 0, 0.4, 0.8, 1.0]),
              ("severe", "(b) severe Covid-19, 1:3", (-1.6, 1.0), [-1.5, -1.0, -0.5, 0, 0.5, 1.0]))
    for p, (name, lab, yr, yt) in enumerate(panels):
        ax = Axes(96 + p * 470, 96, 400, 300, (0.1, 1000), yr, xmap=log10)
        cid = f"c8{p}"
        s += ax.clip(cid) + title(ax.x0, ax.y0 - 16, lab)
        s += ax.frame([0.1, 1, 10, 100, 1000], yt, xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{100 * v:.0f}%",
                      xlab="prior weight, a + b, in cases (log)")
        inner = ""
        sw30 = PR["sweep"][f"ve30_{name}"]
        inner += area(curve(ax, sw30["kappa"], sw30["upper"]) + curve(ax, sw30["kappa"][::-1], sw30["lower"][::-1]), ACCENT, 0.18)
        inner += polyline(curve(ax, sw30["kappa"], sw30["median"]), ACCENT, sw=1.8)
        sw0 = PR["sweep"][f"ve0_{name}"]
        for key_ in ("lower", "upper"):
            inner += polyline(curve(ax, sw0["kappa"], sw0[key_]), LINK, sw=1.3, dash="5,3")
        inner += polyline(curve(ax, sw0["kappa"], sw0["median"]), LINK, sw=1.8)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        s += line(ax.X(1.700102), ax.y0, ax.X(1.700102), ax.y0 + ax.h, stroke=INK, sw=1.0, dash="4,3")
        nobs = 170 if name == "primary" else 4
        s += line(ax.X(nobs), ax.y0, ax.X(nobs), ax.y0 + ax.h, stroke=SOFT, sw=0.9, dash="2,3")
    m = PR["sweep"]["ve0_primary"]["marker"]
    sev_lo = [v for c in ("ve30", "ve0") for v in PR["sweep"][f"{c}_severe"]["lower"]]
    s += note_lines(96, 446, [("black dashed: the trial's prior, worth 1.7 cases; grey dotted: the data, 170 cases in (a) and 4 in (b)", MUTED),
                              (f"(a) a sceptical prior at VE 0% worth 170 cases puts the interval at {pct(m['lower'], 1)} to {pct(m['upper'], 1)}; "
                               f"(b) across these priors the lower limit runs from {pct(min(sev_lo), 1)} to {pct(max(sev_lo), 1)}", MUTED)], gap=15)
    s += legend(vh - 24, vw, [("prior at VE 30%: 95% interval", "band:" + ACCENT + ":0.18"), ("median", "line:" + ACCENT + ":1.8"),
                              ("prior at VE 0%: 95% interval", "dash:" + LINK + ":1.3"), ("median", "line:" + LINK + ":1.8")])
    return emit("08", "prior-sensitivity", "170 cases outvote a light prior; 4 cases do not",
                "The 95% credible interval and median of VE for beta priors of growing weight, centred at the trial's mean and "
                "at no effect.", "how much does the prior matter?", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "three 'uninformative' priors for θ, drawn on θ and on the log-odds, log(θ/(1 - θ)) = log IRR when r = 1")
    ax = Axes(96, 96, 380, 300, (0, 1), (0, 3))
    s += ax.clip("c9a") + title(ax.x0, ax.y0 - 16, "(a) on θ")
    s += ax.frame([0, 0.25, 0.5, 0.75, 1.0], [0, 1, 2, 3], xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: f"{v:.0f}", xlab="θ")
    xs = lin(0.002, 0.998, 500)
    inner = polyline(curve(ax, xs, [1.0 for _ in xs]), INK, sw=1.8)
    inner += polyline(curve(ax, xs, [beta_pdf(x, 0.5, 0.5) for x in xs]), LINK, sw=1.8)
    inner += polyline(curve(ax, xs, [beta_pdf(x, A0, B0) for x in xs]), ACCENT, sw=1.8)
    s += f'<g clip-path="url(#c9a)">{inner}</g>'
    ind = PR["induced"]
    bx = Axes(596, 96, 380, 300, (-8, 8), (0, 0.30))
    s += bx.clip("c9b") + title(bx.x0, bx.y0 - 16, "(b) the same priors on the log-odds")
    s += bx.frame([-8, -4, 0, 4, 8], [0, 0.1, 0.2, 0.3], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:.1f}", xlab="log-odds of θ (top: VE, r = 1)")
    inner = polyline(curve(bx, ind["phi"], ind["uniform"]), INK, sw=1.8)
    inner += polyline(curve(bx, ind["phi"], ind["jeffreys"]), LINK, sw=1.8)
    inner += polyline(curve(bx, ind["phi"], ind["trial"]), ACCENT, sw=1.8)
    inner += line(bx.x0, bx.Y(0.27), bx.x0 + bx.w, bx.Y(0.27), stroke=MUTED, sw=1.2, dash="5,3")
    s += f'<g clip-path="url(#c9b)">{inner}</g>'
    for phi_, lab in ((-math.log(100), "99%"), (-math.log(10), "90%"), (0, "0%"), (math.log(10), "−900%")):
        s += mono(bx.X(phi_), bx.y0 - 2, lab, size=7.5, fill=SOFT)
    s += mono(bx.X(-7.6), bx.Y(0.27) - 6, "Haldane, beta(0, 0): flat here, improper (height arbitrary)", size=8, fill=MUTED, anchor="start")
    pu = PP["uniform"]
    s += note_lines(bx.X(2.2), bx.Y(0.235), [("uniform on θ:", INK), (f"P(VE < 0) = {pu['p_ve_lt_0']:.2f}", INK),
                                             (f"P(VE > 90%) = {pu['p_ve_gt_90']:.4f}", INK)], gap=14)
    s += legend(vh - 24, vw, [("uniform, beta(1, 1)", "line:" + INK + ":1.8"), ("Jeffreys, beta(1/2, 1/2)", "line:" + LINK + ":1.8"),
                              ("the trial's beta(0.700102, 1)", "line:" + ACCENT + ":1.8"), ("Haldane, beta(0, 0)", "dash:" + MUTED + ":1.2")])
    return emit("09", "flat-depends-on-the-scale", "Flat on θ is a hill on the log-odds",
                "The uniform, Jeffreys and trial priors as densities of θ and of its log-odds. Only one of them can be flat on "
                "a given scale.", "how much does the prior matter?", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 540
    s = eyebrow(32, 40, "H0: a birth is a boy with probability 1/2. Each Paris year 1771-1784 alone: exact p-value and Bayes factor")
    ax = Axes(110, 96, 620, 330, (1e-9, 1.0), (1e-6, 300), xmap=log10, ymap=log10)
    s += ax.clip("c10") + title(ax.x0, ax.y0 - 16, "BF01, the data's support for x = 1/2 against a uniform x, by year")
    s += ax.frame([1e-9, 1e-7, 1e-5, 1e-3, 0.05, 1.0], [1e-6, 1e-4, 1e-2, 1, 100], xfmt=lambda v: {0.05: "0.05", 1.0: "1"}.get(v, f"1e{int(round(math.log10(v)))}"),
                  yfmt=lambda v: {1: "1", 100: "100"}.get(v, f"1e{int(round(math.log10(v)))}"), xlab="two-sided exact p-value (log)", ylab="BF01 (log)")
    s += rect(ax.x0 + 0.5, ax.y0 + 0.5, ax.X(0.05) - ax.x0, ax.Y(1) - ax.y0, fill=ACCENT, op=0.07, stroke="none", sw=0)
    s += line(ax.X(0.05), ax.y0, ax.X(0.05), ax.y0 + ax.h, stroke=INK, sw=1.0, dash="4,3")
    s += line(ax.x0, ax.Y(1), ax.x0 + ax.w, ax.Y(1), stroke=INK, sw=1.0, dash="4,3")
    s += mono(ax.x0 + 8, ax.y0 + 16, "p < 0.05 and BF01 > 1: the two schools disagree", size=8.5, fill=ACCENT, anchor="start", weight="600")
    offsets = {"1772": (8, 19), "1779": (-7, -7), "1778": (7, 3), "1782": (-7, -7), "1774": (-8, 13), "1784": (-8, 4),
               "1776": (8, 4), "1780": None}
    assert abs(math.log10(LI["years"]["1776"]["p_exact"] / LI["years"]["1780"]["p_exact"])) < 0.1
    for yr, v in LI["years"].items():
        col = ACCENT if yr in LI["lindley_years"] else INK
        x, y = ax.X(v["p_exact"]), ax.Y(v["bf01"])
        s += dot(x, y, 3.6, fill=col)
        off = offsets.get(yr, (8, 4))
        if off is None:
            continue
        label = "1776, 1780" if yr == "1776" else yr
        s += mono(x + off[0], y + off[1], label, size=8, fill=col, anchor="start" if off[0] > 0 else "end", weight="600" if col == ACCENT else "400")
    y82 = LI["years"]["1782"]
    s += note_lines(760, 140, [("1782: 9,851 boys of 19,387", ACCENT), (f"z = {y82['z']:.3f}, p = {y82['p_exact']:.4f}", ACCENT),
                               (f"BF01 = {y82['bf01']:.2f}, P(H0 | data) = {y82['post_h0']:.3f}", ACCENT),
                               ("", MUTED), ("BF01 = 1 needs z ≈ 3.07 here:", MUTED), ("Jeffreys' sqrt(ln(2n/π))", MUTED),
                               ("", MUTED), ("pooled 1771-1784: z = 11.86,", INK), ("log10 BF01 = −27.9", INK)], gap=15)
    s += legend(vh - 24, vw, [("rejects at 5%, yet the data favour 1/2", "dot:" + ACCENT + ":3.6"), ("the two schools agree", "dot:" + INK + ":3.6"),
                              ("p = 0.05 and BF01 = 1", "dash:" + INK + ":1.0")])
    return emit("10", "lindley-paris-years", "Four years reject ½ at the 5% level while the data favour ½",
                "Each year of Paris baptisms, 1771 to 1784, tested alone against a boy probability of ½: the exact p-value "
                "against the Bayes factor for ½ over a uniform alternative.", "bayes factors and lindley's paradox", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "1782 alone: the Bayes factor depends on the alternative's prior, and at a fixed z it grows like √n")
    f = LI["focus"]
    ax = Axes(96, 96, 380, 300, (1e-3, 1e8), (0.05, 2000), xmap=log10, ymap=log10)
    s += ax.clip("c11a") + title(ax.x0, ax.y0 - 16, "(a) BF01 against the concentration κ of beta(κ/2, κ/2)")
    s += ax.frame([1e-3, 1, 1e3, 1e6], [0.1, 1, 10, 100, 1000], xfmt=lambda v: {1e-3: "0.001", 1: "1", 1e3: "1,000", 1e6: "10^6"}[v],
                  yfmt=lambda v: f"{v:g}", xlab="κ, the prior's worth in births (log)", ylab="BF01 (log)")
    inner = polyline(curve(ax, f["kappa"], f["bf01_beta_kappa"]), INK, sw=1.8)
    inner += line(ax.x0, ax.Y(f["bf01_minimum"]), ax.x0 + ax.w, ax.Y(f["bf01_minimum"]), stroke=ACCENT, sw=1.0, dash="4,3")
    inner += line(ax.x0, ax.Y(1), ax.x0 + ax.w, ax.Y(1), stroke=SOFT, sw=0.9, dash="2,3")
    s += f'<g clip-path="url(#c11a)">{inner}</g>'
    s += dot(ax.X(2), ax.Y(f["bf01_uniform"]), 3.6, fill=INK)
    s += mono(ax.X(2) + 7, ax.Y(f["bf01_uniform"]) - 6, f"uniform: {f['bf01_uniform']:.2f}", size=8, fill=INK, anchor="start", weight="600")
    s += dot(ax.X(493474), ax.Y(f["bf01_informed"]), 3.6, fill=LINK)
    s += mono(ax.X(493474) + 7, ax.Y(f["bf01_informed"]) - 7, f"1/{f['bf10_informed']:.2f}", size=8, fill=LINK, anchor="start", weight="600")
    s += mono(ax.x0 + 6, ax.Y(f["bf01_minimum"]) - 6, f"no prior can go below 1/{f['bf10_maximum']:.2f}", size=8, fill=ACCENT, anchor="start")
    s += note_lines(96, 446, [(f"(a) blue dot: H1's prior is the 1745-1770 posterior, beta(251,528, 241,946), centred at 0.5097 and worth "
                               f"493,474 births, not centred at 1/2: BF01 = 1/{f['bf10_informed']:.2f}", MUTED)], gap=15)
    bx = Axes(596, 96, 380, 300, (50, 1e8), (0.3, 2000), xmap=log10, ymap=log10)
    s += bx.clip("c11b") + title(bx.x0, bx.y0 - 16, "(b) BF01 against n at a fixed z, uniform alternative")
    s += bx.frame([100, 1e4, 1e6, 1e8], [1, 10, 100, 1000], xfmt=lambda v: {100: "100", 1e4: "10^4", 1e6: "10^6", 1e8: "10^8"}[v],
                  yfmt=lambda v: f"{v:g}", xlab="births, n (log)")
    inner = polyline(curve(bx, LI["growth_n"], LI["growth"]["z_1782"]), ACCENT, sw=1.9)
    inner += polyline(curve(bx, LI["growth_n"], LI["growth"]["z_1.96"]), LINK, sw=1.6, dash="5,3")
    inner += line(bx.x0, bx.Y(1), bx.x0 + bx.w, bx.Y(1), stroke=SOFT, sw=0.9, dash="2,3")
    inner += line(bx.x0, bx.Y(19), bx.x0 + bx.w, bx.Y(19), stroke=SOFT, sw=0.9, dash="2,3")
    s += f'<g clip-path="url(#c11b)">{inner}</g>'
    s += dot(bx.X(19387), bx.Y(f["bf01_uniform"]), 3.6, fill=ACCENT)
    s += mono(bx.X(19387) + 7, bx.Y(f["bf01_uniform"]) + 14, "1782", size=8, fill=ACCENT, anchor="start", weight="600")
    s += mono(bx.x0 + bx.w - 4, bx.Y(19) - 6, "P(H0) = 0.95 at even prior odds", size=8, fill=SOFT, anchor="end")
    s += mono(bx.x0 + bx.w - 4, bx.Y(1) - 6, "even evidence", size=8, fill=SOFT, anchor="end")
    c = LI["crossings"]["z_1782"]
    s += note_lines(bx.x0 + 8, bx.y0 + 20, [(f"z = {LI['years']['1782']['z']:.3f}: BF01 passes 1 at n = {c['bf_1']:,.0f}", ACCENT),
                                             (f"and 19 at n = {c['bf_19']:,.0f}", ACCENT)], gap=14)
    s += legend(vh - 24, vw, [("BF01, symmetric priors", "line:" + INK + ":1.8"), ("ceiling of the alternative (spike at the MLE)", "dash:" + ACCENT + ":1.0"),
                              ("z = 2.262 (1782)", "line:" + ACCENT + ":1.9"), ("z = 1.96", "dash:" + LINK + ":1.6")])
    return emit("11", "bayes-factor-prior-and-n", "The Bayes factor depends on the alternative's prior and on n",
                "For the 1782 baptisms, the Bayes factor for ½ under symmetric beta priors of growing concentration and under "
                "the 1745–1770 posterior; and, at a fixed z, against the number of births.", "bayes factors and lindley's paradox", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    for k in (sys.argv[1:] or sorted(FIGS)):
        FIGS[k]()
