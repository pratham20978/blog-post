#!/usr/bin/env python3
"""Build the finished Canery feed for "Evaluating Generative Models: What FID Measures and Hides".

Diffusion Models, part 9. The shell (lockup, rule, serif title, deck, takeaway, footer) is the
construction the series settled on, with the lockup reading "canery.in". Every measured or
computed artefact on a card is read from the lab capture the article ships (../lab/captures.json),
so a card cannot disagree with the post; the one quoted comparison (feed 07) is typed once below,
next to its ledger keys. This part ships feed cards only, no Story frames, as part 8 did.

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
OUT = pathlib.Path(os.environ.get("P9_SOCIAL_OUT", HERE / "social"))
ROOT = HERE.parents[3]                     # a series member sits one level deeper
CAP = json.loads(pathlib.Path(os.environ.get("P9_CAPTURES", HERE.parent / "lab" / "captures.json"))
                 .read_text(encoding="utf-8"))
W, F, B, G = CAP["worked"], CAP["failures"], CAP["bias"], CAP["guidance"]

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
CANONICAL = "canery.in/blogs/evaluating-generative-models"
FOOTER = "EVALUATING GENERATIVE MODELS · CANERY.IN"

# quoted, not measured: Stein et al. 2023, Table 5 and Appendix A.2 (ledger L29, L31)
STEIN = {"StyleGAN-XL": {"fid": 2.26, "err": 0.153}, "DiT-XL/2": {"fid": 2.27, "err": 0.286}}

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
S = F["sets"]


# ------------------------------------------------------------------ feed
def feed_01():
    size, gap, x0 = 168, 22, 72
    v = ""
    for r, key in enumerate(("drops faint", "grainy")):
        y = 534 + r * 316
        v += label(x0, y - 22, {"drops faint": "drops every faint crescent", "grainy": "adds grain to every pixel"}[key],
                   SOFT, "start", 15)
        for c, img in enumerate(S[key]["samples"][:4]):
            v += tile(x0 + c * (size + gap), y, size, img)
        v += label(1008, y + 62, "FD", MUTED, "end", 16)
        v += txt(1008, y + 122, f"{S[key]['fd']:.4f}", 54, ACCENT, SANS, 600, "end")
    assert S["drops faint"]["fd"] == S["grainy"]["fd"]
    emit("feed", 1, "one-number-two-failures",
         ["One number,", "two failures."],
         ["The arithmetic inside FID scores these two crescent generators",
          "exactly equal. One lost half the variety; one adds grain to all."],
         v,
         ["Same score to four decimals. A single distance cannot say whether",
          "a model lost quality or lost variety."],
         FEED_TOTAL)


def feed_02():
    real = W["real"]["values"]
    mm = W["generators"]["moment matched"]
    lo, hi, x0, x1 = 0.25, 1.25, 96, 984

    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)

    def near(v):
        return min(abs(v - r) for r in real) <= 0.05 + 1e-9

    v = ""
    for row, (vals, name) in enumerate(((real, "eight real crescents"), (mm["values"], "a generator built to match them"))):
        base = 660 + row * 250
        v += label(x0, base - 110, name, SOFT, "start", 15)
        pts = [(X(lo + (hi - lo) * i / 300),
                base - 24 - 74 * math.exp(-0.5 * ((lo + (hi - lo) * i / 300 - W["real"]["mean"]) / W["real"]["sd"]) ** 2))
               for i in range(301)]
        v += polyline(pts, BLUE, 4)
        v += hline(x0, x1, base, RULE_SOLID, 2)
        seen = {}
        for val in vals:
            k = seen.get(val, 0)
            seen[val] = k + 1
            cy = base + k * 26
            v += circle(X(val), cy, 10, INK) if near(val) else circle(X(val), cy, 9, PAPER, ACCENT, 4)
    v += mono(x0, 1100, f"mean {W['real']['mean']:.2f} · spread {W['real']['sd']:.4f} in both rows", 20, MUTED)
    v += txt(984, 1100, f"FD = {mm['fd']:.0f}", 40, ACCENT, SANS, 600, "end")
    emit("feed", 2, "fd-can-be-zero",
         ["FD can be zero", "for broken images."],
         ["Reduce each image to its crescent's strength: faint 0.5 or strong",
          "1.0. FD compares only the mean and the spread of those numbers."],
         v,
         [f"Same bell, FD = {mm['fd']:.0f}, yet {8 - mm['within_0.05_of_a_real']} of its 8 values sit more than 0.05",
          "from any real crescent (hollow orange)."],
         FEED_TOTAL)


def feed_03():
    d = 2048
    distinct = d * (d + 1) // 2
    steps = [("images", "any size"), ("resize", "299 × 299"), ("Inception-v3", "ImageNet classifier"),
             (f"{d:,} features", "per image"), ("mean + covariance", "per set"), ("one distance", "FID")]
    v = ""
    y = 500
    for i, (head, sub) in enumerate(steps):
        last = i == len(steps) - 1
        v += box(96, y, 888, 74, "#ffffff" if not last else "rgba(235,108,54,0.08)",
                 ACCENT if last else "rgba(45,49,66,0.28)", 8, 2 if last else 1)
        v += txt(124, y + 47, head, 30, ACCENT if last else INK, SANS, 600)
        v += mono(956, y + 46, sub, 20, MUTED, "end")
        if not last:
            v += f'<line x1="540" y1="{y + 74}" x2="540" y2="{y + 96}" stroke="{MUTED}" stroke-width="3"/>'
        y += 96
    v += mono(96, y + 22, f"each set becomes {d:,} means and {distinct:,} distinct covariances", 20, INK, "start", 600)
    emit("feed", 3, "all-fid-keeps",
         ["All FID keeps", "is two summaries."],
         ["Real and generated images pass through an ImageNet classifier.",
          "Each set is then reduced to the mean and covariance of its features."],
         v,
         [f"In crescent world, a Gaussian blob with the data's mean and covariance",
          f"scored FD {S['gaussian']['fd']:.4f}, level with the perfect generator's {S['perfect']['fd']:.4f}."],
         FEED_TOTAL)


def feed_04():
    metrics = ("precision", "recall", "coverage")
    v = ""
    x_bar, bw = 420, 420
    y = 520
    for key, name in (("drops faint", "Drops faint"), ("grainy", "Grainy")):
        v += txt(96, y, name, 34, INK, SERIF, 400)
        v += mono(1008, y, f"FD {S[key]['fd']:.4f}", 22, ACCENT, "end", 600)
        y += 40
        for m in metrics:
            val = S[key][m]
            v += label(96, y + 26, m, MUTED, "start", 16)
            v += box(x_bar, y + 4, bw, 28, "rgba(45,49,66,0.08)", "none", 4, 0)
            v += box(x_bar, y + 4, max(3, bw * min(val, 1.0)), 28, MUTED, "none", 4, 0)
            v += mono(1008, y + 28, f3(val), 24, INK, "end", 600)
            y += 52
        y += 46
    p = S["perfect"]
    v += mono(96, y + 4, f"a perfect generator: precision {p['precision']:.3f} · recall {p['recall']:.3f} · "
                         f"coverage {p['coverage']:.3f}", 19, MUTED)
    emit("feed", 4, "two-numbers-split-the-tie",
         ["Two numbers", "split the tie."],
         ["Precision asks whether samples look real. Recall and coverage ask",
          "whether the real variety is there. Same FD, opposite answers."],
         v,
         ["Report fidelity and diversity separately, each read against a",
          "real-against-real baseline, never against 1.0."],
         FEED_TOTAL)


def feed_05():
    ws = ("1.0", "1.5", "2.0", "3.0", "4.0", "5.0", "7.5")
    xs = [float(w) for w in ws]
    x0, x1, y0, y1 = 150, 960, 560, 1000

    def X(v):
        return x0 + (v - 1.0) / 6.5 * (x1 - x0)

    def Y(v):
        assert 0 <= v <= 1.0
        return y1 - v * (y1 - y0)

    v = hline(x0, x1, y1, RULE_SOLID, 2)
    for t in (0.0, 0.5, 1.0):
        v += hline(x0, x1, Y(t), RULE, 1) + mono(x0 - 16, Y(t) + 7, f"{t:.1f}", 18, SOFT, "end")
    for w in xs:
        v += mono(X(w), y1 + 34, f"{w:g}", 18, SOFT, "middle")
    v += mono((x0 + x1) / 2, y1 + 70, "guidance weight w", 18, SOFT, "middle", 500)
    for key, colour, dash, name in (("faint", SOFT, "4,8", "faint share (truth)"), ("coverage", BLUE, None, "coverage"),
                                    ("recall", ACCENT, None, "recall")):
        pts = [(X(w), Y(G["weights"][k][key])) for w, k in zip(xs, ws)]
        v += polyline(pts, colour, 5 if key == "recall" else 4, dash)
        for a, b in pts:
            v += circle(a, b, 6, colour)
        last = pts[-1]
        v += label(last[0] - 12, last[1] + (30 if key == "coverage" else -18), name, colour, "end", 15)
    g = G["weights"]["7.5"]
    v += box(520, 486, 440, 60, "#ffffff", ACCENT, 8, 2)
    v += mono(540, 512, f"w = 7.5: {g['faint_holders']} stray faint samples,", 19, ACCENT, "start", 600)
    v += mono(540, 536, f"ball radius {g['faint_holder_radius_median']:.2f} against {g['fake_radius_median']:.2f}", 19, ACCENT,
              "start", 600)
    rx, ry = X(7.5), Y(g["recall"])
    v += f'<line x1="{rx:.1f}" y1="546" x2="{rx:.1f}" y2="{ry - 34:.1f}" stroke="{ACCENT}" stroke-width="2"/>'
    emit("feed", 5, "four-samples-fool-recall",
         ["Four samples", "can fool recall."],
         ["Turn guidance up and the faint crescents vanish. At w = 7.5",
          f"recall jumps back to {g['recall']:.3f}, as if the variety had returned."],
         v,
         [f"Recall credited {pc(g['recall_faint'])} of real faint images; coverage, which puts the",
          f"balls around real images, found a sample near {pc(g['coverage_faint'])} of them."],
         FEED_TOTAL)


def feed_06():
    ns = B["ns"]
    p, gr = B["gens"]["perfect"], B["gens"]["grainy"]
    rows = [(f"perfect generator, N = {n:,}", p["fd_mean"][ns.index(n)], INK) for n in (1000, 4000, 64000)]
    rows.insert(1, (f"grain {B['grain']:.2f}, N = 4,000", gr["fd_mean"][ns.index(4000)], MUSTARD))
    top = max(r[1] for r in rows)
    v = label(96, 512, "FD of 24 repeats, averaged", SOFT, "start", 15)
    y = 580
    for name, val, colour in rows:
        hot = name.startswith("perfect generator, N = 1,000") or name.startswith("grain")
        v += txt(96, y, name, 26, INK, SANS, 600 if hot else 400)
        v += box(96, y + 20, 700 * val / top, 34, colour, "none", 4, 0)
        v += mono(1008, y + 46, f"{val:.4f}", 28, ACCENT if hot else INK, "end", 600)
        y += 132
    assert p["fd_mean"][ns.index(1000)] > gr["fd_mean"][ns.index(4000)]
    emit("feed", 6, "fd-depends-on-n",
         ["FD depends on", "how many samples."],
         ["A perfect generator never scores zero: its FD falls roughly like",
          f"1/N, fitted as {p['fd_inf']:.4f} + {p['slope']:.1f}/N in crescent world."],
         v,
         ["The perfect generator at 1,000 samples scores worse than a grainy",
          "one at 4,000. Compare FIDs only at the same N."],
         FEED_TOTAL)


def feed_07():
    names = ("StyleGAN-XL", "DiT-XL/2")
    v = label(96, 512, "ImageNet 256 × 256 · FID as reported by each paper's authors", SOFT, "start", 15)
    for i, n in enumerate(names):
        x = 96 + i * 456
        v += box(x, 540, 432, 200, "#ffffff", RULE_SOLID, 8, 1)
        v += txt(x + 28, 600, n, 34, INK, SERIF, 400)
        v += label(x + 28, 650, "FID", MUTED, "start", 16)
        v += txt(x + 404, 700, f"{STEIN[n]['fid']:.2f}", 60, INK, SANS, 600, "end")
    v += label(96, 812, "share of real-or-fake judgements people got wrong", SOFT, "start", 15)
    for i, n in enumerate(names):
        y = 850 + i * 110
        err = STEIN[n]["err"]
        v += txt(96, y + 34, n, 28, INK, SANS, 600)
        v += box(400, y + 6, 500 * err / 0.5, 40, ACCENT if i == 1 else MUTED, "none", 4, 0)
        v += mono(1008, y + 36, pc(err), 30, ACCENT if i == 1 else INK, "end", 600)
    v += mono(96, 1100, "chance is 50% · Stein et al., NeurIPS 2023: 41 models, 207,000 judgements", 18, MUTED)
    emit("feed", 7, "same-fid-not-the-same-images",
         ["Same FID, not", "the same images."],
         ["Two ImageNet models tied on FID. In the largest human study of",
          "generative models, people were asked to tell their images from real."],
         v,
         ["People were fooled nearly twice as often by DiT-XL/2. FID, on an",
          "ImageNet classifier's features, saw a tie."],
         FEED_TOTAL)


def feed_08():
    items = [("Which failure", "lost quality or lost variety: one number cannot say"),
             ("Beyond two moments", "a Gaussian blob with the right moments scores like perfect"),
             ("Sample count", "biased upward by roughly K/N"),
             ("The pipeline", "resizing, JPEG and code move it more than models differ"),
             ("What people see", "and the prompt, which it never reads")]
    v = box(72, 500, 936, 600, "#ffffff", RULE_SOLID)
    y = 566
    for head, body in items:
        v += txt(110, y, head, 30, INK, SERIF, 400)
        v += mono(110, y + 38, body, 21, MUTED)
        y += 110
    emit("feed", 8, "read-the-article",
         ["What one number", "hides."],
         ["FID, the headline score for image generators, measured against",
          "precision, coverage, sample count and people, in a toy you can run."],
         v,
         ["Read FID beside precision, coverage and a check by people."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
