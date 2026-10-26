#!/usr/bin/env python3
"""Figures for "Controlling Diffusion Models: Guidance, ControlNet, LoRA" (diffusion-models, part 8).

Every measured or computed number drawn here is read from ../lab/captures.json, the capture that the
article's lab download ships, so the prose, the figures and the lab cannot drift apart. Numbers quoted
from papers (Ho & Salimans' Tables 1-2, the adapter sizes) are typed once, below, next to their ledger
keys.

    python3 _figures.py            # all placed/plot/chart figures plus the cover
    python3 _figures.py 3 5        # just those
    python3 _figures.py cover      # just the cover
Figures 2 and 8 are Mermaid (python3 _mermaid.py); figure 14 is the paper's own (source route).
"""

from __future__ import annotations

import json
import math
import os
import pathlib

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUSTARD, MUTED, PAPER, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, emit, emit_cover, eyebrow, mono, rect, text,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP_PATH = pathlib.Path(os.environ.get("P8_CAPTURES", HERE.parent / "lab" / "captures.json"))
PURPLE = "#8a5a9e"
_CAP = None


def cap():
    global _CAP
    if _CAP is None:
        _CAP = json.loads(CAP_PATH.read_text(encoding="utf-8"))
    return _CAP


# ------------------------------------------------------------------ primitives (as in part 7)

class Axes:
    """Data-to-pixel mapping for a real plot. logx/logy put that axis on log10; a reversed
    range (xr[0] > xr[1]) runs the axis right to left."""

    _n = 0

    def __init__(self, x, y, w, h, xr, yr, logx=False, logy=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr, self.logx, self.logy = xr, yr, logx, logy
        Axes._n += 1
        self.clip = f"clip{Axes._n}"

    def X(self, v):
        if self.logx:
            v = math.log10(max(v, 1e-12))
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        if self.logy:
            v = math.log10(max(v, 1e-12))
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def frame(self, xticks=(), yticks=(), xlabel="", ylabel="", grid=True):
        out = (f'<defs><clipPath id="{self.clip}"><rect x="{self.x}" y="{self.y - 2}" '
               f'width="{self.w}" height="{self.h + 4}"/></clipPath></defs>')
        base = self.y + self.h
        out += (f'<line x1="{self.x}" y1="{base}" x2="{self.x + self.w}" y2="{base}" '
                f'stroke="{RULE_SOLID}" stroke-width="1"/>'
                f'<line x1="{self.x}" y1="{base}" x2="{self.x}" y2="{self.y}" '
                f'stroke="{RULE_SOLID}" stroke-width="1"/>')
        for v, lab in xticks:
            px = self.X(v)
            out += (f'<line x1="{px:.1f}" y1="{base}" x2="{px:.1f}" y2="{base + 4}" '
                    f'stroke="{RULE_SOLID}" stroke-width="1"/>')
            out += mono(px, base + 16, lab, 7, SOFT)
        for v, lab in yticks:
            py = self.Y(v)
            if grid:
                out += (f'<line x1="{self.x}" y1="{py:.1f}" x2="{self.x + self.w}" '
                        f'y2="{py:.1f}" stroke="{RULE}" stroke-width="0.8"/>')
            out += mono(self.x - 10, py + 3, lab, 7, SOFT, "end")
        if xlabel:
            out += mono(self.x + self.w / 2, base + 34, xlabel, 8, SOFT)
        if ylabel:
            cx, cy = self.x - 46, self.y + self.h / 2
            out += (f'<g transform="rotate(-90 {cx} {cy})">'
                    + mono(cx, cy, ylabel, 8, SOFT) + '</g>')
        return out

    def path(self, pts, colour=INK, width=1.8, dash=None, opacity=1.0):
        d = {True: ' stroke-dasharray="6,4"', "dot": ' stroke-dasharray="1.5,3.5"'}.get(dash, "")
        s = " ".join(f"{self.X(a):.1f},{self.Y(b):.1f}" for a, b in pts)
        return (f'<g clip-path="url(#{self.clip})"><polyline points="{s}" fill="none" '
                f'stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" '
                f'stroke-linecap="round" opacity="{opacity}"{d}/></g>')

    def dot(self, a, b, r=4, colour=ACCENT, hollow=False):
        """A marker, clipped to the plot like the lines, so an off-scale point never lands on a label."""
        if hollow:
            c = (f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" '
                 f'fill="{PAPER}" stroke="{colour}" stroke-width="1.6"/>')
        else:
            c = f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{colour}"/>'
        return f'<g clip-path="url(#{self.clip})">{c}</g>'

    def hline(self, v, colour=SOFT, dash=True, width=1.0):
        d = ' stroke-dasharray="5,4"' if dash else ""
        return (f'<line x1="{self.x}" y1="{self.Y(v):.1f}" x2="{self.x + self.w}" y2="{self.Y(v):.1f}" '
                f'stroke="{colour}" stroke-width="{width}"{d}/>')

    def vline(self, v, colour=SOFT, dash=True, width=1.0):
        d = ' stroke-dasharray="5,4"' if dash else ""
        return (f'<line x1="{self.X(v):.1f}" y1="{self.y}" x2="{self.X(v):.1f}" y2="{self.y + self.h}" '
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


def path_line(points, colour=MUTED, width=1.2, dashed=False, accent=False, arrow=True):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    marker = ""
    if arrow:
        marker = ' marker-end="url(#arrow-a)"' if accent else (
            ' marker-end="url(#arrow-l)"' if colour == LINK else ' marker-end="url(#arrow)"')
    return (f'<path d="{d}" fill="none" stroke="{colour}" stroke-width="{width}" '
            f'stroke-linejoin="round"{marker}{dash}/>')


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
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()


LO, HI = -1.6, 3.2           # one display range for every 8x8 tile, high value = bright


def tile(x, y, size, flat, side=8, lo=LO, hi=HI, stroke=RULE_SOLID, sw=0.8):
    rows = [[grey(flat[r * side + c], lo, hi) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>'
            + rect(x, y, size, size, "none", stroke, 0, sw))


def legend_row(x, y, items, gap=22):
    """Inline legend: (label, colour, dash) with a short stroke sample each."""
    out = ""
    for label, colour, dash in items:
        d = {True: ' stroke-dasharray="6,4"', "dot": ' stroke-dasharray="1.5,3.5"'}.get(dash, "")
        out += (f'<line x1="{x}" y1="{y - 4}" x2="{x + 22}" y2="{y - 4}" stroke="{colour}" '
                f'stroke-width="2.2"{d}/>')
        out += mono(x + 28, y, label, 8, MUTED, "start")
        x += 40 + len(label) * 6.2 + gap
    return out


def legend_box(x, y, label, stroke, sw=2.2):
    return (f'<rect x="{x}" y="{y - 10}" width="12" height="12" fill="none" stroke="{stroke}" stroke-width="{sw}"/>'
            + mono(x + 20, y, label, 8, MUTED, "start"))


def minus(v):
    return str(v).replace("-", "−")


def pct(v, digits=0):
    return f"{100 * v:.{digits}f}%"


def mean(xs):
    return sum(xs) / len(xs)


# ------------------------------------------------------------------ the world's shapes (for reading tiles)

def _crescent(r=8, inner=(0.64, 0.42, 0.30), ss=8):
    g = [(i + 0.5) / (r * ss) for i in range(r * ss)]
    m = [[0.0] * r for _ in range(r)]
    for yi, yy in enumerate(g):
        for xi, xx in enumerate(g):
            inside = (xx - 0.5) ** 2 + (yy - 0.5) ** 2 < 0.36 ** 2 and not (
                (xx - inner[0]) ** 2 + (yy - inner[1]) ** 2 < inner[2] ** 2)
            m[yi // ss][xi // ss] += inside / (ss * ss)
    flat = [v for row in m for v in row]
    mu = sum(flat) / len(flat)
    flat = [v - mu for v in flat]
    rms = math.sqrt(sum(v * v for v in flat) / len(flat))
    return [v * 0.9 / rms for v in flat]


def _rot90(flat, k, r=8):
    m = [flat[i * r:(i + 1) * r] for i in range(r)]
    for _ in range(k):
        m = [list(row) for row in zip(*m)][::-1]
    return [v for row in m for v in row]


MU = [_rot90(_crescent(), k) for k in range(4)]
NORM = math.sqrt(sum(v * v for v in MU[0]))


def contrast_of(img, k=0):
    """The image's amount of crescent k, as a fraction of a strong crescent (brightness removed)."""
    mu = sum(img) / len(img)
    return sum((a - mu) * b for a, b in zip(img, MU[k])) / NORM ** 2


def over_line():
    return cap()["world"]["over_threshold"]


# ------------------------------------------------------------------ quoted data

HS_T1 = {  # L08: Ho & Salimans, Table 1 - ImageNet 64x64, p_uncond = 0.1: their w -> (FID, IS)
    0.0: (1.8, 53.71), 0.1: (1.55, 66.11), 0.2: (2.04, 78.91), 0.3: (3.03, 92.8), 0.4: (4.3, 106.2),
    0.5: (5.74, 119.3), 0.6: (7.19, 131.1), 0.7: (8.62, 141.8), 0.8: (10.08, 151.6), 0.9: (11.41, 161.0),
    1.0: (12.6, 170.1), 2.0: (21.03, 225.5), 3.0: (24.83, 250.4), 4.0: (26.22, 260.2)}
HS_T2 = {  # L09: Ho & Salimans, Table 2 - ImageNet 128x128, T = 256: their w -> (FID, IS)
    0.0: (7.27, 82.45), 0.1: (4.53, 106.12), 0.2: (3.03, 132.54), 0.3: (2.43, 158.47), 0.4: (2.49, 183.41),
    0.5: (2.98, 207.98), 0.6: (3.76, 228.83), 0.7: (4.67, 249.25), 0.8: (5.74, 267.99), 0.9: (6.8, 283.41),
    1.0: (7.86, 297.98), 2.0: (15.93, 377.37), 3.0: (19.77, 407.44), 4.0: (21.53, 421.03)}
ADAPTERS = {"T2I-Adapter": 77e6, "IP-Adapter": 22e6}   # L40, L41: "about 77M", "about 22M", as quoted


# -------------------------------------------------------------------- fig 01

def fig01():
    """Guided paths in the one-number world: overshoot early, a moved decision late."""
    vw, vh = 960, 580
    W = cap()["worked"]
    P = W["paths"]
    eps = P["eps"]
    cut = 0.5 * (W["modes"][2] + W["modes"][3])
    body = eyebrow(40, 34, "one number: the requested crescent's contrast, in σ's units · 15 starting noises, the same in both panels")
    ends = {w: [row[-1] for row in P[w]["x"]] for w in ("1.0", "3.0")}
    faint1 = [e < cut for e in ends["1.0"]]
    faint3 = [e < cut for e in ends["3.0"]]
    panels = (("1.0", Axes(96, 112, 330, 320, (math.log10(80), math.log10(0.002)), (-9, 24))),
              ("3.0", Axes(560, 112, 330, 320, (math.log10(80), math.log10(0.002)), (-9, 24))))
    xt = [(math.log10(v), lab) for v, lab in ((80, "80"), (10, "10"), (1, "1"), (0.1, "0.1"), (0.01, "0.01"), (0.002, "0.002"))]
    for w, ax in panels:
        body += ax.frame(xt, [(v, minus(f"{v:g}")) for v in (-7.2, -3.6, 0, 3.6, 7.2, 15, 21)],
                         "NOISE LEVEL σ  (LOG, SAMPLING RUNS LEFT TO RIGHT)", "CONTRAST" if w == "1.0" else "")
        for m, lab in ((7.2, "STRONG"), (3.6, "FAINT")):
            body += ax.hline(m, SOFT, True, 0.9)
            body += mono(ax.x + ax.w + 8, ax.Y(m) + 3, lab, 7, SOFT, "start", 500)   # in the margin: paths end on these lines
        sig = P[w]["sigma"]
        for i, row in enumerate(P[w]["x"]):
            pts = [(math.log10(max(s, 0.002)), v) for s, v in zip(sig, row)]
            if w == "1.0":
                col = BLUE if faint1[i] else INK
            else:
                col = BLUE if faint3[i] else (ACCENT if faint1[i] else INK)
            body += ax.path(pts, col, 1.5, opacity=0.9)
    left, right = panels[0][1], panels[1][1]
    n1, n3 = sum(faint1), sum(faint3)
    body += mono(left.x, 76, f"NO GUIDANCE, w = 1 · {n1} OF {len(eps)} END FAINT", 8, INK, "start", 600)
    body += mono(right.x, 76, f"GUIDANCE w = {W['w']:g} · {n3} OF {len(eps)} END FAINT", 8, INK, "start", 600)
    # the worked step's guided target: the dot on the plot, its words above it, clear of every path
    body += f'<circle cx="{right.X(math.log10(80)):.1f}" cy="{right.Y(W["D_guided"]):.1f}" r="4.5" fill="{ACCENT}"/>'
    body += (f'<circle cx="{right.x + 4}" cy="{93}" r="4" fill="{ACCENT}"/>'
             + mono(right.x + 14, 96, f"THE WORKED EXAMPLE'S GUIDED TARGET AT x = 40, σ = 80: {W['D_guided']:.2f}", 7, ACCENT, "start", 500))
    body += legend_row(96, 494, [("ends faint", BLUE, False), ("ends strong", INK, False),
                                 ("ends strong only because of guidance", ACCENT, False)], 14)
    sh = W["weights"]
    body += footnote(vh - 54, f"Faint share over all starting noises: {sh['1.0']['faint_share'] * 100:.1f}% unguided, "
                              f"{sh['2.0']['faint_share'] * 100:.1f}% at w = 2, {sh['3.0']['faint_share'] * 100:.1f}% at w = 3.")
    body += footnote(vh - 38, "Computed by the lab: the one-number world's exact denoisers, 200 DDIM steps per path. "
                              "Starting noises ε from −2.2 to 2.0")
    body += footnote(vh - 22, "put x = 80ε far off the plot at σ = 80, so every path enters from above or below.")
    emit(1, "guidance-moves-the-decision", "Guidance moves the decision",
         "Every guided path first heads for a target past the strongest real crescent; the faint basin shrinks", body,
         "Fifteen paths of the requested crescent's contrast: unguided they split between faint and strong; at w = 3 all but one end strong", vw, vh)


# -------------------------------------------------------------------- fig 03

def fig03():
    """Ten exact-model samples at four guidance weights."""
    vw, vh = 960, 560
    S = cap()["samples"]
    over = over_line()
    rows = ("1.0", "2.0", "3.0", "5.0")
    size, gap, x0, y0 = 62, 12, 150, 104
    body = eyebrow(40, 34, "the exact model · the same ten starting noises in every row · crescent 0 requested")
    body += mono(x0 + 2.5 * (size + gap) - gap / 2, 72, "FIVE NOISES THAT END FAINT WITHOUT GUIDANCE", 8, INK, "middle", 600)
    body += mono(x0 + 7.5 * (size + gap) + 18 - gap / 2, 72, "FIVE THAT END STRONG", 8, INK, "middle", 600)
    for i, w in enumerate(rows):
        y = y0 + i * (size + 36)
        body += text(40, y + size / 2 + 5, f"w = {float(w):g}", 13, INK, SANS, 600, "start")
        for j, img in enumerate(S[w]):
            x = x0 + j * (size + gap) + (18 if j >= 5 else 0)
            c = contrast_of(img)
            stroke, sw = (BLUE, 2.6) if c < 0.75 else ((ACCENT, 2.6) if c > over else (RULE_SOLID, 0.8))
            body += tile(x, y, size, img, stroke=stroke, sw=sw)
            body += mono(x + size / 2, y + size + 14, f"{c:.2f}", 7, BLUE if c < 0.75 else (ACCENT if c > over else SOFT),
                         "middle", 500)
    ly = y0 + 4 * (size + 36) + 8
    body += legend_box(150, ly, "faint (contrast below 0.75)", BLUE)
    if any(contrast_of(img) > over for w in rows for img in S[w]):
        body += legend_box(390, ly, f"over-saturated (above {over:.3f})", ACCENT)
    body += footnote(vh - 38, "Measured: exact denoisers, 128 DDIM steps. Under each tile: its crescent contrast (data: "
                              "faint 0.5, strong 1.0).")
    body += footnote(vh - 22, f"Display range {minus(LO)} to {HI} for every tile, bright = high.")
    emit(3, "guided-samples", "What guidance does to ten samples",
         "Faint crescents turn strong and strong ones brighten past the data", body,
         "Ten 8x8 crescent samples at guidance weights 1, 2, 3 and 5: faint crescents turn strong and the strong ones "
         "brighten past the data", vw, vh)


# -------------------------------------------------------------------- fig 04

def _net(tag_, field, setting):
    seeds = cap()["networks"]["seeds"]
    return mean([seeds[s][tag_][setting][field] for s in seeds])


def fig04():
    """Coverage, blends and over-saturation against w: exact model and two networks."""
    vw, vh = 960, 560
    E = cap()["exact"]
    nets = cap()["networks"]
    body = eyebrow(40, 34, "4,096 samples of crescent 0 per point · networks: mean of two seeds")
    ws_e = [float(w) for w in E["weights"]]
    ws_n = [1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    panels = [("faint", "FAINT SHARE: COVERAGE OF THE LESS TYPICAL LOOK", (0, 0.6), [(v, pct(v)) for v in (0, 0.2, 0.4, 0.6)]),
              ("blend", "BLENDS: CONTRASTS NO REAL CRESCENT HAS", (0, 0.2), [(v, pct(v)) for v in (0, 0.05, 0.1, 0.15, 0.2)]),
              ("over", "OVER-SATURATED: PAST THE STRONGEST LOOK", (0, 0.5), [(v, pct(v)) for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5)])]
    for k, (field, title, yr, yt) in enumerate(panels):
        ax = Axes(86 + k * 300, 96, 236, 300, (0.7, 7.8), yr)
        body += ax.frame([(v, f"{v:g}") for v in (1, 2, 3, 4, 5, 7.5)], yt, "GUIDANCE WEIGHT w", "")
        body += mono(ax.x, 82, title, 7, INK, "start", 600)
        body += ax.path([(w, E["weights"][f"{w}"][field]) for w in ws_e], INK, 2.2)
        for w in ws_e:
            body += ax.dot(w, E["weights"][f"{w}"][field], 2.6, INK)
        for tg, col, dash in (("model", BLUE, None), ("weak", MUSTARD, True)):
            pts = [(w, _net(tg, field, f"cfg w={w:g}")) for w in ws_n]
            body += ax.path(pts, col, 2.2, dash)
            for p in pts:
                body += ax.dot(p[0], p[1], 2.6, col)
        if field == "faint":
            body += ax.hline(E["data"]["faint"], SOFT, True, 0.9)
            body += tag(ax.x + ax.w - 4, ax.Y(E["data"]["faint"]) - 6, "DATA 50%", SOFT, "end", 7)
    st = nets["steps"]
    body += legend_row(86, 470, [("exact model", INK, False), (f"network, {st['model']:,} steps", BLUE, False),
                                 (f"weaker copy, {st['weak']:,} steps", MUSTARD, True)], 16)
    body += footnote(vh - 38, "Measured. Exact model: closed-form denoisers, 128 DDIM steps. Networks: trained on data "
                              "with 10% label dropout, 64 DDIM steps.")
    body += footnote(vh - 22, "The networks were sampled up to w = 5; the exact model also at 7.5.")
    emit(4, "what-guidance-costs", "What guidance costs, measured",
         "Guidance removes blends, deletes faint crescents, and over-saturates in proportion to the network's error", body,
         "Faint share, blends and over-saturated share against guidance weight for the exact model, a trained network and a "
         "weaker network", vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    """Ho & Salimans' tables, re-labelled to this post's convention."""
    vw, vh = 960, 540
    body = eyebrow(40, 34, "quoted · Ho & Salimans, Tables 1–2 · this post's w = their w + 1")
    xt = [(v, f"{v:g}") for v in (1, 1.5, 2, 3, 4, 5)]
    fid = Axes(96, 96, 360, 300, (0.9, 5.15), (math.log10(1.2), math.log10(32)), logy=True)
    isx = Axes(580, 96, 340, 300, (0.9, 5.15), (0, 450))
    body += fid.frame(xt, [(v, f"{v:g}") for v in (1.5, 2, 3, 5, 10, 20, 30)], "GUIDANCE WEIGHT w", "FID  (LOG, LOWER IS BETTER)")
    body += isx.frame(xt, [(v, f"{v:g}") for v in (0, 100, 200, 300, 400)], "GUIDANCE WEIGHT w", "INCEPTION SCORE")
    body += mono(fid.x, 82, "FID: FIDELITY AND VARIETY TOGETHER", 8, INK, "start", 600)
    body += mono(isx.x, 82, "INCEPTION SCORE: CLASS-CONFIDENT FIDELITY", 8, INK, "start", 600)
    for table, col, dash, name in ((HS_T1, BLUE, None, "ImageNet 64"), (HS_T2, ACCENT, True, "ImageNet 128")):
        pf = [(1 + k, v[0]) for k, v in sorted(table.items())]
        pi = [(1 + k, v[1]) for k, v in sorted(table.items())]
        body += fid.path(pf, col, 2.2, dash) + isx.path(pi, col, 2.2, dash)
        for p in pf:
            body += fid.dot(p[0], p[1], 2.4, col)
        for p in pi:
            body += isx.dot(p[0], p[1], 2.4, col)
        best = min(pf, key=lambda p: p[1])
        body += fid.dot(best[0], best[1], 5.5, col, hollow=True)
    b64 = min(((1 + k, v[0]) for k, v in HS_T1.items()), key=lambda p: p[1])
    b128 = min(((1 + k, v[0]) for k, v in HS_T2.items()), key=lambda p: p[1])
    body += legend_row(96, 470, [(f"ImageNet 64×64, p_uncond 0.1 · best FID {b64[1]:g} at w = {b64[0]:g}", BLUE, False)], 18)
    body += legend_row(96, 490, [(f"ImageNet 128×128, 256 steps · best FID {b128[1]:g} at w = {b128[0]:g}", ACCENT, True)], 18)
    body += mono(520, 486, "hollow circles: each curve's lowest FID", 8, SOFT, "start")
    body += footnote(vh - 22, "Quoted from Ho & Salimans (arXiv:2207.12598), Tables 1–2; 50,000 samples per point. "
                              "Scores compare only within this table.")
    emit(5, "published-guidance-curves", "The published trade",
         "A little guidance lowers FID; more raises it while the Inception Score keeps climbing", body,
         "Quoted FID and Inception Score against guidance strength on ImageNet 64 and 128: FID is lowest at a little "
         "guidance, IS keeps rising", vw, vh)


# -------------------------------------------------------------------- fig 06

def fig06():
    """Guidance switched on only above, or only below, a noise level (exact model)."""
    vw, vh = 960, 540
    E = cap()["exact"]
    body = eyebrow(40, 34, "the exact model · guidance at w = 3 when on · 4,096 samples per point")
    ax = Axes(110, 86, 740, 320, (math.log10(0.04), math.log10(50)), (0, 0.6), logx=True)
    xt = [(v, f"{v:g}") for v in (0.05, 0.1, 0.2, 0.5, 1, 2, 3, 5, 10, 20, 40)]   # raw values: the axis takes the log
    body += rect(ax.X(2), ax.y, ax.X(20) - ax.X(2), ax.h, ACCENT_TINT, "none", 0)
    body += ax.frame(xt, [(v, pct(v)) for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)],
                     "THE NOISE LEVEL σ WHERE GUIDANCE SWITCHES  (LOG)", "FAINT SHARE")
    none_, full = E["weights"]["1.0"]["faint"], E["weights"]["3.0"]["faint"]
    body += ax.hline(none_, SOFT, True, 0.9) + ax.hline(full, SOFT, True, 0.9)
    body += tag(ax.x + 8, ax.Y(none_) - 6, f"NO GUIDANCE: {none_ * 100:.1f}%", SOFT, "start", 7)
    body += tag(ax.x + 8, ax.Y(full) + 14, f"GUIDANCE EVERYWHERE: {full * 100:.1f}%", SOFT, "start", 7)
    for key, col, lab in (("above", ACCENT, "GUIDANCE ONLY ABOVE σ"), ("below", BLUE, "GUIDANCE ONLY AT OR BELOW σ")):
        pts = sorted((float(c), v["faint"]) for c, v in E[key].items())
        body += ax.path(pts, col, 2.4)
        for p in pts:
            body += ax.dot(p[0], p[1], 3, col)
    a40 = E["above"]["40.0"]["faint"]
    b40 = E["below"]["40.0"]["faint"]
    body += tag(ax.X(40) + 10, ax.Y(a40) + 4, "ONLY ABOVE σ", ACCENT, "start", 8)
    body += tag(ax.X(40) + 10, ax.Y(b40) + 4, "ONLY AT OR BELOW σ", BLUE, "start", 8)
    body += mono(ax.X(math.sqrt(2 * 20)), ax.y + 14, "WHERE THIS TOY'S DECISION IS DISTORTED", 7, ACCENT, "middle", 500)
    body += footnote(vh - 38, "Measured: closed-form denoisers, 128 DDIM steps. 'Only above σ' runs guidance at every "
                              "step with a noise level above the cut;")
    body += footnote(vh - 22, "'only at or below σ' at every step at or below it. Shaded: σ from 2 to 20.")
    emit(6, "where-guidance-decides", "Where guidance decides",
         "Below σ = 2 guidance changes nothing; above it, it moves the faint/strong decision", body,
         "Faint share with guidance only above, or only below, a noise level: the faint/strong decision happens between "
         "sigma 2 and 20", vw, vh)


# -------------------------------------------------------------------- fig 07

def fig07():
    """Every fix in one plane: blends against faint share, on the trained network."""
    vw, vh = 960, 600
    body = eyebrow(40, 34, "the trained network · crescent 0 · 4,096 samples per point · mean of two seeds")
    ax = Axes(110, 80, 600, 400, (0.0, 0.62), (0.0, 0.1))
    body += ax.frame([(v, pct(v)) for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)], [(v, pct(v)) for v in (0, 0.02, 0.04, 0.06, 0.08, 0.1)],
                     "FAINT SHARE  (COVERAGE; THE DATA HAS 50%)", "BLENDS  (ERRORS; THE DATA HAS 0.1%)")
    ex = cap()["exact"]["data"]
    body += ax.dot(ex["faint"], ex["blend"], 6, SAGE)
    body += tag(ax.X(ex["faint"]) - 10, ax.Y(ex["blend"]) - 10, "THE DATA", SAGE, "end", 8)
    cfg = [(_net("model", "faint", f"cfg w={w:g}"), _net("model", "blend", f"cfg w={w:g}"), w) for w in (1.0, 1.5, 2.0, 3.0, 4.0, 5.0)]
    auto = [cfg[0]] + [(_net("model", "faint", f"auto w={w:g}"), _net("model", "blend", f"auto w={w:g}"), w) for w in (1.5, 2.0, 2.5, 3.0)]
    body += ax.path([(a, b) for a, b, _ in cfg], INK, 2.2)
    body += ax.path([(a, b) for a, b, _ in auto], ACCENT, 2.4)
    for a, b, w in cfg:
        body += ax.dot(a, b, 3.2, INK)
        if w in (2.0, 3.0, 5.0):
            body += mono(ax.X(a) + 9, ax.Y(b) + 15, f"w = {w:g}", 7, INK, "start", 500)   # below the rising line
        if w == 1.5:
            body += mono(ax.X(a) - 4, ax.Y(b) - 10, f"w = {w:g}", 7, INK, "middle", 500)
    for a, b, w in auto[1:]:
        body += ax.dot(a, b, 3.6, ACCENT)
    a2 = auto[2]
    body += tag(ax.X(a2[0]) - 10, ax.Y(a2[1]) + 4, "AUTOGUIDANCE w = 2", ACCENT, "end", 7)
    a4 = auto[4]
    body += tag(ax.X(a4[0]) - 10, ax.Y(a4[1]) + 4, "w = 3", ACCENT, "end", 7)
    body += tag(ax.X(cfg[0][0]) + 8, ax.Y(cfg[0][1]) - 8, "UNGUIDED", INK, "start", 7)
    marks = []
    for lo, hi in ((0.0, 1.0), (0.0, 2.0), (0.5, 3.0), (1.0, 5.0), (2.0, 80.0)):
        k = f"interval w=3 ({lo:g},{hi:g}]"
        marks.append(("interval", _net("model", "faint", k), _net("model", "blend", k), f"({lo:g}, {hi:g}]"))
    for w in (3.0, 5.0):
        marks.append(("rescale", _net("model", "faint", f"rescale w={w:g}"), _net("model", "blend", f"rescale w={w:g}"), f"w = {w:g}"))
        marks.append(("apg", _net("model", "faint", f"apg w={w:g}"), _net("model", "blend", f"apg w={w:g}"), f"w = {w:g}"))
    colours = {"interval": BLUE, "rescale": MUSTARD, "apg": PURPLE}
    for n, (kind, a, b, lab) in enumerate(marks, 1):
        body += (f'<circle cx="{ax.X(a):.1f}" cy="{ax.Y(b):.1f}" r="7.5" fill="{PAPER}" stroke="{colours[kind]}" stroke-width="1.6"/>'
                 + text(ax.X(a), ax.Y(b) + 3, str(n), 8, colours[kind], MONO, 600))
    # the side legend names each numbered marker and its values, so no label sits on the cluster
    lx, ly = 740, 104
    body += mono(lx, ly - 18, "NUMBERED MARKERS, w = 3 UNLESS NOTED", 7, INK, "start", 600)
    for n, (kind, a, b, lab) in enumerate(marks, 1):
        name = {"interval": "interval σ", "rescale": "CFG-rescale", "apg": "APG"}[kind]
        body += (f'<circle cx="{lx + 6}" cy="{ly - 3}" r="7" fill="{PAPER}" stroke="{colours[kind]}" stroke-width="1.6"/>'
                 + text(lx + 6, ly, str(n), 8, colours[kind], MONO, 600)
                 + mono(lx + 20, ly, f"{name} {lab}", 7, MUTED, "start")
                 + mono(lx + 200, ly, f"{a * 100:.0f}% / {b * 100:.1f}%", 7, SOFT, "end"))
        ly += 19
    body += mono(lx, ly + 6, "FAINT / BLENDS", 7, SOFT, "start")
    body += legend_row(110, 540, [("classifier-free guidance", INK, False), ("autoguidance (5,000-step copy)", ACCENT, False)], 16)
    body += footnote(vh - 22, "Measured: 64 DDIM steps. Lower right is better: few blends, half faint.")
    emit(7, "fixes-compared", "Every fix in one plane",
         "Guidance trades coverage for fewer errors; only autoguidance reduces errors and keeps coverage", body,
         "Blends against faint share for CFG, autoguidance, guidance intervals, CFG-rescale and APG on the trained network",
         vw, vh)


# -------------------------------------------------------------------- fig 09

CN_STEPS = ("0", "25", "50", "100", "200", "400", "800", "1600", "3200")


def fig09():
    """Zero-initialised against Gaussian connectors, over ControlNet training."""
    vw, vh = 960, 560
    C = cap()["controlnet"]
    body = eyebrow(40, 34, "a ControlNet branch on the trained network · control: a 4×4 layout of the target image · two seeds each")
    xs = list(range(len(CN_STEPS)))
    left = Axes(96, 92, 360, 300, (-0.4, len(xs) - 0.6), (0, 0.6))
    right = Axes(570, 92, 350, 300, (-0.4, len(xs) - 0.6), (0, 0.28))
    xt = [(i, s) for i, s in zip(xs, CN_STEPS)]
    body += left.frame(xt, [(v, f"{v:g}") for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6)], "TRAINING STEP", "CONTROL ERROR (RMS)")
    body += right.frame(xt, [(v, f"{v:g}") for v in (0, 0.05, 0.1, 0.15, 0.2, 0.25)], "TRAINING STEP", "SAMPLE DISTANCE")
    body += mono(left.x, 78, "DOES THE IMAGE FOLLOW THE LAYOUT?", 8, INK, "start", 600)
    body += mono(right.x, 78, "DOES THE IMAGE STILL LOOK REAL?", 8, INK, "start", 600)
    base = C["zero"]["1"]["0"]["control_error"]
    body += left.hline(base, SOFT, True, 0.9)
    body += mono(left.x + left.w - 4, left.Y(base) + 14, f"FROZEN MODEL, NO LAYOUT: {base:.2f}", 7, SOFT, "end", 500)
    for key, col, dash in (("zero", ACCENT, None), ("gaussian", MUTED, True)):
        for field, ax in (("control_error", left), ("swd", right)):
            per_seed = [[C[key][s][st][field] for st in CN_STEPS] for s in C[key]]
            for ser in per_seed:
                body += ax.path(list(zip(xs, ser)), col, 1.0, dash, 0.45)
            m = [mean(v) for v in zip(*per_seed)]
            body += ax.path(list(zip(xs, m)), col, 2.4, dash)
            for x_, v in zip(xs, m):
                body += ax.dot(x_, v, 3, col)
    z0 = mean([C["zero"][s]["0"]["swd"] for s in C["zero"]])
    g0 = mean([C["gaussian"][s]["0"]["swd"] for s in C["gaussian"]])
    body += mono(right.X(0) + 22, right.Y(g0) + 4, f"STEP 0, GAUSSIAN: {g0:.2f}", 7, MUTED, "start", 500)
    body += mono(right.X(0) - 4, right.Y(0.022), f"STEP 0, ZERO: {z0:.3f} (THE FROZEN MODEL'S)", 7, ACCENT, "start", 500)
    body += legend_row(96, 470, [("zero-initialised connectors (ControlNet)", ACCENT, False),
                                 ("Gaussian-initialised connectors", MUTED, True)], 16)
    body += footnote(vh - 38, f"Measured: 1,024 layouts from real images per point, 64 DDIM steps; bold lines are the mean "
                              f"of two seeds. At step 0 the zero branch")
    body += footnote(vh - 22, f"changed no output (largest change {C['zero']['1']['0']['max_change']:g}); the Gaussian one by up "
                              f"to {max(C['gaussian'][s]['0']['max_change'] for s in C['gaussian']):.1f}. Learning rate 2e-4.")
    emit(9, "zero-init-vs-gaussian", "Why the connectors start at zero",
         "A zero branch starts as the frozen model and learns the layout abruptly; a Gaussian one starts damaged", body,
         'ControlNet training: zero-initialised connectors start as the frozen model and learn the layout; Gaussian ones start damaged', vw, vh)


# -------------------------------------------------------------------- fig 10

def fig10():
    """Trainable parameters per method on SD 1.5, log scale."""
    vw, vh = 960, 520
    N = cap()["census"]
    rows = [("full fine-tune of the U-Net", N["unet"], False),
            ("ControlNet", N["controlnet"], False),
            ("T2I-Adapter (as quoted)", ADAPTERS["T2I-Adapter"], True),
            ("IP-Adapter (as quoted)", ADAPTERS["IP-Adapter"], True),
            ("Custom Diffusion: cross-attention K, V", N["cross_attention_kv"], False),
            ("LoRA, rank 64, attention", N["lora"]["64"], False),
            ("LoRA, rank 4, attention", N["lora"]["4"], False),
            ("textual inversion: one token", N["token_embedding"], False)]
    body = eyebrow(40, 34, "stable diffusion 1.5 · what each method trains · log scale")
    ax = Axes(330, 70, 520, 340, (2, 9.3), (0, len(rows)))
    for v in range(2, 10):
        px = ax.X(v)
        body += f'<line x1="{px:.1f}" y1="{ax.y}" x2="{px:.1f}" y2="{ax.y + ax.h}" stroke="{RULE}" stroke-width="0.8"/>'
        body += mono(px, ax.y + ax.h + 16, f"10{chr(0x2070 + v) if v not in (2, 3) else ('²' if v == 2 else '³')}", 8, SOFT)
    body += mono(ax.x + ax.w / 2, ax.y + ax.h + 36, "TRAINABLE PARAMETERS  (LOG)", 8, SOFT)
    bh = 26
    for i, (name, n, quoted) in enumerate(rows):
        y = ax.y + i * (ax.h / len(rows)) + (ax.h / len(rows) - bh) / 2
        w = ax.X(math.log10(n)) - ax.x
        col = ACCENT if i == 1 else (SOFT if quoted else BLUE)
        fill = ACCENT_TINT if i == 1 else ("none" if quoted else "rgba(94,122,155,0.18)")
        body += rect(ax.x, y, w, bh, fill, col, 2, 1.2, "4,3" if quoted else None)
        body += text(ax.x - 12, y + bh / 2 + 4, name, 11, INK, SANS, 500, "end")
        label = f"{n:,.0f}" if not quoted else f"about {n / 1e6:.0f} million"
        frac = 100 * n / N["unet"]
        if frac >= 0.1:
            pct_s = f"{frac:.1f}"
        else:                                   # two significant figures, written out: 0.093, 0.000089
            pct_s = f"{frac:.{max(2, 1 - math.floor(math.log10(frac)))}f}"
        share = f"  ·  {pct_s}% of the U-Net" if 0 < n < N["unet"] and not quoted else ""
        s = label + share
        if ax.x + w + 8 + len(s) * 5.1 > vw - 16:          # it would leave the canvas: write it inside the bar
            body += mono(ax.x + w - 10, y + bh / 2 + 3, s, 8, INK, "end", 500)
        else:
            body += mono(ax.x + w + 8, y + bh / 2 + 3, s, 8, MUTED, "start")
    body += footnote(vh - 38, "Computed by the lab's census stage from SD 1.5's published U-Net config, on PyTorch's meta "
                              "device (diffusers 0.40.0);")
    body += footnote(vh - 22, "LoRA counts cover all 128 attention projections. T2I-Adapter and IP-Adapter are as quoted "
                              "in their papers (dashed).")
    emit(10, "what-each-method-trains", "What each method trains",
         "Six orders of magnitude separate a full fine-tune from a new word", body,
         "Trainable parameters per control method on SD 1.5, log scale, from 859.5 million for the full U-Net down to 768 "
         "for textual inversion", vw, vh)


# -------------------------------------------------------------------- fig 11

PMETHODS = (("ti", "textual inversion"), ("lora", "LoRA"), ("lora+ppl", "LoRA + prior"),
            ("full", "full fine-tune"), ("full+ppl", "full + prior"))


def fig11():
    """Personalisation: what each recipe learned and what it cost, after the last checkpoint."""
    vw, vh = 960, 640
    P = cap()["personal"]
    last = str(P["steps"])
    M = P["methods"]
    seeds = list(M["ti"])
    body = eyebrow(40, 34, f"teaching the trained network a thinner crescent 0 from five photos · after {int(last):,} steps · two seeds")
    panels = [("subject_share", "DRAWS THE SUBJECT  ([V] crescent 0)", (0, 1.0), [(v, pct(v)) for v in (0, 0.25, 0.5, 0.75, 1.0)], None),
              ("drift", "DRIFT: PLAIN 'CRESCENT 0' SHOWS THE SUBJECT", (0, 1.0), [(v, pct(v)) for v in (0, 0.25, 0.5, 0.75, 1.0)], None),
              ("others_swd", "FORGETTING: OTHER CLASSES' SAMPLE DISTANCE (DASHED: BEFORE FINE-TUNING)", (0, 0.4), [(v, f"{v:g}") for v in (0, 0.1, 0.2, 0.3, 0.4)], "base"),
              ("subject_brightness_sd", "THE SUBJECT'S BRIGHTNESS SPREAD", (0, 0.35), [(v, f"{v:g}") for v in (0, 0.1, 0.2, 0.3)], "truth")]
    for k, (field, title, yr, yt, ref) in enumerate(panels):
        col_x = 86 + (k % 2) * 450
        row_y = 92 + (k // 2) * 250
        ax = Axes(col_x, row_y, 360, 170, (-0.6, len(PMETHODS) - 0.4), yr)
        body += ax.frame([], yt)
        body += mono(ax.x, row_y - 14, title, 7, INK, "start", 600)
        for i, (key, name) in enumerate(PMETHODS):
            if field == "subject_brightness_sd" and key == "ti":       # it drew no subject to measure
                body += mono(ax.X(i), ax.Y(0.05), "NO SUBJECT", 7, SOFT, "middle", 500)
                body += mono(ax.X(i), ax.y + ax.h + 14, name, 7, MUTED, "middle")
                continue
            vals = [M[key][s][last][field] for s in seeds]
            assert all(yr[0] <= v <= yr[1] for v in vals), (field, key, vals)   # never clip a seed off the panel
            m = mean(vals)
            x0 = ax.X(i) - 22
            body += rect(x0, ax.Y(m), 44, max(ax.Y(0) - ax.Y(m), 0.8), "rgba(94,122,155,0.18)", BLUE, 2, 1)
            for j, v in enumerate(vals):
                body += ax.dot(i + (j - 0.5) * 0.28, v, 3.4, INK)
            body += mono(ax.X(i), ax.y + ax.h + 14, name, 7, MUTED, "middle")
        if ref == "base":
            b = mean([P["base"][s]["others_swd"] for s in P["base"]])
            body += ax.hline(b, SOFT, True, 0.9)
            body += mono(ax.x + ax.w + 6, ax.Y(b) + 3, f"{b:.2f}", 7, SOFT, "start", 500)
        if ref == "truth":
            body += ax.hline(0.3, SAGE, True, 1.0)
            body += tag(ax.x + 6, ax.Y(0.3) - 6, "A REAL SUBJECT: 0.30", SAGE, "start", 7)
            for j, s in enumerate(seeds):
                v = M["full"][s]["photos_brightness_sd"]
                body += ax.hline(v, ACCENT, "dot", 1.2)
            spreads = " AND ".join(f"{M['full'][s]['photos_brightness_sd']:.3f}" for s in seeds)
            body += tag(ax.x + ax.w - 6, ax.Y(0.3) + 16, f"THE FIVE PHOTOS: {spreads}", ACCENT, "end", 7)
    body += (f'<rect x="86" y="{vh - 76}" width="22" height="10" fill="rgba(94,122,155,0.18)" stroke="{BLUE}"/>'
             + mono(116, vh - 67, "mean of two seeds", 8, MUTED, "start")
             + f'<circle cx="262" cy="{vh - 71}" r="3.4" fill="{INK}"/>' + mono(272, vh - 67, "each seed", 8, MUTED, "start"))
    body += footnote(vh - 38, "Measured: five photos per seed, 1,024 samples per prompt, 64 DDIM steps. Prior "
                              "preservation mixes in 1,000 of the model's own crescent 0s.")
    body += footnote(vh - 22, "Distances are sliced Wasserstein; dashed orange: each seed's five photos' own brightness spread.")
    emit(11, "personalisation-costs", "What personalisation learned, and what it cost",
         "Fine-tuning learns the subject and the five photos; prior preservation protects only the class it names", body,
         "Subject share, drift of the plain class, other classes' sample distance and the subject's brightness spread for "
         "each personalisation method", vw, vh)


# -------------------------------------------------------------------- fig 12

INPAINT_ROWS = (("replacement", "replacement"), ("resample 10", "resampling ×10"),
                ("inpainting network", "network with mask inputs"), ("exact posterior", "exact posterior"))


def fig12():
    """Inpainting completions and their coherence."""
    vw, vh = 960, 620
    I = cap()["inpaint"]
    ex = I["examples"]
    body = eyebrow(40, 34, "the left half of each image is known; the right half is generated · 2,048 images per method")
    size, gap, x0, y0 = 70, 14, 230, 96
    body += mono(x0 + 2 * (size + gap) - gap / 2, 78, "FOUR OF THE SOURCE IMAGES AND THEIR COMPLETIONS", 8, INK, "middle", 600)
    rows = [("source", "the source image")] + list(INPAINT_ROWS)
    post = ex["exact posterior"]
    for i, (key, name) in enumerate(rows):
        y = y0 + i * (size + 22)
        body += text(40, y + size / 2 + 5, name, 12, INK, SANS, 500, "start")
        imgs = ex[key]
        for j in range(4):
            x = x0 + j * (size + gap)
            img = imgs[j]
            wrong = False
            if key not in ("source", "exact posterior"):
                d = [a - b for a, b, c in zip(img, post[j], range(64)) if c % 8 >= 4]
                wrong = math.sqrt(sum(v * v for v in d) / len(d)) > 0.3
            body += tile(x, y, size, img, stroke=ACCENT if wrong else RULE_SOLID, sw=2.6 if wrong else 0.8)
            body += (f'<line x1="{x + size / 2:.1f}" y1="{y - 3}" x2="{x + size / 2:.1f}" y2="{y + size + 3}" '
                     f'stroke="{LINK}" stroke-width="1" stroke-dasharray="2,2"/>')
    # coherence column
    cx, cw = 600, 250
    body += mono(cx, 78, "COHERENT COMPLETIONS · DENOISER CALLS", 8, INK, "start", 600)
    stats = []
    for key, name in (("replacement", "replacement"), ("resample 2", "resampling ×2"), ("resample 5", "resampling ×5"),
                      ("resample 10", "resampling ×10")):
        v = I["methods"][key]
        stats.append((name, v["coherent"], v["coherent"], f"{v['calls']} calls"))
    net = I["methods"]["inpainting network"]
    vals = [net[s]["coherent"] for s in net]
    stats.append(("network with mask inputs", min(vals), max(vals), f"{I['steps']} calls · two seeds"))
    stats.append(("exact posterior", I["methods"]["exact posterior"]["coherent"], I["methods"]["exact posterior"]["coherent"], "closed form"))
    for i, (name, lo, hi, calls) in enumerate(stats):
        y = 112 + i * 54
        body += text(cx, y, name, 11, INK, SANS, 500, "start")
        body += rect(cx, y + 8, cw, 12, "none", RULE_SOLID, 2, 0.8)
        col = ACCENT if name == "replacement" else BLUE
        body += rect(cx, y + 8, cw * hi, 12, "rgba(94,122,155,0.25)" if col == BLUE else ACCENT_TINT, col, 2, 1)
        lab = f"{lo * 100:.1f}%" if lo == hi else f"{lo * 100:.1f}–{hi * 100:.1f}%"
        body += mono(cx + cw + 10, y + 18, lab, 8, INK, "start", 600)
        body += mono(cx + cw + 10, y + 32, calls, 7, SOFT, "start")
    body += legend_box(x0, y0 + 5 * (size + 22) - 4, "outlined: a different crescent or contrast from the exact posterior's", ACCENT)
    body += footnote(vh - 38, "Measured: exact denoisers for replacement and resampling, 64 DDIM steps; coherent = the "
                              "generated half within 0.3 RMS of the posterior mean.")
    body += footnote(vh - 22, "The network: the trained model fine-tuned 4,000 steps with zero-initialised mask and "
                              "masked-image inputs. Dashed: the mask's edge.")
    emit(12, "inpainting-coherence", "Filling in the right half",
         "Replacement picks the hidden half's crescent before the known half can speak", body,
         'Right-half completions of four crescents by replacement, resampling, a network with mask inputs and the exact posterior, with coherence', vw, vh)


# -------------------------------------------------------------------- fig 13

def fig13():
    """SDEdit's one dial against DDIM inversion."""
    vw, vh = 960, 560
    E = cap()["edit"]
    tau = cap()["world"]["detail"]
    sd = E["sdedit"]
    inv = E["inversion"]
    s0s = sorted(float(k) for k in sd)
    body = eyebrow(40, 34, "1,024 images of crescent 0 edited into crescent 1 · exact denoisers")
    left = Axes(96, 92, 400, 320, (math.log10(0.07), math.log10(250)), (-0.04, 1.08), logx=True)
    right = Axes(600, 92, 320, 320, (math.log10(0.07), math.log10(250)), (-0.015, 0.35), logx=True)
    xt = [(v, f"{v:g}") for v in (0.1, 0.25, 0.5, 1, 2, 4, 8, 16, 80)]   # raw values: the axis takes the log
    body += left.frame(xt, [(v, f"{v:g}") for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)], "SDEDIT'S STARTING NOISE σ₀  (LOG)", "")
    body += right.frame(xt, [(v, f"{v:g}") for v in (0, 0.1, 0.2, 0.3)], "SDEDIT'S STARTING NOISE σ₀  (LOG)", "")
    body += mono(left.x, 78, "OLD CRESCENT LEFT (GHOST) AND DETAIL KEPT", 8, INK, "start", 600)
    body += mono(right.x, 78, "BRIGHTNESS ERROR (MEAN ABSOLUTE)", 8, INK, "start", 600)
    curve = [(s, tau / math.sqrt(tau * tau + s * s)) for s in [0.07 * 1.05 ** i for i in range(170)] if s <= 90]
    body += left.path(curve, SOFT, 1.4, True)
    body += tag(left.X(0.5) + 8, left.Y(0.36), f"τ/√(τ² + σ₀²), τ = {tau:g}", SOFT, "start", 7)
    g = [(s, sd[str(s)]["ghost"]) for s in s0s]
    d = [(s, sd[str(s)]["detail_corr"]) for s in s0s]
    b = [(s, sd[str(s)]["brightness_error"]) for s in s0s]
    body += left.path(g, ACCENT, 2.2) + left.path(d, BLUE, 2.2)
    for p in g:
        body += left.dot(p[0], p[1], 3, ACCENT)
    for p in d:
        body += left.dot(p[0], p[1], 3, BLUE)
    body += right.path(b, MUTED, 2.2)
    for p in b:
        body += right.dot(p[0], p[1], 3, MUTED)
    # DDIM inversion: one point, off the SDEdit axis
    ix = 180
    for ax in (left, right):
        body += ax.vline(110, RULE_SOLID, True, 0.8)
        body += mono(ax.X(ix), ax.y + ax.h + 16, "INVERSION", 7, ACCENT, "middle", 600)
    for ax, v, col in ((left, inv["ghost"], ACCENT), (left, inv["detail_corr"], BLUE), (right, inv["brightness_error"], MUTED)):
        body += f'<circle cx="{ax.X(ix):.1f}" cy="{ax.Y(v):.1f}" r="5" fill="{col}"/>'   # unclipped: it sits on an edge
    body += tag(left.X(ix) - 8, left.Y(inv["detail_corr"]) + 18, f"{inv['detail_corr']:.2f}", BLUE, "end", 7)
    body += tag(left.X(ix) - 8, left.Y(inv["ghost"]) - 8, f"{inv['ghost']:.3f}", ACCENT, "end", 7)
    body += tag(right.X(ix) - 8, right.Y(inv["brightness_error"]) - 8, f"{inv['brightness_error']:.3f}", MUTED, "end", 7)
    body += legend_row(96, 476, [("ghost: old crescent left", ACCENT, False), ("detail kept (correlation)", BLUE, False),
                                 ("closed form", SOFT, True), ("brightness error", MUTED, False)], 14)
    body += footnote(vh - 38, "Measured: SDEdit noises each image to σ₀ and denoises it as crescent 1 (256-step DDIM grid); "
                              "inversion runs crescent 0's path back")
    body += footnote(vh - 22, "to σ = 80 and crescent 1's forward, 512 steps each. Ghost: median share of the old "
                              "crescent left. Brightness of an unrelated image: 0.32.")
    emit(13, "sdedit-vs-inversion", "One dial against an inverse",
         "SDEdit keeps the detail only by keeping the old crescent; inversion keeps the detail and drops the crescent", body,
         "SDEdit's ghost of the old crescent and its kept detail fall together with starting noise; DDIM inversion keeps the detail, no ghost", vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    W = cap()["worked"]
    P = W["paths"]
    body = eyebrow(72, 73, "diffusion · part eight")
    body += text(72, 148, "Controlling diffusion models", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "guidance, ControlNet and LoRA — and what each one costs", 15, MUTED, MONO, 400, "start")
    ax = Axes(96, 238, 470, 210, (math.log10(80), math.log10(0.002)), (-6, 22))
    body += ax.frame()
    body += ax.hline(7.2, SOFT, True, 0.9) + ax.hline(3.6, SOFT, True, 0.9)
    cut = 0.5 * (W["modes"][2] + W["modes"][3])
    ends1 = [row[-1] < cut for row in P["1.0"]["x"]]
    for i, row in enumerate(P["3.0"]["x"]):
        col = BLUE if row[-1] < cut else (ACCENT if ends1[i] else INK)
        body += ax.path([(math.log10(max(s, 0.002)), v) for s, v in zip(P["3.0"]["sigma"], row)], col, 2.2, opacity=0.9)
    body += mono(ax.x, ax.y + ax.h + 24, "GUIDED PATHS: PAST THE STRONGEST CRESCENT, THEN A MOVED DECISION", 9, MUTED, "start", 500)
    S = cap()["samples"]
    size, gap, x0, y0 = 100, 18, 652, 268
    for i, w in enumerate(("1.0", "2.0", "3.0", "5.0")):
        img = S[w][0]                      # one starting noise that ends faint without guidance
        c = contrast_of(img)
        x = x0 + i * (size + gap)
        body += tile(x, y0, size, img, stroke=BLUE if c < 0.75 else RULE_SOLID, sw=2.6 if c < 0.75 else 0.8)
        body += mono(x + size / 2, y0 + size + 18, f"w = {float(w):g}", 9, MUTED, "middle", 500)
        body += mono(x + size / 2, y0 + size + 34, f"contrast {c:.2f}", 8, BLUE if c < 0.75 else SOFT, "middle")
    body += mono(x0, y0 - 18, "ONE NOISE, FOUR GUIDANCE WEIGHTS: FAINT TURNS STRONG", 9, MUTED, "start", 500)
    body += f'<line x1="72" y1="508" x2="1128" y2="508" stroke="{RULE}" stroke-width="1"/>'
    body += text(72, 548, "Every control adds one term; where you compute it decides what you lose.", 20, MUTED, SERIF, 400, "start", italic=True)
    emit_cover(body, 'Guided paths overshooting the strongest crescent beside one crescent sample that turns from faint to strong as the guidance weight grows')


# keyed by the figure number that reaches the post; 2 and 8 are Mermaid, 14 is the paper's own
FIGURES = {1: fig01, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07, 9: fig09, 10: fig10, 11: fig11, 12: fig12, 13: fig13}

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if not args:
        for f in FIGURES.values():
            f()
        cover()
    for a in args:
        cover() if a == "cover" else FIGURES[int(a)]()
