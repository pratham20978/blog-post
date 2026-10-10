#!/usr/bin/env python3
"""Figures 01-11 for wavelets-and-multiresolution.

Every value drawn here is computed in this file, from the definitions, on the series'
5x5 patch, its rows and its transpose: Haar and 5/3 lifting (JPEG 2000 rounding and
whole-sample mirror), one orthonormal 2-D Haar level with PyWavelets' default half-sample
padding, coefficient counts from each library's size rule, closed-form frequency responses
of the published filter taps, and the threshold rules. Nothing is measured and nothing
loads an image. Run:  python3 _figs.py [01 05 ...]
"""
import cmath
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID,
                    SANS, SOFT, elbow_hvh, emit, eyebrow, hline, masked, mono, txt, vline)

PI = math.pi
SER1, SER2, SER3, SER4 = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50"

# ------------------------------------------------------------------ the data
PATCH = [[40, 40, 40, 200, 200] for _ in range(5)]
PATCH[2][1] = 255
ROW0 = PATCH[0][:]
ROW2 = PATCH[2][:]


def wse(i, n):
    """JPEG 2000's whole-sample symmetric extension: mirror about the end sample."""
    if n == 1:
        return 0
    p = 2 * (n - 1)
    m = i % p
    return min(m, p - m)


def haar_lift(x):
    """d = odd - even, s = even + d/2; an unpaired last sample passes through."""
    d = [x[2 * k + 1] - x[2 * k] for k in range(len(x) // 2)]
    s = [x[2 * k] + (d[k] / 2 if k < len(d) else 0) for k in range((len(x) + 1) // 2)]
    return s, d


def lift53(x, integer=True):
    n = len(x)

    def X(i):
        return x[wse(i, n)]

    def D(i):
        return X(i) - ((X(i - 1) + X(i + 1)) // 2 if integer else (X(i - 1) + X(i + 1)) / 2)

    d = [D(2 * k + 1) for k in range(n // 2)]
    s, upd = [], []
    for k in range((n + 1) // 2):
        i = 2 * k
        dl, dr = D(wse(i - 1, n)), D(wse(i + 1, n))
        u = (dl + dr + 2) // 4 if integer else (dl + dr) / 4
        upd.append(u)
        s.append(x[i] + u)
    return s, d, upd


def inv53(s, d, offset=2):
    n = len(s) + len(d)
    x = [0] * n

    def dat(j):
        return d[(wse(j, n) - 1) // 2]

    for k in range(len(s)):
        i = 2 * k
        x[i] = s[k] - (dat(i - 1) + dat(i + 1) + offset) // 4
    for k in range(len(d)):
        i = 2 * k + 1
        x[i] = d[k] + (x[wse(i - 1, n)] + x[wse(i + 1, n)]) // 2
    return x


def pad_half(M):
    """PyWavelets' default 'symmetric' mode for Haar on odd sizes: repeat the last row/col."""
    M = [r + [r[-1]] if len(r) % 2 else r[:] for r in M]
    return M + [M[-1][:]] if len(M) % 2 else M


def haar2(M):
    """Orthonormal 2-D Haar on 2x2 blocks: (LL, HL, LH, HH) = sum and signed differences / 2.
    HL = left - right (PyWavelets cV), LH = top - bottom (cH), HH = cD."""
    out = []
    for i in range(0, len(M), 2):
        row = []
        for j in range(0, len(M[0]), 2):
            p, q, r, s = M[i][j], M[i][j + 1], M[i + 1][j], M[i + 1][j + 1]
            row.append(((p + q + r + s) / 2, (p - q + r - s) / 2, (p + q - r - s) / 2,
                        (p - q - r + s) / 2))
        out.append(row)
    return out


def ihaar2(C):
    M = [[0.0] * (2 * len(C[0])) for _ in range(2 * len(C))]
    for i, row in enumerate(C):
        for j, (A, HL, LH, HH) in enumerate(row):
            M[2 * i][2 * j] = (A + HL + LH + HH) / 2
            M[2 * i][2 * j + 1] = (A - HL + LH - HH) / 2
            M[2 * i + 1][2 * j] = (A + HL - LH - HH) / 2
            M[2 * i + 1][2 * j + 1] = (A - HL - LH + HH) / 2
    return M


def thr(v, lam, mode):
    if mode == "hard":
        return v if abs(v) >= lam else 0.0
    return math.copysign(max(abs(v) - lam, 0.0), v)


def threshold_patch(lam, mode):
    C = haar2(pad_half(PATCH))
    T = [[(A, thr(a, lam, mode), thr(b, lam, mode), thr(c, lam, mode)) for (A, a, b, c) in row]
         for row in C]
    return [r[:5] for r in ihaar2(T)[:5]]


H0 = haar_lift(ROW0)
L0 = lift53(ROW0)
L2 = lift53(ROW2)
L2R = lift53(ROW2, integer=False)
C2D = haar2(pad_half(PATCH))
LL = [[c[0] for c in r] for r in C2D]
HL = [[c[1] for c in r] for r in C2D]
LH = [[c[2] for c in r] for r in C2D]
HH = [[c[3] for c in r] for r in C2D]
SHIFTS = [("step at c2 | c3 (r0)", [40, 40, 40, 200, 200]),
          ("step moved left", [40, 40, 200, 200, 200]),
          ("step moved right", [40, 40, 40, 40, 200]),
          ("impulse at odd c1", [40, 255, 40, 40, 40]),
          ("impulse at even c2", [40, 40, 255, 40, 40])]


def pywt_len(n, L):
    return (n + L - 1) // 2


def count_multilevel(w, h, L, levels):
    total = 0
    for _ in range(levels):
        w, h = pywt_len(w, L), pywt_len(h, L)
        total += 3 * w * h
    return total + w * h


def pyramid_count(w, h, levels):
    t = 0
    for _ in range(levels):
        t += w * h
        w, h = -(-w // 2), -(-h // 2)
    return t + w * h


FRAME = 1920 * 1080
BUDGET = [  # (label, colour, row of 5, patch 5x5, 1920x1080 at five levels) as coefficients per pixel
    ("lifting (JPEG 2000)", ACCENT, 5 / 5, 25 / 25, 1.0),
    ("PyWavelets haar", SER2, 2 * pywt_len(5, 2) / 5, 4 * pywt_len(5, 2) ** 2 / 25,
     count_multilevel(1920, 1080, 2, 5) / FRAME),
    ("PyWavelets bior2.2", SER2, 2 * pywt_len(5, 6) / 5, 4 * pywt_len(5, 6) ** 2 / 25,
     count_multilevel(1920, 1080, 6, 5) / FRAME),
    ("PyWavelets bior4.4", SER2, 2 * pywt_len(5, 10) / 5, 4 * pywt_len(5, 10) ** 2 / 25,
     count_multilevel(1920, 1080, 10, 5) / FRAME),
    ("Laplacian pyramid", SER3, 11 / 5, 39 / 25, pyramid_count(1920, 1080, 5) / FRAME),
]

HAAR_LO = {0: 0.5, 1: 0.5}
HAAR_HI = {0: -1.0, 1: 1.0}
L53_LO = {-2: -1 / 8, -1: 2 / 8, 0: 6 / 8, 1: 2 / 8, 2: -1 / 8}
L53_HI = {-1: -0.5, 0: 1.0, 1: -0.5}
S97_LO = [0.6029490182363579, 0.2668641184428723, -0.07822326652898785, -0.01686411844287495,
          0.02674875741080976]
S97_HI = [1.115087052456994, -0.5912717631142470, -0.05754352622849957, 0.09127176311424948]
L97_LO = {k * sg: S97_LO[k] for k in range(5) for sg in (1, -1)}
L97_HI = {k * sg: S97_HI[k] for k in range(4) for sg in (1, -1)}


def resp(taps, w):
    return abs(sum(c * cmath.exp(-1j * w * n) for n, c in taps.items()))


# the article's numbers; a figure that disagrees with the text fails here
assert H0 == ([40.0, 120.0, 200], [0, 160])
assert L0[0] == [40, 60, 240] and L0[1] == [0, 80] and inv53(L0[0], L0[1]) == ROW0
assert L2[0] == [148, 114, 240] and L2[1] == [215, 80] and L2[2] == [108, 74, 40]
assert L2R[0] == [147.5, 113.75, 240.0] and inv53(L2[0], L2[1]) == ROW2
assert inv53(L2[0], L2[1], offset=0) == [41, 256, 41, 200, 200]
assert LL == [[80, 240, 400], [187.5, 240, 400], [80, 240, 400]]
assert [r[1] for r in HL] == [-160, -160, -160] and HL[1][0] == -107.5
assert LH[1][0] == 107.5 and HH[1][0] == -107.5
assert sum(v != 0 for r in LH for v in r) == 1 and sum(v != 0 for r in HH for v in r) == 1
assert 4 * 107.5 ** 2 == 215 ** 2 == 46225
assert [haar_lift(x)[1] for _, x in SHIFTS] == [[0, 160], [0, 0], [0, 0], [215, 0], [0, -215]]
assert [lift53(x, False)[1] for _, x in SHIFTS] == [[0, 80], [-80, 0], [0, -80], [215, 0],
                                                       [-107.5, -107.5]]
assert [round(b[4], 4) for b in BUDGET] == [1.0, 1.0001, 1.0118, 1.0229, 1.333]
assert [round(b[2] * 5) for b in BUDGET[1:4]] == [6, 10, 14]
assert [round(b[3] * 25) for b in BUDGET[1:4]] == [36, 100, 196]
assert round(resp(HAAR_LO, PI / 2), 3) == 0.707 and round(resp(L53_LO, PI / 3), 3) == 1.125
assert round(resp(L97_LO, PI / 2), 3) == 0.813 and round(resp(L97_LO, 2 * PI / 3), 3) == 0.354
assert round(resp(L53_LO, 2 * PI / 3), 3) == 0.625 and round(resp(L97_LO, PI / 3), 3) == 0.955
assert threshold_patch(50, "soft")[2] == [65, 180, 65, 175, 200]
assert threshold_patch(50, "soft")[3] == [65, 65, 65, 175, 200]
assert threshold_patch(50, "hard") == [[float(v) for v in r] for r in PATCH]
assert threshold_patch(120, "hard")[2][:2] == [93.75, 93.75]
assert threshold_patch(120, "soft")[0] == [40, 40, 100, 140, 200]
assert round(math.sqrt(2 * math.log(512 * 512)), 3) == 4.995


# ------------------------------------------------------------------ drawing helpers
def fmt(v, nd=2):
    if abs(v - round(v)) < 1e-9:
        s = f"{round(v):,}" if abs(v) >= 10000 else str(int(round(v)))
    else:
        s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return s.replace("-", "−")


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


def vcell(x, y, w, h, v, hi=255.0, size=10, label=None, dash=None):
    """A value cell shaded by value / hi, high = bright."""
    t = v / hi
    s = shade_rect(x, y, w, h, t, dash=dash)
    return s + txt(x + w / 2, y + h / 2 + size * 0.36, label if label is not None else fmt(v),
                   size=size, fill=ink_for(t), family=MONO, weight="500")


def dcell(x, y, w, h, v, size=10, stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, fill="#ffffff"):
    """A detail cell: white, the signed value printed."""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>'
            + txt(x + w / 2, y + h / 2 + size * 0.36, fmt(v), size=size, fill=INK, family=MONO,
                  weight="500"))


def outline(x, y, w, h, stroke=ACCENT, sw=2, dash=None, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def polyline(pts, stroke, sw=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}/>')


def dot(x, y, r=3.4, fill=INK):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'


def node(cx, cy, sym, colour=INK):
    return (f'<circle cx="{cx}" cy="{cy}" r="11" fill="#ffffff" stroke="{colour}" stroke-width="1.2"/>'
            + txt(cx, cy + 4.5, sym, size=13, fill=colour, family=MONO, weight="600"))


def note_lines(x, y, items, size=9, gap=15, anchor="start"):
    s = ""
    for k, (text, colour) in enumerate(items):
        s += mono(x, y + k * gap, text, size=size, fill=colour, anchor=anchor)
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


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str):
        s = (f'<line x1="{self.x0}" y1="{self.y0 + self.h}" x2="{self.x0 + self.w}" '
             f'y2="{self.y0 + self.h}" stroke="{RULE_SOLID}" stroke-width="1"/>')
        s += (f'<line x1="{self.x0}" y1="{self.y0}" x2="{self.x0}" y2="{self.y0 + self.h}" '
              f'stroke="{RULE_SOLID}" stroke-width="1"/>')
        for v in yt:
            yy = self.Y(v)
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


def row_cells(x, y, cs, vals, size=10, hi=255.0):
    return "".join(vcell(x + k * cs, y, cs, cs, v, hi=hi, size=size) for k, v in enumerate(vals))


# ------------------------------------------------------------------ FIG 01
def lane(y0, title, x, evens, odds, d, s, plabel, pvals, ulabel, uvals, notes, cost_colour):
    """One lifting ladder: input row, split into an even and an odd channel, predict on the odd
    channel from the evens, update on the even channel from the details."""
    cs = 40
    ye, yo = y0, y0 + 110
    me, mo = ye + cs / 2, yo + cs / 2
    out = eyebrow(32, y0 - 30, title)
    ym = (me + mo) / 2
    out += mono(48 + 2.5 * cs, ym - 30, "row r0" if x == ROW0 else "row r2", size=8, fill=SOFT)
    out += row_cells(48, ym - cs / 2, cs, x)
    out += elbow_hvh(252, ym, 272, me, 296)
    out += elbow_hvh(252, ym, 272, mo, 296)
    out += mono(300, ye - 8, "evens c0 c2 c4", size=8, fill=SOFT, anchor="start")
    out += mono(300, yo - 8, "odds c1 c3", size=8, fill=SOFT, anchor="start")
    out += row_cells(300, ye, cs, evens)
    out += row_cells(300, yo, cs, odds)
    # channel lines and the two lifting nodes
    out += hline(424, 688, me, marker=None)
    out += hline(712, 756, me)
    out += hline(384, 500, mo, marker=None)
    out += hline(524, 756, mo)
    out += node(700, me, "+", INK)
    out += node(512, mo, "−", INK)
    out += vline(512, me, mo - 12, stroke=MUTED)
    out += f'<circle cx="512" cy="{me}" r="2.6" fill="{MUTED}"/>'
    out += vline(700, mo, me + 12, stroke=MUTED)
    out += f'<circle cx="700" cy="{mo}" r="2.6" fill="{MUTED}"/>'
    out += mono(520, ym - 4, plabel, size=9, fill=INK, anchor="start", weight="500")
    out += mono(520, ym + 11, pvals, size=8.5, fill=SOFT, anchor="start")
    out += mono(708, ym - 4, ulabel, size=9, fill=INK, anchor="start", weight="500")
    out += mono(708, ym + 11, uvals, size=8.5, fill=SOFT, anchor="start")
    # outputs
    out += row_cells(760, ye, cs, s)
    for k, v in enumerate(d):
        out += dcell(760 + k * cs, yo, cs, cs, v,
                     stroke=cost_colour if v else "rgba(45,49,66,0.30)", sw=2 if v else 0.8)
    out += mono(886, me + 4, "s · coarse", size=8.5, fill=MUTED, anchor="start")
    out += mono(846, mo + 4, "d · detail", size=8.5, fill=MUTED, anchor="start")
    out += note_lines(300, yo + cs + 26, notes, size=8.5, gap=14)
    return out


def fig01():
    vw, vh = 1016, 600
    s = eyebrow(32, 40, "one level of row r0 by lifting: split into evens and odds, predict the odds, update the evens")
    s += lane(122, "haar · predict each odd sample from its left neighbour", ROW0, [40, 40, 200], [40, 200],
              H0[1], H0[0], "P = left even", "predictions 40, 40", "U = d / 2", "+0, +80, +0 (c4 passes)",
              [("the flat pair costs 0; the pair across the step costs the whole step, 160", INK),
               ("c4 has no partner: s2 = 200, as if paired with its own copy", SOFT)], ACCENT)
    s += lane(376, "5/3 · predict from both neighbours, round down, mirror at the ends", ROW0, [40, 40, 200],
              [40, 200], L0[1], L0[0], "P = ⌊(left + right) / 2⌋", "predictions 40, 120",
              "U = ⌊(dL + dR + 2) / 4⌋", "+0, +20, +40",
              [("a step costs half its height, 80; a straight line would cost 0", INK),
               ("ends mirror the details: d₋₁ = d₀ = 0 and d₂ = d₁ = 80", SOFT),
               ("240 = (−40 + 400 + 1,200 + 400 − 40) / 8 on the mirrored 40 200 [200] 200 40", ACCENT)],
              ACCENT)
    return emit("01", "lifting-the-top-row", "One level of the top row, two ways",
                "Haar and the 5/3 by lifting on row r0: split, predict, update. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 400
    s = eyebrow(32, 40, "coefficients kept per pixel: lifting keeps one; padding and redundancy add the rest")
    panels = [("a row of 5 samples", 2), ("the 5×5 patch", 3), ("1920×1080, five levels", 4)]
    px0 = [214, 476, 738]
    pw, xmax = 220, 8.0
    y0, gap, bh = 104, 42, 20
    for k, (lab, colour, *_rest) in enumerate(BUDGET):
        y = y0 + k * gap
        s += mono(32, y + 14, lab, size=9, fill=INK, anchor="start", weight="500")
    for (title, idx), x0 in zip(panels, px0):
        s += eyebrow(x0, 82, title)
        base = y0 + len(BUDGET) * gap + 4
        for t in range(0, 9, 2):
            xx = x0 + t / xmax * pw
            s += (f'<line x1="{xx:.1f}" y1="{y0 - 8}" x2="{xx:.1f}" y2="{base}" stroke="{RULE}" '
                  f'stroke-width="0.8"/>')
            s += mono(xx, base + 14, str(t), size=8, fill=SOFT)
        s += (f'<line x1="{x0}" y1="{y0 - 8}" x2="{x0}" y2="{base}" stroke="{RULE_SOLID}" stroke-width="1"/>')
        for k, row in enumerate(BUDGET):
            v, colour = row[idx], row[1]
            y = y0 + k * gap
            w = v / xmax * pw
            s += (f'<rect x="{x0}" y="{y}" width="{w:.1f}" height="{bh}" fill="{colour}" '
                  f'fill-opacity="0.85"/>')
            if idx == 4:
                lab = "1" if v == 1.0 else f"{v:.4f}".rstrip("0") if v < 1.1 else f"{v:.3f}"
            else:
                lab = fmt(v, 2)
            if w > 150:
                s += mono(x0 + w - 6, y + 14, lab, size=8.5, fill="#ffffff", anchor="end", weight="600")
            else:
                s += mono(x0 + w + 6, y + 14, lab, size=8.5, fill=INK, anchor="start", weight="500")
        s += mono(x0 + pw, base + 30, "coefficients per pixel", size=8, fill=SOFT, anchor="end")
    s += mono(32, vh - 30, "row: 5, 6, 10, 14 and 5 + 3 + 2 + 1 = 11 coefficients · patch: 25, 36, 100, 196 and 25 + 9 + 4 + 1 = 39",
              size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "PyWavelets in its default mode, ⌊(N + L − 1) / 2⌋ per band; the pyramid down to one sample, or five levels on the frame",
              size=8, fill=SOFT, anchor="start")
    return emit("02", "coefficient-budget", "The coefficient budget",
                "How many numbers each representation keeps per pixel. Counted from the size rules, not run.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 420
    s = eyebrow(32, 40, "eight samples, eight cells each: how position and frequency are shared out")
    size = 190
    xs = [56, 300, 544, 788]
    y0 = 118
    imp = 5  # the impulse at sample 5 (of 0..7)

    def cell(x0, a, b, f0, f1, hit):
        x = x0 + a / 8 * size
        w = (b - a) / 8 * size
        y = y0 + size - f1 / 0.5 * size
        h = (f1 - f0) / 0.5 * size
        fill = ACCENT_TINT if hit else "#ffffff"
        stroke = ACCENT if hit else "rgba(45,49,66,0.45)"
        return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
                f'stroke="{stroke}" stroke-width="{1.6 if hit else 0.8}"/>')

    tilings = []
    tilings.append([(k, k + 1, 0, 0.5) for k in range(8)])
    tilings.append([(0, 8, k / 16, (k + 1) / 16) for k in range(8)])
    tilings.append([(b * 4, b * 4 + 4, k / 8, (k + 1) / 8) for b in range(2) for k in range(4)])
    wav = [(2 * k, 2 * k + 2, 0.25, 0.5) for k in range(4)]
    wav += [(4 * k, 4 * k + 4, 0.125, 0.25) for k in range(2)]
    wav += [(0, 8, 1 / 16, 0.125), (0, 8, 0, 1 / 16)]
    tilings.append(wav)
    titles = ["pixels", "the dft", "blocks of 4 samples", "wavelets, three levels"]
    for x0, cells, title in zip(xs, tilings, titles):
        hits = 0
        s += eyebrow(x0, y0 - 16, title)
        for a, b, f0, f1 in cells:
            hit = a <= imp < b
            hits += hit
            s += cell(x0, a, b, f0, f1, hit)
        s += (f'<line x1="{x0}" y1="{y0 + size}" x2="{x0 + size}" y2="{y0 + size}" stroke="{RULE_SOLID}"/>')
        tx = x0 + (imp + 0.5) / 8 * size
        s += f'<polygon points="{tx - 4:.1f},{y0 + size + 11} {tx + 4:.1f},{y0 + size + 11} {tx:.1f},{y0 + size + 4}" fill="{ACCENT}"/>'
        s += mono(x0, y0 + size + 26, "position 0", size=8, fill=SOFT, anchor="start")
        s += mono(x0 + size, y0 + size + 26, "8 →", size=8, fill=SOFT, anchor="end")
        s += mono(x0 - 6, y0 + 8, "½", size=8, fill=SOFT, anchor="end")
        s += mono(x0 - 6, y0 + size, "0", size=8, fill=SOFT, anchor="end")
        s += mono(x0 - 6, y0 + size / 2 + 3, "f ↑", size=8, fill=SOFT, anchor="end")
        s += mono(x0, y0 + size + 46, f"{len(cells)} cells of equal area", size=9, fill=INK, anchor="start")
        s += mono(x0, y0 + size + 61, f"an impulse at sample 5 touches {hits}", size=9,
                  fill=ACCENT, anchor="start", weight="500")
    s += mono(32, vh - 16, "idealised cells: real filters overlap, so every cell leaks into its neighbours; ▲ marks the impulse's position",
              size=8, fill=SOFT, anchor="start")
    return emit("03", "position-frequency-tiling", "How each representation tiles position and frequency",
                "Pixels, the DFT, fixed blocks and wavelets for eight samples. An idealisation.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "one orthonormal haar level of the patch: four 3 × 3 subbands from the 6 × 6 padded patch")
    cs, px, py = 36, 64, 118
    P = pad_half(PATCH)
    s += eyebrow(px, py - 22, "the patch, padded")
    for r in range(6):
        for c in range(6):
            ghost = r == 5 or c == 5
            s += vcell(px + c * cs, py + r * cs, cs, cs, P[r][c], size=9.5,
                       dash="3,2" if ghost else None)
    for c, lab in enumerate(["c0", "c1", "c2", "c3", "c4", "c4′"]):
        s += mono(px + c * cs + cs / 2, py - 6, lab, size=8, fill=SOFT)
    for r, lab in enumerate(["r0", "r1", "r2", "r3", "r4", "r4′"]):
        s += mono(px - 8, py + r * cs + cs / 2 + 3, lab, size=8, fill=SOFT, anchor="end")
    s += outline(px, py + 2 * cs, 2 * cs, 2 * cs, stroke=ACCENT, sw=2.2)
    s += outline(px + 2 * cs + 3, py + 3, 2 * cs - 6, 6 * cs - 6, stroke=LINK, sw=1.6, dash="5,3")
    s += mono(px, py + 6 * cs + 22, "dashed: the mirrored row and column", size=8.5, fill=SOFT, anchor="start")
    s += mono(px, py + 6 * cs + 37, "PyWavelets' default pads to 6 × 6: 36 numbers", size=8.5, fill=SOFT, anchor="start")

    sc, gx, gy, gap = 44, 372, 118, 30
    blocks = [("LL · pywt cA", LL, gx, gy, True), ("HL · pywt cV", HL, gx + 3 * sc + gap, gy, False),
              ("LH · pywt cH", LH, gx, gy + 3 * sc + gap + 10, False),
              ("HH · pywt cD", HH, gx + 3 * sc + gap, gy + 3 * sc + gap + 10, False)]
    for title, M, x0, y0, is_ll in blocks:
        s += mono(x0, y0 - 8, title, size=8.5, fill=MUTED, anchor="start", weight="600")
        for i in range(3):
            for j in range(3):
                v = M[i][j]
                if is_ll:
                    s += vcell(x0 + j * sc, y0 + i * sc, sc, sc, v, hi=510.0, size=10)
                else:
                    s += dcell(x0 + j * sc, y0 + i * sc, sc, sc, v, size=10)
        s += outline(x0, y0 + sc, sc, sc, stroke=ACCENT, sw=2.2)
        if title.startswith("HL"):
            s += outline(x0 + sc + 3, y0 + 3, sc - 6, 3 * sc - 6, stroke=LINK, sw=1.6, dash="5,3")
    s += mono(gx, gy + 6 * sc + 2 * gap + 22, "block p q over r s:  LL = (p+q+r+s)/2 · HL = (p−q+r−s)/2", size=8.5, fill=MUTED, anchor="start")
    s += mono(gx, gy + 6 * sc + 2 * gap + 37, "LH = (p+q−r−s)/2 · HH = (p−q−r+s)/2", size=8.5, fill=MUTED, anchor="start")

    bx, bw = 716, 268
    s += eyebrow(bx, 118, "the impulse's energy, 215² = 46,225")
    y1 = 146
    s += mono(bx, y1, "Part 5's DFT: 25 bins × 4%", size=9, fill=INK, anchor="start", weight="500")
    for k in range(25):
        s += (f'<rect x="{bx + k * bw / 25:.1f}" y="{y1 + 8}" width="{bw / 25:.1f}" height="22" '
              f'fill="{MUTED}" fill-opacity="0.35" stroke="{PAPER}" stroke-width="1"/>')
    y2 = y1 + 64
    s += mono(bx, y2, "one Haar level: 4 coefficients × 25%", size=9, fill=ACCENT, anchor="start", weight="500")
    for k in range(4):
        s += (f'<rect x="{bx + k * bw / 4:.1f}" y="{y2 + 8}" width="{bw / 4:.1f}" height="22" '
              f'fill="{ACCENT}" fill-opacity="0.80" stroke="{PAPER}" stroke-width="1.5"/>')
        s += mono(bx + (k + 0.5) * bw / 4, y2 + 23, ["LL", "HL", "LH", "HH"][k] + " 107.5", size=8,
                  fill="#ffffff", weight="600")
    y3 = y2 + 70
    s += note_lines(bx, y3, [("4 × 107.5² = 46,225 = 215²", INK),
                             ("orange: the impulse, one coefficient per subband", ACCENT),
                             ("blue dashed: the step, three −160s in HL", LINK),
                             ("LL is shaded 0 to 510; details print their sign", SOFT)], size=8.5, gap=16)
    return emit("04", "one-haar-level-of-the-patch", "One Haar level of the patch",
                "The impulse lands in one coefficient per subband; the edge in one column of HL. Worked by hand.",
                "one level in 2-d", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 528
    s = eyebrow(32, 40, "three levels of a 1920 × 1080 frame, drawn to scale: the subbands hold exactly the pixel count")
    k = 0.36
    x0, y0 = 48, 100

    def sub(x, y, w, h, name, size, hl=False):
        W, H = w * k, h * k
        fill = ACCENT_TINT if hl else "#ffffff"
        out = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{W:.1f}" height="{H:.1f}" fill="{fill}" '
               f'stroke="rgba(45,49,66,0.45)" stroke-width="0.9"/>')
        cy = y + H / 2
        out += mono(x + W / 2, cy - 2, name, size=size, fill=INK, weight="600")
        out += mono(x + W / 2, cy + size + 2, f"{w}×{h}", size=size - 1, fill=SOFT)
        return out

    w3, h3, w2, h2, w1, h1 = 240, 135, 480, 270, 960, 540
    s += sub(x0, y0, w3, h3, "LL3", 8, True)
    s += sub(x0 + w3 * k, y0, w3, h3, "HL3", 8, True)
    s += sub(x0, y0 + h3 * k, w3, h3, "LH3", 8, True)
    s += sub(x0 + w3 * k, y0 + h3 * k, w3, h3, "HH3", 8, True)
    s += sub(x0 + w2 * k, y0, w2, h2, "HL2", 10)
    s += sub(x0, y0 + h2 * k, w2, h2, "LH2", 10)
    s += sub(x0 + w2 * k, y0 + h2 * k, w2, h2, "HH2", 10)
    s += sub(x0 + w1 * k, y0, w1, h1, "HL1", 12)
    s += sub(x0, y0 + h1 * k, w1, h1, "LH1", 12)
    s += sub(x0 + w1 * k, y0 + h1 * k, w1, h1, "HH1", 12)
    s += outline(x0, y0, w2 * k, h2 * k, stroke=ACCENT, sw=2.4)
    s += mono(x0, y0 + 1080 * k + 22, "orange: LL3 and the level-3 details, the 480×270 preview", size=8.5,
              fill=ACCENT, anchor="start")

    rx = 776
    s += eyebrow(rx, 112, "coefficients")
    rows = [("3 × 960×540", "1,555,200"), ("3 × 480×270", "388,800"), ("3 × 240×135", "97,200"),
            ("LL3 240×135", "32,400"), ("total", "2,073,600")]
    for i, (a, b) in enumerate(rows):
        y = 136 + i * 18
        col = INK if a != "total" else ACCENT
        s += mono(rx, y, a, size=9, fill=col, anchor="start", weight="600" if a == "total" else "400")
        s += mono(rx + 208, y, b, size=9, fill=col, anchor="end", weight="600" if a == "total" else "400")
    s += f'<line x1="{rx}" y1="{136 + 3 * 18 + 6}" x2="{rx + 208}" y2="{136 + 3 * 18 + 6}" stroke="{RULE_SOLID}"/>'
    s += eyebrow(rx, 262, "what a decoder can show")
    ladder = [("LL3 alone", "240×135", "1/64"), ("+ level 3", "480×270", "1/16"),
              ("+ level 2", "960×540", "1/4"), ("+ level 1", "1920×1080", "all")]
    for i, (a, b, c) in enumerate(ladder):
        y = 286 + i * 30
        s += mono(rx, y, a, size=9, fill=INK, anchor="start", weight="500")
        s += mono(rx + 100, y, b, size=9, fill=MUTED, anchor="start")
        s += mono(rx + 208, y, c, size=9, fill=ACCENT if c == "1/16" else SOFT, anchor="end")
    s += mono(rx, 420, "each level's three detail subbands", size=8.5, fill=SOFT, anchor="start")
    s += mono(rx, 434, "double the preview in each direction", size=8.5, fill=SOFT, anchor="start")
    return emit("05", "three-levels-of-a-frame", "Three levels of a 1920×1080 frame",
                "The dyadic layout JPEG 2000 Part 1 uses, to scale, with what each LL decodes to.",
                "one level in 2-d", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "magnitude responses from the published taps: low-pass gain 1 at dc, high-pass gain 2 at nyquist")
    curves = [("haar", HAAR_LO, HAAR_HI, SER4), ("5/3", L53_LO, L53_HI, LINK), ("9/7", L97_LO, L97_HI, SER1)]
    A = Axes(84, 104, 390, 270, (0, PI), (0, 1.2))
    B = Axes(580, 104, 390, 270, (0, PI), (0, 2.1))
    pifmt = {0: "0", PI / 4: "π/4", PI / 2: "π/2", 3 * PI / 4: "3π/4", PI: "π"}
    s += A.frame(list(pifmt), [0, 0.25, 0.5, 0.75, 1.0], xlab="ω, radians per sample",
                 ylab="low-pass |H(ω)|", xfmt=lambda v: pifmt[v], yfmt=lambda v: f"{v:g}")
    s += B.frame(list(pifmt), [0, 0.5, 1.0, 1.5, 2.0], xlab="ω, radians per sample",
                 ylab="high-pass |G(ω)|", xfmt=lambda v: pifmt[v], yfmt=lambda v: f"{v:g}")
    for ax in (A, B):
        xm = ax.X(PI / 2)
        s += (f'<line x1="{xm:.1f}" y1="{ax.y0}" x2="{xm:.1f}" y2="{ax.y0 + ax.h}" stroke="{SOFT}" '
              f'stroke-width="0.9" stroke-dasharray="3,3"/>')
    ws = [PI * i / 240 for i in range(241)]
    for name, lo, hi, col in curves:
        s += polyline([(A.X(w), A.Y(resp(lo, w))) for w in ws], col)
        s += polyline([(B.X(w), B.Y(resp(hi, w))) for w in ws], col)
    # values at the half-band point: dots on the curves, numbers in empty corners
    for name, lo, hi, col in curves:
        s += dot(A.X(PI / 2), A.Y(resp(lo, PI / 2)), fill=col)
        s += dot(B.X(PI / 2), B.Y(resp(hi, PI / 2)), fill=col)
    s += masked(A.X(PI / 3), A.Y(1.125) - 10, "1.125 at π/3", fill=LINK, size=8)
    lx, ly = A.x0 + 12, A.y0 + A.h - 74
    s += mono(lx, ly, "at π/2", size=8.5, fill=SOFT, anchor="start")
    for k, (lab, col) in enumerate((("haar 0.707", SER4), ("5/3 1.000", LINK), ("9/7 0.813", SER1))):
        s += mono(lx, ly + 15 * (k + 1), lab, size=9, fill=col, anchor="start", weight="600")
    rx, ry = B.x0 + B.w - 8, B.y0 + B.h - 98
    s += mono(rx, ry, "at π/2", size=8.5, fill=SOFT, anchor="end")
    for k, (lab, col) in enumerate((("haar 1.414", SER4), ("5/3 1.000", LINK), ("9/7 1.230", SER1))):
        s += mono(rx, ry + 15 * (k + 1), lab, size=9, fill=col, anchor="end", weight="600")
    s += mono(rx, ry + 72, "near 0: ω, ω², ω⁴", size=8.5, fill=INK, anchor="end")
    s += mono(rx, ry + 86, "at π/8: 0.390 · 0.076 · 0.011", size=8.5, fill=SOFT, anchor="end")
    s += mono(A.x0 + A.w - 8, A.y0 + 14, "dashed: the half-band point π/2", size=8.5, fill=SOFT, anchor="end")
    s += legend2(vh - 42, vw, [("haar", SER4, "line", 1), ("5/3 (LeGall)", LINK, "line", 1),
                               ("9/7 (CDF)", SER1, "line", 1)])
    return emit("06", "frequency-responses", "The same trade in frequency",
                "Haar, 5/3 and 9/7 analysis filters, evaluated from their published taps.",
                "which wavelet", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 584
    s = eyebrow(32, 40, "row r2 through the integer 5/3 and back: the inverse recomputes the same rounded numbers")
    cs = 40
    # forward lane
    y0 = 118
    ye, yo = y0, y0 + 110
    me, mo = ye + cs / 2, yo + cs / 2
    ym = (me + mo) / 2
    s += eyebrow(32, y0 - 30, "forward · predict, then update, rounding down")
    s += mono(48 + 2.5 * cs, ym - 30, "row r2", size=8, fill=SOFT)
    s += row_cells(48, ym - cs / 2, cs, ROW2)
    s += elbow_hvh(252, ym, 272, me, 296)
    s += elbow_hvh(252, ym, 272, mo, 296)
    s += row_cells(300, ye, cs, [40, 40, 200])
    s += row_cells(300, yo, cs, [255, 200])
    s += mono(300, ye - 8, "evens", size=8, fill=SOFT, anchor="start")
    s += mono(300, yo - 8, "odds", size=8, fill=SOFT, anchor="start")
    s += hline(424, 688, me, marker=None) + hline(712, 756, me)
    s += hline(384, 500, mo, marker=None) + hline(524, 756, mo)
    s += node(700, me, "+") + node(512, mo, "−")
    s += vline(512, me, mo - 12) + f'<circle cx="512" cy="{me}" r="2.6" fill="{MUTED}"/>'
    s += vline(700, mo, me + 12) + f'<circle cx="700" cy="{mo}" r="2.6" fill="{MUTED}"/>'
    s += mono(520, ym - 4, "P = ⌊(left + right) / 2⌋", size=9, fill=INK, anchor="start", weight="500")
    s += mono(520, ym + 11, "40, 120", size=8.5, fill=SOFT, anchor="start")
    s += mono(708, ym - 4, "U = ⌊(dL + dR + 2) / 4⌋", size=9, fill=INK, anchor="start", weight="500")
    s += mono(708, ym + 11, "+108, +74, +40", size=8.5, fill=ACCENT, anchor="start", weight="500")
    s += row_cells(760, ye, cs, L2[0])
    for k, v in enumerate(L2[1]):
        s += dcell(760 + k * cs, yo, cs, cs, v)
    s += mono(886, me + 4, "s · coarse", size=8.5, fill=MUTED, anchor="start")
    s += mono(846, mo + 4, "d · detail", size=8.5, fill=MUTED, anchor="start")
    s += mono(300, yo + cs + 24, "exact arithmetic would give 147.5, 113.75, 240: the update rounds 107.5 → 108 and 73.75 → 74",
              size=8.5, fill=SOFT, anchor="start")

    # inverse lane
    y1 = 380
    ye, yo = y1, y1 + 110
    me, mo = ye + cs / 2, yo + cs / 2
    ym = (me + mo) / 2
    s += f'<line x1="32" y1="{y1 - 52}" x2="{vw - 32}" y2="{y1 - 52}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y1 - 30, "inverse · undo the update, then the prediction, with the same rounding")
    s += row_cells(48, ye, cs, L2[0])
    for k, v in enumerate(L2[1]):
        s += dcell(48 + k * cs, yo, cs, cs, v)
    s += mono(48, ye - 8, "s", size=8, fill=SOFT, anchor="start")
    s += mono(48, yo - 8, "d", size=8, fill=SOFT, anchor="start")
    s += hline(172, 288, me, marker=None) + hline(312, 396, me)
    s += hline(132, 468, mo, marker=None) + hline(492, 596, mo)
    s += node(300, me, "−") + node(480, mo, "+")
    s += vline(300, mo, me + 12) + f'<circle cx="300" cy="{mo}" r="2.6" fill="{MUTED}"/>'
    s += row_cells(400, ye, cs, inv53(L2[0], L2[1])[0::2])
    s += hline(524, 576, me, marker=None)
    s += vline(576, me, mo - 22, stroke=MUTED, marker=None)
    s += f'<circle cx="576" cy="{me}" r="2.6" fill="{MUTED}"/>'
    s += f'<path d="M 576 {mo - 22} H 480 V {mo - 12}" fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += mono(312, ym - 4, "evens = s − U", size=9, fill=INK, anchor="start", weight="500")
    s += mono(312, ym + 11, "−108, −74, −40", size=8.5, fill=ACCENT, anchor="start", weight="500")
    s += mono(400, ye - 8, "evens restored", size=8, fill=SOFT, anchor="start")
    s += mono(588, ym + 4, "odds = d + P", size=9, fill=INK, anchor="start", weight="500")
    s += mono(588, ym + 19, "P = 40, 120 from the evens", size=8.5, fill=SOFT, anchor="start")
    s += row_cells(600, yo, cs, inv53(L2[0], L2[1])[1::2])
    s += mono(600, yo + cs + 16, "odds restored", size=8, fill=SOFT, anchor="start")
    s += elbow_hvh(524, me, 724, (me + mo) / 2 - 8, 756, r=6)
    s += elbow_hvh(684, mo, 724, (me + mo) / 2 + 8, 756, r=6)
    s += row_cells(760, (me + mo) / 2 - cs / 2, cs, inv53(L2[0], L2[1]))
    s += mono(760 + 2.5 * cs, (me + mo) / 2 - cs / 2 - 8, "row r2, exactly", size=8, fill=SOFT)
    return emit("07", "integer-lifting-forward-and-back", "Integer lifting, forward and back",
                "Row r2 through the reversible 5/3: rounding inside the steps, recomputed by the inverse. Worked by hand.",
                "lifting", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "move a feature one pixel: level-1 details of haar and the 5/3 on rows of the patch")
    cs, y0, rh = 34, 120, 62
    cx = 252
    hx, fx, ex = 470, 640, 812
    s += mono(cx, y0 - 22, "row (Haar pairs bracketed)", size=8, fill=SOFT, anchor="start")
    s += mono(hx, y0 - 22, "Haar d", size=8, fill=SOFT, anchor="start")
    s += mono(fx, y0 - 22, "5/3 d", size=8, fill=SOFT, anchor="start")
    s += mono(ex, y0 - 22, "detail energy: Haar · 5/3", size=8, fill=SOFT, anchor="start")
    for k, (label, row) in enumerate(SHIFTS):
        y = y0 + k * rh
        s += mono(32, y + cs / 2 + 4, label, size=9, fill=INK, anchor="start", weight="500")
        s += row_cells(cx, y, cs, row, size=9.5)
        for a, b in ((0, 2), (2, 4), (4, 5)):
            xa, xb = cx + a * cs + 3, cx + b * cs - 3
            s += (f'<path d="M {xa} {y + cs + 4} V {y + cs + 9} H {xb} V {y + cs + 4}" fill="none" '
                  f'stroke="{SOFT}" stroke-width="0.9"/>')
        hd = haar_lift(row)[1]
        fd = lift53(row, False)[1]
        lost = k in (1, 2)
        split = k == 4
        for j, v in enumerate(hd):
            s += dcell(hx + j * 52, y, 52, cs, v, size=10)
        if lost:
            s += outline(hx, y, 104, cs, stroke=ACCENT, sw=2)
        for j, v in enumerate(fd):
            s += dcell(fx + j * 52, y, 52, cs, v, size=10)
        if split:
            s += outline(fx, y, 104, cs, stroke=ACCENT, sw=2)
        eh = sum(v * v for v in hd)
        ef = sum(v * v for v in fd)
        s += mono(ex, y + cs / 2 + 4, f"{eh:,.0f}" if eh == int(eh) else f"{eh:,.1f}", size=9,
                  fill=ACCENT if lost else INK, anchor="start", weight="500")
        s += mono(ex + 70, y + cs / 2 + 4, "·", size=9, fill=SOFT, anchor="start")
        s += mono(ex + 86, y + cs / 2 + 4, f"{ef:,.1f}".replace(".0", "") if ef != int(ef) else f"{ef:,.0f}",
                  size=9, fill=ACCENT if split else INK, anchor="start", weight="500")
    s += mono(32, vh - 30, "orange: the failure. Haar loses the step at level 1 when it falls between pairs; the 5/3 halves the impulse at an even column",
              size=8.5, fill=ACCENT, anchor="start")
    s += mono(32, vh - 15, "5/3 shown without rounding; Haar d = odd − even, 5/3 d = odd − (left + right) / 2",
              size=8, fill=SOFT, anchor="start")
    return emit("08", "shift-variance", "What a one-pixel shift does",
                "Level-1 details of Haar and the 5/3 for a step and an impulse at two alignments. Worked by hand.",
                "shift variance", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 436
    s = eyebrow(32, 40, "coefficients per pixel in 2-d, and what the redundancy buys")
    rows = [("decimated wavelet", 1.0, "1", "a basis; shift-variant; HH mixes ±45°", ACCENT),
            ("Laplacian pyramid", 4 / 3, "4/3", "exact rebuild; no orientation", SER3),
            ("dual-tree complex", 4.0, "4", "nearly shift-invariant; six orientations", LINK),
            ("undecimated, J = 3", 10.0, "10", "no downsampling: 3J + 1 full-size bands", SER2),
            ("undecimated, J = 5", 16.0, "16", "", SER2)]
    x0, w, xmax = 300, 600, 16.0
    y0, gap = 96, 54
    base = y0 + len(rows) * gap
    for t in (0, 4, 8, 12, 16):
        xx = x0 + t / xmax * w
        s += f'<line x1="{xx:.1f}" y1="{y0 - 10}" x2="{xx:.1f}" y2="{base}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(xx, base + 14, str(t), size=8, fill=SOFT)
    s += f'<line x1="{x0}" y1="{y0 - 10}" x2="{x0}" y2="{base}" stroke="{RULE_SOLID}"/>'
    for k, (lab, v, vl, buys, col) in enumerate(rows):
        y = y0 + k * gap
        s += mono(32, y + 10, lab, size=9.5, fill=INK, anchor="start", weight="600")
        if buys:
            s += mono(32, y + 25, buys, size=8, fill=SOFT, anchor="start")
        s += f'<rect x="{x0}" y="{y}" width="{v / xmax * w:.1f}" height="22" fill="{col}" fill-opacity="0.85"/>'
        s += mono(x0 + v / xmax * w + 8, y + 15, vl, size=9.5, fill=INK, anchor="start", weight="600")
    s += mono(x0 + w, base + 30, "coefficients per pixel", size=8, fill=SOFT, anchor="end")
    s += mono(32, vh - 16, "published factors: dual tree 2ᵈ, undecimated J + 1 in 1-D; the 2-D 3J + 1 follows from the same count",
              size=8, fill=SOFT, anchor="start")
    return emit("09", "price-of-shift-invariance", "What shift invariance costs",
                "Redundancy of the remedies, in 2-D, beside the decimated transform and the pyramid.",
                "shift variance", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "hard and soft thresholding, and what each does to the noise-free patch")
    A = Axes(80, 110, 300, 300, (-200, 200), (-200, 200))
    s += A.frame([-200, -100, 0, 100, 200], [-200, -100, 0, 100, 200], xlab="coefficient w",
                 ylab="after thresholding, λ = 50", xfmt=lambda v: fmt(v), yfmt=lambda v: fmt(v))
    zx0, zx1 = A.X(-50), A.X(50)
    s += (f'<rect x="{zx0:.1f}" y="{A.y0}" width="{zx1 - zx0:.1f}" height="{A.h}" fill="{MUTED}" '
          f'fill-opacity="0.08"/>')
    s += polyline([(A.X(-200), A.Y(-200)), (A.X(200), A.Y(200))], SOFT, sw=1, dash="4,3")
    hard = [(A.X(-200), A.Y(-200)), (A.X(-50), A.Y(-50))]
    s += polyline(hard, LINK, sw=1.8)
    s += polyline([(A.X(-50), A.Y(0)), (A.X(50), A.Y(0))], LINK, sw=1.8)
    s += polyline([(A.X(50), A.Y(50)), (A.X(200), A.Y(200))], LINK, sw=1.8)
    s += polyline([(A.X(-200), A.Y(-150)), (A.X(-50), A.Y(0)), (A.X(50), A.Y(0)), (A.X(200), A.Y(150))],
                  ACCENT, sw=1.8)
    for w0 in (107.5, 160):
        s += dot(A.X(w0), A.Y(w0), fill=LINK)
        s += dot(A.X(w0), A.Y(w0 - 50), fill=ACCENT)
    s += masked(A.X(160) - 4, A.Y(160) - 10, "160 kept", fill=LINK, size=8, anchor="end")
    s += masked(A.X(160) + 4, A.Y(110) + 16, "→ 110", fill=ACCENT, size=8, anchor="start")
    s += mono(A.X(107.5) - 8, A.Y(107.5) - 10, "107.5", size=8, fill=LINK, anchor="end")
    s += masked(A.X(107.5) + 6, A.Y(57.5) + 16, "→ 57.5", fill=ACCENT, size=8, anchor="start")
    s += mono(A.x0 + 6, A.y0 + 14, "shaded: |w| < λ, zeroed by both", size=8, fill=SOFT, anchor="start")

    cs = 28
    cols = [(456, "λ = 50"), (636, "λ = 120")]
    rws = [(128, "soft", "soft"), (348, "hard", "hard")]
    notes = {("soft", 50): "edge 65 | 175 · impulse 180", ("hard", 50): "unchanged",
             ("soft", 120): "edge 100 | 140 · block 93.75", ("hard", 120): "edge kept · block 93.75"}
    for cxp, ctitle in cols:
        s += eyebrow(cxp, 104, ctitle)
    for ry, rtitle, mode in rws:
        s += mono(444, ry + 2.5 * cs + 4, rtitle, size=9.5, fill=ACCENT if mode == "soft" else LINK,
                  anchor="end", weight="600")
        for (cxp, ctitle), lam in zip(cols, (50, 120)):
            R = threshold_patch(lam, mode)
            for r in range(5):
                for c in range(5):
                    s += vcell(cxp + c * cs, ry + r * cs, cs, cs, R[r][c], size=7.2, label=fmt(R[r][c]))
            s += mono(cxp, ry + 5 * cs + 16, notes[(mode, lam)], size=8, fill=SOFT, anchor="start")
    ox = 832
    s += eyebrow(ox, 104, "the patch")
    for r in range(5):
        for c in range(5):
            s += vcell(ox + c * cs, 128 + r * cs, cs, cs, PATCH[r][c], size=7.2)
    s += mono(ox, 128 + 5 * cs + 16, "details 107.5 and 160", size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 42, vw, [("hard", LINK, "line", 1), ("soft", ACCENT, "line", 1),
                               ("identity", SOFT, "dash", 1)])
    return emit("10", "hard-and-soft-thresholds", "Hard and soft thresholds on the patch",
                "Threshold rules at λ = 50, and the patch after each rule at λ = 50 and 120. Worked by hand.",
                "denoising", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 640
    s = eyebrow(32, 40, "which call does what, its size rule or default, and the trap — mapped from source, not run")
    cols = [("call", 32), ("scale or layout", 336), ("size rule or default", 576), ("trap", 784)]
    y0 = 74
    for h, x in cols:
        s += mono(x, y0, h, size=8, fill=SOFT, anchor="start", track="0.08em")
    s += f'<line x1="32" y1="{y0 + 10}" x2="{vw - 32}" y2="{y0 + 10}" stroke="{RULE_SOLID}"/>'
    rows = [
        ("PyWavelets", 'pywt.dwt(x, "haar")', "orthonormal; d = (left − right)/√2", "⌊(N + L − 1)/2⌋ per band", "5 samples → 6 numbers"),
        ("PyWavelets", 'mode="symmetric" / "reflect"', "half- / whole-sample mirror", "symmetric is the default", "JPEG 2000 mirrors: reflect"),
        ("PyWavelets", 'mode="periodization"', "wraps the border", "⌈N/2⌉ per band", "odd N still gives N + 1"),
        ("PyWavelets", 'pywt.dwt2(img, "haar")', "(cA, (cH, cV, cD))", "5×5 → 4 × 3×3 = 36", "cH is JPEG 2000's LH"),
        ("PyWavelets", '"bior2.2", "bior4.4"', "the 5/3 and 9/7, × √2", "6 and 10 taps", "5×5 → 100 and 196"),
        ("PyWavelets", "pywt.threshold(w, lam)", "soft by default", "hard keeps survivors", "shrink details, not cA"),
        ("PyWavelets", "pywt.swt2(img, w, level)", "undecimated", "sides × 2**level", "the 5×5 patch is refused"),
        ("scikit-image", "denoise_wavelet(img)", "db1, soft, BayesShrink", "max levels − 3", "warns: non-orthogonal"),
        ("scikit-image", "estimate_sigma(img)", "db2, finest diagonal band", "median ÷ 0.6745", "exact zeros skipped"),
        ("Pillow", 'img.save("out.jp2")', "OpenJPEG; reversible 5/3", "6 resolutions, fewer if small", "irreversible=True: 9/7"),
        ("Pillow", "num_resolutions=n", "n − 1 levels", "used as given", "no automatic lowering"),
        ("Pillow", "im.reduce = k, then load()", "discards k resolutions", "each halves the size", "set before load"),
        ("OpenJPEG", "dwt.c", "lifting in place", "α…δ, K = 1.230174105", "64×64 code-blocks"),
    ]
    libcol = {"PyWavelets": SER2, "scikit-image": SER1, "Pillow": SER3, "OpenJPEG": SER4}
    for k, (lib, call, scal, rule, trap) in enumerate(rows):
        y = y0 + 34 + k * 40
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 18}" width="{vw - 56}" height="40" fill="rgba(45,49,66,0.03)"/>'
        s += mono(32, y - 4, lib, size=7, fill=libcol[lib], anchor="start", track="0.12em", weight="600")
        s += mono(32, y + 10, call, size=8.5, fill=INK, anchor="start", weight="500")
        s += mono(336, y + 4, scal, size=8.5, fill=MUTED, anchor="start")
        s += mono(576, y + 4, rule, size=8.5, fill=INK, anchor="start")
        s += mono(784, y + 4, trap, size=8.5, fill=ACCENT if "→" in trap or "LH" in trap else INK,
                  anchor="start", weight="600" if "→" in trap or "LH" in trap else "400")
    s += mono(32, vh - 16, "pinned commits: PyWavelets c9b542b, scikit-image b700edc, Pillow c15d19b, OpenJPEG 8314119",
              size=8, fill=SOFT, anchor="start")
    return emit("11", "tooling-map", "The tooling map",
                "Mirrors, sizes, names and defaults for the wavelet transform in four libraries. None of it was executed.",
                "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
