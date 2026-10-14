#!/usr/bin/env python3
"""The numbers behind thresholding-and-segmentation, computed from definitions and asserted against the article.

Nothing loads an image and nothing imports a library: the series' 5x5 patch is typed in, and every
library result is a plain-Python replay of the rule read at a pinned commit (OpenCV 802cf95, the same
rules at tag 4.10.0; scikit-image b700edc, with v0.24.0 against v0.25.0 for the watershed change):

- OpenCV's 8-bit GaussianBlur: the 1-D kernel quantised to 8 fraction bits by error diffusion
  (getGaussianKernelFixedPoint_ED -> [61, 134, 61]/256), an exact horizontal pass, a 16.16 vertical
  pass, rounded half up (smooth.dispatch.cpp, fixedpoint.inl.hpp).
- OpenCV's own Otsu loop (thresh.cpp getThreshVal_Otsu, IEEE doubles, first strict maximum) and its
  triangle method; scikit-image's threshold_otsu (first argmax), threshold_isodata, threshold_triangle.
- scikit-image's watershed (heap on (value, age), label at push, cost clamp from v0.25) and OpenCV's
  cv::watershed (4-neighbour max channel difference, FIFO per level, labels at pop, -1 frame).
- Local thresholds as OpenCV's adaptiveThreshold (MEAN_C, replicate border, mean rounded to 8 bits)
  and scikit-image's _mean_std (centred window, numpy 'reflect' padding, population std).
- Two-class Gaussian mixtures binned to 0..255 in closed form (normal CDF), for Figure 6.
"""
import heapq
import math
from collections import deque

# ------------------------------------------------------------------ the patch and its blur
P = [[40, 40, 40, 200, 200],
     [40, 40, 40, 200, 200],
     [40, 255, 40, 200, 200],
     [40, 40, 40, 200, 200],
     [40, 40, 40, 200, 200]]
N = 5


def r101(i, n):
    """OpenCV's BORDER_REFLECT_101 (numpy 'reflect'): -1 -> 1, n -> n-2."""
    while i < 0 or i > n - 1:
        i = -i if i < 0 else 2 * (n - 1) - i
    return i


def rep(i, n):
    return min(max(i, 0), n - 1)


SIG = 0.8
_e = math.exp(-1 / (2 * SIG * SIG))
KF = [_e / (1 + 2 * _e), 1 / (1 + 2 * _e), _e / (1 + 2 * _e)]       # 0.239, 0.522, 0.239


def fixed_kernel(kf, bits=8):
    """getGaussianKernelFixedPoint_ED for a 3-tap kernel: round the outer tap, centre takes the rest."""
    mult = 1 << bits
    v0 = int(math.floor(kf[0] * mult + 0.5))
    return [v0, mult - 2 * v0, v0]


KQ = fixed_kernel(KF)                                                # [61, 134, 61]


def blur_fixed(img):
    """cv2.GaussianBlur(img, (3, 3), 0.8) on uint8: exact integer pipeline, reflect-101, round half up."""
    n = len(img)
    h = [[sum(KQ[t + 1] * img[i][r101(j + t, n)] for t in (-1, 0, 1)) for j in range(n)] for i in range(n)]
    v = [[sum(KQ[t + 1] * h[r101(i + t, n)][j] for t in (-1, 0, 1)) for j in range(n)] for i in range(n)]
    return [[(v[i][j] + 32768) >> 16 for j in range(n)] for i in range(n)], [[x / 65536 for x in r] for r in v]


def blur_float(img):
    n = len(img)
    h = [[sum(KF[t + 1] * img[i][r101(j + t, n)] for t in (-1, 0, 1)) for j in range(n)] for i in range(n)]
    return [[sum(KF[t + 1] * h[r101(i + t, n)][j] for t in (-1, 0, 1)) for j in range(n)] for i in range(n)]


G3, G3X = blur_fixed(P)          # what OpenCV returns, and its exact pre-rounding value
G3F = blur_float(P)              # the float convolution, for comparison


# ------------------------------------------------------------------ histograms and Otsu by hand
def hist(img):
    h = {}
    for row in img:
        for v in row:
            h[v] = h.get(v, 0) + 1
    return dict(sorted(h.items()))


def otsu_rows(h):
    """Every cut between consecutive occupied levels: n0, n1, mu0, mu1, sigma_B^2, sigma_W^2, eta."""
    n = sum(h.values())
    lv = sorted(h)
    mean = sum(v * c for v, c in h.items()) / n
    var = sum(c * (v - mean) ** 2 for v, c in h.items()) / n
    rows = []
    for k in range(len(lv) - 1):
        c0, c1 = lv[:k + 1], lv[k + 1:]
        n0 = sum(h[v] for v in c0)
        n1 = n - n0
        m0 = sum(h[v] * v for v in c0) / n0
        m1 = sum(h[v] * v for v in c1) / n1
        w0, w1 = n0 / n, n1 / n
        sb = w0 * w1 * (m0 - m1) ** 2
        sw = w0 * sum(h[v] * (v - m0) ** 2 for v in c0) / n0 + w1 * sum(h[v] * (v - m1) ** 2 for v in c1) / n1
        rows.append(dict(lo=lv[k], hi=lv[k + 1], n0=n0, n1=n1, m0=m0, m1=m1, sb=sb, sw=sw, eta=sb / var))
    return rows, mean, var


HR, HS = hist(P), hist(G3)
RAW, RAW_MEAN, RAW_VAR = otsu_rows(HR)
SM, SM_MEAN, SM_VAR = otsu_rows(HS)
RAW_BEST = max(RAW, key=lambda r: r["sb"])
SM_BEST = max(SM, key=lambda r: r["sb"])


# ------------------------------------------------------------------ library threshold rules, replayed
FLT_EPSILON = 1.1920928955078125e-07


def hist256(img):
    h = [0] * 256
    for row in img:
        for v in row:
            h[v] += 1
    return h


def ocv_otsu(h):
    """getThreshVal_Otsu (OpenCV's own code; IPP builds call ippiComputeThreshold_Otsu_8u_C1R first)."""
    scale = 1.0 / sum(h)
    mu = 0.0
    for i in range(256):
        mu += i * float(h[i])
    mu *= scale
    mu1 = q1 = max_sigma = max_val = 0.0
    curve = []
    for i in range(256):
        p_i = h[i] * scale
        mu1 *= q1
        q1 += p_i
        q2 = 1.0 - q1
        if min(q1, q2) < FLT_EPSILON or max(q1, q2) > 1.0 - FLT_EPSILON:
            continue
        mu1 = (mu1 + i * p_i) / q1
        mu2 = (mu - q1 * mu1) / q2
        sigma = q1 * q2 * (mu1 - mu2) * (mu1 - mu2)
        curve.append((i, sigma))
        if sigma > max_sigma:
            max_sigma, max_val = sigma, i
    return int(max_val), curve


def ocv_triangle(h0):
    h = list(h0)
    lb = next(i for i in range(256) if h[i] > 0)
    lb = lb - 1 if lb > 0 else lb
    rb = next(i for i in range(255, 0, -1) if h[i] > 0)
    rb = rb + 1 if rb < 255 else rb
    mx = max_ind = 0
    for i in range(256):
        if h[i] > mx:
            mx, max_ind = h[i], i
    flip = max_ind - lb < rb - max_ind
    if flip:
        h = h[::-1]
        lb, max_ind = 255 - rb, 255 - max_ind
    thresh, dist = lb, 0
    for i in range(lb + 1, max_ind + 1):
        t = mx * i + (lb - max_ind) * h[i]
        if t > dist:
            dist, thresh = t, i
    thresh -= 1
    return 255 - thresh if flip else thresh


def sk_hist(img):
    vals = [v for row in img for v in row]
    lo, hi = min(vals), max(vals)
    counts = [0] * (hi - lo + 1)
    for v in vals:
        counts[v - lo] += 1
    return counts, list(range(lo, hi + 1))


def sk_otsu(img):
    c, x = sk_hist(img)
    n = len(c)
    w1 = [sum(c[:k + 1]) for k in range(n)]
    w2 = [sum(c[k:]) for k in range(n)]
    m1 = [sum(c[i] * x[i] for i in range(k + 1)) / w1[k] for k in range(n)]
    m2 = [sum(c[i] * x[i] for i in range(k, n)) / w2[k] for k in range(n)]
    v = [w1[k] * w2[k + 1] * (m1[k] - m2[k + 1]) ** 2 for k in range(n - 1)]
    return x[v.index(max(v))]


def sk_isodata(img):
    c, x = sk_hist(img)
    n, tot = len(c), sum(c)
    out = []
    for k in range(n - 1):
        lo = sum(c[i] * x[i] for i in range(k + 1)) / sum(c[:k + 1])
        hi = sum(c[i] * x[i] for i in range(k + 1, n)) / (tot - sum(c[:k + 1]))
        if 0 <= (lo + hi) / 2 - x[k] < 1:
            out.append(x[k])
    return out


def sk_triangle(img):
    hist_, x = sk_hist(img)
    nb = len(hist_)
    peak = hist_.index(max(hist_))
    nz = [k for k in range(nb) if hist_[k]]
    lo, hi = nz[0], nz[-1]
    flip = peak - lo < hi - peak
    h = hist_[::-1] if flip else list(hist_)
    if flip:
        lo, peak = nb - hi - 1, nb - peak - 1
    width = peak - lo
    norm = math.hypot(h[peak], width)
    length = [(h[peak] / norm) * k - (width / norm) * h[k + lo] for k in range(width)]
    arg = length.index(max(length)) + lo
    return x[nb - arg - 1 if flip else arg]


OCV_OTSU_RAW, CURVE_RAW = ocv_otsu(hist256(P))
OCV_OTSU_SM, CURVE_SM = ocv_otsu(hist256(G3))
LIB = {
    "raw": dict(otsu=OCV_OTSU_RAW, sk_otsu=sk_otsu(P), isodata=sk_isodata(P), tri=ocv_triangle(hist256(P)),
                sk_tri=sk_triangle(P)),
    "smooth": dict(otsu=OCV_OTSU_SM, sk_otsu=sk_otsu(G3), isodata=sk_isodata(G3), tri=ocv_triangle(hist256(G3)),
                   sk_tri=sk_triangle(G3)),
}


def mask(img, t):
    return [[1 if v > t else 0 for v in row] for row in img]


MASK_RAW, MASK_SM = mask(P, OCV_OTSU_RAW), mask(G3, OCV_OTSU_SM)


# ------------------------------------------------------------------ the relief and its watersheds
def sobel_l2(img):
    """3x3 Sobel, L2, replicate border (== scipy 'reflect' for 3 taps, so skimage.filters.sobel x 4*sqrt2*255)."""
    n = len(img)
    g = lambda i, j: img[rep(i, n)][rep(j, n)]
    out = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            gx = sum(w * (g(i + a, j + 1) - g(i + a, j - 1)) for a, w in ((-1, 1), (0, 2), (1, 1)))
            gy = sum(w * (g(i + 1, j + b) - g(i - 1, j + b)) for b, w in ((-1, 1), (0, 2), (1, 1)))
            out[i][j] = math.hypot(gx, gy)
    return out


M = sobel_l2(P)
NB4 = ((-1, 0), (0, -1), (0, 1), (1, 0))
NB8 = tuple((a, b) for a in (-1, 0, 1) for b in (-1, 0, 1) if (a, b) != (0, 0))


def regional_minima(F, nb):
    n = len(F)
    seen, out = set(), []
    for i in range(n):
        for j in range(n):
            if (i, j) in seen:
                continue
            v, comp, ok, k = F[i][j], [(i, j)], True, 0
            seen.add((i, j))
            while k < len(comp):
                a, b = comp[k]
                k += 1
                for da, db in nb:
                    x, y = a + da, b + db
                    if 0 <= x < n and 0 <= y < n:
                        if F[x][y] == v and (x, y) not in seen:
                            seen.add((x, y))
                            comp.append((x, y))
                        elif F[x][y] < v:
                            ok = False
            if ok:
                out.append(sorted(comp))
    return out


def sk_watershed(F, markers, clamp=True, nb=NB4):
    """skimage watershed_raveled, simple case: heap (value, age), neighbour labelled at push."""
    n = len(F)
    out = [r[:] for r in markers]
    hp, age, log = [], 1, []
    for i in range(n):
        for j in range(n):
            if out[i][j]:
                heapq.heappush(hp, (F[i][j], 0, i * n + j))
    while hp:
        val, _, idx = heapq.heappop(hp)
        i, j = divmod(idx, n)
        log.append(((i, j), val, out[i][j]))
        for di, dj in nb:
            x, y = i + di, j + dj
            if 0 <= x < n and 0 <= y < n and not out[x][y]:
                age += 1
                out[x][y] = out[i][j]
                nv = F[x][y]
                if clamp and nv < val:
                    nv = val
                heapq.heappush(hp, (nv, age, x * n + y))
    return out, log


MINIMA = regional_minima(M, NB4)
MINIMA8 = regional_minima(M, NB8)
MK_NONE = [[0] * N for _ in range(N)]
for _k, _comp in enumerate(MINIMA, 1):
    for (_i, _j) in _comp:
        MK_NONE[_i][_j] = _k
WS_NONE, _ = sk_watershed(M, MK_NONE)
WS_NONE_024, _ = sk_watershed(M, MK_NONE, clamp=False)
HAND = [[0] * N for _ in range(N)]
HAND[0][0], HAND[2][4] = 1, 2
WS_HAND, FLOOD = sk_watershed(M, HAND)
WS_HAND_024, FLOOD_024 = sk_watershed(M, HAND, clamp=False)
WS_NONE8, _ = sk_watershed(M, MK_NONE, nb=NB8)                                   # connectivity=2


def minimax_pass(F, a, b, nb=NB4):
    """Lowest possible highest point on a path from set a to set b (the pass between basins)."""
    n = len(F)
    best = {p: F[p[0]][p[1]] for p in a}
    hp = [(v, p) for p, v in best.items()]
    heapq.heapify(hp)
    bset = set(b)
    while hp:
        v, (i, j) = heapq.heappop(hp)
        if (i, j) in bset:
            return v
        for di, dj in nb:
            x, y = i + di, j + dj
            if 0 <= x < n and 0 <= y < n:
                nv = max(v, F[x][y])
                if nv < best.get((x, y), float("inf")):
                    best[(x, y)] = nv
                    heapq.heappush(hp, (nv, (x, y)))
    return None


TL, BR, IMP, BL = MINIMA[0], MINIMA[1], MINIMA[2], MINIMA[3]
PASS_TL_IMP = minimax_pass(M, TL, IMP)
PASS_TL_BL = minimax_pass(M, TL, BL)
PASS_DARK_BRIGHT = minimax_pass(M, TL + IMP + BL, BR)
PASS8_TL_IMP = minimax_pass(M, TL, IMP, NB8)
PASS8_DARK_BRIGHT = minimax_pass(M, TL + IMP + BL, BR, NB8)


def hminima_count(F, h, nb=NB8):
    """Regional minima left after suppressing minima shallower than h (reconstruction by erosion)."""
    n = len(F)
    J = [[F[i][j] + h for j in range(n)] for i in range(n)]
    while True:
        K = [[max(F[i][j], min([J[i][j]] + [J[i + a][j + b] for a, b in nb
                                            if 0 <= i + a < n and 0 <= j + b < n])) for j in range(n)]
             for i in range(n)]
        if K == J:
            break
        J = K
    return len(regional_minima(J, nb))


HMIN = {h: hminima_count(M, h) for h in (304, 305, 639, 640)}          # 8-connected, as imhmin / h_minima
HMIN4 = {h: hminima_count(M, h, NB4) for h in (429, 430, 639, 640)}


def ocv_watershed(img, markers):
    """cv::watershed on a grey image copied to 3 channels: priority = |difference| to the 4-neighbour."""
    n = len(img)
    m = [r[:] for r in markers]
    WS, INQ = -1, -2
    q = [deque() for _ in range(256)]
    d = lambda a, b: abs(img[a[0]][a[1]] - img[b[0]][b[1]])
    for j in range(n):
        m[0][j] = m[n - 1][j] = WS
    for i in range(1, n - 1):
        m[i][0] = m[i][n - 1] = WS
        for j in range(1, n - 1):
            if m[i][j] < 0:
                m[i][j] = 0
            nbrs = ((i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j))
            if m[i][j] == 0 and any(m[x][y] > 0 for x, y in nbrs):
                q[min(d((i, j), (x, y)) for x, y in nbrs if m[x][y] > 0)].append((i, j))
                m[i][j] = INQ
    act = next((k for k in range(256) if q[k]), 256)
    order = []
    if act == 256:
        return m, order
    while True:
        if not q[act]:
            act = next((k for k in range(act + 1, 256) if q[k]), 256)
            if act == 256:
                break
        i, j = q[act].popleft()
        lab = 0
        for x, y in ((i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j)):
            t = m[x][y]
            if t > 0:
                lab = t if lab == 0 else (lab if t == lab else WS)
        m[i][j] = lab
        order.append(((i, j), act, lab))
        if lab == WS:
            continue
        for x, y in ((i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j)):
            if m[x][y] == 0:
                t = d((i, j), (x, y))
                q[t].append((x, y))
                act = min(act, t)
                m[x][y] = INQ
    return m, order


def _mk(points):
    out = [[0] * N for _ in range(N)]
    for (i, j), v in points.items():
        out[i][j] = v
    return out


OCV_A, _ = ocv_watershed(P, _mk({(0, 0): 1, (2, 4): 2}))                         # the hand markers, on the border
OCV_B, OCV_B_ORDER = ocv_watershed(P, _mk({(1, 1): 1, (2, 3): 2}))              # one interior pixel each
OCV_C, _ = ocv_watershed(P, _mk({(1, 1): 1, (2, 1): 1, (3, 1): 1, (1, 3): 2, (2, 3): 2, (3, 3): 2}))  # strokes


# ------------------------------------------------------------------ two lights: local thresholds
SH = [[round(0.2 * v) for v in row] for row in P]                               # the patch at a fifth of the light
T2 = [P[i] + SH[i] for i in range(N)]                                           # 5 x 10, lit | shadow
W2 = 10
TRUTH = [[1 if (j % 5) >= 3 else 0 for j in range(W2)] for _ in range(N)]
IMPULSES = {(2, 1), (2, 6)}
H2 = hist(T2)
OTSU_T2, _ = ocv_otsu(hist256(T2))


def errors(mk):
    return sum(mk[i][j] != TRUTH[i][j] for i in range(N) for j in range(W2) if (i, j) not in IMPULSES)


def _get(img, i, j, f):
    return img[f(i, len(img))][f(j, len(img[0]))]


def win(img, i, j, w, f):
    r = w // 2
    vals = [_get(img, i + a, j + b, f) for a in range(-r, r + 1) for b in range(-r, r + 1)]
    m = sum(vals) / len(vals)
    return m, math.sqrt(max(sum(v * v for v in vals) / len(vals) - m * m, 0.0))


def mean_c(img, w, C=0):
    """cv2.adaptiveThreshold(img, 255, ADAPTIVE_THRESH_MEAN_C, THRESH_BINARY, w, C)."""
    k = math.ceil(C)
    T = [[int(math.floor(win(img, i, j, w, rep)[0] + 0.5)) - k for j in range(len(img[0]))] for i in range(len(img))]
    return [[1 if img[i][j] > T[i][j] else 0 for j in range(len(img[0]))] for i in range(len(img))], T


def sauvola(img, w, k=0.5, R=128.0):
    T = []
    for i in range(len(img)):
        row = []
        for j in range(len(img[0])):
            m, s = win(img, i, j, w, r101)
            row.append(m * (1 + k * (s / R - 1)))
        T.append(row)
    return [[1 if img[i][j] > T[i][j] else 0 for j in range(len(img[0]))] for i in range(len(img))], T


def niblack(img, w, k=0.2):
    T = [[(lambda ms: ms[0] - k * ms[1])(win(img, i, j, w, r101)) for j in range(len(img[0]))] for i in range(len(img))]
    return [[1 if img[i][j] > T[i][j] else 0 for j in range(len(img[0]))] for i in range(len(img))], T


GLOBAL_T2 = mask(T2, OTSU_T2)
LOCAL = {}
for _w in (3, 5, 7, 9):
    LOCAL[("meanc", _w)] = mean_c(T2, _w)
    LOCAL[("sauvola", _w)] = sauvola(T2, _w)
    LOCAL[("sauvola_sk", _w)] = sauvola(T2, _w, 0.2, 127.5)
    LOCAL[("niblack", _w)] = niblack(T2, _w)
LOCAL_ERR = {key: errors(v[0]) for key, v in LOCAL.items()}


# ------------------------------------------------------------------ closed-form histograms (Figure 6)
def Phi(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def mixture(comps):
    """Each level's share of the mixture, v - 0.5 to v + 0.5; tails beyond 0..255 are dropped, not piled up."""
    return [sum(w * (Phi((v + 0.5 - m) / s) - Phi((v - 0.5 - m) / s)) for w, m, s in comps) for v in range(256)]


def otsu_curve(h):
    tot = sum(h)
    mu = sum(i * h[i] for i in range(256)) / tot
    var = sum(h[i] * (i - mu) ** 2 for i in range(256)) / tot
    w0 = s0 = 0.0
    cur = []
    for k in range(255):
        w0 += h[k] / tot
        s0 += k * h[k] / tot
        w1 = 1 - w0
        cur.append(0.0 if w0 < 1e-12 or w1 < 1e-12 else w0 * w1 * (s0 / w0 - (mu - s0) / w1) ** 2)
    return cur, var


def best_cut(comps):
    """The cut with the least misclassified mass, for known classes (class 0 is <= t)."""
    errs = [cut_error(comps, t) for t in range(255)]
    return errs.index(min(errs))


def cut_error(comps, t):
    (w0, m0, s0), (w1, m1, s1) = comps
    return w0 * (1 - Phi((t + 0.5 - m0) / s0)) + w1 * Phi((t + 0.5 - m1) / s1)


PANELS = {
    "equal": [(0.5, 70, 15), (0.5, 170, 15)],
    "sizes": [(0.99, 70, 15), (0.01, 170, 15)],
    "spreads": [(0.5, 70, 8), (0.5, 170, 35)],
    "overlap": [(0.5, 100, 25), (0.5, 150, 25)],
}
SHAPES = {}
for _name, _comps in PANELS.items():
    _h = mixture(_comps)
    _cur, _var = otsu_curve(_h)
    _k = _cur.index(max(_cur))
    _b = best_cut(_comps)
    SHAPES[_name] = dict(h=_h, cur=_cur, var=_var, otsu=_k, eta=max(_cur) / _var, best=_b,
                         err_otsu=cut_error(_comps, _k), err_best=cut_error(_comps, _b),
                         maxima=[i for i in range(1, 254) if _cur[i] > _cur[i - 1] and _cur[i] >= _cur[i + 1]])


def otsu_cut(comps):
    cur, var = otsu_curve(mixture(comps))
    return cur.index(max(cur)), max(cur) / var


def flip_fraction():
    lo, hi = 0.01, 0.05
    for _ in range(30):
        mid = (lo + hi) / 2
        if otsu_cut([(1 - mid, 70, 15), (mid, 170, 15)])[0] < 100:
            lo = mid
        else:
            hi = mid
    return hi


FLIP = flip_fraction()
ETA_5PC = otsu_cut([(0.95, 70, 15), (0.05, 170, 15)])
THREE = otsu_curve(mixture([(0.35, 50, 10), (0.30, 128, 10), (0.35, 206, 10)]))
THREE_MAX = [i for i in range(1, 254) if THREE[0][i] > THREE[0][i - 1] and THREE[0][i] >= THREE[0][i + 1]]
BAYES_EQUAL = {d: Phi(-d / 2) for d in (2, 3, 4, 4.65, 6)}


# ------------------------------------------------------------------ asserts: the article's numbers
def r(x, nd=1):
    return round(x + 0.0, nd)


assert KQ == [61, 134, 61]
assert G3 == [[40, 40, 78, 162, 200], [64, 67, 90, 162, 200], [94, 99, 105, 162, 200],
              [64, 67, 90, 162, 200], [40, 40, 78, 162, 200]]
assert (r(G3X[1][2], 3), r(G3F[1][2], 3), r(G3X[1][0], 3), r(G3F[1][0], 3)) == (90.332, 90.52, 64.415, 64.561)
assert HR == {40: 14, 200: 10, 255: 1} and sum(v * c for v, c in HR.items()) == 2815
assert HS == {40: 4, 64: 2, 67: 2, 78: 2, 90: 2, 94: 1, 99: 1, 105: 1, 162: 5, 200: 5}
assert (r(RAW_BEST["sb"]), r(RAW_VAR, 2), r(RAW_BEST["eta"], 3)) == (6708.2, 6818.24, 0.984)
assert (r(RAW[1]["sb"]), r(RAW[1]["eta"], 3)) == (844.9, 0.124)
assert (SM_BEST["lo"], SM_BEST["hi"], SM_BEST["n0"], SM_BEST["n1"]) == (105, 162, 15, 10)
assert (r(SM_MEAN, 2), r(SM_VAR, 2)) == (114.64, 3370.47)
assert (r(SM_BEST["m0"], 2), r(SM_BEST["m1"], 1), r(SM_BEST["sb"], 1), r(SM_BEST["sw"], 1), r(SM_BEST["eta"], 3)) \
    == (70.4, 181.0, 2935.8, 434.7, 0.871)
assert all(abs(row["sb"] + row["sw"] - SM_VAR) < 1e-9 for row in SM)
assert [r(row["sb"]) for row in SM] == [1061.2, 1402.4, 1802.5, 2153.9, 2445.7, 2611.9, 2777.0, 2935.8, 1821.6]
assert LIB["raw"] == dict(otsu=40, sk_otsu=40, isodata=[122], tri=42, sk_tri=41)
assert LIB["smooth"] == dict(otsu=105, sk_otsu=105, isodata=[125], tri=160, sk_tri=161)
assert [i for i, s in CURVE_SM if s == max(x for _, x in CURVE_SM)] == list(range(105, 162))   # bit-exact plateau
assert sum(map(sum, MASK_RAW)) == 11 and sum(map(sum, MASK_SM)) == 10 and MASK_SM[2][1] == 0 and MASK_RAW[2][1] == 1
assert [[r(v) for v in row] for row in M] == [[0, 0, 640, 640, 0], [304.1, 430, 476.3, 640, 0], [430, 0, 210, 640, 0],
                                              [304.1, 430, 476.3, 640, 0], [0, 0, 640, 640, 0]]
assert MINIMA == MINIMA8 == [[(0, 0), (0, 1)], [(0, 4), (1, 4), (2, 4), (3, 4), (4, 4)], [(2, 1)], [(4, 0), (4, 1)]]
assert WS_NONE == WS_NONE_024 == [[1, 1, 1, 2, 2], [1, 1, 3, 2, 2], [3, 3, 3, 2, 2], [4, 3, 3, 2, 2], [4, 4, 4, 2, 2]]
assert WS_HAND == WS_HAND_024 == [[1, 1, 1, 2, 2]] * 5
assert sorted({r(v) for _, v, _ in FLOOD}) == [0.0, 304.1, 430.0, 476.3, 640.0]
assert (PASS_TL_IMP, PASS_TL_BL, PASS_DARK_BRIGHT) == (430.0, 430.0, 640.0)
assert HMIN == {304: 4, 305: 2, 639: 2, 640: 1} and HMIN4 == {429: 4, 430: 2, 639: 2, 640: 1}
assert (r(PASS8_TL_IMP), PASS8_DARK_BRIGHT) == (304.1, 640.0)
assert WS_NONE8 == [[1, 1, 1, 2, 2], [1, 1, 1, 2, 2], [3, 3, 3, 2, 2], [3, 3, 3, 2, 2], [4, 4, 4, 2, 2]]
assert OCV_A == [[-1] * 5, [-1, 0, 0, 0, -1], [-1, 0, 0, 0, -1], [-1, 0, 0, 0, -1], [-1] * 5]
assert OCV_B == [[-1] * 5, [-1, 1, 1, -1, -1], [-1, -1, -1, 2, -1], [-1, 2, 2, 2, -1], [-1] * 5]
assert OCV_C == [[-1] * 5, [-1, 1, -1, 2, -1], [-1, 1, -1, 2, -1], [-1, 1, -1, 2, -1], [-1] * 5]
assert H2 == {8: 14, 40: 24, 51: 1, 200: 10, 255: 1} and OTSU_T2 == 51 and errors(GLOBAL_T2) == 10
assert LOCAL_ERR[("meanc", 3)] == 5 and LOCAL_ERR[("sauvola", 3)] == 8 and LOCAL_ERR[("niblack", 3)] == 5
assert all(LOCAL_ERR[(m, w)] == 0 for m in ("meanc", "sauvola", "sauvola_sk", "niblack") for w in (5, 7))
assert LOCAL_ERR[("meanc", 9)] == 5 and LOCAL_ERR[("sauvola", 9)] == 0
assert (SHAPES["equal"]["otsu"], SHAPES["equal"]["best"]) == (120, 119) and r(SHAPES["equal"]["eta"], 3) == 0.918
assert (SHAPES["sizes"]["otsu"], SHAPES["sizes"]["best"]) == (72, 130) and SHAPES["sizes"]["maxima"] == [72, 118]
assert (r(100 * SHAPES["sizes"]["err_otsu"], 0), r(100 * SHAPES["sizes"]["err_best"], 2)) == (43.0, 0.01)
assert (SHAPES["spreads"]["otsu"], SHAPES["spreads"]["best"]) == (124, 92)
assert (r(100 * SHAPES["spreads"]["err_otsu"], 1), r(100 * SHAPES["spreads"]["err_best"], 1)) == (4.8, 0.8)
assert (SHAPES["overlap"]["otsu"], r(100 * SHAPES["overlap"]["err_otsu"], 1)) == (125, 15.9)
assert r(SHAPES["sizes"]["eta"], 2) == 0.51 and r(SHAPES["overlap"]["eta"], 2) == 0.68 and r(ETA_5PC[1], 2) == 0.68
assert r(100 * FLIP, 1) == 2.0 and THREE_MAX == [112, 143]
assert [r(100 * BAYES_EQUAL[d], 1) for d in (2, 3, 4, 4.65, 6)] == [15.9, 6.7, 2.3, 1.0, 0.1]

if __name__ == "__main__":
    print("smoothed patch (OpenCV 8-bit):", G3)
    for row in SM:
        print("  cut %3d|%3d  n0 %2d  mu0 %7.3f  mu1 %7.3f  sB %8.2f  sW %8.2f  eta %.4f"
              % (row["lo"], row["hi"], row["n0"], row["m0"], row["m1"], row["sb"], row["sw"], row["eta"]))
    print("mean %.3f var %.3f" % (SM_MEAN, SM_VAR), "libraries", LIB)
    print("flood levels with hand markers:", [(p, r(v)) for p, v, _ in FLOOD])
    print("passes", PASS_TL_IMP, PASS_TL_BL, PASS_DARK_BRIGHT, "h-minima", HMIN)
    print("OpenCV B order", OCV_B_ORDER)
    for k in sorted(LOCAL_ERR):
        print("local", k, LOCAL_ERR[k])
    for k, v in SHAPES.items():
        print(k, v["otsu"], v["best"], round(v["eta"], 3), round(100 * v["err_otsu"], 2), round(100 * v["err_best"], 3),
              v["maxima"])
    print("flip below %.2f%%" % (100 * FLIP), "eta at 5%%: %.3f" % ETA_5PC[1], "three humps maxima", THREE_MAX)
    print("all asserts passed")
