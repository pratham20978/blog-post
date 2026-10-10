#!/usr/bin/env python3
"""Figures 01-13 for the-2d-dft-spectra-phase-filtering.

Every value drawn here is computed in this file, from the definitions, on the series'
5x5 patch, its transpose, its circular shift and its 2x2 tiling: the 2-D DFT and its
inverse, magnitude-only and phase-only rebuilds, the phase swap, the notch on the tiled
patch, leakage of an off-bin wave, the ideal and Gaussian low-pass on one row, phase
correlation, and the operation-count model (FFTW's 2.5 N log2 N convention for a
real-input transform). Nothing is measured and nothing loads an image.
Run:  python3 _figs.py [01 05 ...]
"""
import cmath
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, box, cell, emit, eyebrow,
                    legend, masked, mono, txt, vline, hline)

PI = math.pi
SER1, SER2, SER3, SER4 = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50"
CDC = "#8e7aa6"

# ------------------------------------------------------------------ the data
PATCH = [[40, 40, 40, 200, 200] for _ in range(5)]
PATCH[2][1] = 255
TRANS = [list(col) for col in zip(*PATCH)]
SHIFT = [[PATCH[(r - 1) % 5][(c - 2) % 5] for c in range(5)] for r in range(5)]
TILE = [[PATCH[r % 5][c % 5] for c in range(10)] for r in range(10)]
ROW0 = [40, 40, 40, 200, 200]
GAUSS = [0.239, 0.522, 0.239]


def dft2(f):
    M, N = len(f), len(f[0])
    return [[sum(f[r][c] * cmath.exp(-2j * PI * (kr * r / M + kc * c / N))
                 for r in range(M) for c in range(N))
             for kc in range(N)] for kr in range(M)]


def idft2(F):
    M, N = len(F), len(F[0])
    return [[(sum(F[kr][kc] * cmath.exp(2j * PI * (kr * r / M + kc * c / N))
                  for kr in range(M) for kc in range(N)) / (M * N)).real
             for c in range(N)] for r in range(M)]


def dft1(x):
    n = len(x)
    return [sum(x[t] * cmath.exp(-2j * PI * k * t / n) for t in range(n)) for k in range(n)]


def idft1(X):
    n = len(X)
    return [(sum(X[k] * cmath.exp(2j * PI * k * t / n) for k in range(n)) / n).real for t in range(n)]


def shift_order(n):
    """numpy.fft.fftshift's index order for one axis: roll by n // 2."""
    h = n // 2
    idx = list(range(n))
    return idx[-h:] + idx[:-h] if h else idx


def ishift_order(n):
    h = n // 2
    idx = list(range(n))
    return idx[h:] + idx[:h]


def freq(k, n):
    return k if k <= (n - 1) // 2 else k - n


def deg(z):
    d = math.degrees(cmath.phase(z))
    return 0.0 if abs(d) < 1e-9 or abs(abs(d) - 360) < 1e-9 else d


FA = dft2(PATCH)
FB = dft2(TRANS)
FC = dft2(SHIFT)
ROWPASS = [[sum(PATCH[r][c] * cmath.exp(-2j * PI * k * c / 5) for c in range(5)) for k in range(5)]
           for r in range(5)]
MAG_ONLY = idft2([[complex(abs(z), 0) for z in row] for row in FA])
PH_ONLY = idft2([[z / abs(z) for z in row] for row in FA])
SWAP_AB = idft2([[abs(FA[i][j]) * cmath.exp(1j * cmath.phase(FB[i][j])) for j in range(5)] for i in range(5)])
SWAP_BA = idft2([[abs(FB[i][j]) * cmath.exp(1j * cmath.phase(FA[i][j])) for j in range(5)] for i in range(5)])

# notch: 2x2 tiling + 20 cos(2 pi 3 r / 10)
BANDS = [20 * math.cos(2 * PI * 3 * r / 10) for r in range(10)]
CORRUPT = [[TILE[r][c] + BANDS[r] for c in range(10)] for r in range(10)]
FT = dft2(TILE)
FG = dft2(CORRUPT)
NOTCH = [[0.0 if (i, j) in ((3, 0), (7, 0)) else 1.0 for j in range(10)] for i in range(10)]
RESTORED = idft2([[NOTCH[i][j] * FG[i][j] for j in range(10)] for i in range(10)])
REST_ERR = max(abs(RESTORED[r][c] - TILE[r][c]) for r in range(10) for c in range(10))

# off-bin: 2.5 cycles in 10 rows
OFF = [20 * math.cos(PI * r / 2) for r in range(10)]
ON = BANDS
N_OFF = dft1(OFF)
N_ON = dft1(ON)

# low-pass on one row
S_ROW = dft1(ROW0)
IDEAL = idft1([S_ROW[k] if k in (0, 1, 4) else 0 for k in range(5)])
H_GAUSS = [GAUSS[1] + 2 * GAUSS[0] * math.cos(2 * PI * k / 5) for k in range(5)]
GAUSS_OUT = idft1([H_GAUSS[k] * S_ROW[k] for k in range(5)])

# phase correlation
XC = idft2([[FA[i][j] * FC[i][j].conjugate() for j in range(5)] for i in range(5)])
PC = idft2([[(FA[i][j] * FC[i][j].conjugate()) / abs(FA[i][j] * FC[i][j].conjugate())
             for j in range(5)] for i in range(5)])


def smooth5(n):
    while True:
        m = n
        for p in (2, 3, 5):
            while m % p == 0:
                m //= p
        if m == 1:
            return n
        n += 1


def fft_route(M, N, m, n_fft=3):
    P, Q = smooth5(M + m - 1), smooth5(N + m - 1)
    one = 2.5 * P * Q * math.log2(P * Q)
    return (n_fft * one + 6 * P * (Q // 2 + 1)) / (M * N)


# the article's numbers; a figure that disagrees with the text fails here
assert round(abs(FA[0][0])) == 2815 and round(abs(FA[0][1]), 2) == 1079.43
assert round(abs(FA[0][2]), 2) == 709.43 and all(round(abs(FA[i][j]), 6) == 215
                                                 for i in range(1, 5) for j in range(5))
assert round(MAG_ONLY[0][0], 2) == 427.71 and round(MAG_ONLY[1][0], 2) == 212.71
assert round(PH_ONLY[2][1], 3) == 0.840 and round(PH_ONLY[0][1], 3) == -0.160
assert round(SWAP_AB[1][2], 2) == 393.31 and round(SWAP_AB[0][0], 2) == 49.65
assert REST_ERR < 1e-9 and round(abs(FG[3][0]), 6) == 1000
assert [round(v, 2) for v in IDEAL] == [72.0, 0.45, 72.0, 187.78, 187.78]
assert [round(v, 2) for v in GAUSS_OUT] == [78.24, 40.0, 78.24, 161.76, 161.76]
assert round(PC[4][3], 9) == 1 and round(XC[4][3]) == 487425 and round(XC[0][3]) == 441200
assert round(fft_route(1920, 1080, 11), 1) == 169.8


# ------------------------------------------------------------------ drawing helpers
def fmt(v, nd=2):
    s = f"{v:.{nd}f}"
    if s.lstrip("-").strip("0.") == "":
        s = s.lstrip("-")
    return s.replace("-", "−")


def fang(d):
    return f"∠{fmt(round(d), 0)}°"


def shade_rect(x, y, w, h, t, stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None):
    """High value = bright (series rule): t = 1 is paper, t = 0 is ink."""
    t = max(0.0, min(1.0, t))
    a = 0.88 * (1 - t) + 0.02
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def ink_for(t):
    return "#ffffff" if t < 0.52 else INK


def pix(x, y, w, h, v, size=10, label=None):
    t = v / 255
    s = shade_rect(x, y, w, h, t)
    return s + txt(x + w / 2, y + h / 2 + size * 0.36, label if label is not None else str(v),
                   size=size, fill=ink_for(t), family=MONO, weight="500")


def vcell(x, y, w, h, v, lo, hi, label, size=9):
    t = (v - lo) / (hi - lo) if hi > lo else 1.0
    return shade_rect(x, y, w, h, t) + txt(x + w / 2, y + h / 2 + size * 0.36, label, size=size,
                                            fill=ink_for(t), family=MONO, weight="500")


def scell(x, y, w, h, z, lmax, show_angle=True, size=9, mag_nd=2):
    """A spectrum bin: log-shaded magnitude, magnitude printed, angle beneath."""
    m = abs(z)
    t = math.log10(1 + m) / lmax
    s = shade_rect(x, y, w, h, t)
    col = ink_for(t)
    if show_angle:
        s += txt(x + w / 2, y + h / 2 - 1, fmt(m, mag_nd), size=size, fill=col, family=MONO, weight="500")
        s += txt(x + w / 2, y + h / 2 + size + 1, fang(deg(z)) if m > 1e-9 else "", size=size - 1,
                 fill=col, family=MONO)
    else:
        s += txt(x + w / 2, y + h / 2 + size * 0.36, fmt(m, mag_nd), size=size, fill=col,
                 family=MONO, weight="500")
    return s


def outline(x, y, w, h, stroke=ACCENT, sw=2, dash=None, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def axis_labels(gx, gy, cs, n, rows, cols, size=8):
    s = ""
    for i, lab in enumerate(cols):
        s += mono(gx + i * cs + cs / 2, gy - 7, lab, size=size, fill=SOFT)
    for i, lab in enumerate(rows):
        s += mono(gx - 8, gy + i * cs + cs / 2 + 3, lab, size=size, fill=SOFT, anchor="end")
    return s


def arrow_right(x1, x2, y, label=None, label2=None, colour=MUTED):
    s = hline(x1, x2, y, stroke=colour, sw=1.2)
    if label:
        s += mono((x1 + x2) / 2, y - 10, label, size=8, fill=colour)
    if label2:
        s += mono((x1 + x2) / 2, y + 16, label2, size=8, fill=SOFT)
    return s


def polyline(pts, stroke, sw=1.4, dash=None, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity else ""
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}{o}/>')


def dot(x, y, r=3.2, fill=INK, stroke=None):
    st = f' stroke="{stroke}" stroke-width="1.2"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{st}/>'


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr, logy=False):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xr, self.yr, self.logy = xr, yr, logy

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        if self.logy:
            lo, hi = math.log10(self.yr[0]), math.log10(self.yr[1])
            return self.y0 + self.h - (math.log10(y) - lo) / (hi - lo) * self.h
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid=True):
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
        if xlab:
            s += eyebrow(self.x0 + self.w, self.y0 + self.h + 30, xlab, anchor="end")
        if ylab:
            s += eyebrow(self.x0, self.y0 - 10, ylab, anchor="start")
        return s


def patch_grid(gx, gy, cs, img, size=10, labels=True):
    s = ""
    for r in range(len(img)):
        for c in range(len(img[0])):
            s += pix(gx + c * cs, gy + r * cs, cs, cs, img[r][c], size=size)
    if labels:
        s += axis_labels(gx, gy, cs, len(img), [f"r{r}" for r in range(len(img))],
                         [f"c{c}" for c in range(len(img[0]))])
    return s


def value_grid(gx, gy, cs, A, nd=2, size=9, lo=None, hi=None):
    flat = [v for row in A for v in row]
    lo = min(flat) if lo is None else lo
    hi = max(flat) if hi is None else hi
    s = ""
    for r, row in enumerate(A):
        for c, v in enumerate(row):
            s += vcell(gx + c * cs, gy + r * cs, cs, cs, v, lo, hi, fmt(v, nd), size=size)
    return s


def fmag(m):
    """Magnitude for a cell: an integer when it is one, else one decimal."""
    return fmt(round(m), 0) if abs(m - round(m)) < 1e-6 else fmt(m, 1)


def note_lines(x, y, items, size=9, gap=15):
    s = ""
    for k, (text, colour) in enumerate(items):
        s += mono(x, y + k * gap, text, size=size, fill=colour, anchor="start")
    return s


def legend2(y, vw, items):
    """Legend whose swatches are drawn exactly like the marks they name.
    item: (label, colour, kind, opacity) with kind in line | dash | box | outline."""
    s = (f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" '
         f'stroke="{RULE}" stroke-width="0.8"/>')
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for label, colour, kind, op in items:
        if kind in ("line", "dash"):
            d = ' stroke-dasharray="4,3"' if kind == "dash" else ""
            s += (f'<line x1="{x}" y1="{y + 5}" x2="{x + 16}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.8"{d}/>')
        elif kind == "box":
            s += (f'<rect x="{x}" y="{y}" width="12" height="10" fill="{colour}" '
                  f'fill-opacity="{op}"/>')
        else:
            s += (f'<rect x="{x}" y="{y}" width="12" height="10" fill="none" stroke="{colour}" '
                  f'stroke-width="1.6"/>')
        s += mono(x + 22, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.06em")
        x += 22 + 6.2 * len(label) + 30
    return s


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 476
    s = eyebrow(32, 40, "the 2-d dft separates: a 5-point dft of every row, then a 5-point dft of every column")
    lmax = math.log10(1 + 2815)
    gy, cs = 118, 52                       # complex grids: 5 x 52 = 260 tall
    px, pcs = 52, 34                       # patch: 5 x 34 = 170, centred on the grids
    ppy = gy + (5 * cs - 5 * pcs) / 2
    rx, fx = 336, 712
    s += eyebrow(px, 92, "the patch f(r, c)")
    s += patch_grid(px, ppy, pcs, PATCH, size=9)
    s += eyebrow(rx, 92, "after the row pass")
    s += eyebrow(fx, 92, "after the column pass: F(kr, kc)")
    for r in range(5):
        for k in range(5):
            s += scell(rx + k * cs, gy + r * cs, cs, cs, ROWPASS[r][k], lmax, size=9)
            s += scell(fx + k * cs, gy + r * cs, cs, cs, FA[r][k], lmax, size=9)
    s += axis_labels(rx, gy, cs, 5, [f"r{r}" for r in range(5)], [f"kc {k}" for k in range(5)])
    s += axis_labels(fx, gy, cs, 5, [f"kr {r}" for r in range(5)], [f"kc {k}" for k in range(5)])
    s += outline(rx, gy + 2 * cs, 5 * cs, cs, stroke=ACCENT, sw=2)
    s += outline(fx, gy, 5 * cs, cs, stroke=LINK, sw=2)
    ay = gy + 2.5 * cs
    s += hline(px + 5 * pcs + 10, rx - 30, ay, stroke=MUTED, sw=1.2)
    s += mono((px + 5 * pcs + 10 + rx - 30) / 2, ay - 10, "row dft", size=8, fill=MUTED)
    s += hline(rx + 5 * cs + 10, fx - 38, ay, stroke=MUTED, sw=1.2)
    s += mono((rx + 5 * cs + 10 + fx - 38) / 2, ay - 10, "column dft", size=8, fill=MUTED)
    ny = gy + 5 * cs + 32
    s += note_lines(px, ny, [("w = e^(−2πi/5)", MUTED), ("shading: log10(1 + |·|)", SOFT),
                             ("cells: magnitude, angle", SOFT)], size=8)
    s += note_lines(rx, ny, [("r0, r1, r3, r4: S(k) = 160 (w^3k + w^4k)", INK),
                             ("r2: S(k) + 215 w^k, the impulse at c1", ACCENT),
                             ("k = ±1: 258.89 − 215;  k = ±2: 98.89 + 215", SOFT)])
    s += note_lines(fx, ny, [("kr = 0: 5 S(kc) + 215 w^kc, the edge", LINK),
                             ("other bins: 215 w^(2kr + kc)", INK),
                             ("magnitude exactly 215: the impulse", SOFT)])
    return emit("01", "rows-then-columns", "Rows first, then columns",
                "The patch's 2-D DFT computed in two passes of 5-point transforms. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 440
    s = eyebrow(32, 40, "the centred spectrum: fftshift puts dc in the middle; shading is log10(1 + |F|)")
    px, py, pcs = 56, 112, 48
    s += eyebrow(px, 84, "the patch")
    s += patch_grid(px, py, pcs, PATCH, size=10)
    s += mono(px + 2.5 * pcs, py + 5 * pcs + 26, "vertical edge between c2 and c3;", size=8, fill=SOFT)
    s += mono(px + 2.5 * pcs, py + 5 * pcs + 40, "one impulse of 255 at (r2, c1)", size=8, fill=SOFT)
    sx, sy, cs = 380, 112, 62
    order = shift_order(5)
    lmax = math.log10(1 + 2815)
    s += eyebrow(sx, 84, "|F(kr, kc)|, centred")
    for i, kr in enumerate(order):
        for j, kc in enumerate(order):
            m = abs(FA[kr][kc])
            t = math.log10(1 + m) / lmax
            s += shade_rect(sx + j * cs, sy + i * cs, cs, cs, t)
            s += txt(sx + j * cs + cs / 2, sy + i * cs + cs / 2 + 4, fmag(m), size=10,
                     fill=ink_for(t), family=MONO, weight="500")
    lab = lambda k: fmt(freq(k, 5), 0) if freq(k, 5) <= 0 else f"+{freq(k, 5)}"
    s += axis_labels(sx, sy, cs, 5, [f"kr {lab(k)}" for k in order], [f"kc {lab(k)}" for k in order])
    s += outline(sx + 2 * cs, sy + 2 * cs, cs, cs, stroke=ACCENT, sw=2.2)
    s += outline(sx, sy + 2 * cs, 5 * cs, cs, stroke=LINK, sw=1.6, dash="5,3")
    ax = sx + 5 * cs + 28
    notes = [(ACCENT, "DC  F(0, 0) = 2,815", "the pixel sum: 25 × the mean 112.6"),
             (LINK, "the bright row  kr = 0", "waves constant down columns: the edge"),
             (INK, "the floor  |F| = 215", "the impulse: every wave equally")]
    y = sy + 10
    floor_t = math.log10(1 + 215) / lmax
    swatches = [
        f'<rect x="{{x}}" y="{{y}}" width="10" height="10" fill="#ffffff" stroke="{ACCENT}" stroke-width="2"/>',
        f'<rect x="{{x}}" y="{{y}}" width="10" height="10" fill="none" stroke="{LINK}" stroke-width="1.6" stroke-dasharray="3,2"/>',
        f'<rect x="{{x}}" y="{{y}}" width="10" height="10" fill="rgba(45,49,66,{0.88 * (1 - floor_t) + 0.02:.3f})" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>',
    ]
    for (col, head, sub), sw_ in zip(notes, swatches):
        s += sw_.format(x=ax, y=y - 10)
        s += mono(ax + 18, y, head, size=10, fill=col, anchor="start", weight="600")
        s += mono(ax + 18, y + 15, sub, size=8, fill=SOFT, anchor="start")
        y += 48
    by = sy + 166
    s += eyebrow(ax, by, "energy: Σ|F|² = 25 Σf²")
    shares = [(0.6503, ACCENT, "DC 65.0%"), (0.2738, LINK, "row 27.4%"), (0.0759, MUTED, "floor 7.6%")]
    bx, bw = ax, 220
    for frac, col, _ in shares:
        s += f'<rect x="{bx:.1f}" y="{by + 10}" width="{frac * bw:.1f}" height="14" fill="{col}" fill-opacity="0.85"/>'
        bx += frac * bw
    for k, (_, col, lab_) in enumerate(shares):
        s += mono(ax + k * 76, by + 42, lab_, size=8, fill=col, anchor="start")
    ly = by + 82
    s += eyebrow(ax, ly, "log10(1 + |F|)")
    for k, (m, lv) in enumerate(((2815, "3.45"), (1079.43, "3.03"), (709.43, "2.85"), (215, "2.33"))):
        s += mono(ax + k * 58, ly + 18, fmt(m, 0), size=9, fill=INK, anchor="start")
        s += mono(ax + k * 58, ly + 32, lv, size=9, fill=SOFT, anchor="start")
    return emit("02", "centred-spectrum", "The spectrum, centred",
                "A vertical edge prints a horizontal line; one bright pixel prints a flat floor.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 456
    s = eyebrow(32, 40, "invert with one half of every coefficient: magnitude with zero phase, or phase with unit magnitude")
    cs, gy = 52, 112
    xs = [48, 372, 696]
    heads = [("the patch", "f(r, c)"), ("magnitude only", "inverse of |F|, phase set to 0"),
             ("phase only", "inverse of F / |F|")]
    for (t, sub), gx in zip(heads, xs):
        s += eyebrow(gx, 70, t)
        s += mono(gx, 85, sub, size=8, fill=SOFT, anchor="start")
    s += patch_grid(xs[0], gy, cs, PATCH, size=10)
    s += value_grid(xs[1], gy, cs, MAG_ONLY, nd=2, size=9)
    s += value_grid(xs[2], gy, cs, PH_ONLY, nd=3, size=8.5)
    for gx in xs[1:]:
        s += axis_labels(gx, gy, cs, 5, [f"r{r}" for r in range(5)], [f"c{c}" for c in range(5)])
    s += outline(xs[0] + cs, gy + 2 * cs, cs, cs)
    s += outline(xs[1], gy, cs, cs)
    s += outline(xs[2] + cs, gy + 2 * cs, cs, cs)
    ny = gy + 5 * cs + 30
    s += note_lines(xs[0], ny, [("impulse at (r2, c1); dark left,", INK),
                                ("bright right, edge between c2 and c3", INK)])
    s += note_lines(xs[1], ny, [("impulse moved to the corner: 427.71", ACCENT),
                                ("rows symmetric about c0: a hump", INK)])
    s += note_lines(xs[2], ny, [("impulse kept at (r2, c1): 0.840", ACCENT),
                                ("dark left, bright right, c2 → c3", INK)])
    s += mono(32, vh - 16, "each panel is shaded on its own range, high = bright; phase-only values are small because unit magnitudes carry little energy",
              size=8, fill=SOFT, anchor="start")
    return emit("03", "phase-only-magnitude-only", "Keep the phase, or keep the magnitude",
                "Phase keeps where things are; magnitude moves them to the origin.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 452
    s = eyebrow(32, 40, "swap halves between the patch a and its transpose b, then invert")
    cs, gy = 42, 122
    xs = [52, 292, 532, 772]
    heads = [("A, the patch", "vertical edge, impulse (r2, c1)", SOFT),
             ("B = Aᵀ", "horizontal edge, impulse (r1, c2)", SOFT),
             ("|A| with the phase of B", "magnitude from A, phase from B", ACCENT),
             ("|B| with the phase of A", "magnitude from B, phase from A", ACCENT)]
    for (t, sub, col), gx in zip(heads, xs):
        s += eyebrow(gx, 78, t, fill=col)
        s += mono(gx, 92, sub, size=8, fill=SOFT, anchor="start")
    s += patch_grid(xs[0], gy, cs, PATCH, size=9)
    s += patch_grid(xs[1], gy, cs, TRANS, size=9)
    for gx, A in ((xs[2], SWAP_AB), (xs[3], SWAP_BA)):
        for r in range(5):
            for c in range(5):
                s += vcell(gx + c * cs, gy + r * cs, cs, cs, A[r][c], 0, 400, fmt(A[r][c], 1), size=8.5)
        s += axis_labels(gx, gy, cs, 5, [f"r{r}" for r in range(5)], [f"c{c}" for c in range(5)])
    for gx, (r, c) in zip(xs, ((2, 1), (1, 2), (1, 2), (2, 1))):
        s += outline(gx + c * cs, gy + r * cs, cs, cs)
    s += outline(xs[2] + 2 * cs - 3, gy - 3, cs + 6, 5 * cs + 6, stroke=LINK, sw=1.6, dash="5,3")
    s += outline(xs[3] - 3, gy + 2 * cs - 3, 5 * cs + 6, cs + 6, stroke=LINK, sw=1.6, dash="5,3")
    ny = gy + 5 * cs + 32
    s += note_lines(xs[0], ny, [("|F_B| is |F_A| transposed:", INK), ("a bright column, not a bright row", INK),
                                ("position follows phase; orientation follows magnitude", MUTED)])
    s += note_lines(xs[2], ny, [("impulse at B's (r1, c2): 393.3", ACCENT), ("rows 3–4 brighter: B's step", INK),
                                ("but the bar is vertical: |A|", LINK)])
    s += note_lines(xs[3], ny, [("impulse at A's (r2, c1): 393.3", ACCENT), ("columns 3–4 brighter: A's step", INK),
                                ("but the bar is horizontal: |B|", LINK)])
    s += mono(32, vh - 16, "swap panels shaded 0 to 400, high = bright; A and B as grey levels", size=8,
              fill=SOFT, anchor="start")
    return emit("04", "phase-swap", "Swapping phase between two images",
                "Positions come from the phase donor; the dominant bar's orientation comes from the magnitude donor.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 846
    s = eyebrow(32, 40, "the patch tiled 2×2 plus 20 cos(2π·3r/10): designed from the spectrum, removed exactly")
    cs = 28
    A = (64, 116)        # corrupted          (top left)
    B = (588, 116)       # centred spectrum   (top right)
    C = (588, 520)       # notch mask         (bottom right)
    D = (64, 520)        # restored           (bottom left)
    order = shift_order(10)
    fl = [freq(k, 10) for k in order]
    flab = [fmt(f, 0) if f <= 0 else f"+{f}" for f in fl]
    # A
    s += eyebrow(A[0], A[1] - 34, "1 · corrupted image (real-valued)")
    hi, lo = max(max(r) for r in CORRUPT), min(min(r) for r in CORRUPT)
    for r in range(10):
        for c in range(10):
            v = CORRUPT[r][c]
            s += vcell(A[0] + c * cs, A[1] + r * cs, cs, cs, v, 0, 255, fmt(v, 1), size=6.5)
        s += mono(A[0] + 10 * cs + 8, A[1] + r * cs + cs / 2 + 3, f"{'+' if BANDS[r] >= 0 else ''}{fmt(BANDS[r], 1)}",
                  size=7, fill=ACCENT, anchor="start")
    s += mono(A[0] + 10 * cs + 8, A[1] - 8, "band", size=7, fill=ACCENT, anchor="start")
    s += axis_labels(A[0], A[1], cs, 10, [f"r{r}" for r in range(10)], [f"c{c}" for c in range(10)], size=7)
    # B
    s += eyebrow(B[0], B[1] - 34, "2 · |F|, centred, log-shaded")
    lmax = math.log10(1 + 11260)
    for i, kr in enumerate(order):
        for j, kc in enumerate(order):
            m = abs(FG[kr][kc])
            t = math.log10(1 + m) / lmax if m > 1e-6 else 0
            s += shade_rect(B[0] + j * cs, B[1] + i * cs, cs, cs, t)
            if m > 1e-6:
                s += txt(B[0] + j * cs + cs / 2, B[1] + i * cs + cs / 2 + 3, fmt(round(m), 0), size=6.5,
                         fill=ink_for(t), family=MONO, weight="500")
            if kr % 2 == 0 and kc % 2 == 0:
                s += outline(B[0] + j * cs + 2, B[1] + i * cs + 2, cs - 4, cs - 4, stroke=SER1, sw=0.9)
    s += axis_labels(B[0], B[1], cs, 10, flab, flab, size=7)
    for kr in (3, 7):
        i, j = order.index(kr), order.index(0)
        s += outline(B[0] + j * cs, B[1] + i * cs, cs, cs, stroke=ACCENT, sw=2.2)
    s += mono(B[0], B[1] + 10 * cs + 20, "green inner box: a tile bin (both indices even)", size=8, fill=SER1, anchor="start")
    s += mono(B[0], B[1] + 10 * cs + 34, "orange: the two spikes, (±3, 0), 1,000 each", size=8, fill=ACCENT, anchor="start")
    # C
    s += eyebrow(C[0], C[1] - 34, "3 · the notch H: 0 at the spikes, 1 elsewhere")
    for i, kr in enumerate(order):
        for j, kc in enumerate(order):
            h = NOTCH[kr][kc]
            s += shade_rect(C[0] + j * cs, C[1] + i * cs, cs, cs, h)
            s += txt(C[0] + j * cs + cs / 2, C[1] + i * cs + cs / 2 + 3, "1" if h else "0", size=7,
                     fill=ink_for(h), family=MONO, weight="500")
            if not h:
                s += outline(C[0] + j * cs, C[1] + i * cs, cs, cs, stroke=ACCENT, sw=2.2)
    s += axis_labels(C[0], C[1], cs, 10, flab, flab, size=7)
    # D
    s += eyebrow(D[0], D[1] - 34, "4 · restored = the tile, to 3 × 10⁻¹²")
    for r in range(10):
        for c in range(10):
            v = RESTORED[r][c]
            s += pix(D[0] + c * cs, D[1] + r * cs, cs, cs, round(v), size=7)
    s += axis_labels(D[0], D[1], cs, 10, [f"r{r}" for r in range(10)], [f"c{c}" for c in range(10)], size=7)
    # arrows: A -> B -> C -> D
    s += hline(A[0] + 10 * cs + 44, B[0] - 44, A[1] + 5 * cs, stroke=MUTED, sw=1.2)
    s += mono((A[0] + 10 * cs + 44 + B[0] - 44) / 2, A[1] + 5 * cs - 10, "fft2", size=8, fill=MUTED)
    s += vline(B[0] + 5 * cs, B[1] + 10 * cs + 46, C[1] - 44, stroke=MUTED, sw=1.2)
    s += mono(B[0] + 5 * cs + 12, B[1] + 10 * cs + 64, "zero the two spikes", size=8, fill=MUTED, anchor="start")
    s += hline(C[0] - 30, D[0] + 10 * cs + 44, C[1] + 5 * cs, stroke=MUTED, sw=1.2)
    s += mono((C[0] - 30 + D[0] + 10 * cs + 44) / 2, C[1] + 5 * cs - 10, "H · F, ifft2", size=8, fill=MUTED)
    s += mono(32, vh - 16, "spectrum and mask drawn centred (fftshift) for reading; the filter is applied in fft2's own layout",
              size=8, fill=SOFT, anchor="start")
    return emit("05", "notch-on-the-tile", "One periodic artefact, removed with a notch",
                "The interference lands on two bins the tile never uses; zeroing them restores the tile exactly.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def arrow_cell(x, y, cs, d, colour, ghost=None):
    cx, cy, L = x + cs / 2, y + cs / 2 + 5, cs * 0.30
    s = (f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="#ffffff" '
         f'stroke="rgba(45,49,66,0.25)" stroke-width="0.8"/>')
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{L:.1f}" fill="none" stroke="{RULE}" stroke-width="0.8"/>'
    if ghost is not None:
        gx, gy = cx + L * math.cos(math.radians(ghost)), cy - L * math.sin(math.radians(ghost))
        s += (f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{gx:.1f}" y2="{gy:.1f}" stroke="{SOFT}" '
              f'stroke-width="1" stroke-dasharray="2,2"/>')
    a = math.radians(d)
    ux, uy = math.cos(a), -math.sin(a)                 # unit vector in SVG coordinates
    tipx, tipy = cx + L * ux, cy + L * uy
    head, half = 6.0, 3.2
    bx, by = tipx - head * ux, tipy - head * uy        # base of the head
    s += (f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{colour}" '
          f'stroke-width="1.6"/>')
    s += (f'<polygon points="{tipx:.1f},{tipy:.1f} {bx - half * uy:.1f},{by + half * ux:.1f} '
          f'{bx + half * uy:.1f},{by - half * ux:.1f}" fill="{colour}"/>')
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="1.8" fill="{colour}"/>'
    s += mono(x + cs / 2, y + 11, f"{fmt(round(d), 0)}°", size=7.5, fill=colour)
    return s


def fig06():
    vw, vh = 1016, 522
    s = eyebrow(32, 40, "the phase of every bin as an arrow; a shift adds a ramp, and the ramp's slope is the position")
    cs, gy = 64, 112
    L, R = 70, 600
    s += eyebrow(L, 86, "the patch: angle of F(kr, kc)")
    s += eyebrow(R, 86, "shifted one column right: every arrow turns −72°·kc")
    for kr in range(5):
        for kc in range(5):
            d0 = deg(FA[kr][kc])
            d1 = (d0 - 72 * kc + 180) % 360 - 180
            col0 = LINK if kr == 0 else MUTED
            s += arrow_cell(L + kc * cs, gy + kr * cs, cs, d0, col0)
            s += arrow_cell(R + kc * cs, gy + kr * cs, cs, d1, ACCENT if kc else col0, ghost=d0 if kc else None)
    for gx in (L, R):
        s += axis_labels(gx, gy, cs, 5, [f"kr {r}" for r in range(5)], [f"kc {k}" for k in range(5)])
        s += outline(gx, gy, 5 * cs, cs, stroke=LINK, sw=1.4, dash="5,3")
    s += hline(L + 5 * cs + 22, R - 48, gy + 2.5 * cs, stroke=MUTED, sw=1.2)
    s += mono((L + 5 * cs + 22 + R - 48) / 2, gy + 2.5 * cs - 10, "shift one column", size=8, fill=MUTED)
    s += mono((L + 5 * cs + 22 + R - 48) / 2, gy + 2.5 * cs + 18, "right", size=8, fill=MUTED)
    ny = gy + 5 * cs + 30
    s += note_lines(L, ny, [("floor bins: 215 at angle −72°·(2kr + kc)", MUTED),
                            ("−72° per kc step → column 1; −144° per kr step → row 2", INK),
                            ("dashed row kr = 0: the edge's own angles", LINK)])
    s += note_lines(R, ny, [("(0, 1): 108° → 36°;  (1, 1): 144° → 72°", ACCENT),
                            ("kc = 0 column unchanged; every magnitude unchanged", INK),
                            ("dotted: the angle before the shift", SOFT)])
    return emit("06", "phase-ramp", "Position is the slope of a phase ramp",
                "The impulse's row and column are the slopes of its phase; a shift turns every arrow in proportion to its frequency.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 486
    s = eyebrow(32, 40, "where each bin goes: the frequency stored at each position, through numpy.fft.fftshift and ifftshift")
    lx, bx, bw, bh = 40, 222, 44, 28
    y = 92
    for n in (5, 10):
        s += mono(lx, y, f"n = {n}{', odd' if n % 2 else ', even'}", size=10, fill=INK, anchor="start", weight="600")
        sh = shift_order(n)
        centred = sh
        back = [centred[i] for i in ishift_order(n)]
        twice = [centred[i] for i in sh]
        rows = [("as computed", list(range(n)), None),
                ("fftshift (centred)", centred, None),
                ("then ifftshift", back, "✓ restored"),
                ("then fftshift again", twice, "✓ restored" if twice == list(range(n)) else "✗ DC in the last place")]
        for k, (lab, idx, mark) in enumerate(rows):
            yy = y + 14 + k * (bh + 8)
            s += mono(lx, yy + bh / 2 + 3, lab, size=9, fill=MUTED, anchor="start")
            for i, b in enumerate(idx):
                f = freq(b, n)
                focal = f == 0
                nyq = n % 2 == 0 and f == -n // 2
                fill = ACCENT_TINT if focal else ("rgba(94,122,155,0.10)" if nyq else "#ffffff")
                stroke = ACCENT if focal else (SER2 if nyq else "rgba(45,49,66,0.30)")
                s += (f'<rect x="{bx + i * bw}" y="{yy}" width="{bw - 4}" height="{bh}" rx="3" '
                      f'fill="{fill}" stroke="{stroke}" stroke-width="{1.6 if focal or nyq else 0.8}"/>')
                s += mono(bx + i * bw + (bw - 4) / 2, yy + bh / 2 + 4, fmt(f, 0) if f <= 0 else f"+{f}",
                          size=10, fill=ACCENT if focal else (SER2 if nyq else INK), weight="600" if focal else "400")
            if mark:
                s += mono(bx + n * bw + 10, yy + bh / 2 + 4, mark, size=9,
                          fill=ACCENT if mark.startswith("✗") else SER1, anchor="start", weight="600")
        y += 14 + 4 * (bh + 8) + 34
    s += note_lines(752, 130, [("fftshift rolls by n//2,", MUTED), ("ifftshift by −(n//2):", MUTED),
                               ("on odd n they differ", ACCENT), ("by one place", ACCENT)], size=9)
    s += note_lines(752, 318, [("on even n both roll by 5;", MUTED), ("−5, the Nyquist bin,", SER2),
                               ("has no positive partner", SER2)], size=9)
    s += mono(32, vh - 16, "boxes show the frequency stored at each position; orange is DC, blue the Nyquist bin",
              size=8, fill=SOFT, anchor="start")
    return emit("07", "fftshift-odd-even", "Where each frequency sits",
                "On odd sizes fftshift and ifftshift differ by one place; on even sizes they agree.",
                "reading a spectrum", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 496
    s = eyebrow(32, 40, "what the dft transforms: the patch as one tile of a periodic plane")
    cs, gx, gy = 24, 52, 88
    for R_ in range(15):
        for C_ in range(15):
            centre = 5 <= R_ < 10 and 5 <= C_ < 10
            cellsvg = pix(gx + C_ * cs, gy + R_ * cs, cs, cs, PATCH[R_ % 5][C_ % 5], size=6.5)
            s += cellsvg if centre else f'<g opacity="0.42">{cellsvg}</g>'
    
    for k in (5, 10):
        x = gx + k * cs
        s += (f'<line x1="{x}" y1="{gy - 6}" x2="{x}" y2="{gy + 15 * cs + 6}" stroke="{ACCENT}" '
              f'stroke-width="2.4"/>')
        y = gy + k * cs
        s += (f'<line x1="{gx - 6}" y1="{y}" x2="{gx + 15 * cs + 6}" y2="{y}" stroke="{SER1}" '
              f'stroke-width="1.2" stroke-dasharray="4,3"/>')
    s += mono(gx + 7.5 * cs, gy + 15 * cs + 24, "full strength: the patch; faded: the tiles the DFT assumes", size=8, fill=SOFT)
    tx = 470
    s += eyebrow(tx, 96, "the invented edge")
    s += note_lines(tx, 116, [("orange: c4's 200 meets the next tile's c0 at 40,", ACCENT),
                              ("a second step of −160 the patch does not contain", INK),
                              ("green dashed: r4 meets r0 — the same row, no jump", SER1)], size=9)
    s += eyebrow(tx, 190, "on a photograph")
    s += note_lines(tx, 210, [("left ≠ right puts a line through DC along kc;", INK),
                              ("top ≠ bottom puts one along kr: the cross", INK)], size=9)
    fixes = [("taper", "multiply by a Hann window: the borders go to 0", INK),
             ("mirror", "reflect first: the jump becomes a kink; = DCT", INK),
             ("split", "periodic + smooth: tile the first, carry the mismatch in the second", INK),
             ("not zero padding", "padding with 0 adds a jump to black at the new border", ACCENT)]
    y = 272
    for name, what, col in fixes:
        s += box(tx, y, 512, 34, fill="#ffffff", stroke="rgba(45,49,66,0.25)", rx=4)
        s += mono(tx + 12, y + 21, name, size=10, fill=col, anchor="start", weight="600")
        s += mono(tx + 132, y + 21, what, size=8.5, fill=MUTED, anchor="start")
        y += 42
    return emit("08", "tiled-patch-cross", "The cross the DFT invents",
                "The DFT computes the spectrum of the tiling; mismatched borders become edges.",
                "reading a spectrum", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 486
    s = eyebrow(32, 40, "two low-pass designs on the row 40 40 40 200 200: the gains, then what they return (circular, n = 5)")
    ax = Axes(80, 92, 380, 236, (-PI, PI), (-0.05, 1.12))
    s += ax.frame([-4 * PI / 5, -2 * PI / 5, 0, 2 * PI / 5, 4 * PI / 5], [0, 0.25, 0.5, 0.75, 1.0],
                  xlab="frequency, bins k = −2 … 2", ylab="gain H(k)",
                  xfmt=lambda v: {-4 * PI / 5: "k −2", -2 * PI / 5: "k −1", 0: "k 0", 2 * PI / 5: "k +1",
                                  4 * PI / 5: "k +2"}[v], yfmt=lambda v: fmt(v, 2))
    s += polyline([(ax.X(w), ax.Y(GAUSS[1] + 2 * GAUSS[0] * math.cos(w)))
                   for w in [(-PI + 2 * PI * i / 300) for i in range(301)]], SER2, sw=1.2, dash="4,3")
    for k in (-2, -1, 0, 1, 2):
        w = 2 * PI * k / 5
        gi = 1.0 if abs(k) <= 1 else 0.0
        gg = H_GAUSS[k % 5]
        xi, xg = ax.X(w) - 5, ax.X(w) + 5
        s += f'<line x1="{xi:.1f}" y1="{ax.Y(0):.1f}" x2="{xi:.1f}" y2="{ax.Y(gi):.1f}" stroke="{ACCENT}" stroke-width="2.2"/>'
        s += dot(xi, ax.Y(gi), r=3.4, fill=ACCENT)
        s += f'<line x1="{xg:.1f}" y1="{ax.Y(0):.1f}" x2="{xg:.1f}" y2="{ax.Y(gg):.1f}" stroke="{SER2}" stroke-width="2.2"/>'
        s += dot(xg, ax.Y(gg), r=3.4, fill=SER2)
        if k >= 0:
            s += mono(xg + 8, ax.Y(gg) - 4, fmt(gg, 3), size=8, fill=SER2, anchor="start")
    s += note_lines(80, 372, [("orange stems: the ideal gains, 1 at k = 0, ±1 and 0 at ±2", ACCENT),
                              ("blue stems: the shared Gaussian's gains; dashed: 0.522 + 0.478 cos ω between them", SER2)], size=8)
    bx = Axes(580, 92, 380, 236, (-0.4, 4.4), (-20, 240))
    s += bx.frame([0, 1, 2, 3, 4], [0, 40, 100, 160, 200], xlab="column c", ylab="output",
                  xfmt=lambda v: f"c{v}", yfmt=lambda v: fmt(v, 0))
    s += polyline([(bx.X(c), bx.Y(v)) for c, v in enumerate(ROW0)], SOFT, sw=1.2, dash="3,3")
    s += polyline([(bx.X(c), bx.Y(v)) for c, v in enumerate(IDEAL)], ACCENT, sw=1.8)
    s += polyline([(bx.X(c), bx.Y(v)) for c, v in enumerate(GAUSS_OUT)], SER2, sw=1.8)
    for c in range(5):
        s += dot(bx.X(c), bx.Y(ROW0[c]), r=2.6, fill=SOFT)
        s += dot(bx.X(c), bx.Y(IDEAL[c]), r=3.4, fill=ACCENT)
        s += dot(bx.X(c), bx.Y(GAUSS_OUT[c]), r=3.4, fill=SER2)
    # end labels beyond c4, and a leader for the dip
    ex = bx.X(4) + 12
    s += mono(ex, bx.Y(IDEAL[4]) + 3, "187.8", size=8, fill=ACCENT, anchor="start")
    s += mono(ex, bx.Y(GAUSS_OUT[4]) + 3, "161.8", size=8, fill=SER2, anchor="start")
    s += mono(ex, bx.Y(200) - 7, "200", size=8, fill=SOFT, anchor="start")
    s += mono(bx.X(0) - 6, bx.Y(GAUSS_OUT[0]) - 8, "78.2", size=8, fill=SER2, anchor="end")
    s += mono(bx.X(0) - 6, bx.Y(IDEAL[0]) + 13, "72.0", size=8, fill=ACCENT, anchor="end")
    lx, ly = bx.X(2.05), bx.Y(12)
    s += (f'<line x1="{bx.X(1) + 5:.1f}" y1="{bx.Y(IDEAL[1]) - 1:.1f}" x2="{lx - 4:.1f}" y2="{ly - 3:.1f}" '
          f'stroke="{ACCENT}" stroke-width="0.9"/>')
    s += mono(lx, ly, "0.45: 39.6 below the flat 40", size=8, fill=ACCENT, anchor="start")
    s += legend2(vh - 58, vw, [("ideal low-pass", ACCENT, "line", 1), ("shared Gaussian", SER2, "line", 1),
                               ("input row", SOFT, "dash", 1)])
    s += mono(32, vh - 16, "evaluated from the closed forms at the row's five frequencies; outputs are circular, as the DFT computes them",
              size=8, fill=SOFT, anchor="start")
    return emit("09", "ideal-vs-gaussian", "Choose the shape for its kernel",
                "A brick-wall gain rings beside the edge; the Gaussian's gain falls smoothly and its output stays in range.",
                "filter design", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 452
    s = eyebrow(32, 40, "one column of the 10 × 10 spectrum, kc = 0: the tile's own bins and the interference's, log scale")
    tile_col = [abs(FT[k][0]) for k in range(10)]
    on2 = [10 * abs(z) for z in N_ON]       # bands constant along rows: 2-D = 10 x the column's 1-D
    off2 = [10 * abs(z) for z in N_OFF]
    assert round(on2[3], 6) == 1000 and round(off2[2], 1) == 647.2 and round(off2[1], 1) == 247.2
    order = shift_order(10)
    fl = [freq(k, 10) for k in order]
    panels = [("3 cycles in 10 rows: two bins", on2, 76), ("2.5 cycles in 10 rows: every bin", off2, 556)]
    for title, N, x0 in panels:
        ax = Axes(x0, 96, 400, 236, (-5.6, 4.6), (50, 30000), logy=True)
        s += eyebrow(x0, 80, title, fill=INK)
        s += ax.frame(fl, [100, 1000, 10000], xlab="kr", ylab=" ",
                      xfmt=lambda v: fmt(v, 0) if v <= 0 else f"+{v}",
                      yfmt=lambda v: {100: "100", 1000: "1,000", 10000: "10,000"}[v])
        for f, k in zip(fl, order):
            if tile_col[k] > 1e-6:
                y = ax.Y(tile_col[k])
                s += (f'<rect x="{ax.X(f) - 14:.1f}" y="{y:.1f}" width="14" height="{ax.Y(50) - y:.1f}" '
                      f'fill="{SOFT}" fill-opacity="0.55"/>')
                s += mono(ax.X(f) - 1, y - 5, fmt(round(tile_col[k]), 0), size=7, fill=MUTED, anchor="end")
            m = N[k]
            if m > 1e-6:
                y = ax.Y(m)
                s += (f'<rect x="{ax.X(f) + 1:.1f}" y="{y:.1f}" width="12" height="{ax.Y(50) - y:.1f}" '
                      f'fill="{ACCENT}" fill-opacity="0.85"/>')
                lab = fmt(round(m), 0) if abs(m - round(m)) < 1e-6 else fmt(m, 1)
                s += mono(ax.X(f) + 1, y - 5, lab, size=7, fill=ACCENT, anchor="start")
    s += note_lines(76, 372, [("both spikes land where the tile is empty (odd kr):", INK),
                              ("a two-bin notch removes them exactly", ACCENT)], size=9)
    s += note_lines(556, 372, [("84% of the energy in ±2 and ±3; the rest leaks everywhere", INK),
                               ("at ±2 the leak, 647.2, meets the tile's 860", ACCENT)], size=9)
    s += legend2(vh - 30, vw, [("the tile's own magnitude", SOFT, "box", 0.55),
                               ("the interference's", ACCENT, "box", 0.85)])
    return emit("10", "leakage-on-and-off-bin", "Why notches need the right frequency",
                "On-bin interference fills two bins; off-bin interference leaks into every bin, including the image's.",
                "notch filtering", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "operations per output pixel on a 1920 × 1080 frame: a flop-count model, not a timing")
    ax = Axes(90, 86, 820, 290, (1, 52), (8, 8000), logy=True)
    s += ax.frame([3, 7, 10, 12, 15, 21, 31, 41, 44, 51], [10, 30, 100, 300, 1000, 3000],
                  xlab="kernel width m (an m × m kernel, or m taps per pass)", ylab="operations per pixel, log scale",
                  xfmt=str, yfmt=lambda v: f"{v:,}")
    ms = list(range(2, 53))
    s += polyline([(ax.X(m), ax.Y(2 * m * m)) for m in ms if 2 * m * m <= 8000], INK, sw=1.8)
    s += polyline([(ax.X(m), ax.Y(4 * m)) for m in ms], SER2, sw=1.8)
    s += polyline([(ax.X(m), ax.Y(fft_route(1920, 1080, m))) for m in ms], ACCENT, sw=2.2)
    s += polyline([(ax.X(m), ax.Y(fft_route(1920, 1080, m, n_fft=2))) for m in ms], ACCENT, sw=1.4, dash="4,3")
    for m, col, lab, yy, anchor, dx in ((7, SOFT, "textbook: 7", 5200, "end", -6),
                                        (11.4, SER3, "OpenCV filter2D switches: area ≥ 130", 5200, "start", 6)):
        x = ax.X(m)
        s += (f'<line x1="{x:.1f}" y1="{ax.Y(8000):.1f}" x2="{x:.1f}" y2="{ax.Y(8):.1f}" stroke="{col}" '
              f'stroke-width="1.2" stroke-dasharray="3,3"/>')
        s += mono(x + dx, ax.Y(yy), lab, size=8, fill=col, anchor=anchor)
    c_full = next(m for m in ms if 2 * m * m > fft_route(1920, 1080, m))
    c_sep = next(m for m in ms if 4 * m > fft_route(1920, 1080, m))
    assert (c_full, c_sep) == (10, 44)
    s += dot(ax.X(c_full), ax.Y(2 * c_full * c_full), r=4.4, fill=ACCENT, stroke="#ffffff")
    s += mono(ax.X(12.3), ax.Y(232), f"full kernel crosses at {c_full}", size=8, fill=INK, anchor="start")
    s += dot(ax.X(c_sep), ax.Y(4 * c_sep), r=4.4, fill=ACCENT, stroke="#ffffff")
    s += mono(ax.X(c_sep) + 2, ax.Y(255), f"separable crosses at {c_sep}", size=8, fill=SER2, anchor="end")
    s += legend2(vh - 34, vw, [("direct, full kernel: 2m²", INK, "line", 1), ("separable: 4m", SER2, "line", 1),
                               ("FFT round trip", ACCENT, "line", 1), ("kernel's FFT cached", ACCENT, "dash", 1)])
    s += mono(32, vh - 10, "FFT: 2.5·PQ·log2(PQ) per real transform (FFTW's convention), padded to the next 2·3·5-smooth size ≥ 1920 + m − 1 by 1080 + m − 1",
              size=7.5, fill=SOFT, anchor="start")
    return emit("11", "cost-model", "When is the FFT round trip cheaper?",
                "A model, not a timing: the FFT route is nearly flat in kernel width; the direct sum's parabola crosses it near 10.",
                "the crossover", vw, vh, s)
# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 492
    s = eyebrow(32, 40, "a and its circular shift by (1, 2): correlate, then normalise every coefficient to unit magnitude")
    cs, gy = 58, 110
    L, R = 70, 600
    s += eyebrow(L, 84, "plain cross-correlation ÷ 1,000")
    s += eyebrow(R, 84, "phase correlation")
    xc = [[v / 1000 for v in row] for row in XC]
    s += value_grid(L, gy, cs, xc, nd=1, size=9, lo=200, hi=490)
    s += value_grid(R, gy, cs, PC, nd=3, size=9, lo=0, hi=1)
    for gx in (L, R):
        s += axis_labels(gx, gy, cs, 5, [f"dr {r}" for r in range(5)], [f"dc {c}" for c in range(5)])
        s += outline(gx + 3 * cs, gy + 4 * cs, cs, cs)
    s += outline(L + 3 * cs - 3, gy - 3, cs + 6, 5 * cs + 6, stroke=LINK, sw=1.6, dash="5,3")
    s += hline(L + 5 * cs + 24, R - 46, gy + 2.5 * cs, stroke=MUTED, sw=1.2)
    s += mono((L + 5 * cs + 24 + R - 46) / 2, gy + 2.5 * cs - 10, "divide by |F_A F_C*|", size=8, fill=MUTED)
    ny = gy + 5 * cs + 30
    s += note_lines(L, ny, [("peak 487,425 at (4, 3); 441,200 at four more in column 3", INK),
                            ("the peak stands 10.5% above a ridge: the step is", LINK),
                            ("constant down the rows, so only the impulse breaks the tie", LINK)])
    s += note_lines(R, ny, [("exactly 1 at (4, 3) ≡ (−1, −2), 0 elsewhere", ACCENT),
                            ("the shift, with the sign set by which spectrum", INK),
                            ("is conjugated; needs every |F| > 0 (here ≥ 215)", INK)])
    return emit("12", "phase-correlation", "Where position is the answer",
                "Normalising every coefficient to unit magnitude turns a correlation ridge into one peak.",
                "phase correlation", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 610
    s = eyebrow(32, 40, "which call does what, how it scales, when it switches, and the trap — mapped from docs and source, not run")
    cols = [("call", 32), ("scaling and layout", 336), ("size or switch rule", 580), ("trap", 780)]
    y0 = 74
    for h, x in cols:
        s += mono(x, y0, h, size=8, fill=SOFT, anchor="start", track="0.08em")
    s += f'<line x1="32" y1="{y0 + 10}" x2="{vw - 32}" y2="{y0 + 10}" stroke="{RULE_SOLID}"/>'
    rows = [
        ("NumPy", "np.fft.fft2(img)", "unscaled forward; inverse ÷ MN", "any size", "match scaling before comparing"),
        ("NumPy", "np.fft.rfft2(img)", "N/2 + 1 columns (even N)", "—", "the other half is conjugate"),
        ("NumPy", "np.fft.fftshift / ifftshift", "roll by n//2 / −(n//2)", "—", "not inverses on odd n"),
        ("OpenCV", "cv2.dft(img, flags=DFT_COMPLEX_OUTPUT)", "full complex array", "—", "without the flag: CCS-packed"),
        ("OpenCV", "cv2.idft(F, flags=DFT_SCALE|DFT_REAL_OUTPUT)", "DFT_SCALE divides by MN", "—", "omit it and get × MN"),
        ("OpenCV", "cv2.getOptimalDFTSize(n)", "—", "next 2^p 3^q 5^r", "zero padding adds a jump"),
        ("OpenCV", "cv2.filter2D(img, -1, k)", "correlation; caller's border", "DFT at area ≥ 130 or ≥ 50", "11 × 11 (121) stays direct"),
        ("OpenCV", "cv2.phaseCorrelate(a, b, window)", "R = Ga Gb* / |Ga Gb*|", "pads to optimal size", "sign set by argument order"),
        ("SciPy", "signal.fftconvolve(a, k)", "float output", "always the FFT", "slow when few outputs needed"),
        ("SciPy", "signal.convolve(a, k, method='auto')", "fitted constants", "2-D: FFT from 3 × 3", "direct if int sums pass 2^52"),
        ("SciPy", "fft.next_fast_len(n)", "—", "next fast length", "may change by version"),
        ("scikit-image", "registration.phase_cross_correlation", "normalization='phase'", "—", "illumination yes, noise no"),
    ]
    libcol = {"NumPy": SER4, "OpenCV": SER2, "SciPy": SER3, "scikit-image": SER1}
    for k, (lib, call, scal, rule, trap) in enumerate(rows):
        y = y0 + 34 + k * 40
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 18}" width="{vw - 56}" height="40" fill="rgba(45,49,66,0.03)"/>'
        s += mono(32, y - 4, lib, size=7, fill=libcol[lib], anchor="start", track="0.12em", weight="600")
        s += mono(32, y + 10, call, size=8.5, fill=INK, anchor="start", weight="500")
        s += mono(336, y + 4, scal, size=8.5, fill=MUTED, anchor="start")
        s += mono(580, y + 4, rule, size=8.5, fill=ACCENT if "area" in rule or "3 × 3" in rule else INK, anchor="start",
                  weight="600" if "area" in rule or "3 × 3" in rule else "400")
        s += mono(780, y + 4, trap, size=8.5, fill=INK, anchor="start")
    s += mono(32, vh - 16, "OpenCV's 130 applies with SSE3 for 8-bit to 8-bit or 16-bit and float to float filtering; 50 otherwise",
              size=8, fill=SOFT, anchor="start")
    return emit("13", "tooling-map", "The tooling map",
                "Scaling, layout, switch rules and traps for the 2-D DFT in four libraries. None of it was executed.",
                "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10, "11": fig11, "12": fig12, "13": fig13}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
