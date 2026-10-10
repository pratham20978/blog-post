#!/usr/bin/env python3
"""Figures 12-22 for postgresql-foundations-storage-layer (20 is the Mermaid figure, built by
_fig20.py). Every number is read from lab/captures.json or is arithmetic on those numbers."""
import json
import math
import pathlib
import re
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, SANS, SERIF, alabel, box, cell, emit, eyebrow,
                    hline, legend, masked, mono, node, tag, txt, vline)
from _figs_a import D, SER1, SER2, bar, fmt, note, ortho


def hv(x1, y1, x2, y2, stroke=MUTED, marker="arrow", r=6, dash=None):
    """Horizontal from (x1, y1) to x2, then vertical down or up to y2, rounded corner."""
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    d = f"M {x1} {y1} H {x2 - sx * r} Q {x2} {y1} {x2} {y1 + sy * r} V {y2}"
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1"{da}{m}/>'


def vturn(x1, y1, y2, x2, stroke=MUTED, marker="arrow", r=6):
    """Vertical from (x1, y1) to y2, then horizontal to x2, then down again is not needed."""
    sx = 1 if x2 > x1 else -1
    sy = 1 if y2 > y1 else -1
    d = f"M {x1} {y1} V {y2 - sy * r} Q {x1} {y2} {x1 + sx * r} {y2} H {x2}"
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1"{m}/>'


def vhv(x1, y1, ymid, x2, y2, stroke=MUTED, marker="arrow", r=6):
    """Down from (x1, y1) to ymid, across to x2, down to (x2, y2)."""
    if abs(x2 - x1) < 2 * r:
        d = f"M {x1} {y1} V {y2}"
    else:
        sx = 1 if x2 > x1 else -1
        d = (f"M {x1} {y1} V {ymid - r} Q {x1} {ymid} {x1 + sx * r} {ymid} "
             f"H {x2 - sx * r} Q {x2} {ymid} {x2} {ymid + r} V {y2}")
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="1"{m}/>'


def panel(x, y, w, h, title, sub, kind="backend"):
    fills = {"backend": ("#ffffff", INK), "focal": (ACCENT_TINT, ACCENT), "store": ("rgba(45,49,66,0.05)", MUTED)}
    fill, stroke = fills[kind]
    out = box(x, y, w, h, fill=fill, stroke=stroke)
    out += txt(x + 16, y + 22, title, size=11, weight="600", fill=ACCENT if kind == "focal" else INK, anchor="start")
    out += mono(x + 16, y + 38, sub, size=8, fill=SOFT, anchor="start")
    return out


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 420
    io = D["ios"]
    runs = [("all-visible", io["clean"]), ("1 row in 50 updated", io["dirty"]), ("after vacuum", io["vacuumed"])]
    times = [float(re.search(r"Execution Time: ([\d.]+) ms", r["plan"]).group(1)) for _, r in runs]
    bufs = [r["shared_hit"] + r["shared_read"] for _, r in runs]
    fetch = [r["heap_fetches"] for _, r in runs]
    s = eyebrow(32, 44, f"one index-only count of 100,000 rows, three times — {fmt(io['pages'])}-page copy of orders, PostgreSQL 16.2")
    base, top = 330, 96
    H = base - top
    # panel A: heap fetches, linear
    ax, aw = 72, 400
    s += txt(ax, 78, "heap fetches (linear)", size=11, weight="600", anchor="start")
    vmax = 110000
    for t in (0, 25000, 50000, 75000, 100000):
        y = base - t / vmax * H
        s += f'<line x1="{ax}" y1="{y}" x2="{ax + aw}" y2="{y}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(ax - 6, y + 3, fmt(t), size=7, fill=SOFT, anchor="end")
    for i, v in enumerate(fetch):
        x = ax + 30 + i * 125
        h = v / vmax * H
        s += bar(x, base - h, 80, max(h, 1.5), fill=ACCENT if i == 1 else SER2, opacity=0.55 if i == 1 else 0.45,
                 stroke=ACCENT if i == 1 else SER2)
        s += mono(x + 40, base - h - 8, fmt(v), size=9, fill=INK, weight="600")
        s += mono(x + 40, base + 16, runs[i][0], size=8, fill=INK)
        s += mono(x + 40, base + 30, f"{times[i]:.1f} ms", size=8, fill=SOFT)
    # panel B: shared buffers, log scale
    bx, bw = 572, 400
    s += txt(bx, 78, "shared buffers touched (log scale)", size=11, weight="600", anchor="start")
    lo, hi = 1, 6
    Y = lambda v: base - (math.log10(v) - lo) / (hi - lo) * H
    for e, lab in ((1, "10"), (2, "100"), (3, "1k"), (4, "10k"), (5, "100k"), (6, "1M")):
        y = Y(10 ** e)
        s += f'<line x1="{bx}" y1="{y}" x2="{bx + bw}" y2="{y}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(bx - 6, y + 3, lab, size=7, fill=SOFT, anchor="end")
    for i, v in enumerate(bufs):
        x = bx + 30 + i * 125
        y = Y(v)
        s += bar(x, y, 80, base - y, fill=ACCENT if i == 1 else SER2, opacity=0.55 if i == 1 else 0.45,
                 stroke=ACCENT if i == 1 else SER2)
        s += mono(x + 40, y - 8, fmt(v), size=9, fill=INK, weight="600")
        s += mono(x + 40, base + 16, runs[i][0], size=8, fill=INK)
    s += note(32, 384, "same plan, same index, same 100,000 rows each time; only the visibility map changed — the update cleared the bit on every page, vacuum set them all again")
    s += note(32, 400, "102,000 fetches for 100,000 counted rows: the extra 2,000 are index entries for old versions of rows the update moved")
    return emit("12", "index-only-scan", "What the visibility map buys an index-only scan",
                "Heap fetches and buffers for the same index-only count, with the visibility map clean, cleared, and clean again.",
                "the visibility map", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 520
    fsm = D["fsm_page_contents"]

    def nodes(blk):
        return [(int(a.rstrip(":")), int(b)) for a, b in re.findall(r"(\d+):\s+(\d+)", fsm[str(blk)])]
    s = eyebrow(32, 44, "the four FSM pages of orders, and the path each search follows — values are free space ÷ 32")
    # FSM page boxes
    s += node(408, 70, 200, 58, "FSM block 0", "level 2 · the root · max 174", kind="store", tagtext="root")
    s += node(408, 176, 200, 58, "FSM block 1", "level 1 · slots: 2 | 174", kind="store")
    s += panel(40, 290, 440, 150, "FSM block 2 · level 0", "leaf slots for heap pages 0 – 4,068")
    s += panel(536, 290, 440, 150, "FSM block 3 · level 0", "leaf slots for heap pages 4,069 onward", kind="focal")
    s += vline(508, 128, 174, stroke=ACCENT, marker="arrow-accent")
    s += alabel(540, 158, "174", fill=ACCENT, w=36)
    s += hv(408, 205, 260, 288, stroke=MUTED)
    s += alabel(340, 262, "slot 0 · max 2", w=96)
    s += hv(608, 205, 756, 288, stroke=ACCENT, marker="arrow-accent")
    s += alabel(690, 262, "slot 1 · max 174", fill=ACCENT, w=110)

    def path_row(x, y, w, pts, focal, last_label):
        step = w / (len(pts) - 1)
        out = ""
        for i, (nid, val) in enumerate(pts):
            cx = x + i * step
            if i:
                out += f'<line x1="{cx - step + 7}" y1="{y}" x2="{cx - 7}" y2="{y}" stroke="{ACCENT if focal else MUTED}" stroke-width="0.9"/>'
            out += (f'<circle cx="{cx}" cy="{y}" r="7" fill="{ACCENT_TINT if focal else "#ffffff"}" '
                    f'stroke="{ACCENT if focal else INK}" stroke-width="0.9"/>')
            out += mono(cx, y + 3, str(val), size=6, fill=INK)
            if i in (0, len(pts) - 1) or i % 3 == 0:
                out += mono(cx, y + 20, str(nid), size=6.5, fill=SOFT)
        out += mono(x + w, y + 36, last_label, size=8, fill=ACCENT if focal else INK, anchor="end", weight="600")
        return out
    p2 = nodes(2)
    p3 = nodes(3)
    s += mono(60, 358, "node index in the page's array →", size=7.5, fill=SOFT, anchor="start")
    s += path_row(64, 382, 392, p2, False, f"leaf node {p2[-1][0]} = heap page 32 · 2 × 32 = 64 B")
    s += mono(556, 358, "root of this page → leaf", size=7.5, fill=SOFT, anchor="start")
    s += path_row(560, 382, 392, p3, True, f"leaf node {p3[-1][0]} = heap page 7692 · 174 × 32 = 5,568 B")
    s += note(32, 470, "each FSM page is a binary max-tree in an array: a parent holds the larger of its two children, so the root answers \"is there room anywhere?\" in one byte")
    s += note(32, 488, "one leaf page covers 4,069 heap pages; orders' 7,693 pages need two leaves, one level-1 page and the root: 4 pages, 32 KB")
    return emit("13", "fsm-tree", "The free space map of orders",
                "Four FSM pages; the root's 174 says the most free space anywhere is 5,568 bytes, on page 7692.",
                "the free space map", vw, vh, s)


# ------------------------------------------------------------------ FIG 14
def fig14():
    vw, vh = 1016, 460
    sw = D["toast_sweep"]
    comp = [(r["raw_bytes"], r["bytes_in_row"]) for r in sw if r["kind"] == "compressible"]
    inc = [(r["raw_bytes"], r["bytes_in_row"]) for r in sw if r["kind"] == "incompressible"]
    x0, x1, y0, y1 = 96, 960, 372, 84
    X = lambda v: x0 + v / 10000 * (x1 - x0)
    Y = lambda v: y0 - (math.log10(v) - 1) / (math.log10(3000) - 1) * (y0 - y1)
    s = eyebrow(32, 44, "bytes a text value occupies in its (int, text) row (log scale), against its raw size — PostgreSQL 16.2, pglz")
    for t in (10, 30, 100, 300, 1000, 3000):
        s += f'<line x1="{x0}" y1="{Y(t)}" x2="{x1}" y2="{Y(t)}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0 - 8, Y(t) + 3, fmt(t), size=7.5, fill=SOFT, anchor="end")
    for t in range(0, 10001, 2000):
        s += f'<line x1="{X(t)}" y1="{y0}" x2="{X(t)}" y2="{y0 + 4}" stroke="{MUTED}" stroke-width="0.8"/>'
        s += mono(X(t), y0 + 16, fmt(t), size=7.5, fill=SOFT)
    s += mono((x0 + x1) / 2, y0 + 34, "raw value size, bytes", size=8, fill=MUTED)
    s += mono(x0 - 60, y1 - 18, "bytes stored in the row · log scale", size=8, fill=MUTED, anchor="start")
    # threshold
    s += f'<line x1="{X(2000.5)}" y1="{y1 - 6}" x2="{X(2000.5)}" y2="{y0}" stroke="{ACCENT}" stroke-width="1" stroke-dasharray="4,3"/>'
    s += masked(X(2000.5) + 8, y1 + 4, "2,000 B value = 2,032 B row: the threshold", size=8, fill=ACCENT, anchor="start")

    def line(pts, col, dash=None):
        d = " ".join(f"{'M' if i == 0 else 'L'} {X(a):.1f} {Y(b):.1f}" for i, (a, b) in enumerate(pts))
        da = f' stroke-dasharray="{dash}"' if dash else ""
        out = f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.6"{da}/>'
        for a, b in pts:
            out += f'<circle cx="{X(a):.1f}" cy="{Y(b):.1f}" r="2.6" fill="{col}"/>'
        return out
    inline = [p for p in comp if p[0] <= 2000]
    s += line(inline, INK)
    s += line([p for p in comp if p[0] > 2000], SER1)
    s += line([p for p in inc if p[0] > 2000], ACCENT)
    s += f'<line x1="{X(2000)}" y1="{Y(2004)}" x2="{X(2001)}" y2="{Y(51)}" stroke="{SER1}" stroke-width="0.8" stroke-dasharray="2,2"/>'
    s += mono(X(500) + 6, Y(504) + 20, "inline, 1 byte per byte", size=8, fill=INK, anchor="start")
    last_c = [p for p in comp if p[0] == 10000][0]
    s += mono(X(10000) - 4, Y(last_c[1]) - 10, f"compressible: {last_c[1]} B at 10,000 (pglz, inline)", size=8, fill=SER1, anchor="end")
    s += mono(X(10000) - 4, Y(18) - 10, "incompressible: an 18 B pointer, value out of line", size=8, fill=ACCENT, anchor="end")
    first_c = [p for p in comp if p[0] == 2001][0]
    s += mono(X(2001) + 10, Y(first_c[1]) + 14, f"2,001 B → {first_c[1]} B", size=8, fill=SER1, anchor="start")
    s += legend(430, vw, [("inline, uncompressed", INK, "line"), ("compressed, inline", SER1, "line"), ("out of line (TOAST pointer)", ACCENT, "line")])
    return emit("14", "toast-threshold", "Where TOAST starts",
                "Bytes stored in the row for text values of increasing size, compressible and not.",
                "TOAST", vw, vh, s)


# ------------------------------------------------------------------ FIG 15
def fig15():
    vw, vh = 1016, 396
    ptr = D["toast_update"]["pointer"]
    b = bytes.fromhex(ptr["hex"])
    s = eyebrow(32, 44, "the last 18 bytes of row 4242's tuple, and the six chunk rows they point at")
    x0, cw, y = 32, 952 / 18, 84
    for i, v in enumerate(b):
        s += cell(x0 + i * cw, y, cw, 34, f"{v:02x}", size=11, fill=ACCENT_TINT if i < 2 else "#ffffff",
                  tcolor=ACCENT if i < 2 else INK)
    fields = [(0, 2, "header 0x01 + tag 18", "on-disk pointer"),
              (2, 4, "raw size", fmt(ptr["va_rawsize"])), (6, 4, "stored size · method", f"{fmt(ptr['va_extsize'])} · none"),
              (10, 4, "value id", str(ptr["va_valueid"])), (14, 4, "TOAST table oid", str(ptr["va_toastrelid"]))]
    for off, n, name, val in fields:
        xa, xb = x0 + off * cw + 2, x0 + (off + n) * cw - 2
        s += f'<path d="M {xa} {y + 42} V {y + 48} H {xb} V {y + 42}" fill="none" stroke="{INK}" stroke-width="0.9"/>'
        s += mono((xa + xb) / 2, y + 64, name, size=8 if n > 1 else 7, fill=INK, weight="600")
        s += mono((xa + xb) / 2, y + 80, val, size=8 if n > 1 else 7, fill=MUTED)
    # chunk rows on two TOAST pages, placed as the heap places tuples: from the page end backwards
    chunks = D["toast_update"]["chunks"]
    yp = 226
    pw = 440
    k = pw / 8192
    for page, seqs in ((0, chunks[:4]), (1, chunks[4:])):
        px = 32 + page * (pw + 72)
        s += mono(px, yp + 92, f"{D['toast_table']} · page {page} · 8,192 B", size=9, fill=INK, anchor="start", weight="600")
        s += bar(px, yp, pw, 70, fill="#ffffff", opacity=1, stroke=INK)
        s += bar(px, yp, 24 * k, 70, fill=INK, opacity=0.6)
        right = px + pw
        for cid, seq, nbytes in seqs:
            tl = 24 + 4 + 4 + 4 + nbytes           # tuple header, chunk_id, chunk_seq, varlena header, data
            wbar = ((tl + 7) // 8 * 8) * k
            left = right - wbar
            small = seq == 5
            s += bar(left, yp + 10, wbar, 50, fill=ACCENT if small else SER2, opacity=0.35, stroke=ACCENT if small else SER2)
            if small:
                s += mono(left - 6, yp + 32, f"seq {seq}", size=8, fill=ACCENT, anchor="end", weight="600")
                s += mono(left - 6, yp + 46, f"{nbytes} B", size=8, fill=ACCENT, anchor="end")
            else:
                s += mono(left + wbar / 2, yp + 32, f"seq {seq}", size=8.5, fill=INK, weight="600")
                s += mono(left + wbar / 2, yp + 46, f"{fmt(nbytes)} B", size=8, fill=MUTED)
            right = left
    s += vline(32 + 12 * cw, y + 88, yp - 2, stroke=ACCENT, marker="arrow-accent")
    s += alabel(32 + 12 * cw + 90, yp - 10, f"chunks with chunk_id {ptr['va_valueid']}", fill=ACCENT, w=160)
    s += note(32, 352, "four full chunks fill TOAST page 0 (the chunk size is chosen so four fit); chunk 4 opens page 1 and the 20-byte remainder follows it")
    s += note(32, 370, "a unique index on (chunk_id, chunk_seq) finds them; the pointer carries both sizes, so length() needs no chunk at all")
    return emit("15", "toast-pointer", "Eighteen bytes for ten thousand",
                "The TOAST pointer at the end of row 4242, decoded, and the six chunks it names.",
                "TOAST", vw, vh, s)


# ------------------------------------------------------------------ FIG 16
def fig16():
    vw, vh = 1016, 600
    walk = D["btree_walk"]
    root, mid, leaf = walk
    s = eyebrow(32, 44, f"looking up customer_id = {D['btree_customer']} in orders_customer_idx — one page per level, then the heap")
    # metapage
    s += node(32, 70, 176, 70, "metapage", f"block 0 · root {D['btree_meta']['root']}, level {D['btree_meta']['level']}", kind="store")
    s += hline(208, 222, 105, stroke=MUTED)
    # root row of pivots
    piv = [None, 24709, 49417, 74125, 98833]
    rx, ry, pw_ = 224, 76, 150
    s += mono(rx, ry - 8, f"block {root['block']} · root, level 2 · {root['live_items']} pivots", size=8, fill=INK, anchor="start", weight="600")
    for i, kv in enumerate(piv):
        chosen = kv == root["downlink_key"]
        s += cell(rx + i * pw_, ry, pw_, 58, "−∞" if kv is None else fmt(kv), size=11,
                  fill=ACCENT_TINT if chosen else "#ffffff", tcolor=ACCENT if chosen else INK)
    cxr = rx + 3 * pw_ + pw_ / 2
    # level 1
    y1 = 206
    cx1 = 32 + 3 * (952 / 7) + (952 / 7) / 2
    s += vhv(cxr, ry + 58, 170, cx1, y1 - 2, stroke=ACCENT, marker="arrow-accent")
    s += alabel(cxr - 110, 170, f"{fmt(root['downlink_key'])} ≤ {fmt(D['btree_customer'])} < 98,833 → block {mid['block']}", fill=ACCENT, w=220)
    cells1 = [("−∞", False), ("74,212", False), ("…", False), (fmt(mid["downlink_key"]), True), ("…", False), ("98,746", False), (f"HK {fmt(mid['high_key'])}", False)]
    w1 = 952 / len(cells1)
    s += mono(32, y1 - 8, f"block {mid['block']} · level 1 · {mid['live_items']} items · {fmt(mid['free_size'])} B free", size=8, fill=INK, anchor="start", weight="600")
    for i, (lab, ch) in enumerate(cells1):
        s += cell(32 + i * w1, y1, w1, 50, lab, size=10, fill=ACCENT_TINT if ch else ("rgba(45,49,66,0.05)" if lab.startswith("HK") else "#ffffff"),
                  tcolor=ACCENT if ch else INK)
    s += mono(32 - 2, y1 + 70, f"← block {mid['prev']}", size=7.5, fill=LINK, anchor="start")
    s += mono(984, y1 + 70, f"block {mid['next']} →", size=7.5, fill=LINK, anchor="end")
    # leaf
    y2 = 330
    target = 32 + 100 + 60 + 230 + 115
    s += vhv(cx1, y1 + 50, 296, target, y2 - 2, stroke=ACCENT, marker="arrow-accent")
    s += alabel(cx1 - 110, 296, f"{fmt(mid['downlink_key'])} ≤ {fmt(D['btree_customer'])} → block {leaf['block']}", fill=ACCENT, w=190)
    m = leaf["matches"]
    cells2 = [(fmt(leaf["first_key"]), "", False), ("…", "", False),
              (f"{fmt(D['btree_customer'])} · posting list", f"{m[0]['ntids']} TIDs · {m[0]['itemlen']} B", True),
              (f"{fmt(D['btree_customer'])} · plain", f"{m[1]['htid']} · {m[1]['itemlen']} B", True),
              ("…", "", False), (fmt(leaf["last_key"]), "", False), (f"HK {fmt(leaf['high_key'])}", "", False)]
    widths = [100, 60, 230, 230, 60, 100, 172]
    s += mono(32, y2 - 8, f"block {leaf['block']} · leaf · {leaf['live_items']} items · {fmt(leaf['free_size'])} B free", size=8, fill=INK, anchor="start", weight="600")
    x = 32
    centers = []
    for (lab, sub, ch), wd in zip(cells2, widths):
        s += cell(x, y2, wd, 56, "", fill=ACCENT_TINT if ch else ("rgba(45,49,66,0.05)" if lab.startswith("HK") else "#ffffff"))
        s += mono(x + wd / 2, y2 + 24 if sub else y2 + 32, lab, size=9.5, fill=ACCENT if ch else INK, weight="600" if ch else "400")
        if sub:
            s += mono(x + wd / 2, y2 + 42, sub, size=8, fill=MUTED)
        centers.append(x + wd / 2)
        x += wd
    s += mono(30, y2 + 76, f"← block {leaf['prev']}", size=7.5, fill=LINK, anchor="start")
    s += mono(984, y2 + 76, f"block {leaf['next']} → (right-link)", size=7.5, fill=LINK, anchor="end")
    # heap
    y3 = 470
    hx = centers[3]
    s += vline(hx, y2 + 56, y3 - 2, stroke=ACCENT, marker="arrow-accent")
    s += alabel(hx + 60, y3 - 16, "heap page 7692", fill=ACCENT, w=110)
    slots = [("slot 41", "redirect → 42"), ("slot 42", "HOT-updated → 43"), ("slot 43", "current version")]
    sx0 = hx - 250
    for i, (a, bsub) in enumerate(slots):
        sx = sx0 + i * 180
        s += node(sx, y3, 150, 56, a, bsub, kind="focal" if i == 2 else "backend")
        if i:
            s += hline(sx - 30, sx - 2, y3 + 28, stroke=ACCENT, marker="arrow-accent")
    s += note(32, 560, f"13 shared buffers for the query: these 3 index pages + 10 heap pages for the customer's 10 orders · the metapage is cached by each backend")
    s += note(32, 578, "HK = high key, the page's upper bound; a search whose key is above it follows the right-link (Lehman & Yao)")
    return emit("16", "btree-lookup", "One B-tree lookup, page by page",
                "Metapage, root, one internal page, one leaf, then a HOT chain on the heap page.",
                "the B-tree", vw, vh, s)


# ------------------------------------------------------------------ FIG 17
def fig17():
    vw, vh = 1016, 540
    before = D["split_before"]
    after = {p[0]: p for p in D["split_after"]["pages"]}
    mid = {p[0]: p for p in D["split_mid"]["after"]}
    wal = {r["record_type"]: r["record_length"] for r in D["split_wal"]}
    usable = 8192 - 24 - 16
    s = eyebrow(32, 44, "a fresh one-column index: 407 ascending keys fill one leaf; the 408th splits it — pages drawn to scale")
    pw = 420

    def page(x, y, label, used, free, focal=False, keys=""):
        out = mono(x, y - 8, label, size=8.5, fill=INK, anchor="start", weight="600")
        out += bar(x, y, pw, 40, fill="#ffffff", opacity=1, stroke=INK)
        out += bar(x, y, pw * used / usable, 40, fill=ACCENT if focal else SER2, opacity=0.35, stroke=ACCENT if focal else SER2)
        out += mono(x + 8, y + 24, keys, size=8.5, fill=INK, anchor="start")
        out += mono(x + pw - 6, y + 56, f"{fmt(free)} B free", size=8, fill=MUTED, anchor="end")
        return out
    # before
    s += txt(32, 88, "before", size=11, weight="600", anchor="start")
    s += page(32, 112, "block 1 · leaf, and the root", usable - before["leaf"][1], before["leaf"][1], True, f"keys 1 … 407 ({before['leaf'][0]} items)")
    # after
    s += txt(520, 88, f"after · SPLIT_R {wal['SPLIT_R']} B + NEWROOT {wal['NEWROOT']} B of WAL", size=11, weight="600", anchor="start")
    s += node(620, 108, 220, 58, "block 3 · new root", "−∞ → block 1 · 367 → block 2", kind="focal")
    y = 230
    l, r = after[1], after[2]
    s += page(32, y, "block 1 · left leaf", usable - l[3], l[3], False, "keys 1 … 366 + high key 367")
    s += page(532, y, "block 2 · right leaf", usable - r[3], r[3], False, "keys 367 … 408")
    s += vhv(680, 166, 196, 242, y - 2, stroke=MUTED)
    s += mono(460, 190, "−∞", size=8, fill=MUTED)
    s += vhv(780, 166, 196, 742, y - 2, stroke=MUTED)
    s += mono(800, 190, "367", size=8, fill=MUTED, anchor="start")
    s += hline(454, 530, y + 14, stroke=LINK, marker="arrow-link")
    s += alabel(492, y + 14, "right-link", fill=LINK, w=70, gap=-12)
    s += note(32, y + 88, f"the left page kept {l[2] - 1} of 407 keys (90% full): at the right edge PostgreSQL assumes keys keep ascending, so it leaves the left page at the leaf fill factor")
    # middle split
    ym = 386
    s += txt(32, ym, f"a split in the middle of a tree, after {D['split_mid']['odd_inserted']} more keys: free space is equalised instead", size=11, weight="600", anchor="start")
    a1, a4 = mid[1], mid[4]
    s += page(32, ym + 26, f"block 1 · {a1[2]} items", usable - a1[3], a1[3], False, "")
    s += page(532, ym + 26, f"block 4 · {a4[2]} items (new)", usable - a4[3], a4[3], False, "")
    s += hline(454, 530, ym + 40, stroke=LINK, marker="arrow-link")
    s += legend(512, vw, [("page that split", ACCENT, "box"), ("leaf after the split", SER2, "box"), ("right-link to the next leaf", LINK, "line")])
    return emit("17", "btree-split", "One leaf split, to scale",
                "At the right edge the left page stays 90% full; in the middle the page splits evenly.",
                "the B-tree", vw, vh, s)


# ------------------------------------------------------------------ FIG 18
def fig18():
    vw, vh = 1016, 460
    rf = D["update2"]["record_file"]
    lsn = rf["lsn"]
    hi, lo = lsn.split("/")
    lo = lo.rjust(8, "0")
    digits = hi.rjust(8, "0") + lo
    s = eyebrow(32, 44, f"LSN {lsn} as 64 bits (hex), and what each part names — 16 MiB segments, timeline 1")
    x0, cw, y = 32, 952 / 16, 84
    for i, dch in enumerate(digits):
        grp = 0 if i < 8 else (1 if i < 10 else 2)
        fill = ["#ffffff", ACCENT_TINT, "rgba(94,122,155,0.18)"][grp]
        s += cell(x0 + i * cw, y, cw, 40, dch, size=13, fill=fill, tcolor=ACCENT if grp == 1 else INK)
    groups = [(0, 8, "high 32 bits: 3", "= name field 2: 00000003"), (8, 2, "top 8 bits of the low half: F6", "= name field 3: 000000F6"),
              (10, 6, f"low 24 bits: {lo[2:]}", f"= byte {fmt(rf['offset_in_segment'])} of the file")]
    for off, n, a, b in groups:
        xa, xb = x0 + off * cw + 2, x0 + (off + n) * cw - 2
        s += f'<path d="M {xa} {y + 48} V {y + 54} H {xb} V {y + 48}" fill="none" stroke="{INK}" stroke-width="0.9"/>'
        s += mono((xa + xb) / 2, y + 72, a, size=8.5, fill=INK, weight="600")
        s += mono((xa + xb) / 2, y + 88, b, size=8.5, fill=MUTED)
    # the file name
    yn = 222
    s += mono(32, yn - 10, "the segment file", size=9, fill=INK, anchor="start", weight="600")
    parts = [("00000001", "timeline"), ("00000003", "segment ÷ 256"), ("000000F6", "segment mod 256")]
    for i, (p, lab) in enumerate(parts):
        s += cell(32 + i * 200, yn, 200, 40, p, size=14, fill=ACCENT_TINT if i == 2 else "#ffffff", tcolor=ACCENT if i == 2 else INK)
        s += mono(32 + i * 200 + 100, yn + 56, lab, size=8, fill=MUTED)
    s += mono(672, yn + 25, f"pg_wal/{rf['segment_file']}", size=10, fill=INK, anchor="start")
    # the segment as WAL pages
    ys = 334
    pages = 2048
    k = 952 / pages
    s += mono(32, ys - 10, f"inside it: 2,048 WAL pages of 8,192 bytes · the record is in page {fmt(rf['wal_page_in_segment'])}, at byte {rf['offset_in_wal_page']}", size=9, fill=INK, anchor="start", weight="600")
    s += bar(32, ys, 952, 28, fill=SER2, opacity=0.22, stroke=SER2)
    s += bar(32, ys, 2.2, 28, fill=INK, opacity=0.8)
    s += bar(32 + rf["wal_page_in_segment"] * k, ys - 4, 2.5, 36, fill=ACCENT, opacity=1)
    s += mono(32 + rf["wal_page_in_segment"] * k, ys + 48, f"page {rf['wal_page_in_segment']} · {fmt(rf['wal_page_in_segment'] * 8192)} + {rf['offset_in_wal_page']} = {fmt(rf['offset_in_segment'])}", size=8, fill=ACCENT)
    s += mono(34, ys + 48, "page 0 · long header", size=8, fill=INK, anchor="start")
    s += note(32, 420, "pg_walfile_name_offset() does this arithmetic; every WAL page starts with a small header, and page 0 of each file with a long one")
    return emit("18", "lsn-to-file", "From an LSN to a file and a byte",
                "The high bits of an LSN name the segment file; the low 24 bits are the byte within it.",
                "WAL", vw, vh, s)


# ------------------------------------------------------------------ FIG 19
def fig19():
    vw, vh = 1016, 520
    rf = D["update2"]["record_file"]
    rec = bytes.fromhex(rf["bytes_hex"])
    dec = rf["decoded"]
    s = eyebrow(32, 44, f"the HOT_UPDATE record at {rf['lsn']}, all {len(rec)} bytes, read from {rf['segment_file']}")
    rows = [
        (0, 24, 84, "XLogRecord header · 24 B", [(0, 4, "total length", str(dec["xl_tot_len"])), (4, 4, "xid", str(dec["xl_xid"])),
                                                (8, 8, "prev record", dec["xl_prev"]), (16, 1, "info", "0x40"),
                                                (17, 1, "rmgr", "10"), (18, 2, "pad", ""), (20, 4, "CRC-32C", dec["xl_crc"])]),
        (24, 46, 224, "block reference · 20 B, then the main-data header · 2 B", [(24, 1, "id", "0"), (25, 1, "flags", "has data"),
                                                                                  (26, 2, "data len", "17"), (28, 4, "tablespace", "1663"),
                                                                                  (32, 4, "database", str(dec["blocks"][0]["rel"][1])),
                                                                                  (36, 4, "relation", str(dec["blocks"][0]["rel"][2])),
                                                                                  (40, 4, "block", str(dec["blocks"][0]["block"])),
                                                                                  (44, 2, "main len", "14")]),
        (46, 77, 364, "block 0 data · 17 B, then main data · 14 B", [(46, 2, "prefix", "24"), (48, 5, "tuple header", "infomask2, infomask, t_hoff"),
                                                                      (53, 1, "pad", ""), (54, 9, "new bytes", "0x13 + refunded"),
                                                                      (63, 4, "old xmax", str(dec["xl_xid"])), (67, 2, "old off", "41"),
                                                                      (69, 1, "bits", ""), (70, 1, "flags", "0x20"), (71, 4, "new xmax", "0"),
                                                                      (75, 2, "new off", "42")]),
    ]
    for start, end, y, label, fields in rows:
        cw = 952 / (end - start)
        s += mono(32, y - 20, label, size=9, fill=INK, anchor="start", weight="600")
        for i in range(start, end):
            xi = 32 + (i - start) * cw
            s += cell(xi, y, cw, 30, f"{rec[i]:02x}", size=10 if cw > 30 else 9,
                      fill=ACCENT_TINT if 54 <= i < 63 else "#ffffff", tcolor=ACCENT if 54 <= i < 63 else INK)
        for off, n, name, val in fields:
            xa = 32 + (off - start) * cw + 2
            xb = 32 + (off + n - start) * cw - 2
            col = ACCENT if off == 54 or name == "CRC-32C" else INK
            s += f'<path d="M {xa} {y + 38} V {y + 44} H {xb} V {y + 38}" fill="none" stroke="{col}" stroke-width="0.9"/>'
            fs = 7.5 if n > 1 else 6.5
            s += mono((xa + xb) / 2, y + 60, name, size=fs, fill=col, weight="600")
            if val:
                s += mono((xa + xb) / 2, y + 75, val, size=fs, fill=MUTED)
    crc = "matches" if dec["crc_ok"] else "does NOT match"
    s += note(32, 480, f"CRC-32C computed by the lab over bytes 24–76 then 0–19: {dec['crc_computed']} — {crc} the stored value")
    s += note(32, 498, "flags 0x20 = the new tuple's first 24 bytes equal the old tuple's, so only the header and the tail are logged (both versions share page 7692)")
    return emit("19", "wal-record", "One WAL record, byte by byte",
                "The 77-byte HOT_UPDATE: header, block reference, the changed tail of the tuple, and the slot numbers.",
                "WAL", vw, vh, s)


# ------------------------------------------------------------------ FIG 21
def fig21():
    vw, vh = 1016, 470
    seg = D["archive"]["switched_file"]
    s = eyebrow(32, 44, "one stream of WAL, three processes that read it — all three ran in the lab")
    s += node(32, 196, 130, 64, "backends", "insert and flush WAL", kind="backend")
    s += node(236, 188, 170, 80, "pg_wal", f"…{seg[-4:]} and neighbours", kind="focal", tagtext="16 MiB segments")
    s += hline(162, 234, 228, stroke=MUTED)
    s += alabel(198, 228, "records", w=58)
    readers = [
        (76, "startup process", "crash recovery, from REDO", "table files", "pages brought current", "redo from 3/F6D691A0"),
        (208, "archiver", "archive_command per segment", "archive directory", f"…{seg[-6:]} + .done", "finished segment"),
        (340, "walsender", "streams records as written", "pg_receivewal", "or a standby's walreceiver", "stream as written"),
    ]
    xm = [430, 450, 470]
    for i, (y, a_, asub, b_, bsub, lab) in enumerate(readers):
        s += node(600, y, 200, 64, a_, asub, kind="backend")
        s += node(830, y, 154, 64, b_, bsub, kind="store")
        s += hline(800, 828, y + 32, stroke=MUTED)
        ey = 204 + i * 24
        s += ortho(406, ey, xm[i], y + 32, 598, stroke=ACCENT, marker="arrow-accent")
        s += alabel((xm[i] + 598) / 2, y + 32, lab, fill=ACCENT, w=len(lab) * 6 + 14)
    s += note(32, 438, f"in this run one file, {seg}, held the second update's record, the crash step's REDO point and replayed records, and was the segment the archiver copied")
    return emit("21", "three-readers", "Three readers of one log",
                "Crash recovery, archiving and streaming all read the same WAL segment files.",
                "recovery", vw, vh, s)


# ------------------------------------------------------------------ FIG 22
def fig22():
    vw, vh = 1016, 470
    cols = [("heap pages · tuples", ""), ("B-tree pages", ""), ("FSM", ""), ("visibility map", ""), ("TOAST values", ""),
            ("WAL records", ""), ("pg_control", ""), ("files on disk", "")]
    tools = [("pageinspect", [1, 1, 1, 0, 1, 0, 0, 0], "bt_multi_page_stats: 16+"),
             ("pg_visibility", [0, 0, 0, 1, 0, 0, 0, 0], ""),
             ("pg_freespacemap", [0, 0, 1, 0, 0, 0, 0, 0], ""),
             ("pg_column_size() · pg_column_compression()", [0, 0, 0, 0, 1, 0, 0, 0], ""),
             ("pg_walinspect", [0, 0, 0, 0, 0, 1, 0, 0], "15+"),
             ("pg_waldump (shell, offline)", [0, 0, 0, 0, 0, 1, 0, 0], ""),
             ("pg_controldata (shell)", [0, 0, 0, 0, 0, 0, 1, 0], ""),
             ("pg_relation_filepath()", [0, 0, 0, 0, 0, 0, 0, 1], "")]
    s = eyebrow(32, 44, "which tool reads which on-disk structure — every one of them reads, none of them writes")
    x0, y0, lw, cw, rh = 32, 120, 260, 86, 36
    for j, (c, _) in enumerate(cols):
        x = x0 + lw + j * cw + cw / 2
        s += f'<text x="{x}" y="{y0 - 22}" transform="rotate(-18 {x} {y0 - 22})" font-size="8.5" font-weight="600" font-family="{MONO}" fill="{INK}" text-anchor="middle">{c}</text>'
    for i, (t, marks, ver) in enumerate(tools):
        y = y0 + i * rh
        s += f'<line x1="{x0}" y1="{y + rh}" x2="{x0 + lw + len(cols) * cw}" y2="{y + rh}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0, y + 20, t, size=9, fill=INK, anchor="start", weight="600")
        if ver:
            s += mono(x0, y + 31, ver, size=7, fill=ACCENT, anchor="start")
        for j, m in enumerate(marks):
            cx = x0 + lw + j * cw + cw / 2
            if m:
                s += f'<circle cx="{cx}" cy="{y + 17}" r="5.5" fill="{INK}" fill-opacity="0.75"/>'
            else:
                s += f'<circle cx="{cx}" cy="{y + 17}" r="5.5" fill="none" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="2,2"/>'
    s += note(32, y0 + len(tools) * rh + 20, "pageinspect reads TOAST chunks as ordinary heap pages of the TOAST table; on 18, page headers also carry a checksum by default")
    s += legend(y0 + len(tools) * rh + 46, vw, [("reads it", INK, "dot"), ("version note", ACCENT, "line")])
    return emit("22", "tooling-map", "Which tool reads which structure",
                "The inspection toolkit, against the on-disk structures in this post.",
                "implementation", vw, vh, s)


ALL = {"12": fig12, "13": fig13, "14": fig14, "15": fig15, "16": fig16, "17": fig17,
       "18": fig18, "19": fig19, "21": fig21, "22": fig22}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
