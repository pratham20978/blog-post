#!/usr/bin/env python3
"""Figures for "What a Diffusion Model Actually Does" (diffusion-models, part 1).

Every number drawn here is computed in this file, not typed in. The post's
worked example and these figures therefore cannot drift apart: if the arithmetic
changes, the picture changes with it.

    python3 _figures.py            # all figures plus the cover
    python3 _figures.py 2 4        # just those
    python3 _figures.py cover      # just the cover
"""

from __future__ import annotations

import math
import sys

from _build import (
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID,
    SERIF, SOFT, curve, emit, emit_cover, eyebrow, h_arrow, lcg, mono, plot_axes,
    rect, subtext, text,
)

# ---------------------------------------------------------------- the example

X0 = [[0.95, 0.60, -0.30, -0.85],
      [0.80, 0.45, -0.55, -0.90],
      [0.55, 0.10, -0.70, -0.95],
      [0.25, -0.20, -0.85, -1.00]]

EPS = [[-0.55, 1.40, 0.45, -1.10],
       [0.85, -1.35, -0.25, 0.70],
       [1.25, 0.30, -0.95, 0.15],
       [-1.05, 0.90, 1.45, -1.10]]

ABAR = 0.64                      # chosen so the coefficients are exactly 0.8/0.6
SQ = ABAR ** 0.5                 # 0.8
SQC = (1 - ABAR) ** 0.5          # 0.6


def scale(M, k):
    return [[k * v for v in row] for row in M]


def add(A, B):
    return [[A[r][c] + B[r][c] for c in range(len(A[0]))] for r in range(len(A))]


def mean_of(mats):
    n = len(mats)
    return [[sum(m[r][c] for m in mats) / n for c in range(len(mats[0][0]))]
            for r in range(len(mats[0]))]


SIG = scale(X0, SQ)              # 0.8 * x0
NOI = scale(EPS, SQC)            # 0.6 * eps
XT = add(SIG, NOI)               # x_t

LO, HI = -1.2, 1.2               # display range shared by every patch figure


# ------------------------------------------------------------------ primitives

def motif(n):
    """One recognisable image: a bright crescent on a dark field.

    Used at three sizes across the post so the reader tracks the SAME picture
    through the noise. A shape that survives corruption is the whole point of
    the figure, so it has to be legible at n = 8.
    """
    M = []
    c0 = (n - 1) / 2
    for r in range(n):
        row = []
        for c in range(n):
            d = (((r - c0) ** 2 + (c - c0) ** 2) ** 0.5) / (n / 2)
            v = 0.95 if d < 0.60 else (-0.85 if d > 0.78 else 0.10)
            d2 = ((((r - c0 + n * 0.17) ** 2 + (c - c0 + n * 0.17) ** 2) ** 0.5)
                  / (n / 2))
            if d < 0.60 and d2 < 0.46:
                v = -0.50
            row.append(v)
        M.append(row)
    return M


def gaussian(n, seed):
    """A unit-variance draw: sum of three uniforms, centred and scaled."""
    rng = lcg(seed)
    return [[(next(rng) + next(rng) + next(rng) - 1.5) * 2.0 for _ in range(n)]
            for _ in range(n)]


def corrupt(target, noise, abar):
    s, k = abar ** 0.5, (1 - abar) ** 0.5
    return [[s * target[r][c] + k * noise[r][c] for c in range(len(target[0]))]
            for r in range(len(target))]


def tone(v, lo=LO, hi=HI):
    """Map a signed pixel value to a greyscale fill. High value = bright."""
    u = min(1.0, max(0.0, (v - lo) / (hi - lo)))
    g = round(26 + u * (250 - 26))
    return f"rgb({g},{g},{g})"


def vgrid(x, y, M, cell=34, gap=3, values=False, size=9, accent=None,
          stroke=RULE_SOLID, lo=LO, hi=HI):
    """A patch drawn as a patch. `accent` is an (row, col) cell to ring."""
    out = ""
    for r, row in enumerate(M):
        for c, v in enumerate(row):
            cx, cy = x + c * (cell + gap), y + r * (cell + gap)
            hot = accent == (r, c)
            out += rect(cx, cy, cell, cell, tone(v, lo, hi),
                        ACCENT if hot else stroke, 2, 1.6 if hot else 0.7)
            if values:
                ink = "#ffffff" if (v - lo) / (hi - lo) < 0.46 else INK
                out += text(cx + cell / 2, cy + cell / 2 + size * 0.36,
                            f"{v:.2f}".replace("-0.00", "0.00"), size,
                            ACCENT if hot else ink, MONO, 600 if hot else 400)
    return out


def gw(cols, cell, gap):
    return cols * cell + (cols - 1) * gap


def cap(x, w, y, title, sub="", sub_fill=SOFT):
    """Centred label under a patch. `title` may be (base, subscript)."""
    if isinstance(title, tuple):
        out = subtext(x + w / 2, y, title[0], title[1], 12, INK, MONO, 600)
    else:
        out = text(x + w / 2, y, title, 11, INK, MONO, 600)
    if sub:
        out += mono(x + w / 2, y + 15, sub, 8, sub_fill)
    return out


def verdict(x, y, w, body):
    out = rect(x, y, w, 30, ACCENT_TINT, ACCENT, 4, 1)
    out += text(x + 14, y + 19, body, 10, INK, MONO, 500, "start")
    return out


def op(x, y, glyph):
    return text(x, y, glyph, 22, MUTED, MONO, 400)


# -------------------------------------------------------------------- fig 01

def fig01():
    """The asymmetry: forward is a formula, backward is the whole network."""
    vw, vh = 1060, 492
    N, cell, gap = 12, 11, 1
    w = gw(N, cell, gap)                       # 143

    target = motif(N)
    noise = gaussian(N, 31)
    levels = [(1.00, ("x", "0")), (0.96, ("x", "100")), (0.64, ("x", "t")),
              (0.25, ("x", "700")), (0.02, ("x", "T"))]

    xs = [60 + i * 196 for i in range(5)]
    top = 152

    body = eyebrow(60, 52, "the asymmetry that makes a diffusion model necessary")

    for (abar, name), x in zip(levels, xs):
        M = target if abar >= 1.0 else corrupt(target, noise, abar)
        body += vgrid(x, top, M, cell, gap, stroke="none")
        body += rect(x - 4, top - 4, w + 8, w + 8, "none", RULE_SOLID, 4, 0.9)
        body += cap(x, w, top + w + 24, name, f"ᾱ = {abar:.2f}")

    cx0, cx4 = xs[0] + w / 2, xs[-1] + w / 2

    # forward, above
    y_fwd = 118
    body += h_arrow(cx0, y_fwd, cx4, MUTED)
    body += rect(340, y_fwd - 32, 400, 24, PAPER, "none", 3)
    body += text(540, y_fwd - 14,
                 "xₜ = √ᾱₜ · x₀ + √(1−ᾱₜ) · ε",
                 13, INK, MONO, 600)
    body += rect(360, y_fwd + 4, 360, 20, PAPER, "none", 3)
    body += mono(540, y_fwd + 18, "forward · closed form · zero parameters", 9, MUTED)

    # reverse, below
    y_rev = 372
    body += h_arrow(cx4, y_rev, cx0, ACCENT, accent=True)
    body += rect(330, y_rev - 28, 420, 20, PAPER, "none", 3)
    body += mono(540, y_rev - 14, "reverse · no closed form · this is the network", 9, ACCENT)
    body += rect(350, y_rev + 8, 380, 24, PAPER, "none", 3)
    body += text(540, y_rev + 26,
                 "xₜ₋₁ = f( xₜ , t , εθ(xₜ, t) )",
                 13, ACCENT, MONO, 600)

    body += verdict(60, vh - 54, 940,
                    "Nothing on the top arrow is learned. Everything anyone trains lives on the bottom one.")

    emit(1, "forward-is-a-formula", "Forward is a formula, reverse is not",
         "The same crescent at five noise levels, with the direction that needs a network marked",
         body,
         "A crescent-shaped patch shown at five rising noise levels; the left-to-right arrow "
         "carries a closed-form equation with no parameters, the right-to-left arrow carries the "
         "learned network",
         vw, vh)


# -------------------------------------------------------------------- fig 02

def fig02():
    """The worked example, with every value on the page."""
    vw, vh = 1120, 560
    cell, gap = 46, 4
    w = gw(4, cell, gap)
    top = 132
    xs = [70, 70 + w + 96, 70 + 2 * (w + 96)]

    hot = (0, 1)        # 0.48 + 0.84 = 1.32, brighter than any original pixel
    hot2 = (3, 2)       # -0.68 + 0.87 = 0.19, a near-black pixel turned neutral

    body = eyebrow(70, 56, "one forward step, computed")
    panels = [(SIG, "0.8 · x₀", "surviving signal"),
              (NOI, "0.6 · ε", "injected noise"),
              (XT, ("x", "t"), "what the network is shown")]

    for (M, title, sub), x in zip(panels, xs):
        body += vgrid(x, top, M, cell, gap, values=True, size=11, accent=hot,
                      lo=-1.6, hi=1.6)
        r2, c2 = hot2
        body += rect(x + c2 * (cell + gap) - 3, top + r2 * (cell + gap) - 3,
                     cell + 6, cell + 6, "none", LINK, 3, 1.5)
        body += cap(x, w, top + w + 26, title, sub)

    body += op(xs[0] + w + 48, top + w / 2 + 8, "+")
    body += op(xs[1] + w + 48, top + w / 2 + 8, "=")

    y1 = top + w + 66
    body += rect(70, y1, 470, 54, "#ffffff", ACCENT, 4, 1)
    body += text(84, y1 + 22, "0.48  +  0.84  =  1.32", 12, ACCENT, MONO, 600, "start")
    body += text(84, y1 + 41, "brighter than 0.95, the brightest pixel x₀ had",
                 10, MUTED, MONO, 400, "start")

    body += rect(560, y1, 490, 54, "#ffffff", LINK, 4, 1)
    body += text(574, y1 + 22, "−0.68  +  0.87  =  0.19", 12, LINK, MONO, 600, "start")
    body += text(574, y1 + 41, "a near-black pixel arrives mid-grey",
                 10, MUTED, MONO, 400, "start")

    body += verdict(70, vh - 54, 980,
                    "ᾱₜ = 0.64, so the coefficients are exactly 0.8 and 0.6. The target is ε — we drew it, so we already know it.")

    emit(2, "one-forward-step", "One forward step on sixteen numbers",
         "0.8·x₀ plus 0.6·ε equals xₜ, with every intermediate value printed",
         body,
         "Three four-by-four grids of printed values, shaded by brightness: the scaled clean "
         "patch, the scaled noise, and their sum, with two cells traced through the addition",
         vw, vh)


# -------------------------------------------------------------------- fig 03

def fig03():
    """What one denoiser call returns: the average of every consistent x0."""
    vw, vh = 1180, 544
    N = 6

    def patch(kind):
        M = [[0.0] * N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                if kind == "v":
                    M[r][c] = 0.85 if c < 3 else -0.85
                elif kind == "h":
                    M[r][c] = 0.85 if r < 3 else -0.85
                elif kind == "d":
                    M[r][c] = 0.85 if (r + c) < 5 else -0.85
                else:
                    M[r][c] = 0.85 if max(abs(r - 2.5), abs(c - 2.5)) < 1.6 else -0.85
        return M

    cands = [patch(k) for k in ("v", "h", "d", "b")]
    avg = mean_of(cands)

    abar = 0.09
    s, k = abar ** 0.5, (1 - abar) ** 0.5          # 0.30 and 0.954
    draw = gaussian(N, 11)
    xt = corrupt(cands[0], draw, abar)

    # every candidate explains x_t with an equally ordinary noise draw
    stds = []
    for M in cands:
        imp = [(xt[r][c] - s * M[r][c]) / k for r in range(N) for c in range(N)]
        m = sum(imp) / len(imp)
        stds.append((sum((v - m) ** 2 for v in imp) / (len(imp) - 1)) ** 0.5)

    body = eyebrow(60, 52, "what a single denoiser call actually returns")

    # the observation
    ocell, ogap = 26, 3
    ow = gw(N, ocell, ogap)                      # 171
    ox, oy = 60, 170
    body += vgrid(ox, oy, xt, ocell, ogap, lo=-2.0, hi=2.0, stroke=RULE)
    body += rect(ox - 5, oy - 5, ow + 10, ow + 10, "none", INK, 4, 1.3)
    body += cap(ox, ow, oy + ow + 26, ("x", "t"), "ᾱ = 0.09 · the input")

    # the candidates, 2 x 2
    ccell, cgap = 18, 2
    cw = gw(N, ccell, cgap)                      # 118
    slots = [(384, 122), (574, 122), (384, 292), (574, 292)]
    names = ["vertical edge", "horizontal edge", "diagonal", "centre blob"]

    body += rect(352, 92, 372, 368, "none", RULE, 8, 1)
    body += mono(538, 80, "four of the many clean patches consistent with it", 9, SOFT)

    for M, (x, y), name, sd in zip(cands, slots, names, stds):
        body += vgrid(x, y, M, ccell, cgap, stroke=RULE)
        body += text(x + cw / 2, y + cw + 17, name, 9, INK, MONO, 500)
        body += text(x + cw / 2, y + cw + 31, f"needs ε of std {sd:.2f}", 8, SOFT, MONO, 400)

    # one connector into the group, landing head-on on its left edge
    body += h_arrow(ox + ow + 8, 276, 344, MUTED)

    # the average
    ax, ay = 900, 170
    body += vgrid(ax, ay, avg, ocell, ogap, stroke=RULE)
    body += rect(ax - 5, ay - 5, ow + 10, ow + 10, "none", ACCENT, 4, 1.5)
    body += cap(ax, ow, ay + ow + 26, "E[ x₀ | xₜ ]", "their average", ACCENT)
    body += h_arrow(736, ay + ow / 2, ax - 12, ACCENT, accent=True)
    body += rect(752, ay + ow / 2 - 30, 128, 18, PAPER, "none", 3)
    body += mono(816, ay + ow / 2 - 17, "mse optimum", 8, ACCENT)

    body += verdict(60, vh - 50, 1060,
                    "Squared-error training drives the network to the mean of the candidates, not to any one of them. That mean is the blur.")

    emit(4, "the-average-is-the-blur", "One call returns an average",
         "One noisy patch, four clean patches that could have produced it, and the mean the "
         "network is trained to output",
         body,
         "A noisy patch on the left fans out to four different clean patches, each needing an "
         "equally ordinary noise draw, and those four average on the right into a smeared "
         "grey patch",
         vw, vh)


# -------------------------------------------------------------------- fig 04

def fig04():
    """One jump versus eight steps, and the arithmetic that separates them."""
    vw, vh = 1180, 676
    N = 12
    target = motif(N)
    seed = gaussian(N, 97)

    def blurred(radius):
        """A genuine local mean: what an averaged estimate looks like."""
        M = [[0.0] * N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                acc = cnt = 0
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        rr, cc = r + dr, c + dc
                        if 0 <= rr < N and 0 <= cc < N:
                            acc += target[rr][cc]
                            cnt += 1
                M[r][c] = acc / cnt
        return M

    body = eyebrow(60, 52, "why the sampler takes many small steps")

    # ---- top lane: one call
    tcell, tgap = 14, 1
    tw = gw(N, tcell, tgap)                       # 179
    tx, ty = 70, 122
    body += mono(70, 104, "ONE CALL", 9, MUTED, "start")
    body += vgrid(tx, ty, corrupt(target, seed, 0.02), tcell, tgap, stroke="none")
    body += rect(tx - 4, ty - 4, tw + 8, tw + 8, "none", RULE_SOLID, 4, 0.9)
    body += cap(tx, tw, ty + tw + 24, ("x", "T"), "ᾱ = 0.02")

    a1, a2 = tx + tw + 20, tx + tw + 230
    body += h_arrow(a1, ty + tw / 2, a2, MUTED)
    body += rect((a1 + a2) / 2 - 92, ty + tw / 2 - 28, 184, 18, PAPER, "none", 3)
    body += mono((a1 + a2) / 2, ty + tw / 2 - 15, "one jump straight to x̂₀", 8, MUTED)

    bx = a2 + 20
    body += vgrid(bx, ty, blurred(2), tcell, tgap, stroke="none")
    body += rect(bx - 4, ty - 4, tw + 8, tw + 8, "none", RULE_SOLID, 4, 0.9)
    body += cap(bx, tw, ty + tw + 24, ("x̂", "0"), "an average, so a blur")

    body += rect(760, ty + 14, 330, 150, "#ffffff", RULE_SOLID, 5, 1)
    body += mono(776, ty + 38, "THE MULTIPLIER", 8, SOFT, "start")
    body += text(776, ty + 60, "an error of δ in the predicted noise",
                 10, INK, MONO, 500, "start")
    body += text(776, ty + 77, "lands as √(1−ᾱ)/√ᾱ × δ in the clean estimate",
                 10, INK, MONO, 500, "start")
    yy = ty + 88
    for abar in (0.02, 0.25, 0.64, 0.96):
        amp = ((1 - abar) ** 0.5) / (abar ** 0.5)
        hot = abar == 0.02
        body += text(790, yy + 16, f"ᾱ = {abar:.2f}", 10,
                     ACCENT if hot else MUTED, MONO, 500, "start")
        body += text(1000, yy + 16, f"× {amp:.2f}", 11,
                     ACCENT if hot else INK, MONO, 600, "end")
        yy += 18

    body += (f'<line x1="70" y1="370" x2="{vw - 70}" y2="370" '
             f'stroke="{RULE}" stroke-width="1"/>')

    # ---- bottom lane: eight calls
    scell, sgap = 7, 1
    sw = gw(N, scell, sgap)                       # 95
    step = 122                                    # must exceed sw, or the patches collide
    sx, sy = 70, 424
    body += mono(70, 406, "EIGHT CALLS, SAME STARTING NOISE", 9, ACCENT, "start")
    schedule = [0.02, 0.06, 0.14, 0.26, 0.42, 0.60, 0.79, 0.93, 1.00]
    for i, abar in enumerate(schedule):
        x = sx + i * step
        M = target if abar >= 1.0 else corrupt(target, seed, abar)
        body += vgrid(x, sy, M, scell, sgap, stroke="none")
        body += rect(x - 3, sy - 3, sw + 6, sw + 6, "none", RULE_SOLID, 4, 0.8)
        if i < len(schedule) - 1:
            body += h_arrow(x + sw + 4, sy + sw / 2, x + step - 6, ACCENT, accent=True)
        body += mono(x + sw / 2, sy + sw + 18, f"{abar:.2f}", 8, SOFT)
    body += mono(sx - 16, sy + sw + 18, "ᾱ", 8, SOFT, "end")
    body += subtext(sx + sw / 2, sy + sw + 38, "x", "T", 11, INK, MONO, 600)
    body += subtext(sx + 8 * step + sw / 2, sy + sw + 38, "x", "0", 11, INK, MONO, 600)

    body += verdict(70, vh - 52, 1040,
                    "At ᾱ = 0.02 the multiplier is 7.00, so a 0.20 error in the predicted noise lands as 1.40 in x̂₀ — wider than the whole pixel range.")

    emit(5, "one-jump-versus-eight-steps", "One jump versus eight steps",
         "The same starting noise resolved in one call and in eight, with the error multiplier "
         "that separates them",
         body,
         "Top lane: one arrow from pure noise to a blurred patch, beside a table of error "
         "multipliers. Bottom lane: the same noise through eight small steps to a sharp crescent",
         vw, vh)


# -------------------------------------------------------------------- fig 05

def fig05():
    """The schedule: two curves, the worked example marked on them."""
    vw, vh = 1060, 560
    T = 1000
    STEPS = 200

    def abar_linear_table():
        out, acc = [], 1.0
        betas = [1e-4 + (0.02 - 1e-4) * i / (T - 1) for i in range(T)]
        marks = [round(u * T / STEPS) for u in range(STEPS + 1)]
        idx, nxt = 0, marks[0]
        for i in range(T + 1):
            while idx <= STEPS and marks[idx] == i:
                out.append(acc)
                idx += 1
            if i < T:
                acc *= (1.0 - betas[i])
        while len(out) <= STEPS:
            out.append(acc)
        return out

    def abar_cosine_table(s=0.008):
        f = lambda z: math.cos((z + s) / (1 + s) * math.pi / 2) ** 2
        f0 = f(0.0)
        return [max(0.0, min(1.0, f(i / STEPS) / f0)) for i in range(STEPS + 1)]

    lin = abar_linear_table()
    cos = abar_cosine_table()

    def at(tab, u):
        z = min(float(STEPS), max(0.0, u * STEPS))
        i = int(z)
        if i >= STEPS:
            return tab[STEPS]
        f = z - i
        return tab[i] * (1 - f) + tab[i + 1] * f

    def crossing(tab, level):
        """First t/T at which sqrt(abar) drops to `level`."""
        for i, v in enumerate(tab):
            if v ** 0.5 <= level:
                return i / STEPS
        return 1.0

    px, py, pw, ph = 108, 122, 690, 300
    body = eyebrow(60, 52, "the noise schedule is configuration, not a learned layer")
    body += plot_axes(px, py, pw, ph, "t / T   ·   fraction of the way to pure noise",
                      "signal coefficient  √ᾱₜ",
                      [(0, "0"), (0.25, "0.25"), (0.5, "0.5"), (0.75, "0.75"), (1, "1")])
    for frac, tag in ((0.25, "0.25"), (0.5, "0.50"), (0.75, "0.75"), (1.0, "1.00")):
        y = py + ph - frac * ph
        body += (f'<line x1="{px}" y1="{y}" x2="{px + pw}" y2="{y}" '
                 f'stroke="{RULE}" stroke-width="0.8"/>')
        body += mono(px - 12, y + 3, tag, 7, SOFT, "end")

    body += curve(px, py, pw, ph, lambda u: at(lin, u) ** 0.5, INK, 1.8)
    body += curve(px, py, pw, ph, lambda u: at(cos, u) ** 0.5, BLUE, 1.8, dash=True)

    # name each curve where the gap between them is widest, not at the shared end
    u_lab = 0.62
    ly = py + ph - at(lin, u_lab) ** 0.5 * ph
    cy = py + ph - at(cos, u_lab) ** 0.5 * ph
    body += rect(px + u_lab * pw - 26, ly + 6, 56, 16, PAPER, "none", 3)
    body += mono(px + u_lab * pw + 2, ly + 18, "linear", 8, INK)
    body += rect(px + u_lab * pw - 30, cy - 24, 62, 16, PAPER, "none", 3)
    body += mono(px + u_lab * pw + 1, cy - 12, "cosine", 8, BLUE)

    # half-signal crossings: the claim "linear destroys faster", as a number
    half = 0.5
    ul, uc = crossing(lin, half), crossing(cos, half)
    hy = py + ph - half * ph
    for u, colour in ((ul, INK), (uc, BLUE)):
        x = px + u * pw
        body += (f'<line x1="{x:.1f}" y1="{hy:.1f}" x2="{x:.1f}" y2="{py + ph}" '
                 f'stroke="{colour}" stroke-width="0.9" stroke-dasharray="3,3" '
                 f'opacity="0.55"/>')
        body += (f'<circle cx="{x:.1f}" cy="{hy:.1f}" r="3.2" fill="{colour}"/>')

    # the worked example, annotated into the empty lower-left region
    target = SQ
    u_hit = crossing(lin, target)
    hx, hy2 = px + u_hit * pw, py + ph - target * ph
    body += (f'<circle cx="{hx:.1f}" cy="{hy2:.1f}" r="5" fill="{ACCENT}"/>')
    bx, by = px + 22, py + ph - 0.46 * ph
    body += (f'<path d="M{bx + 176},{by + 12} L{hx - 8:.1f},{hy2 + 6:.1f}" '
             f'fill="none" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="4,3"/>')
    body += rect(bx, by, 176, 46, "#ffffff", ACCENT, 4, 1)
    body += text(bx + 88, by + 19, "our worked example", 9, ACCENT, MONO, 600)
    body += text(bx + 88, by + 35,
                 f"√ᾱ = 0.80  at  t/T ≈ {u_hit:.2f}", 10, INK, MONO, 500)

    # the readout panel: computed from the two schedule definitions, not quoted
    q = 0.75
    lq, cq = at(lin, q) ** 0.5, at(cos, q) ** 0.5
    rx = px + pw + 44
    body += rect(rx, py + 4, 186, 168, "#ffffff", RULE_SOLID, 5, 1)
    body += mono(rx + 16, py + 28, "HALF THE SIGNAL GONE", 8, SOFT, "start")
    body += text(rx + 16, py + 52, "linear", 10, INK, MONO, 500, "start")
    body += text(rx + 170, py + 52, f"t/T = {ul:.2f}", 11, INK, MONO, 600, "end")
    body += text(rx + 16, py + 72, "cosine", 10, BLUE, MONO, 500, "start")
    body += text(rx + 170, py + 72, f"t/T = {uc:.2f}", 11, BLUE, MONO, 600, "end")
    body += (f'<line x1="{rx + 16}" y1="{py + 88}" x2="{rx + 170}" y2="{py + 88}" '
             f'stroke="{RULE}" stroke-width="0.8"/>')
    body += mono(rx + 16, py + 110, "SIGNAL LEFT AT t/T = 0.75", 8, SOFT, "start")
    body += text(rx + 16, py + 134, "linear", 10, INK, MONO, 500, "start")
    body += text(rx + 170, py + 134, f"\u221a\u03b1\u0304 = {lq:.3f}", 11, ACCENT, MONO, 600, "end")
    body += text(rx + 16, py + 154, "cosine", 10, BLUE, MONO, 500, "start")
    body += text(rx + 170, py + 154, f"\u221a\u03b1\u0304 = {cq:.3f}", 11, BLUE, MONO, 600, "end")

    body += verdict(60, vh - 92, 940,
                    "Same network, same data: move this curve and you move which noise levels the network ever practises on.")
    body += mono(60, vh - 40,
                 "linear: βₜ rising from 1e-4 to 0.02 over T = 1000 (Ho et al. 2020)   ·   "
                 "cosine: ᾱₜ = cos²(((t/T)+s)/(1+s) · π/2) / cos²((s/(1+s)) · π/2), s = 0.008 (Nichol & Dhariwal 2021)",
                 8, SOFT, "start")

    emit(3, "noise-schedule", "The schedule decides what the network practises",
         "Signal coefficient against normalised timestep for the linear and cosine schedules",
         body,
         "Two curves of the signal coefficient against normalised timestep: the linear schedule "
         "loses half its signal far earlier than the cosine one and flattens near zero for the "
         "last third, with the worked example's value of 0.80 marked",
         vw, vh)


# -------------------------------------------------------------------- cover

def cover():
    """Same shell as the rest of the series: eyebrow, serif title, motif band, kicker."""
    N = 12
    target = motif(N)
    noise = gaussian(N, 5)
    cell, gap = 9, 1
    w = gw(N, cell, gap)                     # 119
    levels = [0.012, 0.06, 0.18, 0.40, 0.70, 0.97]
    step = w + 40

    body = eyebrow(72, 73, "diffusion \u00b7 part one")
    body += text(72, 148, "Trained only to undo noise", 46, INK, SERIF, 400, "start")
    body += text(72, 193, "corrupt \u00b7 predict \u00b7 repeat", 15, MUTED, MONO, 400, "start")

    y = 268
    for i, abar in enumerate(levels):
        x = 72 + i * step
        body += vgrid(x, y, corrupt(target, noise, abar), cell, gap, stroke="none")
        if i == len(levels) - 1:
            body += rect(x - 5, y - 5, w + 10, w + 10, "none", ACCENT, 4, 1.6)
        if i < len(levels) - 1:
            body += h_arrow(x + w + 8, y + w / 2, x + step - 10,
                            ACCENT if i == len(levels) - 2 else MUTED,
                            accent=(i == len(levels) - 2))
    end_x = 72 + (len(levels) - 1) * step + w
    body += mono(72, y + w + 26, "PURE NOISE", 8, SOFT, "start")
    body += mono(end_x, y + w + 26, "DATA", 8, ACCENT, "end")

    body += (f'<line x1="72" y1="508" x2="1128" y2="508" '
             f'stroke="{RULE}" stroke-width="1"/>')
    body += text(72, 548, "So where does a new image come from?", 20, MUTED,
                 SERIF, 400, "start", italic=True)

    emit_cover(body,
               "A twelve-by-twelve patch of pure noise resolving through six stages into a "
               "bright crescent, under the line \u2018Trained only to undo noise\u2019")


# keyed by the figure number that reaches the post, not by definition order
FIGURES = {1: fig01, 2: fig02, 3: fig05, 4: fig03, 5: fig04}

if __name__ == "__main__":
    args = sys.argv[1:]
    wanted = [int(a) for a in args if a.isdigit()]
    if wanted:
        for k in wanted:
            FIGURES[k]()
    if "cover" in args:
        cover()
    if not args:
        for fn in FIGURES.values():
            fn()
        cover()
