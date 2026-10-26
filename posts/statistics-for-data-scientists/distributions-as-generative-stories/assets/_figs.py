#!/usr/bin/env python3
"""Figures 02-10 for distributions-as-generative-stories (Figure 01 is Mermaid: _mermaid.py).

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/stories.py.
The asserts below pin each number the article quotes, so a figure cannot drift from the text.
Run:  python3 _figs.py [02 05 ...]
"""
import json
import math
import pathlib
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SANS, SOFT,
                    emit, eyebrow, mono, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
W, A, S, T, L = CAP["worked"], CAP["accidents"], CAP["sums"], CAP["tails"], CAP["loglog"]
COAL = CAP["waiting"]["coal"]

# The numbers the article prints, held to the capture.
assert [round(v, 2) for v in W["clarke"]["expected_poisson"]] == [226.74, 211.39, 98.54, 30.62, 7.14, 1.57]
assert round(W["clarke"]["chi2"], 2) == 1.17 and round(W["clarke"]["chi2_p"], 2) == 0.88
assert round(W["bortkiewicz_200"]["mean"], 2) == 0.61 and round(W["bortkiewicz_200"]["variance"], 3) == 0.611
assert round(A["data"]["variance"], 4) == 0.6919 and round(A["negative_binomial"]["k"], 3) == 0.955
assert round(A["poisson"]["chi2"], 1) == 103.1 and round(A["negative_binomial"]["chi2"], 2) == 4.20
assert round(A["gamma"]["accident_share"]["top_20"], 2) == 0.53
assert round(T["two_sided_tail"]["4"]["ratio"], 1) == 56.4
assert round(L["lognormal"]["r2"], 3) == 0.991 and round(L["lognormal"]["slope"], 3) == -0.918
assert round(COAL["pooled"]["cv"], 2) == 1.47 and round(COAL["1851_1889"]["cv"], 2) == 1.06
assert COAL["explosions_before_1890"] == 123 and COAL["explosions_from_1890"] == 68


# ------------------------------------------------------------------ drawing helpers (Part 14's set)
def fmt(v, nd=1):
    v = float(v)
    s = f"{round(v):,}" if abs(v - round(v)) < 1e-9 else f"{v:,.{nd}f}"
    return s.replace("-", "−")


def sci(v, nd=1):
    """Scientific notation with a real times sign and superscript exponent."""
    m, e = f"{float(v):.{nd}e}".split("e")
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    return f"{m} × 10{str(int(e)).translate(sup)}"


def sg(v, nd=2):
    """A signed number with a true minus sign."""
    return f"{float(v):.{nd}f}".replace("-", "−")


def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{o} '
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

BAR_FILL, BAR_OP, BAR_STROKE = LINK, 0.22, LINK      # observed bars: the same in every legend
TAIL_FILL, TAIL_OP = ACCENT, 0.20
TOP_FILL, TOP_OP = INK, 0.12                         # the high-rate women in Figure 6


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


def legend(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like this post's marks."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, kind in items:
        if kind == "bar":
            s += rect(x, y - 1, 16, 12, fill=BAR_FILL, op=BAR_OP, stroke=BAR_STROKE, sw=1.0)
        elif kind == "tail":
            s += rect(x, y - 1, 16, 12, fill=TAIL_FILL, op=TAIL_OP, stroke="none", sw=0)
        elif kind == "top":
            s += rect(x, y - 1, 16, 12, fill=TOP_FILL, op=TOP_OP, stroke="none", sw=0)
        elif kind == "between":
            s += rect(x, y - 1, 16, 12, fill=TAIL_FILL, op=TAIL_OP, stroke=ACCENT, sw=1.0)
        elif kind.startswith("line:"):
            s += line(x, y + 5, x + 18, y + 5, stroke=kind[5:], sw=2.0)
        elif kind.startswith("linept:"):
            s += line(x, y + 5, x + 18, y + 5, stroke=kind[7:], sw=1.8) + dot(x + 9, y + 5, 3.2, fill=kind[7:])
        elif kind.startswith("dash:"):
            s += line(x, y + 5, x + 18, y + 5, stroke=kind[5:], sw=1.4, dash="5,3")
        elif kind.startswith("pt:"):
            s += dot(x + 8, y + 5, 2.6, fill=kind[3:], op=0.75)
        elif kind.startswith("ring:"):
            s += dot(x + 8, y + 5, 3.4, fill=PAPER, stroke=kind[5:])
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 26
    return s


def rootogram(ax, obs, exp, cid):
    """Hanging rootogram: a bar of sqrt(observed) hangs from the curve at sqrt(expected)."""
    s = f'<g clip-path="url(#{cid})">'
    for j, (o, e) in enumerate(zip(obs, exp)):
        top, bot = math.sqrt(e), math.sqrt(e) - math.sqrt(o)
        x0, x1 = ax.X(j - 0.36), ax.X(j + 0.36)
        s += rect(x0, ax.Y(top), x1 - x0, ax.Y(bot) - ax.Y(top), fill=BAR_FILL, op=BAR_OP,
                  stroke=BAR_STROKE, sw=1.0)
    pts = [(ax.X(j), ax.Y(math.sqrt(e))) for j, e in enumerate(exp)]
    s += polyline(pts, INK, sw=1.8) + "".join(dot(x, y, 3.2, fill=INK) for x, y in pts) + "</g>"
    return s


def warning_band(ax):
    """Zero line and Tukey's ±1 warning limits, labelled just outside the plot's right edge."""
    s = line(ax.x0, ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=MUTED, sw=1.0)
    for v, lab in ((-1, "−1"), (1, "+1")):
        s += line(ax.x0, ax.Y(v), ax.x0 + ax.w, ax.Y(v), stroke=MUTED, sw=1.0, dash="5,3")
        s += mono(ax.x0 + ax.w + 6, ax.Y(v) + 3, lab, size=8, fill=SOFT, anchor="start")
    return s


def bottoms(obs, exp):
    return [math.sqrt(e) - math.sqrt(o) for o, e in zip(obs, exp)]


CLASSES = ["0", "1", "2", "3", "4", "5+"]


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 536
    s = MARKS + eyebrow(32, 40, "two historical tallies, two generative stories, one family")
    c, b = W["clarke"], W["bortkiewicz_200"]
    assert max(abs(v) for v in bottoms(c["observed"], c["expected_poisson"])) < 1
    assert max(abs(v) for v in bottoms(b["observed"], b["expected_poisson"])) < 1
    panels = [
        (Axes(96, 104, 360, 290, (-0.6, 5.6), (-1.6, 16.0)), c, "c2a",
         "Clarke 1946 · 576 squares of south London", "flying bombs per square",
         [0, 5, 10, 15],
         [(f"537 bombs, λ = 537/576 = {c['lambda']:.3f}", INK),
          (f"variance {c['variance']:.3f} against mean {c['mean']:.3f}", MUTED),
          (f"χ² = {c['chi2']:.2f} on 4 df, P = {c['chi2_p']:.2f}", MUTED)]),
        (Axes(600, 104, 360, 290, (-0.6, 5.6), (-1.6, 12.0)), b, "c2b",
         "Bortkiewicz 1898 · 200 corps-years", "horse-kick deaths per corps-year",
         [0, 5, 10],
         [(f"{b['deaths']} deaths, {b['mean']:.2f} per corps-year", INK),
          (f"variance {b['variance']:.3f} against mean {b['mean']:.3f}", MUTED),
          ("the Guard and corps I, VI, XI left out", MUTED)]),
    ]
    for ax, data, cid, head, xlab, yt, notes in panels:
        s += ax.clip(cid)
        s += title(ax.x0, ax.y0 - 28, head)
        s += ax.frame([], yt, ylab="√ count", yfmt=lambda v: f"{v:g}")
        for j, lab in enumerate(CLASSES):
            s += mono(ax.X(j), ax.y0 + ax.h + 15, lab, size=8, fill=SOFT)
        s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, xlab, size=8.5, fill=SOFT, anchor="end")
        s += warning_band(ax)
        s += rootogram(ax, data["observed"], data["expected_poisson"], cid)
        s += note_lines(ax.x0, ax.y0 + ax.h + 58, notes)
    s += legend(vh - 30, vw, [("observed, hung from expected", "bar"), ("Poisson expected", "linept:" + INK),
                              ("Tukey's ±1 warning limits", "dash:" + MUTED)])
    return emit("02", "two-poisson-tallies", "Clarke's flying bombs and Bortkiewicz's horse kicks",
                "Hanging rootograms against the Poisson with the sample mean as its rate. Counts from the papers; "
                "expected values from the lab.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 548
    s = MARKS + eyebrow(32, 40, "the exponential needs one constant rate; the coal record has two")
    dates = COAL["dates"]
    n = len(dates)
    # Panel A: cumulative count of explosions.
    ax = Axes(96, 104, 380, 290, (1850, 1965), (0, 200))
    s += ax.clip("c3a")
    s += title(ax.x0, ax.y0 - 28, "explosions so far, 1851–1962")
    s += ax.frame([1860, 1880, 1900, 1920, 1940, 1960], [0, 50, 100, 150, 200],
                  ylab="explosions killing ten or more", xfmt=str, yfmt=str)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "year", size=8.5, fill=SOFT, anchor="end")
    pts = []
    for i, d in enumerate(dates):
        if pts:
            pts.append((ax.X(d), pts[-1][1]))
        pts.append((ax.X(d), ax.Y(i + 1)))
    s += f'<g clip-path="url(#c3a)">'
    s += line(ax.X(dates[0]), ax.Y(1), ax.X(dates[-1]), ax.Y(n), stroke=MUTED, sw=1.4, dash="5,3")
    s += polyline(pts, INK, sw=1.8) + "</g>"
    s += line(ax.X(1890), ax.y0, ax.X(1890), ax.y0 + ax.h, stroke=RULE_SOLID, sw=1.0, dash="2,3")
    early_rate = COAL["explosions_before_1890"] / (1890 - dates[0])
    late_rate = COAL["explosions_from_1890"] / (dates[-1] - 1890)
    s += plate(ax.X(1890) + 6, ax.y0 + 14, "1 January 1890", size=8, fill=SOFT, anchor="start")
    s += plate(ax.X(1915), ax.Y(70) + 4, "one constant rate, dashed", size=8, fill=MUTED, anchor="start")
    s += note_lines(ax.x0, ax.y0 + ax.h + 58, [
        (f"{COAL['explosions_before_1890']} explosions before 1890, {early_rate:.1f} a year", INK),
        (f"{COAL['explosions_from_1890']} from 1890 to 1962, {late_rate:.2f} a year", MUTED)])
    # Panel B: share of gaps longer than t, log scale; an exponential is a straight line.
    bx = Axes(600, 104, 360, 290, (0, 2000), (0.003, 1), ymap=math.log10)
    s += bx.clip("c3b")
    s += title(bx.x0, bx.y0 - 28, "gaps between explosions")
    s += bx.frame([0, 500, 1000, 1500, 2000], [0.003, 0.01, 0.03, 0.1, 0.3, 1],
                  ylab="share of gaps longer than t, log scale", xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: f"{v:g}")
    s += mono(bx.x0 + bx.w, bx.y0 + bx.h + 32, "t, days", size=8.5, fill=SOFT, anchor="end")
    body = ""
    for key, col in (("pooled", INK), ("1851_1889", LINK)):
        g = COAL[key]
        obs = [(bx.X(t), bx.Y(max(v, 0.002))) for t, v in zip(g["survival_days"], g["survival_observed"]) if v > 0]
        expo = [(bx.X(t), bx.Y(max(v, 0.002))) for t, v in zip(g["survival_days"], g["survival_exponential"])]
        body += polyline(expo, col, sw=1.3, dash="5,3") + polyline(obs, col, sw=2.0)
    s += f'<g clip-path="url(#c3b)">{body}</g>'
    p, e = COAL["pooled"], COAL["1851_1889"]
    s += note_lines(bx.x0, bx.y0 + bx.h + 58, [
        (f"all 190 gaps: CV {p['cv']:.2f}; no record of 190 exponential gaps reached it", INK),
        (f"in R = {COAL['R']:,} (largest {p['sim_cv_max']:.2f})", MUTED),
        (f"1851–1889: CV {e['cv']:.2f}; {e['sim_cv_share_at_least']:.1%} of exponential records reach it", LINK)])
    s += legend(vh - 30, vw, [("all gaps", "line:" + INK), ("exponential, their mean", "dash:" + INK),
                              ("1851–1889 gaps", "line:" + LINK), ("exponential, their mean", "dash:" + LINK)])
    return emit("03", "coal-gaps", "Gaps between coal-mine explosions",
                "Dates of 191 explosions from R's boot package; gaps and simulated exponential records from the lab "
                f"(R = {COAL['R']:,}).", "waiting times", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def lognormal_pdf(x, m, sd):
    return math.exp(-((math.log(x) - m) ** 2) / (2 * sd * sd)) / (x * sd * math.sqrt(2 * math.pi))


def normal_pdf(x, m, sd):
    return math.exp(-((x - m) ** 2) / (2 * sd * sd)) / (sd * math.sqrt(2 * math.pi))


def fig04():
    vw, vh = 1016, 520
    s = MARKS + eyebrow(32, 40, "the same twelve effects, added and multiplied")
    sm, pr, lp = S["sum"], S["product"], S["log_product"]
    panels = [
        ("added: the sum", sm, (8, 16), [8, 10, 12, 14, 16], lambda x: normal_pdf(x, sm["mean"], sm["sd"]),
         "normal with the sum's mean and sd", [(f"skewness {sg(sm['skewness'])}", INK),
                                               (f"median {sm['median']:.2f}, mean {sm['mean']:.2f}", MUTED)]),
        ("multiplied: the product", pr, (0, 4), [0, 1, 2, 3, 4], lambda x: lognormal_pdf(x, lp["mean"], lp["sd"]),
         "lognormal from the log's mean and sd", [(f"skewness {sg(pr['skewness'])}", ACCENT),
                                                  (f"median {pr['median']:.2f}, mean {pr['mean']:.2f}", MUTED),
                                                  (f"{pr['share_below_mean']:.0%} of products below the mean", MUTED),
                                                  (f"{pr['share_outside_hist']:.1%} lie beyond 4, off the axis", MUTED)]),
        ("the log of the product", lp, (-4, 3), [-4, -2, 0, 2], lambda x: normal_pdf(x, lp["mean"], lp["sd"]),
         "normal with the log's mean and sd", [(f"skewness {sg(lp['skewness'])}", INK),
                                               (f"median {sg(lp['median'])}, mean {sg(lp['mean'])}", MUTED)]),
    ]
    for k, (head, d, xr, xt, pdf, _, notes) in enumerate(panels):
        ymax = max(d["hist_density"]) * 1.18
        ax = Axes(80 + k * 322, 110, 252, 250, xr, (0, ymax))
        cid = f"c4{k}"
        s += ax.clip(cid)
        s += title(ax.x0, ax.y0 - 28, head)
        s += ax.frame(xt, [], ylab="density" if k == 0 else None, xfmt=lambda v: fmt(v))
        e, h = d["hist_edges"], d["hist_density"]
        bars = "".join(rect(ax.X(e[i]), ax.Y(h[i]), ax.X(e[i + 1]) - ax.X(e[i]), ax.Y(0) - ax.Y(h[i]),
                            fill=BAR_FILL, op=BAR_OP, stroke=BAR_STROKE, sw=0.5) for i in range(len(h)))
        xs = [xr[0] + (xr[1] - xr[0]) * i / 300 for i in range(1, 301)]
        curve = polyline([(ax.X(x), ax.Y(pdf(x))) for x in xs if pdf(x) < ymax * 1.5], INK, sw=1.8)
        s += f'<g clip-path="url(#{cid})">{bars}{curve}</g>'
        s += note_lines(ax.x0, ax.y0 + ax.h + 44, notes)
    s += note_lines(80, 470, [(f"{S['R']:,} simulated outcomes; each draws 12 effects from 0.5 to 1.5 and combines "
                               "the same draws three ways", MUTED)])
    s += legend(vh - 30, vw, [("simulated outcomes", "bar"), ("normal or lognormal curve, matched moments", "line:" + INK)])
    return emit("04", "sums-and-products", "Twelve effects, added and multiplied",
                f"Histograms of {S['R']:,} simulated outcomes from the lab, with a normal or lognormal curve whose "
                "parameters are the simulated moments.", "sums and products", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 536
    s = MARKS + eyebrow(32, 40, "greenwood and yule's 647 women: the poisson misses both ends")
    d, po, nb = A["data"], A["poisson"], A["negative_binomial"]
    assert max(abs(v) for v in bottoms(d["observed"], nb["expected"])) < 1
    assert sum(abs(v) > 1 for v in bottoms(d["observed"], po["expected"])) >= 3
    panels = [
        (Axes(96, 104, 360, 290, (-0.6, 5.6), (-2.6, 22.5)), po["expected"], "c5a",
         "Poisson, rate 0.465 for every woman",
         [(f"χ² = {po['chi2']:.1f} on 4 df", ACCENT),
          ("too many with none, too few with one,", MUTED), ("and three times too many with three", MUTED)]),
        (Axes(600, 104, 360, 290, (-0.6, 5.6), (-2.6, 22.5)), nb["expected"], "c5b",
         f"negative binomial, k = {nb['k']:.3f} by moments",
         [(f"χ² = {nb['chi2']:.2f} on 3 df", LINK),
          (f"variance {d['variance']:.3f} = {d['mean']:.3f} + {d['mean'] ** 2 / nb['k']:.3f}", MUTED),
          ("every bar ends inside the ±1 band", MUTED)]),
    ]
    for ax, exp, cid, head, notes in panels:
        s += ax.clip(cid)
        s += title(ax.x0, ax.y0 - 28, head)
        s += ax.frame([], [0, 5, 10, 15, 20], ylab="√ count", yfmt=lambda v: f"{v:g}")
        for j, lab in enumerate(CLASSES):
            s += mono(ax.X(j), ax.y0 + ax.h + 15, lab, size=8, fill=SOFT)
        s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "accidents in five weeks", size=8.5, fill=SOFT, anchor="end")
        s += warning_band(ax)
        s += rootogram(ax, d["observed"], exp, cid)
        s += note_lines(ax.x0, ax.y0 + ax.h + 58, notes)
    s += legend(vh - 30, vw, [("observed, hung from expected", "bar"), ("model expected", "linept:" + INK),
                              ("Tukey's ±1 warning limits", "dash:" + MUTED)])
    return emit("05", "accidents-two-fits", "Greenwood and Yule's accidents, two fits",
                "Hanging rootograms for the Poisson and the moment-fitted negative binomial. Counts from the paper "
                "as reproduced; fits from the lab.", "accident counts", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 520
    s = MARKS + eyebrow(32, 40, "what the fitted gamma says about the 647 women")
    g, sim = A["gamma"], A["proneness_simulation"]
    mu, k = A["data"]["mean"], A["negative_binomial"]["k"]
    xs, ys = g["density_x"], g["density"]
    ax = Axes(96, 104, 500, 280, (0, 2.5), (0, 2.8))
    s += ax.clip("c6")
    s += title(ax.x0, ax.y0 - 28, f"each woman's accident rate, gamma with shape {k:.3f} and mean {mu:.3f}")
    s += ax.frame([0, 0.5, 1, 1.5, 2, 2.5], [0, 1, 2], ylab="density", xfmt=lambda v: f"{v:g}",
                  yfmt=lambda v: f"{v:g}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "expected accidents in five weeks", size=8.5, fill=SOFT, anchor="end")
    cut = g["rate_cut"]["top_20"]
    i = next(j for j, x in enumerate(xs) if x >= cut)
    y_cut = ys[i - 1] + (ys[i] - ys[i - 1]) * (cut - xs[i - 1]) / (xs[i] - xs[i - 1])
    top = ([(ax.X(cut), ax.Y(0)), (ax.X(cut), ax.Y(y_cut))] + [(ax.X(x), ax.Y(y)) for x, y in zip(xs[i:], ys[i:])]
           + [(ax.X(xs[-1]), ax.Y(0))])
    s += f'<g clip-path="url(#c6)">' + area(top, TOP_FILL, TOP_OP)
    s += polyline([(ax.X(x), ax.Y(y)) for x, y in zip(xs, ys)], INK, sw=2.0) + "</g>"
    s += line(ax.X(mu), ax.y0, ax.X(mu), ax.y0 + ax.h, stroke=INK, sw=1.0, dash="3,3")
    s += plate(ax.X(mu) + 6, ax.y0 + 14, f"mean rate {mu:.3f}", size=8.5, fill=INK, anchor="start")
    s += plate(ax.X(1.35), ax.Y(0.55), f"top 20% of women: rates above {cut:.2f}", size=8.5, fill=INK, anchor="start",
               weight="600")
    s += plate(ax.X(1.35), ax.Y(0.55) + 16,
               f"{g['accident_share']['top_20']:.0%} of the expected accidents", size=8.5, fill=MUTED, anchor="start")
    s += note_lines(ax.x0, ax.y0 + ax.h + 58, [
        (f"median rate {g['median']:.2f}: {g['share_below_mean']:.1%} of women sit below the mean; the top 10% carry "
         f"{g['accident_share']['top_10']:.0%} of expected accidents", MUTED)])
    # Panel B: the variance in two parts, theory against the simulated factories.
    bx0, by0, bh, bw = 708, 104, 280, 74
    vmax = 0.75
    yv = lambda v: by0 + bh - v / vmax * bh
    s += title(bx0 - 40, by0 - 28, "variance of a woman's count")
    s += line(bx0 - 14, by0 + bh, bx0 + bw + 14, by0 + bh, stroke=RULE_SOLID)
    for v in (0, 0.25, 0.5, 0.75):
        s += mono(bx0 - 20, yv(v) + 3, f"{v:g}", size=8, fill=SOFT, anchor="end")
    s += rect(bx0, yv(mu), bw, yv(0) - yv(mu), fill=BAR_FILL, op=BAR_OP, stroke=BAR_STROKE, sw=1.0)
    s += rect(bx0, yv(mu + mu * mu / k), bw, yv(mu) - yv(mu + mu * mu / k), fill=TAIL_FILL, op=TAIL_OP,
              stroke=ACCENT, sw=1.0)
    s += note_lines(bx0 + bw + 12, yv(mu / 2) - 8, [(f"μ = {mu:.3f}", LINK), ("Poisson noise", MUTED),
                                                     (f"sim. {sim['within_part']:.3f}", MUTED)], size=8.5, gap=14)
    s += note_lines(bx0 + bw + 12, yv(mu + mu * mu / (2 * k)) - 8, [(f"μ²/k = {mu * mu / k:.3f}", ACCENT),
                                                                    ("rates differ", MUTED),
                                                                    (f"sim. {sim['between_part']:.3f}", MUTED)],
                    size=8.5, gap=14)
    s += plate(bx0 + bw / 2, yv(mu + mu * mu / k) - 8, f"total {mu + mu * mu / k:.3f}", size=8.5, fill=INK, weight="600")
    s += note_lines(bx0 - 40, by0 + bh + 58, [(f"simulated: R = {sim['R']:,} factories of 647", MUTED)])
    s += legend(vh - 30, vw, [("gamma density of rates", "line:" + INK), ("top 20% of women", "top"),
                              ("Poisson part", "bar"), ("part from rates that differ", "between")])
    return emit("06", "gamma-behind-the-fit", "The gamma behind the negative binomial",
                "The moment-fitted gamma of accident rates, and the variance split into Poisson noise and rate "
                f"differences. Theory and a simulation from the lab (R = {sim['R']:,}).", "accident counts", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 520
    s = MARKS + eyebrow(32, 40, "a unit-variance t with 5 degrees of freedom against the normal")
    ax = Axes(96, 104, 380, 280, (-5, 5), (0, 0.55))
    s += ax.clip("c7a")
    s += title(ax.x0, ax.y0 - 28, "densities, linear scale")
    s += ax.frame([-4, -2, 0, 2, 4], [0, 0.1, 0.2, 0.3, 0.4, 0.5], ylab="density", xfmt=lambda v: fmt(v),
                  yfmt=lambda v: f"{v:g}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "x, in standard deviations", size=8.5, fill=SOFT, anchor="end")
    dx = T["density_x"]
    s += f'<g clip-path="url(#c7a)">'
    s += polyline([(ax.X(x), ax.Y(y)) for x, y in zip(dx, T["density_normal"])], INK, sw=2.0)
    s += polyline([(ax.X(x), ax.Y(y)) for x, y in zip(dx, T["density_t"])], ACCENT, sw=2.0) + "</g>"
    s += dot(ax.X(0), ax.Y(T["peak_t"]), 3.4, fill=ACCENT) + dot(ax.X(0), ax.Y(T["peak_normal"]), 3.4, fill=INK)
    s += note_lines(ax.x0, ax.y0 + ax.h + 58, [
        (f"peaks (dots): t₅ {T['peak_t']:.3f}, normal {T['peak_normal']:.3f}", INK),
        ("same mean 0 and variance 1; beyond 4 both curves", MUTED),
        ("sit within a pixel of the axis", MUTED)])
    bx = Axes(600, 104, 360, 280, (0, 6.5), (1e-10, 1), ymap=math.log10)
    s += bx.clip("c7b")
    s += title(bx.x0, bx.y0 - 28, "P(|X| > x), log scale")
    yt = [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1]
    s += bx.frame([0, 1, 2, 3, 4, 5, 6], yt, ylab="two-sided tail probability",
                  yfmt=lambda v: "1" if v == 1 else f"1e{int(round(math.log10(v)))}".replace("-", "−"))
    s += mono(bx.x0 + bx.w, bx.y0 + bx.h + 32, "x, in standard deviations", size=8.5, fill=SOFT, anchor="end")
    cx = T["curve_x"]
    s += f'<g clip-path="url(#c7b)">'
    s += polyline([(bx.X(x), bx.Y(max(y, 1e-11))) for x, y in zip(cx, T["curve_normal"])], INK, sw=2.0)
    s += polyline([(bx.X(x), bx.Y(y)) for x, y in zip(cx, T["curve_t"])], ACCENT, sw=2.0) + "</g>"
    for x, dy in ((3, -10), (4, -10), (5, -10)):
        r = T["two_sided_tail"][str(x)]
        s += line(bx.X(x), bx.Y(r["t"]), bx.X(x), bx.Y(r["normal"]), stroke=MUTED, sw=1.0, dash="2,2")
        s += dot(bx.X(x), bx.Y(r["t"]), 3.2, fill=ACCENT) + dot(bx.X(x), bx.Y(r["normal"]), 3.2, fill=INK)
        lab = f"×{r['ratio']:,.1f}" if r["ratio"] < 100 else f"×{r['ratio']:,.0f}"
        s += mono(bx.X(x), bx.Y(0.05), lab, size=8.5, fill=MUTED, anchor="middle", weight="600")
        s += line(bx.X(x), bx.Y(0.05) + 5, bx.X(x), bx.Y(r["t"]) - 5, stroke=MUTED, sw=1.0, dash="2,2")
    r4 = T["two_sided_tail"]["4"]
    s += note_lines(bx.x0, bx.y0 + bx.h + 58, [
        (f"beyond 4: t₅ {r4['t'] * 100:.3f}%, normal {r4['normal'] * 100:.4f}%", INK)])
    s += legend(vh - 30, vw, [("normal", "line:" + INK), ("t₅ scaled to variance 1", "line:" + ACCENT)])
    return emit("07", "t5-against-normal", "A unit-variance t₅ against the normal",
                "Exact densities and two-sided tail probabilities from SciPy, matched to a closed form in the lab.",
                "tails", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 548
    s = MARKS + eyebrow(32, 40, "a q–q plot shows the tails a histogram hides")
    q, sim = T["qq"], T["simulation"]
    theo = q["theoretical"]
    for k, (key, col, head, nb) in enumerate((("normal_sample", INK, "1,000 draws from the normal", q["normal_beyond_4"]),
                                              ("t_sample", ACCENT, "1,000 draws from the unit-variance t₅", q["t_beyond_4"]))):
        ax = Axes(96 + k * 504, 104, 360, 280, (-3.6, 3.6), (-5.2, 5.2))
        cid = f"c8{k}"
        s += ax.clip(cid)
        s += title(ax.x0, ax.y0 - 28, head)
        s += ax.frame([-3, -2, -1, 0, 1, 2, 3], [-4, -2, 0, 2, 4], ylab="sorted sample",
                      xfmt=lambda v: fmt(v), yfmt=lambda v: fmt(v))
        s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "normal quantile", size=8.5, fill=SOFT, anchor="end")
        pts = "".join(dot(ax.X(x), ax.Y(y), 2.0, fill=col, op=0.75) for x, y in zip(theo, q[key]))
        s += f'<g clip-path="url(#{cid})">' + line(ax.X(-3.6), ax.Y(-3.6), ax.X(3.6), ax.Y(3.6), stroke=MUTED, sw=1.2,
                                                  dash="5,3") + pts + "</g>"
        for v in (-4, 4):
            s += line(ax.x0, ax.Y(v), ax.x0 + ax.w, ax.Y(v), stroke=RULE_SOLID, sw=0.8, dash="2,3")
        s += note_lines(ax.x0, ax.y0 + ax.h + 48, [(f"{nb} of 1,000 beyond ±4 in this draw", col)])
    t, z = sim["t"], sim["normal"]
    s += note_lines(96, 478, [(f"over R = {sim['R']:,} samples of 1,000: a point beyond 4 in {t['share_with_any']:.1%} "
                               f"± {t['share_with_any_mcse']:.1%} of t₅ samples, {z['share_with_any']:.1%} ± "
                               f"{z['share_with_any_mcse']:.1%} of normal ones", MUTED)])
    s += legend(vh - 30, vw, [("normal sample", "pt:" + INK), ("t₅ sample", "pt:" + ACCENT),
                              ("y = x: a perfect normal", "dash:" + MUTED)])
    return emit("08", "qq-plots", "Q–Q plots of a normal and a t₅ sample",
                f"One seeded sample of each from the lab, against normal quantiles; tail shares over R = {sim['R']:,} "
                "simulated samples.", "tails", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 536
    s = MARKS + eyebrow(32, 40, "a lognormal sample draws a straight tail on log–log axes")
    ln = L["lognormal"]
    lg = math.log10
    ax = Axes(110, 104, 560, 300, (1e-4, 1e5), (1e-4, 1), xmap=lg, ymap=lg)
    s += ax.clip("c9")
    s += title(ax.x0, ax.y0 - 28, f"P(X ≥ x) for {ln['n']:,} draws of a lognormal with σ = {ln['sigma']:g}")
    xt = [1e-4, 1e-2, 1, 1e2, 1e4]
    s += ax.frame(xt, [1e-4, 1e-3, 1e-2, 1e-1, 1], ylab="share of draws at least x, log scale",
                  xfmt=lambda v: {1e-4: "0.0001", 1e-2: "0.01", 1: "1", 1e2: "100", 1e4: "10,000"}[v],
                  yfmt=lambda v: f"{v:g}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "x, log scale", size=8.5, fill=SOFT, anchor="end")
    pts = [(ax.X(x), ax.Y(y)) for x, y in zip(ln["ccdf_x"], ln["ccdf_y"]) if x > 0]
    thr = ln["threshold"]
    xa, xb = thr, max(ln["ccdf_x"])
    fit = [(ax.X(x), ax.Y(10 ** (ln["intercept"] + ln["slope"] * lg(x)))) for x in (xa, xb)]
    s += f'<rect x="{ax.X(thr):.1f}" y="{ax.y0}" width="{ax.X(1e5) - ax.X(thr):.1f}" height="{ax.h}" fill="rgba(45,49,66,0.035)"/>'
    s += f'<g clip-path="url(#c9)">' + polyline(pts, INK, sw=2.0) + polyline(fit, ACCENT, sw=2.2) + "</g>"
    s += mono(ax.X(thr) + 8, ax.y0 + 16, f"the top 10%: x above {thr:.1f}", size=8.5, fill=MUTED, anchor="start")
    s += note_lines(700, 132, [("least-squares line on the top 10%", ACCENT),
                               (f"{ln['fit_points']:,} points over {ln['decades']:.2f} decades", MUTED),
                               (f"slope {sg(ln['slope'], 3)}, R² = {ln['r2']:.3f}", ACCENT)], gap=15)
    s += note_lines(700, 202, [(f"read as P(X ≥ x) ∝ x^−{-ln['slope']:.2f}, a power law", INK),
                               ("with exponent below 1: an infinite mean", MUTED),
                               ("the lognormal that drew it has", MUTED),
                               (f"mean e^(σ²/2) = {math.exp(ln['sigma'] ** 2 / 2):.1f}", INK)], gap=15)
    s += note_lines(700, 288, [(f"over R = {ln['R']:,} such samples:", MUTED),
                               (f"R² ≥ 0.98 in {ln['share_r2_at_least_098']:.1%} ± {ln['share_r2_at_least_098_mcse']:.1%}",
                                MUTED), (f"median R² {ln['r2_median']:.3f}", MUTED)], gap=15)
    s += note_lines(110, 470, [("left of the shaded band the same curve bends away: the straightness is a property "
                                "of the window, not of the distribution", MUTED)])
    s += legend(vh - 30, vw, [("lognormal sample, complementary CDF", "line:" + INK),
                              ("least-squares line on the top 10%", "line:" + ACCENT)])
    return emit("09", "lognormal-log-log", "A lognormal on log–log axes",
                f"One seeded sample from the lab, its top 10% fitted by least squares; R² over R = {ln['R']:,} samples.",
                "log–log trap", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 520
    s = MARKS + eyebrow(32, 40, "champernowne's walk: one rule turns a lognormal into a power law")
    ch = L["champernowne"]
    ax = Axes(110, 104, 560, 290, (0, 20), (1e-10, 1), ymap=math.log10)
    s += ax.clip("c10")
    s += title(ax.x0, ax.y0 - 28, "P(X ≥ x): income doubles with probability 1/3, halves with 2/3")
    s += ax.frame([0, 5, 10, 15, 20], [1e-10, 1e-8, 1e-6, 1e-4, 1e-2, 1], ylab="P(X ≥ x), log scale",
                  xfmt=lambda v: {0: "1", 5: "32", 10: "1,024", 15: "32,768", 20: "1,048,576"}[v],
                  yfmt=lambda v: "1" if v == 1 else f"1e{int(round(math.log10(v)))}".replace("-", "−"))
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "x, log scale (powers of 2)", size=8.5, fill=SOFT, anchor="end")
    floor = [(ax.X(p["log2x"]), ax.Y(p["ccdf"])) for p in ch["floor_ccdf"]]
    nof = [(ax.X(p["log2x"]), ax.Y(p["ccdf"])) for p in ch["no_floor_ccdf"]]
    sim = "".join(dot(ax.X(j), ax.Y(v), 3.4, fill=PAPER, stroke=LINK) for j, v in enumerate(ch["simulated_floor_ccdf"]) if v > 0)
    s += f'<g clip-path="url(#c10)">' + polyline(floor, LINK, sw=2.0) + polyline(nof, ACCENT, sw=2.0)
    s += "".join(dot(x, y, 3.0, fill=ACCENT) for x, y in nof) + sim + "</g>"
    s += note_lines(700, 132, [("with a floor at 1", LINK), ("P(X ≥ x) = 1/x: a power law", MUTED),
                               ("a straight line of slope −1", MUTED),
                               (f"{ch['simulated_walkers']:,} walkers after {ch['simulated_steps']} steps:", MUTED),
                               (f"within {ch['simulated_max_abs_dev']:.4f} of it", MUTED)], gap=15)
    last = ch["no_floor_ccdf"][-1]["ccdf"]
    s += note_lines(700, 232, [("no floor, after 20 steps", ACCENT), ("log₂ X = 2U − 20, U ~ binomial(20, 1/3)", MUTED),
                               ("a discrete lognormal: it bends", MUTED),
                               (f"P(X ≥ 2²⁰) = {sci(last)} against {sci(2 ** -20)}", MUTED)], gap=15)
    s += note_lines(110, 448, [("same multiplicative steps in both; the only change is a lower barrier "
                                "(Champernowne's model, after Mitzenmacher 2004)", MUTED)])
    s += legend(vh - 30, vw, [("with a floor, exact", "line:" + LINK), ("with a floor, simulated", "ring:" + LINK),
                              ("no floor, exact", "linept:" + ACCENT)])
    return emit("10", "floor-makes-a-power-law", "Champernowne's floor",
                "Exact distributions of the multiplicative walk with and without a lower barrier, and a simulated "
                "check from the lab.", "log–log trap", vw, vh, s)


FIGS = {"02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10}

if __name__ == "__main__":
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
