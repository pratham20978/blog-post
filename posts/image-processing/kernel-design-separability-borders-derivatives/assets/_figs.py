#!/usr/bin/env python3
"""Figures 01-11 for kernel-design-separability-borders-derivatives.

Every value drawn here is computed in this file: the 3x3 derivative family
[p, 1-2p, p] x 1/2[-1 0 1] on the shared patch, closed-form transfer functions and
plane-wave angular errors, Farid & Simoncelli's published taps (Table I), the sampled,
integrated and discrete Gaussians, OpenCV's sigma <= 0 tables (smooth.dispatch.cpp at
bed6800), and the five border extensions of row r2. Nothing is measured.
Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, box, cell, emit, eyebrow,
                    legend, masked, mono, txt)

PI = math.pi
SER1, SER2, SER3, SER4 = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50"
CDC = "#8e7aa6"   # central difference
PATCH = [[40, 40, 40, 200, 200] for _ in range(5)]
PATCH[2][1] = 255
ROW = PATCH[2]

# the family: name, p, colour
FAM = [
    ("central difference", 0.0, CDC),
    ("[1 4 1]/6", 1 / 6, SER1),
    ("Scharr", 3 / 16, ACCENT),
    ("Farid–Simoncelli 3", 0.229879, SER3),
    ("Gaussian σ = 0.8", math.exp(-1 / 1.28) / (1 + 2 * math.exp(-1 / 1.28)), LINK),
    ("Sobel", 0.25, SER2),
    ("Prewitt", 1 / 3, SER4),
]
FS3 = ([0.229879, 0.540242, 0.229879], [0.425287, 0.0, -0.425287])
FS5 = ([0.037659, 0.249153, 0.426375, 0.249153, 0.037659],
       [0.109604, 0.276691, 0.0, -0.276691, -0.109604])


# ------------------------------------------------------------------ maths
def S(w):
    return 1.0 if abs(w) < 1e-12 else math.sin(w) / w


def B(w, p):
    return 1 - 2 * p + 2 * p * math.cos(w)


def P_of(p, w):
    r = len(p) // 2
    return sum(p[i] * math.cos((i - r) * w) for i in range(len(p)))


def D_of(d, w):
    """Derivative filter response, signed so a positive slope reads positive."""
    r = len(d) // 2
    return sum(-d[i] * math.sin((i - r) * w) for i in range(len(d)))


def pair_of_family(p):
    return [p, 1 - 2 * p, p], [0.5, 0.0, -0.5]


def ang_err_pair(pair, w, th):
    pf, df = pair
    u, v = w * math.cos(th), w * math.sin(th)
    gx = D_of(df, u) * P_of(pf, v)
    gy = D_of(df, v) * P_of(pf, u)
    return math.degrees(math.atan2(gy, gx) - th)


def worst(pair, w):
    return max((ang_err_pair(pair, w, math.radians(t / 10)) for t in range(0, 451)), key=abs)


def gx_family(img, r, c, p, get=None):
    get = get or (lambda im, rr, cc: im[rr][cc])
    rows = [(get(img, r + dr, c + 1) - get(img, r + dr, c - 1)) / 2 for dr in (-1, 0, 1)]
    return p * rows[0] + (1 - 2 * p) * rows[1] + p * rows[2], rows


def g2(n, sig=2.0):
    return math.exp(-n * n / (2 * sig * sig))


def trunc_stats(taps, sig=2.0):
    r = taps // 2
    tot = sum(g2(n, sig) for n in range(-60, 61))
    kept = sum(g2(n, sig) for n in range(-r, r + 1))
    var = sum(n * n * g2(n, sig) for n in range(-r, r + 1)) / kept
    return kept / tot, var


def besseli(n, x, terms=60):
    return sum((x / 2) ** (2 * k + n) / (math.factorial(k) * math.factorial(k + n))
               for k in range(terms))


def var_sampled(sig, r=None):
    rr = r if r is not None else 30
    w = [math.exp(-n * n / (2 * sig * sig)) for n in range(-rr, rr + 1)]
    return sum(n * n * x for n, x in zip(range(-rr, rr + 1), w)) / sum(w)


def var_integrated(sig):
    w = [0.5 * (math.erf((n + 0.5) / (sig * math.sqrt(2))) - math.erf((n - 0.5) / (sig * math.sqrt(2))))
         for n in range(-30, 31)]
    return sum(n * n * x for n, x in zip(range(-30, 31), w)) / sum(w)


def ext(row, i, mode):
    n = len(row)
    if 0 <= i < n:
        return row[i]
    if mode == "constant":
        return 0
    if mode == "replicate":
        return row[0] if i < 0 else row[-1]
    if mode == "reflect":
        return row[-i - 1] if i < 0 else row[2 * n - i - 1]
    if mode == "reflect-101":
        return row[-i] if i < 0 else row[2 * n - i - 2]
    if mode == "wrap":
        return row[i % n]
    raise ValueError(mode)


# ------------------------------------------------------------------ plotting helpers
def polyline(pts, stroke, sw=1.4, dash=None, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity else ""
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}{o}/>')


def area_between(top, bot, fill, opacity=0.14):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in top)
    d += " L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in reversed(bot)) + " Z"
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
    return f"{v:.{nd}f}".replace("-", "−")


def pix(x, y, w, h, v, size=11, invented=False):
    """A pixel cell drawn high value = bright (series rule)."""
    shade = 0.88 * (1 - v / 255) + 0.02
    fill = f"rgba(45,49,66,{shade:.3f})"
    dash = ' stroke-dasharray="3,2"' if invented else ""
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
         f'stroke="{"rgba(45,49,66,0.55)" if invented else "rgba(45,49,66,0.30)"}" stroke-width="0.8"{dash}/>')
    s += txt(x + w / 2, y + h / 2 + 4, str(v), size=size, fill="#ffffff" if v < 130 else INK,
             family=MONO, weight="500")
    return s


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "every 3×3 x-derivative, scaled to slope 1: the column p, 1 − 2p, p times ½ [−1 0 1]")
    ax0, ax1, ay = 70, 946, 372
    X = lambda p: ax0 + p / 0.35 * (ax1 - ax0)
    pitch, cw = 136, 122
    w4 = 2 * PI / 4
    for i, (name, p, col) in enumerate(FAM):
        cx = 32 + i * pitch
        focal = name == "Scharr"
        s += box(cx, 62, cw, 206, fill=ACCENT_TINT if focal else "#ffffff",
                 stroke=ACCENT if focal else "rgba(45,49,66,0.35)")
        s += txt(cx + cw / 2, 82, name.replace("Farid–Simoncelli 3", "Farid–Simoncelli"),
                 size=11, weight="600", fill=ACCENT if focal else INK)
        s += mono(cx + cw / 2, 96, "3-tap pair" if "Farid" in name else
                  ("sampled, 3 taps" if "Gaussian" in name else " "), size=8, fill=SOFT)
        # the column p, 1-2p, p
        for j, v in enumerate((p, 1 - 2 * p, p)):
            s += cell(cx + 31, 104 + j * 24, 60, 24, f"{v:.3f}".rstrip("0").rstrip(".") if v else "0",
                      fill="#ffffff", size=10)
        s += mono(cx + cw / 2, 192, f"p = {p:.4f}".rstrip("0").rstrip("."), size=9,
                  fill=ACCENT if focal else MUTED, weight="600")
        a = worst(pair_of_family(p), w4)
        g, _ = gx_family(PATCH, 2, 2, p)
        s += mono(cx + 10, 222, "4-px dir.", size=8, fill=SOFT, anchor="start")
        s += mono(cx + cw - 10, 222, f"{abs(a):.2f}°", size=9, fill=INK, anchor="end", weight="500")
        s += mono(cx + 10, 244, "impulse err", size=8, fill=SOFT, anchor="start")
        s += mono(cx + cw - 10, 244, f"{(80 - g) / 80 * 100:.0f}%", size=9, fill=INK, anchor="end",
                  weight="500")
        # leader to the axis
        s += (f'<line x1="{cx + cw / 2:.1f}" y1="268" x2="{X(p):.1f}" y2="{ay - 8}" '
              f'stroke="{col}" stroke-width="1" stroke-opacity="0.8"/>')
        s += dot(X(p), ay, r=4, fill=col)
    s += f'<line x1="{ax0}" y1="{ay}" x2="{ax1}" y2="{ay}" stroke="{RULE_SOLID}" stroke-width="1.2"/>'
    for v, lab in ((0, "0"), (1 / 6, "1/6"), (3 / 16, "3/16"), (0.25, "1/4"), (1 / 3, "1/3")):
        s += (f'<line x1="{X(v):.1f}" y1="{ay}" x2="{X(v):.1f}" y2="{ay + 6}" stroke="{RULE_SOLID}"/>')
        s += mono(X(v), ay + 20, lab, size=9, fill=MUTED)
    s += eyebrow(ax1, ay + 40, "cross-weight p on each neighbouring row", anchor="end")
    s += mono(32, 436, "4-px dir.: worst gradient-direction error for a plane wave with a 4-pixel wavelength (closed form)",
              size=8, fill=SOFT, anchor="start")
    s += mono(32, 452, "impulse err: error at (r2, c2) of the shared patch against the clean 80 — output = 80 − 107.5 (1 − 2p)",
              size=8, fill=SOFT, anchor="start")
    return emit("01", "derivative-family", "One stencil, one free number",
                "Every 3×3 x-derivative that treats up and down alike is a cross-smoothing column times a central difference.",
                "the family", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 420
    s = eyebrow(32, 40, "the family on the shared patch: at (r2, c3) every p gives 80; at (r2, c2) the impulse pulls it down")
    # left: the patch with the window at (r2, c2)
    gx0, gy0, cs = 48, 96, 44
    for r in range(5):
        s += mono(gx0 - 12, gy0 + r * cs + cs / 2 + 3, f"r{r}", size=8, fill=SOFT, anchor="end")
        for c in range(5):
            s += pix(gx0 + c * cs, gy0 + r * cs, cs, cs, PATCH[r][c], size=10)
    for c in range(5):
        s += mono(gx0 + c * cs + cs / 2, gy0 - 8, f"c{c}", size=8, fill=SOFT)
    s += (f'<rect x="{gx0 + 1 * cs}" y="{gy0 + 1 * cs}" width="{3 * cs}" height="{3 * cs}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="2"/>')
    s += mono(gx0 + 2.5 * cs, gy0 + 5 * cs + 20, "window at (r2, c2)", size=9, fill=ACCENT)
    # row differences
    _, rows = gx_family(PATCH, 2, 2, 0.25)
    rx = gx0 + 5 * cs + 26
    s += eyebrow(rx, gy0 + 20, "row differences", fill=SOFT)
    labels = ["(200 − 40)/2", "(200 − 255)/2", "(200 − 40)/2"]
    for k, (v, lab) in enumerate(zip(rows, labels)):
        yy = gy0 + (k + 1) * cs + cs / 2 + 4
        s += mono(rx, yy - 8, lab, size=8, fill=SOFT, anchor="start")
        s += mono(rx, yy + 6, f"= {fmt(v, 1)}", size=10, fill=ACCENT if v < 0 else INK, anchor="start",
                  weight="600")
    s += mono(rx, gy0 + 4 * cs + 44, "weights p, 1 − 2p, p", size=9, fill=MUTED, anchor="start")
    # right: output vs p
    ax = Axes(560, 90, 400, 280, (0, 0.35), (-40, 95))
    s += ax.frame([0, 1 / 6, 0.25, 1 / 3], [-25, 0, 25, 50, 80], xlab="cross-weight p",
                  ylab="Gx at (r2, c2), normalised",
                  xfmt=lambda v: {0: "0", 1 / 6: "1/6", 0.25: "1/4", 1 / 3: "1/3"}[v],
                  yfmt=lambda v: fmt(v, 0))
    s += (f'<line x1="{ax.X(0)}" y1="{ax.Y(80):.1f}" x2="{ax.X(0.35)}" y2="{ax.Y(80):.1f}" '
          f'stroke="{INK}" stroke-width="1.2" stroke-dasharray="5,4"/>')
    s += masked(ax.X(0.175), ax.Y(80) - 8, "clean edge (r2, c3): 80 for every p", size=8, fill=INK)
    s += polyline(ax.curve(lambda p: 80 - 107.5 * (1 - 2 * p), 0, 0.35, 10), MUTED, sw=1.6)
    offs = {"central difference": (8, 14, "start"), "[1 4 1]/6": (-8, -10, "end"),
            "Scharr": (10, 18, "start"), "Farid–Simoncelli 3": (-8, -36, "end"),
            "Gaussian σ = 0.8": (-8, -12, "end"), "Sobel": (10, 14, "start"),
            "Prewitt": (-8, -10, "end")}
    for name, p, col in FAM:
        g = 80 - 107.5 * (1 - 2 * p)
        s += dot(ax.X(p), ax.Y(g), r=4, fill=col)
        dx, dy, anc = offs[name]
        s += masked(ax.X(p) + dx, ax.Y(g) + dy, f"{name} {fmt(g, 2)}", size=8, fill=col, anchor=anc, pad=4)
    s += mono(ax.X(0.26), ax.Y(-18), "80 − 107.5 (1 − 2p)", size=9, fill=MUTED, anchor="start")
    return emit("02", "family-on-the-patch", "The family on the patch",
                "Beside the impulse the output is a straight line in p; the clean edge cannot tell the members apart.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "σ = 2 sampled at the integers, and what 3, 5, 7 and 13 taps keep of it")
    ax = Axes(70, 90, 560, 220, (-8.7, 8.7), (0, 0.22))
    s += ax.frame([-8, -6, -4, -2, 0, 2, 4, 6, 8], [0, 0.05, 0.1, 0.15, 0.2], xlab="tap n",
                  ylab="weight, sampled and divided by the full sum 5.0133",
                  xfmt=lambda v: str(v).replace("-", "−"), yfmt=lambda v: fmt(v, 2))
    tot = sum(g2(n) for n in range(-60, 61))
    for n in range(-8, 9):
        w = g2(n) / tot
        x = ax.X(n)
        s += (f'<rect x="{x - 11:.1f}" y="{ax.Y(w):.1f}" width="22" height="{ax.Y(0) - ax.Y(w):.1f}" '
              f'fill="{SER2}" fill-opacity="{0.85 if abs(n) <= 1 else 0.45}" stroke="none"/>')
    # windows
    ys = {3: 336, 5: 352, 7: 368, 13: 384}
    cols = {3: ACCENT, 5: SER3, 7: SER1, 13: MUTED}
    for taps, yy in ys.items():
        r = taps // 2
        x1, x2 = ax.X(-r) - 12, ax.X(r) + 12
        s += (f'<path d="M {x1:.1f} {yy - 6} V {yy} H {x2:.1f} V {yy - 6}" fill="none" '
              f'stroke="{cols[taps]}" stroke-width="1.4"/>')
        s += mono(x2 + 8, yy + 3, f"{taps} taps", size=8, fill=cols[taps], anchor="start")
    # table
    tx = 700
    s += eyebrow(tx, 100, "after renormalising", fill=SOFT)
    hdr = ["taps", "mass kept", "variance", "of target", "σ eff."]
    xs = [tx, tx + 50, tx + 128, tx + 196, tx + 262]
    for x, h in zip(xs, hdr):
        s += mono(x, 124, h, size=8, fill=SOFT, anchor="start")
    for k, taps in enumerate((3, 5, 7, 9, 13, 17)):
        kept, var = trunc_stats(taps)
        yy = 148 + k * 24
        col = cols.get(taps, INK)
        vals = [str(taps), f"{kept * 100:.2f}%", f"{var:.3f}", f"{var / 4 * 100:.0f}%", f"{math.sqrt(var):.2f}"]
        for x, v in zip(xs, vals):
            s += mono(x, yy, v, size=10, fill=col, anchor="start", weight="600" if taps == 3 else "400")
    s += mono(tx, 312, "13 = OpenCV's choice for 8-bit at σ = 2", size=8, fill=MUTED, anchor="start")
    s += mono(tx, 326, "17 = OpenCV float, and SciPy's truncate = 4", size=8, fill=MUTED, anchor="start")
    s += mono(tx, 356, "variance counts each tap by n²,", size=9, fill=INK, anchor="start")
    s += mono(tx, 372, "so the far taps carry it:", size=9, fill=INK, anchor="start")
    k7, v7 = trunc_stats(7)
    s += mono(tx, 388, f"7 taps keep {k7 * 100:.0f}% of the mass, {v7 / 4 * 100:.0f}% of the variance",
              size=9, fill=ACCENT, anchor="start")
    y = 436
    s += (f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>')
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    s += f'<rect x="108" y="{y}" width="12" height="10" fill="{SER2}" fill-opacity="0.85"/>'
    s += mono(126, y + 9, "the 3 taps GaussianBlur(img, (3, 3), 2) keeps", size=8, fill=MUTED, anchor="start")
    s += f'<rect x="470" y="{y}" width="12" height="10" fill="{SER2}" fill-opacity="0.45"/>'
    s += mono(488, y + 9, "the tail it discards: 44.85% of the weight", size=8, fill=MUTED, anchor="start")
    return emit("03", "truncating-sigma-2", "Truncating σ = 2",
                "Renormalising keeps the mass; the variance is what truncation takes.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "a plane wave at 4-pixel wavelength, gradient at 22.5°: how each filter shrinks the two components")
    w = 2 * PI / 4
    th = math.radians(22.5)
    u, v = w * math.cos(th), w * math.sin(th)
    ax = Axes(90, 80, 520, 300, (0, 1.6), (0, 0.9))
    s += ax.frame([0, 0.5, 1.0, 1.5], [0, 0.3, 0.6, 0.9], xlab="x component", ylab="y component",
                  xfmt=lambda t: fmt(t, 1), yfmt=lambda t: fmt(t, 1))
    vecs = [("true gradient", u, v, INK, None),
            ("central difference", math.sin(u), math.sin(v), CDC, None),
            ("Sobel", math.sin(u) * B(v, 0.25), math.sin(v) * B(u, 0.25), SER2, None),
            ("Scharr", math.sin(u) * B(v, 3 / 16), math.sin(v) * B(u, 3 / 16), ACCENT, None)]
    for name, gx, gy, col, _ in vecs:
        marker = "arrow-accent" if col == ACCENT else "arrow"
        dash = ' stroke-dasharray="5,4"' if name == "true gradient" else ""
        s += (f'<line x1="{ax.X(0):.1f}" y1="{ax.Y(0):.1f}" x2="{ax.X(gx):.1f}" y2="{ax.Y(gy):.1f}" '
              f'stroke="{col}" stroke-width="{2 if col == ACCENT else 1.5}"{dash} marker-end="url(#{marker})"/>')
    lab = {"true gradient": (-10, -14), "central difference": (6, -8), "Sobel": (8, 12), "Scharr": (8, 4)}
    for name, gx, gy, col, _ in vecs:
        ang = math.degrees(math.atan2(gy, gx))
        dx, dy = lab[name]
        txtl = f"{name}  {ang:.2f}°" if name == "true gradient" else f"{name}  {ang:.2f}° ({ang - 22.5:+.2f}°)".replace("-", "−")
        s += masked(ax.X(gx) + dx, ax.Y(gy) + dy, txtl, size=8, fill=col,
                    anchor="end" if name == "true gradient" else "start", pad=4)
    # table of factors
    tx = 660
    s += eyebrow(tx, 96, "shrink factor on each component", fill=SOFT)
    s += mono(tx, 118, "x: S(ωx) × B(ωy)", size=9, fill=MUTED, anchor="start")
    s += mono(tx, 134, "y: S(ωy) × B(ωx)", size=9, fill=MUTED, anchor="start")
    s += mono(tx, 150, f"ωx = {u:.3f}, ωy = {v:.3f} rad/px", size=8, fill=SOFT, anchor="start")
    xs = [tx, tx + 140, tx + 210, tx + 280]
    for x, h in zip(xs, ["filter", "on x", "on y", "turn"]):
        s += mono(x, 180, h, size=8, fill=SOFT, anchor="start")
    for k, (name, p, col) in enumerate([("central difference", 0.0, CDC), ("Sobel", 0.25, SER2),
                                        ("[1 4 1]/6", 1 / 6, SER1), ("Scharr", 3 / 16, ACCENT)]):
        fx, fy = S(u) * B(v, p), S(v) * B(u, p)
        ang = math.degrees(math.atan2(math.sin(v) * B(u, p), math.sin(u) * B(v, p))) - 22.5
        yy = 204 + k * 24
        s += mono(xs[0], yy, name, size=9, fill=col, anchor="start", weight="600")
        s += mono(xs[1], yy, f"{fx:.3f}", size=10, fill=INK, anchor="start")
        s += mono(xs[2], yy, f"{fy:.3f}", size=10, fill=INK, anchor="start")
        s += mono(xs[3], yy, f"{ang:+.2f}°".replace("-", "−"), size=10, fill=col, anchor="start")
    s += mono(tx, 318, "equal factors keep the direction:", size=9, fill=INK, anchor="start")
    fx, fy = S(u) * B(v, 3 / 16), S(v) * B(u, 3 / 16)
    s += mono(tx, 334, f"Scharr's {fx:.3f} and {fy:.3f} differ by {abs(fx - fy) / fx * 100:.1f}%", size=9,
              fill=ACCENT, anchor="start")
    s += mono(tx, 358, "S(ω) = sin ω / ω, the difference's own blur", size=8, fill=SOFT, anchor="start")
    s += mono(tx, 372, "B(ω) = 1 − 2p + 2p cos ω, the cross-smoothing", size=8, fill=SOFT, anchor="start")
    s += legend(430, vw, [("true direction", INK, "line"), ("central difference", CDC, "line"),
                          ("Sobel", SER2, "line"), ("Scharr", ACCENT, "line")])
    return emit("04", "gradient-turns", "Why the gradient turns",
                "Each component is shrunk at its own frequency; unequal shrinking rotates the vector. A model plane wave, evaluated from closed forms.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "the central difference's own smoothing S(ω), against the cross-smoothing B(ω) for three values of p")
    ax = Axes(80, 80, 560, 290, (0, PI), (0, 1.12))
    xt = [2 * PI / L for L in (8, 4, 3, 2)] + [0]
    s += ax.frame(xt, [0, 0.25, 0.5, 0.75, 1.0], xlab="frequency ω, rad/px (wavelength in px)",
                  ylab="gain", xfmt=lambda t: "0 (∞)" if t == 0 else f"{t:.2f} ({2 * PI / t:.0f})",
                  yfmt=lambda t: fmt(t, 2))
    s += polyline(ax.curve(S, 0, PI), INK, sw=2.2)
    curves = [(1 / 6, SER1, "p = 1/6"), (3 / 16, ACCENT, "p = 3/16 (Scharr)"), (0.25, SER2, "p = 1/4 (Sobel)")]
    for p, col, _ in curves:
        s += polyline(ax.curve(lambda w, p=p: B(w, p), 0, PI), col, sw=1.6)

    def leader(x1, y1, x2, y2, col):
        return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" '
                f'stroke-width="0.8" stroke-dasharray="2,2"/>')
    w316 = 2 * PI / 3.453
    s += dot(ax.X(w316), ax.Y(S(w316)), r=4.5, fill=ACCENT)
    s += leader(ax.X(w316) + 4, ax.Y(S(w316)) - 4, ax.X(2.25), ax.Y(0.70) + 4, ACCENT)
    s += mono(ax.X(2.25) + 4, ax.Y(0.70), "3/16: B = S at 3.45 px", size=8, fill=ACCENT, anchor="start")
    s += dot(ax.X(PI), ax.Y(0), r=4.5, fill=SER2)
    s += leader(ax.X(PI) - 5, ax.Y(0) - 2, ax.X(2.3), ax.Y(0.06) + 2, SER2)
    s += mono(ax.X(2.28), ax.Y(0.06), "1/4: B = S = 0 at 2 px", size=8, fill=SER2, anchor="end")
    s += dot(ax.X(0), ax.Y(1), r=4.5, fill=SER1)
    s += mono(ax.X(0) + 10, ax.Y(1.075), "1/6: B = S to second order as ω → 0", size=8, fill=SER1, anchor="start")
    s += leader(ax.X(1.62), ax.Y(S(1.62)) - 3, ax.X(1.95), ax.Y(0.84) + 3, INK)
    s += mono(ax.X(1.97), ax.Y(0.84), "S(ω) = sin ω / ω", size=9, fill=INK, anchor="start", weight="600")
    # table
    tx = 690
    s += eyebrow(tx, 96, "p that makes B = S", fill=SOFT)
    for x, h in ((tx, "wavelength"), (tx + 110, "S"), (tx + 180, "matching p")):
        s += mono(x, 120, h, size=8, fill=SOFT, anchor="start")
    for k, L in enumerate((None, 8, 6, 4, 3.453, 3, 2.5, 2)):
        w = 1e-4 if L is None else 2 * PI / L
        pm = (1 - S(w)) / (2 * (1 - math.cos(w)))
        yy = 144 + k * 22
        col = ACCENT if L == 3.453 else (SER2 if L == 2 else (SER1 if L is None else INK))
        s += mono(tx, yy, "∞ (smooth)" if L is None else f"{L:g} px", size=10, fill=col, anchor="start")
        s += mono(tx + 110, yy, f"{S(w):.3f}", size=10, fill=col, anchor="start")
        s += mono(tx + 180, yy, f"{pm:.4f}", size=10, fill=col, anchor="start", weight="600")
    s += mono(tx, 334, "(1 − S) / (2 (1 − cos ω))", size=9, fill=MUTED, anchor="start")
    s += legend(430, vw, [("S(ω)", INK, "line"), ("B, p = 1/6", SER1, "line"),
                          ("B, p = 3/16 (Scharr)", ACCENT, "line"), ("B, p = 1/4 (Sobel)", SER2, "line")])
    return emit("05", "matching-the-difference", "Matching the difference's own smoothing",
                "Each p matches the central difference's implicit smoothing at exactly one wavelength. Evaluated from closed forms.",
                "where scharr comes from", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "gradient-direction error against orientation, plane wave with a 4-pixel wavelength (closed form)")
    ax = Axes(80, 80, 560, 320, (0, 90), (-8.5, 8.5))
    s += ax.frame([0, 22.5, 45, 67.5, 90], [-8, -4, 0, 4, 8], xlab="gradient orientation θ, degrees",
                  ylab="error, degrees", xfmt=lambda t: f"{t:g}", yfmt=lambda t: f"{t:+g}".replace("-", "−").replace("+0", "0"))
    w = 2 * PI / 4
    series = [("central difference", pair_of_family(0.0), CDC, None),
              ("Prewitt", pair_of_family(1 / 3), SER4, None),
              ("Sobel", pair_of_family(0.25), SER2, None),
              ("Farid–Simoncelli 3", FS3, SER3, None),
              ("[1 4 1]/6", pair_of_family(1 / 6), SER1, None),
              ("Scharr", pair_of_family(3 / 16), ACCENT, None),
              ("Farid–Simoncelli 5", FS5, LINK, "5,3")]
    for name, pair, col, dash in series:
        pts = ax.curve(lambda t, pair=pair: ang_err_pair(pair, w, math.radians(t)), 0, 90, 180)
        s += polyline(pts, col, sw=2.2 if col == ACCENT else 1.5, dash=dash)
    labs = {"central difference": (22.5, 7.75, "middle"), "Prewitt": (60, 8.05, "end"),
            "Sobel": (70, 3.75, "start"),
            "[1 4 1]/6": (22.5, 1.2, "middle"), "Scharr": (24, -1.0, "start")}
    for name, pair, col, dash in series:
        if name not in labs:
            continue
        th, yv, anc = labs[name]
        lab = name
        s += mono(ax.X(th), ax.Y(yv), lab, size=8, fill=col, anchor=anc, weight="600")
    # table of worst errors
    tx = 690
    s += eyebrow(tx, 96, "worst error over orientation", fill=SOFT)
    for x, h in ((tx, "filter"), (tx + 150, "8 px"), (tx + 205, "4 px"), (tx + 260, "3 px")):
        s += mono(x, 120, h, size=8, fill=SOFT, anchor="start")
    for k, (name, pair, col, dash) in enumerate(series):
        yy = 144 + k * 24
        s += mono(tx, yy, name, size=9, fill=col, anchor="start", weight="600")
        for j, L in enumerate((8, 4, 3)):
            e = abs(worst(pair, 2 * PI / L))
            s += mono(tx + 150 + 55 * j, yy, f"{e:.2f}°", size=10, fill=INK, anchor="start")
    s += mono(tx, 330, "Sobel ksize = 5: identical to ksize = 3", size=8, fill=MUTED, anchor="start")
    s += mono(tx, 346, "5-tap Gaussian, σ = 0.96:", size=8, fill=MUTED, anchor="start")
    g96 = gauss_pair(0.96, 2)
    s += mono(tx, 360, "  " + ", ".join(f"{abs(worst(g96, 2 * PI / L)):.2f}°" for L in (8, 4, 3)),
              size=8, fill=MUTED, anchor="start")
    s += f'<line x1="32" y1="438" x2="{vw - 32}" y2="438" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, 454, "legend", fill=SOFT)
    items = [(name, col, dash) for name, pair, col, dash in series]
    for k, (name, col, dash) in enumerate(items):
        x = 108 + (k % 4) * 215
        y = 446 + (k // 4) * 20
        d = f' stroke-dasharray="{dash}"' if dash else ""
        s += f'<line x1="{x}" y1="{y + 5}" x2="{x + 14}" y2="{y + 5}" stroke="{col}" stroke-width="1.8"{d}/>'
        s += mono(x + 20, y + 9, name + (" (dashed)" if dash else ""), size=8, fill=MUTED, anchor="start")
    return emit("06", "angular-error", "Direction error by orientation",
                "The error in every member of the family is zero on the axes and the diagonal and peaks near 22.5° and 67.5°. A model, not a measurement.",
                "where scharr comes from", vw, vh, s)


def gauss_pair(sig, r):
    w = [math.exp(-n * n / (2 * sig * sig)) for n in range(-r, r + 1)]
    sw = sum(w)
    p = [x / sw for x in w]
    d = [-n / (sig * sig) * p[i] for i, n in enumerate(range(-r, r + 1))]
    return p, d


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "Farid & Simoncelli's criterion: the derivative filter D(ω) must equal ω times its prefilter P(ω)")
    panels = [("Sobel, normalised", ([0.25, 0.5, 0.25], [0.5, 0, -0.5]), SER2),
              ("Scharr, normalised", ([3 / 16, 10 / 16, 3 / 16], [0.5, 0, -0.5]), ACCENT),
              ("Farid–Simoncelli, 3 taps", FS3, SER3),
              ("Farid–Simoncelli, 5 taps", FS5, LINK)]
    pw, ph = 206, 250
    for k, (name, (pf, df), col) in enumerate(panels):
        x0 = 70 + k * 236
        ax = Axes(x0, 96, pw, ph, (0, PI), (0, 1.25))
        s += ax.frame([0, PI / 2, PI], [0, 0.5, 1.0], xfmt=lambda t: {0: "0", PI / 2: "π/2", PI: "π"}[t],
                      yfmt=lambda t: fmt(t, 1))
        s += txt(x0, 84, name, size=11, weight="600", fill=col, anchor="start")
        top = ax.curve(lambda w: w * P_of(pf, w), 0, PI, 200)
        bot = ax.curve(lambda w: D_of(df, w), 0, PI, 200)
        s += area_between(top, bot, col, 0.12)
        s += polyline(top, INK, sw=1.4, dash="5,3")
        s += polyline(bot, col, sw=1.8)
        num = simpson(lambda w: (w * P_of(pf, w) - D_of(df, w)) ** 2, 0, PI)
        den = simpson(lambda w: P_of(pf, w) ** 2, 0, PI)
        gain = sum(-df[i] * (i - len(df) // 2) for i in range(len(df)))
        e = num / den
        sup = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
        m, ex = f"{e:.1e}".split("e")
        es = f"{e:.4f}" if e >= 1e-3 else f"{m} × 10" + str(int(ex)).translate(sup)
        s += mono(x0, 96 + ph + 34, f"error ratio E = {es}", size=9, fill=INK, anchor="start")
        s += mono(x0, 96 + ph + 50, f"gain on a unit ramp = {gain:.3f}", size=9, fill=MUTED, anchor="start")
    s += eyebrow(1016 - 32, 96 + ph + 72, "ω in rad/px, 0 to Nyquist", anchor="end")
    s += legend(432, vw, [("ω · P(ω), what the derivative should be", INK, "line"),
                          ("D(ω), what the filter gives", MUTED, "line"), ("the mismatch", MUTED, "box")])
    return emit("07", "matched-pairs", "Matched derivative and prefilter pairs",
                "The shaded gap is what Farid and Simoncelli's Rayleigh quotient minimises. Evaluated from the published taps.",
                "what optimal means", vw, vh, s)


def simpson(f, a, b, n=800):
    h = (b - a) / n
    t = f(a) + f(b)
    for i in range(1, n):
        t += (4 if i % 2 else 2) * f(a + i * h)
    return t * h / 3


# ------------------------------------------------------------------ FIG 08
def mat(x, y, m, cs=34, hl=None, size=10):
    s = ""
    for r, rowv in enumerate(m):
        for c, v in enumerate(rowv):
            fill = "#ffffff"
            if hl == "neg" and v < 0:
                fill = "rgba(45,49,66,0.08)"
            s += cell(x + c * cs, y + r * cs, cs, cs, str(v).replace("-", "−"), fill=fill, size=size)
    return s


def fig08():
    vw, vh = 1016, 540
    s = eyebrow(32, 40, "a kernel splits into 1-D passes exactly when every row is a multiple of one row")
    cs = 30
    # row 1: Sobel
    blocks = [
        ("Sobel", [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], [1, 2, 1], [-1, 0, 1], SER2, 92),
        ("Scharr", [[-3, 0, 3], [-10, 0, 10], [-3, 0, 3]], [3, 10, 3], [-1, 0, 1], ACCENT, 232),
    ]
    for name, m, col, row, colr, y in blocks:
        s += txt(40, y - 10, name, size=12, weight="600", fill=colr, anchor="start")
        s += mat(40, y, m, cs)
        s += txt(40 + 3 * cs + 22, y + 1.5 * cs + 6, "=", size=18, fill=MUTED)
        cx = 40 + 3 * cs + 44
        s += mat(cx, y, [[v] for v in col], cs)
        s += txt(cx + cs + 16, y + 1.5 * cs + 5, "×", size=14, fill=MUTED)
        s += mat(cx + cs + 32, y + cs, [row], cs)
        mults = " , ".join(str(v) for v in col)
        s += mono(cx + cs + 32 + 3 * cs + 20, y + 22, f"rows are {col[0]}×, {col[1]}×, {col[2]}× the same row",
                  size=9, fill=MUTED, anchor="start")
        s += mono(cx + cs + 32 + 3 * cs + 20, y + 40, "rank 1 · one pair of 1-D passes", size=9, fill=colr,
                  anchor="start", weight="600")
        s += mono(cx + cs + 32 + 3 * cs + 20, y + 58, "3 + 3 = 6 multiplications, not 9", size=9, fill=MUTED,
                  anchor="start")
    # Laplacian
    y = 372
    s += txt(40, y - 10, "4-neighbour Laplacian", size=12, weight="600", fill=SER4, anchor="start")
    s += mat(40, y, [[0, 1, 0], [1, -4, 1], [0, 1, 0]], cs)
    s += txt(40 + 3 * cs + 22, y + 1.5 * cs + 6, "=", size=18, fill=MUTED)
    cx = 40 + 3 * cs + 44
    s += mat(cx, y, [[0], [1], [0]], cs)
    s += txt(cx + cs + 16, y + 1.5 * cs + 5, "×", size=14, fill=MUTED)
    s += mat(cx + cs + 32, y + cs, [[1, -2, 1]], cs)
    x2 = cx + cs + 32 + 3 * cs + 22
    s += txt(x2, y + 1.5 * cs + 6, "+", size=18, fill=MUTED)
    s += mat(x2 + 22, y, [[1], [-2], [1]], cs)
    s += txt(x2 + 22 + cs + 16, y + 1.5 * cs + 5, "×", size=14, fill=MUTED)
    s += mat(x2 + 22 + cs + 32, y + cs, [[0, 1, 0]], cs)
    tx = x2 + 22 + cs + 32 + 3 * cs + 24
    s += mono(tx, y + 22, "row 1, −4, 1 is no multiple of 0, 1, 0", size=9, fill=MUTED, anchor="start")
    s += mono(tx, y + 40, "rank 2 · two pairs of 1-D passes", size=9, fill=SER4, anchor="start", weight="600")
    s += mono(tx, y + 58, "4k = 12 > 9 at 3 taps; 36 < 81 at 9", size=9, fill=MUTED, anchor="start")
    # right column: the rank test and the Gaussian rule
    rx = 700
    s += box(rx, 86, 284, 246, fill="#ffffff", stroke="rgba(45,49,66,0.35)")
    s += eyebrow(rx + 16, 110, "the test, by eye", fill=SOFT)
    lines = ["is each row a multiple of one row?", "yes: rank 1, the multipliers", "are the column factor",
             "no: count how many independent", "rows there are — that many", "column × row terms, 2 passes each"]
    for k, l in enumerate(lines):
        s += mono(rx + 16, 134 + k * 18, l, size=9, fill=INK if k in (0,) else MUTED, anchor="start")
    s += (f'<line x1="{rx + 16}" y1="254" x2="{rx + 268}" y2="254" stroke="{RULE}"/>')
    s += mono(rx + 16, 276, "separable and rotation-invariant", size=9, fill=ACCENT, anchor="start", weight="600")
    s += mono(rx + 16, 294, "at once: only the Gaussian", size=9, fill=ACCENT, anchor="start", weight="600")
    s += mono(rx + 16, 314, "(Kannappan & Sahoo 1992)", size=8, fill=SOFT, anchor="start")
    s += legend(496, vw, [("rank 1: separable", SER2, "box"), ("rank 2: sum of two separable terms", SER4, "box")])
    return emit("08", "rank-and-separability", "Rank and separability",
                "A kernel separates exactly when every row is a multiple of one row; otherwise its rank counts the separable terms.",
                "separability", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "a Gaussian's variance on the grid, as a fraction of σ²: sampled, cut to 3 taps, integrated, discrete")
    ax = Axes(80, 80, 560, 300, (0.3, 2.0), (0, 1.4))
    s += ax.frame([0.3, 0.5, 0.8, 1.0, 1.5, 2.0], [0, 0.25, 0.5, 0.75, 1.0, 1.25], xlab="σ, pixels",
                  ylab="variance / σ²", xfmt=lambda t: f"{t:g}", yfmt=lambda t: fmt(t, 2))
    s += polyline(ax.curve(lambda sg: 1.0, 0.3, 2.0, 4), INK, sw=1.4, dash="6,4")
    s += polyline(ax.curve(lambda sg: min(var_integrated(sg) / sg ** 2, 1.4), 0.3, 2.0, 170), SER3, sw=1.6)
    s += polyline(ax.curve(lambda sg: var_sampled(sg) / sg ** 2, 0.3, 2.0, 170), SER2, sw=1.8)
    s += polyline(ax.curve(lambda sg: var_sampled(sg, 1) / sg ** 2, 0.3, 2.0, 170), ACCENT, sw=2)
    # OpenCV tables at the documented sigma
    tables = {3: [1, 2, 1], 5: [1, 4, 6, 4, 1], 7: [2, 7, 14, 18, 14, 7, 2], 9: [4, 13, 30, 51, 60, 51, 30, 13, 4]}
    for n, t in tables.items():
        r = n // 2
        var = sum((i - r) ** 2 * v for i, v in enumerate(t)) / sum(t)
        sd = 0.3 * ((n - 1) * 0.5 - 1) + 0.8
        x, y = ax.X(sd), ax.Y(var / sd ** 2)
        s += f'<rect x="{x - 4:.1f}" y="{y - 4:.1f}" width="8" height="8" fill="{SER4}"/>'
        s += mono(x + 8, y + 3, f"{n}", size=8, fill=SER4, anchor="start", weight="600")
    # shared kernel, with a leader into open space
    v3 = var_sampled(0.8, 1)
    s += dot(ax.X(0.8), ax.Y(v3 / 0.64), r=5, fill=ACCENT)
    s += (f'<line x1="{ax.X(0.8) + 6:.1f}" y1="{ax.Y(v3 / 0.64):.1f}" x2="{ax.X(1.14):.1f}" '
          f'y2="{ax.Y(0.715):.1f}" stroke="{ACCENT}" stroke-width="0.8" stroke-dasharray="2,2"/>')
    s += mono(ax.X(1.15), ax.Y(0.715) + 3, f"shared kernel, 3 taps: {v3:.3f} / 0.64 = {v3 / 0.64:.2f}",
              size=8, fill=ACCENT, anchor="start", weight="600")
    s += dot(ax.X(0.8), ax.Y(var_sampled(0.8) / 0.64), r=4, fill=SER2)
    s += mono(ax.X(0.84), ax.Y(0.955), "untruncated: 0.6399 / 0.64", size=8, fill=SER2, anchor="start")
    s += mono(ax.X(0.32), ax.Y(1.04), "discrete analogue: exactly 1", size=8, fill=INK, anchor="start")
    s += mono(ax.X(1.1), ax.Y(1.12), "integrated: + 1/12 of a pixel²", size=8, fill=SER3, anchor="start")
    s += mono(ax.X(1.55), ax.Y(0.88), "OpenCV σ = 0 tables", size=8, fill=SER4, anchor="start")
    s += mono(ax.X(1.55), ax.Y(0.835), "at their documented σ", size=8, fill=SER4, anchor="start")
    # side table
    tx = 690
    s += eyebrow(tx, 96, "at σ = 0.8 (σ² = 0.64)", fill=SOFT)
    rows = [("sampled, untruncated", f"{var_sampled(0.8):.4f}", SER2),
            ("sampled, 3 taps (shared)", f"{v3:.4f}", ACCENT),
            ("OpenCV σ = 0, ksize 3", "0.5000", SER4),
            ("integrated", f"{var_integrated(0.8):.4f}", SER3),
            ("discrete analogue", "0.6400", INK)]
    for k, (a, b, col) in enumerate(rows):
        s += mono(tx, 124 + k * 22, a, size=9, fill=col, anchor="start")
        s += mono(tx + 270, 124 + k * 22, b, size=10, fill=col, anchor="end", weight="600")
    s += eyebrow(tx, 256, "sampling alone, untruncated", fill=SOFT)
    for k, sg in enumerate((0.3, 0.4, 0.5, 0.6)):
        r = var_sampled(sg) / sg ** 2 - 1
        s += mono(tx, 280 + k * 20, f"σ = {sg}", size=9, fill=MUTED, anchor="start")
        s += mono(tx + 270, 280 + k * 20, f"{r * 100:+.1f}%".replace("-", "−"), size=10, fill=SER2, anchor="end")
    s += legend(436, vw, [("sampled", SER2, "line"), ("sampled, 3 taps", ACCENT, "line"),
                          ("integrated", SER3, "line"), ("discrete analogue", INK, "line"),
                          ("OpenCV σ = 0 table", SER4, "box")])
    return emit("09", "sampled-truncated-discrete", "Sampling against truncation",
                "Truncation, not sampling, is what shrinks the shared kernel's variance. Evaluated from the definitions.",
                "taps for a gaussian", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "row r2 extended three pixels each way, and the normalised Sobel on the two edge columns")
    modes = [("constant 0", "constant", "BORDER_CONSTANT"), ("replicate", "replicate", "BORDER_REPLICATE"),
             ("reflect", "reflect", "BORDER_REFLECT"), ("reflect-101", "reflect-101", "BORDER_REFLECT_101"),
             ("wrap", "wrap", "BORDER_WRAP")]
    cw, ch = 40, 30
    x0 = 150
    for k, (label, mode, cv) in enumerate(modes):
        y = 88 + k * 76
        focal = mode == "reflect-101"
        s += txt(32, y + 20, label, size=12, weight="600", fill=ACCENT if focal else INK, anchor="start")
        s += mono(32, y + 36, cv, size=7, fill=SOFT, anchor="start")
        if focal:
            s += mono(32, y + 48, "OpenCV's default", size=7, fill=ACCENT, anchor="start")
        for i in range(-3, 8):
            v = ext(ROW, i, mode)
            x = x0 + (i + 3) * cw + (8 if i >= 0 else 0) + (8 if i >= 5 else 0)
            s += pix(x, y, cw, ch, v, size=10, invented=not (0 <= i < 5))
        # outputs
        p = 0.25
        get = lambda img, r, c, m=mode: ext(img[r], c, m)
        g0, rows0 = gx_family(PATCH, 2, 0, p, get)
        g4, rows4 = gx_family(PATCH, 2, 4, p, get)
        ox = x0 + 11 * cw + 40
        for j, (g, rows, lab) in enumerate(((g0, rows0, "at (r2, c0)"), (g4, rows4, "at (r2, c4)"))):
            bx = ox + j * 190
            hot = focal and j == 0
            s += box(bx, y - 4, 170, 40, fill=ACCENT_TINT if hot else "#ffffff",
                     stroke=ACCENT if hot else "rgba(45,49,66,0.35)")
            s += mono(bx + 10, y + 10, lab, size=8, fill=SOFT, anchor="start")
            s += mono(bx + 160, y + 12, fmt(g, 2), size=12, fill=ACCENT if hot else INK, anchor="end", weight="600")
            s += mono(bx + 10, y + 28, "rows " + " · ".join(fmt(r, 1) for r in rows), size=8, fill=MUTED, anchor="start")
    s += mono(x0 + 1.5 * cw, 78, "invented", size=8, fill=SOFT)
    s += mono(x0 + 3 * cw + 8 + 2.5 * cw, 78, "c0 … c4, the real row", size=8, fill=SOFT)
    s += mono(x0 + 8 * cw + 16 + 1.5 * cw, 78, "invented", size=8, fill=SOFT)
    # name map
    y = 474
    s += (f'<line x1="32" y1="{y - 18}" x2="{vw - 32}" y2="{y - 18}" stroke="{RULE}"/>')
    s += eyebrow(32, y, "the same two extensions under three libraries' names", fill=SOFT)
    hdr = [("extension", 32), ("OpenCV", 330), ("SciPy ndimage", 560), ("NumPy pad", 780)]
    for h, x in hdr:
        s += mono(x, y + 22, h, size=8, fill=SOFT, anchor="start")
    rowsn = [("repeat the edge pixel (half-sample)", "BORDER_REFLECT", "'reflect' — default", "'symmetric'"),
             ("mirror about it (whole-sample)", "BORDER_REFLECT_101 — default", "'mirror'", "'reflect'")]
    for k, r in enumerate(rowsn):
        yy = y + 42 + k * 20
        for (h, x), v in zip(hdr, r):
            s += mono(x, yy, v, size=9, fill=INK if x == 32 else (ACCENT if "reflect'" in v else MUTED),
                      anchor="start", weight="500")
    return emit("10", "borders-and-derivatives", "Five borders, five derivatives",
                "Reflect-101 gives exactly 0 on the edge column for any image; constant 0 and wrap invent edges. Worked by hand on row r2.",
                "borders", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 580
    s = eyebrow(32, 40, "which call builds which kernel, at what scale, with which border — mapped from docs and source, not run")
    cols = [("call", 32), ("weights", 300), ("gain on a unit ramp", 520), ("default border", 660), ("gotcha", 800)]
    y0 = 78
    for h, x in cols:
        s += mono(x, y0, h, size=8, fill=SOFT, anchor="start", track="0.08em")
    s += f'<line x1="32" y1="{y0 + 10}" x2="{vw - 32}" y2="{y0 + 10}" stroke="{RULE_SOLID}"/>'
    rows = [
        ("OpenCV", "cv2.Sobel(img, CV_32F, 1, 0, ksize=3)", "[1 2 1] × [−1 0 1], p = 1/4", "8", "reflect-101", "0 on the edge column"),
        ("OpenCV", "cv2.Sobel(..., ksize=5)", "[1 4 6 4 1] × [−1 −2 0 2 1]", "128", "reflect-101", "same direction error as 3"),
        ("OpenCV", "cv2.Scharr(img, CV_32F, 1, 0)", "[3 10 3] × [−1 0 1], p = 3/16", "32", "reflect-101", "4× Sobel's output"),
        ("OpenCV", "cv2.getDerivKernels(1, 0, k, normalize=True)", "the two factors", "1", "—", "ksize −1 = Scharr"),
        ("OpenCV", "cv2.GaussianBlur(img, (3,3), 0)", "[1 2 1]/4 table, not σ = 0.8", "—", "reflect-101", "σ ≤ 0, ksize 3–9: table"),
        ("OpenCV", "cv2.GaussianBlur(img, (0,0), σ)", "sampled, round(6σ+1) taps (8-bit)", "—", "reflect-101", "(3,3) with σ = 2 → σ 0.80"),
        ("SciPy", "ndimage.sobel(img, axis)", "[−1 0 1] × [1 2 1]", "8", "'reflect' (half)", "430 at (r2, c0)"),
        ("SciPy", "ndimage.gaussian_filter(img, σ)", "sampled, radius int(4σ + 0.5)", "—", "'reflect' (half)", "17 taps at σ = 2"),
        ("NumPy", "np.pad(a, n, mode)", "—", "—", "—", "'reflect' = whole-sample"),
        ("scikit-image", "filters.sobel / scharr", "[1 0 −1] × [1 2 1]/4, [3 10 3]/16", "2", "'reflect' (half)", "magnitude ÷ √2"),
        ("scikit-image", "filters.farid", "Farid–Simoncelli 5-tap pair", "0.99", "'reflect' (half)", "most isotropic here"),
    ]
    libcol = {"OpenCV": SER2, "SciPy": SER3, "NumPy": SER4, "scikit-image": SER1}
    for k, (lib, call, wts, gain, border, got) in enumerate(rows):
        y = y0 + 34 + k * 40
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 18}" width="{vw - 56}" height="40" fill="rgba(45,49,66,0.03)"/>'
        s += mono(32, y - 4, lib, size=7, fill=libcol[lib], anchor="start", track="0.12em", weight="600")
        s += mono(32, y + 10, call, size=9, fill=INK, anchor="start", weight="500")
        s += mono(300, y + 4, wts, size=9, fill=MUTED, anchor="start")
        s += mono(520, y + 4, gain, size=10, fill=ACCENT if gain in ("8", "32", "128") else INK, anchor="start", weight="600")
        s += mono(660, y + 4, border, size=9, fill=MUTED, anchor="start")
        s += mono(800, y + 4, got, size=9, fill=INK, anchor="start")
    s += mono(32, vh - 22, "gain on a unit ramp: what the call returns for a slope of 1 grey level per pixel; divide by it to threshold in grey levels per pixel",
              size=8, fill=SOFT, anchor="start")
    return emit("11", "tooling-map", "The tooling map",
                "Weights, raw scale and default border for the derivative and Gaussian calls in four libraries. None of it was executed.",
                "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06,
        "07": fig07, "08": fig08, "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
