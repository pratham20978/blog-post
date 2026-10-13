#!/usr/bin/env python3
"""Figures 01-13 for scale-space-and-sift.

Every value drawn is computed in _data.py from the definitions: the closed-form scale space of the
series' patch enlarged by 7 (and by 5 and 14), the DoG octave, the 26-neighbour test, the quadratic
fit, both rejection tests, the normalised Laplacian, the fixed-level maps and the scale-adapted
Harris measure; Figure 12's histograms come from _replay.py, a plain-Python replay of OpenCV's SIFT
rules (sift.simd.hpp at commit 802cf95). Nothing is measured and nothing loads an image. _data.py's
asserts hold every number drawn here to the article, so a figure that disagrees with the text fails
to build.
Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SOFT,
                    cell, emit, eyebrow, mono, txt)
import _data as d

SER1, SER2, SER3 = "#7c8f6f", "#5e7a9b", "#b8915a"
N = 5          # the shared patch's size, for labels_rc's default

# ------------------------------------------------------------------ drawing helpers
def fmt(v, nd=1):
    if abs(v - round(v)) < 1e-9:
        s = f"{round(v):,}"
    else:
        s = f"{v:,.{nd}f}"
    return s.replace("-", "−")


def shade_rect(x, y, w, h, t, stroke="rgba(45,49,66,0.30)", sw=0.8):
    """High value = bright (series rule): t = 1 is paper, t = 0 is ink."""
    t = max(0.0, min(1.0, t))
    a = 0.88 * (1 - t) + 0.02
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{PAPER}"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="rgba(45,49,66,{a:.3f})" stroke="{stroke}" stroke-width="{sw}"/>')


def ink_for(t):
    return "#ffffff" if t < 0.52 else INK


def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, marker=None, cap=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    c = f' stroke-linecap="{cap}"' if cap else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{m}{c}{o}/>')


def polyline(pts, stroke, sw=1.6, dash=None, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}{o}/>')


def polygon(pts, fill, stroke="none", sw=0.8, op=None):
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}"{o} '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None):
    s = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{s}/>'


def ring(x, y, rr=5, stroke=INK, sw=1.6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{PAPER}" stroke="{stroke}" stroke-width="{sw}"/>'


def ellipse(cx, cy, rx, ry, ang=0.0, fill="none", stroke=INK, sw=1.6, op=None, dash=None):
    """Semi-axis rx along angle `ang` (degrees, clockwise on screen, image convention)."""
    o = f' fill-opacity="{op}"' if op is not None else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{max(rx, 0.01):.2f}" ry="{max(ry, 0.01):.2f}" '
            f'transform="rotate({ang:.2f} {cx:.1f} {cy:.1f})" fill="{fill}"{o} stroke="{stroke}" '
            f'stroke-width="{sw}"{d}/>')


def glyph(cx, cy, l1, l2, ang, scale, stroke=INK, fill=None, op=0.14, sw=1.6):
    """A tensor as an ellipse with semi-axes scale * sqrt(lambda); rank 1 as a capped line."""
    a, b = scale * math.sqrt(max(l1, 0)), scale * math.sqrt(max(l2, 0))
    if b < 0.75:
        dx, dy = a * math.cos(math.radians(ang)), a * math.sin(math.radians(ang))
        return line(cx - dx, cy - dy, cx + dx, cy + dy, stroke=stroke, sw=3.2, cap="round")
    return ellipse(cx, cy, a, b, ang, fill=fill or stroke, stroke=stroke, sw=sw, op=op)


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


def legend2(y, vw, items):
    """Legend whose swatches are drawn exactly like the marks they name."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for item in items:
        label, colour, kind = item[:3]
        op = item[3] if len(item) > 3 else None
        if kind in ("line", "dash", "dot-line"):
            d = {"line": "", "dash": ' stroke-dasharray="5,3"', "dot-line": ' stroke-dasharray="1.5,2.5"'}[kind]
            s += (f'<line x1="{x}" y1="{y + 5}" x2="{x + 18}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.8"{d}' + (f' stroke-opacity="{op}"' if op else "") + '/>')
        elif kind == "dot":
            s += dot(x + 8, y + 5, 4, fill=colour)
        elif kind == "ring":
            s += ring(x + 8, y + 5, 4.5, stroke=colour)
        elif kind == "fill":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke=colour, sw=0.8, op=op or 0.85)
        elif kind == "area":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke="none", sw=0, op=op)
        elif kind == "outline":
            s += rect(x, y - 1, 16, 12, fill="none", stroke=colour, sw=1.8)
        elif kind == "dashbox":
            s += rect(x, y - 1, 16, 12, fill="none", stroke=colour, sw=1.6, dash="3,2")
        elif kind == "hatch":
            s += rect(x, y - 1, 16, 12, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8)
            s += rect(x, y - 1, 16, 12, fill="url(#hatch)", stroke="none", sw=0)
        elif kind == "ell":
            s += ellipse(x + 8, y + 5, 8, 4.2, 0, fill=colour, stroke=colour, sw=1.4, op=op or 0.14)
        elif kind == "rank1":
            s += line(x + 1, y + 5, x + 17, y + 5, stroke=colour, sw=3.2, cap="round")
        elif kind == "hbar":
            s += line(x + 3, y + 5, x + 15, y + 5, stroke=colour, sw=2.4, cap="round")
        elif kind == "vbar":
            s += line(x + 8, y - 1, x + 8, y + 11, stroke=colour, sw=2.4, cap="round")
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.04em")
        x += 24 + 5.6 * len(label) + 30
    return s


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr, xmap=None):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr
        self.xmap = xmap or (lambda v: v)

    def X(self, x):
        a, b = self.xmap(self.xr[0]), self.xmap(self.xr[1])
        return self.x0 + (self.xmap(x) - a) / (b - a) * self.w

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


def labels_rc(x, y, cs, n=N, cols=None):
    s = ""
    for j, name in enumerate(cols or [f"c{j}" for j in range(n)]):
        s += mono(x + j * cs + cs / 2, y - 7, name, size=7.5, fill=SOFT)
    for i in range(n):
        s += mono(x - 8, y + i * cs + cs / 2 + 3, f"r{i}", size=7.5, fill=SOFT, anchor="end")
    return s


MARKS = f"""<defs>
    <marker id="aw" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="#ffffff"/></marker>
    <marker id="ai" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{INK}"/></marker>
    <marker id="al" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{LINK}"/></marker>
    <marker id="aa" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/></marker>
    <marker id="am" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/></marker>
    <pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="1" y1="0" x2="1" y2="7" stroke="rgba(45,49,66,0.34)" stroke-width="1.3"/>
      <line x1="4.5" y1="0" x2="4.5" y2="7" stroke="rgba(255,255,255,0.55)" stroke-width="1.3"/>
    </pattern>
  </defs>"""


def arrow(x1, y1, x2, y2, colour, sw=1.5):
    m = {INK: "ai", LINK: "al", ACCENT: "aa", MUTED: "am", "#ffffff": "aw"}[colour]
    return line(x1, y1, x2, y2, stroke=colour, sw=sw, marker=m)



# ------------------------------------------------------------------ helpers for this post
def legend3(y, vw, items, x=108):
    """legend2 plus the kinds this post needs: dashring, cross, diamond."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for item in items:
        label, colour, kind = item[:3]
        op = item[3] if len(item) > 3 else None
        if kind in ("line", "dash", "dot-line"):
            dd = {"line": "", "dash": ' stroke-dasharray="5,3"', "dot-line": ' stroke-dasharray="1.5,2.5"'}[kind]
            s += (f'<line x1="{x}" y1="{y + 5}" x2="{x + 18}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.8"{dd}/>')
        elif kind == "dot":
            s += dot(x + 8, y + 5, 3.6, fill=colour)
        elif kind == "ring":
            s += ring(x + 8, y + 5, 5, stroke=colour, sw=1.8)
        elif kind == "dashring":
            s += (f'<circle cx="{x + 8}" cy="{y + 5}" r="5" fill="none" stroke="{colour}" stroke-width="1.6" '
                  f'stroke-dasharray="2.5,2"/>')
        elif kind == "cross":
            s += line(x + 4, y + 1, x + 12, y + 9, stroke=colour, sw=1.8) + line(x + 4, y + 9, x + 12, y + 1, stroke=colour, sw=1.8)
        elif kind == "diamond":
            s += polygon([(x + 8, y), (x + 13, y + 5), (x + 8, y + 10), (x + 3, y + 5)], colour)
        elif kind == "area":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke="none", sw=0, op=op)
        elif kind == "outline":
            s += rect(x, y - 1, 16, 12, fill="none", stroke=colour, sw=1.6)
        elif kind == "grey":
            for k, a in enumerate((0.75, 0.45, 0.12)):
                s += rect(x + k * 6, y - 1, 6, 12, fill=f"rgba(45,49,66,{a})", stroke="none", sw=0)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.04em")
        x += 24 + 5.6 * len(label) + 30
    return s


def blend(rgb, a, paper=(245, 245, 245)):
    """An opaque colour equal to rgb at alpha a over the paper, so touching cells cannot double up."""
    r, g, b = (round(a * c + (1 - a) * p) for c, p in zip(rgb, paper))
    return f"#{r:02x}{g:02x}{b:02x}"


def grey_fill(v):
    a = 0.88 * (1 - max(0.0, min(255.0, v)) / 255) + 0.02
    return blend((45, 49, 66), a)


def div_fill(v, vmax, gamma=1.0):
    t = min(1.0, (abs(v) / vmax) ** gamma)
    return blend((46, 90, 168) if v < 0 else (235, 108, 54), 0.03 + 0.85 * t)


def grid_map(x0, y0, cw, ch, M, fill_fn, frame=True):
    """A matrix of values as cells, merged into runs of equal colour (smaller SVG)."""
    s = f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{cw * len(M[0]):.2f}" height="{ch * len(M):.2f}" fill="{PAPER}"/>'
    for i, row in enumerate(M):
        j = 0
        while j < len(row):
            f = fill_fn(row[j])
            k = j + 1
            while k < len(row) and fill_fn(row[k]) == f:
                k += 1
            s += (f'<rect x="{x0 + j * cw:.2f}" y="{y0 + i * ch:.2f}" width="{(k - j) * cw + 0.35:.2f}" '
                  f'height="{ch + 0.35:.2f}" fill="{f}" shape-rendering="crispEdges"/>')
            j = k
    if frame:
        s += rect(x0, y0, cw * len(M[0]), ch * len(M), fill="none", stroke="rgba(45,49,66,0.45)", sw=0.8)
    return s


def contour_segments(F, xs, ys, level):
    """Marching squares on F[j][i] sampled at (xs[i], ys[j]); returns line segments in data units."""
    segs = []
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            c = [(xs[i], ys[j], F[j][i]), (xs[i + 1], ys[j], F[j][i + 1]),
                 (xs[i + 1], ys[j + 1], F[j + 1][i + 1]), (xs[i], ys[j + 1], F[j + 1][i])]
            pts = []
            for a, b in ((0, 1), (1, 2), (2, 3), (3, 0)):
                (xa, ya, va), (xb, yb, vb) = c[a], c[b]
                if (va - level) * (vb - level) < 0:
                    t = (level - va) / (vb - va)
                    pts.append((xa + t * (xb - xa), ya + t * (yb - ya)))
            if len(pts) == 2:
                segs.append(tuple(pts))
            elif len(pts) == 4:
                segs.append((pts[0], pts[1]))
                segs.append((pts[2], pts[3]))
    return segs


def fm(v, nd=3):
    return f"{v:.{nd}f}".replace("-", "−")


def bracket(x1, x2, y, label, colour=ACCENT):
    s = line(x1, y, x2, y, stroke=colour, sw=1.2)
    s += line(x1, y - 5, x1, y, stroke=colour, sw=1.2) + line(x2, y - 5, x2, y, stroke=colour, sw=1.2)
    s += mono((x1 + x2) / 2, y + 14, label, size=8.5, fill=colour, weight="600")
    return s


def dashring(x, y, rr=6, stroke=INK, sw=1.6):
    return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-dasharray="2.5,2"/>')


def cross(x, y, h=4.5, stroke=ACCENT, sw=1.8):
    return line(x - h, y - h, x + h, y + h, stroke=stroke, sw=sw) + line(x - h, y + h, x + h, y - h, stroke=stroke, sw=sw)


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "one octave on the patch enlarged ×7: six gaussian images and the five differences between them")
    cs = 3.6
    side = 35 * cs
    x0, pitch = 45, 160
    yG = 100
    yD = yG + side + 78
    s += title(32, 80, "Gaussian images L(x, y; σ), shaded high = bright")
    for i in range(6):
        x = x0 + pitch * i
        s += grid_map(x, yG, cs, cs, d.G7[i], grey_fill)
        s += mono(x + side / 2, yG + side + 16, f"σ = {d.SIG[i]:.3f}", size=8.5, fill=INK, weight="600")
    s += title(32, yD - 18, "differences D = L(next σ) − L(this σ): blue below zero, orange above")
    for i in range(5):
        x = x0 + pitch * i + 80
        s += grid_map(x, yD, cs, cs, d.D7[i], lambda v: div_fill(v, 36.0))
        s += mono(x + side / 2, yD + side + 16, f"D{i}", size=8.5, fill=INK, weight="600")
        s += mono(x + side / 2, yD + side + 29, f"centre {fm(d.D7[i][d.CY][d.CX], 2)}", size=7.5, fill=SOFT)
    xa, xb = x0 + pitch + 80, x0 + pitch * 3 + 80 + side
    s += bracket(xa, xb, yD + side + 46, "searched for extrema: each has a level above and a level below")
    xd2 = x0 + pitch * 2 + 80
    s += ring(xd2 + (d.CX + 0.5) * cs, yD + (d.CY + 0.5) * cs, 6, stroke=ACCENT, sw=1.8)
    s += dashring(xd2 + (d.GX_ + 0.5) * cs, yD + (d.GY_ + 0.5) * cs, 6, stroke=INK, sw=1.6)
    s += legend3(vh - 30, vw, [("high value", INK, "grey"), ("D below zero", LINK, "area", 0.6),
                               ("D above zero", ACCENT, "area", 0.6), ("(10, 17): kept", ACCENT, "ring"),
                               ("(17, 17): rejected", INK, "dashring")])
    return emit("01", "octave", "One octave on the enlarged patch",
                "Six Gaussian images at σ = 1.6 × 2^(i/3) and their five differences. The square is a well, "
                "deepest on D2; the step is a pair of ridges. Evaluated from the closed form.", "worked example",
                vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 400
    s = eyebrow(32, 40, "the 26-neighbour test at (10, 17): the three levels around level 2, in grey levels")
    cw, ch = 84, 44
    gw, gap = 3 * cw, 70
    x0 = (vw - (3 * gw + 2 * gap)) / 2
    y0 = 118
    lo, hi = -36.0, -27.0
    for k, lab in enumerate(("level 1 · σ 2.016", "level 2 · σ 2.540", "level 3 · σ 3.200")):
        x = x0 + k * (gw + gap)
        s += title(x, y0 - 30, lab, fill=ACCENT if k == 1 else INK)
        for jj, xx in enumerate((9, 10, 11)):
            s += mono(x + jj * cw + cw / 2, y0 - 9, f"x = {xx}", size=7.5, fill=SOFT)
        if k == 0:
            for ii, yy in enumerate((16, 17, 18)):
                s += mono(x - 10, y0 + ii * ch + ch / 2 + 3, f"y = {yy}", size=7.5, fill=SOFT, anchor="end")
        for ii in range(3):
            for jj in range(3):
                v = d.BLOCK[k][ii][jj]
                t = (v - hi) / (lo - hi)
                a = 0.08 + 0.72 * max(0.0, min(1.0, t))
                tc = "#ffffff" if a > 0.52 else INK
                s += cell(x + jj * cw, y0 + ii * ch, cw, ch, fm(v), fill=f"rgba(46,90,168,{a:.3f})", tcolor=tc,
                          size=11, weight="600" if (k, ii, jj) == (1, 1, 1) else "500")
        if k == 1:
            s += rect(x + cw, y0 + ch, cw, ch, fill="none", stroke=ACCENT, sw=2.6)
    yn = y0 + 3 * ch + 42
    s += note_lines(x0, yn, [
        ("centre −35.379 is below all 26 neighbours; the closest, −33.223, is one pixel left on the same level", INK),
        ("rows y = 16 and y = 18 are equal: the patch is symmetric about row 17", MUTED),
        ("x = 11 reads higher than x = 9 on every level: the step, to the right, lifts that side", MUTED),
        ("the whole octave has two such samples: this minimum, and a maximum of +14.740 at (17, 17)", MUTED)], gap=17)
    s += legend3(vh - 30, vw, [("shade: −27 light to −36 dark", LINK, "area", 0.5), ("the candidate", ACCENT, "outline")])
    return emit("02", "neighbour-test", "The 26-neighbour test",
                "The 27 DoG values around (10, 17) on levels 1–3. The centre is the lowest. "
                "Evaluated from the closed form.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "refining scale: the dog at the square's centre on five levels, and the parabola through three")
    ax = Axes(96, 92, 600, 270, (-0.4, 4.4), (-38.0, -18.0))
    s += f"<defs>{ax.clip('c3')}</defs>"
    s += ax.frame([], [-38, -34, -30, -26, -22, -18], ylab="D at (10, 17), grey levels",
                  yfmt=lambda v: f"{v:g}".replace("-", "−"))
    for lv in range(5):
        xx = ax.X(lv)
        s += mono(xx, ax.y0 + ax.h + 14, f"level {lv}", size=8, fill=SOFT)
        s += mono(xx, ax.y0 + ax.h + 27, f"σ {d.SIG[lv]:.3f}", size=8, fill=SOFT)
    us = [-0.4 + 4.8 * k / 400 for k in range(401)]
    sig = lambda u: 1.6 * 2 ** (u / 3)
    dc = lambda u: d.P7.L(d.CX, d.CY, d.K * sig(u)) - d.P7.L(d.CX, d.CY, sig(u))
    cont = [(ax.X(u), ax.Y(dc(u))) for u in us]
    D1, D2, D3 = (d.D7[i][d.CY][d.CX] for i in (1, 2, 3))
    a, b = (D3 + D1 - 2 * D2) / 2, (D3 - D1) / 2
    par = [(ax.X(u), ax.Y(a * (u - 2) ** 2 + b * (u - 2) + D2)) for u in [0.55 + 2.9 * k / 200 for k in range(201)]]
    uc = d.U_DOG
    body = line(ax.X(uc), ax.Y(dc(uc)) + 9, ax.X(uc), ax.y0 + ax.h, stroke=INK, sw=1.0, dash="1.5,2.5")
    body += polyline(cont, INK, sw=1.4) + polyline(par, ACCENT, sw=1.8, dash="5,3")
    s += f'<g clip-path="url(#c3)">{body}</g>'
    # value labels on the side of each sample that the curve does not occupy
    place = {0: (-10, 4, "end"), 1: (12, -10, "start"), 2: (0, -14, "middle"), 3: (-10, -6, "end"), 4: (-10, -6, "end")}
    for lv in range(5):
        v = d.D7[lv][d.CY][d.CX]
        s += dot(ax.X(lv), ax.Y(v), 4.2, fill=INK, stroke="#ffffff")
        dx, dy, anc = place[lv]
        s += mono(ax.X(lv) + dx, ax.Y(v) + dy, fm(v), size=8.5, fill=INK, anchor=anc, weight="600")
    uf = 2 + d.FB["off"][2]
    vf = d.FB["contr"]
    s += polygon([(ax.X(uf), ax.Y(vf) + 6), (ax.X(uf) + 6, ax.Y(vf)), (ax.X(uf), ax.Y(vf) - 6), (ax.X(uf) - 6, ax.Y(vf))], ACCENT)
    nx = 736
    s += note_lines(nx, 120, [
        ("parabola through levels 1–3:", ACCENT), ("vertex 0.056 below level 2", MUTED), ("", None),
        ("3-D fit (x, y, level):", ACCENT), ("offset −0.0554 level", MUTED), ("σ = 1.6 × 2^(1.9446/3) = 2.508", MUTED),
        ("D(x̂) = −35.391", MUTED), ("", None),
        ("dotted: the closed form's own", INK), ("minimum, σ 2.480; the fit", MUTED), ("lands 1% high", MUTED)], gap=15)
    s += legend3(vh - 30, vw, [("sampled level", INK, "dot"), ("parabola, levels 1–3", ACCENT, "dash"),
                               ("closed form, every σ", INK, "line"), ("fitted extremum", ACCENT, "diamond"),
                               ("closed-form minimum", INK, "dot-line")])
    return emit("03", "fit-in-scale", "Refining scale",
                "The DoG at the square's centre on levels 0–4, the parabola through levels 1–3, and the closed "
                "form between the samples. Evaluated from the closed form.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "the edge test reads shape: the dog on level 2 within three pixels of each candidate, as contour lines")
    lev_s1, lev_s2 = d.SIG[2], d.SIG[3]
    Dc = lambda x, y: d.P7.L(x, y, lev_s2) - d.P7.L(x, y, lev_s1)
    size, scale = 300, 50.0
    panels = [(96, d.CX, d.CY, [-35.0, -34.0, -33.0, -32.0, -31.0, -30.0, -29.0, -28.0], LINK, d.FB,
               "(10, 17): the square", "Dxx 4.510 · Dyy 4.420 · Tr²/Det 4.0004", "kept: curvature ratio 1.02"),
              (560, d.GX_, d.GY_, [9.0, 10.0, 11.0, 12.0, 13.0, 14.0, 14.5], ACCENT, d.FG,
               "(17, 17): between square and step", "Dxx −3.804 · Dyy −0.180 · Tr²/Det 23.2", "rejected: ratio 21.1 > 10")]
    y0 = 92
    for k, (x0, cx, cy, levels, colr, F, ttl, n1, n2) in enumerate(panels):
        cid = f"c4{k}"
        s += f'<defs><clipPath id="{cid}"><rect x="{x0}" y="{y0}" width="{size}" height="{size}"/></clipPath></defs>'
        s += rect(x0, y0, size, size, fill="#ffffff", stroke="rgba(45,49,66,0.45)", sw=0.8)
        xs = [cx - 3 + 0.1 * i for i in range(61)]
        ys = [cy - 3 + 0.1 * j for j in range(61)]
        Fv = [[Dc(x, y) for x in xs] for y in ys]
        X = lambda x: x0 + (x - (cx - 3)) * scale
        Y = lambda y: y0 + (y - (cy - 3)) * scale
        body = ""
        for lvl in levels:
            for (p, q) in contour_segments(Fv, xs, ys, lvl):
                body += (f'<line x1="{X(p[0]):.1f}" y1="{Y(p[1]):.1f}" x2="{X(q[0]):.1f}" y2="{Y(q[1]):.1f}" '
                         f'stroke="{colr}" stroke-width="1.2"/>')
        for gx in range(cx - 3, cx + 4):
            for gy in range(cy - 3, cy + 4):
                body += dot(X(gx), Y(gy), 1.8, fill=SOFT)
        s += f'<g clip-path="url(#{cid})">{body}</g>'
        s += (ring if k == 0 else dashring)(X(cx), Y(cy), 7, stroke=ACCENT if k == 0 else INK, sw=1.8)
        s += cross(X(cx + F["off"][0]), Y(cy + F["off"][1]), stroke=ACCENT)
        for gx in (cx - 3, cx, cx + 3):
            s += mono(X(gx), y0 + size + 14, f"x = {gx}", size=7.5, fill=SOFT)
        for gy in (cy - 3, cy, cy + 3):
            s += mono(x0 - 8, Y(gy) + 3, f"y = {gy}", size=7.5, fill=SOFT, anchor="end")
        s += title(x0, y0 - 14, ttl, fill=ACCENT if k == 0 else INK)
        s += note_lines(x0, y0 + size + 40, [(n1, INK), (n2, ACCENT if k == 0 else MUTED),
                                             (f"fitted offset x {F['off'][0]:+.2f}".replace("-", "−"), MUTED)], gap=16)
    s += mono(468, y0 + size / 2 - 6, "test limit", size=8, fill=SOFT, anchor="middle")
    s += mono(468, y0 + size / 2 + 8, "(r + 1)²/r = 12.1", size=8, fill=SOFT, anchor="middle")
    s += legend3(vh - 30, vw, [("contour, D below zero", LINK, "line"), ("contour, D above zero", ACCENT, "line"),
                               ("pixel sample", SOFT, "dot"), ("fitted extremum", ACCENT, "cross")])
    return emit("04", "two-candidates", "Two candidates, two shapes",
                "Contours of the DoG on level 2 within three pixels of each candidate: a round bowl at the square, "
                "a ridge between square and step. Evaluated from the closed form.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "the normalised laplacian at a square's centre against σ: one curve per size, the same curve slid along log σ")
    lg = math.log10
    ax = Axes(96, 92, 640, 270, (0.6, 12.0), (0.0, 175.0), xmap=lg)
    s += f"<defs>{ax.clip('c5')}</defs>"
    s += ax.frame([0.6, 1, 1.6, 2.54, 4, 6, 10], [0, 50, 100, 150], xlab="σ (log scale)",
                  ylab="−σ²∇²L at the centre, contrast 215", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    cols = {3: SER1, 5: SER2, 7: ACCENT, 14: INK}
    sg = [10 ** (lg(0.6) + (lg(12) - lg(0.6)) * k / 500) for k in range(501)]
    body = ""
    for l in d.SIDES:
        body += polyline([(ax.X(x), ax.Y(d.N_SQ(l, x))) for x in sg], cols[l], sw=1.9)
    body += line(ax.X(d.SIG[2]), ax.Y(0), ax.X(d.SIG[2]), ax.Y(172), stroke=MUTED, sw=1.0, dash="4,3")
    s += f'<g clip-path="url(#c5)">{body}</g>'
    for l in d.SIDES:
        sx = l / (2 * d.U_STAR)
        s += dot(ax.X(sx), ax.Y(d.N_SQ(l, sx)), 3.6, fill=cols[l], stroke="#ffffff")
    for l, v in zip(d.SIDES, d.AT254):
        s += dot(ax.X(d.SIG[2]), ax.Y(v), 3.4, fill="#ffffff", stroke=cols[l])
    for s_ in d.SIG:
        s += line(ax.X(s_), ax.y0 + ax.h, ax.X(s_), ax.y0 + ax.h - 7, stroke=ACCENT, sw=1.2)
    nx = 770
    s += note_lines(nx, 118, [
        ("peak at σ = 0.398 × side,", INK), ("height 154.9 for every side", INK), ("", None),
        ("side 3  → σ 1.19", SER1), ("side 5  → σ 1.99", SER2), ("side 7  → σ 2.79", ACCENT), ("side 14 → σ 5.58", INK),
        ("", None), ("at a fixed σ = 2.54 (dashed):", MUTED),
        ("75.8 · 140.4 · 152.2 · 21.1", MUTED), ("one σ, four readings", MUTED), ("", None),
        ("orange ticks: the octave's σ", ACCENT)], gap=15)
    s += legend3(vh - 30, vw, [("side 3", SER1, "line"), ("side 5", SER2, "line"), ("side 7", ACCENT, "line"),
                               ("side 14", INK, "line"), ("fixed σ = 2.54", MUTED, "dash"), ("peak", INK, "dot"),
                               ("reading at 2.54", INK, "ring")])
    return emit("05", "size-on-log-sigma", "Size becomes position on a log σ axis",
                "The normalised Laplacian at the centre of isolated squares of side 3, 5, 7 and 14, contrast 215. "
                "Closed forms.", "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "set σ and the answer depends on the zoom; search σ and only the size changes")
    cs = 3.9
    y0 = 112
    vmax = 36.0
    x7, x14a = 64, 64 + 35 * cs + 70
    x14b = x14a + 70 * cs + 70
    s += grid_map(x7, y0, cs, cs, d.FIX7, lambda v: div_fill(v, vmax))
    s += grid_map(x14a, y0, cs, cs, d.FIX14, lambda v: div_fill(v, vmax))
    s += grid_map(x14b, y0, cs, cs, d.TWICE14, lambda v: div_fill(v, vmax))
    s += title(x7, y0 - 34, "×7, σ 2.540 → 3.200")
    s += mono(x7, y0 - 18, "the level that finds it", size=8, fill=SOFT, anchor="start")
    s += title(x14a, y0 - 34, "×14, the same σ")
    s += mono(x14a, y0 - 18, "the square's corners dominate", size=8, fill=SOFT, anchor="start")
    s += title(x14b, y0 - 34, "×14, σ doubled: 5.080 → 6.400", fill=ACCENT)
    s += mono(x14b, y0 - 18, "one well again, at the centre", size=8, fill=SOFT, anchor="start")
    s += ring(x7 + (d.CX + 0.5) * cs, y0 + (d.CY + 0.5) * cs, 6, stroke=ACCENT, sw=1.8)
    for (x, y) in d.MIN14:
        s += ring(x14a + (x + 0.5) * cs, y0 + (y + 0.5) * cs, 6, stroke=INK, sw=1.6)
    s += ring(x14b + (20.5 + 0.5) * cs, y0 + (34.5 + 0.5) * cs, 7, stroke=ACCENT, sw=1.8)
    yn = y0 + 70 * cs + 30
    s += note_lines(x7, y0 + 35 * cs + 26, [("minimum −35.38", ACCENT), ("at (10, 17)", MUTED)], gap=15)
    s += note_lines(x14a, yn, [("four deepest minima, −20.43,", INK), ("three pixels in from each corner;", MUTED),
                               (f"centre (20.5, 34.5): {fm(d.C14, 2)}", MUTED)], gap=15)
    s += note_lines(x14b, yn, [(f"centre (20.5, 34.5): {fm(d.C14T, 2)},", ACCENT),
                               ("the ×7 value: σ and position scale by 2", MUTED)], gap=15)
    s += legend3(vh - 30, vw, [("D below zero", LINK, "area", 0.6), ("D above zero", ACCENT, "area", 0.6),
                               ("the square, found", ACCENT, "ring"), ("corner minimum", INK, "ring")])
    return emit("06", "set-against-searched", "Set against searched",
                "One DoG level on the ×7 and ×14 patches, and the ×14 patch on the level whose σ is twice as large. "
                "Evaluated from the closed form.", "searched, not set", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "a blob is a peak in position and scale; an edge is a ridge")
    cw, ch = 7.0, 3.6
    smin, smax, ns = 0.6, 6.0, 55
    sig = [smax - (smax - smin) * k / (ns - 1) for k in range(ns)]          # top row = coarsest
    mapA = [[d.P7.N(x, d.CY, sg) for x in range(35)] for sg in sig]
    mapB = [[d.P7.N(x, 0, sg) for x in range(35)] for sg in sig]
    y0 = 104
    xa, xb = 110, 110 + 35 * cw + 150
    s += grid_map(xa, y0, cw, ch, mapA, lambda v: div_fill(v, 155.0))
    s += grid_map(xb, y0, cw, ch, mapB, lambda v: div_fill(v, 40.0))
    Ys = lambda sg: y0 + (smax - sg) / (smax - smin) * (ns - 1) * ch + ch / 2
    Xc = lambda x0, x: x0 + (x + 0.5) * cw
    cid = "c7b"
    s += f'<defs><clipPath id="{cid}"><rect x="{xb}" y="{y0}" width="{35 * cw}" height="{ns * ch}"/></clipPath></defs>'
    guides = ""
    for sgn in (-1, 1):
        pts = [(Xc(xb, 20.5 + sgn * sg), Ys(sg)) for sg in [smin + (smax - smin) * k / 50 for k in range(51)]]
        guides += polyline(pts, INK, sw=1.1, dash="1.5,2.5")
    s += f'<g clip-path="url(#{cid})">{guides}</g>'
    for x0 in (xa, xb):
        for sg in (1, 2, 3, 4, 5, 6):
            s += mono(x0 - 8, Ys(sg) + 3, f"{sg}", size=7.5, fill=SOFT, anchor="end")
        for xx in (0, 10, 20, 34):
            s += mono(Xc(x0, xx), y0 + ns * ch + 14, f"{xx}", size=7.5, fill=SOFT)
        for sg in d.SIG:
            s += line(x0 + 35 * cw, Ys(sg), x0 + 35 * cw + 7, Ys(sg), stroke=ACCENT, sw=1.2)
        s += mono(x0 - 8, y0 - 8, "σ", size=8.5, fill=SOFT, anchor="end")
        s += mono(x0 + 35 * cw, y0 + ns * ch + 28, "x (pixels)", size=8, fill=SOFT, anchor="end")
    s += title(xa, y0 - 22, "row 17, through the square · shade to ±155")
    s += title(xb, y0 - 22, "row 0, the step alone · shade to ±40")
    s += ring(Xc(xa, d.CX), Ys(d.S_LOG), 6, stroke=ACCENT, sw=1.8)
    yn = y0 + ns * ch + 50
    s += note_lines(xa, yn, [(f"peak {fm(d.P7.N(d.CX, d.CY, d.S_LOG), 1)} at x 10, σ {d.S_LOG:.2f}", ACCENT),
                             ("one point in (x, σ): a characteristic scale", MUTED)], gap=15)
    s += note_lines(xb, yn, [("dotted: x = 20.5 − σ and x = 20.5 + σ", INK), ("+38.7 along the first (dark side),", ACCENT),
                             ("−38.7 along the second (bright side):", LINK), ("the same height at every σ, so no scale", MUTED)], gap=15)
    s += legend3(vh - 30, vw, [("σ²∇²L below zero", LINK, "area", 0.6), ("above zero", ACCENT, "area", 0.6),
                               ("the square's peak", ACCENT, "ring"), ("ridge line", INK, "dot-line"), ("octave levels", ACCENT, "line")])
    return emit("07", "peak-and-ridge", "A peak and a ridge",
                "The scale-normalised Laplacian over position and σ, along the square's row and along the top "
                "row, where only the step remains. Closed forms.", "searched, not set", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "which requirement picks the gaussian")
    cols = ["linear, shift-", "rotation-", "semigroup", "scale-", "positive", "non-enhance-", "separable"]
    cols2 = ["invariant", "invariant", "(blur ∘ blur)", "invariant", "", "ment", ""]
    rows = [("Gaussian", ["yes"] * 7),
            ("Poisson", ["yes", "yes", "yes", "yes", "yes", "no", "no"]),
            ("box (moving average)", ["yes", "no", "no", "yes", "yes", "no", "yes"]),
            ("sampled Gaussian", ["yes", "approx.", "approx.", "approx.", "yes", "approx.", "yes"])]
    x0, cw0, cw = 40, 190, 108
    y0 = 92
    for j, (a, b) in enumerate(zip(cols, cols2)):
        xc = x0 + cw0 + j * cw + cw / 2
        s += mono(xc, y0, a, size=8.5, fill=INK, weight="600")
        if b:
            s += mono(xc, y0 + 13, b, size=8.5, fill=INK, weight="600")
    s += line(x0, y0 + 24, x0 + cw0 + 7 * cw, y0 + 24, stroke=RULE_SOLID)
    for i, (name, vals) in enumerate(rows):
        y = y0 + 40 + i * 52
        if i % 2 == 0:
            s += f'<rect x="{x0 - 4}" y="{y - 14}" width="{cw0 + 7 * cw + 8}" height="52" fill="rgba(45,49,66,0.03)"/>'
        s += mono(x0, y + 12, name, size=9, fill=INK, anchor="start", weight="600")
        for j, v in enumerate(vals):
            xc = x0 + cw0 + j * cw + cw / 2
            colr = {"yes": INK, "no": ACCENT, "approx.": SOFT}[v]
            if v == "yes":
                s += dot(xc - 18, y + 9, 3.2, fill=INK)
            elif v == "no":
                s += cross(xc - 18, y + 9, h=3.4, stroke=ACCENT, sw=1.6)
            else:
                s += ring(xc - 18, y + 9, 3.4, stroke=SOFT, sw=1.2)
            s += mono(xc - 10, y + 12, v, size=8.5, fill=colr, anchor="start", weight="600" if v == "no" else "400")
    yb = y0 + 40 + 4 * 52 + 6
    xn = x0 + cw0 + 5 * cw
    s += rect(xn, y0 - 14, 2 * cw, (y0 + 40 + 3 * 52 + 38) - (y0 - 14), fill="none", stroke=ACCENT, sw=1.4, dash="4,3")
    s += mono(xn + cw, y0 + 40 + 3 * 52 + 54, "either one leaves only the Gaussian", size=8, fill=ACCENT, weight="600")
    s += note_lines(x0, yb + 42, [
        ("Poisson: passes linearity, a semigroup, scale and rotation invariance and positivity (Felsberg & Sommer); "
         "fails non-enhancement and separability.", MUTED),
        ("Box: box ∗ box is a triangle, so no semigroup; a square window is not rotation-invariant; on 2 9 1 4 1 7 7 7 6, "
         "a 5-wide box's local maximum 4.40 rises to 4.43 at width 7.", MUTED),
        ("Sampled Gaussian: what libraries compute; semigroup error under 1e-4 for σ ≥ 0.7, worse at finer scales.", MUTED)],
        gap=16, size=8)
    s += legend3(vh - 30, vw, [("holds", INK, "dot"), ("fails", ACCENT, "cross"), ("approximately", SOFT, "ring")])
    return emit("08", "which-requirement", "Which requirement picks the Gaussian",
                "Four kernels against seven requirements. Entries from the cited theorems and, for the box, from its "
                "definition and a worked counterexample.", "why the gaussian", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw = 1016
    s = eyebrow(32, 40, "the pyramid opencv would build for the 35 × 35 patch: sizes to scale, σ in input pixels")
    sizes = d.INFO7["sizes"]
    scale, x0, pitch = 0.86, 190, 128
    s += title(32, 72, "input 35 × 35 → doubled to 70 × 70 by linear interpolation → blurred by 1.249 (camera blur assumed 0.5)")
    y = 100
    tops = []
    for o, n in enumerate(sizes):
        side = max(n * scale, 4.0)
        tops.append((y, side))
        y += side + 18 + 50
    for o, n in enumerate(sizes):
        y, side = tops[o]
        searchable = n >= 11
        s += mono(32, y + 10, f"octave {o}", size=8.5, fill=INK, anchor="start", weight="600")
        s += mono(32, y + 24, f"{n} × {n}", size=8, fill=SOFT, anchor="start")
        if not searchable:
            s += mono(32, y + 38, "too small: no detection", size=7.5, fill=SOFT, anchor="start")
        for i in range(6):
            x = x0 + i * pitch
            sg_in = 0.8 * 2 ** o * 2 ** (i / 3)
            focal = (o == 1 and i == 2)
            fillc = "rgba(235,108,54,0.12)" if focal else ("rgba(45,49,66,0.05)" if searchable else "rgba(45,49,66,0.02)")
            strk = ACCENT if focal else ("rgba(45,49,66,0.55)" if searchable else "rgba(45,49,66,0.28)")
            s += rect(x, y, side, side, fill=fillc, stroke=strk, sw=1.8 if focal else 0.9)
            lab = f"{sg_in:.3f}".rstrip("0").rstrip(".")
            s += mono(x + side / 2, y + side + 13, f"σ {lab}", size=7.5,
                      fill=ACCENT if focal else (INK if searchable else SOFT), weight="600" if focal else "400")
            if i < 5:
                ya = y + min(side / 2, 14)
                s += arrow(x + side + 6, ya, x + pitch, ya, MUTED, sw=1.0)
                s += mono((x + side + x + pitch) / 2, ya - 5, f"+{d.INC[i]:.3f}", size=7, fill=SOFT)
        if o < len(sizes) - 1:
            yn, sn = tops[o + 1]
            xs = x0 + 3 * pitch + side / 2
            ym = y + side + 30
            xt = x0 + sn / 2
            r = 6
            path = (f"M {xs:.1f} {y + side + 18:.1f} V {ym - r:.1f} Q {xs:.1f} {ym:.1f} {xs - r:.1f} {ym:.1f} "
                    f"H {xt + r:.1f} Q {xt:.1f} {ym:.1f} {xt:.1f} {ym + r:.1f} V {yn:.1f}")
            s += (f'<path d="{path}" fill="none" stroke="{MUTED}" stroke-width="1.1" marker-end="url(#am)"/>')
            s += mono((xs + xt) / 2, ym + 13, "level 3, every second pixel → next octave's level 0", size=7.5, fill=SOFT)
    yb = tops[-1][0] + 66
    s += note_lines(32, yb, [
        ("orange: octave 1, level 2: the square, σ = 1.6 × 2^((2 − 0.05)/3) ≈ 2.51 in input pixels", ACCENT),
        ("extra blur per arrow, in each octave's own pixels; σ doubles every three levels", MUTED)], gap=16)
    vh = int(yb + 40)
    return emit("09", "pyramid", "The pyramid for the enlarged patch",
                "Five octaves of six Gaussian levels: sizes to scale, σ in input pixels, the extra blur along each "
                "arrow and the halving between octaves. From the transcribed rules.", "octaves", vw, vh, MARKS + s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "a dog level is the normalised laplacian averaged over one interval of log σ, so it peaks early")
    lg = math.log10
    ax = Axes(96, 92, 620, 270, (1.0, 8.0), (0.0, 175.0), xmap=lg)
    s += f"<defs>{ax.clip('c10')}</defs>"
    s += ax.frame([1, 1.6, 2, 2.48, 3, 4, 6, 8], [0, 50, 100, 150], xlab="σ (log scale); for the DoG, the lower of its pair",
                  ylab="at (10, 17), sign flipped", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    sg = [10 ** (lg(1.0) + (lg(8.0) - lg(1.0)) * k / 500) for k in range(501)]
    Nf = lambda x: -d.P7.N(d.CX, d.CY, x)
    Df = lambda x: -d.D_CONT(x)
    lo, hi = d.S_DOG, d.S_DOG * d.K
    band = [(ax.X(x), ax.Y(Nf(x))) for x in [lo + (hi - lo) * k / 60 for k in range(61)]]
    band = [(ax.X(lo), ax.Y(0))] + band + [(ax.X(hi), ax.Y(0))]
    body = polygon(band, ACCENT, op=0.10)
    body += polyline([(ax.X(x), ax.Y(Nf(x))) for x in sg], INK, sw=1.9)
    body += polyline([(ax.X(x), ax.Y(Df(x) / math.log(d.K))) for x in sg], ACCENT, sw=1.9)
    body += polyline([(ax.X(x), ax.Y(Df(x) / (d.K - 1))) for x in sg], ACCENT, sw=1.3, dash="4,3")
    s += f'<g clip-path="url(#c10)">{body}</g>'
    s += dot(ax.X(d.S_LOG), ax.Y(Nf(d.S_LOG)), 4, fill=INK, stroke="#ffffff")
    s += dot(ax.X(d.S_DOG), ax.Y(Df(d.S_DOG) / math.log(d.K)), 4, fill=ACCENT, stroke="#ffffff")
    s += mono(ax.X(d.S_LOG) + 8, ax.Y(Nf(d.S_LOG)) - 10, "2.776", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(ax.X(d.S_DOG) - 8, ax.Y(Df(d.S_DOG) / math.log(d.K)) - 10, "2.480", size=8.5, fill=ACCENT, anchor="end", weight="600")
    nx = 750
    s += note_lines(nx, 118, [
        ("−σ²∇²L, the normalised Laplacian", INK), ("peak 154.67 at σ 2.776", MUTED), ("", None),
        ("−D / ln k: its average over", ACCENT), ("one interval [σ, kσ]", ACCENT), ("peak at σ 2.480", MUTED),
        ("shaded: the interval at 2.480", MUTED), ("", None),
        ("2.776 / 2.480 = 1.119; √k = 1.122", INK), ("", None),
        ("−D / (k − 1), Lowe's scaling:", ACCENT), ("same peak, 0.89 × as tall", MUTED)], gap=15)
    s += legend3(vh - 30, vw, [("normalised Laplacian", INK, "line"), ("DoG ÷ ln k", ACCENT, "line"),
                               ("DoG ÷ (k − 1)", ACCENT, "dash"), ("averaging interval", ACCENT, "area", 0.10)])
    return emit("10", "dog-averages-log", "What one DoG level measures",
                "At the square's centre: the normalised Laplacian against σ, and the DoG as its average over one "
                "interval of log σ. Closed forms on the ×7 patch.", "octaves", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "sift's edge test is harris's ratio test, applied to the hessian of the dog")
    lg = math.log10
    ax = Axes(96, 92, 620, 270, (0.01, 1.0), (0.0, 0.27), xmap=lg)
    s += f"<defs>{ax.clip('c11')}</defs>"
    s += ax.frame([0.01, 0.03, 0.1, 0.3, 1.0], [0, 0.05, 0.1, 0.15, 0.2, 0.25], xlab="t = smaller / larger curvature (log scale)",
                  ylab="Det / Tr² = t / (1 + t)²", xfmt=lambda v: f"{v:g}", yfmt=lambda v: f"{v:g}")
    ts = [10 ** (-2 + 2 * k / 400) for k in range(401)]
    body = polyline([(ax.X(t), ax.Y(t / (1 + t) ** 2)) for t in ts], INK, sw=1.9)
    for kk, colr, dash in ((0.04, SER2, "5,3"), (0.06, SER2, "1.5,2.5"), (10 / 121, ACCENT, None)):
        body += line(ax.x0, ax.Y(kk), ax.x0 + ax.w, ax.Y(kk), stroke=colr, sw=1.3, dash=dash)
    s += f'<g clip-path="url(#c11)">{body}</g>'
    pts = [(d.T_BLOB, ACCENT, "(10, 17): t = 0.98, kept"), (d.T_GAP, INK, "(17, 17): t = 0.047, rejected")]
    for t, colr, lab in pts:
        s += dot(ax.X(t), ax.Y(t / (1 + t) ** 2), 4.5, fill=colr, stroke="#ffffff")
    s += mono(ax.X(d.T_BLOB) - 10, ax.Y(0.262), "(10, 17): t = 0.98", size=8.5, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(d.T_GAP) + 10, ax.Y(d.T_GAP / (1 + d.T_GAP) ** 2) + 18, "(17, 17): t = 0.047", size=8.5, fill=INK,
              anchor="start", weight="600")
    nx = 750
    s += note_lines(nx, 118, [
        ("SIFT, r = 10: k = 10/121 = 0.0826", ACCENT), ("passes t above 0.1", MUTED), ("", None),
        ("Harris k = 0.04 (dashed)", SER2), ("passes t above 0.0436", MUTED), ("Harris k = 0.06 (dotted)", SER2),
        ("passes t above 0.0685", MUTED), ("", None),
        ("(17, 17): 0.0431 —", INK), ("below SIFT's line,", MUTED), ("above Harris's 0.04", MUTED), ("", None),
        ("(10, 17): 0.2500, the ceiling", ACCENT)], gap=15)
    s += legend3(vh - 30, vw, [("t / (1 + t)²", INK, "line"), ("SIFT 10/121", ACCENT, "line"), ("Harris 0.04", SER2, "dash"),
                               ("Harris 0.06", SER2, "dot-line")])
    return emit("11", "edge-test-is-harris", "SIFT's edge test is a stricter Harris",
                "The curvature-ratio function with SIFT's and Harris's thresholds, and the patch's two candidates. "
                "Closed form.", "refine, then reject", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "the kept keypoint's orientation histogram, replayed from opencv's rules: 36 bins of 10°, smoothed")
    panels = [(d.HIST_P, "precise upscaling: three peaks clear 80%", 96), (d.HIST_D, "default upscaling: two peaks clear 80%", 318)]
    for h, ttl, y0 in panels:
        mx = max(h)
        ax = Axes(96, y0, 640, 150, (-0.5, 35.5), (0.0, 1.05))
        s += ax.frame([], [0, 0.5, 0.8, 1.0], yfmt=lambda v: f"{v:g}")
        s += title(96, y0 - 12, ttl)
        bw = ax.w / 36 * 0.72
        pk = [j for j, q in d.peaks(h) if q >= 0.8]
        for j in range(36):
            q = h[j] / mx
            xc = ax.X(j)
            colr = ACCENT if j in pk else "rgba(45,49,66,0.30)"
            s += rect(xc - bw / 2, ax.Y(q), bw, ax.Y(0) - ax.Y(q), fill=colr, stroke="none", sw=0)
        s += line(ax.x0, ax.Y(0.8), ax.x0 + ax.w, ax.Y(0.8), stroke=INK, sw=1.0, dash="4,3")
        for j in (0, 9, 18, 27):
            s += mono(ax.X(j), ax.y0 + ax.h + 13, f"{j * 10}°", size=7.5, fill=SOFT)
        s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 26, "gradient direction; OpenCV reports 360° minus it", size=7.5, fill=SOFT, anchor="end")
        for j, q in d.peaks(h):
            if q >= 0.8:
                s += mono(ax.X(j), ax.Y(q) - 5, f"{q:.3f}".rstrip("0").rstrip("."), size=7.5, fill=ACCENT, weight="600")
            elif 0.6 < q < 0.8 and j in (10, 17, 18):
                yl = ax.Y(0.86) if q > 0.74 else ax.Y(q) - 5       # keep labels off the 80% line
                s += mono(ax.X(j), yl, f"{q:.3f}", size=7.5, fill=MUTED)
    nx = 760
    s += note_lines(nx, 120, [
        ("precise: bins 0°, 90°, 270°", ACCENT), ("keypoints at 0°, 90.6°, 269.4°", MUTED), ("180° bin: 0.665", MUTED), ("", None),
        ("the step's gradients, in every", MUTED), ("row of the window, feed 0°", MUTED)], gap=15)
    s += note_lines(nx, 342, [
        ("default: the square sampled", INK), ("a quarter pixel off; the", MUTED), ("next peak falls to 0.789", MUTED),
        ("keypoints at 0.3° and 90.2°", MUTED)], gap=15)
    s += legend3(vh - 30, vw, [("peak at or above 80%", ACCENT, "area", 1.0), ("other bins", INK, "area", 0.3),
                               ("80% of the highest", INK, "dash")])
    return emit("12", "orientation-histograms", "One square, two orientation counts",
                "The kept keypoint's 36-bin orientation histogram in OpenCV's two upscaling modes, from a plain-Python "
                "replay of its rules. Not run.", "what is the scale for", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 620
    s = eyebrow(32, 40, "one search, three libraries: mapped from source and documentation, not run")
    cols = [("", 32), ("OpenCV", 196), ("scikit-image", 470), ("MATLAB", 752)]
    y0 = 76
    for h, x in cols:
        s += mono(x, y0, h, size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, y0 + 10, vw - 32, y0 + 10, stroke=RULE_SOLID)
    rows = [
        ("call", "SIFT_create().detect(img, None)", "feature.SIFT().detect(img)", "detectSIFTFeatures(I)"),
        ("doubling", "linear resize ×2 (default)", "rescale ×2, order 1", "not documented"),
        ("positions", "+0.25 px unless precise upscale", "+0.25 px, by its code", "not documented"),
        ("levels / octave", "nOctaveLayers 3", "n_scales 3", "NumLayersInOctave 3"),
        ("base σ", "1.6 (assumes 0.5)", "sigma_min 1.6 (sigma_in 0.5)", "Sigma 1.6"),
        ("DoG threshold", "0.04 ÷ 3 = 0.0133", "0.04/3, rescaled", "ContrastThreshold 0.0133"),
        ("edge ratio r", "10", "c_edge 10", "EdgeThreshold 10"),
        ("26-neighbour", "≥ / ≤: ties pass", "3×3×3 extrema", "not documented"),
        ("border", "5 px never searched", "1 sample per octave", "ROI at least 63 × 63"),
        ("size field", "size = 2σ (a diameter)", "sigmas: σ itself", "Scale: σ itself"),
        ("orientation", "degrees, 360 − bin", "radians", "radians, counterclockwise"),
        ("since", "main module 4.4.0 (2020)", "—", "R2021b"),
    ]
    for k, (what, a, b, c) in enumerate(rows):
        y = y0 + 32 + k * 40
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 18}" width="{vw - 56}" height="40" fill="rgba(45,49,66,0.03)"/>'
        s += mono(32, y + 4, what, size=8, fill=SOFT, anchor="start", track="0.08em", weight="600")
        for txt_, x in ((a, 196), (b, 470), (c, 752)):
            trap = txt_.startswith(("+0.25", "≥ / ≤", "size = 2σ", "0.04 ÷ 3", "linear resize"))
            s += mono(x, y + 4, txt_, size=8.5, fill=ACCENT if trap else (SOFT if txt_ in ("not documented", "—") else INK),
                      anchor="start", weight="600" if trap else "400")
    s += mono(32, vh - 16, "pinned: OpenCV 802cf95 (4.10.0 checked), scikit-image b700edc; MATLAB from MathWorks' pages, "
              "release R2026b. Orange marks the behaviour most likely to surprise.", size=8, fill=SOFT, anchor="start")
    return emit("13", "tooling-map", "The tooling map",
                "Doubling, position offset, levels, thresholds, extremum test, border, size and orientation conventions "
                "in OpenCV, scikit-image and MATLAB. None of it was executed.", "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10, "11": fig11, "12": fig12, "13": fig13}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
