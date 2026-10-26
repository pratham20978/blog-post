#!/usr/bin/env python3
"""Build the finished Canery feed for "Diffusion Beyond Images: Video, Audio, 3-D and Molecules".

Diffusion Models, part 10. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every measured or computed
artefact on a card is read from the lab capture the article ships (../lab/captures.json), so a card
cannot disagree with the post; the one quoted comparison (feed 05) is typed once below, next to its
ledger key. This part ships feed cards only, no Story frames, as parts 8 and 9 did.

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

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("P10_SOCIAL_OUT", HERE / "social"))
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads(pathlib.Path(os.environ.get("P10_CAPTURES", HERE.parent / "lab" / "captures.json"))
                 .read_text(encoding="utf-8"))
WK, V, FC, SD, CEN = CAP["worked"], CAP["video"], CAP["forecast"], CAP["sds"], CAP["census"]

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
BLUE = "#5e7a9b"
MUSTARD = "#b8915a"
SAGE = "#7c8f6f"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/diffusion-beyond-images"
FOOTER = "DIFFUSION BEYOND IMAGES · CANERY.IN"

# quoted, not measured: Hoogeboom et al. 2022 (EDM), Table 1, QM9, molecule stability (ledger L44)
EDM = {"no equivariance": 63.2, "random rotations in training": 71.6, "equivariant network": 82.0, "training data": 95.2}

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


def txt(x, y, value, size=22, fill=INK, family=SANS, weight=400, anchor="start", track=None, italic=False):
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
    return "".join(txt(x, y + i * gap, v, size, fill, family, weight, anchor) for i, v in enumerate(values))


def box(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.28)", rx=8, sw=1):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def circle(cx, cy, r, fill=INK, stroke=None, sw=3):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{s}/>'


def polyline(pts, colour, width=5, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return ('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts)
            + f'" fill="none" stroke="{colour}" stroke-width="{width}" stroke-linejoin="round" '
            f'stroke-linecap="round"{d}/>')


def grey(v, lo=-2.0, hi=2.6):
    """High value = bright, the series' display convention; the same range as the article's tiles."""
    u = min(1.0, max(0.0, (v - lo) / (hi - lo)))
    return round(26 + u * (250 - 26))


def png_gray(rows):
    """A greyscale PNG from rows of 0..255 ints, stdlib only."""
    import base64
    import struct
    import zlib
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(r) for r in rows)

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    return "data:image/png;base64," + base64.b64encode(png).decode()


def tile(x, y, size, flat, side=8, stroke=RULE_SOLID, sw=1.5):
    rows = [[grey(flat[r * side + c]) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>' + box(x, y, size, size, "none", stroke, 0, sw))


def f3(v):
    return f"{v:.4f}" if 0 < v < 0.001 else f"{v:.3f}"


def pc(v, digits=1):
    return f"{100 * v:.{digits}f}%"


# ------------------------------------------------------------------ the shell
def shell(kind, number, total, title, deck, visual, takeaway, cta=None):
    height, logo_y, logo_w = 1350, 72, 220
    rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
    deck_y = title_y + len(title) * title_gap + 20
    take_rule, take_y, foot_y = 1168, 1220, 1305
    scale = logo_w / LOCKUP_FULL_W
    defs = f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style></defs>'
    body = f'<rect width="{VW}" height="{height}" fill="{PAPER}"/>'
    body += (f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
             f'data-logo-width="{logo_w}" fill="{INK}" '
             f'transform="translate(72 {logo_y}) scale({scale})">{LOGO_PATHS}</g>')
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", SOFT, "end", 15)
    body += hline(72, 1008, rule_y)
    body += lines(72, title_y, title, title_size, SERIF, gap=title_gap)
    body += lines(72, deck_y, deck, 22, fill=MUTED, gap=30)
    body += visual
    body += hline(72, 1008, take_rule)
    body += lines(72, take_y, takeaway, 22, weight=600, gap=30)
    body += label(72, foot_y, cta or FOOTER, ACCENT if cta else SOFT, "start", 14)
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
S = V["schemes"]


def size_of(label_start):
    return next(d["numbers"] for d in CEN["sizes"] if d["label"].startswith(label_start))


# ------------------------------------------------------------------ feed
def feed_01():
    size, gap, x0 = 168, 22, 72
    v = ""
    for r, (key, name) in enumerate((("joint", "one denoiser for the whole clip"),
                                     ("independent", "one frame at a time, fresh noise"))):
        y = 534 + r * 316
        v += label(x0, y - 22, name, ACCENT if r == 0 else SOFT, "start", 15)
        for c, img in enumerate(S[key]["_example"][0]):
            v += tile(x0 + c * (size + gap), y, size, img)
        v += label(1008, y + 62, "coherent clips", MUTED, "end", 16)
        v += txt(1008, y + 122, pc(S[key]["coherent_clips"]), 54, ACCENT if r == 0 else INK, SANS, 600, "end")
    emit("feed", 1, "every-frame-right-video-wrong",
         ["Every frame right,", "the video wrong."],
         [f"Sampled frame by frame, an image diffusion model draws valid crescents",
          f"in {pc(S['independent']['valid_frames'])} of frames, and not one coherent clip in {V['n']:,}."],
         v,
         ["The noise step never sees the data's shape. What changes off the",
          "image grid is what the denoiser must see across."],
         FEED_TOTAL)


def feed_02():
    tl = WK["top_left"]
    v = box(72, 500, 936, 120, "#ffffff", RULE_SOLID)
    v += label(100, 540, "one forward step, the top-left value", SOFT, "start", 15)
    v += mono(100, 592, f"0.8 × {tl['x0']:.2f} + 0.6 × ({tl['eps']:.2f}) = {tl['xt']:.2f}".replace("-", "−"),
              34, INK, "start", 600)
    rows = [("an image", "respect its 2-D neighbours"),
            ("a waveform", f"reach far: 1 s is {WK['audio']['per_second']:,} samples"),
            ("a clip", f"frames differ {WK['video']['mean_abs_change_clean']:.3f} clean, "
                       f"{WK['video']['mean_abs_change_noisy']:.3f} noised"),
            ("8 points", f"ignore order ({WK['points']['orderings']:,} listings) and position")]
    y = 690
    for head, body in rows:
        v += txt(100, y, head, 32, INK, SERIF, 400)
        v += mono(330, y - 2, body, 21, MUTED)
        v += hline(100, 1008, y + 30, RULE, 1)
        y += 104
    emit("feed", 2, "the-noise-step-is-shape-blind",
         ["The noise step", "is shape-blind."],
         ["Part 1's 16 numbers, noised once. The same arithmetic, whether they",
          "are an image, a waveform, a clip or a set of points."],
         v,
         ["Same sixteen multiply-adds, four different jobs for the denoiser."],
         FEED_TOTAL)


def feed_03():
    rows = [("independent", "independent noise"), ("mixed 0.5", "mixed noise, ρ = 0.5"), ("mixed 0.9", "mixed noise, ρ = 0.9"),
            ("mixed 0.99", "mixed noise, ρ = 0.99"), ("shared", "shared noise")]
    x_bar, bw = 470, 400
    v = label(96, 506, "share of frame changes", SOFT, "start", 15)
    v += box(x_bar, 494, 16, 14, ACCENT, "none", 2, 0) + mono(x_bar + 26, 507, "brightness flicker", 17, MUTED)
    v += box(x_bar + 250, 494, 16, 14, INK, "none", 2, 0) + mono(x_bar + 276, 507, "no turn", 17, MUTED)
    y = 560
    for key, name in rows:
        st = S[key]
        v += txt(96, y + 24, name, 26, INK, SANS, 500)
        if st["flicker"] > 0:
            v += box(x_bar, y, max(3, bw * st["flicker"]), 18, ACCENT, "none", 3, 0)
        v += mono(x_bar + bw + 16, y + 16, pc(st["flicker"]), 19, ACCENT, "start", 600)
        if st["frozen_turns"] > 0:
            v += box(x_bar, y + 24, max(3, bw * st["frozen_turns"]), 18, INK, "none", 3, 0)
        v += mono(x_bar + bw + 16, y + 40, pc(st["frozen_turns"]), 19, INK, "start", 600)
        y += 76
    v += hline(96, 1008, y + 2, RULE_SOLID, 1)
    for key, name in (("warped", "warped noise"), ("joint", "joint model")):
        y += 52
        v += txt(96, y, name, 26, INK, SANS, 600)
        v += mono(1008, y, f"coherent clips {pc(S[key]['coherent_clips'])}", 24, ACCENT, "end", 600)
    emit("feed", 3, "correlated-noise-freezes",
         ["Correlated noise", "freezes, not moves."],
         ["Share noise between frames and the flicker stops, but so does the",
          "motion. Turning the noise a quarter turn per frame makes it turn."],
         v,
         [f"No correlation gave a coherent clip; warped noise gave {pc(S['warped']['coherent_clips'])}, the joint",
          f"model {pc(S['joint']['coherent_clips'])}. A video model has to see the other frames."],
         FEED_TOTAL)


def feed_04():
    wav = size_of("10 s of audio at 16 kHz")
    mel = size_of("same 10 s as a 64-band mel")
    lat = size_of("same 10 s as AudioLDM's latent")
    rf = CEN["receptive_field"]
    full = 880
    v = label(96, 506, "one 10-second clip at 16 kHz, lengths to scale", SOFT, "start", 15)
    y = 570
    for name, n, colour in (("waveform", wav, INK), ("mel spectrogram", mel, BLUE), ("AudioLDM latent", lat, ACCENT)):
        v += txt(96, y, f"{name} · {n:,}", 28, colour, SANS, 600)
        v += box(96, y + 18, full * n / wav, 40, colour, "none", 4, 0)
        y += 170
    reach = full * rf["samples"] / wav
    v += f'<path d="M96,{570 + 66} V{570 + 76} H{96 + reach:.1f} V{570 + 66}" fill="none" stroke="{ACCENT}" stroke-width="3"/>'
    v += mono(96 + reach + 14, 570 + 82, f"DiffWave's reach: {rf['samples']:,} samples, {rf['seconds_at_16k']:.2f} s", 18, ACCENT)
    v += mono(96, 1100, "the spectrogram drops phase; a vocoder puts a waveform back", 19, MUTED)
    emit("feed", 4, "sound-is-one-long-axis",
         ["Sound is one", "long axis."],
         [f"One second of speech at 16 kHz is {size_of('1 s of speech'):,} samples. Most audio models",
          "shorten the axis before they diffuse."],
         v,
         [f"AudioLDM diffuses 10 s in {lat:,} numbers; Stable Audio's latent holds",
          f"95.1 s of stereo in {CEN['compression']['audio_stable_audio']:.0f} times fewer numbers than the audio."],
         FEED_TOTAL)


def feed_05():
    x_bar, bw = 96, 760
    v = label(96, 506, "QM9 · stable molecules, same network and data · quoted", SOFT, "start", 15)
    y = 560
    colours = {"no equivariance": INK, "random rotations in training": BLUE, "equivariant network": ACCENT,
               "training data": SOFT}
    for name, val in EDM.items():
        v += txt(96, y, name, 26, INK, SANS, 600 if name == "equivariant network" else 500)
        v += box(x_bar, y + 16, bw * val / 100, 30, colours[name], "none", 4, 0)
        v += mono(x_bar + bw * val / 100 + 14, y + 40, f"{val:.1f}%", 22, colours[name], "start", 600)
        y += 126
    gap = (EDM["equivariant network"] - EDM["no equivariance"]) / (EDM["training data"] - EDM["no equivariance"])
    v += mono(96, y + 4, "Hoogeboom et al., ICML 2022, Table 1: 10,000 molecules per model", 17, MUTED)
    emit("feed", 5, "rotate-a-molecule",
         ["Rotate a molecule:", "same molecule."],
         ["A denoiser for 3-D molecules has to treat every orientation alike.",
          "EDM tested three ways on QM9, with the same network and data."],
         v,
         [f"Equivariance closed {100 * gap:.0f}% of the gap to the data. At larger scale and",
          "on other tasks, AlphaFold 3 and MCF did well without it."],
         FEED_TOTAL)


def feed_06():
    W1, W101 = SD["weights"]["1.0"], SD["weights"]["101.0"]
    real = SD["real"]
    size, gap, x0 = 168, 22, 72
    v = ""
    for r, (side, name) in enumerate((("sds", "four SDS runs, w = 1"), ("ancestral", "four ancestral samples, w = 1"))):
        y = 534 + r * 270
        v += mono(x0, y - 22, name, 17, ACCENT if side == "sds" else SOFT, "start", 500)
        for c, img in enumerate(W1[side]["_example"]):
            v += tile(x0 + c * (size + gap), y, size, img)
    v += label(1008, 600, "brightness spread", MUTED, "end", 15)
    v += txt(1008, 656, f"{W1['sds']['brightness_sd']:.3f}", 46, ACCENT, SANS, 600, "end")
    v += label(1008, 870, "brightness spread", MUTED, "end", 15)
    v += txt(1008, 926, f"{W1['ancestral']['brightness_sd']:.2f}", 46, INK, SANS, 600, "end")
    v += mono(72, 1100, f"at w = 101: contrast {W101['sds']['contrast_mean']:.2f}; real strong crescents "
                        f"{real['contrast_strong_mean']:.2f}", 20, MUTED)
    emit("feed", 6, "sds-returns-modes",
         ["SDS returns modes,", "not samples."],
         ["Score distillation builds 3-D objects by optimizing their renders",
          "against a 2-D model. On crescent world every run lands alike."],
         v,
         [f"Brightness spread {W1['sds']['brightness_sd']:.3f} against {W1['ancestral']['brightness_sd']:.2f} for ancestral samples;",
          f"at DreamFusion's w = 101, a contrast of {W101['sds']['contrast_mean']:.2f}, more than twice a real one."],
         FEED_TOTAL)


def feed_07():
    O = FC["observed"]
    x0, x1, y0, y1 = 150, 1000, 540, 1000

    def Y(p):
        assert 0 <= p <= 1
        return y1 - p * (y1 - y0)

    v = hline(x0, x1, y1, RULE_SOLID, 2)
    for t in (0.0, 0.5, 1.0):
        v += (hline(x0, x1, Y(t), RULE, 1) if t == 0.5 else "") + mono(x0 - 16, Y(t) + 7, f"{int(100 * t)}%", 18, SOFT, "end")
    for i, k in enumerate(("1", "2", "3")):
        cx = x0 + 140 + i * 280
        for off, side, colour in ((-58, "replacement", ACCENT), (8, "exact", INK)):
            val = O[k][side]["coherent_clips"]
            v += box(cx + off, Y(val), 50, Y(0) - Y(val), colour, "none", 3, 0)
            v += mono(cx + off + 25, Y(val) - 12, pc(val, 0), 20, colour, "middle", 600)
        v += mono(cx, y1 + 34, f"{k} observed", 19, SOFT, "middle")
    v += box(150, 1072, 16, 14, ACCENT, "none", 2, 0) + mono(176, 1085, "replacement", 18, MUTED)
    v += box(400, 1072, 16, 14, INK, "none", 2, 0) + mono(426, 1085, "exact conditioning", 18, MUTED)
    r1 = O["1"]["replacement"]
    emit("feed", 7, "forecasting-is-inpainting",
         ["Forecasting is", "inpainting in time."],
         ["Predict the rest of a clip from its first frames. Forcing the known",
          "frames into the noisy input is not the same as conditioning on them."],
         v,
         [f"From one frame, replacement continued {pc(r1['coherent_clips'], 0)} of clips coherently; exact",
          f"conditioning {pc(O['1']['exact']['coherent_clips'])}. Brightness went first: kept in only {pc(r1['keeps_brightness'], 0)}."],
         FEED_TOTAL)


def feed_08():
    items = [("A new axis", "frames, samples and steps generated together"),
             ("Symmetry", "point order, rotation and translation"),
             ("Circles", "angles and rotations: noise that wraps ends uniform"),
             ("Scale", f"latents shrink audio {CEN['compression']['audio_stable_audio']:.0f}× and video "
                       f"{CEN['compression']['video_svd']:.0f}× (Stable Audio, SVD)"),
             ("What is given", "condition on it; don't force it into the noisy input")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 8, "read-the-article",
         ["What changes", "off the grid."],
         ["Video, audio, 3-D, molecules and time series, through one recipe",
          "whose noise step never changes."],
         v,
         ["Pick the representation and the symmetries before the network."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
