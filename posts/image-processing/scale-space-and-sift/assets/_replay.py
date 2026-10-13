"""Plain-Python replay of OpenCV's SIFT detection (sift.dispatch.cpp / sift.simd.hpp at commit
802cf95; the same rules at tag 4.10.0),
for 8-bit single-channel input, default parameters. Used by _figs.py for Figure 12 and to hold the
article's OpenCV predictions; nothing here imports OpenCV and nothing here was checked against it. Transcribed rules:
 - createInitialImage: float copy, doubled (firstOctave = -1), then GaussianBlur(sig_diff)
   with sig_diff = sqrt(max(sigma^2 - (0.5*2)^2, 0.01)); doubling by resize INTER_LINEAR
   (half-pixel mapping, clamped) unless enable_precise_upscale, which samples src(x/2, y/2)
   bilinearly with BORDER_REFLECT.
 - GaussianBlur: ksize = cvRound(8 sigma + 1) | 1 for float images, sampled normalised kernel,
   separable, BORDER_REFLECT_101.
 - pyramid: incremental sigmas, new octave = INTER_NEAREST halving of layer nOctaveLayers.
 - extrema: |v| > floor(0.5*0.04/3*255) = 1, non-strict 26-neighbour test, 5-pixel border.
 - adjustLocalExtrema, contrast |D(x)|*3 < 0.04 rejects, edge det<=0 or 10 tr^2 >= 121 det rejects.
 - calcOrientationHist: radius cvRound(4.5 s), weight sigma 1.5 s, 36 bins, [1 4 6 4 1]/16
   smoothing, peaks >= 0.8 max, parabolic interpolation, angle = 360 - 10*bin.
"""
import math, sys

def cvRound(x):
    return int(round(x))   # banker's rounding, as lrint in the default FP mode

def gauss_kernel(sigma):
    ksize = cvRound(sigma * 8 + 1) | 1
    r = (ksize - 1) // 2
    w = [math.exp(-(i * i) / (2 * sigma * sigma)) for i in range(-r, r + 1)]
    s = sum(w)
    return [v / s for v in w], r

def refl101(i, n):
    if n == 1:
        return 0
    period = 2 * (n - 1)
    i %= period
    return i if i < n else period - i

def gblur(img, sigma):
    k, r = gauss_kernel(sigma)
    H, W = len(img), len(img[0])
    tmp = [[sum(k[j + r] * row[refl101(x + j, W)] for j in range(-r, r + 1)) for x in range(W)] for row in img]
    return [[sum(k[j + r] * tmp[refl101(y + j, H)][x] for j in range(-r, r + 1)) for x in range(W)] for y in range(H)]

def lin_coeffs_resize(n_src, n_dst):
    # OpenCV resize INTER_LINEAR generic path: fx = (dx+0.5)*scale - 0.5, clamp at both ends
    scale = n_src / n_dst
    out = []
    for dx in range(n_dst):
        fx = (dx + 0.5) * scale - 0.5
        sx = math.floor(fx); fx -= sx
        if sx < 0:
            fx, sx = 0.0, 0
        if sx >= n_src - 1:
            fx, sx = 0.0, n_src - 1
        out.append((sx, min(sx + 1, n_src - 1), fx))
    return out

def lin_coeffs_precise(n_src, n_dst):
    # warpAffine with inverse map x_src = x_dst / 2, bilinear, BORDER_REFLECT (n -> n-1)
    out = []
    for dx in range(n_dst):
        fx = dx * 0.5
        sx = math.floor(fx); f = fx - sx
        s1 = sx + 1
        if s1 >= n_src:
            s1 = 2 * n_src - 1 - s1
        out.append((sx, s1, f))
    return out

def double(img, precise):
    H, W = len(img), len(img[0])
    cx = (lin_coeffs_precise if precise else lin_coeffs_resize)(W, 2 * W)
    cy = (lin_coeffs_precise if precise else lin_coeffs_resize)(H, 2 * H)
    tmp = [[(1 - f) * row[a] + f * row[b] for (a, b, f) in cx] for row in img]
    return [[(1 - f) * tmp[a][x] + f * tmp[b][x] for x in range(2 * W)] for (a, b, f) in cy]

def halve_nearest(img):
    H, W = len(img), len(img[0])
    return [[img[2 * y][2 * x] for x in range(W // 2)] for y in range(H // 2)]

def sift_detect(img8, precise=False, nOctaveLayers=3, contrastThreshold=0.04, edgeThreshold=10.0, sigma=1.6, verbose=False):
    BORDER, MAXSTEPS = 5, 5
    img = [[float(v) for v in row] for row in img8]
    sig_diff = math.sqrt(max(sigma * sigma - 0.5 * 0.5 * 4, 0.01))
    base = gblur(double(img, precise), sig_diff)
    nOct = cvRound(math.log(min(len(base), len(base[0]))) / math.log(2.0) - 2) - (-1)
    k = 2.0 ** (1.0 / nOctaveLayers)
    sig = [sigma] + [math.sqrt((k ** i * sigma) ** 2 - (k ** (i - 1) * sigma) ** 2) for i in range(1, nOctaveLayers + 3)]
    gpyr = []
    for o in range(nOct):
        for i in range(nOctaveLayers + 3):
            if o == 0 and i == 0:
                gpyr.append(base)
            elif i == 0:
                gpyr.append(halve_nearest(gpyr[(o - 1) * (nOctaveLayers + 3) + nOctaveLayers]))
            else:
                gpyr.append(gblur(gpyr[-1], sig[i]))
    dog = []
    for o in range(nOct):
        for i in range(nOctaveLayers + 2):
            a = gpyr[o * (nOctaveLayers + 3) + i]; b = gpyr[o * (nOctaveLayers + 3) + i + 1]
            dog.append([[b[y][x] - a[y][x] for x in range(len(a[0]))] for y in range(len(a))])
    threshold = math.floor(0.5 * contrastThreshold / nOctaveLayers * 255)
    img_scale = 1.0 / 255
    kpts, cands = [], []

    def D(o, l, r, c):
        return dog[o * (nOctaveLayers + 2) + l][r][c]

    for o in range(nOct):
        rows, cols = len(gpyr[o * (nOctaveLayers + 3)]), len(gpyr[o * (nOctaveLayers + 3)][0])
        for i in range(1, nOctaveLayers + 1):
            for r in range(BORDER, rows - BORDER):
                for c in range(BORDER, cols - BORDER):
                    v = D(o, i, r, c)
                    if abs(v) <= threshold:
                        continue
                    nb = [D(o, i + di, r + dy, c + dx) for di in (-1, 0, 1) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                          if not (di == 0 and dy == 0 and dx == 0)]
                    ok = (v > 0 and v >= max(nb)) or (v < 0 and v <= min(nb))
                    if not ok:
                        continue
                    cands.append((o, i, r, c, v))
                    # adjustLocalExtrema
                    layer, rr, cc = i, r, c
                    xi = xr = xc = 0.0
                    step = 0
                    good = True
                    while step < MAXSTEPS:
                        g = [(D(o, layer, rr, cc + 1) - D(o, layer, rr, cc - 1)) * img_scale * 0.5,
                             (D(o, layer, rr + 1, cc) - D(o, layer, rr - 1, cc)) * img_scale * 0.5,
                             (D(o, layer + 1, rr, cc) - D(o, layer - 1, rr, cc)) * img_scale * 0.5]
                        v2 = D(o, layer, rr, cc) * 2
                        dxx = (D(o, layer, rr, cc + 1) + D(o, layer, rr, cc - 1) - v2) * img_scale
                        dyy = (D(o, layer, rr + 1, cc) + D(o, layer, rr - 1, cc) - v2) * img_scale
                        dss = (D(o, layer + 1, rr, cc) + D(o, layer - 1, rr, cc) - v2) * img_scale
                        dxy = (D(o, layer, rr + 1, cc + 1) - D(o, layer, rr + 1, cc - 1) - D(o, layer, rr - 1, cc + 1) + D(o, layer, rr - 1, cc - 1)) * img_scale * 0.25
                        dxs = (D(o, layer + 1, rr, cc + 1) - D(o, layer + 1, rr, cc - 1) - D(o, layer - 1, rr, cc + 1) + D(o, layer - 1, rr, cc - 1)) * img_scale * 0.25
                        dys = (D(o, layer + 1, rr + 1, cc) - D(o, layer + 1, rr - 1, cc) - D(o, layer - 1, rr + 1, cc) + D(o, layer - 1, rr - 1, cc)) * img_scale * 0.25
                        Hm = [[dxx, dxy, dxs], [dxy, dyy, dys], [dxs, dys, dss]]
                        X = solve3(Hm, g)
                        if X is None:
                            good = False; break
                        xi, xr, xc = -X[2], -X[1], -X[0]
                        if abs(xi) < 0.5 and abs(xr) < 0.5 and abs(xc) < 0.5:
                            break
                        cc += cvRound(xc); rr += cvRound(xr); layer += cvRound(xi)
                        if layer < 1 or layer > nOctaveLayers or cc < BORDER or cc >= cols - BORDER or rr < BORDER or rr >= rows - BORDER:
                            good = False; break
                        step += 1
                    if not good or step >= MAXSTEPS:
                        if verbose: print('  rejected in interpolation', (o, i, r, c))
                        continue
                    g = [(D(o, layer, rr, cc + 1) - D(o, layer, rr, cc - 1)) * img_scale * 0.5,
                         (D(o, layer, rr + 1, cc) - D(o, layer, rr - 1, cc)) * img_scale * 0.5,
                         (D(o, layer + 1, rr, cc) - D(o, layer - 1, rr, cc)) * img_scale * 0.5]
                    contr = D(o, layer, rr, cc) * img_scale + 0.5 * (g[0] * xc + g[1] * xr + g[2] * xi)
                    if abs(contr) * nOctaveLayers < contrastThreshold:
                        if verbose: print('  rejected contrast', (o, i, r, c), contr)
                        continue
                    v2 = D(o, layer, rr, cc) * 2
                    dxx = (D(o, layer, rr, cc + 1) + D(o, layer, rr, cc - 1) - v2) * img_scale
                    dyy = (D(o, layer, rr + 1, cc) + D(o, layer, rr - 1, cc) - v2) * img_scale
                    dxy = (D(o, layer, rr + 1, cc + 1) - D(o, layer, rr + 1, cc - 1) - D(o, layer, rr - 1, cc + 1) + D(o, layer, rr - 1, cc - 1)) * img_scale * 0.25
                    tr = dxx + dyy; det = dxx * dyy - dxy * dxy
                    if det <= 0 or tr * tr * edgeThreshold >= (edgeThreshold + 1) ** 2 * det:
                        if verbose: print('  rejected edge', (o, i, r, c), 'tr2/det', (tr * tr / det if det > 0 else None))
                        continue
                    size = sigma * 2 ** ((layer + xi) / nOctaveLayers) * (1 << o) * 2
                    pt = ((cc + xc) * (1 << o), (rr + xr) * (1 << o))
                    scl_octv = size * 0.5 / (1 << o)
                    hist = orient_hist(gpyr[o * (nOctaveLayers + 3) + layer], cc, rr, cvRound(4.5 * scl_octv), 1.5 * scl_octv)
                    omax = max(hist)
                    n = 36
                    for j in range(n):
                        l = j - 1 if j > 0 else n - 1
                        r2 = j + 1 if j < n - 1 else 0
                        if hist[j] > hist[l] and hist[j] > hist[r2] and hist[j] >= omax * 0.8:
                            b = j + 0.5 * (hist[l] - hist[r2]) / (hist[l] - 2 * hist[j] + hist[r2])
                            b = n + b if b < 0 else (b - n if b >= n else b)
                            ang = 360.0 - (360.0 / n) * b
                            if abs(ang - 360.0) < 1.1920929e-07:
                                ang = 0.0
                            kpts.append(dict(o=o, layer=layer, r=rr, c=cc, xi=xi, xr=xr, xc=xc, pt=pt, size=size,
                                             angle=ang, response=abs(contr), hist=hist))
    # firstOctave = -1 rescale
    for kp in kpts:
        kp['pt'] = (kp['pt'][0] * 0.5, kp['pt'][1] * 0.5)
        kp['size'] *= 0.5
    return kpts, cands, dict(nOct=nOct, sizes=[len(gpyr[o * (nOctaveLayers + 3)]) for o in range(nOct)], sig=sig, sig_diff=sig_diff)

def solve3(H, g):
    def det3(M):
        return (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0])
                + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0]))
    d = det3(H)
    if d == 0:                       # Matx_FastSolveOp<3,3,1> fails only on an exact zero;
        return [0.0, 0.0, 0.0]       # Matx::solve then returns zeros (operations.hpp)
    out = []
    for col in range(3):
        M = [row[:] for row in H]
        for r in range(3):
            M[r][col] = g[r]
        out.append(det3(M) / d)
    return out

def orient_hist(img, cx, cy, radius, sigma):
    n = 36
    expf = -1.0 / (2.0 * sigma * sigma)
    rows, cols = len(img), len(img[0])
    temp = [0.0] * n
    for i in range(-radius, radius + 1):
        y = cy + i
        if y <= 0 or y >= rows - 1:
            continue
        for j in range(-radius, radius + 1):
            x = cx + j
            if x <= 0 or x >= cols - 1:
                continue
            dx = img[y][x + 1] - img[y][x - 1]
            dy = img[y - 1][x] - img[y + 1][x]
            w = math.exp((i * i + j * j) * expf)
            ori = math.degrees(math.atan2(dy, dx)) % 360.0
            mag = math.hypot(dx, dy)
            b = cvRound(n / 360.0 * ori)
            if b >= n: b -= n
            if b < 0: b += n
            temp[b] += w * mag
    hist = [(temp[(i - 2) % n] + temp[(i + 2) % n]) / 16 + (temp[(i - 1) % n] + temp[(i + 1) % n]) * 4 / 16 + temp[i] * 6 / 16 for i in range(n)]
    return hist

def patch(m):
    N = 5 * m
    img = [[40 if x < 3 * m else 200 for x in range(N)] for y in range(N)]
    for y in range(2 * m, 3 * m):
        for x in range(m, 2 * m):
            img[y][x] = 255
    return img
