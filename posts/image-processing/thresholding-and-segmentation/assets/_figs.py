#!/usr/bin/env python3
"""Figures 01-10 for thresholding-and-segmentation.

Every value drawn is computed in _data.py from the definitions: the patch and OpenCV's 8-bit blur of it,
Otsu's criterion over both histograms, the library rules replayed in plain Python (OpenCV 802cf95,
scikit-image b700edc), the Sobel relief and its watersheds, the two-light tiling's local thresholds, and
closed-form mixtures for Figure 6. Nothing is measured and nothing loads an image. _data.py's asserts hold
every number drawn here to the article, so a figure that disagrees with the text fails to build.
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
REG = {1: LINK, 2: ACCENT, 3: SER1, 4: SER3}
REG_FILL = {k: blend(tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)), 0.30) for k, v in REG.items()}
HATCH = "url(#hatch)"


def fv(v, nd=1):
    """A relief value as printed: integers bare, others to nd places."""
    return fmt(v, nd)


def hist_axes(ax, h, colour=INK, w=4.0):
    s = ""
    for v, c in h.items():
        x = ax.X(v)
        s += rect(x - w / 2, ax.Y(c), w, ax.Y(0) - ax.Y(c), fill=colour, stroke="none", sw=0)
    return s


def step_curve(ax, pts, colour, sw=1.6, dash=None):
    """pts: list of (t, value) for consecutive integer t; drawn as a step line."""
    out = []
    for k, (t, v) in enumerate(pts):
        x0, x1 = ax.X(t - 0.5), ax.X(t + 0.5)
        y = ax.Y(v)
        if out:
            out.append((x0, out[-1][1]))
        out.append((x0, y))
        out.append((x1, y))
    return polyline(out, colour, sw=sw, dash=dash)


def label_grid(x0, y0, cs, L, values=None, vsize=7.5, lsize=11, hatch_neg=True, outline=None):
    """A 5x5 label map: region tint per label, hatch for -1, white for 0."""
    s = ""
    for i, row in enumerate(L):
        for j, lab in enumerate(row):
            x, y = x0 + j * cs, y0 + i * cs
            if lab > 0:
                s += rect(x, y, cs, cs, fill=REG_FILL[lab], stroke="rgba(45,49,66,0.30)")
            else:
                s += rect(x, y, cs, cs, fill="#ffffff", stroke="rgba(45,49,66,0.30)")
                if lab < 0 and hatch_neg:
                    s += rect(x, y, cs, cs, fill=HATCH, stroke="none", sw=0)
            if values is not None:
                s += mono(x + cs / 2, y + cs / 2 + 3, values[i][j], size=vsize, fill=INK)
            else:
                t = "−1" if lab < 0 else str(lab)
                if lab < 0 and hatch_neg:
                    s += rect(x + cs / 2 - 11, y + cs / 2 - 8, 22, 15, fill=PAPER, stroke="none", sw=0, rx=2)
                s += mono(x + cs / 2, y + cs / 2 + 4, t, size=lsize, fill=INK if lab >= 0 else MUTED, weight="600")
    s += rect(x0, y0, cs * len(L[0]), cs * len(L), fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    if outline:
        for (i, j), colour in outline:
            s += rect(x0 + j * cs + 1.5, y0 + i * cs + 1.5, cs - 3, cs - 3, fill="none", stroke=colour, sw=2.4)
    return s


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 500
    s = MARKS
    s += eyebrow(32, 40, "otsu's score at every threshold, over two real histograms")
    panels = [
        (48, "the patch: three spikes", d.HR, d.CURVE_RAW, 7500, [0, 2000, 4000, 6000], d.OCV_OTSU_RAW,
         d.RAW_BEST, 15, [0, 5, 10, 15]),
        (548, "the patch smoothed (OpenCV, 8-bit): ten levels", d.HS, d.CURVE_SM, 3500, [0, 1000, 2000, 3000],
         d.OCV_OTSU_SM, d.SM_BEST, 6, [0, 2, 4, 6]),
    ]
    for x0, ttl, h, curve, ymax, yt, ret, best, cmax, ct in panels:
        w = 420
        s += title(x0, 80, ttl)
        ac = Axes(x0 + 30, 104, w, 140, (-3, 258), (0, ymax))
        ah = Axes(x0 + 30, 300, w, 110, (-3, 258), (0, cmax))
        s += ac.frame([], yt, ylab="σB² (between-class variance)", yfmt=lambda v: f"{v:,}")
        s += ah.frame([0, 50, 100, 150, 200, 255], ct, xlab="grey level", ylab="pixels")
        flat = [(t, v) for t, v in curve]
        s += f"<defs>{ac.clip('c' + str(x0))}</defs>"
        s += f'<g clip-path="url(#c{x0})">' + step_curve(ac, flat, MUTED, sw=1.4) + "</g>"
        lo, hi = best["lo"], best["hi"] - 1
        top = [(t, v) for t, v in curve if lo <= t <= hi]
        s += step_curve(ac, top, ACCENT, sw=2.6)
        s += dot(ac.X(ret), ac.Y(best["sb"]), 4.2, fill=ACCENT)
        s += hist_axes(ah, h, colour=INK, w=4.0)
        s += f'<rect x="{ah.X(lo + 0.5):.1f}" y="{ah.y0}" width="{ah.X(hi + 0.5) - ah.X(lo + 0.5):.1f}" ' \
             f'height="{ah.h}" fill="{ACCENT}" fill-opacity="0.08"/>'
        s += note_lines(x0 + 30, 268, [(f"best split: any t from {lo} to {hi};  σB² = {fmt(best['sb'], 1)},  "
                                        f"η = {best['eta']:.3f};  OpenCV returns {ret}", INK)], size=8.5)
    s += legend2(vh - 30, vw, [("histogram bar", INK, "fill"), ("σB² at each threshold t", MUTED, "line"),
                                ("the best run of t", ACCENT, "line"), ("the t OpenCV returns", ACCENT, "dot")])
    return emit("01", "otsu-criterion", "Otsu's criterion over two histograms",
                "The raw patch scores the same at every t from 40 to 199; the smoothed patch has one best run, "
                "105 to 161. Computed from the definition.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "at every cut the two variances add up to the same total")
    ax = Axes(96, 92, 860, 270, (0, 9), (0, 3600))
    s += ax.frame([], [0, 1000, 2000, 3000], ylab="variance (grey levels²)", yfmt=lambda v: f"{v:,}")
    bw, pitch = 62, 860 / 9
    tot = d.SM_VAR
    for k, row in enumerate(d.SM):
        x = 96 + k * pitch + (pitch - bw) / 2
        yb, yt = ax.Y(row["sb"]), ax.Y(tot)
        best = row is d.SM_BEST
        s += rect(x, yb, bw, ax.Y(0) - yb, fill=blend((235, 108, 54), 0.85 if best else 0.55), stroke="none", sw=0)
        s += rect(x, yt, bw, yb - yt, fill=blend((46, 90, 168), 0.20), stroke="none", sw=0)
        s += mono(x + bw / 2, yb + 15, fmt(row["sb"], 0), size=8, fill="#ffffff" if best else INK, weight="600")
        s += mono(x + bw / 2, yb - 7, fmt(row["sw"], 0), size=8, fill=LINK)
        s += mono(x + bw / 2, ax.y0 + ax.h + 14, f"{row['lo']} | {row['hi']}", size=8, fill=INK if best else SOFT,
                  weight="600" if best else "400")
        if best:
            s += rect(x - 3, yt - 3, bw + 6, ax.Y(0) - yt + 3, fill="none", stroke=ACCENT, sw=1.8)
    s += line(ax.x0, ax.Y(tot), ax.x0 + ax.w, ax.Y(tot), stroke=INK, sw=1.0, dash="4,3")
    s += mono(ax.x0 + 12, ax.Y(tot) - 9, f"σT² = {fmt(tot, 2)}, the total variance, at every cut", size=8.5, fill=INK,
              anchor="start", weight="600")
    s += mono(ax.x0 + ax.w, ax.y0 + ax.h + 30, "cut between these two grey levels", size=8.5, fill=SOFT, anchor="end")
    s += legend2(vh - 30, vw, [("σB², between the classes", ACCENT, "area", 0.55), ("σW², within the classes", LINK, "area", 0.20),
                               ("the best cut", ACCENT, "outline")])
    return emit("02", "variance-split", "Between plus within is constant",
                "Nine cuts of the smoothed patch's histogram. The tallest between-class bar sits under the shortest "
                "within-class bar. Computed from the histogram.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 400
    s = eyebrow(32, 40, "three rules print three numbers and draw one mask")
    ah = Axes(70, 140, 470, 150, (30, 210), (0, 6))
    s += title(48, 78, "the smoothed patch's histogram and its empty gap")
    gap0, gap1 = d.SM_BEST["lo"] + 0.5, d.SM_BEST["hi"] - 0.5
    s += f'<rect x="{ah.X(gap0):.1f}" y="{ah.y0}" width="{ah.X(gap1) - ah.X(gap0):.1f}" height="{ah.h}" ' \
         f'fill="{ACCENT}" fill-opacity="0.08"/>'
    s += ah.frame([40, 80, 120, 160, 200], [0, 2, 4, 6], xlab="grey level", ylab="pixels")
    s += hist_axes(ah, d.HS, colour=INK, w=3.0)
    lib = d.LIB["smooth"]
    marks = [(lib["otsu"], f"Otsu {lib['otsu']}", 0), (lib["isodata"][0], f"isodata {lib['isodata'][0]}", 1),
             (lib["tri"], f"triangle {lib['tri']}", 2)]
    for t, lab, k in marks:
        x = ah.X(t + 0.5)
        s += line(x, ah.y0 - 4, x, ah.Y(0), stroke=ACCENT, sw=1.6)
        s += mono(x, ah.y0 - 10 - 13 * k, lab, size=8.5, fill=ACCENT, weight="600")
    cs = 34
    for k, (ttl, img, mk, note) in enumerate([
            (f"raw patch, t = {d.LIB['raw']['otsu']}", d.P, d.MASK_RAW, "impulse bright: a lone speck"),
            ("smoothed, t = 105, 125 or 160", d.G3, d.MASK_SM, "impulse dark: absorbed")]):
        x0 = 600 + k * 205
        y0 = 110
        s += title(x0, y0 - 26, ttl)
        for i in range(5):
            for j in range(5):
                bright = mk[i][j] == 1
                s += rect(x0 + j * cs, y0 + i * cs, cs, cs, fill="#ffffff" if bright else blend((45, 49, 66), 0.80),
                          stroke="rgba(45,49,66,0.30)")
                s += mono(x0 + j * cs + cs / 2, y0 + i * cs + cs / 2 + 3, str(img[i][j]), size=8,
                          fill=INK if bright else "#ffffff")
        s += rect(x0 + cs + 1.5, y0 + 2 * cs + 1.5, cs - 3, cs - 3, fill="none", stroke=ACCENT, sw=2.2)
        s += mono(x0, y0 + 5 * cs + 18, note, size=8.5, fill=INK, anchor="start")
    s += legend2(vh - 30, vw, [("histogram bar", INK, "fill"), ("empty gap, 106 to 161", ACCENT, "area", 0.10),
                               ("a rule's threshold", ACCENT, "line"), ("above t", "#ffffff", "cellw"),
                               ("at or below t", INK, "celld"), ("the impulse", ACCENT, "outline")])
    return emit("03", "three-rules-one-mask", "Three rules, one mask",
                "Otsu, isodata and the triangle method land in the same gap of the smoothed histogram, so their masks "
                "are identical; smoothing moved the impulse to the dark side.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 400
    s = eyebrow(32, 40, "flooding the patch's gradient from two hand-drawn markers")
    levels = [0.0, 304.1, 430.0, 476.3, 640.0]
    pop = {p: v for p, v, _ in d.FLOOD}
    cs, gw, gap = 30, 150, 40
    x00 = (vw - (5 * gw + 4 * gap)) / 2
    y0 = 112
    for k, lv in enumerate(levels):
        x0 = x00 + k * (gw + gap)
        L = [[d.WS_HAND[i][j] if round(pop[(i, j)], 1) <= lv else 0 for j in range(5)] for i in range(5)]
        vals = [[fv(d.M[i][j]) for j in range(5)] for i in range(5)]
        s += label_grid(x0, y0, cs, L, values=vals, vsize=7)
        new = [((i, j), INK) for i in range(5) for j in range(5) if round(pop[(i, j)], 1) == lv and d.HAND[i][j] == 0]
        for (i, j), _ in new:
            s += rect(x0 + j * cs + 2, y0 + i * cs + 2, cs - 4, cs - 4, fill="none", stroke=INK, sw=1.6)
        for (i, j) in ((0, 0), (2, 4)):
            s += rect(x0 + j * cs + 1, y0 + i * cs + 1, cs - 2, cs - 2, fill="none", stroke=ACCENT, sw=2.6)
        s += title(x0, y0 - 26, f"level {fv(lv)}")
        s += mono(x0 + gw / 2, y0 + gw + 18, f"{sum(1 for r_ in L for v in r_ if v)} of 25 flooded", size=8, fill=SOFT)
    s += note_lines(x00, y0 + gw + 46, [
        ("the impulse (r2, c1) floods at 430, not 0: the water has to climb its rim of 430 to reach it", INK),
        ("the two regions first touch at 640, the step: region 1 takes c2, region 2 takes c3", MUTED),
        ("numbers in the cells are the relief, the Sobel magnitude from Part 8", SOFT)], gap=16)
    s += legend2(vh - 30, vw, [("region 1 (dark side)", LINK, "area", 0.30), ("region 2 (bright side)", ACCENT, "area", 0.30),
                               ("marker", ACCENT, "outline"), ("flooded at this level", INK, "outline")])
    return emit("04", "flooding-from-markers", "Flooding from two markers",
                "The Sobel relief of the patch flooded from (r0, c0) and (r2, c4): five levels, two regions, split at "
                "the step. scikit-image's queue rule, worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 400
    s = eyebrow(32, 40, "no markers: every regional minimum becomes a region")
    cs = 36
    y0 = 108
    mins = {}
    for k, comp in enumerate(d.MINIMA, 1):
        for p in comp:
            mins[p] = k
    x0 = 60
    s += title(x0, y0 - 26, "relief: four regional minima")
    for i in range(5):
        for j in range(5):
            k = mins.get((i, j))
            s += rect(x0 + j * cs, y0 + i * cs, cs, cs, fill=REG_FILL[k] if k else "#ffffff", stroke="rgba(45,49,66,0.30)")
            s += mono(x0 + j * cs + cs / 2, y0 + i * cs + cs / 2 + 3, fv(d.M[i][j]), size=8, fill=INK)
    s += rect(x0, y0, 5 * cs, 5 * cs, fill="none", stroke="rgba(45,49,66,0.55)", sw=1.0)
    for k, comp in enumerate(d.MINIMA, 1):
        i, j = comp[0]
        s += mono(x0 + j * cs + 6, y0 + i * cs + 11, str(k), size=8, fill=REG[k], anchor="start", weight="600")
    for k, (ttl, L) in enumerate([("connectivity 1 (4 neighbours)", d.WS_NONE),
                                  ("connectivity 2 (8 neighbours)", d.WS_NONE8)]):
        x = 380 + k * 320
        s += title(x, y0 - 26, ttl)
        s += label_grid(x, y0, cs, L)
    s += note_lines(60, y0 + 5 * cs + 30, [
        ("the impulse's ring of 304.1 to 476.3 cuts the dark side's zeros into a top pair, a bottom pair and the impulse's own pit", INK),
        ("four minima, four regions under either connectivity; the shapes differ, as they do between libraries", MUTED)], gap=16)
    s += legend2(vh - 30, vw, [("region 1", LINK, "area", 0.30), ("region 2", ACCENT, "area", 0.30),
                               ("region 3", SER1, "area", 0.30), ("region 4", SER3, "area", 0.30)])
    return emit("05", "four-minima-four-regions", "One hot pixel, four regions",
                "The patch's relief has four regional minima; flooded without markers they give four regions. "
                "scikit-image's rule with 4 and 8 neighbours, worked by hand.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 590
    s = eyebrow(32, 40, "where otsu cuts, and where the best cut is, for four model histograms")
    specs = [("equal", "equal humps: 70 and 170, σ 15 each"), ("spreads", "unequal spreads: σ 8 at 70, σ 35 at 170"),
             ("sizes", "unequal sizes: a 1% object at 170"), ("overlap", "overlap: 100 and 150, σ 25 each")]
    pw, ph = 420, 92
    for k, (key, ttl) in enumerate(specs):
        sh = d.SHAPES[key]
        col, rowk = k % 2, k // 2
        x0 = 70 + col * 480
        y0 = 100 + rowk * 246
        s += title(x0 - 22, y0 - 16, ttl)
        hmax = max(sh["h"])
        ah = Axes(x0, y0, pw, ph, (0, 255), (0, hmax * 1.08))
        ac = Axes(x0, y0 + ph + 14, pw, 54, (0, 255), (0, max(sh["cur"]) * 1.1))
        s += f"<defs>{ah.clip('h' + key)}{ac.clip('k' + key)}</defs>"
        pts = [(ah.X(v), ah.Y(sh["h"][v])) for v in range(256)]
        s += f'<g clip-path="url(#h{key})">' + polygon([(ah.X(0), ah.Y(0))] + pts + [(ah.X(255), ah.Y(0))], INK, op=0.75) + "</g>"
        s += line(ah.x0, ah.Y(0), ah.x0 + pw, ah.Y(0), stroke=RULE_SOLID)
        cpts = [(ac.X(t), ac.Y(v)) for t, v in enumerate(sh["cur"])]
        s += f'<g clip-path="url(#k{key})">' + polyline(cpts, MUTED, sw=1.4) + "</g>"
        s += line(ac.x0, ac.Y(0), ac.x0 + pw, ac.Y(0), stroke=RULE_SOLID)
        for v in (0, 50, 100, 150, 200, 255):
            s += mono(ac.X(v), ac.y0 + ac.h + 13, str(v), size=7.5, fill=SOFT)
        s += mono(ac.x0 - 6, ac.y0 + 9, "σB²", size=7.5, fill=SOFT, anchor="end")
        xo, xb = ah.X(sh["otsu"] + 0.5), ah.X(sh["best"] + 0.5)
        s += line(xb, ah.y0 - 2, xb, ac.y0 + ac.h, stroke=LINK, sw=1.6, dash="4,3")
        s += line(xo, ah.y0 - 2, xo, ac.y0 + ac.h, stroke=ACCENT, sw=1.8)
        if key == "sizes":
            s += dot(ah.X(170), ah.Y(0), 3.2, fill=INK)
            s += mono(ah.X(142), ah.Y(0) - 10, "the object, too small to see", size=7.5, fill=SOFT, anchor="start")
        tx = x0 + pw - 2
        s += mono(tx, y0 + 12, f"Otsu {sh['otsu']}: {100 * sh['err_otsu']:.2f}% wrong" if sh["err_otsu"] < 0.01
                  else f"Otsu {sh['otsu']}: {100 * sh['err_otsu']:.1f}% wrong", size=8, fill=ACCENT, anchor="end", weight="600")
        s += mono(tx, y0 + 26, f"best {sh['best']}: {100 * sh['err_best']:.2f}% wrong" if sh["err_best"] < 0.01
                  else f"best {sh['best']}: {100 * sh['err_best']:.1f}% wrong", size=8, fill=LINK, anchor="end", weight="600")
        s += mono(tx, y0 + 40, f"η = {sh['eta']:.2f}", size=8, fill=INK, anchor="end")
    s += legend2(vh - 30, vw, [("histogram (closed form)", INK, "area", 0.75), ("Otsu's criterion σB²(t)", MUTED, "line"),
                               ("Otsu's cut", ACCENT, "line"), ("best possible cut", LINK, "dash")])
    return emit("06", "histogram-shapes", "What the histogram has to look like",
                "Mixtures of two normal distributions binned to 0–255, evaluated in closed form. Otsu matches the best "
                "cut only for equal humps.", "histogram shapes", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 690
    s = eyebrow(32, 40, "one row through the patch and its shadowed copy, with global and local thresholds")
    row = d.T2[0]
    truth = d.TRUTH[0]
    panels = [
        ("window 3: every method meets a flat window", [("meanc", 3, LINK, "mean − C, window 3"),
                                                         ("sauvola", 3, ACCENT, "Sauvola, window 3")]),
        ("windows 7 and 9: right, then too wide", [("meanc", 9, LINK, "mean − C, window 9"),
                                                    ("sauvola", 7, ACCENT, "Sauvola, window 7")]),
    ]
    for p, (ttl, methods) in enumerate(panels):
        y0 = 104 + p * 292
        ax = Axes(110, y0, 670, 170, (-0.5, 9.5), (0, 230))
        s += title(48, y0 - 22, ttl)
        s += ax.frame([], [0, 50, 100, 150, 200], ylab="grey level", yfmt=str)
        slot = ax.X(1) - ax.X(0)
        for j, v in enumerate(row):
            x = ax.X(j)
            s += rect(x - slot * 0.34, ax.Y(v), slot * 0.68, ax.Y(0) - ax.Y(v),
                      fill=blend((45, 49, 66), 0.30 if truth[j] else 0.75), stroke="none", sw=0)
            s += mono(x, ax.Y(0) + 14, f"c{j}", size=7.5, fill=SOFT)
            s += mono(x, ax.Y(0) + 26, "bright" if truth[j] else "dark", size=7, fill=SOFT)
        s += line(ax.X(4.5), ax.y0, ax.X(4.5), ax.Y(0), stroke=RULE_SOLID, sw=1.0, dash="2,3")
        s += mono(ax.X(2), ax.y0 + 8, "lit", size=8, fill=SOFT)
        s += mono(ax.X(7), ax.y0 + 8, "a fifth of the light", size=8, fill=SOFT)
        gy = ax.Y(d.OTSU_T2)
        s += line(ax.x0, gy, ax.x0 + ax.w, gy, stroke=MUTED, sw=1.2, dash="5,3")
        yerr = ax.Y(0) + 46
        s += mono(ax.x0 - 10, yerr + 3, "wrong in r0", size=7.5, fill=SOFT, anchor="end")
        for m, (key, w, colour, lab) in enumerate(methods):
            mk, T = d.LOCAL[(key, w)]
            for j in range(10):
                x = ax.X(j)
                xa = x - slot * 0.40 if m == 0 else x + slot * 0.02
                y = ax.Y(T[0][j])
                s += line(xa, y, xa + slot * 0.38, y, stroke=colour, sw=2.4)
                if mk[0][j] != truth[j]:
                    s += cross(x + (-0.2 if m == 0 else 0.2) * slot, yerr, h=4.2, stroke=colour, sw=2.0)
            s += mono(ax.x0 + ax.w + 10, y0 + 16 + 16 * m, f"{lab}: {d.LOCAL_ERR[(key, w)]} wrong", size=8,
                      fill=colour, anchor="start", weight="600")
        s += mono(ax.x0 + ax.w + 10, y0 + 48, f"global Otsu, {d.OTSU_T2}: {d.errors(d.GLOBAL_T2)} wrong", size=8,
                  fill=MUTED, anchor="start")
        s += note_lines(ax.x0 + ax.w + 10, y0 + 84, [("counts are over the", SOFT), ("whole 5 × 10 image,", SOFT),
                                                     ("impulses excluded", SOFT)], size=7.5, gap=12)
    s += legend2(vh - 30, vw, [("pixel, dark class", INK, "area", 0.75), ("pixel, bright class", INK, "area", 0.30),
                               ("global cut, 51", MUTED, "dash"), ("mean − C", LINK, "hbar"), ("Sauvola", ACCENT, "hbar"),
                               ("wrong, in its colour", ACCENT, "cross")])
    return emit("07", "two-lights", "One row, two lights",
                "Row r0 of the patch beside a copy at a fifth of the light. Error counts are over the whole 5×10 image. "
                "Computed from the definitions.", "uneven light", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 430
    s = MARKS + eyebrow(32, 40, "opencv's watershed on the patch, copied into three channels")
    cs = 36
    y0 = 118
    cases = [
        ("markers on the border", {(0, 0): 1, (2, 4): 2}, d.OCV_A,
         ["the frame is set to −1 first,", "so both markers vanish:", "nothing is labelled"]),
        ("one interior pixel each", {(1, 1): 1, (2, 3): 2}, d.OCV_B,
         ["the step costs 160, the impulse 215:", "label 2 crosses the step into", "the dark bottom row"]),
        ("strokes down c1 and c3", {(1, 1): 1, (2, 1): 1, (3, 1): 1, (1, 3): 2, (2, 3): 2, (3, 3): 2}, d.OCV_C,
         ["every dark pixel is reached", "at cost 0; the boundary is", "a −1 line down c2"]),
    ]
    for k, (ttl, mk, out, note) in enumerate(cases):
        x0 = 70 + k * 320
        s += title(x0, y0 - 30, ttl)
        outl = [(p, REG[v]) for p, v in mk.items()]
        s += label_grid(x0, y0, cs, out, outline=outl)
        if k == 1:
            for (i, j) in ((3, 1), (3, 2)):
                s += rect(x0 + j * cs + 5, y0 + i * cs + 5, cs - 10, cs - 10, fill="none", stroke=INK, sw=1.4, dash="3,2")
        s += note_lines(x0, y0 + 5 * cs + 22, [(note[0], INK), (note[1], INK), (note[2], INK)], gap=15)
    s += legend2(vh - 30, vw, [("label 1", LINK, "area", 0.30), ("label 2", ACCENT, "area", 0.30),
                               ("−1: boundary or frame", INK, "hatch"), ("marker, label 1", LINK, "outline"), ("marker, label 2", ACCENT, "outline"),
                               ("dark pixel given label 2", INK, "dashbox")])
    return emit("08", "opencv-watershed", "What cv2.watershed does",
                "It floods neighbour differences of the image, owns the one-pixel frame, and labels on arrival. "
                "Replayed from OpenCV's source.", "library watersheds", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "how deep each minimum is: the level at which basins merge")
    ax = Axes(130, 92, 600, 300, (0, 4), (0, 700))
    s += ax.frame([], [0, 100, 200, 300, 400, 500, 600, 700], ylab="flood level (relief)", yfmt=str)
    xs = [ax.X(0.5), ax.X(1.5), ax.X(2.5), ax.X(3.5)]
    names = ["top-left pair", "impulse pit", "bottom-left pair", "bright column c4"]
    cols = [REG[1], SER1, SER3, REG[2]]
    p4, p8, pb = d.PASS_TL_IMP, d.PASS8_TL_IMP, d.PASS_DARK_BRIGHT
    yh0, yh1 = ax.Y(p8), ax.Y(pb)
    s += rect(ax.x0, yh1, ax.w, yh0 - yh1, fill=ACCENT, stroke="none", sw=0, op=0.07)
    for x, nm, c in zip(xs, names, cols):
        s += line(x, ax.Y(0), x, ax.Y(p4 if c != REG[2] else pb), stroke=c, sw=2.2)
        s += dot(x, ax.Y(0), 4.5, fill=INK)
        s += mono(x, ax.Y(0) + 16, nm, size=8, fill=INK)
    xd = (xs[1] + xs[2]) / 2
    s += line(xs[0], ax.Y(p4), xs[2], ax.Y(p4), stroke=INK, sw=2.2)
    s += line(xd, ax.Y(p4), xd, ax.Y(pb), stroke=INK, sw=2.2)
    s += line(xd, ax.Y(pb), xs[3], ax.Y(pb), stroke=INK, sw=2.2)
    s += line(xs[0] - 14, ax.Y(p8), xs[2] + 14, ax.Y(p8), stroke=INK, sw=1.4, dash="4,3")
    s += mono(ax.x0 + ax.w + 10, ax.Y(p4) + 3, f"{fv(p4)}: the dark three join (4 neighbours)", size=8, fill=INK, anchor="start")
    s += mono(ax.x0 + ax.w + 10, ax.Y(p8) + 3, f"{fv(p8)}: they join diagonally (8 neighbours)", size=8, fill=INK, anchor="start")
    s += mono(ax.x0 + ax.w + 10, ax.Y(pb) + 3, f"{fv(pb)}: dark joins bright, at the step", size=8, fill=INK, anchor="start")
    s += mono(ax.x0 + ax.w + 10, yh1 + 32, "remove minima shallower than h:", size=8, fill=ACCENT,
              anchor="start", weight="600")
    s += mono(ax.x0 + ax.w + 10, yh1 + 46, "any h in the band leaves two", size=8, fill=ACCENT,
              anchor="start", weight="600")
    s += legend2(vh - 30, vw, [("a basin's floor (level 0)", INK, "dot"), ("merge (4 neighbours)", INK, "line"),
                               ("merge (8 neighbours)", INK, "dash"), ("h that leaves two regions (8 neighbours)", ACCENT, "area", 0.10)])
    return emit("09", "merge-tree", "How deep each minimum is",
                "The four basins of the patch's relief merging as the flood rises. The dark three join at 430, or at "
                "304.1 diagonally; the dark side meets the bright only at 640. Worked by hand.", "markers", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 600
    s = eyebrow(32, 40, "one decision, three libraries: mapped from source and documentation, not run")
    cols = [("", 32), ("OpenCV", 196), ("scikit-image", 470), ("MATLAB", 752)]
    y0 = 76
    for h, x in cols:
        s += mono(x, y0, h, size=8.5, fill=INK, anchor="start", weight="600")
    s += line(32, y0 + 10, vw - 32, y0 + 10, stroke=RULE_SOLID)
    rows = [
        ("otsu returns", "first level of the best gap", "first maximum's bin centre", "level from 0 to 1"),
        ("8-bit otsu path", "IPP on x86 builds, else its loop", "its own NumPy code", "256-bin histogram"),
        ("η", "not returned", "not returned", "em, from graythresh"),
        ("global rules", "Otsu (8, 16-bit), triangle (8-bit)", "Otsu, isodata, triangle, li, yen", "Otsu: graythresh, imbinarize"),
        ("local", "mean or Gaussian − C", "Sauvola k 0.2, window 15", "adaptive: Bradley, 0.5"),
        ("watershed floods", "the colour image's differences", "the array you pass", "the array you pass"),
        ("connectivity", "4 neighbours", "4 (connectivity=1)", "8 neighbours"),
        ("boundaries", "−1, and the outer frame", "none unless watershed_line", "0 for no single region"),
        ("no markers given", "markers are required", "every regional minimum", "always its regional minima"),
        ("versions", "THRESH_DRYRUN from 4.12.0", "cost clamp from 0.25.0", "R2026b pages"),
    ]
    for k, (what, a, b, c) in enumerate(rows):
        y = y0 + 34 + k * 46
        if k % 2 == 0:
            s += f'<rect x="28" y="{y - 20}" width="{vw - 56}" height="46" fill="rgba(45,49,66,0.03)"/>'
        s += eyebrow(32, y + 4, what, fill=SOFT, size=8)
        for txt_, x in ((a, 196), (b, 470), (c, 752)):
            trap = txt_.startswith(("IPP on", "the colour image", "−1, and", "every regional", "Sauvola k 0.2", "first level"))
            s += mono(x, y + 4, txt_, size=8.5, fill=ACCENT if trap else (SOFT if txt_.startswith("not ") else INK),
                      anchor="start", weight="600" if trap else "400")
    s += mono(32, vh - 16, "pinned: OpenCV 802cf95 (4.10.0 and 4.12.0 checked), scikit-image b700edc (0.24.0 and 0.25.0 "
              "checked); MATLAB from MathWorks' R2026b pages. Orange marks the behaviour most likely to surprise.",
              size=8, fill=SOFT, anchor="start")
    return emit("10", "tooling-map", "The tooling map",
                "Return values, Otsu's code path, local defaults, what watershed floods, connectivity, boundary labels "
                "and markers in OpenCV, scikit-image and MATLAB. None of it was executed.", "implementation", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07,
        "08": fig08, "09": fig09, "10": fig10}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
