#!/usr/bin/env python3
"""Figures 01-07 and 09-13 for laya-decision-model-explained (figure 08 is Mermaid: _fig08.py).

Every Laya number drawn here is read from ../lab/trace.json, the captured output of
lab/trace_laya.py (laya 0.3.20, CPU, FP32, checkpoint commit 55cf4c4e), so a figure
cannot disagree with the lab or the prose. Figure 07's curves and figure 09's masks are
exact computations; figure 13 draws formats from the cited papers.
Run:  python3 _figs.py [01 05 ...]
"""
import json
import math
import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SOFT, box, cell, emit, esc, eyebrow, legend,
                    masked, mono, txt)

HERE = pathlib.Path(__file__).resolve().parent
DATA = json.loads((HERE.parent / "lab" / "trace.json").read_text(encoding="utf-8"))
EN = DATA["english"]
Q = {q["id"]: q for q in EN["questions"]}

SER1, SER2, SER3 = "#7c8f6f", "#5e7a9b", "#b8915a"
# Segment colours for the decision-model token strip (V13 variant). Fixed for Parts 1-5.
SEG_FILL = {"cls": INK, "sep": INK, "question": "rgba(94,122,155,0.18)",
            "marker": ACCENT, "option": "rgba(184,145,90,0.20)",
            "state": "rgba(124,143,111,0.20)", "pad": "rgba(45,49,66,0.05)"}
SEG_STROKE = {"cls": INK, "sep": INK, "question": SER2, "marker": ACCENT,
              "option": SER3, "state": SER1, "pad": "rgba(45,49,66,0.25)"}
SEG_TEXT = {"cls": "#ffffff", "sep": "#ffffff", "marker": "#ffffff"}
OPT_NAMES = {"route": ["billing", "technical", "account", "sales"],
             "urgency": ["level 0", "level 1", "level 2", "level 3", "level 4"],
             "refund": ["false", "true"]}


# ------------------------------------------------------------------ helpers
def fmt(v, nd=3):
    return f"{v:.{nd}f}".replace("-", "−")


def comma(n):
    return f"{n:,}"


def polyline(pts, stroke, sw=1.4, dash=None, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity else ""
    return (f'<polyline points="{" ".join(f"{px:.1f},{py:.1f}" for px, py in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{d}{o}/>')


def area_between(top, bot, fill, opacity=0.16):
    d = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in top)
    d += " L " + " L ".join(f"{x:.1f} {y:.1f}" for x, y in reversed(bot)) + " Z"
    return f'<path d="{d}" fill="{fill}" fill-opacity="{opacity}" stroke="none"/>'


def dot(x, y, r=3.4, fill=INK, stroke=None, hollow=False):
    if hollow:
        return (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{PAPER}" '
                f'stroke="{fill}" stroke-width="1.4"/>')
    st = f' stroke="{stroke}" stroke-width="1.2"' if stroke else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"{st}/>'


def rect(x, y, w, h, fill, stroke="none", sw=0.8, opacity=None, rx=0, dash=None):
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}"{o} stroke="{stroke}" stroke-width="{sw}"{d}/>')


def hatch_defs():
    return ('<defs><pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse" '
            'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="5" '
            'stroke="rgba(45,49,66,0.28)" stroke-width="1.2"/></pattern></defs>')


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr, ylog=False):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.xr, self.yr, self.ylog = xr, yr, ylog

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        if self.ylog:
            a, b = math.log10(self.yr[0]), math.log10(self.yr[1])
            return self.y0 + self.h - (math.log10(y) - a) / (b - a) * self.h
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def frame(self, xt, yt, xlab=None, ylab=None, xfmt=str, yfmt=str, grid=True):
        s = (f'<line x1="{self.x0}" y1="{self.y0 + self.h}" x2="{self.x0 + self.w}" '
             f'y2="{self.y0 + self.h}" stroke="{RULE_SOLID}" stroke-width="1"/>')
        s += (f'<line x1="{self.x0}" y1="{self.y0}" x2="{self.x0}" y2="{self.y0 + self.h}" '
              f'stroke="{RULE_SOLID}" stroke-width="1"/>')
        for v in yt:
            yy = self.Y(v)
            if grid:
                s += (f'<line x1="{self.x0}" y1="{yy:.1f}" x2="{self.x0 + self.w}" y2="{yy:.1f}" '
                      f'stroke="{RULE}" stroke-width="0.8"/>')
            s += mono(self.x0 - 7, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            s += mono(self.X(v), self.y0 + self.h + 14, xfmt(v), size=8, fill=SOFT)
        if xlab:
            s += eyebrow(self.x0 + self.w, self.y0 + self.h + 30, xlab, anchor="end")
        if ylab:
            s += eyebrow(self.x0, self.y0 - 10, ylab, anchor="start")
        return s


def key(y, vw, items):
    """A legend whose swatches are drawn exactly like the marks they name.

    items: (label, colour, kind, opacity), kind one of bar / line / tri / dot.
    """
    s = (f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" '
         f'stroke="{RULE}" stroke-width="0.8"/>')
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    x = 108
    for label, colour, kind, op in items:
        if kind == "bar":
            s += rect(x, y, 10, 10, colour, opacity=op, rx=1)
        elif kind == "line":
            s += (f'<line x1="{x - 2}" y1="{y + 5}" x2="{x + 12}" y2="{y + 5}" stroke="{colour}" '
                  f'stroke-width="1.6"/>')
        elif kind == "tri":
            s += f'<path d="M {x + 5} {y} l -5 9 l 10 0 Z" fill="{colour}"/>'
        else:
            s += f'<circle cx="{x + 5}" cy="{y + 5}" r="4" fill="{colour}"/>'
        s += mono(x + 18, y + 9, label, size=8, fill=MUTED, anchor="start", track="0.06em")
        x += 18 + 6.0 * len(label) + 28
    return s


def show_tok(t):
    return t.replace("Ċ", "↵")


# ------------------------------------------------------------------ FIG 01 token strip
def fig01():
    q = Q["route"]
    toks, segs = q["tokens"], q["segments"]
    cols, cw, ch, gx, gy = 12, 78, 30, 2, 4
    x0, y0 = 32, 104
    rows = math.ceil(len(toks) / cols)
    vw, vh = 1016, y0 + rows * (ch + gy) + 60
    s = eyebrow(32, 40, "the route question's sequence, token by token: 141 positions, one row of the batch")
    items = [("[CLS] / [SEP]", INK, "box"), ("question · 11", SER2, "box"),
             ("[MASK] marker · 4", ACCENT, "box"), ("option text · 34", SER3, "box"),
             ("ticket (state) · 88", SER1, "box")]
    x = 32
    for label, col, _ in items:
        s += rect(x, 62, 11, 11, SEG_FILL[{INK: "cls", SER2: "question", ACCENT: "marker", SER3: "option", SER1: "state"}[col]],
                  stroke=col, rx=2)
        s += mono(x + 18, 71, label, size=8, fill=MUTED, anchor="start")
        x += 18 + 6.3 * len(label) + 26
    for i, (t, g) in enumerate(zip(toks, segs)):
        r, c = divmod(i, cols)
        cx, cy = x0 + c * (cw + gx), y0 + r * (ch + gy)
        s += rect(cx, cy, cw, ch, SEG_FILL[g], stroke=SEG_STROKE[g], rx=3)
        s += mono(cx + 4, cy + 9, str(i), size=6.5, fill="#ffffff" if g in SEG_TEXT else SOFT, anchor="start")
        s += txt(cx + cw / 2, cy + 21, show_tok(t), size=9 if len(t) < 12 else 8,
                 fill=SEG_TEXT.get(g, INK), family=MONO, weight="600" if g == "marker" else "400")
    s += mono(32, vh - 30, "Tokens are ModernBERT's byte-pair pieces as the tokenizer returns them; Ġ marks a leading space. "
              "Positions of the four [MASK] markers: 13, 23, 34, 43.", size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "Our run: laya 0.3.20 build_sequence on the ticket, checkpoint 55cf4c4e.",
              size=8, fill=SOFT, anchor="start")
    return emit("01", "route-token-strip", "One question, one sequence",
                "The route question's 141 tokens: question, one [MASK] before each option, then the whole ticket.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 02 the batch to scale
def row_segments(q):
    segs = q["segments"]
    out, start = [], 0
    for i in range(1, len(segs) + 1):
        if i == len(segs) or segs[i] != segs[start] or segs[start] == "marker":
            out.append((segs[start], start, i - start))
            start = i
    return out


def fig02():
    vw, vh = 1016, 400
    unit = 5.2
    x0 = 130
    s = hatch_defs()
    s += eyebrow(32, 40, "the batch predict() runs: one row per question, padded to the longest, the ticket copied into each")
    L = EN["shapes"]["input_ids"][1]
    ys = {"route": 84, "urgency": 144, "refund": 204}
    for qid, y in ys.items():
        q = Q[qid]
        s += txt(32, y + 15, qid, size=12, weight="600", anchor="start")
        s += mono(32, y + 29, f"{q['type']} · k = {q['n_options']}", size=8, fill=SOFT, anchor="start")
        for g, st, n in row_segments(q):
            s += rect(x0 + st * unit, y, n * unit, 34, SEG_FILL[g], stroke=SEG_STROKE[g], sw=0.6)
            if g == "state":
                s += txt(x0 + (st + n / 2) * unit, y + 21, f"ticket · {n} tokens", size=10,
                         fill=INK, family=MONO, weight="500")
        pad = L - q["seq_len"]
        if pad:
            s += rect(x0 + q["seq_len"] * unit, y, pad * unit, 34, "url(#hatch)", stroke=SEG_STROKE["pad"], sw=0.6)
        s += mono(x0 + L * unit + 12, y + 15, f"{q['seq_len']} real", size=9, fill=INK, anchor="start", weight="500")
        s += mono(x0 + L * unit + 12, y + 28, f"+ {pad} pad" if pad else "longest row", size=8, fill=SOFT, anchor="start")
    # scale
    ya = 252
    s += f'<line x1="{x0}" y1="{ya}" x2="{x0 + L * unit}" y2="{ya}" stroke="{RULE_SOLID}"/>'
    for v in (0, 25, 50, 75, 100, 125, L):
        s += f'<line x1="{x0 + v * unit}" y1="{ya}" x2="{x0 + v * unit}" y2="{ya + 5}" stroke="{RULE_SOLID}"/>'
        s += mono(x0 + v * unit, ya + 16, str(v), size=8, fill=SOFT)
    s += eyebrow(x0 + L * unit, ya + 32, "position in the row (tokens) · batch shape [3, 141]", anchor="end")
    # the 399 input tokens
    yb, u2 = 318, 1.7
    tot = EN["usage"]["input_tokens"]
    st_tok = EN["state_tokens"]
    other = tot - 3 * st_tok
    s += txt(32, yb + 15, "input_tokens", size=11, weight="600", anchor="start", family=MONO)
    s += mono(32, yb + 29, f"= {tot}", size=9, fill=SOFT, anchor="start")
    s += rect(x0, yb, other * u2, 26, "rgba(45,49,66,0.10)", stroke=MUTED, sw=0.6)
    s += mono(x0 + other * u2 / 2, yb + 17, f"{other} question, option, special", size=8, fill=INK)
    for k in range(3):
        xs = x0 + (other + k * st_tok) * u2
        s += rect(xs, yb, st_tok * u2, 26, SEG_FILL["state"], stroke=SER1, sw=0.8)
        s += mono(xs + st_tok * u2 / 2, yb + 17, f"ticket copy {k + 1} · {st_tok}", size=8, fill=INK)
    s += mono(x0 + tot * u2 + 12, yb + 12, f"{3 * st_tok} of {tot} are the ticket", size=9, fill=INK,
              anchor="start", weight="500")
    s += mono(x0 + tot * u2 + 12, yb + 25, "output_tokens = 0", size=9, fill=ACCENT, anchor="start", weight="600")
    s += mono(32, vh - 14, "Our run: laya 0.3.20, CPU, FP32; usage as reported by predict(). Rows to scale, 1 token = 5.2 px; the bar below, 1 token = 1.7 px.",
              size=8, fill=SOFT, anchor="start")
    return emit("02", "one-batch", "One forward pass is one batch",
                "Three rows, one per question, each carrying its own copy of the 88-token ticket.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 03 decision readout
def bars_panel(x0, y0, w, h, qid, probs, raw, names, title, sub, chosen, score=None):
    ax = Axes(x0, y0, w, h, (0, len(probs)), (0, 1))
    s = txt(x0, y0 - 34, title, size=12, weight="600", anchor="start")
    s += mono(x0, y0 - 20, sub, size=8, fill=SOFT, anchor="start")
    s += ax.frame([], [0, 0.25, 0.5, 0.75, 1], yfmt=lambda v: f"{v:.2f}")
    bw = w / len(probs) * 0.56
    for i, (p, r, n) in enumerate(zip(probs, raw, names)):
        cx = ax.X(i + 0.5)
        col = ACCENT if i == chosen else MUTED
        s += rect(cx - bw / 2, ax.Y(p), bw, ax.Y(0) - ax.Y(p), col, opacity=0.85 if i == chosen else 0.55)
        s += (f'<line x1="{cx - bw / 2 - 5:.1f}" y1="{ax.Y(r):.1f}" x2="{cx + bw / 2 + 5:.1f}" '
              f'y2="{ax.Y(r):.1f}" stroke="{INK}" stroke-width="1.6"/>')
        if p >= 0.2:   # tall bar: the value goes inside, so it cannot be read as the tick's
            s += mono(cx, ax.Y(p) + 15, fmt(p), size=9, fill="#ffffff", weight="600")
        else:
            s += mono(cx, min(ax.Y(p), ax.Y(r)) - 6, fmt(p), size=9, fill=INK)
        s += mono(cx, y0 + h + 14, n, size=8, fill=INK)
    if score is not None:
        sx = ax.X(score + 0.5)
        s += (f'<path d="M {sx:.1f} {y0 + h + 22} l -5 9 l 10 0 Z" fill="{LINK}"/>')
        s += mono(sx, y0 + h + 44, f"score = {score:.3f}", size=8, fill=LINK, weight="600")
    return s


def fig03():
    vw, vh = 1016, 440
    s = eyebrow(32, 40, "what laya returns for the ticket: one distribution per question")
    panels = [("route", 60, 280), ("urgency", 400, 330), ("refund", 790, 190)]
    y0, h = 110, 210
    for qid, x0, w in panels:
        q = Q[qid]
        a = EN["api_response"]["answers"][qid]
        chosen = max(range(q["n_options"]), key=lambda i: q["p_returned"][i])
        conf = a.get("confidence")
        sub = f"{q['type']} · T = {q['temperature']:.3f} · confidence {conf:.3f}"
        title = {"route": "route → billing", "urgency": "urgency → score 3.331", "refund": "refund → noul 0.859"}[qid]
        s += bars_panel(x0, y0, w, h, qid, q["p_returned"], q["p_raw"], OPT_NAMES[qid], title, sub, chosen,
                        score=a.get("score") if qid == "urgency" else None)
    s += key(vh - 58, vw, [("returned probability", MUTED, "bar", 0.55), ("chosen option", ACCENT, "bar", 0.85),
                           ("same logits at T = 1", INK, "line", 1), ("expected level (score)", LINK, "tri", 1)])
    s += mono(32, vh - 16, "Our run: laya 0.3.20, CPU, FP32, checkpoint 55cf4c4e. act_probability was 1.0000 for all three questions.",
              size=8, fill=SOFT, anchor="start")
    return emit("03", "decision-readout", "The decision readout",
                "Returned probabilities per question, with the untempered softmax of the same logits for comparison.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04 three ways
def fig04():
    vw, vh = 1016, 528
    s = eyebrow(32, 40, "the ticket's three answers, three ways: who declares the options, what runs, what comes out")
    cols = [(32, "fine-tuned classifier", "store"), (360, "LLM in JSON mode", "store"), (688, "decision model (Laya)", "focal")]
    cw = 296
    for x, title, kind in cols:
        s += box(x, 60, cw, 440, fill=ACCENT_TINT if kind == "focal" else "#ffffff",
                 stroke=ACCENT if kind == "focal" else "rgba(45,49,66,0.35)")
        s += txt(x + 14, 84, title, size=13, weight="600", anchor="start", fill=ACCENT if kind == "focal" else INK)
    def row(x, y, label, value, strong=False, col=INK):
        r = eyebrow(x + 14, y, label)
        r += txt(x + 14, y + 16, value, size=11, anchor="start", fill=col, weight="600" if strong else "400")
        return r
    # options declared by
    s += row(32, 110, "options declared by", "training data, fixed in the weights")
    s += row(360, 110, "options declared by", "the request (prompt + schema)")
    s += row(688, 110, "options declared by", "the request (typed questions)")
    # the work, drawn to count
    s += eyebrow(46, 162, "what runs")
    s += rect(46, 172, 268, 30, "rgba(45,49,66,0.08)", stroke=MUTED, rx=3)
    s += mono(180, 191, "1 encoder pass over the ticket", size=9, fill=INK)
    for i, (n, k) in enumerate((("route", 4), ("urgency", 5), ("refund", 2))):
        yy = 214 + i * 26
        s += rect(46, yy, 268, 20, "#ffffff", stroke="rgba(45,49,66,0.35)", rx=3)
        s += mono(54, yy + 14, f"{n} head · 1,024 × {k} + {k}", size=8, fill=INK, anchor="start")
        s += mono(306, yy + 14, f"{1024 * k + k:,} params", size=8, fill=SOFT, anchor="end")
    s += eyebrow(374, 162, "what runs")
    s += rect(374, 172, 268, 30, "rgba(45,49,66,0.08)", stroke=MUTED, rx=3)
    s += mono(508, 191, "read the prompt and the ticket", size=9, fill=INK)
    n_dec = EN["json_answer_tokens_modernbert_bpe"]
    for i in range(n_dec):
        xx = 374 + i * 14.1
        s += rect(xx, 216, 11, 22, "#ffffff", stroke=MUTED, rx=2)
    s += mono(374, 256, f"{n_dec} decode steps, one after another", size=8, fill=INK, anchor="start")
    s += mono(374, 270, "each step: one decoder pass for one token", size=8, fill=SOFT, anchor="start")
    s += eyebrow(702, 162, "what runs")
    for i, (qid, L) in enumerate((("route", 141), ("urgency", 136), ("refund", 122))):
        yy = 176 + i * 22
        s += rect(702, yy, 268 * L / 141, 18, SEG_FILL["state"], stroke=SER1, rx=2)
        s += mono(710, yy + 13, f"{qid} row · {L} tokens", size=8, fill=INK, anchor="start")
    s += mono(702, 256, "1 batch [3, 141] through encoder + head", size=8, fill=INK, anchor="start")
    s += mono(702, 270, "one pass; every option scored at its [MASK]", size=8, fill=SOFT, anchor="start")
    # output
    s += row(32, 300, "output", "3 distributions over trained labels")
    s += eyebrow(374, 300, "output")
    s += mono(374, 318, '{"route": "billing", "urgency": 3,', size=9, fill=INK, anchor="start")
    s += mono(374, 331, ' "refund": true}', size=9, fill=INK, anchor="start")
    s += row(688, 300, "output", "3 distributions over declared options", strong=True, col=ACCENT)
    s += mono(702, 334, "output_tokens = 0", size=9, fill=ACCENT, anchor="start", weight="600")
    # probability meaning
    s += row(32, 360, "the probability means", "P(label) for each trained label")
    s += row(360, 360, "the probability means", "P(next token | text so far)")
    s += row(688, 360, "the probability means", "P(option), within its question")
    # new option
    s += row(32, 410, "add a fifth team", "new rows, new labels, retrain")
    s += row(360, 410, "add a fifth team", "edit the prompt")
    s += row(688, 410, "add a fifth team", "edit the request")
    # verdict
    s += row(32, 460, "what you give up", "the interface: labels are frozen", col=MUTED)
    s += row(360, 460, "what you give up", "one step per token; text probabilities", col=MUTED)
    s += row(688, 460, "what it guarantees", "an answer from your options, not a right one", col=MUTED)
    s += mono(32, vh - 14, f"Laya: our run. The {n_dec}-token count uses Laya's tokenizer (ModernBERT BPE); an LLM's own tokenizer gives a different count. Classifier heads computed as 1,024 × k + k.",
              size=8, fill=SOFT, anchor="start")
    return emit("04", "three-ways", "Three ways to get the same three answers",
                "A classifier, an LLM in JSON mode and a decision model, compared on the ticket.",
                "what a decision model is", vw, vh, s)


# ------------------------------------------------------------------ FIG 05 the option budget
def fig05():
    vw, vh = 1016, 470
    rows = DATA["budget"]["rows"]
    en = [r for r in rows if r["max_len"] == 512]
    ml = [r for r in rows if r["max_len"] == 1024]
    s = eyebrow(32, 40, "laya's own build_sequence, route question, 1 to 140 options of about the same length as ours")
    # left: tokens per option
    a = Axes(80, 100, 380, 250, (0, 140), (0, 16))
    s += txt(80, 72, "tokens each option keeps, [MASK] included", size=12, weight="600", anchor="start")
    s += a.frame([0, 20, 40, 60, 80, 100, 120, 140], [0, 4, 8, 12, 16], xlab="number of options k")
    for data, col in ((en, INK), (ml, LINK)):
        pts = [(a.X(r["k"]), a.Y(r["tokens_per_option"])) for r in data if r["tokens_per_option"] is not None]
        s += polyline(pts, col, sw=1.6)
    # labels sit below the plateau, where no curve runs, so nothing is hidden
    for k, col, lab, dy in ((36, INK, "512 / 192: 4 tokens each from k = 36", 18), (49, LINK, "1,024 / 256: from k = 49", 32)):
        s += dot(a.X(k), a.Y(4), fill=col)
        s += mono(a.X(k), a.Y(4) + dy, lab, size=8, fill=col, anchor="start")
    s += masked(a.X(4) + 4, a.Y(14) - 8, "k = 4: 14 each", size=8, fill=MUTED, anchor="start")
    # right: room left for the state
    b = Axes(560, 100, 400, 250, (0, 140), (0, 1000))
    s += txt(560, 72, "room left for the state (tokens)", size=12, weight="600", anchor="start")
    s += b.frame([0, 20, 40, 60, 80, 100, 120, 140], [0, 250, 500, 750, 1000], xlab="number of options k")
    s += rect(b.X(125.5), b.y0, b.X(140) - b.X(125.5), b.h, "rgba(235,108,54,0.10)")
    s += masked(b.X(132.5), b.y0 + 14, "512: options cut", size=7, fill=ACCENT)
    for data, col in ((en, INK), (ml, LINK)):
        pts = [(b.X(r["k"]), b.Y(r["state_room"])) for r in data]
        s += polyline(pts, col, sw=1.6)
    look = {(r["max_len"], r["k"]): r["state_room"] for r in rows}
    marks = [(512, 4, INK, "441", 8, -8), (512, 77, INK, "192 at k = 77", 8, -8),
             (1024, 4, LINK, "953", 8, -8), (1024, 77, LINK, "704 at k = 77", 8, -8), (1024, 125, LINK, "512", 6, -10)]
    for ml_, k, col, lab, dx, dy in marks:
        v = look[(ml_, k)]
        s += dot(b.X(k), b.Y(v), fill=col)
        s += masked(b.X(k) + dx, b.Y(v) + dy, lab, size=8, fill=col, anchor="end" if dx < 0 else "start")
    # the zero point gets a leader from open space between the two curves
    s += dot(b.X(125), b.Y(0), fill=ACCENT)
    s += (f'<line x1="{b.X(116):.1f}" y1="{b.Y(340):.1f}" x2="{b.X(124.4):.1f}" y2="{b.Y(8):.1f}" '
          f'stroke="{ACCENT}" stroke-width="1"/>')
    s += mono(b.X(116), b.Y(340) - 6, "state room 0 at k = 125", size=8, fill=ACCENT, anchor="end", weight="600")
    s += legend(vh - 70, vw, [("English: 512 per row, 192 for question + options", INK, "line"),
                              ("typed-decisions / multilingual: 1,024, 256", LINK, "line")])
    s += mono(32, vh - 30, "Computed by laya 0.3.20 build_sequence with synthetic options of 14 tokens each ([MASK] + 13). At k = 126 the [SEP] closing the options "
              "is cut; at 127 a marker is cut and laya raises.", size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "The question text is cut to 8 tokens from k = 46 (512) and k = 62 (1,024).",
              size=8, fill=SOFT, anchor="start")
    return emit("05", "option-budget", "How options eat the sequence",
                "As options multiply, each keeps fewer tokens, then they take the state's room.",
                "layout", vw, vh, s)


# ------------------------------------------------------------------ FIG 06 scoring grid
def fig06():
    vw = 1016
    blocks = ["route", "urgency", "refund"]
    bh = 158
    vh = 80 + bh * 3 + 30
    s = hatch_defs()
    s += eyebrow(32, 40, "option-marker scoring on the ticket: logits → mask → ÷ T → softmax, one row per question")
    lx, cx0, cw, rh = 32, 262, 138, 26
    for bi, qid in enumerate(blocks):
        q = Q[qid]
        y0 = 70 + bi * bh
        k = q["n_options"]
        chosen = max(range(k), key=lambda i: q["p_returned"][i])
        s += txt(lx, y0 + 16, f"{qid}", size=12, weight="600", anchor="start")
        s += mono(lx, y0 + 30, f"{q['type']} · k = {k} · T = {q['temperature']:.4f}", size=8, fill=SOFT, anchor="start")
        s += mono(lx, y0 + 43, f"markers at {', '.join(map(str, q['markers']))}", size=8, fill=SOFT, anchor="start")
        for j in range(5):
            x = cx0 + j * (cw + 6)
            s += mono(x + cw / 2, y0 + 12, OPT_NAMES[qid][j] if j < k else "unused slot", size=8,
                      fill=INK if j < k else SOFT)
        labels = ["logit z", "masked", "z ÷ T", "probability"]
        for r, lab in enumerate(labels):
            yy = y0 + 20 + r * (rh + 4)
            s += mono(cx0 - 12, yy + 17, lab, size=8, fill=MUTED, anchor="end")
            zt = [v / q["temperature"] for v in q["logits"]]
            for j in range(5):
                x = cx0 + j * (cw + 6)
                used = j < k
                if not used:
                    val = {0: "—", 1: "−10,000", 2: "−10,000 ÷ T", 3: "0"}[r]
                    s += rect(x, yy, cw, rh, "url(#hatch)", stroke="rgba(45,49,66,0.25)")
                    s += mono(x + cw / 2, yy + 17, val, size=9, fill=SOFT)
                    continue
                val = {0: fmt(q["logits"][j]), 1: fmt(q["logits"][j]), 2: fmt(zt[j]),
                       3: fmt(q["p_returned"][j])}[r]
                hi = (j == chosen and r == 3)
                s += cell(x, yy, cw, rh, val, fill=ACCENT_TINT if hi else "#ffffff",
                          stroke=ACCENT if hi else "rgba(45,49,66,0.30)", tcolor=ACCENT if hi else INK, size=10,
                          weight="600" if hi else "500")
        s += f'<line x1="{lx}" y1="{y0 + bh - 8}" x2="{vw - 32}" y2="{y0 + bh - 8}" stroke="{RULE}"/>'
    s += mono(32, vh - 16, "Our run: logits captured from the scorer during predict(); probabilities recomputed from them match the returned JSON to 4 decimals.",
              size=8, fill=SOFT, anchor="start")
    return emit("06", "scoring-grid", "Option-marker scoring, number by number",
                "Each question's slots are scored, the unused ones masked, and a softmax run within the question.",
                "option-marker scoring", vw, vh, s)


# ------------------------------------------------------------------ FIG 07 two confidences
def ent(p):
    return -sum(v * math.log(v) for v in p if v > 1e-15)


def conf_low(pmax, k):
    rem = (1 - pmax) / (k - 1)
    return 1 - ent([pmax] + [rem] * (k - 1)) / math.log(k)


def conf_high(pmax, k):
    m = int(math.floor(1 / pmax + 1e-12))
    p = [pmax] * m
    r = 1 - m * pmax
    if r > 1e-12:
        p.append(r)
    return 1 - ent(p) / math.log(k)


def fig07():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "laya returns two numbers called confidence; the entropy-based one depends on how the rest is spread")
    a = Axes(110, 80, 560, 300, (0.2, 1.0), (0, 1))
    s += a.frame([0.2, 0.4, 0.6, 0.8, 1.0], [0, 0.25, 0.5, 0.75, 1], xlab="top probability max(p)",
                 ylab="confidence field", xfmt=lambda v: f"{v:.1f}", yfmt=lambda v: f"{v:.2f}")
    for k, col in ((5, SER3), (4, SER2)):
        xs = [1 / k + (1 - 1 / k) * i / 300 for i in range(1, 301)]
        lo = [(a.X(x), a.Y(conf_low(x, k))) for x in xs]
        hi = [(a.X(x), a.Y(conf_high(x, k))) for x in xs]
        s += area_between(hi, lo, col, opacity=0.14)
        s += polyline(lo, col, sw=1.1)
        s += polyline(hi, col, sw=1.1, dash="4,3")
    s += polyline([(a.X(0.2), a.Y(0.2)), (a.X(1), a.Y(1))], INK, sw=1.4)
    # Labels live in empty regions (above the identity line, below both bands) with leaders,
    # so no plate hides a curve.
    place = {"route": (0.875, 0.47), "urgency": (0.62, 0.12)}
    for qid in ("route", "urgency"):
        ans = EN["api_response"]["answers"][qid]
        px, c, ac = ans["answer_confidence"], ans["confidence"], ans["answer_confidence"]
        s += (f'<line x1="{a.X(px):.1f}" y1="{a.Y(ac):.1f}" x2="{a.X(px):.1f}" y2="{a.Y(c):.1f}" '
              f'stroke="{MUTED}" stroke-width="1" stroke-dasharray="2,2"/>')
        s += dot(a.X(px), a.Y(ac), fill=INK, hollow=True)
        s += dot(a.X(px), a.Y(c), r=4, fill=ACCENT)
        lx, ly = place[qid]
        s += (f'<line x1="{a.X(px):.1f}" y1="{a.Y(c) + 4:.1f}" x2="{a.X(lx) - 2:.1f}" y2="{a.Y(ly) - 4:.1f}" '
              f'stroke="{ACCENT}" stroke-width="0.8"/>')
        s += mono(a.X(lx), a.Y(ly), f"{qid}: confidence {c:.3f}", size=8, fill=ACCENT, anchor="start", weight="600")
        s += mono(a.X(px) - 6, a.Y(ac) - 16, f"{qid}: answer_confidence {ac:.3f}", size=8, fill=INK, anchor="end")
    r = EN["api_response"]["answers"]["refund"]
    rx, ry = r["answer_confidence"], r["confidence"]
    s += dot(a.X(rx), a.Y(ry), r=4, fill=ACCENT)
    s += (f'<line x1="{a.X(rx):.1f}" y1="{a.Y(ry) - 5:.1f}" x2="{a.X(rx):.1f}" y2="{a.Y(1.0) - 8:.1f}" '
          f'stroke="{ACCENT}" stroke-width="0.8"/>')
    s += mono(a.X(1.0), a.Y(1.0) - 12, f"refund (noul): confidence {ry:.3f} = max(p)", size=8, fill=ACCENT,
              anchor="end", weight="600")
    # side legend
    x = 720
    s += txt(x, 100, "how to read it", size=12, weight="600", anchor="start")
    lines = [("identity line", "answer_confidence = max(p), all types;", "also noul's confidence"),
             ("blue band (k = 4)", "1 − H(p) / ln 4 for choice questions", "with four options"),
             ("ochre band (k = 5)", "the same for a five-level score", ""),
             ("solid edge", "leftover probability spread evenly", ""),
             ("dashed edge", "leftover given to as few rivals as possible", "")]
    yy = 126
    for head, l1, l2 in lines:
        s += mono(x, yy, head, size=9, fill=INK, anchor="start", weight="600")
        s += mono(x, yy + 14, l1, size=8, fill=MUTED, anchor="start")
        if l2:
            s += mono(x, yy + 27, l2, size=8, fill=MUTED, anchor="start")
        yy += 44 if l2 else 34
    s += mono(32, vh - 30, "Bands: exact computation of 1 − H(p)/ln k over every distribution with the given top probability. Points: our run.",
              size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "Neither field is shown to be calibrated here; the card recommends gating on confidence, and calibration is a later part.",
              size=8, fill=SOFT, anchor="start")
    return emit("07", "two-confidences", "Two fields called confidence",
                "The entropy-based confidence can sit far below the probability of the answer it accompanies.",
                "option-marker scoring", vw, vh, s)


# ------------------------------------------------------------------ FIG 09 local vs global attention
def fig09():
    vw, vh = 1016, 668
    q = Q["route"]
    L = q["seq_len"]
    segs = q["segments"]
    half = 64
    s = eyebrow(32, 40, "modernbert-large's 28 layers: every third attends globally; the rest see 64 positions either side")
    # layer pattern strip
    for i in range(28):
        g = i % 3 == 0
        x = 110 + i * 29
        s += rect(x, 62, 25, 22, INK if g else "rgba(45,49,66,0.10)", stroke=INK if g else "rgba(45,49,66,0.35)", rx=2)
        s += mono(x + 12.5, 77, "G" if g else "L", size=9, fill="#ffffff" if g else MUTED, weight="600")
        s += mono(x + 12.5, 97, str(i), size=7, fill=SOFT)
    s += mono(32, 77, "layer", size=8, fill=SOFT, anchor="start")
    s += mono(110, 114, "G: global, 10 layers, RoPE θ = 160,000 · L: local window, 18 layers, RoPE θ = 10,000",
              size=8, fill=MUTED, anchor="start")
    cs = 2.3
    for gi, (title, local) in enumerate((("local layer: attend where |i − j| ≤ 64", True),
                                         ("global layer: attend everywhere", False))):
        x0, y0 = 110 + gi * 460, 190
        s += txt(x0, y0 - 38, title, size=12, weight="600", anchor="start")
        # segment bars along top and left
        for i, g in enumerate(segs):
            col = SEG_STROKE[g]
            s += rect(x0 + i * cs, y0 - 12, cs, 7, col)
            s += rect(x0 - 12, y0 + i * cs, 7, cs, col)
        for i in range(L):
            lo, hi = (max(0, i - half), min(L - 1, i + half)) if local else (0, L - 1)
            s += rect(x0 + lo * cs, y0 + i * cs, (hi - lo + 1) * cs, cs, MUTED, opacity=0.30)
        m = q["markers"][0]
        lo, hi = (max(0, m - half), min(L - 1, m + half)) if local else (0, L - 1)
        s += rect(x0 + lo * cs, y0 + m * cs, (hi - lo + 1) * cs, cs, ACCENT)
        s += rect(x0, y0, L * cs, L * cs, "none", stroke=RULE_SOLID, sw=1)
        # state region bracket on the x axis
        st0, st1 = segs.index("state"), len(segs) - 2
        yb = y0 + L * cs + 10
        s += f'<line x1="{x0 + st0 * cs:.1f}" y1="{yb}" x2="{x0 + (st1 + 1) * cs:.1f}" y2="{yb}" stroke="{SER1}" stroke-width="2"/>'
        s += mono(x0 + (st0 + st1) / 2 * cs, yb + 14, f"ticket: positions {st0}–{st1}", size=8, fill=SER1)
        s += mono(x0 + L * cs / 2, yb + 32, "key position j →", size=8, fill=SOFT)
        # notes sit outside the grid, so no cell of either mask is hidden
        if local:
            s += mono(x0 + L * cs + 8, y0 + m * cs + 4, f"row {m} sees 0–{hi}", size=8, fill=ACCENT, anchor="start", weight="600")
            s += mono(x0 + L * cs + 8, y0 + m * cs + 18, f"{hi - st0 + 1} of 88 ticket", size=8, fill=INK, anchor="start")
            s += mono(x0 + L * cs + 8, y0 + m * cs + 30, "tokens", size=8, fill=INK, anchor="start")
        else:
            s += mono(x0 + L * cs + 8, y0 + m * cs + 4, f"row {m} sees all {L}", size=8, fill=ACCENT, anchor="start", weight="600")
    s += mono(110 - 34, 190 + L * cs / 2, "query i", size=8, fill=SOFT, anchor="middle")
    s += key(vh - 64, vw, [("attended", MUTED, "bar", 0.30), ("billing marker's row", ACCENT, "bar", 1),
                           ("question", SER2, "bar", 1), ("options", SER3, "bar", 1), ("ticket", SER1, "bar", 1)])
    s += mono(32, vh - 16, "Computed from the checkpoint's layer_types and local_attention = 128, with transformers 5.17's rule |i − j| ≤ local_attention / 2. Route row, 141 positions.",
              size=8, fill=SOFT, anchor="start")
    return emit("09", "local-global-attention", "What a marker can see",
                "In local layers the billing marker reaches only the start of the ticket; the rest arrives through global layers.",
                "inside laya", vw, vh, s)


# ------------------------------------------------------------------ FIG 10 act head saturation
def fig10():
    vw, vh = 1016, 460
    sc = EN["scale"]
    s = eyebrow(32, 40, "why act_probability is 1.0: the head's output is never normalised, and the act head reads it raw")
    a = Axes(100, 90, 400, 230, (0, 3), (10, 100000), ylog=True)
    s += txt(100, 72, "[CLS] vector length, log scale", size=12, weight="600", anchor="start")
    s += a.frame([], [10, 100, 1000, 10000, 100000], yfmt=lambda v: f"{v:,}")
    for i, qid in enumerate(("route", "urgency", "refund")):
        b0, b1 = sc["cls_norm_backbone"][i], sc["cls_norm_after_head"][i]
        cx = a.X(i + 0.5)
        for dx, v, col, lab in ((-26, b0, MUTED, "after backbone"), (6, b1, ACCENT, "after head")):
            s += rect(cx + dx, a.Y(v), 20, a.Y(10) - a.Y(v), col, opacity=0.8)
            s += mono(cx + dx + 10, a.Y(v) - 6, f"{v:,.1f}", size=8, fill=col, weight="600")
        s += mono(cx, a.y0 + a.h + 14, qid, size=8, fill=INK)
    # act logits
    b = Axes(610, 90, 340, 230, (-5000, 5000), (0, 3))
    s += txt(610, 72, "act head logits per row", size=12, weight="600", anchor="start")
    s += (f'<line x1="{b.X(0)}" y1="{b.y0}" x2="{b.X(0)}" y2="{b.y0 + b.h}" stroke="{RULE_SOLID}"/>')
    s += (f'<line x1="{b.x0}" y1="{b.y0 + b.h}" x2="{b.x0 + b.w}" y2="{b.y0 + b.h}" stroke="{RULE_SOLID}"/>')
    for v in (-5000, -2500, 0, 2500, 5000):
        s += mono(b.X(v), b.y0 + b.h + 14, f"{v:,}".replace("-", "−"), size=8, fill=SOFT)
    for i, qid in enumerate(("route", "urgency", "refund")):
        act, esc_ = sc["act_logits"][i]
        yy = b.y0 + 18 + i * 72
        s += mono(b.x0 - 8, yy + 16, qid, size=8, fill=INK, anchor="end")
        s += rect(b.X(0), yy, b.X(act) - b.X(0), 14, ACCENT, opacity=0.8)
        s += mono(b.X(act) - 4, yy + 11, f"act {act:,.1f}", size=8, fill="#ffffff", anchor="end", weight="600")
        s += rect(b.X(esc_), yy + 18, b.X(0) - b.X(esc_), 14, MUTED, opacity=0.8)
        s += mono(b.X(esc_) + 4, yy + 29, f"escalate {esc_:,.1f}".replace("-", "−"), size=8, fill="#ffffff", anchor="start", weight="600")
        s += mono(b.X(0) + 6, yy + 48, "softmax → act 1.0000", size=8, fill=INK, anchor="start")
    s += key(vh - 70, vw, [("[CLS] after the backbone", MUTED, "bar", 0.8), ("[CLS] after the two head layers", ACCENT, "bar", 0.8)])
    s += mono(32, vh - 30, "Our run: the [CLS] row's L2 norm leaving the backbone and leaving the second head layer, and the act head's two logits, for each question row.",
              size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "The scorer starts with a LayerNorm, so option probabilities are unaffected. Mechanism first reported in laya issue #185.",
              size=8, fill=SOFT, anchor="start")
    return emit("10", "act-head-saturation", "Why the act head always says act",
                "The [CLS] vector grows about 300 times through the head, and the act head has no normalisation to absorb it.",
                "inside laya", vw, vh, s)


# ------------------------------------------------------------------ FIG 11 parameter accounting
def fig11():
    vw, vh = 1016, 400
    P = EN["params"]
    tot, bb, hd = EN["params_total"], EN["params_backbone"], EN["params_head"]
    s = eyebrow(32, 40, "where laya's 421,293,827 parameters are: counted from the loaded checkpoint")
    x0, W = 32, 952
    parts = [("token embeddings", P["backbone: token embeddings + norm"], SER2, 0.45),
             ("attention × 28", P["backbone: attention"], SER2, 0.30),
             ("GeGLU feed-forward × 28", P["backbone: GeGLU MLP"], SER2, 0.18),
             ("norms", P["backbone: norms"], SER2, 0.6),
             ("decision head", hd, ACCENT, 0.85)]
    y = 110
    s += txt(x0, y - 12, "the whole model", size=12, weight="600", anchor="start")
    x = x0
    for name, n, col, op in parts:
        w = n / tot * W
        s += rect(x, y, w, 40, col, stroke="#ffffff", sw=1, opacity=op)
        if w > 90:
            s += mono(x + w / 2, y + 17, name, size=9, fill=INK, weight="600")
            s += mono(x + w / 2, y + 31, f"{n:,} · {n / tot * 100:.1f}%", size=8, fill=INK)
        x += w
    s += masked(x0 + W - 4, y + 56, f"decision head {hd:,} · {hd / tot * 100:.1f}%", size=8, fill=ACCENT, anchor="end")
    s += masked(x0 + (tot - hd - P["backbone: norms"]) / tot * W - 4, y + 56 + 14,
                f"norms {P['backbone: norms']:,} (a sliver)", size=8, fill=MUTED, anchor="end")
    # bracket for backbone
    bx1 = x0 + bb / tot * W
    s += f'<line x1="{x0}" y1="{y - 4}" x2="{bx1:.1f}" y2="{y - 4}" stroke="{SER2}" stroke-width="2"/>'
    s += mono(bx1 - 4, y - 8, f"backbone {bb:,} → card: 395M", size=8, fill=SER2, anchor="end", weight="600")
    # the head, zoomed
    y2 = 250
    s += txt(x0, y2 - 12, "the decision head, zoomed to the same width", size=12, weight="600", anchor="start")
    hparts = [("2 transformer layers", P["decision head: 2 transformer layers"], 0.85),
              ("scorer", P["decision head: option scorer"], 0.55),
              ("act head", P["decision head: act/escalate head"], 0.35),
              ("type emb.", P["decision head: question-type embedding"], 1.0)]
    x = x0
    small = []
    for name, n, op in hparts:
        w = n / hd * W
        s += rect(x, y2, w, 40, ACCENT, stroke="#ffffff", sw=1, opacity=op)
        if w > 120:
            s += mono(x + w / 2, y2 + 17, name, size=9, fill=INK, weight="600")
            s += mono(x + w / 2, y2 + 31, f"{n:,}", size=8, fill=INK)
        else:
            small.append((name, n, x + w / 2))
        x += w
    # each small segment gets its own leader, stepped down so labels never overlap
    for i, (name, n, cx) in enumerate(small):
        ly = y2 + 56 + i * 14
        s += f'<line x1="{cx:.1f}" y1="{y2 + 41}" x2="{cx:.1f}" y2="{ly - 9}" stroke="{MUTED}" stroke-width="0.8"/>'
        s += mono(cx - 6, ly, f"{name} {n:,}", size=8, fill=MUTED, anchor="end")
    s += mono(32, vh - 30, f"Total {tot:,} → card: 421M (rounds to it). Backbone {bb:,} → card and ModernBERT paper: 395M. No masked-LM head is in the checkpoint.",
              size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "Computed: parameter counts summed from the loaded model (our run), buffers excluded. Stored in FP16: 842,609,210 bytes.",
              size=8, fill=SOFT, anchor="start")
    return emit("11", "parameter-accounting", "Where the parameters live",
                "More than half of Laya is feed-forward weight; the decision head is 6.3%.",
                "parameters", vw, vh, s)


# ------------------------------------------------------------------ FIG 12 three checkpoints
def fig12():
    vw, vh = 1016, 670
    others = {o["checkpoint"]: o for o in DATA["others"]}
    cks = [("laya", EN, "ModernBERT-large · 421.3M · 512 · T fitted"),
           ("laya-multilingual", others["multilingual"], "mmBERT-base · 321.9M · 1,024 · T = 1.0"),
           ("laya-typed-decisions", others["typed-decisions"], "ModernBERT-large · 421.3M · 1,024 · T fitted")]
    s = eyebrow(32, 40, "the same ticket and questions through all three checkpoints")
    cw, x00 = 300, 110
    for ci, (name, d, sub) in enumerate(cks):
        x = x00 + ci * (cw + 6)
        s += txt(x, 72, name, size=12, weight="600", anchor="start")
        s += mono(x, 86, sub, size=8, fill=SOFT, anchor="start")
        qs = {q["id"]: q for q in d["questions"]}
        for ri, qid in enumerate(("route", "urgency", "refund")):
            q = qs[qid]
            y0 = 120 + ri * 162
            if ci == 0:
                s += txt(32, y0 + 60, qid, size=12, weight="600", anchor="start")
            a = Axes(x + 10, y0 + 18, cw - 30, 100, (0, q["n_options"]), (0, 1))
            s += a.frame([], [0, 0.5, 1], yfmt=lambda v: f"{v:.1f}", grid=True)
            k = q["n_options"]
            top = max(range(k), key=lambda i: q["p_returned"][i])
            bw = (cw - 30) / k * 0.55
            for i, p in enumerate(q["p_returned"]):
                cx = a.X(i + 0.5)
                col = ACCENT if i == top else MUTED
                s += rect(cx - bw / 2, a.Y(p), bw, a.Y(0) - a.Y(p), col, opacity=0.85 if i == top else 0.5)
                s += mono(cx, a.Y(p) - 5, fmt(p, 3), size=8, fill=col, weight="600" if i == top else "400")
                lab = OPT_NAMES[qid][i].replace("level ", "")
                s += mono(cx, a.y0 + a.h + 12, lab, size=8, fill=INK)
            extra = ""
            if qid == "urgency":
                extra = f" · score {d['api_response']['answers']['urgency']['score']:.2f}"
            s += mono(x + 10, y0 + 150, f"T = {q['temperature']:.3f}{extra}", size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 30, "Our run: laya 0.3.20, CPU, FP32, all three checkpoints from commit 55cf4c4e. Urgency options are levels 0–4. Multilingual's billing logit leads by 14.7.",
              size=8, fill=SOFT, anchor="start")
    s += mono(32, vh - 16, "Multilingual tokenizes the rows to 139, 141 and 122 tokens (402 input tokens); the other two match the English 141, 136 and 122.",
              size=8, fill=SOFT, anchor="start")
    return emit("12", "three-checkpoints", "One ticket, three checkpoints",
                "All three pick billing and a refund; they disagree on urgency and on how sure they are.",
                "parameters", vw, vh, s)


# ------------------------------------------------------------------ FIG 13 lineage
def fmt_line(x, y, parts, size=9):
    """parts: list of (text, kind) with kind in plain / marker / special / option / state."""
    colours = {"plain": INK, "marker": ACCENT, "special": MUTED, "option": SER3, "state": SER1, "question": SER2}
    spans = "".join(f'<tspan fill="{colours[k]}" font-weight="{"600" if k == "marker" else "400"}">{esc(t)}</tspan>'
                    for t, k in parts)
    return (f'<text x="{x}" y="{y}" font-size="{size}" font-family="{MONO}" text-anchor="start" '
            f'xml:space="preserve">{spans}</text>')


def fig13():
    vw, vh = 1016, 640
    s = eyebrow(32, 40, "from one fixed head to one marker per option: each method's input for the route question")
    T, O, M, S_, P_, Qn = "state", "option", "marker", "special", "plain", "question"
    rows = [
        ("2019", "BERT", "NAACL", [[("[CLS] ", S_), ("ticket", T), (" [SEP] ", S_), ("billing", O), (" [SEP]", S_),
                                    ("   × 4 sequences, one per option", P_)]],
         "4 sequences", "w · [CLS] per sequence, softmax across the 4"),
        ("2019", "Yin, Hay, Roth", "EMNLP", [[("[CLS] ", S_), ("ticket", T), (" [SEP] ", S_), ("This ticket is about billing.", O),
                                              (" [SEP]", S_), ("   × 4", P_)]],
         "4 passes", "entailment probability per label"),
        ("2021", "PET", "EACL", [[("ticket", T), (" Which team should own it? ", Qn), ("[MASK]", M), (".", P_)]],
         "1 pass", "word scores at [MASK]; a verbalizer maps words to labels"),
        ("2022", "UniMC", "EMNLP", [[("[CLS] ", S_), ("[O-MASK]", M), (" billing ", O), ("[O-MASK]", M), (" technical ", O),
                                     ("[O-MASK]", M), (" account ", O), ("[O-MASK]", M), (" sales", O)],
                                    [(" [SEP] ", S_), ("Which team? ", Qn), ("[SEP] ", S_), ("ticket", T), (" [SEP]", S_)]],
         "1 pass", "yes/no at each [O-MASK], softmax across options; options masked from each other"),
        ("2024", "GLiNER", "NAACL", [[("[ENT]", M), (" billing ", O), ("[ENT]", M), (" technical ", O), ("[ENT]", M),
                                      (" account ", O), ("[ENT]", M), (" sales ", O), ("[SEP] ", S_), ("ticket", T)]],
         "1 pass", "each type's vector matched to text spans (entity recognition)"),
        ("2025", "GLiClass", "preprint", [[("«LABEL»", M), (" billing ", O), ("«LABEL»", M), (" technical ", O), ("«LABEL»", M),
                                           (" account ", O), ("«LABEL»", M), (" sales ", O), ("ticket", T)]],
         "1 pass", "each label's vector scored against the text"),
        ("2026", "GLiGuard", "preprint", [[("task and label schema, as tokens", O), ("  +  ", P_), ("text", T),
                                           ("   (many safety tasks at once)", P_)]],
         "1 pass", "labels scored per task in the schema"),
        ("2026", "Laya", "model card + code", [[("[CLS] ", S_), ("choice question: Which support team…? ", Qn), ("[SEP] ", S_),
                                                ("[MASK]", M), (" billing: … ", O), ("[MASK]", M), (" technical: …", O)],
                                               [("[MASK]", M), (" account: … ", O), ("[MASK]", M), (" sales: … ", O),
                                                ("[SEP] ", S_), ("ticket", T), (" [SEP]", S_)],
                                               [("one row like this per question, all rows in one batch", P_)]],
         "1 batch", "scorer on each [MASK], softmax within the question"),
    ]
    xs = {"year": 32, "name": 80, "fmt": 210, "pass": 760, "read": 842}
    y = 80
    for h, col in (("year", "year"), ("method", "name"), ("input for the route question", "fmt"),
                   ("work", "pass"), ("readout", "read")):
        s += eyebrow(xs[col], y, h)
    y += 14
    for yr, name, venue, lines, work, read in rows:
        focal = name == "Laya"
        words, line, out = read.split(), "", []
        for w_ in words:
            if len(line) + len(w_) + 1 > 30:
                out.append(line)
                line = w_
            else:
                line = (line + " " + w_).strip()
        out.append(line)
        rh = max(32 + 14 * (len(lines) - 1), 26 + 12 * len(out))
        if focal:
            s += rect(24, y, vw - 48, rh + 10, ACCENT_TINT, stroke=ACCENT, rx=4)
        s += mono(xs["year"], y + 20, yr, size=9, fill=INK, anchor="start", weight="600")
        s += txt(xs["name"], y + 20, name, size=11, weight="600", anchor="start", fill=ACCENT if focal else INK)
        s += mono(xs["name"], y + 33, venue, size=7.5, fill=SOFT, anchor="start")
        for li, parts in enumerate(lines):
            s += fmt_line(xs["fmt"], y + 20 + li * 14, parts, size=8.5)
        s += mono(xs["pass"], y + 20, work, size=8.5, fill=INK, anchor="start", weight="500")
        for li, t in enumerate(out):
            s += mono(xs["read"], y + 20 + li * 12, t, size=7.5, fill=MUTED, anchor="start")
        y += rh + 16
        if not focal:
            s += f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}"/>'
    vh = int(y + 76)   # the canvas ends where the rows do
    s += key(vh - 56, vw, [("marker token", ACCENT, "bar", 1), ("option / label", SER3, "bar", 1),
                           ("question", SER2, "bar", 1), ("the ticket", SER1, "bar", 1)])
    s += mono(32, vh - 16, "From the cited papers and Laya's code; formats are paraphrased onto our ticket. GLiNER labels entity spans rather than classifying a whole text.",
              size=8, fill=SOFT, anchor="start")
    return emit("13", "lineage", "From one head to one marker per option",
                "The input formats that led to Laya's, written for the same question.",
                "lineage", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06,
        "07": fig07, "09": fig09, "10": fig10, "11": fig11, "12": fig12, "13": fig13}

if __name__ == "__main__":
    want = sys.argv[1:] or list(FIGS)
    for k in want:
        FIGS[k]()
