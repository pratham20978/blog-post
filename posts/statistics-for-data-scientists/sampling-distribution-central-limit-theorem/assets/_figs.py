#!/usr/bin/env python3
"""Figures 01-10 for sampling-distribution-central-limit-theorem.

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/sampling.py.
The asserts below pin each number the article quotes, so a figure cannot drift from the text.
Run:  python3 _figs.py [01 05 ...]
"""
import json
import math
import pathlib
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SANS, SOFT,
                    emit, eyebrow, mono, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
P, SA, SK, ST, BE, HV, RP = (CAP[k] for k in ("population", "sampling", "skewness", "student", "berry", "heavy",
                                              "replications"))
BYN = SA["by_n"]
MU, SD, G = P["mean"], P["sd"], P["skewness"]

# The numbers the article prints, held to the capture.
assert P["N"] == 4317 and round(MU, 2) == 1925.71 and round(P["median"], 2) == 658.26 and round(SD, 2) == 8266.70
assert round(G, 1) == 21.6 and round(P["share_below_mean"], 3) == 0.791 and round(P["top1"]["share_of_spend"], 3) == 0.297
assert round(100 * BYN["30"]["lower"]["p"], 1) == 39.8 and round(100 * BYN["30"]["upper"]["p"], 2) == 0.05
assert round(100 * BYN["1000"]["lower"]["p"], 1) == 17.7 and round(100 * BYN["10000"]["lower"]["p"], 1) == 7.9
assert round(BE["spend"]["n_good"]) == 20652 and BE["spend"]["n_guaranteed"] == 1025322
assert round(ST["t"], 2) == 4.06 and round(100 * ST["p_abs_t9_beyond_z975"], 2) == 8.16


# ------------------------------------------------------------------ drawing helpers (Part 1's set)
def fmt(v, nd=1):
    v = float(v)
    s = f"{round(v):,}" if abs(v - round(v)) < 1e-9 else f"{v:,.{nd}f}"
    return s.replace("-", "−")


def sg(v, nd=2):
    return f"{float(v):.{nd}f}".replace("-", "−")


def gbp(v):
    return f"£{v:,.0f}"


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


MARKS = f"""<defs>
    <marker id="am" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
    <marker id="aa" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
  </defs>"""

BAR_FILL, BAR_OP, BAR_STROKE = LINK, 0.22, LINK      # simulated or observed bars: the same in every legend
TAIL_FILL, TAIL_OP = ACCENT, 0.20


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

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid_y=True, grid_x=False):
        s = ""
        for v in yt:
            yy = self.Y(v)
            if grid_y:
                s += line(self.x0, yy, self.x0 + self.w, yy, stroke=RULE, sw=0.8)
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


def marker(shape, x, y, r=3.4, fill=LINK, stroke=None, op=None):
    """Point marks for Figure 7: one shape per population."""
    o = f' fill-opacity="{op}"' if op is not None else ""
    st = f' stroke="{stroke}" stroke-width="1.2"' if stroke else ""
    if shape == "circle":
        return dot(x, y, r, fill=fill, stroke=stroke, op=op)
    if shape == "square":
        return f'<rect x="{x - r:.1f}" y="{y - r:.1f}" width="{2 * r:.1f}" height="{2 * r:.1f}" fill="{fill}"{o}{st}/>'
    pts = {"triangle": [(0, -1.25), (1.1, 0.75), (-1.1, 0.75)], "tdown": [(0, 1.25), (1.1, -0.75), (-1.1, -0.75)],
           "diamond": [(0, -1.3), (1.1, 0), (0, 1.3), (-1.1, 0)]}[shape]
    poly = " ".join(f"{x + a * r:.1f},{y + b * r:.1f}" for a, b in pts)
    return f'<polygon points="{poly}" fill="{fill}"{o}{st}/>'


def legend(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like this post's marks (colour, size, opacity, stroke)."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, kind in items:
        part = kind.split(":")
        if kind == "bar":
            s += rect(x, y - 1, 16, 12, fill=BAR_FILL, op=BAR_OP, stroke=BAR_STROKE, sw=1.0)
        elif kind == "barflat":
            s += rect(x, y - 1, 16, 12, fill=BAR_FILL, op=BAR_OP, stroke="none", sw=0)
        elif kind == "tail":
            s += rect(x, y - 1, 16, 12, fill=TAIL_FILL, op=TAIL_OP, stroke="none", sw=0)
        elif part[0] == "band":
            s += rect(x, y - 1, 16, 12, fill=part[1], op=float(part[2]), stroke="none", sw=0)
        elif part[0] == "line":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=2.0)
        elif part[0] == "linept":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.8) + dot(x + 9, y + 5, 3.0, fill=part[1])
        elif part[0] == "dash":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.4, dash="5,3")
        elif part[0] == "dashpt":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.4, dash="6,3") + dot(x + 9, y + 5, 3.0, fill=part[1])
        elif part[0] == "dotted":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.2, dash="2,3")
        elif part[0] == "dot":                       # dot:colour:radius:opacity
            s += dot(x + 8, y + 5, float(part[2]), fill=part[1], op=float(part[3]) if len(part) > 3 else None)
        elif part[0] == "ring":
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1])
        elif part[0] == "mk":                        # mk:shape:colour
            s += marker(part[1], x + 8, y + 5, 3.4, fill=part[2])
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 26
    return s


def normal_pdf(x):
    return math.exp(-x * x / 2) / math.sqrt(2 * math.pi)


def log_ticks(v):
    """1, 10, 100, ... as plain numbers with thousands separators."""
    return f"{v:,.0f}" if v >= 1 else f"{v:g}"


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 520
    s = MARKS + eyebrow(32, 40, "the population: 4,317 customers' net spend, december 2010 to december 2011")
    edges, counts = P["hist_log10_edges"], P["hist_counts"]
    ymax = max(counts) * 1.15
    ax = Axes(96, 104, 600, 290, (0.3, 5.6), (0, ymax))
    s += ax.clip("c1")
    s += title(ax.x0, ax.y0 - 28, "customers per tenth of a decade of spend, log scale")
    yt = [v for v in range(0, int(ymax) + 1, 50)]
    s += ax.frame([1, 2, 3, 4, 5], yt, ylab="customers", xfmt=lambda v: "£" + log_ticks(10 ** v), yfmt=str)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "net spend over the year, log scale", size=8.5, fill=SOFT, anchor="end")
    bars = "".join(rect(ax.X(edges[i]), ax.Y(c), ax.X(edges[i + 1]) - ax.X(edges[i]), ax.Y(0) - ax.Y(c),
                        fill=BAR_FILL, op=BAR_OP, stroke=BAR_STROKE, sw=0.6) for i, c in enumerate(counts) if c)
    s += f'<g clip-path="url(#c1)">{bars}</g>'
    lm, lmed = math.log10(MU), math.log10(P["median"])
    s += line(ax.X(lmed), ax.y0 + 18, ax.X(lmed), ax.y0 + ax.h, stroke=INK, sw=1.2, dash="4,3")
    s += line(ax.X(lm), ax.y0 + 18, ax.X(lm), ax.y0 + ax.h, stroke=ACCENT, sw=1.8)
    s += plate(ax.X(lmed) - 6, ax.y0 + 12, f"median {gbp(P['median'])}", size=8.5, fill=INK, anchor="end")
    s += plate(ax.X(lm) + 6, ax.y0 + 12, f"mean {gbp(MU)}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    top = P["top1"]
    floor = BYN["30"]["top1"]["floor"]            # the 43rd-largest spend: where the top 1% start
    xa, xb, yb = ax.X(math.log10(floor)), ax.X(math.log10(P["max"])), ax.Y(62)
    s += line(xa, yb, xb, yb, stroke=INK, sw=1.0) + line(xa, yb, xa, yb + 6, stroke=INK, sw=1.0)
    s += line(xb, yb, xb, yb + 6, stroke=INK, sw=1.0)
    s += mono((xa + xb) / 2, yb - 22, f"top 1%: {top['customers']} customers,", size=8.5, fill=INK, weight="600")
    s += mono((xa + xb) / 2, yb - 8, f"{top['share_of_spend']:.1%} of all spend", size=8.5, fill=INK)
    s += note_lines(740, 128, [("the shape behind every number", INK),
                               (f"{P['share_below_mean']:.1%} of customers spend", MUTED),
                               ("less than the mean", MUTED),
                               ("", MUTED),
                               (f"the top 1% start at {gbp(floor)}", INK),
                               (f"the top 10% hold {P['top10']['share_of_spend']:.1%}", MUTED),
                               ("of all spend", MUTED),
                               ("", MUTED),
                               (f"largest {gbp(P['max'])},", MUTED),
                               (f"{P['max_in_sds']:.1f} SDs above the mean", MUTED),
                               ("", MUTED),
                               (f"SD {gbp(SD)} (divisor N)", INK),
                               (f"skewness {G:.1f}", INK)], gap=16)
    s += note_lines(96, 446, [(f"net spend: every invoice line with a customer ID, cancellations included; the "
                               f"{P['N']:,} customers with a positive total", MUTED)])
    s += legend(vh - 30, vw, [("customers", "bar"), ("median", "dash:" + INK), ("mean", "line:" + ACCENT)])
    return emit("01", "population", "Net spend per customer, UCI Online Retail",
                "The population every sample in this post is drawn from: 4,317 customers' net spend, binned on a "
                "log scale by the lab.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 640
    s = MARKS + eyebrow(32, 40, "the sampling distribution of the mean, in standard errors, for four sample sizes")
    for k, n in enumerate(("10", "30", "100", "1000")):
        r = BYN[n]
        edges, counts = r["hist_z_edges"], r["hist_z_counts"]
        reps = r["R"]
        dens = [c / (reps * (edges[i + 1] - edges[i])) for i, c in enumerate(counts)]
        lo_i, hi_i = edges.index(-3.0), edges.index(6.0)
        ymax = max(max(dens[lo_i:hi_i]), 0.4) * 1.12
        col, row = k % 2, k // 2
        ax = Axes(96 + col * 484, 104 + row * 230, 380, 150, (-3, 6), (0, ymax))
        cid = f"c2{k}"
        s += ax.clip(cid)
        s += title(ax.x0, ax.y0 - 28, f"n = {int(n):,}: standard error {gbp(r['se_theory'])}")
        yt = [v / 10 for v in range(0, int(ymax * 10) + 1, 2 if ymax < 1 else 5)]
        s += ax.frame([-2, 0, 2, 4, 6], yt, ylab="density" if col == 0 else None, xfmt=lambda v: fmt(v),
                      yfmt=lambda v: f"{v:g}")
        bars = "".join(rect(ax.X(edges[i]), ax.Y(d), ax.X(edges[i + 1]) - ax.X(edges[i]), ax.Y(0) - ax.Y(d),
                            fill=BAR_FILL, op=BAR_OP, stroke="none", sw=0) for i, d in enumerate(dens)
                       if lo_i <= i < hi_i and d > 0)
        xs = [-3 + 9 * i / 300 for i in range(301)]
        curve = polyline([(ax.X(x), ax.Y(normal_pdf(x))) for x in xs], INK, sw=1.6)
        s += f'<g clip-path="url(#{cid})">{bars}{curve}</g>'
        s += line(ax.X(0), ax.y0, ax.X(0), ax.y0 + ax.h, stroke=ACCENT, sw=1.2, dash="4,3")
        beyond = sum(counts[hi_i:]) + r["hist_z_above"]
        s += note_lines(ax.x0 + ax.w - 4, ax.y0 + 14, [
            (f"skewness {r['skew_exact']:.2f}", INK),
            (f"{r['p_mean_below_mu']['p']:.1%} of means below μ", ACCENT),
            (f"{beyond / reps:.1%} beyond +6", MUTED)], anchor="end", gap=14)
    s += mono(96 + 380, 104 + 230 + 150 + 32, "sample mean − μ, in standard errors", size=8.5, fill=SOFT, anchor="end")
    s += mono(580 + 380, 104 + 230 + 150 + 32, "sample mean − μ, in standard errors", size=8.5, fill=SOFT, anchor="end")
    s += note_lines(96, 568, [(f"R = {BYN['30']['R']:,} samples per n, drawn with replacement; skewness of the mean is "
                               f"exactly {G:.2f}/√n, and the simulated values match it within their Monte Carlo error",
                               MUTED)])
    s += legend(vh - 30, vw, [("simulated sample means", "barflat"), ("standard normal", "line:" + INK),
                              ("the true mean μ", "dash:" + ACCENT)])
    return emit("02", "sampling-distributions", "The sampling distribution of the mean",
                f"Means of samples of 10, 30, 100 and 1,000 customers, R = {BYN['30']['R']:,} each, standardised by "
                "their true standard error; the normal curve is what the CLT promises in the limit.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 548
    s = MARKS + eyebrow(32, 40, "the standard deviation describes customers; the standard error describes means")
    lg = math.log10
    ax = Axes(110, 104, 560, 300, (6, 16000), (40, 30000), xmap=lg, ymap=lg)
    s += ax.clip("c3")
    s += title(ax.x0, ax.y0 - 28, "spread in pounds, against sample size n, log–log")
    s += ax.frame([10, 30, 100, 300, 1000, 3000, 10000], [100, 300, 1000, 3000, 10000, 30000], ylab="£",
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{v:,}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "sample size n", size=8.5, fill=SOFT, anchor="end")
    ns = [int(n) for n in BYN]
    band_hi = [(ax.X(n), ax.Y(BYN[str(n)]["s_over_sigma_quantiles"]["q90"] * SD / math.sqrt(n))) for n in ns]
    band_lo = [(ax.X(n), ax.Y(BYN[str(n)]["s_over_sigma_quantiles"]["q10"] * SD / math.sqrt(n))) for n in ns]
    med = [(ax.X(n), ax.Y(BYN[str(n)]["s_over_sigma_quantiles"]["q50"] * SD / math.sqrt(n))) for n in ns]
    body = area(band_hi + band_lo[::-1], ACCENT, 0.14)
    body += polyline(med, ACCENT, sw=1.8)
    body += line(ax.X(6), ax.Y(SD), ax.X(16000), ax.Y(SD), stroke=INK, sw=1.6, dash="6,3")
    body += polyline([(ax.X(n), ax.Y(SD / math.sqrt(n))) for n in (6, 16000)], INK, sw=1.8)
    body += "".join(dot(ax.X(n), ax.Y(BYN[str(n)]["se_sim"]), 3.6, fill=LINK) for n in ns)
    s += f'<g clip-path="url(#c3)">{body}</g>'
    s += mono(ax.X(1500), ax.Y(SD) + 18, f"σ = {gbp(SD)}: the SD of one customer's spend", size=8.5, fill=INK)
    r30 = BYN["30"]
    se30, est30 = r30["se_theory"], r30["s_over_sigma_quantiles"]["q50"] * SD / math.sqrt(30)
    s += note_lines(700, 150, [("at n = 30", INK),
                               (f"true standard error σ/√30 = {gbp(se30)}", INK),
                               (f"simulated SD of the means {gbp(r30['se_sim'])}", LINK),
                               (f"typical estimate s/√30 = {gbp(est30)}", ACCENT),
                               (f"s < σ in {r30['p_s_below_sigma']['p']:.1%} of samples,", MUTED),
                               (f"yet s²/σ² averages {r30['mean_s2_over_sigma2']:.3f}", MUTED),
                               (f"± {r30['mean_s2_over_sigma2_mcse']:.3f} (unbiased)", MUTED)], gap=16)
    s += note_lines(700, 300, [("the band: 10th to 90th percentile", MUTED), ("of s/√n over the samples", MUTED)], gap=15)
    s += note_lines(110, 470, [(f"R = {r30['R']:,} samples per n; the simulated SD of the means sits on σ/√n "
                                "at every n, within its Monte Carlo error", MUTED)])
    s += legend(vh - 30, vw, [("σ", "dash:" + INK), ("σ/√n", "line:" + INK), ("simulated SD of means", f"dot:{LINK}:3.6"),
                              ("median s/√n", "line:" + ACCENT), ("10–90% of s/√n", f"band:{ACCENT}:0.14")])
    return emit("03", "sd-and-se", "Standard deviation, standard error, and its estimate",
                f"The population SD, the true standard error and its estimate s/√n from the lab's samples "
                f"(R = {r30['R']:,} per n).", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 540
    s = MARKS + eyebrow(32, 40, "a nominal 5% t-test of the true mean, run on samples of real spend")
    lg = math.log10
    ax = Axes(110, 104, 560, 300, (7, 14000), (0, 45), xmap=lg)
    s += ax.clip("c4")
    s += title(ax.x0, ax.y0 - 28, "share of samples in which the test rejects μ, which is true")
    s += ax.frame([10, 30, 100, 300, 1000, 3000, 10000], [0, 5, 10, 20, 30, 40], ylab="rejections, %",
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{v:g}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "sample size n, log scale", size=8.5, fill=SOFT, anchor="end")
    ns = [int(n) for n in BYN]
    body = line(ax.X(7), ax.Y(5), ax.X(14000), ax.Y(5), stroke=MUTED, sw=1.2, dash="2,3")
    for key, col, sw, dash in (("two_sided", INK, 1.4, "6,3"), ("upper", LINK, 1.8, None), ("lower", ACCENT, 2.2, None)):
        pts = [(ax.X(n), ax.Y(100 * BYN[str(n)][key]["p"])) for n in ns]
        body += polyline(pts, col, sw=sw, dash=dash)
        for n, (x, y) in zip(ns, pts):
            e = 200 * BYN[str(n)][key]["mcse"]
            body += line(x, ax.Y(100 * BYN[str(n)][key]["p"] - e), x, ax.Y(100 * BYN[str(n)][key]["p"] + e), stroke=col, sw=1.0)
            body += dot(x, y, 3.0, fill=col)
    s += f'<g clip-path="url(#c4)">{body}</g>'
    s += plate(ax.X(8.5), ax.Y(5) - 6, "nominal 5%", size=8, fill=MUTED, anchor="start")
    b30, b1k, b10k = BYN["30"], BYN["1000"], BYN["10000"]
    s += plate(ax.X(30) + 8, ax.Y(100 * b30["lower"]["p"]) - 10, f"{100 * b30['lower']['p']:.1f}%", size=8.5, fill=ACCENT,
               anchor="start", weight="600")
    s += plate(ax.X(1000) + 8, ax.Y(100 * b1k["lower"]["p"]) - 10, f"{100 * b1k['lower']['p']:.1f}%", size=8.5,
               fill=ACCENT, anchor="start", weight="600")
    s += note_lines(700, 150, [("one-sided tests at 5% each", INK),
                               ("lower: rejects when t ≤ −t₀.₉₅", ACCENT),
                               ("upper: rejects when t ≥ t₀.₉₅", LINK),
                               ("two-sided 5%: |t| ≥ t₀.₉₇₅", INK),
                               ("", MUTED),
                               (f"n = 30: lower {100 * b30['lower']['p']:.1f}%, upper {100 * b30['upper']['p']:.2f}%", MUTED),
                               (f"n = 1,000: lower {100 * b1k['lower']['p']:.1f}%, upper {100 * b1k['upper']['p']:.2f}%", MUTED),
                               (f"n = 10,000: lower {100 * b10k['lower']['p']:.2f}%, upper {100 * b10k['upper']['p']:.2f}%,", MUTED),
                               (f"two-sided {100 * b10k['two_sided']['p']:.2f}%", MUTED)], gap=16)
    s += note_lines(110, 470, [(f"R = {b30['R']:,} samples per n; bars are ±2 MCSE and mostly hide inside the dots", MUTED)])
    s += legend(vh - 30, vw, [("lower tail", "linept:" + ACCENT), ("upper tail", "linept:" + LINK),
                              ("two-sided", "dashpt:" + INK), ("nominal 5%", "dotted:" + MUTED)])
    return emit("04", "t-test-tails", "The t-test's two tails on real spend",
                f"One-sided and two-sided error rates of a nominal 5% t-test of the true mean, measured by the lab "
                f"with R = {b30['R']:,} samples per n.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 560
    s = MARKS + eyebrow(32, 40, "why one tail fires: a sample's mean and its standard deviation fall together")
    r = BYN["30"]
    xb, sd_s, t95, tp = r["scatter_mean"], r["scatter_sd"], r["t95"], r["top1"]
    lg = math.log10
    ax = Axes(110, 104, 560, 320, (150, 30000), (60, 60000), xmap=lg, ymap=lg)
    s += ax.clip("c5")
    s += title(ax.x0, ax.y0 - 28, "3,000 samples of 30 customers: sample mean against sample SD, log–log")
    s += ax.frame([300, 1000, 3000, 10000, 30000], [100, 1000, 10000], ylab="sample SD s, £",
                  xfmt=lambda v: f"£{v:,}", yfmt=lambda v: f"£{v:,}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "sample mean, £", size=8.5, fill=SOFT, anchor="end")
    rej = [(m, v) for m, v in zip(xb, sd_s) if (m - MU) / (v / math.sqrt(30)) <= -t95]
    keep = [(m, v) for m, v in zip(xb, sd_s) if (m - MU) / (v / math.sqrt(30)) > -t95]
    body = "".join(dot(ax.X(m), ax.Y(v), 1.9, fill=LINK, op=0.45) for m, v in keep)
    body += "".join(dot(ax.X(m), ax.Y(v), 1.9, fill=ACCENT, op=0.75) for m, v in rej)
    bnd = []
    for i in range(200):
        m = 150 * (MU / 150) ** (i / 199)
        if m < MU * 0.9999:
            bnd.append((ax.X(m), ax.Y((MU - m) * math.sqrt(30) / t95)))
    body += polyline(bnd, INK, sw=1.4)
    body += line(ax.X(MU), ax.y0, ax.X(MU), ax.y0 + ax.h, stroke=INK, sw=1.0, dash="4,3")
    s += f'<g clip-path="url(#c5)">{body}</g>'
    s += plate(ax.X(MU) + 6, ax.y0 + 14, f"true mean μ = {gbp(MU)}", size=8.5, fill=INK, anchor="start")
    s += note_lines(ax.X(165), ax.Y(240), [("below the curve:", INK), ("t ≤ −1.70, rejected", INK)], size=8.5, gap=14)
    none = 1 - tp["p_sample_has_one"]["p"]
    s += note_lines(700, 150, [(f"{none:.1%} of samples hold none of", ACCENT),
                               ("the 43 biggest customers:", ACCENT),
                               (f"mean below μ in {tp['p_below_mu_given_none']['p']:.1%},", MUTED),
                               ("and a small s from the same", MUTED),
                               ("small values, so t is far negative:", MUTED),
                               (f"{tp['lower_given_none']['p']:.1%} rejected", ACCENT),
                               ("", MUTED),
                               (f"{tp['p_sample_has_one']['p']:.1%} hold one, which lifts the mean", LINK),
                               ("and inflates s even more, so t stays", MUTED),
                               (f"small: {int(tp['lower_given_one']['p'] * tp['lower_given_one']['R'])} of "
                                f"{tp['lower_given_one']['R']:,} rejected", LINK),
                               ("", MUTED),
                               (f"the upper test fires in {100 * r['upper']['p']:.2f}%", MUTED),
                               ("of all samples", MUTED)], gap=16)
    s += note_lines(110, 486, [(f"correlation of mean and s over R = {r['R']:,} samples: {r['corr_mean_sd']:.3f}; "
                                f"the 43 biggest customers each spent at least {gbp(tp['floor'])}", MUTED)])
    s += legend(vh - 30, vw, [("rejected by the lower-tail test", f"dot:{ACCENT}:1.9:0.75"),
                              ("not rejected", f"dot:{LINK}:1.9:0.45"),
                              ("rejection boundary", "line:" + INK), ("true mean", "dash:" + INK)])
    return emit("05", "mean-and-sd-move-together", "The mean and the SD move together",
                "3,000 of the lab's samples of 30 customers; the curve is where the one-sided t statistic equals "
                "its 5% critical value.", "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 540
    s = MARKS + eyebrow(32, 40, "student's correction: the sleep data, and t with 9 degrees of freedom against z")
    d = ST["differences"]
    ax = Axes(96, 104, 330, 290, (-0.5, 5.0), (0, 1))
    s += title(ax.x0, ax.y0 - 28, "10 patients: extra hours of sleep, drug 2 minus drug 1")
    s += ax.frame([0, 1, 2, 3, 4, 5], [], xfmt=lambda v: f"{v:g}", grid_y=False)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "hours", size=8.5, fill=SOFT, anchor="end")
    seen = {}
    for v in d:
        k = seen.get(v, 0)
        seen[v] = k + 1
        s += dot(ax.X(v), ax.Y(0.12 + 0.09 * k), 5.0, fill=LINK, op=0.85)
    se = ST["sd_n_minus_1"] / math.sqrt(ST["n"])
    ym = ax.Y(0.62)
    s += line(ax.X(ST["mean"] - se), ym, ax.X(ST["mean"] + se), ym, stroke=INK, sw=1.6)
    s += dot(ax.X(ST["mean"]), ym, 4.6, fill=INK)
    s += plate(ax.X(ST["mean"]), ym - 14, f"mean {ST['mean']:.2f} ± SE {se:.2f}", size=8.5, fill=INK)
    s += line(ax.X(0), ax.y0, ax.X(0), ax.y0 + ax.h, stroke=MUTED, sw=1.0, dash="4,3")
    s += note_lines(ax.x0, ax.y0 + ax.h + 58, [
        (f"s = {ST['sd_n_minus_1']:.3f} (divisor n − 1); Student's s.d. {ST['sd_n']:.3f} (divisor n)", MUTED),
        (f"t = {ST['mean']:.2f} / ({ST['sd_n_minus_1']:.3f}/√10) = {ST['t']:.2f}", INK),
        (f"one-sided P = {ST['p_one_sided']:.5f}, odds {ST['odds']:.0f} to 1", MUTED)])
    bx = Axes(560, 104, 400, 290, (-5, 5), (0, 0.43))
    s += bx.clip("c6")
    s += title(bx.x0, bx.y0 - 28, "the reference distribution for t with n = 10")
    s += bx.frame([-4, -2, 0, 2, 4], [0, 0.1, 0.2, 0.3, 0.4], ylab="density", xfmt=lambda v: fmt(v),
                  yfmt=lambda v: f"{v:g}")
    s += mono(bx.x0 + bx.w, bx.y0 + bx.h + 32, "t", size=8.5, fill=SOFT, anchor="end")
    xs, t9, nz = ST["density_x"], ST["density_t9"], ST["density_normal"]
    z975 = ST["z975"]
    left = [(bx.X(x), bx.Y(y)) for x, y in zip(xs, t9) if x <= -z975]
    right = [(bx.X(x), bx.Y(y)) for x, y in zip(xs, t9) if x >= z975]
    body = area([(bx.X(-5), bx.Y(0))] + left + [(left[-1][0], bx.Y(0))], ACCENT, 0.22)
    body += area([(right[0][0], bx.Y(0))] + right + [(bx.X(5), bx.Y(0))], ACCENT, 0.22)
    body += polyline([(bx.X(x), bx.Y(y)) for x, y in zip(xs, nz)], INK, sw=1.8)
    body += polyline([(bx.X(x), bx.Y(y)) for x, y in zip(xs, t9)], LINK, sw=2.0)
    s += f'<g clip-path="url(#c6)">{body}</g>'
    for c, col in ((z975, INK), (ST["t975"], LINK)):
        for sign in (-1, 1):
            s += line(bx.X(sign * c), bx.y0 + 44, bx.X(sign * c), bx.y0 + bx.h, stroke=col, sw=1.0, dash="3,3")
    s += mono(bx.X(ST["t975"]) + 6, bx.y0 + 14, f"±{z975:.3f} normal cutoff", size=8, fill=INK, anchor="start")
    s += mono(bx.X(ST["t975"]) + 6, bx.y0 + 30, f"±{ST['t975']:.3f} t₉ cutoff", size=8, fill=LINK, anchor="start")
    s += mono(bx.x0 + bx.w - 2, bx.Y(0.05), f"sleep data: t = {ST['t']:.2f}", size=8.5, fill=INK, anchor="end")
    s += line(bx.X(ST["t"]), bx.Y(0.05) + 4, bx.X(ST["t"]), bx.Y(0) - 6, stroke=INK, sw=0.8)
    s += dot(bx.X(ST["t"]), bx.Y(0), 3.6, fill=INK)
    sim = ST["sim_normal_n10"]
    s += note_lines(bx.x0, bx.y0 + bx.h + 58, [
        (f"shaded: P(|T₉| ≥ {z975:.2f}) = {100 * ST['p_abs_t9_beyond_z975']:.2f}%, not 5%", ACCENT),
        (f"normal data, n = 10: the 1.96 cutoff rejects {100 * sim['z_with_s']['p']:.2f}% ± {100 * sim['z_with_s']['mcse']:.2f},", MUTED),
        (f"the t cutoff {100 * sim['t']['p']:.2f}% ± {100 * sim['t']['mcse']:.2f} (R = {sim['t']['R']:,})", MUTED)])
    s += legend(vh - 30, vw, [("patients", f"dot:{LINK}:5.0:0.85"), ("Student's t, 9 df", "line:" + LINK),
                              ("standard normal", "line:" + INK),
                              (f"t₉ beyond ±1.96: {100 * ST['p_abs_t9_beyond_z975']:.2f}%", "tail")])
    return emit("06", "student-t", "Student's correction for an estimated σ",
                "Cushny and Peebles' patients as Student printed them in 1908, and exact t and normal densities; "
                "the simulated rates come from the lab.", "student's t", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
SERIES = [("normal", "normal", "ring"), ("t5_unit_variance", "unit-variance t₅", "ring"),
          ("poisson_clarke", "Poisson, Clarke's rate", "circle"), ("exponential", "exponential", "square"),
          ("negbin_greenwood_yule", "neg. binomial, Greenwood–Yule", "triangle"),
          ("lognormal_product", "12 effects multiplied", "diamond"), ("lognormal_sigma1", "standard lognormal", "tdown")]


def fig07():
    vw, vh = 1016, 560
    s = MARKS + eyebrow(32, 40, "skewness over √n sets the t-test's tail error, whatever the population")
    c = SK["edgeworth_coefficient"]
    ax = Axes(110, 104, 520, 320, (0, 1.0), (-1, 14))
    s += ax.clip("c7")
    s += title(ax.x0, ax.y0 - 28, "lower-tail rejections minus the nominal 5%, in points")
    s += ax.frame([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 2, 4, 6, 8, 10, 12, 14], ylab="excess, percentage points",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "population skewness γ divided by √n", size=8.5, fill=SOFT, anchor="end")
    body = line(ax.X(0), ax.Y(0), ax.X(1.0), ax.Y(0), stroke=RULE_SOLID, sw=1.0)
    body += polyline([(ax.X(0), ax.Y(0)), (ax.X(1.0), ax.Y(100 * c))], INK, sw=1.4, dash="6,4")
    for key, label, shape in SERIES:
        pop = SK["populations"][key]
        pts = sorted((pop["skewness"] / math.sqrt(int(n)), 100 * (pop["by_n"][n]["lower"]["p"] - 0.05))
                     for n in ("30", "100", "300", "1000") if pop["skewness"] / math.sqrt(int(n)) <= 1.0)
        if shape == "ring":
            body += "".join(dot(ax.X(x), ax.Y(y), 3.2, fill=PAPER, stroke=INK) for x, y in pts)
            continue
        body += polyline([(ax.X(x), ax.Y(y)) for x, y in pts], LINK, sw=1.0, op=0.45)
        body += "".join(marker(shape, ax.X(x), ax.Y(y), 3.6, fill=LINK) for x, y in pts)
    sp = sorted((G / math.sqrt(int(n)), 100 * (BYN[n]["lower"]["p"] - 0.05)) for n in ("1000", "3000", "10000"))
    body += polyline([(ax.X(x), ax.Y(y)) for x, y in sp], ACCENT, sw=1.6)
    body += "".join(dot(ax.X(x), ax.Y(y), 3.8, fill=ACCENT) for x, y in sp)
    s += f'<g clip-path="url(#c7)">{body}</g>'
    s += mono(ax.X(sp[-1][0]) + 8, ax.Y(sp[-1][1]) + 4, "n = 1,000", size=8, fill=ACCENT, anchor="start")
    s += mono(ax.X(sp[0][0]) - 8, ax.Y(sp[0][1]) - 12, "n = 10,000", size=8, fill=ACCENT, anchor="end")
    # The key: marker, population, skewness, and the n = 30 tails.
    y = 150
    s += mono(668, y, "population", size=8, fill=SOFT, anchor="start")
    s += mono(880, y, "γ", size=8, fill=SOFT, anchor="end")
    s += mono(1000, y, "n = 30: lower / upper %", size=8, fill=SOFT, anchor="end")
    for key, label, shape in SERIES + [("spend", "customer spend", "spend")]:
        y += 22
        if key == "spend":
            g, lo, hi, col = G, BYN["30"]["lower"]["p"], BYN["30"]["upper"]["p"], ACCENT
            s += dot(674, y - 3, 3.8, fill=ACCENT)
        else:
            pop = SK["populations"][key]
            g, lo, hi, col = pop["skewness"], pop["by_n"]["30"]["lower"]["p"], pop["by_n"]["30"]["upper"]["p"], INK
            s += (dot(674, y - 3, 3.2, fill=PAPER, stroke=INK) if shape == "ring"
                  else marker(shape, 674, y - 3, 3.6, fill=LINK))
        s += mono(686, y, label, size=8, fill=col, anchor="start", weight="600" if key == "spend" else "400")
        s += mono(880, y, f"{g:.2f}", size=8, fill=col, anchor="end")
        s += mono(1000, y, f"{100 * lo:.2f} / {100 * hi:.2f}", size=8, fill=col, anchor="end")
    ratios = [(BYN[n]["lower"]["p"] - 0.05) / (c * G / math.sqrt(int(n))) for n in ("1000", "3000", "10000")]
    s += note_lines(668, y + 36, [("from n = 30, the five skewed populations", MUTED), ("sit within 20% of the first-order rule;", MUTED),
                                  (f"the spend, excess kurtosis {P['excess_kurtosis']:.0f}, runs", ACCENT),
                                  (f"{100 * (min(ratios) - 1):.0f}% to {100 * (max(ratios) - 1):.0f}% above it", ACCENT)],
                    size=8, gap=14)
    s += note_lines(110, 486, [(f"R = {SK['R']:,} tests per point, at n = 30, 100, 300 and 1,000 (customer spend: n = 1,000 "
                                "to 10,000); points beyond γ/√n = 1 are off the plot", MUTED)])
    s += legend(vh - 30, vw, [("customer spend", f"dot:{ACCENT}:3.8"), ("skewness 0", "ring:" + INK + ":3.2"),
                              (f"first-order Edgeworth term, {100 * c:.2f} γ/√n", "dash:" + INK)])
    return emit("07", "skewness-sets-the-pace", "Skewness over √n sets the error",
                f"Lower-tail error of a one-sided 5% t-test for seven populations and the spend data, R = {SK['R']:,} "
                "each, against the first-order Edgeworth term.", "how fast", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 560
    s = MARKS + eyebrow(32, 40, "berry–esseen guarantees the normal approximation; the exact distance arrives far sooner")
    lg = math.log10
    ax = Axes(110, 104, 560, 320, (10, 2e6), (2e-4, 2), xmap=lg, ymap=lg)
    s += ax.clip("c8")
    s += title(ax.x0, ax.y0 - 28, "largest gap between the standardised mean's CDF and the normal's")
    s += ax.frame([10, 100, 1000, 1e4, 1e5, 1e6], [1e-3, 1e-2, 1e-1, 1],
                  xfmt=lambda v: {10: "10", 100: "100", 1000: "1,000", 1e4: "10,000", 1e5: "100,000", 1e6: "1,000,000"}[v],
                  yfmt=lambda v: f"{v:g}", ylab="Kolmogorov distance, log scale")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "sample size n, log scale", size=8.5, fill=SOFT, anchor="end")
    body = line(ax.X(10), ax.Y(0.01), ax.X(2e6), ax.Y(0.01), stroke=MUTED, sw=1.2, dash="2,3")
    for key, col in (("spend", ACCENT), ("exponential", LINK)):
        rec = BE[key]
        ns = sorted(int(n) for n in rec["by_n"])
        body += polyline([(ax.X(n), ax.Y(rec["by_n"][str(n)]["exact"])) for n in ns], col, sw=2.0)
        body += polyline([(ax.X(n), ax.Y(BE["C0_upper"] * rec["beta3"] / math.sqrt(n))) for n in (10, 2e6)],
                         col, sw=1.4, dash="6,4")
    sims = [(int(n), r["ks_sim"]) for n, r in BYN.items()]
    body += "".join(marker("diamond", ax.X(n), ax.Y(v), 3.4, fill=INK) for n, v in sims)
    for key, col in (("spend", ACCENT), ("exponential", LINK)):
        rec = BE[key]
        body += dot(ax.X(rec["n_good"]), ax.Y(0.01), 4.4, fill=col)
        body += dot(ax.X(rec["n_guaranteed"]), ax.Y(0.01), 4.4, fill=PAPER, stroke=col)
    s += f'<g clip-path="url(#c8)">{body}</g>'
    sp, ex = BE["spend"], BE["exponential"]
    s += mono(ax.X(12), ax.Y(0.01) - 6, "0.01", size=8, fill=MUTED, anchor="start")
    s += note_lines(700, 150, [("distance reaches 0.01 at n =", INK),
                               (f"spend: {sp['n_good']:,} exact (filled dot),", ACCENT),
                               (f"{sp['n_guaranteed']:,} guaranteed (hollow)", ACCENT),
                               (f"exponential: {ex['n_good']:,} exact,", LINK),
                               (f"{ex['n_guaranteed']:,} guaranteed", LINK),
                               ("", MUTED),
                               (f"bound: {BE['C0_upper']} × β₃ / √n", MUTED),
                               (f"β₃ = {sp['beta3']:.2f} (spend), {ex['beta3']:.2f} (exp.)", MUTED),
                               ("a bound above 1 says nothing", MUTED)], gap=16)
    s += note_lines(110, 486, [("exact: by inverting the characteristic function (spend) and from the gamma CDF "
                                "(exponential); diamonds: the lab's simulated samples of spend", MUTED)])
    s += legend(vh - 30, vw, [("exact", "line:" + INK), ("Berry–Esseen bound", "dash:" + INK),
                              ("simulated, spend", "mk:diamond:" + INK), ("spend", "line:" + ACCENT),
                              ("exponential", "line:" + LINK)])
    return emit("08", "berry-esseen", "Guaranteed against good enough",
                "Exact Kolmogorov distances computed by the lab, against the Berry–Esseen bound with the best proven "
                f"constant {BE['C0_upper']}.", "berry–esseen", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 520
    s = MARKS + eyebrow(32, 40, "infinite variance: the condition the central limit theorem needs, broken")
    lg = math.log10
    cps = HV["checkpoints"]
    cols = (MUTED, MUTED, MUTED)                 # three seeded runs, one neutral colour: colour means a population here
    a = Axes(84, 104, 260, 260, (1, 1e6), (-6, 6), xmap=lg)
    s += a.clip("c9a")
    s += title(a.x0, a.y0 - 28, "Cauchy: running mean, 3 runs")
    s += a.frame([1, 100, 1e4, 1e6], [-6, -3, 0, 3, 6], xfmt=lambda v: {1: "1", 100: "100", 1e4: "10⁴", 1e6: "10⁶"}[v],
                 yfmt=lambda v: fmt(v))
    body = line(a.X(1), a.Y(0), a.X(1e6), a.Y(0), stroke=RULE_SOLID, sw=1.0)
    for run, col in zip(HV["running_means"]["cauchy"], cols):
        body += polyline([(a.X(n), a.Y(max(-7, min(7, v)))) for n, v in zip(cps, run)], col, sw=1.2, op=0.8)
    s += f'<g clip-path="url(#c9a)">{body}</g>'
    lows = [run[-1] for run in HV["running_means"]["cauchy"]]
    worst = min(lows, key=lambda v: -abs(v))
    s += mono(a.x0 + a.w, a.y0 + a.h + 32, "draws, log scale", size=8.5, fill=SOFT, anchor="end")
    iq = HV["cauchy_mean_iqr"]
    s += note_lines(a.x0, a.y0 + a.h + 58, [(f"one run ends at {fmt(worst, 0)} after 10⁶ draws, off the scale", MUTED),
                                            ("interquartile range of the mean, n = 1 to 1,000:", MUTED),
                                            (", ".join(f"{v['iqr']:.2f}" for v in iq.values()) + " (one draw: 2)", INK)], size=8)
    b = Axes(410, 104, 260, 260, (1, 1e6), (1, 7), xmap=lg)
    s += b.clip("c9b")
    s += title(b.x0, b.y0 - 28, "Pareto, tail index 1.5: mean 3")
    s += b.frame([1, 100, 1e4, 1e6], [1, 3, 5, 7], xfmt=lambda v: {1: "1", 100: "100", 1e4: "10⁴", 1e6: "10⁶"}[v],
                 yfmt=lambda v: fmt(v))
    body = line(b.X(1), b.Y(3), b.X(1e6), b.Y(3), stroke=ACCENT, sw=1.2, dash="5,3")
    for run, col in zip(HV["running_means"]["pareto15"], cols):
        body += polyline([(b.X(n), b.Y(max(0.5, min(7.5, v)))) for n, v in zip(cps, run)], col, sw=1.2, op=0.8)
    s += f'<g clip-path="url(#c9b)">{body}</g>'
    s += mono(b.x0 + b.w, b.y0 + b.h + 32, "draws, log scale", size=8.5, fill=SOFT, anchor="end")
    pt = HV["pareto15_ttest"]
    ratios = [pt[str(10 ** (k + 1))]["iqr_of_mean"] / pt[str(10 ** k)]["iqr_of_mean"] for k in (1, 2, 3, 4)]
    s += note_lines(b.x0, b.y0 + b.h + 58, [("spread of the mean per tenfold n:", MUTED),
                                            (f"× {ratios[-1]:.3f} measured; stable law × {10 ** (-1 / 3):.3f};", INK),
                                            (f"finite variance × {10 ** (-1 / 2):.3f}", MUTED)], size=8)
    c = Axes(736, 104, 240, 260, (10, 1e5), (0, 45), xmap=lg)
    s += c.clip("c9c")
    s += title(c.x0, c.y0 - 28, "lower-tail rejections, %")
    s += c.frame([10, 1000, 1e5], [0, 5, 15, 25, 35, 45], xfmt=lambda v: {10: "10", 1000: "1,000", 1e5: "10⁵"}[v],
                 yfmt=lambda v: f"{v:g}")
    body = line(c.X(10), c.Y(5), c.X(1e5), c.Y(5), stroke=MUTED, sw=1.2, dash="2,3")
    par = [(int(n), 100 * v["lower"]["p"]) for n, v in pt.items()]
    spd = [(int(n), 100 * BYN[n]["lower"]["p"]) for n in BYN]
    exn = [(int(n), 100 * SK["populations"]["exponential"]["by_n"][n]["lower"]["p"]) for n in SK["populations"]["exponential"]["by_n"]]
    for pts, col in ((par, ACCENT), (spd, INK), (exn, LINK)):
        body += polyline([(c.X(n), c.Y(v)) for n, v in pts], col, sw=1.8)
        body += "".join(dot(c.X(n), c.Y(v), 2.8, fill=col) for n, v in pts)
    s += f'<g clip-path="url(#c9c)">{body}</g>'
    s += mono(c.x0 + c.w, c.y0 + c.h + 32, "n, log scale", size=8.5, fill=SOFT, anchor="end")
    s += note_lines(c.x0, c.y0 + c.h + 58, [(f"Pareto: {par[-2][1]:.1f}% at n = 10,000,", ACCENT),
                                            (f"{par[-1][1]:.1f}% ± {100 * pt['100000']['lower']['mcse']:.1f} at n = 100,000", ACCENT)], size=8)
    s += legend(vh - 30, vw, [("three seeded runs", "line:" + MUTED), ("Pareto's mean", "dash:" + ACCENT),
                              ("Pareto", "linept:" + ACCENT), ("spend", "linept:" + INK), ("exponential", "linept:" + LINK),
                              ("nominal 5%", "dotted:" + MUTED)], x=100)
    return emit("09", "infinite-variance", "When the CLT never arrives",
                "Running means of a million draws, and the one-sided t-test's lower-tail rate, from the lab.",
                "infinite variance", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 560
    s = MARKS + eyebrow(32, 40, "how much a simulated rate moves between reruns: its monte carlo standard error")
    rec = RP["lognormal_n30"]
    truth = rec["truth"]
    ax = Axes(110, 104, 560, 300, (0.095, 0.140), (0, 2.3))
    s += title(ax.x0, ax.y0 - 28, "standard lognormal, n = 30: two-sided 5% t-test, rejection rate per rerun")
    s += ax.frame([0.10, 0.11, 0.12, 0.13, 0.14], [], xfmt=lambda v: f"{v:.2f}", grid_y=False)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "simulated rejection rate", size=8.5, fill=SOFT, anchor="end")
    rows = (("5000", 1.7, "2017"), ("20000", 0.5, "2023"))
    for key, base, year in rows:
        sr = rec["small_runs"][key]
        est = sr["estimates"]
        bw = 0.001
        bins = {}
        for e in est:
            k = int(math.floor(e / bw))
            bins[k] = bins.get(k, 0) + 1
        top = max(bins.values())
        for k, c in bins.items():
            h = 0.55 * c / top
            s += rect(ax.X(k * bw), ax.Y(base - 0.3 + h), ax.X((k + 1) * bw) - ax.X(k * bw), ax.Y(base - 0.3) - ax.Y(base - 0.3 + h),
                      fill=BAR_FILL, op=BAR_OP, stroke=BAR_STROKE, sw=0.6)
        pub = rec["published"][year]
        s += line(ax.X(pub["value"]), ax.Y(base - 0.3), ax.X(pub["value"]), ax.Y(base + 0.35), stroke=ACCENT, sw=2.0)
        s += plate(ax.X(pub["value"]) - 6, ax.Y(base + 0.40), f"published {year}: {pub['value']}", size=8.5, fill=ACCENT,
                   anchor="end", weight="600")
        s += line(ax.X(truth["p"]), ax.Y(base - 0.3), ax.X(truth["p"]), ax.Y(base + 0.35), stroke=INK, sw=1.6, dash="5,3")
        s += mono(ax.x0 + 6, ax.Y(base - 0.3) + 16, f"{sr['runs']} reruns at R = {int(key):,}: SD {sr['sd']:.4f}; "
                                                    f"formula √(p(1 − p)/R) = {sr['sd_formula']:.4f}", size=8, fill=MUTED,
                  anchor="start")
    s += mono(ax.X(truth["p"]) + 6, ax.Y(rows[0][1] + 0.35) + 4, f"R = {truth['R']:,}: {truth['p']:.4f} ± {truth['mcse']:.4f}",
              size=8.5, fill=INK, anchor="start", weight="600")
    s += note_lines(700, 150, [("the same experiment, rerun with", INK), ("fresh random numbers:", INK),
                               ("each published value sits inside", MUTED), ("the spread of reruns at its own R,", MUTED),
                               ("so the change between the two", MUTED), ("versions is within simulation", MUTED),
                               ("noise; an MCSE beside each", MUTED), ("would have shown it", MUTED)], gap=16)
    s += note_lines(110, 470, [("published values: Wilcox and Rousselet's 2017 preprint (R = 5,000) and their 2023 update; "
                                "the 2023 replication count is not stated unambiguously", MUTED)])
    s += legend(vh - 30, vw, [("reruns of the simulation", "bar"), ("published value", "line:" + ACCENT),
                              ("high-precision value", "dash:" + INK)])
    return emit("10", "monte-carlo-error", "Monte Carlo error, made visible",
                "Reruns of Wilcox and Rousselet's lognormal simulation at the replication counts behind their two "
                "published values, from the lab.", "replications", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10}

if __name__ == "__main__":
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
