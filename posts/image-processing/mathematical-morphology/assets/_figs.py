#!/usr/bin/env python3
"""Figures 01-11 for mathematical-morphology.

Every value drawn is computed in _data.py from the definitions: the patch and its mask, binary and flat grey
erosion, dilation, opening and closing by the cross with two border rules, the granulometry, the threshold
decomposition, reconstruction, and OpenCV's erode/dilate replayed from its source (802cf95, unchanged since
4.10.0). Nothing is measured and nothing loads an image. _data.py's asserts hold every number drawn here to the
article, so a figure that disagrees with the text fails to build.
Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SANS, SOFT,
                    alabel, cell, elbow_hvh, emit, eyebrow, mono, txt)
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
        elif kind == "cross":
            s += cross(x + 8, y + 5, h=4, stroke=colour, sw=1.8)
        elif kind == "cellw":
            s += rect(x, y - 1, 16, 12, fill="#ffffff", stroke="rgba(45,49,66,0.45)", sw=0.8)
        elif kind == "celld":
            s += rect(x, y - 1, 16, 12, fill=blend((45, 49, 66), 0.80), stroke="rgba(45,49,66,0.45)", sw=0.8)
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






# ------------------------------------------------------------------ helpers for this post
WHITE = "#ffffff"
DARK = blend((45, 49, 66), 0.80)
ADD = blend((235, 108, 54), 0.32)
ELEM = blend((46, 90, 168), 0.30)
ELEM2 = blend((46, 90, 168), 0.62)
LINK_TINT = blend((46, 90, 168), 0.30)
ACC_RGB, LINK_RGB = (235, 108, 54), (46, 90, 168)


def bgrid(x0, y0, cs, S, n=N, m=N, ref=None, add_tint=True, rm_mark=True, outline=(), frame_sw=1.0):
    """A binary set on an n x m grid: members white (high = bright), the rest dark. Against `ref`, members
    not in ref are tinted (added) and ref members missing from S get a tangerine cross (removed)."""
    s = ""
    for i in range(n):
        for j in range(m):
            x, y = x0 + j * cs, y0 + i * cs
            inside = (i, j) in S
            fill = WHITE if inside else DARK
            if inside and ref is not None and add_tint and (i, j) not in ref:
                fill = ADD
            s += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{cs:.1f}" height="{cs:.1f}" fill="{fill}" '
                  f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8" shape-rendering="crispEdges"/>')
            if not inside and ref is not None and rm_mark and (i, j) in ref:
                s += cross(x + cs / 2, y + cs / 2, h=cs * 0.22, stroke=ACCENT, sw=1.8)
    for (i, j), colour in outline:
        s += rect(x0 + j * cs + 1.5, y0 + i * cs + 1.5, cs - 3, cs - 3, fill="none", stroke=colour, sw=2.2)
    s += rect(x0, y0, cs * m, cs * n, fill="none", stroke="rgba(45,49,66,0.55)", sw=frame_sw)
    return s


def vgrid(x0, y0, cs, M, fill_fn, fmt_fn=lambda v: fmt(v), size=8, text_fn=None):
    """A grid of values: each cell filled by fill_fn(v), its number printed."""
    s = ""
    for i, row in enumerate(M):
        for j, v in enumerate(row):
            x, y = x0 + j * cs, y0 + i * cs
            s += (f'<rect x="{x:.1f}" y="{y:.1f}" width="{cs:.1f}" height="{cs:.1f}" fill="{fill_fn(v)}" '
                  f'stroke="rgba(45,49,66,0.30)" stroke-width="0.8" shape-rendering="crispEdges"/>')
            colour = text_fn(v) if text_fn else INK
            s += mono(x + cs / 2, y + cs / 2 + 3, fmt_fn(v), size=size, fill=colour, weight="500")
    s += rect(x0, y0, cs * len(M[0]), cs * len(M), fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    return s


def grey_text(v):
    return WHITE if v < 130 else INK


def heat(vmax):
    """0 is white; positive values tint towards tangerine on one scale per panel."""
    return lambda v: WHITE if v <= 0 else blend(ACC_RGB, 0.12 + 0.55 * min(1.0, v / vmax))


def elem(x0, y0, cs, offsets, fill=ELEM, origin=(0, 0), span=1, mark_origin=True):
    """A structuring element drawn on its own (2*span+1)-square offset grid, origin dotted."""
    k = 2 * span + 1
    s = ""
    for i in range(k):
        for j in range(k):
            off = (i - span, j - span)
            f = fill if off in offsets else WHITE
            s += (f'<rect x="{x0 + j * cs:.1f}" y="{y0 + i * cs:.1f}" width="{cs:.1f}" height="{cs:.1f}" '
                  f'fill="{f}" stroke="rgba(45,49,66,0.30)" stroke-width="0.8" shape-rendering="crispEdges"/>')
    if mark_origin:
        s += dot(x0 + (origin[1] + span) * cs + cs / 2, y0 + (origin[0] + span) * cs + cs / 2, max(2.0, cs * 0.14), fill=INK)
    s += rect(x0, y0, cs * k, cs * k, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    return s


def legend4(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like this post's cells."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, kind in items:
        if kind in ("in", "out", "added", "elem", "elem2", "link"):
            f = {"in": WHITE, "out": DARK, "added": ADD, "elem": ELEM, "elem2": ELEM2, "link": LINK_TINT}[kind]
            s += rect(x, y - 1, 16, 12, fill=f, stroke="rgba(45,49,66,0.45)", sw=0.8)
        elif kind == "removed":
            s += rect(x, y - 1, 16, 12, fill=DARK, stroke="rgba(45,49,66,0.45)", sw=0.8)
            s += cross(x + 8, y + 5, h=3.6, stroke=ACCENT, sw=1.6)
        elif kind == "outline":
            s += rect(x + 1, y, 14, 10, fill="none", stroke=ACCENT, sw=2.0)
        elif kind == "dotonly":
            s += dot(x + 8, y + 5, 3.0, fill=INK)
        elif kind == "origin":
            s += rect(x, y - 1, 16, 12, fill=ELEM, stroke="rgba(45,49,66,0.45)", sw=0.8) + dot(x + 8, y + 5, 2.4, fill=INK)
        elif kind == "dash":
            s += line(x, y + 5, x + 18, y + 5, stroke=MUTED, sw=1.4, dash="4,3")
        elif kind == "dashaccent":
            s += line(x, y + 5, x + 18, y + 5, stroke=ACCENT, sw=1.2, dash="4,3")
        elif kind == "dashsoft":
            s += line(x, y + 5, x + 18, y + 5, stroke=SOFT, sw=0.9, dash="3,3")
        elif kind.startswith("bar:"):
            s += rect(x + 3, y - 1, 10, 12, fill=kind[4:], stroke="none", sw=0)
        elif kind.startswith("line:"):
            s += line(x, y + 5, x + 18, y + 5, stroke=kind[5:], sw=2.0)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.04em")
        x += 24 + 5.6 * len(label) + 28
    return s


def caption(x, y, s, fill=SOFT, size=8):
    return mono(x, y, s, size=size, fill=fill, anchor="middle")


def symbol(x, y, s, size=14, fill=MUTED):
    return txt(x, y, s, size=size, fill=fill, family=SANS, weight="500")


def sz(S):
    return f"{len(S)} px"


X = d.X
CROSS = d.CROSS


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 380
    s = MARKS + eyebrow(32, 40, "the cross probes the mask: dilation stamps it, erosion keeps where it fits")
    cs, y0 = 28, 112
    gx = [72, 548, 812]                       # equal gaps round the 84-px element at ex
    panels = [(gx[0], X, None, "X, the mask", "pixels above 40: the bar and the speck"),
              (gx[1], d.D1, X, f"δ(X), dilation: {sz(d.D1)}", "the cross stamped on all 11 pixels"),
              (gx[2], d.E1, X, f"ε(X), erosion: {sz(d.E1)}", "only c4: its outside arm is ignored")]
    for x0, S, ref, head, cap in panels:
        s += title(x0, y0 - 26, head)
        s += bgrid(x0, y0, cs, S, ref=ref)
        s += caption(x0 + 70, y0 + 5 * cs + 18, cap)
    s += labels_rc(gx[0], y0, cs)
    ex = 338
    s += title(ex, y0 - 26, "B, the cross")
    s += elem(ex, y0 + 28, cs, CROSS)
    s += caption(ex + 42, y0 + 28 + 3 * cs + 18, "centre and 4 neighbours")
    s += caption(ex + 42, y0 + 28 + 3 * cs + 32, "dot: the origin")
    s += note_lines(72, y0 + 5 * cs + 56, [
        ("dilation: union of the cross stamped on every pixel of X  ·  erosion: keep x when every in-image arm lands in X", INK),
        ("an arm pointing outside the image never wins: OpenCV pads 8-bit erosion with 255, MATLAB with +∞", MUTED)], gap=16)
    s += legend4(vh - 30, vw, [("in the set", "in"), ("not in the set", "out"), ("added, not in X", "added"),
                               ("in X, removed", "removed"), ("the element", "origin")])
    return emit("01", "erosion-and-dilation", "Erosion and dilation by the cross",
                "The patch's 11-pixel mask dilated (19 pixels) and eroded (5 pixels) by the 3×3 cross, with the "
                "outside of the image ignored. Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 380
    s = MARKS + eyebrow(32, 40, "opening never adds a pixel, closing never removes one, and twice is once")
    cs, y0 = 28, 112
    xs = [86, 298, 578, 790]
    O2 = d.opening(d.O1, CROSS)
    C2 = d.closing(d.C1, CROSS)
    panels = [(xs[0], d.O1, f"γ(X) = δ(ε(X)): {sz(d.O1)}", "the speck goes, the bar is exact"),
              (xs[1], O2, f"γ(γ(X)): {sz(O2)}", "ε(γ(X)) is c4 again"),
              (xs[2], d.C1, f"φ(X) = ε(δ(X)): {sz(d.C1)}", "c2 filled in rows r1 to r3"),
              (xs[3], C2, f"φ(φ(X)): {sz(C2)}", "δ(φ(X)) is δ(X) again")]
    for x0, S, head, cap in panels:
        s += title(x0, y0 - 26, head)
        s += bgrid(x0, y0, cs, S, ref=X)
        s += caption(x0 + 70, y0 + 5 * cs + 18, cap)
    s += labels_rc(xs[0], y0, cs)
    for xa, xb in ((xs[0], xs[1]), (xs[2], xs[3])):
        s += symbol((xa + 140 + xb) / 2, y0 + 75, "=", size=20, fill=INK)
    s += note_lines(86, y0 + 5 * cs + 56, [
        ("opening: erode, then dilate  ·  closing: dilate, then erode  ·  both by the cross, outside ignored", INK),
        ("ε of the opening equals ε(X) and δ of the closing equals δ(X), so the second pass rebuilds the same set", MUTED)],
        gap=16)
    s += legend4(vh - 30, vw, [("in the set", "in"), ("not in the set", "out"), ("added, not in X", "added"),
                               ("in X, removed", "removed")])
    return emit("02", "opening-and-closing", "Opening and closing, once and twice",
                "Opening keeps the 10-pixel bar and drops the speck; closing fills c2 in rows r1 to r3. Either applied "
                "again changes nothing. Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 612
    s = MARKS + eyebrow(32, 40, "the adjunction: δ(A) inside Y exactly when A inside ε(Y)")
    cs = 14
    g = 5 * cs
    cols = {"lab": 40, "dA": 250, "Y": 360, "v1": 460, "A": 600, "eY": 710, "v2": 810, "same": 920}
    hy = 92
    s += mono(cols["dA"], hy, "δ(A)", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(cols["Y"], hy, "Y", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(cols["v1"], hy, "inside?", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(cols["A"], hy, "A", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(cols["eY"], hy, "ε(Y)", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(cols["v2"], hy, "inside?", size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, hy + 10, vw - 32, hy + 10, stroke=RULE_SOLID)
    rows = [("A = the speck", "Y = X", d.SPECK, X),
            ("A = ε(X), column c4", "Y = X", d.E1, X),
            ("A = X", "Y = δ(X)", X, d.D1),
            ("A = X", "Y = X", X, X)]
    for k, (la, ly, A, Y) in enumerate(rows):
        y = hy + 34 + k * 108
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 14}" width="{vw - 56}" height="100" fill="rgba(45,49,66,0.03)"/>'
        dA, eY = d.dil(A, CROSS), d.ero(Y, CROSS)
        left, right = dA <= Y, A <= eY
        s += mono(cols["lab"], y + 26, la, size=8.5, fill=INK, anchor="start", weight="600")
        s += mono(cols["lab"], y + 44, ly, size=8.5, fill=MUTED, anchor="start")
        bad1 = tuple((p, ACCENT) for p in sorted(dA - Y))
        bad2 = tuple((p, ACCENT) for p in sorted(A - eY))
        s += bgrid(cols["dA"], y, cs, dA, outline=bad1)
        s += symbol(cols["dA"] + g + 20, y + g / 2 + 5, "⊆", size=15)
        s += bgrid(cols["Y"], y, cs, Y)
        s += mono(cols["v1"], y + g / 2 + 4, "yes" if left else "no", size=11, fill=INK if left else ACCENT,
                  anchor="start", weight="600")
        s += bgrid(cols["A"], y, cs, A, outline=bad2)
        s += symbol(cols["A"] + g + 20, y + g / 2 + 5, "⊆", size=15)
        s += bgrid(cols["eY"], y, cs, eY)
        s += mono(cols["v2"], y + g / 2 + 4, "yes" if right else "no", size=11, fill=INK if right else ACCENT,
                  anchor="start", weight="600")
        s += mono(cols["same"], y + g / 2 + 4, "same answer" if left == right else "DIFFERENT", size=8.5, fill=SOFT,
                  anchor="start")
    s += mono(40, vh - 58, "all 64 pairs of the eight sets met so far agree; row 2 is the opening's law, row 3 the closing's",
              size=8.5, fill=MUTED, anchor="start")
    s += legend4(vh - 24, vw, [("in the set", "in"), ("not in the set", "out"), ("the pixels that make it a no", "outline")])
    return emit("03", "adjunction", "The adjunction on the patch",
                "Four pairs of sets, each asked whether δ(A) lies inside Y and whether A lies inside ε(Y): the two "
                "answers always agree. Worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 420
    s = MARKS + eyebrow(32, 40, "a sieve with four meshes: what the opening by each size keeps")
    sizes = d.SIZES
    # panel A: mask area kept
    axA = Axes(80, 104, 220, 170, (-0.5, 3.5), (0, 12))
    axB = Axes(410, 104, 220, 170, (-0.5, 3.5), (0, 3000))
    axC = Axes(736, 104, 230, 170, (-0.5, 2.5), (0, 1800))
    s += mono(axA.x0, 84, "mask area kept, pixels", size=9, fill=INK, anchor="start", weight="600")
    s += mono(axB.x0, 84, "grey volume kept", size=9, fill=INK, anchor="start", weight="600")
    s += mono(axC.x0, 84, "pattern spectrum: volume removed", size=9, fill=INK, anchor="start", weight="600")
    s += axA.frame([], [0, 4, 8, 12])
    s += axB.frame([], [0, 1000, 2000, 3000], yfmt=lambda v: fmt(v))
    s += axC.frame([], [0, 600, 1200, 1800], yfmt=lambda v: fmt(v))
    bw = 34
    # the floor of 40 x 25 pixels, drawn first so the bars cover it
    s += line(axB.x0, axB.Y(1000), axB.x0 + axB.w, axB.Y(1000), stroke=ACCENT, sw=1.2, dash="4,3")
    s += mono(axB.x0 + axB.w + 6, axB.Y(1000) + 3, "floor", size=8, fill=ACCENT, anchor="start")
    s += mono(axB.x0 + axB.w + 6, axB.Y(1000) + 14, "25 × 40", size=8, fill=ACCENT, anchor="start")
    for n, a, v in zip(sizes, d.AREA, d.VOLUME):
        x = axA.X(n)
        if a:
            s += rect(x - bw / 2, axA.Y(a), bw, axA.Y(0) - axA.Y(a), fill=INK, stroke="none", sw=0)
        s += mono(x, axA.Y(a) - 6, str(a), size=8.5, fill=INK, weight="600")
        x = axB.X(n)
        s += rect(x - bw / 2, axB.Y(v), bw, axB.Y(0) - axB.Y(v), fill=INK, stroke="none", sw=0)
        s += mono(x, axB.Y(v) - 6, fmt(v), size=8.5, fill=INK, weight="600")
    # element glyphs under the size axis
    for ax in (axA, axB):
        for n in sizes:
            s += mono(ax.X(n), ax.y0 + ax.h + 14, f"n = {n}", size=8, fill=SOFT)
    gy = axA.y0 + axA.h + 26
    for n in sizes:
        el = d.nB(n)
        span = max(1, n)
        c = 4 if n < 3 else 3.2
        k = 2 * span + 1
        s += elem(axA.X(n) - k * c / 2, gy, c, el, span=span, mark_origin=False, fill=ELEM2)
        s += elem(axB.X(n) - k * c / 2, gy, c, el, span=span, mark_origin=False, fill=ELEM2)
    s += mono(axA.x0, gy + 46, f"element nB: {', '.join(str(p) for p in d.ELEMENT_PIXELS)} pixels", size=8, fill=SOFT,
              anchor="start")
    # panel C: spectrum
    spec = [(0, d.SPECTRUM_VOLUME[0], d.SPECTRUM_AREA[0], "the speck", ACCENT),
            (1, d.SPECTRUM_VOLUME[1], d.SPECTRUM_AREA[1], "the bar", INK),
            (2, d.SPECTRUM_VOLUME[2], d.SPECTRUM_AREA[2], "nothing", SOFT)]
    for n, v, a, who, colour in spec:
        x = axC.X(n)
        if v:
            s += rect(x - bw / 2, axC.Y(v), bw, axC.Y(0) - axC.Y(v), fill=colour, stroke="none", sw=0)
        s += mono(x, axC.Y(v) - 20, fmt(v), size=8.5, fill=INK, weight="600")
        s += mono(x, axC.Y(v) - 8, f"{a} px", size=8, fill=SOFT)
        s += mono(x, axC.y0 + axC.h + 14, f"size {n}", size=8, fill=SOFT)
        s += mono(x, axC.y0 + axC.h + 28, who, size=8, fill=colour if colour != SOFT else SOFT, weight="600")
    s += note_lines(80, vh - 62, [
        ("size n holds what the opening by nB keeps and the opening by (n+1)B removes: the speck is size 0, the bar size 1", MUTED)],
        gap=16)
    s += legend4(vh - 24, vw, [("amount kept, or removed by size", "bar:" + INK), ("the speck's 215", "bar:" + ACCENT),
                               ("floor: every pixel at 40", "dashaccent"), ("element nB", "elem2")])
    return emit("04", "granulometry", "The patch through a sieve",
                "Mask area and grey volume after opening by the cross family nB for n = 0 to 3, and the pattern "
                "spectrum. Computed from the definitions.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 360
    s = MARKS + eyebrow(32, 40, "four laws of dilation, on the patch")
    y0 = 118
    # (a) a pixel dilates to the element placed there
    xa, ca = 48, 22
    p = (2, 2)
    s += title(xa, y0 - 30, "a pixel dilates to B")
    s += bgrid(xa, y0, ca, d.dil({p}, CROSS))
    s += dot(xa + p[1] * ca + ca / 2, y0 + p[0] * ca + ca / 2, 3.0, fill=INK)
    s += caption(xa + 55, y0 + 5 * ca + 18, "δ({(r2, c2)}): B placed there")
    # (b) dilation distributes over union: three mini grids
    xb, cb = 238, 15
    s += title(xb, y0 - 30, "dilation distributes over union")
    minis = [(d.D_BAR, f"δ(bar): {len(d.D_BAR)}"), (d.D_SPECK, f"δ(speck): {len(d.D_SPECK)}"), (d.D1, f"δ(X): {len(d.D1)}")]
    for k, (S, lab) in enumerate(minis):
        x0 = xb + k * 103
        s += bgrid(x0, y0 + 18, cb, S)
        s += caption(x0 + 37.5, y0 + 18 + 5 * cb + 16, lab)
    s += symbol(xb + 75 + 14, y0 + 18 + 41, "∪", size=15)
    s += symbol(xb + 103 + 75 + 14, y0 + 18 + 41, "=", size=15)
    s += caption(xb + 140, y0 + 5 * 22 + 18, "15 and 5 share (r2, c2): 19 pixels")
    # (c) elements compose: the cross plus the cross
    xc, cc = 600, 22
    s += title(xc, y0 - 30, "B ⊕ B: one diamond")
    s += elem(xc, y0, cc, d.DIAMOND2, span=2, fill=ELEM)
    for a_, b_ in CROSS:
        s += rect(xc + (b_ + 2) * cc, y0 + (a_ + 2) * cc, cc, cc, fill=ELEM2, stroke="rgba(45,49,66,0.30)", sw=0.8)
    s += dot(xc + 2 * cc + cc / 2, y0 + 2 * cc + cc / 2, 3.0, fill=INK)
    s += rect(xc, y0, 5 * cc, 5 * cc, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    s += caption(xc + 55, y0 + 5 * cc + 18, f"{len(d.DIAMOND2)} pixels")
    # (d) the median as a maximum of erosions
    xd = 760
    s += title(xd, y0 - 30, "median: max of 10 erosions")
    c = 8
    vals = {off: d.P[2 + off[0]][1 + off[1]] for off in CROSS}
    for k, S in enumerate(d.TRIPLES):
        gx = xd + (k % 5) * 44
        gy = y0 + (k // 5) * 62
        s += elem(gx, gy, c, S, span=1, mark_origin=False, fill=ELEM2)
        s += mono(gx + 12, gy + 36, fmt(min(vals[o] for o in S)), size=8, fill=INK, weight="600")
    s += caption(xd + 98, y0 + 5 * 22 + 18, "each subset's min at (r2, c1)")
    s += note_lines(48, y0 + 5 * 22 + 50, [
        ("a dilation is fixed by one pixel, so a translation-invariant one is a Minkowski sum: B is its impulse response", INK),
        ("at the impulse the cross reads 255 and four 40s; every 3-pixel subset holds a 40, so the largest minimum, the median, is 40", MUTED)],
        gap=16)
    s += legend4(vh - 24, vw, [("in the set", "in"), ("not in the set", "out"), ("B and its 3-pixel subsets", "elem2"),
                               ("B ⊕ B", "elem"), ("B's origin", "dotonly")])
    return emit("05", "laws-of-dilation", "Four laws of dilation",
                "A pixel dilates to the element; dilation distributes over union; two crosses compose into a "
                "13-pixel diamond; the median over the cross is the maximum of ten erosions. Worked by hand.",
                "what makes a dilation", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 460
    s = MARKS + eyebrow(32, 40, "grey erosion is binary erosion at every threshold, stacked back")
    cs = 26
    # the patch
    px, py = 48, 146
    s += title(px, py - 26, "f, the patch")
    s += vgrid(px, py, cs, d.P, grey_fill, size=7.5, text_fn=grey_text)
    s += labels_rc(px, py, cs)
    # threshold rows
    c2 = 18
    rows = [(41, 100, "t = 41 to 200: X_t is the mask"), (201, 248, "t = 201 to 255: X_t is the impulse")]
    tx, ex = 300, 520
    for t, ry, head in rows:
        S = d.thr(d.P, t)
        E = d.STACK[t]
        s += title(tx, ry - 12, head, size=9)
        s += bgrid(tx, ry, c2, S)
        s += bgrid(ex, ry, c2, E, ref=S)
        s += mono(ex + 45, ry + 5 * c2 + 15, f"ε(X_t): {sz(E)}" if E else "ε(X_t): empty", size=8, fill=SOFT)
        s += arrow(tx + 5 * c2 + 4, ry + 2.5 * c2, ex - 1, ry + 2.5 * c2, MUTED)
        s += alabel((tx + 5 * c2 + ex) / 2, ry + 2.5 * c2, "erode", gap=16, w=44)
    # fan-out and fan-in connectors
    for t, ry, _ in rows:
        s += elbow_hvh(px + 5 * cs + 2, py + 2.5 * cs, px + 5 * cs + 50, ry + 2.5 * c2, tx - 2, stroke=MUTED, sw=1.2,
                       marker="arrow")
    rx, ryy = 760, 146
    for t, ry, _ in rows:
        s += elbow_hvh(ex + 5 * c2 + 2, ry + 2.5 * c2, ex + 5 * c2 + 50, ryy + 2.5 * cs, rx - 2, stroke=MUTED, sw=1.2,
                       marker="arrow")
    s += title(rx, ryy - 26, "ε(f): stack the erosions")
    s += vgrid(rx, ryy, cs, d.GE, grey_fill, size=7.5, text_fn=grey_text)
    s += mono(rx + 65, ryy + 5 * cs + 18, "200 on c4, 40 elsewhere", size=8, fill=SOFT)
    s += note_lines(48, vh - 66, [
        ("each pixel of ε(f) takes the highest t whose eroded set contains it; every t up to 40 keeps the whole grid", INK),
        ("the threshold set at 41 is the worked example's mask, so the grey erosion is that binary erosion, level by level", MUTED)],
        gap=16)
    s += legend4(vh - 24, vw, [("in the set", "in"), ("not in the set", "out"), ("in X_t, removed by ε", "removed")])
    return emit("06", "threshold-decomposition", "Grey erosion, one threshold at a time",
                "The patch's two non-trivial threshold sets eroded by the cross and stacked back into the grey "
                "erosion. Worked by hand.", "grey levels", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 400
    s = MARKS + eyebrow(32, 40, "gradients and top-hats read heights; Sobel reads slopes")
    cs, y0 = 30, 112
    xs = [56, 300, 544, 788]
    sob = [[round(v, 1) for v in row] for row in d.SOBEL]
    panels = [(xs[0], d.GRAD, 215, "δ − ε, morphological gradient", lambda v: fmt(v)),
              (xs[1], sob, 640, "Sobel L2, Part 8's table", lambda v: fmt(v, 1)),
              (xs[2], d.WTH, 215, "f − γ, white top-hat", lambda v: fmt(v)),
              (xs[3], d.BTH, 215, "φ − f, black top-hat", lambda v: fmt(v))]
    for x0, M, vmax, head, f in panels:
        s += title(x0, y0 - 26, head, size=9)
        s += vgrid(x0, y0, cs, M, heat(vmax), fmt_fn=f, size=7.5 if vmax > 300 else 8)
    s += labels_rc(xs[0], y0, cs)
    s += caption(xs[0] + 75, y0 + 5 * cs + 18, "160 on both sides of the step")
    s += caption(xs[1] + 75, y0 + 5 * cs + 18, "640 on c3, 0 on the impulse")
    s += caption(xs[2] + 75, y0 + 5 * cs + 18, "215 at the impulse only")
    s += caption(xs[3] + 75, y0 + 5 * cs + 18, "160 in the gap the closing filled")
    s += note_lines(56, y0 + 5 * cs + 52, [
        ("the gradient is a range, max − min over the cross: 160 is the step's height and 215 the impulse's, never cancelled", INK),
        ("Sobel reads 640 = 4 × 160 on the step and 0 on the impulse itself, where its two halves cancel", MUTED),
        ("each panel is shaded on its own scale; the numbers are the values", SOFT)], gap=16)
    s += legend4(vh - 24, vw, [("0", "in"), ("larger value, darker tint", "added")])
    return emit("07", "gradient-and-top-hats", "Gradient and top-hats against Sobel",
                "The morphological gradient, Part 8's Sobel magnitude, and the white and black top-hats of the patch "
                "by the cross. Worked by hand.", "grey levels", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 420
    s = MARKS + eyebrow(32, 40, "reconstruction from f − h: a maximum lasts until h reaches its dynamic")
    cs, y0 = 26, 120
    xs = [48, 236, 424]
    for x0, h in zip(xs, (100, 180, 215)):
        M = d.HMAX[h]
        s += title(x0, y0 - 26, f"h = {h}")
        s += vgrid(x0, y0, cs, M, grey_fill, size=7.5, text_fn=grey_text)
        bar, imp = M[0][3] - 40, M[2][1] - 40
        s += caption(x0 + 65, y0 + 5 * cs + 18, f"bar +{bar}, impulse +{imp}")
    s += labels_rc(xs[0], y0, cs)
    ax = Axes(660, y0 - 4, 300, 150, (0, 240), (0, 230))
    s += mono(ax.x0, y0 - 26, "height above 40 after reconstruction", size=9, fill=INK, anchor="start", weight="600")
    s += ax.frame([0, 100, 200], [0, 100, 200], xlab="h")
    s += f'<defs>{ax.clip("c8")}</defs>'
    for h in (100, 180, 215):
        s += line(ax.X(h), ax.y0, ax.X(h), ax.y0 + ax.h, stroke=SOFT, sw=0.9, dash="3,3")
    bar_pts = [(ax.X(0), ax.Y(160)), (ax.X(160), ax.Y(0)), (ax.X(240), ax.Y(0))]
    imp_pts = [(ax.X(0), ax.Y(215)), (ax.X(215), ax.Y(0)), (ax.X(240), ax.Y(0))]
    s += f'<g clip-path="url(#c8)">' + polyline(bar_pts, INK, sw=2.0) + polyline(imp_pts, ACCENT, sw=2.0) + "</g>"
    for h, (b, i) in ((100, (60, 115)), (180, (0, 35)), (215, (0, 0))):
        s += dot(ax.X(h), ax.Y(b), 3.0, fill=INK)
        s += dot(ax.X(h), ax.Y(i), 3.0, fill=ACCENT)
    s += mono(ax.X(160), ax.y0 + ax.h + 28, "160", size=8, fill=INK, weight="600")
    s += mono(ax.X(215), ax.y0 + ax.h + 28, "215", size=8, fill=ACCENT, weight="600")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 42, "dynamics: where each line reaches 0", size=8, fill=SOFT, anchor="end")
    s += note_lines(48, vh - 78, [
        ("subtract h, then dilate inside f until nothing changes: a maximum survives while h is below its dynamic", INK),
        ("the bar's dynamic is 160 (200 − 40), the impulse's 215 (255 − 40); the regional maxima are the mask X again", MUTED)],
        gap=16)
    s += legend4(vh - 24, vw, [("the bar", "line:" + INK), ("the impulse", "line:" + ACCENT), ("h shown on the left", "dashsoft")])
    return emit("08", "h-maxima", "Reconstruction and dynamics",
                "The patch reconstructed from itself minus h, for h = 100, 180 and 215, and each maximum's remaining "
                "height as h grows. Worked by hand.", "what the laws build", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 500
    s = MARKS + eyebrow(32, 40, "the border rule is part of the operator")
    cs, gx, gy = 22, [210, 380], [112, 262]
    s += mono(gx[0], 94, "erosion ε(X)", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(gx[1], 94, "closing φ(X)", size=8.5, fill=INK, anchor="start", weight="600")
    rules = [("outside ignored", "OpenCV, MATLAB, scikit-image", d.E1, d.C1),
             ("outside = 0", "SciPy's binary default", d.E0, d.C0)]
    for (name, who, E, C), y in zip(rules, gy):
        s += mono(40, y + 40, name, size=9, fill=INK, anchor="start", weight="600")
        s += mono(40, y + 56, who, size=8, fill=SOFT, anchor="start")
        s += bgrid(gx[0], y, cs, E, ref=X)
        s += bgrid(gx[1], y, cs, C, ref=X)
        s += mono(gx[0] + 55, y + 5 * cs + 14, sz(E), size=8, fill=SOFT)
        ok = X <= C
        s += mono(gx[1] + 55, y + 5 * cs + 14, f"{sz(C)}, " + ("keeps X" if ok else f"loses {len(X - C)} of X"),
                  size=8, fill=SOFT if ok else ACCENT, weight="400" if ok else "600")
    # the tiling
    tx, ty, tcs = 600, 112, 18
    s += mono(tx, 94, "the patch beside a copy: same bar twice", size=8.5, fill=INK, anchor="start", weight="600")
    s += bgrid(tx, ty, tcs, d.TX, n=5, m=10)
    s += mono(tx + 90, ty + 5 * tcs + 14, f"tiled mask: {len(d.TX)} px", size=8, fill=SOFT)
    oT = d.opening(d.TX, CROSS, grid=d.TGRID)
    s += mono(tx, 262 - 18, "opened by the cross", size=8.5, fill=INK, anchor="start", weight="600")
    s += bgrid(tx, 262, tcs, oT, n=5, m=10, ref=d.TX)
    s += mono(tx + 90, 262 + 5 * tcs + 14, f"{len(oT)} px: only the edge bar survives", size=8, fill=ACCENT, weight="600")
    s += note_lines(40, vh - 72, [
        (f"outside = 0 breaks the adjunction: {d.ADJ_FAIL['zero']:,} of 20,000 random pairs fail, against {d.ADJ_FAIL['ignore']} with the outside ignored", INK),
        ("the two bars are identical; the inner one is 2 pixels wide, the edge one gets a free third column from the outside", MUTED)],
        gap=16)
    s += legend4(vh - 24, vw, [("in the set", "in"), ("not in the set", "out"), ("added, not in X", "added"),
                               ("in X, removed", "removed")])
    return emit("09", "border-rules", "Two border rules and a tiling",
                "Erosion and closing of the mask with the outside ignored and with the outside set to 0, and the "
                "patch tiled beside a copy and opened by the cross. Worked by hand.", "libraries", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 400
    s = MARKS + eyebrow(32, 40, "a 2×2 kernel in OpenCV: the dilation is not reflected")
    # kernel glyphs
    kx, ky, kc = 40, 112, 20
    s += title(kx, ky - 22, "erode and dilate", size=9)
    s += elem(kx, ky, kc, d.cv_offsets(d.K22), span=1)
    s += mono(kx + 30, ky + 3 * kc + 14, "offsets from (1, 1)", size=8, fill=SOFT)
    s += title(kx, ky + 128 - 22, "the adjoint dilation", size=9)
    refl = tuple((-a, -b) for a, b in d.cv_offsets(d.K22))
    s += elem(kx, ky + 128, kc, refl, span=1)
    s += mono(kx + 30, ky + 128 + 3 * kc + 14, "anchor=(0, 0)", size=8, fill=SOFT)
    cs, y0 = 26, 112
    xs = [230, 426, 622, 818]
    panels = [(xs[0], d.CV_OPEN22, "OpenCV MORPH_OPEN", ACCENT),
              (xs[1], d.TRUE_OPEN22, "true opening", INK),
              (xs[2], d.CV_CLOSE22, "OpenCV MORPH_CLOSE", ACCENT),
              (xs[3], d.TRUE_CLOSE22, "true closing", INK)]
    for x0, S, head, colour in panels:
        s += title(x0, y0 - 26, head, fill=colour, size=9)
        s += bgrid(x0, y0, cs, S, ref=X)
        s += mono(x0 + 65, y0 + 5 * cs + 16, sz(S), size=8.5, fill=INK, weight="600")
    s += mono(xs[0] + 65, y0 + 5 * cs + 30, "half the bar is gone", size=8, fill=ACCENT)
    s += mono(xs[1] + 65, y0 + 5 * cs + 30, "the bar: 2×2 squares fit", size=8, fill=SOFT)
    s += mono(xs[2] + 65, y0 + 5 * cs + 30, f"loses {len(d.CV_CLOSE22_LOST)} pixels of X", size=8, fill=ACCENT, weight="600")
    s += mono(xs[3] + 65, y0 + 5 * cs + 30, "contains X: extensive", size=8, fill=SOFT)
    s += note_lines(230, y0 + 5 * cs + 66, [
        ("OpenCV's dilate takes the max over the same offsets as erode, so MORPH_OPEN and MORPH_CLOSE are not an opening and a closing", INK),
        ("fix: cv2.dilate(mask, k, anchor=(0, 0)) reflects the offsets and gives the true results, 10 and 13 pixels", MUTED),
        ("issue #23605, open since May 2023; replayed from OpenCV's source, not run", SOFT)], gap=16)
    s += legend4(vh - 24, vw, [("in the set", "in"), ("not in the set", "out"), ("added, not in X", "added"),
                               ("in X, removed", "removed"), ("offsets, dot at (0, 0)", "origin")])
    return emit("10", "opencv-2x2-kernel", "OpenCV's 2×2 opening and closing",
                "MORPH_OPEN and MORPH_CLOSE with np.ones((2, 2)) against the true opening and closing, and the anchor "
                "fix. Replayed from OpenCV's source.", "libraries", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 560
    s = eyebrow(32, 40, "one algebra, four libraries: mapped from source and documentation, not run")
    cols = [("", 32), ("OpenCV", 190), ("scikit-image", 400), ("SciPy ndimage", 600), ("MATLAB", 800)]
    y0 = 76
    for h, x in cols:
        s += mono(x, y0, h, size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, y0 + 10, vw - 32, y0 + 10, stroke=RULE_SOLID)
    rows = [
        ("default element", "3×3 square", "the cross", "binary: the cross", "none: pass a strel"),
        ("outside, erosion", "max of the type: ignored", "grey 'reflect', binary ignored", "binary: 0, erodes edges", "+∞: ignored"),
        ("dilation reflects", "no: same offsets as erode", "binary yes, grey no", "yes", "yes"),
        ("asymmetric element", "laws broken (#23605)", "fixed in 2023 (#6676)", "laws hold", "laws hold"),
        ("iterations=n", "n erosions, n dilations", "none: pass a larger footprint", "n erosions, n dilations", "none: larger strel"),
        ("disk of radius 2", "ELLIPSE (5, 5): 17 px", "disk(2): 13 px", "build the array", "periodic lines, n = 4"),
        ("reconstruction", "none in imgproc", "reconstruction(), 3×3", "binary_propagation", "imreconstruct, 8-conn"),
        ("pinned", "802cf95, 4.10–4.12", "b700edc, 0.25.2, 0.26.0", "1.18.1", "R2026b"),
    ]
    traps = {"no: same offsets as erode", "laws broken (#23605)", "binary: 0, erodes edges", "ELLIPSE (5, 5): 17 px",
             "binary yes, grey no"}
    for k, (what, *cells) in enumerate(rows):
        y = y0 + 38 + k * 54
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 22}" width="{vw - 56}" height="54" fill="rgba(45,49,66,0.03)"/>'
        s += eyebrow(32, y + 4, what, fill=SOFT, size=8)
        for text, (_, x) in zip(cells, cols[1:]):
            trap = text in traps
            s += mono(x, y + 4, text, size=8.5, fill=ACCENT if trap else INK, anchor="start",
                      weight="600" if trap else "400")
    s += mono(32, vh - 16, "Orange marks the behaviour most likely to surprise. scikit-image's next namespace, skimage2, "
              "drops its own mirroring, so grey dilation reflects as SciPy's does, and defaults to 'ignore'.", size=8, fill=SOFT, anchor="start")
    return emit("11", "tooling-map", "The tooling map",
                "Default element, border rule, reflection, iterations, disk shapes and reconstruction in OpenCV, "
                "scikit-image, SciPy and MATLAB. None of it was executed.", "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
