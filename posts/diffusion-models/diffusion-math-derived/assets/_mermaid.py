#!/usr/bin/env python3
"""Render a .mmd through Mermaid's own layout engine into .svg and .png.

Used for the diagrams that are a *scope* problem rather than a density problem:
whole-system graphs with more nodes and more crossing edges than a hand-placed
SVG can position. blog-visuals section 5 has the test for when to reach for it.

The published article still references a PNG. The site renders Markdown with
rehype-sanitize and no Mermaid plugin, so a fenced block would reach the reader
as visible source code.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile

from _build import FONTS, INK, MUTED, PAPER, RULE_SOLID, SOFT, rasterize

HERE = pathlib.Path(__file__).resolve().parent

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link href="{fonts}" rel="stylesheet">
<style>html,body{{margin:0;background:{paper}}}#d{{padding:24px}}</style>
</head><body><div id="d"><pre class="mermaid">{src}</pre></div>
<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({{
  startOnLoad: false, theme: 'base', securityLevel: 'loose',
  themeVariables: {{
    fontFamily: "'Geist',system-ui,sans-serif", fontSize: '14px',
    primaryColor: '#ffffff', primaryTextColor: '{ink}', primaryBorderColor: '{ink}',
    lineColor: '{muted}', textColor: '{ink}',
    secondaryColor: '#ececec', tertiaryColor: '{paper}',
    clusterBkg: 'rgba(45,49,66,0.035)', clusterBorder: '{rule}',
    edgeLabelBackground: '{paper}'
  }},
  flowchart: {{ curve: 'basis', nodeSpacing: 32, rankSpacing: 58, padding: 10,
               htmlLabels: false, useMaxWidth: false }}
}});
await document.fonts.load("14px 'Geist'"); await document.fonts.ready;
await mermaid.run({{ querySelector: '.mermaid' }});
document.title = 'ready';
</script></body></html>"""


PREVIEW = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>Figure {number}</title><link href="{fonts}" rel="stylesheet"><style>
*{{box-sizing:border-box}}body{{margin:0;padding:40px;background:{paper};color:{ink};
font-family:'Geist',system-ui,sans-serif}}
.k{{font-family:'Geist Mono',monospace;font-size:8px;letter-spacing:.18em;
text-transform:uppercase;color:{soft};margin:0 0 8px}}
h1{{font-family:'Instrument Serif',Georgia,serif;font-size:28px;font-weight:400;margin:0 0 16px}}
svg{{display:block;max-width:100%;height:auto}}
pre{{background:#fff;border:1px solid {rule};border-radius:6px;padding:16px;
font:11px/1.5 'Geist Mono',monospace;overflow:auto;color:{muted};margin-top:24px}}
footer{{border-top:1px solid {rule};margin-top:24px;padding-top:12px;color:{soft};
font:9px 'Geist Mono',monospace}}
</style></head><body><p class="k">Figure {number} · laid out by mermaid</p>
<h1>{stem}</h1>{svg}
<p class="k" style="margin-top:28px">editable source — assets/{stem}.mmd</p>
<pre>{src}</pre>
<footer>diffusion-math-derived · original editorial diagram</footer></body></html>"""


def render(stem: str) -> None:
    src = (HERE / f"{stem}.mmd").read_text(encoding="utf-8")
    page = PAGE.format(src=src, fonts=FONTS, paper=PAPER, ink=INK, muted=MUTED,
                       rule=RULE_SOLID)
    with tempfile.TemporaryDirectory(prefix="mmd-") as temp:
        root = pathlib.Path(temp)
        (root / "m.html").write_text(page, encoding="utf-8")
        out = subprocess.run(
            ["google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
             "--virtual-time-budget=45000", f"--user-data-dir={root / 'p'}",
             "--dump-dom", f"file://{root / 'm.html'}"],
            check=True, capture_output=True, timeout=180).stdout.decode("utf-8")

    found = re.search(r"<svg[\s\S]*?</svg>", out)
    if not found:
        raise RuntimeError(f"{stem}: mermaid produced no SVG")
    svg = found.group(0)

    # Mermaid scopes every CSS rule under the svg's own id, so the opening tag
    # must be kept and patched in place. Rebuilding it drops the id, the rules
    # stop matching, and every edge path falls back to fill:black.
    open_tag = re.match(r"<svg\b[^>]*>", svg).group(0)
    vb = re.search(r'viewBox="([\d.\- ]+)"', open_tag)
    _, _, vw, vh = (float(v) for v in vb.group(1).split())
    scale = min(2.0, 1180 / vw)
    w, h = round(vw * scale), round(vh * scale)

    patched = re.sub(r'\sstyle="[^"]*"', "", open_tag)          # drop max-width
    patched = re.sub(r'\swidth="[^"]*"', "", patched)
    patched = re.sub(r'\sheight="[^"]*"', "", patched)
    patched = patched[:-1] + f' width="{w}" height="{h}">'
    if "xmlns=" not in patched:
        patched = patched.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    svg = patched + f'<rect width="100%" height="100%" fill="{PAPER}"/>' + svg[len(open_tag):]

    (HERE / f"{stem}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg,
                                      encoding="utf-8")
    number = stem.split("-")[1]
    (HERE / f"{stem}.html").write_text(
        PREVIEW.format(stem=stem, number=number, fonts=FONTS, paper=PAPER, ink=INK,
                       muted=MUTED, soft=SOFT, rule=RULE_SOLID, svg=svg,
                       src=(HERE / f"{stem}.mmd").read_text(encoding="utf-8")),
        encoding="utf-8")
    rasterize(svg, HERE / f"{stem}.png", w, h, scale=2)
    print(f"rendered {stem} via mermaid  ({w}x{h})")


if __name__ == "__main__":
    for stem in (sys.argv[1:] or [p.stem for p in sorted(HERE.glob("fig-*.mmd"))]):
        render(stem)
