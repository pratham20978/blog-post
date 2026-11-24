#!/usr/bin/env python3
"""Template cover fallback — deterministic, on-brand, real typography (private build script).

Per blog-visuals/references/cover-prompt.md § Template cover fallback, in the layout of Parts 1–8: title in
Instrument Serif, a Geist Mono category label above it, one simplified motif taken from the post's figures,
white-smoke paper, the tangerine used once. The motif is Figure 2 reduced to its argument: the first 200 of
the 3,170 sorted Hedenfalk p-values on a log scale, Benjamini–Hochberg's line kα/m rising with the rank and
last crossed at rank 94 (tangerine, the one use), against Bonferroni's flat α/m, which stops at rank 2.
Values come from the lab's capture. 1200 x 630, rasterised at 2x. Stdlib only, so system python3 runs it.
The cover carries no brand lockup; the social cards do.
Usage: python3 assets/_cover.py
"""
import html
import json
import math
import pathlib
import subprocess
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
RES = json.loads((HERE.parent / "lab" / "captures" / "results-full.json").read_text(encoding="utf-8"))
VW, VH = 1200, 630
STEM = "cover-multiple-comparisons-fwer-fdr"

PAPER, INK, MUTED, SOFT = "#f5f5f5", "#2d3142", "#4f5d75", "#7a8399"
RULE, ACCENT, LINK = "rgba(45,49,66,0.12)", "#eb6c36", "#2e5aa8"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
SANS = "'Geist', system-ui, sans-serif"
MONO = "'Geist Mono', ui-monospace, monospace"
SERIF = "'Instrument Serif', Georgia, serif"
LOCAL_FONTS = pathlib.Path.home() / ".cache" / "blog-forge-fonts" / "fonts.local.css"


def txt(x, y, s, size=12, fill=INK, family=SANS, weight="400", anchor="middle", track=None):
    t = f' letter-spacing="{track}"' if track else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" font-weight="{weight}" '
            f'font-family="{family}" text-anchor="{anchor}"{t}>{html.escape(s)}</text>')


def mono(x, y, s, size=13, fill=SOFT, anchor="start", weight="400", track=None):
    return txt(x, y, s, size=size, fill=fill, family=MONO, weight=weight, anchor=anchor, track=track)


def svg_doc(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img">\n'
            f"  <defs><style>/*<![CDATA[*/@import url('{FONTS}');/*]]>*/</style></defs>\n"
            f'  <rect width="100%" height="100%" fill="{PAPER}"/>\n{body}\n</svg>')


def rasterize(svg, png_path, scale=2):
    """Headless Chrome against a zero-margin shim sized to the viewBox, the SVG inlined so the webfonts load;
    fonts come from the local Google Fonts cache when it exists (a slow network made Chrome fall back)."""
    fonts = f'<link href="{FONTS}" rel="stylesheet">'
    if LOCAL_FONTS.exists():
        svg = svg.replace(f"@import url('{FONTS}');", "")
        fonts = f"<style>{LOCAL_FONTS.read_text(encoding='utf-8')}</style>"
    with tempfile.TemporaryDirectory() as tmp:
        shim = pathlib.Path(tmp) / "shim.html"
        shim.write_text(f'<!doctype html><meta charset="utf-8">{fonts}<style>html,body{{margin:0;padding:0;'
                        f'background:{PAPER};width:{VW}px;height:{VH}px;overflow:hidden}}svg{{display:block}}</style>{svg}',
                        encoding="utf-8")
        subprocess.run(["google-chrome", "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
                        "--virtual-time-budget=15000", "--force-color-profile=srgb", f"--user-data-dir={tmp}/profile",
                        f"--force-device-scale-factor={scale}", f"--window-size={VW},{VH}",
                        f"--screenshot={png_path.resolve()}", f"file://{shim}"],
                       check=True, capture_output=True, timeout=120)


def build():
    pr = RES["procedures"]
    m, a, n = pr["m"], 0.05, 200
    ps = pr["sorted_p_first_300"][:n]
    k_bh, k_bonf = pr["counts_5pct"]["BH"], pr["counts_5pct"]["Bonferroni"]
    assert (m, k_bh, k_bonf, pr["kstar_bh"]) == (3170, 94, 2, 94)
    assert ps[k_bh - 1] <= k_bh * a / m and all(p > (i + 1) * a / m for i, p in enumerate(ps) if i >= k_bh)
    assert ps[k_bonf - 1] <= a / m < ps[k_bonf] and max(ps) < 1e-2 and min(ps) > 1e-6

    x0, x1, top, base = 90, 570, 190, 470                       # rank 1 to 200; p from 1e-6 to 1e-2 (log)
    ex = lambda r: x0 + (r - 1) / (n - 1) * (x1 - x0)
    ey = lambda p: base - (math.log10(p) + 6) / 4 * (base - top)

    s = f'<line x1="{x0 - 10}" y1="{base}" x2="{x1 + 10}" y2="{base}" stroke="{MUTED}" stroke-width="1.2"/>'
    s += (f'<line x1="{x0}" y1="{ey(a / m):.1f}" x2="{x1}" y2="{ey(a / m):.1f}" stroke="{LINK}" '
          f'stroke-width="2.0"/>')
    bh = " ".join(f"{ex(r):.1f},{ey(r * a / m):.1f}" for r in range(1, n + 1))
    s += f'<polyline points="{bh}" fill="none" stroke="{INK}" stroke-width="2.0" stroke-linejoin="round"/>'
    s += "".join(f'<circle cx="{ex(r):.1f}" cy="{ey(p):.1f}" r="2" fill="{SOFT}"/>' for r, p in enumerate(ps, 1))
    cx, cy = ex(k_bh), ey(ps[k_bh - 1])
    s += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="none" stroke="{ACCENT}" stroke-width="2.2"/>'
    s += mono(cx - 12, cy - 14, f"BH: {k_bh} genes", fill=ACCENT, anchor="end", weight="600")
    s += mono(x1, ey(a / m) - 12, f"Bonferroni: {k_bonf} genes", fill=LINK, anchor="end", weight="600")
    s += mono(x0 - 10, 132, "3,170 sorted p-values against two 5% rules, log scale")
    s += mono(x0, base + 24, f"rank of the p-value: 1 to {n}")

    s += mono(640, 214, "data science  ·  statistics for data scientists, part 9", size=11, weight="500", track="0.2em")
    s += txt(640, 290, "Multiple Comparisons", size=46, family=SERIF, anchor="start")
    s += txt(640, 340, "FWER, FDR, and Tests", size=34, family=SERIF, anchor="start")
    s += txt(640, 382, "You Didn't Count", size=34, family=SERIF, anchor="start")
    s += txt(640, 430, "Bonferroni or Holm, Benjamini–Hochberg or Storey:", size=17, fill=MUTED, anchor="start")
    s += txt(640, 456, "each promise measured where its condition fails", size=17, fill=MUTED, anchor="start")

    s += f'<line x1="96" y1="560" x2="1104" y2="560" stroke="{RULE}" stroke-width="0.8"/>'
    s += mono(96, 586, "Bonferroni · Holm · Benjamini–Hochberg · BY · Storey q-values · PRDS · FDP · forking paths · screening",
              size=10, fill=MUTED, track="0.12em")

    svg = svg_doc(s)
    (HERE / f"{STEM}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg + "\n", encoding="utf-8")
    (HERE / f"{STEM}.html").write_text(f'<!doctype html><meta charset="utf-8"><title>Cover</title>'
                                       f'<link href="{FONTS}" rel="stylesheet">'
                                       f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}\n', encoding="utf-8")
    rasterize(svg, HERE / f"{STEM}.png")
    print(f"  cover: html + svg + png ({VW}x{VH} @2x)")


if __name__ == "__main__":
    build()
