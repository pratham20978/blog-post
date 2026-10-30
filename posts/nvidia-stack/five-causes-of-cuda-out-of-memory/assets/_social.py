#!/usr/bin/env python3
"""Build the finished Canery feed sources for "Five Causes of One “CUDA Out of Memory”".

The NVIDIA Stack, part 4. The shell (lockup reading "canery.in", rule, serif title, deck, takeaway, footer)
is the newest one in the repository (Statistics for Data Scientists, part 5), so every series renders as
one publication. Every number on a card comes from the lab's capture, ../lab/captures.json, and the
asserts below hold each one to the article. Colours follow the figures: tangerine marks each card's
deciding number and free memory, blue the fixed run or another process. Feed cards only: the owner asked
for no Story frames (2026-10-30); the shell keeps its Story layout for parts that want one.

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
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))

VW = 1080
PAPER = "#f5f5f5"
INK = "#2d3142"
MUTED = "#4f5d75"
SOFT = "#7a8399"
RULE = "rgba(45,49,66,0.14)"
RULE_SOLID = "#bfc0c0"
ACCENT = "#eb6c36"
ACCENT_TINT = "rgba(235,108,54,0.08)"
LINK = "#2e5aa8"                            # the figures' blue, so cards and figures match
SANS = "'Geist',system-ui,sans-serif"
SERIF = "'Instrument Serif',Georgia,serif"
MONO = "'Geist Mono',ui-monospace,monospace"
FONTS = ("https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1"
         "&family=Geist:wght@400;500;600&family=Geist+Mono:wght@400;500;600&display=swap")
CANONICAL = "canery.in/blogs/five-causes-of-cuda-out-of-memory"
FOOTER = "FIVE CAUSES OF ONE CUDA OOM · CANERY.IN"

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


def rect(x, y, w, h, fill, stroke="none", sw=0, op=None, dash=None):
    o = f' fill-opacity="{op}"' if op is not None else ""
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{o} stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=INK, sw=2, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{sw}"{dd}/>'


def hline(x1, x2, y, stroke=RULE, sw=1, dash=None):
    return line(x1, y, x2, y, stroke, sw, dash)


def polyline(pts, stroke, sw=3, dash=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}/>')


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


# ------------------------------------------------------------------ the numbers
sys.path.insert(0, str(HERE.parent / "lab"))
import diagnose  # noqa: E402  the lab's own parser, so the cards read the messages the way the tool does

GiB, MiB = 2**30, 2**20
R = CAP["runs"]
FAILS = ("fragmentation", "capacity", "retained", "other-process", "non-pytorch")
MSG = {n: diagnose.parse_message(R[n]["oom"]["message"]) for n in FAILS}
VAL = [t["allocated"] for t in R["retained"]["val_trace"]]
FIX = [t["allocated"] for t in R["retained-fix"]["val_trace"]]
GROWTH = VAL[2] - VAL[1]
ALLOWED = R["baseline"]["ledger_start"]["allowed"]
FRAG = R["fragmentation"]["oom"]
STAGES = [s["non_pytorch"] for s in R["inventory"]["stages"]]
EAGER = [s["non_pytorch"] for s in R["inventory-eager"]["stages"]]
ZOMBIE = R["zombie"]["timeline"]
HOLDER = R["other-process"]["holder"]
(PID, HELD), = MSG["other-process"]["other_processes"].items()
OUTSIDE5 = MSG["non-pytorch"]["this_process"] - MSG["non-pytorch"]["allocated"] - MSG["non-pytorch"]["unallocated"]
g = lambda b, nd=2: f"{b / GiB:.{nd}f}"  # noqa: E731
mb = lambda b: f"{b / MiB:.0f}"  # noqa: E731

assert g(MSG["fragmentation"]["unallocated"]) == "4.63" and mb(MSG["fragmentation"]["requested"]) == "256"
assert g(MSG["fragmentation"]["allocated"]) == "19.00" and FRAG["stats"]["inactive_split.all.current"] == 38
assert FRAG["snapshot"]["free_block_sizes"][str(128 * MiB)] == 37 and FRAG["snapshot"]["largest_free_block"] == 256 * MiB
assert g(MSG["capacity"]["allocated"]) == "23.25" and g(ALLOWED) == "23.67" and g(GROWTH) == "1.55" and GROWTH == 33 * 48 * MiB
assert [g(v) for v in (VAL[0], VAL[-1])] == ["12.00", "22.83"] and len(FIX) == 12 and max(FIX) - min(FIX) <= 1024   # flat: one scalar loss at most
assert g(MSG["retained"]["unallocated"]) == "0.50" and mb(MSG["retained"]["unallocated"]) == "514"
assert (PID, g(HELD)) == (189145, "6.17") and HOLDER["now"]["ppid"] == 1 and HOLDER["now"]["state"] == "S"
assert g(OUTSIDE5) == "4.33" and [round(v / MiB) for v in STAGES] == [173, 242, 336, 344, 892, 892, 504]
assert [round(v / MiB) for v in EAGER] == [943, 1257]
assert [z["state"] for z in ZOMBIE] == ["R", "Z", "Z"] and [z["listed_by_nvml"] for z in ZOMBIE] == [True, True, False]
assert [f"{z['t']:.2f}" for z in ZOMBIE[1:]] == ["0.27", "0.40"] and g(ZOMBIE[2]["memfree_delta"]) == "6.61"
assert R["fragmentation"]["retry_after_empty_cache"]["failed"] and g(R["fragmentation"]["retry_after_empty_cache"]["released"]) == "3.00"
assert R["capacity"]["retry_after_empty_cache"]["failed"] and R["capacity"]["retry_after_empty_cache"]["released"] == 0
FEED_TOTAL = 8


def stat_row(x, y, name, value, colour, note=None, size=56):
    """A labelled statistic: its name in mono on the left, the value large on the right."""
    out = mono(x, y, name, 24, colour, "start", 600)
    out += txt(970, y + 10, value, size, colour, SANS, 600, "end")
    if note:
        out += mono(x, y + 36, note, 19, MUTED)
    return out


# ------------------------------------------------------------------ feed
def feed_01():
    p = MSG["fragmentation"]
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "run 1's message: PyTorch 2.15.0, an emulated 24 GiB card", 21, MUTED, "start", 600)
    v += stat_row(110, 640, "tried to allocate", f"{mb(p['requested'])} MiB", INK, size=48)
    v += stat_row(110, 740, "allocated by PyTorch", f"{g(p['allocated'])} GiB", INK, size=48)
    v += stat_row(110, 840, "reserved, unallocated", f"{g(p['unallocated'])} GiB", ACCENT, "the number that decides: fragmentation", 48)
    v += stat_row(110, 960, "other processes", "none", MUTED, size=40)
    v += mono(110, 1044, "the same first line comes from growth, fragmentation,", 18, SOFT)
    v += mono(110, 1072, "another process, memory outside PyTorch, or capacity", 18, SOFT)
    emit("feed", 1, "one-message-five-causes",
         ["Five causes,", "one OOM message."],
         ["PyTorch prints the same first line for five", "unrelated problems. The numbers differ."],
         v,
         ["Don't stop at the first line: the cause", "is in the numbers after it."],
         FEED_TOTAL)


def feed_02():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "batch doubled: 37 segments of 384 MiB, each a live", 21, MUTED, "start", 600)
    v += mono(110, 584, "256 MiB tensor and a free 128 MiB tail", 21, MUTED, "start", 600)
    sc, rh, gap, per = 0.33, 22, 12, 6
    for k in range(37):
        x, y = 110 + (k % per) * (384 * sc + 14), 620 + (k // per) * (rh + gap)
        v += rect(x, y, 256 * sc, rh, INK, op=0.85)
        v += rect(x + 256 * sc, y, 128 * sc, rh, ACCENT, ACCENT, 1.5, op=0.35)
    v += rect(110, 880, 256 * sc, rh + 6, PAPER, INK, 2.2, dash="6,4")
    v += mono(110 + 256 * sc + 18, 900, "the request: 256 MiB, larger than any tail", 22, INK, "start", 600)
    v += mono(110, 970, f"free in all: {g(FRAG['stats']['inactive_split_bytes.all.current'])} GiB, in 38 pieces", 24, ACCENT, "start", 600)
    v += mono(110, 1044, "fragmentation: free memory that cannot be used because", 18, SOFT)
    v += mono(110, 1072, "it sits beside live tensors, in pieces too small", 18, SOFT)
    emit("feed", 2, "fragmentation",
         ["4.63 GiB free.", "256 MiB refused."],
         ["Doubling the batch left 128 MiB tails", "pinned beside long-lived tensors."],
         v,
         ["Unallocated at least the request means", "fragmentation: try expandable segments."],
         FEED_TOTAL)


def feed_03():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "allocated memory at the start of each evaluation batch", 21, MUTED, "start", 600)
    x0, y0, w, h = 150, 600, 620, 330
    X = lambda k: x0 + k / 11 * w  # noqa: E731
    Y = lambda b: y0 + h - (b / GiB - 10) / 15 * h  # noqa: E731
    v += line(x0, y0 + h, x0 + w, y0 + h, RULE_SOLID, 2) + line(x0, y0, x0, y0 + h, RULE_SOLID, 2)
    for tick in (10, 15, 20, 25):
        v += mono(x0 - 12, Y(tick * GiB) + 7, f"{tick}", 18, SOFT, "end")
    v += line(x0, Y(ALLOWED), x0 + w, Y(ALLOWED), SOFT, 2, "8,6")
    v += mono(x0 + w, Y(ALLOWED) - 10, f"allowed {g(ALLOWED)} GiB", 18, SOFT, "end")
    v += polyline([(X(k), Y(b)) for k, b in enumerate(FIX)], LINK, 4)
    v += polyline([(X(k), Y(b)) for k, b in enumerate(VAL)], ACCENT, 4)
    v += mono(X(7) + 14, Y(VAL[-1]) + 6, "fails", 20, ACCENT, "start", 600)
    v += mono(800, 690, f"+{g(GROWTH)} GiB", 26, ACCENT, "start", 600)
    v += mono(800, 722, "per batch", 20, ACCENT, "start", 600)
    v += mono(800, 772, "33 saved", 20, MUTED, "start")
    v += mono(800, 800, "tensors", 20, MUTED, "start")
    v += mono(800, 828, "× 48 MiB", 20, MUTED, "start")
    v += mono(800, 900, "no_grad:", 20, LINK, "start", 600)
    v += mono(800, 928, "flat", 20, LINK, "start", 600)
    v += mono(x0, 980, "GiB, batches 0 to 11", 18, SOFT)
    v += mono(110, 1044, f"at the failure {mb(MSG['retained']['unallocated'])} MiB was unallocated against a 48 MiB", 18, SOFT)
    v += mono(110, 1072, "request: on its own, that message reads as fragmentation", 18, SOFT)
    emit("feed", 3, "retained-graph",
         ["A leak can look", "like fragmentation."],
         ["An evaluation loop without no_grad kept", "every batch's graph, and its tensors, alive."],
         v,
         ["Check growth first: allocated memory at", "the same point of two iterations."],
         FEED_TOTAL)


def feed_04():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "a child that held 6 GiB exits; its parent never reaps it", 21, MUTED, "start", 600)
    rows = [(f"{ZOMBIE[0]['t']:.2f} s", "running, listed by NVML", INK),
            (f"{ZOMBIE[1]['t']:.2f} s", "a zombie (state Z), still listed", INK),
            (f"{ZOMBIE[2]['t']:.2f} s", f"still a zombie, gone: MemFree +{g(ZOMBIE[2]['memfree_delta'])} GiB", LINK)]
    y = 620
    for t, what, col in rows:
        v += mono(110, y, t, 26, col, "start", 600) + mono(260, y, what, 24, col, "start", 600)
        y += 52
    v += hline(110, 970, 790, RULE_SOLID)
    v += mono(110, 840, "a leftover job whose parent was killed", 21, MUTED, "start", 600)
    v += mono(110, 892, f"parent PID {HOLDER['now']['ppid']} (systemd), state {HOLDER['now']['state']}: alive", 24, ACCENT, "start", 600)
    v += mono(110, 934, f"the message names it: Process {PID} has {g(HELD)} GiB", 24, ACCENT, "start", 600)
    v += mono(110, 1044, "a Unix zombie keeps only its PID, status and usage;", 18, SOFT)
    v += mono(110, 1072, "an orphan is a live process, adopted by init", 18, SOFT)
    emit("feed", 4, "zombie-or-orphan",
         ["The zombie isn't", "holding your GPU."],
         ["A process that exited gives its memory back.", "One that never exited keeps it."],
         v,
         ["Take the PID from the message to ps:", "a parent of 1 means an orphan. Stop it."],
         FEED_TOTAL)


def feed_05():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    v += mono(110, 556, "one process's GPU memory outside PyTorch, on the GB10", 21, MUTED, "start", 600)
    bars = [("CUDA context, lazy", STAGES[0], MUTED), ("context, eager loading", EAGER[0], MUTED),
            ("+ NCCL on one rank", STAGES[4] - STAGES[3], LINK)]
    y = 610
    for name, b, col in bars:
        v += mono(110, y + 20, name, 22, INK, "start", 600)
        w = b / (1000 * MiB) * 380
        v += rect(520, y, w, 30, col, op=0.6)
        v += mono(520 + w + 12, y + 22, f"{mb(b)} MiB", 22, INK, "start", 600)
        y += 62
    v += hline(110, 970, 810, RULE_SOLID)
    v += mono(110, 860, "run 5: a library's 4 GiB pool in the same process", 21, MUTED, "start", 600)
    v += stat_row(110, 930, "this process − PyTorch's reserved", f"{g(OUTSIDE5)} GiB", ACCENT, size=48)
    v += mono(110, 1044, "memory snapshots never see it; cuBLAS workspaces are", 18, SOFT)
    v += mono(110, 1072, "not in it: PyTorch 2.15 takes them from its allocator", 18, SOFT)
    emit("feed", 5, "outside-pytorch",
         ["What PyTorch's", "books can't see."],
         ["The context, NCCL and other libraries' pools", "sit in the process but outside the allocator."],
         v,
         ["This process minus allocated and unallocated", "is the memory outside PyTorch."],
         FEED_TOTAL)


def feed_06():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    fr, ca = R["fragmentation"]["retry_after_empty_cache"], R["capacity"]["retry_after_empty_cache"]
    v += mono(110, 556, "catch the error, call torch.cuda.empty_cache(), retry", 21, MUTED, "start", 600)
    v += stat_row(110, 650, "run 1, fragmentation: released", f"{g(fr['released'])} GiB", INK,
                  "the failed operation's own outputs, freed as it unwound", 48)
    v += mono(110, 740, "then the same optimizer step: failed again", 24, ACCENT, "start", 600)
    v += stat_row(110, 840, "run 2, capacity: released", "0 bytes", INK, size=48)
    v += mono(110, 900, "then the same forward pass: failed again", 24, ACCENT, "start", 600)
    v += mono(110, 1044, "before it raises, the allocator has already freed every", 18, SOFT)
    v += mono(110, 1072, "cached segment that holds no live tensor", 18, SOFT)
    emit("feed", 6, "empty-cache",
         ["empty_cache() can't", "save the crash."],
         ["Everything cached and free at the failure,", "the allocator had already released."],
         v,
         ["It hands cache to other processes; for the", "crashed one, the allocator already tried."],
         FEED_TOTAL)


def feed_07():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("1", "allocated grows per iteration?", f"retained graph · +{g(GROWTH)} GiB a batch", ACCENT),
             ("2", "unallocated ≥ the request?", f"fragmentation · {g(MSG['fragmentation']['unallocated'])} GiB vs 256 MiB", INK),
             ("3", "other processes cover it?", f"another process · {g(HELD)} GiB", INK),
             ("4", "outside PyTorch beyond the context?", f"outside PyTorch · {g(OUTSIDE5)} GiB", INK),
             ("5", "none of these", f"capacity · {g(MSG['capacity']['allocated'])} of {g(ALLOWED)} GiB", INK)]
    y = 566
    for n, q, a, col in items:
        v += txt(110, y + 4, n, 40, col, SERIF, 400)
        v += mono(160, y - 6, q, 23, col, "start", 600)
        v += mono(160, y + 26, a, 21, MUTED)
        y += 104
    emit("feed", 7, "read-in-this-order",
         ["Read the message", "in this order."],
         ["Five questions, each answered by one number;", "the answers are the lab's five runs."],
         v,
         ["Growth first: a leak also leaves slivers", "that read as fragmentation."],
         FEED_TOTAL)


def feed_08():
    v = box(72, 486, 936, 640, "#ffffff", RULE_SOLID)
    items = [("fragmentation", f"{g(MSG['fragmentation']['unallocated'])} GiB free in 38 pieces, none of 256 MiB", ACCENT),
             ("a retained graph", f"+{g(GROWTH)} GiB a batch without no_grad", INK),
             ("another process", f"an orphan's {g(HELD)} GiB, named in the message", INK),
             ("outside PyTorch", f"context {mb(STAGES[0])} MiB lazy, {mb(EAGER[0])} eager; NCCL +{mb(STAGES[4] - STAGES[3])} MiB", INK),
             ("capacity", f"{g(MSG['capacity']['allocated'])} GiB allocated; checkpointing ran the batch", INK)]
    y = 556
    for head, a, colour in items:
        v += txt(110, y, head, 30, colour, SANS, 600)
        v += mono(110, y + 42, a, 21, INK if colour == INK else colour)
        y += 112
    emit("feed", 8, "read-the-article",
         ["Five causes of one", "CUDA out of memory."],
         ["Measured with PyTorch 2.15.0, every message", "real, and a lab that reproduces all five."],
         v,
         ["The decision tree, the allocator's rules,", "and what each fix does."],
         FEED_TOTAL, cta=f"READ IT AT {ascii_upper(CANONICAL)}")


BUILDERS = [feed_01, feed_02, feed_03, feed_04, feed_05, feed_06, feed_07, feed_08]

if __name__ == "__main__":
    wanted = set(sys.argv[1:])
    for b in BUILDERS:
        name = b.__name__.replace("_", "-")
        if not wanted or name in wanted:
            b()
