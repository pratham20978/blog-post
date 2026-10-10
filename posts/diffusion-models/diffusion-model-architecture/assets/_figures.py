#!/usr/bin/env python3
"""Generate the fifteen article figures plus the deterministic cover."""

from _build import (
    SANS,
    ACCENT, ACCENT_TINT, BLUE, INK, LINK, MONO, MUSTARD, MUTED, PAPER, PAPER2,
    RULE, RULE_SOLID, SAGE, SOFT, elbow, emit, emit_cover, eyebrow, h_arrow,
    curve, grid, label, lcg, legend, mono, node, noise_grid, plot_axes, rect,
    subtext, text, token_row, v_arrow, wiggle, zconn,
)


import math


def disc(n=8, r=3.0):
    """An n-by-n motif the eye can lock onto once the noise clears."""
    c = (n - 1) / 2
    return [0.92 if (i // n - c) ** 2 + (i % n - c) ** 2 <= r * r else 0.06
            for i in range(n * n)]


def cover():
    """Noise resolving into structure, mixed with the article's own coefficients."""
    s = eyebrow(72, 76, "DIFFUSION · ARCHITECTURE MAP")
    s += text(72, 152, "From noise to structure", 46, INK, anchor="start")
    s += text(72, 198, "path · field · solver", 16, MUTED, MONO, anchor="start")
    target = [
        0.94, 0.94, 0.94, 0.94, 0.94,
        0.05, 0.94, 0.94, 0.94, 0.05,
        0.05, 0.94, 0.94, 0.94, 0.05,
        0.05, 0.05, 0.94, 0.05, 0.05,
        0.05, 0.05, 0.94, 0.05, 0.05,
    ]
    top, cell, gap, step, left = 286, 18, 4, 168, 96
    span = 5 * cell + 4 * gap
    for i, abar in enumerate([0.0, 0.08, 0.28, 0.55, 0.80, 1.0]):
        x = left + i * step
        s += noise_grid(x, top, 5, 5, cell, abar, target, seed=20260920 + i * 101,
                        gap=gap, accent=(2, 2) if i == 3 else None)
        if i < 5:
            s += h_arrow(x + span + 14, top + span / 2, x + step - 14,
                         ACCENT if i == 2 else MUTED, accent=i == 2)
    s += mono(96, top + span + 34, "PURE NOISE", 8, SOFT, "start")
    s += mono(1002, top + span + 34, "DATA", 8, SOFT, "end")
    s += f'<line x1="72" y1="508" x2="1128" y2="508" stroke="{RULE}" stroke-width="1"/>'
    s += text(72, 552, "A complete system, not a single denoiser", 17, MUTED,
              anchor="start", italic=True)
    emit_cover(s, "Tile fields of pure noise resolve left to right into a structured motif "
                  "as the signal coefficient rises, past one highlighted denoising step")


def fig01():
    """The states are drawn at their actual noise levels, not labelled with them."""
    s = eyebrow(32, 44, "ONE CHAIN · TWO DIRECTIONS")
    xs = [40, 228, 416, 604, 792]
    names = [("x", "0"), ("x", "1"), ("x", "t"), ("x", "t+1"), ("x", "T")]
    caps = ["data", "low noise", "mixed", "high noise", "prior"]
    signals = [1.0, 0.72, 0.36, 0.10, 0.0]
    motif = disc(8, 3.0)
    w, cell, gap = 128, 13, 2
    span = 8 * cell + 7 * gap                       # 118
    top = 224

    for i in range(4):
        gap_l, gap_r = xs[i] + w, xs[i + 1]
        s += h_arrow(gap_l + 2, top - 18, gap_r - 2, MUTED)
        s += label((gap_l + gap_r) / 2, top - 18, "+ noise", width=gap_r - gap_l - 8, dy=-22)
    s += mono(920, 150, "q(xₜ | xₜ₋₁)  ·  FIXED, NO PARAMETERS", 8, MUTED, "end")

    for i in range(4, 0, -1):
        gap_l, gap_r = xs[i - 1] + w, xs[i]
        acc = i == 3
        s += h_arrow(gap_r - 2, top + span + 76, gap_l + 2, ACCENT if acc else MUTED, accent=acc)
        s += label((gap_l + gap_r) / 2, top + span + 76, "denoise", ACCENT if acc else SOFT,
                   width=gap_r - gap_l - 8, dy=8)
    s += mono(480, top + span + 126, "pθ(xₜ₋₁ | xₜ)  ·  LEARNED AT EVERY NOISE LEVEL", 8, ACCENT)

    for x, (base, sub), cap, sig in zip(xs, names, caps, signals):
        gx = x + (w - span) / 2
        focal = sub == "t"
        s += noise_grid(gx, top, 8, 8, cell, sig, motif, seed=4242, gap=gap,
                        stroke=ACCENT if focal else None)
        s += subtext(x + w / 2, top + span + 28, base, sub, 14,
                     ACCENT if focal else INK)
        s += mono(x + w / 2, top + span + 48, cap, 8, SOFT)

    s += f'<path d="M104,{top - 8} V128 H472 Q480,128 480,136 V{top - 8}" fill="none" '
    s += f'stroke="{LINK}" stroke-width="1.1" stroke-dasharray="5,4" marker-end="url(#arrow-l)"/>'
    s += label(288, 128, "training jumps straight here", LINK, width=196, dy=-16)
    s += mono(288, 96, "xₜ = √ᾱₜ x₀ + √(1−ᾱₜ) ε", 9, LINK)

    s += legend(496, 960, [("fixed corruption", MUTED), ("learned direction", ACCENT),
                           ("closed-form shortcut", LINK)])
    emit(1, "forward-reverse", "Forward is fixed; reverse is learned",
         "The model estimates how to move back at every noise level.", s,
         "One chain of noisy states with fixed forward noising above it, learned reverse "
         "denoising below it, and a closed-form shortcut from clean data to any level",
         960, 540)


def matrix(x, y, vals, title, accent_cell=None):
    out = mono(x + 96, y - 16, title, 8, SOFT)
    for r in range(2):
        for c in range(2):
            focal = accent_cell == (r, c)
            out += rect(x + c * 96, y + r * 72, 96, 72,
                        ACCENT_TINT if focal else "#ffffff",
                        ACCENT if focal else RULE_SOLID, 4, 0.8)
            out += mono(x + c * 96 + 48, y + r * 72 + 42, vals[r][c], 12,
                        ACCENT if focal else INK, weight=600)
    return out


def fig02():
    """The article's numbers, already scaled, so the three matrices actually add up."""
    s = eyebrow(48, 56, "WORKED FORWARD PASS")
    s += text(48, 98, "Known scalars mix signal and Gaussian noise", 20, INK, anchor="start")
    s += mono(48, 126, "ᾱₜ = 0.64   ·   √ᾱₜ = 0.8   ·   √(1−ᾱₜ) = 0.6", 9, MUTED, "start")

    # Every cell is post-scaling, so 0.80 + 0.12 = 0.92 reads straight off the figure.
    s += matrix(48, 190, [["0.80", "−0.80"], ["0.40", "0.00"]], "0.8 × x₀  signal kept", (1, 1))
    s += text(288, 268, "+", 26, MUTED)
    s += matrix(336, 190, [["0.12", "0.60"], ["−0.24", "0.36"]], "0.6 × ε  noise added", (1, 1))
    s += text(576, 268, "=", 26, MUTED)
    s += matrix(624, 190, [["0.92", "−0.20"], ["0.16", "0.36"]], "xₜ  what the model sees", (1, 1))

    # The same three tensors as intensity, so the sum is visible and not just stated.
    def heat(x, y, vals, accent_cell=None):
        out = ""
        for r in range(2):
            for c in range(2):
                v = vals[r][c]
                hot = accent_cell == (r, c)
                mag = min(1.0, abs(v) / 1.0)
                fill = ACCENT if hot else INK
                out += (f'<rect x="{x + c * 40}" y="{y + r * 40}" width="36" height="36" '
                        f'rx="3" fill="{fill}" fill-opacity="{0.9 if hot else max(0.06, mag * 0.85):.2f}"/>')
                if v < 0 and not hot:
                    out += (f'<rect x="{x + c * 40 + 12}" y="{y + r * 40 + 16.5}" width="12" '
                            f'height="3" rx="1.5" fill="#ffffff" fill-opacity="0.85"/>')
        return out

    s += heat(96, 354, [[0.80, -0.80], [0.40, 0.00]], (1, 1))
    s += heat(384, 354, [[0.12, 0.60], [-0.24, 0.36]], (1, 1))
    s += heat(672, 354, [[0.92, -0.20], [0.16, 0.36]], (1, 1))
    s += mono(56, 376, "as", 8, SOFT, "end")
    s += mono(56, 394, "intensity", 8, SOFT, "end")
    s += mono(288, 396, "+", 14, MUTED)
    s += mono(576, 396, "=", 14, MUTED)
    s += mono(912, 376, "0.00 + 0.36 = 0.36", 8, ACCENT, "end")
    s += mono(912, 394, "a clean zero is now pure noise", 8, SOFT, "end")
    s += mono(96, 452, "white bar = negative value", 8, SOFT, "start")

    s += rect(48, 486, 440, 62, ACCENT_TINT, ACCENT, 6, 1)
    s += text(68, 512, "Training target", 12, ACCENT, weight=600, anchor="start")
    s += mono(68, 534, "the exact ε drawn above — no human label", 8, MUTED, "start")
    s += rect(512, 486, 400, 62, "rgba(45,49,66,0.04)", RULE_SOLID, 6, 1)
    s += text(532, 512, "Loss on this pair", 12, INK, weight=600, anchor="start")
    s += mono(532, 534, "¼‖ε − ε̂‖²  =  0.025  for ε̂ = [0.1, 0.8; −0.2, 0.7]", 8, MUTED, "start")
    emit(2, "numeric-corruption", "One noisy sample, computed by hand",
         "Scaled signal plus scaled noise gives the tensor the network is asked to explain.", s,
         "Three two-by-two matrices: clean data scaled by 0.8 plus Gaussian noise scaled by 0.6 "
         "equals the noisy tensor, with the bottom-right cell traced from 0.00 to 0.36",
         960, 584)


def fig03():
    """Five design axes, each tagged with whether it survives a checkpoint swap."""
    layers = [
        ("A5", "Numerical solver", "DDPM · DDIM · ODE · SDE", "swap freely", MUTED),
        ("A4", "Conditioning", "class · text tokens · maps", "retrain to change", BLUE),
        ("A3", "Learned field", "U-Net · U-ViT · DiT · MM-DiT", "is the checkpoint", ACCENT),
        ("A2", "Probability path", "VP · VE · flow · rectified flow", "retrain to change", BLUE),
        ("A1", "Representation", "pixel · latent · discrete state", "retrain to change", BLUE),
    ]
    def glyph(kind, x, y, tone):
        """A 34x22 pictogram of the axis, so the row is not four words alone."""
        g = ""
        if kind == "solver":                       # discrete steps
            pts, sx, sy = [], x, y + 18
            for i in range(5):
                pts += [f"{sx + i * 7},{sy - i * 4}", f"{sx + (i + 1) * 7},{sy - i * 4}"]
            g += f'<polyline points="{" ".join(pts)}" fill="none" stroke="{tone}" stroke-width="1.4"/>'
        elif kind == "cond":                       # a token strip
            for i in range(5):
                g += rect(x + i * 7, y + 6, 5, 10, "none", tone, 1, 1)
        elif kind == "field":                      # direction arrows
            for i, dy in enumerate((2, 9, 16)):
                g += (f'<line x1="{x}" y1="{y + dy}" x2="{x + 26}" y2="{y + dy - 4}" '
                      f'stroke="{tone}" stroke-width="1.3" marker-end="url(#arrow{"-a" if tone == ACCENT else ""})"/>')
        elif kind == "path":                       # a falling schedule curve
            g += (f'<path d="M{x},{y + 2} C{x + 12},{y + 3} {x + 16},{y + 18} {x + 30},{y + 19}" '
                  f'fill="none" stroke="{tone}" stroke-width="1.5"/>')
        else:                                      # representation: a grid
            for r in range(3):
                for c in range(4):
                    g += (f'<rect x="{x + c * 7}" y="{y + 2 + r * 6}" width="5" height="4" '
                          f'rx="1" fill="{tone}" fill-opacity="0.45"/>')
        return g

    kinds = ["solver", "cond", "field", "path", "repr"]
    s = eyebrow(72, 52, "SEPARATE THE DESIGN AXES")
    s += mono(872, 52, "CHANGE IT WITHOUT RETRAINING?", 8, SOFT, "end")
    y = 76
    for i, (code, name, sub, verdict, tone) in enumerate(layers):
        focal = tone == ACCENT
        fill = ACCENT_TINT if focal else ("#ffffff" if i % 2 else PAPER2)
        s += rect(96, y, 776, 64, fill, ACCENT if focal else RULE_SOLID, 0, 1)
        s += mono(118, y + 38, code, 8, ACCENT if focal else SOFT, "start", 600)
        s += glyph(kinds[i], 158, y + 21, ACCENT if focal else MUTED)
        s += text(212, y + 38, name, 15, ACCENT if focal else INK, weight=600, anchor="start")
        s += mono(494, y + 38, sub, 8, MUTED, "start")
        s += mono(852, y + 38, verdict, 8, tone, "end", 500)
        y += 64
    s += v_arrow(76, y - 8, 84, MUTED)
    s += mono(76, y + 16, "GENERATION ORDER", 8, SOFT)
    s += rect(96, y + 26, 776, 44, "rgba(45,49,66,0.04)", RULE_SOLID)
    s += mono(484, y + 53, "THE SAMPLE IS THE OUTPUT OF ALL FIVE — NOT A SIXTH AXIS", 8, MUTED)
    s += legend(506, 960, [("the trained checkpoint", ACCENT),
                           ("fixed at training time", BLUE),
                           ("swappable at inference", MUTED)])
    emit(3, "five-layer-system", "Five axes, only one of them swappable",
         "Changing one axis does not silently change the others.", s,
         "Five stacked design axes — representation, probability path, learned field, "
         "conditioning and solver — each marked with whether it can be changed without retraining",
         960, 554)


def fig04():
    """Each interface leaves the box that actually owns it."""
    s = eyebrow(32, 44, "CONDITIONAL LATENT GENERATOR")

    # Latent pipeline, left to right.
    s += h_arrow(164, 166, 228, LINK)
    s += h_arrow(392, 166, 462, LINK)
    s += h_arrow(638, 166, 716, LINK)
    s += node(32, 120, 132, 92, "Pixels", "B×3×512×512", "input", "DATA")
    s += node(228, 120, 164, 92, "Autoencoder", "encode once", "normal", "VAE")
    s += node(470, 112, 168, 108, "Denoiser", "B×4×64×64", "focal", "FIELD")
    s += node(716, 120, 164, 92, "Decoder", "pixels once", "normal", "VAE")

    # Everything that touches the denoiser, and the edge it enters on.
    s += node(32, 356, 124, 88, "Prompt", "token IDs", "input", "TEXT")
    s += node(212, 356, 156, 88, "Text encoder", "token embeddings", "link", "COND")
    s += node(444, 356, 150, 88, "Time embed", "t / σ / log-SNR", "soft", "TIME")
    s += node(672, 356, 156, 88, "Solver", "chooses σᵢ₊₁", "normal", "STEP")
    s += h_arrow(156, 400, 204, MUTED)

    riser = ('<path d="{d}" fill="none" stroke="{c}" stroke-width="1.2" '
             'marker-end="url(#{m})"/>')
    # Text tokens reach the denoiser through cross-attention, not through the clock.
    s += riser.format(d="M290,356 V308 Q290,300 298,300 H498 Q506,300 506,292 V224",
                      c=LINK, m="arrow-l")
    s += mono(498, 262, "CROSS-ATTENTION", 8, LINK, "end")
    # The noise level modulates every block.
    s += riser.format(d="M554,356 V224", c=MUTED, m="arrow")
    s += mono(546, 330, "MODULATION", 8, MUTED, "end")
    # The solver is the thing that calls the denoiser again and again.
    s += riser.format(d="M672,400 H622 Q614,400 614,392 V224", c=MUTED, m="arrow")
    s += mono(622, 262, "×N CALLS", 8, MUTED, "start")
    s += elbow(638, 190, 700, 348, MUTED)
    s += mono(708, 302, "PREDICTION", 8, MUTED, "start")

    s += legend(474, 960, [("learned denoiser", ACCENT), ("conditioning", LINK),
                           ("system component", MUTED)])
    emit(4, "complete-system", "A complete diffusion generation system",
         "Representation, conditioning, field and solver meet at explicit tensor interfaces.", s,
         "System map in which the text encoder feeds the denoiser by cross-attention, the time "
         "embedding modulates it, and the solver calls it repeatedly between one encode and one decode",
         960, 522)


def fig05():
    """Block height is spatial resolution, block width is channel count."""
    s = eyebrow(32, 44, "BLOCK SIZE IS THE TENSOR SHAPE")
    # (x, centre y, width=channels, height=resolution, label, shape, focal)
    stages = [
        (104, 168, 16, 100, "Input", "4×64×64", False),
        (188, 252, 48, 72, "Down 1", "128×32×32", False),
        (300, 322, 66, 52, "Down 2", "256×16×16", False),
        (430, 380, 88, 38, "Middle", "512×8×8", True),
        (588, 322, 66, 52, "Up 2", "256×16×16", False),
        (700, 252, 48, 72, "Up 1", "128×32×32", False),
        (792, 168, 16, 100, "Output", "4×64×64", False),
    ]
    for x, cy, w, h, name, shape, focal in stages:
        s += rect(x, cy - h / 2, w, h, ACCENT_TINT if focal else "#ffffff",
                  ACCENT if focal else INK, 3, 1.2)
        s += text(x + w / 2, cy - h / 2 - 12, name, 11, ACCENT if focal else INK,
                  SANS, 600)
        s += mono(x + w / 2, cy + h / 2 + 18, shape, 8, SOFT)

    def hop(a, b):
        return (f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="{MUTED}" '
                f'stroke-width="1.2" marker-end="url(#arrow)"/>')
    chain = [((120, 218), (196, 232)), ((236, 288), (296, 304)), ((366, 348), (424, 368)),
             ((518, 380), (582, 342)), ((654, 296), (696, 276)), ((748, 216), (788, 196))]
    for a, b in chain:
        s += hop(a, b)

    # Skips are horizontal because they only ever join matching resolutions.
    for y, x1, x2 in ((150, 120, 792), (234, 236, 700), (304, 366, 588)):
        s += (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{BLUE}" '
              f'stroke-width="1" stroke-dasharray="5,4" marker-end="url(#arrow-l)"/>')
    s += mono(456, 132, "EACH SKIP JOINS ONE RESOLUTION TO ITS MIRROR", 8, BLUE)

    s += rect(60, 404, 300, 62, "rgba(45,49,66,0.04)", RULE_SOLID)
    s += mono(76, 428, "height  =  spatial resolution", 8, MUTED, "start")
    s += mono(76, 450, "width   =  channel count", 8, MUTED, "start")
    s += mono(600, 428, "the pyramid trades one for the other", 8, SOFT, "start")
    s += mono(600, 450, "64² × 4ch  →  8² × 512ch", 8, ACCENT, "start")

    s += legend(496, 960, [("bottleneck", ACCENT), ("long skip", LINK), ("main path", MUTED)])
    emit(5, "unet-shapes", "Diffusion U-Net: shape is the architecture",
         "The pyramid trades spatial size for context, then restores detail through skips.", s,
         "A U-shaped tensor trace descends from 4 by 64 by 64 to 512 by 8 by 8 and climbs "
         "back, one dashed skip joining each resolution to its mirror")


def fig06():
    """Time modulation drawn as what it is: per-channel scale and shift on the rows."""
    s = eyebrow(32, 44, "TIME REACHES EVERY CHANNEL, NOT JUST THE FIRST LAYER")
    rng = lcg(808)
    chans, cols, cell, gap = 6, 10, 15, 2
    gw = cols * (cell + gap) - gap                 # 168
    top = 150
    base = [[next(rng) * 0.55 + 0.2 for _ in range(cols)] for _ in range(chans)]
    sc = [0.35, 1.35, 0.55, 1.55, 0.90, 1.15]      # one scale per channel
    sh = [0.05, -0.08, 0.14, -0.02, 0.10, -0.12]   # one shift per channel

    def fmap(x, rows, tag, tone=INK):
        out = mono(x + gw / 2, top - 14, tag, 8, tone)
        for r in range(chans):
            for c in range(cols):
                v = rows[r][c]
                out += (f'<rect x="{x + c * (cell + gap)}" y="{top + r * (cell + gap)}" '
                        f'width="{cell}" height="{cell}" rx="1" fill="{INK}" '
                        f'fill-opacity="{min(0.92, max(0.05, v)):.2f}"/>')
        return out

    s += fmap(92, base, "NORMALIZED  h")
    after = [[min(1.0, max(0.0, sc[r] * base[r][c] + sh[r])) for c in range(cols)]
             for r in range(chans)]
    s += fmap(560, after, "MODULATED  (1+s)·h + b", ACCENT)

    for r in range(chans):
        y = top + r * (cell + gap) + cell / 2
        s += mono(312, y + 3, f"s={sc[r]:.2f}", 7, SOFT, "end")
        s += rect(322, y - 5, sc[r] * 44, 10, ACCENT_TINT, ACCENT, 2, 0.9)
        s += mono(404, y + 3, f"b={sh[r]:+.2f}", 7, SOFT, "start")
    s += mono(360, top - 14, "PER CHANNEL", 8, ACCENT)
    s += h_arrow(492, top + 50, 546, ACCENT, accent=True)

    s += node(92, 292, 140, 76, "Noise level", "t / σ", "input", "SCALAR")
    s += node(280, 292, 152, 76, "Time MLP", "Fourier → 2C", "link", "EMBED")
    s += h_arrow(232, 330, 272, LINK)
    s += f'<path d="M356,292 V268 Q356,260 364,260 H364" fill="none" '
    s += f'stroke="{LINK}" stroke-width="1.2" marker-end="url(#arrow-l)"/>'
    s += mono(452, 330, "2C numbers in total — one s and one b for every channel", 8, LINK, "start")

    s += rect(480, 268, 448, 62, "rgba(45,49,66,0.04)", RULE_SOLID)
    s += mono(500, 292, "a low-noise step and a high-noise step run the SAME weights", 8, MUTED, "start")
    s += mono(500, 314, "and receive different s and b, so every block re-specialises", 8, ACCENT, "start")

    s += f'<path d="M92,140 V104 H644 V140" fill="none" stroke="{MUTED}" stroke-width="1" '
    s += f'stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
    s += mono(368, 92, "IDENTITY PATH · h IS ADDED BACK AFTER THE CONVOLUTION", 8, SOFT)

    s += legend(400, 960, [("time modulation", ACCENT), ("conditioning path", LINK),
                           ("identity path", MUTED)])
    emit(6, "time-residual-block", "Time changes computation throughout depth",
         "Every block can specialize to a different noise regime while retaining a stable residual path.", s,
         "Residual block in which a Fourier time embedding produces per-channel scale and shift "
         "applied to normalized features before the convolution",
         960, 444)


def score_matrix(x, y, rows, cols, cell, fn, gap=1.5, accent_row=None):
    """The actual QK-transpose grid. Its aspect ratio is the whole lesson."""
    out = ""
    for r in range(rows):
        for c in range(cols):
            v = fn(r, c)
            hot = accent_row == r
            out += (f'<rect x="{x + c * (cell + gap):.1f}" y="{y + r * (cell + gap):.1f}" '
                    f'width="{cell}" height="{cell}" rx="1" fill="{ACCENT if hot else INK}" '
                    f'fill-opacity="{min(0.95, max(0.05, v)):.2f}"/>')
    return out


def fig07():
    """Self- and cross-attention differ in one visible way: the shape of QKᵀ."""
    import math
    s = eyebrow(32, 44, "THE SCORE MATRIX IS THE DIFFERENCE")
    cell, gap = 14, 1.5
    rows = 12

    def panel(ox, title, cols, kv_label, kv_colour, shape, cost, note):
        out = eyebrow(ox - 34, 96, title)
        mw = cols * cell + (cols - 1) * gap
        mh = rows * cell + (rows - 1) * gap
        top = 168
        # Keys run across the top, queries down the left: the grid is their product.
        out += token_row(ox, top - 30, cols, cell, gap, stroke=kv_colour)
        for r in range(rows):
            out += rect(ox - 30, top + r * (cell + gap), cell, cell, "#ffffff", RULE_SOLID, 2, 0.9)
        out += mono(ox + mw / 2, top - 44, kv_label, 8, kv_colour)
        out += f'<g transform="rotate(-90 {ox - 52} {top + mh / 2})">' + \
               mono(ox - 52, top + mh / 2, "QUERIES · N IMAGE TOKENS", 8, MUTED) + '</g>'
        if cols == rows:
            fn = lambda r, c: 0.10 + 0.85 * math.exp(-((r - c) ** 2) / 6.0)
        else:
            fn = lambda r, c: 0.10 + 0.80 * math.exp(-((c - (r * 0.28) % cols) ** 2) / 1.4)
        out += score_matrix(ox, top, rows, cols, cell, fn, gap, accent_row=6)
        out += rect(ox - 3, top - 3, mw + 6, mh + 6, "none", RULE_SOLID, 3, 1)
        out += text(ox, top + mh + 34, shape, 15, INK, SANS, 600, "start")
        out += mono(ox, top + mh + 56, cost, 8, ACCENT if cols == rows else SOFT, "start")
        out += mono(ox, top + mh + 76, note, 8, MUTED, "start")
        return out

    s += panel(150, "SELF-ATTENTION", 12, "KEYS · THE SAME N IMAGE TOKENS", MUTED,
               "N × N", "4,096² pairs — grows quadratically", "every position reads every position")
    s += panel(620, "CROSS-ATTENTION", 4, "KEYS · L PROMPT TOKENS", LINK,
               "N × L", "4,096 × 77 pairs — linear in L", "every position reads the prompt")
    s += f'<line x1="500" y1="96" x2="500" y2="392" stroke="{RULE}" stroke-width="1"/>'
    s += mono(150, 462, "one highlighted row = what a single image position attends to", 8, SOFT, "start")
    s += legend(498, 960, [("one query's row", ACCENT), ("prompt keys", LINK),
                           ("image keys", MUTED)])
    emit(7, "self-vs-cross-attention", "The Q/K/V source defines the attention job",
         "The same equation either mixes image positions or injects a condition sequence.", s,
         "Self- and cross-attention take queries from the same noisy tokens but draw keys and "
         "values from the image or from text, giving an N by N or N by L matrix",
         960, 542)


def fig08():
    """Patchification drawn as patchification, with both patch sizes side by side."""
    s = eyebrow(32, 44, "PATCH SIZE SETS THE SEQUENCE LENGTH")
    rng = lcg(5150)
    vals = [next(rng) * 0.7 + 0.15 for _ in range(64)]

    def latent(x, y, cell, p):
        """An 8x8 latent with the patch lattice drawn over it."""
        out = grid(x, y, 8, 8, cell, vals, gap=1, rx=0.5)
        side = 8 * cell + 7
        for k in range(0, 9, p):
            off = k * (cell + 1)
            out += (f'<line x1="{x + off - 0.5}" y1="{y - 2}" x2="{x + off - 0.5}" y2="{y + side}" '
                    f'stroke="{ACCENT}" stroke-width="1.4" opacity="0.9"/>')
            out += (f'<line x1="{x - 2}" y1="{y + off - 0.5}" x2="{x + side}" y2="{y + off - 0.5}" '
                    f'stroke="{ACCENT}" stroke-width="1.4" opacity="0.9"/>')
        return out

    def strip(x, y, count, cell, gap, accent=None):
        out = ""
        for i in range(count):
            hot = accent == i
            out += rect(x + i * (cell + gap), y, cell, cell,
                        ACCENT_TINT if hot else "#ffffff",
                        ACCENT if hot else RULE_SOLID, 1.5, 0.9)
        return out

    # P = 2 : sixteen patches become sixteen tokens.
    s += latent(72, 118, 15, 2)
    s += mono(136, 266, "8×8 latent · P = 2", 8, MUTED)
    s += h_arrow(214, 178, 262, ACCENT, accent=True)
    s += label(238, 178, "flatten", width=44, dy=-20)
    s += strip(276, 162, 16, 18, 4, accent=5)
    s += mono(276, 210, "16 tokens here · 1,024 at 64×64 with P=2", 8, INK, "start")
    s += node(700, 134, 176, 88, "DiT blocks", "attention + MLP", "focal", "×L")
    s += h_arrow(636, 178, 692, MUTED)

    s += f'<line x1="60" y1="292" x2="900" y2="292" stroke="{RULE}" stroke-width="1"/>'

    # P = 1 : the same latent, four times the sequence, sixteen times the pairs.
    s += latent(72, 318, 15, 1)
    s += mono(136, 466, "8×8 latent · P = 1", 8, ACCENT)
    s += h_arrow(214, 378, 262, ACCENT, accent=True)
    s += label(238, 378, "flatten", width=44, dy=-20)
    s += strip(276, 368, 64, 7, 2, accent=21)
    s += mono(276, 410, "64 tokens here · 4,096 at 64×64 with P=1", 8, ACCENT, "start")
    s += rect(700, 334, 176, 88, "rgba(45,49,66,0.04)", RULE_SOLID)
    s += mono(788, 364, "×4  SEQUENCE LENGTH", 8, ACCENT)
    s += mono(788, 386, "×16 ATTENTION PAIRS", 8, ACCENT)
    s += mono(788, 406, "same latent resolution", 8, SOFT)

    s += legend(486, 960, [("patch lattice", ACCENT), ("one token", MUTED)])
    emit(8, "dit-token-flow", "DiT turns the latent grid into a sequence",
         "Patch size sets both spatial granularity and token-count cost.", s,
         "A noisy latent is patchified into 1,024 tokens, processed by adaLN-conditioned DiT "
         "blocks and unpatchified; halving the patch size quadruples the tokens",
         960, 530)


def fig09():
    """The latent is drawn 8x smaller per side, because that is the entire argument."""
    s = eyebrow(32, 44, "ONE ENCODE · MANY DENOISE CALLS · ONE DECODE")
    big, small = 160, 20                     # 512/64 = 8, so 160/8 = 20
    rng = lcg(31337)
    pix = [next(rng) * 0.45 + 0.25 for _ in range(20 * 20)]

    s += grid(72, 150, 20, 20, big / 20 - 1, pix, gap=1, rx=0.5, stroke=SOFT)
    s += text(72 + big / 2, 138, "Pixels", 13, INK, SANS, 600)
    s += mono(72 + big / 2, 336, "3 × 512 × 512", 8, SOFT)
    s += mono(72 + big / 2, 354, "262,144 positions", 8, MUTED)

    lx, ly = 430, 220
    s += grid(lx, ly, 4, 4, small / 4 - 1, [next(rng) * 0.6 + 0.2 for _ in range(16)],
              gap=1, rx=0.5, stroke=ACCENT)
    s += text(lx - 22, ly + small / 2 + 4, "Latent zₜ", 13, ACCENT, SANS, 600, "end")
    s += mono(lx + small / 2, ly + small + 22, "4 × 64 × 64", 8, ACCENT)
    s += mono(lx + small / 2, ly + small + 40, "4,096 positions", 8, MUTED)
    s += mono(lx + small / 2, ly + small + 58, "8× per side · 64× fewer", 8, SOFT)

    s += h_arrow(248, 230, 410, MUTED)
    s += label(330, 230, "encode once", width=104, dy=-22)
    s += h_arrow(466, 230, 620, MUTED)
    s += label(544, 230, "decode once", width=104, dy=-22)

    s += grid(640, 150, 20, 20, big / 20 - 1, pix, gap=1, rx=0.5, stroke=SOFT)
    s += text(640 + big / 2, 138, "Image", 13, INK, SANS, 600)
    s += mono(640 + big / 2, 336, "3 × 512 × 512", 8, SOFT)

    # The loop lives on the small tensor. That is the compute argument, drawn.
    s += node(360, 76, 160, 64, "Denoiser + solver", "one reverse step", "focal", "×N")
    s += f'<path d="M436,214 V148" fill="none" stroke="{ACCENT}" stroke-width="1.4" marker-end="url(#arrow-a)"/>'
    s += f'<path d="M458,140 V212" fill="none" stroke="{ACCENT}" stroke-width="1.4" marker-end="url(#arrow-a)"/>'
    s += mono(540, 112, "EVERY ONE OF THE N CALLS RUNS HERE", 8, ACCENT, "start")

    s += rect(72, 372, 816, 62, "rgba(45,49,66,0.04)", RULE_SOLID)
    s += mono(92, 396, "Benefit  ·  the ×64 element saving repeats at every one of the N denoiser calls", 8, MUTED, "start")
    s += mono(92, 418, "Ceiling  ·  anything E drops out of those 262,144 positions is not in the 4,096, and D cannot invent it", 8, ACCENT, "start")
    s += legend(474, 960, [("iterative region", ACCENT), ("one-time transform", MUTED)])
    emit(9, "latent-diffusion", "Latent diffusion moves the loop behind compression",
         "The compute saving repeats at every denoiser call; reconstruction loss is inherited once at the boundary.", s,
         "Pixels are encoded once into a small latent, the denoiser and solver loop on that "
         "latent N times, and the decoder runs once to produce the image",
         960, 518)


def fig10():
    """Every target is drawn where its own algebra puts it."""
    s = eyebrow(32, 44, "ONE NOISY POINT · FOUR DESCRIPTIONS OF IT")
    cx, cy, r = 400, 268, 150
    a, sg = 0.8, 0.6                      # the worked example's coefficients
    xt = (cx + a * r, cy - sg * r)
    v = (cx - sg * r, cy - a * r)

    s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += f'<line x1="{cx - r - 44}" y1="{cy}" x2="{cx + r + 44}" y2="{cy}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += f'<line x1="{cx}" y1="{cy + r + 44}" x2="{cx}" y2="{cy - r - 44}" stroke="{RULE_SOLID}" stroke-width="1"/>'

    # Projections: the schedule coefficients are literally the shadows of x_t.
    s += f'<line x1="{xt[0]}" y1="{xt[1]}" x2="{xt[0]}" y2="{cy}" stroke="{SOFT}" stroke-width="1" stroke-dasharray="4,4"/>'
    s += f'<line x1="{xt[0]}" y1="{xt[1]}" x2="{cx}" y2="{xt[1]}" stroke="{SOFT}" stroke-width="1" stroke-dasharray="4,4"/>'
    s += mono(xt[0] + 10, cy - 22, "σₜ = 0.6", 8, SOFT, "start")
    s += mono(cx + 58, xt[1] - 10, "αₜ = 0.8", 8, SOFT, "start")

    s += f'<line x1="{cx}" y1="{cy}" x2="{xt[0]}" y2="{xt[1]}" stroke="{ACCENT}" stroke-width="2.2" marker-end="url(#arrow-a)"/>'
    s += f'<line x1="{cx}" y1="{cy}" x2="{v[0]}" y2="{v[1]}" stroke="{LINK}" stroke-width="1.8" marker-end="url(#arrow-l)"/>'
    s += subtext(xt[0] + 22, xt[1] - 6, "x", "t", 15, ACCENT)
    s += text(v[0] - 16, v[1] - 8, "v", 15, LINK, weight=600)
    s += mono(cx + 12, cy - r - 18, "ε  AXIS", 8, MUTED, "start")
    s += mono(cx + r + 34, cy - 14, "x₀  AXIS", 8, MUTED, "end")
    s += mono(cx + 12, cy + r + 30, "score  =  −ε / σₜ", 8, BLUE, "start")
    s += f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy + r}" stroke="{BLUE}" stroke-width="1.6" marker-end="url(#arrow-l)"/>'
    s += mono(60, cy - 10, "αₜ² + σₜ² = 1", 8, SOFT, "start")
    s += mono(60, cy + 10, "so v ⟂ xₜ", 8, SOFT, "start")

    s += rect(628, 132, 300, 276, "#ffffff", RULE_SOLID)
    s += mono(648, 162, "GIVEN ONE PREDICTION ε̂", 8, SOFT, "start", 500)
    rows = [
        ("ε̂", "the noise that was added", INK),
        ("x̂₀", "(xₜ − σₜ·ε̂) / αₜ", INK),
        ("ŝ", "− ε̂ / σₜ", BLUE),
        ("v̂", "αₜ ε̂ − σₜ x̂₀", ACCENT),
    ]
    y = 200
    for name, expr, tone in rows:
        s += text(652, y, name, 13, tone, weight=600, anchor="start")
        s += mono(700, y, expr, 9, MUTED, "start")
        y += 42
    s += f'<line x1="648" y1="358" x2="908" y2="358" stroke="{RULE}" stroke-width="1"/>'
    s += mono(648, 384, "same point · four regression problems", 8, SOFT, "start")

    s += legend(474, 960, [("noisy state", ACCENT), ("velocity / score", LINK),
                           ("schedule coefficient", MUTED)])
    emit(10, "prediction-geometry", "Prediction targets are coordinate choices",
         "Schedule coefficients convert noise, clean data, score and velocity descriptions.", s,
         "In the clean-data and noise plane, x-t sits at coefficients 0.8 and 0.6, velocity sits "
         "perpendicular to it, score points along negative noise, and a table converts one predicted epsilon into all four",
         960, 518)


def fig11():
    """The schedule is a curve, so plot it. Both panels are definitions, not measurements."""
    T = 1000
    beta = [1e-4 + (0.02 - 1e-4) * i / (T - 1) for i in range(T)]
    lin, acc = [], 1.0
    for b in beta:
        acc *= (1 - b); lin.append(acc)
    off = 0.008
    f0 = math.cos((off / (1 + off)) * math.pi / 2) ** 2
    cos = [max(1e-8, (math.cos(((i / T + off) / (1 + off)) * math.pi / 2) ** 2) / f0)
           for i in range(T)]

    def at(series, u):
        return series[min(T - 1, max(0, int(u * (T - 1))))]

    s = eyebrow(32, 44, "TWO SCHEDULES · THE SAME AXES")
    px, py, pw, ph = 108, 108, 330, 268

    # Panel 1: how much signal survives.
    s += plot_axes(px, py, pw, ph, "t / T", "ᾱₜ  (signal kept)",
                   ((0, "0"), (0.5, "0.5"), (1, "1")))
    s += curve(px, py, pw, ph, lambda u: at(lin, u), MUTED, 1.8)
    s += curve(px, py, pw, ph, lambda u: at(cos, u), ACCENT, 1.8)
    s += mono(px + pw - 6, py + ph - 52, "linear", 8, MUTED, "end")
    s += mono(px + pw - 6, py + ph - 34, "cosine", 8, ACCENT, "end")
    s += mono(px + pw / 2, py - 24, "SIGNAL COEFFICIENT", 8, SOFT)

    # Panel 2: the same thing as SNR, where the endpoint problem becomes visible.
    qx = 560
    s += plot_axes(qx, py, pw, ph, "t / T", "log₁₀ SNR(t)",
                   ((0, "0"), (0.5, "0.5"), (1, "1")))
    def lsnr(series, u):
        a = at(series, u)
        v = math.log10(max(1e-12, a / max(1e-12, 1 - a)))
        return min(1.0, max(0.0, (v + 6) / 12))          # -6..+6 decades
    s += curve(qx, py, pw, ph, lambda u: lsnr(lin, u), MUTED, 1.8)
    s += curve(qx, py, pw, ph, lambda u: lsnr(cos, u), ACCENT, 1.8)
    s += f'<line x1="{qx}" y1="{py + ph / 2}" x2="{qx + pw}" y2="{py + ph / 2}" stroke="{RULE}" stroke-width="1" stroke-dasharray="4,4"/>'
    s += mono(qx + pw - 4, py + ph / 2 - 8, "SNR = 1", 7, SOFT, "end")
    s += mono(qx + pw / 2, py - 24, "SIGNAL-TO-NOISE RATIO", 8, SOFT)

    # The endpoint the article's L29 claim is about, computed rather than asserted.
    end_lin = lin[-1] / (1 - lin[-1])
    ey = py + ph - lsnr(lin, 1.0) * ph
    s += f'<circle cx="{qx + pw}" cy="{ey:.1f}" r="4" fill="{ACCENT}"/>'
    s += mono(qx + pw - 10, ey - 16, f"linear ends at SNR ≈ {end_lin:.1e} — small, but not zero", 8, ACCENT, "end")

    s += rect(108, 414, 782, 62, ACCENT_TINT, ACCENT, 6, 1)
    s += mono(128, 438, "The linear schedule never reaches pure noise, so the last training input still", 8, MUTED, "start")
    s += mono(128, 458, "carries signal while inference starts from x_T ~ N(0, I). That gap is the mismatch.", 8, ACCENT, "start")
    s += legend(510, 960, [("cosine schedule", ACCENT), ("linear schedule", MUTED)])
    emit(11, "noise-schedule", "The schedule decides which noise levels exist",
         "Both curves are definitions computed from the schedule, not measured results.", s,
         "Two panels plot the signal coefficient and the log signal-to-noise ratio against "
         "normalised timestep for the linear and cosine schedules, marking the linear "
         "schedule's nonzero terminal SNR",
         960, 550)


def fig12():
    """One batch, six different noise levels — the thing the caption claims, drawn."""
    s = eyebrow(32, 44, "ONE BATCH · A DIFFERENT NOISE LEVEL PER EXAMPLE")
    motif = disc(6, 2.2)
    levels = [("t=14", 0.90), ("t=173", 0.62), ("t=402", 0.38),
              ("t=611", 0.20), ("t=840", 0.08), ("t=977", 0.01)]
    cell, gap = 10, 1.5
    side = 6 * cell + 5 * gap                       # 67.5
    cols, pitch_x, pitch_y = 2, 104, 86
    x0, y0 = 104, 112
    for i, (tag, sig) in enumerate(levels):
        gx = x0 + (i % cols) * pitch_x
        gy = y0 + (i // cols) * pitch_y
        s += noise_grid(gx, gy, 6, 6, cell, sig, motif, seed=606 + i * 31, gap=gap,
                        stroke=ACCENT if i == 2 else None)
        s += mono(gx + side / 2, gy + side + 15, tag, 8, ACCENT if i == 2 else SOFT)
    s += rect(84, 94, 212, 292, "none", RULE_SOLID, 6, 1)
    s += mono(190, 408, "ONE BATCH · SAME STEP", 8, MUTED)
    s += h_arrow(300, 230, 352, MUTED)

    s += node(360, 178, 168, 104, "εθ(xₜ, t, c)", "one shared network", "focal", "PREDICT")
    s += h_arrow(528, 230, 578, ACCENT, accent=True)
    s += node(586, 178, 160, 104, "Weighted MSE", "w(t)·‖ε − ε̂‖²", "normal", "LOSS")
    s += h_arrow(746, 230, 796, MUTED)
    s += node(804, 178, 132, 104, "Update θ", "then EMA", "normal", "STEP")
    s += f'<path d="M870,282 V432 Q870,440 862,440 H198 Q190,440 190,432 V398" fill="none" '
    s += f'stroke="{MUTED}" stroke-width="1" stroke-dasharray="5,4" marker-end="url(#arrow)"/>'
    s += label(530, 440, "next batch — a fresh t for every example again", SOFT, width=300, dy=-14)
    s += mono(360, 478, "training never walks a trajectory; it only ever sees isolated noise levels", 8, SOFT, "start")
    s += legend(512, 960, [("neural prediction", ACCENT), ("training loop", MUTED)])
    emit(12, "training-loop", "Diffusion training is direct noisy regression",
         "The chain is sampled analytically; the optimizer loop is not the reverse sampling loop.", s,
         "Training flows from a data batch through a randomly drawn timestep and noise, a "
         "closed-form noisy input, a prediction and a weighted loss, then loops again",
         960, 556)


def fig13():
    """Two lanes of real trajectories: same endpoints, visibly different paths."""
    s = eyebrow(32, 44, "SAME MARGINALS · DIFFERENT TRAJECTORIES")
    x1, x2 = 232, 726
    rng = lcg(90210)
    spread = [-66, -40, -14, 14, 40, 66]
    # Both lanes land on the same contracted spread: same marginals, different paths.
    land = [round(v * 0.58) for v in spread]

    def endpoints(cy, colour):
        out = ""
        for dy in spread:
            out += f'<circle cx="{x1 - 14}" cy="{cy + dy}" r="3.2" fill="{colour}" fill-opacity="0.55"/>'
        for dy in land:
            out += f'<circle cx="{x2 + 14}" cy="{cy + dy}" r="3.2" fill="{colour}" fill-opacity="0.55"/>'
        return out

    # Lane 1: the reverse SDE keeps its Brownian term, so every path jitters.
    cy = 158
    s += endpoints(cy, MUTED)
    for i, dy in enumerate(spread):
        s += wiggle(x1, cy + dy, x2, cy + land[(i * 5 + 2) % 6], 16, 1000 + i * 77,
                    ACCENT if i == 2 else MUTED, 1.4 if i == 2 else 1.0)
    s += mono(32, cy - 92, "REVERSE SDE", 8, ACCENT, "start", 500)
    s += mono(200, cy - 92, "dx = [f − g²sθ] dt + g dW̄", 9, INK, "start")
    s += mono(920, cy - 92, "stochastic · a new path every run", 8, SOFT, "end")

    # Lane 2: the probability-flow ODE drops it, so paths are smooth and never cross.
    cy = 344
    s += endpoints(cy, BLUE)
    for i, dy in enumerate(spread):
        end = cy + land[i]
        s += (f'<path d="M{x1},{cy + dy} C{x1 + 200},{cy + dy} {x2 - 200},{end} {x2},{end}" '
              f'fill="none" stroke="{LINK if i == 2 else BLUE}" '
              f'stroke-width="{1.4 if i == 2 else 1.0}" opacity="0.85"/>')
    s += mono(32, cy - 92, "PROBABILITY-FLOW ODE", 8, LINK, "start", 500)
    s += mono(200, cy - 92, "dx = [f − ½ g² sθ] dt", 9, INK, "start")
    s += mono(920, cy - 92, "deterministic · one path per start", 8, SOFT, "end")

    s += mono(x1 - 14, 448, "PRIOR", 8, SOFT)
    s += mono(x2 + 14, 448, "DATA", 8, SOFT)
    s += f'<line x1="{x1 - 14}" y1="72" x2="{x1 - 14}" y2="430" stroke="{RULE}" stroke-width="1" stroke-dasharray="3,5"/>'
    s += f'<line x1="{x2 + 14}" y1="72" x2="{x2 + 14}" y2="430" stroke="{RULE}" stroke-width="1" stroke-dasharray="3,5"/>'
    s += mono(480, 470, "ONE LEARNED SCORE FEEDS BOTH · THE HALF APPEARS ONLY WHEN THE NOISE TERM LEAVES", 8, MUTED)
    s += legend(516, 960, [("one highlighted path", ACCENT), ("deterministic route", LINK),
                           ("stochastic route", MUTED)])
    emit(13, "sde-ode", "The score can drive an SDE or an ODE",
         "Continuous-time unification separates the learned field from stochasticity in the sampler.", s,
         "One learned score feeds either a reverse SDE that keeps the Brownian term or a "
         "probability-flow ODE whose drift carries a factor of one half and no noise",
         960, 560)


def fig14():
    s = eyebrow(32, 44, "SAMPLER SELECTION")
    s += node(360, 72, 240, 76, "Can the checkpoint change?", "training budget", "focal", "DECIDE")

    def fork(x0, y0, x1, y1, colour, marker):
        return (f'<path d="M{x0},{y0} V{y0 + 24} Q{x0},{y0 + 32} {x0 + (8 if x1 > x0 else -8)},{y0 + 32} '
                f'H{x1 - (8 if x1 > x0 else -8)} Q{x1},{y0 + 32} {x1},{y0 + 40} V{y1}" fill="none" '
                f'stroke="{colour}" stroke-width="1.2" marker-end="url(#{marker})"/>')

    # Branches leave the bottom edge, so nothing is drawn across the question.
    s += fork(440, 148, 220, 212, MUTED, "arrow")
    s += fork(520, 148, 740, 212, LINK, "arrow-l")
    s += mono(300, 174, "NO", 8, MUTED)
    s += mono(660, 174, "YES", 8, LINK)

    s += node(120, 220, 200, 76, "No retraining", "off-the-shelf weights", "normal", "NO")
    s += node(640, 220, 200, 76, "Retraining allowed", "new objective", "link", "YES")

    s += fork(180, 296, 116, 356, MUTED, "arrow")
    s += fork(260, 296, 316, 356, MUTED, "arrow")
    s += fork(700, 296, 644, 356, LINK, "arrow-l")
    s += fork(780, 296, 844, 356, LINK, "arrow-l")

    s += node(32, 364, 168, 76, "Ancestral", "stochastic", "normal", "DDPM")
    s += node(232, 364, 168, 76, "DDIM / ODE", "deterministic", "normal", "SOLVER")
    s += node(560, 364, 168, 76, "Distillation", "few-step student", "normal", "TRAIN")
    s += node(760, 364, 168, 76, "Consistency", "endpoint map", "link", "TRAIN")

    # Each leaf carries a picture of the trajectory it actually produces.
    s += wiggle(52, 464, 180, 464, 9, 4242, MUTED, 1.2, 22)
    s += f'<path d="M252,464 C300,464 332,464 380,464" fill="none" stroke="{MUTED}" stroke-width="1.4"/>'
    pts = " ".join(f"{580 + i * 36},{464 - (i % 2) * 7}" for i in range(5))
    s += f'<polyline points="{pts}" fill="none" stroke="{MUTED}" stroke-width="1.4" stroke-linejoin="round"/>'
    for i in range(5):
        s += f'<circle cx="{580 + i * 36}" cy="{464 - (i % 2) * 7}" r="2.6" fill="{MUTED}"/>'
    s += f'<line x1="780" y1="464" x2="900" y2="464" stroke="{LINK}" stroke-width="1.4" marker-end="url(#arrow-l)"/>'
    s += f'<circle cx="780" cy="464" r="3.2" fill="{LINK}"/>'
    s += mono(116, 488, "many small noisy steps", 7, SOFT)
    s += mono(316, 488, "many small smooth steps", 7, SOFT)
    s += mono(644, 488, "a few large steps", 7, SOFT)
    s += mono(844, 488, "one jump to the endpoint", 7, LINK)

    s += legend(534, 960, [("decision", ACCENT), ("new training required", LINK),
                           ("compatible solver", MUTED)])
    emit(14, "sampler-decision", "First ask whether you may retrain",
         "Solver changes and objective changes occupy different parts of the acceleration space.", s,
         "A decision tree splits on whether the checkpoint may change, sending off-the-shelf weights "
         "to ancestral or deterministic solvers and a retraining budget to distillation or consistency models",
         960, 578)


def fig15():
    """Guidance is a slider along one ray, so draw the ray and put w on it."""
    s = eyebrow(32, 44, "GUIDANCE SLIDES ALONG ONE LINE")
    ox, oy = 120, 224
    ux, uy = 330, 168                  # unconditional prediction
    dx, dy = 40, 28                    # (conditional − unconditional)
    cx, cy = ux + dx, uy + dy

    s += (f'<line x1="{ux}" y1="{uy}" x2="{ux + dx * 6.6:.0f}" y2="{uy + dy * 6.6:.0f}" '
          f'stroke="{SOFT}" stroke-width="1" stroke-dasharray="6,5"/>')
    for w, tone in ((1.0, MUTED), (3.0, MUTED), (6.0, ACCENT)):
        gx, gy = ux + dx * w, uy + dy * w
        acc = tone is ACCENT
        s += (f'<line x1="{ox}" y1="{oy}" x2="{gx:.0f}" y2="{gy:.0f}" stroke="{tone}" '
              f'stroke-width="{2.2 if acc else 1.1}" '
              f'marker-end="url(#{"arrow-a" if acc else "arrow"})" opacity="{1 if acc else 0.45}"/>')
        s += mono(gx + 12, gy + 16, f"w = {w:g}", 8, tone, "start")
    s += f'<line x1="{ox}" y1="{oy}" x2="{ux}" y2="{uy}" stroke="{MUTED}" stroke-width="1.8" marker-end="url(#arrow)"/>'
    s += f'<line x1="{ox}" y1="{oy}" x2="{cx}" y2="{cy}" stroke="{LINK}" stroke-width="1.8" marker-end="url(#arrow-l)"/>'
    s += f'<circle cx="{ox}" cy="{oy}" r="18" fill="#ffffff" stroke="{INK}" stroke-width="1.4"/>'
    s += subtext(ox, oy + 5, "z", "i", 12, INK)
    s += mono(ux - 8, uy - 14, "εᵤ  null condition", 8, MUTED, "end")
    s += mono(cx + 14, cy - 4, "ε𝑐  text condition", 8, LINK, "start")
    s += mono(120, 402, "w = 1 is the plain conditional prediction; above it the step is an extrapolation, not a blend",
              8, SOFT, "start")

    s += rect(640, 120, 288, 158, "#ffffff", RULE_SOLID)
    s += mono(660, 150, "ONE GUIDED STEP COSTS", 8, SOFT, "start", 500)
    s += text(660, 186, "2 denoiser calls", 15, INK, SANS, 600, "start")
    s += mono(660, 208, "usually one doubled batch", 8, MUTED, "start")
    s += text(660, 244, "1 solver update", 15, ACCENT, SANS, 600, "start")
    s += mono(660, 264, "it never sees the two branches", 8, MUTED, "start")

    s += legend(444, 960, [("guided prediction", ACCENT), ("conditional", LINK),
                           ("unconditional", MUTED)])
    emit(15, "cfg-step", "Guidance changes the field before integration",
         "The solver receives one extrapolated prediction assembled from conditional and null branches.", s,
         "The latent is denoised twice, with a null condition and with text, the predictions are "
         "extrapolated into one guided field, and only then does the solver advance",
         960, 488)


def fig16():
    s = eyebrow(32, 44, "QUALITATIVE BACKBONE MAP · NOT MEASURED DATA")
    ox, oy, w, h = 200, 92, 648, 300
    s += f'<line x1="{ox}" y1="{oy+h}" x2="{ox+w+28}" y2="{oy+h}" stroke="{INK}" stroke-width="1.2" marker-end="url(#arrow)"/>'
    s += f'<line x1="{ox}" y1="{oy+h}" x2="{ox}" y2="{oy-28}" stroke="{INK}" stroke-width="1.2" marker-end="url(#arrow)"/>'
    s += f'<line x1="{ox+w/2}" y1="{oy}" x2="{ox+w/2}" y2="{oy+h}" stroke="{RULE}" stroke-width="0.8"/>'
    s += f'<line x1="{ox}" y1="{oy+h/2}" x2="{ox+w}" y2="{oy+h/2}" stroke="{RULE}" stroke-width="0.8"/>'
    points = [
        (300, 344, "U-Net", MUTED, "local pyramid", "start"),
        (492, 236, "U-ViT", BLUE, "skips + tokens", "start"),
        (614, 300, "DiT", INK, "shared tokens", "start"),
        (770, 158, "MM-DiT", ACCENT, "separate streams", "end"),
    ]
    for x, y, name, colour, sub, anchor in points:
        dx = 16 if anchor == "start" else -18
        s += f'<circle cx="{x}" cy="{y}" r="7" fill="{colour}"/>'
        s += text(x + dx, y - 6, name, 13, colour, weight=600, anchor=anchor)
        s += mono(x + dx, y + 14, sub, 8, SOFT, anchor)

    # Axis names sit clear of both the arrowheads and the eyebrow.
    s += (f'<g transform="rotate(-90 {ox - 44} {oy + h / 2})">'
          + mono(ox - 44, oy + h / 2, "MODALITY INTERACTION", 8, MUTED) + '</g>')
    s += mono(ox - 30, oy + 6, "separate", 8, SOFT, "end")
    s += mono(ox - 30, oy + h, "shared", 8, SOFT, "end")
    s += mono(ox + w / 2, oy + h + 32, "TOKEN MIXING RANGE", 8, MUTED)
    s += mono(ox, oy + h + 22, "local", 8, SOFT, "start")
    s += mono(ox + w, oy + h + 22, "global", 8, SOFT, "end")

    s += legend(452, 960, [("conv pyramid", MUTED), ("skips + tokens", BLUE),
                           ("single stream", INK), ("split streams", ACCENT)])
    emit(16, "backbone-map", "Backbone choice follows structure and scale",
         "Locality, token count and modality interaction matter more than architecture fashion.", s,
         "A qualitative map places U-Net, U-ViT, DiT and MM-DiT by how far their token mixing reaches "
         "and how separately they treat modalities; it plots no measured data",
         960, 496)


if __name__ == "__main__":
    cover()
    # fig04 is laid out by mermaid — see _mermaid.py and blog-visuals section 5.
    for fn in (fig01, fig02, fig03, fig05, fig06, fig07, fig08, fig09, fig10,
               fig11, fig12, fig13, fig14, fig15, fig16):
        fn()
