#!/usr/bin/env python3
"""The numbers behind mathematical-morphology, computed from definitions and asserted against the article.

Nothing loads an image and nothing imports a library: the series' 5x5 patch is typed in, and every
library result is a plain-Python replay of the rule read at a pinned commit or tag:

- Binary and flat grey erosion and dilation as Minkowski operations, with two border rules: the
  outside never wins (OpenCV's default border values, MATLAB's +/-inf, scikit-image's 'ignore'),
  and the outside is 0 (SciPy's binary default, border_value=0, ni_morphology.c).
- OpenCV's erode and dilate (morph.dispatch.cpp / morph.simd.hpp at 802cf95, unchanged since 4.10.0):
  offsets measured from the anchor (default ksize // 2), the SAME offsets for the minimum and the
  maximum, so dilate is not reflected; morphologyEx = erode n times then dilate n times.
- Reconstruction by iterated geodesic dilation (Vincent 1993), h-maxima, regional maxima.
- Sobel 3x3 with replicate border (Part 8's table), for comparison with the morphological gradient.
"""
import itertools
import random

# ------------------------------------------------------------------ the patch, the mask, the grid
P = [[40, 40, 40, 200, 200],
     [40, 40, 40, 200, 200],
     [40, 255, 40, 200, 200],
     [40, 40, 40, 200, 200],
     [40, 40, 40, 200, 200]]
N = 5
GRID = frozenset((r, c) for r in range(N) for c in range(N))
X = frozenset(p for p in GRID if P[p[0]][p[1]] > 40)          # Otsu's raw cut (Part 11): pixels above 40
BAR = frozenset((r, c) for r in range(N) for c in (3, 4))
SPECK = frozenset({(2, 1)})
assert X == BAR | SPECK and len(X) == 11

CROSS = ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1))
SQUARE = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1))


def msum(A, B):
    return tuple(sorted({(a1 + a2, b1 + b2) for a1, b1 in A for a2, b2 in B}))


def nB(n, B=CROSS):
    S = ((0, 0),)
    for _ in range(n):
        S = msum(S, B)
    return S


def disk(r):
    return tuple(sorted((a, b) for a in range(-r, r + 1) for b in range(-r, r + 1) if a * a + b * b <= r * r))


# ------------------------------------------------------------------ binary operators on a bounded grid
def dil(A, B, grid=GRID):
    """Minkowski sum cut to the grid: the outside never contributes."""
    return frozenset((r + a, c + b) for r, c in A for a, b in B if (r + a, c + b) in grid)


def ero(Y, B, border="ignore", grid=GRID):
    """{x : B_x ∩ grid ⊆ Y} when the outside is ignored; {x : B_x ⊆ Y} when the outside is 0."""
    out = set()
    for r, c in grid:
        ok = True
        for a, b in B:
            p = (r + a, c + b)
            if p in grid:
                if p not in Y:
                    ok = False
                    break
            elif border == "zero":
                ok = False
                break
        if ok:
            out.add((r, c))
    return frozenset(out)


def opening(Y, B, border="ignore", grid=GRID):
    return dil(ero(Y, B, border, grid), B, grid)


def closing(Y, B, border="ignore", grid=GRID):
    return ero(dil(Y, B, grid), B, border, grid)


E1, D1 = ero(X, CROSS), dil(X, CROSS)
O1, C1 = opening(X, CROSS), closing(X, CROSS)
assert E1 == frozenset((r, 4) for r in range(N)) and len(E1) == 5
assert len(D1) == 19 and D1 == frozenset((r, c) for r in range(N) for c in (2, 3, 4)) | {(1, 1), (2, 0), (2, 1), (3, 1)}
assert O1 == BAR and len(O1) == 10
assert C1 == BAR | {(1, 2), (2, 2), (3, 2), (2, 1)} and len(C1) == 14
# Step 5: each twice; the two identities that make it so
assert opening(O1, CROSS) == O1 and closing(C1, CROSS) == C1
assert ero(O1, CROSS) == E1 and dil(C1, CROSS) == D1
assert O1 <= X <= C1

# Step 4: the adjunction on the named sets, and on random pairs (the SAME pairs for both border rules)
NAMED = {"empty": frozenset(), "speck": SPECK, "erosion": E1, "opening": O1, "X": X,
         "closing": C1, "dilation": D1, "grid": GRID}
ADJ_NAMED = {(a, y): (dil(A, CROSS) <= Y, A <= ero(Y, CROSS))
             for (a, A), (y, Y) in itertools.product(NAMED.items(), NAMED.items())}
assert len(ADJ_NAMED) == 64 and all(l == r for l, r in ADJ_NAMED.values())
TABLE4 = [("speck", "X"), ("erosion", "X"), ("X", "dilation"), ("X", "X")]
assert [ADJ_NAMED[k] for k in TABLE4] == [(False, False), (True, True), (True, True), (False, False)]

_rng = random.Random(12)
_cells = sorted(GRID)
PAIRS = [(frozenset(p for p in _cells if _rng.random() < 0.15), frozenset(p for p in _cells if _rng.random() < 0.7))
         for _ in range(20000)]
ADJ_FAIL = {rule: sum((dil(A, CROSS) <= Y) != (A <= ero(Y, CROSS, rule)) for A, Y in PAIRS)
            for rule in ("ignore", "zero")}
assert ADJ_FAIL["ignore"] == 0 and ADJ_FAIL["zero"] == 616
CORNER = frozenset({(0, 4)})
assert dil(CORNER, CROSS) <= dil(CORNER, CROSS) and not CORNER <= ero(dil(CORNER, CROSS), CROSS, "zero")

# SciPy's default border (outside = 0)
E0, C0 = ero(X, CROSS, "zero"), closing(X, CROSS, "zero")
assert len(E0) == 0
assert C0 == frozenset({(1, 2), (2, 2), (3, 2), (1, 3), (2, 3), (3, 3), (2, 1)}) and len(C0) == 7
C0_LOST, C0_GAINED = X - C0, C0 - X
assert C0_LOST == frozenset((r, 4) for r in range(N)) | {(0, 3), (4, 3)} and len(C0_LOST) == 7
assert C0_GAINED == frozenset({(1, 2), (2, 2), (3, 2)})

# ------------------------------------------------------------------ laws of dilation (Figure 5)
D_BAR, D_SPECK = dil(BAR, CROSS), dil(SPECK, CROSS)
assert len(D_BAR) == 15 and len(D_SPECK) == 5 and D_BAR & D_SPECK == {(2, 2)} and D_BAR | D_SPECK == D1
assert ero(BAR | SPECK, CROSS) >= ero(BAR, CROSS) | ero(SPECK, CROSS)
assert dil({(2, 2)}, CROSS) == frozenset((2 + a, 2 + b) for a, b in CROSS)
DIAMOND2 = msum(CROSS, CROSS)
assert len(DIAMOND2) == 13 and DIAMOND2 == nB(2)
assert ero(ero(X, CROSS), CROSS) == ero(X, DIAMOND2) and dil(dil(X, CROSS), CROSS) == dil(X, DIAMOND2)
TRIPLES = list(itertools.combinations(CROSS, 3))
assert len(TRIPLES) == 10

# ------------------------------------------------------------------ grey operators (flat, outside never wins)
def inside(r, c, n=N, m=N):
    return 0 <= r < n and 0 <= c < m


def gero(f, B):
    n, m = len(f), len(f[0])
    return [[min(f[r + a][c + b] for a, b in B if inside(r + a, c + b, n, m)) for c in range(m)] for r in range(n)]


def gdil(f, B):
    n, m = len(f), len(f[0])
    return [[max(f[r - a][c - b] for a, b in B if inside(r - a, c - b, n, m)) for c in range(m)] for r in range(n)]


def gsub(f, g):
    return [[f[r][c] - g[r][c] for c in range(len(f[0]))] for r in range(len(f))]


def total(f):
    return sum(map(sum, f))


GE, GD = gero(P, CROSS), gdil(P, CROSS)
GO, GC = gdil(GE, CROSS), gero(GD, CROSS)
NO_IMPULSE = [[40, 40, 40, 200, 200] for _ in range(N)]
assert GE == [[40, 40, 40, 40, 200] for _ in range(N)]
assert GD == [[40, 40, 200, 200, 200], [40, 255, 200, 200, 200], [255, 255, 255, 200, 200],
              [40, 255, 200, 200, 200], [40, 40, 200, 200, 200]]
assert GO == NO_IMPULSE and total(GO) == 2600 and total(P) == 2815
assert GC == [[40, 40, 40, 200, 200], [40, 40, 200, 200, 200], [40, 255, 200, 200, 200],
              [40, 40, 200, 200, 200], [40, 40, 40, 200, 200]] and total(GC) == 3295
GRAD = gsub(GD, GE)
assert GRAD == [[0, 0, 160, 160, 0], [0, 215, 160, 160, 0], [215, 215, 215, 160, 0],
                [0, 215, 160, 160, 0], [0, 0, 160, 160, 0]]
HALF_IN, HALF_OUT = gsub(P, GE), gsub(GD, P)
assert [row[3] for row in HALF_IN] == [160] * 5 and HALF_IN[2][1] == 215
assert [row[2] for row in HALF_OUT] == [160, 160, 215, 160, 160] and HALF_OUT[1][1] == HALF_OUT[2][0] == 215
WTH, BTH = gsub(P, GO), gsub(GC, P)
assert all(WTH[r][c] == (215 if (r, c) == (2, 1) else 0) for r in range(N) for c in range(N))
assert all(BTH[r][c] == (160 if (r, c) in {(1, 2), (2, 2), (3, 2)} else 0) for r in range(N) for c in range(N))
GRAD_SQ = gsub(gdil(P, SQUARE), gero(P, SQUARE))
assert sum(v == 215 for row in GRAD_SQ for v in row) == 9 and sum(v == 160 for row in GRAD_SQ for v in row) == 7
assert all(GRAD_SQ[r][c] == 215 for r in (1, 2, 3) for c in (0, 1, 2))

# Sobel 3x3, replicate border, L2 (Part 8's table) for Figure 7
def sobel_l2(f):
    rep = lambda i: min(max(i, 0), N - 1)
    g = lambda r, c: f[rep(r)][rep(c)]
    out = []
    for r in range(N):
        row = []
        for c in range(N):
            gx = sum(w * (g(r + d, c + 1) - g(r + d, c - 1)) for d, w in ((-1, 1), (0, 2), (1, 1)))
            gy = sum(w * (g(r + 1, c + d) - g(r - 1, c + d)) for d, w in ((-1, 1), (0, 2), (1, 1)))
            row.append((gx * gx + gy * gy) ** 0.5)
        out.append(row)
    return out


SOBEL = sobel_l2(P)
assert [round(v, 1) for v in SOBEL[0]] == [0, 0, 640, 640, 0]
assert [round(v, 1) for v in SOBEL[1]] == [304.1, 430.0, 476.3, 640.0, 0]
assert [round(v, 1) for v in SOBEL[2]] == [430.0, 0, 210.0, 640.0, 0]

# Threshold decomposition (Figure 6): X_t(ε f) = ε(X_t f) for every t
def thr(f, t):
    return frozenset((r, c) for r in range(N) for c in range(N) if f[r][c] >= t)


assert all(thr(GE, t) == ero(thr(P, t), CROSS) and thr(GD, t) == dil(thr(P, t), CROSS) for t in range(0, 257))
assert thr(P, 41) == X and thr(P, 200) == X and thr(P, 201) == SPECK and thr(P, 40) == GRID
LEVELS = [40, 41, 201]                     # the three distinct threshold sets: grid, mask, impulse
STACK = {t: ero(thr(P, t), CROSS) for t in LEVELS}
assert STACK[41] == E1 and STACK[201] == frozenset() and STACK[40] == GRID

# Median over the cross = max of erosions by its ten 3-point subsets (interior pixels)
for r in range(1, N - 1):
    for c in range(1, N - 1):
        med = sorted(P[r + a][c + b] for a, b in CROSS)[2]
        assert med == max(min(P[r + a][c + b] for a, b in S) for S in TRIPLES)
assert sorted(P[2 + a][1 + b] for a, b in CROSS)[2] == 40

# ------------------------------------------------------------------ granulometry (Figure 4)
SIZES = [0, 1, 2, 3]
ELEMENT_PIXELS = [len(nB(n)) for n in SIZES]
assert ELEMENT_PIXELS == [1, 5, 13, 25]
AREA = [len(opening(X, nB(n))) if n else len(X) for n in SIZES]
VOLUME = [total(gdil(gero(P, nB(n)), nB(n))) if n else total(P) for n in SIZES]
assert AREA == [11, 10, 0, 0] and VOLUME == [2815, 2600, 1000, 1000]
SPECTRUM_AREA = [AREA[i] - AREA[i + 1] for i in range(3)]
SPECTRUM_VOLUME = [VOLUME[i] - VOLUME[i + 1] for i in range(3)]
assert SPECTRUM_AREA == [1, 10, 0] and SPECTRUM_VOLUME == [215, 1600, 0]


def gopen(f, n):
    return gdil(gero(f, nB(n)), nB(n)) if n else f


assert all(gopen(gopen(P, m), n) == gopen(P, max(m, n)) for m in SIZES for n in SIZES)
# squares give the same curve on this patch
assert [total(gdil(gero(P, nB(n, SQUARE)), nB(n, SQUARE))) for n in (1, 2, 3)] == [2600, 1000, 1000]

# the patch beside a copy of itself (5 x 10): two identical bars, two sizes
TILE = [row + row for row in P]
TGRID = frozenset((r, c) for r in range(N) for c in range(2 * N))
TX = frozenset(p for p in TGRID if TILE[p[0]][p[1]] > 40)
TILE_AREA = [len(opening(TX, nB(n), grid=TGRID)) if n else len(TX) for n in SIZES]
assert TILE_AREA == [22, 10, 0, 0]
assert opening(TX, CROSS, grid=TGRID) == frozenset((r, c) for r in range(N) for c in (8, 9))

# exact disks are not a sieve; diamonds are
assert len(disk(3)) == 29 and len(disk(2)) == 13 and msum(disk(1), disk(2)) != disk(3)


def open_free(S, B):
    """Opening of the finite set S by B on the unbounded grid: the union of fitting translates."""
    S = set(S)
    centres = {(p[0] - a, p[1] - b) for p in S for a, b in B}
    fits = [x for x in centres if all((x[0] + a, x[1] + b) in S for a, b in B)]
    return {(x[0] + a, x[1] + b) for x in fits for a, b in B}


DISK_LOST = sorted(set(disk(3)) - open_free(disk(3), disk(2)))
assert DISK_LOST == [(-2, -2), (-2, 2), (2, -2), (2, 2)]
assert open_free(nB(3), nB(2)) == set(nB(3))

# ------------------------------------------------------------------ OpenCV replay (Figure 10)
def cv_offsets(K, anchor=None):
    h, w = len(K), len(K[0])
    ax, ay = (w // 2, h // 2) if anchor is None else anchor
    return tuple((i - ay, j - ax) for i in range(h) for j in range(w) if K[i][j])


def cv_erode(S, K, anchor=None, grid=GRID):          # dst(x) = min_k src(x + k); outside never wins
    O = cv_offsets(K, anchor)
    return frozenset(x for x in grid if all((x[0] + a, x[1] + b) in S for a, b in O if (x[0] + a, x[1] + b) in grid))


def cv_dilate(S, K, anchor=None, grid=GRID):         # dst(x) = max_k src(x + k): the SAME offsets, no reflection
    O = cv_offsets(K, anchor)
    return frozenset(x for x in grid if any((x[0] + a, x[1] + b) in S for a, b in O))


K22, K12 = [[1, 1], [1, 1]], [[1, 1]]
assert cv_offsets(K22) == ((-1, -1), (-1, 0), (0, -1), (0, 0))
CV_OPEN22 = cv_dilate(cv_erode(X, K22), K22)
CV_CLOSE22 = cv_erode(cv_dilate(X, K22), K22)
TRUE_OPEN22 = dil(cv_erode(X, K22), cv_offsets(K22))   # Minkowski dilation by the same offsets = reflected scan
TRUE_CLOSE22 = cv_erode(dil(X, cv_offsets(K22)), K22)
assert CV_OPEN22 == E1 and len(CV_OPEN22) == 5
assert CV_CLOSE22 == E1 | {(3, 2), (3, 3)} and len(CV_CLOSE22) == 7
CV_CLOSE22_LOST = X - CV_CLOSE22
assert CV_CLOSE22_LOST == frozenset({(0, 3), (1, 3), (2, 3), (4, 3), (2, 1)}) and len(CV_CLOSE22_LOST) == 5
assert CV_CLOSE22 - X == {(3, 2)}
assert TRUE_OPEN22 == BAR and TRUE_CLOSE22 == X | {(2, 0), (2, 2)} and len(TRUE_CLOSE22) == 13
assert TRUE_OPEN22 <= X <= TRUE_CLOSE22 and not X <= CV_CLOSE22
# the fix: dilate with the reflected anchor (0, 0)
assert cv_erode(cv_dilate(X, K22, anchor=(0, 0)), K22) == TRUE_CLOSE22
assert cv_dilate(cv_erode(X, K22), K22, anchor=(0, 0)) == TRUE_OPEN22
# the 1x2 kernel behaves the same way
assert cv_dilate(cv_erode(X, K12), K12) == E1 and cv_erode(cv_dilate(X, K12), K12) == E1 | {(2, 2), (2, 3)}
# issue #23605's example, replayed
A5 = [[0, 0, 0, 0, 0], [0, 1, 1, 0, 0], [0, 1, 1, 1, 0], [0, 1, 1, 1, 0], [0, 0, 0, 0, 0]]
B3 = [[1, 1, 0], [0, 1, 1], [1, 0, 0]]
A5S = frozenset((r, c) for r in range(5) for c in range(5) if A5[r][c])
R23605 = cv_dilate(cv_erode(A5S, B3), B3)
assert R23605 == frozenset({(1, 3), (2, 1), (2, 2), (3, 2), (3, 3)}) and not R23605 <= A5S

# iterations=2: erode twice, dilate twice (an opening by 2B), against opening twice
assert dil(dil(ero(ero(X, CROSS), CROSS), CROSS), CROSS) == frozenset()
assert gdil(gdil(gero(gero(P, CROSS), CROSS), CROSS), CROSS) == [[40] * 5 for _ in range(N)]
assert opening(opening(X, CROSS), CROSS) == O1
assert opening(X, SQUARE) == BAR and dil(dil(ero(ero(X, SQUARE), SQUARE), SQUARE), SQUARE) == frozenset()

# ------------------------------------------------------------------ element shapes
def cv_ellipse(w, h):
    r, c = h // 2, w // 2
    inv = 1.0 / (r * r) if r else 0.0
    rows = []
    for i in range(h):
        dy = i - r
        j1 = j2 = 0
        if abs(dy) <= r:
            dx = int(round(c * ((r * r - dy * dy) * inv) ** 0.5))
            j1, j2 = max(c - dx, 0), min(c + dx + 1, w)
        rows.append([1 if j1 <= j < j2 else 0 for j in range(w)])
    return rows


assert cv_ellipse(3, 3) == [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
assert sum(map(sum, cv_ellipse(5, 5))) == 17 and len(disk(2)) == 13

# ------------------------------------------------------------------ reconstruction (Figure 8)
def grecon(marker, mask, B=SQUARE):
    m = [[min(marker[r][c], mask[r][c]) for c in range(N)] for r in range(N)]
    while True:
        d = [[min(max(m[r + a][c + b] for a, b in B if inside(r + a, c + b)), mask[r][c]) for c in range(N)]
             for r in range(N)]
        if d == m:
            return m
        m = d


assert grecon(GE, P) == GO                          # opening by reconstruction = opening, here
HMAX = {h: grecon([[v - h for v in row] for row in P], P) for h in (100, 180, 215)}
assert (HMAX[100][0][3], HMAX[100][2][1], HMAX[100][0][0]) == (100, 155, 40)
assert (HMAX[180][0][3], HMAX[180][2][1], HMAX[180][0][0]) == (40, 75, 40)
assert HMAX[215] == [[40] * 5 for _ in range(N)]
DYNAMIC = {"bar": 160, "impulse": 215}
assert all(grecon([[v - h for v in row] for row in P], P)[0][3] > 40 for h in range(1, 160))
assert grecon([[v - 160 for v in row] for row in P], P)[0][3] == 40
REG_MAX = frozenset((r, c) for r in range(N) for c in range(N)
                    if P[r][c] - grecon([[v - 1 for v in row] for row in P], P)[r][c] > 0)
assert REG_MAX == X

# ------------------------------------------------------------------ distance transform as stacked erosions
DT = [[0] * N for _ in range(N)]
S = X
while S:
    for r, c in S:
        DT[r][c] += 1
    S = ero(S, CROSS)
_bg = [p for p in GRID if p not in X]
assert DT == [[min(abs(r - a) + abs(c - b) for a, b in _bg) if (r, c) in X else 0 for c in range(N)] for r in range(N)]
assert [DT[0][3], DT[0][4], DT[2][1]] == [1, 2, 1]

if __name__ == "__main__":
    print("all asserts hold")
    print("adjunction failures on the same 20,000 random pairs:", ADJ_FAIL)
    print("SciPy-default closing lost", sorted(C0_LOST), "gained", sorted(C0_GAINED))
