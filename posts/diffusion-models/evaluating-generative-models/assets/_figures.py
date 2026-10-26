#!/usr/bin/env python3
"""Figures for "Evaluating Generative Models: What FID Measures and Hides" (diffusion-models, part 9).

Every measured or computed number drawn here is read from ../lab/captures.json, the capture that the
article's lab download ships, so the prose, the figures and the lab cannot drift apart. Figure 2 is a
hand-placed diagram of the published pipeline; Figure 7 is Stein et al.'s own figure (source route),
converted from its SVG without change by `python3 _figures.py 7`.

    python3 _figures.py            # every figure plus the cover
    python3 _figures.py 3 5        # just those
    python3 _figures.py cover      # just the cover
"""

from __future__ import annotations

import json
import math
import os
import pathlib
import subprocess
import tempfile

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, MONO, MUSTARD, MUTED, PAPER, PAPER2, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, emit, emit_cover, eyebrow, label, mono, node, rect, text, zconn, h_arrow,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP_PATH = pathlib.Path(os.environ.get("P9_CAPTURES", HERE.parent / "lab" / "captures.json"))
BLOG = HERE.parent / "blog.md"
_CAP = None


def cap():
    global _CAP
    if _CAP is None:
        _CAP = json.loads(CAP_PATH.read_text(encoding="utf-8"))
    return _CAP


def alt_checked(value):
    """The alt text drawn into the SVG must be the same string blog.md carries."""
    if f"![{value}](" not in BLOG.read_text(encoding="utf-8"):
        raise ValueError(f"alt text not found in blog.md: {value}")
    return value


# ------------------------------------------------------------------ primitives (as in part 8)

class Axes:
    """Data-to-pixel mapping for a real plot; logy puts the y axis on log10."""

    _n = 0

    def __init__(self, x, y, w, h, xr, yr, logy=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr, self.logy = xr, yr, logy
        Axes._n += 1
        self.clip = f"clip{Axes._n}"

    def X(self, v):
        assert self.xr[0] - 1e-12 <= v <= self.xr[1] + 1e-12, f"x value {v} outside {self.xr}"
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        if self.logy:
            v = math.log10(v)
        assert self.yr[0] - 1e-12 <= v <= self.yr[1] + 1e-12, f"y value {v} outside {self.yr}"
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def frame(self, xticks=(), yticks=(), xlabel="", ylabel="", grid=True):
        out = (f'<defs><clipPath id="{self.clip}"><rect x="{self.x}" y="{self.y - 2}" '
               f'width="{self.w}" height="{self.h + 4}"/></clipPath></defs>')
        base = self.y + self.h
        out += (f'<line x1="{self.x}" y1="{base}" x2="{self.x + self.w}" y2="{base}" stroke="{RULE_SOLID}" stroke-width="1"/>'
                f'<line x1="{self.x}" y1="{base}" x2="{self.x}" y2="{self.y}" stroke="{RULE_SOLID}" stroke-width="1"/>')
        for v, lab in xticks:
            px = self.X(v)
            out += f'<line x1="{px:.1f}" y1="{base}" x2="{px:.1f}" y2="{base + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
            out += mono(px, base + 16, lab, 7, SOFT)
        for v, lab in yticks:
            py = self.Y(v)
            if grid:
                out += f'<line x1="{self.x}" y1="{py:.1f}" x2="{self.x + self.w}" y2="{py:.1f}" stroke="{RULE}" stroke-width="0.8"/>'
            out += mono(self.x - 10, py + 3, lab, 7, SOFT, "end")
        if xlabel:
            out += mono(self.x + self.w / 2, base + 34, xlabel, 8, SOFT)
        if ylabel:
            cx, cy = self.x - 48, self.y + self.h / 2
            out += f'<g transform="rotate(-90 {cx} {cy})">' + mono(cx, cy, ylabel, 8, SOFT) + '</g>'
        return out

    def path(self, pts, colour=INK, width=1.8, dash=None):
        d = {True: ' stroke-dasharray="6,4"', "dot": ' stroke-dasharray="1.5,3.5"'}.get(dash, "")
        s = " ".join(f"{self.X(a):.1f},{self.Y(b):.1f}" for a, b in pts)
        return (f'<g clip-path="url(#{self.clip})"><polyline points="{s}" fill="none" stroke="{colour}" '
                f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{d}/></g>')

    def dot(self, a, b, r=4, colour=INK, hollow=False):
        if hollow:
            return (f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{PAPER}" '
                    f'stroke="{colour}" stroke-width="1.6"/>')
        return f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{colour}"/>'

    def hline(self, v, colour=SOFT, dash=True, width=1.0):
        d = ' stroke-dasharray="5,4"' if dash else ""
        return (f'<line x1="{self.x}" y1="{self.Y(v):.1f}" x2="{self.x + self.w}" y2="{self.Y(v):.1f}" '
                f'stroke="{colour}" stroke-width="{width}"{d}/>')


def plate(x, y, w, h=16):
    return rect(x, y, w, h, PAPER, "none", 3)


def tag(x, y, value, fill=INK, anchor="middle", size=9, weight=500, bg=True, w=None):
    """A label on an opaque plate so a line passing behind it cannot cut it."""
    w = w or len(value) * size * 0.62 + 10
    left = x - w / 2 if anchor == "middle" else (x - 5 if anchor == "start" else x - w + 5)
    out = plate(left, y - size - 2, w, size + 7) if bg else ""
    return out + text(x, y, value, size, fill, MONO, weight, anchor)


def footnote(y, value, x=40, vw=960):
    """A source line under a figure; a line that would leave the canvas is a defect, so refuse it."""
    if x + len(value) * 5.95 > vw - 24:
        raise ValueError(f"footnote too long for the canvas ({len(value)} chars): {value[:60]}...")
    return mono(x, y, value, 8, SOFT, "start")


def grey(v, lo, hi):
    """High value = bright: the series' display convention for patches."""
    u = min(1.0, max(0.0, (v - lo) / (hi - lo)))
    return round(26 + u * (250 - 26))


def png_gray(rows):
    """A greyscale PNG from rows of 0..255 ints, stdlib only."""
    import base64
    import struct
    import zlib
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()


LO, HI = -2.0, 2.6           # one display range for every 8x8 tile, high value = bright


def tile(x, y, size, flat, side=8, lo=LO, hi=HI, stroke=RULE_SOLID, sw=0.8):
    rows = [[grey(flat[r * side + c], lo, hi) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>' + rect(x, y, size, size, "none", stroke, 0, sw))


def legend_row(x, y, items, gap=22):
    """Inline legend: (label, colour, dash) with a short stroke sample each."""
    out = ""
    for lab, colour, dash in items:
        d = {True: ' stroke-dasharray="6,4"', "dot": ' stroke-dasharray="1.5,3.5"'}.get(dash, "")
        out += f'<line x1="{x}" y1="{y - 4}" x2="{x + 22}" y2="{y - 4}" stroke="{colour}" stroke-width="2.2"{d}/>'
        out += mono(x + 28, y, lab, 8, MUTED, "start")
        x += 40 + len(lab) * 6.2 + gap
    return out


def f4(v):
    return f"{v:.4f}"


def pct(v, digits=1):
    return f"{100 * v:.{digits}f}%"


# -------------------------------------------------------------------- fig 01

def fig01():
    """The worked example on number lines: three generators, their bells and their FD."""
    vw, vh = 960, 650
    W = cap()["worked"]
    real = W["real"]["values"]
    m_r, s_r = W["real"]["mean"], W["real"]["sd"]
    rows = [("real contrasts", real, m_r, s_r, None)]
    rows += [(name, g["values"], g["mean"], g["sd"], g) for name, g in W["generators"].items()]
    lo, hi = 0.25, 1.25
    x0, x1 = 160, 640

    def X(v):
        assert lo <= v <= hi, v
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    near = 0.05
    zones = []
    for r in sorted(real):
        a, b = r - near, r + near
        if zones and a <= zones[-1][1] + 1e-9:
            zones[-1][1] = max(zones[-1][1], b)
        else:
            zones.append([a, b])
    top, row_h = 92, 112
    body = eyebrow(40, 34, "worked example · each image reduced to one number: its crescent contrast")
    for a, b in zones:
        body += rect(X(a), top - 6, X(b) - X(a), row_h * len(rows) + 4, PAPER2, "none", 0)
    for za, zb in zones:
        body += mono((X(za) + X(zb)) / 2, top - 14, f"WITHIN {near:.2f} OF A REAL CONTRAST", 7, SOFT)

    def bell(m, s, base, colour, dash=False, height=40):
        pts = []
        for i in range(401):
            v = lo + (hi - lo) * i / 400
            pts.append(f"{X(v):.1f},{base - 12 - height * math.exp(-0.5 * ((v - m) / s) ** 2):.1f}")
        d = ' stroke-dasharray="5,4"' if dash else ""
        return f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colour}" stroke-width="1.8"{d}/>'

    for i, (name, vals, m, s, g) in enumerate(rows):
        base = top + 70 + i * row_h
        body += text(40, base - 44, name, 13, INK, SANS, 600, "start")
        body += f'<line x1="{X(lo)}" y1="{base}" x2="{X(hi)}" y2="{base}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        body += bell(m_r, s_r, base, SOFT, dash=True)
        if g is not None:
            body += bell(m, s, base, BLUE)
            if abs(m - m_r) < 1e-9 and abs(s - s_r) < 1e-9:
                body += tag(X(m_r), base - 58, "same bell as the real data", BLUE, size=8)
        seen = {}
        for v in vals:
            k = seen.get(v, 0)
            seen[v] = k + 1
            cy = base + k * 11
            ok = min(abs(v - r) for r in real) <= near + 1e-9
            if ok:
                body += f'<circle cx="{X(v):.1f}" cy="{cy}" r="4.6" fill="{INK}"/>'
            else:
                body += f'<circle cx="{X(v):.1f}" cy="{cy}" r="4.6" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.8"/>'
        tx = 676
        if g is None:
            body += mono(tx, base - 30, f"mean {f4(m)}", 9, INK, "start", 500)
            body += mono(tx, base - 14, f"spread {f4(s)}", 9, INK, "start", 500)
        else:
            assert abs(g["mean_term"] + g["spread_term"] - g["fd"]) < 1e-6
            body += mono(tx, base - 38, f"mean {f4(m)} · spread {f4(s)}", 8, MUTED, "start")
            body += mono(tx, base - 20, f"FD = {f4(g['mean_term'])} + {f4(g['spread_term'])}", 9, INK, "start", 500)
            body += text(tx, base + 2, f"= {f4(g['fd'])}", 15, INK, SANS, 600, "start")
            body += mono(tx + 90, base + 1, f"{g['within_0.05_of_a_real']} of 8 within 0.05", 8, MUTED, "start")
    axis_y = top + 70 + (len(rows) - 1) * row_h + 34
    for v in (0.3, 0.5, 0.7, 0.9, 1.1):
        body += f'<line x1="{X(v):.1f}" y1="{axis_y - 4}" x2="{X(v):.1f}" y2="{axis_y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        body += mono(X(v), axis_y + 12, f"{v:.1f}", 7, SOFT)
    body += f'<line x1="{X(lo)}" y1="{axis_y}" x2="{X(hi)}" y2="{axis_y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    faint_c, strong_c = cap()["world"]["contrasts"]
    body += mono((x0 + x1) / 2, axis_y + 26, f"CRESCENT CONTRAST (FAINT {faint_c}, STRONG {strong_c})", 8, SOFT)
    ly = axis_y + 50
    body += legend_row(160, ly, [("bell with the row's mean and spread", BLUE, False), ("the real bell", SOFT, True)])
    body += f'<circle cx="610" cy="{ly - 4}" r="4.6" fill="{INK}"/>' + mono(620, ly, "near a real value", 8, MUTED, "start")
    body += (f'<circle cx="740" cy="{ly - 4}" r="4.6" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.8"/>'
             + mono(750, ly, f"farther than {near:.2f}", 8, MUTED, "start"))
    body += footnote(vh - 22, "Computed by evaluate.py worked. Spread divides by 8; bells drawn to equal height; repeated values stack.")
    emit(1, "fd-on-one-number", "FD on one number",
         "The moment-matched generator scores a perfect 0 while half its values fall between the real clusters", body,
         alt_checked("Number lines of eight real crescent contrasts and three generators, with each generator's mean, "
                     "spread and Fréchet distance"), vw, vh)


# -------------------------------------------------------------------- fig 02

def fig02():
    """The FID pipeline with a shape on every edge and the five protocol choices tagged."""
    vw, vh = 960, 560
    d = 2048
    distinct = d * (d + 1) // 2
    yr, yg, hgt = 150, 330, 66
    span_y, span_h = yr, yg + hgt - yr
    cols = {"img": (24, 124), "resize": (200, 84), "incep": (336, 112), "feat": (500, 108), "mom": (660, 116),
            "fd": (820, 116)}
    body = eyebrow(24, 34, "how fid is computed · the same chain for both sets")
    x, w = cols["img"]
    body += node(x, yr, w, hgt, "Real images", "the reference set")
    body += node(x, yg, w, hgt, "Generated images", "50,000 samples")
    x, w = cols["resize"]
    body += node(x, span_y, w, span_h, "Resize", "to 299 × 299")
    x, w = cols["incep"]
    body += node(x, span_y, w, span_h, "Inception-v3", "ImageNet-trained", kind="soft")
    for y in (yr, yg):
        x, w = cols["feat"]
        body += node(x, y, w, hgt, "pool3 features", f"{d:,} per image")
        x, w = cols["mom"]
        body += node(x, y, w, hgt, "Mean, covariance", f"{d:,} + {d:,}²")
    x, w = cols["fd"]
    body += node(x, 236, w, 74, "Fréchet distance", "one number", kind="focal")

    def edge_label(x1, x2, y, value):
        tw = len(value) * 5.3 + 8
        assert tw <= x2 - x1 - 4, f"edge label {value} too wide for its gap"
        cx = (x1 + x2) / 2
        return rect(cx - tw / 2, y - 22, tw, 14, PAPER, "none", 2) + mono(cx, y - 12, value, 7.5, SOFT)

    order = ("img", "resize", "incep", "feat", "mom")
    labels = ("H×W×3", "299²×3", "2,048", "N×2,048")
    for y in (yr + hgt / 2, yg + hgt / 2):
        for a, b in zip(order[:-1], order[1:]):
            x1 = cols[a][0] + cols[a][1]
            x2 = cols[b][0]
            body += h_arrow(x1, y, x2 - 2)
    for (a, b), lab in zip(zip(order[:-1], order[1:]), labels):
        body += edge_label(cols[a][0] + cols[a][1], cols[b][0], yr + hgt / 2, lab)
    mx0 = cols["mom"][0] + cols["mom"][1]
    body += zconn(mx0, yr + hgt / 2, cols["fd"][0] - 2, 258, mx=mx0 + 22)
    body += zconn(mx0, yg + hgt / 2, cols["fd"][0] - 2, 288, mx=mx0 + 22)
    body += mono(mx0 + 22, yr + hgt / 2 - 10, "μ, Σ", 8, SOFT)
    body += mono(mx0 + 22, yg + hgt / 2 + 20, "μ, Σ", 8, SOFT)

    def ptag(cx, y, value):
        w = len(value) * 6.0 + 16
        return rect(cx - w / 2, y - 12, w, 18, ACCENT_TINT, ACCENT, 3, 1) + mono(cx, y + 1, value, 8, ACCENT, "middle", 500)

    def link(cx, y1, y2):
        return f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2}" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="3,3"/>'
    ic = cols["img"][0] + cols["img"][1] / 2
    body += ptag(ic, 104, "1 · REFERENCE SET") + link(ic, 110, yr)
    body += ptag(ic, 276, "2 · FILE FORMAT") + link(ic, 264, yr + hgt) + link(ic, 282, yg)
    body += ptag(ic, 444, "3 · SAMPLE COUNT N") + link(ic, yg + hgt, 432)
    rc = cols["resize"][0] + cols["resize"][1] / 2
    body += ptag(rc + 20, 104, "4 · RESIZE FILTER") + link(rc, 110, span_y)
    nc = cols["incep"][0] + cols["incep"][1] / 2
    body += ptag(nc + 50, 104, "5 · WEIGHTS AND CODE") + link(nc, 110, span_y)
    body += f'<line x1="24" y1="{vh - 82}" x2="{vw - 24}" y2="{vh - 82}" stroke="{RULE}" stroke-width="0.8"/>'
    body += text(24, vh - 58, f"After the Inception box, each set is {d:,} means and {distinct:,} distinct covariances; "
                 "a difference those numbers miss is invisible.", 12, INK, SANS, 500, "start")
    body += footnote(vh - 22, "Pipeline: Heusel et al. 2017 (pool3 features, Fréchet distance); the 299 × 299 resize of "
                              "the reference code (Parmar et al. 2022).", x=24)
    emit(2, "how-fid-is-computed", "How FID is computed",
         "Everything FID knows about a set of images is a mean vector and a covariance matrix", body,
         alt_checked("FID pipeline: real and generated images resized to 299 px, Inception-v3 pool3 features, "
                     "means and covariances, one Fréchet distance"), vw, vh)


# -------------------------------------------------------------------- fig 03

ORDER = ("perfect", "drops faint", "grainy", "gaussian", "copier")


def fig03():
    """Five generators: samples, FD and the k-NN metrics, with what is actually wrong with each."""
    vw, vh = 960, 640
    F = cap()["failures"]
    S, data = F["sets"], F["data"]
    truth = {
        "perfect": "fresh draws from the true distribution",
        "drops faint": f"faint crescents {pct(S['drops faint']['faint'])} (real {pct(data['faint'])})",
        "grainy": f"pixel noise {S['grainy']['detail_sd']:.3f} (real {data['detail_sd']:.3f})",
        "gaussian": f"{pct(S['gaussian']['off_contrast'])} impossible contrasts (real {pct(data['off_contrast'])})",
        "copier": "returns training images",
    }
    assert S["drops faint"]["fd"] == S["grainy"]["fd"]
    names = {"perfect": "Perfect", "drops faint": "Drops faint", "grainy": "Grainy", "gaussian": "Gaussian blob",
             "copier": "Copier"}
    body = eyebrow(40, 34, f"crescent world · {F['n']:,} samples per generator · training set {F['n_train']:,} · "
                           "fd on the 64 pixel values")
    cols = {"fd": 600, "precision": 690, "recall": 780, "coverage": 870}
    hy = 78
    body += mono(cols["fd"], hy, "FD", 8, INK, "middle", 600)
    for k in ("precision", "recall", "coverage"):
        body += mono(cols[k] + 26, hy, k.upper(), 8, INK, "middle", 600)
    size, gap, tx0, row_h, y0 = 46, 6, 246, 100, 100
    for i, key in enumerate(ORDER):
        st = S[key]
        y = y0 + i * row_h
        body += text(40, y + 22, names[key], 13, INK, SANS, 600, "start")
        sub = truth[key]
        if len(sub) > 38:
            cut = sub.rfind(" ", 0, 38)
            body += mono(40, y + 40, sub[:cut], 7.5, MUTED, "start")
            body += mono(40, y + 52, sub[cut + 1:], 7.5, MUTED, "start")
        else:
            body += mono(40, y + 40, sub, 7.5, MUTED, "start")
        for j, img in enumerate(st["samples"][:6]):
            body += tile(tx0 + j * (size + gap), y + 6, size, img)
        tied = key in ("drops faint", "grainy")
        body += text(cols["fd"], y + 36, f4(st["fd"]), 14, ACCENT if tied else INK, SANS, 600, "middle")
        for k in ("precision", "recall", "coverage"):
            v = st[k]
            bx, by = cols[k], y + 18
            body += rect(bx, by, 52, 8, "rgba(45,49,66,0.08)", "none", 1)
            body += rect(bx, by, max(0.5, 52 * min(v, 1.0)), 8, MUTED, "none", 1)
            body += mono(bx + 26, by + 26, f"{v:.4f}" if 0 < v < 0.001 else f"{v:.3f}", 9, INK, "middle", 500)
    # the tie: a bracket left of the FD column spanning the two tied rows
    by1, by2 = y0 + 1 * row_h + 30, y0 + 2 * row_h + 30
    bx = cols["fd"] - 36
    assert bx > tx0 + 6 * (size + gap), "bracket would cut the tiles"
    body += (f'<path d="M{bx + 6},{by1} H{bx} V{by2} H{bx + 6}" fill="none" stroke="{ACCENT}" stroke-width="1.6"/>')
    body += mono(bx - 6, (by1 + by2) / 2 + 3, "SAME FD", 7.5, ACCENT, "end", 600)
    body += footnote(vh - 38, f"Measured by evaluate.py failures. Precision and recall k = 3, density and coverage k = 5; "
                              f"grain tuned to {F['grain']:.4f}.")
    body += footnote(vh - 22, f"Tiles: six samples per generator, one display range ({LO} to {HI}) for all, bright = high.")
    emit(3, "same-fd-different-failures", "Same FD, different failures",
         "A faint-dropper and a grainy generator tie; precision, recall and coverage tell them apart", body,
         alt_checked(f"8x8 samples from five generators with FD, precision, recall and coverage: drops-faint and grainy "
                     f"tie at FD {S['grainy']['fd']:.4f}"), vw, vh)


# -------------------------------------------------------------------- fig 04

def fig04():
    """One number, k = 2 balls: a stray generated sample buys recall; coverage does not move."""
    vw, vh = 960, 640
    P = cap()["worked"]["prdc"]
    real, k = P["real"], P["k"]
    n0 = len(P["sets"]["strong only"]["fake"])
    lo, hi = 0.0, 1.3
    x0, x1 = 150, 700

    def X(v):
        return x0 + (min(max(v, lo), hi) - lo) / (hi - lo) * (x1 - x0)

    ticks = (0.0, 0.25, 0.5, 0.75, 1.0, 1.25)
    axis_y = 560
    body = eyebrow(40, 34, f"one number per image · every ball reaches the sample's {k}nd-nearest neighbour in its own set")
    for v in ticks:
        body += f'<line x1="{X(v):.1f}" y1="70" x2="{X(v):.1f}" y2="{axis_y}" stroke="{RULE}" stroke-width="0.8"/>'
    panels = (("strong only", "Generated: strong crescents only"),
              ("strong + one stray", "Generated: the same, plus one stray sample"))
    for pi, (key, title) in enumerate(panels):
        st = P["sets"][key]
        fake, rr, rf = st["fake"], st["real_radii"], st["fake_radii"]
        top = 64 + pi * 246
        body += plate(36, top + 4, len(title) * 7.2 + 12, 20) + text(40, top + 18, title, 13, INK, SANS, 600, "start")
        yr, yf = top + 100, top + 150
        body += mono(40, yr + 3, "REAL", 8, MUTED, "start", 600)
        body += mono(40, yf + 3, "GENERATED", 8, MUTED, "start", 600)
        for y in (yr, yf):
            body += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        half = len(real) // 2                      # five faint, then five strong: one lane per ball in each cluster
        for i, (v, r) in enumerate(zip(real, rr)):
            ly = yr - 12 - (i % half) * 7
            body += (f'<line x1="{X(v - r):.1f}" y1="{ly}" x2="{X(v + r):.1f}" y2="{ly}" stroke="{MUTED}" '
                     f'stroke-width="2.2" stroke-linecap="round"/>')
        for i, (v, r) in enumerate(zip(fake, rf)):
            stray = i >= n0
            ly = yf + 12 + (n0 * 7 + 4 if stray else (i % n0) * 7)
            col = ACCENT if stray else BLUE
            body += (f'<line x1="{X(v - r):.1f}" y1="{ly}" x2="{X(v + r):.1f}" y2="{ly}" stroke="{col}" '
                     f'stroke-width="{2.6 if stray else 2.2}" stroke-linecap="round"/>')
            if stray:
                if v - r < lo:
                    body += (f'<path d="M{X(lo) + 8},{ly - 5} L{X(lo)},{ly} L{X(lo) + 8},{ly + 5}" fill="none" '
                             f'stroke="{ACCENT}" stroke-width="1.6"/>')
                body += tag((X(max(v - r, lo)) + X(v + r)) / 2, ly + 20, f"stray at {v:.2f}: ball radius {r:.2f}",
                            ACCENT, size=8)
        for v in real:
            inside = any(abs(v - f) <= r + 1e-9 for f, r in zip(fake, rf))
            only_stray = inside and not any(abs(v - f) <= r + 1e-9 for f, r in zip(fake[:n0], rf[:n0]))
            body += f'<circle cx="{X(v):.1f}" cy="{yr}" r="4.6" fill="{INK}"/>'
            if only_stray:
                body += f'<circle cx="{X(v):.1f}" cy="{yr}" r="8" fill="none" stroke="{ACCENT}" stroke-width="1.6"/>'
        for v in fake:
            body += f'<circle cx="{X(v):.1f}" cy="{yf}" r="4.6" fill="{BLUE}"/>'
        mx = 740
        body += rect(mx, top + 52, 192, 132, "#ffffff", RULE_SOLID, 6, 1)
        for j, field in enumerate(("precision", "recall", "density", "coverage")):
            yy = top + 80 + j * 28
            hot = pi == 1 and field == "recall"
            body += mono(mx + 18, yy, field.upper(), 8, ACCENT if hot else MUTED, "start", 600)
            body += text(mx + 176, yy + 1, f"{st[field]:.3f}", 14, ACCENT if hot else INK, SANS, 600, "end")
    for v in ticks:
        body += f'<line x1="{X(v):.1f}" y1="{axis_y}" x2="{X(v):.1f}" y2="{axis_y + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        body += mono(X(v), axis_y + 16, f"{v:.2f}", 7, SOFT)
    body += f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    body += mono((x0 + x1) / 2, axis_y + 32, "CRESCENT CONTRAST", 8, SOFT)
    ly = vh - 22
    body += f'<line x1="{x0}" y1="{ly - 4}" x2="{x0 + 22}" y2="{ly - 4}" stroke="{MUTED}" stroke-width="2.2"/>'
    body += mono(x0 + 28, ly, "a real sample's ball", 8, MUTED, "start")
    body += f'<line x1="{x0 + 190}" y1="{ly - 4}" x2="{x0 + 212}" y2="{ly - 4}" stroke="{BLUE}" stroke-width="2.2"/>'
    body += mono(x0 + 218, ly, "a generated sample's ball", 8, MUTED, "start")
    body += (f'<circle cx="{x0 + 420}" cy="{ly - 4}" r="8" fill="none" stroke="{ACCENT}" stroke-width="1.6"/>'
             + mono(x0 + 434, ly, "credited to recall only by the stray's ball", 8, MUTED, "start"))
    emit(4, "one-stray-sample-buys-recall", "One stray sample buys recall",
         "Recall builds balls around generated samples, so one isolated sample can claim a whole missing mode", body,
         alt_checked("Number line of real and generated contrasts with k-NN balls: one stray generated sample's wide ball "
                     "lifts recall to 100%"), vw, vh)


# -------------------------------------------------------------------- fig 05

WS = ("1.0", "1.5", "2.0", "3.0", "4.0", "5.0", "7.5")


def fig05():
    """Guidance weight against every metric, on part 8's exact-model samples, with the truth (faint share)."""
    vw, vh = 960, 580
    G = cap()["guidance"]["weights"]
    ws = [float(w) for w in WS]
    body = eyebrow(40, 34, f"part 8's guided samples, exact model · {cap()['guidance']['n']:,} samples per weight · "
                           "real class-0 images as the reference")
    a = Axes(110, 80, 300, 330, (1.0, 7.5), (-3, 1.5), logy=True)
    body += text(110, 66, "FD (log scale)", 12, INK, SANS, 600, "start")
    body += a.frame(xticks=[(w, f"{w:g}") for w in ws], yticks=[(1e-3, "0.001"), (1e-2, "0.01"), (1e-1, "0.1"), (1.0, "1"), (10.0, "10")],
                    xlabel="GUIDANCE WEIGHT w")
    body += a.path([(w, G[k]["fd"]) for w, k in zip(ws, WS)], INK, 2)
    for w, k in zip(ws, WS):
        body += a.dot(w, G[k]["fd"], 3.6, INK)
    base = G["data"]["fd"]
    body += a.hline(base, SOFT, True)
    body += tag(a.x + 70, a.Y(base) - 6, f"real against real {base:.4f}", SOFT, size=7.5)
    b = Axes(540, 80, 360, 330, (1.0, 7.5), (0.0, 1.4))
    body += text(540, 66, "Precision, recall, density, coverage", 12, INK, SANS, 600, "start")
    body += b.frame(xticks=[(w, f"{w:g}") for w in ws], yticks=[(v / 5, f"{v / 5:.1f}") for v in range(8)],
                    xlabel="GUIDANCE WEIGHT w")
    series = (("faint share (the truth)", "faint", SOFT, "dot"), ("precision", "precision", INK, False),
              ("recall", "recall", ACCENT, False), ("density", "density", SAGE, True), ("coverage", "coverage", BLUE, False))
    for name, key, colour, dash in series:
        body += b.path([(w, G[k][key]) for w, k in zip(ws, WS)], colour, 2.2 if key == "recall" else 1.8, dash)
        for w, k in zip(ws, WS):
            body += b.dot(w, G[k][key], 2.6 if key == "faint" else 3.2, colour)
    g75 = G["7.5"]
    lx, ly = b.x + b.w, b.Y(1.31)
    body += tag(lx, ly, f"recall {g75['recall']:.3f} at w = 7.5: {g75['faint_holders']} stray faint samples,", ACCENT, "end", size=8)
    body += tag(lx, ly + 14, f"ball radius {g75['faint_holder_radius_median']:.2f} against {g75['fake_radius_median']:.2f}",
                ACCENT, "end", size=8)
    rx, ry = b.X(7.5), b.Y(g75["recall"])
    body += f'<line x1="{rx - 2}" y1="{ry - 8}" x2="{rx - 2}" y2="{ly + 20}" stroke="{ACCENT}" stroke-width="1"/>'
    body += legend_row(110, 470, [(name, colour, dash) for name, _, colour, dash in series], gap=8)
    body += footnote(vh - 54, f"Real against real: precision {G['data']['precision']:.3f}, recall {G['data']['recall']:.3f}, "
                              f"density {G['data']['density']:.3f}, coverage {G['data']['coverage']:.3f}, faint share "
                              f"{pct(G['data']['faint'])}.")
    body += footnote(vh - 38, "Measured by evaluate.py guidance on the exact denoisers, 128 DDIM steps; precision and recall "
                              "k = 3, density and coverage k = 5.")
    body += footnote(vh - 22, "Faint share: generated samples whose crescent is faint (contrast below 0.75); "
                              f"it falls from {pct(G['1.0']['faint'])} to {pct(G['7.5']['faint'])}.")
    emit(5, "guidance-through-the-metrics", "Guidance through every metric",
         "Recall rebounds at w = 7.5 because four stray faint samples have huge balls; coverage keeps falling", body,
         alt_checked("FD, precision, recall, density and coverage against guidance weight: recall falls then rebounds "
                     "at w = 7.5, coverage keeps falling"), vw, vh)


# -------------------------------------------------------------------- fig 06

def fig06():
    """FD against 1/N with the fitted lines: the bias, and why only equal N compares."""
    vw, vh = 960, 560
    B = cap()["bias"]
    ns, reps = B["ns"], B["repeats"]
    gens = (("perfect", INK, "perfect generator"), ("grainy", MUSTARD, f"grain {B['grain']:.2f}"))
    a = Axes(120, 70, 600, 360, (0.0, 0.00105), (0.0, 0.11))
    body = eyebrow(40, 34, f"crescent world · {reps} repeats per point · reference of {B['n_ref']:,} images")
    ticks = [(0.0, "∞")] + [(1 / n, f"{n:,}") for n in ns if n <= 8000]
    body += a.frame(xticks=ticks, yticks=[(v / 100, f"{v / 100:.2f}") for v in range(0, 11, 2)],
                    xlabel="SAMPLES N  (AXIS LINEAR IN 1/N)", ylabel="FD")
    for key, colour, name in gens:
        g = B["gens"][key]
        body += a.path([(0.0, g["fd_inf"]), (0.001, g["fd_inf"] + g["slope"] * 0.001)], colour, 1.4, True)
        for n, m, s in zip(ns, g["fd_mean"], g["fd_sd"]):
            se = s / math.sqrt(reps)
            body += (f'<line x1="{a.X(1 / n):.1f}" y1="{a.Y(m - se):.1f}" x2="{a.X(1 / n):.1f}" y2="{a.Y(m + se):.1f}" '
                     f'stroke="{colour}" stroke-width="1.2"/>')
            body += a.dot(1 / n, m, 3.8, colour)
    p, gr = B["gens"]["perfect"], B["gens"]["grainy"]
    n_lo, n_hi = 1000, 4000                       # the cross-N comparison the article makes
    i1, i4 = ns.index(n_lo), ns.index(n_hi)
    assert p["fd_mean"][i1] > gr["fd_mean"][i4]
    for (n, m) in ((n_lo, p["fd_mean"][i1]), (n_hi, gr["fd_mean"][i4])):
        body += f'<circle cx="{a.X(1 / n):.1f}" cy="{a.Y(m):.1f}" r="9" fill="none" stroke="{ACCENT}" stroke-width="1.6"/>'
    body += tag(a.X(1 / n_lo) - 16, a.Y(p["fd_mean"][i1]) + 30, f"perfect at {n_lo:,}: {p['fd_mean'][i1]:.4f}", ACCENT, "end", size=8)
    body += tag(a.x + 8, a.Y(gr["fd_mean"][i4]) - 20, f"grain {B['grain']:.2f} at {n_hi:,}: {gr['fd_mean'][i4]:.4f}",
                ACCENT, "start", size=8)
    lx = 756
    body += text(lx, 96, "Fitted lines", 12, INK, SANS, 600, "start")
    body += mono(lx, 116, f"N ≥ {B['fit_from']:,}", 8, MUTED, "start")
    for j, (key, colour, name) in enumerate(gens):
        g = B["gens"][key]
        y = 148 + j * 46
        body += f'<line x1="{lx}" y1="{y - 4}" x2="{lx + 22}" y2="{y - 4}" stroke="{colour}" stroke-width="2.2"/>'
        body += mono(lx + 28, y, name, 8, MUTED, "start", 600)
        body += mono(lx + 28, y + 16, f"{g['fd_inf']:.4f} + {g['slope']:.1f}/N", 9, INK, "start", 500)
    body += mono(lx, 260, "First term: FD-infinity,", 8, MUTED, "start")
    body += mono(lx, 274, "the line read at 1/N = 0.", 8, MUTED, "start")
    body += footnote(vh - 38, "Measured by evaluate.py bias. Dots: mean FD over repeats; bars: one standard error. "
                              "Points left of 8,000 are 16,000 to 64,000.")
    body += footnote(vh - 22, "Dashed lines: the fit FD = FD-infinity + K/N on N of 2,000 or more, extended to N = 1,000.")
    emit(6, "fd-depends-on-n", "FD depends on N",
         "FD is biased upward by about K/N; only scores at the same N compare", body,
         alt_checked(f"FD against 1/N for a perfect and a slightly grainy generator: straight lines whose intercepts are "
                     f"{p['fd_inf']:.4f} and {gr['fd_inf']:.4f}"), vw, vh)


# -------------------------------------------------------------------- fig 07 (source route)

def fig07():
    """Stein et al. 2023, Figure 2, unchanged: the SVG as published, rasterised at 2x for the post."""
    svg = HERE / "fig-07-human-error-vs-fid.svg"
    if not svg.exists():
        raise SystemExit("fetch https://arxiv.org/html/2306.04675v2/summary.svg to fig-07-human-error-vs-fid.svg first")
    w_pt, h_pt = 732.84378, 306.3008                     # the SVG's own width and height, in points
    vw, vh = round(w_pt * 4 / 3), round(h_pt * 4 / 3)    # CSS pixels
    shim = (f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;width:{vw}px;height:{vh}px;'
            f'background:#fff;overflow:hidden}}img{{display:block;width:{vw}px;height:{vh}px}}</style>'
            f'<img src="{svg.resolve().as_uri()}">')
    with tempfile.TemporaryDirectory(prefix="diffusion-p9-src-") as temp:
        page = pathlib.Path(temp) / "shim.html"
        page.write_text(shim, encoding="utf-8")
        subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--allow-file-access-from-files", f"--user-data-dir={pathlib.Path(temp) / 'profile'}",
                        "--force-device-scale-factor=2", f"--window-size={vw},{vh}",
                        f"--screenshot={(HERE / 'fig-07-human-error-vs-fid.png').resolve()}", page.resolve().as_uri()],
                       check=True, capture_output=True, timeout=120)
    print("rendered fig-07-human-error-vs-fid (source, unchanged)")


# -------------------------------------------------------------------- cover

def cover():
    W = cap()["worked"]
    F = cap()["failures"]["sets"]
    body = eyebrow(72, 73, "diffusion · part nine")
    body += text(72, 148, "Evaluating generative models", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "what FID measures, and what one number hides", 15, MUTED, MONO, 400, "start")
    lo, hi, x0, x1 = 0.25, 1.25, 96, 556

    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    m_r, s_r = W["real"]["mean"], W["real"]["sd"]
    mm = W["generators"]["moment matched"]
    for row, (vals, colour, name) in enumerate(((W["real"]["values"], INK, "REAL"), (mm["values"], ACCENT, "MOMENT MATCHED"))):
        base = 318 + row * 112
        body += f'<line x1="{x0}" y1="{base}" x2="{x1}" y2="{base}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        pts = " ".join(f"{X(lo + (hi - lo) * i / 300):.1f},{base - 12 - 54 * math.exp(-0.5 * ((lo + (hi - lo) * i / 300 - m_r) / s_r) ** 2):.1f}"
                       for i in range(301))
        body += f'<polyline points="{pts}" fill="none" stroke="{MUTED}" stroke-width="2"/>'
        seen = {}
        for v in vals:
            k = seen.get(v, 0)
            seen[v] = k + 1
            near = min(abs(v - r) for r in W["real"]["values"]) <= 0.05 + 1e-9
            fill = f'fill="{INK}"' if near else f'fill="{PAPER}" stroke="{ACCENT}" stroke-width="2"'
            body += f'<circle cx="{X(v):.1f}" cy="{base + k * 12}" r="5.4" {fill}/>'
        body += mono(x0, base - 76, name, 9, MUTED, "start", 500)
    body += mono(x0, 486, f"SAME MEAN, SAME SPREAD: FD = {mm['fd']:.0f}", 9, ACCENT, "start", 600)
    size, gap = 64, 10
    for row, key in enumerate(("drops faint", "grainy")):
        y = 262 + row * 118
        for j, img in enumerate(F[key]["samples"][:4]):
            body += tile(660 + j * (size + gap), y, size, img)
        body += mono(660, y - 12, f"{key.upper()} · FD {F[key]['fd']:.4f}", 9, MUTED, "start", 500)
    body += f'<line x1="72" y1="528" x2="1128" y2="528" stroke="{RULE}" stroke-width="1"/>'
    body += text(72, 568, "One number cannot say whether a model lost quality or lost variety.", 20, MUTED, SERIF, 400,
                 "start", italic=True)
    emit_cover(body, alt_checked("Real and moment-matched crescent contrasts on number lines beside two crescent sample sets "
                                 f"that share the same FD of {F['grainy']['fd']:.4f}"))


FIGURES = {1: fig01, 2: fig02, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07}

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if not args:
        for f in FIGURES.values():
            f()
        cover()
    for arg in args:
        cover() if arg == "cover" else FIGURES[int(arg)]()
