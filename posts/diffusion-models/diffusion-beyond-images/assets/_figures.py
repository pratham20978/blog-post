#!/usr/bin/env python3
"""Figures for "Diffusion Beyond Images: Video, Audio, 3-D and Molecules" (diffusion-models, part 10).

Every measured or computed number drawn here is read from ../lab/captures.json, the capture that the
article's lab download ships, so the prose, the figures and the lab cannot drift apart. Two figures carry
numbers from papers instead: Figure 4's shapes come from Stable Video Diffusion's inference config (14
frames of 576 x 1024 in a 4-channel latent at 1/8 per side; ledger L12, L13), and Figure 6 draws EDM's
Table 1 (ledger L44), held once in QUOTED_EDM below. Figure 10 is MVDream's own Figure 1 (source route),
cropped from the arXiv v4 PDF without change; `python3 _figures.py 10` only checks the file is in place.

    python3 _figures.py            # every figure plus the cover
    python3 _figures.py 3 5        # just those
    python3 _figures.py cover      # just the cover
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, MONO, MUSTARD, MUTED, PAPER, PAPER2, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, emit, emit_cover, eyebrow, label, lcg, mono, node, rect, subtext, text,
    v_arrow, h_arrow, zconn,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP_PATH = pathlib.Path(os.environ.get("P10_CAPTURES", HERE.parent / "lab" / "captures.json"))
BLOG = HERE.parent / "blog.md"
_CAP = None

QUOTED_EDM = {  # Hoogeboom et al. 2022, Table 1, QM9, 10,000 samples, 3 runs (ledger L44)
    "GDM": {"mol": 63.2, "atom": 97.0},
    "GDM-aug": {"mol": 71.6, "atom": 97.6},
    "EDM": {"mol": 82.0, "atom": 98.7, "mol_sd": 0.4},
    "data": {"mol": 95.2, "atom": 99.0},
}
SVD = {"frames": 14, "h": 576, "w": 1024, "factor": 8, "latent_ch": 4, "cond_ch": 4, "width": 320,
       "temporal_params_m": 656, "total_params_m": 1521}   # ledger L12, L13


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


# ------------------------------------------------------------------ primitives (as in parts 8-9)

class Axes:
    """Data-to-pixel mapping for a real plot; logx/logy put an axis on log10."""

    _n = 0

    def __init__(self, x, y, w, h, xr, yr, logx=False, logy=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr, self.logx, self.logy = xr, yr, logx, logy
        Axes._n += 1
        self.clip = f"clip{Axes._n}"

    def X(self, v):
        if self.logx:
            v = math.log10(v)
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
            cx, cy = self.x - 52, self.y + self.h / 2
            out += f'<g transform="rotate(-90 {cx} {cy})">' + mono(cx, cy, ylabel, 8, SOFT) + '</g>'
        return out

    def path(self, pts, colour=INK, width=1.8, dash=None):
        d = {True: ' stroke-dasharray="6,4"', "dot": ' stroke-dasharray="1.5,3.5"'}.get(dash, "")
        s = " ".join(f"{self.X(a):.1f},{self.Y(b):.1f}" for a, b in pts)
        return (f'<g clip-path="url(#{self.clip})"><polyline points="{s}" fill="none" stroke="{colour}" '
                f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{d}/></g>')

    def dot(self, a, b, r=4, colour=INK, hollow=False, opacity=1.0):
        if hollow:
            return (f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{PAPER}" '
                    f'stroke="{colour}" stroke-width="1.6"/>')
        op = f' fill-opacity="{opacity}"' if opacity < 1 else ""
        return f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{colour}"{op}/>'

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


LO, HI = -2.0, 2.6           # one display range for every 8x8 tile, high value = bright (parts 8-9)


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


def swatch_row(x, y, items, gap=26):
    """Legend for filled marks: (label, fill) with a swatch filled exactly like the marks it names."""
    out = ""
    for lab, fill in items:
        out += rect(x, y - 9, 14, 10, fill, "none", 1)
        out += mono(x + 22, y, lab, 8, MUTED, "start")
        x += 36 + len(lab) * 6.2 + gap
    return out


def num(v):
    """Display a number with a real minus sign."""
    return f"{v:.2f}".replace("-", "−")


def pct(v, digits=1):
    return f"{100 * v:.{digits}f}%"


def frame_mean(flat):
    return sum(flat) / len(flat)


# -------------------------------------------------------------------- fig 01

FIG01_ROWS = [
    ("for scale", [("one 256 x 256 RGB image, for scale", "one 256 × 256 RGB image")]),
    ("molecules", [("GEOM-DRUGS molecule, average torsion angles", "GEOM-DRUGS molecule as torsion angles"),
                   ("GEOM-DRUGS molecule, average (44 atoms x 3 coordinates)", "the same molecule as 44 atoms × 3"),
                   ("QM9 molecule, EDM (29 atoms x 3 coordinates + 5 atom types + 1 charge)",
                    "QM9 molecule in EDM: 29 atoms × 9")]),
    ("point clouds", [("PVD point cloud (2,048 points x 3)", "PVD shape: 2,048 points × 3"),
                      ("Point-E point cloud (4,096 points x xyz + RGB)", "Point-E cloud: 4,096 points × 6")]),
    ("audio", [("1 s of speech at 16 kHz (DiffWave)", "1 s of speech at 16 kHz"),
               ("10 s of audio at 16 kHz (AudioLDM waveform)", "10 s at 16 kHz: waveform"),
               ("same 10 s as a 64-band mel spectrogram (hop 160)", "as a 64-band mel spectrogram"),
               ("same 10 s as AudioLDM's latent (r = 4, C = 8)", "as AudioLDM's latent"),
               ("95.1 s of 44.1 kHz stereo (Stable Audio window)", "95.1 s of 44.1 kHz stereo"),
               ("same window as Stable Audio's latent (1/1024 in time, 64 channels)", "as Stable Audio's latent")]),
    ("video", [("16 frames of 64 x 64 RGB (Video Diffusion Models)", "VDM clip: 16 frames of 64 × 64"),
               ("14 frames of 576 x 1024 RGB (Stable Video Diffusion)", "SVD clip: 14 frames of 576 × 1024"),
               ("same 14 frames as SVD's latent (1/8 per side, 4 channels)", "as SVD's latent")]),
]


def fig01():
    """One sample's size across the post's modalities, log scale, from each paper's configuration."""
    vw, vh = 960, 720
    C = {d["label"]: d for d in cap()["census"]["sizes"]}
    comp = cap()["census"]["compression"]
    ratio = {"as AudioLDM's latent": comp["audio_audioldm_vs_waveform"],
             "as Stable Audio's latent": comp["audio_stable_audio"], "as SVD's latent": comp["video_svd"]}
    ref = C["one 256 x 256 RGB image, for scale"]["numbers"]
    x0, x1 = 400, 840
    colours = {"raw": INK, "reduced": BLUE, "latent": ACCENT, "scale": RULE_SOLID}

    def X(v):
        lv = math.log10(v)
        assert 0 <= lv <= 8, v
        return x0 + lv / 8 * (x1 - x0)

    body = eyebrow(40, 52, "one sample, counted from each paper's stated configuration · numbers per sample, log scale")
    y = 100
    for group, items in FIG01_ROWS:
        body += eyebrow(40, y + 4, group, MUTED)
        for key, disp in items:
            d = C[key]
            v, kind = d["numbers"], ("scale" if group == "for scale" else d["kind"])
            indent = kind != "raw" and disp.startswith("as ")
            body += text(166 if indent else 150, y + 4, disp, 11,
                         MUTED if indent else INK, SANS, 500, "start")
            body += rect(x0, y - 7, max(2.0, X(v) - x0), 14, colours[kind], "none", 2)
            val = f"{v:,}" if v >= 10 else f"{v:g}"
            if disp in ratio:
                val += f"  ÷{ratio[disp]:.0f}"
            body += mono(X(v) + 8, y + 4, val, 9, {"raw": INK, "scale": MUTED}.get(kind, colours[kind]), "start", 500)
            y += 27
        y += 12
    bottom = y - 12
    # axis
    ay = bottom + 8
    body += f'<line x1="{x0}" y1="{ay}" x2="{x1}" y2="{ay}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for e, lab in enumerate(("1", "10", "100", "1k", "10k", "100k", "1M", "10M", "100M")):
        px = X(10 ** e)
        body += f'<line x1="{px:.1f}" y1="{ay}" x2="{px:.1f}" y2="{ay + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        body += mono(px, ay + 16, lab, 7, SOFT)
    body += mono((x0 + x1) / 2, ay + 34, "NUMBERS PER SAMPLE (LOG SCALE)", 8, SOFT)
    body += swatch_row(150, ay + 70, (("raw array", INK), ("reduced: spectrogram, torsion angles", BLUE),
                                      ("autoencoder latent", ACCENT)))
    body += footnote(vh - 50, "Computed by beyond.py census from the sizes each paper states: EDM, torsional diffusion, PVD, "
                              "Point-E, DiffWave,")
    body += footnote(vh - 32, "AudioLDM (64 bands, hop 160, r = 4, C = 8), Stable Audio (1/1024, 64 channels), VDM, SVD "
                              "(1/8 per side, 4 channels).")
    emit(1, "numbers-per-sample",
         "One sample spans more than five orders of magnitude", "latent spaces exist because video and audio sit at the top", body,
         alt_checked("Log-scale bars of numbers per sample, from 7.9 torsion angles and a 261-number molecule to 24.8 "
                     "million for 14 video frames"), vw, vh)


# -------------------------------------------------------------------- fig 02

def numgrid(x, y, rows, cw=46, ch=24, hot=None, ring=(), size=9):
    out = ""
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            cx, cy = x + c * cw, y + r * ch
            is_hot, is_ring = hot == (r, c), (r, c) in ring
            fill = ACCENT_TINT if is_hot else "#ffffff"
            stroke = ACCENT if (is_hot or is_ring) else RULE_SOLID
            out += rect(cx, cy, cw - 4, ch - 4, fill, stroke, 2, 1.4 if (is_hot or is_ring) else 0.8)
            out += mono(cx + (cw - 4) / 2, cy + (ch - 4) / 2 + 3, num(v), size, ACCENT if is_hot else INK)
    return out


def panel(x, y, w, h, title, must):
    out = rect(x, y, w, h, "#ffffff", RULE_SOLID, 6, 0.8)
    out += eyebrow(x + 16, y + 22, title, MUTED)
    out += f'<line x1="{x + 16}" y1="{y + h - 30}" x2="{x + w - 16}" y2="{y + h - 30}" stroke="{RULE}" stroke-width="0.8"/>'
    out += eyebrow(x + 16, y + h - 13, "the denoiser must: " + must, ACCENT)
    return out


def fig02():
    """Part 1's 16 numbers, one forward step, read four ways."""
    vw, vh = 960, 720
    W = cap()["worked"]
    x0, eps, xt = W["x0"], W["eps"], W["xt"]
    body = eyebrow(40, 46, "part 1's 4 × 4 patch · one forward step with signal scale 0.8 and noise scale 0.6")
    gy = 96
    body += text(40, gy + 52, "0.8 ×", 14, INK, MONO, 500, "start")
    body += subtext(88 + 90, gy - 12, "x", "0", 13, INK)
    body += numgrid(88, gy, x0, hot=(0, 0))
    body += text(286, gy + 52, "+ 0.6 ×", 14, INK, MONO, 500, "start")
    body += text(368 + 90, gy - 12, "ε", 13, INK, SANS, 600)
    body += numgrid(368, gy, eps, hot=(0, 0))
    body += text(566, gy + 52, "=", 16, INK, MONO, 500, "start")
    body += subtext(596 + 90, gy - 12, "x", "t", 13, INK)
    body += numgrid(596, gy, xt, hot=(0, 0))
    tl = W["top_left"]
    body += mono(800, gy + 30, "top-left:", 9, MUTED, "start")
    body += mono(800, gy + 48, f"0.8 × {num(tl['x0'])}", 9, INK, "start")
    body += mono(800, gy + 64, f"+ 0.6 × {num(tl['eps'])}", 9, INK, "start")
    body += mono(800, gy + 80, f"= {num(tl['xt'])}", 9, ACCENT, "start", 600)
    body += mono(40, gy + 122, "the same sixteen multiply-adds whatever the numbers mean; below, the clean values read four ways",
                 9, MUTED, "start")

    # A: image
    px, py, pw, ph = 40, 250, 430, 210
    body += panel(px, py, pw, ph, "an image · 4 × 4 pixels", "respect 2-d neighbours")
    ring = {(0, 1), (2, 1), (1, 0), (1, 2)}
    body += numgrid(px + 16, py + 38, x0, cw=42, ch=30, hot=(1, 1), ring=ring)
    nb = W["image"]["neighbours"]
    lx = px + 210
    body += text(lx, py + 62, f"value {num(W['image']['value'])}", 11, INK, SANS, 600, "start")
    body += mono(lx, py + 82, f"4 neighbours: {num(nb['up'])} above,", 8, MUTED, "start")
    body += mono(lx, py + 96, f"{num(nb['down'])} below, {num(nb['left'])} left,", 8, MUTED, "start")
    body += mono(lx, py + 110, f"{num(nb['right'])} right", 8, MUTED, "start")
    body += mono(lx, py + 134, "one filter slides over", 8, MUTED, "start")
    body += mono(lx, py + 148, "every position", 8, MUTED, "start")

    # B: waveform
    px, py = 490, 250
    body += panel(px, py, pw, ph, f"a waveform · 16 samples = {W['audio']['ms']:g} ms at 16 khz", "reach far along one axis")
    flat = [v for row in x0 for v in row]
    ax = Axes(px + 30, py + 40, 370, 90, (0, 15), (-1.1, 1.1))
    body += f'<line x1="{ax.X(0) - 6}" y1="{ax.Y(0):.1f}" x2="{ax.X(15) + 6}" y2="{ax.Y(0):.1f}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for i, v in enumerate(flat):
        hot, ringed = i == 5, i in (4, 6)
        colour = ACCENT if hot else INK
        body += (f'<line x1="{ax.X(i):.1f}" y1="{ax.Y(0):.1f}" x2="{ax.X(i):.1f}" y2="{ax.Y(v):.1f}" '
                 f'stroke="{colour}" stroke-width="1.4"/>')
        body += ax.dot(i, v, 4 if hot else 3, colour, hollow=ringed)
    body += mono(px + 30, py + 150, f"sample 6 = {num(flat[5])}; neighbours {num(flat[4])} and {num(flat[6])}", 8, MUTED, "start")
    body += mono(px + 30, py + 164, f"1 s = {W['audio']['per_second']:,} samples, {W['audio']['patches_per_second']:,} of these patches",
                 8, MUTED, "start")

    # C: clip
    px, py = 40, 480
    V = W["video"]
    body += panel(px, py, pw, ph, "a clip · 4 frames of 1 × 4", "look across frames")
    body += subtext(px + 34 + 80, py + 44, "clean x", "0", 9, SOFT, MONO, 500)
    body += subtext(px + 230 + 80, py + 44, "noisy x", "t", 9, SOFT, MONO, 500)
    for f in range(4):
        body += mono(px + 12, py + 66 + f * 26, f"f{f + 1}", 8, SOFT, "start")
        body += numgrid(px + 34, py + 52 + f * 26, [x0[f]], cw=40, ch=24, size=8)
        body += numgrid(px + 230, py + 52 + f * 26, [xt[f]], cw=40, ch=24, size=8)
    body += mono(px + 16, py + 168, f"mean change between frames: {V['mean_abs_change_clean']:.3f} clean, "
                                     f"{V['mean_abs_change_noisy']:.3f} noisy ({V['ratio']:.1f}×)", 8, MUTED, "start")

    # D: points
    px, py = 490, 480
    P = W["points"]
    body += panel(px, py, pw, ph, f"8 points · one set, {P['orderings']:,} orders", "ignore order and position")
    ax = Axes(px + 40, py + 40, 200, 120, (-1.0, 1.0), (-1.1, 0.7))
    body += (f'<line x1="{ax.X(-1.0)}" y1="{ax.Y(0):.1f}" x2="{ax.X(1.0)}" y2="{ax.Y(0):.1f}" stroke="{RULE}" stroke-width="0.8"/>'
             f'<line x1="{ax.X(0):.1f}" y1="{ax.Y(-1.1)}" x2="{ax.X(0):.1f}" y2="{ax.Y(0.7)}" stroke="{RULE}" stroke-width="0.8"/>')
    offsets = {1: (7, -4), 2: (7, -4), 3: (8, 11), 4: (0, 14), 5: (-10, -6), 6: (0, 14), 7: (7, -4), 8: (0, 14)}
    for i, (a, b) in enumerate(P["x0"]):
        dx, dy = offsets[i + 1]
        body += ax.dot(a, b, 3.2, INK)
        body += mono(ax.X(a) + dx, ax.Y(b) + dy, str(i + 1), 7, SOFT, "start" if dx > 0 else "middle")
    cx, cy = P["centroid_x0"]
    sx, sy = P["centroid_shift_by_noise"]
    body += (f'<line x1="{ax.X(cx) - 5:.1f}" y1="{ax.Y(cy):.1f}" x2="{ax.X(cx) + 5:.1f}" y2="{ax.Y(cy):.1f}" stroke="{ACCENT}" stroke-width="1.6"/>'
             f'<line x1="{ax.X(cx):.1f}" y1="{ax.Y(cy) - 5:.1f}" x2="{ax.X(cx):.1f}" y2="{ax.Y(cy) + 5:.1f}" stroke="{ACCENT}" stroke-width="1.6"/>')
    lx = px + 262
    body += text(lx, py + 62, "centre +", 11, ACCENT, SANS, 600, "start")
    body += mono(lx, py + 82, "noise moves it by", 8, MUTED, "start")
    body += mono(lx, py + 96, f"({sx:.2f}, {sy:.4f})".replace("-", "−"), 8, INK, "start")
    body += mono(lx, py + 120, "labels 1-8: one of", 8, MUTED, "start")
    body += mono(lx, py + 134, f"{P['orderings']:,} listings", 8, MUTED, "start")
    body += mono(lx, py + 148, "of the same set", 8, MUTED, "start")
    emit(2, "one-step-four-readings", "One forward step, four readings",
         "the noise step is identical; the neighbours and the symmetries differ", body,
         alt_checked("One forward step on Part 1's 16 numbers, and the clean values as a 4x4 image, a 16-sample "
                     "waveform, four 1x4 frames and eight 2-D points"), vw, vh)


# -------------------------------------------------------------------- fig 03

FIG03_ROWS = [("data", "Real clips", "a quarter turn per frame"),
              ("independent", "Independent noise", "image model, fresh noise per frame"),
              ("mixed 0.5", "Mixed noise, ρ = 0.5", "PYoCo's prior with α = {alpha:g}"),
              ("mixed 0.9", "Mixed noise, ρ = 0.9", "one shared draw dominates"),
              ("mixed 0.99", "Mixed noise, ρ = 0.99", "nearly one noise"),
              ("shared", "Shared noise", "one noise for every frame"),
              ("warped", "Warped noise", "frame 0's noise, turned per frame"),
              ("joint", "Joint model", "one denoiser for the whole clip")]
FIG03_COLS = [("flicker", "brightness flicker", "of frame changes"), ("contrast_flips", "contrast flips", "of frame changes"),
              ("frozen_turns", "no turn", "of frame changes"), ("coherent_clips", "coherent", "of clips")]


def fig03():
    """Per-frame model under four noise schemes against the joint model: flicker, freezing, coherence."""
    vw, vh = 960, 720
    V = cap()["video"]
    S = V["schemes"]
    body = eyebrow(40, 46, f"crescent world in motion · {V['n']:,} clips of {V['frames']} frames per scheme · "
                           "exact denoisers, 128 ddim steps")
    cols_x = [574, 676, 778, 880]
    body += mono(292 + 97, 96, "EXAMPLE CLIP, FRAMES 1-4", 8, SOFT)
    for (key, head, sub), cx in zip(FIG03_COLS, cols_x):
        body += mono(cx, 90, head.upper(), 8, INK, weight=500)
        body += mono(cx, 103, sub, 7, SOFT)
    y = 128
    for key, name, sub in FIG03_ROWS:
        st = S[key]
        if key in ("warped", "joint", "data"):
            body += rect(28, y - 4, 904, 62, ACCENT_TINT if key != "data" else "rgba(45,49,66,0.04)", "none", 4)
        body += text(40, y + 24, name, 13, INK, SANS, 600, "start")
        body += mono(40, y + 42, sub.format(alpha=st.get("pyoco_alpha", 0)), 8, MUTED, "start")
        for f, fr in enumerate(st["_example"][0]):
            body += tile(292 + f * 50, y + 6, 44, fr)
        for (k, _, _), cx in zip(FIG03_COLS, cols_x):
            v = st[k]
            colour = ACCENT if k == "coherent_clips" else INK
            body += rect(cx - 36, y + 16, 72, 8, PAPER2, "none", 2)
            if v > 0:
                body += rect(cx - 36, y + 16, max(1.5, 72 * v), 8, colour, "none", 2)
            shown = "<0.1%" if 0 < v < 0.0005 else pct(v)
            body += mono(cx, y + 44, shown, 9, colour if k == "coherent_clips" else INK, weight=500)
        y += 66
    tau = cap()["world"]["detail"]
    body += footnote(vh - 50, f"Measured by beyond.py video. Flicker: the frame's mean brightness moves by more than "
                              f"{V['bright_tol']:g} (within real clips, sd {tau * math.sqrt(2 / 64):.3f}).")
    body += footnote(vh - 32, "Tiles: each scheme's first clip, frames left to right; one display range (-2.0 to 2.6), "
                              "bright = high.")
    emit(3, "frame-by-frame-vs-joint", "Correlated noise trades flicker for freezing",
         "warped noise moves only because a quarter turn is a symmetry of the image model", body,
         alt_checked(f"Bars for {V['n']:,} clips per noise scheme: independent noise flickers, correlated noise freezes, "
                     "warped noise and the joint model move"), vw, vh)


# -------------------------------------------------------------------- fig 04

def fig04():
    """One level of a factorized video U-Net in SVD's latent, with the tensor shape on every edge."""
    vw, vh = 960, 700
    T, H, Wd = SVD["frames"], SVD["h"] // SVD["factor"], SVD["w"] // SVD["factor"]
    tokens = H * Wd
    c_in, width = SVD["latent_ch"] + SVD["cond_ch"], SVD["width"]
    body = eyebrow(40, 46, f"stable video diffusion's denoiser, first level · {T} frames at {SVD['h']} × {SVD['w']} "
                           f"in a {SVD['latent_ch']}-channel latent at 1/{SVD['factor']} per side")
    cx, nw, nh = 400, 300, 62
    x = cx - nw / 2
    ys = [84, 192, 300, 408, 516]
    nodes = [(("Noisy latent clip", ""), f"B × {T} × {c_in} × {H} × {Wd}  ({SVD['latent_ch']} noisy + {SVD['cond_ch']} condition)", "input"),
             (("conv_in, per frame", ""), f"{c_in} → {width} channels", "soft"),
             (("Spatial ResBlock + attention", ""), f"{tokens:,} tokens per frame; frames never meet", "normal"),
             (("Temporal conv + attention", ""), f"{T} tokens per position · where frames meet", "focal"),
             (("Next level, then decoder", ""), f"same pattern at {H // 2} × {Wd // 2} and {H // 4} × {Wd // 4}", "soft")]
    for (title, sub, kind), y in zip(nodes, ys):
        body += node(x, y, nw, nh, title[0], sub, kind)
    edges = [(f"B·{T} × {c_in} × {H} × {Wd}", "frames as batch"),
             (f"B·{T} × {width} × {H} × {Wd}", "frames as batch"),
             (f"B·{tokens:,} × {T} × {width}", "reshape: positions as batch"),
             (f"B·{T} × {width} × {H} × {Wd}", "reshape back")]
    for i, (shape, meaning) in enumerate(edges):
        y1, y2 = ys[i] + nh, ys[i + 1]
        colour = ACCENT if i == 2 else MUTED
        body += v_arrow(cx, y1 + 2, y2 - 2, colour, accent=(i == 2))
        body += mono(cx + 14, (y1 + y2) / 2 - 2, shape, 8, colour, "start", 500)
        body += mono(cx + 14, (y1 + y2) / 2 + 11, meaning, 7, SOFT, "start")
    # brackets: what is frozen, what is new
    bx = x - 26
    body += (f'<path d="M{bx + 10},{ys[2]} H{bx} V{ys[2] + nh} H{bx + 10}" fill="none" stroke="{MUTED}" stroke-width="1"/>')
    body += mono(bx - 8, ys[2] + 18, "IMAGE MODEL'S LAYERS", 8, MUTED, "end", 500)
    body += mono(bx - 8, ys[2] + 34, "Align your Latents", 7, SOFT, "end")
    body += mono(bx - 8, ys[2] + 46, "keeps these frozen", 7, SOFT, "end")
    body += (f'<path d="M{bx + 10},{ys[3]} H{bx} V{ys[3] + nh} H{bx + 10}" fill="none" stroke="{ACCENT}" stroke-width="1"/>')
    body += mono(bx - 8, ys[3] + 24, "NEW LAYERS", 8, ACCENT, "end", 500)
    body += mono(bx - 8, ys[3] + 38, f"{SVD['temporal_params_m']}M of SVD's", 7, SOFT, "end")
    body += mono(bx - 8, ys[3] + 50, f"{SVD['total_params_m']:,}M parameters", 7, SOFT, "end")
    # attention cost at this level, computed from the shapes
    sp, tp, full = T * tokens ** 2, tokens * T ** 2, (T * tokens) ** 2
    rx = 704
    body += rect(rx - 14, 300, 246, 220, "#ffffff", RULE_SOLID, 6, 0.8)
    body += eyebrow(rx, 322, "token pairs scored per layer", MUTED)
    rows = [("spatial", f"{T} × {tokens:,}²", sp, INK), ("temporal", f"{tokens:,} × {T}²", tp, ACCENT),
            ("full space-time", f"({T} × {tokens:,})²", full, MUTED)]
    yy = 348
    for name, expr, val, colour in rows:
        body += text(rx, yy, name, 11, colour, SANS, 600, "start")
        body += mono(rx, yy + 16, f"{expr} = {val:,}", 8, MUTED, "start")
        yy += 44
    body += mono(rx, yy + 4, f"full attention would score {full // sp}× the", 8, INK, "start")
    body += mono(rx, yy + 18, "spatial pass's pairs", 8, INK, "start")
    body += footnote(vh - 50, "Shapes from SVD's inference config (4 latent channels, ch_mult [1, 2, 4, 4]) and the paper's "
                              "14 frames at 576 × 1024.")
    body += footnote(vh - 32, "Token pairs computed from those shapes for one attention layer at this level; B is the batch size.")
    emit(4, "video-denoiser-block", "Temporal layers are the only place frames meet",
         "frames are a batch for the spatial layers; positions are a batch for the temporal ones", body,
         alt_checked(f"Video denoiser block: latent clip {T}x{SVD['latent_ch']}x{H}x{Wd}, spatial layers per frame, "
                     "temporal layers per pixel across frames, shapes on edges"), vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    """One 10-s clip at 16 kHz as waveform, mel spectrogram and latent, to scale, with DiffWave's reach."""
    vw, vh = 960, 580
    C = {d["label"]: d["numbers"] for d in cap()["census"]["sizes"]}
    rf = cap()["census"]["receptive_field"]
    wav = C["10 s of audio at 16 kHz (AudioLDM waveform)"]
    mel = C["same 10 s as a 64-band mel spectrogram (hop 160)"]
    lat = C["same 10 s as AudioLDM's latent (r = 4, C = 8)"]
    sa_raw = C["95.1 s of 44.1 kHz stereo (Stable Audio window)"]
    sa_lat = C["same window as Stable Audio's latent (1/1024 in time, 64 channels)"]
    x0, full = 60, 760
    scale = full / wav

    def bar_w(n):
        return n * scale

    body = eyebrow(40, 46, "one 10-second clip at 16 khz, mono · lengths drawn to scale · audioldm's pipeline")
    # waveform
    y = 112
    body += text(x0, y - 16, f"Waveform · {wav:,} samples", 13, INK, SANS, 600, "start")
    body += mono(x0 + full, y - 16, "16,000 per second", 8, MUTED, "end")
    body += rect(x0, y, full, 46, "#ffffff", RULE_SOLID, 3, 0.8)
    rng = lcg(10)
    pts = []
    for i in range(381):
        u = i / 380
        env = 0.35 + 0.65 * abs(math.sin(u * 7.3)) * (0.6 + 0.4 * math.sin(u * 31.0))
        pts.append(f"{x0 + 4 + u * (full - 8):.1f},{y + 23 + (next(rng) - 0.5) * 38 * env:.1f}")
    body += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="0.9" opacity="0.8"/>'
    reach = bar_w(rf["samples"])
    body += (f'<path d="M{x0},{y + 54} V{y + 60} H{x0 + reach:.1f} V{y + 54}" fill="none" stroke="{ACCENT}" stroke-width="1.6"/>')
    body += mono(x0, y + 76, f"DiffWave's reach: {rf['samples']:,} samples = {rf['seconds_at_16k']:.2f} s "
                             "(30 dilated layers); T reverse steps carry it up to T times as far", 8, ACCENT, "start")
    # mel
    y2 = 250
    body += text(x0, y2 - 16, f"Mel spectrogram · {mel // 64:,} frames × 64 bands = {mel:,}", 13, INK, SANS, 600, "start")
    mw = bar_w(mel)
    body += rect(x0, y2, mw, 46, "#ffffff", BLUE, 3, 1)
    for i in range(1, 32):
        body += (f'<line x1="{x0 + i * mw / 32:.1f}" y1="{y2 + 2}" x2="{x0 + i * mw / 32:.1f}" y2="{y2 + 44}" '
                 f'stroke="{BLUE}" stroke-width="0.6" opacity="0.35"/>')
    for j in range(1, 8):
        body += (f'<line x1="{x0 + 2}" y1="{y2 + j * 46 / 8:.1f}" x2="{x0 + mw - 2:.1f}" y2="{y2 + j * 46 / 8:.1f}" '
                 f'stroke="{BLUE}" stroke-width="0.6" opacity="0.35"/>')
    body += mono(x0, y2 - 36, "▼ short-time transform, window 1,024, hop 160, 64 mel bands; magnitudes only, phase dropped",
                 8, BLUE, "start")
    # latent
    y3 = 370
    body += text(x0, y3 - 16, f"AudioLDM latent · {mel // 64 // 4:,} × 16 × 8 channels = {lat:,}", 13, ACCENT, SANS, 600, "start")
    lw = bar_w(lat)
    body += rect(x0, y3, lw, 46, ACCENT_TINT, ACCENT, 3, 1.2)
    for i in range(1, 16):
        body += (f'<line x1="{x0 + i * lw / 16:.1f}" y1="{y3 + 2}" x2="{x0 + i * lw / 16:.1f}" y2="{y3 + 44}" '
                 f'stroke="{ACCENT}" stroke-width="0.6" opacity="0.4"/>')
    body += mono(x0, y3 - 36, "▼ VAE encoder: 1/4 in time and in frequency, 8 channels", 8, ACCENT, "start")
    body += mono(x0 + lw + 12, y3 + 20, "diffusion runs here", 8, ACCENT, "start", 600)
    body += mono(x0 + lw + 12, y3 + 34, f"{wav // lat:.0f}× fewer numbers than the waveform; decoded back by", 8, MUTED, "start")
    body += mono(x0 + lw + 12, y3 + 48, "the VAE decoder, then a HiFi-GAN vocoder", 8, MUTED, "start")
    # the chain between them, as text: no connector can cross a label

    # Stable Audio note
    body += rect(40, 452, 880, 52, "#ffffff", RULE_SOLID, 6, 0.8)
    body += text(56, 474, "Stable Audio skips the spectrogram:", 11, INK, SANS, 600, "start")
    body += mono(56, 492, f"95.1 s of 44.1 kHz stereo, {sa_raw:,} numbers, to a 64-channel latent at 1/1,024 of the "
                          f"rate: {sa_lat:,}, {sa_raw // sa_lat}× fewer", 8, MUTED, "start")
    body += footnote(vh - 50, "Sizes computed by beyond.py census from AudioLDM's (16 kHz, 64 bands, hop 160, r = 4, C = 8), "
                              "DiffWave's and Stable Audio's")
    body += footnote(vh - 32, "stated configurations. Waveform and spectrogram textures are illustrative; lengths are to scale.")
    emit(5, "audio-to-scale", "Shortening the axis is most of what changes for sound",
         "the denoiser then runs on a spectrogram or a latent; encoder and vocoder carry the rest", body,
         alt_checked(f"One 10-second clip drawn to scale as {wav:,} waveform samples, {mel:,} mel values and {lat:,} latent "
                     f"values, with a {rf['seconds_at_16k']:.2f} s reach"), vw, vh)


# -------------------------------------------------------------------- fig 06

def fig06():
    """EDM's Table 1: one network size and dataset, three ways to handle rotation (quoted)."""
    vw, vh = 960, 540
    E = QUOTED_EDM
    rows = [("GDM", "No equivariance", "a rotated molecule is a new input to the network", INK),
            ("GDM-aug", "Random rotations in training", "the same network learns rotation from rotated copies", BLUE),
            ("EDM", "Equivariant network (EGNN)", "its predicted noise turns with its input, by construction", ACCENT),
            ("data", "Training data", "QM9's own molecules", SOFT)]
    x0, x1 = 470, 860

    def X(p):
        assert 0 <= p <= 100, p
        return x0 + p / 100 * (x1 - x0)

    body = eyebrow(40, 46, "qm9 · 10,000 generated molecules per model, 3 runs · same 9-layer, 256-feature network · quoted")
    body += mono(x0, 96, "STABLE MOLECULES: EVERY ATOM WITH THE RIGHT NUMBER OF BONDS", 8, INK, "start", 500)
    y = 140
    ys = {}
    for key, name, sub, colour in rows:
        e = E[key]
        ys[key] = y
        body += text(40, y + 2, name, 13, INK, SANS, 600, "start")
        body += mono(40, y + 20, sub, 8, MUTED, "start")
        body += rect(x0, y - 9, X(100) - x0, 16, PAPER2, "none", 2)
        body += rect(x0, y - 9, X(e["mol"]) - x0, 16, colour, "none", 2)
        body += mono(X(e["mol"]) + 8, y + 3, f"{e['mol']:.1f}%", 9, colour if key != "data" else MUTED, "start", 600)
        extra = f" · molecules ± {e['mol_sd']:.1f} over 3 runs" if "mol_sd" in e else ""
        body += mono(x0, y + 26, f"atoms stable: {e['atom']:.1f}%{extra}", 7, SOFT, "start")
        y += 72
    for p, lab in ((0, "0"), (25, "25%"), (50, "50%"), (75, "75%"), (100, "100%")):
        body += f'<line x1="{X(p):.1f}" y1="{y - 34}" x2="{X(p):.1f}" y2="{y - 30}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        body += mono(X(p), y - 18, lab, 7, SOFT)
    body += f'<line x1="{x0}" y1="{y - 34}" x2="{x1}" y2="{y - 34}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    gap = (E["EDM"]["mol"] - E["GDM"]["mol"]) / (E["data"]["mol"] - E["GDM"]["mol"])
    body += mono(40, y + 6, f"Equivariance closes {100 * gap:.0f}% of the gap between no equivariance "
                           f"({E['GDM']['mol']}%) and the data ({E['data']['mol']}%).", 8, ACCENT, "start", 500)
    body += footnote(vh - 50, "Quoted from Hoogeboom et al., Equivariant Diffusion for Molecule Generation in 3D (ICML 2022), "
                              "Table 1; ± is a standard")
    body += footnote(vh - 32, "deviation over 3 runs. GDM and GDM-aug are the paper's non-equivariant ablations of the same model.")
    emit(6, "equivariance-on-qm9", "Same network, three ways to handle rotation",
         "equivariance by construction beat learning rotation from rotated copies", body,
         alt_checked(f"Bars of QM9 molecule stability: non-equivariant {E['GDM']['mol']}%, rotation-augmented "
                     f"{E['GDM-aug']['mol']}%, equivariant EDM {E['EDM']['mol']}%, training data {E['data']['mol']}%"), vw, vh)


# -------------------------------------------------------------------- fig 07

def fig07():
    """Wrapped normal on a circle at three spreads, against line Gaussians, computed."""
    vw, vh = 960, 580
    C = cap()["census"]
    cur, wn = C["curves"], C["wrapped_normal"]
    th = cur["theta"]
    ax = Axes(100, 92, 540, 330, (-3.1416, 3.1416), (0.0, 0.56))   # theta is stored to 4 decimals
    body = eyebrow(40, 46, "gaussian noise on an angle, wrapped onto the circle · computed, density per radian")
    body += ax.frame(xticks=((-math.pi, "−π"), (-math.pi / 2, "−π/2"), (0, "0"), (math.pi / 2, "π/2"), (math.pi, "π")),
                     yticks=[(v, f"{v:.1f}") for v in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5)],
                     xlabel="ANGLE θ (RADIANS); −π AND π ARE THE SAME ANGLE", ylabel="DENSITY")
    uni = 1 / (2 * math.pi)
    body += ax.hline(uni, SOFT, dash=True)
    body += tag(ax.X(-math.pi) + 70, ax.Y(uni) - 6, "uniform = 1/2π", SOFT, "middle", 8)
    styles = {"0.25": (BLUE, "σ = π/4"), "0.5": (INK, "σ = π/2"), "1.0": (ACCENT, "σ = π")}
    for key, (colour, _) in styles.items():
        body += ax.path(list(zip(th, cur[key])), colour, 2.0)
        if key != "0.25":
            body += ax.path(list(zip(th, cur[f"line {key}"])), colour, 1.4, dash=True)
    body += legend_row(100, vh - 76, [("σ = π/4", BLUE, False), ("σ = π/2", INK, False), ("σ = π", ACCENT, False),
                                      ("dashed: same σ on a line, no wrap", MUTED, True)])
    rx = 680
    body += text(rx, 118, "Peak over trough", 12, INK, SANS, 600, "start")
    yy = 142
    for key, lab in (("0.25", "σ = π/4"), ("0.5", "σ = π/2"), ("1.0", "σ = π")):
        mm = wn[key]["max_over_min"]
        body += mono(rx, yy, f"{lab}:", 9, styles[key][0], "start", 600)
        body += mono(rx + 70, yy, f"{mm:,.4f}" if mm < 10 else f"{mm:,.0f}", 9, INK, "start")
        yy += 20
    body += mono(rx, yy + 14, "at σ = π, torsional diffusion's", 8, MUTED, "start")
    body += mono(rx, yy + 28, "largest noise, the circle is", 8, MUTED, "start")
    body += mono(rx, yy + 42, f"within {100 * (wn['1.0']['max_over_min'] - 1):.0f}% of flat", 8, MUTED, "start")
    body += text(rx, yy + 82, "Line Gaussian, one turn", 12, INK, SANS, 600, "start")
    body += mono(rx, yy + 104, f"σ = π keeps {pct(wn['1.0']['line_gaussian_mass_inside'], 0)} of its", 8, MUTED, "start")
    body += mono(rx, yy + 118, "mass inside −π..π; on the circle", 8, MUTED, "start")
    body += mono(rx, yy + 132, "the rest wraps round and fills in", 8, MUTED, "start")
    body += footnote(vh - 50, "Computed by beyond.py census: the wrapped normal is the line Gaussian summed over shifts of "
                              "2π (equation 4).")
    body += footnote(vh - 32, "The dashed curves show the same Gaussian on a line, restricted to one turn; at σ = π/4 the two coincide.")
    emit(7, "noise-on-a-circle", "On a circle, noise ends uniform", "a wrapped Gaussian flattens instead of spreading forever",
         body, alt_checked("Wrapped normal densities on a circle at three noise levels flattening toward uniform, beside "
                           "line Gaussians that spread past one turn"), vw, vh)


# -------------------------------------------------------------------- fig 08

def node2(x, y, w, h, title, sub1, sub2, kind="normal"):
    """A node with a title and two short sub-lines, so no line has to be squeezed into the box."""
    styles = {"normal": ("#ffffff", INK), "focal": (ACCENT_TINT, ACCENT), "soft": ("rgba(45,49,66,0.05)", MUTED),
              "input": ("rgba(79,93,117,0.10)", SOFT)}
    fill, stroke = styles[kind]
    out = rect(x, y, w, h, PAPER, "none") + rect(x, y, w, h, fill, stroke)
    out += text(x + w / 2, y + 26, title, 12, ACCENT if kind == "focal" else INK, SANS, 600)
    out += mono(x + w / 2, y + 46, sub1, 8, SOFT)
    out += mono(x + w / 2, y + 60, sub2, 8, SOFT)
    return out


def fig08():
    """DreamFusion's score distillation loop, with what travels on every edge."""
    vw, vh = 960, 560
    body = eyebrow(40, 46, "score distillation sampling · one optimisation step of a nerf against a frozen 2-d model")
    nw, nh = 170, 76
    xs = [40, 276, 512, 748]
    top, low = 150, 344
    A, B, C, D = [(x, top) for x in xs]
    E, F = (748, low), (40, low)
    body += node2(*A, nw, nh, "NeRF θ", "MLP: point, direction", "→ colour, density", "input")
    body += node2(*B, nw, nh, "Render", "64 × 64 image", "at random camera c")
    body += node2(*C, nw, nh, "Add noise", "z_t = α_t x + σ_t ε", "t ~ U(0.02, 0.98)")
    body += node2(*D, nw, nh, "Frozen 2-D denoiser", "Imagen, 64 × 64", "guidance ω = 100", "focal")
    body += node2(*E, nw, nh, "Noise residual", "predicted noise", "minus added noise")
    body += node2(*F, nw, nh, "Update θ", "residual × ∂x/∂θ", "no U-Net Jacobian", "soft")
    mid = top + nh / 2
    for (x1, _), (x2, _), lab in ((A, B, "θ"), (B, C, "x, 64×64"), (C, D, "z_t")):
        body += h_arrow(x1 + nw + 2, mid, x2 - 2)
        body += mono((x1 + nw + x2) / 2, mid - 10, lab, 8, MUTED)
    body += v_arrow(D[0] + nw / 2, top + nh + 2, low - 2)
    body += mono(D[0] + nw / 2 - 10, (top + nh + low) / 2 + 3, "predicted noise", 8, MUTED, "end")
    nx = C[0] + nw / 2
    ey = low + nh / 2
    body += (f'<path d="M{nx},{top + nh + 2} V{ey - 8} Q{nx},{ey} {nx + 8},{ey} H{E[0] - 2}" '
             f'fill="none" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#arrow)"/>')
    body += mono(nx + 10, (top + nh + low) / 2 + 3, "added noise ε", 8, MUTED, "start")
    body += (f'<path d="M{E[0] + nw / 2},{low + nh + 2} V{low + nh + 30} H{F[0] + nw / 2} V{low + nh + 2}" '
             f'fill="none" stroke="{ACCENT}" stroke-width="1.4" marker-end="url(#arrow-a)"/>')
    body += mono((F[0] + E[0] + nw) / 2, low + nh + 48, "w(t) × residual, back through the renderer", 8, ACCENT)
    body += v_arrow(F[0] + nw / 2, low - 2, top + nh + 2, MUTED)
    body += mono(F[0] + nw / 2 + 10, (top + nh + low) / 2 + 3, "new θ", 8, MUTED, "start")
    body += mono(B[0] + nw / 2, 100, "a random camera each step", 8, SOFT)
    body += v_arrow(B[0] + nw / 2, 108, top - 2, SOFT)
    body += mono(D[0] + nw / 2, 100, "prompt + front / side / back view", 8, SOFT)
    body += v_arrow(D[0] + nw / 2, 108, top - 2, SOFT)
    body += mono(276, low + 30, "The 2-D model never sees the object:", 9, INK, "start")
    body += mono(276, low + 46, "only noisy renders go in, and only", 9, INK, "start")
    body += mono(276, low + 62, "a noise residual comes back.", 9, INK, "start")
    body += footnote(vh - 50, "After DreamFusion (Poole et al., ICLR 2023), Sections 2-3: guidance ω = 100, which is w = 101 "
                              "in this series; view text by camera.")
    body += footnote(vh - 32, "15,000 steps, about 1.5 hours per object on a 4-chip TPUv4. The residual is the predicted "
                              "noise minus the noise added.")
    emit(8, "score-distillation-loop", "The 2-D model never sees the object", "only noisy renders go in, a residual comes back",
         body, alt_checked("Score distillation loop: NeRF parameters, render at a random camera, add noise, frozen 2-D "
                           "denoiser with guidance, residual back"), vw, vh)


# -------------------------------------------------------------------- fig 09

def fig09():
    """SDS on crescent world against ancestral sampling: every run's contrast, and what SDS erases."""
    vw, vh = 960, 640
    D = cap()["sds"]
    Wt = D["weights"]
    real = D["real"]
    world = cap()["world"]
    weights = [float(w) for w in Wt]
    runs = [v for w in Wt for v in Wt[w]["sds"]["_contrast_runs"]]
    hi = max(runs + [Wt[w]["ancestral"]["_contrast_quantiles"]["0.95"] for w in Wt])
    assert hi < 2.75, hi
    ax = Axes(96, 96, 470, 400, (-0.1, math.log10(101) + 0.08), (0.2, 2.75))
    body = eyebrow(40, 46, f"crescent world, class 0 · score distillation with an identity renderer · {D['runs']} runs per "
                           f"weight, {D['iterations']:,} steps each")
    over, wk, (m0, m1) = world["over_threshold"], world["weak_threshold"], world["blend_band"]
    for lo, hi_, fill in ((wk, m0, "rgba(45,49,66,0.07)"), (m1, over, "rgba(45,49,66,0.07)"),
                          (over, 2.75, "rgba(235,108,54,0.07)")):
        body += rect(ax.x, ax.Y(hi_), ax.w, ax.Y(lo) - ax.Y(hi_), fill, "none", 0)
    body += ax.frame(xticks=[(math.log10(w), f"{w:g}") for w in weights],
                     yticks=[(v, f"{v:.1f}") for v in (0.5, 1.0, 1.5, 2.0, 2.5)],
                     xlabel="GUIDANCE WEIGHT w (LOG SCALE; DREAMFUSION'S ω = 100 IS w = 101)",
                     ylabel="CONTRAST (FRACTION OF A STRONG CRESCENT)")
    body += mono(ax.x + ax.w - 6, ax.Y((wk + m0) / 2) + 3, "REAL FAINT", 7, MUTED, "end", 500)
    body += mono(ax.x + ax.w - 6, ax.Y((m1 + over) / 2) + 3, "REAL STRONG", 7, MUTED, "end", 500)
    body += mono(ax.x + 10, ax.Y(2.62), f"ABOVE {over:.3f}: BRIGHTER THAN ANY REAL CRESCENT", 7, ACCENT, "start", 500)
    rng = lcg(9)
    for w in Wt:
        lx = math.log10(float(w))
        q = Wt[w]["ancestral"]["_contrast_quantiles"]
        px = ax.X(lx) + 15
        body += (f'<line x1="{px:.1f}" y1="{ax.Y(q["0.05"]):.1f}" x2="{px:.1f}" y2="{ax.Y(q["0.95"]):.1f}" '
                 f'stroke="{INK}" stroke-width="2.2"/>')
        body += f'<circle cx="{px:.1f}" cy="{ax.Y(q["0.5"]):.1f}" r="3.4" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>'
        for v in Wt[w]["sds"]["_contrast_runs"]:
            jx = ax.X(lx) - 3 + (next(rng) - 0.5) * 12
            body += f'<circle cx="{jx:.1f}" cy="{ax.Y(v):.1f}" r="1.7" fill="{ACCENT}" fill-opacity="0.45"/>'
    body += (f'<circle cx="112" cy="{vh - 89}" r="2.4" fill="{ACCENT}" fill-opacity="0.6"/>'
             + mono(122, vh - 86, "one SDS run (final image)", 8, MUTED, "start"))
    body += (f'<line x1="330" y1="{vh - 97}" x2="330" y2="{vh - 81}" stroke="{INK}" stroke-width="2.2"/>'
             f'<circle cx="330" cy="{vh - 89}" r="3.4" fill="{PAPER}" stroke="{INK}" stroke-width="1.6"/>'
             + mono(342, vh - 86, "ancestral samples: 5-95% range, median", 8, MUTED, "start"))
    # right panel: what SDS erases, at w = 1
    s1, a1 = Wt["1.0"]["sds"], Wt["1.0"]["ancestral"]
    rx, rw = 640, 280
    body += text(rx, 112, "What SDS erases, w = 1", 12, INK, SANS, 600, "start")
    metrics = [("brightness spread", real["brightness_sd"], a1["brightness_sd"], s1["brightness_sd"], ".3f"),
               ("pixel detail", real["detail_sd"], a1["detail_sd"], s1["detail_sd"], ".4f"),
               ("distance to nearest other", real["nearest_other_median"], a1["nearest_other_median"],
                s1["nearest_other_median"], ".3f")]
    yy = 140
    for name, rv, av, sv, fmt in metrics:
        top = max(rv, av, sv)
        body += mono(rx, yy, name.upper(), 7, MUTED, "start", 500)
        for j, (lab, v, colour) in enumerate((("real", rv, SOFT), ("ancestral", av, INK), ("SDS", sv, ACCENT))):
            by = yy + 10 + j * 13
            body += mono(rx, by + 7, lab, 7, SOFT, "start")
            body += rect(rx + 62, by, max(1.2, 150 * v / top), 8, colour, "none", 1)
            body += mono(rx + 62 + max(1.2, 150 * v / top) + 6, by + 7, format(v, fmt), 7, colour, "start")
        yy += 64
    body += mono(rx, yy + 6, "FOUR SDS RUNS, w = 1", 7, ACCENT, "start", 500)
    for j, img in enumerate(s1["_example"]):
        body += tile(rx + j * 52, yy + 14, 44, img)
    body += mono(rx, yy + 82, "FOUR ANCESTRAL SAMPLES, w = 1", 7, INK, "start", 500)
    for j, img in enumerate(a1["_example"]):
        body += tile(rx + j * 52, yy + 90, 44, img)
    body += footnote(vh - 50, f"Measured by beyond.py sds: SDS as in DreamFusion's equation 3 on the exact denoisers; "
                              f"ancestral = 128-step DDIM, {D['runs'] * 4:,} per weight.")
    body += footnote(vh - 32, "Bands: real faint and strong contrasts (mean ± 3 spreads). Tiles share one display range, "
                              "bright = high.")
    emit(9, "sds-on-crescent-world", "SDS returns modes, not samples",
         "every run agrees from w = 2, and guidance pushes contrast past the real range", body,
         alt_checked(f"SDS on crescent world: contrast and spread of {D['runs']} runs per guidance weight against ancestral "
                     "samples; SDS collapses and saturates"), vw, vh)


# -------------------------------------------------------------------- fig 10

def fig10():
    """MVDream's Figure 1, as published: cropped from the arXiv v4 PDF (page 2) at 400 dpi, caption excluded.

    pdftoppm -r 400 -f 2 -l 2 -x 556 -y 333 -W 2444 -H 442 -png 2308.16512v4.pdf crop, then trimmed to the
    figure's own extent plus 24 px of white; nothing inside the figure is changed."""
    png = HERE / "fig-10-janus-and-content-drift.png"
    if not png.exists():
        raise SystemExit("extract MVDream's Figure 1 to fig-10-janus-and-content-drift.png first (see the docstring)")
    print(f"kept fig-10-janus-and-content-drift (source, unchanged; sha1 {hashlib.sha1(png.read_bytes()).hexdigest()[:12]})")
    alt_checked("MVDream's Figure 1: a generated horse with two faces across four views, and fried chicken that turns "
                "into waffles across views")


# -------------------------------------------------------------------- fig 11

def fig11():
    """Forecasting crescent clips from their first frames: replacement against exact conditioning."""
    vw, vh = 960, 560
    F = cap()["forecast"]
    O = F["observed"]
    body = eyebrow(40, 46, f"crescent world in motion · predict the rest of {F['n']:,} real clips from their first frames · "
                           "joint model")
    ax = Axes(96, 104, 420, 300, (0.4, 3.6), (0.0, 1.0))
    body += ax.frame(xticks=[(k, f"{k} observed") for k in (1, 2, 3)],
                     yticks=[(v, f"{int(100 * v)}%") for v in (0, 0.25, 0.5, 0.75, 1.0)],
                     ylabel="COHERENT CLIPS")
    for k in (1, 2, 3):
        rep, ex = O[str(k)]["replacement"]["coherent_clips"], O[str(k)]["exact"]["coherent_clips"]
        for off, v, colour in ((-0.18, rep, ACCENT), (0.18, ex, INK)):
            x = ax.X(k + off) - 20
            body += rect(x, ax.Y(v), 40, ax.Y(0) - ax.Y(v), colour, "none", 2)
            body += mono(x + 20, ax.Y(v) - 7, pct(v), 9, colour, weight=600)
    body += swatch_row(96, 470, (("replacement: observed frames forced into the noisy input", ACCENT),
                                      ("exact conditioning", INK)))
    # right: what replacement gets wrong from one frame
    r1 = O["1"]["replacement"]
    rx = 600
    body += text(rx, 118, "Replacement from 1 frame", 12, INK, SANS, 600, "start")
    items = [("motion continues", r1["continues_motion"]), ("contrast kept", r1["keeps_contrast"]),
             ("brightness kept", r1["keeps_brightness"]), ("frames valid", r1["valid_frames"])]
    yy = 146
    for name, v in items:
        body += mono(rx, yy + 7, name, 8, MUTED, "start")
        body += rect(rx + 118, yy, 160, 9, PAPER2, "none", 2)
        body += rect(rx + 118, yy, 160 * v, 9, ACCENT, "none", 2)
        body += mono(rx + 286, yy + 8, pct(v), 8, ACCENT, "start", 600)
        yy += 24
    # an example: the first replacement forecast whose brightness jumps
    ex = r1["_example"]
    pick = max(range(len(ex)), key=lambda i: abs(frame_mean(ex[i][1]) - frame_mean(ex[i][0])))
    clip = ex[pick]
    jump = frame_mean(clip[1]) - frame_mean(clip[0])
    ty = 278
    body += mono(rx, ty - 10, "AN EXAMPLE FORECAST", 7, MUTED, "start", 500)
    for f, fr in enumerate(clip):
        body += tile(rx + f * 58, ty, 50, fr, stroke=INK if f == 0 else RULE_SOLID, sw=2 if f == 0 else 0.8)
        body += mono(rx + f * 58 + 25, ty + 64, "given" if f == 0 else f"frame {f + 1}", 7, INK if f == 0 else SOFT)
    body += mono(rx, ty + 88, f"brightness {'drops' if jump < 0 else 'rises'} by {abs(jump):.2f} after the given frame",
                 8, ACCENT, "start")
    body += mono(rx, ty + 102, f"(real clips keep it within {cap()['video']['bright_tol']:g})", 8, MUTED, "start")
    body += footnote(vh - 50, "Measured by beyond.py forecast: replacement re-noises the true frames at every DDIM step; exact "
                              "conditioning samples the true")
    body += footnote(vh - 32, "posterior of the rest of the clip given the observed frames. Coherent: every frame real, one "
                              "steady turn, one contrast, no flicker.")
    reps = [O[str(k)]["replacement"]["coherent_clips"] for k in (1, 2, 3)]
    emit(11, "forecasting-by-replacement", "Conditioning must reach the model, not just its input",
         "replacement lets the guesses for missing frames outvote the evidence", body,
         alt_checked(f"Coherent forecasts from 1, 2 or 3 observed frames: replacement {100 * reps[0]:.0f}%, "
                     f"{100 * reps[1]:.0f}%, {100 * reps[2]:.0f}% against exact conditioning 99% at every count"), vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    S = cap()["video"]["schemes"]
    body = eyebrow(72, 73, "diffusion · part ten")
    body += text(72, 148, "Diffusion beyond images", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "video, audio, 3-D, molecules and time series", 15, MUTED, MONO, 400, "start")
    size, gap = 96, 14
    for row, (key, name) in enumerate((("joint", "ONE DENOISER FOR THE WHOLE CLIP"), ("independent", "ONE FRAME AT A TIME"))):
        y = 262 + row * 150
        body += mono(624, y - 14, name, 9, ACCENT if row == 0 else MUTED, "start", 500)
        for f, fr in enumerate(S[key]["_example"][0]):
            body += tile(624 + f * (size + gap), y, size, fr)
    body += mono(72, 300, "the noise step adds the same Gaussian", 11, MUTED, "start")
    body += mono(72, 320, "to any list of numbers;", 11, MUTED, "start")
    body += mono(72, 352, "frames, points, angles and samples", 11, MUTED, "start")
    body += mono(72, 372, "differ in what the denoiser must know", 11, MUTED, "start")
    body += f'<line x1="72" y1="528" x2="1128" y2="528" stroke="{RULE}" stroke-width="1"/>'
    body += text(72, 568, "Every frame right is not the same as the video right.", 20, MUTED, SERIF, 400, "start", italic=True)
    emit_cover(body, alt_checked("Four frames of a crescent turning a quarter turn each, above four frames sampled one at a "
                                 "time that flicker and jump"))


FIGURES = {1: fig01, 2: fig02, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07, 8: fig08, 9: fig09, 10: fig10,
           11: fig11}

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if not args:
        for f in FIGURES.values():
            f()
        cover()
    for arg in args:
        cover() if arg == "cover" else FIGURES[int(arg)]()
