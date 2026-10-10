#!/usr/bin/env python3
"""Figures 15-28 for postgresql-foundations-process-layer. Every number is from lab/captures.md
or the research ledger; nothing here is plotted from a formula."""
import math
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, SANS, SERIF, alabel, box, cell, elbow, emit,
                    eyebrow, elbow_hvh, hline, legend, masked, mono, node, tag,
                    txt, vline)
from _figs_a import SER1, SER2, hbar, lane, msg, selfmsg, note


# ------------------------------------------------------------------ FIG 15
def fig15():
    vw, vh = 1016, 420
    s = eyebrow(32, 44, "one checkpoint interval (checkpoint_timeout 5 min, completion_target 0.9) and the lab's forced one, to scale with each other")
    x0, x1 = 60, 956
    # scheduled interval
    y = 120
    def tx(t):
        return x0 + (x1 - x0) * t / 300.0
    s += txt(32, y - 44, "a scheduled checkpoint", size=11, weight="600", anchor="start")
    s += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for t in range(0, 301, 60):
        s += f'<line x1="{tx(t)}" y1="{y - 4}" x2="{tx(t)}" y2="{y + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        s += mono(tx(t), y + 18, f"{t // 60} min", size=8, fill=SOFT)
    s += f'<circle cx="{tx(0)}" cy="{y}" r="5" fill="{INK}"/>'
    s += mono(tx(0) + 8, y - 12, "redo point noted", size=8, fill=INK, anchor="start")
    s += hbar(tx(0), y - 3, tx(270) - tx(0), 6, fill=INK, opacity=0.14)
    s += masked(tx(135), y - 14, "dirty buffers written, paced: CheckpointWriteDelay between batches", size=8, fill=INK)
    s += hbar(tx(270), y - 3, tx(282) - tx(270), 6, fill=ACCENT, opacity=0.9)
    s += mono(tx(276), y - 12, "fsync · checkpoint record · pg_control · recycle WAL", size=7.5, fill=ACCENT, anchor="end")
    s += vline(tx(270), y + 6, y + 30, stroke=ACCENT, marker=None, dash="3,3")
    s += mono(tx(270) - 6, y + 34, "90% of the interval", size=8, fill=ACCENT, anchor="end")
    s += mono(tx(300) + 12, y + 34, "next one starts", size=8, fill=MUTED, anchor="end")
    # the forced one
    y2 = 250
    s += txt(32, y2 - 44, "the lab's CHECKPOINT command — 10,137 dirty buffers, unpaced", size=11, weight="600", anchor="start")
    def tx2(t):  # seconds, 0..0.4
        return x0 + (x1 - x0) * t / 0.40
    s += f'<line x1="{x0}" y1="{y2}" x2="{x1}" y2="{y2}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for t in (0, 0.1, 0.2, 0.3, 0.4):
        s += f'<line x1="{tx2(t)}" y1="{y2 - 4}" x2="{tx2(t)}" y2="{y2 + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        s += mono(tx2(t), y2 + 18, f"{t:.1f} s", size=8, fill=SOFT)
    s += hbar(tx2(0), y2 - 3, tx2(0.055) - tx2(0), 6, fill=INK, opacity=0.4)
    s += masked(tx2(0.03), y2 - 14, "write 0.055 s", size=8, fill=INK)
    s += hbar(tx2(0.055), y2 - 3, tx2(0.265) - tx2(0.055), 6, fill=ACCENT, opacity=0.5)
    s += masked(tx2(0.17), y2 - 14, "sync 0.210 s · 313 files · longest 5 ms", size=8, fill=ACCENT)
    s += hbar(tx2(0.265), y2 - 3, tx2(0.321) - tx2(0.265), 6, fill=MUTED, opacity=0.5)
    s += masked(tx2(0.295), y2 - 14, "record, pg_control, 8 segments recycled", size=7.5, fill=MUTED)
    s += mono(tx2(0.321), y2 + 42, "total 0.321 s", size=8, fill=INK, weight="600")
    s += note(32, 330, "the redo lsn (3/236669C0) is 56 bytes before the record's lsn (3/236669F8) · recovery starts at the redo point, not at the record")
    s += note(32, 346, "a scheduled checkpoint spreads its writes so I/O is flat across the interval · a forced one pays it all at once, and the fsync phase dominates")
    s += legend(390, vw, [("writing dirty buffers", INK, "box"), ("fsync", ACCENT, "box"), ("bookkeeping", MUTED, "box")])
    return emit("15", "checkpoint-timeline", "What a checkpoint does, and when",
                "A scheduled checkpoint paces its writes to finish at 90% of the interval. The lab's forced one did 10,137 pages in 55 ms and then spent 210 ms in fsync.",
                "the checkpointer", vw, vh, s)


# ------------------------------------------------------------------ FIG 16
def fig16():
    vw, vh = 1016, 360
    s = eyebrow(32, 44, "ForwardSyncRequest, checkpointer.c — backends write pages; the checkpointer fsyncs files")
    s += node(40, 100, 200, 60, "backend", "writes a dirty page with pwrite()", kind="backend")
    s += node(40, 200, 200, 60, "background writer", "same path", kind="backend")
    s += hline(240, 330, 130)
    s += hline(240, 330, 230)
    s += alabel(286, 130, "fsync request", gap=14)
    s += alabel(286, 230, "fsync request", gap=14)
    # queue
    qx, qy, qw, qh = 334, 96, 340, 170
    s += box(qx, qy, qw, qh, fill="rgba(45,49,66,0.04)", stroke=INK)
    s += tag(qx + 8, qy + 6, "CheckpointerShmem", stroke=MUTED, w=130)
    s += txt(qx + qw / 2, qy + 40, "request queue", size=11, weight="600")
    s += mono(qx + qw / 2, qy + 56, "NBuffers slots — 16,384 here", size=8, fill=MUTED)
    for i in range(24):
        fx = qx + 16 + (i % 12) * 26
        fy = qy + 76 + (i // 12) * 22
        filled = i < 9
        s += f'<rect x="{fx}" y="{fy}" width="22" height="16" rx="2" fill="{INK if filled else "#ffffff"}" fill-opacity="{0.35 if filled else 1}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += mono(qx + qw / 2, qy + 148, "> half full → SetLatch(checkpointer)", size=7.5, fill=ACCENT)
    s += hline(qx + qw, 760, 181)
    s += alabel(716, 181, "drained at", gap=14)
    s += node(764, 151, 212, 60, "checkpointer", "fsync every requested file", kind="focal")
    # full path
    s += box(334, 282, 640, 40, fill=ACCENT_TINT, stroke=ACCENT, rx=4)
    s += txt(348, 300, "queue full?", size=9.5, weight="600", fill=ACCENT, anchor="start")
    s += mono(430, 300, "first CompactCheckpointerRequestQueue() drops duplicates · still full, or no checkpointer → the backend fsyncs itself", size=7.5, fill=INK, anchor="start")
    s += mono(430, 314, "and buffers_backend_fsync counts it — the number that should be zero", size=7.5, fill=ACCENT, anchor="start")
    s += legend(346, vw, [("a request", INK, "box"), ("the process that fsyncs", ACCENT, "box")])
    return emit("16", "fsync-queue", "Who fsyncs",
                "Backends and the background writer write pages and hand the fsync to the checkpointer through a shared queue sized to the buffer pool.",
                "the checkpointer", vw, vh, s)


# ------------------------------------------------------------------ FIG 17
def fig17():
    vw, vh = 1016, 360
    s = eyebrow(32, 44, "pg_stat_io, relation object, after dirtying 10,137 pages and checkpointing — PostgreSQL 16.2")
    x0, y0, w, h = 120, 90, 380, 180
    top = 11000
    def th(v):
        return v / top * h
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += eyebrow(x0, y0 - 14, "page writes", anchor="start")
    bars = [("checkpointer", 10137, ACCENT), ("client backend", 0, INK), ("background writer", 0, MUTED)]
    for i, (name, v, col) in enumerate(bars):
        bx = x0 + 30 + i * 120
        bh = th(v)
        s += hbar(bx, y0 + h - bh, 70, bh, fill=col, opacity=0.18, stroke=col)
        s += mono(bx + 35, y0 + h - bh - 6, f"{v:,}", size=9, fill=col, weight="600")
        s += mono(bx + 35, y0 + h + 14, name, size=8, fill=INK)
    s += mono(x0 + 30 + 120 + 35, y0 + h - 34, "extends: 9,238", size=7.5, fill=INK)
    s += mono(x0 + 30 + 120 + 35, y0 + h - 22, "evictions: 0", size=7.5, fill=INK)
    s += mono(x0 + 30 + 240 + 35, y0 + h - 22, "no row at all", size=7.5, fill=MUTED)
    # fsyncs
    x1 = 620
    s += f'<line x1="{x1}" y1="{y0 + h}" x2="{x1 + 300}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    s += eyebrow(x1, y0 - 14, "file fsyncs", anchor="start")
    fb = [("checkpointer", 312, ACCENT), ("client backend", 0, INK)]
    for i, (name, v, col) in enumerate(fb):
        bx = x1 + 30 + i * 130
        bh = v / 340 * h
        s += hbar(bx, y0 + h - bh, 70, bh, fill=col, opacity=0.18, stroke=col)
        s += mono(bx + 35, y0 + h - bh - 6, f"{v:,}", size=9, fill=col, weight="600")
        s += mono(bx + 35, y0 + h + 14, name, size=8, fill=INK)
    s += note(32, 306, "the pool never filled (8,403 table pages < 16,384 buffers), so backends evicted nothing and the background writer had nothing to clean ahead of")
    s += note(32, 322, "pg_stat_bgwriter.buffers_backend rose by 1,351 in the same step — the old column counts extensions as writes; 17 drops it in favour of this view")
    return emit("17", "who-wrote", "Who wrote the lab's dirty pages",
                "On a pool that never filled, the answer is the checkpointer, at the checkpoint. The background writer has no row.",
                "the background writer", vw, vh, s)


# ------------------------------------------------------------------ FIG 18
def fig18():
    vw, vh = 1016, 510
    s = eyebrow(32, 44, "what a commit waits for — synchronous_commit on (default) and off")
    xs = {"c": 120, "be": 360, "ww": 640, "d": 880}
    names = {"c": "client", "be": "backend", "ww": "WAL writer", "d": "WAL file"}
    # each section tag sits on its own line above the lane boxes, clear of the client box
    s += tag(32, 62, "on", stroke=INK, w=40)
    for k, x in xs.items():
        s += lane(x, 114, 262, names[k])
    s += msg(xs["c"], xs["be"], 136, "COMMIT")
    s += selfmsg(xs["be"], 152, "write commit record into WAL buffers")
    s += msg(xs["be"], xs["d"], 192, "XLogFlush: write + fdatasync up to my record", accent=True, sub="the backend waits here")
    s += msg(xs["d"], xs["be"], 228, "durable", dash="3,3")
    s += msg(xs["be"], xs["c"], 252, "COMMIT — reported after the disk confirmed", dash="3,3")
    s += tag(32, 284, "off", stroke=ACCENT, w=44)
    for k, x in xs.items():
        s += lane(x, 336, 460, names[k])
    s += msg(xs["c"], xs["be"], 358, "COMMIT")
    s += selfmsg(xs["be"], 374, "write commit record into WAL buffers")
    s += msg(xs["be"], xs["c"], 408, "COMMIT — reported now", dash="3,3", accent=True)
    s += msg(xs["ww"], xs["d"], 436, "XLogBackgroundFlush every wal_writer_delay (200 ms)", sub="durable within 3 × 200 ms = 600 ms")
    s += hbar(xs["ww"] - 6, 342, 12, 80, fill=ACCENT, opacity=0.06)
    s += masked(xs["ww"], 386, "the risk window", size=7.5, fill=ACCENT)
    s += legend(486, vw, [("the wait", ACCENT, "line"), ("reply", MUTED, "dashline")])
    return emit("18", "commit-paths", "What a commit waits for",
                "With on, the backend waits for fdatasync before replying. With off, it replies at once and the WAL writer closes the gap within 600 ms.",
                "the WAL writer", vw, vh, s)


# ------------------------------------------------------------------ FIG 19
def fig19():
    vw, vh = 1016, 340
    s = eyebrow(32, 44, "5,000 single-row transactions from one client — PostgreSQL 16.2, fdatasync, NVMe")
    groups = [("transactions per second", [867, 13771], "{:,.0f}", 15000),
              ("fdatasync calls (pg_stat_wal.wal_sync)", [5000, 2], "{:,.0f}", 5600),
              ("XLogWrite calls (wal_write)", [5000, 105], "{:,.0f}", 5600)]
    x0, y0, gw, h = 60, 90, 310, 170
    for gi, (title, vals, fmt, top) in enumerate(groups):
        gx = x0 + gi * gw
        s += txt(gx + 120, y0 - 14, title, size=10, weight="600")
        s += f'<line x1="{gx}" y1="{y0 + h}" x2="{gx + 250}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        for j, v in enumerate(vals):
            col = INK if j == 0 else ACCENT
            bx = gx + 30 + j * 120
            bh = max(v / top * h, 1.5)
            s += hbar(bx, y0 + h - bh, 70, bh, fill=col, opacity=0.18, stroke=col)
            s += mono(bx + 35, y0 + h - bh - 6, fmt.format(v), size=9, fill=col, weight="600")
            s += mono(bx + 35, y0 + h + 14, "on" if j == 0 else "off", size=8, fill=INK)
    s += box(802, 96, 156, 46, fill=ACCENT_TINT, stroke=ACCENT, rx=4)
    s += txt(880, 116, "16×", size=16, weight="600", fill=ACCENT, family=SERIF)
    s += mono(880, 132, "5.76 s → 0.36 s", size=8, fill=ACCENT)
    s += note(32, 300, "the commit is not slow because of the write · it is slow because of the wait for the disk to confirm it · off batches 5,000 commits into 2 syncs")
    return emit("19", "sync-commit", "Five thousand commits, two settings",
                "Same rows, same disk. The only difference is whether the backend waits for fdatasync before replying.",
                "the WAL writer", vw, vh, s)


# ------------------------------------------------------------------ FIG 20
def fig20():
    vw, vh = 1016, 520
    s = eyebrow(32, 44, "autovacuum.c — the launcher never forks and never sees a table")
    xs = {"l": 130, "pm": 400, "w": 700, "db": 900}
    names = {"l": "launcher", "pm": "postmaster", "w": "worker", "db": "database"}
    for k, x in xs.items():
        s += lane(x, 100, 470, names[k], w=110)
    s += selfmsg(xs["l"], 118, "wake (naptime / N databases) · pick the database due next")
    s += selfmsg(xs["l"], 150, "write the choice into AutoVacuumShmem")
    s += msg(xs["l"], xs["pm"], 196, "SendPostmasterSignal(PMSIGNAL_START_AUTOVAC_WORKER)", accent=True)
    s += msg(xs["pm"], xs["w"], 232, "fork_process() — the child knows only 'become a worker'", accent=True)
    s += selfmsg(xs["w"], 250, "attach to shared memory · read which database")
    s += msg(xs["w"], xs["db"], 292, "connect")
    s += selfmsg(xs["w"], 310, "every table: relation_needs_vacanalyze()")
    s += msg(xs["w"], xs["db"], 352, "VACUUM / ANALYZE the ones that qualify", sub="under the shared cost budget")
    s += msg(xs["w"], xs["l"], 400, "SIGUSR2: done — a slot is free", dash="3,3")
    s += selfmsg(xs["l"], 418, "rebalance cost limits among remaining workers · maybe launch another")
    s += legend(496, vw, [("the only two signals that create a process", ACCENT, "line"), ("everything else", MUTED, "line")])
    return emit("20", "autovacuum-handshake", "How an autovacuum worker comes to exist",
                "The launcher asks. The postmaster forks. The worker decides. No step is skipped, even for a table that crossed its threshold a minute ago.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 21
def fig21():
    vw, vh = 1016, 386
    s = eyebrow(32, 44, "the launcher's round with two databases and autovacuum_naptime 60 s — a visit every 30 s, alternating")
    x0, x1, y = 60, 956, 130
    T = 180.0
    def tx(t):
        return x0 + (x1 - x0) * t / T
    s += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for t in range(0, 181, 30):
        s += f'<line x1="{tx(t)}" y1="{y - 4}" x2="{tx(t)}" y2="{y + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        s += mono(tx(t), y + 18, f"{t} s", size=8, fill=SOFT)
    for i, t in enumerate(range(0, 181, 30)):
        db = "proclab" if i % 2 == 0 else "postgres"
        col = ACCENT if db == "proclab" else MUTED
        s += vline(tx(t), y - 40, y - 8, stroke=col, marker="arrow-accent" if db == "proclab" else "arrow")
        s += mono(tx(t), y - 48, db, size=7.5, fill=col)
    # worker slots
    sy = 226
    s += txt(32, sy - 10, "worker slots (autovacuum_max_workers = 3)", size=9.5, weight="600", anchor="start")
    for k in range(3):
        yy = sy + k * 18
        s += f'<line x1="{x0}" y1="{yy + 8}" x2="{x1}" y2="{yy + 8}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0 - 8, yy + 11, f"slot {k + 1}", size=7.5, fill=SOFT, anchor="end")
    # busy spans: each visit spawns a short worker; at 60 s proclab's worker is the lab's
    for i, t in enumerate(range(0, 181, 30)):
        w = 0.03 if i != 2 else 0.03
        s += hbar(tx(t), sy + 2, max(tx(t + 2) - tx(t), 3), 12, fill=ACCENT if i % 2 == 0 else MUTED, opacity=0.6)
    s += hbar(tx(95), sy + 20, tx(140) - tx(95), 12, fill=INK, opacity=0.25)
    s += masked(tx(117), sy + 48, "a long vacuum holds a slot; the next database waits for one", size=7.5, fill=INK)
    # the lab's update
    s += f'<circle cx="{tx(31)}" cy="{y}" r="5" fill="{INK}"/>'
    s += mono(tx(31) + 8, y + 40, "the lab's UPDATE, just after a visit to the other database", size=8, fill=INK, anchor="start")
    s += hbar(tx(31), y - 3, tx(60) - tx(31), 6, fill=INK, opacity=0.14)
    s += masked(tx(45), y + 56, "waits 30 s for the next proclab visit — 60 s had it landed at t = 1", size=8, fill=INK)
    s += note(32, 322, "expected arrival = naptime / 2 + queueing for a slot · in 16 the slot count needs a restart; 18 adds autovacuum_worker_slots so it can move at runtime")
    s += legend(352, vw, [("visit to proclab", ACCENT, "line"), ("visit to the other database", MUTED, "line"), ("slot occupied", INK, "box")])
    return emit("21", "launcher-round", "The launcher's clock",
                "One visit per database per naptime, round-robin, and three slots for the workers those visits spawn. Arrival time is the sum of the two.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 22
def fig22():
    vw, vh = 1016, 416
    s = eyebrow(32, 44, "vacuum threshold = 50 + 0.2 × reltuples — the default line, with the lab's two tables on it (log-log)")
    x0, y0, w, h = 110, 84, 760, 230
    def px(n):
        return x0 + (math.log10(n) - 3) / 6 * w
    def py(v):
        return y0 + h - (math.log10(v) - 2) / 7 * h
    for n in (1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9):
        s += f'<line x1="{px(n)}" y1="{y0}" x2="{px(n)}" y2="{y0 + h}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(px(n), y0 + h + 16, f"{int(n):,}", size=7.5, fill=SOFT)
    for v in (1e2, 1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9):
        s += f'<line x1="{x0}" y1="{py(v)}" x2="{x0 + w}" y2="{py(v)}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0 - 8, py(v) + 3, f"{int(v):,}", size=7.5, fill=SOFT, anchor="end")
    s += mono(x0 + w / 2, y0 + h + 32, "rows in the table (reltuples)", size=8.5, fill=MUTED)
    s += txt(32, y0 - 12, "dead tuples before autovacuum acts", size=8.5, fill=MUTED, anchor="start")
    pts = [(n, 50 + 0.2 * n) for n in (1e3, 3e3, 1e4, 3e4, 1e5, 3e5, 1e6, 3e6, 1e7, 3e7, 1e8, 3e8, 1e9)]
    d = " ".join(f"{'M' if i == 0 else 'L'} {px(n)} {py(v)}" for i, (n, v) in enumerate(pts))
    s += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="1.6"/>'
    # a per-table override line at 0.01
    pts2 = [(n, 50 + 0.01 * n) for n in (1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9)]
    d2 = " ".join(f"{'M' if i == 0 else 'L'} {px(n)} {py(v)}" for i, (n, v) in enumerate(pts2))
    s += f'<path d="{d2}" fill="none" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="4,3"/>'
    s += masked(px(1e8) + 8, py(50 + 0.01 * 1e8) + 20, "scale_factor 0.01 per table", size=7.5, fill=MUTED, anchor="start")
    for n, v, lab in ((1e5, 20050, "customers · 100,000 rows → 20,050"), (1e6, 200050, "orders · 1,000,000 rows → 200,050")):
        s += f'<circle cx="{px(n)}" cy="{py(v)}" r="5" fill="{ACCENT}"/>'
        s += masked(px(n) - 12, py(v) - 8, lab, size=8, fill=ACCENT, anchor="end")
    s += f'<circle cx="{px(1e9)}" cy="{py(50 + 0.2e9)}" r="4" fill="none" stroke="{INK}" stroke-width="1.2"/>'
    s += masked(px(1e9) - 16, py(50 + 0.2e9) - 7, "a billion rows → 200 million dead before anything happens", size=7.5, fill=INK, anchor="end")
    s += note(32, 366, "the insert rule (1,000 + 0.2 × rows) and the analyze rule (50 + 0.1 × rows) are the same shape · in 18, autovacuum_vacuum_max_threshold caps the count regardless of scale")
    s += legend(392, vw, [("default: 50 + 0.2 × rows", INK, "line"), ("a per-table override", MUTED, "dashline"), ("the lab's tables", ACCENT, "dot")])
    return emit("22", "threshold-line", "The default threshold is a fifth of the table",
                "On a million rows that is 200,000 dead tuples before autovacuum acts; on a billion, 200 million. Large tables override it per table.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 23
def fig23():
    vw, vh = 1016, 330
    s = eyebrow(32, 44, "AutoVacuumUpdateCostLimit: vacuum_cost_limit / nworkers_for_balance — the same total, however many workers")
    total_w = 560
    for i, (title, n) in enumerate((("one worker", 1), ("three workers", 3))):
        y = 92 + i * 100
        s += txt(32, y + 6, title, size=11, weight="600", anchor="start")
        s += mono(32, y + 22, f"{200 // n} cost units per 2 ms each", size=8, fill=MUTED, anchor="start")
        seg = total_w / n
        for k in range(n):
            s += hbar(240 + k * seg, y - 6, seg - (4 if n > 1 else 0), 36, fill=ACCENT if n == 1 else INK, opacity=0.18, stroke=ACCENT if n == 1 else INK)
            s += mono(240 + k * seg + (seg - 4) / 2, y + 16, f"worker {k + 1}: limit {200 // n}", size=8.5, fill=ACCENT if n == 1 else INK, weight="600")
        s += mono(240 + total_w + 14, y + 16, "= 200 units / 2 ms", size=9, fill=INK, anchor="start", weight="600")
        s += mono(240 + total_w + 14, y + 30, "≈ 100,000 units/s", size=7.5, fill=SOFT, anchor="start")
    s += box(240, 232, 744, 40, fill=ACCENT_TINT, stroke=ACCENT, rx=4)
    s += txt(254, 250, "to vacuum faster:", size=9.5, weight="600", fill=ACCENT, anchor="start")
    s += mono(370, 250, "raise autovacuum_vacuum_cost_limit (or set it per table) · adding workers changes who does the I/O, not how much", size=7.5, fill=INK, anchor="start")
    s += mono(370, 264, "at defaults: 50,000 page misses/s or 5,000 dirtied pages/s (≈ 39 MB/s) for the whole cluster", size=7.5, fill=INK, anchor="start")
    s += note(32, 300, "a table with its own cost storage parameters is left out of the balance · a manual VACUUM has vacuum_cost_delay 0 and is not throttled at all")
    return emit("23", "cost-balance", "Three workers do not vacuum three times as fast",
                "They share one budget, divided evenly. The width of the bar is the cluster's vacuum I/O ceiling, and it does not change with the headcount.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 24
def fig24():
    vw, vh = 1016, 380
    s = eyebrow(32, 44, "pg_stat_progress_vacuum.phase — the state machine, from progress-reporting docs and the lab's 10 ms samples")
    # five columns of 140-wide boxes across 32..984; connectors turn in the 63 px gaps between them
    c = [102 + k * 203 for k in range(5)]
    states = [("initializing", c[0], 150), ("scanning heap", c[1], 150), ("vacuuming indexes", c[2], 90), ("vacuuming heap", c[2], 210),
              ("cleaning up indexes", c[3], 150), ("truncating heap", c[4], 90), ("final cleanup", c[4], 210)]
    for name, x, y in states:
        focal = name in ("scanning heap", "vacuuming indexes", "vacuuming heap")
        s += box(x - 70, y - 20, 140, 40, fill=ACCENT_TINT if focal else "#ffffff", stroke=ACCENT if focal else INK)
        s += txt(x, y + 4, name, size=9.5, weight="600", fill=ACCENT if focal else INK)
    g1, g2, g3 = c[1] + 101, c[2] + 101, c[3] + 101        # mid-gap x after columns 1, 2, 3
    s += hline(c[0] + 70, c[1] - 72, 150)
    s += (f'<path d="M {c[1] + 70} 150 H {g1 - 8} Q {g1} 150 {g1} 142 V 98 Q {g1} 90 {g1 + 8} 90 H {c[2] - 72}" '
          f'fill="none" stroke="{ACCENT}" stroke-width="1.2" marker-end="url(#arrow-accent)"/>')
    s += mono(g1 - 8, 112, "store full, or heap done", size=7, fill=ACCENT, anchor="end")
    s += vline(c[2], 110, 188, stroke=ACCENT, marker="arrow-accent")
    s += masked(c[2], 150, "every index, in full", size=7, fill=ACCENT)
    # back to scanning heap: in under its bottom edge
    s += (f'<path d="M {c[2] - 70} 210 H {c[1] + 28} Q {c[1] + 20} 210 {c[1] + 20} 202 V 172" fill="none" stroke="{ACCENT}" '
          f'stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arrow-accent)"/>')
    s += mono(c[2] - 78, 226, "heap not finished: resume where it stopped", size=7, fill=ACCENT, anchor="end")
    # forward
    s += (f'<path d="M {c[2] + 70} 210 H {g2 - 8} Q {g2} 210 {g2} 202 V 158 Q {g2} 150 {g2 + 8} 150 H {c[3] - 72}" '
          f'fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>')
    s += mono(g2 + 6, 190, "heap finished", size=7, fill=MUTED, anchor="start")
    s += (f'<path d="M {c[3] + 70} 150 H {g3 - 8} Q {g3} 150 {g3} 142 V 98 Q {g3} 90 {g3 + 8} 90 H {c[4] - 72}" '
          f'fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>')
    s += vline(c[4], 110, 188, stroke=MUTED, marker="arrow")
    s += box(60, 280, 896, 44, fill="rgba(45,49,66,0.04)", stroke=MUTED, dash="4,3")
    s += mono(76, 298, "the lab at 1 MB: num_dead_tuples climbs to 174,512 → vacuuming indexes → index_vacuum_count 1 → vacuuming heap through page 1,677 → scanning heap resumes at 1,678, counter reset · five times", size=7.5, fill=INK, anchor="start")
    s += mono(76, 312, "1,375 distinct samples caught every phase but final cleanup, which is too brief for the sampler", size=7.5, fill=SOFT, anchor="start")
    s += legend(354, vw, [("the loop that maintenance_work_mem controls", ACCENT, "box"), ("runs once", INK, "box")])
    return emit("24", "vacuum-phases", "The vacuum state machine",
                "Each time the dead-tuple store fills, vacuum leaves the heap, walks every index in full, comes back, and resumes. That loop is the whole story.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 25
def fig25():
    vw, vh = 1016, 420
    s = eyebrow(32, 44, "800,000 dead tuples in a 7,693-page heap with two indexes — the trace at 1 MB and at 256 MB")
    hx, hw = 60, 640
    # 1 MB
    y = 100
    s += txt(32, y - 16, "maintenance_work_mem = 1 MB · store holds 174,761 · 5 index passes", size=10, weight="600", anchor="start")
    s += hbar(hx, y, hw, 18, fill=INK, opacity=0.06, stroke=RULE_SOLID)
    cuts = [0, 1679, 3358, 5037, 6716, 7693]
    for i in range(5):
        a, b = cuts[i], cuts[i + 1]
        s += hbar(hx + hw * a / 7693, y, hw * (b - a) / 7693 - 2, 18, fill=ACCENT, opacity=0.10 + 0.04 * i, stroke=ACCENT)
        s += mono(hx + hw * (a + b) / 2 / 7693, y + 12, f"scan {i + 1}", size=7.5, fill=ACCENT)
        # index pass marker
        ix = hx + hw * b / 7693
        s += vline(ix, y + 20, y + 44, stroke=ACCENT, marker=None)
        s += box(ix - 34, y + 44, 68, 26, fill=ACCENT_TINT, stroke=ACCENT, rx=3)
        s += mono(ix, y + 55, "idx A", size=7, fill=ACCENT)
        s += mono(ix, y + 65, "idx B", size=7, fill=ACCENT)
    s += mono(hx + hw + 48, y + 12, "heap: read once", size=8, fill=INK, anchor="start")
    s += mono(hx + hw + 48, y + 56, "indexes: 5 × 2,603 pages", size=8, fill=ACCENT, anchor="start")
    s += mono(hx + hw + 48, y + 70, "= 13,015 index pages", size=8, fill=ACCENT, anchor="start", weight="600")
    # 256 MB
    y = 230
    s += txt(32, y - 16, "maintenance_work_mem = 256 MB · store holds 44,739,242 · 1 index pass", size=10, weight="600", anchor="start")
    s += hbar(hx, y, hw, 18, fill=INK, opacity=0.10, stroke=INK)
    s += mono(hx + hw / 2, y + 12, "scan 1 — the whole heap, 7,693 pages", size=7.5, fill=INK)
    ix = hx + hw
    s += vline(ix, y + 20, y + 44, stroke=INK, marker=None)
    s += box(ix - 34, y + 44, 68, 26, fill="#ffffff", stroke=INK, rx=3)
    s += mono(ix, y + 55, "idx A", size=7, fill=INK)
    s += mono(ix, y + 65, "idx B", size=7, fill=INK)
    s += mono(hx + hw + 48, y + 12, "heap: read once", size=8, fill=INK, anchor="start")
    s += mono(hx + hw + 48, y + 56, "indexes: 1 × 2,603 pages", size=8, fill=INK, anchor="start")
    s += mono(hx + hw + 48, y + 70, "= 2,603 index pages", size=8, fill=INK, anchor="start", weight="600")
    s += note(32, 340, "passes = ⌈ dead × 6 B / maintenance_work_mem ⌉ on 16 · the heap is read once regardless · 17's TidStore changes the 6 B and removes the 1 GB cap")
    s += note(32, 356, "the vacuuming-heap phase after each index pass revisits only the pages scanned so far, which is why heap_blks_vacuumed trails heap_blks_scanned")
    s += legend(394, vw, [("1 MB: five cycles", ACCENT, "box"), ("256 MB: one cycle", INK, "box")])
    return emit("25", "index-pass-trace", "Five passes at 1 MB, one at 256 MB",
                "The same 800,000 dead tuples. The store's size is the only variable, and it multiplies the index work five times.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 26
def fig26():
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "Workers Planned comes from a ceiling; Workers Launched comes from a pool — the lab's 6 planned, 1 launched")
    # plan tree
    s += node(60, 90, 220, 50, "Finalize Aggregate", None, kind="backend")
    s += vline(170, 140, 166)
    s += node(60, 168, 220, 60, "Gather", "Workers Planned: 6", kind="focal")
    s += vline(170, 228, 254)
    s += node(60, 256, 220, 50, "Partial Aggregate", None, kind="backend")
    s += vline(170, 306, 332)
    s += node(60, 334, 220, 50, "Parallel Seq Scan on orders", "Workers Launched: 1", kind="focal")
    # planner inputs
    s += box(330, 90, 340, 110, fill="#ffffff", stroke=INK)
    s += tag(338, 96, "planner", stroke=MUTED, w=60)
    s += txt(344, 128, "size rule: 1 worker at min_parallel_table_scan_size (8 MB),", size=8.5, anchor="start")
    s += txt(344, 142, "roughly one more each time the table triples", size=8.5, anchor="start")
    s += txt(344, 160, "capped by max_parallel_workers_per_gather (2 → set to 6)", size=8.5, anchor="start")
    s += txt(344, 178, "or fixed by the table's parallel_workers option (= 6)", size=8.5, anchor="start", weight="600")
    s += mono(344, 192, "→ 6 planned. The planner cannot see the pool.", size=8, fill=ACCENT, anchor="start")
    s += hline(330, 284, 198, marker="arrow", stroke=MUTED)
    # pool
    s += box(330, 232, 340, 150, fill="#ffffff", stroke=INK)
    s += tag(338, 238, "executor", stroke=MUTED, w=66)
    s += txt(344, 270, "requests 6 dynamic background workers", size=8.5, anchor="start")
    s += txt(344, 286, "from max_worker_processes (8) · max_parallel_workers (1 here)", size=8.5, anchor="start")
    for i in range(8):
        fx = 344 + i * 34
        used = i < 7
        s += f'<rect x="{fx}" y="{300}" width="28" height="20" rx="3" fill="{INK if used else ACCENT}" fill-opacity="{0.25 if used else 0.8}" stroke="{INK if used else ACCENT}" stroke-width="0.8"/>'
    s += mono(344, 338, "7 of 8 slots unavailable to parallel query (max_parallel_workers = 1)", size=7.5, fill=MUTED, anchor="start")
    s += mono(344, 352, "→ 1 launched · the leader runs the plan too, so it still completes", size=8, fill=ACCENT, anchor="start")
    s += mono(344, 368, "on the default pool the same plan launched all 6", size=7.5, fill=SOFT, anchor="start")
    s += hline(330, 284, 360, marker="arrow", stroke=MUTED)
    # results table
    s += box(680, 90, 296, 200, fill="rgba(45,49,66,0.04)", stroke=MUTED, dash="4,3")
    s += tag(688, 96, "the lab's four runs", stroke=MUTED, w=120)
    rows = [("defaults", "2", "2"), ("per_gather = 6 only", "2", "2"), ("+ table parallel_workers = 6", "6", "6"), ("+ max_parallel_workers = 1", "6", "1")]
    s += mono(700, 132, "setting", size=7.5, fill=SOFT, anchor="start")
    s += mono(900, 132, "planned", size=7.5, fill=SOFT, anchor="end")
    s += mono(960, 132, "launched", size=7.5, fill=SOFT, anchor="end")
    for i, (a, b, c) in enumerate(rows):
        yy = 152 + i * 22
        s += mono(700, yy, a, size=8, fill=INK, anchor="start")
        s += mono(900, yy, b, size=8, fill=INK, anchor="end", weight="600")
        s += mono(960, yy, c, size=8, fill=ACCENT if b != c else INK, anchor="end", weight="600")
    s += mono(700, 262, "caught in pg_stat_activity: one client backend", size=7.5, fill=SOFT, anchor="start")
    s += mono(700, 274, "with leader_pid null, four parallel workers with its pid", size=7.5, fill=SOFT, anchor="start")
    return emit("26", "planned-vs-launched", "Planned is a decision; launched is a request",
                "The planner decides against a ceiling and cannot see the pool. The executor asks the pool and gets what is free.",
                "parallel workers", vw, vh, s)


# ------------------------------------------------------------------ FIG 27
def fig27():
    vw, vh = 1016, 552
    s = eyebrow(32, 44, "every process kind a 16 server can run, the condition that summons each, and the one it no longer runs")
    cx, cy = 508, 250
    # connectors first, so the centre box and the nodes occlude them
    for x, y, _n, _c in [(110, 90, 0, 0), (330, 76, 0, 0), (686, 76, 0, 0), (906, 90, 0, 0), (110, 250, 0, 0), (906, 250, 0, 0),
                          (110, 410, 0, 0), (330, 424, 0, 0), (686, 424, 0, 0), (906, 410, 0, 0)]:
        s += f'<line x1="{x}" y1="{y}" x2="{cx}" y2="{cy}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="2,3"/>'
    # centre: always present
    s += box(cx - 190, cy - 90, 380, 180, fill=ACCENT_TINT, stroke=ACCENT, rx=8)
    s += tag(cx - 182, cy - 84, "always present", stroke=ACCENT, w=100)
    s += txt(cx, cy - 50, "postmaster", size=12, weight="600", fill=ACCENT)
    for i, n in enumerate(("checkpointer", "background writer", "walwriter", "autovacuum launcher", "logical replication launcher")):
        s += txt(cx, cy - 26 + i * 20, n, size=10, weight="500")
    # around: conditional
    around = [
        (110, 90, "client backend", "one per connection"),
        (330, 76, "autovacuum worker", "launcher request, ≤ 3 at once"),
        (686, 76, "parallel worker", "a Gather node, from the 8-slot pool"),
        (906, 90, "startup", "crash recovery, or a standby"),
        (110, 250, "archiver", "archive_mode = on"),
        (906, 250, "walsender", "one per replica, ≤ 10"),
        (110, 410, "walreceiver", "on a standby"),
        (330, 424, "logical rep. apply worker", "one per subscription, ≤ 4"),
        (686, 424, "I/O worker × 3", "18+: io_method = worker"),
        (906, 410, "extension worker", "shared_preload_libraries"),
    ]
    for x, y, name, cond in around:
        s += box(x - 96, y - 24, 192, 48, fill="#ffffff", stroke=INK)
        s += txt(x, y - 4, name, size=9.5, weight="600")
        s += mono(x, y + 12, cond, size=7.5, fill=MUTED)
    # the removed one
    s += box(368, 466, 280, 40, fill="rgba(45,49,66,0.03)", stroke="rgba(45,49,66,0.3)", dash="4,3")
    s += txt(508, 483, "statistics collector", size=9.5, weight="600", fill=SOFT)
    s += f'<line x1="446" y1="480" x2="570" y2="480" stroke="{SOFT}" stroke-width="1.2"/>'
    s += mono(508, 498, "removed in 15 — stats live in shared memory now", size=7, fill=SOFT)
    s += note(32, 532, "every one of these is a child of the postmaster and a row in pg_stat_activity (since 10; archiver since 14)")
    return emit("27", "the-cast", "The whole cast",
                "The always-present six in the centre; around them, every process that exists only when something summons it; and one that was retired.",
                "the rest of the cast", vw, vh, s)


# ------------------------------------------------------------------ FIG 28
def fig28():
    vw, vh = 1016, 470
    s = eyebrow(32, 44, "which view watches which process, and where the view moved between 16 and 18")
    views = [("pg_stat_activity", "10+"), ("pg_stat_io", "16+"), ("pg_stat_bgwriter", "→ pg_stat_checkpointer in 17"), ("pg_stat_wal", "14+"),
             ("pg_stat_progress_vacuum", "cols renamed in 17"), ("log_checkpoints", "on by default 15+"), ("log_autovacuum_min_duration", "10 min default 15+")]
    procs = [("postmaster", [0, 0, 0, 0, 0, 0, 0]),
             ("client backend", [1, 1, 1, 1, 0, 0, 0]),
             ("checkpointer", [1, 1, 1, 0, 0, 1, 0]),
             ("background writer", [1, 1, 1, 0, 0, 0, 0]),
             ("WAL writer", [1, 0, 0, 1, 0, 0, 0]),
             ("autovacuum launcher", [1, 0, 0, 0, 0, 0, 0]),
             ("autovacuum worker", [1, 1, 0, 1, 1, 0, 1]),
             ("parallel worker", [1, 1, 0, 1, 0, 0, 0])]
    x0, y0, lw, rh = 32, 120, 150, 34
    cw = (952 - lw) / 7
    for j, (v, ver) in enumerate(views):
        x = x0 + lw + j * cw + cw / 2
        # alternate rows so long names can overhang a neighbour; the last one ends at the margin
        hx, anchor = (984, "end") if j == len(views) - 1 else (x, "middle")
        s += mono(hx, y0 - 50 if j % 2 == 0 else y0 - 34, v, size=8, fill=INK, weight="600", anchor=anchor)
        s += mono(x, y0 - 14, ver, size=7, fill=ACCENT if ("→" in ver or "renamed" in ver) else SOFT)
    for i, (name, marks) in enumerate(procs):
        y = y0 + i * rh
        s += f'<line x1="{x0}" y1="{y + rh}" x2="{x0 + lw + 7 * cw}" y2="{y + rh}" stroke="{RULE}" stroke-width="0.8"/>'
        s += txt(x0, y + 22, name, size=10, weight="600", fill=ACCENT if name == "postmaster" else INK, anchor="start")
        for j, m in enumerate(marks):
            cx = x0 + lw + j * cw + cw / 2
            if m:
                s += f'<circle cx="{cx}" cy="{y + 17}" r="5.5" fill="{INK}" fill-opacity="0.75"/>'
            else:
                s += f'<circle cx="{cx}" cy="{y + 17}" r="5.5" fill="none" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="2,2"/>'
    s += note(32, 418, "the postmaster has no view at all — only the server log knows what it did · nothing sees the fsync request queue directly except buffers_backend_fsync")
    s += legend(446, vw, [("the view reports this process", INK, "dot"), ("moved or renamed after 16", ACCENT, "line")])
    return emit("28", "tooling-map", "Which view sees which process",
                "Every process in this post, against the view or log setting that reports it, with the version where each moved.",
                "implementation", vw, vh, s)


ALL = {"15": fig15, "16": fig16, "17": fig17, "18": fig18, "19": fig19, "20": fig20, "21": fig21,
       "22": fig22, "23": fig23, "24": fig24, "25": fig25, "26": fig26, "27": fig27, "28": fig28}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
