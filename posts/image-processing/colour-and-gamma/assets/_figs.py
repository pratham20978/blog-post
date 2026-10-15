#!/usr/bin/env python3
"""Figures 01-09 for colour-and-gamma.

Every value drawn is computed in _data.py from the standards' constants: the sRGB curve, the sRGB and
1953 NTSC matrices, CIELAB under three whites, the patch's step blurred in codes and in light, and the
all-colour luma sweep. Swatches are painted with their true sRGB values (Chrome is pinned to the sRGB
profile in _build.rasterize). Colour meanings hold across the post: tangerine is a computation on codes
(luma, a blur of codes), blue is a computation on light (luminance, a blur of light).
Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SANS, SOFT,
                    emit, eyebrow, mono, txt)
import _data as d

LINE_SOFT = "rgba(45,49,66,0.45)"


# ------------------------------------------------------------------ drawing helpers (series toolchain)
def fmt(v, nd=1):
    s = f"{v:,.{nd}f}"
    return s.replace("-", "−")


def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, marker=None, cap=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    c = f' stroke-linecap="{cap}"' if cap else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}{m}{c}{o}/>')


def polyline(pts, stroke, sw=1.6, dash=None, op=None, clip=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    cp = f' clip-path="url(#{clip})"' if clip else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}{o}{cp}/>')


def polygon(pts, fill, stroke="none", sw=0.8, op=None, dash=None):
    o = f' fill-opacity="{op}"' if op is not None else ""
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None):
    s = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{s}/>'


def ring(x, y, rr=5, stroke=INK, sw=1.6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{PAPER}" stroke="{stroke}" stroke-width="{sw}"/>'


def note_lines(x, y, items, size=8.5, gap=16, anchor="start"):
    out = ""
    for k, (t, c) in enumerate(items):
        if t:
            out += mono(x, y + k * gap, t, size=size, fill=c, anchor=anchor,
                        weight="600" if c in (INK, LINK, ACCENT) else "400")
    return out


def title(x, y, s, fill=INK, anchor="start", size=9.5):
    """A panel title in mono, not uppercased, so notation like sRGB, L* and Y′ keeps its case."""
    return mono(x, y, s, size=size, fill=fill, anchor=anchor, weight="600")


def plate(x, y, s, size=8, fill=INK, anchor="middle", weight="600", bg=PAPER, pad=4):
    """Text on an opaque plate, used only where a label must sit on a fill, never over a plotted line."""
    w = 0.62 * size * len(str(s)) + 2 * pad
    x0 = {"middle": x - w / 2, "start": x - pad, "end": x - w + pad}[anchor]
    return (f'<rect x="{x0:.1f}" y="{y - size - 2:.1f}" width="{w:.1f}" height="{size + 6}" rx="2" fill="{bg}"/>'
            + mono(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight))


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def clip(self, cid):
        return (f'<clipPath id="{cid}"><rect x="{self.x0}" y="{self.y0}" width="{self.w}" '
                f'height="{self.h}"/></clipPath>')

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid_y=True):
        s = line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, stroke=RULE_SOLID)
        s += line(self.x0, self.y0, self.x0, self.y0 + self.h, stroke=RULE_SOLID)
        for v in yt:
            yy = self.Y(v)
            if grid_y:
                s += line(self.x0, yy, self.x0 + self.w, yy, stroke=RULE, sw=0.8)
            s += mono(self.x0 - 7, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            s += mono(self.X(v), self.y0 + self.h + 14, xfmt(v), size=8, fill=SOFT)
        if xlab:
            s += mono(self.x0 + self.w, self.y0 + self.h + 30, xlab, size=8.5, fill=SOFT, anchor="end")
        if ylab:
            s += mono(self.x0, self.y0 - 10, ylab, size=8.5, fill=SOFT, anchor="start")
        return s


MARKS = f"""<defs>
    <marker id="ai" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{INK}"/></marker>
    <marker id="al" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
    <marker id="aa" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
    <marker id="am" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
  </defs>"""


def arrow(x1, y1, x2, y2, colour, sw=1.4, dash=None):
    m = {INK: "ai", LINK: "al", ACCENT: "aa", MUTED: "am"}[colour]
    return line(x1, y1, x2, y2, stroke=colour, sw=sw, marker=m, dash=dash)


def rgb(t):
    return f"rgb({t[0]},{t[1]},{t[2]})"


def grey(v):
    g = max(0, min(255, round(v)))
    return f"rgb({g},{g},{g})"


def swatch(x, y, w, h, fill, stroke=LINE_SOFT, sw=0.8):
    return rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw)


def text_on(v):
    """Ink on light greys, white on dark ones (a code's own lightness decides)."""
    return "#ffffff" if v < 118 else INK


def legend(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like the marks they name."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, colour, kind in items:
        if kind == "line":
            s += line(x, y + 5, x + 18, y + 5, stroke=colour, sw=1.8)
        elif kind == "linedot":
            s += line(x, y + 5, x + 18, y + 5, stroke=colour, sw=1.8) + dot(x + 9, y + 5, 3.2, fill=colour)
        elif kind == "dash":
            s += line(x, y + 5, x + 18, y + 5, stroke=colour, sw=1.6, dash="5,3")
        elif kind == "dot":
            s += dot(x + 8, y + 5, 3.6, fill=colour)
        elif kind == "ring":
            s += ring(x + 8, y + 5, 4.5, stroke=colour)
        elif kind == "bar":
            s += rect(x + 3, y - 1, 10, 12, fill=colour, stroke="none", sw=0)
        elif kind == "frame":
            s += rect(x, y - 1, 16, 12, fill=grey(170), stroke=colour, sw=2.0)
        elif kind == "tri":
            s += polygon([(x + 1, y + 10), (x + 9, y), (x + 17, y + 10)], "none", stroke=colour, sw=1.6)
        elif kind == "tridash":
            s += polygon([(x + 1, y + 10), (x + 9, y), (x + 17, y + 10)], "none", stroke=colour, sw=1.4, dash="3,2")
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.04em")
        x += 24 + 5.6 * len(label) + 28
    return s


# ------------------------------------------------------------------ FIG 01: three rulers
def fig01():
    vw, vh = 1016, 486
    s = MARKS + eyebrow(32, 40, "three scales for the same grey: light, code and lightness")
    x0, x1 = 112, 944
    W = x1 - x0
    yL, yC0, yC1, yS = 132, 240, 262, 372
    XL = lambda L: x0 + L * W
    XC = lambda c: x0 + c / 255 * W
    XS = lambda l: x0 + l / 100 * W
    n = 64
    cw = W / n
    # equal steps of light (top strip), the code bar (equal code steps), equal steps of lightness (bottom strip)
    for k in range(n):
        Lk = (k + 0.5) / n
        s += rect(x0 + k * cw, 82, cw + 0.4, 16, fill=grey(d.enc8(Lk)), stroke="none", sw=0)
    for k in range(n):
        ck = (k + 0.5) / n * 255
        s += rect(x0 + k * cw, yC0, cw + 0.4, yC1 - yC0, fill=grey(ck), stroke="none", sw=0)
    for k in range(n):
        lk = (k + 0.5) / n * 100
        Yk = ((lk + 16) / 116) ** 3 if lk > 8 else lk / d.KAPPA
        s += rect(x0 + k * cw, 410, cw + 0.4, 16, fill=grey(d.enc8(Yk)), stroke="none", sw=0)
    s += rect(x0, 82, W, 16, fill="none", stroke=LINE_SOFT, sw=0.8)
    s += rect(x0, yC0, W, yC1 - yC0, fill="none", stroke=LINE_SOFT, sw=0.8)
    s += rect(x0, 410, W, 16, fill="none", stroke=LINE_SOFT, sw=0.8)
    s += mono(x0, 74, "equal steps of light, as they look", size=8, fill=SOFT, anchor="start")
    s += mono(x0, 442, "equal steps of lightness, as they look", size=8, fill=SOFT, anchor="start")
    # rulers
    s += line(x0, yL, x1, yL, stroke=INK, sw=1.2) + line(x0, yS, x1, yS, stroke=INK, sw=1.2)
    for t in (0, 0.25, 0.5, 0.75, 1):
        s += line(XL(t), yL - 4, XL(t), yL + 4, stroke=INK, sw=1)
    for t in (0, 25, 50, 75, 100):
        s += line(XS(t), yS - 4, XS(t), yS + 4, stroke=INK, sw=1)
    s += title(32, yL + 4, "light Y", size=9)
    s += mono(32, yL + 17, "0 to 100%", size=7.5, fill=SOFT, anchor="start")
    s += title(32, (yC0 + yC1) / 2 + 4, "sRGB code", size=9)
    s += mono(32, (yC0 + yC1) / 2 + 17, "0 to 255", size=7.5, fill=SOFT, anchor="start")
    s += title(32, yS + 4, "lightness L*", size=9)
    s += mono(32, yS + 17, "0 to 100", size=7.5, fill=SOFT, anchor="start")
    # marked codes: lines from the code bar up to their light and down to their lightness
    marks = [(c, d.LIN[c], d.LSTAR[c]) for c in d.RULER_CODES]
    for c, L, l in marks:
        s += line(XC(c), yC0, XL(L), yL, stroke=INK, sw=1.1)
        s += line(XC(c), yC1, XS(l), yS, stroke=INK, sw=1.1)
        s += dot(XL(L), yL, 3.0, fill=INK) + dot(XS(l), yS, 3.0, fill=INK)
    # half of white's light, in blue
    c_half, l_half = d.enc8(0.5), d.lstar(0.5)
    s += line(XL(0.5), yL, XC(c_half), yC0, stroke=LINK, sw=1.4, dash="4,3")
    s += line(XC(c_half), yC1, XS(l_half), yS, stroke=LINK, sw=1.4, dash="4,3")
    s += dot(XL(0.5), yL, 3.2, fill=LINK) + dot(XS(l_half), yS, 3.2, fill=LINK)
    # value labels: light above its ruler, lightness below, codes on plates inside the bar
    lab_light = {40: (f"{100 * d.LIN[40]:.1f}%", "middle"), 119: (f"{100 * d.LIN[119]:.1f}%", "end"),
                 128: (f"{100 * d.LIN[128]:.1f}%", "start"), 200: (f"{100 * d.LIN[200]:.1f}%", "middle"),
                 255: ("100%", "middle")}
    for c, L, l in marks:
        t, a = lab_light[c]
        xx = XL(L) + {"middle": 0, "end": -4, "start": 4}[a]
        s += mono(xx, yL - 10, t, size=8.5, fill=INK, anchor=a, weight="600")
    s += mono(XL(0.5), yL - 10, "50%", size=8.5, fill=LINK, anchor="middle", weight="600")
    lab_ls = {40: ("middle",), 119: ("end",), 128: ("start",), 200: ("middle",), 255: ("middle",)}
    for c, L, l in marks:
        a = lab_ls[c][0]
        xx = XS(l) + {"middle": 0, "end": -4, "start": 4}[a]
        s += mono(xx, yS + 18, "100" if c == 255 else fmt(l), size=8.5, fill=INK, anchor=a, weight="600")
    s += mono(XS(l_half), yS + 18, fmt(l_half), size=8.5, fill=LINK, anchor="middle", weight="600")
    for c, L, l in marks:
        if c == 255:      # keep the plate inside the bar's right end
            s += plate(XC(c) - 6, yC1 - 6, str(c), size=8, fill=INK, bg="#ffffff", anchor="end")
        else:
            s += plate(XC(c), yC1 - 6, str(c), size=8, fill=INK, bg="#ffffff")
    s += plate(XC(c_half), yC1 - 6, fmt(c_half), size=8, fill=LINK, bg="#ffffff")
    s += note_lines(x0, 470, [("Code 119 looks halfway between black and white (L* 50) but sends 18.4% of white's light; "
                               "half of the light needs code 187.5.", MUTED)])
    return emit("01", "three-rulers", "Code, light and lightness",
                "Five codes from the patch's levels and the middle grey, joined to the light they send and the "
                "lightness they look. Computed from the sRGB and CIELAB definitions.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02: one pixel, two greys
def node_box(x, y, w, h, name, lines, stroke=INK, fill="#ffffff", name_fill=INK):
    s = rect(x, y, w, h, fill=fill, stroke=stroke, sw=1.0, rx=6)
    s += txt(x + w / 2, y + 22, name, size=12, fill=name_fill, family=SANS, weight="600")
    for k, (t, c) in enumerate(lines):
        s += mono(x + w / 2, y + 40 + 15 * k, t, size=9, fill=c)
    return s


def fig02():
    vw, vh = 1016, 412
    s = MARKS + eyebrow(32, 40, "the azure, carried from codes to Lab, and its two greys")
    bw, bh, ytop = 196, 86, 84
    xs = [32, 280, 528, 776]
    lin, xyz, labv = d.AZ_LIN, d.AZ_XYZ, d.AZ_LAB
    # box 1: the pixel, with its swatch
    s += rect(xs[0], ytop, bw, bh, fill="#ffffff", stroke=INK, sw=1.0, rx=6)
    s += swatch(xs[0] + 14, ytop + 16, 54, 54, rgb(d.AZURE))
    s += txt(xs[0] + 132, ytop + 30, "the azure", size=12, fill=INK, family=SANS, weight="600")
    s += mono(xs[0] + 132, ytop + 48, "sRGB codes", size=9, fill=SOFT)
    s += mono(xs[0] + 132, ytop + 63, "(40, 200, 255)", size=9, fill=INK)
    s += node_box(xs[1], ytop, bw, bh, "linear light", [("R, G, B", SOFT),
                  (f"({lin[0]:.4f}, {lin[1]:.4f}, {lin[2]:.4f})", INK)])
    s += node_box(xs[2], ytop, bw, bh, "CIE XYZ", [(f"({xyz[0]:.4f}, {xyz[1]:.4f}, {xyz[2]:.4f})", INK),
                  (f"Y = {xyz[1]:.4f}: luminance", LINK)])
    s += node_box(xs[3], ytop, bw, bh, "CIELAB", [("L*, a*, b*", SOFT),
                  (f"({fmt(labv[0])}, {fmt(labv[1])}, {fmt(labv[2])})", INK)])
    ym = ytop + bh / 2
    for k, (l1, l2) in enumerate([("decode", "eq. 1"), ("× matrix", "step 2"), ("∛ ratios", "step 3")]):
        xa, xb = xs[k] + bw, xs[k + 1]
        s += arrow(xa + 3, ym, xb - 3, ym, MUTED)
        s += mono((xa + xb) / 2, ym - 14, l1, size=8, fill=MUTED, weight="600")
        s += mono((xa + xb) / 2, ym + 18, l2, size=7.5, fill=SOFT)
    # bottom row: luma from the codes, luminance from Y
    yb, bh2 = 232, 104
    s += rect(xs[0], yb, bw, bh2, fill="#ffffff", stroke=ACCENT, sw=1.4, rx=6)
    s += txt(xs[0] + bw / 2, yb + 22, "luma Y′ (BGR2GRAY)", size=12, fill=ACCENT, family=SANS, weight="600")
    s += mono(xs[0] + bw / 2, yb + 41, "0.299·40 + 0.587·200", size=9, fill=INK)
    s += mono(xs[0] + bw / 2, yb + 56, "+ 0.114·255", size=9, fill=INK)
    s += mono(xs[0] + bw / 2, yb + 74, f"= {d.AZ_LUMA:.1f} → {d.cv_gray8(*d.AZURE)}", size=9.5, fill=ACCENT, weight="600")
    s += mono(xs[0] + bw / 2, yb + 91, "weights on codes", size=8, fill=SOFT)
    s += rect(xs[2], yb, bw, bh2, fill="#ffffff", stroke=LINK, sw=1.4, rx=6)
    s += txt(xs[2] + bw / 2, yb + 22, "luminance grey", size=12, fill=LINK, family=SANS, weight="600")
    s += mono(xs[2] + bw / 2, yb + 41, f"encode Y = {xyz[1]:.4f}", size=9, fill=INK)
    s += mono(xs[2] + bw / 2, yb + 56, f"1.055·Y^(1/2.4) − 0.055 = {d.encode(xyz[1]):.4f}", size=8.5, fill=INK)
    s += mono(xs[2] + bw / 2, yb + 74, f"× 255 = {d.AZ_LUMGREY:.1f} → {round(d.AZ_LUMGREY)}", size=9.5, fill=LINK, weight="600")
    s += mono(xs[2] + bw / 2, yb + 91, "weights on light", size=8, fill=SOFT)
    s += arrow(xs[0] + bw / 2, ytop + bh + 3, xs[0] + bw / 2, yb - 3, ACCENT)
    s += mono(xs[0] + bw / 2 + 8, (ytop + bh + yb) / 2 + 3, "the codes, as they are", size=8, fill=ACCENT, anchor="start")
    s += arrow(xs[2] + bw / 2, ytop + bh + 3, xs[2] + bw / 2, yb - 3, LINK)
    s += mono(xs[2] + bw / 2 + 8, (ytop + bh + yb) / 2 + 3, "Y only", size=8, fill=LINK, anchor="start")
    # side by side, with lightness
    px, py = xs[3], yb
    s += rect(px, py, bw, bh2, fill="#ffffff", stroke=RULE_SOLID, sw=1.0, rx=6)
    s += mono(px + bw / 2, py + 16, "side by side", size=8.5, fill=MUTED, weight="600")
    cells = [(rgb(d.AZURE), "azure", f"L* {fmt(labv[0])}", INK),
             (grey(d.AZ_LUMA), str(round(d.AZ_LUMA)), f"L* {fmt(d.lstar(d.AZ_LUMA_Y))}", ACCENT),
             (grey(d.AZ_LUMGREY), str(round(d.AZ_LUMGREY)), f"L* {fmt(d.lstar(d.AZ_Y))}", LINK)]
    for k, (fill, name, lt, col) in enumerate(cells):
        cx = px + 16 + k * 60
        s += swatch(cx, py + 26, 44, 40, fill, stroke=col if col != INK else LINE_SOFT, sw=1.6 if col != INK else 0.8)
        s += mono(cx + 22, py + 80, name, size=8.5, fill=col, weight="600")
        s += mono(cx + 22, py + 94, lt, size=7.5, fill=SOFT)
    s += note_lines(32, 364, [(f"The luma grey is {round(d.AZ_LUMGREY) - round(d.AZ_LUMA)} levels darker and "
                               f"{fmt(labv[0] - d.lstar(d.AZ_LUMA_Y))} units of L* below the azure; the luminance "
                               "grey sends the same light as the azure.", MUTED)])
    s += legend(vh - 24, vw, [("computed on codes", ACCENT, "line"), ("computed on light", LINK, "line")])
    return emit("02", "one-pixel-two-greys", "One pixel, two greys",
                "The azure (40, 200, 255) decoded, multiplied into XYZ and turned into Lab, with its luma and "
                "luminance greys. Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03: one blur in two encodings
def fig03():
    vw, vh = 1016, 540
    s = MARKS + eyebrow(32, 40, "row r0 of the patch, blurred with the series' Gaussian in codes and in light")
    axA = Axes(96, 92, 360, 210, (-0.4, 4.4), (0, 255))
    axB = Axes(594, 92, 360, 210, (-0.4, 4.4), (0, 0.6))
    s += axA.clip("cpA") + axB.clip("cpB")
    s += title(axA.x0, 76, "the blurred row, read as codes")
    s += title(axB.x0, 76, "the blurred row, read as light")
    s += axA.frame([], [0, 64, 128, 192, 255])
    s += axB.frame([], [0, 0.2, 0.4, 0.6], yfmt=lambda v: f"{v:.1f}")
    for ax in (axA, axB):
        for j in range(5):
            s += mono(ax.X(j), ax.y0 + ax.h + 14, f"c{j}", size=8, fill=SOFT)
    # halfway references, behind the data, labelled in the empty upper left of each plot
    s += line(axA.x0, axA.Y(d.MID_CODES), axA.x0 + axA.w, axA.Y(d.MID_CODES), stroke=ACCENT, sw=0.9, dash="3,3")
    s += mono(axA.x0 + 8, axA.Y(d.MID_CODES) - 7, "halfway in codes: 120", size=7.5, fill=ACCENT, anchor="start")
    s += line(axB.x0, axB.Y(d.MID_LIGHT), axB.x0 + axB.w, axB.Y(d.MID_LIGHT), stroke=LINK, sw=0.9, dash="3,3")
    s += mono(axB.x0 + 8, axB.Y(d.MID_LIGHT) - 7, f"halfway in light: {d.MID_LIGHT:.4f}", size=7.5, fill=LINK, anchor="start")
    series_A = [(d.BLUR_CODES, ACCENT), (d.BLUR_LIGHT_AS_CODES, LINK)]
    series_B = [(d.BLUR_CODES_AS_LIGHT, ACCENT), (d.BLUR_LIGHT, LINK)]
    for vals, col in series_A:
        s += polyline([(axA.X(j), axA.Y(v)) for j, v in enumerate(vals)], col, sw=1.8, clip="cpA")
        for j, v in enumerate(vals):
            s += dot(axA.X(j), axA.Y(v), 3.2, fill=col)
    for vals, col in series_B:
        s += polyline([(axB.X(j), axB.Y(v)) for j, v in enumerate(vals)], col, sw=1.8, clip="cpB")
        for j, v in enumerate(vals):
            s += dot(axB.X(j), axB.Y(v), 3.2, fill=col)
    # the values, as a small table under each axis, where no plotted line can reach them
    def num(v, f):
        return str(round(v)) if abs(v - round(v)) < 1e-9 else f(v)
    for ax, (a, b), f in ((axA, (d.BLUR_CODES, d.BLUR_LIGHT_AS_CODES), lambda v: fmt(v)),
                          (axB, (d.BLUR_CODES_AS_LIGHT, d.BLUR_LIGHT), lambda v: f"{v:.4f}")):
        for j in range(5):
            s += mono(ax.X(j), ax.y0 + ax.h + 32, num(a[j], f), size=8.5, fill=ACCENT, weight="600")
            s += mono(ax.X(j), ax.y0 + ax.h + 47, num(b[j], f), size=8.5, fill=LINK, weight="600")
    # the three rows as true sRGB greys
    rows = [("row r0 of the patch", d.STEP_ROW, INK), ("blurred in codes", d.BLUR_CODES, ACCENT),
            ("blurred in light", d.BLUR_LIGHT_AS_CODES, LINK)]
    cs, ys = 44, 400
    for k, (name, vals, col) in enumerate(rows):
        x = 96 + k * 300
        s += title(x, ys - 10, name, fill=col, size=9)
        for j, v in enumerate(vals):
            s += swatch(x + j * cs, ys, cs, cs, grey(v), stroke="rgba(45,49,66,0.30)")
            s += mono(x + j * cs + cs / 2, ys + cs / 2 + 3, num(v, fmt), size=7.5, fill=text_on(v), weight="500")
        s += rect(x, ys, 5 * cs, cs, fill="none", stroke=LINE_SOFT, sw=1.0)
    s += note_lines(96, ys + cs + 30, [("Each blur is symmetric in its own units: 78.2 and 161.8 sit evenly about 120; "
                                        "0.1542 and 0.4446 sit evenly about 0.2994.", MUTED)])
    s += legend(vh - 24, vw, [("blurred in codes", ACCENT, "linedot"),
                              ("decoded, blurred in light, encoded", LINK, "linedot")])
    return emit("03", "blur-in-two-encodings", "One blur, two encodings",
                "The step 40 40 40 200 200 blurred with weights 0.239, 0.522, 0.239 on codes and on decoded "
                "light, shown in both units and as greys. Computed from the definitions.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04: where the codes go
def fig04():
    vw, vh = 1016, 440
    s = MARKS + eyebrow(32, 40, "how many of the 256 codes each tenth of lightness gets")
    ax = Axes(96, 80, 840, 230, (-0.5, 9.5), (0, 70))
    s += ax.frame([], [0, 10, 20, 30, 40, 50, 60, 70], ylab="codes in the band")
    even = 25.6
    s += line(ax.x0, ax.Y(even), ax.x0 + ax.w, ax.Y(even), stroke=MUTED, sw=1.0, dash="4,3")
    s += mono(ax.x0 + ax.w + 6, ax.Y(even) - 2, "even split", size=7.5, fill=MUTED, anchor="start")
    s += mono(ax.x0 + ax.w + 6, ax.Y(even) + 9, "25.6", size=7.5, fill=MUTED, anchor="start")
    bw = 26
    for k in range(10):
        xc = ax.X(k)
        for v, col, dx in ((d.BANDS_SRGB[k], ACCENT, -bw / 2 - 2), (d.BANDS_LIN[k], LINK, bw / 2 + 2)):
            s += rect(xc + dx - bw / 2, ax.Y(v), bw, ax.Y(0) - ax.Y(v), fill=col, stroke="none", sw=0)
            if ax.Y(0) - ax.Y(v) >= 16:      # inside the bar, where the even-split line is hidden
                s += mono(xc + dx, ax.Y(v) + 12, str(v), size=8.5, fill="#ffffff", weight="600")
            else:                            # short bars sit far below the line
                s += mono(xc + dx, ax.Y(v) - 5, str(v), size=8.5, fill=col, weight="600")
        s += mono(xc, ax.y0 + ax.h + 14, f"{10 * k}–{10 * k + 10}", size=8, fill=SOFT)
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 30, "lightness L*, in tenths", size=8.5, fill=SOFT, anchor="end")
    s += note_lines(96, 364, [
        (f"Largest step between neighbouring codes: sRGB {max(d.STEPS_SRGB):.2f} L* (code 24 to 25); "
         f"linear 8-bit {max(d.STEPS_LIN):.2f} L* (code 0 to 1).", INK),
        (f"About one unit of L* is visible. Linear 8-bit coding has {sum(x > 1 for x in d.STEPS_LIN)} steps above it, "
         "all near black; sRGB has none.", MUTED)])
    s += legend(vh - 24, vw, [("sRGB codes", ACCENT, "bar"), ("linear 8-bit codes", LINK, "bar"),
                              ("even split, 256 / 10", MUTED, "dash")])
    return emit("04", "codes-per-lightness", "Where the 256 codes go",
                "Codes per tenth of CIE lightness for the sRGB curve and for linear 8-bit coding. "
                "Computed from the definitions.", "why a pixel is an encoding", vw, vh, s)


# ------------------------------------------------------------------ FIG 05: chromaticity and the weights
def fig05():
    vw, vh = 1016, 660
    s = MARKS + eyebrow(32, 40, "primaries and white fix the luminance weights")
    scale = 600
    ax = Axes(96, 70, 0.8 * scale, 0.9 * scale, (0, 0.8), (0, 0.9))
    s += ax.clip("cp5")
    s += ax.frame([0, 0.2, 0.4, 0.6, 0.8], [0, 0.2, 0.4, 0.6, 0.8], xlab="x", ylab="y",
                  xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: f"{v:.1f}", grid_y=False)
    loc = [(ax.X(x), ax.Y(y)) for _, x, y in d.LOCUS]
    s += polygon(loc, "rgba(45,49,66,0.035)", stroke="none")
    s += polyline(loc, INK, sw=1.4)
    s += line(loc[-1][0], loc[-1][1], loc[0][0], loc[0][1], stroke=SOFT, sw=1.0, dash="3,3")
    # wavelength labels along the outward normal
    pts = {w: (x, y) for w, x, y in d.LOCUS}
    cx, cy = 0.33, 0.33
    for w in (470, 480, 490, 500, 510, 520, 540, 560, 580, 600, 620):
        x, y = pts[w]
        dx, dy = x - cx, y - cy
        nrm = math.hypot(dx, dy)
        off = 0.035 if x + 0.035 * dx / nrm > 0.03 else -0.045     # labels that would cross the y axis go inside
        px, py = ax.X(x + off * dx / nrm), ax.Y(y + off * dy / nrm)
        s += dot(ax.X(x), ax.Y(y), 1.8, fill=INK)
        s += mono(px, py + 3, f"{w}", size=7.5, fill=SOFT)
    # BT.601 625-line first: it shares red and blue with BT.709, whose blue vertices are drawn last, on top
    tris = [(d.P601_625, MUTED, "4,3", 1.3), (d.P_NTSC, ACCENT, None, 1.7), (d.P709, LINK, None, 1.7)]
    for P, col, dash, sw in tris:
        s += polygon([(ax.X(x), ax.Y(y)) for x, y in P], "none", stroke=col, sw=sw, dash=dash)
        for x, y in P:
            s += dot(ax.X(x), ax.Y(y), 3.0, fill=col)
    # whites
    s += dot(ax.X(d.WP_D65[0]), ax.Y(d.WP_D65[1]), 3.4, fill=LINK)
    s += dot(ax.X(d.WP_C_CIE[0]), ax.Y(d.WP_C_CIE[1]), 3.4, fill=ACCENT)
    s += mono(ax.X(d.WP_D65[0]) + 8, ax.Y(d.WP_D65[1]) + 0, "D65", size=8, fill=LINK, anchor="start", weight="600")
    s += mono(ax.X(d.WP_C_CIE[0]) - 8, ax.Y(d.WP_C_CIE[1]) + 8, "C", size=8, fill=ACCENT, anchor="end", weight="600")
    # the 625-line green, the only vertex that differs from BT.709's
    gx, gy = d.P601_625[1]
    s += mono(ax.X(gx) - 8, ax.Y(gy) + 14, "625-line G", size=7.5, fill=MUTED, anchor="end")
    s += mono(ax.X(0.21) + 8, ax.Y(0.71) + 3, "NTSC G", size=7.5, fill=ACCENT, anchor="start")
    s += mono(ax.X(0.30) - 2, ax.Y(0.60) - 9, "709 G", size=7.5, fill=LINK, anchor="end")
    # right panel: the three standards and their weights
    rx = 640
    entries = [
        (ACCENT, None, "NTSC 1953, white C", "R (0.67, 0.33)  G (0.21, 0.71)  B (0.14, 0.08)",
         "luminance row " + " · ".join(f"{v:.4f}" for v in d.ROW_NTSC), "= BT.601's 0.299 · 0.587 · 0.114"),
        (LINK, None, "BT.709 and sRGB, white D65", "R (0.64, 0.33)  G (0.30, 0.60)  B (0.15, 0.06)",
         "luminance row " + " · ".join(f"{v:.4f}" for v in d.ROW_709), "sRGB's luminance weights"),
        (MUTED, "4,3", "BT.601 625-line, white D65", "R (0.64, 0.33)  G (0.29, 0.60)  B (0.15, 0.06)",
         "luminance row " + " · ".join(f"{v:.3f}" for v in d.ROW_625), "BT.601 still codes with 0.299 · 0.587 · 0.114"),
    ]
    for k, (col, dash, name, prim, row, note) in enumerate(entries):
        y = 110 + k * 132
        s += polygon([(rx, y + 2), (rx + 9, y - 12), (rx + 18, y + 2)], "none", stroke=col, sw=1.6, dash=dash)
        s += title(rx + 28, y, name, fill=col, size=9.5)
        s += mono(rx + 28, y + 20, prim, size=8, fill=MUTED, anchor="start")
        s += mono(rx + 28, y + 40, row, size=8.5, fill=INK, anchor="start", weight="600")
        s += mono(rx + 28, y + 58, note, size=8, fill=col if col != MUTED else SOFT, anchor="start")
    s += note_lines(rx, 520, [("Each luminance row is the middle row of the", SOFT),
                              ("matrix that the primaries and the white fix", SOFT),
                              ("(equation 2). Horseshoe: the spectral colours,", SOFT),
                              ("labelled in nm, from the CIE's 1931 2° table", SOFT),
                              ("(CC BY-SA 4.0). The 625-line triangle shares", SOFT),
                              ("BT.709's red and blue.", SOFT)], size=8, gap=14)
    return emit("05", "primaries-and-weights", "Primaries fix the weights",
                "CIE 1931 xy diagram with the NTSC 1953, BT.709 and BT.601 625-line primaries and whites, and "
                "the luminance weights each implies. Spectral locus from the CIE's table.", "grey weights", vw, vh, s)


# ------------------------------------------------------------------ FIG 06: luma against luminance
def fig06():
    vw, vh = 1016, 476
    s = MARKS + eyebrow(32, 40, "BGR2GRAY's luma against the grey of equal luminance, for nine colours")
    cw = 104
    x0 = 40
    zero_y, k_px = 306, 1.0
    s += line(x0, zero_y, x0 + 9 * cw, zero_y, stroke=MUTED, sw=1.0)
    for k, (name, t) in enumerate(d.SWATCHES):
        cx = x0 + k * cw + cw / 2
        luma, lg = d.GREYS[name]
        s += swatch(cx - 32, 78, 64, 52, rgb(t))
        s += mono(cx, 146, name, size=8.5, fill=INK, weight="600")
        s += mono(cx, 159, f"({t[0]}, {t[1]}, {t[2]})", size=7.5, fill=SOFT)
        s += swatch(cx - 42, 176, 38, 46, grey(luma), stroke=ACCENT, sw=2.0)
        s += swatch(cx + 4, 176, 38, 46, grey(lg), stroke=LINK, sw=2.0)
        s += mono(cx - 23, 238, str(round(luma)), size=9, fill=ACCENT, weight="600")
        s += mono(cx + 23, 238, str(round(lg)), size=9, fill=LINK, weight="600")
        diff = luma - lg
        h = diff * k_px
        if abs(h) > 0.4:
            s += rect(cx - 9, min(zero_y, zero_y - h), 18, abs(h), fill=ACCENT, stroke="none", sw=0)
        ly = zero_y - h - 6 if diff > 0 else zero_y - h + 13
        if abs(h) < 1:
            ly = zero_y - 6
        s += mono(cx, ly, "0" if abs(diff) < 0.05 else fmt(diff), size=8.5, fill=INK, weight="600")
    s += title(x0, 268, "luma minus the luminance grey, in codes", fill=INK, size=9)
    s += mono(x0 + 9 * cw, 268, "bar height: 1 px per code", size=7.5, fill=SOFT, anchor="end")
    s += note_lines(x0, 412, [
        (f"Over all {d.SWEEP['colours']:,} 8-bit colours: from {fmt(d.SWEEP['luma601_minus_lumgrey_min'][0])} "
         f"(pure green) to +{d.SWEEP['luma601_minus_lumgrey_max'][0]:.1f} (255, 172, 255); exactly 0 on every grey.", INK)])
    s += legend(vh - 24, vw, [("luma: BT.601 weights on codes", ACCENT, "frame"),
                              ("luminance grey: decoded, weighted, encoded", LINK, "frame"),
                              ("luma minus luminance grey", ACCENT, "bar")])
    return emit("06", "luma-against-luminance", "Luma against luminance",
                "BT.601 luma and the luminance-matched grey for nine colours, with their difference and the "
                "range over all 8-bit colours. Computed from the definitions.", "how wrong is luma", vw, vh, s)


# ------------------------------------------------------------------ FIG 07: Lab and its white
def fig07():
    vw, vh = 1016, 560
    s = MARKS + eyebrow(32, 40, "the same azure and the same white in three Labs")
    k = 5.6
    ax = Axes(110, 80, 60 * k, 70 * k, (-50, 10), (-65, 5))
    s += ax.frame([-50, -40, -30, -20, -10, 0, 10], [-60, -40, -20, 0], xlab="a*", ylab="b*",
                  xfmt=lambda v: fmt(v, 0), yfmt=lambda v: fmt(v, 0), grid_y=False)
    X, Y = ax.X, ax.Y
    s += line(X(0), ax.y0, X(0), ax.y0 + ax.h, stroke=RULE_SOLID, sw=0.8, dash="2,3")
    s += line(ax.x0, Y(0), ax.x0 + ax.w, Y(0), stroke=RULE_SOLID, sw=0.8, dash="2,3")
    s += mono(ax.x0 + 6, Y(0) - 6, "green ← a* → red", size=7.5, fill=SOFT, anchor="start")
    s += mono(X(0) + 6, Y(-62), "blue ↓ b*", size=7.5, fill=SOFT, anchor="start")
    p65, p50, psk, wsk = d.AZ_LAB_D65_CSS, d.AZ_LAB_D50, d.AZ_LAB_SK50, d.WHITE_LAB_SK50

    def toward(p, q, back):
        """End an arrow `back` px short of point q, so its head meets the marker's edge."""
        x1, y1, x2, y2 = X(p[1]), Y(p[2]), X(q[1]), Y(q[2])
        L = math.hypot(x2 - x1, y2 - y1)
        return x1, y1, x2 - (x2 - x1) * back / L, y2 - (y2 - y1) * back / L

    s += arrow(*toward(p65, p50, 5.5), LINK)
    s += arrow(*toward(p65, psk, 5.5), ACCENT)
    s += arrow(*toward((100, 0, 0), wsk, 6.5), ACCENT)
    s += dot(X(p65[1]), Y(p65[2]), 4.2, fill=INK)
    s += dot(X(p50[1]), Y(p50[2]), 4.2, fill=LINK)
    s += dot(X(psk[1]), Y(psk[2]), 4.2, fill=ACCENT)
    s += ring(X(0), Y(0), 5, stroke=INK)
    s += ring(X(wsk[1]), Y(wsk[2]), 5, stroke=ACCENT)
    s += mono(X(p65[1]) + 9, Y(p65[2]) - 6, f"D65 ({fmt(p65[1])}, {fmt(p65[2])})", size=8, fill=INK, anchor="start", weight="600")
    s += mono(X(p50[1]) - 8, Y(p50[2]) + 4, f"D50 ({fmt(p50[1])}, {fmt(p50[2])})", size=8, fill=LINK, anchor="end", weight="600")
    s += mono(X(psk[1]) + 9, Y(psk[2]) + 4, f"({fmt(psk[1])}, {fmt(psk[2])})", size=8, fill=ACCENT, anchor="start", weight="600")
    s += mono(X(0) + 9, Y(0) + 15, "white (0, 0)", size=8, fill=INK, anchor="start", weight="600")
    s += mono(X(wsk[1]) - 9, Y(wsk[2]) + 4, f"white ({fmt(wsk[1])}, {fmt(wsk[2])})", size=8, fill=ACCENT, anchor="end", weight="600")
    # right panel, with the pixel itself
    rx = 540
    s += swatch(rx, 74, 30, 30, rgb(d.AZURE))
    s += title(rx + 42, 86, "the azure (40, 200, 255)", size=9.5)
    s += mono(rx + 42, 101, "a* and b* in the plot; L* in the list", size=8, fill=SOFT, anchor="start")
    rows = [
        (INK, ["D65: OpenCV, scikit-image, MATLAB"], f"azure ({fmt(p65[0])}, {fmt(p65[1])}, {fmt(p65[2])})",
         "sRGB's own white; the default in all three"),
        (LINK, ["D50 by Bradford adaptation: CSS"], f"azure ({fmt(p50[0])}, {fmt(p50[1])}, {fmt(p50[2])})",
         f"{d.DE_65_50:.1f} ΔE from the D65 Lab; white stays (100, 0, 0)"),
        (ACCENT, ["D50 without adaptation:", 'scikit-image\'s illuminant="D50"'],
         f"azure ({fmt(psk[0])}, {fmt(psk[1])}, {fmt(psk[2])})", f"white (100, {fmt(wsk[1])}, {fmt(wsk[2])}): visibly blue"),
    ]
    y = 150
    for col, names, val, note in rows:
        s += dot(rx + 6, y - 4, 4.2, fill=col)
        for j, nm in enumerate(names):
            s += title(rx + 20, y + 16 * j, nm, fill=col, size=9.5)
        y += 16 * (len(names) - 1)
        s += mono(rx + 20, y + 20, val, size=8.5, fill=INK, anchor="start", weight="600")
        s += mono(rx + 20, y + 38, note, size=8, fill=MUTED, anchor="start")
        y += 92
    s += note_lines(rx, 444, [("Lightness barely moves; a* and b* do. Each Lab is", SOFT),
                              ("correct for its own white, so a Lab number means", SOFT),
                              ("little without it.", SOFT)], size=8, gap=14)
    s += legend(vh - 24, vw, [("azure", INK, "dot"), ("sRGB white", INK, "ring"),
                              ("adapted to D50", LINK, "line"), ("white swapped, not adapted", ACCENT, "line")])
    return emit("07", "lab-and-its-white", "One pixel, three Labs",
                "The azure and sRGB white in the a*b* plane under D65, under CSS's Bradford-adapted D50, and under "
                "scikit-image's unadapted D50. Computed from the definitions.", "what Lab adds", vw, vh, s)


# ------------------------------------------------------------------ FIG 08: chords under the curve
def fig08():
    vw, vh = 1016, 500
    s = MARKS + eyebrow(32, 40, "the encode curve lies above its chords: averaging codes is darker than averaging light")
    ax = Axes(96, 72, 520, 320, (0, 1), (0, 255))
    s += ax.clip("cp8")
    s += ax.frame([0, 0.25, 0.5, 0.75, 1], [0, 64, 128, 192, 255], xlab="linear light L", ylab="sRGB code",
                  xfmt=lambda v: f"{v:.2f}")
    curve = [(ax.X(L), ax.Y(d.enc8(L))) for L in [i / 400 for i in range(401)]]
    s += polyline(curve, LINK, sw=2.0, clip="cp8")
    # chord A: codes 40 and 200
    La, Lb = d.LIN[40], d.LIN[200]
    s += line(ax.X(La), ax.Y(40), ax.X(Lb), ax.Y(200), stroke=ACCENT, sw=1.6)
    s += dot(ax.X(La), ax.Y(40), 3.2, fill=INK) + dot(ax.X(Lb), ax.Y(200), 3.2, fill=INK)
    xm = d.MID_LIGHT
    s += line(ax.X(xm), ax.Y(d.MID_CODES), ax.X(xm), ax.Y(d.enc8(xm)), stroke=INK, sw=1.0, dash="2,2")
    s += dot(ax.X(xm), ax.Y(d.MID_CODES), 3.6, fill=ACCENT) + dot(ax.X(xm), ax.Y(d.enc8(xm)), 3.6, fill=LINK)
    # chord B: codes 0 and 255
    s += line(ax.X(0), ax.Y(0), ax.X(1), ax.Y(255), stroke=ACCENT, sw=1.4, dash="5,3")
    s += line(ax.X(0.5), ax.Y(d.STRIPE_CODES), ax.X(0.5), ax.Y(d.STRIPE_LIGHT_CODE), stroke=INK, sw=1.0, dash="2,2")
    s += dot(ax.X(0.5), ax.Y(d.STRIPE_CODES), 3.6, fill=ACCENT) + dot(ax.X(0.5), ax.Y(d.STRIPE_LIGHT_CODE), 3.6, fill=LINK)
    # point labels, placed off the lines
    s += mono(ax.X(La) + 8, ax.Y(40) + 16, "code 40", size=8, fill=INK, anchor="start")
    s += mono(ax.X(Lb) + 8, ax.Y(200) + 14, "code 200", size=8, fill=INK, anchor="start")
    s += mono(ax.X(xm) + 8, ax.Y(d.MID_CODES) + 14, "120", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.X(xm) - 8, ax.Y(d.enc8(xm)) - 8, fmt(d.enc8(xm)), size=8.5, fill=LINK, anchor="end", weight="600")
    s += mono(ax.X(0.5) + 8, ax.Y(d.STRIPE_CODES) + 14, "127.5", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.X(0.5) - 8, ax.Y(d.STRIPE_LIGHT_CODE) - 8, fmt(d.STRIPE_LIGHT_CODE), size=8.5, fill=LINK, anchor="end", weight="600")
    # right panel
    rx = 668
    items = [
        (title(rx, 110, "chord from code 40 to code 200", fill=ACCENT, size=9.5), None),
        (mono(rx, 130, f"average light {d.MID_LIGHT:.4f}", size=8.5, fill=MUTED, anchor="start"), None),
        (mono(rx, 147, "average of the codes: 120", size=8.5, fill=ACCENT, anchor="start", weight="600"), None),
        (mono(rx, 164, f"code of the average light: {fmt(d.enc8(xm))}", size=8.5, fill=LINK, anchor="start", weight="600"), None),
        (mono(rx, 181, f"code 120 sends {100 * d.dec8(120):.1f}% of white, not {100 * xm:.1f}%", size=8, fill=SOFT, anchor="start"), None),
        (title(rx, 228, "chord from code 0 to code 255", fill=ACCENT, size=9.5), None),
        (mono(rx, 248, "one-pixel black and white stripes", size=8.5, fill=MUTED, anchor="start"), None),
        (mono(rx, 265, "average of the codes: 127.5", size=8.5, fill=ACCENT, anchor="start", weight="600"), None),
        (mono(rx, 282, f"code of the average light: {fmt(d.STRIPE_LIGHT_CODE)}", size=8.5, fill=LINK, anchor="start", weight="600"), None),
        (mono(rx, 299, f"code 127.5 sends {100 * d.STRIPE_CODES_LIGHT:.1f}% of white, not 50%", size=8, fill=SOFT, anchor="start"), None),
    ]
    s += "".join(t for t, _ in items)
    s += note_lines(rx, 346, [("A concave curve lies above every chord, so", MUTED),
                              ("for non-negative weights the average of codes", MUTED),
                              ("is at most the code of the average light.", MUTED)], size=8, gap=14)
    s += legend(vh - 24, vw, [("sRGB encode", LINK, "line"), ("chord: an average of codes", ACCENT, "line"),
                              ("the same average done in light", LINK, "dot")])
    return emit("08", "chords-under-the-curve", "Why averaging codes darkens",
                "The sRGB encode curve with the chords from code 40 to 200 and from 0 to 255, and the code of "
                "the average light above each chord's midpoint. Computed from the definitions.",
                "which operations need linear light", vw, vh, s)


# ------------------------------------------------------------------ FIG 09: the tooling map
def fig09():
    vw, vh = 1016, 604
    s = eyebrow(32, 40, "one pixel, four libraries: mapped from source and documentation, not run")
    cols = [("", 32), ("OpenCV", 196), ("scikit-image", 406), ("Pillow", 616), ("MATLAB", 790)]
    y0 = 76
    for h, x in cols:
        s += mono(x, y0, h, size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, y0 + 10, vw - 32, y0 + 10, stroke=RULE_SOLID)
    rows = [
        ("grey call", "cvtColor BGR2GRAY", "rgb2gray", 'convert("L")', "rgb2gray"),
        ("grey weights", "0.299, 0.587, 0.114", "0.2125, 0.7154, 0.0721", "0.299, 0.587, 0.114", "0.298936…, 0.587043…, 0.114021…"),
        ("decodes first?", "no: luma, 158", "no: luma, 0.6665", "no: luma, 158", "no: luma, 158.44"),
        ("docs call it", "Gray, Y", "luminance", "luma", "luminance (E′y)"),
        ("XYZ", "BGR2XYZ: no decode", "rgb2xyz: decodes", "—", "—"),
        ("Lab", "BGR2Lab: decodes, undocumented", "rgb2lab: decodes", "—", "rgb2lab: decodes"),
        ("Lab white", "D65, fixed", "D65; others not adapted", "—", "D65 default; d50, icc"),
        ("resize, blur", "on the values given", "on the values given", "on the values given", "decode first with rgb2lin"),
        ("pinned", "802cf95; 4.10, 4.14, 5.0", "b700edc, 0.26.0", "12.3.0", "R2026b"),
    ]
    traps = {"no: luma, 158", "no: luma, 0.6665", "no: luma, 158.44", "luminance", "luminance (E′y)",
             "BGR2XYZ: no decode", "D65; others not adapted", "on the values given"}
    blue = {"rgb2xyz: decodes", "rgb2lab: decodes", "BGR2Lab: decodes, undocumented"}
    for k, (what, *cells) in enumerate(rows):
        y = y0 + 38 + k * 50
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 22}" width="{vw - 56}" height="50" fill="rgba(45,49,66,0.03)"/>'
        s += eyebrow(32, y + 4, what, fill=SOFT, size=8)
        for text, (_, x) in zip(cells, cols[1:]):
            col = ACCENT if text in traps else (LINK if text in blue else INK)
            s += mono(x, y + 4, text, size=8.5, fill=col, anchor="start", weight="600" if col != INK else "400")
    s += mono(32, vh - 34, "Tangerine: the call weighs codes, or its documentation says otherwise. Blue: the call decodes "
              "sRGB first and so works on light. — : not covered here.", size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 18, "Values are for the azure (40, 200, 255); scikit-image's are on its 0-to-1 float scale.",
              size=8, fill=SOFT, anchor="start")
    return emit("09", "tooling-map", "The tooling map",
                "Grey weights, decoding, XYZ, Lab and resizing in OpenCV, scikit-image, Pillow and MATLAB. None of "
                "it was executed.", "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
