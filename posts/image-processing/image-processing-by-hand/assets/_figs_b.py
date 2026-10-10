#!/usr/bin/env python3
"""Figures 10-17 for image-processing-by-hand."""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, alabel, box, cell, elbow, elbow_hvh, emit,
                    eyebrow, hline, legend, masked, mono, node, tag, txt, vline)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "all three sort — what differs is the set")
    fams = [
        (32, "Threshold", "against one constant", "otsu · adaptive",
         "one comparison per pixel", "backend"),
        (352, "Rank", "within a neighbourhood", "median · min · max",
         "sort n values, take position k", "focal"),
        (672, "Morphology", "within a structuring element", "erode · dilate · open · close",
         "min and max, with set semantics", "backend"),
    ]
    for x, name, ordered, ops, how, kind in fams:
        focal = kind == "focal"
        colour = ACCENT if focal else INK
        s += box(x, 96, 312, 152,
                 fill=ACCENT_TINT if focal else "#ffffff", stroke=colour)
        s += tag(x + 16, 112, "sorts", stroke=colour)
        s += txt(x + 156, 152, name, size=12, weight="600", fill=colour)
        s += mono(x + 156, 172, ordered, size=9, fill=SOFT)
        s += (f'<line x1="{x + 40}" y1="{188}" x2="{x + 272}" y2="{188}" '
              f'stroke="{RULE}" stroke-width="0.8"/>')
        s += mono(x + 156, 208, ops, size=8, fill=MUTED, track="0.06em")
        s += mono(x + 156, 228, how, size=8, fill=SOFT, track="0.04em")

    s += (f'<rect x="32" y="280" width="952" height="40" rx="6" fill="none" '
          f'stroke="{RULE}" stroke-width="0.8" stroke-dasharray="4,3"/>')
    s += txt(508, 304, "none of them is a weighted sum, so none of them has a transfer function",
             size=11, fill=MUTED)

    s += legend(352, vw, [("no free parameter", ACCENT, "box"),
                          ("takes a parameter", INK, "box")])
    return emit("10", "nonlinear-families", "Where linearity stops",
                "Three families of non-linear operator, separated by what they order over.",
                "stage 4 — decide", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 432
    s = eyebrow(32, 44, "two ways to measure one gradient")
    ox, oy, k = 300, 336, 0.44           # origin, and px per gradient unit
    gx = gy = 480
    px, py = ox + gx * k, oy - gy * k     # (511.2, 124.8)

    s += f'<line x1="{ox}" y1="{oy}" x2="{ox + 280}" y2="{oy}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - 280}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += mono(ox + 288, oy + 4, "Gx", size=9, fill=SOFT, anchor="start")
    s += mono(ox - 4, oy - 288, "Gy", size=9, fill=SOFT, anchor="end")

    # L1 path: along the two legs
    s += (f'<polyline points="{ox},{oy} {px},{oy} {px},{py}" fill="none" '
          f'stroke="{MUTED}" stroke-width="1.6"/>')
    s += masked((ox + px) / 2, oy + 22, "480", size=8, fill=MUTED)
    s += masked(px + 30, (oy + py) / 2, "480", size=8, fill=MUTED)

    # L2: the hypotenuse
    s += (f'<line x1="{ox}" y1="{oy}" x2="{px}" y2="{py}" stroke="{ACCENT}" '
          f'stroke-width="1.8" marker-end="url(#arrow-accent)"/>')
    s += f'<circle cx="{px}" cy="{py}" r="3.5" fill="{ACCENT}"/>'
    s += masked((ox + px) / 2 - 44, (oy + py) / 2 - 8, "678.8", size=9, fill=ACCENT)

    # the 45-degree arc
    s += (f'<path d="M {ox + 56} {oy} A 56 56 0 0 0 {ox + 56 * math.cos(math.pi/4):.1f} '
          f'{oy - 56 * math.sin(math.pi/4):.1f}" fill="none" stroke="{SOFT}" stroke-width="0.8"/>')
    s += mono(ox + 76, oy - 20, "45°", size=8, fill=SOFT)

    rows = [("L2  √(480² + 480²)", "678.8", "the true magnitude — rotation invariant", ACCENT),
            ("L1  |480| + |480|", "960", "OpenCV's Canny default", MUTED)]
    for i, (expr, val, note, colour) in enumerate(rows):
        y = 140 + i * 88
        s += box(640, y, 344, 64, fill=ACCENT_TINT if colour == ACCENT else "#ffffff",
                 stroke=colour)
        s += mono(660, y + 26, expr, size=10, fill=colour, anchor="start", track="0.04em")
        s += mono(660, y + 48, note, size=8, fill=SOFT, anchor="start", track="0.04em")
        s += txt(940, y + 38, val, size=18, weight="600", family=MONO, fill=colour)

    s += txt(508, 372, "the ratio is exactly √2 at 45°, and exactly 1 where either component is zero",
             size=11, fill=MUTED)
    s += legend(400, vw, [("euclidean (L2)", ACCENT, "line"),
                          ("manhattan (L1)", MUTED, "line")])
    return emit("11", "l1-vs-l2", "Two lengths for the same vector",
                "The gradient at a 45° edge, measured both ways.",
                "detector — step 2", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 368
    s = eyebrow(32, 44, "canny, decomposed into stages you already have")
    steps = [
        (32, "Smooth", "Gaussian σ", "stage 2", "backend"),
        (280, "Gradient", "Sobel Gx, Gy", "stage 2", "backend"),
        (528, "Suppress", "keep local maxima along θ", "stage 4", "backend"),
        (776, "Hysteresis", "two thresholds + connectivity", "stage 4", "focal"),
    ]
    for x, name, sub, st, kind in steps:
        focal = kind == "focal"
        s += node(x, 104, 208, 96, name, sub, kind=kind, tagtext=st)
    for x1, x2 in [(240, 276), (488, 524), (736, 772)]:
        s += hline(x1, x2, 152, stroke=MUTED)

    s += mono(136, 228, "reused", size=8, fill=SOFT, track="0.14em")
    s += mono(384, 228, "reused", size=8, fill=SOFT, track="0.14em")
    s += mono(632, 228, "reused", size=8, fill=SOFT, track="0.14em")
    s += mono(880, 228, "the only new idea", size=8, fill=ACCENT, track="0.14em")

    s += (f'<rect x="32" y="256" width="704" height="40" rx="6" fill="none" '
          f'stroke="{RULE}" stroke-width="0.8" stroke-dasharray="4,3"/>')
    s += txt(384, 280, "three of the four steps are earlier stages of the pipeline",
             size=11, fill=MUTED)

    s += legend(324, vw, [("new to canny", ACCENT, "box"),
                          ("earlier stage reused", INK, "box")])
    return emit("12", "canny-chain", "Canny, end to end",
                "Four steps, three of which are operators the pipeline already defined.",
                "detector — assembly", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 476
    s = eyebrow(32, 44, "a model profile — drawn from closed forms, not measured")
    x0, x1 = 96, 920
    n = 200

    def xs(i):
        return x0 + (x1 - x0) * i / n

    # panel 1: a smoothed step
    b0 = 176
    pts = []
    for i in range(n + 1):
        u = (i / n - 0.5) * 12
        pts.append(f"{xs(i):.1f},{b0 - 72 / (1 + math.exp(-u)):.1f}")
    s += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="1.4"/>'
    s += mono(x0, 96, "brightness across the edge", size=8, fill=SOFT, anchor="start", track="0.10em")

    # panel 2: its gradient magnitude — a broad ridge
    b1 = 344
    pts = []
    for i in range(n + 1):
        u = (i / n - 0.5) * 12
        g = math.exp(-u) / (1 + math.exp(-u)) ** 2
        pts.append(f"{xs(i):.1f},{b1 - 4 * 96 * g:.1f}")
    s += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{MUTED}" stroke-width="1.4"/>'
    s += f'<line x1="{x0}" y1="{b1}" x2="{x1}" y2="{b1}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += mono(x0, 236, "gradient magnitude — several columns respond", size=8, fill=SOFT,
              anchor="start", track="0.10em")

    # the two thresholds
    for val, name, colour in ((0.62, "high", ACCENT), (0.28, "low", MUTED)):
        y = b1 - 96 * val
        s += (f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{colour}" '
              f'stroke-width="0.8" stroke-dasharray="5,4"/>')
        s += masked(x1 - 4, y - 6, f"{name} threshold", size=8, fill=colour, anchor="end")

    # the single surviving column after suppression
    peak = xs(n // 2)
    s += (f'<line x1="{peak}" y1="{b1}" x2="{peak}" y2="{b1 - 96}" stroke="{ACCENT}" '
          f'stroke-width="2.4"/>')
    s += masked(peak, b1 - 108, "one column survives", size=8, fill=ACCENT)
    s += masked(peak + 160, b1 - 36, "suppressed", size=8, fill=SOFT)
    s += masked(peak - 160, b1 - 36, "suppressed", size=8, fill=SOFT)

    s += txt(508, 396, "non-maximum suppression makes the edge thin; the gradient alone never does",
             size=11, fill=MUTED)
    s += legend(424, vw, [("surviving edge", ACCENT, "line"),
                          ("gradient ridge", MUTED, "line"),
                          ("brightness", INK, "line")])
    return emit("13", "nms-hysteresis", "Suppression, then hysteresis",
                "How a broad gradient ridge becomes a one-pixel edge. A model, not a measurement.",
                "detector — steps 3 and 4", vw, vh, s)


# ------------------------------------------------------------------ FIG 14
def fig14():
    vw, vh = 1016, 468
    s = eyebrow(32, 44, "the two eigenvalues of the gradient covariance")
    ox, oy, size = 264, 368, 288
    s += f'<line x1="{ox}" y1="{oy}" x2="{ox + size}" y2="{oy}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy - size}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += mono(ox + size + 8, oy + 4, "λ₁", size=10, fill=SOFT, anchor="start")
    s += mono(ox - 8, oy - size - 4, "λ₂", size=10, fill=SOFT, anchor="end")

    regions = [
        (ox + 16, oy - 96, 80, 80, "flat", "both small", MUTED),
        (ox + 128, oy - 96, 144, 80, "edge", "one large", MUTED),
        (ox + 128, oy - 272, 144, 144, "corner", "both large", ACCENT),
        (ox + 16, oy - 272, 80, 144, "edge", "one large", MUTED),
    ]
    for x, y, w, h, name, sub, colour in regions:
        focal = colour == ACCENT
        s += (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" '
              f'fill="{ACCENT if focal else INK}" fill-opacity="{0.10 if focal else 0.04}" '
              f'stroke="{colour}" stroke-width="0.8" stroke-opacity="{1 if focal else 0.5}"/>')
        s += txt(x + w / 2, y + h / 2, name, size=12, weight="600", fill=colour)
        s += mono(x + w / 2, y + h / 2 + 16, sub, size=8, fill=SOFT)

    # the boundary k moves
    s += (f'<path d="M {ox + 112} {oy - 8} L {ox + 112} {oy - size + 8}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="5,4"/>')
    s += (f'<line x1="{ox + 112}" y1="{oy - 300}" x2="{ox + 160}" y2="{oy - 300}" '
          f'stroke="{ACCENT}" stroke-width="1" marker-end="url(#arrow-accent)"/>')
    s += masked(ox + 200, oy - 296, "k moves this", size=8, fill=ACCENT, anchor="start")

    rows = [("Harris", "det M − k (tr M)²", "k is empirical, 0.04–0.06, no default", ACCENT),
            ("Shi–Tomasi", "min(λ₁, λ₂)", "same test, nothing to tune", MUTED)]
    for i, (name, expr, note, colour) in enumerate(rows):
        y = 152 + i * 88
        s += box(624, y, 360, 64, fill=ACCENT_TINT if colour == ACCENT else "#ffffff",
                 stroke=colour)
        s += txt(644, y + 26, name, size=12, weight="600", anchor="start", fill=colour)
        s += mono(644, y + 48, note, size=8, fill=SOFT, anchor="start", track="0.04em")
        s += mono(964, y + 30, expr, size=10, fill=colour, anchor="end", track="0.04em")

    s += legend(416, vw, [("corner region", ACCENT, "box"),
                          ("edge or flat", MUTED, "box")])
    return emit("14", "eigenvalue-plane", "What the free parameter actually controls",
                "Flat, edge and corner in the λ₁–λ₂ plane, and where k puts the boundary.",
                "detector — corners", vw, vh, s)


# ------------------------------------------------------------------ FIG 15
def fig15():
    vw, vh = 1016, 432
    s = eyebrow(32, 44, "σ is an axis, not a knob")
    x0, w, n = 120, 800, 240
    levels = [(0.6, 128, "σ = 0.8", MUTED),
              (1.6, 208, "σ = 1.6", MUTED),
              (3.2, 288, "σ = 3.2", ACCENT)]

    def profile(sig, amp, base):
        pts = []
        for i in range(n + 1):
            u = x0 + w * i / n
            # two features: a narrow one and a wide one, each blurred by sig
            fine = math.exp(-((u - 320) ** 2) / (2 * (6 + 26 * sig) ** 2))
            broad = math.exp(-((u - 680) ** 2) / (2 * (56 + 26 * sig) ** 2))
            v = fine / (1 + 0.9 * sig) + broad
            pts.append(f"{u:.1f},{base - amp * v:.1f}")
        return pts

    for sig, base, label, colour in levels:
        pts = profile(sig, 72, base)
        s += (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colour}" '
              f'stroke-width="1.4"/>')
        s += (f'<line x1="{x0}" y1="{base}" x2="{x0 + w}" y2="{base}" '
              f'stroke="{RULE}" stroke-width="0.8"/>')
        s += mono(x0 - 16, base - 4, label, size=8, fill=colour, anchor="end", track="0.06em")

    for gx, lab in ((320, "fine feature — gone by σ = 3.2"),
                    (680, "coarse feature — survives")):
        s += (f'<line x1="{gx}" y1="72" x2="{gx}" y2="304" stroke="{RULE}" '
              f'stroke-width="0.8" stroke-dasharray="4,3"/>')
        s += masked(gx, 320, lab, size=8, fill=SOFT)

    s += txt(508, 348, "choosing σ chooses which structures exist in the image your operator sees",
             size=11, fill=MUTED)
    s += legend(380, vw, [("coarsest scale", ACCENT, "line"),
                          ("finer scales", MUTED, "line")])
    return emit("15", "scale-axis", "What σ decides",
                "The same signal at three scales: one feature survives, one does not.",
                "scale", vw, vh, s)


# ------------------------------------------------------------------ FIG 16
def fig16():
    vw, vh = 1016, 412
    s = eyebrow(32, 44, "math → call site · none of it executed for this post")
    cols = [
        (32, "Sample", ["cv2.resize", "cv2.pyrDown", "INTER_AREA"],
         "resample on a new grid", "backend"),
        (280, "Filter", ["cv2.filter2D", "cv2.sepFilter2D", "cv2.GaussianBlur",
                         "cv2.Sobel / Scharr"], "the weighted sum", "focal"),
        (528, "Transform", ["cv2.dft / cv2.idft", "np.fft.fft2",
                            "getOptimalDFTSize"], "change of basis", "backend"),
        (776, "Decide", ["cv2.threshold", "cv2.medianBlur", "cv2.erode / dilate",
                         "cv2.morphologyEx"], "sort and compare", "backend"),
    ]
    for x, name, calls, sub, kind in cols:
        focal = kind == "focal"
        colour = ACCENT if focal else INK
        s += box(x, 96, 208, 200, fill=ACCENT_TINT if focal else "#ffffff", stroke=colour)
        s += txt(x + 104, 128, name, size=12, weight="600", fill=colour)
        s += mono(x + 104, 146, sub, size=8, fill=SOFT, track="0.04em")
        s += (f'<line x1="{x + 24}" y1="160" x2="{x + 184}" y2="160" '
              f'stroke="{RULE}" stroke-width="0.8"/>')
        for i, c in enumerate(calls):
            s += mono(x + 104, 186 + i * 26, c, size=9, fill=MUTED, track="0.02em")
    for x1, x2 in [(240, 276), (488, 524), (736, 772)]:
        s += hline(x1, x2, 216, stroke=MUTED)

    s += txt(508, 332, "NumPy holds the array · OpenCV supplies the operators · SciPy uses the convolution convention",
             size=11, fill=MUTED)
    s += legend(360, vw, [("where the sum lives", ACCENT, "box"),
                          ("other stages", INK, "box")])
    return emit("16", "tooling-map", "The tooling map",
                "Each stage of the pipeline against the calls that implement it.",
                "implementation", vw, vh, s)


# ------------------------------------------------------------------ FIG 17
def fig17():
    vw, vh = 1016, 528
    s = eyebrow(32, 44, "this post, and what it hands off")
    s += box(360, 88, 296, 72, fill=ACCENT_TINT, stroke=ACCENT)
    s += txt(508, 120, "Image Processing by Hand", size=12, weight="600", fill=ACCENT)
    s += mono(508, 140, "the frame and the shared math", size=8, fill=SOFT, track="0.04em")

    groups = [
        (36, "Sample", ["Resampling and aliasing"]),
        (228, "Filter", ["Kernel design"]),
        (420, "Transform", ["The 2-D DFT", "Wavelets"]),
        (612, "Decide", ["Thresholding and segmentation", "Morphology",
                         "Edge-preserving smoothing"]),
        (804, "Detect & scale", ["Canny, line by line", "The structure tensor",
                                 "Scale space and SIFT", "Luma, luminance, gamma"]),
    ]
    for x, name, children in groups:
        w = 176
        cx = x + w / 2
        s += elbow(508, 160, cx, 208, stroke=MUTED)
        s += box(x, 208, w, 40, fill="#ffffff", stroke=INK)
        s += txt(cx, 233, name, size=11, weight="600", fill=INK)
        for i, ch in enumerate(children):
            y = 272 + i * 44
            s += box(x, y, w, 32, fill="rgba(45,49,66,0.03)", stroke="rgba(45,49,66,0.30)")
            s += mono(cx, y + 20, ch, size=8, fill=MUTED, track="0.02em")
            s += (f'<line x1="{cx}" y1="{248 if i == 0 else y - 12}" x2="{cx}" y2="{y}" '
                  f'stroke="{RULE}" stroke-width="0.8"/>')

    s += legend(472, vw, [("this post", ACCENT, "box"),
                          ("area named here", INK, "box"),
                          ("child post", MUTED, "box")])
    return emit("17", "series-map", "The series",
                "Every area this post names, and the child post that goes deep on it.",
                "series", vw, vh, s)


FIGS = {"10": fig10, "11": fig11, "12": fig12, "13": fig13, "14": fig14,
        "15": fig15, "16": fig16, "17": fig17}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FIGS)
    for k in want:
        if k in FIGS:
            FIGS[k]()
