#!/usr/bin/env python3
"""Figures 01-10 for resampling-and-aliasing.

Every value drawn here is computed in this file from the kernels' definitions — Keys
1981 eq. (4), Mitchell-Netravali eq. (8), the box, the triangle and sinc(x)·sinc(x/3) —
on row r2 of the shared patch, with the same half-pixel convention and edge replication
the article uses. Nothing is measured. Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, alabel, box, cell, emit, eyebrow,
                    hline, legend, masked, mono, node, txt, vline)

SER1, SER2, SER3, SER4 = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50"
ROW = [40, 255, 40, 200, 200]
CLEAN = [40, 40, 40, 200, 200]
N = 5
COL = {"nearest": SER4, "linear": SER1, "cubic": SER2, "lanczos3": SER3}
NAME = {"nearest": "nearest", "linear": "linear", "cubic": "Keys, a = −1/2",
        "lanczos3": "Lanczos-3"}


# ------------------------------------------------------------------ kernels
def box_k(x):
    return 1.0 if -0.5 < x <= 0.5 else 0.0


def tri(x):
    x = abs(x)
    return 1.0 - x if x < 1 else 0.0


def keys(x, a=-0.5):
    x = abs(x)
    if x < 1:
        return (a + 2) * x ** 3 - (a + 3) * x ** 2 + 1
    if x < 2:
        return a * x ** 3 - 5 * a * x ** 2 + 8 * a * x - 4 * a
    return 0.0


def sinc(x):
    return 1.0 if x == 0 else math.sin(math.pi * x) / (math.pi * x)


def lanczos(x, n=3):
    return sinc(x) * sinc(x / n) if -n < x < n else 0.0


def bc(x, B, C):
    x = abs(x)
    if x < 1:
        return ((12 - 9 * B - 6 * C) * x ** 3 + (-18 + 12 * B + 6 * C) * x ** 2 + (6 - 2 * B)) / 6
    if x < 2:
        return ((-B - 6 * C) * x ** 3 + (6 * B + 30 * C) * x ** 2 + (-12 * B - 48 * C) * x
                + (8 * B + 24 * C)) / 6
    return 0.0


KERN = {"nearest": (box_k, 0.5), "linear": (tri, 1), "cubic": (keys, 2), "lanczos3": (lanczos, 3)}


def clamp(i):
    return min(max(i, 0), N - 1)


def taps(x, name, row=ROW):
    """(index, clamped index, weight) for one output at x, OpenCV-style edges."""
    if name == "nearest":
        c = clamp(math.floor(x + 0.5))
        return [(c, c, 1.0)]
    k, sup = KERN[name]
    lo = math.floor(x) - sup + 1
    t = [(i, clamp(i), k(x - i)) for i in range(lo, lo + 2 * sup)]
    if name == "lanczos3":
        s = sum(w for _, _, w in t)
        t = [(i, c, w / s) for i, c, w in t]
    return t


def value(x, name, row=ROW):
    return sum(row[c] * w for _, c, w in taps(x, name, row))


def recon(x, name, row=ROW):
    """Continuous reconstruction f^(x) = sum f[k] h(x-k), edges replicated, Lanczos normalised."""
    k, sup = KERN[name]
    lo = math.floor(x) - int(math.ceil(sup)) - 1
    ws = [(clamp(i), k(x - i)) for i in range(lo, lo + 2 * int(math.ceil(sup)) + 3)]
    if name == "lanczos3":
        s = sum(w for _, w in ws)
        ws = [(c, w / s) for c, w in ws]
    return sum(row[c] * w for c, w in ws)


def ft(h, sup, nu, steps=1200):
    step = sup / steps
    s = 0.0
    for i in range(steps + 1):
        x = i * step
        w = 1 if i in (0, steps) else (4 if i % 2 else 2)
        s += w * h(x) * math.cos(2 * math.pi * nu * x)
    return 2 * s * step / 3


def H(name, nu):
    if name == "nearest":
        return sinc(nu)
    if name == "linear":
        return sinc(nu) ** 2
    k, sup = KERN[name]
    return ft(k, sup, nu)


def centres(n_out, s):
    return [(j + 0.5) / s - 0.5 for j in range(n_out)]


XS_DN = centres(3, 0.6)
XS_UP = centres(8, 1.7)


# ------------------------------------------------------------------ plotting helpers
def polyline(pts, stroke, sw=1.4, dash=None, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity else ""
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}{o}/>')


def area_fill(pts, y0, fill, opacity=0.18):
    """Fill between a polyline and the horizontal line y0."""
    if not pts:
        return ""
    d = f"M {pts[0][0]:.1f} {y0:.1f} " + " ".join(f"L {x:.1f} {y:.1f}" for x, y in pts)
    d += f" L {pts[-1][0]:.1f} {y0:.1f} Z"
    return f'<path d="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="none"/>'


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xr, self.yr = xr, yr

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def curve(self, f, a, b, n=400):
        return [(self.X(a + (b - a) * i / n), self.Y(f(a + (b - a) * i / n))) for i in range(n + 1)]

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid=True, zero=True):
        s = (f'<line x1="{self.x0}" y1="{self.y0 + self.h}" x2="{self.x0 + self.w}" '
             f'y2="{self.y0 + self.h}" stroke="{RULE_SOLID}" stroke-width="1"/>')
        s += (f'<line x1="{self.x0}" y1="{self.y0}" x2="{self.x0}" y2="{self.y0 + self.h}" '
              f'stroke="{RULE_SOLID}" stroke-width="1"/>')
        for v in yt:
            yy = self.Y(v)
            if grid:
                s += (f'<line x1="{self.x0}" y1="{yy:.1f}" x2="{self.x0 + self.w}" y2="{yy:.1f}" '
                      f'stroke="{RULE}" stroke-width="0.8"/>')
            s += mono(self.x0 - 7, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            s += mono(self.X(v), self.y0 + self.h + 14, xfmt(v), size=8, fill=SOFT)
        if zero and self.yr[0] < 0 < self.yr[1]:
            s += (f'<line x1="{self.x0}" y1="{self.Y(0):.1f}" x2="{self.x0 + self.w}" '
                  f'y2="{self.Y(0):.1f}" stroke="{RULE_SOLID}" stroke-width="0.9"/>')
        if xlab:
            s += eyebrow(self.x0 + self.w, self.y0 + self.h + 30, xlab, anchor="end")
        if ylab:
            s += eyebrow(self.x0, self.y0 - 10, ylab, anchor="start")
        return s


def dot(x, y, r=3.2, fill=INK, stroke=None):
    st = f' stroke="{stroke}" stroke-width="1.2"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{st}/>'


def fmt(v, nd=2):
    s = f"{v:.{nd}f}"
    return s.replace("-", "−")


def wfmt(v):
    if abs(v) < 5e-5:
        return "0"
    if abs(v - round(v)) < 5e-5:
        return str(int(round(v)))
    return f"{v:.3f}".replace("-", "−")


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 440
    s = eyebrow(32, 40, "shrink row r2 to 0.6×: where do the three new samples sit?")
    cw, gx = 116, 214
    def px(x):                         # input-pixel coordinate (centres at integers) -> px
        return gx + (x + 0.5) * cw
    # input cells
    y0 = 70
    for i, v in enumerate(ROW):
        hi = i == 1
        s += cell(gx + i * cw, y0, cw, 40, v, fill=ACCENT_TINT if hi else "#ffffff",
                  stroke=ACCENT if hi else "rgba(45,49,66,0.30)",
                  tcolor=ACCENT if hi else INK, size=13, weight="600" if hi else "500")
        s += mono(gx + i * cw + cw / 2, y0 + 56, f"c{i}", size=9, fill=SOFT)
        s += dot(px(i), y0 + 40, r=2.4, fill=MUTED)
    s += txt(32, y0 + 25, "input row r2", size=12, weight="600", anchor="start")
    s += mono(32, y0 + 41, "sample at each cell's centre", size=8, fill=SOFT, anchor="start")
    # coordinate ruler
    ry = y0 + 76
    s += f'<line x1="{px(-0.5)}" y1="{ry}" x2="{px(4.5)}" y2="{ry}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for t in range(-0, 5):
        s += f'<line x1="{px(t)}" y1="{ry - 4}" x2="{px(t)}" y2="{ry + 4}" stroke="{SOFT}" stroke-width="1"/>'
        s += mono(px(t), ry + 16, str(t), size=8, fill=SOFT)
    for t in (-0.5, 4.5):
        s += f'<line x1="{px(t)}" y1="{ry - 6}" x2="{px(t)}" y2="{ry + 6}" stroke="{SOFT}" stroke-width="1"/>'
        s += mono(px(t), ry + 16, fmt(t, 1), size=8, fill=SOFT)
    s += eyebrow(px(4.5) + 16, ry + 3, "x, input pixels", anchor="start")

    rows = [
        ("pixel centres", "OpenCV linear / cubic, Pillow",
         XS_DN, [0, 2, 4], ["1/3", "2", "11/3"], "c0 · c2 · c4", "40 · 40 · 200", False),
        ("floor index ⌊j/s⌋", "OpenCV INTER_NEAREST",
         [-0.5, 7 / 6, 17 / 6], [0, 1, 3], ["−0.5", "1.17", "2.83"], "c0 · c1 · c3", "40 · 255 · 200", True),
        ("corner-aligned", "SciPy zoom, grid_mode=False",
         [0, 2, 4], [0, 2, 4], ["0", "2", "4"], "c0 · c2 · c4", "40 · 40 · 200", False),
    ]
    y = ry + 58
    for title, who, xs, picks, labs, reads, vals, focal in rows:
        colour = ACCENT if focal else INK
        s += txt(32, y + 4, title, size=12, weight="600", anchor="start", fill=colour)
        s += mono(32, y + 20, who, size=8, fill=SOFT, anchor="start")
        # output cells (width 5/3) as brackets
        for j in range(3):
            a, b = -0.5 + j * 5 / 3, -0.5 + (j + 1) * 5 / 3
            s += (f'<rect x="{px(a) + 1:.1f}" y="{y - 12}" width="{(b - a) * cw - 2:.1f}" height="24" rx="3" '
                  f'fill="rgba(45,49,66,0.03)" stroke="rgba(45,49,66,0.22)" stroke-width="0.8"/>')
        for x, lab in zip(xs, labs):
            s += (f'<line x1="{px(x):.1f}" y1="{y - 12}" x2="{px(x):.1f}" y2="{y + 12}" '
                  f'stroke="{colour}" stroke-width="1.4"/>')
            s += dot(px(x), y, r=4, fill=PAPER, stroke=colour)
            s += mono(px(x), y + 26, lab, size=8, fill=colour)
        s += mono(px(4.5) + 16, y - 1, reads, size=10, fill=colour, anchor="start", weight="600")
        s += mono(px(4.5) + 16, y + 14, vals, size=9, fill=MUTED, anchor="start")
        y += 72
    s += legend(vh - 30, vw, [("output cell, 5/3 input pixels wide", MUTED, "box"),
                              ("sample point", INK, "line"),
                              ("the only grid that reads the impulse", ACCENT, "dot")])
    return emit("01", "where-the-samples-sit", "Where do the new samples sit?",
                "Three coordinate conventions for the same 0.6× nearest-neighbour shrink of row r2.",
                "the problem", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 700
    s = eyebrow(32, 40, "row r2 shrunk to 0.6× — every kernel's window under every output")
    xr = (-3.2, 7.2)
    top = Axes(190, 70, 620, 96, xr, (0, 280))
    # row as stems
    for i in range(-3, 8):
        v = ROW[clamp(i)]
        faint = not 0 <= i < N
        col = ACCENT if i == 1 else (SOFT if faint else INK)
        s += (f'<line x1="{top.X(i):.1f}" y1="{top.Y(0):.1f}" x2="{top.X(i):.1f}" y2="{top.Y(v):.1f}" '
              f'stroke="{col}" stroke-width="{1 if faint else 2}"'
              f'{" stroke-dasharray=\"2,3\"" if faint else ""}/>')
        s += dot(top.X(i), top.Y(v), r=2.6 if faint else 3.2, fill=col)
        if not faint:
            s += mono(top.X(i), top.Y(v) - 8, str(v), size=8, fill=col, weight="500")
            s += masked(top.X(i), top.y0 + top.h + 16, f"c{i}", size=8, fill=SOFT, pad=4)
    s += f'<line x1="{top.X(xr[0])}" y1="{top.Y(0)}" x2="{top.X(xr[1])}" y2="{top.Y(0)}" stroke="{RULE_SOLID}"/>'
    s += txt(32, 110, "row r2", size=12, weight="600", anchor="start")
    s += mono(32, 126, "dashed stems: edge pixel", size=8, fill=SOFT, anchor="start")
    s += mono(32, 139, "replicated past the row", size=8, fill=SOFT, anchor="start")
    # output position lines through all strips
    ybot = 640
    for j, x in enumerate(XS_DN):
        s += (f'<line x1="{top.X(x):.1f}" y1="{top.y0 - 4}" x2="{top.X(x):.1f}" y2="{ybot}" '
              f'stroke="{ACCENT}" stroke-width="0.9" stroke-dasharray="4,4" stroke-opacity="0.7"/>')
        s += masked(top.X(x), top.y0 - 8, f"x{j} = {['1/3', '2', '11/3'][j]}", size=8, fill=ACCENT)
    for i in range(N):
        s += masked(top.X(i), top.y0 + top.h + 16, f"c{i}", size=8, fill=SOFT, pad=4)
    s += mono(846, 96, "outputs", size=8, fill=SOFT, anchor="start", track="0.12em")
    s += mono(846, 108, "j0 · j1 · j2", size=8, fill=SOFT, anchor="start")
    # strips
    y = 210
    for name in ["nearest", "linear", "cubic", "lanczos3"]:
        ax = Axes(190, y, 620, 84, xr, (-0.25, 1.1))
        col = COL[name]
        s += f'<line x1="{ax.X(xr[0])}" y1="{ax.Y(0):.1f}" x2="{ax.X(xr[1])}" y2="{ax.Y(0):.1f}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
        k, sup = KERN[name]
        outs = []
        for j, x in enumerate(XS_DN):
            if name == "nearest":
                pts = [(ax.X(x - 0.5), ax.Y(0)), (ax.X(x - 0.5), ax.Y(1)),
                       (ax.X(x + 0.5), ax.Y(1)), (ax.X(x + 0.5), ax.Y(0))]
            else:
                pts = ax.curve(lambda u, x=x: k(u - x), x - sup, x + sup, n=240)
            s += area_fill(pts, ax.Y(0), col, 0.10)
            s += polyline(pts, col, sw=1.3)
            ts = taps(x, name)
            for i, c, w in ts:
                if abs(w) < 1e-6:
                    continue
                on_imp = c == 1
                s += dot(ax.X(i), ax.Y(w), r=3.2, fill=ACCENT if on_imp else col)
            outs.append(value(x, name))
        s += txt(32, y + 34, NAME[name], size=12, weight="600", anchor="start", fill=col)
        s += mono(32, y + 50, {"nearest": "1 tap", "linear": "2 taps", "cubic": "4 taps",
                               "lanczos3": "6 taps, normalised"}[name], size=8, fill=SOFT, anchor="start")
        s += mono(846, y + 40, " · ".join(fmt(o) if abs(o - round(o)) > 0.004 else str(int(round(o)))
                                          for o in outs), size=10, fill=INK, anchor="start", weight="600")
        s += mono(846, y + 55, f"mean {sum(outs) / 3:.1f}", size=8, fill=SOFT, anchor="start")
        y += 108
    s += mono(846, y - 30, "input mean 147", size=8, fill=ACCENT, anchor="start", weight="500")
    s += legend(vh - 22, vw, [("kernel centred on an output", MUTED, "line"),
                              ("a tap and its weight", INK, "dot"),
                              ("a tap on the impulse c1", ACCENT, "dot")])
    return emit("02", "shrink-taps", "Shrinking to 0.6×: which pixels each kernel reads",
                "Four kernels centred on the three output positions of row r2; dots are the taps.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def ringing(x, v):
    """Below 40, above 200 on the step (not beside the impulse), or past 255."""
    near_impulse = abs(x - 1) < 1
    return v < 40 - 0.05 or v > 255 or (v > 200.05 and not near_impulse)


def fig03():
    vw, vh = 1016, 660
    s = eyebrow(32, 40, "row r2 enlarged to 1.7× — eight samples read off one curve per kernel")
    names = ["nearest", "linear", "cubic", "lanczos3"]
    for idx, name in enumerate(names):
        cx = 96 + (idx % 2) * 470
        cy = 96 + (idx // 2) * 280
        ax = Axes(cx, cy, 390, 190, (-0.6, 4.6), (0, 280))
        col = COL[name]
        s += ax.frame([0, 1, 2, 3, 4], [0, 40, 200, 255], xfmt=lambda v: f"c{v}",
                      yfmt=str, grid=False, zero=False)
        for lvl, lab in ((40, None), (200, None), (255, "8-bit ceiling")):
            s += (f'<line x1="{ax.x0}" y1="{ax.Y(lvl):.1f}" x2="{ax.x0 + ax.w}" y2="{ax.Y(lvl):.1f}" '
                  f'stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="3,3"/>')
            if lab:
                s += mono(ax.x0 + ax.w, ax.Y(lvl) - 5, lab, size=7, fill=SOFT, anchor="end")
        if name == "nearest":
            pts = []
            for i in range(N):
                a_, b_ = max(i - 0.5, -0.5), min(i + 0.5, 4.5)
                pts += [(ax.X(a_), ax.Y(ROW[i])), (ax.X(b_), ax.Y(ROW[i]))]
        else:
            pts = ax.curve(lambda u: recon(u, name), -0.5, 4.5, n=500)
        s += polyline(pts, col, sw=1.6)
        for i in range(N):
            s += dot(ax.X(i), ax.Y(ROW[i]), r=2.4, fill=MUTED)
        vals = []
        for j, x in enumerate(XS_UP):
            v = value(x, name)
            vals.append(v)
            hot = ringing(x, v)
            c = ACCENT if hot else INK
            s += (f'<line x1="{ax.X(x):.1f}" y1="{ax.y0 + ax.h}" x2="{ax.X(x):.1f}" y2="{ax.Y(v):.1f}" '
                  f'stroke="{c}" stroke-width="0.7" stroke-opacity="0.45"/>')
            s += dot(ax.X(x), ax.Y(v), r=3.6 if hot else 3, fill=c)
            if hot:
                if v < 120:            # low points: label to the right, clear of the axis
                    s += masked(ax.X(x) + 10, ax.Y(v) + 4, fmt(v, 1), size=8, fill=ACCENT,
                                anchor="start", pad=3)
                else:                  # high points: label above
                    s += masked(ax.X(x), ax.Y(v) - 10, fmt(v, 1), size=8, fill=ACCENT, pad=3)
        s += txt(cx, cy - 22, NAME[name], size=12, weight="600", anchor="start", fill=col)
        head = " ".join((str(int(v)) if name == "nearest" else f"{v:.1f}") for v in vals)
        s += mono(cx + ax.w, cy - 22, head, size=8, fill=MUTED, anchor="end")
    s += legend(vh - 26, vw, [("reconstruction f̂(x)", MUTED, "line"),
                              ("input sample", MUTED, "dot"),
                              ("output sample", INK, "dot"),
                              ("below 40, above 200 at the step, or past 255", ACCENT, "dot")])
    return emit("03", "enlarge-reconstructions", "Enlarging to 1.7×: one curve per kernel",
                "Each kernel's continuous reconstruction of row r2, with the eight output samples.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def elabel(x, y, s_, fill=SOFT, gap=18):
    """Edge label that keeps its case (f[k] is not F[K]), on an opaque plate."""
    w = 5.2 * len(s_) + 14
    return (f'<rect x="{x - w / 2:.1f}" y="{y - gap}" width="{w:.1f}" height="13" rx="2" fill="{PAPER}"/>'
            + mono(x, y - gap + 10, s_, size=8, fill=fill))


def fig04():
    vw, vh = 1016, 530
    s = eyebrow(32, 40, "one pipeline, two regimes — which Nyquist frequency is lower decides the prefilter's job")
    bw, bh = 160, 64
    xs = [40, 292, 544, 796]
    rows = [
        ("enlarge 1.7×", 96, [
            ("samples f[k]", "5 px · band ≤ 0.5", "input"),
            ("reconstruct", "kernel h · 1–4 px", "backend"),
            ("prefilter", "nothing to remove", "external"),
            ("sample", "every 0.588 px → 8", "backend")],
         ["f[k]", "f̂(x) ≤ 0.5", "as is"], 0.85, None),
        ("shrink 0.6×", 316, [
            ("samples f[k]", "5 px · band ≤ 0.5", "input"),
            ("reconstruct", "kernel h", "backend"),
            ("prefilter", "cut 0.3 – 0.5 cyc/px", "focal"),
            ("sample", "every 1.667 px → 3", "backend")],
         ["f[k]", "f̂(x) ≤ 0.5", "≤ 0.3"], 0.30, (0.30, 0.50)),
    ]
    for title, y, boxes, edges, nyq, cut in rows:
        s += txt(40, y - 16, title, size=13, weight="600", anchor="start",
                 fill=ACCENT if cut else INK)
        for (name, sub, kind), x in zip(boxes, xs):
            s += node(x, y, bw, bh, name, sub=sub, kind=kind)
        for i, lab in enumerate(edges):
            x1, x2 = xs[i] + bw, xs[i + 1]
            hot = bool(cut) and i == 2
            s += hline(x1, x2 - 2, y + bh / 2, stroke=ACCENT if hot else MUTED,
                       marker="arrow-accent" if hot else "arrow")
            s += elabel((x1 + x2) / 2, y + bh / 2, lab, fill=ACCENT if hot else SOFT)
        # spectrum strip, under the three stages that act on the signal
        ax = Axes(xs[1], y + bh + 40, xs[3] + bw - xs[1], 38, (0, 1.0), (0, 1))
        s += f'<line x1="{ax.X(0)}" y1="{ax.Y(0)}" x2="{ax.X(1.0)}" y2="{ax.Y(0)}" stroke="{RULE_SOLID}"/>'
        s += (f'<rect x="{ax.X(0)}" y="{ax.Y(1)}" width="{ax.X(0.5) - ax.X(0)}" height="{ax.h}" '
              f'fill="rgba(45,49,66,0.06)" stroke="none"/>')
        s += mono(ax.X(0.015), ax.Y(0.5) + 3, "input holds 0 – 0.5", size=8, fill=MUTED, anchor="start")
        if cut:
            s += (f'<rect x="{ax.X(cut[0])}" y="{ax.Y(1)}" width="{ax.X(cut[1]) - ax.X(cut[0])}" '
                  f'height="{ax.h}" fill="{ACCENT}" fill-opacity="0.16" stroke="none"/>')
            s += mono((ax.X(0.3) + ax.X(0.5)) / 2, ax.Y(0.5) + 3, "folds unless removed",
                      size=8, fill=ACCENT)
        s += (f'<line x1="{ax.X(nyq)}" y1="{ax.Y(1) - 6}" x2="{ax.X(nyq)}" y2="{ax.Y(0)}" '
              f'stroke="{ACCENT if cut else INK}" stroke-width="1.4"/>')
        s += mono(ax.X(nyq) + (6 if not cut else -6), ax.Y(1) - 10,
                  f"new Nyquist {nyq:.2f}", size=8, fill=ACCENT if cut else INK,
                  anchor="start" if not cut else "end", weight="600")
        for v in (0, 0.25, 0.5, 0.75, 1.0):
            s += mono(ax.X(v), ax.Y(0) + 14, f"{v:g}", size=7, fill=SOFT)
        s += eyebrow(ax.x0 - 12, ax.Y(0.5) + 3, "cycles / input px", anchor="end")
    s += legend(vh - 26, vw, [("stage", INK, "box"), ("the prefilter a shrink needs", ACCENT, "box"),
                              ("stage with nothing to do", SOFT, "box")])
    return emit("04", "two-regimes", "Reconstruct, prefilter, sample",
                "The same three stages at 1.7× and at 0.6×, with each grid's Nyquist frequency.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 380
    s = eyebrow(32, 40, "four kernels over the sinc they approximate")
    specs = [("nearest", "box", 1, box_k, 0.5), ("linear", "triangle", 2, tri, 1),
             ("cubic", "Keys cubic", 4, keys, 2), ("lanczos3", "Lanczos-3", 6, lanczos, 3)]
    for idx, (name, title, ntap, k, sup) in enumerate(specs):
        ax = Axes(56 + idx * 240, 96, 200, 190, (-3.4, 3.4), (-0.3, 1.1))
        col = COL[name]
        s += ax.frame([-3, -2, -1, 0, 1, 2, 3], [0, 0.5, 1], yfmt=lambda v: f"{v:g}", grid=False)
        s += polyline(ax.curve(sinc, -3.4, 3.4, 400), MUTED, sw=0.9, dash="3,3", opacity=0.55)
        if name == "nearest":
            pts = [(ax.X(-3.4), ax.Y(0)), (ax.X(-0.5), ax.Y(0)), (ax.X(-0.5), ax.Y(1)),
                   (ax.X(0.5), ax.Y(1)), (ax.X(0.5), ax.Y(0)), (ax.X(3.4), ax.Y(0))]
        else:
            pts = ax.curve(k, -3.4, 3.4, 600)
        # negative lobes
        if name in ("cubic", "lanczos3"):
            for sign in (-1, 1):
                a, b = (1, 2) if sign > 0 else (-2, -1)
                neg = ax.curve(k, a, b, 80)
                s += area_fill(neg, ax.Y(0), ACCENT, 0.22)
        if name == "cubic":
            s += polyline(ax.curve(lambda u: keys(u, -0.75), -2, 2, 300), col, sw=1, dash="5,3")
            s += mono(ax.X(1.9), ax.Y(0.55), "a = −3/4", size=7, fill=col, anchor="start")
            s += mono(ax.X(1.9), ax.Y(0.43), "(dashed)", size=7, fill=SOFT, anchor="start")
        s += polyline(pts, col, sw=1.8)
        s += txt(ax.x0, ax.y0 - 26, title, size=12, weight="600", anchor="start", fill=col)
        s += mono(ax.x0 + ax.w, ax.y0 - 26, f"{ntap} tap{'s' if ntap > 1 else ''}", size=9,
                  fill=INK, anchor="end", weight="600")
        # support bracket
        yb = ax.y0 + ax.h + 32
        s += (f'<line x1="{ax.X(-sup):.1f}" y1="{yb}" x2="{ax.X(sup):.1f}" y2="{yb}" '
              f'stroke="{col}" stroke-width="1.2"/>')
        for e in (-sup, sup):
            s += f'<line x1="{ax.X(e):.1f}" y1="{yb - 4}" x2="{ax.X(e):.1f}" y2="{yb + 4}" stroke="{col}" stroke-width="1.2"/>'
        s += mono(ax.X(0), yb + 14, f"support ±{sup:g}", size=8, fill=col)
    s += legend(vh - 22, vw, [("kernel h(x)", INK, "line"), ("ideal sinc (dashed)", MUTED, "line"),
                              ("negative lobe", ACCENT, "box")])
    return emit("05", "four-kernels", "Four kernels and the sinc",
                "Box, triangle, Keys' cubic and Lanczos-3, evaluated from their definitions.",
                "kernels in frequency", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "transfer functions — what each kernel passes, frequency by frequency")
    ax = Axes(96, 84, 600, 340, (0, 1.5), (-0.25, 1.1))
    s += ax.frame([0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5], [0, 0.25, 0.5, 0.75, 1.0],
                  xlab="frequency ν, cycles per input pixel", ylab="gain H(ν)",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    # band to remove for a 0.6x shrink
    s += (f'<rect x="{ax.X(0.3):.1f}" y="{ax.Y(1.1):.1f}" width="{ax.X(0.5) - ax.X(0.3):.1f}" '
          f'height="{ax.Y(-0.25) - ax.Y(1.1):.1f}" fill="{ACCENT}" fill-opacity="0.08"/>')
    for v, lab, col, dx in ((0.5, "Nyquist, input grid", INK, 6), (0.3, "Nyquist after 0.6×", ACCENT, -6)):
        s += (f'<line x1="{ax.X(v):.1f}" y1="{ax.Y(1.1):.1f}" x2="{ax.X(v):.1f}" y2="{ax.Y(-0.25):.1f}" '
              f'stroke="{col}" stroke-width="1" stroke-dasharray="4,3"/>')
        s += mono(ax.X(v) + dx, ax.Y(1.07), lab, size=8, fill=col, anchor="start" if dx > 0 else "end")
    # ideal
    s += polyline([(ax.X(0), ax.Y(1)), (ax.X(0.5), ax.Y(1)), (ax.X(0.5), ax.Y(0)), (ax.X(1.5), ax.Y(0))],
                  INK, sw=1.2, dash="6,3")
    for name in ["nearest", "linear", "cubic", "lanczos3"]:
        pts = [(ax.X(i / 200 * 1.5), ax.Y(H(name, i / 200 * 1.5))) for i in range(201)]
        s += polyline(pts, COL[name], sw=1.8)
        s += dot(ax.X(0.4), ax.Y(H(name, 0.4)), r=3, fill=COL[name])
    s += masked(ax.X(0.4), ax.Y(-0.19), "0.3 – 0.5: must go before a 0.6× shrink", size=8, fill=ACCENT)
    # value table
    tx, ty = 730, 100
    s += eyebrow(tx, ty, "gain at", anchor="start")
    heads = ["0.25", "0.4", "0.75"]
    for c, h in enumerate(heads):
        s += mono(tx + 138 + c * 48, ty + 20, f"ν={h}", size=8, fill=SOFT, anchor="middle")
    rows = [("ideal, enlarge", "ie"), ("ideal, 0.6× shrink", "is")] + \
        [(NAME[n], n) for n in ["nearest", "linear", "cubic", "lanczos3"]]
    for r, (lab, n) in enumerate(rows):
        yy = ty + 44 + r * 26
        col = INK if n in ("ie", "is") else COL[n]
        s += txt(tx, yy, lab, size=10, fill=col, anchor="start", weight="600")
        if n in ("ie", "is"):
            vals = [1.0, 1.0 if n == "ie" else 0.0, 0.0]
        else:
            vals = [H(n, 0.25), H(n, 0.4), H(n, 0.75)]
        for c, v in enumerate(vals):
            hi = c == 1 and n not in ("ie", "is")
            s += mono(tx + 138 + c * 48, yy, f"{v:g}" if n in ("ie", "is") else fmt(v, 3), size=9,
                      fill=ACCENT if hi else INK, weight="600" if hi else "400")
    s += mono(tx, ty + 44 + 6 * 26 + 8, "ν = 0.4 lies above the 0.6× Nyquist:", size=8, fill=ACCENT, anchor="start")
    s += mono(tx, ty + 44 + 6 * 26 + 21, "whatever passes there folds", size=8, fill=ACCENT, anchor="start")
    s += legend(vh - 22, vw, [(NAME["nearest"], COL["nearest"], "line"), (NAME["linear"], COL["linear"], "line"),
                              (NAME["cubic"], COL["cubic"], "line"), (NAME["lanczos3"], COL["lanczos3"], "line"),
                              ("ideal box (dashed)", INK, "line")])
    return emit("06", "transfer-functions", "What each kernel passes",
                "Transfer functions of four kernels against the ideal box, evaluated from their definitions.",
                "kernels in frequency", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def step_overshoot(B, C):
    best = 0
    for i in range(0, 3000):
        x = i / 1000
        best = max(best, sum(bc(x - k, B, C) for k in range(0, 6)))
    return best - 1


def fig07():
    vw, vh = 1016, 540
    s = eyebrow(32, 40, "Mitchell–Netravali's (B, C) plane — every \"bicubic\" is one point on it")
    ax = Axes(110, 84, 520, 380, (-0.1, 1.2), (-0.1, 1.15))
    s += ax.frame([0, 0.25, 0.5, 0.75, 1.0], [0, 0.25, 0.5, 0.75, 1.0], xlab="B — blur, and loss of interpolation",
                  ylab="C — ringing", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", grid=True, zero=False)
    # interpolating axis
    s += (f'<line x1="{ax.X(0):.1f}" y1="{ax.Y(-0.1):.1f}" x2="{ax.X(0):.1f}" y2="{ax.Y(1.15):.1f}" '
          f'stroke="{INK}" stroke-width="2"/>')
    s += masked(ax.X(0) + 6, ax.Y(1.12), "B = 0: passes through the samples", size=8, fill=INK, anchor="start")
    pts = [
        ("cubic B-spline", 1.0, 0.0, False, (-10, -30), "end"),
        ("Mitchell (1/3, 1/3)", 1 / 3, 1 / 3, False, (10, 4), "start"),
        ("Catmull–Rom = Keys a = −1/2 · Pillow BICUBIC", 0.0, 0.5, True, (10, 4), "start"),
        ("Keys a = −3/4 · OpenCV INTER_CUBIC", 0.0, 0.75, True, (10, 4), "start"),
        ("Rifman a = −1", 0.0, 1.0, False, (10, 4), "start"),
    ]
    for name, B, C, lib, (dx, dy), anc in pts:
        ov = step_overshoot(B, C)
        h25 = ft(lambda u: bc(u, B, C), 2, 0.25)
        col = ACCENT if lib else INK
        s += dot(ax.X(B), ax.Y(C), r=5.5 if lib else 4.5, fill=PAPER if not lib else ACCENT_TINT, stroke=col)
        s += txt(ax.X(B) + dx, ax.Y(C) + dy - 2, name, size=10, fill=col, anchor=anc, weight="600")
        s += mono(ax.X(B) + dx, ax.Y(C) + dy + 12,
                  f"overshoot {100 * ov:.1f}% · H(0.25) = {h25:.3f} · h(0) = {bc(0, B, C):.3g}",
                  size=8, fill=MUTED, anchor=anc)
    # right-side notes
    nx = 690
    s += eyebrow(nx, 110, "reading the plane", anchor="start")
    notes = [
        ("up the B = 0 axis", "sharper, more overshoot:", "−4a/27 of the step height"),
        ("right, off the axis", "blurrier, no overshoot,", "and h(0) < 1: samples not kept"),
        ("Keys' a is (B, C) = (0, −a)", "checked by expanding", "both formulas"),
    ]
    y = 140
    for a, b, c in notes:
        s += txt(nx, y, a, size=11, fill=INK, anchor="start", weight="600")
        s += mono(nx, y + 16, b, size=8, fill=MUTED, anchor="start")
        s += mono(nx, y + 29, c, size=8, fill=MUTED, anchor="start")
        y += 66
    s += legend(vh - 22, vw, [("named cubic", INK, "dot"), ("the two library defaults", ACCENT, "dot"),
                              ("interpolating axis, B = 0", INK, "line")])
    return emit("07", "bicubic-family", "\"Bicubic\" is a family",
                "Named cubic kernels on Mitchell and Netravali's two-parameter plane, with computed overshoot and blur.",
                "bicubic is a family", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def matrix(name):
    W = [[0.0] * N for _ in range(3)]
    for j, x in enumerate(XS_DN):
        if name == "area":
            a, b = j * 5 / 3, (j + 1) * 5 / 3
            for i in range(N):
                ov = max(0.0, min(b, i + 1) - max(a, i))
                W[j][i] += ov / (5 / 3)
        else:
            for _, c, w in taps(x, name):
                W[j][c] += w
    return W


def fig08():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "the 0.6× shrink of row r2 as four 3 × 5 matrices — rows are outputs, columns are inputs")
    cw, ch = 60, 30
    blocks = [("nearest", "nearest, pixel centres", 60, 90), ("linear", "linear", 540, 90),
              ("cubic", "Keys, a = −1/2", 60, 290), ("area", "area averaging", 540, 290)]
    for name, title, bx, by in blocks:
        W = matrix(name)
        focal = name == "area"
        col = ACCENT if focal else INK
        s += txt(bx, by - 10, title, size=12, weight="600", anchor="start", fill=col)
        for i in range(N):
            s += mono(bx + 40 + i * cw + cw / 2, by + 8, f"c{i}", size=8, fill=ACCENT if i == 1 else SOFT)
        s += mono(bx + 40 + N * cw + 30, by + 8, "row Σ", size=8, fill=SOFT)
        for j in range(3):
            y = by + 16 + j * ch
            s += mono(bx + 20, y + ch / 2 + 3, f"j{j}", size=8, fill=SOFT)
            for i in range(N):
                w = W[j][i]
                fill = ("rgba(45,49,66,%.3f)" % (0.04 + 0.22 * max(w, 0))) if abs(w) > 1e-9 else "#ffffff"
                if w < -1e-9:
                    fill = "rgba(235,108,54,0.10)"
                s += cell(bx + 40 + i * cw, y, cw, ch, wfmt(w), fill=fill,
                          stroke=ACCENT if i == 1 else "rgba(45,49,66,0.25)",
                          tcolor=SOFT if abs(w) < 1e-9 else INK, size=9)
            s += mono(bx + 40 + N * cw + 30, y + ch / 2 + 3, wfmt(sum(W[j])), size=9, fill=MUTED)
        # column sums
        y = by + 16 + 3 * ch + 6
        cs = [sum(W[j][i] for j in range(3)) for i in range(N)]
        s += mono(bx + 14, y + 16, "col Σ", size=8, fill=SOFT, anchor="start")
        for i in range(N):
            s += (f'<rect x="{bx + 40 + i * cw + 4}" y="{y}" width="{cw - 8}" height="24" rx="3" '
                  f'fill="{ACCENT_TINT if focal else PAPER}" stroke="{col if focal else "rgba(45,49,66,0.35)"}" stroke-width="1"/>')
            s += mono(bx + 40 + i * cw + cw / 2, y + 16, wfmt(cs[i]), size=10,
                      fill=ACCENT if (i == 1 or focal) else INK, weight="600")
        mean = sum(ROW[i] * cs[i] for i in range(N)) / 3
        s += mono(bx + 40 + N * cw + 30, y + 16, f"mean {mean:.1f}", size=8,
                  fill=ACCENT if focal else MUTED, weight="600" if focal else "400")
    s += legend(vh - 22, vw, [("weight of input i in output j", MUTED, "box"),
                              ("negative weight", ACCENT, "box"),
                              ("column c1: the impulse", ACCENT, "line")])
    return emit("08", "resampling-matrices", "A resize is a matrix",
                "Row sums are always 1; column sums show how much each input pixel is heard.",
                "the prefilter", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "the triangle at output j1 (x = 2), before and after stretching by 1/0.6")
    # space panel
    ax = Axes(80, 96, 400, 250, (-0.6, 4.6), (-0.05, 1.12))
    s += ax.frame([0, 1, 2, 3, 4], [0, 0.5, 1.0], xfmt=lambda v: f"c{v}", yfmt=lambda v: f"{v:g}",
                  grid=False, ylab="raw kernel height", zero=False)
    s += area_fill(ax.curve(lambda u: tri(u - 2), 1, 3, 100), ax.Y(0), SER1, 0.12)
    s += polyline(ax.curve(lambda u: tri(u - 2), 1, 3, 100), SER1, sw=1.8)
    st = lambda u: tri((u - 2) * 0.6)
    s += area_fill(ax.curve(st, 2 - 5 / 3, 2 + 5 / 3, 200), ax.Y(0), ACCENT, 0.08)
    s += polyline(ax.curve(st, 2 - 5 / 3, 2 + 5 / 3, 200), ACCENT, sw=1.8)
    for i, raw, norm in ((1, 0.4, 0.4 / 1.8), (2, 1.0, 1 / 1.8), (3, 0.4, 0.4 / 1.8)):
        s += dot(ax.X(i), ax.Y(raw), r=3.6, fill=ACCENT)
        s += mono(ax.X(i) + (0 if i == 2 else (-6 if i == 1 else 6)), ax.Y(raw) - 10,
                  f"{raw:g} → {norm:.3f}", size=8, fill=ACCENT,
                  anchor="middle" if i == 2 else ("end" if i == 1 else "start"))
    s += dot(ax.X(2), ax.Y(1.0), r=2.4, fill=SER1)
    for i, v in enumerate(ROW):
        s += mono(ax.X(i), ax.y0 + ax.h + 30, str(v), size=8, fill=ACCENT if i == 1 else MUTED)
    s += mono(ax.x0 - 8, ax.y0 + ax.h + 30, "value", size=7, fill=SOFT, anchor="end")
    s += txt(ax.x0, ax.y0 + ax.h + 58, "plain triangle: c2 only → 40", size=11, fill=SER1, anchor="start", weight="600")
    s += txt(ax.x0 + 400, ax.y0 + ax.h + 58, "stretched: c1, c2, c3 → 123.33", size=11, fill=ACCENT,
             anchor="end", weight="600")
    # frequency panel
    fx = Axes(590, 96, 360, 250, (0, 1.0), (-0.02, 1.08))
    s += fx.frame([0, 0.25, 0.5, 0.75, 1.0], [0, 0.5, 1.0], xlab="ν, cycles per input pixel",
                  ylab="gain", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", zero=False)
    s += (f'<rect x="{fx.X(0.3):.1f}" y="{fx.Y(1.08):.1f}" width="{fx.X(0.5) - fx.X(0.3):.1f}" '
          f'height="{fx.Y(-0.02) - fx.Y(1.08):.1f}" fill="{ACCENT}" fill-opacity="0.08"/>')
    for v, lab, col, dx in ((0.5, "old Nyquist", INK, 5), (0.3, "new Nyquist", ACCENT, -5)):
        s += (f'<line x1="{fx.X(v):.1f}" y1="{fx.Y(1.08):.1f}" x2="{fx.X(v):.1f}" y2="{fx.Y(-0.02):.1f}" '
              f'stroke="{col}" stroke-width="1" stroke-dasharray="4,3"/>')
        s += mono(fx.X(v) + dx, fx.Y(1.03), lab, size=8, fill=col, anchor="start" if dx > 0 else "end")
    s += polyline(fx.curve(lambda n: sinc(n) ** 2, 0, 1.0, 300), SER1, sw=1.8)
    s += polyline(fx.curve(lambda n: sinc(n / 0.6) ** 2, 0, 1.0, 300), ACCENT, sw=1.8)
    for f_, col, lab, dy in ((lambda n: sinc(n) ** 2, SER1, "0.573", -10),
                             (lambda n: sinc(n / 0.6) ** 2, ACCENT, "0.171", -10)):
        s += dot(fx.X(0.4), fx.Y(f_(0.4)), r=3.4, fill=col)
        if col == ACCENT:
            s += masked(fx.X(0.4) - 10, fx.Y(f_(0.4)) + 18, f"{lab} at ν = 0.4", size=8, fill=col,
                        anchor="end", pad=3)
        else:
            s += masked(fx.X(0.4) + 10, fx.Y(f_(0.4)) - 6, f"{lab} at ν = 0.4", size=8, fill=col,
                        anchor="start", pad=3)
    s += mono(fx.x0 + fx.w, fx.y0 + fx.h + 58, "H(ν)  →  H(ν / 0.6)", size=11, fill=INK, anchor="end", weight="600")
    s += legend(vh - 22, vw, [("triangle, unit width", SER1, "line"),
                              ("triangle stretched by 1/0.6 — the prefilter", ACCENT, "line")])
    return emit("09", "stretched-kernel", "Stretching the kernel is the prefilter",
                "The triangle at unit width and at 1/0.6 width, in space and in frequency.",
                "the prefilter", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 610
    s = eyebrow(32, 40, "resize calls, and what each one actually computes (documentation and source; nothing executed)")
    cols = [("call", 236), ("kernel · taps per axis", 214), ("cubic a", 76),
            ("prefilter when shrinking", 216), ("sample positions", 176)]
    x0, y0, rh = 40, 72, 42
    x = x0
    for name, w in cols:
        s += eyebrow(x + 10, y0 + 16, name, anchor="start", size=8)
        x += w
    s += f'<line x1="{x0}" y1="{y0 + 26}" x2="{x}" y2="{y0 + 26}" stroke="{RULE_SOLID}"/>'
    rows = [
        ("OpenCV", "INTER_NEAREST", "box · 1", "—", ("no", False), "cell left edge, ⌊j/s⌋"),
        ("OpenCV", "INTER_NEAREST_EXACT", "box · 1", "—", ("no", False), "pixel centres"),
        ("OpenCV", "INTER_LINEAR (default)", "triangle · 2", "—", ("no — area at exactly 0.5×", False), "pixel centres"),
        ("OpenCV", "INTER_CUBIC", "Keys · 4", "−0.75", ("no", False), "pixel centres"),
        ("OpenCV", "INTER_LANCZOS4", "Lanczos-4 · 8", "—", ("no", False), "pixel centres"),
        ("OpenCV", "INTER_AREA", "box, width 1/s", "—", ("yes — box", True), "cell overlap"),
        ("OpenCV", "pyrDown", "5×5 binomial, drop half", "—", ("yes — exactly 2× only", True), "every other pixel"),
        ("Pillow", "resize, BICUBIC (default)", "Keys · 4 → 4/s", "−0.5", ("yes — kernel stretched", True), "pixel centres"),
        ("Pillow", "resize, LANCZOS", "Lanczos-3 · 6 → 6/s", "—", ("yes — kernel stretched", True), "pixel centres"),
        ("scikit-image", "transform.resize", "order 1 · 2", "—", ("yes — Gaussian, σ = (d−1)/2", True), "pixel centres"),
        ("SciPy", "ndimage.zoom", "cubic B-spline · 4", "—", ("no — prefilter ≠ anti-alias", False), "corner-aligned"),
    ]
    y = y0 + 34
    for lib, call, kern, a, (pre, yes), pos in rows:
        s += (f'<rect x="{x0}" y="{y}" width="{x - x0}" height="{rh - 6}" rx="3" '
              f'fill="#ffffff" stroke="rgba(45,49,66,0.12)" stroke-width="0.8"/>')
        cx = x0
        s += mono(cx + 10, y + 14, lib, size=7, fill=SOFT, anchor="start", track="0.1em")
        s += mono(cx + 10, y + 28, call, size=9, fill=INK, anchor="start", weight="600")
        cx += cols[0][1]
        s += mono(cx + 10, y + 22, kern, size=9, fill=INK, anchor="start")
        cx += cols[1][1]
        s += mono(cx + 10, y + 22, a, size=9, fill=INK if a != "—" else SOFT, anchor="start",
                  weight="600" if a != "—" else "400")
        cx += cols[2][1]
        s += (f'<rect x="{cx + 6}" y="{y + 6}" width="{cols[3][1] - 12}" height="{rh - 18}" rx="3" '
              f'fill="{ACCENT_TINT if yes else PAPER}" stroke="{ACCENT if yes else "rgba(45,49,66,0.18)"}" '
              f'stroke-width="0.8"/>')
        s += mono(cx + 14, y + 22, pre, size=8.5 if len(pre) > 30 else 9, fill=ACCENT if yes else MUTED,
                  anchor="start", weight="600" if yes else "400")
        cx += cols[3][1]
        s += mono(cx + 10, y + 22, pos, size=9, fill=MUTED, anchor="start")
        y += rh
    s += legend(vh - 22, vw, [("stretches or prefilters on a shrink", ACCENT, "box"),
                              ("fixed width: aliases when shrinking", MUTED, "box")])
    return emit("10", "tooling-map", "The tooling map",
                "What each resize call computes, from its documentation and source.",
                "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05,
        "06": fig06, "07": fig07, "08": fig08, "09": fig09, "10": fig10}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
