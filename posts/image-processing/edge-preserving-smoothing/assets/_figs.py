#!/usr/bin/env python3
"""Figures 01-11 for edge-preserving-smoothing.

Every value drawn here is computed in this file, from the definitions, on the series'
5x5 patch: the bilateral filter with the shared 3x3 Gaussian as its spatial kernel, the
3x3 median, NL-means with 3x3 patches under both self-weight rules, and the Perona-Malik
scheme, all with reflect-101 borders (adiabatic for diffusion). Nothing is measured and
nothing loads an image. Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID,
                    SANS, SOFT, emit, eyebrow, hline, masked, mono, txt, vline)

SER1, SER2, SER3, SER4 = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50"
C_GAUSS, C_MEDIAN, C_BIL, C_NLM, C_PM = SOFT, SER1, LINK, SER4, SER3

# ------------------------------------------------------------------ the data
N = 5
PATCH = [[40, 40, 40, 200, 200] for _ in range(N)]
PATCH[2][1] = 255


def r101(i, n=N):
    """OpenCV's BORDER_REFLECT_101: mirror about the edge pixel without repeating it."""
    while i < 0 or i >= n:
        i = -i if i < 0 else 2 * (n - 1) - i
    return i


def at(M, i, j):
    return M[r101(i)][r101(j)]


G1 = [math.exp(-1 / 1.28), 1.0, math.exp(-1 / 1.28)]
G1 = [v / sum(G1) for v in G1]                                  # [0.239, 0.522, 0.239]
W2 = {(di, dj): G1[di + 1] * G1[dj + 1] for di in (-1, 0, 1) for dj in (-1, 0, 1)}


def rw(delta, sr):
    return 1.0 if sr is None else math.exp(-delta * delta / (2 * sr * sr))


def bilateral(M, i, j, sr):
    num = den = 0.0
    for (di, dj), ws in W2.items():
        v = at(M, i + di, j + dj)
        w = ws * rw(v - M[i][j], sr)
        num += w * v
        den += w
    return num / den


def bil_weights(M, i, j, sr):
    """Normalised bilateral weights of the 3x3 window, as a 3x3 grid."""
    raw = {(di, dj): ws * rw(at(M, i + di, j + dj) - M[i][j], sr) for (di, dj), ws in W2.items()}
    tot = sum(raw.values())
    return [[raw[(di, dj)] / tot for dj in (-1, 0, 1)] for di in (-1, 0, 1)]


def median(M, i, j):
    return sorted(at(M, i + di, j + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1))[4]


def patch3(M, i, j):
    return [at(M, i + di, j + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1)]


def d2(M, a, b):
    pa, pb = patch3(M, *a), patch3(M, *b)
    return sum((x - y) ** 2 for x, y in zip(pa, pb)) / 9


def nlm(M, i, j, h, rule):
    """Every pixel of the patch is a candidate; rule 'one' = own weight 1 (OpenCV,
    scikit-image), 'max' = own weight is the largest of the others (IPOL)."""
    ws = {(a, b): math.exp(-d2(M, (i, j), (a, b)) / (h * h)) for a in range(N) for b in range(N)}
    if rule == "max":
        ws[(i, j)] = max(v for k, v in ws.items() if k != (i, j))
    return sum(w * M[a][b] for (a, b), w in ws.items()) / sum(ws.values())


def g_rat(s, K=80.0):
    return 1.0 / (1.0 + (s / K) ** 2)


def g_exp(s, K=80.0):
    return math.exp(-(s / K) ** 2)


def pm_step(M, K=80.0, lam=0.25, g=g_rat):
    out = [r[:] for r in M]
    for i in range(N):
        for j in range(N):
            tot = 0.0
            for di, dj in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                a, b = i + di, j + dj
                if 0 <= a < N and 0 <= b < N:                  # adiabatic: no face at the border
                    d = M[a][b] - M[i][j]
                    tot += g(abs(d), K) * d
            out[i][j] = M[i][j] + lam * tot
    return out


def pm_iter(n, K=80.0, g=g_rat):
    M = [r[:] for r in PATCH]
    seq = [M]
    for _ in range(n):
        M = pm_step(M, K, g=g)
        seq.append(M)
    return seq


def full(fn):
    return [[fn(i, j) for j in range(N)] for i in range(N)]


def contrasts(M):
    """Impulse: value minus the mean of its four neighbours. Step: r0 c3 minus r0 c2."""
    imp = M[2][1] - (M[1][1] + M[3][1] + M[2][0] + M[2][2]) / 4
    return imp, M[0][3] - M[0][2]


GAUSS = full(lambda i, j: bilateral(PATCH, i, j, None))
MED = full(lambda i, j: median(PATCH, i, j))
BIL80 = full(lambda i, j: bilateral(PATCH, i, j, 80))
NLM_ONE = full(lambda i, j: nlm(PATCH, i, j, 20, "one"))
NLM_MAX = full(lambda i, j: nlm(PATCH, i, j, 20, "max"))
PM = pm_iter(100)


def r(v, nd=2):
    return round(v, nd)


# the article's numbers; a figure that disagrees with the text fails here
assert [r(v, 3) for v in G1] == [0.239, 0.522, 0.239]
assert (r(W2[(0, 0)], 4), r(W2[(0, 1)], 4), r(W2[(1, 1)], 4)) == (0.2725, 0.1248, 0.0571)
assert sum(map(sum, PATCH)) == 2815 and 2815 / 25 == 112.6
assert (r(rw(20, 80), 3), r(rw(160, 80), 3), r(rw(215, 80), 3)) == (0.969, 0.135, 0.027)
assert r(BIL80[2][1], 1) == 240.5 and r(BIL80[0][2], 1) == 46.5 and r(BIL80[0][3], 1) == 193.5
assert [r(v, 1) for v in BIL80[2]] == [41.9, 240.5, 48.8, 193.5, 200.0]
assert r(GAUSS[2][1], 1) == 98.6 and r(GAUSS[0][2], 1) == 78.2 and r(GAUSS[0][3], 1) == 161.8
assert r(GAUSS[2][0], 1) == 93.6
assert MED[2] == [40, 40, 40, 200, 200] and MED[0] == [40, 40, 40, 200, 200]
_bump = [row[:] for row in PATCH]
_bump[2][1] = 60
assert r(bilateral(_bump, 2, 1, 80), 1) == 45.6 and r(bilateral(_bump, 2, 1, None), 2) == 45.45
_e3 = [row[:] for row in PATCH]
_e3[2][1] = 120
assert r(bilateral(_e3, 2, 1, 80), 1) == 70.5
assert r(d2(PATCH, (2, 1), (0, 0))) == 5136.11 and r(math.sqrt(d2(PATCH, (2, 1), (0, 0))), 1) == 71.7
assert d2(PATCH, (0, 2), (4, 2)) == 0 and r(d2(PATCH, (0, 2), (0, 3)), 1) == 8533.3
assert sorted(k for k in ((a, b) for a in range(N) for b in range(N))
              if r(d2(PATCH, (2, 1), k)) == 5136.11) == [(0, 0), (0, 1), (4, 0), (4, 1)]
assert r(NLM_ONE[2][1], 1) == 255.0 and r(NLM_MAX[2][1], 1) == 83.0
assert [r(v, 1) for v in NLM_MAX[0]] == [40, 40, 40, 200, 200]
assert r(nlm(PATCH, 2, 1, 80, "one"), 1) == 110.7 and r(nlm(PATCH, 0, 2, 80, "one"), 1) == 82.0
assert r(nlm(PATCH, 0, 3, 80, "one"), 1) == 170.4
assert (g_rat(160), r(g_rat(215), 3)) == (0.2, 0.122) and r(215 * g_rat(215), 2) == 26.15
assert [r(v, 2) for v in PM[1][2]] == [46.54, 228.85, 54.54, 192.0, 200.0] and PM[1][0][2:4] == [48.0, 192.0]
assert [r(v, 2) for v in PM[2][2]] == [50.65, 199.19, 67.57, 185.29, 198.02]
assert [r(v, 2) for v in PM[2][0]] == [40.0, 43.6, 54.51, 185.49, 198.02]
assert [r(v, 2) for v in PM[3][2]] == [55.33, 165.25, 80.9, 179.19, 194.91]
assert [r(v, 1) for v in (PM[3][2][1], PM[3][2][0], PM[3][0][2], PM[3][0][3])] == [165.2, 55.3, 61.5, 179.7]
assert [r(v, 2) for v in PM[3][0]] == [41.71, 47.22, 61.54, 179.65, 194.96]
assert [r(contrasts(PM[k])[0], 1) for k in (1, 2, 3, 5, 10)] == [180.3, 144.1, 102.5, 13.4, -2.9]
assert [r(contrasts(PM[k])[1], 1) for k in (1, 2, 3, 5, 10)] == [144.0, 131.0, 118.1, 92.4, 39.2]
assert all(abs(v - 112.6) < 0.05 for row in PM[100] for v in row)
_lin = pm_step(PATCH, K=1e12)
assert _lin[2][1] == 40 and _lin[1][1] == 93.75 and _lin[0][2:4] == [80, 160]
assert r(1 + (215 / 80) ** 2, 3) == 8.223 and r(215 / (1 + (215 / 80) ** 2), 2) == 26.15
assert r(255 - 215 / (1 + (215 / 80) ** 2), 2) == 228.85 and r(1 - g_rat(215), 3) == 0.878
assert r(math.sqrt(49 * 9 * math.log(1000)), 0) == 55


def opencv_plus(M, i, j, sr=80, ss=0.8):
    """cv2.bilateralFilter with d = 3: a disc of radius 1, five taps."""
    num = den = 0.0
    for di, dj in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
        v = at(M, i + di, j + dj)
        w = math.exp(-(di * di + dj * dj) / (2 * ss * ss)) * rw(v - M[i][j], sr)
        num += w * v
        den += w
    return num / den


assert r(opencv_plus(PATCH, 2, 1), 1) == 244.9 and r(opencv_plus(PATCH, 0, 2), 1) == 44.1
assert {R: sum(1 for i in range(-R, R + 1) for j in range(-R, R + 1) if i * i + j * j <= R * R)
        for R in (1, 2, 4)} == {1: 5, 2: 13, 4: 49}


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
    t = v / hi
    s = shade_rect(x, y, w, h, t, dash=dash)
    return s + txt(x + w / 2, y + h / 2 + size * 0.36, label if label is not None else fmt(v),
                   size=size, fill=ink_for(t), family=MONO, weight="500")


def dcell(x, y, w, h, label, size=10, stroke="rgba(45,49,66,0.30)", sw=0.8, fill="#ffffff",
          tcolor=INK, weight="500"):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
            + txt(x + w / 2, y + h / 2 + size * 0.36, label, size=size, fill=tcolor, family=MONO,
                  weight=weight))


def outline(x, y, w, h, stroke=ACCENT, sw=2, dash=None, rx=0):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def polyline(pts, stroke, sw=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None):
    s = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{s}/>'


def note_lines(x, y, items, size=9, gap=15, anchor="start"):
    return "".join(mono(x, y + k * gap, t, size=size, fill=c, anchor=anchor) for k, (t, c) in enumerate(items))


def legend2(y, vw, items):
    """Legend whose swatches are drawn exactly like the marks they name.
    item: (label, colour, kind) with kind in line | dash | dot | ring | box."""
    s = (f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" '
         f'stroke="{RULE}" stroke-width="0.8"/>')
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for label, colour, kind in items:
        if kind in ("line", "dash"):
            d = ' stroke-dasharray="5,3"' if kind == "dash" else ""
            s += (f'<line x1="{x}" y1="{y + 5}" x2="{x + 18}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.8"{d}/>')
        elif kind == "dot":
            s += dot(x + 8, y + 5, 4, fill=colour)
        elif kind == "ring":
            s += f'<circle cx="{x + 8}" cy="{y + 5}" r="4.2" fill="#ffffff" stroke="{colour}" stroke-width="1.6"/>'
        else:
            s += (f'<rect x="{x}" y="{y}" width="14" height="10" fill="none" stroke="{colour}" '
                  f'stroke-width="1.8"/>')
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.06em")
        x += 24 + 6.2 * len(label) + 30
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

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, raw=False):
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
            s += (mono(self.x0 + self.w, self.y0 + self.h + 30, xlab, size=8.5, fill=SOFT, anchor="end")
                  if raw else eyebrow(self.x0 + self.w, self.y0 + self.h + 30, xlab, anchor="end"))
        if ylab:
            s += (mono(self.x0, self.y0 - 10, ylab, size=8.5, fill=SOFT, anchor="start")
                  if raw else eyebrow(self.x0, self.y0 - 10, ylab, anchor="start"))
        return s


def title(x, y, s, fill=INK):
    """A panel title in mono, not uppercased, so positions like (r2, c1) keep their case."""
    return mono(x, y, s, size=9.5, fill=fill, anchor="start", weight="600")


def grid(x, y, cs, M, size=9, hi=255.0, nd=1, labels=False):
    s = ""
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            s += vcell(x + j * cs, y + i * cs, cs, cs, v, hi=hi, size=size, label=fmt(v, nd))
    if labels:
        for j in range(len(M[0])):
            s += mono(x + j * cs + cs / 2, y - 6, f"c{j}", size=7.5, fill=SOFT)
        for i in range(len(M)):
            s += mono(x - 6, y + i * cs + cs / 2 + 3, f"r{i}", size=7.5, fill=SOFT, anchor="end")
    return s



# ------------------------------------------------------------------ FIG 01
def bil_panel(y0, head, i, j, note, hl):
    cs = 40
    vals = [[at(PATCH, i + di, j + dj) for dj in (-1, 0, 1)] for di in (-1, 0, 1)]
    spat = [[W2[(di, dj)] for dj in (-1, 0, 1)] for di in (-1, 0, 1)]
    rng = [[rw(vals[a][b] - PATCH[i][j], 80) for b in range(3)] for a in range(3)]
    nw = bil_weights(PATCH, i, j, 80)
    out = bilateral(PATCH, i, j, 80)
    s = title(32, y0 - 34, head)
    xs = [48, 236, 424, 612]
    heads = ["window values", "spatial weight", "range weight, σr = 80", "product ÷ its sum"]
    for x, h in zip(xs, heads):
        s += mono(x, y0 - 10, h, size=8.5, fill=SOFT, anchor="start")
    for a in range(3):
        for b in range(3):
            s += vcell(xs[0] + b * cs, y0 + a * cs, cs, cs, vals[a][b], size=9.5)
            s += dcell(xs[1] + b * cs, y0 + a * cs, cs, cs, f"{spat[a][b]:.3f}", size=8.5)
            tiny = rng[a][b] < 0.5
            s += dcell(xs[2] + b * cs, y0 + a * cs, cs, cs, fmt(rng[a][b], 3), size=8.5,
                       tcolor=ACCENT if tiny else INK, weight="600" if tiny else "500")
            s += dcell(xs[3] + b * cs, y0 + a * cs, cs, cs, f"{nw[a][b]:.3f}", size=8.5)
    for x in xs:
        s += hl(x, y0, cs)
    mid = y0 + 1.5 * cs
    s += mono(xs[1] + 3 * cs + 24, mid + 5, "×", size=16, fill=MUTED)
    s += mono(xs[2] + 3 * cs + 24, mid + 5, "=", size=16, fill=MUTED)
    s += hline(xs[3] + 3 * cs + 10, 817, mid)
    s += vcell(818, mid - 30, 60, 60, out, size=13, label=fmt(out, 1))
    s += mono(848, mid + 46, f"was {PATCH[i][j]}", size=8.5, fill=SOFT)
    s += note_lines(48, y0 + 3 * cs + 24, note, size=8.5, gap=14)
    return s


def fig01():
    vw, vh = 1016, 556
    s = eyebrow(32, 40, "the bilateral filter at two pixels: spatial weight × range weight, normalised to sum 1")

    def hl_imp(x, y0, cs):
        return outline(x + cs, y0 + cs, cs, cs, stroke=ACCENT, sw=2)

    def hl_step(x, y0, cs):
        return outline(x + 2 * cs + 2, y0 + 2, cs - 4, 3 * cs - 4, stroke=LINK, sw=1.6, dash="5,3")

    s += bil_panel(124, "the impulse (r2, c1): every neighbour differs by 215", 2, 1,
                   [("each neighbour keeps e^(−215² / 12,800) = 0.027 of its spatial weight", ACCENT),
                    ("(0.2725 × 255 + 0.7275 × 0.027 × 40) / (0.2725 + 0.7275 × 0.027) = 70.27 / 0.2922 = 240.5", MUTED)],
                   hl_imp)
    s += f'<line x1="32" y1="318" x2="{vw - 32}" y2="318" stroke="{RULE}" stroke-width="0.8"/>'
    s += bil_panel(384, "the step's dark side (r0, c2): the far column differs by 160", 0, 2,
                   [("the far column keeps e^(−2) = 0.135 of its spatial weight", LINK),
                    ("(0.761 × 40 + 0.0323 × 200) / (0.761 + 0.0323) = 46.5: the step keeps 147 of 160, the impulse 200.5 of 215", MUTED)],
                   hl_step)
    return emit("01", "bilateral-weights", "The bilateral filter's weights at two pixels",
                "Spatial weight times range weight, normalised, at the impulse and beside the step. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def dist_panel(x0, head, ref, note):
    s = title(x0, 92, head)
    i, j = ref
    pt = patch3(PATCH, i, j)
    s += mono(x0, 116, "its 3×3 patch", size=8.5, fill=SOFT, anchor="start")
    for a in range(3):
        for b in range(3):
            s += vcell(x0 + b * 30, 124 + a * 30, 30, 30, pt[3 * a + b], size=8.5)
    gx, gy, gc = x0 + 140, 124, 56
    s += mono(gx, 116, "d², mean squared patch difference, to every pixel", size=8.5, fill=SOFT, anchor="start")
    for a in range(N):
        for b in range(N):
            v = d2(PATCH, ref, (a, b))
            me = (a, b) == ref
            copy = v == 0 and not me
            near = abs(v - 5136.11) < 0.1
            hot = copy or (near and ref == (2, 1))
            s += dcell(gx + b * gc, gy + a * 30, gc, 30, "self" if me else f"{v:,.0f}", size=8.5,
                       fill=ACCENT_TINT if hot else "#ffffff", tcolor=ACCENT if hot else INK,
                       weight="600" if hot else "400")
            if me:
                s += outline(gx + b * gc + 1.5, gy + a * 30 + 1.5, gc - 3, 27, stroke=INK, sw=1.6)
    for b in range(N):
        s += mono(gx + b * gc + gc / 2, gy + 5 * 30 + 13, f"c{b}", size=7.5, fill=SOFT)
    for a in range(N):
        s += mono(gx - 6, gy + a * 30 + 18, f"r{a}", size=7.5, fill=SOFT, anchor="end")
    s += note_lines(x0, 316, note, size=8.5, gap=15)
    return s


def fig02():
    vw, vh = 1016, 404
    s = eyebrow(32, 40, "non-local means compares neighbourhoods: patch distances from two pixels, 3×3 patches")
    s += dist_panel(32, "from the step pixel (r0, c2)", (0, 2),
                    [("an exact copy at (r4, c2): d² = 0, weight 1", ACCENT),
                     ("every close match has 40 at its centre, so (r0, c2) stays 40", INK),
                     ("5,136 = 215² / 9: the copies that also hold the impulse", SOFT)])
    s += f'<line x1="508" y1="84" x2="508" y2="{vh - 36}" stroke="{RULE}" stroke-width="0.8"/>'
    s += dist_panel(532, "from the impulse (r2, c1)", (2, 1),
                    [("no copy: the nearest four are flat 40s at d² = 5,136", ACCENT),
                     ("at h = 20 each weighs e^(−12.8) ≈ 0.000003", INK),
                     ("own weight 1 → 255 · own weight = max → (255 + 4×40) / 5 = 83.0", INK)])
    s += mono(32, vh - 14, "borders mirror without repeating the edge pixel (reflect-101), so the patches at (r0, c0), (r0, c1), (r4, c0) and (r4, c1) are flat",
              size=8, fill=SOFT, anchor="start")
    return emit("02", "patch-distances", "Patch distances from the step and from the impulse",
                "NL-means weighs candidates by the similarity of whole patches. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 452
    s = eyebrow(32, 40, "perona–malik on the patch: three iterations, rational conductance, K = 80, time step 1/4")
    cs, gy = 38, 126
    xs = [40, 286, 532, 778]
    for k, x0 in enumerate(xs):
        M = PM[k]
        s += eyebrow(x0, gy - 32, f"iteration {k}")
        s += grid(x0, gy, cs, M, size=8 if k else 9, nd=1, labels=(k == 0))
        s += outline(x0 + cs, gy + 2 * cs, cs, cs, stroke=ACCENT, sw=2)
        s += (f'<line x1="{x0 + 3 * cs}" y1="{gy - 4}" x2="{x0 + 3 * cs}" y2="{gy + 5 * cs + 4}" '
              f'stroke="{LINK}" stroke-width="1.6" stroke-dasharray="5,3"/>')
        s += mono(x0, gy + 5 * cs + 22, f"impulse {fmt(M[2][1], 2)}", size=8.5, fill=ACCENT, anchor="start",
                  weight="600")
        s += mono(x0, gy + 5 * cs + 37, f"step {fmt(M[0][2], 2)} | {fmt(M[0][3], 2)}", size=8.5, fill=LINK,
                  anchor="start", weight="600")
    s += note_lines(40, gy + 5 * cs + 70,
                    [("each face carries g(difference) × difference, g(s) = 1 / (1 + (s/80)²); a flat face carries nothing", INK),
                     ("step faces conduct g(160) = 0.2: each side moves ¼ × 32 = 8 in iteration 1", LINK),
                     ("impulse faces conduct g(215) = 0.122, but there are four: it loses 215 / 8.223 = 26.15 at once", ACCENT)],
                    size=8.5, gap=15)
    s += mono(32, vh - 16, "orange: the impulse cell · blue dashed: the face between c2 and c3 · no flow through the border · high value = bright",
              size=8, fill=SOFT, anchor="start")
    return emit("03", "perona-malik-three-iterations", "Three iterations of Perona–Malik",
                "K = 80, λ = 1/4, four neighbours, adiabatic border. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def pct(M):
    imp, step = contrasts(M)
    return 100 * step / 160, 100 * imp / 215


def fig04():
    vw, vh = 1016, 540
    s = eyebrow(32, 40, "two features, one trade-off: what each method keeps of the step and of the impulse")
    bil = [pct(full(lambda i, j, sr=sr: bilateral(PATCH, i, j, sr))) for sr in
           (10, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 200, 260, 350, 500, 1000)] + [pct(GAUSS)]
    pm = [pct(PM[k]) for k in range(0, 13)]
    A = Axes(110, 96, 540, 330, (0, 105), (-6, 106))
    s += A.frame([0, 20, 40, 60, 80, 100], [0, 20, 40, 60, 80, 100], xlab="step contrast kept, %",
                 ylab="impulse contrast left, %", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    s += (f'<rect x="{A.X(80):.1f}" y="{A.Y(25):.1f}" width="{A.X(105) - A.X(80):.1f}" '
          f'height="{A.Y(-6) - A.Y(25):.1f}" fill="{SER1}" fill-opacity="0.10"/>')
    s += mono(A.X(80) + 4, A.Y(25) - 17, "wanted: edge kept,", size=8, fill=SER1, anchor="start", weight="600")
    s += mono(A.X(80) + 4, A.Y(25) - 6, "impulse gone", size=8, fill=SER1, anchor="start", weight="600")
    s += polyline([(A.X(x), A.Y(y)) for x, y in bil], C_BIL, sw=2)
    s += polyline([(A.X(x), A.Y(y)) for x, y in pm], C_PM, sw=2)
    for sr in (80, 100, 160):
        x, y = pct(full(lambda i, j: bilateral(PATCH, i, j, sr)))
        s += dot(A.X(x), A.Y(y), 3.4, fill=C_BIL)
        s += mono(A.X(x) - 10, A.Y(y) + 3, f"σr = {sr}", size=8, fill=C_BIL, anchor="end", weight="500")
    for k in (1, 3, 5, 10):
        x, y = pct(PM[k])
        s += dot(A.X(x), A.Y(y), 3.4, fill=C_PM)
        lab = f"{k} iteration{'s' if k > 1 else ''}"
        if k == 10:   # the curve runs flat through the dot here, so the label goes above it
            s += mono(A.X(x), A.Y(y) - 12, lab, size=8, fill=C_PM, weight="500")
        else:
            s += mono(A.X(x) + 10, A.Y(y) + 3, lab, size=8, fill=C_PM, anchor="start", weight="500")
    gx, gy = pct(GAUSS)
    s += dot(A.X(gx), A.Y(gy), 4.4, fill=C_GAUSS)
    s += mono(A.X(gx) - 10, A.Y(gy) - 8, "Gaussian", size=8, fill=MUTED, anchor="end", weight="500")
    s += dot(A.X(100), A.Y(0), 5, fill=C_MEDIAN)
    s += mono(A.X(100) - 10, A.Y(0) + 3, "median", size=8, fill=C_MEDIAN, anchor="end", weight="600")
    s += dot(A.X(100), A.Y(20), 5, fill=C_NLM)
    s += mono(A.X(100) - 10, A.Y(20) + 3, "NL-means, max rule", size=8, fill=C_NLM, anchor="end", weight="600")
    s += f'<circle cx="{A.X(100):.1f}" cy="{A.Y(100):.1f}" r="5" fill="#ffffff" stroke="{C_NLM}" stroke-width="1.6"/>'
    s += mono(A.X(100) - 12, A.Y(100) - 9, "no change: NL-means with own weight 1", size=8, fill=C_NLM,
              anchor="end", weight="600")
    rx = 700
    s += eyebrow(rx, 112, "how to read it")
    s += note_lines(rx, 136, [("blue: the bilateral filter as σr runs", C_BIL),
                              ("from 10 up to ∞, where it is the Gaussian", C_BIL),
                              ("mustard: Perona–Malik, K = 80,", C_PM),
                              ("iterations 0 to 12", C_PM),
                              ("NL-means at h = 20, and the median:", C_NLM),
                              ("single points", C_NLM)], size=8.5, gap=16)
    s += note_lines(rx, 248, [("both contrast curves run from no change,", INK),
                              ("top right, towards the Gaussian; neither", INK),
                              ("enters the shaded corner. Rank (the", INK),
                              ("median) and repetition (NL-means under", INK),
                              ("the max rule) sit on its right edge.", INK)], size=8.5, gap=16)
    s += note_lines(rx, 348, [("impulse contrast: (r2, c1) minus the mean", SOFT),
                              ("of its four neighbours, so spreading the", SOFT),
                              ("impulse counts as lowering it", SOFT),
                              ("step contrast: r0 c3 minus r0 c2", SOFT)], size=8, gap=14)
    s += legend2(vh - 40, vw, [("bilateral", C_BIL, "line"), ("Perona–Malik", C_PM, "line"),
                               ("NL-means, max rule", C_NLM, "dot"), ("NL-means, own weight 1", C_NLM, "ring"),
                               ("median", C_MEDIAN, "dot"), ("Gaussian", C_GAUSS, "dot")])
    return emit("04", "the-trade-off", "Two features, one trade-off",
                "Step contrast kept against impulse contrast left, for every setting of the contrast-based methods. Computed from the definitions.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 492
    s = eyebrow(32, 40, "the range weight is a soft contrast threshold")
    A = Axes(90, 96, 600, 280, (0, 255), (0, 1.05))
    s += A.frame([0, 20, 50, 100, 160, 215, 255], [0, 0.25, 0.5, 0.75, 1.0], xlab=None,
                 ylab="range weight e^(−Δ² / 2σr²)", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", raw=True)
    s += mono(A.x0 + A.w, A.y0 + A.h + 46, "Δ, difference in grey levels", size=8.5, fill=SOFT, anchor="end")
    for xv, col in ((20, SOFT), (160, LINK), (215, ACCENT)):
        xx = A.X(xv)
        s += (f'<line x1="{xx:.1f}" y1="{A.y0}" x2="{xx:.1f}" y2="{A.y0 + A.h}" stroke="{col}" '
              f'stroke-width="1" stroke-dasharray="3,3"/>')
    for sr, col in ((20, SER1), (50, SER2), (80, C_BIL), (160, SER3)):
        pts = [(A.X(d), A.Y(rw(d, sr))) for d in [k * 255 / 300 for k in range(301)]]
        s += polyline(pts, col, sw=2.2 if sr == 80 else 1.5)
    for xv in (20, 160, 215):
        s += dot(A.X(xv), A.Y(rw(xv, 80)), 3.6, fill=C_BIL)
    for sr, col, xv, yv in ((20, SER1, 34, 0.30), (50, SER2, 75, 0.40), (80, C_BIL, 110, 0.45), (160, SER3, 186, 0.57)):
        s += mono(A.X(xv), A.Y(yv), f"σr = {sr}", size=8.5, fill=col, anchor="start", weight="600")
    s += mono(A.X(20), A.y0 + A.h + 27, "bump", size=8, fill=SOFT, weight="600")
    s += mono(A.X(160), A.y0 + A.h + 27, "step", size=8, fill=LINK, weight="600")
    s += mono(A.X(215), A.y0 + A.h + 27, "impulse", size=8, fill=ACCENT, weight="600")
    rx = 730
    s += mono(rx, 112, "at σr = 80", size=8.5, fill=SOFT, anchor="start", weight="600")
    s += note_lines(rx, 136, [("a bump of 20 keeps 0.969:", INK), ("averaged, like a Gaussian", SOFT),
                              ("the step's 160 keeps 0.135", LINK), ("the impulse's 215 keeps 0.027", ACCENT)],
                    size=8.5, gap=16)
    s += note_lines(rx, 230, [("every curve passes 160 before 215:", INK), ("no σr keeps the step while", INK),
                              ("letting the impulse through", INK)], size=8.5, gap=16)
    s += legend2(vh - 42, vw, [("σr = 20", SER1, "line"), ("σr = 50", SER2, "line"), ("σr = 80", C_BIL, "line"),
                               ("σr = 160", SER3, "line")])
    return emit("05", "range-weights", "The range weight is a contrast threshold",
                "Range weight against intensity difference for four values of σr. Evaluated from the definition.",
                "the bilateral filter", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 490
    s = eyebrow(32, 40, "row r2 lifted into position × intensity: the bilateral filter is a gaussian blur in this plane")
    A = Axes(110, 92, 520, 340, (-0.8, 4.8), (0, 320))
    s += A.frame([0, 1, 2, 3, 4], [0, 80, 160, 240], xlab="position along the row", ylab="intensity",
                 xfmt=lambda v: f"c{v}", yfmt=lambda v: f"{v:g}")
    s += (f'<clipPath id="plot06"><rect x="{A.x0}" y="{A.y0}" width="{A.w}" height="{A.h}"/></clipPath>')
    xg = -0.8
    while xg <= 4.8 + 1e-9:
        xx = A.X(xg)
        s += (f'<line x1="{xx:.1f}" y1="{A.y0}" x2="{xx:.1f}" y2="{A.y0 + A.h}" stroke="{RULE}" '
              f'stroke-width="0.8" stroke-dasharray="2,3"/>')
        xg += 0.8
    row = PATCH[2]
    rx_, ry_ = A.X(0.8) - A.X(0), A.Y(0) - A.Y(80)
    s += '<g clip-path="url(#plot06)">'
    for j, v in enumerate(row):
        col = ACCENT if j == 1 else INK
        s += (f'<ellipse cx="{A.X(j):.1f}" cy="{A.Y(v):.1f}" rx="{rx_:.1f}" ry="{ry_:.1f}" fill="{col}" '
              f'fill-opacity="0.06" stroke="{col}" stroke-opacity="0.45" stroke-width="1"/>')
    s += '</g>'
    for j, v in enumerate(row):
        col = ACCENT if j == 1 else INK
        s += dot(A.X(j), A.Y(v), 5, fill=col)
        left = j == 3                      # c3's label would sit on c4's ellipse outline
        s += mono(A.X(j) + (-9 if left else 9), A.Y(v) - 9, f"{v}", size=8.5, fill=col,
                  anchor="end" if left else "start", weight="600")
    xa = A.X(0.5)
    s += f'<line x1="{xa:.1f}" y1="{A.Y(40):.1f}" x2="{xa:.1f}" y2="{A.Y(255):.1f}" stroke="{ACCENT}" stroke-width="1.4"/>'
    s += mono(xa - 10, A.Y(150), "215 = 2.69 σr", size=8.5, fill=ACCENT, anchor="end", weight="600")
    xb = A.X(2.5)
    s += f'<line x1="{xb:.1f}" y1="{A.Y(40):.1f}" x2="{xb:.1f}" y2="{A.Y(200):.1f}" stroke="{LINK}" stroke-width="1.4"/>'
    s += mono(xb - 10, A.Y(140), "160 = 2.00 σr", size=8.5, fill=LINK, anchor="end", weight="600")
    rx = 676
    s += eyebrow(rx, 112, "how the lift works")
    s += note_lines(rx, 136, [("each pixel becomes a point (x, I)", INK),
                              ("blur the points with a 2-D Gaussian", INK),
                              ("σs wide and σr tall (ellipses: 1σ)", SOFT),
                              ("read each pixel at its own (x, I)", INK),
                              ("and divide by the blurred weight", SOFT)], size=8.5, gap=16)
    s += note_lines(rx, 236, [("points far apart in intensity barely", INK),
                              ("mix: the impulse sits 2.69 σr above its", ACCENT),
                              ("neighbours, the step 2.00 σr across", LINK)], size=8.5, gap=16)
    s += note_lines(rx, 304, [("the blurred plane is smooth, so it can be", INK),
                              ("stored at one cell per σs × σr: the", INK),
                              ("bilateral grid, and the fast versions", INK)], size=8.5, gap=16)
    s += note_lines(rx, 372, [("dotted grid: cells 0.8 px wide (σs)", SOFT),
                              ("and 80 levels tall (σr)", SOFT)], size=8, gap=14)
    return emit("06", "position-intensity-lift", "The bilateral filter, lifted",
                "Row r2 in the position–intensity plane, on the grid the fast versions sample. Drawn to scale.",
                "the bilateral filter", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 490
    s = eyebrow(32, 40, "nl-means on the patch as the filtering strength grows: the pixel's own vote decides the impulse")
    hs = [5 + 2.5 * k for k in range(39)]
    imp1 = [nlm(PATCH, 2, 1, h, "one") for h in hs]
    impx = [nlm(PATCH, 2, 1, h, "max") for h in hs]
    st2 = [nlm(PATCH, 0, 2, h, "one") for h in hs]
    st3 = [nlm(PATCH, 0, 3, h, "one") for h in hs]
    A = Axes(90, 96, 600, 300, (5, 100), (0, 285))
    s += A.frame([5, 20, 40, 60, 80, 100], [0, 40, 80, 120, 160, 200, 240], xlab="h, grey levels",
                 ylab="output value", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", raw=True)
    for yv in (40, 200, 255):
        s += (f'<line x1="{A.x0}" y1="{A.Y(yv):.1f}" x2="{A.x0 + A.w}" y2="{A.Y(yv):.1f}" stroke="{SOFT}" '
              f'stroke-width="0.8" stroke-dasharray="2,3"/>')
    for h in (20, 80):
        xx = A.X(h)
        s += f'<line x1="{xx:.1f}" y1="{A.y0 + 16}" x2="{xx:.1f}" y2="{A.y0 + A.h}" stroke="{MUTED}" stroke-width="0.9"/>'
        s += mono(xx, A.y0 + 10, f"h = {h}", size=8, fill=MUTED)
    s += polyline([(A.X(h), A.Y(v)) for h, v in zip(hs, imp1)], C_NLM, sw=1.8, dash="5,3")
    s += polyline([(A.X(h), A.Y(v)) for h, v in zip(hs, impx)], C_NLM, sw=2)
    s += polyline([(A.X(h), A.Y(v)) for h, v in zip(hs, st2)], C_BIL, sw=1.6)
    s += polyline([(A.X(h), A.Y(v)) for h, v in zip(hs, st3)], C_BIL, sw=1.6)
    i80 = nlm(PATCH, 2, 1, 80, "one")
    s += dot(A.X(20), A.Y(255), 3.4, fill=C_NLM) + dot(A.X(20), A.Y(83), 3.4, fill=C_NLM)
    s += dot(A.X(80), A.Y(i80), 3.4, fill=C_NLM)
    s += dot(A.X(80), A.Y(82.04), 3.4, fill=C_BIL) + dot(A.X(80), A.Y(170.36), 3.4, fill=C_BIL)
    s += mono(A.X(20) + 7, A.Y(255) + 14, "255", size=8.5, fill=C_NLM, anchor="start", weight="600")
    s += mono(A.X(20) + 7, A.Y(83) + 14, "83.0", size=8.5, fill=C_NLM, anchor="start", weight="600")
    s += mono(A.X(80) + 7, A.Y(i80) - 7, "110.7", size=8.5, fill=C_NLM, anchor="start", weight="600")
    s += mono(A.X(80) + 7, A.Y(170.36) - 7, "170.4", size=8.5, fill=C_BIL, anchor="start", weight="600")
    s += mono(A.X(80) + 7, A.Y(82.04) + 15, "82.0", size=8.5, fill=C_BIL, anchor="start", weight="600")
    rx = 730
    s += eyebrow(rx, 112, "what the curves say")
    s += note_lines(rx, 136, [("own weight 1 (OpenCV, scikit-image):", C_NLM),
                              ("the impulse stays 255 until h is", INK), ("large enough to blur the step too", INK)],
                    size=8.5, gap=16)
    s += note_lines(rx, 196, [("own weight = max (IPOL):", C_NLM), ("four flat patches outvote it: 83.0", INK),
                              ("for every h up to about 30, with", INK), ("the step exact", INK)], size=8.5, gap=16)
    s += note_lines(rx, 272, [("the step pixels (blue) have an exact", C_BIL), ("copy, so both rules agree on them", INK)],
                    size=8.5, gap=16)
    s += legend2(vh - 42, vw, [("impulse, own weight 1", C_NLM, "dash"), ("impulse, max rule", C_NLM, "line"),
                               ("step pixels r0 c2 and c3", C_BIL, "line")])
    return emit("07", "nl-means-against-h", "NL-means against h, under two self-weight rules",
                "The impulse and the step's two sides as h grows. Computed from the definitions on the patch.",
                "non-local means", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "the flux across a face, difference × conductance, for K = 80")
    A = Axes(90, 96, 600, 280, (0, 255), (0, 70))
    s += A.frame([0, 20, 80, 160, 215, 255], [0, 10, 20, 30, 40, 50, 60, 70], xlab="s, the difference across a face",
                 ylab="flux s · g(s)", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}", raw=True)
    s += (f'<rect x="{A.X(80):.1f}" y="{A.y0}" width="{A.X(255) - A.X(80):.1f}" height="{A.h}" fill="{MUTED}" '
          f'fill-opacity="0.06"/>')
    s += mono(A.X(84), A.y0 + 14, "beyond K: a bigger jump leaks less", size=8, fill=SOFT, anchor="start")
    ss = [k * 255 / 400 for k in range(401)]
    s += polyline([(A.X(x), A.Y(x)) for x in ss if x <= 70], SOFT, sw=1.2, dash="4,3")
    s += mono(A.X(8), A.Y(60) + 3, "heat equation: flux = s", size=8, fill=SOFT, anchor="start")
    s += polyline([(A.X(x), A.Y(x * g_rat(x))) for x in ss], C_PM, sw=2)
    s += polyline([(A.X(x), A.Y(x * g_exp(x))) for x in ss], SER2, sw=1.6)
    for xv, col in ((20, SOFT), (160, LINK), (215, ACCENT)):
        xx = A.X(xv)
        top = A.Y(xv * g_rat(xv)) + 6
        s += (f'<line x1="{xx:.1f}" y1="{top:.1f}" x2="{xx:.1f}" y2="{A.y0 + A.h}" stroke="{col}" '
              f'stroke-width="1" stroke-dasharray="3,3"/>')
        s += dot(xx, A.Y(xv * g_rat(xv)), 3.6, fill=C_PM)
    s += mono(A.X(160), A.Y(32) - 10, "32", size=8.5, fill=C_PM, weight="600")
    s += mono(A.X(215), A.Y(26.15) - 10, "26.15", size=8.5, fill=C_PM, weight="600")
    s += mono(A.X(20) + 9, A.Y(20 * g_rat(20)) + 14, "18.8", size=8.5, fill=C_PM, anchor="start", weight="600")
    s += mono(A.X(80) + 6, A.Y(40) - 10, "peak 40 at s = K", size=8.5, fill=C_PM, anchor="start", weight="600")
    rx = 730
    s += mono(rx, 112, "rational g, K = 80", size=8.5, fill=SOFT, anchor="start", weight="600")
    s += note_lines(rx, 136, [("below K the flux grows with the jump:", INK), ("ordinary smoothing", SOFT),
                              ("above K it shrinks: the step (160) and", INK), ("the impulse (215) both leak slowly", INK)],
                    size=8.5, gap=16)
    s += note_lines(rx, 216, [("a 20-level bump is on the rising side", INK), ("and diffuses almost as in the heat equation", SOFT)],
                    size=8.5, gap=16)
    s += note_lines(rx, 264, [("the exponential g passes only 2.9", SER2), ("at 160 and 0.16 at 215: it all but", SER2),
                              ("stops both features", SER2)], size=8.5, gap=16)
    s += legend2(vh - 42, vw, [("rational g = 1 / (1 + (s/K)²)", C_PM, "line"),
                               ("exponential g = e^(−(s/K)²)", SER2, "line"), ("heat equation", SOFT, "dash")])
    return emit("08", "flux", "The flux across a face",
                "Flux s · g(s) for Perona and Malik's two conductances at K = 80. Evaluated from the definitions.",
                "diffusion", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "perona–malik on the patch, K = 80: both features drain, and the patch ends at its mean, 112.6")
    lx = lambda t: math.log(1 + t)
    A = Axes(90, 96, 380, 280, (0, 100), (-10, 220), xmap=lx)
    B = Axes(560, 96, 380, 280, (0, 100), (0, 260), xmap=lx)
    ticks = [0, 1, 2, 3, 5, 10, 20, 50, 100]
    s += A.frame(ticks, [0, 50, 100, 150, 200], xlab="iteration (log scale)", ylab="contrast",
                 xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    s += B.frame(ticks, [0, 40, 112.6, 200, 255], xlab="iteration (log scale)", ylab="pixel value",
                 xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    imp = [contrasts(PM[k])[0] for k in range(101)]
    stp = [contrasts(PM[k])[1] for k in range(101)]
    s += polyline([(A.X(k), A.Y(v)) for k, v in enumerate(imp)], ACCENT, sw=2)
    s += polyline([(A.X(k), A.Y(v)) for k, v in enumerate(stp)], LINK, sw=2)
    for k in (3, 5, 10):
        s += dot(A.X(k), A.Y(imp[k]), 3.2, fill=ACCENT) + dot(A.X(k), A.Y(stp[k]), 3.2, fill=LINK)
    s += mono(A.X(3) + 8, A.Y(stp[3]) - 8, "118.1", size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(A.X(3) - 8, A.Y(imp[3]) + 3, "102.5", size=8.5, fill=ACCENT, anchor="end", weight="600")
    s += mono(A.X(5) + 8, A.Y(stp[5]) - 8, "92.4", size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(A.X(5) - 8, A.Y(imp[5]) + 3, "13.4", size=8.5, fill=ACCENT, anchor="end", weight="600")
    s += mono(A.X(10) + 8, A.Y(stp[10]) - 8, "39.2", size=8.5, fill=LINK, anchor="start", weight="600")
    tracks = [((2, 1), ACCENT), ((0, 2), LINK), ((0, 3), SER2), ((0, 0), SER1)]
    for (i, j), col in tracks:
        s += polyline([(B.X(k), B.Y(PM[k][i][j])) for k in range(101)], col, sw=1.8)
    s += (f'<line x1="{B.x0}" y1="{B.Y(112.6):.1f}" x2="{B.x0 + B.w}" y2="{B.Y(112.6):.1f}" stroke="{INK}" '
          f'stroke-width="0.9" stroke-dasharray="4,3"/>')
    s += mono(B.x0 + 8, B.Y(112.6) - 8, "mean 112.6 = 2,815 / 25", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(A.x0, A.y0 + A.h + 48, "contrast: the impulse minus its four neighbours' mean; the step, r0 c3 minus r0 c2",
              size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 36, vw, [("impulse (r2, c1)", ACCENT, "line"), ("step, or its dark side (r0, c2)", LINK, "line"),
                               ("bright side (r0, c3)", SER2, "line"), ("flat corner (r0, c0)", SER1, "line")])
    return emit("09", "stopping-time", "Why diffusion needs a stopping time",
                "Contrast and pixel values over 100 iterations. Iterated from the scheme's definition.",
                "diffusion", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
COST = [("Gaussian 3×3, separable", 6, C_GAUSS, "3 + 3 taps"),
        ("median 3×3", 9, C_MEDIAN, "sort 9 values"),
        ("bilateral, OpenCV d = 5", 13, C_BIL, "a disc of 13 taps"),
        ("bilateral, d = 9 or skimage 7×7", 49, C_BIL, "49 taps"),
        ("Perona–Malik, 10 iterations", 40, C_PM, "4 face differences × 10"),
        ("Perona–Malik, 100 iterations", 400, C_PM, "4 face differences × 100"),
        ("NL-means, integral images", 441, C_NLM, "21² window shifts, a few reads each"),
        ("NL-means, naive, 7×7 in 21×21", 21609, C_NLM, "21² × 7² pixel differences")]


def fig10():
    vw, vh = 1016, 504
    s = eyebrow(32, 40, "work per output pixel, counted from each definition (not measured)")
    x0, w = 330, 520
    X = lambda v: x0 + math.log10(v) / 5 * w
    y0, gap = 92, 40
    base = y0 + len(COST) * gap
    for t in (1, 10, 100, 1000, 10000, 100000):
        xx = X(t)
        s += f'<line x1="{xx:.1f}" y1="{y0 - 8}" x2="{xx:.1f}" y2="{base}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(xx, base + 14, f"{t:,}", size=8, fill=SOFT)
    s += f'<line x1="{x0}" y1="{y0 - 8}" x2="{x0}" y2="{base}" stroke="{RULE_SOLID}"/>'
    for k, (lab, v, col, how) in enumerate(COST):
        y = y0 + k * gap
        s += mono(32, y + 10, lab, size=9, fill=INK, anchor="start", weight="500")
        s += mono(32, y + 24, how, size=8, fill=SOFT, anchor="start")
        s += (f'<rect x="{x0}" y="{y}" width="{X(v) - x0:.1f}" height="22" fill="{col}" fill-opacity="0.85"/>')
        s += mono(X(v) + 8, y + 15, f"{v:,}", size=9, fill=INK, anchor="start", weight="600")
    s += mono(x0 + w, base + 30, "work per output pixel in each method's own unit, log scale", size=8.5, fill=SOFT,
              anchor="end")
    s += mono(32, vh - 30, "one integral-image shift costs a few reads per pixel whatever the patch size; Perona–Malik pays per iteration",
              size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "a disc of radius 2 holds 13 pixels and of radius 4, 49; NL-means at OpenCV's defaults, 7×7 patches in a 21×21 window",
              size=8, fill=SOFT, anchor="start")
    return emit("10", "cost-per-pixel", "What each method costs per pixel",
                "Work per output pixel for the median, the bilateral filter, Perona–Malik and NL-means. Counted, not run.",
                "cost", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "which call does what, its default, and the trap — mapped from source, not run")
    cols = [("call", 32), ("what it computes", 360), ("default", 590), ("trap", 776)]
    y0 = 74
    for h, x in cols:
        s += mono(x, y0, h, size=8, fill=SOFT, anchor="start", track="0.08em")
    s += f'<line x1="32" y1="{y0 + 10}" x2="{vw - 32}" y2="{y0 + 10}" stroke="{RULE_SOLID}"/>'
    rows = [
        ("OpenCV", "bilateralFilter(img, d, sigmaColor, sigmaSpace)", "disc window; colour = L1 sum", "d ≤ 0: radius 1.5 × sigmaSpace", "d = 3 is 5 taps, not 9"),
        ("OpenCV", "fastNlMeansDenoising(img, None, h)", "patch MSE; own weight 1", "h 3, patch 7, window 21", "a lone pixel Δ > ~55 is kept"),
        ("OpenCV", "fastNlMeansDenoisingColored", "CIELAB inside", "h = hColor = 3", "h for L, hColor for a and b"),
        ("contrib", "ximgproc.anisotropicDiffusion", "exponential g; 8 neighbours", "8-bit 3-channel only", "alpha ≤ 1/8, docs say 0–1"),
        ("skimage", "denoise_bilateral(img, ...)", "square window; zero border", "σ colour = image std, 7×7", "ints become 0–1 units"),
        ("skimage", "denoise_bilateral, spatial table", "win_size + 1 points read as win_size", "commit b700edc", "read, not run: check"),
        ("skimage", "denoise_nl_means(img, h, ...)", "own weight 1; cut-off e^−5", "h 0.1 (25.5 levels), 7, 11", "h is not OpenCV's h"),
        ("ITK", "GradientAnisotropicDiffusion", "exponential g; K × RMS gradient", "time step 0.125 (2-D)", "warns above 0.125"),
        ("MedPy", "anisotropic_diffusion(img, ...)", "options: exp, rational, Tukey", "kappa 50, gamma 0.1", "gamma ≤ 0.25"),
        ("this post", "equations (2), (3), (4) by hand", "3×3 square; h = 20; K = 80", "σr = 80, λ = 1/4", "own weight: say which"),
    ]
    libcol = {"OpenCV": SER2, "contrib": SER2, "skimage": SER1, "ITK": SER3, "MedPy": SER4, "this post": ACCENT}
    for k, (lib, call, what, dflt, trap) in enumerate(rows):
        y = y0 + 34 + k * 44
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 18}" width="{vw - 56}" height="44" fill="rgba(45,49,66,0.03)"/>'
        s += mono(32, y - 4, lib, size=7, fill=libcol[lib], anchor="start", track="0.12em", weight="600")
        s += mono(32, y + 10, call, size=8.5, fill=INK, anchor="start", weight="500")
        s += mono(360, y + 4, what, size=8.5, fill=MUTED, anchor="start")
        s += mono(590, y + 4, dflt, size=8.5, fill=INK, anchor="start")
        s += mono(776, y + 4, trap, size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(32, vh - 16, "pinned commits: OpenCV 802cf95, opencv_contrib 6484ab2, scikit-image b700edc, ITK dfef081, MedPy d6abf41",
              size=8, fill=SOFT, anchor="start")
    return emit("11", "tooling-map", "The tooling map",
                "Windows, units, self-weights and stability limits for the three methods in five libraries. None of it was executed.",
                "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
