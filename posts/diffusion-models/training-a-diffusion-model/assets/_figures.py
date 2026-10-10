#!/usr/bin/env python3
"""Figures for "Training a Diffusion Model: The Decisions Before Step One" (diffusion-models, part 5).

Every measured number drawn here is read from ../lab/captures.json, the capture that the
article's lab download ships, so the prose, the figures and the lab cannot drift apart.
Numbers quoted from papers (Hang et al. 2025's Table 3, EDM2's Table 2) are typed once, below,
next to the ledger keys they come from. Closed-form curves are computed here and say so.

    python3 _figures.py            # all placed/plot/chart figures plus the cover
    python3 _figures.py 3 10       # just those
    python3 _figures.py cover      # just the cover
Figure 1 is Mermaid (python3 _mermaid.py); Figure 8 is Lin et al.'s Figure 3, extracted unchanged.
"""

from __future__ import annotations

import json
import math
import pathlib

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUSTARD, MUTED, PAPER, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, emit, emit_cover, eyebrow, h_arrow, mono, rect, subtext, text, v_arrow,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ primitives

class Axes:
    """Data-to-pixel mapping for a real plot. logx/logy put that axis on log10."""

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
        d = ' stroke-dasharray="6,4"' if dash else ""
        s = " ".join(f"{self.X(a):.1f},{self.Y(b):.1f}" for a, b in pts)
        return (f'<g clip-path="url(#{self.clip})"><polyline points="{s}" fill="none" '
                f'stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" '
                f'stroke-linecap="round" opacity="{opacity}"{d}/></g>')

    def dot(self, a, b, r=4, colour=ACCENT, hollow=False):
        if hollow:
            return (f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" '
                    f'fill="{PAPER}" stroke="{colour}" stroke-width="1.6"/>')
        return (f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{colour}"/>')


def plate(x, y, w, h=16):
    return rect(x, y, w, h, PAPER, "none", 3)


def tag(x, y, value, fill=INK, anchor="middle", size=9, weight=500, bg=True, w=None):
    """A label on an opaque plate so a line passing behind it cannot cut it."""
    w = w or len(value) * size * 0.62 + 10
    left = x - w / 2 if anchor == "middle" else (x - 5 if anchor == "start" else x - w + 5)
    out = plate(left, y - size - 2, w, size + 7) if bg else ""
    return out + text(x, y, value, size, fill, MONO, weight, anchor)


def footnote(y, value, x=60):
    return mono(x, y, value, 8, SOFT, "start")


def verdict(x, y, w, body):
    out = rect(x, y, w, 30, ACCENT_TINT, ACCENT, 4, 1)
    out += text(x + 14, y + 19, body, 10, INK, MONO, 500, "start")
    return out


def path_line(points, colour=MUTED, width=1.2, dashed=False, accent=False, arrow=True):
    """A polyline with an optional arrowhead at the last point."""
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


def valgrid(x, y, M, cell, gap=3, lo=-1.5, hi=1.5, digits=2, size=10):
    """A patch drawn as cells shaded by value, each printing its value."""
    out = ""
    for r, row in enumerate(M):
        for c, v in enumerate(row):
            g = grey(v, lo, hi)
            cx, cy = x + c * (cell + gap), y + r * (cell + gap)
            out += (f'<rect x="{cx}" y="{cy}" width="{cell}" height="{cell}" rx="2" '
                    f'fill="rgb({g},{g},{g})"/>')
            ink = INK if g > 140 else "#ffffff"
            out += text(cx + cell / 2, cy + cell / 2 + size * 0.36, f"{v:.{digits}f}".replace("-", "−"),
                        size, ink, MONO, 500)
    return out


def cells(x, y, n_cols, n_rows, cell, gap, fill="#ffffff", stroke=RULE_SOLID, count=None, sw=0.8):
    """Empty cells in a grid: token strips, attention-pair grids."""
    out, k = "", 0
    for r in range(n_rows):
        for c in range(n_cols):
            if count is not None and k >= count:
                return out
            out += (f'<rect x="{x + c * (cell + gap):.1f}" y="{y + r * (cell + gap):.1f}" '
                    f'width="{cell}" height="{cell}" rx="1" fill="{fill}" stroke="{stroke}" '
                    f'stroke-width="{sw}"/>')
            k += 1
    return out


def motif(n):
    """The bright crescent on a dark field that every part of the series carries."""
    M, c0 = [], (n - 1) / 2
    for r in range(n):
        row = []
        for c in range(n):
            d = (((r - c0) ** 2 + (c - c0) ** 2) ** 0.5) / (n / 2)
            v = 0.95 if d < 0.60 else (-0.85 if d > 0.78 else 0.10)
            d2 = (((r - c0 + n * 0.17) ** 2 + (c - c0 + n * 0.17) ** 2) ** 0.5) / (n / 2)
            if d < 0.60 and d2 < 0.46:
                v = -0.50
            row.append(v)
        M.append(row)
    return M


def lcg_normals(n, seed=20260925):
    """Deterministic standard normals, the same generator part 3's lab ships."""
    state, out = seed, []
    while len(out) < n:
        state = (1103515245 * state + 12345) % 2147483648
        u1 = (state + 1) / 2147483649
        state = (1103515245 * state + 12345) % 2147483648
        u2 = state / 2147483648
        r = math.sqrt(-2 * math.log(u1))
        out += [r * math.cos(2 * math.pi * u2), r * math.sin(2 * math.pi * u2)]
    return out[:n]


def noisy_motif(n, abar=0.64, seed=7):
    clean = motif(n)
    eps = lcg_normals(n * n, seed)
    a, s = math.sqrt(abar), math.sqrt(1 - abar)
    return [[a * clean[r][c] + s * eps[r * n + c] for c in range(n)] for r in range(n)]


def patch(x, y, M, cell=8, gap=1, lo=-1.2, hi=1.2):
    out = ""
    for r, row in enumerate(M):
        for c, v in enumerate(row):
            g = grey(v, lo, hi)
            out += (f'<rect x="{x + c * (cell + gap)}" y="{y + r * (cell + gap)}" width="{cell}" '
                    f'height="{cell}" rx="1" fill="rgb({g},{g},{g})"/>')
    return out


def box(x, y, w, h, title, sub="", kind="normal", title_size=11):
    styles = {"normal": ("#ffffff", INK), "focal": (ACCENT_TINT, ACCENT),
              "soft": ("rgba(45,49,66,0.05)", MUTED), "link": ("rgba(46,90,168,0.06)", LINK)}
    fill, stroke = styles[kind]
    out = rect(x, y, w, h, fill, stroke, 5, 1)
    ty = y + h / 2 + (-4 if sub else 4)
    out += text(x + w / 2, ty, title, title_size, ACCENT if kind == "focal" else INK, SANS, 600)
    if sub:
        out += mono(x + w / 2, ty + 16, sub, 8, SOFT)
    return out


# ------------------------------------------------------------------ data

SCHED = CAP["schedules"]["schedules"]
LEAK = CAP["leak"]
TRAIN = CAP.get("train")
S_B, TAU = LEAK["s_b"], LEAK["tau"]

# Part 1's 4×4 crescent patch and its noise draw, the series' running example (context.md).
X0 = [[0.95, 0.60, -0.30, -0.85], [0.80, 0.45, -0.55, -0.90],
      [0.55, 0.10, -0.70, -0.95], [0.25, -0.20, -0.85, -1.00]]
EPS = [[-0.55, 1.40, 0.45, -1.10], [0.85, -1.35, -0.25, 0.70],
       [1.25, 0.30, -0.95, 0.15], [-1.05, 0.90, 1.45, -1.10]]

# Quoted from papers, with their ledger keys.
HANG25 = [  # L46: Hang et al. 2025, Table 3 — best FID-10K over CFG 1.5/2/3, DiT-B/2, 500K iterations
    ("baseline", "Cosine schedule", 10.85),
    ("other", "EDM", 11.56), ("other", "Flow matching (OT)", 11.98),
    ("reweight", "Min-SNR-5", 9.70), ("reweight", "Soft-Min-SNR", 9.07),
    ("resample", "Shifted cosine", 11.13), ("resample", "Cauchy", 8.14),
    ("resample", "Scaled cosine", 8.04), ("resample", "Laplace", 7.96),
]
EDM2 = [  # L52: EDM2 Table 2, ImageNet-512, (Mparams, FID no guidance, FID with guidance)
    ("XS", 125, 3.53, 2.91), ("S", 280, 2.56, 2.23), ("M", 498, 2.25, 2.01),
    ("L", 777, 2.06, 1.88), ("XL", 1119, 1.96, 1.85), ("XXL", 1523, 1.91, 1.81),
]


def minus(v):
    return str(v).replace("-", "−")


def png_gray(rows):
    """A greyscale PNG from rows of 0..255 ints, stdlib only: sample tiles stay pixels, not 1,024 rects."""
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


def tile(x, y, size, M, lo=-1.6, hi=1.6):
    rows = [[grey(v, lo, hi) for v in row] for row in M]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>'
            + rect(x, y, size, size, "none", RULE_SOLID, 0, 0.8))


def legend_row(x, y, items, gap=26):
    """Inline legend: (label, colour, dash) with a short stroke sample each."""
    out = ""
    for label, colour, dash in items:
        d = ' stroke-dasharray="6,4"' if dash else ""
        out += (f'<line x1="{x}" y1="{y - 4}" x2="{x + 22}" y2="{y - 4}" stroke="{colour}" '
                f'stroke-width="2.2"{d}/>')
        out += mono(x + 28, y, label, 8, MUTED, "start")
        x += 40 + len(label) * 6.2 + gap
    return out


def normal_pdf(x, mu, sd):
    return math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def schedule_points(name):
    """(t/T, λ) pairs from the lab's capture: every 10th index plus the last; None where λ = −∞."""
    lam = SCHED[name]["logsnr_every10"]
    idx = list(range(0, 1000, 10)) + [999]
    return [((i + 1) / 1000, v) for i, v in zip(idx, lam)]


# -------------------------------------------------------------------- fig 02

def fig02():
    vw, vh = 960, 410
    a = SCHED["scaled_linear"]["sqrt_abar_T"]
    s = math.sqrt(1 - a * a)
    xT = [[a * X0[r][c] + s * EPS[r][c] for c in range(4)] for r in range(4)]
    m0 = sum(map(sum, X0)) / 16
    body = eyebrow(40, 42, "one patch at stable diffusion's last training step")
    cell, gap = 44, 3
    g1, g2, gy = 40, 300, 92
    body += subtext(g1, gy - 16, "x", "0", 13, INK, SANS, 600, "start")
    body += text(g1 + 18, gy - 16, "· part 1's 4×4 patch", 12, INK, SANS, 600, "start")
    body += valgrid(g1, gy, X0, cell, gap, -1.5, 1.5, 2, 10)
    body += subtext(g2, gy - 16, "x", "T", 13, INK, SANS, 600, "start")
    body += text(g2 + 18, gy - 16, "· the last training input", 12, INK, SANS, 600, "start")
    body += valgrid(g2, gy, xT, cell, gap, -1.5, 1.5, 2, 10)
    gw = 4 * cell + 3 * gap
    body += h_arrow(g1 + gw + 12, gy + gw / 2, g2 - 12, ACCENT, accent=True)
    body += tag((g1 + gw + g2) / 2, gy + gw / 2 - 12, f"×{a:.4f}", ACCENT, size=9)
    body += tag((g1 + gw + g2) / 2, gy + gw / 2 + 24, f"+ {s:.4f}·ε", ACCENT, size=9)
    body += mono(g1, gy + gw + 22, f"MEAN {minus(f'{m0:.4f}')}", 8, MUTED, "start")
    body += mono(g2, gy + gw + 22, f"SIGNAL IN THE MEAN {minus(f'{a * m0:.4f}')}", 8, ACCENT, "start", 500)
    body += mono(g2, gy + gw + 36, f"NOISE IN A MEAN OF 16: S.D. {s / 4:.3f}", 8, MUTED, "start")

    # right: the same signal against the noise in a mean of n values
    ax_x, ax_w, top = 560, 300, 92
    body += text(ax_x, top - 16, "The mean's leak, in noise standard deviations", 12, INK, SANS, 600, "start")
    rows = [(16, "16 · part 1's patch"), (256, "256 · 16×16"), (4096, "4,096 · 64×64"),
            (16384, "16,384 · SD's 4×64×64 latent")]
    vmax = 1.6
    one = ax_x + ax_w / vmax
    body += (f'<line x1="{one}" y1="{top + 4}" x2="{one}" y2="{top + 214}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4,4"/>')
    for k, (n, lab) in enumerate(rows):
        y = top + 18 + k * 50
        z = abs(a * m0) / (s / math.sqrt(n))
        r2 = n * a * a * S_B ** 2 / (n * a * a * S_B ** 2 + 1 - a * a)
        hot = n == 16384
        body += mono(ax_x, y - 4, lab, 8, INK if hot else MUTED, "start", 500)
        body += rect(ax_x, y + 2, ax_w, 14, "rgba(45,49,66,0.04)", "none", 2)
        body += rect(ax_x, y + 2, max(2, ax_w * min(z, vmax) / vmax), 14,
                     ACCENT if hot else "rgba(45,49,66,0.55)", "none", 2)
        lx = ax_x + ax_w * min(z, vmax) / vmax + 8
        if abs(lx + 24 - one) < 34:            # keep the value clear of the 1 s.d. rule
            lx = one + 8
        body += tag(lx, y + 13, f"{z:.2f} S.D.", INK, "start", 8)
        body += mono(ax_x + ax_w + 72, y + 13, f"{100 * r2:.1f}%", 8, ACCENT if hot else MUTED, "end", 500)
    body += tag(one, top + 228, "1 NOISE S.D.", INK, "middle", 8)
    body += mono(ax_x + ax_w + 72, top + 6, "R² BRIGHTNESS", 7, SOFT, "end")
    body += footnote(vh - 58, f"Stable Diffusion's scaled-linear schedule ends with √ᾱ = {a:.6f} at t = T: the last "
                              f"input keeps {100 * a:.1f}% of the image's amplitude.", 40)
    body += footnote(vh - 42, "Averaging n values shrinks the noise in their mean by √n and keeps the signal.", 40)
    body += footnote(vh - 26, "R²: the brightness variance a network could read from the mean, if brightness varies "
                              "with s.d. 0.3 (a model input).", 40)
    emit(2, "what-survives-the-last-step", "What survives Stable Diffusion's last step",
         "The same 6.8% leak, read through averages of different sizes",
         body, "Part 1's 4×4 patch at Stable Diffusion's last step beside bars of the mean's leak in noise "
               "standard deviations for 16, 256, 4,096 and 16,384 values, rising from 0.04 to 1.42", vw, vh)


# -------------------------------------------------------------------- fig 03

def fig03():
    vw, vh = 960, 520
    ax = Axes(96, 64, 640, 360, (0, 1), (-21, 12))
    body = eyebrow(40, 36, "log-snr at each of 1,000 training steps, four schedules")
    body += ax.frame([(v, f"{v:g}") for v in (0, 0.25, 0.5, 0.75, 1)],
                     [(v, minus(v)) for v in (-20, -15, -10, -5, 0, 5, 10)],
                     "FRACTION OF TRAINING STEPS  t / T", "LOG-SNR  λ")
    zy = ax.Y(0)
    body += (f'<line x1="{ax.x}" y1="{zy}" x2="{ax.x + ax.w}" y2="{zy}" stroke="{INK}" '
             f'stroke-width="0.8" stroke-dasharray="3,4"/>')
    body += mono(ax.x + 8, zy - 6, "SNR = 1", 8, INK, "start", 500)
    series = [("linear", "DDPM linear", BLUE, False), ("cosine", "iDDPM cosine", SAGE, False),
              ("scaled_linear", "Stable Diffusion", INK, False),
              ("scaled_linear_zero_snr", "Stable Diffusion, rescaled", ACCENT, True)]
    for key, lab, colour, dash in series:
        pts = [(u, v) for u, v in schedule_points(key) if v is not None]
        body += ax.path(pts, colour, 2.2 if key == "scaled_linear" else 1.8, dash)
    # end values, read from the capture
    ends = [("scaled_linear", INK, "Stable Diffusion"), ("linear", BLUE, "DDPM linear"),
            ("cosine", SAGE, "iDDPM cosine")]
    for key, colour, lab in ends:
        v = SCHED[key]["logsnr_T"]
        body += ax.dot(1.0, v, 3.5, colour)
        body += mono(ax.x + ax.w + 14, ax.Y(v) + 3, f"{minus(f'{v:.1f}')}  {lab}", 8, colour, "start", 500)
    last = [p for p in schedule_points("scaled_linear_zero_snr") if p[1] is not None][-1]
    body += path_line([(ax.X(last[0]), ax.Y(last[1])), (ax.X(1.0), ax.y + ax.h - 4)], ACCENT, 1.6, True, True)
    body += mono(ax.x + ax.w + 14, ax.Y(-15) + 3, "−∞  rescaled, at t = T", 8, ACCENT, "start", 500)
    body += path_line([(ax.x + ax.w + 10, ax.Y(-15)), (ax.X(1.0) + 3, ax.Y(-15))], ACCENT, 1.0, False, False, False)
    for key, lab, colour in (("linear", "linear", BLUE), ("scaled_linear", "SD", INK), ("cosine", "cosine", SAGE)):
        f = SCHED[key]["snr1_crossing_frac"]
        body += ax.dot(f, 0, 3, colour, hollow=True)
    body += legend_row(ax.x, vh - 40, [(lab, colour, dash) for _, lab, colour, dash in series])
    emit(3, "four-schedules-in-log-snr", "Four schedules in log-SNR",
         "Computed from the published formulas by the lab", body,
         "Log-SNR against fraction of training steps for the linear, cosine and Stable Diffusion schedules and the "
         "zero-terminal-SNR rescale, with each end value marked", vw, vh)


# -------------------------------------------------------------------- fig 04

def fig04():
    vw, vh = 960, 500
    ax = Axes(96, 64, 760, 310, (-12, 12), (0, 0.24))
    body = eyebrow(40, 36, "where training draws its noise levels — density over log-snr")
    body += ax.frame([(v, minus(v)) for v in (-12, -8, -4, 0, 4, 8, 12)],
                     [(v, f"{v:.2f}") for v in (0, 0.06, 0.12, 0.18, 0.24)],
                     "LOG-SNR  λ   (← NOISIER        CLEANER →)", "DENSITY")
    body += (f'<line x1="{ax.X(0)}" y1="{ax.y}" x2="{ax.X(0)}" y2="{ax.y + ax.h}" stroke="{INK}" '
             f'stroke-width="0.8" stroke-dasharray="3,4"/>')
    first = {}
    for key, colour in (("linear", BLUE), ("cosine", SAGE), ("scaled_linear", INK)):
        pts = schedule_points(key)
        dens = []
        for (u1, l1), (u2, l2) in zip(pts, pts[1:]):
            if l1 is None or l2 is None or l1 == l2:
                continue
            dens.append(((l1 + l2) / 2, (u2 - u1) / abs(l1 - l2)))
        dens.sort()
        first[key] = dens[0]
        body += ax.path(dens, colour, 2.2 if key == "scaled_linear" else 1.8)
    xs = [-12 + 24 * i / 240 for i in range(241)]
    body += ax.path([(x, normal_pdf(x, 2.4, 2.4)) for x in xs], MUSTARD, 2.0)
    body += ax.path([(x, normal_pdf(x, 0.0, 2.0)) for x in xs], ACCENT, 2.2)
    body += ax.path([(x, normal_pdf(x, -2 * math.log(3), 2.0)) for x in xs], ACCENT, 1.6, True)
    body += tag(ax.X(2.4) + 74, ax.Y(normal_pdf(2.4, 2.4, 2.4)) - 6, "EDM  N(2.4, 2.4²)", MUSTARD)
    body += tag(ax.X(0) + 52, ax.Y(normal_pdf(0, 0, 2)) - 10, "SD3  N(0, 2²)", ACCENT)
    body += tag(ax.X(-2 * math.log(3)) - 96, ax.Y(normal_pdf(0, 0, 2)) + 4, "SD3 at 1024², shift 3", ACCENT)
    lx, ly = first["scaled_linear"]
    body += ax.dot(lx, ly, 3.5, INK)
    body += tag(ax.X(lx) - 8, ax.Y(ly) - 10, f"SD stops at {minus(f'{SCHED['scaled_linear']['logsnr_T']:.1f}')}", INK, "end", 8)
    body += legend_row(ax.x, vh - 70, [("DDPM linear, uniform t", BLUE, False), ("cosine, uniform t", SAGE, False),
                                        ("Stable Diffusion, uniform t", INK, False)], 22)
    body += legend_row(ax.x, vh - 52, [("EDM log-normal", MUSTARD, False), ("SD3 logit-normal", ACCENT, False),
                                        ("SD3, 1024² shift", ACCENT, True)], 22)
    body += footnote(vh - 30, "Uniform-t curves from the lab's schedules. EDM: ln σ ~ N(−1.2, 1.2²), λ = −2 ln σ. "
                              "SD3: logit(t) ~ N(0, 1), λ = −2·logit(t).", 40)
    body += footnote(vh - 16, "The cosine schedule's density continues to −19.8 off the left edge.", 40)
    emit(4, "where-training-spends-its-samples", "Where training spends its samples",
         "Density of training noise levels over log-SNR, computed from each recipe's definition", body,
         "Densities over log-SNR: uniform-timestep sampling under the linear, cosine and Stable Diffusion schedules, "
         "EDM's log-normal centred at 2.4, and SD3's logit-normal centred at 0 with its 1024-pixel shift to −2.2", vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    vw, vh = 960, 500
    ax = Axes(96, 64, 800, 340, (0, 1), (-12, 16))

    def cos_lam(u):
        return -2 * math.log(math.tan(math.pi * u / 2))
    us = [0.02 + 0.96 * i / 240 for i in range(241)]
    body = eyebrow(40, 36, "one cosine schedule, read at three scales, and the shift that undoes it")
    body += ax.frame([(v, f"{v:g}") for v in (0, 0.25, 0.5, 0.75, 1)],
                     [(v, minus(v)) for v in (-12, -8, -4, 0, 4, 8, 12, 16)],
                     "FRACTION OF TRAINING STEPS  t / T", "LOG-SNR  λ")
    zy = ax.Y(0)
    body += (f'<line x1="{ax.x}" y1="{zy}" x2="{ax.x + ax.w}" y2="{zy}" stroke="{INK}" '
             f'stroke-width="0.8" stroke-dasharray="3,4"/>')
    s4, s16 = 2 * math.log(4), 2 * math.log(16)
    body += ax.path([(u, cos_lam(u) + s16) for u in us], SOFT, 1.6, True)
    body += ax.path([(u, cos_lam(u) + s4) for u in us], MUTED, 1.8, True)
    body += ax.path([(u, cos_lam(u)) for u in us], INK, 2.4)
    body += ax.path([(u, cos_lam(u) - s4) for u in us], ACCENT, 2.2)
    u0 = 0.62
    body += tag(ax.X(u0) + 6, ax.Y(cos_lam(u0) + s16) - 8, f"mean of 16×16 blocks  +{s16:.1f}", SOFT, "start")
    body += tag(ax.X(u0) + 6, ax.Y(cos_lam(u0) + s4) - 8, f"mean of 4×4 blocks  +{s4:.1f}", MUTED, "start")
    body += tag(ax.X(u0) + 6, ax.Y(cos_lam(u0)) - 8, "each pixel", INK, "start")
    body += tag(ax.X(u0) + 6, ax.Y(cos_lam(u0) - s4) + 18, f"shifted for 4× the side  −{s4:.1f}", ACCENT, "start")
    body += verdict(ax.X(0.04), ax.Y(-8.6), 318, "SHIFT −2.8 + POOL 4×4 = THE BLACK CURVE AGAIN")
    body += footnote(vh - 40, "Averaging an s×s window multiplies SNR by s², so log-SNR rises by 2 ln s (simple diffusion, eq. 4). "
                              "simple diffusion shifts by 2 ln(d/64); SD3 at 1024² by 2 ln 3 = 2.2.", 40)
    body += footnote(vh - 24, "Cosine schedule λ = −2 ln tan(πt/2), as simple diffusion writes it; computed, not measured.", 40)
    emit(5, "resolution-shifts-the-schedule", "Resolution shifts the schedule",
         "The same per-pixel schedule is easier for coarse structure", body,
         "Log-SNR against fraction of steps for the cosine schedule at the pixel level and for the means of 4×4 and "
         "16×16 blocks, which sit 2.8 and 5.5 higher, beside the same schedule shifted down for a four-times-larger image",
         vw, vh)


# -------------------------------------------------------------------- fig 06

def fig06():
    vw, vh = 960, 560
    r = LEAK["by_resolution"]["128"]
    rows = [("The data", r["data_previews_32"], r["data_hist"], 20000, 1.0, INK),
            ("Stable Diffusion's schedule", r["variants"]["sd_trailing_noise"]["previews_32"],
             r["variants"]["sd_trailing_noise"]["hist"], LEAK["N"],
             r["variants"]["sd_trailing_noise"]["std_ratio"], INK),
            ("Rescaled to zero terminal SNR", r["variants"]["zero_snr_trailing_noise"]["previews_32"],
             r["variants"]["zero_snr_trailing_noise"]["hist"], LEAK["N"],
             r["variants"]["zero_snr_trailing_noise"]["std_ratio"], ACCENT)]
    edges = r["variants"]["sd_trailing_noise"]["hist_edges"]
    bw = edges[1] - edges[0]
    data_density = [c / (20000 * bw) for c in r["data_hist"]]
    body = eyebrow(40, 36, "exact denoiser · 50-step ddim · 128×128 = 16,384 pixels · same starting noise for both schedules")
    size, gap, x0, y0, rowh = 72, 10, 40, 74, 150
    hx, hw = 600, 320
    hax_top = 0
    for k, (lab, prev, hist, n, ratio, colour) in enumerate(rows):
        y = y0 + k * rowh
        body += text(x0, y - 10, lab, 12, colour if k else INK, SANS, 600, "start")
        for j, M in enumerate(prev[:6]):
            body += tile(x0 + j * (size + gap), y + 6, size, M)
        ax = Axes(hx, y + 2, hw, size + 6, (-1.2, 1.2), (0, 4.2))
        body += ax.frame([(v, minus(v)) for v in (-1.2, -0.6, 0, 0.6, 1.2)] if k == 2 else [],
                         [], "" if k < 2 else "IMAGE BRIGHTNESS (MEAN PIXEL)", "", grid=False)
        dens = [c / (n * bw) for c in hist]
        # the data's histogram as a light reference in every row
        pts = []
        for i, d in enumerate(data_density):
            pts += [(edges[i], d), (edges[i + 1], d)]
        body += ax.path(pts, SOFT, 1.2, opacity=0.9)
        if k:
            pts = []
            for i, d in enumerate(dens):
                pts += [(edges[i], d), (edges[i + 1], d)]
            body += ax.path(pts, colour, 2.0)
        spread = "spread 1.00 (reference)" if k == 0 else f"spread {ratio:.3f} of the data's"
        body += mono(hx + hw, y - 10, spread.upper(), 8, colour if k else MUTED, "end", 500)
    body += footnote(vh - 40, "Grey outline in every histogram: the data's brightness distribution. Tiles share one grey "
                              "scale (high value = bright) and show 32×32 block means of the 128×128 samples.", 40)
    body += footnote(vh - 24, "Measured by the lab: 20,000 data images, 4,000 samples per schedule.", 40)
    emit(6, "the-leak-in-samples", "The leak in samples",
         "Same shapes, lost brightness: a perfect denoiser under Stable Diffusion's schedule", body,
         "Six sample images each from the data, from Stable Diffusion's schedule and from the zero-terminal-SNR "
         "schedule at 16,384 pixels, with brightness histograms showing the flawed samples bunched in the middle", vw, vh)


# -------------------------------------------------------------------- fig 07

def fig07():
    vw, vh = 960, 500
    by = LEAK["by_resolution"]
    body = eyebrow(40, 36, "fraction of the data's brightness spread that samples keep · exact denoiser")
    # left: against pixel count
    ax = Axes(96, 70, 360, 300, (math.log10(10), math.log10(30000)), (0, 1.1))
    ns = [16, 256, 4096, 16384]
    body += ax.frame([(math.log10(n), f"{n:,}") for n in ns],
                     [(v, f"{v:.1f}") for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)],
                     "VALUES PER IMAGE  n  (LOG)", "SPREAD KEPT")
    abT = SCHED["scaled_linear"]["sqrt_abar_T"] ** 2
    curve_pts = []
    for i in range(121):
        n = 10 ** (1 + 3.33 * i / 120)
        curve_pts.append((math.log10(n), 1 / math.sqrt(1 - abT + abT * (n * S_B ** 2 + TAU ** 2))))
    body += ax.path(curve_pts, INK, 1.6, True)
    for key, colour, hollow in (("sd_trailing_noise", INK, False), ("sd_trailing_oracle", SAGE, False),
                                ("zero_snr_trailing_noise", ACCENT, False), ("sd_leading_noise", MUTED, True)):
        pts = [(math.log10(by[str(r)]["n"]), by[str(r)]["variants"][key]["std_ratio"]) for r in (4, 16, 64, 128)]
        body += ax.path(pts, colour, 1.2, opacity=0.6)
        for p in pts:
            body += ax.dot(p[0], p[1], 4, colour, hollow)
    v = by["128"]["variants"]
    lx = ax.X(math.log10(16384)) - 14
    body += tag(lx, ax.Y(v["sd_trailing_noise"]["std_ratio"]) - 8,
                f"trailing {v['sd_trailing_noise']['std_ratio']:.3f}", INK, "end", 8)
    body += tag(lx, ax.Y(v["sd_leading_noise"]["std_ratio"]) + 16,
                f"leading {v['sd_leading_noise']['std_ratio']:.3f}", MUTED, "end", 8)
    body += tag(lx, ax.Y(v["zero_snr_trailing_noise"]["std_ratio"]) + 16,
                f"{v['zero_snr_trailing_noise']['std_ratio']:.3f}", ACCENT, "end", 8)
    body += tag(lx, ax.Y(v["sd_trailing_oracle"]["std_ratio"]) - 10,
                f"{v['sd_trailing_oracle']['std_ratio']:.3f}", SAGE, "end", 8)
    # right: against sampling steps at n = 16,384
    rows = LEAK["steps_sweep"]["rows"]
    bx = Axes(560, 70, 330, 300, (math.log2(20), math.log2(250)), (0, 1.1))
    body += bx.frame([(math.log2(r["steps"]), str(r["steps"])) for r in rows],
                     [(v, f"{v:.1f}") for v in (0, 0.2, 0.4, 0.6, 0.8, 1.0)],
                     "SAMPLING STEPS  (n = 16,384, LOG)", "")
    pred = 1 / math.sqrt(1 - abT + abT * (16384 * S_B ** 2 + TAU ** 2))
    body += bx.path([(math.log2(20), pred), (math.log2(250), pred)], INK, 1.2, True)
    body += bx.path([(math.log2(20), 1.0), (math.log2(250), 1.0)], SOFT, 1.0, True)
    for key, colour in (("sd_trailing_noise", INK), ("zero_snr_trailing_noise", ACCENT)):
        pts = [(math.log2(r["steps"]), r[key]) for r in rows]
        body += bx.path(pts, colour, 1.6)
        for p in pts:
            body += bx.dot(p[0], p[1], 4, colour)
        for (px, py), r in zip(pts, rows):
            body += tag(bx.X(px), bx.Y(py) + (20 if key == "sd_trailing_noise" else -10), f"{py:.3f}", colour, size=8)
    body += mono(bx.x + bx.w, bx.Y(pred) - 22, f"CLOSED FORM {pred:.3f}", 8, INK, "end", 500)
    body += mono(bx.x + 6, bx.Y(1.0) - 8, "THE DATA", 8, SOFT, "start", 500)
    body += legend_row(96, vh - 60, [("SD schedule, trailing", INK, False), ("closed form", INK, True),
                                     ("oracle start", SAGE, False), ("zero terminal SNR", ACCENT, False),
                                     ("SD schedule, leading", MUTED, False)], 14)
    body += footnote(vh - 34, f"Measured by the lab, {LEAK['N']:,} samples per point (1,000 in the step sweep); "
                              "50-step DDIM unless the axis says otherwise.", 40)
    body += footnote(vh - 18, "Oracle: start the same sampler from the true noisy input at t = T, signal included.", 40)
    emit(7, "leak-vs-pixels-and-steps", "The leak against pixels and steps",
         "A training-sampling mismatch is a fixed point, not a discretisation error", body,
         "Two measured panels: brightness spread kept by samples against pixel count from 16 to 16,384, and against "
         "sampling steps from 25 to 200, where the flawed schedule stays at 0.36 and the rescaled one rises toward 1",
         vw, vh)


# -------------------------------------------------------------------- fig 09

def fig09():
    vw, vh = 960, 480
    lams = [-10 + 20 * i / 200 for i in range(201)]

    def sig(z):
        return 1 / (1 + math.exp(-z))
    body = eyebrow(40, 36, "how an output error of δ reaches the two estimates a sampler uses")
    panels = [(96, "error in the clean-image estimate x₀ / δ",
               [("ε output", INK, lambda l: math.exp(-l / 2)), ("x₀ output", BLUE, lambda l: 1.0),
                ("v output", ACCENT, lambda l: math.sqrt(1 - sig(l)))]),
              (548, "error in the noise estimate ε / δ",
               [("ε output", INK, lambda l: 1.0), ("x₀ output", BLUE, lambda l: math.exp(l / 2)),
                ("v output", ACCENT, lambda l: math.sqrt(sig(l)))])]
    for px, title, curves in panels:
        ax = Axes(px, 84, 340, 290, (-10, 10), (math.log10(0.005), math.log10(200)), logy=True)
        body += text(px, 70, title, 12, INK, SANS, 600, "start")
        body += ax.frame([(v, minus(v)) for v in (-10, -5, 0, 5, 10)],
                         [(v, lab) for v, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100"))],
                         "LOG-SNR  λ   (← NOISIER     CLEANER →)", "AMPLIFICATION")
        for lab, colour, fn in curves:
            body += ax.path([(l, fn(l)) for l in lams], colour, 2.2 if colour == ACCENT else 1.8)
    ax = Axes(96, 84, 340, 290, (-10, 10), (math.log10(0.005), math.log10(200)), logy=True)
    body += ax.dot(-9, math.exp(4.5), 4, INK)
    body += tag(ax.X(-9) + 8, ax.Y(math.exp(4.5)) + 4, "×90 at λ = −9", INK, "start")
    sd = SCHED["scaled_linear"]["logsnr_T"]
    body += ax.dot(sd, math.exp(-sd / 2), 4, INK, hollow=True)
    body += tag(ax.X(sd) + 8, ax.Y(math.exp(-sd / 2)) + 4, f"×{math.exp(-sd / 2):.1f} at SD's last step", INK, "start")
    body += legend_row(96, vh - 46, [("network outputs ε", INK, False), ("network outputs x₀", BLUE, False),
                                     ("network outputs v", ACCENT, False)])
    body += footnote(vh - 22, "Computed from xₜ = √ᾱ·x₀ + √(1−ᾱ)·ε and v = √ᾱ·ε − √(1−ᾱ)·x₀; the math section derives each curve.", 40)
    emit(9, "error-amplification-by-target", "Error amplification by target",
         "Same minimiser, different conditioning", body,
         "Amplification of an output error into the clean-image estimate and the noise estimate for epsilon, x0 and v "
         "prediction against log-SNR: epsilon explodes at high noise, x0 at low noise, v stays at or below one", vw, vh)


# -------------------------------------------------------------------- fig 12

def fig12():
    vw, vh = 960, 470
    body = eyebrow(40, 36, "hang et al. 2025 · dit-b/2 · imagenet 256 latents · 500k iterations · best fid-10k over cfg 1.5–3")
    groups = {"baseline": ("baseline", INK), "other": ("other formulations", MUTED),
              "reweight": ("reweight the loss", BLUE), "resample": ("resample log-SNR", ACCENT)}
    order = [("baseline", "Cosine schedule"), ("other", "EDM"), ("other", "Flow matching (OT)"),
             ("reweight", "Min-SNR-5"), ("reweight", "Soft-Min-SNR"),
             ("resample", "Shifted cosine"), ("resample", "Cauchy"), ("resample", "Scaled cosine"),
             ("resample", "Laplace")]
    val = {(g, n): v for g, n, v in HANG25}
    x0, y0, w, rh = 250, 70, 560, 36
    vmax = 13.0
    base = val[("baseline", "Cosine schedule")]
    for i, (g, n) in enumerate(order):
        y = y0 + i * rh
        v = val[(g, n)]
        colour = groups[g][1]
        body += mono(x0 - 14, y + 13, n, 9, INK, "end", 500)
        body += rect(x0, y + 2, w * v / vmax, 16, colour, "none", 2)
        body += mono(x0 + w * v / vmax + 8, y + 14, f"{v:.2f}", 9, INK, "start", 500)
        if i == 0 or order[i - 1][0] != g:
            body += mono(40, y + 13, groups[g][0].upper(), 8, colour, "start", 500)
    bx = x0 + w * base / vmax
    body += (f'<line x1="{bx}" y1="{y0 - 6}" x2="{bx}" y2="{y0 + len(order) * rh}" stroke="{INK}" '
             f'stroke-width="1" stroke-dasharray="4,4"/>')
    body += mono(bx, y0 + len(order) * rh + 14, f"BASELINE {base:.2f}", 8, INK, "middle", 500)
    for v in (0, 4, 8, 12):
        body += mono(x0 + w * v / vmax, y0 - 10, str(v), 7, SOFT)
    body += footnote(vh - 40, "Quoted from Hang, Gu, Geng & Guo, ICCV 2025, Table 3; lower is better; zero baseline. "
                              "Compare within this chart only.", 40)
    body += footnote(vh - 24, "In expectation, reweighting a noise level and sampling it more often spend the same budget.", 40)
    emit(12, "reweight-or-resample", "Reweight or resample",
         "Spending the same training budget on noise levels two ways", body,
         "Bar chart of best FID-10K after 500K iterations on ImageNet 256 with DiT-B/2 for the cosine baseline, EDM, "
         "flow matching, Min-SNR, Soft-Min-SNR and the Laplace, Cauchy, scaled-cosine and shifted-cosine schedules", vw, vh)

# -------------------------------------------------------------------- training helpers

BLOW = 10.0   # a sample distance above this means the sampler left the data's scale ("blew up")


def runs(exp, **kw):
    return [r for r in TRAIN["runs"] if r["config"]["exp"] == exp
            and all(r["config"][k] == v for k, v in kw.items())]


def mean_curve(rs, ck, model="raw"):
    n = len(TRAIN["lam_grid"])
    return [sum(r["checkpoints"][str(ck)][model]["excess"][i] for r in rs) / len(rs) for i in range(n)]


def swd_summary(rs, ck, model="raw"):
    vals = [r["checkpoints"][str(ck)][model]["swd"] for r in rs]
    bad = sum(1 for v in vals if v is None or v > BLOW)
    ok = sorted(v for v in vals if v is not None and v <= BLOW)
    if not ok:
        return None, bad, len(vals)
    m = len(ok) // 2
    med = ok[m] if len(ok) % 2 else (ok[m - 1] + ok[m]) / 2
    return med, bad, len(vals)


def power_gamma(sigma_rel):
    """EDM2's sigma_rel = sqrt(g+1) / ((g+2) sqrt(g+3)), solved for the exponent g by bisection."""
    lo, hi = 0.0, 1e4
    for _ in range(200):
        g = 0.5 * (lo + hi)
        if math.sqrt(g + 1) / ((g + 2) * math.sqrt(g + 3)) > sigma_rel:
            lo = g
        else:
            hi = g
    return 0.5 * (lo + hi)


def excess_axes(px, py, w, h, ylo=1e-5, yhi=10):
    ax = Axes(px, py, w, h, (-9, 9), (math.log10(ylo), math.log10(yhi)), logy=True)
    ticks = [(10.0 ** e, f"{10.0 ** e:g}" if e >= -3 else f"1e{e}")
             for e in range(int(round(math.log10(ylo))), int(round(math.log10(yhi))) + 1)]
    frame = ax.frame([(v, minus(v)) for v in (-9, -6, -3, 0, 3, 6, 9)], ticks,
                     "LOG-SNR  λ   (← NOISIER     CLEANER →)", "EXCESS ERROR")
    return ax, frame


def mmse_line(ax):
    lams, mm = TRAIN["lam_grid"], TRAIN["runs"][0]["mmse_x0"]
    return ax.path(list(zip(lams, mm)), SOFT, 1.4, True)


# -------------------------------------------------------------------- fig 11

WEIGHT_STYLE = [("const", "constant", BLUE), ("maxsnr1", "truncated SNR, max(SNR, 1)", SAGE),
                ("minsnr5", "Min-SNR-5, min(SNR, 5)", ACCENT), ("snr", "SNR (the ε-loss)", INK)]


def fig11():
    vw, vh = 960, 540
    lams = TRAIN["lam_grid"]
    body = eyebrow(40, 36, "x₀-predicting mlp, width 128, 40,000 steps, three seeds · error against the exact denoiser")
    ax, frame = excess_axes(96, 78, 500, 330, 1e-4, 10)
    body += text(96, 66, "Excess error per noise level (raw weights, mean of 3 seeds)", 12, INK, SANS, 600, "start")
    body += frame + mmse_line(ax)
    for key, lab, colour in WEIGHT_STYLE:
        rs = runs("weighting", weighting=key)
        body += ax.path(list(zip(lams, mean_curve(rs, rs[0]["config"]["steps"]))), colour,
                        2.4 if key == "minsnr5" else 1.8)
    body += tag(ax.X(-2.2), ax.Y(TRAIN["runs"][0]["mmse_x0"][9]) - 10, "the exact denoiser's own error", SOFT, "start", 8)
    snr = mean_curve(runs("weighting", weighting="snr"), 40000)
    body += tag(ax.X(-9) + 10, ax.Y(snr[0]) - 6, f"SNR: {snr[0]:.2f}, worse than the ideal", INK, "start", 8)
    # right: what the samples look like at the end, with the EMA weights practice samples from
    bx0, by0 = 660, 100
    body += text(bx0, 66, "Samples at 40,000 steps", 12, INK, SANS, 600, "start")
    body += mono(bx0, 84, "MEDIAN SLICED DISTANCE, POWER EMA σ_REL 0.10", 7, SOFT, "start", 500)
    w, vmax = 240, 0.2
    floor = TRAIN["floors"]["swd"]
    fx = bx0 + w * floor / vmax
    body += (f'<line x1="{fx}" y1="{by0 + 6}" x2="{fx}" y2="{by0 + 4 * 64 + 34}" stroke="{SOFT}" '
             f'stroke-width="1" stroke-dasharray="4,4"/>')
    body += mono(fx, by0 + 4 * 64 + 48, f"TWO DATA DRAWS {floor:.3f}", 7, SOFT, "middle", 500)
    for i, (key, lab, colour) in enumerate(WEIGHT_STYLE):
        y = by0 + 20 + i * 64
        med, bad, n = swd_summary(runs("weighting", weighting=key), 40000, "power_0.1")
        body += tag(bx0, y, lab, INK, "start", 8)
        if med is None:
            body += rect(bx0, y + 8, w, 18, "rgba(45,49,66,0.06)", INK, 2, 1, "4,3")
            body += tag(bx0 + w / 2, y + 21, f"SAMPLER BLEW UP · {bad} OF {n}", INK, "middle", 8)
        else:
            body += rect(bx0, y + 8, w * med / vmax, 18, colour, "none", 2)
            body += mono(bx0 + w * med / vmax + 6, y + 21, f"{med:.3f}", 8, INK, "start", 500)
    body += legend_row(96, vh - 64, [(lab, colour, False) for _, lab, colour in WEIGHT_STYLE[:2]]
                       + [("exact denoiser's error", SOFT, True)], 18)
    body += legend_row(96, vh - 46, [(lab, colour, False) for _, lab, colour in WEIGHT_STYLE[2:]], 18)
    body += footnote(vh - 22, "Measured by the lab. Each weighting is a weight on the x₀ error; SNR weighting equals the "
                              "plain ε-loss. A sample distance above 10 counts as blown up.", 40)
    emit(11, "where-each-weighting-puts-the-error", "Where each weighting puts the error",
         "One network, four ways to share its capacity across noise levels", body,
         "Measured excess error by log-SNR for constant, SNR, truncated-SNR and Min-SNR-5 weighting of an "
         "x0-predicting network, beside median sample distance", vw, vh)


# -------------------------------------------------------------------- fig 13

EMA_STYLE = [("raw", "raw weights", INK, False), ("ema_0.99", "EMA 0.99", SOFT, False),
             ("ema_0.999", "EMA 0.999", BLUE, False), ("ema_0.9999", "EMA 0.9999", MUSTARD, False),
             ("power_0.05", "power σ_rel 0.05", ACCENT, False), ("power_0.1", "power σ_rel 0.10", ACCENT, True),
             ("power_0.2", "power σ_rel 0.20", SAGE, False)]


def fig13():
    vw, vh = 960, 560
    body = eyebrow(40, 36, "weight averages · computed profiles, and measured samples from nine training runs")
    # left: the weight each average gives to each past step, at the end of a 40,000-step run
    t_end = 40000
    ax = Axes(96, 92, 340, 300, (0, t_end), (math.log10(1e-7), math.log10(3e-3)), logy=True)
    body += text(96, 66, "Weight on each past step, end of a 40,000-step run", 12, INK, SANS, 600, "start")
    body += ax.frame([(v, f"{v // 1000}k") for v in (0, 10000, 20000, 30000, 40000)],
                     [(10.0 ** e, f"10{str(e).translate(str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'))}") for e in range(-7, -2)],
                     "TRAINING STEP", "WEIGHT PER STEP")
    taus = [t_end * i / 400 for i in range(1, 401)]
    for b, colour in ((0.999, BLUE), (0.9999, MUSTARD)):
        body += ax.path([(tau, (1 - b) * b ** (t_end - tau)) for tau in taus], colour, 1.8)
    for sr, colour, dash in ((0.05, ACCENT, False), (0.10, ACCENT, True), (0.20, SAGE, False)):
        g = power_gamma(sr)
        body += ax.path([(tau, (g + 1) / t_end * (tau / t_end) ** g) for tau in taus], colour, 1.8, dash)
    init = 0.9999 ** t_end
    body += ax.dot(0, (1 - 0.9999) * 0.9999 ** t_end, 4, MUSTARD)
    body += tag(ax.X(0) + 10, ax.Y((1 - 0.9999) * 0.9999 ** t_end) - 8,
                f"+ {100 * init:.1f}% on the random start", MUSTARD, "start", 8)
    # right: measured median sample distance by average, at four checkpoints
    rs = [r for r in runs("weighting") if r["config"]["weighting"] != "snr"]
    cks = sorted(int(c) for c in rs[0]["checkpoints"])
    bx = Axes(560, 92, 280, 300, (math.log2(4000), math.log2(50000)), (math.log10(0.06), math.log10(1.2)), logy=True)
    body += text(560, 66, "Measured sample distance (median of 9 runs)", 12, INK, SANS, 600, "start")
    body += bx.frame([(math.log2(c), f"{c // 1000}k") for c in cks],
                     [(v, f"{v:g}") for v in (0.1, 0.2, 0.5, 1.0)], "TRAINING STEPS (LOG)", "SLICED DISTANCE")
    floor = TRAIN["floors"]["swd"]
    body += bx.path([(math.log2(4000), floor), (math.log2(50000), floor)], SOFT, 1.0, True)
    body += mono(bx.x + 8, bx.Y(floor) - 6, f"TWO DATA DRAWS {floor:.3f}", 7, SOFT, "start", 500)
    blown = {}
    for key, lab, colour, dash in EMA_STYLE:
        pts = []
        for c in cks:
            med, bad, n = swd_summary(rs, c, key)
            blown[key] = blown.get(key, 0) + bad
            if med is not None:
                pts.append((math.log2(c), med))
        body += bx.path(pts, colour, 2.2 if key in ("raw", "ema_0.9999") else 1.6, dash)
        for p in pts:
            body += bx.dot(p[0], p[1], 3, colour)
    last = cks[-1]
    ends = {key: swd_summary(rs, last, key)[0] for key, _, _, _ in EMA_STYLE}
    for key, lab, colour in (("ema_0.9999", "EMA 0.9999", MUSTARD), ("power_0.2", "power 0.20", SAGE),
                             ("raw", "raw", INK)):
        body += tag(bx.X(math.log2(last)) + 10, bx.Y(ends[key]) + 4, lab, colour, "start", 8)
    cluster = [ends[k] for k in ("ema_0.99", "ema_0.999", "power_0.05", "power_0.1")]
    body += tag(bx.X(math.log2(last)) + 10, bx.Y(sum(cluster) / 4) + 18,
                f"four others {min(cluster):.3f}–{max(cluster):.3f}", BLUE, "start", 8)
    body += legend_row(96, vh - 82, [(lab, colour, dash) for _, lab, colour, dash in EMA_STYLE[:4]], 16)
    body += legend_row(96, vh - 64, [(lab, colour, dash) for _, lab, colour, dash in EMA_STYLE[4:]], 16)
    total = len(rs) * len(cks)
    body += footnote(vh - 40, "Left: computed from each update rule. Right: measured by the lab on the constant, truncated-SNR "
                              "and Min-SNR runs (3 seeds each).", 40)
    body += footnote(vh - 24, "Sampler blow-ups out of " + str(total) + " evaluations: " + ", ".join(
        f"{lab} {blown[key]}" for key, lab, _, _ in EMA_STYLE) + ".", 40)
    emit(13, "ema-profiles-and-lengths", "EMA profiles and lengths",
         "What each average remembers, and what it samples like", body,
         "EMA weight on past steps for exponential and power-function averages, and measured sample distance by "
         "EMA length at four checkpoints", vw, vh)


# -------------------------------------------------------------------- fig 10

TARGET_STYLE = [("eps", "ε output", INK), ("x0", "x₀ output", BLUE), ("v", "v output", ACCENT)]


def fig10():
    vw, vh = 960, 560
    lams = TRAIN["lam_grid"]
    body = eyebrow(40, 36, "one objective (min-snr-5), three outputs · mlp on 8×8 = 64 values · 20,000 steps, three seeds")
    panels = [(256, 96, "Width 256, wider than the 64-value data"), (32, 548, "Width 32, narrower than the data")]
    for width, px, title in panels:
        ax, frame = excess_axes(px, 92, 330, 290, 1e-5, 1e4)
        body += text(px, 70, title, 12, INK, SANS, 600, "start")
        body += frame + mmse_line(ax)
        steps = runs("target", width=width)[0]["config"]["steps"]
        for key, lab, colour in TARGET_STYLE:
            rs = runs("target", target=key, width=width)
            body += ax.path(list(zip(lams, mean_curve(rs, steps))), colour, 2.4 if key == "v" else 1.8)
        y = 92 + 290 + 62
        body += mono(px, y, "SAMPLES · MEDIAN DISTANCE, POWER EMA", 7, SOFT, "start", 500)
        for j, (key, lab, colour) in enumerate(TARGET_STYLE):
            med, bad, n = swd_summary(runs("target", target=key, width=width), steps, "power_0.1")
            val = "blew up" if med is None else f"{med:.3f}"
            note = f" · {bad} of {n} blew up" if bad and med is not None else ""
            body += mono(px + j * 116, y + 18, f"{lab.split()[0]} {val}{note}", 8, colour, "start", 600)
    w32 = mean_curve(runs("target", target="eps", width=32), 20000)
    ax32 = Axes(548, 92, 330, 290, (-9, 9), (math.log10(1e-5), math.log10(1e4)), logy=True)
    body += tag(ax32.X(-9) + 10, ax32.Y(w32[0]) + 4, f"ε: {w32[0]:,.0f} at λ = −9", INK, "start", 8)
    w256 = mean_curve(runs("target", target="eps", width=256), 20000)
    ax256 = Axes(96, 92, 330, 290, (-9, 9), (math.log10(1e-5), math.log10(1e4)), logy=True)
    body += tag(ax256.X(-9) + 10, ax256.Y(w256[0]) - 8, f"ε: {w256[0]:.0f} at λ = −9", INK, "start", 8)
    body += legend_row(96, vh - 64, [(lab, colour, False) for _, lab, colour in TARGET_STYLE]
                       + [("exact denoiser's error", SOFT, True)], 18)
    body += footnote(vh - 40, "Measured by the lab. Excess error is the clean-image estimate's squared error above the exact "
                              "denoiser's, per value; raw weights, mean of 3 seeds.", 40)
    body += footnote(vh - 24, "Each target's loss is reweighted so all three optimise the same Min-SNR-5 objective in expectation.", 40)
    emit(10, "targets-at-two-widths", "Targets at two widths",
         "Same objective, three output meanings, two network widths", body,
         "Measured excess error by log-SNR for ε, x0 and v prediction at network widths 256 and 32, with median "
         "sample distances", vw, vh)


# -------------------------------------------------------------------- fig 14

def fig14():
    vw, vh = 960, 540
    body = eyebrow(40, 36, "scaling · published model sizes, and the lab's width sweep")
    # left: EDM2's size ladder, quoted
    ax = Axes(96, 92, 340, 300, (math.log10(100), math.log10(2000)), (1.6, 3.8))
    body += text(96, 70, "EDM2, ImageNet-512 (quoted)", 12, INK, SANS, 600, "start")
    body += ax.frame([(math.log10(v), f"{v}") for v in (125, 280, 498, 777, 1119, 1523)],
                     [(v, f"{v:.1f}") for v in (1.8, 2.2, 2.6, 3.0, 3.4, 3.8)],
                     "PARAMETERS, MILLIONS (LOG)", "FID")
    for col, colour, lab in ((2, INK, "no guidance"), (3, ACCENT, "with guidance")):
        pts = [(math.log10(r[1]), r[col]) for r in EDM2]
        body += ax.path(pts, colour, 1.8)
        for (a, b), r in zip(pts, EDM2):
            body += ax.dot(a, b, 3.5, colour)
    # right: the lab's width sweep, at the two ends of the noise range
    widths = [32, 64, 128, 256, 512]
    lam = TRAIN["lam_grid"]
    i0, i9 = lam.index(-9.0), lam.index(9.0)
    bx = Axes(560, 92, 320, 300, (math.log10(24), math.log10(700)), (math.log10(5e-4), math.log10(5)), logy=True)
    body += text(560, 70, "Lab: excess error against width", 12, INK, SANS, 600, "start")
    body += bx.frame([(math.log10(w), str(w)) for w in widths],
                     [(v, f"{v:g}") for v in (0.001, 0.01, 0.1, 1)], "MLP WIDTH (LOG)", "EXCESS ERROR")
    for key, colour in (("snr", INK), ("minsnr5", ACCENT)):
        for idx, dash in ((i0, False), (i9, True)):
            pts = []
            for w in widths:
                rs = runs("width", weighting=key, width=w)
                pts.append((math.log10(w), sum(r["checkpoints"]["20000"]["raw"]["excess"][idx] for r in rs) / len(rs)))
            body += bx.path(pts, colour, 2.0, dash)
            for p in pts:
                body += bx.dot(p[0], p[1], 3, colour)
    snr_hi = sum(r["checkpoints"]["20000"]["raw"]["excess"][i0] for r in runs("width", weighting="snr", width=512)) / 2
    body += tag(bx.X(math.log10(512)) - 6, bx.Y(snr_hi) - 8, f"SNR, λ = −9: {snr_hi:.1f}", INK, "end", 8)
    body += legend_row(96, vh - 82, [(f"no guidance: {EDM2[0][2]:.2f} → {EDM2[-1][2]:.2f}", INK, False)], 14)
    body += legend_row(96, vh - 64, [(f"with guidance: {EDM2[0][3]:.2f} → {EDM2[-1][3]:.2f}", ACCENT, False)], 14)
    body += legend_row(560, vh - 82, [("SNR weighting", INK, False), ("Min-SNR-5", ACCENT, False)], 14)
    body += legend_row(560, vh - 64, [("noisiest, λ = −9", MUTED, False), ("cleanest, λ = +9", MUTED, True)], 14)
    body += footnote(vh - 40, "Left: EDM2 Table 2, 63 network evaluations, FID; compare within the chart only. Right: measured, "
                              "x₀-network, 20,000 steps, 2 seeds per point, raw weights.", 40)
    body += footnote(vh - 24, "SNR weighting's sampler worked at width 32 and failed at every larger width.", 40)
    emit(14, "scaling-model-size", "Scaling model size",
         "Bigger keeps helping; it does not rescue a starved noise level", body,
         "EDM2's ImageNet-512 FID falling from 3.53 at 125M to 1.91 at 1.5B parameters, beside the lab's error "
         "against width for two weightings", vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    body = eyebrow(72, 73, "diffusion · part five")
    body += text(72, 148, "Training a diffusion model", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "schedule · endpoint · target · weighting · EMA — fixed before step one", 15, MUTED,
                 MONO, 400, "start")

    # left: Stable Diffusion's log-SNR curve, its rescale, and the endpoint that leaks
    ax = Axes(96, 238, 420, 214, (0, 1), (-12, 8))
    body += (f'<line x1="{ax.x}" y1="{ax.Y(0)}" x2="{ax.x + ax.w}" y2="{ax.Y(0)}" stroke="{RULE_SOLID}" '
             f'stroke-width="1" stroke-dasharray="3,4"/>')
    body += (f'<line x1="{ax.x}" y1="{ax.y + ax.h}" x2="{ax.x + ax.w}" y2="{ax.y + ax.h}" stroke="{RULE_SOLID}" stroke-width="1"/>')
    sd = [(u, v) for u, v in schedule_points("scaled_linear") if v is not None]
    zs = [(u, v) for u, v in schedule_points("scaled_linear_zero_snr") if v is not None]
    body += ax.path(zs, ACCENT, 2.0, True)
    body += ax.path(sd, INK, 2.6)
    end = SCHED["scaled_linear"]["logsnr_T"]
    body += ax.dot(1.0, end, 6, ACCENT)
    ly = ax.Y(0) - 22                     # above the curve's end, clear of both lines
    body += (f'<line x1="{ax.X(1.0)}" y1="{ly + 6}" x2="{ax.X(1.0)}" y2="{ax.Y(end) - 9}" stroke="{ACCENT}" '
             f'stroke-width="1"/>')
    body += tag(ax.X(1.0), ly, f"last step: λ = {minus(f'{end:.1f}')}, not −∞", ACCENT, "end", 10)
    body += mono(ax.x, ax.y + ax.h + 22, "STABLE DIFFUSION'S SCHEDULE, AND ITS ZERO-SNR RESCALE", 9, MUTED, "start", 500)

    # right: the same starting noise through the rescaled schedule and through SD's
    var = LEAK["by_resolution"]["128"]["variants"]
    tx, size, gap = 640, 64, 12
    for row, (lab, key, colour, y0) in enumerate((("LAST STEP PURE NOISE", "zero_snr_trailing_noise", MUTED, 256),
                                                  ("LAST STEP KEEPS 6.8%", "sd_trailing_noise", ACCENT, 376))):
        body += mono(tx, y0 - 10, lab, 9, colour, "start", 500)
        for j, M in enumerate(var[key]["previews_32"][:6]):
            body += tile(tx + j * (size + gap), y0, size, M)

    body += f'<line x1="72" y1="508" x2="1128" y2="508" stroke="{RULE}" stroke-width="1"/>'
    body += text(72, 548, "The last step must be pure noise.", 20, MUTED, SERIF, 400, "start", italic=True)
    emit_cover(body, "Stable Diffusion's schedule ending at log-SNR −5.4, not minus infinity, beside crescents "
                     "sampled with and without a pure-noise last step")



# keyed by the figure number that reaches the post; 1 is Mermaid and 8 is a source figure
FIGURES = {2: fig02, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07, 9: fig09, 10: fig10, 11: fig11,
           12: fig12, 13: fig13, 14: fig14}

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
