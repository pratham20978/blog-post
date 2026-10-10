#!/usr/bin/env python3
"""Figures for "Where the Diffusion MSE Loss Comes From" (diffusion-models, part 3).

Every number drawn here comes from ../lab/loss_identities.py — the same module the
article's lab download ships — so the prose, the figures and the lab cannot drift
apart. Measured numbers (Figures 6 and 12) are typed once, below, with their ledger
keys, because they are quotations from papers rather than computations.

    python3 _figures.py            # all placed/plot/chart figures plus the cover
    python3 _figures.py 1 5        # just those
    python3 _figures.py cover      # just the cover
Figure 10 is Mermaid:  python3 _mermaid.py fig-10-three-formulations-one-object
"""

from __future__ import annotations

import math
import pathlib
import sys

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUSTARD, MUTED, PAPER, RULE, RULE_SOLID,
    SAGE, SERIF, SOFT, emit, emit_cover, eyebrow, h_arrow, mono, node, rect, subtext, text,
    v_arrow,
)

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lab"))
import loss_identities as L  # noqa: E402

STEP = L.coarse_step()
A, S = math.sqrt(L.ABAR_T), math.sqrt(1 - L.ABAR_T)          # 0.8, 0.6
LAM_WORKED = math.log(L.snr(L.ABAR_T))                        # 0.575


# ------------------------------------------------------------------ primitives

class Axes:
    """Data-to-pixel mapping for a real plot. log=True puts y on log10."""

    _n = 0

    def __init__(self, x, y, w, h, xr, yr, logy=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr, self.logy = xr, yr, logy
        Axes._n += 1
        self.clip = f"clip{Axes._n}"

    def X(self, v):
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
            cx, cy = self.x - 58, self.y + self.h / 2
            out += (f'<g transform="rotate(-90 {cx} {cy})">'
                    + mono(cx, cy, ylabel, 8, SOFT) + '</g>')
        return out

    def path(self, pts, colour=INK, width=1.8, dash=None, opacity=1.0):
        d = ' stroke-dasharray="6,4"' if dash else ""
        s = " ".join(f"{self.X(a):.1f},{self.Y(b):.1f}" for a, b in pts)
        return (f'<g clip-path="url(#{self.clip})"><polyline points="{s}" fill="none" '
                f'stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" '
                f'stroke-linecap="round" opacity="{opacity}"{d}/></g>')

    def fn(self, f, colour=INK, width=1.8, dash=None, n=400, opacity=1.0):
        a, b = self.xr
        return self.path([(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)],
                         colour, width, dash, opacity)

    def dot(self, a, b, r=4, colour=ACCENT, opacity=1.0):
        return (f'<circle cx="{self.X(a):.1f}" cy="{self.Y(b):.1f}" r="{r}" '
                f'fill="{colour}" opacity="{opacity}"/>')

    def vline(self, a, colour=RULE_SOLID, dash=True, y0=None, y1=None, width=1):
        d = ' stroke-dasharray="3,3"' if dash else ""
        top = self.y if y0 is None else self.Y(y0)
        bot = self.y + self.h if y1 is None else self.Y(y1)
        return (f'<line x1="{self.X(a):.1f}" y1="{top:.1f}" x2="{self.X(a):.1f}" '
                f'y2="{bot:.1f}" stroke="{colour}" stroke-width="{width}"{d}/>')


def gpdf(x, m, v):
    return math.exp(-(x - m) ** 2 / (2 * v)) / math.sqrt(2 * math.pi * v)


def plate(x, y, w, h=16):
    return rect(x, y, w, h, PAPER, "none", 3)


def tag(x, y, value, fill=INK, anchor="middle", size=9, weight=500, bg=True, w=None):
    """A label on an opaque plate so a curve passing behind it cannot cut it."""
    w = w or len(value) * size * 0.62 + 10
    left = x - w / 2 if anchor == "middle" else (x - 5 if anchor == "start" else x - w + 5)
    out = plate(left, y - size - 2, w, size + 7) if bg else ""
    return out + text(x, y, value, size, fill, MONO, weight, anchor)


def rich(x, y, value, size=10, fill=INK, weight=500, anchor="middle", family=MONO):
    """Text where `_x` or `_{xyz}` becomes a real subscript: 'L_T', 'L_{simple}'."""
    import html as _h, re as _re
    parts, pos = [], 0
    for m in _re.finditer(r"_\{([^}]*)\}|_(\S)", value):
        parts.append((value[pos:m.start()], False))
        parts.append((m.group(1) or m.group(2), True))
        pos = m.end()
    parts.append((value[pos:], False))
    inner, low = "", False
    sub = round(size * 0.68, 2)
    shift = round(size * 0.25, 2)
    for chunk, is_sub in parts:
        if not chunk:
            continue
        if is_sub and not low:
            inner += f'<tspan font-size="{sub}" dy="{shift}">{_h.escape(chunk)}</tspan>'
            low = True
        elif is_sub:
            inner += f'<tspan font-size="{sub}">{_h.escape(chunk)}</tspan>'
        elif low:
            inner += f'<tspan font-size="{size}" dy="{-shift}">{_h.escape(chunk)}</tspan>'
            low = False
        else:
            inner += f'<tspan>{_h.escape(chunk)}</tspan>'
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-family="{family}" '
            f'font-weight="{weight}" text-anchor="{anchor}">{inner}</text>')


def rtag(x, y, value, fill=INK, anchor="middle", size=9, weight=500, w=None):
    """rich() on an opaque plate."""
    import re as _re
    plain = _re.sub(r"_\{([^}]*)\}|_(\S)", lambda m: m.group(1) or m.group(2), value)
    w = w or len(plain) * size * 0.62 + 10
    left = x - w / 2 if anchor == "middle" else (x - 5 if anchor == "start" else x - w + 5)
    return plate(left, y - size - 2, w, size + 7) + rich(x, y, value, size, fill, weight, anchor)


def verdict(x, y, w, body):
    out = rect(x, y, w, 30, ACCENT_TINT, ACCENT, 4, 1)
    out += text(x + 14, y + 19, body, 10, INK, MONO, 500, "start")
    return out


def panel(x, y, w, h, rows, title):
    """A readout box: title, then (label, value, colour) rows. h=None fits the rows."""
    if h is None:
        h = 50 + sum(8 if r[0] == "---" else 22 for r in rows) + 4
    out = rect(x, y, w, h, "#ffffff", RULE_SOLID, 5, 1)
    out += mono(x + 16, y + 24, title, 8, SOFT, "start")
    yy = y + 50
    for label, value, colour in rows:
        if label == "---":
            out += (f'<line x1="{x + 16}" y1="{yy - 10}" x2="{x + w - 16}" y2="{yy - 10}" '
                    f'stroke="{RULE}" stroke-width="0.8"/>')
            yy += 8
            continue
        out += rich(x + 16, yy, label, 10, MUTED, 400, "start")
        out += rich(x + w - 16, yy, value, 11, colour, 600, "end")
        yy += 22
    return out


def footnote(y, value, x=60):
    return mono(x, y, value, 8, SOFT, "start")


# ------------------------------------------------ the series motif (from part 1)

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


def patch(x, y, M, cell=8, gap=1, lo=-1.2, hi=1.2):
    """High value = bright, the series' display convention."""
    out = ""
    for r, row in enumerate(M):
        for c, v in enumerate(row):
            u = min(1.0, max(0.0, (v - lo) / (hi - lo)))
            g = round(26 + u * (250 - 26))
            out += (f'<rect x="{x + c * (cell + gap)}" y="{y + r * (cell + gap)}" width="{cell}" '
                    f'height="{cell}" rx="1" fill="rgb({g},{g},{g})"/>')
    return out


# -------------------------------------------------------------------- fig 01

def fig01():
    """The teacher is a precision sum; the student is the teacher, shifted."""
    vw, vh = 1120, 600
    c = STEP
    ax = Axes(110, 110, 680, 330, (-0.45, 1.85), (0.0, 1.30))
    body = eyebrow(60, 52, "one reverse step on one pixel, coarse chain ᾱ 0.80 → 0.64")
    body += ax.frame([(v, f"{v:.1f}") for v in (-0.4, 0.0, 0.4, 0.8, 1.2, 1.6)],
                     [(v, f"{v:.1f}") for v in (0.4, 0.8, 1.2)],
                     "value of the pixel one step earlier,  xₜ₋₁", "probability density")

    curves = [
        (c["m_from_x0"], c["v_from_x0"], BLUE, None, 1.6),
        (c["m_from_xt"], c["v_from_xt"], MUSTARD, None, 1.6),
        (c["teacher_mean"], c["teacher_var"], INK, None, 2.4),
        (c["student_mean"], c["teacher_var"], ACCENT, True, 2.2),
    ]
    for m, v, col, dash, wd in curves:
        body += ax.fn(lambda x, m=m, v=v: gpdf(x, m, v), col, wd, dash)

    # name each curve beside its own peak, on a plate
    peak = lambda v: 1 / math.sqrt(2 * math.pi * v)
    body += tag(ax.X(1.55), ax.Y(0.72),
                f"from x₀:  N({c['m_from_x0']:.4f}, 0.20)", BLUE, size=9)
    body += tag(ax.X(-0.02), ax.Y(0.98),
                f"from xₜ:  N({c['m_from_xt']:.4f}, 0.25)", MUSTARD, size=9)
    body += tag(ax.X(c["teacher_mean"]) + 118, ax.Y(peak(c["teacher_var"])) + 14,
                f"teacher  N({c['teacher_mean']:.4f}, 1/9)", INK, size=9, weight=600)
    body += tag(ax.X(c["student_mean"]) - 116, ax.Y(peak(c["teacher_var"])) + 14,
                f"student  N({c['student_mean']:.4f}, 1/9)", ACCENT, size=9, weight=600)

    # the gap between centres, drawn at the top of the two peaks
    top = ax.Y(peak(c["teacher_var"])) - 16
    xa, xb = ax.X(c["student_mean"]), ax.X(c["teacher_mean"])
    body += ax.vline(c["student_mean"], ACCENT, True, 0, peak(c["teacher_var"]))
    body += ax.vline(c["teacher_mean"], INK, True, 0, peak(c["teacher_var"]))
    body += (f'<line x1="{xa:.1f}" y1="{top:.1f}" x2="{xb:.1f}" y2="{top:.1f}" '
             f'stroke="{ACCENT}" stroke-width="1.6"/>'
             f'<line x1="{xa:.1f}" y1="{top - 5:.1f}" x2="{xa:.1f}" y2="{top + 5:.1f}" stroke="{ACCENT}" stroke-width="1.6"/>'
             f'<line x1="{xb:.1f}" y1="{top - 5:.1f}" x2="{xb:.1f}" y2="{top + 5:.1f}" stroke="{ACCENT}" stroke-width="1.6"/>')
    body += tag((xa + xb) / 2, top - 10, f"gap {abs(c['gap']):.4f}", ACCENT, size=9, weight=600)

    body += panel(836, 118, 232, None, [
        ("precision from x₀", f"{1 / c['v_from_x0']:.0f}", BLUE),
        ("precision from xₜ", f"{1 / c['v_from_xt']:.0f}", MUSTARD),
        ("teacher precision", "5 + 4 = 9", INK),
        ("---", "", INK),
        ("network's x̂₀", f"{c['x0_hat']:.2f}", ACCENT),
        ("gap²", f"{c['gap'] ** 2:.6f}", ACCENT),
        ("KL = gap² ÷ (2/9)", f"{c['kl']:.4f}", ACCENT),
    ], "THE ARITHMETIC")

    body += verdict(60, vh - 78, 1008,
                    "Same width, so the KL can only see where the centres sit: a squared error between two means.")
    body += footnote(vh - 26, "x₀ = 0.95, ε = −0.55, xₜ = 0.43; β = 0.20, α = 0.80. "
                     "Densities computed from the stated Gaussians, not measured.")

    emit(1, "teacher-and-student", "The teacher and the student",
         "Two Gaussian pieces of evidence, their product, and the network's step, for one pixel",
         body,
         "Four bell curves over the previous pixel value: evidence from the clean pixel centred "
         "at 0.85, evidence from the noisy pixel at 0.48, their product the teacher at 0.69, and "
         "the student at 0.61", vw, vh)


# -------------------------------------------------------------------- fig 02

def fig02():
    """One error, five prices: a ledger of real values with proportional bars."""
    vw, vh = 1160, 500
    rows = L.five_prices()
    c = STEP
    body = eyebrow(60, 52, "one prediction error of +0.20, priced five ways at ᾱ = 0.64")

    cols = [60, 250, 360, 470, 580, 860, 1000]
    heads = ["network predicts", "true", "predicted", "error", "squared error",
             "× constant", "noise units"]
    y0 = 104
    for x, h in zip(cols, heads):
        anchor = "start" if x in (60, 580, 860) else "end"
        hx = x if anchor == "start" else x + 70
        body += mono(hx, y0, h.upper(), 8, SOFT, anchor)
    body += (f'<line x1="60" y1="{y0 + 12}" x2="1100" y2="{y0 + 12}" '
             f'stroke="{RULE_SOLID}" stroke-width="1"/>')

    names = {"epsilon": ("noise ε", "× 1"), "x0": ("clean pixel x₀", "× SNR 1.7778"),
             "score": ("score −ε / 0.6", "× (1−ᾱ) 0.36"),
             "v": ("velocity 0.8ε − 0.6x₀", "× ᾱ 0.64")}
    scale = 200 / 0.12                                    # px per unit of squared error
    y = y0 + 52
    for name, true, pred, sq, conv in rows:
        label, const = names[name]
        body += text(60, y, label, 11, INK, MONO, 600, "start")
        body += text(cols[1] + 70, y, f"{true:+.4f}", 11, MUTED, MONO, 400, "end")
        body += text(cols[2] + 70, y, f"{pred:+.4f}", 11, MUTED, MONO, 400, "end")
        body += text(cols[3] + 70, y, f"{pred - true:+.4f}", 11, INK, MONO, 500, "end")
        body += rect(580, y - 13, sq * scale, 16, "rgba(46,90,168,0.16)", LINK, 2, 0.9)
        body += text(580 + sq * scale + 8, y, f"{sq:.4f}", 10, LINK, MONO, 600, "start")
        body += text(860, y, const, 10, MUTED, MONO, 400, "start")
        body += text(1070, y, f"{sq * conv:.4f}", 12, INK, MONO, 600, "end")
        y += 58

    # the ELBO row, in accent
    body += (f'<line x1="60" y1="{y - 34}" x2="1100" y2="{y - 34}" '
             f'stroke="{RULE}" stroke-width="0.8"/>')
    body += text(60, y, "this step's KL (the bound)", 11, ACCENT, MONO, 600, "start")
    body += rect(580, y - 13, c["kl"] * scale, 16, ACCENT_TINT, ACCENT, 2, 1.2)
    body += text(580 + c["kl"] * scale + 8, y, f"{c['kl']:.4f}", 10, ACCENT, MONO, 600, "start")
    body += text(860, y, f"= {c['weight']:.3f} × 0.0400", 10, ACCENT, MONO, 500, "start")
    body += text(1070, y, f"{c['kl']:.4f}", 12, ACCENT, MONO, 600, "end")

    body += verdict(60, vh - 78, 1040,
                    "At one noise level the losses are one number times a constant, so they share a minimiser.")
    body += footnote(vh - 26, "Top-left pixel of part 1's patch: x₀ = 0.95, ε = −0.55, predicted noise "
                     "−0.35, xₜ = 0.43. KL on the coarse chain ᾱ 0.80 → 0.64, reverse variance 1/9.")

    emit(2, "one-error-five-prices", "One error, five prices",
         "The same +0.20 noise error expressed in every target a diffusion network is trained on",
         body,
         "Five rows pricing one prediction error: noise, clean pixel, score, velocity and the "
         "ELBO step, each with its squared error as a bar and the constant that converts it "
         "back to 0.04", vw, vh)


# -------------------------------------------------------------------- fig 03

def fig03():
    """VAE, hierarchical VAE, diffusion: which arrows are learned."""
    vw, vh = 1200, 500
    body = eyebrow(60, 52, "diffusion is a hierarchical VAE with a frozen encoder")
    nw, nh = 88, 60
    fy, ry = 150, 214          # forward arrows above node row, reverse below
    rowy = 162

    def pair(x1, x2, enc_col, enc_lab, dec_lab, enc_dash=False):
        out = h_arrow(x1 + nw, rowy + 12, x2, enc_col, dashed=enc_dash)
        out += h_arrow(x2, rowy + nh - 12, x1 + nw, ACCENT, accent=True)
        mid = (x1 + nw + x2) / 2
        out += tag(mid, rowy - 4, enc_lab, enc_col, size=8, bg=True)
        out += tag(mid, rowy + nh + 20, dec_lab, ACCENT, size=8, bg=True)
        return out

    panels = [
        (60, "VARIATIONAL AUTOENCODER", [(("x", ""), "data"), (("z", ""), "smaller latent")],
         MUTED, "qφ learned", "pθ learned", False,
         ["1 latent, smaller than x", "encoder and decoder both trained"]),
        (426, "HIERARCHICAL VAE", [(("x", ""), "data"), (("z", "1"), ""), (("z", "2"), "")],
         MUTED, "qφ", "pθ", False,
         ["a chain of latents", "every arrow trained"]),
        (792, "DIFFUSION MODEL", [(("x", "0"), "image"), (("x", "t"), "same size"), (("x", "T"), "≈ N(0, I)")],
         SOFT, "q fixed", "pθ", True,
         ["latents the size of the image", "only the reverse arrows trained"]),
    ]
    for px, title, nodes, ecol, elab, dlab, dash, notes in panels:
        body += mono(px, 112, title, 8, INK if px != 792 else ACCENT, "start")
        gapw = 42 if len(nodes) == 3 else 130
        xs = [px + i * (nw + gapw) for i in range(len(nodes))]
        for (nm, sub), x in zip(nodes, xs):
            kind = "focal" if (px == 792 and nm == ("x", "0")) else "normal"
            body += node(x, rowy, nw, nh, nm, sub, kind)
        for a, b in zip(xs, xs[1:]):
            body += pair(a, b, ecol, elab, dlab, dash)
        for i, note in enumerate(notes):
            body += text(px, 282 + i * 20, note, 10, MUTED, MONO, 400, "start")

    # the one sentence that makes it a bound, placed under the panels
    body += rect(60, 340, 1080, 62, "#ffffff", RULE_SOLID, 5, 1)
    body += text(80, 364, "log p(x) = ELBO + KL( encoder ‖ true posterior )", 12, INK, MONO, 600, "start")
    body += text(80, 388, "In a VAE either side can shrink that gap. In diffusion the encoder "
                 "cannot move, so the reverse chain must close it alone.", 10, MUTED, MONO, 400, "start")

    body += verdict(60, vh - 70, 1080,
                    "Set T = 1 and the diffusion bound is the ordinary VAE bound; freeze the encoder and every KL becomes Gaussian.")

    emit(3, "diffusion-is-a-fixed-encoder-vae", "Diffusion is a VAE with a frozen encoder",
         "Three graphical models side by side, marking which arrows are learned",
         body,
         "Three small graphical models side by side: a VAE with a learned encoder, a "
         "hierarchical VAE with a chain of learned encoders, and a diffusion model whose "
         "encoder chain is fixed and whose latents have the image's size", vw, vh)


# -------------------------------------------------------------------- fig 04

def fig04():
    """The chain with the three kinds of ELBO term bracketed where they act."""
    vw, vh = 1180, 440
    body = eyebrow(60, 52, "where each term of the bound lives on the chain")
    nw, nh = 96, 50
    rowy = 120
    names = [("x", "0"), ("x", "1"), ("x", "t−1"), ("x", "t"), ("x", "T")]
    xs = [70, 250, 500, 680, 960]
    for (b, s), x in zip(names, xs):
        kind = "focal" if s == "0" else "normal"
        body += node(x, rowy, nw, nh, (b, s), "", kind)
    # ellipses where steps are elided
    for xm in ((xs[1] + nw + xs[2]) / 2, (xs[3] + nw + xs[4]) / 2):
        body += text(xm, rowy + 30, "· · ·", 16, SOFT, MONO, 400)

    # forward (fixed) above, reverse (learned) below, only between drawn neighbours
    for a, b in ((0, 1), (2, 3)):
        x1, x2 = xs[a] + nw, xs[b]
        body += h_arrow(x1, rowy + 13, x2, SOFT, dashed=True)
        body += h_arrow(x2, rowy + nh - 13, x1, ACCENT, accent=True)
    body += tag((xs[0] + nw + xs[1]) / 2, rowy - 6, "q fixed", SOFT, size=8)
    body += tag((xs[0] + nw + xs[1]) / 2, rowy + nh + 20, "pθ(x₀ | x₁)", ACCENT, size=8)
    body += tag((xs[2] + nw + xs[3]) / 2, rowy - 6, "q(xₜ | xₜ₋₁) fixed", SOFT, size=8)
    body += tag((xs[2] + nw + xs[3]) / 2, rowy + nh + 20, "pθ(xₜ₋₁ | xₜ)", ACCENT, size=8)

    def bracket(x1, x2, y, col, title, formula, note, theta):
        out = (f'<path d="M{x1},{y} v10 H{x2} v-10" fill="none" stroke="{col}" '
               f'stroke-width="1.4"/>')
        cx = (x1 + x2) / 2
        out += rich(cx, y + 34, title, 11, col, 600)
        out += rich(cx, y + 54, formula, 10, INK, 500)
        out += text(cx, y + 72, note, 9, MUTED, MONO, 400)
        out += text(cx, y + 90, theta, 9, col, MONO, 600)
        return out

    by = rowy + nh + 44
    body += bracket(xs[0], xs[1] + nw, by, ACCENT, "L₀  reconstruction",
                    "−log pθ(x₀ | x₁)", "discrete decoder, once", "trains θ")
    body += bracket(xs[2], xs[3] + nw, by, ACCENT, "Lₜ₋₁  denoising matching",
                    "KL( q(xₜ₋₁|xₜ,x₀) ‖ pθ(xₜ₋₁|xₜ) )",
                    "teacher sees x₀, student does not · t = 2 … T", "trains θ at every noise level")
    body += bracket(xs[4] - 40, xs[4] + nw + 40, by, SOFT, "L_T  prior matching",
                    "KL( q(x_T | x₀) ‖ N(0, I) )", "≈ 1e-5 bits/dim in DDPM", "no θ: a constant")


    body += verdict(60, vh - 74, 1060,
                    "Only the middle bracket repeats. Every noise level the denoiser learns, it learns there.")

    emit(4, "where-each-elbo-term-lives", "Where each term of the bound lives",
         "The diffusion chain with the prior, denoising-matching and reconstruction terms marked",
         body,
         "The chain from x-zero to x-T with three brackets: the prior term at the noise end, one "
         "denoising-matching term per intermediate step, and the reconstruction term at the image "
         "end, each marked with whether it touches the network", vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    """DDPM's per-step ELBO weight across its real schedule, against L_simple's 1."""
    vw, vh = 1120, 600
    wb = L.elbo_weights(variance="beta")
    wt = L.elbo_weights(variance="beta_tilde")
    _, abar = L.ddpm_linear()
    ax = Axes(120, 110, 690, 330, (0, 1000), (-3.0, 0.4), logy=True)
    body = eyebrow(60, 52, "the per-step weight the simple loss replaces with 1")
    body += ax.frame([(v, str(v)) for v in (2, 200, 400, 600, 800, 1000)],
                     [(10 ** e, lab) for e, lab in ((-3, "0.001"), (-2, "0.01"), (-1, "0.1"), (0, "1"))],
                     "diffusion step t   (DDPM: T = 1000, β from 1e-4 to 0.02)",
                     "weight on ‖ε − ε̂‖²   (log scale)")
    body += ax.path([(t, 1.0) for t in (0, 1000)], ACCENT, 2.2)
    body += ax.path(sorted(wt.items()), BLUE, 1.4, dash=True)
    body += ax.path(sorted(wb.items()), INK, 2.0)

    lo_t = min(wb, key=wb.get)
    marks = [(2, wb[2], "t = 2:  0.2727", 70, -12),
             (lo_t, wb[lo_t], f"minimum t = {lo_t}:  {wb[lo_t]:.5f}", 0, 34),
             (1000, wb[1000], f"t = 1000:  {wb[1000]:.4f}", -84, -16)]
    for t, v, lab, dx, dy in marks:
        body += ax.dot(t, v, 4.5, INK)
        body += tag(ax.X(t) + dx, ax.Y(v) + dy, lab, INK, size=9)
    body += ax.dot(207, wb[207], 5, ACCENT)
    body += tag(ax.X(207) + 6, ax.Y(wb[207]) - 16, f"ᾱ ≈ 0.64 (t = 207): {wb[207]:.5f}",
                ACCENT, anchor="start", size=9)
    body += rtag(ax.X(640), ax.Y(1.0) + 20, "L_{simple}: 1 at every step", ACCENT, size=9, weight=600)
    body += tag(ax.X(2) + 14, ax.Y(wt[2]) - 2, f"posterior variance (dashed): {wt[2]:.4f} at t = 2",
                BLUE, anchor="start", size=8)

    body += panel(846, 118, 222, None, [
        ("largest (t = 2)", f"{wb[2]:.4f}", INK),
        (f"smallest (t = {lo_t})", f"{wb[lo_t]:.5f}", INK),
        ("ratio", f"{wb[2] / wb[lo_t]:.0f} ×", ACCENT),
        ("---", "", INK),
        ("simple loss, every t", "1", ACCENT),
    ], "INSIDE THE BOUND, σ² = β")

    body += verdict(60, vh - 78, 1008,
                    "Per step, the bound pays the most for the nearly clean ones; the simple loss pays every step the same.")
    body += footnote(vh - 26, "Computed from Ho et al. (2020) eq. 12 and the published linear "
                     "schedule; not a measurement. t = 1 is the decoder term and is not drawn.")

    emit(5, "the-weight-ddpm-dropped", "The weight DDPM dropped",
         "DDPM's per-step ELBO weight on the noise error across 1,000 steps",
         body,
         "Log-scale curve of the per-step ELBO weight across 1,000 DDPM steps: 0.27 at the second "
         "step, falling to a minimum of 0.005 near step 349, rising to 0.010 at the last step, "
         "beside a flat line at 1 for the simple loss", vw, vh)


# -------------------------------------------------------------------- fig 06

# Measured. Ledger L10 (Ho et al. 2020, Table 1) and L42 (Nichol & Dhariwal 2021, Table 2).
MEASURED_DDPM = [("true bound L", 3.70, 13.51), ("L_{simple}", 3.75, 3.17)]
MEASURED_IDDPM = [("L_{vlb} (bound)", 2.94, 11.47), ("L_{hybrid}", 3.17, 3.19), ("L_{simple}", 3.26, 3.05)]


def fig06():
    vw, vh = 1160, 470
    body = eyebrow(60, 52, "measured: the bound buys likelihood and costs sample quality")
    groups = [("DDPM · CIFAR-10 · T = 1000, linear, fixed Σ", MEASURED_DDPM),
              ("IMPROVED DDPM · CIFAR-10 · 500K iters, T = 4000, cosine", MEASURED_IDDPM)]
    panels = [("NLL, bits per dimension — lower is better", 1, 4.0, 340),
              ("FID — lower is better", 2, 14.0, 300)]
    x0s = [260, 740]
    y = 118
    body += mono(x0s[0], y, panels[0][0].upper(), 8, SOFT, "start")
    body += mono(x0s[1], y, panels[1][0].upper(), 8, SOFT, "start")
    y += 30
    for gname, rows in groups:
        body += mono(60, y, gname, 8, INK, "start")
        y += 18
        for x0 in x0s:                      # zero baseline, drawn per group
            body += (f'<line x1="{x0}" y1="{y - 4}" x2="{x0}" y2="{y + 30 * len(rows) - 8}" '
                     f'stroke="{RULE_SOLID}" stroke-width="1"/>')
        for name, nll, fid in rows:
            is_bound = "bound" in name
            col = INK if is_bound else (ACCENT if name == "L_{simple}" else BLUE)
            body += rich(240, y + 13, name, 10, col, 600, "end")
            for (label, idx, vmax, wmax), x0 in zip(panels, x0s):
                val = nll if idx == 1 else fid
                bw = val / vmax * wmax
                fill = {INK: "rgba(45,49,66,0.14)", ACCENT: ACCENT_TINT,
                        BLUE: "rgba(94,122,155,0.18)"}[col]
                body += rect(x0, y, bw, 18, fill, col, 2, 1)
                pre = "≤ " if (idx == 1 and rows is MEASURED_DDPM) else ""
                body += text(x0 + bw + 8, y + 13, f"{pre}{val:.2f}", 10, col, MONO, 600, "start")
            y += 30
        y += 22
    for x0 in x0s:
        body += mono(x0, y - 12, "0", 7, SOFT)

    body += verdict(60, vh - 96, 1040,
                    "Within each paper the ordering is the same. Do not compare numbers across the two groups.")
    body += footnote(vh - 46, "DDPM: Ho et al. (2020) Table 1, unconditional CIFAR-10, FID against the "
                     "training set, NLL an upper bound on the test set.")
    body += footnote(vh - 28, "Improved DDPM: Nichol & Dhariwal (2021) Table 2; the hybrid and bound runs use "
                     "learned variances, and the bound run importance-samples t.")

    emit(6, "bound-versus-samples", "Bound versus samples",
         "Negative log-likelihood and FID for the true bound, the hybrid loss and the simple loss",
         body,
         "Two bar panels of CIFAR-10 results: negative log-likelihood in bits per dimension and FID "
         "for the true bound, the hybrid loss and the simple loss, from the DDPM and Improved DDPM "
         "papers with their setups labelled", vw, vh)


# -------------------------------------------------------------------- fig 07

def weightings():
    sech = lambda z: 1 / math.cosh(z)
    norm = lambda l: math.exp(-(l - 2.4) ** 2 / (2 * 2.4 ** 2)) / (2.4 * math.sqrt(2 * math.pi))
    raw = {
        "ELBO": (lambda l: 1.0, INK, 2.4, None),
        "ε-prediction, cosine": (lambda l: sech(l / 2), BLUE, 1.8, None),
        "v-prediction, cosine": (lambda l: math.exp(-l / 2), SAGE, 1.8, None),
        "EDM": (lambda l: norm(l) * (math.exp(-l) + 0.25), MUSTARD, 1.8, None),
        "Min-SNR, γ = 5": (lambda l: sech(l / 2) * min(1.0, 5 * math.exp(-l)), LINK, 1.6, True),
    }
    # scaled to 1 at SNR = 1 (λ = 0), so every curve passes through one shared point
    return {k: (lambda l, f=f: f(l) / f(0.0), col, wd, dash)
            for k, (f, col, wd, dash) in raw.items()}


def fig07():
    vw, vh = 1160, 620
    W = weightings()
    ax = Axes(120, 110, 700, 340, (-10, 10), (-3.0, 2.3), logy=True)
    body = eyebrow(60, 52, "every published loss is one integral over log-SNR with its own weight")
    body += ax.frame([(v, f"{v:+d}" if v else "0") for v in (-10, -6, -2, 0, 2, 6, 10)],
                     [(10 ** e, lab) for e, lab in ((-3, "0.001"), (-2, "0.01"), (-1, "0.1"),
                                                    (0, "1"), (1, "10"), (2, "100"))],
                     "log-SNR  λ   ←  noisier        cleaner  →",
                     "weight on ‖ε − ε̂‖², scaled to 1 at λ = 0 (log)")
    body += ax.vline(LAM_WORKED, ACCENT, True)
    for k, (f, col, wd, dash) in W.items():
        body += ax.fn(f, col, wd, dash)

    # names placed where each curve is alone
    body += tag(ax.X(-3.0), ax.Y(30), "v-prediction, cosine", SAGE, size=9)
    body += tag(ax.X(6.4), ax.Y(1.0) - 12, "ELBO: flat", INK, size=9, weight=600)
    body += tag(ax.X(-3.2), ax.Y(0.09), "ε-prediction, cosine", BLUE, size=9)
    body += tag(ax.X(6.9), ax.Y(0.004), "Min-SNR, γ = 5 (dashed)", LINK, size=9)
    body += tag(ax.X(5.2), ax.Y(W["EDM"][0](5.2)) - 14, "EDM", MUSTARD, size=9)
    body += tag(ax.X(LAM_WORKED) + 6, ax.y + 14, "worked example, λ = 0.575", ACCENT,
                anchor="start", size=8)

    rows = [(k, f"{W[k][0](LAM_WORKED):.2f}", W[k][1]) for k in W]
    body += panel(858, 118, 250, None, rows, "WEIGHT AT λ = 0.575")

    body += verdict(60, vh - 96, 1048,
                    "Only the ELBO treats every noise level alike. Picking a target or a loss is picking one of these curves.")
    body += footnote(vh - 46, "Curves evaluated from the weighting formulas tabulated by Kingma & Gao "
                     "(2023, Table 1); not measured. DDPM's linear schedule covers λ from −10.1 to +9.2.")
    body += footnote(vh - 28, "Scaled to 1 at SNR = 1 so the curves share a point; overall constants "
                     "do not change which prediction minimises a loss.")

    emit(7, "one-loss-many-weightings", "One loss, many weightings",
         "Published diffusion losses as weighting functions over log signal-to-noise ratio",
         body,
         "Weighting curves over log signal-to-noise ratio for the ELBO, epsilon and velocity "
         "prediction with the cosine schedule, EDM and Min-SNR, with the worked example's noise "
         "level marked", vw, vh)


# -------------------------------------------------------------------- fig 08

def fig08():
    vw, vh = 1160, 740
    z = 0.43
    wts = L.posterior_weights(z, A, S)
    mean = L.ideal_denoiser(z, A, S)
    sc = L.score(z, A, S)
    body = eyebrow(60, 52, "the ideal denoiser is a weighted average; the score points at it")

    # --- top: the number line with posterior weights -------------------------
    top = Axes(120, 100, 700, 170, (-1.25, 1.25), (0, 1.0))
    base = top.y + top.h
    body += (f'<line x1="{top.x}" y1="{base}" x2="{top.x + top.w}" y2="{base}" '
             f'stroke="{RULE_SOLID}" stroke-width="1"/>')
    for v in (-1.0, -0.5, 0.0, 0.5, 1.0):
        body += mono(top.X(v), base + 16, f"{v:+.1f}" if v else "0", 7, SOFT)
    body += mono(top.x + top.w / 2, base + 34, "clean pixel value  x₀", 8, SOFT)
    for x0, w in zip(L.DATA_LEVELS, wts):
        bx = top.X(x0)
        body += rect(bx - 22, base - w * 150, 44, w * 150, "rgba(46,90,168,0.16)", LINK, 2, 1)
        body += tag(bx, base - w * 150 - 10, f"weight {w:.3f}", LINK, size=9)
        body += (f'<circle cx="{bx:.1f}" cy="{base}" r="5" fill="{INK}"/>')
    body += (f'<line x1="{top.X(mean):.1f}" y1="{base - 150}" x2="{top.X(mean):.1f}" '
             f'y2="{base}" stroke="{ACCENT}" stroke-width="2"/>')
    body += tag(top.X(mean), base - 162, f"E[x₀ | xₜ] = {mean:.4f}", ACCENT, size=9, weight=600)

    # noisy scale: the same number line after the √ᾱ = 0.8 shrink
    ny = base + 100
    body += (f'<line x1="{top.x}" y1="{ny}" x2="{top.x + top.w}" y2="{ny}" '
             f'stroke="{RULE_SOLID}" stroke-width="1"/>')
    body += mono(top.x - 10, ny + 3, "NOISY SCALE", 7, SOFT, "end")
    for x0 in L.DATA_LEVELS:
        body += (f'<circle cx="{top.X(A * x0):.1f}" cy="{ny}" r="5" fill="{PAPER}" '
                 f'stroke="{INK}" stroke-width="1.4"/>')
        body += mono(top.X(A * x0), ny + 20, f"0.8 × {x0:+.2f}", 7, SOFT)
    xt_x, am_x = top.X(z), top.X(A * mean)
    body += (f'<circle cx="{xt_x:.1f}" cy="{ny}" r="5" fill="{INK}"/>')
    body += tag(xt_x + 12, ny + 4, "xₜ = 0.43", INK, anchor="start", size=8)
    body += (f'<circle cx="{am_x:.1f}" cy="{ny}" r="5" fill="{ACCENT}"/>')
    for xx in (xt_x, am_x):                     # ticks tie the arrow to its two dots
        body += (f'<line x1="{xx:.1f}" y1="{ny - 7}" x2="{xx:.1f}" y2="{ny - 20}" '
                 f'stroke="{ACCENT}" stroke-width="1"/>')
    body += h_arrow(xt_x, ny - 16, am_x, ACCENT, accent=True)
    body += tag(am_x - 8, ny - 12, f"(1 − ᾱ) × score = {A * mean - z:+.4f}", ACCENT,
                anchor="end", size=8)

    body += panel(858, 100, 250, None, [
        ("xₜ", f"{z:.2f}", INK),
        ("E[x₀ | xₜ]", f"{mean:.4f}", ACCENT),
        ("√ᾱ · E[x₀ | xₜ]", f"{A * mean:.4f}", ACCENT),
        ("difference", f"{A * mean - z:+.4f}", INK),
        ("÷ (1 − ᾱ) = score", f"{sc:+.4f}", ACCENT),
    ], "TWEEDIE, ON THESE NUMBERS")

    # --- bottom: the score field over x_t, with the worked point -------------
    ax = Axes(120, 440, 700, 170, (-2.0, 2.0), (-4.0, 4.0))
    body += ax.frame([(v, f"{v:+.1f}" if v else "0") for v in (-2, -1, 0, 1, 2)],
                     [(v, f"{v:+d}" if v else "0") for v in (-4, -2, 0, 2, 4)],
                     "noisy value  xₜ   (ᾱ = 0.64)", "score  ∇ log q(xₜ)")
    body += ax.path([(-2, 0), (2, 0)], RULE_SOLID, 1)
    body += ax.fn(lambda x: L.score(x, A, S), ACCENT, 2.2)
    body += ax.fn(lambda x: A * L.ideal_denoiser(x, A, S) - x, INK, 1.4, dash=True)
    body += ax.dot(z, sc, 5, ACCENT)
    body += tag(ax.X(0.5), ax.Y(1.4), f"xₜ = 0.43  →  score {sc:+.3f}", ACCENT,
                anchor="start", size=9)
    body += tag(ax.X(-1.35), ax.Y(L.score(-1.35, A, S)) - 14, "score", ACCENT, size=9)
    body += tag(ax.X(-1.0), ax.Y(-0.9),
                "√ᾱ·E[x₀|xₜ] − xₜ  (dashed)", INK, size=8)
    body += panel(858, 440, 250, None, [
        ("dataset", "3 grey levels", INK),
        ("", "−0.85, 0.10, 0.95", INK),
        ("noise level", "ᾱ = 0.64", INK),
        ("score × 0.36", "= dashed curve", MUTED),
    ], "THE TOY DATASET")

    body += verdict(60, vh - 78, 1048,
                    "The ideal denoiser answers 0.40, not any clean value: it is right on average over every x₀ that fits.")
    body += footnote(vh - 26, "Exact posterior over the three crescent-motif grey levels, computed; "
                     "the score is checked against a finite difference of log q in the lab.")

    emit(8, "the-ideal-denoiser-is-an-average", "The ideal denoiser is an average",
         "Posterior weights over a three-value dataset, their average, and the score field it implies",
         body,
         "A noisy value on a line with three data values marked; bars show each value's posterior "
         "weight, the weighted average sits between them, and below it the score curve is marked "
         "at the noisy value", vw, vh)


# -------------------------------------------------------------------- fig 09

def fig09():
    vw, vh = 1160, 620
    dots = L.dsm_samples(600)
    bins = L.binned_means(L.dsm_samples(6000))
    ax = Axes(120, 100, 700, 360, (-2.2, 2.2), (-5.5, 5.5))
    body = eyebrow(60, 52, "denoising score matching: noisy targets, exact average")
    body += ax.frame([(v, f"{v:+.1f}" if v else "0") for v in (-2, -1, 0, 1, 2)],
                     [(v, f"{v:+d}" if v else "0") for v in (-4, -2, 0, 2, 4)],
                     "noisy value  xₜ   (ᾱ = 0.64)", "per-sample target  −ε / 0.6")
    body += ax.path([(-2.2, 0), (2.2, 0)], RULE_SOLID, 1)
    body += f'<g clip-path="url(#{ax.clip})">'
    for zz, yy in dots:
        body += ax.dot(zz, yy, 2.2, MUTED, 0.35)
    body += "</g>"
    body += ax.fn(lambda x: L.score(x, A, S), ACCENT, 2.4)
    for zc, m, _ in bins:
        body += (f'<rect x="{ax.X(zc) - 4:.1f}" y="{ax.Y(m) - 4:.1f}" width="8" height="8" '
                 f'fill="{INK}"/>')

    dev6 = max(abs(m - L.score(zc, A, S)) for zc, m, _ in bins)
    dev60 = max(abs(m - L.score(zc, A, S)) for zc, m, _ in L.binned_means(L.dsm_samples(60000)))
    rms = math.sqrt(sum(y * y for _, y in L.dsm_samples(6000)) / 6000)
    body += tag(ax.X(-1.55), ax.Y(L.score(-1.55, A, S)) - 16, "exact score", ACCENT, size=9, weight=600)

    body += panel(858, 108, 250, None, [
        ("dots shown", "600", MUTED),
        ("target RMS", f"{rms:.2f}", MUTED),
        ("---", "", INK),
        ("bin means from", "6,000", INK),
        ("worst bin error", f"{dev6:.2f}", INK),
        ("with 60,000", f"{dev60:.2f}", INK),
    ], "SAMPLES VS AVERAGES")
    body += rect(858, 300, 250, 82, "#ffffff", RULE_SOLID, 5, 1)
    body += (f'<circle cx="878" cy="321" r="3" fill="{MUTED}" opacity="0.5"/>')
    body += text(892, 325, "one (xₜ, −ε/0.6) pair", 9, MUTED, MONO, 400, "start")
    body += text(892, 343, "one line per clean level", 9, SOFT, MONO, 400, "start")
    body += rect(874, 357, 8, 8, INK, "none", 0, 0)
    body += text(892, 365, "mean target in a bin", 9, INK, MONO, 400, "start")

    body += verdict(60, vh - 78, 1048,
                    "Regression converges to the conditional mean of its target, and that mean is the score.")
    body += footnote(vh - 26, "Deterministic simulation from the lab script on the three-level dataset; "
                     "no network was trained. Bins are 0.25 wide.")

    emit(9, "noisy-targets-average-to-the-score", "Noisy targets average to the score",
         "Per-sample denoising-score-matching targets against the exact score of the noised data",
         body,
         "Scatter of six hundred noisy per-sample targets against the noisy value, spread widely, "
         "with binned averages of those targets lying on the exact score curve of the three-level "
         "dataset", vw, vh)


# -------------------------------------------------------------------- fig 11

def fig11():
    vw, vh = 1160, 600
    x0, eps = L.X0[0][0], L.EPS[0][0]
    ax = Axes(120, 100, 700, 350, (5.0, -4.0), (-3.4, 1.4))
    body = eyebrow(60, 52, "variance-preserving and variance-exploding: one path, rescaled")
    body += ax.frame([(v, f"{v:+d}" if v else "0") for v in (5, 3, 1, -1, -3)],
                     [(v, f"{v:+d}" if v else "0") for v in (-3, -2, -1, 0, 1)],
                     "log-SNR  λ   ←  cleaner        noisier  →", "value of the top-left pixel")
    lams = [5.0 - 9.0 * i / 300 for i in range(301)]
    rows = L.vp_ve_path(x0, eps, lams)
    body += ax.path([(r[0], r[2]) for r in rows], BLUE, 2.0)
    body += ax.path([(r[0], r[1]) for r in rows], INK, 2.6)
    body += ax.path([(r[0], r[3]) for r in rows], ACCENT, 2.0, dash=True)
    body += ax.vline(LAM_WORKED, ACCENT, True)
    w = L.vp_ve_path(x0, eps, [LAM_WORKED])[0]
    body += ax.dot(LAM_WORKED, w[1], 5, INK)
    body += ax.dot(LAM_WORKED, w[2], 5, BLUE)
    body += tag(ax.X(LAM_WORKED) + 8, ax.Y(w[2]) - 12, f"VE {w[2]:.4f}", BLUE, anchor="start", size=9)
    body += tag(ax.X(LAM_WORKED) + 8, ax.Y(w[1]) + 22, f"VP {w[1]:.2f}", INK, anchor="start", size=9)
    lx, ly = ax.X(4.6), ax.Y(-1.5)
    body += rect(lx - 12, ly - 22, 296, 96, "#ffffff", RULE_SOLID, 5, 1)
    for i, (col, dash, lab) in enumerate([(BLUE, "", "VE:  x₀ + σε,  σ = 1/√SNR"),
                                          (INK, "", "VP:  √ᾱ x₀ + √(1−ᾱ) ε"),
                                          (ACCENT, ' stroke-dasharray="6,4"', "√ᾱ × VE  — lands on VP")]):
        yy = ly + i * 26
        body += (f'<line x1="{lx}" y1="{yy - 4}" x2="{lx + 34}" y2="{yy - 4}" stroke="{col}" '
                 f'stroke-width="2.2"{dash}/>')
        body += text(lx + 46, yy, lab, 10, col, MONO, 500, "start")

    body += panel(858, 108, 250, None, [
        ("worked λ", "0.575", INK),
        ("σ_{VE} = 1/√SNR", f"{w[4]:.4f}", BLUE),
        ("VE value", f"{w[2]:.4f}", BLUE),
        ("× √ᾱ = 0.8", f"{w[3]:.4f}", ACCENT),
        ("VP value", f"{w[1]:.4f}", INK),
    ], "AT THE WORKED LEVEL")

    body += verdict(60, vh - 78, 1048,
                    "Same information at every noise level; only the scale differs, and the scale is known.")
    body += footnote(vh - 26, "Computed for x₀ = 0.95 with the fixed draw ε = −0.55 at every level; "
                     "real corruption draws fresh noise, the rescaling identity holds per draw.")

    emit(11, "vp-and-ve-are-one-path", "VP and VE are one path, rescaled",
         "The same pixel under variance-preserving and variance-exploding corruption",
         body,
         "Two trajectories of the top-left pixel against log signal-to-noise ratio: the VE value "
         "explodes past minus three as noise grows while the VP value stays within one, and the "
         "rescaled VE curve lies exactly on the VP curve", vw, vh)


# -------------------------------------------------------------------- fig 12

# Measured. Ledger L22 (Kingma et al. 2021, Table 2): T_train = T_eval, CIFAR-10 test BPD.
MEASURED_VDM = [("10", 4.31), ("100", 2.84), ("250", 2.73), ("500", 2.68),
                ("1,000", 2.67), ("10,000", 2.66), ("∞", 2.65)]


def fig12():
    vw, vh = 1120, 556
    body = eyebrow(60, 52, "measured: more steps give a tighter bound")
    x0, base, bw, gap = 150, 400, 88, 36
    ymax = 4.6
    hscale = 300 / ymax
    for v in (1, 2, 3, 4):
        y = base - v * hscale
        body += (f'<line x1="{x0 - 20}" y1="{y}" x2="{x0 + 7 * (bw + gap)}" y2="{y}" '
                 f'stroke="{RULE}" stroke-width="0.8"/>')
        body += mono(x0 - 30, y + 3, f"{v}.0", 7, SOFT, "end")
    body += (f'<line x1="{x0 - 20}" y1="{base}" x2="{x0 + 7 * (bw + gap)}" y2="{base}" '
             f'stroke="{RULE_SOLID}" stroke-width="1"/>')
    body += mono(x0 - 30, base + 3, "0", 7, SOFT, "end")
    for i, (lab, v) in enumerate(MEASURED_VDM):
        x = x0 + i * (bw + gap)
        col = ACCENT if lab == "∞" else INK
        fill = ACCENT_TINT if lab == "∞" else "rgba(45,49,66,0.12)"
        body += rect(x, base - v * hscale, bw, v * hscale, fill, col, 2, 1)
        body += text(x + bw / 2, base - v * hscale - 10, f"{v:.2f}", 11, col, MONO, 600)
        body += mono(x + bw / 2, base + 18, f"T = {lab}", 8, col)
    cont = base - 2.65 * hscale
    body += (f'<line x1="{x0 - 20}" y1="{cont}" x2="{x0 + 7 * (bw + gap)}" y2="{cont}" '
             f'stroke="{ACCENT}" stroke-width="1" stroke-dasharray="5,4"/>')
    body += (f'<g transform="rotate(-90 {x0 - 72} {base - 150})">'
             + mono(x0 - 72, base - 150, "test bits per dimension", 8, SOFT) + "</g>")
    body += mono(60, 76, "dashed line: the continuous-time value, 2.65", 8, ACCENT, "start")
    body += mono(x0 + 3.5 * (bw + gap) - gap / 2, base + 40,
                 "diffusion steps, same count in training and evaluation", 8, SOFT)

    body += verdict(60, vh - 78, 1000,
                    "Ten steps cost 1.66 bits per dimension over continuous time; a thousand cost 0.02.")
    body += footnote(vh - 26, "Kingma et al. (2021), Variational Diffusion Models, Table 2: CIFAR-10 "
                     "test set, same model family at every T. Zero baseline.")

    emit(12, "more-steps-tighter-bound", "More steps, tighter bound",
         "Measured CIFAR-10 bits per dimension against the number of diffusion steps",
         body,
         "Bits per dimension on the CIFAR-10 test set falling as the number of diffusion steps "
         "grows from 10 to 10,000, levelling toward the continuous-time value of 2.65", vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    """Series shell: eyebrow, serif title, kicker, and the teacher/student motif."""
    c = STEP
    body = eyebrow(72, 73, "diffusion · part three")
    body += text(72, 148, "Where the MSE loss comes from", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "a likelihood bound · one squared error per step", 15, MUTED,
                 MONO, 400, "start")

    ax = Axes(200, 250, 800, 220, (-0.2, 1.6), (0, 1.3))
    ax.clip = "coverclip"
    body += (f'<defs><clipPath id="{ax.clip}"><rect x="{ax.x}" y="{ax.y - 4}" '
             f'width="{ax.w}" height="{ax.h + 8}"/></clipPath></defs>')
    body += (f'<line x1="{ax.x}" y1="{ax.y + ax.h}" x2="{ax.x + ax.w}" y2="{ax.y + ax.h}" '
             f'stroke="{RULE_SOLID}" stroke-width="1"/>')
    body += ax.fn(lambda x: gpdf(x, c["teacher_mean"], c["teacher_var"]), INK, 3.0)
    body += ax.fn(lambda x: gpdf(x, c["student_mean"], c["teacher_var"]), ACCENT, 3.0, dash=True)
    pk = 1 / math.sqrt(2 * math.pi * c["teacher_var"])
    xa, xb = ax.X(c["student_mean"]), ax.X(c["teacher_mean"])
    yy = ax.Y(pk) - 18
    body += (f'<line x1="{xa:.1f}" y1="{yy:.1f}" x2="{xb:.1f}" y2="{yy:.1f}" stroke="{ACCENT}" stroke-width="2"/>'
             f'<line x1="{xa:.1f}" y1="{yy - 6:.1f}" x2="{xa:.1f}" y2="{yy + 6:.1f}" stroke="{ACCENT}" stroke-width="2"/>'
             f'<line x1="{xb:.1f}" y1="{yy - 6:.1f}" x2="{xb:.1f}" y2="{yy + 6:.1f}" stroke="{ACCENT}" stroke-width="2"/>')
    body += text((xa + xb) / 2, yy - 12, "‖ gap ‖²", 16, ACCENT, MONO, 600)
    body += mono(ax.X(c["teacher_mean"]) + 150, ax.Y(0.9), "TEACHER  q(xₜ₋₁ | xₜ, x₀)", 9, INK, "start")
    body += mono(ax.X(c["student_mean"]) - 150, ax.Y(0.9), "STUDENT  pθ(xₜ₋₁ | xₜ)", 9, ACCENT, "end")

    # the crescent, clean and at the worked noise level, top right
    N = 12
    clean = motif(N)
    draw = L.lcg_normals(N * N, 7)
    noisy = [[A * clean[r][c] + S * draw[r * N + c] for c in range(N)] for r in range(N)]
    body += patch(860, 60, clean) + patch(1000, 60, noisy)
    body += h_arrow(972, 113, 994, MUTED)
    body += mono(913, 180, "x₀", 9, SOFT) + mono(1053, 180, "ᾱ = 0.64", 9, SOFT)

    body += (f'<line x1="72" y1="508" x2="1128" y2="508" '
             f'stroke="{RULE}" stroke-width="1"/>')
    body += text(72, 548, "Same width, so the only thing left to compare is the centres.", 20,
                 MUTED, SERIF, 400, "start", italic=True)

    emit_cover(body,
               "Two overlapping bell curves, the teacher's solid and the network's dashed, with the "
               "gap between their centres marked, under the line ‘Where the MSE loss comes from’")


# keyed by the figure number that reaches the post; 10 is the Mermaid figure
FIGURES = {1: fig01, 2: fig02, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07,
           8: fig08, 9: fig09, 11: fig11, 12: fig12}

if __name__ == "__main__":
    args = sys.argv[1:]
    wanted = [int(a) for a in args if a.isdigit()]
    for k in wanted:
        FIGURES[k]()
    if "cover" in args:
        cover()
    if not args:
        for fn in FIGURES.values():
            fn()
        cover()
