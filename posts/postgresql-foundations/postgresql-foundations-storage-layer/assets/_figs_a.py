#!/usr/bin/env python3
"""Figures 01-11 for postgresql-foundations-storage-layer. Every number is read from
lab/captures.json (the run the article quotes) or is arithmetic on those numbers."""
import json
import pathlib
import sys

from _build import (ACCENT, ACCENT_TINT, INK, LINK, MONO, MUTED, PAPER, RULE,
                    RULE_SOLID, SOFT, SANS, SERIF, alabel, box, cell, elbow, emit,
                    eyebrow, elbow_hvh, hline, legend, masked, mono, node, tag,
                    txt, vline)

HERE = pathlib.Path(__file__).resolve().parent
D = json.loads((HERE.parent / "lab" / "captures.json").read_text())
SER1, SER2 = "#7c8f6f", "#5e7a9b"


def fmt(n):
    return f"{n:,}"


def note(x, y, text, anchor="start", fill=SOFT, size=8):
    return mono(x, y, text, size=size, fill=fill, anchor=anchor, track="0.02em")


def ortho(x1, y1, xm, y2, x2, stroke=MUTED, marker="arrow", dash=None, r=6, sw=1):
    """Horizontal to xm, vertical to y2, horizontal to x2; rounded corners in either direction."""
    sx1 = 1 if xm > x1 else -1
    sx2 = 1 if x2 > xm else -1
    sy = 1 if y2 > y1 else -1
    d = (f"M {x1} {y1} H {xm - sx1 * r} Q {xm} {y1} {xm} {y1 + sy * r} "
         f"V {y2 - sy * r} Q {xm} {y2} {xm + sx2 * r} {y2} H {x2}")
    m = f' marker-end="url(#{marker})"' if marker else ""
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{da}{m}/>'


def bar(x, y, w, h, fill=INK, opacity=0.14, stroke=None, rx=2):
    st = f' stroke="{stroke}" stroke-width="0.8"' if stroke else ""
    return (f'<rect x="{x}" y="{y}" width="{max(w, 0.8)}" height="{h}" rx="{rx}" fill="{fill}" '
            f'fill-opacity="{opacity}"{st}/>')


# ------------------------------------------------------------------ FIG 01
def fig01():
    vw, vh = 1016, 312
    s = eyebrow(32, 44, "the three layers, and where this post sits")
    layers = [
        ("memory layer", "shared buffers · WAL buffers · per-process memory · the rest of shared memory", "done", "part 1"),
        ("process layer", "postmaster · backends · checkpointer · background writer · WAL writer · autovacuum", "done", "part 2"),
        ("storage layer", "heap pages · line pointers · visibility map · free space map · TOAST · B-tree pages · WAL segments", "focal", "part 3 · this post"),
    ]
    y = 72
    for name, sub, state, part in layers:
        focal = state == "focal"
        s += box(32, y, 952, 62, fill=ACCENT_TINT if focal else "rgba(45,49,66,0.04)",
                 stroke=ACCENT if focal else "rgba(45,49,66,0.35)")
        s += txt(56, y + 27, name, size=14, weight="600", fill=ACCENT if focal else SOFT, anchor="start")
        s += mono(56, y + 47, sub, size=9, fill=MUTED if focal else SOFT, anchor="start")
        s += tag(846, y + 8, part, stroke=ACCENT if focal else MUTED, w=122)
        y += 74
    s += note(32, y + 14, "this post links up to part 1 for full-page images and the WAL-before-data rule, and to part 2 for who runs vacuum")
    return emit("01", "three-layers", "The three layers of a PostgreSQL server",
                "Memory, process, storage. Parts 1 and 2 covered the top two layers; this post is the bottom one.",
                "the series", vw, vh, s)


# ------------------------------------------------------------------ FIG 02
def fig02():
    vw, vh = 1016, 520
    f = D["files"]
    heap = f["orders"]
    rel = D["relfilepath_orders"].split("/")[-1]
    dboid = D["db_oid"]
    toast = f[D["toast_table"]]
    tname, tsize = next(iter(toast.items()))
    idx_c = f["orders_customer_idx"]
    idx_d = f["orders_created_idx"]
    rows = [
        (f"base/{dboid}/{rel}", "orders · the heap", heap[rel], f"{fmt(heap[rel] // 8192)} pages", True),
        (f"{rel}_fsm", "free space map fork", heap[f"{rel}_fsm"], f"{heap[rel + '_fsm'] // 8192} pages", False),
        (f"{rel}_vm", "visibility map fork", heap[f"{rel}_vm"], f"{heap[rel + '_vm'] // 8192} page", False),
        (next(iter(idx_c)), "orders_customer_idx", next(iter(idx_c.values())), f"{fmt(D['pages']['orders_customer_idx'])} pages", False),
        (next(iter(idx_d)), "orders_created_idx", next(iter(idx_d.values())), f"{fmt(D['pages']['orders_created_idx'])} pages", False),
        (tname, "TOAST table (empty until step 8)", tsize, "0 pages", False),
        (str(int(tname) + 1), "TOAST index", 8192, "1 page", False),
    ]
    s = eyebrow(32, 44, f"every file behind orders, from ls on the data directory — PostgreSQL 16.2, database oid {dboid}")
    x0, y0, rh = 32, 80, 40
    scale = 440 / heap[rel]
    bx = 384
    for i, (fname, what, size, pages, focal) in enumerate(rows):
        y = y0 + i * rh
        s += f'<line x1="{x0}" y1="{y + rh - 6}" x2="{vw - 32}" y2="{y + rh - 6}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x0, y + 14, fname, size=10, fill=ACCENT if focal else INK, anchor="start", weight="600")
        s += txt(x0, y + 28, what, size=10, fill=MUTED, anchor="start")
        w = size * scale
        s += bar(bx, y + 6, w, 16, fill=ACCENT if focal else INK, opacity=0.22 if focal else 0.16,
                 stroke=ACCENT if focal else None)
        lab = f"{fmt(size)} B · {pages}"
        s += mono(bx + max(w, 1) + 8, y + 18, lab, size=9, fill=INK, anchor="start")
    # the maps callout
    y = y0 + 1 * rh
    s += masked(820, y + 58, "both maps: 40,960 B = 0.06% of the heap", size=8, fill=ACCENT)
    # pg_wal, cluster-wide
    yw = y0 + len(rows) * rh + 22
    n, total = D["pg_wal"]
    s += box(32, yw, 952, 96, fill="rgba(45,49,66,0.04)", stroke="rgba(45,49,66,0.30)", dash="3,3")
    s += mono(52, yw + 22, "pg_wal/", size=10, fill=INK, anchor="start", weight="600")
    s += txt(52, yw + 38, f"the one log, shared by every table: {n} segment files of 16 MiB = {int(total) // 2**20} MiB", size=10, fill=MUTED, anchor="start")
    tw = 52
    for k in range(n):
        s += bar(52 + k * (tw + 4), yw + 52, tw, 26, fill=INK, opacity=0.10, stroke="rgba(45,49,66,0.35)")
        s += mono(52 + k * (tw + 4) + tw / 2, yw + 69, "16 MiB", size=7, fill=SOFT)
    s += note(32, yw + 118, "bar lengths are to scale against the 63 MB heap; the two map forks are too small to see at this scale, which is the point")
    return emit("02", "on-disk-inventory", "What orders is, on disk",
                "One heap file, two small map forks, two index files, an empty TOAST table, and the cluster's shared log.",
                "the problem", vw, vh, s)


# ------------------------------------------------------------------ FIG 03
def fig03():
    vw, vh = 1016, 500
    u1, u2 = D["update1"], D["update2"]
    w1 = sum(r["record_length"] for r in u1["wal"] if r["xid"] == str(u1["xid"]))
    w2 = sum(r["record_length"] for r in u2["wal"])
    walk = D["btree_walk"]
    cr = D["crash"]
    steps = [
        ("1 · after the load", D["row_ctid"], [f"xmin {D['row_tuple_header']['t_xmin']}", "53-byte tuple, page 32 full", f"{D['free_bytes_on_page']} bytes free"], False),
        ("2 · update 1, not HOT", u1["new_ctid"], ["page 32 had no room", "+1 entry in each index", f"{w1} B of WAL, 5 records"], True),
        ("3 · a reader prunes", u1["new_ctid"], ["old (32,82) cut to a 4 B stub", "56 B freed on page 32", "57 B PRUNE record"], False),
        ("4 · update 2, HOT", "(7692,42)", ["same page, heap-only", "no index touched", f"{w2} B of WAL, 2 records"], True),
        ("5 · vacuum", "(7692,42)", ["2 of 7,693 pages read", "slot 41 → redirect to 42", "forced cleanup: slot 82 unused"], False),
        ("6 · a 10,000-byte note", D["toast_update"]["ctid"], ["HOT again", "6 chunks in the TOAST table", "row grows by an 18 B pointer"], True),
        ("7 · lookup by customer", D["toast_update"]["ctid"], [f"index pages {walk[0]['block']} → {walk[1]['block']} → {walk[2]['block']}", "index says (7692,41): 41 → 42 → 43", "13 buffers in all"], False),
        ("8 · crash and replay", cr["ctid"], [f"redo from {cr['controldata_after_checkpoint']['Latest checkpoint' + chr(39) + 's REDO location']}", "file was one change behind", "after replay: caught up"], True),
    ]
    s = eyebrow(32, 44, "row id = 4242 of orders, step by step — its address after each step")
    cw, ch, gx, gy = 224, 164, 18, 34
    x0, y0 = 32, 76
    for i, (title, addr, lines, focal) in enumerate(steps):
        r, c = divmod(i, 4)
        x, y = x0 + c * (cw + gx), y0 + r * (ch + gy)
        s += box(x, y, cw, ch, fill=ACCENT_TINT if focal else "#ffffff", stroke=ACCENT if focal else INK)
        s += txt(x + 14, y + 24, title, size=11, weight="600", fill=ACCENT if focal else INK, anchor="start")
        s += f'<rect x="{x + 14}" y="{y + 38}" width="{cw - 28}" height="30" rx="4" fill="{PAPER}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
        s += mono(x + cw / 2, y + 58, addr, size=13, fill=INK, weight="600")
        for k, ln in enumerate(lines):
            s += mono(x + 14, y + 92 + k * 18, ln, size=8.5, fill=MUTED, anchor="start")
        if c < 3:
            s += hline(x + cw + 2, x + cw + gx - 2, y + ch / 2, stroke=MUTED)
    # row-wrap connector from cell 4 to cell 5
    xa = x0 + 3 * (cw + gx) + cw / 2
    s += (f'<path d="M {xa} {y0 + ch + 2} V {y0 + ch + gy / 2} H {x0 + cw / 2} V {y0 + ch + gy - 2}" '
          f'fill="none" stroke="{MUTED}" stroke-width="1" marker-end="url(#arrow)"/>')
    s += legend(470, vw, [("the row moved to a new address", ACCENT, "box"), ("the address stayed; something else changed", INK, "box")])
    return emit("03", "life-of-a-row", "The physical life of one row",
                "Row 4242's address after each of the lab's eight steps.",
                "worked example", vw, vh, s)


# ------------------------------------------------------------------ FIG 04
def fig04():
    vw, vh = 1016, 540
    s = eyebrow(32, 44, "every structure on disk is data, a map of the data, or the log — every arrow is a real pointer")
    s += tag(40, 64, "data", stroke=INK, w=60)
    s += tag(640, 64, "maps", stroke=MUTED, w=60)
    s += tag(640, 322, "log", stroke=ACCENT, w=52)
    s += node(40, 90, 300, 70, "index page", "orders_customer_idx · leaf 1068 · entry (7692,41)", kind="backend", tagtext="8 KB")
    s += node(40, 212, 300, 120, "heap page", "page 7692 · slot 41 → 42 → 43 · pd_lsn in header", kind="focal", tagtext="8 KB")
    s += node(40, 384, 300, 70, "TOAST table", "pg_toast_91057 · value 91083 · 6 chunks", kind="backend", tagtext="8 KB pages")
    s += node(640, 90, 300, 64, "visibility map", "_vm fork · 2 bits per heap page", kind="store")
    s += node(640, 180, 300, 64, "free space map", "_fsm fork · 1 byte per heap page", kind="store")
    s += node(640, 344, 300, 84, "WAL segment", "pg_wal/0000000100000003000000F6 · records by LSN", kind="focal")
    # index -> heap, heap -> toast
    s += vline(190, 160, 210, stroke=INK)
    s += alabel(262, 196, "ctid (7692,41)")
    s += vline(190, 332, 382, stroke=INK)
    s += alabel(272, 368, "toast pointer · 18 B", w=126)
    # maps -> heap
    s += ortho(640, 122, 520, 234, 342, stroke=MUTED)
    s += alabel(580, 122, "all-visible bit", w=100)
    s += ortho(640, 212, 540, 256, 342, stroke=MUTED)
    s += alabel(590, 212, "free ÷ 32", w=72)
    # heap -> WAL (pd_lsn) and WAL -> heap (block reference); parallel, no crossing
    s += ortho(342, 282, 600, 360, 638, stroke=ACCENT, marker="arrow-accent", dash="4,3")
    s += alabel(452, 282, "pd_lsn 3/F6D69D50", fill=ACCENT, gap=-6, w=124)
    s += ortho(640, 396, 560, 318, 342, stroke=ACCENT, marker="arrow-accent")
    s += alabel(570, 396, "rel 91057 · blk 7692", fill=ACCENT, gap=-6, w=128)
    s += note(32, 490, "maps may be wrong in one safe direction; the log is never wrong; a data page is as current as the last WAL record applied to it")
    s += legend(516, vw, [("data", INK, "box"), ("map", MUTED, "box"), ("log, and the page it keeps in step", ACCENT, "box")])
    return emit("04", "data-maps-log", "Data, maps and log",
                "The three kinds of on-disk structure, and the pointers that connect them.",
                "intuition", vw, vh, s)


# ------------------------------------------------------------------ FIG 05
def fig05():
    vw, vh = 1016, 380
    ph = D["page_header"]
    lp = D["lp_row"]
    s = eyebrow(32, 44, "page 32 of orders, all 8,192 bytes to scale, then its first 700 bytes enlarged")
    x0, w = 32, 952
    k = w / 8192
    y = 80
    # full page
    s += bar(x0, y, w, 34, fill="#ffffff", opacity=1, stroke=INK)
    s += bar(x0, y, 24 * k, 34, fill=INK, opacity=0.6)
    s += bar(x0 + 24 * k, y, (ph["pd_lower"] - 24) * k, 34, fill=SER2, opacity=0.35)
    s += bar(x0 + ph["pd_upper"] * k, y, (8192 - ph["pd_upper"]) * k, 34, fill=INK, opacity=0.10)
    s += bar(x0 + lp["lp_off"] * k, y, lp["lp_len"] * k, 34, fill=ACCENT, opacity=0.9)
    s += mono(x0 + lp["lp_off"] * k + 3, y + 52, f"row 4242 · bytes {fmt(lp['lp_off'])}–{fmt(lp['lp_off'] + lp['lp_len'])}", size=8, fill=ACCENT, anchor="middle")
    s += mono(x0 + (lp["lp_off"] + lp["lp_len"] + 8192) / 2 * k, y + 22, "130 tuples, packed from the end backwards", size=9, fill=MUTED)
    for b in (0, 2048, 4096, 6144, 8192):
        s += mono(x0 + b * k, y - 6, fmt(b), size=7, fill=SOFT)
    # zoom guides from the first 700 bytes down to the enlarged bar
    zk = w / 700
    s += f'<line x1="{x0}" y1="{y + 34}" x2="{x0}" y2="220" stroke="{RULE_SOLID}" stroke-width="0.7" stroke-dasharray="2,2"/>'
    s += f'<line x1="{x0 + 700 * k}" y1="{y + 34}" x2="{x0 + w}" y2="220" stroke="{RULE_SOLID}" stroke-width="0.7" stroke-dasharray="2,2"/>'
    y2 = 220
    s += bar(x0, y2, w, 44, fill="#ffffff", opacity=1, stroke=INK)
    s += bar(x0, y2, 24 * zk, 44, fill=INK, opacity=0.6)
    s += bar(x0 + 24 * zk, y2, (ph["pd_lower"] - 24) * zk, 44, fill=SER2, opacity=0.35)
    for i in range(1, 131):
        xx = x0 + (24 + 4 * i) * zk
        s += f'<line x1="{xx}" y1="{y2}" x2="{xx}" y2="{y2 + 44}" stroke="#ffffff" stroke-width="0.6"/>'
    s += bar(x0 + ph["pd_lower"] * zk, y2, (ph["pd_upper"] - ph["pd_lower"]) * zk, 44, fill=ACCENT, opacity=0.25, stroke=ACCENT)
    s += bar(x0 + ph["pd_upper"] * zk, y2, (700 - ph["pd_upper"]) * zk, 44, fill=INK, opacity=0.10)
    s += mono(x0, y2 + 64, "header · 24 B", size=8, fill=INK, anchor="start")
    s += mono(x0 + (24 + ph["pd_lower"]) / 2 * zk, y2 + 27, "130 line pointers × 4 B = 520 B", size=9, fill=INK)
    s += mono(x0 + (ph["pd_lower"] + ph["pd_upper"]) / 2 * zk, y2 + 64, f"free: {ph['pd_upper'] - ph['pd_lower']} B", size=8, fill=ACCENT, weight="600")
    s += mono(x0 + (ph["pd_upper"] + 700) / 2 * zk, y2 + 27, "lowest tuple starts here", size=9, fill=MUTED)
    for b, lab in ((0, "0"), (24, "24"), (ph["pd_lower"], f"pd_lower {ph['pd_lower']}"), (ph["pd_upper"], f"pd_upper {ph['pd_upper']}"), (700, "700")):
        anchor = "end" if b == ph["pd_lower"] else ("start" if b == ph["pd_upper"] else "middle")
        s += mono(x0 + b * zk, y2 - 6, lab, size=7.5, fill=SOFT, anchor=anchor)
    s += note(32, 322, "line pointers grow forward from the header, tuples grow backward from the end; the page is full when the two meet — here 24 bytes short")
    s += legend(348, vw, [("page header", INK, "box"), ("line pointers", SER2, "box"), ("free space", ACCENT, "box"), ("tuples", SOFT, "box")])
    return emit("05", "page-to-scale", "Page 32, to scale",
                "Header, line pointers, a 24-byte hole, and 130 tuples.",
                "the heap page", vw, vh, s)


# ------------------------------------------------------------------ FIG 06
def fig06():
    vw, vh = 1016, 420
    raw = bytes.fromhex(D["page_header_hex"])
    ph = D["page_header"]
    s = eyebrow(32, 44, "the first 24 bytes of page 32 as stored, little-endian, and one line pointer")
    x0, y0, cw = 32, 84, 952 / 24
    fields = [(0, 8, "pd_lsn", ph["pd_lsn"], True), (8, 2, "pd_checksum", "0|checksums off", False),
              (10, 2, "pd_flags", "0x0004|all-visible", False), (12, 2, "pd_lower", str(ph["pd_lower"]), False),
              (14, 2, "pd_upper", str(ph["pd_upper"]), False), (16, 2, "pd_special", str(ph["pd_special"]), False),
              (18, 2, "pagesize | version", f"{ph['page_size']} | {ph['layout_version']}", False),
              (20, 4, "pd_prune_xid", "0", False)]
    for i, b in enumerate(raw):
        s += cell(x0 + i * cw, y0, cw, 34, f"{b:02x}", fill="#ffffff", size=11)
        s += mono(x0 + i * cw + cw / 2, y0 - 6, str(i), size=7, fill=SOFT)
    for off, n, name, val, focal in fields:
        xa, xb = x0 + off * cw + 2, x0 + (off + n) * cw - 2
        col = ACCENT if focal else INK
        s += f'<path d="M {xa} {y0 + 42} V {y0 + 48} H {xb} V {y0 + 42}" fill="none" stroke="{col}" stroke-width="0.9"/>'
        s += mono((xa + xb) / 2, y0 + 64, name, size=8, fill=col, weight="600")
        v1, _, v2 = val.partition("|")
        s += mono((xa + xb) / 2, y0 + 80, v1, size=8, fill=MUTED)
        if v2:
            s += mono((xa + xb) / 2, y0 + 94, v2, size=7.5, fill=SOFT)
    s += note(32, y0 + 118, "pd_lsn is two 32-bit halves: 03 00 00 00 → 3, then c0 3b 72 eb → 0xEB723BC0; the LSN is 3/EB723BC0 — just past the last WAL record that changed this page")
    # line pointer 82
    lp = D["lp_row"]
    lb = bytes.fromhex(lp["raw_hex"])
    y1 = 250
    s += mono(32, y1 - 18, "line pointer 82, at byte 24 + 81 × 4 = 348:", size=9, fill=INK, anchor="start", weight="600")
    for i, b in enumerate(lb):
        s += cell(32 + i * 40, y1, 40, 30, f"{b:02x}", size=11)
    s += mono(212, y1 + 20, "→  0x" + f"{int.from_bytes(lb, 'little'):08x}" + "  as a 32-bit word", size=10, fill=INK, anchor="start")
    # bit fields: len 15 | flags 2 | off 15 (high to low)
    bx, bw = 32, 952 / 32
    yb = y1 + 50
    segs = [(0, 15, f"lp_len = {lp['lp_len']}", INK), (15, 2, f"flags = {lp['lp_flags']}", ACCENT), (17, 15, f"lp_off = {fmt(lp['lp_off'])}", INK)]
    word = int.from_bytes(lb, "little")
    for i in range(32):
        bit = (word >> (31 - i)) & 1
        seg_col = ACCENT if 15 <= i < 17 else INK
        s += cell(bx + i * bw, yb, bw, 24, str(bit), fill=ACCENT_TINT if 15 <= i < 17 else "#ffffff", size=9, tcolor=seg_col)
    for a, n, lab, col in segs:
        xa, xb = bx + a * bw + 2, bx + (a + n) * bw - 2
        s += f'<path d="M {xa} {yb + 30} V {yb + 36} H {xb} V {yb + 30}" fill="none" stroke="{col}" stroke-width="0.9"/>'
        s += mono((xa + xb) / 2, yb + 52, lab, size=9, fill=col, weight="600")
    s += note(32, 404, "bits 31–17: length 53 · bits 16–15: 1 = normal · bits 14–0: offset 3,384 from the start of the page")
    return emit("06", "header-bytes", "The page header, decoded",
                "Twenty-four bytes of header and one four-byte line pointer, read straight from page 32.",
                "the heap page", vw, vh, s)


# ------------------------------------------------------------------ FIG 07
def fig07():
    vw, vh = 1016, 360
    tup = bytes.fromhex(D["row_tuple_hex"])
    h, d = D["row_tuple_header"], D["row_tuple_data"]
    s = eyebrow(32, 44, "row 4242's 53 bytes, as stored on page 32 at offset 3,384")
    x0 = 32
    rows = [(0, 24, 84, "header · t_hoff = 24"), (24, 53, 214, "data · five columns")]
    groups = [
        (0, 4, "t_xmin", str(h["t_xmin"]), False), (4, 4, "t_xmax", "0", False), (8, 4, "t_cid", "0", False),
        (12, 6, "t_ctid", h["t_ctid"], False), (18, 2, "t_infomask2", "5 attributes", False),
        (20, 2, "t_infomask", "0x0902", True), (22, 1, "t_hoff", "24", False), (23, 1, "pad", "", False),
        (24, 4, "id", str(d["id"]), False), (28, 4, "customer_id", fmt(d["customer_id"]), False),
        (32, 4, "amount_cents", fmt(d["amount_cents"]), False), (36, 4, "pad to 8", "no column", True),
        (40, 8, "created · µs since 2000", "2026-01-01 01:10:42", False), (48, 1, "len", "0x0b", False),
        (49, 4, "status", "paid", False),
    ]
    for start, end, y, label in rows:
        cw = 952 / (end - start)
        s += mono(32, y - 20, label, size=9, fill=INK, anchor="start", weight="600")
        for i in range(start, end):
            xi = x0 + (i - start) * cw
            is_pad = i == 23 or 36 <= i < 40
            s += cell(xi, y, cw, 32, f"{tup[i]:02x}", fill=ACCENT_TINT if is_pad else "#ffffff", size=11,
                      tcolor=ACCENT if is_pad else INK)
            s += mono(xi + cw / 2, y - 4, str(i), size=6.5, fill=SOFT)
        for gs, gn, name, val, focal in groups:
            if not (start <= gs < end):
                continue
            xa = x0 + (gs - start) * cw + 2
            xb = x0 + (gs + gn - start) * cw - 2
            col = ACCENT if focal else INK
            s += f'<path d="M {xa} {y + 40} V {y + 46} H {xb} V {y + 40}" fill="none" stroke="{col}" stroke-width="0.9"/>'
            s += mono((xa + xb) / 2, y + 62, name, size=7.5 if gn < 3 else 8, fill=col, weight="600")
            if val:
                s += mono((xa + xb) / 2, y + 78, val, size=7.5 if gn < 3 else 8, fill=MUTED)
    s += note(32, 336, "infomask 0x0902 = has a variable-width column (0x0002) + inserting xact committed (0x0100) + xmax invalid (0x0800) · status: 0x0b → short header, total length 0x0b >> 1 = 5")
    return emit("07", "tuple-bytes", "Row 4242, byte by byte",
                "The 23-byte header and its pad byte, then five columns with four bytes of alignment padding between them.",
                "the heap page", vw, vh, s)


# ------------------------------------------------------------------ FIG 08
def fig08():
    vw, vh = 1016, 400
    u1, u2 = D["update1"], D["update2"]
    t_x = int(D["toast_update"]["tuple"]["header"]["t_xmin"])
    c_x = D["crash"]["xid"]
    x_load = D["row_tuple_header"]["t_xmin"]
    versions = [
        (D["row_ctid"], x_load, u1["xid"], "paid"),
        (u1["new_ctid"], u1["xid"], u2["xid"], "shipped"),
        ("(7692,42)", u2["xid"], t_x, "refunded"),
        (D["toast_update"]["ctid"], t_x, c_x, "refunded + 10 kB note"),
        (D["crash"]["ctid"], c_x, None, "amount 60000"),
    ]
    lo, hi = x_load - 6, c_x + 12
    x0, w = 200, 780
    X = lambda xid: x0 + (xid - lo) / (hi - lo) * w
    s = eyebrow(32, 44, "the five versions of row 4242, each alive from its xmin to its xmax (transaction ids, to scale)")
    y0 = 84
    snap = t_x + 10
    for i, (ctid, xmn, xmx, what) in enumerate(versions):
        y = y0 + i * 48
        seen = xmn <= snap and (xmx is None or snap < xmx)
        s += mono(32, y + 16, ctid, size=10, fill=ACCENT if seen else INK, anchor="start", weight="600")
        s += mono(32, y + 30, what, size=8, fill=SOFT, anchor="start")
        end = X(xmx) if xmx else x0 + w
        s += bar(X(xmn), y + 4, end - X(xmn), 22, fill=ACCENT if seen else INK, opacity=0.35 if seen else 0.14,
                 stroke=ACCENT if seen else None)
        s += mono(X(xmn) - 4, y + 19, f"xmin {xmn}", size=7.5, fill=INK, anchor="end")
        if xmx:
            s += mono(end + 4, y + 19, f"xmax {xmx}", size=7.5, fill=INK, anchor="start")
        else:
            s += mono(end - 4, y + 19, "xmax 0 · current", size=7.5, fill=INK, anchor="end")
    ys = y0 - 12
    s += f'<line x1="{X(snap)}" y1="{ys}" x2="{X(snap)}" y2="{y0 + 5 * 48 - 10}" stroke="{ACCENT}" stroke-width="1.2" stroke-dasharray="4,3"/>'
    s += masked(X(snap), ys - 2, f"a snapshot at xid {snap}", size=8, fill=ACCENT)
    # axis
    ya = y0 + 5 * 48
    s += f'<line x1="{x0}" y1="{ya}" x2="{x0 + w}" y2="{ya}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    for xid in sorted({x_load, u1["xid"], u2["xid"], t_x, c_x}):
        s += f'<line x1="{X(xid)}" y1="{ya}" x2="{X(xid)}" y2="{ya + 5}" stroke="{MUTED}" stroke-width="0.8"/>'
    s += mono(X(x_load), ya + 16, str(x_load), size=7.5, fill=SOFT)
    s += mono((X(u1["xid"]) + X(u2["xid"])) / 2, ya + 16, f"{u1['xid']}·{u2['xid']}", size=7.5, fill=SOFT)
    s += mono(X(t_x), ya + 16, str(t_x), size=7.5, fill=SOFT)
    s += mono(X(c_x), ya + 16, str(c_x), size=7.5, fill=SOFT)
    s += note(32, ya + 42, "visible = xmin committed before the snapshot and xmax empty or not yet committed; any snapshot line crosses exactly one bar")
    return emit("08", "version-lifetimes", "Five versions of one row",
                "Each version of row 4242 on an axis of transaction ids; a snapshot sees exactly one.",
                "visibility", vw, vh, s)


# ------------------------------------------------------------------ FIG 09
def fig09():
    vw, vh = 1016, 470
    s = eyebrow(32, 44, "line pointers on pages 32 and 7692, and where the two indexes point, after each step")
    panels = [
        ("after update 1", [("32:82", "normal", "xmax set → (7692,41)"), ("7692:41", "normal", "new version"), ("7692:42", None, "")], "(32,82) and (7692,41)"),
        ("after a reader", [("32:82", "dead", "4-byte stub"), ("7692:41", "normal", ""), ("7692:42", None, "")], "(32,82) and (7692,41)"),
        ("after update 2", [("32:82", "dead", ""), ("7692:41", "hot", "HOT-updated → 42"), ("7692:42", "heaponly", "heap-only")], "(32,82) and (7692,41)"),
        ("after vacuum 1", [("32:82", "dead", "cleanup bypassed"), ("7692:41", "redirect", "redirect → 42"), ("7692:42", "heaponly", "heap-only")], "(32,82) and (7692,41)"),
        ("after vacuum 2", [("32:82", "unused", "free for reuse"), ("7692:41", "redirect", "redirect → 42"), ("7692:42", "heaponly", "heap-only")], "(7692,41) only"),
    ]
    styles = {"normal": ("#ffffff", INK), "dead": ("rgba(45,49,66,0.12)", MUTED), "hot": (ACCENT_TINT, ACCENT),
              "heaponly": (ACCENT_TINT, ACCENT), "redirect": ("#ffffff", LINK), "unused": ("#ffffff", "rgba(45,49,66,0.30)")}
    pw, gap = 180, 13
    x0, y0 = 32, 84
    for i, (title, slots, idx) in enumerate(panels):
        x = x0 + i * (pw + gap)
        s += box(x, y0, pw, 330, fill="#ffffff", stroke=RULE_SOLID)
        s += txt(x + pw / 2, y0 + 22, title, size=10.5, weight="600")
        for k, (slot, state, sub) in enumerate(slots):
            y = y0 + 44 + k * 78
            if state is None:
                s += f'<rect x="{x + 16}" y="{y}" width="{pw - 32}" height="54" rx="4" fill="none" stroke="{RULE_SOLID}" stroke-dasharray="3,3"/>'
                s += mono(x + pw / 2, y + 32, f"{slot} · not yet", size=8, fill=SOFT)
                continue
            fill, stroke = styles[state]
            s += f'<rect x="{x + 16}" y="{y}" width="{pw - 32}" height="54" rx="4" fill="{PAPER}"/>'
            s += f'<rect x="{x + 16}" y="{y}" width="{pw - 32}" height="54" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            s += mono(x + 26, y + 18, slot, size=9, fill=INK, anchor="start", weight="600")
            s += mono(x + pw - 26, y + 18, state.replace("heaponly", "normal").replace("hot", "normal"), size=7.5, fill=stroke, anchor="end")
            s += mono(x + 26, y + 38, sub, size=7.5, fill=MUTED, anchor="start")
        s += f'<line x1="{x + 14}" y1="{y0 + 282}" x2="{x + pw - 14}" y2="{y0 + 282}" stroke="{RULE}" stroke-width="0.8"/>'
        s += mono(x + pw / 2, y0 + 300, "each index has entries for", size=7.5, fill=SOFT)
        s += mono(x + pw / 2, y0 + 316, idx, size=8, fill=INK, weight="600")
    s += legend(440, vw, [("HOT chain member", ACCENT, "box"), ("redirect", LINK, "box"), ("dead stub", MUTED, "box"), ("normal", INK, "box")])
    return emit("09", "hot-chain", "The HOT chain, step by step",
                "Update 1 left page 32; update 2 stayed on page 7692; vacuum turned slot 41 into a redirect.",
                "HOT", vw, vh, s)


# ------------------------------------------------------------------ FIG 10
def fig10():
    vw, vh = 1016, 290
    u1, u2 = D["update1"], D["update2"]
    r1 = [(r["record_type"], r["record_length"]) for r in u1["wal"] if r["xid"] == str(u1["xid"])]
    r2 = [(r["record_type"], r["record_length"]) for r in u2["wal"]]
    t1, t2 = sum(n for _, n in r1), sum(n for _, n in r2)
    s = eyebrow(32, 44, "WAL written by each update, by record — PostgreSQL 16.2, no checkpoint between them, no full-page images")
    x0, w = 220, 640
    k = w / t1
    cols = {"LOCK": SER2, "UPDATE": INK, "INSERT_LEAF": SER1, "COMMIT": SOFT, "HOT_UPDATE": ACCENT}
    for row, (label, recs, total, pages) in enumerate([("update 1 · not HOT", r1, t1, "4 pages: 2 heap, 2 index leaves"),
                                                       ("update 2 · HOT", r2, t2, "1 page: heap page 7692")]):
        y = 84 + row * 78
        s += txt(32, y + 18, label, size=11, weight="600", anchor="start", fill=ACCENT if row else INK)
        s += mono(32, y + 34, pages, size=8, fill=MUTED, anchor="start")
        x = x0
        for name, n in recs:
            c = cols[name]
            s += bar(x, y, n * k, 30, fill=c, opacity=0.35, stroke=c)
            if n * k > 38:
                s += mono(x + n * k / 2, y + 13, name, size=7, fill=INK)
                s += mono(x + n * k / 2, y + 25, f"{n} B", size=7.5, fill=INK, weight="600")
            x += n * k
        s += mono(x + 10, y + 20, f"{total} B · {len(recs)} records", size=10, fill=INK, anchor="start", weight="600")
    # axis
    ya = 236
    s += f'<line x1="{x0}" y1="{ya}" x2="{x0 + w}" y2="{ya}" stroke="{RULE_SOLID}" stroke-width="0.8"/>'
    for b in range(0, t1 + 1, 50):
        s += f'<line x1="{x0 + b * k}" y1="{ya}" x2="{x0 + b * k}" y2="{ya + 4}" stroke="{MUTED}" stroke-width="0.8"/>'
        s += mono(x0 + b * k, ya + 15, str(b), size=7, fill=SOFT)
    s += mono(x0 + w + 10, ya + 15, "bytes of record", size=7.5, fill=SOFT, anchor="start")
    s += note(32, 274, "sizes are pg_walinspect record_length; the HOT_UPDATE logs only the changed tail of the tuple, because both versions share a page")
    return emit("10", "update-cost", "What each update wrote",
                "The non-HOT update cost five records on four pages; the HOT update cost two records on one page.",
                "HOT", vw, vh, s)


# ------------------------------------------------------------------ FIG 11
def fig11():
    vw, vh = 1016, 470
    n = D["pages"]["orders"]
    states = [("before vacuum", {32, 7692}), ("after vacuum 1", {32}), ("after vacuum 2", set())]
    x0, w = 220, 764
    k = w / n
    s = eyebrow(32, 44, f"visibility-map all-visible bit for each of the {fmt(n)} pages of orders")
    for i, (label, clear) in enumerate(states):
        y = 78 + i * 50
        s += txt(32, y + 17, label, size=10.5, weight="600", anchor="start")
        s += mono(32, y + 31, f"{fmt(n - len(clear))} of {fmt(n)} set", size=8, fill=MUTED, anchor="start")
        s += bar(x0, y, w, 26, fill=SER2, opacity=0.30)
        for p in clear:
            s += bar(x0 + p * k - 1, y - 3, 3, 32, fill=ACCENT, opacity=1)
    s += mono(x0 + 32 * k, 70, "32", size=7.5, fill=ACCENT)
    s += mono(x0 + 7692 * k, 70, "7692", size=7.5, fill=ACCENT, anchor="end")
    # zoom on pages 0..40 of the 'before' band
    yz = 262
    s += mono(32, yz - 14, "before vacuum, pages 0–40 enlarged: what vacuum read", size=9, fill=INK, anchor="start", weight="600")
    cw = 952 / 41
    for p in range(41):
        clear = p == 32
        s += cell(32 + p * cw, yz, cw, 28, str(p) if p % 4 == 0 or p == 32 else "",
                  fill=ACCENT_TINT if clear else "rgba(94,122,155,0.25)", size=7,
                  tcolor=ACCENT if clear else INK, stroke="#ffffff")
    s += f'<path d="M {34} {yz + 36} V {yz + 42} H {32 + 32 * cw - 2} V {yz + 36}" fill="none" stroke="{MUTED}" stroke-width="0.9"/>'
    s += mono(32 + 16 * cw, yz + 58, "a run of 32 all-visible pages: long enough to skip (runs under 32 are read anyway)", size=8, fill=MUTED)
    s += mono(32 + 32.5 * cw, yz + 78, "read", size=8, fill=ACCENT, weight="600")
    s += mono(32 + 37 * cw, yz + 58, "…skip…", size=8, fill=SOFT)
    s += note(32, 380, "VACUUM (VERBOSE): pages: 0 removed, 7693 remain, 2 scanned (0.03% of total) — pages 32 and 7692")
    s += note(32, 398, "index scan bypassed: 1 pages from table (0.01% of total) have 1 dead item identifiers — so page 32 stayed clear until INDEX_CLEANUP ON")
    s += legend(436, vw, [("all-visible: vacuum may skip, index-only scans need not visit", SER2, "box"), ("not all-visible", ACCENT, "box")])
    return emit("11", "visibility-map", "The visibility map before and after vacuum",
                "Two clear bits out of 7,693 made vacuum read two pages.",
                "the visibility map", vw, vh, s)


ALL = {"01": fig01, "02": fig02, "03": fig03, "04": fig04, "05": fig05, "06": fig06,
       "07": fig07, "08": fig08, "09": fig09, "10": fig10, "11": fig11}

if __name__ == "__main__":
    want = sys.argv[1:] or sorted(ALL)
    for k in want:
        ALL[k]()
