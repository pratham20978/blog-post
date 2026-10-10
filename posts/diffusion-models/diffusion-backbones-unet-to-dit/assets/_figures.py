#!/usr/bin/env python3
"""Figures for "Diffusion Backbones: U-Net to DiT, Block by Block" (diffusion-models, part 4).

Every measured number drawn here is read from ../lab/captures.json, the capture that the
article's lab download ships, so the prose, the figures and the lab cannot drift apart.
Numbers quoted from papers (DiT's Table 4, SD3's encoder table) are typed once, below,
next to the ledger keys they come from.

    python3 _figures.py            # all placed/plot/chart figures plus the cover
    python3 _figures.py 3 10       # just those
    python3 _figures.py cover      # just the cover
Figures 4, 7 and 8 are Mermaid:  python3 _mermaid.py
"""

from __future__ import annotations

import json
import math
import pathlib

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUSTARD, MUTED, PAPER, RULE, RULE_SOLID,
    SAGE, SANS, SERIF, SOFT, emit, emit_cover, eyebrow, h_arrow, mono, rect, text, v_arrow,
)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
UNET, DIT, MMDIT = CAP["unet"], CAP["dit"], CAP["mmdit"]
ATT, MEM, PATCH = CAP["attention"], CAP["memory"], CAP["patch"]

# Quoted from papers, with their ledger keys.
DIT_FID = {4: 43.01, 2: 19.47}                     # L16: FID-50K, 400K steps, no guidance
DIT_PAPER_GFLOPS = {4: 29.05, 2: 118.64}           # L16
SD3_ENCODERS_GB = [("T5-XXL", 19.05), ("CLIP-G", 2.78), ("CLIP-L", 0.49),
                   ("VAE encoder", 0.14)]          # L29: SD3 App. E.1, Table 7


def dit(name, image=256):
    return next(r for r in DIT if r["name"] == name and r["image"] == image)


def fmt(n, d=1):
    return f"{n:,.{d}f}"


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


# -------------------------------------------------------------------- fig 01

def fig01():
    vw, vh = 960, 470
    body = eyebrow(60, 44, "one contract, three ways to spend it · 512×512 image, latent factor f = 8")

    # inputs and output
    body += rect(40, 168, 158, 142, "#ffffff", INK, 6, 1)
    body += mono(56, 190, "INPUTS", 8, SOFT, "start")
    body += text(56, 216, "noisy latent xₜ", 11, INK, SANS, 600, "start")
    body += mono(56, 232, "C × 64 × 64", 8, MUTED, "start")
    body += text(56, 258, "timestep t", 11, INK, SANS, 600, "start")
    body += text(56, 284, "condition c", 11, INK, SANS, 600, "start")
    body += mono(56, 300, "class or text tokens", 8, MUTED, "start")

    body += rect(782, 190, 140, 98, ACCENT_TINT, ACCENT, 6, 1)
    body += mono(798, 212, "OUTPUT", 8, SOFT, "start")
    body += text(798, 238, "prediction", 11, ACCENT, SANS, 600, "start")
    body += mono(798, 256, "C × 64 × 64", 8, MUTED, "start")
    body += mono(798, 272, "the shape of xₜ", 8, MUTED, "start")

    rows = [(80, "U-NET · SD 1.5"), (200, "DIT · XL/2"), (320, "MM-DIT · SD3")]
    for y, name in rows:
        body += rect(262, y, 470, 104, "#ffffff", RULE_SOLID, 6, 1)
        body += mono(278, y + 20, name, 8, INK, "start", 600)
        # fan in from the inputs box, fan out to the output box
        body += path_line([(198, 239), (230, 239), (230, y + 52), (262, y + 52)], MUTED)
        body += path_line([(732, y + 52), (756, y + 52), (756, 239), (782, 239)], MUTED)

    # U-Net: the pyramid, drawn to scale (side ∝ grid side)
    y0 = 80
    xs, sides, labels = [280, 348, 398, 438], [64, 32, 16, 8], ["4,096", "1,024", "256", "64"]
    widths = ["320 ch", "640", "1,280", "1,280"]
    for x, s_, lab, wd in zip(xs, sides, labels, widths):
        side = s_ * 0.78
        top = y0 + 26 + (50 - side)
        body += rect(x, top, side, side, "rgba(45,49,66,0.06)", INK, 2, 0.9)
        body += mono(x + side / 2, y0 + 89, lab, 7, MUTED)
        body += mono(x + side / 2, y0 + 99, wd, 7, SOFT)
    body += mono(482, y0 + 46, "positions per layer: 4,096 → 64 → 4,096", 8, INK, "start")
    body += mono(482, y0 + 62, "attention at 64², 32², 16² and the 8² middle", 8, MUTED, "start")
    body += mono(482, y0 + 78, "12 skips carry detail back up", 8, MUTED, "start")

    # DiT: one strip, the same length in every block
    y0 = 200
    body += cells(278, y0 + 42, 34, 1, 9, 2)
    body += mono(656, y0 + 51, "… 1,024 tokens", 8, MUTED, "start")
    body += mono(278, y0 + 76, "1,024 TOKENS × 1,152 WIDE", 8, INK, "start", 600)
    body += mono(278, y0 + 92, "the same N in all 28 blocks · timestep and class enter by adaLN", 8, MUTED, "start")

    # MM-DiT: an image strip and a text strip, one attention over both
    y0 = 320
    body += cells(278, y0 + 34, 30, 1, 9, 2)
    body += cells(278, y0 + 52, 5, 1, 9, 2, "rgba(184,145,90,0.18)", MUSTARD)
    body += mono(612, y0 + 43, "… 1,024 image tokens", 8, INK, "start")
    body += mono(340, y0 + 61, "154 text tokens (77 CLIP + 77 T5)", 8, MUSTARD, "start")
    body += mono(278, y0 + 84, "own weights per stream · one joint attention over 1,178 tokens", 8, MUTED, "start")

    body += footnote(vh - 26, "C = 4 for SD 1.5 and DiT, 16 for SD3. Token counts assume a 2×2 patch. "
                              "Squares drawn with side proportional to grid side.")
    emit(1, "one-contract-three-backbones", "One contract, three internals",
         "Same-shape in, same-shape out; the backbones differ in how many positions each layer sees.",
         body, "Three backbones mapping a C×64×64 latent to a same-shaped prediction", vw, vh)


# -------------------------------------------------------------------- fig 02

def fig02():
    vw, vh = 960, 470
    M = [[PATCH["p1"]["values"][r * 4 + c][0] for c in range(4)] for r in range(4)]
    pooled = PATCH["avgpool2"]
    toks = PATCH["p2"]["values"]
    body = eyebrow(60, 44, "part 1's noisy patch xₜ at ᾱ = 0.64, shrunk two ways")

    # the 4x4 patch with its 2x2 patch lattice
    gx, gy, cell, gap = 60, 120, 52, 4
    body += valgrid(gx, gy, M, cell, gap)
    span = 2 * cell + gap
    for r in (0, 1):
        for c in (0, 1):
            body += rect(gx + c * (span + gap) - 3, gy + r * (span + gap) - 3, span + 6, span + 6,
                         "none", ACCENT, 4, 1.4)
    body += mono(gx + 114, gy + 252, "16 POSITIONS · 256 ATTENTION PAIRS", 8, INK, "middle", 600)
    body += mono(gx + 114, gy + 268, "orange: the four 2×2 patches", 8, ACCENT)

    # route 1: pool (U-Net)
    body += mono(392, 100, "2×2 AVERAGE POOL · U-NET", 8, INK, "start", 600)
    body += path_line([(284, 176), (330, 176), (330, 168), (392, 168)], MUTED)
    body += valgrid(392, 112, pooled, 54, 4, digits=4, size=10)
    body += mono(522, 130, "4 positions · 16 pairs", 8, INK, "start", 600)
    body += mono(522, 146, "12 of 16 values discarded", 8, MUTED, "start")
    body += mono(522, 162, "a skip keeps the 4×4 original", 8, ACCENT, "start")

    # route 2: patchify (DiT)
    body += mono(392, 254, "PATCHIFY, p = 2 · DIT", 8, INK, "start", 600)
    body += path_line([(284, 287), (330, 287), (330, 323), (392, 323)], MUTED)
    ty = 266
    for i, tok in enumerate(toks):
        y = ty + i * 30
        body += valgrid(392, y, [tok], 26, 2, digits=2, size=7)
        body += mono(510, y + 17, f"token {i + 1}", 8, SOFT, "start")
    body += mono(580, 300, "4 tokens · 16 pairs", 8, INK, "start", 600)
    body += mono(580, 316, "nothing discarded: a reshape", 8, MUTED, "start")
    body += mono(580, 332, "16 values in token width", 8, ACCENT, "start")

    # attention pairs, drawn to scale
    body += rect(752, 96, 176, 330, "#ffffff", RULE_SOLID, 6, 1)
    body += mono(768, 118, "ATTENTION PAIRS, TO SCALE", 8, SOFT, "start")
    body += cells(768, 134, 16, 16, 7, 2, "rgba(45,49,66,0.10)", "none")
    body += mono(768, 292, "16 positions · 256 pairs", 8, INK, "start")
    body += cells(768, 312, 4, 4, 7, 2, ACCENT_TINT, ACCENT)
    body += mono(768, 364, "4 pooled positions or", 8, ACCENT, "start")
    body += mono(768, 378, "4 tokens · 16 pairs", 8, ACCENT, "start")
    body += mono(768, 400, "each cell = one comparison", 8, SOFT, "start")

    body += footnote(vh - 26, "Values from part 1 of this series, rounded to two decimals; pooled means are exact. "
                              "High value = bright.")
    emit(2, "two-ways-to-shrink-a-patch", "Two ways to shrink a patch",
         "Pooling discards values and needs a skip; patchifying keeps them all in token width.",
         body, "A 4×4 noisy patch pooled to 2×2 and patchified into four tokens", vw, vh)


# -------------------------------------------------------------------- fig 03

def fig03():
    vw, vh = 960, 660
    tr = {r["module"]: r for r in UNET["trace"]}
    p = lambda m: tr[m]["params"] / 1e6
    body = eyebrow(60, 40, "stable diffusion 1.5 u-net, one 512×512 image · measured with forward hooks")

    LY = {64: 160, 32: 300, 16: 410, 8: 490}          # level centre lines
    H = {64: 89.6, 32: 44.8, 16: 22.4, 8: 11.2}       # box height ∝ grid side (1.4 px per cell)
    W = {4: 4, 320: 16, 640: 32, 1280: 64}            # box width ∝ channels (0.05 px per channel)
    mid_y = 560

    def stage(x, res, ch, y=None):
        y = LY[res] if y is None else y
        return {"x": x, "w": W[ch], "y": y, "h": H[res], "res": res, "ch": ch,
                "cx": x + W[ch] / 2, "top": y - H[res] / 2, "bot": y + H[res] / 2}

    S = {
        "in": stage(40, 64, 4), "d0": stage(110, 64, 320), "d1": stage(205, 32, 640),
        "d2": stage(300, 16, 1280), "d3": stage(395, 8, 1280), "mid": stage(448, 8, 1280, mid_y),
        "u0": stage(501, 8, 1280), "u1": stage(596, 16, 1280), "u2": stage(723, 32, 640),
        "u3": stage(834, 64, 320), "out": stage(916, 64, 4),
    }
    # skips first, so the stage boxes paint over their ends
    skips = [
        (64, "d0", "u3", "3 SKIPS · 320×64×64 EACH (CONV_IN + 2 BLOCK OUTPUTS)", 480, -8),
        (32, "d1", "u2", "320×32×32 + 2 × 640×32×32", 480, -8),
        (16, "d2", "u1", "640×16×16 + 2 × 1280×16×16", 480, -8),
        (8, "d3", "u0", "3 × 1280×8×8", 480, -22),
    ]
    for res, a, b, lab, lx, dy in skips:
        y = LY[res]
        body += path_line([(S[a]["x"] + S[a]["w"], y), (S[b]["x"], y)], LINK, 1.2, dashed=True)
        body += tag(lx, y + dy, lab, LINK, "middle", 7.5, 500)

    for k, s in S.items():
        fill = "rgba(45,49,66,0.08)" if k not in ("in", "out") else "rgba(235,108,54,0.18)"
        stroke = INK if k not in ("in", "out") else ACCENT
        body += rect(s["x"], s["top"], s["w"], s["h"], fill, stroke, 1.5, 1)

    def vhv(a, b, label, up=False):
        """Bottom edge down to the next stage's top edge (or up, on the decoder side)."""
        A, B = S[a], S[b]
        if not up:
            y1, y2 = A["bot"], B["top"]
        else:
            y1, y2 = A["top"], B["bot"]
        ym = (y1 + y2) / 2
        out = path_line([(A["cx"], y1), (A["cx"], ym), (B["cx"], ym), (B["cx"], y2)], MUTED)
        out += tag((A["cx"] + B["cx"]) / 2, ym - 5, label, MUTED, "middle", 7.5, 500)
        return out

    body += vhv("d0", "d1", "320×32×32")
    body += vhv("d1", "d2", "640×16×16")
    body += vhv("d2", "d3", "1280×8×8")
    body += vhv("u0", "u1", "1280×16×16", up=True)
    body += vhv("u1", "u2", "1280×32×32", up=True)
    body += vhv("u2", "u3", "640×64×64", up=True)
    # into and out of the middle block, head-on
    d3, m, u0 = S["d3"], S["mid"], S["u0"]
    body += path_line([(d3["cx"], d3["bot"]), (d3["cx"], m["y"]), (m["x"], m["y"])], MUTED)
    body += path_line([(m["x"] + m["w"], m["y"]), (u0["cx"], m["y"]), (u0["cx"], u0["bot"])], MUTED)
    body += tag(d3["cx"] - 8, mid_y - 26, "1280×8×8", MUTED, "end", 7.5)
    body += tag(u0["cx"] + 8, mid_y - 26, "1280×8×8", MUTED, "start", 7.5)
    # conv_in, conv_out
    body += path_line([(S["in"]["x"] + 4, 160), (S["d0"]["x"], 160)], MUTED)
    body += path_line([(S["u3"]["x"] + 16, 160), (S["out"]["x"], 160)], MUTED)
    body += tag(76, 150, "CONV_IN", MUTED, "middle", 7.5)
    body += tag(883, 150, "CONV_OUT", MUTED, "middle", 7.5)

    def label(k, name, params, attn, anchor="middle", dx=0, dy=0, where="above"):
        s = S[k]
        if where == "above":
            x, y = s["cx"] + dx, s["top"] - 22 + dy
        elif where == "below":
            x, y = s["cx"] + dx, s["bot"] + 16 + dy
        elif where == "left":
            x, y = s["x"] - 8 + dx, s["y"] - 4 + dy
        else:
            x, y = s["x"] + s["w"] + 8 + dx, s["y"] - 4 + dy
        out = text(x, y, name, 9, INK, MONO, 600, anchor)
        out += mono(x, y + 12, f"{params:.1f}M · {attn}", 7.5, ACCENT if "tok" in attn else SOFT, anchor)
        return out

    body += label("d0", "DOWN 64×64", p("down_blocks.0"), "attn 4,096 tok")
    body += label("d1", "DOWN 32×32", p("down_blocks.1"), "attn 1,024 tok", "end", where="left")
    body += label("d2", "DOWN 16×16", p("down_blocks.2"), "attn 256 tok", "end", where="left")
    body += label("d3", "DOWN 8×8", p("down_blocks.3"), "no attention", "end", where="left")
    body += label("mid", "MIDDLE 8×8", p("mid_block"), "attn 64 tok", where="below")
    body += label("u0", "UP 8×8", p("up_blocks.0"), "no attention", "start", where="right")
    body += label("u1", "UP 16×16", p("up_blocks.1"), "attn 256 tok", "start", where="right")
    body += label("u2", "UP 32×32", p("up_blocks.2"), "attn 1,024 tok", "start", where="right")
    body += label("u3", "UP 64×64", p("up_blocks.3"), "attn 4,096 tok")
    body += mono(43, 226, "LATENT", 7.5, ACCENT, "middle", 600)
    body += mono(43, 238, "4×64×64", 7.5, SOFT)
    body += mono(919, 226, "OUTPUT", 7.5, ACCENT, "middle", 600)
    body += mono(919, 238, "4×64×64", 7.5, SOFT)

    # what the up path's ResNet blocks actually receive
    body += rect(612, 548, 300, 66, "#ffffff", RULE_SOLID, 5, 1)
    body += mono(626, 566, "DECODER RESNETS SEE INPUT + SKIP CHANNELS", 7.5, SOFT, "start")
    body += mono(626, 582, "16×16: 2,560 · 2,560 · 1,920", 8, INK, "start")
    body += mono(626, 598, "64×64:   960 ·   640 ·   640", 8, INK, "start")

    skip_mb = UNET["skip_bytes_fp16"] / 1e6
    body += footnote(vh - 30, f"{UNET['params']:,} parameters, {UNET['flops'] / 1e9:.1f} GFLOP per call. "
                              f"Box height ∝ grid side, width ∝ channels. Skip stack: {len(UNET['skips'])} "
                              f"tensors, {skip_mb:.1f} MB in fp16.")
    body += footnote(vh - 16, "Dashed: skip connections, saved on the way down and concatenated on the way up.")
    emit(3, "sd15-unet-shape-trace", "SD 1.5's U-Net, traced",
         "Every block's shape and parameter count, measured, and drawn to scale.",
         body, "SD 1.5 U-Net traced to scale with all skip connections", vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    vw, vh = 960, 420
    lv = {l["level"]: l for l in UNET["levels"]}
    P, F = UNET["params"], UNET["flops"]
    body = eyebrow(60, 44, "sd 1.5 u-net per level · one 512×512 image, batch 1 · measured")
    ax0, ax1, scale = 250, 610, 210 / 50          # 0–50% over 210 px, both panels
    body += mono(ax0, 82, f"SHARE OF PARAMETERS ({P / 1e6:.1f}M)", 8, SOFT, "start")
    body += mono(ax1, 82, f"SHARE OF FLOPS ({F / 1e9:.1f} GFLOP)", 8, SOFT, "start")
    for x in (ax0, ax1):
        for pct in (0, 25, 50):
            gx = x + pct * scale
            body += (f'<line x1="{gx}" y1="96" x2="{gx}" y2="344" stroke="{RULE}" stroke-width="0.8"/>')
            body += mono(gx, 358, f"{pct}%", 7, SOFT)
    rows = [(0, "64×64", "width 320"), (1, "32×32", "width 640"), (2, "16×16", "width 1,280"),
            (3, "8×8 + middle", "width 1,280")]
    y = 112
    for key, grid_, width in rows:
        l = lv[key]
        pp, fp = 100 * l["params"] / P, 100 * l["flops"] / F
        ap = 100 * l["flops_split"].get("attention_core", 0) / F
        body += text(60, y + 16, grid_, 12, INK, SANS, 600, "start")
        body += mono(60, y + 32, f"{width} · {l['tokens']:,} positions", 8, SOFT, "start")
        body += rect(ax0, y + 4, pp * scale, 26, "rgba(94,122,155,0.22)", BLUE, 2, 1)
        body += tag(ax0 + pp * scale + 10, y + 21, f"{pp:.1f}% · {l['params'] / 1e6:.1f}M", BLUE, "start", 9, 600)
        body += rect(ax1, y + 4, fp * scale, 26, "rgba(45,49,66,0.12)", INK, 2, 1)
        if ap * scale > 1:
            body += rect(ax1, y + 4, ap * scale, 26, "rgba(235,108,54,0.55)", ACCENT, 2, 1)
        body += tag(ax1 + fp * scale + 10, y + 21, f"{fp:.1f}% · {l['flops'] / 1e9:.1f} GFLOP", INK, "start", 9, 600)
        y += 58
    body += rect(ax1, 374, 12, 12, "rgba(235,108,54,0.55)", ACCENT, 2, 1)
    body += mono(ax1 + 20, 384, "of which attention comparisons (QKᵀ and softmax·V)", 8, MUTED, "start")
    body += footnote(vh - 14, "Time embedding, conv_in and conv_out (0.2% of parameters, 0.02% of FLOPs) not shown. "
                              "A FLOP here is one multiply or one add.")
    emit(5, "unet-params-vs-flops-by-level", "Parameters at the bottom, compute at the top",
         "Where SD 1.5's U-Net stores its weights and where it spends its arithmetic.",
         body, "Per-level share of parameters and FLOPs in SD 1.5's U-Net", vw, vh)


# -------------------------------------------------------------------- fig 06

def fig06():
    vw, vh = 960, 560
    body = eyebrow(60, 40, "dit-xl on the 4×32×32 latent of a 256×256 image · same model, two patch sizes")
    lat = noisy_motif(32, abar=0.96, seed=11)
    for i, (p, x0) in enumerate(((4, 40), (2, 500))):
        r = dit(f"DiT-XL/{p}")
        n_side = 32 // p
        body += rect(x0, 64, 420, 410, "#ffffff", RULE_SOLID, 6, 1)
        body += text(x0 + 18, 92, f"DiT-XL/{p}", 15, ACCENT if p == 2 else INK, SERIF, 400, "start")
        body += mono(x0 + 120, 90, f"PATCH {p}×{p}", 8, SOFT, "start")
        # the latent and its patch lattice
        gx, gy, c = x0 + 18, 110, 5
        body += patch(gx, gy, lat, c, 1)
        step = p * (c + 1)
        for k in range(n_side + 1):
            body += (f'<line x1="{gx + k * step - 0.5:.1f}" y1="{gy - 0.5}" x2="{gx + k * step - 0.5:.1f}" '
                     f'y2="{gy + 32 * (c + 1) - 0.5}" stroke="{ACCENT}" stroke-width="0.9" opacity="0.9"/>')
            body += (f'<line x1="{gx - 0.5}" y1="{gy + k * step - 0.5:.1f}" x2="{gx + 32 * (c + 1) - 0.5}" '
                     f'y2="{gy + k * step - 0.5:.1f}" stroke="{ACCENT}" stroke-width="0.9" opacity="0.9"/>')
        body += mono(gx + 96, gy + 210, f"{n_side}×{n_side} = {r['tokens']} patches", 8, ACCENT, "middle", 600)
        # readout
        rx = x0 + 232
        rows = [("tokens", f"{r['tokens']}"), ("token length", f"{4 * p * p} values"),
                ("parameters", f"{r['params']:,}"), ("compute (lab)", f"{r['gmac']:.2f} GMAC"),
                ("compute (paper)", f"{DIT_PAPER_GFLOPS[p]} Gflops"),
                ("FID-50K (paper)", f"{DIT_FID[p]}")]
        yy = 124
        for k, (a, b) in enumerate(rows):
            body += mono(rx, yy, a.upper(), 7, SOFT, "start")
            col = ACCENT if (p == 2 and a in ("tokens", "compute (lab)", "FID-50K (paper)")) else INK
            body += text(rx, yy + 15, b, 11, col, MONO, 600, "start")
            yy += 32
        # the token sequence each block sees
        body += mono(x0 + 18, 352, f"THE SEQUENCE EVERY ONE OF 28 BLOCKS PROCESSES · {r['tokens']} × 1,152", 7.5, SOFT, "start")
        body += cells(x0 + 18, 364, 32, r["tokens"] // 32, 9, 2,
                      ACCENT_TINT if p == 2 else "#ffffff", ACCENT if p == 2 else RULE_SOLID)
    body += verdict(40, 488, 880, "Same 28 blocks, ×4 tokens: ×4.08 compute, parameters unchanged to 0.01%, "
                                   "FID 43.01 → 19.47 at 400K steps.")
    body += footnote(vh - 20, "Compute and parameters measured by the lab; Gflops and FID from DiT's Table 4 "
                              "(ImageNet 256×256, 400K steps, no guidance).")
    emit(6, "dit-two-patch-sizes", "DiT at two patch sizes",
         "Halving the patch quadruples the tokens every block sees, not the weights.",
         body, "DiT-XL/4 and DiT-XL/2 lattices and their compute", vw, vh)


# -------------------------------------------------------------------- fig 09

def fig09():
    vw, vh = 960, 340
    d24, call = MMDIT["d24"], MMDIT["call_1024"]
    ps, fs = d24["params_split"], call["flops_by_stream"]
    body = eyebrow(60, 44, "sd3 mm-dit, depth 24 (2b) · one 1024×1024 call: 4,096 image + 154 text tokens · measured")
    x0, w = 230, 680
    colours = {"image": (BLUE, "rgba(94,122,155,0.30)"), "text": (MUSTARD, "rgba(184,145,90,0.35)"),
               "joint_attention_core": (ACCENT, "rgba(235,108,54,0.45)"),
               "outside_blocks": (SOFT, "rgba(122,131,153,0.25)")}
    bars = [("PARAMETERS", f"{d24['params'] / 1e6:,.1f}M", d24["params"],
             [("image", ps["image"], f"image stream {ps['image'] / 1e6:,.1f}M"),
              ("text", ps["text"], f"text stream {ps['text'] / 1e6:,.1f}M"),
              ("outside_blocks", ps["outside_blocks"], "")]),
            ("FLOPS PER CALL", f"{call['flops'] / 1e9:,.0f} GFLOP", call["flops"],
             [("image", fs["image"], f"image stream {fs['image'] / 1e9:,.0f}"),
              ("joint_attention_core", fs["joint_attention_core"],
               f"joint attention {fs['joint_attention_core'] / 1e9:,.0f}"),
              ("text", fs["text"], ""), ("outside_blocks", fs["outside_blocks"], "")])]
    y = 96
    for title, total_, tot, segs in bars:
        body += mono(60, y + 18, title, 8, INK, "start", 600)
        body += mono(60, y + 33, total_, 8, SOFT, "start")
        x = x0
        for key, v, lab in segs:
            sw = v / tot * w
            stroke, fill = colours[key]
            body += rect(x, y, max(sw, 0.8), 44, fill, stroke, 2, 1)
            if lab and sw > 120:
                body += mono(x + sw / 2, y + 20, lab.upper(), 7.5, INK, "middle", 600)
                body += mono(x + sw / 2, y + 34, f"{100 * v / tot:.1f}%", 8, INK, "middle")
            x += sw
        y += 92
    # the small text-stream FLOP share, labelled outside its sliver
    tx = x0 + (fs["image"] + fs["joint_attention_core"]) / call["flops"] * w
    sliver = fs["text"] / call["flops"] * w
    body += path_line([(tx + sliver / 2, 232), (tx + sliver / 2, 252), (tx - 40, 252)], MUSTARD, 1, arrow=False)
    body += mono(tx - 46, 256, f"text stream {fs['text'] / 1e9:.1f} GFLOP · "
                               f"{100 * fs['text'] / call['flops']:.1f}%", 8, MUSTARD, "end", 600)
    body += mono(x0, 290, f"outside the blocks: {ps['outside_blocks'] / 1e6:.1f}M parameters, "
                          f"{fs['outside_blocks'] / 1e9:.1f} GFLOP (thin grey slivers)", 8, SOFT, "start")
    body += footnote(vh - 14, "Built from SD3's sizing rule (width 64·d, d heads) through diffusers' SD3 implementation; "
                              "the last block's text stream stops after attention.")
    emit(9, "mmdit-params-vs-flops-by-stream", "Half the weights, a sliver of the arithmetic",
         "SD3's text stream costs parameters by width and FLOPs by tokens.",
         body, "Parameters and FLOPs of SD3's 2B MM-DiT by stream", vw, vh)


# -------------------------------------------------------------------- fig 10

def fig10():
    vw, vh = 960, 500
    body = eyebrow(60, 44, "attention's share of one transformer block = N / (N + 6D) · width D, 4× mlp")
    ax = Axes(110, 80, 780, 320, (math.log10(0.03), math.log10(30)), (0, 80), logx=True)
    xt = [(0.05, "0.05"), (0.1, "0.1"), (0.3, "0.3"), (1, "1"), (3, "3"), (10, "10"), (30, "30")]
    body += ax.frame(xt, [(v, f"{v}%") for v in (0, 20, 40, 60, 80)],
                     "TOKENS PER UNIT OF WIDTH, N / D  (LOG SCALE)", "SHARE OF THE BLOCK'S FLOPS")
    for share, r, lab in ((100 / 3, 3, "N = 3D · one third"), (50, 6, "N = 6D · one half")):
        body += (f'<line x1="{ax.X(0.03):.1f}" y1="{ax.Y(share):.1f}" x2="{ax.X(r):.1f}" y2="{ax.Y(share):.1f}" '
                 f'stroke="{RULE_SOLID}" stroke-dasharray="3,3"/>')
        body += (f'<line x1="{ax.X(r):.1f}" y1="{ax.Y(share):.1f}" x2="{ax.X(r):.1f}" y2="{ax.Y(0):.1f}" '
                 f'stroke="{RULE_SOLID}" stroke-dasharray="3,3"/>')
        if r == 3:
            body += tag(ax.X(r) - 6, ax.Y(0) - 8, lab.upper(), SOFT, "end", 7.5)
        else:
            body += tag(ax.X(r) + 6, ax.Y(0) - 8, lab.upper(), SOFT, "start", 7.5)
    pts = [(10 ** (math.log10(0.03) + i * (math.log10(30) - math.log10(0.03)) / 300)) for i in range(301)]
    body += ax.path([(r, 100 * r / (r + 6)) for r in pts], INK, 2.2)
    D = ATT["width"]
    names = {64: "DiT-XL block at 64 tokens", 256: "DiT-XL/2 at 256 px · 256 tokens",
             1024: "DiT-XL/2 at 512 px · 1,024 tokens", 4096: "DiT-XL block at 4,096 tokens (1024 px)",
             16384: "DiT-XL block at 16,384 tokens (2048 px)"}
    key = []
    for i, row in enumerate(ATT["flops"], start=1):
        r, s = row["tokens"] / D, 100 * row["share"]
        body += ax.dot(r, s, 4.5, INK)
        body += tag(ax.X(r) - 9, ax.Y(s) - 9, str(i), INK, "end", 8.5, 600)
        key.append((str(i), f"{names[row['tokens']]} · N/D = {r:.2f} · {s:.1f}%", INK))
    c = MMDIT["call_1024"]
    r = c["joint_tokens"] / MMDIT["d24"]["width"]
    s = 100 * c["flops_by_stream"]["joint_attention_core"] / c["flops"]
    body += ax.dot(r, s, 5.5, ACCENT)
    body += tag(ax.X(r) - 10, ax.Y(s) - 10, "S", ACCENT, "end", 8.5, 600)
    key.append(("S", f"SD3-2B, whole 1024 px call · N = 4,250, D = 1,536 · N/D = {r:.2f} · {s:.1f}%", ACCENT))
    kx, ky = 132, 96
    body += rect(kx, ky, 430, 26 + 16 * len(key), "#ffffff", RULE_SOLID, 5, 1)
    body += mono(kx + 12, ky + 17, "MEASURED POINTS", 7.5, SOFT, "start", 600)
    for j, (k, line, col) in enumerate(key):
        body += mono(kx + 14, ky + 34 + 16 * j, k, 8, col, "start", 600)
        body += mono(kx + 30, ky + 34 + 16 * j, line, 8, col, "start")
    body += footnote(vh - 28, "Dots: FLOP counts measured by the lab. Line: the closed form N/(N+6D), not a fit.")
    body += footnote(vh - 14, "Resolutions assume a latent factor of 8 and a 2×2 patch.")
    emit(10, "attention-share-of-a-block", "When attention takes over",
         "Attention's share depends only on tokens per unit of width.",
         body, "Attention share of a transformer block against N over D", vw, vh)


# -------------------------------------------------------------------- fig 11

def fig11():
    vw, vh = 960, 448
    rows = ATT["cpu"]
    body = eyebrow(60, 44, "one 16-head attention layer, head width 72, fp32, batch 1 · amd ryzen 7 5825u, 8 threads · measured")
    xr = (math.log10(200), math.log10(5200))
    xt = [(256, "256"), (1024, "1,024"), (2048, "2,048"), (4096, "4,096")]
    panels = [(90, "TIME PER CALL (MS, LOG)", "ms", (math.log10(0.4), math.log10(2000)),
               [(1, "1"), (10, "10"), (100, "100"), (1000, "1,000")], "naive_ms", "fused_ms"),
              (540, "LARGEST SINGLE ALLOCATION (MB, LOG)", "MB", (math.log10(0.7), math.log10(3000)),
               [(1, "1"), (10, "10"), (100, "100"), (1000, "1,000")], "naive_largest_alloc_MB",
               "fused_largest_alloc_MB")]
    for x0, title, unit, yr, yt, kn, kf in panels:
        ax = Axes(x0, 90, 316, 240, xr, yr, logx=True, logy=True)
        body += mono(x0, 78, title, 8, SOFT, "start")
        body += ax.frame(xt, yt, "TOKENS N", "")
        if unit == "MB":
            body += ax.path([(r["tokens"], r["score_matrix_MB_fp32"]) for r in rows], SOFT, 1.4, dash=True)
            body += tag(ax.X(1024) - 6, ax.Y(rows[1]["score_matrix_MB_fp32"]) - 18,
                        "16·N²·4 BYTES: THE SCORE MATRIX", SOFT, "end", 7.5)
        for key, colour, name in ((kn, INK, "naive"), (kf, ACCENT, "fused")):
            body += ax.path([(r["tokens"], r[key]) for r in rows], colour, 2)
            for r in rows:
                body += ax.dot(r["tokens"], r[key], 3.5, colour)
            last = rows[-1]
            body += tag(ax.X(last["tokens"]) + 10, ax.Y(last[key]) + 4,
                        f"{name} {last[key]:,.1f} {unit}" if unit == "MB" else f"{name} {last[key]:,.0f} {unit}",
                        colour, "start", 8.5, 600)
    nv, fu = rows[-1], rows[-1]
    body += verdict(90, 376, 800, f"At 4,096 tokens: same arithmetic, {nv['naive_ms'] / fu['fused_ms']:.1f}× "
                                   f"the time and {nv['naive_largest_alloc_MB'] / fu['fused_largest_alloc_MB']:.0f}× "
                                   f"the largest allocation for the naive path.")
    body += footnote(vh - 28, "Naive: softmax(QKᵀ/√d)·V written out. Fused: torch.nn.functional.scaled_dot_product_attention, "
                              "profiler op _scaled_dot_product_flash_attention_for_cpu.")
    body += footnote(vh - 14, "Times vary between runs and machines; the arithmetic of the two paths is identical.")
    emit(11, "naive-vs-fused-attention-cpu", "Same FLOPs, different bytes",
         "The fused kernel never stores the N×N score matrix.",
         body, "Naive and fused attention time and memory against token count", vw, vh)


# -------------------------------------------------------------------- fig 12

def fig12():
    vw, vh = 960, 470
    mem = {r["model"]: r for r in MEM}
    sd15, d512, s2 = (mem["SD 1.5 U-Net, 512px"], mem["DiT-XL/2, 512px"],
                      mem["SD3 MM-DiT d=24, 1024px"])
    enc = sum(v for _, v in SD3_ENCODERS_GB)
    t5 = SD3_ENCODERS_GB[0][1]
    body = eyebrow(60, 44, "memory per image, decimal gb, one scale for both panels · computed from measured parameter counts")
    W_ = (INK, "rgba(45,49,66,0.55)")
    ENC = (MUSTARD, "rgba(184,145,90,0.40)")
    ST = (BLUE, "rgba(94,122,155,0.30)")
    ACT = (SAGE, "rgba(124,143,111,0.40)")
    SC = (ACCENT, "rgba(235,108,54,0.45)")
    x0, scale = 250, 560 / 95            # px per GB, shared by both panels

    def hbar(y, segs, total_label, colour=INK):
        out, x = "", x0
        for v, (stroke, fill) in segs:
            out += rect(x, y, max(v * scale, 0.8), 22, fill, stroke, 2, 1)
            x += v * scale
        out += mono(x + 8, y + 15, total_label, 8.5, colour, "start", 600)
        return out

    # gridlines and the shared axis
    top, bottom = 92, 384
    for g_ in (0, 20, 40, 60, 80):
        gx = x0 + g_ * scale
        body += (f'<line x1="{gx:.1f}" y1="{top}" x2="{gx:.1f}" y2="{bottom}" stroke="{RULE}" stroke-width="0.8"/>')
        body += mono(gx, bottom + 14, f"{g_} GB", 7, SOFT)

    body += mono(60, 86, "INFERENCE · WHAT MUST BE LOADED", 8, SOFT, "start", 600)
    irows = [("SD 1.5 U-Net", [(sd15["weights_bf16_GB"], W_)], f"{sd15['weights_bf16_GB']:.2f}"),
             ("DiT-XL/2", [(d512["weights_bf16_GB"], W_)], f"{d512['weights_bf16_GB']:.2f}"),
             ("SD3-2B denoiser", [(s2["weights_bf16_GB"], W_)], f"{s2['weights_bf16_GB']:.2f}"),
             ("SD3-2B + its encoders", [(s2["weights_bf16_GB"], W_), (enc, ENC)],
              f"{s2['weights_bf16_GB'] + enc:.2f} · T5-XXL alone {t5}, "
              f"{t5 / s2['weights_bf16_GB']:.1f}× the denoiser")]
    y = 98
    for name, segs, lab in irows:
        body += text(60, y + 15, name, 10.5, INK, SANS, 600, "start")
        body += hbar(y, segs, lab)
        y += 32

    body += mono(60, 248, "TRAINING · ONE IMAGE AT A TIME", 8, SOFT, "start", 600)
    trows = [("SD 1.5 U-Net · 512 px", [(sd15["train_state_GB"], ST)],
              f"{sd15['train_state_GB']:.1f} + activations (U-Net: no closed form here)"),
             ("DiT-XL/2 · 512 px", [(d512["train_state_GB"], ST), (d512["train_activations_no_scores_GB"], ACT),
                                     (d512["train_activations_GB"] - d512["train_activations_no_scores_GB"], SC)],
              f"{d512['train_state_GB'] + d512['train_activations_GB']:.1f}"),
             ("SD3-2B · 1024 px", [(s2["train_state_GB"], ST), (s2["train_activations_no_scores_GB"], ACT),
                                    (s2["train_activations_GB"] - s2["train_activations_no_scores_GB"], SC)],
              f"{s2['train_state_GB'] + s2['train_activations_GB']:.1f}")]
    y = 260
    for name, segs, lab in trows:
        body += text(60, y + 15, name, 10.5, INK, SANS, 600, "start")
        body += hbar(y, segs, lab)
        y += 40
    # legend
    lx, ly = 60, 428
    for name, (stroke, fill) in (("bf16 weights", W_), ("frozen encoders", ENC),
                                 ("training state, 16 B/param", ST), ("activations without scores", ACT),
                                 ("stored attention scores", SC)):
        body += rect(lx, ly - 9, 12, 12, fill, stroke, 2, 1)
        body += mono(lx + 18, ly + 1, name, 8, MUTED, "start")
        lx += 34 + len(name) * 5.2
    body += footnote(vh - 14, "Training state per ZeRO (weights included); activations per Korthikanti et al.'s "
                              "per-layer count, an upper estimate. Encoders: SD3's own load measurement.")
    emit(12, "the-memory-bill", "The memory bill",
         "Weights are the small part; encoders and activations dominate at 1024 px.",
         body, "Inference and training memory per model", vw, vh)


# -------------------------------------------------------------------- fig 13

def fig13():
    vw, vh = 960, 480
    body = eyebrow(60, 40, "where measured models sit · attention tokens per unit of width at the largest grid they attend over")
    ax = Axes(250, 78, 660, 300, (math.log10(0.1), math.log10(30)), (0, 3))
    bands = [(2, "updated text tokens", "joint attention (MM-DiT)"),
             (1, "fixed text tokens", "cross-attention"),
             (0, "one vector: timestep, class", "adaLN")]
    for b, name, mech in bands:
        y0, y1 = ax.Y(b + 1), ax.Y(b)
        body += rect(ax.x, y0, ax.w, y1 - y0, "rgba(45,49,66,0.03)" if b % 2 == 0 else "#ffffff",
                     RULE_SOLID, 0, 0.6)
        body += text(60, (y0 + y1) / 2 - 2, name, 10.5, INK, SANS, 600, "start")
        body += mono(60, (y0 + y1) / 2 + 14, mech.upper(), 7.5, SOFT, "start")
    for r, lab in ((3, "N = 3D"), (6, "N = 6D")):
        x = ax.X(math.log10(r))
        body += (f'<line x1="{x:.1f}" y1="{ax.y}" x2="{x:.1f}" y2="{ax.y + ax.h}" stroke="{ACCENT if r == 6 else RULE_SOLID}" '
                 f'stroke-width="{1.4 if r == 6 else 1}" stroke-dasharray="5,4"/>')
        body += mono(x, ax.y - 8, lab, 8, ACCENT if r == 6 else SOFT, "middle", 600)
    for v, lab in ((0.1, "0.1"), (0.3, "0.3"), (1, "1"), (3, "3"), (10, "10"), (30, "30")):
        x = ax.X(math.log10(v))
        body += mono(x, ax.y + ax.h + 16, lab, 7, SOFT)
    body += mono(ax.x + ax.w / 2, ax.y + ax.h + 34, "N / D  (LOG SCALE)", 8, SOFT)
    D = ATT["width"]
    s2 = MMDIT["call_1024"]
    pts = [
        (256 / D, 0, "DiT-XL/2 · 256 px", INK, False, (0, -14, "middle")),
        (1024 / D, 0, "DiT-XL/2 · 512 px", INK, False, (0, -14, "middle")),
        (16384 / D, 0, "DiT-XL/2 · 2048 px", INK, True, (0, -14, "middle")),
        (4096 / 640, 1, "SDXL · 64×64 level", BLUE, False, (12, -14, "start")),
        (4096 / 320, 1, "SD 1.5 · 64×64 level", BLUE, False, (-68, 26, "start")),
        (s2["joint_tokens"] / MMDIT["d24"]["width"], 2, "SD3-2B · 1024 px", ACCENT, False, (-12, -14, "end")),
    ]
    for r, band, name, colour, hollow, (dx, dy, anc) in pts:
        x, y = ax.X(math.log10(r)), (ax.Y(band) + ax.Y(band + 1)) / 2
        if hollow:
            body += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{PAPER}" stroke="{colour}" stroke-width="1.6"/>')
        else:
            body += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="{colour}"/>'
        body += tag(x + dx, y + dy, f"{name} · {r:.2f}", colour, anc, 8, 600)
    body += mono(ax.X(math.log10(0.12)), ax.y + ax.h - 8, "← UNIFORM TRANSFORMER PAYS OFF", 7.5, MUTED, "start", 600)
    body += mono(ax.X(math.log10(28)), ax.y + ax.h - 8, "ATTENTION DOMINATES →", 7.5, MUTED, "end", 600)
    body += footnote(vh - 42, "Right of N = 6D, attention is over half of a transformer block: go hierarchical "
                              "(U-Net, U-DiT), local (HDiT), or at least fused.")
    body += footnote(vh - 28, "U-Net positions use the width at their finest attended grid (320 for SD 1.5, 640 for SDXL); "
                              "SDXL removed attention from its 128×128 level.")
    body += footnote(vh - 14, "Hollow: DiT-XL/2 run at 2048 px, a configuration it was not trained at, shown for its token count.")
    emit(13, "when-to-swap-the-backbone", "When to swap",
         "Swap when the token count or the conditioning changes, not when the parameter count does.",
         body, "Decision map of backbones by token count and conditioning", vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    body = eyebrow(72, 73, "diffusion · part four")
    body += text(72, 148, "Diffusion backbones, block by block", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "U-Net · DiT · MM-DiT — where the weights live and the compute goes", 15, MUTED,
                 MONO, 400, "start")

    # left: a U, to scale (height ∝ grid side, width ∝ channels), with its skips
    levels = [(64, 320), (32, 640), (16, 1280), (8, 1280)]
    down_x = [96, 150, 204, 258]
    up_x = [462, 408, 354, 300]
    base = 250
    ys = {}
    for i, (res, ch) in enumerate(levels):
        h, w = res * 2.0, ch / 1280 * 30 + 8
        y = base + i * 46
        ys[i] = (y, h, w)
        body += rect(down_x[i], y, w, h, "rgba(45,49,66,0.08)", INK, 2, 1.2)
        if i < 3:
            body += rect(up_x[i] + 30 - w, y, w, h, "rgba(45,49,66,0.08)", INK, 2, 1.2)
            body += (f'<line x1="{down_x[i] + w + 4}" y1="{y + 10}" x2="{up_x[i] + 30 - w - 4}" y2="{y + 10}" '
                     f'stroke="{LINK}" stroke-width="1.2" stroke-dasharray="5,4"/>')
    body += mono(282, 470, "U-NET · 64² → 8² → 64² · 12 SKIPS", 10, MUTED, "middle", 500)

    # middle: the crescent, noised, with its 2x2 patch lattice
    N = 12
    noisy = noisy_motif(N)
    gx, gy, c = 520, 252, 13
    body += patch(gx, gy, noisy, c, 1)
    step = 2 * (c + 1)
    for k in range(N // 2 + 1):
        body += (f'<line x1="{gx + k * step - 0.5}" y1="{gy - 0.5}" x2="{gx + k * step - 0.5}" '
                 f'y2="{gy + N * (c + 1) - 0.5}" stroke="{ACCENT}" stroke-width="1.4"/>')
        body += (f'<line x1="{gx - 0.5}" y1="{gy + k * step - 0.5}" x2="{gx + N * (c + 1) - 0.5}" '
                 f'y2="{gy + k * step - 0.5}" stroke="{ACCENT}" stroke-width="1.4"/>')
    body += h_arrow(700, 336, 760, ACCENT, accent=True)

    # right: the token strip
    tx, ty = 778, 300
    for i in range(36):
        r, col = divmod(i, 12)
        body += rect(tx + col * 28, ty + r * 26, 22, 20, ACCENT_TINT, ACCENT, 2, 1)
    body += mono(946, 470, "DIT · 2×2 PATCHES → 36 TOKENS", 10, MUTED, "middle", 500)

    body += (f'<line x1="72" y1="508" x2="1128" y2="508" stroke="{RULE}" stroke-width="1"/>')
    body += text(72, 548, "Count tokens, not parameters.", 20, MUTED, SERIF, 400, "start", italic=True)
    emit_cover(body, "A U-shaped stack of shrinking feature maps beside the noisy crescent patch cut into 2×2 "
                     "patches and laid out as a strip of tokens")


# keyed by the figure number that reaches the post; 4, 7 and 8 are Mermaid figures
FIGURES = {1: fig01, 2: fig02, 3: fig03, 5: fig05, 6: fig06, 9: fig09, 10: fig10, 11: fig11,
           12: fig12, 13: fig13}

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
