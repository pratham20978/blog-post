#!/usr/bin/env python3
"""Figures 01-11 for canny-line-by-line.

Every value drawn here is computed in this file, from the definitions, on the series'
5x5 patch: the 3x3 Sobel under cv2.Canny's replicate border, OpenCV's four-bin
suppression rule (transcribed from canny.simd.hpp at commit 802cf95), scikit-image's
interpolated rule (from _canny_cy.pyx at commit b700edc), hysteresis as 8-connected
components with strict comparisons, the shared 3x3 Gaussian with reflect-101 borders,
Devernay's parabola, OpenCV's Sobel kernel generator, and the closed-form noise model.
Nothing is measured and nothing loads an image. The asserts below hold the figures to
the article's numbers. Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SOFT,
                    emit, eyebrow, hline, mono, txt)

SER1, SER2, SER3, SER4 = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50"

# ------------------------------------------------------------------ the data
N = 5
PATCH = [[40, 40, 40, 200, 200] for _ in range(N)]
PATCH[2][1] = 255


def pad(i, mode):
    if 0 <= i < N:
        return i
    if mode == "replicate":
        return 0 if i < 0 else N - 1
    return -i if i < 0 else 2 * (N - 1) - i          # reflect-101


def px(M, r, c, mode):
    return M[pad(r, mode)][pad(c, mode)]


def sobel(M, mode="replicate"):
    gx = [[sum(w * (px(M, r + d, c + 1, mode) - px(M, r + d, c - 1, mode)) for d, w in ((-1, 1), (0, 2), (1, 1)))
           for c in range(N)] for r in range(N)]
    gy = [[sum(w * (px(M, r + 1, c + d, mode) - px(M, r - 1, c + d, mode)) for d, w in ((-1, 1), (0, 2), (1, 1)))
           for c in range(N)] for r in range(N)]
    return gx, gy


def l2(gx, gy):
    return [[math.hypot(gx[r][c], gy[r][c]) for c in range(N)] for r in range(N)]


def l1(gx, gy):
    return [[abs(gx[r][c]) + abs(gy[r][c]) for c in range(N)] for r in range(N)]


TG22 = 13573                                          # canny.simd.hpp: tan 22.5 deg * 2^15


def bin_of(xs, ys):
    x, y = abs(xs), abs(ys) * 32768
    t = x * TG22
    if y < t:
        return "H"
    if y > t + x * 65536:
        return "V"
    return "D+" if (xs >= 0) == (ys >= 0) else "D-"


def nms_opencv(gx, gy, M, low=0.0):
    """canny_nms_row: > before and >= after for H and V, > both for diagonals; 0 outside."""
    def m(r, c):
        return M[r][c] if 0 <= r < N and 0 <= c < N else 0

    keep, bins = set(), {}
    for r in range(N):
        for c in range(N):
            b = bin_of(gx[r][c], gy[r][c])
            bins[(r, c)] = b
            v = M[r][c]
            if not v > low:
                continue
            if b == "H":
                ok = v > m(r, c - 1) and v >= m(r, c + 1)
            elif b == "V":
                ok = v > m(r - 1, c) and v >= m(r + 1, c)
            else:
                s = 1 if b == "D+" else -1
                ok = v > m(r - 1, c - s) and v > m(r + 1, c + s)
            if ok:
                keep.add((r, c))
    return keep, bins


def nms_interp(gx, gy, M):
    """_nonmaximum_suppression_bilinear: keep when both interpolated neighbours <= m; 0 outside."""
    def m(r, c):
        return M[r][c] if 0 <= r < N and 0 <= c < N else 0.0

    keep, detail = set(), {}
    for x in range(N):
        for y in range(N):
            v = M[x][y]
            if not v >= 1e-14:
                continue
            i, j = gy[x][y], gx[x][y]
            up, down, left, right = i >= 0, i <= 0, j <= 0, j >= 0
            c1 = (up and right) or (down and left)
            c2 = (down and right) or (up and left)
            ai, aj = abs(i), abs(j)
            if c1:
                if ai > aj:
                    w, a1, a2, b1, b2 = aj / ai, m(x + 1, y), m(x + 1, y + 1), m(x - 1, y), m(x - 1, y - 1)
                else:
                    w, a1, a2, b1, b2 = ai / aj, m(x, y + 1), m(x + 1, y + 1), m(x, y - 1), m(x - 1, y - 1)
            elif c2:
                if ai < aj:
                    w, a1, a2, b1, b2 = ai / aj, m(x, y + 1), m(x - 1, y + 1), m(x, y - 1), m(x + 1, y - 1)
                else:
                    w, a1, a2, b1, b2 = aj / ai, m(x - 1, y), m(x - 1, y + 1), m(x + 1, y), m(x + 1, y - 1)
            else:
                continue
            ahead, behind = a2 * w + a1 * (1 - w), b2 * w + b1 * (1 - w)
            detail[(x, y)] = (w, ahead, behind)
            if ahead <= v and behind <= v:
                keep.add((x, y))
    return keep, detail


def components(S):
    S, seen, out = set(S), set(), []
    for p in sorted(S):
        if p in seen:
            continue
        stack, comp = [p], set()
        seen.add(p)
        while stack:
            r, c = stack.pop()
            comp.add((r, c))
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    q = (r + dr, c + dc)
                    if q in S and q not in seen:
                        seen.add(q)
                        stack.append(q)
        out.append(comp)
    return out


def hysteresis(keep, M, low, high):
    cand = {p for p in keep if M[p[0]][p[1]] > low}
    out = set()
    for comp in components(cand):
        if any(M[r][c] > high for r, c in comp):
            out |= comp
    return out


W1 = math.exp(-1 / (2 * 0.64))
K3 = [W1 / (1 + 2 * W1), 1 / (1 + 2 * W1), W1 / (1 + 2 * W1)]


def blur(M):
    t = [[sum(K3[d + 1] * M[r][pad(c + d, "reflect101")] for d in (-1, 0, 1)) for c in range(N)] for r in range(N)]
    return [[sum(K3[d + 1] * t[pad(r + d, "reflect101")][c] for d in (-1, 0, 1)) for c in range(N)] for r in range(N)]


def devernay(a, b, c):
    return 0.5 * (a - c) / (a + c - 2 * b)


def sobel_kernels(ksize, order):
    """deriv.cpp getSobelKernels."""
    if ksize == 3:
        return {0: [1, 2, 1], 1: [-1, 0, 1]}[order]
    k = [1] + [0] * ksize
    for _ in range(ksize - order - 1):
        k = [k[0]] + [k[j] + k[j - 1] for j in range(1, ksize + 1)]
    for _ in range(order):
        k = [-k[0]] + [k[j - 1] - k[j] for j in range(1, ksize + 1)]
    return k[:ksize]


def gains(d, s):
    half = len(d) // 2
    step = sum(d[i] for i in range(len(d)) if i > half) * sum(s)
    ramp = sum(d[i] * (i - half) for i in range(len(d))) * sum(s)
    return step, ramp


# raw patch, as cv2.Canny computes it
GX, GY = sobel(PATCH, "replicate")
M2, M1 = l2(GX, GY), l1(GX, GY)
KEEP2, BINS = nms_opencv(GX, GY, M2)
KEEP1, _ = nms_opencv(GX, GY, M1)
KEEPI, _ = nms_interp(GX, GY, M2)
LINE2 = {(0, 2), (1, 3), (2, 3), (3, 3), (4, 2)}
RING = {(1, 0), (1, 1), (2, 0), (3, 0), (3, 1)}
LINE1 = {(0, 2), (2, 3), (4, 2)}

# smoothed patch
SM = blur(PATCH)
SGX, SGY = sobel(SM, "replicate")
SM2, SM1 = l2(SGX, SGY), l1(SGX, SGY)
SKEEP2, SBINS = nms_opencv(SGX, SGY, SM2)
SKEEP1, _ = nms_opencv(SGX, SGY, SM1)
SKEEPI, SDET = nms_interp(SGX, SGY, SM2)
COL = {(r, 3) for r in range(N)}


def r1(v, nd=1):
    return round(v + 0.0, nd)


# ------------------------------------------------------------------ the article's numbers
assert GX == [[0, 0, 640, 640, 0], [215, 0, 425, 640, 0], [430, 0, 210, 640, 0], [215, 0, 425, 640, 0],
              [0, 0, 640, 640, 0]]
assert GY[1] == [215, 430, 215, 0, 0] and GY[3] == [-215, -430, -215, 0, 0] and GY[0] == GY[2] == GY[4] == [0] * 5
assert [r1(v) for v in M2[1]] == [304.1, 430.0, 476.3, 640.0, 0.0] and M1[1][2] == 640 and M1[1][0] == 430
assert GX[2][1] == GY[2][1] == 0
assert sobel(PATCH, "reflect101")[0][2][0] == 0                       # reflect-101 zero at (r2, c0)
assert r1(math.degrees(math.atan2(GY[1][2], GX[1][2]))) == 26.8 and BINS[(1, 2)] == "D+" and BINS[(1, 3)] == "H"
assert KEEP2 == LINE2 | RING and KEEP1 == LINE1 | RING
assert KEEPI == KEEP2 | {(0, 3), (4, 3)}
assert len(components(KEEP2)) == 1 and len(components(KEEP1)) == 2
assert hysteresis(KEEP2, M2, 450, 600) == LINE2 and hysteresis(KEEP2, M2, 180, 450) == KEEP2
assert hysteresis(KEEP2, M2, 304.1, 600) == LINE2 | {(1, 1), (2, 0), (3, 1)}
assert hysteresis(KEEP1, M1, 450, 600) == LINE1 and len(hysteresis(KEEP1, M1, 200, 600)) == 8
assert r1(640 / 430, 2) == 1.49
assert [r1(v, 2) for v in SM[0]] == [40.0, 40.0, 78.24, 161.76, 200.0]
assert [r1(v, 2) for v in SM[1]] == [64.56, 66.82, 90.52, 161.76, 200.0]
assert [r1(v, 2) for v in SM[2]] == [93.65, 98.59, 105.06, 161.76, 200.0]
assert [r1(v) for v in SM2[0]] == [100.5, 167.3, 463.1, 474.9, 153.0]
assert [r1(v) for v in SM2[1]] == [219.7, 222.2, 391.3, 436.5, 153.0]
assert [r1(v) for v in SM2[2]] == [14.4, 74.7, 316.2, 408.8, 153.0]
assert SKEEP2 == COL | {(1, 0), (3, 0)} and SKEEPI == SKEEP2 | {(1, 1), (3, 1)}
assert SKEEP1 == {(0, 2), (1, 2), (2, 3), (3, 2), (4, 2), (1, 0), (3, 0)}
assert r1(SM1[1][0]) == 229.0 and r1(SM1[0][2]) == 511.6 and r1(SM1[1][2]) == 487.0
_w, _ahead, _behind = SDET[(1, 1)]
assert (r1(_w, 3), r1(_ahead), r1(_behind)) == (0.514, 198.8, 133.0) and SBINS[(1, 1)] == "D+"
assert r1(math.degrees(math.atan2(SGY[1][1], SGX[1][1]))) == 62.8
assert hysteresis(SKEEP2, SM2, 180, 450) == COL and hysteresis(SKEEPI, SM2, 180, 450) == COL
SMR = [[math.floor(v + 0.5) for v in row] for row in SM]                 # whole grey levels
_rx, _ry = sobel(SMR, "replicate")
assert nms_opencv(_rx, _ry, l2(_rx, _ry))[0] == SKEEP2
assert [r1(devernay(M2[r][c - 1], M2[r][c], M2[r][c + 1] if c + 1 < N else 0), 2) + c
        for r, c in ((0, 2), (1, 3), (2, 3))] == [2.5, 2.7, 2.9]
assert [r1(c + devernay(SM2[r][c - 1], SM2[r][c], SM2[r][c + 1]), 2) for r, c in ((0, 3), (1, 3), (2, 3))] == \
    [2.54, 2.64, 2.77]
KER = {k: (sobel_kernels(k, 1), sobel_kernels(k, 0)) for k in (3, 5, 7)}
KER[-1] = ([-1, 0, 1], [3, 10, 3])
assert KER[5] == ([-1, -2, 0, 2, 1], [1, 4, 6, 4, 1]) and KER[7] == ([-1, -4, -5, 0, 5, 4, 1], [1, 6, 15, 20, 15, 6, 1])
GAIN = {k: gains(*KER[k]) for k in KER}
assert GAIN == {3: (4, 8), 5: (48, 128), 7: (640, 2048), -1: (16, 32)}
assert r1(math.sqrt(12), 3) == 3.464
S_SMOOTH = math.sqrt(sum(v * v for v in [-K3[0], -K3[1], K3[0] - K3[2], K3[1], K3[2]]) *
                     sum(v * v for v in [K3[0], 2 * K3[0] + K3[1], K3[0] + 2 * K3[1] + K3[2], K3[1] + 2 * K3[2], K3[2]]))
assert r1(S_SMOOTH, 3) == 1.709
SIG = 2.0
S_NOISE = math.sqrt(12) * SIG
TH = S_NOISE * math.sqrt(2 * math.log(1e4))
TL = TH / 2
assert (r1(S_NOISE, 2), r1(TH), r1(TH / 4), r1(TL)) == (6.93, 29.7, 7.4, 14.9)
assert r1(math.exp(-TL ** 2 / (2 * S_NOISE ** 2)), 2) == 0.10 and r1(1e-4 ** (1 / 9), 2) == 0.36
assert (r1(math.sqrt(2 * math.log(1e3)), 2), r1(math.sqrt(2 * math.log(1e4)), 2)) == (3.72, 4.29)
assert (r1(math.sqrt(2 * math.log(2)), 3), r1(math.sqrt(-2 * math.log(0.2)), 3)) == (1.177, 1.794)
AC = math.sqrt(2 * math.log(1e6))
assert (r1(AC, 2), r1(AC / 2, 2), r1(AC / 3, 2)) == (5.26, 2.63, 1.75)
ANG12 = math.degrees(math.atan2(GY[1][2], GX[1][2]))                   # 26.83 degrees
assert r1(math.cos(math.radians(ANG12)) + math.sin(math.radians(ANG12)), 3) == r1(640 / M2[1][2], 3) == 1.344
_vals = sorted(r1(v) for row in M2 for v in row)
assert sum(1 for v in _vals if v > 0) == 15 and _vals[19] == 640.0
_e3 = [row[:] for row in PATCH]
_e3[2][1] = 120
_ex, _ey = sobel(_e3, "replicate")
_e2 = l2(_ex, _ey)
assert (_e2[1][1], _e2[2][0], r1(_e2[1][0]), r1(_e2[1][2])) == (160, 160, 113.1, 565.7)
assert hysteresis(nms_opencv(_ex, _ey, _e2)[0], _e2, 200, 600) == LINE2
assert (GX[3][2], GY[3][2], BINS[(3, 2)]) == (425, -215, "D-") and (3, 2) not in KEEP2


# ------------------------------------------------------------------ drawing helpers
def fmt(v, nd=1):
    if abs(v - round(v)) < 1e-9:
        s = f"{round(v):,}"
    else:
        s = f"{v:.{nd}f}"
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


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, marker=None, cap=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    c = f' stroke-linecap="{cap}"' if cap else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{m}{c}/>')


def polyline(pts, stroke, sw=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}/>')


def polygon(pts, fill, stroke="none", sw=0.8, op=None):
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None):
    s = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{s}/>'


def diamond(x, y, rr=5, fill=LINK):
    return polygon([(x, y - rr), (x + rr, y), (x, y + rr), (x - rr, y)], fill, stroke="#ffffff", sw=1.0)


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
    """Legend whose swatches are drawn exactly like the marks they name.
    item: (label, colour, kind) with kind in line | dash | dot | fill | tint | hollow | bridge."""
    s = (f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>')
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for item in items:
        label, colour, kind = item[:3]
        op = item[3] if len(item) > 3 else None
        if kind in ("line", "dash"):
            d = ' stroke-dasharray="5,3"' if kind == "dash" else ""
            s += (f'<line x1="{x}" y1="{y + 5}" x2="{x + 18}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.8"{d}/>')
        elif kind == "dot":
            s += dot(x + 8, y + 5, 4, fill=colour)
        elif kind == "fill":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke=colour, sw=0.8, op=op or 0.85)
        elif kind == "tint":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke=colour, sw=1.2, op=op or 0.16)
        elif kind == "area":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke="none", sw=0, op=op)
        elif kind == "plain":
            s += rect(x, y - 1, 16, 12, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8)
        elif kind == "outline":
            s += rect(x, y - 1, 16, 12, fill="none", stroke=colour, sw=1.8)
        elif kind == "diamond":
            s += diamond(x + 8, y + 5, 5, fill=colour)
        elif kind == "hollow":
            s += rect(x, y - 1, 16, 12, fill="#ffffff", stroke=colour, sw=1.2, dash="3,2")
        elif kind == "bridge":
            s += line(x + 2, y + 5, x + 16, y + 5, stroke=colour, sw=4, cap="round")
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


def labels_rc(x, y, cs, n=N):
    s = ""
    for j in range(n):
        s += mono(x + j * cs + cs / 2, y - 7, f"c{j}", size=7.5, fill=SOFT)
    for i in range(n):
        s += mono(x - 8, y + i * cs + cs / 2 + 3, f"r{i}", size=7.5, fill=SOFT, anchor="end")
    return s


MARKS = f"""<defs>
    <marker id="aw" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#ffffff"/></marker>
    <marker id="ai" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{INK}"/></marker>
    <marker id="al" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
    <marker id="aa" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
  </defs>"""


def glyph(cx, cy, b, half=6, stroke=MUTED):
    """The direction a bin compares along (the gradient direction, quantised)."""
    d = {"H": (1, 0), "V": (0, 1), "D+": (0.7071, 0.7071), "D-": (0.7071, -0.7071)}[b]
    return line(cx - half * d[0], cy - half * d[1], cx + half * d[0], cy + half * d[1], stroke=stroke, sw=1.4,
                cap="round")


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 470
    s = MARKS + eyebrow(32, 40, "the patch's sobel gradient: replicate border, no smoothing, as cv2.canny computes it")
    cs, xa, xb, y0 = 60, 64, 436, 112
    s += title(xa - 32, 86, "the patch, with each pixel's gradient vector")
    s += title(xb - 32, 86, "L2 magnitude; L1 where it differs")
    s += labels_rc(xa, y0, cs) + labels_rc(xb, y0, cs)
    for r in range(N):
        for c in range(N):
            x, y = xa + c * cs, y0 + r * cs
            t = PATCH[r][c] / 255
            s += shade_rect(x, y, cs, cs, t)
            col = ink_for(t)
            s += mono(x + 5, y + 12, str(PATCH[r][c]), size=7.5, fill=col, anchor="start")
            m = M2[r][c]
            cx, cy = x + cs / 2, y + cs / 2 + 4
            if m == 0:
                if (r, c) == (2, 1):
                    s += mono(cx, cy + 4, "0", size=11, fill=ACCENT, weight="600")
                continue
            L = 0.68 * cs * math.sqrt(m / 640)
            ux, uy = GX[r][c] / m, GY[r][c] / m
            s += line(cx - ux * L / 2, cy - uy * L / 2, cx + ux * L / 2, cy + uy * L / 2, stroke=col, sw=1.5,
                      marker="aw" if col == "#ffffff" else "ai")
    s += rect(xa + cs, y0 + 2 * cs, cs, cs, fill="none", stroke=ACCENT, sw=2)
    for r in range(N):
        for c in range(N):
            x, y = xb + c * cs, y0 + r * cs
            m = M2[r][c]
            t = m / 640
            s += shade_rect(x, y, cs, cs, t)
            col = ink_for(t)
            if M1[r][c] != m:
                s += mono(x + cs / 2, y + cs / 2 - 1, fmt(m), size=10, fill=col, weight="500")
                s += mono(x + cs / 2, y + cs / 2 + 14, f"L1 {fmt(M1[r][c])}", size=7.5, fill=col)
            else:
                s += mono(x + cs / 2, y + cs / 2 + 4, fmt(m), size=10, fill=col, weight="500")
    s += rect(xb + 2 * cs + 1.5, y0 + cs + 1.5, cs - 3, cs - 3, fill="none", stroke=ACCENT, sw=1.8, dash="4,3")
    s += rect(xb + 1.5, y0 + 2 * cs + 1.5, cs - 3, cs - 3, fill="none", stroke=LINK, sw=1.8, dash="4,3")
    nx = 790
    s += note_lines(nx, 128, [
        ("the step reads 640 = 4 × 160", LINK), ("on c2 and c3 at once: a tie", MUTED), ("", None),
        ("the impulse's own pixel: 0", ACCENT), ("its left and right columns", MUTED),
        ("cancel, and so do the rows", MUTED), ("above and below it", MUTED), ("", None),
        ("(r1, c2): L2 476.3, L1 640", ACCENT), ("", None),
        ("(r2, c0): 430 with replicate,", LINK), ("0 with reflect-101", MUTED)])
    s += mono(32, vh - 22, "arrows point from dark to bright; their length grows with the magnitude. "
              "Gx is the right column minus the left, rows weighted 1, 2, 1; Gy the same, turned.", size=8, fill=SOFT, anchor="start")
    return emit("01", "patch-gradient", "The patch's Sobel gradient",
                "Gx, Gy and the magnitude under cv2.Canny's replicate border, no smoothing. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def nms_grid(x0, y0, cs, M, keep, gap=None):
    s = labels_rc(x0, y0, cs)
    for r in range(N):
        for c in range(N):
            x, y = x0 + c * cs, y0 + r * cs
            m = M[r][c]
            if (r, c) in keep:
                colr = LINK if (r, c) in LINE2 else ACCENT
                s += rect(x, y, cs, cs, fill=colr, stroke=colr, sw=1.0, op=0.85)
                s += mono(x + cs / 2, y + cs / 2 + 8, fmt(m), size=9.5, fill="#ffffff", weight="600")
                gcol = "#ffffff"
            else:
                s += rect(x, y, cs, cs, fill="#ffffff")
                s += mono(x + cs / 2, y + cs / 2 + 8, fmt(m), size=9, fill=SOFT if m else RULE_SOLID)
                gcol = SOFT
            if m:
                s += glyph(x + cs / 2, y + 14, BINS[(r, c)], stroke=gcol)
    for (r, c) in gap or ():
        s += rect(x0 + c * cs + 2, y0 + r * cs + 2, 2 * cs - 4, cs - 4, fill="none", stroke=ACCENT, sw=1.8, dash="4,3")
    return s


def fig02():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "non-maximum suppression on the raw patch, opencv's four-bin rule")
    cs, xa, xb, y0 = 56, 64, 408, 116
    s += title(xa - 32, 90, "L2 magnitude (L2gradient=True)")
    s += title(xb - 32, 90, "L1 magnitude (OpenCV's default)")
    s += nms_grid(xa, y0, cs, M2, KEEP2)
    s += nms_grid(xb, y0, cs, M1, KEEP1, gap=[(1, 2), (3, 2)])
    s += mono(xa + 2.5 * cs, y0 + 5 * cs + 26, "line on every row: 5 + a ring of 5", size=8.5, fill=LINK, weight="600")
    s += mono(xb + 2.5 * cs, y0 + 5 * cs + 26, "rows r1 and r3 lose the edge: 3 + 5", size=8.5, fill=ACCENT,
              weight="600")
    nx = 744
    s += note_lines(nx, 130, [
        ("each pixel must beat its two", INK), ("neighbours along its bin:", INK),
        ("> the one before, ≥ the one after", MUTED), ("(> both, on the diagonals)", MUTED), ("", None),
        ("L2: (r1, c3) beats 476.3 on", LINK), ("its left and survives", LINK), ("", None),
        ("L1: (r1, c2) reads 425 + 215 = 640", ACCENT), ("and ties (r1, c3), which fails >;", MUTED),
        ("(r1, c2) loses its diagonal test", MUTED), ("to (r2, c3) = 640", MUTED)])
    s += legend2(vh - 40, vw, [("survives, step's line", LINK, "fill"), ("survives, from impulse", ACCENT, "fill"),
                               ("suppressed", SOFT, "plain"), ("the tie that costs a row", ACCENT, "hollow"),
                               ("bin compared", SOFT, "line")])
    return emit("02", "suppression-l2-l1", "Suppression on the raw patch, L2 against L1",
                "OpenCV's rule on the raw patch's gradient with each norm. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def bridges(x0, y0, cs, S, colour_of):
    s = ""
    S = sorted(S)
    for a in range(len(S)):
        for b in range(a + 1, len(S)):
            (r, c), (q, d) = S[a], S[b]
            if max(abs(r - q), abs(c - d)) != 1:
                continue
            col = colour_of((r, c), (q, d))
            ex = x0 + (max(c, d) if c != d else c + 0.5) * cs
            ey = y0 + (max(r, q) if r != q else r + 0.5) * cs
            if r == q:
                s += line(ex - 7, ey, ex + 7, ey, stroke=col, sw=4.5, cap="round")
            elif c == d:
                s += line(ex, ey - 7, ex, ey + 7, stroke=col, sw=4.5, cap="round")
            else:
                sgn = 1 if (d - c) * (q - r) > 0 else -1
                s += line(ex - 6, ey - 6 * sgn, ex + 6, ey + 6 * sgn, stroke=col, sw=4.5, cap="round")
    return s


def hyst_grid(x0, y0, cs, M, keep, low, high, ring_like):
    out = hysteresis(keep, M, low, high)
    s = labels_rc(x0, y0, cs)
    for r in range(N):
        for c in range(N):
            x, y = x0 + c * cs, y0 + r * cs
            p = (r, c)
            if p not in keep:
                s += rect(x, y, cs, cs, fill="#ffffff", stroke="rgba(45,49,66,0.16)")
                continue
            m = M[r][c]
            if m > high:
                s += rect(x, y, cs, cs, fill=LINK, stroke=LINK, sw=1.0, op=0.85)
                s += mono(x + cs / 2, y + cs / 2 + 4, fmt(m), size=9.5, fill="#ffffff", weight="600")
            elif p in out:
                colr = ACCENT if p in ring_like else LINK
                s += rect(x, y, cs, cs, fill=colr, stroke=colr, sw=1.4, op=0.16)
                s += mono(x + cs / 2, y + cs / 2 + 4, fmt(m), size=9.5, fill=colr, weight="600")
            else:
                s += rect(x, y, cs, cs, fill="#ffffff", stroke=SOFT, sw=1.0, dash="3,2")
                s += mono(x + cs / 2, y + cs / 2 + 4, fmt(m), size=9, fill=SOFT)
    col = lambda a, b: ACCENT if (a in ring_like) != (b in ring_like) else (LINK if a in out and b in out else SOFT)
    s += bridges(x0, y0, cs, keep, col)
    return s, out


def fig03():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "hysteresis with high 450 and low 180, a ratio of 2.5, before and after smoothing")
    cs, xa, xb, y0 = 56, 64, 408, 116
    s += title(xa - 32, 90, "raw patch, L2: the survivors of figure 2")
    s += title(xb - 32, 90, "after the shared 3×3 Gaussian, L2")
    g, out_a = hyst_grid(xa, y0, cs, M2, KEEP2, 180, 450, RING)
    s += g
    g, out_b = hyst_grid(xb, y0, cs, SM2, SKEEP2, 180, 450, {(1, 0), (3, 0)})
    s += g
    assert out_a == KEEP2 and out_b == COL
    s += mono(xa + 2.5 * cs, y0 + 5 * cs + 26, "10 pixels out: the ring rides in", size=8.5, fill=ACCENT, weight="600")
    s += mono(xb + 2.5 * cs, y0 + 5 * cs + 26, "5 pixels out: the line alone", size=8.5, fill=LINK, weight="600")
    nx = 744
    s += note_lines(nx, 130, [
        ("raw: one 8-connected chain.", INK), ("(r1, c1) touches (r0, c2) at a", MUTED),
        ("corner, (r3, c1) touches (r4, c2);", MUTED), ("every ring pixel is above 180", MUTED),
        ("", None), ("smoothed: the ring is two", INK), ("pixels of 219.7, two columns", MUTED),
        ("from the line, with no seed:", MUTED), ("both are dropped", MUTED), ("", None),
        ("same thresholds, two answers", ACCENT)])
    s += legend2(vh - 40, vw, [("seed, above 450", LINK, "fill"), ("kept: line", LINK, "tint"),
                               ("kept: from impulse", ACCENT, "tint"), ("dropped, no seed", SOFT, "hollow"),
                               ("8-connected", LINK, "bridge"), ("ring meets line", ACCENT, "bridge")])
    return emit("03", "hysteresis-chains", "Hysteresis on the raw and the smoothed patch",
                "The same thresholds, 450 and 180, on the raw patch and after the shared Gaussian. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def clip_half(poly):
    """Clip a polygon to the half-plane high > low (y > x, in data units)."""
    out = []
    for k in range(len(poly)):
        p, q = poly[k], poly[(k + 1) % len(poly)]
        fp, fq = p[1] - p[0], q[1] - q[0]
        if fp >= 0:
            out.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return out


def outcome(keep, M, low, high):
    return len(hysteresis(keep, M, low, high))


PLANES = [
    ("raw, L1: OpenCV's default", KEEP1, M1,
     [((0, 700), (640, 700), "nothing", "0"), ((430, 640), (0, 640), "dots", "3 dots"),
      ((0, 430), (0, 640), "ring", "8: dots + ring")]),
    ("raw, L2", KEEP2, M2,
     [((0, 700), (640, 700), "nothing", "0"), ((430, 640), (0, 640), "line", "5"),
      ((304.1, 430), (0, 640), "ring", "8"), ((0, 304.1), (0, 640), "ring", "10: line + ring")]),
    ("after the 3×3 Gaussian, L2", SKEEP2, SM2,
     [((0, 700), (474.9, 700), "nothing", "0"), ((436.5, 474.9), (0, 474.9), "dots", "2"),
      ((408.8, 436.5), (0, 474.9), "dots", "4"), ((0, 408.8), (219.7, 474.9), "line", "5: line alone"),
      ((0, 219.7), (0, 219.7), "ring", "7")]),
]
FILLS = {"nothing": ("rgba(45,49,66,0.05)", SOFT), "line": (LINK, LINK), "ring": (ACCENT, ACCENT),
         "dots": (SOFT, MUTED)}


def fig04():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "what every pair of thresholds returns on the patch, counted in edge pixels")
    size, y0, xs = 262, 118, [72, 388, 704]
    for k, (head, keep, M, regions) in enumerate(PLANES):
        A = Axes(xs[k], y0, size, size, (0, 700), (0, 700))
        s += title(xs[k] - 40, y0 - 30, head)
        s += A.clip(f"pl{k}") + f'<g clip-path="url(#pl{k})">'
        for (lo1, lo2), (hi1, hi2), kind, lab in regions:
            poly = clip_half([(lo1, hi1), (lo2, hi1), (lo2, hi2), (lo1, hi2)])
            if len(poly) < 3:
                continue
            fill, _ = FILLS[kind]
            op = 0.10 if kind == "nothing" else (0.30 if kind == "line" else 0.22)
            s += polygon([(A.X(a), A.Y(b)) for a, b in poly], fill if kind != "nothing" else "#2d3142",
                         stroke="#ffffff", sw=1.0, op=op if kind != "nothing" else 0.05)
        s += polyline([(A.X(0), A.Y(0)), (A.X(700), A.Y(700))], RULE_SOLID, sw=1)
        for ratio in (2, 3):
            s += polyline([(A.X(0), A.Y(0)), (A.X(700 / ratio), A.Y(700))], INK, sw=1.2, dash="5,3")
        s += "</g>"
        s += A.frame([0, 200, 400, 600], [0, 200, 400, 600], xlab="low threshold", ylab="high threshold",
                     xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", grid_y=False)
        for ratio in (2, 3):
            s += mono(A.X(700 / ratio) + (3 if ratio == 2 else -3), A.y0 - 4, f"×{ratio}", size=8, fill=INK,
                      anchor="start" if ratio == 2 else "end", weight="600")
        s += mono(A.X(560), A.Y(170), "low ≥ high:", size=7.5, fill=SOFT)
        s += mono(A.X(560), A.Y(170) + 11, "swapped", size=7.5, fill=SOFT)
        for (lo1, lo2), (hi1, hi2), kind, lab in regions:
            mid_lo, mid_hi = (lo1 + lo2) / 2, (hi1 + hi2) / 2
            # check the label against the real outcome at a sample point inside the region
            ls = min(lo2 - 1e-3, max(lo1 + 1e-3, mid_lo))
            hs = max(ls + 1, min(hi2 - 1e-3, max(hi1 + 1e-3, mid_hi)))
            n = outcome(keep, M, ls, hs)
            assert lab.split(":")[0].split(" ")[0] == str(n), (head, lab, n)
        s += region_labels(k, A)
    s += mono(32, vh - 62, "dashed lines: high = 2 × low and high = 3 × low, the range Canny used. "
              "OpenCV swaps a pair given in the wrong order, so only the region above the diagonal matters.",
              size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 34, vw, [("the line alone", LINK, "area", 0.30), ("line with impulse pixels", ACCENT, "area", 0.22),
                               ("broken line", SOFT, "area", 0.22), ("nothing", "#2d3142", "area", 0.05),
                               ("ratio 2 and 3", INK, "dash")])
    return emit("04", "threshold-plane", "What each threshold pair returns",
                "Edge pixels returned for every (low, high) pair on the raw patch with L1 and L2, and after smoothing. "
                "Computed from the definitions.", "intuition", vw, vh, s)


def region_labels(k, A):
    s = ""
    if k in (0, 1):
        s += mono(A.X(500), A.Y(662), "0: nothing", size=8.5, fill=MUTED, weight="600")
        big = ("8: dots", "+ ring") if k == 0 else ("10: line", "+ ring")
        s += mono(A.X(62), A.Y(470), big[0], size=8.5, fill=ACCENT, weight="600")
        s += mono(A.X(62), A.Y(470) + 12, big[1], size=8.5, fill=ACCENT, weight="600")
        if k == 0:
            s += mono(A.X(505), A.Y(560), "3 dots", size=8, fill=MUTED, weight="600")
        else:
            s += mono(A.X(367), A.Y(560), "8", size=8.5, fill=ACCENT, weight="600")
            s += mono(A.X(505), A.Y(575), "5: the", size=8, fill=LINK, weight="600")
            s += mono(A.X(505), A.Y(575) + 11, "line", size=8, fill=LINK, weight="600")
    else:
        s += mono(A.X(470), A.Y(600), "0: nothing", size=8.5, fill=MUTED, weight="600")
        s += mono(A.X(330), A.Y(432), "5: the line", size=8.5, fill=LINK, weight="600")
        s += mono(A.X(330), A.Y(432) + 12, "alone", size=8.5, fill=LINK, weight="600")
        s += mono(A.X(110), A.Y(150), "7", size=8.5, fill=ACCENT, weight="600")
        s += line(A.X(423), A.Y(452), A.x0 + A.w + 8, A.Y(400), stroke=MUTED, sw=0.8)
        s += mono(A.x0 + A.w + 12, A.Y(400) + 3, "4", size=8, fill=MUTED, weight="600", anchor="start")
        s += line(A.X(462), A.Y(470), A.x0 + A.w + 8, A.Y(470), stroke=MUTED, sw=0.8)
        s += mono(A.x0 + A.w + 12, A.Y(470) + 3, "2", size=8, fill=MUTED, weight="600", anchor="start")
    return s


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 480
    s = MARKS + eyebrow(32, 40, "two ways to find the neighbour along the gradient")
    # bins on a circle
    cx, cy, R = 200, 278, 118
    s += title(32, 92, "OpenCV's four bins, modulo 180°")
    bands = [(-22.5, 22.5, "H"), (22.5, 67.5, "D"), (67.5, 112.5, "V"), (112.5, 157.5, "D"),
             (157.5, 202.5, "H"), (202.5, 247.5, "D"), (247.5, 292.5, "V"), (292.5, 337.5, "D")]
    cols = {"H": SER1, "D": SER3, "V": SER2}
    for a0, a1, b in bands:
        pts = [(cx, cy)] + [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
                            for a in [a0 + (a1 - a0) * t / 12 for t in range(13)]]
        s += polygon(pts, cols[b], stroke="#ffffff", sw=1.2, op=0.22)
        am = math.radians((a0 + a1) / 2)
        s += mono(cx + 0.78 * R * math.cos(am), cy + 0.78 * R * math.sin(am) + 3, b, size=9, fill=MUTED, weight="600")
    for a in (22.5, 67.5):
        s += mono(cx + (R + 18) * math.cos(math.radians(-a)), cy + (R + 18) * math.sin(math.radians(-a)) + 3,
                  f"{a}°", size=7.5, fill=SOFT)
    ang = math.atan2(SGY[1][1], SGX[1][1])
    s += line(cx, cy, cx + 0.92 * R * math.cos(ang), cy + 0.92 * R * math.sin(ang), stroke=ACCENT, sw=2, marker="aa")
    s += mono(cx + 1.06 * R * math.cos(ang) + 4, cy + 1.06 * R * math.sin(ang) + 10, "62.8°", size=8.5, fill=ACCENT,
              weight="600", anchor="start")
    s += mono(cx, cy + R + 32, "angles measured from +x towards +y, down the image", size=7.5, fill=SOFT)
    # the 3x3 neighbourhood
    cs, gx0, gy0 = 96, 420, 132
    s += title(gx0 - 20, 92, "(r1, c1) of the smoothed patch and its neighbours, L2")
    for a in range(3):
        for b in range(3):
            v = SM2[a][b]
            s += rect(gx0 + b * cs, gy0 + a * cs, cs, cs, fill="#ffffff")
            s += mono(gx0 + b * cs + cs / 2, gy0 + a * cs + cs / 2 + 4, fmt(v), size=10.5, fill=INK, weight="500")
    for b in range(3):
        s += mono(gx0 + b * cs + cs / 2, gy0 - 7, f"c{b}", size=7.5, fill=SOFT)
    for a in range(3):
        s += mono(gx0 - 8, gy0 + a * cs + cs / 2 + 3, f"r{a}", size=7.5, fill=SOFT, anchor="end")
    s += rect(gx0 + cs, gy0 + cs, cs, cs, fill="none", stroke=ACCENT, sw=2)
    for (a, b) in ((0, 0), (2, 2)):
        s += rect(gx0 + b * cs + 14, gy0 + a * cs + 14, cs - 28, cs - 28, fill="none", stroke=SER2, sw=1.6, dash="5,3")
    w, ahead, behind = SDET[(1, 1)]
    # the gradient line, drawn outside the centre cell's number
    ux, uy = SGX[1][1] / SGY[1][1], 1.0
    centre = (gx0 + 1.5 * cs, gy0 + 1.5 * cs)
    fwd = (centre[0] + ux * cs, centre[1] + cs)
    back = (centre[0] - ux * cs, centre[1] - cs)
    exit_b = (centre[0] + ux * cs / 2, centre[1] + cs / 2)
    exit_t = (centre[0] - ux * cs / 2, centre[1] - cs / 2)
    s += line(exit_b[0], exit_b[1], fwd[0], fwd[1], stroke=LINK, sw=1.6)
    s += line(exit_t[0], exit_t[1], back[0], back[1], stroke=LINK, sw=1.6)
    s += diamond(fwd[0], fwd[1], 6) + diamond(back[0], back[1], 6)
    s += mono(fwd[0] - 10, fwd[1] + 28, fmt(ahead), size=9.5, fill=LINK, weight="600", anchor="end")
    s += mono(back[0] + 10, back[1] - 18, fmt(behind), size=9.5, fill=LINK, weight="600", anchor="start")
    assert abs((fwd[0] - gx0) / cs - (1.5 + w)) < 1e-9
    nx = 760
    s += note_lines(nx, 132, [
        ("quantised (OpenCV)", SER2), ("62.8° is in a diagonal bin, so", MUTED),
        ("compare with 100.5 and 316.2", MUTED), ("222.2 < 316.2: suppressed", ACCENT), ("", None),
        ("interpolated (Canny 1983,", LINK), ("scikit-image)", LINK), ("the gradient line crosses r2", MUTED),
        ("0.514 of the way from c1 to c2:", MUTED), ("0.486 × 74.7 + 0.514 × 316.2", MUTED),
        ("= 198.8; behind it, 133.0", MUTED), ("222.2 beats both: kept", LINK)])
    s += legend2(vh - 36, vw, [("the pixel tested", ACCENT, "outline"), ("what the bin compares", SER2, "hollow"),
                               ("interpolated neighbours", LINK, "diamond"), ("the gradient line", LINK, "line")])
    return emit("05", "bins-and-interpolation", "Four bins, or interpolation",
                "OpenCV's direction bins, and what each variant compares at (r1, c1) of the smoothed patch. Worked by hand.",
                "non-maximum suppression", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 452
    s = eyebrow(32, 40, "one clean row, 0 0 640 640 0: three tie rules, three answers")
    prof = [0, 0, 640, 640, 0]
    rules = [("strict on both sides", "as Grompone von Gioi and Randall state Canny's test", lambda a, m, b: m > a and m > b),
             ("OpenCV: > before, ≥ after", "canny.simd.hpp, horizontal and vertical bins", lambda a, m, b: m > a and m >= b),
             ("scikit-image: ≥ on both sides", "_canny_cy.pyx keeps a pixel no neighbour exceeds",
              lambda a, m, b: m >= a and m >= b)]
    outs = []
    for k, (head, sub, test) in enumerate(rules):
        x0 = 48 + k * 324
        s += title(x0 - 16, 92, head)
        s += mono(x0 - 16, 108, sub, size=7.5, fill=SOFT, anchor="start")
        base, top = 300, 150
        kept = []
        for c in range(5):
            m = prof[c]
            a = prof[c - 1] if c > 0 else 0
            b = prof[c + 1] if c < 4 else 0
            ok = m > 0 and test(a, m, b)
            if ok:
                kept.append(c)
            h = (base - top) * m / 640
            bx = x0 + c * 50
            if m:
                s += rect(bx, base - h, 34, h, fill=LINK if ok else "#ffffff", stroke=LINK if ok else SOFT,
                          sw=1.2, dash=None if ok else "4,3", op=0.85 if ok else None)
                s += mono(bx + 17, base - h - 7, "640", size=8.5, fill=LINK if ok else SOFT, weight="600" if ok else "400")
            else:
                s += line(bx, base, bx + 34, base, stroke=SOFT, sw=1.2)
                s += mono(bx + 17, base - 7, "0", size=8.5, fill=SOFT)
            s += mono(bx + 17, base + 16, f"c{c}", size=8, fill=SOFT)
        outs.append(kept)
        verdict = {0: "no pixel kept: the edge vanishes", 1: "one kept: c2, the left of the pair",
                   2: "two kept: the edge is 2 pixels wide"}[len(kept)]
        s += mono(x0 + 117, base + 44, verdict, size=8.5, fill=ACCENT if not kept else LINK, weight="600")
        why = {0: "c2: 640 > 640 fails; c3: 640 > 640 fails", 1: "c2: 640 ≥ 640 passes; c3: 640 > 640 fails",
               2: "c2 and c3: 640 ≥ 640 passes on both sides"}[len(kept)]
        s += mono(x0 + 117, base + 60, why, size=8, fill=SOFT)
    assert outs == [[], [2], [2, 3]]
    s += mono(32, vh - 62, "the step lies exactly between c2 and c3, so Sobel reads 640 on both; mirror it and "
              "OpenCV still keeps the left pixel, now on the bright side", size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 34, vw, [("kept", LINK, "fill"), ("suppressed", SOFT, "hollow")])
    return emit("06", "tie-rules", "Three tie rules on one row",
                "Strict, OpenCV's and scikit-image's comparisons on the profile 0, 0, 640, 640, 0. Worked by hand.",
                "non-maximum suppression", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def parabola(xm, a, b, c):
    """Through (xm-1, a), (xm, b), (xm+1, c)."""
    A2 = (a + c - 2 * b) / 2
    B1 = (c - a) / 2
    return lambda x: A2 * (x - xm) ** 2 + B1 * (x - xm) + b


def fig07():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "devernay's correction: the vertex of a parabola through three magnitudes")
    A = Axes(92, 96, 600, 290, (0.5, 4.5), (0, 800))
    s += A.frame([1, 2, 3, 4], [0, 200, 400, 600, 800], ylab="L2 magnitude", xfmt=lambda v: f"c{v}",
                 yfmt=lambda v: f"{v:g}")
    s += mono(A.x0 + A.w, A.y0 + A.h + 46, "column", size=8.5, fill=SOFT, anchor="end")
    s += A.clip("pl7") + '<g clip-path="url(#pl7)">'
    rows = [(0, 2, LINK), (2, 3, ACCENT)]
    verts = []
    for r, c, col in rows:
        a, b, cc = M2[r][c - 1], M2[r][c], (M2[r][c + 1] if c + 1 < N else 0)
        f = parabola(c, a, b, cc)
        xv = c + devernay(a, b, cc)
        verts.append((xv, f(xv), col))
        s += polyline([(A.X(x), A.Y(f(x))) for x in [c - 1 + 2 * t / 100 for t in range(101)]], col, sw=2)
        s += line(A.X(xv), A.Y(f(xv)), A.X(xv), A.Y(0), stroke=col, sw=1, dash="3,3")
        for x, v in ((c - 1, a), (c, b), (c + 1, cc)):
            s += dot(A.X(x), A.Y(v), 4, fill=col)
    s += "</g>"
    assert [round(v[0], 2) for v in verts] == [2.5, 2.9]
    s += mono(A.X(verts[0][0]) - 4, A.Y(0) + 30, "2.5", size=8.5, fill=LINK, weight="600", anchor="end")
    s += mono(A.X(verts[1][0]) + 4, A.Y(0) + 30, "2.90", size=8.5, fill=ACCENT, weight="600", anchor="start")
    s += mono(A.X(2.5), A.Y(verts[0][1]) - 10, "row r0: vertex 720 at 2.5", size=8.5, fill=LINK, weight="600",
              anchor="end")
    s += mono(A.X(3.55), A.Y(520), "row r2: vertex at 2.90", size=8.5, fill=ACCENT, weight="600", anchor="start")
    nx = 734
    s += note_lines(nx, 112, [
        ("offset η = ½ (A − C) / (A + C − 2B)", INK), ("from the kept pixel, along the gradient", MUTED), ("", None),
        ("row r0: 0, 640, 640 → 2.5,", LINK), ("exactly where the step is", MUTED), ("", None),
        ("row r2: 210, 640, 0 → 2.90:", ACCENT), ("the impulse two columns away", MUTED),
        ("lowers the left value and pulls", MUTED), ("the estimate 0.4 pixel right", MUTED), ("", None),
        ("smoothed patch: 2.54 and 2.77", MUTED)])
    s += legend2(vh - 36, vw, [("row r0, through c1, c2, c3", LINK, "line"), ("row r2, through c2, c3, c4", ACCENT, "line")])
    return emit("07", "sub-pixel-position", "Where exactly is the edge?",
                "Devernay's parabola through three magnitudes on rows r0 and r2 of the raw patch. "
                "Evaluated from the worked values.", "non-maximum suppression", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "the units of a canny threshold: what the derivative reads, by aperture and norm")
    x0, w = 250, 330
    X = lambda v: x0 + math.log10(v) / 6 * w
    y0 = 108
    s += title(32, 86, "the patch's step of 160 and a ramp of 1 per pixel; weights: smoothing · derivative")
    rows = [(3, "aperture 3 (default)"), (-1, "aperture −1 (Scharr)"), (5, "aperture 5"), (7, "aperture 7")]
    base = y0 + len(rows) * 66
    for t in (1, 10, 100, 1000, 10000, 100000, 1000000):
        xx = X(t)
        s += line(xx, y0 - 8, xx, base - 10, stroke=RULE, sw=0.8)
        s += mono(xx, base + 4, f"{t:,}", size=7.5, fill=SOFT)
    s += line(x0, y0 - 8, x0, base - 10, stroke=RULE_SOLID)
    for k, (ap, lab) in enumerate(rows):
        y = y0 + k * 66
        st, rp = GAIN[ap]
        s += mono(32, y + 12, lab, size=9, fill=INK, anchor="start", weight="500")
        d, sm = KER[ap]
        s += mono(32, y + 26, f"{' '.join(str(v) for v in sm)}  ·  {' '.join(str(v) for v in d)}".replace("-", "−"),
                  size=7.5, fill=SOFT, anchor="start")
        s += rect(x0, y, X(st * 160) - x0, 18, fill=LINK, stroke=LINK, op=0.85)
        s += mono(X(st * 160) + 6, y + 13, f"{st * 160:,}  ({st}h)", size=8.5, fill=LINK, anchor="start", weight="600")
        s += rect(x0, y + 24, X(rp) - x0, 18, fill=SER3, stroke=SER3, op=0.85)
        s += mono(X(rp) + 6, y + 37, f"{rp:,}", size=8.5, fill=SER3, anchor="start", weight="600")
    s += mono(x0 + w, base + 20, "derivative output, log scale", size=8, fill=SOFT, anchor="end")
    # L1 over L2 against angle
    A = Axes(690, 110, 280, 220, (0, 90), (0.95, 1.5))
    s += title(658, 86, "L1 ÷ L2 against gradient angle")
    s += A.frame([0, 22.5, 45, 67.5, 90], [1.0, 1.1, 1.2, 1.3, 1.4], xfmt=lambda v: f"{v:g}°",
                 yfmt=lambda v: f"{v:.1f}")
    s += A.clip("pl8") + '<g clip-path="url(#pl8)">'
    s += polyline([(A.X(a), A.Y(abs(math.cos(math.radians(a))) + abs(math.sin(math.radians(a)))))
                   for a in [90 * t / 180 for t in range(181)]], INK, sw=1.8)
    s += "</g>"
    for a, col in ((ANG12, ACCENT), (45, INK)):
        v = math.cos(math.radians(a)) + math.sin(math.radians(a))
        s += dot(A.X(a), A.Y(v), 4, fill=col)
    s += mono(A.X(ANG12) + 8, A.Y(1.344) + 16, "1.344 at 26.8°", size=8, fill=ACCENT, weight="600", anchor="start")
    s += mono(A.X(ANG12) + 8, A.Y(1.344) + 28, "(r1, c2)", size=8, fill=ACCENT, weight="600", anchor="start")
    s += mono(A.X(45), A.Y(1.414) - 9, "1.414 at 45°", size=8, fill=INK, weight="600")
    s += mono(A.x0 + A.w, A.y0 + A.h + 30, "angle from the x axis", size=8, fill=SOFT, anchor="end")
    s += note_lines(658, 388, [("aperture 3 → 5 multiplies a step by 12", INK), ("and a ramp by 16: no single factor", MUTED),
                               ("converts a threshold between apertures", MUTED)], size=8.5)
    s += legend2(vh - 36, vw, [("a step of 160 levels", LINK, "fill"), ("a ramp of 1 level per pixel", SER3, "fill"),
                               ("L1 ÷ L2", INK, "line")])
    return emit("08", "threshold-units", "The units of a Canny threshold",
                "Sobel and Scharr responses by aperture, and the L1 norm against the L2 norm. "
                "Computed from OpenCV's kernels.", "units", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "thresholds from the noise: flat-region gradient magnitude for noise of 2 grey levels")
    A = Axes(92, 96, 620, 280, (0, 90), (0, 0.1))
    s += A.frame([0, 10, 20, 30, 40, 50, 60, 70, 80, 90], [0, 0.025, 0.05, 0.075, 0.1], ylab="probability density",
                 xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    s += mono(A.x0 + A.w, A.y0 + A.h + 30, "L2 gradient magnitude, aperture 3", size=8.5, fill=SOFT, anchor="end")
    sN = S_NOISE
    f = lambda m: m / sN ** 2 * math.exp(-m * m / (2 * sN * sN))
    xs = [90 * t / 360 for t in range(361)]
    s += A.clip("pl9") + '<g clip-path="url(#pl9)">'
    tail = [(A.X(TL), A.Y(0))] + [(A.X(x), A.Y(f(x))) for x in xs if x >= TL] + [(A.X(90), A.Y(0))]
    s += polygon(tail, SER2, op=0.18)
    s += polyline([(A.X(x), A.Y(f(x))) for x in xs], INK, sw=2)
    for xv, col in ((TL, SER2), (TH, LINK), (80, ACCENT)):
        s += line(A.X(xv), A.Y(0.1), A.X(xv), A.Y(0), stroke=col, sw=1.2, dash="4,3")
    s += "</g>"
    s += mono(A.X(TL) - 5, A.Y(0.093), "low 14.9", size=8.5, fill=SER2, weight="600", anchor="end")
    s += mono(A.X(TH) + 5, A.Y(0.093), "high 29.7", size=8.5, fill=LINK, weight="600", anchor="start")
    s += mono(A.X(80) - 5, A.Y(0.093), "a 20-level step: 80", size=8.5, fill=ACCENT, weight="600", anchor="end")
    for k, t in enumerate(("0.10 of flat", "pixels above", "the low one")):
        s += mono(A.X(22.3), A.Y(0.074) + 12 * k, t, size=8, fill=SER2)
    s += line(A.X(21.2), A.Y(0.074) + 30, A.X(18.6), A.Y(0.005), stroke=SER2, sw=0.8)
    nx = 744
    s += note_lines(nx, 112, [
        ("σ = 2 grey levels of noise", INK), ("each derivative: √12 σ = 6.93", MUTED), ("L2 magnitude: Rayleigh, s = 6.93", MUTED),
        ("", None), ("high = s √(2 ln 10⁴) = 29.7:", LINK), ("1 flat pixel in 10,000 above", MUTED),
        ("smallest seeding step 29.7 / 4 = 7.4", MUTED), ("", None), ("low = high / 2 = 14.9:", SER2),
        ("1 flat pixel in 10 above, harmless", MUTED), ("unless it touches a seeded chain", MUTED)])
    s += legend2(vh - 36, vw, [("noise magnitude density", INK, "line"), ("above the low threshold", SER2, "area", 0.18)])
    return emit("09", "noise-thresholds", "Thresholds from the noise",
                "The Rayleigh density of flat-region magnitude for σ = 2, with both thresholds. "
                "Model inputs: Gaussian noise, aperture 3, L2.", "setting the thresholds", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "why two thresholds: the contrast a chain needs falls with its length")
    A = Axes(92, 96, 620, 280, (1, 30), (0, 6))
    s += A.frame([1, 4, 9, 16, 25, 30], [0, 1, 2, 3, 4, 5, 6], ylab="required contrast, in units of s",
                 xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    s += mono(A.x0 + A.w, A.y0 + A.h + 30, "chain length l, in pixels", size=8.5, fill=SOFT, anchor="end")
    mu = lambda l: AC / math.sqrt(l)
    s += A.clip("pl10") + '<g clip-path="url(#pl10)">'
    for v, col in ((AC, LINK), (AC / 2, SER2), (AC / 3, SER3)):
        s += line(A.X(1), A.Y(v), A.X(30), A.Y(v), stroke=col, sw=1.2, dash="5,3")
    s += polyline([(A.X(l), A.Y(mu(l))) for l in [1 + 29 * t / 300 for t in range(301)]], INK, sw=2)
    for l, col in ((4, SER2), (9, SER3)):
        s += line(A.X(l), A.Y(mu(l)), A.X(l), A.Y(0), stroke=col, sw=1, dash="2,3")
    s += "</g>"
    s += dot(A.X(1), A.Y(AC), 4, fill=LINK) + dot(A.X(4), A.Y(AC / 2), 4, fill=SER2) + dot(A.X(9), A.Y(AC / 3), 4, fill=SER3)
    s += mono(A.X(30), A.Y(AC) - 7, "high: one pixel, 5.26 s", size=8.5, fill=LINK, weight="600", anchor="end")
    s += mono(A.X(30), A.Y(AC / 2) - 7, "high ÷ 2 = 2.63 s: a chain of 4", size=8.5, fill=SER2, weight="600", anchor="end")
    s += mono(A.X(30), A.Y(AC / 3) - 7, "high ÷ 3 = 1.75 s: a chain of 9", size=8.5, fill=SER3, weight="600", anchor="end")
    s += mono(A.X(3.2), A.Y(4.4), "μmin(l) = s √(2 ln N / l)", size=9, fill=INK, weight="600", anchor="start")
    nx = 744
    s += note_lines(nx, 112, [
        ("a curve is meaningful when", INK), ("N · H(μ)^l ≤ 1 (Desolneux,", MUTED), ("Moisan and Morel)", MUTED), ("", None),
        ("with the Rayleigh tail as H,", MUTED), ("N = 10⁶ curves:", MUTED), ("", None),
        ("a chain k² times longer needs", INK), ("1/k of the contrast, so Canny's", MUTED),
        ("ratio of 2 to 3 is the drop", MUTED), ("for chains of 4 to 9 pixels", MUTED)])
    s += legend2(vh - 36, vw, [("required contrast", INK, "line"), ("high threshold", LINK, "dash"),
                               ("high ÷ 2", SER2, "dash"), ("high ÷ 3", SER3, "dash")])
    return emit("10", "a-contrario-length", "Why two thresholds",
                "Required contrast against chain length under the a contrario rule with a Rayleigh tail. "
                "Model inputs: N = 10⁶ curves, independent points.", "setting the thresholds", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 612
    s = eyebrow(32, 40, "one method, three implementations: mapped from source and documentation, not run")
    cols = [("", 32), ("OpenCV  cv2.Canny", 196), ("scikit-image  feature.canny", 462), ("MATLAB  edge(I, \"canny\")", 744)]
    y0 = 76
    for h, x in cols:
        s += mono(x, y0, h, size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, y0 + 10, vw - 32, y0 + 10, stroke=RULE_SOLID)
    rows = [
        ("smoothing", "none: add GaussianBlur yourself", "Gaussian, σ = 1 by default", "derivative of Gaussian, σ = √2"),
        ("derivative", "Sobel 3, 5, 7, or Scharr (−1)", "SciPy Sobel 3×3", "derivative of Gaussian"),
        ("border", "replicate, not reflect-101", "Gaussian: constant; 1-px border masked", "not documented"),
        ("magnitude", "L1 unless L2gradient=True", "L2", "not documented"),
        ("suppression", "4 bins, nearest neighbour", "interpolated, 2 neighbours", "not documented"),
        ("ties", "> before, ≥ after; > on diagonals", "≥ both: a plateau stays 2 wide", "not documented"),
        ("threshold tests", "> low, > high", "≥ low, ≥ high", "not documented"),
        ("linking", "8-connected, stack walk", "8-connected components", "not documented"),
        ("threshold units", "raw: 4h per step at 3, 48h at 5", "raw Sobel of a 0–1 image", "fractions from 0 to 1"),
        ("defaults", "none: both required", "10% and 20% of dtype max", "heuristic; low = 0.4 × high"),
        ("low > high", "swapped silently", "raises an error", "not documented"),
        ("input", "8-bit; or your own 16-bit dx, dy", "any dtype but 64-bit integers", "2-D grayscale"),
    ]
    for k, (what, a, b, c) in enumerate(rows):
        y = y0 + 34 + k * 40
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 18}" width="{vw - 56}" height="40" fill="rgba(45,49,66,0.03)"/>'
        s += mono(32, y + 4, what, size=8, fill=SOFT, anchor="start", track="0.08em", weight="600")
        for txt_, x in ((a, 196), (b, 462), (c, 744)):
            trap = txt_.startswith(("none: add", "replicate", "L1 unless", "swapped", "raises"))
            s += mono(x, y + 4, txt_, size=8.5, fill=ACCENT if trap else (SOFT if txt_ == "not documented" else INK),
                      anchor="start", weight="600" if trap else "400")
    s += mono(32, vh - 16, "pinned: OpenCV 802cf95, scikit-image b700edc; MATLAB from MathWorks' edge page, release R2026b. "
              "Orange marks the behaviour most likely to surprise.", size=8, fill=SOFT, anchor="start")
    return emit("11", "tooling-map", "The tooling map",
                "Smoothing, border, norm, suppression, ties, comparisons, linking and units in OpenCV, "
                "scikit-image and MATLAB. None of it was executed.", "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
