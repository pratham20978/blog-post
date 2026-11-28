#!/usr/bin/env python3
"""Figures 01-08 and 10-13 for mcmc-diagnostics-metropolis-nuts (Statistics for Data Scientists, part 12).

Figure 09 is a Mermaid figure (fig-09-*.mmd, rendered by _mermaid.py). Every value drawn here comes from the lab's
capture, ../lab/captures.json, written by lab/mcmc.py, or from a closed form evaluated here (the beta density through
math.lgamma) whose parameters come from the capture. The asserts pin each number the article quotes, so a figure
cannot drift from the text. Run:  python3 _figs.py [01 ...]
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
PF, TU, NB, DG, MC, RH, BM, NU = (CAP[k] for k in ("pfizer", "tuning", "nb", "diagnostics", "mcse", "rhat", "bimodal",
                                                   "nuts"))
XC = CAP["author_crosscheck"]
A_POST, B_POST = 0.700102 + 8, 163.0          # Part 11's posterior; rebuilt from its inputs, not read back from r6 values
R_SURV = 2.214 / 2.222
CH = (INK, LINK, "#7d9ccf", MUTED)             # four chains: ink, link blue, a lighter blue, muted slate


def hp(share, nd=1):
    """A share as a percentage, rounded half up from its stored decimal, as the lab prints it."""
    return float((Decimal(repr(float(share))) * 100).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


def hv(x, nd=4):
    """A number rounded half up from its stored decimal."""
    return float(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP))


# ------------------------------------------------------------------ the numbers the article quotes
EX = PF["exact"]
assert (hp(EX["ve_q025"], 2), hp(EX["ve_q975"], 2)) == (90.32, 97.62)
assert (hp(PF["estimates"]["q025"]["value"], 2), hp(PF["estimates"]["q975"]["value"], 2)) == (90.47, 97.52)
assert hv(PF["estimates"]["q025"]["z"], 2) == 1.20 and hv(PF["estimates"]["q975"]["z"], 2) == -2.61
assert round(PF["diagnostics"]["ess_bulk"]) == 4242 and round(PF["diagnostics"]["ess_tail"]) == 4458
assert [r["accept"] for r in PF["first_iterations"]] == [False, True, True, False, False, False, False, False]
assert round(PF["running"]["tau_chain1"], 2) == 5.08
TR = TU["traces"]
assert [hp(TR[k]["acceptance"]) for k in ("0.002", "0.04", "1.0")] == [95.5, 42.8, 2.2]
assert [round(TR[k]["ess_mean"]) for k in ("0.002", "0.04", "1.0")] == [46, 3638, 296]
assert [TR[k]["max_t"] for k in ("0.002", "0.04", "1.0")] == [589, 31, 125]
SW = TU["sweep"]
assert (hp(SW["1d"]["best_acceptance"]), hv(SW["1d"]["best_efficiency"], 3)) == (42.1, 0.207)
assert (hp(SW["2d"]["best_acceptance"]), hv(SW["2d"]["best_efficiency"], 3)) == (31.2, 0.135)
G = NB["grid"]
assert (hv(G["mu"]["mean"], 4), hv(G["k"]["mean"], 4), hv(G["k"]["q500"], 3)) == (0.4665, 0.9088, 0.877)
assert (hv(G["mode_mu"], 4), hv(G["mode_k"], 4)) == (0.4657, 0.8666)
assert DG["worst_rel_diff"] == 0.0 and XC["worst_rel_diag"] < 1e-11
P = DG["pieces"]
assert (round(P["tau"], 3), round(P["ess_mean"], 1), P["max_t"]) == (4.961, 4031.7, 13)
ST = MC["steps"]
assert [hp(ST[k]["naive"]) for k in ("0.008", "0.04", "0.25")] == [29.8, 65.1, 34.3]
assert [hp(ST[k]["ess_based"]) for k in ("0.008", "0.04", "0.25")] == [93.2, 94.9, 94.9]
assert [hp(ST[k]["quantile"]) for k in ("0.008", "0.04", "0.25")] == [86.5, 91.4, 86.4]
TRD = RH["trend"]["rhat"]
assert (hv(TRD["unsplit"], 3), hv(TRD["split"], 3), hv(TRD["bulk"], 3), hv(TRD["folded"], 3)) == (0.999, 1.732, 1.798, 1.177)
C1000 = RH["constructed"]["1000"]
CR = C1000["crossings"]
assert (hv(CR["shift_split_1.01"], 2), hv(CR["shift_split_1.1"], 2)) == (0.31, 0.99)
assert (hv(CR["scale_folded_1.01"], 2), hv(CR["scale_folded_1.1"], 2)) == (0.76, 0.36)
RU = RH["threshold"]["rules"]
assert (RU["rank<1.1"]["passed"], hp(RU["rank<1.1"]["share_off_1pt"]), hp(RU["rank<1.1"]["worst"], 2)) == (1762, 10.6, 3.96)
assert (RU["rank<1.01 & ESS>400"]["passed"], RU["rank<1.01 & ESS>400"]["share_off_1pt"]) == (296, 0.0)
OM, DI, LJ = BM["one_mode"], BM["dispersed"], BM["long_jumps"]
assert (hv(OM["diagnostics"]["rank"], 4), round(OM["diagnostics"]["ess_bulk"]), OM["crossings"]) == (1.0006, 4295, 0)
assert hv(DI["diagnostics"]["rank"], 2) == 1.60 and hv(LJ["p_right"], 3) == 0.301
CS = BM["crossing"]["by_separation"]
assert [hp(CS[k]["share"]) for k in ("10.0", "12.0", "14.0", "16.0")] == [99.7, 40.2, 3.2, 0.1]
assert NU["divergences"] == 0 and round(NU["mean_n_steps"], 2) == 2.68
assert [round(NU["params"][p]["mine"]["ess_bulk"]) for p in ("mu", "k")] == [3769, 3943]


# ------------------------------------------------------------------ drawing helpers (Part 11's set)
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
        elif part[0] == "cross":
            s += line(x + 4, y + 1, x + 12, y + 9, stroke=part[1], sw=1.4) + line(x + 12, y + 1, x + 4, y + 9, stroke=part[1], sw=1.4)
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


def lin(a, b, m):
    return [a + (b - a) * i / (m - 1) for i in range(m)]


def beta_pdf(x, a, b):
    return math.exp((a - 1) * math.log(x) + (b - 1) * math.log1p(-x) - (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)))


def ve(theta):
    return 1 - theta / ((1 - theta) * R_SURV)


def cross_mark(x, y, r=3.6, stroke=SOFT, sw=1.4):
    return line(x - r, y - r, x + r, y + r, stroke=stroke, sw=sw) + line(x + r, y - r, x - r, y + r, stroke=stroke, sw=sw)


def bars(ax, lo, hi, counts, total, fill, op=0.35, stroke=None):
    """A histogram drawn as a density on ax, from bin counts over equal bins between lo and hi."""
    w = (hi - lo) / len(counts)
    s = ""
    for i, c in enumerate(counts):
        if c == 0:
            continue
        d = c / (total * w)
        x0, x1 = lo + i * w, lo + (i + 1) * w
        s += rect(ax.X(x0), ax.Y(d), ax.X(x1) - ax.X(x0), ax.Y(0) - ax.Y(d), fill=fill, op=op,
                  stroke=stroke or "none", sw=0.6 if stroke else 0)
    return s


def contour_segments(z, xs, ys, level):
    """Marching squares on z[i][j] over xs[i], ys[j]: the line segments where z crosses level."""
    segs = []
    for i in range(len(xs) - 1):
        for j in range(len(ys) - 1):
            v = (z[i][j], z[i + 1][j], z[i + 1][j + 1], z[i][j + 1])
            pts = ((xs[i], ys[j]), (xs[i + 1], ys[j]), (xs[i + 1], ys[j + 1]), (xs[i], ys[j + 1]))
            cr = []
            for k in range(4):
                a, b = v[k], v[(k + 1) % 4]
                if (a >= level) != (b >= level):
                    t = (level - a) / (b - a)
                    (x1, y1), (x2, y2) = pts[k], pts[(k + 1) % 4]
                    cr.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
            if len(cr) == 2:
                segs.append((cr[0], cr[1]))
            elif len(cr) == 4:
                centre = sum(v) / 4 >= level
                segs += ([(cr[0], cr[3]), (cr[1], cr[2])] if centre == (v[0] >= level) else [(cr[0], cr[1]), (cr[2], cr[3])])
    return segs


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 540
    rows = PF["first_iterations"]
    s = eyebrow(32, 40, "metropolis by hand on part 11's posterior for θ, step 0.04: eight iterations from θ = 0.10")
    ax = Axes(96, 92, 470, 300, (0.0, 0.18), (0, 28))
    s += ax.clip("c1a") + title(ax.x0, ax.y0 - 16, "(a) each proposal θ* against the density: accept if u < r = p(θ*)/p(θ)")
    s += ax.frame([0, 0.04, 0.08, 0.12, 0.16], [0, 10, 20], xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: f"{v:.0f}",
                  xlab="θ, the vaccine group's share of cases", ylab="posterior density beta(8.700102, 163)")
    xs = lin(0.0005, 0.18, 400)
    inner = polyline(curve(ax, xs, [beta_pdf(x, A_POST, B_POST) for x in xs]), INK, sw=1.6)
    s += f'<g clip-path="url(#c1a)">{inner}</g>'
    # proposals, numbered by iteration; staggered labels where two proposals sit close
    offsets = {1: -14, 2: -14, 3: -14, 4: -14, 5: -14, 6: 16, 7: -14, 8: -16}
    for r in rows:
        x = ax.X(r["proposal"])
        y = ax.Y(beta_pdf(r["proposal"], A_POST, B_POST))
        if r["accept"]:
            s += dot(x, y, 4.2, fill=LINK)
        else:
            s += dot(x, y, 4.0, fill=PAPER, stroke=SOFT, sw=1.3)
        dx = 8 if r["t"] != 8 else -8
        s += mono(x + dx, y + offsets[r["t"]], f"{r['t']}", size=8.5, fill=LINK if r["accept"] else SOFT,
                  anchor="start" if dx > 0 else "end", weight="600")
    # the current state for iterations 4-8, and its density level
    cur = rows[3]["theta"]
    pc_ = beta_pdf(cur, A_POST, B_POST)
    s += line(ax.X(0.0), ax.Y(pc_), ax.X(0.18), ax.Y(pc_), stroke=ACCENT, sw=1.0, dash="4,3")
    s += dot(ax.X(cur), ax.Y(pc_), 4.6, fill=ACCENT)
    s += mono(ax.X(0.096), ax.Y(pc_) - 22, f"p(θ) at θ = {cur:.4f} (proposal 3, accepted):", size=8, fill=ACCENT,
              anchor="start", weight="600")
    s += mono(ax.X(0.096), ax.Y(pc_) - 8, "the state for t = 4 to 8", size=8, fill=ACCENT, anchor="start", weight="600")
    s += note_lines(ax.X(0.096), ax.Y(pc_) + 22, [("below the line: r < 1,", MUTED), ("accepted only if u < r", MUTED)])
    # panel (b): the table as a trace
    bx = Axes(650, 92, 330, 300, (0, 8), (0.0, 0.18))
    s += bx.clip("c1b") + title(bx.x0, bx.y0 - 16, "(b) the chain θ0 ... θ8: a rejection repeats θ")
    s += bx.frame(list(range(0, 9)), [0, 0.04, 0.08, 0.12, 0.16], xfmt=lambda v: f"{v}", yfmt=lambda v: f"{v:.2f}",
                  xlab="iteration t", ylab="θ_t")
    states = [rows[0]["theta"]] + [r["next"] for r in rows]
    pts = []
    for t, v in enumerate(states):
        pts.append((bx.X(t), bx.Y(v)))
    s += polyline(pts, INK, sw=1.4)
    for r in rows:
        x, y = bx.X(r["t"]), bx.Y(r["proposal"])
        if r["accept"]:
            s += dot(x, y, 3.8, fill=LINK)
        else:
            s += cross_mark(x, y) if r["proposal"] <= 0.18 else ""
    for t, v in enumerate(states):
        s += dot(bx.X(t), bx.Y(v), 3.0, fill=INK)
    s += note_lines(bx.X(3.4), bx.Y(0.135), [(f"t = 4 to 8: five proposals rejected,", MUTED),
                                            (f"θ stays at {cur:.4f} five times", INK)])
    s += note_lines(96, 440, [(f"t = 2: r = {rows[1]['r']:.2f} ≥ 1, accepted whatever u is;  t = 3: r = {rows[2]['r']:.3f}, accepted", MUTED),
                              (f"t = 6: r = {rows[5]['r']:.3f} but u = {rows[5]['u']:.3f}, rejected;  t = 7: θ* = {rows[6]['proposal']:.4f}, "
                               f"r = 4.2 × 10^-6, rejected", MUTED)], size=8.5, gap=16)
    s += legend(vh - 24, vw, [("accepted proposal", "dot:" + LINK + ":4"), ("rejected proposal", "ring:" + SOFT + ":4"),
                              ("rejected (trace)", "cross:" + SOFT), ("the chain's state", "dot:" + INK + ":3"),
                              ("current state and its density", "dash:" + ACCENT + ":1.2")])
    return emit("01", "one-metropolis-step", "One Metropolis step, eight times",
                "Eight iterations of random-walk Metropolis on the trial's posterior: two proposals accepted, six "
                "rejected, and each rejection repeats the current state.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "four chains from dispersed starts, step 0.04: 1,000 warmup iterations discarded, 5,000 kept each")
    ax = Axes(96, 92, 400, 300, (0, 400), (0.003, 0.6), ymap=math.log10)
    s += ax.clip("c2a") + title(ax.x0, ax.y0 - 16, "(a) the first 400 iterations (log scale)")
    s += ax.frame([0, 100, 200, 300, 400], [0.005, 0.01, 0.03, 0.1, 0.3], xfmt=lambda v: f"{v}",
                  yfmt=lambda v: f"{v:g}", xlab="iteration", ylab="θ")
    lo, hi = EX["theta_q025"], EX["theta_q975"]
    inner = rect(ax.X(0), ax.Y(hi), ax.w, ax.Y(lo) - ax.Y(hi), fill=ACCENT, op=0.12, stroke="none", sw=0)
    for c, tr in enumerate(PF["trace_head"]):     # the capture records the state after iterations 1, 2, ...
        st = PF["starts"][c]
        inner += polyline(curve(ax, list(range(len(tr) + 1)), [st] + tr), CH[c], sw=1.0)
    s += f'<g clip-path="url(#c2a)">{inner}</g>'
    for c, st in enumerate(PF["starts"]):
        s += dot(ax.X(0), ax.Y(st), 4.0, fill=CH[c])
    entry = []
    for c, tr in enumerate(PF["trace_head"]):
        st = PF["starts"][c]
        if lo <= st <= hi:
            entry.append(f"from {st:g}: starts inside")
        else:
            entry.append(f"from {st:g}: {next(i for i, v in enumerate(tr, start=1) if lo <= v <= hi)}")
    s += mono(ax.X(396), ax.Y(0.42), f"shaded: exact central 95% of θ, {lo:.4f} to {hi:.4f}", size=8, fill=ACCENT, anchor="end")
    s += note_lines(ax.x0, 448, [("dots: the four starts at iteration 0. Iterations until each chain is inside the band:", MUTED),
                                 ("; ".join(entry), INK)], size=8.5, gap=16)
    # panel (b): kept draws against the exact density of VE
    hb = PF["ve_hist"]
    bx = Axes(596, 92, 380, 300, (0.86, 0.995), (0, 30))
    s += bx.clip("c2b") + title(bx.x0, bx.y0 - 16, "(b) 20,000 kept draws of VE against the closed form")
    s += bx.frame([0.88, 0.92, 0.96, 0.99], [0, 10, 20, 30], xfmt=lambda v: f"{100 * v:.0f}%", yfmt=lambda v: f"{v:.0f}",
                  xlab="vaccine efficacy VE", ylab="density")
    inner = bars(bx, hb["lo"], hb["hi"], hb["counts"], hb["n"], LINK, op=0.30)
    dv = PF["ve_density"]
    inner += polyline(curve(bx, dv["v"], dv["density"]), INK, sw=1.7)
    s += f'<g clip-path="url(#c2b)">{inner}</g>'
    e025, e975 = EX["ve_q025"], EX["ve_q975"]
    c025, c975 = PF["estimates"]["q025"]["value"], PF["estimates"]["q975"]["value"]
    for v in (e025, e975):
        s += line(bx.X(v), bx.Y(0), bx.X(v), bx.Y(27), stroke=ACCENT, sw=1.4)
    for v in (c025, c975):
        s += line(bx.X(v), bx.Y(0), bx.X(v), bx.Y(24), stroke=LINK, sw=1.2, dash="4,3")
    s += note_lines(bx.x0 + 8, bx.y0 + 16, [(f"exact: {pct(e025, 2)} to {pct(e975, 2)}", ACCENT),
                                            (f"chain: {pct(c025, 2)} to {pct(c975, 2)}", LINK),
                                            (f"MCSE {hp(PF['estimates']['q025']['mcse'], 2):.2f} and "
                                             f"{hp(PF['estimates']['q975']['mcse'], 2):.2f} points", MUTED),
                                            (f"z = {hv(PF['estimates']['q025']['z'], 2):+.2f} and "
                                             f"{hv(PF['estimates']['q975']['z'], 2):+.2f}".replace("-", "−"), MUTED)])
    s += legend(vh - 24, vw, [("chains 1-4 and their starts", "line:" + INK + ":1.2"), ("kept draws", "bar:" + LINK + ":0.30"),
                              ("exact density of VE", "line:" + INK + ":1.7"), ("exact 95% (θ or VE)", "band:" + ACCENT + ":0.3"),
                              ("chain's 2.5% and 97.5% points", "dash:" + LINK + ":1.2")])
    return emit("02", "four-chains-to-the-posterior", "Four chains forget where they started",
                "Four random-walk Metropolis chains started far apart reach the posterior within the warmup; their "
                "20,000 kept draws reproduce the exact density of efficacy.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 470
    ru = PF["running"]
    tau, sd, ex = ru["tau_chain1"], ru["sd"], ru["exact"]
    s = eyebrow(32, 40, "running mean of VE: one chain's kept draws against as many independent exact draws")
    ax = Axes(96, 84, 840, 290, (10, 5000), (0.925, 0.967), xmap=math.log10)
    s += ax.clip("c3") + title(ax.x0, ax.y0 - 16, f"95% bands around the exact mean: ±1.96 SD/√n for independent draws, "
                                                  f"±1.96 SD·√(τ/n) for the chain (τ = {tau:.2f})")
    s += ax.frame([10, 30, 100, 300, 1000, 3000], [0.93, 0.94, 0.95, 0.96], xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: f"{100 * v:.0f}%", xlab="number of draws n (log scale)", ylab="running mean of VE")
    ns = ru["n"]
    band_c = [(n, ex + 1.96 * sd * math.sqrt(tau / n)) for n in ns] + [(n, ex - 1.96 * sd * math.sqrt(tau / n)) for n in reversed(ns)]
    band_i = [(n, ex + 1.96 * sd / math.sqrt(n)) for n in ns] + [(n, ex - 1.96 * sd / math.sqrt(n)) for n in reversed(ns)]
    inner = area([(ax.X(a), ax.Y(min(max(b, 0.925), 0.967))) for a, b in band_c], LINK, 0.12)
    for sign in (1, -1):
        inner += polyline([(ax.X(n), ax.Y(ex + sign * 1.96 * sd / math.sqrt(n))) for n in ns], MUTED, sw=1.0, dash="4,3")
    inner += line(ax.X(10), ax.Y(ex), ax.X(5000), ax.Y(ex), stroke=ACCENT, sw=1.2, dash="5,3")
    inner += polyline(curve(ax, ns, ru["iid"]), MUTED, sw=1.3)
    inner += polyline(curve(ax, ns, ru["chain"]), LINK, sw=1.6)
    s += f'<g clip-path="url(#c3)">{inner}</g>'
    hw_i = 1.96 * sd / math.sqrt(ns[-1])
    hw_c = 1.96 * sd * math.sqrt(tau / ns[-1])
    s += note_lines(ax.X(700), ax.Y(0.9605), [(f"at n = {ns[-1]:,}: half-width {hp(hw_i, 2):.2f} points independent,", MUTED),
                                               (f"{hp(hw_c, 2):.2f} points for the chain: √τ = {math.sqrt(tau):.2f} times wider", LINK)])
    s += mono(ax.X(11), ax.Y(ex) + 14, f"exact mean {pct(ex, 2)}", size=8, fill=ACCENT, anchor="start", weight="600")
    s += legend(vh - 24, vw, [("chain 1, kept draws", "line:" + LINK + ":1.6"), ("independent draws", "line:" + MUTED + ":1.3"),
                              ("chain's band", "band:" + LINK + ":0.12"), ("independent band", "dash:" + MUTED + ":1.0"),
                              ("exact mean", "dash:" + ACCENT + ":1.2")])
    return emit("03", "running-means-dependence", "A dependent average wanders further",
                "The running mean of one Metropolis chain against the running mean of independent exact draws: the "
                "chain behaves like an independent sample τ times smaller.", "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 600
    s = eyebrow(32, 40, "one chain from θ = 0.10 at three proposal steps; acceptance from this trace, ESS from four chains of 5,000")
    labels = {"0.002": ("too small", "the chain crawls: almost every proposal", "is accepted and goes nowhere"),
              "0.04": ("about right", "about 2.4 posterior SDs: big moves,", "often accepted"),
              "1.0": ("too large", "the chain sticks: most proposals land", "outside (0, 1) or in the far tail")}
    y0 = 84
    for i, k in enumerate(("0.002", "0.04", "1.0")):
        t = TR[k]
        ax = Axes(96, y0 + i * 150, 600, 110, (0, 1000), (0.0, 0.16))
        cid = f"c4{i}"
        s += ax.clip(cid) + title(ax.x0, ax.y0 - 10, f"step {k}: {labels[k][0]}")
        s += ax.frame([0, 250, 500, 750, 1000] if i == 2 else [], [0, 0.08, 0.16], xfmt=lambda v: f"{v}",
                      yfmt=lambda v: f"{v:.2f}", xlab="iteration" if i == 2 else None)
        band = rect(ax.X(0), ax.Y(EX["theta_q975"]), ax.w, ax.Y(EX["theta_q025"]) - ax.Y(EX["theta_q975"]),
                    fill=ACCENT, op=0.10, stroke="none", sw=0)
        inner = band + polyline(curve(ax, list(range(len(t["trace"]))), t["trace"]), INK, sw=1.0)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        s += note_lines(730, ax.y0 + 16, [(f"acceptance {pct(t['acceptance_trace'])} here", INK),
                                         (f"four chains: {pct(t['acceptance'])} accepted,", MUTED),
                                         (f"ESS {t['ess_mean']:,.0f} of 20,000 draws", LINK),
                                         (f"τ = {t['tau']:,.1f}", MUTED),
                                         (labels[k][1], SOFT), (labels[k][2], SOFT)], size=8.5, gap=15)
    s += legend(vh - 24, vw, [("θ, one chain", "line:" + INK + ":1.2"), ("exact central 95% of θ", "band:" + ACCENT + ":0.25")])
    return emit("04", "step-size-traces", "Too small crawls, too large sticks",
                "Traces of random-walk Metropolis at three proposal steps on the trial's posterior, with their "
                "acceptance rates and effective sample sizes.", "how big should the step be", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "efficiency of random-walk metropolis against its acceptance rate: 25 proposal scales, 80,000 draws each")
    ax = Axes(96, 84, 840, 290, (0, 1.0), (0, 0.24))
    s += ax.clip("c5") + title(ax.x0, ax.y0 - 16, "ESS per draw for the posterior mean; the scale c multiplies each parameter's posterior SD")
    s += ax.frame([0, 0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.05, 0.10, 0.15, 0.20], xfmt=lambda v: f"{100 * v:.0f}%",
                  yfmt=lambda v: f"{v:.2f}", xlab="acceptance rate", ylab="ESS per draw")
    inner = ""
    for v, lab in ((0.44, "0.44: one dimension"), (0.234, "0.234: the high-dimensional limit")):
        inner += line(ax.X(v), ax.y0, ax.X(v), ax.Y(0), stroke=SOFT, sw=1.0, dash="4,3")
    for dim, col in (("1d", INK), ("2d", LINK)):
        sw_ = SW[dim]
        pts = sorted(zip(sw_["acceptance"], sw_["efficiency"]))
        inner += polyline([(ax.X(a), ax.Y(e)) for a, e in pts], col, sw=1.6)
        for a, e in pts:
            inner += dot(ax.X(a), ax.Y(e), 2.6, fill=col)
        inner += dot(ax.X(sw_["best_acceptance"]), ax.Y(sw_["best_efficiency"]), 6, fill="none", stroke=ACCENT, sw=1.6)
    s += f'<g clip-path="url(#c5)">{inner}</g>'
    s += mono(ax.X(0.44) + 4, ax.y0 + 12, "BDA3: 0.44 in one dimension", size=8, fill=SOFT, anchor="start")
    s += mono(ax.X(0.234) - 4, ax.y0 + 12, "0.234 as dimension grows", size=8, fill=SOFT, anchor="end")
    b1, b2 = SW["1d"], SW["2d"]
    s += note_lines(ax.X(0.62), ax.Y(0.205), [(f"one dimension (the trial): best c = {b1['best_c']:.2f},", INK),
                                             (f"acceptance {pct(b1['best_acceptance'])}, ESS per draw {b1['best_efficiency']:.3f}", INK),
                                             (f"two dimensions (accidents, ESS of log mu): best c = {b2['best_c']:.2f},", LINK),
                                             (f"acceptance {pct(b2['best_acceptance'])}, ESS per draw {b2['best_efficiency']:.3f}", LINK)])
    s += legend(vh - 24, vw, [("one dimension: the trial's θ", "line:" + INK + ":1.6"),
                              ("two dimensions, measured on log mu", "line:" + LINK + ":1.6"),
                              ("most efficient scale tried", "ring:" + ACCENT + ":5"),
                              ("theoretical optima", "dash:" + SOFT + ":1.0")])
    return emit("05", "efficiency-against-acceptance", "Efficiency peaks at middling acceptance",
                "Effective sample size per draw against acceptance rate for random-walk Metropolis on the trial's "
                "posterior and on the two-parameter accidents posterior.", "how big should the step be", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 600
    f = NB["fig"]
    s = eyebrow(32, 40, "greenwood and yule's 647 women: negative binomial posterior of mean mu and shape k; log mu, log k normal priors, sd 2")
    # panel (a): warmup from the four corners, log axes
    ax = Axes(96, 100, 300, 300, (0.1, 3.5), (0.1, 9.0), xmap=math.log10, ymap=math.log10)
    s += ax.clip("c6a") + title(ax.x0, ax.y0 - 18, "(a) adaptive warmup: first 150 iterations")
    s += ax.frame([0.1, 0.3, 1, 3], [0.1, 0.3, 1, 3], xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}",
                  xlab="mu (log scale)", ylab="k (log scale)")
    inner = ""
    for c, wh in enumerate(f["warm_head"]):
        inner += polyline([(ax.X(math.exp(a)), ax.Y(math.exp(b))) for a, b in wh], CH[c], sw=1.0)
        inner += dot(ax.X(math.exp(wh[0][0])), ax.Y(math.exp(wh[0][1])), 3.4, fill=CH[c])
    mus = [math.exp(v) for v in f["a"]]
    ks = [math.exp(v) for v in f["b"]]
    for (p1, p2) in contour_segments(f["p"], mus, ks, f["levels"]["0.99"]):
        inner += line(ax.X(p1[0]), ax.Y(p1[1]), ax.X(p2[0]), ax.Y(p2[1]), stroke=ACCENT, sw=1.4)
    s += f'<g clip-path="url(#c6a)">{inner}</g>'
    s += mono(ax.X(0.62), ax.Y(0.55), "99% region", size=8, fill=ACCENT, anchor="start", weight="600")
    # panel (b): kept draws, contours and marginals
    bx = Axes(560, 150, 300, 250, (0.36, 0.60), (0.35, 2.0))
    s += title(bx.x0 - 30, 92, "(b) 1,200 of 20,000 kept draws; the grid's 50, 90 and 99% regions")
    s += bx.clip("c6b") + bx.frame([0.40, 0.45, 0.50, 0.55], [0.5, 1.0, 1.5, 2.0], xfmt=lambda v: f"{v:.2f}",
                                   yfmt=lambda v: f"{v:.1f}", xlab="mu, accidents per woman in five weeks", ylab=None)
    s += mono(bx.x0 - 34, bx.y0 + bx.h / 2, "k", size=9, fill=SOFT)
    inner = ""
    for a, b in f["draws_log"]:
        inner += dot(bx.X(math.exp(a)), bx.Y(math.exp(b)), 1.4, fill=LINK, op=0.45)
    for lev, sw_ in (("0.5", 1.3), ("0.9", 1.1), ("0.99", 1.0)):
        for (p1, p2) in contour_segments(f["p"], mus, ks, f["levels"][lev]):
            inner += line(bx.X(p1[0]), bx.Y(p1[1]), bx.X(p2[0]), bx.Y(p2[1]), stroke=ACCENT, sw=sw_)
    inner += dot(bx.X(G["mode_mu"]), bx.Y(G["mode_k"]), 3.6, fill=INK)
    s += f'<g clip-path="url(#c6b)">{inner}</g>'
    # top marginal of mu, right marginal of k (grid density per unit of mu or k = density of log / value)
    tx = Axes(bx.x0, 104, bx.w, 40, bx.xr, (0, 13))
    mh = f["mu_hist"]
    hist_mu = bars(tx, mh["lo"], mh["hi"], mh["counts"], sum(mh["counts"]), LINK, op=0.30)
    mm = f["mu_marg"]
    dens_mu = [d / x for d, x in zip(mm["dens_log"], mm["x"])]
    s += f'<g clip-path="url(#c6t)">{hist_mu}{polyline(curve(tx, mm["x"], dens_mu), INK, sw=1.3)}</g>'
    s += f'<clipPath id="c6t"><rect x="{tx.x0}" y="{tx.y0}" width="{tx.w}" height="{tx.h}"/></clipPath>'
    rx_ = Axes(bx.x0 + bx.w + 8, bx.y0, 70, bx.h, (0, 2.4), bx.yr)
    kh = f["k_hist"]
    wk = (kh["hi"] - kh["lo"]) / len(kh["counts"])
    hist_k = ""
    for i, c in enumerate(kh["counts"]):
        d = c / (sum(kh["counts"]) * wk)
        y1, y2 = kh["lo"] + i * wk, kh["lo"] + (i + 1) * wk
        hist_k += rect(rx_.X(0), rx_.Y(y2), rx_.X(d) - rx_.X(0), rx_.Y(y1) - rx_.Y(y2), fill=LINK, op=0.30, stroke="none", sw=0)
    km = f["k_marg"]
    dens_k = [d / x for d, x in zip(km["dens_log"], km["x"])]
    kcurve = [(rx_.X(d), rx_.Y(x)) for d, x in zip(dens_k, km["x"]) if bx.yr[0] <= x <= bx.yr[1]]
    s += f'<clipPath id="c6r"><rect x="{rx_.x0}" y="{rx_.y0}" width="{rx_.w}" height="{rx_.h}"/></clipPath>'
    s += f'<g clip-path="url(#c6r)">{hist_k}{polyline(kcurve, INK, sw=1.3)}</g>'
    mu_s, k_s = G["mu"], G["k"]
    s += note_lines(560, 470, [(f"grid: mu mean {mu_s['mean']:.4f} (SD {mu_s['sd']:.4f}); k mean {k_s['mean']:.4f}, median "
                                f"{k_s['q500']:.3f}, 95% {k_s['q025']:.3f} to {k_s['q975']:.3f}", INK),
                               (f"posterior mode ({G['mode_mu']:.4f}, {G['mode_k']:.4f}); k's mean sits above its mode: "
                                f"a right-skewed shape", MUTED)], size=8.5, gap=16)
    s += note_lines(96, 470, [("starts at the corners of a wide box,", MUTED), ("(log mu, log k) = (−2 or 1, −2 or 2)", MUTED)],
                    size=8.5, gap=16)
    s += legend(vh - 24, vw, [("warmup paths, chains 1-4", "line:" + INK + ":1.0"), ("kept draws", "dot:" + LINK + ":2"),
                              ("grid posterior regions", "line:" + ACCENT + ":1.3"), ("grid marginal", "line:" + INK + ":1.3"),
                              ("chain marginal", "bar:" + LINK + ":0.30"), ("posterior mode", "dot:" + INK + ":3.4")])
    return emit("06", "accidents-posterior-grid", "The sampler against a brute-force grid",
                "Metropolis draws of the negative binomial posterior for Greenwood and Yule's accident counts, against "
                "an 801 by 801 grid evaluation of the same posterior.", "a posterior with no closed form", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "autocorrelation of θ's draws at three steps (mean of the four chains' autocorrelations), and geyer's truncation")
    ax = Axes(96, 84, 840, 290, (0, 80), (-0.1, 1.0))
    s += ax.clip("c7") + title(ax.x0, ax.y0 - 16, "ρ_t: correlation between draws t iterations apart; τ = 1 + 2 Σ ρ_t sets ESS = S/τ")
    s += ax.frame([0, 10, 20, 30, 40, 50, 60, 70, 80], [0, 0.25, 0.5, 0.75, 1.0], xfmt=lambda v: f"{v}",
                  yfmt=lambda v: f"{v:.2f}", xlab="lag t", ylab="autocorrelation")
    cols = {"0.002": SOFT, "0.04": INK, "1.0": LINK}
    inner = line(ax.X(0), ax.Y(0), ax.X(80), ax.Y(0), stroke=RULE_SOLID, sw=0.8)
    for k, col in cols.items():
        inner += polyline(curve(ax, list(range(81)), TR[k]["acf"]), col, sw=1.6)
    stop = TR["0.04"]["max_t"] + 1
    inner += line(ax.X(stop), ax.Y(0.15), ax.X(stop), ax.Y(-0.1), stroke=INK, sw=1.0, dash="4,3")
    s += f'<g clip-path="url(#c7)">{inner}</g>'
    s += mono(ax.X(stop) + 6, ax.Y(0.10), f"step 0.04: Geyer's rule stops at lag {stop}", size=8, fill=INK, anchor="start", weight="600")
    s += note_lines(ax.X(44), ax.Y(0.62), [(f"step 0.002: τ = {TR['0.002']['tau']:.1f}, stops at lag {TR['0.002']['max_t'] + 1}", SOFT),
                                          (f"step 1.0: τ = {TR['1.0']['tau']:.1f}, stops at lag {TR['1.0']['max_t'] + 1}", LINK),
                                          (f"step 0.04: τ = {TR['0.04']['tau']:.2f}, ESS {TR['0.04']['ess_mean']:,.0f} of 20,000", INK)])
    s += legend(vh - 24, vw, [("step 0.002", "line:" + SOFT + ":1.6"), ("step 0.04", "line:" + INK + ":1.6"),
                              ("step 1.0", "line:" + LINK + ":1.6"), ("where Geyer's rule stops (step 0.04)", "dash:" + INK + ":1.0")])
    return emit("07", "autocorrelation-and-tau", "Autocorrelation is what ESS charges for",
                "Autocorrelation functions of the trial chain's draws at three proposal steps, with the integrated "
                "autocorrelation time each gives and where Geyer's rule stops the sum.", "how many independent draws", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 480
    reps = MC["reps"]
    s = eyebrow(32, 40, f"{reps:,} independent runs per step, four chains of 1,000 draws each, started from exact posterior draws")
    ax = Axes(96, 84, 840, 290, (0, 3), (0, 1.0))
    s += ax.clip("c8") + title(ax.x0, ax.y0 - 16, "share of runs whose estimate ± 1.96 standard errors contains the exact value (bars: ±1.96 MCSE of the share)")
    s += ax.frame([], [0, 0.25, 0.5, 0.75, 0.95, 1.0], yfmt=lambda v: f"{100 * v:.0f}%", ylab="coverage")
    inner = line(ax.X(0), ax.Y(0.95), ax.X(3), ax.Y(0.95), stroke=ACCENT, sw=1.2, dash="5,3")
    kinds = (("naive", "mean, naive SE = SD/√S", SOFT), ("ess_based", "mean, MCSE = SD/√ESS", INK),
             ("quantile", "VE 2.5% point, quantile MCSE", LINK))
    for g, k in enumerate(("0.008", "0.04", "0.25")):
        st = ST[k]
        for j, (key, _, col) in enumerate(kinds):
            x = ax.X(g + 0.28 + 0.22 * j)
            v = st[key]
            e = 1.96 * math.sqrt(v * (1 - v) / reps)
            inner += line(x, ax.Y(v - e), x, ax.Y(v + e), stroke=col, sw=1.4)
            inner += dot(x, ax.Y(v), 4.2, fill=col)
            inner += mono(x, ax.Y(v) + (18 if key != "naive" else -10), pct(v), size=8, fill=col, weight="600")
        s += mono(ax.X(g + 0.5), ax.Y(0) + 16, f"step {k}: acceptance {pct(st['acceptance'])}", size=8.5, fill=INK, weight="600")
        s += mono(ax.X(g + 0.5), ax.Y(0) + 30, f"median ESS {st['ess_median']:,.0f} of 4,000", size=8, fill=SOFT)
    s += f'<g clip-path="url(#c8)">{inner}</g>'
    s += mono(ax.X(3) - 4, ax.Y(0.95) - 5, "nominal 95%", size=8, fill=ACCENT, anchor="end")
    s += legend(vh - 24, vw, [(lab, "dot:" + col + ":4") for _, lab, col in kinds] + [("nominal 95%", "dash:" + ACCENT + ":1.2")])
    return emit("08", "mcse-coverage", "The naive standard error lies; the MCSE mostly does not",
                "Coverage of the exact posterior mean by estimate ± 1.96 standard errors, with the naive and the "
                "ESS-based standard error, and of the 2.5% quantile by its MCSE.", "how many independent draws", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "each R-hat on four failures: tangerine cells exceed 1.01, outlined cells exceed 1.1")
    sh, sc = C1000["shift"], C1000["scale"]
    i_sh = C1000["deltas"].index(0.5)
    i_sc = C1000["scales"].index(0.5)
    om = OM["diagnostics"]
    cases = [("shared trend", "4 chains from θ = 0.30,", "step 0.004, no warmup", TRD),
             ("one chain shifted", "0.5 SD; constructed,", "median of 400 runs", {k: sh[k][i_sh] for k in sh}),
             ("one chain half as wide", "SD 0.5; constructed,", "median of 400 runs", {k: sc[k][i_sc] for k in sc}),
             ("a mode no chain visited", "the bimodal posterior,", "all starts in one mode", om)]
    rows = (("unsplit", "unsplit (1992 form)"), ("split", "split (BDA3)"), ("bulk", "rank-normalised, bulk"),
            ("folded", "rank-normalised, folded"))
    x0, y0, cw, chh = 260, 120, 180, 52
    for j, (name, l1, l2, _) in enumerate(cases):
        cx = x0 + j * cw + cw / 2
        s += mono(cx, y0 - 44, name, size=9, fill=INK, weight="600")
        s += mono(cx, y0 - 29, l1, size=8, fill=SOFT)
        s += mono(cx, y0 - 16, l2, size=8, fill=SOFT)
    for i, (key, lab) in enumerate(rows):
        y = y0 + i * chh
        s += mono(x0 - 14, y + chh / 2 + 3, lab, size=8.5, fill=MUTED, anchor="end")
        for j, (_, _, _, vals) in enumerate(cases):
            v = vals[key]
            x = x0 + j * cw
            fill = ACCENT if v > 1.01 else "#ffffff"
            op = 0.22 if v > 1.01 else 1.0
            s += rect(x + 4, y + 4, cw - 8, chh - 8, fill=fill, op=op, stroke=INK if v > 1.1 else "rgba(45,49,66,0.30)",
                      sw=1.6 if v > 1.1 else 0.8)
            s += mono(x + cw / 2, y + chh / 2 + 4, f"{v:.4f}", size=10, fill=INK if v > 1.01 else MUTED,
                      weight="600" if v > 1.01 else "400")
    s += note_lines(96, y0 + 4 * chh + 30, [("The reported R-hat is the larger of the two rank-normalised values. Only the last "
                                             "column passes every variant at 1.01,", MUTED),
                                            (f"and its draws hold none of the {pct(BM['exact']['p_right'], 0)} of the posterior that lies in "
                                             "the other mode.", MUTED)],
                    size=8.5, gap=16)
    ly = vh - 24
    s += f'<line x1="32" y1="{ly - 8}" x2="{vw - 32}" y2="{ly - 8}" stroke="{RULE}" stroke-width="0.8"/>' + eyebrow(32, ly + 8, "legend", fill=SOFT)
    lx = 108
    for lab, fill, op, stroke, sw_ in (("above 1.01", ACCENT, 0.22, "rgba(45,49,66,0.30)", 0.8), ("above 1.1", ACCENT, 0.22, INK, 1.6),
                                       ("at or below 1.01", "#ffffff", 1.0, "rgba(45,49,66,0.30)", 0.8)):
        s += rect(lx, ly - 1, 22, 12, fill=fill, op=op, stroke=stroke, sw=sw_)
        s += mono(lx + 30, ly + 9, lab, size=8, fill=MUTED, anchor="start")
        lx += 30 + 5.4 * len(lab) + 28
    return emit("10", "what-each-rhat-sees", "Which R-hat sees which failure",
                "Four versions of R-hat on four ways chains fail to converge: a shared trend, a shifted chain, a narrow "
                "chain, and a mode no chain visited.", "what r-hat compares", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 540
    c250 = RH["constructed"]["250"]
    s = eyebrow(32, 40, "four chains of independent normal draws, one of them altered; median of 400 runs per point (Vehtari et al.'s appendix a)")
    ax = Axes(96, 92, 380, 290, (0, 1.6), (0.985, 1.2))
    s += ax.clip("c11a") + title(ax.x0, ax.y0 - 16, "(a) one chain shifted by δ SDs: split R-hat")
    s += ax.frame([0, 0.4, 0.8, 1.2, 1.6], [1.0, 1.05, 1.1, 1.15, 1.2], xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: f"{v:.2f}",
                  xlab="shift δ, in posterior SDs", ylab="median R-hat")
    inner = ""
    for lev in (1.01, 1.1):
        inner += line(ax.X(0), ax.Y(lev), ax.X(1.6), ax.Y(lev), stroke=ACCENT if lev == 1.01 else INK, sw=1.0, dash="4,3")
    inner += polyline(curve(ax, C1000["deltas"], C1000["shift"]["split"]), INK, sw=1.7)
    inner += polyline(curve(ax, c250["deltas"], c250["shift"]["split"]), MUTED, sw=1.2, dash="5,3")
    for lev, key in ((1.01, "shift_split_1.01"), (1.1, "shift_split_1.1")):
        xv = CR[key]
        inner += dot(ax.X(xv), ax.Y(lev), 4.4, fill=ACCENT if lev == 1.01 else INK)
    s += f'<g clip-path="url(#c11a)">{inner}</g>'
    s += mono(ax.X(CR["shift_split_1.01"]) + 10, ax.Y(1.003), f"1.01 at δ = {CR['shift_split_1.01']:.2f}", size=8, fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.X(CR["shift_split_1.1"]) - 8, ax.Y(1.1) - 8, f"1.1 at δ = {CR['shift_split_1.1']:.2f}", size=8, fill=INK, anchor="end", weight="600")
    bx = Axes(596, 92, 380, 290, (1.0, 0.05), (0.985, 1.2))
    s += bx.clip("c11b") + title(bx.x0, bx.y0 - 16, "(b) one chain with SD s times the others': folded and split R-hat")
    s += bx.frame([1.0, 0.75, 0.5, 0.25], [1.0, 1.05, 1.1, 1.15, 1.2], xfmt=lambda v: f"{v:.2f}", yfmt=lambda v: f"{v:.2f}",
                  xlab="SD ratio s (smaller to the right)", ylab="median R-hat")
    inner = ""
    for lev in (1.01, 1.1):
        inner += line(bx.X(1.0), bx.Y(lev), bx.X(0.05), bx.Y(lev), stroke=ACCENT if lev == 1.01 else INK, sw=1.0, dash="4,3")
    inner += polyline(curve(bx, C1000["scales"], C1000["scale"]["folded"]), INK, sw=1.7)
    inner += polyline(curve(bx, C1000["scales"], C1000["scale"]["split"]), LINK, sw=1.4)
    for lev, key in ((1.01, "scale_folded_1.01"), (1.1, "scale_folded_1.1")):
        inner += dot(bx.X(CR[key]), bx.Y(lev), 4.4, fill=ACCENT if lev == 1.01 else INK)
    s += f'<g clip-path="url(#c11b)">{inner}</g>'
    s += mono(bx.X(CR["scale_folded_1.01"]) - 8, bx.Y(1.01) - 8, f"1.01 at s = {CR['scale_folded_1.01']:.2f}", size=8, fill=ACCENT, anchor="end", weight="600")
    s += mono(bx.X(CR["scale_folded_1.1"]) + 8, bx.Y(1.1) + 14, f"1.1 at s = {CR['scale_folded_1.1']:.2f}", size=8, fill=INK, anchor="start", weight="600")
    s += mono(bx.X(0.75), bx.Y(0.9935), "split R-hat stays at 1.00: it cannot see scale", size=8, fill=LINK, anchor="start")
    s += note_lines(96, 446, [("Vehtari et al. (2021) report a third of an SD and one SD in (a), and three quarters and a quarter in (b).", MUTED),
                              (f"Folded R-hat at s = 0.5 is {C1000['scale']['folded'][C1000['scales'].index(0.5)]:.3f} and at 0.25 is "
                               f"{C1000['scale']['folded'][C1000['scales'].index(0.25)]:.3f}, so on a grid of quarters 1.1 is first passed at a quarter.", MUTED)],
                    size=8.5, gap=16)
    s += legend(vh - 24, vw, [("1,000 draws per chain", "line:" + INK + ":1.7"), ("250 draws per chain", "dash:" + MUTED + ":1.2"),
                              ("split R-hat in (b)", "line:" + LINK + ":1.4"), ("1.01", "dash:" + ACCENT + ":1.0"), ("1.1", "dash:" + INK + ":1.0")])
    return emit("11", "rhat-thresholds", "What 1.1 lets through",
                "Median split R-hat against the shift of one chain, and median folded R-hat against the spread of one "
                "chain, with the thresholds 1.01 and 1.1 and where each is crossed.", "is 1.1 close enough", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 620
    dens = BM["density"]
    s = eyebrow(32, 40, f"a constructed bimodal posterior, 0.7 n(0, 1) + 0.3 n(16, 1): exact mean {BM['exact']['mean']:g}, "
                        f"p(θ > 8) = {BM['exact']['p_right']:g}")
    runs = (("one_mode", "all four chains start near 0, step 2.4", OM), ("dispersed", "two start near 0, two near 16, step 2.4", DI),
            ("long_jumps", "all start near 0, step 16: proposals can reach the other mode", LJ))
    for i, (key, lab, r) in enumerate(runs):
        ax = Axes(96, 86 + i * 150, 560, 104, (-4, 20), (0, 0.42))
        cid = f"c12{i}"
        s += ax.clip(cid) + title(ax.x0, ax.y0 - 10, f"({'abc'[i]}) {lab}")
        s += ax.frame([-4, 0, 4, 8, 12, 16, 20] if i == 2 else [], [0, 0.2, 0.4], xfmt=lambda v: f"{v}", yfmt=lambda v: f"{v:.1f}",
                      xlab="θ" if i == 2 else None)
        inner = bars(ax, -4, 20, r["hist"], sum(r["hist"]), LINK, op=0.35)
        inner += polyline(curve(ax, dens["x"], dens["p"]), INK, sw=1.4)
        s += f'<g clip-path="url(#{cid})">{inner}</g>'
        d = r["diagnostics"]
        s += note_lines(690, ax.y0 + 14, [(f"R-hat {d['rank']:.4f}", ACCENT if d["rank"] > 1.01 else INK),
                                         (f"bulk ESS {d['ess_bulk']:,.1f}, tail ESS {d['ess_tail']:,.1f}", MUTED),
                                         (f"mean {r['mean']:.3f} (exact {BM['exact']['mean']:g})", INK),
                                         (f"P(θ > 8) {r['p_right']:.4f} (exact {BM['exact']['p_right']:g})", INK),
                                         (f"chains' shares above 8: " + ", ".join(f"{v:.2f}" for v in r["chain_share_right"]), SOFT)],
                        size=8.5, gap=15)
    s += note_lines(96, 548, [("Of 1,000 chains started near 0 with step 2.4 and run for 6,000 iterations, the share that ever reached the other mode:", MUTED),
                              (", ".join(f"{pct(CS[k]['share'])} at separation {float(k):g}" for k in ("10.0", "12.0", "14.0", "16.0"))
                               + ". R-hat is printed in tangerine where it exceeds 1.01.", MUTED)], size=8.5, gap=16)
    s += legend(vh - 24, vw, [("kept draws, four chains", "bar:" + LINK + ":0.35"), ("exact density", "line:" + INK + ":1.4")])
    return emit("12", "the-mode-no-chain-visited", "Perfect diagnostics, a third of the posterior missing",
                "Draws from three runs on a bimodal posterior against its exact density: chains started in one mode pass "
                "every diagnostic and miss the other mode.", "the mode no chain visited", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "rank plots: each chain's draws ranked among all chains, in 20 bins; uniform bars mean the chains agree")

    def rank_panel(x0, y0, hists, total, label):
        out = title(x0, y0 - 14, label)
        per = total / len(hists)
        exp_ = per / 20
        top = max(max(h) for h in hists)
        ymax = max(top, exp_ * 2.2)
        for c, h in enumerate(hists):
            ax = Axes(x0 + c * 96, y0, 86, 120, (0, 20), (0, ymax))
            out += rect(ax.x0, ax.y0, ax.w, ax.h, fill="#ffffff", stroke=RULE_SOLID, sw=0.8)
            for b, v in enumerate(h):
                out += rect(ax.X(b) + 0.4, ax.Y(v), ax.X(b + 1) - ax.X(b) - 0.8, ax.Y(0) - ax.Y(v), fill=SOFT, op=0.75,
                            stroke="none", sw=0)
            out += line(ax.x0, ax.Y(exp_), ax.x0 + ax.w, ax.Y(exp_), stroke=ACCENT, sw=1.0, dash="3,2")
            out += mono(ax.x0 + ax.w / 2, ax.y0 + ax.h + 13, f"chain {c + 1}", size=8, fill=SOFT)
        return out
    kk = NU["params"]["k"]
    s += rank_panel(96, 104, kk["rank_hist"], NU["draws"] * 4, f"(a) NUTS in PyMC, k: R-hat {kk['mine']['rank']:.4f}")
    s += rank_panel(560, 104, DI["rank_hist"], 20000, f"(b) bimodal, dispersed starts: R-hat {DI['diagnostics']['rank']:.4f}")
    # panel (c): ESS per draw, Metropolis against NUTS
    cx = Axes(250, 300, 560, 140, (0, 1.1), (0, 4))
    s += title(96, 290, "(c) bulk ESS per draw on the accidents model, the same priors and data")
    items = [("Metropolis, mu", NB["params"]["mu"]["diagnostics"]["ess_bulk"] / 20000, MUTED),
             ("Metropolis, k", NB["params"]["k"]["diagnostics"]["ess_bulk"] / 20000, MUTED),
             ("NUTS, mu", NU["params"]["mu"]["ess_per_draw"], LINK), ("NUTS, k", NU["params"]["k"]["ess_per_draw"], LINK)]
    for i, (lab, v, col) in enumerate(items):
        y = cx.y0 + 12 + i * 30
        s += rect(cx.X(0), y, cx.X(v) - cx.X(0), 18, fill=col, op=0.7, stroke="none", sw=0)
        s += mono(cx.X(0) - 10, y + 13, lab, size=8.5, fill=MUTED, anchor="end")
        s += mono(cx.X(v) - 8, y + 13, f"{v:.3f}", size=8.5, fill="#ffffff", anchor="end", weight="600")
    s += line(cx.X(1.0), cx.y0 + 4, cx.X(1.0), cx.y0 + 128, stroke=SOFT, sw=1.0, dash="4,3")
    s += mono(cx.X(1.0) + 4, cx.y0 + 4, "1 effective draw per draw", size=8, fill=SOFT, anchor="start")
    s += note_lines(96, 462, [(f"NUTS: {NU['mean_n_steps']:.2f} leapfrog steps per draw, {NU['divergences']} divergences, "
                               f"step size {NU['step_size']:.3f}; Metropolis: one density evaluation per draw", MUTED)], size=8.5)
    s += legend(vh - 24, vw, [("ranks, each chain", "bar:" + SOFT + ":0.75"), ("uniform level", "dash:" + ACCENT + ":1.0"),
                              ("Metropolis", "bar:" + MUTED + ":0.7"), ("NUTS", "bar:" + LINK + ":0.7")])
    return emit("13", "nuts-rank-plots", "Rank plots show what R-hat summarises",
                "Rank plots for PyMC's NUTS chains on the accidents model and for the stuck bimodal chains, and the "
                "effective sample size per draw of both samplers.", "nuts in pymc", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "10": fig10, "11": fig11, "12": fig12, "13": fig13}

if __name__ == "__main__":
    for k in (sys.argv[1:] or sorted(FIGS)):
        FIGS[k]()
