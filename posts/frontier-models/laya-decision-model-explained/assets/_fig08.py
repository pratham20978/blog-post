#!/usr/bin/env python3
"""FIG_08 is routed `mermaid`: it is the post's one end-to-end architecture view, so Mermaid's
layout engine places it. This script renders fig-08-laya-end-to-end-laya-decision-model-explained.mmd with mermaid-cli, then
rasterises the SVG with the same headless-Chrome shim as every other figure. Paths are absolute:
a relative path makes Chrome screenshot its own error page into the PNG, and nothing downstream
would notice."""
import pathlib
import re
import subprocess

from _build import SUFFIX, rasterize

HERE = pathlib.Path(__file__).resolve().parent
MMD = (HERE / f"fig-08-laya-end-to-end-{SUFFIX}.mmd").resolve()
STEM = f"fig-08-laya-end-to-end-{SUFFIX}"
SVG = (HERE / f"{STEM}.svg").resolve()
PNG = (HERE / f"{STEM}.png").resolve()

subprocess.run(["npx", "-y", "@mermaid-js/mermaid-cli", "-i", str(MMD), "-o", str(SVG),
                "-b", "#f5f5f5", "-c", str(HERE / "_mermaid-config.json"),
                "-p", str(HERE / "_puppeteer.json")], check=True, cwd=HERE)
svg = SVG.read_text(encoding="utf-8")
_, _, vw, vh = (float(v) for v in re.search(r'viewBox="([^"]+)"', svg).group(1).split())
svg = re.sub(r'<svg ', f'<svg width="{int(vw)}" height="{int(vh)}" ', svg, count=1)
svg = svg.replace('width="100%"', "", 1)
rasterize(SVG, PNG, int(vw), int(vh), svg_markup=svg)
print(f"  {STEM}: mmd + svg + png ({int(vw)}x{int(vh)} @2x)")
