#!/usr/bin/env python3
"""Figures 01-09 for image-processing-by-hand."""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, alabel, box, cell, elbow, emit, eyebrow,
                    elbow_hvh, hline, legend, masked, mono, node, tag, txt, vline)

PATCH = [[40, 40, 40, 200, 200],
         [40, 40, 40, 200, 200],
         [40, 255, 40, 200, 200],
         [40, 40, 40, 200, 200],
         [40, 40, 40, 200, 200]]


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 372
    s = eyebrow(32, 44, "stage / what it costs")
    ys, h = 96, 80
    stages = [
        (184, "Sample", "grid + levels", "focal", "01"),
        (356, "Filter", "weighted sum", "backend", "02"),
        (528, "Transform", "change of basis", "backend", "03"),
        (700, "Decide", "sort / compare", "backend", "04"),
    ]
    s += node(32, ys, 112, h, "Scene", "continuous", kind="input")
    for x, name, sub, kind, t in stages:
        s += node(x, ys, 132, h, name, sub, kind=kind, tagtext=t)
    s += node(872, ys, 112, h, "Answer", "labels", kind="external")

    ay = ys + h / 2
    for x1, x2 in [(144, 180), (316, 352), (488, 524), (660, 696), (832, 868)]:
        s += hline(x1, x2, ay, stroke=MUTED)

    notes = [(184 + 66, "irreversible", ACCENT, "information is gone"),
             (356 + 66, "not invertible", MUTED, "in practice"),
             (528 + 66, "invertible", MUTED, "by construction"),
             (700 + 66, "irreversible", MUTED, "keeps only the answer")]
    for cx, head, colour, sub in notes:
        s += mono(cx, 212, head.upper(), size=8, fill=colour, track="0.14em")
        s += txt(cx, 230, sub, size=11, fill=SOFT)

    s += (f'<rect x="184" y="252" width="132" height="36" rx="6" '
          f'fill="{ACCENT_TINT}" stroke="{ACCENT}" stroke-width="0.8" '
          f'stroke-dasharray="4,4"/>')
    s += mono(250, 274, "the only lossy step", size=8, fill=ACCENT, track="0.06em")

    s += legend(320, vw, [("focal stage", ACCENT, "box"),
                          ("operator stage", INK, "box"),
                          ("outside your code", MUTED, "box")])
    return emit("01", "four-stages", "The four stages",
                "Sample, filter, transform, decide — and which of them can be undone.",
                "pipeline", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 484
    s = eyebrow(32, 44, "the array you index")
    s += eyebrow(568, 44, "the signal you reason about — row r2")

    cw, ch, x0, y0 = 48, 44, 96, 108
    for c in range(5):
        s += mono(x0 + c * cw + cw / 2, y0 - 12, f"c{c}", size=8, fill=SOFT, track="0.08em")
    for r in range(5):
        s += mono(x0 - 16, y0 + r * ch + ch / 2 + 4, f"r{r}", size=8, fill=SOFT, track="0.08em")
    for r in range(5):
        for c in range(5):
            v = PATCH[r][c]
            spike = (r, c) == (2, 1)
            fill = ACCENT_TINT if spike else ("#ffffff" if v == 40 else "rgba(45,49,66,0.08)")
            stroke = ACCENT if spike else "rgba(45,49,66,0.28)"
            s += cell(x0 + c * cw, y0 + r * ch, cw, ch, v, fill=fill, stroke=stroke,
                      tcolor=ACCENT if spike else INK,
                      weight="600" if spike else "500")
    s += mono(x0 + 24, y0 + 5 * ch + 24, "background 40", size=8, fill=SOFT, track="0.06em", anchor="start")
    s += mono(x0 + 152, y0 + 5 * ch + 24, "step 200", size=8, fill=SOFT, track="0.06em", anchor="start")
    s += mono(x0, y0 + 5 * ch + 44, "impulse 255 at (2, 1)", size=8, fill=ACCENT,
              track="0.06em", anchor="start")

    # row 2 as a step profile — the row that carries every feature at once
    rx0, step, base, k = 600, 72, 344, 0.86
    row = PATCH[2]
    pts = [f"{rx0},{base}"]
    for c, v in enumerate(row):
        x1, x2 = rx0 + c * step, rx0 + (c + 1) * step
        pts += [f"{x1},{base - v * k}", f"{x2},{base - v * k}"]
    pts.append(f"{rx0 + 5 * step},{base}")
    s += (f'<polygon points="{" ".join(pts)}" fill="{INK}" fill-opacity="0.05" '
          f'stroke="{INK}" stroke-width="1" stroke-linejoin="round"/>')
    sx1, sx2 = rx0 + step, rx0 + 2 * step
    s += (f'<polyline points="{sx1},{base - 40 * k} {sx1},{base - 255 * k} '
          f'{sx2},{base - 255 * k} {sx2},{base - 40 * k}" fill="none" '
          f'stroke="{ACCENT}" stroke-width="1.6" stroke-linejoin="round"/>')
    s += (f'<line x1="{rx0 - 8}" y1="{base}" x2="{rx0 + 5 * step + 8}" y2="{base}" '
          f'stroke="{RULE_SOLID}" stroke-width="0.8"/>')
    for c, v in enumerate(row):
        cx = rx0 + c * step + step / 2
        s += masked(cx, base - v * k - 8, str(v), size=8,
                    fill=ACCENT if v == 255 else MUTED)
        s += mono(cx, base + 18, f"c{c}", size=8, fill=SOFT, track="0.08em")
    s += mono(rx0 - 16, base - 36 * k, "40", size=8, fill=SOFT, anchor="end")

    s += txt(rx0 + 180, 392, "one plateau, one spike, one step — the other four rows",
             size=11, fill=SOFT)
    s += txt(rx0 + 180, 410, "are identical without the spike", size=11, fill=SOFT)

    s += legend(436, vw, [("impulse", ACCENT, "line"),
                          ("row profile", INK, "line")])
    return emit("02", "grid-and-surface", "One patch, two readings",
                "The same 25 integers as a table and as a sampled surface.",
                "representation", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 452
    s = eyebrow(32, 44, "one window, nine numbers")
    win = [[40, 40, 40], [40, 255, 40], [40, 40, 40]]
    cw, x0, y0 = 56, 88, 128
    for r in range(3):
        for c in range(3):
            v = win[r][c]
            spike = v == 255
            s += cell(x0 + c * cw, y0 + r * cw, cw, cw, v,
                      fill=ACCENT_TINT if spike else "#ffffff",
                      stroke=ACCENT if spike else "rgba(45,49,66,0.28)",
                      tcolor=ACCENT if spike else INK, size=12,
                      weight="600" if spike else "500")
    s += mono(x0 + 84, y0 - 16, "3 x 3 at (2, 1)", size=8, fill=SOFT, track="0.10em")

    # each connector leaves the grid at its own point and turns in its own column,
    # so no two verticals ever share a path
    results = [
        (96, 176, 320, "Box mean", "575 / 9 = 63.9", "64", "backend",
         "smears it over nine pixels"),
        (200, 216, 360, "Gaussian", "0.2725(255) + 0.7275(40)", "99", "backend",
         "27% of the weight sits on the bad pixel"),
        (304, 256, 400, "Median", "sorted: 40 40 40 40 [40] 40 40 40 255", "40", "focal",
         "removes it exactly, neighbours untouched"),
    ]
    for y, yattach, xturn, name, work, out, kind, note in results:
        focal = kind == "focal"
        colour = ACCENT if focal else MUTED
        s += elbow_hvh(x0 + 3 * cw, yattach, xturn, y + 36, 496, stroke=colour,
                       marker="arrow-accent" if focal else "arrow")
        s += node(504, y, 300, 72, "", kind=kind)
        s += txt(520, y + 26, name, size=12, weight="600", anchor="start",
                 fill=ACCENT if focal else INK)
        s += mono(520, y + 44, work, size=8, fill=SOFT, anchor="start", track="0.04em")
        s += mono(520, y + 60, note, size=8, fill=MUTED, anchor="start", track="0.04em")
        s += box(824, y + 12, 88, 48,
                 fill=ACCENT_TINT if focal else "rgba(45,49,66,0.05)",
                 stroke=ACCENT if focal else MUTED)
        s += txt(868, y + 44, out, size=20, weight="600", family=MONO,
                 fill=ACCENT if focal else INK)

    s += legend(408, vw, [("removes the impulse", ACCENT, "box"),
                          ("spreads it", INK, "box")])
    return emit("03", "three-answers", "Three answers from the same nine numbers",
                "Box, Gaussian and median applied to one neighbourhood.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 396
    s = eyebrow(32, 44, "same shape, different weights")
    stencils = [
        (64, "Box", "1/9 each", [["1/9"] * 3] * 3, "sums to 1", INK),
        (392, "Gaussian σ = 0.8", "sampled, normalised",
         [["0.0571", "0.1248", "0.0571"],
          ["0.1248", "0.2725", "0.1248"],
          ["0.0571", "0.1248", "0.0571"]], "sums to 1", INK),
        (720, "Sobel Gx", "smooth × difference",
         [["-1", "0", "1"], ["-2", "0", "2"], ["-1", "0", "1"]], "sums to 0", ACCENT),
    ]
    cw, y0 = 76, 128
    for x0, name, sub, vals, foot, colour in stencils:
        s += txt(x0 + 114, 96, name, size=12, weight="600", fill=colour)
        s += mono(x0 + 114, 112, sub, size=8, fill=SOFT, track="0.06em")
        for r in range(3):
            for c in range(3):
                v = vals[r][c]
                focal = colour == ACCENT and v not in ("0",)
                s += cell(x0 + c * cw, y0 + r * 56, cw, 56, v,
                          fill=ACCENT_TINT if focal else "#ffffff",
                          stroke=colour if colour == ACCENT else "rgba(45,49,66,0.28)",
                          tcolor=colour if focal else INK, size=10)
        s += (f'<rect x="{x0 + 60}" y="{y0 + 180}" width="108" height="16" rx="2" '
              f'fill="transparent" stroke="{colour}" stroke-opacity="0.40" stroke-width="0.8"/>')
        s += mono(x0 + 114, y0 + 192, foot, size=8, fill=colour, track="0.10em")

    s += txt(508, 344, "A unit-sum stencil is an average. A zero-sum stencil is a derivative.",
             size=11, fill=MUTED)
    s += legend(372, vw, [("derivative", ACCENT, "box"), ("average", INK, "box")])
    return emit("04", "weight-stencils", "Three stencils",
                "One operation — a weighted sum — carrying three different weight sets.",
                "operators", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 516
    s = eyebrow(32, 44, "sampling replicates the spectrum")

    def panel(y0, spacing, label, overlap):
        out = f'<line x1="96" y1="{y0}" x2="920" y2="{y0}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
        centres = [508 - spacing, 508, 508 + spacing]
        half = 132
        for i, cx in enumerate(centres):
            focal = i == 1
            col = INK if focal else MUTED
            pts = f"{cx - half},{y0} {cx},{y0 - 88} {cx + half},{y0}"
            out += (f'<polygon points="{pts}" fill="{col}" fill-opacity="'
                    f'{0.10 if focal else 0.06}" stroke="{col}" stroke-width="1"/>')
        if overlap:
            for cx in (508 - spacing, 508 + spacing):
                lo, hi = sorted([cx, 508])
                xa, xb = hi - half, lo + half
                if xb > xa:
                    mid = (xa + xb) / 2
                    peak = y0 - 88 * (1 - abs(mid - 508) / half)
                    out += (f'<polygon points="{xa},{y0} {mid},{peak} {xb},{y0}" '
                            f'fill="{ACCENT}" fill-opacity="0.22" stroke="{ACCENT}" '
                            f'stroke-width="1"/>')
        for cx, lab in zip(centres, ["-ωs", "0", "+ωs"]):
            out += mono(cx, y0 + 18, lab, size=8, fill=SOFT, track="0.08em")
        out += mono(96, y0 - 96, label.upper(), size=8, fill=SOFT, anchor="start", track="0.14em")
        return out

    s += panel(184, 296, "sampled fast enough — copies clear each other", False)
    s += panel(392, 208, "sampled too slowly — copies sum in the overlap", True)
    s += mono(508, 440, "aliasing: the overlap is added before you ever see a sample",
              size=9, fill=ACCENT, track="0.04em")

    s += legend(472, vw, [("baseband", INK, "box"),
                          ("replicas", MUTED, "box"),
                          ("aliased energy", ACCENT, "box")])
    return emit("05", "spectral-replication", "Why aliasing cannot be fixed afterwards",
                "Sampling copies the spectrum at every multiple of the sampling frequency.",
                "stage 1 — sample", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 356
    s = eyebrow(32, 44, "one 3x3 pass vs two 1-d passes")
    s += node(32, 128, 112, 72, "Input", "row of pixels", kind="input")

    s += node(232, 64, 200, 72, "3 × 3 stencil", "9 multiplies / pixel", kind="backend")
    s += node(232, 216, 168, 72, "Row pass 1 × 3", "3 multiplies", kind="focal")
    s += node(456, 216, 168, 72, "Column pass 3 × 1", "3 multiplies", kind="focal")
    s += node(760, 128, 112, 72, "Output", "identical", kind="external")

    s += elbow(144, 164, 232, 100, stroke=MUTED)
    s += hline(432, 752, 100, stroke=MUTED)
    s += elbow(144, 164, 232, 252, stroke=ACCENT, marker="arrow-accent")
    s += hline(400, 452, 252, stroke=ACCENT, marker="arrow-accent")
    s += elbow(624, 252, 756, 176, stroke=ACCENT, marker="arrow-accent")

    s += alabel(592, 100, "9 mults", fill=MUTED, gap=18, w=56)
    s += alabel(692, 252, "6 mults", fill=ACCENT, gap=18, w=56)

    s += mono(508, 316, "k × k costs k² one way and 2k the other: 9 vs 6 at k = 3, 225 vs 30 at k = 15",
              size=9, fill=SOFT, track="0.04em")
    return emit("06", "separability", "Separability",
                "A kernel that factors runs as two 1-D passes for the same result.",
                "stage 2 — filter", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 420
    s = eyebrow(32, 44, "five rules, five answers, same pixel")
    rows = [
        ("BORDER_CONSTANT", ["0", "0"], "invents zeros", MUTED),
        ("BORDER_REPLICATE", ["40", "40"], "repeats the edge value", MUTED),
        ("BORDER_REFLECT", ["40", "40"], "mirrors, edge duplicated", MUTED),
        ("BORDER_REFLECT_101", ["40", "40"], "mirrors, edge not duplicated", ACCENT),
        ("BORDER_WRAP", ["200", "200"], "pulls from the far side", MUTED),
    ]
    real = ["40", "40", "40", "200", "200"]
    cw, y0, x0 = 64, 104, 344
    s += mono(x0 - 68, y0 - 16, "invented", size=8, fill=SOFT, track="0.10em")
    s += mono(x0 + 160, y0 - 16, "real pixels of row 0", size=8, fill=SOFT, track="0.10em")
    for i, (name, inv, note, colour) in enumerate(rows):
        y = y0 + i * 56
        s += mono(32, y + 34, name, size=9, fill=colour, anchor="start", track="0.04em")
        for j, v in enumerate(inv):
            s += cell(x0 - 128 + j * cw, y, cw, 48, v,
                      fill=ACCENT_TINT if colour == ACCENT else "rgba(45,49,66,0.04)",
                      stroke=colour if colour == ACCENT else "rgba(45,49,66,0.22)",
                      tcolor=colour if colour == ACCENT else SOFT, size=11)
        for j, v in enumerate(real):
            s += cell(x0 + j * cw, y, cw, 48, v, fill="#ffffff",
                      stroke="rgba(45,49,66,0.28)", size=11)
        s += mono(x0 + 344, y + 30, note, size=8, fill=SOFT, anchor="start", track="0.04em")
    s += (f'<line x1="{x0 - 4}" y1="{y0 - 8}" x2="{x0 - 4}" y2="{y0 + 5 * 56 - 8}" '
          f'stroke="{INK}" stroke-width="1" stroke-dasharray="4,3"/>')
    s += mono(508, 400, "the linear filters and the morphological operators do not share a default",
              size=9, fill=MUTED, track="0.04em")
    return emit("07", "border-modes", "Borders are a parameter",
                "What each extrapolation rule invents where the window leaves the array.",
                "stage 2 — filter", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 460
    s = eyebrow(32, 44, "four points, two routes, one answer")
    panels = [
        (32, "x[n]", [40, 40, 200, 200], 200, INK, "the step"),
        (280, "|X[k]|", [480, 226.3, 0, 226.3], 480, MUTED, "its spectrum"),
        (528, "H[k]", [1, 0.5, 0, 0.5], 1, ACCENT, "the filter's gain"),
        (776, "y[n]", [80, 80, 160, 160], 200, INK, "the result"),
    ]
    bw, base, top = 44, 296, 128
    for x0, name, vals, vmax, colour, note in panels:
        s += mono(x0 + 104, 92, name, size=10, fill=colour, track="0.08em", weight="500")
        s += mono(x0 + 104, 108, note, size=8, fill=SOFT, track="0.04em")
        s += (f'<line x1="{x0}" y1="{base}" x2="{x0 + 208}" y2="{base}" '
              f'stroke="{RULE_SOLID}" stroke-width="0.8"/>')
        for i, v in enumerate(vals):
            hgt = (v / vmax) * (base - top)
            bx = x0 + 12 + i * (bw + 8)
            if hgt > 0:
                s += (f'<rect x="{bx}" y="{base - hgt}" width="{bw}" height="{hgt}" '
                      f'fill="{colour}" fill-opacity="0.18" stroke="{colour}" stroke-width="1"/>')
            lbl = f"{v:g}" if v == int(v) else f"{v:.1f}"
            s += mono(bx + bw / 2, base - hgt - 8 if hgt > 0 else base - 8, lbl,
                      size=8, fill=colour, track="0.04em")
            s += mono(bx + bw / 2, base + 16, str(i), size=8, fill=SOFT)
    for x, lab, colour in ((256, "dft", MUTED), (504, "× H[k]", ACCENT),
                           (752, "inverse", MUTED)):
        s += mono(x, 208, "→", size=14, fill=colour)
        s += mono(x, 228, lab.upper(), size=8, fill=colour, track="0.10em")
    s += mono(508, 352, "route A — nine multiplies in space: 0.5(40) + 0.25(200) + 0.25(40) = 80",
              size=9, fill=MUTED, track="0.04em")
    s += mono(508, 372, "route B — one multiply per frequency, then invert: same [80, 80, 160, 160]",
              size=9, fill=ACCENT, track="0.04em")
    s += legend(412, vw, [("signal", INK, "box"),
                          ("spectrum", MUTED, "box"),
                          ("transfer function", ACCENT, "box")])
    return emit("08", "dft-four-point", "A 4-point DFT, by hand",
                "The step, its spectrum, the filter's gain per frequency, and the result.",
                "stage 3 — transform", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 456
    s = eyebrow(32, 44, "gain against normalised frequency")
    x0, x1, base, top = 96, 900, 320, 96
    zero = 264  # y for gain 0; below it the curve is negative

    s += f'<line x1="{x0}" y1="{zero}" x2="{x1}" y2="{zero}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += f'<line x1="{x0}" y1="{top}" x2="{x0}" y2="{base}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    for frac, lab in [(0, "0"), (0.5, "π/2"), (1, "π")]:
        x = x0 + frac * (x1 - x0)
        s += f'<line x1="{x}" y1="{zero - 3}" x2="{x}" y2="{zero + 3}" stroke="{SOFT}" stroke-width="0.8"/>'
        s += mono(x, zero + 20, lab, size=8, fill=SOFT)
    for val, lab in [(1, "1"), (0, "0")]:
        y = zero - val * (zero - top)
        s += mono(x0 - 16, y + 4, lab, size=8, fill=SOFT)

    def curve(fn, colour, width=1.4, dash=None):
        pts = []
        for i in range(161):
            w = math.pi * i / 160
            g = fn(w)
            x = x0 + (w / math.pi) * (x1 - x0)
            y = zero - g * (zero - top)
            y = max(top - 4, min(base, y))
            pts.append(f"{x:.1f},{y:.1f}")
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colour}" '
                f'stroke-width="{width}"{d}/>')

    def box3(w):  # 3-tap box mean, normalised
        return (1 + 2 * math.cos(w)) / 3

    def gauss(w):  # sigma = 0.8, 3-tap sampled Gaussian
        return 0.5221 + 2 * 0.2389 * math.cos(w)

    def lap(w):  # 1-D second difference, scaled to 1 at Nyquist
        return (2 - 2 * math.cos(w)) / 4

    # shade where the box filter's gain is negative — that is the whole point of it
    neg = []
    for i in range(161):
        w = math.pi * i / 160
        g = box3(w)
        if g < 0:
            x = x0 + (w / math.pi) * (x1 - x0)
            neg.append((x, zero - g * (zero - top)))
    if neg:
        pts = f"{neg[0][0]:.1f},{zero} " + " ".join(f"{x:.1f},{y:.1f}" for x, y in neg) \
              + f" {neg[-1][0]:.1f},{zero}"
        s += f'<polygon points="{pts}" fill="{MUTED}" fill-opacity="0.14"/>'

    s += curve(box3, MUTED)
    s += curve(gauss, INK)
    s += curve(lap, ACCENT)

    s += masked(x1 - 8, base + 28, "normalised frequency  0 → π", size=8, fill=SOFT, anchor="end")
    s += masked(700, 176, "Laplacian — gain grows with frequency", size=8, fill=ACCENT)
    s += masked(280, 208, "Gaussian — monotone, never negative", size=8, fill=INK)
    s += masked(452, 344, "box mean — negative lobe: it inverts, not just attenuates",
                size=8, fill=MUTED)
    s += masked(x0 - 20, base + 4, "−1/3", size=8, fill=SOFT)

    s += legend(408, vw, [("box mean", MUTED, "line"),
                          ("gaussian σ = 0.8", INK, "line"),
                          ("laplacian", ACCENT, "line")])
    return emit("09", "transfer-functions", "What three kernels do to each frequency",
                "Plotted from the closed-form transfer functions — a model, not a measurement.",
                "stage 3 — transform", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05,
        "06": fig06, "07": fig07, "08": fig08, "09": fig09}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FIGS)
    for k in want:
        if k in FIGS:
            FIGS[k]()
