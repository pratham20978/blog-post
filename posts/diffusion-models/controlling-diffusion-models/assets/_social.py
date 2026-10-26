#!/usr/bin/env python3
"""Build the finished Canery feed for "Controlling Diffusion Models: Guidance, ControlNet, LoRA".

Diffusion Models, part 8. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every measured or
computed artefact on a card is read from the lab capture the article ships (../lab/captures.json),
so a card cannot disagree with the post. This part ships feed cards only, no Story frames.

The feed lockup width is 220, which render_social.py locks.
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

from _figures import contrast_of

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("P8_SOCIAL_OUT", HERE / "social"))
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads(pathlib.Path(os.environ.get("P8_CAPTURES", HERE.parent / "lab" / "captures.json"))
                 .read_text(encoding="utf-8"))
W, E, NETS, CN, PER, ED = (CAP["worked"], CAP["exact"], CAP["networks"]["seeds"], CAP["controlnet"],
                           CAP["personal"], CAP["edit"])

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
SAGE = "#7c8f6f"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/controlling-diffusion-models"
FOOTER = "CONTROLLING DIFFUSION MODELS · CANERY.IN"

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


def grey(v, lo=-1.6, hi=3.2):
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




FEED_TOTAL = 8


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


def tile(x, y, size, flat, side=8, stroke=RULE_SOLID, sw=1.5):
    rows = [[grey(flat[r * side + c]) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>'
            + box(x, y, size, size, "none", stroke, 0, sw))


def pc(v):
    """A share as a percentage: whole numbers from 2% up, one decimal below, no trailing zero."""
    s = f"{100 * v:.0f}" if v >= 0.02 else f"{100 * v:.1f}".rstrip("0").rstrip(".")
    return s


def span(vals, fmt, unit=""):
    """Two seeds as 'a–b', or one value when both print the same."""
    a, b = fmt(min(vals)), fmt(max(vals))
    return (a if a == b else f"{a}–{b}") + unit


def seeds(kind, key, field):
    return [NETS[s][kind][key][field] for s in NETS]


FAINT = 0.75                               # halfway between the faint (0.5) and strong (1.0) looks


# ------------------------------------------------------------------ feed
def feed_01():
    S = CAP["samples"]
    size, gx, gy, x0, y0 = 104, 30, 46, 300, 512
    v = label(x0, 484, "four noises that end faint unguided · exact model", SOFT, "start", 15)
    for r, w in enumerate(("1.0", "2.0", "3.0", "5.0")):
        y = y0 + r * (size + gy)
        v += mono(96, y + size / 2 + 9, f"w = {float(w):g}", 26, INK, "start", 600)
        for c in range(4):
            img = S[w][c]
            k = contrast_of(img)
            x = x0 + c * (size + gx)
            v += tile(x, y, size, img, stroke=BLUE if k < FAINT else RULE_SOLID, sw=5 if k < FAINT else 1.5)
            v += mono(x + size / 2, y + size + 24, f"{k:.2f}", 18, BLUE if k < FAINT else SOFT, "middle",
                      600 if k < FAINT else 400)
    v += box(x0, 1112, 22, 22, "none", BLUE, 0, 4) + mono(x0 + 36, 1130, "faint: contrast below 0.75", 18, MUTED)
    emit("feed", 1, "every-control-has-a-price",
         ["Every control", "has a price."],
         ["Guidance, ControlNet, LoRA, inpainting and editing each steer a",
          "diffusion model, and each pays in something you can measure."],
         v,
         [f"With exact denoisers, guidance at w = 3 left {100 * E['weights']['3.0']['faint']:.1f}% of samples faint,",
          f"where the data has {pc(E['data']['faint'])}%. It deletes the less typical look."],
         FEED_TOTAL)


def feed_02():
    rows = [("unconditional denoiser D_u", f"{W['D_uncond']:.3f}", MUTED, False),
            ("conditional denoiser D_c", f"{W['D_cond']:.3f}", MUTED, False),
            (f"guided, w = {W['w']:g}: D_u + {W['w']:g} (D_c − D_u)", f"{W['D_guided']:.3f}", ACCENT, True),
            ("the strongest real crescent", f"{max(W['modes']):g}", INK, True),
            (f"one DDIM step to σ = {W['sigma_next']:.2f}: unguided · conditional · guided",
             f"{W['step_uncond']:.2f} · {W['step_cond']:.2f} · {W['step_guided']:.2f}", MUTED, False)]
    v = label(96, 520, f"one number at σ = {W['sigma']:g}, x = {W['x']:g} · exact denoisers", SOFT, "start", 16)
    y = 600
    for i, (name, val, colour, bold) in enumerate(rows):
        if i == 3:
            v += hline(96, 984, y - 46, RULE, 1)
        if i == 4:
            v += txt(96, y, name, 24, MUTED, SANS, 400)
            v += mono(984, y + 52, val, 30, colour, "end", 600)
            break
        v += txt(96, y, name, 27, INK if bold else MUTED, SANS, 600 if bold else 400)
        v += mono(984, y, val, 30, colour, "end", 600)
        y += 92 if i != 2 else 112
    a, b = W["modes"][2], W["modes"][3]
    emit("feed", 2, "guidance-asks-for-more",
         ["Guidance asks for", "more than exists."],
         [f"One number: how much of the requested crescent an image shows. Its",
          f"real crescents sit at {a:g} (faint) and {b:g} (strong)."],
         v,
         ["The guided target is more than twice the strongest real crescent.",
          "The overshoot fades; the decision it moved stays."],
         FEED_TOTAL)


def feed_03():
    ws = list(E["weights"])
    x0, bw, top = 236, 560, 0.6
    v = label(x0, 500, "faint share", SOFT, "start", 15) + label(1008, 500, "over-saturated", ACCENT, "end", 15)
    y = 556
    for w in ws:
        f, o = E["weights"][w]["faint"], E["weights"][w]["over"]
        v += mono(96, y + 8, f"w = {float(w):g}", 22, INK, "start", 600)
        v += box(x0, y - 16, bw * f / top, 30, BLUE, "none", 3, 0)
        v += mono(x0 + bw * f / top + 14, y + 8, f"{100 * f:.1f}%", 22, BLUE, "start", 600)
        v += mono(1008, y + 8, f"{100 * o:.2f}%", 22, ACCENT, "end", 500)
        y += 76
    xd = x0 + bw * E["data"]["faint"] / top
    v += f'<line x1="{xd:.1f}" y1="522" x2="{xd:.1f}" y2="{y - 40}" stroke="{INK}" stroke-width="2" stroke-dasharray="8,7"/>'
    v += label(xd, y - 6, f"the data: {pc(E['data']['faint'])}%", INK, "middle", 15)
    v += label(96, 1124, "4,096 samples per weight · over-saturated: contrast above 1.185", SOFT, "start", 15)
    emit("feed", 3, "guidance-deletes-the-faint-look",
         ["Guidance deletes", "the faint look."],
         ["Samples of one class from the exact model, whose denoisers have",
          "closed forms, where half of all real crescents are faint."],
         v,
         [f"Sample distance grew from {E['weights']['1.0']['swd']:.3f} unguided to {E['weights']['3.0']['swd']:.3f} at w = 3:",
          "with an ideal denoiser, guidance is strictly harmful."],
         FEED_TOTAL)


def feed_04():
    cols = [(560, "faint"), (770, "blends"), (1008, "distance")]
    v = "".join(label(x, 520, name, SOFT, "end", 15) for x, name in cols)
    rows = [("no guidance", "cfg w=1", INK), ("CFG, w = 3", "cfg w=3", INK), ("autoguidance, w = 2", "auto w=2", ACCENT)]
    y = 600
    for name, key, colour in rows:
        bold = colour == ACCENT
        v += txt(96, y, name, 27, colour if bold else INK, SANS, 600 if bold else 400)
        v += mono(560, y, span(seeds("model", key, "faint"), lambda u: f"{100 * u:.0f}", "%"), 25, colour, "end", 600)
        v += mono(770, y, span(seeds("model", key, "blend"), lambda u: f"{100 * u:.1f}", "%"), 25, colour, "end", 600)
        v += mono(1008, y, span(seeds("model", key, "swd"), lambda u: f"{u:.3f}"), 25, colour, "end", 600)
        y += 92
    v += hline(96, 1008, y - 46, RULE, 1)
    D = E["data"]
    v += txt(96, y + 6, "the data", 27, MUTED, SANS, 400)
    v += mono(560, y + 6, f"{pc(D['faint'])}%", 25, MUTED, "end", 500)
    v += mono(770, y + 6, f"{100 * D['blend']:.2f}%", 25, MUTED, "end", 500)
    v += mono(1008, y + 6, f"{D['swd']:.3f}", 25, MUTED, "end", 500)
    v += label(96, y + 90, "the lab's trained model · two seeds · 4,096 samples each", SOFT, "start", 15)
    v += label(96, y + 120, "blends: half-faint crescents no real image has", SOFT, "start", 15)
    v += label(96, y + 150, "distance: sliced Wasserstein to real images; the data row: two real sets", SOFT, "start", 15)
    emit("feed", 4, "a-weaker-model-is-a-better-guide",
         ["A weaker model", "is a better guide."],
         ["Autoguidance extrapolates away from a copy of the model trained a",
          "quarter as long, not away from its unconditional mode."],
         v,
         ["Autoguidance was the only setting in the lab that improved the",
          "model's sample distance. CFG paid for its cleanup in coverage."],
         FEED_TOTAL)


def feed_05():
    steps = list(CN["zero"]["1"])
    pl = Plot(170, 540, 790, 400, (0, len(steps) - 1), (0, 0.3))

    def mean_of(kind, i, field):
        vals = [CN[kind][s][steps[i]][field] for s in CN[kind]]
        return sum(vals) / len(vals)
    v = label(170, 512, "sample distance to real images · mean of two seeds", SOFT, "start", 15)
    for g in (0, 0.1, 0.2, 0.3):
        v += hline(170, 960, pl.Y(g), RULE_SOLID if g == 0 else RULE, 1.5 if g == 0 else 1)
        v += mono(156, pl.Y(g) + 7, f"{g:g}", 18, SOFT, "end")
    for i, s in enumerate(steps):
        v += mono(pl.X(i), 540 + 400 + 34, f"{int(s):,}", 17, SOFT, "middle")
    for kind, colour, dash in (("gaussian", INK, "14,10"), ("zero", ACCENT, None)):
        pts = [(pl.X(i), pl.Y(mean_of(kind, i, "swd"))) for i in range(len(steps))]
        v += polyline(pts, colour, 5, dash)
        v += "".join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="6" fill="{colour}"/>' for a, b in pts)
    z0, g0 = mean_of("zero", 0, "swd"), mean_of("gaussian", 0, "swd")
    v += mono(pl.X(0) + 22, pl.Y(g0) + 7, f"Gaussian connectors: {g0:.2f}", 20, INK, "start", 600)
    v += mono(pl.X(0) + 22, pl.Y(z0) + 40, f"zero: {z0:.2f}, the frozen model's", 20, ACCENT, "start", 600)
    v += label(170, 1010, "training step", SOFT, "start", 15)
    mz = max(CN["zero"][s]["0"]["max_change"] for s in CN["zero"])
    mg = max(CN["gaussian"][s]["0"]["max_change"] for s in CN["gaussian"])
    v += label(170, 1100, f"largest output change at step 0: zero {mz:g} · Gaussian up to {mg:.1f}", SOFT, "start", 15)
    gs = [CN["gaussian"][s]["0"]["swd"] for s in CN["gaussian"]]
    emit("feed", 5, "controlnet-starts-at-zero",
         ["ControlNet starts", "by changing nothing."],
         ["A trainable copy joins the frozen model through layers whose",
          "weights start at zero, so its first output is the frozen model's."],
         v,
         [f"Gaussian connectors began {span(gs, lambda u: f'{u:.2f}')} from real images, against the",
          f"frozen model's {z0:.2f}. With zeros, no noise reaches the frozen features."],
         FEED_TOTAL)


def feed_06():
    M, last = PER["methods"], str(PER["steps"])
    names = [("ti", "textual inversion"), ("lora", "LoRA"), ("lora+ppl", "LoRA + prior preservation"),
             ("full", "full fine-tune"), ("full+ppl", "full fine-tune + prior")]
    v = label(700, 500, "draws the subject", SOFT, "end", 15) + label(1008, 500, "plain 'crescent 0' drifts", SOFT, "end", 15)
    y = 556
    for key, name in names:
        sub = [M[key][s][last]["subject_share"] for s in M[key]]
        dr = [M[key][s][last]["drift"] for s in M[key]]
        hot = min(dr) > 0.5
        v += txt(96, y, name, 25, INK, SANS, 400)
        v += mono(700, y, span(sub, pc, "%"), 25, INK, "end", 600)
        v += mono(1008, y, span(dr, pc, "%"), 25, ACCENT if hot else INK, "end", 600)
        y += 60
    v += hline(96, 1008, y - 24, RULE, 1)
    fine = ("lora", "lora+ppl", "full", "full+ppl")
    v += label(96, y + 30, "brightness spread of the subject's samples", SOFT, "start", 15)
    v += txt(96, y + 82, "a real thin crescent", 24, MUTED, SANS, 400)
    v += mono(1008, y + 82, f"{CAP['world']['brightness_sd']:.2f}", 25, SAGE, "end", 600)
    yy = y + 134
    for s in M["full"]:
        photos = M["full"][s]["photos_brightness_sd"]
        models = [M[k][s][last]["subject_brightness_sd"] for k in fine]
        v += txt(96, yy, f"seed {s}: its five photos · the four fine-tunes", 24, MUTED, SANS, 400)
        v += mono(1008, yy, f"{photos:.3f} · {span(models, lambda u: f'{u:.2f}')}", 25, ACCENT, "end", 600)
        yy += 52
    emit("feed", 6, "five-photos-teach-the-photos",
         ["Five photos teach", "the photos."],
         [f"The lab fine-tuned its model on five photos of a thinner crescent 0,",
          f"five ways, {int(last):,} steps each, two seeds."],
         v,
         ["Without prior preservation, every plain 'crescent 0' became the",
          "subject. Every fine-tune copied its photos' brightness spread."],
         FEED_TOTAL)


def feed_07():
    tau = CAP["world"]["detail"]
    sd = ED["sdedit"]
    v = txt(96, 548, "kept  =  τ / √(τ² + σ₀²)", 46, INK, SERIF, 400)
    v += mono(1008, 548, f"τ = {tau:g}", 24, MUTED, "end", 500)
    cols = [(560, "ghost left"), (790, "detail kept"), (1008, "closed form")]
    v += label(96, 628, "σ₀", SOFT, "start", 15) + "".join(label(x, 628, n, SOFT, "end", 15) for x, n in cols)
    y = 684
    for s0 in ("0.5", "1.0", "2.0", "4.0"):
        r = sd[s0]
        cf = tau / math.sqrt(tau ** 2 + float(s0) ** 2)
        v += mono(96, y, f"{float(s0):g}", 25, INK, "start", 600)
        v += mono(560, y, f"{r['ghost']:.3f}", 25, ACCENT, "end", 600)
        v += mono(790, y, f"{r['detail_corr']:.3f}", 25, BLUE, "end", 600)
        v += mono(1008, y, f"{cf:.3f}", 25, MUTED, "end", 500)
        y += 58
    v += hline(96, 1008, y - 26, RULE, 1)
    inv = ED["inversion"]
    v += txt(96, y + 14, "DDIM inversion", 25, INK, SANS, 600)
    v += mono(560, y + 14, f"{inv['ghost']:.3f}", 25, ACCENT, "end", 600)
    v += mono(790, y + 14, f"{inv['detail_corr']:.3f}", 25, BLUE, "end", 600)
    v += label(96, y + 92, f"{ED['n']:,} images of crescent {ED['from_class']} edited into crescent {ED['to_class']} · exact denoisers", SOFT, "start", 15)
    v += label(96, y + 122, "ghost: share of the old crescent left · detail: correlation with the source's", SOFT, "start", 15)
    emit("feed", 7, "editing-trades-a-ghost-for-detail",
         ["Editing trades", "a ghost for detail."],
         ["SDEdit noises an image to σ₀ and denoises it as the new class; in",
          "crescent world, what it keeps of the old image has a closed form."],
         v,
         ["No σ₀ keeps the detail without keeping the ghost. DDIM inversion",
          f"escapes the dial: {100 * inv['ghost']:.1f}% of the old crescent left, all of the detail."],
         FEED_TOTAL)


def feed_08():
    items = [("Classifier-free guidance", "pays in coverage: the less typical look goes"),
             ("ControlNet", "361M trained parameters whose output starts at zero"),
             ("LoRA and DreamBooth", "learn the subject; without prior preservation, the class too"),
             ("Inpainting", "coherence, or ten times the calls"),
             ("SDEdit and DDIM inversion", "a ghost, or the inverse path")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 8, "read-the-article",
         ["Every control", "has a price."],
         ["Guidance and its fixes, ControlNet, LoRA, DreamBooth, inpainting and",
          "editing, measured on a laptop in a toy world with exact denoisers."],
         v,
         ["Choosing a knob is choosing what to lose."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
