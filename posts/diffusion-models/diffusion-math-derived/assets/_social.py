#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Where the Diffusion MSE Loss Comes From".

Diffusion Models, part 3. The shell (lockup, rule, serif title, deck, takeaway,
footer) is the construction the NVIDIA Stack series settled on, with the lockup
reading "canery.in". Every artefact on a card is computed from the lab module the
article ships, or quoted from a ledger row, so a card cannot disagree with the post.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]                     # a series member sits one level deeper
sys.path.insert(0, str(HERE.parent / "lab"))
import loss_identities as L  # noqa: E402

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
CANONICAL = "canery.in/blogs/diffusion-math-derived"
FOOTER = "WHERE THE DIFFUSION MSE LOSS COMES FROM · CANERY.IN"

STEP = L.coarse_step()
A, S = math.sqrt(L.ABAR_T), math.sqrt(1 - L.ABAR_T)

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
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def gpdf(x, m, v):
    return math.exp(-(x - m) ** 2 / (2 * v)) / math.sqrt(2 * math.pi * v)


def curve(x0, y0, w, h, xr, yr, f, colour, width=4, dash=None, n=240):
    pts = []
    for i in range(n + 1):
        u = xr[0] + (xr[1] - xr[0]) * i / n
        v = f(u)
        pts.append(f"{x0 + (u - xr[0]) / (xr[1] - xr[0]) * w:.1f},"
                   f"{y0 + h - (v - yr[0]) / (yr[1] - yr[0]) * h:.1f}")
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(pts)}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{d}/>')


def teacher_student(x0, y0, w, h, show_evidence=False):
    """The article's Figure 1 motif, redrawn at card scale."""
    c = STEP
    xr, yr = (-0.3, 1.7), (0, 1.32)
    X = lambda v: x0 + (v - xr[0]) / (xr[1] - xr[0]) * w
    Y = lambda v: y0 + h - (v - yr[0]) / (yr[1] - yr[0]) * h
    out = hline(x0, x0 + w, y0 + h, RULE_SOLID, 1.5)
    if show_evidence:
        out += curve(x0, y0, w, h, xr, yr, lambda u: gpdf(u, c["m_from_x0"], c["v_from_x0"]), BLUE, 3)
        out += curve(x0, y0, w, h, xr, yr, lambda u: gpdf(u, c["m_from_xt"], c["v_from_xt"]), MUSTARD, 3)
    out += curve(x0, y0, w, h, xr, yr, lambda u: gpdf(u, c["teacher_mean"], c["teacher_var"]), INK, 5)
    out += curve(x0, y0, w, h, xr, yr, lambda u: gpdf(u, c["student_mean"], c["teacher_var"]),
                 ACCENT, 5, "12,8")
    pk = gpdf(0, 0, c["teacher_var"])
    xa, xb, yy = X(c["student_mean"]), X(c["teacher_mean"]), Y(pk) - 26
    out += (f'<line x1="{xa:.1f}" y1="{yy:.1f}" x2="{xb:.1f}" y2="{yy:.1f}" stroke="{ACCENT}" stroke-width="3"/>'
            f'<line x1="{xa:.1f}" y1="{yy - 10:.1f}" x2="{xa:.1f}" y2="{yy + 10:.1f}" stroke="{ACCENT}" stroke-width="3"/>'
            f'<line x1="{xb:.1f}" y1="{yy - 10:.1f}" x2="{xb:.1f}" y2="{yy + 10:.1f}" stroke="{ACCENT}" stroke-width="3"/>')
    out += mono((xa + xb) / 2, yy - 18, f"gap {abs(c['gap']):.4f}", 22, ACCENT, "middle", 600)
    out += label(X(c["teacher_mean"]) + 120, Y(1.05), "teacher · knows x₀", INK, "start", 15)
    out += label(X(c["student_mean"]) - 120, Y(1.05), "student · network", ACCENT, "end", 15)
    return out


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


# ------------------------------------------------------------------ feed
FEED_TOTAL, STORY_TOTAL = 7, 4


def feed_01():
    c = STEP
    v = teacher_student(110, 520, 860, 380)
    v += box(110, 960, 860, 150, "#ffffff", RULE_SOLID)
    v += mono(540, 1022, f"KL = gap² ÷ (2 × 1/9) = {c['kl']:.4f} nats", 30, INK, "middle", 600)
    v += mono(540, 1070, f"= {c['weight']:.3f} × (noise error)²,  with (noise error)² = 0.04", 22, ACCENT, "middle", 500)
    emit("feed", 1, "your-mse-is-a-bound",
         ["Your MSE loss is a", "likelihood bound."],
         ["One reverse step, one pixel: the teacher knows the clean image,",
          "the network does not. Same width, so only the centres differ."],
         v,
         ["Two Gaussians of equal width: their KL is a squared",
          "error between two means. That is where the MSE comes from."],
         FEED_TOTAL)


def feed_02():
    c = STEP
    v = teacher_student(110, 520, 860, 330, show_evidence=True)
    rows = [("evidence from x₀", f"N({c['m_from_x0']:.4f}, 0.20)", "precision 5", BLUE),
            ("evidence from xₜ", f"N({c['m_from_xt']:.4f}, 0.25)", "precision 4", MUSTARD),
            ("teacher", f"N({c['teacher_mean']:.4f}, 1/9)", "5 + 4 = 9", INK)]
    y = 912
    v += box(110, y, 860, 216, "#ffffff", RULE_SOLID)
    for i, (a, b, p, col) in enumerate(rows):
        yy = y + 58 + i * 60
        v += txt(140, yy, a, 22, col, SANS, 600)
        v += mono(560, yy, b, 22, INK, "middle")
        v += mono(940, yy, p, 22, col, "end", 600)
    emit("feed", 2, "precisions-add",
         ["The teacher is two", "Gaussians, multiplied."],
         ["Given the clean pixel 0.95 and the noisy pixel 0.43, where was",
          "the pixel one step earlier? Two pieces of evidence answer."],
         v,
         ["Precisions add. That is the whole forward posterior,",
          "and DDPM's closed form gives the same 0.6857."],
         FEED_TOTAL)


def feed_03():
    rows = L.five_prices()
    names = {"epsilon": "noise ε", "x0": "clean pixel x₀", "score": "score −ε/0.6",
             "v": "velocity v"}
    consts = {"epsilon": "× 1", "x0": "× SNR 1.78", "score": "× 0.36", "v": "× 0.64"}
    v = box(72, 500, 936, 620, "#ffffff", RULE_SOLID)
    v += label(110, 560, "network predicts", SOFT, "start", 13)
    v += label(600, 560, "squared error", SOFT, "end", 13)
    v += label(800, 560, "× constant", SOFT, "end", 13)
    v += label(970, 560, "noise units", SOFT, "end", 13)
    y = 640
    for name, true, pred, sq, conv in rows:
        v += txt(110, y, names[name], 28, INK, SANS, 600)
        v += mono(600, y, f"{sq:.4f}", 28, BLUE, "end")
        v += mono(800, y, consts[name], 24, MUTED, "end")
        v += mono(970, y, f"{sq * conv:.4f}", 28, INK, "end", 600)
        y += 92
    v += hline(110, 970, y - 50)
    v += txt(110, y + 4, "this step's KL", 28, ACCENT, SANS, 600)
    v += mono(600, y + 4, f"{STEP['kl']:.4f}", 28, ACCENT, "end")
    v += mono(800, y + 4, "= 0.625 ×", 24, ACCENT, "end")
    v += mono(970, y + 4, "0.0400", 28, ACCENT, "end", 600)
    emit("feed", 3, "one-error-five-prices",
         ["One error,", "five prices."],
         ["The network misreads the noise by +0.20. Priced as noise, clean",
          "pixel, score or velocity, it is the same 0.04 each time."],
         v,
         ["At one noise level every target has the same minimiser.",
          "Targets differ only in how they trade levels off."],
         FEED_TOTAL)


def feed_04():
    wb = L.elbo_weights(variance="beta")
    lo_t = min(wb, key=wb.get)
    x0, y0, w, h = 150, 520, 820, 420
    lo, hi = -3.0, 0.4
    X = lambda t: x0 + (t - 0) / 1000 * w
    Y = lambda val: y0 + h - (math.log10(val) - lo) / (hi - lo) * h
    v = hline(x0, x0 + w, y0 + h, RULE_SOLID, 1.5)
    for e, lab in ((-3, "0.001"), (-2, "0.01"), (-1, "0.1"), (0, "1")):
        v += hline(x0, x0 + w, Y(10 ** e), RULE)
        v += mono(x0 - 14, Y(10 ** e) + 6, lab, 16, SOFT, "end")
    v += hline(x0, x0 + w, Y(1.0), ACCENT, 4)
    pts = " ".join(f"{X(t):.1f},{Y(val):.1f}" for t, val in sorted(wb.items()))
    v += f'<polyline points="{pts}" fill="none" stroke="{INK}" stroke-width="4"/>'
    for t, dx, dy, lab in ((2, 20, -8, f"t = 2: {wb[2]:.4f}"),
                           (lo_t, 0, 44, f"t = {lo_t}: {wb[lo_t]:.5f}"),
                           (1000, -10, -24, f"t = 1000: {wb[1000]:.4f}")):
        v += f'<circle cx="{X(t):.1f}" cy="{Y(wb[t]):.1f}" r="8" fill="{INK}"/>'
        v += mono(X(t) + dx, Y(wb[t]) + dy, lab, 20, INK, "start" if t == 2 else ("middle" if t == lo_t else "end"), 600)
    v += mono(x0 + w - 8, Y(1.0) + 36, "the simple loss: 1 at every step", 20, ACCENT, "end", 600)
    v += mono(x0 + w / 2, y0 + h + 44, "DDPM step t, 1,000 steps, linear schedule", 18, SOFT, "middle")
    v += box(150, 1030, 820, 96, ACCENT_TINT, ACCENT, 8, 1.5)
    v += mono(560, 1090, f"inside the bound: {wb[2] / wb[lo_t]:.0f}× between largest and smallest", 24, ACCENT, "middle", 600)
    emit("feed", 4, "the-weight-ddpm-dropped",
         ["The weight DDPM", "dropped."],
         ["Each step of the bound puts its own weight on the noise error.",
          "DDPM's simple loss replaces every one of them with 1."],
         v,
         ["The dropped weights favour nearly clean steps. Setting",
          "them to 1 turns those down and trains the harder ones."],
         FEED_TOTAL)


def feed_05():
    groups = [("DDPM · CIFAR-10", [("true bound", 3.70, 13.51, INK), ("simple loss", 3.75, 3.17, ACCENT)]),
              ("IMPROVED DDPM · CIFAR-10", [("true bound", 2.94, 11.47, INK),
                                            ("hybrid", 3.17, 3.19, BLUE),
                                            ("simple loss", 3.26, 3.05, ACCENT)])]
    v = label(420, 520, "nll, bits/dim ↓", SOFT, "start", 14)
    v += label(760, 520, "fid ↓", SOFT, "start", 14)
    y = 580
    for gname, rows in groups:
        v += label(72, y, gname, INK, "start", 15)
        y += 22
        for name, nll, fid, col in rows:
            v += txt(390, y + 36, name, 26, col, SANS, 600, "end")
            v += box(420, y + 10, nll / 4.0 * 280, 36, "#ffffff", col, 4, 2)
            v += mono(420 + nll / 4.0 * 280 + 12, y + 38, f"{nll:.2f}", 22, col, "start", 600)
            v += box(760, y + 10, fid / 14.0 * 150, 36, "#ffffff", col, 4, 2)
            v += mono(760 + fid / 14.0 * 150 + 12, y + 38, f"{fid:.2f}", 22, col, "start", 600)
            y += 62
        y += 44
    v += mono(72, 1060, "Different setups: compare within a group, not across.", 18, SOFT)
    emit("feed", 5, "bound-versus-samples",
         ["Better bound,", "worse samples."],
         ["Measured on CIFAR-10 in two papers. Training on the true bound",
          "wins on likelihood and loses on image quality."],
         v,
         ["DDPM's best-FID model has the worse bound, 3.75 against",
          "3.70 bits per dimension. The loss value is not a likelihood."],
         FEED_TOTAL)


def feed_06():
    rows = [("ELBO", "1", "flat", INK),
            ("ε-prediction, cosine", "sech(λ/2)", "bump at SNR 1", BLUE),
            ("v-prediction, cosine", "e^(−λ/2)", "rises with noise", "#7c8f6f"),
            ("EDM", "N(λ; 2.4, 2.4²)(e^−λ + 0.25)", "bump", MUSTARD),
            ("Min-SNR, γ = 5", "sech(λ/2)·min(1, 5e^−λ)", "cuts clean end", ACCENT)]
    v = box(72, 500, 936, 560, "#ffffff", RULE_SOLID)
    v += label(110, 556, "loss", SOFT, "start", 13)
    v += label(520, 556, "weight w(λ) on the noise error", SOFT, "start", 13)
    y = 636
    for name, w, shape, col in rows:
        v += txt(110, y, name, 26, col, SANS, 600)
        v += mono(520, y, w, 22, INK)
        y += 86
    v += mono(72, 1110, "λ = log SNR. Formulas as tabulated by Kingma & Gao, NeurIPS 2023.", 18, SOFT)
    emit("feed", 6, "one-loss-many-weightings",
         ["One loss,", "many weightings."],
         ["Every published diffusion loss is one integral of the noise",
          "error over log-SNR. Only the weight in front changes."],
         v,
         ["Picking a prediction target is picking one of these",
          "weights, whether you meant to or not."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 520, 936, 560, "#ffffff", RULE_SOLID)
    items = [("DDPM", "variance-preserving chain · predicts ε", "T → ∞ gives the VP SDE"),
             ("NCSN", "variance-exploding ladder · predicts the score", "levels → ∞ gives the VE SDE"),
             ("VP ↔ VE", "divide x by √ᾱ: σ = 1/√SNR", "same information, known scale"),
             ("the loss", "½∫ w(λ) · (noise error)² dλ", "ELBO, simple loss, DSM: three weights")]
    y = 594
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "the loss" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 124
    emit("feed", 7, "read-the-article",
         ["Three formulations,", "one object."],
         ["DDPM, NCSN and the score SDE learn the same function of the",
          "same noisy input. They differ in scale, limit and weight."],
         v,
         ["The full derivation, on part 1's numbers, with a",
          "lab script that checks every identity."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    c = STEP
    v = teacher_student(110, 820, 860, 420)
    v += box(110, 1300, 860, 150, "#ffffff", RULE_SOLID)
    v += mono(540, 1362, f"KL = {c['kl']:.4f} nats", 38, INK, "middle", 600)
    v += mono(540, 1414, f"= {c['weight']:.3f} × (noise error)²", 28, ACCENT, "middle", 500)
    emit("story", 1, "your-mse-is-a-bound",
         ["Your MSE loss is", "a likelihood bound."],
         ["Each denoising step is scored by a KL", "between two Gaussians of equal width."],
         v,
         ["Equal widths leave only the centres to compare:", "a squared error."],
         STORY_TOTAL)


def story_02():
    rows = L.five_prices()
    names = {"epsilon": "noise ε", "x0": "clean pixel x₀", "score": "score", "v": "velocity v"}
    v = box(72, 780, 936, 680, "#ffffff", RULE_SOLID)
    y = 880
    for name, true, pred, sq, conv in rows:
        v += txt(120, y, names[name], 34, INK, SANS, 600)
        v += mono(640, y, f"{sq:.4f}", 32, BLUE, "end")
        v += mono(960, y, f"→ {sq * conv:.4f}", 32, INK, "end", 600)
        y += 118
    v += hline(120, 960, y - 64)
    v += txt(120, y, "the bound's KL", 34, ACCENT, SANS, 600)
    v += mono(960, y, f"{STEP['kl']:.4f} = 0.625 × 0.04", 30, ACCENT, "end", 600)
    emit("story", 2, "one-error-five-prices",
         ["One error,", "five prices."],
         ["A +0.20 noise error, priced as each target", "a diffusion network can predict."],
         v,
         ["Same minimiser at every noise level.", "Only the weights across levels differ."],
         STORY_TOTAL)


def story_03():
    pairs = L.dsm_samples(600)
    bins = L.binned_means(L.dsm_samples(6000))
    x0, y0, w, h = 110, 880, 860, 530
    xr, yr = (-2.2, 2.2), (-5.5, 5.5)
    X = lambda u: x0 + (u - xr[0]) / (xr[1] - xr[0]) * w
    Y = lambda u: y0 + h - (u - yr[0]) / (yr[1] - yr[0]) * h
    v = box(x0 - 20, y0 - 100, w + 40, h + 120, "#ffffff", RULE_SOLID)
    v += hline(x0, x0 + w, Y(0), RULE_SOLID)
    v += f'<clipPath id="sc"><rect x="{x0}" y="{y0}" width="{w}" height="{h}"/></clipPath><g clip-path="url(#sc)">'
    for z, t in pairs:
        v += f'<circle cx="{X(z):.1f}" cy="{Y(t):.1f}" r="4" fill="{SOFT}" opacity="0.35"/>'
    v += "</g>"
    v += curve(x0, y0, w, h, xr, yr, lambda u: L.score(u, A, S), ACCENT, 6)
    for zc, m, _ in bins:
        v += f'<rect x="{X(zc) - 8:.1f}" y="{Y(m) - 8:.1f}" width="16" height="16" fill="{INK}"/>'
    v += f'<circle cx="{x0 + 8}" cy="{y0 - 62}" r="6" fill="{SOFT}" opacity="0.6"/>'
    v += label(x0 + 26, y0 - 56, "one noisy target", SOFT, "start", 15)
    v += f'<rect x="{x0 + 330}" y="{y0 - 70}" width="16" height="16" fill="{INK}"/>'
    v += label(x0 + 356, y0 - 56, "their average", INK, "start", 15)
    v += hline(x0 + 600, x0 + 640, y0 - 62, ACCENT, 6)
    v += label(x0 + 652, y0 - 56, "exact score", ACCENT, "start", 15)
    emit("story", 3, "noisy-targets-exact-average",
         ["Noisy targets,", "exact average."],
         ["Each target is a single noise draw.", "Their average is the score."],
         v,
         ["Regression finds the average of its target.", "That is why denoising learns a score."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["Jensen's inequality: log p(x) ≥ ELBO",
             "Bayes on each forward step",
             "KL of equal-width Gaussians = squared error",
             "write the mean through the noise",
             "drop the weights → the simple loss"]
    y = 880
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 30, INK, SANS, 600 if i == 4 else 400)
        y += 108
    emit("story", 4, "read-the-article",
         ["Five steps from a", "likelihood to an MSE."],
         ["Four are exact.", "The last one is a choice."],
         v,
         ["The full derivation is on Canery."],
         STORY_TOTAL, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07,
            story_01, story_02, story_03, story_04]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
