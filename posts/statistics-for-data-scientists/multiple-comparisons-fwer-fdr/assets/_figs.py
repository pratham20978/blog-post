"""Build the Part 9 figures (private build script, never uploaded).

Every coordinate is computed here from the lab's captures (lab/captures/results-full.json) or from
the shipped data (lab/data/hedenfalk.csv). Writes assets/fig-NN-<name>.html in the diagram-design
article profile (viewBox 720 wide, text >= 11 px at 720 px).
Usage: python assets/_figs.py
"""
import html
import json
import math
import pathlib
import sys
from decimal import ROUND_HALF_UP, Decimal

HERE = pathlib.Path(__file__).resolve().parent
POST = HERE.parent
sys.path.insert(0, str(POST / "lab"))
import multiplicity as lab  # noqa: E402  (the lab's own rules, for the data figures)
import numpy as np  # noqa: E402

RES = json.loads((POST / "lab" / "captures" / "results-full.json").read_text())
C = dict(paper="#f5f5f5", ink="#2d3142", muted="#4f5d75", soft="#7a8399", rule="rgba(45,49,66,0.12)",
         rule2="#bfc0c0", accent="#eb6c36", tint="rgba(235,108,54,0.08)", sage="#7c8f6f", blue="#5e7a9b",
         mustard="#b8915a", rust="#9c6b50", slate="#6e6479", white="#ffffff")
SANS, MONO, SERIF = "'Geist', sans-serif", "'Geist Mono', monospace", "'Instrument Serif', serif"
W = 720


def hp(x, d=1):
    """Round half up once from the exact decimal, as the lab's pc() does."""
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))


def pct(x, d=1):
    return hp(float(Decimal(repr(float(x))) * 100), d) + "%"


def T(x, y, s, size=12, fam=MONO, fill=None, anchor="start", weight=None, italic=False):
    attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'fill="{fill or C["muted"]}"', f'font-size="{size}"',
             f'font-family="{fam}"', f'text-anchor="{anchor}"']
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if italic:
        attrs.append('font-style="italic"')
    return f'<text {" ".join(attrs)}>{html.escape(s)}</text>'


def L(x1, y1, x2, y2, stroke=None, w=1.0, dash=None, cap=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    c = f' stroke-linecap="{cap}"' if cap else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke or C["muted"]}" stroke-width="{w}"{d}{c}/>'


def R(x, y, w, h, fill="none", stroke=None, sw=1.0, rx=0, dash=None, opacity=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{o}{s}{d}/>'


def mask(x, y, w, h):
    return R(x, y, w, h, fill=C["paper"])


def PL(points, stroke, w=1.6, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"{d}/>'


def CIRC(x, y, r, fill, stroke=None, sw=1.0):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{s}/>'


def page(name, eyebrow, title, body, h):
    svg = (f'<svg viewBox="0 0 {W} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{html.escape(title)}">\n'
           f'<rect width="100%" height="100%" fill="{C["paper"]}"/>\n' + "\n".join(body) + "\n</svg>")
    doc = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>{html.escape(title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Geist',system-ui,sans-serif;background:#f5f5f5;color:#2d3142;padding:2rem}}
  .frame{{max-width:1200px;margin:0 auto}}
  .eyebrow{{font-family:'Geist Mono',monospace;font-size:.66rem;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:#4f5d75;margin-bottom:.5rem}}
  h1{{font-family:'Instrument Serif',serif;font-weight:400;font-size:2rem;line-height:1.15;margin-bottom:1.5rem}}
  svg{{width:100%;height:auto;display:block}}
</style></head><body><div class="frame">
<p class="eyebrow">{html.escape(eyebrow)}</p><h1>{html.escape(title)}</h1>
{svg}
</div></body></html>
"""
    (HERE / f"{name}.html").write_text(doc, encoding="utf-8")
    print("wrote", name)


class Lin:
    def __init__(self, d0, d1, r0, r1):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v):
        return self.r0 + (v - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)


class Log:
    def __init__(self, d0, d1, r0, r1):
        self.a, self.b, self.r0, self.r1 = math.log10(d0), math.log10(d1), r0, r1

    def __call__(self, v):
        return self.r0 + (math.log10(v) - self.a) / (self.b - self.a) * (self.r1 - self.r0)


def yaxis(body, sy, ticks, x0, x1, fmt, title=None, title_x=None):
    for v in ticks:
        y = sy(v)
        body.append(L(x0, y, x1, y, C["rule"], 1))
        body.append(T(x0 - 8, y + 4, fmt(v), 12, MONO, C["muted"], "end"))
    if title:
        body.append(T(title_x if title_x is not None else x0, sy(ticks[-1]) - 14, title, 12, MONO, C["muted"], "start"))


def xaxis(body, sx, ticks, y, fmt, title=None, title_y=None, x_title=None):
    body.append(L(sx(ticks[0]), y, sx(ticks[-1]), y, C["ink"], 1))
    for v in ticks:
        x = sx(v)
        body.append(L(x, y, x, y + 5, C["ink"], 1))
        body.append(T(x, y + 20, fmt(v), 12, MONO, C["muted"], "middle"))
    if title:
        body.append(T(x_title if x_title is not None else (sx(ticks[0]) + sx(ticks[-1])) / 2,
                      title_y or y + 42, title, 12, MONO, C["muted"], "middle"))


# ---------------------------------------------------------------------------------------------

def fig01():
    _, null_ge, p = lab.load_hedenfalk()
    # Right-closed bins (0, 0.05], (0.05, 0.10], ... decided in exact integers (p = null_ge / 317,000), so the
    # first bar holds the genes with p <= 0.05 that its label counts; one gene sits exactly on 0.05.
    assert null_ge.min() >= 1 and np.array_equal(null_ge / 317_000, p)
    counts = np.bincount((null_ge - 1) // (317_000 // 20), minlength=20)
    assert counts.size == 20 and counts[0] == int((p <= 0.05).sum())
    pi_half = RES["procedures"]["pi0_lambda_half"]
    floor = pi_half * p.size * 0.05
    h = 400
    x0, x1, y0, y1 = 64, 700, 330, 40
    sx, sy = Lin(0, 1, x0, x1), Lin(0, 650, y0, y1)
    b = []
    yaxis(b, sy, [0, 100, 200, 300, 400, 500, 600], x0, x1, lambda v: str(v), "genes per bin of width 0.05", x0)
    bw = (x1 - x0) / 20
    for i, c in enumerate(counts):
        fill, stroke = (C["tint"], C["accent"]) if i == 0 else (C["white"], C["ink"])
        b.append(R(sx(i * 0.05) + 2, sy(c), bw - 4, y0 - sy(c), fill, stroke, 1))
    b.append(L(x0, sy(floor), x1, sy(floor), C["ink"], 1.4, "6,4"))
    lab_y = sy(floor) - 13                     # the knockout stays clear of the 0.85-0.90 bar's top edge
    b.append(mask(408, lab_y - 14, 290, 18))
    b.append(T(696, lab_y, f"null floor: π0 × 3,170 × 0.05 ≈ {hp(floor, 0)}", 12, MONO, C["ink"], "end"))
    b.append(T(sx(0.05) + 14, sy(counts[0]) + 16, f"{int((p <= 0.05).sum())} genes with p ≤ 0.05", 13, SANS, C["ink"], "start", 600))
    b.append(T(sx(0.05) + 14, sy(counts[0]) + 34, f"about {hp(floor, 0)} of them expected noise", 13, SANS, C["muted"]))
    b.append(T(sx(0.05) + 14, sy(counts[0]) + 52, f"(π0 = {hp(pi_half, 3)} at λ = 0.5)", 12, MONO, C["muted"]))
    xaxis(b, sx, [0, 0.2, 0.4, 0.6, 0.8, 1.0], y0, lambda v: f"{v:.1f}", "p-value (3,170 Hedenfalk genes)", 372)
    page("fig-01-hedenfalk-histogram", "Data · Histogram", "The Hedenfalk p-values over their null floor", b, h)


def fig02():
    pr = RES["procedures"]
    ps = np.array(pr["sorted_p_first_300"])
    m, a, H = pr["m"], 0.05, pr["harmonic_m"]
    pi0 = pr["pi0"]["qvalue 2.x"]
    h = 440
    x0, x1, y0, y1 = 72, 556, 380, 30
    sx, sy = Lin(0, 300, x0, x1), Log(1e-6, 1e-2, y0, y1)
    b = []
    yaxis(b, sy, [1e-6, 1e-5, 1e-4, 1e-3, 1e-2], x0, x1, lambda v: f"1e{int(math.log10(v))}", "sorted p-value, log scale", x0)
    k = np.arange(1, 301)
    lines = [("Storey q", k * a / (m * pi0), C["accent"], 1.6, None),
             ("BH", k * a / m, C["ink"], 1.6, None),
             ("BY", k * a / (m * H), C["sage"], 1.6, "6,4"),
             ("Holm", a / (m - k + 1), C["blue"], 1.4, None),
             ("Bonferroni", np.full(300, a / m), C["muted"], 1.2, "2,3")]
    for name, yv, col, w, dash in lines:
        pts = [(sx(i), sy(v)) for i, v in zip(k, yv) if 1e-6 <= v <= 1e-2]
        b.append(PL(pts, col, w, dash))
    for i, v in zip(k, ps):
        b.append(CIRC(sx(i), sy(v), 1.7, C["ink"]))
    # crossings: last rank under each step-up line, first failure for step-down
    marks = [(int(pr["counts_5pct"]["Storey q"]), "Storey q: 162", C["accent"]),
             (int(pr["counts_5pct"]["BH"]), "BH: 94", C["ink"])]
    for rank, label, col in marks:
        x = sx(rank)
        b.append(L(x, y0, x, sy(ps[rank - 1]) + 6, col, 1, "3,3"))
    # direct labels at the right edge
    b.append(T(562, sy(300 * a / (m * pi0)) - 2, "Storey q", 12, MONO, C["ink"], "start", 600))
    b.append(T(562, sy(300 * a / (m * pi0)) + 13, "kα/(m·π0)", 11, MONO, C["muted"]))
    b.append(T(562, sy(300 * a / m) + 12, "BH  kα/m", 12, MONO, C["ink"], "start", 600))
    b.append(T(562, sy(300 * a / (m * H)) + 4, "BY  kα/(m·H_m)", 12, MONO, C["ink"], "start", 600))
    b.append(T(562, sy(a / (m - 299)) - 8, "Holm", 12, MONO, C["ink"], "start", 600))
    b.append(T(562, sy(a / m) + 16, "Bonferroni α/m", 12, MONO, C["ink"], "start", 600))
    b.append(mask(sx(94) - 30, y0 - 46, 60, 18))
    b.append(T(sx(94), y0 - 33, "BH 94", 12, MONO, C["ink"], "middle"))
    b.append(mask(sx(162) - 46, y0 - 46, 92, 18))
    b.append(T(sx(162), y0 - 33, "Storey q 162", 12, MONO, C["ink"], "middle"))
    gy = sy(1e-5)                                  # the note sits between Bonferroni's line and the 1e-5 grid line
    b.append(mask(sx(22) - 4, gy - 15, 254, 14.4))  # breaks the two rank lines behind it, not the grid line
    b.append(T(sx(22), gy - 3, "Bonferroni and Holm stop at rank 2", 12, MONO, C["ink"]))
    xaxis(b, sx, [0, 50, 100, 150, 200, 250, 300], y0, lambda v: str(v), "rank of the p-value (first 300 of 3,170)", 420, 314)
    page("fig-02-rejection-lines", "Data · Rejection boundaries", "Five rules as five lines through the sorted p-values", b, h)


def fig03():
    g = RES["pi0_lambda_grid"]
    pr = RES["procedures"]["pi0"]
    h = 400
    x0, x1, y0, y1 = 72, 696, 330, 40
    sx, sy = Lin(0, 1, x0, x1), Lin(0.60, 0.90, y0, y1)
    b = []
    yaxis(b, sy, [0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90], x0, x1, lambda v: f"{v:.2f}", "π0(λ): share of p ≥ λ, over 1 − λ", x0)
    paper = g["paper 2003"]
    for lam, v in zip(paper["lambda"], paper["raw"]):
        if v <= 0.90:
            b.append(CIRC(sx(lam), sy(v), 1.6, C["soft"]))
    q2 = g["qvalue 2.x"]
    for lam, v in zip(q2["lambda"], q2["raw"]):
        b.append(CIRC(sx(lam), sy(v), 3.2, C["white"], C["ink"], 1.2))
    styles = {"paper 2003": (C["muted"], "5,3"), "qvalue 2.x": (C["accent"], None), "qvalue 1.x": (C["sage"], "2,3")}
    for name, (col, dash) in styles.items():
        cv = g[name]
        lam = np.array(cv["curve_x"])
        lo, hi = min(g[name]["lambda"]), {"paper 2003": 1.0, "qvalue 2.x": 0.95, "qvalue 1.x": 0.90}[name]
        pts = [(sx(x), sy(y)) for x, y in zip(lam, cv["curve_y"]) if lo <= x <= hi + 1e-9]
        b.append(PL(pts, col, 1.8, dash))
    ends = [("paper 2003", 1.0, "paper 2003 · spline at λ = 1"), ("qvalue 2.x", 0.95, "qvalue 2.x · at λ = 0.95"),
            ("qvalue 1.x", 0.90, "qvalue 1.x · at λ = 0.90")]
    lx, ly = x0 + 14, sy(0.655)
    for i, (name, at, label) in enumerate(ends):
        v = pr[name]
        col, dash = styles[name]
        b.append(CIRC(sx(at), sy(v), 4.2, col))
        y = ly + i * 21
        b.append(L(lx, y - 4, lx + 26, y - 4, col, 1.8, dash))
        b.append(T(lx + 34, y, f"{hp(v, 4)}", 13, MONO, C["ink"], "start", 600))
        b.append(T(lx + 94, y, label, 12, MONO, C["muted"]))
    xaxis(b, sx, [0, 0.2, 0.4, 0.6, 0.8, 1.0], y0, lambda v: f"{v:.1f}", "λ (tuning threshold)", 372, 316)
    page("fig-03-pi0-smoother", "Data · π0 estimate", "Reading π0 off a smoothed curve, three ways", b, h)


def fig05():
    d = RES["dependence"]
    rhos = d["rhos"]
    h = 420
    x0, x1, y0, y1 = 64, 520, 360, 40
    sx, sy = Lin(0, 0.5, x0, x1), Lin(0, 0.30, y0, y1)
    b = []
    yaxis(b, sy, [0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], x0, x1, lambda v: f"{v:.2f}", "false discovery rate (mean FDP)", x0)
    b.append(L(x0, sy(0.05), x1, sy(0.05), C["ink"], 1, "6,4"))
    b.append(L(x0, sy(0.05 * 2124 / 3170), x1, sy(0.05 * 2124 / 3170), C["soft"], 1, "2,3"))
    series = [("Storey q", C["accent"], 2.0), ("BH", C["ink"], 1.8), ("BY", C["sage"], 1.8)]
    ends = {}
    for name, col, w in series:
        pts = [(sx(r), sy(d["by_rho"][str(r)][name]["FDR"])) for r in rhos]
        b.append(PL(pts, col, w))
        for r in rhos:
            e = d["by_rho"][str(r)][name]
            ylo, yhi = sy(e["FDR"] - 2 * e["FDR_se"]), sy(e["FDR"] + 2 * e["FDR_se"])
            b.append(L(sx(r), ylo, sx(r), yhi, col, 1.2))
            b.append(CIRC(sx(r), sy(e["FDR"]), 3.4 if name == "Storey q" else 3, col))
        ends[name] = d["by_rho"]["0.5"][name]["FDR"]
    b.append(T(530, sy(ends["Storey q"]) + 4, f"Storey q  {hp(ends['Storey q'], 3)}", 13, MONO, C["ink"], "start", 600))
    b.append(T(530, sy(ends["BH"]) - 6, f"BH  {hp(ends['BH'], 3)}", 13, MONO, C["ink"]))
    b.append(T(530, sy(ends["BY"]) - 4, f"BY  {hp(ends['BY'], 3)}", 13, MONO, C["ink"]))
    b.append(mask(sx(0.31) - 2, sy(0.05) - 17, 124, 15))
    b.append(T(sx(0.31), sy(0.05) - 6, "target q = 0.05", 12, MONO, C["ink"]))
    b.append(mask(x0 + 222, sy(0.0335) - 16, 236, 15))
    b.append(T(x0 + 224, sy(0.0335) - 5, "BH's promise q·m0/m = 0.0335", 12, MONO, C["muted"]))
    xaxis(b, sx, [0, 0.1, 0.2, 0.3, 0.4, 0.5], y0, lambda v: f"{v:.1f}", "correlation ρ between every pair of tests", 400, 292)
    b.append(T(x0, 424, "bars: ±2 MCSE, R = 20,000 studies per point", 11, MONO, C["muted"]))
    page("fig-05-fdr-vs-correlation", "Simulation · Line chart", "What correlation does to each rule's FDR", b, 436)


def fig06():
    d = RES["dependence"]
    bins = np.array(d["fdp_bins"])
    R_ = d["R"]
    h = 470
    x0, x1 = 72, 700
    sx = Lin(0, 0.5, x0, x1)
    b = []
    panels = [("0.0", 40, "ρ = 0 (independent tests)"), ("0.5", 250, "ρ = 0.5 (every pair correlated)")]
    for key, top, label in panels:
        e = d["by_rho"][key]["BH"]
        counts = np.array(e["FDP_hist"], float)
        counts[0] += e["P_D_zero"] * R_          # an empty list has FDP 0 by definition
        share = counts / R_
        y0p, y1p = top + 160, top + 20
        sy = Lin(0, 0.9, y0p, y1p)
        b.append(T(x0, top + 8, label, 13, SANS, C["ink"], "start", 600))
        for v in (0, 0.3, 0.6, 0.9):
            b.append(L(x0, sy(v), x1, sy(v), C["rule"], 1))
            b.append(T(x0 - 8, sy(v) + 4, f"{int(v * 100)}%", 12, MONO, C["muted"], "end"))
        bw = sx(0.02) - sx(0)
        for i, s in enumerate(share[:25]):
            if s <= 0:
                continue
            hgt = max(y0p - sy(s), 1)
            big = bins[i] >= 0.10
            b.append(R(sx(bins[i]) + 1, y0p - hgt, bw - 2, hgt, C["tint"] if big else C["white"], C["accent"] if big else C["ink"], 1))
        b.append(L(sx(0.10), y1p - 6, sx(0.10), y0p, C["accent"], 1.2, "4,3"))
        b.append(L(sx(e["FDR"]), y1p - 6, sx(e["FDR"]), y0p, C["ink"], 1.2))
        tx = 470
        b.append(T(tx, top + 40, f"FDR (mean FDP) = {hp(e['FDR'], 4)}", 12, MONO, C["ink"]))
        b.append(T(tx, top + 58, f"P(FDP > 10%) = {pct(e['P_FDP_gt_10'], 2)}", 12, MONO, C["ink"], "start", 600))
        b.append(T(tx, top + 76, f"no discoveries: {pct(e['P_D_zero'], 1)} of studies", 12, MONO, C["muted"]))
        if key == "0.5":
            b.append(T(tx, top + 94, f"among studies with a list: {pct(e['P_FDP_gt_10_given_D'], 1)}", 12, MONO, C["muted"]))
        b.append(L(x0, y0p, x1, y0p, C["ink"], 1))
        for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
            b.append(L(sx(v), y0p, sx(v), y0p + 5, C["ink"], 1))
            b.append(T(sx(v), y0p + 19, f"{v:.1f}", 12, MONO, C["muted"], "middle"))
    b.append(T((x0 + x1) / 2, 458, "false discovery proportion of one study's BH list at q = 0.05 (R = 20,000 studies each)", 12, MONO, C["muted"], "middle"))
    page("fig-06-fdp-distribution", "Simulation · Histograms", "Same FDR, different promise", b, h)


def fig07():
    m, a = 5, 0.05
    H = sum(1 / k for k in range(1, m + 1))
    h = 440
    x0, x1 = 150, 520
    sx = Lin(0, a, x0, x1)
    b = []
    top = 56
    # slots and BH thresholds
    b.append(T(x0, 28, "the first α of the p-value axis, cut into m = 5 slots of width α/m", 12, MONO, C["muted"]))
    for k in range(m + 1):
        b.append(L(sx(k * a / m), top - 6, sx(k * a / m), top + 5 * 58 + 6, C["rule2"], 1))
    for k in range(1, m + 1):
        b.append(T(sx(k * a / m), top - 12, "α/m" if k == 1 else f"{k}α/m", 11, MONO, C["muted"], "middle"))
    rows_y = [top + 22 + (k - 1) * 58 for k in range(1, m + 1)]
    for k, y in zip(range(1, m + 1), rows_y):
        b.append(T(28, y + 5, f"event E{k}", 13, SANS, C["ink"], "start", 600))
        b.append(T(28, y + 21, f"P = α/{k} = {a / k:.4f}", 11, MONO, C["muted"]))
        b.append(L(x0, y, x1, y, C["rule"], 1))
        # k p-values inside slot k (spread evenly for display)
        left, right = sx((k - 1) * a / m), sx(k * a / m)
        for j in range(k):
            cx = left + (right - left) * (j + 0.5) / k
            b.append(CIRC(cx, y, 4.2, C["accent"] if k == m else C["ink"]))
        b.append(T(540, y + 5, "1 null p-value ≤ α/m" if k == 1 else f"{k} null p-values ≤ {k}α/m", 12, MONO, C["ink"]))
        b.append(T(540, y + 21, f"BH rejects {k}, all false", 11, MONO, C["muted"]))
    yb = top + 5 * 58 + 34
    b.append(L(28, yb - 14, 692, yb - 14, C["rule"], 1))
    b.append(T(28, yb + 6, f"FDR = α(1 + 1/2 + … + 1/{m}) = α·H_{m} = {a * H:.4f}", 13, MONO, C["ink"], "start", 600))
    b.append(T(28, yb + 26, "every other p-value sits above α; each test's p-value is still uniform on (0, 1)", 12, MONO, C["muted"]))
    b.append(T(28, yb + 44, f"at m = 3,170 the same law gives α·H_m = {RES['adversarial']['exact']['3170']['BH']:.4f}", 12, MONO, C["muted"]))
    page("fig-07-worst-case-law", "Construction · Placed", "The joint law that breaks Benjamini–Hochberg", b, h)


def fig08():
    fk = RES["forking"]
    layers = [("OUTCOME", "Which outcome?", "DV1 · DV2 · their mean", 3),
              ("SAMPLE", "When to stop?", "20 per cell · or 10 more", 2),
              ("CONDITIONS", "Which conditions?", "low–mid · low–high · mid–high · trend", 4),
              ("MODEL", "Which model?", "plain · + gender · × gender (2 tests)", 4)]
    h = 420
    b = []
    x, w, hh, gap = 40, 520, 64, 14
    total = 1
    for i, (tag, name, opts, n) in enumerate(layers):
        y = 30 + i * (hh + gap)
        total *= n
        b.append(R(x, y, w, hh, C["white"], C["ink"], 1, 6))
        tw = 10 + len(tag) * 7.2
        b.append(R(x + 10, y + 10, tw, 18, "transparent", C["muted"], 0.8, 2))
        b.append(T(x + 10 + tw / 2, y + 23, tag, 11, MONO, C["muted"], "middle"))
        b.append(T(x + 20 + tw, y + 24, name, 15, SANS, C["ink"], "start", 600))
        b.append(T(x + 10, y + 50, opts, 13, MONO, C["muted"]))
        b.append(T(x + w - 12, y + 40, f"× {n}", 15, MONO, C["ink"], "end", 600))
        b.append(T(x + w + 24, y + 30, f"{total}", 15, MONO, C["ink"], "start", 600))
        b.append(T(x + w + 24, y + 47, "tests so far", 11, MONO, C["muted"]))
    yb = 30 + 4 * (hh + gap) + 6
    b.append(R(x, yb, w, 60, C["tint"], C["accent"], 1, 6))
    b.append(T(x + 14, yb + 25, f"one reported result, {fk['tests_per_sample']} tests underneath", 15, SANS, C["ink"], "start", 600))
    rate = fk["rates"]["dummy"]["A+B+C+D"]
    b.append(T(x + 14, yb + 45, f"P(any p < .05 | no effect anywhere) = {pct(rate['rate'], 1)} ± {pct(rate['se'], 1)}", 13, MONO, C["muted"]))
    page("fig-08-forking-layers", "Researcher degrees of freedom · Layers", "Four forks, ninety-six tests", b, h)


def fig09():
    fk = RES["forking"]
    rows = ["A two DVs", "B ten more per cell", "C gender", "D three conditions", "A+B", "A+B+C", "A+B+C+D"]
    labels = {"A two DVs": "A  two outcomes", "B ten more per cell": "B  10 more per cell", "C gender": "C  gender covariate",
              "D three conditions": "D  three conditions", "A+B": "A + B", "A+B+C": "A + B + C", "A+B+C+D": "A + B + C + D"}
    h = 400
    x0, x1 = 220, 690
    sx = Lin(0, 0.7, x0, x1)
    b = []
    top, step = 52, 40
    for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7):
        b.append(L(sx(v), top - 16, sx(v), top + step * 6 + 16, C["rule"], 1))
        b.append(T(sx(v), top + step * 6 + 36, f"{int(round(v * 100))}%", 12, MONO, C["muted"], "middle"))
    b.append(L(sx(0.05), top - 16, sx(0.05), top + step * 6 + 16, C["ink"], 1, "4,3"))
    b.append(T(sx(0.05) + 4, top - 22, "nominal 5%", 11, MONO, C["ink"]))
    for i, name in enumerate(rows):
        y = top + i * step
        b.append(T(24, y + 4, labels[name], 13, SANS, C["ink"], "start", 600 if "+" in name else None))
        ours, eff, paper = fk["rates"]["dummy"][name], fk["rates"]["effect"][name], fk["paper"][name]
        b.append(L(sx(min(ours["rate"], paper, eff["rate"])), y, sx(max(ours["rate"], paper, eff["rate"])), y, C["rule2"], 2))
        b.append(f'<path d="M{sx(eff["rate"]):.1f},{y - 5:.1f} l5,5 l-5,5 l-5,-5 z" fill="{C["white"]}" stroke="{C["sage"]}" stroke-width="1.4"/>')
        b.append(CIRC(sx(paper), y, 5, C["white"], C["ink"], 1.6))
        b.append(CIRC(sx(ours["rate"]), y, 4, C["accent"]))
    yl = top + step * 6 + 58
    b.append(CIRC(30, yl - 4, 5, C["white"], C["ink"], 1.6))
    b.append(T(42, yl, "paper (15,000 samples)", 12, MONO, C["ink"]))
    b.append(CIRC(250, yl - 4, 4, C["accent"]))
    b.append(T(262, yl, "ours, dummy coding (R = 100,000)", 12, MONO, C["ink"]))
    b.append(f'<path d="M520,{yl - 9} l5,5 l-5,5 l-5,-5 z" fill="{C["white"]}" stroke="{C["sage"]}" stroke-width="1.4"/>')
    b.append(T(532, yl, "effect coding", 12, MONO, C["ink"]))
    page("fig-09-sns-reproduction", "Simulation · Dot plot", "Simmons, Nelson and Simonsohn's Table 1, rerun", b, 372)


def fig10():
    fr = RES["freedman"]
    edges = np.array(fr["log10_pF_bins"])
    h = 420
    x0, x1 = 72, 700
    sx = Lin(-6, 0, x0, x1)
    b = []
    panels = [("hist_pass1", 30, f"pass 1: all 50 regressors; F significant in {pct(fr['P_F_sig_pass1'], 1)}"),
              ("hist_pass2", 236, f"pass 2: the {hp(fr['kept'], 1)} with p < 0.25 refitted; F significant in {pct(fr['P_F_sig_pass2'], 1)}")]
    for key, top, label in panels:
        cnt = np.array(fr[key], float)
        share = cnt / fr["R"]
        # fold everything below 1e-6 into the first displayed bin
        keep = edges[:-1] >= -6
        folded = share[keep].copy()
        folded[0] += share[~keep].sum()
        left = edges[:-1][keep]
        y0p, y1p = top + 150, top + 26
        sy = Lin(0, 0.7, y0p, y1p)
        b.append(T(x0, top + 10, label, 13, SANS, C["ink"], "start", 600))
        for v in (0, 0.35, 0.7):
            b.append(L(x0, sy(v), x1, sy(v), C["rule"], 1))
            b.append(T(x0 - 8, sy(v) + 4, f"{int(v * 100)}%", 12, MONO, C["muted"], "end"))
        bw = sx(0.5) - sx(0)
        for lft, s in zip(left, folded):
            if s <= 0:
                continue
            hgt = max(y0p - sy(s), 1)
            sig = lft + 0.5 <= math.log10(0.05) + 1e-9
            b.append(R(sx(lft) + 1, y0p - hgt, bw - 2, hgt, C["tint"] if sig else C["white"], C["accent"] if sig else C["ink"], 1))
        b.append(L(sx(math.log10(0.05)), y1p - 8, sx(math.log10(0.05)), y0p, C["ink"], 1.2, "4,3"))
        b.append(L(x0, y0p, x1, y0p, C["ink"], 1))
        for v in range(-6, 1):
            b.append(L(sx(v), y0p, sx(v), y0p + 5, C["ink"], 1))
            b.append(T(sx(v), y0p + 19, "1" if v == 0 else f"1e{v}", 12, MONO, C["muted"], "middle"))
    b.append(T(sx(math.log10(0.05)) - 6, 52, "p = 0.05", 11, MONO, C["ink"], "end"))
    b.append(T((x0 + x1) / 2, 438, f"p-value of the overall F test, log scale (R = {fr['R']:,} pure-noise datasets, n = 100)", 12, MONO, C["muted"], "middle"))
    page("fig-10-freedman-screen", "Simulation · Histograms", "Screening noise until it looks significant", b, 452)


if __name__ == "__main__":
    for f in (fig01, fig02, fig03, fig05, fig06, fig07, fig08, fig09, fig10):
        f()
