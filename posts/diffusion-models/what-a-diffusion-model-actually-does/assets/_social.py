#!/usr/bin/env python3
"""Build the editable HTML sources for the part-1 diffusion article's social package.

Every card's artefact is computed here from the same numbers the article uses.
"""

from __future__ import annotations

import html
import pathlib
import re


HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
# one level deeper than a standalone post: posts/<series>/<post>/assets
TEMPLATES = HERE.parents[3] / ".claude/blog-forge/skills/blog-visuals/assets"

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
            fill = ORANGE if hot else mix("#20232e", "#f7f8f9", min(1, max(0, v)))
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
        return '<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="72" data-logo-width="220" transform="translate(72 72) scale(.2680965)"><use href="#canery-lockup-feed"/></g>'
    return '<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="250" data-logo-width="245" transform="translate(72 250) scale(.297885)"><use href="#canery-lockup-story"/></g>'


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


def footer(kind, takeaway, label="WHAT A DIFFUSION MODEL ACTUALLY DOES · CANERY"):
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


# --------------------------------------------------------------- the article

X0 = [0.95, 0.60, -0.30, -0.85,
      0.80, 0.45, -0.55, -0.90,
      0.55, 0.10, -0.70, -0.95,
      0.25, -0.20, -0.85, -1.00]
EPS = [-0.55, 1.40, 0.45, -1.10,
       0.85, -1.35, -0.25, 0.70,
       1.25, 0.30, -0.95, 0.15,
       -1.05, 0.90, 1.45, -1.10]
SIG = [0.8 * v for v in X0]
NOI = [0.6 * v for v in EPS]
XT = [a + b for a, b in zip(SIG, NOI)]


def crescent(n):
    """The article's motif, as a flat 0..1 list for `tiles`."""
    out, c = [], (n - 1) / 2
    for r in range(n):
        for col in range(n):
            d = (((r - c) ** 2 + (col - c) ** 2) ** 0.5) / (n / 2)
            v = 0.95 if d < 0.60 else (-0.85 if d > 0.78 else 0.10)
            d2 = ((((r - c + n * 0.17) ** 2 + (col - c + n * 0.17) ** 2) ** 0.5) / (n / 2))
            if d < 0.60 and d2 < 0.46:
                v = -0.50
            out.append((v + 1.0) / 2.0)
    return out


def vcell(x, y, w, h, value, hot=False, ring=False, size=15, lo=-1.6, hi=1.6):
    """One printed value on a tile shaded by that value."""
    u = min(1.0, max(0.0, (value - lo) / (hi - lo)))
    fill = mix("#f7f8f9", "#20232e", 1 - u)
    ink = WHITE if u < 0.46 else INK
    out = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" '
           f'stroke="{ORANGE if hot else (BLUE if ring else SILVER)}" '
           f'stroke-width="{3 if (hot or ring) else 1}"/>')
    out += text(x + w / 2, y + h / 2 + size * 0.36, f"{value:.2f}", size,
                ORANGE if hot else ink, MONO, 600 if hot else 400, "middle")
    return out


def vmatrix(x, y, values, cell=60, gap=6, hot=None, ring=None, size=15):
    out = ""
    for i, v in enumerate(values):
        r, c = divmod(i, 4)
        out += vcell(x + c * (cell + gap), y + r * (cell + gap), cell, cell, v,
                     hot=(i == hot), ring=(i == ring), size=size)
    return out


def patch(x, y, n, cell, values, gap=3, outline=None):
    out = tiles(x, y, n, n, cell, values, gap, 3)
    if outline:
        w = n * cell + (n - 1) * gap
        out += (f'<rect x="{x - 6}" y="{y - 6}" width="{w + 12}" height="{w + 12}" '
                f'rx="8" fill="none" stroke="{outline}" stroke-width="3"/>')
    return out


def flat(kind):
    """Candidate patches for the averaging card, as 0..1 lists."""
    n, out = 6, []
    for r in range(n):
        for c in range(n):
            if kind == "v":
                v = 0.92 if c < 3 else 0.08
            elif kind == "h":
                v = 0.92 if r < 3 else 0.08
            elif kind == "d":
                v = 0.92 if (r + c) < 5 else 0.08
            else:
                v = 0.92 if max(abs(r - 2.5), abs(c - 2.5)) < 1.6 else 0.08
            out.append(v)
    return out


def stat(x, y, w, value, label, detail, accent=False, vsize=64):
    out = rect(x, y, w, 196, "rgba(235,108,54,.06)" if accent else WHITE,
               ORANGE if accent else RULE)
    out += text(x + 28, y + 86, value, vsize, ORANGE if accent else INK, MONO, 600)
    out += text(x + 28, y + 126, label, 19, INK, SANS, 600)
    out += lines(x + 28, y + 158, detail, 15, 22, fill=MUTED)
    return out


# ------------------------------------------------------------------- feed

def feed_01():
    body = header("feed", 1, 7, ["Trained only to undo noise."],
                  ["It is never shown a picture and asked to draw one."])
    motif = crescent(11)
    for i, abar in enumerate([0.012, 0.10, 0.34, 0.70, 0.97]):
        body += noise_tiles(86 + i * 186, 470, 11, 11, 13, abar, motif,
                            seed=4100 + i * 137, gap=2, rx=2)
        if i == 4:
            body += (f'<rect x="{86 + 4 * 186 - 7}" y="463" width="177" height="177" '
                     f'rx="8" fill="none" stroke="{ORANGE}" stroke-width="3"/>')
        if i < 4:
            body += line(86 + i * 186 + 172, 551, 86 + i * 186 + 176, 551, SILVER, 3, True)
    body += line(86, 690, 994, 690, RULE, 1)
    body += text(86, 722, "ᾱ  0.012", 15, MUTED, MONO, 500, spacing=".12em")
    body += text(994, 722, "0.97", 15, ORANGE, MONO, 500, "end", spacing=".12em")

    body += rect(86, 774, 908, 300, WHITE, RULE)
    body += text(126, 838, "xₜ = √ᾱₜ · x₀ + √(1−ᾱₜ) · ε",
                 34, INK, MONO, 600)
    body += text(126, 878, "forward · closed form · zero parameters", 17, MUTED, MONO, 400,
                 spacing=".08em")
    body += line(126, 918, 954, 918, RULE, 1)
    body += text(126, 984, "xₜ₋₁ = f( xₜ , t , εθ(xₜ, t) )", 34, ORANGE, MONO, 600)
    body += text(126, 1024, "reverse · no closed form · this is the network", 17, ORANGE,
                 MONO, 400, spacing=".08em")

    body += footer("feed", ["Nothing on the first line is learned.",
                            "Everything anyone trains lives on the second."])
    return document("feed", "Trained only to undo noise",
                    "Pure noise resolving in five stages into a crescent, above the closed-form "
                    "forward equation and the learned reverse step.", body)


def feed_02():
    body = header("feed", 2, 7, ["The answer key is free."],
                  ["We draw the noise before adding it, so the target needs no labelling."])
    for i, (vals, label, hot, ring) in enumerate([
            (SIG, "0.8 · x₀", 1, 14), (NOI, "0.6 · ε", 1, 14),
            (XT, "xₜ", 1, 14)]):
        x = 86 + i * 306
        body += vmatrix(x, 452, vals, cell=60, gap=6, hot=hot, ring=ring, size=15)
        body += text(x + 132, 748, label, 22, INK, MONO, 600, "middle")
    body += text(86 + 276, 578, "+", 42, MUTED, MONO, 400, "middle")
    body += text(86 + 582, 578, "=", 42, MUTED, MONO, 400, "middle")

    body += rect(86, 790, 440, 130, WHITE, ORANGE)
    body += text(118, 850, "0.48 + 0.84 = 1.32", 27, ORANGE, MONO, 600)
    body += text(118, 890, "brighter than any pixel x₀ had", 17, MUTED, SANS, 400)
    body += rect(554, 790, 440, 130, WHITE, BLUE)
    body += text(586, 850, "−0.68 + 0.87 = 0.19", 27, BLUE, MONO, 600)
    body += text(586, 890, "near-black arrives mid-grey", 17, MUTED, SANS, 400)

    body += text(86, 990, "ᾱₜ = 0.64, so the coefficients are exactly 0.8 and 0.6.",
                 21, INK, SANS, 500)
    body += text(86, 1026, "The network is shown xₜ and t. The target is the ε we already hold.",
                 21, MUTED, SANS, 400)
    body += footer("feed", ["No annotator, no labels — a fresh training pair",
                            "from any image, at any noise level, forever."])
    return document("feed", "The answer key is free",
                    "Three four-by-four grids of printed values — scaled signal, scaled noise "
                    "and their sum — with two cells traced through the addition.", body)


def feed_03():
    body = header("feed", 3, 7, ["One call returns an average."],
                  ["Many clean patches explain the same noisy one. It cannot pick."])
    body += patch(86, 520, 6, 34, noise_mix(), outline=INK)
    body += text(86 + 110, 800, "x\u209c  \u00b7  \u03b1\u0304 = 0.09", 20, INK, MONO, 600, "middle")

    body += rect(340, 440, 400, 380, "none", RULE)
    labels = ["vertical", "horizontal", "diagonal", "blob"]
    for i, kind in enumerate(["v", "h", "d", "b"]):
        x = 390 + (i % 2) * 170
        y = 474 + (i // 2) * 172
        body += patch(x, y, 6, 20, flat(kind))
        body += text(x + 65, y + 158, labels[i], 15, MUTED, MONO, 400, "middle")

    avg = [sum(f[i] for f in (flat("v"), flat("h"), flat("d"), flat("b"))) / 4
           for i in range(36)]
    body += patch(775, 520, 6, 34, avg, outline=ORANGE)
    body += text(775 + 110, 800, "E[ x\u2080 | x\u209c ]", 20, ORANGE, MONO, 600, "middle")
    body += line(748, 630, 766, 630, ORANGE, 3, True)

    body += rect(86, 856, 908, 150, "rgba(235,108,54,.06)", ORANGE)
    body += text(120, 916, "Squared-error training drives the network", 26, INK, SANS, 600)
    body += text(120, 956, "to the mean of the candidates, not to one of them.", 26, INK, SANS, 600)
    body += footer("feed", ["The blur is not the network being weak.",
                            "A perfect network would return the same blur."])
    return document("feed", "One call returns an average",
                    "A noisy patch fanning out to four clean patches that could have produced it, "
                    "and the smeared mean the network is trained to output.", body)


def noise_mix():
    """The observation in card 3: the vertical-edge candidate at abar = 0.09."""
    rng = lcg(11)
    base = flat("v")
    s, k = 0.09 ** 0.5, (1 - 0.09) ** 0.5
    return [min(1.0, max(0.0, s * base[i] + k * next(rng))) for i in range(36)]


def feed_04():
    body = header("feed", 4, 7, ["Why it takes many small steps."],
                  ["A prediction error is amplified when it is turned back into an image."])
    body += rect(86, 452, 908, 118, WHITE, RULE)
    body += text(540, 502, "an error δ in the predicted noise", 22, MUTED, SANS, 400, "middle")
    body += text(540, 546, "lands as  √(1−ᾱ)/√ᾱ  ×  δ  in the image",
                 27, INK, MONO, 600, "middle")

    rows = [(0.96, 0.20), (0.64, 0.75), (0.25, 1.73), (0.02, 7.00)]
    y = 610
    for abar, amp in rows:
        hot = abar == 0.02
        body += rect(86, y, 908, 92, "rgba(235,108,54,.06)" if hot else WHITE,
                     ORANGE if hot else RULE)
        body += text(126, y + 58, f"ᾱ = {abar:.2f}", 26,
                     ORANGE if hot else INK, MONO, 500)
        bar = 600 * (amp / 7.0)
        body += (f'<rect x="330" y="{y + 34}" width="{bar:.0f}" height="24" rx="6" '
                 f'fill="{ORANGE if hot else SILVER}"/>')
        body += text(954, y + 58, f"× {amp:.2f}", 30,
                     ORANGE if hot else INK, MONO, 600, "end")
        y += 100

    body += text(86, 1064, "At ᾱ = 0.02 a 0.20 error arrives as 1.40 — wider than the pixel range.",
                 21, MUTED, SANS, 400)
    body += footer("feed", ["Small steps keep the multiplier near 1,",
                            "and each step re-reads a cleaner image."])
    return document("feed", "Why it takes many small steps",
                    "Four rows of the error multiplier against the signal coefficient, with bars "
                    "to scale: 0.20 at high signal rising to 7.00 at near-pure noise.", body)


def feed_05():
    body = header("feed", 5, 7, ["The schedule is configuration."],
                  ["Not a layer. It decides which noise levels the network ever practises."])
    import math
    T, N = 1000, 160
    betas = [1e-4 + (0.02 - 1e-4) * i / (T - 1) for i in range(T)]
    ab, acc = [], 1.0
    for b in betas:
        acc *= (1 - b)
        ab.append(acc)
    lin = [ab[min(T - 1, int(u / N * T))] ** 0.5 for u in range(N + 1)]
    f = lambda z: math.cos((z + 0.008) / 1.008 * math.pi / 2) ** 2
    cos = [(f(u / N) / f(0.0)) ** 0.5 for u in range(N + 1)]

    px, py, pw, ph = 150, 470, 820, 360
    body += line(px, py + ph, px + pw, py + ph, SILVER, 2)
    body += line(px, py, px, py + ph, SILVER, 2)
    for frac in (0.25, 0.5, 0.75, 1.0):
        yy = py + ph - frac * ph
        body += line(px, yy, px + pw, yy, RULE, 1)
        body += text(px - 16, yy + 6, f"{frac:.2f}", 14, MUTED, MONO, 400, "end")
    body += polyline([(px + i / N * pw, py + ph - cos[i] * ph) for i in range(N + 1)],
                     BLUE, 5, dash="14,10")
    body += polyline([(px + i / N * pw, py + ph - lin[i] * ph) for i in range(N + 1)], INK, 5)
    body += text(px + 0.60 * pw, py + ph - cos[int(0.60 * N)] * ph - 20, "cosine", 18, BLUE, MONO, 500, "middle")
    body += text(px + 0.60 * pw, py + ph - lin[int(0.60 * N)] * ph + 36, "linear", 18, INK, MONO, 500, "middle")
    body += text(px, py + ph + 34, "t / T = 0", 14, MUTED, MONO, 400)
    body += text(px + pw, py + ph + 34, "1", 14, MUTED, MONO, 400, "end")
    body += text(px - 74, py + ph / 2, "√ᾱₜ", 20, MUTED, MONO, 500, "middle")

    lq, cq = lin[int(0.75 * N)], cos[int(0.75 * N)]
    body += rect(86, 892, 440, 168, WHITE, ORANGE)
    body += text(120, 952, "linear", 20, INK, MONO, 500)
    body += text(120, 1010, f"√ᾱ = {lq:.3f}", 40, ORANGE, MONO, 600)
    body += text(492, 952, "at t/T = 0.75", 16, MUTED, MONO, 400, "end")
    body += rect(554, 892, 440, 168, WHITE, RULE)
    body += text(588, 952, "cosine", 20, BLUE, MONO, 500)
    body += text(588, 1010, f"√ᾱ = {cq:.3f}", 40, BLUE, MONO, 600)
    body += text(960, 952, "at t/T = 0.75", 16, MUTED, MONO, 400, "end")

    body += footer("feed", ["The linear schedule spends its last quarter",
                            "shuffling what is already noise."])
    return document("feed", "The schedule is configuration",
                    "Signal coefficient against normalised timestep for the linear and cosine "
                    "schedules, with the surviving signal at three-quarters of the way through.", body)


def feed_06():
    body = header("feed", 6, 7, ["Where the new image comes from."],
                  ["The seed — with a measured exception worth stating precisely."])
    body += stat(86, 452, 908, "94", "training images extracted from Stable Diffusion",
                 ["from 175,000,000 generations: 500 images for each of the 350,000",
                  "MOST-DUPLICATED training captions, then filtered  ·  Carlini et al., USENIX Security 2023"],
                 accent=True, vsize=76)
    body += stat(86, 672, 440, "1.88%", "of 9,000 random-caption generations",
                 ["matched a training image at SSCD ≥ 0.5, against an index",
                  "covering under 0.6% of the data · Somepalli, CVPR 2023"])
    body += stat(554, 672, 440, "34.1×", "mean duplication of the matches",
                 ["duplication in the training set is what predicts",
                  "replication — not model size  ·  same paper"])
    body += rect(86, 892, 908, 168, WHITE, RULE)
    body += text(120, 948, "Two networks trained on non-overlapping halves of a dataset",
                 22, INK, SANS, 500)
    body += text(120, 984, "converge on the same denoiser and, from the same seed, produce",
                 22, INK, SANS, 500)
    body += text(120, 1020, "the same image — one in neither training set.", 22, INK, SANS, 500)
    body += text(954, 1020, "Kadkhodaie et al., ICLR 2024", 15, MUTED, MONO, 400, "end")
    body += footer("feed", ["Novel by default. Recalled when the data",
                            "showed it the same picture over and over."])
    return document("feed", "Where the new image comes from",
                    "Three measured statistics on diffusion memorisation with their exact "
                    "experimental conditions, above the disjoint-training-set result.", body)


def feed_07():
    body = header("feed", 7, 7, ["The four moving parts."],
                  ["Only one of them was trained. Read part 1 of the series."])
    rows = [("①", "THE SCHEDULE", "fixed β₁ … β_T", "configuration", False),
            ("②", "THE TRAINING LOOP", "corrupt, predict, update", "runs once, offline", False),
            ("③", "THE DENOISER", "εθ(xₜ, t)", "the only trained part", True),
            ("④", "THE SAMPLER", "xₜ₋₁ from xₜ and ε̂", "arithmetic, no parameters", False)]
    y = 452
    for mark, name, detail, note, active in rows:
        body += rect(86, y, 908, 124, "rgba(235,108,54,.08)" if active else WHITE,
                     ORANGE if active else RULE)
        body += text(128, y + 76, mark, 40, ORANGE if active else SILVER, SANS, 400)
        body += text(196, y + 58, name, 24, ORANGE if active else INK, MONO, 600, spacing=".05em")
        body += text(196, y + 94, detail, 21, BLUE, MONO, 400)
        body += text(954, y + 78, note, 18, MUTED, SANS, 400, "end")
        y += 136

    body += rect(86, 1004, 908, 118, "rgba(235,108,54,.06)", ORANGE)
    body += text(540, 1052, "canery.in/blogs/", 22, MUTED, MONO, 400, "middle")
    body += text(540, 1094, "what-a-diffusion-model-actually-does", 26, ORANGE, MONO, 600, "middle")
    body += footer("feed", ["Swap the schedule, the sampler or the seed",
                            "and the same checkpoint still works."])
    return document("feed", "The four moving parts",
                    "The four components of a diffusion system with the denoiser highlighted as "
                    "the only trained one, above the article link.", body)


# ------------------------------------------------------------------ story

def story_01():
    body = header("story", 1, 4, ["Trained only", "to undo noise."],
                  ["So where does a new image come from?"])
    motif = crescent(12)
    for i, abar in enumerate([0.012, 0.16, 0.48, 0.97]):
        x = 150 + (i % 2) * 420
        y = 700 + (i // 2) * 400
        body += noise_tiles(x, y, 12, 12, 26, abar, motif, seed=5200 + i * 173, gap=3, rx=3)
        if i == 3:
            body += (f'<rect x="{x - 9}" y="{y - 9}" width="366" height="366" rx="10" '
                     f'fill="none" stroke="{ORANGE}" stroke-width="4"/>')
        body += text(x + 174, y + 372, f"ᾱ = {abar:.3f}", 20, MUTED, MONO, 400, "middle")
    body += footer("story", ["The forward corruption is a formula.",
                             "The network exists only because",
                             "it cannot be run backwards."])
    return document("story", "Trained only to undo noise",
                    "A crescent emerging from pure noise across four panels of rising signal.", body)


def story_02():
    body = header("story", 2, 4, ["The answer key", "is free."],
                  ["We draw the noise ourselves, so nothing needs labelling."])
    body += vmatrix(150, 760, SIG, cell=90, gap=8, hot=1, size=22)
    body += text(150 + 192, 1180, "0.8 · x₀", 26, INK, MONO, 600, "middle")
    body += vmatrix(546, 760, NOI, cell=90, gap=8, hot=1, size=22)
    body += text(546 + 192, 1180, "0.6 · ε", 26, INK, MONO, 600, "middle")
    body += text(516, 950, "+", 48, MUTED, MONO, 400, "middle")
    body += rect(150, 1230, 780, 210, WHITE, ORANGE)
    body += text(190, 1300, "0.48 + 0.84 = 1.32", 44, ORANGE, MONO, 600)
    body += text(190, 1360, "one cell of xₜ, the tensor the network sees.", 24, INK, SANS, 400)
    body += text(190, 1404, "The target is the ε we already hold.", 24, MUTED, SANS, 400)
    body += footer("story", ["A fresh training pair from any image,",
                             "at any noise level, forever."])
    return document("story", "The answer key is free",
                    "Two four-by-four grids of printed values adding to one cell of the noisy "
                    "tensor, with the free training target named.", body)


def story_03():
    body = header("story", 3, 4, ["Why not just", "take one step?"],
                  ["Because the error multiplier is worst exactly where you would jump."])
    body += rect(150, 740, 780, 150, WHITE, RULE)
    body += text(540, 800, "error δ in the predicted noise", 24, MUTED, SANS, 400, "middle")
    body += text(540, 856, "→  √(1−ᾱ)/√ᾱ × δ  in the image",
                 30, INK, MONO, 600, "middle")
    rows = [(0.96, 0.20), (0.64, 0.75), (0.25, 1.73), (0.02, 7.00)]
    y = 930
    for abar, amp in rows:
        hot = abar == 0.02
        body += rect(150, y, 780, 108, "rgba(235,108,54,.06)" if hot else WHITE,
                     ORANGE if hot else RULE)
        body += text(190, y + 68, f"ᾱ = {abar:.2f}", 30, ORANGE if hot else INK, MONO, 500)
        bar = 400 * (amp / 7.0)
        body += (f'<rect x="420" y="{y + 40}" width="{bar:.0f}" height="28" rx="7" '
                 f'fill="{ORANGE if hot else SILVER}"/>')
        body += text(890, y + 68, f"× {amp:.2f}", 34, ORANGE if hot else INK, MONO, 600, "end")
        y += 120
    body += text(150, 1470, "A 0.20 error becomes 1.40 — wider than the whole pixel range.",
                 24, MUTED, SANS, 400)
    body += footer("story", ["Many small steps keep the multiplier",
                             "near 1, and each one re-reads",
                             "a cleaner image than the last."])
    return document("story", "Why not just take one step",
                    "The error multiplier at four signal levels, drawn as bars to scale, rising "
                    "from 0.20 to 7.00.", body)


def story_04():
    body = header("story", 4, 4, ["What a diffusion", "model actually does."],
                  ["Part 1 of the Diffusion Models series, on Canery."])
    rows = [("①", "THE SCHEDULE", "configuration"),
            ("②", "THE TRAINING LOOP", "runs once, offline"),
            ("③", "THE DENOISER", "the only trained part"),
            ("④", "THE SAMPLER", "arithmetic, no parameters")]
    y = 760
    for i, (mark, name, note) in enumerate(rows):
        active = i == 2
        body += rect(150, y, 780, 130, "rgba(235,108,54,.08)" if active else WHITE,
                     ORANGE if active else RULE)
        body += text(196, y + 82, mark, 44, ORANGE if active else SILVER, SANS, 400)
        body += text(272, y + 62, name, 27, ORANGE if active else INK, MONO, 600, spacing=".05em")
        body += text(272, y + 100, note, 21, MUTED, SANS, 400)
        y += 142
    body += rect(150, 1338, 780, 120, "rgba(235,108,54,.06)", ORANGE)
    body += text(540, 1390, "read the article", 22, MUTED, MONO, 400, "middle", spacing=".14em")
    body += text(540, 1432, "canery.in", 32, ORANGE, MONO, 600, "middle")
    body += footer("story", ["Link in the sticker above —",
                             "the full worked example is in the post."])
    return document("story", "Read the article",
                    "The four parts of a diffusion system with the denoiser highlighted, above "
                    "the call to read the article on Canery.", body)


ASSETS = {
    "feed-01-trained-only-to-undo-noise": feed_01,
    "feed-02-the-answer-key-is-free": feed_02,
    "feed-03-one-call-returns-an-average": feed_03,
    "feed-04-the-error-multiplier": feed_04,
    "feed-05-the-schedule-is-configuration": feed_05,
    "feed-06-where-the-new-image-comes-from": feed_06,
    "feed-07-the-four-moving-parts": feed_07,
    "story-01-trained-only-to-undo-noise": story_01,
    "story-02-the-answer-key-is-free": story_02,
    "story-03-why-not-one-step": story_03,
    "story-04-read-the-article": story_04,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for stem, builder in ASSETS.items():
        (OUT / f"{stem}.html").write_text(builder(), encoding="utf-8")
        print(f"built {stem}")


if __name__ == "__main__":
    main()
