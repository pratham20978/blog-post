#!/usr/bin/env python3
"""Figures 01-13 for likelihood-mle-fisher-information.

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/likelihood.py.
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
P, NB, B, TK, PL = (CAP[k] for k in ("poisson", "nb", "boundary", "tank", "powerlaw"))
V1, CORPS = P["v1"], P["corps"]
XI = CORPS["all"]["XI"]
S_V1, N_V1, LAM = V1["total"], V1["n"], V1["lam_hat"]
LAM0 = 0.85
ST = V1["nulls"]["0.85"]
WALD_C, SCORE_C, LR_C = LINK, ACCENT, INK            # one colour per statistic, in every figure that shows them

# The numbers the article prints, held to the capture.
assert (S_V1, N_V1) == (537, 576) and round(LAM, 4) == 0.9323 and round(V1["se"], 4) == 0.0402
assert round(V1["obs_info"], 1) == 617.8 and round(V1["exp_info"], 1) == 617.8
assert (round(ST["wald"], 2), round(ST["score"], 2), round(ST["lr"], 2)) == (4.18, 4.59, 4.45)
assert (XI["total"], XI["n"], round(CORPS["null_rate"], 2)) == (25, 20, 0.61)
assert (round(XI["wald"], 2), round(XI["score"], 2), round(XI["lr"], 2)) == (6.55, 13.43, 10.27)
assert round(min(P["wald_scale"]["corps"]), 2) == 3.63 and round(max(P["wald_scale"]["corps"]), 1) == 27.5
assert round(NB["k_hat"], 3) == 0.865 and round(NB["k_mom"], 3) == 0.955 and round(NB["ybar"], 4) == 0.4652
assert [round(v, 3) for v in NB["intervals_k"]["profile"]] == [0.585, 1.383]
assert [round(v, 3) for v in NB["intervals_k"]["wald_obs"]] == [0.500, 1.230]
assert round(NB["se_obs"][1], 4) == 0.1863 and round(NB["se_exp"][1], 4) == 0.1839
assert round(NB["dispersion"]["d_hat"], 3) == 1.538 and round(NB["dispersion"]["se_delta"], 3) == 0.122
assert round(100 * NB["k_sampling"]["above_wald"], 2) == 7.47 and round(100 * NB["k_sampling"]["below_wald"], 2) == 0.14
assert round(B["v1"]["lr"], 2) == 0.41 and round(B["v1"]["alpha_hat"], 3) == 0.040
NBV, NIN = B["null_boundary"]["v1"], B["null_interior"]
assert round(100 * NBV["p_zero"], 1) == 52.6 and round(100 * NBV["p_gt_3841"], 2) == 2.17
assert round(100 * NBV["p_gt_2706"], 2) == 4.40 and round(100 * NIN["p_gt_3841"], 2) == 5.01
assert TK["m"] == 303 and round(TK["first_difference"], 4) == -0.0166
assert round(PL["by_threshold"][2]["z"], 2) == 2.29 and round(PL["by_threshold"][2]["p"], 3) == 0.022
assert PL["ks"]["n_tail"] == 509 and round(PL["ks"]["p"], 2) == 0.20


# ------------------------------------------------------------------ drawing helpers (Part 3's set)
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
    <marker id="aw" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{WALD_C}"/></marker>
    <marker id="aw0" markerWidth="8" markerHeight="6" refX="1" refY="3" orient="auto-start-reverse"><polygon points="0 0, 8 3, 0 6" fill="{WALD_C}"/></marker>
    <marker id="ai" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{INK}"/></marker>
    <marker id="ai0" markerWidth="8" markerHeight="6" refX="1" refY="3" orient="auto-start-reverse"><polygon points="0 0, 8 3, 0 6" fill="{INK}"/></marker>
  </defs>"""


def double_h(x1, x2, y, colour, marker):
    """A horizontal span with an arrowhead at each end, for a distance on the parameter axis."""
    return (f'<line x1="{x1:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y:.1f}" stroke="{colour}" stroke-width="1.6" '
            f'marker-start="url(#{marker}0)" marker-end="url(#{marker})"/>')


def double_v(x, y1, y2, colour, marker):
    return (f'<line x1="{x:.1f}" y1="{y1:.1f}" x2="{x:.1f}" y2="{y2:.1f}" stroke="{colour}" stroke-width="1.6" '
            f'marker-start="url(#{marker}0)" marker-end="url(#{marker})"/>')


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
    """Legend whose swatches are drawn exactly like this post's marks (colour, size, opacity, stroke)."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, kind in items:
        part = kind.split(":")
        if part[0] == "band":
            s += rect(x, y - 1, 16, 12, fill=part[1], op=float(part[2]), stroke="none", sw=0)
        elif part[0] == "boxst":
            s += rect(x, y - 1, 16, 12, fill=part[1], op=float(part[2]), stroke=part[1], sw=1.0)
        elif part[0] == "line":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=float(part[2]) if len(part) > 2 else 2.0)
        elif part[0] == "dash":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.4, dash="5,3")
        elif part[0] == "dotted":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.4, dash="1.5,2.5")
        elif part[0] == "dot":
            s += dot(x + 8, y + 5, float(part[2]), fill=part[1], op=float(part[3]) if len(part) > 3 else None)
        elif part[0] == "ring":
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1])
        elif part[0] == "span":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=3.0)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 26
    return s


def num(v, nd=1):
    """A number with thousands separators and a true minus sign."""
    return f"{v:,.{nd}f}".replace("-", "−")


def pct(v, nd=1):
    return f"{100 * v:.{nd}f}%"


def pois_ll(total, n, lam, lam_hat):
    """Poisson log-likelihood relative to its maximum."""
    return total * math.log(lam / lam_hat) - n * (lam - lam_hat)


def curve(ax, xs, ys):
    return [(ax.X(a), ax.Y(b)) for a, b in zip(xs, ys)]


def normal_pdf(x, mu, sd):
    return math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def chi2_sf1(x):
    return math.erfc(math.sqrt(x / 2)) if x > 0 else 1.0


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 588
    cv = V1["curve"]
    info, se = V1["obs_info"], V1["se"]
    s = MARKS + eyebrow(32, 40, f"Clarke's {N_V1} squares and {S_V1} hits: the Poisson log-likelihood for the rate, and its slope")
    a = Axes(96, 104, 560, 190, (0.787, 1.077), (-7.6, 0.6))
    s += a.clip("c1a") + title(a.x0, a.y0 - 16, "log-likelihood l(λ), minus its maximum")
    s += a.frame([], [-6, -4, -2, 0], yfmt=lambda v: num(v, 0))
    cut = -0.5 * 1.959964 ** 2
    inner = (line(a.x0, a.Y(cut), a.x0 + a.w, a.Y(cut), stroke=SOFT, sw=0.8, dash="2,3")
             + polyline(curve(a, cv["lam"], cv["quad"]), LINK, sw=1.4, dash="5,3")
             + polyline(curve(a, cv["lam"], cv["ll"]), INK, sw=2.0))
    s += f'<g clip-path="url(#c1a)">{inner}</g>'
    s += line(a.X(LAM), a.y0 + 22, a.X(LAM), a.y0 + a.h, stroke=ACCENT, sw=1.2, dash="4,3")
    s += plate(a.X(LAM), a.y0 + 12, f"MLE {S_V1}/{N_V1} = {LAM:.4f}", fill=ACCENT, weight="600")
    lo, hi = LAM - 1.959964 * se, LAM + 1.959964 * se
    s += dot(a.X(lo), a.Y(cut), 3.0, fill=LINK) + dot(a.X(hi), a.Y(cut), 3.0, fill=LINK)
    s += plate(a.X(0.927), a.Y(-2.45), "−1.92 = −1.96²/2", fill=SOFT, anchor="end")
    s += plate(a.X(0.815), a.Y(-6.55), "steeper than the quadratic", fill=INK, anchor="start")
    s += plate(a.X(1.015), a.Y(-3.5), "flatter on the right", fill=INK, anchor="end")
    s += note_lines(694, a.y0 + 14, [
        ("the peak is the MLE:", MUTED), (f"{S_V1}/{N_V1} = {LAM:.4f} hits per square", INK), ("", INK),
        ("how sharply it falls is the information:", MUTED),
        (f"observed: −l″ at the MLE = {S_V1}/{LAM:.4f}² = {info:.1f}", INK),
        (f"expected: {N_V1}/{LAM:.4f} = {V1['exp_info']:.1f}, the same here", INK), ("", INK),
        (f"SE = 1/√{info:.1f} = {se:.4f}", ACCENT),
        (f"dashed: the quadratic −{info:.1f} (λ − {LAM:.4f})² / 2", LINK)])
    b = Axes(96, 360, 560, 140, (0.787, 1.077), (-90, 115))
    s += b.clip("c1b") + title(b.x0, b.y0 - 16, f"score U(λ) = {S_V1}/λ − {N_V1}, the slope of the curve above")
    s += b.frame([0.80, 0.85, 0.90, 0.95, 1.00, 1.05], [-80, -40, 0, 40, 80], xlab="rate λ, hits per square",
                 xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: num(v, 0))
    tangent = [(x, -info * (x - LAM)) for x in (0.787, 1.077)]
    inner = (line(b.x0, b.Y(0), b.x0 + b.w, b.Y(0), stroke=RULE_SOLID, sw=1.0)
             + polyline([(b.X(x), b.Y(y)) for x, y in tangent], LINK, sw=1.4, dash="5,3")
             + polyline(curve(b, cv["lam"], cv["score"]), INK, sw=2.0))
    s += f'<g clip-path="url(#c1b)">{inner}</g>'
    s += line(b.X(LAM), b.y0, b.X(LAM), b.y0 + b.h, stroke=ACCENT, sw=1.2, dash="4,3")
    s += dot(b.X(LAM), b.Y(0), 3.6, fill=ACCENT)
    s += note_lines(694, b.y0 + 14, [("the score is zero at the MLE", INK),
                                     (f"its slope there is −{info:.1f}:", MUTED),
                                     ("the same information", MUTED),
                                     (f"dashed: the tangent −{info:.1f} (λ − {LAM:.4f})", LINK)])
    s += legend(vh - 24, vw, [("log-likelihood and score", "line:" + INK), ("quadratic and tangent, curvature 617.8", "dash:" + LINK),
                              ("MLE", "dash:" + ACCENT), ("MLE ± 1.96 SE", "dot:" + LINK + ":3.0")])
    return emit("01", "likelihood-and-score", "The likelihood of Clarke's V-1 counts",
                "The Poisson log-likelihood for the rate of hits per square, its quadratic approximation, and the score, "
                "computed by the lab from Clarke's 1946 table.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02 and 03: the three distances
def three_distances(ax, total, n, lam_hat, lam0, info_hat, cid, lam_range, tan, lr_dx, wald_y, quad=False):
    lo, hi = lam_range
    xs = [lo + (hi - lo) * i / 400 for i in range(401)]
    ys = [pois_ll(total, n, x, lam_hat) for x in xs]
    drop = pois_ll(total, n, lam0, lam_hat)
    slope = total / lam0 - n
    s = ax.clip(cid)
    inner = polyline(curve(ax, xs, ys), INK, sw=2.0)
    if quad:
        inner = polyline([(ax.X(x), ax.Y(-0.5 * info_hat * (x - lam_hat) ** 2)) for x in xs], LINK, sw=1.3, dash="5,3") + inner
    t0, t1 = lam0 - tan[0], lam0 + tan[1]
    inner += line(ax.X(t0), ax.Y(drop + slope * (t0 - lam0)), ax.X(t1), ax.Y(drop + slope * (t1 - lam0)), stroke=SCORE_C, sw=1.8)
    s += f'<g clip-path="url(#{cid})">{inner}</g>'
    s += line(ax.X(lam0), ax.Y(drop), ax.X(lam0), ax.y0 + ax.h, stroke=SOFT, sw=0.8, dash="2,3")
    s += line(ax.X(lam_hat), ax.Y(0), ax.X(lam_hat), ax.y0 + ax.h, stroke=SOFT, sw=0.8, dash="2,3")
    s += double_v(ax.X(lam0) - lr_dx, ax.Y(0) + 2, ax.Y(drop) - 2, LR_C, "ai")
    s += line(ax.X(lam0) - lr_dx - 8, ax.Y(0), ax.X(lam0) - 2, ax.Y(0), stroke=LR_C, sw=0.8)
    s += line(ax.X(lam0) - lr_dx - 8, ax.Y(drop), ax.X(lam0) - 4, ax.Y(drop), stroke=LR_C, sw=0.8)
    s += double_h(ax.X(lam0) + 2, ax.X(lam_hat) - 2, ax.Y(wald_y), WALD_C, "aw")
    s += dot(ax.X(lam_hat), ax.Y(0), 4.0, fill=INK) + dot(ax.X(lam0), ax.Y(drop), 4.0, fill=SCORE_C)
    return s, drop, slope


def fig02():
    vw, vh = 1016, 500
    info0 = N_V1 / LAM0
    s = MARKS + eyebrow(32, 40, f"three ways to measure how far the null value {LAM0} sits from the MLE {LAM:.4f}, on Clarke's curve")
    ax = Axes(96, 100, 560, 300, (0.818, 0.952), (-3.3, 0.45))
    s += title(ax.x0, ax.y0 - 16, "log-likelihood l(λ), minus its maximum")
    s += ax.frame([0.82, 0.84, 0.86, 0.88, 0.90, 0.92, 0.94], [-3, -2, -1, 0], xlab="rate λ, hits per square",
                  xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: num(v, 0))
    body, drop, slope = three_distances(ax, S_V1, N_V1, LAM, LAM0, V1["obs_info"], "c2", (0.818, 0.952),
                                        (0.012, 0.034), 26, 0.2)
    s += body
    s += plate(ax.X(LAM0), ax.y0 + ax.h - 8, f"λ₀ = {LAM0}", fill=MUTED)
    s += plate(ax.X(LAM), ax.y0 + ax.h - 8, f"MLE {LAM:.4f}", fill=MUTED)
    s += plate((ax.X(LAM0) + ax.X(LAM)) / 2, ax.Y(0.2) - 8, f"gap {LAM - LAM0:.4f}", fill=WALD_C, weight="600")
    s += plate(ax.X(LAM0) - 34, ax.Y(-1.25), f"drop {-drop:.3f}", fill=LR_C, anchor="end", weight="600")
    top = LAM0 + 0.034
    s += plate(ax.X(top), ax.Y(drop + slope * 0.034) - 10, f"slope {slope:.2f}", fill=SCORE_C, weight="600")
    s += note_lines(690, ax.y0 + 20, [
        ("Wald: the gap squared, times", WALD_C), ("the curvature at the MLE", MUTED),
        (f"{LAM - LAM0:.4f}² × {V1['obs_info']:.1f} = {ST['wald']:.2f}", WALD_C), ("", INK),
        ("likelihood ratio: twice the drop", LR_C), (f"2 × {-drop:.4f} = {ST['lr']:.2f}", LR_C), ("", INK),
        ("score: the slope at λ₀ squared, over", SCORE_C), (f"the information at λ₀, {N_V1}/{LAM0}", MUTED),
        (f"{slope:.2f}² / {info0:.1f} = {ST['score']:.2f}", SCORE_C), ("", INK),
        ("p against χ²₁: Wald / LR / score", MUTED),
        (" / ".join(f"{ST['p'][k]:.3f}" for k in ("wald", "lr", "score")), MUTED), ("", INK),
        ("all three within 10% of each other", INK)], gap=16)
    s += legend(vh - 24, vw, [("log-likelihood; twice its drop is the LR", "line:" + INK),
                              ("Wald: the horizontal gap", "line:" + WALD_C), ("score: the slope at λ₀", "line:" + SCORE_C)])
    return emit("02", "three-distances", "Three distances on one curve",
                f"The Wald, likelihood-ratio and score statistics for H0: λ = {LAM0}, read off the log-likelihood of "
                "Clarke's counts, computed by the lab.", "worked example", vw, vh, s)


def fig03():
    vw, vh = 1016, 500
    lam0, tot, n = CORPS["null_rate"], XI["total"], XI["n"]
    lam_hat = tot / n
    info_hat, info0 = n / lam_hat, n / lam0
    s = MARKS + eyebrow(32, 40, f"corps XI: {tot} deaths in {n} years, against the regular corps' rate of {lam0:.2f}")
    ax = Axes(96, 100, 560, 300, (0.25, 2.25), (-9.3, 0.9))
    s += title(ax.x0, ax.y0 - 16, "log-likelihood l(λ), minus its maximum")
    s += ax.frame([0.5, 1.0, 1.5, 2.0], [-8, -6, -4, -2, 0], xlab="deaths per corps-year, λ",
                  xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: num(v, 0))
    body, drop, slope = three_distances(ax, tot, n, lam_hat, lam0, info_hat, "c3", (0.25, 2.25), (0.12, 0.22), 60, 0.42,
                                        quad=True)
    s += body
    qd = -0.5 * info_hat * (lam0 - lam_hat) ** 2
    s += dot(ax.X(lam0), ax.Y(qd), 3.4, fill=LINK)
    s += plate(ax.X(lam0) - 6, ax.Y(qd + 0.55), f"{qd:.2f}".replace("-", "−"), fill=LINK, anchor="end", weight="600")
    s += plate(ax.X(lam0) + 8, ax.Y(drop) + 18, f"{drop:.2f}".replace("-", "−"), fill=INK, anchor="start", weight="600")
    s += plate(ax.X(lam0), ax.y0 + ax.h - 8, f"λ₀ = {lam0:.2f}", fill=MUTED)
    s += plate(ax.X(lam_hat), ax.y0 + ax.h - 8, f"MLE {lam_hat:.2f}", fill=MUTED)
    s += plate((ax.X(lam0) + ax.X(lam_hat)) / 2, ax.Y(0.42) - 8, f"gap {lam_hat - lam0:.2f}", fill=WALD_C, weight="600")
    s += note_lines(ax.X(1.33), ax.Y(-6.9), [("dashed: the quadratic Wald assumes,", LINK),
                                             (f"curvature {n}/{lam_hat:.2f} = {info_hat:.0f} at the MLE", LINK)], gap=15)
    s += note_lines(690, ax.y0 + 20, [
        ("Wald: gap² × information at the MLE", WALD_C), (f"{lam_hat - lam0:.2f}² × {n}/{lam_hat:.2f} = {XI['wald']:.2f}", WALD_C),
        (f"= twice the quadratic's drop, 2 × {-qd:.2f}", MUTED), ("", INK),
        ("likelihood ratio: twice the curve's drop", LR_C), (f"2 × {-drop:.3f} = {XI['lr']:.2f}", LR_C), ("", INK),
        ("score: slope² / information at λ₀", SCORE_C), (f"{slope:.2f}² / ({n}/{lam0:.2f}) = {XI['score']:.2f}", SCORE_C), ("", INK),
        ("the curve falls faster to the left", MUTED), ("than the quadratic Wald assumes:", MUTED),
        ("Wald sees the least distance,", MUTED), ("the score test the most", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("log-likelihood; twice its drop is the LR", "line:" + INK),
                              ("Wald: the gap, and its quadratic", "dash:" + WALD_C), ("score: the slope at λ₀", "line:" + SCORE_C)])
    return emit("03", "small-sample-geometry", "The same three distances on 20 years",
                "Bortkiewicz's corps XI against the rate of the ten corps he kept, taken as known; the lab's computation.",
                "when the three tests disagree", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 470
    sz = P["sizes"]
    ms = sz["m"]
    s = MARKS + eyebrow(32, 40, "how often each nominal 5% test rejects a true null rate, computed exactly")
    ax = Axes(96, 96, 620, 280, (0.5, 2000), (0, 0.20), xmap=math.log10)
    s += ax.clip("c4") + title(ax.x0, ax.y0 - 16, "exact probability of rejecting a true H0")
    s += ax.frame([0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000], [0, 0.05, 0.10, 0.15, 0.20],
                  xlab="expected total count under H0, m = nλ₀ (log scale)", xfmt=lambda v: f"{v:g}",
                  yfmt=lambda v: f"{100 * v:.0f}%")
    inner = line(ax.x0, ax.Y(0.05), ax.x0 + ax.w, ax.Y(0.05), stroke=SOFT, sw=1.0, dash="4,3")
    for key, col in (("wald", WALD_C), ("lr", LR_C), ("score", SCORE_C)):
        inner += polyline(curve(ax, ms, sz[key]), col, sw=1.5)
    s += f'<g clip-path="url(#c4)">{inner}</g>'
    big = max(zip(sz["wald"], ms))
    s += note_lines(ax.X(0.55), ax.Y(0.187), [("Wald > 20%", WALD_C), (f"({pct(big[0], 0)} at {big[1]:g})", WALD_C)], gap=14)
    j_xi = min(range(len(ms)), key=lambda j: abs(ms[j] - XI["n"] * CORPS["null_rate"]))
    j_v1 = min(range(len(ms)), key=lambda j: abs(ms[j] - S_V1))
    for j, lab in ((j_xi, "corps XI, 20 years"), (j_v1, "Clarke, 576 squares")):
        s += line(ax.X(ms[j]), ax.y0 + 28, ax.X(ms[j]), ax.y0 + ax.h, stroke=MUTED, sw=0.8, dash="2,3")
        s += plate(ax.X(ms[j]), ax.y0 + 24, f"{lab}: m = {ms[j]:.3g}", fill=MUTED)
    s += plate(ax.X(2000), ax.Y(0.05) - 6, "nominal 5%", fill=SOFT, anchor="end")
    s += note_lines(752, ax.y0 + 20, [
        (f"at m = {ms[j_xi]:.1f} (corps XI)", INK),
        (f"Wald {pct(sz['wald'][j_xi], 2)}", WALD_C), (f"likelihood ratio {pct(sz['lr'][j_xi], 2)}", LR_C),
        (f"score {pct(sz['score'][j_xi], 2)}", SCORE_C),
        (f"verdicts differ in {pct(sz['verdicts_differ'][j_xi], 1)}", MUTED), ("", INK),
        (f"at m = {ms[j_v1]:.0f} (Clarke)", INK),
        (f"Wald {pct(sz['wald'][j_v1], 2)}", WALD_C), (f"likelihood ratio {pct(sz['lr'][j_v1], 2)}", LR_C),
        (f"score {pct(sz['score'][j_v1], 2)}", SCORE_C),
        (f"verdicts differ in {pct(sz['verdicts_differ'][j_v1], 1)}", MUTED), ("", INK),
        ("the zigzag is the count's", SOFT), ("discreteness, not noise", SOFT)], gap=15)
    s += legend(vh - 24, vw, [("Wald", "line:" + WALD_C), ("likelihood ratio", "line:" + LR_C), ("score", "line:" + SCORE_C),
                              ("nominal 5%", "dash:" + SOFT)])
    return emit("04", "exact-sizes", "Exact error rates of the three tests",
                "For a Poisson rate each statistic depends on the data only through the total count, so the lab sums "
                "the Poisson probabilities of every count that rejects.", "when the three tests disagree", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 450
    ws = P["wald_scale"]
    cs = ws["power"]
    bare = lambda x, y, t, fill=MUTED, anchor="middle", weight="400": mono(x, y, t, size=8.5, fill=fill, anchor=anchor,
                                                                          weight=weight)
    s = MARKS + eyebrow(32, 40, "the Wald statistic for one null value, computed on different scales of the same parameter")
    panels = [("corps XI: 25 deaths in 20 years, λ₀ = 0.61", ws["corps"], XI, (0, 30), [0, 5, 10, 15, 20, 25, 30],
               dict(log=(-0.05, 11.6, "end"), lam=(1.06, 8.2, "start"), lr=(-0.95, -1.6), score=(1.95, 0.8))),
              ("Clarke: 537 hits on 576 squares, λ₀ = 0.85", ws["v1"], ST, (3.0, 5.5), [3.0, 3.5, 4.0, 4.5, 5.0, 5.5],
               dict(log=(0.05, 4.86, "start"), lam=(0.95, 4.0, "end"), lr=(-0.95, -0.15), score=(1.95, 0.06)))]
    for i, (name, wv, st, yr, yt, pos) in enumerate(panels):
        ax = Axes(84 + i * 476, 104, 400, 230, (-1, 2), yr)
        s += ax.clip(f"c5{i}") + title(ax.x0, ax.y0 - 16, name)
        s += ax.frame([-1, 0, 1, 2], yt, xlab="power c of the scale λ^c", xfmt=lambda v: f"{v:g}".replace("-", "−"),
                      yfmt=lambda v: f"{v:g}")
        inner = line(ax.x0, ax.Y(3.8415), ax.x0 + ax.w, ax.Y(3.8415), stroke=SOFT, sw=1.0, dash="4,3")
        inner += line(ax.x0, ax.Y(st["lr"]), ax.x0 + ax.w, ax.Y(st["lr"]), stroke=LR_C, sw=1.6)
        inner += line(ax.x0, ax.Y(st["score"]), ax.x0 + ax.w, ax.Y(st["score"]), stroke=SCORE_C, sw=1.6)
        inner += polyline(curve(ax, cs, wv), WALD_C, sw=2.0)
        s += f'<g clip-path="url(#c5{i})">{inner}</g>'
        val = {c: wv[min(range(len(cs)), key=lambda q: abs(cs[q] - c))] for c in (-1, 0, 1, 2)}
        for c in (-1, 0, 1, 2):
            s += dot(ax.X(c), ax.Y(val[c]), 3.6, fill=WALD_C)
        s += bare(ax.X(-1) + 8, ax.Y(val[-1]) - 9, f"1/λ: {val[-1]:.2f}", fill=WALD_C, anchor="start", weight="600")
        lx, ly, la = pos["log"]
        s += bare(ax.X(lx), ax.Y(ly), f"log λ: {val[0]:.2f}", fill=WALD_C, anchor=la, weight="600")
        lx, ly, la = pos["lam"]
        s += bare(ax.X(lx), ax.Y(ly), f"λ: {val[1]:.2f}", fill=WALD_C, anchor=la, weight="600")
        s += bare(ax.X(1.95), ax.Y(val[2]) + 17, f"λ²: {val[2]:.2f}", fill=WALD_C, anchor="end", weight="600")
        x_lr, dy_lr = pos["lr"]
        s += bare(ax.X(x_lr), ax.Y(st["lr"] + dy_lr), f"LR {st['lr']:.2f}", fill=LR_C, anchor="start")
        x_sc, dy_sc = pos["score"]
        s += bare(ax.X(x_sc), ax.Y(st["score"] + dy_sc) - 6, f"score {st['score']:.2f}", fill=SCORE_C, anchor="end")
        s += bare(ax.x0 + 6, ax.Y(3.8415) + 13, "3.84: the χ²₁ 5% point", fill=SOFT, anchor="start")
    s += note_lines(84, 382, [("c = 1 tests the rate itself, c = 0 its log, c = −1 the mean time between deaths: the same hypothesis "
                               "each time. The score and likelihood-ratio statistics do not change.", MUTED)])
    s += legend(vh - 24, vw, [("Wald on the scale λ^c", "line:" + WALD_C), ("likelihood ratio", "line:" + LR_C),
                              ("score", "line:" + SCORE_C), ("χ²₁ 5% point", "dash:" + SOFT)])
    return emit("05", "wald-depends-on-scale", "Wald depends on how the parameter is written",
                "The Wald statistic for one null value, with the information carried to each scale by the chain rule; "
                "the lab's computation.", "when the three tests disagree", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 540
    mu, k = NB["ybar"], NB["k_hat"]
    J = NB["obs_info"]
    s = MARKS + eyebrow(32, 40, "the negative binomial likelihood for Greenwood and Yule's 647 women, over both parameters")
    ax = Axes(96, 96, 540, 360, (0.36, 0.59), (0.3, 2.0))
    s += ax.clip("c6") + title(ax.x0, ax.y0 - 16, "shape k (lower = more unequal accident rates)")
    s += ax.frame([0.38, 0.42, 0.46, 0.50, 0.54, 0.58], [0.4, 0.8, 1.2, 1.6, 2.0], xlab="mean accidents per woman, μ",
                  xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: f"{v:.1f}")
    inner = ""
    for lv, col, sw, op in (("0.99", SOFT, 1.0, 0.0), ("0.95", INK, 1.8, 0.07), ("0.5", SOFT, 1.0, 0.0)):
        pts = [(ax.X(a), ax.Y(b)) for a, b in NB["regions"][lv]]
        if op:
            inner += area(pts, INK, op)
        inner += polyline(pts + pts[:1], col, sw=sw)
    r = math.sqrt(5.991465)
    ell = [(mu + r / math.sqrt(J[0][0]) * math.cos(t), k + r / math.sqrt(J[1][1]) * math.sin(t))
           for t in [2 * math.pi * i / 180 for i in range(181)]]
    inner += polyline([(ax.X(a), ax.Y(b)) for a, b in ell], WALD_C, sw=1.5, dash="5,3")
    inner += line(ax.X(mu), ax.y0 + 22, ax.X(mu), ax.y0 + ax.h, stroke=MUTED, sw=0.8, dash="2,3")
    s += f'<g clip-path="url(#c6)">{inner}</g>'
    s += dot(ax.X(mu), ax.Y(k), 4.2, fill=ACCENT) + dot(ax.X(mu), ax.Y(NB["k_mom"]), 4.0, fill=PAPER, stroke=INK)
    s += plate(ax.X(mu) + 9, ax.Y(k) + 4, "MLE", fill=ACCENT, anchor="start", weight="600")
    s += plate(ax.X(mu) + 9, ax.Y(NB["k_mom"]) + 1, "moments", fill=INK, anchor="start")
    s += plate(ax.X(mu), ax.y0 + 12, "μ = ȳ: the best μ for every k", fill=MUTED)
    ks95 = [b for a, b in NB["regions"]["0.95"]]
    s += note_lines(676, ax.y0 + 20, [
        (f"MLE: μ = {mu:.4f}, k = {k:.3f}", ACCENT), (f"moments: μ = {mu:.4f}, k = {NB['k_mom']:.3f}", INK), ("", INK),
        ("95% likelihood region: a drop of", INK), ("χ²₂ 95% / 2 = 3.00 from the peak", INK),
        (f"k from {min(ks95):.3f} to {max(ks95):.3f}", INK), ("", INK),
        ("95% Wald ellipse from the information", WALD_C),
        (f"k from {k - r / math.sqrt(J[1][1]):.3f} to {k + r / math.sqrt(J[1][1]):.3f}", WALD_C), ("", INK),
        ("observed information at the MLE", MUTED), (f"J(μ, μ) = {J[0][0]:.1f}; J(k, k) = {J[1][1]:.2f}", MUTED),
        ("J(μ, k) = 0: μ and k are orthogonal,", MUTED), ("so neither shape is tilted", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("95% likelihood region", "boxst:" + INK + ":0.07"), ("50% and 99% regions", "line:" + SOFT + ":1.0"),
                              ("95% Wald ellipse", "dash:" + WALD_C), ("MLE", "dot:" + ACCENT + ":4.2"),
                              ("moment estimate", "ring:" + INK)])
    return emit("06", "nb-likelihood-surface", "The negative binomial's likelihood surface",
                "Likelihood regions traced by the lab along rays from the MLE, against the ellipse the observed "
                "information implies.", "a second parameter", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 545
    k = NB["k_hat"]
    D = NB["dispersion"]
    cut = -0.5 * 3.841459
    s = MARKS + eyebrow(32, 40, "profile log-likelihoods and their Wald quadratics, cut at −1.92 for 95% intervals")
    pc = NB["profile_curve"]
    a = Axes(84, 104, 420, 250, (0.3, 2.1), (-4.6, 0.6))
    s += a.clip("c7a") + title(a.x0, a.y0 - 16, "shape k")
    s += a.frame([0.5, 1.0, 1.5, 2.0], [-4, -3, -2, -1, 0], xlab="k", xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: num(v, 0))
    inner = (line(a.x0, a.Y(cut), a.x0 + a.w, a.Y(cut), stroke=SOFT, sw=1.0, dash="4,3")
             + polyline(curve(a, pc["k"], pc["wald_log"]), WALD_C, sw=1.3, dash="1.5,2.5")
             + polyline(curve(a, pc["k"], pc["wald"]), WALD_C, sw=1.4, dash="5,3")
             + polyline(curve(a, pc["k"], pc["ll"]), INK, sw=2.0))
    s += f'<g clip-path="url(#c7a)">{inner}</g>'
    s += dot(a.X(k), a.Y(0), 3.6, fill=ACCENT)
    s += plate(a.X(k), a.Y(0) - 9, f"k̂ = {k:.3f}", fill=ACCENT, weight="600")
    s += plate(a.X(2.08), a.Y(cut) - 6, "−1.92", fill=SOFT, anchor="end")
    rows = [("profile", NB["intervals_k"]["profile"], INK, None), ("Wald, k", NB["intervals_k"]["wald_obs"], WALD_C, None),
            ("Wald, log k", NB["intervals_k"]["wald_log"], WALD_C, "1.5,2.5")]
    for j, (lab, (lo, hi), col, dash) in enumerate(rows):
        yy = a.y0 + a.h + 52 + j * 17
        s += line(a.X(lo), yy, a.X(hi), yy, stroke=col, sw=3.0, dash=dash) + dot(a.X(k), yy, 2.6, fill=col)
        s += mono(a.X(hi) + 8, yy + 3, f"{lab}: {lo:.3f} to {hi:.3f}", size=8, fill=col, anchor="start", weight="600")
    dc = D["curve"]
    b = Axes(588, 104, 380, 250, (1.15, 2.1), (-4.6, 0.6))
    s += b.clip("c7b") + title(b.x0, b.y0 - 16, "dispersion index D = 1 + μ/k")
    s += b.frame([1.2, 1.4, 1.6, 1.8, 2.0], [-4, -3, -2, -1, 0], xlab="D = variance / mean", xfmt=lambda v: f"{v:.1f}",
                 yfmt=lambda v: num(v, 0))
    inner = (line(b.x0, b.Y(cut), b.x0 + b.w, b.Y(cut), stroke=SOFT, sw=1.0, dash="4,3")
             + polyline(curve(b, dc["d"], dc["delta"]), WALD_C, sw=1.4, dash="5,3")
             + polyline(curve(b, dc["d"], dc["ll"]), INK, sw=2.0))
    s += f'<g clip-path="url(#c7b)">{inner}</g>'
    s += dot(b.X(D["d_hat"]), b.Y(0), 3.6, fill=ACCENT)
    s += plate(b.X(D["d_hat"]), b.Y(0) - 9, f"D̂ = {D['d_hat']:.3f}", fill=ACCENT, weight="600")
    for j, (lab, (lo, hi), col) in enumerate((("profile", D["profile"], INK), ("delta method", D["delta"], WALD_C))):
        yy = b.y0 + b.h + 52 + j * 17
        s += line(b.X(lo), yy, b.X(hi), yy, stroke=col, sw=3.0) + dot(b.X(D["d_hat"]), yy, 2.6, fill=col)
        s += mono(b.X(hi) + 8, yy + 3, f"{lab}: {lo:.3f} to {hi:.3f}", size=8, fill=col, anchor="start", weight="600")
    pk = NB["intervals_k"]["profile"]
    s += note_lines(84, a.y0 + a.h + 118, [
        (f"the profile interval for k runs {k - pk[0]:.3f} below k̂ and {pk[1] - k:.3f} above; Wald puts "
         f"{NB['intervals_k']['wald_obs'][1] - k:.3f} on each side (SE {NB['se_obs'][1]:.4f} from the observed information)", MUTED),
        (f"the delta method gives D an SE of {D['se_delta']:.4f}, {pct(D['share_from_k'], 0)} of its variance from k̂; "
         "its interval is symmetric, the profile's is not", MUTED)], gap=16)
    s += legend(vh - 24, vw, [("profile log-likelihood", "line:" + INK), ("Wald or delta-method quadratic", "dash:" + WALD_C),
                              ("Wald quadratic in log k", "dotted:" + WALD_C), ("95% cut", "dash:" + SOFT)])
    return emit("07", "profile-intervals", "Profile and Wald intervals",
                "Profile log-likelihoods for the shape k and for the dispersion index, computed by the lab with μ "
                "maximised out at every point.", "a lopsided interval", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 450
    ks = NB["k_sampling"]
    edges, hist, R = ks["hist_edges"], ks["hist"], ks["R"]
    k, se = NB["k_hat"], NB["se_obs"][1]
    lo, hi = NB["intervals_k"]["wald_obs"]
    s = MARKS + eyebrow(32, 40, f"the shape estimate, refitted on {R:,} data sets of 647 women drawn from the fitted negative binomial")
    ax = Axes(96, 96, 620, 270, (0.3, 2.1), (0, 2.6))
    s += ax.clip("c8") + title(ax.x0, ax.y0 - 16, "density of k̂")
    s += ax.frame([0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0], [0, 0.5, 1.0, 1.5, 2.0, 2.5], xlab="k̂",
                  xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: f"{v:.1f}")
    bars = ""
    for j, c in enumerate(hist[:-1]):                         # the last bin also holds every k̂ beyond the axis
        d = c / (R * (edges[j + 1] - edges[j]))
        if c:
            fill_op = 0.40 if edges[j] >= hi - 1e-9 else 0.22
            bars += rect(ax.X(edges[j]), ax.Y(d), ax.X(edges[j + 1]) - ax.X(edges[j]), ax.Y(0) - ax.Y(d),
                         fill=MUTED, op=fill_op, stroke="none", sw=0)
    xs = [0.3 + 1.8 * i / 300 for i in range(301)]
    inner = bars + polyline([(ax.X(x), ax.Y(normal_pdf(x, k, se))) for x in xs], WALD_C, sw=1.8)
    for v in (lo, hi):
        inner += line(ax.X(v), ax.y0, ax.X(v), ax.y0 + ax.h, stroke=WALD_C, sw=1.0, dash="4,3")
    inner += line(ax.X(k), ax.y0 + 22, ax.X(k), ax.y0 + ax.h, stroke=ACCENT, sw=1.4)
    s += f'<g clip-path="url(#c8)">{inner}</g>'
    s += plate(ax.X(k), ax.y0 + 12, f"true k = {k:.3f}", fill=ACCENT, weight="600")
    s += plate(ax.X(hi) + 6, ax.Y(1.25), f"{pct(ks['above_wald'], 2)} above {hi:.3f}", fill=INK, anchor="start", weight="600")
    s += plate(ax.X(lo) + 6, ax.Y(2.35), f"{pct(ks['below_wald'], 2)} below {lo:.3f}", fill=INK, anchor="start", weight="600")
    s += note_lines(752, ax.y0 + 20, [
        (f"R = {R:,}", MUTED), (f"mean {ks['mean']:.3f}, median {ks['median']:.3f}", INK), (f"SD {ks['sd']:.4f}", INK),
        (f"skewness {ks['skew']:.2f}", INK), ("", INK), ("blue curve: normal, k̂ ± the SE", WALD_C),
        (f"from the observed information, {se:.4f}", WALD_C), ("dashed: its 95% limits", WALD_C), ("", INK),
        ("each tail should hold 2.5%: the", MUTED), (f"right holds {pct(ks['above_wald'], 2)} ± {ks['above_mcse'] * 100:.2f},", MUTED),
        (f"the left {pct(ks['below_wald'], 2)} ± {ks['below_mcse'] * 100:.2f}", MUTED), ("", INK),
        (f"k̂ ≥ {edges[-2]:.2f}, off the axis: {pct(hist[-1] / R, 2)}", SOFT)], gap=16)
    s += legend(vh - 24, vw, [("simulated k̂", "band:" + MUTED + ":0.22"), ("beyond the upper Wald limit", "band:" + MUTED + ":0.40"),
                              ("normal from the Wald SE", "line:" + WALD_C), ("true k", "line:" + ACCENT)])
    return emit("08", "k-sampling-distribution", "The sampling distribution of k̂",
                "Data sets of 647 drawn by the lab from the negative binomial fitted to Greenwood and Yule's table, each "
                "refitted by maximum likelihood.", "a lopsided interval", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 470
    pr = B["profiles"]
    al = pr["alpha"]
    v1 = B["v1"]
    s = MARKS + eyebrow(32, 40, "the negative binomial's profile log-likelihood over its dispersion, relative to the Poisson")
    panels = [(f"Clarke's squares: variance {v1['var_n']:.4f} > mean {v1['mean']:.4f}", pr["v1"], (-1.3, 0.42),
               [-1.0, -0.5, 0, 0.25]),
              (f"a simulated Poisson data set: variance {pr['simulated_var_n']:.4f} < mean {pr['simulated_mean']:.4f}",
               pr["simulated"], (-6.4, 0.6), [-6, -4, -2, 0])]
    axes = []
    for i, (name, ys, yr, yt) in enumerate(panels):
        ax = Axes(96 + i * 476, 104, 380, 250, (-0.05, 0.25), yr)
        axes.append(ax)
        s += ax.clip(f"c9{i}") + title(ax.x0, ax.y0 - 16, name, size=8.8)
        s += rect(ax.x0, ax.y0, ax.X(0) - ax.x0, ax.h, fill=SOFT, op=0.12, stroke="none", sw=0)
        s += mono((ax.x0 + ax.X(0)) / 2, ax.y0 + ax.h - 34, "α < 0:", size=8, fill=SOFT)
        s += mono((ax.x0 + ax.X(0)) / 2, ax.y0 + ax.h - 21, "no such", size=8, fill=SOFT)
        s += mono((ax.x0 + ax.X(0)) / 2, ax.y0 + ax.h - 8, "model", size=8, fill=SOFT)
        s += ax.frame([0, 0.05, 0.10, 0.15, 0.20, 0.25], yt, xlab="α = 1/k", xfmt=lambda v: f"{v:.2f}",
                      yfmt=lambda v: f"{v:g}".replace("-", "−"))
        inner = line(ax.X(0), ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=RULE_SOLID, sw=1.0)
        inner += polyline(curve(ax, al, ys), INK, sw=2.0)
        s += f'<g clip-path="url(#c9{i})">{inner}</g>'
        s += line(ax.X(0), ax.y0, ax.X(0), ax.y0 + ax.h, stroke=ACCENT, sw=2.4)
    a0, a1 = axes
    ah, half = v1["alpha_hat"], v1["lr"] / 2
    s += dot(a0.X(ah), a0.Y(half), 4.0, fill=INK)
    s += plate(a0.X(ah) + 8, a0.Y(0.335), f"MLE α = {ah:.3f}: LR = 2 × {half:.3f} = {v1['lr']:.2f}", fill=INK, anchor="start",
               weight="600")
    s += note_lines(a0.X(0.006), a0.Y(-0.62), [("rises from α = 0:", MUTED), ("the score there is positive", MUTED)], gap=14)
    s += dot(a1.X(0), a1.Y(0), 4.0, fill=ACCENT)
    s += plate(a1.X(0.012), a1.Y(0.28), "MLE α = 0, the Poisson: LR = 0 exactly", fill=ACCENT, anchor="start", weight="600")
    s += note_lines(a1.X(0.008), a1.Y(-4.4), [("falls from α = 0:", MUTED), ("the score there is negative", MUTED)], gap=14)
    s += note_lines(96, 420, [("α cannot go below 0 (orange edge), so when the curve falls from the edge the maximum sits on it. "
                               "Under a Poisson that happens in about half of all data sets.", MUTED)])
    s += legend(vh - 24, vw, [("profile log-likelihood", "line:" + INK), ("the boundary α = 0, the Poisson", "line:" + ACCENT + ":2.4"),
                              ("outside the parameter space", "band:" + SOFT + ":0.12")])
    return emit("09", "boundary-profiles", "A maximum on the boundary",
                "The negative binomial's profile log-likelihood in α for Clarke's table and for one Poisson data set "
                "simulated by the lab at Clarke's rate.", "a null on the boundary", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 480
    s = MARKS + eyebrow(32, 40, f"the share of likelihood ratios above each value, over {NIN['R']:,} simulated data sets per panel")
    grid = NBV["sf_grid"]
    log_y = lambda v: math.log10(max(v, 1e-9))
    panels = [("inside: NB data (k = 0.865), testing the true k", NIN, False),
              ("on the boundary: Poisson data at Clarke's n and rate, testing α = 0", NBV, True)]
    for i, (name, d, mixture) in enumerate(panels):
        ax = Axes(96 + i * 476, 104, 380, 270, (0, 10), (0.0005, 1.0), ymap=log_y)
        s += ax.clip(f"c10{i}") + title(ax.x0, ax.y0 - 16, name, size=8.8)
        s += ax.frame([0, 2, 4, 6, 8, 10], [0.001, 0.01, 0.1, 1.0], xlab="value x of the likelihood ratio",
                      xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
        xs = [10 * j / 200 for j in range(201)]
        inner = polyline([(ax.X(x), ax.Y(chi2_sf1(x))) for x in xs], LINK, sw=1.4, dash="5,3")
        if mixture:
            inner += polyline([(ax.X(x), ax.Y(0.5 * chi2_sf1(x))) for x in xs[1:]], ACCENT, sw=1.4, dash="5,3")
        sim = [(ax.X(x), ax.Y(v)) for x, v in zip(grid, d["sf"]) if v > 0]
        if mixture:                                         # the point mass at 0: P(LR >= 0) = 1, P(LR > 0) = sf[0]
            sim = [(ax.X(0), ax.Y(1.0))] + sim
        inner += polyline(sim, INK, sw=2.0)
        for xv in (2.7055, 3.8415):                       # stop above the text block in the lower left
            inner += line(ax.X(xv), ax.y0, ax.X(xv), ax.Y(0.0062), stroke=SOFT, sw=0.8, dash="2,3")
        s += f'<g clip-path="url(#c10{i})">{inner}</g>'
        s += dot(ax.X(3.8415), ax.Y(d["p_gt_3841"]), 3.6, fill=INK)
        rows = [(f"above 3.84 (χ²₁ test): {pct(d['p_gt_3841'], 2)} ± {100 * d['p_gt_3841_mcse']:.2f}", INK)]
        if mixture:
            s += dot(ax.X(2.7055), ax.Y(d["p_gt_2706"]), 3.6, fill=INK)
            rows = [(f"exactly 0: {pct(d['p_zero'], 1)} ± {100 * d['p_zero_mcse']:.1f}", INK)] + rows
            rows.append((f"above 2.71 (mixture test): {pct(d['p_gt_2706'], 2)} ± {100 * d['p_gt_2706_mcse']:.2f}", INK))
        else:
            rows.append(("the dashed χ²₁ curve lies under", MUTED))
            rows.append(("the simulated one", MUTED))
        s += note_lines(ax.X(0.25), ax.Y(0.0035), rows, gap=15)
    s += note_lines(96, 428, [("dotted verticals: 2.71 and 3.84, the 5% points of the 50:50 mixture and of χ²₁. On the boundary the "
                               "simulated curve drops from 1 to 0.47 at 0, the point mass.", MUTED)])
    s += legend(vh - 24, vw, [("simulated", "line:" + INK), ("χ²₁", "dash:" + LINK), ("50:50 mixture of χ²₀ and χ²₁", "dash:" + ACCENT)])
    return emit("10", "boundary-null-distribution", "χ²₁ inside, a mixture on the boundary",
                "Survival functions of the likelihood-ratio statistic, simulated by the lab under each null.",
                "a null on the boundary", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 480
    m, k = TK["m"], TK["k"]
    s = MARKS + eyebrow(32, 40, "the German tank likelihood for five serial numbers, the largest 303, and the error of its MLE")
    a = Axes(96, 104, 400, 250, (260, 560), (-3.4, 0.4))
    s += a.clip("c11a") + title(a.x0, a.y0 - 16, "log L(N) − log L(m), with L(N) = 1 / C(N, 5)")
    s += a.frame([300, 350, 400, 450, 500, 550], [-3, -2, -1, 0], xlab="number of tanks N", xfmt=lambda v: f"{v:g}",
                 yfmt=lambda v: f"{v:g}".replace("-", "−"))
    s += rect(a.x0, a.y0, a.X(m) - a.x0, a.h, fill=SOFT, op=0.12, stroke="none", sw=0)
    s += mono((a.x0 + a.X(m)) / 2, a.y0 + a.h / 2 - 6, "L = 0:", size=8, fill=SOFT)
    s += mono((a.x0 + a.X(m)) / 2, a.y0 + a.h / 2 + 7, f"N < {m}", size=8, fill=SOFT)
    inner = polyline(curve(a, TK["curve"]["N"], TK["curve"]["ll"]), INK, sw=2.0)
    inner += line(a.X(m), a.Y(0), a.X(m), a.y0 + a.h, stroke=INK, sw=2.0)
    s += f'<g clip-path="url(#c11a)">{inner}</g>'
    s += dot(a.X(m), a.Y(0), 4.0, fill=ACCENT)
    s += plate(a.X(m) + 8, a.Y(0) - 8, f"MLE = m = {m}: on the edge", fill=ACCENT, anchor="start", weight="600")
    s += note_lines(a.X(315), a.Y(-2.3), [(f"slope at m: {TK['first_difference']:.4f} per tank, not 0", MUTED),
                                         ("it bends upward, so −l″ is negative:", MUTED),
                                         ("no information, no standard error", MUTED)], gap=15)
    d5 = TK["distribution"]["5"]
    mu, sd = d5["mean"], d5["sd"]
    b = Axes(596, 104, 380, 250, (-150, 260), (0, 0.016))
    s += b.clip("c11b") + title(b.x0, b.y0 - 16, f"error of the MLE, N − m, over all captures (k = {k}, N = {TK['N']})")
    s += b.frame([-100, 0, 100, 200], [0, 0.005, 0.010, 0.015], xlab="N − MLE, tanks", xfmt=lambda v: f"{v:g}".replace("-", "−"),
                 yfmt=lambda v: f"{100 * v:.1f}%")
    bars = ""
    for e, p in zip(d5["err"], d5["p"]):
        bars += rect(b.X(e - 0.5), b.Y(p), b.X(e + 0.5) - b.X(e - 0.5), b.Y(0) - b.Y(p), fill=MUTED, op=0.30, stroke="none", sw=0)
    xs = [-150 + 410 * j / 300 for j in range(301)]
    neg = [(b.X(x), b.Y(normal_pdf(x, mu, sd))) for x in xs if x <= 0]
    inner = bars + area(neg + [(b.X(0), b.Y(0)), (b.X(-150), b.Y(0))], LINK, 0.16)
    inner += polyline([(b.X(x), b.Y(normal_pdf(x, mu, sd))) for x in xs], LINK, sw=1.6, dash="5,3")
    inner += line(b.X(0), b.y0, b.X(0), b.y0 + b.h, stroke=ACCENT, sw=1.4)
    s += f'<g clip-path="url(#c11b)">{inner}</g>'
    share_neg = 0.5 * math.erfc(mu / sd / math.sqrt(2))
    s += note_lines(b.X(-146), b.Y(0.0143), [("a normal with the", LINK), ("same mean and SD", LINK), (f"puts {pct(share_neg, 0)} of its", LINK),
                                             ("errors below 0,", LINK), ("where none can be", LINK)], gap=14)
    s += plate(b.X(250), b.Y(0.0125), f"exact: mean {mu:.1f}, SD {sd:.1f}", fill=INK, anchor="end")
    s += plate(b.X(250), b.Y(0.0110), f"skewness {d5['skew']:.2f}; exponential: 2", fill=INK, anchor="end")
    s += note_lines(96, 420, [("The support of the serial numbers depends on N, so the likelihood is cut off at the largest serial. "
                               "The MLE lands on that edge, and its error never becomes normal.", MUTED)])
    s += legend(vh - 24, vw, [("log-likelihood", "line:" + INK), ("exact distribution of N − m", "band:" + MUTED + ":0.30"),
                              ("normal with the same mean and SD", "dash:" + LINK), ("MLE, and zero error", "line:" + ACCENT)])
    return emit("11", "tank-likelihood", "A likelihood outside the regularity conditions",
                "The German tank likelihood for the third part's capture, and the exact distribution of the MLE's error, "
                "both computed by the lab.", "the regularity conditions", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 490
    cd = PL["ccdf"]
    row = PL["by_threshold"][2]
    s = MARKS + eyebrow(32, 40, "the first part's lognormal sample: its top 1,000 values with both fits, on log–log axes")
    ax = Axes(96, 96, 600, 320, (20, 12000), (0.0007, 1.3), xmap=math.log10, ymap=math.log10)
    s += ax.clip("c12") + title(ax.x0, ax.y0 - 16, "share of the 1,000 values at least x")
    s += ax.frame([20, 100, 1000, 10000], [0.001, 0.01, 0.1, 1.0], xlab="x (log scale)", xfmt=lambda v: f"{v:,.0f}",
                  yfmt=lambda v: f"{v:g}")
    inner = polyline([(ax.X(x), ax.Y(v)) for x, v in zip(cd["x"], cd["pl"])], LINK, sw=1.8)
    inner += polyline([(ax.X(x), ax.Y(v)) for x, v in zip(cd["x"], cd["ln"])], ACCENT, sw=1.8)
    for x, v in zip(cd["x"], cd["s"]):
        inner += dot(ax.X(x), ax.Y(v), 1.9, fill=INK, op=0.55)
    ks = PL["ks"]
    inner += line(ax.X(ks["xmin"]), ax.y0, ax.X(ks["xmin"]), ax.y0 + ax.h, stroke=SOFT, sw=1.0, dash="4,3")
    s += f'<g clip-path="url(#c12)">{inner}</g>'
    s += plate(ax.X(ks["xmin"]) + 6, ax.Y(0.0018), f"CSN's threshold {ks['xmin']:.1f}: {ks['n_tail']} values", fill=SOFT,
               anchor="start")
    s += note_lines(730, ax.y0 + 20, [
        (f"threshold {row['xmin']:.2f}: the top 1,000", INK), ("", INK),
        (f"power law, MLE α = {row['alpha']:.3f} ± {row['alpha_se']:.3f}", LINK),
        ("lognormal cut at the threshold, MLE", ACCENT), (f"μ = {row['ln_mu']:.2f}, σ = {row['ln_sigma']:.2f}".replace("-", "−"), ACCENT),
        ("", INK),
        (f"log-likelihood: lognormal {row['ll_ln']:.1f}".replace("-", "−"), INK), (f"power law {row['ll_pl']:.1f}".replace("-", "−"), INK),
        (f"ratio R = {row['R']:.2f} for the lognormal", INK), ("", INK),
        (f"Vuong: R / (SD × √n) = {row['z']:.2f}", INK), (f"p = {row['p']:.3f}", INK), ("", INK),
        (f"at CSN's threshold: {ks['z']:.2f}, p = {ks['p']:.2f}", SOFT)], gap=16)
    s += legend(vh - 24, vw, [("data, top 1,000 of 10,000", "dot:" + INK + ":1.9:0.55"), ("power-law fit", "line:" + LINK),
                              ("lognormal fit", "line:" + ACCENT), ("KS threshold", "dash:" + SOFT)])
    return emit("12", "power-law-or-lognormal", "Power law or lognormal, by likelihood",
                "Both models fitted by maximum likelihood above the threshold the first part used; the lab regenerates "
                "that part's sample exactly.", "power law or lognormal", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 470
    rows = PL["by_threshold"]
    pw = PL["power"]
    s = MARKS + eyebrow(32, 40, "Vuong's normalised likelihood ratio against the number of points above the threshold")
    ax = Axes(96, 96, 600, 290, (70, 7000), (-3, 13.5), xmap=math.log10)
    s += ax.clip("c13") + title(ax.x0, ax.y0 - 16, "normalised ratio (above 0 favours the lognormal)")
    s += ax.frame([100, 200, 500, 1000, 2000, 5000], [-2, 0, 2, 4, 6, 8, 10, 12], xlab="points above the threshold (log scale)",
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: f"{v:g}".replace("-", "−"))
    z = 1.6448536
    inner = rect(ax.x0, ax.Y(z), ax.w, ax.Y(-z) - ax.Y(z), fill=SOFT, op=0.14, stroke="none", sw=0)
    inner += line(ax.x0, ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=RULE_SOLID, sw=1.0)
    inner += polyline([(ax.X(r["n_tail"]), ax.Y(r["z"])) for r in rows], INK, sw=1.6)
    s += f'<g clip-path="url(#c13)">{inner}</g>'
    for key, n_pts, dx, col in (("lognormal_top5", 500, 0.86, ACCENT), ("lognormal_top10", 1000, 0.86, ACCENT),
                                ("powerlaw_1000", 1000, 1.16, LINK)):
        q = pw[key]["z_quantiles"]
        x = ax.X(n_pts * dx)
        s += line(x, ax.Y(q[0]), x, ax.Y(q[4]), stroke=col, sw=2.4)
        s += line(x - 6, ax.Y(q[2]), x + 6, ax.Y(q[2]), stroke=col, sw=2.4)
    for r in rows:
        s += dot(ax.X(r["n_tail"]), ax.Y(r["z"]), 4.0, fill=INK)
    for j, r in enumerate(rows[:3]):                       # 12.49 beside its dot; 6.23 and 2.29 below the rising line
        dy = 4 if j == 0 else 17
        s += plate(ax.X(r["n_tail"]) + 8, ax.Y(r["z"]) + dy, f"{r['z']:.2f}", fill=INK, anchor="start", weight="600")
    ks = PL["ks"]
    s += dot(ax.X(ks["n_tail"]), ax.Y(ks["z"]), 4.0, fill=PAPER, stroke=INK)
    s += plate(ax.X(ks["n_tail"]) - 10, ax.Y(-1.0), f"KS threshold, {ks['n_tail']} points: {ks['z']:.2f}", fill=INK, anchor="end")
    s += plate(ax.X(7000) - 6, ax.Y(z) + 13, "|ratio| < 1.64: p > 0.1, undecided", fill=SOFT, anchor="end")
    s += note_lines(730, ax.y0 + 20, [
        ("dots: the first part's sample, at", INK), ("thresholds keeping 1% to 50% of it", INK), ("", INK),
        (f"bars: 5% to 95% of {pw['lognormal_top10']['R']:,} fresh", MUTED), ("samples, drawn beside the dots", MUTED), ("", INK),
        ("lognormal truth, decided for it in", ACCENT),
        (f"{pct(pw['lognormal_top10']['favours_lognormal'], 1)} at 1,000 points", ACCENT),
        (f"{pct(pw['lognormal_top5']['favours_lognormal'], 1)} at 500 points", ACCENT), ("", INK),
        ("power-law truth, 1,000 points:", LINK), (f"decided for it in {pct(pw['powerlaw_1000']['favours_power_law'], 1)}", LINK),
        (f"for the lognormal in {pct(pw['powerlaw_1000']['favours_lognormal'], 1)}", LINK)], gap=16)
    s += legend(vh - 24, vw, [("the first part's sample", "dot:" + INK + ":4.0"), ("lognormal truth, 5% to 95%", "line:" + ACCENT + ":2.4"),
                              ("power-law truth, 5% to 95%", "line:" + LINK + ":2.4"), ("undecided band", "band:" + SOFT + ":0.14")])
    return emit("13", "vuong-by-threshold", "The verdict depends on the threshold",
                "Vuong's statistic on the first part's sample at six thresholds and at CSN's, with its spread over fresh "
                "samples simulated by the lab.", "power law or lognormal", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09, "10": fig10, "11": fig11, "12": fig12, "13": fig13}

if __name__ == "__main__":
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
