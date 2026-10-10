#!/usr/bin/env python3
"""Figures 01-16 for laplacian-by-hand. Every number here is from the outline table."""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, SANS, SERIF, alabel, box, cell, elbow, emit,
                    eyebrow, elbow_hvh, hline, legend, masked, mono, node, tag,
                    txt, vline)

SER1, SER2, SER3, SER4 = "#7c8f6f", "#5e7a9b", "#b8915a", "#9c6b50"
PATCH = [[40, 40, 40, 200, 200],
         [40, 40, 40, 200, 200],
         [40, 255, 40, 200, 200],
         [40, 40, 40, 200, 200],
         [40, 40, 40, 200, 200]]
CLEAN = [[40, 40, 40, 200, 200]] * 5


# ------------------------------------------------------------------ helpers
def window(x, y, img, r, c, cw=40, hi=None, hi_kind="focal", show_weights=False):
    """3x3 window of img centred on (r, c). hi = (dr, dc) offsets to highlight."""
    s = ""
    W = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            v = img[r + dr][c + dc]
            cx, cy = x + (dc + 1) * cw, y + (dr + 1) * cw
            is_hi = hi is not None and (dr, dc) in hi
            centre = (dr, dc) == (0, 0)
            if is_hi:
                fill, stroke, tcol, wt = ACCENT_TINT, ACCENT, ACCENT, "600"
            elif centre:
                fill, stroke, tcol, wt = "rgba(45,49,66,0.10)", INK, INK, "600"
            elif v == 200:
                fill, stroke, tcol, wt = "rgba(45,49,66,0.05)", "rgba(45,49,66,0.30)", INK, "500"
            else:
                fill, stroke, tcol, wt = "#ffffff", "rgba(45,49,66,0.30)", INK, "500"
            s += cell(cx, cy, cw, cw, v, fill=fill, stroke=stroke, tcolor=tcol, weight=wt)
            if show_weights and W[dr + 1][dc + 1]:
                s += mono(cx + cw - 4, cy + 10, f"×{W[dr + 1][dc + 1]}", size=7, fill=SOFT,
                          anchor="end")
    return s


def stencil(x, y, w, cw=36, hi=None, title=None, fill_neg=False, fmt=str):
    """A square grid of weights. hi: set of (r,c) drawn focal."""
    s = ""
    n = len(w)
    for r in range(n):
        for c in range(n):
            v = w[r][c]
            cx, cy = x + c * cw, y + r * cw
            if hi and (r, c) in hi:
                fill, stroke, tcol, wt = ACCENT_TINT, ACCENT, ACCENT, "600"
            elif fill_neg and v < 0:
                fill, stroke, tcol, wt = "rgba(45,49,66,0.10)", "rgba(45,49,66,0.30)", INK, "600"
            elif v == 0:
                fill, stroke, tcol, wt = "#ffffff", "rgba(45,49,66,0.30)", SOFT, "400"
            else:
                fill, stroke, tcol, wt = "#ffffff", "rgba(45,49,66,0.30)", INK, "500"
            s += cell(cx, cy, cw, cw, fmt(v), fill=fill, stroke=stroke, tcolor=tcol,
                      size=10 if n > 3 else 11, weight=wt)
    if title:
        s += mono(x + n * cw / 2, y - 10, title, size=8, fill=SOFT, track="0.10em")
    return s


def axes(x0, y0, w, h, xt, yt, xlab, ylab, xfmt=str, yfmt=str, grid=True):
    """Plot frame. xt/yt: list of (value, position 0..1)."""
    s = f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for v, p in yt:
        yy = y0 + h - p * h
        if grid and p > 0:
            s += f'<line x1="{x0}" y1="{yy}" x2="{x0 + w}" y2="{yy}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0 - 8, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
    for v, p in xt:
        xx = x0 + p * w
        s += mono(xx, y0 + h + 16, xfmt(v), size=8, fill=SOFT)
    s += eyebrow(x0 + w, y0 + h + 32, xlab, anchor="end")
    s += eyebrow(x0, y0 - 12, ylab, anchor="start")
    return s


def polyline(pts, stroke, sw=1.2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}/>')


def steps_plot(x0, y0, w, h, vals, vmin, vmax, labels, stroke=INK, fill=None,
               value_fmt=str, hi=None, hi_col=ACCENT, zero=True):
    """Step plot of a 1-D profile: n samples as flat segments."""
    n = len(vals)
    cw = w / n
    s = ""
    def ty(v):
        return y0 + h - (v - vmin) / (vmax - vmin) * h
    if zero and vmin < 0 < vmax:
        s += f'<line x1="{x0}" y1="{ty(0)}" x2="{x0 + w}" y2="{ty(0)}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="3,3"/>'
    for i, v in enumerate(vals):
        if v is None:
            s += mono(x0 + i * cw + cw / 2, ty(0) - 6, "—", size=9, fill=SOFT)
            continue
        colour = hi_col if (hi and i in hi) else stroke
        yy = ty(v)
        if fill:
            top, bot = min(yy, ty(0)), max(yy, ty(0))
            s += (f'<rect x="{x0 + i * cw + 6}" y="{top}" width="{cw - 12}" height="{max(bot - top, 0)}" '
                  f'fill="{colour}" fill-opacity="0.10"/>')
        s += f'<line x1="{x0 + i * cw + 6}" y1="{yy}" x2="{x0 + i * cw + cw - 6}" y2="{yy}" stroke="{colour}" stroke-width="2"/>'
        s += mono(x0 + i * cw + cw / 2, yy - 8 if v >= 0 else yy + 14, value_fmt(v), size=9,
                  fill=colour, weight="500")
    for i, lab in enumerate(labels):
        s += mono(x0 + i * cw + cw / 2, y0 + h + 14, lab, size=8, fill=SOFT)
    return s


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 528
    s = eyebrow(32, 44, "row r2 of the patch, and its two differences")
    x0, w = 200, 640
    labels = ["c0", "c1", "c2", "c3", "c4"]
    # panel 1: profile
    s += txt(32, 96, "the profile", size=12, fill=INK, anchor="start", weight="600")
    s += mono(32, 112, "f", size=9, fill=SOFT, anchor="start")
    s += steps_plot(x0, 72, w, 88, [40, 40, 40, 200, 200], 0, 255, labels, stroke=INK, fill=True)
    # panel 2: first difference (between samples)
    s += txt(32, 236, "first difference", size=12, fill=INK, anchor="start", weight="600")
    s += mono(32, 252, "f[c+1] − f[c]", size=9, fill=SOFT, anchor="start")
    cw = w / 5
    y0, h = 208, 88
    def ty(v, lo=-40, hi=200):
        return y0 + h - (v - lo) / (hi - lo) * h
    s += f'<line x1="{x0}" y1="{ty(0)}" x2="{x0 + w}" y2="{ty(0)}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="3,3"/>'
    for i, v in enumerate([0, 0, 160, 0]):
        cx = x0 + (i + 1) * cw
        s += f'<line x1="{cx - 22}" y1="{ty(v)}" x2="{cx + 22}" y2="{ty(v)}" stroke="{INK}" stroke-width="2"/>'
        if v:
            s += f'<rect x="{cx - 22}" y="{ty(v)}" width="44" height="{ty(0) - ty(v)}" fill="{INK}" fill-opacity="0.10"/>'
        s += mono(cx, ty(v) - 8, str(v), size=9, fill=INK, weight="500")
    s += mono(x0 + 3 * cw, y0 + h + 14, "one peak, on the step", size=8, fill=SOFT, track="0.06em")
    # panel 3: second difference
    s += txt(32, 376, "second difference", size=12, fill=INK, anchor="start", weight="600")
    s += mono(32, 392, "f[c−1] − 2f[c] + f[c+1]", size=9, fill=SOFT, anchor="start")
    s += steps_plot(x0, 344, w, 104, [None, 0, 160, -160, None], -200, 200, labels,
                    stroke=INK, fill=True)
    # zero-crossing marker
    zx = x0 + 3 * cw
    zy = 344 + 52
    s += f'<circle cx="{zx}" cy="{zy}" r="5" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.6"/>'
    s += masked(zx, zy + 30, "zero-crossing at c = 2.5", size=8, fill=ACCENT)
    s += txt(880, 396, "+160 then −160:", size=11, fill=MUTED, anchor="start")
    s += txt(880, 412, "the edge appears twice,", size=11, fill=MUTED, anchor="start")
    s += txt(880, 428, "and the zero sits on it", size=11, fill=MUTED, anchor="start")
    s += legend(480, vw, [("value computed from the patch", INK, "line"),
                          ("the zero-crossing", ACCENT, "dot")])
    return emit("01", "two-signatures", "One edge, two signatures",
                "Row r2 of the patch, its first difference, and its second difference.",
                "the problem", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 420
    s = eyebrow(32, 44, "clean patch — the impulse replaced by 40")
    cw = 44
    # window at (2,2)
    s += mono(96 + 66, 84, "window at (2, 2)", size=9, fill=SOFT, track="0.08em")
    s += window(96, 96, CLEAN, 2, 2, cw=cw, show_weights=True)
    s += txt(96 + 66, 262, "40 + 40 + 40 + 200 = 320", size=11, fill=MUTED, family=MONO)
    s += txt(96 + 66, 280, "320 − 4 × 40 = +160", size=12, fill=INK, family=MONO, weight="600")
    # window at (2,3)
    s += mono(592 + 66, 84, "window at (2, 3)", size=9, fill=SOFT, track="0.08em")
    s += window(592, 96, CLEAN, 2, 3, cw=cw, show_weights=True)
    s += txt(592 + 66, 262, "200 + 200 + 40 + 200 = 640", size=11, fill=MUTED, family=MONO)
    s += txt(592 + 66, 280, "640 − 4 × 200 = −160", size=12, fill=INK, family=MONO, weight="600")
    # the crossing between them
    mx = 412
    s += f'<line x1="{mx}" y1="120" x2="{mx}" y2="304" stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="4,4"/>'
    s += f'<circle cx="{mx}" cy="212" r="6" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.6"/>'
    s += masked(mx, 328, "zero-crossing", size=8, fill=ACCENT)
    s += masked(mx, 344, "between c2 and c3 — the step", size=8, fill=ACCENT)
    s += legend(372, vw, [("centre pixel", INK, "box"), ("bright side (200)", MUTED, "box"),
                          ("the zero-crossing", ACCENT, "dot")])
    return emit("02", "clean-windows", "The clean edge: +160 and −160",
                "The four-neighbour stencil at the two pixels either side of the step.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 440
    s = eyebrow(32, 44, "patch with the impulse — 255 at (2, 1)")
    cw = 44
    cols = [(64, 2, 1, {(0, 0)}, "at the impulse (2, 1)",
             "40 + 40 + 40 + 40 = 160", "160 − 4 × 255 = −860"),
            (392, 2, 2, {(0, -1)}, "at the edge pixel (2, 2)",
             "40 + 40 + 255 + 200 = 535", "535 − 4 × 40 = +375"),
            (720, 1, 2, set(), "one row up, (1, 2)",
             "40 + 40 + 40 + 200 = 320", "320 − 4 × 40 = +160")]
    for x, r, c, hi, title, l1, l2 in cols:
        s += mono(x + 66, 84, title, size=9, fill=SOFT, track="0.08em")
        s += window(x, 96, PATCH, r, c, cw=cw, hi=hi, show_weights=True)
        s += txt(x + 66, 262, l1, size=11, fill=MUTED, family=MONO)
        s += txt(x + 66, 280, l2, size=12, fill=INK, family=MONO, weight="600")
    s += txt(64 + 66, 308, "5.4 × the edge response", size=11, fill=MUTED)
    s += txt(392 + 66, 308, "was 160: a 134% error", size=11, fill=MUTED)
    s += txt(720 + 66, 308, "unchanged: no diagonal weight", size=11, fill=MUTED)
    # note: the impulse is diagonal to (1,2)
    s += (f'<rect x="{720 + 0 * cw}" y="{96 + 2 * cw}" width="{cw}" height="{cw}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="3,3"/>')
    s += legend(392, vw, [("centre pixel", INK, "box"), ("the impulse, 255", ACCENT, "box"),
                          ("impulse outside the stencil", ACCENT, "line")])
    return emit("03", "impulse-windows", "One bad pixel",
                "The same stencil with the 255 present: −860 at the impulse, 375 at the edge, 160 one row up.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 452
    s = eyebrow(32, 44, "the same five products, read two ways")
    cw = 40
    # left: stencil reading at (2,2)
    s += mono(64 + 60, 84, "stencil arithmetic", size=9, fill=SOFT, track="0.08em")
    s += window(64, 96, CLEAN, 2, 2, cw=cw, show_weights=True)
    s += txt(124, 244, "320 − 4 × 40 = 160", size=12, fill=INK, family=MONO, weight="600")
    # arrow to the right reading
    s += hline(232, 296, 156, stroke=MUTED)
    s += alabel(264, 156, "same sum")
    # right: mean minus centre
    s += mono(320 + 60, 84, "neighbour mean − centre", size=9, fill=SOFT, track="0.08em")
    s += window(320, 96, CLEAN, 2, 2, cw=cw, hi={(-1, 0), (1, 0), (0, -1), (0, 1)})
    s += txt(380, 244, "mean 80 − centre 40 = 40", size=12, fill=INK, family=MONO, weight="600")
    s += txt(380, 262, "× 4 = 160", size=12, fill=INK, family=MONO, weight="600")
    # the question
    s += box(600, 104, 352, 104, fill=ACCENT_TINT, stroke=ACCENT, dash="4,4")
    s += txt(776, 140, "how far is this pixel from", size=14, fill=INK, family=SERIF, style="italic")
    s += txt(776, 160, "what its neighbours expect?", size=14, fill=INK, family=SERIF, style="italic")
    s += mono(776, 188, "brighter than expected → negative", size=8, fill=MUTED, track="0.06em")
    # bottom: the impulse
    s += mono(320 + 60, 300, "at the impulse", size=9, fill=SOFT, track="0.08em")
    s += window(320, 312, PATCH, 2, 1, cw=cw, hi={(0, 0)})
    s += txt(380 + 200, 360, "mean 40 − centre 255 = −215", size=12, fill=INK, family=MONO, weight="600", anchor="start")
    s += txt(380 + 200, 380, "× 4 = −860", size=12, fill=ACCENT, family=MONO, weight="600", anchor="start")
    s += txt(380 + 200, 404, "flat region: mean = centre → 0", size=11, fill=MUTED, family=MONO, anchor="start")
    s += txt(380 + 200, 420, "ramp: mean = centre → 0", size=11, fill=MUTED, family=MONO, anchor="start")
    return emit("04", "mean-minus-centre", "Neighbour average minus centre",
                "The four-neighbour Laplacian is four times the gap between a pixel and its neighbours' mean.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "five 3×3 second-derivative stencils")
    cw = 36
    items = [
        (40, [[0, 1, 0], [1, -4, 1], [0, 1, 0]], "five-point", "× 1", "160", None, ""),
        (232, [[1, 0, 1], [0, -4, 0], [1, 0, 1]], "diagonal", "× 2", "320", None, ""),
        (424, [[1, 1, 1], [1, -8, 1], [1, 1, 1]], "eight-neighbour", "× 3", "480", None, ""),
        (616, [[2, 0, 2], [0, -8, 0], [2, 0, 2]], "OpenCV ksize=3", "× 4", "640", {(1, 1)}, ""),
        (808, [[1, 4, 1], [4, -20, 4], [1, 4, 1]], "nine-point ÷ 6", "× 1", "160", None, "isotropic"),
    ]
    for x, w, name, mult, val, hi, note in items:
        s += stencil(x, 96, w, cw=cw, hi=hi, fill_neg=True)
        focal = hi is not None
        s += txt(x + 54, 232, name, size=12, fill=ACCENT if focal else INK, weight="600")
        s += mono(x + 54, 252, f"approximates {mult} ∇²", size=9, fill=MUTED)
        s += mono(x + 54, 276, f"at (2,2): {val}", size=9, fill=INK, weight="500")
        if note:
            s += mono(x + 54, 292, note, size=8, fill=SOFT, track="0.10em")
    s += mono(808 + 54, 84, "÷ 6", size=8, fill=SOFT, track="0.08em")
    s += legend(352, vw, [("negative weight", INK, "box"), ("the one OpenCV runs for ksize=3", ACCENT, "box")])
    return emit("05", "five-stencils", "Five Laplacians, four scales",
                "Each stencil applied to x² + y², whose Laplacian is 4, and to the clean edge pixel of the patch.",
                "which discrete laplacian", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 520
    s = eyebrow(32, 44, "model — magnitude of the transfer function, plotted from the closed forms")
    x0, y0, w, h = 96, 80, 760, 320
    s += axes(x0, y0, w, h,
              [(v, v / math.pi) for v in (0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi)],
              [(v, v / 10) for v in (0, 2, 4, 6, 8, 10)],
              "|ω|, radians per pixel", "−H(ω)",
              xfmt=lambda v: {0: "0", math.pi: "π"}.get(v, f"{v / math.pi:.2f}π"))
    def P(f, along):
        pts = []
        for i in range(0, 161):
            om = math.pi * i / 160
            if along == "axis":
                wx, wy = om, 0.0
            else:
                wx = wy = om / math.sqrt(2)
            pts.append((x0 + om / math.pi * w, y0 + h - f(wx, wy) / 10 * h))
        return pts
    cont = lambda wx, wy: wx * wx + wy * wy
    h5 = lambda wx, wy: 4 - 2 * math.cos(wx) - 2 * math.cos(wy)
    h9 = lambda wx, wy: (20 - 8 * math.cos(wx) - 8 * math.cos(wy) - 4 * math.cos(wx) * math.cos(wy)) / 6
    s += polyline(P(cont, "axis"), INK, sw=1.2, dash="5,4")
    s += polyline(P(h5, "axis"), ACCENT, sw=1.8)
    s += polyline(P(h5, "diag"), ACCENT, sw=1.8, dash="2,3")
    s += polyline(P(h9, "axis"), SER2, sw=1.2)
    s += polyline(P(h9, "diag"), SER2, sw=1.2, dash="2,3")
    # end labels
    def yv(v):
        return y0 + h - v / 10 * h
    ex = x0 + w + 8
    s += mono(ex, yv(9.87) + 3, "9.87  continuous", size=8, fill=INK, anchor="start")
    s += mono(ex, yv(6.42) + 3, "6.42  five-point, diagonal", size=8, fill=ACCENT, anchor="start")
    s += mono(ex, yv(4.70) + 3, "4.70  nine-point, diagonal", size=8, fill=SER2, anchor="start")
    s += mono(ex, yv(4.0) + 3, "4.00  both, along the axis", size=8, fill=MUTED, anchor="start")
    s += masked(x0 + 0.5 * w, yv(2.4) - 4, "all four agree below about π/4", size=8, fill=SOFT)
    s += legend(472, vw, [("continuous ω²", INK, "line"), ("five-point stencil", ACCENT, "line"),
                          ("nine-point stencil", SER2, "line"), ("dashed = along the diagonal", MUTED, "line")])
    return emit("06", "transfer-functions", "Axis versus diagonal",
                "A model, not a measurement: how much curvature each stencil reads from a wave of a given frequency.",
                "which discrete laplacian", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 552
    s = eyebrow(32, 44, "row r2, clean patch — the sharpening g = f − ∇²f")
    x0, w = 200, 640
    labels = ["c0", "c1", "c2", "c3", "c4"]
    s += txt(32, 96, "original f", size=12, fill=INK, anchor="start", weight="600")
    s += steps_plot(x0, 72, w, 88, [40, 40, 40, 200, 200], 0, 400, labels, stroke=INK, fill=True)
    s += txt(32, 232, "Laplacian ∇²f", size=12, fill=INK, anchor="start", weight="600")
    s += mono(32, 248, "what blur would remove", size=9, fill=SOFT, anchor="start")
    s += steps_plot(x0, 208, w, 96, [None, 0, 160, -160, None], -200, 200, labels, stroke=MUTED, fill=True)
    s += txt(32, 376, "sharpened g = f − ∇²f", size=12, fill=INK, anchor="start", weight="600")
    s += mono(32, 392, "clipped to 0 … 255", size=9, fill=SOFT, anchor="start")
    y0, h = 344, 128
    def ty(v, lo=-160, hi=400):
        return y0 + h - (v - lo) / (hi - lo) * h
    cw = w / 5
    s += f'<line x1="{x0}" y1="{ty(0)}" x2="{x0 + w}" y2="{ty(0)}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="3,3"/>'
    s += f'<line x1="{x0}" y1="{ty(255)}" x2="{x0 + w}" y2="{ty(255)}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="3,3"/>'
    s += mono(x0 - 8, ty(255) + 3, "255", size=8, fill=SOFT, anchor="end")
    s += mono(x0 - 8, ty(0) + 3, "0", size=8, fill=SOFT, anchor="end")
    raw = [None, 40, -120, 360, None]
    clip = [None, 40, 0, 255, None]
    for i, (rv, cv) in enumerate(zip(raw, clip)):
        cx = x0 + i * cw + cw / 2
        if rv is None:
            s += mono(cx, ty(0) - 6, "—", size=9, fill=SOFT)
            continue
        col = ACCENT if rv != cv else INK
        # raw value as a hollow marker, clipped as the solid segment
        if rv != cv:
            s += f'<line x1="{cx - 22}" y1="{ty(rv)}" x2="{cx + 22}" y2="{ty(rv)}" stroke="{col}" stroke-width="1.2" stroke-dasharray="3,3"/>'
            s += f'<line x1="{cx}" y1="{ty(rv)}" x2="{cx}" y2="{ty(cv)}" stroke="{col}" stroke-width="1" stroke-dasharray="2,3"/>'
            s += mono(cx, ty(rv) - 8 if rv > cv else ty(rv) + 14, f"{rv} → {cv}", size=9, fill=col, weight="500")
        else:
            s += mono(cx, ty(cv) - 8, str(cv), size=9, fill=col, weight="500")
        s += f'<line x1="{cx - 22}" y1="{ty(cv)}" x2="{cx + 22}" y2="{ty(cv)}" stroke="{col}" stroke-width="2"/>'
    for i, lab in enumerate(labels):
        s += mono(x0 + i * cw + cw / 2, y0 + h + 14, lab, size=8, fill=SOFT)
    s += txt(872, 404, "undershoot on the dark side,", size=11, fill=MUTED, anchor="start")
    s += txt(872, 420, "overshoot on the bright side,", size=11, fill=MUTED, anchor="start")
    s += txt(872, 436, "each one stencil wide", size=11, fill=MUTED, anchor="start")
    s += legend(504, vw, [("computed value", INK, "line"), ("clipped by the 8-bit range", ACCENT, "line")])
    return emit("07", "sharpening-halo", "The halo is the Laplacian, sign flipped",
                "Subtracting the Laplacian from the clean row overshoots on both sides of the step.",
                "sharpening", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 500
    s = eyebrow(32, 44, "model — ∇²G at σ = 1 and the difference of Gaussians at ratio 1.6, from the closed forms")
    x0, y0, w, h = 96, 80, 760, 300
    lo, hi = -0.20, 0.06
    def ty(v):
        return y0 + h - (v - lo) / (hi - lo) * h
    def tx(r):
        return x0 + (r + 4) / 8 * w
    s += axes(x0, y0, w, h, [(v, (v + 4) / 8) for v in (-4, -2, 0, 2, 4)],
              [(v, (v - lo) / (hi - lo)) for v in (-0.2, -0.15, -0.1, -0.05, 0, 0.05)],
              "r, in units of σ", "kernel value", xfmt=lambda v: f"{v:g}σ", yfmt=lambda v: f"{v:g}")
    def logk(r):
        return -(1 / math.pi) * (1 - r * r / 2) * math.exp(-r * r / 2)
    def dog(r, k=1.6):
        g = lambda r, s: math.exp(-r * r / (2 * s * s)) / (2 * math.pi * s * s)
        return g(r, k) - g(r, 1.0)
    pts_l, pts_d = [], []
    for i in range(0, 241):
        r = -4 + 8 * i / 240
        pts_l.append((tx(r), ty(0.6 * logk(r))))
        pts_d.append((tx(r), ty(dog(r))))
    s += f'<line x1="{x0}" y1="{ty(0)}" x2="{x0 + w}" y2="{ty(0)}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += polyline(pts_l, ACCENT, sw=1.8)
    s += polyline(pts_d, SER2, sw=1.4, dash="5,4")
    # zero markers
    z = math.sqrt(2)
    s += f'<circle cx="{tx(z)}" cy="{ty(0)}" r="4" fill="{ACCENT}"/>'
    s += f'<circle cx="{tx(-z)}" cy="{ty(0)}" r="4" fill="{ACCENT}"/>'
    s += f'<circle cx="{tx(1.756)}" cy="{ty(0)}" r="4" fill="{PAPER}" stroke="{SER2}" stroke-width="1.4"/>'
    s += f'<circle cx="{tx(-1.756)}" cy="{ty(0)}" r="4" fill="{PAPER}" stroke="{SER2}" stroke-width="1.4"/>'
    # width bracket
    by = ty(0) - 20
    s += f'<line x1="{tx(-z)}" y1="{by}" x2="{tx(z)}" y2="{by}" stroke="{ACCENT}" stroke-width="1"/>'
    s += f'<line x1="{tx(-z)}" y1="{by - 4}" x2="{tx(-z)}" y2="{by + 4}" stroke="{ACCENT}" stroke-width="1"/>'
    s += f'<line x1="{tx(z)}" y1="{by - 4}" x2="{tx(z)}" y2="{by + 4}" stroke="{ACCENT}" stroke-width="1"/>'
    s += masked(tx(0), by - 10, "w = 2√2 σ — the negative disc", size=8, fill=ACCENT)
    s += masked(tx(2.9), ty(-0.17), "DoG zero at 1.76σ, ∇²G zero at 1.41σ", size=8, fill=SER2)
    s += masked(tx(-2.4), ty(-0.19), "centre: −0.191 versus −0.097", size=8, fill=MUTED)
    s += legend(452, vw, [("(k−1) σ² ∇²G, k = 1.6", ACCENT, "line"), ("G(1.6σ) − G(σ)", SER2, "line"),
                          ("zeros", ACCENT, "dot")])
    return emit("08", "mexican-hat-dog", "The Mexican hat and its stand-in",
                "A model, not a measurement: the Laplacian of Gaussian and the difference of Gaussians Marr and Hildreth proposed in its place.",
                "zero-crossings", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 452
    s = eyebrow(32, 44, "∇²₅ ∘ G₃ — the five-point stencil convolved with the 3×3 Gaussian, σ = 0.8")
    K = [[0, 0.0571, 0.1248, 0.0571, 0],
         [0.0571, 0.021, -0.1123, 0.021, 0.0571],
         [0.1248, -0.1123, -0.591, -0.1123, 0.1248],
         [0.0571, 0.021, -0.1123, 0.021, 0.0571],
         [0, 0.0571, 0.1248, 0.0571, 0]]
    cw = 56
    x0, y0 = 96, 80
    for r in range(5):
        for c in range(5):
            v = K[r][c]
            if v < 0:
                fill, stroke, tcol, wt = ACCENT_TINT, ACCENT, ACCENT, "600"
            elif v == 0:
                fill, stroke, tcol, wt = "#ffffff", "rgba(45,49,66,0.30)", SOFT, "400"
            else:
                fill, stroke, tcol, wt = "#ffffff", "rgba(45,49,66,0.30)", INK, "500"
            label = "0" if v == 0 else f"{v:+.4f}".replace("+", "+")
            s += cell(x0 + c * cw, y0 + r * cw, cw, cw, label, fill=fill, stroke=stroke,
                      tcolor=tcol, size=10, weight=wt)
    # radius annotation
    cx, cy = x0 + 2.5 * cw, y0 + 2.5 * cw
    rad = 1.13 * cw
    s += f'<circle cx="{cx}" cy="{cy}" r="{rad}" fill="none" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="4,3"/>'
    # side notes
    nx = 480
    s += txt(nx, 112, "centre −0.591, four neighbours −0.1123:", size=12, fill=INK, anchor="start")
    s += txt(nx, 130, "the negative disc, radius √2 σ = 1.13 px", size=12, fill=INK, anchor="start")
    s += txt(nx, 168, "diagonals at distance 1.41 are already positive", size=12, fill=INK, anchor="start")
    s += txt(nx, 206, "the outer ring is the Gaussian's own weights,", size=12, fill=INK, anchor="start")
    s += txt(nx, 224, "shifted out by one pixel", size=12, fill=INK, anchor="start")
    s += mono(nx, 262, "sum of all 25 weights = 0", size=9, fill=MUTED, anchor="start")
    s += mono(nx, 280, "on the patch at (2,2): 45.3 clean, 21.1 with the impulse", size=9, fill=MUTED, anchor="start")
    s += legend(404, vw, [("negative weight — the disc", ACCENT, "box"), ("positive weight — the ring", INK, "box"),
                          ("r = √2 σ", ACCENT, "line")])
    return emit("09", "log-kernel", "The Mexican hat at σ = 0.8, as numbers",
                "The Laplacian of Gaussian is one kernel; at this σ it fits in 5×5.",
                "zero-crossings", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 560
    s = eyebrow(32, 44, "model — two nearby steps of the same sign, smoothed, and their derivatives")
    x0, w = 200, 640
    def f(x):
        sg = lambda u: 1 / (1 + math.exp(-u))
        return 40 + 80 * sg((x - 3.0) / 0.5) + 80 * sg((x - 6.0) / 0.5)
    def d1(x, e=1e-3):
        return (f(x + e) - f(x - e)) / (2 * e)
    def d2(x, e=1e-3):
        return (d1(x + e) - d1(x - e)) / (2 * e)
    N = 320
    xs = [9 * i / N for i in range(N + 1)]
    def panel(y0, h, g, lo, hi, name, sub, col):
        out = txt(32, y0 + 24, name, size=12, fill=INK, anchor="start", weight="600")
        out += mono(32, y0 + 40, sub, size=9, fill=SOFT, anchor="start")
        ty = lambda v: y0 + h - (v - lo) / (hi - lo) * h
        if lo < 0 < hi:
            out += f'<line x1="{x0}" y1="{ty(0)}" x2="{x0 + w}" y2="{ty(0)}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="3,3"/>'
        out += polyline([(x0 + x / 9 * w, ty(g(x))) for x in xs], col, sw=1.6)
        return out, ty
    p, _ = panel(72, 96, f, 0, 220, "the profile", "two steps, 40 → 120 → 200", INK); s += p
    p, ty1 = panel(200, 96, d1, 0, 60, "first derivative", "two maxima, a minimum between", MUTED); s += p
    p, ty2 = panel(328, 128, d2, -60, 60, "second derivative", "three zero-crossings", INK); s += p
    # locate zeros of d2 numerically
    zeros = []
    prev = d2(xs[0])
    for x in xs[1:]:
        cur = d2(x)
        if prev * cur < 0:
            zeros.append(x)
        prev = cur
    # the middle zero is the phantom (minimum of |f'|)
    for i, z in enumerate(zeros[:3]):
        px = x0 + z / 9 * w
        phantom = i == 1
        col = ACCENT if phantom else INK
        s += f'<line x1="{px}" y1="{ty1(60)}" x2="{px}" y2="{ty2(-60)}" stroke="{col}" stroke-width="0.8" stroke-dasharray="3,3"/>'
        s += f'<circle cx="{px}" cy="{ty2(0)}" r="5" fill="{PAPER}" stroke="{col}" stroke-width="1.6"/>'
        s += masked(px, ty2(-60) + 22, "phantom" if phantom else "authentic", size=8, fill=col)
        s += masked(px, ty1(60) - 8, "min |f′|" if phantom else "max |f′|", size=8, fill=col)
    s += legend(512, vw, [("authentic zero-crossing", INK, "dot"), ("phantom zero-crossing", ACCENT, "dot")])
    return emit("10", "phantom-edges", "Three zeros, two edges",
                "A model profile: every zero of the second derivative is an extremum of the gradient, and only the maxima are edges.",
                "zero-crossings", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 440
    s = eyebrow(32, 44, "a straight edge, and the frame rotated to it")
    # edge: a rotated half-plane inside a square window
    gx, gy, gw = 96, 80, 240
    s += f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gw}" fill="#ffffff" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>'
    ang = -30
    cx, cy = gx + gw / 2, gy + gw / 2
    s += f'<g transform="rotate({ang} {cx} {cy})">'
    s += f'<rect x="{cx}" y="{cy - 200}" width="200" height="400" fill="rgba(45,49,66,0.10)"/>'
    s += f'<line x1="{cx}" y1="{cy - 200}" x2="{cx}" y2="{cy + 200}" stroke="{INK}" stroke-width="1.6"/>'
    # n axis (across), t axis (along)
    s += f'<line x1="{cx}" y1="{cy}" x2="{cx + 88}" y2="{cy}" stroke="{ACCENT}" stroke-width="1.4" marker-end="url(#arrow-accent)"/>'
    s += f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - 88}" stroke="{MUTED}" stroke-width="1.4" marker-end="url(#arrow)"/>'
    s += "</g>"
    # clip the rotated fill to the window: overlay paper outside (simple mask via four rects)
    s += f'<rect x="0" y="0" width="{vw}" height="{gy}" fill="{PAPER}"/>'
    s += f'<rect x="0" y="{gy + gw}" width="{vw}" height="{vh - gy - gw}" fill="{PAPER}"/>'
    s += f'<rect x="0" y="0" width="{gx}" height="{vh}" fill="{PAPER}"/>'
    s += f'<rect x="{gx + gw}" y="0" width="{vw - gx - gw}" height="{vh}" fill="{PAPER}"/>'
    s += f'<rect x="{gx}" y="{gy}" width="{gw}" height="{gw}" fill="none" stroke="rgba(45,49,66,0.30)" stroke-width="0.8"/>'
    s += eyebrow(32, 44, "a straight edge, and the frame rotated to it")
    # axis labels placed in unrotated space
    s += masked(gx + gw + 12, cy - 44, "n — across the edge", size=8, fill=ACCENT, anchor="start")
    s += masked(cx - 96, cy - 96, "t — along the edge", size=8, fill=MUTED)
    s += mono(gx + gw / 2, gy + gw + 20, "dark on the left, bright on the right", size=8, fill=SOFT, track="0.06em")
    # the decomposition
    ex = 420
    s += txt(ex, 124, "∇²f", size=28, fill=INK, family=SERIF, anchor="start")
    s += txt(ex + 64, 124, "=", size=28, fill=MUTED, family=SERIF, anchor="start")
    s += box(ex + 104, 96, 176, 48, fill=ACCENT_TINT, stroke=ACCENT)
    s += txt(ex + 192, 118, "∂²f / ∂n²", size=16, fill=ACCENT, family=SERIF)
    s += mono(ex + 192, 134, "across", size=8, fill=ACCENT, track="0.10em")
    s += txt(ex + 296, 124, "+", size=28, fill=MUTED, family=SERIF, anchor="start")
    s += box(ex + 336, 96, 176, 48, fill="#ffffff", stroke=INK)
    s += txt(ex + 424, 118, "∂²f / ∂t²", size=16, fill=INK, family=SERIF)
    s += mono(ex + 424, 134, "along", size=8, fill=MUTED, track="0.10em")
    # notes under each term
    s += txt(ex + 192, 184, "Canny's directional operator:", size=11, fill=MUTED)
    s += txt(ex + 192, 200, "all of the detection,", size=11, fill=MUTED)
    s += txt(ex + 192, 216, "all of the localisation", size=11, fill=MUTED)
    s += txt(ex + 424, 184, "zero on a straight edge —", size=11, fill=MUTED)
    s += txt(ex + 424, 200, "the intensity is constant along it —", size=11, fill=MUTED)
    s += txt(ex + 424, 216, "and pure noise everywhere else", size=11, fill=MUTED)
    # the counter-argument
    s += f'<line x1="{ex}" y1="256" x2="{vw - 32}" y2="256" stroke="{RULE}" stroke-width="0.8"/>'
    s += txt(ex, 284, "Across scales, the sum wins:", size=14, fill=INK, family=SERIF, style="italic", anchor="start")
    s += txt(ex, 304, "the Gaussian never creates new zeros of ∇²f as σ grows,", size=11, fill=MUTED, anchor="start")
    s += txt(ex, 320, "and no filter has that property for ∂²f/∂n² alone.", size=11, fill=MUTED, anchor="start")
    s += mono(ex, 344, "Canny 1986 · Yuille & Poggio 1986", size=8, fill=SOFT, anchor="start", track="0.10em")
    s += legend(392, vw, [("the term that carries the edge", ACCENT, "box"), ("the term that carries only noise", INK, "box")])
    return emit("11", "canny-decomposition", "Across the edge, and along it",
                "The Laplacian is the second derivative across the edge plus the second derivative along it.",
                "zero-crossings", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 520
    s = eyebrow(32, 44, "model — scale-normalised response at the centre, contrast 160, from the closed forms")
    x0, y0, w, h = 96, 80, 760, 320
    smin, smax = 0.5, 4.0
    def tx(sg):
        return x0 + (sg - smin) / (smax - smin) * w
    def ty(v):
        return y0 + h - v / 140 * h
    s += axes(x0, y0, w, h, [(v, (v - smin) / (smax - smin)) for v in (0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4)],
              [(v, v / 140) for v in (0, 20, 40, 60, 80, 100, 120, 140)],
              "σ, pixels", "|σ² ∇²(G∗f)| at the centre", xfmt=lambda v: f"{v:g}")
    bar = lambda sg: 160 * 3 / (math.sqrt(2 * math.pi) * sg) * math.exp(-9 / (8 * sg * sg))
    disc = lambda sg: 160 * 9 / (sg * sg) * math.exp(-9 / (2 * sg * sg))
    N = 280
    sgs = [smin + (smax - smin) * i / N for i in range(N + 1)]
    s += polyline([(tx(g), ty(bar(g))) for g in sgs], SER2, sw=1.4)
    s += polyline([(tx(g), ty(disc(g))) for g in sgs], ACCENT, sw=1.8)
    # peaks
    for sg, v, col, lab, dx in ((1.5, 77.4, SER2, "σ = w/2 = 1.5", -104), (2.121, 117.7, ACCENT, "σ = r/√2 = 2.12", 0)):
        s += f'<line x1="{tx(sg)}" y1="{ty(v)}" x2="{tx(sg)}" y2="{y0 + h}" stroke="{col}" stroke-width="0.8" stroke-dasharray="3,3"/>'
        s += f'<circle cx="{tx(sg)}" cy="{ty(v)}" r="4" fill="{col}"/>'
        s += masked(tx(sg) + dx, ty(v) - 14, f"{lab} → {v}", size=8, fill=col)
    for sg, v, col, dx, dy in ((1.0, 62.2, SER2, 28, 16), (3.0, 56.3, SER2, 28, 16), (1.5, 86.6, ACCENT, 36, -6), (4.0, 67.9, ACCENT, -28, -10)):
        s += f'<circle cx="{tx(sg)}" cy="{ty(v)}" r="3" fill="{PAPER}" stroke="{col}" stroke-width="1.2"/>'
        s += masked(tx(sg) + dx, ty(v) + dy, f"{v}", size=8, fill=col)
    s += legend(472, vw, [("disc of radius 3", ACCENT, "line"), ("bar of width 3", SER2, "line"),
                          ("values quoted in the text", MUTED, "dot")])
    return emit("12", "scale-selection", "The σ at the peak is the size",
                "A model, not a measurement: the normalised Laplacian response of a bar and a disc as σ varies.",
                "scale selection", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 520
    s = eyebrow(32, 44, "the space–scale cube and the 26-neighbour test")
    # five planes as parallelograms, stacked
    px, py, pw, ph, sk = 200, 96, 400, 56, 120
    labels = ["σ / k", "σ", "kσ", "k²σ", "k³σ"]
    n = 5
    def plane(i):
        yy = py + (n - 1 - i) * 72
        return (f'<path d="M {px + sk} {yy} H {px + sk + pw} L {px + pw} {yy + ph} H {px} Z" '
                f'fill="#ffffff" stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>', yy)
    # draw from back (top) to front (bottom)
    for i in range(n - 1, -1, -1):
        p, yy = plane(i)
        s += p
        s += mono(px + sk + pw + 12, yy + ph / 2 + 3, labels[i], size=9, fill=MUTED, anchor="start")
    # the 3x3 blocks on planes 1,2,3 (indices)
    def block(i, focal=False):
        yy = py + (n - 1 - i) * 72
        # centre of plane
        cx = px + sk / 2 + pw / 2
        cy = yy + ph / 2
        out = ""
        cwx, cwy = 22, 12
        for r in (-1, 0, 1):
            for c in (-1, 0, 1):
                x = cx + c * cwx + r * (sk / ph) * cwy * -1 - cwx / 2
                y = cy + r * cwy - cwy / 2
                centre = focal and r == 0 and c == 0
                out += (f'<path d="M {x + (sk/ph)*cwy/2} {y} h {cwx} l {-(sk/ph)*cwy/2 if False else 0} 0 '
                        f'l {-(sk/ph)*cwy} {cwy} h {-cwx} Z" '
                        f'fill="{ACCENT if centre else ("rgba(235,108,54,0.18)" if focal else "rgba(45,49,66,0.14)")}" '
                        f'stroke="{ACCENT if focal else MUTED}" stroke-width="0.6"/>')
        return out
    s += block(3)
    s += block(2, focal=True)
    s += block(1)
    # counts
    s += masked(px + sk + pw / 2 + 200, py + (n - 1 - 3) * 72 + 8, "9 above", size=8, fill=MUTED)
    s += masked(px + sk + pw / 2 + 200, py + (n - 1 - 2) * 72 + 8, "8 around", size=8, fill=ACCENT)
    s += masked(px + sk + pw / 2 + 200, py + (n - 1 - 1) * 72 + 8, "9 below", size=8, fill=MUTED)
    # scale axis
    ax = px - 40
    s += f'<line x1="{ax}" y1="{py + (n - 1) * 72 + ph}" x2="{ax}" y2="{py - 8}" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += mono(ax - 8, py + 2 * 72 + ph / 2, "scale", size=8, fill=SOFT, anchor="end", track="0.10em")
    # side notes
    nx = 776
    s += txt(nx, 128, "each plane is σ² ∇²(G∗f)", size=12, fill=INK, anchor="start", weight="600")
    s += txt(nx, 148, "or, in a DoG stack, (k−1) σ² ∇²G ∗ f", size=11, fill=MUTED, anchor="start")
    s += txt(nx, 188, "a blob is a pixel that beats", size=11, fill=MUTED, anchor="start")
    s += txt(nx, 204, "all 26 neighbours in the", size=11, fill=MUTED, anchor="start")
    s += txt(nx, 220, "3 × 3 × 3 block", size=11, fill=MUTED, anchor="start")
    s += txt(nx, 260, "then a parabola over σ", size=11, fill=MUTED, anchor="start")
    s += txt(nx, 276, "refines the scale", size=11, fill=MUTED, anchor="start")
    s += mono(nx, 316, "blob_log: −gaussian_laplace × σ²", size=8, fill=SOFT, anchor="start", track="0.04em")
    s += mono(nx, 332, "blob_dog: (G(σ) − G(kσ)) / (k − 1)", size=8, fill=SOFT, anchor="start", track="0.04em")
    s += legend(472, vw, [("the candidate", ACCENT, "dot"), ("its 26 neighbours", MUTED, "box")])
    return emit("13", "scale-space-cube", "26 neighbours",
                "A scale-space extremum beats its 8 spatial neighbours and the 9 pixels one scale up and one scale down.",
                "scale selection", vw, vh, s)


# ------------------------------------------------------------------ FIG 14
def fig14():
    vw, vh = 1016, 468
    s = eyebrow(32, 44, "REDUCE, EXPAND, subtract — and the way back")
    bw, bh = 128, 64
    # Gaussian levels along the top, Laplacian levels below
    gx = [96, 392, 688]
    gy = 88
    ly = 264
    names = [("g₀", "the image"), ("g₁", "half size"), ("g₂ = L₂", "the residual")]
    for i, (x, (nm, sub)) in enumerate(zip(gx, names)):
        s += node(x, gy, bw, bh, nm, sub, kind="store" if i < 2 else "focal")
    lnames = [("L₀ = g₀ − E(g₁)", "fine detail"), ("L₁ = g₁ − E(g₂)", "coarser detail")]
    for x, (nm, sub) in zip(gx[:2], lnames):
        s += node(x, ly, 160, bh, nm, sub, kind="backend")
    # REDUCE arrows
    for x1, x2 in ((gx[0] + bw, gx[1]), (gx[1] + bw, gx[2])):
        s += hline(x1, x2 - 4, gy + bh / 2, stroke=MUTED)
        s += alabel((x1 + x2) / 2, gy + bh / 2, "reduce")
        s += masked((x1 + x2) / 2, gy + bh / 2 - 26, "blur · keep every other", size=8, fill=SOFT)
    # EXPAND + subtract: leave g_{i+1} by its left edge, drop in the gap, enter L_i from the right.
    # (Routed through the gap so the connector never passes behind L_i itself.)
    for i in range(2):
        x_from = gx[i + 1]                 # left edge of g_{i+1}
        y_from = gy + bh - 16              # 20px below the REDUCE line, its own attach point
        xt = gx[i + 1] - 68                # the vertical runs in the gap between columns
        x_to = gx[i] + 160                 # right edge of L_i
        y_to = ly + bh / 2 + 12
        d = (f"M {x_from} {y_from} H {xt + 8} Q {xt} {y_from} {xt} {y_from + 8} "
             f"V {y_to - 8} Q {xt} {y_to} {xt - 8} {y_to} H {x_to + 4}")
        s += f'<path d="{d}" fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>'
        s += masked(xt + 12, (y_from + y_to) / 2 + 4, "expand, subtract", size=8, fill=SOFT, anchor="start")
    # g_i down to L_i (minus)
    for i in range(2):
        xa = gx[i] + 40
        s += vline(xa, gy + bh, ly - 4, stroke=MUTED)
        s += masked(xa + 12, gy + bh + 44, "minus", size=8, fill=SOFT, anchor="start")
    # reconstruction path, dashed, along the bottom
    ry = ly + bh + 56
    s += mono(gx[2] + bw / 2 + 16, ry - 28, "reconstruction — exact, by construction", size=8, fill=ACCENT, anchor="start", track="0.10em")
    s += f'<path d="M {gx[2] + bw / 2} {gy + bh + 8} V {ry - 8} Q {gx[2] + bw / 2} {ry} {gx[2] + bw / 2 - 8} {ry} H {gx[1] + 80 + 4}" fill="none" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="5,4" marker-end="url(#arrow-accent)"/>'
    s += f'<path d="M {gx[1] + 80 - 8} {ry} H {gx[0] + 80 + 4}" fill="none" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="5,4" marker-end="url(#arrow-accent)"/>'
    s += masked((gx[1] + 80 + gx[2] + bw / 2) / 2, ry - 12, "expand, add L₁", size=8, fill=ACCENT)
    s += masked((gx[0] + 80 + gx[1] + 80) / 2, ry - 12, "expand, add L₀", size=8, fill=ACCENT)
    s += mono(gx[0] + 80, ry + 18, "= g₀ again", size=8, fill=ACCENT)
    s += legend(420, vw, [("Gaussian level", MUTED, "box"), ("Laplacian level, stored", INK, "box"),
                          ("residual, stored whole", ACCENT, "box"), ("reconstruction", ACCENT, "line")])
    return emit("14", "laplacian-pyramid", "The Laplacian pyramid",
                "Each level stores what EXPAND of the next level cannot predict; the top stores the rest.",
                "the pyramid", vw, vh, s)


# ------------------------------------------------------------------ FIG 15
def fig15():
    vw, vh = 1016, 460
    s = eyebrow(32, 44, "what Poisson editing keeps, and from where")
    # source image with region
    s += box(64, 88, 240, 200, fill="rgba(45,49,66,0.03)", stroke="rgba(45,49,66,0.30)")
    s += tag(72, 94, "source g", stroke=INK)
    s += f'<rect x="120" y="140" width="128" height="96" rx="6" fill="none" stroke="{INK}" stroke-width="1"/>'
    s += txt(184, 184, "∇²g", size=20, fill=INK, family=SERIF)
    s += mono(184, 204, "its Laplacian", size=8, fill=MUTED, track="0.08em")
    # target image with region omega
    s += box(456, 88, 480, 280, fill="rgba(45,49,66,0.03)", stroke="rgba(45,49,66,0.30)")
    s += tag(464, 94, "target f*", stroke=INK)
    s += f'<rect x="580" y="148" width="232" height="160" rx="6" fill="{ACCENT_TINT}" stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="5,4"/>'
    s += txt(696, 212, "∇²f = ∇²g", size=20, fill=ACCENT, family=SERIF)
    s += mono(696, 232, "interior: unknown pixels f", size=8, fill=ACCENT, track="0.08em")
    s += mono(696, 248, "one five-point equation each", size=8, fill=ACCENT, track="0.08em")
    s += masked(696, 140, "boundary ∂Ω: f = f*, from the target", size=8, fill=INK)
    s += masked(696, 330, "Ω", size=10, fill=ACCENT)
    # arrow source region -> omega (orthogonal): right from the source region, then into omega's left edge
    s += f'<path d="M 248 188 H 572" fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += alabel(410, 188, "transplant ∇²g")
    # notes
    s += txt(64, 332, "kept from the source: the second derivatives —", size=11, fill=MUTED, anchor="start")
    s += txt(64, 348, "edges, texture, highlights", size=11, fill=MUTED, anchor="start")
    s += txt(64, 380, "absorbed by the solve: a slow gradient that", size=11, fill=MUTED, anchor="start")
    s += txt(64, 396, "matches the source's level to the target's", size=11, fill=MUTED, anchor="start")
    s += legend(412, vw, [("the region Ω, solved for", ACCENT, "box"), ("image data, given", INK, "box")])
    return emit("15", "poisson-editing", "Boundary from the target, Laplacian from the source",
                "The pixels inside Ω are whatever makes the source's Laplacian consistent with the target's boundary.",
                "keeping the laplacian", vw, vh, s)


# ------------------------------------------------------------------ FIG 16
def fig16():
    vw, vh = 1016, 560
    s = eyebrow(32, 44, "job → call, with the scale factor the call applies")
    rows = [
        ("five-point Laplacian", "cv2.Laplacian(img, CV_64F, ksize=1)", "scipy.ndimage.laplace(img)", "× 1", False),
        ("the diagonal Laplacian", "cv2.Laplacian(img, CV_64F, ksize=3)", "add scale=0.25 to compare", "× 4", True),
        ("Laplacian of Gaussian", "cv2.GaussianBlur → cv2.Laplacian", "scipy.ndimage.gaussian_laplace(img, σ)", "no σ²", False),
        ("blob scale selection", "skimage.feature.blob_log(img, …)", "skimage.feature.blob_dog(img, sigma_ratio=1.6)", "σ² · 1/(k−1)", False),
        ("the pyramid", "cv2.pyrDown · cv2.pyrUp(dstsize=…)", "cv2.buildPyramid(img, maxlevel)", "exact", False),
        ("Poisson editing", "one 5-point equation per pixel", "any sparse linear solver", "—", False),
    ]
    y = 80
    for job, c1, c2, factor, focal in rows:
        s += txt(32, y + 22, job, size=12, fill=ACCENT if focal else INK, anchor="start", weight="600")
        s += hline(232, 296, y + 18, stroke=ACCENT if focal else MUTED, marker="arrow-accent" if focal else "arrow")
        s += masked(264, y + 6, factor, size=8, fill=ACCENT if focal else SOFT)
        s += box(304, y, 344, 36, fill=ACCENT_TINT if focal else "#ffffff", stroke=ACCENT if focal else INK)
        s += mono(476, y + 22, c1, size=9, fill=ACCENT if focal else INK, weight="500")
        s += box(664, y, 320, 36, fill="#ffffff", stroke="rgba(45,49,66,0.30)")
        s += mono(824, y + 22, c2, size=9, fill=MUTED)
        y += 64
    s += mono(32, y + 8, "ddepth: CV_16S or CV_64F, never 8-bit — the negative half is the half the zero-crossing needs",
              size=8, fill=SOFT, anchor="start", track="0.04em")
    s += legend(512, vw, [("the call that runs the job", INK, "box"), ("the alternative", MUTED, "box"),
                          ("the one whose scale surprises people", ACCENT, "box")])
    return emit("16", "tooling-map", "The tooling map",
                "Each job, the call that performs it, and the factor that call silently applies. None of it was executed for this post.",
                "implementation", vw, vh, s)


ALL = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06,
       "07": fig07, "08": fig08, "09": fig09, "10": fig10, "11": fig11, "12": fig12,
       "13": fig13, "14": fig14, "15": fig15, "16": fig16}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
