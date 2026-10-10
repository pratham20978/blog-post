#!/usr/bin/env python3
"""Generate figures 1-10 for gpu-idle-at-100-percent-utilization.

    python3 _figs.py            # all figures
    python3 _figs.py 2 10       # only those numbers

Every figure emits a triplet: an editable .html, an .svg, and a 2x .png.

Figures 2, 3, 4, 9 and 10 draw the worked example. They import the article's own
model, lab/queue_model.py, and read every number from it, so a figure cannot
disagree with the prose or with the lab. Figure 8 plots a measurement from the
ledger (Gray, NVIDIA, 2019). Figures 1, 5, 6 and 7 carry definitions whose
wording is in research/ledger.md.
"""

import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, PAPER2, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, box, callout, emit, eyebrow,
                    hbracket, hline, legend, masked, mono, txt, vline)

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "lab"))
import queue_model as qm  # noqa: E402

W = 960
STEP = {name: qm.one_step(phases) for name, phases in qm.VERSIONS}
AS_WRITTEN = STEP[qm.VERSIONS[0][0]]
NO_SYNC = STEP[qm.VERSIONS[1][0]]
FEWER = STEP[qm.VERSIONS[2][0]]
GRAPH = STEP[qm.VERSIONS[3][0]]
STEADY = {name: qm.steady_state(phases) for name, phases in qm.VERSIONS}


def ms(v, nd=1):
    return f"{v:.{nd}f} ms"


def seg(x, y, w, h, fill, stroke, dash=None, rx=3, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (f'<rect x="{x:.2f}" y="{y}" width="{max(w, 0.8):.2f}" height="{h}" rx="{rx}" '
            f'fill="{fill}"{o} stroke="{stroke}" stroke-width="1"{d}/>')


def hatch_defs(pid, colour, gap=6):
    return (f'<pattern id="{pid}" width="{gap}" height="{gap}" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="{gap}" '
            f'stroke="{colour}" stroke-width="1.2" stroke-opacity="0.55"/></pattern>')


def time_axis(x0, x1, y, lo, hi, ticks, label="milliseconds into the step"):
    def px(t):
        return x0 + (t - lo) / (hi - lo) * (x1 - x0)
    s = f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{MUTED}" stroke-width="1"/>'
    for t in ticks:
        s += (f'<line x1="{px(t):.2f}" y1="{y}" x2="{px(t):.2f}" y2="{y + 5}" '
              f'stroke="{MUTED}" stroke-width="0.8"/>')
        s += mono(px(t), y + 18, f"{t:g}", size=9, fill=SOFT)
    s += mono(x1, y + 34, label, size=8, fill=SOFT, anchor="end", track="0.10em")
    return s


# ---------------------------------------------------------------- figure 1
def fig01():
    """Four sample windows: nvidia-smi utilization against DCGM SM Activity."""
    vh = 470
    s = eyebrow(40, 44, "one sample window, four workloads", fill=SOFT)
    rows, cols = 10, 20          # N = 10 SMs drawn; time in 20 slices
    cw, ch = 9, 11
    panels = [
        ("A", "one block, whole window", [(0, 1, 0, cols)], "100%", "1/N", True),
        ("B", "N/5 blocks, whole window", [(0, 2, 0, cols)], "100%", "0.20", True),
        ("C", "N blocks, 1/5 of the window", [(0, rows, 0, cols // 5)], "20%", "0.20", False),
        ("D", "N blocks, whole window", [(0, rows, 0, cols)], "100%", "1.00", False),
    ]
    pw, gap = 205, 13
    x = 40
    for key, title, fills, util, act, mismatch in panels:
        gx, gy = x + 12, 104
        s += box(x, 64, pw, 316, fill="#ffffff",
                 stroke=ACCENT if mismatch else "rgba(45,49,66,0.28)", rx=6)
        s += mono(x + 12, 84, key, size=10, fill=ACCENT if mismatch else INK,
                  anchor="start", weight="600")
        s += txt(x + 30, 85, title, size=10.5, fill=INK, anchor="start", weight="500")
        gx = x + 38
        cw = 8.0
        for r in range(rows):
            for c in range(cols):
                on = any(r0 <= r < r1 and c0 <= c < c1 for r0, r1, c0, c1 in fills)
                s += (f'<rect x="{gx + c * cw}" y="{gy + r * ch}" width="{cw - 1.5}" '
                      f'height="{ch - 1.5}" rx="1" fill="{INK if on else PAPER2}" '
                      f'fill-opacity="{0.78 if on else 1}"/>')
        s += mono(gx - 6, gy + 7, "SM 1", size=6.5, fill=SOFT, anchor="end")
        s += mono(gx - 6, gy + rows * ch - 3, "SM N", size=6.5, fill=SOFT, anchor="end")
        s += hbracket(gx, gx + cols * cw - 1.5, gy + rows * ch + 8, "one window, 1/6 s to 1 s",
                      colour=SOFT, gap=14)
        ry = 262
        s += (f'<line x1="{x + 12}" y1="{ry - 14}" x2="{x + pw - 12}" y2="{ry - 14}" '
              f'stroke="{RULE}" stroke-width="0.8"/>')
        s += mono(x + 12, ry + 6, "nvidia-smi", size=8.5, fill=SOFT, anchor="start")
        s += mono(x + 12, ry + 18, "utilization.gpu", size=7.5, fill=SOFT, anchor="start")
        s += txt(x + pw - 14, ry + 16, util, size=22, family=SERIF,
                 fill=ACCENT if mismatch else INK, anchor="end")
        s += mono(x + 12, ry + 52, "DCGM", size=8.5, fill=SOFT, anchor="start")
        s += mono(x + 12, ry + 64, "SM Activity", size=7.5, fill=SOFT, anchor="start")
        s += txt(x + pw - 14, ry + 62, act, size=22, family=SERIF, fill=INK, anchor="end")
        s += mono(x + pw / 2, 366, "readings disagree" if mismatch else "readings agree",
                  size=8, fill=ACCENT if mismatch else SOFT, track="0.10em")
        x += pw + gap

    s += txt(W / 2, 414, "Utilization asks whether any kernel was executing: a question about "
             "time. SM Activity asks how many SMs held a warp: a question about space.",
             size=11, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 22, W, [
        ("an SM with at least one warp resident", INK, "box"),
        ("utilization reads 100% while most SMs are empty", ACCENT, "hollow"),
    ])
    return emit("01", "clock-not-gauge", "A clock, not a gauge",
                "nvidia-smi reports the share of a sample window during which some kernel was "
                "executing. It has no spatial term, so A and B read 100% on a mostly empty chip.",
                "part 3 · figure 1", W, vh, s)


# ---------------------------------------------------------------- figure 2
def lanes(s, x0, x1, lo, hi, step, y_host, y_gpu, h, *, labels=True, show_opt_band=True):
    def px(t):
        return x0 + (t - lo) / (hi - lo) * (x1 - x0)
    sp = step["spans_ms"]
    # host lane
    for name, (h0, h1, g0, g1) in sp.items():
        if name == "loss.item()":
            s += (f'<rect x="{px(h0):.2f}" y="{y_host}" width="{px(h1) - px(h0):.2f}" '
                  f'height="{h}" rx="3" fill="url(#hatch-accent)" stroke="{ACCENT}" '
                  f'stroke-width="1" stroke-dasharray="4 3"/>')
        elif h1 > h0:
            s += seg(px(h0), y_host, px(h1) - px(h0), h, "#ffffff", INK)
    # GPU lane: busy blocks for dense phases, a thin-density band for the optimizer
    s += seg(px(lo), y_gpu, px(hi) - px(lo), h, PAPER2, "rgba(45,49,66,0.18)", rx=3)
    kernels = step["kernels_ms"]
    for name, (h0, h1, g0, g1) in sp.items():
        if g1 <= g0:
            continue
        k = step["kernel_ms"][name]
        density = k / (g1 - g0)
        if density > 0.95:
            s += seg(px(g0), y_gpu, px(g1) - px(g0), h, ACCENT_TINT, ACCENT)
        elif show_opt_band:
            # One tick per 0.25 ms slice, as wide as the share of that slice the GPU
            # actually spent in a kernel -- read from the model's per-kernel intervals,
            # so a burst of queued kernels draws dense and a starved stretch draws sparse.
            t = g0
            while t < g1 - 1e-9:
                t1 = min(t + 0.25, g1)
                busy = sum(max(0.0, min(e, t1) - max(b, t)) for b, e in kernels
                           if e > t and b < t1)
                if busy > 0:
                    s += (f'<rect x="{px(t):.2f}" y="{y_gpu + 1}" '
                          f'width="{max(px(t + busy) - px(t), 0.6):.2f}" height="{h - 2}" '
                          f'fill="{ACCENT}" fill-opacity="0.85"/>')
                t = t1
    return s, px


def fig02():
    """The step as two lanes, host and GPU, to scale."""
    vh = 470
    st = AS_WRITTEN
    s = f"<defs>{hatch_defs('hatch-accent', ACCENT)}</defs>"
    s += eyebrow(40, 44, "one training step, one stream, to scale", fill=SOFT)
    x0, x1, lo, hi = 150, 920, 0.0, 32.5
    y_host, y_gpu, h = 116, 236, 40
    s += txt(40, y_host + 18, "host", size=13, weight="600", anchor="start")
    s += mono(40, y_host + 33, "Python thread", size=8, fill=SOFT, anchor="start")
    s += txt(40, y_gpu + 18, "GPU", size=13, weight="600", anchor="start")
    s += mono(40, y_gpu + 33, "stream 0", size=8, fill=SOFT, anchor="start")
    s, px = lanes(s, x0, x1, lo, hi, st, y_host, y_gpu, h)
    sp = st["spans_ms"]

    # host labels
    f0, f1 = sp["forward"][0], sp["backward"][1]
    s += mono(px(f0), y_host - 10,
              f"forward + backward issued in {ms(st['naive_ms']['forward'] + st['naive_ms']['backward'])}",
              size=8, fill=MUTED, anchor="start")
    w0, w1 = sp["loss.item()"][0], sp["loss.item()"][1]
    s += masked((px(w0) + px(w1)) / 2, y_host + 24,
                f"blocked in loss.item()  {ms(st['naive_ms']['loss.item()'])}",
                size=8.5, fill=ACCENT, pad=6)
    o0, o1 = sp["optimizer"][0], sp["optimizer"][1]
    s += mono((px(o0) + px(o1)) / 2, y_host + 24,
              f"issuing 1,000 optimizer launches  {ms(st['naive_ms']['optimizer'])}",
              size=8.5, fill=INK, weight="500")

    # GPU labels
    g0, g1 = sp["forward"][2], sp["forward"][3]
    s += mono((px(g0) + px(g1)) / 2, y_gpu + 24, f"forward {ms(st['kernel_ms']['forward'])}",
              size=8.5, fill=ACCENT, weight="600")
    g0, g1 = sp["backward"][2], sp["backward"][3]
    s += mono((px(g0) + px(g1)) / 2, y_gpu + 24, f"backward {ms(st['kernel_ms']['backward'])}",
              size=8.5, fill=ACCENT, weight="600")
    g0, g1 = sp["optimizer"][2], sp["optimizer"][3]
    s += mono((px(g0) + px(g1)) / 2, y_gpu + h + 16,
              f"1,000 kernels × 3 µs, one arriving every 20 µs: busy {ms(st['kernel_ms']['optimizer'])} of {ms(g1 - g0)}",
              size=8, fill=MUTED)

    # the release: GPU drains the queue at 12.0, the host is let go
    rel = sp["loss.item()"][1]
    s += vline(px(rel), y_gpu - 4, y_host + h + 6, stroke=ACCENT, marker="arrow-accent")
    s += mono(px(rel) + 8, (y_host + h + y_gpu) / 2 + 3, "queue empty: loss.item() returns",
              size=8, fill=ACCENT, anchor="start")
    # the host running ahead
    s += (f'<line x1="{px(sp["backward"][1])}" y1="{y_host + h + 6}" '
          f'x2="{px(sp["backward"][1])}" y2="{y_gpu - 6}" stroke="{RULE_SOLID}" '
          f'stroke-width="0.8" stroke-dasharray="2 3"/>')
    s += mono(px(sp["backward"][1]) + 6, y_gpu - 12, "host is 9.6 ms ahead of the GPU here",
              size=8, fill=SOFT, anchor="start")

    s += time_axis(x0, x1, 318, lo, hi, [0, 4, 8, 12, 16, 20, 24, 28, 32])
    idle = st["idle_ms"]
    s += txt(W / 2, 390, f"The GPU has nothing to run for {ms(idle)} of {ms(st['wall_ms'])} "
             f"({100 - st['utilization_pct']:.0f}%): more than half of this step is host-side.",
             size=11.5, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 24, W, [
        ("host issuing work", INK, "hollow"),
        ("host blocked on a sync point", ACCENT, "hollow"),
        ("kernels executing", ACCENT, "box"),
        ("GPU idle", SOFT, "box"),
    ])
    return emit("02", "one-step-two-lanes", "One step, two lanes",
                "The host lane and the GPU lane of one training step, drawn to one time scale "
                "from the article's model. Round inputs, not a measurement.",
                "part 3 · figure 2", W, vh, s)


# ---------------------------------------------------------------- figure 3
def fig03():
    """Host timer against CUDA events, per phase, with the 9.6 ms moved."""
    vh = 452
    st = AS_WRITTEN
    s = eyebrow(40, 44, "the same step, read by two clocks", fill=SOFT)
    x0, x1, hi = 230, 690, 21.0

    def px(v):
        return x0 + v / hi * (x1 - x0)

    phases = ["forward", "backward", "loss.item()", "optimizer"]
    verdict = {
        "forward": ("GPU-bound", "events 5× the host timer"),
        "backward": ("GPU-bound", "events 5× the host timer"),
        "loss.item()": ("billed for waiting", "no kernel ran here"),
        "optimizer": ("host-bound", "the clocks agree; 3.0 ms of kernels"),
    }
    y = 84
    s += mono(x0, 74, "host timer (perf_counter)", size=8, fill=INK, anchor="start", weight="500")
    s += mono(x0 + 190, 74, "CUDA events", size=8, fill=ACCENT, anchor="start", weight="500")
    ys = {}
    for ph in phases:
        n, e = st["naive_ms"][ph], st["event_ms"][ph]
        s += mono(40, y + 22, ph, size=11, fill=INK, anchor="start", weight="600")
        s += (f'<line x1="40" y1="{y + 62}" x2="{W - 40}" y2="{y + 62}" stroke="{RULE}" '
              f'stroke-width="0.8"/>')
        s += seg(x0, y + 6, px(n) - x0, 18, "#ffffff", INK)
        s += mono(px(n) + 8, y + 19, ms(n), size=9, fill=INK, anchor="start")
        s += seg(x0, y + 30, max(px(e) - x0, 1.2), 18, ACCENT_TINT, ACCENT)
        s += mono(px(e) + 8, y + 43, ms(e), size=9, fill=ACCENT, anchor="start")
        a, b = verdict[ph]
        s += txt(W - 44, y + 22, a, size=10.5, fill=ACCENT if ph == "loss.item()" else INK,
                 anchor="end", weight="600")
        s += txt(W - 44, y + 38, b, size=9, fill=SOFT, anchor="end")
        ys[ph] = y
        y += 70

    # totals
    tn = sum(st["naive_ms"].values())
    te = sum(st["event_ms"].values())
    s += mono(40, y + 18, "whole step", size=11, fill=INK, anchor="start", weight="600")
    s += mono(x0, y + 18, f"host timer {ms(tn)}   ·   CUDA events {ms(te)}", size=10,
              fill=MUTED, anchor="start")
    s += txt(W - 44, y + 18, "same total, different story", size=10.5, fill=INK,
             anchor="end", weight="600")

    # the transfer: 9.6 ms billed to loss.item() belongs to forward + backward
    yi = ys["loss.item()"] + 15
    yb = ys["backward"] + 39
    xi = px(st["naive_ms"]["loss.item()"])
    s += (f'<path d="M {xi + 62} {yi} C {xi + 120} {yi}, {xi + 120} {yb}, '
          f'{px(st["event_ms"]["backward"]) + 62} {yb}" fill="none" stroke="{ACCENT}" '
          f'stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow-accent)"/>')
    s += masked(xi + 70, yi + 24, "9.6 = 12.0 ms of GPU work − 2.4 ms spent issuing it",
                size=8, fill=ACCENT, anchor="start", pad=4)

    s += legend(vh - 24, W, [
        ("host clock: when the Python line returned", INK, "hollow"),
        ("GPU clock: when the stream reached the event", ACCENT, "box"),
    ])
    return emit("03", "two-readouts", "Two readouts of one step",
                "Each phase timed twice. The host timer charges loss.item() for 9.6 ms of work "
                "that ran earlier on the GPU; the events put it back where it happened.",
                "part 3 · figure 3", W, vh, s)


# ---------------------------------------------------------------- figure 4
def fig04():
    """Queue depth over the step, from the model's own trace."""
    vh = 440
    st = AS_WRITTEN
    s = eyebrow(40, 44, "kernels issued but not finished, over one step", fill=SOFT)
    x0, x1, lo, hi = 110, 910, 0.0, 32.5
    y0, y1, dmax = 330, 90, 100

    def px(t):
        return x0 + (t - lo) / (hi - lo) * (x1 - x0)

    def py(d):
        return y0 - d / dmax * (y0 - y1)

    # step curve
    pts = [(0.0, 0)]
    for t, d in st["trace"]:
        pts.append((t, pts[-1][1]))
        pts.append((t, d))
    pts.append((hi, pts[-1][1]))
    path = " ".join(f"{'M' if i == 0 else 'L'} {px(t):.2f} {py(d):.2f}" for i, (t, d) in enumerate(pts))
    area = path + f" L {px(hi):.2f} {py(0):.2f} L {px(0):.2f} {py(0):.2f} Z"
    s += f'<path d="{area}" fill="{ACCENT}" fill-opacity="0.10" stroke="none"/>'
    s += f'<path d="{path}" fill="none" stroke="{ACCENT}" stroke-width="1.4"/>'

    # axes
    s += f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="{MUTED}" stroke-width="1"/>'
    s += f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}" stroke="{MUTED}" stroke-width="1"/>'
    for d in (0, 25, 50, 75, 100):
        s += (f'<line x1="{x0 - 5}" y1="{py(d)}" x2="{x0}" y2="{py(d)}" stroke="{MUTED}" '
              f'stroke-width="0.8"/>')
        s += mono(x0 - 9, py(d) + 3, str(d), size=9, fill=SOFT, anchor="end")
    s += mono(x0 - 9, y1 - 14, "kernels in queue", size=8, fill=SOFT, anchor="start")
    for t in (0, 4, 8, 12, 16, 20, 24, 28, 32):
        s += (f'<line x1="{px(t):.2f}" y1="{y0}" x2="{px(t):.2f}" y2="{y0 + 5}" '
              f'stroke="{MUTED}" stroke-width="0.8"/>')
        s += mono(px(t), y0 + 18, str(t), size=9, fill=SOFT)
    s += mono(x1, y0 + 34, "milliseconds into the step", size=8, fill=SOFT, anchor="end",
              track="0.10em")

    # annotations, each tied to a point on the curve
    peak_t, peak_d = max(st["trace"], key=lambda p: p[1])
    sp = st["spans_ms"]
    s += callout(px(peak_t) + 60, py(peak_d) - 2,
                 f"{peak_d} kernels queued at {peak_t:.1f} ms: the host is ahead",
                 px(peak_t), py(peak_d), colour=ACCENT, anchor="start",
                 leader=(px(peak_t) + 54, py(peak_d) - 6), cx=px(peak_t) + 20, cy=py(peak_d) - 16)
    rel = sp["loss.item()"][1]
    s += callout(px(rel) + 40, py(38), "loss.item() waits until this reaches zero",
                 px(rel), py(1), colour=INK, anchor="start",
                 leader=(px(rel) + 34, py(38) + 4), cx=px(rel) + 10, cy=py(20))
    s += callout(px(22), py(20), "optimizer: the queue holds only the kernel that is running",
                 px(20), py(1), colour=INK, anchor="middle",
                 leader=(px(22), py(20) + 8), cx=px(21), cy=py(8))
    s += txt(W / 2, 398, "A deep queue means the GPU is the bottleneck. An empty one means "
             "the host is.", size=11.5, fill=MUTED, family=SERIF, style="italic")
    return emit("04", "queue-depth", "The queue between two clocks",
                "Queue depth over the worked example's step, computed by the article's model. "
                "Model output, not a measurement.",
                "part 3 · figure 4", W, vh, s)


# ---------------------------------------------------------------- figure 5
def fig05():
    """Two streams, one event, a device-side wait; the host never blocks."""
    vh = 450
    s = eyebrow(40, 44, "copy the next batch while this one computes", fill=SOFT)
    x0, x1 = 170, 910
    yh, ya, yb, h = 84, 196, 318, 38

    def px(f):                      # position as a fraction of the lane, schematic time
        return x0 + f * (x1 - x0)

    s += txt(40, yh + 16, "host", size=13, weight="600", anchor="start")
    s += mono(40, yh + 31, "Python thread", size=8, fill=SOFT, anchor="start")
    s += txt(40, ya + 16, "stream A", size=13, weight="600", anchor="start")
    s += mono(40, ya + 31, "copy engine", size=8, fill=SOFT, anchor="start")
    s += txt(40, yb + 16, "stream B", size=13, weight="600", anchor="start")
    s += mono(40, yb + 31, "compute", size=8, fill=SOFT, anchor="start")

    # host: five calls, issued back to back in microseconds, then the host is free
    calls = ["copy k+1 \u2192 A", "record E \u2192 A", "step k \u2192 B", "wait E \u2192 B",
             "step k+1 \u2192 B"]
    cx, cw_ = x0, 118
    for lab in calls:
        s += seg(cx, yh, cw_ - 6, h, "#ffffff", INK)
        s += mono(cx + (cw_ - 6) / 2, yh + 23, lab, size=8.5, fill=INK)
        cx += cw_
    s += mono(cx + 6, yh + 16, "all five return", size=8, fill=SOFT, anchor="start")
    s += mono(cx + 6, yh + 29, "in microseconds", size=8, fill=SOFT, anchor="start")

    # stream A: the copy, then event E
    a0, a1 = px(0.02), px(0.44)
    s += seg(a0, ya, a1 - a0, h, "#ffffff", LINK)
    s += mono((a0 + a1) / 2, ya + 23, "H2D copy of batch k+1, pinned", size=8.5, fill=LINK)
    ex = a1 + 12
    s += (f'<circle cx="{ex}" cy="{ya + h / 2}" r="7" fill="{PAPER}" stroke="{ACCENT}" '
          f'stroke-width="1.6"/>')
    s += mono(ex + 14, ya + h / 2 + 4, "E completes", size=8.5, fill=ACCENT, anchor="start",
              weight="600")

    # stream B: step k, the wait (already satisfied), step k+1
    b0, b1 = px(0.04), px(0.62)
    s += seg(b0, yb, b1 - b0, h, ACCENT_TINT, ACCENT)
    s += mono((b0 + b1) / 2, yb + 23, "step k kernels", size=8.5, fill=ACCENT, weight="600")
    wx = b1 + 10
    s += (f'<polygon points="{wx} {yb + 6}, {wx + 8} {yb + h / 2}, {wx} {yb + h - 6}, '
          f'{wx - 8} {yb + h / 2}" fill="{PAPER}" stroke="{ACCENT}" stroke-width="1.2"/>')
    c0, c1 = wx + 14, px(1.0)
    s += seg(c0, yb, c1 - c0, h, ACCENT_TINT, ACCENT)
    s += mono((c0 + c1) / 2, yb + 23, "step k+1 reads batch k+1", size=8.5, fill=ACCENT,
              weight="600")

    # the dependency: down from E, across between the lanes, down onto the wait marker
    mid = (ya + h + yb) / 2
    s += (f'<path d="M {ex} {ya + h / 2 + 8} V {mid - 8} Q {ex} {mid} {ex + 8} {mid} '
          f'H {wx - 8} Q {wx} {mid} {wx} {mid + 8} V {yb + 4}" fill="none" stroke="{ACCENT}" '
          f'stroke-width="1" stroke-dasharray="4 3" marker-end="url(#arrow-accent)"/>')
    s += mono(ex + 16, mid - 8, "cudaStreamWaitEvent: the wait happens on the GPU",
              size=8, fill=ACCENT, anchor="start")

    s += txt(W / 2, 392, "Nothing on the host lane blocks. The order between the two streams "
             "lives in event E, on the GPU.", size=11.5, fill=MUTED, family=SERIF,
             style="italic")
    s += legend(vh - 22, W, [
        ("host call, returns at once", INK, "hollow"),
        ("copy-engine work", LINK, "hollow"),
        ("compute kernels", ACCENT, "box"),
    ])
    return emit("05", "two-streams-one-event", "Two streams and one event",
                "An event recorded on the copy stream orders the compute stream without the host "
                "waiting for anything. Schematic order in time, not measured durations.",
                "part 3 · figure 5", W, vh, s)


# ---------------------------------------------------------------- figure 6
def fig06():
    """The legacy default stream serialises blocking streams; non-blocking ones overlap."""
    vh = 420
    s = eyebrow(40, 44, "k1 on stream 1, then k2 on stream 0, then k3 on stream 2", fill=SOFT)
    pw = 420
    panels = [
        (40, "blocking streams (cudaStreamCreate)", True),
        (500, "non-blocking streams (cudaStreamNonBlocking)", False),
    ]
    for px0, title, serial in panels:
        s += box(px0, 64, pw, 250, fill="#ffffff",
                 stroke=ACCENT if serial else "rgba(45,49,66,0.28)", rx=6)
        s += txt(px0 + 16, 88, title, size=11, weight="600", anchor="start",
                 fill=ACCENT if serial else INK)
        rows = [("stream 1", "k1"), ("stream 0", "k2"), ("stream 2", "k3")]
        for i, (sname, k) in enumerate(rows):
            y = 116 + i * 56
            s += mono(px0 + 16, y + 20, sname, size=9, fill=MUTED, anchor="start")
            s += (f'<line x1="{px0 + 90}" y1="{y + 30}" x2="{px0 + pw - 16}" y2="{y + 30}" '
                  f'stroke="{RULE}" stroke-width="0.8"/>')
            start = px0 + 96 + (i * 100 if serial else i * 14)
            s += seg(start, y + 6, 96, 24, ACCENT_TINT if serial else "#ffffff",
                     ACCENT if serial else INK)
            s += mono(start + 48, y + 22, k, size=9, fill=ACCENT if serial else INK, weight="600")
        verdict = ("stream 0 waits for stream 1, then stream 2 waits for stream 0"
                   if serial else "stream 0 no longer synchronises with them; they may overlap")
        s += txt(px0 + pw / 2, 296, verdict, size=9.5, fill=ACCENT if serial else MUTED)
    s += txt(W / 2, 350, "PyTorch's default stream is stream 0; the side streams it hands out "
             "are created non-blocking.", size=11.5, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 24, W, [
        ("serialised by the legacy default stream", ACCENT, "box"),
        ("free to overlap, resources permitting", INK, "hollow"),
    ])
    return emit("06", "default-stream", "The default stream is a hidden barrier",
                "The same three launches, against blocking and non-blocking streams. Schematic "
                "order in time, not measured durations.",
                "part 3 · figure 6", W, vh, s)


# ---------------------------------------------------------------- figure 7
def fig07():
    """The sync-point catalogue."""
    vh = 640
    s = eyebrow(40, 44, "calls that stop the host until the GPU catches up", fill=SOFT)
    cols = [(40, "the call"), (330, "the host waits for"), (640, "where you meet it")]
    for x, label in cols:
        s += eyebrow(x, 74, label, fill=SOFT)
    rows = [
        ("torch.cuda.synchronize()", "every stream on the device", "you wrote it", False),
        ("stream / event .synchronize()", "one stream, or one event's work", "you wrote it", False),
        ("t.item()   print(t)", "the value, copied back to the host", "logging, metrics", True),
        ("t.cpu()   t.to('cpu')", "the copy to finish", "saving, metrics, NumPy", True),
        ("t.nonzero()", "the GPU, to learn the output's size", "finding the indices of a mask", True),
        ("if (t != 0).all():", "the value, to pick a Python branch", "early stopping, guards", True),
        ("x.to('cuda')  non_blocking=False", "the copy (a stream sync follows it)", "every default copy", True),
        ("cudaFree", "work queued on all GPUs, possibly", "PyTorch's allocator avoids it", False),
        ("CUDA_LAUNCH_BLOCKING=1", "every kernel, after every launch", "debugging only", False),
    ]
    y = 88
    for call, waits, where, hidden in rows:
        h = 46
        s += box(40, y, W - 80, h, fill=ACCENT_TINT if hidden else "#ffffff",
                 stroke=ACCENT if hidden else "rgba(45,49,66,0.28)", rx=5)
        s += mono(58, y + h / 2 + 4, call, size=10.5, fill=ACCENT if hidden else INK,
                  anchor="start", weight="600")
        s += vline(318, y + 10, y + h - 10, stroke=RULE_SOLID, sw=0.8, marker=None)
        s += txt(330, y + h / 2 + 4, waits, size=10.5, fill=INK, anchor="start")
        s += vline(628, y + 10, y + h - 10, stroke=RULE_SOLID, sw=0.8, marker=None)
        s += txt(640, y + h / 2 + 4, where, size=10, fill=SOFT, anchor="start")
        y += h + 6
    s += txt(W / 2, y + 30, "The shaded rows are the ones nobody writes on purpose: each one "
             "moves a value, or a decision, from the GPU back to Python.",
             size=11.5, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 24, W, [
        ("an implicit sync: no synchronize in sight", ACCENT, "box"),
        ("explicit, or outside the training loop", INK, "hollow"),
    ])
    return emit("07", "sync-points", "Host-side sync points",
                "What each call waits for, and where it hides in a training loop. The PyTorch rows "
                "are the five kinds its Performance Tuning Guide names, plus the default copy.",
                "part 3 · figure 7", W, vh, s)


# ---------------------------------------------------------------- figure 8
def fig08():
    """Gray (NVIDIA, 2019): per-kernel cost on a V100, three ways."""
    vh = 400
    s = eyebrow(40, 44, "one short kernel, launched 20,000 times, three ways", fill=SOFT)
    x0, x1, hi = 330, 790, 10.0

    def px(v):
        return x0 + v / hi * (x1 - x0)

    kernel = 2.9
    rows = [
        ("synchronize after every launch", "cudaStreamSynchronize per kernel", 9.6),
        ("launches overlap execution", "one synchronize per step of 20", 3.8),
        ("one CUDA graph per step", "capture once, cudaGraphLaunch per step", 3.4),
    ]
    y = 90
    for label, sub, v in rows:
        s += txt(40, y + 16, label, size=11.5, weight="600", anchor="start")
        s += mono(40, y + 32, sub, size=8.5, fill=SOFT, anchor="start")
        s += seg(x0, y + 4, px(kernel) - x0, 28, INK, INK, rx=0, opacity=0.78)
        s += seg(px(kernel), y + 4, px(v) - px(kernel), 28, ACCENT, ACCENT, rx=0, opacity=0.85)
        s += mono(px(v) + 10, y + 23, f"{v:.1f} µs per kernel", size=10, fill=INK,
                  anchor="start", weight="600")
        s += mono(px(v) + 10, y + 37, f"{v - kernel:.1f} µs of overhead", size=8.5,
                  fill=ACCENT, anchor="start")
        y += 66
    # axis
    ay = y + 6
    s += f'<line x1="{x0}" y1="{ay}" x2="{x1}" y2="{ay}" stroke="{MUTED}" stroke-width="1"/>'
    for t in range(0, 11, 2):
        s += (f'<line x1="{px(t)}" y1="{ay}" x2="{px(t)}" y2="{ay + 5}" stroke="{MUTED}" '
              f'stroke-width="0.8"/>')
        s += mono(px(t), ay + 18, str(t), size=9, fill=SOFT)
    s += mono(x1, ay + 34, "microseconds per kernel, including overheads", size=8,
              fill=SOFT, anchor="end", track="0.10em")
    s += (f'<line x1="{px(kernel)}" y1="84" x2="{px(kernel)}" y2="{ay}" stroke="{INK}" '
          f'stroke-width="0.8" stroke-dasharray="2 3"/>')
    s += mono(px(kernel), 80, "2.9 µs: the kernel itself", size=8, fill=INK)
    s += legend(vh - 24, W, [
        ("kernel execution, 2.9 µs", INK, "box"),
        ("launch and synchronisation overhead", ACCENT, "box"),
    ])
    return emit("08", "launch-cost", "What a launch costs",
                "Measured by NVIDIA on a Tesla V100 with CUDA 10.1: an element-wise kernel over "
                "500,000 floats, 20 launches per step, 1,000 steps, wall clock divided by 20,000.",
                "part 3 · figure 8", W, vh, s)


# ---------------------------------------------------------------- figure 9
def fig09():
    """What a graph replay removes, and what survives."""
    vh = 476
    s = f"<defs>{hatch_defs('hatch-accent', ACCENT)}</defs>"
    s += eyebrow(40, 44, "the step without its sync point, eager against one graph", fill=SOFT)
    x0, x1, lo, hi = 160, 690, 0.0, 23.0
    h = 30
    rows = [("eager", NO_SYNC, 84), ("graph", GRAPH, 244)]
    for label, st, y in rows:
        s += txt(40, y + 20, label, size=13, weight="600", anchor="start")
        s += mono(40, y + 36, f"{ms(st['wall_ms'])} per step", size=8.5, fill=SOFT, anchor="start")
        s += mono(x0 - 12, y + 20, "host", size=8, fill=SOFT, anchor="end")
        s += mono(x0 - 12, y + h + 30, "GPU", size=8, fill=SOFT, anchor="end")
        s, px = lanes(s, x0, x1, lo, hi, st, y, y + h + 10, h)
        if label == "eager":
            sp = st["spans_ms"]
            s += mono(x0, y - 10, "1,120 launches in the step, 20 µs of host time each",
                      size=8, fill=MUTED, anchor="start")
            s += mono((px(sp["optimizer"][0]) + px(sp["optimizer"][1])) / 2, y + 19,
                      "optimizer: 1,000 of them", size=8, fill=INK)
        else:
            s += mono(px(0.02) + 6, y + 19, "one cudaGraphLaunch", size=8, fill=INK, anchor="start")
            s += mono(px(8), y + h + 29, "the same 15.0 ms of kernels, back to back",
                      size=8.5, fill=ACCENT, weight="600")
    s += time_axis(x0, x1, 350, lo, hi, [0, 4, 8, 12, 16, 20])

    # right-hand ledger of what changes
    lx = 716
    s += eyebrow(lx, 88, "removed", fill=ACCENT)
    removed = ["per-kernel host launch cost", "Python, C++ and driver dispatch"]
    for i, r in enumerate(removed):
        s += txt(lx, 108 + i * 17, r, size=10, fill=INK, anchor="start")
    s += eyebrow(lx, 170, "survives", fill=SOFT)
    kept = ["every kernel's execution time", "CPU work outside the graph", "sync points, moved out of it"]
    for i, r in enumerate(kept):
        s += txt(lx, 190 + i * 17, r, size=10, fill=INK, anchor="start")
    s += eyebrow(lx, 268, "costs added", fill=SOFT)
    added = ["capture + instantiation, once", "a private memory pool", "static shapes and addresses"]
    for i, r in enumerate(added):
        s += txt(lx, 288 + i * 17, r, size=10, fill=INK, anchor="start")
    s += txt(W / 2, 418, "A graph shortens the host lane. It cannot shorten the GPU lane.",
             size=11.5, fill=MUTED, family=SERIF, style="italic")
    s += legend(vh - 24, W, [
        ("host issuing", INK, "hollow"),
        ("kernels executing", ACCENT, "box"),
        ("GPU idle", SOFT, "box"),
    ])
    return emit("09", "what-graphs-remove", "What a graph replay removes",
                "The worked example's step with its mid-step sync removed, eager and as one "
                "captured graph, from the article's model. Round inputs, not a measurement.",
                "part 3 · figure 9", W, vh, s)


# ---------------------------------------------------------------- figure 10
def fig10():
    """Three versions of the step, one time scale."""
    vh = 520
    s = f"<defs>{hatch_defs('hatch-accent', ACCENT)}</defs>"
    s += eyebrow(40, 44, "the worked example, fixed twice, drawn to one scale", fill=SOFT)
    x0, x1, lo, hi = 190, 790, 0.0, 32.5
    h = 26
    versions = [
        ("as written", "loss.item() mid-step", AS_WRITTEN, STEADY[qm.VERSIONS[0][0]]),
        ("fix 1", "log outside the step", NO_SYNC, STEADY[qm.VERSIONS[1][0]]),
        ("fix 2", "optimizer as 10 launches", FEWER, STEADY[qm.VERSIONS[2][0]]),
    ]
    y = 80
    for label, sub, st, sd in versions:
        s += txt(40, y + 18, label, size=13, weight="600", anchor="start")
        s += mono(40, y + 34, sub, size=8.5, fill=SOFT, anchor="start")
        s += mono(x0 - 12, y + 18, "host", size=8, fill=SOFT, anchor="end")
        s += mono(x0 - 12, y + h + 26, "GPU", size=8, fill=SOFT, anchor="end")
        s, px = lanes(s, x0, x1, lo, hi, st, y, y + h + 8, h)
        if label == "fix 2":
            s += mono(px(st["spans_ms"]["optimizer"][1]) + 10, y + 11,
                      "host free after 2.6 ms:", size=8, fill=SOFT, anchor="start")
            s += mono(px(st["spans_ms"]["optimizer"][1]) + 10, y + 23,
                      "it runs ahead into the next step", size=8, fill=SOFT, anchor="start")
        s += (f'<line x1="{px(st["wall_ms"]):.2f}" y1="{y - 6}" x2="{px(st["wall_ms"]):.2f}" '
              f'y2="{y + 2 * h + 14}" stroke="{INK}" stroke-width="1"/>')
        s += txt(810, y + 22, ms(sd["period_ms"]), size=20, family=SERIF, anchor="start")
        util = sd["utilization_pct"]
        s += mono(810, y + 42, f"utilization {util:.0f}%", size=9,
                  fill=ACCENT if util >= 99.5 else MUTED, anchor="start", weight="600")
        y += 2 * h + 70
    s += time_axis(x0, x1, y - 36, lo, hi, [0, 4, 8, 12, 16, 20, 24, 28, 32])
    s += txt(W / 2, y + 22, "The last row reads 100%. That is where nvidia-smi stops "
             "being able to tell you anything.", size=11.5, fill=MUTED,
             family=SERIF, style="italic")
    s += legend(vh - 24, W, [
        ("host issuing", INK, "hollow"),
        ("host blocked", ACCENT, "hollow"),
        ("kernels executing", ACCENT, "box"),
        ("GPU idle", SOFT, "box"),
    ])
    return emit("10", "three-versions", "Three versions of one step",
                "Per-step time and utilization by nvidia-smi's definition, from the article's "
                "model: 32.0, then 22.4, then 15.0 ms. Round inputs, not a measurement.",
                "part 3 · figure 10", W, vh, s)


FIGURES = {1: fig01, 2: fig02, 3: fig03, 4: fig04, 5: fig05, 6: fig06, 7: fig07,
           8: fig08, 9: fig09, 10: fig10}

if __name__ == "__main__":
    wanted = [int(a) for a in sys.argv[1:]] or sorted(FIGURES)
    for n in wanted:
        FIGURES[n]()
