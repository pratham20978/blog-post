#!/usr/bin/env python3
"""Build the editable HTML sources for the diffusion article's social package."""

from __future__ import annotations

import html
import pathlib
import re


HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
TEMPLATES = HERE.parents[2] / ".claude/blog-forge/skills/blog-visuals/assets"

INK = "#2d3142"
BLUE = "#4f5d75"
SILVER = "#bfc0c0"
PAPER = "#f5f5f5"
ORANGE = "#eb6c36"
MUTED = "#7a8399"
WHITE = "#ffffff"
RULE = "rgba(45,49,66,.14)"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"


def mix(a, b, t):
    """Blend two #rrggbb colours; t=0 gives a, t=1 gives b."""
    pa = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    pb = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(pa, pb))


def lcg(seed):
    """Deterministic noise so a rebuild reproduces the same card."""
    state = seed
    while True:
        state = (1103515245 * state + 12345) % 2147483648
        yield state / 2147483648


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x, y, value, size=20, fill=INK, family=SANS, weight=400,
         anchor="start", spacing=None, italic=False):
    attrs = ""
    if spacing is not None:
        attrs += f' letter-spacing="{spacing}"'
    if italic:
        attrs += ' font-style="italic"'
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"{attrs}>'
            f'{esc(value)}</text>')


def lines(x, y, values, size=20, gap=30, **kwargs):
    return "".join(text(x, y + i * gap, value, size, **kwargs)
                   for i, value in enumerate(values))


def rect(x, y, w, h, fill=WHITE, stroke=RULE, radius=8, width=1):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')


def line(x1, y1, x2, y2, stroke=BLUE, width=2, marker=False, dash=None):
    attrs = ' marker-end="url(#arrow)"' if marker else ""
    if dash:
        attrs += f' stroke-dasharray="{dash}"'
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{stroke}" stroke-width="{width}"{attrs}/>')


def circle(cx, cy, r, fill=WHITE, stroke=BLUE, width=2):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{width}"/>')


def tiles(x, y, cols, rows, cell, values, gap=3, rx=3, accent=None):
    """A field drawn cell by cell. Shading carries the value; no label needed."""
    out = ""
    for r in range(rows):
        for c in range(cols):
            v = values[r * cols + c]
            hot = accent == (r, c)
            fill = ORANGE if hot else mix("#eef0f3", "#2d3142", min(1, max(0, v)))
            out += (f'<rect x="{x + c * (cell + gap):.1f}" y="{y + r * (cell + gap):.1f}" '
                    f'width="{cell}" height="{cell}" rx="{rx}" fill="{fill}"/>')
    return out


def noise_tiles(x, y, cols, rows, cell, signal, target, seed, gap=3, rx=3, accent=None):
    """The same mixture the article uses: sqrt(abar)*target + sqrt(1-abar)*noise."""
    rng = lcg(seed)
    n = [next(rng) for _ in range(cols * rows)]
    sig, noi = signal ** 0.5, (1 - signal) ** 0.5
    vals = [sig * target[i] + noi * n[i] for i in range(cols * rows)]
    return tiles(x, y, cols, rows, cell, vals, gap, rx, accent)


def polyline(pts, stroke=BLUE, width=4, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    body = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return (f'<polyline points="{body}" fill="none" stroke="{stroke}" '
            f'stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{d}/>')


def plot(x, y, w, h, fn, stroke=BLUE, width=4, samples=90):
    """fn(u in 0..1) -> 0..1 measured up from the baseline."""
    return polyline([(x + u / samples * w, y + h - fn(u / samples) * h)
                     for u in range(samples + 1)], stroke, width)


def disc(n, r):
    c = (n - 1) / 2
    return [0.94 if (i // n - c) ** 2 + (i % n - c) ** 2 <= r * r else 0.06
            for i in range(n * n)]


def template_logo(kind):
    source = (TEMPLATES / f"social-{kind}-template.html").read_text(encoding="utf-8")
    found = re.search(rf'<g id="canery-lockup-{kind}"[\s\S]*?</g>', source)
    if not found:
        raise RuntimeError(f"locked {kind} logo was not found")
    return found.group(0)


LOGOS = {kind: template_logo(kind) for kind in ("feed", "story")}


def defs(kind):
    return f'''<defs>
<style>@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap');</style>
<marker id="arrow" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="10" refX="13" refY="5" orient="auto"><polygon points="0 0, 14 5, 0 10" fill="{BLUE}"/></marker>
<marker id="arrow-orange" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="11" refX="15" refY="5.5" orient="auto"><polygon points="0 0, 16 5.5, 0 11" fill="{ORANGE}"/></marker>
<marker id="arrow-ink" markerUnits="userSpaceOnUse" markerWidth="14" markerHeight="10" refX="13" refY="5" orient="auto"><polygon points="0 0, 14 5, 0 10" fill="{INK}"/></marker>
{LOGOS[kind]}
</defs>'''


def logo(kind):
    if kind == "feed":
        return '<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="72" data-logo-width="180" transform="translate(72 72) scale(.2680965)"><use href="#canery-lockup-feed"/></g>'
    return '<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="250" data-logo-width="200" transform="translate(72 250) scale(.297885)"><use href="#canery-lockup-story"/></g>'


def header(kind, number, total, title_values, setup_values):
    if kind == "feed":
        out = logo(kind)
        out += text(1008, 105, f"{number:02d} / {total:02d}", 15, MUTED, MONO, 500, "end", ".16em")
        out += line(72, 150, 1008, 150, RULE, 1)
        out += lines(72, 236, title_values, 58, 62, family=SERIF)
        setup_y = 358 if len(title_values) == 1 else 374
        out += lines(72, setup_y, setup_values, 21, 29, fill=BLUE)
        return out
    out = logo(kind)
    out += text(1008, 285, f"{number:02d} / {total:02d}", 17, MUTED, MONO, 500, "end", ".16em")
    out += line(72, 340, 1008, 340, RULE, 1)
    out += lines(72, 458, title_values, 66, 70, family=SERIF)
    setup_y = 595 if len(title_values) == 1 else 618
    out += lines(72, setup_y, setup_values, 25, 34, fill=BLUE)
    return out


def footer(kind, takeaway, label="DIFFUSION MODEL ARCHITECTURE · CANERY"):
    if kind == "feed":
        out = line(72, 1166, 1008, 1166, RULE, 1)
        out += lines(72, 1216, takeaway, 22, 29, weight=600)
        out += text(72, 1303, label, 13, ORANGE, MONO, 500, spacing=".13em")
        return out
    out = line(72, 1570, 1008, 1570, RULE, 1)
    out += lines(72, 1630, takeaway, 27, 36, weight=600)
    out += text(72, 1740, label, 15, ORANGE, MONO, 500, spacing=".13em")
    return out


def document(kind, title_value, description, body):
    height = 1350 if kind == "feed" else 1920
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 {height}" '
           f'width="1080" height="{height}" role="img" aria-labelledby="title description">'
           f'<title id="title">{esc(title_value)}</title><desc id="description">{esc(description)}</desc>'
           f'{defs(kind)}<rect width="1080" height="{height}" fill="{PAPER}"/>{body}</svg>')
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title_value)}</title>'
            '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&amp;family=Geist:wght@400;500;600&amp;family=Geist+Mono:wght@400;500;600&amp;display=swap" rel="stylesheet">'
            f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style></head><body>{svg}</body></html>')


def feed_01():
    body = header("feed", 1, 8, ["A diffusion model is a system."],
                  ["The denoiser is one component—not the whole generator."])
    motif = disc(7, 2.6)
    for i, abar in enumerate([0.0, 0.3, 0.68, 1.0]):
        body += noise_tiles(104 + i * 232, 440, 7, 7, 22, abar, motif,
                            seed=7000 + i * 91, gap=3, rx=3,
                            accent=(3, 3) if i == 2 else None)
        if i < 3:
            body += line(104 + i * 232 + 180, 526, 104 + i * 232 + 216, 526, SILVER, 3, True)
    body += text(540, 712, "noise → data is the product; the system is what gets it there",
                 18, MUTED, MONO, 400, "middle")

    rows = [("REPRESENTATION", "pixels or latent"), ("PATH", "which noisy states exist"),
            ("FIELD", "the learned direction"), ("CONDITION", "text · class · maps"),
            ("SOLVER", "how each step is taken")]
    y = 762
    for i, (name, detail) in enumerate(rows):
        active = i == 2
        body += rect(132, y, 816, 74, "rgba(235,108,54,.08)" if active else WHITE,
                     ORANGE if active else RULE)
        body += text(168, y + 32, f"0{i+1}", 12, ORANGE if active else MUTED, MONO, 600, spacing=".12em")
        body += text(234, y + 36, name, 16, ORANGE if active else INK, MONO, 600, spacing=".06em")
        body += text(610, y + 36, detail, 17, BLUE, SANS, 400)
        y += 82
    body += footer("feed", ["Architecture is the contract among all five axes."])
    return document("feed", "A diffusion model is a system", "A noise-to-data strip above five design axes: representation, path, field, conditioning and solver.", body)


def matrix(x, y, values, accent=None):
    out = ""
    for row in range(2):
        for col in range(2):
            index = row * 2 + col
            fill = "rgba(235,108,54,.10)" if accent == index else PAPER
            stroke = ORANGE if accent == index else RULE
            out += rect(x + col * 92, y + row * 72, 78, 58, fill, stroke, 5)
            out += text(x + col * 92 + 39, y + row * 72 + 36, values[index], 18,
                        ORANGE if accent == index else INK, MONO, 500, "middle")
    return out


def feed_02():
    body = header("feed", 2, 8, ["One noisy pair teaches the field."],
                  ["Training creates its own target by retaining the sampled noise."])
    body += rect(72, 446, 936, 624, WHITE, RULE)
    body += text(540, 500, "xₜ = √ᾱₜ x₀ + √(1−ᾱₜ) ε", 31, INK, MONO, 500, "middle")
    body += text(230, 574, "0.8 x₀", 16, MUTED, MONO, 600, "middle", ".08em")
    body += matrix(140, 606, ["0.80", "−0.80", "0.40", "0.00"], 3)
    body += text(380, 682, "+", 34, BLUE, SERIF, 400, "middle")
    body += text(540, 574, "0.6 ε", 16, MUTED, MONO, 600, "middle", ".08em")
    body += matrix(450, 606, ["0.12", "0.60", "−0.24", "0.36"], 3)
    body += text(690, 682, "=", 34, BLUE, SERIF, 400, "middle")
    body += text(850, 574, "xₜ", 16, MUTED, MONO, 600, "middle", ".08em")
    body += matrix(760, 606, ["0.92", "−0.20", "0.16", "0.36"], 3)
    body += rect(140, 810, 800, 118, INK, INK)
    body += text(178, 858, "TARGET", 13, "#ffad84", MONO, 600, spacing=".12em")
    body += text(178, 899, "ε is known exactly · example MSE = 0.025", 22, WHITE, MONO, 500)
    body += text(540, 997, "No human labels. No sampling loop inside this training step.", 17, BLUE, SANS, 500, "middle")
    body += footer("feed", ["A sampled timestep turns generation into supervised regression."])
    return document("feed", "One noisy pair teaches the field", "The worked two-by-two tensors show clean signal and sampled noise combining into one supervised diffusion training pair.", body)


def feed_03():
    body = header("feed", 3, 8, ["Path. Field. Solver."],
                  ["Three objects explain most diffusion papers and implementations."])
    cards = [(84, "PATH", ["which states exist", "q(xₜ | x₀)"], SILVER),
             (396, "FIELD", ["where to move", "εθ(xₜ, t, c)"], ORANGE),
             (708, "SOLVER", ["how to step", "xₜ → xₜ₋₁"], BLUE)]
    for x, name, details, colour in cards:
        fill = "rgba(235,108,54,.08)" if colour == ORANGE else WHITE
        body += rect(x, 488, 288, 410, fill, colour, 10, 2)
        body += text(x + 30, 540, name, 15, colour, MONO, 600, spacing=".12em")
        body += circle(x + 144, 670, 66, PAPER, colour, 3)
        if name == "PATH":
            body += line(x + 98, 670, x + 190, 670, BLUE, 3, True)
            body += circle(x + 99, 670, 8, SILVER, SILVER)
        elif name == "FIELD":
            for dy in (-28, 0, 28):
                body += line(x + 102, 670 + dy, x + 184, 642 + dy, ORANGE if dy == 0 else BLUE, 3, True)
        else:
            body += text(x + 144, 682, "Δt", 28, BLUE, MONO, 600, "middle")
        body += lines(x + 144, 810, details, 18, 34, fill=BLUE, family=MONO, anchor="middle")
    body += line(396, 694, 372, 694, SILVER, 2)
    body += line(708, 694, 684, 694, SILVER, 2)
    body += rect(170, 954, 740, 84, PAPER, RULE)
    body += text(540, 1007, "change one layer without renaming the others", 18, INK, MONO, 500, "middle")
    body += footer("feed", ["A faster solver does not teach a better field."])
    return document("feed", "Path, field, and solver", "Three separate cards distinguish the diffusion path, the learned vector field, and the numerical solver.", body)


def feed_04():
    body = header("feed", 4, 8, ["U-Net and DiT estimate the same field."],
                  ["Their inductive biases and cost-carrying shapes are different."])
    body += rect(72, 448, 450, 610, WHITE, RULE)
    body += rect(558, 448, 450, 610, WHITE, RULE)
    body += text(108, 500, "U-NET", 15, MUTED, MONO, 600, spacing=".12em")
    body += text(594, 500, "DIT", 15, MUTED, MONO, 600, spacing=".12em")

    # height = spatial resolution, width = channels. The trade becomes a shape.
    # Blocks must not overlap, or the chain arrows end up running backwards.
    stages = [(104, 616, 20, 140), (152, 706, 46, 96), (216, 780, 64, 62),
              (306, 780, 64, 62), (400, 706, 46, 96), (466, 616, 20, 140)]
    for i, (x, cy, w, h) in enumerate(stages):
        focal = i in (2, 3)
        body += rect(x, cy - h / 2, w, h, "rgba(235,108,54,.10)" if focal else PAPER,
                     ORANGE if focal else SILVER, 4, 2)
    hops = [((124, 616), (146, 700)), ((198, 706), (210, 774)), ((280, 780), (300, 780)),
            ((370, 780), (392, 712)), ((446, 706), (460, 622))]
    for (ax, ay), (bx, by) in hops:
        body += line(ax, ay, bx, by, BLUE, 2, True)
    for y, x1, x2 in ((616, 126, 462), (706, 200, 396)):
        body += line(x1, y, x2, y, SILVER, 2, True, "7 6")
    body += text(297, 916, "height = resolution · width = channels", 15, BLUE, MONO, 500, "middle")
    body += text(297, 982, "spatial scales + skip paths", 16, BLUE, MONO, 500, "middle")

    # One uniform token sequence; its LENGTH is the cost.
    for r in range(4):
        for c in range(8):
            x, y = 598 + c * 46, 592 + r * 46
            active = r == 1 and c == 4
            body += rect(x, y, 38, 38, "rgba(235,108,54,.12)" if active else PAPER,
                         ORANGE if active else SILVER, 4)
    body += line(600, 812, 966, 812, BLUE, 3, True)
    body += text(783, 862, "N tokens, all the same size", 15, BLUE, MONO, 500, "middle")
    body += text(783, 916, "cost grows with N, not with depth", 15, ORANGE, MONO, 500, "middle")
    body += text(783, 982, "token sequence length N", 16, BLUE, MONO, 500, "middle")
    body += footer("feed", ["Choose the backbone with the representation and scale budget."])
    return document("feed", "U-Net and DiT estimate the same field", "A U-Net whose block sizes encode resolution and channels, beside a uniform DiT token grid.", body)


def feed_05():
    body = header("feed", 5, 8, ["Four targets, one noisy point."],
                  ["ε, x₀, score and v are coordinates on the same state."])
    body += rect(72, 446, 936, 566, WHITE, RULE)
    cx, cy, r = 306, 742, 168
    a, sg = 0.8, 0.6
    xt = (cx + a * r, cy - sg * r)
    v = (cx - sg * r, cy - a * r)
    body += circle(cx, cy, r, PAPER, "#e2e3e7", 2)
    body += line(cx - r - 40, cy, cx + r + 40, cy, "#d6d7dc", 2)
    body += line(cx, cy + r + 40, cx, cy - r - 40, "#d6d7dc", 2)
    body += line(xt[0], xt[1], xt[0], cy, SILVER, 2, False, "6 6")
    body += line(xt[0], xt[1], cx, xt[1], SILVER, 2, False, "6 6")
    body += (f'<line x1="{cx}" y1="{cy}" x2="{xt[0]}" y2="{xt[1]}" stroke="{ORANGE}" '
             'stroke-width="5" marker-end="url(#arrow-orange)"/>')
    body += line(cx, cy, v[0], v[1], BLUE, 4, True)
    body += line(cx, cy, cx, cy + r, BLUE, 4, True)
    body += text(xt[0] + 24, xt[1] - 6, "xₜ", 20, ORANGE, MONO, 600)
    body += text(v[0] - 30, v[1] - 12, "v", 20, BLUE, MONO, 600)
    body += text(cx + 18, cy + r + 34, "score", 16, BLUE, MONO, 500)
    body += text(cx + 14, cy - r - 18, "ε", 16, MUTED, MONO, 500)
    body += text(cx + r + 36, cy - 14, "x₀", 16, MUTED, MONO, 500, "end")
    body += text(xt[0] + 14, cy - 40, "σₜ = 0.6", 14, MUTED, MONO, 500)
    body += text(cx + 40, xt[1] - 14, "αₜ = 0.8", 14, MUTED, MONO, 500)

    body += text(596, 520, "GIVEN ONE PREDICTED ε̂", 14, MUTED, MONO, 600, spacing=".10em")
    rows = [("x̂₀", "(xₜ − σₜ·ε̂) / αₜ", INK), ("ŝ", "− ε̂ / σₜ", BLUE),
            ("v̂", "αₜ·ε̂ − σₜ·x̂₀", ORANGE)]
    y = 604
    for name, expr, tone in rows:
        body += text(596, y, name, 24, tone, MONO, 600)
        body += text(676, y, expr, 20, BLUE, MONO, 400)
        y += 82
    body += line(596, 872, 968, 872, RULE, 1)
    body += text(596, 916, "αₜ² + σₜ² = 1  ·  v ⟂ xₜ", 16, MUTED, MONO, 400)
    body += text(596, 952, "the schedule converts one into any other", 16, MUTED, MONO, 400)
    body += rect(72, 1042, 936, 92, INK, INK)
    body += text(540, 1098, "SAME POINT · FOUR REGRESSION PROBLEMS", 19, WHITE, MONO, 600, "middle", ".08em")
    body += footer("feed", ["Checkpoint metadata must name which target the weights encode."])
    return document("feed", "Four targets, one noisy point", "The clean-data and noise plane shows x-t, velocity and score as coordinates on one state, with the conversions from a single predicted epsilon.", body)


def feed_06():
    import math
    body = header("feed", 6, 8, ["The schedule decides which", "noise levels exist."],
                  ["Both curves are definitions, not measured results."])
    T = 1000
    beta = [1e-4 + (0.02 - 1e-4) * i / (T - 1) for i in range(T)]
    lin, acc = [], 1.0
    for b in beta:
        acc *= (1 - b); lin.append(acc)
    off = 0.008
    f0 = math.cos((off / (1 + off)) * math.pi / 2) ** 2
    cos = [max(1e-8, (math.cos(((i / T + off) / (1 + off)) * math.pi / 2) ** 2) / f0)
           for i in range(T)]
    at = lambda ser, u: ser[min(T - 1, max(0, int(u * (T - 1))))]

    px, py, pw, ph = 180, 530, 720, 380
    body += rect(72, 446, 936, 574, WHITE, RULE)
    body += line(px, py + ph, px + pw, py + ph, SILVER, 2)
    body += line(px, py, px, py + ph, SILVER, 2)
    body += text(px - 18, py + 10, "1", 15, MUTED, MONO, 400, "end")
    body += text(px - 18, py + ph + 6, "0", 15, MUTED, MONO, 400, "end")
    body += text(px, py + ph + 40, "t = 0", 15, MUTED, MONO, 400, "middle")
    body += text(px + pw, py + ph + 40, "t = T", 15, MUTED, MONO, 400, "middle")
    body += plot(px, py, pw, ph, lambda u: at(lin, u), BLUE, 5)
    body += plot(px, py, pw, ph, lambda u: at(cos, u), ORANGE, 5)
    body += text(px + 28, py + ph - 28, "ᾱₜ  ·  how much signal survives", 18, MUTED, MONO, 400)
    body += text(px + pw - 12, py + 150, "cosine", 18, ORANGE, MONO, 600, "end")
    body += text(px + 236, py + ph - 96, "linear", 18, BLUE, MONO, 600, "start")
    end = lin[-1] / (1 - lin[-1])
    body += circle(px + pw, py + ph - 4, 9, BLUE, BLUE, 0)
    body += text(px + pw, py + ph + 78, f"linear ends at SNR ≈ {end:.0e}, not 0", 17, BLUE, MONO, 500, "end")
    body += rect(140, 1052, 800, 86, INK, INK)
    body += text(540, 1104, "SMALL IS NOT ZERO — AND INFERENCE STARTS AT ZERO", 18, WHITE, MONO, 600, "middle", ".05em")
    body += footer("feed", ["A nonzero terminal SNR is a train-inference mismatch,",
                            "not a rounding detail."])
    return document("feed", "The schedule decides which noise levels exist", "Signal-coefficient curves for the linear and cosine schedules, marking the linear schedule's nonzero terminal SNR.", body)


def feed_07():
    body = header("feed", 7, 8, ["Same shape. Wrong meaning."],
                  ["A checkpoint can pass every assertion and still be misread."])
    body += rect(72, 446, 936, 476, WHITE, RULE)
    motif = disc(7, 2.6)

    # One tensor in the middle; two readings of it that do not agree.
    body += tiles(462, 494, 7, 7, 20, [0.5] * 49, 3, 3)
    body += text(540, 480, "ONE 4×64×64 TENSOR", 14, MUTED, MONO, 600, "middle", ".10em")
    body += line(452, 624, 338, 676, BLUE, 3, True)
    body += line(628, 624, 742, 676, ORANGE, 3, True)

    body += noise_tiles(210, 700, 7, 7, 20, 1.0, motif, seed=11, gap=3, rx=3)
    body += text(210, 672, "read as ε", 18, BLUE, MONO, 600, "start")
    body += text(292, 890, "coherent sample", 16, BLUE, MONO, 400, "middle")

    body += noise_tiles(690, 700, 7, 7, 20, 0.12, motif, seed=29, gap=3, rx=3)
    body += text(854, 672, "read as v", 18, ORANGE, MONO, 600, "end")
    body += text(772, 890, "washed out, same shapes", 16, ORANGE, MONO, 400, "middle")

    pairs = [("B×4×64×64", "latent scale 1.0 or 0.18215?"),
             ("4 output channels", "ε, x₀ or v?"),
             ("t ∈ [0, 999]", "respaced, or indexed from 1?"),
             ("final step runs", "is terminal SNR actually zero?")]
    y = 966
    for shape, meaning in pairs:
        body += text(96, y, "✓", 17, "#9aa3ad", SANS, 600)
        body += text(128, y, shape, 18, INK, MONO, 500)
        body += text(548, y, "?", 17, ORANGE, SANS, 700)
        body += text(580, y, meaning, 17, BLUE, MONO, 400)
        y += 44
    body += footer("feed", ["Overexposed or washed-out output is usually a metadata bug,",
                            "not a weights bug."])
    return document("feed", "Same shape, wrong meaning", "One tensor read two incompatible ways, above four checkpoint properties that are shape-correct but semantically ambiguous.", body)


def feed_08():
    body = header("feed", 8, 8, ["Design the interfaces, not one magic block."],
                  ["Use this architecture check before changing a checkpoint."])
    items = [("01", "REPRESENTATION", "pixels or latent · exact scaling"),
             ("02", "PATH", "schedule · terminal SNR"),
             ("03", "FIELD", "U-Net · DiT · and its ε/x₀/score/v target"),
             ("04", "CONDITIONING", "tokens · cross-attention · adaLN"),
             ("05", "SOLVER", "sampler · steps · guidance")]
    y = 452
    for index, name, detail in items:
        body += rect(72, y, 936, 102, WHITE, RULE)
        body += circle(122, y + 51, 24, PAPER, ORANGE if index == "05" else SILVER, 2)
        body += text(122, y + 57, index, 12, ORANGE if index == "05" else MUTED, MONO, 600, "middle")
        body += text(174, y + 44, name, 15, INK, MONO, 600, spacing=".10em")
        body += text(174, y + 76, detail, 18, BLUE, SANS, 400)
        y += 112
    body += rect(72, 1030, 936, 86, INK, INK)
    body += text(540, 1082, "READ THE COMPLETE L4 GUIDE · CANERY.IN", 17, WHITE, MONO, 600, "middle", ".08em")
    body += footer("feed", ["A diffusion model works only when every contract agrees."], "DIFFUSION MODEL ARCHITECTURE · FULL GUIDE")
    return document("feed", "Design the interfaces, not one magic block", "A five-axis architecture checklist covers representation, path, field, conditioning, and solver.", body)


def story_01():
    body = header("story", 1, 4, ["Noise is the start,", "not the architecture."],
                  ["Generation follows a learned field through many", "numerical updates toward the data distribution."])
    body += rect(72, 720, 936, 730, WHITE, RULE)
    rng = lcg(20260920)
    y_values = [800, 952, 1104, 1256]
    for row, y in enumerate(y_values):
        w = row / (len(y_values) - 1)          # how much signal has been recovered
        body += text(126, y + 34, f"0{row+1}", 13, MUTED, MONO, 600, spacing=".10em")
        for col in range(6):
            n = next(rng)
            active = row == 2 and col == 3
            # Grain and misalignment both fall as the trajectory approaches data.
            shade = mix(mix("#eceef1", "#8b929d", n), BLUE, w)
            offset = round((n - 0.5) * 2 * 22 * (1 - w))
            body += rect(250 + col * 94, y + offset, 62, 62,
                         ORANGE if active else shade, ORANGE if active else shade, 5)
        if row < 3:
            body += line(540, y + 84, 540, y + 126, BLUE, 2, True)
    body += text(540, 1406, "repeated field evaluation + solver step", 17, BLUE, MONO, 500, "middle")
    body += footer("story", ["A complete system coordinates representation, path,", "field, condition, and solver."])
    return document("story", "Noise is the start, not the architecture", "Four rows of tiles lose their grain and misalignment as repeated field evaluations and solver steps recover structure.", body)


def story_02():
    body = header("story", 2, 4, ["Guidance changes the direction", "before the solver moves."],
                  ["Classifier-free guidance extrapolates past the", "conditional prediction, it does not average."])
    body += rect(72, 724, 936, 720, WHITE, RULE)
    body += text(540, 806, "εguided = εu + w(εc − εu)", 30, INK, MONO, 500, "middle")

    # w = 2, so the guided tip sits on the u-to-c ray, one step beyond c.
    o, u, c = (280, 1010), (540, 944), (584, 1058)
    w = 2
    g = (u[0] + w * (c[0] - u[0]), u[1] + w * (c[1] - u[1]))

    body += line(u[0], u[1], g[0], g[1], SILVER, 2, False, "7 7")
    body += line(o[0], o[1], u[0], u[1], "#a9aeb8", 4, True)
    body += line(o[0], o[1], c[0], c[1], BLUE, 4, True)
    body += (f'<line x1="{o[0]}" y1="{o[1]}" x2="{g[0]}" y2="{g[1]}" stroke="{ORANGE}" '
             'stroke-width="6" marker-end="url(#arrow-orange)"/>')
    body += line(u[0], u[1], c[0], c[1], SILVER, 2, False, "5 5")

    body += circle(o[0], o[1], 34, PAPER, INK, 3)
    body += text(o[0], o[1] + 7, "xₜ", 17, INK, MONO, 600, "middle")
    body += text(u[0] + 20, u[1] - 12, "unconditional εu", 16, MUTED, MONO, 500)
    body += text(c[0] + 22, c[1] + 2, "conditional εc", 16, BLUE, MONO, 500)
    body += text(g[0] + 22, g[1] + 10, "guided · w = 2", 17, ORANGE, MONO, 600)
    body += text(430, 1218, "the guided tip stays on the εu → εc line", 15, MUTED, MONO, 400, "middle")

    body += rect(230, 1252, 620, 104, INK, INK)
    body += text(540, 1295, "THEN ONE SOLVER UPDATE", 14, "#ffad84", MONO, 600, "middle", ".12em")
    body += text(540, 1331, "xₜ → xₜ₋₁", 23, WHITE, MONO, 500, "middle")
    body += footer("story", ["Stronger guidance can improve adherence", "while reducing diversity or causing artifacts."])
    return document("story", "Guidance changes direction before the solver moves", "The guided prediction is an extrapolation along the line from the unconditional to the conditional prediction, taken before a single solver update.", body)


def story_03():
    body = header("story", 3, 4, ["The encoder sets a ceiling", "the denoiser cannot cross."],
                  ["Whatever E throws away, D cannot return —", "and no sampler can invent it."])
    body += rect(72, 724, 936, 720, WHITE, RULE)
    stages = [
        (804, "x  ·  fine detail present", 16, True),
        (1000, "z = E(x)  ·  8× smaller per side", 8, False),
        (1196, "D(E(x))  ·  detail gone for good", 16, False),
    ]
    for y, caption, count, alternating in stages:
        gap = 8 if count == 16 else 12
        cell = (832 - gap * (count - 1)) / count
        for i in range(count):
            if alternating:
                shade = "#343a4a" if i % 2 else "#e2e4e8"
            else:
                shade = "#b4b8c1"
            active = (alternating and i == 9) or (count == 16 and not alternating and i == 9)
            body += rect(round(132 + i * (cell + gap)), y, round(cell), 62,
                         ORANGE if active else shade, ORANGE if active else shade, 5)
        body += text(132, y + 98, caption, 17, BLUE, MONO, 500)
    for y in (890, 1086):
        body += line(540, y, 540, y + 44, BLUE, 2, True)
    body += rect(132, 1336, 832, 84, INK, INK)
    body += text(548, 1386, "MEASURE D(E(x)) BEFORE YOU BLAME THE DENOISER", 17, WHITE, MONO, 600, "middle", ".06em")
    body += footer("story", ["Small text and faces often fail at the autoencoder,", "not at the diffusion objective."])
    return document("story", "The encoder sets a ceiling the denoiser cannot cross", "A high-frequency pixel pattern is compressed into a coarser latent and comes back uniform, showing the autoencoder reconstruction ceiling.", body)


def story_04():
    body = header("story", 4, 4, ["Read the complete", "diffusion architecture guide."],
                  ["From the forward process to U-Nets, DiTs,", "conditioning, objectives, and samplers."])
    body += rect(72, 724, 936, 670, INK, INK)
    topics = [("PATH", "forward process + SNR"), ("FIELD", "U-Net + transformers"),
              ("TARGET", "ε + x₀ + score + v"), ("CONDITION", "text + CFG"),
              ("SOLVER", "DDPM + DDIM + ODE")]
    y = 798
    for i, (name, detail) in enumerate(topics):
        body += circle(128, y - 6, 19, INK, ORANGE if i == 4 else SILVER, 2)
        body += text(128, y, "✓", 14, ORANGE if i == 4 else WHITE, SANS, 600, "middle")
        body += text(174, y, name, 14, "#ffad84" if i == 4 else WHITE, MONO, 600, spacing=".10em")
        body += text(440, y, detail, 19, "#d9dbe3", SANS, 400)
        y += 100
    body += line(120, 1318, 960, 1318, "rgba(255,255,255,.18)", 1)
    body += text(540, 1360, "CANERY.IN/BLOGS/DIFFUSION-MODEL-ARCHITECTURE", 14, WHITE, MONO, 600, "middle", ".05em")
    body += footer("story", ["Add the link sticker below, then keep this", "reference for your next model review."], "READ THE ARTICLE · LINK STICKER")
    return document("story", "Read the complete diffusion architecture guide", "A five-part checklist closes the Story with the article URL and a prompt to read the full guide.", body)


ASSETS = {
    "feed-01-diffusion-is-a-system": feed_01,
    "feed-02-one-noisy-training-pair": feed_02,
    "feed-03-path-field-solver": feed_03,
    "feed-04-unet-vs-dit": feed_04,
    "feed-05-four-targets-one-point": feed_05,
    "feed-06-noise-schedule": feed_06,
    "feed-07-same-shape-wrong-meaning": feed_07,
    "feed-08-design-checklist": feed_08,
    "story-01-noise-to-structure": story_01,
    "story-02-guidance-changes-direction": story_02,
    "story-03-autoencoder-ceiling": story_03,
    "story-04-read-the-complete-guide": story_04,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, builder in ASSETS.items():
        (OUT / f"{stem}.html").write_text(builder(), encoding="utf-8")
        print(f"built {stem}")


if __name__ == "__main__":
    main()
