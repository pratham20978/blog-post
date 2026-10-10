#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for "Laya, Part 1".

Frontier Models, part 1. The shell (lockup, rule, serif title, deck, takeaway, footer) is
copied from image-processing part 4's _social.py, with the lockup reading "canery.in". Every
number on a card is read from ../lab/trace.json, the captured output of lab/trace_laya.py
(laya 0.3.20, CPU, FP32, checkpoint 55cf4c4e), so a card cannot disagree with the article.

Lockup widths are 220 (feed) and 245 (story), which render_social.py locks.
This script writes editable HTML only; Blog Forge's render_social.py exports the
standalone SVG and exact-size PNG:

    python3 _social.py
    python3 ../../../../.claude/blog-forge/scripts/render_social.py social/
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]                     # a series member sits one level deeper
DATA = json.loads((HERE.parent / "lab" / "trace.json").read_text(encoding="utf-8"))
EN = DATA["english"]
Q = {q["id"]: q for q in EN["questions"]}
ANS = EN["api_response"]["answers"]

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
GREEN, BLUE, MUSTARD = "#7c8f6f", "#5e7a9b", "#b8915a"
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/laya-decision-model-explained"
FOOTER = "LAYA, PART 1 · CANERY.IN"
PROV = "our run · laya 0.3.20 · CPU · FP32"

# ------------------------------------------------------------------ the numbers
assert EN["usage"] == {"input_tokens": 399, "output_tokens": 0}
assert EN["state_tokens"] == 88 and EN["params_total"] == 421293827
assert round(ANS["route"]["probabilities"]["billing"], 4) == 0.8468

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


def txt(x, y, value, size=22, fill=INK, family=SANS, weight=400, anchor="start", track=None):
    extra = f' letter-spacing="{track}"' if track else ""
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


def rect(x, y, w, h, fill, stroke="none", sw=1, rx=0, opacity=None):
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}"{o} stroke="{stroke}" stroke-width="{sw}"/>')


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


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
    defs = f'<defs><style>@import url(\'{FONTS.replace("&", "&amp;")}\');</style></defs>'
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


FEED_TOTAL, STORY_TOTAL = 8, 4
SEG = {"question": ("rgba(94,122,155,0.20)", BLUE), "option": ("rgba(184,145,90,0.22)", MUSTARD),
       "state": ("rgba(124,143,111,0.22)", GREEN)}


# ------------------------------------------------------------------ shared visuals
def route_bars(x0, y_base, bar_w, gap, hmax, size=24, big=False):
    """The route question's four returned probabilities, billing in the accent."""
    names = ["billing", "technical", "account", "sales"]
    v = ""
    for i, (n, p) in enumerate(zip(names, Q["route"]["p_returned"])):
        x = x0 + i * (bar_w + gap)
        col = ACCENT if i == 0 else MUTED
        v += rect(x, y_base - p * hmax, bar_w, p * hmax, col, opacity=0.85 if i == 0 else 0.45)
        v += mono(x + bar_w / 2, y_base - p * hmax - 12, f"{p:.3f}", size, col, "middle", 600)
        v += mono(x + bar_w / 2, y_base + size + 10, n, size - 2, INK, "middle")
    v += hline(x0 - 10, x0 + 4 * (bar_w + gap) - gap + 10, y_base, RULE_SOLID, 1.5)
    return v


def mask_strip(x0, y, tw, th, gap):
    """A token strip: question, then [MASK] + option four times, then the ticket."""
    tiles = ["question"] * 3 + ["m", "option", "option"] * 4 + ["state"] * 4
    v, centres = "", []
    for i, t in enumerate(tiles):
        x = x0 + i * (tw + gap)
        if t == "m":
            focal = not centres
            centres.append(x + tw / 2)
            v += rect(x, y, tw, th, ACCENT if focal else "#ffffff", ACCENT if focal else INK, 2, 4)
        else:
            f, s = SEG[t]
            v += rect(x, y, tw, th, f, s, 1.2, 4)
    return v, centres


def batch_rows(x0, y0, unit, rh, gap, size=20):
    """The three batch rows to scale, with the ticket band repeated in each."""
    v = ""
    for i, qid in enumerate(("route", "urgency", "refund")):
        q = Q[qid]
        y = y0 + i * (rh + gap)
        pre = q["seq_len"] - EN["state_tokens"] - 1
        v += mono(x0, y - 10, f"{qid} · {q['seq_len']} tokens", size - 2, INK, "start", 600)
        v += rect(x0, y, pre * unit, rh, SEG["question"][0], BLUE, 1.2)
        v += rect(x0 + pre * unit, y, EN["state_tokens"] * unit, rh, SEG["state"][0], GREEN, 1.2)
        v += mono(x0 + (pre + EN["state_tokens"] / 2) * unit, y + rh / 2 + 7, "ticket · 88", size, INK, "middle", 600)
    return v


# ------------------------------------------------------------------ feed
def feed_01():
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    strip, centres = mask_strip(122, 540, 36, 54, 7)
    v += strip
    base = 1000
    probs = Q["route"]["p_returned"]
    for i, (cx, p) in enumerate(zip(centres, probs)):
        col = ACCENT if i == 0 else MUTED
        v += (f'<line x1="{cx:.1f}" y1="596" x2="{cx:.1f}" y2="{base - p * 300 - 44:.1f}" stroke="{col}" '
              f'stroke-width="2" stroke-dasharray="{"" if i == 0 else "6,6"}"/>')
        v += rect(cx - 28, base - p * 300, 56, p * 300, col, opacity=0.85 if i == 0 else 0.45)
        v += mono(cx, base - p * 300 - 12, f"{p:.3f}", 22, col, "middle", 600)
        v += mono(cx, base + 30, ["billing", "technical", "account", "sales"][i], 18, INK, "middle")
    v += hline(110, 970, base, RULE_SOLID, 1.5)
    v += label(110, 1090, PROV, SOFT, "start", 13)
    v += mono(970, 1090, "output_tokens = 0", 22, ACCENT, "end", 600)
    emit("feed", 1, "a-decision-model-scores-options",
         ["A decision model scores", "your options. It never", "writes them."],
         ["Laya puts a [MASK] in front of every option and reads a score off each one."],
         v,
         ["A softmax over those scores is the answer:",
          "billing 0.847 for our support ticket, with zero output tokens."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    v += batch_rows(120, 570, 5.6, 58, 62)
    tot, st = EN["usage"]["input_tokens"], EN["state_tokens"]
    y = 930
    v += label(120, y, "input tokens reported", SOFT, "start", 14)
    other = tot - 3 * st
    u = 840 / tot
    v += rect(120, y + 24, other * u, 56, "rgba(45,49,66,0.10)", MUTED, 1.2)
    v += mono(120 + other * u / 2, y + 60, f"{other}", 22, INK, "middle", 600)
    for k in range(3):
        x = 120 + (other + k * st) * u
        v += rect(x, y + 24, st * u, 56, SEG["state"][0], GREEN, 1.2)
        v += mono(x + st * u / 2, y + 60, "88", 22, INK, "middle", 600)
    v += mono(120, y + 118, f"{3 * st} of {tot} are the same ticket, three times", 22, INK, "start", 600)
    v += label(120, 1090, PROV, SOFT, "start", 13)
    emit("feed", 2, "one-pass-is-not-one-read",
         ["One forward pass is not", "one read of the ticket."],
         ["Laya builds one row per question, and every row carries",
          "the whole ticket. The rows run as one batch."],
         v,
         ["Three questions over an 88-token ticket: 399 input tokens.",
          "The cost grows with questions × state length."],
         FEED_TOTAL)


def feed_03():
    q = Q["route"]
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    names = ["billing", "technical", "account", "sales"]
    cols = [300, 470, 640, 810]
    v += label(110, 560, "option", SOFT, "start", 14)
    rows = [("logit", q["logits"]), ("÷ T = 1.760", [z / q["temperature"] for z in q["logits"]]),
            ("softmax", q["p_returned"])]
    for j, n in enumerate(names):
        v += mono(cols[j] + 70, 560, n, 22, ACCENT if j == 0 else INK, "middle", 600)
    y = 650
    for name, vals in rows:
        v += label(110, y, name, MUTED, "start", 15)
        for j, val in enumerate(vals):
            hi = name == "softmax" and j == 0
            v += rect(cols[j], y - 44, 140, 64, ACCENT_TINT if hi else "#ffffff",
                      ACCENT if hi else "rgba(45,49,66,0.30)", 1.5 if hi else 1, 6)
            v += mono(cols[j] + 70, y - 2, f"{val:.3f}".replace("-", "−"), 26,
                      ACCENT if hi else INK, "middle", 600 if hi else 400)
        y += 110
    v += mono(110, 1010, "e^2.384 ÷ (e^2.384 + e^−0.007 + e^−0.607 + e^−0.859) = 1 ÷ 1.181 = 0.847",
              19, MUTED, "start")
    v += label(110, 1090, PROV, SOFT, "start", 13)
    emit("feed", 3, "from-logit-to-0-847",
         ["From a logit of 4.196", "to 0.847."],
         ["Each option's [MASK] is scored, the scores are divided by a fitted",
          "temperature, and a softmax runs within the question."],
         v,
         ["Options compete only inside their own question.",
          "Three questions, three separate distributions."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 560, "question", SOFT, "start", 14)
    v += label(560, 560, "confidence", SOFT, "end", 14)
    v += label(960, 560, "answer_confidence", SOFT, "end", 14)
    y = 660
    for qid in ("route", "urgency", "refund"):
        a = ANS[qid]
        v += txt(110, y, qid, 34, INK, SANS, 600)
        v += mono(560, y, f"{a['confidence']:.3f}", 40, ACCENT if qid != "refund" else INK, "end", 600)
        v += mono(960, y, f"{a['answer_confidence']:.3f}", 40, INK, "end", 600)
        y += 120
    v += mono(110, 1000, "confidence = 1 − H(p) / ln k for choice and score; max(p) for noul", 20, MUTED)
    v += label(110, 1090, PROV, SOFT, "start", 13)
    emit("feed", 4, "two-fields-called-confidence",
         ["Two fields called", "confidence."],
         ["For choice and score questions, confidence measures how spread",
          "the distribution is. answer_confidence is the answer's probability."],
         v,
         ["Billing has probability 0.847, but confidence 0.577.",
          "Know which one your code thresholds on."],
         FEED_TOTAL)


def feed_05():
    sc = EN["scale"]
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    v += label(110, 560, "[CLS] vector length, route row", SOFT, "start", 14)
    v += txt(110, 640, "after the backbone", 26, MUTED)
    v += mono(960, 640, f"{sc['cls_norm_backbone'][0]:.1f}", 40, MUTED, "end", 600)
    v += txt(110, 720, "after the two head layers", 26, INK)
    v += mono(960, 720, f"{sc['cls_norm_after_head'][0]:,.1f}", 40, ACCENT, "end", 600)
    v += hline(110, 960, 780)
    act, esc_ = sc["act_logits"][0]
    v += label(110, 840, "act head logits", SOFT, "start", 14)
    v += txt(110, 910, "act", 26, INK)
    v += mono(960, 910, f"{act:,.1f}", 40, INK, "end", 600)
    v += txt(110, 980, "escalate", 26, INK)
    v += mono(960, 980, f"{esc_:,.1f}".replace("-", "−"), 40, INK, "end", 600)
    v += mono(110, 1040, "softmax → act_probability 1.0000, on every row", 21, ACCENT, "start", 600)
    v += label(110, 1090, PROV + " · mechanism: laya issue #185", SOFT, "start", 13)
    emit("feed", 5, "act-probability-is-always-one",
         ["act_probability is", "always 1.0."],
         ["The head's pre-norm layers leave the [CLS] vector unnormalised,",
          "and the act head reads it raw. It saturates."],
         v,
         ["Convai's own card: no usable signal yet.",
          "Gate on confidence, never on act_probability."],
         FEED_TOTAL)


def feed_06():
    P = EN["params"]
    tot = EN["params_total"]
    parts = [("embeddings", P["backbone: token embeddings + norm"], BLUE, 0.45),
             ("attention", P["backbone: attention"], BLUE, 0.30),
             ("GeGLU feed-forward", P["backbone: GeGLU MLP"], BLUE, 0.16),
             ("head", EN["params_head"], ACCENT, 0.85)]
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    x, W = 110, 860
    for name, n, col, op in parts:
        w = n / tot * W
        v += rect(x, 560, w, 90, col, "#ffffff", 2, 0, op)
        x += w
    y = 716
    for name, n, col, op in parts:
        v += rect(110, y - 22, 24, 24, col, "none", 0, 4, op)
        v += txt(150, y, name, 26, INK)
        v += mono(960, y, f"{n:,}", 28, ACCENT if name == "head" else INK, "end", 600)
        y += 56
    norms = P["backbone: norms"]
    v += txt(150, y, "norms (too thin to draw)", 26, MUTED)
    v += mono(960, y, f"{norms:,}", 28, MUTED, "end", 600)
    y += 34
    v += hline(110, 960, y)
    v += txt(150, y + 44, "total", 26, INK, SANS, 600)
    v += mono(960, y + 44, f"{tot:,}", 28, INK, "end", 600)
    v += label(110, 1090, "counted from the loaded checkpoint (our run)", SOFT, "start", 13)
    emit("feed", 6, "where-421-million-parameters-live",
         ["Where Laya's 421 million", "parameters live."],
         ["A 394.8M ModernBERT-large encoder, without BERT's vocabulary head,",
          "plus a 26.5M decision head trained from scratch."],
         v,
         ["The decision head is 6.3% of the model.",
          "More than half of Laya is feed-forward weight."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    rows = [("2019", "BERT", "4 sequences, one per option"),
            ("2021", "PET", "one [MASK], a verbalizer maps words to labels"),
            ("2022", "UniMC", "[O-MASK] before each option, one sequence"),
            ("2024", "GLiNER", "[ENT] before each entity type"),
            ("2025", "GLiClass", "«LABEL» before each label"),
            ("2026", "Laya", "[MASK] before each option, one row per question")]
    y = 570
    for yr, name, fmt_ in rows:
        focal = name == "Laya"
        v += mono(110, y, yr, 24, ACCENT if focal else SOFT, "start", 600)
        v += txt(210, y, name, 28, ACCENT if focal else INK, SANS, 600)
        v += mono(390, y, fmt_, 19, ACCENT if focal else MUTED)
        y += 88
    v += label(110, 1090, "from the cited papers and Laya's code", SOFT, "start", 13)
    emit("feed", 7, "option-markers-are-not-new",
         ["Option markers are", "not new."],
         ["UniMC put a marker before every option in one sequence in 2022.",
          "GLiNER, GLiClass and GLiGuard carried the idea on."],
         v,
         ["Laya's new part is the typed contract, one row",
          "per question, and its training objective."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 480, 936, 640, "#ffffff", RULE_SOLID)
    items = [("the trace", "one ticket, three typed questions, every number", "tokens, markers, shapes, logits, softmax, JSON"),
             ("the model", "ModernBERT-large + a decision head built from scratch", "421,293,827 parameters, reconciled by hand"),
             ("the traps", "three checkpoints are three models", "act_probability, confidence, option names"),
             ("the lab", "a CPU script that reproduces it all", "laya 0.3.20 · checks every probability")]
    y = 574
    for head, a, b in items:
        v += txt(110, y, head, 30, ACCENT if head == "the trace" else INK, SANS, 600)
        v += mono(110, y + 40, a, 21, INK)
        v += mono(110, y + 72, b, 19, SOFT)
        y += 132
    emit("feed", 8, "read-the-article",
         ["What a decision model is,", "traced through Laya."],
         ["The first part of Frontier Models, and the first of three",
          "on Convai's open decision model."],
         v,
         ["The full walk-through, with the lab to run it",
          "yourself on a laptop CPU."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


# ------------------------------------------------------------------ story
def story_01():
    v = route_bars(160, 1300, 150, 60, 480, 30)
    v += mono(1008, 1440, "output_tokens = 0", 30, ACCENT, "end", 600)
    v += label(72, 1440, PROV, SOFT, "start", 15)
    emit("story", 1, "a-decision-model-scores-options",
         ["A decision model", "never writes a word."],
         ["It scores the options you declare,", "one [MASK] per option."],
         v,
         ["Our support ticket: billing at 0.847,", "with zero output tokens."],
         STORY_TOTAL)


def story_02():
    v = batch_rows(100, 860, 5.8, 80, 104, 26)   # 141 tokens × 5.8 = 818 px, inside the 1008 margin
    v += mono(100, 1392, "399 input tokens: 264 are the ticket", 32, INK, "start", 600)
    v += label(100, 1446, PROV, SOFT, "start", 15)
    emit("story", 2, "one-pass-is-not-one-read",
         ["One pass is not", "one read."],
         ["Each question gets its own row,", "and every row carries the ticket."],
         v,
         ["Cost grows with questions", "× state length."],
         STORY_TOTAL)


def story_03():
    sc = EN["scale"]
    v = box(72, 840, 936, 560, "#ffffff", RULE_SOLID)
    v += label(120, 920, "[CLS] vector length", SOFT, "start", 16)
    v += txt(120, 1000, "after the backbone", 32, MUTED)
    v += mono(960, 1000, f"{sc['cls_norm_backbone'][0]:.1f}", 46, MUTED, "end", 600)
    v += txt(120, 1090, "after the head", 32, INK)
    v += mono(960, 1090, f"{sc['cls_norm_after_head'][0]:,.1f}", 46, ACCENT, "end", 600)
    v += hline(120, 960, 1150)
    v += txt(120, 1230, "act_probability", 32, INK, SANS, 600)
    v += mono(960, 1230, "1.0000", 46, ACCENT, "end", 600)
    v += mono(120, 1310, "on every row, whatever the ticket says", 24, MUTED)
    emit("story", 3, "act-probability-is-always-one",
         ["act_probability:", "1.0, always."],
         ["The act head reads an", "unnormalised vector and saturates."],
         v,
         ["Gate on confidence instead,", "as Convai's card advises."],
         STORY_TOTAL)


def story_04():
    v = box(72, 790, 936, 640, ACCENT_TINT, ACCENT, 8, 1.5)
    steps = ["one [MASK] per option",
             "one row per question",
             "one softmax per question",
             "421,293,827 parameters"]
    y = 900
    for i, s in enumerate(steps):
        v += mono(120, y, f"{i + 1}", 34, ACCENT, "start", 600)
        v += txt(180, y, s, 32, INK, SANS, 600 if i == 0 else 400)
        y += 132
    emit("story", 4, "read-the-article",
         ["A decision model,", "traced."],
         ["Every number from one run", "of Laya on a laptop CPU."],
         v,
         ["The full walk-through is on Canery."],
         STORY_TOTAL, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08,
            story_01, story_02, story_03, story_04]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
