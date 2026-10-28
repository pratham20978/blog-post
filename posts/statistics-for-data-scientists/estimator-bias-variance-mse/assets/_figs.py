#!/usr/bin/env python3
"""Figures 01-11 for estimator-bias-variance-mse.

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/estimators.py.
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
T, C, D, B, S = (CAP[k] for k in ("tanks", "consistency", "divisors", "baseball", "stein"))
EX, SIM = T["exact"], T["sim"]
N, K = T["N"], T["k"]
RB = T["rao_blackwell"]
POP = D["populations"]
RAW, ARC, REG, REP = B["raw"], B["arcsine"], B["regression"], B["replay"]

# The numbers the article prints, held to the capture.
assert (N, K, T["R"]) == (342, 5, 1_000_000) and T["worked"]["serials"] == [58, 171, 272, 273, 303]
assert round(EX["mle"]["bias"], 2) == -56.17 and round(EX["mvue"]["var"], 1) == 3302.6 and round(EX["mle"]["mse"]) == 5448
assert round(EX["mle"]["rmse"], 1) == 73.8 and round(EX["mvue"]["rmse"], 1) == 57.5 and round(EX["mom"]["rmse"], 1) == 87.8
assert round(T["mse_ratio_mle_mvue"]["exact"], 2) == 1.65 and round(T["mse_ratio_minmse_mvue"]["exact"], 4) == 0.9727
assert round(100 * T["shares"]["mvue_vs_mle"]["p"], 1) == 62.1 and round(T["var_ratio_mom_mvue"]["exact"], 2) == 2.33
assert [r["intelligence_ratio"] for r in T["ruggles_brodie"]] == [1000 / 122, 1550 / 271, 1550 / 342]
assert round(C["exact"]["10"]["mvue"]["rmse"] / C["exact"]["100"]["mvue"]["rmse"], 1) == 10.8
assert round(POP["normal"]["at"]["n-1"]["mse_exact"], 4) == 0.2222 and round(POP["normal"]["at"]["n+1"]["mse_exact"], 4) == 0.1818
assert round(POP["exponential"]["best_d_theory"], 1) == 16.4 and round(POP["uniform"]["best_d_theory"], 2) == 9.92
assert round(POP["exponential"]["mse_ratio_best_nm1"]["exact"], 2) == 0.55
assert round(RAW["c"], 3) == 0.212 and round(RAW["tse_y"], 4) == 0.0753 and round(RAW["tse_z"], 4) == 0.0213
assert RAW["closer"] == 16 and ARC["closer"] == 15 and round(ARC["tse_x"], 2) == 17.57 and round(ARC["tse_d"], 2) == 5.00
assert round(REG["slope"], 3) == 0.190 and round(100 * REP["share_js_wins"], 1) == 96.2
assert round(REP["efficiency_raw"]["ratio"], 2) == 2.66 and round(REP["ratio_quantiles"]["0.5"], 2) == 3.05
assert round(S["points"][0]["exact"], 3) == 3.0 and round(S["points"][-1]["efficiency_exact"], 2) == 2.64


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
        elif part[0] == "boxst":                     # boxst:colour:opacity, filled and outlined like a bar
            s += rect(x, y - 1, 16, 12, fill=part[1], op=float(part[2]), stroke=part[1], sw=1.0)
        elif part[0] == "thin":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.2)
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



def pct(v, nd=1):
    return f"{100 * v:.{nd}f}%"


def num(v, nd=1):
    """A number with thousands separators and a true minus sign."""
    return f"{v:,.{nd}f}".replace("-", "−")


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 440
    w, est = T["worked"], T["worked"]["estimates"]
    s = MARKS + eyebrow(32, 40, f"one capture: k = {K} tanks from N = {N}, and four estimates of N")
    X = lambda v: 80 + v * 856 / 560
    ya, yb = 156, 262
    s += title(80, ya - 40, "the five captured serial numbers")
    s += line(X(0), ya, X(w["max"]), ya, stroke=RULE_SOLID, sw=1.0)    # the observed range ends at the largest serial
    s += line(X(w["max"]), ya, X(est["mvue"]), ya, stroke=LINK, sw=1.8, dash="5,3")
    for v in w["serials"]:
        s += dot(X(v), ya, 4.5, fill=INK)
    labels = [(58, "58"), (171, "171"), (272.5, "272, 273"), (303, "303")]
    for v, lab in labels:
        s += mono(X(v), ya - 14, lab, size=9, fill=INK, weight="600")
    unseen = [g - 1 for g in w["gaps"]]
    s += mono(X(est["mvue"]) + 10, ya + 4, f"+ {num(est['mvue'] - w['max'])}: one more average gap, ({w['max']} − {K})/{K}",
              size=8.5, fill=LINK, anchor="start", weight="600")
    s += title(80, yb - 34, "estimates of N from this capture")
    s += line(X(0), yb, X(560), yb, stroke=RULE_SOLID, sw=1.0)
    marks = [("mle", "MLE", INK), ("mvue", "MVUE", LINK), ("mom", "2 × mean − 1", MUTED), ("first", "2 × one tank − 1", SOFT)]
    for key, lab, col in marks:
        x = X(est[key])
        s += line(x, yb - 10, x, yb + 10, stroke=col, sw=2.2)
        s += mono(x, yb + 28, lab, size=8.5, fill=col, weight="600")
        s += mono(x, yb + 42, num(est[key]) if abs(est[key] - round(est[key])) > 1e-9 else f"{est[key]:.0f}", size=8.5, fill=col)
    s += line(X(N), ya - 50, X(N), yb + 12, stroke=ACCENT, sw=1.6, dash="4,3")
    s += mono(X(N), ya - 56, f"true N = {N}", size=8.5, fill=ACCENT, weight="600")
    for v in range(0, 501, 100):
        s += line(X(v), 336, X(v), 341, stroke=RULE_SOLID) + mono(X(v), 355, str(v), size=8, fill=SOFT)
    s += line(X(0), 336, X(560), 336, stroke=RULE_SOLID)
    s += mono(X(560), 372, "serial number, and estimate of N", size=8.5, fill=SOFT, anchor="end")
    s += note_lines(80, 384, [(f"unseen serial numbers below {w['max']}, gap by gap: {', '.join(map(str, unseen))}; "
                               f"their average, {num(sum(unseen) / K)}, is the MVUE's step beyond the largest", MUTED)])
    s += legend(vh - 22, vw, [("captured serial number", "dot:" + INK + ":4.5:1"), ("true N", "dash:" + ACCENT),
                              ("one more average gap", "dash:" + LINK)])
    return emit("01", "one-capture", "One capture of five tanks",
                f"Five serial numbers drawn by the lab from 1 to {N} without replacement, and four estimates of N "
                "computed from them.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 680
    edges, reps = T["hist_edges"], T["R"]
    s = MARKS + eyebrow(32, 40, f"sampling distributions of three estimators over {reps:,} captures of k = {K} from N = {N}")
    panels = [("mle", "MLE: the largest serial number, m"), ("mvue", "MVUE: m(1 + 1/k) − 1"), ("mom", "2 × mean − 1")]
    by_m, pmf = T["count_by_max"], T["pmf_max"]          # captures per value of m; exact P(M = m) for m = k..N
    scale = {"mle": lambda m: m, "mvue": lambda m: m * (1 + 1 / K) - 1}
    for i, (key, name) in enumerate(panels):
        ax = Axes(96, 104 + i * 168, 600, 112, (0, 700), (0, 1.6))
        cid = f"c2{i}"
        s += ax.clip(cid)
        s += title(ax.x0, ax.y0 - 14, name)
        s += ax.frame([0, 100, 200, 300, 400, 500, 600, 700] if i == 2 else [], [0, 0.5, 1.0, 1.5],
                      ylab=None, xfmt=str, yfmt=lambda v: f"{v:g}%")
        bars = exact = ""
        if key in scale:                                   # bins of five values of m, ending at N, so none is cut short
            f = scale[key]
            for hi in range(N, K - 1, -5):
                lo = max(K, hi - 4)
                c = sum(by_m[lo:hi + 1])
                a, b = f(lo - 0.5), f(hi + 0.5)
                dens = 100 * c / (reps * (b - a))          # % of captures per tank of the estimate
                if c:
                    bars += rect(ax.X(a), ax.Y(dens), ax.X(b) - ax.X(a), ax.Y(0) - ax.Y(dens), fill=BAR_FILL,
                                 op=BAR_OP, stroke="none", sw=0)
            step = f(1) - f(0)
            exact = polyline([(ax.X(f(K + j)), ax.Y(100 * pv / step)) for j, pv in enumerate(pmf)], MUTED, sw=1.2)
        else:
            for j, c in enumerate(T["hist"][key]):
                dens = 100 * c / (reps * (edges[j + 1] - edges[j]))
                if c:
                    bars += rect(ax.X(edges[j]), ax.Y(dens), ax.X(edges[j + 1]) - ax.X(edges[j]), ax.Y(0) - ax.Y(dens),
                                 fill=BAR_FILL, op=BAR_OP, stroke="none", sw=0)
        s += f'<g clip-path="url(#{cid})">{bars}{exact}</g>'
        mean = EX[key]["mean"]
        s += line(ax.X(N), ax.y0, ax.X(N), ax.y0 + ax.h, stroke=ACCENT, sw=1.6)
        if abs(mean - N) > 1:
            s += line(ax.X(mean), ax.y0, ax.X(mean), ax.y0 + ax.h, stroke=INK, sw=1.2, dash="4,3")
        ex, si = EX[key], SIM[key]
        rows = [(f"bias {num(ex['bias'])}, SD {num(ex['sd'])}", INK), (f"RMSE {num(ex['rmse'])} tanks", INK),
                (f"simulated bias {num(si['bias'], 2)} ± {si['bias_mcse']:.2f}", MUTED)]
        if key == "mle":
            rows.append((f"never above {N}; equal to it in {pct(T['shares']['mle_hits_N']['p'], 2)}", ACCENT))
            rows.append((f"of captures (exact {K}/{N} = {pct(K / N, 2)})", ACCENT))
        if key == "mvue":
            rows.append(("mean exactly N: unbiased", MUTED))
        s += note_lines(740, ax.y0 + 10, rows, gap=15)
    s += mono(96 + 600, 104 + 2 * 168 + 112 + 32, "estimate of N; share of captures per tank of the estimate",
              size=8.5, fill=SOFT, anchor="end")
    s += note_lines(96, 104 + 2 * 168 + 112 + 58, [("bars group five values of m (5 tanks for the MLE, 6 for the MVUE) "
                                                    "and 5 tanks for 2 × mean − 1", SOFT)])
    s += legend(vh - 26, vw, [(f"simulated, R = {reps:,}", "barflat"), ("exact distribution", "thin:" + MUTED),
                              ("true N", "line:" + ACCENT), ("the estimator's mean", "dash:" + INK)])
    return emit("02", "sampling-distributions", "Three estimators' sampling distributions",
                f"Each estimator applied to {reps:,} simulated captures of five tanks from {N}, binned by the lab.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 470
    s = MARKS + eyebrow(32, 40, "mean squared error = bias² + variance, N = 342, k = 5")
    rows = [("mle", "MLE  m"), ("mvue", "MVUE  m(1 + 1/k) − 1"), ("minmse", "m(k + 2)/(k + 1) − 1"), ("mom", "2 × mean − 1")]
    x0, wpx, top = 250, 520, 104
    X = lambda v: x0 + v / 8000 * wpx
    for i, (key, name) in enumerate(rows):
        y = top + i * 56
        ex, si = EX[key], SIM[key]
        b2 = ex["bias"] ** 2
        s += mono(x0 - 14, y + 18, name, size=9, fill=INK, anchor="end", weight="600")
        s += rect(X(0), y, X(ex["var"]) - X(0), 28, fill=LINK, op=0.22, stroke=LINK, sw=1.0)
        if b2 > 1:
            s += rect(X(ex["var"]), y, X(ex["mse"]) - X(ex["var"]), 28, fill=ACCENT, op=0.25, stroke=ACCENT, sw=1.0)
        if X(ex["var"]) - X(0) > 110:
            s += mono((X(0) + X(ex["var"])) / 2, y + 18, f"variance {num(ex['var'], 0)}", size=8.5, fill=LINK)
        if X(ex["mse"]) - X(ex["var"]) > 100:
            s += mono((X(ex["var"]) + X(ex["mse"])) / 2, y + 18, f"bias² {num(b2, 0)}", size=8.5, fill=ACCENT, weight="600")
        s += dot(X(si["mse"]), y + 14, 3.6, fill=PAPER, stroke=INK)
        label = f"MSE {num(ex['mse'], 0)} · RMSE {num(ex['rmse'])}"
        if key == "minmse":
            label = f"MSE {num(ex['mse'], 0)} (bias² {num(b2, 0)}) · RMSE {num(ex['rmse'])}"
        s += mono(X(ex["mse"]) + 12, y + 18, label, size=8.5, fill=INK, anchor="start")
    ya = top + 4 * 56 - 8
    s += line(X(0), ya, X(8000), ya, stroke=RULE_SOLID)
    for v in range(0, 8001, 2000):
        s += line(X(v), ya, X(v), ya + 5, stroke=RULE_SOLID) + mono(X(v), ya + 18, f"{v:,}", size=8, fill=SOFT)
    s += mono(X(8000), ya + 34, "mean squared error, tanks²", size=8.5, fill=SOFT, anchor="end")
    r = T["mse_ratio_mle_mvue"]
    s += note_lines(x0, ya + 62, [
        (f"the MLE's MSE is {r['exact']:.2f} times the MVUE's, and {pct(EX['mle']['bias'] ** 2 / EX['mle']['mse'], 0)} of it is bias²; "
         f"2 × one tank − 1, also unbiased, has MSE {num(EX['first']['mse'], 0)}, off this scale", MUTED),
        (f"exact, from the distribution of the maximum; rings: simulated MSE, R = {T['R']:,} (MCSE at most "
         f"{max(SIM[k]['mse_mcse'] for k, _ in rows):.0f})", MUTED)])
    s += legend(vh - 22, vw, [("variance", "boxst:" + LINK + ":0.22"), ("bias²", "boxst:" + ACCENT + ":0.25"),
                              ("simulated MSE", "ring:" + INK + ":3.6")])
    return emit("03", "bias-variance-mse", "Mean squared error, split into bias² and variance",
                "Four estimators of the number of tanks, N = 342, from five captured serial numbers.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 470
    s = MARKS + eyebrow(32, 40, "german monthly tank production: intelligence, serial numbers and the records")
    ax = Axes(140, 104, 540, 290, (0, 3), (80, 3000), ymap=math.log10)
    s += ax.frame([], [100, 200, 500, 1000, 2000], ylab="tanks per month, log scale", yfmt=lambda v: f"{v:,}")
    for i, row in enumerate(T["ruggles_brodie"]):
        cx = ax.X(i + 0.5)
        s += mono(cx, ax.y0 + ax.h + 18, row["month"], size=9, fill=INK, weight="600")
        s += mono(cx, ax.y0 + ax.h + 32, f"serial numbers off by {row['serial_error']:+d}".replace("-", "−"), size=8,
                  fill=LINK)
        yi, ys, yr = ax.Y(row["intelligence"]), ax.Y(row["serial_number"]), ax.Y(row["records"])
        s += marker("square", cx, yi, 4.6, fill=MUTED)
        s += mono(cx + 10, yi + 3, f"{row['intelligence']:,} ({row['intelligence_ratio']:.1f}×)", size=8.5,
                  fill=MUTED, anchor="start")
        s += dot(cx - 14, ys, 4.4, fill=LINK)
        s += mono(cx - 24, ys + 3, f"{row['serial_number']}", size=8.5, fill=LINK, anchor="end", weight="600")
        s += marker("diamond", cx + 14, yr, 4.6, fill=ACCENT)
        s += mono(cx + 24, yr + 3, f"{row['records']}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    errs = [r["serial_error_pct"] for r in T["ruggles_brodie"]]
    ratios = [r["intelligence_ratio"] for r in T["ruggles_brodie"]]
    s += note_lines(730, 132, [("serial-number estimates", LINK),
                               (f"within {min(abs(e) for e in errs):.1f}% to {max(abs(e) for e in errs):.1f}%", MUTED),
                               ("of the German records", MUTED), ("", MUTED),
                               ("intelligence estimates", MUTED),
                               (f"{min(ratios):.1f} to {max(ratios):.1f} times the records", MUTED),
                               ("(in brackets: estimate ÷ records)", MUTED), ("", MUTED),
                               ("as reproduced by Simon (2024) and", SOFT),
                               ("by Miller, Sharma and Yang (2024)", SOFT),
                               ("from Ruggles and Brodie (1947)", SOFT)], gap=16)
    s += legend(vh - 22, vw, [("intelligence estimate", "mk:square:" + MUTED), ("serial-number estimate", "dot:" + LINK + ":4.4:1"),
                              ("German records", "mk:diamond:" + ACCENT)])
    return emit("04", "statistics-against-spies", "Serial numbers against conventional intelligence",
                "Monthly German tank production in three months, as published in 1947; the numbers, not a "
                "reproduction of any figure.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 590
    s = MARKS + eyebrow(32, 40, "rao–blackwell: average 2 × mean − 1 over the captures that share a maximum")
    ax = Axes(96, 104, 600, 380, (80, 350), (0, 720))
    s += ax.clip("c5")
    s += ax.frame([100, 150, 200, 250, 300, 342], [0, 200, 400, 600], ylab="2 × mean − 1 of the five serial numbers",
                  xfmt=str, yfmt=lambda v: f"{v:g}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "m, the largest of the five serial numbers", size=8.5, fill=SOFT, anchor="end")
    pts = "".join(dot(ax.X(m), ax.Y(v), 1.6, fill=LINK, op=0.35) for m, v in zip(RB["scatter_m"], RB["scatter_mom"]))
    rings = "".join(dot(ax.X(m), ax.Y(cm), 2.4, fill=PAPER, stroke=INK)
                    for j, (m, cm) in enumerate(zip(RB["m"], RB["cond_mean"])) if m % 5 == 2)
    ln = polyline([(ax.X(80), ax.Y(80 * (1 + 1 / K) - 1)), (ax.X(N), ax.Y(N * (1 + 1 / K) - 1))], INK, sw=1.6)
    s += f'<g clip-path="url(#c5)">{pts}{ln}{rings}</g>'
    s += line(ax.X(80), ax.Y(N), ax.X(350), ax.Y(N), stroke=ACCENT, sw=1.4, dash="4,3")
    i300 = RB["m"].index(300)
    c300, sd300 = RB["cond_mean"][i300], RB["cond_sd"][i300]
    xb = ax.X(300)                                     # the bracket stands exactly at m = 300
    s += line(xb, ax.Y(c300 - sd300), xb, ax.Y(c300 + sd300), stroke=INK, sw=1.4)
    s += line(xb - 5, ax.Y(c300 - sd300), xb + 5, ax.Y(c300 - sd300), stroke=INK, sw=1.4)
    s += line(xb - 5, ax.Y(c300 + sd300), xb + 5, ax.Y(c300 + sd300), stroke=INK, sw=1.4)
    v = T["var_ratio_mom_mvue"]
    ft = RB["fit"]
    s += note_lines(740, 128, [("conditioning on m replaces each", INK), ("vertical spread by its centre,", INK),
                               ("m(1 + 1/k) − 1: the MVUE", INK), ("", MUTED),
                               (f"bracket at m = 300: ± 1 SD = {sd300:.0f},", MUTED),
                               (f"centred on {c300:.1f}; the MVUE gives {300 * (1 + 1 / K) - 1:.0f}", MUTED), ("", MUTED),
                               (f"Var(2 × mean − 1) = {num(EX['mom']['var'], 0)}", MUTED),
                               (f"Var(MVUE) = {num(EX['mvue']['var'], 0)}", MUTED),
                               (f"ratio {v['exact']:.3f} = (k + 2)/3", MUTED),
                               (f"simulated {v['ratio']:.4f} ± {v['mcse']:.4f}", MUTED), ("", MUTED),
                               (f"means over {T['R']:,} captures:", MUTED),
                               (f"slope {ft['slope']:.4f} ± {ft['slope_se']:.4f},", MUTED),
                               (f"intercept {num(ft['intercept'], 2)} ± {ft['intercept_se']:.2f}", MUTED),
                               ("theory: 1.2 and −1", MUTED), ("", MUTED),
                               (f"true N = {N} (dashed)", ACCENT)], gap=16)
    s += legend(vh - 22, vw, [(f"{len(RB['scatter_m']):,} captures", "dot:" + LINK + ":1.6:0.35"),
                              ("mean of 2 × mean − 1 at that m", "ring:" + INK + ":2.4"),
                              ("MVUE m(1 + 1/k) − 1", "line:" + INK), ("true N", "dash:" + ACCENT)])
    return emit("05", "rao-blackwell", "Rao–Blackwell, drawn",
                "The unbiased but wasteful 2 × mean − 1 against the largest serial number, and its average at each "
                "value of the largest.", "best unbiased estimator", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 560
    s = MARKS + eyebrow(32, 40, f"error as the capture grows: root mean squared error against k, N = {N}")
    ax = Axes(96, 104, 600, 350, (1, 130), (1, 400), xmap=math.log10, ymap=math.log10)
    s += ax.clip("c6")
    s += ax.frame([1, 2, 5, 10, 20, 50, 100], [1, 3, 10, 30, 100, 300], ylab="RMSE, tanks (log scale)",
                  xfmt=str, yfmt=str, grid_x=False)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "k, tanks captured (log scale)", size=8.5, fill=SOFT, anchor="end")
    ks = C["ks"]
    series = [("mle", INK, None, 1.8), ("mvue", LINK, None, 1.8), ("mom", MUTED, "5,3", 1.6), ("first", SOFT, "2,3", 1.4)]
    body = ""
    for key, col, dash, sw in series:
        pts = [(ax.X(k), ax.Y(C["exact"][str(k)][key]["rmse"])) for k in ks if C["exact"][str(k)][key]["rmse"] > 0.5]
        body += polyline(pts, col, sw=sw, dash=dash)
        for k, row in C["sim"].items():
            body += dot(ax.X(int(k)), ax.Y(row[key]["rmse"]), 3.0, fill=col)
    s += f'<g clip-path="url(#c6)">{body}</g>'
    e10, e100 = C["exact"]["10"], C["exact"]["100"]
    s += note_lines(740, 128, [
        ("2 × one tank − 1: unbiased at every k,", SOFT), (f"RMSE {num(e100['first']['rmse'])} at every k", SOFT), ("", MUTED),
        ("MLE: biased at every k below N", INK), (f"(bias {num(EX['mle']['bias'])} at k = 5,", MUTED),
        (f"{num(e100['mle']['bias'], 2)} at k = 100), yet its error", MUTED), ("shrinks to zero", MUTED), ("", MUTED),
        (f"k = 10 to 100: MVUE error ÷ {e10['mvue']['rmse'] / e100['mvue']['rmse']:.1f},", LINK),
        (f"2 × mean − 1 ÷ {e10['mom']['rmse'] / e100['mom']['rmse']:.1f}: about 1/k against 1/√k", MUTED), ("", MUTED),
        (f"lines exact; dots simulated, R = {C['R']:,}", SOFT)], gap=16)
    s += legend(vh - 22, vw, [("MLE", "line:" + INK), ("MVUE", "line:" + LINK), ("2 × mean − 1", "dash:" + MUTED),
                              ("2 × one tank − 1", "dotted:" + SOFT), ("simulated", "dot:" + INK + ":3.0")])
    return emit("06", "consistency", "Unbiased is not consistent",
                f"Root mean squared error of four estimators of N = {N} as the number of captured tanks grows from "
                "1 to 100.", "consistency", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 560
    n = D["n"]
    s = MARKS + eyebrow(32, 40, f"estimating a variance from n = {n}: mean squared error of the sum of squares / d")
    ax = Axes(96, 104, 600, 340, (7, 30), (0, 1.0))
    s += ax.clip("c7")
    s += ax.frame([8, 10, 12, 14, 16, 18, 20, 24, 28], [0, 0.2, 0.4, 0.6, 0.8, 1.0], ylab="MSE, with σ² = 1",
                  xfmt=str, yfmt=lambda v: f"{v:.1f}")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "d, the divisor", size=8.5, fill=SOFT, anchor="end")
    for d, lab in ((n - 1, "n − 1"), (n, "n"), (n + 1, "n + 1")):
        s += line(ax.X(d), ax.y0, ax.X(d), ax.y0 + ax.h, stroke=RULE, sw=1.0)
        s += mono(ax.X(d), ax.y0 + ax.h - 8, lab, size=8, fill=SOFT)       # inside, above the axis, below every curve
    grid = D["grid"]
    cols = {"normal": INK, "uniform": MUTED, "exponential": LINK}
    body, best = "", ""
    for name, col in cols.items():
        pop = POP[name]
        dash, sw = ("5,3", 1.4) if name == "uniform" else (None, 1.8)
        body += polyline([(ax.X(d), ax.Y(m)) for d, m in zip(grid, pop["curve_exact"])], col, sw=sw, dash=dash)
        for key in ("n-1", "n", "n+1"):
            a = pop["at"][key]
            body += dot(ax.X(a["d"]), ax.Y(a["mse"]), 3.4, fill=PAPER, stroke=col)
        b = pop["at"]["best"]
        best += dot(ax.X(b["d"]), ax.Y(b["mse_exact"]), 3.8, fill=ACCENT)
    s += f'<g clip-path="url(#c7)">{body}{best}</g>'
    pe, pu, pn = POP["exponential"], POP["uniform"], POP["normal"]
    s += mono(ax.X(pe["best_d_theory"]), ax.Y(pe["at"]["best"]["mse_exact"]) - 14, f"best {pe['best_d_theory']:.1f}",
              size=8, fill=ACCENT, weight="600")
    s += note_lines(740, 128, [
        ("normal (κ = 0): best d = n + 1", INK),
        (f"MSE {pn['at']['n+1']['mse_exact']:.4f} against {pn['at']['n-1']['mse_exact']:.4f} at n − 1,", MUTED),
        (f"{pct(1 - 1 / pn['mse_ratio_nm1_np1']['exact'], 0)} lower", MUTED), ("", MUTED),
        (f"uniform (κ = −1.2): best d = {pu['best_d_theory']:.2f}", MUTED),
        (f"n − 1 and n + 1 within {pct(pu['mse_ratio_nm1_np1']['exact'] - 1, 1)}", MUTED), ("", MUTED),
        (f"exponential (κ = 6): best d = {pe['best_d_theory']:.1f}", LINK),
        (f"MSE {pct(1 - pe['mse_ratio_best_nm1']['exact'], 0)} below n − 1's", MUTED), ("", MUTED),
        ("best d = n + 1 + (n − 1)κ/n", INK), ("", MUTED),
        ("every curve's n − 1 estimate is unbiased:", SOFT),
        ("simulated means " + ", ".join(format(POP[q]["mean_s2_unbiased"], ".4f") for q in cols), SOFT)], gap=16)
    s += legend(vh - 22, vw, [("normal", "line:" + INK), ("uniform", "dash:" + MUTED), ("exponential", "line:" + LINK),
                              (f"simulated, R = {D['R']:,}", "ring:" + INK + ":3.4"), ("best divisor", "dot:" + ACCENT + ":3.8:1")])
    return emit("07", "variance-divisors", "The best divisor depends on the tails",
                f"Exact mean squared error of the sum of squares divided by d, for samples of {n} from three "
                "unit-variance populations, with simulated checks at n − 1, n and n + 1.", "divisors", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 610
    s = MARKS + eyebrow(32, 40, "efron and morris's 18 batters, 1970: first 45 at-bats against the rest of the season")
    ax = Axes(96, 104, 600, 386, (0.14, 0.42), (0.18, 0.36))
    s += ax.clip("c8")
    s += ax.frame([0.15, 0.20, 0.25, 0.30, 0.35, 0.40], [0.20, 0.25, 0.30, 0.35], ylab="batting average, rest of the season",
                  xfmt=lambda v: f"{v:.2f}".lstrip("0"), yfmt=lambda v: f"{v:.2f}".lstrip("0"))
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "batting average, first 45 at-bats", size=8.5, fill=SOFT, anchor="end")
    y, p, z = B["y"], B["p"], RAW["z"]
    ybar, c = RAW["ybar"], RAW["c"]
    xs = (0.14, 0.42)
    body = polyline([(ax.X(x), ax.Y(x)) for x in xs], SOFT, sw=1.2, dash="2,3")
    body += polyline([(ax.X(x), ax.Y(REG["intercept"] + REG["slope"] * x)) for x in xs], MUTED, sw=1.4, dash="5,3")
    body += polyline([(ax.X(x), ax.Y(ybar + c * (x - ybar))) for x in xs], LINK, sw=2.0)
    for yi, pi in zip(y, p):
        body += dot(ax.X(yi), ax.Y(pi), 3.6, fill=INK)
    s += f'<g clip-path="url(#c8)">{body}</g>'
    names = B["players"]
    for nm, dx, dy, anc in (("Clemente", -8, -8, "end"), ("Munson", 8, -6, "start"), ("Alvis", 8, 4, "start")):
        i = names.index(nm)
        s += mono(ax.X(y[i]) + dx, ax.Y(p[i]) + dy, f"{nm} {y[i]:.3f}".replace("0.", "."), size=8, fill=INK, anchor=anc)
    s += note_lines(740, 128, [
        (f"grand average {ybar:.3f}", INK),
        (f"shrinking factor c = {c:.3f}: each average", LINK), (f"moves {pct(1 - c, 0)} of the way to {ybar:.3f}", LINK), ("", MUTED),
        (f"Clemente {y[0]:.3f} → {z[0]:.3f}; rest {p[0]:.3f}", MUTED),
        (f"Munson {y[16]:.3f} → {z[16]:.3f}; rest {p[16]:.3f}", MUTED), ("", MUTED),
        ("total squared error against the rest", INK), (f"of the season: averages {RAW['tse_y']:.4f},", MUTED),
        (f"James–Stein {RAW['tse_z']:.4f}", LINK), ("", MUTED),
        (f"with hindsight, least squares across the", MUTED), (f"18 gives slope {REG['slope']:.3f}", MUTED), ("", MUTED),
        ("Unser and Petrocelli share one point,", SOFT), (".222 and .264", SOFT)], gap=16)
    s += legend(vh - 22, vw, [("player", "dot:" + INK + ":3.6:1"), ("own average, slope 1", "dotted:" + SOFT),
                              (f"James–Stein, slope {c:.3f}", "line:" + LINK),
                              (f"least squares with hindsight, slope {REG['slope']:.3f}", "dash:" + MUTED)])
    return emit("08", "shrinkage-as-regression", "James–Stein as regression toward the mean",
                "Each player's average over his first 45 at-bats of 1970 against his average for the rest of the "
                "season, from Efron and Morris's 1975 table, with three prediction lines.", "stein's paradox", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 590
    s = MARKS + eyebrow(32, 40, "each player's squared error, predicting the rest of 1970: own average against james–stein")
    names, y, p, z = B["players"], B["y"], B["p"], RAW["z"]
    x0, wpx, top, rh = 210, 520, 112, 22
    X = lambda v: x0 + v / 0.020 * wpx
    worse = set(RAW["worse"])
    for i, nm in enumerate(names):
        yy = top + i * rh
        ea, ej = (y[i] - p[i]) ** 2, (z[i] - p[i]) ** 2
        col = ACCENT if nm in worse else LINK
        s += line(x0, yy, x0 + wpx, yy, stroke=RULE, sw=0.8)
        s += mono(x0 - 12, yy + 3, f"{nm}  {y[i]:.3f}".replace("0.", "."), size=8.5, fill=INK, anchor="end")
        s += line(X(ea), yy, X(ej), yy, stroke=col, sw=1.4)
        s += dot(X(ea), yy, 3.6, fill=PAPER, stroke=INK)
        s += dot(X(ej), yy, 3.6, fill=col)
    ya = top + len(names) * rh - 6
    s += line(x0, ya, x0 + wpx, ya, stroke=RULE_SOLID)
    for v in (0, 0.005, 0.010, 0.015, 0.020):
        s += line(X(v), ya, X(v), ya + 5, stroke=RULE_SOLID) + mono(X(v), ya + 18, f"{v:.3f}".lstrip("0") if v else "0", size=8, fill=SOFT)
    s += mono(x0 + wpx, ya + 34, "squared error against the rest-of-season average", size=8.5, fill=SOFT, anchor="end")
    s += mono(x0 - 12, top - 16, "player, first-45 average", size=8, fill=SOFT, anchor="end")
    s += note_lines(770, 134, [(f"James–Stein closer for {RAW['closer']} of 18", LINK),
                               (f"further for {' and '.join(RAW['worse'])}", ACCENT), ("", MUTED),
                               ("totals:", INK), (f"own averages {RAW['tse_y']:.4f}", MUTED),
                               (f"James–Stein {RAW['tse_z']:.4f}", LINK),
                               (f"ratio {RAW['ratio']:.2f}", INK), ("", MUTED),
                               ("the 1977 article prints", SOFT), ("0.077 and 0.022, ratio 3.5", SOFT)], gap=16)
    s += legend(vh - 22, vw, [("own average", "ring:" + INK + ":3.6"), ("James–Stein, closer", "dot:" + LINK + ":3.6:1"),
                              ("James–Stein, further", "dot:" + ACCENT + ":3.6:1")])
    return emit("09", "per-player-errors", "Where the 3.5 comes from",
                "Squared prediction error for each of the 18 batters, from Efron and Morris's 1975 table, with "
                "James–Stein computed by the 1977 article's raw-scale rule.", "stein's paradox", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 520
    reps = REP["R"]
    s = MARKS + eyebrow(32, 40, f"1970 replayed {reps:,} times: total squared error of the averages ÷ that of james–stein")
    edges, counts = REP["ratio_hist_edges"], REP["ratio_hist"]
    xmax = 8.0
    shown = [(edges[j], edges[j + 1], c) for j, c in enumerate(counts) if edges[j + 1] <= xmax + 1e-9]
    beyond = sum(c for j, c in enumerate(counts) if edges[j] >= xmax - 1e-9)
    ymax = max(100 * c / reps for _, _, c in shown) * 1.15
    ax = Axes(96, 104, 600, 300, (0, xmax), (0, ymax))
    s += ax.clip("c10")
    s += ax.frame(list(range(0, 9)), list(range(0, int(ymax) + 1)), ylab="share of seasons per 0.1",
                  xfmt=str, yfmt=lambda v: f"{v:g}%")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "ratio of total squared errors, averages ÷ James–Stein", size=8.5,
              fill=SOFT, anchor="end")
    bars = "".join(rect(ax.X(a), ax.Y(100 * c / reps), ax.X(b) - ax.X(a), ax.Y(0) - ax.Y(100 * c / reps),
                        fill=BAR_FILL, op=BAR_OP, stroke="none", sw=0) for a, b, c in shown if c)
    s += f'<g clip-path="url(#c10)">{bars}</g>'
    q = REP["ratio_quantiles"]
    s += line(ax.X(1), ax.y0, ax.X(1), ax.y0 + ax.h, stroke=INK, sw=1.2, dash="4,3")
    s += line(ax.X(q["0.5"]), ax.y0, ax.X(q["0.5"]), ax.y0 + ax.h, stroke=MUTED, sw=1.2, dash="2,3")
    s += line(ax.X(RAW["ratio"]), ax.y0, ax.X(RAW["ratio"]), ax.y0 + ax.h, stroke=ACCENT, sw=1.8)
    s += mono(ax.X(1) - 6, ax.y0 + 12, "break-even", size=8, fill=INK, anchor="end")
    s += mono(ax.X(RAW["ratio"]) + 6, ax.y0 + 12, f"1970: {RAW['ratio']:.2f}", size=8.5, fill=ACCENT, anchor="start", weight="600")
    e, ep = REP["efficiency_raw"], REP["efficiency_positive_part"]
    s += note_lines(740, 128, [
        (f"James–Stein has the smaller total", LINK), (f"in {pct(REP['share_js_wins'])} of seasons", LINK), ("", MUTED),
        (f"median ratio {q['0.5']:.2f}; 90% of seasons", MUTED), (f"between {q['0.05']:.2f} and {q['0.95']:.2f}", MUTED),
        (f"{pct(REP['share_ratio_ge_observed'])} reach 1970's {RAW['ratio']:.2f}", ACCENT), ("", MUTED),
        (f"mean totals: {REP['mean_tse_y']:.4f} against {REP['mean_tse_z']:.4f},", MUTED),
        (f"ratio {e['ratio']:.3f} ± {e['mcse']:.3f}", INK), (f"(positive part {ep['ratio']:.3f} ± {ep['mcse']:.3f})", MUTED), ("", MUTED),
        ("true averages: each player's", SOFT), ("rest-of-season average", SOFT),
        (f"{pct(beyond / reps, 2)} of ratios beyond {xmax:.0f}, not shown", SOFT)], gap=16)
    s += legend(vh - 22, vw, [("replayed seasons", "barflat"), ("break-even", "dash:" + INK), ("median", "dotted:" + MUTED),
                              ("1970 as it happened", "line:" + ACCENT)])
    return emit("10", "replayed-seasons", "1970, replayed",
                f"{reps:,} simulated seasons of 45 at-bats per player, each player's true average set to his "
                "rest-of-season average; the lab's binomial simulation.", "how much shrinking gains", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 560
    k = S["k"]
    s = MARKS + eyebrow(32, 40, f"total risk for k = {k} normal means with unit variance, against the spread of the true means")
    ax = Axes(96, 104, 600, 330, (0, 300), (0, 20), xmap=math.sqrt)
    s += ax.clip("c11")
    s += ax.frame([0, 1, 4, 16, 64, 256], [0, 3, 6, 9, 12, 15, 18], ylab="expected total squared error (risk)",
                  xfmt=str, yfmt=str, grid_x=False)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 32, "spread of the true means, Σ(θ − θ̄)², square-root scale", size=8.5,
              fill=SOFT, anchor="end")
    body = line(ax.X(0), ax.Y(k), ax.X(300), ax.Y(k), stroke=INK, sw=1.6)
    body += polyline([(ax.X(sp), ax.Y(r)) for sp, r in zip(S["curve_spread"], S["curve_exact"]) if sp <= 300], LINK, sw=1.8)
    pts = ""                                           # points are drawn unclipped, so the spread-0 pair stays whole
    for pt in S["points"]:
        if pt["spread"] <= 300:
            pts += dot(ax.X(pt["spread"]), ax.Y(pt["js_plus"]), 3.2, fill=PAPER, stroke=MUTED)
            pts += dot(ax.X(pt["spread"]), ax.Y(pt["js"]), 3.0, fill=LINK)
    s += f'<g clip-path="url(#c11)">{body}</g>{pts}'
    bb = S["points"][-1]
    s += line(ax.X(bb["spread"]), ax.y0, ax.X(bb["spread"]), ax.y0 + ax.h, stroke=ACCENT, sw=1.4, dash="4,3")
    s += mono(ax.X(bb["spread"]) + 8, ax.Y(1.2), f"18 batters: spread {bb['spread']:.2f}", size=8.5, fill=ACCENT,
              anchor="start", weight="600")                # below every curve and point: no plate needed
    p0 = S["points"][0]
    far = [pt for pt in S["points"] if pt["spread"] == 256][0]
    s += note_lines(740, 128, [
        (f"separate averages: {k} at every spread", INK), ("", MUTED),
        ("James–Stein toward the grand mean:", LINK),
        (f"{p0['exact']:.0f} when all true means are equal", MUTED), (f"({p0['efficiency_exact']:.0f} times better)", MUTED),
        (f"{bb['exact']:.2f} at the batters' spread", ACCENT), (f"({bb['efficiency_exact']:.2f} times better)", ACCENT),
        (f"{far['exact']:.2f} at spread 256 ({far['efficiency_exact']:.2f} times)", MUTED), ("", MUTED),
        (f"never above {k}: James and Stein (1961)", INK), ("", MUTED),
        ("positive part: lower still where the", MUTED), ("spread is small", MUTED), ("", MUTED),
        (f"curve exact; points simulated, R = {S['R']:,}", SOFT)], gap=16)
    s += legend(vh - 22, vw, [("separate averages", "line:" + INK), ("James–Stein, exact", "line:" + LINK),
                              ("simulated", "dot:" + LINK + ":3.0:1"), ("positive part, simulated", "ring:" + MUTED + ":3.2"),
                              ("the batters' spread", "dash:" + ACCENT)])
    return emit("11", "stein-risk", "How much shrinking gains",
                f"Exact risk of James–Stein toward the grand mean for {k} unit-variance normal means, with the lab's "
                "simulated checks.", "how much shrinking gains", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
