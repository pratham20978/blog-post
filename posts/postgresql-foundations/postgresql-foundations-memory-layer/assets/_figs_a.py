#!/usr/bin/env python3
"""Figures 01-11 for postgresql-foundations-memory-layer. Every number is from lab/captures.md
or the research ledger; nothing here is plotted from a formula."""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, SANS, SERIF, alabel, box, cell, elbow, emit,
                    eyebrow, elbow_hvh, hline, legend, masked, mono, node, tag,
                    txt, vline)

SER1, SER2 = "#7c8f6f", "#5e7a9b"


# ------------------------------------------------------------------ helpers
def hbar(x, y, w, h, fill=INK, opacity=0.14, stroke=None, rx=2):
    st = f' stroke="{stroke}" stroke-width="0.8"' if stroke else ""
    return (f'<rect x="{x}" y="{y}" width="{max(w, 0.5)}" height="{h}" rx="{rx}" fill="{fill}" '
            f'fill-opacity="{opacity}"{st}/>')


def lane(x, y1, y2, label):
    s = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="2,3"/>'
    s += box(x - 62, y1 - 30, 124, 26, fill="#ffffff", stroke=INK, rx=4)
    s += txt(x, y1 - 12, label, size=10, weight="600")
    return s


def msg(x1, x2, y, label, accent=False, dash=None, sub=None):
    col = ACCENT if accent else MUTED
    m = "arrow-accent" if accent else "arrow"
    s = hline(x1, x2 - 4 if x2 > x1 else x2 + 4, y, stroke=col, marker=m, dash=dash)
    s += masked((x1 + x2) / 2, y - 6, label, size=8, fill=ACCENT if accent else INK)
    if sub:
        s += masked((x1 + x2) / 2, y + 14, sub, size=7, fill=SOFT)
    return s


def selfmsg(x, y, label, accent=False):
    col = ACCENT if accent else MUTED
    d = f"M {x} {y} H {x + 36} V {y + 18} H {x + 4}"
    s = f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1" marker-end="url(#{"arrow-accent" if accent else "arrow"})"/>'
    s += masked(x + 48, y + 12, label, size=8, fill=ACCENT if accent else INK, anchor="start")
    return s


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 312
    s = eyebrow(32, 44, "the three layers, and where this post sits")
    layers = [
        ("memory layer", "shared buffers · WAL buffers · per-process memory · the rest of shared memory", True, "part 1 · this post"),
        ("process layer", "postmaster · backends · checkpointer · background writer · WAL writer · autovacuum", False, "part 2"),
        ("storage layer", "heap files · indexes · visibility map · WAL segments · pg_xact", False, "part 3"),
    ]
    y = 72
    for name, sub, focal, part in layers:
        s += box(32, y, 952, 62, fill=ACCENT_TINT if focal else "#ffffff", stroke=ACCENT if focal else INK)
        s += txt(56, y + 27, name, size=14, weight="600", fill=ACCENT if focal else INK, anchor="start", family=SANS)
        s += mono(56, y + 47, sub, size=9, fill=MUTED, anchor="start")
        s += tag(864, y + 8, part, stroke=ACCENT if focal else MUTED, w=104)
        y += 74
    s += mono(32, y + 14, "each layer reads the one below it; nothing in this post is scheduled (part 2) or written to a file format (part 3)",
              size=8, fill=SOFT, anchor="start", track="0.04em")
    return emit("01", "three-layers", "The three layers of a PostgreSQL server",
                "Memory, process, storage. This post stays in the top layer and names the boundary where it stops.",
                "the series", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 560
    s = eyebrow(32, 44, "one server, three pools, and two layers it does not own")
    # outer server box
    s += box(32, 64, 952, 330, fill="rgba(45,49,66,0.02)", stroke="rgba(45,49,66,0.35)", rx=8, dash="4,3")
    s += eyebrow(48, 84, "one postgresql server (one data directory, one postmaster)")
    # shared memory region
    s += box(48, 100, 920, 128, fill="#ffffff", stroke=INK, rx=6)
    s += eyebrow(64, 120, "shared memory — mapped once, by every process")
    s += node(72, 134, 300, 72, "shared buffers", "128 MB · 16,384 pages of 8 KB", kind="focal", tagtext="pool 1")
    s += node(396, 134, 260, 72, "WAL buffers", "4 MB · shared_buffers / 32", kind="backend", tagtext="pool 2")
    s += node(680, 134, 272, 72, "everything else", "15 MB · locks · procs · SLRUs · stats", kind="store", tagtext="shared")
    # backends
    bx = [72, 300, 528]
    for i, x in enumerate(bx):
        s += box(x, 268, 204, 108, fill="#ffffff", stroke=INK)
        s += tag(x + 8, 274, "one process", stroke=INK)
        s += txt(x + 102, 310, f"backend {i + 1}", size=12, weight="600")
        s += mono(x + 102, 330, "local memory", size=9, fill=INK, weight="500")
        s += mono(x + 102, 346, "work_mem · temp_buffers · contexts", size=8, fill=SOFT)
        s += mono(x + 102, 362, "pool 3 · private", size=8, fill=ACCENT, track="0.06em")
        s += vline(x + 102, 264, 232, stroke=MUTED, marker="arrow")
    s += node(760, 268, 192, 108, "postmaster", "forks a backend per connection", kind="external")
    s += mono(856, 362, "+ checkpointer · bgwriter · wal writer", size=7, fill=SOFT)
    s += mono(856, 254, "each process maps the same region", size=8, fill=SOFT, track="0.06em")
    # kernel and disk
    s += box(32, 410, 952, 46, fill="rgba(79,93,117,0.08)", stroke=SOFT, rx=6)
    s += txt(56, 438, "kernel page cache", size=12, weight="600", anchor="start")
    s += mono(720, 438, "copies of the same file pages · not sized or seen by PostgreSQL", size=8, fill=MUTED, anchor="middle")
    s += box(32, 476, 952, 46, fill="rgba(45,49,66,0.05)", stroke=MUTED, rx=6)
    s += txt(56, 504, "disk", size=12, weight="600", anchor="start")
    s += mono(720, 504, "heap and index files · WAL segments · pg_xact", size=8, fill=MUTED, anchor="middle")
    # arrows shared buffers <-> kernel <-> disk, WAL -> disk
    s += vline(222, 390, 406, stroke=INK, marker="arrow")
    s += vline(236, 406, 390, stroke=INK, marker="arrow")
    s += masked(300, 402, "pread / write, 8 KB at a time", size=8, fill=INK, anchor="start")
    s += vline(222, 456, 472, stroke=MUTED, marker="arrow")
    s += vline(236, 472, 456, stroke=MUTED, marker="arrow")
    s += vline(526, 390, 472, stroke=ACCENT, marker="arrow-accent")
    s += masked(540, 470, "WAL: written at every commit, fsync'd", size=8, fill=ACCENT, anchor="start")
    s += legend(540, vw, [("the pool this post spends most time in", ACCENT, "box"), ("shared by all processes", INK, "box"),
                          ("private to one process", MUTED, "box")])
    return emit("02", "three-pools", "The three pools",
                "Shared buffers and WAL buffers live in one region every process maps; working memory is per process; the kernel cache underneath is a fourth pool PostgreSQL cannot see.",
                "the problem", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 388
    s = eyebrow(32, 44, "pg_shmem_allocations on the lab server: 57 allocations, 149,495,808 bytes")
    total = 149_495_808
    bb = 134_221_824
    x0, w = 32, 952
    y = 72
    s += mono(32, y - 6, "143 MB, to scale", size=8, fill=SOFT, anchor="start", track="0.10em")
    wb = w * bb / total
    s += hbar(x0, y, wb, 40, fill=ACCENT, opacity=0.16, stroke=ACCENT)
    s += txt(x0 + wb / 2, y + 25, "Buffer Blocks — 128 MB — 16,384 pages × 8,192 bytes", size=11, fill=ACCENT, weight="600")
    s += hbar(x0 + wb, y, w - wb, 40, fill=INK, opacity=0.10, stroke=MUTED)
    s += mono(x0 + wb + (w - wb) / 2, y + 24, "15 MB", size=9, fill=INK, weight="600")
    # zoom marker under the 15 MB piece
    s += f'<path d="M {x0 + wb + (w - wb) / 2} {y + 44} V {y + 60}" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += mono(x0 + wb + (w - wb) / 2, y + 74, "zoomed below", size=7, fill=SOFT, track="0.10em")
    # second bar: the 15 MB
    rest = 15_273_984
    parts = [("<anonymous>", 4_777_344, MUTED), ("XLOG Ctl (WAL buffers)", 4_208_256, ACCENT),
             ("free", 1_875_456, SOFT), ("descriptors", 1_048_576, INK),
             ("CommitTs", 534_016, SER2), ("Xact", 529_152, SER2), ("Checkpointer", 721_024, SER1),
             ("stats", 277_888, MUTED), ("Subtrans", 267_008, SER2), ("IO CVs", 262_144, INK),
             ("other 46", 773_120, SOFT)]
    assert sum(p[1] for p in parts) == rest, sum(p[1] for p in parts)
    y2 = y + 100
    s += mono(32, y2 - 6, "the other 15 MB, to scale (56 allocations)", size=8, fill=SOFT, anchor="start", track="0.10em")
    x = x0
    for name, size, col in parts:
        pw = w * size / rest
        focal = col == ACCENT
        s += hbar(x, y2, pw, 40, fill=col, opacity=0.18 if focal else 0.12, stroke=col)
        if pw > 60:
            s += mono(x + pw / 2, y2 + 18, name, size=8, fill=ACCENT if focal else INK, weight="600" if focal else "500")
            s += mono(x + pw / 2, y2 + 32, f"{size / 1024 / 1024:.2f} MB", size=8, fill=ACCENT if focal else MUTED)
        x += pw
    # callouts for small ones
    s += mono(32, y2 + 66, "unlabelled, left to right: CommitTs 0.51 · Xact 0.50 · Checkpointer 0.69 · stats 0.27 · Subtrans 0.25 · IO condition variables 0.25 · 46 others 0.74 MB",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += mono(32, y2 + 84, "Buffer Descriptors = 1,048,576 bytes = 16,384 × 64 — one cache line per buffer", size=8, fill=INK, anchor="start", track="0.02em")
    s += legend(336, vw, [("page storage", ACCENT, "box"), ("WAL buffer ring", ACCENT, "line"),
                          ("transaction-status caches", SER2, "box"), ("bookkeeping", INK, "box")])
    return emit("03", "shared-memory-map", "What the postmaster carved out at startup",
                "128 MB of the 143 MB is page storage. The other 15 MB is bookkeeping, and the largest piece of it is the WAL buffer ring.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 440
    s = eyebrow(32, 44, "where the 7,693 pages of orders are, after each step of the lab")
    steps = [("restart + drop cache", 0, 0), ("cold sequential scan", 7693, 32),
             ("pg_prewarm('orders')", 7693, 7693), ("prewarm a bigger table", 7693, 320)]
    levels = ["shared buffers", "kernel cache", "disk"]
    x0, colw = 176, 200
    rowy = [96, 196, 296]
    for i, lab in enumerate(levels):
        s += txt(32, rowy[i] + 40, lab, size=11, weight="600", anchor="start")
        s += mono(32, rowy[i] + 56, ["16,384 slots", "not PostgreSQL's", "the file"][i], size=8, fill=SOFT, anchor="start")
        s += f'<line x1="{x0 - 8}" y1="{rowy[i] + 78}" x2="{vw - 32}" y2="{rowy[i] + 78}" stroke="{RULE}" stroke-width="0.8"/>'
    maxw = colw - 32
    for j, (name, kern, shared) in enumerate(steps):
        x = x0 + j * colw
        s += mono(x + maxw / 2, 76, name, size=8, fill=INK, weight="600", track="0.04em")
        vals = [shared, kern, 7693]
        for i, v in enumerate(vals):
            y = rowy[i] + 8
            frac = v / 7693
            focal = i == 0 and v > 0
            s += hbar(x, y, maxw, 56, fill=INK, opacity=0.04, stroke="rgba(45,49,66,0.18)")
            if v:
                s += hbar(x, y, maxw * frac, 56, fill=ACCENT if focal else (MUTED if i == 1 else INK),
                          opacity=0.22 if focal else 0.14, stroke=ACCENT if focal else None)
            s += mono(x + maxw / 2, y + 34, f"{v:,} pages" if v else "0", size=10, fill=ACCENT if focal else INK, weight="600")
    s += mono(32, 398, "the ring keeps 32 pages of a 7,693-page scan; only pg_prewarm fills the pool, and only a bigger table empties it again (10,048 evictions)",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += legend(416, vw, [("in shared buffers", ACCENT, "box"), ("in the kernel cache", MUTED, "box"), ("on disk (always)", INK, "box")])
    return emit("04", "three-levels", "The same 60 MB, four times",
                "PostgreSQL 16.2, default settings. Each column is one step of the lab; each row is one place a page can be.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 262
    s = eyebrow(32, 44, "the one comparison that decides the scan strategy: pages > NBuffers / 4 ?")
    x0, w = 64, 900
    y = 150
    N = 16384
    def X(p):
        return x0 + w * p / N
    s += f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for p in (0, 4096, 8192, 12288, 16384):
        s += f'<line x1="{X(p)}" y1="{y - 4}" x2="{X(p)}" y2="{y + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        s += mono(X(p), y + 20, f"{p:,}", size=8, fill=SOFT)
    s += eyebrow(x0 + w, y + 38, "pages · pool = 16,384", anchor="end")
    # bars
    s += hbar(x0, y - 44, X(710) - x0, 22, fill=INK, opacity=0.14, stroke=INK)
    s += mono(X(710) + 8, y - 29, "customers · 710 pages · normal strategy, cached whole", size=9, fill=INK, anchor="start", weight="500")
    s += hbar(x0, y - 78, X(7693) - x0, 22, fill=ACCENT, opacity=0.16, stroke=ACCENT)
    s += mono(X(7693) + 8, y - 63, "orders · 7,693 pages · ring", size=9, fill=ACCENT, anchor="start", weight="600")
    # threshold
    s += f'<line x1="{X(4096)}" y1="{y - 86}" x2="{X(4096)}" y2="{y + 44}" stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="4,3"/>'
    s += masked(X(4096), y + 58, "NBuffers / 4 = 4,096 pages = 32 MB", size=8, fill=ACCENT)
    s += mono(32, 236, "both tables fit in the pool; only the one under the threshold is allowed to use it",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    return emit("05", "the-threshold", "Two tables against one threshold",
                "initscan compares the table's page count with a quarter of shared_buffers. Over it: a 32-buffer ring. Under it: the pool.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 500
    s = eyebrow(32, 44, "one buffer = a 64-byte descriptor + an 8,192-byte page, plus one hash-table entry")
    # hash table at top
    s += node(32, 68, 400, 60, "buffer lookup table", "shared hash · tag → buffer id · 128 partition locks", kind="store")
    s += mono(232, 148, "hash(tag) picks the partition; a lookup takes it shared, a re-tag takes it exclusive", size=8, fill=SOFT)
    # descriptor strip, to scale: 64 bytes -> 640 px
    dx, dy, scale = 32, 200, 10
    fields = [("tag", 20, "spcOid · dbOid · relNumber · forkNum · blockNum", INK),
              ("buf_id", 4, "", MUTED), ("state", 4, "", ACCENT), ("waiter", 4, "", MUTED),
              ("freeNext", 4, "", MUTED), ("content_lock", 16, "LWLock · shared to read · exclusive to write", INK),
              ("pad", 12, "to 64", SOFT)]
    s += mono(dx, dy - 10, "BufferDesc — 64 bytes, drawn to scale (1 byte = 10 px)", size=8, fill=SOFT, anchor="start", track="0.10em")
    x = dx
    for name, nbytes, sub, col in fields:
        fw = nbytes * scale
        focal = col == ACCENT
        s += box(x, dy, fw, 44, fill=ACCENT_TINT if focal else ("#ffffff" if col != SOFT else "rgba(45,49,66,0.04)"),
                 stroke=col if col != SOFT else "rgba(45,49,66,0.25)", rx=3)
        s += mono(x + fw / 2, dy + 20, name, size=9 if fw > 50 else 7, fill=col if col != SOFT else SOFT, weight="600")
        s += mono(x + fw / 2, dy + 34, f"{nbytes} B", size=7, fill=SOFT)
        if sub:
            s += mono(x + fw / 2, dy + 60, sub, size=7, fill=MUTED)
        x += fw
    # state word breakdown
    sy = 300
    s += f'<path d="M {dx + 240} {dy + 44} L {dx + 240} {sy - 8} M {dx + 280} {dy + 44} L {dx + 280} {sy - 8}" stroke="{ACCENT}" stroke-width="0.8" stroke-dasharray="3,3" fill="none"/>'
    s += mono(dx, sy - 12, "the state word — 32 bits, one atomic integer, three facts", size=8, fill=ACCENT, anchor="start", track="0.10em")
    bits = [("refcount (pins)", 18, "MAX_BACKENDS = 2¹⁸ − 1", "middle"), ("usage count", 4, "0 … 5", "middle"), ("10 flags", 10, "LOCKED · DIRTY · VALID · IO_IN_PROGRESS · …", "end")]
    x = dx
    bw = 640 / 32
    for name, n, sub, anc in bits:
        fw = n * bw
        s += box(x, sy, fw, 40, fill=ACCENT_TINT, stroke=ACCENT, rx=3)
        s += mono(x + fw / 2, sy + 18, name, size=9, fill=ACCENT, weight="600")
        s += mono(x + fw / 2, sy + 32, f"{n} bits", size=7, fill=SOFT)
        s += mono(x + fw if anc == "end" else x + fw / 2, sy + 56, sub, size=7, fill=MUTED, anchor=anc)
        x += fw
    s += mono(dx, sy + 82, "pinning = one compare-and-swap on this word; the header spinlock is the LOCKED bit, not a separate field (9.6, commit 48354581)",
              size=8, fill=INK, anchor="start", track="0.02em")
    # page block on the right
    px, py = 720, 200
    s += box(px, py, 264, 232, fill="#ffffff", stroke=INK, rx=6)
    s += txt(px + 132, py + 30, "the page", size=13, weight="600")
    s += mono(px + 132, py + 48, "8,192 bytes · one block of one fork", size=8, fill=SOFT)
    s += box(px + 16, py + 66, 232, 18, fill="rgba(45,49,66,0.10)", stroke="rgba(45,49,66,0.30)", rx=2)
    s += mono(px + 132, py + 79, "24-byte header · pd_lsn first", size=7, fill=INK)
    s += box(px + 16, py + 90, 232, 22, fill="rgba(45,49,66,0.05)", stroke="rgba(45,49,66,0.30)", rx=2)
    s += mono(px + 132, py + 105, "line pointers →", size=7, fill=MUTED)
    s += box(px + 16, py + 118, 232, 40, fill="#ffffff", stroke="rgba(45,49,66,0.30)", rx=2, dash="3,3")
    s += mono(px + 132, py + 142, "free space (the hole)", size=7, fill=SOFT)
    s += box(px + 16, py + 164, 232, 50, fill="rgba(45,49,66,0.05)", stroke="rgba(45,49,66,0.30)", rx=2)
    s += mono(px + 132, py + 193, "← tuples", size=7, fill=MUTED)
    s += mono(px + 132, py + 250, "128 × the descriptor, in a separate array", size=8, fill=SOFT)
    s += hline(dx + 640 + 8, px - 4, dy + 22, stroke=MUTED)
    s += masked(696, dy - 18, "buf_id = index into Buffer Blocks", size=7, fill=SOFT)
    s += legend(476, vw, [("identity and locks", INK, "box"), ("the atomic state word", ACCENT, "box"), ("page bytes", MUTED, "box")])
    return emit("06", "buffer-anatomy", "What a buffer actually is",
                "The descriptor is what the clock sweep and the pins touch; the page is what queries read. They live in two arrays, joined by an index.",
                "shared buffers", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 640
    s = eyebrow(32, 44, "ReadBuffer on PostgreSQL 16.2 — the hit path and the miss path, at function level")
    xs = {"be": 150, "tab": 352, "desc": 562, "wal": 752, "file": 920}
    names = {"be": "backend", "tab": "lookup table", "desc": "buffer descriptor", "wal": "WAL", "file": "file (smgr/md)"}
    # HIT
    s += tag(32, 72, "hit", stroke=INK, w=40)
    for k, x in xs.items():
        s += lane(x, 110, 216, names[k])
    s += msg(xs["be"], xs["tab"], 132, "BufTableLookup(tag) — shared partition lock")
    s += msg(xs["tab"], xs["be"], 158, "buffer id", dash="3,3")
    s += msg(xs["be"], xs["desc"], 184, "PinBuffer: CAS refcount+1, usage+1 (≤5)", accent=True)
    s += msg(xs["desc"], xs["be"], 206, "page pointer — no I/O, no header lock", dash="3,3")
    # MISS
    s += tag(32, 244, "miss", stroke=ACCENT, w=48)
    for k, x in xs.items():
        s += lane(x, 282, 600, names[k])
    s += msg(xs["be"], xs["tab"], 304, "BufTableLookup(tag) → not found")
    s += selfmsg(xs["be"], 322, "StrategyGetBuffer: free list, else clock sweep → victim")
    s += msg(xs["be"], xs["desc"], 366, "pin victim; is it dirty?")
    s += msg(xs["be"], xs["wal"], 392, "FlushBuffer → XLogFlush(victim's pd_lsn)", accent=True, sub="the write-ahead rule")
    s += msg(xs["be"], xs["file"], 424, "smgrwrite(victim page)", sub="only if dirty")
    s += msg(xs["be"], xs["tab"], 456, "BufTableDelete(old) · BufTableInsert(new) — exclusive lock", sub="tag valid · usage = 1 · not yet VALID")
    s += msg(xs["be"], xs["file"], 494, "smgrread → mdread → pread(8 KB)", accent=True, sub="kernel cache or disk — PostgreSQL cannot tell")
    s += msg(xs["file"], xs["be"], 526, "bytes", dash="3,3")
    s += msg(xs["be"], xs["desc"], 552, "TerminateBufferIO: set BM_VALID, wake waiters")
    s += msg(xs["desc"], xs["be"], 578, "page pointer", dash="3,3")
    s += legend(616, vw, [("no lock, one atomic op", INK, "line"), ("the expensive steps", ACCENT, "line"), ("return", MUTED, "line")])
    return emit("07", "hit-and-miss", "A hit and a miss",
                "A hit is a hash lookup and one compare-and-swap. A miss may flush WAL and write someone else's page before it can read its own.",
                "shared buffers", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 484
    s = eyebrow(32, 44, "the clock sweep on eight buffers — usage counts, one pinned buffer, one pass")
    panels = [
        ("start: the hand is at buffer 1", [3, 0, 1, 5, 0, 2, 1, 0], 0, None),
        ("after four steps: counts lowered, the pinned buffer untouched", [2, 0, 0, 4, 0, 2, 1, 0], 4, None),
        ("buffer 5 is unpinned with count 0 — the victim", [2, 0, 0, 4, 0, 2, 1, 0], 4, 4),
    ]
    cw, gap = 96, 12
    x0 = 120
    y = 82
    for title, counts, hand, victim in panels:
        s += mono(32, y - 8, title, size=8, fill=INK, anchor="start", weight="500", track="0.04em")
        for i, c in enumerate(counts):
            x = x0 + i * (cw + gap)
            pinned = i == 1
            is_victim = victim == i
            fill = ACCENT_TINT if is_victim else ("rgba(45,49,66,0.10)" if pinned else "#ffffff")
            stroke = ACCENT if is_victim else (INK if pinned else "rgba(45,49,66,0.30)")
            s += box(x, y, cw, 54, fill=fill, stroke=stroke, rx=4)
            s += mono(x + cw / 2, y + 22, f"usage {c}", size=10, fill=ACCENT if is_victim else INK, weight="600")
            s += mono(x + cw / 2, y + 40, "pinned" if pinned else (f"buffer {i + 1}"), size=8, fill=INK if pinned else SOFT)
        # hand
        hx = x0 + hand * (cw + gap) + cw / 2
        s += f'<path d="M {hx} {y + 70} L {hx - 6} {y + 82} L {hx + 6} {y + 82} Z" fill="{ACCENT}"/>'
        s += mono(hx, y + 96, "hand", size=7, fill=ACCENT, track="0.10em")
        y += 118
    s += mono(32, y - 2, "rule: pinned → skip · usage > 0 → subtract one, skip · usage 0 → victim. No list is reordered; the hand is the only shared state.",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += legend(460, vw, [("pinned — skipped, not decremented", INK, "box"), ("the victim", ACCENT, "box")])
    return emit("08", "clock-sweep-trace", "The clock sweep, by hand",
                "Eight buffers, one pass. Buffer 4 at usage 5 will survive four more passes; buffer 3 at usage 1 lasted one.",
                "the clock sweep", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "pg_buffercache_usage_counts() before and after prewarming a table that does not fit — log scale")
    before = [14956, 263, 12, 85, 185, 883]
    after = [5148, 10146, 190, 765, 1, 134]
    x0, y0, w, h = 96, 84, 860, 220
    def ty(v):
        return y0 + h - (math.log10(v + 1) / math.log10(24000)) * h
    for v in (1, 10, 100, 1000, 10000):
        yy = ty(v)
        s += f'<line x1="{x0}" y1="{yy}" x2="{x0 + w}" y2="{yy}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0 - 8, yy + 3, f"{v:,}", size=8, fill=SOFT, anchor="end")
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += eyebrow(x0, y0 - 26, "buffers (log scale)", anchor="start")
    gw = w / 6
    for i in range(6):
        gx = x0 + i * gw
        for j, (v, col, lab) in enumerate(((before[i], MUTED, "before"), (after[i], ACCENT, "after"))):
            bx = gx + 24 + j * 44
            top = ty(v)
            s += hbar(bx, top, 36, y0 + h - top, fill=col, opacity=0.18 if j else 0.12, stroke=col)
            s += mono(bx + 18, top - 6, f"{v:,}", size=8, fill=col, weight="600")
        s += mono(gx + gw / 2, y0 + h + 18, f"usage {i}", size=9, fill=INK, weight="500")
    s += mono(32, 346, "before: an almost empty pool (14,956 at zero) with customers at 5 · after: 10,146 prewarmed pages at 1, the survivors lowered from 5 towards 3, almost no zeros left",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += legend(376, vw, [("before the sweep", MUTED, "box"), ("after 10,048 evictions", ACCENT, "box")])
    return emit("09", "usage-histogram", "The sweep's fingerprint",
                "PostgreSQL 16.2, 16,384 buffers. Log scale, because the pool went from mostly empty to mostly usage-count 1.",
                "the clock sweep", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 340
    s = eyebrow(32, 44, "twenty years of one data structure — events in order, not to a time scale")
    events = [
        ("8.0", "ARC replaces LRU", "2005-01-19", False),
        ("8.0.2", "2Q replaces ARC — patent", "2005-04-07", False),
        ("8.1", "the clock sweep", "2005-11-08", True),
        ("8.3", "rings for bulk scans", "", False),
        ("9.6", "lock-free buffer header", "2016-09-29", False),
        ("14", "I/O locks → condition variables", "", False),
        ("16", "pg_stat_io · vacuum ring GUC", "2023-09-14", False),
        ("17", "vacuum ring 2 MB · SLRU banks", "2024-09-26", False),
        ("18", "AIO reads · ring grows", "2025-09-25", False),
        ("19", "free list removed", "planned 2026-09", False),
    ]
    x0, w = 80, 860
    y = 176
    n = len(events)
    step = w / (n - 1)
    s += f'<line x1="{x0 - 30}" y1="{y}" x2="{x0 + w + 30}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    # year-gap markers
    for i in (3, 4, 5):
        gx = x0 + (i + 0.5) * step
        s += f'<path d="M {gx - 5} {y + 7} L {gx + 1} {y - 7} M {gx + 1} {y + 7} L {gx + 7} {y - 7}" stroke="{PAPER}" stroke-width="5" fill="none"/>'
        s += f'<path d="M {gx - 5} {y + 7} L {gx + 1} {y - 7} M {gx + 1} {y + 7} L {gx + 7} {y - 7}" stroke="{RULE_SOLID}" stroke-width="1" fill="none"/>'
    for i, (ver, what, date, focal) in enumerate(events):
        x = x0 + i * step
        col = ACCENT if focal else INK
        s += f'<circle cx="{x}" cy="{y}" r="{6 if focal else 4}" fill="{col if focal else PAPER}" stroke="{col}" stroke-width="1.2"/>'
        up = i % 2 == 0
        yy = y - 58 if up else y + 62
        s += f'<line x1="{x}" y1="{y + (-8 if up else 8)}" x2="{x}" y2="{yy + (34 if up else -26)}" stroke="{col}" stroke-width="0.8" stroke-opacity="0.5"/>'
        s += mono(x, yy, ver, size=11, fill=col, weight="600")
        s += mono(x, yy + 14, what, size=7, fill=col if focal else MUTED)
        s += mono(x, yy + 26, date if date else "(version only)", size=7, fill=SOFT)
    s += mono(32, 306, "the policy has been the clock sweep since 8.1; everything after is about locks, rings and what happens on a miss · break marks: years skipped",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    return emit("10", "replacement-timeline", "From LRU to the clock sweep",
                "Three replacement policies in one year, then twenty years of the same one. Dates are release dates from the release notes; versions without a date are cited to the source tree.",
                "the clock sweep", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 452
    s = eyebrow(32, 44, "a 32-buffer ring cycling through a 7,693-page scan — one ring per process")
    # big ring on the left
    cx, cy, r = 240, 240, 130
    n = 32
    for i in range(n):
        a = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        dirty = i == 9
        cur = i == 3
        fill = ACCENT_TINT if cur else ("rgba(45,49,66,0.12)" if dirty else "#ffffff")
        stroke = ACCENT if cur else (INK if dirty else "rgba(45,49,66,0.35)")
        s += f'<rect x="{x - 9}" y="{y - 9}" width="18" height="18" rx="2" fill="{fill}" stroke="{stroke}" stroke-width="{1.2 if cur or dirty else 0.8}"/>'
    s += txt(cx, cy - 8, "32 slots", size=14, weight="600")
    s += mono(cx, cy + 10, "256 KB", size=9, fill=SOFT)
    s += mono(cx, cy + 26, "pages 1 … 7,693 pass through", size=8, fill=MUTED)
    # incoming pages arrow
    s += hline(32, cx - r - 16, cy, stroke=MUTED)
    s += masked(70, cy - 8, "next page", size=7, fill=SOFT)
    # the dirty slot ejected
    ax = cx + r * math.cos(-math.pi / 2 + 2 * math.pi * 9 / n)
    ay = cy + r * math.sin(-math.pi / 2 + 2 * math.pi * 9 / n)
    s += f'<path d="M {ax + 12} {ay} H {ax + 80}" fill="none" stroke="{INK}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += masked(ax + 92, ay - 8, "dirtied → needs a WAL flush → ejected to the pool; a fresh victim replaces it", size=7, fill=INK, anchor="start")
    s += mono(32, 400, "a slot is reused only while its buffer is unpinned and at usage ≤ 1; otherwise someone else wanted that page and the ring lets it go",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    # three mini rings on the right
    labels = ["leader", "worker 1", "worker 2"]
    for k, lab in enumerate(labels):
        mx, my, mr = 620 + k * 128, 140, 44
        for i in range(16):
            a = -math.pi / 2 + 2 * math.pi * i / 16
            x, y = mx + mr * math.cos(a), my + mr * math.sin(a)
            s += f'<rect x="{x - 4}" y="{y - 4}" width="8" height="8" rx="1" fill="#ffffff" stroke="rgba(45,49,66,0.35)" stroke-width="0.8"/>'
        s += mono(mx, my + 4, "32", size=10, fill=INK, weight="600")
        s += mono(mx, my + 66, lab, size=8, fill=INK, track="0.08em")
    s += txt(748, 316, "32 + 32 + 32 = 96 pages left behind", size=11, weight="600", fill=ACCENT)
    s += mono(748, 334, "the lab's parallel scan: shared hit=64 read=7629, and 160 buffers of orders afterwards", size=8, fill=MUTED)
    s += mono(748, 350, "(32 + 32 from the two earlier scans + 96)", size=8, fill=SOFT)
    s += legend(428, vw, [("the slot being filled", ACCENT, "box"), ("a dirtied slot", INK, "box"), ("clean slot", MUTED, "box")])
    return emit("11", "the-ring", "The ring",
                "A bulk-read strategy is a private circle of 32 buffers. Three processes scanning in parallel run three rings, which is the 96 the lab measured.",
                "rings", vw, vh, s)


ALL = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06,
       "07": fig07, "08": fig08, "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
