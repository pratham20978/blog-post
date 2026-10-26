#!/usr/bin/env python3
"""Figures for "Discrete Diffusion Language Models: Masks, LLaDA, Samplers" (diffusion-models, part 11).

Every measured or computed number drawn here is read from ../lab/captures.json, the capture that the
article's lab download ships, so the prose, the figures and the lab cannot drift apart. Four figures carry
numbers from papers instead, each held once below with its ledger key: Figure 3 (SEDD's Table 1, L13),
Figure 7 (LLaDA's Table 1, L45), Figure 8 (LLaDA's Table 9, L37) and Figure 10's right panel (Zheng et al.'s
Table 2, L02); Figure 4's shapes are LLaDA's configuration (L09, L44). Figure 6 is the survey's own Figure 7
(source route), cropped from the arXiv v3 PDF without change; `python3 _figures.py 6` only checks it.

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

import numpy as np

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, MONO, MUSTARD, MUTED, PAPER, PAPER2, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, emit, emit_cover, eyebrow, h_arrow, lcg, mono, rect, subtext, text, v_arrow,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP_PATH = pathlib.Path(os.environ.get("P11_CAPTURES", HERE.parent / "lab" / "captures.json"))
BLOG = HERE.parent / "blog.md"
_CAP = None

QUOTED_SEDD = {  # Lou et al. 2024, Table 1: zero-shot perplexity, small models; diffusion values are bounds (L13)
    "LAMBADA": {"GPT-2": 45.04, "SEDD absorbing": 50.92, "SEDD uniform": 65.40, "D3PM": 93.47, "Plaid": 57.28},
    "WikiText2": {"GPT-2": 42.43, "SEDD absorbing": 41.84, "SEDD uniform": 50.27, "D3PM": 77.28, "Plaid": 51.80},
    "PTB": {"GPT-2": 138.43, "SEDD absorbing": 114.24, "SEDD uniform": 140.12, "D3PM": 200.82, "Plaid": 142.60},
    "WikiText103": {"GPT-2": 41.60, "SEDD absorbing": 40.62, "SEDD uniform": 49.60, "D3PM": 75.16, "Plaid": 50.86},
    "1BW": {"GPT-2": 75.20, "SEDD absorbing": 79.29, "SEDD uniform": 101.37, "D3PM": 138.92, "Plaid": 91.12},
}
QUOTED_LLADA = [  # Nie et al. 2025 (v3), Table 1: LLaDA 8B Base vs LLaMA3 8B Base, same protocol (L45)
    ("General", "MMLU", 5, 65.9, 65.4), ("General", "BBH", 3, 49.7, 62.1), ("General", "ARC-C", 0, 45.9, 53.1),
    ("General", "HellaSwag", 0, 70.5, 79.1), ("General", "TruthfulQA", 0, 46.1, 44.0),
    ("General", "WinoGrande", 5, 74.8, 77.3), ("General", "PIQA", 0, 73.6, 80.6),
    ("Math and science", "GSM8K", 4, 70.3, 48.7), ("Math and science", "Math", 4, 31.4, 16.0),
    ("Math and science", "GPQA", 5, 25.2, 25.9),
    ("Code", "HumanEval", 0, 35.4, 34.8), ("Code", "HumanEval-FIM", 2, 73.8, 73.3), ("Code", "MBPP", 4, 40.0, 48.8),
    ("Chinese", "CMMLU", 5, 69.9, 50.7), ("Chinese", "C-Eval", 5, 70.5, 51.7),
]
QUOTED_REMASK = [  # Nie et al. 2025 (v3), Table 9: LLaDA 8B Base, length and steps 256 (L37)
    ("BBH", 32.1, 45.0), ("GSM8K", 21.3, 70.0), ("Math", 9.2, 30.3), ("HumanEval", 11.6, 32.9), ("MBPP", 21.0, 40.2),
]
QUOTED_ZHENG = [  # Zheng et al. 2025, Table 2: 8 samples of 2,048 steps, only the sampling code changed (L02)
    ("32-bit", 31.24, 5.17), ("64-bit", 126.11, 5.66), ("64-bit, truncated like 32-bit", 28.64, 5.12),
]
LLADA = {"length": 4096, "vocab": 126464, "layers": 32, "width": 4096, "heads": 32, "params_b": 8.02}  # L09, L44


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


# ------------------------------------------------------------------ primitives (as in parts 8-10)

class Axes:
    """Data-to-pixel mapping for a real plot; logx/logy put an axis on log10 (pass raw values)."""

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

    def dot(self, a, b, r=4, colour=INK, hollow=False):
        if hollow:
            return (f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{PAPER}" '
                    f'stroke="{colour}" stroke-width="1.6"/>')
        return f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" fill="{colour}"/>'

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


def grey(v, lo, hi):
    """High value = bright: the series' display convention for patches and tokens."""
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


def num(v, digits=2):
    """Display a number with a real minus sign."""
    return f"{v:.{digits}f}".replace("-", "−")


def pct(v, digits=1):
    return f"{100 * v:.{digits}f}%"


HATCH = (f'<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
         f'patternTransform="rotate(45)"><rect width="6" height="6" fill="{PAPER2}"/>'
         f'<line x1="0" y1="0" x2="0" y2="6" stroke="{ACCENT}" stroke-width="2.2"/></pattern></defs>')


def tile(x, y, size, toks, mask=None, side=8, levels=28, stroke=RULE_SOLID, sw=0.8):
    """An 8x8 token image as greys (level 0 dark, top level bright); masked cells hatched."""
    rows = [[grey(toks[r * side + c], 0, levels - 1) for c in range(side)] for r in range(side)]
    out = (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
           f'preserveAspectRatio="none" style="image-rendering:pixelated"/>')
    if mask is not None:
        cs = size / side
        for i, m in enumerate(mask):
            if m:
                r, c = divmod(i, side)
                out += f'<rect x="{x + c * cs:.2f}" y="{y + r * cs:.2f}" width="{cs:.2f}" height="{cs:.2f}" fill="url(#hatch)"/>'
    return out + rect(x, y, size, size, "none", stroke, 0, sw)


def tok4(x, y, toks, cell=34, gap=4, mask=None, ring=(), size=13):
    """A 4x4 grid of grey-level tokens 0-3 with the level printed; masked cells hatched with an M."""
    out = ""
    for r in range(4):
        for c in range(4):
            cx, cy = x + c * (cell + gap), y + r * (cell + gap)
            if mask is not None and mask[r][c]:
                out += rect(cx, cy, cell, cell, "url(#hatch)", ACCENT, 2, 1.2)
                out += plate(cx + cell / 2 - 8, cy + cell / 2 - 8, 16, 16)
                out += mono(cx + cell / 2, cy + cell / 2 + 4, "M", 10, ACCENT, weight=600)
                continue
            v = toks[r][c]
            g = grey(v, 0, 3)
            out += rect(cx, cy, cell, cell, f"rgb({g},{g},{g})", ACCENT if (r, c) in ring else RULE_SOLID, 2,
                        2 if (r, c) in ring else 0.8)
            out += text(cx + cell / 2, cy + cell / 2 + size * 0.36, str(v), size, PAPER if v <= 1 else INK, MONO, 600)
    return out


def numgrid(x, y, rows, cw=50, ch=28, ring=(), size=9):
    out = ""
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            cx, cy = x + c * cw, y + r * ch
            is_ring = (r, c) in ring
            out += rect(cx, cy, cw - 4, ch - 4, ACCENT_TINT if is_ring else "#ffffff", ACCENT if is_ring else RULE_SOLID, 2,
                        1.4 if is_ring else 0.8)
            out += mono(cx + (cw - 4) / 2, cy + (ch - 4) / 2 + 3, num(v), size, ACCENT if is_ring else INK)
    return out


# -------------------------------------------------- the 72-image world, rebuilt only to mark validity

def world_images():
    """The lab's 72 images, rebuilt with the lab's arithmetic and checked against the capture's examples."""
    def crescent_shape(r=8, inner=(0.64, 0.42, 0.30), ss=8):
        g = (np.arange(r * ss) + 0.5) / (r * ss)
        yy, xx = np.meshgrid(g, g, indexing="ij")
        outer = (xx - 0.5) ** 2 + (yy - 0.5) ** 2 < 0.36 ** 2
        hole = (xx - inner[0]) ** 2 + (yy - inner[1]) ** 2 < inner[2] ** 2
        return (outer & ~hole).astype(float).reshape(r, ss, r, ss).mean(axis=(1, 3))

    def unit(m):
        m = m.reshape(-1) - m.mean()
        return m * 0.9 / np.sqrt((m ** 2).mean())
    mu = [unit(np.rot90(crescent_shape(), k)) for k in range(4)]
    b = 0.15 * (np.arange(9) - 4)
    imgs = [np.floor((a * mu[k] + bb) / 0.15 + 0.5).astype(int) for k in range(4) for a in (0.5, 1.0) for bb in b]
    lo = min(i.min() for i in imgs)
    imgs = {tuple((i - lo).tolist()) for i in imgs}
    W = cap()["world"]
    for ex in W["examples"]["turn0_strong_by_level"] + W["examples"]["middle_level"]:
        assert tuple(ex) in imgs, "rebuilt world disagrees with the capture"
    assert len(imgs) == W["images"]
    return imgs


def mark(x, y, ok):
    """A small valid / not-valid mark under a tile."""
    return mono(x, y, "ONE OF THE 72" if ok else "NOT AN IMAGE", 7, SAGE if ok else ACCENT, weight=600)


# -------------------------------------------------------------------- fig 01

def fig01():
    """Part 1's patch as tokens, and one forward step on them: masking against uniform replacement."""
    vw, vh = 960, 600
    W = cap()["worked"]
    tok, masked, cut = W["tokens"], W["masked"], W["eps_cut"]
    x0 = [[0.95, 0.60, -0.30, -0.85], [0.80, 0.45, -0.55, -0.90], [0.55, 0.10, -0.70, -0.95], [0.25, -0.20, -0.85, -1.00]]
    eps = [[-0.55, 1.40, 0.45, -1.10], [0.85, -1.35, -0.25, 0.70], [1.25, 0.30, -0.95, 0.15], [-1.05, 0.90, 1.45, -1.10]]
    ring = {(r, c) for r in range(4) for c in range(4) if masked[r][c]}
    assert all((eps[r][c] > cut) == bool(masked[r][c]) for r in range(4) for c in range(4))
    body = HATCH + eyebrow(40, 46, f"part 1's 4 × 4 patch as 16 tokens · one forward step at ᾱ = {W['abar']} · computed")
    # row 1: numbers -> tokens
    y1 = 92
    body += subtext(40, y1, "x", "0", 13, INK, anchor="start")
    body += mono(64, y1, "PART 1'S PATCH", 8, SOFT, "start")
    body += numgrid(40, y1 + 14, x0)
    body += h_arrow(250, y1 + 70, 334)
    body += mono(284, y1 + 56, "ROUND", 8, SOFT)
    body += eyebrow(334, y1, "16 tokens, grey levels 0-3")
    body += tok4(334, y1 + 14, tok)
    lx = 540
    for i, (lev, rng) in enumerate(((0, "below −0.5"), (1, "−0.5 to 0"), (2, "0 to 0.5"), (3, "0.5 and up"))):
        g = grey(lev, 0, 3)
        yy = y1 + 26 + i * 28
        body += rect(lx, yy - 12, 18, 18, f"rgb({g},{g},{g})", RULE_SOLID, 2, 0.8)
        body += mono(lx + 9, yy + 1, str(lev), 9, PAPER if lev <= 1 else INK, weight=600)
        body += mono(lx + 30, yy + 1, f"level {lev}: x₀ {rng}", 9, MUTED, "start")
    body += mono(lx, y1 + 146, "a token is a label: level 3 is not 'three times' level 1", 8, SOFT, "start")
    # row 2: eps decides the mask; masking against uniform replacement
    y2 = 318
    body += text(40, y2, "ε", 13, INK, SANS, 600, "start")
    body += mono(56, y2, "PART 1'S NOISE DRAW", 8, SOFT, "start")
    body += numgrid(40, y2 + 14, eps, ring=ring)
    body += mono(40, y2 + 140, f"ringed: ε above {cut}, so Φ(ε) above {W['abar']}", 8, ACCENT, "start", 500)
    body += h_arrow(250, y2 + 70, 334, accent=True)
    body += mono(284, y2 + 56, "MASK", 8, ACCENT)
    body += eyebrow(334, y2, f"masking: {W['n_masked']} of 16 hidden", ACCENT)
    body += tok4(334, y2 + 14, tok, mask=masked)
    body += mono(334, y2 + 176, f"expected {W['expected_masked']:.2f}; the network sees", 8, MUTED, "start")
    body += mono(334, y2 + 192, "which tokens are unknown", 8, MUTED, "start")
    # uniform replacement odds for one token at level 3
    U = W["uniform"]
    ux, uy, bw = 600, y2 + 14, 40
    body += eyebrow(ux, y2, "uniform replacement instead")
    body += mono(ux, uy + 10, "a token at level 3 becomes, with probability:", 8, MUTED, "start")
    base = uy + 130
    for lev in range(4):
        p = U["stay"] if lev == 3 else U["each_other"]
        h = p * 100
        bx = ux + 10 + lev * (bw + 22)
        g = grey(lev, 0, 3)
        body += rect(bx, base - h, bw, h, ACCENT if lev == 3 else MUTED, "none", 2)
        body += mono(bx + bw / 2, base - h - 6, f"{p:.2f}", 9, ACCENT if lev == 3 else INK, weight=600)
        body += rect(bx + bw / 2 - 9, base + 6, 18, 18, f"rgb({g},{g},{g})", RULE_SOLID, 2, 0.8)
        body += mono(bx + bw / 2, base + 19, str(lev), 9, PAPER if lev <= 1 else INK, weight=600)
    body += f'<line x1="{ux}" y1="{base}" x2="{ux + 4 * (bw + 22)}" y2="{base}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    body += mono(ux, base + 46, f"stays: 0.64 + 0.36/4 = {U['stay']:.2f}", 8, MUTED, "start")
    body += mono(ux, base + 62, "a changed token looks like any other", 8, MUTED, "start")
    body += footnote(vh - 32, "Computed by tokens.py worked. Masking keeps each token with probability ᾱ; uniform "
                              "replacement redraws it with probability 1 − ᾱ.")
    emit(1, "tokens-forward-step", "One forward step on 16 tokens",
         "masking says what it hid; uniform replacement hides its changes among real tokens", body,
         alt_checked("Part 1's patch as 16 grey-level tokens, Part 1's noise draw marking 7 of them masked at abar 0.64, "
                     "and uniform replacement's odds"), vw, vh)


# -------------------------------------------------------------------- fig 02

def fig02():
    """The four-turn world: predictions with everything masked, one at a time against all at once."""
    vw, vh = 960, 664
    W = cap()["worked"]
    turns, marg = W["turns"], W["marginals"]
    body = HATCH + eyebrow(40, 46, "a world of the patch's four quarter turns, each with probability 1/4 · exact denoiser "
                                   "by counting · computed")
    names = ("upright", "quarter turn", "half turn", "three-quarter turn")
    for k in range(4):
        x = 40 + k * 150
        body += eyebrow(x, 82, names[k], INK)
        body += tok4(x, 92, turns[k], cell=26, gap=3, size=11)
        body += mono(x, 222, "probability 1/4", 8, SOFT, "start")
    body += mono(650, 112, "THE EXACT DENOISER", 8, ACCENT, "start", 600)
    for i, line in enumerate(("counts the turns that agree with", "every visible token, and predicts",
                              "each hidden position from them")):
        body += mono(650, 134 + i * 18, line, 9, MUTED, "start")
    # everything masked: each position's prediction, four bars per cell
    y = 268
    body += eyebrow(40, y, "all 16 masked: each position's prediction")
    cell, gap = 62, 6
    for r in range(4):
        for c in range(4):
            cx, cy = 40 + c * (cell + gap), y + 14 + r * (cell + gap)
            body += rect(cx, cy, cell, cell, "#ffffff", ACCENT if (r, c) == (0, 0) else RULE_SOLID, 3,
                         1.6 if (r, c) == (0, 0) else 0.8)
            for lev in range(4):
                p = marg[r][c][lev]
                g = grey(lev, 0, 3)
                bx = cx + 7 + lev * 12.5
                body += rect(bx, cy + cell - 10, 10, 4, f"rgb({g},{g},{g})", "none", 0)
                if p > 0:
                    body += rect(bx, cy + cell - 12 - p * 42, 10, p * 42, ACCENT if (r, c) == (0, 0) else MUTED, "none", 1)
    tl = marg[0][0]
    body += mono(40, y + 302, "bars: probability of levels 0, 1, 2, 3 (swatches under)", 8, MUTED, "start")
    body += mono(40, y + 320, f"top-left: level 0 with {tl[0]:.2f}, 2 with {tl[2]:.2f}, 3 with {tl[3]:.2f}", 8, ACCENT,
                 "start", 500)
    # one at a time
    sx = 350
    body += eyebrow(sx, y, "one token at a time", INK)
    body += mono(sx + 140, y, "decoding the quarter turn", 8, MUTED, "start")
    ch = W["sequential"][1]                                   # the quarter turn's path
    steps = ch["first_steps"]
    lines = [(f"top-left reads {steps[0]['token']}", f"p = {steps[0]['p']:.1f} · {steps[0]['turns_left']} turns left"),
             (f"top-right reads {steps[1]['token']}", f"p = {steps[1]['p']:.1f} · {steps[1]['turns_left']} turn left"),
             ("every other token", "p = 1 · cost 0")]
    for i, (a, b) in enumerate(lines):
        yy = y + 30 + i * 70
        body += rect(sx, yy, 250, 48, "#ffffff" if i < 2 else "rgba(45,49,66,0.04)", RULE_SOLID, 4, 0.8)
        body += text(sx + 14, yy + 20, a, 11, INK, SANS, 600, "start")
        body += mono(sx + 14, yy + 37, b, 8, MUTED, "start")
        if i < 2:
            body += v_arrow(sx + 125, yy + 48, yy + 69)
    nats = [c["nats"] for c in W["sequential"]]
    assert max(nats) - min(nats) < 1e-9 and abs(nats[0] - W["ln4"]) < 1e-9
    body += mono(sx, y + 252, f"cost ln 2 + ln 2 = ln 4 = {W['ln4']:.3f} nats;", 9, ACCENT, "start", 600)
    body += mono(sx, y + 270, "in every order, for every turn", 9, ACCENT, "start", 600)
    # all at once
    ax = 660
    body += eyebrow(ax, y, "all 16 at once", INK)
    body += tok4(ax, y + 14, W["all_at_once_example"], cell=30, gap=4, size=12)
    assert W["all_at_once_example"] not in turns
    body += mono(ax, y + 162, "one draw: not one of the four turns", 8, ACCENT, "start", 600)
    p_all = W["p_valid_all_16_at_once"]
    body += mono(ax, y + 184, f"a real turn with probability {p_all * 1e6:.2f} × 10⁻⁶", 9, INK, "start", 500)
    C = W["corners"]
    body += mono(ax, y + 214, "two opposite corners at once:", 9, INK, "start", 500)
    body += mono(ax, y + 232, f"a real pair {C['p_consistent']:.2f} of the time,", 9, MUTED, "start")
    body += mono(ax, y + 250, f"both darkest {C['p_both_darkest']:.2f}: no turn has that", 9, MUTED, "start")
    body += footnote(vh - 32, "Computed by tokens.py worked. Each draw takes every position from its own prediction, "
                              "independently.")
    emit(2, "four-turn-world-decoding", "Exact predictions, wrong joint",
         "drawing positions one at a time is exact; drawing them together mixes turns", body,
         alt_checked("Four quarter turns of the patch, per-position probabilities with all 16 masked, decoding one token "
                     "at a time, and one all-at-once draw"), vw, vh)


# -------------------------------------------------------------------- fig 03

def fig03():
    """SEDD's zero-shot table: absorbing against uniform, with GPT-2, D3PM and Plaid (quoted)."""
    vw, vh = 960, 560
    models = [("GPT-2", INK, True), ("SEDD absorbing", ACCENT, False), ("SEDD uniform", BLUE, False),
              ("Plaid", SAGE, False), ("D3PM", MUSTARD, False)]
    ax = Axes(240, 96, 560, 330, (math.log10(35), math.log10(230)), (0, 5), logx=True)
    body = eyebrow(40, 46, "zero-shot perplexity of small models (gpt-2 small's size) · lower is better · quoted")
    body += ax.frame(xticks=[(v, str(v)) for v in (40, 60, 80, 100, 150, 200)], xlabel="PERPLEXITY (LOG SCALE)",
                     grid=False)
    for i, (ds, row) in enumerate(QUOTED_SEDD.items()):
        yv = 4.5 - i
        py = ax.Y(yv)
        body += text(40, py + 4, ds, 12, INK, SANS, 600, "start")
        lo, hi = min(row.values()), max(row.values())
        body += f'<line x1="{ax.X(lo):.1f}" y1="{py:.1f}" x2="{ax.X(hi):.1f}" y2="{py:.1f}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        for j, (name, colour, hollow) in enumerate(models):        # one lane per model, so near-equal values stay apart
            cy = py + (j - 2) * 9
            body += f'<line x1="{ax.X(row[name]):.1f}" y1="{py:.1f}" x2="{ax.X(row[name]):.1f}" y2="{cy:.1f}" stroke="{colour}" stroke-width="0.8"/>'
            body += (f'<circle cx="{ax.X(row[name]):.1f}" cy="{cy:.1f}" r="4.5" fill="{PAPER if hollow else colour}" '
                     f'stroke="{colour}" stroke-width="1.6"/>')
        gain = row["SEDD uniform"] / row["SEDD absorbing"] - 1
        body += mono(820, py + 4, f"uniform +{100 * gain:.0f}%", 9, BLUE, "start", 500)
    body += mono(820, 80, "UNIFORM VS", 7, SOFT, "start")
    body += mono(820, 90, "ABSORBING", 7, SOFT, "start")
    lx = 40
    for name, colour, hollow in models:
        body += (f'<circle cx="{lx + 6}" cy="{vh - 82}" r="5" fill="{PAPER if hollow else colour}" stroke="{colour}" '
                 f'stroke-width="1.6"/>')
        lab = name + (" (exact)" if hollow else " (bound)")
        body += mono(lx + 16, vh - 79, lab, 8, MUTED, "start")
        lx += 32 + len(lab) * 6.2
    body += footnote(vh - 50, "Quoted from Lou, Meng & Ermon, Discrete Diffusion Modeling by Estimating the Ratios of "
                              "the Data Distribution (ICML 2024), Table 1.")
    body += footnote(vh - 32, "Diffusion values are upper bounds; GPT-2's are exact, recomputed without a sliding window.")
    emit(3, "absorbing-beats-uniform", "Masking beats uniform replacement",
         "on every dataset; a GPT-2-sized masked model beats GPT-2 on three of five", body,
         alt_checked("Zero-shot perplexity of GPT-2 small, SEDD absorbing, SEDD uniform, D3PM and Plaid on five datasets; "
                     "absorbing beats uniform on all five"), vw, vh)


# -------------------------------------------------------------------- fig 04

def strip(x, y, n, cell, gap, mask=None, seed=3, hot=None):
    """A token sequence as a strip of cells; masked cells hatched."""
    rng = lcg(seed)
    out = ""
    for i in range(n):
        g = round(70 + next(rng) * 160)
        cx = x + i * (cell + gap)
        if mask is not None and mask[i]:
            out += rect(cx, y, cell, cell, "url(#hatch)", ACCENT, 2, 1)
        else:
            out += rect(cx, y, cell, cell, f"rgb({g},{g},{g})", RULE_SOLID, 2, 0.8)
    return out


def fig04():
    """One LLaDA training step, with its shapes."""
    vw, vh = 960, 600
    L, V = LLADA["length"], LLADA["vocab"]
    n, cell, gap = 16, 30, 6
    x0 = 300
    rng = lcg(11)
    mask = [next(rng) < 0.5 for _ in range(n)]               # one draw at t = 0.5, for the picture
    ax_x = x0 + 7 * (cell + gap) + cell / 2                  # every arrow runs down the eighth cell's centre
    body = HATCH + eyebrow(40, 46, "one training step at llada's sizes · the strips show the first 16 of 4,096 tokens")
    y = 86
    body += text(40, y + 20, "clean sequence", 13, INK, SANS, 600, "start")
    body += subtext(40, y + 40, "x", "0", 12, MUTED, MONO, 500, "start")
    body += mono(60, y + 40, f"· {L:,} tokens", 8, MUTED, "start")
    body += mono(40, y + 56, f"from a {V:,}-token vocabulary", 8, MUTED, "start")
    body += strip(x0, y + 6, n, cell, gap)
    body += v_arrow(ax_x, y + 40, y + 106, accent=True)         # lands on the next strip's eighth cell
    body += tag(x0 + 8 * (cell + gap) + 150, y + 72, "draw t from U(0, 1); mask each token with probability t", ACCENT,
                size=8)
    y = 186
    body += text(40, y + 20, "masked sequence", 13, INK, SANS, 600, "start")
    body += subtext(40, y + 40, "x", "t", 12, MUTED, MONO, 500, "start")
    body += mono(60, y + 40, f"· about t × {L:,} masks (here t = 0.5)", 8, MUTED, "start")
    body += strip(x0, y + 6, n, cell, gap, mask=mask)
    body += v_arrow(ax_x, y + 40, y + 96)
    body += tag(x0 + 8 * (cell + gap) + 112, y + 70, "the whole sequence, read both ways", MUTED, size=8)
    y = 282
    tw = n * (cell + gap) - gap
    body += rect(x0, y, tw, 64, ACCENT_TINT, ACCENT, 6, 1.2)
    body += text(x0 + tw / 2, y + 26, "transformer with no causal mask", 13, ACCENT, SANS, 600)
    body += mono(x0 + tw / 2, y + 46, f"{LLADA['layers']} layers · width {LLADA['width']:,} · {LLADA['heads']} heads · "
                                      f"{LLADA['params_b']}B parameters", 8, MUTED)
    body += text(40, y + 30, "mask predictor", 13, INK, SANS, 600, "start")
    body += mono(40, y + 48, "no time input needed", 8, MUTED, "start")
    body += v_arrow(ax_x, y + 64, y + 128)
    body += tag(x0 + 8 * (cell + gap) + 128, y + 92, f"{L:,} × {V:,} probabilities", MUTED, size=8)
    y = 404
    body += text(40, y + 20, "per-token loss", 13, INK, SANS, 600, "start")
    body += mono(40, y + 38, "hidden: −log p(true token)", 8, ACCENT, "start", 500)
    body += mono(40, y + 54, "visible: copied, no loss", 8, MUTED, "start")
    r2 = lcg(5)
    for i in range(n):
        cx = x0 + i * (cell + gap)
        if mask[i]:
            p = 0.15 + 0.8 * next(r2)
            body += rect(cx, y + 6, cell, 40, "#ffffff", RULE_SOLID, 2, 0.8)
            body += rect(cx + 4, y + 42 - 34 * p, cell - 8, 34 * p, ACCENT, "none", 1)
        else:
            body += rect(cx, y + 6, cell, 40, "rgba(45,49,66,0.04)", RULE, 2, 0.8)
            body += mono(cx + cell / 2, y + 30, "–", 9, SOFT)
    body += mono(x0, y + 62, "bars: the probability the network gave each hidden token's true value (illustrative)", 7,
                 SOFT, "start")
    body += rect(x0, y + 82, tw, 40, "#ffffff", INK, 6, 1.2)
    body += text(x0 + tw / 2, y + 107, "loss = (1/t) × sum over hidden tokens of −log p(true token)", 12, INK, MONO, 500)
    body += mono(40, y + 100, "BERT: one fixed rate, 15% of positions", 8, MUTED, "start")
    body += mono(40, y + 116, "LLaDA: every t from 0 to 1, weight 1/t", 8, ACCENT, "start", 500)
    body += footnote(vh - 32, "Shapes from LLaDA 8B's configuration (Nie et al. 2025, Table 5): 4,096-token sequences, "
                              "126,464-token vocabulary.")
    emit(4, "llada-training-step", "BERT's loss at every masking rate",
         "draw t, mask, predict every hidden token, weight the cross-entropy by 1/t", body,
         alt_checked("One LLaDA training step: draw t, mask 4,096 tokens, a transformer without a causal mask, "
                     "cross-entropy on masked tokens times 1/t"), vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    """Valid share against network calls for every parallel sampler (lab, 4,096 images each)."""
    vw, vh = 960, 640
    D = cap()["decode"]
    imgs = world_images()
    ax = Axes(110, 90, 470, 380, (0, 6), (0, 1.0))
    body = HATCH + eyebrow(40, 46, f"crescent world as tokens · {D['images_per_sampler']:,} images per sampler · exact "
                                   "denoiser · measured")
    body += ax.frame(xticks=[(math.log2(v), str(v)) for v in (1, 2, 4, 8, 16, 32, 64)],
                     yticks=[(v / 4, f"{25 * v}%") for v in range(5)],
                     xlabel="NETWORK CALLS PER IMAGE (LOG SCALE)", ylabel="VALID: ONE OF THE 72 IMAGES")
    L2 = lambda v: math.log2(v)
    rnd = [(64, D["one_per_step"]["random"]["valid"])] + [(64 // k, D["parallel"][f"random_{k}"]["valid"])
                                                          for k in (2, 4, 8, 16, 64)]
    body += ax.path([(L2(c), v) for c, v in sorted(rnd)], INK, 2)
    for c, v in rnd:
        body += ax.dot(L2(c), v, 4, INK)
    anc = [(D["ancestral"][s]["calls"], D["ancestral"][s]["valid"], s) for s in ("64", "256", "1024")]
    body += ax.path([(L2(c), v) for c, v, _ in anc], MUSTARD, 2)
    for c, v, s in anc:
        body += ax.dot(L2(c), v, 4.5, MUSTARD)
    for (c, v, s), dy in zip(anc, (-8, 4, 4)):             # left of their dots, clear of the black line and the 50% grid
        body += tag(ax.X(L2(c)) - 10, ax.Y(v) + dy, f"{int(s):,} steps {pct(v)}", MUSTARD, "end", 8)
    th = D["threshold_certain"]
    tx_, ty_ = ax.X(L2(th["calls"])), ax.Y(th["valid"])
    body += (f'<rect x="{tx_ - 5:.1f}" y="{ty_ - 5:.1f}" width="10" height="10" fill="{ACCENT}" '
             f'transform="rotate(45 {tx_:.1f} {ty_:.1f})"/>')
    body += tag(tx_ + 12, ty_ + 24, "certainty threshold:", ACCENT, "start", 8)
    body += tag(tx_ + 12, ty_ + 39, f"{pct(th['valid'], 0)} valid in {th['calls']:.1f} calls", ACCENT, "start", 8, 600)
    v2 = D["parallel"]["random_2"]["valid"]
    body += tag(ax.X(L2(32)) + 8, ax.Y(v2) + 4, f"2 per call {pct(v2)}", INK, "start", 8)
    v4 = D["parallel"]["random_4"]["valid"]
    body += tag(ax.X(L2(16)) - 10, ax.Y(0) - 30, f"4 per call {pct(v4, 2)}", INK, "end", 8)
    body += mono(ax.X(L2(4)), ax.Y(0) - 12, "8 or more per call: 0%", 8, MUTED, weight=500)
    body += legend_row(110, vh - 92, (("fixed tokens per call, random positions", INK, False),
                                      ("MDLM ancestral steps", MUSTARD, False)))
    # tiles: one per call against two per call
    tx = 640
    body += eyebrow(tx, 96, "one token per call", INK)
    for i, ex in enumerate(D["one_per_step"]["random"]["examples"][:4]):
        body += tile(tx + i * 72, 108, 62, ex)
        body += mark(tx + i * 72 + 31, 186, tuple(ex) in imgs)
    body += eyebrow(tx, 232, "two tokens per call", INK)
    for i, ex in enumerate(D["parallel"]["random_2"]["examples"][:4]):
        body += tile(tx + i * 72, 244, 62, ex)
        body += mark(tx + i * 72 + 31, 322, tuple(ex) in imgs)
    body += eyebrow(tx, 368, "four tokens per call", INK)
    for i, ex in enumerate(D["parallel"]["random_4"]["examples"][:4]):
        body += tile(tx + i * 72, 380, 62, ex)
        body += mark(tx + i * 72 + 31, 458, tuple(ex) in imgs)
    body += footnote(vh - 50, "Measured by tokens.py decode. Ancestral: MDLM's update with caching, so calls count "
                              "only steps that revealed something.")
    body += footnote(vh - 32, "Tiles: each sampler's first samples, grey level 0 dark to 27 bright.")
    emit(5, "valid-share-against-calls", "Exact predictions, broken samples",
         "writing several tokens per call ignores their dependence", body,
         alt_checked("Share of valid images against network calls: one token per call is exact; 2, 4 and 8 per call "
                     "fail; ancestral steps; a threshold"), vw, vh)


# -------------------------------------------------------------------- fig 06

def fig06():
    """The survey's Figure 7, as published: page 20 of arXiv:2508.10875v3 rendered at 400 dpi and cropped.

    pdftoppm -r 400 -f 20 -l 20 -x 222 -y 222 -W 2955 -H 1567 -png 2508.10875v3.pdf crop, then trimmed to the
    figure's own extent (above the caption, which starts at y = 328.8 pt) plus 24 px of white; nothing inside
    the figure is changed."""
    png = HERE / "fig-06-llada-answers-by-step-count.png"
    if not png.exists():
        raise SystemExit("extract the survey's Figure 7 to fig-06-llada-answers-by-step-count.png first (see the docstring)")
    print(f"kept fig-06-llada-answers-by-step-count (source, unchanged; sha1 {hashlib.sha1(png.read_bytes()).hexdigest()[:12]})")
    alt_checked("LLaDA and MMaDA answers to one prompt at several step counts: correct with 1 or 2 tokens per step, "
                "wrong or garbled with more")


# -------------------------------------------------------------------- fig 07

def fig07():
    """LLaDA 8B Base against LLaMA3 8B Base, one protocol (quoted)."""
    vw, vh = 960, 830
    x0, x1 = 300, 820

    def X(v):
        assert 0 <= v <= 100, v
        return x0 + v / 100 * (x1 - x0)

    body = eyebrow(40, 46, "base models under one protocol · llada 8b trained on 2.3t tokens, llama 3 8b on 15t · quoted")
    body += mono(x0, 80, "SCORE (SHOTS IN BRACKETS)", 8, SOFT, "start")
    y, group = 104, None
    for g, name, shots, a, b in QUOTED_LLADA:
        if g != group:
            group = g
            body += eyebrow(40, y + 6, g, MUTED)
            y += 22
        body += text(56, y + 9, f"{name} ({shots})", 11, INK, SANS, 500, "start")
        body += rect(x0, y - 2, X(a) - x0, 8, ACCENT, "none", 2)
        body += rect(x0, y + 9, X(b) - x0, 8, INK, "none", 2)
        lead = round(a - b, 1)
        body += mono(X(max(a, b)) + 8, y + 10, f"{a:.1f} / {b:.1f}", 8, MUTED, "start")
        body += mono(900, y + 10, f"{lead:+.1f}".replace("-", "−"), 9, ACCENT if lead > 0 else INK, "end", 600)
        y += 34
    assert y + 60 < vh - 60, "legend would reach the footnotes"
    for v in (0, 25, 50, 75, 100):
        body += f'<line x1="{X(v):.1f}" y1="{y - 6}" x2="{X(v):.1f}" y2="{y - 2}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        body += mono(X(v), y + 10, str(v), 7, SOFT)
    body += f'<line x1="{x0}" y1="{y - 6}" x2="{x1}" y2="{y - 6}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    body += swatch_row(x0, y + 40, (("LLaDA 8B Base", ACCENT), ("LLaMA 3 8B Base", INK)))
    body += mono(900, 80, "LLADA − LLAMA 3", 8, SOFT, "end")
    body += footnote(vh - 50, "Quoted from Nie et al., Large Language Diffusion Models (NeurIPS 2025), Table 1 (v3), one "
                              "protocol. Scored by likelihood: MMLU,")
    body += footnote(vh - 32, "ARC-C, HellaSwag, TruthfulQA, WinoGrande, PIQA, GPQA, CMMLU, C-Eval; the other six by "
                              "generated answers.")
    emit(7, "llada-against-llama3", "LLaDA 8B against LLaMA 3 8B",
         "ahead on math and Chinese, behind on reasoning and commonsense, on 2.3T against 15T tokens", body,
         alt_checked("LLaDA 8B Base against LLaMA 3 8B Base on 15 benchmarks: ahead on math and Chinese, behind on BBH, "
                     "HellaSwag, PIQA and MBPP"), vw, vh)


# -------------------------------------------------------------------- fig 08

def fig08():
    """LLaDA's remasking ablation: random against low-confidence (quoted)."""
    vw, vh = 960, 520
    x0, x1 = 220, 760

    def X(v):
        assert 0 <= v <= 80, v
        return x0 + v / 80 * (x1 - x0)

    body = eyebrow(40, 46, "llada 8b base · generation length 256, 256 steps: one token per step · same model, two "
                           "decoders · quoted")
    y = 104
    for name, rnd, low in QUOTED_REMASK:
        body += text(40, y + 12, name, 13, INK, SANS, 600, "start")
        body += rect(x0, y, X(rnd) - x0, 10, BLUE, "none", 2)
        body += mono(X(rnd) + 8, y + 9, f"{rnd:.1f}", 9, BLUE, "start", 600)
        body += rect(x0, y + 16, X(low) - x0, 10, ACCENT, "none", 2)
        body += mono(X(low) + 8, y + 25, f"{low:.1f}", 9, ACCENT, "start", 600)
        body += mono(900, y + 18, f"+{low - rnd:.1f}", 10, ACCENT, "end", 600)
        y += 60
    for v in (0, 20, 40, 60, 80):
        body += f'<line x1="{X(v):.1f}" y1="{y - 8}" x2="{X(v):.1f}" y2="{y - 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        body += mono(X(v), y + 8, str(v), 7, SOFT)
    body += f'<line x1="{x0}" y1="{y - 8}" x2="{x1}" y2="{y - 8}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    body += swatch_row(x0, y + 40, (("random remasking: keep random positions", BLUE),
                                    ("low-confidence remasking: keep the most confident", ACCENT)))
    body += footnote(vh - 50, "Quoted from Nie et al., Large Language Diffusion Models (NeurIPS 2025), Table 9 (v3). "
                              "The authors liken low confidence")
    body += footnote(vh - 32, "to the annealed sampling autoregressive models use: more accurate, less diverse.")
    emit(8, "llada-remasking-ablation", "The decoder, not the model",
         "keeping the surest predictions moved GSM8K from 21.3 to 70.0", body,
         alt_checked("LLaDA 8B Base with random against low-confidence remasking: BBH, GSM8K, Math, HumanEval and MBPP "
                     "all rise with low confidence"), vw, vh)


# -------------------------------------------------------------------- fig 09

FIG09_ROWS = [
    ("random", "Random order, sampled", "first-hitting: the exact sampler"),
    ("position", "Surest position first, sampled", "rank by how sure each position is"),
    ("drawn", "Likeliest draw first, sampled", "rank by the drawn token's probability"),
    ("greedy_random", "Random order, greedy", "argmax tokens"),
    ("greedy_drawn", "Surest first, greedy", "LLaDA's default decoder"),
]


def fig09():
    """Five decoders at one token per step: images found and brightness spread (lab)."""
    vw, vh = 960, 640
    D = cap()["decode"]["one_per_step"]
    W = cap()["world"]
    body = eyebrow(40, 46, f"crescent world as tokens · one token per call · {cap()['decode']['images_per_sampler']:,} "
                           "images per decoder · measured")
    ix, bx = 300, 450
    body += mono(ix + 50, 86, f"IMAGES FOUND, OF {W['images']}", 8, INK, weight=500)
    body += mono(bx + 50, 86, "BRIGHTNESS SPREAD", 8, INK, weight=500)
    body += mono(700, 86, "FIRST SIX SAMPLES", 8, SOFT, "start")
    y = 112
    for key, name, sub in FIG09_ROWS:
        R = D[key]
        exact = key in ("random", "position")
        if exact:
            body += rect(28, y - 6, 904, 76, "rgba(45,49,66,0.04)", "none", 4)
        body += text(40, y + 22, name, 12, INK, SANS, 600, "start")
        body += mono(40, y + 40, sub, 8, MUTED, "start")
        f = R["images_found"] / W["images"]
        colour = INK if exact else ACCENT
        body += rect(ix, y + 18, 100, 9, PAPER2, "none", 2)
        body += rect(ix, y + 18, 100 * f, 9, colour, "none", 2)
        body += mono(ix + 50, y + 44, str(R["images_found"]), 10, colour, weight=600)
        s = R["brightness_sd"]
        assert 0 <= s <= 0.3
        body += rect(bx, y + 18, 100, 9, PAPER2, "none", 2)
        if s > 0:
            body += rect(bx, y + 18, 100 * s / 0.3, 9, colour, "none", 2)
        wx = bx + 100 * W["brightness_sd"] / 0.3
        body += f'<line x1="{wx:.1f}" y1="{y + 13}" x2="{wx:.1f}" y2="{y + 32}" stroke="{SAGE}" stroke-width="1.6"/>'
        body += mono(bx + 50, y + 44, f"{s:.3f}", 10, colour, weight=600)
        for i, ex in enumerate(R["examples"][:6]):
            body += tile(700 + i * 38, y + 6, 32, ex)
        y += 86
    body += f'<line x1="{bx + 10}" y1="{y + 2}" x2="{bx + 24}" y2="{y + 2}" stroke="{SAGE}" stroke-width="1.6"/>'
    body += mono(bx + 30, y + 5, f"the world's own spread, {W['brightness_sd']:.3f}", 8, MUTED, "start")
    body += footnote(vh - 50, "Measured by tokens.py decode. Spread: the standard deviation of the samples' brightness; "
                              "all decoders' samples are valid.")
    body += footnote(vh - 32, "Tiles: grey level 0 dark to 27 bright. Greedy takes each position's likeliest token.")
    emit(9, "decoders-that-do-not-sample", "Which positions first is harmless; how they are chosen is not",
         "ranking by the drawn token, or decoding greedily, loses most of the 72 images", body,
         alt_checked("Images found of 72 and brightness spread for five one-token-per-step decoders with sample tiles; "
                     "ranking by the drawn token collapses"), vw, vh)


# -------------------------------------------------------------------- fig 10

def fig10():
    """The float32 race (lab) beside Zheng et al.'s precision ablation (quoted)."""
    vw, vh = 960, 600
    P = cap()["precision"]
    cs, f32, f64, cf = P["c"], P["float32"], P["float64"], P["closed_form_float32"]
    ax = Axes(100, 96, 470, 340, (-9, -5), (0, 1.1), logx=True)
    body = eyebrow(40, 46, f"mdlm's race: [mask] with weight 1 against one token with weight c · "
                           f"{P['draws_per_c']:,} draws per c · measured")
    body += ax.frame(xticks=[(10.0 ** e, f"1e{e}") for e in range(-9, -4)],
                     yticks=[(v, f"{v:.2f}") for v in (0, 0.25, 0.5, 0.75, 1.0)],
                     xlabel="TOKEN WEIGHT c, RELATIVE TO THE MASK (LOG SCALE)",
                     ylabel="SHARE OF ITS FAIR CHANCE")
    xs = [10 ** (-9 + 4 * i / 200) for i in range(201)]
    curve = [(x, (2 ** -24 / x) / math.expm1(2 ** -24 / x)) for x in xs]
    body += ax.path(curve, INK, 1.4, True)
    for c, a, b in zip(cs, f32, f64):
        body += ax.dot(c, min(b, 1.1), 4, BLUE, hollow=True)
        body += ax.dot(c, a, 4.5, ACCENT)
    half = P["half_share_c"]
    body += ax.vline(half, SOFT)
    body += mono(ax.X(half) + 8, ax.Y(0.5) + 16, f"half at c = {half * 1e8:.2f} × 10⁻⁸", 8, MUTED, "start", 500)
    even = P["even_share"]["gpt2_50257"]
    c1000 = even / 999
    share = (2 ** -24 / c1000) / math.expm1(2 ** -24 / c1000)
    body += ax.vline(c1000, ACCENT)
    lx = ax.X(c1000) - 8                                    # right-aligned against the line, between two gridlines
    lines = ("an even share of GPT-2's", "50,257 tokens, step 1 of", f"1,000: {pct(share, 0)} of its chance",
             "(closed form)")
    top = ax.Y(0.75) + 16
    for i, line in enumerate(lines):
        body += mono(lx, top + i * 15, line, 8, ACCENT, "end", 600 if i == 2 else 500)
    assert lx - max(len(s) for s in lines) * 5.3 > ax.x + 4, "label would reach the y-axis"
    assert top + 3 * 15 + 4 < ax.Y(0.5) - 2, "label would reach the 0.50 gridline"
    ly = vh - 92
    body += f'<circle cx="106" cy="{ly - 4}" r="4.5" fill="{ACCENT}"/>' + mono(118, ly, "float32 draws", 8, MUTED, "start")
    body += (f'<circle cx="236" cy="{ly - 4}" r="4.5" fill="{PAPER}" stroke="{BLUE}" stroke-width="1.6"/>'
             + mono(248, ly, "float64 draws", 8, MUTED, "start"))
    body += (f'<line x1="358" y1="{ly - 4}" x2="380" y2="{ly - 4}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="6,4"/>'
             + mono(388, ly, "closed form x / (eˣ − 1), x = 2⁻²⁴ / c", 8, MUTED, "start"))
    # Zheng et al.'s ablation
    zx = 640
    body += eyebrow(zx, 96, "zheng et al.: only the sampling code changed", INK)
    top = max(g for _, g, _ in QUOTED_ZHENG)
    for i, (name, g, e) in enumerate(QUOTED_ZHENG):
        yy = 130 + i * 92
        body += text(zx, yy, name, 11, INK, SANS, 600, "start")
        w = 170 * g / top
        colour = BLUE if name == "64-bit" else ACCENT
        body += rect(zx, yy + 10, w, 12, colour, "none", 2)
        body += mono(zx + w + 6, yy + 20, f"Gen PPL {g:.2f}", 9, colour, "start", 600)
        body += mono(zx, yy + 42, f"entropy {e:.2f}", 9, MUTED, "start")
    body += mono(zx, 420, "8 samples of 2,048 steps; Gen PPL under GPT-2 Large", 8, SOFT, "start")
    body += mono(zx, 436, "lower Gen PPL, lower entropy: a lower temperature", 8, SOFT, "start")
    body += footnote(vh - 50, "Measured by tokens.py precision (left); quoted from Zheng et al., ICLR 2025, Table 2 "
                              "(right).")
    body += footnote(vh - 32, "At the first step of an N-step MDLM run a token of probability p has weight c = p / (N − 1).")
    emit(10, "float32-race", "Float32 starves unlikely tokens",
         "and lowers the temperature of every sampler that races [MASK] against them", body,
         alt_checked("Share of its fair chance a token wins MDLM's race against the mask, float32 against float64, "
                     "with the closed form and Zheng's ablation"), vw, vh)


# ------------------------------------------------------------------------------- cover

def cover():
    W = cap()["world"]
    img = W["examples"]["turn0_strong_by_level"][4]           # strong crescent at middle brightness
    rng = lcg(2026)
    order = sorted(range(64), key=lambda _: next(rng))       # one random reveal order, fixed
    body = HATCH + eyebrow(72, 73, "diffusion · part eleven")
    body += text(72, 148, "Discrete diffusion language models", 44, INK, SERIF, 400, "start")
    body += text(72, 193, "masks, LLaDA and the samplers in dispute", 15, MUTED, MONO, 400, "start")
    size, gap, x0, y0 = 150, 16, 476, 262
    for k, shown in enumerate((16, 32, 48, 64)):
        visible = set(order[:shown])
        mask = [i not in visible for i in range(64)]
        body += tile(x0 + k * (size + gap), y0, size, img, mask=mask, sw=1.0)
        body += mono(x0 + k * (size + gap) + size / 2, y0 + size + 22, f"{shown} OF 64 WRITTEN", 9,
                     ACCENT if shown < 64 else INK, weight=500)
    body += mono(72, 290, "replace a token with [MASK],", 12, MUTED, "start")
    body += mono(72, 312, "learn to fill it back in;", 12, MUTED, "start")
    body += mono(72, 346, "the loss is BERT's at every rate,", 12, MUTED, "start")
    body += mono(72, 368, "the dispute is how you sample", 12, MUTED, "start")
    body += f'<line x1="72" y1="528" x2="1128" y2="528" stroke="{RULE}" stroke-width="1"/>'
    body += text(72, 568, "Every prediction right is not the same as the sample right.", 20, MUTED, SERIF, 400, "start",
                 italic=True)
    emit_cover(body, alt_checked("Four 8 by 8 token grids unmasking a crescent in random order: 16, 32, 48 and all 64 "
                                 "tokens written, masked cells hatched"))


FIGURES = {1: fig01, 2: fig02, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07, 8: fig08, 9: fig09, 10: fig10}

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if not args:
        for f in FIGURES.values():
            f()
        cover()
    for arg in args:
        cover() if arg == "cover" else FIGURES[int(arg)]()
