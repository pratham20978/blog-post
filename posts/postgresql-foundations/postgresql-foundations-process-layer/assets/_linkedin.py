#!/usr/bin/env python3
"""LinkedIn carousel frames — 4:5, built in the diagram-design skin.

blog-visuals stops at prompts because image models mangle typography. Built here
instead, the frames carry real Instrument Serif headlines and the lab's own numbers.
The illustration prompts in linkedin-prompts.md remain the alternative route.

Run:  python3 _linkedin.py           # all frames
      python3 _linkedin.py 03 05     # only those
"""
import math
import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, FONTS, INK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SANS, SERIF, SOFT, box, mono, rasterize, svg_doc, txt)
from _figs_a import hbar

HERE = pathlib.Path(__file__).resolve().parent
VW, VH = 1080, 1350
M = 80

SLUGS = {1: "one-parent", 2: "five-passes", 3: "thirty-seconds",
         4: "one-budget", 5: "sixteen-times", 6: "one-killed-backend"}


def frame(num, total, kicker, headline, deck, visual, takeaway, cta=None):
    s = ""
    s += mono(M, 120, kicker, size=15, fill=SOFT, anchor="start", track="0.24em", weight="500")
    s += mono(VW - M, 120, f"{num} / {total}", size=15, fill=ACCENT if num == total else SOFT,
              anchor="end", track="0.24em", weight="500")
    s += f'<line x1="{M}" y1="148" x2="{VW - M}" y2="148" stroke="{RULE}" stroke-width="1"/>'
    y = 232
    for line in headline:
        s += txt(M, y, line, size=58, fill=INK, family=SERIF, anchor="start")
        y += 68
    y += 6
    for line in deck:
        s += txt(M, y, line, size=21, fill=MUTED, family=SANS, anchor="start")
        y += 30
    s += visual
    s += f'<line x1="{M}" y1="1176" x2="{VW - M}" y2="1176" stroke="{RULE}" stroke-width="1"/>'
    ty = 1216
    for line in takeaway:
        s += txt(M, ty, line, size=22, fill=INK, family=SANS, anchor="start", weight="500")
        ty += 30
    if cta:
        s += mono(M, 1300, cta, size=14, fill=ACCENT, anchor="start", track="0.16em")
    else:
        s += mono(M, 1300, "how postgresql uses processes", size=14, fill=SOFT, anchor="start", track="0.16em")
    s += mono(VW - M, 1300, "canery", size=14, fill=SOFT, anchor="end", track="0.24em")
    svg = svg_doc(VW, VH, s)
    stem = f"linkedin-{num:02d}-{SLUGS[num]}"
    (HERE / f"{stem}.svg").write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    (HERE / f"{stem}.html").write_text(
        f'<!doctype html><meta charset="utf-8"><title>{stem}</title>'
        f'<link href="{FONTS}" rel="stylesheet">'
        f'<style>body{{margin:0;background:{PAPER}}}</style>{svg}', encoding="utf-8")
    rasterize(HERE / f"{stem}.svg", HERE / f"{stem}.png", VW, VH, svg_markup=svg)
    print(f"  {stem}: html + svg + png ({VW}x{VH} @2x)")


# ------------------------------------------------------------------ 01
def f01():
    v = ""
    cw = 44
    px, py = M + 300, 520
    v += f'<rect x="{px}" y="{py}" width="{cw}" height="{cw}" rx="6" fill="{ACCENT_TINT}" stroke="{ACCENT}" stroke-width="1.6"/>'
    v += mono(px + cw / 2, py - 16, "postmaster · never touches your data", size=14, fill=ACCENT, track="0.10em")
    kids = ["backend", "backend", "backend", "checkpointer", "bg writer", "WAL writer", "av launcher", "av worker", "parallel wkr"]
    n = len(kids)
    gap = (VW - 2 * M - n * cw) / (n - 1)
    ry = 760
    for i, k in enumerate(kids):
        x = M + i * (cw + gap)
        v += f'<line x1="{px + cw / 2}" y1="{py + cw}" x2="{x + cw / 2}" y2="{ry}" stroke="rgba(45,49,66,0.30)" stroke-width="1"/>'
        v += f'<rect x="{x}" y="{ry}" width="{cw}" height="{cw}" rx="6" fill="#ffffff" stroke="rgba(45,49,66,0.40)" stroke-width="1"/>'
        v += f'<text x="{x + cw / 2}" y="{ry + cw + 20}" transform="rotate(-30 {x + cw / 2} {ry + cw + 20})" font-size="12" font-family="{MONO}" fill="{MUTED}" text-anchor="end">{k}</text>'
    v += txt(M, 930, "Every process in a PostgreSQL server is a child of one", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 962, "supervisor that never runs a query, never reads a page,", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 994, "and is the only process allowed to fork.", size=20, fill=INK, family=SANS, anchor="start")
    frame(1, 6, "postgresql foundations · part 2 of 3",
          ["PostgreSQL is not", "one program."],
          ["It is a supervisor and a crowd of single-purpose",
           "processes: one per connection, plus a fixed background cast."],
          v,
          ["The autovacuum launcher cannot start a worker. A parallel",
           "query cannot start its own. Every one of them asks the postmaster."])


# ------------------------------------------------------------------ 02
def f02():
    v = ""
    y0 = 560
    for i, (label, passes, col) in enumerate((("maintenance_work_mem = 1 MB", 5, ACCENT), ("maintenance_work_mem = 256 MB", 1, INK))):
        y = y0 + i * 190
        v += mono(M, y - 14, label, size=15, fill=col, anchor="start", track="0.08em", weight="600")
        v += hbar(M, y, VW - 2 * M, 30, fill=col, opacity=0.08, stroke=col)
        v += mono(M + 12, y + 20, "heap: 7,693 pages, read once", size=13, fill=col, anchor="start")
        for k in range(passes):
            x = M + k * ((VW - 2 * M) / passes)
            v += hbar(x, y + 46, (VW - 2 * M) / passes - 8, 44, fill=col, opacity=0.18 + 0.05 * k, stroke=col)
            v += mono(x + ((VW - 2 * M) / passes - 8) / 2, y + 73, "both indexes, in full", size=12 if passes == 5 else 14, fill=col)
        v += mono(M, y + 118, f"{passes} index pass{'es' if passes > 1 else ''} · {passes * 2603:,} index pages read", size=15, fill=col, anchor="start", weight="600")
    v += txt(M, 970, "In 16 a dead tuple costs 6 bytes of memory. When the list fills,", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1002, "vacuum stops, walks every index in full, and resumes. 1 MB holds", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1034, "174,761 of them; 800,000 dead rows means five complete passes.", size=20, fill=INK, family=SANS, anchor="start")
    frame(2, 6, "the surprise",
          ["Same delete.", "Five index passes."],
          ["800,000 dead tuples, two indexes, one setting changed:",
           "the vacuum read its indexes five times instead of once."],
          v,
          ["passes = ⌈ dead tuples × 6 B / maintenance_work_mem ⌉.",
           "On a churning table, that one setting decides how long vacuum takes."])


# ------------------------------------------------------------------ 03
def f03():
    v = ""
    x0, w = M, VW - 2 * M
    y = 640
    def X(t):
        return x0 + w * t / 36.0
    v += f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1.4"/>'
    for t in range(0, 31, 5):
        v += f'<line x1="{X(t)}" y1="{y - 6}" x2="{X(t)}" y2="{y + 6}" stroke="{RULE_SOLID}" stroke-width="1.4"/>'
        v += mono(X(t), y + 28, f"{t} s", size=13, fill=SOFT)
    v += f'<circle cx="{X(0)}" cy="{y}" r="8" fill="{INK}"/>'
    v += mono(X(0) + 16, y - 60, "UPDATE 30,000 rows", size=15, fill=INK, anchor="start", weight="600")
    v += mono(X(0) + 16, y - 38, "threshold 20,050 crossed at once", size=13, fill=MUTED, anchor="start")
    v += hbar(X(0), y - 5, X(30) - X(0), 10, fill=MUTED, opacity=0.18)
    v += mono(X(15), y - 100, "30.0 seconds · the launcher is asleep", size=15, fill=MUTED, weight="500")
    v += f'<circle cx="{X(30)}" cy="{y}" r="8" fill="{ACCENT}"/>'
    v += mono(X(30) - 16, y + 80, "worker forked", size=15, fill=ACCENT, anchor="end", weight="600")
    v += mono(X(30) - 16, y + 102, "30,000 removed in 0.03 s", size=13, fill=ACCENT, anchor="end")
    v += txt(M, 840, "The launcher visits each database once per autovacuum_naptime,", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 872, "60 s by default, round-robin. It does not watch tables; it keeps", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 904, "time. A table that qualifies waits for the next visit — up to a minute.", size=20, fill=INK, family=SANS, anchor="start")
    frame(3, 6, "the launcher's clock",
          ["Thirty seconds waiting.", "Thirty milliseconds working."],
          ["The table crossed its threshold the instant the UPDATE",
           "committed. Nobody looked for half a minute. Nothing was misconfigured."],
          v,
          ["Expected arrival: naptime / 2. Worst case: naptime, plus queueing",
           "for one of three worker slots. Halving naptime halves the wait, not the work."])


# ------------------------------------------------------------------ 04
def f04():
    v = ""
    tw = VW - 2 * M
    for i, (label, n) in enumerate((("one worker", 1), ("three workers", 3), ("eight workers", 8))):
        y = 560 + i * 120
        v += mono(M, y - 14, f"{label} · {200 // n} cost units per 2 ms each", size=15, fill=INK if n > 1 else ACCENT, anchor="start", track="0.06em", weight="600")
        seg = tw / n
        for k in range(n):
            v += hbar(M + k * seg, y, seg - (6 if n > 1 else 0), 54, fill=ACCENT if n == 1 else INK, opacity=0.16, stroke=ACCENT if n == 1 else INK)
            if n <= 3:
                v += mono(M + k * seg + (seg - 6) / 2, y + 32, f"limit {200 // n}", size=14, fill=ACCENT if n == 1 else INK, weight="600")
        v += mono(M + tw, y + 74, "= 200 units / 2 ms · the same total", size=13, fill=SOFT, anchor="end")
    v += txt(M, 970, "autovacuum_vacuum_cost_limit is divided among the running", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1002, "workers. The bar's width is the cluster's vacuum I/O ceiling —", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1034, "about 39 MB/s of dirtied pages at the defaults — and it never moves.", size=20, fill=INK, family=SANS, anchor="start")
    frame(4, 6, "the mistake",
          ["More workers.", "Same speed."],
          ["Raising autovacuum_max_workers from 3 to 8 cannot make",
           "vacuum keep up, because all of them share one budget."],
          v,
          ["To vacuum faster, raise the budget. Add workers only when",
           "many tables need vacuuming at the same time."])


# ------------------------------------------------------------------ 05
def f05():
    v = ""
    x0 = M
    y0, h = 560, 300
    top = 15000
    for i, (label, tps, syncs, col) in enumerate((("synchronous_commit = on", 867, 5000, INK), ("synchronous_commit = off", 13771, 2, ACCENT))):
        bx = x0 + 60 + i * 440
        bh = tps / top * h
        v += hbar(bx, y0 + h - bh, 180, bh, fill=col, opacity=0.16, stroke=col)
        v += txt(bx + 90, y0 + h - bh - 16, f"{tps:,}", size=36, fill=col, family=SERIF)
        v += mono(bx + 90, y0 + h + 28, label, size=13, fill=INK, track="0.04em")
        v += mono(bx + 90, y0 + h + 50, f"transactions per second", size=12, fill=SOFT)
        v += mono(bx + 90, y0 + h + 84, f"{syncs:,} fdatasync calls", size=14, fill=col, weight="600")
        v += mono(bx + 90, y0 + h + 104, "for 5,000 commits", size=12, fill=SOFT)
    v += f'<line x1="{x0}" y1="{y0 + h}" x2="{VW - M}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1.4"/>'
    v += txt(M, 1000, "With on, the committing backend waits for the disk to confirm its", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1032, "log record. With off, it replies at once and the WAL writer flushes", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1064, "within 3 × wal_writer_delay = 600 ms. Nothing can be corrupted.", size=20, fill=INK, family=SANS, anchor="start")
    frame(5, 6, "what a commit waits for",
          ["Sixteen times faster.", "Zero corruption risk."],
          ["5,000 single-row commits on the same disk. The only difference",
           "is whether the backend waits for fdatasync before replying."],
          v,
          ["off risks the last 600 ms of commits in a crash, never consistency.",
           "It is a per-transaction setting: off for the reload, on for the payment."])


# ------------------------------------------------------------------ 06
def f06():
    v = ""
    lines = ['LOG:  server process (PID 130554) was terminated by signal 9: Killed',
             'LOG:  terminating any other active server processes',
             'LOG:  all server processes terminated; reinitializing',
             'LOG:  database system was not properly shut down;',
             '      automatic recovery in progress',
             'LOG:  redo starts at 3/73592518',
             'LOG:  database system is ready to accept connections']
    v += box(M, 520, VW - 2 * M, 250, fill="rgba(45,49,66,0.04)", stroke=RULE_SOLID, rx=8)
    for i, l in enumerate(lines):
        col = ACCENT if i == 1 else INK
        v += mono(M + 24, 556 + i * 30, l, size=13.5, fill=col, anchor="start", weight="600" if i == 1 else "400")
    v += txt(M, 830, "The postmaster never reads shared memory, so it cannot know what", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 862, "a killed backend left behind. It does the only safe thing: terminate", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 894, "every child, reset, recover. Two seconds later it was serving again.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 960, "That is the design, not a fault. Find the child in the line above.", size=20, fill=ACCENT, family=SANS, anchor="start", weight="500")
    frame(6, 6, "the log line everyone misreads",
          ["One backend killed.", "Every session dropped."],
          ["kill -9 on one connection. An innocent second connection got",
           "'server closed the connection unexpectedly'. Here is why."],
          v,
          ["Eleven processes, what each decides, and a lab you can run:",
           "PostgreSQL 16.2, default settings, every number quoted verbatim."],
          cta="read it on canery →")


FRAMES = {"01": f01, "02": f02, "03": f03, "04": f04, "05": f05, "06": f06}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FRAMES)
    for kk in want:
        FRAMES[kk]()
