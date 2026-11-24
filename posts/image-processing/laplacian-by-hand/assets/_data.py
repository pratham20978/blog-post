#!/usr/bin/env python3
"""Every number the post and its figures print, computed in plain Python and asserted.

Run `python3 _data.py` after any edit: an assertion failure means the article and the
arithmetic disagree. `_figs.py` imports its numbers from here, so a figure cannot print a
value the article does not.
"""
import math
from fractions import Fraction as Fr

# ------------------------------------------------------------------ the patch
CLEAN = [[40, 40, 40, 200, 200] for _ in range(5)]
PATCH = [r[:] for r in CLEAN]
PATCH[2][1] = 255


def lap5(f, r, c):
    return f[r - 1][c] + f[r + 1][c] + f[r][c - 1] + f[r][c + 1] - 4 * f[r][c]


def nbr_sum(f, r, c):
    return f[r - 1][c] + f[r + 1][c] + f[r][c - 1] + f[r][c + 1]


def avg5(f, r, c):
    return (nbr_sum(f, r, c) + f[r][c]) / 5


def stencil_at(f, r, c, w):
    return sum(w[i][j] * f[r - 1 + i][c - 1 + j] for i in range(3) for j in range(3))


assert (lap5(CLEAN, 2, 2), lap5(CLEAN, 2, 3), lap5(CLEAN, 2, 1)) == (160, -160, 0)
assert (lap5(PATCH, 2, 1), lap5(PATCH, 2, 2), lap5(PATCH, 1, 2)) == (-860, 375, 160)
assert nbr_sum(PATCH, 2, 2) == 535 and nbr_sum(PATCH, 2, 1) == 160 and nbr_sum(PATCH, 1, 2) == 320

# zero-crossings in row 2
ZC_CLEAN = 2 + 160 / (160 + 160)
ZC_EDGE = 2 + 375 / (375 + 160)
ZC_IMP = 1 + 860 / (860 + 375)
assert ZC_CLEAN == 2.5 and round(ZC_EDGE, 2) == 2.70 and round(ZC_IMP, 2) == 1.70

# the five-pixel average: change = Laplacian / 5
for f, (r, c), before, after in ((CLEAN, (2, 2), 40, 72), (CLEAN, (2, 3), 200, 168),
                                 (PATCH, (2, 1), 255, 83), (PATCH, (2, 2), 40, 115)):
    assert f[r][c] == before and avg5(f, r, c) == after
    assert avg5(f, r, c) - f[r][c] == lap5(f, r, c) / 5

# the five stencils at (2,2) of the clean patch, and on x^2 + y^2
STENCILS = {
    "five-point": [[0, 1, 0], [1, -4, 1], [0, 1, 0]],
    "diagonal": [[1, 0, 1], [0, -4, 0], [1, 0, 1]],
    "eight-neighbour": [[1, 1, 1], [1, -8, 1], [1, 1, 1]],
    "OpenCV ksize=3": [[2, 0, 2], [0, -8, 0], [2, 0, 2]],
    "nine-point ÷ 6": [[1, 4, 1], [4, -20, 4], [1, 4, 1]],
}
QUAD = [[2, 1, 2], [1, 0, 1], [2, 1, 2]]
SCALE = {}
AT22 = {}
for name, w in STENCILS.items():
    div = 6 if name.startswith("nine") else 1
    SCALE[name] = sum(w[i][j] * QUAD[i][j] for i in range(3) for j in range(3)) / div / 4
    AT22[name] = stencil_at(CLEAN, 2, 2, w) / div
assert list(SCALE.values()) == [1, 2, 3, 4, 1]
assert list(AT22.values()) == [160, 320, 480, 640, 160]

# ksize=3 on the impulse patch (the opening table)
K3 = STENCILS["OpenCV ksize=3"]
assert stencil_at(PATCH, 2, 1, K3) == -1720 and stencil_at(PATCH, 2, 2, K3) == 640
assert stencil_at(PATCH, 1, 2, K3) == 1070 and stencil_at(CLEAN, 1, 2, K3) == 640

# ------------------------------------------------------------------ the 3x3 Gaussian
SIG = 0.8
_e = math.exp(-1 / (2 * SIG * SIG))
W1 = _e / (1 + 2 * _e)            # 0.239, the side weight
W0 = 1 / (1 + 2 * _e)             # 0.522
V = 2 * W1                        # 0.478, the actual variance
G2 = [[W1 * W1, W0 * W1, W1 * W1], [W0 * W1, W0 * W0, W0 * W1], [W1 * W1, W0 * W1, W1 * W1]]
assert (round(W1, 3), round(W0, 3), round(V, 3)) == (0.239, 0.522, 0.478)
assert (round(G2[0][0], 4), round(G2[0][1], 4), round(G2[1][1], 4)) == (0.0571, 0.1248, 0.2725)
QUAD_CHANGE = sum(G2[i][j] * QUAD[i][j] for i in range(3) for j in range(3))
assert round(QUAD_CHANGE, 3) == 0.956 and abs(QUAD_CHANGE - 2 * V) < 1e-12
assert round(4 * 0.0571 * 2, 3) == 0.457 and round(4 * 0.1248, 3) == 0.499


def sampled_var(sig, n):
    ws = [math.exp(-k * k / (2 * sig * sig)) for k in range(-n, n + 1)]
    return sum(w * k * k for w, k in zip(ws, range(-n, n + 1))) / sum(ws)


assert round(sampled_var(0.8, 1), 3) == 0.478 and round(sampled_var(0.8, 2), 3) == 0.632
assert round(sampled_var(0.8, 3), 3) == 0.640 and round(sampled_var(0.8, 30), 3) == 0.640
assert round(sampled_var(0.5, 30), 3) == 0.215
assert round(0.64 / 2 * 4 - 2 * V, 3) == 0.324 and round((1.28 - 2 * V) / (2 * V) * 100, 1) == 33.9


def blur(f, r, c):
    return sum(G2[i][j] * f[r - 1 + i][c - 1 + j] for i in range(3) for j in range(3))


def cross(f, r, c):
    d = (1, -2, 1)
    return sum(d[i] * d[j] * f[r - 1 + i][c - 1 + j] for i in range(3) for j in range(3))


GRID_ROWS = []
for f, (r, c) in ((CLEAN, (2, 2)), (CLEAN, (2, 3)), (PATCH, (2, 1)), (PATCH, (1, 2))):
    b = blur(f, r, c)
    assert abs((b - f[r][c]) - (W1 * lap5(f, r, c) + W1 * W1 * cross(f, r, c))) < 1e-9
    GRID_ROWS.append((f[r][c], b, b - f[r][c], W1 * lap5(f, r, c), W1 * W1 * cross(f, r, c)))
assert [round(x[1], 1) for x in GRID_ROWS] == [78.2, 161.8, 98.6, 90.5]
assert [round(x[4], 1) for x in GRID_ROWS] == [0, 0, 49.1, 12.3]
assert round(2 * 40 - blur(CLEAN, 2, 2), 1) == 1.8 and round(400 - blur(CLEAN, 2, 3), 1) == 238.2

# smooth first, then the five-point stencil at (2,2): the combined 5x5 kernel
LOG5 = [[0.0] * 5 for _ in range(5)]
for i in range(3):
    for j in range(3):
        for (di, dj), wt in (((0, 1), 1), ((1, 0), 1), ((1, 1), -4), ((1, 2), 1), ((2, 1), 1)):
            LOG5[i + di][j + dj] += wt * G2[i][j]
assert abs(sum(map(sum, LOG5))) < 1e-12
assert round(LOG5[2][2], 3) == -0.591 and round(LOG5[1][2], 4) == -0.1123
assert round(LOG5[1][1], 3) == 0.021 and round(LOG5[0][2], 4) == 0.1248
assert round(LOG5[0][1], 4) == 0.0571 and LOG5[0][0] == 0


def log5_at(f, r, c):
    return sum(LOG5[i][j] * f[r - 2 + i][c - 2 + j] for i in range(5) for j in range(5))


assert round(log5_at(CLEAN, 2, 2), 1) == 45.3 and round(log5_at(PATCH, 2, 2), 1) == 21.1

# ------------------------------------------------------------------ transfer functions
H5 = lambda wx, wy: 2 * math.cos(wx) + 2 * math.cos(wy) - 4
H9 = lambda wx, wy: (8 * math.cos(wx) + 8 * math.cos(wy) + 4 * math.cos(wx) * math.cos(wy) - 20) / 6
D = math.pi / math.sqrt(2)
TF = {"five_axis": H5(math.pi, 0), "five_diag": H5(D, D), "nine_axis": H9(math.pi, 0),
      "nine_diag": H9(D, D), "cont": -math.pi ** 2}
assert round(TF["five_axis"], 2) == -4 and round(TF["five_diag"], 2) == -6.42
assert round(TF["nine_axis"], 2) == -4 and round(TF["nine_diag"], 2) == -4.70
assert round(TF["cont"], 2) == -9.87 and round(4 / math.pi ** 2, 3) == 0.405
SPREAD5 = (-TF["five_diag"] - 4) / 4
SPREAD9 = (-TF["nine_diag"] - 4) / 4
assert round(SPREAD5 * 100, 1) == 60.6 and round(SPREAD9 * 100, 1) == 17.6
assert round((1 - SPREAD9 / SPREAD5) * 100) == 71
assert H5(math.pi, math.pi) == -8
assert [round(1 + ds / 2 * -8, 2) for ds in (0.25, 0.4, 0.5, 0.6)] == [0, -0.6, -1, -1.4]

# ------------------------------------------------------------------ LoG and DoG


def gauss(r, s):
    return math.exp(-r * r / (2 * s * s)) / (2 * math.pi * s * s)


def log(r, s):
    return (r * r - 2 * s * s) / (2 * math.pi * s ** 6) * math.exp(-r * r / (2 * s * s))


assert abs(log(0.7, 1.3) - (-1 / (math.pi * 1.3 ** 4) * (1 - 0.49 / (2 * 1.69)) * math.exp(-0.49 / 3.38))) < 1e-15
KDOG = 1.6
DOG_CENTRE = gauss(0, KDOG) - gauss(0, 1)
LOG_CENTRE = (KDOG - 1) * log(0, 1)
assert round(DOG_CENTRE, 3) == -0.097 and round(LOG_CENTRE, 3) == -0.191
lo, hi = 1.0, 3.0
for _ in range(200):
    m = (lo + hi) / 2
    if (gauss(lo, KDOG) - gauss(lo, 1) < 0) == (gauss(m, KDOG) - gauss(m, 1) < 0):
        lo = m
    else:
        hi = m
DOG_ZERO = lo
assert round(DOG_ZERO, 2) == 1.76 and round(DOG_ZERO / math.sqrt(2) - 1, 2) == 0.24


def band(target):
    g = lambda u: u * u * math.exp(1 - u * u) - target
    out = []
    for a, b in ((1e-6, 1.0), (1.0, 5.0)):
        for _ in range(200):
            m = (a + b) / 2
            if (g(a) < 0) == (g(m) < 0):
                a = m
            else:
                b = m
        out.append((a + b) / 2)
    return out


HP = band(1 / math.sqrt(2))
assert (round(HP[0], 2), round(HP[1], 2), round(HP[1] / HP[0], 2)) == (0.62, 1.44, 2.34)
assert round(math.log2(HP[1] / HP[0]), 2) == 1.22
HA = band(0.5)
assert round(math.log2(HA[1] / HA[0]), 2) == 1.76
for sig, r0, w, lam in ((0.8, 1.13, 2.26, 3.6), (2.12, 3.0, 6.0, 9.4), (4.24, 6.0, 12.0, 18.8), (8.49, 12.0, 24.0, 37.7)):
    s = sig if sig == 0.8 else w / (2 * math.sqrt(2))
    assert round(math.sqrt(2) * s, 2) == r0 and round(2 * math.sqrt(2) * s, 2) == w
    assert round(math.sqrt(2) * math.pi * s, 1) == lam

# ------------------------------------------------------------------ scale selection
A = 160
bar = lambda s, w=3: A * w / (math.sqrt(2 * math.pi) * s) * math.exp(-w * w / (8 * s * s))
disc = lambda s, r=3: A * r * r / (s * s) * math.exp(-r * r / (2 * s * s))
assert [round(bar(s), 1) for s in (1.0, 1.5, 2.1213, 3.0, 4.0)] == [62.2, 77.4, 70.3, 56.3, 44.6]
assert [round(disc(s), 1) for s in (1.0, 1.5, 3 / math.sqrt(2), 3.0, 4.0)] == [16.0, 86.6, 117.7, 97.0, 67.9]
assert round(5 / math.sqrt(2), 2) == 3.54


def disc_off(x0, y0, s, r=3, n=4096):
    """|sigma^2 A (integral of LoG over the disc)| at (x0, y0), by the divergence theorem."""
    tot = 0.0
    for i in range(n):
        th = 2 * math.pi * i / n
        dx, dy = r * math.cos(th) - x0, r * math.sin(th) - y0
        g = math.exp(-(dx * dx + dy * dy) / (2 * s * s)) / (2 * math.pi * s * s)
        tot += -(dx * math.cos(th) + dy * math.sin(th)) / (s * s) * g * r * (2 * math.pi / n)
    return -A * s * s * tot


LADDER = [2 ** (i / 3) for i in range(7)]
CUBE_SIGMAS = (LADDER[2], LADDER[3], LADDER[4])
CUBE = [[[disc_off(dx, dy, s) for dx in (-1, 0, 1)] for dy in (-1, 0, 1)] for s in CUBE_SIGMAS]
assert abs(CUBE[1][1][1] - disc(2.0)) < 1e-9
assert [round(CUBE[k][1][1], 1) for k in range(3)] == [95.8, 116.9, 111.6]
assert [round(CUBE[1][0][1], 1), round(CUBE[1][0][0], 1)] == [104.3, 92.4]
others = [CUBE[k][i][j] for k in range(3) for i in range(3) for j in range(3) if (k, i, j) != (1, 1, 1)]
assert len(others) == 26 and max(others) < CUBE[1][1][1] and round(max(others), 1) == 111.6
Rm, R0, Rp = (round(CUBE[k][1][1], 1) for k in range(3))
DELTA = 0.5 * (Rm - Rp) / (Rm - 2 * R0 + Rp)
SIGMA_STAR = 2 ** ((3 + DELTA) / 3)
assert round(DELTA, 2) == 0.30 and round(SIGMA_STAR, 2) == 2.14
assert round(SIGMA_STAR / (3 / math.sqrt(2)) - 1, 2) == 0.01


def vertex(xs, ys):
    (x0, x1, x2), (y0, y1, y2) = xs, ys
    den = (x0 - x1) * (x0 - x2) * (x1 - x2)
    a = (x2 * (y1 - y0) + x1 * (y0 - y2) + x0 * (y2 - y1)) / den
    b = (x2 ** 2 * (y0 - y1) + x1 ** 2 * (y2 - y0) + x0 ** 2 * (y1 - y2)) / den
    return -b / (2 * a)


ys = [CUBE[k][1][1] for k in range(3)]
assert round(vertex(CUBE_SIGMAS, ys), 2) == 2.18
assert round(math.sqrt(vertex([s * s for s in CUBE_SIGMAS], ys)), 2) == 2.22
assert [round(s, 2) for s in LADDER[:4]] == [1.0, 1.26, 1.59, 2.0]
assert (10 + 1) ** 2 / 10 == 12.1 and (1 + 1) ** 2 / 1 == 4

# ------------------------------------------------------------------ the pyramid
BIN = [Fr(1, 16), Fr(4, 16), Fr(6, 16), Fr(4, 16), Fr(1, 16)]


def refl101(x, i):
    n = len(x)
    while i < 0 or i >= n:
        i = -i if i < 0 else 2 * (n - 1) - i
    return x[i]


def blur1(x):
    return [sum(BIN[k] * refl101(x, i + k - 2) for k in range(5)) for i in range(len(x))]


def reduce1(x):
    return blur1(x)[0::2]


def expand1(g, n):
    z = [Fr(0)] * n
    for i, v in enumerate(g):
        z[2 * i] = v
    return [2 * sum(BIN[k] * refl101(z, i + k - 2) for k in range(5)) for i in range(n)]


G0 = [Fr(v) for v in (40, 40, 40, 200, 200)]
BLUR0 = blur1(G0)
G1 = reduce1(G0)
E1 = expand1(G1, 5)
L0 = [a - b for a, b in zip(G0, E1)]
G2P = reduce1(G1)
E2 = expand1(G2P, 3)
L1 = [a - b for a, b in zip(G1, E2)]
assert BLUR0 == [40, 50, 90, 150, 180] and G1 == [40, 90, 180]
assert E1 == [Fr(105, 2), 65, 95, 135, Fr(315, 2)] and L0 == [Fr(-25, 2), -25, -55, 65, Fr(85, 2)]
assert G2P == [Fr(165, 2), Fr(235, 2)] and E2 == [Fr(365, 4), 100, Fr(435, 4)]
assert L1 == [Fr(-205, 4), -10, Fr(285, 4)]
assert [a + b for a, b in zip(L0, E1)] == G0 and [a + b for a, b in zip(L1, E2)] == G1
assert round(float(2 + Fr(55, 120)), 2) == 2.46
assert sum(BIN[k] * (k - 2) ** 2 for k in range(5)) == 1
for a, c, var in ((Fr(1, 2), 0, Fr(1, 2)), (Fr(2, 5), Fr(1, 20), Fr(9, 10)), (Fr(3, 8), Fr(1, 16), 1), (Fr(3, 10), Fr(1, 10), Fr(13, 10))):
    assert Fr(1, 4) - a / 2 == c and 2 * (Fr(1, 4) + 4 * c) == var
assert sum((256 >> l) ** 2 for l in range(5)) == 87296 and round(87296 / 65536, 3) == 1.332
assert 257 * 257 == 66049 and round(66049 * 7.57) == 499991 and 66049 * 8 == 528392

if __name__ == "__main__":
    print("all article numbers check out")
    print("cube:", [[[round(v, 1) for v in row] for row in sl] for sl in CUBE])
