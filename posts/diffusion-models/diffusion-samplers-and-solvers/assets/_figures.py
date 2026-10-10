#!/usr/bin/env python3
"""Figures for "Diffusion Samplers and Solvers: 1,000 Steps Into 20" (diffusion-models, part 6).

Every measured or computed number drawn here is read from ../lab/captures.json, the capture that
the article's lab download ships, so the prose, the figures and the lab cannot drift apart.
Numbers quoted from papers (DPM-Solver's Tables 1 and 4, DDIM's Table 1, Restart's Tables 4 and 5,
Align Your Steps' Table 5) are typed once, below, next to their ledger keys.

    python3 _figures.py            # all placed/plot/chart figures plus the cover
    python3 _figures.py 6 9        # just those
    python3 _figures.py cover      # just the cover
Figure 4 is Mermaid (python3 _mermaid.py).
"""

from __future__ import annotations

import json
import math
import os
import pathlib

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUSTARD, MUTED, PAPER, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, ascii_upper, emit, emit_cover, eyebrow, mono, rect, text,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads(pathlib.Path(os.environ.get("P6_CAPTURES", HERE.parent / "lab" / "captures.json"))
                 .read_text(encoding="utf-8"))
PURPLE = "#8a5a9e"


# ------------------------------------------------------------------ primitives

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


def plate(x, y, w, h=16):
    return rect(x, y, w, h, PAPER, "none", 3)


def tag(x, y, value, fill=INK, anchor="middle", size=9, weight=500, bg=True, w=None):
    """A label on an opaque plate so a line passing behind it cannot cut it."""
    w = w or len(value) * size * 0.62 + 10
    left = x - w / 2 if anchor == "middle" else (x - 5 if anchor == "start" else x - w + 5)
    out = plate(left, y - size - 2, w, size + 7) if bg else ""
    return out + text(x, y, value, size, fill, MONO, weight, anchor)


def footnote(y, value, x=40, vw=960):
    """A source line under a figure. Geist Mono at 8px with 0.06em tracking measures about 5.95px a
    glyph in the render; a line that would leave the canvas is a defect, so refuse it."""
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


def tile(x, y, size, flat, side=32, lo=-1.6, hi=1.6):
    rows = [[grey(flat[r * side + c], lo, hi) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>'
            + rect(x, y, size, size, "none", RULE_SOLID, 0, 0.8))


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


def minus(v):
    return str(v).replace("-", "−")


def sci(v, digits=0):
    """1.2e-05 -> 1.2×10⁻⁵ for plot labels."""
    sup = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")
    m, e = f"{v:.{digits}e}".split("e")
    e = int(e)
    return (f"{m}×10" if m not in ("1", "1.0") else "10") + str(e).translate(sup)


def pow10_ticks(lo, hi, every=1):
    """Ticks at 10^lo .. 10^hi as raw values, for an axis built with logy=True or logx=True."""
    return [(10.0 ** e, "1" if e == 0 else ("10" if e == 1 else sci(10.0 ** e))) for e in range(lo, hi + 1, every)]


# ------------------------------------------------------------------ data

W = CAP["worked"]
ODE = CAP["ode"]
LOCAL = CAP["local"]
SDE = CAP["sde"]
SAMPLES = CAP["samples"]
GREY = ODE["grey"]

STYLE = {  # sampler -> (label, colour, dash)
    "ddim": ("DDIM / Euler", INK, False),
    "heun": ("Heun (EDM)", BLUE, False),
    "dpm2": ("DPM-Solver-2", SAGE, False),
    "dpm3": ("DPM-Solver-3", MUSTARD, False),
    "dpmpp2m": ("DPM-Solver++(2M)", ACCENT, False),
    "euler_vp": ("Euler in VP time", SOFT, True),
    "ancestral": ("ancestral, η = 1", LINK, True),
    "edm_sde": ("EDM stochastic", PURPLE, True),
}
SCHED_LABEL = {"vp_time": "time-uniform", "logsnr": "log-SNR", "edm3": "EDM ρ = 3", "edm7": "EDM ρ = 7",
               "uniform": "uniform in σ"}

# Quoted from papers, with their ledger keys.
DPMS_T1 = {  # L16: Lu et al. 2022, Table 1 — FID, CIFAR-10, continuous VP model, uniform λ steps
    "nfe": [12, 18, 24, 30, 36, 42, 48],
    "RK2 in t": [16.40, 7.25, 3.90, 3.63, 3.58, 3.59, 3.54],
    "RK2 in λ": [107.81, 42.04, 17.71, 7.65, 4.62, 3.58, 3.17],
    "DPM-Solver-2": [5.28, 3.43, 3.02, 2.85, 2.78, 2.72, 2.69],
    "RK3 in t": [48.75, 21.86, 10.90, 6.96, 5.22, 4.56, 4.12],
    "RK3 in λ": [34.29, 4.90, 3.50, 3.03, 2.85, 2.74, 2.69],
    "DPM-Solver-3": [6.03, 2.90, 2.75, 2.70, 2.67, 2.65, 2.65],
}
DPMS_T4 = {  # L18: Lu et al. 2022, Table 4 — FID, CIFAR-10, DDPM's discrete-time model
    "nfe": [10, 12, 15, 20, 50, 200, 1000],
    "DDPM ancestral": [278.67, 246.29, 197.63, 137.34, 32.63, 4.03, 3.16],
    "Analytic-DDPM": [35.03, 27.69, 20.82, 15.35, 7.34, 4.11, 3.84],
    "DDIM": [13.58, 11.02, 8.92, 6.94, 4.73, 4.07, 3.95],
    "Analytic-DDIM": [14.74, 11.68, 9.16, 7.20, 4.28, 3.60, 3.86],
}
DPMS_T4_SOLVER = [(10, 6.37), (12, 4.65), (15, 3.78), (20, 3.80), (46, 3.57)]  # L18: ε = 10⁻³ up to 15 NFE, 10⁻⁴ above
DDIM_T1 = {  # L06: Song et al. 2021, Table 1 — FID, CIFAR-10, one model trained with T = 1000
    "steps": [10, 20, 50, 100, 1000],
    "η = 0 (DDIM)": [13.36, 6.84, 4.67, 4.16, 4.04],
    "η = 0.5": [16.66, 8.35, 5.25, 4.46, 4.29],
    "η = 1 (DDPM)": [41.07, 18.36, 8.01, 5.78, 4.73],
    "DDPM, larger noise": [367.43, 133.37, 32.72, 9.99, 3.17],
}
RESTART_T4 = {  # L36: Xu et al. 2023, Tables 4 and 5 — FID (50k), class-conditional ImageNet-64, EDM's model
    "ODE (Heun)": [(35, 2.46), (63, 2.30), (127, 2.25), (255, 2.24), (511, 2.24), (1023, 2.24)],
    "EDM stochastic": [(35, 2.97), (63, 2.24), (127, 1.75), (255, 1.50), (511, 1.45), (1023, 1.40)],
    "Euler–Maruyama SDE": [(128, 59.71), (256, 11.91), (512, 3.38), (1024, 1.89)],
    "Restart": [(39, 2.38), (67, 1.95), (99, 1.71), (165, 1.51), (203, 1.46), (385, 1.41), (535, 1.39), (623, 1.36)],
}
AYS_T5 = {  # L38: Sabour et al. 2024, Table 5 — FID, CIFAR-10, EDM's model
    "nfe": [10, 20, 30, 50],
    "DDIM, log-SNR steps": [16.44, 6.01, 3.97, 2.82],
    "DDIM, AYS steps": [10.73, 4.67, 3.30, 2.56],
    "DPM-Solver++(2M), log-SNR": [5.07, 2.37, 2.12, 2.04],
    "DPM-Solver++(2M), AYS": [2.98, 2.10, 2.02, 2.01],
}


# -------------------------------------------------------------------- fig 01

def fig01():
    vw, vh = 960, 500
    v0 = W["v0"]
    sv = math.sqrt(v0)
    body = eyebrow(40, 36, "one gaussian direction · each sampler's value over the exact ode's, after every step")
    ax = Axes(96, 76, 780, 300, (math.log10(400), math.log10(0.02)), (0.80, 1.025), logx=True)
    lo, hi = sv / 3, sv * 3
    body += rect(ax.X(hi), ax.y, ax.X(lo) - ax.X(hi), ax.h, ACCENT_TINT, "none", 0)
    body += mono((ax.X(hi) + ax.X(lo)) / 2, ax.y + ax.h - 12, f"σ WITHIN 3× OF √V₀ = {sv:.1f}", 8, ACCENT, "middle", 500)
    xt = [(v, lab) for v, lab in ((300, "300"), (100, "100"), (30, "30"), (10, "10"), (3, "3"),
                                    (1, "1"), (0.3, "0.3"), (0.1, "0.1"), (0.03, "0.03"))]
    body += ax.frame(xt, [(v, f"{v:.2f}") for v in (0.80, 0.85, 0.90, 0.95, 1.00)],
                     "NOISE LEVEL σ  (LOG, SAMPLING RUNS LEFT TO RIGHT)", "VALUE ÷ EXACT")
    body += ax.hline(1.0, SOFT, True)
    P = W["paths"]
    for key, colour, dash in (("dpmpp2m/logsnr", ACCENT, False), ("ddim/logsnr", INK, True)):
        pts = [(s, v) for s, v in P[key] if s > 0]
        body += ax.path(pts, colour, 1.6, dash)
    tr = [(s, v) for s, v in P["ddim/trailing"] if s > 0]
    body += ax.path(tr, INK, 2.0)
    for s, v in tr:
        body += ax.dot(s, v, 3.2, INK)
    # the start at sigma = infinity, off the left edge
    s1, v1 = tr[0]
    body += path_line([(ax.x + 2, ax.Y(1.0) + 1), (ax.X(s1) - 6, ax.Y(v1) - 3)], INK, 1.2, True, arrow=True)
    body += tag(ax.x + 8, ax.Y(1.0) - 10, "START: PURE NOISE, σ = ∞", INK, "start", 8)
    body += tag(ax.X(s1) + 10, ax.Y(v1) + 4, f"STEP 1, ∞ → {s1:.0f}: {v1:.3f}", INK, "start", 8)
    six = tr[5]
    body += tag(ax.X(six[0]) + 8, ax.Y(six[1]) + 24, f"AFTER 6 STEPS (σ = {six[0]:.1f}): {six[1]:.3f}", INK, "start", 8)
    end_tr = P["ddim/trailing"][-1][1]
    end_ls = P["ddim/logsnr"][-1][1]
    end_pp = P["dpmpp2m/logsnr"][-1][1]
    rx = ax.x + ax.w - 4
    body += tag(rx, ax.Y(end_pp) - 8, f"DPM-SOLVER++(2M), LOG-SNR: {end_pp:.3f}", ACCENT, "end", 8)
    body += tag(rx, ax.Y(end_ls) + 16, f"DDIM, LOG-SNR: {end_ls:.3f}", INK, "end", 8)
    body += tag(rx, ax.Y(end_tr) + 16, f"DDIM, PART 5'S GRID: {end_tr:.3f}", INK, "end", 8)
    body += legend_row(96, vh - 64, [("DDIM, part 5's trailing grid", INK, False), ("DDIM, log-SNR grid", INK, True),
                                     ("DPM-Solver++(2M), log-SNR grid", ACCENT, False)], 18)
    body += footnote(vh - 38, f"Computed exactly by the lab: one Gaussian direction, data variance V₀ = {v0:,.2f} "
                              "(brightness of a 16,384-value image, part 5).")
    body += footnote(vh - 22, "Each dot is one DDIM step on the zero-terminal-SNR grid; log-SNR grids start at σ = 4,096. "
                              "Final values are at σ = 0.")
    emit(1, "where-ddim-loses-the-spread", "Where DDIM loses the spread",
         "The error is made in the few steps that straddle √V₀", body,
         "DDIM's value over the exact ODE's after each of 50 steps: it drops from 1 to 0.942 on the first step "
         "and to 0.860 by σ = 14.5, then stays; log-SNR spacing ends at 0.941 and DPM-Solver++ at 1.004", vw, vh)


# -------------------------------------------------------------------- fig 02

def fig02():
    vw, vh = 960, 490
    S = W["sweeps"]
    N1 = W["nfe_to_1pct"]
    body = eyebrow(40, 36, "one gaussian direction · error in the spread kept, against network calls")
    ax = Axes(96, 70, 620, 330, (math.log10(8), math.log10(2200)), (-4.3, 1.8), logx=True, logy=True)
    xt = [(v, f"{v:,}") for v in (10, 20, 50, 100, 200, 500, 1000, 2000)]
    body += ax.frame(xt, pow10_ticks(-4, 1), "NFE  (NETWORK CALLS PER SAMPLE, LOG)", "|1 − SPREAD KEPT|  (LOG)")
    body += ax.hline(0.01, ACCENT, True, 1.0)
    body += tag(ax.x + 8, ax.Y(0.01) - 6, "1% ERROR", ACCENT, "start", 8)
    series = [("ddim/trailing", INK, False, "DDIM, trailing"), ("ddim/logsnr", INK, True, "DDIM, log-SNR"),
              ("dpmpp2m/trailing", ACCENT, True, "DPM++(2M), trailing"),
              ("dpmpp2m/logsnr", ACCENT, False, "DPM++(2M), log-SNR"),
              ("heun/trailing4096", BLUE, True, "Heun, trailing from 4,096"),
              ("heun/logsnr", BLUE, False, "Heun, log-SNR")]
    for key, colour, dash, label in series:
        pts = [(r["nfe"], max(abs(1 - r["kept"]), 1e-6)) for r in S[key]]
        body += ax.path(pts, colour, 1.7, dash)
        for p in pts:
            body += ax.dot(p[0], p[1], 2.6, colour)
        n1 = N1[key]
        if n1:
            body += ax.dot(n1, 0.01, 4.4, colour, hollow=True)
    lab_y = {"ddim/trailing": 0, "ddim/logsnr": 0, "dpmpp2m/trailing": 0, "dpmpp2m/logsnr": 0,
             "heun/trailing4096": 0, "heun/logsnr": 0}
    # direct labels at the right edge, ordered by the curves' final heights
    finals = sorted(((max(abs(1 - S[k][-1]["kept"]), 1e-6), k) for k in lab_y), reverse=True)
    ly = ax.y + 18
    for err, key in finals:
        colour, dash, label = next((c, d, l) for k, c, d, l in series if k == key)
        n1 = N1[key]
        lx = ax.x + ax.w + 16
        d = ' stroke-dasharray="6,4"' if dash else ""
        body += (f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 20}" y2="{ly - 4}" stroke="{colour}" '
                 f'stroke-width="2.2"{d}/>')
        body += mono(lx + 26, ly, label, 8, colour, "start", 500)
        body += mono(lx + 26, ly + 12, f"1% AT NFE {n1:.0f}" if n1 else "", 7, SOFT, "start")
        ly += 40
    body += footnote(vh - 38, "Computed exactly on the worked example's direction (V₀ = 1,474.57). Hollow circles: "
                              "where each curve falls through 1% for good.")
    body += footnote(vh - 22, "Trailing: part 5's zero-terminal-SNR grid. Heun cannot start at σ = ∞, so it starts at "
                              "σ = 4,096 (diffusers' patch), as log-SNR grids do.")
    emit(2, "same-nfe-forty-fold", "Same calls, a forty-fold range of error",
         "First order halves the error per doubling; second order quarters it, once the steps are small",
         body, "Log-log error in the brightness spread against NFE for DDIM, DPM-Solver++(2M) and Heun on two grids: "
               "DDIM reaches 1% at 778 calls, DPM-Solver++(2M) with log-SNR spacing at 30", vw, vh)


# -------------------------------------------------------------------- fig 03

def fig03():
    vw, vh = 960, 520
    P = SAMPLES["paths"]
    sig = P["sigma"]
    body = eyebrow(40, 36, "exact ode paths of six samples (lines) and ddim with six steps (dashed), 32×32 crescents")
    ent = {round(e["sigma"]): e["entropy_bits"] for e in SAMPLES["decision_entropy"]}
    panels = [("crescent", "CRESCENT COORDINATE", 96), ("brightness", "BRIGHTNESS COORDINATE", 540)]
    for key, ylab, px in panels:
        vals = [v for row, s in zip(P[key], sig) if s <= 40 for v in row]
        lo, hi = min(vals), max(vals)
        pad = 0.08 * (hi - lo)
        ax = Axes(px, 96, 360, 300, (40, 0), (lo - pad, hi + pad))
        step = 20 if hi - lo > 80 else 10
        yt = [(v, minus(f"{v:.0f}")) for v in range(int(math.ceil((lo - pad) / step) * step), int(hi + pad) + 1, step)]
        body += ax.frame([(v, f"{v}") for v in (40, 30, 20, 10, 0)], yt, "NOISE LEVEL σ  (SAMPLING RUNS LEFT TO RIGHT)",
                         ylab)
        body += rect(ax.X(20), ax.y, ax.X(5) - ax.X(20), ax.h, ACCENT_TINT, "none", 0)
        for j in range(6):
            pts = [(s, row[j]) for s, row in zip(sig, P[key]) if s <= 41]
            body += ax.path(pts, MUTED, 1.4, opacity=0.9)
        sd = P["ddim6_sigma"]
        for j in range(6):
            pts = [(s, row[j]) for s, row in zip(sd, P[f"ddim6_{key}"])]
            body += ax.path(pts, ACCENT, 1.5, True)
            for s, row in zip(sd, P[f"ddim6_{key}"]):
                if s <= 40:
                    body += ax.dot(s, row[j], 3, ACCENT)
        body += mono(ax.X(12.5), ax.y + 14, "THE BEND", 8, ACCENT, "middle", 500)
    # decision entropy strip across the top
    body += mono(96, 70, "UNCERTAINTY ABOUT WHICH CRESCENT, BITS (OF 2):", 8, SOFT, "start", 500)
    x = 400
    for s in (40, 30, 20, 10, 5):
        body += mono(x, 70, f"σ {s}: {ent[s]:.2f}", 8, INK if s in (20, 10) else MUTED, "start", 500)
        x += 98
    body += legend_row(96, vh - 64, [("exact ODE path", MUTED, False), ("DDIM, six steps", ACCENT, True)], 18)
    body += footnote(vh - 38, "Measured with the exact denoiser. Crescent coordinate: projection on the difference of "
                              "two opposite crescents; brightness: on all-ones.")
    body += footnote(vh - 22, f"DDIM's six steps land at σ = {', '.join(f'{s:.3g}' for s in P['ddim6_sigma'][1:-1])}, then 0 "
                              "(EDM's ρ = 7 grid from σ = 80).")
    emit(3, "straight-lines-and-one-bend", "Straight lines and one bend",
         "In DDIM's coordinates the path is straight wherever the denoiser's answer holds still", body,
         "Exact ODE paths of six crescent samples against noise level, straight above σ = 20 and below σ = 5 and "
         "bending between, with DDIM's six-step chords cutting across the bend", vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    vw, vh = 960, 620
    body = eyebrow(40, 36, "one step from σ to σ′ on a log-snr axis · filled = a new denoiser call, hollow = reused")
    xs, xe = 330, 560                       # σ and σ′ for every row
    rows = [
        ("DDIM / Euler", "order 1 · 1 NFE", [("call", xs)], "x′ = D + (σ′/σ)(x − D)", "exact if D does not move"),
        ("Heun (EDM)", "order 2 · 2 NFE", [("call", xs), ("call", xe)], "Euler to σ′, call D there,",
         "average the two slopes"),
        ("DPM-Solver-2", "order 2 · 2 NFE", [("call", xs), ("call", (xs + xe) / 2)], "first-order step to √(σσ′);",
         "its noise estimate drives the step"),
        ("DPM-Solver-3", "order 3 · 3 NFE", [("call", xs), ("call", xs + (xe - xs) / 3), ("call", xs + 2 * (xe - xs) / 3)],
         "two inner calls at 1/3 and 2/3", "of the log-SNR step"),
        ("DPM-Solver++(2M)", "order 2 · 1 NFE", [("reuse", xs - 150), ("call", xs)], "D extrapolated from this call",
         "and the last: (1 + 1/2r)Dᵢ − (1/2r)Dᵢ₋₁"),
        ("Ancestral, η = 1", "stochastic · 1 NFE", [("call", xs)], "overshoot to σ_down = σ′²/σ,",
         "then add fresh noise σ_up"),
        ("EDM stochastic", "stochastic · 2 NFE", [("call", xs - 60), ("call", xe)], "add noise up to (1 + γ)σ,",
         "then one Heun step to σ′"),
    ]
    y0, gap = 92, 70
    body += mono(xs, y0 - 26, "σ", 10, INK, "middle", 600) + mono(xe, y0 - 26, "σ′", 10, INK, "middle", 600)
    body += mono(xs - 160, y0 - 26, "NOISIER", 8, SOFT, "start") + mono(xe + 90, y0 - 26, "CLEANER", 8, SOFT, "end")
    for i, (name, sub, pts, r1, r2) in enumerate(rows):
        y = y0 + i * gap
        body += text(40, y + 2, name, 12, INK, SANS, 600, "start")
        body += mono(40, y + 18, sub, 8, SOFT, "start")
        body += (f'<line x1="{xs - 165}" y1="{y}" x2="{xe + 95}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
                 f'<line x1="{xs}" y1="{y - 6}" x2="{xs}" y2="{y + 6}" stroke="{RULE_SOLID}" stroke-width="1"/>'
                 f'<line x1="{xe}" y1="{y - 6}" x2="{xe}" y2="{y + 6}" stroke="{RULE_SOLID}" stroke-width="1"/>')
        if name.startswith("Ancestral"):
            xd = xe + 70
            body += path_line([(xs + 7, y - 12), (xd - 2, y - 12)], ACCENT, 1.4, accent=True)
            body += mono((xs + xd) / 2, y - 18, "STEP TO σ_DOWN", 7, ACCENT, "middle", 500)
            body += (f'<circle cx="{xd}" cy="{y}" r="3" fill="{PAPER}" stroke="{SOFT}" stroke-width="1.2"/>')
            body += path_line([(xd - 4, y + 12), (xe + 6, y + 12)], LINK, 1.4)
            body += mono((xe + xd) / 2, y + 24, "+ NOISE σ_UP", 7, LINK, "middle", 500)
        elif name.startswith("EDM"):
            xh = xs - 60
            body += path_line([(xs - 4, y + 12), (xh + 6, y + 12)], LINK, 1.4)
            body += mono((xs + xh) / 2, y + 24, "+ NOISE", 7, LINK, "middle", 500)
            body += path_line([(xh + 7, y - 12), (xe - 6, y - 12)], ACCENT, 1.4, accent=True)
            body += mono((xh + xe) / 2, y - 18, "HEUN STEP FROM (1 + γ)σ", 7, ACCENT, "middle", 500)
        else:
            body += path_line([(xs + 7, y - 12), (xe - 6, y - 12)], ACCENT, 1.4, accent=True)
        for kind, px in pts:
            if kind == "reuse":
                body += (f'<circle cx="{px}" cy="{y}" r="5" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.6"/>')
                body += mono(px, y + 20, "LAST STEP'S D", 7, SOFT, "middle")
            else:
                body += f'<circle cx="{px}" cy="{y}" r="5" fill="{ACCENT}"/>'
        body += mono(xe + 120, y - 2, r1, 8, INK, "start", 500)
        body += mono(xe + 120, y + 12, r2, 8, MUTED, "start")
    body += footnote(vh - 38, "To scale on a log-SNR axis except two marks: the ancestral overshoot, which really reaches "
                              "as far past σ′ as σ is before it,")
    body += footnote(vh - 22, "and 2M's previous call, drawn after a step two-thirds as long. Every method ends with a "
                              "plain DDIM step to σ = 0.")
    emit(5, "what-each-solver-evaluates", "What each solver evaluates in one step",
         "Higher order means more information about how the denoiser's answer drifts across the step", body,
         "Seven samplers drawn as one step on a log-SNR axis, with dots where each calls the denoiser: one call for "
         "DDIM, two for Heun, three for DPM-Solver-3, one plus a reused call for DPM-Solver++(2M)", vw, vh)


# -------------------------------------------------------------------- fig 06

def fig06():
    vw, vh = 960, 515
    C, NG = ODE["curves"], ODE["nfe_to_grey"]
    body = eyebrow(40, 36, "rms distance from the exact ode endpoint, 256 shared starts, edm's ρ = 7 grid")
    ax = Axes(96, 70, 690, 350, (0, 3), (-7.3, 0.3), logx=True, logy=True)
    body += ax.frame([(v, f"{v:,}") for v in (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000)], pow10_ticks(-7, 0),
                     "NFE  (NETWORK CALLS PER SAMPLE, LOG)", "RMS ERROR  (LOG)")
    body += ax.hline(GREY, ACCENT, True, 1.0)
    body += tag(ax.x + 8, ax.Y(GREY) - 6, "ONE 8-BIT GREY LEVEL", ACCENT, "start", 8)
    order = ["ddim", "heun", "dpm2", "dpmpp2m", "dpm3"]
    for smp in order:
        label, colour, dash = STYLE[smp]
        rows = C[f"{smp}/edm7"]
        pts = [(r["nfe"], r["rms"]) for r in rows]
        body += ax.path(pts, colour, 1.8, dash)
        n = NG[f"{smp}/edm7"]
        if n:
            body += ax.dot(n, GREY, 4.6, colour, hollow=True)
    # slope guides: a fan in the empty top-right region, from 150 to 450 NFE
    a0, a1, e0 = 150, 450, 0.5
    for p in (1, 2, 3):
        e1 = e0 * (a0 / a1) ** p
        body += ax.path([(a0, e0), (a1, e1)], SOFT, 1.0, True)
        body += mono(ax.X(a1) + 6, ax.Y(e1) + 3, f"SLOPE −{p}", 7, SOFT, "start")
    body += mono(ax.X(a0) - 6, ax.Y(e0) + 3, "ORDER", 7, SOFT, "end")
    ly = ax.y + 10
    for smp in order:
        label, colour, dash = STYLE[smp]
        body += mono(ax.x + ax.w + 14, ly, label, 8, colour, "start", 500)
        body += mono(ax.x + ax.w + 14, ly + 12, f"GREY LEVEL AT NFE {NG[f'{smp}/edm7']}", 7, SOFT, "start")
        ly += 36
    body += footnote(vh - 38, f"Measured by the lab: exact denoiser, so the reference is the exact ODE solution (RK4, "
                              f"self-check {ODE['reference_self_check_rms']:.0e}); 32×32 crescents, σ from 80 to 0.002.")
    body += footnote(vh - 22, "Hollow circles: the NFE from which each curve stays under one grey level (2/256, data "
                              "scaled to [−1, 1]) for every larger NFE in the sweep.")
    emit(6, "error-against-nfe", "Error against network calls",
         "Order is the slope; it pays only once the steps are small enough", body,
         "Log-log RMS error against NFE for DDIM, Heun, DPM-Solver-2, DPM-Solver++(2M) and DPM-Solver-3, with slopes "
         "near 1, 2 and 3 and one grey level reached at 100, 49, 41, 25 and 16 calls", vw, vh)


# -------------------------------------------------------------------- fig 07

def fig07():
    vw, vh = 960, 520
    body = eyebrow(40, 36, "quoted from dpm-solver (neurips 2022) · fid on cifar-10, lower is better")
    ax = Axes(90, 80, 330, 300, (12, 48), (math.log10(2.3), math.log10(130)), logy=True)
    body += mono(90, 62, "SAME ORDER, THREE FORMULATIONS · TABLE 1", 8, INK, "start", 600)
    body += ax.frame([(v, str(v)) for v in DPMS_T1["nfe"]],
                     [(v, f"{v}") for v in (3, 5, 10, 20, 50, 100)], "NFE", "FID  (LOG)")
    style1 = {"RK2 in t": (SAGE, True), "RK2 in λ": (SAGE, "dot"), "DPM-Solver-2": (SAGE, False),
              "RK3 in t": (MUSTARD, True), "RK3 in λ": (MUSTARD, "dot"), "DPM-Solver-3": (MUSTARD, False)}
    for k, (colour, dash) in style1.items():
        pts = list(zip(DPMS_T1["nfe"], DPMS_T1[k]))
        body += ax.path(pts, colour, 1.8 if not dash else 1.4, dash)
        for p in pts:
            body += ax.dot(p[0], p[1], 2.4, colour)
    body += legend_row(90, 438, [("RK, time t", MUTED, True), ("RK, log-SNR λ", MUTED, "dot"),
                                 ("DPM-Solver", MUTED, False)], 10)
    body += mono(90, 456, "GREEN: SECOND ORDER · OCHRE: THIRD ORDER", 7, SOFT, "start")
    bx = Axes(560, 80, 360, 300, (1, 3), (math.log10(2.5), math.log10(320)), logx=True, logy=True)
    body += mono(560, 62, "ONE CHECKPOINT, FIVE SAMPLERS · TABLE 4", 8, INK, "start", 600)
    body += bx.frame([(v, f"{v:,}") for v in (10, 20, 50, 100, 200, 500, 1000)],
                     [(v, f"{v}") for v in (3, 5, 10, 20, 50, 100, 200)], "NFE  (LOG)", "FID  (LOG)")
    style4 = {"DDPM ancestral": (LINK, True), "Analytic-DDPM": (LINK, "dot"), "DDIM": (INK, False),
              "Analytic-DDIM": (INK, "dot")}
    for k, (colour, dash) in style4.items():
        pts = list(zip(DPMS_T4["nfe"], DPMS_T4[k]))
        body += bx.path(pts, colour, 1.6, dash)
        for p in pts:
            body += bx.dot(p[0], p[1], 2.4, colour)
    pts = list(DPMS_T4_SOLVER)
    body += bx.path(pts, MUSTARD, 2.0)
    for p in pts:
        body += bx.dot(p[0], p[1], 3, MUSTARD)
    body += legend_row(560, 438, [("DDPM", LINK, True), ("Analytic-DDPM", LINK, "dot"), ("DDIM", INK, False)], 8)
    body += legend_row(560, 456, [("Analytic-DDIM", INK, "dot"), ("DPM-Solver", MUSTARD, False)], 8)
    body += footnote(vh - 38, "Left: continuous-time VP model; RK in t on uniform t steps, the rest on uniform λ steps. "
                              "Right: DDPM's discrete-time model.")
    body += footnote(vh - 22, "DPM-Solver at end time 10⁻³ up to 15 NFE and 10⁻⁴ above, as the paper advises; 46 NFE is "
                              "its adaptive run. Lu et al. 2022, Tables 1 and 4.")
    emit(7, "dpm-solver-tables", "Formulation and sampler, on one checkpoint",
         "The same order of accuracy can be ten times better or worse depending on what it is applied to", body,
         "Two quoted panels: second- and third-order Runge–Kutta in t or λ against DPM-Solver at 12 to 48 NFE, "
         "and DDPM, Analytic-DDPM, DDIM, Analytic-DDIM and DPM-Solver on one CIFAR-10 model from 10 to 1,000 NFE",
         vw, vh)


# -------------------------------------------------------------------- fig 08

def fig08():
    vw, vh = 960, 560
    G = SAMPLES["grid"]
    body = eyebrow(40, 36, "the same three starting noises · 32×32 crescents · exact denoiser")
    size, gap, cg = 52, 6, 36
    cw = 3 * size + 2 * gap
    x0 = 230
    budgets = (5, 10, 20)
    for c, b in enumerate(budgets):
        body += mono(x0 + c * (cw + cg) + cw / 2, 84, f"ABOUT {b} NFE", 9, INK, "middle", 600)
    y = 100
    body += text(40, y + 30, "Exact ODE endpoint", 12, INK, SANS, 600, "start")
    body += mono(40, y + 46, "RK4, 8,000 CALLS", 8, SOFT, "start")
    body += mono(40, y + 60, "REPEATED IN EACH COLUMN", 8, SOFT, "start")
    for c in range(3):
        for j in range(3):
            body += tile(x0 + c * (cw + cg) + j * (size + gap), y, size, SAMPLES["exact"][j])
    y += size + 30
    body += f'<line x1="40" y1="{y - 14}" x2="{vw - 40}" y2="{y - 14}" stroke="{RULE}" stroke-width="1"/>'
    for smp in ("ddim", "heun", "dpmpp2m", "ancestral"):
        label, colour, dash = STYLE[smp]
        body += text(40, y + 30, label, 12, INK, SANS, 600, "start")
        for c, b in enumerate(budgets):
            cell = G[f"{smp}/{b}"]
            for j in range(3):
                body += tile(x0 + c * (cw + cg) + j * (size + gap), y, size, cell["images"][j])
            body += mono(x0 + c * (cw + cg) + cw, y + size + 12, f"{cell['nfe']} NFE", 7, SOFT, "end")
        y += size + 26
    body += footnote(vh - 38, "Measured by the lab: EDM's ρ = 7 grid from σ = 80; Heun's budgets are odd (2N − 1). "
                              "Ancestral draws fresh noise,")
    body += footnote(vh - 24, "so its images are different crescents from the exact ones by design. Display: −1.6 "
                              "black to +1.6 white, high = bright.")
    emit(8, "samples-at-low-nfe", "Samples at five, ten and twenty calls",
         "Too few deterministic steps blur the detail or leave noise in; ancestral sampling loses detail longest", body,
         "Grid of crescent samples from four samplers at about 5, 10 and 20 network calls beside the exact ODE endpoints "
         "of the same three starting noises", vw, vh)


# -------------------------------------------------------------------- fig 09

def fig09():
    vw, vh = 960, 520
    Gs = LOCAL["grids"]
    body = eyebrow(40, 36, f"error of one step started on the exact path · {LOCAL['N']} steps per grid · 32×32 crescents")
    styles = {"uniform": (MUTED, "dot"), "edm3": (BLUE, False), "edm7": (ACCENT, False), "logsnr": (SAGE, True)}
    for key, title, px in (("ddim", "DDIM / EULER", 96), ("heun", "HEUN", 540)):
        vals = [r[key] for g in Gs.values() for r in g]
        ax = Axes(px, 84, 340, 300, (math.log10(80), math.log10(0.002)), (-10.3, 0.5), logx=True, logy=True)
        body += mono(px, 70, title, 9, INK, "start", 600)
        body += rect(ax.X(30), ax.y, ax.X(5) - ax.X(30), ax.h, ACCENT_TINT, "none", 0)
        body += rect(ax.X(0.3), ax.y, ax.X(0.03) - ax.X(0.3), ax.h, "rgba(46,90,168,0.06)", "none", 0)
        body += ax.frame([(v, lab) for v, lab in ((30, "30"), (10, "10"), (3, "3"), (1, "1"), (0.3, "0.3"),
                                                   (0.1, "0.1"), (0.03, "0.03"), (0.01, "0.01"))],
                         pow10_ticks(-10, 0, 2), "σ AT THE END OF THE STEP  (LOG)", "RMS ERROR OF ONE STEP" if key == "ddim" else "")
        body += mono(ax.X(12), ax.y + 14, "SHAPE AND BRIGHTNESS", 7, ACCENT, "middle", 500)
        body += mono(ax.X(0.1), ax.y + 14, "DETAIL, τ = 0.1", 7, LINK, "middle", 500)
        for sched, (colour, dash) in styles.items():
            pts = [(r["sigma_to"], max(r[key], 1e-12)) for r in Gs[sched]]
            body += ax.path(pts, colour, 1.6, dash)
            for p in pts:
                body += ax.dot(p[0], p[1], 2.2, colour)
    body += legend_row(96, vh - 66, [("uniform in σ (ρ = 1)", MUTED, "dot"), ("EDM ρ = 3", BLUE, False),
                                     ("EDM ρ = 7", ACCENT, False), ("log-SNR", SAGE, True)], 18)
    body += footnote(vh - 38, "Measured by the lab: each point is one step from the exact state at the previous grid "
                              "point, compared with the exact state at its own (RK4 between).")
    body += footnote(vh - 22, "Shaded: where the toy's structure is decided (σ ≈ 5–30, which crescent and how bright) "
                              "and where its fine detail is (σ near τ = 0.1).")
    emit(9, "local-error-per-noise-level", "Where each step makes its error",
         "The schedule moves error between noise levels; it cannot remove the bends", body,
         "Two log-log panels of one-step error against noise level for DDIM and Heun under four 32-step schedules, "
         "peaking where the toy's structure and detail are decided", vw, vh)


# -------------------------------------------------------------------- fig 10

def fig10():
    vw, vh = 960, 500
    NG = ODE["nfe_to_grey"]
    body = eyebrow(40, 36, "nfe needed to stay within one grey level of the exact endpoint · measured on the toy")
    cols = ["vp_time", "logsnr", "edm3", "edm7", "uniform"]
    rows = ["ddim", "heun", "dpm2", "dpmpp2m", "dpm3"]
    x0, y0, cw, ch = 190, 92, 72, 46
    for j, s in enumerate(cols):
        body += mono(x0 + j * cw + cw / 2, y0 - 12, ascii_upper(SCHED_LABEL[s]), 7, MUTED, "middle", 500)
    vals = [NG[f"{r}/{s}"] for r in rows for s in cols if NG[f"{r}/{s}"]]
    lo, hi = math.log10(min(vals)), math.log10(1000)
    for i, r in enumerate(rows):
        label, colour, dash = STYLE[r]
        body += text(x0 - 14, y0 + i * ch + ch / 2 + 4, label, 11, INK, SANS, 600, "end")
        for j, s in enumerate(cols):
            v = NG[f"{r}/{s}"]
            x, y = x0 + j * cw, y0 + i * ch
            if v is None:
                body += rect(x + 2, y + 2, cw - 4, ch - 4, "#ffffff", RULE_SOLID, 3, 0.8)
                body += mono(x + cw / 2, y + ch / 2 + 3, "NEVER", 8, SOFT, "middle", 500)
                continue
            u = 1 - (math.log10(v) - lo) / (hi - lo)
            body += rect(x + 2, y + 2, cw - 4, ch - 4, f"rgba(235,108,54,{0.08 + 0.6 * u:.2f})", "none", 3)
            body += text(x + cw / 2, y + ch / 2 + 4, f"{v}", 12, INK, MONO, 600, "middle")
    body += mono(x0, y0 + 5 * ch + 22, "WHITE: NEVER WITHIN 1,000 NFE. DEEPER ORANGE: FEWER CALLS.", 7, SOFT, "start")
    # right: AYS
    ax = Axes(640, 92, 270, 250, (10, 50), (math.log10(1.8), math.log10(20)), logy=True)
    body += mono(640, 66, "QUOTED: OPTIMISED STEPS · CIFAR-10 FID", 8, INK, "start", 600)
    body += ax.frame([(v, str(v)) for v in AYS_T5["nfe"]], [(v, f"{v}") for v in (2, 3, 5, 10, 20)],
                     "NFE", "FID  (LOG)")
    st = {"DDIM, log-SNR steps": (INK, True), "DDIM, AYS steps": (INK, False),
          "DPM-Solver++(2M), log-SNR": (ACCENT, True), "DPM-Solver++(2M), AYS": (ACCENT, False)}
    for k, (colour, dash) in st.items():
        pts = list(zip(AYS_T5["nfe"], AYS_T5[k]))
        body += ax.path(pts, colour, 1.7, dash)
        for p in pts:
            body += ax.dot(p[0], p[1], 2.6, colour)
    body += legend_row(640, 400, [("log-SNR steps", MUTED, True), ("AYS steps", MUTED, False)], 8)
    body += mono(640, 418, "BLACK: DDIM · ORANGE: DPM-SOLVER++(2M)", 7, SOFT, "start")
    body += footnote(vh - 38, "Left, measured: 32×32 crescents, σ from 80 to 0.002, 256 starts; the NFE from which the "
                              "error stays under 2/256 at every larger NFE tried.")
    body += footnote(vh - 22, "Right, quoted from Sabour, Fidler & Kreis (ICML 2024), Table 5: EDM's CIFAR-10 model, "
                              "50,000 samples.")
    emit(10, "schedules-at-matched-nfe", "The schedule matters as much as the order",
         "Same solver, different steps: five to sixteen times the calls for the same accuracy", body,
         "A grid of the NFE each solver needs under five step schedules, beside quoted CIFAR-10 FID for DDIM and "
         "DPM-Solver++(2M) with log-SNR and optimised steps", vw, vh)


# -------------------------------------------------------------------- fig 11

def fig11():
    vw, vh = 960, 520
    body = eyebrow(40, 36, "measured with the exact denoiser · left: a good start · right: part 5's flawed start")
    C = SDE["curves"]
    ax = Axes(96, 84, 360, 300, (math.log10(3), math.log10(520)), (-1.1, 1.05), logx=True, logy=True)
    body += mono(96, 70, "FINE DETAIL OF THE SAMPLES, ÷ THE DATA'S", 8, INK, "start", 600)
    body += ax.frame([(v, str(v)) for v in (3, 10, 30, 100, 300)],
                     [(v, lab) for v, lab in ((0.1, "0.1"), (0.3, "0.3"), (1, "1"), (3, "3"), (10, "10"))],
                     "NFE  (LOG)", "DETAIL RATIO  (LOG)")
    body += ax.hline(1.0, SOFT, True)
    body += tag(ax.x + ax.w - 4, ax.Y(1.0) - 6, "THE DATA", SOFT, "end", 8)
    for smp in ("ddim", "heun", "dpmpp2m", "ancestral", "edm_sde"):
        label, colour, dash = STYLE[smp]
        pts = [(r["nfe"], r["detail"]) for r in C[smp] if r["nfe"] >= 3]
        body += ax.path(pts, colour, 1.8, dash)
    body += tag(ax.x + ax.w - 6, ax.y + ax.h - 12, "BELOW 1: TOO SMOOTH", SOFT, "end", 8)
    body += tag(ax.x + ax.w - 6, ax.y + 16, "ABOVE 1: NOISE LEFT IN", SOFT, "end", 8)
    body += legend_row(96, 440, [("DDIM", INK, False), ("Heun", BLUE, False), ("DPM++(2M)", ACCENT, False)], 10)
    body += legend_row(96, 458, [("ancestral", LINK, True), ("EDM stochastic", PURPLE, True)], 10)
    F = W["flawed"]
    bx = Axes(560, 84, 350, 300, (math.log10(20), math.log10(1200)), (0.30, 0.55), logx=True)
    body += mono(560, 70, "BRIGHTNESS SPREAD KEPT, PART 5'S FLAWED SCHEDULE", 8, INK, "start", 600)
    body += bx.frame([(v, f"{v:,}") for v in (25, 50, 100, 200, 500, 1000)],
                     [(v, f"{v:.2f}") for v in (0.30, 0.35, 0.40, 0.45, 0.50, 0.55)], "SAMPLING STEPS  (LOG)", "")
    body += bx.hline(F["ode_limit"], INK, True)
    body += bx.hline(F["sde_limit"], LINK, True)
    body += tag(bx.x + 6, bx.Y(F["ode_limit"]) - 6, f"EXACT ODE: {F['ode_limit']:.3f}", INK, "start", 8)
    body += tag(bx.x + 6, bx.Y(F["sde_limit"]) - 6, f"EXACT REVERSE SDE: {F['sde_limit']:.3f}", LINK, "start", 8)
    for key, colour, dash in (("ddim", INK, False), ("dpmpp2m", ACCENT, False), ("ancestral", LINK, False)):
        pts = [(r["steps"], r[key]) for r in F["rows"]]
        body += bx.path(pts, colour, 1.8, dash)
        for p in pts:
            body += bx.dot(p[0], p[1], 3, colour)
    m = next(r for r in CAP["worked_measured"]["rows"] if r["schedule"] == "flawed")
    mx = bx.X(m["steps"] * 1.07)
    body += (f'<line x1="{mx:.1f}" y1="{bx.Y(m["kept"] - 2 * m["kept_se"]):.1f}" x2="{mx:.1f}" '
             f'y2="{bx.Y(m["kept"] + 2 * m["kept_se"]):.1f}" stroke="{LINK}" stroke-width="1.4"/>')
    body += f'<rect x="{mx - 4:.1f}" y="{bx.Y(m["kept"]) - 4:.1f}" width="8" height="8" fill="{PAPER}" stroke="{LINK}" stroke-width="1.6"/>'
    body += tag(bx.x + bx.w - 4, bx.Y(0.528), f"MEASURED AT {m['steps']} STEPS, 16,384 PX: {m['kept']:.3f} ± "
                f"{2 * m['kept_se']:.3f}", LINK, "end", 8)
    body += path_line([(mx, bx.Y(0.524)), (mx, bx.Y(m["kept"] + 2 * m["kept_se"]) - 3)], LINK, 1.0, arrow=False)
    body += legend_row(560, 440, [("DDIM", INK, False), ("DPM++(2M)", ACCENT, False), ("ancestral", LINK, False)], 10)
    body += footnote(vh - 38, f"Left: 32×32 crescents, {SDE['samples']:,} samples per point, EDM's ρ = 7 grid; detail "
                              "ratio 1 is the data's own per-pixel detail. Right: computed exactly (lines),")
    body += footnote(vh - 22, "and measured once on 2,000 images of 16,384 values (square, ±2 standard errors); "
                              "trailing spacing on Stable Diffusion's schedule, part 5's setup.")
    emit(11, "noise-costs-and-buys", "Noise costs accuracy and buys forgetting",
         "With a good start, deterministic samplers converge faster; with a wrong start, only noise moves the answer",
         body, "Left: sample detail against NFE for three deterministic and two stochastic samplers, converging to the "
               "data's level fastest for DPM-Solver++(2M); right: spread kept on part 5's flawed schedule, stuck at "
               "0.357 for DDIM and rising toward 0.487 for ancestral sampling", vw, vh)


# -------------------------------------------------------------------- fig 12

def fig12():
    vw, vh = 960, 520
    body = eyebrow(40, 36, "quoted · fid, lower is better · each panel is one model, so compare within a panel only")
    ax = Axes(96, 84, 380, 300, (math.log10(30), math.log10(1200)), (math.log10(1.2), math.log10(70)), logx=True, logy=True)
    body += mono(96, 70, "IMAGENET 64×64, EDM'S MODEL · RESTART, TABLES 4–5", 8, INK, "start", 600)
    body += ax.frame([(v, f"{v:,}") for v in (30, 50, 100, 200, 500, 1000)],
                     [(v, f"{v}") for v in (1.5, 2, 3, 5, 10, 20, 50)], "NFE  (LOG)", "FID  (LOG)")
    st = {"ODE (Heun)": (BLUE, False), "EDM stochastic": (PURPLE, True), "Euler–Maruyama SDE": (LINK, "dot"),
          "Restart": (ACCENT, False)}
    for k, (colour, dash) in st.items():
        pts = list(RESTART_T4[k])
        body += ax.path(pts, colour, 1.8, dash)
        for p in pts:
            body += ax.dot(p[0], p[1], 2.6, colour)
    body += legend_row(96, 440, [("ODE, Heun", BLUE, False), ("EDM stochastic", PURPLE, True)], 10)
    body += legend_row(96, 458, [("Euler–Maruyama SDE", LINK, "dot"), ("Restart", ACCENT, False)], 10)
    bx = Axes(560, 84, 350, 300, (1, 3), (math.log10(2.5), math.log10(420)), logx=True, logy=True)
    body += mono(560, 70, "CIFAR-10, ONE DDPM-TRAINED MODEL · DDIM, TABLE 1", 8, INK, "start", 600)
    body += bx.frame([(v, f"{v:,}") for v in (10, 20, 50, 100, 200, 500, 1000)],
                     [(v, f"{v}") for v in (3, 5, 10, 30, 100, 300)], "SAMPLING STEPS = NFE  (LOG)", "")
    st2 = {"η = 0 (DDIM)": (INK, False), "η = 0.5": (MUTED, True), "η = 1 (DDPM)": (LINK, True),
           "DDPM, larger noise": (LINK, "dot")}
    for k, (colour, dash) in st2.items():
        pts = list(zip(DDIM_T1["steps"], DDIM_T1[k]))
        body += bx.path(pts, colour, 1.8, dash)
        for p in pts:
            body += bx.dot(p[0], p[1], 2.6, colour)
    body += legend_row(560, 440, [("η = 0, DDIM", INK, False), ("η = 0.5", MUTED, True)], 10)
    body += legend_row(560, 458, [("η = 1, DDPM", LINK, True), ("DDPM, larger noise", LINK, "dot")], 10)
    body += footnote(vh - 38, "Left: Xu et al. (NeurIPS 2023), class-conditional ImageNet 64×64, EDM's checkpoint, "
                              "50,000 samples; Euler–Maruyama is")
    body += footnote(vh - 24, "reported from 128 NFE up. Right: Song, Meng & Ermon (ICLR 2021), CIFAR-10, T = 1000; "
                              "larger noise is DDPM's σ² = β.")
    emit(12, "published-ode-vs-sde", "Deterministic wins early, stochastic wins late",
         "Two models, the same crossover", body,
         "Two quoted panels: ImageNet-64 FID against NFE for Heun, EDM's stochastic sampler, Euler–Maruyama and Restart; "
         "CIFAR-10 FID against steps for DDIM at η = 0, 0.5, 1 and DDPM's larger noise", vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    body = eyebrow(72, 73, "diffusion · part six")
    body += text(72, 148, "Diffusion samplers and solvers", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "1,000 steps into 20 — measured against the exact path", 15, MUTED, MONO, 400, "start")
    # left: error against network calls, DDIM against a third-order solver
    C, NG = ODE["curves"], ODE["nfe_to_grey"]
    ax = Axes(96, 248, 420, 200, (0, 3), (-7.3, 0.3), logx=True, logy=True)
    body += ax.frame()
    body += ax.hline(GREY, ACCENT, True, 1.0)
    for smp, colour in (("ddim", INK), ("dpm3", ACCENT)):
        pts = [(r["nfe"], r["rms"]) for r in C[f"{smp}/edm7"]]
        body += ax.path(pts, colour, 2.6)
        body += ax.dot(NG[f"{smp}/edm7"], GREY, 6, colour, hollow=True)
    body += tag(ax.X(NG["ddim/edm7"]) + 10, ax.Y(GREY) - 12, f"DDIM: {NG['ddim/edm7']} CALLS", INK, "start", 10)
    body += tag(ax.X(NG["dpm3/edm7"]) - 12, ax.Y(GREY) + 28, f"THIRD ORDER: {NG['dpm3/edm7']}", ACCENT, "end", 10)
    body += mono(ax.x, ax.y + ax.h + 24, "ERROR AGAINST NETWORK CALLS, 1 TO 1,000 (LOG–LOG)", 9, MUTED, "start", 500)
    # right: the exact paths and DDIM's six chords, ending on the crescents they reach
    P = SAMPLES["paths"]
    sig = P["sigma"]
    vals = [v for row, sg in zip(P["crescent"], sig) if sg <= 40 for v in row]
    bx = Axes(626, 238, 380, 220, (40, 0), (min(vals) - 4, max(vals) + 4))
    body += bx.frame()
    for j in range(6):
        body += bx.path([(sg, row[j]) for sg, row in zip(sig, P["crescent"]) if sg <= 41], MUTED, 1.6)
        body += bx.path([(sg, row[j]) for sg, row in zip(P["ddim6_sigma"], P["ddim6_crescent"])], ACCENT, 1.8, True)
    ends, used = [], []
    for j, v in enumerate(P["crescent"][-1]):
        if all(abs(v - u) > 6 for u in used):
            used.append(v)
            ends.append((v, j))
    size, gap = 50, 8
    slots = sorted((bx.Y(v) - size / 2, v, j) for v, j in ends)      # top to bottom
    ys = []
    for y, v, j in slots:                                             # keep tiles apart, in order
        ys.append(max(y, ys[-1] + size + gap) if ys else y)
    shift = max(0.0, ys[-1] + size - (bx.y + bx.h + 12))
    for (y0, v, j), y in zip(slots, ys):
        y -= shift
        body += path_line([(bx.x + bx.w + 4, bx.Y(v)), (bx.x + bx.w + 14, bx.Y(v)), (bx.x + bx.w + 14, y + size / 2),
                           (bx.x + bx.w + 22, y + size / 2)], SOFT, 1.0, arrow=False)
        body += tile(bx.x + bx.w + 22, y, size, SAMPLES["exact"][j])
    body += mono(bx.x, bx.y + bx.h + 24, "EXACT PATHS (SOLID) AND SIX DDIM STEPS (DASHED), NOISE TO IMAGE", 9, MUTED,
                 "start", 500)
    body += f'<line x1="72" y1="508" x2="1128" y2="508" stroke="{RULE}" stroke-width="1"/>'
    body += text(72, 548, "A sampler is an ODE solver.", 20, MUTED, SERIF, 400, "start", italic=True)
    emit_cover(body, "Error against network calls for DDIM and a third-order solver, beside exact sampling paths "
                     "that bend once and end on crescents")


# keyed by the figure number that reaches the post; 4 is Mermaid
FIGURES = {1: fig01, 2: fig02, 3: fig03, 5: fig05, 6: fig06, 7: fig07, 8: fig08, 9: fig09, 10: fig10,
           11: fig11, 12: fig12}

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    for k in [int(a) for a in args if a.isdigit()]:
        FIGURES[k]()
    if "cover" in args:
        cover()
    if not args:
        for fn in FIGURES.values():
            fn()
        cover()
