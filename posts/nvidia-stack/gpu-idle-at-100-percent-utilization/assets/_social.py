#!/usr/bin/env python3
"""Build the finished Canery feed and Story sources for this article.

Lockup widths are 220 (feed) and 245 (story), which is what
blog-forge/scripts/render_social.py locks. Scales are the part-6 values
multiplied by the same ratio, so the mark keeps its proportions.

NVIDIA Stack, part 3. Same construction as parts 1, 2 and 6 so the series reads as one set.

The shared feed is 1080x1350 for Instagram and LinkedIn. Story frames are
independently composed at 1080x1920. This script writes editable HTML only;
Blog Forge's render_social.py exports the standalone SVG and exact-size PNG.
"""

from __future__ import annotations

import pathlib
import re
import sys

from _build import (
    ACCENT,
    ACCENT_TINT,
    DEFS,
    FONTS,
    INK,
    LINK,
    MONO,
    MUTED,
    PAPER,
    RULE,
    RULE_SOLID,
    SANS,
    SERIF,
    SOFT,
    ascii_upper,
    box,
    esc,
    mono,
    txt,
)

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "social"
ROOT = HERE.parents[3]
VW = 1080


# The brand lockup ships as bird + "Canery" only. Every social frame must read
# "canery.in", so the domain suffix is drawn here in the lockup's own coordinate
# space, on the wordmark's baseline and at its cap height.
LOCKUP_VIEWBOX_W = 671.40      # the source lockup's own width
IN_GAP = -10                   # the source viewBox has trailing padding; close it up
IN_SIZE = 140                  # matches the wordmark's cap height
IN_ADVANCE = 171               # measured advance of ".in" in Geist 600 at IN_SIZE
LOCKUP_FULL_W = LOCKUP_VIEWBOX_W + IN_GAP + IN_ADVANCE


def logo_paths() -> str:
    source = (ROOT / "web/public/brand/canerly-lockup-horizontal.svg").read_text(encoding="utf-8")
    paths = re.findall(r"<path\b[\s\S]*?/>", source)
    if len(paths) != 2:
        raise RuntimeError("Could not read the canonical Canery horizontal lockup")
    suffix = (
        f'<text x="{LOCKUP_VIEWBOX_W + IN_GAP}" y="122.5" font-size="{IN_SIZE}" '
        f'font-family="{SANS}" font-weight="600" text-anchor="start">.in</text>'
    )
    return "\n".join(paths) + "\n" + suffix


LOGO_PATHS = logo_paths()


def lines(x, y, values, *, size, family=SANS, fill=INK, weight="400", gap=None, anchor="start"):
    gap = gap or int(size * 1.16)
    return "".join(
        txt(x, y + index * gap, value, size=size, fill=fill, family=family,
            weight=weight, anchor=anchor)
        for index, value in enumerate(values)
    )


def label(x, y, value, *, fill=SOFT, anchor="start", size=14):
    return mono(x, y, ascii_upper(value), size=size, fill=fill, anchor=anchor,
                weight="500", track="0.12em")


def card(x, y, w, h, title, detail, *, focal=False, tag=None):
    stroke = ACCENT if focal else "rgba(45,49,66,0.28)"
    fill = ACCENT_TINT if focal else "#ffffff"
    result = box(x, y, w, h, fill=fill, stroke=stroke, rx=8, sw=1.2 if focal else 1)
    if tag:
        result += label(x + 22, y + 28, tag, fill=ACCENT if focal else SOFT, size=12)
    result += txt(x + 22, y + 60, title, size=22, fill=ACCENT if focal else INK,
                  family=SANS, weight="600", anchor="start")
    if isinstance(detail, str):
        detail = [detail]
    result += lines(x + 22, y + 92, detail, size=15, family=MONO, fill=MUTED, gap=23)
    return result


def shell(kind, number, total, title, deck, visual, takeaway, *, cta=None):
    if kind == "feed":
        height, logo_y, logo_width, scale = 1350, 72, 220, 220 / LOCKUP_FULL_W
        rule_y, title_y, title_size, title_gap = 150, 245, 58, 66
        deck_y = title_y + len(title) * title_gap + 20
        takeaway_rule, takeaway_y, footer_y = 1168, 1220, 1305
    else:
        height, logo_y, logo_width, scale = 1920, 250, 245, 245 / LOCKUP_FULL_W
        rule_y, title_y, title_size, title_gap = 340, 470, 70, 80
        deck_y = title_y + len(title) * title_gap + 28
        takeaway_rule, takeaway_y, footer_y = 1505, 1570, 1665

    defs = DEFS
    logo = (
        f'<g data-canery-logo="lockup" data-logo-x="72" data-logo-y="{logo_y}" '
        f'data-logo-width="{logo_width}" fill="{INK}" '
        f'transform="translate(72 {logo_y}) scale({scale})">{LOGO_PATHS}</g>'
    )
    body = f'<rect width="{VW}" height="{height}" fill="{PAPER}"/>'
    body += logo
    body += label(1008, logo_y + 35, f"{number:02d} / {total:02d}", anchor="end", size=15)
    body += f'<line x1="72" y1="{rule_y}" x2="1008" y2="{rule_y}" stroke="{RULE}"/>'
    body += lines(72, title_y, title, size=title_size, family=SERIF, gap=title_gap)
    body += lines(72, deck_y, deck, size=22 if kind == "feed" else 26,
                  fill=MUTED, gap=30 if kind == "feed" else 36)
    body += visual
    body += f'<line x1="72" y1="{takeaway_rule}" x2="1008" y2="{takeaway_rule}" stroke="{RULE}"/>'
    body += lines(72, takeaway_y, takeaway, size=22 if kind == "feed" else 27,
                  weight="600", gap=30 if kind == "feed" else 36)
    footer = cta or "WHY YOUR GPU IS IDLE AT 100% · CANERY.IN"
    body += label(72, footer_y, footer, fill=ACCENT if cta else SOFT,
                  size=14 if kind == "feed" else 16)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {height}" '
        f'width="{VW}" height="{height}" role="img">\n{defs}\n{body}\n</svg>'
    )


def emit(kind, number, slug, title, deck, visual, takeaway, *, total, cta=None):
    svg = shell(kind, number, total, title, deck, visual, takeaway, cta=cta)
    html = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<title>{esc(" ".join(title))}</title><link href="{FONTS}" rel="stylesheet">'
        f'<style>html,body{{margin:0;background:{PAPER}}}svg{{display:block}}</style>'
        f'</head><body>{svg}</body></html>'
    )
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"{kind}-{number:02d}-{slug}.html"
    path.write_text(html, encoding="utf-8")
    print(path.name)






def sm_grid(x, y, rows, cols, lit_rows, *, cell=22, gap=5, full_cols=None):
    """A grid of SMs (rows) against time (columns); lit cells had a warp resident."""
    out = ""
    full_cols = cols if full_cols is None else full_cols
    for r in range(rows):
        for c in range(cols):
            on = r < lit_rows and c < full_cols
            out += (f'<rect x="{x + c * (cell + gap)}" y="{y + r * (cell + gap)}" width="{cell}" '
                    f'height="{cell}" rx="3" fill="{INK if on else "#e6e6e6"}" '
                    f'fill-opacity="{0.8 if on else 1}"/>')
    return out


def feed_01():
    visual = ""
    panels = [("ONE BLOCK", 1, "100%", "1/N", True),
              ("N/5 BLOCKS", 2, "100%", "0.20", True),
              ("N BLOCKS", 10, "100%", "1.00", False)]
    x = 72
    for name, lit, util, act, focal in panels:
        visual += box(x, 470, 296, 640, fill="#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8, sw=1.4 if focal else 1)
        visual += label(x + 22, 512, name, fill=ACCENT if focal else INK, size=13)
        visual += sm_grid(x + 22, 540, 10, 9, lit, cell=24, gap=4)
        visual += mono(x + 22, 848, "nvidia-smi", size=15, fill=SOFT, anchor="start")
        visual += txt(x + 274, 900, util, size=54, family=SERIF,
                      fill=ACCENT if focal else INK, anchor="end")
        visual += mono(x + 22, 972, "SM Activity", size=15, fill=SOFT, anchor="start")
        visual += txt(x + 274, 1024, act, size=54, family=SERIF, fill=INK, anchor="end")
        visual += mono(x + 148, 1080, "disagree" if focal else "agree", size=14,
                       fill=ACCENT if focal else SOFT, weight="600")
        x += 320
    emit("feed", 1, "a-clock-not-a-gauge",
         ["100% is a clock,", "not a gauge."],
         ["nvidia-smi counts the time some kernel was running.",
          "It never asks how much of the GPU that kernel used."],
         visual,
         ["One spinning thread reads 100%. So does",
          "a full chip. The number cannot tell them apart."],
         total=6)


def feed_02():
    visual = ""
    visual += label(72, 480, "the same step, two clocks  ·  model inputs, not a measurement")
    visual += box(72, 505, 936, 560, fill="#ffffff", stroke=INK, rx=8)
    visual += label(560, 560, "host timer", fill=INK, anchor="end", size=13)
    visual += label(900, 560, "cuda events", fill=ACCENT, anchor="end", size=13)
    rows = [("forward", "0.8 ms", "4.0 ms", False), ("backward", "1.6 ms", "8.0 ms", False),
            ("loss.item()", "9.6 ms", "0.0 ms", True), ("optimizer", "20.0 ms", "20.0 ms", False)]
    y = 640
    for name, host, ev, focal in rows:
        if focal:
            visual += (f'<rect x="88" y="{y - 42}" width="904" height="64" rx="6" '
                       f'fill="{ACCENT_TINT}" stroke="{ACCENT}" stroke-width="1"/>')
        visual += mono(112, y, name, size=24, fill=ACCENT if focal else INK, anchor="start",
                       weight="600")
        visual += mono(560, y, host, size=24, fill=ACCENT if focal else INK, anchor="end")
        visual += mono(900, y, ev, size=24, fill=ACCENT, anchor="end")
        y += 88
    visual += f'<line x1="104" y1="{y - 50}" x2="976" y2="{y - 50}" stroke="{RULE}"/>'
    visual += mono(112, y, "whole step", size=24, fill=INK, anchor="start", weight="600")
    visual += mono(560, y, "32.0 ms", size=24, fill=INK, anchor="end", weight="600")
    visual += mono(900, y, "32.0 ms", size=24, fill=ACCENT, anchor="end", weight="600")
    visual += mono(540, 1110, "same total, a different bill", size=18, fill=ACCENT, weight="600")
    emit("feed", 2, "two-clocks",
         ["One step,", "two clocks."],
         ["A host timer measures when each Python line returned.",
          "CUDA events measure when the GPU got there."],
         visual,
         ["The timer billed 9.6 ms to the one",
          "line that did no work at all."],
         total=6)


def feed_03():
    visual = ""
    visual += label(72, 480, "each max( ) is host issue time vs gpu time  ·  model inputs")
    for y, focal, tag, name, f1, f2 in [
            (505, True, "one max per segment", "with loss.item() mid-step",
             "max(2.4, 12.0) + max(20.0, 3.0)", "= 12.0 + 20.0 = 32.0 ms"),
            (785, False, "one max for the whole step", "without it",
             "max(2.4 + 20.0, 12.0 + 3.0)", "= max(22.4, 15.0) = 22.4 ms")]:
        visual += box(72, y, 936, 250, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8,
                      sw=1.2 if focal else 1)
        visual += label(104, y + 40, tag, fill=ACCENT if focal else SOFT, size=13)
        visual += txt(104, y + 82, name, size=24, weight="600", anchor="start",
                      fill=ACCENT if focal else INK)
        visual += mono(104, y + 150, f1, size=28, fill=INK, anchor="start")
        visual += mono(104, y + 204, f2, size=28, fill=ACCENT if focal else INK,
                       anchor="start", weight="600")
    visual += mono(540, 1105, "the sum of the maxes never beats the max of the sums",
                   size=18, fill=ACCENT, weight="600")
    emit("feed", 3, "a-sync-point-costs-overlap",
         ["A sync point costs", "the overlap."],
         ["loss.item() does no work. It stops the host",
          "issuing while the GPU is still running."],
         visual,
         ["One logging line: 9.6 ms of a 32.0 ms step,",
          "gone the moment the value stays on the GPU."],
         total=6)


def feed_04():
    visual = ""
    visual += label(72, 480, "one short kernel, 20,000 launches, nvidia's v100 test")
    rows = [("sync after every launch", 9.6), ("launches overlap execution", 3.8),
            ("one cuda graph per step", 3.4)]
    x0, scale = 120, 80.0
    y = 540
    for name, v in rows:
        focal = v == 9.6
        visual += mono(x0, y, name, size=17, fill=INK, anchor="start", weight="600")
        visual += (f'<rect x="{x0}" y="{y + 18}" width="{2.9 * scale}" height="56" '
                   f'fill="{INK}" fill-opacity="0.78"/>')
        visual += (f'<rect x="{x0 + 2.9 * scale}" y="{y + 18}" width="{(v - 2.9) * scale}" '
                   f'height="56" fill="{ACCENT}" fill-opacity="0.85"/>')
        visual += mono(x0 + v * scale + 16, y + 56, f"{v:.1f} µs", size=24,
                       fill=ACCENT if focal else INK, anchor="start", weight="600")
        y += 170
    visual += mono(x0, y - 20, "dark: the 2.9 µs kernel   ·   orange: overhead", size=15,
                   fill=SOFT, anchor="start")
    visual += mono(540, 1105, "Tesla V100, CUDA 10.1, measured by NVIDIA", size=16, fill=MUTED)
    emit("feed", 4, "what-a-launch-costs",
         ["A launch costs", "microseconds."],
         ["Cheap in absolute terms. Expensive next to a",
          "kernel that only runs for a few of them."],
         visual,
         ["A launch hides only behind a kernel",
          "that runs longer than the launch takes."],
         total=6)


def feed_05():
    visual = ""
    visual += card(72, 470, 936, 200, "removed",
                   ["per-kernel host launch cost:",
                    "Python, C++ and driver dispatch"], focal=True, tag="one launch replaces many")
    visual += card(72, 690, 936, 220, "survives",
                   ["every kernel's execution time",
                    "CPU work outside the graph",
                    "sync points, which capture forbids"], tag="what a graph cannot touch")
    visual += card(72, 930, 936, 200, "added",
                   ["capture and instantiation, once",
                    "static shapes, a private memory pool"], tag="what it costs")
    emit("feed", 5, "what-graphs-cannot-remove",
         ["What a CUDA graph", "cannot remove."],
         ["A graph replays a captured step with one launch.",
          "It does nothing about the work inside it."],
         visual,
         ["A graph shortens the host lane.",
          "It cannot shorten the GPU lane."],
         total=6)


def feed_06():
    visual = ""
    visual += label(72, 480, "the worked example, fixed twice  ·  model inputs")
    rows = [("as written", "loss.item() mid-step", "32.0 ms", "47%", False),
            ("fix 1", "log outside the step", "22.4 ms", "67%", False),
            ("fix 2", "optimizer as 10 launches", "15.0 ms", "100%", True)]
    y = 510
    for name, sub, t, u, focal in rows:
        visual += box(72, y, 936, 150, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8, sw=1.4 if focal else 1)
        visual += txt(104, y + 62, name, size=26, weight="600", anchor="start",
                      fill=ACCENT if focal else INK)
        visual += mono(104, y + 104, sub, size=16, fill=MUTED, anchor="start")
        visual += txt(760, y + 90, t, size=46, family=SERIF, anchor="end",
                      fill=ACCENT if focal else INK)
        visual += mono(976, y + 88, f"util {u}", size=18, fill=ACCENT if focal else MUTED,
                       anchor="end", weight="600")
        y += 176
    visual += mono(540, 1080, "utilization by nvidia-smi's definition", size=15, fill=SOFT)
    emit("feed", 6, "read-the-article",
         ["32.0, 22.4,", "15.0 ms."],
         ["Drop the mid-step sync, then cut the optimizer's",
          "launches. Nothing about the kernels changed."],
         visual,
         ["The last one reads 100%: the point where",
          "the number stops telling you anything."],
         total=6, cta="READ IT AT CANERY.IN/BLOGS/GPU-IDLE-AT-100-PERCENT-UTILIZATION")


def story_01():
    visual = ""
    visual += box(72, 745, 936, 160, fill="#ffffff", stroke=INK, rx=8)
    visual += mono(110, 812, "utilization.gpu", size=22, fill=SOFT, anchor="start")
    visual += txt(970, 868, "100%", size=104, family=SERIF, fill=ACCENT, anchor="end")
    rows, cols, cell, gap = 8, 16, 46, 10
    x0 = 540 - (cols * (cell + gap) - gap) / 2
    for r in range(rows):
        for c in range(cols):
            lit = (r, c) == (0, 0)
            visual += (f'<rect x="{x0 + c * (cell + gap):.1f}" y="{945 + r * (cell + gap)}" '
                       f'width="{cell}" height="{cell}" rx="5" '
                       f'fill="{ACCENT if lit else "#e6e6e6"}"/>')
    visual += mono(540, 1430, "one kernel resident  ·  one SM busy", size=21, fill=MUTED)
    emit("story", 1, "one-thread",
         ["100% busy.", "One thread."],
         ["The utilization number counts time,",
          "not how much of the chip is working."],
         visual,
         ["By NVIDIA's own definition,", "this reads 100%."],
         total=4)


def story_02():
    visual = ""
    visual += label(72, 760, "loss.item() in the middle of a step  ·  model inputs")
    visual += card(72, 800, 936, 250, "host timer: 9.6 ms",
                   ["the Python line took this long", "to return"], focal=True,
                   tag="what the timer said")
    visual += card(72, 1090, 936, 250, "CUDA events: 0.0 ms",
                   ["no kernel ran in that time;", "the host was waiting in line"],
                   tag="what the gpu did")
    visual += mono(540, 1420, "12.0 ms of queued GPU work, less the 2.4 spent issuing it",
                   size=19, fill=ACCENT, weight="600")
    emit("story", 2, "the-line-that-waited",
         ["The line that", "only waited."],
         ["A sync point in the middle of a training",
          "step, timed on two clocks."],
         visual,
         ["It did no work. It made the host", "stop issuing while the GPU ran."],
         total=4)


def story_03():
    visual = ""
    visual += label(72, 760, "the order the fixes go in")
    rows = [("1", "remove the mid-step sync", "32.0 → 22.4 ms", False),
            ("2", "fewer, larger launches", "22.4 → 15.0 ms", True),
            ("3", "graph what is left", "one launch per step", False)]
    y = 800
    for n, what, gain, focal in rows:
        visual += box(72, y, 936, 170, fill=ACCENT_TINT if focal else "#ffffff",
                      stroke=ACCENT if focal else "rgba(45,49,66,0.28)", rx=8, sw=1.4 if focal else 1)
        visual += txt(112, y + 104, n, size=64, family=SERIF, anchor="start",
                      fill=ACCENT if focal else INK)
        visual += txt(190, y + 76, what, size=28, weight="600", anchor="start")
        visual += mono(190, y + 122, gain, size=20, fill=ACCENT if focal else MUTED, anchor="start")
        y += 196
    emit("story", 3, "the-order-of-fixes",
         ["Syncs, launches,", "then graphs."],
         ["The order matters: CUDA graphs forbid",
          "sync points, so the first fix is not optional."],
         visual,
         ["Fix the host lane before", "reaching for a graph."],
         total=4)


def story_04():
    visual = ""
    visual += label(72, 760, "a dozen lines, in the article")
    visual += box(72, 800, 936, 330, fill="#ffffff", stroke=INK, rx=8)
    code = ["ev = torch.cuda.Event(enable_timing=True)",
            "ev.record()          # returns at once",
            "t = time.perf_counter()",
            "...",
            "torch.cuda.synchronize()   # once, at the end"]
    y = 866
    for line in code:
        visual += mono(104, y, line, size=21, fill=INK, anchor="start")
        y += 54
    visual += box(72, 1165, 936, 290, fill=ACCENT_TINT, stroke=ACCENT, rx=8, sw=1.2)
    visual += label(104, 1210, "read the two together", fill=ACCENT, size=13)
    for i, (cond, verdict) in enumerate([("events far above host", "GPU-bound"),
                                         ("the two agree", "host-bound"),
                                         ("events near zero", "a sync point")]):
        yy = 1280 + i * 62
        visual += mono(104, yy, cond, size=24, fill=INK, anchor="start")
        visual += mono(976, yy, verdict, size=24, fill=ACCENT, anchor="end", weight="600")
    emit("story", 4, "read-the-article",
         ["Time it on", "two clocks."],
         ["A host timer and CUDA events, side by side,",
          "and one synchronize at the very end."],
         visual,
         ["The full article is on Canery."],
         total=4, cta="LINK IN THE STICKER ABOVE")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06,
            story_01, story_02, story_03, story_04]


if __name__ == "__main__":
    requested = set(sys.argv[1:])
    for builder in BUILDERS:
        name = builder.__name__.replace("_", "-")
        if not requested or name in requested:
            builder()
