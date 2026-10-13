#!/usr/bin/env python3
"""The numbers behind scale-space-and-sift, computed from definitions and asserted against the article.

The patch enlarged by m (each pixel an m x m block, its border extended outward) is
40 + 160*[x > 3m - 0.5] + 215*[block (r2, c1)], so its Gaussian scale space is a closed form in the
normal CDF. Everything here is evaluated from that closed form at pixel centres: the DoG octave, the
26-neighbour test, the quadratic fit, the contrast and edge tests, the normalised Laplacian, the
fixed-level maps, the scale-adapted Harris measure. OpenCV's behaviour comes from _replay.py, a
plain-Python replay of its SIFT rules. Nothing is measured and nothing loads an image.
"""
import math

from _replay import patch as rpatch, sift_detect

SQ2 = math.sqrt(2.0)


def Phi(z):
    return 0.5 * (1.0 + math.erf(z / SQ2))


def phi(z):
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


def dphi(z):
    return -z * phi(z)


class Enlarged:
    def __init__(self, m):
        self.m, self.n = m, 5 * m
        self.xs = 3 * m - 0.5
        self.x1, self.x2 = m - 0.5, 2 * m - 0.5
        self.y1, self.y2 = 2 * m - 0.5, 3 * m - 0.5

    def L(self, x, y, s):
        bx = Phi((x - self.x1) / s) - Phi((x - self.x2) / s)
        by = Phi((y - self.y1) / s) - Phi((y - self.y2) / s)
        return 40 + 160 * Phi((x - self.xs) / s) + 215 * bx * by

    def N(self, x, y, s):
        """Scale-normalised Laplacian sigma^2 (Lxx + Lyy), analytic."""
        zx1, zx2 = (x - self.x1) / s, (x - self.x2) / s
        zy1, zy2 = (y - self.y1) / s, (y - self.y2) / s
        bx, by = Phi(zx1) - Phi(zx2), Phi(zy1) - Phi(zy2)
        bxx, byy = dphi(zx1) - dphi(zx2), dphi(zy1) - dphi(zy2)
        return 160 * dphi((x - self.xs) / s) + 215 * (bxx * by + bx * byy)

    def grad(self, x, y, s):
        """(Lx, Ly) at scale s, analytic."""
        bx = Phi((x - self.x1) / s) - Phi((x - self.x2) / s)
        by = Phi((y - self.y1) / s) - Phi((y - self.y2) / s)
        dbx = (phi((x - self.x1) / s) - phi((x - self.x2) / s)) / s
        dby = (phi((y - self.y1) / s) - phi((y - self.y2) / s)) / s
        return 160 * phi((x - self.xs) / s) / s + 215 * dbx * by, 215 * bx * dby


P5, P7, P14 = Enlarged(5), Enlarged(7), Enlarged(14)
K = 2 ** (1 / 3)
SIG = [1.6 * K ** i for i in range(6)]
INC = [math.sqrt(SIG[i] ** 2 - SIG[i - 1] ** 2) for i in range(1, 6)]


def gauss_stack(P, sigs):
    return [[[P.L(x, y, s) for x in range(P.n)] for y in range(P.n)] for s in sigs]


def dog_stack(G):
    n = len(G[0])
    return [[[G[i + 1][y][x] - G[i][y][x] for x in range(n)] for y in range(n)] for i in range(len(G) - 1)]


def dog_level(P, s1, s2):
    return [[P.L(x, y, s2) - P.L(x, y, s1) for x in range(P.n)] for y in range(P.n)]


G7 = gauss_stack(P7, SIG)
D7 = dog_stack(G7)


def candidates(D, s=3):
    out = []
    n = len(D[0])
    for i in range(1, s + 1):
        for y in range(1, n - 1):
            for x in range(1, n - 1):
                v = D[i][y][x]
                nb = [D[i + a][y + b][x + c] for a in (-1, 0, 1) for b in (-1, 0, 1) for c in (-1, 0, 1)
                      if a or b or c]
                if v < min(nb) or v > max(nb):
                    out.append((i, x, y, v))
    return out


def solve3(H, g):
    def det3(M):
        return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1])
                - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    d = det3(H)
    out = []
    for col in range(3):
        M = [row[:] for row in H]
        for r in range(3):
            M[r][col] = g[r]
        out.append(det3(M) / d)
    return out


def fit(D, i, x, y):
    """Brown-Lowe fit and both tests, in grey levels (OpenCV divides by 255)."""
    v = D[i][y][x]
    g = [(D[i][y][x + 1] - D[i][y][x - 1]) / 2, (D[i][y + 1][x] - D[i][y - 1][x]) / 2,
         (D[i + 1][y][x] - D[i - 1][y][x]) / 2]
    dxx = D[i][y][x + 1] + D[i][y][x - 1] - 2 * v
    dyy = D[i][y + 1][x] + D[i][y - 1][x] - 2 * v
    dss = D[i + 1][y][x] + D[i - 1][y][x] - 2 * v
    dxy = (D[i][y + 1][x + 1] - D[i][y + 1][x - 1] - D[i][y - 1][x + 1] + D[i][y - 1][x - 1]) / 4
    dxs = (D[i + 1][y][x + 1] - D[i + 1][y][x - 1] - D[i - 1][y][x + 1] + D[i - 1][y][x - 1]) / 4
    dys = (D[i + 1][y + 1][x] - D[i + 1][y - 1][x] - D[i - 1][y + 1][x] + D[i - 1][y - 1][x]) / 4
    H = [[dxx, dxy, dxs], [dxy, dyy, dys], [dxs, dys, dss]]
    off = [-t for t in solve3(H, g)]
    contr = v + 0.5 * sum(a * b for a, b in zip(g, off))
    tr, det = dxx + dyy, dxx * dyy - dxy * dxy
    disc = math.sqrt(max(tr * tr / 4 - det, 0.0))
    l1, l2 = tr / 2 + disc, tr / 2 - disc
    ratio = max(abs(l1), abs(l2)) / min(abs(l1), abs(l2))
    return dict(v=v, g=g, H=H, off=off, contr=contr, tr=tr, det=det, test=tr * tr / det, ratio=ratio,
                sigma=1.6 * 2 ** ((i + off[2]) / 3))


def r(v, nd=3):
    return round(v + 0.0, nd)


def golden_max(f, a, b, tol=1e-10):
    gr = (math.sqrt(5) - 1) / 2
    c, d = b - gr * (b - a), a + gr * (b - a)
    while abs(b - a) > tol:
        if f(c) > f(d):
            b = d
        else:
            a = c
        c, d = b - gr * (b - a), a + gr * (b - a)
    return (a + b) / 2


# ------------------------------------------------------------------ the worked example
CX, CY, GX_, GY_ = 10, 17, 17, 17
assert [r(D7[i][CY][CX]) for i in range(5)] == [-21.855, -32.216, -35.379, -31.417, -23.124]
BLOCK = [[[D7[i][y][x] for x in (9, 10, 11)] for y in (16, 17, 18)] for i in (1, 2, 3)]
assert [r(v) for v in BLOCK[0][0]] == [-29.038, -30.586, -29.024]
assert [r(v) for v in BLOCK[0][1]] == [-30.589, -32.216, -30.575]
assert [r(v) for v in BLOCK[1][0]] == [-31.126, -33.169, -30.927]
assert [r(v) for v in BLOCK[1][1]] == [-33.223, -35.379, -33.024]
assert [r(v) for v in BLOCK[2][0]] == [-28.432, -29.723, -27.516]
assert [r(v) for v in BLOCK[2][1]] == [-30.056, -31.417, -29.140]
assert all(abs(BLOCK[i][0][j] - BLOCK[i][2][j]) < 1e-9 for i in range(3) for j in range(3))   # symmetric about row 17
_nb = [v for i in range(3) for y in range(3) for x in range(3) for v in [BLOCK[i][y][x]] if (i, y, x) != (1, 1, 1)]
assert BLOCK[1][1][1] < min(_nb) and r(min(_nb)) == -33.223
CANDS = candidates(D7)
assert [(c[0], c[1], c[2]) for c in CANDS] == [(2, 10, 17), (2, 17, 17)] and r(CANDS[1][3]) == 14.740
FB, FG = fit(D7, 2, CX, CY), fit(D7, 2, GX_, GY_)
assert [r(v, 4) for v in FB["g"]] == [0.0995, 0.0, 0.3993]
assert [[r(v, 4) for v in row] for row in FB["H"]] == [[4.5102, 0.0, 0.2256], [0.0, 4.4198, 0.0], [0.2256, 0.0, 7.1241]]
assert [r(v, 4) for v in FB["off"]] == [-0.0193, 0.0, -0.0554]
assert r(FB["contr"]) == -35.391 and r(abs(FB["contr"]) / 255) == 0.139 and r(FB["sigma"]) == 2.508
assert r(FB["test"], 4) == 4.0004 and r(FB["ratio"], 2) == 1.02 and r(FB["H"][0][0]) == 4.510 and r(FB["H"][1][1]) == 4.420
assert [r(v, 2) for v in FG["off"]] == [0.38, 0.0, -0.12] and r(FG["contr"]) == 15.073 and r(FG["contr"] / 255) == 0.059
assert r(FG["H"][0][0]) == -3.804 and r(FG["H"][1][1]) == -0.180 and r(FG["test"], 1) == 23.2 and r(FG["ratio"], 1) == 21.1
T_BLOB, T_GAP = 1 / FB["ratio"], 1 / FG["ratio"]
assert r(T_GAP) == 0.047 and r(T_BLOB, 2) == 0.98 and T_GAP / (1 + T_GAP) ** 2 > 0.04 and T_GAP / (1 + T_GAP) ** 2 < 10 / 121
assert [r(s) for s in SIG] == [1.6, 2.016, 2.54, 3.2, 4.032, 5.08] and [r(v) for v in INC] == [1.226, 1.545, 1.947, 2.453, 3.09]
assert r(math.sqrt(1.6 ** 2 - 1.0), 3) == 1.249 and round(math.log2(70) - 2) + 1 == 5
_par = (D7[3][CY][CX] - D7[1][CY][CX]) / 2, (D7[3][CY][CX] + D7[1][CY][CX] - 2 * D7[2][CY][CX])
PAR_OFF = -0.5 * _par[0] / (_par[1] / 2)
assert r(PAR_OFF, 3) == -0.056 and r(1.6 * 2 ** ((2 + PAR_OFF) / 3)) == 2.507
assert r(-0.3995 / 7.125, 4) == -0.0561            # E1, from the three-decimal values the article prints

# ------------------------------------------------------------------ sizes, curves, covariance
f_sq = lambda u: u * phi(u) * (2 * Phi(u) - 1)                     # -N / (4A) at a square's centre
U_STAR = golden_max(f_sq, 0.5, 3.0)
assert r(U_STAR, 4) == 1.2554 and r(1 / (2 * U_STAR), 4) == 0.3983 and r(4 * f_sq(U_STAR), 3) == 0.720
assert r(1 / math.sqrt(2 * math.pi), 4) == 0.3989 and r(4 * f_sq(U_STAR) * 215, 1) == 154.9
SIDES = [3, 5, 7, 14]
assert [r(l / (2 * U_STAR), 2) for l in SIDES] == [1.19, 1.99, 2.79, 5.58]
N_SQ = lambda l, s: 860 * f_sq(l / (2 * s))                       # magnitude, contrast 215
AT254 = [N_SQ(l, SIG[2]) for l in SIDES]
assert [r(v, 1) for v in AT254] == [75.8, 140.4, 152.2, 21.1]
S_LOG = golden_max(lambda s: -P7.N(CX, CY, s), 1.0, 6.0)
D_CONT = lambda s: P7.L(CX, CY, K * s) - P7.L(CX, CY, s)
S_DOG = golden_max(lambda s: -D_CONT(s), 1.0, 6.0)
assert r(S_LOG) == 2.776 and r(P7.N(CX, CY, S_LOG)) == -154.671 and r(S_DOG) == 2.48 and r(D_CONT(S_DOG), 2) == -35.42
assert r(S_LOG / S_DOG) == 1.119 and r(math.sqrt(K)) == 1.122 and r(abs(D_CONT(S_DOG) / P7.N(CX, CY, S_LOG))) == 0.229
assert (r(K - 1), r((K * K - 1) / 2), r(math.log(K))) == (0.26, 0.294, 0.231)
U_DOG = 3 * math.log2(S_DOG / 1.6)                                 # continuous level of the DoG minimum
assert r(1.6 * 2 ** (U_DOG / 3)) == 2.48 and r(abs(FB["sigma"] - S_DOG) / S_DOG, 2) == 0.01
assert (r(160 * phi(1), 1), r(160 * phi(0), 1)) == (38.7, 63.8)

# fixed level: the DoG between sigma 2.540 and 3.200 on the x7 and x14 patches, and x14 at twice the sigma
FIX7 = dog_level(P7, SIG[2], SIG[3])
FIX14 = dog_level(P14, SIG[2], SIG[3])
TWICE14 = dog_level(P14, 2 * SIG[2], 2 * SIG[3])


def strict_extrema(M):
    n = len(M)
    out = []
    for y in range(1, n - 1):
        for x in range(1, n - 1):
            v = M[y][x]
            nb = [M[y + b][x + a] for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b]
            if v < min(nb) or v > max(nb):
                out.append((x, y, v))
    return out


EX7, EX14 = strict_extrema(FIX7), strict_extrema(FIX14)
assert [(x, y, r(v, 2)) for x, y, v in EX7] == [(3, 17, 6.27), (10, 17, -35.38), (17, 17, 14.74)]
MIN14 = [(x, y) for x, y, v in EX14 if v < -15]          # the deep wells; the centre pixels tie near -10.06
assert MIN14 == [(17, 31), (24, 31), (17, 38), (24, 38)] and {r(v, 2) for x, y, v in EX14 if v < -15} == {-20.43}
assert r(FIX14[34][21], 2) == r(FIX14[35][21], 2) == -10.06 and min(v for row in FIX14 for v in row) > -20.44
assert [(x, y, r(v, 1)) for x, y, v in EX14 if v > 0] == [(21, 24, 10.6), (21, 45, 10.6)]
C14 = P14.L(20.5, 34.5, SIG[3]) - P14.L(20.5, 34.5, SIG[2])
assert r(C14, 2) == -9.66
C14T = P14.L(20.5, 34.5, 2 * SIG[3]) - P14.L(20.5, 34.5, 2 * SIG[2])
assert abs(C14T - D7[2][CY][CX]) < 1e-9                             # exact scaling: x14 at 2 sigma = x7 at sigma

# Harris-Laplace on the x7 patch: levels 1.4^n, sigma_D = 0.7 sigma_I, Gaussian window
LV = [1.4 ** n for n in range(1, 6)]


def harris_maxima(sI, alpha=0.04, xr=(3, 22), yr=(10, 24)):
    sD = 0.7 * sI
    R = int(math.ceil(4 * sI))
    w = {(a, b): math.exp(-(a * a + b * b) / (2 * sI * sI)) for a in range(-R, R + 1) for b in range(-R, R + 1)}
    G = {(x, y): P7.grad(x, y, sD) for x in range(xr[0] - R - 1, xr[1] + R + 2) for y in range(yr[0] - R - 1, yr[1] + R + 2)}
    H = {}
    for y in range(yr[0] - 1, yr[1] + 2):
        for x in range(xr[0] - 1, xr[1] + 2):
            a = b = c = 0.0
            for (dx, dy), ww in w.items():
                gx, gy = G[(x + dx, y + dy)]
                a += ww * gx * gx
                b += ww * gx * gy
                c += ww * gy * gy
            H[(x, y)] = a * c - b * b - alpha * (a + c) ** 2
    return [(x, y) for y in range(yr[0], yr[1] + 1) for x in range(xr[0], xr[1] + 1)
            if H[(x, y)] > 0 and all(H[(x, y)] > H[(x + a, y + b)] for a in (-1, 0, 1) for b in (-1, 0, 1) if a or b)]


assert harris_maxima(1.4 ** 2) == [(8, 15), (12, 15), (8, 19), (12, 19)]
assert harris_maxima(1.4 ** 3) == [(10, 17)] and harris_maxima(1.4 ** 4) == [(10, 17)]
HL_C = [P7.N(CX, CY, s) for s in LV]
HL_K = [P7.N(8, 15, s) for s in LV]
assert [r(v, 1) for v in HL_C] == [-37.2, -115.2, -154.6, -127.5, -69.1]
assert [r(v, 1) for v in HL_K[:4]] == [-89.1, -83.2, -86.9, -85.4]
assert [r(P7.N(x, y, 1.96), 1) for x, y in ((12, 15), (8, 19), (12, 19))] == [-83.2, -83.2, -83.2]

# ------------------------------------------------------------------ OpenCV, replayed
KP7D, _, INFO7 = sift_detect(rpatch(7), precise=False)
KP7P, _, _ = sift_detect(rpatch(7), precise=True)
assert INFO7["sizes"] == [70, 35, 17, 8, 4] and [r(v, 4) for v in INFO7["sig"][1:]] == [1.2263, 1.545, 1.9466, 2.4525, 3.09]
assert {(r(k["pt"][0], 2), r(k["pt"][1], 2), r(k["size"], 2)) for k in KP7D} == {(10.23, 17.25, 5.02)} and len(KP7D) == 2
assert {(r(k["pt"][0], 2), r(k["pt"][1], 2), r(k["size"], 2)) for k in KP7P} == {(9.98, 17.0, 5.03)}
assert sorted(r(k["angle"], 1) for k in KP7P) == [0.0, 90.6, 269.4]
assert all(k["o"] == 1 and k["layer"] == 2 for k in KP7D + KP7P)
HIST_P, HIST_D = KP7P[0]["hist"], KP7D[0]["hist"]


def peaks(h):
    mx = max(h)
    return [(j, h[j] / mx) for j in range(36) if h[j] > h[(j - 1) % 36] and h[j] > h[(j + 1) % 36]]


assert [(j, r(q, 3)) for j, q in peaks(HIST_P) if q > 0.6] == [(0, 1.0), (9, 0.826), (12, 0.733), (18, 0.665), (24, 0.733), (27, 0.826)]
assert [(j, r(q, 3)) for j, q in peaks(HIST_D)] == [(0, 1.0), (10, 0.789), (17, 0.658), (27, 0.855)]
KP14P, _, _ = sift_detect(rpatch(14), precise=True)
_c14 = [k for k in KP14P if k["o"] == 2]
assert {(r(k["pt"][0], 2), r(k["pt"][1], 2), r(k["size"], 2)) for k in _c14} == {(20.46, 34.5, 10.03)}
assert abs(_c14[0]["pt"][0] - (2 * KP7P[0]["pt"][0] + 0.5)) < 0.005 and abs(_c14[0]["pt"][1] - 34.5) < 0.005
assert {r(k["size"] / 2, 1) for k in KP14P if k["o"] == 1} == {2.2}
KP14D, _, _ = sift_detect(rpatch(14), precise=False)
assert all(k["o"] == 2 for k in KP14D)                              # no corners with the default upscale
assert sift_detect(rpatch(1))[0] == []                              # the 5x5 patch: nothing
KP5P, _, _ = sift_detect(rpatch(5), precise=True)
assert {(r(k["pt"][0], 2), r(k["pt"][1], 2), r(k["size"] / 2, 2), k["layer"], r(k["xi"], 2)) for k in KP5P} == {(6.99, 12.0, 1.78, 3, 0.47)}
KP5D, _, _ = sift_detect(rpatch(5), precise=False)
assert len(KP5D) == 2 and all(r(k["pt"][0], 1) == 12.5 for k in KP5D)   # the gap, not the square
assert (r(P5.L(7, 12, SIG[1]) - P5.L(7, 12, SIG[0]), 2), r(P5.L(7, 12, SIG[2]) - P5.L(7, 12, SIG[1]), 2)) == (-34.66, -34.31)
_sq = 2.5147                                                          # kept keypoint's sigma, precise mode
assert r(KP7P[0]["size"] / 2, 2) == 2.51 and round(4.5 * KP7P[0]["size"] / 2) == 11 and r(1.5 * KP7P[0]["size"] / 2, 1) == 3.8
assert r(3 * KP7P[0]["size"] / 2, 1) == 7.5 and round(12 * KP7P[0]["size"] / 2) == 30


# ------------------------------------------------------------------ the box counterexample (Figure 8)
def box1d(f, w):
    h, n = (w - 1) // 2, len(f)
    return [sum(f[min(max(i + j, 0), n - 1)] for j in range(-h, h + 1)) / w for i in range(n)]


BOXF = [2, 9, 1, 4, 1, 7, 7, 7, 6]
_b5, _b7 = box1d(BOXF, 5), box1d(BOXF, 7)
assert _b5[3] > _b5[2] and _b5[3] > _b5[4] and r(_b5[3], 2) == 4.4 and r(_b7[3], 2) == 4.43
