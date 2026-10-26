#!/usr/bin/env python3
"""Shared diagram-design renderer for "Evaluating Generative Models: What FID Measures and Hides"."""

from __future__ import annotations

import html
import pathlib
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent

PAPER = "#f5f5f5"
PAPER2 = "#ececec"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.12)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
LINK = "#2e5aa8"
SAGE = "#7c8f6f"
BLUE = "#5e7a9b"
MUSTARD = "#b8915a"

FONTS = (
    "https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
    "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap"
)
SANS = "'Geist',system-ui,sans-serif"
MONO = "'Geist Mono',ui-monospace,monospace"
SERIF = "'Instrument Serif',Georgia,serif"

DEFS = f"""<defs>
<style>@import url('{FONTS}');</style>
<marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{MUTED}"/></marker>
<marker id="arrow-a" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{ACCENT}"/></marker>
<marker id="arrow-l" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto"><polygon points="0 0,8 3,0 6" fill="{LINK}"/></marker>
</defs>"""


def esc(value: object) -> str:
    return html.escape(str(value))


def text(x, y, value, size=12, fill=INK, family=SANS, weight=400,
         anchor="middle", track=None, italic=False):
    attrs = (
        f'x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
        f'font-family="{family}" font-weight="{weight}" text-anchor="{anchor}"'
    )
    if track:
        attrs += f' letter-spacing="{track}"'
    if italic:
        attrs += ' font-style="italic"'
    return f"<text {attrs}>{esc(value)}</text>"


def mono(x, y, value, size=8, fill=MUTED, anchor="middle", weight=400):
    return text(x, y, value, size, fill, MONO, weight, anchor, "0.06em")


def subtext(x, y, base, sub="", size=12, fill=INK, family=SANS, weight=600,
            anchor="middle"):
    """Base glyph with a real typographic subscript.

    Unicode has no subscript for capitals, so every state label is drawn with a
    tspan instead. That keeps x_0, x_t and x_T rendering the same way.
    """
    inner = esc(base)
    if sub:
        inner += (f'<tspan font-size="{round(size * 0.66, 2)}" '
                  f'dy="{round(size * 0.22, 2)}">{esc(sub)}</tspan>')
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" '
            f'font-family="{family}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{inner}</text>')


def ascii_upper(value) -> str:
    """Uppercase ASCII letters only, so Greek (σ, λ, ε) and µ survive a label."""
    return "".join(c.upper() if "a" <= c <= "z" else c for c in str(value))


def eyebrow(x, y, value, fill=SOFT, anchor="start"):
    return text(x, y, ascii_upper(value), 8, fill, MONO, 500, anchor, "0.18em")


def rect(x, y, w, h, fill="#ffffff", stroke=INK, rx=6, sw=1, dash=None):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{extra}/>'
    )


def node(x, y, w, h, title, sub="", kind="normal", badge=None):
    styles = {
        "normal": ("#ffffff", INK),
        "focal": (ACCENT_TINT, ACCENT),
        "soft": ("rgba(45,49,66,0.05)", MUTED),
        "input": ("rgba(79,93,117,0.10)", SOFT),
        "link": ("rgba(46,90,168,0.06)", LINK),
    }
    fill, stroke = styles[kind]
    out = rect(x, y, w, h, PAPER, "none") + rect(x, y, w, h, fill, stroke)
    if badge:
        bw = max(32, 8 * len(badge) + 12)
        out += rect(x + 8, y + 8, bw, 16, "transparent", stroke, 2, 0.8)
        out += mono(x + 8 + bw / 2, y + 20, ascii_upper(badge), 8, stroke, weight=500)
    cy = y + h / 2 + (8 if badge else 0)
    ink = ACCENT if kind == "focal" else INK
    if isinstance(title, tuple):
        out += subtext(x + w / 2, cy, title[0], title[1], 13, ink)
    else:
        out += text(x + w / 2, cy, title, 12, ink, SANS, 600)
    if sub:
        out += mono(x + w / 2, cy + 20, sub, 8, SOFT)
    return out


def h_arrow(x1, y, x2, colour=MUTED, accent=False, dashed=False, width=1.2):
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    marker = "arrow-a" if accent else ("arrow-l" if colour == LINK else "arrow")
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{colour}" '
            f'stroke-width="{width}" marker-end="url(#{marker})"{dash}/>' )


def v_arrow(x, y1, y2, colour=MUTED, accent=False, dashed=False, width=1.2):
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    marker = "arrow-a" if accent else ("arrow-l" if colour == LINK else "arrow")
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{colour}" '
            f'stroke-width="{width}" marker-end="url(#{marker})"{dash}/>' )


def elbow(x1, y1, x2, y2, colour=MUTED, accent=False, dashed=False):
    """Orthogonal horizontal-then-vertical connector with an 8px bend."""
    sx = 1 if x2 >= x1 else -1
    sy = 1 if y2 >= y1 else -1
    r = 8
    path = f"M{x1},{y1} H{x2-sx*r} Q{x2},{y1} {x2},{y1+sy*r} V{y2}"
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    marker = "arrow-a" if accent else ("arrow-l" if colour == LINK else "arrow")
    return (f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="1.2" '
            f'marker-end="url(#{marker})"{dash}/>' )


def zconn(x1, y1, x2, y2, colour=MUTED, accent=False, dashed=False, mx=None):
    """Horizontal out, vertical across, horizontal in.

    `elbow` turns the other way round, so it always arrives travelling
    vertically and stabs a left or right edge side-on. Use this whenever the
    target is beside the source: the arrowhead then enters the edge head-on,
    which is the only way the connection reads as a connection.

    `mx` moves the vertical leg off the midpoint, which is how you buy a long
    enough horizontal run to label the branch without touching either box.
    """
    if abs(y2 - y1) < 1:
        return h_arrow(x1, y1, x2, colour, accent, dashed)
    mx = (x1 + x2) / 2 if mx is None else mx
    sx = 1 if x2 >= x1 else -1
    sy = 1 if y2 >= y1 else -1
    r = 8
    path = (f"M{x1},{y1} H{mx - sx * r} Q{mx},{y1} {mx},{y1 + sy * r} "
            f"V{y2 - sy * r} Q{mx},{y2} {mx + sx * r},{y2} H{x2}")
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    marker = "arrow-a" if accent else ("arrow-l" if colour == LINK else "arrow")
    return (f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="1.2" '
            f'marker-end="url(#{marker})"{dash}/>')


def label(x, arrow_y, value, fill=SOFT, width=None, dy=-28):
    """Arrow label on an opaque plate.

    `width` is the plate, not the text. Pass the free gap between two nodes so
    the plate can never paint over a node border.
    """
    width = width or max(48, len(value) * 7 + 20)
    return (rect(x - width / 2, arrow_y + dy, width, 16, PAPER, "none", 2)
            + mono(x, arrow_y + dy + 12, ascii_upper(value), 8, fill))


def legend(y, vw, items):
    out = f'<line x1="32" y1="{y-12}" x2="{vw-32}" y2="{y-12}" stroke="{RULE}" stroke-width="0.8"/>'
    out += eyebrow(32, y + 4, "legend")
    x = 120
    for name, colour in items:
        out += rect(x, y - 8, 12, 12, f"{colour}22", colour, 2, 0.8)
        out += mono(x + 20, y + 2, name, 8, MUTED, "start")
        x += 64 + len(name) * 7
    return out


def lcg(seed):
    """Deterministic noise so every rebuild reproduces the same figure."""
    state = seed
    while True:
        state = (1103515245 * state + 12345) % 2147483648
        yield state / 2147483648


def shade(t, dark=INK):
    """Map 0..1 to an ink opacity that stays legible on PAPER."""
    return f'{dark}" fill-opacity="{min(0.92, max(0.05, t)):.2f}'


def grid(x, y, cols, rows, cell, values, gap=2, rx=1, accent=None, stroke=None):
    """A feature map drawn as a feature map: one cell per element, shaded by value.

    `values` is a flat list of 0..1, row-major. This is the primitive that turns
    "a 64x64 latent" from a phrase inside a box into something the eye can size.
    """
    out = ""
    for r in range(rows):
        for c in range(cols):
            v = values[r * cols + c] if values else 0.5
            hot = accent is not None and accent == (r, c)
            fill = ACCENT if hot else shade(v)
            op = "" if hot else ""
            out += (f'<rect x="{x + c * (cell + gap):.1f}" y="{y + r * (cell + gap):.1f}" '
                    f'width="{cell}" height="{cell}" rx="{rx}" fill="{fill}{op}"/>')
    if stroke:
        w = cols * cell + (cols - 1) * gap
        h = rows * cell + (rows - 1) * gap
        out += rect(x - 3, y - 3, w + 6, h + 6, "none", stroke, 3, 1)
    return out


def noise_grid(x, y, cols, rows, cell, signal, target=None, seed=7, gap=2,
               accent=None, stroke=None):
    """A grid at a chosen signal level: sqrt(abar)*target + sqrt(1-abar)*noise."""
    rng = lcg(seed)
    n = [next(rng) for _ in range(cols * rows)]
    sig, noi = signal ** 0.5, (1 - signal) ** 0.5
    vals = [sig * (target[i] if target else 0.5) + noi * n[i] for i in range(cols * rows)]
    return grid(x, y, cols, rows, cell, vals, gap, 1, accent, stroke)


def token_row(x, y, count, cell, gap=3, fill=None, accent=None, stroke=None):
    """A token sequence drawn as a strip, so sequence length is a visible length."""
    out = ""
    for i in range(count):
        hot = accent == i
        out += rect(x + i * (cell + gap), y, cell, cell,
                    ACCENT_TINT if hot else (fill or "#ffffff"),
                    ACCENT if hot else (stroke or RULE_SOLID), 2, 0.9)
    return out


def plot_axes(x, y, w, h, xlabel="", ylabel="", ticks=()):
    """Bare axes for a real curve. Math figures get plotted, not described."""
    out = (f'<line x1="{x}" y1="{y + h}" x2="{x + w + 10}" y2="{y + h}" '
           f'stroke="{RULE_SOLID}" stroke-width="1"/>'
           f'<line x1="{x}" y1="{y + h}" x2="{x}" y2="{y - 10}" '
           f'stroke="{RULE_SOLID}" stroke-width="1"/>')
    if xlabel:
        out += mono(x + w / 2, y + h + 26, xlabel, 8, SOFT)
    if ylabel:
        out += f'<g transform="rotate(-90 {x - 34} {y + h / 2})">' + mono(x - 34, y + h / 2, ylabel, 8, SOFT) + '</g>'
    for tx, label in ticks:
        px = x + tx * w
        out += f'<line x1="{px}" y1="{y + h}" x2="{px}" y2="{y + h + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        out += mono(px, y + h + 16, label, 7, SOFT)
    return out


def curve(x, y, w, h, fn, colour=INK, width=1.6, dash=None, samples=120):
    """Plot fn(u) for u in [0,1], fn returning 0..1 measured from the axis."""
    pts = []
    for i in range(samples + 1):
        u = i / samples
        pts.append(f"{x + u * w:.1f},{y + h - fn(u) * h:.1f}")
    d = ' stroke-dasharray="5,4"' if dash else ""
    return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}" stroke-linecap="round"{d}/>')


def wiggle(x1, y1, x2, y2, amp, seed, colour=MUTED, width=1.2, steps=26):
    """A stochastic trajectory. Draws the randomness instead of labelling it."""
    rng = lcg(seed)
    pts, drift = [], 0.0
    for i in range(steps + 1):
        u = i / steps
        drift += (next(rng) - 0.5) * amp
        drift *= 0.82
        pts.append(f"{x1 + u * (x2 - x1):.1f},{y1 + u * (y2 - y1) + drift:.1f}")
    return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}" stroke-linejoin="round" opacity="0.85"/>')


def svg_doc(vw, vh, body, aria):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" '
        f'width="{vw}" height="{vh}" role="img" aria-label="{esc(aria)}">'
        f'{DEFS}<rect width="100%" height="100%" fill="{PAPER}"/>{body}</svg>'
    )


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{title}</title><link href="{fonts}" rel="stylesheet"><style>
*{{box-sizing:border-box}}body{{margin:0;padding:40px;background:{paper};color:{ink};font-family:{sans}}}
.k{{font-family:{mono};font-size:8px;letter-spacing:.18em;text-transform:uppercase;color:{soft};margin:0 0 8px}}
h1{{font-family:{serif};font-size:28px;font-weight:400;margin:0 0 4px}}p{{color:{muted};margin:0 0 24px}}svg{{display:block;max-width:100%;height:auto}}
footer{{border-top:1px solid {rule};margin-top:24px;padding-top:12px;color:{soft};font:9px {mono}}}
</style></head><body><p class="k">{eyebrow}</p><h1>{title}</h1><p>{sub}</p>{svg}
<footer>evaluating-generative-models · original editorial diagram</footer></body></html>"""


def rasterize(svg, out, vw, vh, scale=2):
    shim = (
        '<!doctype html><meta charset="utf-8">'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>html,body{{margin:0;width:{vw}px;height:{vh}px;overflow:hidden;background:{PAPER}}}svg{{display:block}}</style>{svg}'
    )
    with tempfile.TemporaryDirectory(prefix="diffusion-p9-fig-") as temp:
        root = pathlib.Path(temp)
        source = root / "render.html"
        source.write_text(shim, encoding="utf-8")
        command = [
            "google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--virtual-time-budget=15000",
            f"--user-data-dir={root / 'profile'}", f"--force-device-scale-factor={scale}",
            f"--window-size={vw},{vh}", f"--screenshot={out.resolve()}", f"file://{source}",
        ]
        subprocess.run(command, check=True, capture_output=True, timeout=120)


def emit(number, slug, title, sub, body, aria, vw=960, vh=540):
    stem = f"fig-{number:02d}-{slug}"
    svg = svg_doc(vw, vh, body, aria)
    page = PAGE.format(title=title, sub=sub, eyebrow=f"Figure {number:02d}", svg=svg,
                       fonts=FONTS, paper=PAPER, ink=INK, muted=MUTED, soft=SOFT,
                       rule=RULE, sans=SANS, mono=MONO, serif=SERIF)
    (HERE / f"{stem}.html").write_text(page, encoding="utf-8")
    (HERE / f"{stem}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    rasterize(svg, HERE / f"{stem}.png", vw, vh)
    print(f"rendered {stem}")


def emit_cover(body, aria):
    vw, vh = 1200, 630
    svg = svg_doc(vw, vh, body, aria)
    page = PAGE.format(title="Evaluating Generative Models", sub="what FID measures, and what one number hides",
                       eyebrow="Machine learning", svg=svg, fonts=FONTS, paper=PAPER,
                       ink=INK, muted=MUTED, soft=SOFT, rule=RULE, sans=SANS, mono=MONO,
                       serif=SERIF)
    (HERE / "cover.html").write_text(page, encoding="utf-8")
    (HERE / "cover.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    rasterize(svg, HERE / "cover.png", vw, vh, scale=1)
    print("rendered cover")
