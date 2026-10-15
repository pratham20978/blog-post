#!/usr/bin/env python3
"""Every number in colour-and-gamma, computed in plain Python and asserted against the article.

Nothing loads an image and no imaging library runs. The sRGB curve, the matrices, CIELAB and the luma
weights are typed from the standards and from the libraries' source (ledger keys in the comments). The
two CIE tables (_cie_*.csv, S9 and S10) are the CIE's own CSVs, read as text.

Importing this module is quick, so the figure scripts can use it. Running it (`python3 _data.py`) also
sweeps all 2^24 8-bit colours (about a minute) and checks that SWEEP, the sweep results the article and
figures print, still holds.
"""
import csv
import math
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent


def close(a, b, tol):
    return abs(a - b) <= tol


# ------------------------------------------------------------------ the sRGB curve (L02, L04)
T_DEC, T_ENC, SLOPE, OFF, EXP = 0.04045, 0.0031308, 12.92, 0.055, 2.4   # IEC, as S5/S20/S23 restate it
T_DEC_1996, T_ENC_1996 = 0.03928, 0.00304                               # the 1996 proposal (S2, S3)


def decode(v):
    """Normalised code v in [0, 1] -> linear light."""
    return v / SLOPE if v <= T_DEC else ((v + OFF) / (1 + OFF)) ** EXP


def encode(L):
    """Linear light L in [0, 1] -> normalised code."""
    return L * SLOPE if L <= T_ENC else (1 + OFF) * L ** (1 / EXP) - OFF


def dec8(c):
    return decode(c / 255)


def enc8(L):
    return 255 * encode(L)


DEC = [dec8(c) for c in range(256)]

# ------------------------------------------------------------------ CIELAB (L23: the CIE's fractions)
EPS, KAPPA = 216 / 24389, 24389 / 27


def f_lab(t):
    return t ** (1 / 3) if t > EPS else (KAPPA * t + 16) / 116


def lstar(Y):
    return 116 * f_lab(Y) - 16


def lab(XYZ, W):
    fx, fy, fz = (f_lab(XYZ[i] / W[i]) for i in range(3))
    return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))


def matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(3)) for i in range(3)]


# ------------------------------------------------------------------ matrices and whites
M4 = [[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]          # L42 (S3 eq. 1.8)
W4 = [sum(r) for r in M4]                                                                    # (0.9505, 1, 1.0890)
M_CSS = [[506752 / 1228815, 87881 / 245763, 12673 / 70218],                                  # L42 (S5 §19)
         [87098 / 409605, 175762 / 245763, 12673 / 175545],
         [7918 / 409605, 87881 / 737289, 1001167 / 1053270]]
M_CV = [[0.412453, 0.357580, 0.180423], [0.212671, 0.715160, 0.072169], [0.019334, 0.119193, 0.950227]]  # L29, L26, L34
W_CV = (0.950456, 1.0, 1.088754)                                                             # L30
W_SK65 = (0.95047, 1.0, 1.08883)                                                             # L34
W_SK50 = (0.9642119944211994, 1.0, 0.8251882845188288)                                       # L34 (no adaptation)
D50_CSS = (0.3457 / 0.3585, 1.0, (1 - 0.3457 - 0.3585) / 0.3585)                             # L24
D65_CSS = (0.3127 / 0.3290, 1.0, (1 - 0.3127 - 0.3290) / 0.3290)
BRADFORD_65_50 = [[1.0479297925449969, 0.022946870601609652, -0.05019226628920524],          # L24 (S5 §19)
                  [0.02962780877005599, 0.9904344267538799, -0.017073799063418826],
                  [-0.009243040646204504, 0.015055191490298152, 0.7518742814281371]]
assert close(W4[0], 0.9505, 1e-9) and close(W4[2], 1.0890, 1e-9) and close(W4[1], 1.0, 1e-9)

# ------------------------------------------------------------------ step 1: three codes, and the rulers
PATCH_LEVELS = (40, 200, 255)
LIN = {c: dec8(c) for c in (0, 10, 40, 118, 119, 128, 188, 200, 255)}
assert f"{LIN[40]:.6f}" == "0.021219" and f"{LIN[200]:.6f}" == "0.577580" and LIN[255] == 1.0
assert f"{LIN[128]:.6f}" == "0.215861" and f"{LIN[118]:.6f}" == "0.181164"
assert f"{LIN[40]:.4f}" == "0.0212" and f"{LIN[200]:.4f}" == "0.5776" and f"{100 * LIN[128]:.1f}" == "21.6"
LSTAR = {c: lstar(LIN[c]) for c in LIN}
assert [f"{LSTAR[c]:.1f}" for c in (40, 118, 119, 128, 200)] == ["16.1", "49.6", "50.0", "53.6", "80.6"]
assert f"{enc8(0.5):.1f}" == "187.5" and f"{lstar(0.5):.1f}" == "76.1"      # half of white's light
Y_MID = ((50 + 16) / 116) ** 3                           # L* 50
assert f"{Y_MID:.4f}" == "0.1842" and f"{enc8(Y_MID):.1f}" == "118.9" and f"{255 * Y_MID:.1f}" == "47.0"
POW22_10 = (10 / 255) ** 2.2                             # a plain 2.2 power at code 10
assert f"{LIN[10]:.4f}" == "0.0030" and f"{POW22_10:.4f}" == "0.0008" and f"{LIN[10] / POW22_10:.1f}" == "3.8"
RULER_CODES = (40, 119, 128, 200, 255)                   # Figure 1's marked codes

# ------------------------------------------------------------------ steps 2-4: the azure (40, 200, 255)
AZURE = (40, 200, 255)
AZ_LIN = [dec8(c) for c in AZURE]
AZ_XYZ = matvec(M4, AZ_LIN)
assert [f"{v:.4f}" for v in AZ_XYZ] == ["0.3958", "0.4898", "1.0198"]
AZ_RATIO = [AZ_XYZ[i] / W4[i] for i in range(3)]
assert [f"{v:.4f}" for v in AZ_RATIO] == ["0.4164", "0.4898", "0.9364"]
AZ_F = [f_lab(t) for t in AZ_RATIO]
assert [f"{v:.4f}" for v in AZ_F] == ["0.7467", "0.7883", "0.9783"]
AZ_LAB = lab(AZ_XYZ, W4)
assert [f"{v:.2f}" for v in AZ_LAB] == ["75.44", "-20.76", "-38.02"]
assert [f"{v:.1f}" for v in AZ_LAB] == ["75.4", "-20.8", "-38.0"]
assert [f"{v:.2f}" for v in lab(matvec(M_CV, AZ_LIN), W_CV)] == ["75.44", "-20.77", "-38.02"]   # OpenCV's matrix/white
AZ_Y = AZ_XYZ[1]
AZ_LUMGREY = enc8(AZ_Y)
assert f"{AZ_LUMGREY:.1f}" == "185.8" and round(AZ_LUMGREY) == 186 and f"{encode(AZ_Y):.4f}" == "0.7286"


def luma601(r, g, b):
    return 0.299 * r + 0.587 * g + 0.114 * b             # L15, L27, L36, L39


def cv_gray8(r, g, b):
    """OpenCV's 8-bit BGR2GRAY: 15-bit weights, rounded (L27)."""
    return (b * 3735 + g * 19235 + r * 9798 + (1 << 14)) >> 15


def pil_l(r, g, b):
    """Pillow's convert('L'): 16-bit weights, rounded (L36)."""
    return (r * 19595 + g * 38470 + b * 7471 + 0x8000) >> 16


AZ_LUMA = luma601(*AZURE)
assert f"{AZ_LUMA:.2f}" == "158.43" and cv_gray8(*AZURE) == 158 and pil_l(*AZURE) == 158
AZ_MATLAB = 0.298936021293775 * 40 + 0.587043074451121 * 200 + 0.114020904255103 * 255   # L37
assert f"{AZ_MATLAB:.2f}" == "158.44"
AZ_SK_GRAY = (0.2125 * 40 + 0.7154 * 200 + 0.0721 * 255) / 255                            # L33
assert f"{AZ_SK_GRAY:.4f}" == "0.6665" and f"{255 * AZ_SK_GRAY:.1f}" == "170.0"
AZ_SK_Y = matvec(M_CV, AZ_LIN)[1]                                                          # L34: rgb2xyz decodes
assert f"{AZ_SK_Y:.4f}" == "0.4897"
AZ_CV_XYZ_Y8 = (871 * 40 + 2929 * 200 + 296 * 255 + 2048) >> 12                           # L43
AZ_CV_XYZ_YF = 0.212671 * 40 / 255 + 0.715160 * 200 / 255 + 0.072169                       # L29, float input
assert AZ_CV_XYZ_Y8 == 170 and f"{AZ_CV_XYZ_YF:.4f}" == "0.6664"
AZ_LUMA_Y = dec8(AZ_LUMA)                                                                  # the luma grey's light
assert f"{AZ_LUMA_Y:.3f}" == "0.344" and f"{lstar(AZ_LUMA_Y):.1f}" == "65.3"
assert f"{AZ_LAB[0] - lstar(AZ_LUMA_Y):.1f}" == "10.2"
AZ_LAB8 = (AZ_LAB[0] * 255 / 100, AZ_LAB[1] + 128, AZ_LAB[2] + 128)                        # L30, documented scaling
assert [round(v) for v in AZ_LAB8] == [192, 107, 90]
# Lab under other whites (Figure 7)
AZ_LAB_D50 = lab(matvec(BRADFORD_65_50, matvec(M_CSS, AZ_LIN)), D50_CSS)                   # CSS lab()
AZ_LAB_D65_CSS = lab(matvec(M_CSS, AZ_LIN), D65_CSS)
AZ_LAB_SK50 = lab(matvec(M_CV, AZ_LIN), W_SK50)                                            # skimage illuminant="D50"
WHITE_LAB_SK50 = lab(matvec(M_CV, [1.0, 1.0, 1.0]), W_SK50)
WHITE_LAB_D50 = lab(matvec(BRADFORD_65_50, matvec(M_CSS, [1.0, 1.0, 1.0])), D50_CSS)
assert [f"{v:.1f}" for v in AZ_LAB_D50] == ["74.8", "-26.4", "-39.0"]
assert [f"{v:.1f}" for v in AZ_LAB_D65_CSS] == ["75.4", "-20.8", "-38.0"]
assert [f"{v:.1f}" for v in AZ_LAB_SK50] == ["75.4", "-22.6", "-57.0"]
assert [f"{v:.1f}" for v in WHITE_LAB_SK50] == ["100.0", "-2.4", "-19.4"]
assert all(abs(v) < 0.01 for v in WHITE_LAB_D50[1:]) and close(WHITE_LAB_D50[0], 100, 0.01)
DE_65_50 = math.dist(AZ_LAB_D65_CSS, AZ_LAB_D50)
assert f"{DE_65_50:.1f}" == "5.8"

# ------------------------------------------------------------------ step 5: one blur in two encodings
W_SIDE = math.exp(-1 / (2 * 0.8 ** 2))
GAUSS = (W_SIDE / (1 + 2 * W_SIDE), 1 / (1 + 2 * W_SIDE), W_SIDE / (1 + 2 * W_SIDE))
assert [f"{w:.3f}" for w in GAUSS] == ["0.239", "0.522", "0.239"]
STEP_ROW = [40, 40, 40, 200, 200]                         # row r0 of the patch: no impulse within reach


def blur_row(vals):
    """The 3-tap Gaussian along a row, reflect-101 at the ends (both ends are flat here)."""
    n = len(vals)
    pad = [vals[1]] + list(vals) + [vals[n - 2]]
    return [GAUSS[0] * pad[j] + GAUSS[1] * pad[j + 1] + GAUSS[2] * pad[j + 2] for j in range(n)]


BLUR_CODES = blur_row(STEP_ROW)
BLUR_LIGHT = blur_row([dec8(c) for c in STEP_ROW])         # in linear light
BLUR_LIGHT_AS_CODES = [enc8(L) for L in BLUR_LIGHT]
BLUR_CODES_AS_LIGHT = [dec8(c) for c in BLUR_CODES]
assert [f"{v:.1f}" for v in BLUR_CODES] == ["40.0", "40.0", "78.2", "161.8", "200.0"]
assert [f"{v:.1f}" for v in BLUR_LIGHT_AS_CODES] == ["40.0", "40.0", "109.4", "177.9", "200.0"]
assert [f"{v:.4f}" for v in BLUR_LIGHT] == ["0.0212", "0.0212", "0.1542", "0.4446", "0.5776"]
assert [f"{v:.4f}" for v in BLUR_CODES_AS_LIGHT] == ["0.0212", "0.0212", "0.0767", "0.3601", "0.5776"]
assert all(a >= b - 1e-9 for a, b in zip(BLUR_LIGHT_AS_CODES, BLUR_CODES))                # Jensen, on the row
MID_CODES = (40 + 200) / 2
MID_LIGHT = (LIN[40] + LIN[200]) / 2
assert MID_CODES == 120 and f"{enc8(MID_LIGHT):.1f}" == "148.7" and f"{MID_LIGHT:.4f}" == "0.2994"
assert f"{dec8(MID_CODES):.3f}" == "0.188"                 # what code 120 actually emits
# the impulse, Part 1's two answers redone in light (L40)
C2D = GAUSS[1] ** 2
IMP_G_CODES = C2D * 255 + (1 - C2D) * 40
IMP_G_LIGHT = enc8(C2D * 1.0 + (1 - C2D) * LIN[40])
IMP_BOX_CODES = (8 * 40 + 255) / 9
IMP_BOX_LIGHT = enc8((8 * LIN[40] + 1.0) / 9)
assert f"{IMP_G_CODES:.1f}" == "98.6" and f"{IMP_G_LIGHT:.1f}" == "146.1"
assert round(IMP_BOX_CODES) == 64 and round(IMP_BOX_LIGHT) == 101
# stripes of 0 and 255, averaged in pairs
STRIPE_CODES = 127.5
STRIPE_CODES_LIGHT = decode(STRIPE_CODES / 255)
STRIPE_LIGHT_CODE = enc8(0.5)
assert f"{100 * STRIPE_CODES_LIGHT:.1f}" == "21.4" and f"{STRIPE_LIGHT_CODE:.1f}" == "187.5"

# ------------------------------------------------------------------ the encoding budget (Figure 4)
L_SRGB = [lstar(DEC[c]) for c in range(256)]
L_LIN = [lstar(c / 255) for c in range(256)]


def bands(Ls):
    out = [0] * 10
    for v in Ls:
        out[min(int(v // 10), 9)] += 1
    return out


BANDS_SRGB, BANDS_LIN = bands(L_SRGB), bands(L_LIN)
assert BANDS_SRGB == [28, 21, 22, 24, 24, 26, 27, 27, 28, 29]
assert BANDS_LIN == [3, 5, 8, 13, 18, 25, 32, 41, 50, 61]
STEPS_SRGB = [L_SRGB[c + 1] - L_SRGB[c] for c in range(255)]
STEPS_LIN = [L_LIN[c + 1] - L_LIN[c] for c in range(255)]
assert f"{max(STEPS_SRGB):.2f}" == "0.51" and STEPS_SRGB.index(max(STEPS_SRGB)) == 24
assert f"{max(STEPS_LIN):.2f}" == "3.54" and STEPS_LIN.index(max(STEPS_LIN)) == 0
assert sum(s > 1 for s in STEPS_LIN) == 15 and sum(s > 2.3 for s in STEPS_LIN) == 4 and sum(s > 1 for s in STEPS_SRGB) == 0

# ------------------------------------------------------------------ the two thresholds (our geometry, not the IEC's reasoning)
U_T = OFF / ((1 + OFF) * (1 - 1 / EXP))
L_TANGENT = U_T ** EXP
V_TANGENT = (1 + OFF) / EXP * U_T
SLOPE_TANGENT = V_TANGENT / L_TANGENT
assert f"{L_TANGENT:.5f}" == "0.00304" and f"{V_TANGENT:.5f}" == "0.03929" and f"{SLOPE_TANGENT:.4f}" == "12.9232"
assert close(V_TANGENT, OFF / (EXP - 1), 1e-15)            # the tangent's code is exactly 0.055/1.4 = 0.0392857...
assert f"{V_TANGENT:.7f}" == "0.0392857" and str(T_DEC_1996) == "0.03928"   # the proposal printed it truncated
assert f"{L_TANGENT:.7f}" == "0.0030399"


def _gap(L):
    return (1 + OFF) * L ** (1 / EXP) - OFF - SLOPE * L


def _bisect(a, b):
    for _ in range(200):
        m = (a + b) / 2
        if _gap(a) * _gap(m) <= 0:
            b = m
        else:
            a = m
    return (a + b) / 2


CROSS_LO, CROSS_HI = _bisect(0.0025, L_TANGENT), _bisect(L_TANGENT, 0.004)
assert f"{SLOPE * CROSS_LO:.5f}" == "0.03815" and f"{SLOPE * CROSS_HI:.5f}" == "0.04045"
assert f"{CROSS_HI:.7f}" == "0.0031307"
assert [c for c in range(256) if T_DEC_1996 < c / 255 <= T_DEC] == []
assert sum(1 for c in range(65536) if T_DEC_1996 < c / 65535 <= T_DEC) == 76
assert f"{10 / 255:.4f}" == "0.0392" and f"{11 / 255:.4f}" == "0.0431"
# the curve bends down everywhere: second differences on a fine grid (the pieces meet within 1e-7)
_g = [encode(k / 200000) for k in range(200001)]
assert max(_g[k - 1] - 2 * _g[k] + _g[k + 1] for k in range(1, 200000)) < 1e-7
assert abs(SLOPE * T_ENC - encode(T_ENC + 1e-15)) < 1e-6

# ------------------------------------------------------------------ luma against the luminance grey (Figure 6)
LUM = (0.2126, 0.7152, 0.0722)                            # L13, L42


def lum_grey(r, g, b):
    return enc8(LUM[0] * DEC[r] + LUM[1] * DEC[g] + LUM[2] * DEC[b])


SWATCHES = [("red", (255, 0, 0)), ("green", (0, 255, 0)), ("blue", (0, 0, 255)), ("yellow", (255, 255, 0)),
            ("cyan", (0, 255, 255)), ("magenta", (255, 0, 255)), ("azure", AZURE), ("pink", (255, 172, 255)),
            ("grey", (128, 128, 128))]
GREYS = {name: (luma601(*t), lum_grey(*t)) for name, t in SWATCHES}
assert [f"{GREYS[n][0]:.1f}/{GREYS[n][1]:.1f}" for n, _ in SWATCHES] == [
    "76.2/127.1", "149.7/219.9", "29.1/76.0", "225.9/246.7", "178.8/229.5", "105.3/145.4",
    "158.4/185.8", "206.3/200.4", "128.0/128.0"]
assert cv_gray8(0, 255, 0) == 150 and cv_gray8(255, 172, 255) == 206 and round(lum_grey(255, 172, 255)) == 200
GREEN_L = (lstar(DEC[255] * LUM[1]), lstar(dec8(luma601(0, 255, 0))))
assert f"{GREEN_L[0]:.1f}" == "87.7" and f"{GREEN_L[1]:.1f}" == "62.0" and f"{GREEN_L[0] - GREEN_L[1]:.1f}" == "25.8"
assert f"{luma601(0, 255, 0) - lum_grey(0, 255, 0):.1f}" == "-70.2" and f"{luma601(255, 172, 255) - lum_grey(255, 172, 255):.1f}" == "5.9"
assert f"{AZ_LUMGREY - AZ_LUMA:.1f}" == "27.4" and round(AZ_LUMGREY) - round(AZ_LUMA) == 28
assert f"{min(STEPS_LIN):.2f}" == "0.15"

# ------------------------------------------------------------------ weights from primaries (Figure 5; L03, L16, L17, L19)


def solve3(A, b):
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for i in range(3):
        p = max(range(i, 3), key=lambda r: abs(M[r][i]))
        M[i], M[p] = M[p], M[i]
        for r in range(3):
            if r != i:
                fct = M[r][i] / M[i][i]
                M[r] = [M[r][k] - fct * M[i][k] for k in range(4)]
    return [M[i][3] / M[i][i] for i in range(3)]


def rgb_to_xyz(prims, white):
    cols = [[x / y, 1.0, (1 - x - y) / y] for (x, y) in prims]
    A = [[cols[j][i] for j in range(3)] for i in range(3)]
    Wt = [white[0] / white[1], 1.0, (1 - white[0] - white[1]) / white[1]]
    s = solve3(A, Wt)
    return [[A[i][j] * s[j] for j in range(3)] for i in range(3)]


P709 = [(0.64, 0.33), (0.30, 0.60), (0.15, 0.06)]
P_NTSC = [(0.67, 0.33), (0.21, 0.71), (0.14, 0.08)]
P601_625 = [(0.640, 0.330), (0.290, 0.600), (0.150, 0.060)]
P601_525 = [(0.630, 0.340), (0.310, 0.595), (0.155, 0.070)]
WP_D65, WP_C_CIE, WP_C_470 = (0.3127, 0.3290), (0.31006, 0.31617), (0.310, 0.316)
ROW_709 = rgb_to_xyz(P709, WP_D65)[1]
ROW_NTSC = rgb_to_xyz(P_NTSC, WP_C_CIE)[1]
ROW_NTSC_470 = rgb_to_xyz(P_NTSC, WP_C_470)[1]
ROW_625 = rgb_to_xyz(P601_625, WP_D65)[1]
ROW_525 = rgb_to_xyz(P601_525, WP_D65)[1]
assert [f"{v:.6f}" for v in ROW_709] == ["0.212639", "0.715169", "0.072192"]
assert [f"{v:.4f}" for v in ROW_709] == ["0.2126", "0.7152", "0.0722"]
assert all(close(ROW_709[i], M_CSS[1][i], 5e-7) for i in range(3))
assert [f"{v:.4f}" for v in ROW_NTSC] == ["0.2989", "0.5866", "0.1145"]
assert [f"{v:.3f}" for v in ROW_NTSC] == ["0.299", "0.587", "0.114"]
assert [f"{v:.4f}" for v in ROW_NTSC_470] == ["0.2990", "0.5864", "0.1146"]
assert [f"{v:.3f}" for v in ROW_625] == ["0.222", "0.707", "0.071"]
assert [f"{v:.3f}" for v in ROW_525] == ["0.212", "0.701", "0.087"]

# ------------------------------------------------------------------ the CIE tables (Figure 5; L20)


def _read(name, ncol):
    rows = {}
    for r in csv.reader(open(HERE / name, encoding="utf-8")):
        if r and r[0].strip():
            rows[int(float(r[0]))] = [float(x) for x in r[1:1 + ncol]]
    return rows


CMF = _read("_cie_xyz_1931_2deg.csv", 3)
VLAMBDA = _read("_cie_sle_photopic.csv", 1)
assert sorted(CMF) == sorted(VLAMBDA) == list(range(360, 831))
assert all(CMF[w][1] == VLAMBDA[w][0] for w in CMF)          # ybar is V(lambda), at all 471 wavelengths
LOCUS = [(w, CMF[w][0] / sum(CMF[w]), CMF[w][1] / sum(CMF[w])) for w in range(380, 701)]

# ------------------------------------------------------------------ the all-colour sweeps (run as a script)
SWEEP = {
    "luma601_minus_lumgrey_min": (-70.25, (0, 255, 0)),
    "luma601_minus_lumgrey_max": (5.93, (255, 172, 255)),
    "luma709_minus_lumgrey_max": 0.0,
    "cv_vs_pillow_disagree": 21745,
    "cv_vs_pillow_first": (0, 1, 201),
    "colours": 16777216,
}


def sweep():
    lo, hi, hi709, n_dis, first = (1e9, None), (-1e9, None), -1e9, 0, None
    for r in range(256):
        dr = DEC[r]
        for g in range(256):
            dg = DEC[g]
            for b in range(256):
                lg = enc8(LUM[0] * dr + LUM[1] * dg + LUM[2] * DEC[b])
                d601 = 0.299 * r + 0.587 * g + 0.114 * b - lg
                if d601 < lo[0]:
                    lo = (d601, (r, g, b))
                if d601 > hi[0]:
                    hi = (d601, (r, g, b))
                d709 = LUM[0] * r + LUM[1] * g + LUM[2] * b - lg
                if d709 > hi709:
                    hi709 = d709
                if cv_gray8(r, g, b) != pil_l(r, g, b):
                    n_dis += 1
                    if first is None:
                        first = (r, g, b)
    return {
        "luma601_minus_lumgrey_min": (round(lo[0], 2), lo[1]),
        "luma601_minus_lumgrey_max": (round(hi[0], 2), hi[1]),
        "luma709_minus_lumgrey_max": round(hi709, 6) + 0.0,
        "cv_vs_pillow_disagree": n_dis,
        "cv_vs_pillow_first": first,
        "colours": 256 ** 3,
    }


if __name__ == "__main__":
    got = sweep()
    for k in SWEEP:
        assert got[k] == SWEEP[k], (k, got[k], SWEEP[k])
    print("all asserts hold, including the sweep over", got["colours"], "colours")
    print("azure: lin", [round(v, 4) for v in AZ_LIN], "XYZ", [round(v, 4) for v in AZ_XYZ], "Lab",
          [round(v, 2) for v in AZ_LAB], "luma", round(AZ_LUMA, 2), "luminance grey", round(AZ_LUMGREY, 2))
    print("sweep:", got)
    sys.exit(0)
