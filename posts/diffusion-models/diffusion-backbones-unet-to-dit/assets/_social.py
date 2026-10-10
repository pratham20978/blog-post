#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Diffusion Backbones: U-Net to DiT,
Block by Block".

Diffusion Models, part 4. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every artefact on a
card is read from the lab capture the article ships (../lab/captures.json) or quoted from a
ledger row, so a card cannot disagree with the post.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import json
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
UNET, DIT, MMDIT, ATT, PATCH = CAP["unet"], CAP["dit"], CAP["mmdit"], CAP["attention"], CAP["patch"]

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
BLUE = "#5e7a9b"
MUSTARD = "#b8915a"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/diffusion-backbones-unet-to-dit"
FOOTER = "DIFFUSION BACKBONES, BLOCK BY BLOCK · CANERY.IN"

DIT_FID = {4: 43.01, 2: 19.47}            # L16: DiT Table 4, 400K steps, no guidance


def dit(name, image=256):
    return next(r for r in DIT if r["name"] == name and r["image"] == image)


# ------------------------------------------------------------------ the lockup
LOCKUP_VIEWBOX_W = 671.40
IN_GAP = -10
IN_SIZE = 140
IN_ADVANCE = 171
LOCKUP_FULL_W = LOCKUP_VIEWBOX_W + IN_GAP + IN_ADVANCE


def logo_paths() -> str:
    source = (ROOT / "web/public/brand/canerly-lockup-horizontal.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b[\s\S]*?/>", source)
    if len(paths) != 2:
        raise RuntimeError("Could not read the canonical Canery horizontal lockup")
    suffix = (f'<text x="{LOCKUP_VIEWBOX_W + IN_GAP}" y="122.5" font-size="{IN_SIZE}" '
              f'font-family="{SANS}" font-weight="600" text-anchor="start">.in</text>')
    return "\n".join(paths) + "\n" + suffix


LOGO_PATHS = logo_paths()


# ------------------------------------------------------------------ primitives
def esc(v) -> str:
    return html.escape(str(v), quote=True)


def ascii_upper(v) -> str:
    return "".join(c.upper() if "a" <= c <= "z" else c for c in str(v))


def txt(x, y, value, size=22, fill=INK, family=SANS, weight=400, anchor="start", track=None,
        italic=False):
    extra = f' letter-spacing="{track}"' if track else ""
    extra += ' font-style="italic"' if italic else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{extra}>{esc(value)}</text>')


def mono(x, y, value, size=18, fill=INK, anchor="start", weight=400):
    return txt(x, y, value, size, fill, MONO, weight, anchor)


def label(x, y, value, fill=SOFT, anchor="start", size=14):
    return txt(x, y, ascii_upper(value), size, fill, MONO, 500, anchor, "0.12em")


def lines(x, y, values, size, family=SANS, fill=INK, weight=400, gap=None, anchor="start"):
    gap = gap or int(size * 1.16)
    return "".join(txt(x, y + i * gap, v, size, fill, family, weight, anchor)
                   for i, v in enumerate(values))


def box(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.28)", rx=8, sw=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def grey(v, lo=-1.5, hi=1.5):
    """High value = bright, the series' display convention."""
    u = min(1.0, max(0.0, (v - lo) / (hi - lo)))
    return round(26 + u * (250 - 26))


def valgrid(x, y, M, cell, gap, digits=2, size=20, lo=-1.5, hi=1.5):
    out = ""
    for r, row in enumerate(M):
        for c, v in enumerate(row):
            g = grey(v, lo, hi)
            cx, cy = x + c * (cell + gap), y + r * (cell + gap)
            out += box(cx, cy, cell, cell, f"rgb({g},{g},{g})", "none", 3, 0)
            ink = INK if g > 140 else "#ffffff"
            out += txt(cx + cell / 2, cy + cell / 2 + size * 0.36, f"{v:.{digits}f}".replace("-", "−"),
                       size, ink, MONO, 500, "middle")
    return out


def motif(n):
    """The bright crescent on a dark field that every part of the series carries."""
    M, c0 = [], (n - 1) / 2
    for r in range(n):
        row = []
        for c in range(n):
            d = (((r - c0) ** 2 + (c - c0) ** 2) ** 0.5) / (n / 2)
            v = 0.95 if d < 0.60 else (-0.85 if d > 0.78 else 0.10)
            d2 = (((r - c0 + n * 0.17) ** 2 + (c - c0 + n * 0.17) ** 2) ** 0.5) / (n / 2)
            if d < 0.60 and d2 < 0.46:
                v = -0.50
            row.append(v)
        M.append(row)
    return M


def lcg_normals(n, seed=20260925):
    state, out = seed, []
    while len(out) < n:
        state = (1103515245 * state + 12345) % 2147483648
        u1 = (state + 1) / 2147483649
        state = (1103515245 * state + 12345) % 2147483648
        u2 = state / 2147483648
        r = math.sqrt(-2 * math.log(u1))
        out += [r * math.cos(2 * math.pi * u2), r * math.sin(2 * math.pi * u2)]
    return out[:n]


def latent(n=32, abar=0.96, seed=11):
    clean, eps = motif(n), lcg_normals(n * n, seed)
    a, s = math.sqrt(abar), math.sqrt(1 - abar)
    return [[a * clean[r][c] + s * eps[r * n + c] for c in range(n)] for r in range(n)]


def lattice(x, y, M, cell, gap, p, stroke=ACCENT):
    """A latent drawn as cells with its patch lattice on top."""
    out = ""
    for r, row in enumerate(M):
        for c, v in enumerate(row):
            g = grey(v, -1.2, 1.2)
            out += (f'<rect x="{x + c * (cell + gap):.1f}" y="{y + r * (cell + gap):.1f}" width="{cell}" '
                    f'height="{cell}" fill="rgb({g},{g},{g})"/>')
    n, step = len(M), p * (cell + gap)
    span = n * (cell + gap) - gap
    for k in range(n // p + 1):
        o = min(k * step - gap / 2, span)
        out += (f'<line x1="{x + o:.1f}" y1="{y - 1}" x2="{x + o:.1f}" y2="{y + span + 1}" '
                f'stroke="{stroke}" stroke-width="2"/>')
        out += (f'<line x1="{x - 1}" y1="{y + o:.1f}" x2="{x + span + 1}" y2="{y + o:.1f}" '
                f'stroke="{stroke}" stroke-width="2"/>')
    return out


class Plot:
    def __init__(self, x, y, w, h, xr, yr, logx=False):
        self.x, self.y, self.w, self.h, self.xr, self.yr, self.logx = x, y, w, h, xr, yr, logx

    def X(self, v):
        if self.logx:
            v = math.log10(v)
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h


# ------------------------------------------------------------------ the shell
def shell(kind, number, total, title, deck, visual, takeaway, cta=None):
    if kind == "feed":
        height, logo_y, logo_w = 1350, 72, 220
        rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
        deck_y = title_y + len(title) * title_gap + 20
        take_rule, take_y, foot_y = 1168, 1220, 1305
    else:
        height, logo_y, logo_w = 1920, 250, 245
        rule_y, title_y, title_size, title_gap = 340, 470, 70, 80
        deck_y = title_y + len(title) * title_gap + 28
        take_rule, take_y, foot_y = 1505, 1570, 1665
    scale = logo_w / LOCKUP_FULL_W
    defs = (f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style>'
            f'<marker id="arrow-a" markerUnits="userSpaceOnUse" markerWidth="16" markerHeight="11" '
            f'refX="15" refY="5.5" orient="auto"><polygon points="0 0,16 5.5,0 11" fill="{ACCENT}"/></marker>'
            f'</defs>')
    body = f'<rect width="{VW}" height="{height}" fill="{PAPER}"/>'
    body += (f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
             f'data-logo-width="{logo_w}" fill="{INK}" '
             f'transform="translate(72 {logo_y}) scale({scale})">{LOGO_PATHS}</g>')
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", SOFT, "end", 15)
    body += hline(72, 1008, rule_y)
    body += lines(72, title_y, title, title_size, SERIF, gap=title_gap)
    body += lines(72, deck_y, deck, 22 if kind == "feed" else 26, fill=MUTED,
                  gap=30 if kind == "feed" else 36)
    body += visual
    body += hline(72, 1008, take_rule)
    body += lines(72, take_y, takeaway, 22 if kind == "feed" else 27, weight=600,
                  gap=30 if kind == "feed" else 36)
    body += label(72, foot_y, cta or FOOTER, ACCENT if cta else SOFT, "start",
                  14 if kind == "feed" else 16)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {height}" '
            f'width="{VW}" height="{height}" role="img">\n{defs}\n{body}\n</svg>')


def emit(kind, number, slug, title, deck, visual, takeaway, total, cta=None):
    svg = shell(kind, number, total, title, deck, visual, takeaway, cta)
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>{esc(" ".join(title))}</title><link href="{FONTS.replace("&", "&amp;")}" rel="stylesheet">'
            f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style>'
            f'</head><body>{svg}</body></html>')
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{kind}-{number:02d}-{slug}.html"
    path.write_text(page, encoding="utf-8")
    print(path.name)


FEED_TOTAL, STORY_TOTAL = 7, 4


# ------------------------------------------------------------------ shared artefacts
def two_patch_sizes(x0, y0, cell, gap, col_w, rows_gap=40, size=24):
    """DiT-XL/4 and DiT-XL/2 side by side on the same latent, with their numbers."""
    lat = latent()
    out = ""
    span = 32 * (cell + gap) - gap
    for i, p in enumerate((4, 2)):
        r = dit(f"DiT-XL/{p}")
        x = x0 + i * col_w
        out += lattice(x, y0, lat, cell, gap, p)
        hot = ACCENT if p == 2 else INK
        ty = y0 + span + 52
        out += txt(x, ty, f"DiT-XL/{p} · patch {p}×{p}", size + 6, hot, SERIF, 400)
        rows = [(f"{r['tokens']} tokens", hot), (f"{r['gmac']:.2f} GMAC per call", hot),
                (f"FID {DIT_FID[p]} at 400K steps", hot), (f"{r['params']:,} parameters", MUTED)]
        for k, (t, c) in enumerate(rows):
            out += mono(x, ty + 44 + k * rows_gap, t, size, c, "start", 600 if k < 3 else 400)
    return out


def legend(x, y, size=15):
    out = ""
    for name, fill, stroke in (("weights", "rgba(94,122,155,0.25)", BLUE),
                               ("FLOPs", "rgba(45,49,66,0.10)", INK),
                               ("of which attention comparisons", "rgba(235,108,54,0.55)", ACCENT)):
        out += box(x, y - size + 2, size, size, fill, stroke, 3, 1.5)
        out += label(x + size + 10, y, name, MUTED, "start", size)
        x += size + 30 + len(name) * size * 0.72
    return out


def level_bars(x0, y0, row_h, scale, size=26):
    """SD 1.5's U-Net per level: share of parameters against share of FLOPs."""
    lv = {l["level"]: l for l in UNET["levels"]}
    P, F = UNET["params"], UNET["flops"]
    out = ""
    names = [(0, "64×64", "width 320"), (1, "32×32", "width 640"), (2, "16×16", "width 1,280"),
             (3, "8×8 + middle", "width 1,280")]
    for i, (k, name, width) in enumerate(names):
        l, y = lv[k], y0 + i * row_h
        pp, fp = 100 * l["params"] / P, 100 * l["flops"] / F
        ap = 100 * l["flops_split"].get("attention_core", 0) / F
        out += txt(x0, y + 30, name, size + 6, INK, SERIF, 400)
        out += mono(x0, y + 60, width, size - 8, SOFT)
        bx = x0 + 250
        out += box(bx, y + 6, pp * scale, 32, "rgba(94,122,155,0.25)", BLUE, 3, 1.5)
        out += mono(bx + pp * scale + 12, y + 31, f"{pp:.1f}% of weights", size - 6, BLUE, "start", 600)
        out += box(bx, y + 46, fp * scale, 32, "rgba(45,49,66,0.10)", INK, 3, 1.5)
        if ap * scale > 2:
            out += box(bx, y + 46, ap * scale, 32, "rgba(235,108,54,0.55)", ACCENT, 3, 1.5)
        out += mono(bx + fp * scale + 12, y + 71, f"{fp:.1f}% of FLOPs", size - 6, INK, "start", 600)
    return out


def share_plot(x, y, w, h, size=20):
    """Attention's share of one transformer block, with measured points."""
    pl = Plot(x, y, w, h, (math.log10(0.03), math.log10(30)), (0, 80), logx=True)
    out = hline(x, x + w, y + h, RULE_SOLID, 1.5)
    out += f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + h}" stroke="{RULE_SOLID}" stroke-width="1.5"/>'
    for v in (20, 40, 60, 80):
        out += hline(x, x + w, pl.Y(v), RULE)
        out += mono(x - 12, pl.Y(v) + 7, f"{v}%", size - 4, SOFT, "end")
    for v, t in ((0.1, "0.1"), (1, "1"), (10, "10")):
        out += mono(pl.X(v), y + h + 30, t, size - 4, SOFT, "middle")
    out += mono(x + w / 2, y + h + 62, "N / D, tokens per unit of width (log scale)", size - 4, SOFT, "middle")
    for share, r, t in ((100 / 3, 3, "N = 3D"), (50, 6, "N = 6D")):
        out += (f'<line x1="{pl.X(r):.1f}" y1="{pl.Y(share):.1f}" x2="{pl.X(r):.1f}" y2="{y + h}" '
                f'stroke="{RULE_SOLID}" stroke-width="1.5" stroke-dasharray="6,5"/>')
        if r == 3:
            out += mono(pl.X(r) - 8, y + h - 12, t, size - 4, SOFT, "end", 500)
        else:
            out += mono(pl.X(r) + 8, y + h - 12, t, size - 4, SOFT, "start", 500)
    pts = []
    for i in range(241):
        r = 10 ** (math.log10(0.03) + i * 3 / 240)
        pts.append(f"{pl.X(r):.1f},{pl.Y(100 * r / (r + 6)):.1f}")
    out += (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{INK}" stroke-width="4" '
            f'stroke-linejoin="round"/>')
    D = ATT["width"]
    marks = []
    for row in ATT["flops"]:
        if row["tokens"] in (256, 16384):
            marks.append((row["tokens"] / D, 100 * row["share"], INK))
    c = MMDIT["call_1024"]
    marks.append((c["joint_tokens"] / MMDIT["d24"]["width"],
                  100 * c["flops_by_stream"]["joint_attention_core"] / c["flops"], ACCENT))
    for r, s, col in marks:
        out += f'<circle cx="{pl.X(r):.1f}" cy="{pl.Y(s):.1f}" r="11" fill="{col}"/>'
    return out, marks, pl


# ------------------------------------------------------------------ feed
def feed_01():
    v = two_patch_sizes(100, 500, 11, 1, 520)
    emit("feed", 1, "count-tokens-not-parameters",
         ["Count tokens,", "not parameters."],
         ["Two DiT-XL models with the same 675M parameters. One cuts",
          "its latent into 4×4 patches, the other into 2×2."],
         v,
         ["Halving the patch quadruples the tokens every block sees:",
          "4.08× the compute, and FID falls from 43.01 to 19.47."],
         FEED_TOTAL)


def feed_02():
    M = [[PATCH["p1"]["values"][r * 4 + c][0] for c in range(4)] for r in range(4)]
    cell, gap = 76, 6
    v = valgrid(96, 520, M, cell, gap, 2, 22)
    span = 2 * cell + gap
    for r in (0, 1):
        for c in (0, 1):
            v += box(96 + c * (span + gap) - 4, 520 + r * (span + gap) - 4, span + 8, span + 8,
                     "none", ACCENT, 6, 3)
    v += mono(96, 890, "16 positions · 256 pairs", 22, INK, "start", 600)
    v += label(510, 506, "U-Net · average pool", INK, "start", 16)
    v += valgrid(510, 522, PATCH["avgpool2"], 96, 6, 4, 19)
    v += mono(732, 572, "4 positions", 22, INK, "start", 600)
    v += mono(732, 606, "12 values gone", 22, MUTED)
    v += mono(732, 640, "a skip keeps them", 22, ACCENT)
    v += label(510, 756, "DiT · patchify, p = 2", INK, "start", 16)
    for i, tok in enumerate(PATCH["p2"]["values"]):
        v += valgrid(510, 772 + i * 54, [tok], 50, 4, 2, 15)
    v += mono(740, 824, "4 tokens", 22, INK, "start", 600)
    v += mono(740, 858, "all 16 values kept", 22, MUTED)
    v += mono(740, 892, "in token width", 22, ACCENT)
    v += box(96, 1030, 888, 96, ACCENT_TINT, ACCENT, 8, 1.5)
    v += mono(540, 1088, "attention pairs: 256 → 16, either way", 26, INK, "middle", 600)
    emit("feed", 2, "two-ways-to-shrink-a-patch",
         ["Two ways to shrink", "a patch."],
         ["Part 1's noisy 4×4 patch, made smaller before attention",
          "compares every position with every other."],
         v,
         ["Pooling throws 12 of 16 values away and needs a skip.",
          "Patchifying keeps all 16 in the token's width."],
         FEED_TOTAL)


def feed_03():
    v = legend(72, 500, 15)
    v += level_bars(72, 530, 150, 8.4)
    emit("feed", 3, "params-bottom-compute-top",
         ["Parameters at the bottom,", "compute at the top."],
         ["Stable Diffusion 1.5's U-Net, measured level by level for",
          f"one 512×512 image: 860M parameters, {UNET['flops'] / 1e9:.0f} GFLOP."],
         v,
         ["The 64×64 level holds 3.4% of the weights and does 38.2%",
          "of the work, mostly attention over 4,096 positions."],
         FEED_TOTAL)


def feed_04():
    d24, c = MMDIT["d24"], MMDIT["call_1024"]
    ps, fs = d24["params_split"], c["flops_by_stream"]
    x0, w = 96, 888
    v = label(x0, 520, f"parameters · {d24['params'] / 1e9:.2f}B", INK, "start", 16)
    x = x0
    for key, col, fill, name in (("image", BLUE, "rgba(94,122,155,0.30)", "image stream"),
                                 ("text", MUSTARD, "rgba(184,145,90,0.35)", "text stream"),
                                 ("outside_blocks", SOFT, "rgba(122,131,153,0.25)", "")):
        sw = ps[key] / d24["params"] * w
        v += box(x, 540, max(sw, 2), 110, fill, col, 4, 1.5)
        if name:
            v += mono(x + sw / 2, 590, name, 24, INK, "middle", 600)
            v += mono(x + sw / 2, 626, f"{100 * ps[key] / d24['params']:.1f}%", 24, INK, "middle")
        x += sw
    v += label(x0, 730, f"flops per 1024×1024 call · {c['flops'] / 1e9:,.0f} gflop", INK, "start", 16)
    x = x0
    for key, col, fill, name in (("image", BLUE, "rgba(94,122,155,0.30)", "image stream"),
                                 ("joint_attention_core", ACCENT, "rgba(235,108,54,0.45)", "joint attention"),
                                 ("text", MUSTARD, "rgba(184,145,90,0.35)", ""),
                                 ("outside_blocks", SOFT, "rgba(122,131,153,0.25)", "")):
        sw = fs[key] / c["flops"] * w
        v += box(x, 750, max(sw, 2), 110, fill, col, 4, 1.5)
        if name:
            v += mono(x + sw / 2, 800, name, 24, INK, "middle", 600)
            v += mono(x + sw / 2, 836, f"{100 * fs[key] / c['flops']:.1f}%", 24, INK, "middle")
        x += sw
    tx = x0 + (fs["image"] + fs["joint_attention_core"]) / c["flops"] * w + fs["text"] / c["flops"] * w / 2
    v += f'<line x1="{tx:.1f}" y1="860" x2="{tx:.1f}" y2="900" stroke="{MUSTARD}" stroke-width="2.5"/>'
    v += mono(tx, 934, f"text stream: {100 * fs['text'] / c['flops']:.1f}%", 24, MUSTARD, "end", 600)
    v += mono(x0, 1030, "4,096 image tokens and 154 text tokens,", 22, MUTED)
    v += mono(x0, 1064, "one joint attention over all 4,250 of them", 22, MUTED)
    emit("feed", 4, "half-the-weights",
         ["Half the weights,", "2.4% of the arithmetic."],
         ["SD3's 2B MM-DiT gives text its own stream of weights.",
          "One 1024×1024 call, measured stream by stream."],
         v,
         ["Weights cost by width; FLOPs cost by tokens. Joint",
          "attention over 4,250 tokens is 31.6% of the call."],
         FEED_TOTAL)


def feed_05():
    v, marks, pl = share_plot(170, 500, 800, 470)
    names = ["DiT-XL/2 · 256 px · 3.6%", "DiT-XL at 16,384 tokens · 70.3%", "SD3-2B · 1024 px · 31.6%"]
    offs = [(-200, -58, "start"), (-18, -14, "end"), (-20, -16, "end")]
    for (r, s, col), name, (dx, dy, anc) in zip(marks, names, offs):
        v += mono(pl.X(r) + dx, pl.Y(s) + dy, name, 21, col, anc, 600)
    r, s, _ = marks[0]
    v += (f'<line x1="{pl.X(r):.1f}" y1="{pl.Y(s) - 14:.1f}" x2="{pl.X(r):.1f}" y2="{pl.Y(s) - 50:.1f}" '
          f'stroke="{INK}" stroke-width="1.5"/>')
    emit("feed", 5, "attention-takes-over",
         ["Attention's share", "is N / (N + 6D)."],
         ["N tokens, width D, a standard transformer block with a",
          "4× MLP. Every measured model lands on the same curve."],
         v,
         ["A third at N = 3D, half at N = 6D. The same DiT-XL block",
          "is 3.6% attention at 256 px and 70.3% at 2048 px."],
         FEED_TOTAL)


def feed_06():
    row = next(r for r in ATT["cpu"] if r["tokens"] == 4096)
    x0, w = 96, 640
    v = label(x0, 520, "time per call, 4,096 tokens", INK, "start", 16)
    v += box(x0, 540, w, 70, "rgba(45,49,66,0.15)", INK, 4, 1.5)
    v += mono(x0 + w + 16, 586, f"naive {row['naive_ms']:.0f} ms", 24, INK, "start", 600)
    v += box(x0, 626, row["fused_ms"] / row["naive_ms"] * w, 70, "rgba(235,108,54,0.45)", ACCENT, 4, 1.5)
    v += mono(x0 + row["fused_ms"] / row["naive_ms"] * w + 16, 672, f"fused {row['fused_ms']:.0f} ms",
              24, ACCENT, "start", 600)
    v += label(x0, 776, "largest single allocation", INK, "start", 16)
    v += box(x0, 796, w, 70, "rgba(45,49,66,0.15)", INK, 4, 1.5)
    v += mono(x0 + w + 16, 842, f"naive {row['naive_largest_alloc_MB']:,.0f} MB", 24, INK, "start", 600)
    fw = row["fused_largest_alloc_MB"] / row["naive_largest_alloc_MB"] * w
    v += box(x0, 882, max(fw, 4), 70, "rgba(235,108,54,0.45)", ACCENT, 4, 1.5)
    v += mono(x0 + max(fw, 4) + 16, 928, f"fused {row['fused_largest_alloc_MB']:.1f} MB", 24, ACCENT, "start", 600)
    v += mono(x0, 1040, f"score matrix: 16 heads × 4,096² × 4 bytes = {row['score_matrix_MB_fp32']:,.1f} MB",
              21, MUTED)
    v += mono(x0, 1074, "fp32, batch 1, AMD Ryzen 7 5825U, 8 threads", 21, SOFT)
    emit("feed", 6, "same-flops-different-bytes",
         ["Same FLOPs,", "58× the memory."],
         ["One 16-head attention layer at 4,096 tokens on a laptop",
          "CPU, computed naively and with PyTorch's fused kernel."],
         v,
         ["The naive path stores the full score matrix. The fused",
          "kernel computes the same numbers without ever holding it."],
         FEED_TOTAL)


def feed_07():
    items = [("U-Net · SD 1.5", "84% of the weights at 16² and 8²; 38% of FLOPs at 64²"),
             ("DiT-XL", "patch 4 → 2: ×4 tokens, ×4.08 compute, same 675M"),
             ("MM-DiT · SD3-2B", "text stream: 49% of weights, 2.4% of FLOPs"),
             ("Attention", "share = N / (N + 6D): half at N = 6D"),
             ("Memory", "SD3's T5 encoder alone needs 19.05 GB")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 7, "read-the-article",
         ["The denoiser,", "block by block."],
         ["Shapes, parameters, FLOPs and memory for SD 1.5's U-Net,",
          "DiT-XL and SD3's MM-DiT, measured in a lab you can run."],
         v,
         ["Count tokens before parameters when you choose,",
          "fine-tune or serve a diffusion model."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = two_patch_sizes(96, 800, 12, 1, 470, 46, 26)
    emit("story", 1, "count-tokens-not-parameters",
         ["Count tokens,", "not parameters."],
         ["Same 675M parameters.", "4× the tokens, 4.08× the compute."],
         v,
         ["Patch size is a compute dial,", "not a size dial."],
         STORY_TOTAL)


def story_02():
    v = legend(72, 790, 16)
    v += level_bars(72, 830, 165, 8.0, 28)
    emit("story", 2, "params-bottom-compute-top",
         ["Parameters at the bottom,", "compute at the top."],
         ["SD 1.5's U-Net, level by level,", "for one 512×512 image."],
         v,
         ["The finest level is cheap to store", "and expensive to run."],
         STORY_TOTAL)


def story_03():
    v, marks, pl = share_plot(170, 800, 790, 520, 24)
    names = ["DiT-XL/2 · 256 px · 3.6%", "16,384 tokens · 70.3%", "SD3-2B · 31.6%"]
    offs = [(-200, -124, "start"), (-20, -16, "end"), (-22, -18, "end")]
    for (r, s, col), name, (dx, dy, anc) in zip(marks, names, offs):
        v += mono(pl.X(r) + dx, pl.Y(s) + dy, name, 24, col, anc, 600)
    r, s, _ = marks[0]
    v += (f'<line x1="{pl.X(r):.1f}" y1="{pl.Y(s) - 14:.1f}" x2="{pl.X(r):.1f}" y2="{pl.Y(s) - 116:.1f}" '
          f'stroke="{INK}" stroke-width="1.5"/>')
    emit("story", 3, "attention-takes-over",
         ["Attention's share", "is N / (N + 6D)."],
         ["N tokens, width D:", "half the block at N = 6D."],
         v,
         ["Token count, not parameter count,", "decides when to swap backbones."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["trace a real U-Net, block by block",
             "DiT at two patch sizes",
             "MM-DiT's two streams, one attention",
             "attention cost against token count",
             "the memory bill, and when to swap"]
    y = 880
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 30, INK, SANS, 600 if i == 4 else 400)
        y += 108
    emit("story", 4, "read-the-article",
         ["The denoiser,", "block by block."],
         ["Every number measured", "in a lab you can run."],
         v,
         ["The full article is on Canery."],
         STORY_TOTAL, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07,
            story_01, story_02, story_03, story_04]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
