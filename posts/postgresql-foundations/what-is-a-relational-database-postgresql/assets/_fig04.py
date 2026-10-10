#!/usr/bin/env python3
"""FIG_04 is routed `mermaid`: Mermaid's layout engine places the flowchart. This script renders
fig-04-path-of-a-query.mmd with mermaid-cli, then rasterises the SVG with the same headless
Chrome shim as every other figure. Paths are absolute: a relative path makes Chrome screenshot its
own error page into the PNG, and nothing downstream would notice."""
import pathlib
import re
import subprocess

from _build import rasterize

HERE = pathlib.Path(__file__).resolve().parent
MMD = (HERE / "fig-04-path-of-a-query.mmd").resolve()
SVG = (HERE / "fig-04-path-of-a-query.svg").resolve()
PNG = (HERE / "fig-04-path-of-a-query.png").resolve()

subprocess.run(["npx", "-y", "@mermaid-js/mermaid-cli", "-i", str(MMD), "-o", str(SVG),
                "-b", "#f5f5f5", "-c", str(HERE / "_mermaid-config.json"),
                "-p", str(HERE / "_puppeteer.json")], check=True, cwd=HERE)
svg = SVG.read_text(encoding="utf-8")
_, _, vw, vh = (float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split())
svg = re.sub(r'<svg ', f'<svg width="{int(vw)}" height="{int(vh)}" ', svg, count=1)
svg = svg.replace('width="100%"', "", 1)
rasterize(SVG, PNG, int(vw), int(vh), svg_markup=svg)
print(f"  fig-04-path-of-a-query: mmd + svg + png ({int(vw)}x{int(vh)} @2x)")
