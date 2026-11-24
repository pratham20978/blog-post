"""Build the Part 9 social feed cards (private build script, never uploaded).

Writes assets/social/feed-NN-<beat>.html from the locked feed shell in the blog-visuals skill.
Every value is read from lab/captures/results-full.json and every coordinate is computed here.
Text widths are measured with the installed house fonts, and the build stops if any text runs
outside its area or collides with other text. Render afterwards with blog-forge's
render_social.py, which writes the .svg and the exact-size .png and checks the lockup.
Usage: python3 assets/_social.py
"""
import html
import json
import math
import pathlib
import re
import subprocess
from decimal import ROUND_HALF_UP, Decimal

from fontTools.ttLib import TTFont
from PIL import ImageFont

HERE = pathlib.Path(__file__).resolve().parent
POST = HERE.parent
OUT = HERE / "social"
RES = json.loads((POST / "lab" / "captures" / "results-full.json").read_text())
SKILL = next(pathlib.Path("/root/.claude/skills/synced").rglob("blog-visuals/SKILL.md")).read_text()
TOTAL = 7

INK, MUTED, SOFT, SILVER, PAPER, WHITE = "#2d3142", "#4f5d75", "#7a8399", "#bfc0c0", "#f5f5f5", "#ffffff"
ACCENT, TINT, RULE = "#eb6c36", "rgba(235,108,54,0.10)", "rgba(45,49,66,0.12)"
CSS = {"serif": "'Instrument Serif',serif", "sans": "'Geist',sans-serif", "mono": "'Geist Mono',monospace"}
FILES = {("serif", 400): "InstrumentSerif-Regular.ttf", ("sans", 400): "Geist-Regular.ttf",
         ("sans", 500): "Geist-Medium.ttf", ("sans", 600): "Geist-SemiBold.ttf",
         ("mono", 400): "GeistMono-Regular.ttf", ("mono", 500): "GeistMono-Medium.ttf",
         ("mono", 600): "GeistMono-SemiBold.ttf"}
FONTDIR = pathlib.Path.home() / ".fonts"
FALLBACK = subprocess.run(["fc-match", "-f", "%{file}", "Inter"], capture_output=True, text=True).stdout.strip()
_faces, _cmaps = {}, {}


def hp(x, d):
    """Round half up once from the exact decimal, as the lab's hu() and pc() do."""
    return str(Decimal(repr(float(x))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))


def pct(x, d):
    return hp(float(Decimal(repr(float(x))) * 100), d) + "%"


def face(path, size):
    key = (path, size)
    if key not in _faces:
        _faces[key] = ImageFont.truetype(str(path), size)
    return _faces[key]


def width(s, fam, weight, size, ls=0.0):
    """Advance width in px; glyphs the house face lacks are measured in the fallback face."""
    path = FONTDIR / FILES[(fam, weight)]
    if path not in _cmaps:
        _cmaps[path] = TTFont(str(path)).getBestCmap()
    total, run, run_ok = 0.0, "", None
    for ch in s + "\0":
        ok = ch == "\0" or ord(ch) in _cmaps[path]
        if run and (ok != run_ok or ch == "\0"):
            total += face(path if run_ok else FALLBACK, size).getlength(run)
            run = ""
        if ch != "\0":
            run, run_ok = run + ch, ok
    return total + ls * max(len(s) - 1, 0)


class Card:
    def __init__(self, n, stem, title, desc, headline, setup, takeaway):
        self.n, self.stem, self.title, self.desc = n, stem, title, desc
        self.headline, self.setup, self.takeaway = headline, setup, takeaway
        self.v, self.boxes = [], []

    # text: every run is measured and registered for the overlap check
    def t(self, x, y, s, size, fam="sans", weight=400, fill=INK, anchor="start", ls=0.0, upper=False):
        s = s.upper() if upper else s
        w = width(s, fam, weight, size, ls)
        x0 = {"start": x, "middle": x - w / 2, "end": x - w}[anchor]
        self.boxes.append((x0, y - 0.74 * size, x0 + w, y + 0.24 * size, s))
        a = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'fill="{fill}"', f'font-family="{CSS[fam]}"', f'font-size="{size}"']
        if weight != 400:
            a.append(f'font-weight="{weight}"')
        if anchor != "start":
            a.append(f'text-anchor="{anchor}"')
        if ls:
            a.append(f'letter-spacing="{ls}"')
        self.v.append(f'<text {" ".join(a)}>{html.escape(s)}</text>')
        return w

    def line(self, x1, y1, x2, y2, stroke=MUTED, w=1.0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.v.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{w}"{d}/>')

    def rect(self, x, y, w, h, fill="none", stroke=None, sw=1.0, rx=0):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.v.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{s}/>')

    def poly(self, pts, stroke, w=2.0, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        self.v.append(f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"{d}/>')

    def dot(self, x, y, r, fill, stroke=None, sw=1.0):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        self.v.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{s}/>')

    def path(self, d, stroke, w=1.2, dash=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.v.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{w}"{da}/>')

    # ------------------------------------------------------------------------------------
    def svg(self):
        shell = re.search(r"\*\*Locked feed shell\*\*.*?```html\n(.*?)```", SKILL, re.S).group(1)
        hl = self.headline
        if len(hl) == 1:
            ys, sy = [258], 316
        else:
            ys, sy = [222, 292], 342
        assert len(hl) <= 2 and (len(hl) == 1 or len(self.setup) == 1), self.stem
        for s in hl:
            assert width(s, "serif", 400, 64) <= 936, (self.stem, s, width(s, "serif", 400, 64))
        for s in self.setup:
            assert width(s, "sans", 400, 22) <= 936, (self.stem, s, width(s, "sans", 400, 22))
        for s in self.takeaway:
            assert width(s, "sans", 600, 24) <= 936, (self.stem, s, width(s, "sans", 600, 24))
        head = "".join(f'<tspan x="72" y="{y}">{html.escape(s)}</tspan>' for y, s in zip(ys, hl))
        setup = "".join(f'<tspan x="72" y="{sy + 30 * i}">{html.escape(s)}</tspan>' for i, s in enumerate(self.setup))
        tys = [1228] if len(self.takeaway) == 1 else [1214, 1248]
        take = "".join(f'<tspan x="72" y="{y}">{html.escape(s)}</tspan>' for y, s in zip(tys, self.takeaway))
        pairs = [
            ("<title>feed-NN-beat</title>", f"<title>{self.stem}</title>"),
            ('<title id="title">Card title</title><desc id="description">One-sentence description</desc>',
             f'<title id="title">{html.escape(self.title)}</title><desc id="description">{html.escape(self.desc)}</desc>'),
            (">01 / 06</text>", f">{self.n:02d} / {TOTAL:02d}</text>"),
            ('font-size="64">Article-specific headline</text>', f'font-size="64">{head}</text>'),
            ('font-size="22">One precise setup sentence from the article.</text>', f'font-size="22">{setup}</text>'),
            ("<!-- the article-specific technical artefact goes inside x 72–1008, y 390–1080 -->",
             "\n  ".join(self.v)),
            ('font-weight="600">One evidence-backed takeaway.</text>', f'font-weight="600">{take}</text>'),
        ]
        for a, b in pairs:
            assert shell.count(a) == 1, (self.stem, a)
            shell = shell.replace(a, b)
        return shell

    def check(self):
        for (x0, y0, x1, y1, s) in self.boxes:
            assert 80 <= x0 and x1 <= 1000 and 398 <= y0 and y1 <= 1072, (self.stem, "outside panel", s, x0, y0, x1, y1)
        for i, a in enumerate(self.boxes):
            for b in self.boxes[i + 1:]:
                if a[0] < b[2] - 1 and b[0] < a[2] - 1 and a[1] < b[3] - 1 and b[1] < a[3] - 1:
                    raise AssertionError((self.stem, "text collision", a[4], b[4]))

    def write(self):
        self.check()
        OUT.mkdir(exist_ok=True)
        (OUT / f"{self.stem}.html").write_text(self.svg())
        print("wrote", self.stem, f"({len(self.boxes)} text runs checked)")


class Lin:
    def __init__(self, d0, d1, r0, r1):
        self.d0, self.d1, self.r0, self.r1 = d0, d1, r0, r1

    def __call__(self, v):
        return self.r0 + (v - self.d0) / (self.d1 - self.d0) * (self.r1 - self.r0)


P = RES["procedures"]
D = RES["dependence"]
M = P["m"]
PI0 = P["pi0"]["qvalue 2.x"]


# ----------------------------------------------------------------------------------------
def card1():
    c = Card(1, "feed-01-cover", "Same genes, same 5%: 2, 94 or 162 discoveries",
             "Five corrections at the same 5% level on 3,170 breast-cancer genes find 2, 94, 162 or 0 genes.",
             ["Same genes, same 5%:", "2, 94 or 162 discoveries"],
             [f"Hedenfalk's {M:,} breast-cancer genes, one test each, five corrections at 5%."],
             ["Choose the error rate from your claim, then the rule from the dependence."])
    n = P["counts_5pct"]
    cols = [(228, "FWER ≤ 0.05", str(n["Holm"]), "Bonferroni, Holm", ["no false gene, with", "probability ≥ 0.95"]),
            (540, "FDR ≤ 0.05", str(n["BH"]), "Benjamini–Hochberg", ["expected false share", "of the list ≤ 0.05"]),
            (852, "FDR ≤ 0.05", str(n["Storey q"]), "Storey q-value", ["same promise, with", f"π0 = {hp(PI0, 3)} estimated"])]
    assert n["Bonferroni"] == n["Holm"]
    for x in (384, 696):
        c.line(x, 440, x, 870, RULE, 1)
    for x, eyebrow, num, name, lines in cols:
        c.t(x, 474, eyebrow, 17, "mono", 500, MUTED, "middle", 1.5)
        c.t(x, 684, num, 176, "serif", 400, INK, "middle")
        c.t(x, 770, name, 26, "sans", 600, INK, "middle")
        for i, s in enumerate(lines):
            c.t(x, 812 + 30 * i, s, 20, "sans", 400, MUTED, "middle")
    c.rect(540 - 48, 706, 96, 6, ACCENT)
    c.line(112, 930, 968, 930, RULE, 1)
    c.t(540, 984, f"Benjamini–Yekutieli, valid under any dependence: {n['BY']} genes", 22, "sans", 400, INK, "middle")
    c.t(540, 1022, f"it runs BH at 0.05 / H_m, with H_m = {hp(P['harmonic_m'], 2)} for {M:,} tests", 18, "mono", 400, MUTED, "middle")
    c.write()


def card2():
    c = Card(2, "feed-02-two-promises", "Two promises about a count you never see",
             "The outcome table of m tests, with the family-wise error rate and the false discovery rate defined on V.",
             ["Two promises about one unseen count"],
             ["Run m tests and reject R of them. V of the R rejections are false, and V is", "never observed. Each correction bounds a different summary of V."],
             ["A finding that stands alone needs FWER; a list for follow-up needs FDR."])
    cx = {"not rejected": 566, "rejected": 736, "total": 892}
    for k, x in cx.items():
        c.t(x, 466, k, 17, "mono", 500, MUTED, "middle", 1.0, upper=True)
    c.line(112, 490, 968, 490, RULE, 1)
    rows = [("true null", ["U", "V", "m0"], 546), ("false null", ["T", "S", "m1"], 614), ("total", ["m − R", "R", "m"], 690)]
    c.rect(cx["rejected"] - 56, 546 - 38, 112, 54, TINT, ACCENT, 1.6, 6)
    for label, cells, y in rows:
        c.t(112, y, label, 22, "sans", 600 if label == "total" else 400, INK)
        for x, s in zip(cx.values(), cells):
            c.t(x, y, s, 30, "mono", 500, INK, "middle")
    c.line(112, 648, 968, 648, RULE, 1)
    boxes = [(112, "family-wise error rate", "FWER = P(V ≥ 1)", 32, ["the chance of even one", "false discovery"], "Bonferroni · Holm"),
             (560, "false discovery rate", "FDR = E[V / max(R, 1)]", 26, ["the expected false share", "of the list, over studies"], "BH · BY · Storey q-values")]
    for x, eyebrow, formula, fs, lines, rules in boxes:
        c.rect(x, 728, 408, 312, PAPER, SILVER, 1, 8)
        c.t(x + 28, 776, eyebrow, 16, "mono", 500, MUTED, "start", 2.0, upper=True)
        c.t(x + 28, 840, formula, fs, "mono", 500, INK)
        for i, s in enumerate(lines):
            c.t(x + 28, 892 + 30 * i, s, 21, "sans", 400, MUTED)
        c.t(x + 28, 1002, rules, 21, "sans", 600, INK)
    c.write()


def card3():
    ps = P["sorted_p_first_300"][:200]
    k = P["kstar_bh"]
    c = Card(3, "feed-03-step-up-line", "BH keeps every gene up to rank 94",
             "The 200 smallest Hedenfalk p-values with the Bonferroni, BH and Storey lines; rank 94 is the last under BH's line.",
             [f"BH keeps every gene up to rank {k}"],
             [f"Sort the {M:,} p-values. BH finds the largest rank k with p(k) ≤ k × 0.05 / {M:,},",
              "then rejects ranks 1 to k. Storey's line is the same, divided by π0."],
             ["BH's threshold at rank k is k times Bonferroni's: 94 genes instead of 2."])
    X0, X1, Y0, Y1 = 200, 800, 476, 950
    sx = Lin(0, 200, X0, X1)
    sy = lambda p: Y0 + (-2 - math.log10(p)) / 4 * (Y1 - Y0)  # noqa: E731  (1e-2 at top, 1e-6 at bottom)
    for e in range(-6, -1):
        c.line(X0, sy(10 ** e), X1, sy(10 ** e), RULE, 1)
        c.t(X0 - 12, sy(10 ** e) + 6, f"1e{e}", 18, "mono", 400, MUTED, "end")
    c.t(112, 438, "p-value, log scale", 17, "mono", 400, MUTED)
    c.line(X0, Y1, X1, Y1, INK, 1.2)
    for v in (0, 50, 100, 150, 200):
        c.line(sx(v), Y1, sx(v), Y1 + 6, INK, 1.2)
        c.t(sx(v), Y1 + 30, str(v), 18, "mono", 400, MUTED, "middle")
    c.t((X0 + X1) / 2, Y1 + 66, "rank of the sorted p-value", 17, "mono", 400, MUTED, "middle")
    a = 0.05
    c.poly([(sx(i), sy(i * a / M)) for i in range(1, 201)], INK, 2.4)
    c.poly([(sx(i), sy(i * a / (PI0 * M))) for i in range(1, 201)], MUTED, 2.0, "9,6")
    c.line(sx(1), sy(a / M), X1, sy(a / M), MUTED, 2.0, "2,5")
    for i, p in enumerate(ps, 1):
        c.dot(sx(i), sy(p), 3.6 if i <= k else 3.0, INK if i <= k else SOFT)
    c.dot(sx(k), sy(ps[k - 1]), 11, "none", ACCENT, 2.6)
    # line names at the right end, nudged apart where the lines converge
    yb, ys_ = sy(200 * a / M), sy(200 * a / (PI0 * M))
    n = P["counts_5pct"]
    c.t(X1 + 14, ys_ - 4, f"Storey · {n['Storey q']}", 19, "sans", 600, MUTED)
    c.t(X1 + 14, yb + 22, f"BH · {n['BH']}", 19, "sans", 600, INK)
    c.t(X1 + 14, sy(a / M) + 7, f"Bonferroni · {n['Bonferroni']}", 19, "sans", 600, MUTED)
    # the rank-k callout, in the empty upper-left of the plot
    kx, ky = sx(k), sy(ps[k - 1])
    bx = 540
    c.t(bx, 660, f"rank {k} is the last p-value", 20, "sans", 400, INK)
    c.t(bx, 688, "under BH's line:", 20, "sans", 400, INK)
    c.t(bx, 720, f"{ps[k - 1]:.4e} ≤ {k * a / M:.4e}".replace("e-03", "e-3"), 19, "mono", 600, INK)
    c.path(f"M {bx - 8:.1f},{652:.1f} C {bx - 30:.1f},{652:.1f} {kx + 6:.1f},{ky + 40:.1f} {kx + 4:.1f},{ky + 13:.1f}",
           "rgba(45,49,66,0.45)", 1.4, "4,3")
    c.dot(kx + 4, ky + 13, 2, "rgba(45,49,66,0.45)")
    c.t(222, sy(a / M) + 36, f"Bonferroni and Holm stop at rank {n['Holm']}", 19, "sans", 400, MUTED)
    c.write()


def card4():
    R = D["R"]
    bins = D["fdp_bins"]
    e0, e5 = D["by_rho"]["0.0"]["BH"], D["by_rho"]["0.5"]["BH"]
    c = Card(4, "feed-04-fdp-spread", "Same FDR, very different lists",
             "BH's false discovery proportion across 20,000 simulated studies, independent tests against tests correlated at 0.5.",
             ["Same FDR, very different lists"],
             [f"{R:,} simulated studies each, BH at q = 0.05 on {M:,} one-sided tests, with every",
              "pair of tests independent (top) or correlated at 0.5 (bottom)."],
             ["An FDR is an average over studies; one list can be far dirtier than 5%."])
    X0, X1 = 200, 940
    sx = Lin(0, 0.5, X0, X1)
    bw = sx(0.02) - sx(0)
    panels = [(e0, 452, "Independent tests", [f"FDR = {hp(e0['FDR'], 4)}", f"P(FDP > 10%) = {pct(e0['P_FDP_gt_10'], 2)}"]),
              (e5, 728, "Every pair correlated at 0.5",
               [f"FDR = {hp(e5['FDR'], 4)}", f"P(FDP > 10%) = {pct(e5['P_FDP_gt_10'], 2)}",
                f"no list at all: {pct(e5['P_D_zero'], 1)}", f"non-empty lists >10% false: {pct(e5['P_FDP_gt_10_given_D'], 1)}"])]
    for e, top, title, stats in panels:
        y0p, y1p = top + 188, top + 30
        sy = Lin(0, 0.9, y0p, y1p)
        c.t(112, top, title, 21, "sans", 600, INK)
        for v in (0.3, 0.6, 0.9):
            c.line(X0, sy(v), X1, sy(v), RULE, 1)
        for v in (0, 0.3, 0.6, 0.9):
            c.t(X0 - 12, sy(v) + 6, f"{round(v * 100)}%", 17, "mono", 400, MUTED, "end")
        share = list(e["FDP_hist"])
        share[0] += e["P_D_zero"] * R                      # an empty list has FDP 0 by definition
        for i, s in enumerate(share[:25]):
            if s <= 0:
                continue
            h = max(y0p - sy(s / R), 1.2)
            tail = bins[i] >= 0.10
            c.rect(sx(bins[i]) + 1.5, y0p - h, bw - 3, h, TINT if tail else WHITE, ACCENT if tail else INK, 1.3)
        c.line(sx(0.10), y1p - 4, sx(0.10), y0p, ACCENT, 1.6, "5,4")
        c.line(X0, y0p, X1, y0p, INK, 1.2)
        for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
            c.line(sx(v), y0p, sx(v), y0p + 6, INK, 1.2)
            c.t(sx(v), y0p + 28, f"{v:.1f}", 17, "mono", 400, MUTED, "middle")
        c.rect(548, top + 20, 420, 30 * len(stats) + 8, WHITE)
        for i, s in enumerate(stats):
            c.t(560, top + 44 + 30 * i, s, 19, "mono", 600 if "P(FDP" in s else 400, INK)
    c.t((X0 + X1) / 2, 992, "false discovery proportion of one study's BH list; an empty list counts as 0", 16, "mono", 400, MUTED, "middle")
    c.write()


def card5():
    rhos = D["rhos"]
    get = lambda r, rule: D["by_rho"][str(float(r))][rule]["FDR"]  # noqa: E731
    st = [get(r, "Storey q") for r in rhos]
    c = Card(5, "feed-05-storey-correlation", "Storey's q-values overshoot when tests correlate",
             "FDR of Storey's q-values, BH and BY against the correlation between tests; Storey rises from 0.050 to 0.272.",
             ["Storey's q-values overshoot", "when the tests correlate"],
             [f"Target FDR 0.05. Each point is {D['R']:,} simulated studies of {M:,} one-sided tests."],
             ["Correlated tests? Use plain BH: the q-values reached an FDR of 0.27."])
    X0, X1, Y0, Y1 = 200, 780, 470, 950
    sx, sy = Lin(0, 0.5, X0, X1), Lin(0, 0.30, Y1, Y0)
    for v in (0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
        c.line(X0, sy(v), X1, sy(v), RULE, 1)
    for v in (0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30):
        c.t(X0 - 12, sy(v) + 6, "0" if v == 0 else f"{v:.2f}", 18, "mono", 400, MUTED, "end")
    c.t(112, 438, "false discovery rate", 17, "mono", 400, MUTED)
    c.line(X0, Y1, X1, Y1, INK, 1.2)
    for v in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
        c.line(sx(v), Y1, sx(v), Y1 + 6, INK, 1.2)
        c.t(sx(v), Y1 + 30, f"{v:.1f}", 18, "mono", 400, MUTED, "middle")
    c.t((X0 + X1) / 2, Y1 + 66, "correlation between every pair of tests", 17, "mono", 400, MUTED, "middle")
    c.line(X0, sy(0.05), X1, sy(0.05), INK, 1.4, "7,5")
    by = [get(r, "BY") for r in rhos]
    bh = [get(r, "BH") for r in rhos]
    c.poly([(sx(r), sy(v)) for r, v in zip(rhos, by)], MUTED, 2.0, "2,4")
    c.poly([(sx(r), sy(v)) for r, v in zip(rhos, bh)], INK, 2.4)
    for r, v in zip(rhos, bh):
        c.dot(sx(r), sy(v), 4.5, INK)
    c.poly([(sx(r), sy(v)) for r, v in zip(rhos, st)], ACCENT, 3.0)
    for r, v in zip(rhos, st):
        c.dot(sx(r), sy(v), 6.5, ACCENT)
        if r:
            c.t(sx(r) - 12, sy(v) - 14, hp(v, 3), 19, "mono", 500, INK, "end")
    c.t(X1 + 16, sy(st[-1]) + 30, "Storey q", 19, "sans", 600, INK)
    c.t(X1 + 16, sy(0.05) - 8, "target", 18, "mono", 400, INK)
    c.t(X1 + 16, sy(bh[-1]) + 4, f"BH {hp(bh[-1], 3)}", 18, "mono", 500, INK)
    c.t(X1 + 16, sy(by[-1]) + 4, f"BY {hp(by[-1], 3)}", 18, "mono", 400, MUTED)
    c.t(232, 520, "±2 MCSE is smaller than each dot.", 18, "sans", 400, MUTED)
    c.t(232, 548, f"Independent tests: {hp(st[0], 3)}, on target.", 18, "sans", 400, MUTED)
    c.t(232, 576, f"At 0.5: {hp(st[-1] / 0.05, 1)} × the target.", 18, "sans", 400, MUTED)
    c.write()


def card6():
    F = RES["forking"]
    rt = F["rates"]["dummy"]
    c = Card(6, "feed-06-forking-paths", "One reported test, 96 underneath",
             "Four ordinary analysis choices multiply into 96 tests; with no effect, 61.4% of samples give a significant result.",
             [f"One reported test, {F['tests_per_sample']} underneath"],
             ["Simmons, Nelson & Simonsohn's four ordinary choices, rerun on",
              f"{F['R']:,} samples with no effect anywhere."],
             ["A correction needs m, and forks hide m: pre-specify them or count them."])
    rows = [("outcome", "DV1, DV2 or their mean", "× 3"), ("stopping", "20 per cell, or 10 more", "× 2"),
            ("conditions", "three pairs, or a trend", "× 4"), ("model", "plain, + gender, × gender (2)", "× 4")]
    for i, (eyebrow, detail, mult) in enumerate(rows):
        y = 440 + 112 * i
        c.rect(112, y, 400, 92, PAPER, SILVER, 1, 6)
        c.t(134, y + 32, eyebrow, 15, "mono", 500, MUTED, "start", 2.0, upper=True)
        c.t(134, y + 68, detail, 20, "sans", 400, INK)
        c.t(492, y + 58, mult, 30, "mono", 500, INK, "end")
    c.t(312, 948, f"3 × 2 × 4 × 4 = {F['tests_per_sample']}", 32, "mono", 500, INK, "middle")
    c.t(312, 988, "p-values behind one reported result", 19, "sans", 400, MUTED, "middle")
    bars = [("one t-test", rt["one t test"]), ("outcome", rt["A two DVs"]), ("stopping", rt["B ten more per cell"]),
            ("gender", rt["C gender"]), ("conditions", rt["D three conditions"]), ("all four", rt["A+B+C+D"])]
    c.t(560, 452, "FALSE POSITIVES AT p < .05", 16, "mono", 500, MUTED, "start", 1.0)
    BX0, BX1 = 690, 880
    sx = Lin(0, 0.75, BX0, BX1)
    for i, (name, e) in enumerate(bars):
        y = 496 + 70 * i + (20 if name == "all four" else 0)
        last = name == "all four"
        c.t(BX0 - 12, y + 22, name, 19, "sans", 600 if last else 400, INK, "end")
        c.rect(BX0, y, sx(e["rate"]) - BX0, 30, ACCENT if last else WHITE, None if last else INK, 1.3)
        c.t(sx(e["rate"]) + 10, y + 22, pct(e["rate"], 1), 19, "mono", 500, INK)
    yl = 496 + 70 * 5 + 20
    xp = sx(F["paper"]["A+B+C+D"])
    c.line(xp, yl - 8, xp, yl + 38, INK, 2)
    c.t(xp, yl + 64, f"paper: {pct(F['paper']['A+B+C+D'], 1)}", 16, "mono", 400, MUTED, "middle")
    c.line(BX0, 484, BX0, yl + 40, INK, 1.2)
    c.t(560, 988, f"± {pct(rt['A+B+C+D']['se'], 2)} on all four; R = {F['R']:,}", 16, "mono", 400, MUTED)
    c.write()


def card7():
    c = Card(7, "feed-07-read-the-article", "Check which rule your library runs",
             "Default multiple-testing methods in R, statsmodels and SciPy, with a link to the full article on Canery.",
             ["Check which rule your library runs"],
             ["The libraries agree on the numbers and disagree on the defaults."],
             ["Read it at canery.in/blogs/multiple-comparisons-fwer-fdr"])
    cols = (112, 352, 836)
    for x, h in zip(cols, ("library", "call", "default")):
        c.t(x, 456, h, 15, "mono", 500, MUTED, "start", 2.0, upper=True)
    c.line(112, 476, 968, 476, RULE, 1)
    rows = [("R 4.5", "p.adjust(p, method)", '"holm"', '"fdr" is an alias for "BH"'),
            ("statsmodels 0.15", "multipletests(p, alpha, method)", "'hs'", "Holm–Šidák; returns (reject, adjusted, …)"),
            ("SciPy 1.18", "false_discovery_control(ps, method)", "'bh'", "adjusted p-values only; no FWER methods")]
    for i, (lib, call, default, note) in enumerate(rows):
        y = 530 + 100 * i
        c.t(cols[0], y, lib, 22, "sans", 600, INK)
        c.t(cols[1], y, call, 20, "mono", 400, INK)
        w = width(default, "mono", 500, 20)
        c.rect(cols[2] - 8, y - 24, w + 16, 34, PAPER, SILVER, 1, 2)
        c.t(cols[2], y, default, 20, "mono", 500, INK)
        c.t(cols[1], y + 34, note, 18, "sans", 400, MUTED)
        if i < 2:
            c.line(112, y + 62, 968, y + 62, RULE, 1)
    c.rect(112, 862, 856, 164, TINT, ACCENT, 1.6, 8)
    c.t(148, 932, "Read the full article on Canery", 46, "serif", 400, INK)
    c.t(148, 980, "Five rules by hand, four simulations and a lab you can run.", 20, "sans", 400, MUTED)
    c.write()


if __name__ == "__main__":
    for f in (card1, card2, card3, card4, card5, card6, card7):
        f()
