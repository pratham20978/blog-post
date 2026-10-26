#!/usr/bin/env python3
"""Figures for "Few-Step Diffusion and Distillation: 20 Steps Into 1" (diffusion-models, part 7).

Every measured or computed number drawn here is read from ../lab/captures.json, the capture that the
article's lab download ships, so the prose, the figures and the lab cannot drift apart. Numbers quoted
from papers (iCT's Table 3, the shortcut-model paper's Table 1) are typed once, below, next to their
ledger keys.

    python3 _figures.py            # all placed/plot/chart figures plus the cover
    python3 _figures.py 3 5        # just those
    python3 _figures.py cover      # just the cover
Figure 2 is Mermaid (python3 _mermaid.py).
"""

from __future__ import annotations

import json
import math
import os
import pathlib

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUSTARD, MUTED, PAPER, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, ascii_upper, emit, emit_cover, eyebrow, mono, node, rect, subtext, text,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP_PATH = pathlib.Path(os.environ.get("P7_CAPTURES", HERE.parent / "lab" / "captures.json"))
PURPLE = "#8a5a9e"
_CAP = None


def cap():
    global _CAP
    if _CAP is None:
        _CAP = json.loads(CAP_PATH.read_text(encoding="utf-8"))
    return _CAP


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


def minus(v):
    return str(v).replace("-", "−")


def pct(v, digits=1):
    return f"{100 * v:.{digits}f}%"


# ------------------------------------------------------------------ quoted data

ICT_T3 = {  # L57: Song & Dhariwal (iCT), Table 3 — class-conditional ImageNet 64x64: (steps, FID, precision, recall)
    "EDM teacher, Heun": [(79, 2.44, 0.71, 0.67)],
    "progressive distillation": [(1, 15.39, 0.59, 0.62), (2, 8.95, 0.63, 0.65), (4, 6.77, 0.66, 0.65)],
    "consistency distillation": [(1, 6.20, 0.68, 0.63), (2, 4.70, 0.69, 0.64)],
    "consistency training": [(1, 13.0, 0.71, 0.47), (2, 11.1, 0.69, 0.56)],
    "iCT-deep": [(1, 3.25, 0.72, 0.63), (2, 2.77, 0.74, 0.62)],
    "BigGAN-deep (a GAN)": [(1, 4.06, 0.79, 0.48)],
}

SHORTCUT_T1 = {  # L42: Frans et al. (shortcut models), Table 1 — FID-50k at 128 / 4 / 1 steps, DiT-B, one codebase.
    # A value in parentheses in the paper (the objective is not meant for that budget) is stored negative.
    "CelebA-HQ 256": {"flow matching": [7.3, -63.3, -280.5], "progressive distillation": [-302.9, -251.3, 14.8],
                      "consistency distillation": [59.5, 39.6, 38.2], "consistency training": [53.7, 19.0, 33.2],
                      "reflow": [16.1, 18.4, 23.2], "shortcut model": [6.9, 13.8, 20.5]},
    "ImageNet 256": {"flow matching": [17.3, -108.2, -324.8], "progressive distillation": [-201.9, -142.5, 35.6],
                     "consistency distillation": [132.8, 98.01, 136.5], "consistency training": [42.8, 43.0, 69.7],
                     "reflow": [16.9, 32.8, 44.8], "shortcut model": [15.5, 28.3, 40.3]},
}

METHOD_COLOUR = {"progressive distillation": BLUE, "consistency distillation": PURPLE, "consistency training": SAGE,
                 "iCT-deep": MUSTARD, "BigGAN-deep (a GAN)": LINK, "EDM teacher, Heun": INK,
                 "flow matching": INK, "reflow": MUSTARD, "shortcut model": ACCENT}


# -------------------------------------------------------------------- fig 06

def fig06():
    """The distribution-matching update, with the critic's own loop."""
    vw, vh = 960, 600
    body = eyebrow(40, 36, "one generator update in dmd · the fake denoiser trains on the generator's own samples in between")
    # row A: noise -> generator -> sample
    body += node(56, 78, 140, 60, "noise z", "64 PIXELS, N(0, I)", "input")
    body += node(262, 70, 220, 76, "generator G", "ONE CALL AT σ = 80", "focal")
    body += node(548, 78, 170, 60, "sample x = G(z)", "ONE 8×8 IMAGE")
    body += path_line([(196, 108), (260, 108)], MUTED)
    body += tag(229, 101, "z", MUTED, "middle", 8, bg=False)
    body += path_line([(482, 108), (546, 108)], MUTED)
    body += tag(514, 101, "x", MUTED, "middle", 8, bg=False)
    # row B: noised sample
    body += node(508, 202, 250, 64, "noised sample x_σ = x + σε", "σ RANDOM IN [0.02, 80]")
    body += path_line([(633, 138), (633, 200)], MUTED)
    body += mono(642, 174, "ADD NOISE", 7, SOFT, "start", 500)
    # row C: the two denoisers
    body += node(318, 324, 250, 68, "fake denoiser D_fake", "TRAINED ON G'S SAMPLES", "soft")
    body += node(640, 324, 260, 68, "real denoiser D_real", "THE FROZEN TEACHER (EXACT HERE)", "link")
    body += path_line([(590, 266), (590, 290), (443, 290), (443, 322)], MUTED)
    body += path_line([(676, 266), (676, 290), (770, 290), (770, 322)], MUTED)
    body += tag(516, 286, "x_σ", MUTED, "middle", 8, bg=True)
    body += tag(726, 286, "x_σ", MUTED, "middle", 8, bg=True)
    # row D: the update
    body += node(318, 470, 582, 64, "g = (D_fake − D_real) ÷ mean|D_real − x|",
                 "MOVE x TOWARD THE DATA AND AWAY FROM WHERE G ALREADY PUTS SAMPLES", "focal")
    body += path_line([(443, 392), (443, 468)], MUTED)
    body += path_line([(770, 392), (770, 468)], LINK)
    body += tag(452, 432, "D_FAKE(x_σ)", MUTED, "start", 8)
    body += tag(779, 432, "D_REAL(x_σ)", LINK, "start", 8)
    # the update returns through G's weights
    body += path_line([(318, 502), (150, 502), (150, 170), (300, 170), (300, 148)], ACCENT, 1.4, accent=True)
    body += tag(158, 330, "−g, BACK", ACCENT, "start", 8)
    body += tag(158, 346, "THROUGH G", ACCENT, "start", 8)
    # the critic's own loop: G's samples, detached, train the fake denoiser
    body += path_line([(570, 138), (570, 160), (360, 160), (360, 322)], SOFT, 1.2, dashed=True)
    body += tag(352, 216, "G'S SAMPLES,", MUTED, "end", 8)
    body += tag(352, 232, "DETACHED: A DENOISING", MUTED, "end", 8)
    body += tag(352, 248, "LOSS, 5 UPDATES PER", MUTED, "end", 8)
    body += tag(352, 264, "G UPDATE IN DMD2", MUTED, "end", 8)
    body += footnote(vh - 38, "DMD adds a regression loss on teacher noise-image pairs to G's update; DMD2 drops it, "
                              "updates D_fake five times per G update,")
    body += footnote(vh - 22, "and adds a GAN loss on real images. Weighting from Yin et al. 2024, Eqs. 7–8.")
    emit(6, "the-dmd-update", "The distribution-matching update",
         "Two denoisers read the same noised sample; their difference is the direction to move it", body,
         "DMD's update: generator output is noised, read by the frozen teacher and by a fake denoiser trained on "
         "the generator's samples; their difference moves G", vw, vh)


# -------------------------------------------------------------------- fig 09

def fig10():
    """Published precision against recall on one benchmark, from one paper's table."""
    vw, vh = 960, 560
    body = eyebrow(40, 36, "quoted from ict (iclr 2024), table 3 · class-conditional imagenet 64×64")
    ax = Axes(110, 78, 500, 380, (0.43, 0.70), (0.565, 0.81))
    body += ax.frame([(v / 100, f"{v / 100:.2f}") for v in range(45, 71, 5)],
                     [(v / 100, f"{v / 100:.2f}") for v in range(58, 82, 4)],
                     "RECALL  (SHARE OF REAL IMAGES THE SAMPLES COVER)", "PRECISION  (SHARE OF SAMPLES THAT LOOK REAL)")
    t_steps, t_fid, t_p, t_r = ICT_T3["EDM teacher, Heun"][0]
    body += ax.vline(t_r, INK, True, 0.8) + ax.hline(t_p, INK, True, 0.8)
    offsets = {  # where each step number sits relative to its dot, clear of the lines
        ("progressive distillation", 1): (-12, 4), ("progressive distillation", 2): (12, 12),
        ("progressive distillation", 4): (12, 4),
        ("consistency distillation", 1): (-12, 4), ("consistency distillation", 2): (12, 4),
        ("consistency training", 1): (-12, -6), ("consistency training", 2): (0, 18),
        ("iCT-deep", 1): (12, 4), ("iCT-deep", 2): (-12, 4),
        ("BigGAN-deep (a GAN)", 1): (12, 4), ("EDM teacher, Heun", 79): (12, 16),
    }
    for name, rows in ICT_T3.items():
        col = METHOD_COLOUR[name]
        if len(rows) > 1:
            body += ax.path([(r, p) for _, _, p, r in rows], col, 1.4, True)
        for steps, fid, p, r in rows:
            teacher = name.startswith("EDM")
            body += ax.dot(r, p, 6 if teacher else 4.5, col, hollow=teacher)
            dx, dy = offsets[(name, steps)]
            label = "TEACHER" if teacher else str(steps)
            body += text(ax.X(r) + dx, ax.Y(p) + dy, label, 9, col, MONO, 600, "middle" if dx == 0 else ("start" if dx > 0 else "end"))
    lx, ly = 650, 92
    body += mono(lx, ly, "METHOD · FID AT EACH STEP COUNT", 8, SOFT, "start", 500)
    rows_txt = {
        "EDM teacher, Heun": "79 calls: 2.44",
        "progressive distillation": "1: 15.39 · 2: 8.95 · 4: 6.77",
        "consistency distillation": "1: 6.20 · 2: 4.70",
        "consistency training": "1: 13.0 · 2: 11.1",
        "iCT-deep": "1: 3.25 · 2: 2.77",
        "BigGAN-deep (a GAN)": "1: 4.06",
    }
    for i, name in enumerate(ICT_T3):
        y = ly + 26 + i * 34
        teacher = name.startswith("EDM")
        body += (f'<circle cx="{lx + 6}" cy="{y - 3}" r="4.5" fill="{PAPER if teacher else METHOD_COLOUR[name]}" '
                 f'stroke="{METHOD_COLOUR[name]}" stroke-width="1.6"/>')
        body += mono(lx + 18, y, name, 8, INK, "start", 500)
        body += mono(lx + 18, y + 14, rows_txt[name], 8, MUTED, "start")
    body += mono(lx, ly + 252, "DASHED LINES: THE TEACHER'S PRECISION AND RECALL", 7, SOFT, "start", 500)
    body += mono(lx, ly + 268, "BELOW THEM: LESS FIDELITY (BLUR, ARTEFACTS)", 7, SOFT, "start")
    body += mono(lx, ly + 284, "LEFT OF THEM: LESS COVERAGE (LOST MODES)", 7, SOFT, "start")
    body += footnote(vh - 38, "Most rows are taken by iCT's authors from earlier papers; progressive distillation's row "
                              "is their re-implementation (ℓ2 loss).")
    body += footnote(vh - 22, "Precision and recall as defined by Kynkäänniemi et al. 2019. Song & Dhariwal 2024, Table 3.")
    emit(10, "precision-against-recall", "Which metric shows the damage",
         "One-step students lose fidelity or coverage, and the two move separately", body,
         "Quoted precision against recall on ImageNet 64: one-step PD loses precision, consistency training and a "
         "GAN lose recall, iCT-deep sits near the teacher", vw, vh)


# -------------------------------------------------------------------- fig 10

def fig09():
    """The shortcut paper's controlled comparison: one architecture, one codebase, three budgets."""
    vw, vh = 960, 566
    body = eyebrow(40, 36, "quoted from frans et al. (iclr 2025), table 1 · fid-50k, dit-b, every objective trained in one codebase")
    steps = [128, 4, 1]
    panels = [("CelebA-HQ 256", 96), ("ImageNet 256", 530)]
    for title, x0 in panels:
        ax = Axes(x0, 86, 340, 330, (-0.25, 2.25), (math.log10(5), math.log10(400)), logy=True)
        body += mono(x0, 68, ascii_upper(title), 8, INK, "start", 600)
        body += ax.frame([(i, f"{s} STEP" + ("S" if s > 1 else "")) for i, s in enumerate(steps)],
                         [(v, str(v)) for v in (5, 10, 20, 50, 100, 200)], "SAMPLING BUDGET", "FID  (LOG)" if x0 < 300 else "")
        for name, vals in SHORTCUT_T1[title].items():
            col = METHOD_COLOUR[name]
            pts = [(i, abs(v)) for i, v in enumerate(vals)]
            body += ax.path(pts, col, 1.8 if name == "shortcut model" else 1.3, None if name == "shortcut model" else True)
            for i, v in enumerate(vals):
                body += ax.dot(i, abs(v), 4.5, col, hollow=v < 0)
    body += legend_row(96, 486, [("flow matching", INK, True), ("progressive distillation", BLUE, True),
                                 ("consistency distillation", PURPLE, True)], 14)
    body += legend_row(96, 506, [("consistency training", SAGE, True), ("reflow", MUSTARD, True),
                                 ("shortcut model", ACCENT, False)], 14)
    body += mono(620, 506, "HOLLOW: A BUDGET THE OBJECTIVE IS NOT MEANT FOR", 7, SOFT, "start")
    body += footnote(vh - 22, "Two rows omitted: plain diffusion and the authors' live reflow. Frans, Hafner, Levine & "
                              "Abbeel 2025, Table 1.")
    emit(9, "one-codebase-three-budgets", "One codebase, three budgets",
         "Progressive distillation wins at one step and cannot take many; the shortcut model gives up a little at one "
         "step and keeps every budget", body,
         "Quoted FIDs at 128, 4 and 1 steps for six training objectives on CelebA-HQ and ImageNet 256: the shortcut "
         "model stays low at every budget", vw, vh)



# ------------------------------------------------------------------ crescent world, for labelling samples

def _crescents(r=8, ss=8, a_c=0.9):
    """The lab's four crescents in pure Python (distill.py's crescent_shapes), to tell which one a sample shows."""
    n = r * ss
    g = [(i + 0.5) / n for i in range(n)]
    m = [[1.0 if ((g[j] - 0.5) ** 2 + (g[i] - 0.5) ** 2 < 0.36 ** 2 and not ((g[j] - 0.64) ** 2 + (g[i] - 0.42) ** 2 < 0.30 ** 2))
          else 0.0 for j in range(n)] for i in range(n)]
    base = [[sum(m[a * ss + u][b * ss + v] for u in range(ss) for v in range(ss)) / ss ** 2 for b in range(r)] for a in range(r)]
    out = []
    cur = base
    for k in range(4):
        flat = [v for row in cur for v in row]
        mean = sum(flat) / len(flat)
        flat = [v - mean for v in flat]
        rms = math.sqrt(sum(v * v for v in flat) / len(flat))
        out.append([v * a_c / rms for v in flat])
        cur = [[cur[j][r - 1 - i] for j in range(r)] for i in range(r)]       # numpy's rot90
    return out


MU = _crescents()


def crescent_of(img):
    mean = sum(img) / len(img)
    proj = [sum((v - mean) * mu for v, mu in zip(img, m)) for m in MU]
    return proj.index(max(proj))


def S(name, seed="1"):
    return cap()["students"][name][seed]


def mean_over_seeds(name, key, field):
    vals = [run["steps"][key][field] for run in cap()["students"][name].values() if key in run["steps"]]
    return sum(vals) / len(vals), min(vals), max(vals)


STUDENT_STYLE = {  # name -> (label, colour)
    "regression": ("direct regression", MUSTARD),
    "pd": ("progressive distillation", BLUE),
    "cd": ("consistency distillation", PURPLE),
    "shortcut": ("shortcut model", ACCENT),
    "dmd_1to1": ("DMD, 1:1 updates", SAGE),
    "dmd_5to1": ("DMD, 5:1 updates", LINK),
    "dmd_regression": ("DMD + regression loss", SOFT),
}


# -------------------------------------------------------------------- fig 01

def fig01():
    """The worked example's cliff: exact endpoint against starting noise, DDIM ramps, a fitted student."""
    vw, vh = 960, 520
    W = cap()["worked"]
    a = W["a"]
    M = W["map"]
    body = eyebrow(40, 36, "one number between two opposite crescents · where each starting noise ends")
    left = Axes(96, 78, 400, 320, (-3, 3), (-5.9, 5.9))
    right = Axes(590, 78, 330, 320, (-0.05, 0.05), (-5.9, 5.9))
    for ax, xt in ((left, [(v, minus(f"{v:g}")) for v in (-3, -2, -1, 0, 1, 2, 3)]),
                   (right, [(v, minus(f"{v:g}")) for v in (-0.04, -0.02, 0, 0.02, 0.04)])):
        body += rect(ax.x, ax.Y(a / 2), ax.w, ax.Y(-a / 2) - ax.Y(a / 2), ACCENT_TINT, "none", 0)
        body += ax.frame(xt, [(v, minus(f"{v:g}")) for v in (-5, -2.5, 0, 2.5, 5)],
                         "STARTING NOISE ε  (x = 80ε AT σ = 80)", "WHERE THE SAMPLE ENDS" if ax is left else "")
        body += ax.hline(a, SOFT, True, 0.8) + ax.hline(-a, SOFT, True, 0.8)
    body += mono(left.x + 8, left.Y(a) - 6, f"CRESCENT +{a:.2f}", 7, SOFT, "start")
    body += mono(left.x + left.w - 8, left.Y(-a) + 13, f"CRESCENT −{a:.2f}", 7, SOFT, "end")
    body += mono(left.x + left.w - 8, left.Y(-a / 2) - 8, "BETWEEN THE CRESCENTS", 7, ACCENT, "end", 500)
    eps = M["eps"]
    neg = [i for i, e in enumerate(eps) if e < 0]
    pos = [i for i, e in enumerate(eps) if e > 0]
    for key, col, width, dash in (("ddim1", SOFT, 1.6, None), ("ddim2", BLUE, 1.6, True), ("ddim4", SAGE, 1.6, True)):
        pts = [(eps[i], M[key][i]) for i in neg + pos]
        body += left.path(pts, col, width, dash)
        body += right.path([(e, v) for e, v in pts if abs(e) <= 0.06], col, width, dash)
    for ax in (left, right):            # the exact map: two branches and the jump between them
        body += ax.path([(eps[i], M["exact"][i]) for i in neg], INK, 2.4)
        body += ax.path([(eps[i], M["exact"][i]) for i in pos], INK, 2.4)
        body += ax.path([(0, M["exact"][neg[-1]]), (0, M["exact"][pos[0]])], INK, 1.0, "dot")
    st = W["student_1d"]
    body += right.path([(e, v) for e, v in st["curve"] if abs(e) <= 0.06], ACCENT, 2.2)
    lo, hi = st["ramp"]
    yb = right.Y(5.62)
    body += path_line([(right.X(lo), yb), (right.X(hi), yb)], ACCENT, 1.2, arrow=False)
    for xx in (lo, hi):
        body += path_line([(right.X(xx), yb - 5), (right.X(xx), yb + 5)], ACCENT, 1.2, arrow=False)
    body += mono(right.X(hi) + 8, yb + 3, f"RAMP {minus(f'{lo:.3f}')} TO +{hi:.3f}", 7, ACCENT, "start", 500)
    body += mono(left.x, 66, "ε FROM −3 TO 3", 8, INK, "start", 600)
    body += mono(right.x, 66, "ZOOM: ε FROM −0.05 TO 0.05", 8, INK, "start", 600)
    body += legend_row(96, 446, [("exact path", INK, False), ("DDIM, 1 call", SOFT, False),
                                 ("DDIM, 2 calls", BLUE, True), ("DDIM, 4 calls", SAGE, True),
                                 ("network fitted to the exact ends", ACCENT, False)], 12)
    body += footnote(vh - 38, "Computed by the lab. The student is a network with two hidden layers of 64 units, fitted by "
                              "least squares to 200,000 exact endpoints.")
    body += footnote(vh - 22, "Shaded band: closer to the midpoint than to either crescent.")
    emit(1, "the-cliff", "Where each starting noise ends",
         "The exact map is a step; every smooth approximation of it is a ramp", body,
         f"Endpoint against starting noise between two crescents: the exact map jumps from −{W['exact_pm'][0]:.2f} to "
         f"+{W['exact_pm'][0]:.2f} at zero; DDIM and a fitted network are ramps", vw, vh)


# -------------------------------------------------------------------- fig 03

def _solver_series(name, field):
    sol = cap()["reference"]["solvers"][name]
    return [(int(k), v[field]) for k, v in sorted(sol.items(), key=lambda kv: int(kv[0]))]


def fig03():
    """Progressive distillation's students against solvers with the exact denoiser, at matched calls."""
    vw, vh = 960, 540
    R = cap()["reference"]
    floor = R["swd_floor"]
    body = eyebrow(40, 36, "each point: 4,096 shared starting noises · solvers use the exact denoiser · students are trained networks")
    lx = Axes(96, 84, 360, 320, (math.log10(0.8), math.log10(160)), (math.log10(0.03), math.log10(0.9)), logx=True, logy=True)
    rx = Axes(570, 84, 350, 320, (math.log10(0.8), math.log10(160)), (-0.02, 1.02), logx=True)
    calls = [(v, str(v)) for v in (1, 2, 4, 8, 16, 32, 64, 128)]
    body += lx.frame(calls, [(v, f"{v:g}") for v in (0.03, 0.05, 0.1, 0.2, 0.5)], "NETWORK CALLS PER SAMPLE  (LOG)",
                     "SAMPLE DISTANCE TO THE DATA  (LOG)")
    body += rx.frame(calls, [(v, f"{round(100 * v)}%") for v in (0, 0.25, 0.5, 0.75, 1.0)], "NETWORK CALLS PER SAMPLE  (LOG)",
                     "SAMPLES THAT ARE BLENDS")
    body += mono(lx.x, 70, "THE SET: SLICED WASSERSTEIN DISTANCE", 8, INK, "start", 600)
    body += mono(rx.x, 70, "BLENDS: SHAPE BETWEEN TWO CRESCENTS", 8, INK, "start", 600)
    body += lx.hline(floor, SOFT, True, 0.9)
    body += tag(lx.x + lx.w - 4, lx.Y(floor) - 6, f"TWO REAL SETS: {floor:.3f}", SOFT, "end", 7)
    teacher = cap()["teacher"]["ddim"]
    series = [
        ("DDIM, exact denoiser", INK, True, _solver_series("ddim", "swd"), _solver_series("ddim", "blend")),
        ("DPM-Solver++(2M), exact denoiser", MUTED, "dot", _solver_series("dpmpp2m", "swd"), _solver_series("dpmpp2m", "blend")),
        ("DDIM, network teacher", SOFT, True, [(int(k), v["swd"]) for k, v in sorted(teacher.items(), key=lambda kv: int(kv[0]))],
         [(int(k), v["blend"]) for k, v in sorted(teacher.items(), key=lambda kv: int(kv[0]))]),
    ]
    pd = sorted(cap()["students"]["pd"]["1"]["steps"], key=int)
    pd_swd = [(int(n), mean_over_seeds("pd", n, "swd")[0]) for n in pd]
    pd_bl = [(int(n), mean_over_seeds("pd", n, "blend")[0]) for n in pd]
    series.append(("progressive distillation, one student per count", BLUE, False, pd_swd, pd_bl))
    for label, col, dash, s1, s2 in series:
        body += lx.path(s1, col, 2.2 if col == BLUE else 1.5, dash if col != BLUE else None)
        body += rx.path(s2, col, 2.2 if col == BLUE else 1.5, dash if col != BLUE else None)
        for p in s1:
            body += lx.dot(p[0], p[1], 3.4 if col == BLUE else 2.4, col)
        for p in s2:
            body += rx.dot(p[0], p[1], 3.4 if col == BLUE else 2.4, col)
    reg = mean_over_seeds("regression", "1", "swd")[0], mean_over_seeds("regression", "1", "blend")[0]
    body += lx.dot(1, reg[0], 5, MUSTARD, hollow=True) + rx.dot(1, reg[1], 5, MUSTARD, hollow=True)
    body += legend_row(96, 462, [("DDIM, exact denoiser", INK, True), ("DPM-Solver++(2M), exact", MUTED, "dot"),
                                 ("DDIM, network teacher", SOFT, True)], 12)
    body += legend_row(96, 480, [("progressive distillation", BLUE, False)], 12)
    body += (f'<circle cx="{330}" cy="{476}" r="5" fill="{PAPER}" stroke="{MUSTARD}" stroke-width="1.6"/>'
             + mono(342, 480, "direct regression, one call", 8, MUTED, "start"))
    body += footnote(vh - 22, "Students: mean of two seeds. Progressive distillation starts from 64 DDIM steps with the "
                              "exact denoiser and halves six times.")
    emit(3, "students-against-solvers", "Students against solvers at matched calls",
         "Below eight calls a distilled student beats any solver, even one with the exact denoiser", body,
         "Sample distance and blend share against network calls: DDIM and DPM-Solver++ with the exact denoiser against "
         "progressive distillation's students", vw, vh)


# -------------------------------------------------------------------- fig 04

def fig04():
    """One-call samples near and far from a decision, against the exact endpoints."""
    vw, vh = 960, 700
    SM = cap()["samples"]
    rows = [("exact path", "exact"), ("DDIM, 1 call", "ddim_1"), ("DDIM, 4 calls", "ddim_4"),
            ("direct regression, 1 call", "regression_1"), ("progressive distillation, 1 call", "pd_1"),
            ("consistency distillation, 1 call", "cd_1"), ("shortcut model, 1 call", "shortcut_1"),
            ("DMD, 5:1 updates, 1 call", "dmd_5to1_1"), ("DMD + regression loss, 1 call", "dmd_regression_1")]
    body = eyebrow(40, 36, "six starting noises: three within 0.002 of a decision boundary, three far from one")
    size, gap, x0, y0 = 50, 10, 330, 92
    for j in range(6):
        cx = x0 + j * (size + gap) + (24 if j >= 3 else 0)
        body += mono(cx + size / 2, y0 - 12, f"{SM['margin'][j]:.3f}", 7, SOFT)
    body += mono(x0 + 1.5 * (size + gap) - gap / 2, y0 - 30, "NEAR A BOUNDARY (MARGIN)", 8, INK, "middle", 600)
    body += mono(x0 + 4.5 * (size + gap) + 24 - gap / 2, y0 - 30, "FAR FROM ONE (MARGIN)", 8, INK, "middle", 600)
    exact_k = [crescent_of(img) for img in SM["exact"]]
    for i, (label, key) in enumerate(rows):
        y = y0 + i * (size + gap)
        body += text(40, y + size / 2 + 4, label, 11, INK, SANS, 500, "start")
        imgs = SM["exact"] if key == "exact" else SM["methods"][key]
        for j, img in enumerate(imgs):
            cx = x0 + j * (size + gap) + (24 if j >= 3 else 0)
            flip = key != "exact" and crescent_of(img) != exact_k[j]
            body += tile(cx, y, size, img, stroke=ACCENT if flip else RULE_SOLID, sw=2.4 if flip else 0.8)
    body += (f'<rect x="{x0 + 6 * (size + gap) + 40}" y="{y0}" width="14" height="14" fill="none" stroke="{ACCENT}" '
             f'stroke-width="2.4"/>' + mono(x0 + 6 * (size + gap) + 62, y0 + 11, "DIFFERENT CRESCENT", 7, ACCENT, "start", 500))
    body += mono(x0 + 6 * (size + gap) + 62, y0 + 24, "FROM THE EXACT PATH", 7, ACCENT, "start", 500)
    body += footnote(vh - 38, "Measured: seed 1 of each student, the same six noises from the lab's 4,096. Display range "
                              f"{minus(LO)} to {HI} for every tile, bright = high.")
    body += footnote(vh - 22, "Margin: the gap between a noise's two largest projections onto the crescent directions.")
    emit(4, "one-call-samples", "One call, near and far from a decision",
         "Far from a boundary every student draws the exact path's crescent; near one, they blend or pick another", body,
         "Eight-by-eight samples from six noises: exact endpoints, DDIM, and one-call students; near a decision some "
         "students blend or flip crescents", vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    """Flips and blends of one-call students, by how close the starting noise is to a decision boundary."""
    vw, vh = 960, 540
    C = cap()
    bins = C["margin_bins"]
    share = C["margin_share"]
    labels = ["<0.025", "0.025–0.05", "0.05–0.1", "0.1–0.2", "0.2–0.4", "0.4–0.8", ">0.8"]
    body = eyebrow(40, 36, "one-call students · 4,096 starting noises binned by their distance from a decision boundary")
    lx = Axes(96, 84, 360, 300, (-0.5, 6.5), (0, 0.3))
    rx = Axes(570, 84, 350, 300, (-0.5, 6.5), (0, 1.0))
    xt = [(i, labels[i]) for i in range(7)]
    body += lx.frame(xt, [(v, f"{round(100 * v)}%") for v in (0, 0.1, 0.2, 0.3)], "MARGIN OF THE STARTING NOISE",
                     "SHARE THAT FLIP")
    body += rx.frame(xt, [(v, f"{round(100 * v)}%") for v in (0, 0.25, 0.5, 0.75, 1.0)], "MARGIN OF THE STARTING NOISE",
                     "SHARE THAT ARE BLENDS")
    body += mono(lx.x, 70, "PAIRING: A DIFFERENT CRESCENT FROM THE EXACT PATH", 8, INK, "start", 600)
    body += mono(rx.x, 70, "SHAPE: BETWEEN TWO CRESCENTS", 8, INK, "start", 600)
    for i, s in enumerate(share):          # how many noises fall in each bin
        for ax in (lx, rx):
            bw = 22
            body += rect(ax.X(i) - bw / 2, ax.Y(s), bw, ax.Y(0) - ax.Y(s), "rgba(45,49,66,0.10)", "none", 0)
    for name in ("regression", "pd", "cd", "shortcut"):
        label, col = STUDENT_STYLE[name]
        f = [sum(r["steps"]["1"]["flip_by_margin"][i] for r in C["students"][name].values()) / len(C["students"][name])
             for i in range(7)]
        b = [sum(r["steps"]["1"]["blend_by_margin"][i] for r in C["students"][name].values()) / len(C["students"][name])
             for i in range(7)]
        body += lx.path(list(enumerate(f)), col, 1.8) + rx.path(list(enumerate(b)), col, 1.8)
        for i in range(7):
            body += lx.dot(i, f[i], 3, col) + rx.dot(i, b[i], 3, col)
    body += legend_row(96, 452, [(STUDENT_STYLE[n][0], STUDENT_STYLE[n][1], False) for n in ("regression", "pd", "cd", "shortcut")], 12)
    body += (rect(96, 466, 14, 10, "rgba(45,49,66,0.10)", "none", 0)
             + mono(116, 475, "GREY BARS: SHARE OF ALL STARTING NOISES IN THE BIN", 7, SOFT, "start"))
    body += footnote(vh - 22, "Measured: mean of two seeds per student. Margin: the gap between a noise's two largest "
                              "projections onto the crescent directions.")
    emit(5, "errors-live-at-decisions", "Errors live at the decisions",
         "Flips and blends concentrate in the few percent of noises that start next to a boundary", body,
         "Flip and blend shares of one-call students by margin bin, with the share of noises per bin; errors are "
         "concentrated at small margins", vw, vh)


# -------------------------------------------------------------------- fig 07

def fig07():
    """Crescent coverage over training for three distribution-matching variants, and their mean brightness."""
    vw, vh = 960, 760
    names = [("dmd_1to1", "DMD, 1:1 UPDATES"), ("dmd_5to1", "DMD, 5:1 UPDATES (DMD2'S RULE)"),
             ("dmd_regression", "DMD + REGRESSION LOSS, 1:1")]
    cols = [INK, ACCENT, BLUE, SAGE]
    body = eyebrow(40, 36, "1,024 fixed noises through the generator every 100 updates · seed 1 above, both seeds below")
    for p_, (name, title) in enumerate(names):
        tr = S(name)["trace"]
        steps = [r["step"] for r in tr]
        ax = Axes(80 + p_ * 300, 84, 250, 250, (0, max(steps)), (0, 1.0))
        body += mono(ax.x, 70, title, 8, INK, "start", 600)
        body += ax.frame([(v, f"{v:,}") for v in range(0, max(steps) + 1, 2000)],
                         [(v, f"{round(100 * v)}%" if p_ == 0 else "") for v in (0, 0.25, 0.5, 0.75, 1.0)],
                         "GENERATOR UPDATES", "SHARE OF SAMPLES" if p_ == 0 else "")
        body += ax.hline(0.25, SOFT, True, 0.8)
        for k in range(4):
            body += ax.path([(r["step"], r["cover"][k]) for r in tr], cols[k], 1.6)
        fin = S(name)["steps"]["1"]["cover"]
        body += mono(ax.x, ax.y + ax.h + 50, "FINAL, 4,096 NOISES: " + " / ".join(f"{v:.2f}" for v in fin), 8, MUTED, "start", 500)
    body += legend_row(80, 420, [(f"crescent {k + 1}", cols[k], False) for k in range(4)], 12)
    body += mono(600, 420, "DASHED: AN EVEN SHARE, 25%", 7, SOFT, "start")
    # brightness: the batch mean over training, both seeds of the two critic ratios
    bx = Axes(80, 470, 840, 170, (0, 8000), (-0.08, 0.09))
    body += mono(bx.x, 456, "MEAN BRIGHTNESS OF THE SAME 1,024 SAMPLES (THE DATA'S IS 0)", 8, INK, "start", 600)
    body += bx.frame([(v, f"{v:,}") for v in range(0, 8001, 1000)],
                     [(v, minus(f"{v:+.2f}" if v else "0")) for v in (-0.06, -0.03, 0, 0.03, 0.06, 0.09)],
                     "GENERATOR UPDATES", "")
    body += bx.hline(0, SOFT, True, 0.8)
    for name, col, dash in (("dmd_1to1", MUSTARD, None), ("dmd_5to1", PURPLE, None)):
        for seed in ("1", "2"):
            tr = S(name, seed)["trace"]
            body += bx.path([(r["step"], r["brightness_mean"]) for r in tr], col, 1.3, True if seed == "2" else None)
    body += legend_row(80, vh - 46, [("1:1 updates, seed 1", MUSTARD, False), ("seed 2", MUSTARD, True),
                                     ("5:1 updates, seed 1", PURPLE, False), ("seed 2", PURPLE, True)], 10)
    body += footnote(vh - 18, "Measured. The fake denoiser trains for 2,000 updates on the generator's first samples in all "
                              "three runs before the generator moves.")
    emit(7, "coverage-during-training", "Coverage during distribution matching",
         "Every run first piles onto one crescent; the pairs bring the others back fastest, and five critic updates steady "
         "the brightness", body,
         "Crescent coverage during DMD training: every run collapses onto one crescent by update 100, then recovers; "
         "brightness drifts less at 5:1", vw, vh)


# -------------------------------------------------------------------- fig 08

def fig08():
    """One network for every step count against one student per count."""
    vw, vh = 960, 540
    body = eyebrow(40, 36, "sample distance and pairing against calls · mean of two seeds")
    lx = Axes(96, 84, 360, 320, (math.log10(0.8), math.log10(160)), (math.log10(0.03), math.log10(0.2)), logx=True, logy=True)
    rx = Axes(570, 84, 350, 320, (math.log10(0.8), math.log10(160)), (-0.02, 1.02), logx=True)
    calls = [(v, str(v)) for v in (1, 2, 4, 8, 16, 32, 64, 128)]
    body += lx.frame(calls, [(v, f"{v:g}") for v in (0.03, 0.05, 0.1, 0.2)], "NETWORK CALLS PER SAMPLE  (LOG)",
                     "SAMPLE DISTANCE TO THE DATA  (LOG)")
    body += rx.frame(calls, [(v, f"{round(100 * v)}%") for v in (0, 0.25, 0.5, 0.75, 1.0)], "NETWORK CALLS PER SAMPLE  (LOG)",
                     "SHARE THAT FLIP")
    body += mono(lx.x, 70, "THE SET", 8, INK, "start", 600)
    body += mono(rx.x, 70, "PAIRING WITH THE EXACT PATH", 8, INK, "start", 600)
    floor = cap()["reference"]["swd_floor"]
    body += lx.hline(floor, SOFT, True, 0.9)
    body += tag(lx.x + lx.w - 4, lx.Y(floor) - 6, f"TWO REAL SETS: {floor:.3f}", SOFT, "end", 7)
    for name, dash in (("pd", True), ("cd", False), ("shortcut", False)):
        label, col = STUDENT_STYLE[name]
        keys = sorted(cap()["students"][name]["1"]["steps"], key=int)
        s1 = [(int(k), mean_over_seeds(name, k, "swd")[0]) for k in keys]
        s2 = [(int(k), mean_over_seeds(name, k, "flip")[0]) for k in keys]
        body += lx.path(s1, col, 2.0, dash) + rx.path(s2, col, 2.0, dash)
        for p in s1:
            body += lx.dot(p[0], p[1], 3.2, col)
        for p in s2:
            body += rx.dot(p[0], p[1], 3.2, col)
    body += legend_row(96, 462, [("progressive distillation, one student per count", BLUE, True),
                                 ("consistency model, multistep", PURPLE, False), ("shortcut model, one network", ACCENT, False)], 12)
    body += footnote(vh - 22, "Measured. The consistency model re-noises between calls to the ρ = 7 levels; the shortcut "
                              "model jumps along the same levels.")
    emit(8, "one-network-any-step-count", "One network for every step count",
         "The shortcut model improves with calls and keeps its pairing; the consistency model re-decides at every call", body,
         "Sample distance and flip share against calls for progressive distillation, a multistep consistency model and "
         "a shortcut model", vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    W = cap()["worked"]
    M = W["map"]
    a = W["a"]
    body = eyebrow(72, 73, "diffusion · part seven")
    body += text(72, 148, "Few-step diffusion and distillation", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "20 steps into 1 — and where one step breaks", 15, MUTED, MONO, 400, "start")
    ax = Axes(96, 248, 420, 200, (-0.05, 0.05), (-5.9, 5.9))
    body += rect(ax.x, ax.Y(a / 2), ax.w, ax.Y(-a / 2) - ax.Y(a / 2), ACCENT_TINT, "none", 0)
    body += ax.frame()
    eps = M["eps"]
    neg = [i for i, e in enumerate(eps) if e < 0]
    pos = [i for i, e in enumerate(eps) if e > 0]
    body += ax.path([(eps[i], M["exact"][i]) for i in neg], INK, 3)
    body += ax.path([(eps[i], M["exact"][i]) for i in pos], INK, 3)
    body += ax.path([(e, v) for e, v in W["student_1d"]["curve"] if abs(e) <= 0.06], ACCENT, 3)
    body += mono(ax.x, ax.y + ax.h + 24, "WHERE EACH NOISE ENDS: THE EXACT STEP AND A STUDENT'S RAMP", 9, MUTED, "start", 500)
    SM = cap()["samples"]
    size, gap = 64, 12
    x0, y0 = 640, 250
    rows = [("EXACT", SM["exact"]), ("1 CALL, DDIM", SM["methods"]["ddim_1"]), ("1 CALL, STUDENT", SM["methods"]["pd_1"])]
    for i, (lab, imgs) in enumerate(rows):
        y = y0 + i * (size + gap)
        body += mono(x0 - 12, y + size / 2 + 4, lab, 9, MUTED, "end", 500)
        for j in range(4):
            body += tile(x0 + j * (size + gap), y, size, imgs[j + 1])
    body += f'<line x1="72" y1="508" x2="1128" y2="508" stroke="{RULE}" stroke-width="1"/>'
    body += text(72, 548, "A student jumps to where the path ends, and stumbles where it decides.", 20, MUTED, SERIF, 400, "start", italic=True)
    emit_cover(body, "The exact endpoint as a step against a student's ramp, beside crescent samples from the exact path, "
                     "one DDIM call and a one-call student")


# keyed by the figure number that reaches the post; 2 is Mermaid
FIGURES = {1: fig01, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07, 8: fig08, 9: fig09, 10: fig10}

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
