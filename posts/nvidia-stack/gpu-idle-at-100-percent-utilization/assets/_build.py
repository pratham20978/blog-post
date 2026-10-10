#!/usr/bin/env python3
"""Figure toolchain for the gpu-idle-at-100-percent-utilization post (nvidia-stack part 3).

Writes, for each figure: a self-contained diagram-design HTML page, a standalone
.svg, and a 2x .png rasterised with headless Chrome (Playwright is not installed
and diagram-design/references/export.md says not to auto-install it).

Run:  python3 _build.py            # all figures
      python3 _build.py 01 05      # only those
"""

import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------- design tokens
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

FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")

SANS = "'Geist', system-ui, sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"
SERIF = "'Instrument Serif', Georgia, serif"

DEFS = f"""  <defs>
    <style>/*<![CDATA[*/@import url('{FONTS}');/*]]>*/</style>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="{MUTED}"/>
    </marker>
    <marker id="arrow-accent" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="{ACCENT}"/>
    </marker>
    <marker id="arrow-link" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
      <polygon points="0 0, 8 3, 0 6" fill="{LINK}"/>
    </marker>
  </defs>"""


# ---------------------------------------------------------------- primitives
def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def txt(x, y, s, size=12, fill=INK, family=SANS, weight="400", anchor="middle",
        track=None, style=None):
    a = (f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
         f'font-family="{family}" text-anchor="{anchor}"')
    if track:
        a += f' letter-spacing="{track}"'
    if style:
        a += f' font-style="{style}"'
    return a + f">{esc(s)}</text>"


def ascii_upper(s):
    """Uppercase ASCII only: .upper() turns the micro sign in "µs" into a capital mu."""
    return "".join(c.upper() if c.isascii() else c for c in str(s))


def eyebrow(x, y, s, fill=SOFT, anchor="start", size=8):
    return txt(x, y, ascii_upper(s), size=size, fill=fill, family=MONO,
               weight="500", anchor=anchor, track="0.18em")


def mono(x, y, s, size=9, fill=MUTED, anchor="middle", weight="400", track=None):
    return txt(x, y, s, size=size, fill=fill, family=MONO, weight=weight,
               anchor=anchor, track=track)


def box(x, y, w, h, fill="#ffffff", stroke=INK, rx=6, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{PAPER}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{d}/>')


def tag(x, y, s, stroke=INK, w=None):
    w = w or max(28, 7 * len(s) + 10)
    return (f'<rect x="{x}" y="{y}" width="{w}" height="12" rx="2" fill="transparent" '
            f'stroke="{stroke}" stroke-opacity="0.40" stroke-width="0.8"/>'
            + txt(x + w / 2, y + 9, s.upper(), size=7, fill=stroke, family=MONO,
                  weight="500", anchor="middle", track="0.08em"))


def node(x, y, w, h, name, sub=None, kind="backend", tagtext=None):
    fills = {
        "backend": ("#ffffff", INK),
        "focal": (ACCENT_TINT, ACCENT),
        "store": ("rgba(45,49,66,0.05)", MUTED),
        "external": ("rgba(45,49,66,0.03)", "rgba(45,49,66,0.30)"),
        "input": ("rgba(79,93,117,0.10)", SOFT),
    }
    fill, stroke = fills[kind]
    s = box(x, y, w, h, fill=fill, stroke=stroke)
    cy = y + h / 2
    if tagtext:
        s += tag(x + 8, y + 6, tagtext, stroke=stroke)
        cy = y + h / 2 + 8
    s += txt(x + w / 2, cy + 2, name, size=12, weight="600",
             fill=ACCENT if kind == "focal" else INK)
    if sub:
        s += mono(x + w / 2, cy + 16, sub, size=9, fill=SOFT)
    return s


def hline(x1, x2, y, stroke=MUTED, sw=1, marker="arrow", dash=None):
    m = f' marker-end="url(#{marker})"' if marker else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{m}/>')


def vline(x, y1, y2, stroke=MUTED, sw=1, marker="arrow", dash=None):
    m = f' marker-end="url(#{marker})"' if marker else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{m}/>')


def elbow(x1, y1, x2, y2, r=8, stroke=MUTED, sw=1, marker="arrow", dash=None):
    """Orthogonal path: horizontal then vertical, with a rounded corner."""
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    d = (f"M {x1} {y1} H {x2 - sx * r} Q {x2} {y1} {x2} {y1 + sy * r} V {y2}")
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>')


def elbow_hvh(x1, y1, xt, y2, x2, r=8, stroke=MUTED, sw=1, marker="arrow", dash=None):
    """Right, then vertical at xt, then right again — ends horizontally at (x2, y2).

    Give each connector on a shared edge its own `xt` so no two verticals overlap.
    """
    sy = 1 if y2 > y1 else -1
    if abs(y2 - y1) < 2 * r:
        d = f"M {x1} {y1} H {x2}"
    else:
        d = (f"M {x1} {y1} H {xt - r} Q {xt} {y1} {xt} {y1 + sy * r} "
             f"V {y2 - sy * r} Q {xt} {y2} {xt + r} {y2} H {x2}")
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>'


def masked(x, y, s, size=8, fill=MUTED, family=MONO, anchor="middle", pad=8, track="0.04em"):
    """Text on an opaque plate — for labels that sit over curves or fills."""
    w = 0.62 * size * len(str(s)) + 2 * pad
    x0 = {"middle": x - w / 2, "start": x - pad, "end": x - w + pad}[anchor]
    return (f'<rect x="{x0}" y="{y - size - 3}" width="{w}" height="{size + 8}" rx="2" '
            f'fill="{PAPER}"/>'
            + txt(x, y, s, size=size, fill=fill, family=family, anchor=anchor, track=track))


def alabel(x, y, s, fill=SOFT, gap=20, w=None):
    """Arrow label with an opaque mask, sitting `gap` px above the stroke at y."""
    w = w or max(28, 6 * len(s) + 12)
    return (f'<rect x="{x - w / 2}" y="{y - gap}" width="{w}" height="12" rx="2" fill="{PAPER}"/>'
            + mono(x, y - gap + 9, ascii_upper(s), size=8, fill=fill, track="0.06em"))


def diamond(cx, cy, w, h, name, sub=None, stroke=INK, fill="#ffffff"):
    """Decision node. `w`/`h` are the full diagonals."""
    pts = f"{cx} {cy - h / 2}, {cx + w / 2} {cy}, {cx} {cy + h / 2}, {cx - w / 2} {cy}"
    s = (f'<polygon points="{pts}" fill="{PAPER}"/>'
         f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="1" '
         f'stroke-linejoin="round"/>')
    if sub:
        s += txt(cx, cy - 2, name, size=12, weight="600", fill=INK)
        s += mono(cx, cy + 12, sub, size=8, fill=SOFT)
    else:
        s += txt(cx, cy + 4, name, size=12, weight="600", fill=INK)
    return s


def oval(x, y, w, h, name, sub=None, stroke=INK, fill="#ffffff", tcolor=None):
    """Terminal node — start / end."""
    s = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{PAPER}"/>'
         f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" fill="{fill}" '
         f'stroke="{stroke}" stroke-width="1"/>')
    cy = y + h / 2
    if sub:
        s += txt(x + w / 2, cy - 2, name, size=12, weight="600", fill=tcolor or INK)
        s += mono(x + w / 2, cy + 12, sub, size=8, fill=SOFT)
    else:
        s += txt(x + w / 2, cy + 4, name, size=12, weight="600", fill=tcolor or INK)
    return s


def vbracket(x, y1, y2, label, colour=MUTED, side="right", arm=8):
    """Vertical bracket beside a span, label centred on it (label sits outside the arm)."""
    d = 1 if side == "right" else -1
    s = (f'<path d="M {x - d * arm} {y1} H {x} V {y2} H {x - d * arm}" fill="none" '
         f'stroke="{colour}" stroke-width="1"/>')
    s += mono(x + d * 12, (y1 + y2) / 2 + 3, label, size=8, fill=colour,
              anchor="start" if side == "right" else "end", track="0.10em")
    return s


def hbracket(x1, x2, y, label, colour=MUTED, below=True, arm=8, gap=16):
    """Horizontal bracket under (or over) a span."""
    d = 1 if below else -1
    s = (f'<path d="M {x1} {y - d * arm} V {y} H {x2} V {y - d * arm}" fill="none" '
         f'stroke="{colour}" stroke-width="1"/>')
    s += mono((x1 + x2) / 2, y + d * gap + (3 if below else 0), label, size=8,
              fill=colour, track="0.10em")
    return s


def callout(tx, ty, text, lx, ly, colour=INK, anchor="end", leader=None, cx=None, cy=None):
    """Italic-serif editorial aside with a dashed Bezier leader and a landing dot.

    (tx, ty) text position, (lx, ly) landing point; `leader` overrides the path start.
    """
    lc = {INK: "rgba(45,49,66,0.40)", ACCENT: "rgba(235,108,54,0.50)",
          MUTED: "rgba(45,49,66,0.30)"}.get(colour, "rgba(45,49,66,0.40)")
    sx, sy = leader or (tx - (8 if anchor == "end" else -8), ty + 6)
    cx = cx if cx is not None else (sx + lx) / 2
    cy = cy if cy is not None else (sy + ly) / 2 + 24
    s = txt(tx, ty, text, size=14, fill=colour, family=SERIF, anchor=anchor, style="italic")
    s += (f'<path d="M {sx} {sy} Q {cx} {cy} {lx} {ly}" fill="none" stroke="{lc}" '
          f'stroke-width="1" stroke-dasharray="4,3"/>')
    s += f'<circle cx="{lx}" cy="{ly}" r="2" fill="{colour}"/>'
    return s


def vhv(x1, y1, x2, y2, ym, r=8, stroke=MUTED, sw=1, marker="arrow", dash=None):
    """Down (or up) to ym, across to x2, then on to y2 — ends vertically at (x2, y2)."""
    sy = 1 if y2 > y1 else -1
    sx = 1 if x2 > x1 else -1
    if abs(x2 - x1) < 2 * r:
        d = f"M {x1} {y1} V {y2}"
    else:
        d = (f"M {x1} {y1} V {ym - sy * r} Q {x1} {ym} {x1 + sx * r} {ym} "
             f"H {x2 - sx * r} Q {x2} {ym} {x2} {ym + sy * r} V {y2}")
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>'


def elbow_vh(x1, y1, x2, y2, r=8, stroke=MUTED, sw=1, marker="arrow", dash=None):
    """Orthogonal path: vertical then horizontal, rounded corner — ends horizontally."""
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    d = f"M {x1} {y1} V {y2 - sy * r} Q {x1} {y2} {x1 + sx * r} {y2} H {x2}"
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>'


def mark(x, y, ok, colour=None, size=10):
    """Pass / fail glyph: a tick or a cross, drawn as strokes so it renders everywhere."""
    if ok:
        c = colour or MUTED
        return (f'<path d="M {x - size / 2} {y} L {x - size / 8} {y + size / 2 - 1} '
                f'L {x + size / 2} {y - size / 2 + 1}" fill="none" stroke="{c}" '
                f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>')
    c = colour or ACCENT
    h = size / 2 - 1
    return (f'<path d="M {x - h} {y - h} L {x + h} {y + h} M {x + h} {y - h} L {x - h} {y + h}" '
            f'stroke="{c}" stroke-width="1.6" stroke-linecap="round"/>')


def chip(x, y, s, colour=MUTED, fill=None, size=8, pad=8, h=16):
    """Small rounded mono chip, left-anchored at x. Returns (svg, width)."""
    w = round(0.62 * size * len(s) + 2 * pad)
    svg = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" '
           f'fill="{fill or PAPER}" stroke="{colour}" stroke-opacity="0.45" stroke-width="0.8"/>'
           + mono(x + w / 2, y + h / 2 + 3, s, size=size, fill=colour, track="0.04em"))
    return svg, w


def cell(x, y, w, h, value, fill="#ffffff", stroke="rgba(45,49,66,0.30)",
         tcolor=INK, size=11, weight="500"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="0.8"/>'
            + txt(x + w / 2, y + h / 2 + 4, value, size=size, fill=tcolor,
                  family=MONO, weight=weight))


def legend(y, vw, items):
    s = (f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" '
         f'stroke="{RULE}" stroke-width="0.8"/>')
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for label, colour, shape in items:
        if shape == "box":
            s += (f'<rect x="{x}" y="{y}" width="10" height="10" rx="2" fill="{colour}" '
                  f'fill-opacity="0.18" stroke="{colour}" stroke-width="0.8"/>')
        elif shape == "line":
            s += f'<line x1="{x}" y1="{y + 5}" x2="{x + 12}" y2="{y + 5}" stroke="{colour}" stroke-width="1.4"/>'
        elif shape == "hollow":
            s += (f'<rect x="{x}" y="{y}" width="10" height="10" rx="2" fill="none" '
                  f'stroke="{colour}" stroke-width="1"/>')
        else:
            s += f'<circle cx="{x + 5}" cy="{y + 5}" r="4" fill="{colour}"/>'
        s += mono(x + 18, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.06em")
        x += 18 + 7.2 * len(label) + 28
    return s


# ---------------------------------------------------------------- page + export
PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{title}</title>
<link href="{fonts}" rel="stylesheet">
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; padding: 40px; background: {paper}; color: {ink};
         font-family: {sans}; }}
  .eyebrow {{ font-family: {mono}; font-size: 8px; letter-spacing: 0.18em;
              text-transform: uppercase; color: {soft}; margin: 0 0 6px; }}
  h1 {{ font-family: {serif}; font-weight: 400; font-size: 1.75rem; margin: 0 0 4px; }}
  .sub {{ font-family: {sans}; font-size: 13px; color: {muted}; margin: 0 0 24px;
          max-width: 62ch; }}
  svg {{ display: block; max-width: 100%; height: auto; }}
  footer {{ margin-top: 28px; padding-top: 12px; border-top: 1px solid {rule};
            font-family: {mono}; font-size: 9px; color: {soft};
            letter-spacing: 0.06em; }}
</style></head><body>
<p class="eyebrow">{eyebrow}</p>
<h1>{title}</h1>
<p class="sub">{sub}</p>
{svg}
<footer>gpu-idle-at-100-percent-utilization &middot; figure {num} &middot; own redraw, not reproduced from any source</footer>
</body></html>
"""


def svg_doc(vw, vh, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw} {vh}" '
            f'width="{vw}" height="{vh}" role="img">\n{DEFS}\n'
            f'  <rect width="100%" height="100%" fill="{PAPER}"/>\n{body}\n</svg>')


def rasterize(svg_path, png_path, vw, vh, scale=2, svg_markup=None):
    """Headless Chrome against a zero-margin shim page sized to the viewBox.

    The SVG is inlined rather than referenced with <img src>: an SVG loaded as an
    image is a sandboxed context that will not fetch the webfonts, so the typography
    would silently fall back.
    """
    body = svg_markup if svg_markup is not None else svg_path.read_text(encoding="utf-8")
    body = body.replace('<?xml version="1.0" encoding="UTF-8"?>\n', "")
    shim = (f'<!doctype html><meta charset="utf-8">'
            f'<link href="{FONTS}" rel="stylesheet">'
            f'<style>html,body{{margin:0;padding:0;background:{PAPER};'
            f'width:{vw}px;height:{vh}px;overflow:hidden}}'
            f'svg{{display:block}}</style>'
            f'{body}')
    shim_path = svg_path.with_name(f"_shim_{svg_path.stem}.html")
    shim_path.write_text(shim, encoding="utf-8")
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run(
            ["google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
             "--hide-scrollbars", "--virtual-time-budget=6000",
             f"--user-data-dir={prof}",
             f"--force-device-scale-factor={scale}",
             f"--window-size={vw},{vh}",
             f"--screenshot={png_path}",
             f"file://{shim_path}"],
            check=True, capture_output=True, timeout=120)
    shim_path.unlink(missing_ok=True)


def emit(num, slug, title, sub, eyebrow_text, vw, vh, body):
    stem = f"fig-{num}-{slug}"
    svg = svg_doc(vw, vh, body)
    html = PAGE.format(title=title, sub=sub, eyebrow=ascii_upper(eyebrow_text), num=num,
                       svg=svg, fonts=FONTS, paper=PAPER, ink=INK, muted=MUTED,
                       soft=SOFT, rule=RULE, sans=SANS, mono=MONO, serif=SERIF)
    (HERE / f"{stem}.html").write_text(html, encoding="utf-8")
    svg_path = HERE / f"{stem}.svg"
    svg_path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    png_path = HERE / f"{stem}.png"
    rasterize(svg_path, png_path, vw, vh, svg_markup=svg)
    print(f"  {stem}: html + svg + png ({vw}x{vh} @2x)")
    return stem
