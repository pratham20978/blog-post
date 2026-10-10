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

SLUGS = {1: "three-pools", 2: "fits-but-not-cached", 3: "the-clock-sweep",
         4: "7544-bytes-vs-176", 5: "work-mem-multiplies", 6: "where-85-mb-went"}


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
        s += mono(M, 1300, "how postgresql uses memory", size=14, fill=SOFT, anchor="start", track="0.16em")
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
    rows = [("shared buffers", "128 MB · 16,384 pages · every process maps it", 12, 3, True),
            ("WAL buffers", "4 MB · must reach disk before any page may", 5, 1, False),
            ("local memory", "work_mem · per sort, per hash, per process", 7, 2, False)]
    y = 520
    cw, gap = 40, 10
    for name, sub, n, h, focal in rows:
        for r in range(h):
            for c in range(n):
                x = M + c * (cw + gap)
                is_focal = focal and r == 1 and c == 4
                v += (f'<rect x="{x}" y="{y + r * (cw + gap)}" width="{cw}" height="{cw}" rx="5" '
                      f'fill="{ACCENT_TINT if is_focal else "#ffffff"}" stroke="{ACCENT if is_focal else "rgba(45,49,66,0.30)"}" '
                      f'stroke-width="{1.6 if is_focal else 1}"/>')
        yy = y + h * (cw + gap) + 22
        v += txt(M, yy, name, size=24, fill=INK, family=SANS, anchor="start", weight="600")
        v += mono(M, yy + 24, sub, size=14, fill=MUTED, anchor="start")
        y = yy + 66
    frame(1, 6, "postgresql foundations · part 1 of 3",
          ["PostgreSQL keeps RAM", "in three pools."],
          ["Not one cache. A shared page pool, a small log ring,",
           "and private working memory in every process."],
          v,
          ["The kernel's page cache is a fourth pool underneath —",
           "PostgreSQL relies on it and cannot see it."])


# ------------------------------------------------------------------ 02
def f02():
    v = ""
    x0, w = M, VW - 2 * M
    N = 16384
    def X(p):
        return x0 + w * p / N
    y = 640
    v += f'<line x1="{x0}" y1="{y}" x2="{x0 + w}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1.4"/>'
    for p in (0, 4096, 8192, 12288, 16384):
        v += f'<line x1="{X(p)}" y1="{y - 6}" x2="{X(p)}" y2="{y + 6}" stroke="{RULE_SOLID}" stroke-width="1.4"/>'
        v += mono(X(p), y + 28, f"{p:,}", size=13, fill=SOFT)
    v += mono(x0 + w, y + 54, "pages · the pool is 16,384", size=13, fill=SOFT, anchor="end", track="0.10em")
    v += hbar(x0, y - 70, X(710) - x0, 34, fill=INK, opacity=0.14, stroke=INK)
    v += mono(X(710) + 12, y - 47, "customers · 710 pages · cached whole", size=15, fill=INK, anchor="start", weight="500")
    v += hbar(x0, y - 124, X(7693) - x0, 34, fill=ACCENT, opacity=0.16, stroke=ACCENT)
    v += mono(X(7693) + 12, y - 101, "orders · 7,693 pages", size=15, fill=ACCENT, anchor="start", weight="600")
    v += f'<line x1="{X(4096)}" y1="{y - 140}" x2="{X(4096)}" y2="{y + 70}" stroke="{ACCENT}" stroke-width="1.6" stroke-dasharray="6,4"/>'
    v += mono(X(4096), y + 96, "NBuffers / 4 = 4,096 pages", size=14, fill=ACCENT, weight="600")
    v += txt(M, 840, "Over the line, a scan runs through a 32-buffer ring", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 872, "and leaves 256 KB behind. The lab: shared hit=32 read=7661,", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 904, "every time, with 16,352 empty slots looking on.", size=20, fill=INK, family=SANS, anchor="start")
    frame(2, 6, "the surprise",
          ["It fits in cache.", "It is not cached."],
          ["A 60 MB table, a 128 MB pool, and after every scan",
           "exactly 32 of its 7,693 pages are in shared buffers."],
          v,
          ["The buffer manager does not ask 'does it fit?'. It asks",
           "'is this table bigger than a quarter of the pool?'"])


# ------------------------------------------------------------------ 03
def f03():
    v = ""
    counts = [3, 0, 1, 5, 0, 2, 1, 0]
    after = [2, 0, 0, 4, 0, 2, 1, 0]
    cw, gap = 108, 12
    for k, (title, cs, victim) in enumerate((("the hand starts at buffer 1", counts, None), ("four steps later: buffer 5 is the victim", after, 4))):
        y = 540 + k * 200
        v += mono(M, y - 16, title, size=14, fill=INK, anchor="start", weight="500", track="0.06em")
        for i, c in enumerate(cs):
            x = M + i * (cw + gap)
            pinned = i == 1
            is_victim = victim == i
            fill = ACCENT_TINT if is_victim else ("rgba(45,49,66,0.10)" if pinned else "#ffffff")
            stroke = ACCENT if is_victim else (INK if pinned else "rgba(45,49,66,0.30)")
            v += box(x, y, cw, 84, fill=fill, stroke=stroke, rx=8)
            v += mono(x + cw / 2, y + 40, str(c), size=30, fill=ACCENT if is_victim else INK, weight="600")
            v += mono(x + cw / 2, y + 66, "pinned" if pinned else f"buf {i + 1}", size=12, fill=INK if pinned else SOFT)
        hx = M + (0 if k == 0 else 4) * (cw + gap) + cw / 2
        v += f'<path d="M {hx} {y + 100} L {hx - 9} {y + 118} L {hx + 9} {y + 118} Z" fill="{ACCENT}"/>'
    v += txt(M, 960, "Pinned: skip. Count above 0: subtract one, skip. Count 0: evict.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 992, "Nothing is reordered; the hand is the only shared state.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1024, "In the lab, 710 pages at count 5 survived; 7,373 at count 1 did not.", size=20, fill=INK, family=SANS, anchor="start")
    frame(3, 6, "the policy",
          ["Not LRU. A clock,", "and a counter from 0 to 5."],
          ["Every visit raises a page's counter; every pass of the hand",
           "lowers it. The first unpinned zero is the victim."],
          v,
          ["ARC lasted three months in 2005 (a patent). 2Q lasted seven.",
           "The clock sweep has run since 8.1, because it never takes a list lock."])


# ------------------------------------------------------------------ 04
def f04():
    v = ""
    x0 = M
    sc = 0.115
    y = 560
    v += txt(M, y - 20, "first update after CHECKPOINT", size=20, fill=INK, family=SANS, anchor="start", weight="600")
    w = 7408 * sc
    v += hbar(x0, y, w, 60, fill=ACCENT, opacity=0.18, stroke=ACCENT)
    v += mono(x0 + w / 2, y + 36, "full-page image · 7,408 bytes", size=16, fill=ACCENT, weight="600")
    v += hbar(x0 + w, y, 65 * sc, 60, fill=INK, opacity=0.25, stroke=INK)
    v += hbar(x0 + w + 65 * sc + 6, y, 34 * sc, 60, fill=INK, opacity=0.25, stroke=INK)
    v += mono(x0, y + 90, "7,544 bytes of WAL for a two-byte change", size=15, fill=INK, anchor="start")
    y = 760
    v += txt(M, y - 20, "second update, same row, same page", size=20, fill=INK, family=SANS, anchor="start", weight="600")
    x = x0
    for b in (59, 70, 34):
        v += hbar(x, y, b * sc, 60, fill=INK, opacity=0.25, stroke=INK)
        x += b * sc + 3
    v += mono(x + 14, y + 36, "← 176 bytes, to the same scale", size=16, fill=INK, anchor="start", weight="600")
    v += mono(x0, y + 90, "PRUNE 59 · HOT_UPDATE 70 · COMMIT 34", size=15, fill=MUTED, anchor="start")
    v += txt(M, 960, "The first change to a page after a checkpoint logs the whole page,", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 992, "because an 8 KB disk write is not assumed to be atomic.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1024, "The hole between line pointers and tuples is skipped: 8,192 − 784.", size=20, fill=INK, family=SANS, anchor="start")
    frame(4, 6, "the write-ahead rule",
          ["7,544 bytes,", "then 176."],
          ["pg_walinspect on the same one-column UPDATE, run twice.",
           "The only difference: a checkpoint before the first."],
          v,
          ["A dirty page cannot be written until the log describing it is on disk.",
           "That rule is why checkpoints, wal_buffers and shared_buffers are one decision."])


# ------------------------------------------------------------------ 05
def f05():
    v = ""
    cols = [("leader", M), ("worker 1", M + 316), ("worker 2", M + 632)]
    for lab, x in cols:
        v += box(x, 520, 288, 300, fill="rgba(45,49,66,0.02)", stroke="rgba(45,49,66,0.30)", rx=10, dash="6,4")
        v += mono(x + 144, 552, lab, size=14, fill=INK, track="0.12em", weight="500")
        v += box(x + 20, 580, 248, 92, fill="#ffffff", stroke=INK, rx=8)
        v += txt(x + 144, 616, "Sort", size=22, fill=INK, family=SANS, weight="600")
        v += mono(x + 144, 646, "external merge · 2.5 MB", size=13, fill=MUTED)
        v += box(x + 20, 696, 248, 100, fill=ACCENT_TINT, stroke=ACCENT, rx=8)
        v += txt(x + 144, 734, "HashAggregate", size=22, fill=ACCENT, family=SANS, weight="600")
        v += mono(x + 144, 762, "2,065 kB · 9 batches", size=13, fill=ACCENT)
        v += mono(x + 144, 782, "7.5 MB on disk", size=13, fill=MUTED)
    v += txt(M, 880, "work_mem was 1 MB. EXPLAIN printed 'Memory Usage: 2065kB' three times", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 912, "and 'external merge' three times: six budgets for one query.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 970, "worst case = work_mem × operations × (leader + workers) × sessions", size=20, fill=ACCENT, family=SANS, anchor="start", weight="600")
    v += txt(M, 1002, "256 MB × 9 × 3 × 20 connections = 138 GB. Nothing stops it.", size=20, fill=INK, family=SANS, anchor="start")
    frame(5, 6, "local memory",
          ["work_mem is not", "a connection limit."],
          ["It is a limit per sort or hash, per process — and hash tables",
           "get twice it (hash_mem_multiplier = 2.0)."],
          v,
          ["The failure is not a slow query. It is the kernel killing a backend,",
           "which takes the whole server down with it. Set it per session."])


# ------------------------------------------------------------------ 06
def f06():
    v = ""
    x0, w = M, VW - 2 * M
    total = 85_132_832
    parts = [("SortTuple array", 25_174_064, ACCENT), ("the tuples themselves", 58_720_256, INK), ("rest", 1_238_512, SOFT)]
    x = x0
    y = 540
    for name, b, col in parts:
        pw = w * b / total
        v += hbar(x, y, pw, 70, fill=col, opacity=0.16 if col == ACCENT else 0.12, stroke=col)
        if pw > 90:
            v += mono(x + pw / 2, y + 32, name, size=14, fill=col if col != SOFT else MUTED, weight="600")
            v += mono(x + pw / 2, y + 54, f"{b / 1e6:.1f} MB", size=14, fill=col if col != SOFT else MUTED)
        x += pw
    v += mono(M, 640, "2²⁰ slots × 24 bytes = 25.2 MB · 1,000,000 chunks in 17 blocks = 58.7 MB", size=14, fill=MUTED, anchor="start")
    vals = [("idle", 12, MUTED), ("cursor open, sort done", 97, ACCENT), ("after CLOSE", 18, INK)]
    y = 700
    for lab, mb, col in vals:
        v += mono(M, y + 28, lab, size=14, fill=INK, anchor="start")
        bw = mb * 6.4
        v += hbar(M + 250, y + 6, bw, 34, fill=col, opacity=0.16 if col == ACCENT else 0.12, stroke=col)
        v += mono(M + 250 + bw + 12, y + 28, f"{mb} MB", size=16, fill=col, anchor="start", weight="600")
        y += 60
    v += mono(M, 900, "resident set of one backend (VmRSS), PostgreSQL 16.2, work_mem = 256 MB", size=13, fill=SOFT, anchor="start")
    v += txt(M, 960, "The memory came back in one call: the executor's context was deleted", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 992, "with every child, and no tuple was freed individually.", size=20, fill=INK, family=SANS, anchor="start")
    v += txt(M, 1024, "Twenty-two figures, one lab, and every number reproducible.", size=20, fill=INK, family=SANS, anchor="start")
    frame(6, 6, "memory contexts",
          ["Where 85 MB went,", "and how it came back."],
          ["A backend never frees a sort's million tuples one by one.",
           "It drops the context they live in."],
          v,
          ["Three pools, one rule, and a lab you can run: PostgreSQL 16.2,",
           "default settings, two tables, every EXPLAIN quoted verbatim."],
          cta="read it on canery →")


FRAMES = {"01": f01, "02": f02, "03": f03, "04": f04, "05": f05, "06": f06}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(FRAMES)
    for kk in want:
        FRAMES[kk]()
