#!/usr/bin/env python3
"""Figures 01-12 for the-structure-tensor.

Every value drawn here is computed in this file, from the definitions, on the series'
5x5 patch: 3x3 Sobel derivatives under OpenCV's default reflect-101 border, the products
summed over a 3x3 box with the same border (cornerEigenValsVecs in corner.cpp at commit
802cf95, without its 1/3060 scale), the series' shared 3x3 Gaussian as an alternative
window, eigenvalues, every score, goodFeaturesToTrack's selection rule (featureselect.cpp),
and one Lucas-Kanade step on the patch moved one pixel right. Nothing is measured and
nothing loads an image. The asserts below hold the figures to the article's numbers.
Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SOFT,
                    emit, eyebrow, mono, txt)

SER1, SER2, SER3 = "#7c8f6f", "#5e7a9b", "#b8915a"

# ------------------------------------------------------------------ the data
N = 5
PATCH = [[40, 40, 40, 200, 200] for _ in range(N)]
PATCH[2][1] = 255


def pad(i, mode="reflect101"):
    if 0 <= i < N:
        return i
    if mode == "replicate":
        return 0 if i < 0 else N - 1
    return -i if i < 0 else 2 * (N - 1) - i          # reflect-101


def px(M, r, c, mode="reflect101"):
    return M[pad(r, mode)][pad(c, mode)]


def sobel(M, mode="reflect101"):
    gx = [[sum(w * (px(M, r + d, c + 1, mode) - px(M, r + d, c - 1, mode)) for d, w in ((-1, 1), (0, 2), (1, 1)))
           for c in range(N)] for r in range(N)]
    gy = [[sum(w * (px(M, r + 1, c + d, mode) - px(M, r - 1, c + d, mode)) for d, w in ((-1, 1), (0, 2), (1, 1)))
           for c in range(N)] for r in range(N)]
    return gx, gy


BOX = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
W1 = math.exp(-1 / (2 * 0.64))
G1 = [W1 / (1 + 2 * W1), 1 / (1 + 2 * W1), W1 / (1 + 2 * W1)]       # 0.239, 0.522, 0.239
GAUSS = [[G1[i] * G1[j] for j in range(3)] for i in range(3)]


def wsum(M, r, c, W):
    return sum(W[i + 1][j + 1] * px(M, r + i, c + j) for i in (-1, 0, 1) for j in (-1, 0, 1))


def tensor(gx, gy, W=BOX):
    xx = [[gx[r][c] ** 2 for c in range(N)] for r in range(N)]
    xy = [[gx[r][c] * gy[r][c] for c in range(N)] for r in range(N)]
    yy = [[gy[r][c] ** 2 for c in range(N)] for r in range(N)]
    return ([[wsum(xx, r, c, W) for c in range(N)] for r in range(N)],
            [[wsum(xy, r, c, W) for c in range(N)] for r in range(N)],
            [[wsum(yy, r, c, W) for c in range(N)] for r in range(N)])


def eig(a, b, c):
    m, d = (a + c) / 2, math.sqrt(((a - c) / 2) ** 2 + b * b)
    return m + d, m - d


def theta(a, b, c):
    return 0.5 * math.degrees(math.atan2(2 * b, a - c))


def harris(a, b, c, k):
    return a * c - b * b - k * (a + c) ** 2


def gftt(score, q=0.01):
    """featureselect.cpp: THRESH_TOZERO at q * max, 3x3 dilation, scan rows/cols 1..N-2."""
    mx = max(max(row) for row in score)
    t = [[v if v > mx * q else 0 for v in row] for row in score]
    dil = [[max(t[rr][cc] for rr in range(max(0, r - 1), min(N, r + 2)) for cc in range(max(0, c - 1), min(N, c + 2)))
            for c in range(N)] for r in range(N)]
    return mx, [(c, r) for r in range(1, N - 1) for c in range(1, N - 1) if t[r][c] != 0 and t[r][c] == dil[r][c]]


GX, GY = sobel(PATCH)
A, B, C = tensor(GX, GY)
L1 = [[eig(A[r][c], B[r][c], C[r][c])[0] for c in range(N)] for r in range(N)]
L2 = [[eig(A[r][c], B[r][c], C[r][c])[1] for c in range(N)] for r in range(N)]
TH = [[theta(A[r][c], B[r][c], C[r][c]) for c in range(N)] for r in range(N)]
COH = [[(L1[r][c] - L2[r][c]) / (L1[r][c] + L2[r][c]) for c in range(N)] for r in range(N)]
H04 = [[harris(A[r][c], B[r][c], C[r][c], 0.04) for c in range(N)] for r in range(N)]
H06 = [[harris(A[r][c], B[r][c], C[r][c], 0.06) for c in range(N)] for r in range(N)]
Q = [[4 * (A[r][c] * C[r][c] - B[r][c] ** 2) / (A[r][c] + C[r][c]) ** 2 for c in range(N)] for r in range(N)]
WF = [[(A[r][c] * C[r][c] - B[r][c] ** 2) / (A[r][c] + C[r][c]) for c in range(N)] for r in range(N)]
AG, BG, CG = tensor(GX, GY, GAUSS)


def tstar(k):
    """Ratio lambda2/lambda1 at which Harris's R changes sign."""
    return ((1 - 2 * k) - math.sqrt(1 - 4 * k)) / (2 * k)


def shifted_right(M):
    """The patch moved one pixel right; the new column c0 repeats the patch's own left value."""
    return [[M[r][c - 1] if c > 0 else M[r][0] for c in range(N)] for r in range(N)]


I2 = shifted_right(PATCH)
IT = [[I2[r][c] - PATCH[r][c] for c in range(N)] for r in range(N)]


def lk_one_step(r, c):
    """M d = -8 sum(G It): Sobel units, so g = G / 8 grey levels per pixel."""
    xt = [[GX[i][j] * IT[i][j] for j in range(N)] for i in range(N)]
    yt = [[GY[i][j] * IT[i][j] for j in range(N)] for i in range(N)]
    b1, b2 = -8 * wsum(xt, r, c, BOX), -8 * wsum(yt, r, c, BOX)
    a, b, cc = A[r][c], B[r][c], C[r][c]
    det = a * cc - b * b
    if det == 0:
        return None, (a, cc, b1, b2)
    return ((cc * b1 - b * b2) / det, (a * b2 - b * b1) / det), (a, cc, b1, b2)


def r1(v, nd=1):
    return round(v + 0.0, nd)


# ------------------------------------------------------------------ the article's numbers
assert GX == [[0, 0, 640, 640, 0], [0, 0, 425, 640, 0], [0, 0, 210, 640, 0], [0, 0, 425, 640, 0],
              [0, 0, 640, 640, 0]]
assert GY[1] == [430, 430, 215, 0, 0] and GY[3] == [-430, -430, -215, 0, 0] and GY[0] == GY[2] == GY[4] == [0] * 5
assert sobel(PATCH, "replicate")[0][2][0] == 430                       # Part 8's replicate value at (r2, c0)
assert [A[2][c] for c in range(N)] == [0, 405350, 1634150, 1634150, 2457600]
assert [C[2][c] for c in range(N)] == [1109400, 832050, 462250, 92450, 0] and B[2] == [0] * 5
assert (A[1][2], B[1][2], C[1][2]) == (1863125, 91375, 231125)
assert (r1(L1[1][2]), r1(L2[1][2]), r1(TH[1][2], 2)) == (1868225.1, 226024.9, 3.19)
assert (A[1][1], B[1][1], C[1][1]) == (634325, 91375, 416025) and (round(L1[1][1]), round(L2[1][1])) == (667524, 382826)
assert r1(TH[1][1], 1) == 20.0 and r1(COH[1][1], 2) == 0.27 and r1(TH[0][1], 1) == 49.8
assert [r1(H04[2][c] / 1e9) for c in range(N)] == [-49.2, 276.0, 579.6, 31.8, -241.6]
assert [r1(H06[2][c] / 1e9) for c in range(N)] == [-73.8, 245.4, 491.7, -27.8, -362.4]
assert r1(H04[1][2] / 1e9) == 246.8
assert [r1(L2[2][c] / L1[2][c], 3) for c in range(N)] == [0.0, 0.487, 0.283, 0.057, 0.0]
assert (r1(tstar(0.04), 4), r1(tstar(0.05), 4), r1(tstar(0.06), 4)) == (0.0436, 0.0557, 0.0685)
assert (r1(1 / tstar(0.04)), r1(1 / tstar(0.06), 1)) == (23.0, 14.6)
_t2 = L2[2][2] / L1[2][2]
assert r1(_t2 / (1 + _t2) ** 2, 3) == 0.172
_t1 = L2[2][1] / L1[2][1]
_t3 = L2[2][3] / L1[2][3]
assert r1(_t1 / (1 + _t1) ** 2, 3) == 0.220 and r1(_t3 / (1 + _t3) ** 2, 4) == 0.0507
S = 1 / (4 * 3 * 255)
assert 1 / S == 3060
assert r1(L2[2][2] * S * S, 5) == 0.04937 and r1(H04[2][2] * S ** 4, 6) == 0.006611
assert r1(H04[2][3] * S ** 4, 6) == 0.000363 and r1(H06[2][3] * S ** 4, 6) == -0.000317
MX, PTS = gftt(L2)
assert r1(MX) == 616155.8 and L2[0][1] == L2[4][1] == MX and PTS == [(2, 2)]
assert gftt(H04)[1] == [(2, 2)] and gftt(L2, 0.8)[1] == [] and r1(L2[2][2] / MX, 4) == 0.7502
assert r1(MX * 0.8) == 492924.7
assert [r1(Q[2][c], 3) for c in (1, 2, 3)] == [0.881, 0.688, 0.203]
assert (round(WF[2][1]), round(WF[2][2])) == (272565, 360325)
_pass = [(r, c) for r in range(1, N - 1) for c in range(1, N - 1) if Q[r][c] > 0.75]
assert _pass == [(1, 1), (2, 1), (3, 1)] and max(_pass, key=lambda p: WF[p[0]][p[1]]) == (2, 1)
_r = lambda q: (2 - q + 2 * math.sqrt(1 - q)) / q                 # eigenvalue ratio with roundness q
assert (r1(_r(0.75), 2), r1(_r(0.5), 1)) == (3.0, 5.8)
assert [r1(COH[2][c], 2) for c in range(N)] == [1.0, 0.34, 0.56, 0.89, 1.0]
assert IT[2] == [0, -215, 215, -160, 0] and IT[0] == [0, 0, 0, -160, 0]
_d2, _ = lk_one_step(2, 2)
_d1, _ = lk_one_step(2, 1)
_d3, _ = lk_one_step(2, 3)
_n4, (_a4, _c4, _b14, _b24) = lk_one_step(2, 4)
_n0, (_a0, _c0, _b10, _b20) = lk_one_step(2, 0)
assert (r1(_d2[0], 2), _d2[1]) == (1.28, 0) and (r1(_d1[0], 2), _d1[1]) == (-0.89, 0) and r1(_d3[0], 2) == 1.28
assert _n4 is None and _b24 == 0 and _b14 / _a4 == 2.0 and _n0 is None and _b20 == 0 and _b10 == 0
assert sum(GX[r][c] * IT[r][c] for r in (1, 2, 3) for c in (1, 2, 3)) == -262050
assert [r1(math.sqrt(L1[2][c] / L2[2][c]), 2) for c in (3, 2, 1)] == [4.2, 1.88, 1.43]
assert (r1(A[2][2] / 64), r1(C[2][2] / 64)) == (25533.6, 7222.7)
_dbl = [(GX[r][c] ** 2 - GY[r][c] ** 2, 2 * GX[r][c] * GY[r][c]) for r in (1, 2, 3) for c in (0, 1, 2)]
assert (sum(v[0] for v in _dbl), sum(v[1] for v in _dbl)) == (-426700, 0)
assert (sum(GX[r][c] for r in (1, 2, 3) for c in (0, 1, 2)), sum(GY[r][c] for r in (1, 2, 3) for c in (0, 1, 2))) == (1060, 0)
assert [r1(min(AG[2][c], CG[2][c]) / max(AG[2][c], CG[2][c]), 4) for c in (1, 2, 3)] == [0.3603, 0.2107, 0.022]
assert [r1(v, 4) for v in (GAUSS[0][0], GAUSS[0][1], GAUSS[1][1])] == [0.0571, 0.1248, 0.2725]
_p3 = [row[:] for row in PATCH]
_p3[2][1] = 120
_gx3, _gy3 = sobel(_p3)
_a3, _b3, _c3 = tensor(_gx3, _gy3)
_l23 = [[eig(_a3[r][c], _b3[r][c], _c3[r][c])[1] for c in range(N)] for r in range(N)]
assert gftt(_l23)[1] == [(1, 2)] and (_a3[2][1], _c3[2][1], _c3[2][2]) == (857600, 115200, 64000)
_xt = [[GX[i][j] * IT[i][j] for j in range(N)] for i in range(N)]
_tt = [[IT[i][j] ** 2 for j in range(N)] for i in range(N)]
assert (A[2][4] / 64, wsum(_xt, 2, 4, BOX) / 8, wsum(_tt, 2, 4, BOX)) == (38400, -76800, 153600)  # E5


# ------------------------------------------------------------------ drawing helpers
def fmt(v, nd=1):
    if abs(v - round(v)) < 1e-9:
        s = f"{round(v):,}"
    else:
        s = f"{v:,.{nd}f}"
    return s.replace("-", "−")


def shade_rect(x, y, w, h, t, stroke="rgba(45,49,66,0.30)", sw=0.8):
    """High value = bright (series rule): t = 1 is paper, t = 0 is ink."""
    t = max(0.0, min(1.0, t))
    a = 0.88 * (1 - t) + 0.02
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"/>')


def ink_for(t):
    return "#ffffff" if t < 0.52 else INK


def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, marker=None, cap=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    c = f' stroke-linecap="{cap}"' if cap else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{m}{c}{o}/>')


def polyline(pts, stroke, sw=1.6, dash=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}{o}/>')


def polygon(pts, fill, stroke="none", sw=0.8, op=None):
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None):
    s = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{s}/>'


def ring(x, y, rr=5, stroke=INK, sw=1.6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{PAPER}" stroke="{stroke}" stroke-width="{sw}"/>'


def ellipse(cx, cy, rx, ry, ang=0.0, fill="none", stroke=INK, sw=1.6, op=None, dash=None):
    """Semi-axis rx along angle `ang` (degrees, clockwise on screen, image convention)."""
    o = f' fill-opacity="{op}"' if op is not None else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{max(rx, 0.01):.2f}" ry="{max(ry, 0.01):.2f}" '
            f'transform="rotate({ang:.2f} {cx:.1f} {cy:.1f})" fill="{fill}"{o} stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


def glyph(cx, cy, l1, l2, ang, scale, stroke=INK, fill=None, op=0.14, sw=1.6):
    """A tensor as an ellipse with semi-axes scale * sqrt(lambda); rank 1 as a capped line."""
    a, b = scale * math.sqrt(max(l1, 0)), scale * math.sqrt(max(l2, 0))
    if b < 0.75:
        dx, dy = a * math.cos(math.radians(ang)), a * math.sin(math.radians(ang))
        return line(cx - dx, cy - dy, cx + dx, cy + dy, stroke=stroke, sw=3.2, cap="round")
    return ellipse(cx, cy, a, b, ang, fill=fill or stroke, stroke=stroke, sw=sw, op=op)


def note_lines(x, y, items, size=8.5, gap=16, anchor="start"):
    out = ""
    for k, (t, c) in enumerate(items):
        if t:
            out += mono(x, y + k * gap, t, size=size, fill=c, anchor=anchor,
                        weight="600" if c in (INK, LINK, ACCENT) else "400")
    return out


def title(x, y, s, fill=INK, anchor="start", size=9.5):
    """A panel title in mono, not uppercased, so positions like (r2, c1) keep their case."""
    return mono(x, y, s, size=size, fill=fill, anchor=anchor, weight="600")


def legend2(y, vw, items):
    """Legend whose swatches are drawn exactly like the marks they name."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for item in items:
        label, colour, kind = item[:3]
        op = item[3] if len(item) > 3 else None
        if kind in ("line", "dash", "dot-line"):
            d = {"line": "", "dash": ' stroke-dasharray="5,3"', "dot-line": ' stroke-dasharray="1.5,2.5"'}[kind]
            s += (f'<line x1="{x}" y1="{y + 5}" x2="{x + 18}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.8"{d}' + (f' stroke-opacity="{op}"' if op else "") + '/>')
        elif kind == "dot":
            s += dot(x + 8, y + 5, 4, fill=colour)
        elif kind == "ring":
            s += ring(x + 8, y + 5, 4.5, stroke=colour)
        elif kind == "fill":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke=colour, sw=0.8, op=op or 0.85)
        elif kind == "area":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke="none", sw=0, op=op)
        elif kind == "outline":
            s += rect(x, y - 1, 16, 12, fill="none", stroke=colour, sw=1.8)
        elif kind == "dashbox":
            s += rect(x, y - 1, 16, 12, fill="none", stroke=colour, sw=1.6, dash="3,2")
        elif kind == "hatch":
            s += rect(x, y - 1, 16, 12, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8)
            s += rect(x, y - 1, 16, 12, fill="url(#hatch)", stroke="none", sw=0)
        elif kind == "ell":
            s += ellipse(x + 8, y + 5, 8, 4.2, 0, fill=colour, stroke=colour, sw=1.4, op=op or 0.14)
        elif kind == "rank1":
            s += line(x + 1, y + 5, x + 17, y + 5, stroke=colour, sw=3.2, cap="round")
        elif kind == "hbar":
            s += line(x + 3, y + 5, x + 15, y + 5, stroke=colour, sw=2.4, cap="round")
        elif kind == "vbar":
            s += line(x + 8, y - 1, x + 8, y + 11, stroke=colour, sw=2.4, cap="round")
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.04em")
        x += 24 + 5.6 * len(label) + 30
    return s


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr, xmap=None):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr
        self.xmap = xmap or (lambda v: v)

    def X(self, x):
        a, b = self.xmap(self.xr[0]), self.xmap(self.xr[1])
        return self.x0 + (self.xmap(x) - a) / (b - a) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def clip(self, cid):
        return (f'<clipPath id="{cid}"><rect x="{self.x0}" y="{self.y0}" width="{self.w}" '
                f'height="{self.h}"/></clipPath>')

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid_y=True):
        s = line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, stroke=RULE_SOLID)
        s += line(self.x0, self.y0, self.x0, self.y0 + self.h, stroke=RULE_SOLID)
        for v in yt:
            yy = self.Y(v)
            if grid_y:
                s += line(self.x0, yy, self.x0 + self.w, yy, stroke=RULE, sw=0.8)
            s += mono(self.x0 - 7, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            s += mono(self.X(v), self.y0 + self.h + 14, xfmt(v), size=8, fill=SOFT)
        if xlab:
            s += mono(self.x0 + self.w, self.y0 + self.h + 30, xlab, size=8.5, fill=SOFT, anchor="end")
        if ylab:
            s += mono(self.x0, self.y0 - 10, ylab, size=8.5, fill=SOFT, anchor="start")
        return s


def labels_rc(x, y, cs, n=N, cols=None):
    s = ""
    for j, name in enumerate(cols or [f"c{j}" for j in range(n)]):
        s += mono(x + j * cs + cs / 2, y - 7, name, size=7.5, fill=SOFT)
    for i in range(n):
        s += mono(x - 8, y + i * cs + cs / 2 + 3, f"r{i}", size=7.5, fill=SOFT, anchor="end")
    return s


MARKS = f"""<defs>
    <marker id="aw" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#ffffff"/></marker>
    <marker id="ai" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{INK}"/></marker>
    <marker id="al" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
    <marker id="aa" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
    <marker id="am" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
    <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="1" y1="0" x2="1" y2="7" stroke="rgba(45,49,66,0.34)" stroke-width="1.3"/>
      <line x1="4.5" y1="0" x2="4.5" y2="7" stroke="rgba(255,255,255,0.55)" stroke-width="1.3"/>
    </pattern>
  </defs>"""


def arrow(x1, y1, x2, y2, colour, sw=1.5):
    m = {INK: "ai", LINK: "al", ACCENT: "aa", MUTED: "am", "#ffffff": "aw"}[colour]
    return line(x1, y1, x2, y2, stroke=colour, sw=sw, marker=m)


ROW2 = [(2, c) for c in range(N)]
NAME = {0: "mirrored ring", 1: "the impulse", 2: "step plus ring", 3: "step, two ring pixels", 4: "the step alone"}


# ------------------------------------------------------------------ FIG 01
def mini_window(x0, y0, cs, cc):
    """Columns c-1..c5 of the padded gradient; the 3x3 window centred at (r2, cc) outlined."""
    s = ""
    cols = list(range(-1, N + 1))
    for k, c in enumerate(cols):
        ghost = c < 0 or c >= N
        s += mono(x0 + k * cs + cs / 2, y0 - 6, f"c{c}" if not ghost else ("c1" if c < 0 else "c3"),
                  size=6.5, fill=SOFT if not ghost else RULE_SOLID)
        for r in range(N):
            x, y = x0 + k * cs, y0 + r * cs
            v = px(PATCH, r, c)
            s += shade_rect(x, y, cs, cs, v / 255, sw=0.6)
            if ghost:
                s += rect(x, y, cs, cs, fill="url(#hatch)", stroke="rgba(45,49,66,0.30)", sw=0.6)
            gx, gy = px(GX, r, c), px(GY, r, c)
            cx, cy = x + cs / 2, y + cs / 2
            if gx:
                s += line(cx - 5.5, cy, cx + 5.5, cy, stroke="#ffffff", sw=4.4, cap="round")
                s += line(cx - 5.5, cy, cx + 5.5, cy, stroke=LINK, sw=2.4, cap="round")
            if gy:
                s += line(cx, cy - 5.5, cx, cy + 5.5, stroke="#ffffff", sw=4.4, cap="round")
                s += line(cx, cy - 5.5, cx, cy + 5.5, stroke=ACCENT, sw=2.4, cap="round")
    k0 = cols.index(cc - 1)
    s += rect(x0 + k0 * cs, y0 + cs, 3 * cs, 3 * cs, fill="none", stroke=ACCENT, sw=2.2)
    return s


def fig01():
    vw, vh = 1016, 676
    s = MARKS + eyebrow(32, 40, "the gradient opencv's corner functions sum: sobel 3×3, reflect-101 border")
    cs, xa, y0 = 56, 72, 108
    s += title(xa - 32, 86, "the patch, with each pixel's gradient vector")
    s += labels_rc(xa, y0, cs)
    for r in range(N):
        for c in range(N):
            x, y = xa + c * cs, y0 + r * cs
            t = PATCH[r][c] / 255
            s += shade_rect(x, y, cs, cs, t)
            col = ink_for(t)
            s += mono(x + 5, y + 12, str(PATCH[r][c]), size=7.5, fill=col, anchor="start")
            m = math.hypot(GX[r][c], GY[r][c])
            cx, cy = x + cs / 2, y + cs / 2 + 4
            if m == 0:
                if (r, c) == (2, 1):
                    s += mono(cx, cy + 4, "0", size=11, fill=ACCENT, weight="600")
                continue
            L = 0.66 * cs * math.sqrt(m / 640)
            ux, uy = GX[r][c] / m, GY[r][c] / m
            s += arrow(cx - ux * L / 2, cy - uy * L / 2, cx + ux * L / 2, cy + uy * L / 2,
                       "#ffffff" if col == "#ffffff" else INK)
    nx = 410
    s += note_lines(nx, 128, [
        ("the step reads 640 = 4 × 160 on c2 and c3", LINK), ("", None),
        ("the impulse's own pixel: gradient 0,", ACCENT), ("the same zero matrix as a flat pixel", MUTED), ("", None),
        ("column c0: reflect-101 copies c1 to its left,", INK), ("so Gx = 0 there and only the ring's", MUTED),
        ("vertical derivatives remain (Part 8's replicate", MUTED), ("table read 215, 430, 215 here)", MUTED), ("", None),
        ("one pixel's outer product has rank 0 or 1:", INK), ("no single pixel can be a corner", MUTED)])
    s += title(32, 440, "the five windows of row r2: what each 3×3 sum takes in")
    mcs, mx0, my0, gap = 18, 52, 470, 58
    for k, cc in enumerate(range(N)):
        x0 = mx0 + k * (7 * mcs + gap)
        s += mini_window(x0, my0, mcs, cc)
        cx = x0 + 3.5 * mcs
        s += title(cx, my0 + 5 * mcs + 20, f"(r2, c{cc})", anchor="middle", size=9)
        s += mono(cx, my0 + 5 * mcs + 36, f"A = {fmt(A[2][cc])}", size=8, fill=LINK, weight="600")
        s += mono(cx, my0 + 5 * mcs + 50, f"C = {fmt(C[2][cc])}", size=8, fill=ACCENT, weight="600")
    s += legend2(vh - 30, vw, [("Gx ≠ 0", LINK, "hbar"), ("Gy ≠ 0", ACCENT, "vbar"),
                               ("3×3 window", ACCENT, "outline"), ("column mirrored by reflect-101", SOFT, "hatch")])
    return emit("01", "patch-gradient", "The patch's gradient and the windows of row r2",
                "Sobel 3×3 under OpenCV's reflect-101 border, and what each 3×3 window on row r2 sums. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 436
    s = eyebrow(32, 40, "row r2: each window's tensor drawn as an ellipse, semi-axes ∝ √λ")
    pw, x0, cy = 184, 48, 196
    scale = 70 / math.sqrt(max(L1[2]))
    for k, (r, c) in enumerate(ROW2):
        cx = x0 + k * pw + pw / 2
        s += rect(x0 + k * pw + 6, 70, pw - 12, 300, fill="#ffffff", stroke="rgba(45,49,66,0.14)", rx=4)
        s += title(cx, 92, f"(r2, c{c})", anchor="middle")
        s += mono(cx, 108, NAME[c], size=8, fill=SOFT)
        win = c == 2
        colr = ACCENT if win else INK
        s += line(cx - 78, cy, cx + 78, cy, stroke=RULE, sw=0.8)
        s += line(cx, cy - 76, cx, cy + 76, stroke=RULE, sw=0.8)
        s += glyph(cx, cy, L1[r][c], L2[r][c], TH[r][c], scale, stroke=colr)
        rank = 1 if L2[r][c] < 1e-9 else 2
        s += mono(cx, 300, f"λ1 = {fmt(L1[r][c])}", size=8.5, fill=INK, weight="600")
        s += mono(cx, 316, f"λ2 = {fmt(L2[r][c])}", size=8.5, fill=INK, weight="600")
        ratio = L2[r][c] / L1[r][c]
        s += mono(cx, 334, f"λ2/λ1 = {ratio:.3f}" if ratio else "λ2/λ1 = 0", size=8, fill=MUTED)
        verdict = {0: "rank 1: reads as an edge", 1: "rank 2", 2: "rank 2: the strongest", 3: "rank 2, barely",
                   4: "rank 1: an edge"}[c]
        s += mono(cx, 352, verdict, size=8, fill=ACCENT if c in (2, 3) else MUTED, weight="600" if c in (2, 3) else "400")
        assert (rank == 1) == (c in (0, 4))
    s += legend2(vh - 30, vw, [("rank-2 tensor", INK, "ell"), ("rank 1: a line, one direction", INK, "rank1"),
                               ("goodFeaturesToTrack's pick", ACCENT, "ell")])
    return emit("02", "row-r2-tensors", "Row r2's five tensors",
                "Each window's 2×2 matrix drawn as an ellipse along its eigenvectors, semi-axes proportional "
                "to the square roots of its eigenvalues. Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 540
    s = MARKS + eyebrow(32, 40, "goodfeaturestotrack on the patch: the smaller-eigenvalue map and the one point it returns")
    cs, xa, y0 = 66, 72, 112
    s += title(xa - 32, 88, "λ2 at every pixel (box 3×3, reflect-101)")
    s += labels_rc(xa, y0, cs)
    for r in range(N):
        for c in range(N):
            x, y = xa + c * cs, y0 + r * cs
            t = L2[r][c] / MX
            s += shade_rect(x, y, cs, cs, t)
            border = r in (0, N - 1) or c in (0, N - 1)
            if border:
                s += rect(x, y, cs, cs, fill="url(#hatch)", stroke="rgba(45,49,66,0.30)", sw=0.8)
            lab = fmt(L2[r][c], 0) if L2[r][c] else "0"
            s += rect(x + cs / 2 - 3.1 * len(lab) - 4, y + cs / 2 - 6, 6.2 * len(lab) + 8, 14, rx=2,
                      fill=PAPER if t >= 0.52 else "#3a3e4f", stroke="none", sw=0)
            s += mono(x + cs / 2, y + cs / 2 + 4, lab, size=8.5, fill=ink_for(t), weight="500")
    for (r, c) in ((0, 1), (4, 1)):
        s += rect(xa + c * cs + 2, y0 + r * cs + 2, cs - 4, cs - 4, fill="none", stroke=LINK, sw=2, dash="4,3")
    s += rect(xa + 2 * cs + 1, y0 + 2 * cs + 1, cs - 2, cs - 2, fill="none", stroke=ACCENT, sw=2.6)
    nx = 448
    s += title(nx, 88, "the selection rule, on these numbers")
    s += note_lines(nx, 112, [
        ("1  maximum of the map: 616,156 at (r0, c1), (r4, c1)", LINK),
        ("   (reflect-101 mirrors row r1's ring over r0 and r4)", MUTED),
        ("2  zero everything at or below 0.01 × max = 6,162", MUTED),
        ("3  keep pixels equal to their 3×3 maximum", MUTED),
        ("4  scan rows and columns 1 to 3 only", MUTED),
        ("   → one point: (2, 2), λ2 = 462,250", ACCENT)], gap=17)
    s += title(nx, 252, "why (r2, c2): two edges in one window")
    gy, sc = 352, 62 / math.sqrt(A[2][2])
    parts = [(A[2][2], 0, 0, "the step's Gx²: A = 1,634,150", LINK),
             (C[2][2], 0, 90, "the ring's Gy²: C = 462,250", ACCENT),
             (A[2][2], C[2][2], 0, "their sum: (r2, c2)'s tensor", INK)]
    for k, (l1, l2, ang, lab, colr) in enumerate(parts):
        cx = nx + 70 + k * 172
        s += glyph(cx, gy, l1, l2, ang, sc, stroke=colr)
        s += mono(cx, gy + 84, lab, size=8, fill=colr, weight="600")
        if k < 2:
            s += mono(cx + 86, gy + 4, "+" if k == 0 else "=", size=16, fill=MUTED, weight="600")
    s += legend2(vh - 30, vw, [("never returned: the 1-px border", SOFT, "hatch"), ("the map's maximum", LINK, "dashbox"),
                               ("the returned point", ACCENT, "outline")])
    return emit("03", "good-features-verdict", "What goodFeaturesToTrack returns, and why",
                "The smaller-eigenvalue map, the border the function never returns, and the one interior "
                "maximum: (r2, c2). Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 440
    s = eyebrow(32, 40, "the cost of shifting a window by up to one pixel, in grey levels squared")
    levels = [(2000, 0.35), (6000, 0.55), (12000, 0.75), (20000, 0.95)]
    pw, sz, x0, y0 = 240, 170, 54, 104
    for k, c in enumerate((4, 3, 2, 1)):
        ax = Axes(x0 + k * pw, y0, sz, sz, (-1, 1), (-1, 1))
        cid = f"c4_{k}"
        s += f"<defs>{ax.clip(cid)}</defs>"
        s += ax.frame([-1, 0, 1], [-1, 0, 1], xlab="u (px)", ylab="v (px, down)", xfmt=lambda v: fmt(v, 0),
                      yfmt=lambda v: fmt(-v, 0), grid_y=False)
        s += line(ax.X(0), ax.Y(-1), ax.X(0), ax.Y(1), stroke=RULE, sw=0.8)
        s += line(ax.X(-1), ax.Y(0), ax.X(1), ax.Y(0), stroke=RULE, sw=0.8)
        a, cc = A[2][c] / 64, C[2][c] / 64
        body = ""
        for lev, op in levels:
            ru = math.sqrt(lev / a) if a else 99
            rv = math.sqrt(lev / cc) if cc else 99
            pxu, pxv = ru * sz / 2, rv * sz / 2
            if cc == 0:
                for sgn in (-1, 1):
                    body += line(ax.X(sgn * ru), ax.y0, ax.X(sgn * ru), ax.y0 + sz, stroke=INK, sw=1.3, op=op)
            else:
                body += ellipse(ax.X(0), ax.Y(0), pxu, pxv, 0, stroke=INK, sw=1.3, op=None).replace(
                    'stroke-width="1.3"', f'stroke-width="1.3" stroke-opacity="{op}"')
        s += f'<g clip-path="url(#{cid})">{body}</g>'
        s += title(ax.x0, 72, f"(r2, c{c}): {'a trough' if c == 4 else 'a long bowl' if c == 3 else 'a bowl'}", size=9)
        s += mono(ax.x0, ax.y0 + sz + 48, f"curvature in u: {fmt(a)}", size=8, fill=MUTED, anchor="start")
        s += mono(ax.x0, ax.y0 + sz + 62, f"curvature in v: {fmt(cc)}", size=8, fill=MUTED, anchor="start")
    s += mono(32, vh - 52, "contours of the quadratic cost dᵀMd, M in squared grey levels per pixel: the Sobel-unit tensor ÷ 64 "
              "(Sobel reads a unit ramp as 8)", size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 30, vw, [(f"cost {fmt(lev)}", INK, "line", op) for lev, op in levels])
    return emit("04", "shift-cost-surfaces", "The cost of shifting a window",
                "Contours of the quadratic shift cost for four windows of row r2. Evaluated from the worked matrices.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "the eigenvalue plane to scale: every boundary is a ray except shi–tomasi's")
    ax = Axes(96, 96, 624, 240, (0, 2.6e6), (0, 1.0e6))
    s += f"<defs>{ax.clip('c5')}<clipPath id='c5i'><rect x='780' y='118' width='200' height='170'/></clipPath></defs>"
    s += ax.frame([0, 0.5e6, 1e6, 1.5e6, 2e6, 2.5e6], [0, 0.5e6, 1e6], xlab="λ1, the larger eigenvalue",
                  ylab="λ2", xfmt=lambda v: f"{v / 1e6:.1f}M" if v else "0", yfmt=lambda v: f"{v / 1e6:.1f}M" if v else "0")
    rays = [(tstar(0.04), ACCENT, "line", "Harris k = 0.04"), (tstar(0.06), ACCENT, "dash", "Harris k = 0.06"),
            (1 / _r(0.5), LINK, "dash", "Förstner q = 0.5"), (1 / _r(0.75), LINK, "line", "Förstner q = 0.75"),
            (1.0, RULE_SOLID, "line", "λ2 = λ1")]
    body = ""
    for t, colr, kind, _ in rays:
        body += line(ax.X(0), ax.Y(0), ax.X(2.6e6), ax.Y(2.6e6 * t), stroke=colr, sw=1.4,
                     dash="5,3" if kind == "dash" else None)
    tau = 0.5 * MX
    body += line(ax.X(0), ax.Y(tau), ax.X(2.6e6), ax.Y(tau), stroke=SER1, sw=1.4, dash="1.5,2.5")
    pts = {c: (L1[2][c], L2[2][c]) for c in range(N)}
    for c, (a, b) in pts.items():
        body += dot(ax.X(a), ax.Y(b), 4.2, fill=ACCENT if c == 2 else INK, stroke="#ffffff")
    s += f'<g clip-path="url(#c5)">{body}</g>'
    lab = {0: (10, 24, "c0"), 1: (-10, -8, "c1, the impulse"), 2: (6, -8, "c2"), 3: (0, -22, "c3"), 4: (-4, -9, "c4")}
    for c, (dx, dy, t) in lab.items():
        a, b = pts[c]
        s += mono(ax.X(a) + dx, ax.Y(b) + dy, t, size=8, fill=INK, weight="600", anchor="end" if c == 1 else "start" if c == 2 else "middle")
    s += mono(ax.X(2.58e6), ax.Y(tau) + 14, f"qualityLevel 0.5: λ2 > {fmt(tau, 0)}", size=7.5, fill=SER1, anchor="end")
    s += mono(ax.X(0.64e6), ax.Y(0.64e6) - 8, "λ2 = λ1", size=7.5, fill=SOFT, anchor="end")
    # inset: around c3, not to scale
    ix, iy, iw, ih = 780, 118, 200, 170
    xr, yr = (1.45e6, 1.85e6), (0, 1.5e5)
    IX = lambda v: ix + (v - xr[0]) / (xr[1] - xr[0]) * iw
    IY = lambda v: iy + ih - (v - yr[0]) / (yr[1] - yr[0]) * ih
    s += rect(ix, iy, iw, ih, fill="#ffffff", stroke=RULE_SOLID, sw=0.8)
    inner = ""
    for t, colr, kind, _ in rays[:2]:
        inner += line(IX(xr[0]), IY(xr[0] * t), IX(xr[1]), IY(xr[1] * t), stroke=colr, sw=1.6,
                      dash="5,3" if kind == "dash" else None)
    a3, b3 = pts[3]
    inner += line(IX(a3), IY(a3 * tstar(0.04)), IX(a3), IY(a3 * tstar(0.06)), stroke=SOFT, sw=0.8, dash="2,2")
    inner += dot(IX(a3), IY(b3), 4.6, fill=INK, stroke="#ffffff")
    s += f'<g clip-path="url(#c5i)">{inner}</g>'
    s += title(ix, iy - 10, "zoom on c3 (not to scale)", size=8.5)
    s += mono(IX(a3) + 9, IY(b3) + 3, f"c3: {fmt(b3, 0)}", size=8, fill=INK, anchor="start", weight="600")
    s += mono(ix + 8, IY(xr[0] * tstar(0.06)) - 8, "k = 0.06", size=7.5, fill=ACCENT, anchor="start")
    s += mono(ix + 8, IY(xr[0] * tstar(0.04)) + 16, "k = 0.04", size=7.5, fill=ACCENT, anchor="start")
    s += mono(ix, iy + ih + 16, f"at λ1 = {fmt(a3, 0)}: k 0.04 boundary {fmt(a3 * tstar(0.04), 0)},", size=7.5,
              fill=SOFT, anchor="start")
    s += mono(ix, iy + ih + 30, f"k 0.06 boundary {fmt(a3 * tstar(0.06), 0)}; c3 between", size=7.5, fill=SOFT,
              anchor="start")
    # a quiet box on the main plot marks where the zoom comes from
    s += rect(ax.X(xr[0]), ax.Y(yr[1]), ax.X(xr[1]) - ax.X(xr[0]), ax.Y(0) - ax.Y(yr[1]), fill="none",
              stroke=SOFT, sw=0.8, dash="2,2")
    s += note_lines(96, 384, [
        ("Harris's sign depends only on λ2/λ1, so its zero line is a ray: corners lie above it.", INK),
        ("Förstner's roundness is a ray too. Shi–Tomasi's threshold on λ2 is a horizontal line: it moves", MUTED),
        ("with contrast, while the rays do not. Points: row r2's windows (c0 and c4 have λ2 = 0).", MUTED)])
    s += legend2(vh - 30, vw, [("Harris k = 0.04", ACCENT, "line"), ("k = 0.06", ACCENT, "dash"),
                               ("Förstner q = 0.75", LINK, "line"), ("q = 0.5", LINK, "dash"),
                               ("λ2 threshold", SER1, "dot-line"), ("window", INK, "dot"), ("the pick", ACCENT, "dot")])
    return emit("05", "eigenvalue-plane", "The eigenvalue plane, to scale",
                "Harris's and Förstner's boundaries as rays, a Shi–Tomasi threshold as a line, and row r2's "
                "windows. Computed from the definitions on the worked eigenvalues.", "scores", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "each score against the eigenvalue ratio at a fixed trace, scaled to 1 for equal eigenvalues")
    lg = lambda v: math.log10(v)
    ax = Axes(96, 96, 640, 250, (0.01, 1.0), (-0.4, 1.05), xmap=lg)
    s += f"<defs>{ax.clip('c6')}</defs>"
    s += ax.frame([0.01, 0.03, 0.1, 0.3, 1.0], [-0.25, 0, 0.25, 0.5, 0.75, 1.0], xlab="t = λ2 / λ1 (log scale)",
                  ylab="score ÷ score at t = 1", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}".replace("-", "−"))
    s += line(ax.x0, ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=INK, sw=0.9)
    ts = [10 ** (-2 + 2 * i / 400) for i in range(401)]
    curves = [(lambda t: (t / (1 + t) ** 2 - 0.04) / (0.25 - 0.04), ACCENT, None),
              (lambda t: (t / (1 + t) ** 2 - 0.06) / (0.25 - 0.06), ACCENT, "5,3"),
              (lambda t: 2 * t / (1 + t), INK, None),
              (lambda t: 4 * t / (1 + t) ** 2, LINK, None)]
    body = ""
    for f, colr, dash in curves:
        body += polyline([(ax.X(t), ax.Y(f(t))) for t in ts], colr, sw=1.8, dash=dash)
    for k in (0.04, 0.06):
        body += dot(ax.X(tstar(k)), ax.Y(0), 3.8, fill=ACCENT, stroke="#ffffff")
    s += f'<g clip-path="url(#c6)">{body}</g>'
    for c, lab in ((3, "c3 0.057"), (2, "c2 0.283"), (1, "c1 0.487")):
        t = L2[2][c] / L1[2][c]
        s += line(ax.X(t), ax.y0 + 14, ax.X(t), ax.y0 + ax.h, stroke=SOFT, sw=0.8, dash="2,3")
        s += mono(ax.X(t), ax.y0 + 8, lab, size=7.5, fill=INK, weight="600")
    for k, lab in ((0.04, "0.0436"), (0.06, "0.0685")):
        xk = ax.X(tstar(k))
        s += line(xk, ax.Y(0) + 5, xk, ax.Y(-0.30), stroke=ACCENT, sw=0.8, dash="1.5,2")
        s += mono(xk, ax.Y(-0.30) + 11, lab, size=7.5, fill=ACCENT, weight="600")
    nx = 770
    s += note_lines(nx, 120, [
        ("Harris: t/(1+t)² − k", ACCENT), ("negative below its zero:", MUTED), ("k = 0.04 → 0.0436", MUTED),
        ("k = 0.06 → 0.0685", MUTED), ("c3 sits between", MUTED), ("", None),
        ("Shi–Tomasi: λ2 ∝ t/(1+t)", INK), ("never negative", MUTED), ("", None),
        ("Förstner q = 4t/(1+t)²", LINK), ("harmonic mean: same shape", MUTED), ("", None),
        ("c0 and c4: t = 0, off the", SOFT), ("left edge", SOFT)], gap=15)
    s += legend2(vh - 30, vw, [("Harris k = 0.04", ACCENT, "line"), ("Harris k = 0.06", ACCENT, "dash"),
                               ("Shi–Tomasi", INK, "line"), ("Förstner roundness", LINK, "line")])
    return emit("06", "scores-against-ratio", "Every score against the eigenvalue ratio",
                "Harris, Shi–Tomasi and Förstner as functions of λ2/λ1 at a fixed trace, with row r2's ratios "
                "marked. Closed forms.", "scores", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 460
    s = MARKS + eyebrow(32, 40, "why the tensor squares before it sums, on the impulse's window")
    cs, xa, y0 = 70, 64, 116
    s += title(32, 92, "(r2, c1): nine gradients (Sobel, reflect-101)")
    for j, name in enumerate(("c0", "c1", "c2")):
        s += mono(xa + j * cs + cs / 2, y0 - 7, name, size=7.5, fill=SOFT)
    rows = (1, 2, 3)
    for i, r in enumerate(rows):
        s += mono(xa - 8, y0 + i * cs + cs / 2 + 3, f"r{r}", size=7.5, fill=SOFT, anchor="end")
        for j, c in enumerate((0, 1, 2)):
            x, y = xa + j * cs, y0 + i * cs
            s += shade_rect(x, y, cs, cs, PATCH[r][c] / 255)
            g = (GX[r][c], GY[r][c])
            m = math.hypot(*g)
            col = ink_for(PATCH[r][c] / 255)
            if m:
                L = 0.62 * cs * math.sqrt(m / 640)
                cx, cy = x + cs / 2, y + cs / 2
                s += arrow(cx - g[0] / m * L / 2, cy - g[1] / m * L / 2, cx + g[0] / m * L / 2, cy + g[1] / m * L / 2,
                           "#ffffff" if col == "#ffffff" else INK)
                s += mono(x + cs / 2, y + cs - 6, f"({g[0]}, {g[1]})".replace("-", "−"), size=6.8, fill=col)
            else:
                s += mono(x + cs / 2, y + cs / 2 + 4, "0", size=10, fill=col if (r, c) != (2, 1) else ACCENT, weight="600")
    # panel b: vectors tip to tail
    bx, by, sc = 360, 150, 0.105
    s += title(330, 92, "summed as vectors")
    order = [(1, 0), (1, 1), (1, 2), (2, 2), (3, 0), (3, 1), (3, 2)]
    x, y = bx, by
    for (r, c) in order:
        g = (GX[r][c], GY[r][c])
        x2, y2 = x + g[0] * sc, y + g[1] * sc
        s += arrow(x, y, x2, y2, LINK if g[0] == 0 else MUTED, sw=1.4)
        x, y = x2, y2
    s += arrow(bx, by - 26, bx + 1060 * sc, by - 26, ACCENT, sw=2.2)
    s += dot(bx, by, 2.6, fill=INK)
    s += mono(bx + 1060 * sc / 2, by - 34, "sum (1,060, 0)", size=8, fill=ACCENT, weight="600")
    s += note_lines(330, 300, [("the vertical parts cancel:", LINK), ("430 + 430 + 215 down,", MUTED),
                               ("430 + 430 + 215 up", MUTED), ("the step's Gx survives", MUTED)])
    # panel c: doubled angles from a common origin
    cx0, cy0, sd = 900, 170, 1 / 3200
    s += title(640, 92, "summed as doubled angles: (Gx² − Gy², 2GxGy)")
    x, y = cx0, cy0
    for (r, c) in [(1, 0), (1, 1), (3, 0), (3, 1), (1, 2), (2, 2), (3, 2)]:
        gx, gy = GX[r][c], GY[r][c]
        vx, vy = (gx * gx - gy * gy) * sd, (2 * gx * gy) * sd
        s += arrow(x, y, x + vx, y + vy, LINK if gx == 0 else MUTED, sw=1.4)
        x, y = x + vx, y + vy
    assert abs(x - (cx0 - 426700 * sd)) < 1e-6 and abs(y - cy0) < 1e-6
    s += dot(cx0, cy0, 2.6, fill=INK)
    s += arrow(cx0, cy0 - 26, cx0 - 426700 * sd, cy0 - 26, ACCENT, sw=2.4)
    s += mono(cx0 - 426700 * sd / 2, cy0 - 34, "sum (−426,700, 0)", size=8, fill=ACCENT, weight="600")
    s += note_lines(640, 300, [("opposite gradients now point the same way:", LINK),
                               ("(0, ±430) → (−184,900, 0), four times", MUTED),
                               ("length of the sum = λ1 − λ2 = 426,700", ACCENT),
                               ("total A + C = λ1 + λ2 = 1,237,400", MUTED),
                               ("coherence 426,700 / 1,237,400 = 0.345", INK)])
    s += legend2(vh - 30, vw, [("vertical gradient", LINK, "line"), ("gradient with Gx", MUTED, "line"),
                               ("the sum", ACCENT, "line")])
    return emit("07", "why-squares", "Why the tensor squares before it sums",
                "The impulse window's gradients summed as vectors and as doubled angles. Worked by hand.",
                "orientation", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "all 25 tensors: long axis along the dominant gradient, semi-axes ∝ √λ")
    cs, xa, y0 = 84, 72, 92
    s += labels_rc(xa, y0, cs)
    scale = 36 / math.sqrt(max(max(row) for row in L1))
    for r in range(N):
        for c in range(N):
            x, y = xa + c * cs, y0 + r * cs
            t = PATCH[r][c] / 255
            s += shade_rect(x, y, cs, cs, 0.55 + 0.45 * t, sw=0.6)
            coh = COH[r][c]
            colr = LINK if coh >= 0.9 else (ACCENT if coh < 0.5 else INK)
            s += glyph(x + cs / 2, y + cs / 2, L1[r][c], L2[r][c], TH[r][c], scale, stroke=colr, op=0.16)
            if (r, c) in ((0, 1), (1, 1), (1, 2), (0, 3)):
                s += mono(x + cs - 5, y + cs - 6, f"{TH[r][c]:.1f}°", size=7, fill=INK, anchor="end")
    nx = 520
    s += note_lines(nx, 112, [
        ("columns c0 and c4: rank 1, coherence 1", LINK), ("c0's line is vertical: the mirrored ring", MUTED),
        ("c4's is horizontal: the step alone", MUTED), ("", None),
        ("column c3: nearly rank 1, coherence 0.89–0.96", LINK), ("", None),
        ("column c1: the roundest, coherence 0.23–0.34", ACCENT), ("they tilt with the ring: 49.8° at (r0, c1),", MUTED),
        ("20.0° at (r1, c1), mirrored below r2", MUTED), ("", None),
        ("column c2: 3.2° at (r1, c2), 6.7° at (r0, c2)", INK), ("", None),
        ("angles: θ = ½ atan2(2B, A − C), clockwise", SOFT), ("from +x, image coordinates", SOFT)])
    s += legend2(vh - 30, vw, [("coherence ≥ 0.9", LINK, "ell"), ("0.5 to 0.9", INK, "ell"),
                               ("below 0.5", ACCENT, "ell"), ("rank 1", LINK, "rank1")])
    return emit("08", "orientation-field", "Orientation and coherence across the patch",
                "Every pixel's tensor as an oriented ellipse. Worked by hand.", "orientation", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 392
    s = eyebrow(32, 40, "lucas–kanade on the same matrices: one step, patch moved (1, 0); 1-σ ellipses for σ = 20")
    sig = 20.0
    pw, x0, y0, w, h = 240, 60, 106, 200, 150
    for k, c in enumerate((4, 3, 2, 1)):
        ax = Axes(x0 + k * pw, y0, w, h, (-1.5, 2.5), (-1.5, 1.5))
        cid = f"c9_{k}"
        s += f"<defs>{ax.clip(cid)}</defs>"
        s += ax.frame([-1, 0, 1, 2], [-1, 0, 1], xlab="u (px)", ylab="v (px, down)", xfmt=lambda v: fmt(v, 0),
                      yfmt=lambda v: fmt(-v, 0), grid_y=False)
        s += line(ax.X(0), ax.Y(-1.5), ax.X(0), ax.Y(1.5), stroke=RULE, sw=0.8)
        s += line(ax.X(-1.5), ax.Y(0), ax.X(2.5), ax.Y(0), stroke=RULE, sw=0.8)
        d, _ = lk_one_step(2, c)
        body = ""
        if d is None:
            body += line(ax.X(2.0), ax.y0, ax.X(2.0), ax.y0 + h, stroke=ACCENT, sw=2.4)
        else:
            l1x, l2y = A[2][c] / 64, C[2][c] / 64
            rx = sig / math.sqrt(l1x) * (w / 4)
            ry = sig / math.sqrt(l2y) * (h / 3)
            body += ellipse(ax.X(d[0]), ax.Y(-d[1]), rx, ry, 0, fill=ACCENT, stroke=ACCENT, sw=1.4, op=0.16)
            body += dot(ax.X(d[0]), ax.Y(-d[1]), 3.6, fill=ACCENT, stroke="#ffffff")
        body += ring(ax.X(1), ax.Y(0), 5, stroke=INK)
        s += f'<g clip-path="url(#{cid})">{body}</g>'
        s += title(ax.x0, 74, f"(r2, c{c})", size=9)
        lab = {4: "u = 2.00, v undetermined", 3: "(1.28, 0); v uncertain 4.2×", 2: "(1.28, 0); v uncertain 1.9×",
               1: "(−0.89, 0): wrong way"}[c]
        s += mono(ax.x0, ax.y0 + h + 48, lab, size=8, fill=ACCENT if c in (1, 4) else INK, anchor="start", weight="600")
    s += legend2(vh - 30, vw, [("true motion (1, 0)", INK, "ring"), ("one-step estimate", ACCENT, "dot"),
                               ("1-σ error ellipse", ACCENT, "ell"), ("every point fits: the aperture", ACCENT, "line")])
    return emit("09", "aperture-and-precision", "What each window can say about motion",
                "One Lucas–Kanade step on the patch moved one pixel right, and the error ellipses σ²M⁻¹. "
                "Evaluated from the worked matrices.", "lucas–kanade", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "one row, moved one pixel right: what the linear model predicts against what happens")
    s += title(110, 70, "row r2 of the patch")
    ax = Axes(110, 92, 600, 130, (-0.5, 4.5), (0, 270))
    s += ax.frame([0, 1, 2, 3, 4], [40, 200, 255], ylab="grey level", xfmt=lambda v: f"c{v}", yfmt=lambda v: str(v))
    before = [PATCH[2][c] for c in range(N)]
    after = [I2[2][c] for c in range(N)]

    def steps(vals):
        pts = []
        for c, v in enumerate(vals):
            pts += [(ax.X(c - 0.5), ax.Y(v)), (ax.X(c + 0.5), ax.Y(v))]
        return pts
    s += polyline(steps(before), INK, sw=2.0)
    s += polyline(steps(after), LINK, sw=2.0, dash="5,3")
    s += mono(ax.X(1), ax.Y(255) - 8, "impulse before", size=7.5, fill=INK)
    s += mono(ax.X(2), ax.Y(255) - 8, "after", size=7.5, fill=LINK)
    bx = Axes(110, 290, 600, 140, (-0.5, 4.5), (-280, 280))
    s += bx.frame([0, 1, 2, 3, 4], [-200, -100, 0, 100, 200], ylab="It, grey levels", xfmt=lambda v: f"c{v}",
                  yfmt=lambda v: f"{v:+d}".replace("+0", "0").replace("-", "−"))
    s += line(bx.x0, bx.Y(0), bx.x0 + bx.w, bx.Y(0), stroke=INK, sw=0.9)
    bw = 34
    for c in range(N):
        act = IT[2][c]
        pred = -GX[2][c] / 8
        xa_, xp_ = bx.X(c) - bw - 2, bx.X(c) + 2
        if act:
            y1, y2 = sorted((bx.Y(0), bx.Y(act)))
            s += rect(xa_, y1, bw, y2 - y1, fill=INK, stroke=INK, sw=0.8, op=0.85)
            s += mono(xa_ + bw / 2, (bx.Y(act) - 6) if act > 0 else (bx.Y(act) + 13), fmt(act), size=8, fill=INK, weight="600")
        if pred:
            y1, y2 = sorted((bx.Y(0), bx.Y(pred)))
            s += rect(xp_, y1, bw, y2 - y1, fill=ACCENT, stroke=ACCENT, sw=0.8, op=0.85)
            s += mono(xp_ + bw / 2, bx.Y(pred) + 13, fmt(pred, 2), size=8, fill=ACCENT, weight="600")
    nx = 745
    s += note_lines(nx, 300, [("predicted: −(Gx/8) × u, u = 1", ACCENT), ("actual: after − before", INK), ("", None),
                              ("c2: Gx = 210, the step's slope", MUTED), ("dominates, so the model says", MUTED),
                              ("−26.25; the impulse arrives: +215", ACCENT), ("", None),
                              ("c3: −80 predicted, −160 actual:", MUTED), ("the step moved a whole pixel", MUTED),
                              ("past a 2-pixel-wide slope", MUTED)], gap=15)
    s += note_lines(nx, 110, [("before: 40 255 40 200 200", INK), ("after:  40 40 255 40 200", LINK),
                              ("c0 is refilled with 40", SOFT)], gap=15)
    s += legend2(vh - 30, vw, [("row r2 before", INK, "line"), ("after", LINK, "dash"), ("actual It", INK, "fill"),
                               ("linear prediction", ACCENT, "fill")])
    return emit("10", "linearisation", "When one linear step goes wrong",
                "Row r2 before and after a one-pixel move, and the frame difference against the linear model's "
                "prediction. Worked by hand.", "lucas–kanade", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "the window: its footprint, its weights, and what the weights do to one pixel of the step")
    cs, xa, y0 = 40, 70, 112
    s += title(40, 90, "a 3×3 derivative in a 3×3 window reads 5×5")
    for r in range(N):
        for c in range(N):
            s += shade_rect(xa + c * cs, y0 + r * cs, cs, cs, 0.62 + 0.38 * PATCH[r][c] / 255, sw=0.6)
    s += rect(xa + cs, y0 + cs, 3 * cs, 3 * cs, fill="none", stroke=ACCENT, sw=2.2)
    s += rect(xa + 2, y0 + 2, 3 * cs - 4, 3 * cs - 4, fill="none", stroke=LINK, sw=1.6, dash="4,3")
    s += rect(xa, y0, 5 * cs, 5 * cs, fill="none", stroke=INK, sw=1.2)
    s += mono(xa + 2.5 * cs, y0 + 5 * cs + 18, "window at (r2, c2): orange", size=8, fill=ACCENT)
    s += mono(xa + 2.5 * cs, y0 + 5 * cs + 32, "Sobel support of its corner pixel: blue", size=8, fill=LINK)
    s += mono(xa + 2.5 * cs, y0 + 5 * cs + 46, "the union: the whole patch", size=8, fill=INK)

    def weights(x0, wts, lab):
        out = title(x0, 90, lab)
        for i in range(3):
            for j in range(3):
                v = wts[i][j]
                t = 0.12 + 0.88 * v / GAUSS[1][1]          # one scale for both grids; heavier = brighter
                out += shade_rect(x0 + j * 50, y0 + i * 50, 50, 50, t)
                out += mono(x0 + j * 50 + 25, y0 + i * 50 + 29, f"{v:.4f}", size=8.5, fill=ink_for(t), weight="500")
        return out
    s += weights(330, [[1 / 9] * 3 for _ in range(3)], "box, as a mean: 1/9 each")
    s += weights(520, GAUSS, "the series' Gaussian (σ = 0.8)")
    s += mono(330, y0 + 170, "corners count as much as the centre", size=8, fill=MUTED, anchor="start")
    s += mono(330, y0 + 186, "shading: heavier weight is brighter, one scale", size=8, fill=SOFT, anchor="start")
    s += mono(520, y0 + 170, "corners 0.0571, centre 0.2725", size=8, fill=MUTED, anchor="start")
    # ratio axis
    ax = Axes(720, 150, 250, 60, (0, 0.08), (0, 1))
    s += title(720, 90, "(r2, c3): λ2 / λ1 under each window")
    s += line(ax.x0, ax.Y(0), ax.x0 + ax.w, ax.Y(0), stroke=RULE_SOLID)
    for v in (0, 0.02, 0.04, 0.06, 0.08):
        s += line(ax.X(v), ax.Y(0), ax.X(v), ax.Y(0) + 4, stroke=RULE_SOLID)
        s += mono(ax.X(v), ax.Y(0) + 16, f"{v:g}", size=8, fill=SOFT)
    for k, dash in ((0.04, None), (0.06, "5,3")):
        x = ax.X(tstar(k))
        s += line(x, ax.y0 - 6, x, ax.Y(0), stroke=ACCENT, sw=1.4, dash=dash)
    s += mono(ax.X(tstar(0.04)), ax.y0 - 12, "k .04", size=7.5, fill=ACCENT, anchor="end")
    s += mono(ax.X(tstar(0.06)), ax.y0 - 12, "k .06", size=7.5, fill=ACCENT, anchor="start")
    rb = L2[2][3] / L1[2][3]
    rg = min(AG[2][3], CG[2][3]) / max(AG[2][3], CG[2][3])
    s += dot(ax.X(rb), ax.Y(0.55), 4.4, fill=INK, stroke="#ffffff")
    s += mono(ax.X(rb), ax.Y(0.55) - 9, f"box {rb:.3f}", size=8, fill=INK, weight="600")
    s += dot(ax.X(rg), ax.Y(0.2), 4.4, fill=LINK, stroke="#ffffff")
    s += mono(ax.X(rg), ax.Y(0.2) - 9, f"Gaussian {rg:.3f}", size=8, fill=LINK, weight="600")
    s += note_lines(720, 262, [("box: between the two Harris boundaries,", INK), ("a corner at 0.04, an edge at 0.06", MUTED),
                               ("Gaussian: below both, an edge", LINK), ("for either k", MUTED), ("", None),
                               ("the ring's two pixels sit in the", MUTED), ("window's corners: weight 1 of 9", MUTED),
                               ("in the box, 0.0571 in the Gaussian", MUTED)], gap=15)
    s += legend2(vh - 30, vw, [("3×3 window", ACCENT, "outline"), ("one pixel's Sobel support", LINK, "dashbox"),
                               ("box window", INK, "dot"), ("Gaussian window", LINK, "dot"), ("Harris k = 0.04", ACCENT, "line"),
                               ("k = 0.06", ACCENT, "dash")])
    return emit("11", "window-and-weights", "The window: footprint and weights",
                "Why no window on the patch is flat, and how the window's weights move (r2, c3) across the "
                "Harris boundary. Worked by hand.", "window and scale", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 590
    s = eyebrow(32, 40, "one matrix, three libraries: mapped from source and documentation, not run")
    cols = [("", 32), ("OpenCV", 196), ("scikit-image", 470), ("MATLAB", 752)]
    y0 = 76
    for h, x in cols:
        s += mono(x, y0, h, size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, y0 + 10, vw - 32, y0 + 10, stroke=RULE_SOLID)
    rows = [
        ("derivative", "Sobel, ksize 3 (Scharr if −1)", "SciPy Sobel on a 0–1 image", "not documented"),
        ("window", "box, blockSize × blockSize", "Gaussian, σ = 1, cut at 4σ", "Gaussian 5×5, σ = 5/3"),
        ("border", "reflect-101", "zeros (mode constant)", "not documented"),
        ("Harris k", "required; 0.04 in goodFeatures", "0.05", "not documented"),
        ("units", "mean of (Sobel/1,020)² at 3, 3", "Gaussian mean of (Sobel/255)²", "not documented"),
        ("selection", "3×3 maxima > qualityLevel × max", "corner_peaks, min_distance 1", "MinQuality 0.01 of max"),
        ("image border", "1-px ring never returned", "1-px border excluded", "not documented"),
        ("Förstner", "—", "corner_foerstner → (w, q)", "—"),
        ("flow", "PyrLK: sparse, 21×21, 3 levels", "optical_flow_ilk: dense, 15×15", "opticalFlowLK: dense, one scale"),
        ("weak windows", "minEig/N < 1e-4 → status 0", "|det| < 1e-14 → zero flow", "NoiseThreshold 0.0039"),
        ("which code", "IPP for Harris only with", "—", "—"),
    ]
    for k, (what, a, b, c) in enumerate(rows):
        y = y0 + 34 + k * 40
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 18}" width="{vw - 56}" height="40" fill="rgba(45,49,66,0.03)"/>'
        s += mono(32, y + 4, what, size=8, fill=SOFT, anchor="start", track="0.08em", weight="600")
        for txt_, x in ((a, 196), (b, 470), (c, 752)):
            trap = txt_.startswith(("box,", "required", "1-px ring", "zeros", "minEig/N"))
            s += mono(x, y + 4, txt_, size=8.5, fill=ACCENT if trap else (SOFT if txt_ in ("not documented", "—") else INK),
                      anchor="start", weight="600" if trap else "400")
        if what == "which code":
            s += mono(196, y + 17, "constant/replicate borders", size=8.5, fill=INK, anchor="start")
    s += mono(32, vh - 16, "pinned: OpenCV 802cf95 (4.10.0 checked), scikit-image b700edc; MATLAB from MathWorks' pages, "
              "release R2026b. Orange marks the behaviour most likely to surprise.", size=8, fill=SOFT, anchor="start")
    return emit("12", "tooling-map", "The tooling map",
                "Derivative, window, border, k, units, selection and flow defaults in OpenCV, scikit-image and "
                "MATLAB. None of it was executed.", "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10, "11": fig11, "12": fig12}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
