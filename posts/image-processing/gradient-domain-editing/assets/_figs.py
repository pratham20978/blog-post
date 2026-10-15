#!/usr/bin/env python3
"""Figures 01-10 for gradient-domain-editing.

Every value drawn is computed in _data.py: the patch's region and ring, the nine equations, exact
Gauss-Seidel sweeps, one V-cycle, four fills of the hole, the closed-form sweep counts, Fattal's factor,
the attenuated square, the tiled row, and the libraries read from source. Nothing is measured and nothing
loads an image. _data.py's asserts hold every number drawn here to the article.
Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SANS, SOFT,
                    emit, eyebrow, mono, txt)
import _data as d


# ------------------------------------------------------------------ drawing helpers (Part 12's set)
def fmt(v, nd=1):
    v = float(v)
    if abs(v - round(v)) < 1e-9:
        s = f"{round(v):,}"
    else:
        s = f"{v:,.{nd}f}"
    return s.replace("-", "−")


def blend(rgb, a, paper=(245, 245, 245)):
    r, g, b = (round(paper[i] * (1 - a) + rgb[i] * a) for i in range(3))
    return f"#{r:02x}{g:02x}{b:02x}"


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


def path(dpath, stroke=MUTED, sw=1.2, marker=None, dash=None):
    m = f' marker-end="url(#{marker})"' if marker else ""
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{dpath}" fill="none" stroke="{stroke}" stroke-width="{sw}"{dd}{m}/>'


def polyline(pts, stroke, sw=1.6, dash=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}{o}/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None):
    s = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{s}/>'


def note_lines(x, y, items, size=8.5, gap=16, anchor="start"):
    out = ""
    for k, (t, c) in enumerate(items):
        if t:
            out += mono(x, y + k * gap, t, size=size, fill=c, anchor=anchor,
                        weight="600" if c in (INK, LINK, ACCENT) else "400")
    return out


def title(x, y, s, fill=INK, anchor="start", size=9.5):
    """A panel title in mono, not uppercased, so positions like (r2, c1) keep their case."""
    return mono(x, y, s, size=size, fill=fill, anchor=anchor, weight="600")


def caption(x, y, s, fill=SOFT, size=8, anchor="middle"):
    return mono(x, y, s, size=size, fill=fill, anchor=anchor)


def symbol(x, y, s, size=16, fill=MUTED):
    return txt(x, y, s, size=size, fill=fill, family=SANS, weight="500")


MARKS = f"""<defs>
    <marker id="ai" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{INK}"/></marker>
    <marker id="al" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
    <marker id="aa" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
    <marker id="am" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
    <pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="1" y1="0" x2="1" y2="6" stroke="rgba(45,49,66,0.22)" stroke-width="1.1"/>
    </pattern>
  </defs>"""


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr, xmap=None, ymap=None):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr
        self.xmap = xmap or (lambda v: v)
        self.ymap = ymap or (lambda v: v)

    def X(self, x):
        a, b = self.xmap(self.xr[0]), self.xmap(self.xr[1])
        return self.x0 + (self.xmap(x) - a) / (b - a) * self.w

    def Y(self, y):
        a, b = self.ymap(self.yr[0]), self.ymap(self.yr[1])
        return self.y0 + self.h - (self.ymap(y) - a) / (b - a) * self.h

    def clip(self, cid):
        return (f'<clipPath id="{cid}"><rect x="{self.x0}" y="{self.y0}" width="{self.w}" '
                f'height="{self.h}"/></clipPath>')

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid_y=True, grid_x=False):
        s = ""
        for v in yt:
            yy = self.Y(v)
            if grid_y:
                s += line(self.x0, yy, self.x0 + self.w, yy, stroke=RULE, sw=0.8)
            s += mono(self.x0 - 8, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            xx = self.X(v)
            if grid_x:
                s += line(xx, self.y0, xx, self.y0 + self.h, stroke=RULE, sw=0.8)
            s += mono(xx, self.y0 + self.h + 15, xfmt(v), size=8, fill=SOFT)
        s += line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, stroke=RULE_SOLID)
        s += line(self.x0, self.y0, self.x0, self.y0 + self.h, stroke=RULE_SOLID)
        if xlab:
            s += mono(self.x0 + self.w, self.y0 + self.h + 32, xlab, size=8.5, fill=SOFT, anchor="end")
        if ylab:
            s += mono(self.x0, self.y0 - 12, ylab, size=8.5, fill=SOFT, anchor="start")
        return s


# ------------------------------------------------------------------ cells for this post
WHITE = "#ffffff"
INK_RGB, ACC_RGB, LINK_RGB = (45, 49, 66), (235, 108, 54), (46, 90, 168)
CELL_STROKE = "rgba(45,49,66,0.30)"
UNUSED = blend(INK_RGB, 0.06)
OMEGA_FILL = WHITE


def grey_fill(v):
    """High value = bright (series rule); values below 0 or above 255 are clamped for the fill."""
    t = max(0.0, min(1.0, float(v) / 255))
    return blend(INK_RGB, 0.88 * (1 - t) + 0.02)


def grey_ink(v):
    return WHITE if float(v) < 133 else INK


def err_fill(e, emax=255.0):
    """Error size: one blue ramp, deeper = larger, whatever the sign (the sign is printed)."""
    a = min(1.0, abs(float(e)) / emax)
    return blend(LINK_RGB, 0.06 + 0.62 * a) if abs(float(e)) > 1e-9 else WHITE


def err_ink(e, emax=255.0):
    return WHITE if abs(float(e)) / emax > 0.62 else INK


def vcell(x, y, w, h, value, fill, tcolor=INK, size=9, weight="500", nd=1, stroke=CELL_STROKE, sw=0.8):
    s = (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" '
         f'stroke="{stroke}" stroke-width="{sw}" shape-rendering="crispEdges"/>')
    if value is not None:
        s += mono(x + w / 2, y + h / 2 + size * 0.36, value if isinstance(value, str) else fmt(value, nd),
                  size=size, fill=tcolor, weight=weight)
    return s


def grid3(x0, y0, cs, vals, fill_fn, ink_fn, size=9, nd=1, frame=True):
    s = ""
    for k, v in enumerate(vals):
        r, c = divmod(k, 3)
        s += vcell(x0 + c * cs, y0 + r * cs, cs, cs, v, fill_fn(v), ink_fn(v), size=size, nd=nd)
    if frame:
        s += rect(x0, y0, 3 * cs, 3 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    return s


def labels_rc(x, y, cs, n=5, m=5, r0=0, c0=0):
    s = ""
    for j in range(m):
        s += mono(x + j * cs + cs / 2, y - 7, f"c{c0 + j}", size=7.5, fill=SOFT)
    for i in range(n):
        s += mono(x - 8, y + i * cs + cs / 2 + 3, f"r{r0 + i}", size=7.5, fill=SOFT, anchor="end")
    return s


def framed5(x0, y0, cs, frame_vals, inner_vals, size=8.5, neg_mark=False, omega=True, inner_nd=1):
    """A 5x5 grid: the ring from frame_vals (5x5), the 3x3 interior from inner_vals (row-major 9),
    corners drawn as unused. Grey shading by value, high = bright."""
    s = ""
    for i in range(5):
        for j in range(5):
            x, y = x0 + j * cs, y0 + i * cs
            if (i, j) in ((0, 0), (0, 4), (4, 0), (4, 4)):
                s += vcell(x, y, cs, cs, None, UNUSED)
                s += rect(x, y, cs, cs, fill="url(#hatch)", stroke="none", sw=0)
                continue
            if 1 <= i <= 3 and 1 <= j <= 3:
                v = float(inner_vals[3 * (i - 1) + (j - 1)])
                s += vcell(x, y, cs, cs, v, grey_fill(v), grey_ink(v), size=size, nd=inner_nd)
                if neg_mark and v < 0:
                    s += rect(x + 2, y + 2, cs - 4, cs - 4, fill="none", stroke=ACCENT, sw=2.0)
            else:
                v = float(frame_vals[i][j])
                s += vcell(x, y, cs, cs, v, grey_fill(v), grey_ink(v), size=size)
    if omega:
        s += rect(x0 + cs, y0 + cs, 3 * cs, 3 * cs, fill="none", stroke=LINK, sw=2.2)
    s += rect(x0, y0, 5 * cs, 5 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    return s


def legend5(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like this post's marks."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, kind in items:
        if kind == "grey":
            s += rect(x, y - 1, 16, 12, fill=grey_fill(120), stroke=CELL_STROKE, sw=0.8)
        elif kind == "white":
            s += rect(x, y - 1, 16, 12, fill=WHITE, stroke=CELL_STROKE, sw=0.8)
        elif kind == "unused":
            s += rect(x, y - 1, 16, 12, fill=UNUSED, stroke=CELL_STROKE, sw=0.8)
            s += rect(x, y - 1, 16, 12, fill="url(#hatch)", stroke="none", sw=0)
        elif kind == "omega":
            s += rect(x + 1, y, 14, 10, fill="none", stroke=LINK, sw=2.0)
        elif kind == "neg":
            s += rect(x, y - 1, 16, 12, fill=grey_fill(0), stroke=CELL_STROKE, sw=0.8)
            s += rect(x + 1.5, y + 0.5, 13, 9, fill="none", stroke=ACCENT, sw=1.8)
        elif kind == "err":
            s += rect(x, y - 1, 16, 12, fill=err_fill(150), stroke=CELL_STROKE, sw=0.8)
        elif kind == "lap":
            s += rect(x, y - 1, 16, 12, fill=WHITE, stroke=CELL_STROKE, sw=0.8)
            s += mono(x + 8, y + 8, "∇²", size=7.5, fill=ACCENT, weight="600")
        elif kind.startswith("line:"):
            s += line(x, y + 5, x + 18, y + 5, stroke=kind[5:], sw=2.0)
        elif kind.startswith("dash:"):
            s += line(x, y + 5, x + 18, y + 5, stroke=kind[5:], sw=1.6, dash="5,3")
        elif kind.startswith("dot:"):
            s += line(x, y + 5, x + 18, y + 5, stroke=kind[4:], sw=1.6, dash="1.5,2.5")
        elif kind.startswith("pt:"):
            s += dot(x + 8, y + 5, 3.6, fill=kind[3:])
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.04em")
        x += 24 + 5.6 * len(label) + 28
    return s


def arrow(x1, y1, x2, y2, colour=MUTED, sw=1.4):
    m = {INK: "ai", LINK: "al", ACCENT: "aa", MUTED: "am"}[colour]
    return line(x1, y1, x2, y2, stroke=colour, sw=sw, marker=m)


def plate(x, y, s, size=8.5, fill=MUTED, anchor="middle", weight="400"):
    """Text on an opaque plate, for labels that sit beside lines in a plot."""
    w = 0.62 * size * len(str(s)) + 10
    x0 = {"middle": x - w / 2, "start": x - 5, "end": x - w + 5}[anchor]
    return (f'<rect x="{x0:.1f}" y="{y - size - 2:.1f}" width="{w:.1f}" height="{size + 7}" rx="2" fill="{PAPER}"/>'
            + mono(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight))


P = d.PATCH
XS = [float(v) for v in d.XSTAR]


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 452
    s = MARKS + eyebrow(32, 40, "what gradient-domain editing keeps: twelve boundary values and nine laplacians")
    cs, y0 = 46, 112
    xa, xb = 96, 600
    s += title(xa, y0 - 30, "the patch: 25 pixels")
    for i in range(5):
        for j in range(5):
            v = P[i][j]
            s += vcell(xa + j * cs, y0 + i * cs, cs, cs, v, grey_fill(v), grey_ink(v), size=10)
    s += rect(xa, y0, 5 * cs, 5 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    s += labels_rc(xa, y0, cs)
    # the operation
    ax0, ax1, ay = xa + 5 * cs + 34, xb - 34, y0 + 2.5 * cs
    s += arrow(ax0, ay, ax1, ay, colour=MUTED)
    s += note_lines((ax0 + ax1) / 2, ay - 40, [("keep the ring", INK), ("and the Laplacian;", INK),
                                               ("throw the nine away", ACCENT)], size=8.5, gap=14, anchor="middle")
    s += caption((ax0 + ax1) / 2, ay + 26, "Laplacian = four neighbours")
    s += caption((ax0 + ax1) / 2, ay + 40, "minus four times the pixel")
    # what is kept
    s += title(xb, y0 - 30, "kept: 12 values + 9 Laplacians")
    lap = {p: d.LAP[i] for i, p in enumerate(d.OMEGA)}
    for i in range(5):
        for j in range(5):
            x, y = xb + j * cs, y0 + i * cs
            if (i, j) in ((0, 0), (0, 4), (4, 0), (4, 4)):
                s += vcell(x, y, cs, cs, None, UNUSED)
                s += rect(x, y, cs, cs, fill="url(#hatch)", stroke="none", sw=0)
            elif (i, j) in lap:
                s += vcell(x, y, cs, cs, None, WHITE)
                s += mono(x + cs / 2, y + 15, "f = ?", size=7.5, fill=SOFT)
                s += mono(x + cs / 2, y + cs - 11, fmt(lap[(i, j)]), size=10, fill=ACCENT, weight="600")
            else:
                v = P[i][j]
                s += vcell(x, y, cs, cs, v, grey_fill(v), grey_ink(v), size=10)
    s += rect(xb + cs, y0 + cs, 3 * cs, 3 * cs, fill="none", stroke=LINK, sw=2.2)
    s += rect(xb, y0, 5 * cs, 5 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    s += labels_rc(xb, y0, cs)
    s += note_lines(xb + 5 * cs + 22, y0 + 18, [
        ("Ω: rows r1–r3,", LINK), ("columns c1–c3", LINK), ("", MUTED),
        ("ring: 40, 40, 200", MUTED), ("top and bottom;", MUTED), ("40 left, 200 right", MUTED), ("", MUTED),
        ("corners: unused", SOFT), ("by the stencil", SOFT)], size=8.5, gap=15)
    s += note_lines(96, y0 + 5 * cs + 40, [
        ("the Laplacians sum to −215: the net flow through the ring, all of it at the impulse's left edge", MUTED)])
    s += legend5(vh - 30, vw, [("pixel value, kept", "grey"), ("unknown; its Laplacian kept", "lap"),
                               ("the region Ω", "omega"), ("corner, unused", "unused")])
    return emit("01", "what-is-kept", "What gradient-domain editing keeps",
                "The patch's 3×3 interior is erased; its Laplacian and the twelve frame pixels that touch it are "
                "kept. Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 488
    s = MARKS + eyebrow(32, 40, "nine equations, one system: every row is the five-point stencil")
    cs, y0, x0 = 28, 118, 182
    names = ["r1c1", "r1c2", "r1c3", "r2c1", "r2c2", "r2c3", "r3c1", "r3c2", "r3c3"]
    s += title(x0, y0 - 46, "A: 4 on the diagonal, −1 between neighbours")
    for j, n in enumerate(names):
        s += mono(x0 + j * cs + cs / 2, y0 - 8, n[1] + n[3], size=7, fill=SOFT)
    for i in range(9):
        s += mono(x0 - 8, y0 + i * cs + cs / 2 + 3, names[i], size=7.5, fill=SOFT, anchor="end")
        for j in range(9):
            a = d.A[i][j]
            if a == 4:
                s += vcell(x0 + j * cs, y0 + i * cs, cs, cs, "4", blend(INK_RGB, 0.10), INK, size=9, weight="600")
            elif a == -1:
                s += vcell(x0 + j * cs, y0 + i * cs, cs, cs, "−1", blend(LINK_RGB, 0.16), LINK, size=8.5)
            else:
                s += vcell(x0 + j * cs, y0 + i * cs, cs, cs, None, WHITE)
    s += rect(x0, y0, 9 * cs, 9 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    cw = 52
    cols = [("x: the patch", XS, "pix"), ("known", [float(v) for v in d.BND], "plain"),
            ("Laplacian", [float(v) for v in d.LAP], "lap"), ("b", [float(v) for v in d.B], "b")]
    xs = [x0 + 9 * cs + 46, None, None, None]
    xs[1] = xs[0] + cw + 70
    xs[2] = xs[1] + cw + 50
    xs[3] = xs[2] + cw + 50
    syms = [("×", x0 + 9 * cs + 23), ("=", xs[0] + cw + 35), ("−", xs[1] + cw + 25), ("=", xs[2] + cw + 25)]
    for (head, vals, kind), xx in zip(cols, xs):
        s += title(xx + cw / 2, y0 - 22, head, anchor="middle")
        for i, v in enumerate(vals):
            y = y0 + i * cs
            if kind == "pix":
                s += vcell(xx, y, cw, cs, v, grey_fill(v), grey_ink(v), size=9)
            elif kind == "lap":
                s += vcell(xx, y, cw, cs, v, WHITE, ACCENT, size=9, weight="600")
            elif kind == "b":
                s += vcell(xx, y, cw, cs, v, blend(INK_RGB, 0.05), INK, size=9, weight="600")
            else:
                s += vcell(xx, y, cw, cs, v, WHITE, MUTED, size=9)
        s += rect(xx, y0, cw, 9 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    for sym, xx in syms:
        s += symbol(xx, y0 + 4.5 * cs + 6, sym, size=18, fill=INK)
    s += caption(xs[1] + cw + 25, y0 + 9 * cs + 22, "b = known neighbours − Laplacian", fill=MUTED, size=8.5)
    s += note_lines(182, y0 + 9 * cs + 56, [
        ("row r2c1, the impulse:  4 × 255 − 40 − 40 − 40 = 900 = 40 + 860", INK),
        ("A is symmetric and positive definite, so the patch is the only solution: the nine pixels come back", MUTED)])
    return emit("02", "nine-equations", "The nine equations as one system",
                "Each row of A is the five-point stencil with the known neighbours moved into b. Worked by hand.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 584
    s = MARKS + eyebrow(32, 40, "three gauss-seidel sweeps from zero: the error loses its jumps, then halves")
    cs, ytop, ybot = 40, 120, 296
    xs = [110, 330, 550, 770]
    heads = ["start: all zero", "after sweep 1", "after sweep 2", "after sweep 3"]
    s += mono(32, ytop + 1.5 * cs + 3, "iterate", size=8.5, fill=MUTED, anchor="start", weight="600")
    s += mono(32, ybot + 1.5 * cs - 4, "error =", size=8.5, fill=MUTED, anchor="start", weight="600")
    s += mono(32, ybot + 1.5 * cs + 10, "iterate", size=8.5, fill=MUTED, anchor="start", weight="600")
    s += mono(32, ybot + 1.5 * cs + 24, "− patch", size=8.5, fill=MUTED, anchor="start", weight="600")
    for k, x0 in enumerate(xs):
        it = [float(v) for v in d.SWEEPS[k]]
        er = d.err(d.SWEEPS[k])
        s += title(x0 + 1.5 * cs, ytop - 22, heads[k], anchor="middle")
        s += grid3(x0, ytop, cs, it, grey_fill, grey_ink, size=8.5)
        s += grid3(x0, ybot, cs, er, err_fill, err_ink, size=8.5)
        s += mono(x0 + 1.5 * cs, ybot + 3 * cs + 20, f"largest error {fmt(d.SWEEP_ERR[k])}", size=8.5,
                  fill=INK, weight="600")
        if k < 3:
            s += mono(x0 + 1.5 * cs, ybot + 3 * cs + 36, f"smoothest pattern {round(100 * d.SHARES[k])}%",
                      size=8, fill=MUTED)
        if k > 0:
            xm = x0 - 50
            s += arrow(xm - 18, ytop + 1.5 * cs, xm + 18, ytop + 1.5 * cs, colour=MUTED)
    s += note_lines(110, ybot + 3 * cs + 82, [
        ("each update: (b + the current unknown neighbours) / 4, in row order, newest values first", INK),
        ("from the third sweep on the largest error halves each sweep: 15.5, 7.8, 3.9, 1.9, 0.97, then 0.49 after nine",
         MUTED)])
    s += legend5(vh - 30, vw, [("value, high = bright", "grey"), ("error size, deeper = larger", "err")])
    return emit("03", "three-sweeps", "Three Gauss–Seidel sweeps from zero",
                "Iterates and errors after each sweep. The jumps in the error go first; what is left is a bowl that "
                "halves per sweep. Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 560
    s = MARKS + eyebrow(32, 40, "one v-cycle: two sweeps and one coarse equation leave half what three sweeps leave")
    cs = 36
    g = 3 * cs
    A_ = (48, 100)            # after the pre-sweep (error)
    B_ = (238, 226)           # residual
    C_ = (442, 352)           # coarse point (box)
    D_ = (636, 226)           # correction
    E_ = (836, 100)           # after the post-sweep (error)
    s += title(A_[0] + g / 2, A_[1] - 16, "1. one sweep: error", anchor="middle")
    s += grid3(A_[0], A_[1], cs, d.err(d.SWEEPS[1]), err_fill, err_ink, size=8)
    s += caption(A_[0] + g / 2, A_[1] + g + 16, f"largest {fmt(d.SWEEP_ERR[1])}", fill=MUTED)
    s += title(B_[0] + g / 2, B_[1] + g + 20, "2. residual b − Ax", anchor="middle")
    s += grid3(B_[0], B_[1], cs, [float(v) for v in d.V_RES], lambda v: WHITE, lambda v: INK, size=8)
    cw, ch = 132, 74
    s += rect(C_[0], C_[1], cw, ch, fill=blend(ACC_RGB, 0.10), stroke=ACCENT, sw=1.2, rx=4)
    s += mono(C_[0] + cw / 2, C_[1] + 20, "coarse point", size=8, fill=SOFT)
    s += mono(C_[0] + cw / 2, C_[1] + 40, f"r = {fmt(d.V_RC)}", size=9.5, fill=INK, weight="600")
    s += mono(C_[0] + cw / 2, C_[1] + 60, f"e = r / (3/4) = {fmt(d.V_EC)}", size=8.5, fill=ACCENT, weight="600")
    s += title(C_[0] + cw / 2, C_[1] + ch + 20, "3. one equation", anchor="middle")
    corr = [float(w * d.V_EC) for w in d.PW]
    s += title(D_[0] + g / 2, D_[1] - 16, "4. correction, bilinear", anchor="middle")
    s += grid3(D_[0], D_[1], cs, corr, lambda v: blend(ACC_RGB, 0.08 + 0.4 * v / 106.8), lambda v: INK, size=8)
    s += title(E_[0] + g / 2, E_[1] - 16, "5. add, sweep: error", anchor="middle")
    s += grid3(E_[0], E_[1], cs, d.err(d.V1), err_fill, err_ink, size=8)
    s += caption(E_[0] - 12, E_[1] + g / 2 + 3, f"largest {fmt(d.V1_ERR)}", fill=INK, anchor="end")
    # connectors: horizontal out of a side, vertical into a top or bottom edge
    def hv(x1, y1, x2, y2, label=None, lx=None, ly=None, colour=MUTED):
        r = 8
        sy = 1 if y2 > y1 else -1
        dp = f"M {x1} {y1} H {x2 - r} Q {x2} {y1} {x2} {y1 + sy * r} V {y2}"
        out = path(dp, stroke=colour, sw=1.3, marker={MUTED: "am", ACCENT: "aa"}[colour])
        if label:
            out += note_lines(lx, ly, label, size=8, gap=12)
        return out
    s += hv(A_[0] + g, A_[1] + g / 2, B_[0] + g / 2, B_[1],
            [("what the", SOFT), ("equations lack", SOFT)], A_[0] + g + 14, A_[1] + g / 2 + 22)
    s += hv(B_[0] + g, B_[1] + g / 2, C_[0] + cw / 2, C_[1],
            [("restrict:", SOFT), ("1, 2, 4 over 16", SOFT)], B_[0] + g + 14, B_[1] + g / 2 + 22)
    s += hv(C_[0] + cw, C_[1] + ch / 2, D_[0] + g / 2, D_[1] + g, None, None, None, colour=ACCENT)
    s += note_lines(C_[0] + cw + 14, C_[1] + ch / 2 + 20, [("prolong:", SOFT), ("4 × its transpose", SOFT)], size=8, gap=12)
    s += hv(D_[0] + g, D_[1] + g / 2, E_[0] + g / 2, E_[1] + g, None, None, None, colour=ACCENT)
    s += note_lines(D_[0] + g + 14, D_[1] + g / 2 + 22, [("add it,", SOFT), ("then sweep", SOFT)], size=8, gap=12)
    s += note_lines(48, 470, [
        (f"three plain sweeps: largest error {fmt(d.SWEEP_ERR[3])}  ·  one V-cycle: {fmt(d.V1_ERR)}  ·  "
         f"two V-cycles: {d.maxabs(d.err(d.V2)):.2f}", INK),
        ("3/4 is restriction × A × interpolation on one point; writing the stencil afresh at spacing 2 gives 1, and 27.1",
         MUTED)])
    s += legend5(vh - 30, vw, [("error size, deeper = larger", "err"), ("residual", "white"),
                               ("coarse step", "line:" + ACCENT)])
    return emit("04", "one-v-cycle", "One V-cycle on nine unknowns",
                "A sweep, the residual, one coarse equation, the correction interpolated back, and a sweep. Worked "
                "by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 470
    s = MARKS + eyebrow(32, 40, "four fills of one hole: the frame sets the level, the guidance sets the shape")
    cs, y0 = 36, 118
    xs = [52, 300, 548, 796]
    sh = [[float(v) for v in row] for row in d.SHADOW]
    panels = [
        (xs[0], P, d.FILL_MEMBRANE, "membrane: no guidance", ["the spike is lost,", "the step smeared"], False),
        (xs[1], P, d.FILL_GUIDED, "guided by the patch", ["the patch, exactly"], False),
        (xs[2], sh, d.FILL_SHADOW, "shadowed frame, in codes", ["differences kept:", "−40 at (r2, c2)"], True),
        (xs[3], sh, d.FILL_LOG, "shadowed frame, in log", ["ratios kept: the", "shadowed patch, 8 40 51"], False),
    ]
    for x0, frame, inner, head, cap, neg in panels:
        s += title(x0 + 2.5 * cs, y0 - 26, head, anchor="middle")
        s += framed5(x0, y0, cs, frame, inner, size=8, neg_mark=neg)
        for k, c in enumerate(cap):
            s += caption(x0 + 2.5 * cs, y0 + 5 * cs + 20 + 14 * k, c, fill=MUTED if k == 0 else INK)
    s += labels_rc(xs[0], y0, cs)
    s += note_lines(52, y0 + 5 * cs + 78, [
        ("the shadowed copy is the same scene at a fifth of the light: 8, 40 and 51 for 40, 200 and 255", MUTED),
        ("in log a fifth of the light is the constant −ln 5 all round the frame, so the membrane is flat", INK)])
    s += legend5(vh - 30, vw, [("frame, fixed", "grey"), ("the region Ω, solved", "omega"),
                               ("below black", "neg"), ("corner, unused", "unused")])
    return emit("05", "four-fills", "Four fills of one hole",
                "The membrane, the guided fill, and the clone into the shadowed copy in codes and in log. Worked by "
                "hand.", "cloning", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 504
    s = MARKS + eyebrow(32, 40, "sweeps per digit: plain sweeps grow with the square of the width, over-relaxed ones with the width")
    lg = math.log10
    ax = Axes(120, 92, 620, 296, (3, 4095), (1, 1e7), xmap=lg, ymap=lg)
    xt = [3, 31, 255, 1023, 4095]
    yt = [1, 10, 100, 1e3, 1e4, 1e5, 1e6, 1e7]
    yl = {1: "1", 10: "10", 100: "100", 1e3: "1k", 1e4: "10k", 1e5: "100k", 1e6: "1M", 1e7: "10M"}
    s += ax.clip("c6")
    s += ax.frame(xt, yt, xlab="region width N (pixels), log scale", ylab="sweeps per decimal digit, log scale",
                  xfmt=lambda v: f"{v:,}", yfmt=lambda v: yl[v])
    Ns = [3 * (4095 / 3) ** (i / 400) for i in range(401)]
    gs = [(ax.X(n), ax.Y(d.sweeps_per_digit(d.gs_rho(n)))) for n in Ns]
    sor = [(ax.X(n), ax.Y(d.sweeps_per_digit(d.sor_rho(n)))) for n in Ns]
    s += f'<g clip-path="url(#c6)">' + polyline(gs, INK, sw=2.0) + polyline(sor, LINK, sw=2.0, dash="6,3") + "</g>"
    for n, v, col in [(3, d.SPD[3], INK), (1023, d.SPD[1023], INK),
                      (3, d.sweeps_per_digit(d.sor_rho(3)), LINK), (1023, d.sweeps_per_digit(d.sor_rho(1023)), LINK)]:
        s += dot(ax.X(n), ax.Y(v), 3.8, fill=col)
    s += note_lines(770, 132, [("Gauss–Seidel", INK), ("cos²(π/(N+1)) per sweep", MUTED),
                               ("≈ 0.233 (N+1)² sweeps", MUTED),
                               (f"N = 3: {d.SPD[3]:.1f}", INK), (f"N = 1,023: {round(d.SPD[1023]):,}", INK)],
                    size=8.5, gap=14)
    s += note_lines(770, 252, [("SOR at the best ω", LINK), ("ω = 2/(1 + sin(π/(N+1)))", MUTED),
                               ("≈ 0.37 (N+1) sweeps", MUTED),
                               (f"N = 3: {d.sweeps_per_digit(d.sor_rho(3)):.1f}", LINK),
                               (f"N = 1,023: {round(d.sweeps_per_digit(d.sor_rho(1023)))}", LINK)], size=8.5, gap=14)
    s += note_lines(120, 448, [
        ("multigrid: a fixed number of V-cycles, each about 4/3 of a fine sweep's work, whatever N (Brandt 1977)", INK)])
    s += legend5(vh - 30, vw, [("Gauss–Seidel", "line:" + INK), ("optimal SOR", "dash:" + LINK),
                               ("N = 3 and N = 1,023", "pt:" + INK)])
    return emit("06", "sweeps-per-digit", "Sweeps per digit against region width",
                "Closed forms for the smoothest error pattern on an N × N region with a fixed frame. Plotted from "
                "the formulas, not measured.", "solvers", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 500
    s = MARKS + eyebrow(32, 40, "fattal's factor: gradients above alpha shrink, gradients below it grow")
    lg = math.log10
    ax = Axes(120, 92, 560, 296, (0.1, 100), (0.3, 2.0), xmap=lg, ymap=lg)
    xt = [0.1, 1, 10, 25, 100]
    yt = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    s += ax.clip("c7")
    s += f'<rect x="{ax.X(1):.1f}" y="{ax.y0}" width="{ax.X(100) - ax.X(1):.1f}" height="{ax.h}" fill="rgba(45,49,66,0.035)"/>'
    s += ax.frame(xt, yt, xlab="gradient magnitude in units of α, log scale", ylab="φ, log scale",
                  xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    s += line(ax.X(1), ax.y0, ax.X(1), ax.y0 + ax.h, stroke=RULE_SOLID, sw=1.0, dash="3,3")
    s += line(ax.x0, ax.Y(1), ax.x0 + ax.w, ax.Y(1), stroke=RULE_SOLID, sw=1.0, dash="3,3")
    styles = {0.8: (MUTED, "5,3"), 0.85: (ACCENT, None), 0.9: (MUTED, "1.5,2.5")}
    xs = [0.1 * 1000 ** (i / 200) for i in range(201)]
    body = ""
    for beta, (col, dash) in styles.items():
        body += polyline([(ax.X(x), ax.Y(x ** (beta - 1))) for x in xs], col, sw=2.0 if beta == 0.85 else 1.6, dash=dash)
    s += f'<g clip-path="url(#c7)">{body}</g>'
    for beta in (0.8, 0.85, 0.9):
        p = d.HDR1[beta][0]
        col = ACCENT if beta == 0.85 else MUTED
        s += dot(ax.X(25), ax.Y(p), 3.8, fill=col)
    s += mono(ax.X(1) + 6, ax.y0 + 14, "shrinks →", size=8, fill=SOFT, anchor="start")
    s += mono(ax.X(1) - 6, ax.y0 + 14, "← grows", size=8, fill=SOFT, anchor="end")
    s += note_lines(712, 120, [("at 25α:", INK), (f"β = 0.9, dotted: {d.HDR1[0.9][0]:.3f}", MUTED),
                               (f"β = 0.85: {d.HDR1[0.85][0]:.3f}", ACCENT),
                               (f"β = 0.8, dashed: {d.HDR1[0.8][0]:.3f}", MUTED)], size=8.5, gap=15)
    s += note_lines(712, 208, [("the step row:", INK), ("log rise ln 5 = 1.609", MUTED),
                               ("central differences 0.805", MUTED), ("mean 0.322, α 0.0322", MUTED),
                               ("the step sits at 25α", MUTED)], size=8.5, gap=15)
    s += note_lines(712, 302, [("at β = 0.85:", INK), ("1.609 × 0.617 = 0.993", ACCENT),
                               ("5:1 becomes 2.70:1", ACCENT)], size=8.5, gap=15)
    s += note_lines(120, 446, [("φ = (magnitude / α)^(β − 1), α = 0.1 × the average gradient magnitude; one pyramid level, "
                                "as the patch is smaller than the 32 px the method's coarsest level needs", MUTED)])
    s += legend5(vh - 30, vw, [("β = 0.85", "line:" + ACCENT), ("β = 0.8", "dash:" + MUTED),
                               ("β = 0.9", "dot:" + MUTED)])
    return emit("07", "attenuation-factor", "Fattal's attenuation factor",
                "φ against gradient magnitude for three values of β, with the step row's step at 25α. Plotted from "
                "the closed form.", "hdr", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 470
    s = MARKS + eyebrow(32, 40, "after attenuation the field is no image's gradient: one square does not close")
    cs, x0, y0 = 50, 72, 128
    s += title(x0, y0 - 34, "rows r1 and r2 of the patch")
    for i, r in enumerate((1, 2)):
        for j in range(5):
            v = P[r][j]
            s += vcell(x0 + j * cs, y0 + i * cs, cs, cs, v, grey_fill(v), grey_ink(v), size=10)
    s += rect(x0, y0, 5 * cs, 2 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    s += rect(x0 + 2 * cs + 2, y0 + 2, cs - 4, 2 * cs - 4, fill="none", stroke=LINK, sw=2.0)
    s += labels_rc(x0, y0, cs, n=2, m=5, r0=1)
    # central-difference spans for (r1, c2) and (r2, c2)
    yb1 = y0 + 2 * cs + 26
    s += line(x0 + 1.5 * cs, yb1, x0 + 3.5 * cs, yb1, stroke=MUTED, sw=1.2)
    s += line(x0 + 1.5 * cs, yb1 - 5, x0 + 1.5 * cs, yb1 + 5, stroke=MUTED, sw=1.2)
    s += line(x0 + 3.5 * cs, yb1 - 5, x0 + 3.5 * cs, yb1 + 5, stroke=MUTED, sw=1.2)
    s += note_lines(x0, yb1 + 26, [
        ("central difference at c2: from c1 to c3", MUTED),
        (f"r1: 40 → 200, magnitude {d.MAG2[1][2]:.3f}, φ {d.PHI_R1C2:.3f}", INK),
        (f"r2: 255 → 200, magnitude {d.MAG2[2][2]:.3f}, φ {d.PHI_R2C2:.3f}", ACCENT),
        ("(α = 0.0406, β = 0.85; the impulse sits at c1)", SOFT)], size=8.5, gap=16)
    # the square
    sx, sy, side = 560, 120, 200
    pts = {"r1c2": (sx, sy), "r1c3": (sx + side, sy), "r2c3": (sx + side, sy + side), "r2c2": (sx, sy + side)}
    s += title(sx + side / 2, sy - 34, "the attenuated log differences", anchor="middle")
    gap = 14
    s += arrow(sx + gap, sy, sx + side - gap, sy, colour=INK, sw=1.8)
    s += arrow(sx + side, sy + gap, sx + side, sy + side - gap, colour=MUTED, sw=1.4)
    s += arrow(sx + side - gap, sy + side, sx + gap, sy + side, colour=ACCENT, sw=1.8)
    s += arrow(sx, sy + side - gap, sx, sy + gap, colour=MUTED, sw=1.4)
    for k, (xx, yy) in pts.items():
        s += dot(xx, yy, 5.5, fill=PAPER, stroke=INK)
    s += mono(sx - 12, sy - 10, "(r1, c2)", size=8.5, fill=SOFT, anchor="end")
    s += mono(sx + side + 12, sy - 10, "(r1, c3)", size=8.5, fill=SOFT, anchor="start")
    s += mono(sx + side + 12, sy + side + 18, "(r2, c3)", size=8.5, fill=SOFT, anchor="start")
    s += mono(sx - 12, sy + side + 18, "(r2, c2)", size=8.5, fill=SOFT, anchor="end")
    s += mono(sx + side / 2, sy - 10, f"right along r1: +{d.GX_R1:.3f}", size=8.5, fill=INK, weight="600")
    s += mono(sx + side / 2, sy + side + 22, f"left along r2: −{d.GX_R2:.3f}", size=8.5, fill=ACCENT, weight="600")
    s += mono(sx + side + 14, sy + side / 2 + 3, "down c3: 0", size=8.5, fill=MUTED, anchor="start")
    s += mono(sx - 14, sy + side / 2 + 3, "up c2: 0", size=8.5, fill=MUTED, anchor="end")
    s += mono(sx + side / 2, sy + side / 2 - 4, "sum round the loop", size=8.5, fill=SOFT)
    s += mono(sx + side / 2, sy + side / 2 + 14, f"{d.CIRC:.3f}".replace("-", "−"), size=13, fill=INK, weight="600")
    s += note_lines(560, sy + side + 62, [
        (f"r1's step becomes {math.exp(d.GX_R1):.2f}:1 and r2's {math.exp(d.GX_R2):.2f}:1, with nothing changing up c2 or c3",
         MUTED),
        ("an image's differences round any loop add to zero: least squares splits the −0.337", INK)], size=8.5, gap=16)
    s += legend5(vh - 30, vw, [("pixel value", "grey"), ("column c2, where the factor is read", "omega"),
                               ("row r1", "line:" + INK), ("row r2", "line:" + ACCENT)])
    return emit("08", "not-a-gradient", "A square that does not close",
                "Around one square of the patch the attenuated differences sum to −0.337, so no image has them. "
                "Worked by hand.", "hdr", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 486
    s = MARKS + eyebrow(32, 40, "seamless tiling: the seam's jump becomes a slope across the tile")
    cs, x0 = 50, 128
    rows = [("tiled as it is", [float(v) for v in d.STEP_ROW] * 3, 110),
            ("after Pérez's rule", [float(v) for v in d.TILE_ROW] * 3, 248)]
    for head, vals, y0 in rows:
        s += title(x0, y0 - 18, head)
        for j, v in enumerate(vals):
            s += vcell(x0 + j * cs, y0, cs, cs, v, grey_fill(v), grey_ink(v), size=10)
        s += rect(x0, y0, 15 * cs, cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
        for t in (1, 2):
            xx = x0 + 5 * t * cs
            s += line(xx, y0 - 8, xx, y0 + cs + 8, stroke=LINK, sw=2.0)
            jump = vals[5 * t] - vals[5 * t - 1]
            col = ACCENT if abs(jump) > 0 else INK
            s += mono(xx, y0 + cs + 24, f"seam: {fmt(jump)}", size=8.5, fill=col, weight="600")
    # the membrane that was added, per tile
    ym = 248 + cs + 64
    s += title(x0, ym - 8, "added per tile: a straight line from +80 to −80")
    mem = [float(d.TILE_ROW[i] - d.STEP_ROW[i]) for i in range(5)]
    for t in range(3):
        for j, v in enumerate(mem):
            s += vcell(x0 + (5 * t + j) * cs, ym + 4, cs, 26, f"{'+' if v > 0 else ''}{fmt(v)}", WHITE,
                       MUTED, size=8.5)
    s += rect(x0, ym + 4, 15 * cs, 26, fill="none", stroke="rgba(45,49,66,0.45)", sw=0.8)
    s += note_lines(x0, ym + 58, [("both ends become (40 + 200) / 2 = 120; the step shrinks from 160 to 120 and the flat runs "
                                   "fall 40 a pixel", MUTED)])
    s += legend5(vh - 30, vw, [("pixel value", "grey"), ("tile boundary", "line:" + LINK)])
    return emit("09", "seamless-tiling", "Seamless tiling of the step row",
                "The row repeated three times before and after Pérez's averaging rule. Worked by hand.",
                "tiling", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 588
    s = eyebrow(32, 40, "where each piece lives: mapped from source and documentation, not run")
    cols = [("call", 32), ("solves on", 236), ("solver", 410), ("guidance", 588), ("watch for", 792)]
    y0 = 78
    for h, x in cols:
        s += mono(x, y0, h, size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, y0 + 10, vw - 32, y0 + 10, stroke=RULE_SOLID)
    # (call lines, region lines, solver lines, guidance lines, watch lines); first call line bold
    rows = [
        (["seamlessClone", "NORMAL_CLONE", "MIXED_CLONE", "MONOCHROME_TRANSFER"],
         ["the mask's", "bounding box"], ["sine transform,", "exact"],
         ["src in the mask, dst out", "pair with larger abs(gx − gy)", "grey src in the mask", ""],
         ["mask eroded 3 px: under", "7 px clones nothing; MIXED", "drops spikes and 45° edges;", "p is the box centre"]),
        (["illuminationChange", "alpha 0.2, beta 0.4"], ["the whole image"], ["sine transform,", "exact"],
         ["Pérez's eq. 16", "on the codes"], ["not in log; α fixed,", "not 0.2 × the mean"]),
        (["textureFlattening", "30, 45, 3"], ["the whole image"], ["sine transform,", "exact"],
         ["kept only where", "Canny marks an edge"], ["", ""]),
        (["createTonemapMantiuk"], ["the whole image"], ["≤ 100 conjugate-", "gradient iterations"],
         ["contrast on every", "pyramid level"], ["OpenCV has no", "Fattal operator"]),
        (["regionfill (MATLAB)"], ["the masked region"], ["not documented"], ["none: the membrane"],
         ["spike lost,", "step smeared"]),
        (["scipy.sparse.linalg", "spsolve"], ["any region you", "assemble"], ["direct, sparse"],
         ["equation (2),", "as you assemble it"], ["the assembly", "is yours"]),
        (["scipy.fft.dstn", "type=1"], ["a rectangle"], ["direct,", "O(n log n)"], ["b, as you build it"],
         ["rectangles only"]),
    ]
    traps = {"mask eroded 3 px: under", "7 px clones nothing; MIXED", "drops spikes and 45° edges;",
             "p is the box centre", "not in log; α fixed,", "not 0.2 × the mean", "OpenCV has no", "Fattal operator"}
    y = y0 + 34
    for k, (calls, region, solver, guide, watch) in enumerate(rows):
        n = max(len(calls), len(region), len(solver), len(guide), len(watch))
        hgt = 26 + 15 * (n - 1) + 14
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 20}" width="{vw - 56}" height="{hgt}" fill="rgba(45,49,66,0.03)"/>'
        for j, c in enumerate(calls):
            s += mono(32, y + 15 * j, c, size=8.5 if j == 0 else 8, fill=INK if j == 0 else SOFT, anchor="start",
                      weight="600" if j == 0 else "400")
        for j, c in enumerate(region):
            s += mono(236, y + 15 * j, c, size=8.5, fill=INK, anchor="start")
        for j, c in enumerate(solver):
            direct = "exact" in " ".join(solver) or "direct" in " ".join(solver)
            s += mono(410, y + 15 * j, c, size=8.5, fill=LINK if direct else INK, anchor="start")
        for j, c in enumerate(guide):
            if c:
                s += mono(588, y + 15 * j, c, size=8.5, fill=INK, anchor="start")
        for j, c in enumerate(watch):
            if c:
                s += mono(792, y + 15 * j, c, size=8.5, fill=ACCENT if c in traps else MUTED, anchor="start",
                          weight="600" if c in traps else "400")
        y += hgt
    s += mono(32, vh - 50, "From 4.11.0 seamlessClone, colorChange, illuminationChange and textureFlattening erode and invert a "
              "1-channel mask in place;", size=8, fill=ACCENT, anchor="start")
    s += mono(32, vh - 34, "OpenCV clamps results to 0–255 and truncates. Tangerine: a departure from Pérez et al. or a trap. "
              "Blue: a direct solve, no iteration.", size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 18, "OpenCV read at 802cf95, 4.10.0–4.14.0 and 5.0.0; MATLAB R2026b and SciPy 1.18.0 documentation. "
              "None of it was executed.", size=8, fill=SOFT, anchor="start")
    return emit("10", "tooling-map", "The tooling map",
                "OpenCV's photo module, MATLAB and SciPy: where each solves, how, with which guidance, and what to "
                "watch for. None of it was executed.", "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
