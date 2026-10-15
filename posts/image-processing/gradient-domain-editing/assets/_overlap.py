#!/usr/bin/env python3
"""Measure every <text> in each SVG with getBBox() in headless Chrome, after loading the
webfonts explicitly, and report: text over text, text off the canvas, and text spilling
out of the innermost rect that contains its centre.

lint_visuals.py only sees text leaving the canvas; this sees text leaving its box or
landing on other text. It cannot see text over lines, legend/mark mismatches or wrong
arithmetic, so open every PNG as well.

Known false positives: consecutive serif title lines on social cards (Instrument Serif's
tall font box), and the lockup's ".in", which getBBox reports in the logo's untransformed
local space.

Usage: python3 _overlap.py [svg-dir-or-file ...]   (default: this directory and social/)
Shim pages go to a temporary directory and are deleted afterwards.
"""
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
LOCAL_FONTS = pathlib.Path.home() / ".cache" / "blog-forge-fonts" / "fonts.local.css"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")

JS = r"""
<script>
(async () => {
  const loads = ['400 10px "Geist Mono"', '500 10px "Geist Mono"', '600 10px "Geist Mono"',
                 '400 10px "Geist"', '500 10px "Geist"', '600 10px "Geist"', '400 20px "Instrument Serif"'];
  try { await Promise.all(loads.map(f => document.fonts.load(f, 'Aa0−∠°'))); } catch (e) {}
  await document.fonts.ready;
  const svg = document.querySelector('svg');
  const vb = svg.viewBox.baseVal;
  const texts = [...svg.querySelectorAll('text')].map((t, i) => {
    const b = t.getBBox();
    return {i, s: t.textContent, x: b.x, y: b.y, w: b.width, h: b.height};
  });
  const rects = [...svg.querySelectorAll('rect')].map(r => {
    const b = r.getBBox();
    const stroke = r.getAttribute('stroke');
    return {x: b.x, y: b.y, w: b.width, h: b.height, stroked: !!stroke && stroke !== 'none'};
  }).filter(r => r.w < vb.width - 1 && r.w > 6 && r.h > 6);
  const out = {canvas: [vb.width, vb.height], overlaps: [], offcanvas: [], spill: [],
               fonts: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight)};
  const shrink = 0.5;
  for (let a = 0; a < texts.length; a++) {
    const A = texts[a];
    if (A.w === 0) continue;
    if (A.x < -0.5 || A.y < -0.5 || A.x + A.w > vb.width + 0.5 || A.y + A.h > vb.height + 0.5)
      out.offcanvas.push(A.s);
    for (let b = a + 1; b < texts.length; b++) {
      const B = texts[b];
      if (B.w === 0) continue;
      const ix = Math.min(A.x + A.w, B.x + B.w) - Math.max(A.x, B.x) - 2 * shrink;
      const iy = Math.min(A.y + A.h, B.y + B.h) - Math.max(A.y, B.y) - 2 * shrink;
      if (ix > 0.5 && iy > 0.5) out.overlaps.push([A.s, B.s, +(ix * iy).toFixed(1)]);
    }
    const cx = A.x + A.w / 2, cy = A.y + A.h / 2;
    const holders = rects.filter(r => cx >= r.x && cx <= r.x + r.w && cy >= r.y && cy <= r.y + r.h);
    if (holders.length) {
      holders.sort((p, q) => p.w * p.h - q.w * q.h);
      const r = holders[0];
      const dl = r.x - A.x, dr = A.x + A.w - (r.x + r.w), dt = r.y - A.y, db = A.y + A.h - (r.y + r.h);
      const worst = Math.max(dl, dr, dt, db);
      if (worst > 1.0) out.spill.push([A.s, +worst.toFixed(1), [r.x, r.y, r.w, r.h].map(v => +v.toFixed(0))]);
    }
  }
  const pre = document.createElement('pre');
  pre.id = 'overlap-out';
  pre.textContent = JSON.stringify(out);
  document.body.appendChild(pre);
})();
</script>
"""


def check(svg_path):
    svg = svg_path.read_text(encoding="utf-8").replace('<?xml version="1.0" encoding="UTF-8"?>\n', "")
    fonts = f'<link href="{FONTS}" rel="stylesheet">'
    if LOCAL_FONTS.exists():                      # same local copy the rasteriser uses (see _build.py)
        svg = svg.replace(f"@import url('{FONTS}');", "")
        fonts = f"<style>{LOCAL_FONTS.read_text(encoding='utf-8')}</style>"
    page = (f'<!doctype html><meta charset="utf-8">{fonts}'
            f'<style>body{{margin:0}}</style>{svg}{JS}')
    with tempfile.TemporaryDirectory() as tmp:
        shim = pathlib.Path(tmp) / f"{svg_path.stem}.html"
        shim.write_text(page, encoding="utf-8")
        prof = pathlib.Path(tmp) / "profile"
        res = subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox",
                              f"--user-data-dir={prof}", "--virtual-time-budget=15000", "--dump-dom",
                              f"file://{shim}"], capture_output=True, text=True, timeout=180)
    m = re.search(r'<pre id="overlap-out">(.*?)</pre>', res.stdout, re.S)
    if not m:
        return {"error": "no output"}
    raw = m.group(1).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    return json.loads(raw)


def main():
    files = []
    for arg in sys.argv[1:] or [str(HERE), str(HERE / "social")]:
        p = pathlib.Path(arg).resolve()
        files += sorted(p.glob("*.svg")) if p.is_dir() else [p]
    total = 0
    for f in files:
        r = check(f)
        issues = len(r.get("overlaps", [])) + len(r.get("offcanvas", [])) + len(r.get("spill", []))
        total += issues
        print(f"\n{f.name}: {issues} issue(s); fonts loaded: {len(r.get('fonts', []))}")
        for a, b, area in r.get("overlaps", []):
            print(f"  OVERLAP {area:7.1f}px²  {a!r}  ×  {b!r}")
        for s in r.get("offcanvas", []):
            print(f"  OFF-CANVAS  {s!r}")
        for s, d, rect in r.get("spill", []):
            print(f"  SPILL {d:5.1f}px  {s!r}  out of rect {rect}")
        if "error" in r:
            print("  ERROR", r["error"])
    print(f"\n{len(files)} files, {total} issues")


if __name__ == "__main__":
    main()
