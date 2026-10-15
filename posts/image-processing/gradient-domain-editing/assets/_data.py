#!/usr/bin/env python3
"""Every number in gradient-domain-editing, computed in plain Python and asserted against the article.

Nothing loads an image and no imaging library runs. The system, the sweeps, the V-cycle and the fills
are exact rational arithmetic (`fractions`); the sine transform, the attenuation factors and the
OpenCV replay are floating point (`math`). The OpenCV replay follows seamless_cloning.cpp and
seamless_cloning_impl.cpp at commit 802cf95 line by line (ledger L40-L48); it is a model of that code,
not a run of it.

Importing this module is quick, so the figure scripts can use it. Running it (`python3 _data.py`)
prints the headline numbers after every assert has held.
"""
import math
import sys
from fractions import Fraction as F


def close(a, b, tol):
    return abs(a - b) <= tol


# ------------------------------------------------------------------ the patch, its region and ring
PATCH = [[40, 40, 40, 200, 200],
         [40, 40, 40, 200, 200],
         [40, 255, 40, 200, 200],
         [40, 40, 40, 200, 200],
         [40, 40, 40, 200, 200]]
OMEGA = [(r, c) for r in (1, 2, 3) for c in (1, 2, 3)]       # row-major: (r1,c1) ... (r3,c3)
IDX = {p: i for i, p in enumerate(OMEGA)}


def nbrs(r, c):
    return [(r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)]


def lap5(g, r, c):
    """Five-point Laplacian, Part 2's sign: positive on the dark side of a step (L54)."""
    return sum(g[a][b] for a, b in nbrs(r, c)) - 4 * g[r][c]


RING = sorted({q for p in OMEGA for q in nbrs(*p) if q not in IDX})
assert len(RING) == 12
LAP = [lap5(PATCH, r, c) for r, c in OMEGA]
assert LAP == [215, 160, -160, -860, 375, -160, 215, 160, -160]          # Part 2's values (L54)
assert sum(LAP) == -215                                                   # net flux: the impulse's left edge


def assemble(frame, guide):
    """Pérez eq. (7) on OMEGA (L03): A, b. frame gives the ring values; guide the kept differences
    (None = membrane, v = 0). Returns A (ints), b (Fractions), boundary sums."""
    A = [[0] * 9 for _ in range(9)]
    b = [F(0)] * 9
    bnd = [F(0)] * 9
    for (r, c), i in IDX.items():
        A[i][i] = 4
        for q in nbrs(r, c):
            if q in IDX:
                A[i][IDX[q]] = -1
            else:
                bnd[i] += F(frame[q[0]][q[1]])
        b[i] = bnd[i]
        if guide is not None:                                 # sum over edges of (g_p - g_q) = -Laplacian
            b[i] += 4 * F(guide[r][c]) - sum(F(guide[a][bb]) for a, bb in nbrs(r, c))
    return A, b, bnd


def solve_exact(A, b):
    n = len(b)
    M = [[F(A[i][j]) for j in range(n)] + [F(b[i])] for i in range(n)]
    for col in range(n):
        piv = next(r for r in range(col, n) if M[r][col] != 0)
        M[col], M[piv] = M[piv], M[col]
        for r in range(n):
            if r != col and M[r][col] != 0:
                f = M[r][col] / M[col][col]
                M[r] = [M[r][k] - f * M[col][k] for k in range(n + 1)]
    return [M[i][n] / M[i][i] for i in range(n)]


A, B, BND = assemble(PATCH, PATCH)
XSTAR = [PATCH[r][c] for r, c in OMEGA]
assert BND == [80, 40, 400, 40, 0, 200, 80, 40, 400]
assert B == [-135, -120, 560, 900, -375, 360, -135, -120, 560]
assert all(sum(A[i][j] * XSTAR[j] for j in range(9)) == B[i] for i in range(9))
assert all(A[i][j] == A[j][i] for i in range(9) for j in range(9))           # symmetric
assert solve_exact(A, B) == XSTAR                                              # the pixels come back

# ------------------------------------------------------------------ Gauss-Seidel from zero (L27)


def gs_sweep(x, b=None):
    b = B if b is None else b
    x = list(x)
    for i in range(9):
        x[i] = (b[i] + sum(-A[i][j] * x[j] for j in range(9) if j != i)) / 4
    return x


def err(x):
    return [float(x[i] - XSTAR[i]) for i in range(9)]


def maxabs(e):
    return max(abs(v) for v in e)


def rms(e):
    return math.sqrt(sum(v * v for v in e) / len(e))


SWEEPS = [[F(0)] * 9]
for _ in range(12):
    SWEEPS.append(gs_sweep(SWEEPS[-1]))
SWEEP_ERR = [maxabs(err(x)) for x in SWEEPS]
assert SWEEP_ERR[0] == 255
assert [round(v, 1) for v in SWEEP_ERR[1:9]] == [89.7, 62.1, 31.1, 15.5, 7.8, 3.9, 1.9, 1.0]
assert close(SWEEP_ERR[8], 0.97, 0.005) and SWEEP_ERR[9] < 0.5 < SWEEP_ERR[8]   # nine sweeps for 8-bit
assert [round(float(v), 2) for v in SWEEPS[1]] == [-33.75, -38.44, 130.39, 216.56, -49.22, 110.29,
                                                    20.39, -37.21, 158.27]
assert [round(float(v), 2) for v in SWEEPS[2]] == [10.78, -7.01, 165.82, 220.49, -22.11, 165.5,
                                                    12.07, 7.06, 183.14]
assert [round(float(v), 2) for v in SWEEPS[3]] == [19.62, 10.83, 184.08, 227.4, 8.95, 184.04,
                                                    24.86, 24.24, 192.07]
E1 = err(SWEEPS[1])
assert all(v < 0 for v in E1) and round(min(E1), 1) == -89.7 and round(max(E1), 1) == -19.6
assert round(E1[0], 1) == -73.8 and round(E1[4], 1) == -89.2                  # (r1,c1), centre
assert round(rms(E1), 1) == 68.3 and round(rms(err(SWEEPS[3])), 1) == 21.2
def smooth_share(e):
    """Share of the error's energy in the smoothest sine pattern (k = l = 1)."""
    sn = lambda k, m: math.sin(k * m * math.pi / 4)
    co = {(k, l): sum(e[3 * r + c] * sn(k, r + 1) * sn(l, c + 1) for r in range(3) for c in range(3)) / 2
          for k in (1, 2, 3) for l in (1, 2, 3)}
    return co[(1, 1)] ** 2 / sum(v * v for v in co.values())


SHARES = [smooth_share(err(x)) for x in SWEEPS[:4]]
assert [round(v, 2) for v in SHARES[:3]] == [0.56, 0.92, 0.97]
E2 = err(SWEEPS[2])
assert round(E2[4], 1) == -62.1 and round(max(E2), 1) == -16.9 and round(min(E2[i] for i in (0, 2, 6, 8)), 1) == -34.2
assert [round(E2[i], 1) for i in (1, 3, 5, 7)] == [-47.0, -34.5, -34.5, -32.9]
for k in range(3, 11):                                                        # halves from the third on
    assert close(SWEEP_ERR[k + 1] / SWEEP_ERR[k], 0.5, 1e-9)

# ------------------------------------------------------------------ one V(1,1) cycle (L29, L30)
PW = [F(1, 4), F(1, 2), F(1, 4), F(1, 2), F(1), F(1, 2), F(1, 4), F(1, 2), F(1, 4)]   # bilinear, centre
RW = [w / 4 for w in PW]                                                              # full weighting
assert RW == [F(1, 16), F(1, 8), F(1, 16), F(1, 8), F(1, 4), F(1, 8), F(1, 16), F(1, 8), F(1, 16)]
AP = [sum(A[i][j] * PW[j] for j in range(9)) for i in range(9)]
AC = sum(RW[i] * AP[i] for i in range(9))
assert AP == [0, F(1, 2), 0, F(1, 2), 2, F(1, 2), 0, F(1, 2), 0] and AC == F(3, 4)    # Galerkin RAP
AC_REDISC = F(1)                                                                       # 4/H^2 with H = 2


def residual(x, b=None):
    b = B if b is None else b
    return [b[i] - sum(A[i][j] * x[j] for j in range(9)) for i in range(9)]


def vcycle(x, ac=AC, b=None):
    x = gs_sweep(x, b)
    r = residual(x, b)
    rc = sum(RW[i] * r[i] for i in range(9))
    ec = rc / ac
    x = [x[i] + PW[i] * ec for i in range(9)]
    mid = list(x)
    return gs_sweep(x, b), r, rc, ec, mid


V1, V_RES, V_RC, V_EC, V_MID = vcycle([F(0)] * 9)
assert [round(float(v), 2) for v in V_RES] == [178.12, 81.17, 110.29, -28.83, 73.09, 158.27, -37.21,
                                               158.27, 0.0]
assert round(float(V_RC), 2) == 80.08 and round(float(V_EC), 2) == 106.78
assert [round(float(PW[i] * V_EC), 2) for i in (0, 1, 4)] == [26.69, 53.39, 106.78]
assert round(maxabs(err(V_MID)), 1) == 47.1
assert [round(float(v), 2) for v in V1] == [37.48, 33.03, 189.18, 260.53, 24.61, 189.69, 35.43, 31.25,
                                            195.23]
V1_ERR = maxabs(err(V1))
assert round(V1_ERR, 1) == 15.4 and round(rms(err(V1)), 1) == 8.6
V2 = vcycle(V1)[0]
assert round(maxabs(err(V2)), 2) == 0.82
VR1 = vcycle([F(0)] * 9, AC_REDISC)[0]
assert round(maxabs(err(VR1)), 1) == 27.1 and round(maxabs(err(vcycle(VR1, AC_REDISC)[0])), 1) == 2.9

# ------------------------------------------------------------------ the sine transform (L25, L43)
LAMS = {(k, l): 4 - 2 * math.cos(k * math.pi / 4) - 2 * math.cos(l * math.pi / 4)
        for k in (1, 2, 3) for l in (1, 2, 3)}
assert sorted(round(v, 3) for v in LAMS.values()) == [1.172, 2.586, 2.586, 4.0, 4.0, 4.0, 5.414, 5.414,
                                                     6.828]


def s(k, m):
    return math.sin(k * m * math.pi / 4)


BHAT = {(k, l): sum(float(B[3 * r + c]) * s(k, r + 1) * s(l, c + 1) for r in range(3) for c in range(3))
        for k in (1, 2, 3) for l in (1, 2, 3)}
assert all(abs(BHAT[(2, l)]) < 1e-9 for l in (1, 2, 3))                       # rows r1 and r3 equal
DST_X = [sum(BHAT[(k, l)] / LAMS[(k, l)] * s(k, r + 1) * s(l, c + 1) for k in (1, 2, 3) for l in (1, 2, 3)) / 4
         for r in range(3) for c in range(3)]
assert all(close(DST_X[i], XSTAR[i], 1e-9) for i in range(9))
JACOBI_SLOW = 1 - LAMS[(1, 1)] / 4
assert close(JACOBI_SLOW, math.cos(math.pi / 4), 1e-12) and close(JACOBI_SLOW ** 2, 0.5, 1e-12)

# ------------------------------------------------------------------ scale: sweeps per digit (L27, L28)


def gs_rho(N):
    return math.cos(math.pi / (N + 1)) ** 2


def sweeps_per_digit(rho):
    return math.log(10) / -math.log(rho)


def sor_rho(N):
    return 2 / (1 + math.sin(math.pi / (N + 1))) - 1          # omega_opt - 1


SPD = {N: sweeps_per_digit(gs_rho(N)) for N in (3, 31, 255, 1023)}
assert [round(SPD[3], 1), round(SPD[31], 1), round(SPD[255]), round(SPD[1023])] == [3.3, 238.5, 15289, 244633]
assert close(SPD[1023] / (1024 ** 2), math.log(10) / math.pi ** 2, 1e-5)      # 0.2333 (N+1)^2
assert round(math.log(10) / math.pi ** 2, 3) == 0.233
assert round(gs_rho(1023), 7) == 0.9999906
OMEGA_OPT = {N: 2 / (1 + math.sin(math.pi / (N + 1))) for N in (3, 1023)}
assert round(OMEGA_OPT[3], 3) == 1.172 and round(OMEGA_OPT[1023], 5) == 1.99388
assert round(sweeps_per_digit(sor_rho(3)), 1) == 1.3 and round(sweeps_per_digit(sor_rho(1023))) == 375
assert close(2 / (1 + math.sqrt(1 - math.cos(math.pi / 4) ** 2)), OMEGA_OPT[3], 1e-12)   # Saad (4.47)
assert round(math.log(10) / (2 * math.pi), 2) == 0.37 and close(sweeps_per_digit(sor_rho(1023)) / 1024, math.log(10) / (2 * math.pi), 1e-3)

# ------------------------------------------------------------------ four fills of the hole (L01, L02)
SHADOW = [[F(v, 5) for v in row] for row in PATCH]                           # Part 11's copy (L55)
assert sorted({v for row in SHADOW for v in row}) == [8, 40, 51]
FILL_MEMBRANE = solve_exact(*assemble(PATCH, None)[:2])
FILL_GUIDED = solve_exact(*assemble(PATCH, PATCH)[:2])
FILL_SHADOW = solve_exact(*assemble(SHADOW, PATCH)[:2])
MISMATCH = [[SHADOW[r][c] - PATCH[r][c] for c in range(5)] for r in range(5)]
FILL_CORR = solve_exact(*assemble(MISMATCH, None)[:2])
DARK60 = [[v - 60 for v in row] for row in PATCH]
FILL_DARK60 = solve_exact(*assemble(DARK60, PATCH)[:2])
assert [round(float(v), 2) for v in FILL_MEMBRANE] == [58.57, 90.0, 161.43, 64.29, 100.0, 155.71, 58.57, 90.0,
                                                       161.43]
assert FILL_GUIDED == XSTAR
assert [round(float(v), 2) for v in FILL_SHADOW] == [-6.86, -32.0, 70.86, 203.57, -40.0, 75.43, -6.86, -32.0,
                                                     70.86]
assert [round(float(v), 2) for v in FILL_CORR] == [-46.86, -72.0, -129.14, -51.43, -80.0, -124.57, -46.86,
                                                   -72.0, -129.14]
assert all(FILL_SHADOW[i] == XSTAR[i] + FILL_CORR[i] for i in range(9))       # f = g + h (L02)
assert FILL_DARK60 == [v - 60 for v in XSTAR]
assert round(float(FILL_SHADOW[2] - FILL_SHADOW[1]), 2) == 102.86            # step at r1
assert round(float(FILL_SHADOW[3] - FILL_SHADOW[4]), 2) == 243.57            # spike above (r2,c2)
CLAMP_TRUNC = [int(min(255.0, max(0.0, float(v)))) for v in FILL_SHADOW]      # OpenCV's store (L44)
assert CLAMP_TRUNC == [0, 0, 70, 203, 0, 75, 0, 0, 70]
LOG_P = [[math.log(v) for v in row] for row in PATCH]
LOG_S = [[math.log(float(v)) for v in row] for row in SHADOW]


def solve_float(frame, guide):
    A_, b_, _ = assemble([[F(v).limit_denominator(10 ** 15) for v in row] for row in frame],
                         [[F(v).limit_denominator(10 ** 15) for v in row] for row in guide])
    return [float(v) for v in solve_exact(A_, b_)]


FILL_LOG = [math.exp(v) for v in solve_float(LOG_S, LOG_P)]
assert all(close(FILL_LOG[i], float(SHADOW[r][c]), 1e-9) for i, (r, c) in enumerate(OMEGA))
assert close(-math.log(5), LOG_S[0][0] - LOG_P[0][0], 1e-12)

# ------------------------------------------------------------------ HDR: Fattal's factor (L14, L37)
LN5 = math.log(5)


def central_mag(H, r, c):
    n, m = len(H), len(H[0])
    h = lambda a, b: H[min(max(a, 0), n - 1)][min(max(b, 0), m - 1)]     # zero derivative outside
    return math.hypot((h(r, c + 1) - h(r, c - 1)) / 2, (h(r + 1, c) - h(r - 1, c)) / 2)


STEP_ROW = [40, 40, 40, 200, 200]
H1 = [[math.log(v) for v in STEP_ROW]]
CD1 = [central_mag(H1, 0, c) for c in range(5)]
ALPHA1 = 0.1 * sum(CD1) / 5
assert [round(v, 4) for v in CD1] == [0.0, 0.0, 0.8047, 0.8047, 0.0]
assert round(sum(CD1) / 5, 4) == 0.3219 and round(ALPHA1, 4) == 0.0322 and close(CD1[2] / ALPHA1, 25, 1e-9)


def phi(mag, alpha, beta):
    return (mag / alpha) ** (beta - 1)


HDR1 = {}
for beta in (0.8, 0.85, 0.9):
    p = phi(CD1[2], ALPHA1, beta)
    HDR1[beta] = (p, LN5 * p, math.exp(LN5 * p))
assert [round(HDR1[b][0], 3) for b in (0.8, 0.85, 0.9)] == [0.525, 0.617, 0.725]
assert [round(HDR1[b][1], 3) for b in (0.8, 0.85, 0.9)] == [0.845, 0.993, 1.166]
assert [round(HDR1[b][2], 2) for b in (0.8, 0.85, 0.9)] == [2.33, 2.70, 3.21]
assert round(LN5, 3) == 1.609

H2 = [[math.log(v) for v in row] for row in PATCH]
MAG2 = [[central_mag(H2, r, c) for c in range(5)] for r in range(5)]
ALPHA2 = 0.1 * sum(map(sum, MAG2)) / 25
assert round(sum(map(sum, MAG2)) / 25, 4) == 0.4057 and round(ALPHA2, 4) == 0.0406
assert round(MAG2[2][2], 4) == 0.1215 and MAG2[2][1] == 0 and round(MAG2[1][1], 4) == 0.9262
PHI_R1C2, PHI_R2C2 = phi(MAG2[1][2], ALPHA2, 0.85), phi(MAG2[2][2], ALPHA2, 0.85)
GX_R1, GX_R2 = PHI_R1C2 * (H2[1][3] - H2[1][2]), PHI_R2C2 * (H2[2][3] - H2[2][2])
CIRC = GX_R1 + 0.0 - GX_R2 - 0.0                       # right along r1, down c3, left along r2, up c2
assert round(PHI_R1C2, 3) == 0.639 and round(PHI_R2C2, 3) == 0.848 and round(PHI_R2C2 / PHI_R1C2, 3) == 1.328
assert round(GX_R1, 3) == 1.028 and round(GX_R2, 3) == 1.365
assert round(math.exp(GX_R1), 2) == 2.80 and round(math.exp(GX_R2), 2) == 3.92
assert round(CIRC, 3) == -0.337
assert H2[2][2] - H2[1][2] == 0 and H2[2][3] - H2[1][3] == 0                  # zero up c2 and c3
PHI_SPIKE = phi(1e-4, ALPHA2, 0.85)                                           # Luminance HDR's floor
OUT_SPIKE = math.log(40 / 255)
assert round(PHI_SPIKE, 2) == 2.46 and round(OUT_SPIKE, 3) == -1.852 and round(PHI_SPIKE * OUT_SPIKE, 2) == -4.56

# ------------------------------------------------------------------ seamless tiling (L09)
END = F(STEP_ROW[0] + STEP_ROW[-1], 2)
M0, M4 = END - STEP_ROW[0], END - STEP_ROW[-1]
TILE_ROW = [STEP_ROW[i] + M0 + (M4 - M0) * F(i, 4) for i in range(5)]       # 1-D membrane is a line
assert END == 120 and (M0, M4) == (80, -80) and TILE_ROW == [120, 80, 40, 160, 120]
assert TILE_ROW[3] - TILE_ROW[2] == 120 and TILE_ROW[-1] == TILE_ROW[0]
TILE_FRAME = [list(row) for row in PATCH]
for r in range(5):
    TILE_FRAME[r][0] = TILE_FRAME[r][4] = F(PATCH[r][0] + PATCH[r][4], 2)
for c in range(5):
    TILE_FRAME[0][c] = TILE_FRAME[4][c] = F(PATCH[0][c] + PATCH[4][c], 2)
TILE_2D = solve_exact(*assemble(TILE_FRAME, PATCH)[:2])
assert [round(float(v), 2) for v in TILE_2D] == [68.57, 40.0, 171.43, 289.29, 40.0, 165.71, 68.57, 40.0, 171.43]

# ------------------------------------------------------------------ OpenCV seamlessClone, replayed (L40-L48)


def dst1(v):
    """Unnormalised DST-I of a list: y_k = sum_n v_n sin(pi (k+1)(n+1)/(N+1))."""
    N = len(v)
    return [sum(v[n] * math.sin(math.pi * (k + 1) * (n + 1) / (N + 1)) for n in range(N)) for k in range(N)]


def poisson_rect(dest, lap):
    """Dirichlet frame = dest's frame; interior solves 5-point Laplacian(f) = lap (as Cloning::solve)."""
    h, w = len(dest), len(dest[0])
    bound = [[dest[r][c] if r in (0, h - 1) or c in (0, w - 1) else 0.0 for c in range(w)] for r in range(h)]
    mod = [[lap[r][c] - (bound[r - 1][c] + bound[r + 1][c] + bound[r][c - 1] + bound[r][c + 1] - 4 * bound[r][c])
            for c in range(1, w - 1)] for r in range(1, h - 1)]
    H_, W_ = h - 2, w - 2
    rows = [dst1(row) for row in mod]
    co = [dst1([rows[r][c] for r in range(H_)]) for c in range(W_)]          # co[c][r]
    fx = [2 * math.cos(math.pi * (i + 1) / (w - 1)) for i in range(W_)]
    fy = [2 * math.cos(math.pi * (j + 1) / (h - 1)) for j in range(H_)]
    co = [[co[c][r] / (fx[c] + fy[r] - 4) for r in range(H_)] for c in range(W_)]
    back = [dst1(co[c]) for c in range(W_)]
    inner = [dst1([back[c][r] for c in range(W_)]) for r in range(H_)]
    scale = (2 / (H_ + 1)) * (2 / (W_ + 1))                                   # DST-I is its own inverse up to this
    out = [list(map(float, row)) for row in dest]
    for r in range(H_):
        for c in range(W_):
            out[r + 1][c + 1] = inner[r][c] * scale
    return out


def erode_square(m, k):
    """Erosion by a k x k square, zeros outside (the parent mask outside the bounding box, L42)."""
    h, w, rad = len(m), len(m[0]), k // 2
    return [[min((m[r + dr][c + dc] if 0 <= r + dr < h and 0 <= c + dc < w else 0)
                 for dr in range(-rad, rad + 1) for dc in range(-rad, rad + 1)) for c in range(w)] for r in range(h)]


def cv_seamless_clone(src, dst, mask, p, mixed=False):
    """1-channel replay of cv::seamlessClone at 802cf95 (NORMAL_CLONE / MIXED_CLONE, no _WIDE).
    Returns (blend, the caller's mask as the call leaves it)."""
    mask = [list(row) for row in mask]                     # the caller's array (shared at 802cf95, L48)
    H, W = len(mask), len(mask[0])
    for r in range(H):
        for c in range(W):
            if r in (0, H - 1) or c in (0, W - 1):
                mask[r][c] = 0                             # copyMakeBorder of the inner part (L40)
    pts = [(r, c) for r in range(H) for c in range(W) if mask[r][c]]
    blend = [list(map(float, row)) for row in dst]
    if not pts:
        return blend, mask
    r0, r1 = min(r for r, _ in pts), max(r for r, _ in pts)
    c0, c1 = min(c for _, c in pts), max(c for _, c in pts)
    h, w = r1 - r0 + 1, c1 - c0 + 1
    td, ld = p[1] - h // 2, p[0] - w // 2                  # p = (x, y), the bounding box's centre
    dROI = [[float(dst[td + r][ld + c]) for c in range(w)] for r in range(h)]
    sROI = [[float(src[r0 + r][c0 + c]) if mask[r0 + r][c0 + c] else 0.0 for c in range(w)] for r in range(h)]
    mROI = [[mask[r0 + r][c0 + c] for c in range(w)] for r in range(h)]
    ext = [[mask[r][c] for c in range(W)] for r in range(H)]
    ero = erode_square(ext, 7)                             # 3 iterations of 3x3 = one 7x7 (L42)
    mE = [[ero[r0 + r][c0 + c] / 255 for c in range(w)] for r in range(h)]

    def gx(a, r, c):                                       # forward differences (L41); reflect-101 at the end
        return (a[r][c + 1] if c + 1 < w else a[r][c - 1]) - a[r][c]

    def gy(a, r, c):
        return (a[r + 1][c] if r + 1 < h else a[r - 1][c]) - a[r][c]
    vx = [[0.0] * w for _ in range(h)]
    vy = [[0.0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            sx, sy, dx, dy = gx(sROI, r, c), gy(sROI, r, c), gx(dROI, r, c), gy(dROI, r, c)
            if mixed and not abs(sx - sy) > abs(dx - dy):  # L45: abs(gx - gy), both from the winner
                sx, sy = dx, dy
            vx[r][c] = sx * mE[r][c] + dx * (1 - mE[r][c])
            vy[r][c] = sy * mE[r][c] + dy * (1 - mE[r][c])
    lap = [[(vx[r][c] - (vx[r][c - 1] if c else 0.0)) + (vy[r][c] - (vy[r - 1][c] if r else 0.0))
            for c in range(w)] for r in range(h)]
    sol = poisson_rect(dROI, lap)
    for r in range(h):
        for c in range(w):
            v = sol[r][c]
            if 0 < r < h - 1 and 0 < c < w - 1:
                v = 0 if v < 0 else 255 if v > 255 else int(v)   # clamp, then truncate (L44)
            blend[td + r][ld + c] = v
    for r in range(h):                                     # erosion, then bitwise_not, in place (L48)
        for c in range(w):
            mask[r0 + r][c0 + c] = 0 if ero[r0 + r][c0 + c] else 255
    return blend, mask


# The 5x5 patch with a full mask clones nothing: frame cleared, 3x3 eroded away.
FULL = [[255] * 5 for _ in range(5)]
FLAT40 = [[40] * 5 for _ in range(5)]
OUT_5, MASK_AFTER_5 = cv_seamless_clone(PATCH, FLAT40, FULL, (2, 2))
assert all(close(OUT_5[r][c], 40, 1e-9) for r in range(5) for c in range(5))
assert MASK_AFTER_5 == [[0] * 5] + [[0, 255, 255, 255, 0]] * 3 + [[0] * 5]   # caller's mask after the call

# The dimmed spike: the patch's left three columns, padded with their edge value 40 to 15 x 15.
STAR_N = 15
STAR = [[40] * STAR_N for _ in range(STAR_N)]
STAR[7][7] = 255
SKY = [[40] * STAR_N for _ in range(STAR_N)]
FULLN = [[255] * STAR_N for _ in range(STAR_N)]
NORM_OUT, _ = cv_seamless_clone(STAR, SKY, FULLN, (7, 7))
MIX_OUT, _ = cv_seamless_clone(STAR, SKY, FULLN, (7, 7), mixed=True)
assert NORM_OUT[7][7] in (254, 255) and all(NORM_OUT[r][c] in (39, 40) for r in range(STAR_N)
                                            for c in range(STAR_N) if (r, c) != (7, 7))
STAR_PEAK = MIX_OUT[7][7]
STAR_LEFT, STAR_UP, STAR_RIGHT, STAR_DOWN = MIX_OUT[7][6], MIX_OUT[6][7], MIX_OUT[7][8], MIX_OUT[8][7]


if __name__ == "__main__":
    print("all asserts hold")
    print("sweep max errors:", [round(v, 2) for v in SWEEP_ERR[:10]])
    print("V-cycle: rc %.2f ec %.2f; error after one cycle %.2f, two %.2f" % (V_RC, V_EC, V1_ERR, maxabs(err(V2))))
    print("shadow clone:", [round(float(v), 2) for v in FILL_SHADOW])
    print("HDR step row:", {b: tuple(round(x, 3) for x in HDR1[b]) for b in HDR1})
    print("2-D loop: r1 %.3f r2 %.3f circ %.3f" % (GX_R1, GX_R2, CIRC))
    print("MIXED spike: peak", STAR_PEAK, "left", STAR_LEFT, "up", STAR_UP, "right", STAR_RIGHT, "down", STAR_DOWN)
    print("MIXED neighbourhood:")
    for r in range(4, 11):
        print("   ", [MIX_OUT[r][c] for c in range(4, 11)])
    sys.exit(0)
