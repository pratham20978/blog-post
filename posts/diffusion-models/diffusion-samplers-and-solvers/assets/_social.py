#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Diffusion Samplers and Solvers:
1,000 Steps Into 20".

Diffusion Models, part 6. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every measured or
computed artefact on a card is read from the lab capture the article ships (../lab/captures.json);
the one quoted table (Restart's Table 4) is typed once below with its ledger key, so a card cannot
disagree with the post.

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
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("P6_SOCIAL_OUT", HERE / "social"))
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads(pathlib.Path(os.environ.get("P6_CAPTURES", HERE.parent / "lab" / "captures.json"))
                 .read_text(encoding="utf-8"))
W, ODE, SAMPLES = CAP["worked"], CAP["ode"], CAP["samples"]
NG = ODE["nfe_to_grey"]

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
PURPLE = "#8a5a9e"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/diffusion-samplers-and-solvers"
FOOTER = "DIFFUSION SAMPLERS AND SOLVERS · CANERY.IN"

# Quoted from Xu et al. 2023 (Restart), Table 4 — FID, class-conditional ImageNet 64×64, EDM's model (L36)
RESTART_T4 = {"Heun ODE": [(35, 2.46), (63, 2.30), (127, 2.25), (255, 2.24), (511, 2.24), (1023, 2.24)],
              "EDM stochastic": [(35, 2.97), (63, 2.24), (127, 1.75), (255, 1.50), (511, 1.45), (1023, 1.40)]}


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


def grey(v, lo=-1.6, hi=1.6):
    """High value = bright, the series' display convention."""
    u = min(1.0, max(0.0, (v - lo) / (hi - lo)))
    return round(26 + u * (250 - 26))


def polyline(pts, colour, width=5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return ('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
            + f'" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" '
            f'stroke-linecap="round"{d}/>')


class Plot:
    """Data to pixels; logx/logy put an axis on log10, and a reversed range runs right to left."""

    def __init__(self, x, y, w, h, xr, yr, logx=False, logy=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.xr, self.yr, self.logx, self.logy = xr, yr, logx, logy

    def X(self, v):
        v = math.log10(v) if self.logx else v
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        v = math.log10(max(v, 1e-12)) if self.logy else v
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
def png_gray(rows):
    """A greyscale PNG from rows of 0..255 ints, stdlib only."""
    import base64
    import struct
    import zlib
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()


def tile(x, y, size, flat, side=32):
    rows = [[grey(flat[r * side + c]) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>'
            + box(x, y, size, size, "none", RULE_SOLID, 0, 1))


def fan(x, y, w, h, tile_size, label_size=16):
    """The toy's exact ODE paths (crescent coordinate) with DDIM's six-step chords, ending on the
    crescents they reach: the article's Figure 3 and the cover, restyled for a card."""
    P = SAMPLES["paths"]
    sig = P["sigma"]
    vals = [v for row, s in zip(P["crescent"], sig) if s <= 40 for v in row]
    pl = Plot(x, y, w, h, (40, 0), (min(vals) - 4, max(vals) + 4))
    out = box(pl.X(20), y, pl.X(5) - pl.X(20), h, ACCENT_TINT, "none", 0, 0)
    out += label((pl.X(20) + pl.X(5)) / 2, y + 26, "the bend", ACCENT, "middle", label_size)
    for j in range(6):
        path = [(s, row[j]) for s, row in zip(sig, P["crescent"])]
        k = next(i for i, (s, _) in enumerate(path) if s <= 40)
        (s0, v0), (s1, v1) = path[k - 1], path[k]
        v40 = v0 + (v1 - v0) * (s0 - 40) / (s0 - s1)
        out += polyline([(pl.X(40), pl.Y(v40))] + [(pl.X(s), pl.Y(v)) for s, v in path[k:]], MUTED, 3.5)
        pts = [(s, row[j]) for s, row in zip(P["ddim6_sigma"], P["ddim6_crescent"])]
        clip = [(pl.X(max(min(s, 40), 0)), pl.Y(v)) for s, v in pts if s <= 40] or []
        if pts[0][0] > 40:                                         # enter the panel where the first chord crosses σ = 40
            (s0, v0), (s1, v1) = pts[0], pts[1]
            v40 = v0 + (v1 - v0) * (s0 - 40) / (s0 - s1)
            clip = [(pl.X(40), pl.Y(v40))] + clip
        out += polyline(clip, ACCENT, 4, "12,9")
    out += hline(x, x + w, y + h, RULE_SOLID, 1.5)
    for s in (40, 30, 20, 10, 0):
        out += mono(pl.X(s), y + h + 34, f"σ {s}", 18, SOFT, "middle")
    ends, used = [], []
    for j, v in enumerate(P["crescent"][-1]):
        if all(abs(v - u) > 6 for u in used):
            used.append(v)
            ends.append((v, j))
    slots = sorted((pl.Y(v) - tile_size / 2, v, j) for v, j in ends)
    ys = []
    for yy, v, j in slots:
        ys.append(max(yy, ys[-1] + tile_size + 14) if ys else yy)
    for (y0, v, j), yy in zip(slots, ys):
        out += polyline([(x + w + 6, pl.Y(v)), (x + w + 22, pl.Y(v)), (x + w + 22, yy + tile_size / 2),
                         (x + w + 34, yy + tile_size / 2)], SOFT, 2)
        out += tile(x + w + 34, yy, tile_size, SAMPLES["exact"][j])
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    v = fan(96, 520, 690, 470, 104)
    v += polyline([(110, 1068), (170, 1068)], MUTED, 4) + mono(184, 1075, "exact path", 21, MUTED)
    v += polyline([(390, 1068), (450, 1068)], ACCENT, 4, "12,9") + mono(464, 1075, "DDIM, six steps", 21, ACCENT)
    emit("feed", 1, "a-sampler-is-an-ode-solver",
         ["A sampler is an", "ODE solver."],
         ["The trained denoiser fixes one exact path from each noise",
          "sample to an image. DDIM, Heun and DPM-Solver follow it."],
         v,
         ["The step count is an accuracy dial, not a property",
          "of the model. No retraining needed."],
         FEED_TOTAL)


def first_steps_table(x, y, row_h, size=26, head=16):
    rows = [(1, "∞ → 107.96", None, None, W["first_step_kept"])]
    P = W["paths"]["ddim/trailing"]
    for i, r in enumerate(W["first_steps"][:5]):
        rows.append((r["step"], f"{r['sigma']:.2f} → {r['sigma_next']:.2f}", r["ddim"], r["exact"], P[i + 1][1]))
    out = ""
    cols = (0, 90, 410, 590, 760)
    for c, hd in zip(cols, ("step", "σ → σ′", "DDIM ×", "exact ×", "kept")):
        out += label(x + c, y, hd, SOFT, "start", head)
    for k, (st, sg, fd, fe, kept) in enumerate(rows):
        yy = y + 56 + k * row_h
        out += mono(x + cols[0], yy, f"{st}", size, MUTED)
        out += mono(x + cols[1], yy, sg, size, INK)
        out += mono(x + cols[2], yy, "—" if fd is None else f"{fd:.4f}", size, INK)
        out += mono(x + cols[3], yy, "—" if fe is None else f"{fe:.4f}", size, MUTED)
        out += mono(x + cols[4], yy, f"{kept:.3f}", size, ACCENT, "start", 600)
    return out, y + 56 + len(rows) * row_h


def feed_02():
    v, bottom = first_steps_table(96, 540, 62)
    P = W["paths"]["ddim/trailing"]
    v += box(96, bottom + 10, 888, 96, ACCENT_TINT, ACCENT, 8, 1.5)
    v += mono(540, bottom + 70, f"after all 50 steps: {P[-1][1]:.3f} — six steps lost {(1 - P[5][1]) * 100:.0f}%",
              26, INK, "middle", 600)
    emit("feed", 2, "where-ddim-loses-the-spread",
         ["DDIM's error is made", "where the path bends."],
         [f"One Gaussian direction, V₀ = {W['v0']:,.2f}, on part 5's 50-step grid:",
          "each DDIM step's factor against the exact path's."],
         v,
         [f"The loss sits within a factor of three of √V₀ = {W['sqrt_v0']:.1f}.",
          "Above and below that, DDIM's assumption costs almost nothing."],
         FEED_TOTAL)


def feed_03():
    S = W["sweeps"]
    at50 = lambda key: next(r["kept"] for r in S[key] if r["nfe"] == 50)
    rows = [("DDIM, part 5's grid", "ddim/trailing", INK), ("DDIM, log-SNR grid", "ddim/logsnr", MUTED),
            ("DPM-Solver++(2M), log-SNR", "dpmpp2m/logsnr", ACCENT)]
    v = label(96, 540, "50 network calls · brightness spread kept", SOFT, "start", 16)
    y = 600
    for name, key, colour in rows:
        k = at50(key)
        v += txt(96, y, name, 30, INK, SANS, 600 if colour == ACCENT else 400)
        v += box(96, y + 18, 640, 34, "rgba(45,49,66,0.06)", "none", 4, 0)
        v += box(96, y + 18, 640 * min(k, 1.0), 34, colour, "none", 4, 0)
        v += mono(760, y + 46, f"{k:.4f}", 28, colour, "start", 600)
        v += mono(96, y + 90, f"error {abs(1 - k) * 100:.2f}% · 1% from NFE {W['nfe_to_1pct'][key]:.0f}", 22, MUTED)
        y += 160
    emit("feed", 3, "same-calls-forty-fold",
         ["Same 50 calls,", "forty times the error."],
         ["Two choices decide it: where the steps go, and what each",
          "step assumes about the denoiser's answer."],
         v,
         ["A second-order method on log-SNR steps reaches 1% in",
          f"{W['nfe_to_1pct']['dpmpp2m/logsnr']:.0f} calls; DDIM on part 5's grid needs {W['nfe_to_1pct']['ddim/trailing']:.0f}."],
         FEED_TOTAL)


def error_plot(x, y, w, h, keys, size=20, label_size=16, slot=46):
    C = ODE["curves"]
    pl = Plot(x, y, w, h, (0, 3), (-7.3, 0.3), logx=True, logy=True)
    out = ""
    out += (f'<clipPath id="plot-clip"><rect x="{x}" y="{y}" width="{w}" height="{h}"/></clipPath>')
    for e in (0, -2, -4, -6):
        out += hline(x, x + w, pl.Y(10.0 ** e), RULE, 1)
        exp = "" if e == 0 else f'<tspan dy="-9" font-size="13">{str(e).replace("-", "−")}</tspan>'
        out += (f'<text x="{x - 14}" y="{pl.Y(10.0 ** e) + 7:.1f}" fill="{SOFT}" font-family="{MONO}" font-size="18" '
                f'text-anchor="end">{"1" if e == 0 else "10"}{exp}</text>')
    out += hline(x, x + w, pl.Y(ODE["grey"]), ACCENT, 2, "10,8")
    for n in (1, 10, 100, 1000):
        out += mono(pl.X(n), y + h + 34, f"{n:,}", 18, SOFT, "middle")
    for key, name, colour in keys:
        pts = [(pl.X(r["nfe"]), pl.Y(r["rms"])) for r in C[key] if r["nfe"] <= 10 ** pl.xr[1]]
        out += f'<g clip-path="url(#plot-clip)">{polyline(pts, colour, 5)}</g>'
        n = NG[key]
        out += f'<circle cx="{pl.X(n):.1f}" cy="{pl.Y(ODE["grey"]):.1f}" r="12" fill="{PAPER}" stroke="{colour}" stroke-width="4"/>'
    ly = y + 20
    for key, name, colour in keys:
        out += mono(x + w + 26, ly, name, size, colour, "start", 600)
        out += mono(x + w + 26, ly + 26, f"{NG[key]} calls", size - 2, MUTED)
        ly += slot + 26
    return out, pl


def feed_04():
    keys = [("ddim/edm7", "DDIM", INK), ("heun/edm7", "Heun", BLUE), ("dpmpp2m/edm7", "DPM++(2M)", ACCENT),
            ("dpm3/edm7", "DPM-Solver-3", MUSTARD)]
    v, pl = error_plot(150, 520, 560, 470, keys)
    v += label(150, 1062, "network calls (log) · rms error vs the exact path (log)", SOFT, "start", 15)
    v += label(150, 1090, "dashed: one 8-bit grey level", ACCENT, "start", 15)
    emit("feed", 4, "order-is-a-slope",
         ["Order is a slope.", "It pays late."],
         ["Distance from the exact endpoint against network calls,",
          "measured with an exact denoiser. Circles: one grey level."],
         v,
         [f"First order needs {NG['ddim/edm7']} calls for one grey level, third",
          f"order {NG['dpm3/edm7']}. Below 10 calls, order is no guarantee."],
         FEED_TOTAL)


def feed_05():
    rows = [("DDIM (η = 0), Euler", "= DPM-Solver-1", "1", "1"),
            ("Euler a, DDIM η = 1", "= DDPM ancestral", "1", "—"),
            ("Heun", "EDM, trapezoid", "2", "2"),
            ("DPM2", "DPM-Solver-2", "2", "2"),
            ("DPM++ 2M", "reuses its last call", "1", "2"),
            ("UniPC", "free corrector", "1", "2–3")]
    v = label(96, 540, "name", SOFT, "start", 16) + label(560, 540, "calls per step", SOFT, "start", 16)
    v += label(820, 540, "order", SOFT, "start", 16)
    y = 610
    for name, what, calls, order in rows:
        hot = name.startswith("DPM++")
        v += txt(96, y, name, 30, ACCENT if hot else INK, SANS, 600 if hot else 400)
        v += mono(96, y + 34, what, 21, MUTED)
        v += mono(600, y + 10, calls, 30, INK, "middle", 600)
        v += mono(860, y + 10, order, 30, INK, "middle", 600)
        y += 84
    emit("feed", 5, "six-names-two-algorithms",
         ["Six names,", "two algorithms."],
         ["DDIM, Euler and DPM-Solver-1 are one update; DDPM's chain and",
          "Euler a are another. The rest add order on top."],
         v,
         ["Count network calls, not steps: 20 Heun steps cost",
          "39 calls; 20 DPM++ 2M steps cost 20."],
         FEED_TOTAL)


def restart_plot(x, y, w, h, size=20, label_size=16):
    pl = Plot(x, y, w, h, (math.log10(30), math.log10(1200)), (1.2, 3.2), logx=True)
    out = ""
    for f in (1.5, 2.0, 2.5, 3.0):
        out += hline(x, x + w, pl.Y(f), RULE, 1)
        out += mono(x - 14, pl.Y(f) + 7, f"{f:.1f}", 18, SOFT, "end")
    for n in (35, 100, 300, 1000):
        out += mono(pl.X(n), y + h + 34, f"{n:,}", 18, SOFT, "middle")
    for (name, colour, dash), pts in zip((("Heun ODE", BLUE, None), ("EDM stochastic", PURPLE, "12,9")),
                                         RESTART_T4.values()):
        out += polyline([(pl.X(n), pl.Y(f)) for n, f in pts], colour, 5, dash)
        for n, f in pts:
            out += f'<circle cx="{pl.X(n):.1f}" cy="{pl.Y(f):.1f}" r="8" fill="{colour}"/>'
    h0, s0 = RESTART_T4["Heun ODE"], RESTART_T4["EDM stochastic"]
    out += mono(pl.X(h0[0][0]) + 14, pl.Y(h0[0][1]) + 34, f"{h0[0][1]:.2f}", size, BLUE, "start", 600)
    out += mono(pl.X(s0[0][0]) + 14, pl.Y(s0[0][1]) - 14, f"{s0[0][1]:.2f}", size, PURPLE, "start", 600)
    out += mono(pl.X(h0[-1][0]), pl.Y(h0[-1][1]) - 22, f"{h0[-1][1]:.2f}", size, BLUE, "end", 600)
    out += mono(pl.X(s0[-1][0]), pl.Y(s0[-1][1]) + 36, f"{s0[-1][1]:.2f}", size, PURPLE, "end", 600)
    out += label(x, y - 26, "imagenet 64×64 · fid · lower is better", SOFT, "start", label_size)
    return out


def feed_06():
    v = restart_plot(150, 560, 780, 400)
    v += polyline([(150, 1068), (210, 1068)], BLUE, 5) + mono(224, 1075, "Heun (ODE)", 21, BLUE)
    v += polyline([(470, 1068), (530, 1068)], PURPLE, 5, "12,9") + mono(544, 1075, "EDM stochastic (SDE)", 21, PURPLE)
    v += label(150, 1110, "network calls (log) · quoted from Xu et al., NeurIPS 2023", SOFT, "start", 15)
    emit("feed", 6, "noise-costs-and-buys",
         ["Noise costs accuracy.", "It buys forgetting."],
         ["Same model, same calls: the deterministic sampler wins",
          "early; the stochastic one wins once calls are plentiful."],
         v,
         ["Fresh noise erases earlier errors, the network's",
          "included, at the price of a larger error per step."],
         FEED_TOTAL)


def feed_07():
    items = [("Order", f"one grey level: {NG['ddim/edm7']} calls for DDIM, {NG['dpm3/edm7']} for third order"),
             ("Placement", "steps belong where the path bends"),
             ("Reuse", "DPM++ 2M: second order at one call per step"),
             ("Noise", "worth it only when calls are plentiful"),
             ("Measure", "error at matched calls, against a reference")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 7, "read-the-article",
         ["1,000 steps", "into 20."],
         ["Samplers as numerical analysis, measured against the",
          "exact path in a lab you can run on a laptop."],
         v,
         ["Pick a sampler and a step count from measured",
          "error at matched calls, not folklore."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = fan(96, 820, 650, 560, 112, 18)
    emit("story", 1, "a-sampler-is-an-ode-solver",
         ["A sampler is an", "ODE solver."],
         ["Solid: the exact path from noise", "to image. Dashed: DDIM, six steps."],
         v,
         ["The step count is an accuracy dial,", "not a property of the model."],
         STORY_TOTAL)


def story_02():
    S = W["sweeps"]
    at50 = lambda key: next(r["kept"] for r in S[key] if r["nfe"] == 50)
    rows = [("DDIM, part 5's grid", "ddim/trailing", INK), ("DDIM, log-SNR grid", "ddim/logsnr", MUTED),
            ("DPM-Solver++(2M), log-SNR", "dpmpp2m/logsnr", ACCENT)]
    v = label(96, 860, "50 calls · brightness spread kept", SOFT, "start", 18)
    y = 940
    for name, key, colour in rows:
        k = at50(key)
        v += txt(96, y, name, 34, INK, SANS, 600 if colour == ACCENT else 400)
        v += box(96, y + 24, 620, 40, "rgba(45,49,66,0.06)", "none", 4, 0)
        v += box(96, y + 24, 620 * min(k, 1.0), 40, colour, "none", 4, 0)
        v += mono(740, y + 56, f"{k:.4f}", 32, colour, "start", 600)
        y += 170
    emit("story", 2, "same-calls-forty-fold",
         ["Same 50 calls,", "forty times the error."],
         ["Where the steps go and what each", "step assumes decide the error."],
         v,
         ["Second order on log-SNR steps:", f"1% error in {W['nfe_to_1pct']['dpmpp2m/logsnr']:.0f} calls, not {W['nfe_to_1pct']['ddim/trailing']:.0f}."],
         STORY_TOTAL)


def story_03():
    keys = [("ddim/edm7", "DDIM", INK), ("heun/edm7", "Heun", BLUE), ("dpmpp2m/edm7", "DPM++(2M)", ACCENT),
            ("dpm3/edm7", "DPM-Solver-3", MUSTARD)]
    v, pl = error_plot(150, 860, 520, 520, keys, 24, 18, 60)
    emit("story", 3, "order-is-a-slope",
         ["Order is a slope.", "It pays late."],
         ["Error against network calls.", "Circles: within one grey level."],
         v,
         [f"{NG['ddim/edm7']} calls for DDIM, {NG['dpm3/edm7']} for", "a third-order solver."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["why fewer steps need no retraining",
             "what DDIM actually computes",
             "how higher order buys accuracy",
             "where the steps should go",
             "when a sampler should add noise"]
    y = 880
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 30, INK, SANS, 400)
        y += 108
    emit("story", 4, "read-the-article",
         ["1,000 steps", "into 20."],
         ["Samplers as numerical analysis,", "measured on a laptop."],
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
