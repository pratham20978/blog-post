#!/usr/bin/env python3
"""Figures 01-14 for postgresql-foundations-process-layer. Every number is from lab/captures.md
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


def lane(x, y1, y2, label, w=124):
    s = f'<line x1="{x}" y1="{y1}" x2="{x}" y2="{y2}" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="2,3"/>'
    s += box(x - w / 2, y1 - 30, w, 26, fill="#ffffff", stroke=INK, rx=4)
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


def note(x, y, text, w=None):
    return mono(x, y, text, size=8, fill=SOFT, anchor="start", track="0.02em")


def wrap(s, size, width):
    """Fewest Geist Mono lines at `size` that fit `width`, evened out so no line is a stub."""
    adv, words = 0.605 * size, s.split()

    def greedy(limit):
        lines, cur = [], ""
        for w in words:
            t = f"{cur} {w}".strip()
            if len(t) * adv <= limit or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        return lines + [cur]

    best = greedy(width)
    lim = width
    while lim > max(len(w) for w in words) * adv:
        lim -= adv
        g = greedy(lim)
        if len(g) > len(best):
            break
        best = g
    return best


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 326
    s = eyebrow(32, 44, "the three layers, and where this post sits")
    layers = [
        ("memory layer", "shared buffers · WAL buffers · per-process memory · the rest of shared memory", "done", "part 1"),
        ("process layer", "postmaster · backends · checkpointer · background writer · WAL writer · autovacuum · parallel workers", "focal", "part 2 · this post"),
        ("storage layer", "heap files · indexes · visibility map · WAL segments · pg_xact", "next", "part 3"),
    ]
    y = 72
    for name, sub, state, part in layers:
        focal = state == "focal"
        done = state == "done"
        s += box(32, y, 952, 62, fill=ACCENT_TINT if focal else ("rgba(45,49,66,0.04)" if done else "#ffffff"),
                 stroke=ACCENT if focal else ("rgba(45,49,66,0.35)" if done else INK))
        s += txt(56, y + 27, name, size=14, weight="600", fill=ACCENT if focal else (SOFT if done else INK), anchor="start", family=SANS)
        s += mono(56, y + 47, sub, size=9, fill=SOFT if done else MUTED, anchor="start")
        s += tag(846, y + 8, part, stroke=ACCENT if focal else MUTED, w=122)
        y += 74
    s += note(32, y + 14, "this post links up to part 1 for memory facts and stops where bytes hit a file format (part 3)")
    return emit("01", "three-layers", "The three layers of a PostgreSQL server",
                "Memory, process, storage. Part 1 was the top layer; this post is the middle one.",
                "the series", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "ps -o pid,ppid,rss,args --ppid 128882 -p 128882 — PostgreSQL 16.2, no client connected")
    # postmaster
    s += node(348, 76, 320, 66, "postmaster", "pid 128882 · rss 18,176 kB · ppid 3166 (the shell)", kind="focal", tagtext="the only parent")
    kids = [
        ("checkpointer", "129064", "90,240 kB — shared pages touched", "dirty pages · fsyncs · checkpoints"),
        ("background writer", "129065", "5,404 kB", "cleans ahead of the clock hand"),
        ("walwriter", "129144", "8,204 kB", "flushes WAL nobody flushed"),
        ("autovacuum launcher", "129145", "6,768 kB", "picks a database, asks for a worker"),
        ("logical replication launcher", "129146", "5,856 kB", "idle without a subscription"),
    ]
    n = len(kids)
    cw, gap = 176, 16
    x0 = (vw - (n * cw + (n - 1) * gap)) / 2
    busy = 224
    s += vline(508, 142, 176, stroke=MUTED, marker=None)
    s += hline(x0 + cw / 2, x0 + (n - 1) * (cw + gap) + cw / 2, 176, stroke=MUTED, marker=None)
    for i, (name, pid, rss, job) in enumerate(kids):
        x = x0 + i * (cw + gap)
        s += vline(x + cw / 2, 176, busy - 2, stroke=MUTED)
        s += box(x, busy, cw, 92, fill="#ffffff", stroke=INK)
        s += txt(x + cw / 2, busy + 24, name, size=10, weight="600")
        s += mono(x + cw / 2, busy + 42, f"pid {pid} · ppid 128882", size=8, fill=MUTED)
        s += mono(x + cw / 2, busy + 56, rss, size=8, fill=SOFT)
        s += mono(x + cw / 2, busy + 76, job, size=7, fill=SOFT)
    s += note(32, 350, "five children exist before any client connects · every ppid is 128882 · rss counts touched shared pages, which is why the checkpointer's is large")
    s += legend(376, vw, [("the supervisor", ACCENT, "box"), ("a child, forked by the postmaster", INK, "hollow")])
    return emit("02", "process-tree", "A 16.2 server at rest",
                "The postmaster and five children, none of them serving a client. `ps --ppid` confirms the parent of every one is the postmaster.",
                "the process layer", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 470
    s = eyebrow(32, 44, "which process touches which pool from part 1 — a mark means 'reads or writes it in normal operation'")
    pools = ["shared buffers", "WAL buffers", "local memory", "the disk"]
    rows = [
        ("postmaster", [0, 0, 0, 0], "creates shared memory, then never touches it"),
        ("client backend", [1, 1, 1, 1], "pages, WAL, work_mem, files on a miss"),
        ("checkpointer", [1, 0, 0, 1], "writes every dirty page, fsyncs every file"),
        ("background writer", [1, 0, 0, 1], "writes some dirty pages ahead of the sweep"),
        ("WAL writer", [0, 1, 0, 1], "flushes the WAL ring to its segment"),
        ("autovacuum worker", [2, 1, 1, 1], "own 256 kB ring · maintenance_work_mem"),
        ("parallel worker", [1, 1, 1, 1], "a backend in every respect, with its own work_mem"),
        ("autovacuum launcher", [0, 0, 0, 0], "reads pg_database, decides, signals"),
    ]
    x0, y0, lw, cw, rh = 32, 92, 190, 128, 38
    for j, p in enumerate(pools):
        s += txt(x0 + lw + j * cw + cw / 2, y0 - 12, p, size=10, weight="600")
    for i, (name, marks, why) in enumerate(rows):
        y = y0 + i * rh
        focal = name == "postmaster"
        s += f'<line x1="{x0}" y1="{y + rh}" x2="{x0 + lw + 4 * cw}" y2="{y + rh}" stroke="{RULE}" stroke-width="0.8"/>'
        s += txt(x0, y + 24, name, size=11, weight="600", fill=ACCENT if focal else INK, anchor="start")
        for j, m in enumerate(marks):
            cx = x0 + lw + j * cw + cw / 2
            if m == 1:
                s += f'<circle cx="{cx}" cy="{y + 19}" r="6" fill="{INK}" fill-opacity="0.75"/>'
            elif m == 2:
                s += f'<circle cx="{cx}" cy="{y + 19}" r="6" fill="none" stroke="{INK}" stroke-width="1.4"/>'
                s += f'<circle cx="{cx}" cy="{y + 19}" r="2.5" fill="{INK}"/>'
            else:
                s += f'<circle cx="{cx}" cy="{y + 19}" r="6" fill="none" stroke="{RULE_SOLID}" stroke-width="0.8" stroke-dasharray="2,2"/>'
        s += mono(x0 + lw + 4 * cw + 14, y + 23, why, size=7.5, fill=SOFT, anchor="start")
    s += note(32, 418, "the postmaster's row is empty on purpose · the launcher's is empty because it decides and signals but never opens a table")
    s += legend(446, vw, [("touches it directly", INK, "dot"), ("through its own ring (part 1)", INK, "ring"), ("never", RULE_SOLID, "dashcircle")])
    return emit("03", "who-touches-what", "Who touches what",
                "Each process against the three memory pools from part 1 and the disk. The empty rows are the point.",
                "the process layer", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 380
    s = eyebrow(32, 44, "200 fresh connections vs 200 round trips on one open connection — log scale, per operation")
    x0, y0, w, h = 120, 84, 700, 200
    lo, hi = 0.01, 10.0
    def ty(v):
        return y0 + h - (math.log10(v / lo) / math.log10(hi / lo)) * h
    for v in (0.01, 0.1, 1, 10):
        yy = ty(v)
        s += f'<line x1="{x0}" y1="{yy}" x2="{x0 + w}" y2="{yy}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0 - 8, yy + 3, f"{v:g} ms", size=8, fill=SOFT, anchor="end")
    s += f'<line x1="{x0}" y1="{y0 + h}" x2="{x0 + w}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    # fresh connection bar, segmented by stage (proportions illustrative, total exact)
    bx, bw = x0 + 120, 150
    top = ty(1.762)
    s += hbar(bx, top, bw, y0 + h - top, fill=ACCENT, opacity=0.16, stroke=ACCENT)
    s += mono(bx + bw / 2, top - 8, "1.762 ms", size=10, fill=ACCENT, weight="600")
    s += txt(bx + bw / 2, y0 + h + 20, "one fresh connection", size=10, weight="600")
    s += mono(bx + bw / 2, y0 + h + 34, "fork · authenticate · InitPostgres · select 1 · close", size=7.5, fill=SOFT)
    # stage ticks along the accent bar (labels only; the lab did not time stages separately)
    for k, lab in enumerate(("fork()", "ClientAuthentication", "InitPostgres: PGPROC, caches", "query")):
        yy = top + (k + 0.5) * (y0 + h - top) / 4
        s += mono(bx + bw + 10, yy + 3, lab, size=7.5, fill=MUTED, anchor="start")
    bx2 = x0 + 470
    top2 = ty(0.0299)
    s += hbar(bx2, top2, bw, y0 + h - top2, fill=INK, opacity=0.12, stroke=INK)
    s += mono(bx2 + bw / 2, top2 - 8, "0.030 ms", size=10, fill=INK, weight="600")
    s += txt(bx2 + bw / 2, y0 + h + 20, "one round trip, open connection", size=10, weight="600")
    s += mono(bx2 + bw / 2, y0 + h + 34, "send · execute · reply", size=7.5, fill=SOFT)
    s += box(x0 + w - 148, y0 + 8, 148, 40, fill=ACCENT_TINT, stroke=ACCENT, rx=4)
    s += txt(x0 + w - 74, y0 + 25, "59×", size=16, weight="600", fill=ACCENT, family=SERIF)
    s += mono(x0 + w - 74, y0 + 40, "the case for a pooler", size=7.5, fill=ACCENT)
    s += note(32, 336, "Unix socket, trust authentication, laptop · a TCP + TLS + password connection is slower · fresh backend 13.0 MB resident, 14.5 MB after one catalog query")
    return emit("04", "connection-cost", "A connection costs about sixty queries",
                "Fork, authenticate, initialise, query, close — against send, execute, reply on a process that already exists.",
                "what a connection costs", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 330
    s = eyebrow(32, 44, "UPDATE customers … (30,000 rows, threshold 20,050) at t = 0 · autovacuum_naptime 60 s · two databases")
    x0, x1, y = 60, 956, 150
    def tx(t):
        return x0 + (x1 - x0) * t / 36.0
    s += f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{RULE_SOLID}" stroke-width="1"/>'
    for t in range(0, 31, 5):
        s += f'<line x1="{tx(t)}" y1="{y - 4}" x2="{tx(t)}" y2="{y + 4}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        s += mono(tx(t), y + 18, f"{t} s", size=8, fill=SOFT)
    # launcher visits: this database at t=0 (just missed), next at 60
    for t, lab in ((0, "launcher visited the other\ndatabase just before this"), (30, "launcher visits\nproclab")):
        s += vline(tx(t), y - 46, y - 8, stroke=MUTED if t != 30 else ACCENT, marker=None, dash="3,3")
        for k, l in enumerate(lab.split("\n")):
            s += mono(tx(t) if t else tx(0) + 4, y - 60 + k * 11, l, size=7.5, fill=MUTED if t != 30 else ACCENT,
                      anchor="middle" if t else "start")
    # the threshold crossed at 0
    s += f'<circle cx="{tx(0)}" cy="{y}" r="5" fill="{INK}"/>'
    s += mono(tx(0) + 10, y + 40, "threshold crossed: n_dead_tup 30,000 > 20,050", size=8, fill=INK, anchor="start")
    # the wait
    s += hbar(tx(0), y - 3, tx(30) - tx(0), 6, fill=MUTED, opacity=0.18)
    s += masked(tx(15), y - 12, "30.0 s of nothing — the launcher is asleep on its latch", size=8, fill=MUTED)
    # the work
    s += hbar(tx(30), y - 3, max(tx(30.03) - tx(30), 3), 6, fill=ACCENT, opacity=0.9)
    s += f'<circle cx="{tx(30)}" cy="{y}" r="5" fill="{ACCENT}"/>'
    s += mono(tx(30) - 10, y + 40, "postmaster forks worker 130208", size=8, fill=ACCENT, anchor="end")
    s += mono(tx(30) - 10, y + 54, "566 pages scanned · 30,000 removed · 1 index scan", size=8, fill=ACCENT, anchor="end")
    s += mono(tx(30) - 10, y + 68, "elapsed 0.03 s", size=8, fill=ACCENT, anchor="end", weight="600")
    s += note(32, 290, "expected wait: naptime / 2 on average, naptime at worst · the lab drew the average · halving naptime halves the wait and changes nothing about the work")
    return emit("05", "arrival-time", "Thirty seconds of waiting for thirty milliseconds of work",
                "The launcher visits each database once per naptime. The table qualified the instant the UPDATE committed; nobody looked for half a minute.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 440
    s = eyebrow(32, 44, "VACUUM of 800,000 dead tuples, two indexes (2,603 pages) — maintenance_work_mem 1 MB vs 256 MB, warm then cold")
    groups = [
        ("index passes", [5, 1, 5, 1], "{:.0f}", 6),
        ("elapsed, s", [0.258, 0.232, 1.100, 0.867], "{:.2f}", 1.3),
        ("buffer misses", [0, 0, 21283, 16575], "{:,.0f}", 24000),
        ("WAL records", [36022, 25670, 43715, 33363], "{:,.0f}", 48000),
    ]
    x0, y0, gw, h = 60, 92, 232, 210
    for gi, (title, vals, fmt, top) in enumerate(groups):
        gx = x0 + gi * gw
        s += txt(gx + gw / 2 - 8, y0 - 14, title, size=10, weight="600")
        s += f'<line x1="{gx}" y1="{y0 + h}" x2="{gx + gw - 24}" y2="{y0 + h}" stroke="{RULE_SOLID}" stroke-width="1"/>'
        bw = 38
        for j, v in enumerate(vals):
            cold = j >= 2
            small = j % 2 == 0
            col = ACCENT if small else INK
            bx = gx + 8 + j * (bw + 8) + (10 if cold else 0)
            bh = (v / top) * h
            s += hbar(bx, y0 + h - bh, bw, bh, fill=col, opacity=0.18 if cold else 0.10, stroke=col)
            s += mono(bx + bw / 2, y0 + h - bh - 6, fmt.format(v), size=7.5, fill=col, weight="600")
        s += mono(gx + 8 + bw + 4, y0 + h + 14, "warm", size=8, fill=SOFT)
        s += mono(gx + 8 + 2 * (bw + 8) + 10 + bw + 4, y0 + h + 14, "cold", size=8, fill=SOFT)
    s += note(32, 340, "warm: everything already in the 128 MB pool, so passes 2–5 are memory reads and the clock barely moves")
    s += note(32, 356, "cold: server restarted (shared buffers empty) and the heap and index files evicted from the kernel cache — each extra pass is now a disk read")
    s += note(32, 372, "the pass count is decided by arithmetic: ⌈800,000 / ((1 MB − 8 B) / 6 B − 291)⌉ = 5 · it does not care about the cache; each pass's price does")
    s += legend(410, vw, [("maintenance_work_mem = 1 MB", ACCENT, "box"), ("maintenance_work_mem = 256 MB", INK, "box")])
    return emit("06", "index-passes", "The same delete, vacuumed twice",
                "Five complete index passes at 1 MB, one at 256 MB, on identical data. Warm and cold, so the price of a pass is visible.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 380
    s = eyebrow(32, 44, "VACUUM (VERBOSE) vac_demo with a REPEATABLE READ snapshot held in another session, then after it commits")
    panels = [
        ("snapshot held", ACCENT, ["7,693 pages scanned (100%)", "index scans: 0", "0 removed", "800,000 dead but not yet removable", "removable cutoff 71185 — 1 XID old"],
         "the holder: pid 130456 · idle in transaction · backend_xmin 71185"),
        ("snapshot released", INK, ["7,693 pages scanned (100%)", "index scans: 1", "800,000 removed", "0 dead but not yet removable", "removable cutoff 71186"],
         "same table, same dead tuples, one COMMIT in the other window"),
    ]
    for i, (title, col, lines, foot) in enumerate(panels):
        x = 48 + i * 480
        s += box(x, 76, 440, 236, fill=ACCENT_TINT if i == 0 else "#ffffff", stroke=col)
        s += txt(x + 20, 104, title, size=13, weight="600", fill=col, anchor="start", family=SANS)
        # heap strip
        s += hbar(x + 20, 122, 400, 14, fill=col, opacity=0.10, stroke=col)
        s += mono(x + 220, 132, "heap · 7,693 pages · all scanned", size=7.5, fill=col)
        # dead tuples strip
        s += hbar(x + 20, 146, 400 * 0.8, 14, fill=col, opacity=0.35 if i == 0 else 0.06, stroke=col, rx=1)
        s += hbar(x + 20 + 400 * 0.8, 146, 400 * 0.2, 14, fill=INK, opacity=0.06, stroke=RULE_SOLID, rx=1)
        s += mono(x + 20 + 160, 156, "800,000 dead" + (" — still here" if i == 0 else " — removed"), size=7.5, fill="#ffffff" if i == 0 else col)
        s += mono(x + 20 + 400 * 0.9, 156, "200,000 live", size=7.5, fill=MUTED)
        for k, l in enumerate(lines):
            s += mono(x + 20, 184 + k * 16, "· " + l, size=8.5, fill=INK, anchor="start")
        s += mono(x + 20, 296, foot, size=7.5, fill=SOFT, anchor="start")
    s += vline(508, 90, 300, stroke=RULE_SOLID, marker=None, dash="3,3")
    s += note(32, 340, "the removable cutoff is the oldest xmin of any snapshot in the cluster · one idle BEGIN anywhere pins it for every table in every database")
    return emit("07", "held-snapshot", "One idle transaction, and nothing can be cleaned",
                "The vacuum did all of its reading and none of its removing. The other session's COMMIT changed one number and everything followed.",
                "autovacuum", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 510
    # written upper-case: eyebrow() only uppercases ASCII, so "maître" would print as MAîTRE
    s = eyebrow(32, 44, "THE RESTAURANT — ONE MAÎTRE D', A COOK PER TABLE, A PERMANENT CREW OF FOUR — AND WHERE THE PICTURE STOPS BEING TRUE")
    # door + maitre d
    s += node(40, 76, 170, 68, "maître d'", "seats · never cooks", kind="focal", tagtext="postmaster")
    # tables: one trunk out of the maître d', one branch up into each table — seated, not chained
    xs = [260 + i * 184 for i in range(4)]
    bus = 168
    s += (f'<path d="M 125 145 V {bus - 8} Q 125 {bus} 133 {bus} H {xs[-1] + 82}" fill="none" '
          f'stroke="{MUTED}" stroke-width="1"/>')
    for i, x in enumerate(xs):
        s += node(x, 76, 164, 68, f"table {i + 1}", "own cook", tagtext="backend")
        s += vline(x + 82, bus, 146)
    s += mono(618, 190, "one cook per party, hired at the door — a client backend per connection", size=8, fill=MUTED)
    # pantry
    s += box(260, 206, 716, 40, fill="rgba(45,49,66,0.05)", stroke=MUTED, dash="4,3")
    s += txt(618, 230, "the pantry — shared memory — every cook reaches into the same shelves", size=9.5, fill=MUTED)
    # crew
    crew = [("ledger", "writes every order down the instant it is placed", "WAL writer"),
            ("plates", "tidies plates a little before a cook needs one", "background writer"),
            ("sweep", "full clear every few minutes, then tears out the old ledger pages", "checkpointer"),
            ("rounds", "walks the tables on a fixed round, calls for a busser when one is dirty enough", "autovacuum launcher")]
    for i, (name, job, real) in enumerate(crew):
        x = 40 + i * 240
        s += box(x, 270, 216, 82, fill="#ffffff", stroke=INK)
        s += tag(x + 8, 276, real, stroke=MUTED)
        s += txt(x + 108, 310, name, size=12, weight="600")
        for k, line in enumerate(wrap(job, 8, 196)):
            s += mono(x + 108, 327 + k * 12, line, size=8, fill=SOFT)
    # breaks
    brk = [("the pantry is shared", "a cook who spoils the pantry has spoiled every table's ingredients — so the whole room is cleared, not one table"),
           ("hires only on request", "the maître d' never decides to hire; the rounds-walker asks, and the maître d' only ever says yes"),
           ("one guest blocks every table", "the whole building shares one clock for 'old enough to clear' — a lingering guest anywhere blocks clearing everywhere")]
    for i, (h, t) in enumerate(brk):
        x = 40 + i * 320
        s += box(x, 374, 296, 78, fill=ACCENT_TINT, stroke=ACCENT, rx=4, dash="4,3")
        s += txt(x + 14, 396, "breaks: " + h, size=9.5, weight="600", fill=ACCENT, anchor="start")
        for k, line in enumerate(wrap(t, 8, 268)):
            s += mono(x + 14, 414 + k * 12, line, size=8, fill=INK, anchor="start")
    s += legend(482, vw, [("the supervisor", ACCENT, "box"), ("a process", INK, "hollow"), ("where the analogy fails", ACCENT, "dashbox")])
    return emit("08", "the-kitchen", "The crew, and where the picture stops",
                "A supervisor who never cooks, a cook per table, and four people nobody ordered. Three properties carry over; three do not.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 520
    s = eyebrow(32, 44, "from connect() to the first query — the postmaster's involvement ends at the fork")
    # lanes sit left so the backend's self-message labels end inside the right margin
    xs = {"c": 100, "pm": 320, "be": 580}
    names = {"c": "client", "pm": "postmaster", "be": "new backend"}
    for k, x in xs.items():
        s += lane(x, 100, 470, names[k])
    s += msg(xs["c"], xs["pm"], 122, "connect() to the listening socket")
    s += selfmsg(xs["pm"], 140, "ServerLoop: accept() → BackendStartup")
    s += msg(xs["pm"], xs["be"], 186, "fork_process() — a plain fork()", accent=True, sub="the postmaster returns to ServerLoop here")
    s += msg(xs["c"], xs["be"], 226, "startup packet: user, database, options")
    s += selfmsg(xs["be"], 244, "ClientAuthentication: pg_hba.conf, TLS, password")
    s += msg(xs["be"], xs["c"], 290, "AuthenticationOk", dash="3,3")
    s += selfmsg(xs["be"], 308, "InitPostgres: take a PGPROC slot")
    s += selfmsg(xs["be"], 334, "register with sinval · relcache · catcache · plancache · pgstat")
    s += msg(xs["be"], xs["c"], 380, "ReadyForQuery", dash="3,3")
    s += msg(xs["c"], xs["be"], 410, "select 1")
    s += selfmsg(xs["be"], 428, "PostgresMain: parse → plan → execute → reply, until disconnect")
    s += hbar(xs["pm"] - 6, 200, 12, 262, fill=MUTED, opacity=0.06)
    s += masked(xs["pm"], 336, "not involved", size=7.5, fill=SOFT)
    s += legend(496, vw, [("the one thing the postmaster does", ACCENT, "line"), ("work done by the child", MUTED, "line"), ("reply", MUTED, "dashline")])
    return emit("09", "connection-sequence", "From connect to first query",
                "The postmaster forks before it reads a byte from the client. Authentication, initialisation and every query happen in the child.",
                "the postmaster", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 446
    s = eyebrow(32, 44, "HandleChildCrash, postmaster.c — what happens when ServerLoop collects an exit status")
    y = 90
    s += node(40, y, 180, 50, "child exits", "SIGCHLD → waitpid", kind="input")
    s += hline(220, 262, y + 25)
    s += box(264, y, 200, 50, fill="#ffffff", stroke=INK, rx=6)
    s += txt(364, y + 22, "exit status clean?", size=11, weight="600")
    s += mono(364, y + 38, "0, or a signal we sent", size=8, fill=SOFT)
    # yes branch
    s += hline(464, 556, y + 25)
    s += alabel(510, y + 25, "yes", gap=14)
    s += node(560, y, 200, 50, "release the slot", "carry on", kind="backend")
    # no branch
    s += vline(364, y + 50, y + 90)
    s += alabel(364, y + 90, "no", gap=18)
    steps = [("log it", "\"server process (PID n) was terminated by signal 9\""),
             ("log 'terminating any other active server processes'", "SetQuitSignalReason(PMQUIT_FOR_CRASH)"),
             ("SIGQUIT every other child", "backends, checkpointer, walwriter, workers — no exceptions"),
             ("wait until none remain", "PM_WAIT_DEAD_END → PM_NO_CHILDREN"),
             ("reinitialise shared memory · start recovery", "startup process replays from the last redo point"),
             ("accept connections again", "a fresh set of children")]
    yy = y + 92
    for i, (h, sub) in enumerate(steps):
        focal = i in (1, 2)
        s += box(96, yy, 536, 30, fill=ACCENT_TINT if focal else "#ffffff", stroke=ACCENT if focal else INK, rx=4)
        s += txt(110, yy + 19, h, size=9.5, weight="600", fill=ACCENT if focal else INK, anchor="start")
        s += mono(626, yy + 19, sub, size=7.5, fill=SOFT, anchor="end")
        if i < len(steps) - 1:
            s += vline(364, yy + 30, yy + 36, marker=None)
        yy += 38
    s += box(680, 200, 300, 78, fill="rgba(45,49,66,0.04)", stroke=MUTED, dash="4,3")
    s += txt(694, 222, "restart_after_crash = off", size=9.5, weight="600", anchor="start")
    s += mono(694, 240, "same sequence, but the postmaster", size=8, fill=MUTED, anchor="start")
    s += mono(694, 253, "shuts down instead of reinitialising —", size=8, fill=MUTED, anchor="start")
    s += mono(694, 266, "for clusters with an external supervisor", size=8, fill=MUTED, anchor="start")
    s += note(32, 428, "no branch inspects shared memory to decide how bad it is · the postmaster does not look; it resets")
    return emit("10", "child-crash", "One child dies badly",
                "The postmaster cannot know what a killed backend left behind in shared memory, so it does not try to find out.",
                "the postmaster", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 316
    s = eyebrow(32, 44, "one backend's private memory against the shared segment from part 1 — to scale, PostgreSQL 16.2 defaults")
    x0, y0 = 60, 90
    scale = 880 / 143.0
    s += hbar(x0, y0, 143 * scale, 34, fill=INK, opacity=0.10, stroke=INK)
    s += mono(x0 + 143 * scale / 2, y0 + 21, "shared memory segment · 143 MB · mapped by every process (part 1, figure 3)", size=9, fill=INK)
    s += hbar(x0, y0 + 50, 13.0 * scale, 20, fill=ACCENT, opacity=0.18, stroke=ACCENT)
    s += mono(x0 + 13.0 * scale + 8, y0 + 64, "fresh backend · 13.0 MB resident", size=8.5, fill=ACCENT, anchor="start")
    s += hbar(x0, y0 + 78, 14.5 * scale, 20, fill=ACCENT, opacity=0.28, stroke=ACCENT)
    s += mono(x0 + 14.5 * scale + 8, y0 + 92, "after one catalog query · 14.5 MB · relcache, catcache, plancache, memory contexts", size=8.5, fill=ACCENT, anchor="start")
    # 100 connections
    s += hbar(x0, y0 + 116, 143 * scale, 20, fill=ACCENT, opacity=0.06, stroke=ACCENT, rx=1)
    for i in range(10):
        s += f'<line x1="{x0 + (i + 1) * 14.3 * scale}" y1="{y0 + 116}" x2="{x0 + (i + 1) * 14.3 * scale}" y2="{y0 + 136}" stroke="{ACCENT}" stroke-width="0.6" stroke-opacity="0.5"/>'
    s += mono(x0, y0 + 152, "100 idle connections at 14.5 MB each ≈ 1.4 GB, this bar drawn at 1/10 scale — ten times the shared segment, and none of it shared", size=8.5, fill=ACCENT, anchor="start")
    s += note(32, 266, "a warm backend grows past this as its caches fill · the shared segment is fixed at start; the private total is fixed by nothing but max_connections")
    s += legend(292, vw, [("shared, once", INK, "box"), ("private, per connection", ACCENT, "box")])
    return emit("11", "private-vs-shared", "What a connection owns",
                "The shared segment is one size for the whole server. Private memory is that size again for every hundred idle connections.",
                "what a connection costs", vw, vh, s)


# ------------------------------------------------------------------ FIG 12
def fig12():
    vw, vh = 1016, 320
    s = eyebrow(32, 44, "the only link between private caches — the shared-invalidation queue, sinvaladt.c")
    # ring; the two arrow rows (y = 130, 230) cut its outer edge at x = cx ± 49
    cx, cy, r = 508, 180, 70
    s += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="rgba(45,49,66,0.05)" stroke="{INK}" stroke-width="1.2"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r - 22}" fill="{PAPER}" stroke="{INK}" stroke-width="1.2"/>'
    for i in range(16):
        a = i * math.tau / 16
        s += f'<line x1="{cx + (r - 22) * math.cos(a)}" y1="{cy + (r - 22) * math.sin(a)}" x2="{cx + r * math.cos(a)}" y2="{cy + r * math.sin(a)}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    s += txt(cx, cy - 2, "sinval", size=11, weight="600")
    s += mono(cx, cy + 12, "fixed ring", size=7.5, fill=SOFT)
    s += mono(cx, cy + 24, "in shared memory", size=7.5, fill=SOFT)
    # backends around
    bes = [(122, 130, "backend A", True), (122, 230, "backend B", False), (894, 130, "backend C", False), (894, 230, "backend D", False)]
    for x, y, name, writer in bes:
        s += box(x - 90, y - 34, 180, 68, fill=ACCENT_TINT if writer else "#ffffff", stroke=ACCENT if writer else INK)
        s += txt(x, y - 12, name, size=10, weight="600", fill=ACCENT if writer else INK)
        s += mono(x, y + 4, "relcache · catcache · plancache", size=7.5, fill=MUTED)
        s += mono(x, y + 18, "private — nobody else can read it", size=7, fill=SOFT)
    left, right = cx - 49, cx + 49
    s += hline(212, left - 1, 130, stroke=ACCENT, marker="arrow-accent")
    s += mono(224, 108, "ALTER TABLE … COMMIT:", size=7.5, fill=ACCENT, anchor="start")
    s += mono(224, 120, "append invalidation message", size=7.5, fill=ACCENT, anchor="start")
    s += hline(left, 214, 230, dash="3,3")
    s += mono(224, 248, "next transaction start:", size=7.5, fill=MUTED, anchor="start")
    s += mono(224, 260, "read new messages, drop stale entries", size=7.5, fill=MUTED, anchor="start")
    s += hline(right, 802, 130, dash="3,3")
    s += mono(792, 108, "far behind →", size=7.5, fill=MUTED, anchor="end")
    s += mono(792, 120, "catchup interrupt (ProcSignal)", size=7.5, fill=MUTED, anchor="end")
    s += hline(right, 802, 230, dash="3,3")
    s += mono(792, 248, "off the end of the ring →", size=7.5, fill=MUTED, anchor="end")
    s += mono(792, 260, "reset all caches", size=7.5, fill=MUTED, anchor="end")
    s += note(32, 298, "backends never talk to each other about schema · they all read the same ring at their own pace, and a slow reader is nudged with a signal")
    return emit("12", "sinval", "How private caches learn that a table changed",
                "One backend appends; every other backend reads the ring at its next transaction start. There is no other channel.",
                "what a connection costs", vw, vh, s)


# ------------------------------------------------------------------ FIG 13
def fig13():
    vw, vh = 1016, 470
    s = eyebrow(32, 44, "pg_cancel_backend(pid) — from the caller to the moment the target acts on it")
    # lanes sit left so backend B's self-message labels end inside the right margin
    xs = {"a": 100, "k": 300, "b": 500}
    names = {"a": "session A", "k": "kernel", "b": "backend B (in pg_sleep)"}
    for k, x in xs.items():
        s += lane(x, 100, 420, names[k], w=150 if k == "b" else 124)
    s += selfmsg(xs["a"], 118, "select pg_cancel_backend(130523)")
    s += msg(xs["a"], xs["k"], 160, "kill(130523, SIGINT)", sub="pg_terminate_backend sends SIGTERM instead")
    s += msg(xs["k"], xs["b"], 196, "SIGINT delivered", accent=True)
    s += selfmsg(xs["b"], 214, "StatementCancelHandler: QueryCancelPending = true; InterruptPending = true; SetLatch")
    s += mono(xs["b"] + 48, 246, "…and return. Nothing else happens in the handler.", size=8, fill=SOFT, anchor="start")
    s += selfmsg(xs["b"], 268, "WaitLatch in pg_sleep returns early")
    s += selfmsg(xs["b"], 300, "CHECK_FOR_INTERRUPTS(): InterruptPending? → ProcessInterrupts()")
    s += selfmsg(xs["b"], 332, "QueryCancelPending → ERROR: canceling statement due to user request", accent=True)
    s += msg(xs["b"], xs["a"], 380, "(via B's own client) error, then ReadyForQuery — connection alive", dash="3,3")
    s += hbar(xs["b"] - 6, 196, 12, 150, fill=ACCENT, opacity=0.06)
    s += legend(446, vw, [("the signal", ACCENT, "line"), ("what the target does, when it chooses", MUTED, "line")])
    return emit("13", "cancel-sequence", "How a cancel actually lands",
                "The signal handler sets a flag and returns. The backend interrupts itself at the next CHECK_FOR_INTERRUPTS, which is why a cancel is usually instant and occasionally not.",
                "interrupts", vw, vh, s)


# ------------------------------------------------------------------ FIG 14
def fig14():
    vw, vh = 1016, 400
    s = eyebrow(32, 44, "pg_stat_activity.wait_event_type / wait_event sampled 200× per second while a join ran — PostgreSQL 16.2")
    rows = [("client backend", "(running)", "(cpu)", 34, ACCENT),
            ("parallel worker", "(running)", "(cpu)", 31, ACCENT),
            ("autovacuum launcher", "Activity", "AutoVacuumMain", 19, INK),
            ("background writer", "Activity", "BgWriterMain", 19, INK),
            ("walwriter", "Activity", "WalWriterMain", 19, INK),
            ("logical replication launcher", "Activity", "LogicalLauncherMain", 19, INK),
            ("checkpointer", "Timeout", "CheckpointWriteDelay", 19, SER2),
            ("parallel worker", "IO", "DataFileRead", 2, SER1),
            ("client backend", "IO", "DataFileWrite", 2, SER1)]
    x0, y0, rh = 300, 80, 26
    scale = 560 / 34
    for i, (bt, wt, we, n, col) in enumerate(rows):
        y = y0 + i * rh
        s += txt(x0 - 12, y + 16, bt, size=9.5, weight="600", anchor="end")
        s += hbar(x0, y + 4, n * scale, 16, fill=col, opacity=0.18, stroke=col)
        s += mono(x0 + n * scale + 8, y + 16, f"{wt} · {we}", size=8, fill=col, anchor="start")
        s += mono(x0 + n * scale - 6, y + 16, str(n), size=8, fill=col, anchor="end", weight="600")
    s += note(32, 330, "every background process was asleep on its own latch the whole time, named by its main loop · the checkpointer slept between paced writes")
    s += note(32, 346, "a sample of instants, not a profile — but the cheapest way there is to see where a server's time goes")
    s += legend(372, vw, [("on CPU", ACCENT, "box"), ("Activity: idle in main loop", INK, "box"), ("Timeout", SER2, "box"), ("IO", SER1, "box")])
    return emit("14", "wait-events", "A server seen through its latches",
                "Each idle process names the loop it is sleeping in. The two doing work have no wait event at all.",
                "interrupts", vw, vh, s)


ALL = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06,
       "07": fig07, "08": fig08, "09": fig09, "10": fig10, "11": fig11, "12": fig12,
       "13": fig13, "14": fig14}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
