#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Training a Diffusion Model: The
Decisions Before Step One".

Diffusion Models, part 5. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every artefact on a
card is read from the lab capture the article ships (../lab/captures.json) or quoted from the
article, so a card cannot disagree with the post.

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
SCHED, LEAK, TRAIN = CAP["schedules"]["schedules"], CAP["leak"], CAP.get("train")
A_T = SCHED["scaled_linear"]["sqrt_abar_T"]        # 0.068265: SD's signal coefficient at t = T
S_T = math.sqrt(1 - A_T ** 2)
S_B, TAU = LEAK["s_b"], LEAK["tau"]

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
CANONICAL = "canery.in/blogs/training-a-diffusion-model"
FOOTER = "TRAINING A DIFFUSION MODEL · CANERY.IN"


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


def tile(x, y, size, M, lo=-1.6, hi=1.6):
    rows = [[grey(v, lo, hi) for v in row] for row in M]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>'
            + box(x, y, size, size, "none", RULE_SOLID, 0, 1))


def leak_tiles(x, y, size, gap, n, label_size=16, num_size=20):
    """The same starting noise sampled through two schedules, each tile's brightness printed under it."""
    r = LEAK["by_resolution"]["128"]["variants"]
    rows = [("same noise · last step pure noise (rescaled)", r["zero_snr_trailing_noise"]["previews_32"], INK),
            ("same noise · Stable Diffusion's schedule", r["sd_trailing_noise"]["previews_32"], ACCENT)]
    out, yy = "", y
    for lab, prev, colour in rows:
        out += label(x, yy - 14, lab, colour, "start", label_size)
        for j, M in enumerate(prev[:n]):
            out += tile(x + j * (size + gap), yy, size, M)
            b = sum(map(sum, M)) / (len(M) * len(M[0]))
            out += mono(x + j * (size + gap) + size / 2, yy + size + num_size + 8, f"{b:+.2f}".replace("-", "−"),
                        num_size, colour, "middle", 600)
        yy += size + num_size + 80
    return out, yy - 80 + num_size


def leak_bars(x, y, w, row_h, size=22):
    """The mean's leak, in noise standard deviations, at four sizes."""
    m0 = -0.1625                                        # part 1's patch mean (context.md)
    rows = [(16, "16 · part 1's 4×4 patch"), (256, "256 · 16×16"), (4096, "4,096 · 64×64"),
            (16384, "16,384 · SD's 4×64×64 latent")]
    vmax = 1.6
    out = ""
    one = x + w / vmax
    dash = f'stroke="{INK}" stroke-width="2" stroke-dasharray="8,7"'
    for k, (n, lab) in enumerate(rows):
        yy = y + k * row_h
        last = k == len(rows) - 1                       # the last segment runs on down to its label
        out += f'<line x1="{one:.1f}" y1="{yy + 6}" x2="{one:.1f}" y2="{y + len(rows) * row_h - 20 if last else yy + 56}" {dash}/>'
        z = abs(A_T * m0) / (S_T / math.sqrt(n))
        hot = n == 16384
        out += mono(x, yy, lab, size, INK if hot else MUTED, "start", 600 if hot else 400)
        out += box(x, yy + 14, w, 34, "rgba(45,49,66,0.05)", "none", 4, 0)
        out += box(x, yy + 14, max(4, w * min(z, vmax) / vmax), 34, ACCENT if hot else "rgba(45,49,66,0.55)",
                   "none", 4, 0)
        lx = x + w * min(z, vmax) / vmax + 14
        if abs(lx + 50 - one) < 70:
            lx = one + 14
        out += box(lx - 6, yy + 18, 150, 28, PAPER, "none", 3, 0)
        out += mono(lx, yy + 41, f"{z:.2f} s.d.", size, INK, "start", 600)
    out += mono(one, y + len(rows) * row_h + 10, "1 noise s.d.", size - 2, INK, "middle", 600)
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    v, bottom = leak_tiles(96, 560, 128, 24, 6)
    var = LEAK["by_resolution"]["128"]["variants"]
    v += box(96, bottom + 40, 888, 120, ACCENT_TINT, ACCENT, 8, 1.5)
    v += mono(540, bottom + 92, f"brightness spread kept: {100 * var['sd_trailing_noise']['std_ratio']:.1f}%",
              30, INK, "middle", 600)
    v += mono(540, bottom + 132, f"rescaled: {100 * var['zero_snr_trailing_noise']['std_ratio']:.1f}% "
              "with 50 steps, toward 100% with more", 21, MUTED, "middle")
    emit("feed", 1, "the-last-step-is-not-noise",
         ["Stable Diffusion's last", "step isn't pure noise."],
         [f"Its last training input is {A_T:.3f}·x₀ + {S_T:.3f}·ε. Train on",
          "that and even a perfect denoiser pulls brightness to the middle."],
         v,
         ["The flaw is the schedule's endpoint, not the network:",
          "measured with an exact denoiser at 16,384 pixels."],
         FEED_TOTAL)


def feed_02():
    v = leak_bars(96, 560, 600, 132)
    emit("feed", 2, "the-leak-lives-in-the-mean",
         ["The leak lives", "in the mean."],
         ["The last step keeps 6.8% of the image's amplitude. Averaging",
          "n values shrinks the noise in their mean by √n, not the signal."],
         v,
         ["The same leaked mean is 0.04 noise s.d. in a 4×4 patch",
          "and 1.42 s.d. in Stable Diffusion's 16,384-value latent."],
         FEED_TOTAL)


def feed_03():
    rows = LEAK["steps_sweep"]["rows"]
    pl = Plot(150, 540, 780, 470, (math.log2(20), math.log2(250)), (0, 1.1))
    v = ""
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        v += hline(pl.x, pl.x + pl.w, pl.Y(t), RULE, 1)
        v += mono(pl.x - 18, pl.Y(t) + 7, f"{t:.2f}", 18, SOFT, "end")
    pred = 1 / math.sqrt(1 - A_T ** 2 + A_T ** 2 * (16384 * S_B ** 2 + TAU ** 2))
    v += hline(pl.x, pl.x + pl.w, pl.Y(pred), INK, 2, "10,8")
    v += mono(pl.x + pl.w, pl.Y(pred) - 18, f"closed form {pred:.3f}", 20, INK, "end", 600)
    for key, colour, dy in (("sd_trailing_noise", INK, 44), ("zero_snr_trailing_noise", ACCENT, -22)):
        pts = [(pl.X(math.log2(r["steps"])), pl.Y(r[key])) for r in rows]
        v += ('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
              + f'" fill="none" stroke="{colour}" stroke-width="5" stroke-linejoin="round"/>')
        for (a, b), r in zip(pts, rows):
            v += f'<circle cx="{a:.1f}" cy="{b:.1f}" r="11" fill="{colour}"/>'
            v += mono(a, b + dy, f"{r[key]:.3f}", 22, colour, "middle", 600)
    for r in rows:
        v += mono(pl.X(math.log2(r["steps"])), pl.y + pl.h + 40, str(r["steps"]), 20, SOFT, "middle")
    v += label(pl.x, pl.y + pl.h + 84, "sampling steps · 16,384 pixels · exact denoiser", SOFT, "start", 15)
    v += label(pl.x, pl.y - 26, "zero terminal SNR", ACCENT, "start", 16)
    v += label(pl.x, pl.Y(pred) + 92, "Stable Diffusion's schedule", INK, "start", 16)
    emit("feed", 3, "more-steps-cannot-fix-it",
         ["More sampling steps", "can't fix it."],
         ["Fraction of the data's brightness spread that samples keep,",
          "for 25 to 200 deterministic sampling steps."],
         v,
         ["A training/sampling mismatch is a fixed point. After the",
          "rescale, what is left is ordinary sampler error."],
         FEED_TOTAL)


def feed_04():
    code = ["r = abar.sqrt()", "r0, rT = r[0], r[-1]", "r = (r - rT) * r0 / (r0 - rT)", "abar = r ** 2"]
    v = box(96, 520, 888, 250, "#ffffff", "rgba(45,49,66,0.28)", 8, 1)
    for i, line in enumerate(code):
        v += mono(132, 584 + i * 52, line, 30, INK)
    sl = SCHED["scaled_linear"]
    r0 = math.sqrt(1 / (1 + math.exp(-sl["logsnr_first"])))     # √ᾱ at the first step, 0.999575
    mid = ((0.8 - A_T) * r0 / (r0 - A_T)) ** 2                  # the series' running level, √ᾱ = 0.8
    items = [("in the middle", f"ᾱ = 0.640 → {mid:.3f}"),
             ("at the last step", f"ᾱ = {sl['sqrt_abar_T'] ** 2:.5f} → 0"),
             ("then", "predict v, start at t = T, sample via x₀")]
    y = 840
    for head, body in items:
        v += label(96, y, head, ACCENT, "start", 16)
        v += mono(96, y + 42, body, 28, INK, "start", 600)
        y += 104
    emit("feed", 4, "the-fix-is-four-lines",
         ["The fix is", "four lines."],
         ["Lin et al.: keep √ᾱ at the first step, move it to zero at",
          "the last, and rescale every step between linearly."],
         v,
         ["It barely moves the middle of the schedule and makes",
          "the last training input pure noise."],
         FEED_TOTAL)


def feed_05():
    pl = Plot(150, 540, 780, 460, (-10, 10), (math.log10(0.005), math.log10(200)))
    v = ""
    for val, lab in ((0.01, "0.01"), (0.1, "0.1"), (1, "1"), (10, "10"), (100, "100")):
        y = pl.Y(math.log10(val))
        v += hline(pl.x, pl.x + pl.w, y, RULE, 1)
        v += mono(pl.x - 18, y + 7, lab, 18, SOFT, "end")
    for lv in (-10, -5, 0, 5, 10):
        v += mono(pl.X(lv), pl.y + pl.h + 38, str(lv).replace("-", "−"), 18, SOFT, "middle")
    v += label(pl.x, pl.y + pl.h + 80, "log-SNR λ   ← noisier · cleaner →", SOFT, "start", 15)

    def sig(z):
        return 1 / (1 + math.exp(-z))
    for fn, colour, name, at in ((lambda l: math.exp(-l / 2), INK, "ε output", -5.0),
                                 (lambda l: 1.0, BLUE, "x₀ output", 6.0),
                                 (lambda l: math.sqrt(1 - sig(l)), ACCENT, "v output", 4.5)):
        pts = [(pl.X(l), pl.Y(math.log10(fn(l)))) for l in [-10 + i * 0.1 for i in range(201)]
               if pl.y <= pl.Y(math.log10(fn(l))) <= pl.y + pl.h]
        v += ('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
              + f'" fill="none" stroke="{colour}" stroke-width="5" stroke-linejoin="round"/>')
        yy = pl.Y(math.log10(fn(at)))
        dy = 36 if name.startswith("ε") else -46          # the ε label sits below its steep line
        v += box(pl.X(at) + 10, yy + dy, 170, 34, PAPER, "none", 3, 0)
        v += mono(pl.X(at) + 18, yy + dy + 25, name, 24, colour, "start", 600)
    v += f'<circle cx="{pl.X(-9):.1f}" cy="{pl.Y(math.log10(math.exp(4.5))):.1f}" r="11" fill="{INK}"/>'
    v += mono(pl.X(-9) + 24, pl.Y(math.log10(math.exp(4.5))) + 8, "×90 at λ = −9", 24, INK, "start", 600)
    emit("feed", 5, "same-answer-different-amplifier",
         ["ε, x₀ or v: same", "answer, new amplifier."],
         ["How much an output error grows on its way into the",
          "clean-image estimate a sampler uses, by target."],
         v,
         ["v never amplifies an error by more than one, and it",
          "survives a zero-SNR last step, where ε divides by zero."],
         FEED_TOTAL)


def weighting_table(x, y, col, size=24):
    rows = [("constant", "const", BLUE), ("Min-SNR-5", "minsnr5", ACCENT), ("SNR (ε-loss)", "snr", INK)]
    lam = TRAIN["lam_grid"]
    i0, i9 = lam.index(-9.0), lam.index(9.0)
    mm = TRAIN["runs"][0]["mmse_x0"]
    out = label(x, y, "weighting", SOFT, "start", 15)
    heads = ["λ = −9 · noisiest", "λ = +9 · cleanest", "samples"]
    for j, h in enumerate(heads):
        out += label(x + col[j], y, h, SOFT, "start", 15)
    for k, (name, key, colour) in enumerate(rows):
        yy = y + 76 + k * 112
        rs = [r for r in TRAIN["runs"] if r["config"]["exp"] == "weighting" and r["config"]["weighting"] == key]
        cur = [sum(r["checkpoints"]["40000"]["raw"]["excess"][i] for r in rs) / len(rs) for i in (i0, i9)]
        vals = [r["checkpoints"]["40000"]["power_0.1"]["swd"] for r in rs]
        ok = sorted(v for v in vals if v is not None and v <= 10)
        out += txt(x, yy, name, 34, colour, SERIF, 400)
        out += mono(x + col[0], yy, f"{cur[0]:.4f}" if cur[0] < 0.1 else f"{cur[0]:.2f}", size, INK, "start", 600)
        out += mono(x + col[1], yy, f"{cur[1]:.4f}", size, INK, "start", 600)
        out += mono(x + col[2], yy, f"{ok[len(ok) // 2]:.3f}" if len(ok) == 3 else "blew up", size,
                    INK if len(ok) == 3 else ACCENT, "start", 600)
    out += hline(x, x + 888, y + 76 + 3 * 112 - 40, RULE, 1)
    out += mono(x, y + 76 + 3 * 112, "exact denoiser's error", 20, MUTED)
    out += mono(x + col[0], y + 76 + 3 * 112, f"{mm[i0]:.2f}", 20, MUTED)
    out += mono(x + col[1], y + 76 + 3 * 112, f"{mm[i9]:.4f}", 20, MUTED)
    floor = TRAIN["floors"]["swd"]
    out += mono(x, y + 76 + 3 * 112 + 84, "samples: median sliced distance to the data, lower is better;", 20, MUTED)
    out += mono(x, y + 76 + 3 * 112 + 116, f"two independent draws of the data score {floor:.3f}.", 20, MUTED)
    return out


def feed_06():
    v = weighting_table(96, 540, (330, 560, 780))
    emit("feed", 6, "a-weighting-is-a-budget",
         ["A loss weighting is", "a capacity budget."],
         ["Excess error over the exact denoiser at the two ends of",
          "the noise range: x₀-network, three seeds, 40,000 steps."],
         v,
         ["One network can't win everywhere. SNR weighting starved",
          "the noise levels every sampler starts from."],
         FEED_TOTAL)


def feed_07():
    items = [("Schedule", "its endpoints and density; resolution shifts it"),
             ("Endpoint", "SD's last step keeps 6.8% of the image's amplitude"),
             ("Target", "an ε error grows ×90 at λ = −9; v's never grows"),
             ("Weighting", "it decides which noise levels the network gets right"),
             ("EMA", "a decay of 0.9999 is a 6,931-step half-life")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 7, "read-the-article",
         ["Decide before", "step one."],
         ["Five training decisions, each tested in a lab you",
          "can run on a laptop."],
         v,
         ["Each is one config line, fixed before the first gradient",
          "step and paid for in every step after."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v, bottom = leak_tiles(96, 880, 200, 28, 4, 18, 26)
    sd = LEAK["by_resolution"]["128"]["variants"]["sd_trailing_noise"]
    emit("story", 1, "the-last-step-is-not-noise",
         ["Stable Diffusion's last", "step isn't noise."],
         ["A perfect denoiser on its schedule", f"keeps {100 * sd['std_ratio']:.0f}% of the data's brightness spread."],
         v,
         ["The endpoint, not the network,", "pulls every image to the middle."],
         STORY_TOTAL)


def story_02():
    v = leak_bars(96, 860, 520, 150, 26)
    emit("story", 2, "the-leak-lives-in-the-mean",
         ["The leak lives", "in the mean."],
         ["Average n values: the noise in", "their mean shrinks by √n."],
         v,
         ["Hidden in a 4×4 patch,", "readable in a 4×64×64 latent."],
         STORY_TOTAL)


def story_03():
    rs = [r for r in TRAIN["runs"] if r["config"]["exp"] == "weighting" and r["config"]["weighting"] != "snr"]

    def med(model, ck):
        vals = sorted(r["checkpoints"][ck][model]["swd"] for r in rs
                      if r["checkpoints"][ck][model]["swd"] is not None and r["checkpoints"][ck][model]["swd"] <= 10)
        m = len(vals) // 2
        return vals[m] if len(vals) % 2 else (vals[m - 1] + vals[m]) / 2
    v = box(72, 820, 936, 560, "#ffffff", RULE_SOLID)
    v += label(120, 890, "EMA decay 0.9999 · half-life 6,931 steps", INK, "start", 18)
    rows = [("after 5,000 steps", f"{100 * 0.9999 ** 5000:.0f}% of it is the random start",
             f"samples {med('ema_0.9999', '5000') / med('raw', '5000'):.1f}× further from the data than raw"),
            ("after 40,000 steps", f"{100 * 0.9999 ** 40000:.1f}% of it is the random start",
             f"distance {med('ema_0.9999', '40000'):.2f} against raw {med('raw', '40000'):.2f}")]
    y = 980
    for head, a, b in rows:
        v += txt(120, y, head, 40, INK, SERIF, 400)
        v += mono(120, y + 56, a, 26, ACCENT, "start", 600)
        v += mono(120, y + 100, b, 24, MUTED)
        y += 210
    emit("story", 3, "an-ema-is-a-half-life",
         ["An EMA decay", "is a half-life."],
         ["Half of a 0.9999 average's weight", "sits on the last 6,931 steps."],
         v,
         ["Match the average to the run,", "or use a power-function EMA."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["the schedule: endpoints and density",
             "the endpoint: the leak in the mean",
             "the target: ε, x₀, v and capacity",
             "the weighting: a capacity budget",
             "the EMA, and how training scales"]
    y = 880
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 30, INK, SANS, 600 if i == 1 else 400)
        y += 108
    emit("story", 4, "read-the-article",
         ["Decide before", "step one."],
         ["Five decisions, each tested in", "a lab you can run on a laptop."],
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
