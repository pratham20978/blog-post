#!/usr/bin/env python3
"""Figures 01-09 for five-causes-of-cuda-out-of-memory.

Every value drawn comes from the lab's capture, ../lab/captures.json, written by lab/oom_lab.py on the
GB10. The asserts below pin each number the article quotes, so a figure cannot drift from the text.
Figures 03 and 04 are laid out by Mermaid: this script writes their .mmd from the same data and
_mermaid.py renders them.
Run:  python3 _figs.py [01 05 ...]
"""
import json
import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE, RULE_SOLID, SANS, SOFT,
                    emit, eyebrow, mono, txt)

HERE = pathlib.Path(__file__).resolve().parent
CAP = json.loads((HERE.parent / "lab" / "captures.json").read_text(encoding="utf-8"))
R = CAP["runs"]
GiB, MiB = 2**30, 2**20
CARD = CAP["card_bytes"]
FAILS = ("fragmentation", "capacity", "retained", "other-process", "non-pytorch")

sys.path.insert(0, str(HERE.parent / "lab"))
import diagnose  # noqa: E402  the lab's own parser, so the figures read the messages the way the tool does

MSG = {n: diagnose.parse_message(R[n]["oom"]["message"]) for n in FAILS}
VERDICT = {n: diagnose.diagnose(MSG[n], card=CARD, growth=diagnose.growth_from_trace(
    R[n].get("val_trace") or R[n].get("trace") or [])) for n in FAILS}


def g(b, nd=2):
    return f"{b / GiB:.{nd}f}"


def m(b, nd=0):
    return f"{b / MiB:.{nd}f}"


VAL = [t["allocated"] for t in R["retained"]["val_trace"]]
GROWTH = VAL[2] - VAL[1]
ALLOWED = R["baseline"]["ledger_start"]["allowed"]
BASE_PEAK = max(max(t["peaks"].values()) for t in R["baseline"]["trace"])
FRAG_SNAP = R["fragmentation"]["oom"]["snapshot"]
STAGES = {s["stage"]: s["non_pytorch"] for s in R["inventory"]["stages"]}
EAGER = {s["stage"]: s["non_pytorch"] for s in R["inventory-eager"]["stages"]}
LOOKS = R["unified"]["looks"]
GRAPHICS = R["unified"]["graphics_processes"]

# The numbers the article prints, held to the capture.
assert g(CARD) == "24.00" and g(ALLOWED) == "23.67" and g(BASE_PEAK) == "20.00"
assert [g(MSG[n]["unallocated"]) for n in FAILS] == ["4.63", "0.25", "0.50", "0.00", "0.00"]
assert [g(MSG[n]["allocated"]) for n in FAILS] == ["19.00", "23.25", "23.16", "17.50", "19.50"]
assert [m(MSG[n]["requested"]) for n in FAILS] == ["256", "384", "48", "256", "256"]
assert [VERDICT[n]["cause"] for n in FAILS] == ["fragmentation", "capacity", "retained graph", "other process",
                                                "non-PyTorch"]
assert g(GROWTH) == "1.55" and GROWTH == 33 * 48 * MiB
assert g(sum(MSG["other-process"]["other_processes"].values())) == "6.17"
assert g(VERDICT["non-pytorch"]["numbers"]["non_pytorch_in_this_process"]) == "4.33"
FRAG_STATS = R["fragmentation"]["oom"]["stats"]
assert FRAG_SNAP["free_block_sizes"][str(128 * MiB)] == 37 and FRAG_STATS["inactive_split.all.current"] == 38
assert g(FRAG_STATS["inactive_split_bytes.all.current"]) == "4.63"   # 37 tails of 128 MiB and one small block
assert [g(v) for v in VAL] == ["12.00", "13.55", "15.09", "16.64", "18.19", "19.73", "21.28", "22.83"]
assert [round(STAGES[k] / MiB) for k in STAGES] == [173, 242, 336, 344, 892, 892, 504]
assert [round(v / MiB) for v in EAGER.values()] == [943, 1257]
assert [g(LOOKS[0][k]) for k in ("cuda_free", "MemFree", "MemAvailable", "Cached")] == ["104.25", "104.25", "114.45",
                                                                                         "9.18"]
assert g(LOOKS[0]["cuda_free"] - LOOKS[1]["cuda_free"]) == "8.02"
assert round(sum(p["used"] for p in GRAPHICS.values()) / MiB) == 792


# ------------------------------------------------------------------ drawing helpers (Statistics Part 5's set)
def rect(x, y, w, h, fill="#ffffff", stroke="rgba(45,49,66,0.30)", sw=0.8, dash=None, rx=0, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{rx}" '
            f'fill="{fill}"{o} stroke="{stroke}" stroke-width="{sw}"{dd}/>')


def line(x1, y1, x2, y2, stroke=MUTED, sw=1.0, dash=None, marker=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    mk = f' marker-end="url(#{marker})"' if marker else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" '
            f'stroke-width="{sw}"{dd}{mk}{o}/>')


def polyline(pts, stroke, sw=1.6, dash=None, op=None):
    dd = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{op}"' if op is not None else ""
    return (f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" '
            f'fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round"{dd}{o}/>')


def dot(x, y, rr=3.4, fill=INK, stroke=None, op=None):
    s = f' stroke="{stroke}" stroke-width="1.2"' if stroke else ""
    o = f' fill-opacity="{op}"' if op is not None else ""
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rr}" fill="{fill}"{o}{s}/>'


def note_lines(x, y, items, size=8.5, gap=15, anchor="start"):
    out = ""
    for k, (t, c) in enumerate(items):
        if t:
            out += mono(x, y + k * gap, t, size=size, fill=c, anchor=anchor,
                        weight="600" if c in (INK, LINK, ACCENT) else "400")
    return out


def title(x, y, s, fill=INK, anchor="start", size=9.5):
    """A panel title in mono, not uppercased, so units and names keep their case."""
    return mono(x, y, s, size=size, fill=fill, anchor=anchor, weight="600")


class Axes:
    def __init__(self, x0, y0, w, h, xr, yr):
        self.x0, self.y0, self.w, self.h, self.xr, self.yr = x0, y0, w, h, xr, yr

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def frame(self, xt, yt, xlab=None, xfmt=str, yfmt=str):
        s = ""
        for v in yt:
            yy = self.Y(v)
            s += line(self.x0, yy, self.x0 + self.w, yy, stroke=RULE, sw=0.8)
            s += mono(self.x0 - 8, yy + 3, yfmt(v), size=8, fill=SOFT, anchor="end")
        for v in xt:
            s += mono(self.X(v), self.y0 + self.h + 15, xfmt(v), size=8, fill=SOFT)
        s += line(self.x0, self.y0 + self.h, self.x0 + self.w, self.y0 + self.h, stroke=RULE_SOLID)
        s += line(self.x0, self.y0, self.x0, self.y0 + self.h, stroke=RULE_SOLID)
        if xlab:
            s += mono(self.x0 + self.w, self.y0 + self.h + 32, xlab, size=8.5, fill=SOFT, anchor="end")
        return s


def legend(y, vw, items, x=108):
    """Legend whose swatches are drawn exactly like this post's marks."""
    s = f'<line x1="32" y1="{y - 8}" x2="{vw - 32}" y2="{y - 8}" stroke="{RULE}" stroke-width="0.8"/>'
    s += eyebrow(32, y + 8, "legend", fill=SOFT)
    for label, kind in items:
        part = kind.split(":")
        if part[0] == "fill":
            s += rect(x, y - 1, 16, 12, fill=part[1], op=float(part[2]), stroke=part[3] if len(part) > 3 else "none",
                      sw=0.8 if len(part) > 3 else 0, dash=part[4] if len(part) > 4 else None)
        elif part[0] == "line":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=float(part[2]) if len(part) > 2 else 2.0)
        elif part[0] == "dash":
            s += line(x, y + 5, x + 18, y + 5, stroke=part[1], sw=1.4, dash="5,3")
        elif part[0] == "dot":
            s += dot(x + 8, y + 5, float(part[2]), fill=part[1])
        elif part[0] == "ring":
            s += dot(x + 8, y + 5, float(part[2]) if len(part) > 2 else 3.4, fill=PAPER, stroke=part[1])
        elif part[0] == "outline":
            s += rect(x, y - 1, 16, 12, fill=PAPER, stroke=part[1], sw=1.4, dash=part[2] if len(part) > 2 else None)
        s += mono(x + 24, y + 9, label, size=8, fill=MUTED, anchor="start")
        x += 24 + 5.4 * len(label) + 26
    return s


# Colours with one meaning each, in every figure of this post.
C_ALLOC = INK          # allocated by PyTorch
C_FREE_IN = ACCENT     # reserved by PyTorch but unallocated
C_OUTSIDE = MUTED      # this process, outside PyTorch's allocator
C_OTHER = LINK         # other processes


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 556
    p = MSG["fragmentation"]
    lines = [
        ("CUDA out of memory. Tried to allocate 256.00 MiB.", "1"),
        ("GPU 0 has a total capacity of 121.63 GiB of which 79.59 GiB is free.", "2"),
        ("Including non-PyTorch memory, this process has 23.96 GiB memory in use.", "4"),
        ("23.67 GiB allowed;", "5"),
        ("Of the allocated memory 19.00 GiB is allocated by PyTorch,", "6"),
        ("and 4.63 GiB is reserved by PyTorch but unallocated.", "6"),
    ]
    # Every number on the block is the run's own, read back from the message itself.
    msg = R["fragmentation"]["oom"]["message"]
    for text, _ in lines:
        assert text.rstrip(",") in msg or text in msg, text
    assert (diagnose.fmt(p["requested"]), diagnose.fmt(p["unallocated"])) == ("256.00 MiB", "4.63 GiB")
    s = eyebrow(32, 40, "the fragmentation run's message, one sentence per line, as PyTorch 2.15.0 printed it")
    x0, y0, bw, lh = 32, 64, 548, 30
    s += rect(x0, y0, bw, 30 + lh * len(lines), fill="#ffffff", stroke=RULE_SOLID, rx=6)
    for k, (text, badge) in enumerate(lines):
        yy = y0 + 30 + k * lh
        s += mono(x0 + 46, yy, text, size=9.6, fill=INK, anchor="start")
        s += dot(x0 + 22, yy - 3.5, 9, fill=PAPER, stroke=ACCENT if badge in ("6",) else MUTED)
        s += mono(x0 + 22, yy, badge, size=9, fill=ACCENT if badge == "6" else MUTED, weight="600")
    by = y0 + 30 + lh * len(lines) + 4
    s += mono(x0 + 46, by + 14, "(3) other processes would appear here as  Process N has X memory in use.",
              size=8.5, fill=SOFT, anchor="start")
    s += mono(x0 + 46, by + 30, "    none did: the card held only this process", size=8.5, fill=SOFT, anchor="start")
    cards = [
        ("1", "the request", "the allocator", "the block or segment it needed,",
         "rounded up: 3 MiB can read 20 MiB", MUTED),
        ("2", "total and free", "cudaMemGetInfo", "the whole device, every process;",
         "on this GB10, the machine's memory", MUTED),
        ("3", "other processes", "NVML, compute list", "one line per other CUDA process;",
         "graphics clients never appear", C_OTHER),
        ("4", "this process", "NVML", "minus PyTorch's reserved =",
         f"memory outside PyTorch: {g(p['this_process'] - p['allocated'] - p['unallocated'])} GiB", C_OUTSIDE),
        ("5", "allowed", "a memory fraction", "only when a fraction caps PyTorch;",
         "here, the emulated 24 GiB card", MUTED),
        ("6", "allocated, unallocated", "the allocator", f"unallocated {diagnose.fmt(p['unallocated'])} ≥ request",
         f"{diagnose.fmt(p['requested'])}: fragmentation", ACCENT),
    ]
    cx, cy0, cw, chh, gap = 612, 64, 372, 64, 12
    for k, (badge, name, inst, l1, l2, col) in enumerate(cards):
        yy = cy0 + k * (chh + gap)
        s += rect(cx, yy, cw, chh, fill=ACCENT_TINT if badge == "6" else "#ffffff",
                  stroke=ACCENT if badge == "6" else RULE_SOLID, rx=6, sw=1.2 if badge == "6" else 0.8)
        s += dot(cx + 20, yy + 20, 9, fill=PAPER, stroke=col)
        s += mono(cx + 20, yy + 23.5, badge, size=9, fill=col, weight="600")
        s += txt(cx + 38, yy + 24, name, size=12, weight="600", anchor="start",
                 fill=ACCENT if badge == "6" else INK)
        verb = "set by" if badge == "5" else "measured by"
        s += mono(cx + cw - 12, yy + 23, f"{verb} {inst}", size=8, fill=SOFT, anchor="end")
        s += mono(cx + 38, yy + 41, l1, size=8.5, fill=MUTED, anchor="start")
        s += mono(cx + 38, yy + 55, l2, size=8.5, fill=MUTED, anchor="start")
    for k, note in enumerate(["Numbers 2 and 5 come from the emulation's host:", "a real 24 GiB card prints its own total and",
                              "free, and no \"allowed\" clause.", "", "Numbers 1, 3, 4 and 6 mean the same on any card."]):
        s += mono(x0 + 46, by + 70 + 15 * k, note, size=8.5, fill=SOFT, anchor="start")
    return emit("01", "message-anatomy", "One message, six numbers, three instruments",
                "The run 1 message with each number tied to what measured it and what it can reveal.",
                "the message", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 504
    s = eyebrow(32, 40, "where the 24 GiB card's bytes were when each run failed, from each message (capture 2026-10-30)")
    ax0, axw, top, rh, gap = 230, 560, 82, 30, 30
    X = lambda b: ax0 + b / CARD * axw  # noqa: E731
    for v in range(0, 24, 4):
        s += line(X(v * GiB), top - 14, X(v * GiB), top + 6 * (rh + gap) - gap + 4, stroke=RULE, sw=0.8)
        s += mono(X(v * GiB), top - 20, f"{v} GiB", size=8, fill=SOFT)
    s += line(X(CARD), top - 14, X(CARD), top + 6 * (rh + gap) - gap + 4, stroke=INK, sw=1.4)
    s += mono(X(CARD), top - 20, f"{g(CARD, 0)} GiB card", size=8, fill=INK, weight="600")
    rows = [("baseline", "fits: peak", None)] + [(n, None, n) for n in FAILS]
    labels = {"baseline": ("0 · baseline", "batch 6,144"), "fragmentation": ("1 · fragmentation", "batch 12,288"),
              "capacity": ("2 · capacity", "12,288, expandable"), "retained": ("3 · retained graph", "eval, no no_grad"),
              "other-process": ("4 · another process", "a 6 GiB orphan"),
              "non-pytorch": ("5 · outside PyTorch", "a 4 GiB library pool")}
    for k, (name, _, run) in enumerate(rows):
        y = top + k * (rh + gap)
        l1, l2 = labels[name]
        s += txt(ax0 - 14, y + 13, l1, size=11.5, weight="600", anchor="end")
        s += mono(ax0 - 14, y + 27, l2, size=8.5, fill=SOFT, anchor="end")
        if run is None:
            outside = R["baseline"]["ledger_start"]["non_pytorch"]
            parts = [(BASE_PEAK, C_ALLOC, 0.85, None), (outside, C_OUTSIDE, 0.55, None)]
            focus = None
        else:
            p = MSG[run]
            others = sum(p["other_processes"].values())
            outside = p["this_process"] - p["allocated"] - p["unallocated"]
            parts = [(p["allocated"], C_ALLOC, 0.85, "alloc"), (p["unallocated"], C_FREE_IN, 0.35, "unalloc"),
                     (outside, C_OUTSIDE, 0.55, "outside"), (others, C_OTHER, 0.55, "other")]
            focus = {"fragmentation": "unalloc", "capacity": "alloc", "retained": "alloc",
                     "other-process": "other", "non-pytorch": "outside"}[run]
        x = ax0
        for b, col, op, key in parts:
            w = b / CARD * axw
            if w > 0.2:
                hit = focus is not None and key == focus
            s += rect(x, y, w, rh, fill=col, op=op, stroke=ACCENT if hit else "none", sw=2.0 if hit else 0)
            x += w
        if run is None:
            s += mono(X(CARD) + 16, y + 13, f"peak {g(BASE_PEAK)} GiB: fits", size=8.5, fill=INK, anchor="start", weight="600")
            s += mono(X(CARD) + 16, y + 27, f"{g(CARD - BASE_PEAK - outside)} GiB to spare", size=8.5, fill=SOFT, anchor="start")
            continue
        req = MSG[run]["requested"]
        s += rect(x, y - 5, max(req / CARD * axw, 2.5), rh + 10, fill=PAPER, stroke=INK, sw=1.4, dash="3,2")
        if run == "fragmentation":
            tag = f"unallocated {g(MSG[run]['unallocated'])} GiB"
        elif run == "capacity":
            tag = f"allocated {g(MSG[run]['allocated'])} GiB"
        elif run == "retained":
            tag = f"+{g(GROWTH)} GiB per batch"
        elif run == "other-process":
            (pid, held), = MSG[run]["other_processes"].items()
            tag = f"PID {pid}: {g(held)} GiB"
        else:
            tag = f"outside PyTorch {g(VERDICT[run]['numbers']['non_pytorch_in_this_process'])} GiB"
        s += mono(X(CARD) + 16, y + 13, tag, size=8.5, fill=ACCENT, anchor="start", weight="600")
        s += mono(X(CARD) + 16, y + 27, f"request {m(req)} MiB", size=8.5, fill=SOFT, anchor="start")
    s += mono(32, vh - 56, "The dashed box after each bar is the request, to scale: on a full card it lands past the edge. "
              "The outlined segment decides the cause.", size=8.5, fill=MUTED, anchor="start")
    s += legend(vh - 24, vw, [("allocated by PyTorch", f"fill:{C_ALLOC}:0.85"),
                              ("reserved, unallocated", f"fill:{C_FREE_IN}:0.35"),
                              ("outside PyTorch", f"fill:{C_OUTSIDE}:0.55"), ("other processes", f"fill:{C_OTHER}:0.55"),
                              ("the request", f"outline:{INK}:3,2")])
    return emit("02", "five-runs-one-card", "The same card, filled five ways",
                "Each failing run's message, drawn on the emulated 24 GiB card: the segment that grew is outlined.",
                "five failures", vw, vh, s)


# ------------------------------------------------------------------ FIG 03 and 04 (Mermaid)
def mmd03():
    fr, ca, op, npt = MSG["fragmentation"], MSG["capacity"], MSG["other-process"], VERDICT["non-pytorch"]
    pid = next(iter(op["other_processes"]))
    return f"""flowchart TD
  S["CUDA out of memory<br/>Tried to allocate R"] --> Q1{{"Does allocated memory grow<br/>between iterations, g > 0?"}}
  Q1 -- "yes" --> C3["retained graph<br/>run 3: +{g(GROWTH)} GiB per batch"]
  Q1 -- "no, or not known" --> Q2{{"Reserved but unallocated<br/>at least the request, U ≥ R?"}}
  Q2 -- "yes" --> C1["fragmentation<br/>run 1: U {g(fr['unallocated'])} GiB, R {m(fr['requested'])} MiB"]
  Q2 -- "no" --> Q3{{"Other processes cover<br/>the shortfall, O + X ≥ D?"}}
  Q3 -- "yes" --> C4["another process<br/>run 4: PID {pid} holds {g(sum(op['other_processes'].values()))} GiB"]
  Q3 -- "no" --> Q4{{"Outside PyTorch beyond the<br/>context covers it, N − 0.5 GiB ≥ D?"}}
  Q4 -- "yes" --> C5["memory outside PyTorch<br/>run 5: N = {g(npt['numbers']['non_pytorch_in_this_process'])} GiB"]
  Q4 -- "no" --> C2["capacity<br/>run 2: A = {g(ca['allocated'])} of {g(ca['allowed'])} GiB allowed"]
  classDef cause fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
  class C1,C2,C3,C4,C5 cause
"""


def mmd04():
    return """flowchart TD
  A["a tensor needs n bytes on CUDA stream s<br/>round n up: at least 512 B · up to 1 MiB → small pool"] --> C{"a free cached block that fits,<br/>in this stream's pool?"}
  C -- "yes: the smallest that fits" --> D["split off the rest if worth keeping<br/>small pool ≥ 512 B · large pool > 1 MiB<br/>the block goes to the tensor: allocated += block"]
  C -- "no" --> F["cudaMalloc a new segment<br/>2 MiB · 20 MiB · n rounded to 2 MiB"]
  F -- "granted: reserved += segment" --> D
  F -- "refused, or over the memory fraction" --> H{"max_split_size_mb set?"}
  H -- "yes" --> I["free just enough large<br/>cached blocks, try again"]
  I -- "granted" --> D
  I -- "refused" --> J
  H -- "no" --> J["synchronize, free every unsplit<br/>cached block, try again<br/>num_alloc_retries += 1"]
  J -- "granted" --> D
  J -- "refused" --> K["raise OutOfMemoryError<br/>U = free space inside split segments"]
  classDef stop fill:#fdf0ea,stroke:#eb6c36,color:#2d3142
  class K stop
"""


def mermaid(num, slug, text):
    stem = f"fig-{num}-{slug}-five-causes-of-cuda-out-of-memory"
    (HERE / f"{stem}.mmd").write_text(text, encoding="utf-8")
    import _mermaid
    _mermaid.render(stem)
    return stem


def fig03():
    return mermaid("03", "decision-tree", mmd03().replace("flowchart TD", "flowchart LR"))


def fig04():
    return mermaid("04", "allocator-path", mmd04())


# ------------------------------------------------------------------ FIG 05
def fig05():
    segs = FRAG_SNAP["segments"]
    split = [sg for sg in segs if sg["total"] == 384 * MiB and sg["largest_free"] == 128 * MiB]
    live256 = [sg for sg in segs if sg["total"] == 256 * MiB and sg["allocated"] == 256 * MiB]
    temps = [sg for sg in segs if sg["total"] == 256 * MiB and sg["allocated"] == 0]
    assert (len(split), len(live256), len(temps)) == (37, 27, 12)
    sc, rh, rg = 0.30, 20, 10                          # px per MiB, row height, row gap
    s = eyebrow(32, 40, "run 1's reserved memory at the failure, every segment to scale (allocator snapshot)")
    # 37 split segments, 6 to a row
    y = 70
    s += title(32, y, f"{len(split)} segments of 384 MiB: a live 256 MiB tensor and a free 128 MiB tail")
    per, cw = 6, 384 * sc + 18
    for k, _ in enumerate(split):
        x, yy = 32 + (k % per) * cw, y + 14 + (k // per) * (rh + rg)
        s += rect(x, yy, 256 * sc, rh, fill=C_ALLOC, op=0.85, stroke="none", sw=0)
        s += rect(x + 256 * sc, yy, 128 * sc, rh, fill=C_FREE_IN, op=0.35, stroke=ACCENT, sw=1.0)
    y = y + 14 + 7 * (rh + rg) + 18
    s += title(32, y, f"{len(live256)} live segments of 256 MiB: 16 weights, 11 gradients and Adam states")
    per, cw = 9, 256 * sc + 10
    for k, _ in enumerate(live256):
        x, yy = 32 + (k % per) * cw, y + 14 + (k // per) * (rh + rg)
        s += rect(x, yy, 256 * sc, rh, fill=C_ALLOC, op=0.85, stroke="none", sw=0)
    y = y + 14 + 3 * (rh + rg) + 18
    s += title(32, y, f"{len(temps)} segments of the optimizer's temporaries: live at the failure, freed as the error unwound")
    for k, _ in enumerate(temps):
        x, yy = 32 + (k % per) * cw, y + 14 + (k // per) * (rh + rg)
        s += rect(x, yy, 256 * sc, rh, fill=C_ALLOC, op=0.35, stroke=INK, sw=0.8, dash="3,2")
    bottom = y + 14 + 2 * (rh + rg)
    # the request, in its own column, to the same scale
    rx, ry = 836, 84
    s += title(rx, 70, "the request")
    s += rect(rx, ry, 256 * sc, rh, fill=PAPER, stroke=INK, sw=1.2, dash="3,2")
    s += mono(rx + 256 * sc + 8, ry + 14, "256 MiB", size=9, fill=INK, anchor="start", weight="600")
    s += rect(rx, ry + rh + 12, 128 * sc, rh, fill=C_FREE_IN, op=0.35, stroke=ACCENT, sw=1.0)
    s += mono(rx + 128 * sc + 8, ry + rh + 26, "largest free: 128 MiB", size=8.5, fill=ACCENT, anchor="start", weight="600")
    rows = [(f"free in all: {g(FRAG_STATS['inactive_split_bytes.all.current'])} GiB", INK),
            (f"in {FRAG_STATS['inactive_split.all.current']} pieces,", MUTED), (f"{len(split)} of them 128 MiB tails", MUTED),
            ("", INK), ("no free piece holds", MUTED), ("256 MiB: out of memory", ACCENT)]
    s += note_lines(rx, ry + 2 * (rh + 12) + 26, rows, gap=15)
    total = sum(sg["total"] for sg in segs)
    vh = bottom + 76
    s += mono(32, vh - 50, f"Reserved {g(total)} GiB in {len(segs)} segments (one 2 MiB small-pool segment not drawn). "
              "A tail never merges across its live head or into another segment.", size=8.5, fill=MUTED, anchor="start")
    s += legend(vh - 24, 1016, [("allocated (live)", f"fill:{C_ALLOC}:0.85"), ("free tail", f"fill:{C_FREE_IN}:0.35:{ACCENT}"),
                                ("temporary, live at the failure", f"fill:{C_ALLOC}:0.35:{INK}:3,2"),
                                ("the request", f"outline:{INK}:3,2")])
    return emit("05", "slivers", "4.63 GiB free, and nowhere to put 256 MiB",
                "Run 1's allocator snapshot: the free memory is 37 tails, each pinned beside a live tensor.",
                "fragmentation", 1016, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 440
    s = eyebrow(32, 40, "why expandable segments let free space merge: addresses on top, physical memory below")
    live_w, free_w = 120, 60                           # 256 MiB and 128 MiB, in proportion
    # Panel A: three separate cudaMalloc segments, with gaps between their address ranges
    s += title(32, 72, "default: one cudaMalloc per segment, each its own address range")
    ya = 88
    for k in range(3):
        x = 32 + k * (live_w + free_w + 44)
        s += rect(x, ya, live_w + free_w, 44, fill="#ffffff", stroke=INK, sw=1.0, rx=3)
        s += rect(x, ya, live_w, 44, fill=C_ALLOC, op=0.85, stroke="none", sw=0)
        s += txt(x + live_w / 2, ya + 26, "live 256 MiB", size=10, fill=PAPER, weight="600")
        s += rect(x + live_w, ya, free_w, 44, fill=C_FREE_IN, op=0.35, stroke=ACCENT, sw=1.0)
        s += mono(x + live_w + free_w / 2, ya + 26, "free 128", size=8.5, fill=ACCENT, weight="600")
        if k < 2:
            s += mono(x + live_w + free_w + 22, ya + 26, "· · ·", size=9, fill=SOFT)
    xr = 32 + 3 * (live_w + free_w + 44)
    s += rect(xr, ya + 6, 120, 32, fill=PAPER, stroke=INK, sw=1.2, dash="3,2")
    s += mono(xr + 60, ya + 26, "request 256 MiB", size=8.5, fill=INK, weight="600")
    s += mono(32, ya + 66, "3 × 128 MiB free, in three tails that can never join: the 256 MiB request fits in none",
              size=8.5, fill=ACCENT, anchor="start", weight="600")
    # Panel B: one expandable segment
    s += title(32, 196, "expandable_segments:True: one reserved range per stream and pool")
    xb, yb, wb = 32, 230, 952
    s += rect(xb, yb, wb, 44, fill=PAPER, stroke=SOFT, sw=1.0, dash="4,3", rx=3)
    s += mono(xb + wb, yb - 8, "cuMemAddressReserve: 1⅛ × device memory of addresses, no memory behind them",
              size=8.5, fill=SOFT, anchor="end")
    x = xb
    for _ in range(3):
        s += rect(x, yb, live_w, 44, fill=C_ALLOC, op=0.85, stroke=PAPER, sw=1.0)
        s += txt(x + live_w / 2, yb + 26, "live 256 MiB", size=10, fill=PAPER, weight="600")
        x += live_w
    s += rect(x, yb, 3 * free_w, 44, fill=C_FREE_IN, op=0.35, stroke=ACCENT, sw=1.0)
    s += mono(x + 1.5 * free_w, yb + 20, "384 MiB free, one block:", size=8.5, fill=ACCENT, weight="600")
    s += mono(x + 1.5 * free_w, yb + 34, "the 256 MiB request fits", size=8.5, fill=ACCENT, weight="600")
    s += mono(x + 3 * free_w + 16, yb + 26, "unmapped addresses: the range grows here", size=8.5, fill=MUTED, anchor="start")
    py, pw = yb + 76, 20
    s += mono(xb, py - 10, "cuMemCreate: physical pages of 20 MiB (2 MiB in the small pool), cuMemMap'd under the range",
              size=8.5, fill=MUTED, anchor="start")
    npages = int((3 * live_w + 3 * free_w) / pw)
    for k in range(npages):
        s += rect(xb + k * pw + 1, py, pw - 2, 16, fill="#ffffff", stroke=MUTED, sw=0.8, rx=2)
    s += mono(xb, py + 40, "On out-of-memory the allocator can unmap whole free pages and map them again at the end of the range,",
              size=8.5, fill=MUTED, anchor="start")
    s += mono(xb, py + 55, "where the next request needs them. Free space still cannot merge across a live block.",
              size=8.5, fill=MUTED, anchor="start")
    s += mono(xb, py + 80, "Blocks in proportion, pages not. Off by default and documented as experimental in PyTorch 2.15.0.",
              size=8.5, fill=SOFT, anchor="start")
    s += legend(vh - 24, vw, [("allocated (live)", f"fill:{C_ALLOC}:0.85"), ("free", f"fill:{C_FREE_IN}:0.35:{ACCENT}"),
                              ("reserved addresses", f"outline:{SOFT}:4,3"), ("physical page", f"outline:{MUTED}"),
                              ("the request", f"outline:{INK}:3,2")])
    return emit("06", "expandable-segments", "Separate segments trap their tails; one growing range does not",
                "The default allocator against expandable segments, which reserve addresses and map memory as needed.",
                "expandable segments", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 470
    fix = [t["allocated"] for t in R["retained-fix"]["val_trace"]]
    s = eyebrow(32, 40, "allocated memory at the start of each evaluation batch of 1,536 rows, after two training steps")
    ax = Axes(96, 76, 600, 300, (0, 11), (10, 25))
    s += ax.frame(list(range(12)), [10, 13, 16, 19, 22, 25], xlab="evaluation batch", xfmt=str, yfmt=lambda v: f"{v} GiB")
    s += line(ax.x0, ax.Y(ALLOWED / GiB), ax.x0 + ax.w, ax.Y(ALLOWED / GiB), stroke=SOFT, sw=1.0, dash="4,3")
    s += mono(ax.x0 + ax.w - 4, ax.Y(ALLOWED / GiB) - 6, f"allowed {g(ALLOWED)} GiB", size=8.5, fill=SOFT, anchor="end")
    s += polyline([(ax.X(k), ax.Y(v / GiB)) for k, v in enumerate(fix)], LINK, sw=1.9)
    for k, v in enumerate(fix):
        s += dot(ax.X(k), ax.Y(v / GiB), 3.0, fill=LINK)
    s += polyline([(ax.X(k), ax.Y(v / GiB)) for k, v in enumerate(VAL)], ACCENT, sw=1.9)
    for k, v in enumerate(VAL[:-1]):
        s += dot(ax.X(k), ax.Y(v / GiB), 3.0, fill=ACCENT)
    kx, ky = ax.X(len(VAL) - 1), ax.Y(VAL[-1] / GiB)
    s += line(kx - 5, ky - 5, kx + 5, ky + 5, stroke=ACCENT, sw=2.2) + line(kx - 5, ky + 5, kx + 5, ky - 5, stroke=ACCENT, sw=2.2)
    s += mono(kx + 10, ky + 4, "fails asking for 48 MiB", size=8.5, fill=ACCENT, anchor="start", weight="600")
    s += mono(ax.X(3.2), ax.Y(17.6), f"+{g(GROWTH)} GiB per batch", size=9, fill=ACCENT, anchor="end", weight="600")
    s += mono(ax.X(10), ax.Y(fix[0] / GiB) + 16, f"flat at {g(fix[0])} GiB", size=9, fill=LINK, anchor="middle", weight="600")
    rows = [("each batch keeps its graph:", INK), ("33 saved tensors × 48 MiB", MUTED), ("= 1,584 MiB", MUTED), ("", INK),
            ("16 linear-layer inputs,", MUTED), ("16 GELU inputs,", MUTED), ("1 input to the final square", MUTED), ("", INK),
            ("at the failure, 514 MiB is", MUTED), ("reserved but unallocated:", MUTED), ("alone, that reads as", MUTED),
            ("fragmentation", ACCENT)]
    s += note_lines(742, ax.y0 + 14, rows, gap=15)
    s += legend(vh - 24, vw, [("total = total + loss, grad on", f"line:{ACCENT}:1.9"),
                              ("under no_grad, summing loss.item()", f"line:{LINK}:1.9"),
                              ("the allowance", f"dash:{SOFT}")])
    return emit("07", "retained-graph", "A retained graph is a slope",
                "The same evaluation loop with and without torch.no_grad(): one climbs 1.55 GiB a batch, one stays flat.",
                "retained graph", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 520
    s = eyebrow(32, 40, "memory one process holds outside PyTorch's allocator, measured stage by stage on the GB10")
    names = list(STAGES)
    short = ["CUDA context, first tensor", "+ first cuBLAS matmul", "+ training kernels (GELU, Adam)",
             "+ first cuDNN convolution", "+ NCCL communicator, 1 rank", "+ first all_reduce", "after destroy_process_group()"]
    ax0, axw, top, rh, gap = 300, 560, 80, 22, 12
    X = lambda b: ax0 + b / (1300 * MiB) * axw  # noqa: E731
    for v in (0, 250, 500, 750, 1000, 1250):
        s += line(X(v * MiB), top - 12, X(v * MiB), top + 9 * (rh + gap) + 18, stroke=RULE, sw=0.8)
        s += mono(X(v * MiB), top - 18, f"{v} MiB", size=8, fill=SOFT)
    s += title(32, top + 8, "lazy loading (the default)", fill=INK)
    prev = None
    for k, name in enumerate(names):
        y = top + 16 + k * (rh + gap)
        v = STAGES[name]
        s += mono(ax0 - 12, y + 15, short[k], size=9, fill=INK, anchor="end")
        col = C_OTHER if "NCCL" in name or "all_reduce" in name else C_OUTSIDE
        s += rect(ax0, y, X(v) - ax0, rh, fill=col, op=0.55, stroke="none", sw=0)
        delta = "" if prev is None else (f"  ({'+' if v >= prev else '−'}{abs(v - prev) / MiB:.0f})")
        s += mono(X(v) + 8, y + 15, f"{v / MiB:.0f} MiB{delta}", size=8.5, fill=INK, anchor="start", weight="600")
        prev = v
    ye = top + 16 + len(names) * (rh + gap) + 24
    s += title(32, ye, "CUDA_MODULE_LOADING=EAGER", fill=INK)
    for k, (name, v) in enumerate(EAGER.items()):
        y = ye + 8 + k * (rh + gap)
        s += mono(ax0 - 12, y + 15, short[k], size=9, fill=INK, anchor="end")
        s += rect(ax0, y, X(v) - ax0, rh, fill=C_OUTSIDE, op=0.85, stroke="none", sw=0)
        s += mono(X(v) + 8, y + 15, f"{v / MiB:.0f} MiB", size=8.5, fill=INK, anchor="start", weight="600")
    s += mono(32, vh - 50, "Each bar is NVML's figure for the process minus PyTorch's reserved memory. cuBLAS workspaces "
              "are not in it: PyTorch 2.15 takes them from its own allocator.", size=8.5, fill=MUTED, anchor="start")
    s += legend(vh - 24, vw, [("CUDA context and loaded kernels, lazy", f"fill:{C_OUTSIDE}:0.55"),
                              ("with NCCL", f"fill:{C_OTHER}:0.55"), ("eager loading", f"fill:{C_OUTSIDE}:0.85")])
    return emit("08", "outside-pytorch", "What a process holds outside PyTorch",
                "The CUDA context is the floor; lazy loading keeps it small, and NCCL on one rank adds more than both.",
                "outside pytorch", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 470
    s = eyebrow(32, 40, "what the GB10 reported before, during and after an 8 GiB CPU tensor in an ordinary process")
    ax = Axes(110, 76, 520, 290, (-0.5, 2.5), (90, 118))
    s += ax.frame([0, 1, 2], [90, 95, 100, 105, 110, 115], xfmt=lambda v: ["start", "8 GiB CPU tensor", "freed"][v],
                  yfmt=lambda v: f"{v} GiB")
    series = [("cuda_free", INK, "CUDA free (cudaMemGetInfo)"), ("MemFree", ACCENT, "MemFree"),
              ("MemAvailable", LINK, "MemAvailable")]
    for key, col, _ in series:
        pts = [(ax.X(k), ax.Y(LOOKS[k][key] / GiB)) for k in range(3)]
        ring = key == "MemFree"             # drawn as rings round the CUDA-free dots it coincides with
        if not ring:
            s += polyline(pts, col, sw=1.6)
        for x, y in pts:
            s += dot(x, y, 6.5, fill="none", stroke=col) if ring else dot(x, y, 4.2, fill=col)
    for k in range(3):                       # left of the first column, under the middle one, right of the last
        dx, dy, anchor = {0: (-14, 4, "end"), 1: (0, 24, "middle"), 2: (14, 4, "start")}[k]
        s += mono(ax.X(k) + dx, ax.Y(LOOKS[k]["cuda_free"] / GiB) + dy, g(LOOKS[k]["cuda_free"]), size=8.5, fill=INK,
                  anchor=anchor, weight="600")
        s += mono(ax.X(k) + dx, ax.Y(LOOKS[k]["MemAvailable"] / GiB) + dy, g(LOOKS[k]["MemAvailable"]), size=8.5,
                  fill=LINK, anchor=anchor, weight="600")
    rows = [("CUDA total = MemTotal =", INK), (f"{g(LOOKS[0]['cuda_total'])} GiB", INK), ("", INK),
            ("CUDA free = MemFree,", INK), ("to the hundredth of a GiB", MUTED), ("", INK),
            (f"MemAvailable is {g(LOOKS[0]['MemAvailable'] - LOOKS[0]['cuda_free'])} GiB higher:", MUTED),
            ("memory Linux could reclaim,", MUTED), (f"{g(LOOKS[0]['Cached'])} GiB of it page cache,", MUTED),
            ("that CUDA does not count as free", MUTED), ("", INK),
            (f"the tensor cut CUDA free by {g(LOOKS[0]['cuda_free'] - LOOKS[1]['cuda_free'])} GiB;", ACCENT),
            ("NVML charged it to no GPU process", MUTED), ("", INK),
            ("nvidia-smi: Memory-Usage Not Supported", MUTED)]
    s += note_lines(690, ax.y0 + 12, rows, gap=15)
    s += mono(ax.x0, ax.y0 + ax.h + 34, "y axis starts at 90 GiB", size=8.5, fill=SOFT, anchor="start")
    s += legend(vh - 24, vw, [("CUDA free (cudaMemGetInfo)", f"dot:{INK}:4.2"), ("MemFree", f"ring:{ACCENT}:6.5"),
                              ("MemAvailable", f"dot:{LINK}:4.2")])
    return emit("09", "unified-memory", "On a unified-memory GPU, every program shares the card",
                "CUDA's free memory on the GB10 tracks the kernel's MemFree, not MemAvailable, and falls with CPU allocations.",
                "unified memory", vw, vh, s)


FIGS = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06, "07": fig07, "08": fig08,
        "09": fig09}

if __name__ == "__main__":
    for key in (sys.argv[1:] or FIGS):
        FIGS[key]()
