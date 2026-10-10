#!/usr/bin/env python3
"""LinkedIn carousel frames — 4:5, built in the diagram-design skin.

blog-visuals stops at prompts because image models mangle typography. Built here
instead, the frames get real Instrument Serif headlines and the post's own numbers.
The illustration prompts in linkedin-prompts.md remain the alternative route.

Run:  python3 _linkedin.py           # all frames
      python3 _linkedin.py 03 05     # only those
"""
import math
import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, box, cell, masked, mono,
                    rasterize, svg_doc, txt)

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1080, 1350
M = 80
MID = VW / 2
SER2 = "#5e7a9b"

SLUGS = {1: "one-operator", 2: "mean-minus-centre", 3: "one-bad-pixel",
         4: "ksize-three", 5: "sigma-is-a-ruler", 6: "the-factor"}


def frame(num, total, kicker, headline, deck, visual, takeaway, cta=None):
    s = ""
    s += mono(M, 120, kicker, size=15, fill=SOFT, anchor="start", track="0.24em", weight="500")
    s += mono(VW - M, 120, f"{num} / {total}", size=15, fill=ACCENT if num == total else SOFT,
              anchor="end", track="0.24em", weight="500")
    s += f'<line x1="{M}" y1="148" x2="{VW - M}" y2="148" stroke="{RULE}" stroke-width="1"/>'
    y = 232
    for line in headline:
        s += txt(M, y, line, size=58, fill=INK, family=SERIF, anchor="start")
        y += 68
    y += 6
    for line in deck:
        s += txt(M, y, line, size=21, fill=MUTED, family=SANS, anchor="start")
        y += 30
    s += visual
    s += f'<line x1="{M}" y1="1176" x2="{VW - M}" y2="1176" stroke="{RULE}" stroke-width="1"/>'
    ty = 1216
    for line in takeaway:
        s += txt(M, ty, line, size=22, fill=INK, family=SANS, anchor="start", weight="500")
        ty += 30
    if cta:
        s += mono(M, 1300, cta, size=14, fill=ACCENT, anchor="start", track="0.16em")
    else:
        s += mono(M, 1300, "the laplacian by hand", size=14, fill=SOFT, anchor="start", track="0.16em")
    s += mono(VW - M, 1300, "canery", size=14, fill=SOFT, anchor="end", track="0.24em")
    svg = svg_doc(VW, VH, s)
    stem = f"linkedin-{num:02d}-{SLUGS[num]}"
    (HERE / f"{stem}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    (HERE / f"{stem}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>{stem}</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / f"{stem}.svg", HERE / f"{stem}.png", VW, VH, svg_markup=svg)
    print(f"  {stem}.png  ({VW}x{VH} @2x)")


def big_stencil(x, y, w, cw=96, hi=None, fill_neg=True):
    out = ""
    for r in range(3):
        for c in range(3):
            v = w[r][c]
            focal = hi and (r, c) in hi
            if focal:
                fill, stroke, tcol = ACCENT_TINT, ACCENT, ACCENT
            elif fill_neg and v < 0:
                fill, stroke, tcol = "rgba(45,49,66,0.10)", "rgba(45,49,66,0.30)", INK
            else:
                fill, stroke, tcol = "#ffffff", "rgba(45,49,66,0.26)", (SOFT if v == 0 else INK)
            out += cell(x + c * cw, y + r * cw, cw, cw, str(v).replace("-", "−"),
                        fill=fill, stroke=stroke, tcolor=tcol, size=30, weight="600")
    return out


def big_window(x, y, vals, cw=96, hi=None):
    out = ""
    for r in range(3):
        for c in range(3):
            v = vals[r][c]
            focal = hi and (r, c) in hi
            centre = (r, c) == (1, 1)
            if focal:
                fill, stroke, tcol = ACCENT_TINT, ACCENT, ACCENT
            elif centre:
                fill, stroke, tcol = "rgba(45,49,66,0.10)", INK, INK
            elif v == 200:
                fill, stroke, tcol = "rgba(45,49,66,0.05)", "rgba(45,49,66,0.26)", INK
            else:
                fill, stroke, tcol = "#ffffff", "rgba(45,49,66,0.26)", INK
            out += cell(x + c * cw, y + r * cw, cw, cw, v, fill=fill, stroke=stroke, tcolor=tcol,
                        size=30, weight="600")
    return out


# ------------------------------------------------------------------ 01
def f01():
    v = ""
    v += mono(M, 500, "the whole operator", size=15, fill=SOFT, anchor="start", track="0.14em")
    v += big_stencil(M, 524, [[0, 1, 0], [1, -4, 1], [0, 1, 0]], hi={(1, 1)}, fill_neg=False)
    jobs = [("sharpen", "add it back"), ("find the edge", "locate its zero"),
            ("pick the scale", "σ² × it, find the extremum"), ("split the octaves", "store it per level"),
            ("keep it, not the pixels", "Poisson editing")]
    x1 = M + 3 * 96 + 32
    for i, (job, how) in enumerate(jobs):
        y = 552 + i * 66
        v += f'<line x1="{x1}" y1="{y}" x2="{x1 + 40}" y2="{y}" stroke="{MUTED}" stroke-width="2"/>'
        v += txt(x1 + 56, y + 7, job, size=24, fill=INK, family=SANS, anchor="start", weight="600")
        v += mono(x1 + 56, y + 32, how, size=14, fill=SOFT, anchor="start", track="0.06em")
    v += masked(MID, 920, "∂L/∂s = ½ ∇²L", size=30, fill=ACCENT, family=SERIF)
    v += mono(MID, 964, "blur a little; the difference from the original is the Laplacian", size=15, fill=MUTED)
    v += mono(MID, 990, "exactly, on smooth data", size=15, fill=MUTED)
    frame(1, 6, "edges · blobs · pyramids · sharpening",
          ["One operator,", "five jobs."],
          ["The Laplacian is what Gaussian blur removes, per unit of",
           "scale. Everything it is used for is a consequence of that."],
          v,
          ["Sharpening, zero-crossing edges, blob scale selection, the",
           "Laplacian pyramid and Poisson editing are one identity, five ways."])


# ------------------------------------------------------------------ 02
def f02():
    v = ""
    v += mono(M, 500, "the window at the edge pixel", size=15, fill=SOFT, anchor="start", track="0.14em")
    v += big_window(M, 524, [[40, 40, 200], [40, 40, 200], [40, 40, 200]], hi={(0, 1), (2, 1), (1, 0), (1, 2)})
    rx = M + 3 * 96 + 48
    v += txt(rx, 570, "neighbour mean", size=21, fill=MUTED, family=SANS, anchor="start")
    v += txt(rx, 604, "(40 + 40 + 40 + 200) / 4 = 80", size=22, fill=INK, family=MONO, anchor="start", weight="500")
    v += txt(rx, 660, "minus the centre", size=21, fill=MUTED, family=SANS, anchor="start")
    v += txt(rx, 694, "80 − 40 = 40", size=22, fill=INK, family=MONO, anchor="start", weight="500")
    v += txt(rx, 750, "times four", size=21, fill=MUTED, family=SANS, anchor="start")
    v += txt(rx, 784, "= 160", size=30, fill=ACCENT, family=MONO, anchor="start", weight="600")
    v += f'<line x1="{M}" y1="860" x2="{VW - M}" y2="860" stroke="{RULE}" stroke-width="1"/>'
    v += txt(M, 912, "At a hot pixel of 255 among 40s: mean 40 − 255 = −215, × 4 = −860.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 944, "Flat region: mean = centre, so 0. A ramp: also 0.", size=20, fill=MUTED, family=SANS, anchor="start")
    v += txt(M, 1000, "Brighter than the neighbourhood expects → negative.", size=20, fill=MUTED, family=SANS, anchor="start")
    v += txt(M, 1032, "Darker → positive. That is why sharpening subtracts it.", size=20, fill=MUTED, family=SANS, anchor="start")
    frame(2, 6, "the same five products, read differently",
          ["Neighbour average,", "minus the centre."],
          ["The four-neighbour stencil asks one question: how far is",
           "this pixel from what its neighbours predict? Four times that."],
          v,
          ["A pixel that disagrees with its neighbours by δ scores 4δ,",
           "whatever caused the disagreement. Edges and defects alike."])


# ------------------------------------------------------------------ 03
def f03():
    v = ""
    v += mono(M, 500, "the same window, one bad pixel three columns from nothing", size=15, fill=SOFT, anchor="start", track="0.14em")
    v += big_window(M, 524, [[40, 40, 200], [255, 40, 200], [40, 40, 200]], hi={(1, 0)})
    rx = M + 3 * 96 + 48
    v += txt(rx, 570, "neighbour sum", size=21, fill=MUTED, family=SANS, anchor="start")
    v += txt(rx, 604, "40 + 40 + 255 + 200 = 535", size=22, fill=INK, family=MONO, anchor="start", weight="500")
    v += txt(rx, 660, "minus four times the centre", size=21, fill=MUTED, family=SANS, anchor="start")
    v += txt(rx, 694, "535 − 160 = 375", size=30, fill=ACCENT, family=MONO, anchor="start", weight="600")
    v += txt(rx, 750, "was 160 without it", size=21, fill=MUTED, family=SANS, anchor="start")
    v += txt(rx, 784, "a 134% error", size=22, fill=INK, family=MONO, anchor="start", weight="500")
    v += f'<line x1="{M}" y1="860" x2="{VW - M}" y2="860" stroke="{RULE}" stroke-width="1"/>'
    # smoothing table
    cols = [("", 300), ("raw", 620), ("after σ = 0.8", 860)]
    for lab, x in cols:
        v += mono(x, 904, lab, size=15, fill=SOFT, track="0.10em")
    rows = [("clean edge", "160", "45.3"), ("with the bad pixel", "375", "21.1"), ("error", "+215", "−24")]
    for i, (a, b, c) in enumerate(rows):
        y = 948 + i * 40
        v += txt(M, y, a, size=20, fill=INK, family=SANS, anchor="start")
        v += txt(620, y, b, size=22, fill=INK if i < 2 else ACCENT, family=MONO, weight="500")
        v += txt(860, y, c, size=22, fill=INK if i < 2 else ACCENT, family=MONO, weight="500")
    v += mono(M, 1108, "the damage falls nine times over; the relative error is still 53%, because σ = 0.8 < one pixel", size=13, fill=SOFT, anchor="start")
    frame(3, 6, "why nobody runs the raw stencil",
          ["One bad pixel.", "A 134% error."],
          ["At its own location the hot pixel scores −860, 5.4 times the",
           "genuine edge. At the edge pixel next to it, 375 instead of 160."],
          v,
          ["Smooth first. Every discrete Laplacian without a σ is a defect",
           "detector first and an edge detector second."])


# ------------------------------------------------------------------ 04
def f04():
    v = ""
    v += mono(M, 500, "cv2.Laplacian(img, CV_64F, ksize=1)", size=15, fill=SOFT, anchor="start", track="0.06em")
    v += big_stencil(M, 524, [[0, 1, 0], [1, -4, 1], [0, 1, 0]], cw=88)
    v += mono(M + 132, 830, "≈ 1 × ∇²", size=22, fill=INK, weight="500")
    v += mono(M + 132, 862, "at the edge: 160", size=15, fill=MUTED)
    x2 = VW - M - 3 * 88
    v += mono(VW - M, 500, "cv2.Laplacian(img, CV_64F, ksize=3)", size=15, fill=ACCENT, anchor="end", track="0.06em")
    v += big_stencil(x2, 524, [[2, 0, 2], [0, -8, 0], [2, 0, 2]], cw=88, hi={(1, 1)})
    v += mono(x2 + 132, 830, "≈ 4 × ∇²", size=22, fill=ACCENT, weight="500")
    v += mono(x2 + 132, 862, "at the edge: 640", size=15, fill=MUTED)
    v += f'<line x1="{M}" y1="912" x2="{VW - M}" y2="912" stroke="{RULE}" stroke-width="1"/>'
    v += txt(M, 960, "The docs say Sobel second derivatives. The source says a", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 992, "precomputed 3×3 — and it is the Sobel pair summed: diagonals only,", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1024, "four times the scale. A hot pixel now spills onto its diagonal", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1056, "neighbours instead of the ones beside it.", size=20, fill=INK, family=SANS, anchor="start")
    v += mono(M, 1112, "pass scale=0.25 to compare — on smooth data only", size=15, fill=ACCENT, anchor="start", track="0.06em")
    frame(4, 6, "the library is not the math",
          ["ksize=3 is not", "a smoother ksize=1."],
          ["Change one argument and every value quadruples, the",
           "threshold you tuned yesterday passes everything, and the",
           "hot pixel's smear moves one diagonal step."],
          v,
          ["There are at least five 3×3 Laplacians. They agree on smooth",
           "data and disagree on exactly the pixels you care about."])


# ------------------------------------------------------------------ 05
def f05():
    v = ""
    x0, y0, w, h = M + 40, 520, VW - 2 * M - 40, 400
    smin, smax = 0.5, 4.0
    tx = lambda sg: x0 + (sg - smin) / (smax - smin) * w
    ty = lambda val: y0 + h - val / 140 * h
    v += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1.5"/>'
    v += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1.5"/>'
    for sg in (1, 2, 3, 4):
        v += mono(tx(sg), y0 + h + 28, f"σ = {sg}", size=15, fill=SOFT)
    bar = lambda sg: 160 * 3 / (math.sqrt(2 * math.pi) * sg) * math.exp(-9 / (8 * sg * sg))
    disc = lambda sg: 160 * 9 / (sg * sg) * math.exp(-9 / (2 * sg * sg))
    sgs = [smin + (smax - smin) * i / 280 for i in range(281)]
    for f, col, sw in ((bar, SER2, 3), (disc, ACCENT, 4)):
        pts = " ".join(f"{tx(g):.1f},{ty(f(g)):.1f}" for g in sgs)
        v += f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round"/>'
    for sg, val, col, lab, dx in ((1.5, 77.4, SER2, "bar of width 3: peak at σ = w/2 = 1.5", -60),
                                  (2.121, 117.7, ACCENT, "disc of radius 3: peak at σ = r/√2 = 2.12", 40)):
        v += f'<line x1="{tx(sg)}" y1="{ty(val)}" x2="{tx(sg)}" y2="{y0 + h}" stroke="{col}" stroke-width="1.5" stroke-dasharray="5,5"/>'
        v += f'<circle cx="{tx(sg)}" cy="{ty(val)}" r="8" fill="{col}"/>'
        v += masked(tx(sg) + dx, ty(val) - 24, lab, size=15, fill=col, anchor="middle" if col == SER2 else "start")
    v += mono(M, 1000, "model — closed forms, contrast 160, nothing measured", size=13, fill=SOFT, anchor="start", track="0.10em")
    v += txt(M, 1052, "The raw response falls as 1/σ², so the smallest σ always wins.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1084, "Multiply by σ² and the σ at the peak is the size of the structure.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1128, "That derivation is why blob_log reports radius = √2 σ.", size=20, fill=MUTED, family=SANS, anchor="start")
    frame(5, 6, "scale selection",
          ["Multiply by σ²,", "and σ is a ruler."],
          ["Lindeberg's normalisation turns the Laplacian into a",
           "measuring instrument: search σ, read off the size."],
          v,
          ["A difference of Gaussians at a constant ratio carries the σ²",
           "for free — which is why SIFT and blob_dog can use it instead."])


# ------------------------------------------------------------------ 06
def f06():
    v = ""
    rows = [("five-point", "cv2.Laplacian(…, ksize=1)", "× 1", False),
            ("diagonal", "cv2.Laplacian(…, ksize=3)", "× 4", True),
            ("LoG", "scipy.ndimage.gaussian_laplace", "no σ²", False),
            ("blob scale", "skimage.feature.blob_log", "× σ²", False),
            ("blob scale", "skimage.feature.blob_dog", "× 1/(k−1)", False),
            ("pyramid", "cv2.pyrDown · cv2.pyrUp", "exact", False)]
    y = 500
    for job, call, factor, focal in rows:
        col = ACCENT if focal else INK
        v += txt(M, y + 30, job, size=20, fill=col, family=SANS, anchor="start", weight="600")
        v += box(M + 200, y, 520, 48, fill=ACCENT_TINT if focal else "#ffffff", stroke=col)
        v += mono(M + 460, y + 30, call, size=17, fill=col, weight="500")
        v += txt(VW - M, y + 30, factor, size=22, fill=ACCENT if focal else MUTED, family=MONO, anchor="end", weight="600")
        y += 72
    v += f'<line x1="{M}" y1="{y + 8}" x2="{VW - M}" y2="{y + 8}" stroke="{RULE}" stroke-width="1"/>'
    v += txt(M, y + 56, "Never write the Laplacian into 8 bits: the negative half is", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, y + 88, "the half the zero-crossing needs, and convertScaleAbs", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, y + 120, "throws it away before you can look for one.", size=20, fill=INK, family=SANS, anchor="start")
    frame(6, 6, "the tooling map",
          ["The library is the", "math — with a factor."],
          ["Every call applies a scale the docs mention on a different",
           "page. Written on the arrow, none of them is a surprise."],
          v,
          ["Sixteen figures, one 5×5 patch, thirty-one sources, and every",
           "number worked by hand before any library was named."],
          cta="read it on canery →")


FRAMES = {"01": f01, "02": f02, "03": f03, "04": f04, "05": f05, "06": f06}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FRAMES)
    for kk in want:
        FRAMES[kk]()
