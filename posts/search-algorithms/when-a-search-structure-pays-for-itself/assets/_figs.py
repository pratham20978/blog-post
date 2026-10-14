#!/usr/bin/env python3
"""Figures 01-06 for when-a-search-structure-pays-for-itself.

Every value drawn comes from the lab's captures.json through _data.py, whose asserts hold each one
to the number the article prints. Helpers below are copied from image-processing part 11's _figs.py
(copy, never import across posts).
Run:  python3 _figs.py [01 05 ...]
"""
import math
import sys

from _build import (ACCENT, INK, LINK, MUTED, PAPER, RULE, RULE_SOLID, SOFT, emit, eyebrow,
                    mono, txt)
import _data as d

GREEN = "#5e7a6f"


# ------------------------------------------------------------------ drawing helpers
def fmt(v, nd=2):
    if abs(v - round(v)) < 1e-9:
        return f"{round(v):,}"
    return f"{v:,.{nd}f}"


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


def polyline(pts, stroke, sw=1.8, dash=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}{o}/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None):
    s = f' stroke="{stroke}" stroke-width="1.4"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{s}/>'


def ring(x, y, rr=4.5, stroke=INK, sw=1.6):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{PAPER}" stroke="{stroke}" stroke-width="{sw}"/>'


def blend(rgb, a, paper=(245, 245, 245)):
    """An opaque colour equal to rgb at alpha a over the paper."""
    r, g, b = (round(a * c + (1 - a) * p) for c, p in zip(rgb, paper))
    return f"#{r:02x}{g:02x}{b:02x}"


ACCENT_RGB, LINK_RGB, INK_RGB = (235, 108, 54), (46, 90, 168), (45, 49, 66)


def plate(x, y, s, size=8.5, fill=MUTED, anchor="middle", weight="400", pad=6):
    """Mono text on an opaque paper plate, for labels that sit over lines."""
    w = 0.6 * size * len(str(s)) + 2 * pad
    x0 = {"middle": x - w / 2, "start": x - pad, "end": x - w + pad}[anchor]
    return (f'<rect x="{x0:.1f}" y="{y - size - 2:.1f}" width="{w:.1f}" height="{size + 7:.1f}" rx="2" fill="{PAPER}"/>'
            + mono(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight))


def title(x, y, s, fill=INK, anchor="start", size=9.5):
    """A panel title in mono, not uppercased, so notation keeps its case."""
    return mono(x, y, s, size=size, fill=fill, anchor=anchor, weight="600")


def legend2(y, vw, items):
    """Legend whose swatches are drawn exactly like the marks they name."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for item in items:
        label, colour, kind = item[:3]
        if kind in ("line", "dash", "dot-line"):
            dd = {"line": "", "dash": ' stroke-dasharray="5,3"', "dot-line": ' stroke-dasharray="1.5,2.5"'}[kind]
            s += (f'<line x1="{x}" y1="{y + 5}" x2="{x + 18}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.8"{dd}/>')
        elif kind == "dot-solid":
            s += line(x, y + 5, x + 18, y + 5, stroke=colour, sw=1.8) + dot(x + 9, y + 5, 3.2, fill=colour)
        elif kind == "ring-dash":
            s += line(x, y + 5, x + 18, y + 5, stroke=colour, sw=1.6, dash="5,3") + ring(x + 9, y + 5, 3.4, stroke=colour, sw=1.4)
        elif kind == "node-black":
            s += f'<circle cx="{x + 8}" cy="{y + 5}" r="6.5" fill="{INK}"/>'
        elif kind == "node-red":
            s += f'<circle cx="{x + 8}" cy="{y + 5}" r="6.5" fill="{ACCENT}"/>'
        elif kind == "path":
            s += line(x, y + 5, x + 18, y + 5, stroke=LINK, sw=2.6, cap="round")
        elif kind == "fill":
            s += rect(x, y - 1, 16, 12, fill=colour, stroke=colour, sw=0.8)
        elif kind == "outline":
            s += rect(x, y - 1, 16, 12, fill="#ffffff", stroke=colour, sw=1.6)
        elif kind == "tint-outline":
            fill, stroke = colour
            s += rect(x, y - 1, 16, 12, fill=fill, stroke=stroke, sw=1.4)
        elif kind == "dashring":
            s += (f'<circle cx="{x + 8}" cy="{y + 5}" r="6" fill="none" stroke="{colour}" stroke-width="1.4" '
                  f'stroke-dasharray="3,2"/>')
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.04em")
        x += 24 + 5.6 * len(label) + 28
    return s


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

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str):
        s = line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, stroke=RULE_SOLID)
        s += line(self.x0, self.y0, self.x0, self.y0 + self.h, stroke=RULE_SOLID)
        for v in yt:
            yy = self.Y(v)
            s += line(self.x0, yy, self.x0 + self.w, yy, stroke=RULE, sw=0.8)
            s += mono(self.x0 - 7, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            s += mono(self.X(v), self.y0 + self.h + 14, xfmt(v), size=8, fill=SOFT)
        if xlab:
            s += mono(self.x0 + self.w, self.y0 + self.h + 30, xlab, size=8.5, fill=SOFT, anchor="end")
        if ylab:
            s += mono(self.x0, self.y0 - 10, ylab, size=8.5, fill=SOFT, anchor="start")
        return s


def cell(x, y, w, h, value, fill="#ffffff", stroke="rgba(45,49,66,0.30)", tcolor=INK, size=11, weight="500", sw=0.8):
    return (rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw)
            + txt(x + w / 2, y + h / 2 + 4, value, size=size, fill=tcolor, family="'Geist Mono', ui-monospace, monospace",
                  weight=weight))


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "a fixed charge, then cheaper lookups")
    ax = Axes(96, 92, 760, 280, (0, 20), (0, 180))
    s += ax.frame(range(0, 21, 2), [0, 40, 80, 120, 160], xlab="lookups q",
                  ylab="comparisons so far (cumulative)")
    scan = [(r["q"], r["scan"]) for r in d.CUM]
    worst = [(r["q"], r["sorted_worst"]) for r in d.CUM]
    mean = [(r["q"], r["sorted_mean"]) for r in d.CUM]
    P = lambda pts: [(ax.X(q), ax.Y(v)) for q, v in pts]
    # the lookups from 10 on, where sorting is ahead
    s += rect(ax.X(10), ax.y0, ax.X(20) - ax.X(10), ax.h, fill=blend(ACCENT_RGB, 0.06), stroke="none", sw=0)
    s += line(ax.X(10), ax.y0, ax.X(10), ax.y0 + ax.h, stroke=ACCENT, sw=0.9, dash="2,3")
    s += mono(ax.X(10) + 8, ax.y0 + 14, "sorting is ahead from the 10th lookup", size=8.5, fill=ACCENT,
              anchor="start", weight="600")
    s += polyline(P(scan), INK, sw=2.0)
    s += polyline(P(mean), ACCENT, sw=1.6, dash="5,3")
    s += polyline(P(worst), ACCENT, sw=2.2)
    xq, yq = ax.X(d.Q_WORST), ax.Y(d.SCAN_HIT * d.Q_WORST)
    s += dot(xq, yq, 4.2, fill=ACCENT, stroke=PAPER)
    xm, ym = ax.X(d.Q_MEAN), ax.Y(d.SCAN_HIT * d.Q_MEAN)
    s += ring(xm, ym, 3.6, stroke=ACCENT, sw=1.4)
    s += mono(ax.X(10) + 8, ax.Y(56), f"worst-case sort: the lines cross at {fmt(d.Q_WORST)}", size=8.5,
              fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.X(10) + 8, ax.Y(56) + 14, f"mean sort: they cross at {fmt(d.Q_MEAN)}", size=8.5, fill=ACCENT,
              anchor="start")
    s += mono(ax.X(0) + 6, ax.Y(d.SORT_WORST) - 8, f"{d.SORT_WORST}", size=8.5, fill=ACCENT, anchor="start",
              weight="600")
    s += mono(ax.X(0) + 6, ax.Y(d.SORT_MEAN) + 26, f"{fmt(d.SORT_MEAN)}", size=8.5, fill=ACCENT, anchor="start")
    tx = ax.x0 + ax.w + 12
    s += mono(tx, ax.Y(scan[-1][1]) + 3, f"scan: {fmt(scan[-1][1])}", size=8.5, fill=INK, anchor="start",
              weight="600")
    s += mono(tx, ax.Y(worst[-1][1]) + 3, f"sort, then", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(tx, ax.Y(worst[-1][1]) + 16, f"search: {fmt(worst[-1][1], 1)}", size=8.5, fill=ACCENT, anchor="start",
              weight="600")
    s += mono(32, vh - 64, f"16 keys. Each line starts at the sort's cost: {d.SORT_WORST} in the worst case, "
                           f"{fmt(d.SORT_MEAN)} on average over all 16! orders. A successful scan averages "
                           f"{d.SCAN_HIT}, a binary search {d.BIN_HIT}.", size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 30, vw, [("scan, 8.5 a lookup", INK, "line"),
                               ("worst-case sort, then 3.375 a lookup", ACCENT, "line"),
                               ("mean sort, then 3.375 a lookup", ACCENT, "dash")])
    return emit("01", "break-even", "The sort is repaid after 9.56 lookups",
                "Cumulative comparisons for q successful lookups on 16 keys: scanning every time, against "
                "sorting once and binary-searching. Counted by the lab.", "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def tree_layout(t, depth=1, out=None):
    """In-order index for x, depth for y: no edge can cross another."""
    if out is None:
        out = []
    if t is None:
        return out
    key, colour, left, right = t
    tree_layout(left, depth + 1, out)
    out.append((key, colour, depth, left[0] if left else None, right[0] if right else None))
    tree_layout(right, depth + 1, out)
    return out


def fig02():
    vw, vh = 1016, 736
    s = eyebrow(32, 40, "one insert, three structures")
    # ---- panel A: the sorted array
    s += title(32, 76, "sorted array: insert 50")
    cw, ch, x0 = 46, 30, 120
    yb, ya = 112, 196
    s += mono(x0 - 14, yb + 19, "before", size=8.5, fill=SOFT, anchor="end")
    s += mono(x0 - 14, ya + 19, "after", size=8.5, fill=SOFT, anchor="end")
    for i, k in enumerate(d.KEYS):
        moving = i >= d.INS["slot"]
        s += mono(x0 + i * cw + cw / 2, yb - 7, str(i), size=7.5, fill=SOFT)
        s += cell(x0 + i * cw, yb, cw, ch, k, fill=blend(ACCENT_RGB, 0.10) if moving else "#ffffff",
                  stroke=ACCENT if moving else "rgba(45,49,66,0.30)", sw=1.2 if moving else 0.8)
    after = d.KEYS[:d.INS["slot"]] + [50] + d.KEYS[d.INS["slot"]:]
    for i, k in enumerate(after):
        if i == d.INS["slot"]:
            s += cell(x0 + i * cw, ya, cw, ch, k, fill=ACCENT, stroke=ACCENT, tcolor="#ffffff", weight="600")
        elif i > d.INS["slot"]:
            s += cell(x0 + i * cw, ya, cw, ch, k, fill=blend(ACCENT_RGB, 0.10), stroke=ACCENT, sw=1.2)
        else:
            s += cell(x0 + i * cw, ya, cw, ch, k)
        s += mono(x0 + i * cw + cw / 2, ya + ch + 13, str(i), size=7.5, fill=SOFT)
    # one shift arrow for the whole run, between the rows
    xa1, xa2 = x0 + d.INS["slot"] * cw + 6, x0 + (len(d.KEYS) + 1) * cw - 6
    ym = (yb + ch + ya) / 2
    s += line(xa1, ym + 6, xa2, ym + 6, stroke=ACCENT, sw=1.4, marker="arrow-accent")
    s += mono((xa1 + xa2) / 2, ym - 4, f"{d.INS['shifts']} keys each move one slot right", size=8.5, fill=ACCENT,
              weight="600")
    s += mono(x0 + 4 * cw, ym + 3, f"binary search: {d.INS['comparisons']} comparisons find slot {d.INS['slot']}",
              size=8.5, fill=INK)
    # ---- panel B: the red-black tree after inserting 50
    by = 290
    s += line(32, by - 26, vw - 32, by - 26, stroke=RULE, sw=0.8)
    s += title(32, by, "red-black tree (TreeMap): the 16 keys inserted in order, then 50")
    nodes = tree_layout(d.TREE_AFTER)
    dx, dy, tx0, ty0, r = 30, 50, 66, by + 34, 12.5
    pos = {k: (tx0 + i * dx, ty0 + (dep - 1) * dy) for i, (k, _, dep, _, _) in enumerate(nodes)}
    path_edges = set(zip(d.PATH_50, d.PATH_50[1:] + [50]))
    for k, _, _, lc, rc in nodes:
        for c in (lc, rc):
            if c is None:
                continue
            (x1, y1), (x2, y2) = pos[k], pos[c]
            L = math.hypot(x2 - x1, y2 - y1)
            ux, uy = (x2 - x1) / L, (y2 - y1) / L
            on = (k, c) in path_edges
            s += line(x1 + ux * r, y1 + uy * r, x2 - ux * r, y2 - uy * r, stroke=LINK if on else RULE_SOLID,
                      sw=2.6 if on else 1.1, cap="round")
    for k, colour, _, _, _ in nodes:
        x, y = pos[k]
        fill = INK if colour == "black" else ACCENT
        s += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>'
        s += txt(x, y + 3.6, k, size=9.5, fill="#ffffff", family="'Geist Mono', ui-monospace, monospace", weight="600")
    parent = {c: k for k, _, _, lc, rc in nodes for c in (lc, rc) if c is not None}
    for step, k in enumerate(d.PATH_50, 1):
        x, y = pos[k]
        right_child = k in parent and pos[parent[k]][0] < x   # its edge arrives from the upper left
        s += mono(x + r + 5 if right_child else x - r - 5, y - 8, str(step), size=8, fill=LINK,
                  anchor="start" if right_child else "end", weight="600")
    x50, y50 = pos[50]
    s += (f'<circle cx="{x50:.1f}" cy="{y50:.1f}" r="{r + 4}" fill="none" stroke="{LINK}" '
          f'stroke-width="1.4" stroke-dasharray="3,2"/>')
    tm = d.TM
    s += mono(32, vh - 104, f"insert 50: {tm['insert_50']['comparisons']} comparisons (1–5), "
                            f"{tm['insert_50']['rotations']} rotations, {tm['insert_50']['flips']} colour flips, 0 shifts",
              size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(32, vh - 86, f"the build: {tm['build_comparisons']} comparisons, {tm['build_rotations']} rotations, "
                           f"{tm['build_flips']} flips; height {tm['height']}", size=8.5, fill=MUTED, anchor="start")
    # ---- panel C: the same keys with no balancing
    cx0, cy0, cdx, cdy, cr = 640, by + 30, 19.5, 17.2, 8.6
    s += line(612, by - 14, 612, vh - 50, stroke=RULE, sw=0.8)
    s += title(632, by, "no balancing: the same keys in order")
    find = d.KEYS[:d.KEYS.index(61) + 1]
    for i, k in enumerate(d.KEYS):
        x, y = cx0 + i * cdx, cy0 + i * cdy
        if i:
            px, py = cx0 + (i - 1) * cdx, cy0 + (i - 1) * cdy
            L = math.hypot(cdx, cdy)
            on = k in find
            s += line(px + cdx / L * cr, py + cdy / L * cr, x - cdx / L * cr, y - cdy / L * cr,
                      stroke=LINK if on else RULE_SOLID, sw=2.2 if on else 1.0, cap="round")
        s += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{cr}" fill="#ffffff" '
              f'stroke="{LINK if k in find else "rgba(45,49,66,0.45)"}" stroke-width="{1.6 if k in find else 1.0}"/>')
        s += txt(x, y + 2.6, k, size=7, fill=INK, family="'Geist Mono', ui-monospace, monospace", weight="600")
    pl = d.PLAIN
    s += mono(632, vh - 104, f"find 61: {pl['find_61_comparisons']} comparisons, part 1's scan",
              size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(632, vh - 86, f"build: {pl['build_comparisons']} comparisons; height {pl['height']}", size=8.5, fill=MUTED,
              anchor="start")
    s += legend2(vh - 30, vw, [("black node", INK, "node-black"), ("red node", ACCENT, "node-red"),
                               ("comparisons on the way", LINK, "path"), ("the new key", LINK, "dashring"),
                               ("keys that move", (blend(ACCENT_RGB, 0.10), ACCENT), "tint-outline")])
    return emit("02", "insert-50", "One insert, three structures",
                "Inserting 50 shifts eight keys of the sorted array, touches one five-node path of TreeMap's red-black "
                "tree, and shows what the same ascending keys do to a tree with no balancing. Counted by the lab.",
                "writes", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 500
    s = eyebrow(32, 40, "writes a sorted structure can absorb")
    ns = [16, 64, 256, 1024, 4096, 16384, 65536]
    ax = Axes(110, 92, 690, 290, (16, 65536), (0.1, 10000), xmap=math.log2, ymap=math.log10)
    s += ax.frame(ns, [0.1, 1, 10, 100, 1000, 10000], xlab="keys n (log scale)",
                  ylab="writes per read at break-even (log scale)", xfmt=lambda v: f"{v:,}",
                  yfmt=lambda v: f"{v:,}" if v >= 1 else str(v))
    s += line(ax.x0, ax.Y(1), ax.x0 + ax.w, ax.Y(1), stroke=INK, sw=0.9, dash="1.5,2.5")
    series = [("tree", 1.0, ACCENT, None), ("tree", 0.1, ACCENT, "5,3"),
              ("array", 1.0, LINK, None), ("array", 0.1, LINK, "5,3")]
    for kind, price, colour, dash in series:
        pts = [(ax.X(n), ax.Y(v)) for n, v in d.writes(price, kind)]
        s += polyline(pts, colour, sw=2.0 if dash is None else 1.6, dash=dash)
        for x, y in pts:
            s += dot(x, y, 3.2, fill=colour) if dash is None else ring(x, y, 3.4, stroke=colour, sw=1.4)
    tx = ax.x0 + ax.w + 14
    t1, t01 = d.writes(1.0, "tree")[-1][1], d.writes(0.1, "tree")[-1][1]
    a1, a01 = d.writes(1.0, "array")[-1][1], d.writes(0.1, "array")[-1][1]
    s += mono(tx, ax.Y(t1) - 4, "red-black tree", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(tx, ax.Y(t1) + 9, f"{fmt(t1, 1)}; {fmt(t01, 1)} with", size=8, fill=ACCENT, anchor="start")
    s += mono(tx, ax.Y(t1) + 21, "cheap writes", size=8, fill=ACCENT, anchor="start")
    s += mono(tx, ax.Y(a01) - 2, "sorted array,", size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(tx, ax.Y(a01) + 11, f"cheap writes: {fmt(a01)}", size=8, fill=LINK, anchor="start")
    s += mono(tx, ax.Y(a1) - 13, "sorted array:", size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(tx, ax.Y(a1), f"{fmt(a1)} write per read", size=8, fill=LINK, anchor="start")
    s += mono(ax.X(1024) + 10, ax.Y(1) - 6, "one write per read", size=8, fill=INK, anchor="start")
    s += mono(32, vh - 64, "Against appending and scanning, lookups that hit. Solid: a write (shift, store, rotation, "
                           "flip) costs one comparison. Dashed: a tenth of one.", size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 30, vw, [("red-black tree", ACCENT, "dot-solid"), ("tree, cheap writes", ACCENT, "ring-dash"),
                               ("sorted array", LINK, "dot-solid"), ("array, cheap writes", LINK, "ring-dash")])
    return emit("03", "write-share", "How many writes per read before appending wins",
                "The share of writes at which keeping keys sorted stops paying, as writes per read, for a sorted array "
                "and for TreeMap's red-black tree with keys inserted in ascending order. From the lab's counts.",
                "writes", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 618
    s = eyebrow(32, 40, "order keeps a range in one piece")
    cw, ch, x0 = 50, 32, 120
    keys = d.KEYS
    lo_i, hi_i = keys.index(d.OQ["range_keys"][0]), keys.index(d.OQ["range_keys"][-1]) + 1
    fl_i = keys.index(d.OQ["floor"])
    # ---- row 1: the range
    y1 = 130
    s += title(32, 76, "sorted array: every key from 40 to 70")
    for i, k in enumerate(keys):
        inr = lo_i <= i < hi_i
        s += cell(x0 + i * cw, y1, cw, ch, k, fill=blend(LINK_RGB, 0.14) if inr else "#ffffff",
                  stroke=LINK if inr else "rgba(45,49,66,0.30)", sw=1.3 if inr else 0.8)
        s += mono(x0 + i * cw + cw / 2, y1 + ch + 13, str(i), size=7.5, fill=SOFT)
    xl, xh = x0 + lo_i * cw + cw / 2, x0 + hi_i * cw + cw / 2
    s += mono(xl, 100, f"first key ≥ 40: index {lo_i}", size=8.5, fill=INK, weight="600")
    s += mono(xh, 100, f"first key greater than 70: index {hi_i}", size=8.5, fill=INK, weight="600")
    s += line(xl, 106, xl, y1, stroke=INK, sw=1.2, marker="arrow")
    s += line(xh, 106, xh, y1, stroke=INK, sw=1.2, marker="arrow")
    yk = y1 + ch + 20
    s += f'<path d="M {x0 + lo_i * cw + 2} {yk} V {yk + 6} H {x0 + hi_i * cw - 2} V {yk}" fill="none" stroke="{LINK}" stroke-width="1.2"/>'
    s += mono(x0 + (lo_i + hi_i) / 2 * cw, yk + 20, f"read {d.OQ['range_reads']} neighbours", size=8.5, fill=LINK,
              weight="600")
    s += mono(x0, yk + 20, f"two boundary searches: {d.OQ['range_comparisons_sorted']} comparisons", size=8.5,
              fill=INK, anchor="start", weight="600")
    # ---- row 2: the floor of 60
    y2 = 278
    s += title(32, y2 - 22, "sorted array: the largest key ≤ 60, and the nearest to 60")
    for i, k in enumerate(keys):
        if i == fl_i:
            s += cell(x0 + i * cw, y2, cw, ch, k, fill=ACCENT, stroke=ACCENT, tcolor="#ffffff", weight="600")
        elif i == fl_i + 1:
            s += cell(x0 + i * cw, y2, cw, ch, k, fill=blend(ACCENT_RGB, 0.12), stroke=ACCENT, sw=1.3)
        else:
            s += cell(x0 + i * cw, y2, cw, ch, k)
    xf = x0 + (fl_i + 1) * cw + cw / 2
    s += line(xf, y2 + ch + 26, xf, y2 + ch, stroke=ACCENT, sw=1.2, marker="arrow-accent")
    s += mono(xf, y2 + ch + 40, f"first key greater than 60: index {fl_i + 1}; the floor is the key before it, "
                                f"{d.OQ['floor']}, in {d.OQ['floor_comparisons_sorted']} comparisons",
              size=8.5, fill=ACCENT, weight="600")
    s += mono(xf, y2 + ch + 55, f"the nearest key is {d.OQ['floor']} or {keys[fl_i + 1]}: here {d.OQ['nearest_to_60']}",
              size=8, fill=MUTED)
    # ---- row 3: a hash table, as a labelled model
    y3 = 432
    s += line(32, y3 - 44, vw - 32, y3 - 44, stroke=RULE, sw=0.8)
    s += title(32, y3 - 22, f"hash table, a model with {d.BUCKETS} buckets: bucket = key mod {d.BUCKETS}")
    buckets = {b: [k for k in keys if k % d.BUCKETS == b] for b in range(d.BUCKETS)}
    for b in range(d.BUCKETS):
        x = x0 + b * cw
        s += mono(x + cw / 2, y3 - 7, str(b), size=7.5, fill=SOFT)
        s += rect(x, y3, cw, 8, fill=blend(INK_RGB, 0.10), stroke="rgba(45,49,66,0.30)")
        for j, k in enumerate(buckets[b]):
            inr = k in d.OQ["range_keys"]
            s += cell(x + 4, y3 + 12 + j * 30, cw - 8, 26, k, fill=blend(LINK_RGB, 0.14) if inr else "#ffffff",
                      stroke=LINK if inr else "rgba(45,49,66,0.30)", sw=1.3 if inr else 0.8, size=10)
    s += mono(x0, y3 + 118, f"the range's five keys land in buckets "
                            f"{', '.join(str(k % d.BUCKETS) for k in sorted(d.OQ['range_keys'], key=lambda k: k % d.BUCKETS))}"
                            f": a range query must look at all {d.OQ['range_scan_visits']} keys",
              size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(x0, y3 + 134, f"for integer keys only, it can instead probe each of the {d.OQ['range_integer_probes']} "
                            f"values 40, 41, …, 70", size=8, fill=MUTED, anchor="start")
    s += legend2(vh - 30, vw, [("a key in the range", (blend(LINK_RGB, 0.14), LINK), "tint-outline"),
                               ("the floor of 60", ACCENT, "fill"),
                               ("its successor", (blend(ACCENT_RGB, 0.12), ACCENT), "tint-outline")])
    return emit("04", "ordered-queries", "Order keeps a range in one piece",
                "The range from 40 to 70 and the floor of 60 on the sorted array, and the same 16 keys in a 16-bucket "
                "hash table drawn as a model (bucket = key mod 16). Counts from the lab.", "query types", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "sixteen keys with one shared hash")
    ax = Axes(96, 92, 760, 280, (1, 16), (0, 140))
    s += ax.frame(range(1, 17), [0, 20, 40, 60, 80, 100, 120, 140], xlab="keys inserted",
                  ylab="key comparisons so far (cumulative)")
    cpy = d.cumulative(d.COLL["insert_eq_calls"])
    model = d.cumulative(d.COLL["one_list_model"])
    spread = d.cumulative(d.SPREAD["insert_eq_calls"])
    X = lambda k: ax.X(k + 1)
    # the eight inserts that pay one extra comparison
    extra = [i for i, e in enumerate(d.COLL["extra_vs_model"]) if e]
    s += rect(X(extra[0]) - 10, ax.y0, X(extra[-1]) - X(extra[0]) + 20, ax.h, fill=blend(ACCENT_RGB, 0.06),
              stroke="none", sw=0)
    s += mono(X(extra[0]) - 4, ax.y0 + 14, f"inserts {extra[0] + 1} to {extra[-1] + 1}: the probe sequence passes "
                                           f"the first key's slot twice", size=8, fill=ACCENT, anchor="start")
    s += polyline([(X(i), ax.Y(v)) for i, v in enumerate(model)], INK, sw=1.6, dash="5,3")
    s += polyline([(X(i), ax.Y(v)) for i, v in enumerate(cpy)], ACCENT, sw=2.2)
    for i, v in enumerate(cpy):
        s += dot(X(i), ax.Y(v), 3.0, fill=ACCENT)
    s += polyline([(X(i), ax.Y(v)) for i, v in enumerate(spread)], LINK, sw=2.2)
    for i, v in enumerate(spread):
        s += dot(X(i), ax.Y(v), 3.0, fill=LINK)
    tx = ax.x0 + ax.w + 12
    s += mono(tx, ax.Y(cpy[-1]) + 3, f"{cpy[-1]}  CPython", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(tx, ax.Y(model[-1]) + 6, f"{model[-1]}  one list", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(tx, ax.Y(model[-1]) + 18, "= 0 + 1 + … + 15", size=8, fill=MUTED, anchor="start")
    s += mono(tx, ax.Y(0) + 3, f"{spread[-1]}  spread", size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(32, vh - 64, f"Measured in CPython 3.14.4 by counting __eq__ calls. Looking up the last key then takes "
                           f"{d.COLL['lookup_97_eq_calls']} comparisons, against {d.SPREAD['lookup_97_eq_calls']} with "
                           f"spread hashes.", size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 30, vw, [("CPython dict, one shared hash", ACCENT, "dot-solid"),
                               ("one-list model", INK, "dash"), ("ordinary integer hashes", LINK, "dot-solid")])
    return emit("05", "hash-flooding", "Collisions turn a hash table back into a list",
                "Cumulative key comparisons while 16 keys go into a hash table: all keys sharing one hash, in a one-list "
                "model and in CPython's own dict, against the same keys with their ordinary hashes.", "flooding", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 480
    s = eyebrow(32, 40, "the break-even grows like log n")
    ax = Axes(96, 92, 760, 280, (16, 1 << 20), (0, 40), xmap=math.log2)
    xt = [1 << k for k in range(4, 21, 2)]
    s += ax.frame(xt, [0, 10, 20, 30, 40], xlab="keys n (log scale)", ylab="lookups that repay a worst-case merge sort",
                  xfmt=lambda v: f"{v:,}")
    rows = d.SCALE_ROWS
    hits = [(ax.X(r["n"]), ax.Y(r["q_hits"])) for r in rows]
    miss = [(ax.X(r["n"]), ax.Y(r["q_misses"])) for r in rows]
    mh = [(ax.X(r["n"]), ax.Y(2 * math.log2(r["n"]) - 2)) for r in rows]
    mm = [(ax.X(r["n"]), ax.Y(math.log2(r["n"]) - 1)) for r in rows]
    s += polyline(mh, ACCENT, sw=1.0, dash="1.5,2.5")
    s += polyline(mm, LINK, sw=1.0, dash="1.5,2.5")
    s += polyline(hits, ACCENT, sw=2.0)
    s += polyline(miss, LINK, sw=2.0)
    for x, y in hits:
        s += dot(x, y, 3.0, fill=ACCENT)
    for x, y in miss:
        s += dot(x, y, 3.0, fill=LINK)
    first, last = rows[0], rows[-1]
    s += mono(hits[0][0] + 8, hits[0][1] - 22, f"{fmt(first['q_hits'])} at 16 keys", size=8.5, fill=ACCENT,
              anchor="start", weight="600")
    s += mono(miss[0][0] + 8, miss[0][1] + 22, f"{fmt(first['q_misses'])}", size=8.5, fill=LINK, anchor="start",
              weight="600")
    tx = ax.x0 + ax.w + 12
    s += mono(tx, hits[-1][1] + 3, f"{fmt(last['q_hits'])} hits", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(tx, miss[-1][1] + 3, f"{fmt(last['q_misses'])} misses", size=8.5, fill=LINK, anchor="start", weight="600")
    s += mono(32, vh - 64, "Exact counts at every power of two: counted directly up to 4,096 keys, by the same "
                           "recursion beyond. Thin dotted lines are the models, not data.", size=8, fill=SOFT, anchor="start")
    s += legend2(vh - 30, vw, [("successful lookups", ACCENT, "dot-solid"), ("model 2 log₂ n − 2", ACCENT, "dot-line"),
                               ("failed lookups", LINK, "dot-solid"), ("model log₂ n − 1", LINK, "dot-line")])
    return emit("06", "break-even-by-n", "Lookups needed to repay a sort, from 16 keys to a million",
                "The break-even lookup count for a worst-case merge sort against scanning, for successful and failed "
                "lookups, at every power of two from 16 to 2^20 keys.", "the math", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06}

if __name__ == "__main__":
    for k in sys.argv[1:] or list(FIGS):
        FIGS[k]()
