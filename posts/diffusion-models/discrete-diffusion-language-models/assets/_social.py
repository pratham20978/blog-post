#!/usr/bin/env python3
"""Build the finished Canery feed for "Discrete Diffusion Language Models: Masks, LLaDA, Samplers".

Diffusion Models, part 11. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every measured or computed
artefact on a card is read from the lab capture the article ships (../lab/captures.json), so a card
cannot disagree with the post; the two quoted comparisons (feed 05 and 07) are typed once below, next to
their ledger keys. This part ships feed cards only, no Story frames, as parts 8 to 10 did.

The feed lockup width is 220, which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = pathlib.Path(os.environ.get("P11_SOCIAL_OUT", HERE / "social"))
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads(pathlib.Path(os.environ.get("P11_CAPTURES", HERE.parent / "lab" / "captures.json"))
                 .read_text(encoding="utf-8"))
WK, WD, DC, PR = CAP["worked"], CAP["world"], CAP["decode"], CAP["precision"]

VW = 1080
PAPER = "#f5f5f5"
PAPER2 = "#ececec"
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
CANONICAL = "canery.in/blogs/discrete-diffusion-language-models"
FOOTER = "DISCRETE DIFFUSION LANGUAGE MODELS · CANERY.IN"

# quoted, not measured: LLaDA 8B Base, random against low-confidence remasking, Nie et al. 2025, Table 9 (L37)
REMASK = {"BBH": (32.1, 45.0), "GSM8K": (21.3, 70.0), "Math": (9.2, 30.3), "HumanEval": (11.6, 32.9), "MBPP": (21.0, 40.2)}
# quoted, not measured: Zheng et al. 2025, Table 2, 8 samples of 2,048 steps, only the sampling code changed (L02)
ZHENG = {"32-bit": (31.24, 5.17), "64-bit": (126.11, 5.66)}

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


def grey(v, lo, hi):
    """High value = bright, the series' display convention; the article's tiles use the same ranges."""
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


HATCH = (f'<defs><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse" '
         f'patternTransform="rotate(45)"><rect width="10" height="10" fill="{PAPER2}"/>'
         f'<line x1="0" y1="0" x2="0" y2="10" stroke="{ACCENT}" stroke-width="3.5"/></pattern></defs>')


def tile(x, y, size, toks, side=8, levels=28, stroke=RULE_SOLID, sw=1.5):
    rows = [[grey(toks[r * side + c], 0, levels - 1) for c in range(side)] for r in range(side)]
    return (f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="{png_gray(rows)}" '
            f'preserveAspectRatio="none" style="image-rendering:pixelated"/>' + box(x, y, size, size, "none", stroke, 0, sw))


def tok4(x, y, toks, cell=66, gap=8, mask=None, size=30):
    """Part 1's patch as four-level tokens, the level printed; masked cells hatched with an M."""
    out = ""
    for r in range(4):
        for c in range(4):
            cx, cy = x + c * (cell + gap), y + r * (cell + gap)
            if mask is not None and mask[r][c]:
                out += box(cx, cy, cell, cell, "url(#hatch)", ACCENT, 4, 2)
                out += box(cx + cell / 2 - 17, cy + cell / 2 - 17, 34, 34, PAPER, "none", 4, 0)
                out += txt(cx + cell / 2, cy + cell / 2 + 9, "M", 24, ACCENT, MONO, 600, "middle")
                continue
            v = toks[r][c]
            g = grey(v, 0, 3)
            out += box(cx, cy, cell, cell, f"rgb({g},{g},{g})", RULE_SOLID, 4, 1.2)
            out += txt(cx + cell / 2, cy + cell / 2 + size * 0.36, str(v), size, PAPER if v <= 1 else INK, MONO, 600, "middle")
    return out


def pc(v, digits=1):
    return "100%" if v == 1 else ("0%" if v == 0 else f"{100 * v:.{digits}f}%")


def world_keys():
    """The 72 images' token tuples, rebuilt as the lab builds them and checked against the capture."""
    import numpy as np

    def crescent_shape(r=8, inner=(0.64, 0.42, 0.30), ss=8):
        g = (np.arange(r * ss) + 0.5) / (r * ss)
        yy, xx = np.meshgrid(g, g, indexing="ij")
        outer = (xx - 0.5) ** 2 + (yy - 0.5) ** 2 < 0.36 ** 2
        hole = (xx - inner[0]) ** 2 + (yy - inner[1]) ** 2 < inner[2] ** 2
        return (outer & ~hole).astype(float).reshape(r, ss, r, ss).mean(axis=(1, 3))

    def unit(m):
        m = m.reshape(-1) - m.mean()
        return m * 0.9 / np.sqrt((m ** 2).mean())
    mu = [unit(np.rot90(crescent_shape(), k)) for k in range(4)]
    b = 0.15 * (np.arange(9) - 4)
    imgs = [np.floor((a * mu[k] + bb) / 0.15 + 0.5).astype(int) for k in range(4) for a in (0.5, 1.0) for bb in b]
    lo = min(i.min() for i in imgs)
    keys = {tuple((i - lo).tolist()) for i in imgs}
    for ex in WD["examples"]["turn0_strong_by_level"] + WD["examples"]["middle_level"]:
        assert tuple(ex) in keys
    return keys


KEYS = world_keys()


# ------------------------------------------------------------------ the shell
def shell(kind, number, total, title, deck, visual, takeaway, cta=None):
    height, logo_y, logo_w = 1350, 72, 220
    rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
    deck_y = title_y + len(title) * title_gap + 20
    take_rule, take_y, foot_y = 1168, 1220, 1305
    scale = logo_w / LOCKUP_FULL_W
    defs = f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style></defs>' + HATCH
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
ONE = DC["one_per_step"]
PAR = DC["parallel"]


# ------------------------------------------------------------------ feed
def feed_01():
    size, gap, x0 = 168, 22, 72
    v = ""
    rows = (("one token per call", ONE["random"]), ("two tokens per call", PAR["random_2"]))
    for r, (name, R) in enumerate(rows):
        y = 534 + r * 316
        v += label(x0, y - 22, name, INK if r == 0 else ACCENT, "start", 15)
        for c, img in enumerate(R["examples"][:4]):
            v += tile(x0 + c * (size + gap), y, size, img)
            ok = tuple(img) in KEYS
            v += mono(x0 + c * (size + gap) + size / 2, y + size + 30, "one of the 72" if ok else "not an image", 16,
                      SAGE if ok else ACCENT, "middle", 600)
        v += label(1008, y + 62, "valid samples", MUTED, "end", 16)
        v += txt(1008, y + 122, pc(R["valid"]), 54, INK if r == 0 else ACCENT, SANS, 600, "end")
    emit("feed", 1, "right-predictions-wrong-samples",
         ["Right predictions,", "wrong samples."],
         ["A masked diffusion model whose every prediction is exact still writes",
          "broken images when it fills in two tokens per network call."],
         v,
         ["The joint is what parallel decoding breaks, not the predictions.",
          f"Crescent world as tokens, {DC['images_per_sampler']:,} images per sampler."],
         FEED_TOTAL)


def feed_02():
    v = label(72, 500, "part 1's patch as 16 tokens", SOFT, "start", 15)
    v += tok4(72, 520, WK["tokens"])
    v += txt(450, 680, "→", 64, ACCENT, SANS, 400, "middle")
    v += label(526, 500, f"masked at ᾱ = {WK['abar']}: {WK['n_masked']} of 16 hidden", ACCENT, "start", 15)
    v += tok4(526, 520, WK["tokens"], mask=WK["masked"])
    v += mono(72, 870, f"Gaussian noise on a token is meaningless: level 3 plus noise", 20, MUTED)
    v += mono(72, 900, "is no token. Masking hides a token and says which one it hid;", 20, MUTED)
    v += mono(72, 930, f"uniform replacement keeps it with {WK['uniform']['stay']:.2f} and hides its changes.", 20, MUTED)
    v += box(72, 980, 936, 120, "#ffffff", RULE_SOLID)
    v += label(100, 1022, "which tokens to hide", SOFT, "start", 14)
    v += mono(100, 1068, f"part 1's own noise draw: hidden where ε > {WK['eps_cut']:.4f}, Φ(ε) > {WK['abar']}", 22, INK,
              "start", 600)
    emit("feed", 2, "noise-a-token-by-hiding-it",
         ["Noise a token", "by hiding it."],
         ["Text is categories, so diffusion swaps Gaussian noise for a [MASK]",
          "symbol. Part 1's patch, rounded to four grey levels, shows how."],
         v,
         ["Masking beat uniform replacement on every dataset in SEDD's",
          "zero-shot table, and later work built on masking."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 500, 936, 150, "#ffffff", RULE_SOLID)
    v += label(100, 542, "the training loss", SOFT, "start", 15)
    v += mono(100, 606, "(1/t) × Σ hidden −log p(true token)", 38, INK, "start", 600)
    rows = [("BERT", "one fixed rate: 15% of positions"),
            ("LLaDA", "every rate t from 0 to 1, weight 1/t"),
            ("the weight", "about tL tokens hidden: every rate weighs L")]
    y = 730
    for head, body in rows:
        v += txt(100, y, head, 32, INK, SERIF, 400)
        v += mono(330, y - 2, body, 21, MUTED)
        v += hline(100, 1008, y + 30, RULE, 1)
        y += 96
    oc = WD["order_check"]
    v += mono(100, 1030, f"exact denoiser: every reveal order of {WD['images']} images costs", 20, ACCENT, "start", 500)
    m, e = f"{oc['max_abs_error_nats']:.1e}".split("e")
    sup = str(int(e)).replace("-", "⁻").translate(str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹"))
    v += mono(100, 1060, f"−log p(image) to {m} × 10{sup} nats", 20, ACCENT, "start", 500)
    emit("feed", 3, "berts-loss-at-every-rate",
         ["BERT's loss,", "at every rate."],
         ["Mask each token with probability t, predict the hidden ones, and",
          "weight their cross-entropy by 1/t: a bound on the likelihood."],
         v,
         ["Training every rate turns a fill-in-the-blank model into a generator.",
          "LLaDA 8B was trained this way on 2.3T tokens."],
         FEED_TOTAL)


def feed_04():
    C = WK["corners"]
    v = box(72, 500, 936, 200, "#ffffff", RULE_SOLID)
    v += label(100, 542, "two opposite corners of the four-turn world, drawn at once", SOFT, "start", 15)
    v += mono(100, 596, f"each corner alone: 0 with 1/2, 2 with 1/4, 3 with 1/4", 22, INK, "start", 500)
    v += mono(100, 640, f"a real pair {C['p_consistent']:.2f} of the time; both 0 ({C['p_both_darkest']:.2f})", 22, ACCENT,
              "start", 600)
    v += mono(100, 676, "is a pair no turn has", 22, ACCENT, "start", 600)
    rows = [("one per call", ONE["random"]["valid"], INK), ("two per call", PAR["random_2"]["valid"], ACCENT),
            ("four per call", PAR["random_4"]["valid"], ACCENT), ("eight per call", PAR["random_8"]["valid"], ACCENT)]
    x_bar, bw = 400, 480
    y = 780
    v += label(100, y - 26, "crescent world as tokens: valid samples", SOFT, "start", 14)
    for name, val, colour in rows:
        v += txt(100, y + 22, name, 26, INK, SANS, 500)
        v += box(x_bar, y + 4, bw, 22, PAPER2, "none", 3, 0)
        if val > 0:
            v += box(x_bar, y + 4, max(3, bw * val), 22, colour, "none", 3, 0)
        v += mono(1008, y + 22, pc(val, 2 if 0 < val < 0.01 else 1), 22, colour, "end", 600)
        y += 72
    emit("feed", 4, "two-at-once-can-clash",
         ["Two at once", "can clash."],
         ["Each hidden token is drawn from its own prediction. Drawn together,",
          "two tokens that depend on each other can come from different answers."],
         v,
         [f"MDLM's own sampler at 64 steps for 64 tokens revealed "
          f"{pc(DC['ancestral']['64']['revealed_alongside_another'], 0)} of",
          f"tokens alongside another: {pc(DC['ancestral']['64']['valid'])} of its samples were valid."],
         FEED_TOTAL)


def feed_05():
    x_bar, bw = 300, 560
    v = label(100, 506, "llada 8b base · one token per step, 256 tokens · quoted", SOFT, "start", 15)
    y = 560
    for name, (rnd, low) in REMASK.items():
        v += txt(100, y + 28, name, 28, INK, SANS, 600)
        v += box(x_bar, y + 4, bw * rnd / 80, 18, BLUE, "none", 3, 0)
        v += mono(x_bar + bw * rnd / 80 + 12, y + 20, f"{rnd:.1f}", 19, BLUE, "start", 600)
        v += box(x_bar, y + 28, bw * low / 80, 18, ACCENT, "none", 3, 0)
        v += mono(x_bar + bw * low / 80 + 12, y + 44, f"{low:.1f}", 19, ACCENT, "start", 600)
        y += 100
    v += box(100, y + 6, 16, 14, BLUE, "none", 2, 0) + mono(126, y + 19, "random positions", 18, MUTED)
    v += box(420, y + 6, 16, 14, ACCENT, "none", 2, 0) + mono(446, y + 19, "most confident positions", 18, MUTED)
    emit("feed", 5, "same-model-different-decoder",
         ["Same model,", "different decoder."],
         ["LLaDA's ablation kept either random predictions or the most confident",
          "ones each step. The model did not change; the scores did."],
         v,
         ["GSM8K went from 21.3 to 70.0. Headline scores describe the decoder,",
          "which the authors liken to annealed sampling: accurate, less diverse."],
         FEED_TOTAL)


def feed_06():
    rows = [("random order, sampled", ONE["random"], INK), ("surest position first", ONE["position"], INK),
            ("likeliest draw first", ONE["drawn"], ACCENT), ("surest first, greedy", ONE["greedy_drawn"], ACCENT)]
    v = label(100, 506, "one token per call · images found of 72 · brightness spread", SOFT, "start", 15)
    size, gap = 76, 12
    y = 560
    for name, R, colour in rows:
        v += txt(100, y + 26, name, 26, INK, SANS, 600)
        v += mono(100, y + 62, f"{R['images_found']} images · spread {R['brightness_sd']:.3f}", 20, colour, "start", 600)
        for c, img in enumerate(R["examples"][:4]):
            v += tile(640 + c * (size + gap), y, size, img)
        y += 128
    v += mono(100, y + 14, f"the world's own spread: {WD['brightness_sd']:.3f}", 19, MUTED)
    emit("feed", 6, "most-confident-first-stops-sampling",
         ["Most confident first", "stops sampling."],
         ["With exact predictions the order is harmless. Ranking by the token",
          "just drawn keeps lucky draws, and brightness collapses."],
         v,
         [f"LLaDA's default decoder, greedy and most confident first, returned",
          f"{ONE['greedy_drawn']['images_found']} of the toy's 72 images, all faint and at one brightness."],
         FEED_TOTAL)


def feed_07():
    share = PR["float32"][PR["c"].index(1e-08)]
    even = PR["even_share"]["gpt2_50257"]
    v = box(72, 500, 936, 250, "#ffffff", RULE_SOLID)
    v += label(100, 542, "zheng et al. · only the sampling code changed · quoted", SOFT, "start", 15)
    y = 600
    for name, (g, e) in ZHENG.items():
        colour = ACCENT if name == "32-bit" else BLUE
        v += txt(100, y, name, 30, INK, SERIF, 400)
        v += mono(300, y - 2, f"Gen PPL {g:.2f}", 24, colour, "start", 600)
        v += mono(640, y - 2, f"entropy {e:.2f}", 24, colour, "start", 600)
        y += 64
    v += mono(100, y + 4, "lower perplexity, lower entropy: a lower temperature", 20, MUTED)
    v += label(100, 830, "the lab's race: [mask] against one token", SOFT, "start", 14)
    v += mono(100, 878, f"weight 1e-8 of the mask's: float32 wins {pc(share)} of its fair chance", 22, ACCENT, "start", 600)
    v += mono(100, 918, f"float32 halves a token's chance below c = {PR['half_share_c'] * 1e8:.2f} × 10⁻⁸", 22, INK)
    p_line = PR["half_share_p_first_step"]["1000"]
    v += mono(100, 958, f"at step 1 of 1,000 that is a token probability of {p_line:.2e};", 22, INK)
    v += mono(100, 998, f"an even share of GPT-2's 50,257 tokens, {even:.2e}, is below it", 22, INK)
    emit("feed", 7, "float32-lowered-the-temperature",
         ["Float32 lowered", "the temperature."],
         ["MDLM's and SEDD's samplers race [MASK] against every token each step.",
          "In float32 unlikely tokens almost never win, so diversity quietly falls."],
         v,
         ["Masked diffusion looked better than GPT-2 on generative perplexity",
          "until the sampler ran in float64. Later codebases sample in float64."],
         FEED_TOTAL)


def feed_08():
    items = [("Precision", "float32 races [MASK] against tiny weights; use float64"),
             ("Tokens per step", "two at once can clash; threshold on certainty"),
             ("Decoder", "greedy, most confident first is not sampling the model"),
             ("Metric", "report entropy beside generative perplexity"),
             ("Protocol", "likelihood-scored or generated, and at how many steps")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 8, "read-the-article",
         ["What to check in", "a diffusion LM claim."],
         ["Masked diffusion writes text by unmasking tokens. The model is half",
          "the story; the sampler is the other half."],
         v,
         ["Ask how it was sampled before you compare it."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
