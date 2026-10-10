#!/usr/bin/env python3
"""Figures 12-22 for postgresql-foundations-memory-layer. Numbers from lab/captures.md and the ledger."""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, SANS, SERIF, alabel, box, cell, elbow, emit,
                    eyebrow, elbow_hvh, hline, legend, masked, mono, node, tag,
                    txt, vline)
from _figs_a import hbar, lane, msg, selfmsg

SER1, SER2 = "#7c8f6f", "#5e7a9b"


# ------------------------------------------------------------------ FIG 12
def wrap(text, width):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > width and cur:
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd).strip()
    if cur:
        lines.append(cur)
    return lines


def fig12():
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "the three rings on postgresql 16.2, and what changed in 17 and 18")
    cols = [("ring", 32), ("size · buffers", 150), ("who uses it", 300), ("dirty pages", 604), ("17 / 18", 800)]
    y = 76
    for name, x in cols:
        s += eyebrow(x, y, name)
    s += f'<line x1="32" y1="{y + 8}" x2="{vw - 32}" y2="{y + 8}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    rows = [
        ("bulk read", "256 KB · 32", "sequential scans of tables over NBuffers / 4", "ejected from the ring, so a WAL flush is never paid", "18: grows by io_combine_limit × effective_io_concurrency (2,304 KB with defaults)", True),
        ("bulk write", "16 MB · 2,048", "COPY FROM · CREATE TABLE AS · REFRESH MATERIALIZED VIEW · table rewrites", "kept; WAL flushed as needed", "unchanged", False),
        ("vacuum", "256 KB · 32", "VACUUM · ANALYZE · autovacuum, sized by vacuum_buffer_usage_limit", "kept; WAL flushed as needed", "17: default 2 MB · 16+: BUFFER_USAGE_LIMIT per call", False),
    ]
    y += 24
    for ring, size, who, dirty, ver, focal in rows:
        col = ACCENT if focal else INK
        s += box(32, y, 952, 62, fill=ACCENT_TINT if focal else "#ffffff", stroke=col if focal else "rgba(45,49,66,0.30)", rx=4)
        s += txt(48, y + 36, ring, size=12, weight="600", fill=col, anchor="start")
        s += mono(150, y + 36, size, size=10, fill=col, anchor="start", weight="600")
        for i, line in enumerate(wrap(who, 58)[:3]):
            s += mono(300, y + 24 + i * 13, line, size=8, fill=INK, anchor="start")
        for i, line in enumerate(wrap(dirty, 36)[:3]):
            s += mono(604, y + 24 + i * 13, line, size=8, fill=MUTED, anchor="start")
        for i, line in enumerate(wrap(ver, 40)[:3]):
            s += mono(800, y + 24 + i * 13, line, size=7, fill=SOFT, anchor="start")
        y += 72
    y += 8
    s += mono(32, y + 10, "every ring is capped at NBuffers / 8 (2,048 buffers here, so the bulk-write ring is exactly at its cap) · a ring slot is reused only while unpinned and at usage ≤ 1",
              size=8, fill=INK, anchor="start", track="0.02em")
    s += mono(32, y + 28, "a table qualifies for a ring when it has more than NBuffers / 4 pages: 4,096 pages = 32 MB on the default pool",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += legend(376, vw, [("the ring the worked example used", ACCENT, "box"), ("the other two", INK, "box")])
    return emit("12", "ring-sizes", "Three rings",
                "Sizes and users from freelist.c, heapam.c and the buffer README at REL_16_2; the 17 and 18 changes from the release notes and commit 15f0cb26.",
                "rings", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 600
    s = eyebrow(32, 44, "one update, from the heap page to the segment file")
    xs = {"be": 130, "pos": 330, "buf": 540, "ww": 740, "seg": 920}
    names = {"be": "backend", "pos": "insert position", "buf": "WAL buffers (4 MB)", "ww": "WAL writer", "seg": "segment file"}
    for k, x in xs.items():
        s += lane(x, 100, 540, names[k])
    s += selfmsg(xs["be"], 112, "modify the page in shared buffers; MarkBufferDirty (critical section)")
    s += msg(xs["be"], xs["pos"], 160, "reserve bytes: spinlock", sub="the one serialised step")
    s += msg(xs["pos"], xs["be"], 196, "start, end positions", dash="3,3")
    s += msg(xs["be"], xs["buf"], 222, "copy the record under 1 of 8 insertion locks", accent=True, sub="up to 8 backends copy at once")
    s += selfmsg(xs["be"], 246, "PageSetLSN(end position) — the page now says which WAL it depends on")
    s += msg(xs["be"], xs["buf"], 300, "COMMIT: XLogFlush(commit LSN)", accent=True)
    s += msg(xs["buf"], xs["seg"], 326, "write + fsync everything up to and beyond it", accent=True, sub="piggybacks any WAL already in the ring")
    s += msg(xs["seg"], xs["be"], 356, "durable — tell the client COMMIT", dash="3,3")
    # async / wal writer
    s += msg(xs["ww"], xs["seg"], 400, "every 200 ms: write, fsync", sub="wal_writer_delay · async commits")
    # buffers full path
    s += tag(32, 436, "ring full", stroke=INK, w=72)
    s += msg(xs["be"], xs["buf"], 462, "need a buffer still holding unwritten WAL?")
    s += msg(xs["buf"], xs["seg"], 490, "the inserter writes that buffer itself · wal_buffers_full++", sub="8,919 times during the lab's load")
    s += legend(576, vw, [("the write-ahead rule in motion", ACCENT, "line"), ("bookkeeping", INK, "line"), ("return", MUTED, "line")])
    return emit("13", "wal-insert-path", "How a record gets into WAL, and out again",
                "Reserve under a spinlock, copy under an insertion lock, flush at commit. The ring is written at every commit, which is why it stays small.",
                "wal buffers", vw, vh, s)


# ------------------------------------------------------------------ FIG 14
def fig14():
    vw, vh = 1016, 372
    s = eyebrow(32, 44, "pg_walinspect: the same one-column update, logged twice — bytes, to scale")
    x0 = 180
    sc = 0.09  # px per byte: 7,473 B = 673 px
    # first update
    y = 92
    s += txt(32, y + 21, "first update", size=12, weight="600", anchor="start")
    s += mono(32, y + 38, "right after CHECKPOINT", size=8, fill=SOFT, anchor="start")
    w_img = 7408 * sc
    w_hdr = 65 * sc
    w_hole = 784 * sc
    w_commit = 34 * sc
    s += hbar(x0, y, w_img, 34, fill=ACCENT, opacity=0.18, stroke=ACCENT)
    s += mono(x0 + w_img / 2, y + 21, "full-page image · 7,408 B", size=9, fill=ACCENT, weight="600")
    s += hbar(x0 + w_img, y, w_hdr, 34, fill=INK, opacity=0.25, stroke=INK)
    s += f'<rect x="{x0 + w_img + w_hdr}" y="{y}" width="{w_hole}" height="34" rx="2" fill="none" stroke="{SOFT}" stroke-width="0.8" stroke-dasharray="3,3"/>'
    s += mono(x0 + w_img + w_hdr + w_hole / 2, y + 21, "hole 784 B", size=7, fill=SOFT)
    s += hbar(x0 + w_img + w_hdr + w_hole + 6, y, w_commit, 34, fill=INK, opacity=0.25, stroke=INK)
    # leaders
    s += mono(x0, y + 52, "HOT_UPDATE record = 7,473 bytes = 7,408 image + 65 header and change", size=8, fill=ACCENT, anchor="start")
    s += mono(x0 + w_img + w_hdr + w_hole / 2, y + 52, "not logged: free space", size=7, fill=SOFT)
    s += mono(x0 + w_img + w_hdr + w_hole + 6 + w_commit + 6, y + 21, "COMMIT 34", size=7, fill=INK, anchor="start")
    s += mono(x0, y + 66, "total: 7,544 bytes", size=8, fill=INK, anchor="start", weight="600")
    # second update, to scale
    y = 196
    s += txt(32, y + 21, "second update", size=12, weight="600", anchor="start")
    s += mono(32, y + 38, "no checkpoint between", size=8, fill=SOFT, anchor="start")
    x = x0
    for b in (59, 70, 34):
        s += hbar(x, y, b * sc, 34, fill=INK, opacity=0.25, stroke=INK)
        x += b * sc + 2
    s += mono(x + 6, y + 21, "← to the same scale: 176 bytes", size=8, fill=INK, anchor="start", weight="600")
    # zoomed inset ×20
    zx, zsc = 420, 1.8
    s += mono(zx, y - 8, "zoomed ×20", size=7, fill=SOFT, anchor="start", track="0.10em")
    x = zx
    for name, b, col in (("PRUNE 59", 59, SER2), ("HOT_UPDATE 70", 70, INK), ("COMMIT 34", 34, INK)):
        w = b * zsc
        s += hbar(x, y, w, 34, fill=col, opacity=0.14, stroke=col)
        s += mono(x + w / 2, y + 21, name, size=8, fill=col, weight="600")
        x += w + 6
    s += mono(x0, y + 52, "three records, 163 bytes of content, 176 with alignment — 43× less than the first", size=8, fill=INK, anchor="start")
    s += mono(32, 300, "full_page_writes = on: the first change to a page after a checkpoint logs the page; recovery lays it down whole because an 8 KB disk write is not assumed atomic",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += legend(348, vw, [("page image", ACCENT, "box"), ("record headers and the change itself", INK, "box"), ("not written", SOFT, "box")])
    return emit("14", "full-page-image", "7,544 bytes versus 176",
                "PostgreSQL 16.2, customers block 30, fillfactor 90. Record lengths from pg_get_wal_records_info; the only difference between the two updates is the checkpoint before the first.",
                "wal buffers", vw, vh, s)


# ------------------------------------------------------------------ FIG 15
def fig15():
    vw, vh = 1016, 380
    s = eyebrow(32, 44, "three positions decide whether a dirty page may be written: its pd_lsn, the WAL flush position, and the checkpoint")
    x0, w = 64, 900
    y = 130
    s += f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += eyebrow(x0 + w, y + 22, "WAL position (LSN) →", anchor="end")
    marks = [(0.12, "page modified", "pd_lsn = A", ACCENT), (0.38, "COMMIT", "XLogFlush → flush ≥ A", INK),
             (0.66, "checkpoint", "every dirty page written", MUTED), (0.9, "next change", "full-page image again", SOFT)]
    for f, lab, sub, col in marks:
        x = x0 + w * f
        s += f'<line x1="{x}" y1="{y - 8}" x2="{x}" y2="{y + 8}" stroke="{col}" stroke-width="1.4"/>'
        s += mono(x, y - 20, lab, size=9, fill=col, weight="600")
        s += mono(x, y - 34, sub, size=7, fill=col if col != SOFT else SOFT)
    # forbidden window
    xa, xb = x0 + w * 0.12, x0 + w * 0.38
    s += hbar(xa, y + 14, xb - xa, 10, fill=ACCENT, opacity=0.25, stroke=None, rx=1)
    s += mono((xa + xb) / 2, y + 40, "may NOT be written: WAL up to A is not on disk", size=8, fill=ACCENT, weight="600")
    s += hbar(xb, y + 14, x0 + w * 0.66 - xb, 10, fill=INK, opacity=0.10, stroke=None, rx=1)
    s += mono(xb + 6, y + 58, "may be written by anyone: bgwriter, a backend needing the buffer, or the checkpointer", size=8, fill=INK, anchor="start")
    # buffer state strip
    sy = 220
    s += eyebrow(x0, sy - 10, "the buffer's state word, over the same span")
    states = [(0.0, 0.12, "VALID · clean", "#ffffff", "rgba(45,49,66,0.30)", INK), (0.12, 0.38, "VALID · DIRTY", ACCENT_TINT, ACCENT, ACCENT),
              (0.38, 0.66, "VALID · DIRTY · flushable", "rgba(45,49,66,0.06)", INK, INK), (0.66, 1.0, "VALID · clean (written at the checkpoint)", "#ffffff", "rgba(45,49,66,0.30)", INK)]
    for a, b, lab, fill, stroke, tcol in states:
        xa, xb = x0 + w * a, x0 + w * b
        s += box(xa, sy, xb - xa, 40, fill=fill, stroke=stroke, rx=3)
        s += mono((xa + xb) / 2, sy + 24, lab, size=8, fill=tcol, weight="600" if tcol == ACCENT else "500")
    s += mono(32, 300, "FlushBuffer(page) begins with XLogFlush(pd_lsn). Whoever writes — checkpointer, background writer, or a backend evicting a victim — calls the same function and waits on the same rule.",
              size=8, fill=INK, anchor="start", track="0.02em")
    s += mono(32, 318, "the lab: pd_lsn 0/4E578B78 after the updates, isdirty = t, then CHECKPOINT → isdirty = f, still resident",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += legend(356, vw, [("write forbidden", ACCENT, "box"), ("write allowed", INK, "box")])
    return emit("15", "when-a-page-may-leave", "When a dirty page may leave memory",
                "The write-ahead rule as a timeline. Between the change and the commit's flush, the page is a hostage of the log.",
                "wal buffers", vw, vh, s)


# ------------------------------------------------------------------ FIG 16
def fig16():
    vw, vh = 1016, 480
    s = eyebrow(32, 44, "the lab's grouping query with work_mem = 1 MB: leader + 2 workers, every budget copied")
    s += node(318, 72, 380, 56, "Finalize GroupAggregate ← Gather Merge", "combines three partial results", kind="external")
    cols = [("leader", 48), ("worker 1", 372), ("worker 2", 696)]
    for lab, x in cols:
        s += vline(x + 136, 132, 160, stroke=MUTED, marker="arrow")
        s += box(x, 164, 272, 244, fill="rgba(45,49,66,0.02)", stroke="rgba(45,49,66,0.30)", rx=6, dash="4,3")
        s += tag(x + 8, 172, lab, stroke=INK, w=64)
        s += node(x + 16, 196, 240, 56, "Sort", "external merge · ~2.5 MB on disk", kind="backend")
        s += mono(x + 136, 266, "budget: work_mem = 1 MB", size=8, fill=ACCENT, track="0.06em")
        s += vline(x + 136, 272, 284, stroke=MUTED, marker=None)
        s += node(x + 16, 288, 240, 56, "Partial HashAggregate", "9 batches · 2,065 kB · ~7.5 MB disk", kind="focal")
        s += mono(x + 136, 358, "budget: 1 MB × 2.0 = 2 MB", size=8, fill=ACCENT, track="0.06em")
        s += mono(x + 136, 390, "← Parallel Seq Scan · 333,333 rows", size=8, fill=SOFT)
    s += mono(32, 430, "six operations, six budgets: three sorts at work_mem and three hash tables at twice work_mem, in three processes, for one query (PostgreSQL 16.2)",
              size=8, fill=INK, anchor="start", track="0.02em")
    s += legend(456, vw, [("hash table — spilled to disk in every process", ACCENT, "box"), ("sort — spilled in every process", INK, "box")])
    return emit("16", "per-process-budgets", "work_mem is per operation, per process",
                "EXPLAIN (ANALYZE) reported 'Memory Usage: 2065kB' three times and an external sort three times. Resource limits apply to each worker individually.",
                "local memory", vw, vh, s)


# ------------------------------------------------------------------ FIG 17
def fig17():
    vw, vh = 1016, 320
    s = eyebrow(32, 44, "one million rows, ORDER BY amount_cents, single process — space and time under two budgets")
    rows = [("work_mem = 4 MB", 40464, "temp files", 662.2, False), ("work_mem = 256 MB", 81868, "memory", 493.2, True)]
    y = 90
    sw = 0.0072  # px per kB: 81,868 kB = 589 px
    for lab, kb, kind, ms, focal in rows:
        col = ACCENT if focal else INK
        s += txt(32, y + 20, lab, size=12, weight="600", anchor="start", fill=col)
        s += mono(32, y + 38, f"Sort Method: {'quicksort' if focal else 'external merge'}", size=8, fill=SOFT, anchor="start")
        w = kb * sw
        s += hbar(200, y, w, 30, fill=col, opacity=0.16 if focal else 0.12, stroke=col)
        s += mono(200 + w + 8, y + 19, f"{kb:,} kB in {kind}", size=9, fill=col, anchor="start", weight="600")
        tw = ms * 0.5
        s += hbar(200, y + 40, tw, 14, fill=MUTED, opacity=0.18, stroke=MUTED)
        s += mono(200 + tw + 8, y + 51, f"{ms:.0f} ms", size=8, fill=MUTED, anchor="start")
        y += 92
    s += mono(32, 268, "the in-memory sort needs twenty times the default budget and is 26% faster; the spill is a merge over 10,135 temp blocks, not a catastrophe",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    s += legend(296, vw, [("space used by the sort", INK, "box"), ("in memory", ACCENT, "box"), ("execution time", MUTED, "box")])
    return emit("17", "sort-two-budgets", "The same sort, two budgets",
                "PostgreSQL 16.2, parallel query off. From EXPLAIN (ANALYZE, BUFFERS): 40,464 kB of temp files versus 81,868 kB of memory.",
                "local memory", vw, vh, s)


# ------------------------------------------------------------------ FIG 18
def fig18():
    vw, vh = 1016, 520
    s = eyebrow(32, 44, "pg_log_backend_memory_contexts on the lab backend, with the 256 MB sort held open in a cursor")
    # tree: x by level
    def tnode(x, y, w, name, size, kind="backend"):
        return node(x, y, w, 46, name, size, kind=kind)
    s += tnode(32, 76, 220, "TopMemoryContext", "root · never reset", "store")
    kids = [("CacheMemoryContext", "512 kB · relcache, catcache"), ("MessageContext", "64 kB · reset per command"),
            ("TopTransactionContext", "reset at transaction end"), ("PortalContext →", "per-portal, the cursor")]
    y = 140
    for i, (n, sub) in enumerate(kids):
        focal = i == 3
        s += tnode(96, y, 236, n, sub, "focal" if focal else "backend")
        s += elbow(64, 122, 92, y + 23, stroke=MUTED)
        y += 60
    # portal -> executor -> tuplesort -> caller tuples
    s += tnode(372, 320, 220, "ExecutorState", "the running query", "backend")
    s += elbow(332, 343, 368, 343, stroke=MUTED) if False else hline(332, 368, 343, stroke=MUTED)
    s += tnode(632, 320, 172, "TupleSort main", "25,174,064 B", "focal")
    s += hline(592, 628, 343, stroke=MUTED)
    s += tnode(632, 396, 172, "Caller tuples", "58,720,256 B · 17 blocks", "focal")
    s += elbow(612, 366, 700, 396, stroke=MUTED) if False else f'<path d="M {612} {366} V {419} H {628}" fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>'
    s += mono(720, 458, "1,000,000 chunks — one per row", size=8, fill=ACCENT)
    s += mono(718, 372, "= 2²⁰ SortTuples × 24 B", size=8, fill=ACCENT)
    s += box(832, 320, 152, 122, fill="#ffffff", stroke="rgba(45,49,66,0.30)", rx=6)
    s += eyebrow(848, 340, "grand total")
    s += txt(908, 372, "85,132,832 B", size=13, weight="600", fill=INK)
    s += mono(908, 392, "209 blocks · 143 free chunks", size=7, fill=SOFT)
    s += mono(908, 412, "idle: 118 contexts, 1,298 kB", size=7, fill=SOFT)
    s += mono(908, 428, "the query owns 98.5% of it", size=7, fill=MUTED)
    s += mono(32, 478, "CLOSE the cursor and COMMIT: ExecutorState is deleted with its children, 84 MB goes back in one call, and no tuple is freed individually",
              size=8, fill=INK, anchor="start", track="0.02em")
    s += legend(500, vw, [("permanent", MUTED, "box"), ("per command or transaction", INK, "box"), ("the sort's memory", ACCENT, "box")])
    return emit("18", "context-tree", "The tree of one backend, mid-sort",
                "PostgreSQL 16.2, work_mem = 256 MB, cursor left open after the first FETCH. Sizes as logged; the tree is trimmed to the branches that matter.",
                "memory contexts", vw, vh, s)


# ------------------------------------------------------------------ FIG 19
def fig19():
    vw, vh = 1016, 360
    s = eyebrow(32, 44, "where the sort's 85 MB went, and that it came back — PostgreSQL 16.2, 1,000,000 rows")
    # stacked bar
    x0, y0, w = 32, 92, 520
    total = 85_132_832
    parts = [("SortTuple array", 25_174_064, ACCENT, "2²⁰ slots × 24 B, grown by doubling"),
             ("tuples ('Caller tuples')", 58_720_256, INK, "1,000,000 chunks in 17 Generation blocks"),
             ("everything else", total - 25_174_064 - 58_720_256, SOFT, "catalog caches, the plan, the portal")]
    x = x0
    for name, b, col, sub in parts:
        pw = w * b / total
        s += hbar(x, y0, pw, 44, fill=col, opacity=0.16 if col == ACCENT else 0.12, stroke=col)
        if pw > 60:
            s += mono(x + pw / 2, y0 + 20, name, size=8, fill=col if col != SOFT else MUTED, weight="600")
            s += mono(x + pw / 2, y0 + 34, f"{b / 1e6:.1f} MB", size=8, fill=col if col != SOFT else MUTED)
        x += pw
    s += mono(x0, y0 + 64, "25.2 + 58.7 + 1.2 = 85.1 MB (decimal), against 'quicksort  Memory: 81868kB'", size=8, fill=SOFT, anchor="start")
    s += mono(x0, y0 + 78, "in EXPLAIN — the difference is block headers and binary-vs-decimal rounding", size=8, fill=SOFT, anchor="start")
    s += mono(x0, y0 + 96, "the array: 1,048,576 × 24 = 25,165,824 B,", size=8, fill=INK, anchor="start")
    s += mono(x0, y0 + 110, "one 8 KB block short of the logged 25,174,064", size=8, fill=INK, anchor="start")
    # RSS bars
    rx, ry = 640, 92
    s += eyebrow(rx, ry - 12, "resident set of the backend (VmRSS)")
    vals = [("idle", 12, MUTED), ("cursor open", 97, ACCENT), ("after CLOSE", 18, INK)]
    bh = 30
    for i, (lab, mb, col) in enumerate(vals):
        y = ry + i * 44
        s += mono(rx, y + 20, lab, size=8, fill=INK, anchor="start")
        bw = mb * 2.2
        s += hbar(rx + 90, y + 4, bw, bh - 6, fill=col, opacity=0.16 if col == ACCENT else 0.12, stroke=col)
        s += mono(rx + 90 + bw + 8, y + 20, f"{mb} MB", size=9, fill=col, anchor="start", weight="600")
    s += mono(rx, ry + 150, "6 MB stays after CLOSE: relcache and catcache, not a leak", size=7, fill=SOFT, anchor="start")
    s += mono(32, 300, "freeing was one MemoryContextDelete on the executor's context; the operating system got the pages back because whole blocks, not chunks, were released",
              size=8, fill=INK, anchor="start", track="0.02em")
    s += legend(336, vw, [("SortTuple array", ACCENT, "box"), ("tuples", INK, "box"), ("resident size", MUTED, "box")])
    return emit("19", "where-85-mb-went", "Where 85 MB went",
                "Both halves of the sort's memory decompose exactly: a doubling array of 24-byte entries, and one chunk per row.",
                "memory contexts", vw, vh, s)


# ------------------------------------------------------------------ FIG 20
def fig20():
    vw, vh = 1016, 440
    s = eyebrow(32, 44, "the 15 MB that is not page storage — pg_shmem_allocations, lab server, to scale")
    items = [
        ("<anonymous>", 4_777_344, MUTED, "untracked ShmemAlloc callers"),
        ("XLOG Ctl", 4_208_256, ACCENT, "the WAL buffer ring + control"),
        ("free", 1_875_456, SOFT, "headroom for extensions"),
        ("descriptors", 1_048_576, INK, "16,384 × 64 B"),
        ("CommitTs", 534_016, SER2, "SLRU: commit timestamps"),
        ("Xact", 529_152, SER2, "SLRU: commit status (pg_xact)"),
        ("Checkpointer Data", 393_344, SER1, "request queue"),
        ("Checkpoint BufferIds", 327_680, SER1, "sorted dirty-buffer array"),
        ("Shared Memory Stats", 277_888, MUTED, "cumulative statistics"),
        ("Subtrans", 267_008, SER2, "SLRU: parent xids"),
        ("Buffer IO CVs", 262_144, INK, "16,384 × 16 B"),
        ("Serial · MultiXact · Notify", 467_712, SER2, "three more SLRUs"),
        ("backend arrays", 202_752, MUTED, "activity, status, names"),
        ("locks · procs · 39 others", 102_656, INK, "small, sized by max_connections"),
    ]
    total = 15_273_984
    assert sum(i[1] for i in items) == total, sum(i[1] for i in items)
    # slice-and-dice treemap: two rows
    x0, y0, W, H = 32, 76, 952, 260
    row1 = items[:4]
    row2 = items[4:]
    r1 = sum(i[1] for i in row1)
    h1 = H * r1 / total
    x = x0
    for name, b, col, sub in row1:
        w = W * b / r1
        s += box(x, y0, w, h1, fill=ACCENT_TINT if col == ACCENT else ("#ffffff" if col in (INK, SOFT) else "rgba(45,49,66,0.05)"),
                 stroke=col if col != SOFT else "rgba(45,49,66,0.25)", rx=3)
        s += txt(x + w / 2, y0 + h1 / 2 - 6, name, size=11 if w > 150 else 9, weight="600", fill=col if col != SOFT else MUTED)
        s += mono(x + w / 2, y0 + h1 / 2 + 12, f"{b / 1024 / 1024:.2f} MB", size=8, fill=col if col != SOFT else MUTED)
        s += mono(x + w / 2, y0 + h1 / 2 + 26, sub, size=7, fill=SOFT)
        x += w
    r2 = total - r1
    h2 = H - h1
    x = x0
    for name, b, col, sub in row2:
        w = W * b / r2
        s += box(x, y0 + h1, w, h2, fill="rgba(45,49,66,0.04)" if col == SER2 else "#ffffff",
                 stroke=col, rx=3)
        if w > 74:
            s += mono(x + w / 2, y0 + h1 + h2 / 2 - 6, name, size=7, fill=col, weight="600")
            s += mono(x + w / 2, y0 + h1 + h2 / 2 + 8, f"{b / 1024:.0f} kB", size=7, fill=MUTED)
        else:
            s += mono(x + w / 2, y0 + h1 + h2 / 2 + 3, f"{b / 1024:.0f}k", size=6, fill=MUTED)
        x += w
    s += mono(32, 356, "bottom row, left to right: CommitTs · Xact · Checkpointer Data · Checkpoint BufferIds · stats · Subtrans · Buffer IO CVs · Serial+MultiXact+Notify · backend arrays · locks, procs and 39 others",
              size=7, fill=SOFT, anchor="start", track="0.02em")
    s += mono(32, 374, "SLRU caches were compile-time sized in 16 (Xact = shared_buffers / 512 pages, here 32); 17 made them GUCs and split each into 16-page banks",
              size=8, fill=INK, anchor="start", track="0.02em")
    s += legend(416, vw, [("WAL buffer ring", ACCENT, "box"), ("buffer bookkeeping", INK, "box"), ("SLRU status caches", SER2, "box"), ("checkpointer", SER1, "box")])
    return emit("20", "rest-of-shared-memory", "The rest of shared memory",
                "57 named allocations minus the page storage. Everything here is sized at startup by shared_buffers and max_connections and is never freed.",
                "the rest of shared memory", vw, vh, s)


# ------------------------------------------------------------------ FIG 21
def fig21():
    vw, vh = 1016, 300
    s = eyebrow(32, 44, "the same 143 MB region, mapped by every process, as small pages or huge pages")
    x0, w = 32, 952
    y = 90
    s += txt(x0, y - 8, "4 kB pages: 36,608 of them", size=11, weight="600", anchor="start")
    s += mono(x0 + 240, y - 8, "one TLB entry each — the pattern below is every 8th page", size=8, fill=SOFT, anchor="start")
    s += box(x0, y, w, 44, fill="#ffffff", stroke=INK, rx=3)
    n = 36608 // 8
    step = w / n
    for i in range(n):
        xx = x0 + i * step
        s += f'<line x1="{xx:.2f}" y1="{y + 2}" x2="{xx:.2f}" y2="{y + 42}" stroke="{INK}" stroke-opacity="0.18" stroke-width="0.4"/>'
    y2 = 170
    s += txt(x0, y2 - 8, "2 MB huge pages: 72 of them", size=11, weight="600", anchor="start", fill=ACCENT)
    s += mono(x0 + 240, y2 - 8, "shared_memory_size_in_huge_pages = 72 · 72 × 2 MB = 144 MB ≥ 143 MB", size=8, fill=SOFT, anchor="start")
    s += box(x0, y2, w, 44, fill=ACCENT_TINT, stroke=ACCENT, rx=3)
    for i in range(1, 72):
        xx = x0 + i * w / 72
        s += f'<line x1="{xx:.2f}" y1="{y2 + 2}" x2="{xx:.2f}" y2="{y2 + 42}" stroke="{ACCENT}" stroke-opacity="0.5" stroke-width="0.8"/>'
    s += mono(32, 246, "huge_pages = try asked for MAP_HUGETLB and fell back silently: HugePages_Total was 0 on the lab machine. Check huge_pages_status (17+) or /proc/meminfo after every restart.",
              size=8, fill=INK, anchor="start", track="0.02em")
    s += mono(32, 264, "procedure: postgres -D $PGDATA -C shared_memory_size_in_huge_pages on the stopped server, then vm.nr_hugepages ≥ that number", size=8, fill=SOFT, anchor="start", track="0.02em")
    return emit("21", "huge-pages", "36,608 pages or 72",
                "Every backend maps the whole region, so every backend carries its page-table entries. Huge pages cut that 500-fold; 'try' does not guarantee them.",
                "the rest of shared memory", vw, vh, s)


# ------------------------------------------------------------------ FIG 22
def fig22():
    vw, vh = 1016, 420
    s = eyebrow(32, 44, "which tool sees which pool — PostgreSQL 16.2; version notes for 17 and 18 in the text")
    rows = [
        ("shared buffers", ACCENT, ["pg_shmem_allocations", "pg_buffercache", "pg_buffercache_usage_counts()", "pg_stat_io (context, reuses, evictions)", "EXPLAIN (BUFFERS): shared hit/read", "pg_prewarm"]),
        ("WAL buffers", INK, ["pg_stat_wal (wal_buffers_full)", "pg_walinspect", "pg_current_wal_*_lsn()", "pageinspect: page_header().lsn"]),
        ("local memory", INK, ["pg_backend_memory_contexts", "pg_log_backend_memory_contexts(pid)", "EXPLAIN (ANALYZE): Sort Method, Batches, Memory Usage", "EXPLAIN (BUFFERS): local, temp"]),
        ("kernel page cache", SOFT, ["fincore (util-linux) on pg_relation_filepath()", "track_io_timing — the only hint from inside", "no PostgreSQL view"]),
    ]
    y = 80
    for pool, col, tools in rows:
        s += box(32, y, 952, 66, fill=ACCENT_TINT if col == ACCENT else ("rgba(79,93,117,0.06)" if col == SOFT else "#ffffff"),
                 stroke=col if col != SOFT else "rgba(45,49,66,0.30)", rx=4)
        s += txt(48, y + 38, pool, size=12, weight="600", anchor="start", fill=col if col != SOFT else MUTED)
        x = 220
        yy = y + 22
        for t in tools:
            tw = 6.2 * len(t) + 18
            if x + tw > 972:
                x = 220
                yy += 26
            s += box(x, yy - 12, tw, 20, fill="#ffffff", stroke=col if col != SOFT else "rgba(45,49,66,0.30)", rx=10, sw=0.8)
            s += mono(x + tw / 2, yy + 2, t, size=8, fill=INK if col != SOFT else MUTED)
            x += tw + 8
        y += 76
    s += mono(32, 392, "pg_stat_io is the only view that shows the rings; nothing inside PostgreSQL shows the kernel cache",
              size=8, fill=SOFT, anchor="start", track="0.02em")
    return emit("22", "tooling-map", "One view per pool",
                "The instruments used in this post, by the pool they observe. The kernel cache needs an operating-system tool.",
                "implementation", vw, vh, s)


ALL = {"12": fig12, "13": fig13, "14": fig14, "15": fig15, "16": fig16, "17": fig17,
       "18": fig18, "19": fig19, "20": fig20, "21": fig21, "22": fig22}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
